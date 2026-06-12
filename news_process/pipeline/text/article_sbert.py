"""news_process.pipeline.text.article_sbert — stage 30a article-level SBERT 持久化.

v3.7.0 PR #9 — D 组前置. 把 stage 30 内部计算后即丢的 article-level SBERT
embeddings 持久化, 让 D2 (staleness) / D3 (Krippendorff α)
能直接复用, 避免重复编码 (节省 ~12-15 h 计算).

学术依据
--------
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and
business cycles. Review of Financial Studies, 37(3), 887-936.
→ 标题 + 首段 300 字策略 (避免 SBERT 512-token 截断丢尾段)

设计决策
--------
1. **SBERT 模型**: 读 ``config/features.yaml::embedding_robustness.model``
   (默认 ``shibing624/text2vec-base-chinese``, 与 stage 15 / strategic_diff t2v 轨
   真单源, 零下载 + 零双轨配置漂移; fix(omni-g-embed-05, 2026-06-11) — 此前读
   不存在的 'embedding' 键恒走硬编码默认)
2. **输入策略**: 标题 + 首段 300 字 (实际新闻中位 800 字 ≈ 1200 token, SBERT
   max_seq_len=512 截断会丢失末段)
3. **双轨** (2026-06-08 dual-track parity): full 读 content_full / ctx 读 content_ctx
   (两者均由 stage 13 prepend 标题【恰好一次】), 编码时 title_col=None 关闭二次前置 →
   两轨同型构造、标题各一次 (修 ctx 标题×2 反向病根); 仅输入文本范围不同 (全文 vs 实体
   窗口)。缺 content_full 时回退裸 '内容'+'标题' (走 _truncate_for_sbert Bybee 前置, 标题一次)
4. **存储**: parquet (article_id, target_bank, year, emb_full[768], emb_ctx[768])
   预估 400k × 768 × 4 byte × 2 轨 = ~2.5 GB

D-0 实测项
----------
- HF cache 是否含 shibing624/text2vec-base-chinese (validate via SentenceTransformer init)
- GPU vs CPU 速度 (项目本机有 CUDA 时 < 2 h, CPU 4-6 h)

运行方式
---------
本 stage 已注册于 core/dag.py::STAGES_MAIN (无 enabled_when 条件, 随主管道
always-on 执行); 也可单独手动触发 (全量 40 万文章编码 GPU 约 4-6 h):
    python news_process/30a_article_sbert.py
"""

from __future__ import annotations

import os
import sys
import time
from typing import Optional

import numpy as np
import pandas as pd

# 路径注入: 让 ``news_process.core.*`` 在任意 cwd 下可解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "30a_article_sbert"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

def _resolve_sbert_model(config: dict) -> tuple[str, str | None]:
    """从 config/features.yaml::embedding_robustness 解析 (model_id, revision).

    fix(omni-g-embed-05, 2026-06-11): 此前读不存在的 'embedding' 顶级键 (features.yaml
    仅有 embedding_api / embedding_robustness 两键) → 恒走硬编码默认, "单源对齐"声称
    失实; 改 embedding_robustness.model 时 stage 30a 静默不跟随, 与 stage 15/25 t2v
    轨配置漂移。现真单源 = embedding_robustness.model (+ 可选 revision 键钉死 HF
    commit, 防上游模型权重更新静默改变全部嵌入派生测度)。
    """
    rob = (config or {}).get('embedding_robustness', {}) or {}
    model_id = rob.get('model') or 'shibing624/text2vec-base-chinese'
    revision = rob.get('revision') or None
    return model_id, revision


# 与 config/features.yaml::embedding_robustness.model 真单源对齐 (stage 15/25 t2v 同源)
_SBERT_MODEL_ID, _SBERT_REVISION = _resolve_sbert_model(CONFIG)

