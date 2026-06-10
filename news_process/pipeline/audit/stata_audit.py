"""
news_process.pipeline.audit.stata_audit — Stata 用面板数据最高标准审核与验证
==============================================================================

迁移说明 (Phase 7a-8)：
    本模块由原 root script ``52_stata_data_audit.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.audit.stata_audit``


功能:
  对最终输出至 Stata 的所有 .dta / .parquet 面板数据进行全面审核:
    1. 面板结构完整性 (唯一键、平衡性、维度)
    2. 变量质量审核 (缺失率、异常值、值域合规)
    3. 情感指标一致性检验 (票投一致性、加权恒等式、跨轨道相关)
    4. IV 有效性预检 (Bartik 份额归一、LOO 排除己检验)
    5. DID 变量合规性 (0/1 编码、时间逻辑、treated/post 一致性)
    6. Stata 兼容性 (列名合规、数据类型、缺失编码)
    7. 跨文件数据一致性 (40 vs 51 面板核心变量一致)

参考文献:
  [1] Baltagi, B.H. (2021). Econometric Analysis of Panel Data. 6th ed.
      → 面板平衡性诊断标准
  [2] Wooldridge, J.M. (2010). Econometric Analysis of Cross Section and Panel Data.
      → 面板唯一键约束
  [3] Goldsmith-Pinkham, S., Sorkin, I. & Swift, H. (2020, AER).
      "Bartik Instruments." → Bartik 份额归一化检验

输入:
  data/processed/40_panel_yearly.parquet
  data/processed/40_panel_yearly.dta
  data/processed/51_panel_with_controls.parquet
  data/processed/51_panel_with_controls.dta
  data/processed/40_article_bank_level.parquet

输出:
  data/processed/eval_reports/52_stata_data_audit.csv    (审核摘要表)
  logs/52_stata_data_audit.log                           (详细日志)
"""

import os
import sys
import time
import warnings

import numpy as np
import pandas as pd

# Phase 7a-8: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/audit/stata_audit.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "52_stata_data_audit"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
FILENAMES = CONFIG.get("filenames", {})

# 审核结果收集器
audit_results = []

def record(category: str, check_name: str, status: str, detail: str, severity: str = 'INFO'):
    """记录一条审核结果。"""
    audit_results.append({
        'category': category,
        'check': check_name,
        'status': status,   # PASS / WARN / FAIL
        'severity': severity,
        'detail': detail,
    })
    marker = {'PASS': '✅', 'WARN': '⚠️', 'FAIL': '❌'}.get(status, 'ℹ️')
    log_func = {'PASS': logger.info, 'WARN': logger.warning, 'FAIL': logger.error}.get(status, logger.info)
    log_func(f"  {marker} [{category}] {check_name}: {detail}")


# ============================================================================
# 1. 面板结构完整性审核
# ============================================================================

