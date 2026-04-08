"""
24_herd_decay_processor.py — 跟风/抄袭新闻检测与衰减加权
==========================================================

功能:
  对同一 target_bank 在同一时间窗口内的多篇新闻进行文本相似度聚类,
  识别"跟风抄袭"新闻并施加衰减权重, 防止重复计数导致情感指标注水。

学术依据:
  - Tetlock (2011, JF): 媒体新闻的信息冗余与重复效应
  - Sautner et al. (2023, JF): 文本相似度驱动的曝光度度量

关键设计:
  - TF-IDF 向量化 + 维度封锁 (max_features=10000)
  - pairwise_distances_chunked 分块运算, 峰值内存 < 30GB
  - 相似度阈值 0.35: 高于此值视为"跟风"
  - 衰减公式: weight = 1 / (1 + n_similar_predecessors)

输入: 21_tone_llms.parquet (篇章级已验证新闻)
输出: 21_tone_llms.parquet (原地追加 herd_weight 列)
"""

import os
import logging
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances_chunked

from utils.helpers import load_config, setup_logging

# ============================================================================
# 1. 全局配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "24_herd_decay_processor"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]

# 跟风检测参数
HERD_CFG = CONFIG.get('herd_detection', {})
SIMILARITY_THRESHOLD = HERD_CFG.get('similarity_threshold', 0.35)
TIME_WINDOW_DAYS = HERD_CFG.get('time_window_days', 7)
MAX_FEATURES = HERD_CFG.get('max_features', 10000)
MIN_DF = HERD_CFG.get('min_df', 5)
MAX_DF = HERD_CFG.get('max_df', 0.9)
CHUNK_SIZE = HERD_CFG.get('chunk_size', 1000)


# ============================================================================
# 2. 核心算法: 分块相似度计算
# ============================================================================

