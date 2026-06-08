"""news_process.pipeline.text.article_topic — stage 17 BERTopic narrative topic.

v3.7.0 PR #10 (D1) — Article-level narrative topic labeling. 立 P10 paper
(narrative-novelty) 的核心方法.

学术依据
--------
Bybee, J., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and
business cycles. Review of Financial Studies, 37(3), 887-936.

Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation
within the FOMC: A computational linguistics approach. Quarterly Journal of
Economics, 133(2), 801-870.

Grootendorst, M. (2022). BERTopic: Neural topic modeling with a class-based
TF-IDF procedure. arXiv:2203.05794.

设计决策
--------
1. **SBERT 模型**: 复用 stage 30a 已持久化 article embeddings (零重新编码)
2. **UMAP**: random_state=42 固定 seed (UMAP stochastic 必锁)
3. **HDBSCAN**: min_cluster_size=5000, 400k 文章 → K ≈ 15-30 预期
4. **CountVectorizer tokenizer**: 用 PR #1 的 cn_tokenize (jieba + 中文金融停用词)
5. **embedding_model=None**: 绕过 BERTopic 默认下载 all-MiniLM (HF 网络限制)
6. **full → ctx hierarchical alignment**: full 轨先 fit_transform, ctx 轨用
   .transform() 复用同一组 topic embeddings (zero K drift)

panel 新增列
-----------
``frac_topic_k_{full,ctx}`` × K (K 个 narrative topic 的 bank-year 比例)
``topic_hhi_{full,ctx}``     bank-year 内 topic 分布 HHI (聚焦度)

依赖
----
v3.7.0 启用需 pip install -r requirements.txt 包含 bertopic / umap-learn / hdbscan
(默认注释化, 见 PR #8.5).

D-0 实测项 (v2.3 G-D1.1)
------------------------
BERTopic K 自动发现实际值 + c-TF-IDF top-10 词中文金融专家解读 ≥ 80%.

stub 说明
---------
模块代码完整, 实际跑由用户执行:
    1. 取消 requirements.txt 中 bertopic / umap-learn / hdbscan 行注释
    2. pip install -r requirements.txt
    3. python news_process/30a_article_sbert.py   # 4-6 h SBERT 编码
    4. python news_process/17_article_topic.py    # 4-6 h BERTopic
"""

from __future__ import annotations

import json
import os
import sys
import time

import numpy as np
import pandas as pd

# Path injection
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config  # noqa: E402
from news_process.core.logging import setup_logging  # noqa: E402
from news_process.core.text.cn_text_utils import cn_tokenize  # noqa: E402

CONFIG = load_config()
STAGE_NAME = "17_article_topic"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# UMAP + HDBSCAN config (v2.3 PR #10 详细配置)
UMAP_PARAMS = dict(
    n_neighbors=15,
    n_components=5,
    min_dist=0.0,
    metric='cosine',
    random_state=42,
)
HDBSCAN_PARAMS = dict(
    min_cluster_size=5000,
    metric='euclidean',
    cluster_selection_method='eom',
    prediction_data=True,
)
VECTORIZER_PARAMS = dict(
    tokenizer=cn_tokenize,
    token_pattern=None,
    max_features=10000,
    min_df=10,
    max_df=0.95,
)


def build_topic_model():
    """构造 BERTopic 实例; 关键: embedding_model=None 避免 HF 下载.

    Returns:
        BERTopic instance (未 fit).
    """
    try:
        from bertopic import BERTopic
        from hdbscan import HDBSCAN
        from sklearn.feature_extraction.text import CountVectorizer
        from umap import UMAP
    except ImportError as e:
        logger.error(
            f"  依赖未装: {e}; 启用步骤: 取消 requirements.txt 中 bertopic / "
            f"umap-learn / hdbscan 行注释后 pip install"
        )
        raise

    umap_model = UMAP(**UMAP_PARAMS)
    hdbscan_model = HDBSCAN(**HDBSCAN_PARAMS)
    vectorizer = CountVectorizer(**VECTORIZER_PARAMS)

    return BERTopic(
        embedding_model=None,  # 不让 BERTopic 自己下载, 用 precomputed embeddings
        umap_model=umap_model,
        hdbscan_model=hdbscan_model,
        vectorizer_model=vectorizer,
        calculate_probabilities=True,
        verbose=True,
    )


