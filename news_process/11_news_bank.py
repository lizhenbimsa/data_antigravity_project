"""
11_news_bank.py — 阶段11：银行新闻判断
=========================================

功能：
    判断每篇新闻是否关于某家银行的中文新闻报道。

判断策略：
    1. 将"内容"按字符数等分为上下两半（默认 50%/50%）
    2. 对每家银行，汇总其所有名称变体在上半和下半的出现次数
    3. 判定条件（须同时满足出现次数条件 + 任一分布条件）：
       前置条件) 该银行的任一名称变体在标题或全文中合计出现 ≥ MIN_NAME_OCCURRENCES 次
       a) 上半合计出现 ≥ MIN_UPPER 次 AND 下半合计出现 ≥ MIN_LOWER 次
       b) 该银行的任一名称变体出现在"标题"中 AND 全文合计出现 ≥ MIN_UPPER 次
    4. 记录每家银行的匹配详情（各变体出现次数、上下半分布、标题出现情况）

    假阳性排除（基于国际顶刊标准）：
    5. 否定模式排除：如"务农行列""交通行业"等完整短语匹配到银行简称时排除
    6. 短名歧义消解：对 ≤2 字的银行简称（如"工行""中行"），检查前后
       context_window 个字符的上下文，命中排除词则排除该匹配

学术依据：
    [Hassan2019]  Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019).
                  "Firm-Level Political Risk: Measurement and Effects."
                  Quarterly Journal of Economics, 134(4), 2135–2202.
                  → 企业级文本暴露度测度: 关键词在文本中的出现频次作为风险暴露指标
                  → 本模块的 "article × bank" 展开逻辑对标其 firm-level exposure 框架

    [Gentzkow2019] Gentzkow, M., Kelly, B. & Taddy, M. (2019).
                   "Text as Data." Journal of Economic Literature, 57(3), 535–574.
                   → 文本分类的规范化框架: 关键词匹配 + 分布条件 + 阈值敏感性
                   → 本模块的多条件判定逻辑和阈值设计遵循该方法论标准

性能优化：
    - 使用 Aho-Corasick 自动机一次线性扫描匹配所有银行名称变体
    - 复杂度从 O(文本长度 × 银行数 × 变体数) 降至 O(文本长度)
    - 否定模式同样使用 AC 自动机实现 O(n) 匹配
    - joblib 并行分批处理
    - 减少不必要的 DataFrame 深拷贝

输入：
    阶段1输出的 Parquet 文件（``00_preprocessing.parquet``）

输出：
    仅保留判定为银行新闻的记录，追加 ``is_bank_news`` 和 ``matched_banks_info`` 列
"""

import os
import re
import json
import os
import sys
import time
import pandas as pd
import ahocorasick
from collections import Counter, defaultdict
from joblib import Parallel, delayed
import psutil

# Phase 6a: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(_HERE)
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import setup_logging, log_memory_usage, log_stage_summary
from news_process.core.reporting import safe_save_preview_csv
from news_process.core.text.ahocorasick import (
    load_bank_names, load_exclusion_patterns, is_match_excluded,
    analyze_bank_matches,
)

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "11_news_bank"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从配置中提取银行新闻判断参数
BANK_NEWS_PARAMS = CONFIG.get('bank_news_classification', {})

# 分割比例和阈值
# “上下半分布”策略的设计依据: 如果一家银行在文章的上半和下半都被提及,
# 说明该银行是文章的核心主题(而非仅在某处一笔带过)。
# 参考: Hassan et al. (2019, QJE) Firm-Level Political Risk
SPLIT_RATIO = BANK_NEWS_PARAMS.get('split_ratio', 0.5)
MIN_UPPER = BANK_NEWS_PARAMS.get('min_occurrences_upper', 1)
MIN_LOWER = BANK_NEWS_PARAMS.get('min_occurrences_lower', 1)
MIN_NAME_OCCURRENCES = BANK_NEWS_PARAMS.get('min_name_occurrences', 3)


# ============================================================================
# 2. 银行名称加载与 Aho-Corasick 自动机构建（委托至 utils.aho_corasick）
# ============================================================================

# 全局加载银行名称数据和 AC 自动机（模块导入时执行一次）
BANKS, BANK_AC_AUTOMATON, VARIANT_TO_BANK = load_bank_names(
    CONFIG['paths'].get('bank_names_file', '')
)