def compute_herd_weights(df: pd.DataFrame) -> pd.DataFrame:
    """对同一银行在时间窗口内的新闻进行跟风检测。

    算法流程:
      1. 按 target_bank 分组
      2. 对每组新闻进行 TF-IDF 向量化
      3. 使用 pairwise_distances_chunked 分块计算余弦距离
      4. 在时间窗口内, 若文章 j 与更早的文章 i 的相似度 > 阈值, 
         则 j 被标记为"跟风", 衰减权重递减
      5. 衰减公式: weight_j = 1 / (1 + n_similar_predecessors)

    Args:
        df: 篇章级 DataFrame, 须含 'target_bank', '日期', '正文' 列

    Returns:
        df: 附加 'herd_weight' 和 'n_similar_articles' 列
    """
    logger.info("=" * 60)
    logger.info("步骤 1: 跟风/抄袭新闻检测与衰减加权")
    logger.info("=" * 60)
    logger.info(f"  参数: similarity_threshold={SIMILARITY_THRESHOLD}, "
                f"time_window={TIME_WINDOW_DAYS}天, "
                f"max_features={MAX_FEATURES}, chunk_size={CHUNK_SIZE}")

    # 确保日期列为 datetime
    df['日期'] = pd.to_datetime(df['日期'], errors='coerce')

    # 确定文本列
    text_col = '正文' if '正文' in df.columns else 'content'
    if text_col not in df.columns:
        logger.warning(f"  文本列 '{text_col}' 不存在, 所有 herd_weight 设为 1.0")
        df['herd_weight'] = 1.0
        df['n_similar_articles'] = 0
        return df

    # 初始化结果列
    df['herd_weight'] = 1.0
    df['n_similar_articles'] = 0

    # 按银行分组处理
    bank_groups = df.groupby('target_bank')
    n_banks = len(bank_groups)
    logger.info(f"  共 {n_banks} 家银行待处理")

    total_herd_detected = 0

    for bank_idx, (bank_name, bank_df) in enumerate(bank_groups):
        if len(bank_df) < 2:
            continue  # 只有1篇新闻, 无需检测

        # 按日期排序 (确保时序因果: 只有更早的文章才能是"原创")
        bank_df = bank_df.sort_values('日期').copy()
        indices = bank_df.index.tolist()

        # TF-IDF 向量化
        texts = bank_df[text_col].fillna('').astype(str).tolist()

        # 跳过全空文本
        non_empty = [t for t in texts if len(t.strip()) > 0]
        if len(non_empty) < 2:
            continue

        try:
            vectorizer = TfidfVectorizer(
                max_features=MAX_FEATURES,
                min_df=min(MIN_DF, len(texts)),
                max_df=MAX_DF,
                analyzer='char_wb',  # 中文友好: 字符级 n-gram
                ngram_range=(2, 4),
                dtype=np.float32  # 节省内存
            )
            tfidf_matrix = vectorizer.fit_transform(texts)
        except ValueError as e:
            logger.warning(f"  银行 '{bank_name}' TF-IDF 失败: {e}")
            continue

        # 获取日期序列
        dates = bank_df['日期'].tolist()

        # 分块计算余弦距离
        n_articles = len(indices)
        similar_counts = np.zeros(n_articles, dtype=int)

        # 使用 pairwise_distances_chunked 控制内存
        # metric='cosine' → 距离 ∈ [0, 2], 相似度 = 1 - 距离
        row_start = 0
        for chunk in pairwise_distances_chunked(
            tfidf_matrix, 
            working_memory=128,  # MB, 控制每个 chunk 的内存
            metric='cosine'
        ):
            n_rows_in_chunk = chunk.shape[0]
            similarity_chunk = 1.0 - chunk  # 转为相似度

            for local_i in range(n_rows_in_chunk):
                global_i = row_start + local_i
                date_i = dates[global_i]

                # 只检查比自己更早的文章 (j < global_i)
                for j in range(global_i):
                    date_j = dates[j]
                    # 时间窗口检查
                    if pd.notna(date_i) and pd.notna(date_j):
                        delta_days = abs((date_i - date_j).days)
                        if delta_days > TIME_WINDOW_DAYS:
                            continue

                    sim = similarity_chunk[local_i, j]
                    if sim >= SIMILARITY_THRESHOLD:
                        similar_counts[global_i] += 1

            row_start += n_rows_in_chunk

        # 计算衰减权重
        for k in range(n_articles):
            idx = indices[k]
            n_sim = int(similar_counts[k])
            df.at[idx, 'n_similar_articles'] = n_sim
            df.at[idx, 'herd_weight'] = 1.0 / (1.0 + n_sim)
            if n_sim > 0:
                total_herd_detected += 1

        if (bank_idx + 1) % 50 == 0:
            logger.info(f"  已处理 {bank_idx + 1}/{n_banks} 家银行")

    # 统计摘要
    n_total = len(df)
    herd_pct = total_herd_detected / n_total if n_total > 0 else 0
    logger.info(f"  跟风检测完成:")
    logger.info(f"    总新闻数: {n_total:,}")
    logger.info(f"    检测到跟风新闻: {total_herd_detected:,} ({herd_pct:.1%})")
    logger.info(f"    herd_weight 统计: mean={df['herd_weight'].mean():.4f}, "
                f"min={df['herd_weight'].min():.4f}")

    return df


# ============================================================================
# 3. 主流程
# ============================================================================

def main():
    """主入口: 加载数据 → 跟风检测 → 保存。"""
    import time
    start_time = time.time()

    logger.info("=" * 60)
    logger.info(f"阶段 {STAGE_NAME} 启动")
    logger.info("=" * 60)

    # 加载篇章级数据
    input_file = os.path.join(OUTPUT_DIR, '21_tone_llms.parquet')
    if not os.path.exists(input_file):
        logger.error(f"输入文件不存在: {input_file}")
        return

    df = pd.read_parquet(input_file)
    logger.info(f"  加载 {len(df):,} 条新闻")

    # 执行跟风检测
    df = compute_herd_weights(df)

    # 保存 (原地覆写, 追加 herd_weight 列)
    df.to_parquet(input_file, index=False)
    logger.info(f"  已保存至 {input_file}")

    elapsed = time.time() - start_time
    logger.info(f"  耗时: {elapsed:.1f}秒")
    logger.info(f"阶段 {STAGE_NAME} 完成 ✓")


if __name__ == '__main__':
    main()
