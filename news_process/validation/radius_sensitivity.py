"""
news_process.validation.radius_sensitivity — 窗口半径敏感性检验

迁移说明 (Phase 7b)：
    本模块由原 root script ``65_radius_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.radius_sensitivity``

===============================================================

功能：
    对 entity_context 的 sentence_radius 参数进行系统性敏感性分析，
    验证情感分析结果对窗口大小选择的稳健性。

检验设计：
    - 对 radius ∈ {0, 1, 2, 3} 四组设定，分别提取实体上下文
    - 使用与生产 22_tone_words 完全一致的 6 套基准中文情感词典
      (jiang/yao/bian/du/you/loughran) 重新计算情感得分和标签
      (2026-06-20 起本旁路 loader 已对齐生产 union 口径: 含第 6 部
       loughran_mcdonald_zh_2026 + positive∩negative 跨类重叠词保留并两侧计数,
       用户决策 2026-06-24 逆转双侧剔除)
    - 计算跨半径的标签一致性、得分相关性和分布统计
    - 生成学术论文附录级别的报告（LaTeX 表格 + 可视化图表）

学术依据：
    Hassan et al. (2019, QJE) Proximity-based Attribution 的参数敏感性检验。
    顶刊标准要求对关键方法论参数进行 robustness check。

输入：
    阶段21输出（经 LLM 语义精筛后的数据，含 target_bank 列）

输出：
    1. 敏感性分析报告（JSON + LaTeX 表格）
    2. 可视化图表（标签分布对比、相关性热力图）
    3. 控制台/日志完整统计输出

白话:
    ctx 轨提取"银行名前后几句话"时, "几句"是个人为参数 (生产用前后 1 句)。
    本检验把窗口改成 0/1/2/3 句各算一遍词典情感分, 看结果变不变: 邻近
    窗口 (1 vs 2/3) 高度一致就说明参数选择不要紧; r=0 (只留银行名所在
    那一句) 是故意的极端压力测试, 它偏差大是预期内的 — 上下文被砍没了,
    不能据此否定默认窗口。另注意"Kappa 悖论": 当 90% 以上文章都是同一个
    标签时, κ 会被数学机制压得很低, 此时一致率和相关系数更可靠。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 65_radius_sensitivity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**核心问题**: ctx 轨提取'银行名前后几句'时, 半径 (`sentence_radius`, 生产=1) 是人为参数。本阶段在 radius ∈ {0,1,2,3} (`RADII`) 上扫描, 验证词典情感结论对窗口大小是否稳健。

**输入 (订正)**: 优先 `21_tone_llms.parquet` (CONFIG['filenames']['output_21_tone_llms'] — 经 LLM 精筛、仅 llm_verified=True 的下游产物, 含 `target_bank` 列), 回退 `12_fintech_news.parquet`。⚠ 注意是 `21_tone_llms.parquet` 而非 `_full` 版本。必需列 `target_bank` + `内容`。

**处理步骤**:
1. 加载 6 套中文金融情感词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran; 正面+1/负面-1/政治正面+0.5; positive∩negative 跨类重叠词保留并两侧计数, 用户决策 2026-06-24 逆转双侧剔除), 注入 jieba (词典词+银行名+金科词+否定/程度/转折词)。2026-06-20 起本旁路 loader 已与生产 22_tone_words 的 6 词典 union 口径完全对齐 (含第 6 部 loughran_mcdonald_zh_2026)。
2. 对每篇文章, `analyze_single_article_multi_radius`: 每个 radius 调 `core.text.entity_context.extract_entity_context(sentence_radius=r, fallback_char_radius=150)` 提上下文 (未命中回退原文), jieba 分词, 对 6 词典各算 `_compute_sentiment_with_rules` (否定窗口翻转/程度副词缩放/转折增强/句末标点重置状态机, 与 22_tone_words 逐行对齐) → 归一化得分 + 三分类标签 (正/中/负, 阈值 ±0.1)。
3. 跨半径对比 (基准 r=1): 对每词典算标签一致率、Cohen's κ、Pearson/Spearman 相关、配对 t 检验 (ttest_1samp 得分差)。

**关键算法/公式**: 归一化得分 = total_score / (pos_count+neg_count)。Cohen's κ = (p_o−p_e)/(1−p_e)。零方差守卫 (radius-zerovar-guard, 2026-06-10): 常量分数 (词典零命中/空窗口/样本退化) 或 n≤2 下 pearsonr/spearmanr 置 NaN (语义=相关无定义), 下游裁决用 np.nanmin/np.nanmean (`_compute_pairwise_radius_corr` 热力图同款守卫, NaN 渲染为 'n/a')。'Kappa 悖论' 检测: 主导标签占比 ≥90% 时 κ 被数学压低, 此时一致率/Pearson 更可靠。判定: 邻近窗口 (r=1 vs 2/3) min κ≥0.80 = 强稳健; r=0 (仅实体所在句) 是故意极端压力测试, 偏差大属预期。

**外部依赖**: jieba (必需, 缺则 raise ImportError); scipy.stats; matplotlib (经 HAS_MATPLOTLIB 守卫, 缺则跳图)。无 LLM/缓存。无显式 timeout。确定性: 纯词典+确定提取, 无随机性 (不抽样, 全量处理)。

**学术依据**: Hassan et al. (2019, QJE) proximity-based attribution 参数敏感性。

■ 白话说明

**这一步在做什么**: 判断一篇长新闻对某银行是褒是贬时, 流水线不读整篇, 只截取'银行名字出现的那句话, 加上下各 N 句'这一小段来打分 (现在 N=1, 即前后各 1 句)。这个'前后几句'的窗口大小是人定的。这一步把窗口改成 0/1/2/3 句各算一遍情感分, 看分数变不变。

**为什么需要它**: 防审稿人质疑'你只截前后 1 句, 换 2 句结果会不会完全不同?'。如果 1 句和 2/3 句算出来高度一致 (相关 ≥0.8、标签几乎不变), 就证明窗口怎么选都不影响结论。其中 0 句 (只留银行名那一句、上下文全砍掉) 是故意做的极端压力测试, 它偏差大是正常的, 不能拿它否定默认设置。

**对面板和论文的影响**: ctx 轨 (实体上下文情感) 是 P1 主线论文的主变量来源。窗口若选得不稳, 银行情感打分就会随'截多少句'飘忽, 银行-年度面板里的语调变量就不可信。这一步给出的是'情感测量对截取范围稳健'的附录证据, 是 ctx 主结果可信度的支柱之一。
========================================================================
"""

import json
import logging
import os
import platform
import sys
import time
from collections import Counter

import numpy as np
import pandas as pd
from scipy import stats as scipy_stats

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/radius_sensitivity.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
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

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)
except ImportError:
    raise ImportError("请安装 jieba: pip install jieba")

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "65_radius_sensitivity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 检验参数
RADII = [0, 1, 2, 3]                    # 待检验的窗口半径
FALLBACK_CHAR_RADIUS = 150               # 字符级回退窗口（与原始设定一致）

# v3.6.0 (Plan E P7 C1): 多轨标记 — 当前实现仍为词典法单轨 (用 '内容' 全文重提
# ctx 在不同 radius 下的得分). 真正"多轨敏感性" 要求在 _full / _ctx / _ss 各跑一
# 遍整个 RADII grid, 输出 65_radius_sensitivity_{full,ctx,ss}.json 各一份。
# 注(三轨, 2026-06-14): radius 扫描本身是 track-agnostic 的窗口半径参数扫描 (只动
# 提取半径, 不切换 LLM 情感轨), 故 _ss 第三轨同 _ctx 一样落入下方待实施 TODO; 本轮
# 三轨化无需改本模块的扫描逻辑, 仅同步术语 双轨→多轨。
# 多轨敏感性扫描 (full + ctx + ss 各跑一遍 RADII grid) 为待实施项 (TODO; 由 RUN_MULTI_TRACK 开关控制)。
# 当前模块的 radius 扫描已经隐式覆盖 ctx 提取参数, 半成品多轨。
RUN_MULTI_TRACK = False  # 占位开关, 尚未接线 (main() 未分支于此); 多轨扫描见上方 TODO, 翻 True 暂不生效

# 从 22_tone_words 复用的情感参数
SENTIMENT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_words', {})
NEGATION_WORDS = frozenset(SENTIMENT_PARAMS.get('negation_words', []))
DEGREE_WORDS = SENTIMENT_PARAMS.get('degree_words', {})
ADVERSATIVE_WORDS = frozenset(SENTIMENT_PARAMS.get('adversative_words', []))
ADVERSATIVE_BOOST = float(SENTIMENT_PARAMS.get('adversative_boost', 1.5))
NEGATION_WINDOW = SENTIMENT_PARAMS.get('negation_window', 2)
POS_THRESHOLD = SENTIMENT_PARAMS.get('pos_threshold', 0.1)
NEG_THRESHOLD = SENTIMENT_PARAMS.get('neg_threshold', -0.1)

# 句末标点集合（遇到时重置转折/否定/程度状态，确保作用域限定为当前句）
SENTENCE_END_MARKERS = frozenset(SENTIMENT_PARAMS.get('sentence_end_markers', ['。', '！', '？', '!', '?', '；', ';']))

# 词典文件路径
TONE_DICTS_FILE = CONFIG['paths'].get(
    'tone_dicts_file',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'tone_dicts.json')
)


# ============================================================================
# 2. 从 22_tone_words.py 复用的核心函数（避免导入时的副作用）
# ============================================================================

# 列前缀别名: loughran_mcdonald_zh_2026 → 'loughran' (镜像生产 tone_words.DICT_COLUMN_ALIAS;
# 此处本地复制以避免 import 22_tone_words 触发模块级副作用, 见上方 §2 节标题)。
_DICT_COLUMN_ALIAS = {'loughran_mcdonald_zh_2026': 'loughran'}

