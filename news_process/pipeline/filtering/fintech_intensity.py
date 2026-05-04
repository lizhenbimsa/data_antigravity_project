"""
news_process.pipeline.filtering.fintech_intensity — 阶段14：金融科技技术重度评分
=================================================================================

功能：
    在阶段 12 的 AC 关键词分类（二元判定）基础上，使用 TF-IDF + SIF 词向量质心
    计算连续型技术强度得分 `fintech_intensity_score`，消除三类系统性偏差：
      1. 复读机刷分（Cheap Talk）— Bingler et al. (2022, FRL)
      2. 长文体量偏差（Document Length Bias）— Manning et al. (2008, Ch 6.4)
      3. 术语区分度缺失（Term Discriminability Loss）— Loughran & McDonald (2011, JF)

    核心公式（双重对数方程）:
      Score_d = Σ_{i: TF_{d,i}>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i
      其中 W_i = IDF_i × CosSim_scaled_i

    白话解释:
      给每个金融科技关键词加上"含金量权重"（IDF稀缺度 × 语义纯粹度），
      同时防复读机刷分和长文偏差。产出连续型"真实技术强度分"。

    **阶段 12 零修改。** 本文件完全独立，删除即可回滚。

输入：
    阶段 12 输出的 `12_fintech_news_full.parquet`（全量，用于全局 IDF 计算）
    阶段 12 输出的 `12_fintech_news.parquet`（仅金融科技，用于得分计算）

输出：
    `14_fintech_intensity.parquet`（= 12 filtered + fintech_intensity_score + intensity_verified）

学术依据：
    Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using
      machine learning. The Review of Financial Studies, 34(7), 3265-3315.
    Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information
      Retrieval. Cambridge University Press.
    Arora, S., Liang, Y., & Ma, T. (2017). A simple but tough-to-beat baseline for
      sentence embeddings. Proceedings of ICLR 2017.
    Ethayarajh, K. (2019). How contextual are contextualized word representations?
      Proceedings of EMNLP-IJCNLP 2019.
    Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization.
      Proceedings of SIGIR '96, pp. 21-29.

迁移说明 (Phase 7a-3)：
    本模块由原 root script ``14_fintech_intensity.py`` body 迁入。
    规范调用方式：
        python -m news_process.pipeline.filtering.fintech_intensity
"""

import os
import time
import json
import math
import sys
import numpy as np
import pandas as pd
import jieba

from collections import Counter
from joblib import Parallel, delayed

# Phase 7a-3: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_memory_usage, log_stage_summary
from news_process.core.reporting import save_dataset
from news_process.core.text.ahocorasick import load_fintech_dict

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "14_fintech_intensity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 读取技术重度评分配置 (config.yaml → fintech_intensity 节)
INTENSITY_CONFIG = CONFIG.get('fintech_intensity', {})
EMBEDDING_MODEL = INTENSITY_CONFIG.get('embedding_model', 'shibing624/text2vec-base-chinese')
MIN_DISTINCT_KEYWORDS_JIEBA = INTENSITY_CONFIG.get('min_distinct_keywords_jieba', 2)
WINSORIZE_PERCENTILES = INTENSITY_CONFIG.get('winsorize_percentiles', [1, 99])
ANISOTROPY_FLOOR = INTENSITY_CONFIG.get('anisotropy_floor', 0.1)

# 加载金融科技词典（与阶段 12 共享同一份词典）
FINTECH_KEYWORDS, _ = load_fintech_dict(CONFIG['paths'].get('fintech_dict_file', ''))
logger.info(f"金融科技词典: 共 {len(FINTECH_KEYWORDS)} 个词汇")


# ============================================================================
# 2. 全局文档频率解析 (Module A)
# ============================================================================

def _parse_global_df(df_full: pd.DataFrame) -> tuple:
    """从全量分类结果中解析每个关键词的文档频率 (DF)。

    无需重新执行 AC 扫描 —— 阶段 12 已将完整命中信息持久化于
    fintech_keyword_details 列。

    学术依据: Gentzkow, Kelly & Taddy (2019, JEL, §2.2):
      "IDF must be computed on the full reference corpus"

    Args:
        df_full: 全量 DataFrame（含非金融科技文档）。

    Returns:
        tuple: (keyword_doc_freq: Counter, N_total: int)
    """
    keyword_doc_freq = Counter()
    N_total = len(df_full)

    for details_json in df_full['fintech_keyword_details']:
        if details_json:
            try:
                details = json.loads(details_json)
                doc_kw_set = {kd['keyword'] for kd in details}
                keyword_doc_freq.update(doc_kw_set)
            except (json.JSONDecodeError, KeyError, TypeError):
                continue

    logger.info(f"全局 DF 解析完成: {N_total} 篇文档, "
                f"{len(keyword_doc_freq)} 个不同关键词")
    return keyword_doc_freq, N_total


# ============================================================================
# 3. 综合权重构建 (Module B)
# ============================================================================

