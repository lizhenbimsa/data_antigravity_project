"""news_process.pipeline.text.article_sbert — stage 30a article-level SBERT 持久化.

v3.7.0 PR #9 — D 组前置. 把 stage 30 内部计算后即丢的 article-level SBERT
embeddings 持久化, 让 D1 (BERTopic) / D2 (staleness) / D3 (Krippendorff α)
能直接复用, 避免 ×3 重新编码 (节省 ~12-15 h 计算).

学术依据
--------
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and
business cycles. Review of Financial Studies, 37(3), 887-936.
→ 标题 + 首段 300 字策略 (避免 SBERT 512-token 截断丢尾段)

设计决策
--------
1. **SBERT 模型**: ``shibing624/text2vec-base-chinese`` (与 stage 30 / 15 /
   strategic_diff 4 callsite 完全一致, 零下载 + 零双轨配置漂移)
2. **输入策略**: 标题 + 首段 300 字 (实际新闻中位 800 字 ≈ 1200 token, SBERT
   max_seq_len=512 截断会丢失末段)
3. **双轨**: '内容' (full 轨, 标题经 Bybee 截断单独前置) + content_ctx 各编码一次 (与 v3.5.1 真双轨对齐)
4. **存储**: parquet (article_id, target_bank, year, emb_full[768], emb_ctx[768])
   预估 400k × 768 × 4 byte × 2 轨 = ~2.5 GB

D-0 实测项
----------
- HF cache 是否含 shibing624/text2vec-base-chinese (validate via SentenceTransformer init)
- GPU vs CPU 速度 (项目本机有 CUDA 时 < 2 h, CPU 4-6 h)

stub 说明
---------
模块代码完整可跑, 但实际 4-6 h 编码需用户手动触发:
    python news_process/30a_article_sbert.py
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

import numpy as np
import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "30a_article_sbert"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 与 config/features.yaml::embedding.model 单源对齐
_SBERT_MODEL_ID = CONFIG.get('embedding', {}).get(
    'model', 'shibing624/text2vec-base-chinese'
)

# Bybee 2024 风格 "标题 + 首段 300 字" 截断
TITLE_CHARS = 100
FIRST_PARA_CHARS = 300


def _truncate_for_sbert(title: str, content: str) -> str:
    """构造 SBERT 输入: 截短标题 + 首段 300 字; 避免 512 token 截断丢尾."""
    t = (title or '')[:TITLE_CHARS].strip()
    c = (content or '')[:FIRST_PARA_CHARS].strip()
    if t and c:
        return f"{t} | {c}"
    return t or c


def encode_articles(
    df: pd.DataFrame,
    content_col: str,
    title_col: Optional[str] = '标题',
    batch_size: int = 64,
) -> np.ndarray:
    """SBERT batch 编码; 输出 (N, 768) numpy 数组.

    Args:
        df: article-level DataFrame.
        content_col: '内容' or 'content_ctx'.
        title_col: '标题' (可选, 用于 Bybee 2024 截断策略).
        batch_size: 默认 64; GPU 可上调 128/256.

    Returns:
        (N, 768) float32 embeddings.
    """
    try:
        from sentence_transformers import SentenceTransformer  # noqa: E402
    except ImportError:
        logger.error("sentence-transformers 未安装; pip install sentence-transformers")
        raise

    logger.info(f"  加载 SBERT: {_SBERT_MODEL_ID}")
    model = SentenceTransformer(_SBERT_MODEL_ID)

    if title_col and title_col in df.columns:
        docs = [
            _truncate_for_sbert(t, c)
            for t, c in zip(df[title_col].fillna(''), df[content_col].fillna(''))
        ]
    else:
        docs = [
            (c or '')[:TITLE_CHARS + FIRST_PARA_CHARS]
            for c in df[content_col].fillna('')
        ]

    logger.info(f"  编码 {len(docs)} 篇文章, batch_size={batch_size}")
    t0 = time.time()
    embs = model.encode(
        docs,
        batch_size=batch_size,
        # 仅在交互式 (stderr 为 TTY) 时显示 tqdm 进度条; 在 run_pipeline_function
        # 子进程 (stderr 为管道) 下静默, 避免向 stderr 输出进度条噪声 (不影响编码结果)。
        show_progress_bar=sys.stderr.isatty(),
        normalize_embeddings=True,  # D2 cosine 友好 + D1 UMAP cosine metric 等价欧式
        convert_to_numpy=True,
    )
    logger.info(f"  编码完成: {time.time() - t0:.1f}s, shape={embs.shape}")
    return embs.astype(np.float32)


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 30a: Article-level SBERT 持久化 (v3.7.0 PR #9)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    if not os.path.exists(src_path):
        logger.error(f"  上游 stage 13 未跑: {src_path}")
        sys.exit(1)

    df = pd.read_parquet(src_path)
    logger.info(f"  article-level: {len(df)} 行")

    # ── 双轨编码 ──
    embs_full = encode_articles(df, content_col='内容', title_col='标题')
    embs_ctx = (
        encode_articles(df, content_col='content_ctx', title_col='标题')
        if 'content_ctx' in df.columns
        else np.full_like(embs_full, np.nan)
    )

    # ── 持久化 ──
    out_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    out_df = pd.DataFrame({
        'article_id': df.index if 'article_id' not in df.columns else df['article_id'],
        'target_bank': df['target_bank'] if 'target_bank' in df.columns else pd.NA,
        'year': df['year'] if 'year' in df.columns else pd.NA,
        '日期': df['日期'] if '日期' in df.columns else pd.NA,
        'emb_full': list(embs_full),   # list of 1D arrays (parquet-compatible)
        'emb_ctx': list(embs_ctx),
    })
    out_df.to_parquet(out_path, index=False)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    logger.info(f"  输出: {out_path} ({size_mb:.1f} MB)")
    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