# 跨类重叠词「两侧计数」注册表 (与生产 22_tone_words 一致, 用户决策 2026-06-24 逆转双侧剔除)。
# 键 = 列前缀别名, 值 = 该词典 positive∩negative 同时出现的词集。由 load_all_dictionaries 重建。
_BOTH_SIDED_BY_DICT: dict[str, frozenset[str]] = {}


def load_all_dictionaries() -> list[tuple[str, dict[str, float]]]:
    """从 tone_dicts.json 加载与 22_tone_words 完全一致的 6 套中文情感词典 (jiang/yao/bian/du/you/loughran), 复用其逐句规则逻辑。2026-06-20 起本旁路 loader 已对齐生产 union 口径: 含第 6 部 loughran_mcdonald_zh_2026 + positive∩negative 跨类重叠词保留并两侧计数 (用户决策 2026-06-24 逆转双侧剔除, 与生产一致), 不再是早期刻意保留的 5 套子集。"""
    logger.info(f"正在从 {TONE_DICTS_FILE} 加载情感词典...")

    all_dict_data = {}
    if os.path.exists(TONE_DICTS_FILE):
        try:
            with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
                all_dict_data = json.load(f)
            # 与生产 tone_words 一致: 顶层须为 JSON 对象, 否则优雅降级为空
            # (防 list 型配置在 .get() 处抛 AttributeError)。
            if not isinstance(all_dict_data, dict):
                logger.error(f"词典文件格式错误: 期望 JSON 对象, 实际为 {type(all_dict_data).__name__}")
                all_dict_data = {}
        except Exception as e:
            logger.error(f"加载词典文件失败: {e}")

    _BOTH_SIDED_BY_DICT.clear()
    dictionaries = []
    dict_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018',
                 'loughran_mcdonald_zh_2026']

    for dict_key in dict_keys:
        entry = all_dict_data.get(dict_key, {})
        alias = _DICT_COLUMN_ALIAS.get(dict_key, dict_key)
        d = {}
        # positive∩negative 跨类重叠词「保留并两侧计数」(用户决策 2026-06-24, 逆转双侧剔除),
        # 与生产 22_tone_words 一致; sorted 保证 dict 插入序确定 (可复现性)。
        pos_words = {str(w).strip() for w in entry.get('positive', []) if str(w).strip()}
        neg_words = {str(w).strip() for w in entry.get('negative', []) if str(w).strip()}
        cross_overlap = pos_words & neg_words
        if cross_overlap:
            logger.info(
                f"  {dict_key}: positive∩negative 跨类重叠 {len(cross_overlap)} 词保留并两侧计数 "
                f"(用户决策 2026-06-24, 逆转双侧剔除): {sorted(cross_overlap)}")
            _BOTH_SIDED_BY_DICT[alias] = frozenset(cross_overlap)
        for word in sorted(pos_words - cross_overlap):
            d[word] = 1.0
        for word in sorted(neg_words - cross_overlap):
            d[word] = -1.0
        for word in sorted(cross_overlap):
            d[word] = 1.0  # 占位幅值; 两侧计数取 abs (见 _compute_sentiment_with_rules both_sided)
        # 政治正面词 (du_2022 特有) 以 0.5 权重加入, 不覆盖已有正面/负面/重叠词。
        for word in entry.get('political_positive', []):
            word = str(word).strip()
            if word and word not in d:
                d[word] = 0.5
        dictionaries.append((alias, d))

        both_cnt = len(cross_overlap)
        pos_cnt = len(pos_words - cross_overlap)
        neg_cnt = len(neg_words - cross_overlap)
        _both_str = f", 跨类两侧计数={both_cnt}" if both_cnt else ""
        logger.info(f"  {dict_key}: {len(d)} 个词汇 (正面={pos_cnt}, 负面={neg_cnt}{_both_str})")

    return dictionaries


def _compute_sentiment_with_rules(
    tokens: list[str], sentiment_dict: dict[str, float],
    both_sided_words: frozenset = frozenset(),
) -> tuple[float, float, int, int]:
    """语言学规则增强的词典情感计算。复用 22_tone_words.py 核心逻辑。

    both_sided_words: 跨类重叠词集 (与生产一致, 用户决策 2026-06-24「保留并两侧计数」):
        命中词同时计入 pos/neg、对 total_score 净贡献 0 → 拉向中性而非剔除。

    Returns:
        tuple: (raw_score, normalized_score, pos_count, neg_count)
    """
    total_score = 0.0
    pos_count = 0
    neg_count = 0
    negation_remaining = 0
    degree_multiplier = 1.0
    adversative_active = False

    for token in tokens:
        if token in SENTENCE_END_MARKERS:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue
        if token in ADVERSATIVE_WORDS:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue
        if token in NEGATION_WORDS:
            negation_remaining = NEGATION_WINDOW
            continue
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token]
            continue
        if token in sentiment_dict:
            base_score = sentiment_dict[token]
            if negation_remaining > 0:
                base_score = -base_score
            final_score = base_score * degree_multiplier
            if adversative_active:
                final_score *= ADVERSATIVE_BOOST
            if token in both_sided_words:
                # 跨类重叠词两侧计数: 净 0 贡献 total_score, pos/neg 各 +1 → 拉向中性 (与生产一致)
                pos_count += 1
                neg_count += 1
            else:
                total_score += final_score
                if final_score > 0:
                    pos_count += 1
                elif final_score < 0:
                    neg_count += 1
            degree_multiplier = 1.0
        else:
            degree_multiplier = 1.0
        if negation_remaining > 0:
            negation_remaining -= 1

    total_matched = pos_count + neg_count
    normalized_score = total_score / total_matched if total_matched > 0 else 0.0
    return total_score, normalized_score, pos_count, neg_count


def _score_to_label(normalized_score: float) -> str:
    """将归一化得分映射为情感标签。"""
    if normalized_score > POS_THRESHOLD:
        return "正面"
    elif normalized_score < NEG_THRESHOLD:
        return "负面"
    else:
        return "中性"