# 全局加载否定模式数据（模块导入时执行一次）
_exclusion_file = CONFIG['paths'].get(
    'bank_name_exclusions_file',
    os.path.join(os.path.dirname(CONFIG['paths'].get('bank_names_file', '')),
                 'bank_name_exclusions.json')
)
NEGATION_AC, SHORT_NAME_EXCLUSIONS, CONTEXT_WINDOW = load_exclusion_patterns(
    _exclusion_file
)


def _analyze_single_article(content: str, title: str = "") -> dict:
    """使用共享 AC 自动机分析单篇文章，返回银行匹配详情。

    委托至 utils.aho_corasick.analyze_bank_matches，使用全局加载的
    AC 自动机和否定模式配置。
    """
    return analyze_bank_matches(
        content=content,
        title=title,
        bank_ac=BANK_AC_AUTOMATON,
        banks_list=BANKS,
        split_ratio=SPLIT_RATIO,
        negation_ac=NEGATION_AC,
        short_name_exclusions=SHORT_NAME_EXCLUSIONS,
        context_window=CONTEXT_WINDOW,
        min_name_occurrences=MIN_NAME_OCCURRENCES,
        min_upper=MIN_UPPER,
        min_lower=MIN_LOWER,
    )


# ============================================================================
# 3. 批量处理与统计
# ============================================================================

def classify_batch(df_batch: pd.DataFrame) -> tuple:
    """对单个批次执行银行新闻分类。

    在 joblib 子进程中运行，直接在传入的 DataFrame 上操作
    （子进程拥有独立数据副本，无需额外 copy）。

    Args:
        df_batch: 待分类的 DataFrame 批次。

    Returns:
        tuple: (processed_df, stats_dict)
    """
    stats = {
        'total': 0,
        'is_bank_news_true': 0,
        'is_bank_news_false': 0,
        'is_bank_news_with_title': 0,
        'bank_article_counts': Counter(),
        'bank_title_article_counts': Counter(),
        'negation_excluded_total': 0,
        'short_name_excluded_total': 0,
    }

    if df_batch.empty:
        return df_batch, stats

    df = df_batch.copy()
    stats['total'] = len(df)

    # 批量分析：zip 迭代比 apply 快约 20%
    contents = df['内容'].fillna('').astype(str).values
    titles = df['标题'].fillna('').astype(str).values if '标题' in df.columns else [''] * len(df)
    results = [_analyze_single_article(c, t) for c, t in zip(contents, titles)]

    # === 提早展开: 每个合格银行生成独立物理行 (Firm-Document Level) ===
    # 设计意图: 一篇新闻可能同时提及多家银行(如“工行和建行签署合作协议”),
    # 需要为每家银行生成一条独立记录, 以便后续阶段对每家银行
    # 独立计算实体特异性情感分数。
    # 这种“展开”会增加行数, 但这是计量经济学中 Firm-Document 级别分析的标准做法。
    expanded_rows = []
    original_columns = list(df.columns)

    for row_i in range(len(df)):
        r = results[row_i]
        if not r['is_bank_news']:
            continue

        # 提取满足阈值的银行（复用原有判定逻辑，确保一致性）
        qualified_banks = [
            b for b in r['matched_banks']
            if b.get('total_with_title', b['total_count']) >= MIN_NAME_OCCURRENCES
               and ((b['upper_count'] >= MIN_UPPER and b['lower_count'] >= MIN_LOWER)
                    or (b['in_title'] and b['total_count'] >= MIN_UPPER))
        ]
        if not qualified_banks:
            continue

        all_qualified_names = [b['bank_name'] for b in qualified_banks]
        row_data = df.iloc[row_i]

        for bank_info in qualified_banks:
            new_row = row_data.to_dict()
            new_row['is_bank_news'] = True
            new_row['target_bank'] = bank_info['bank_name']
            new_row['co_mentioned_banks'] = ';'.join(
                [n for n in all_qualified_names if n != bank_info['bank_name']]
            )
            new_row['target_bank_in_title'] = int(bank_info.get('in_title', False))
            new_row['matched_banks_info'] = json.dumps(
                r['matched_banks'], ensure_ascii=False
            )
            # 保留 matched_bank_names 以兼容下游过渡期
            new_row['matched_bank_names'] = ';'.join(all_qualified_names)
            # --- 提及密度(Value-weighted Exposure, Hassan 2019 QJE) ---
            # mention_density = 提及次数 / 文档总字数
            # 这个指标反映了银行在新闻中的“占比”, 可用于加权情感分析。
            # 更高的密度意味着该银行更可能是新闻的核心主题。
            doc_len = max(len(str(row_data.get('内容', ''))), 1)
            new_row['doc_length'] = doc_len
            new_row['target_bank_mention_count'] = bank_info['total_count']
            new_row['mention_density'] = bank_info['total_count'] / doc_len
            expanded_rows.append(new_row)

    # 构建展开后的 DataFrame
    if expanded_rows:
        df = pd.DataFrame(expanded_rows)
    else:
        # 边界情况：该批次无任何银行新闻
        extra_cols = ['is_bank_news', 'target_bank', 'co_mentioned_banks',
                      'target_bank_in_title', 'matched_banks_info', 'matched_bank_names',
                      'doc_length', 'target_bank_mention_count', 'mention_density']
        df = pd.DataFrame(columns=original_columns + extra_cols)

    # 统计
    n_bank_news_articles = len(set(
        i for i in range(len(results)) if results[i]['is_bank_news']
    ))
    stats['is_bank_news_true'] = n_bank_news_articles
    stats['is_bank_news_false'] = stats['total'] - n_bank_news_articles
    stats['is_bank_news_with_title'] = sum(
        1 for r in results
        if r['is_bank_news'] and any(b.get('in_title', False) for b in r['matched_banks'])
    )

    # 汇总排除计数（遍历原始 results）
    for result in results:
        stats['negation_excluded_total'] += result['negation_excluded']
        stats['short_name_excluded_total'] += result['short_name_excluded']

    # 各银行文章计数（使用展开后的 target_bank）
    if not df.empty and 'target_bank' in df.columns:
        for bank_name in df['target_bank']:
            stats['bank_article_counts'][bank_name] += 1
        if 'target_bank_in_title' in df.columns:
            title_mask = df['target_bank_in_title'] == 1
            for bank_name in df.loc[title_mask, 'target_bank']:
                stats['bank_title_article_counts'][bank_name] += 1

    return df, stats