def audit_panel_structure(panel: pd.DataFrame, name: str):
    """审核面板数据的结构完整性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 面板结构完整性审核")
    logger.info("=" * 70)
    cat = f"{name}/结构"

    # 1a. 唯一键检验 (Wooldridge 2010)
    dups = panel.duplicated(subset=['target_bank', 'year'], keep=False)
    n_dup = dups.sum()
    if n_dup == 0:
        record(cat, '唯一键约束', 'PASS', '(target_bank, year) 无重复行')
    else:
        dup_detail = panel[dups][['target_bank', 'year']].drop_duplicates()
        record(cat, '唯一键约束', 'FAIL',
               f'发现 {n_dup} 行重复! 涉及 {len(dup_detail)} 个 (bank, year) 组合',
               severity='CRITICAL')

    # 1b. 面板维度
    n_banks = panel['target_bank'].nunique()
    n_years = panel['year'].nunique()
    y_min, y_max = panel['year'].min(), panel['year'].max()
    expected_rows = n_banks * (y_max - y_min + 1)
    balance_ratio = len(panel) / expected_rows if expected_rows > 0 else 0

    record(cat, '面板维度', 'PASS',
           f'{n_banks} 银行 × {n_years} 年 ({y_min}-{y_max}), '
           f'行数={len(panel):,}, 理论行数={expected_rows:,}')

    if balance_ratio >= 0.999:
        record(cat, '面板平衡性', 'PASS', f'平衡率={balance_ratio:.4%} (完全平衡)')
    elif balance_ratio >= 0.95:
        record(cat, '面板平衡性', 'WARN', f'平衡率={balance_ratio:.4%} (近似平衡)')
    else:
        record(cat, '面板平衡性', 'FAIL', f'平衡率={balance_ratio:.4%} (不平衡!)')

    # 1c. 银行名一致性 (确保无空值、空字符串)
    blank_banks = panel['target_bank'].isna() | (panel['target_bank'].astype(str).str.strip() == '')
    if blank_banks.sum() > 0:
        record(cat, '银行名完整性', 'FAIL', f'{blank_banks.sum()} 行银行名为空')
    else:
        record(cat, '银行名完整性', 'PASS', '所有 target_bank 非空')

    # 1d. 年份合理性 (2000-2030 范围)
    bad_years = (panel['year'] < 2000) | (panel['year'] > 2030)
    if bad_years.sum() > 0:
        record(cat, '年份合理性', 'FAIL', f'{bad_years.sum()} 行年份超出 [2000, 2030]')
    else:
        record(cat, '年份合理性', 'PASS', f'所有年份在 [{y_min}, {y_max}] 范围内')

    # 1e. 列数报告
    record(cat, '列数统计', 'PASS', f'总计 {panel.shape[1]} 列')

    return n_banks, n_years


# ============================================================================
# 2. 变量质量审核
# ============================================================================

def audit_variable_quality(panel: pd.DataFrame, name: str):
    """审核所有变量的数据质量。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 变量质量审核")
    logger.info("=" * 70)
    cat = f"{name}/变量质量"

    # 2a. 全局缺失率
    n_rows = len(panel)
    missing_report = []
    for col in panel.columns:
        miss = panel[col].isna().sum()
        miss_pct = miss / n_rows if n_rows > 0 else 0
        if miss > 0:
            missing_report.append((col, miss, miss_pct))

    if missing_report:
        # 高缺失率变量
        high_miss = [(c, n, p) for c, n, p in missing_report if p > 0.5]
        if high_miss:
            detail = '; '.join([f'{c}={p:.1%}' for c, n, p in high_miss[:10]])
            record(cat, '高缺失率变量(>50%)', 'WARN',
                   f'{len(high_miss)} 个变量: {detail}')

        # 关键变量缺失检查
        key_vars = [
            ('n_articles', 0.0, '新闻篇数'),
            ('llm_vote_tone_full', None, 'LLM投票情感(全文)'),
            ('llm_vote_tone_ctx', None, 'LLM投票情感(上下文)'),
            ('ln_news_coverage', None, '新闻覆盖度对数'),
        ]
        for var, expected_miss, label in key_vars:
            if var in panel.columns:
                miss_pct = panel[var].isna().mean()
                if expected_miss is not None:
                    if miss_pct > expected_miss + 0.01:
                        record(cat, f'关键变量缺失-{label}', 'FAIL',
                               f'{var} 缺失率={miss_pct:.1%}, 预期≤{expected_miss:.1%}')
                    else:
                        record(cat, f'关键变量缺失-{label}', 'PASS',
                               f'{var} 缺失率={miss_pct:.1%}')
                else:
                    # 情感变量: 在有新闻的行应非缺失
                    # metric-audit 2026-06-02: 用 LLM-valid 篇数(重构后 n_articles=物理),
                    # 缺列回退 n_articles, 保旧行为(不对 LLM 全失败行误 WARN).
                    _nac_mv = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
                    has_news = panel[_nac_mv] > 0 if _nac_mv in panel.columns else pd.Series(True, index=panel.index)
                    miss_in_news = panel.loc[has_news, var].isna().mean() if has_news.sum() > 0 else 0
                    if miss_in_news > 0.05:
                        record(cat, f'关键变量缺失-{label}', 'WARN',
                               f'{var} 在有新闻行的缺失率={miss_in_news:.1%}')
                    else:
                        record(cat, f'关键变量缺失-{label}', 'PASS',
                               f'{var} 在有新闻行缺失率={miss_in_news:.1%}')
    else:
        record(cat, '缺失率检查', 'PASS', '所有变量均无缺失')

    # 2b. 数值类型检查 (确保情感指标为 float)
    sentiment_cols = [c for c in panel.columns
                      if any(kw in c for kw in ['tone', 'cont', 'pos', 'neg', 'frac', 'score'])]
    non_numeric = []
    for col in sentiment_cols:
        if not pd.api.types.is_numeric_dtype(panel[col]):
            non_numeric.append(col)
    if non_numeric:
        record(cat, '数值类型检查', 'FAIL',
               f'{len(non_numeric)} 个情感列非数值: {non_numeric[:5]}')
    else:
        record(cat, '数值类型检查', 'PASS',
               f'{len(sentiment_cols)} 个情感列均为数值类型')

    # 2c. 值域合规性
    # n_articles >= 0
    if 'n_articles' in panel.columns:
        neg_articles = (panel['n_articles'] < 0).sum()
        if neg_articles > 0:
            record(cat, 'n_articles值域', 'FAIL', f'{neg_articles} 行 n_articles < 0')
        else:
            record(cat, 'n_articles值域', 'PASS', f'min={panel["n_articles"].min()}, max={panel["n_articles"].max()}')

    # 离散情感 tone 应在 [-1, 1]
    for col in ['llm_vote_tone_full', 'llm_vote_tone_ctx']:
        if col in panel.columns:
            valid = panel[col].dropna()
            if len(valid) > 0:
                if valid.min() < -1.001 or valid.max() > 1.001:
                    record(cat, f'{col}值域', 'FAIL',
                           f'超出[-1,1]: min={valid.min():.4f}, max={valid.max():.4f}')
                else:
                    record(cat, f'{col}值域', 'PASS',
                           f'值域=[{valid.min():.4f}, {valid.max():.4f}], mean={valid.mean():.4f}')

    # 哑变量检查 (0/1)
    dummy_vars = [c for c in panel.columns
                  if c.startswith(('has_', 'dummy_', 'dcep_', 'sandbox_'))
                  and c not in ('dcep_treat_year', 'sandbox_treat_year', 'dcep_rel_year', 'sandbox_rel_year')]
    for col in dummy_vars:
        if col in panel.columns:
            unique_vals = set(panel[col].dropna().unique())
            # ruff B033: {0, 0.0} / {1, 1.0} 在 set 中等价 → 折叠为 {0, 1}
            # 原代码语义上想兼容 int/float 表示, 但 set 无差异; pandas
            # .unique() 返回 dtype 取决于源列, issubset({0, 1}) 自动 OK.
            valid_vals = {0, 1}
            if not unique_vals.issubset(valid_vals):
                record(cat, f'哑变量{col}', 'FAIL',
                       f'含非0/1值: {unique_vals - valid_vals}')

    # 2d. 异常值检测 (情感指标 > 5σ)
    outlier_cols = ['llm_vote_tone_full', 'llm_vote_cont_full',
                    'dict_avg_tone_full', 'bert_avg_pos_full']
    for col in outlier_cols:
        if col in panel.columns:
            valid = panel[col].dropna()
            if len(valid) > 10:
                mean, std = valid.mean(), valid.std()
                if std > 0:
                    outliers = ((valid - mean).abs() > 5 * std).sum()
                    if outliers > 0:
                        record(cat, f'异常值-{col}', 'WARN',
                               f'{outliers} 个观测超出5σ (mean={mean:.4f}, std={std:.4f})')

    # 2e. Inf 检查
    numeric_cols = panel.select_dtypes(include=[np.number]).columns
    inf_cols = []
    for col in numeric_cols:
        n_inf = np.isinf(panel[col]).sum()
        if n_inf > 0:
            inf_cols.append((col, n_inf))
    if inf_cols:
        detail = '; '.join([f'{c}={n}' for c, n in inf_cols[:10]])
        record(cat, 'Inf值检查', 'FAIL', f'{len(inf_cols)} 列含Inf: {detail}')
    else:
        record(cat, 'Inf值检查', 'PASS', '无Inf值')


