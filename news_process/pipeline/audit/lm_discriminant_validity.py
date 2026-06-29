"""news_process.pipeline.audit.lm_discriminant_validity — stage 39e.

v3.5.2 PR #4 — LM 6 子词典与 v3.5.1 lexical clarity / numerical intensity
的 panel-level 判别效度 (Discriminant Validity) 测试.

学术依据
--------
Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). A new criterion for
assessing discriminant validity in variance-based structural equation
modeling. Journal of the Academy of Marketing Science, 43(1), 115-135.
→ HTMT (Heterotrait-Monotrait ratio) 双 cutoff: 0.85 strict / 0.90 lenient

Cohen, J. (1960). A coefficient of agreement for nominal scales.
Educational and Psychological Measurement, 20(1), 37-46.

Cronbach, L. J. (1951). Coefficient alpha and the internal structure of
tests. Psychometrika, 16(3), 297-334.

测试指标对
----------
本 stage 测试 8 维构念间的判别效度 (v3.10.0: LM 4→6 子集):
    1. uncert_frac (LM uncertainty)
    2. litig_frac (LM litigious)
    3. constr_frac (LM constraining)
    4. modal_strong_frac (LM modal_strong)
    5. modal_weak_frac (LM weak_modal, v3.10.0)
    6. complexity_frac (LM complexity, v3.10.0)
    7. clarity_score (v3.5.1 A1)
    8. num_intensity (v3.5.1 A3)

预期: 8×8 HTMT 矩阵中 LM 6 子集互相 HTMT < 0.85, 且与 clarity / num_intensity
HTMT < 0.85 (判别效度通过).

输入 / 输出
-----------
输入: ``data/processed/40_panel_yearly.parquet`` (含 v3.5.1 + v3.5.2 全部列)
输出 (按 full / ctx / ss 三轨各写一份):
    ``eval_reports/74_lm_htmt_matrix_{ctx,full,ss}.csv``   8×8 HTMT 矩阵
    ``eval_reports/74_lm_permutation_{ctx,full,ss}.csv``   1000-rep permutation null (seed=42)
    (仅产上述 CSV — 与 core/schemas.py 登记的契约一致; 不单独落盘 Cohen κ /
     Cronbach α CSV, 亦不产 parquet; ss = 银行+金科同句共现轨, 列缺失时该轨优雅跳过)

实现状态
--------
``main()`` 与 ``permutation_null`` 已由 PR #14 集成完成 (非 stub): 依赖 v3.5.2
PR #3 (lm_non_sentiment) 输出的 panel 列存在; G-A1.2 准入门控
(panel HTMT < 0.85) 在该集成中验证。

白话: LM 词典给文本打了 6 类标签 (不确定性/诉讼/约束/强弱情态/复杂度), 我们又造了
清晰度和数字密集度两个测度。这一步检查这 8 个测度两两相关是否都低于
0.85 — 低才说明它们各测各的、没有重复造轮子; 否则要请专家复核。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 74_lm_discriminant_validity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 `40_panel_yearly.parquet`(银行-年度面板)。每轨 8 个 indicator: LM 6 子词典频率 uncert_frac / litig_frac / constr_frac / modal_strong_frac / modal_weak_frac / complexity_frac, 加 v3.5.1 的 mean_clarity_score、mean_num_intensity(各带 _ctx/_full/_ss 后缀)。panel 缺失时 sys.exit(0) 优雅跳过。

**处理步骤**(`main`):
- `_apply_llm_valid_mask`: 与 39d 统一, 优先 `n_articles_llm_valid ≥ 2`(缺该列回退 n_articles, 两列均缺则不过滤)以保证 HTMT/α/permutation 同样本可比(修 omni-g-audit-family-05)。
- 三轨循环, 每轨: `compute_htmt_matrix` 取 present 列(<2 列跳过)算 `panel[present].corr().abs()`(单 item HTMT 退化为 |Pearson r|); `compute_cronbach_alpha` 跨 8 item α=(k/(k−1))(1−Σσ²_i/σ²_total); `permutation_null` 在 listwise-complete 子样本(观测与 null 同域; len(sub)<4 则跳过)上对每列洗牌 1000 次(seed=42)算 HTMT 上限 null 分布, 报 obs_htmt_max、perm_htmt_max_p95、p_empirical、n_listwise、note(披露行置换未处理 bank 聚类); `_offdiag_max` 用 to_numpy(copy=True) 取非对角最大值(pandas 3.0 Copy-on-Write 下只读数组守卫, 修 P0 崩溃)。
- G-A1.2 准入门控: max off-diagonal HTMT < 0.85 → PASS, 否则 FAIL(need expert audit), 仅写日志。

**关键算法/公式**: Henseler-Ringle-Sarstedt(2015) HTMT 双 cutoff 0.85/0.90; Cronbach(1951) α; 1000-rep permutation(与 39d 基线对齐, Henseler 建议≥500)。预期 8×8 中 LM 6 子集互相及与 clarity/num_intensity 的 HTMT 均<0.85。

**输出**: 上列 CSV; α 与 G-A1.2 判定仅入日志。

**外部依赖/超时/确定性**: 纯 numpy/pandas, 无 sklearn/LLM/Embedding/_llm_cache.db; seed=42; DAG timeout=900(15 分钟, 仿 39d)。

**DAG 位置**: 验证阶段 39e(STAGES_VALIDATION), 上游=stage 40 panel(及上游 LM 子词典/clarity/num_intensity 列), 与 39d 测同一对 clarity/num_intensity 构念但扩到 LM 8 维, 互补不冲突; 服务 G-A1.2 准入门控与论文判别效度披露。

■ 白话说明

**这一步在做什么**: Loughran-McDonald(LM)金融词典会给文本贴六类标签——不确定性、诉讼、约束、强/弱语气情态、复杂度; 我们又加了"表述清晰度"和"数字密集度"两把尺子, 一共 8 个测度。这一步像检查"这 8 个测度是不是各管各的、有没有谁跟谁其实在量同一件事": 它把 8 个测度两两的相关排成一张 8×8 表, 看是不是都低于 0.85; 再用随机打乱一千次确认"这个判断不是碰巧"。

**为什么需要它**: 这 8 个词典/文本指标如果彼此高度相关, 同时塞进回归就是重复计量、会误导结论。这一步设了一个"准入门"(G-A1.2): 只有最大相关低于 0.85 才算通过, 否则要请专家人工复核。它和 39d 测的是同一对清晰度/数字密集度, 用同一套样本过滤, 保证两份报告互相可比。

**对最终面板/论文的影响**: 它不改主回归面板(只产几张 CSV 诊断表和日志), 但它是这些文本指标能否进论文的"安检"。安检通过, 论文可以放心声称这些词典测度各自独立有效; 不通过, 就得砍掉或合并冗余指标, 直接影响论文用哪些自变量、结论的可信度。
========================================================================
"""

