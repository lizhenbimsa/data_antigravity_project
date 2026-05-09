"""
news_process.pipeline.sentiment.herd_decay — 跟风/抄袭新闻检测与衰减加权
=========================================================================

迁移说明 (Phase 7a-7)：
    本模块由原 root script ``24_herd_decay_processor.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.herd_decay``


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

输入: 23_bert_tone.parquet (阶段 23 BERT 情感分析的输出, 硬编码读取, 不做回退)
输出: 24_herd_decay.parquet (追加 herd_weight 列)
"""

import os
import sys
import logging
import numpy as np
import pandas as pd

from scipy.sparse import csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import pairwise_distances_chunked, pairwise_distances

# Phase 7a-7: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/herd_decay.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging

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
CHUNK_SIZE = HERD_CFG.get('chunk_size', 1000)  # 仅用于日志显示; 实际内存分块由 pairwise_distances_chunked(working_memory=) 控制


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
        df: 篇章级 DataFrame, 须含 'target_bank', '日期', '内容' 列

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
    # 文本列名优先级: '内容'(流水线标准列名) > '正文' > 'content'
    text_col = '内容' if '内容' in df.columns else ('正文' if '正文' in df.columns else 'content')
    if text_col not in df.columns:
        logger.warning(f"  文本列 '{text_col}' 不存在, 所有 herd_weight 设为 1.0")
        df['herd_weight'] = 1.0
        df['n_similar_articles'] = 0
        return df

    # 初始化结果列
    df['herd_weight'] = 1.0
    df['n_similar_articles'] = 0

    # 校验必需列
    if 'target_bank' not in df.columns:
        logger.warning("  'target_bank' 列不存在, 所有 herd_weight 设为 1.0")
        return df

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

        if n_articles <= 2000:
            # ---- 向量化路径 ----
            # NaT 处理策略 (plan s1)：含 NaT 的配对视为"窗口外"，不计入跟风
            # 用 epoch 绝对日期转换，避免基准点漂移
            _epoch = pd.Timestamp('1970-01-01')
            dates_num = np.array(
                [(d - _epoch).days if pd.notna(d) else np.nan for d in dates],
                dtype=np.float64)
            time_diff = np.abs(np.subtract.outer(dates_num, dates_num))
            # NaN time_diff → TIME_WINDOW_DAYS+1: 含 NaT 的配对必然超出窗口
            # (修复历史 bug: 之前 nan_to_num(..., nan=0.0) 会让 NaT 配对总是通过窗口检查,
            #  导致跨任意时间相隔的相似文章被误判为前驱、herd_weight 系统性偏低)
            time_diff = np.nan_to_num(time_diff, nan=float(TIME_WINDOW_DAYS + 1))
            valid_mask = (time_diff <= TIME_WINDOW_DAYS) & np.tril(
                np.ones((n_articles, n_articles), dtype=bool), k=-1)
            sim_matrix = 1.0 - pairwise_distances(tfidf_matrix, metric='cosine')
            herd_mask = (sim_matrix >= SIMILARITY_THRESHOLD) & valid_mask
            similar_counts = herd_mask.sum(axis=1)
        else:
            # ---- 分块路径 ----
            similar_counts = np.zeros(n_articles, dtype=int)
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
                        # 时间窗口检查 (plan s1: 任一为 NaT → 视为窗口外, 跳过)
                        if pd.isna(date_i) or pd.isna(date_j):
                            continue
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

    # 加载篇章级数据: 固定读取阶段 23 (BERT情感分析) 的输出
    # 严禁回退读取 22/21 的输出，避免磁盘残留旧文件导致静默数据污染
    filenames = CONFIG.get('filenames', {})
    input_filename = filenames.get('output_23_bert_tone', '23_bert_tone.parquet')
    output_filename = filenames.get('output_24_herd_decay', '24_herd_decay.parquet')
    input_file = os.path.join(OUTPUT_DIR, input_filename)
    output_file = os.path.join(OUTPUT_DIR, output_filename)

    if not os.path.exists(input_file):
        logger.error(
            f"输入文件未找到: {input_file}。"
            f"请确保阶段 23 (tone_berts) 已在 enabled_methods 中启用并成功执行。"
        )
        # 显式以非零返回码退出, 让上游编排器能感知"DAG 24 依赖 23"契约违规,
        # 避免父进程把 'silent return' 误判为 stage 24 成功 (详见 plan c2)。
        raise SystemExit(1)

    # 记录输入文件修改时间，便于数据溯源审计
    import datetime as _dt
    _mtime = os.path.getmtime(input_file)
    logger.info(
        f"  📁 输入文件: {input_filename} "
        f"(修改时间: {_dt.datetime.fromtimestamp(_mtime).strftime('%Y-%m-%d %H:%M:%S')})"
    )

    df = pd.read_parquet(input_file)
    logger.info(f"  加载 {len(df):,} 条新闻 (来源: {input_filename})")

    # 执行跟风检测
    df = compute_herd_weights(df)

    # 保存 (追加 herd_weight 列后写入独立输出文件)
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(cfg['paths']['output_dir'],
                              cfg['filenames']['output_21_tone_llms'])
    save_parquet_with_metadata(
        df=df,
        output_path=output_file,
        stage_name="24_herd_decay",
        config=cfg,
        input_files=[input_file],
    )
    logger.info(f"  已保存至 {output_file}")

    elapsed = time.time() - start_time
    logger.info(f"  耗时: {elapsed:.1f}秒")
    logger.info(f"阶段 {STAGE_NAME} 完成 ✓")


if __name__ == '__main__':
    main()
