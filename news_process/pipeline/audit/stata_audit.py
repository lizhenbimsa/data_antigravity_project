"""
news_process.pipeline.audit.stata_audit — Stata 用面板数据最高标准审核与验证
==============================================================================

迁移说明 (Phase 7a-8)：
    本模块由原 root script ``81_stata_data_audit.py`` body 迁入。
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
  data/processed/eval_reports/81_stata_data_audit.csv    (审核摘要表)
  logs/81_stata_data_audit.log                           (详细日志)

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 81_stata_data_audit.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读最终交付 Stata 的面板数据 — 40_panel_yearly.parquet 与同名 .dta、51_panel_with_controls.parquet 与同名 .dta (按存在性消费; 40 缺则 error, 51 缺则 warning 跳过该半套审核)。40_article_bank_level 在本模块 docstring 提及但 main() 实际只加载 40/51 两套面板。

**处理步骤 (main, 顶刊级面板审核)**: 对 40 / 51 各跑 9 个 per-file 只读审核函数, 再加 1 个跨文件函数, 共 **10 类**检查 (草稿原列 7 类有遗漏)。经 `record(category, check_name, status, detail, severity='INFO')` 收集 PASS/WARN/FAIL —
1. 面板结构完整性 (`audit_panel_structure`): (target_bank, year) 唯一键 (Wooldridge 2010) + 平衡率 (实际行/理论行 n_banks×年跨度, Baltagi 2021) + 银行名/年份合理性 + 列数。
2. 变量质量 (`audit_variable_quality`): 缺失率/异常值(5σ)/值域合规/哑变量0-1/Inf。
3. 情感指标一致性 (`audit_sentiment_consistency`): pos+neg+neutral frac 恒等、全 *_frac∈[0,1]、情感计数≤物理篇数、三轨 pairwise 相关、LLM 模型间相关、VW/MW/HW 加权恒等式、fintech 分类恒等式。
4. IV 有效性预检 (`audit_iv_variables`): Bartik 份额和≤1(排除 other 类, GPSS 2020)、LOO 排除自身、Bartik IV 变异性。
5. DID 变量合规 (`audit_did_variables`): treated/post 0-1 编码、treated-post 时间逻辑、event-study lead/lag 互斥。
6. Stata 兼容性 (`audit_stata_compatibility`): 列名合规、.dta 可读性/行数一致/数值精度(含 NaN 对齐对称校验)、nullable dtype。
7. 网络变量 (`audit_network_variables`): 中心度列存在性/值域/年度常量校验。
8. 地理变量 (`audit_geography_variables`): bank_province/city 跨年一致性、bank_zone 覆盖率。
9. 描述性统计 (`audit_descriptive_stats`): 核心变量 describe + 零新闻占比。
10. 跨文件一致性 (`audit_cross_file_consistency`, 仅 40+51 均存在时): 行数/键集/核心变量值/51 含 nf_ 列。
汇总 audit_results → DataFrame → to_csv (eval_reports/81_stata_data_audit.csv)。

**外部依赖**: 纯 pandas/numpy 只读; 无 LLM/Embedding/网络。无 timeout 约束 (不在 DAG)。确定性强 (只读校验)。规范调用: `python -m news_process.pipeline.audit.stata_audit` 或 `python news_process/81_stata_data_audit.py`。

**DAG 位置**: 不在 DAG。逻辑上是 stage 45/46/51 的下游质检关卡, 但作为 user-CLI 手动触发, 与流水线主链解耦。

■ 白话说明

**这一步是什么**: 这是数据交付前的质检员。当面板表格和 .dta 文件都做好、准备交给经济学家跑回归之前, 这个工具会把它们从头到脚体检一遍: 有没有同一家银行同一年出现两行 (重复)、面板缺了多少格、各种情感指标算得自不自洽、工具变量的份额加起来是不是 ≤1、DID 的处理前后标记有没有搞反、列名符不符合 Stata 规矩、网络/地理变量稳不稳、两张表 (主面板和加了对照变量的面板) 对得上对不上。最后出一张体检报告 (CSV) 列出每一项是通过、警告还是失败。

**为什么需要它**: 流水线自动跑出来的数据可能藏着不易察觉的毛病, 一旦带病进了回归, 论文结果就不可信。这个工具相当于交付前的安检, 把问题拦在送进 Stata 之前, 省得跑出一堆表才发现数据有坑。它是用户想用的时候手动跑的, 不是流水线自动环节。

**做得好不好的影响**: 它不改数据、只挑毛病, 所以不会直接影响面板数值。但它是最后一道人工眼睛: 如果它能抓出重复键、缺失异常、变量不自洽这些问题, 研究者就能在写论文前修好; 如果跳过这一步, 一些隐蔽错误可能一路带到发表。可以理解为买保险——平时用不上, 出事时能救命。
========================================================================
"""

import os
import platform
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
from news_process.core.logging import pct4, setup_logging, sig4

warnings.filterwarnings('ignore', category=FutureWarning)

