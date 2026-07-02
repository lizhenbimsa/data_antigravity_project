"""news_process.pipeline.panel.encode_collab — v3.5.0 D2 八格分解 + D4 跨轨残差。

依 v3.5.0 Stage-3 augmentation plan §2.1 / §2.3 (历史方法学文档, 已随 docs/ 目录删除):
    D2 八格编码: cell_id = subst*4 + locus*2 + collab + 1 ∈ {1..8}
        baseline (cell 1) = (0, 0, 0) = 实质性 × 底层技术 × 自主研发
    D4 跨轨残差信号 (9 个文章级 + 18 个面板级 frac/count
        + 3 个 n_articles_{dim}_bothvalid 覆盖披露列, omni 2026-06-11)

锚定文献:
    Angrist & Pischke (2009) Mostly Harmless Econometrics Ch.5 saturated regression (D2)
    Sun & Abraham (2021 JOE 225) cohort decomposition 类比 (D2)
    Loughran & McDonald (2011 JF) tone-vs-context differential 类比借用 (D4)
    Westphal & Zajac (2001 ASQ) decoupling 类比借用 narrative-context layer (D4)

v3.7.0 breaking 备忘: 若未来 collab_mode 升级为 6-class (multi-class A1), CELL_LABEL_MAP
必须重写为 24 项; 向后兼容方案为 panel 同时保留 cell_id_v3_5_full + cell_id_v3_7_full,
旧列再于后续版本 deprecate (截至目前未发生, 仅留为升级预案)。

白话: 把每篇文章按三个二选一属性 (实质/象征 × 底层/应用 × 自研/协同)
落进 2×2×2=8 个格子, 像三位二进制编号, 回归时可以"饱和地"比较任意格子
组合而不必预设哪两维交互。D4 残差则看两个文本口径 (full/ctx) 对同一篇
文章判得是否一致 — 不一致本身就是有信息量的信号。

三轨 (full/ctx/ss) 范围说明 (plan §7.3-A1 决策): D2/D4 collab-cell 分解**有意仅
full/ctx 两轨**, 第三轨 ss (银行+金科同句) 不参与 — cell_id 分类的是
substantiveness/locus/collab 这类 full/ctx 锚定的 LLM 属性, ss 是纯情感轨,
不做属性分解 (故无 cell_id_ss / n_articles_cell_*_ss 列, 见各函数内 intentionally
NOT produced 注释)。clarity / num_intensity 等情感族聚合得 `_ss` 三轨。
⚠ v3.10.0 (apply_v3_5_2): LM 6 子词典 / FLS 等非情感 lexicon 族**亦产 `_ss` 三轨**
(用户决策推翻原 §7.3-A1 "非情感族仅 full/ctx" 冻结设计; 仅 D2/D4 cell_id 分解仍 full/ctx)。
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Optional

import pandas as pd

# 日志富集 (2026-06-24): 四位有效数字渲染单一事实源 (sig4/pct4); 仅服务于日志,
# 不改任何写盘值/schema/控制流 (golden-safe, 纯增量 logging)。
from news_process.core.logging import pct4, sig4

# v3.10.0: LM 子集前缀单一事实源 (取代 apply_v3_5_2 内硬编码 6-tuple, 防漂移)。
# lm_non_sentiment 仅依赖 jieba/json/re/pathlib, 无 panel 导入 → 无循环。
from news_process.pipeline.sentiment.lm_non_sentiment import SUBSET_PREFIXES

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 方法学引文注册表 (经核验, 仅供 emit 进日志; 逐字取自 VERIFIED_REFERENCES.md)。
# encode_collab 是 encode.py 调用的库模块 (无独立 main/run_stage), 共享 panel-build
# 运行期日志; 各 apply_v3_5_* 入口在被调时打印子步骤 banner + 下列方法依据 + 本步判读。
# Sun & Abraham (2021 JOE 225) cohort decomposition 注册表未收录 → 有意不 emit。
# ---------------------------------------------------------------------------
_METHOD_REFS_D2 = (
    "Angrist, J. D., & Pischke, J.-S. (2009). Mostly harmless econometrics: "
    "An empiricist's companion. Princeton University Press. "
    "https://doi.org/10.1515/9781400829828",
)
_METHOD_REFS_D4 = (
    "Loughran, T., & McDonald, B. (2011). When is a liability not a liability? "
    "Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), "
    "35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x",
    "Westphal, J. D., & Zajac, E. J. (2001). Decoupling policy from practice: "
    "The case of stock repurchase programs. Administrative Science Quarterly, "
    "46(2), 202–228. https://doi.org/10.2307/2667086",
)

# collab 维度 (自主研发 vs 外部协同) 文献锚点 — cell_id 第三 bit (c_bit) 编码的正是
# innovation_collab_mode 的自研/协同二分, 这是本模块 (encode_collab) 命名所指的核心维度。
# 仅供 emit 进日志 (golden-safe); 逐字取自项目 Crossref 三道核验注册表, 严禁臆造。
_METHOD_REFS_COLLAB = (
    # method-origin: 自研 vs 外部协同二分的开放式创新理论锚点 (Chesbrough 20 年 meta 升级)
    "Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and "
    "outcomes of open innovation over the past 20 years: A framework and "
    "meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. "
    "https://doi.org/10.1111/jpim.12710",
    # 创新来源归属先例: 专利区分金融创新由谁内部产出 (P5 自研 vs 外部协同)
    "Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in "
    "the twenty-first century: Evidence from US patents. Journal of Political "
    "Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712",
    # 中国语境近期应用: 银行-fintech 合作库直接区分自研 vs 合作
    "Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation "
    "between banks and fintech companies increase bank risk-taking? Evidence "
    "from China. Applied Economics. Advance online publication. "
    "https://doi.org/10.1080/00036846.2025.2536881",
    # 外部协同 (并购) 的金融市场应用: 事件研究度量银行首次 fintech 收购 CAR
    "Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial "
    "institutions' stock price response to fintech acquisitions. Finance "
    "Research Letters, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779",
    # 自研(内部 R&D) vs 外部协同(M&A/技术获取) 的差异化战略锚点 (cell_id 第三 bit 直接)
    "Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, "
    "product market rivalry, and M&A transactions. Strategic Management "
    "Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687",
    # 生态联盟 vs 自主成长: 联盟战略与技术互依的近期管理学证据 (外部协同维度)
    "Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in "
    "ecosystem venturing: The impacts of alliance strategy and technology "
    "interdependence. Journal of Management Studies, 62(2), 565-596. "
    "https://doi.org/10.1111/joms.13063",
)
# collab 维度文献白话 (与上元组逐条对应; 仅供日志, 不参与计算)
_METHOD_REFS_COLLAB_PLAIN = (
    "Chesbrough 开放式创新 20 年 meta 框架, 升级自研 vs 外部协同二分锚点",
    "专利区分金融创新由谁内部产出, 自研 vs 外部协同的来源归属先例",
    "129 家中国银行-fintech 合作库, 直接区分自研 vs 合作, 与中国语境高度契合",
    "事件研究度量银行首次 fintech 收购 CAR, 外部协同 (并购) 的二元金融市场应用",
    "技术差异化 × 并购: 自研内部 R&D 与外部 M&A 技术获取的战略权衡 (collab bit 直接锚)",
    "生态联盟战略与技术互依: 外部协同(联盟) vs 自主成长路径的近期证据",
)

# substantiveness (实质性 vs 象征性, cell_id 第一 bit) + D4 say-do 解耦 (freerider/
# quietworker) 的近期 decoupling 测度文献锚点 — 与 D4 既有 Westphal & Zajac (2001)
# 解耦锚同族, 升级到 2025 系统综述/实证。仅供 emit 进日志 (golden-safe), 逐字取自
# Crossref 核验注册表, 严禁臆造。
_METHOD_REFS_SUBST = (
    "Cepeda, C., Monteiro, A. P., & Aibar-Guzmán, B. (2025). Decoupling in "
    "sustainability reporting: A systematic literature review. Corporate Social "
    "Responsibility and Environmental Management, 32(3), 2988-3007. "
    "https://doi.org/10.1002/csr.3114",
    "Velte, P. (2025). Corporate social responsibility (CSR) decoupling and tax "
    "avoidance: Symbolic use of sustainable boards in the European Union? "
    "Corporate Social Responsibility and Environmental Management, 32(3), "
    "4179-4193. https://doi.org/10.1002/csr.3172",
)

# FLS (前瞻陈述 forward-looking statements) 专属锚点 — apply_v3_5_2 聚合的
# frac_fls_{full,ctx,ss} 是 FLS 词表占比构念 (tone_dicts.json 的 FLS 词表操作化),
# 其源文献是下列 FLS 测度专论, 而非 LM (2011) 情感词典 (banner 此前仅 emit L&M, 与
# 'FLS' 命名错配)。仅供 emit 进日志 (golden-safe), 逐字取自项目 Crossref 三道核验
# 注册表 (LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md), 严禁臆造。
_METHOD_REFS_FLS = (
    # FLS 词表操作化先例: 管理层盈余预测与其他前瞻性陈述的文本测度 (frac_fls 正是其占比)
    "Bozanic, Z., Roulstone, D. T., & Van Buskirk, A. (2018). Management "
    "earnings forecasts and other forward-looking statements. Journal of "
    "Accounting and Economics, 65(1), 1–20. "
    "https://doi.org/10.1016/j.jacceco.2017.11.008",
    # FLS 比例度量奠基: 公司文件中前瞻性陈述比例的朴素贝叶斯机器学习度量 (frac_fls 同型)
    "Li, F. (2010). The information content of forward-looking statements in "
    "corporate filings: A naïve Bayesian machine learning approach. Journal of "
    "Accounting Research, 48(5), 1049–1102. "
    "https://doi.org/10.1111/j.1475-679X.2010.00382.x",
)

# num_intensity (数字密度) 专属锚点 — aggregate_num_intensity_panel 产出的
# mean_num_intensity_{full,ctx,ss} (+ 词级孪生) 度量新闻叙事的数字披露密集度, 其直接
# 源文献是下列"数字披露的叙事语境"专论, 而非 LM (2011) 情感词典。仅供 emit 进日志
# (golden-safe), 逐字取自项目 Crossref 三道核验注册表, 严禁臆造。
_METHOD_REFS_NUMINT = (
    # 数字披露密度的近期应用: 数字披露的叙事语境 (呼应 num_intensity 数字密集度构念)
    "Taraj, I., & Wahlström, R. R. (2026). Narratives contextualizing numeric "
    "disclosures: Insights from earnings calls. Journal of Business Finance & "
    "Accounting, 53(3), 1263–1286. https://doi.org/10.1111/jbfa.70056",
)

# v3.5.0 D2: 8-cell encoding (baseline=cell 1 三维全 0)
VALID_SUBST = {'实质性', '象征性'}
VALID_LOCUS = {'底层技术', '应用场景'}
VALID_COLLAB = {'自主研发', '外部协同'}

CELL_LABEL_MAP = {
    1: '实质性·底层技术·自主研发',
    2: '实质性·底层技术·外部协同',
    3: '实质性·应用场景·自主研发',
    4: '实质性·应用场景·外部协同',
    5: '象征性·底层技术·自主研发',
    6: '象征性·底层技术·外部协同',
    7: '象征性·应用场景·自主研发',
    8: '象征性·应用场景·外部协同',
}

# v3.5.0 D4: 9 个文章级残差信号 (3 维度 × 3 信号)
DIMS_D4 = [
    ('subst',  'innovation_substantiveness', '实质性',   '象征性'),
    ('locus',  'innovation_locus',           '底层技术', '应用场景'),
    ('collab', 'innovation_collab_mode',     '自主研发', '外部协同'),
]


def _normalize_label(series: pd.Series) -> pd.Series:
    """LLM 标签预归一化: 去首尾空白 + 全角空格 + 所有内部 \\s。

    Per plan §2.1.1 F32: 防御 stage 21 LLM 输出携带的尾随空格 / U+3000 /
    换行噪声。NaN 经 .str accessor 链保持 NaN。
    """
    # fix(omni-g-encode-collab-02, 2026-06-11): pandas 3.0 读 parquet/构造字符串列默认
    # 返回新 `str` dtype, `series.dtype == object` 恒 False → F32 脏标签清洗在生产路径
    # 静默 no-op。gate 放宽为 object 或 string dtype (legacy object / pandas3 str /
    # StringDtype 三者 .str accessor 均可用); 非字符串 dtype (如全 NaN float64) 仍原样返回。
    if series.dtype == object or pd.api.types.is_string_dtype(series):
        return (series.str.strip()
                      .str.replace('　', '', regex=False)
                      .str.replace(r'\s+', '', regex=True))
    return series


def _is_nan(v) -> bool:
    """None 或 float NaN 判定 (sidecar / median 锚点通用小工具)."""
    return v is None or (isinstance(v, float) and v != v)


def _both_valid_mask(full_norm: pd.Series, ctx_norm: pd.Series,
                     baseline: str, contrast: str) -> pd.Series:
    """D4 dim-level both_valid: full 与 ctx 两路归一化标签均为 canonical (baseline/contrast).

    cell_id 仅 full/ctx (ss 不分解 — ss 是纯情感轨, 不产属性标签)。

    fix(omni-g-encode-collab-02, 2026-06-11): 用 isin 白名单 (与 compute_cell_id 校验
    口径对齐) 取代 notna() — 非 canonical 但非 NaN 的脏标签不再计入 both_valid, 否则
    它只推高 disagree 而打破 invariant (ii) freerider+quietworker == disagree。
    derive_residual_signals 与 aggregate_d4_panel 共用本函数 ⇒ frac 分子/分母同域。
    """
    valid = (baseline, contrast)
    return full_norm.isin(valid) & ctx_norm.isin(valid)


def compute_cell_id(df: pd.DataFrame, track: str) -> pd.Series:
    """计算指定轨道 ('full' 或 'ctx') 的文章级 cell_id ∈ {1..8}。

    # cell_id_ss intentionally NOT produced: track 仅取 full/ctx — D2/D4 cells 分类的是
    # full/ctx-anchored 属性 (substantiveness/locus/collab), ss 是纯情感轨不分解
    # (plan §7.3-A1)。故本函数永不以 track='ss' 调用。

    返回 Int8 nullable Series:
        - 三个维度标签均合法 (归一化后落在 VALID_* 集合) 时取有效值 1..8
        - 任一维度为 NaN / 脏标签 / 列缺失时为 pd.NA

    Per plan §2.1.1 (F27/F28/F32/B-NEW-2/m3):
        - 缺列守卫返回全 NA Int8 (不抛 KeyError)
        - 脏标签防御走 _normalize_label + isin
        - .where(valid, pd.NA).astype('Int8') 兼容各版本 pandas/numpy

    白话: 把每篇文章在三个二元维度上的标签 (实质/象征 × 底层/应用 ×
    自研/协同) 编成 1~8 号"格子", 类似三位二进制数 +1, 方便后面按格子
    数文章做饱和回归。
    """
    s_col = f'innovation_substantiveness_{track}'
    l_col = f'innovation_locus_{track}'
    c_col = f'innovation_collab_mode_{track}'

    missing = [c for c in (s_col, l_col, c_col) if c not in df.columns]
    if missing:
        logger.warning(
            f"v3.5.0 D2 cell_id_{track}: missing columns {missing}, returning all-NA Int8"
        )
        return pd.Series([pd.NA] * len(df), dtype='Int8', index=df.index)

    s_norm = _normalize_label(df[s_col])
    l_norm = _normalize_label(df[l_col])
    c_norm = _normalize_label(df[c_col])

    valid = (s_norm.isin(VALID_SUBST) &
             l_norm.isin(VALID_LOCUS) &
             c_norm.isin(VALID_COLLAB))

    s_bit = (s_norm == '象征性').astype('int8')
    l_bit = (l_norm == '应用场景').astype('int8')
    c_bit = (c_norm == '外部协同').astype('int8')

    cell = (s_bit * 4 + l_bit * 2 + c_bit + 1).where(valid, pd.NA).astype('Int8')
    return cell


def derive_residual_signals(df: pd.DataFrame) -> list[str]:
    """原地 (in-place) 添加 9 个文章级 D4 残差指示列。

    **WARNING (CR-2)**: 本函数**原地修改** ``df``。若 ``{dim}_disagree`` /
    ``{dim}_freerider`` / ``{dim}_quietworker`` 列已存在 (如开发流程中重复
    调用), 将被**静默覆盖**。

    Per plan §2.3.2 (F C-NEW-4 invariants i/ii/iii):
        对每个 dim ∈ {subst, locus, collab}:
            {dim}_disagree    = (full != ctx) ∧ both_valid           [boolean]
            {dim}_freerider   = (full == baseline) ∧ (ctx == contrast) [boolean]
            {dim}_quietworker = (full == contrast) ∧ (ctx == baseline) [boolean]

    Invariants (provable by construction):
        (i)  freerider + quietworker ≤ 1 (mutually exclusive)
        (ii) freerider + quietworker == disagree (definitionally; 由 both_valid 的
             isin 白名单口径保证 — 非 canonical 标签不进 both_valid)
        (iii) NaN 传播: 任一轨为 NaN **或非 canonical 脏标签** ⇒
             三列全为 False (而非 NaN)

    Returns: 新增列名 list (供下游 panel 聚合登记)。

    白话: 对每个维度比较两个文本口径的标签 — "disagree"=full 与 ctx 两路说法不一;
    "freerider"=全文看着像基线类、贴近实体的上下文却是对照类 (说一套
    做一套的疑似信号); "quietworker"=反过来 (做了不说)。这些差异本身
    就是研究变量。

    # ss 残差 intentionally NOT produced: D4 比较的是 full vs ctx 两个属性口径的
    # 标签一致性 (substantiveness/locus/collab), ss 是纯情感轨不产属性标签, 故无
    # {dim}_*_ss 残差列 (plan §7.3-A1, 本族有意仅 full/ctx 两轨)。
    """
    added_cols: list[str] = []
    for short, base, baseline, contrast in DIMS_D4:
        full_col = f'{base}_full'
        ctx_col = f'{base}_ctx'
        if full_col not in df.columns or ctx_col not in df.columns:
            logger.warning(
                f"v3.5.0 D4: missing track column(s) for {base}, "
                f"skipping {short}_(disagree|freerider|quietworker)"
            )
            continue

        full_norm = _normalize_label(df[full_col])
        ctx_norm = _normalize_label(df[ctx_col])
        # fix(omni-g-encode-collab-02, 2026-06-11): notna() → isin 白名单 (修 invariant ii)
        both_valid = _both_valid_mask(full_norm, ctx_norm, baseline, contrast)

        df[f'{short}_disagree'] = ((full_norm != ctx_norm) & both_valid)
        df[f'{short}_freerider'] = ((full_norm == baseline) & (ctx_norm == contrast))
        df[f'{short}_quietworker'] = ((full_norm == contrast) & (ctx_norm == baseline))
        added_cols.extend([
            f'{short}_disagree', f'{short}_freerider', f'{short}_quietworker'
        ])
    return added_cols


def aggregate_d2_panel(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """把 D2 8 格计数聚合到 bank-year 面板。

    Per plan §2.1.2 + F-CR-cell-NA (R6 fix):
        - 8 个格子计数列: n_articles_cell_{1..8}_full
        - 1 个 NA 桶列: n_articles_cell_NA_full
          (articles 在 cell_id_full = NA, 通常 LLM 对 substantiveness/locus/
           collab_mode 三维之一失败)
        - 主恒等式: ``n_articles >= Σ n_articles_cell_{1..8}_full``
          (逻辑必然性, n_articles 包含 cell_NA bucket; main_fail 仅在 n_articles
          < sum 时 > 0, 那才是真不一致 bug 而非 LLM 部分失败)
        - 更严完整性: ``n_articles == Σ cells_1..8 + n_articles_cell_NA_full``
          (na_bucket_fail > 0 → 上游 race condition)
        - 交叉恒等式 (对 v3.4.0 _indep/_collab):
            n_articles_indep  >= n_articles_cell_{1,3,5,7}_full
            n_articles_collab >= n_articles_cell_{2,4,6,8}_full

    返回含恒等式校验失败计数的 dict (per plan §2.1.2 F27/C-NEW-2
    + R6 F-CR-cell-NA: na_bucket_fail / n_articles_cell_NA_total / na_bucket_pct)。

    # n_articles_cell_*_ss intentionally NOT produced: 8 格分解只读 cell_id_full
    # (full/ctx-anchored 属性), ss 是纯情感轨不分解 (plan §7.3-A1, 有意仅 full 锚)。
    """
    # CR-3 / CR-4 (CRITICAL fix): 与 production encode.py 对齐 — panel 是 flat
    # DataFrame, target_bank + year 是**列**而非 MultiIndex (参 encode.py:666
    # `panel = df.groupby(['target_bank', 'year']).agg(...).reset_index()`).
    # df 也用 'target_bank' (encode.py:221 注释). 之前用 ['bank', 'year'] 是错误,
    # 单元测试 fixture 与 production 不一致 — 通过 real-data smoke test (CR-20) 发现.
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns:
            raise KeyError(
                f"aggregate_d2_panel 要求 panel 含 '{required_col}' 列 "
                f"(production encode.py:666 约定 flat panel with target_bank/year columns); "
                f"got panel.columns starts with {list(panel.columns[:5])}"
            )
        if required_col not in df.columns:
            raise KeyError(
                f"aggregate_d2_panel 要求 df 含 '{required_col}' 列; "
                f"got df.columns starts with {list(df.columns[:5])}"
            )

    if 'cell_id_full' not in df.columns:
        logger.info("  v3.5.0 D2: cell_id_full not in df, skipping panel aggregation")
        # F-52: skip 路径返回 None 而非 0, 避免 "0 = validation passed" 误读
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'cell_id_col_absent'}

    # 边界 F27 (修正): graceful skip 而非 raise — 测试 fixtures / 缺 LLM 列 / 极小 panel 安全
    # 仅当 cell_id_full 全 NA (LLM 输入列缺失或全 dirty label) 时跳过整 D2 panel 派生.
    if df['cell_id_full'].isna().all():
        # F-51 + F-50: 升级为 warning level, 提示 upstream stage 21 数据缺失第三维度
        # 这通常意味 stage 21 未在 v3.4.0+ 重跑 (innovation_collab_mode_* 列缺失).
        # 调用方应检查 cell_aggregation_skipped + skip_reason 而非依赖 main_fail.
        logger.warning(
            "  ⚠ v3.5.0 D2: cell_id_full 全 NA (LLM 输入列缺失或 dirty 全失败); "
            "通常源于 stage 21 未 post-v3.4.0 重跑产出 innovation_collab_mode_* 列. "
            "v3.5.0 D2 主 deliverable (8-cell decomposition) 在此条件下**不可用**. "
            "解决方案: 重跑 stage 21 with prompt v8 (含 collab_mode 维度)."
        )
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'all_na_cell_id'}

    if panel.shape[0] == 0:
        logger.warning("  v3.5.0 D2: panel 空 (0 rows), 跳过 panel 8-cell 聚合")
        return {'main_fail': None, 'indep_cross_fail': None, 'collab_cross_fail': None,
                'cell_aggregation_skipped': True,
                'skip_reason': 'empty_panel'}

    if df.shape[0] < 1000:
        panel.attrs['D2_small_sample_warning'] = True
        logger.info(
            f"  v3.5.0 D2: small sample (df={df.shape[0]} articles < 1000); "
            "panel.attrs['D2_small_sample_warning'] = True; 继续聚合 (production threshold ≥ 100k)"
        )

    # 经 MultiIndex 把 groupby 结果对齐到 panel 行序 (panel 本身保持 flat)
    panel_idx = pd.MultiIndex.from_frame(panel[['target_bank', 'year']])

    # F-CR-cell-NA (R6 fix): cell 聚合需与 panel.n_articles 同源 subset 计数。
    # encode.py:672 `n_articles_llm_valid = ('llm_vote_score_full','count')` 只数 LLM
    # 总分非 NaN 的 articles (= 本 cell 子集口径); 注意 encode.py:671 `n_articles` 本身
    # 用 'size' (含 NA, 物理篇数), 故 cell 聚合须对齐 n_articles_llm_valid 而非 n_articles.
    # 直接 `df['cell_id_full'] == cell_id` 会把 LLM 总分失败但
    # cell_id 三维都合法的 articles 也计入 cells → Σ cells > n_articles → 假阳性
    # main_fail (实测 13/87 bank-years). 解决: cell aggregation 限定在与 n_articles
    # 同源 subset 上. 优先用 llm_vote_score_full (encode.py 计算后状态); 退化时复刻
    # encode.py:113-137 完整 invalid_mask 公式 (verified=False ∨ call_failure ∨
    # undefined ∨ sentiment_full 缺失 → invalid).
    if 'llm_vote_score_full' in df.columns:
        df_scored = df[df['llm_vote_score_full'].notna()].copy()
    elif 'llm_sentiment_full' in df.columns:
        invalid = pd.Series(False, index=df.index)
        if 'llm_call_failure_full' in df.columns:
            invalid = invalid | df['llm_call_failure_full'].fillna(0).astype(bool)
        if 'llm_undefined_full' in df.columns:
            invalid = invalid | df['llm_undefined_full'].fillna(0).astype(bool)
        if 'llm_verified_full' in df.columns:
            invalid = invalid | (~df['llm_verified_full'].fillna(False).astype(bool))
        invalid = invalid | df['llm_sentiment_full'].isna()
        df_scored = df[~invalid].copy()
    else:
        # 退化: 上游列全缺失时退回全 df (保留旧语义)
        df_scored = df

    for cell_id in range(1, 9):
        df_cell = df_scored[df_scored['cell_id_full'] == cell_id]
        col = f'n_articles_cell_{cell_id}_full'
        counts = (df_cell.groupby(['target_bank', 'year']).size()
                         .reindex(panel_idx, fill_value=0).astype('Int32'))
        panel[col] = counts.values

    # F-CR-cell-NA: 显式追踪 cell_id_full = NA 的 (LLM-scored) article 数 per (bank, year).
    # 该 bucket = LLM 总分成功 (在 n_articles 中) 但 substantiveness/locus/collab_mode
    # 任一维度失败的 articles. identity: n_articles = Σ cells_1..8 + n_articles_cell_NA_full.
    df_cell_na = df_scored[df_scored['cell_id_full'].isna()]
    na_counts = (df_cell_na.groupby(['target_bank', 'year']).size()
                           .reindex(panel_idx, fill_value=0).astype('Int32'))
    panel['n_articles_cell_NA_full'] = na_counts.values

    # F-CR-cell-NA: identity 改为 "逻辑必然性" 检查 `n_articles >= Σ cells 1..8`,
    # main_fail = 数 of rows where `n_articles < Σ cells` (才是真不一致 bug). 同时新增
    # 严格完整性公式 `n_articles == Σ cells + n_articles_cell_NA_full` 作为 stronger
    # check (na_bucket_fail), 任何时候都应 = 0 — 若不为 0 则上游 LLM 输出有 race condition.
    main_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in range(1, 9))
    # metric-audit 2026-06-02 (encode-02 重构对齐): cells + NA 桶建在 LLM-valid 子集
    # (count 口径), 故恒等式 LHS 须同口径; 重构后 n_articles=物理 size → 用
    # n_articles_llm_valid (旧 panel 缺列回退 n_articles, 其即 count). 否则含 LLM 失败行
    # 的 bank-year 令 size != Σcells+NA → 误报"上游 race condition".
    _nac = 'n_articles_llm_valid' if 'n_articles_llm_valid' in panel.columns else 'n_articles'
    has_news = panel[_nac] > 0
    main_fail = int((panel.loc[has_news, _nac]
                     < main_sum.loc[has_news]).sum())
    na_bucket_fail = int((panel.loc[has_news, _nac]
                          != main_sum.loc[has_news]
                          + panel.loc[has_news, 'n_articles_cell_NA_full']).sum())

    # Cross identities (only if v3.4.0 二元后缀列存在); 改用 ">=" 同 main_fail 一致
    indep_cross_fail = 0
    collab_cross_fail = 0
    if 'n_articles_indep' in panel.columns:
        indep_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in [1, 3, 5, 7])
        has_indep = panel['n_articles_indep'] > 0
        indep_cross_fail = int((panel.loc[has_indep, 'n_articles_indep']
                                < indep_sum.loc[has_indep]).sum())
    if 'n_articles_collab' in panel.columns:
        collab_sum = sum(panel[f'n_articles_cell_{i}_full'] for i in [2, 4, 6, 8])
        has_collab = panel['n_articles_collab'] > 0
        collab_cross_fail = int((panel.loc[has_collab, 'n_articles_collab']
                                 < collab_sum.loc[has_collab]).sum())

    # F-CR-cell-NA: 即便 main_fail / cross_fail 都 = 0, 仍报告 NA bucket 占比 (诊断信息)
    na_total = int(panel['n_articles_cell_NA_full'].sum())
    n_articles_total = int(panel.loc[has_news, _nac].sum())
    na_pct = (na_total / n_articles_total * 100) if n_articles_total > 0 else 0.0

    if main_fail > 0 or indep_cross_fail > 0 or collab_cross_fail > 0:
        logger.warning(
            f"  ✗ cell_id identity 失败 (n_articles < Σ cells 不可能成立): "
            f"main={main_fail}, indep_cross={indep_cross_fail}, "
            f"collab_cross={collab_cross_fail}"
        )
    elif na_bucket_fail > 0:
        logger.warning(
            f"  ⚠ cell_id NA bucket identity 失败 (上游数据 race condition?): "
            f"na_bucket_fail={na_bucket_fail}"
        )
    else:
        # 把 LLM partial failure 的诊断信息从 WARNING 降为 INFO (设计性预期)
        logger.info(
            f"  ✓ cell_id identity 通过 (n_articles_cell_NA_full bucket = "
            f"{na_total:,d}/{n_articles_total:,d} = {pct4(na_pct, fraction=False)} "
            f"LLM 部分失败 articles)"
        )
        # 结果判读 (D2 8 格覆盖率): NA 桶占比衡量 collab_mode 三维标注的完整度。
        # 阈值 (经验): <5% 好 (LLM 三维标注稳健) / 5–15% 临界 / >15% 偏弱
        # (substantiveness/locus/collab_mode 任一维度失败率偏高, 8 格分解功效下降)。
        try:
            if na_pct < 5.0:
                _verdict = "好 (LLM 三维标注完整, 8 格分解可用)"
            elif na_pct <= 15.0:
                _verdict = "临界 (部分维度标注缺失, 留意 cell 计数稀释)"
            else:
                _verdict = "偏弱 (collab_mode 维度标注失败偏高, 建议复查 stage 21 prompt v8)"
            logger.info(
                f"  📊 D2 cell-NA 覆盖判读: na_pct={pct4(na_pct, fraction=False)} → {_verdict}"
            )
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"  ⚠ D2 cell-NA 判读日志失败 (graceful): {_e}")

    return {
        'main_fail': main_fail,
        'indep_cross_fail': indep_cross_fail,
        'collab_cross_fail': collab_cross_fail,
        'cell_aggregation_skipped': False,
        'na_bucket_fail': na_bucket_fail,
        'n_articles_cell_NA_total': na_total,
        'na_bucket_pct': na_pct,
    }


def aggregate_d4_panel(df: pd.DataFrame, panel: pd.DataFrame,
                       ctx_baseline_path: Optional[str] = None) -> dict:
    """把 D4 残差信号聚合到 bank-year 面板。

    Per plan §2.3.3 + §2.3.4 (分母语义修订, omni 2026-06-11):
        18 个 panel 列: {dim}_{signal}_frac + n_articles_{dim}_{signal}
            (3 维度 × 3 信号 × 2 度量)
        + 3 个覆盖列: n_articles_{dim}_bothvalid (论文披露 both_valid 覆盖率)
        *_frac = Σ signal / n_bothvalid — 分母为该维 both_valid (full/ctx 两路 canonical 标签)
            文章数, 与分子同域; n_bothvalid == 0 → NaN (非假零)。
        小样本限制: n_bothvalid < 5 → *_frac 强制 NaN
            (valid 域门; 上游标签列缺失时回退 legacy 物理分母 + n_articles < 5 门)
        ctx 覆盖率自适应告警 + d4_data_quality_flag 字符串列 (F6 + C-NEW-3)

    ctx_baseline_path: v3_4_0_ctx_coverage_baseline.json 路径 (per §9.10)。
                       None 或缺失时回退固定 0.5 阈值并注明 caveat。

    CR-6 note: 覆盖率检查用 `innovation_collab_mode_ctx` 作 canonical 代理
    (假定其为 3 个 ctx 维度中覆盖最低者 — Hassan-2019 实体上下文抽取在
    v3.4.0 最新加入的维度上波动最大)。若要求对称处理, 未来版本可对
    3 个 ctx 维度取平均。

    CR-4 (CRITICAL fix): 与 aggregate_d2_panel 同样要求 panel 含 target_bank + year **列**
    (production flat panel, 非 MultiIndex; 参 encode.py:666 约定).

    白话: 分母只数"两个口径都给出合法标签"的文章 — 因为分子 (分歧/言行
    不一信号) 只可能在这类文章上为真。如果拿全部物理文章数当分母, 没
    标签的文章会被当成"无分歧", 把分歧率系统性压低; 样本不足 5 篇时
    占比噪声太大, 直接记缺失。

    # ss frac/count intentionally NOT produced: D4 残差只比 full vs ctx 两个属性口径
    # (DIMS_D4 维度全是 full/ctx-anchored), ss 是纯情感轨不产属性标签 (plan §7.3-A1,
    # cell_id 仅 full/ctx, ss 不分解 — 本族有意只走 full/ctx 两路)。  # no-ss-track
    """
    # CR-4: column invariant (与 aggregate_d2_panel 对称 — flat panel with target_bank/year cols)
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns:
            raise KeyError(
                f"aggregate_d4_panel 要求 panel 含 '{required_col}' 列; "
                f"got panel.columns starts with {list(panel.columns[:5])}"
            )
        if required_col not in df.columns:
            raise KeyError(
                f"aggregate_d4_panel 要求 df 含 '{required_col}' 列"
            )

    panel_idx = pd.MultiIndex.from_frame(panel[['target_bank', 'year']])

    residual_frac_cols: list[str] = []
    has_residual = False
    # fix(omni-g-encode-collab-01, 2026-06-11): *_frac 分母改 both_valid 计数 (与分子同域)。
    # derive_residual_signals invariant (iii) 把任一轨缺失/脏标签的文章编为 False (非 NaN),
    # 旧实现 groupby.mean() 的分母=物理文章数 → 缺标签文章被静默计为"不分歧" (系统性下偏),
    # both_valid=0 的组输出假零 0.0。现: frac = Σ signal / n_bothvalid, n_bothvalid < 5
    # (含 ==0) → NaN (small-sample 门同步迁移到 valid 域); 另导出 n_articles_{dim}_bothvalid
    # 供论文披露覆盖率。上游标签列缺失 (无法重建 both_valid) 时回退 legacy 物理分母。
    fallback_frac_cols: list[str] = []
    for short, base, baseline, contrast in DIMS_D4:
        signal_cols = [f'{short}_{s}' for s in ('disagree', 'freerider', 'quietworker')
                       if f'{short}_{s}' in df.columns]
        if not signal_cols:
            continue
        has_residual = True

        full_col = f'{base}_full'
        ctx_col = f'{base}_ctx'
        bv_count = None
        if full_col in df.columns and ctx_col in df.columns:
            # 与 derive_residual_signals 共用 _both_valid_mask ⇒ 分母与分子可达域一致
            bv = _both_valid_mask(_normalize_label(df[full_col]),
                                  _normalize_label(df[ctx_col]),
                                  baseline, contrast)
            bv_count = (bv.groupby([df['target_bank'], df['year']]).sum()
                          .reindex(panel_idx, fill_value=0).astype('Int32'))
            panel[f'n_articles_{short}_bothvalid'] = bv_count.values
        else:
            logger.warning(
                f"  v3.5.0 D4: {base} full/ctx 源列缺失, {short}_*_frac 回退 legacy 物理分母 "
                "(both_valid 不可重建)"  # no-ss-track: cell_id 仅 full/ctx, ss 不分解
            )

        for col in signal_cols:
            frac_col = f'{col}_frac'
            count_col = f'n_articles_{col}'
            # 用 target_bank (生产约定) + reindex 到 panel_idx 做行对齐
            count_series = (df.groupby(['target_bank', 'year'])[col]
                              .sum().reindex(panel_idx, fill_value=0).astype('Int32'))
            panel[count_col] = count_series.values
            if bv_count is not None:
                denom = bv_count.astype('float64')
                # n_bothvalid < 5 (含 ==0 假零) → NaN
                frac_series = (count_series.astype('float64') / denom).where(denom >= 5)
                panel[frac_col] = frac_series.values
            else:
                mean_series = (df.groupby(['target_bank', 'year'])[col]
                                 .mean().reindex(panel_idx))
                panel[frac_col] = mean_series.values
                fallback_frac_cols.append(frac_col)
            residual_frac_cols.append(frac_col)

    if not has_residual:
        logger.info("  v3.5.0 D4: residual signal columns absent, skipping panel aggregation")
        return {'residual_skipped': True}

    # Small-sample restriction (修 m5 + C-NEW-3): 仅 legacy 回退列沿用物理 n_articles 门
    # (both_valid 路径已在上方用 valid 域门 n_bothvalid < 5)
    if fallback_frac_cols:
        small_mask = panel['n_articles'] < 5
        for col in fallback_frac_cols:
            panel.loc[small_mask, col] = pd.NA

    # ctx coverage 自适应警告 (修 C-NEW-3 + F6)
    quality_flag = 'ok'
    ctx_check_col = 'innovation_collab_mode_ctx'
    if ctx_check_col in df.columns:
        current_coverage = float(df[ctx_check_col].notna().mean())
        threshold_low = 0.5  # fallback
        baseline_loaded = False
        if ctx_baseline_path and os.path.exists(ctx_baseline_path):
            try:
                with open(ctx_baseline_path) as f:
                    baseline = json.load(f)
                threshold_low = float(baseline['mean']) - 2.0 * float(baseline['std'])
                baseline_loaded = True
            except (KeyError, ValueError, OSError) as e:
                logger.warning(
                    f"  v3.5.0 D4: failed to load ctx baseline {ctx_baseline_path}: {e}; "
                    "fallback threshold = 0.5"
                )
        if current_coverage < threshold_low:
            quality_flag = 'insufficient'
            logger.warning(
                f"  ⚠ ctx coverage {pct4(current_coverage)} < "
                f"{'baseline-2σ' if baseline_loaded else 'fallback'} threshold "
                f"{pct4(threshold_low)}; panel.attrs['D4_data_quality'] marked"
            )
            panel.attrs['D4_data_quality'] = 'insufficient_ctx_coverage'
        else:
            # 结果判读 (D4 ctx 覆盖率): 高于阈值即认为实体上下文抽取覆盖充足,
            # both_valid 分母可靠 → frac 信号无系统性下偏风险。
            logger.info(
                f"  📊 D4 ctx 覆盖判读: coverage={pct4(current_coverage)} ≥ "
                f"{'baseline-2σ' if baseline_loaded else 'fallback'} "
                f"{pct4(threshold_low)} → 好 (both_valid 分母可靠, frac 信号无下偏)"
            )

    # F6: str column 持久化到 parquet/.dta, Stata 用户可见
    panel['d4_data_quality_flag'] = quality_flag

    return {
        'residual_skipped': False,
        'd4_data_quality_flag': quality_flag,
        'residual_frac_cols': residual_frac_cols,
    }


def apply_v3_5_0(df: pd.DataFrame, panel: pd.DataFrame,
                 ctx_baseline_path: Optional[str] = None) -> dict:
    """一次性入口: 对 df + panel 应用全部 v3.5.0 D2 + D4 派生。

    由 encode.py::aggregate_panel 在 v3.4.0 collab_mode 聚合块之后调用。
    返回汇总诊断 dict, 供 audit log §A。
    """
    # ---- 子步骤 banner (helper module, 复用 panel-build 运行期日志; 不重打 ENV/CONFIG) ----
    # 该块为纯日志增量 (golden-safe): 仅 logger.info + 局部 _t* 计时变量, 不改任何写盘值。
    _t0 = time.time()
    try:
        logger.info("=" * 72)
        logger.info(
            "  步骤 D2+D4 (encode_collab.apply_v3_5_0): collab-cell 八格分解 + 跨轨残差信号"
        )
        logger.info(
            f"    · 输入: article df={df.shape[0]:,d} 行 × {df.shape[1]:,d} 列, "
            f"panel={panel.shape[0]:,d} 行 (bank-year)"
        )
        logger.info(
            "    · 方法 D2 (8-cell 饱和编码 cell_id = subst*4 + locus*2 + collab + 1):"
        )
        for _ref in _METHOD_REFS_D2:
            logger.info(f"        - {_ref}")
        logger.info(
            "    · 方法 D4 (full vs ctx 标签一致性残差 = disagree/freerider/quietworker):"
        )
        for _ref in _METHOD_REFS_D4:
            logger.info(f"        - {_ref}")
        # 📖 substantiveness 二分 (cell_id 第一 bit: 实质性 vs 象征性) + D4 say-do
        # 解耦 (freerider/quietworker = 说一套做一套) 的近期 decoupling 测度依据。
        logger.info(
            "    · 📖 substantiveness 二分 + D4 say-do 解耦 (decoupling) 近期测度依据:"
        )
        for _ref in _METHOD_REFS_SUBST:
            logger.info(f"        - {_ref}")
        # 📖 方法论依据 (collab 维度专属): cell_id 第三 bit 编码的 innovation_collab_mode
        # (自主研发 vs 外部协同) 是本模块命名所指的核心维度, 下列文献锚定其二分构念与度量。
        logger.info(
            "    · 📖 方法论依据 (collab 维度 = cell_id 第三 bit: 自主研发 vs 外部协同):"
        )
        for _ref, _plain in zip(_METHOD_REFS_COLLAB, _METHOD_REFS_COLLAB_PLAIN):
            logger.info(f"        - {_ref}")
            logger.info(f"          (白话: {_plain})")
        logger.info(
            "    · 白话: 把每篇文章按三个二选一属性落进 2×2×2=8 格做饱和回归; "
            "D4 看 full/ctx 两口径判得是否一致 (不一致本身即信号)。"
        )
        logger.info(
            "    · 轨道范围 (plan §7.3-A1): D2/D4 cell 分解有意仅 full/ctx 两轨, "
            "ss 是纯情感轨不分解属性 (无 cell_id_ss)。确定性纯 CPU/$0。"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_0 banner 日志失败 (graceful): {_e}")

    # 文章级 D2
    # cell_id_ss intentionally NOT produced: D2/D4 collab cells classify full/ctx-anchored
    # attributes (substantiveness/locus/collab_mode); ss 是纯情感轨, 不分解属性
    # (plan §7.3-A1 决策, cell_id 仅 full/ctx, ss 不分解)。  # no-ss-track
    df['cell_id_full'] = compute_cell_id(df, 'full')
    df['cell_id_ctx'] = compute_cell_id(df, 'ctx')

    # 文章级 D4
    residual_cols = derive_residual_signals(df)
    _t_article = time.time()

    # 面板级 D2 8 格计数 + 恒等式
    d2_diag = aggregate_d2_panel(df, panel)

    # 面板级 D4 frac/count + d4_data_quality_flag
    d4_diag = aggregate_d4_panel(df, panel, ctx_baseline_path)
    _t_panel = time.time()

    # ---- 阶段计时 + 结果汇总 (纯日志) ----
    try:
        logger.info(
            f"  ⏱ apply_v3_5_0 计时: article 级 (cell_id+residual) "
            f"{sig4(_t_article - _t0)}s · panel 级 (D2+D4 聚合) "
            f"{sig4(_t_panel - _t_article)}s · 合计 {sig4(_t_panel - _t0)}s"
        )
        logger.info(
            f"  ✓ apply_v3_5_0 完成: cell_id 2 轨 + residual {len(residual_cols):,d} 文章级列; "
            f"D2 skipped={d2_diag.get('cell_aggregation_skipped')} · "
            f"D4 quality_flag={d4_diag.get('d4_data_quality_flag', 'n/a')}"
        )
        # 📈 结果统计 (collab 维度 = cell_id 第三 bit): 报 cell_id_full 有效率 +
        # 8 格分布 + 外部协同占比 (cells 2/4/6/8 = c_bit=1)。纯日志, 不改任何写盘值。
        _cid = df['cell_id_full']
        _n_total = len(_cid)
        _n_valid = int(_cid.notna().sum())
        _valid_pct = (_n_valid / _n_total) if _n_total else 0.0
        logger.info(
            f"  📈 cell_id_full 覆盖: 有效 {_n_valid:,d}/{_n_total:,d} = "
            f"{pct4(_valid_pct)} (NA = LLM 三维之一标注失败)"
        )
        if _n_valid > 0:
            _collab_cells = {2, 4, 6, 8}  # c_bit=1 → 外部协同
            _n_collab = int(_cid.isin(_collab_cells).sum())
            _collab_share = _n_collab / _n_valid
            logger.info(
                f"  📈 collab 维度占比 (有效文章中): 外部协同 {_n_collab:,d} = "
                f"{pct4(_collab_share)} · 自主研发 {_n_valid - _n_collab:,d} = "
                f"{pct4(1.0 - _collab_share)}"
            )
            # 8 格分布逐格计数 (cell_label → n), 供饱和回归前的格内样本量诊断
            _cnts = _cid.value_counts().to_dict()
            _cell_brief = " · ".join(
                f"{_i}:{int(_cnts.get(_i, 0)):,d}({pct4(int(_cnts.get(_i, 0)) / _n_valid)})"
                for _i in range(1, 9)
            )
            logger.info(f"  📈 D2 8 格分布 (cell_id:n(占比)): {_cell_brief}")
        # 📈 D4 say-do 解耦率 (per-dimension): 文章级 disagree/freerider/quietworker
        # 在 both_valid 子集 (full/ctx 两路 canonical 标签) 中的占比 — 这才是 D4 的实质
        # 发现 (full vs ctx 说做不一的横截面普遍程度), 此前 summary 只报残差列数 (len),
        # 把它藏在列计数后。仅日志, both_valid/标签归一化均复用模块函数得 discarded local,
        # 不改任何写盘值/schema/控制流。
        for _short, _base, _bl, _ct in DIMS_D4:
            _dcol = f'{_short}_disagree'
            _fcol = f'{_short}_freerider'
            _qcol = f'{_short}_quietworker'
            _fc, _cc = f'{_base}_full', f'{_base}_ctx'
            if not all(_c in df.columns for _c in (_dcol, _fcol, _qcol, _fc, _cc)):
                continue
            _bv = _both_valid_mask(_normalize_label(df[_fc]),
                                   _normalize_label(df[_cc]), _bl, _ct)
            _n_bv = int(_bv.sum())
            if _n_bv == 0:
                continue
            _n_dis = int(df[_dcol].sum())
            _n_free = int(df[_fcol].sum())
            _n_quiet = int(df[_qcol].sum())
            logger.info(
                f"  📈 D4 解耦率 ({_short}, both_valid={_n_bv:,d}): "
                f"disagree {pct4(_n_dis / _n_bv)} · "
                f"freerider {pct4(_n_free / _n_bv)} · "
                f"quietworker {pct4(_n_quiet / _n_bv)}"
            )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_0 计时/汇总日志失败 (graceful): {_e}")

    return {
        'v3_5_0_cell_id_added': ['cell_id_full', 'cell_id_ctx'],
        'v3_5_0_residual_articles_added': residual_cols,
        'd2_identity': d2_diag,
        'd4_quality': d4_diag,
    }


# ============================================================================
# v3.5.1 A1 + A3 真三轨补强 (per stage3_v3_5_1 plan v0.3 §2.1.2 + §2.2.2;
# 三轨 full/ctx/ss 见 third-track plan §⑥/§7.3-A1: clarity / num_intensity 属情感族,
# 与 ctx 平价得第三轨 ss 银行+金科同句; ss 列缺失时各 aggregate_* 内部优雅跳过 ss)。
# `apply_v3_5_1` 与 `apply_v3_5_0` **并存** (修 C2); v3.6.0 合并方案: 新建
# `apply_supplementation` 统一入口, v3.5.0 entry 保留 deprecation alias 至 v3.7.0.
# ============================================================================


def aggregate_clarity_panel(df: pd.DataFrame, panel: pd.DataFrame,
                            median_amb_d0: Optional[float] = None,
                            median_amb_d0_ctx: Optional[float] = None,
                            median_amb_d0_ss: Optional[float] = None) -> dict:
    """v3.5.1 A1: 聚合 article 层 clarity 列到 bank-year panel (full/ctx 6 列 + ss 3 列).

    Per plan v0.3 §2.1.4 公式 (修 H2 + R8-H2 + R9-M3; 分母口径修订 omni 2026-06-11):
        mean_clarity_score_full[b,t] = Σ_valid w_i × clarity_score_full_i / Σ_valid w_i
        mean_frac_definite_full[b,t] = Σ_valid w_i × frac_definite_full_i / Σ_valid w_i
        frac_amb_articles_full[b,t]  = #{i: frac_ambiguous_full_i ≥ median_amb_d0}
                                       / n_clarity_valid_full   (n_clarity_valid ≥ 2 门)
        (同 ctx/ss 三轨; frac_amb 分母 = 该轨 clarity 非缺失文章数, 与分子同域 —
         空文/零 token 文章 (tone_words 显式 NaN) 不再进物理分母造成系统性下偏;
         n_clarity_valid < 2 或 median 为 NaN (全 NaN 轨) → NaN 而非假零)

    三轨 (full/ctx/ss): clarity 属情感/文本测度族 (lexical_complexity), 第三轨
    ss (银行+金科同句) 与 ctx 完全平价 (plan §④/§7.3-A1 "仅情感族得 _ss")。ss 列
    源自 stage 22 ss 轨, 缺失时 (旧 parquet 无 clarity_*_ss) 优雅跳过 ss 部分。

    Args:
        df: article-level DataFrame (含 clarity_* 三轨 article 列, 来自 stage 22).
        panel: bank-year panel DataFrame (含 target_bank + year).
        median_amb_d0: D0 frozen full 轨全样本中位数 (生产经 apply_v3_5_1 从 sidecar
            冻结值传入); if None, in-sample 计算 (首跑 freeze / 测试).
        median_amb_d0_ctx: D0 frozen ctx 轨中位数, 语义同上 (ctx 轨用自身分布阈值).
        median_amb_d0_ss: D0 frozen ss 轨中位数 (银行+金科同句), 语义同 ctx
            (ss 轨用自身分布阈值); ss 列缺失时不使用。

    Returns:
        dict: diagnostics + median_amb_d0 / median_amb_d0_ctx / median_amb_d0_ss actual used.
    """
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns or required_col not in df.columns:
            logger.warning(f"v3.5.1 A1: 缺 '{required_col}' 列, clarity panel 聚合跳过")
            return {'v3_5_1_clarity_added': [], 'median_amb_d0': float('nan'),
                    'median_amb_d0_ctx': float('nan'), 'median_amb_d0_ss': float('nan')}

    # 检查 article 层 clarity 列存在性 (graceful)。full/ctx 为硬必需 (任缺则整体跳过);
    # ss 三轨为加性可选 — ss 列齐则平价聚合, 缺则仅 full/ctx (旧 parquet 无 clarity_*_ss
    # 时优雅降级, 不阻塞主轨, 镜像约定 #3 的 ss guard)。
    required_article_cols = [
        'clarity_frac_ambiguous_full', 'clarity_frac_definite_full',
        'clarity_clarity_score_full',
        'clarity_frac_ambiguous_ctx', 'clarity_frac_definite_ctx',
        'clarity_clarity_score_ctx',
    ]
    missing = [c for c in required_article_cols if c not in df.columns]
    if missing:
        logger.info(f"v3.5.1 A1: article 层 clarity 列缺 {missing}, 跳过 panel 聚合 (graceful)")
        return {'v3_5_1_clarity_added': [], 'median_amb_d0': float('nan'),
                'median_amb_d0_ctx': float('nan'), 'median_amb_d0_ss': float('nan')}

    # ss 轨可用性: 三个 ss article 列齐备才聚合 ss (银行+金科同句, 平价第三轨)
    ss_article_cols = ['clarity_frac_ambiguous_ss', 'clarity_frac_definite_ss',
                       'clarity_clarity_score_ss']
    has_ss = all(c in df.columns for c in ss_article_cols)

    # D0 frozen median (修 H2 + R7-H1): 若未给, in-sample 算 (首跑 freeze);
    # 生产由 apply_v3_5_1 从 sidecar JSON 读冻结值传入 (fix(omni-known-open-2, 2026-06-11))
    if median_amb_d0 is None:
        median_amb_d0 = float(df['clarity_frac_ambiguous_full'].dropna().median())
        logger.info(f"v3.5.1 A1: D0 median_amb(full) 实测 = {sig4(median_amb_d0)}")
    # fix(encode_collab-01): ctx 轨用 ctx 自身分布的 median 二值化, 不再套用 full 轨阈值
    if median_amb_d0_ctx is None:
        median_amb_d0_ctx = float(df['clarity_frac_ambiguous_ctx'].dropna().median())
        logger.info(f"v3.5.1 A1: D0 median_amb(ctx) 实测 = {sig4(median_amb_d0_ctx)}")
    # ss 轨 (银行+金科同句) 用 ss 自身分布的 median 二值化 (镜像 ctx, 各轨独立阈值)
    if has_ss and median_amb_d0_ss is None:
        median_amb_d0_ss = float(df['clarity_frac_ambiguous_ss'].dropna().median())
        logger.info(f"v3.5.1 A1: D0 median_amb(ss) 实测 = {sig4(median_amb_d0_ss)}")

    # weight = stage21 media_authority × herd_decay
    # fix(herd-ghost-01): full/ctx/ss 三轨各配自己的 herd 权重 (Edwards 2001 measurement-treatment
    # matching), 不再让 ctx/ss 轨借用 herd_weight_full。herd_weight_{ctx,ss} 缺失时优雅回退 full。
    def _track_weight(track: str) -> pd.Series:
        wt = pd.Series(1.0, index=df.index)
        if 'media_authority_weight' in df.columns:
            wt = wt * df['media_authority_weight'].fillna(1.0)
        herd_col = f'herd_weight{track}'
        if herd_col in df.columns:
            wt = wt * df[herd_col].fillna(1.0)
        elif 'herd_weight_full' in df.columns:
            wt = wt * df['herd_weight_full'].fillna(1.0)
        return wt
    w_full = _track_weight('_full')
    w_ctx = _track_weight('_ctx')
    # ss 轨权重: 仅 ss 列齐备时计算 (与 ctx 同口径, 银行+金科同句平价第三轨)
    w_ss = _track_weight('_ss') if has_ss else None

    added_cols = []
    # 加 weighted columns 给 article level
    # 单次 assign 写入临时列, 避免逐列 insert 触发 pandas PerformanceWarning
    # fix(clarity-weighted-denom, metric-audit 2026-06-10): 加权均值分母须 mask 到各指标
    # valid 集, 否则 clarity 缺失文章的权重仍进物理分母 → Σ_valid(w·x)/Σ_all(w) 系统性下偏
    # (VW/MW/HW 同型未标记兄弟)。各指标(clarity/frac_definite × full/ctx/ss)用自己的 valid 分母。
    assign_kwargs = dict(
        _w_clarity_full=df['clarity_clarity_score_full'] * w_full,
        _w_clarity_ctx=df['clarity_clarity_score_ctx'] * w_ctx,
        _w_def_full=df['clarity_frac_definite_full'] * w_full,
        _w_def_ctx=df['clarity_frac_definite_ctx'] * w_ctx,
        _wd_clarity_full=w_full.where(df['clarity_clarity_score_full'].notna()),
        _wd_clarity_ctx=w_ctx.where(df['clarity_clarity_score_ctx'].notna()),
        _wd_def_full=w_full.where(df['clarity_frac_definite_full'].notna()),
        _wd_def_ctx=w_ctx.where(df['clarity_frac_definite_ctx'].notna()),
        _w_full=w_full,
        _w_ctx=w_ctx,
    )
    # ss 轨临时列 (镜像 ctx, 平价第三轨; 仅 ss 列齐备时加)
    if has_ss:
        assign_kwargs.update(
            _w_clarity_ss=df['clarity_clarity_score_ss'] * w_ss,
            _w_def_ss=df['clarity_frac_definite_ss'] * w_ss,
            _wd_clarity_ss=w_ss.where(df['clarity_clarity_score_ss'].notna()),
            _wd_def_ss=w_ss.where(df['clarity_frac_definite_ss'].notna()),
            _w_ss=w_ss,
        )
    df = df.assign(**assign_kwargs)

    agg_kwargs = dict(
        _sum_w_clarity_full=('_w_clarity_full', 'sum'),
        _sum_w_clarity_ctx=('_w_clarity_ctx', 'sum'),
        _sum_w_def_full=('_w_def_full', 'sum'),
        _sum_w_def_ctx=('_w_def_ctx', 'sum'),
        _sum_wd_clarity_full=('_wd_clarity_full', 'sum'),
        _sum_wd_clarity_ctx=('_wd_clarity_ctx', 'sum'),
        _sum_wd_def_full=('_wd_def_full', 'sum'),
        _sum_wd_def_ctx=('_wd_def_ctx', 'sum'),
        _sum_w_full=('_w_full', 'sum'),
        _sum_w_ctx=('_w_ctx', 'sum'),
        _n_articles=('_w_full', 'count'),
        # fix(omni-g-encode-collab-03, 2026-06-11): clarity-valid 计数 (count 自动跳 NaN),
        # 作 frac_amb_articles 分母 — 与分子 (s >= median).sum() 只可能数 valid 文章同域
        _n_clar_valid_full=('clarity_frac_ambiguous_full', 'count'),
        _n_clar_valid_ctx=('clarity_frac_ambiguous_ctx', 'count'),
        _n_amb_full=('clarity_frac_ambiguous_full',
                     lambda s: int((s >= median_amb_d0).sum())),
        _n_amb_ctx=('clarity_frac_ambiguous_ctx',
                    lambda s: int((s >= median_amb_d0_ctx).sum())),
    )
    # ss 轨聚合项 (镜像 ctx; 闭包捕获 median_amb_d0_ss, 仅 ss 齐备时加入)
    if has_ss:
        agg_kwargs.update(
            _sum_w_clarity_ss=('_w_clarity_ss', 'sum'),
            _sum_w_def_ss=('_w_def_ss', 'sum'),
            _sum_wd_clarity_ss=('_wd_clarity_ss', 'sum'),
            _sum_wd_def_ss=('_wd_def_ss', 'sum'),
            _sum_w_ss=('_w_ss', 'sum'),
            _n_clar_valid_ss=('clarity_frac_ambiguous_ss', 'count'),
            _n_amb_ss=('clarity_frac_ambiguous_ss',
                       lambda s: int((s >= median_amb_d0_ss).sum())),
        )
    agg = df.groupby(['target_bank', 'year']).agg(**agg_kwargs).reset_index()

    # 派生 panel 列 (各指标用自己 valid-mask 的权重和作分母, 域与分子一致)
    agg['mean_clarity_score_full'] = agg['_sum_w_clarity_full'] / agg['_sum_wd_clarity_full'].replace(0, float('nan'))
    agg['mean_clarity_score_ctx'] = agg['_sum_w_clarity_ctx'] / agg['_sum_wd_clarity_ctx'].replace(0, float('nan'))
    agg['mean_frac_definite_full'] = agg['_sum_w_def_full'] / agg['_sum_wd_def_full'].replace(0, float('nan'))
    agg['mean_frac_definite_ctx'] = agg['_sum_w_def_ctx'] / agg['_sum_wd_def_ctx'].replace(0, float('nan'))

    # fix(omni-g-encode-collab-03, 2026-06-11): frac_amb_articles 分母改 clarity-valid
    # 计数 (刚修的加权均值 valid-mask 分母同型同步, 见 L529 注释理由)。旧分母 _n_articles
    # =物理篇数 → clarity 缺失 (空文/零 token, tone_words.py 显式 NaN) 文章进分母不进
    # 分子的系统性下偏。≥ 2 mask (修 R8-H2) 同步迁移到各轨 valid 计数; median 为 NaN
    # (该轨全 NaN) 时输出 NaN 而非 "s>=NaN 全 False" 的全员假零。
    mask_full = agg['_n_clar_valid_full'] >= 2
    mask_ctx = agg['_n_clar_valid_ctx'] >= 2
    agg['frac_amb_articles_full'] = agg['_n_amb_full'] / agg['_n_clar_valid_full'].where(mask_full)
    agg['frac_amb_articles_ctx'] = agg['_n_amb_ctx'] / agg['_n_clar_valid_ctx'].where(mask_ctx)
    if _is_nan(median_amb_d0):
        agg['frac_amb_articles_full'] = float('nan')
    if _is_nan(median_amb_d0_ctx):
        agg['frac_amb_articles_ctx'] = float('nan')

    out_cols = ['mean_clarity_score_full', 'mean_clarity_score_ctx',
                'mean_frac_definite_full', 'mean_frac_definite_ctx',
                'frac_amb_articles_full', 'frac_amb_articles_ctx']

    # ss 轨 (银行+金科同句) 派生 panel 列 (镜像 ctx, 平价第三轨; 仅 ss 齐备时)
    if has_ss:
        agg['mean_clarity_score_ss'] = agg['_sum_w_clarity_ss'] / agg['_sum_wd_clarity_ss'].replace(0, float('nan'))
        agg['mean_frac_definite_ss'] = agg['_sum_w_def_ss'] / agg['_sum_wd_def_ss'].replace(0, float('nan'))
        mask_ss = agg['_n_clar_valid_ss'] >= 2
        agg['frac_amb_articles_ss'] = agg['_n_amb_ss'] / agg['_n_clar_valid_ss'].where(mask_ss)
        if _is_nan(median_amb_d0_ss):
            agg['frac_amb_articles_ss'] = float('nan')
        out_cols += ['mean_clarity_score_ss', 'mean_frac_definite_ss',
                     'frac_amb_articles_ss']

    # idempotent: 先 drop panel 已有的 out_cols (避免 merge 后 _x/_y 后缀冲突)
    for c in out_cols:
        if c in panel.columns:
            del panel[c]

    # merge 回 panel
    keep = ['target_bank', 'year'] + out_cols
    panel_merged = panel.merge(agg[keep], on=['target_bank', 'year'], how='left')
    for c in out_cols:
        panel[c] = panel_merged[c].values
        added_cols.append(c)

    # cleanup (含 ss 临时列, 仅 ss 聚合过才存在)
    for tmp in ('_w_clarity_full', '_w_clarity_ctx', '_w_def_full', '_w_def_ctx',
                '_w_full', '_w_ctx',
                '_w_clarity_ss', '_w_def_ss', '_w_ss'):
        if tmp in df.columns:
            del df[tmp]

    return {'v3_5_1_clarity_added': added_cols, 'median_amb_d0': median_amb_d0,
            'median_amb_d0_ctx': median_amb_d0_ctx, 'median_amb_d0_ss': median_amb_d0_ss}


def aggregate_num_intensity_panel(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """v3.5.1 A3: 聚合 article 层 num_intensity 列到 bank-year panel.

    句级 (mean_num_intensity_{full,ctx,ss}) + 词级替代版
    (mean_num_intensity_word_{full,ctx,ss}, §4.3, 2026-06-05 新增)。
    Per plan v0.3 §2.2.4 公式: weighted mean by stage21 weights (媒体权威×herd)。

    三轨 (full/ctx/ss): num_intensity 属情感/文本测度族 (numerical_intensity), 第三轨
    ss (银行+金科同句) 与 ctx 完全平价 (plan §④/§7.3-A1 "仅情感族得 _ss")。ss 句级/词级
    列源自 stage 22 ss 轨, 缺失时 (旧 parquet 无 num_intensity[_word]_ss) 优雅跳过 ss 部分。
    """
    for required_col in ('target_bank', 'year'):
        if required_col not in panel.columns or required_col not in df.columns:
            return {'v3_5_1_num_intensity_added': []}

    if 'num_intensity_full' not in df.columns or 'num_intensity_ctx' not in df.columns:
        logger.info("v3.5.1 A3: num_intensity article 列缺, 跳过 panel 聚合 (graceful)")
        return {'v3_5_1_num_intensity_added': []}

    # fix(herd-ghost-01): full/ctx/ss 三轨各配自己的 herd 权重 (与 clarity 聚合同口径)
    def _track_weight(track: str) -> pd.Series:
        wt = pd.Series(1.0, index=df.index)
        if 'media_authority_weight' in df.columns:
            wt = wt * df['media_authority_weight'].fillna(1.0)
        herd_col = f'herd_weight{track}'
        if herd_col in df.columns:
            wt = wt * df[herd_col].fillna(1.0)
        elif 'herd_weight_full' in df.columns:
            wt = wt * df['herd_weight_full'].fillna(1.0)
        return wt
    w_full = _track_weight('_full')
    w_ctx = _track_weight('_ctx')

    # ss 轨 (银行+金科同句, 平价第三轨) 句级列是否就位 (graceful: 旧 parquet 无 ss 时仅聚 full/ctx)
    has_ss = 'num_intensity_ss' in df.columns
    w_ss = _track_weight('_ss') if has_ss else None

    # word-level 替代版 (§4.3) 列是否就位 (graceful: 旧 parquet 无此列时仅聚句级版)
    has_word = ('num_intensity_word_full' in df.columns
                and 'num_intensity_word_ctx' in df.columns)
    # ss 词级替代版 (须 ss 句级先就位; 镜像 has_word 的 full/ctx 守卫)
    has_word_ss = has_ss and ('num_intensity_word_ss' in df.columns)

    # 单次 assign 写入临时列, 避免逐列 insert 触发 pandas PerformanceWarning
    # fix(numint-weighted-denom, metric-audit 2026-06-10): 加权均值分母须 mask 到各指标的
    # valid 集 (num_intensity 非 NaN), 否则空文本(A7 显式 NaN 保护)的权重仍进物理分母 →
    # Σ_valid(w·x)/Σ_all(w) 系统性下偏, 抵消 A7 的 NaN 语义。各指标用自己的 valid-mask 分母。
    assign_kwargs = dict(
        _w_ni_full=df['num_intensity_full'] * w_full,
        _w_ni_ctx=df['num_intensity_ctx'] * w_ctx,
        _wd_ni_full=w_full.where(df['num_intensity_full'].notna()),
        _wd_ni_ctx=w_ctx.where(df['num_intensity_ctx'].notna()),
        _w_full=w_full,
        _w_ctx=w_ctx,
    )
    if has_word:
        # 词级替代版加权分子 (与句级版同权重 w_full/w_ctx, 仅 article 分母从句数→词数)
        assign_kwargs['_w_niw_full'] = df['num_intensity_word_full'] * w_full
        assign_kwargs['_w_niw_ctx'] = df['num_intensity_word_ctx'] * w_ctx
        assign_kwargs['_wd_niw_full'] = w_full.where(df['num_intensity_word_full'].notna())
        assign_kwargs['_wd_niw_ctx'] = w_ctx.where(df['num_intensity_word_ctx'].notna())
    if has_ss:
        # ss 句级临时列 (镜像 ctx, 平价第三轨)
        assign_kwargs['_w_ni_ss'] = df['num_intensity_ss'] * w_ss
        assign_kwargs['_wd_ni_ss'] = w_ss.where(df['num_intensity_ss'].notna())
        assign_kwargs['_w_ss'] = w_ss
    if has_word_ss:
        # ss 词级替代版临时列
        assign_kwargs['_w_niw_ss'] = df['num_intensity_word_ss'] * w_ss
        assign_kwargs['_wd_niw_ss'] = w_ss.where(df['num_intensity_word_ss'].notna())
    df = df.assign(**assign_kwargs)

    agg_kwargs = dict(
        _sum_w_ni_full=('_w_ni_full', 'sum'),
        _sum_w_ni_ctx=('_w_ni_ctx', 'sum'),
        _sum_wd_ni_full=('_wd_ni_full', 'sum'),
        _sum_wd_ni_ctx=('_wd_ni_ctx', 'sum'),
        _sum_w_full=('_w_full', 'sum'),
        _sum_w_ctx=('_w_ctx', 'sum'),
    )
    if has_word:
        agg_kwargs['_sum_w_niw_full'] = ('_w_niw_full', 'sum')
        agg_kwargs['_sum_w_niw_ctx'] = ('_w_niw_ctx', 'sum')
        agg_kwargs['_sum_wd_niw_full'] = ('_wd_niw_full', 'sum')
        agg_kwargs['_sum_wd_niw_ctx'] = ('_wd_niw_ctx', 'sum')
    if has_ss:
        agg_kwargs['_sum_w_ni_ss'] = ('_w_ni_ss', 'sum')
        agg_kwargs['_sum_wd_ni_ss'] = ('_wd_ni_ss', 'sum')
        agg_kwargs['_sum_w_ss'] = ('_w_ss', 'sum')
    if has_word_ss:
        agg_kwargs['_sum_w_niw_ss'] = ('_w_niw_ss', 'sum')
        agg_kwargs['_sum_wd_niw_ss'] = ('_wd_niw_ss', 'sum')
    agg = df.groupby(['target_bank', 'year']).agg(**agg_kwargs).reset_index()
    # 分母 = 各指标 valid-mask 后的权重和 (域与分子一致)
    swd_ni_full = agg['_sum_wd_ni_full'].replace(0, float('nan'))
    swd_ni_ctx = agg['_sum_wd_ni_ctx'].replace(0, float('nan'))
    agg['mean_num_intensity_full'] = agg['_sum_w_ni_full'] / swd_ni_full
    agg['mean_num_intensity_ctx'] = agg['_sum_w_ni_ctx'] / swd_ni_ctx

    out_cols = ['mean_num_intensity_full', 'mean_num_intensity_ctx']
    if has_ss:
        # ss 句级数字密度 bank-year 加权均值 (镜像 ctx, 平价第三轨)
        swd_ni_ss = agg['_sum_wd_ni_ss'].replace(0, float('nan'))
        agg['mean_num_intensity_ss'] = agg['_sum_w_ni_ss'] / swd_ni_ss
        out_cols += ['mean_num_intensity_ss']
    if has_word:
        # 兑现 §4.3: 词级数字密度 bank-year 加权均值 (分母词数, 对中文句读 sparse 稳健)
        swd_niw_full = agg['_sum_wd_niw_full'].replace(0, float('nan'))
        swd_niw_ctx = agg['_sum_wd_niw_ctx'].replace(0, float('nan'))
        agg['mean_num_intensity_word_full'] = agg['_sum_w_niw_full'] / swd_niw_full
        agg['mean_num_intensity_word_ctx'] = agg['_sum_w_niw_ctx'] / swd_niw_ctx
        out_cols += ['mean_num_intensity_word_full', 'mean_num_intensity_word_ctx']
    if has_word_ss:
        # ss 词级数字密度 (镜像 full/ctx 词级版)
        swd_niw_ss = agg['_sum_wd_niw_ss'].replace(0, float('nan'))
        agg['mean_num_intensity_word_ss'] = agg['_sum_w_niw_ss'] / swd_niw_ss
        out_cols += ['mean_num_intensity_word_ss']
    # idempotent: 先 drop panel 已有的 out_cols (避免 merge _x/_y 后缀冲突)
    for c in out_cols:
        if c in panel.columns:
            del panel[c]
    keep = ['target_bank', 'year'] + out_cols
    panel_merged = panel.merge(agg[keep], on=['target_bank', 'year'], how='left')
    for c in out_cols:
        panel[c] = panel_merged[c].values

    for tmp in ('_w_ni_full', '_w_ni_ctx', '_w_niw_full', '_w_niw_ctx', '_w_full', '_w_ctx',
                '_w_ni_ss', '_w_niw_ss', '_w_ss'):
        if tmp in df.columns:
            del df[tmp]

    # 📊 结果分布 (产出 headline 测度 mean_num_intensity_{full,ctx,ss} 的 bank-year 横截面
    # 分布): 此前本函数对其输出零日志 (仅 graceful-skip 行), 审稿人需要实测的数字密度分布。
    # 仅日志, 读已聚合进 panel 的列 (discarded local), 不改任何写盘值/schema/控制流。
    try:
        for _nm in ('mean_num_intensity_full', 'mean_num_intensity_ctx',
                    'mean_num_intensity_ss'):
            if _nm not in panel.columns:
                continue
            _v_ni = panel[_nm].dropna()
            if len(_v_ni) == 0:
                continue
            logger.info(
                f"  📊 {_nm} 分布 (bank-year): 非空 {len(_v_ni):,d} · "
                f"mean={sig4(_v_ni.mean())} · std={sig4(_v_ni.std())} · "
                f"min={sig4(_v_ni.min())} · max={sig4(_v_ni.max())}"
            )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ A3 num_intensity 分布日志失败 (graceful): {_e}")

    return {'v3_5_1_num_intensity_added': out_cols}


def apply_v3_5_1(df: pd.DataFrame, panel: pd.DataFrame,
                 prompt_v8_sha256: Optional[str] = None) -> dict:
    """v3.5.1 A1 + A3 panel 聚合一站入口 (与 apply_v3_5_0 并存, 修 C2).

    顺序: 读 sidecar 冻结 median → A1 clarity → A3 num_intensity → 写 sidecar JSON.

    Sidecar JSON path: ``data/processed/v3_5_1_constants.json`` (修 C1' + R7-H1
    双 anchor: prompt_v8_sha256 + stage21_last_run_timestamp).

    fix(omni-known-open-2, 2026-06-11) frozen-median 接线 (防泄漏机制): clarity 二值化
    阈值 median_amb_d0 / median_amb_d0_ctx / median_amb_d0_ss 优先读 sidecar 已冻结值传入
    聚合; sidecar 不存在 (或锚值缺失/NaN) 则首跑 in-sample 计算并持久化, 后续跑一律读冻结
    值 — 阈值不再随每次重跑的样本组成漂移 (look-ahead / 全样本中位数泄漏防护, D0 freeze
    语义)。ss 轨 (银行+金科同句) 阈值同 ctx 平价冻结 (用自身分布, plan §7.3-A1)。

    Args:
        df: article-level DataFrame (含 clarity_* 三轨列 + num_intensity 三轨列;
            ss 列缺失时 aggregate_* 内部优雅跳过 ss 部分).
        panel: bank-year panel DataFrame.
        prompt_v8_sha256: optional anchor (写入 sidecar).

    Returns:
        dict: {v3_5_1_clarity_added, v3_5_1_num_intensity_added, median_amb_d0,
        median_amb_d0_ctx, median_amb_d0_ss, sidecar_path}.
    """
    import os
    from datetime import datetime, timezone

    # ---- 子步骤 banner (helper module, 复用 panel-build 运行期日志; 不重打 ENV/CONFIG) ----
    _t0 = time.time()
    try:
        logger.info("=" * 72)
        logger.info(
            "  步骤 A1+A3 (encode_collab.apply_v3_5_1): clarity 清晰度 + num_intensity "
            "数字密度 文章级→bank-year 加权聚合 (三轨 full/ctx/ss)"
        )
        logger.info(
            f"    · 输入: article df={df.shape[0]:,d} 行 × {df.shape[1]:,d} 列, "
            f"panel={panel.shape[0]:,d} 行"
        )
        logger.info(
            "    · 方法 (词典法文本测度族, D0-frozen median 二值化防全样本中位数泄漏):"
        )
        for _ref in _METHOD_REFS_D4[:1]:  # Loughran & McDonald (2011) 词典文本分析锚点
            logger.info(f"        - {_ref}")
        # 📖 方法论依据 (A3 num_intensity 数字密度专属): mean_num_intensity_* 度量新闻
        # 叙事的数字披露密集度, 直接源文献为"数字披露的叙事语境"专论 (非情感词典)。
        logger.info(
            "    · 📖 数字密度 (num_intensity) 测度依据 (数字披露的叙事语境):"
        )
        for _ref in _METHOD_REFS_NUMINT:
            logger.info(f"        - {_ref}")
        logger.info(
            "    · 白话: 把每篇文章的措辞清晰度/数字密集度按媒体权威×跟风权重加权, "
            "聚合到银行-年; 二值化阈值用历史冻结中位数, 不随每次重跑漂移。确定性纯 CPU/$0。"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_1 banner 日志失败 (graceful): {_e}")

    sidecar_path = 'data/processed/v3_5_1_constants.json'
    # P0-B (2026-05-25): preserve-if-set — 若 caller 未显式传 prompt_v8_sha256
    # 但已有 sidecar 含非 null SHA, 保留旧值 (避免 stage 21 重跑无声 wipe
    # 已手动锚定的 SHA). 仅当 caller 显式传 SHA 时覆盖.
    # 审计扩展 (2026-05-29): median_amb_d0 同为 "D0 frozen 全样本中位数" 手动锚点
    # (CLAUDE.md 双 anchor); 与 SHA 同理, 当 in-sample 重算得 NaN / 空列表 (文章级
    # clarity 列缺失时早退) 时须保留既有锚值, 否则 run_pipeline_function 每次重跑
    # 都会把受跟踪的 frozen anchor 清成 NaN/空 (见 aggregate_clarity_panel 文档串)。
    # fix(omni-known-open-2, 2026-06-11): sidecar 读移到聚合**之前**, 冻结 median 真正
    # 接线进 aggregate_clarity_panel (此前每次重跑都 in-sample 重算, freeze 名存实亡)。
    existing_sha = None
    existing_median = None
    existing_median_ctx = None
    existing_median_ss = None
    existing_clarity_cols = None
    existing_ni_cols = None
    if os.path.exists(sidecar_path):
        try:
            with open(sidecar_path, 'r', encoding='utf-8') as _f:
                _prev = json.load(_f)
            existing_sha = _prev.get('prompt_v8_sha256')
            existing_median = _prev.get('median_amb_d0')
            existing_median_ctx = _prev.get('median_amb_d0_ctx')
            # ss 轨冻结阈值 (银行+金科同句, 平价第三轨; 旧 sidecar 无此键 → None)
            existing_median_ss = _prev.get('median_amb_d0_ss')
            existing_clarity_cols = _prev.get('a1_clarity_panel_cols')
            existing_ni_cols = _prev.get('a3_num_intensity_panel_cols')
        except Exception:  # noqa: BLE001
            pass

    # A1 clarity panel 聚合 (D0 frozen median: sidecar 有值用冻结值, 否则首跑 in-sample)
    frozen_median = existing_median if not _is_nan(existing_median) else None
    frozen_median_ctx = existing_median_ctx if not _is_nan(existing_median_ctx) else None
    frozen_median_ss = existing_median_ss if not _is_nan(existing_median_ss) else None
    clarity_diag = aggregate_clarity_panel(df, panel, median_amb_d0=frozen_median,
                                           median_amb_d0_ctx=frozen_median_ctx,
                                           median_amb_d0_ss=frozen_median_ss)

    # A3 num_intensity panel 聚合
    ni_diag = aggregate_num_intensity_panel(df, panel)

    # 写 sidecar JSON (修 C1' 序列化丢失 -> parquet/.dta 不保留 attrs)
    effective_sha = prompt_v8_sha256 if prompt_v8_sha256 is not None else existing_sha

    _recomputed_median = clarity_diag.get('median_amb_d0', float('nan'))
    effective_median = (
        _recomputed_median if not _is_nan(_recomputed_median)
        else (existing_median if not _is_nan(existing_median) else _recomputed_median)
    )
    _recomputed_median_ctx = clarity_diag.get('median_amb_d0_ctx', float('nan'))
    effective_median_ctx = (
        _recomputed_median_ctx if not _is_nan(_recomputed_median_ctx)
        else (existing_median_ctx if not _is_nan(existing_median_ctx)
              else _recomputed_median_ctx)
    )
    # ss 轨阈值 preserve-if-set (镜像 ctx; ss 列缺失时 clarity_diag 返回 NaN → 保留旧锚值)
    _recomputed_median_ss = clarity_diag.get('median_amb_d0_ss', float('nan'))
    effective_median_ss = (
        _recomputed_median_ss if not _is_nan(_recomputed_median_ss)
        else (existing_median_ss if not _is_nan(existing_median_ss)
              else _recomputed_median_ss)
    )
    _recomputed_clarity = clarity_diag.get('v3_5_1_clarity_added', []) or []
    effective_clarity_cols = _recomputed_clarity or (existing_clarity_cols or [])
    _recomputed_ni = ni_diag.get('v3_5_1_num_intensity_added', []) or []
    effective_ni_cols = _recomputed_ni or (existing_ni_cols or [])
    try:
        os.makedirs(os.path.dirname(sidecar_path), exist_ok=True)
        sidecar = {
            'plan_version': 'v3.5.1',
            'median_amb_d0': effective_median,
            # fix(omni-known-open-2, 2026-06-11): ctx 轨阈值同步冻结 (ctx 用自身分布)
            'median_amb_d0_ctx': effective_median_ctx,
            # ss 轨阈值同步冻结 (银行+金科同句, 平价第三轨, 用自身分布; plan §7.3-A1)
            'median_amb_d0_ss': effective_median_ss,
            'prompt_v8_sha256': effective_sha,
            'stage21_last_run_timestamp': datetime.now(timezone.utc).isoformat(),
            'a1_clarity_panel_cols': effective_clarity_cols,
            'a3_num_intensity_panel_cols': effective_ni_cols,
        }
        with open(sidecar_path, 'w', encoding='utf-8') as f:
            json.dump(sidecar, f, ensure_ascii=False, indent=2)
        logger.info(f"v3.5.1: sidecar JSON 写入 {sidecar_path}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"v3.5.1: sidecar JSON 写入失败 (graceful): {e}")

    # ---- 阶段计时 + 结果判读 (纯日志) ----
    try:
        _n_clar = len(clarity_diag.get('v3_5_1_clarity_added', []) or [])
        _n_ni = len(ni_diag.get('v3_5_1_num_intensity_added', []) or [])
        logger.info(
            f"  ⏱ apply_v3_5_1 计时: 合计 {sig4(time.time() - _t0)}s "
            f"(clarity {_n_clar:,d} 列 + num_intensity {_n_ni:,d} 列)"
        )
        # 结果判读 (clarity 列产出 + 冻结阈值): 满产 (full/ctx 各 3 + ss 3 = 9 列) 为好;
        # 仅 full/ctx (6 列) 为临界 (旧 parquet 无 ss 轨, 第三轨平价覆盖缺失); 0 列偏弱
        # (上游 stage 22 clarity article 列缺失, 须重跑)。
        if _n_clar >= 9:
            _v = "好 (三轨 full/ctx/ss 满产)"
        elif _n_clar >= 6:
            _v = "临界 (仅 full/ctx, ss 第三轨缺失)"
        elif _n_clar > 0:
            _v = "偏弱 (clarity 列部分产出)"
        else:
            _v = "缺失 (上游 stage 22 clarity 列不可用, 优雅跳过)"
        _med = clarity_diag.get('median_amb_d0', float('nan'))
        logger.info(
            f"  📊 A1 clarity 判读: 产出 {_n_clar:,d} 列 → {_v}; "
            f"frozen median_amb(full)={sig4(_med)}"
        )
        # 📊 结果分布 (headline 测度 mean_clarity_score_{full,ctx,ss} 的 bank-year 横截面
        # 分布): 此前 summary 只报"列数 + frozen median", 从不报分布 — 审稿人要看的是
        # 实测分布。仅日志, 读已聚合进 panel 的列 (discarded local), 不改任何写盘值/schema。
        try:
            for _cm in ('mean_clarity_score_full', 'mean_clarity_score_ctx',
                        'mean_clarity_score_ss'):
                if _cm not in panel.columns:
                    continue
                _v_clar = panel[_cm].dropna()
                if len(_v_clar) == 0:
                    continue
                logger.info(
                    f"  📊 {_cm} 分布 (bank-year): 非空 {len(_v_clar):,d} · "
                    f"mean={sig4(_v_clar.mean())} · median={sig4(_v_clar.median())} · "
                    f"std={sig4(_v_clar.std())} · min={sig4(_v_clar.min())} · "
                    f"max={sig4(_v_clar.max())}"
                )
        except Exception as _e2:  # noqa: BLE001
            logger.warning(f"  ⚠ A1 clarity 分布日志失败 (graceful): {_e2}")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_1 计时/判读日志失败 (graceful): {_e}")

    return {
        **clarity_diag,
        **ni_diag,
        'sidecar_path': sidecar_path,
    }


def apply_v3_5_2(df: pd.DataFrame, panel: pd.DataFrame) -> dict:
    """v3.5.2 PR #2/#3 + v3.10.0: LM 6 子词典 + FLS 的 panel 层聚合 (三轨)。

    把 article 级 LM/FLS frac 列按简单均值聚合到 bank-year panel
    (输出列名与 article 源列**同名**, dst_col = src_col, 无 _panel 后缀 —
    与下游 Stata/codebook 既有契约期待的列名一致):
        LM 6 子词典 × 3 轨 (full, ctx, ss) = 18 个 panel 列:
            uncert_frac / litig_frac / constr_frac / modal_strong_frac /
            modal_weak_frac / complexity_frac  各 × {full,ctx,ss} (mean)
        FLS 双基名 (frac_fls 双门 canonical + frac_fls_fonly 单门稳健臂, 2026-07-03 D2) × 3 轨 = 6 个 panel 列 (mean)

    这些 panel 列为下游 Stata/codebook 既有契约
    (即下游 Stata 已期待这些列存在)。

    _ss 第三轨 (v3.10.0): LM/FLS 非情感 lexicon 族**亦产 _ss** —— 这是用户
    2026 决策对 §7.3-A1 "非情感族仅 full/ctx 两轨" 冻结设计的**有意推翻**
    (理由: 第三轨平价覆盖)。原仅情感族 (clarity/num_intensity) 得 _ss 的限制
    已解除; A2 新增 modal_weak/complexity 两子集亦随 6×3 矩阵产出。

    Args:
        df: article 级 DataFrame (含 LM 6 子集 + FLS article 列, 三轨)。
        panel: bank-year panel DataFrame (原地新增 24 列; 2026-07-03 D2 +fonly 3 列)。

    Returns:
        dict: {v3_5_2_lm_added, v3_5_2_fls_added, v3_5_2_skipped_reason}。
    """
    # ---- 子步骤 banner (helper module, 复用 panel-build 运行期日志; 不重打 ENV/CONFIG) ----
    _t0 = time.time()
    try:
        logger.info("=" * 72)
        logger.info(
            "  步骤 v3.5.2 (encode_collab.apply_v3_5_2): LM 6 子词典 + FLS 文章级 frac "
            "→ bank-year 简单均值聚合 (三轨 full/ctx/ss, 24 列; D2 +frac_fls_fonly)"
        )
        logger.info(
            f"    · 输入: article df={df.shape[0]:,d} 行 × {df.shape[1]:,d} 列, "
            f"panel={panel.shape[0]:,d} 行"
        )
        logger.info("    · 方法 (LM 子词典文本分析, 不确定/诉讼/约束/语气/复杂度 + 前瞻陈述 FLS):")
        for _ref in _METHOD_REFS_D4[:1]:  # Loughran & McDonald (2011) 词典文本分析锚点
            logger.info(f"        - {_ref}")
        # 📖 方法论依据 (FLS 前瞻陈述专属): frac_fls_* 是 FLS 词表占比构念 (tone_dicts.json
        # FLS 词表操作化), 源文献为下列 FLS 测度专论, 而非 LM (2011) 情感词典。
        logger.info(
            "    · 📖 前瞻陈述 (FLS) frac_fls 测度依据 (FLS 词表操作化 + 比例度量奠基):"
        )
        for _ref in _METHOD_REFS_FLS:
            logger.info(f"        - {_ref}")
        logger.info(
            "    · 白话: 把每篇文章在 6 个语言学子词典 + 前瞻陈述上的词频占比, "
            "按银行-年取简单均值, 供下游 Stata/codebook 既有契约列。确定性纯 CPU/$0。"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_2 banner 日志失败 (graceful): {_e}")

    # v3.10.0: 6 子集前缀直接复用 lm_non_sentiment.SUBSET_PREFIXES (单一事实源, 防漂移)。
    # 现值 = ('uncert','litig','constr','modal_strong','modal_weak','complexity')。
    LM_KEYS = SUBSET_PREFIXES
    # v3.10.0: LM/FLS 全族产 _ss (用户决策推翻 §7.3-A1, 见上 docstring)。
    TRACKS = ('full', 'ctx', 'ss')

    added_cols: list[str] = []
    skipped_cols: list[str] = []

    # 上游列健全性检查 (缺键列则整体跳过)
    needed = ['target_bank', 'year']
    for col in needed:
        if col not in df.columns:
            return {
                'v3_5_2_lm_added': [],
                'v3_5_2_fls_added': [],
                'v3_5_2_skipped_reason': f"article df 缺 '{col}' 列, 跳过 v3.5.2 panel-agg",
            }

    agg_dict: dict[str, tuple[str, str]] = {}

    # LM 6 subdicts × 3 tracks (v3.10.0: LM_KEYS=SUBSET_PREFIXES 6, TRACKS=full/ctx/ss)
    for k in LM_KEYS:
        for track in TRACKS:
            src_col = f'{k}_frac_{track}'
            dst_col = src_col  # 与下游 Stata/codebook 既有契约列名一致
            if src_col in df.columns:
                agg_dict[dst_col] = (src_col, 'mean')
                added_cols.append(dst_col)
            else:
                skipped_cols.append(src_col)

    # FLS × 3 tracks (v3.10.0: TRACKS=full/ctx/ss); 2026-07-03 §5 D2 双基名:
    # frac_fls (双门 canonical) + frac_fls_fonly (单门稳健臂, 互为稳健、不分主次;
    # 禁混同一 over-identified Hansen J)。同名直聚合 (dst=src, 非 avg_ 前缀范式)。
    for base in ('frac_fls', 'frac_fls_fonly'):
        for track in TRACKS:
            src_col = f'{base}_{track}'
            dst_col = src_col
            if src_col in df.columns:
                agg_dict[dst_col] = (src_col, 'mean')
                added_cols.append(dst_col)
            else:
                skipped_cols.append(src_col)

    if not agg_dict:
        return {
            'v3_5_2_lm_added': [],
            'v3_5_2_fls_added': [],
            'v3_5_2_skipped_reason': f"article df 缺所有 LM/FLS 源列 ({skipped_cols[:3]}...), 跳过",
        }

    # 聚合到 bank-year (文章级 frac 的简单均值)
    agg_panel = (
        df.groupby(['target_bank', 'year'], as_index=False)
        .agg(**agg_dict)
    )

    # 按键匹配合并进既有 panel (追加列)
    # fix(omni-g-encode-collab-04, 2026-06-11): idempotent pre-drop — 镜像 clarity/
    # num_intensity 聚合的同款防护; 否则 panel 已含同名列时 (二次调用/增量重编码)
    # merge 默认 suffixes 产生 *_x/*_y 幻影列双双入 panel, 未后缀陈旧原列保旧值,
    # 下游 stata_export 按精确列名抓到陈旧值。
    for c in added_cols:
        if c in panel.columns:
            del panel[c]
    panel_pre_cols = set(panel.columns)
    merged = panel.merge(agg_panel, on=['target_bank', 'year'], how='left')
    new_cols = [c for c in merged.columns if c not in panel_pre_cols]

    # 原地往 panel (调用方传入的 DataFrame) 加列
    for c in new_cols:
        panel[c] = merged[c].values

    lm_added = [c for c in added_cols if any(c.startswith(k) for k in LM_KEYS)]
    fls_added = [c for c in added_cols if 'fls' in c]

    # ---- 阶段计时 + 结果判读 (纯日志) ----
    try:
        # 期望满产: LM 6 子集 × 3 轨 = 18 + FLS 双基名 (canonical + fonly, 2026-07-03 D2)
        # × 3 轨 = 6 → 共 24 列。
        _n_lm, _n_fls = len(lm_added), len(fls_added)
        _n_total = _n_lm + _n_fls
        if _n_total >= 24:
            _v = "好 (LM 18 + FLS 6 三轨满产)"
        elif _n_total >= 21:
            _v = "临界 (fonly 稳健臂缺失, 多半旧 parquet 未回填 D2 列)"
        elif _n_total >= 14:
            _v = "临界 (部分轨缺失, 多半旧 parquet 无 _ss 第三轨)"
        else:
            _v = "偏弱 (上游 stage 22 LM/FLS article 列大量缺失)"
        logger.info(
            f"  ⏱ apply_v3_5_2 计时: 合计 {sig4(time.time() - _t0)}s"
        )
        logger.info(
            f"  📊 v3.5.2 LM+FLS 判读: LM {_n_lm:,d} 列 + FLS {_n_fls:,d} 列 = "
            f"{_n_total:,d}/24 → {_v}; 跳过源列 {len(skipped_cols):,d} 个"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  ⚠ apply_v3_5_2 计时/判读日志失败 (graceful): {_e}")

    return {
        'v3_5_2_lm_added': lm_added,
        'v3_5_2_fls_added': fls_added,
        'v3_5_2_skipped_reason': None,
    }