from __future__ import annotations

import os
import platform
import sys
import time

import numpy as np
import pandas as pd

# sys.path 注入 (保证从任意 cwd 直跑本文件时可 import news_process 包)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import pct4, setup_logging, sig4  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "74_lm_discriminant_validity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 8 个 indicator 列 (三轨各一组; main spec 用 _ctx 与 P1 v3.6.0 G3 对齐)。
# v3.10.0: 6 个 LM 非情感子集 (原 4 + modal_weak/complexity) + clarity + num_intensity。
# compute_htmt_matrix/permutation_null/compute_cronbach_alpha 均 k-agnostic, 自动扩 8×8。
# 注: L&M 极性 (pos/neg) 走 loughran_tone 主轨, **不进** 39e — 此处全为单值非情感 frac/mean,
# 无 pos/neg 极性对, 故无需"极性对 HTMT≈1 例外"逻辑。
INDICATORS_CTX = [
    'uncert_frac_ctx',
    'litig_frac_ctx',
    'constr_frac_ctx',
    'modal_strong_frac_ctx',
    'modal_weak_frac_ctx',
    'complexity_frac_ctx',
    'mean_clarity_score_ctx',
    'mean_num_intensity_ctx',
]
INDICATORS_FULL = [
    'uncert_frac_full',
    'litig_frac_full',
    'constr_frac_full',
    'modal_strong_frac_full',
    'modal_weak_frac_full',
    'complexity_frac_full',
    'mean_clarity_score_full',
    'mean_num_intensity_full',
]
# 第三轨 ss = 银行+金科同句共现轨 (suffix _ss): 机械 _full→_ss swap (继承同 8 维度);
# ss 列尚未物化时下游 compute_htmt_matrix 缺列优雅跳过 (present < 2 → 空矩阵)。
INDICATORS_SS = [c.replace('_full', '_ss') for c in INDICATORS_FULL]

HTMT_STRICT = 0.85
HTMT_LENIENT = 0.90

# fix(omni-g-audit-family-05, 2026-06-11): 与 39d (lexical_discriminant_validity
# run_discriminant_validity min_n_articles=2, 修 R8-H2) 统一样本过滤口径.
MIN_N_ARTICLES = 2


