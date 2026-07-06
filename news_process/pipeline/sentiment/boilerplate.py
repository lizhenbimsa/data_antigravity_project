"""pipeline/sentiment/boilerplate.py — 跨文档套话比率 (boilerplate phrase ratio).

构念 (Lang-Stice-Lawrence 2015 JAE; Dyer-Lang-Stice-Lawrence 2017 JAE): 一篇报道里
"跨语料高频公式化短语"(套话, 如 "本报讯/记者报道/有限公司/股份制" 等)占其全部文本片段
的比例。与 within_doc_redundancy (篇内自重复) 正交, 与 surface_staleness (整篇相似度) 不同
(此处是"高频套话短语命中率"非"两篇相似度")。

**口径与铁律 (执行计划 NONPOLARITY_DIMENSIONS WS-B2)**:
- 语料级两遍: 第一遍统计 char_wb (4,6)-gram 的 document-frequency, DF/N ≥ 阈值的 n-gram
  = "套话集"; 第二遍逐文算 命中套话 n-gram 出现数 / 全部 n-gram 出现数。
- ⚠ 语料 = stage 22 输入 (21_tone_llms gated 子集, 非真全量) → 套话集建在该子集上,
  非 Lang-Stice-Lawrence 英文 10-K 真全量做法 (中文新闻落地, 概念同源, 如实披露)。
- **三轨 (2026-07-03, ROBUSTNESS_GAP_BACKFILL 计划 §4 WP-C)**: full = canonical headline,
  ctx/ss = 互为稳健性轨 (不分主次; 各轨独立建各自语料上的套话集)。列名
  boilerplate_phrase_ratio_{full,ctx,ss}。解释性限定 (原 by-design DEFER 的理由, 转为
  codebook 披露): 套话集口径在 ctx/ss 子窗口文本上信号较弱, ctx/ss 轨作稳健性对照解读。
  ⚠ 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。
  ⚠ 三轨逐轨顺序跑, 词表不叠加 → 峰值 = 单轨峰值。
  非嵌入族 (char n-gram DF 统计) → 无 `_lg` 孪生 (carve-out, 同 surface_staleness)。
- **确定性**: CountVectorizer 固定参数 (min_df=1/max_df=1.0/max_features=None, `_make_vectorizer`
  工厂 + 类型感知 assert 锁定) + sorted(boiler_set) 传 vocabulary → 无 HASHSEED 依赖; round(,6)。
- **SAFE**: 套话集为空 (无 n-gram ≥ 阈值) → 全 nan + loud WARNING (镜像 FINTECH_AC=None,
  绝不静默清空); 空/哨兵/退化(实字< n-gram 下界)文本 → nan (_clean 守卫)。
- **analyzer='char_wb'**: 实测中文上与 analyzer='char' corr≈0.99 (边界空格影响可忽略, 真盘
  最短文 133 字不触退化边界); 保留 char_wb 与 herd_decay 范式一致。
- **⚠ 生产 T=18 OOM 硬化 (执行计划 BOILERPLATE_CHUNKED_TWOPASS_OOM_HARDENING 2026-07-06)**:
  改造为 **exact two-pass** (字节等价单遍, golden 零漂移; 三轮对抗评审 + 实测确认):
  Pass1 分块流式**精确**累加全局 DF (`global_df` dict) + 顺带存逐文 total → 套话集;
  Pass2 用固定小 `boiler_set` 词表 `CountVectorizer(vocabulary=)` 逐块 transform 算命中。
  两驱动: 全量 CSR (随语料线性, 分块后不物化) + vocab dict (`global_df`, 亚线性但仍随 N 增长,
  是 binding 项)。**tier 1 (memory_tier='in_memory', 本模块已实现)** 消除 CSR 驱动 (较小项) + 建骨架;
  **tier 2 (disk-backed 精确 DF) DEFERRED** —— vocab-binding 生产可产性须生产机跑执行计划 §3-P0
  外推裁定后补 tier2 (memory_tier='disk'/'auto' 现 raise NotImplementedError, 绝不静默 OOM)。
  运行期硬闸: `global_df` 超 `df_dict_budget_hard` (Pass1 循环内周期检查) → SystemExit
  (拒绝跑优于被 OOM-killer 静默 SIGKILL)。旧单遍保留为 memory_tier='single_pass' 字节等价参照臂。
  ⚠ 严禁 HashingVectorizer/近似 sketch/块内 min_df 预剪 (碰撞/近似破 exact DF 与 golden)。
- **小语料饱和**: n_docs < 1/阈值 时任意 DF≥1 的 n-gram 都满足 → 套话集=全词表 → 比率饱和≈1.0
  不可解释 (与 T 无关, 任意极小 stage-22 子集皆然); `compute_boilerplate_ratios` loud WARNING。
"""
from __future__ import annotations

