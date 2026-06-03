"""news_process.pipeline.panel.risk_taking_outcomes — Stage 49 实现.

V4 audit DC2 + C2 deliverable (2026-05-18).

输入
----
- data/processed/40_panel_yearly.parquet (stage 45 输出, bank-year panel)
- data/dry_run/<period>_outcome.parquet 或 data/processed/47_outcomes/*.parquet
  (DC2 dry_run / full acquisition 输出, 含 ROA / CAR / NPL / RWA 等原始字段)
- news_process/config/bank_list.yaml (bank metadata: is_soe / tier)

输出
----
- data/processed/49_risk_taking_outcomes.parquet
  schema: target_bank × year × {
      z_score, npl_formation_rate, rwa_to_ta_ratio,
      sigma_roa_5y_rolling, loan_loss_provision_discretion,
      is_soe, bank_type_id, implicit_guarantee_tier  (from bank_list.yaml)
  }

Z-score 计算
------------
Z_score[b, t] = (ROA[b, t] + CAR[b, t]) / sigma_roa_5y_rolling[b, t]

其中:
    sigma_roa_5y_rolling[b, t] = std(ROA[b, t-4..t])  if  count(non-NaN) >= 4
                               = NaN                  otherwise

NPL formation rate 计算
----------------------
NPL_formation[b, t] = (NPL_balance[b, t] - NPL_balance[b, t-1] + writeoffs[b, t])
                     / Total_loans[b, t-1]

writeoffs 缺失时 fallback 为 0 (会保守低估 NPL formation).

V4 audit 修复对应
----------------
- F-P1.1 implicit guarantee 框架: 加 is_soe / bank_type_id / implicit_guarantee_tier 列
- F5.2 σ(ROA) rolling window: 默认 5y, 提供 3y/7y robustness
- F5.3 NPL formation 公式: 已注入 writeoffs 修正项
- F5.5 winsorize: 1%/5% 选项 (default 不 winsorize, 留给 stage 51)
- Fallback path α/β/γ: 通过 outcome 列可得率自动判定 (path γ → 仅保留 ROA + NPL ratio)
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# v3.7.0 (m6 修复): eps 提取为 module 常量, 避免 3 处重复硬编码
_DIV_EPS = 1e-6  # 除法分母最小绝对值, 低于此视为 0

# P1 修复 (metric-audit 2026-06-02): 默认 bank_list 路径此前写死相对字符串
# 'news_process/config/bank_list.yaml'; 主 cwd=news_process/ 下解析为
# news_process/news_process/config/... (不存在) → merge_bank_metadata 静默跳过 →
# is_soe / bank_type_id / implicit_guarantee_tier 全 NaN 但回归仍跑. 改为相对本
# 模块文件解析 (本模块在 pipeline/panel/, config 在 parents[2]/config).
_DEFAULT_BANK_LIST = Path(__file__).resolve().parents[2] / 'config' / 'bank_list.yaml'

# 与 banking_outcome_dry_run.py::OUTCOME_SCHEMA 一致的原始字段名
INPUT_OUTCOME_COLS = [
    'target_bank', 'year', 'quarter',
    'roa', 'capital_adequacy_ratio',
    'total_assets', 'rwa',
    'npl_balance', 'npl_ratio', 'total_loans',
    'loan_writeoffs', 'loan_loss_provision',
]

# 输出字段
OUTPUT_OUTCOME_COLS = [
    'target_bank', 'year',
    'z_score',
    'npl_formation_rate',
    'writeoffs_imputed',                # v3.7.0 M7: writeoffs imputation indicator
    'rwa_to_ta_ratio',
    'sigma_roa_5y_rolling',
    'loan_loss_provision_discretion',   # raw LLP/Loans ratio; BW 2012 residual 在 Stata
    'roa',                              # 保留原始字段供 fallback path γ
    'npl_ratio',
    'is_soe',
    'bank_type_id',
    'implicit_guarantee_tier',
]


def aggregate_quarterly_to_yearly(df_quarterly: pd.DataFrame) -> pd.DataFrame:
    """季度数据聚合为年度.

    v3.7.0 (M8 修复): stock 类不再仅取 Q4, 而是 fallback 到 *最后可得季度*.
    避免 Q4 缺失即全年丢失的边界 bug.

    财务量类 (stock): 该 bank-year *最后可得* 季度的值 (forward-fill semantic)
        total_assets, rwa, npl_balance, total_loans, loan_loss_provision
    比率类 (intensive): 年内均值
        roa, capital_adequacy_ratio, npl_ratio
    流量类 (flow): 年内累计 (min_count=1 → 全 NaN 时返回 NaN)
        loan_writeoffs
    """
    if 'quarter' not in df_quarterly.columns:
        return df_quarterly.copy()

    stock_cols = ['total_assets', 'rwa', 'npl_balance', 'total_loans',
                  'loan_loss_provision']
    intensive_cols = ['roa', 'capital_adequacy_ratio', 'npl_ratio']
    flow_cols = ['loan_writeoffs']

    stock_avail = [c for c in stock_cols if c in df_quarterly.columns]
    intensive_avail = [c for c in intensive_cols if c in df_quarterly.columns]
    flow_avail = [c for c in flow_cols if c in df_quarterly.columns]

    # Stock: 每个 (bank, year) 取 quarter 最大值, 但每列分别取最大可得 quarter
    # (避免 Q4 缺失全年丢失). 实现: 按 (bank, year) 排序 quarter 后 last valid.
    if stock_avail:
        df_q_sorted = df_quarterly.sort_values(['target_bank', 'year', 'quarter'])
        df_stock = (df_q_sorted
                    .groupby(['target_bank', 'year'])[stock_avail]
                    .apply(lambda g: g.ffill().iloc[-1])
                    .reset_index())
    else:
        df_stock = pd.DataFrame(columns=['target_bank', 'year'])

    # 年内均值 (intensive)
    if intensive_avail:
        df_intensive = (
            df_quarterly.groupby(['target_bank', 'year'])[intensive_avail]
            .mean()
            .reset_index()
        )
    else:
        df_intensive = pd.DataFrame(columns=['target_bank', 'year'])

    # 年内累计 (flow)
    if flow_avail:
        df_flow = (
            df_quarterly.groupby(['target_bank', 'year'])[flow_avail]
            .sum(min_count=1)
            .reset_index()
        )
    else:
        df_flow = pd.DataFrame(columns=['target_bank', 'year'])

    # Merge
    result = df_stock if not df_stock.empty else pd.DataFrame(
        columns=['target_bank', 'year']
    )
    for d in (df_intensive, df_flow):
        if not d.empty:
            result = result.merge(d, on=['target_bank', 'year'], how='outer')
    return result


def compute_sigma_roa_rolling(
    df_yearly: pd.DataFrame,
    window: int = 5,
    min_periods: int = 4,
) -> pd.Series:
    """5-year rolling std of ROA per bank (V4 F5.2)."""
    df_yearly = df_yearly.sort_values(['target_bank', 'year'])
    return (
        df_yearly.groupby('target_bank')['roa']
        .rolling(window=window, min_periods=min_periods)
        .std()
        .reset_index(level=0, drop=True)
    )


def compute_z_score(df: pd.DataFrame) -> pd.Series:
    """Bank stability Z-score = (ROA + CAR) / sigma_roa_5y_rolling.

    ⚠ 构念说明 (audit-fixes 2026-05-29, M2): 此处资本项用监管 Basel 资本充足率
    (capital_adequacy_ratio, RWA 加权), 而 Laeven-Levine (2009 JFE) 原版 Z-score
    的资本项是账面 equity/total-assets (book leverage)。二者经济含义不同 (监管
    CAR 系统性更大、行为不同), 故本实现是 *CAR-based* 稳定性变体, 不应直接归因于
    L&L 2009。USER DECISION 待定: (a) 若可获取 total_equity, 应另算 equity/assets
    版并保留 CAR 版作 robustness; (b) 否则论文中明确标注为 CAR-based 变体而非
    直引 L&L。量纲无碍 (ROA 与 CAR 同为 %, 与 sigma 约掉)。

    v3.7.0 (M6 修复): NaN 处理 explicit, 不依赖 NaN.abs() < eps 行为隐含.
    """
    numerator = df['roa'] + df['capital_adequacy_ratio']
    denominator = df['sigma_roa_5y_rolling']
    invalid_denom = denominator.isna() | (denominator.abs() < _DIV_EPS)
    return np.where(invalid_denom, np.nan, numerator / denominator)


def compute_npl_formation(df_yearly: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """NPL formation rate (Bushman-Williams 2015 JAR forward-looking).

    v3.7.0 (M7 修复): 返回 (npl_formation_rate, writeoffs_imputed) 两列.
    writeoffs_imputed=1 表示该 obs 用了 0 imputation (writeoffs 缺失) — 下游回归
    需要区分真实 0 vs imputation, 否则系数偏 (writeoffs missing 集中在小银行).

    Returns:
        (npl_formation: pd.Series, writeoffs_imputed: pd.Series)
    """
    df_yearly = df_yearly.sort_values(['target_bank', 'year'])
    npl_lag1 = df_yearly.groupby('target_bank')['npl_balance'].shift(1)
    loan_lag1 = df_yearly.groupby('target_bank')['total_loans'].shift(1)

    if 'loan_writeoffs' in df_yearly.columns:
        writeoffs_raw = df_yearly['loan_writeoffs']
    else:
        writeoffs_raw = pd.Series(np.nan, index=df_yearly.index)
    # imputation indicator (1=用了 0 imputation, 0=真实数据)
    writeoffs_imputed = writeoffs_raw.isna().astype('Int8')
    writeoffs = writeoffs_raw.fillna(0.0)

    numerator = (df_yearly['npl_balance'] - npl_lag1) + writeoffs
    invalid_loan = loan_lag1.isna() | (loan_lag1.abs() < _DIV_EPS)
    npl_formation = pd.Series(
        np.where(invalid_loan, np.nan, numerator / loan_lag1),
        index=df_yearly.index,
    )
    return npl_formation, writeoffs_imputed


def compute_llp_discretion(df_yearly: pd.DataFrame) -> pd.Series:
    """Loan loss provision raw ratio (LLP / Total_loans).

    ⚠ 诚实度声明: 本函数返回的是 **裸 LLP/loans 比率, 不是 BW2012 (Bushman-
    Williams 2012 JAE) 基于残差的贷款损失准备裁量度量** (raw LLP/loans ratio,
    NOT the BW2012 residual-based discretion measure). residual 回归在本仓库中
    **尚未实现** (residual regression NOT implemented): 列名 / 变量名虽含
    "discretion" 字样, 但其数值只是 LLP/loans, 任何把它当作"裁量性"准备解读的
    下游分析都是过度声称, 须先减去 fundamentals 拟合值才成立。

    真实 BW 2012 discretion = residual from fundamentals regression, 设计上应在
    Stata 模板中 2-stage 实施 (先跑 fundamentals model 算 residual, 再用 residual
    作 outcome); 本 stage 仅产 raw ratio 作该 fundamentals model 的 LHS 输入。

    Stata 模板 papers/bank_news_clarity/stata_templates/12_table3_bw2012_llp_residual.do.tmpl
    **尚不存在 (待 M5 创建)**, 因此目前整个 pipeline 中没有任何 BW2012 residual
    产出。计划中的 Bushman-Williams 2012 Eq.(2):
        LLP_t / Loans_{t-1} = α + β1·ΔNPL_t + β2·ΔLoans_t + β3·GDP_t + ε_t
        → residual ε_t = LLP discretion
    """
    llp = df_yearly.get('loan_loss_provision',
                        pd.Series(np.nan, index=df_yearly.index))
    loans = df_yearly['total_loans']
    invalid_loans = loans.isna() | (loans.abs() < _DIV_EPS)
    return np.where(invalid_loans, np.nan, llp / loans)


def merge_bank_metadata(
    df: pd.DataFrame,
    bank_list_path: Path = _DEFAULT_BANK_LIST,
) -> pd.DataFrame:
    """从 bank_list.yaml 合并 is_soe / bank_type_id / tier 列.

    v3.7.0 (M9 修复): PyYAML import fail-loud — 项目已依赖 PyYAML (paper_spec.yaml
    加载、core/config.py YAML split), silent skip 让下游 SOE/tier 列全 NaN 但
    回归仍跑 → 错误结果通过 audit. 改为直接 import (PyYAML 真不可用时 ImportError).
    """
    import yaml  # fail-loud, 不 try/except

    if not bank_list_path.exists():
        logger.warning(f"bank_list.yaml 不存在: {bank_list_path}, 跳过 metadata 合并")
        return df

    with bank_list_path.open('r', encoding='utf-8') as f:
        cfg = yaml.safe_load(f)

    banks = cfg.get('banks', [])
    if not banks:
        logger.warning("bank_list.yaml banks 列表为空, 跳过")
        return df

    metadata_df = pd.DataFrame(banks)[
        ['target_bank', 'is_soe', 'bank_type_id', 'implicit_guarantee_tier']
    ]
    merged = df.merge(metadata_df, on='target_bank', how='left')
    n_unmatched = merged['is_soe'].isna().sum()
    if n_unmatched > 0:
        logger.warning(
            f"  {n_unmatched} / {len(merged)} bank-year 无 metadata 匹配 "
            f"(bank_list.yaml 当前仅 frozen {len(banks)} 行, "
            f"M1 待补全 ~460 行, 见 implicit_guarantee_framework.md)"
        )
    return merged


def build_risk_taking_outcomes(
    df_quarterly_or_yearly: pd.DataFrame,
    bank_list_path: Optional[Path] = None,
    rolling_window: int = 5,
    min_periods: int = 4,
) -> pd.DataFrame:
    """构建 risk-taking outcomes panel.

    Args:
        df_quarterly_or_yearly: DC2 dry-run 或 full acquisition 输出 dataframe.
        bank_list_path: bank_list.yaml 路径 (None 时用默认).
        rolling_window: σ(ROA) 滚动窗口 (默认 5 年, V4 F5.2 多窗口 robustness).
        min_periods: 滚动窗口最小观测数.

    Returns:
        pd.DataFrame 含 OUTPUT_OUTCOME_COLS 字段.
    """
    # Step 1: 季度 → 年度 (若需要)
    if 'quarter' in df_quarterly_or_yearly.columns:
        df_y = aggregate_quarterly_to_yearly(df_quarterly_or_yearly)
        logger.info(
            f"  季度 → 年度聚合: {len(df_quarterly_or_yearly)} 行 "
            f"→ {len(df_y)} bank-year obs"
        )
    else:
        df_y = df_quarterly_or_yearly.copy()

    # Step 2: σ(ROA) 5y rolling
    df_y = df_y.sort_values(['target_bank', 'year']).reset_index(drop=True)
    df_y['sigma_roa_5y_rolling'] = compute_sigma_roa_rolling(
        df_y, window=rolling_window, min_periods=min_periods
    )

    # Step 3: Z-score
    df_y['z_score'] = compute_z_score(df_y)

    # Step 4: NPL formation rate (M7 修复: 同时输出 writeoffs_imputed indicator)
    npl_formation, writeoffs_imputed = compute_npl_formation(df_y)
    df_y['npl_formation_rate'] = npl_formation
    df_y['writeoffs_imputed'] = writeoffs_imputed

    # Step 5: RWA / TA ratio (M6 修复: NaN 处理 explicit, _DIV_EPS module 常量)
    total_assets = df_y.get('total_assets', pd.Series(np.nan, index=df_y.index))
    rwa = df_y.get('rwa', pd.Series(np.nan, index=df_y.index))
    invalid_ta = total_assets.isna() | (total_assets.abs() < _DIV_EPS)
    df_y['rwa_to_ta_ratio'] = np.where(invalid_ta, np.nan, rwa / total_assets)

    # Step 6: LLP discretion (raw ratio; full BW 2012 residual 在 Stata 模板)
    df_y['loan_loss_provision_discretion'] = compute_llp_discretion(df_y)

    # Step 7: Merge bank metadata
    bp = bank_list_path if bank_list_path else _DEFAULT_BANK_LIST
    df_y = merge_bank_metadata(df_y, bp)

    # Step 8: 选 OUTPUT_OUTCOME_COLS, 缺失列补 NaN
    out_cols = [c for c in OUTPUT_OUTCOME_COLS if c in df_y.columns]
    for c in OUTPUT_OUTCOME_COLS:
        if c not in df_y.columns:
            df_y[c] = np.nan
            out_cols.append(c)

    return df_y[OUTPUT_OUTCOME_COLS].copy()


def summarize_outcomes(df: pd.DataFrame) -> dict:
    """计算 outcome panel 关键指标供 fallback decision 复用."""
    return {
        'n_bank_year_obs': len(df),
        'n_unique_banks': df['target_bank'].nunique(),
        'year_range': [int(df['year'].min()), int(df['year'].max())],
        'per_outcome_availability': {
            c: float(df[c].notna().mean())
            for c in ['z_score', 'npl_formation_rate', 'rwa_to_ta_ratio',
                      'sigma_roa_5y_rolling', 'loan_loss_provision_discretion']
        },
        'is_soe_count': int(df['is_soe'].fillna(False).astype(bool).sum()),
        'tier_distribution': df['implicit_guarantee_tier'].value_counts(dropna=False)
                              .to_dict(),
    }


def main():
    """Stage 49 CLI 入口."""
    parser = argparse.ArgumentParser(
        description='Stage 49: risk-taking outcomes 构建',
        epilog="""