def _apply_llm_valid_mask(panel: pd.DataFrame,
                          min_n_articles: int = MIN_N_ARTICLES) -> pd.DataFrame:
    """对 panel 施加 n_articles_llm_valid ≥ min_n_articles mask (与 39d 同口径).

    fix(omni-g-audit-family-05, 2026-06-11): 39d 与 39e 测同一对构念
    (clarity / num_intensity), 旧 39e 完全不 mask — 单篇文章 bank-year 的噪声
    测度进入 HTMT, 两份判别效度报告在不同样本上互不可比, 且 G-A1.2 门控
    (max HTMT < 0.85) 的判定样本与 39d 论文口径脱节. 现复用 39d 的过滤:
    优先 ``n_articles_llm_valid`` (判别效度测度建立在 LLM-valid 文章上),
    旧冻结 panel 缺该列则回退 ``n_articles``; 两列均缺 → 不过滤 (graceful).
    """
    mask_col = ('n_articles_llm_valid'
                if 'n_articles_llm_valid' in panel.columns else 'n_articles')
    if mask_col not in panel.columns:
        logger.warning(
            f"  39e mask: panel 缺 n_articles_llm_valid / n_articles 列, "
            f"不过滤 (与 39d 口径对齐失败, 结果与 39d 不可比)")
        return panel
    masked = panel.loc[panel[mask_col] >= min_n_articles].copy()
    logger.info(f"  39e: {mask_col} ≥ {min_n_articles} mask 后 {len(masked)} obs "
                f"(原 {len(panel)}; 与 39d R8-H2 口径统一)")
    return masked


def _offdiag_max(corr: pd.DataFrame) -> float:
    """对称矩阵的非对角最大值 (P0 修复 metric-audit 2026-06-02; CoW 安全).

    pandas 3.0 Copy-on-Write 下 DataFrame.values / corr().abs().values 返回**只读**
    数组, 此前 `np.fill_diagonal(df.values, np.nan)` 抛
    ``ValueError: assignment destination is read-only`` → stage 39e (默认启用的
    validation stage) 运行期崩溃. 改为在可写副本上置对角为 NaN 后取 nanmax,
    语义与旧 ``fill_diagonal + df.max().max()`` 完全一致 (off-diagonal 最大值).
    """
    arr = corr.to_numpy(copy=True)
    np.fill_diagonal(arr, np.nan)
    return float(np.nanmax(arr))


def compute_htmt_matrix(panel: pd.DataFrame, indicators: list[str]) -> pd.DataFrame:
    """k×k HTMT 矩阵 (Henseler et al. 2015 JAMS).

    HTMT(i, j) = corr(indicator_i, indicator_j) / sqrt(rel_i × rel_j),
    其中 rel_i 用 Cronbach α 估单维 reliability. 因 LM 子集 single-item,
    退化为 single-indicator HTMT = |corr(i, j)| / sqrt(1 × 1) = |corr|.

    Note:
        v3.5.1 stage 39d 已实现 multi-indicator HTMT 完整版; stage 39e 因
        LM 6 子集为 single-item, 用 abs(Pearson r) 作为 HTMT 简化估计.
        与 39d 互补不冲突.
    """
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        logger.warning(f"  indicators 列不足 2 列存在 ({present}); HTMT 跳过")
        return pd.DataFrame()
    corr = panel[present].corr().abs()
    return corr


def compute_cronbach_alpha(panel: pd.DataFrame, indicators: list[str]) -> float:
    """跨 8 个 indicator 的 Cronbach α (Cronbach 1951)。"""
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return float('nan')
    sub = panel[present].dropna()
    k = len(present)
    if len(sub) < 2:
        return float('nan')
    var_items = sub.var(axis=0).sum()
    var_total = sub.sum(axis=1).var()
    if var_total == 0:
        return float('nan')
    return (k / (k - 1)) * (1 - var_items / var_total)