def fit_full_track(docs_full: list[str], embeddings_full: np.ndarray):
    """full 轨 fit_transform; 输出 topic_model + topics + probs."""
    topic_model = build_topic_model()
    logger.info(f"  full 轨 fit_transform: {len(docs_full)} docs")
    t0 = time.time()
    topics, probs = topic_model.fit_transform(docs_full, embeddings_full)
    logger.info(
        f"  full 轨完成 ({time.time() - t0:.1f}s); K={len(topic_model.get_topic_info()) - 1} "
        f"(去除 outlier topic -1)"
    )
    return topic_model, topics, probs


def transform_ctx_track(
    topic_model,
    docs_ctx: list[str],
    embeddings_ctx: np.ndarray,
) -> tuple[list[int], np.ndarray]:
    """ctx 轨用 full 轨已 fit 的 topic_model.transform(), 保 K 一致."""
    logger.info(f"  ctx 轨 transform: {len(docs_ctx)} docs (hierarchical alignment)")
    t0 = time.time()
    topics_ctx, probs_ctx = topic_model.transform(docs_ctx, embeddings_ctx)
    logger.info(f"  ctx 轨完成 ({time.time() - t0:.1f}s)")
    return topics_ctx, probs_ctx


def aggregate_to_bank_year(
    article_df: pd.DataFrame,
    topics_full: list[int],
    topics_ctx: list[int],
    K: int,
) -> pd.DataFrame:
    """article-level topic id → bank-year topic 分布.

    Returns:
        panel DataFrame with frac_topic_k_{full,ctx} × K + topic_hhi_{full,ctx}.
    """
    df = article_df.copy()
    df['_topic_full'] = topics_full
    df['_topic_ctx'] = topics_ctx

    # 双轨 dummy-encode topic ID → bank-year mean
    # dual-track parity (2026-06-08): 两轨 dummy 列集 reindex 到【共享】topic-id 空间
    # range(-1, K) (-1=outlier, 0..K-1=topics)。修 presence-driven get_dummies 的孤儿列
    # 缺陷 — 某 topic 若只在一轨出现, 另一轨缺该 frac_topic_k 列 → 破坏 _full/_ctx 结构对等。
    # 两轨共享同一 fit 的 topic_model (ctx 走 transform 复用, K 一致), 故拓扑空间良定义;
    # reindex 仅对缺席 topic 补全 0 列, 对实际出现的 topic 零数值影响。
    _topic_cat = pd.CategoricalDtype(categories=list(range(-1, K)))
    full_dummies = pd.get_dummies(df['_topic_full'].astype(_topic_cat), prefix='_tf')
    ctx_dummies = pd.get_dummies(df['_topic_ctx'].astype(_topic_cat), prefix='_tc')

    full_panel = (
        pd.concat([df[['target_bank', 'year']], full_dummies], axis=1)
        .groupby(['target_bank', 'year'])
        .mean()
        .reset_index()
    )
    ctx_panel = (
        pd.concat([df[['target_bank', 'year']], ctx_dummies], axis=1)
        .groupby(['target_bank', 'year'])
        .mean()
        .reset_index()
    )

    # 重命名为 frac_topic_k_full / frac_topic_k_ctx
    full_panel.columns = [
        c.replace('_tf_', 'frac_topic_').replace('-1', 'outlier') + '_full'
        if c.startswith('_tf_') else c
        for c in full_panel.columns
    ]
    ctx_panel.columns = [
        c.replace('_tc_', 'frac_topic_').replace('-1', 'outlier') + '_ctx'
        if c.startswith('_tc_') else c
        for c in ctx_panel.columns
    ]

    panel = full_panel.merge(ctx_panel, on=['target_bank', 'year'], how='outer')

    # topic HHI (聚焦度)
    full_cols = [c for c in panel.columns if c.startswith('frac_topic_') and c.endswith('_full')]
    ctx_cols = [c for c in panel.columns if c.startswith('frac_topic_') and c.endswith('_ctx')]
    if full_cols:
        panel['topic_hhi_full'] = (panel[full_cols] ** 2).sum(axis=1)
    if ctx_cols:
        panel['topic_hhi_ctx'] = (panel[ctx_cols] ** 2).sum(axis=1)

    # topic Shannon 熵 (叙事多样性, Dyer-Lang-Stice-Lawrence 2017 JAE; Blei 2003) —
    # HHI 的对偶: HHI=Σp² 对【头部】主题敏感, 熵=−Σp·ln p 对【长尾】主题敏感 (批 #14,
    # 2026-06-05)。dormant: 依附 stage 17 BERTopic 的 frac_topic 输入, stage 17 未跑通时
    # 本 stage 不产出, 故默认 golden 无此列 (与 topic_hhi 同条件)。
    def _row_entropy(row) -> float:
        import math
        vals = [v for v in row.to_numpy() if v == v and v > 0]  # 去 NaN/0/负
        tot = sum(vals)
        if tot <= 0:
            return float('nan')
        return float(-sum((v / tot) * math.log(v / tot) for v in vals))
    if full_cols:
        panel['topic_entropy_full'] = panel[full_cols].apply(_row_entropy, axis=1)
    if ctx_cols:
        panel['topic_entropy_ctx'] = panel[ctx_cols].apply(_row_entropy, axis=1)

    return panel