# ============================================================================
# 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "81_stata_data_audit"
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
        record(cat, '面板平衡性', 'PASS', f'平衡率={pct4(balance_ratio)} (完全平衡)')
    elif balance_ratio >= 0.95:
        record(cat, '面板平衡性', 'WARN', f'平衡率={pct4(balance_ratio)} (近似平衡)')
    else:
        record(cat, '面板平衡性', 'FAIL', f'平衡率={pct4(balance_ratio)} (不平衡!)')

    # 缺年诊断 (log-only, 不进 record/CSV → golden-safe): 平衡率 <1 时列出年份覆盖
    # 不全的银行样本, 便于定位"哪些 bank 缺哪些年", 比单一 balance_ratio 更可操作。
    try:
        if 0 < balance_ratio < 0.999 and n_years > 1:
            _full_years = set(range(int(y_min), int(y_max) + 1))
            _gaps = []
            for _bk, _g in panel.groupby('target_bank'):
                _have = {int(y) for y in _g['year'].dropna().unique()}
                _missing = sorted(_full_years - _have)
                if _missing:
                    _gaps.append((_bk, _missing))
            if _gaps:
                logger.info(f"  缺年诊断: {len(_gaps):,} 家银行年份覆盖不全 "
                            f"(占 {pct4(len(_gaps) / max(n_banks, 1))}); 样本前 5 家:")
                for _bk, _missing in _gaps[:5]:
                    _disp = f"{_missing[:6]}…" if len(_missing) > 6 else f"{_missing}"
                    logger.info(f"      {_bk}: 缺 {len(_missing):,} 年 {_disp}")
    except Exception as _e:  # noqa: BLE001
        logger.debug(f"  缺年诊断跳过 (不影响审核): {_e}")

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
            detail = '; '.join([f'{c}={pct4(p)}' for c, n, p in high_miss[:10]])
            record(cat, '高缺失率变量(>50%)', 'WARN',
                   f'{len(high_miss)} 个变量: {detail}')

        # 关键变量缺失检查 (三轨: full/ctx/ss)
        key_vars = [
            ('n_articles', 0.0, '新闻篇数'),
            ('llm_vote_tone_full', None, 'LLM投票情感(全文)'),
            ('llm_vote_tone_ctx', None, 'LLM投票情感(上下文)'),
            ('llm_vote_tone_ss', None, 'LLM投票情感(银行+金科同句)'),
            ('ln_news_coverage', None, '新闻覆盖度对数'),
        ]
        for var, expected_miss, label in key_vars:
            if var in panel.columns:
                miss_pct = panel[var].isna().mean()
                if expected_miss is not None:
                    if miss_pct > expected_miss + 0.01:
                        record(cat, f'关键变量缺失-{label}', 'FAIL',
                               f'{var} 缺失率={pct4(miss_pct)}, 预期≤{pct4(expected_miss)}')
                    else:
                        record(cat, f'关键变量缺失-{label}', 'PASS',
                               f'{var} 缺失率={pct4(miss_pct)}')
                else:
                    # 情感变量: 在有新闻的行应非缺失
                    # metric-audit 2026-06-02: 用 LLM-valid 篇数(重构后 n_articles=物理),
                    # 缺列回退 n_articles, 保旧行为(不对 LLM 全失败行误 WARN).
                    _nac_mv = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
                    has_news = panel[_nac_mv] > 0 if _nac_mv in panel.columns else pd.Series(True, index=panel.index)
                    miss_in_news = panel.loc[has_news, var].isna().mean() if has_news.sum() > 0 else 0
                    if miss_in_news > 0.05:
                        record(cat, f'关键变量缺失-{label}', 'WARN',
                               f'{var} 在有新闻行的缺失率={pct4(miss_in_news)}')
                    else:
                        record(cat, f'关键变量缺失-{label}', 'PASS',
                               f'{var} 在有新闻行缺失率={pct4(miss_in_news)}')
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

    # 离散情感 tone 应在 [-1, 1] (三轨: full/ctx/ss; ss 列缺失时该轨自动跳过)
    for col in ['llm_vote_tone_full', 'llm_vote_tone_ctx', 'llm_vote_tone_ss']:
        if col in panel.columns:
            valid = panel[col].dropna()
            if len(valid) > 0:
                if valid.min() < -1.001 or valid.max() > 1.001:
                    record(cat, f'{col}值域', 'FAIL',
                           f'超出[-1,1]: min={sig4(valid.min())}, max={sig4(valid.max())}')
                else:
                    record(cat, f'{col}值域', 'PASS',
                           f'值域=[{sig4(valid.min())}, {sig4(valid.max())}], mean={sig4(valid.mean())}')

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
                               f'{outliers} 个观测超出5σ (mean={sig4(mean)}, std={sig4(std)})')

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
    # → 误 FAIL, 而 audit_sentiment_consistency 的 FAIL 会使 stage 81 退出码=1.
    _nac = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
    # 缺列兜底 (与 audit_variable_quality:198 对称; 终验复核修: _nac 改写不得丢失
    # 原 graceful 守卫, 否则无 count 列的 panel 抛 KeyError).
    has_news = panel[_nac] > 0 if _nac in panel.columns else pd.Series(True, index=panel.index)
    p = panel[has_news]

    # 3a. pos_frac + neg_frac + neutral_frac 恒等式 (三轨: full/ctx/ss;
    # ss = 银行+金科同句共现轨, 列缺失时该轨经下方 in-columns 守卫自动跳过)
    for track in ['_full', '_ctx', '_ss']:
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
                       f'所有行满足约束, max_sum={sig4(row_sum.max())}')

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
            _oob_frac.append(f'{c}[{sig4(s.min())},{sig4(s.max())}]')
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
    # 物理篇数 14/4/1/2 ≥ ctx pos+neg 13/2/1/2, 是合法轨间独立成功率差异, 非双计 bug).
    # 旧冻结 panel (无 n_articles_llm_valid → n_articles 实为 full-valid 非物理) 下该
    # 上界本身偏小, _ctx 越界为已知口径限制 → WARN; 重生 panel (n_articles=物理) 上
    # 仍越界才是真双重计数 → FAIL.
    # 三轨 (full/ctx/ss); ss = 银行+金科同句共现轨, 列缺失时经 in-columns 守卫跳过。
    _is_physical_count = 'n_articles_llm_valid' in panel.columns
    for track in ['_full', '_ctx', '_ss']:
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
                         else ' (旧 panel n_articles=full-valid 非物理, 轨间独立成功率差异已知, 降 WARN; 重生后复测)')
                record(cat, f'情感计数恒等式 ({track})', _status,
                       f'{neg_neutral} 行 pos+neg > n_articles{_note}')
            else:
                record(cat, f'情感计数恒等式 ({track})', 'PASS',
                       '所有行满足 pos+neg ≤ n_articles')

    # 3c. 跨轨道相关性 — 三轨两两 pairwise (full_ctx / full_ss / ctx_ss)
    # ss = 银行+金科同句共现轨; 任一轨 tone 列缺失时该 pair 自动跳过 (graceful)。
    # 注意: 这是诊断披露 (相关高=对归因窗口稳健), 三轨互为稳健性, 去留不由相关性决定。
    _tone_pairs = [
        ('llm_vote_tone_full', 'llm_vote_tone_ctx', 'Full-Ctx'),
        ('llm_vote_tone_full', 'llm_vote_tone_ss', 'Full-SS'),
        ('llm_vote_tone_ctx', 'llm_vote_tone_ss', 'Ctx-SS'),
    ]
    for col_a, col_b, pair_label in _tone_pairs:
        if col_a in p.columns and col_b in p.columns:
            valid = p[[col_a, col_b]].dropna()
            if len(valid) > 10:
                r = valid[col_a].corr(valid[col_b])
                if r < 0.5:
                    record(cat, f'{pair_label} 跨轨道相关', 'WARN',
                           f'Pearson r={sig4(r)} < 0.5, 该对轨道分歧较大')
                else:
                    record(cat, f'{pair_label} 跨轨道相关', 'PASS',
                           f'Pearson r={sig4(r)}')

    # 3d. LLM 模型间情感一致性
    llm_models = ['gpt54nano', 'gemini31', 'deepseekv4']  # v3: 真三家族 (OpenAI + Google + DeepSeek)
    llm_tone_cols = [f'{m}_tone_full' for m in llm_models if f'{m}_tone_full' in p.columns]
    if len(llm_tone_cols) >= 2:
        corrs = p[llm_tone_cols].corr()
        # 提取上三角 (排除对角线的 1.0) 的最小值
        upper_tri = corrs.values[np.triu_indices_from(corrs.values, k=1)]
        min_pair_corr = upper_tri.min() if len(upper_tri) > 0 else 1.0
        record(cat, 'LLM模型间一致性', 'PASS' if min_pair_corr > 0.5 else 'WARN',
               f'最小成对相关={sig4(min_pair_corr)} ({len(llm_tone_cols)}个模型)')

    # 3e. 加权均值恒等式 (VW, MW, HW) — 三轨 (full/ctx/ss)
    # 列名模式 (与 encode.py 实际产出对齐):
    #   VW: tone=llm_vote_tone_vw{track}, 分子=llm_vote_score_w_sum{track}
    #       (⚠ 分子真名带 _w_ 而非 _vw_, 见 encode.py 聚合 llm_vote_score_w_sum)
    #   MW: tone=llm_vote_tone_mw{track}, 分子=llm_vote_score_mw_sum{track}
    #   HW: tone=llm_vote_tone_hw{track}, 分子=llm_vote_score_hw_sum{track}
    # fix(omni-g-stata-audit-01, 2026-06-11): LLM 族期望分母优先用 valid-mask 列
    # sum_wd_{wtag}_llm{track} (与 encode.py::_llm_denom 2026-06-10 修复对齐) —
    # 否则 valid-mask 重生面板上按物理分母重算恒等式必误 FAIL (含 LLM-invalid 文章
    # 的 bank-year diff 可达 0.5) 并把 stage 81 退出码打成 1; 缺 mask 列回退物理分母
    # (同 encode 回退契约, 旧冻结 panel 兼容), detail 注明所用分母口径。
    # fix(omni-g-stata-audit-02, 2026-06-11): 修正两处陈旧列名导致的静默死亡 —
    # VW 分子 llm_vote_score_vw_sum_full → llm_vote_score_w_sum{track}; HW 物理
    # 分母 sum_herd_weight → sum_herd_weight_full/_ctx/_ss (v3.6.0 多轨化后无后缀
    # 单列已不存在)。并把 else 兜底改为: 三种权重缺任一所需列即 record WARN, 杜绝静默跳过。
    # 三轨 (full/ctx/ss); ss 轨缺所需列时经 else 分支 record WARN (不静默跳过)。
    for track in ['_full', '_ctx', '_ss']:
        for wt_type, num_tpl, phys_denom_tpl in [
            ('VW', 'llm_vote_score_w_sum{track}', 'sum_mention_density'),
            ('MW', 'llm_vote_score_mw_sum{track}', 'sum_media_authority_weight'),
            ('HW', 'llm_vote_score_hw_sum{track}', 'sum_herd_weight{track}'),
        ]:
            wt_sfx = wt_type.lower()
            tone_col = f'llm_vote_tone_{wt_sfx}{track}'
            sum_col = num_tpl.format(track=track)
            mask_col = f'sum_wd_{wt_sfx}_llm{track}'        # valid-mask 分母 (encode 同名)
            phys_col = phys_denom_tpl.format(track=track)   # 物理分母 (回退)
            if mask_col in p.columns:
                denom_col, denom_kind = mask_col, 'valid-mask'
            elif phys_col in p.columns:
                denom_col, denom_kind = phys_col, 'physical'
            else:
                denom_col, denom_kind = None, None
            check = f'{wt_type}加权恒等式 ({track})'
            if tone_col in p.columns and sum_col in p.columns and denom_col is not None:
                denom = p[denom_col].replace(0, np.nan)
                expected = p[sum_col] / denom
                actual = p[tone_col]
                diff = (actual - expected).abs().dropna()
                if len(diff) > 0:
                    max_diff = float(diff.max())
                    record(cat, check, 'FAIL' if max_diff > 1e-8 else 'PASS',
                           f'最大差异={sig4(max_diff)} (分母口径={denom_kind}:{denom_col})')
                else:
                    record(cat, check, 'WARN',
                           f'无可比对行 (tone/expected 全缺失), 分母口径={denom_kind}:{denom_col}')
            else:
                missing = [label for label, ok in [
                    (tone_col, tone_col in p.columns),
                    (sum_col, sum_col in p.columns),
                    (f'{mask_col}|{phys_col}', denom_col is not None),
                ] if not ok]
                record(cat, check, 'WARN', f'缺列跳过检验: {missing}')

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
    # 白话: Bartik 工具变量 = "本行初始的媒体类别构成份额 × 各类别全国趋势"
    # 加权求和。份额是比例, 加起来理应 ≤ 1; 这里只在份额和 > 1 (溢出, 真错误)
    # 时报 FAIL, 和 < 1 是因为刻意丢掉了 'other' 类, 属正常。
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
                           f'{over_one}行份额和>1.01 (溢出!), max={sig4(max_sum)}')
                elif mean_sum < 0.5:
                    # 均值太低可能说明份额计算有问题
                    record(cat, f'Bartik份额归一-{prefix}', 'WARN',
                           f'份额均值={sig4(mean_sum)}偏低, 可能other类占比过高, '
                           f'{len(share_cols)}个份额列, range=[{sig4(min_sum)}, {sig4(max_sum)}]')
                else:
                    record(cat, f'Bartik份额归一-{prefix}', 'PASS',
                           f'{len(share_cols)}个份额列, 均值={sig4(mean_sum)}, '
                           f'range=[{sig4(min_sum)}, {sig4(max_sum)}]')

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
                           f'r={sig4(r)} (截面数据, 负相关可由LOO数学性质导致)')
                elif abs(r) < 0.05:
                    record(cat, f'LOO-IV相关性({geo})', 'WARN',
                           f'r={sig4(r)}, 相关性极弱 — 可能弱IV风险')
                else:
                    record(cat, f'LOO-IV相关性({geo})', 'PASS',
                           f'r={sig4(r)}')

    # 4c. Zone LOO IV
    zone_col = 'zone_leave1out_tone_full'
    if zone_col in panel.columns:
        valid = panel[zone_col].dropna()
        record(cat, 'Zone LOO IV', 'PASS',
               f'有效值={len(valid):,}, 缺失率={pct4(panel[zone_col].isna().mean())}')

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

        # 5b-2. fix(log-round4-2026-06-20): DiD 可识别性退化守卫 — post 或 treated 无变异
        #   (T=2 伪两年常见: post 全 0 = 无政策后期窗口) → DiD 结构不可识别, 下方 5c/5e 的
        #   treated-post 逻辑 / event-study 互斥 PASS 均为【空集恒真 (vacuous)】, 不代表识别有效。
        #   loud WARN 披露, 防 referee 误读 all-PASS 为"DiD 设计成立"。生产 T=18 方可识别。
        if post_col in panel.columns:
            _post_uniq = panel[post_col].dropna().nunique()
            _treated_uniq = panel[treated_col].dropna().nunique()
            if _post_uniq <= 1 or _treated_uniq <= 1:
                record(cat, f'{policy} DiD 可识别性', 'WARN',
                       f'post/treated 无变异 (post_uniq={_post_uniq}, treated_uniq={_treated_uniq}; '
                       f'T=2 伪两年常见) → DiD 结构不可识别, 下方 treated-post/event-study 的 PASS '
                       f'为空集恒真 (vacuous) 非识别有效; 生产 T=18 (2007–2024) 方可识别。')

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
            # fix(omni-g-stata-audit-03, 2026-06-11): 旧实现 (dta-pq).abs().max() 在
            # 任一侧为 NaN 的位置产生 NaN diff, 被 .max() skipna 静默吞掉 → 值在
            # .dta 写出端被静默改写为缺失 (如 Int8∈[101,126] 落 Stata extended
            # missing, KNOWN-OPEN ⑥ 的腐蚀模式) 时 max_diff=0.0 恒 PASS, 审计对该
            # "值→缺失"腐蚀类结构性失明。现补 NaN 对称比对: 逐位缺失掩码须对齐
            # (含非空计数), 不对齐即 FAIL; 数值精度仅在双侧均非缺失的位置比较。
            if len(dta) == len(panel):
                for col in ['llm_vote_tone_full', 'n_articles', 'ln_news_coverage']:
                    dta_col = col[:32]  # Stata 列名截断兼容
                    if dta_col in dta.columns and col in panel.columns:
                        dta_vals = dta[dta_col].astype(float).to_numpy()
                        pq_vals = panel[col].astype(float).to_numpy()
                        dta_nan = np.isnan(dta_vals)
                        pq_nan = np.isnan(pq_vals)
                        n_misalign = int((dta_nan != pq_nan).sum())
                        if n_misalign > 0:
                            record(cat, f'.dta NaN对齐-{col}', 'FAIL',
                                   f'{n_misalign} 处缺失位置不对齐 '
                                   f'(.dta 非空={int((~dta_nan).sum())} vs '
                                   f'.parquet 非空={int((~pq_nan).sum())}; '
                                   f'疑似值被写出端静默改写为缺失)')
                        both = ~(dta_nan | pq_nan)
                        diff = float(np.abs(dta_vals[both] - pq_vals[both]).max()) if both.any() else 0.0
                        if diff > 0.001:
                            record(cat, f'.dta 精度-{col}', 'WARN',
                                   f'最大差异={sig4(diff)}')
                        else:
                            record(cat, f'.dta 精度-{col}', 'PASS',
                                   f'精度一致 (max_diff={sig4(diff)}, 含 NaN 位置对称校验)')
            else:
                # 行数不一致已由 6c record FAIL; 逐位比对无意义, 显式 WARN 不静默
                record(cat, '.dta 精度检查', 'WARN', '行数不一致, 跳过逐位精度比对 (见 6c)')

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
                    record(cat, f'{col} 数值一致', 'FAIL', f'最大差异={sig4(diff)}')
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

    # 核心变量描述统计 (三轨 full/ctx/ss; ss 列缺失时经下方 `if c in panel.columns`
    # 静默过滤, 不报缺失 — 镜像 ctx 既有行为)。
    core_vars = [
        'n_articles', 'ln_news_coverage', 'media_breadth',
        'llm_vote_tone_full', 'llm_vote_tone_ctx', 'llm_vote_tone_ss',
        'llm_vote_cont_full', 'llm_vote_cont_ctx', 'llm_vote_cont_ss',
        'pos_frac_full', 'neg_frac_full',
        'dict_avg_tone_full', 'bert_avg_pos_full',
        'llm_vote_tone_vw_full', 'llm_vote_tone_mw_full', 'llm_vote_tone_hw_full',
        'fintech_share', 'nf_ln_coverage', 'all_ln_coverage',
        # fix(omni-g-panel-export-02, 2026-06-11): v3.6.0 多轨化后无后缀
        # avg_herd_weight 列已不存在 (encode.py 产出 *_full/_ctx/_ss), 陈旧名被
        # `if c in panel.columns` 静默过滤 → herd 权重从未进描述统计; 改三轨名。
        'avg_herd_weight_full', 'avg_herd_weight_ctx', 'avg_herd_weight_ss',
        'avg_llm_conf_full',
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
            # describe() 已算出 25%/50%/75% 三分位 (此前仅用 mean/std 而丢弃)。
            # 白话: 情感/覆盖度多为右偏分布, 均值易被极端值拉偏; 补报
            # median (50%) 作 outlier-robust 位置量 + 四分位区间 [Q1, Q3]
            # (IQR=Q3−Q1) 作稳健离散量, 与 mean/std 互证分布形状。log-only。
            logger.info(f"  {var:40s} | n={int(s['n_valid']):>6,} | "
                        f"mean={sig4(s['mean']):>9} | std={sig4(s['std']):>9} | "
                        f"median={sig4(s['50%']):>9} | "
                        f"IQR=[{sig4(s['25%'])}, {sig4(s['75%'])}] | "
                        f"min={sig4(s['min']):>9} | max={sig4(s['max']):>9} | "
                        f"miss={pct4(s['missing_pct'])}")

        record(cat, '描述性统计', 'PASS', f'{len(existing)} 个核心变量统计已生成')

    # 零新闻诊断
    if 'n_articles' in panel.columns:
        zero_pct = (panel['n_articles'] == 0).mean()
        record(cat, '零新闻Bank-Year占比', 'PASS' if zero_pct < 0.3 else 'WARN',
               f'{pct4(zero_pct)}')


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
                record(cat, f'{col}值域', 'WARN', f'存在负值: min={sig4(valid.min())}')

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
                       f'一致, 缺失率={pct4(miss_pct)}')

    # 10b. bank_zone 应与 bank_province 对应
    if 'bank_zone' in panel.columns and 'bank_province' in panel.columns:
        miss_zone = panel['bank_zone'].isna().mean()
        record(cat, 'bank_zone 覆盖率', 'PASS' if miss_zone < 0.1 else 'WARN',
               f'缺失率={pct4(miss_zone)}')