# 30a 输入文本构造版本 (provenance, 与 LLMCache 的 prompt_version 维度同哲学):
# v2 = 2026-06-08 dual-track parity (content_full/content_ctx 已 prepend 标题一次,
# title_col=None 关闭二次前置)。任何对输入构造/截断策略的变更必须 bump。
_TEXT_PIPELINE_VERSION = 'v2-2026-06-08-dualtrack-prepend'

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

    # fix(omni-g-embed-07, 2026-06-11): 推理前确定性硬化 (共享 helper, 对齐 stage 23
    # tone_berts V4 T1.1a — seed 四源 + deterministic algorithms + cuDNN 策略)
    from news_process.pipeline.text.embedding_engine import ensure_torch_determinism
    ensure_torch_determinism()

    logger.info(
        f"  加载 SBERT: {_SBERT_MODEL_ID}"
        + (f" @ revision={_SBERT_REVISION}" if _SBERT_REVISION else "")
    )
    # fix(omni-g-embed-05, 2026-06-11): 配置了 revision 时钉死 HF commit;
    # 未配置保持旧调用形态 (兼容旧版 sentence-transformers 无 revision kwarg)
    if _SBERT_REVISION:
        model = SentenceTransformer(_SBERT_MODEL_ID, revision=_SBERT_REVISION)
    else:
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


def _build_output_frame(
    df: pd.DataFrame, embs_full: np.ndarray, embs_ctx: np.ndarray,
) -> pd.DataFrame:
    """组装 30a 输出 frame (对齐键 + provenance + 双轨向量).

    fix(omni-g-embed-03, 2026-06-11): 新增 model_id / model_revision /
    text_pipeline_version provenance 列 (与 LLMCache 键维度对齐) + docid 透传 —
    供 stage 18 消费端按 article_id 显式 join 并检测 30a 陈旧 (此前消费端纯位置
    对齐, 行数恰相等的陈旧 30a 会静默整列错位)。
    """
    out: dict = {
        'article_id': df.index if 'article_id' not in df.columns else df['article_id'],
    }
    if 'docid' in df.columns:
        out['docid'] = df['docid']
    out.update({
        'target_bank': df['target_bank'] if 'target_bank' in df.columns else pd.NA,
        'year': df['year'] if 'year' in df.columns else pd.NA,
        '日期': df['日期'] if '日期' in df.columns else pd.NA,
        'emb_full': list(embs_full),   # list of 1D arrays (parquet-compatible)
        'emb_ctx': list(embs_ctx),
        'model_id': _SBERT_MODEL_ID,
        'model_revision': _SBERT_REVISION or '',
        'text_pipeline_version': _TEXT_PIPELINE_VERSION,
    })
    return pd.DataFrame(out)


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

    # ── 双轨编码 (dual-track parity 2026-06-08) ──
    # content_full / content_ctx 均已由 stage 13 (ctx_materializer) prepend 标题【恰好一次】。
    # 故 title_col=None 关闭 encode_articles 内 _truncate_for_sbert 的二次标题前置 —— 否则
    # ctx 轨 (读已含标题的 content_ctx) 会重复注入标题 (标题×2), 与 full 轨 (标题×1) 不对称,
    # 致 emb_full/emb_ctx 语义权重不可比 (下传 stage 18 semantic_staleness;
    # 原 stage 17 topic emb 消费端已于 2026-06-09 随 BERTopic 阶段整体移除)。
    # 两轨改为同型构造: 各取 content_*[:TITLE+PARA] (标题在串首恰好一次), 仅输入文本范围不同
    # (full=标题+全文 / ctx=标题+实体窗口)。与同源 content_full/content_ctx 消费者 (stage 15
    # policy_alignment / stage 27 benefit_society) 读同一含标题串、标题注入一次的口径对齐
    # (注: 各模块下游截断方式不同——sbert 取字符 [:400], stage 15 走 token 截断——此处仅指
    #  "读含标题串、标题恰好一次"这一点对齐, 非截断算法相同)。
    # 缺 content_full 时回退裸 '内容'+'标题' (旧 schema; _truncate_for_sbert 注入标题一次)。
    _has_cfull = 'content_full' in df.columns
    embs_full = encode_articles(
        df,
        content_col='content_full' if _has_cfull else '内容',
        title_col=None if _has_cfull else '标题',
    )
    embs_ctx = (
        encode_articles(df, content_col='content_ctx', title_col=None)
        if 'content_ctx' in df.columns
        else np.full_like(embs_full, np.nan)
    )

    # ── 持久化 (fix(omni-g-embed-03, 2026-06-11): 含 provenance 列) ──
    out_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    out_df = _build_output_frame(df, embs_full, embs_ctx)
    out_df.to_parquet(out_path, index=False)

    size_mb = os.path.getsize(out_path) / 1024 / 1024
    logger.info(f"  输出: {out_path} ({size_mb:.1f} MB)")
    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