import logging
import math
import re

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

# 套话判据: n-gram 出现在 ≥ 此比例的文档中即视为"跨文档套话"。0.10 = 出现在 ≥10% 文档。
# (设计参数, 非文献硬值; 生产 T=18 可经稳健性网格微调。)
DF_RATIO_THRESHOLD = 0.10
NGRAM_RANGE = (4, 6)
OUT_COL = 'boilerplate_phrase_ratio_full'
# 三轨 (2026-07-03 §4 WP-C): full = headline (OUT_COL 保留为 canonical 锚, 勿改名);
# ctx/ss = 稳健性轨, 由 enrich_with_boilerplate 在 canonical 轨之外追加。
TRACKS = ('full', 'ctx', 'ss')
_SENTINELS = frozenset({'', 'nan', 'none', '<na>'})
# legacy 单遍臂 (memory_tier='single_pass') 的安全规模上界; 超过则 loud WARNING。
# ⚠ 保留供 legacy 字节等价参照臂消费 (勿删: 只要 test_boilerplate_chunked 存在即为受保护参照)。
_MAX_SAFE_DOCS = 50_000
# ── tier1 chunked exact two-pass 参数 (执行计划 2026-07-06; config/sentiment.yaml::boilerplate 可覆盖) ──
_DEFAULT_CHUNK_SIZE = 20_000        # 每块文档数; 纯性能参数, 不改输出 (字节等价)
_DEFAULT_TIER = 'in_memory'         # in_memory=tier1(已实现) / single_pass=legacy 参照臂 / disk|auto=DEFERRED→raise
_DEFAULT_BUDGET_WARN = 8_000_000    # global_df entry 软预算, 超则 loud WARNING (非兜底)
_DEFAULT_BUDGET_HARD = 40_000_000   # global_df entry 硬上限, 超则 SystemExit (Pass1 循环内); ⚠ 保守占位, 生产 P0 实测 per-entry 字节后按 128GB 反推校准
_VALID_TIERS = frozenset({'in_memory', 'single_pass', 'disk', 'auto'})
# 零宽/不可见字符 (str.strip() 不剥离 ​ 等 → 退化文本逃逸成伪值; code review 2026-06-20)。
_ZERO_WIDTH_RE = re.compile(r'[​‌‍⁠﻿]')
# 实字下界 = n-gram 最小长; 不足以产合法 (4,6)-gram 的退化文本 → nan (防 char_wb 边界伪值)。
_MIN_REAL_CHARS = NGRAM_RANGE[0]


def _clean(text) -> str:
    """返回喂给向量器的文本 (空/哨兵/退化 → '' → 上层记 nan)。

    ⚠ 保值铁律: 对**非退化**文本返回 `text.strip()` (与旧实现逐字节一致, golden 不漂);
    仅对"剔零宽+空白后实字 < _MIN_REAL_CHARS"的退化文本额外判 '' (真盘最短 133 字不触发)。
    退化判定在副本上做, 不改返回文本 → 真盘所有文档喂给向量器的输入与旧版完全相同。"""
    if not isinstance(text, str):
        return ''
    t = text.strip()
    if t.lower() in _SENTINELS:
        return ''
    # 退化判定 (副本): 剔零宽 + 各类空白后的"实字"数 < n-gram 下界 → '' (防 char_wb 边界伪值)
    real = _ZERO_WIDTH_RE.sub('', t)
    real = re.sub(r'\s|　', '', real)  # 半角/制表/全角空格
    if len(real) < _MIN_REAL_CHARS:
        return ''
    return t  # 非退化: 返回原 strip 文本 (不剔零宽), 保证与旧版逐字节一致