def _build_intensity_weights(keyword_doc_freq: Counter, N_total: int) -> dict:
    """构建 IDF × CosSim 综合权重。

    步骤 A: 全局 IDF 计算 + 均值归一化 + Winsorization
    步骤 B: SIF 加权质心 + 各向异性校准
    步骤 C: 预乘综合权重

    Args:
        keyword_doc_freq: {关键词: 出现该词的文档数}。
        N_total: 全量文档总数。

    Returns:
        dict: {关键词: 综合权重 (float)}
    """
    if not keyword_doc_freq or N_total == 0:
        logger.warning("DF 为空或文档数为零，所有权重降级为 1.0")
        return {kw: 1.0 for kw in FINTECH_KEYWORDS}

    # ── 步骤 A: 全局 IDF 计算 ──
    raw_idf = {}
    for kw in FINTECH_KEYWORDS:
        df_w = keyword_doc_freq.get(kw, 0)
        raw_idf[kw] = math.log10(N_total / (1 + df_w))

    values = list(raw_idf.values())
    mean_val = float(np.mean(values)) if values else 1.0
    if mean_val > 0:
        normed_idf = {w: v / mean_val for w, v in raw_idf.items()}
    else:
        normed_idf = {w: 1.0 for w in raw_idf}

    normed_vals = np.array(list(normed_idf.values()))
    p_lo, p_hi = WINSORIZE_PERCENTILES
    if len(normed_vals) >= 2:
        p1 = float(np.percentile(normed_vals, p_lo))
        p99 = float(np.percentile(normed_vals, p_hi))
        idf_weights = {w: float(np.clip(v, p1, p99)) for w, v in normed_idf.items()}
    else:
        idf_weights = dict(normed_idf)

    logger.info(f"IDF 权重: mean={np.mean(list(idf_weights.values())):.4f}, "
                f"std={np.std(list(idf_weights.values())):.4f}")

    # ── 步骤 B: SIF 加权质心 + 各向异性校准 ──
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"加载词向量模型: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)

        kw_list = list(idf_weights.keys())
        embeddings = model.encode(kw_list, show_progress_bar=False)

        weights_arr = np.array([idf_weights[kw] for kw in kw_list])
        centroid = np.average(embeddings, axis=0, weights=weights_arr)

        centroid_norm = centroid / (np.linalg.norm(centroid) + 1e-10)
        emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
        cos_sims = emb_norms @ centroid_norm

        # ── 各向异性校准 (Ethayarajh, 2019, EMNLP) ──
        min_sim, max_sim = float(cos_sims.min()), float(cos_sims.max())

        cos_sim_scaled = {}
        if max_sim > min_sim:
            for i, kw in enumerate(kw_list):
                scaled = ANISOTROPY_FLOOR + (1.0 - ANISOTROPY_FLOOR) * \
                         (cos_sims[i] - min_sim) / (max_sim - min_sim)
                cos_sim_scaled[kw] = float(scaled)
        else:
            logger.warning("所有关键词余弦相似度相同，CosSim 权重回退为 1.0")
            cos_sim_scaled = {kw: 1.0 for kw in kw_list}

        logger.info(f"CosSim 校准: min={min_sim:.4f}, max={max_sim:.4f}, "
                    f"floor={ANISOTROPY_FLOOR}")
        del model, embeddings

    except ImportError:
        logger.warning("sentence_transformers 未安装，CosSim 权重降级为 1.0"
                       "（仅使用 IDF 权重）")
        cos_sim_scaled = {kw: 1.0 for kw in idf_weights}
    except Exception as e:
        logger.warning(f"词向量计算异常 ({type(e).__name__}: {e})，CosSim 降级为 1.0")
        cos_sim_scaled = {kw: 1.0 for kw in idf_weights}

    # ── 步骤 C: 预乘综合权重 ──
    combined_weights = {}
    for kw in FINTECH_KEYWORDS:
        combined_weights[kw] = idf_weights.get(kw, 1.0) * cos_sim_scaled.get(kw, 1.0)

    sorted_weights = sorted(combined_weights.items(), key=lambda x: x[1], reverse=True)
    logger.info("综合权重 Top 20 (硬核词):")
    for kw, w in sorted_weights[:20]:
        logger.info(f"  {kw}: {w:.4f} (IDF={idf_weights.get(kw, 0):.3f}, "
                    f"CosSim={cos_sim_scaled.get(kw, 0):.3f})")
    logger.info("综合权重 Bottom 20 (泛化词):")
    for kw, w in sorted_weights[-20:]:
        logger.info(f"  {kw}: {w:.4f} (IDF={idf_weights.get(kw, 0):.3f}, "
                    f"CosSim={cos_sim_scaled.get(kw, 0):.3f})")

    return combined_weights


# ============================================================================
# 4. 逐文档得分计算 (Module C)
# ============================================================================