def merge_stats(stats_list: list) -> dict:
    """合并多个批次的统计结果。

    Args:
        stats_list: 各批次返回的统计字典列表。

    Returns:
        dict: 合并后的统计字典。
    """
    merged = {
        'total': 0,
        'is_bank_news_true': 0,
        'is_bank_news_false': 0,
        'is_bank_news_with_title': 0,
        'bank_article_counts': Counter(),
        'bank_title_article_counts': Counter(),
        'negation_excluded_total': 0,
        'short_name_excluded_total': 0,
    }
    for s in stats_list:
        merged['total'] += s['total']
        merged['is_bank_news_true'] += s['is_bank_news_true']
        merged['is_bank_news_false'] += s['is_bank_news_false']
        merged['is_bank_news_with_title'] += s.get('is_bank_news_with_title', 0)
        merged['bank_article_counts'] += s['bank_article_counts']
        merged['bank_title_article_counts'] += s.get('bank_title_article_counts', Counter())
        merged['negation_excluded_total'] += s['negation_excluded_total']
        merged['short_name_excluded_total'] += s['short_name_excluded_total']
    return merged


def log_classification_report(stats: dict, logger):
    """输出银行新闻分类统计报告。

    Args:
        stats:  合并后的统计字典。
        logger: 日志记录器。
    """
    logger.info("=" * 70)
    logger.info("===        银行新闻判断统计报告        ===")
    logger.info("=" * 70)

    total = stats['total']
    true_count = stats['is_bank_news_true']
    pct = (true_count / total * 100) if total > 0 else 0.0

    logger.info(f"总记录数: {total:,}")
    logger.info(f"判定为银行新闻: {true_count:,} ({pct:.2f}%)")
    if true_count > 0:
        with_title = stats.get('is_bank_news_with_title', 0)
        no_title = true_count - with_title
        logger.info(f"  - 包含标题匹配: {with_title:,} 篇 ({with_title/true_count*100:.2f}%)")
        logger.info(f"  - 仅靠正文匹配: {no_title:,} 篇 ({no_title/true_count*100:.2f}%)")
    logger.info(f"判定为非银行新闻: {stats['is_bank_news_false']:,} ({100 - pct:.2f}%)")
    logger.info(
        f"判定参数: 内容分割比例={SPLIT_RATIO}, "
        f"上半最低出现={MIN_UPPER}次, 下半最低出现={MIN_LOWER}次, "
        f"前置最少出现={MIN_NAME_OCCURRENCES}次, 标题出现时全文最少={MIN_UPPER}次即可"
    )
    logger.info(f"银行名称配置: 共 {len(BANKS)} 家银行")

    # 假阳性排除统计
    neg_count = stats.get('negation_excluded_total', 0)
    short_count = stats.get('short_name_excluded_total', 0)
    total_excluded = neg_count + short_count
    logger.info("-" * 70)
    logger.info("假阳性排除统计:")
    logger.info(f"  否定模式排除匹配数: {neg_count:,}")
    logger.info(f"  短名歧义消解排除匹配数: {short_count:,}")
    logger.info(f"  合计排除匹配数: {total_excluded:,}")

    # 按银行名称分组统计 所有
    logger.info("-" * 70)
    logger.info("判定为银行新闻的报道篇数 (按银行名称 所有):")
    bank_top = stats['bank_article_counts'].most_common()
    if bank_top:
        for rank, (bank, count) in enumerate(bank_top, 1):
            title_count = stats.get('bank_title_article_counts', {}).get(bank, 0)
            logger.info(f"  {rank:>3}. {bank}: {count:,} 篇 (其中标题匹配 {title_count:,} 篇)")
    else:
        logger.info("  (无匹配)")

    unique_banks = len(stats['bank_article_counts'])
    logger.info("-" * 70)
    logger.info(f"涉及不同银行数: {unique_banks}")
    logger.info("=" * 70)