# ============================================================================
# 主函数
# ============================================================================

def _log_environment_and_config(panel_40_path: str, panel_51_path: str,
                                dta_40_path: str, dta_51_path: str) -> None:
    """打印 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调阈值、依据哪些方法学文献"
    一次性落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / 控制流
    (golden-safe)。失败时仅记 warning, 不让本块崩阶段。
    """
    try:
        report_path = os.path.join(OUTPUT_DIR, 'eval_reports', '81_stata_data_audit.csv')

        # ① 🧭 项目 / 环境信息
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (Stata 用面板交付前质检; user-CLI, 不在 DAG)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.15.0")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · numpy={np.__version__} | pandas={pd.__version__}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 pandas/numpy 只读校验, 无 LLM·Embedding·网络 ($0), 逐位可复现")

        # ② 📂 输入 / 输出文件
        logger.info("  📂 输入 / 输出文件 (config/paths.yaml::output_dir + filenames)")
        logger.info(f"     · 输入主面板: {panel_40_path} (+ 同名 .dta: {dta_40_path})")
        logger.info(f"     · 输入对照面板: {panel_51_path} (+ 同名 .dta: {dta_51_path})")
        logger.info(f"     · 输出报告: {report_path} (PASS/WARN/FAIL 体检表 CSV)")

        # ③ ⚙ 运行配置 (本阶段的硬编码审核阈值 / 容差)
        logger.info("  ⚙ 运行配置 (审核阈值 / 容差; 只读校验, 无 YAML 可调参数)")
        logger.info(f"     · 平衡率判读: 完全平衡≥{sig4(0.999)} / 近似平衡≥{sig4(0.95)} / 否则不平衡")
        logger.info(f"     · 异常值阈: |x−mean| > {sig4(5.0)}σ (情感指标 5σ 离群)")
        logger.info(f"     · Bartik 份额溢出阈: 行和 > {sig4(1.01)} (排除 other 类后理应≤1)")
        logger.info(f"     · 加权恒等式容差: max_diff > {sig4(1e-8)} 即 FAIL")
        logger.info(f"     · .dta 精度容差: max_diff > {sig4(0.001)} 即 WARN; 跨文件一致 > {sig4(1e-6)} 即 FAIL")
        logger.info(f"     · 弱 IV 阈: |LOO-IV r| < {sig4(0.05)} (多年面板) | 跨轨相关 r < {sig4(0.5)} 报分歧")
        logger.info(f"     · 列名合规: ASCII 起首字母/下划线, ≤32 字符 (Stata 标识符规范)")

        # ④ 📖 方法论依据 (参考文献; 仅 emit 经核验注册表中的 DOI)
        logger.info("  📖 方法论依据 (核心审核准则的学术出处)")
        logger.info("     · 面板唯一键约束: Wooldridge, J. M. (2010). Econometric Analysis of Cross "
                    "Section and Panel Data (2nd ed.). MIT Press.")
        logger.info("       → (target_bank, year) 须唯一, 否则银行年固定效应回归崩坏")
        logger.info("     · 面板平衡性诊断: Baltagi, B. H. (2021). Econometric Analysis of Panel "
                    "Data (6th ed.). Springer.")
        logger.info("       → 实际行/理论行 (n_banks × 年跨度) 判读完全/近似/不平衡")
        logger.info("     · Bartik 份额归一: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). "
                    "Bartik instruments: What, when, why, and how. American Economic Review, "
                    "110(8), 2586-2624. https://doi.org/10.1257/aer.20181047")
        logger.info("       → 初始份额 × 全国趋势的 shift-share IV; 排除 other 后份额和理应 ≤1")
        logger.info("     · 面板 TWFE/DiD 适用性 (本审计存在的目的): Wooldridge, J. M. (2025). "
                    "Two-way fixed effects, the two-way Mundlak regression, and "
                    "difference-in-differences estimators. Empirical Economics, 69(5), "
                    "2545–2587. https://doi.org/10.1007/s00181-025-02807-z")
        logger.info("       → (bank, year) 唯一键 + 平衡率审计正是为银行年 TWFE/Mundlak/DiD 估计交付合规面板")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响审核): {e}")


