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
- **单轨 (full only)**: 套话集口径在 ctx/ss 子窗口意义弱, ctx/ss 延后 (by-design,
  镜像 semantic_staleness_ss DEFER 先例); 列名 boilerplate_phrase_ratio_full。
- **确定性**: CountVectorizer 固定参数 + sklearn 内部 vocab 字典序 → 无 HASHSEED 依赖。
- **SAFE**: 套话集为空 (无 n-gram ≥ 阈值) → 全 nan + loud WARNING (镜像 FINTECH_AC=None,
  绝不静默清空); 空/哨兵/退化(实字< n-gram 下界)文本 → nan (_clean 守卫)。
- **analyzer='char_wb'**: 实测中文上与 analyzer='char' corr≈0.99 (边界空格影响可忽略, 真盘
  最短文 133 字不触退化边界); 保留 char_wb 与 herd_decay 范式一致。
- **⚠ 生产 T=18 OOM 风险 (code review 2026-06-20 P1)**: 当前为**单遍全语料 fit_transform**,
  vocab dict 随唯一 4-6gram 近线性膨胀 (实测 847 文→2.4M n-gram≈231MB); T=18 gated 子集
  (数十万~百万篇) 会 OOM。**本机 T=2 可行**, 生产前**必须改造**为分块/限词表二遍:
  第一遍流式累加 DF (或 HashingVectorizer/min_df) 得套话集, 第二遍 CountVectorizer(vocabulary=
  套话集) 只对小子词表二次扫描算逐文命中。`_MAX_SAFE_DOCS` 守卫在超规模时 loud WARNING。
  (旧 docstring "分块防 OOM" 系**未兑现的承诺**, 已订正为如上实况 + TODO。)
- **小语料饱和**: n_docs < 1/阈值 时任意 DF≥1 的 n-gram 都满足 → 套话集=全词表 → 比率饱和≈1.0
  不可解释 (与 T 无关, 任意极小 stage-22 子集皆然); `compute_boilerplate_ratios` loud WARNING。
"""
from __future__ import annotations

import logging
import math
import re

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# 套话判据: n-gram 出现在 ≥ 此比例的文档中即视为"跨文档套话"。0.10 = 出现在 ≥10% 文档。
# (设计参数, 非文献硬值; 生产 T=18 可经稳健性网格微调。)
DF_RATIO_THRESHOLD = 0.10
NGRAM_RANGE = (4, 6)
OUT_COL = 'boilerplate_phrase_ratio_full'
_SENTINELS = frozenset({'', 'nan', 'none', '<na>'})
# 单遍全语料 fit 的安全规模上界; 超过则 loud WARNING (生产须改分块, 见 docstring P1)。
_MAX_SAFE_DOCS = 50_000
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


def compute_boilerplate_ratios(texts: list[str],
                               df_ratio_threshold: float = DF_RATIO_THRESHOLD,
                               ngram_range: tuple[int, int] = NGRAM_RANGE) -> list[float]:
    """语料级两遍, 返回每文 boilerplate 比率 (与 texts 等长)。空文/无套话集 → nan。"""
    from sklearn.feature_extraction.text import CountVectorizer

    cleaned = [_clean(t) for t in texts]
    nonempty_idx = [i for i, t in enumerate(cleaned) if t]
    out = [float('nan')] * len(texts)
    if not nonempty_idx:
        logger.warning("boilerplate: 全部文本为空/哨兵 → 全 nan (SAFE 降级)")
        return out

    docs = [cleaned[i] for i in nonempty_idx]
    n_docs = len(docs)
    # 生产规模 OOM 守卫 (code review 2026-06-20 P1): 单遍全语料 fit 的 vocab dict 随唯一
    # n-gram 近线性膨胀 (847 文≈2.4M n-gram/231MB); 超规模 → loud WARNING, 生产须改分块/限词表。
    if n_docs > _MAX_SAFE_DOCS:
        logger.warning(
            f"boilerplate: n_docs={n_docs} 超单遍安全规模 {_MAX_SAFE_DOCS} — char_wb"
            f"{ngram_range} 全词表单遍 fit 极可能 OOM; 生产 T=18 须改分块/限词表二遍 "
            f"(min_df/HashingVectorizer 求套话集 → CountVectorizer(vocabulary=套话集) 二扫), "
            f"见模块 docstring P1 TODO")
    # 小语料饱和守卫: n_docs < 1/阈值 → 套话集坍缩为全词表 → 比率饱和≈1.0 不可解释。
    _sat = math.ceil(1 / df_ratio_threshold) if df_ratio_threshold > 0 else 0
    if n_docs < _sat:
        logger.warning(
            f"boilerplate: n_docs={n_docs} < 1/阈值={_sat} → 套话集坍缩为全词表, "
            f"比率饱和≈1.0 不可解释 (小样本退化, 与 T 无关; 须更大语料方可解读)")
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
            f"boilerplate: 无 n-gram 达 DF≥{df_ratio_threshold:.0%} (套话集为空, "
            f"n_docs={n_docs}) → 全 nan (SAFE 降级, 绝不静默清空)")
        return out
    # vocabulary 固定序 (sorted by ngram 字面) — 防 HASHSEED 漂移; mask 已按列序故确定。
    logger.info(
        f"boilerplate: 套话集 {n_boiler}/{X.shape[1]} 个 char_wb{ngram_range}-gram "
        f"(DF≥{df_ratio_threshold:.0%} of {n_docs} 文); 第二遍算逐文命中率")

    # 第二遍: 逐文 命中套话 n-gram 出现数 / 全部 n-gram 出现数 (occurrence-weighted)。
    total = np.asarray(X.sum(axis=1)).ravel().astype(float)
    boiler = np.asarray(X[:, boiler_mask].sum(axis=1)).ravel().astype(float)
    for k, i in enumerate(nonempty_idx):
        out[i] = round(boiler[k] / total[k], 6) if total[k] > 0 else float('nan')
    return out


def enrich_with_boilerplate(df: pd.DataFrame, text_col: str = 'content_full',
                            out_col: str = OUT_COL) -> pd.DataFrame:
    """在 df 上加单轨 boilerplate_phrase_ratio_full 列 (in-place 安全, 返回同 df)。

    缺 text_col → 加全 nan 列 + WARNING (graceful, 不阻断 stage 22)。"""
    if text_col not in df.columns:
        logger.warning(f"boilerplate: 缺文本列 {text_col} → {out_col} 全 nan (graceful)")
        df[out_col] = float('nan')
        return df
    ratios = compute_boilerplate_ratios(df[text_col].tolist())
    df[out_col] = ratios
    n_valid = sum(1 for v in ratios if not (isinstance(v, float) and math.isnan(v)))
    logger.info(f"boilerplate: {out_col} 派生完成 ({n_valid}/{len(ratios)} 非空, 单轨 full)")
    return df