def _compute_intensity_scores(df: pd.DataFrame, combined_weights: dict) -> tuple:
    """计算每篇文档的技术重度得分。

    核函数（双重对数方程）:
      Score_d = Σ_{i: TF>0} [ (1 + ln(TF_{d,i})) / (1 + ln(L_d)) ] × W_i

    Args:
        df: 金融科技子集 DataFrame（含 doc_length 列）。
        combined_weights: {关键词: 综合权重}。

    Returns:
        tuple: (scores: list[float], verified_flags: list[bool])
    """
    for kw in FINTECH_KEYWORDS:
        jieba.add_word(kw)

    contents = df['内容'].fillna('').astype(str).tolist()
    kw_set = set(FINTECH_KEYWORDS)

    def _tokenize_chunk(chunk_texts):
        chunk_results = []
        for text in chunk_texts:
            tokens = list(jieba.cut(text))
            tf = Counter(t for t in tokens if t in kw_set)
            chunk_results.append(tf)
        return chunk_results

    batch_size = 2000
    n_docs = len(contents)
    num_batches = max(1, (n_docs - 1) // batch_size + 1)
    chunks = [contents[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    logger.info(f"Jieba 并行分词: {n_docs} 篇, {num_batches} 批次")
    parallel_results = Parallel(n_jobs=-1, prefer='threads')(
        delayed(_tokenize_chunk)(chunk) for chunk in chunks
    )

    all_tfs = []
    for chunk_res in parallel_results:
        all_tfs.extend(chunk_res)

    scores = []
    verified_flags = []

    doc_lengths = df['doc_length'].values if 'doc_length' in df.columns else \
        df['内容'].fillna('').str.len().clip(lower=1).values

    n_fused = 0

    for idx in range(n_docs):
        tf = all_tfs[idx]
        L_d = max(int(doc_lengths[idx]), 1)

        distinct = len(tf)

        if distinct < MIN_DISTINCT_KEYWORDS_JIEBA:
            scores.append(0.0)
            verified_flags.append(False)
            n_fused += 1
            continue

        score = 0.0
        ln_L = 1.0 + math.log(L_d) if L_d > 1 else 1.0
        for kw, count in tf.items():
            if count > 0 and kw in combined_weights:
                ln_tf = 1.0 + math.log(count)
                score += (ln_tf / ln_L) * combined_weights[kw]

        scores.append(round(score, 6))
        verified_flags.append(True)

    logger.info(f"得分计算完成: {n_docs} 篇, 二次熔断降级: {n_fused} 篇 "
                f"({n_fused / max(n_docs, 1) * 100:.1f}%)")

    valid_scores = [s for s, v in zip(scores, verified_flags) if v]
    if valid_scores:
        logger.info(f"得分分布 (verified=True): "
                    f"mean={np.mean(valid_scores):.4f}, "
                    f"std={np.std(valid_scores):.4f}, "
                    f"min={np.min(valid_scores):.4f}, "
                    f"max={np.max(valid_scores):.4f}, "
                    f"median={np.median(valid_scores):.4f}")

    return scores, verified_flags


# ============================================================================
# 5. 主流程编排 (Module D)
# ============================================================================

def main():
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    log_memory_usage(logger, "阶段启动")

    output_dir = CONFIG['paths']['output_dir']

    full_filename = CONFIG['filenames'].get('output_12_fintech_full', '12_fintech_news_full.parquet')
    full_path = os.path.join(output_dir, full_filename)

    if not os.path.exists(full_path):
        logger.error(f"全量分类结果文件未找到: {full_path}")
        logger.error("请确保阶段 12 已执行且生成了全量输出文件。")
        return

    logger.info(f"加载全量分类结果: {full_path}")
    df_full = pd.read_parquet(full_path)
    keyword_doc_freq, N_total = _parse_global_df(df_full)
    del df_full
    log_memory_usage(logger, "全量 DF 解析后(已释放)")

    combined_weights = _build_intensity_weights(keyword_doc_freq, N_total)

    filtered_filename = CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')
    filtered_path = os.path.join(output_dir, filtered_filename)

    if not os.path.exists(filtered_path):
        logger.error(f"金融科技子集文件未找到: {filtered_path}")
        return

    logger.info(f"加载金融科技子集: {filtered_path}")
    df = pd.read_parquet(filtered_path)
    logger.info(f"金融科技子集: {len(df)} 篇文档")

    scores, verified_flags = _compute_intensity_scores(df, combined_weights)

    df['fintech_intensity_score'] = scores
    df['intensity_verified'] = verified_flags

    assert 'is_fintech_news' in df.columns, "原有列 is_fintech_news 丢失!"
    assert 'fintech_intensity_score' in df.columns
    assert 'intensity_verified' in df.columns

    output_filename = CONFIG['filenames'].get(
        'output_14_fintech_intensity', '14_fintech_intensity.parquet')
    output_path = os.path.join(output_dir, output_filename)
    save_dataset(df, output_path, logger)

    n_verified = sum(verified_flags)
    n_total = len(df)
    logger.info(f"intensity_verified=True: {n_verified}/{n_total} "
                f"({n_verified / max(n_total, 1) * 100:.1f}%)")

    log_stage_summary(logger, STAGE_NAME, stage_start, n_total, n_total)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