def permutation_null(panel: pd.DataFrame, indicators: list[str],
                     n_perm: int = 1000, seed: int = 42) -> pd.DataFrame:
    """HTMT 的 permutation null 分布 (按列随机洗牌)。

    实现仿 stage 39c::permutation_null: 对每个 indicator 列独立随机置换 n_perm 次,
    统计 HTMT 上限的 null 分布 (当前为串行循环, 非 n_jobs 并行)。

    fix(omni-g-audit-family-05, 2026-06-11) 两处口径修正:
    (a) 旧实现对含 NaN 的全样本列直接 ``rng.permutation`` — NaN 随值一起洗牌,
        破坏列间缺失对齐 → null 的有效 pairwise n 缩水, |corr| null 分布偏宽
        (p95 偏高, 方向保守但口径失准). 现观测与置换统一在 listwise-complete
        子样本上进行 (缺失模式固定, 观测/null 同域).
    (b) 披露: 行置换假设观测行独立, 未处理面板 bank 聚类 (within-bank 序列
        相关下 null 可能偏窄) — 写入输出 ``note`` 字段.
    """
    rng = np.random.default_rng(seed)
    present = [c for c in indicators if c in panel.columns]
    if len(present) < 2:
        return pd.DataFrame()
    # fix(omni-g-audit-family-05): listwise-complete 子样本 — 观测与 null 同域
    sub = panel[present].dropna()
    if len(sub) < 4:
        logger.warning(
            f"  permutation_null: listwise-complete 样本不足 ({len(sub)} 行 < 4); 跳过")
        return pd.DataFrame()
    # 观测 HTMT 上限 (对角置 NaN 后取全矩阵最大值), 作为下方 permutation null 的对比基准.
    obs_htmt = compute_htmt_matrix(sub, present)
    if obs_htmt.empty:
        return pd.DataFrame()
    obs_max = _offdiag_max(obs_htmt)  # P0 修复: CoW 安全 (不写只读 .values)
    # Layer 8.1 (v2.3-followup-v2 第 17 轮 user-request): perm 100 stub → n_perm reps.
    # 与 stage 39c/39d v3.5.0/v3.5.1 1000-rep 基线对齐 (Henseler-Ringle-
    # Sarstedt 2015 JAMS 建议 ≥ 500; 项目 stage 39d 用 1000 seed=42).
    perm_max = []
    for _ in range(n_perm):
        shuffled = sub.apply(lambda c: rng.permutation(c.values))
        h = shuffled.corr().abs()
        perm_max.append(_offdiag_max(h))  # P0 修复: CoW 安全
    p_emp = float((np.array(perm_max) >= obs_max).mean())
    return pd.DataFrame([{
        'obs_htmt_max': obs_max,  # P0 修复: off-diag max (obs_htmt 不再 in-place 改)
        'perm_htmt_max_mean': float(np.mean(perm_max)),
        'perm_htmt_max_p95': float(np.percentile(perm_max, 95)),
        'p_empirical': p_emp,
        'n_perm': len(perm_max),
        'n_listwise': int(len(sub)),
        'note': (f'{n_perm} reps (与 stage 39d 1000-rep 基线对齐); seed={seed}; '
                 f'obs 与 null 同 listwise-complete 域 (n={len(sub)}); '
                 f'披露: 行置换未处理面板 bank 聚类 (within-bank 相关下 null 或偏窄)'),
    }])