def _make_vectorizer(ngram_range: tuple[int, int] = NGRAM_RANGE, vocabulary=None):
    """单一 CountVectorizer 工厂 (Pass1/Pass2 共用), 类型感知锁死字节等价命门。

    ⚠ 不变量 I/II 仅在无语料级剪枝 (min_df=1/max_df=1.0/max_features=None) 时成立;
    工厂 + assert 把该隐性前提转为运行时硬约束 (执行计划 §2.6)。类型感知防 1==1.0 逃逸:
    min_df=1(int, 无剪枝) vs 1.0(float, 100%剪枝) 语义天壤但 ==1 同真。ngram_range 穿透形参
    (勿硬编码常量, 否则 compute 的 public ngram_range 沦为死参)。"""
    from sklearn.feature_extraction.text import CountVectorizer
    min_df, max_df, max_features = 1, 1.0, None
    assert type(min_df) is int and min_df == 1, "boilerplate: min_df 必须 int 1 (无剪枝); float 1.0=100%剪枝"
    assert isinstance(max_df, float) and not isinstance(max_df, bool) and max_df == 1.0, \
        "boilerplate: max_df 必须 float 1.0 (无剪枝)"
    assert max_features is None, "boilerplate: max_features 必须 None (无剪枝)"
    return CountVectorizer(analyzer='char_wb', ngram_range=ngram_range, lowercase=True,
                           min_df=min_df, max_df=max_df, max_features=max_features,
                           vocabulary=vocabulary)


def _coerce_int(v, default: int, name: str) -> int:
    """config 畸值兜底: None/非数值/bool → default + WARNING (优雅降级, 不裸 TypeError)。"""
    if isinstance(v, bool) or v is None:            # bool 是 int 子类, 显式排除防 True→1 静默
        logger.warning(f"boilerplate: {name}={v!r} 非法 → 回落默认 {default:,d}")
        return default
    try:
        return int(v)
    except (TypeError, ValueError, OverflowError):   # OverflowError: int(±inf) (Result R2 补齐)
        logger.warning(f"boilerplate: {name}={v!r} 无法转 int → 回落默认 {default:,d}")
        return default


def compute_boilerplate_ratios(texts: list[str],
                               df_ratio_threshold: float = DF_RATIO_THRESHOLD,
                               ngram_range: tuple[int, int] = NGRAM_RANGE,
                               *,
                               chunk_size: int = _DEFAULT_CHUNK_SIZE,
                               memory_tier: str = _DEFAULT_TIER,
                               df_dict_budget_warn: int = _DEFAULT_BUDGET_WARN,
                               df_dict_budget_hard: int = _DEFAULT_BUDGET_HARD) -> list[float]:
    """语料级 exact two-pass, 返回每文 boilerplate 比率 (与 texts 等长)。空文/无套话集 → nan。

    memory_tier: 'in_memory'=tier1 chunked (默认, 字节等价) / 'single_pass'=legacy 单遍参照臂
    / 'disk'|'auto'=tier2 DEFERRED (raise NotImplementedError)。畸值在入口 clamp (直调+enrich 双护)。"""
    # ── 入口 clamp (Round2 P2 + Result R1 P2: 直调与 enrich 注入两路径都受保护) ──
    # None/非数值 config 畸值 → 回落默认 + WARNING (优雅降级, 不裸 TypeError 崩 stage 22)。
    chunk_size = max(1, _coerce_int(chunk_size, _DEFAULT_CHUNK_SIZE, 'chunk_size'))
    df_dict_budget_warn = _coerce_int(df_dict_budget_warn, _DEFAULT_BUDGET_WARN, 'df_dict_budget_warn')
    df_dict_budget_hard = _coerce_int(df_dict_budget_hard, _DEFAULT_BUDGET_HARD, 'df_dict_budget_hard')
    if memory_tier not in _VALID_TIERS:
        logger.warning(f"boilerplate: 未知 memory_tier={memory_tier!r} → 'in_memory' (默认)")
        memory_tier = 'in_memory'
    if memory_tier in ('disk', 'auto'):          # tier2 DEFERRED: fail-loud, 绝不静默回落 tier1 跑到 OOM
        raise NotImplementedError(
            f"boilerplate: memory_tier={memory_tier!r} (tier2 disk-backed DF) DEFERRED 未实现; "
            f"请设 memory_tier='in_memory', 或到生产机跑执行计划 §3-P0 外推裁定后启用 tier2")

    cleaned = [_clean(t) for t in texts]
    nonempty_idx = [i for i, t in enumerate(cleaned) if t]
    out = [float('nan')] * len(texts)
    if not nonempty_idx:
        logger.warning("boilerplate: 全部文本为空/哨兵 → 全 nan (SAFE 降级)")
        return out

    docs = [cleaned[i] for i in nonempty_idx]
    n_docs = len(docs)
    # 小语料饱和守卫 (两臂共享): n_docs < 1/阈值 → 套话集坍缩为全词表 → 比率饱和≈1.0 不可解释。
    _sat = math.ceil(1 / df_ratio_threshold) if df_ratio_threshold > 0 else 0
    if n_docs < _sat:
        logger.warning(
            f"boilerplate: n_docs={n_docs} < 1/阈值={_sat} → 套话集坍缩为全词表, "
            f"比率饱和≈1.0 不可解释 (小样本退化, 与 T 无关; 须更大语料方可解读)")

    if memory_tier == 'single_pass':
        return _compute_single_pass_legacy(docs, nonempty_idx, out, n_docs,
                                           df_ratio_threshold, ngram_range)
    return _compute_chunked(docs, nonempty_idx, out, n_docs, df_ratio_threshold, ngram_range,
                            chunk_size, df_dict_budget_warn, df_dict_budget_hard)


