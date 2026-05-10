"""
news_process.pipeline.filtering.news_fintech — 阶段12：金融科技新闻判断
========================================================================

功能：
    判断每篇新闻是否关于金融科技的中文新闻报道。

判断策略：
    1. 将"内容"按字符数等分为上下两半（默认 50%/50%）
    2. 对金融科技词典中的所有词汇，统计在上半和下半的出现情况
    3. 判定条件（须同时满足多样性条件 + 任一分布条件）：
       前置条件) 在标题或全文中，至少出现 ≥ MIN_DISTINCT_KEYWORDS 个不同的词汇
       a) 所有词汇在上半合计出现 ≥ MIN_UPPER 次 AND 下半合计出现 ≥ MIN_LOWER 次
       b) 任一词汇出现在"标题"中 AND 全文合计出现 ≥ MIN_UPPER 次
    4. 记录每个词汇的匹配详情（出现次数、上下半分布、标题出现情况）

学术依据：
    [胡俊2024]     胡俊, 李强, 戴嘉诚, 曾勇 (2024). "基于文本分析的商业银行
                   金融科技测度及赋能效果检验." 中国管理科学, 32(1), 31–41.
                   DOI: 10.16381/j.cnki.issn1003-207x.2022.0125

    [LoughranMcDonald2011] Loughran, T. & McDonald, B. (2011).
                   "When Is a Liability Not a Liability?" Journal of Finance,
                   66(1), 35–65.

性能优化：
    - 使用 Aho-Corasick 自动机一次线性扫描匹配所有关键词
    - 复杂度从 O(文本长度 × 关键词数) 降至 O(文本长度)
    - joblib 并行分批处理

输入：
    阶段2输出的 Parquet 文件（``11_news_bank.parquet``）

输出：
    1. 全量分类结果（含非金融科技新闻），保存为 12_news_fintech_full.parquet/.csv
    2. 仅保留判定为金融科技新闻的记录，追加分类结果列

迁移说明 (Phase 7a-2)：
    本模块由原 root script ``12_news_fintech.py`` body 迁入。
    规范调用方式：
        python -m news_process.pipeline.filtering.news_fintech
"""

import os
import json
import sys
import time
import pandas as pd
import ahocorasick  # noqa: F401
from collections import Counter
from joblib import Parallel, delayed
import psutil

# Phase 7a-2: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_memory_usage, log_stage_summary
from news_process.core.reporting import safe_save_preview_csv
from news_process.core.text.ahocorasick import load_fintech_dict, analyze_fintech_matches

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "12_news_fintech"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从配置中提取参数
FINTECH_NEWS_PARAMS = CONFIG.get('fintech_news_classification', {})

# 分割比例和阈值
SPLIT_RATIO = FINTECH_NEWS_PARAMS.get('split_ratio', 0.5)
MIN_UPPER = FINTECH_NEWS_PARAMS.get('min_occurrences_upper', 1)
MIN_LOWER = FINTECH_NEWS_PARAMS.get('min_occurrences_lower', 1)
MIN_DISTINCT_KEYWORDS = FINTECH_NEWS_PARAMS.get('min_distinct_keywords', 3)


# ============================================================================
# 2. 金融科技词典加载与 Aho-Corasick 自动机构建
# ============================================================================

FINTECH_KEYWORDS, FINTECH_AC_AUTOMATON = load_fintech_dict(
    CONFIG['paths'].get('fintech_dict_file', '')
)


def _analyze_single_article(content: str, title: str = "") -> dict:
    """使用共享 AC 自动机分析单篇文章，返回金融科技词汇匹配详情。"""
    return analyze_fintech_matches(
        content=content,
        title=title,
        fintech_ac=FINTECH_AC_AUTOMATON,
        split_ratio=SPLIT_RATIO,
        min_distinct_keywords=MIN_DISTINCT_KEYWORDS,
        min_upper=MIN_UPPER,
        min_lower=MIN_LOWER,
    )


# ============================================================================
# 3. 批量处理与统计
# ============================================================================

