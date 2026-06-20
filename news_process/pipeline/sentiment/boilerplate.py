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
- **确定性**: vocabulary 用 sorted 固定序 + CountVectorizer 固定参数 → 无 HASHSEED 依赖。
- **SAFE**: 套话集为空 (无 n-gram ≥ 阈值) → 全 nan + loud WARNING (镜像 FINTECH_AC=None,
  绝不静默清空); 空/哨兵文本 → nan。
- **T=2 退化**: 小样本下高频 4-6gram 几乎全跨"两年"共现 → 比率近饱和/近空, 本机仅验管道,
  功效须生产 T=18 (分块防 OOM)。
"""
from __future__ import annotations

import logging
import math

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# 套话判据: n-gram 出现在 ≥ 此比例的文档中即视为"跨文档套话"。0.10 = 出现在 ≥10% 文档。
# (设计参数, 非文献硬值; 生产 T=18 可经稳健性网格微调。)
DF_RATIO_THRESHOLD = 0.10
NGRAM_RANGE = (4, 6)
OUT_COL = 'boilerplate_phrase_ratio_full'
_SENTINELS = frozenset({'', 'nan', 'none', '<na>'})


def _clean(text) -> str:
    if not isinstance(text, str):
        return ''
    t = text.strip()
    return '' if t.lower() in _SENTINELS else t


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