def _compute_single_pass_legacy(docs, nonempty_idx, out, n_docs,
                                df_ratio_threshold, ngram_range) -> list[float]:
    """legacy 单遍全语料 fit_transform (memory_tier='single_pass' 参照臂)。

    ⚠ 冻结: 这是 chunked exact two-pass 的字节等价参照实现 (gate test_boilerplate_chunked 的
    A 臂)。只要该 gate 存在即禁改此函数逻辑 (改动会失去字节等价参照)。"""
    from sklearn.feature_extraction.text import CountVectorizer

    # 单遍全语料 fit 的 vocab dict 随唯一 n-gram 近线性膨胀 (847 文≈2.4M n-gram); 超规模 → loud WARNING。
    if n_docs > _MAX_SAFE_DOCS:
        logger.warning(
            f"boilerplate: n_docs={n_docs} 超 legacy 单遍安全规模 {_MAX_SAFE_DOCS} — char_wb"
            f"{ngram_range} 全词表单遍 fit 极可能 OOM; 生产 T=18 请改 memory_tier='in_memory' "
            f"(tier1 chunked exact two-pass), 见模块 docstring")
    try:
        vec = CountVectorizer(analyzer='char_wb', ngram_range=ngram_range)
        X = vec.fit_transform(docs)               # doc × ngram 计数 (CSR), 确定性
    except ValueError as e:                       # 空词表 (全停用/过短)
        logger.warning(f"boilerplate: CountVectorizer 空词表 → 全 nan (SAFE): {e}")
        return out

    # 第一遍: document-frequency → 套话集 (DF/N ≥ 阈值)。确定性: 纯计数 + 阈值比较。
    df_counts = np.asarray((X > 0).sum(axis=0)).ravel()
    boiler_mask = (df_counts / n_docs) >= df_ratio_threshold
    n_boiler = int(boiler_mask.sum())
    if n_boiler == 0:
        logger.warning(
            f"boilerplate: 无 n-gram 达 DF≥{pct4(df_ratio_threshold)} (套话集为空, "
            f"n_docs={n_docs:,d}) → 全 nan (SAFE 降级, 绝不静默清空)")
        return out
    logger.info(
        f"boilerplate: 套话集 {n_boiler:,d}/{X.shape[1]:,d} 个 char_wb{ngram_range}-gram "
        f"(占全词表 {pct4(n_boiler / X.shape[1]) if X.shape[1] else 'n/a'}, "
        f"DF≥{pct4(df_ratio_threshold)} of {n_docs:,d} 文); 第二遍算逐文命中率")

    # ── 构念效度: 套话集示例 + DF 占比谱 (log-only, 全程 discarded, 不参与第二遍计算) ──
    try:
        feats = vec.get_feature_names_out()             # 全词表 char_wb-gram 字面 (与列序一致)
        masked_pos = np.flatnonzero(boiler_mask)        # 套话 n-gram 在全词表中的列位
        topk = masked_pos[np.argsort(df_counts[masked_pos])[::-1][:10]]
        logger.info(
            f"  · 套话集 top-{min(10, n_boiler):,d} 高 DF char_wb-gram (按文档频率降序, "
            f"构念效度示例 — 这些跨文档高频公式化短语即被判为'套话'):")
        for rank, j in enumerate(topk, 1):
            phrase = feats[j]                           # repr 化以显形 char_wb 边界空格
            logger.info(
                f"     #{rank:>2d} {phrase!r:<16} DF={int(df_counts[j]):,d}/{n_docs:,d} "
                f"= {pct4(df_counts[j] / n_docs)}")
        sel = df_counts[boiler_mask] / n_docs
        logger.info(
            f"  · 套话集 DF 占比谱: [min={pct4(float(sel.min()))} "
            f"中位={pct4(float(np.median(sel)))} max={pct4(float(sel.max()))}] "
            f"(min 贴近阈值 {pct4(df_ratio_threshold)} → DF 截断起约束; "
            f"max 趋近 1.0 → 套话集含近乎全语料皆现的极高频公式化短语)")
    except Exception as e:  # noqa: BLE001 — 日志块绝不阻断派生
        logger.warning(f"boilerplate: 套话集示例/DF 谱打印失败 (忽略, 不影响派生): {e}")

    # 第二遍: 逐文 命中套话 n-gram 出现数 / 全部 n-gram 出现数 (occurrence-weighted)。
    total = np.asarray(X.sum(axis=1)).ravel().astype(float)
    boiler = np.asarray(X[:, boiler_mask].sum(axis=1)).ravel().astype(float)
    for k, i in enumerate(nonempty_idx):
        out[i] = round(boiler[k] / total[k], 6) if total[k] > 0 else float('nan')
    return out