def classify_batch(df_batch: pd.DataFrame) -> tuple:
    """对单个批次执行金融科技新闻分类。

    Args:
        df_batch: 待分类的 DataFrame 批次。

    Returns:
        tuple: (processed_df, stats_dict)
    """
    stats = {
        'total': 0,
        'is_fintech_news_true': 0,
        'is_fintech_news_false': 0,
        'is_fintech_news_with_title': 0,
        'keyword_article_counts': Counter(),
        'keyword_title_article_counts': Counter(),
    }

    if df_batch.empty:
        return df_batch, stats

    df = df_batch.copy()
    stats['total'] = len(df)

    contents = df['内容'].fillna('').astype(str).values
    titles = df['标题'].fillna('').astype(str).values if '标题' in df.columns else [''] * len(df)
    results = [_analyze_single_article(c, t) for c, t in zip(contents, titles)]

    df['is_fintech_news'] = [r['is_fintech_news'] for r in results]
    df['fintech_total_count'] = [r['total_count'] for r in results]
    df['fintech_upper_count'] = [r['upper_count'] for r in results]
    df['fintech_lower_count'] = [r['lower_count'] for r in results]
    df['fintech_in_title'] = [r['in_title'] for r in results]
    df['fintech_distinct_keywords'] = [r['distinct_count'] for r in results]
    df['fintech_keyword_details'] = [
        json.dumps(r['keyword_details'], ensure_ascii=False) if r['keyword_details'] else ''
        for r in results
    ]

    stats['is_fintech_news_true'] = int(df['is_fintech_news'].sum())
    stats['is_fintech_news_false'] = stats['total'] - stats['is_fintech_news_true']
    stats['is_fintech_news_with_title'] = int(df[df['is_fintech_news']]['fintech_in_title'].sum())

    for result in results:
        if result['is_fintech_news']:
            for kd in result['keyword_details']:
                if ((kd['upper'] >= MIN_UPPER and kd['lower'] >= MIN_LOWER)
                        or (kd['in_title'] and kd['total'] >= MIN_UPPER)):
                    stats['keyword_article_counts'][kd['keyword']] += 1
                    if kd['in_title']:
                        stats['keyword_title_article_counts'][kd['keyword']] += 1

    return df, stats


def merge_stats(stats_list: list) -> dict:
    """合并多个批次的统计结果。"""
    merged = {
        'total': 0,
        'is_fintech_news_true': 0,
        'is_fintech_news_false': 0,
        'is_fintech_news_with_title': 0,
        'keyword_article_counts': Counter(),
        'keyword_title_article_counts': Counter(),
    }
    for s in stats_list:
        merged['total'] += s['total']
        merged['is_fintech_news_true'] += s['is_fintech_news_true']
        merged['is_fintech_news_false'] += s['is_fintech_news_false']
        merged['is_fintech_news_with_title'] += s.get('is_fintech_news_with_title', 0)
        merged['keyword_article_counts'] += s['keyword_article_counts']
        merged['keyword_title_article_counts'] += s.get('keyword_title_article_counts', Counter())
    return merged