def _log_environment_and_config(panel_path: str, eval_dir: str) -> None:
    """打印 ① 项目/环境 + ② 输入输出 + ③ 运行配置 + ④ 方法论依据 块 (日志富集 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、依据哪些方法学文献"一次性
    落进日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 / schema / 控制流 (golden-safe)。

    方法学引文按手册铁律仅 emit 已核验事实: 本阶段 Henseler-Ringle-Sarstedt (2015) JAMS、
    Cronbach (1951) Psychometrika 与置换检验锚点 Young (2019) QJE 三条经复核**已收录**于经
    核验参考文献注册表 (pool.json), emit 时**附**其 DOI 链接; 仅 Cohen (1960) EPM 尚未核验,
    故只 emit 作者-年-期刊卷(期):页, **不**附 DOI 链接 (避免伪造)。
    """
    try:
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (LM 8 维判别效度 / 验证轨 STAGES_VALIDATION; "
                    "DAG stage 39e)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "| 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · numpy={np.__version__} | pandas={pd.__version__}")
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "纯 numpy/pandas, 无 LLM·Embedding·sklearn·网络 ($0); seed=42 逐位可复现")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入 panel:  {panel_path}")
        logger.info(f"     · 输出目录:    {eval_dir}")
        logger.info("     · 输出 (三轨各一份, 仅 CSV 诊断表, 不落 parquet / 不进主面板):")
        logger.info("         74_lm_htmt_matrix_{ctx,full,ss}.csv   (8×8 HTMT 矩阵)")
        logger.info("         74_lm_permutation_{ctx,full,ss}.csv   (1000-rep permutation null 汇总)")

        logger.info("  ⚙ 运行配置")
        logger.info(f"     · HTMT 双 cutoff: strict={sig4(HTMT_STRICT)} / lenient={sig4(HTMT_LENIENT)} "
                    "(G-A1.2 准入门控以 strict 为界)")
        logger.info(f"     · 样本过滤: n_articles_llm_valid ≥ {MIN_N_ARTICLES:,d} "
                    "(缺该列回退 n_articles; 与 stage 39d R8-H2 口径统一)")
        logger.info(f"     · permutation: n_perm={1000:,d} reps | seed={42:,d} "
                    "(listwise-complete 子样本上逐列洗牌; Henseler 建议 ≥500)")
        logger.info(f"     · 三轨 indicator 集 (各 8 维): ctx={len(INDICATORS_CTX):,d} | "
                    f"full={len(INDICATORS_FULL):,d} | ss={len(INDICATORS_SS):,d} "
                    "(LM 6 子词典 frac + clarity + num_intensity)")

        logger.info("  📖 方法论依据 (本阶段核心构念/方法的学术出处)")
        # (2026-06-29 DOI 升级) Henseler 与 Cronbach 两条经复核已收录于本工作流『经核验参考
        # 文献注册表』(pool.json: 10.1007/s11747-014-0403-8 / 10.1007/bf02310555), 故补回各自
        # DOI 链接; 旧『三条均无 DOI』免责声明随之收窄到唯一仍未核验的 Cohen 1960。
        logger.info("     · HTMT 判别效度判据: Henseler, J., Ringle, C. M., & Sarstedt, M. (2015). "
                    "A new criterion for assessing discriminant validity in variance-based "
                    "structural equation modeling. Journal of the Academy of Marketing Science, "
                    "43(1), 115-135. https://doi.org/10.1007/s11747-014-0403-8")
        logger.info("       → 异质-同质相关比 (HTMT) 双 cutoff 0.85 strict / 0.90 lenient; "
                    "低=两构念各测各的、未重复造轮子")
        logger.info("     · Cronbach α (内部一致性): Cronbach, L. J. (1951). Coefficient alpha "
                    "and the internal structure of tests. Psychometrika, 16(3), 297-334. "
                    "https://doi.org/10.1007/bf02310555")
        logger.info("       → α=(k/(k-1))(1-Σσ²_i/σ²_total); 8 维本应低耦合, α 高反提示构念不纯")
        # (2026-06-29 新增) permutation_null() 的 1000-rep 逐列洗牌经验 p 值 = Fisher 随机化
        # 推断 (randomization inference) 的实现; Young (2019 QJE) 是其规范锚点 (白话: 把"观测
        # 相关能否由随机重排复现"当作显著性判据, 不依赖参数分布假设)。
        logger.info("     · 置换/随机化推断 (permutation_null 经验 p 值): Young, A. (2019). "
                    "Channeling Fisher: Randomization tests and the statistical insignificance of "
                    "seemingly significant experimental results. The Quarterly Journal of "
                    "Economics, 134(2), 557-598. https://doi.org/10.1093/qje/qjy029")
        logger.info("       → 对 HTMT 上限统计量逐列洗牌 1000 次得经验 null, p_empirical 即随机化"
                    "检验 p 值 (无参数分布假设; seed=42 逐位可复现)")
        logger.info("     · 名义一致性系数 (κ 谱系): Cohen, J. (1960). "
                    "Educational and Psychological Measurement, 20(1), 37-46.")
        logger.info("       (注: 仅上述 Cohen (1960) 一条尚不在本工作流『经核验参考文献注册表』内, "
                    "故按手册铁律仅 emit 作者-年-期刊卷(期):页, 不附 DOI 链接以避免伪造)")
        logger.info("     · 近期补充 (经 Crossref 核验注册表; 偏 2023-2026, 附 DOI):")
        logger.info("       - 词典法度量的当代背书: Barbaglia, L., Consoli, S., Manzan, S., "
                    "Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic "
                    "text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. "
                    "https://doi.org/10.1111/ecin.13264")
        logger.info("         (白话: 2025 证据表明领域词典法在经济新闻中仍可与机器学习竞争, "
                    "为本阶段所验证的 LM 6 子词典 frac 测度在 LLM 时代保留词典轨提供外部背书)")
        logger.info("       - 信度/一致性系数族的现代实现: Marzi, G., Balzano, M., & Marchiori, D. "
                    "(2024). K-Alpha Calculator–Krippendorff's Alpha Calculator: A user-friendly "
                    "tool for computing Krippendorff's Alpha inter-rater reliability coefficient. "
                    "MethodsX, 12, 102545. https://doi.org/10.1016/j.mex.2023.102545")
        logger.info("         (白话: Krippendorff α 是与本阶段所算 Cronbach α / κ 谱系同族的"
                    "信度/一致性系数, 其 2024 现代实现工具锚定一致性度量的当代计算口径)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    stage_start = time.time()
    logger.info("=" * 72)
    logger.info("阶段 39e: LM 词典 8 维判别效度 (v3.5.2 PR #4; Henseler-Ringle-Sarstedt 2015 HTMT)")
    logger.info("=" * 72)
    logger.info("【功能】给 8 个非情感文本测度 (LM 6 子词典频率 uncert/litig/constr/modal_strong/modal_weak/complexity +")
    logger.info("        清晰度 mean_clarity_score + 数字密集度 mean_num_intensity) 做判别效度安检:")
    logger.info("        把两两相关排成 8×8 表, 看它们是否各测各的、有没有谁跟谁其实在量同一件事。")
    logger.info("        产出 (三轨各一份): 74_lm_htmt_matrix_{ctx,full,ss}.csv (8×8 HTMT 矩阵) +")
    logger.info("        74_lm_permutation_{ctx,full,ss}.csv (1000-rep permutation null 汇总)。")
    logger.info("【方法】单 item HTMT 退化为 |Pearson r|; Cronbach α=(k/(k-1))(1-Σσ²_i/σ²_total);")
    logger.info("        permutation null 在 listwise-complete 子样本上对每列洗牌 1000 次 (seed=42);")
    logger.info("        G-A1.2 准入门控: max off-diagonal HTMT < 0.85(strict) → PASS, 否则 FAIL(需专家复核)。")
    logger.info("        样本口径与 39d 统一 (n_articles_llm_valid ≥ 2), 两份判别效度报告同样本可比。")
    logger.info("【判读】HTMT 越低越好 (越低=两测度越独立); 8×8 全 < 0.85 即判别效度通过、8 个测度可独立进回归;")
    logger.info("        某对 ≥ 0.85 = 疑似重复计量, 需砍掉或合并冗余指标。permutation p_empirical 越大")
    logger.info("        说明观测 HTMT 越接近随机噪声 (相关弱、判别效度越强)。Cronbach α 此处仅供参考")
    logger.info("        (8 维本就该低耦合, α 高反而坏 — 与传统'量表内一致性高=好'方向相反)。")
    logger.info("【确定性】纯 numpy/pandas, 无 LLM/Embedding/sklearn; seed=42; 逐位可复现。")
    logger.info("=" * 72)

    output_dir = CONFIG['paths']['output_dir']
    eval_dir = os.path.join(output_dir, 'eval_reports')
    os.makedirs(eval_dir, exist_ok=True)

    # fix(stage-input-config-wiring, 2026-06-25): panel 名经 config 单一真值解析
    # (output_40_panel_yearly; 键存在值=默认 → golden-safe), 替代硬编码字面量。
    panel_path = os.path.join(output_dir, CONFIG['filenames'].get('output_40_panel_yearly', '40_panel_yearly.parquet'))

    # 项目/环境 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24; golden-safe)
    _log_environment_and_config(panel_path, eval_dir)

    if not os.path.exists(panel_path):
        logger.error(f"  panel 未找到: {panel_path}; 跳过 39e")
        sys.exit(0)

    _t_load = time.time()
    panel = pd.read_parquet(panel_path)
    logger.info(f"  panel: {len(panel):,d} 行 × {len(panel.columns):,d} 列")

    # fix(omni-g-audit-family-05, 2026-06-11): 与 39d 统一 n_articles_llm_valid ≥ 2
    # 样本过滤 (HTMT / Cronbach α / permutation 全部在同一过滤后样本上计算)
    panel = _apply_llm_valid_mask(panel)
    # per-phase 墙钟计时 (日志富集; 纯日志, 不影响产物)
    _phase_durations: dict[str, float] = {'①加载panel+样本过滤': time.time() - _t_load}

    # 三轨各跑一次 (full / ctx / ss; 与 v3.5.1 stage 39d 对齐)
    # ss = 银行+金科同句共现轨; INDICATORS_SS 列尚未物化时 compute_htmt_matrix
    # 内部 present < 2 → 返回空矩阵, 本轮 continue 优雅跳过 (镜像 ctx/full 缺列守卫)。
    # _track_summaries: 仅供下方【结果分析】打印的本地累积器, 不回写 df / 任何产物。
    _track_summaries = []
    _skipped_tracks = []
    n_obs_masked = len(panel)
    for suffix, indicators in (
        ('ctx', INDICATORS_CTX),
        ('full', INDICATORS_FULL),
        ('ss', INDICATORS_SS),
    ):
        logger.info(f"  ── 轨道 {suffix} ──")
        # (IO provenance 2026-06-29) 算 HTMT 前先把本轨 8 维 indicator 的"入表/缺失"明细落日志:
        # compute_htmt_matrix 内部对缺列静默丢弃 (仅 present<2 时才 warn), 读者无从得知究竟哪几个
        # 构念真正进了矩阵。此处用与函数体内**完全相同**的成员判定 (纯读 panel.columns, 不改数据),
        # 让"优雅跳过缺列"的降级行为在轨边界可审计 (golden-safe)。
        try:
            _present = [c for c in indicators if c in panel.columns]
            _missing = [c for c in indicators if c not in panel.columns]
            logger.info(
                f"    schema: present {len(_present):,d}/{len(indicators):,d} "
                f"→ {_present}; missing {len(_missing):,d} → {_missing or '(无)'}")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"    [schema provenance] 打印异常, 跳过(不影响产物): {_e}")
        _t_track = time.time()
        htmt = compute_htmt_matrix(panel, indicators)
        if htmt.empty:
            logger.warning(f"  {suffix}: HTMT 跳过 (indicator 列缺失)")
            _skipped_tracks.append(suffix)
            _phase_durations[f'②轨{suffix}(跳过)'] = time.time() - _t_track
            continue
        htmt_path = os.path.join(eval_dir, f'74_lm_htmt_matrix_{suffix}.csv')
        htmt.to_csv(htmt_path)
        logger.info(f"    HTMT matrix → {htmt_path}")

        alpha = compute_cronbach_alpha(panel, indicators)
        logger.info(f"    Cronbach α = {sig4(alpha)}")

        perm = permutation_null(panel, indicators)
        if not perm.empty:
            perm_path = os.path.join(eval_dir, f'74_lm_permutation_{suffix}.csv')
            perm.to_csv(perm_path, index=False)
            logger.info(f"    Permutation → {perm_path}")

        # G-A1.2 准入门控判定
        max_htmt = _offdiag_max(htmt)  # P0 修复: CoW 安全
        logger.info(
            f"    G-A1.2 判定: max HTMT = {sig4(max_htmt)} "
            f"({'PASS' if max_htmt < HTMT_STRICT else 'FAIL (need expert audit)'})"
        )
        # (result distribution 2026-06-29) 纯读已算出的 htmt 矩阵, 把"哪一对构念顶到 max_htmt"
        # 与 off-diagonal 相关谱 (mean/median/min) 落日志: 仅标量 max 入日志时审稿人无从得知是哪
        # 两个测度在驱动 FAIL。argmax pair 与 spread 正是一张判别效度表应报的结果统计量。纯读 +
        # try/except 兜底, 任何异常只 warning, 不回写矩阵 / 不改产物 (golden-safe)。
        try:
            _off = htmt.where(~np.eye(htmt.shape[0], dtype=bool))  # 对角置 NaN 的只读副本
            _stacked = _off.stack()  # MultiIndex (行 indicator, 列 indicator) → |corr|; 默认丢 NaN
            if not _stacked.empty:
                _i_max, _j_max = _stacked.idxmax()
                logger.info(
                    f"    最大 off-diag HTMT 对: 「{_i_max}」×「{_j_max}」= {sig4(_stacked.max())} "
                    f"(该对最接近冗余; FAIL 时即此对触门)")
                logger.info(
                    f"    off-diag HTMT 谱: mean={sig4(_stacked.mean())} / "
                    f"median={sig4(_stacked.median())} / min={sig4(_stacked.min())} "
                    f"(n_pairs={_stacked.shape[0] // 2:,d} 个无序构念对; 越低=判别效度越强)")
        except Exception as _e:  # noqa: BLE001
            logger.warning(f"    [HTMT 谱] 诊断打印异常, 跳过(不影响产物): {_e}")
        # 记录本轨汇总供【结果分析】(纯日志, 不影响产物)
        _track_summaries.append({
            'suffix': suffix,
            'n_items': htmt.shape[0],
            'max_htmt': max_htmt,
            'alpha': alpha,
            'p_emp': (None if perm.empty else float(perm['p_empirical'].iloc[0])),
            'p95': (None if perm.empty else float(perm['perm_htmt_max_p95'].iloc[0])),
            'n_listwise': (None if perm.empty else int(perm['n_listwise'].iloc[0])),
        })
        _phase_durations[f'②轨{suffix}(HTMT+α+1000置换)'] = time.time() - _t_track

    # ── 【结果分析】(纯日志增量; 引用变量均在作用域内) ──────────────────
    # crash-guard (硬化 A): 整块【结果分析】纯读 _track_summaries / n_obs_masked 算指标,
    # 且所有 CSV 已在上方循环内 to_csv 落盘完毕; 此处再包 try/except 兜底, 任何诊断
    # 计算异常都只 warning 跳过, 绝不冒泡使阶段崩溃丢产物 (确保 golden-safe)。
    try:
        logger.info("-" * 72)
        logger.info("【结果分析】LM 8 维判别效度安检结果逐轨解读 (主 spec 用 ctx 轨):")
        logger.info(f"  样本: mask 后 {n_obs_masked:,d} 个 bank-year 单元参与判别效度计算。")
        if _track_summaries:
            for s in _track_summaries:
                mh = s['max_htmt']
                # NaN-guard (硬化 B): max_htmt 为 NaN (该轨全 NaN / 方差退化 → corr 全 NaN
                # → nanmax 返回 nan) 时, 不能落进 < 阈值的方向 ternary (nan 比较恒 False
                # → 会误判成 FAIL), 走独立"无有效数据"分支。
                if mh != mh:  # NaN (NaN != NaN)
                    logger.info(
                        f"  [{s['suffix']:>4}] {s['n_items']} 维: max off-diag HTMT = NaN "
                        f"→ 该轨无有效数据 (列存在但全 NaN / 方差退化), 判别效度不可估, 跳过判读。")
                else:
                    # verdict 与上方 G-A1.2 二分门控 (max<strict → PASS, 否则 FAIL) 显式对齐:
                    # canonical 门控以 strict(0.85) 为界, [strict,lenient) 区间门控已判 FAIL,
                    # 仅按 Henseler-Ringle-Sarstedt(2015) lenient(0.90) 线尚属临界 (仍需专家复核),
                    # 不把门控未过的指标软化为 "borderline 可放行"。
                    verdict = (
                        f'PASS(G-A1.2 门控通过, max<strict={sig4(HTMT_STRICT)})' if mh < HTMT_STRICT
                        else (
                            f'G-A1.2 门控判 FAIL — max≥strict({sig4(HTMT_STRICT)})未达; '
                            f'按 Henseler lenient({sig4(HTMT_LENIENT)})尚属临界 '
                            f'({sig4(HTMT_STRICT)}≤HTMT<{sig4(HTMT_LENIENT)}), 仍需专家复核'
                            if mh < HTMT_LENIENT
                            else f'FAIL(疑似重复计量, max≥lenient={sig4(HTMT_LENIENT)}, 需专家复核)'))
                    logger.info(
                        f"  [{s['suffix']:>4}] {s['n_items']} 维: max off-diag HTMT = "
                        f"{sig4(mh)} (阈值 strict={sig4(HTMT_STRICT)} / "
                        f"lenient={sig4(HTMT_LENIENT)}) → {verdict}")
                    if mh >= HTMT_STRICT:
                        logger.warning(
                            f"  [{s['suffix']}] 最大 HTMT ≥ {sig4(HTMT_STRICT)}: 8 个测度中存在疑似冗余对, "
                            f"该轨这些词典/文本指标不应同时进回归 (论文需砍掉或合并)。")
                # Cronbach α 反向判读: 8 维本应低耦合, α 高反而提示构念不纯
                if s['alpha'] == s['alpha']:  # 非 NaN (NaN != NaN)
                    a_read = ('良性(8 维低耦合, 符合判别效度预期)' if s['alpha'] < 0.7
                              else '偏高(8 维内部一致性高 → 可能在量同一构念, 与判别效度方向相悖, 留意)')
                    logger.info(f"        Cronbach α = {sig4(s['alpha'])} → {a_read}")
                else:
                    logger.info("        Cronbach α = NaN (present 列不足或方差退化, 不可估)")
                # permutation null 判读: p_empirical 越大越说明观测 HTMT 接近随机噪声
                if s['p_emp'] is not None:
                    p_read = ('观测 HTMT 弱于/接近随机洗牌 null, 相关非系统性 (判别效度强)'
                              if s['p_emp'] >= 0.05
                              else '观测 HTMT 显著高于洗牌 null (p<0.05), 该轨指标对存在系统性相关')
                    logger.info(
                        f"        permutation: p_empirical = {sig4(s['p_emp'])}, "
                        f"null p95 = {sig4(s['p95'])}, "
                        f"n_listwise = {s['n_listwise']:,d} → {p_read}")
                    if s['n_listwise'] is not None and s['n_listwise'] < 30:
                        logger.warning(
                            f"        [{s['suffix']}] listwise-complete 样本仅 {s['n_listwise']:,d} 行: "
                            f"permutation null 自由度低, p 值不稳, 仅供参考。")
                else:
                    logger.info("        permutation: 跳过 (listwise-complete 样本 < 4 行)")
        else:
            logger.warning("  全部三轨均跳过 (无任一轨 HTMT 可算); 见下方依赖缺失提示。")
        if _skipped_tracks:
            logger.warning(
                f"  优雅降级: 轨道 {_skipped_tracks} indicator 列缺失而跳过 "
                f"(ss 轨首跑前列未物化属预期; full/ctx 缺列说明上游 LM 子词典/clarity/"
                f"num_intensity 列未落盘, 须先跑 stage 14/15/22 与 panel 重生)。")
        # 小样本警告 (盘面 T=2 → bank-year 单元有限, HTMT/permutation 自由度低)
        if n_obs_masked < 50:
            logger.info(
                f"  小样本提示: 当前仅 {n_obs_masked:,d} 个 bank-year 单元 (盘面 T=2 demo), "
                f"HTMT 矩阵与 permutation null 自由度低, 此结果仅验证管道正确性; "
                f"判别效度结论以全量 17M / T=18 实测为准。")
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ── ⏱ 阶段计时汇总 (各子阶段墙钟耗时; 纯日志增量, golden-safe) ──────────
    try:
        _total = time.time() - stage_start
        logger.info("  ⏱ 阶段计时汇总 (墙钟秒)")
        for _name, _dur in _phase_durations.items():
            _share = (_dur / _total) if _total > 0 else 0.0
            logger.info(f"     · {_name}: {sig4(_dur)} s ({pct4(_share)})")
        logger.info(f"     · 合计: {sig4(_total)} s")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  [阶段计时] 汇总打印异常, 跳过(不影响产物): {_e}")

    logger.info(f"  耗时: {sig4(time.time() - stage_start)} s")


if __name__ == '__main__':
    main()