# ============================================================================
# 3. 情感指标一致性检验
# ============================================================================

def audit_sentiment_consistency(panel: pd.DataFrame, name: str):
    """审核情感指标的内部一致性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 情感指标一致性审核")
    logger.info("=" * 70)
    cat = f"{name}/情感一致性"

    # metric-audit 2026-06-02 (encode-02 重构对齐): 情感/分类计数恒等式须用 LLM-valid
    # 篇数 (count 口径); 重构后 n_articles=物理 size → 用 n_articles_llm_valid (旧 panel
    # 缺列回退 n_articles, 其即 count). 否则含 LLM 失败行的 bank-year 令 size != tech+app
    # → 误 FAIL, 而 audit_sentiment_consistency 的 FAIL 会使 stage 52 退出码=1.
    _nac = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
    # 缺列兜底 (与 audit_variable_quality:198 对称; 终验复核修: _nac 改写不得丢失
    # 原 graceful 守卫, 否则无 count 列的 panel 抛 KeyError).
    has_news = panel[_nac] > 0 if _nac in panel.columns else pd.Series(True, index=panel.index)
    p = panel[has_news]

    # 3a. pos_frac + neg_frac + neutral_frac 恒等式
    for track in ['_full', '_ctx']:
        pos_col = f'pos_frac{track}'
        neg_col = f'neg_frac{track}'
        if pos_col in p.columns and neg_col in p.columns:
            row_sum = p[pos_col].fillna(0) + p[neg_col].fillna(0)
            # 由于有中性，和应 <= 1
            over_one = (row_sum > 1.001).sum()
            if over_one > 0:
                record(cat, f'pos+neg<=1 ({track})', 'FAIL',
                       f'{over_one} 行 pos_frac + neg_frac > 1')
            else:
                record(cat, f'pos+neg<=1 ({track})', 'PASS',
                       f'所有行满足约束, max_sum={row_sum.max():.4f}')

    # 3a-bis. 全 *_frac 列值域 ∈ [0,1] (metric-audit 2026-06-02 final 补盲区):
    # 旧 audit 只检 pos/neg_frac 与 full 轨 n_tech+n_app 计数恒等, 不扫 ctx 对角线
    # 分类 frac 值域 → app_frac_lc/sub_frac_sc/collab_frac_cm 轨道不对称除法越界至
    # 3.0 完全逃检 (ctx 分子/full 分母). 现全列扫描 (排除 _z 标准化列), 任一 frac>1 即 FAIL.
    _frac_cols = [c for c in p.columns
                  if (c.endswith('_frac') or '_frac_' in c) and not c.endswith('_z')]
    _oob_frac = []
    for c in _frac_cols:
        s = pd.to_numeric(p[c], errors='coerce').dropna()
        if len(s) and (s.max() > 1.001 or s.min() < -0.001):
            _oob_frac.append(f'{c}[{s.min():.3f},{s.max():.3f}]')
    if _oob_frac:
        record(cat, '分类 frac 值域 ∈[0,1]', 'FAIL',
               f'{len(_oob_frac)}/{len(_frac_cols)} 个 frac 列越界 (轨道不对称除法?): '
               + '; '.join(_oob_frac[:8]))
    elif _frac_cols:
        record(cat, '分类 frac 值域 ∈[0,1]', 'PASS',
               f'{len(_frac_cols)} 个 *_frac 列全部 ∈[0,1]')

    # 3b. 情感非中性计数 ≤ 物理篇数 (pos+neg ≤ n_articles, 隐含 neutral ≥ 0)
    # metric-audit 2026-06-02 终验复核 (_ctx 越界缺陷根因修复): 本 sanity check 的
    # 上界应是"物理篇数"(物理 ≥ 任一轨有效篇数 ≥ 该轨 pos+neg), 故用 n_articles
    # (重构后 = 物理 size) 而非 _nac (= full 轨 LLM 有效计数). 否则 _ctx 轨在
    # "full 失败但 ctx 成功"的文章上 ctx-valid > full-valid → 拿 full 计数当上界会
    # 误报 (实测冻结 panel 4/176 行 pos_count_ctx+neg_count_ctx > n_articles; 但其
    # 物理篇数 14/4/1/2 ≥ ctx pos+neg 13/2/1/2, 是合法两轨独立成功率差异, 非双计 bug).
    # 旧冻结 panel (无 n_articles_llm_valid → n_articles 实为 full-valid 非物理) 下该
    # 上界本身偏小, _ctx 越界为已知口径限制 → WARN; 重生 panel (n_articles=物理) 上
    # 仍越界才是真双重计数 → FAIL.
    _is_physical_count = 'n_articles_llm_valid' in panel.columns
    for track in ['_full', '_ctx']:
        pos_col = f'pos_count{track}'
        neg_col = f'neg_count{track}'
        if pos_col in p.columns and neg_col in p.columns:
            # fix(int8-stata-audit, 2026-06-10): pos_count/neg_count 为 nullable Int8,
            # 元素级 Int8+Int8 在 pandas 静默回绕 (98+60→-98), 会击穿本审计要查的
            # "pos+neg>n_articles 双重计数"检验。先 astype('int64') 再相加。
            pos = p[pos_col].fillna(0).astype('int64')
            neg = p[neg_col].fillna(0).astype('int64')
            total_sentiment = pos + neg
            neutral_implied = p['n_articles'] - total_sentiment
            neg_neutral = (neutral_implied < -0.5).sum()
            if neg_neutral > 0:
                _status = 'FAIL' if _is_physical_count else 'WARN'
                _note = ('' if _is_physical_count
                         else ' (旧 panel n_articles=full-valid 非物理, 两轨独立成功率差异已知, 降 WARN; 重生后复测)')
                record(cat, f'情感计数恒等式 ({track})', _status,
                       f'{neg_neutral} 行 pos+neg > n_articles{_note}')
            else:
                record(cat, f'情感计数恒等式 ({track})', 'PASS',
                       '所有行满足 pos+neg ≤ n_articles')

    # 3c. 跨轨道相关性 (full vs ctx)
    if 'llm_vote_tone_full' in p.columns and 'llm_vote_tone_ctx' in p.columns:
        valid = p[['llm_vote_tone_full', 'llm_vote_tone_ctx']].dropna()
        if len(valid) > 10:
            r = valid['llm_vote_tone_full'].corr(valid['llm_vote_tone_ctx'])
            if r < 0.5:
                record(cat, 'Full-Ctx 跨轨道相关', 'WARN',
                       f'Pearson r={r:.4f} < 0.5, 两轨道分歧较大')
            else:
                record(cat, 'Full-Ctx 跨轨道相关', 'PASS',
                       f'Pearson r={r:.4f}')

    # 3d. LLM 模型间情感一致性
    llm_models = ['gpt54nano', 'gemini31111', 'deepseekv4']  # v3: 真三家族 (OpenAI + Google + DeepSeek)
    llm_tone_cols = [f'{m}_tone_full' for m in llm_models if f'{m}_tone_full' in p.columns]
    if len(llm_tone_cols) >= 2:
        corrs = p[llm_tone_cols].corr()
        # 提取上三角 (排除对角线的 1.0) 的最小值
        upper_tri = corrs.values[np.triu_indices_from(corrs.values, k=1)]
        min_pair_corr = upper_tri.min() if len(upper_tri) > 0 else 1.0
        record(cat, 'LLM模型间一致性', 'PASS' if min_pair_corr > 0.5 else 'WARN',
               f'最小成对相关={min_pair_corr:.4f} ({len(llm_tone_cols)}个模型)')

    # 3e. 加权均值恒等式 (VW, MW, HW)
    # 列名模式: tone=llm_vote_tone_{wt}_full, sum=llm_vote_score_{wt}_sum_full
    # 注意 VW 的列名后缀是 _vw, MW 是 _mw, HW 是 _hw
    for wt_type, wt_sfx, denom_col in [
        ('VW', 'vw', 'sum_mention_density'),
        ('MW', 'mw', 'sum_media_authority_weight'),
        ('HW', 'hw', 'sum_herd_weight'),
    ]:
        tone_col = f'llm_vote_tone_{wt_sfx}_full'
        sum_col = f'llm_vote_score_{wt_sfx}_sum_full'
        if tone_col in p.columns and sum_col in p.columns and denom_col in p.columns:
            denom = p[denom_col].replace(0, np.nan)
            expected = p[sum_col] / denom
            actual = p[tone_col]
            diff = (actual - expected).abs().dropna()
            if len(diff) > 0:
                max_diff = diff.max()
                if max_diff > 1e-8:
                    record(cat, f'{wt_type}加权恒等式', 'FAIL',
                           f'最大差异={max_diff:.6e}')
                else:
                    record(cat, f'{wt_type}加权恒等式', 'PASS',
                           f'最大差异={max_diff:.6e}')
        else:
            # HW 等可选模块未启用时列不存在，无需报 WARN
            # 仅当 VW/MW 这类核心加权列缺失时才报告
            if wt_sfx in ('vw', 'mw') and tone_col not in p.columns:
                record(cat, f'{wt_type}加权恒等式', 'WARN',
                       f'列 {tone_col} 不存在, 跳过检验')

    # 3f. 分类恒等式 n = tech + app
    if all(c in panel.columns for c in ['n_articles', 'n_articles_tech', 'n_articles_app']):
        check = panel.loc[has_news]
        identity = (check[_nac] ==
                    check['n_articles_tech'] + check['n_articles_app'])
        failures = (~identity).sum()
        if failures > 0:
            record(cat, 'fintech分类恒等式', 'FAIL', f'{failures} 行不满足 n=tech+app')
        else:
            record(cat, 'fintech分类恒等式', 'PASS', '恒等式成立')


# ============================================================================
# 4. IV 有效性预检
# ============================================================================

def audit_iv_variables(panel: pd.DataFrame, name: str):
    """审核工具变量的数据合规性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] IV 有效性预检")
    logger.info("=" * 70)
    cat = f"{name}/IV"

    # 4a. Bartik 份额归一化检验 (Goldsmith-Pinkham et al. 2020)
    # 注意: compute_bartik_iv/compute_bartik_iv_fintech 在计算 share 时
    # 会排除 'other' 类别 (groups = sorted(set(v for v in map.values() if v != 'other')))
    # 因此 share 列之和 <= 1.0 是**设计意图**, 不是数据错误
    # 检验标准: sum <= 1.0 + tolerance (排除 other 后不应超过 1)
    bartik_groups = {}
    for col in panel.columns:
        if col.startswith('bartik_') and '_share_' in col:
            prefix = col.split('_share_')[0]
            bartik_groups.setdefault(prefix, []).append(col)

    for prefix, share_cols in bartik_groups.items():
        if len(share_cols) >= 2:
            row_sums = panel[share_cols].sum(axis=1).dropna()
            if len(row_sums) > 0:
                max_sum = row_sums.max()
                min_sum = row_sums.min()
                mean_sum = row_sums.mean()
                # 关键判断: sum > 1 + tolerance 说明份额溢出 (真正的错误)
                # sum < 1 是因为 other 类未导出 (预期行为)
                over_one = (row_sums > 1.01).sum()
                if over_one > 0:
                    record(cat, f'Bartik份额归一-{prefix}', 'FAIL',
                           f'{over_one}行份额和>1.01 (溢出!), max={max_sum:.6f}')
                elif mean_sum < 0.5:
                    # 均值太低可能说明份额计算有问题
                    record(cat, f'Bartik份额归一-{prefix}', 'WARN',
                           f'份额均值={mean_sum:.4f}偏低, 可能other类占比过高, '
                           f'{len(share_cols)}个份额列, range=[{min_sum:.4f}, {max_sum:.4f}]')
                else:
                    record(cat, f'Bartik份额归一-{prefix}', 'PASS',
                           f'{len(share_cols)}个份额列, 均值={mean_sum:.4f}, '
                           f'range=[{min_sum:.4f}, {max_sum:.4f}]')

    # 4b. Leave-one-out IV 排除己检验
    n_years = panel['year'].nunique()
    for geo in ['prov', 'city']:
        loo_col = f'{geo}_leave1out_tone_full'
        tone_col = 'llm_vote_tone_full'
        if geo == 'prov':
            geo_col = 'bank_province'
        else:
            geo_col = 'bank_city'

        if loo_col in panel.columns and tone_col in panel.columns and geo_col in panel.columns:
            valid = panel[[tone_col, loo_col, geo_col, 'year']].dropna()
            if len(valid) > 10:
                r = valid[tone_col].corr(valid[loo_col])
                # 在截面数据(仅1年)中，LOO 与自身的相关性可能为负
                # (因为 LOO 从组均值中减去自身，数学上趋向负相关)
                # 只在多年面板中才要求正相关
                if n_years <= 1:
                    # 截面数据: 仅报告信息，不判断 PASS/WARN
                    record(cat, f'LOO-IV相关性({geo})', 'PASS',
                           f'r={r:.4f} (截面数据, 负相关可由LOO数学性质导致)')
                elif abs(r) < 0.05:
                    record(cat, f'LOO-IV相关性({geo})', 'WARN',
                           f'r={r:.4f}, 相关性极弱 — 可能弱IV风险')
                else:
                    record(cat, f'LOO-IV相关性({geo})', 'PASS',
                           f'r={r:.4f}')

    # 4c. Zone LOO IV
    zone_col = 'zone_leave1out_tone_full'
    if zone_col in panel.columns:
        valid = panel[zone_col].dropna()
        record(cat, 'Zone LOO IV', 'PASS',
               f'有效值={len(valid):,}, 缺失率={(panel[zone_col].isna().mean()):.1%}')

    # 4d. Bartik IV 变异性检查 (全零或常数的 IV 无效)
    iv_cols = [c for c in panel.columns if c.startswith('bartik_') and '_iv_' in c]
    constant_ivs = []
    for col in iv_cols:
        valid = panel[col].dropna()
        if len(valid) > 0 and valid.std() < 1e-10:
            constant_ivs.append(col)
    if constant_ivs:
        record(cat, 'Bartik IV变异性', 'WARN',
               f'{len(constant_ivs)} 个IV方差为零: {constant_ivs[:5]}')
    else:
        record(cat, 'Bartik IV变异性', 'PASS', f'{len(iv_cols)} 个IV均有变异')