def log_classification_report(stats: dict, logger):
    """输出金融科技新闻分类统计报告。"""
    logger.info("=" * 70)
    logger.info("===      金融科技新闻判断统计报告      ===")
    logger.info("=" * 70)

    total = stats['total']
    true_count = stats['is_fintech_news_true']
    pct = (true_count / total * 100) if total > 0 else 0.0

    logger.info(f"总记录数: {total:,}")
    logger.info(f"判定为金融科技新闻: {true_count:,} ({pct:.2f}%)")
    if true_count > 0:
        with_title = stats.get('is_fintech_news_with_title', 0)
        no_title = true_count - with_title
        logger.info(f"  - 包含标题匹配的篇数: {with_title:,} 篇 ({with_title/true_count*100:.2f}%)")
        logger.info(f"  - 仅靠正文匹配的篇数: {no_title:,} 篇 ({no_title/true_count*100:.2f}%)")
    logger.info(f"判定为非金融科技新闻: {stats['is_fintech_news_false']:,} ({100 - pct:.2f}%)")
    logger.info(
        f"判定参数: 内容分割比例={SPLIT_RATIO}, "
        f"上半最低出现={MIN_UPPER}次, 下半最低出现={MIN_LOWER}次, "
        f"前置最少不同词汇数={MIN_DISTINCT_KEYWORDS}个, 标题出现时全文最少={MIN_UPPER}次即可"
    )
    logger.info(f"金融科技词典: 共 {len(FINTECH_KEYWORDS)} 个词汇")

    logger.info("-" * 70)
    logger.info("按关键词统计 (金融科技新闻中出现的文章数 所有):")
    kw_top = stats['keyword_article_counts'].most_common()
    if kw_top:
        for rank, (kw, count) in enumerate(kw_top, 1):
            title_count = stats.get('keyword_title_article_counts', {}).get(kw, 0)
            logger.info(f"  {rank:>3}. {kw}: {count:,} 篇 (其中标题匹配 {title_count:,} 篇)")
    else:
        logger.info("  (无匹配)")

    logger.info("=" * 70)


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """金融科技新闻判断阶段主入口。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    total_keywords = len(FINTECH_KEYWORDS)
    logger.info(f"金融科技词典: 共 {total_keywords} 个词汇")
    logger.info(f"AC 自动机状态: {'已构建' if FINTECH_AC_AUTOMATON else '未构建'}")
    logger.info(
        f"分割比例: {SPLIT_RATIO}, "
        f"上半最低出现次数: {MIN_UPPER}, 下半最低出现次数: {MIN_LOWER}, "
        f"最少不同词汇数: {MIN_DISTINCT_KEYWORDS}"
    )

    if not FINTECH_KEYWORDS:
        logger.error("金融科技词典为空！无法执行分类。")
        return

    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_11_bank_news'])
    output_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_12_fintech_news'])

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        return

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    logger.info("开始执行金融科技新闻判断（Aho-Corasick + 并行）...")

    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    if n_jobs <= 0:
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]
    logger.info(f"批次处理: 共 {num_batches} 个批次，每批次 {batch_size} 行，使用 {n_jobs} 个并行进程")

    results = Parallel(n_jobs=n_jobs)(
        delayed(classify_batch)(batch) for batch in df_batches
    )

    classified_dfs = []
    all_stats = []
    for res_df, res_stats in results:
        if not res_df.empty:
            classified_dfs.append(res_df)
        all_stats.append(res_stats)

    if classified_dfs:
        processed_df = pd.concat(classified_dfs, ignore_index=True)
    else:
        processed_df = pd.DataFrame(
            columns=list(df.columns) + [
                'is_fintech_news', 'fintech_total_count',
                'fintech_upper_count', 'fintech_lower_count',
                'fintech_in_title', 'fintech_distinct_keywords',
                'fintech_keyword_details'
            ]
        )

    merged_stats = merge_stats(all_stats)
    log_classification_report(merged_stats, logger)

    # --- 保存全量分类结果（过滤前，含非金融科技新闻，供人工验证抽样使用） ---
    full_output_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_12_fintech_full', '12_fintech_news_full.parquet')
    )
    logger.info(f"正在将全量分类结果（含非金融科技新闻）写入 {full_output_path}...")
    # 使用数据版本控制保存 full 版本
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_11_bank_news'])
    save_parquet_with_metadata(
        df=processed_df,
        output_path=full_output_path,
        stage_name="12_news_fintech",
        config=CONFIG,
        input_files=[input_file],
    )
    full_preview_path = full_output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, full_preview_path, logger)
    logger.info(f"全量分类结果已保存: {len(processed_df):,} 行（供人工验证抽样使用）")

    # --- 只保留金融科技新闻 ---
    before_count = len(processed_df)
    processed_df = processed_df[processed_df['is_fintech_news'] == True].reset_index(drop=True)
    after_count = len(processed_df)
    logger.info(
        f"过滤非金融科技新闻: {before_count:,} → {after_count:,} 行"
        f"（移除 {before_count - after_count:,} 行）"
    )

    logger.info(f"正在将处理结果写入 {output_path}...")
    # 使用数据版本控制保存 filtered 版本
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_11_bank_news'])
    save_parquet_with_metadata(
        df=processed_df,
        output_path=output_path,
        stage_name="12_news_fintech",
        config=CONFIG,
        input_files=[input_file],
    )

    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
