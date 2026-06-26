"""
news_process.pipeline.filtering.news_bank — 阶段11：银行新闻判断
=================================================================

功能：
    判断每篇新闻是否关于某家银行的中文新闻报道。

判断策略：
    1. 将"内容"按字符数等分为上下两半（默认 50%/50%）
    2. 对每家银行，汇总其所有名称变体在上半和下半的出现次数
    3. 判定条件（须同时满足出现次数条件 + 任一分布条件）：
       前置条件) 该银行的任一名称变体在标题或全文中合计出现 ≥ MIN_NAME_OCCURRENCES 次
       a) 上半合计出现 ≥ MIN_UPPER 次 AND 下半合计出现 ≥ MIN_LOWER 次
       b) 该银行的任一名称变体出现在"标题"中 AND 全文合计出现 ≥ MIN_UPPER 次
    4. 记录每家银行的匹配详情（各变体出现次数、上下半分布、标题出现情况），
       并按 firm-document 级展开：每家合格银行生成一条独立物理行

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
    阶段 00 输出的 Parquet 文件（``00_preprocessing.parquet``）

输出：
    仅保留判定为银行新闻的记录，并展开为 firm-document 级（每家合格银行生成一条
    独立物理行，故输出行数可多于输入）。每行追加 9 列：``is_bank_news``、
    ``target_bank``、``co_mentioned_banks``、``target_bank_in_title``、
    ``matched_banks_info``、``matched_bank_names``、``doc_length``、
    ``target_bank_mention_count``、``mention_density``
    （仅当某批次无任何银行新闻的空回退路径才退化为 is_bank_news / matched_banks_info 两列）

迁移说明 (Phase 7a-1)：
    本模块由原 root script ``11_news_bank.py`` body 迁入。原 root 现为 thin
    shim，仅负责 ``python 11_news_bank.py`` 历史调用契约。规范调用方式：
        python -m news_process.pipeline.filtering.news_bank

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 11_news_bank.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: `00_preprocessing.parquet` (config 键 output_00_preprocessing) 的 内容/标题/版面/页号/作者 等列。

**处理步骤** (`main` → joblib `Parallel` 分批 → `classify_batch` → 委托 `core.text.ahocorasick.analyze_bank_matches`):
1. 按 `parallel.batch_size` (默认 5000) 切批, `n_jobs` 默认满核-1 (psutil), joblib 并行。
2. 每篇文章按 `split_ratio` (默认 0.5) 把'内容'按字符数等分上下两半; 用全局 Aho-Corasick 自动机一次线性扫描所有银行别名 (`load_bank_names` → BANKS/BANK_AC_AUTOMATON/VARIANT_TO_BANK)。
3. **firm-document 展开**: 一篇可同时命中多家银行 → 每家合格银行生成一条独立物理行 (故输出行数可多于输入)。

**关键算法/判定公式** (`analyze_bank_matches`, 每家银行; classify_batch 复用同一阈值):
- 前置: 任一别名 总计 (含标题, `total_with_title`) ≥ `MIN_NAME_OCCURRENCES` (默认 2);
- 分布条件 (满足其一): (a) 上半 ≥ `MIN_UPPER` (默认 1) ∧ 下半 ≥ `MIN_LOWER` (默认 1); 或 (b) 别名出现在标题 ∧ 全文合计 `total_count` ≥ `MIN_UPPER`。
- **不对称口径的假阳性排除**: ① 否定模式排除 ('务农行列''交通行业'命中'农行' → 排除, NEGATION_AC); ② 短名歧义消解 (≤2 字简称如'工行''中行', 检查前后 context_window 字符, 命中排除词则剔除该次匹配)。这套排除规则与 stage 13 ctx/ss 锚定共用同一事实源 (core/text/ahocorasick)。

**输出列** (合格行追加 9 列): `is_bank_news`, `target_bank`, `co_mentioned_banks`, `target_bank_in_title` (int 0/1, 显著性/β 信号, 刻意保留非情感轨), `matched_banks_info` (json), `matched_bank_names`, `doc_length`, `target_bank_mention_count`, `mention_density` (= total_count / max(len(str(内容)),1), 即 提及次数/文档字符数, value-weighted exposure)。另经 `compute_news_salience` 追加 NEWS_SALIENCE_KEYS (版位/导语命中 target_in_lead/署名 has_byline 等, 用全部别名 + 同款否定/短名排除)。
注: classify_batch 内某批次无任何银行新闻时, 空回退 DataFrame 仍含全部 9 列 + NEWS_SALIENCE_KEYS (见 classify_batch 空批次分支); 仅当**全部批次**均无银行新闻时, main() 最终回退到只含 is_bank_news/matched_banks_info 两列的空 DataFrame (见 main() 全空回退分支)。

**外部依赖/确定性**: 纯 CPU (ahocorasick / joblib / psutil), 无 LLM/Embedding/网络。确定性: 给定语料+词典逐位可复现。词典文件纳入 parquet 血缘 input_hashes (防词典内容篡改而路径不变导致完整性校验失明)。

**DAG 位置**: 上游 stage 00, 下游 stage 12 (金科判定) 读其输出。学术依据 Hassan 2019 QJE (firm-level exposure) + Gentzkow-Kelly-Taddy 2019 JEL (Text as Data; 见模块 docstring)。

■ 白话说明

**这一步在做什么**: 从全部新闻里挑出'真的在讲某家银行'的那些, 并标注是哪家银行。打个比方: 像图书管理员把一摞剪报里凡是讲'工商银行''建设银行'的挑出来, 还在每篇上贴标签写明主角是谁; 如果一篇同时认真讲了工行和建行, 就复印成两份各自归档 (这就是'按银行展开成独立行')。

**为什么需要它**: 后面研究的是'每家银行每年的媒体形象', 所以必须先确定每篇新闻属于哪家银行。难点在于中文简称会误伤——'农行'可能其实是'务农行列', '中行'可能是'居中行驶'。这步特意加了两道'防误判'闸门 (否定短语排除 + 短名前后文检查), 还要求银行名在文章上半段和下半段都出现 (说明是主角而非一笔带过), 才算数。

**做得好不好的影响**: 这步决定了每家银行'有多少篇新闻'——这是整个银行-年度面板的样本来源。挑太松会把不相关的稿件算进某家银行 (污染情感、注意力指标, 系数失真); 挑太严会漏掉真实报道 (样本变小、估计不稳)。它顺手算的'提及密度''是否上标题'还会被后面用作加权和稳健性信号, 影响主回归与显著性。
========================================================================
"""

