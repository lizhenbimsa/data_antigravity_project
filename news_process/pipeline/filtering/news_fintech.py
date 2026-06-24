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
                   DOI: 10.16381/j.cnki.issn1003-207x.2021.1714

    [LoughranMcDonald2011] Loughran, T. & McDonald, B. (2011).
                   "When Is a Liability Not a Liability?" Journal of Finance,
                   66(1), 35–65.

性能优化：
    - 使用 Aho-Corasick 自动机一次线性扫描匹配所有关键词
    - 复杂度从 O(文本长度 × 关键词数) 降至 O(文本长度)
    - joblib 并行分批处理

输入：
    阶段 11 输出的 Parquet 文件（``11_bank_news.parquet``）

输出：
    1. 全量分类结果（含非金融科技新闻），保存为 12_news_fintech_full.parquet/.csv
    2. 仅保留判定为金融科技新闻的记录，追加分类结果列

迁移说明 (Phase 7a-2)：
    本模块由原 root script ``12_news_fintech.py`` body 迁入。
    规范调用方式：
        python -m news_process.pipeline.filtering.news_fintech

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 12_news_fintech.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: `11_bank_news.parquet` (config 键 output_11_bank_news) 全列 + 内容/标题。

**处理步骤** (`main` → joblib `Parallel` 分批 → `classify_batch` → 委托 `analyze_fintech_matches`):
1. 同 stage 11 的分批/并行框架 (batch_size 默认 5000, n_jobs 满核-1)。
2. 每篇按 split_ratio (默认 0.5) 按字符数等分上下半; 用全局 Aho-Corasick (`load_fintech_dict`, 1506 词金科词典) 一次线性扫描。

**关键判定公式** (`analyze_fintech_matches`, 整篇判定——stage 12 **不再** firm-document 展开, 沿用 stage 11 已展开的行):
- 前置 (多样性): 标题或全文出现 ≥ `MIN_DISTINCT_KEYWORDS` (默认 2) 个**不同**金科词;
- 分布条件 (其一): (a) 全部词上半合计 ≥ `MIN_UPPER` (默认 1) ∧ 下半合计 ≥ `MIN_LOWER` (默认 1); 或 (b) 任一词在标题 ∧ 全文合计 ≥ `MIN_UPPER`。
- 金科侧为**裸 AC 匹配** (不做否定/短名排除), 与 stage 13 ss 轨'不对称口径'的金科侧一致 (单一事实源 core/text/ahocorasick)。

**输出列** (对每行追加 7 列): `is_fintech_news` (bool), `fintech_total_count`, `fintech_upper_count`, `fintech_lower_count`, `fintech_in_title` (供下游显著性, 刻意保留), `fintech_distinct_keywords`, `fintech_keyword_details` (json)。

**双产出语义**:
- `12_fintech_news_full.parquet`: 写在过滤**之前** (见 main() full 落盘段), 含全部 stage 11 银行新闻行 (含非金科) + 上述 7 列, 与 stage 11 输出 1:1 行对应 (供人工验证抽样)。注: 任务简述'_full=过滤前全量银行新闻(与 11 1:1)'成立——它就是'银行新闻全集 + 金科分类标记', 未做金科过滤。下游 controls.py 用其'减面板后去重'部分作 fintech_share 分母的一块 (见 memory fintech-share-denominator)。
- `12_fintech_news.parquet`: 对 full 做 `is_fintech_news==True` 过滤后的子集 (见 main() 过滤落盘段), 即'既是银行新闻又是金科新闻'的稿件, 供 stage 13+ 三轨/强度/情感消费。

**外部依赖/确定性**: 纯 CPU (ahocorasick/joblib/psutil), 无 LLM/网络, 逐位可复现。fintech_dict.json 纳入两个 parquet 的 input_hashes 血缘 (防词典内容篡改失明)。

**DAG 位置**: 上游 stage 11, 下游 stage 13 (ctx_materializer) 读 12_fintech_news.parquet。学术依据 胡俊等 2024 中国管理科学 + Loughran-McDonald 2011 JF (见模块 docstring)。

■ 白话说明

**这一步在做什么**: 在'已经是银行新闻'的稿件里, 再判断哪几篇是真的在谈'金融科技'(手机银行、移动支付、大数据风控、区块链这类)。它会输出两份: 一份是'银行新闻全集, 每篇都打上是不是金科的标记'(供抽查核对), 另一份是'确实是金科的那个子集'(交给后面用)。打个比方: 先有一摞银行剪报, 这步给每篇盖个章——'涉金融科技'或'不涉', 然后把盖章'涉'的单独抽出来一叠。