def _compute_chunked(docs, nonempty_idx, out, n_docs, df_ratio_threshold, ngram_range,
                     chunk_size, df_dict_budget_warn, df_dict_budget_hard) -> list[float]:
    """tier1 chunked exact two-pass (memory_tier='in_memory', 默认)。

    与 legacy 单遍逐字节等价 (执行计划 §9 三不变量: DF 可加性 / total 逐文独立 / 分子同值;
    实测确认)。分块消除全量 CSR 物化 (较小驱动); global_df 词表仍驻 RAM (binding, 超硬闸则 fail-loud)。"""
    N = n_docs
    global_df: dict[str, int] = {}                # n-gram 字面(含 char_wb 边界空格) → 全局 DF
    per_doc_total = np.zeros(N, dtype=float)       # np.zeros(非 empty): 未写入位 fail-safe 0→nan (§2.1)
    _warned_soft = False
    # ── Pass 1: 流式精确全局 DF + 顺带存逐文 total (免 Pass2 重分词; 免物化全量 CSR) ──
    for start in range(0, N, chunk_size):
        stop = min(start + chunk_size, N)
        chunk = docs[start:stop]
        idx = np.arange(start, stop)               # 全局位置 (§2.1 chunks_with_index 契约)
        vec_c = _make_vectorizer(ngram_range=ngram_range)
        try:
            Xc = vec_c.fit_transform(chunk)        # 块内矩阵 (即弃)
        except ValueError:                         # 空词表块; _clean≥4 下不可达=死分支, 仍显式防御
            per_doc_total[idx] = 0.0               # → 逐文 total=0 → nan (belt-and-suspenders)
            continue
        feats = vec_c.get_feature_names_out()
        df_c = np.asarray((Xc > 0).sum(axis=0)).ravel()
        for j, ng in enumerate(feats):
            global_df[ng] = global_df.get(ng, 0) + int(df_c[j])   # 不变量 I: DF 可加
        per_doc_total[idx] = np.asarray(Xc.sum(axis=1)).ravel()   # 不变量 II: 块内行和 = 单遍行和
        if not _warned_soft and 0 < df_dict_budget_warn < len(global_df):
            logger.warning(
                f"boilerplate: global_df {len(global_df):,d} entry 超软预算 {df_dict_budget_warn:,d} "
                f"(仅告警, 非兜底; 生产超规模请跑 P0 裁定 tier2)")
            _warned_soft = True
        # ⚠ 运行期硬闸 IN-LOOP (Round2 P1): RAM 耗尽前抢先 fail-loud, 防 OOM-killer 静默 SIGKILL
        if 0 < df_dict_budget_hard < len(global_df):
            raise SystemExit(
                f"boilerplate: global_df {len(global_df)} entry 超硬上限 {df_dict_budget_hard}; "
                f"tier1 不可产, 到生产机跑执行计划 §3-P0 外推裁定 tier2 (DEFERRED)")

    if not global_df:                              # 全块空词表 (不可达); global_df 空 → SAFE 全 nan
        logger.warning("boilerplate: global_df 空 (全块空词表) → 全 nan (SAFE 降级)")
        return out

    # ── 套话集: DF/N ≥ 阈值 (不变量 I ⟹ 与单遍 boiler_mask 同集) ──
    boiler_set = [ng for ng, d in global_df.items() if d / N >= df_ratio_threshold]
    n_boiler = len(boiler_set)
    if n_boiler == 0:
        logger.warning(
            f"boilerplate: 无 n-gram 达 DF≥{pct4(df_ratio_threshold)} (套话集为空, "
            f"n_docs={N:,d}) → 全 nan (SAFE 降级, 绝不静默清空)")
        return out
    logger.info(
        f"boilerplate: 套话集 {n_boiler:,d}/{len(global_df):,d} 个 char_wb{ngram_range}-gram "
        f"(占全词表 {pct4(n_boiler / len(global_df))}, "
        f"DF≥{pct4(df_ratio_threshold)} of {N:,d} 文); 第二遍算逐文命中率")

    # ── 构念效度: top-k 高 DF 套话短语 + DF 占比谱 (log-only, discarded; §2.5 集合等价) ──
    # 从 global_df 复现; DF 谱数值由不变量 I 与单遍精确等; top-k 集合等价 (tie 序 log-only 不强求)。
    try:
        _sorted = sorted(boiler_set, key=lambda ng: (-global_df[ng], ng))   # DF 降序, tie 按字面 (确定)
        topk = _sorted[:10]
        logger.info(
            f"  · 套话集 top-{min(10, n_boiler):,d} 高 DF char_wb-gram (按文档频率降序, "
            f"构念效度示例 — 这些跨文档高频公式化短语即被判为'套话'):")
        for rank, ng in enumerate(topk, 1):
            logger.info(
                f"     #{rank:>2d} {ng!r:<16} DF={global_df[ng]:,d}/{N:,d} "
                f"= {pct4(global_df[ng] / N)}")
        sel = np.asarray([global_df[ng] / N for ng in boiler_set], dtype=float)
        logger.info(
            f"  · 套话集 DF 占比谱: [min={pct4(float(sel.min()))} "
            f"中位={pct4(float(np.median(sel)))} max={pct4(float(sel.max()))}] "
            f"(min 贴近阈值 {pct4(df_ratio_threshold)} → DF 截断起约束; "
            f"max 趋近 1.0 → 套话集含近乎全语料皆现的极高频公式化短语)")
    except Exception as e:  # noqa: BLE001 — 日志块绝不阻断派生
        logger.warning(f"boilerplate: 套话集示例/DF 谱打印失败 (忽略, 不影响派生): {e}")

    # ── Pass 2: 流式逐文命中 (固定小 boiler_set 词表, 内存恒有界; 仅一次 transform/块) ──
    vec_boiler = _make_vectorizer(ngram_range=ngram_range, vocabulary=sorted(boiler_set))
    for start in range(0, N, chunk_size):
        stop = min(start + chunk_size, N)
        chunk = docs[start:stop]
        idx = np.arange(start, stop)
        boiler_c = np.asarray(vec_boiler.transform(chunk).sum(axis=1)).ravel().astype(float)
        for k in range(len(idx)):
            i_global = int(idx[k])
            t = per_doc_total[i_global]
            out[nonempty_idx[i_global]] = round(boiler_c[k] / t, 6) if t > 0 else float('nan')
    return out