# ============================================================================
# 5. DID 变量合规性
# ============================================================================

def audit_did_variables(panel: pd.DataFrame, name: str):
    """审核 DID 政策冲击变量的合规性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] DID 变量合规性审核")
    logger.info("=" * 70)
    cat = f"{name}/DID"

    for policy in ['dcep', 'sandbox']:
        treated_col = f'{policy}_treated'
        post_col = f'{policy}_post'
        ty_col = f'{policy}_treat_year'

        if treated_col not in panel.columns:
            record(cat, f'{policy} 存在性', 'WARN', f'{treated_col} 列不存在')
            continue

        # 5a. treated 应为 0/1 (B033: {0, 0.0, 1, 1.0} → {0, 1})
        treated_vals = set(panel[treated_col].dropna().unique())
        if not treated_vals.issubset({0, 1}):
            record(cat, f'{policy}_treated 编码', 'FAIL', f'非0/1: {treated_vals}')
        else:
            n_treated = (panel[treated_col] == 1).sum()
            record(cat, f'{policy}_treated 编码', 'PASS',
                   f'treated=1: {n_treated:,} 行')

        # 5b. post 应为 0/1 (B033: {0, 0.0, 1, 1.0} → {0, 1})
        if post_col in panel.columns:
            post_vals = set(panel[post_col].dropna().unique())
            if not post_vals.issubset({0, 1}):
                record(cat, f'{policy}_post 编码', 'FAIL', f'非0/1: {post_vals}')
            else:
                record(cat, f'{policy}_post 编码', 'PASS', '0/1 编码正确')

        # 5c. post=1 仅在 treated=1 的行中出现
        if post_col in panel.columns:
            post_in_control = ((panel[treated_col] == 0) & (panel[post_col] == 1)).sum()
            if post_in_control > 0:
                record(cat, f'{policy} treated-post 逻辑', 'FAIL',
                       f'{post_in_control} 行 treated=0 但 post=1')
            else:
                record(cat, f'{policy} treated-post 逻辑', 'PASS', '逻辑一致')

        # 5d. treat_year > 0 仅在 treated=1 时
        if ty_col in panel.columns:
            ty_in_control = ((panel[treated_col] == 0) & (panel[ty_col] > 0)).sum()
            if ty_in_control > 0:
                record(cat, f'{policy} treat_year 逻辑', 'WARN',
                       f'{ty_in_control} 行 treated=0 但 treat_year > 0')
            else:
                record(cat, f'{policy} treat_year 逻辑', 'PASS', '逻辑一致')

    # 5e. Event study 变量 — lead/lag 应互斥
    for policy in ['dcep', 'sandbox']:
        es_cols = [c for c in panel.columns
                   if c.startswith(f'{policy}_lead') or c.startswith(f'{policy}_lag')]
        if len(es_cols) >= 2:
            # 每行最多只有一个 event study dummy = 1 (或全为 0)
            es_sum = panel[es_cols].sum(axis=1)
            multi_active = (es_sum > 1).sum()
            if multi_active > 0:
                record(cat, f'{policy} event-study 互斥', 'FAIL',
                       f'{multi_active} 行有多个 lead/lag = 1')
            else:
                record(cat, f'{policy} event-study 互斥', 'PASS',
                       f'{len(es_cols)} 个 lead/lag 变量互斥性良好')


# ============================================================================
# 6. Stata 兼容性审核
# ============================================================================

def audit_stata_compatibility(panel: pd.DataFrame, dta_path: str, name: str):
    """审核 Stata .dta 文件的兼容性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] Stata 兼容性审核")
    logger.info("=" * 70)
    cat = f"{name}/Stata兼容"

    # 6a. 列名合规 (ASCII, ≤32 字符, 无特殊字符)
    import re
    bad_cols = []
    for col in panel.columns:
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]{0,31}$', col):
            bad_cols.append(col)
    if bad_cols:
        record(cat, 'Parquet列名Stata合规', 'WARN',
               f'{len(bad_cols)} 列名不符合Stata规范: {bad_cols[:5]}')
    else:
        record(cat, 'Parquet列名Stata合规', 'PASS', '所有列名合规')

    # 6b. .dta 文件可读性
    if os.path.exists(dta_path):
        try:
            dta = pd.read_stata(dta_path)
            record(cat, '.dta 可读性', 'PASS',
                   f'{dta_path} 读取成功, {dta.shape[0]} 行 × {dta.shape[1]} 列')

            # 6c. .dta 行数与 .parquet 一致
            if len(dta) != len(panel):
                record(cat, '.dta 行数一致性', 'FAIL',
                       f'.dta={len(dta)} vs .parquet={len(panel)}')
            else:
                record(cat, '.dta 行数一致性', 'PASS', f'均为 {len(dta)} 行')

            # 6d. .dta 数值精度验证 (核心变量)
            for col in ['llm_vote_tone_full', 'n_articles', 'ln_news_coverage']:
                dta_col = col[:32]  # Stata 列名截断兼容
                if dta_col in dta.columns and col in panel.columns:
                    dta_vals = dta[dta_col].astype(float)
                    pq_vals = panel[col].astype(float)
                    diff = (dta_vals - pq_vals).abs().max()
                    if diff > 0.001:
                        record(cat, f'.dta 精度-{col}', 'WARN',
                               f'最大差异={diff:.6e}')
                    else:
                        record(cat, f'.dta 精度-{col}', 'PASS',
                               f'精度一致 (max_diff={diff:.6e})')

        except Exception as e:
            record(cat, '.dta 可读性', 'FAIL', f'读取失败: {e}')
    else:
        record(cat, '.dta 文件存在性', 'WARN', f'{dta_path} 不存在')

    # 6e. Nullable dtypes 检查 (Stata 不支持)
    nullable_cols = panel.select_dtypes(include=['Float64', 'Int64']).columns.tolist()
    if nullable_cols:
        record(cat, 'Nullable Dtypes', 'WARN',
               f'{len(nullable_cols)} 列使用 Nullable dtype: {nullable_cols[:5]}')
    else:
        record(cat, 'Nullable Dtypes', 'PASS', '无 Nullable dtype')