def _inject_custom_dicts_to_jieba(dictionaries):
    """将领域词汇注入 jieba 分词器。"""
    added = 0
    for _, sentiment_dict in dictionaries:
        for word in sentiment_dict:
            jieba.add_word(word)
            added += 1

    # 注入银行名称
    bank_path = CONFIG['paths'].get('bank_names_file', '')
    if bank_path and os.path.exists(bank_path):
        try:
            with open(bank_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            for bank in bank_data:
                if not isinstance(bank, dict):
                    continue
                # 修正：使用正确的字段名 bank_name（非 standard_name）
                std_name = bank.get('bank_name')
                if std_name:
                    jieba.add_word(str(std_name).strip())
                    added += 1
                for v in bank.get('variants', []):
                    if v:
                        jieba.add_word(str(v).strip())
                        added += 1
        except Exception as e:
            logger.warning(f"加载银行词典失败: {e}")

    # 注入金融科技词典
    fintech_path = CONFIG['paths'].get('fintech_dict_file', '')
    if fintech_path and os.path.exists(fintech_path):
        try:
            with open(fintech_path, 'r', encoding='utf-8') as f:
                fintech_data = json.load(f)
            if isinstance(fintech_data, list):
                for word in fintech_data:
                    if word:
                        jieba.add_word(str(word).strip())
                        added += 1
            elif isinstance(fintech_data, dict):
                for _, words_list in fintech_data.items():
                    if isinstance(words_list, list):
                        for word in words_list:
                            if word:
                                jieba.add_word(str(word).strip())
                                added += 1
        except Exception as e:
            logger.warning(f"加载金融科技词典失败: {e}")

    # 否定词、程度词、转折词
    for word in NEGATION_WORDS:
        jieba.add_word(word)
    for word in DEGREE_WORDS:
        jieba.add_word(word)
    for word in ADVERSATIVE_WORDS:
        jieba.add_word(word)

    logger.info(f"成功注入 {added} 个领域词汇到 jieba 分词器。")


# ============================================================================
# 3. 从 entity_context.py 复用的上下文提取（支持参数化 radius）
# ============================================================================

from news_process.core.text.entity_context import extract_entity_context, get_target_aliases

# ============================================================================
# 4. 敏感性分析核心引擎
# ============================================================================

def analyze_single_article_multi_radius(
    content: str,
    target_aliases: list[str],
    dictionaries: list[tuple[str, dict[str, float]]],
) -> dict[int, dict]:
    """对单篇文章，在多个 radius 下提取上下文并计算情感。

    Returns:
        dict: {radius: {dict_name + '_score': float, dict_name + '_label': str, 'context_len': int, ...}}
    """
    results = {}

    for radius in RADII:
        ctx = extract_entity_context(
            content, target_aliases,
            sentence_radius=radius,
            fallback_char_radius=FALLBACK_CHAR_RADIUS,
        )
        # 若未匹配到，回退到原文
        text_for_analysis = ctx if ctx else content
        context_len = len(text_for_analysis)
        full_len = len(content) if content else 1

        # 分词（共享 jieba 实例）
        tokens = [t for t in jieba.cut(text_for_analysis) if t.strip()]

        radius_result = {
            'context_len': context_len,
            'context_ratio': round(context_len / full_len, 4) if full_len > 0 else 1.0,
            'token_count': len(tokens),
            'context_empty': (ctx == ""),
        }

        # 对每个词典计算
        for dict_name, sentiment_dict in dictionaries:
            if not sentiment_dict:
                radius_result[f'{dict_name}_score'] = 0.0
                radius_result[f'{dict_name}_label'] = '中性'
                continue

            _bs = _BOTH_SIDED_BY_DICT.get(dict_name, frozenset())  # 跨类重叠词两侧计数 (与生产一致)
            _, norm_score, pos_cnt, neg_cnt = _compute_sentiment_with_rules(
                tokens, sentiment_dict, _bs)
            radius_result[f'{dict_name}_score'] = round(norm_score, 4)
            radius_result[f'{dict_name}_label'] = _score_to_label(norm_score)
            radius_result[f'{dict_name}_pos_count'] = pos_cnt
            radius_result[f'{dict_name}_neg_count'] = neg_cnt

        results[radius] = radius_result

    return results


# ============================================================================
# 5. 统计指标计算
# ============================================================================

def compute_label_agreement(labels_a: list[str], labels_b: list[str]) -> float:
    """计算两组标签的一致率。"""
    if not labels_a or len(labels_a) != len(labels_b):
        return 0.0
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    return agree / len(labels_a)


def compute_cohens_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    """计算 Cohen's Kappa。"""
    n = len(labels_a)
    if n == 0:
        return 0.0

    cats = sorted(set(labels_a) | set(labels_b))
    cat_idx = {c: i for i, c in enumerate(cats)}
    k = len(cats)

    matrix = np.zeros((k, k), dtype=int)
    for a, b in zip(labels_a, labels_b):
        matrix[cat_idx[a], cat_idx[b]] += 1

    p_o = np.trace(matrix) / n
    row_sums = matrix.sum(axis=1)
    col_sums = matrix.sum(axis=0)
    p_e = (row_sums * col_sums).sum() / (n * n)

    if p_e == 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def run_sensitivity_analysis(
    df: pd.DataFrame,
    dictionaries: list[tuple[str, dict[str, float]]],
) -> dict:
    """对整个数据集执行敏感性分析。

    Returns:
        dict: 完整的分析结果。
    """
    total = len(df)
    dict_names = [name for name, _ in dictionaries]

    # 预加载别名缓存
    bank_names_file = CONFIG['paths'].get('bank_names_file', '')
    alias_cache = {}

    # 收集每个 radius 下所有文章的结果
    per_radius_data = {r: [] for r in RADII}

    logger.info(f"正在对 {total:,} 篇文章执行 {len(RADII)} 组窗口半径敏感性检验...")

    process_start = time.time()
    report_interval = max(1, total // 10)

    for i, (_, row) in enumerate(df.iterrows()):
        target_bank = str(row.get('target_bank', ''))
        content = str(row.get('内容', ''))

        if not target_bank or not content.strip():
            # 无目标银行或空内容，所有 radius 产出相同的默认结果
            for r in RADII:
                empty_result = {'context_len': 0, 'context_ratio': 0, 'token_count': 0, 'context_empty': True}
                for dn in dict_names:
                    empty_result[f'{dn}_score'] = 0.0
                    empty_result[f'{dn}_label'] = '中性'
                per_radius_data[r].append(empty_result)
            continue

        # 获取别名
        if target_bank not in alias_cache:
            alias_cache[target_bank] = get_target_aliases(target_bank, bank_names_file)
        aliases = alias_cache[target_bank]

        # 多半径分析
        multi_result = analyze_single_article_multi_radius(content, aliases, dictionaries)
        for r in RADII:
            per_radius_data[r].append(multi_result[r])

        if (i + 1) % report_interval == 0 or (i + 1) == total:
            elapsed = time.time() - process_start
            speed = (i + 1) / elapsed if elapsed > 0 else 0
            logger.info(f"  进度: {i + 1:,}/{total:,} ({pct4((i + 1) / total)}) "
                        f"| 速度: {sig4(speed)} 文章/秒")

    total_elapsed = time.time() - process_start
    _avg_speed = total / total_elapsed if total_elapsed > 0 else 0.0
    logger.info(f"全部文章处理完成。耗时: {sig4(total_elapsed)}s, "
                f"平均速度: {sig4(_avg_speed)} 文章/秒")

    # ── 汇总统计 ──
    analysis_results = {
        'meta': {
            'total_articles': total,
            'radii_tested': RADII,
            'dictionaries': dict_names,
            'processing_time_seconds': round(total_elapsed, 1),
        },
        'per_radius': {},
        'cross_radius': {},
    }

    # 5.1 每个 radius 的基础统计
    for r in RADII:
        data_list = per_radius_data[r]
        r_stats = {
            'context': {
                'mean_char_len': round(np.mean([d['context_len'] for d in data_list]), 1),
                'mean_ratio': round(np.mean([d['context_ratio'] for d in data_list]), 4),
                'empty_count': sum(1 for d in data_list if d['context_empty']),
                'mean_token_count': round(np.mean([d['token_count'] for d in data_list]), 1),
            },
            'dictionaries': {},
        }
        for dn in dict_names:
            scores = [d[f'{dn}_score'] for d in data_list]
            labels = [d[f'{dn}_label'] for d in data_list]
            label_dist = Counter(labels)
            r_stats['dictionaries'][dn] = {
                'score_mean': round(np.mean(scores), 4),
                'score_std': round(np.std(scores), 4),
                'score_median': round(np.median(scores), 4),
                'label_distribution': {
                    '正面': label_dist.get('正面', 0),
                    '中性': label_dist.get('中性', 0),
                    '负面': label_dist.get('负面', 0),
                },
                'label_distribution_pct': {
                    '正面': round(label_dist.get('正面', 0) / total * 100, 2) if total > 0 else 0,
                    '中性': round(label_dist.get('中性', 0) / total * 100, 2) if total > 0 else 0,
                    '负面': round(label_dist.get('负面', 0) / total * 100, 2) if total > 0 else 0,
                },
            }
        analysis_results['per_radius'][str(r)] = r_stats

    # 5.2 跨半径对比（基准 = radius=1，即当前生产配置）
    baseline_radius = 1
    baseline_data = per_radius_data[baseline_radius]

    for r in RADII:
        if r == baseline_radius:
            continue
        compare_data = per_radius_data[r]
        comparison = {}

        for dn in dict_names:
            base_labels = [d[f'{dn}_label'] for d in baseline_data]
            comp_labels = [d[f'{dn}_label'] for d in compare_data]
            base_scores = [d[f'{dn}_score'] for d in baseline_data]
            comp_scores = [d[f'{dn}_score'] for d in compare_data]

            agreement = compute_label_agreement(base_labels, comp_labels)
            kappa = compute_cohens_kappa(base_labels, comp_labels)

            # Pearson 和 Spearman 相关
            # fix(radius-zerovar-guard, 2026-06-10 + review-closure F1/F4): 零方差(常量分数 —
            # 词典零命中/空实体窗口/T=2 退化样本)下 pearsonr/spearmanr 返 NaN 并发
            # ConstantInputWarning。本守卫显式把常量输入的相关定义为 **NaN**(语义正确: 相关
            # 无定义)。注: 兄弟 decay_sensitivity 选 0.0 sentinel (下游 builtin min/mean 安全),
            # 本模块选 NaN 并**同步把下游裁决聚合改 np.nanmin/np.nanmean**(见 §汇总段), 二者
            # 路线不同但均无静默污染; 勿误以为与 decay 行为逐位一致。
            if (len(base_scores) > 2
                    and float(np.std(base_scores)) > 0
                    and float(np.std(comp_scores)) > 0):
                pearson_r, pearson_p = scipy_stats.pearsonr(base_scores, comp_scores)
                spearman_r, spearman_p = scipy_stats.spearmanr(base_scores, comp_scores)
            else:
                pearson_r, pearson_p = (float('nan'), float('nan'))
                spearman_r, spearman_p = (float('nan'), float('nan'))

            # 均值差异的配对 t 检验
            score_diffs = [c - b for b, c in zip(base_scores, comp_scores)]
            if len(score_diffs) > 1 and np.std(score_diffs) > 0:
                t_stat, t_p = scipy_stats.ttest_1samp(score_diffs, 0)
            else:
                t_stat, t_p = 0.0, 1.0

            comparison[dn] = {
                'label_agreement': round(agreement, 4),
                'cohens_kappa': round(kappa, 4),
                'pearson_r': round(pearson_r, 4),
                'pearson_p': round(pearson_p, 6),
                'spearman_rho': round(spearman_r, 4),
                'spearman_p': round(spearman_p, 6),
                'mean_score_diff': round(np.mean(score_diffs), 4),
                'paired_t_stat': round(t_stat, 4),
                'paired_t_p': round(t_p, 6),
            }

        analysis_results['cross_radius'][f'r{baseline_radius}_vs_r{r}'] = comparison

        # 日志富集 (round 7): 逐对比组速览 — 计算完成即落 4 位有效数字汇总, 让 65_*.log
        # 在分析推进时实时反馈"窗口从 r=1 改到 r={r}"对各词典得分的撼动幅度 (纯日志,
        # 只读已算好的 comparison, 局部变量不回写任何产物 → golden-safe)。
        try:
            _ks = [comparison[dn]['cohens_kappa'] for dn in dict_names]
            _pes = [comparison[dn]['pearson_r'] for dn in dict_names]
            _ags = [comparison[dn]['label_agreement'] for dn in dict_names]
            _nan_pe = sum(1 for v in _pes if np.isnan(v))
            _pe_mean = float(np.nanmean(_pes)) if _nan_pe < len(_pes) else float('nan')
            logger.info(
                f"  [基准 r={baseline_radius} vs r={r}] 跨 {len(dict_names)} 词典汇总: "
                f"κ 均值={sig4(float(np.mean(_ks)))} (min={sig4(float(min(_ks)))}) | "
                f"Pearson 均值={sig4(_pe_mean)} | 标签一致率 均值={pct4(float(np.mean(_ags)))}"
                + (f" | ⚠ {_nan_pe} 词典零方差→Pearson 置 NaN" if _nan_pe else ""))
        except Exception:  # noqa: BLE001
            pass

    return analysis_results, per_radius_data


# ============================================================================
# 6. 报告生成
# ============================================================================

def _log_key_interpretation(results: dict, dict_names: list[str], logger):
    """根据分析结果自动生成关键解读并记录到日志。

    解读逻辑：
        1. 检测标签不平衡程度，判断 Kappa 悖论风险
        2. 按对比组分类统计（极端窗口 r=0 vs 邻近窗口 r=2/3）
        3. 汇总 t 检验显著性
        4. 生成综合研判结论（适合论文讨论部分引用）
    """
    meta = results['meta']
    baseline_radius = 1
    radii = meta['radii_tested']
    total_articles = meta['total_articles']

    logger.info("")
    logger.info("─" * 80)
    logger.info(">>>  关键解读（自动生成）  <<<")
    logger.info("─" * 80)

    # ── 1. 标签不平衡检测与 Kappa 悖论 ──
    logger.info("")
    logger.info("【1. 标签分布不平衡检测】")
    max_dominant_pct = 0.0
    dominant_label = ""
    for dn in dict_names:
        for r in radii:
            dist_pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            for label, pct in dist_pct.items():
                if pct > max_dominant_pct:
                    max_dominant_pct = pct
                    dominant_label = label

    # 计算各半径下主导标签的平均占比
    dominant_pcts_per_radius = {}
    for r in radii:
        pcts = []
        for dn in dict_names:
            dist_pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            pcts.append(max(dist_pct.values()))
        dominant_pcts_per_radius[r] = np.mean(pcts)

    avg_dominant = np.mean(list(dominant_pcts_per_radius.values()))
    logger.info(f"  主导标签「{dominant_label}」平均占比: {pct4(avg_dominant, fraction=False)}")

    kappa_paradox = avg_dominant >= 90.0
    if kappa_paradox:
        logger.info("  检测到高度不平衡（主导标签 ≥ 90%）")
        logger.info(f"    → Kappa 悖论 (Paradox of High Agreement but Low Kappa):")
        logger.info(f"      当分类高度集中于单一类别时，即使一致率很高，")
        logger.info(f"      Kappa 也会因为 P(e) 过大而被严重压低。")
        logger.info(f"      因此 Kappa 值不应作为唯一稳健性判据。")
    else:
        logger.info(f"  标签分布相对均衡，Kappa 指标可作为可靠判据。")

    # ── 2. 分组对比分析 ──
    logger.info("")
    logger.info("【2. 分组对比分析】")

    # 区分极端窗口 (r=0) 和邻近窗口 (r=2, r=3)
    extreme_key = f"r{baseline_radius}_vs_r0"
    adjacent_keys = [k for k in results['cross_radius'].keys() if k != extreme_key]

    # 极端窗口 (r=0)
    if extreme_key in results['cross_radius']:
        pair_data = results['cross_radius'][extreme_key]
        kappas = [pair_data[dn]['cohens_kappa'] for dn in dict_names]
        pearsons = [pair_data[dn]['pearson_r'] for dn in dict_names]
        agrees = [pair_data[dn]['label_agreement'] for dn in dict_names]
        t_ps = [pair_data[dn]['paired_t_p'] for dn in dict_names]
        sig_count = sum(1 for p in t_ps if p < 0.05)

        logger.info("  ── r=1 vs r=0（极端窗口: 仅实体所在句）──")
        logger.info(f"     Kappa 范围:     {sig4(min(kappas))} ~ {sig4(max(kappas))}  (均值 {sig4(np.mean(kappas))})")
        logger.info(f"     Pearson 范围:   {sig4(np.nanmin(pearsons))} ~ {sig4(np.nanmax(pearsons))}  (均值 {sig4(np.nanmean(pearsons))})")
        logger.info(f"     一致率范围:     {pct4(min(agrees))} ~ {pct4(max(agrees))}")
        logger.info(f"     t 检验显著 (p<0.05): {sig_count}/{len(dict_names)} 个词典")
        if np.mean(kappas) < 0.60:
            logger.info("     → 解读: r=0 仅保留实体所在句，上下文信息严重不足，")
            logger.info("       与 r=1 差异较大属于预期行为，不影响 r=1 的合理性。")

    # 邻近窗口 (r=2, r=3)
    if adjacent_keys:
        adj_kappas = []
        adj_pearsons = []
        adj_agrees = []
        adj_t_ps = []
        for key in adjacent_keys:
            pair_data = results['cross_radius'][key]
            for dn in dict_names:
                adj_kappas.append(pair_data[dn]['cohens_kappa'])
                adj_pearsons.append(pair_data[dn]['pearson_r'])
                adj_agrees.append(pair_data[dn]['label_agreement'])
                adj_t_ps.append(pair_data[dn]['paired_t_p'])

        adj_sig_count = sum(1 for p in adj_t_ps if p < 0.05)
        adj_radii_str = ", ".join(k.split("_vs_")[1] for k in adjacent_keys)

        logger.info(f"  ── r=1 vs 邻近窗口（{adj_radii_str}）──")
        logger.info(f"     Kappa 范围:     {sig4(min(adj_kappas))} ~ {sig4(max(adj_kappas))}  (均值 {sig4(np.mean(adj_kappas))})")
        logger.info(f"     Pearson 范围:   {sig4(np.nanmin(adj_pearsons))} ~ {sig4(np.nanmax(adj_pearsons))}  (均值 {sig4(np.nanmean(adj_pearsons))})")
        logger.info(f"     一致率范围:     {pct4(min(adj_agrees))} ~ {pct4(max(adj_agrees))}")
        logger.info(f"     t 检验显著 (p<0.05): {adj_sig_count}/{len(adj_t_ps)} 个词典×对比组")
        if np.nanmean(adj_pearsons) >= 0.80:
            logger.info("     → 解读: 邻近半径间得分高度相关 (Pearson ≥ 0.80)，")
            logger.info("       标签变化极少，结果具有良好稳健性。")

    # ── 3. t 检验显著性汇总 ──
    logger.info("")
    logger.info("【3. 配对 t 检验显著性汇总】")
    all_t_ps = []
    sig_pairs = []
    for pair_key, pair_data in results['cross_radius'].items():
        for dn in dict_names:
            p_val = pair_data[dn]['paired_t_p']
            all_t_ps.append(p_val)
            if p_val < 0.05:
                sig_pairs.append((pair_key, dn, p_val))

    total_tests = len(all_t_ps)
    total_sig = len(sig_pairs)
    logger.info(f"  共进行 {total_tests} 组配对 t 检验（{len(results['cross_radius'])} 对比组 × {len(dict_names)} 词典）")
    logger.info(f"  显著 (p < 0.05): {total_sig} 组")
    logger.info(f"  不显著 (p ≥ 0.05): {total_tests - total_sig} 组")
    if sig_pairs:
        logger.info("  显著的对比组:")
        for pair_key, dn, p_val in sig_pairs:
            logger.info(f"    - {pair_key} × {dn}: p = {sig4(p_val)}")
    else:
        logger.info("  → 所有对比组的均值差异均不具有统计显著性。")

    # ── 4. 综合研判结论 ──
    logger.info("")
    logger.info("【4. 综合研判结论】")

    # 判定邻近窗口的稳健性
    adj_robust = (len(adjacent_keys) > 0
                  and np.nanmean(adj_pearsons) >= 0.80
                  and np.mean(adj_agrees) >= 0.95)

    # 判定极端窗口是否有偏差
    extreme_deviated = False
    if extreme_key in results['cross_radius']:
        extreme_pair = results['cross_radius'][extreme_key]
        extreme_kappas = [extreme_pair[dn]['cohens_kappa'] for dn in dict_names]
        extreme_deviated = np.mean(extreme_kappas) < 0.60

    # 判定 t 检验总体不显著
    mostly_nonsig = (total_sig / total_tests) <= 0.2 if total_tests > 0 else True

    if adj_robust and mostly_nonsig:
        # 邻近稳健 + t 检验多数不显著 → 实质稳健
        if extreme_deviated and kappa_paradox:
            logger.info("  结论: 情感分析结果对窗口半径选择具有实质稳健性。")
            logger.info("")
            logger.info(f"  - 当前生产配置 r={baseline_radius} 是合理的折中选择。")
            logger.info(f"  - 邻近半径 (r={baseline_radius} vs r=2/r=3) 一致率 ≥ {pct4(min(adj_agrees))}，")
            logger.info(f"    Pearson 相关 ≥ {sig4(np.nanmin(adj_pearsons))}，差异统计上不显著。")
            logger.info(f"  - r=0 的 Kappa 较低是由标签高度不平衡导致的 Kappa 悖论，")
            logger.info(f"    以及 r=0 上下文信息不足的双重因素所致，")
            logger.info(f"    不影响 r={baseline_radius} 作为默认值的方法论合理性。")
            logger.info(f"  - 建议论文讨论: 在附录中报告本检验结果，说明 r=0 偏差")
            logger.info(f"    归因于上下文信息不足，符合 proximity-based attribution 的理论预期。")
        elif extreme_deviated:
            logger.info("  结论: 情感分析结果在邻近半径间具有良好稳健性，")
            logger.info("        但 r=0 极端窗口存在显著偏差。")
            logger.info("")
            logger.info(f"  - r={baseline_radius} 与 r=2/r=3 的差异不显著，结果稳健。")
            logger.info(f"  - r=0 偏差较大，建议在论文中讨论上下文窗口的边界效应。")
        else:
            logger.info("  结论: 情感分析结果对窗口半径选择具有良好稳健性。")
            logger.info("")
            logger.info(f"  - 所有半径对比均显示较高一致性。")
            logger.info(f"  - r={baseline_radius} 是稳健的默认选择。")
    elif adj_robust:
        logger.info("  结论: 邻近半径间稳健性良好，但个别对比组存在统计显著差异。")
        logger.info("")
        logger.info(f"  - 虽有 {total_sig} 组 t 检验显著，但实际均值差异幅度很小。")
        logger.info(f"  - r={baseline_radius} 仍可作为合理的默认选择。")
    else:
        logger.info("  结论: 情感分析结果对窗口半径选择存在一定敏感性。")
        logger.info("")
        logger.info(f"  - 建议在论文中充分讨论参数选择依据。")
        logger.info(f"  - 考虑展示多半径结果作为稳健性检验的一部分。")

    logger.info("")
    logger.info("=" * 80)


def log_report(results: dict):
    """将分析结果输出到日志（结构化文本报告）。"""
    meta = results['meta']
    dict_names = meta['dictionaries']

    logger.info("=" * 80)
    logger.info("===   实体上下文窗口半径敏感性检验报告（Sensitivity Analysis）   ===")
    logger.info("=" * 80)
    logger.info(f"总文章数: {meta['total_articles']:,}")
    logger.info(f"检验半径: {meta['radii_tested']}")
    logger.info(f"使用词典: {dict_names}")
    logger.info(f"处理耗时: {meta['processing_time_seconds']}s")

    # ── Panel A: 上下文统计 ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel A: 各半径下的上下文提取统计")
    logger.info("─" * 80)
    logger.info(f"{'Radius':>8} {'平均字符数':>12} {'占全文比例':>12} {'平均分词数':>12} {'未命中(回退)':>14}")
    logger.info("-" * 60)
    for r in meta['radii_tested']:
        ctx = results['per_radius'][str(r)]['context']
        logger.info(f"{r:>8} {sig4(ctx['mean_char_len']):>12} {pct4(ctx['mean_ratio']):>12} "
                     f"{sig4(ctx['mean_token_count']):>12} {ctx['empty_count']:>14,}")

    # ── Panel B: 标签分布 ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel B: 各半径 × 词典的标签分布 (%)")
    logger.info("─" * 80)
    header = f"{'词典':<12} {'Radius':>8}   {'正面':>8} {'中性':>8} {'负面':>8}"
    logger.info(header)
    logger.info("-" * 54)
    for dn in dict_names:
        for r in meta['radii_tested']:
            dist = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
            logger.info(f"{dn:<12} {r:>8}   {pct4(dist['正面'], fraction=False):>8} "
                        f"{pct4(dist['中性'], fraction=False):>8} {pct4(dist['负面'], fraction=False):>8}")
        logger.info("")

    # ── Panel C: 跨半径一致性（对比基准 r=1） ──
    logger.info("")
    logger.info("─" * 80)
    logger.info("Panel C: 跨半径一致性（基准 = radius=1）")
    logger.info("─" * 80)
    header2 = (f"{'对比':>14} {'词典':<12} {'一致率':>8} {'Kappa':>8} "
               f"{'Pearson':>9} {'Spearman':>9} {'均值差':>8} {'t-test p':>10}")
    logger.info(header2)
    logger.info("-" * 90)
    for pair_key, pair_data in results['cross_radius'].items():
        for dn in dict_names:
            d = pair_data[dn]
            logger.info(
                f"{pair_key:>14} {dn:<12} {pct4(d['label_agreement']):>8} {sig4(d['cohens_kappa']):>8} "
                f"{sig4(d['pearson_r']):>9} {sig4(d['spearman_rho']):>9} {sig4(d['mean_score_diff']):>8} "
                f"{sig4(d['paired_t_p']):>10}"
            )
        logger.info("")

    logger.info("=" * 80)

    # ── 结论摘要 ──
    logger.info("")
    logger.info(">>>  结论摘要  <<<")

    all_kappas = []
    all_agreements = []
    all_pearsons = []
    for pair_data in results['cross_radius'].values():
        for dn_data in pair_data.values():
            all_kappas.append(dn_data['cohens_kappa'])
            all_agreements.append(dn_data['label_agreement'])
            all_pearsons.append(dn_data['pearson_r'])

    if all_kappas:
        min_kappa = min(all_kappas)
        min_agree = min(all_agreements)
        min_pearson = float(np.nanmin(all_pearsons)) if all_pearsons else float('nan')  # fix(radius-F1): nan-safe

        baseline_radius = 1
        extreme_key = f"r{baseline_radius}_vs_r0"
        adjacent_pairs = {
            k: v for k, v in results['cross_radius'].items()
            if k != extreme_key
        }
        adjacent_kappas = []
        adjacent_agreements = []
        adjacent_pearsons = []
        for pair_data in adjacent_pairs.values():
            for dn_data in pair_data.values():
                adjacent_kappas.append(dn_data['cohens_kappa'])
                adjacent_agreements.append(dn_data['label_agreement'])
                adjacent_pearsons.append(dn_data['pearson_r'])

        logger.info(f"  全部对比最低标签一致率: {pct4(min_agree)}")
        logger.info(f"  全部对比最低 Cohen's Kappa: {sig4(min_kappa)}")
        logger.info(f"  全部对比最低 Pearson 相关: {sig4(min_pearson)}")

        if adjacent_kappas:
            adj_min_kappa = min(adjacent_kappas)
            adj_min_agree = min(adjacent_agreements)
            # fix(radius-F1, review-closure 2026-06-10): nan-safe — adjacent_pearsons 可含
            # 零方差守卫产生的 NaN, builtin min(含 nan) 不可靠。
            adj_min_pearson = float(np.nanmin(adjacent_pearsons)) if adjacent_pearsons else float('nan')
            logger.info(f"  邻近窗口最低标签一致率: {pct4(adj_min_agree)}")
            logger.info(f"  邻近窗口最低 Cohen's Kappa: {sig4(adj_min_kappa)}")
            logger.info(f"  邻近窗口最低 Pearson 相关: {sig4(adj_min_pearson)}")
        else:
            adj_min_kappa = min_kappa
            adj_min_agree = min_agree
            adj_min_pearson = min_pearson

        if adj_min_kappa >= 0.80:
            logger.info("  ✅ 判定: 邻近窗口半径下情感分析结果具有强稳健性（κ ≥ 0.80）")
        elif adj_min_kappa >= 0.60 and adj_min_agree >= 0.95 and adj_min_pearson >= 0.80:
            logger.info("  判定: 邻近窗口半径下情感分析结果具有实质稳健性（κ ≥ 0.60, agreement ≥ 95%, Pearson ≥ 0.80）")
        else:
            logger.info("  判定: 邻近窗口半径下情感分析结果存在一定敏感性，需讨论参数选择")

        if extreme_key in results['cross_radius'] and min_kappa < 0.60:
            logger.info("  注: 最低 κ 来自 r=0 极端压力测试；r=0 仅保留实体所在句，不作为默认窗口稳健性的主判据。")

    logger.info("=" * 80)

    # ── 关键解读（自动生成） ──
    _log_key_interpretation(results, dict_names, logger)


def generate_latex_table(results: dict) -> str:
    """生成 LaTeX 格式的敏感性分析表格（论文附录使用）。"""
    meta = results['meta']
    dict_names = meta['dictionaries']

    lines = []
    lines.append(r"\begin{table}[htbp]")
    lines.append(r"\centering")
    lines.append(r"\caption{Entity Context Window Radius Sensitivity Analysis}")
    lines.append(r"\label{tab:radius_sensitivity}")
    lines.append(r"\small")

    # ── Panel A: 标签分布 Label Distribution ──
    lines.append(r"\begin{tabular}{ll" + "r" * len(meta['radii_tested']) + "}")
    lines.append(r"\toprule")
    header_cols = " & ".join([f"$r={r}$" for r in meta['radii_tested']])
    lines.append(r"Dictionary & Label & " + header_cols + r" \\")
    lines.append(r"\midrule")

    for dn in dict_names:
        dn_display = dn.replace('_', r'\_')
        for label in ['正面', '中性', '负面']:
            label_en = {'正面': 'Positive', '中性': 'Neutral', '负面': 'Negative'}[label]
            vals = []
            for r in meta['radii_tested']:
                pct = results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct'][label]
                vals.append(f"{pct:.1f}\\%")
            row_dn = dn_display if label == '正面' else ""
            lines.append(f"  {row_dn} & {label_en} & " + " & ".join(vals) + r" \\")
        lines.append(r"\addlinespace")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")

    lines.append(r"\vspace{0.5em}")

    # ── Panel B: 跨半径一致率 Cross-Radius Agreement ──
    lines.append(r"\begin{tabular}{llrrrrr}")
    lines.append(r"\toprule")
    lines.append(r"Comparison & Dictionary & Agreement & $\kappa$ & Pearson $r$ & Spearman $\rho$ & $p$-value \\")
    lines.append(r"\midrule")

    for pair_key, pair_data in results['cross_radius'].items():
        pair_display = pair_key.replace('_', r'\_')
        for dn in dict_names:
            d = pair_data[dn]
            dn_display = dn.replace('_', r'\_')
            p_str = f"{d['paired_t_p']:.4f}" if d['paired_t_p'] >= 0.0001 else "<0.0001"
            lines.append(
                f"  {pair_display} & {dn_display} & "
                f"{d['label_agreement']:.2%} & {d['cohens_kappa']:.3f} & "
                f"{d['pearson_r']:.3f} & {d['spearman_rho']:.3f} & {p_str}" + r" \\"
            )
        pair_display = ""  # 后续行不重复
        lines.append(r"\addlinespace")

    lines.append(r"\bottomrule")
    lines.append(r"\end{tabular}")
    lines.append(r"\end{table}")

    return "\n".join(lines)


def _compute_pairwise_radius_corr(per_radius_data: dict, dict_name: str,
                                  radii: list) -> np.ndarray:
    """计算各半径得分两两 Pearson 相关矩阵 (供热力图渲染)。

    fix(omni-g-val-robust-03, 2026-06-11): FIX-REGRESSION 闭合 — 复用 cross_radius
    统计路径的 radius-zerovar-guard (2026-06-10, 见 run_sensitivity_analysis 内
    注释): 零方差 (常量分数 — 词典零命中/空实体窗口/T=2 退化样本) 或样本 n<=2
    时 pearsonr 无定义。此前热力图路径裸调 pearsonr → NaN + ConstantInputWarning,
    'nan' 文本被直接渲染进论文附录图 65_radius_correlation_heatmap.png。
    现与统计路径同语义置 NaN, 由调用方标注 'n/a'; 对角线按惯例固定 1.0。

    Args:
        per_radius_data: {radius: [per-article dict, ...]} 得分明细。
        dict_name:       词典名 (取 f'{dict_name}_score' 列)。
        radii:           半径列表 (与矩阵行列顺序一致)。

    Returns:
        np.ndarray: len(radii) × len(radii) 相关矩阵, 退化单元格为 NaN。
    """
    n = len(radii)
    corr = np.ones((n, n))
    for i, r1 in enumerate(radii):
        scores_1 = [d[f'{dict_name}_score'] for d in per_radius_data[r1]]
        for j, r2 in enumerate(radii):
            if i == j:
                continue
            scores_2 = [d[f'{dict_name}_score'] for d in per_radius_data[r2]]
            if (len(scores_1) > 2
                    and float(np.std(scores_1)) > 0
                    and float(np.std(scores_2)) > 0):
                corr[i, j] = scipy_stats.pearsonr(scores_1, scores_2)[0]
            else:
                corr[i, j] = float('nan')
    return corr


def generate_visualizations(results: dict, per_radius_data: dict, output_dir: str):
    """生成可视化图表。"""
    if not HAS_MATPLOTLIB:
        logger.warning("matplotlib 未安装，跳过可视化生成。")
        return

    # 尝试设置中文字体
    try:
        # Windows 常见中文字体路径
        font_paths = [
            'C:/Windows/Fonts/msyh.ttc',     # 微软雅黑
            'C:/Windows/Fonts/simhei.ttf',    # 黑体
            'C:/Windows/Fonts/simsun.ttc',    # 宋体
        ]
        zh_font = None
        for fp in font_paths:
            if os.path.exists(fp):
                zh_font = font_manager.FontProperties(fname=fp)
                break
        if zh_font is None:
            zh_font = font_manager.FontProperties()
    except Exception:
        zh_font = font_manager.FontProperties()

    meta = results['meta']
    dict_names = meta['dictionaries']

    # ── 图1: 标签分布柱状图 ──
    fig, axes = plt.subplots(1, len(dict_names), figsize=(4 * len(dict_names), 4), sharey=True)
    if len(dict_names) == 1:
        axes = [axes]

    labels_cn = ['正面', '中性', '负面']
    labels_en = ['Positive', 'Neutral', 'Negative']
    colors = ['#2ecc71', '#95a5a6', '#e74c3c']

    for idx, dn in enumerate(dict_names):
        ax = axes[idx]
        x = np.arange(len(labels_cn))
        width = 0.18
        for ri, r in enumerate(meta['radii_tested']):
            pcts = [results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct'][l]
                    for l in labels_cn]
            ax.bar(x + ri * width, pcts, width, label=f'r={r}', alpha=0.85)
        ax.set_xlabel('Sentiment', fontsize=10)
        ax.set_ylabel('Percentage (%)' if idx == 0 else '', fontsize=10)
        ax.set_title(dn.replace('_', ' ').title(), fontsize=11)
        ax.set_xticks(x + width * (len(meta['radii_tested']) - 1) / 2)
        ax.set_xticklabels(labels_en, fontsize=9)
        ax.legend(fontsize=8, loc='upper right')

    plt.suptitle('Label Distribution Across Window Radii', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig_path_1 = os.path.join(output_dir, '65_radius_label_distribution.png')
    plt.savefig(fig_path_1, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"图表已保存: {fig_path_1}")

    # ── 图2: 得分相关性热力图 ──
    fig, axes = plt.subplots(1, len(dict_names), figsize=(4 * len(dict_names), 3.5))
    if len(dict_names) == 1:
        axes = [axes]

    for idx, dn in enumerate(dict_names):
        ax = axes[idx]
        # fix(omni-g-val-robust-03, 2026-06-11): 改走带零方差/样本量守卫的辅助函数
        # (与 cross_radius 统计路径的 radius-zerovar-guard 同款), 防 NaN 渲染进附录图
        corr_matrix = _compute_pairwise_radius_corr(per_radius_data, dn, RADII)

        im = ax.imshow(corr_matrix, cmap='RdYlGn', vmin=0.5, vmax=1.0, aspect='auto')
        ax.set_xticks(range(len(RADII)))
        ax.set_yticks(range(len(RADII)))
        ax.set_xticklabels([f'r={r}' for r in RADII], fontsize=9)
        ax.set_yticklabels([f'r={r}' for r in RADII], fontsize=9)
        ax.set_title(dn.replace('_', ' ').title(), fontsize=11)

        # 在单元格中标注数值
        for i in range(len(RADII)):
            for j in range(len(RADII)):
                val = corr_matrix[i, j]
                if np.isnan(val):
                    # fix(omni-g-val-robust-03): 零方差单元格显式标注 n/a
                    # (相关无定义), 与 cross_radius 的 NaN 语义一致
                    ax.text(j, i, 'n/a', ha='center', va='center',
                            fontsize=8, color='black')
                else:
                    text_color = 'white' if val < 0.75 else 'black'
                    ax.text(j, i, f'{val:.3f}',
                            ha='center', va='center', fontsize=8, color=text_color)

    plt.suptitle('Score Correlation Across Window Radii (Pearson r)', fontsize=13, fontweight='bold')
    plt.tight_layout()
    fig_path_2 = os.path.join(output_dir, '65_radius_correlation_heatmap.png')
    plt.savefig(fig_path_2, dpi=200, bbox_inches='tight')
    plt.close()
    logger.info(f"图表已保存: {fig_path_2}")


# ============================================================================
# 7. 主函数
# ============================================================================

def _log_environment_and_config(input_path: str) -> None:
    """打印 项目/环境信息 + 输入输出 + 运行配置 + 方法论引用 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数、方法学出处"一次性落进
    日志, 便于复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    """
    try:
        out_dir = CONFIG['paths']['output_dir']
        json_path = os.path.join(out_dir, '65_radius_sensitivity.json')
        tex_path = os.path.join(out_dir, '65_radius_sensitivity.tex')
        bank_file = CONFIG['paths'].get('bank_names_file', '(默认)')
        fintech_file = CONFIG['paths'].get('fintech_dict_file', '(默认)')

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (实体上下文窗口半径敏感性检验, STAGES_VALIDATION; ctx 轨稳健性附录证据)")
        logger.info("     · 项目: news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板), 版本 v3.11.1")
        logger.info("     · 行为版本: 跨类重叠词『保留并两侧计数』(用户决策 2026-06-24, 逆转双侧剔除; 旁路 loader 已对齐生产 22_tone_words 6 词典 union)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · jieba:    {getattr(jieba, '__version__', '?')} (冻结锚点 0.42.1; 确定性来源=jieba版本+词典文件) | matplotlib={'可用' if HAS_MATPLOTLIB else '缺失(跳图)'}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU 词典 / 无 LLM·Embedding·网络·API / 无缓存 / 不抽样(全量) ($0, 逐位可复现)")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:     {input_path}")
        logger.info(f"     · 词典文件: {TONE_DICTS_FILE}")
        logger.info(f"     · 注入词源: 银行名={bank_file} | 金科={fintech_file}")
        logger.info(f"     · 输出JSON: {json_path}")
        logger.info(f"     · 输出LaTeX:{tex_path}")
        logger.info(f"     · 输出图表: {os.path.join(out_dir, '65_radius_label_distribution.png')} / "
                    f"{os.path.join(out_dir, '65_radius_correlation_heatmap.png')}")

        logger.info("  ⚙ 运行配置 (config/sentiment.yaml::sentiment_analysis.tone_words 等)")
        logger.info(f"     · 待检验窗口半径 RADII={RADII} | 基准半径=1 (生产配置) | 字符级回退窗口 FALLBACK_CHAR_RADIUS={FALLBACK_CHAR_RADIUS}")
        logger.info(f"     · 多轨开关 RUN_MULTI_TRACK={RUN_MULTI_TRACK} (占位, 未接线; 当前为 track-agnostic 半径扫描)")
        logger.info(f"     · 否定窗口 NEGATION_WINDOW={NEGATION_WINDOW} | 转折增强 ADVERSATIVE_BOOST={sig4(ADVERSATIVE_BOOST)}")
        logger.info(f"     · 标签阈值: 正面>{sig4(POS_THRESHOLD)} / 负面<{sig4(NEG_THRESHOLD)} / 其间=中性 (_score_to_label)")
        logger.info(f"     · 语言学规则词表: 否定词={len(NEGATION_WORDS):,} | 程度副词={len(DEGREE_WORDS):,} "
                    f"| 转折连词={len(ADVERSATIVE_WORDS):,} | 句末标点={len(SENTENCE_END_MARKERS):,}")

        logger.info("  📖 方法论依据 (参考文献; 仅引经核验注册表条目, 逐字照抄 APA-7 + DOI)")
        logger.info("     · 邻近归因参数敏感性 (核心): Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). "
                    "Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, "
                    "134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021")
        logger.info("       → 本阶段把 ctx 提取窗口 (proximity-based attribution 的句级半径) 当作关键方法论参数, "
                    "扫描 r∈{0,1,2,3} 做顶刊标准的稳健性检验。")
        logger.info("     · firm-level 文本度量构建范式 (词表/二元组命中): Sautner, Z., van Lent, L., Vilkov, G., "
                    "& Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), "
                    "1449-1498. https://doi.org/10.1111/jofi.13219")
        logger.info("       → (白话: 用 ML 发现关键词 + 二元组命中构企业级 attention 度量, 是本阶段 ctx 轨"
                    "词典命中型 firm-level 文本度量的标准模板; 度量对构建参数的稳健性正是顶刊要求的附录证据。)")
        logger.info("     · bag-of-words 文本暴露度量 + 外部效度验证: Wu, D. (A.). (2024). Text-based measure of "
                    "supply chain risk exposure. Management Science, 70(7), 4781-4801. "
                    "https://doi.org/10.1287/mnsc.2023.4927")
        logger.info("       → (白话: 种子词嵌入 + 词袋构企业级文本暴露并以波动率作外部验证, 与本阶段词袋式"
                    "词典计分同族; 同样需对窗口/词表等设定做敏感性披露以证度量非任意。)")
        logger.info("     · 词典法情感测度的方法学基底 (lexicon-based, 6 套中文金融词典逐句计分): "
                    "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). "
                    "Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, "
                    "63(1), 125-143. https://doi.org/10.1111/ecin.13264")
        logger.info("       → 本阶段在每个 radius 下复用生产 22_tone_words 的词典逐句规则 (否定翻转/程度缩放/"
                    "转折增强) 重算情感分, 属经济文本 lexicon-based 情感分析谱系; 对截取窗口的稳健性即该测度"
                    "可信度的附录证据。")
        logger.info("     · κ 分级判读阈值 + 'Kappa 悖论' 判据来源: "
                    "Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for "
                    "categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310")
        logger.info("       → 本阶段邻近窗口稳健性判定 (min κ≥0.80 强稳健 / ≥0.60 且一致率≥95%·Pearson≥0.80 "
                    "实质稳健) 锚定其 substantial(κ≥0.61) 区间; 主导标签 ≥90% 集中时 κ 被 P(e) 数学压低的"
                    "'Kappa 悖论'亦本框架推论, 故配一致率/Pearson 佐证。")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置/方法信息打印失败 (不影响处理): {e}")


def main():
    """窗口半径敏感性检验主入口。"""
    stage_start = time.time()
    phase_durations: dict[str, float] = {}  # 各主要子阶段墙钟耗时 (日志富集, 末尾汇总)
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info(f"检验的窗口半径: {RADII}")
    logger.info("基准半径: 1（当前生产配置）")

    # ── 阶段功能 banner（黄金范式: 让 <stage>.log 自带说明书）──
    logger.info("=" * 72)
    logger.info("阶段 35: 实体上下文窗口半径敏感性检验 (Hassan et al. 2019 QJE, proximity-based attribution)")
    logger.info("=" * 72)
    logger.info("【功能】ctx 轨只截取'银行名所在句 ± N 句'这一小段文本来打情感分, '几句'(sentence_radius,")
    logger.info("        生产 = 前后 1 句) 是人为参数。本阶段把窗口改成 radius ∈ {0,1,2,3} 各重提一遍、用")
    logger.info("        6 套中文金融情感词典各重算情感分, 检验结论对窗口大小是否稳健。产出 JSON/LaTeX 表 +")
    logger.info("        标签分布柱状图 + 半径相关性热力图 (附录级证据, 无 parquet)。")
    logger.info(f"【方法】每篇文章对每个 radius 调 extract_entity_context(sentence_radius=r, "
                f"fallback_char_radius={FALLBACK_CHAR_RADIUS}) 提上下文 (未命中回退原文), jieba 分词后")
    logger.info("        对 6 词典各算否定翻转/程度缩放/转折增强的规则增强词典分 → 归一化得分 + 三分类标签")
    logger.info(f"        (阈值 ±{POS_THRESHOLD})。以 r=1 为基准, 跨半径算 标签一致率 / Cohen's κ / "
                f"Pearson·Spearman 相关 / 配对 t 检验。")
    logger.info("【判读】邻近窗口 (r=1 vs 2/3): κ↑、一致率↑、Pearson↑ = 稳健 (min κ≥0.80 强稳健; ≥0.60")
    logger.info("        且一致率≥95%、Pearson≥0.80 实质稳健)。r=0 (仅实体所在句、砍光上下文) 是故意的极端")
    logger.info("        压力测试, 偏差大属预期, 不作主判据。标签 ≥90% 集中于单一类时存在 'Kappa 悖论'")
    logger.info("        (κ 被 P(e) 数学压低), 此时一致率/Pearson 更可信。")
    logger.info("【确定性】纯 CPU 词典 + 确定性提取, 不调 LLM/Embedding、无缓存、无抽样 (全量处理), 逐位可复现。")

    # ── 加载输入数据 ──
    # 优先使用阶段 21 的输出（经 LLM 精筛，含 target_bank 列）
    # 注 (2026-06-15): 回退候选 12_fintech_news.parquet 是 stage 12b 同句共现硬过滤
    #   【之前】的候选集 (pre-12b)。本检验意在评估 ctx 半径稳健性、是对'12b 应取何
    #   radius'的诊断, 故在 pre-12b 候选集上量窗口口径是有意为之, 非 bug。
    input_candidates = [
        CONFIG['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet'),
        CONFIG['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet'),
    ]

    input_path = None
    for fname in input_candidates:
        candidate = os.path.join(CONFIG['paths']['output_dir'], fname)
        if os.path.exists(candidate):
            input_path = candidate
            break

    if input_path is None:
        logger.error("未找到输入文件。需要阶段 21 或阶段 12 的输出。")
        return

    # 项目/环境信息 + 输入输出 + 运行配置 + 方法论引用 (日志富集 2026-06-24)
    _log_environment_and_config(input_path)

    logger.info(f"加载输入数据: {input_path}")
    _t = time.time()
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    phase_durations['①数据加载'] = time.time() - _t
    logger.info(f"已加载 {input_rows:,} 行数据。耗时 {sig4(phase_durations['①数据加载'])}s")
    log_memory_usage(logger, "数据加载后")

    # 检查必要列
    if 'target_bank' not in df.columns:
        logger.error("输入数据缺少 'target_bank' 列，无法执行 entity_context 提取。")
        return
    if '内容' not in df.columns:
        logger.error("输入数据缺少 '内容' 列。")
        return

    # 统计 target_bank 分布
    bank_counts = df['target_bank'].value_counts()
    logger.info(f"涵盖银行数: {len(bank_counts)}")
    logger.info(f"target_bank 非空记录: {df['target_bank'].notna().sum():,}")

    # ── 加载词典 ──
    _t = time.time()
    dictionaries = load_all_dictionaries()
    non_empty = sum(1 for _, d in dictionaries if d)
    phase_durations['②词典加载'] = time.time() - _t
    logger.info(f"有效词典数: {non_empty}/{len(dictionaries)} | 耗时 {sig4(phase_durations['②词典加载'])}s")

    # ── 初始化 jieba ──
    logger.info("初始化 jieba 分词器...")
    _t = time.time()
    _inject_custom_dicts_to_jieba(dictionaries)
    phase_durations['③jieba注入'] = time.time() - _t
    logger.info(f"jieba 词汇注入耗时 {sig4(phase_durations['③jieba注入'])}s")

    # ── 执行敏感性分析 ──
    _t = time.time()
    analysis_results, per_radius_data = run_sensitivity_analysis(df, dictionaries)
    phase_durations['④敏感性分析'] = time.time() - _t
    logger.info(f"敏感性分析(全量 × {len(RADII)} 半径)耗时 {sig4(phase_durations['④敏感性分析'])}s")

    # ── 输出报告 ──
    log_report(analysis_results)

    # ── 结果分析（黄金范式: 取真实产出指标 + 对照阈值/预期方向给判读）──
    # 说明: 以下全部为纯增量日志计算 — 只读 analysis_results / per_radius_data, 局部变量
    #       不回写任何产物, 不改返回值/写盘内容/schema/计量逻辑 (golden-safe)。
    # crash-guard: 本分析块跑在 JSON/LaTeX/PNG 写盘 (下方) 之前, 一旦此处诊断计算抛异常
    #       (如缺键 KeyError / 空 Series 聚合 ValueError) 会带崩整个阶段并丢失产物 →
    #       证伪 golden-safe。故整体 try/except, 异常仅告警跳过, 绝不阻断后续写盘。
    # 去重声明 (fix radius-P2): 本文件改动【前】已有两层自动研判 —— log_report 内
    #       '结论摘要'(min κ/一致率/Pearson + 强/实质稳健判定) + _log_key_interpretation
    #       '关键解读'(标签不平衡/Kappa 悖论/极端 vs 邻近窗口/t 检验汇总/综合研判)。下面这段
    #       与其中 κ/一致率/Pearson/Kappa悖论/t检验 几项【口径完全相同、数值同源】, 仅作单点
    #       速览 + 补充真增量诊断 (上下文回退率/词典降级/小样本), 非另一套独立检验。
    logger.info("【结果分析】下文为对上方'结论摘要'+'关键解读'的补充诊断速览: 同名指标 "
                "(κ/一致率/Pearson/Kappa悖论/t检验) 系同源复述、阈值口径一致, 增量在 "
                "(7)上下文回退率/(8)词典降级/(9)小样本 三项。")
    try:
        dict_names_ra = analysis_results['meta']['dictionaries']
        cross = analysis_results['cross_radius']
        baseline_r = 1
        extreme_k = f"r{baseline_r}_vs_r0"

        # 汇总全部对比组 + 区分邻近窗口(r=2/3) vs 极端窗口(r=0)
        all_k, all_ag, all_pe = [], [], []
        adj_k, adj_ag, adj_pe = [], [], []
        for pair_key, pair_data in cross.items():
            for dn in dict_names_ra:
                d = pair_data[dn]
                all_k.append(d['cohens_kappa'])
                all_ag.append(d['label_agreement'])
                all_pe.append(d['pearson_r'])
                if pair_key != extreme_k:
                    adj_k.append(d['cohens_kappa'])
                    adj_ag.append(d['label_agreement'])
                    adj_pe.append(d['pearson_r'])

        logger.info("-" * 72)
        logger.info("【结果分析】实体上下文窗口半径稳健性逐指标研判")

        # (1) 邻近窗口 Cohen's κ — 主稳健性判据 (强稳健阈值 0.80 / 实质稳健 0.60)
        #     注: compute_cohens_kappa 恒返回有限浮点 (不产 NaN), 故 κ 无需 nan-guard。
        if adj_k:
            adj_min_k = min(adj_k)
            adj_mean_k = float(np.mean(adj_k))
            if adj_min_k >= 0.80:
                verdict_k = "好(≥0.80 强稳健: 邻近窗口标签判定高度一致)"
            elif adj_min_k >= 0.60:
                verdict_k = "临界(0.60~0.80 实质稳健, 需配合一致率/Pearson 佐证)"
            else:
                verdict_k = "偏弱(<0.60: 留意是否 Kappa 悖论或上下文不足所致)"
            logger.info(f"  邻近窗口(r=1 vs r=2/3) Cohen's κ: min={sig4(adj_min_k)} / mean={sig4(adj_mean_k)} → {verdict_k}")
        else:
            logger.info("  邻近窗口对比组为空 (RADII 不含 2/3?), 无邻近 κ 可判。")

        # (2) 邻近窗口标签一致率 — 阈值 0.95 (compute_label_agreement 恒为 [0,1] 比例, 无 NaN)
        if adj_ag:
            adj_min_ag = min(adj_ag)
            verdict_ag = "好(≥95%)" if adj_min_ag >= 0.95 else (
                "临界(90%~95%)" if adj_min_ag >= 0.90 else "偏低(<90%, 窗口改变明显翻动标签)")
            logger.info(f"  邻近窗口最低标签一致率: {pct4(adj_min_ag)} → {verdict_ag}")

        # (3) 邻近窗口 Pearson 相关 — 阈值 0.80 (nan-guard: 零方差守卫可置 NaN)
        if adj_pe:
            nan_pe = sum(1 for v in adj_pe if np.isnan(v))
            if nan_pe == len(adj_pe):
                # 全 NaN: 不落进数值方向判断 (nanmin/nanmean 对全 NaN 会 RuntimeWarning + 返 nan)
                logger.info(f"  邻近窗口 Pearson 相关: 全部 {len(adj_pe)} 个词典×对比组均零方差/退化 "
                            f"→ 相关无定义 (不可判)。")
            else:
                adj_min_pe = float(np.nanmin(adj_pe))
                adj_mean_pe = float(np.nanmean(adj_pe))
                if adj_mean_pe >= 0.80:
                    verdict_pe = "好(均值≥0.80: 得分随窗口几乎不变)"
                else:
                    verdict_pe = "偏低(<0.80: 得分对窗口敏感)"
                logger.info(f"  邻近窗口 Pearson 相关: min={sig4(adj_min_pe)} / mean={sig4(adj_mean_pe)} → {verdict_pe}")
                if nan_pe:
                    logger.warning(f"  零方差守卫: 邻近窗口有 {nan_pe} 个词典×对比组的 Pearson 被置 NaN "
                                   f"(常量分数/词典零命中/空窗口/小样本退化 → 相关无定义, 已 nan-safe 聚合)。")

        # (4) 极端窗口 r=0 — 故意压力测试, 偏差大属预期 (非否定 r=1 的证据)
        if extreme_k in cross:
            ext_k = [cross[extreme_k][dn]['cohens_kappa'] for dn in dict_names_ra]
            ext_ag = [cross[extreme_k][dn]['label_agreement'] for dn in dict_names_ra]
            if ext_k:
                ext_mean_k = float(np.mean(ext_k))
                logger.info(f"  极端窗口(r=1 vs r=0, 仅实体所在句) κ: min={sig4(min(ext_k))} / mean={sig4(ext_mean_k)}, "
                            f"一致率 min={pct4(min(ext_ag))} → "
                            f"{'偏差大属预期(上下文被砍光, 不作主判据)' if ext_mean_k < 0.60 else '意外稳健(r=0 即已足够)'}")

        # (5) Kappa 悖论检测 — 主导标签平均占比 ≥90% 时 κ 被数学压低
        dom_pcts = []
        for r in analysis_results['meta']['radii_tested']:
            for dn in dict_names_ra:
                dist_pct = analysis_results['per_radius'][str(r)]['dictionaries'][dn]['label_distribution_pct']
                dom_pcts.append(max(dist_pct.values()))
        avg_dom = float(np.mean(dom_pcts)) if dom_pcts else 0.0
        if avg_dom >= 90.0:
            logger.info(f"  标签分布: 主导标签平均占比 {pct4(avg_dom, fraction=False)} (≥90%) → 触发 Kappa 悖论, "
                        f"κ 偏低应以一致率/Pearson 为准, 勿仅凭 κ 否定稳健性。")
        else:
            logger.info(f"  标签分布: 主导标签平均占比 {pct4(avg_dom, fraction=False)} (<90%) → 分布较均衡, κ 可作可靠判据。")

        # (6) 配对 t 检验显著比例 — 越低越说明均值差异不显著(稳健)
        #     注: NaN p 值 (退化样本) 不满足 p<0.05 → 不计入显著, 偏保守, 语义正确。
        t_ps = [cross[pk][dn]['paired_t_p'] for pk in cross for dn in dict_names_ra]
        if t_ps:
            sig = sum(1 for p in t_ps if p < 0.05)
            sig_frac = sig / len(t_ps)
            logger.info(f"  配对 t 检验: {sig}/{len(t_ps)} 组均值差异显著(p<0.05) "
                        f"({pct4(sig_frac)}) → {'多数不显著, 窗口改变未系统性移动得分(好)' if sig_frac <= 0.2 else '显著比例偏高, 需讨论参数选择'}")

        # (7) 上下文回退(未命中实体)率 — 回退过高会削弱 ctx 与 full 的区分度
        for r in analysis_results['meta']['radii_tested']:
            ctx_stat = analysis_results['per_radius'][str(r)]['context']
            empty_n = ctx_stat['empty_count']
            empty_frac = empty_n / input_rows if input_rows > 0 else 0.0
            logger.info(f"  r={r}: 平均上下文 {sig4(ctx_stat['mean_char_len'])} 字 (占全文 {pct4(ctx_stat['mean_ratio'])}), "
                        f"未命中回退 {empty_n:,} 篇 ({pct4(empty_frac)})")

        # (8) 词典可用性优雅降级警告
        if non_empty < len(dictionaries):
            logger.warning(f"  词典降级: 仅 {non_empty}/{len(dictionaries)} 套情感词典非空 "
                           f"(tone_dicts.json 缺失/损坏?), 空词典文章被记为'中性', 会人为抬高一致率/κ。")

        # (9) 小样本警告 (盘面 T=2 仅验证管道正确性)
        if input_rows < 5000:
            logger.info(f"  ⚠ 样本量 {input_rows:,} 篇偏小 (盘面 T=2 退化): 本次结果仅验证管道正确性, "
                        f"全量稳健性结论以 17M 篇 / T=18 实测为准 (小样本下 κ/相关易退化、零方差守卫频繁触发)。")

        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")

    # ── 保存 JSON / LaTeX / 可视化 ──
    _t = time.time()
    output_dir = CONFIG['paths']['output_dir']
    json_path = os.path.join(output_dir, '65_radius_sensitivity.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_results, f, ensure_ascii=False, indent=2)
    logger.info(f"JSON 报告已保存: {json_path}")

    # ── 保存 LaTeX 表格 ──
    latex_path = os.path.join(output_dir, '65_radius_sensitivity.tex')
    latex_content = generate_latex_table(analysis_results)
    with open(latex_path, 'w', encoding='utf-8') as f:
        f.write(latex_content)
    logger.info(f"LaTeX 表格已保存: {latex_path}")

    # ── 生成可视化 ──
    generate_visualizations(analysis_results, per_radius_data, output_dir)
    phase_durations['⑤报告+图表写盘'] = time.time() - _t

    # ── 各子阶段墙钟耗时汇总 (日志富集) ──
    try:
        logger.info("  ⏱ 各子阶段墙钟耗时 (秒, 4 位有效数字)")
        for _name, _dur in phase_durations.items():
            logger.info(f"     · {_name}: {sig4(_dur)}s")
        logger.info(f"     · 合计(已计时子阶段): {sig4(sum(phase_durations.values()))}s")
    except Exception as _te:  # noqa: BLE001
        logger.warning(f"  阶段计时汇总打印失败 (不影响产物): {_te}")

    # ── 阶段摘要 ──
    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=input_rows)
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} ---")


if __name__ == "__main__":
    main()