import json
import os
import platform
import sys
import time
from collections import Counter

import ahocorasick  # noqa: F401  (原 body 中的 import, 部分被 AC 工具间接使用)
import pandas as pd
import psutil
from joblib import Parallel, delayed

# Phase 7a-1: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (子进程通过 ``python -m news_process.pipeline.filtering.news_bank`` 启动时
#  通常已正确解析, 这里是 belt-and-suspenders 防御)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)
from news_process.core.reporting import safe_save_preview_csv
from news_process.core.text.ahocorasick import (
    analyze_bank_matches,
    load_bank_names,
    load_exclusion_patterns,
)
from news_process.pipeline.filtering.news_salience import (
    NEWS_SALIENCE_KEYS,
    compute_news_salience,
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
MIN_NAME_OCCURRENCES = BANK_NEWS_PARAMS.get('min_name_occurrences', 2)


# ============================================================================
# 2. 银行名称加载与 Aho-Corasick 自动机构建（委托至 core.text.ahocorasick）
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

# fix(omni-g-entity-12, 2026-06-11): 规范行名 → 全部名称变体 查找表, 供
# news_salience.target_in_lead 全变体匹配 (替代仅规范名的 5 倍跨行低估)。
_BANK_VARIANTS = {b['bank_name']: b['variants'] for b in BANKS}


def _analyze_single_article(content: str, title: str = "") -> dict:
    """使用共享 AC 自动机分析单篇文章，返回银行匹配详情。

    委托至 core.text.ahocorasick.analyze_bank_matches，使用全局加载的
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

        # fix(omni-g-entity-13, 2026-06-11): 缺失单元格 (NaN/None) → '' (而非
        # str() 出的字面 'nan'), 让 news_salience 缺失路径正确触发。
        def _cell(col: str, _row=row_data) -> str:
            v = _row.get(col, '')
            return '' if pd.isna(v) else str(v)

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
            # ── 新闻体裁显著性 (批 #8–#10, 2026-06-05): 版位/导语/署名, $0 纯解析 ──
            # 在 stage 11 物化 (此处原始 版面/页号/作者 列俱在, 且早于 noise 剥离, 见
            # news_salience docstring); 经 encode 聚合到 bank-year。
            # fix(omni-g-entity-12/13, 2026-06-11):
            #   - 缺失源字段经 _cell 转 '' 走 news_salience 的 NaN 路径,
            #     不再被 str() 成字面 'nan' 文本 (原 'nan' 作者会被误计 has_byline=1);
            #   - target_in_lead 传入全部名称变体 + stage 11 同款否定/短名排除。
            new_row.update(compute_news_salience(
                _cell('版面'), _cell('页号'), _cell('作者'),
                _cell('标题'), _cell('内容'), bank_info['bank_name'],
                aliases=_BANK_VARIANTS.get(bank_info['bank_name']),
                negation_ac=NEGATION_AC,
                short_name_exclusions=SHORT_NAME_EXCLUSIONS,
                context_window=CONTEXT_WINDOW,
            ))
            expanded_rows.append(new_row)

    # 构建展开后的 DataFrame
    if expanded_rows:
        df = pd.DataFrame(expanded_rows)
    else:
        # 边界情况：该批次无任何银行新闻
        extra_cols = ['is_bank_news', 'target_bank', 'co_mentioned_banks',
                      'target_bank_in_title', 'matched_banks_info', 'matched_bank_names',
                      'doc_length', 'target_bank_mention_count', 'mention_density',
                      *NEWS_SALIENCE_KEYS]
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
    logger.info(f"判定为银行新闻: {true_count:,} ({pct4(pct, fraction=False)})")
    if true_count > 0:
        with_title = stats.get('is_bank_news_with_title', 0)
        no_title = true_count - with_title
        logger.info(f"  - 包含标题匹配: {with_title:,} 篇 ({pct4(with_title / true_count)})")
        logger.info(f"  - 仅靠正文匹配: {no_title:,} 篇 ({pct4(no_title / true_count)})")
    logger.info(f"判定为非银行新闻: {stats['is_bank_news_false']:,} ({pct4(100 - pct, fraction=False)})")
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

def _log_environment_and_methodology(input_path: str, output_path: str) -> None:
    """打印 ① 项目/环境信息 ② 输入/输出文件 ③ 运行配置 ④ 方法论依据(含 DOI)。

    目标 (日志富集, 2026-06-24, 用户要求"在日志中提供尽可能多的项目/运行期/结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    11_news_bank.log, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    方法论引文逐字取自经核验参考文献注册表 (VERIFIED_REFERENCES), 含可访问 DOI 链接。
    """
    try:
        preview_path = output_path.replace('.parquet', '.csv')
        bank_file = CONFIG['paths'].get('bank_names_file', '(默认)')
        excl_file = CONFIG['paths'].get('bank_name_exclusions_file', _exclusion_file)
        parallel_cfg = CONFIG.get('parallel', {})
        total_variants = sum(len(b['variants']) for b in BANKS) if BANKS else 0

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (银行新闻判定, STAGES_MAIN; firm-document 级展开)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) "
                    "| 版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU (ahocorasick/joblib/psutil), 无 LLM·网络·API ($0)")
        logger.info("     · 确定性: 给定语料+词典逐位可复现; 词典文件纳入 parquet 血缘 "
                    "input_hashes (防词典内容篡改而路径不变致完整性校验失明)。")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:     {input_path} (config 键 output_00_preprocessing)")
        logger.info(f"     · 输出:     {output_path} (config 键 output_11_bank_news)")
        logger.info(f"     · 预览:     {preview_path}")
        logger.info(f"     · 银行词典: {bank_file}")
        logger.info(f"     · 排除词典: {excl_file}")

        logger.info("  ⚙ 运行配置 (config::bank_news_classification + config::parallel)")
        logger.info(f"     · 分布判定: split_ratio={sig4(SPLIT_RATIO)} | MIN_UPPER={MIN_UPPER} "
                    f"| MIN_LOWER={MIN_LOWER} | MIN_NAME_OCCURRENCES={MIN_NAME_OCCURRENCES}")
        logger.info(f"     · 词典规模: 银行 {len(BANKS):,} 家 | 名称变体合计 {total_variants:,} "
                    f"| AC 自动机={'已构建' if BANK_AC_AUTOMATON else '未构建'}")
        logger.info(f"     · 假阳性闸门: 否定模式 AC={'已加载' if NEGATION_AC else '缺失'} "
                    f"| 短名排除词 {len(SHORT_NAME_EXCLUSIONS):,} 项 "
                    f"| context_window={CONTEXT_WINDOW} 字符")
        logger.info(f"     · 并行: batch_size={parallel_cfg.get('batch_size', 5000):,} "
                    f"| n_jobs={parallel_cfg.get('n_jobs', -1)} (joblib)")

        logger.info("  📖 方法论依据 (核心方法/构念学术出处; 逐字取自经核验参考文献注册表)")
        logger.info("     · 企业级文本暴露度 (article×bank 展开 + mention_density value-weighted "
                    "exposure 对标 firm-level exposure 框架):")
        logger.info("       Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                    "Firm-level political risk: Measurement and effects. The Quarterly Journal "
                    "of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021")
        logger.info("     · 文本分类规范框架 (关键词匹配 + 分布条件 + 阈值敏感性, 多条件判定逻辑"
                    "与阈值设计遵循 Text-as-Data 方法论标准):")
        logger.info("       Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal "
                    "of Economic Literature, 57(3), 535-574. "
                    "https://doi.org/10.1257/jel.20181020")
        logger.info("     · 关键词/词表命中构建 firm-level 文本暴露度的近期 (2023-2024) 同范式实例 "
                    "(本模块以银行别名命中量化每家银行的媒体暴露, 与下列 firm-level 文本暴露测度"
                    "同一方法谱系, 均以词表/种子词命中 → 企业级暴露指标):")
        logger.info("       Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level "
                    "climate change exposure. The Journal of Finance, 78(3), 1449-1498. "
                    "https://doi.org/10.1111/jofi.13219 "
                    "(白话: ML 关键词发现 + 二元组命中构 firm-level climate attention, 词表"
                    "构建标准模板)")
        logger.info("       Wu, D. A. (2024). Text-based measure of supply chain risk exposure. "
                    "Management Science, 70(7), 4781-4801. "
                    "https://doi.org/10.1287/mnsc.2023.4927 "
                    "(白话: 种子词嵌入 + 词袋构 firm-level 文本暴露并以波动率验证, 同法 2024 "
                    "近期实例)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法论信息打印失败 (不影响处理): {e}")


def main():
    """银行新闻判断阶段主入口。"""
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # ── 黄金范式【功能】banner: 让 11_news_bank.log 自带说明书 ──────────────
    logger.info("=" * 72)
    logger.info("阶段 11: 银行新闻判断 (Aho-Corasick 实体匹配 + 上下半分布判定)")
    logger.info("=" * 72)
    logger.info("【功能】从 stage 00 全部预处理新闻里挑出'真的在讲某家银行'的稿件,")
    logger.info("        并标注主角是哪家银行; 一篇同时认真讲多家银行时按 firm-document")
    logger.info("        展开为多条独立物理行。产出 11_bank_news.parquet (银行-文档级),")
    logger.info("        是整个银行-年度面板的样本来源, 也是下游金科/三轨情感的公共上游。")
    logger.info("【方法】每篇按 split_ratio 等分上下两半, 全局 AC 自动机一次线性扫描全部")
    logger.info("        银行别名; 判定 = 前置(任一别名含标题合计 >= MIN_NAME_OCCURRENCES)")
    logger.info("        ∧ 分布条件(上半>=MIN_UPPER ∧ 下半>=MIN_LOWER, 或 别名在标题 ∧ 全文")
    logger.info("        合计>=MIN_UPPER); 另设两道假阳性闸门: 否定模式排除('务农行列'误中")
    logger.info("        '农行') + 短名歧义消解(<=2字简称查前后 context_window 字符)。")
    logger.info(
        f"        当前阈值: split_ratio={SPLIT_RATIO}, MIN_UPPER={MIN_UPPER}, "
        f"MIN_LOWER={MIN_LOWER}, MIN_NAME_OCCURRENCES={MIN_NAME_OCCURRENCES}。"
    )
    logger.info("【判读】银行新闻占比偏高=判定可能过松(噪声稿件混入, 污染情感/注意力);")
    logger.info("        偏低=可能过严(漏真实报道, 样本变小估计不稳); 排除计数>0 说明假阳性")
    logger.info("        闸门在生效, 越多说明中文简称歧义越被有效拦截。")
    logger.info("【确定性】纯 CPU (ahocorasick/joblib/psutil), 无 LLM/Embedding/网络;")
    logger.info("        给定语料+词典逐位可复现, 词典文件已纳入 parquet 血缘 input_hashes。")

    # 定义输入输出 (env/方法论 banner 需引用路径, 故先解析)
    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_00_preprocessing'])
    output_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_11_bank_news'])

    # ── 黄金范式【环境/输入输出/配置/方法论(含 DOI)】banner ───────────────────
    _log_environment_and_methodology(input_path, output_path)

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
        raise SystemExit(1)

    # input_path / output_path 已在 banner 前解析 (供 env/方法论 banner 引用)

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    # ── per-phase 墙钟计时 (日志富集, golden-safe; 仅服务日志, 不改产物) ──
    _t_load0 = time.time()
    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    _t_load = time.time() - _t_load0
    logger.info(f"已加载 {input_rows:,} 行数据。(⏱ 加载耗时 {sig4(_t_load)} 秒)")
    log_memory_usage(logger, "数据加载后")

    # --- 执行并行分类 ---
    _t_clf0 = time.time()
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

    _t_clf = time.time() - _t_clf0
    logger.info(
        f"并行分类 + firm-document 展开 + 合并完成。(⏱ 分类阶段耗时 {sig4(_t_clf)} 秒; "
        f"{sig4(input_rows / _t_clf) if _t_clf > 0 else 'n/a'} 行/秒)"
    )

    # 统计报告
    merged_stats = merge_stats(all_stats)
    log_classification_report(merged_stats, logger)

    # 提早展开已在 classify_batch 中完成过滤，所有行均为银行新闻
    processed_df = processed_df.reset_index(drop=True)
    after_count = len(processed_df)
    logger.info(f"展开后 Firm-Document 对总数: {after_count:,} 行")

    # ── 黄金范式【结果分析】: 取真实产出指标 + 对照阈值/预期方向给判读 ────────
    # 注: 下述变量均为只服务于日志的局部计算, 不回写 df / 不改任何产物。
    # crash-guard: 整个分析块在最终写盘 (save_parquet_with_metadata) 之前执行,
    # 若取数/算指标异常 (缺键/除零/格式化) 绝不能拖垮阶段丢产物 → 整体 try/except。
    try:
        _total_seen = merged_stats.get('total', 0)
        _bank_true = merged_stats.get('is_bank_news_true', 0)
        _bank_pct = (_bank_true / _total_seen * 100) if _total_seen > 0 else 0.0
        _with_title = merged_stats.get('is_bank_news_with_title', 0)
        _title_pct = (_with_title / _bank_true * 100) if _bank_true > 0 else 0.0
        _neg_excl = merged_stats.get('negation_excluded_total', 0)
        _short_excl = merged_stats.get('short_name_excluded_total', 0)
        _total_excl = _neg_excl + _short_excl
        _unique_banks = len(merged_stats.get('bank_article_counts', {}))
        _expand_ratio = (after_count / _bank_true) if _bank_true > 0 else 0.0

        logger.info("-" * 72)
        logger.info("【结果分析】对本次银行新闻判定的关键产出指标逐项解读 (对照阈值/预期方向):")
        logger.info(
            f"  · 银行新闻判定率: {_bank_true:,}/{_total_seen:,} = {pct4(_bank_pct, fraction=False)} "
            f"(文章去重计)。判读: 中文报纸语料里多数稿件并非银行报道, 该比率通常远低于"
            f" 50%; 若异常高(>50%)需警惕判定过松(噪声混入), 异常低(接近 0)需警惕过严或"
            f"词典/输入异常。"
        )
        logger.info(
            f"  · 标题命中占比: {_with_title:,}/{_bank_true:,} = {pct4(_title_pct, fraction=False)} "
            f"(银行名出现在标题的银行新闻)。判读: 偏高=报道更聚焦该行(target_bank_in_title"
            f"=1 这类显著性/β 信号更密集); 偏低=多为正文一笔带过, 下游加权权重更分散。"
        )
        logger.info(
            f"  · firm-document 展开比: 展开后 {after_count:,} 行 / 银行新闻 {_bank_true:,} "
            f"篇 = {sig4(_expand_ratio)} 行每篇。判读: >1 表示存在'一篇同时讲多家银行'被复制成"
            f"多行 (Hassan 2019 firm-level 标准做法); =1 则几乎每篇只命中单一银行。"
        )
        logger.info(
            f"  · 涉及不同银行数: {_unique_banks} 家 / 词典共 {len(BANKS)} 家。判读: 覆盖面"
            f"越广越说明样本不偏集于少数大行; 远低于词典规模说明多数银行在本语料无合格报道"
            f"(小样本/特定年份下属正常)。"
        )
        logger.info(
            f"  · 假阳性闸门拦截: 否定模式排除 {_neg_excl:,} 次 + 短名歧义消解 {_short_excl:,}"
            f" 次 = 合计 {_total_excl:,} 次。判读: >0 说明两道防误判闸门在生效(拦下'务农行列'"
            f"误中'农行'之类); 恒为 0 时若语料含大量银行简称, 需复核排除词典是否真正加载。"
        )

        # 优雅降级警告: 假阳性排除词典缺失 → 两道闸门失效
        if NEGATION_AC is None and not SHORT_NAME_EXCLUSIONS:
            logger.warning(
                "  ⚠ 假阳性排除配置 (bank_name_exclusions.json) 缺失或为空 → 否定模式 + "
                "短名歧义消解两道闸门均未生效, 银行简称误匹配风险升高 (优雅降级, 不中断), "
                "判定结果可能偏松, 请确认 paths.bank_name_exclusions_file 指向正确词典。"
            )

        # 小样本警告: 盘面 T=2 仅验证管道, 结论以全量为准
        if _total_seen > 0 and _bank_true < 1000:
            logger.info(
                f"  ⚠ 本次输入 {_total_seen:,} 行、银行新闻 {_bank_true:,} 篇属小样本 (盘面 "
                f"T=2 / 子样本); 上述比率仅用于验证管道正确性, 全量结论以 17M / T=18 实测为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # --- 保存结果 ---
    _t_write0 = time.time()
    logger.info(f"正在将处理结果写入 {output_path}...")
    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_00_preprocessing'])
    # audit S10/B 修复 (2026-05-30): 把决定银行分类结果的词典文件纳入血缘
    # input_files。否则编辑 bank_names.json / bank_name_exclusions.json (路径不变、
    # 内容变) 后, input_hashes 不变 → verify_data_integrity 假阳性 PASS, 对词典
    # 篡改完全失明。compute_config_hash 只哈希 config dict (含路径字符串), 不读
    # 词典内容, 故必须把词典文件本身纳入 input_hashes。
    _lexicon_inputs = [
        CONFIG['paths'].get('bank_names_file'),
        CONFIG['paths'].get('bank_name_exclusions_file'),
    ]
    input_files = [input_file] + [
        p for p in _lexicon_inputs if p and os.path.exists(p)
    ]
    save_parquet_with_metadata(
        df=processed_df,
        output_path=output_path,
        stage_name="11_news_bank",
        config=CONFIG,
        input_files=input_files,
    )

    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)
    _t_write = time.time() - _t_write0
    logger.info(f"写盘 (parquet+血缘) + 预览 CSV 完成。(⏱ 写盘阶段耗时 {sig4(_t_write)} 秒)")

    # ── per-phase 计时汇总 (墙钟; 各子阶段 + 总耗时) ──
    try:
        _t_total = time.time() - stage_start
        logger.info("-" * 72)
        logger.info("⏱ 阶段计时汇总 (墙钟秒):")
        logger.info(f"     · 加载 parquet:        {sig4(_t_load)} 秒")
        logger.info(f"     · 并行分类+展开+合并:  {sig4(_t_clf)} 秒")
        logger.info(f"     · 写盘+预览:           {sig4(_t_write)} 秒")
        logger.info(f"     · 阶段总耗时:          {sig4(_t_total)} 秒")
        logger.info("-" * 72)
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"[阶段计时] 汇总打印异常, 跳过(不影响产物): {_e}")

    # 阶段摘要
    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