# ============================================================================
# 7. 跨文件一致性
# ============================================================================

def audit_cross_file_consistency(panel_40: pd.DataFrame, panel_51: pd.DataFrame):
    """验证 40 和 51 面板的核心变量一致性。"""
    logger.info("=" * 70)
    logger.info("跨文件一致性审核 (40 vs 51)")
    logger.info("=" * 70)
    cat = "跨文件一致性"

    # 7a. 行数
    if len(panel_40) != len(panel_51):
        record(cat, '行数一致', 'WARN',
               f'40面板={len(panel_40)}, 51面板={len(panel_51)}')
    else:
        record(cat, '行数一致', 'PASS', f'均为 {len(panel_40)} 行')

    # 7b. 核心变量值一致
    merged = panel_40[['target_bank', 'year']].merge(
        panel_51[['target_bank', 'year']], on=['target_bank', 'year'], how='outer', indicator=True
    )
    only_40 = (merged['_merge'] == 'left_only').sum()
    only_51 = (merged['_merge'] == 'right_only').sum()

    if only_40 > 0 or only_51 > 0:
        record(cat, 'Bank-Year 键集一致', 'FAIL',
               f'仅40面板={only_40}, 仅51面板={only_51}')
    else:
        record(cat, 'Bank-Year 键集一致', 'PASS', '完全匹配')

    # 7c. 数值一致性
    if only_40 == 0 and only_51 == 0:
        m = panel_40.merge(panel_51, on=['target_bank', 'year'], suffixes=('_40', '_51'))
        for col in ['n_articles', 'llm_vote_tone_full', 'ln_news_coverage']:
            c40 = f'{col}_40'
            c51 = f'{col}_51'
            if c40 in m.columns and c51 in m.columns:
                diff = (m[c40].fillna(-999) - m[c51].fillna(-999)).abs().max()
                if diff > 1e-6:
                    record(cat, f'{col} 数值一致', 'FAIL', f'最大差异={diff:.6e}')
                else:
                    record(cat, f'{col} 数值一致', 'PASS', f'完全一致')

    # 7d. 51 面板应包含额外的 nf_ 列
    nf_cols = [c for c in panel_51.columns if c.startswith('nf_')]
    if len(nf_cols) > 0:
        record(cat, '51面板非金融科技变量', 'PASS',
               f'{len(nf_cols)} 个 nf_ 前缀变量存在')
    else:
        record(cat, '51面板非金融科技变量', 'WARN', '未找到 nf_ 前缀变量')