# ============================================================================
# 4. 主函数
# ============================================================================

def main():
    """银行新闻判断阶段主入口。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # 检查数据加载状态
    logger.info(f"银行名称分组数据: 共 {len(BANKS)} 家银行")
    if BANKS:
        total_variants = sum(len(b['variants']) for b in BANKS)
        logger.info(f"  名称变体总数: {total_variants}")
        logger.info(f"  前5家银行: {[b['bank_name'] for b in BANKS[:5]]}...")
        logger.info(f"  AC 自动机状态: {'已构建' if BANK_AC_AUTOMATON else '未构建'}")
    logger.info(
        f"分割比例: {SPLIT_RATIO}, "
        f"上半最低出现次数: {MIN_UPPER}, 下半最低出现次数: {MIN_LOWER}, "
        f"最少出现次数: {MIN_NAME_OCCURRENCES}"
    )

    if not BANKS:
        logger.error("银行名称分组数据为空！无法执行分类。")
        return

    # 定义输入输出
    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_00_preprocessing'])
    output_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_11_bank_news'])

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        return

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # --- 执行并行分类 ---
    logger.info("开始执行银行新闻判断（Aho-Corasick + 并行）...")

    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    if n_jobs <= 0:
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    # 分批
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]
    logger.info(f"批次处理: 共 {num_batches} 个批次，每批次 {batch_size} 行，使用 {n_jobs} 个并行进程")

    # 并行执行
    results = Parallel(n_jobs=n_jobs)(
        delayed(classify_batch)(batch) for batch in df_batches
    )

    # 合并结果
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
            columns=list(df.columns) + ['is_bank_news', 'matched_banks_info']
        )

    # 统计报告
    merged_stats = merge_stats(all_stats)
    log_classification_report(merged_stats, logger)
    
    # 提早展开已在 classify_batch 中完成过滤，所有行均为银行新闻
    processed_df = processed_df.reset_index(drop=True)
    after_count = len(processed_df)
    logger.info(f"展开后 Firm-Document 对总数: {after_count:,} 行")
    
    # --- 保存结果 ---
    logger.info(f"正在将处理结果写入 {output_path}...")
    processed_df.to_parquet(output_path, index=False)

    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)

    # 阶段摘要
    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