**为什么需要它**: 整个项目研究的是'媒体怎么报道银行与金融科技的关系', 所以必须先框定'银行×金科'这个话题范围。判定要求一篇里出现至少 2 个不同的金科词 (而不是偶然蹦一个), 避免把只顺嘴提一句'扫码支付'的普通银行新闻误算进来。

**做得好不好的影响**: 这步圈定的金科新闻子集, 是后面所有'银行金融科技注意力/态度/实质性'指标的原料。框太宽会把噪声稿件灌进来, 框太窄会漏掉真实的金科报道, 都会让银行-年度面板里的核心解释变量偏移。它保留的那份'全量+标记'还充当 fintech_share (银行新闻里金科占比) 指标的分母来源之一, 直接影响该比例型变量的口径; 同时它的金科词典就是后面'银行和金科出现在同一句'(第三条文本轨) 用来认定共现的金科词源。
========================================================================
"""

import json
import os
import platform
import sys
import time
from collections import Counter

import ahocorasick  # noqa: F401
import pandas as pd
import psutil
from joblib import Parallel, delayed

# Phase 7a-2: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
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
from news_process.core.text.ahocorasick import analyze_fintech_matches, load_fintech_dict

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
MIN_DISTINCT_KEYWORDS = FINTECH_NEWS_PARAMS.get('min_distinct_keywords', 2)


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
    logger.info(f"判定为金融科技新闻: {true_count:,} ({pct4(pct, fraction=False)})")
    if true_count > 0:
        with_title = stats.get('is_fintech_news_with_title', 0)
        no_title = true_count - with_title
        logger.info(f"  - 包含标题匹配的篇数: {with_title:,} 篇 ({pct4(with_title/true_count)})")
        logger.info(f"  - 仅靠正文匹配的篇数: {no_title:,} 篇 ({pct4(no_title/true_count)})")
    logger.info(f"判定为非金融科技新闻: {stats['is_fintech_news_false']:,} ({pct4(100 - pct, fraction=False)})")
    logger.info(
        f"判定参数: 内容分割比例={sig4(SPLIT_RATIO)}, "
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

def _log_environment_and_config(input_path: str, output_path: str, full_output_path: str,
                                total_keywords: int, n_jobs: int, batch_size: int) -> None:
    """打印项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集, 2026-06-24)。

    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、依据哪些学术方法"一次性
    落进 12_news_fintech.log, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    引文逐字取自经核验参考文献注册表 (VERIFIED_REFERENCES.md), 零伪造。
    """
    try:
        preview_path = output_path.replace('.parquet', '.csv')
        fintech_file = CONFIG['paths'].get('fintech_dict_file', '(默认)')

        # ① 🧭 项目 / 环境信息
        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (金融科技新闻判断, STAGES_MAIN; "
                    "在'已是银行新闻'稿件里再框定'银行×金科'话题范围)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板), "
                    "当前版本 v3.11.1")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · ahocorasick: {getattr(ahocorasick, '__version__', '?')} "
                    "(确定性来源 = AC 自动机 + fintech_dict.json 内容)")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·网络·API ($0) / 逐位可复现")

        # ② 📂 输入 / 输出文件
        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:        {input_path} (config 键 output_11_bank_news)")
        logger.info(f"     · 输出(full):  {full_output_path} (过滤前全量银行新闻+金科标记, 与 11 1:1)")
        logger.info(f"     · 输出(filter):{output_path} (is_fintech_news==True 子集, 交 stage 13+)")
        logger.info(f"     · 预览:        {preview_path}")
        logger.info(f"     · 金科词典:    {fintech_file} (纳入两 parquet 的 input_hashes 血缘)")

        # ③ ⚙ 运行配置 (config 键 fintech_news_classification + parallel)
        logger.info("  ⚙ 运行配置 (config::fintech_news_classification / parallel)")
        logger.info(f"     · 分割比例 split_ratio={sig4(SPLIT_RATIO)} | "
                    f"上半最低 MIN_UPPER={MIN_UPPER} | 下半最低 MIN_LOWER={MIN_LOWER}")
        logger.info(f"     · 前置多样性门 MIN_DISTINCT_KEYWORDS={MIN_DISTINCT_KEYWORDS} 个不同金科词")
        logger.info(f"     · 金科词典词数={total_keywords:,} | AC 自动机={'已构建' if FINTECH_AC_AUTOMATON else '未构建'}")
        logger.info(f"     · 并行: batch_size={batch_size:,} | n_jobs={n_jobs} (joblib Parallel)")

        # ④ 📖 方法论依据 (引文逐字取自 VERIFIED_REFERENCES.md, 含 DOI 可访问链接)
        logger.info("  📖 方法论依据 (参考文献)")
        logger.info("     · 金科测度构念: 胡俊, 李强, 戴嘉诚, & 曾勇. (2024). 基于文本分析的商业银行"
                    "金融科技测度及赋能效果检验. 中国管理科学, 32(1), 31–41. "
                    "https://doi.org/10.16381/j.cnki.issn1003-207x.2021.1714")
        logger.info("       → 白话: 用金融科技词典在中文报道里做关键词测度, 框定'银行×金科'话题, "
                    "本阶段沿用该法的词频/分布判定思路。")
        logger.info("     · 词典法文本分析: Loughran, T., & McDonald, B. (2011). When is a "
                    "liability not a liability? Textual analysis, dictionaries, and 10-Ks. "
                    "The Journal of Finance, 66(1), 35-65. "
                    "https://doi.org/10.1111/j.1540-6261.2010.01625.x")
        logger.info("       → 白话: 词典法做金融文本测度的经典范式 (须多样性/分布门压噪声), "
                    "本阶段以 ≥2 不同词 + 上下半分布门避免'顺嘴一句'误判。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    """金融科技新闻判断阶段主入口。"""
    stage_start = time.time()
    # 运行期各主要子阶段墙钟耗时累计 (末尾汇总; 纯日志, golden-safe)
    phase_durations: dict[str, float] = {}
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")

    # threshold_number_fidelity 修复: 词数动态取自 len(FINTECH_KEYWORDS), 不再硬编码 "1506",
    # 以免日后词典增删后 banner 散文与实际词数漂移失真。total_keywords 上移到 banner 之前。
    total_keywords = len(FINTECH_KEYWORDS)

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    logger.info("=" * 72)
    logger.info(f"阶段 12: 金融科技新闻判断 + 全量分类结果 (胡俊等 2024 中国管理科学 / Aho-Corasick {total_keywords} 词)")
    logger.info("=" * 72)
    logger.info("【功能】在'已是银行新闻'的稿件里, 再判断哪几篇真在谈金融科技 (手机银行/移动支付/")
    logger.info("        大数据风控/区块链等), 框定全项目'银行×金科'话题范围。产出两份: full=")
    logger.info("        银行新闻全集+金科标记 (供抽查 & fintech_share 分母来源之一); filtered=")
    logger.info("        is_fintech_news==True 的子集 (交 stage 13+ 三轨/强度/情感消费)。")
    logger.info("【方法】每篇按 split_ratio 等分上下半, 用全局 Aho-Corasick 一次线性扫描金科词典;")
    logger.info(f"        判定 = 前置多样性 (标题或全文 ≥{MIN_DISTINCT_KEYWORDS} 个不同金科词) ∧ 分布条件其一")
    logger.info(f"        ((a) 上半合计≥{MIN_UPPER} ∧ 下半合计≥{MIN_LOWER}; 或 (b) 任一词在标题 ∧ 全文≥{MIN_UPPER})。")
    logger.info("        金科侧裸 AC 匹配 (不做否定/短名排除), 与 stage 13 _ss 轨金科侧同一事实源。")
    logger.info("【判读】判定率 (true%) 适中为佳: 过高=框太宽噪声灌入 (核心解释变量被稀释), 过低=")
    logger.info(f"        漏掉真实金科报道 (核心变量偏移); 多样性前置 (≥{MIN_DISTINCT_KEYWORDS} 不同词) 即用于压制'顺嘴一句'误判。")
    logger.info("【确定性】纯 CPU (ahocorasick/joblib/psutil), 无 LLM/网络, 逐位可复现; fintech_dict.json")
    logger.info("          纳入两 parquet 的 input_hashes 血缘 (防词典篡改失明)。")

    if not FINTECH_KEYWORDS:
        logger.error("金融科技词典为空！无法执行分类。")
        raise SystemExit(1)

    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_11_bank_news'])
    output_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames']['output_12_fintech_news'])
    full_output_path = os.path.join(
        CONFIG['paths']['output_dir'],
        CONFIG['filenames'].get('output_12_fintech_full', '12_fintech_news_full.parquet')
    )

    # 并行参数解析 (上移到 ENV/CONFIG block 之前, 便于一次性披露)
    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    if n_jobs <= 0:
        n_jobs = max(1, psutil.cpu_count(logical=True) - 1)

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论依据 (日志富集 2026-06-24)
    logger.info("")
    _log_environment_and_config(input_path, output_path, full_output_path,
                                total_keywords, n_jobs, batch_size)
    logger.info("")

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"正在从 {input_path} 加载数据...")
    _t = time.time()
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    phase_durations['①加载输入'] = time.time() - _t
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    logger.info("开始执行金融科技新闻判断（Aho-Corasick + 并行）...")

    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]
    logger.info(f"批次处理: 共 {num_batches} 个批次，每批次 {batch_size} 行，使用 {n_jobs} 个并行进程")

    _t = time.time()
    results = Parallel(n_jobs=n_jobs)(
        delayed(classify_batch)(batch) for batch in df_batches
    )
    phase_durations['②AC并行扫描判定'] = time.time() - _t

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
    # full_output_path 已在 main() 开头解析 (供 ENV/CONFIG block 一次性披露)。
    logger.info(f"正在将全量分类结果（含非金融科技新闻）写入 {full_output_path}...")
    _t = time.time()
    # 使用数据版本控制保存 full 版本
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_11_bank_news'])
    # audit S10/B 修复 (2026-05-30): fintech 分类由 fintech_dict.json (1506 关键词)
    # 决定; 把它纳入血缘 input_files, 否则编辑词典内容 (路径不变) 后 input_hashes
    # 不变 → verify_data_integrity 对词典篡改失明。
    _fintech_dict = CONFIG['paths'].get('fintech_dict_file')
    input_files = [input_file] + (
        [_fintech_dict] if _fintech_dict and os.path.exists(_fintech_dict) else []
    )
    save_parquet_with_metadata(
        df=processed_df,
        output_path=full_output_path,
        stage_name="12_news_fintech",
        config=CONFIG,
        input_files=input_files,
    )
    full_preview_path = full_output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, full_preview_path, logger)
    phase_durations['③写盘 full+预览'] = time.time() - _t
    logger.info(f"全量分类结果已保存: {len(processed_df):,} 行（供人工验证抽样使用）")

    # --- 只保留金融科技新闻 ---
    before_count = len(processed_df)
    processed_df = processed_df[processed_df['is_fintech_news'] == True].reset_index(drop=True)
    after_count = len(processed_df)
    logger.info(
        f"过滤非金融科技新闻: {before_count:,} → {after_count:,} 行"
        f"（移除 {before_count - after_count:,} 行）"
    )

    # 结果分析 — 写入日志: 判定率/标题占比/词典命中分布逐项判读 (仿 39c)。
    # crash-guard: 本块在 filtered parquet 最终写盘 (下方 save_parquet_with_metadata)
    # 之前执行, 整体 try/except, 任何诊断异常都不得拖垮 stage 产物 (golden-safe)。
    try:
        total_n = merged_stats['total']
        true_n = merged_stats['is_fintech_news_true']
        with_title_n = merged_stats.get('is_fintech_news_with_title', 0)
        true_pct = (true_n / total_n * 100) if total_n > 0 else 0.0
        title_pct = (with_title_n / true_n * 100) if true_n > 0 else 0.0
        kw_hit = merged_stats['keyword_article_counts']
        n_distinct_kw_hit = len(kw_hit)  # 实际触发判定的不同金科词数 (覆盖广度)
        kw_coverage = (n_distinct_kw_hit / total_keywords * 100) if total_keywords > 0 else 0.0
        top_kw = kw_hit.most_common(1)[0] if kw_hit else None
        # corpus-level 集中度 (非 per-article 多样性): 最高频触发词占所有触发次数的份额。
        # 注意此处与单篇 MIN_DISTINCT_KEYWORDS=2 门是【不同量纲】(全语料 broad vs 单篇 diversity),
        # 故不复用 2 词门做广度判读; 仅作 log-only 诊断, 不回写 df, golden-safe。
        # top_share 越高 = 主题越集中于个别热词 (疑单点驱动); 经验阈值 0.30, 仅启发, 非硬 gate。
        breadth_top_share_warn = 0.30  # log-only 局部阈值, 不进 config / 不回写 df
        total_kw_hits = sum(kw_hit.values())
        top_share = (top_kw[1] / total_kw_hits) if (top_kw is not None and total_kw_hits > 0) else 0.0

        logger.info("-" * 72)
        logger.info("【结果分析】金科判定产出指标判读 (越接近预期方向越健康):")
        # ① 输入对账: 与上游 stage 11 行数 1:1
        logger.info(
            f"  ① 输入对账: 加载 {input_rows:,} 行 (stage 11 银行新闻); 分类后 full={before_count:,} 行"
            f" → {'1:1 对齐 (好)' if before_count == input_rows else '⚠ 与输入不一致, 检查并行 concat'}"
        )
        # ② 判定率: 适中为佳, 过高=框太宽, 过低=漏报
        if true_pct >= 60.0:
            verdict_pct = "⚠ 偏高 (疑框太宽, 噪声稿件可能灌入)"
        elif true_pct < 1.0:
            verdict_pct = "⚠ 偏低 (疑词典/阈值过严, 可能漏报真实金科报道)"
        else:
            verdict_pct = "适中 (好)"
        logger.info(
            f"  ② 金科判定率: {true_n:,}/{total_n:,} = {pct4(true_pct, fraction=False)} → {verdict_pct}"
        )
        # ③ 标题匹配占比: 标题命中 = 强信号, 占比越高判定越可信
        logger.info(
            f"  ③ 标题命中占比 (金科篇内): {with_title_n:,}/{true_n:,} = {pct4(title_pct, fraction=False)}"
            f" → {'含标题强信号, 判定可信度高 (好)' if title_pct >= 30.0 else '多靠正文匹配 (信号偏弱, 关注)' if true_n > 0 else '无金科篇'}"
        )
        # ④ 词典覆盖广度 (corpus-level): 触发判定的不同金科词越多 + 最高频词份额越低,
        #    主题越分散 (非单点关键词驱动)。判据用 corpus-level 集中度 top_share, 与单篇
        #    MIN_DISTINCT_KEYWORDS 门是不同量纲, 不复用 2 词门 (见上方注释)。
        if total_kw_hits == 0:
            verdict_breadth = "无触发词 (无金科篇, 无法判读广度)"
        elif top_share > breadth_top_share_warn:
            verdict_breadth = (
                f"⚠ 触发高度集中 (最高频词占 {pct4(top_share)} > {pct4(breadth_top_share_warn)}), "
                "疑单点关键词主导, 主题不分散"
            )
        else:
            verdict_breadth = f"广度健康, 非单点驱动 (最高频词占 {pct4(top_share)}, 好)"
        logger.info(
            f"  ④ 词典命中广度: {n_distinct_kw_hit:,}/{total_keywords:,} 个金科词曾触发判定 "
            f"({pct4(kw_coverage, fraction=False)}) → {verdict_breadth}"
        )
        if top_kw is not None:
            logger.info(f"     最高频触发词: '{top_kw[0]}' ({top_kw[1]:,} 篇)")
        # ⑤ 下游交付量: filtered 子集是 stage 13+ 全部三轨/强度/情感的原料
        logger.info(
            f"  ⑤ 下游交付 (filtered 子集): {after_count:,} 篇交 stage 13 (ctx 物化)"
            f" → {'有可消费样本 (好)' if after_count > 0 else '⚠ 零金科篇, 下游三轨链将空跑'}"
        )
        # 优雅降级 / 边界警告
        if not FINTECH_AC_AUTOMATON:
            logger.warning(
                "  ⚠ FINTECH_AC_AUTOMATON 未构建 (词典加载失败/为空): 所有判定将退化, "
                "金科子集可能异常; 须核查 fintech_dict_file 路径与内容。"
            )
        if after_count < 100:
            logger.info(
                f"  ⚠ 金科子集仅 {after_count:,} 篇 (盘面 T=2 小样本): 上述比率仅验证管道正确性, "
                "全量结论以 17M/T=18 实测为准。"
            )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    logger.info(f"正在将处理结果写入 {output_path}...")
    _t = time.time()
    # 使用数据版本控制保存 filtered 版本
    from news_process.core.data_versioning import save_parquet_with_metadata
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_11_bank_news'])
    # audit S10/B 修复 (2026-05-30): 同 full 版本, fintech_dict 纳入血缘。
    _fintech_dict = CONFIG['paths'].get('fintech_dict_file')
    input_files = [input_file] + (
        [_fintech_dict] if _fintech_dict and os.path.exists(_fintech_dict) else []
    )
    save_parquet_with_metadata(
        df=processed_df,
        output_path=output_path,
        stage_name="12_news_fintech",
        config=CONFIG,
        input_files=input_files,
    )

    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)
    phase_durations['④写盘 filtered+预览'] = time.time() - _t

    # ⏱ 各子阶段墙钟耗时汇总 (纯日志, golden-safe)
    try:
        logger.info("  ⏱ 各子阶段墙钟耗时 (秒, 4 位有效数字):")
        for _name, _dur in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_dur)} 秒")
        _total_phase = sum(phase_durations.values())
        logger.info(f"     · 子阶段合计: {sig4(_total_phase)} 秒 "
                    f"(占总阶段 {pct4(_total_phase / max(time.time() - stage_start, 1e-9))})")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  [计时汇总] 异常, 跳过(不影响产物): {_e}")

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