# ============================================================================
# 8. 描述性统计摘要
# ============================================================================

def audit_descriptive_stats(panel: pd.DataFrame, name: str):
    """生成核心变量的描述性统计。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 描述性统计摘要")
    logger.info("=" * 70)
    cat = f"{name}/描述统计"

    core_vars = [
        'n_articles', 'ln_news_coverage', 'media_breadth',
        'llm_vote_tone_full', 'llm_vote_tone_ctx',
        'llm_vote_cont_full', 'llm_vote_cont_ctx',
        'pos_frac_full', 'neg_frac_full',
        'dict_avg_tone_full', 'bert_avg_pos_full',
        'llm_vote_tone_vw_full', 'llm_vote_tone_mw_full', 'llm_vote_tone_hw_full',
        'fintech_share', 'nf_ln_coverage', 'all_ln_coverage',
        'avg_herd_weight', 'avg_llm_conf_full',
        'washing_ratio', 'jf_coefficient_full',
    ]

    existing = [c for c in core_vars if c in panel.columns]
    if existing:
        stats = panel[existing].describe().T
        stats['missing_pct'] = panel[existing].isna().mean()
        stats['n_valid'] = panel[existing].notna().sum()

        logger.info("  核心变量描述性统计:")
        for var in existing:
            s = stats.loc[var]
            logger.info(f"  {var:40s} | n={int(s['n_valid']):>6,} | "
                        f"mean={s['mean']:>8.4f} | std={s['std']:>8.4f} | "
                        f"min={s['min']:>8.4f} | max={s['max']:>8.4f} | "
                        f"miss={s['missing_pct']:.1%}")

        record(cat, '描述性统计', 'PASS', f'{len(existing)} 个核心变量统计已生成')

    # 零新闻诊断
    if 'n_articles' in panel.columns:
        zero_pct = (panel['n_articles'] == 0).mean()
        record(cat, '零新闻Bank-Year占比', 'PASS' if zero_pct < 0.3 else 'WARN',
               f'{zero_pct:.1%}')


# ============================================================================
# 9. 网络指标审核
# ============================================================================

def audit_network_variables(panel: pd.DataFrame, name: str):
    """审核银行共现网络中心度变量。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 网络变量审核")
    logger.info("=" * 70)
    cat = f"{name}/网络"

    net_cols = [c for c in panel.columns
                if c.startswith('bank_') and c.endswith('_cent')]
    if not net_cols:
        record(cat, '网络变量存在性', 'WARN', '未找到网络中心度变量')
        return

    record(cat, '网络变量存在性', 'PASS', f'{len(net_cols)} 个中心度变量')

    # 值域检查
    for col in net_cols:
        valid = panel[col].dropna()
        if len(valid) > 0:
            if valid.min() < -0.01:
                record(cat, f'{col}值域', 'WARN', f'存在负值: min={valid.min():.6f}')

    # 全局网络指标年度变异
    global_cols = [c for c in panel.columns if c.startswith('net_') and c.endswith('_yr')]
    for col in global_cols:
        if col in panel.columns:
            unique_per_year = panel.groupby('year')[col].nunique()
            multi_val_years = (unique_per_year > 1).sum()
            if multi_val_years > 0:
                record(cat, f'{col}年度唯一性', 'FAIL',
                       f'{multi_val_years} 个年份内有多个不同值 (应为年度常数)')


