"""news_process.pipeline.external.epu_merge — stage 16: EPU 中国版 merge (B1).

v3.6.1 PR #5 — 把 policyuncertainty.com 中国月度 EPU 时间序列按 (year, month)
合并到 article-level, 然后 bank-year 聚合输出 3 列 macro control.

学术依据
--------
Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy
uncertainty. The Quarterly Journal of Economics, 131(4), 1593-1636.
https://doi.org/10.1093/qje/qjw024

Davis, S. J., Liu, D., & Sheng, X. S. (2019). Economic policy uncertainty
in China since 1949. NBER Working Paper.

数据源
------
默认 path: ``data/external/epu_china_monthly_2007_2024.csv``
预期 schema:
    year:int, month:int, epu:float
若文件不存在或不全, stage 输出仍生成 (碎片化 with NaN), 不阻塞下游.

D-0 实测项 (v2.3 G-B1.1)
------------------------
1. policyuncertainty.com 实际覆盖年份 (可能止于 2022)
2. 若止于 2022 → 2023-2024 用 last-12m rolling carry-forward + dummy 标记
3. 与 GDP / M2 多重共线性检验 (corr < 0.7)

输出
----
``data/processed/16_epu_panel.parquet`` 列契约:
    target_bank: str (主键)
    year: int (主键)
    epu_mean_year: float (年内月度 EPU 均值, 月度等权 BBD 2016 QJE; 非文章数加权)
    epu_year_end: float (该年 12 月 EPU)
    epu_std_year: float (年内月度 EPU 标准差)
    epu_data_complete: int (0/1; 该年是否所有月份都有 EPU 数据)
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Optional

import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "16_epu_merge"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])


def _resolve_epu_path() -> Optional[Path]:
    """解析 EPU csv 路径; 优先 config['paths']['epu_china_csv']."""
    cfg_path = CONFIG.get('paths', {}).get('epu_china_csv', '')
    if cfg_path and os.path.exists(cfg_path):
        return Path(cfg_path)
    default = Path(_PROJECT_PARENT) / 'news_process' / 'data' / 'external' / 'epu_china_monthly_2007_2024.csv'
    if default.exists():
        return default
    return None


def load_epu_china(path: Optional[Path] = None) -> pd.DataFrame:
    """加载 EPU 中国月度数据.

    Returns:
        DataFrame with columns [year, month, epu]; 空 DataFrame if missing.
    """
    p = path or _resolve_epu_path()
    # 显式传 path 但文件不存在 → 退化 (与 path=None 同款 graceful 处理)
    if p is None or (path is not None and not Path(p).exists()):
        logger.warning(f"  EPU csv 文件未找到 (p={p}); stage 16 输出全 NaN")
        return pd.DataFrame(columns=['year', 'month', 'epu'])
    df = pd.read_csv(p)
    # 兼容大小写列名
    df.columns = [c.lower().strip() for c in df.columns]
    required = {'year', 'month', 'epu'}
    if not required.issubset(set(df.columns)):
        logger.error(
            f"  EPU csv 列缺失: 期望 {required}, 实际 {set(df.columns)}; "
            f"stage 16 输出全 NaN"
        )
        return pd.DataFrame(columns=['year', 'month', 'epu'])
    df['year'] = df['year'].astype(int)
    df['month'] = df['month'].astype(int)
    df['epu'] = pd.to_numeric(df['epu'], errors='coerce')
    logger.info(
        f"  EPU 加载完成: {len(df)} 月度观测, "
        f"覆盖 {df['year'].min()}-{df['year'].max()}"
    )
    return df[['year', 'month', 'epu']]


def aggregate_epu_to_bank_year(
    article_df: pd.DataFrame,
    epu_df: pd.DataFrame,
) -> pd.DataFrame:
    """article-level merge → bank-year aggregate.

    Args:
        article_df: 必含 ['target_bank', 'year', '日期' or 'publish_date'] 列.
        epu_df: load_epu_china() 输出.

    Returns:
        bank-year panel with EPU 3 列 + completeness flag.
    """
    if epu_df.empty:
        # 退化: 返回 target_bank × year 空骨架
        out = (
            article_df[['target_bank', 'year']].drop_duplicates().copy()
            if 'target_bank' in article_df.columns and 'year' in article_df.columns
            else pd.DataFrame(columns=['target_bank', 'year'])
        )
        out['epu_mean_year'] = float('nan')
        out['epu_year_end'] = float('nan')
        out['epu_std_year'] = float('nan')
        out['epu_data_complete'] = 0
        return out

    # ── article-level merge ──
    date_col = '日期' if '日期' in article_df.columns else 'publish_date'
    if date_col not in article_df.columns:
        logger.warning(f"  article_df 缺 date 列, 仅按 year merge")
        # year-only fallback: 月度等权年均 (P1 修复 metric-audit 2026-06-02: 与主路径
        # 口径统一 — year_end 取 month==12, complete 用 distinct 月份数; 旧 .last()/
        # size()==12 在缺月或重复行 CSV 上偏离主路径).
        year_epu = epu_df.groupby('year', as_index=False).agg(
            epu_mean_year=('epu', 'mean'),
            epu_std_year=('epu', 'std'),
        )
        _ye = (epu_df[epu_df['month'] == 12][['year', 'epu']]
               .rename(columns={'epu': 'epu_year_end'}))
        year_epu = year_epu.merge(_ye, on='year', how='left')
        _nm = (epu_df.dropna(subset=['epu']).groupby('year')['month'].nunique()
               .rename('_n_months').reset_index())
        year_epu = year_epu.merge(_nm, on='year', how='left')
        year_epu['epu_data_complete'] = (year_epu['_n_months'].fillna(0) >= 12).astype(int)
        year_epu = year_epu.drop(columns=['_n_months'])
        out = article_df[['target_bank', 'year']].drop_duplicates().merge(
            year_epu, on='year', how='left',
        )
        return out

    # ── bank-year aggregate (P1 修复 metric-audit 2026-06-02) ──
    # EPU 是国家级月度宏观序列, 某年内对所有银行相同 (Baker-Bloom-Davis 2016 QJE).
    # 旧实现在 article-level merged 上取 mean/std → 被各银行各月发稿量加权 (epu-01/03,
    # 高 EPU 月发稿多的 bank-year 系统性偏移, 引入机械内生性); n_months 用 EPU 值
    # nunique 且仅覆盖该 bank-year 文章所在月 (≤2) → epu_data_complete 恒 0 (epu-04);
    # year_end 用 .last() 取最后可得月而非 12 月 (epu-02). 改为直接从 epu_df 算月度
    # 等权年度聚合, 按 year broadcast 到 bank-year (与下方 year-only fallback 同口径,
    # 消除主/备路径系统性分叉). date_col 仅用于上方 fallback 触发判断, 主路径不再需要.
    year_epu = epu_df.groupby('year', as_index=False).agg(
        epu_mean_year=('epu', 'mean'),    # 月度等权年均
        epu_std_year=('epu', 'std'),      # 月度等权年内 SD
    )
    # epu_year_end: 显式取 12 月观测 (缺则 NaN), 不回退到"最后可得月"
    year_end = (
        epu_df[epu_df['month'] == 12][['year', 'epu']]
        .rename(columns={'epu': 'epu_year_end'})
    )
    year_epu = year_epu.merge(year_end, on='year', how='left')
    # epu_data_complete: 该年覆盖的 distinct 月份数 ≥ 12 (对月份去重, 非对 EPU 取值)
    n_months = (
        epu_df.dropna(subset=['epu']).groupby('year')['month'].nunique()
        .rename('_n_months').reset_index()
    )
    year_epu = year_epu.merge(n_months, on='year', how='left')
    year_epu['epu_data_complete'] = (year_epu['_n_months'].fillna(0) >= 12).astype(int)
    year_epu = year_epu.drop(columns=['_n_months'])

    # broadcast 到 bank-year (EPU 在年内对所有银行相同)
    # P1 修复回归补丁 (metric-audit 2026-06-02): 函数契约 (docstring) 声明 article_df
    # 含 'year', 但实际上游 13_news_with_ctx.parquet 仅有 date_col ('日期') 无派生 year;
    # 旧主路径自行从 date 派生, 本批重写主路径时漏带. 此处显式派生 (与 executive_ner /
    # article_staleness 的 pd.to_datetime(日期).dt.year 同口径), 避免 KeyError.
    if 'year' in article_df.columns:
        bank_year = article_df[['target_bank', 'year']].dropna(subset=['year']).copy()
    else:
        bank_year = pd.DataFrame({
            'target_bank': article_df['target_bank'].values,
            'year': pd.to_datetime(article_df[date_col], errors='coerce').dt.year,
        }).dropna(subset=['year'])
    bank_year['year'] = bank_year['year'].astype(int)
    out = (
        bank_year.drop_duplicates()
        .merge(year_epu, on='year', how='left')
    )
    return out


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 16: EPU 中国版 merge (v3.6.1 PR #5, B1)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    out_path = os.path.join(output_dir, '16_epu_panel.parquet')

    # ── 加载上游 article-level (stage 13 物化后) ──
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        # fallback stage 12
        src_path = os.path.join(output_dir, '12_fintech_news.parquet')
    if not os.path.exists(src_path):
        logger.error("  上游 article-level parquet 未找到; 跳过 stage 16")
        sys.exit(0)

    article_df = pd.read_parquet(src_path)
    logger.info(f"  上游 article-level: {len(article_df)} 行")

    epu_df = load_epu_china()
    panel = aggregate_epu_to_bank_year(article_df, epu_df)

    # ── 共线性诊断 (G-B1.2) ──
    if not panel['epu_mean_year'].isna().all():
        logger.info(
            f"  EPU panel: rows={len(panel)}, "
            f"epu_mean_year 非空率={panel['epu_mean_year'].notna().mean():.1%}"
        )

    panel.to_parquet(out_path, index=False)
    logger.info(f"  输出: {out_path}")
    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")

    # R1-R5 audit fix A9 (2026-05-27): 修 R4-A8 silent failure ——
    # 若 panel 为 (0, 6) 空骨架, 显式打 ERROR 级日志而非 silent OK exit.
    # 下游 Stata `merge 1:1 epu_*` 在空表上是 no-op, 主回归 silent 缺 EPU
    # control. 此处不 raise (保留 graceful by-design behavior, 与 CLAUDE.md
    # v3.6.1 PR #5 声明一致), 但显式 ERROR 让 user/CI catch 状态.
    if len(panel) == 0:
        logger.error(
            "  ⚠ EPU panel shape=(0,6) — 检查 data/external/"
            "epu_china_monthly_2007_2024.csv 是否存在. 下游 Stata merge 将"
            "silent 缺 EPU control, 影响所有 paper macro control 路径."
        )
    elif panel['epu_mean_year'].isna().all():
        logger.error(
            "  ⚠ EPU panel 全 NaN — 上游 article-level merge 失败 (可能日期 "
            "parse 出错或时间窗未覆盖). 下游 macro control 失效."
        )


if __name__ == '__main__':
    main()