v3.7.0 (m7) 用法场景:
  (a) DC2 dry-run 模式 (M1 期间, 用户手动验证):
      --input data/dry_run/<period>_outcome.parquet
  (b) Full acquisition 模式 (M2+, pipeline 自动跑):
      --input data/processed/<acquisition_output>.parquet
      (DC2 dry-run 通过 → fallback path α → 大规模抓取 → stage 49 自动跑)

  DAG 集成 (config/panel.yaml::risk_taking_outcomes::enabled: true) 后,
  run_pipeline_function 会用默认 --input 跑 stage 49.
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '--input',
        default='data/dry_run/2024Q1_outcome.parquet',
        type=Path,
        help='Outcome quarterly/yearly raw parquet (default: DC2 dry-run 输出)',
    )
    parser.add_argument(
        '--output',
        default='data/processed/49_risk_taking_outcomes.parquet',
        type=Path,
    )
    parser.add_argument(
        '--bank-list',
        default=_DEFAULT_BANK_LIST,
        type=Path,
    )
    parser.add_argument('--rolling-window', type=int, default=5)
    parser.add_argument('--min-periods', type=int, default=4)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

    if not args.input.exists():
        # 优雅跳过守卫 (2026-06-01, config/panel.yaml::risk_taking_outcomes 全功能打开后):
        # stage 49 现默认入主流水线, 但 DC2 dry-run outcome 数据需用户先用
        # scripts/data_acquisition/banking_outcome_dry_run.py 抓取. 数据缺失时
        # *不再* fail-loud 中断整条 fail-fast 流水线 (旧 raise SystemExit(1)),
        # 改为写出 schema 合法的空 outcome panel + 醒目 WARNING, 让 orchestrator
        # 的 "registered output 存在" 检查通过, 后续 stage 照常推进。下游论文 10/11
        # 的 outcome 分析在数据就绪后重跑本 stage 即可填实。
        logger.warning(
            "⚠ Stage 49 输入缺失: %s (DC2 dry-run outcome 数据未生成)。"
            " 按 opt-in 优雅跳过: 写出 0 行 schema 合法空 panel, 不中断主流水线。"
            " 需真实 outcome 时先运行 scripts/data_acquisition/banking_outcome_dry_run.py"
            " 生成 %s 后重跑本 stage。",
            args.input, args.input,
        )
        empty = pd.DataFrame({c: pd.Series(dtype='float64') for c in OUTPUT_OUTCOME_COLS})
        # 标识列保留 object dtype (target_bank 是字符串, *_id / tier 可空)
        for _c in ('target_bank', 'bank_type_id', 'implicit_guarantee_tier'):
            if _c in empty.columns:
                empty[_c] = pd.Series(dtype='object')
        args.output.parent.mkdir(parents=True, exist_ok=True)
        empty.to_parquet(args.output, engine='pyarrow')
        logger.warning("  已写空 outcome panel (0 行, %d 列) → %s",
                       len(OUTPUT_OUTCOME_COLS), args.output)
        return

    df_in = pd.read_parquet(args.input)
    logger.info(f"加载 {len(df_in)} 行 outcome raw data from {args.input}")

    df_out = build_risk_taking_outcomes(
        df_in,
        bank_list_path=args.bank_list,
        rolling_window=args.rolling_window,
        min_periods=args.min_periods,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_parquet(args.output, engine='pyarrow')
    logger.info(f"输出 {len(df_out)} bank-year obs → {args.output}")

    # v3.7.0 (C1 + C2 修复): 同时输出 .dta 供 Stata 模板 use, 并单独导出
    # bank_metadata.dta 供模板 merge m:1.
    # 依赖 pyreadstat (与 stage 46 stata_export 一致).
    try:
        import pyreadstat
    except ImportError:
        logger.warning(
            "pyreadstat 不可用, 跳过 .dta 导出 (Stata 模板无法直接 use). "
            "安装: pip install pyreadstat"
        )
    else:
        # (a) outcome panel .dta (与 .parquet 同目录, 同名替换扩展名)
        dta_path = args.output.with_suffix('.dta')
        # pyreadstat 不接受中文字段, 需 sanitize column names (与 stata_export 一致)
        df_out_dta = df_out.copy()
        # bool → int (Stata 不支持 bool)
        for col in df_out_dta.select_dtypes(include='bool').columns:
            df_out_dta[col] = df_out_dta[col].astype('Int8')
        try:
            # v3.7.0 V2 E2E 修复: pyreadstat write_dta 默认 version=15 (Stata 14+
            # 输出 .dta format spec 118), 与项目 stata_export.py 用法一致.
            # 之前的 file_format_version=118 不是合法参数, 会 TypeError 被 except 吞.
            pyreadstat.write_dta(df_out_dta, str(dta_path))
            logger.info(f"  .dta 导出 → {dta_path}")
        except Exception as exc:
            logger.warning(f"  .dta 导出失败 (Stata 模板降级): {exc!r}")

        # (b) bank_metadata.dta (单独表, 供 Stata 模板 merge m:1)
        metadata_cols = ['target_bank', 'is_soe', 'bank_type_id',
                         'implicit_guarantee_tier']
        if all(c in df_out_dta.columns for c in metadata_cols):
            meta_df = (df_out_dta[metadata_cols]
                       .drop_duplicates(subset=['target_bank']).reset_index(drop=True))
            meta_path = args.output.parent / 'bank_metadata.dta'
            try:
                pyreadstat.write_dta(meta_df, str(meta_path))  # V2 E2E 修复
                logger.info(f"  bank_metadata.dta → {meta_path} "
                            f"({len(meta_df)} 行 unique bank)")
            except Exception as exc:
                logger.warning(f"  bank_metadata.dta 导出失败: {exc!r}")

    summary = summarize_outcomes(df_out)
    logger.info("Outcome panel summary:")
    for k, v in summary.items():
        logger.info(f"  {k}: {v}")


if __name__ == '__main__':
    main()