# ============================================================================
# 10. 地理变量审核
# ============================================================================

def audit_geography_variables(panel: pd.DataFrame, name: str):
    """审核银行地理变量的完整性和一致性。"""
    logger.info("=" * 70)
    logger.info(f"[{name}] 地理变量审核")
    logger.info("=" * 70)
    cat = f"{name}/地理"

    # 10a. bank_province / bank_city 同一银行跨年应一致
    for geo_col in ['bank_province', 'bank_city']:
        if geo_col in panel.columns:
            bank_geo = panel.groupby('target_bank')[geo_col].nunique()
            inconsistent = (bank_geo > 1).sum()
            if inconsistent > 0:
                bad_banks = bank_geo[bank_geo > 1].index.tolist()
                record(cat, f'{geo_col}跨年一致性', 'FAIL',
                       f'{inconsistent} 家银行跨年变化: {bad_banks[:5]}')
            else:
                miss_pct = panel[geo_col].isna().mean()
                record(cat, f'{geo_col}跨年一致性', 'PASS',
                       f'一致, 缺失率={miss_pct:.1%}')

    # 10b. bank_zone 应与 bank_province 对应
    if 'bank_zone' in panel.columns and 'bank_province' in panel.columns:
        miss_zone = panel['bank_zone'].isna().mean()
        record(cat, 'bank_zone 覆盖率', 'PASS' if miss_zone < 0.1 else 'WARN',
               f'缺失率={miss_zone:.1%}')