def enrich_with_boilerplate(df: pd.DataFrame, text_col: str = 'content_full',
                            out_col: str = OUT_COL) -> pd.DataFrame:
    """在 df 上加三轨 boilerplate_phrase_ratio_{full,ctx,ss} 列 (in-place 安全, 返回同 df)。

    2026-07-03 §4 WP-C 三轨化: (text_col, out_col) 形参对 = canonical full 轨
    (向后兼容既有调用方的 '内容' 回退与自定义列名); ctx/ss 稳健轨固定读
    content_{ctx,ss} 写 boilerplate_phrase_ratio_{ctx,ss}, 各轨独立两遍建集。
    任一轨缺文本列 → 该轨全 nan 列 + WARNING (graceful, 不阻断 stage 22)。

    OOM 硬化 (2026-07-06): 读 config/sentiment.yaml::boilerplate (缺段→模块默认) 下传
    compute_boilerplate_ratios 的 chunk_size/memory_tier/budget kwargs (exact two-pass, 字节等价)。"""
    # ── config 接线 (执行计划 §2.3, Round1 P1: load_config 扁平根 dict, boilerplate 为顶层块) ──
    _bp_cfg = {}
    try:
        from news_process.core.config import load_config
        _bp_cfg = load_config().get('boilerplate', {}) or {}
    except Exception as e:  # noqa: BLE001 — config 不可用则全走模块默认 (test 零 config 直调不受影响)
        logger.warning(f"boilerplate: load_config 读取失败 → 走模块默认 kwargs: {e}")
    _bp_kwargs = {k: _bp_cfg[k] for k in
                  ('chunk_size', 'memory_tier', 'df_dict_budget_warn', 'df_dict_budget_hard')
                  if k in _bp_cfg}
    _tier = _bp_kwargs.get('memory_tier', _DEFAULT_TIER)
    _chunk = _bp_kwargs.get('chunk_size', _DEFAULT_CHUNK_SIZE)

    # ── 子步骤 banner (called-by-runner helper, 共享 stage 22 tone_words 日志) ──
    # 不重打 ENV/CONFIG (那是 stage 22 入口 main 的职责), 仅打本步骤名+方法依据+本步配置。
    try:
        logger.info("─" * 70)
        logger.info("[stage 22 子步骤] boilerplate_phrase_ratio_{full,ctx,ss} — 跨文档套话比率派生 (三轨)")
        logger.info(
            "  · 功能: 语料级 exact two-pass 统计 char_wb%s-gram 的 document-frequency, "
            "DF/N ≥ 阈值者为'套话集', 逐文算 命中套话 n-gram 数 / 全部 n-gram 数 (占比越高=越公式化套话)",
            NGRAM_RANGE)
        # 方法依据 (注册表中无对应 DOI → 仅作者-年散文, 不伪造 DOI; 见富集铁律 §4)。
        logger.info(
            "  · 方法依据: Lang & Stice-Lawrence (2015), JAE; "
            "Dyer, Lang & Stice-Lawrence (2017), JAE — 跨语料高频公式化短语(套话)占比构念 "
            "(DOI 不在经核验注册表, 仅注释保留, 未 emit)")
        logger.info(
            "  · 本步配置: text_col=%s | out_col=%s | DF 阈值=%s | n-gram=char_wb%s | "
            "memory_tier=%s | chunk_size=%s | 三轨(full=headline, ctx/ss=稳健轨, 2026-07-03) | "
            "$0 纯 CPU/确定性(exact two-pass, 字节等价, 无 HASHSEED 依赖)",
            text_col, out_col, pct4(DF_RATIO_THRESHOLD), NGRAM_RANGE, _tier, f"{int(_chunk):,d}")
    except Exception as e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"boilerplate: 子步骤 banner 打印失败 (忽略, 不影响派生): {e}")

    # 三轨槽位: canonical full 用形参对 (向后兼容 '内容' 回退/自定义列), ctx/ss 固定列名
    _slots = [(text_col, out_col)] + [
        (f'content_{trk}', f'boilerplate_phrase_ratio_{trk}') for trk in TRACKS[1:]
    ]
    ratios = None  # canonical 轨结果 (供下方结果分析块, 保持既有判读语义)
    for _tc, _oc in _slots:
        if _tc not in df.columns:
            logger.warning(f"boilerplate: 缺文本列 {_tc} → {_oc} 全 nan (graceful)")
            df[_oc] = float('nan')
            if _oc == out_col:
                ratios = [float('nan')] * len(df)
            continue
        _r = compute_boilerplate_ratios(df[_tc].tolist(), **_bp_kwargs)   # 三轨各自穿透 config kwargs
        df[_oc] = _r
        if _oc == out_col:
            ratios = _r
        _nv = sum(1 for v in _r if not (isinstance(v, float) and math.isnan(v)))
        logger.info(f"boilerplate: {_oc} 派生完成 ({_nv:,d}/{len(_r):,d} 非空)")
    n_valid = sum(1 for v in ratios if not (isinstance(v, float) and math.isnan(v)))

    # ── 结果分析 (阈值判读: 有效率 / 套话占比分布 / 饱和退化告警) ──
    try:
        n_total = len(ratios)
        valid_rate = n_valid / n_total if n_total else 0.0
        if valid_rate >= 0.95:
            vr_verdict = "✅ 好 (≥95% 文档可算套话比率)"
        elif valid_rate >= 0.80:
            vr_verdict = "⚠ 临界 (80–95% 有效, 留意空/哨兵/退化文本占比)"
        else:
            vr_verdict = "❌ 偏弱 (<80% 有效, 多数文本退化/无套话集, 谨慎解读)"
        logger.info(
            f"  ⑤ 有效率: {n_valid:,d}/{n_total:,d} = {pct4(valid_rate)} — {vr_verdict}")

        vals = np.asarray(
            [v for v in ratios if isinstance(v, float) and not math.isnan(v)],
            dtype=float)
        if vals.size:
            mean_r = float(vals.mean())
            std_r = float(vals.std())
            min_r, max_r = float(vals.min()), float(vals.max())
            # 饱和退化: 小语料下套话集坍缩为全词表 → 比率饱和≈1.0 不可解释。
            sat_frac = float((vals >= 0.99).mean())
            if mean_r >= 0.95 or sat_frac >= 0.50:
                dist_verdict = ("❌ 饱和退化 (套话比率≈1.0, 套话集疑坍缩为全词表; "
                                "小样本/stage-22 子集过小, 不可解释)")
            elif std_r < 1e-4:
                dist_verdict = "⚠ 临界 (零方差: 全文同值, 无区分度, 单列对回归无信息)"
            else:
                dist_verdict = "✅ 好 (比率分布有区分度, 套话集口径有效)"
            q25, q50, q75 = (float(x) for x in np.percentile(vals, [25, 50, 75]))
            logger.info(
                f"  ⑤ 套话比率分布: μ={sig4(mean_r)} σ={sig4(std_r)} "
                f"[min={sig4(min_r)}, max={sig4(max_r)}] 饱和(≥0.99)占比={pct4(sat_frac)} "
                f"— {dist_verdict}")
            logger.info(
                f"  ⑤ 套话比率分位: P25={sig4(q25)} 中位={sig4(q50)} P75={sig4(q75)} "
                f"(四分位距 IQR={sig4(q75 - q25)})")
        else:
            logger.warning(
                "  ⑤ 套话比率分布: 全部 nan (无有效值) — ❌ 套话集为空或全文退化, 该列下游无信息")
    except Exception as e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"boilerplate: 结果分析块打印失败 (忽略, 不影响派生): {e}")

    # ── 📖 方法论依据 (经核验注册表近期顶刊文献; 仅日志 emit, 不参与任何计算) ──
    try:
        logger.info("  📖 方法论依据 (boilerplate 跨文档套话比率构念的近期顶刊操作化):")
        logger.info(
            "     • Zhu, X., Li, J., & Wang, Y. (2024). Are risk disclosures in financial "
            "reports informative? A text mining-based perspective. Humanities and Social "
            "Sciences Communications, 11(1), 1653. https://doi.org/10.1057/s41599-024-04169-w")
        logger.info(
            "       (白话: 用文本挖掘评披露含量, 把套话/具体性/相似度操作化为度量, 与本模块同法。)")
        logger.info(
            "     • Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a "
            "machine is listening: Corporate disclosure in the age of AI. The Review of "
            "Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021")
        logger.info(
            "       (白话: 机器读者时代企业为算法调措辞, 正当化用 NLP 机器化测文本特征+策略性写作。)")
        logger.info(
            "     • Gietzmann, M., Grossetti, F., & Lewis, C. M. (2026). Investor distraction "
            "and multi-dimensional financial narrative. Review of Accounting Studies, 31(1), "
            "334–373. https://doi.org/10.1007/s11142-026-09950-7")
        logger.info(
            "       (白话: 多维叙事特征(可读性/数字/套话)联注意力, 套话多维度量的顶刊近用。)")
    except Exception as e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"boilerplate: 方法论依据块打印失败 (忽略, 不影响派生): {e}")
    return df