def main():
    stage_start = time.time()
    logger.info("=" * 60)
    logger.info("阶段 17: Article-level BERTopic narrative topic (v3.7.0 PR #10, D1)")
    logger.info("=" * 60)

    output_dir = CONFIG['paths']['output_dir']

    # ── 加载 stage 30a article embeddings ──
    emb_path = os.path.join(output_dir, '30a_article_embeddings.parquet')
    if not os.path.exists(emb_path):
        logger.error(
            f"  stage 30a 未跑: {emb_path}; 先执行 python news_process/30a_article_sbert.py"
        )
        sys.exit(1)

    emb_df = pd.read_parquet(emb_path)
    logger.info(f"  article embeddings: {len(emb_df)} 行")

    # 加载 article-level 文本 (供 BERTopic CountVectorizer 重新 tokenize)
    src_path = os.path.join(output_dir, '13_news_with_ctx.parquet')
    art_df = pd.read_parquet(src_path)

    # metric-audit 2026-06-02 final (病根A 同型 latent crash): 13_news_with_ctx 仅有
    # str '日期' 无 'year' 列, 而 out_article['year']=art_df['year'] (下方) + 聚合
    # groupby(['target_bank','year']) 会 KeyError('year'). 与 executive_ner /
    # article_staleness 同口径从 '日期' 派生 year (在 emb merge 前, 使 year 随 art_df 保留).
    if 'year' not in art_df.columns:
        _date_col = '日期' if '日期' in art_df.columns else 'publish_date'
        art_df['year'] = pd.to_datetime(art_df[_date_col], errors='coerce').dt.year

    # 修 S2.2 merge bug: 拆 if/else 三路分支, 避免 left_index 参数类型混合 (pandas TypeError).
    if 'article_id' in emb_df.columns and 'article_id' in art_df.columns:
        art_df = art_df.merge(
            emb_df[['article_id', 'emb_full', 'emb_ctx']],
            on='article_id', how='inner',
        )
    elif 'article_id' in emb_df.columns:
        # art_df 用 index 作 article_id
        art_df = art_df.reset_index().rename(columns={'index': 'article_id'}).merge(
            emb_df[['article_id', 'emb_full', 'emb_ctx']],
            on='article_id', how='inner',
        )
    else:
        # 行序对齐 fallback (stage 30a 输出与 stage 13 输入行序一致, 见 article_sbert.py:main)
        if len(art_df) != len(emb_df):
            logger.error(
                f"  emb_df 与 art_df 行数不一致 ({len(emb_df)} vs {len(art_df)}), "
                f"无 article_id 列, 无法 merge"
            )
            sys.exit(1)
        art_df = art_df.assign(
            emb_full=list(emb_df['emb_full']),
            emb_ctx=list(emb_df['emb_ctx']),
        )

    # P1 修复 (metric-audit 2026-06-02, 病根A): full 轨改读 content_full (含标题).
    docs_full = art_df['content_full' if 'content_full' in art_df.columns else '内容'].fillna('').tolist()
    docs_ctx = art_df['content_ctx'].fillna('').tolist() if 'content_ctx' in art_df.columns else docs_full
    embs_full = np.stack(art_df['emb_full'].tolist())
    embs_ctx = np.stack(art_df['emb_ctx'].tolist())

    # ── full 轨 fit_transform ──
    topic_model, topics_full, _ = fit_full_track(docs_full, embs_full)

    # ── ctx 轨 transform (hierarchical alignment) ──
    topics_ctx, _ = transform_ctx_track(topic_model, docs_ctx, embs_ctx)

    # ── 持久化 article-level topic 标签 ──
    out_article = pd.DataFrame({
        'article_id': art_df.index if 'article_id' not in art_df.columns else art_df['article_id'],
        'target_bank': art_df['target_bank'],
        'year': art_df['year'],
        'topic_id_full': topics_full,
        'topic_id_ctx': topics_ctx,
    })
    out_article_path = os.path.join(output_dir, '17_article_topics.parquet')
    out_article.to_parquet(out_article_path, index=False)
    logger.info(f"  article-level → {out_article_path}")

    # ── topic_info 持久化 (c-TF-IDF 关键词) ──
    info = topic_model.get_topic_info()
    info_path = os.path.join(output_dir, '17_topic_info.parquet')
    info.to_parquet(info_path, index=False)
    logger.info(f"  topic_info → {info_path}")

    # ── bank-year 聚合 ──
    K = len(info) - 1  # 去除 outlier -1
    panel = aggregate_to_bank_year(art_df, topics_full, topics_ctx, K)
    panel_path = os.path.join(output_dir, '17_topic_panel.parquet')
    panel.to_parquet(panel_path, index=False)
    logger.info(f"  bank-year panel → {panel_path} ({len(panel)} 行)")

    # ── sidecar JSON: K + topic name mapping (供 PR #14 集成) ──
    sidecar = {
        'stage': '17_article_topic',
        'v3_7_0_pr': '#10 (D1 BERTopic)',
        'K_discovered': int(K),
        'sbert_model': 'shibing624/text2vec-base-chinese',
        'umap_seed': 42,
        'min_cluster_size': HDBSCAN_PARAMS['min_cluster_size'],
        'topic_keywords_top10': {
            int(tid): [w for w, _ in topic_model.get_topic(tid)][:10]
            for tid in info['Topic'].tolist() if tid != -1
        },
        'note': 'G-D1.2 准入门控: top-10 词中文金融专家解读 ≥ 80%',
    }
    sidecar_path = os.path.join(output_dir, '17_topic_metadata.json')
    with open(sidecar_path, 'w', encoding='utf-8') as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2)
    logger.info(f"  sidecar → {sidecar_path}")

    logger.info(f"  耗时: {time.time() - stage_start:.1f} s")


if __name__ == '__main__':
    main()