def main():
    start_time = time.time()
    # 运行期阶段计时累计 (各主要子阶段墙钟耗时, 末尾汇总打印; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}

    # ---【功能 banner】交付前面板质检 (黄金范式: 紧随启动日志; 已替换旧短 banner, 不叠加) ---
    logger.info("=" * 72)
    logger.info("阶段 81: Stata 用面板数据审计 (CLI; Baltagi 2021 / Wooldridge 2010 / GPSS 2020)")
    logger.info("=" * 72)
    logger.info("【功能】交付前的数据质检员: 把准备送进 Stata 跑回归的面板表 (40_panel_yearly")
    logger.info("        / 51_panel_with_controls) 与同名 .dta 从头到脚体检一遍, 最后出一张")
    logger.info("        体检报告 (eval_reports/81_stata_data_audit.csv) 列出每项 PASS/WARN/FAIL。")
    logger.info("【方法】对 40/51 各跑 9 类只读审核函数 + 1 类跨文件一致性, 共 10 类: 面板结构")
    logger.info("        (唯一键/平衡率)、变量质量 (缺失率/5σ异常/值域/Inf)、情感一致性 (frac")
    logger.info("        恒等式/三轨相关/VW·MW·HW 加权恒等式)、IV 预检 (Bartik 份额≤1/LOO/变异)、")
    logger.info("        DID 合规 (0-1编码/treated-post 逻辑/event-study 互斥)、Stata 兼容 (列名/")
    logger.info("        .dta 行数·精度·NaN对齐/nullable dtype)、网络/地理变量、描述统计。")
    logger.info("【判读】只读不改数: FAIL=必修硬错 (重复键/份额溢出/恒等式破裂→退出码 1), ")
    logger.info("        WARN=需人工复核的临界/已知口径限制, PASS=该项体检通过; FAIL 越少越好。")
    logger.info("【确定性】纯 pandas/numpy 只读校验, 无 LLM/Embedding/网络, 逐位可复现。")

    # --- 加载数据 ---
    panel_40_path = os.path.join(OUTPUT_DIR,
        FILENAMES.get('output_40_panel_yearly', '40_panel_yearly.parquet'))
    panel_51_path = os.path.join(OUTPUT_DIR,
        FILENAMES.get('output_51_panel_controls', '51_panel_with_controls.parquet'))
    dta_40_path = os.path.splitext(panel_40_path)[0] + '.dta'
    dta_51_path = os.path.splitext(panel_51_path)[0] + '.dta'

    # 项目/环境/输入输出/配置/方法论 富集 banner (日志富集 2026-06-24)
    _log_environment_and_config(panel_40_path, panel_51_path, dta_40_path, dta_51_path)

    panel_40 = None
    panel_51 = None

    _t = time.time()
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
    phase_durations['①加载面板 parquet'] = time.time() - _t

    # --- 审核 40_panel_yearly ---
    _t = time.time()
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
    phase_durations['②审核 40 主面板 (9 类)'] = time.time() - _t

    # --- 审核 51_panel_with_controls ---
    _t = time.time()
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
    phase_durations['③审核 51 对照面板 (9 类)'] = time.time() - _t

    # --- 跨文件一致性 ---
    _t = time.time()
    if panel_40 is not None and panel_51 is not None:
        audit_cross_file_consistency(panel_40, panel_51)
    phase_durations['④跨文件一致性 (40 vs 51)'] = time.time() - _t

    # --- 汇总报告 ---
    logger.info("=" * 70)
    logger.info("===  审核汇总  ===")
    logger.info("=" * 70)

    df_results = pd.DataFrame(audit_results)
    n_pass = (df_results['status'] == 'PASS').sum()
    n_warn = (df_results['status'] == 'WARN').sum()
    n_fail = (df_results['status'] == 'FAIL').sum()
    n_total = len(df_results)

    logger.info(f"  总检查项: {n_total:,}")
    logger.info(f"  ✅ PASS: {n_pass:,} ({pct4(n_pass/max(n_total,1))})")
    logger.info(f"  ⚠️ WARN: {n_warn:,} ({pct4(n_warn/max(n_total,1))})")
    logger.info(f"  ❌ FAIL: {n_fail:,} ({pct4(n_fail/max(n_total,1))})")

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

    # ---【结果分析】把上面 PASS/WARN/FAIL 计数翻译成"数据能不能交付"的判读 ---
    # crash-guard: 整块只读诊断包进 try/except — 本块在导出 CSV 报告之前执行,
    # 若因空 df / 缺列 / dtype 异常抛错会丢失产物, 故失败时仅记 warning 跳过, 不影响写盘。
    logger.info("-" * 72)
    logger.info("【结果分析】交付前体检报告判读 (FAIL=硬错须修, WARN=人工复核, PASS=通过):")
    try:
        if n_total == 0 or 'status' not in df_results.columns:
            # NaN/空守卫: 两面板皆缺 → audit_results 为空, 无任何检查项可判读
            logger.warning("  · 无任何审核结果 (面板皆缺失或未产出检查项), 跳过结果分析。")
        else:
            # (1) 总体通过率 — 纯 PASS 占比, 越接近 100% 越干净
            pass_rate = n_pass / max(n_total, 1)
            if n_fail > 0:
                logger.info(
                    f"  · 总体: {n_total:,} 项检查, PASS {pct4(pass_rate)} / WARN {pct4(n_warn/max(n_total,1))}"
                    f" / FAIL {pct4(n_fail/max(n_total,1))} → 存在 {n_fail:,} 项 FAIL [坏], 数据"
                    "不应直接交付 Stata, 须先按下方失败项修复后重生面板。")
            elif n_warn > 0:
                logger.info(
                    f"  · 总体: {n_total:,} 项检查, 0 FAIL [好], 但有 {n_warn:,} 项 WARN [临界] —"
                    "多为已知口径限制/小样本退化/缺列优雅跳过, 须逐条人工复核确认非真错。")
            else:
                logger.info(
                    f"  · 总体: {n_total:,} 项检查全部 PASS [好], 0 WARN/0 FAIL, 面板可放心交付 Stata。")

            # (2) CRITICAL 级硬错单列 — record(severity='CRITICAL') 仅用于唯一键重复 (最致命)
            if 'severity' in df_results.columns:
                n_critical = int((df_results['severity'] == 'CRITICAL').sum())
                if n_critical > 0:
                    logger.warning(
                        f"  · CRITICAL: {n_critical} 项致命错 (如 (target_bank, year) 唯一键重复) [极坏] —"
                        "面板键非唯一会使所有银行年回归崩坏, 必须最优先修复。")
                else:
                    logger.info("  · CRITICAL: 0 项 [好], (target_bank, year) 面板唯一键约束未被违反。")

            # (3) 按 10 类检查域归并 FAIL/WARN, 定位问题集中在哪个子系统 (结构/情感/IV/DID/Stata/...)
            if n_fail > 0 or n_warn > 0:
                _bad = df_results[df_results['status'].isin(['FAIL', 'WARN'])]
                _by_cat = (
                    _bad.assign(is_fail=(_bad['status'] == 'FAIL'))
                    .groupby('category')
                    .agg(fail=('is_fail', 'sum'), n=('status', 'size'))
                    .sort_values(['fail', 'n'], ascending=False)
                )
                logger.info("  · 问题分布 (按检查域, 优先看 FAIL 多的域):")
                for _cat, _row in _by_cat.head(12).iterrows():
                    _f = int(_row['fail'])
                    _w = int(_row['n']) - _f
                    logger.info(
                        f"      [{_cat}] FAIL={_f} / WARN={_w}"
                        + (" ← 含硬错, 优先修" if _f > 0 else ""))

            # (4) 关键恒等式族单独点名 (情感 frac/计数恒等式、Bartik 份额、加权恒等式) —
            #     这些是论文核心变量的内部自洽性, 破裂直接威胁结果可信度
            _identity_keywords = ('恒等式', '份额归一', 'frac 值域', 'event-study 互斥')
            _identity = df_results[df_results['check'].str.contains(
                '|'.join(_identity_keywords), na=False)]
            if len(_identity) > 0:
                _id_fail = int((_identity['status'] == 'FAIL').sum())
                _id_warn = int((_identity['status'] == 'WARN').sum())
                if _id_fail > 0:
                    logger.warning(
                        f"  · 核心恒等式族: {len(_identity)} 项中 {_id_fail} FAIL / {_id_warn} WARN [坏] —"
                        "情感/分类计数或 Bartik 份额自洽性破裂, 优先排查 (双重计数/份额溢出/陈旧列名)。")
                else:
                    logger.info(
                        f"  · 核心恒等式族: {len(_identity)} 项全无硬错 (FAIL=0, WARN={_id_warn}) [好] —"
                        "情感 frac/计数、Bartik 份额、加权恒等式内部自洽。")

            # (5) 小样本 (T=2) 提醒: 盘面年跨度小则 IV/DID/平衡率检查多为退化, 仅验证管道正确性
            _spans = []
            for _p, _nm in [(panel_40, '40面板'), (panel_51, '51面板')]:
                if _p is not None and 'year' in _p.columns:
                    _yn = int(_p['year'].nunique())
                    _spans.append((_nm, _yn, _p.shape))
            for _nm, _yn, _shape in _spans:
                if _yn <= 2:
                    # 口径对齐 audit_iv_variables (n_years<=1 才是截面 LOO 负相关路径, 见 line 575):
                    # T=1 纯截面退化时 LOO 数学性质致负相关; T=2 时 n_years=2>1, LOO 走常规面板
                    # 分支 (abs(r)<0.05/else), 不进截面负相关路径, 退化主要在时间逻辑近乎无功效。
                    logger.info(
                        f"  · 小样本警告 [{_nm}]: 仅 {_yn} 个年份 ({_shape[0]} 行) — T={_yn} 下"
                        "LOO-IV/DID/事件研究/平衡率检查多退化 (T=1 截面退化时 LOO 数学性质致负相关、"
                        "T=2 时间逻辑近乎无功效、treated-post 无变异), 本次审计仅验证管道正确性; 全量结论以"
                        " 17M/T=18 重生面板实测为准。")

            # (6) 优雅降级: 若 51 面板缺失 → 跨文件一致性 + 51 半套审核全部跳过, 覆盖面打折
            if panel_40 is not None and panel_51 is None:
                logger.warning(
                    "  · 优雅降级: 51_panel_with_controls 缺失 → 已跳过跨文件一致性 (40 vs 51) 与"
                    "51 半套审核, 本次仅覆盖 40 面板; nf_ 控制变量与对照组一致性未受检。")
            elif panel_40 is None:
                logger.warning(
                    "  · 优雅降级: 40_panel_yearly 缺失 → 主面板未加载, 绝大多数检查未执行; "
                    "请先重跑 stage 45/46 产出面板再审计。")
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")
    logger.info("-" * 72)

    # 导出审核结果
    report_dir = os.path.join(OUTPUT_DIR, 'eval_reports')
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, '81_stata_data_audit.csv')
    df_results.to_csv(report_path, index=False, encoding='utf-8-sig')
    logger.info(f"  审核报告已导出: {report_path}")

    # ⏱ 阶段计时 (各主要子阶段墙钟耗时汇总; 纯日志, golden-safe)
    try:
        elapsed = time.time() - start_time
        phase_durations['⑤汇总+写盘 CSV'] = max(elapsed - sum(phase_durations.values()), 0.0)
        logger.info("  ⏱ 阶段计时 (墙钟秒)")
        for _phase, _dur in phase_durations.items():
            _share = _dur / elapsed if elapsed > 0 else 0.0
            logger.info(f"     · {_phase}: {sig4(_dur)}s ({pct4(_share)})")
        logger.info(f"     · 合计总耗时: {sig4(elapsed)}s")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  [阶段计时] 日志诊断异常, 跳过 (不影响产物): {_e}")
    logger.info("81_stata_data_audit 完成 ✓")

    # 返回状态码
    return 1 if n_fail > 0 else 0


if __name__ == '__main__':
    sys.exit(main())