# ============================================================================
# 主函数
# ============================================================================

def main():
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("===  52_stata_data_audit: Stata 用面板数据全面审核  ===")
    logger.info("=" * 70)

    # --- 加载数据 ---
    panel_40_path = os.path.join(OUTPUT_DIR,
        FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet'))
    panel_51_path = os.path.join(OUTPUT_DIR,
        FILENAMES.get('output_51_panel_controls', '51_panel_with_controls.parquet'))
    dta_40_path = os.path.splitext(panel_40_path)[0] + '.dta'
    dta_51_path = os.path.splitext(panel_51_path)[0] + '.dta'

    panel_40 = None
    panel_51 = None

    if os.path.exists(panel_40_path):
        panel_40 = pd.read_parquet(panel_40_path)
        logger.info(f"已加载 40_panel_yearly: {panel_40.shape}")
    else:
        logger.error(f"40_panel_yearly 不存在: {panel_40_path}")

    if os.path.exists(panel_51_path):
        panel_51 = pd.read_parquet(panel_51_path)
        logger.info(f"已加载 51_panel_with_controls: {panel_51.shape}")
    else:
        logger.warning(f"51_panel_with_controls 不存在: {panel_51_path}")

    # --- 审核 40_panel_yearly ---
    if panel_40 is not None:
        audit_panel_structure(panel_40, '40面板')
        audit_variable_quality(panel_40, '40面板')
        audit_sentiment_consistency(panel_40, '40面板')
        audit_iv_variables(panel_40, '40面板')
        audit_did_variables(panel_40, '40面板')
        audit_stata_compatibility(panel_40, dta_40_path, '40面板')
        audit_network_variables(panel_40, '40面板')
        audit_geography_variables(panel_40, '40面板')
        audit_descriptive_stats(panel_40, '40面板')

    # --- 审核 51_panel_with_controls ---
    if panel_51 is not None:
        audit_panel_structure(panel_51, '51面板')
        audit_variable_quality(panel_51, '51面板')
        audit_sentiment_consistency(panel_51, '51面板')
        audit_iv_variables(panel_51, '51面板')
        audit_did_variables(panel_51, '51面板')
        audit_stata_compatibility(panel_51, dta_51_path, '51面板')
        audit_network_variables(panel_51, '51面板')
        audit_geography_variables(panel_51, '51面板')
        audit_descriptive_stats(panel_51, '51面板')

    # --- 跨文件一致性 ---
    if panel_40 is not None and panel_51 is not None:
        audit_cross_file_consistency(panel_40, panel_51)

    # --- 汇总报告 ---
    logger.info("=" * 70)
    logger.info("===  审核汇总  ===")
    logger.info("=" * 70)

    df_results = pd.DataFrame(audit_results)
    n_pass = (df_results['status'] == 'PASS').sum()
    n_warn = (df_results['status'] == 'WARN').sum()
    n_fail = (df_results['status'] == 'FAIL').sum()
    n_total = len(df_results)

    logger.info(f"  总检查项: {n_total}")
    logger.info(f"  ✅ PASS: {n_pass} ({n_pass/max(n_total,1):.1%})")
    logger.info(f"  ⚠️ WARN: {n_warn} ({n_warn/max(n_total,1):.1%})")
    logger.info(f"  ❌ FAIL: {n_fail} ({n_fail/max(n_total,1):.1%})")

    if n_fail > 0:
        logger.error("")
        logger.error("  === 失败项详情 ===")
        for _, row in df_results[df_results['status'] == 'FAIL'].iterrows():
            logger.error(f"  ❌ [{row['category']}] {row['check']}: {row['detail']}")

    if n_warn > 0:
        logger.warning("")
        logger.warning("  === 警告项摘要 ===")
        for _, row in df_results[df_results['status'] == 'WARN'].iterrows():
            logger.warning(f"  ⚠️ [{row['category']}] {row['check']}: {row['detail']}")

    # 导出审核结果
    report_dir = os.path.join(OUTPUT_DIR, 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, '52_stata_data_audit.csv')
    df_results.to_csv(report_path, index=False, encoding='utf-8-sig')
    logger.info(f"  审核报告已导出: {report_path}")

    elapsed = time.time() - start_time
    logger.info(f"  总耗时: {elapsed:.1f}s")
    logger.info("52_stata_data_audit 完成 ✓")

    # 返回状态码
    return 1 if n_fail > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
