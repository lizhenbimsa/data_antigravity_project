"""
news_process.pipeline.sentiment.tone_words — 阶段22：基于词典的情感分析 + 语言学规则增强
=========================================================================================

迁移说明 (Phase 7a-5)：
    本模块由原 root script ``22_tone_words.py`` body 迁入。
    规范调用方式: ``python -m news_process.pipeline.sentiment.tone_words``


功能：
    使用多个中文金融/通用情感词典，对每篇新闻计算情感得分。

┌────────────────────────────────────────────────────────────┐
│ 词典列表（来源：config/tone_dicts.json）                      │
├────────────────────────────────────────────────────────────┤
│ 1. jiang_2021  姜富伟等（2021）中文金融情感词典                 │
│    └─ positive(3,194)  /  negative(5,621)                  │
│       基于 LM(2011) 英文词典翻译扩充；两类不跨类去重            │
│                                                            │
│ 2. yao_2021   姚加权等（2021）金融领域中文情绪词典              │
│    ├─ annualReport_positive(3,592) / negative(1,633)        │
│    ├─ socialMedia_positive(912)    / negative(965)          │
│    └─ positive = 年报∪社媒去重(3,844) / negative(2,074)      │
│                                                            │
│ 3. bian_2021  Bian et al.(2021) LM 中文本土化扩充版           │
│    └─ positive(1,107)  /  negative(1,488)                  │
│                                                            │
│ 4. du_2022    Du et al.(2022) 含政治正面词金融情感扩充          │
│    ├─ positive(2,235)  /  negative(2,986)                  │
│    └─ political_positive(1,434)（以 0.5 权重加入）              │
│                                                            │
│ 5. you_2018   You et al.(2018) 中文金融情感词典               │
│    ├─ positive(1,425)  / negative(1,583)                   │
│    ├─ definite(388)  / ambiguous(178, v3.5.1 起用于 clarity) │
└────────────────────────────────────────────────────────────┘

词典消歧 (fix omni-g-tonewords-03/-07, 2026-06-11):
    加载时对每部词典的 positive∩negative 跨类重叠词 (jiang_2021 21 词 /
    you_2018 5 词) 按 LM 2011 JF 惯例**双侧剔除** + 日志披露 — 旧实现
    negative 循环 last-writer-wins 静默判负。clarity 的 definite∩ambiguous
    重叠 ('不可') 同样双侧剔除。故运行时词条数 < 上表原始计数。

聚合测度的固定词典 (fix omni-g-tonewords-01/-05, 2026-06-11):
    pos_ratio / neg_ratio / msent_score 的计数基从"逐篇匹配数最多的词典"
    (best-dict, 测量工具跨观测漂移) 改为 **5 词典固定 union 词典**
    (build_union_dictionary: 并集 + 重叠词极性多数票消解, 平票剔除),
    兑现 Tetlock 2007 / Garcia 2013 / Henry 2008 的固定词表构念。

语言学规则增强：
    - 否定词处理（翻转极性，窗口 = NEGATION_WINDOW 个分词单元）
    - 程度副词处理（放大/缩小情感强度，六级权重体系）
    - 转折连词处理（转折后权重提升 ADVERSATIVE_BOOST 倍）

性能优化：
    - frozenset 替代 set 加速 O(1) 查找
    - jieba 静默初始化
    - joblib 并行分批处理

输入：
    阶段21输出的 Parquet 文件（经过 LLM 语义精筛确认的银行金融科技新闻）

输出：
    追加各词典的得分、标签和匹配详情列

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 22_tone_words.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 stage 21 输出 `21_tone_llms.parquet` (config 键 output_21_tone_llms; 取其 `content_full`/`content_ctx`/`content_ss`/`内容`/`标题` 等列)。

**处理步骤**: ①`load_all_dictionaries()` 延迟加载五部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018) + 跨类重叠词双侧剔除 + `_inject_custom_dicts_to_jieba` 注入 jieba 自定义词; ②可选 `build_idf_weights` 在与 TF 同一语料 (caller 传 content_full, 缺则回退 '内容') 上算 IDF 文档频率 (Gentzkow-Kelly-Taddy 2019 JEL §2.2), 公式 `log10(N/(1+df(w)))`, 均值归一(mean→1) 后 P1/P99 Winsorize, 文档级去重统计 N/df, 存 22_idf_weights.json; ③joblib 线程并行分批 `classify_batch`, 每批对每篇文章三轨调用打分; ④对每部词典每轨的 score 列做 Z-score 标准化 (`_zscore_or_nan`, σ 退化→整列 NaN); ⑤调 `enrich_with_num_intensity_dual_track` (外部模块导入) 三轨派生 `num_intensity_{full,ctx,ss}` (数值披露强度, Davis & Tama-Sweet 2012 CAR); ⑥写 parquet + 预览 CSV + 三轨分类报告。

**关键算法/公式**: 核心是 `_compute_sentiment_with_rules(tokens, dict, apply_degree, apply_adversative)` —— 逐 token 状态机施加语言学规则: 否定词翻转极性 (窗口 NEGATION_WINDOW=2 个分词单元)、程度副词六级权重缩放 (HowNet 六级体系 + Liu 2012, DEGREE_WORDS 由 config 注入)、转折连词后权重 ×ADVERSATIVE_BOOST(默认 1.5)、句末标点重置作用域 (Ding 2008 从句级)。最终分 = self-normalized Σ(final)/Σ|final| ∈ [-1,+1]。**negonly 消融变体**: `apply_degree=False & apply_adversative=False` 只保留否定翻转, 产 `{dict}_score_negonly`/`msent_negonly`, 用作'主结果对去掉程度/转折两条规则是否敏感'的稳健性 (实测 corr(full,negonly)≈0.998-0.999 高度共线, 是稳健性对照非独立信号)。另产 `pos_ratio`/`neg_ratio` (固定 union 词典计数 / word-token 数)、`msent_score`=(raw_neg−raw_pos)/(raw_pos+raw_neg) 原始极性计数 (零规则; framing ≈ Tetlock 2007/Garcia 2013/Henry 2008; 代码注 He et al. 2024 IRFA Eq.1)、clarity/可读性/词汇复杂度等 $0 测度族。

**输出列**: 每部词典 × 三轨的 `{dict}_score/zscore/idf_score/idf_zscore`、`{dict}_score_negonly`、跨词典 `pos_ratio/neg_ratio/msent_score/msent_negonly`、`num_intensity_{full,ctx,ss}`、可读性/复杂度列。

**外部依赖**: jieba (`==0.42.1` 冻结); 纯 CPU, 无 LLM/网络/API, $0; 无缓存锚点 (确定性来自 jieba 版本 + 词典文件)。

**DAG 位置**: 上游 stage 21 (`21_tone_llms.parquet`); 下游 stage 23 (BERT 读 `22_words_tone.parquet`)。STAGES_MAIN 阶段22。

■ 白话说明

这一步是'查字典版'的情绪打分: 准备好五本专门的中文金融情绪词典 (里面标好哪些词是褒义、哪些是贬义), 然后逐字逐词扫每篇新闻, 数褒义词、贬义词, 还会按中文语法做修正——遇到'不'就把后面词的好坏反过来 (不乐观=负面), 遇到'非常'就把强度放大, 遇到'但是/然而'就更看重转折后那半句话 (因为作者真实立场常在转折之后)。为什么需要它: 大模型那一步虽然聪明但也可能有偏差或'幻觉', 用一套透明、可解释、谁来跑都一样的词典法另算一遍, 等于给大模型的结论找了个独立的旁证 (论文里叫'稳健性检验')。如果两种方法算出的银行情绪走势一致, 结论就更可信; 如果只用一种, 审稿人会质疑是不是方法本身的偏差。它还专门留了一个'只做否定、不做程度和转折'的简化版本, 用来回答'我的主结果是不是过度依赖那两条修饰规则'——实测发现两者几乎一模一样, 正好证明结论稳。这一步不花钱、不联网, 同样按全文/银行相关段落/银行金科同句段落三种范围各算一遍。
========================================================================
"""

import json
import logging
import math
import os
import re
import string
import sys
import threading
import time
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

# Phase 7a-5: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 pipeline/sentiment/tone_words.py 出发, 上溯 3 层抵达 news_process/ 的父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

# v3.5.2 PR #3 集成: A1 LM 4 子词典 (uncert/litig/constr/modal_strong) + A2 FLS.
# 复用 v3.5.1 真双轨架构 (_dual_analyze 内对 content_full + content_ctx 各扫一次).
from news_process.core.config import load_config
from news_process.core.logging import log_memory_usage, log_stage_summary, setup_logging
from news_process.core.reporting import safe_save_preview_csv
from news_process.pipeline.sentiment.forward_looking import (  # noqa: E402
    compute_fls_for_text,
)
from news_process.pipeline.sentiment.lexical_complexity import (  # noqa: E402
    LEXICAL_COMPLEXITY_KEYS,
    WORD_COUNT_KEY,
    compute_lexical_complexity,
)
from news_process.pipeline.sentiment.lm_non_sentiment import (  # noqa: E402
    _LMFLS_NONWORD_RE,
    load_lm_non_sentiment_dicts,
)

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)  # 抑制 jieba 的 INFO 级别日志输出
except ImportError:
    raise ImportError("请安装 jieba: pip install jieba")

# ============================================================================
# 1. 全局配置和初始化
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "22_tone_words"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

# 从配置中获取情感分析参数
SENTIMENT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_words', {})

# 词典文件路径
TONE_DICTS_FILE = CONFIG['paths'].get(
    'tone_dicts_file',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'tone_dicts.json')
)


# ============================================================================
# 2. 语言学规则常量（从 config/sentiment.yaml 加载; config.yaml 为 legacy stub）
#
# 设计依据与参考文献（APA 7th Edition，附带有效 DOI 链接）：
#
#   否定词判定：
#     - Jia, L., Yu, C., & Meng, W. (2009). The effect of negation on sentiment analysis and retrieval effectiveness. 
#       In Proceedings of the 18th ACM Conference on Information and Knowledge Management (CIKM '09), 1827-1830.
#       https://doi.org/10.1145/1645953.1646241
#     - Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. 
#       Foundations and Trends® in Information Retrieval, 2(1-2), 1-135.
#       https://doi.org/10.1561/1500000001
#
#   程度副词权重矩阵：
#     - Li, F., Huang, M., & Zhu, X. (2010). Sentiment analysis with global topics and local dependency. 
#       In Proceedings of the 24th AAAI Conference on Artificial Intelligence (AAAI '10), 1371-1376.
#       https://doi.org/10.1609/aaai.v24i1.7523
#     - Liu, B. (2012). Sentiment analysis and opinion mining. Morgan & Claypool Publishers.
#       https://doi.org/10.2200/s00416ed1v01y201204hlt016
#     - Kennedy, A., & Inkpen, D. (2006). Sentiment classification of movie reviews using contextual valence shifters. 
#       Computational Intelligence, 22(2), 110-125.
#       https://doi.org/10.1111/j.1467-8640.2006.00277.x
#
#   转折连词动态增强：
#     - Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. 
#       In Proceedings of the 2008 International Conference on Web Search and Data Mining (WSDM '08), 231-240.
#       https://doi.org/10.1145/1341531.1341561
#     - Wang, F., Wu, Y., & Qiu, L. (2012). Effectively exploiting sequence-level combinations of multiple features for Chinese sentiment analysis. 
#       In Proceedings of COLING 2012: Posters, 1311-1320.
#       https://aclanthology.org/C12-2128/
# ============================================================================

# ── 否定词集合（frozenset：不可变 + O(1) 查找） ──
# 遇到否定词时，将其后 NEGATION_WINDOW 个分词单元内的情感词极性翻转。
NEGATION_WORDS: frozenset[str] = frozenset(SENTIMENT_PARAMS.get('negation_words', []))

# ── 程度副词及其权重倍数 ──
# 权重含义：>1 程度加强，<1 程度减弱
# 分级依据：HowNet 六级程度体系 + Liu(2012) 三级线性近似
DEGREE_WORDS: dict[str, float] = SENTIMENT_PARAMS.get('degree_words', {})

# ── 转折连词集合 ──
# 转折后的内容更能反映作者真实立场（"末尾效应"）
ADVERSATIVE_WORDS: frozenset[str] = frozenset(SENTIMENT_PARAMS.get('adversative_words', []))

# 转折后权重提升倍数
ADVERSATIVE_BOOST: float = float(SENTIMENT_PARAMS.get('adversative_boost', 1.5))

# ── 句末标点集合（句法边界标记）──
# 遇到句末标点时重置转折/否定/程度状态，确保作用域限定为当前句
# 学术依据: Ding, Liu & Yu (2008, WSDM) 的转折效应作用域为从句级别
# 注意: 不包含逗号——逗号连接同一复句内的从句, 转折效应理应跨越
SENTENCE_END_MARKERS: frozenset[str] = frozenset(
    SENTIMENT_PARAMS.get('sentence_end_markers', ['。', '！', '？', '!', '?', '；', ';'])
)

# 否定词有效作用窗口（向后影响的分词单元数）
# 设为 2：覆盖"不 [程度副词] 情感词"结构（如"不太 乐观"）
NEGATION_WINDOW = SENTIMENT_PARAMS.get('negation_window', 2)




# ============================================================================
# 3. 词典加载
# ============================================================================

# v3.5.1 A1: Lexical Clarity 词典 lazy cache
# 锚定: Loughran & McDonald (2011 JF 66:1) uncertain dictionary;
#       You et al. (2018) hhx055 Chinese adaptation Panel C 388 词 / Panel D 178 词
# 与现有 5 词典 (positive/negative score) 并存; clarity 走独立 frozenset 路径以 O(1) 查找
_CLARITY_DICTS: tuple[frozenset, frozenset] | None = None


def load_clarity_dictionaries() -> tuple[frozenset, frozenset]:
    """加载 you_2018 Panel C (definite) + Panel D (ambiguous) 词典 (v3.5.1 A1 真双轨激活).

    Returns:
        tuple[frozenset, frozenset]: ``(definite_set, ambiguous_set)``
            definite_set = 388 词 (Panel C, You 2018);
            ambiguous_set = 178 词 (Panel D, You 2018).
            注 (fix omni-g-tonewords-03): definite∩ambiguous 跨类重叠词双侧剔除
            后实际为 387 / 177 词 (剔除 '不可' 1 词, 见加载段日志披露)。

    锚定文献:
        - Loughran & McDonald (2011) JF 66(1) uncertain dictionary
        - You et al. (2018) hhx055 中文金融情感词典 Panel C/D
        - Bonsall et al. (2017) JAE 63(2-3) 信息环境模糊度框架

    与 v3.4.0 及之前差异: 此前 you_2018.definite/ambiguous "仅存档" (tone_dicts.json
    含 keys 但无消费); v3.5.1 激活为真双轨独立扫描指标.
    """
    global _CLARITY_DICTS
    if _CLARITY_DICTS is not None:
        return _CLARITY_DICTS

    def_set: frozenset = frozenset()
    amb_set: frozenset = frozenset()
    if os.path.exists(TONE_DICTS_FILE):
        try:
            with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            you = data.get('you_2018', {})
            if isinstance(you, dict):
                def_set = frozenset(w.strip() for w in you.get('definite', []) if w and isinstance(w, str))
                amb_set = frozenset(w.strip() for w in you.get('ambiguous', []) if w and isinstance(w, str))
                # fix(omni-g-tonewords-03, 2026-06-11): definite∩ambiguous 跨类重叠词
                # (实测 '不可' 1 词) 双侧剔除 — 旧实现同词双计, 在 clarity_score 中
                # 抵消但同时虚增 frac_definite 与 frac_ambiguous; LM 2011 惯例为剔除
                # 极性/类别歧义词。剔除清单日志披露。
                _cross = def_set & amb_set
                if _cross:
                    logger.warning(
                        f"clarity definite∩ambiguous 跨类重叠 {len(_cross)} 词已双侧剔除 "
                        f"(fix omni-g-tonewords-03): {sorted(_cross)}")
                    def_set = def_set - _cross
                    amb_set = amb_set - _cross
        except Exception as e:
            logger.error(f"v3.5.1 A1 clarity 词典加载失败: {e}")

    if def_set or amb_set:
        logger.info(f"v3.5.1 A1 clarity 词典加载: definite={len(def_set)} 词, ambiguous={len(amb_set)} 词")
    else:
        logger.warning("v3.5.1 A1 clarity 词典空 (you_2018 Panel C/D 未找到)")

    _CLARITY_DICTS = (def_set, amb_set)
    return _CLARITY_DICTS


def _compute_clarity_for_text(text: str, def_set: frozenset, amb_set: frozenset) -> dict[str, float]:
    """对**单一文本**独立扫描派生 clarity 指标 (v3.5.1 A1 真双轨核心).

    此函数是真双轨的关键: ``_dual_analyze`` 对 content_full 和 content_ctx 各调用一次,
    得到独立的 clarity_score_full_i 和 clarity_score_ctx_i — 与项目现有 ``_analyze_single_article``
    的双轨契约一致 (per stage3_v3_5_1 plan v0.3 §2.1.1 修 R3-C1).

    分词流: tone tokenizer (独立 jieba.Tokenizer 实例, 见 ``_get_tone_tokenizer``) +
    去空字符 token (与 ``_analyze_single_article`` 一致).
    分母 (fix omni-g-tonewords-02/-12, 2026-06-11) = **word-token** 数 — 排除纯标点/
    纯数字 token (复用 ``lm_non_sentiment._LMFLS_NONWORD_RE``, 与 2026-06-10 lmfls-01
    的 LM/FLS 分母修复同口径; 旧分母含 ~19% 标点/数字 token, 逐篇 14.5–25% 非常数稀释)。
    仍为"未去停用词"版 (paper §3.4 disclosure 不变)。

    Args:
        text: 任意单一文本 (典型为 content_full 或 content_ctx).
        def_set: frozenset of definite words (388, You 2018 Panel C).
        amb_set: frozenset of ambiguous words (178, You 2018 Panel D).

    Returns:
        dict: {
            'n_definite': int,
            'n_ambiguous': int,
            'n_tokens_clarity_base': int (= word-token 数, 排除纯标点/纯数字 token),
            'frac_definite': float | None (分母=0 时 NA via float('nan')),
            'frac_ambiguous': float | None,
            'clarity_score': float | None (∈ [-1, +1] = frac_definite - frac_ambiguous),
        }
    """
    if not isinstance(text, str) or not text.strip():
        return {
            'n_definite': 0,
            'n_ambiguous': 0,
            'n_tokens_clarity_base': 0,
            'frac_definite': float('nan'),
            'frac_ambiguous': float('nan'),
            'clarity_score': float('nan'),
        }

    tokens = list(_get_tone_tokenizer().cut(text))
    tokens = [t for t in tokens if t.strip()]
    # fix(omni-g-tonewords-02, 2026-06-11): 分母 word-token 化 — 排除纯标点/纯数字
    # token (与 lm_non_sentiment lmfls-01 修复同口径); 分子 def/amb 词均为真词,
    # 标点/数字本不命中, 仅分母收紧。
    word_tokens = [t for t in tokens if not _LMFLS_NONWORD_RE.fullmatch(t.strip())]
    n_tokens = len(word_tokens)

    if n_tokens == 0:
        return {
            'n_definite': 0, 'n_ambiguous': 0, 'n_tokens_clarity_base': 0,
            'frac_definite': float('nan'), 'frac_ambiguous': float('nan'),
            'clarity_score': float('nan'),
        }

    n_def = sum(1 for t in word_tokens if t in def_set)
    n_amb = sum(1 for t in word_tokens if t in amb_set)
    frac_def = n_def / n_tokens
    frac_amb = n_amb / n_tokens
    return {
        'n_definite': n_def,
        'n_ambiguous': n_amb,
        'n_tokens_clarity_base': n_tokens,
        'frac_definite': round(frac_def, 6),
        'frac_ambiguous': round(frac_amb, 6),
        'clarity_score': round(frac_def - frac_amb, 6),
    }


def load_all_dictionaries() -> list[tuple[str, dict[str, float]]]:
    """从统一的 tone_dicts.json 加载所有情感词典。

    Returns:
        list[tuple]: ``[(dict_name, {word: score}), ...]``
            其中 score > 0 表示正面词，score < 0 表示负面词，
            score = 0.5 表示政治正面词（du_2022 特有）。

    跨类重叠消解 (fix omni-g-tonewords-03/-07, 2026-06-11):
        旧实现 negative 循环无 ``word not in d`` 守卫 (对照 political_positive 有),
        positive∩negative 重叠词被静默 last-writer-wins 判负 (jiang_2021 21 词 /
        you_2018 5 词, 含 9.7% 文档命中的 '打破')。现按 LM 2011 JF 惯例对重叠词
        **双侧剔除** + logger.warning 披露清单与数量。
    """
    logger.info(f"正在从 {TONE_DICTS_FILE} 加载情感词典...")

    all_dict_data = {}
    if os.path.exists(TONE_DICTS_FILE):
        try:
            with open(TONE_DICTS_FILE, 'r', encoding='utf-8') as f:
                all_dict_data = json.load(f)
            if not isinstance(all_dict_data, dict):
                logger.error(f"词典文件格式错误: 期望 JSON 对象，实际为 {type(all_dict_data).__name__}")
                all_dict_data = {}
        except json.JSONDecodeError as e:
            logger.error(f"词典文件 JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"加载 {TONE_DICTS_FILE} 失败: {e}")
    else:
        logger.warning(f"词典文件未找到: {TONE_DICTS_FILE}")

    dictionaries = []
    dict_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']

    for dict_key in dict_keys:
        entry = all_dict_data.get(dict_key, {})
        dict_name = entry.get('name', dict_key)
        d = {}

        # 从 JSON 中的 positive/negative 列表构建 {word: score}
        # fix(omni-g-tonewords-03/-07, 2026-06-11): positive∩negative 跨类重叠词显式
        # 消解 — 双侧剔除 (LM 2011 惯例) + 日志披露, 替代旧的静默 last-writer-wins 判负。
        pos_words = {str(w).strip() for w in entry.get('positive', []) if str(w).strip()}
        neg_words = {str(w).strip() for w in entry.get('negative', []) if str(w).strip()}
        cross_overlap = pos_words & neg_words
        if cross_overlap:
            logger.warning(
                f"  {dict_key}: positive∩negative 跨类重叠 {len(cross_overlap)} 词已双侧剔除 "
                f"(LM 2011 惯例, fix omni-g-tonewords-03): {sorted(cross_overlap)}")
        # sorted 保证 dict 插入序确定 (可复现性)
        for word in sorted(pos_words - cross_overlap):
            d[word] = 1.0
        for word in sorted(neg_words - cross_overlap):
            d[word] = -1.0
        # 数量断言 (fix omni-g-tonewords-03): 剔除后正负词条数恒等校验 (防回归静默覆盖)
        assert len(d) == len(pos_words - cross_overlap) + len(neg_words - cross_overlap), (
            f"{dict_key}: 跨类重叠消解后词条数不恒等 (存在残余覆盖)")

        # Du et al. (2022) 特有：政治正面词以较低权重 0.5 加入
        for word in entry.get('political_positive', []):
            word = str(word).strip()
            if word and word not in d:  # 避免覆盖已有正面词
                d[word] = 0.5

        dictionaries.append((dict_key, d))

        pos_cnt = sum(1 for v in d.values() if v > 0)
        neg_cnt = sum(1 for v in d.values() if v < 0)
        pol_cnt = sum(1 for v in d.values() if v == 0.5)

        if d:
            logger.info(f"  {dict_key} ({dict_name}): {len(d)} 个词汇 "
                        f"(正面={pos_cnt}, 负面={neg_cnt})")
            # 各词典子类别详细统计
            if dict_key == 'du_2022' and pol_cnt > 0:
                logger.info(f"    └─ political_positive: {pol_cnt} 词 (权重=0.5)")
        else:
            logger.info(f"  {dict_key} ({dict_name}): 空（待填充）")

    total_loaded = sum(len(d) for _, d in dictionaries)
    non_empty = sum(1 for _, d in dictionaries if len(d) > 0)
    logger.info(f"词典加载完成: {non_empty}/{len(dict_keys)} 个词典有效, 共 {total_loaded} 个词汇条目")

    return dictionaries


def build_union_dictionary(
    dictionaries: list[tuple[str, dict[str, float]]],
) -> dict[str, float]:
    """构造 5 词典固定 union 词典 (fix omni-g-tonewords-01/-05, 2026-06-11).

    动机: pos_ratio / neg_ratio / msent_score 旧实现取"逐篇匹配数最多的词典"
    (best-dict), 测量工具跨观测漂移 (盘上实证: 胜出词典逐篇切换, yao 51%/du 41%),
    与所引 Tetlock 2007 JF / Garcia 2013 JF / Henry 2008 的**固定词表**构念冲突。
    本函数把 5 部词典合并为单一固定词表, 全样本统一使用。

    极性消解规则 (确定性, 与词典顺序无关):
        1. 每词收集其出现的所有词典的 score;
        2. 极性 = 正/负出现次数的**多数票**;
        3. 平票 (正负词典数相同) → 极性歧义, 剔除 (LM 2011 惯例);
        4. 幅值 = 胜出极性内最大 |score| (政治正面词 0.5 仅当无 ±1.0 同向词时保留)。

    Args:
        dictionaries: ``load_all_dictionaries()`` 的输出 [(name, {word: score}), ...]。

    Returns:
        dict[str, float]: 固定 union 词典 {word: score}。

    白话: 以前算总体正负词占比时, 每篇文章各自挑"匹配词最多的那部词典"
    来数, 等于不同文章用不同的尺子量长度, 结果不可比。现在把 5 部词典
    合成一张固定大词表, 全部文章统一用它。同一个词若在不同词典里有的
    判正有的判负, 就按"判正的词典多还是判负的多"投票定极性; 票数打平
    说明这词本身有歧义, 干脆不要。
    """
    polarity_votes: dict[str, list[float]] = {}
    for _name, d in dictionaries:
        for word, score in (d or {}).items():
            polarity_votes.setdefault(word, []).append(score)

    union: dict[str, float] = {}
    n_dropped = 0
    for word, scores in polarity_votes.items():
        n_pos = sum(1 for s in scores if s > 0)
        n_neg = sum(1 for s in scores if s < 0)
        if n_pos == n_neg:
            n_dropped += 1  # 平票 → 极性歧义词剔除
            continue
        sign = 1.0 if n_pos > n_neg else -1.0
        magnitude = max(abs(s) for s in scores if (s > 0) == (sign > 0))
        union[word] = sign * magnitude
    if n_dropped:
        logger.info(f"union 词典: 跨词典极性平票剔除 {n_dropped} 词 (LM 2011 惯例)")
    return union


# union 词典 lazy cache: 以 (对象 id, 各词典 (name, 词条数) 指纹) 为 key (main() 加载后
# 构建一次; 测试直接改写 ALL_DICTIONARIES 时自动失效重建)。指纹防 CPython id 回收复用
# 造成陈旧缓存 (旧 list 被 GC 后新 list 可能分配到同一地址)。
_UNION_DICT_CACHE: tuple[Any, dict[str, float]] | None = None


def _get_union_dictionary() -> dict[str, float]:
    """返回与当前 ALL_DICTIONARIES 对应的固定 union 词典 (带身份+指纹缓存)."""
    global _UNION_DICT_CACHE
    dicts = ALL_DICTIONARIES or []
    key = (id(ALL_DICTIONARIES),
           tuple((name, len(d or {})) for name, d in dicts))
    if _UNION_DICT_CACHE is not None and _UNION_DICT_CACHE[0] == key:
        return _UNION_DICT_CACHE[1]
    union = build_union_dictionary(dicts)
    _UNION_DICT_CACHE = (key, union)
    return union


# ============================================================================
# 4. 语言学规则情感计算引擎
# ============================================================================

def _compute_sentiment_with_rules(tokens: list[str], sentiment_dict: dict[str, float]) -> tuple[float, float, int, int, list[dict[str, Any]]]:
    """对分词序列使用语言学规则增强的词典法计算情感得分。

    内部状态机：
      遍历 token 序列，维护三个状态变量：
        ① negation_remaining: 否定窗口剩余 token 数（>0 则极性翻转）
        ② degree_multiplier:  当前程度副词倍率（碰到情感词时消费并重置）
        ③ adversative_active:  是否处于转折后区域（遇句末标点重置, Ding 2008 从句级作用域）

    状态转移规则：
        token ∈ SENTENCE_END_MARKERS → 重置转折、否定、程度（句法边界）
        token ∈ ADVERSATIVE_WORDS → 激活转折，重置否定和程度
        token ∈ NEGATION_WORDS    → 设置否定窗口
        token ∈ DEGREE_WORDS      → 设置程度倍率
        token ∈ sentiment_dict    → 计算 score = base × degree × negation × adversative
        其他                       → 重置程度副词（未被消费）

    归一化 (fix omni-g-tonewords-09, 2026-06-11):
        normalized_score = Σ(final_score) / Σ|final_score| ∈ [-1, +1]。
        旧分母为裸匹配词数 (pos_count+neg_count), 分子含程度副词(最高×3.0)×转折(×1.5)
        放大 → 理论值域 ±4.5, 盘上实测 4/5 词典 13% 文章 >1 (max 1.286), 破坏与
        LLM/BERT 有界 tone 轨的可比性且 ±0.1 标签阈值按单位区间校准。改加权幅度和
        分母后恒有界; 无匹配时仍返回 0.0 (中性)。

    Args:
        tokens:         分词结果列表。
        sentiment_dict: ``{word: score}`` 情感词典。

    Returns:
        tuple: (raw_score, normalized_score, pos_count, neg_count, matched_words)

    白话: 不是见到情感词就简单加减分, 而是看上下文修饰: "不乐观"里的
    "不"会把"乐观"翻成负面; "非常好"的"非常"把分数放大; "但是"之后的话
    往往才是作者真实态度, 给更高权重; 一到句号这些修饰效果就清零,
    不会跨句串味。最后把总分除以各词加权后的绝对值之和, 保证结果
    永远落在 -1 到 +1 之间, 和 LLM/BERT 的打分尺度能对得上。
    """
    total_score: float = 0.0
    total_abs_score: float = 0.0
    pos_count: int = 0
    neg_count: int = 0
    matched_words: list[dict[str, Any]] = []

    negation_remaining: int = 0
    degree_multiplier: float = 1.0
    adversative_active: bool = False

    for token in tokens:
        # ── 句法边界: 句末标点重置全部句法级状态 ──
        # Ding et al. (2008): 转折效应限定为从句级 (Clause-level)
        if token in SENTENCE_END_MARKERS:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue

        # 检查转折连词
        if token in ADVERSATIVE_WORDS:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue

        # 检查否定词
        if token in NEGATION_WORDS:
            negation_remaining = NEGATION_WINDOW
            continue

        # 检查程度副词
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token]
            continue

        # 检查情感词
        if token in sentiment_dict:
            base_score = sentiment_dict[token]

            # 应用否定词翻转
            if negation_remaining > 0:
                base_score = -base_score

            # 应用程度副词
            final_score = base_score * degree_multiplier

            # 应用转折加权
            if adversative_active:
                final_score *= ADVERSATIVE_BOOST

            total_score += final_score
            # fix(omni-g-tonewords-09, 2026-06-11): 累积加权幅度和 Σ|final_score|
            # 作归一化分母 — 与分子同含 degree×adversative 权重 → 恒有界 [-1,1]
            total_abs_score += abs(final_score)

            if final_score > 0:
                pos_count += 1
            elif final_score < 0:
                neg_count += 1

            matched_words.append({
                'word': token,
                'base': sentiment_dict[token],
                'final': round(final_score, 4),
                'boosted': adversative_active,
            })

            degree_multiplier = 1.0  # 已消费程度副词
        else:
            degree_multiplier = 1.0  # 非情感词重置程度副词

        # 否定窗口递减
        if negation_remaining > 0:
            negation_remaining -= 1

    # 归一化 (fix omni-g-tonewords-09, 2026-06-11): 分母改 Σ|final_score| (加权幅度和)。
    # 旧分母 = 裸匹配词数 (pos_count+neg_count), 分子被 degree(≤3.0)×adversative(1.5)
    # 放大 → 理论值域 ±4.5, 盘上实测 13% 文章 >1; 现恒有界 ∈ [-1, +1]。
    normalized_score = total_score / total_abs_score if total_abs_score > 0 else 0.0

    return total_score, normalized_score, pos_count, neg_count, matched_words


def _score_to_label(normalized_score: float, pos_threshold=0.1, neg_threshold=-0.1) -> str:
    """将归一化得分映射为情感标签。

    Args:
        normalized_score: 归一化情感得分。
        pos_threshold:    正面阈值（默认 0.1）。
        neg_threshold:    负面阈值（默认 -0.1）。

    Returns:
        str: ``"正面"`` / ``"中性"`` / ``"负面"``
    """
    if normalized_score > pos_threshold:
        return "正面"
    elif normalized_score < neg_threshold:
        return "负面"
    else:
        return "中性"





def _compute_readability(content: str, tokens: list[str]) -> dict[str, float]:
    """计算中文文本可读性的三维度代理指标。

    学术依据:
      Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. 
      The Journal of Finance, 69(4), 1643-1671.
      https://doi.org/10.1111/jofi.12162
      — 指出 Gunning-Fog Index 不适用于金融文本（多音节商业术语
      如 "financial", "company" 被误判为"复杂"），建议使用替代度量。

      Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). 
      A plain English measure of financial reporting readability. 
      Journal of Accounting and Economics, 63(2-3), 329-357.
      https://doi.org/10.1016/j.jacceco.2017.03.002
      — 提出 Bog Index 捕捉 SEC Plain English 属性，但依赖英文句法。

    对于中文文本，采用以下三个维度的代理指标：

    1. avg_sentence_len (ASL): 平均句长（字符/句）— 越长越难读
    2. type_token_ratio (TTR): 词汇丰富度（唯一词/真实词频）— 越高越复杂
    3. char_per_word (CPW): 平均词长（真实字符/真实词频）— 越长越倾向专业术语

    Args:
        content: 原始文本字符串。
        tokens:  jieba 分词结果列表。

    Returns:
        dict: {'avg_sentence_len': float, 'type_token_ratio': float,
               'char_per_word': float}
    """
    # 彻底剔除标点与空白，仅保留实际词汇计算可读性丰富度指标，防止无意义标点夸大词汇数量
    punctuation_set = frozenset(string.punctuation + "“”‘’：；！？（）【】「」《》、，。·…—\n\t \r")
    real_tokens = [t for t in tokens if t not in punctuation_set and not t.isspace() and t]

    # 1. 平均句长 (ASL) — 按中文句末标点分割，保留基于整个内容原始结构的度量
    sentences = re.split(r'[。！？!?；;]', content)
    sentences = [s for s in sentences if len(s.strip()) > 0]
    n_sentences = max(len(sentences), 1)
    avg_sentence_len = sum(len(s.strip()) for s in sentences) / n_sentences

    # 2. Type-Token Ratio (TTR) — 词汇丰富度
    n_real_tokens = max(len(real_tokens), 1)
    ttr = len(set(real_tokens)) / n_real_tokens

    # 3. 平均词长 (CPW) — 字符级词复杂度
    total_chars = sum(len(t) for t in real_tokens)
    cpw = total_chars / n_real_tokens

    return {
        'avg_sentence_len': round(avg_sentence_len, 2),
        'type_token_ratio': round(ttr, 4),
        'char_per_word': round(cpw, 4),
    }


# ============================================================================
# 4B. IDF 加权稳健性检验 (Gentzkow, Kelly & Taddy, 2019, JEL §2.2)
# ============================================================================

def build_idf_weights(
    df: pd.DataFrame,
    dictionaries: list[tuple[str, dict[str, float]]],
    text_col: str = '内容',
) -> dict[str, dict[str, float]]:
    """基于全语料库计算每个词典中情感词的 IDF 权重。

    公式 (smooth IDF + 均值归一化 + Winsorization):
        raw_idf(w) = log₁₀(N / (1 + df(w)))
        normalized_idf(w) = raw_idf(w) / mean(raw_idf)
        final_idf(w) = Winsorize(normalized_idf, P1, P99)

    学术依据:
      Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. 
      Journal of Economic Literature, 57(3), 535-574. §2.2: TF-IDF.
      https://doi.org/10.1257/jel.20181020

      Manning, C. D., Raghavan, P., & Schütze, H. (2008). 
      Introduction to Information Retrieval. Cambridge University Press. 
      Ch. 6.2.1: smooth IDF 公式。

      Fama, E. F., & French, K. R. (1993). Common risk factors in the returns on stocks and bonds. 
      Journal of Financial Economics, 33(1), 3-56.
      https://doi.org/10.1016/0304-405X(93)90023-5
      — Winsorization (P1/P99) 标准做法。

    设计决策:
      1. 为了和特征抽取保持严格语义同构，使用与 TF 匹配同一注入态的 tone tokenizer
         (``_get_tone_tokenizer``) 并行分词来统计 Document Frequency，
         坚决废除 Aho-Corasick 子匹配以避免把 “大家” 错误计为 “大”。
      2. IDF 在与 TF 加权同一语料（caller 传 text_col='content_full'，含标题；缺则回退
         '内容'）上统一计算一次，两轨共享 (fix 2026-06-10: 原裸 '内容' 与 TF 打分语料不一致)。
      3. 均值归一化确保 IDF 加权后得分量级 ≈ 等权版，可共享阈值。
      4. P1/P99 Winsorization 防止极端稀有词主导或极高频词归零。
      5. DF/N 按**唯一文档**统计 (fix omni-g-tonewords-04, 2026-06-11): stage 21 输出
         是 (article×bank) 展开表 (同篇多银行文章重复至多 8 行), 旧实现 N=len(df)+逐行
         DF 使重复文章的 df(w) 与 N 同向膨胀, 偏离 Gentzkow-Kelly-Taddy 2019 JEL §2.2 /
         Manning IIR 6.2.1 的文档级 DF 定义。现以文本内容自身为唯一键去重 (同 content
         = 同 document)。

    Args:
        df:           全量 DataFrame，需含 text_col 列。
        dictionaries: 词典列表 [(name, {word: score}), ...]。
        text_col:     文本列名。

    Returns:
        dict: {dict_name: {word: capped_normalized_idf}}

    白话: 像"发展""提高"这类词几乎每篇新闻都有, 信息量低; 像"违约""挤兑"
    这类词很少出现, 一出现就很说明问题。IDF 就是按"一个词在多少篇文章里
    出现过"给它定权重: 越常见权重越低, 越稀有权重越高。再做两步保险:
    (1) 把权重整体缩放到平均为 1, 让加权版得分和不加权版量级差不多,
    能共用同一套阈值; (2) 把最极端 1% 的权重削平 (Winsorize), 防止某个
    超稀有词一词定乾坤。统计文档数时同一篇文章只算一次 (去重), 不让
    "一篇新闻提到 8 家银行被展开成 8 行"虚增计数。
    """
    # fix(omni-g-tonewords-04, 2026-06-11): 唯一文档去重 — N 与 df(w) 均在去重后语料上统计
    texts = (
        df[text_col].fillna('').astype(str).drop_duplicates().tolist()
        if len(df) > 0 else []
    )
    N = len(texts)
    if N == 0:
        logger.warning("IDF: 语料为空，所有权重降级为 1.0")
        return {name: {w: 1.0 for w in d} for name, d in dictionaries}

    # 1. 抽取全局词典内词汇以快速过滤
    all_words = set()
    for _, d in dictionaries:
        all_words.update(d.keys())

    if not all_words:
        return {name: {} for name, _ in dictionaries}

    # 2. 定义局部并行切词函数，解决匹配必须是完整 token 的缺陷
    # fix(omni-g-tonewords-10, 2026-06-11): 用与 TF 匹配同一注入态的 tone tokenizer
    # (而非全局 jieba) 统计 DF — 注入隔离后全局分词器无领域复合词, 若仍用全局会把
    # 多字情感词切碎, DF 系统性=0 → IDF 与 TF 语义不同构。
    _tk = _get_tone_tokenizer()

    def _compute_chunk_df(chunk_texts):
        local_df = Counter()
        for text in chunk_texts:
            tokens_in_doc = set(_tk.cut(text)) & all_words
            local_df.update(tokens_in_doc)
        return local_df

    # 3. 执行多线程分块并行的 tone tokenizer 切词统计 (去重后唯一文档语料)
    batch_size = 2000
    num_batches = max(1, (N - 1) // batch_size + 1)
    chunks = [texts[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    logger.info(f"IDF: 正在使用 jieba 并行计算文档频率以保持语义精确同构 (唯一文档 {N} 篇, {num_batches} 个批次)...")
    results = Parallel(n_jobs=-1, prefer='threads')(
        delayed(_compute_chunk_df)(chunk) for chunk in chunks
    )
    
    doc_freq = Counter()
    for local_df in results:
        doc_freq.update(local_df)

    # 3. 为每个词典分别计算 IDF → 均值归一化 → Winsorize
    result: dict[str, dict[str, float]] = {}
    for dict_name, sentiment_dict in dictionaries:
        if not sentiment_dict:
            result[dict_name] = {}
            continue

        raw_idf = {}
        for word in sentiment_dict:
            df_w = doc_freq.get(word, 0)
            raw_idf[word] = math.log10(N / (1 + df_w))

        # 均值归一化（使 IDF 加权后量级 ≈ 等权版）
        values = list(raw_idf.values())
        mean_val = float(np.mean(values)) if values else 1.0
        if mean_val > 0:
            normed = {w: v / mean_val for w, v in raw_idf.items()}
        else:
            normed = {w: 1.0 for w in raw_idf}

        # P1/P99 Winsorization (Fama & French 1993)
        normed_vals = np.array(list(normed.values()))
        if len(normed_vals) >= 2:
            p1, p99 = float(np.percentile(normed_vals, 1)), float(np.percentile(normed_vals, 99))
            capped = {w: float(np.clip(v, p1, p99)) for w, v in normed.items()}
        else:
            capped = dict(normed)

        result[dict_name] = capped

    return result


def _build_idf_weighted_dict(
    sentiment_dict: dict[str, float],
    idf_weights: dict[str, float],
) -> dict[str, float]:
    """将 IDF 权重乘入情感词典的 base_score。

    weighted_score(w) = base_score(w) × idf_weight(w)

    保留 base_score 的符号（正/负极性）和非对称幅值：
    - 正面词: +1.0 × idf
    - 负面词: -1.0 × idf
    - du_2022 政治词: +0.5 × idf（保留较低权重）

    语言学规则引擎兼容性:
      生成的 idf_dict 可直接传入 _compute_sentiment_with_rules()，
      因为该函数仅关心 sentiment_dict[token] 的数值，
      否定/程度/转折规则在此之上叠加，与 IDF 权重正交。
    """
    return {
        word: base_score * idf_weights.get(word, 1.0)
        for word, base_score in sentiment_dict.items()
    }


# ============================================================================
# 5. 单篇文章分析
# ============================================================================

# 全局词典变量（延迟加载，在 main() 中初始化）
ALL_DICTIONARIES = None
IDF_DICTIONARIES = None  # IDF 加权词典（稳健性检验，在 main() 中初始化）

_JIEBA_INJECTED = False
_JIEBA_LOCK = threading.Lock()

# fix(omni-g-tonewords-10/-11, 2026-06-11): stage-22 词典匹配专用的**独立** jieba
# Tokenizer 实例 (注入隔离)。领域词注入只写入此实例, 全局 jieba.dt / jieba.posseg
# 保持纯净 → (a) lexical_complexity 的 posseg 词性不再被 add_word 的 tag='x' 回退
# 污染 (OOV 领域词如 '金融科技' 被当标点剔出分母, 全 8 列失真且与领域词密度逐篇
# 相关); (b) forward_looking 的 FLS 双门控不再被注入复合词吞掉 2 字门控 token
# ('目标'/'战略' 等), 兑现 forward-looking-jieba (2026-06-10) "刻意不用 add_word"
# 的修复设计; (c) 同一函数在注入态/非注入态 (生产 vs 单测/validation) 不再给出两套值。
_TONE_TOKENIZER: "jieba.Tokenizer | None" = None


def _get_tone_tokenizer() -> "jieba.Tokenizer":
    """返回 stage-22 词典匹配专用的独立 jieba.Tokenizer (lazy 单例, DCL 锁).

    fix(omni-g-tonewords-10/-11, 2026-06-11): 见 ``_TONE_TOKENIZER`` 注释 — 领域词
    注入 (``_inject_custom_dicts_to_jieba``) 只进此实例, 全局分词器零注入。
    消费方: ``_analyze_single_article`` (情感词典匹配) / ``_compute_clarity_for_text``
    / ``build_idf_weights`` (DF 统计) / LM 4 子词典扫描
    (经本文件 ``_compute_lm_non_sentiment_for_text_tone_tok`` 包装)。
    """
    global _TONE_TOKENIZER
    if _TONE_TOKENIZER is None:
        with _JIEBA_LOCK:
            if _TONE_TOKENIZER is None:
                _TONE_TOKENIZER = jieba.Tokenizer()
    return _TONE_TOKENIZER


def _inject_custom_dicts_to_jieba():
    global _JIEBA_INJECTED
    # 第一次检查 (无锁)：在绝大多数情况下，字典已被加载，直接返回，避免获取锁的系统开销
    if _JIEBA_INJECTED:
        return
    with _JIEBA_LOCK:
        # 第二次检查 (有锁)：防止多个线程同时越过第一次检查，排队获取锁后造成重复注入
        if _JIEBA_INJECTED:
            return

        """
        将所有情感词、银行名称、金融科技词汇注入**独立 tone tokenizer**，防止专业词汇被切碎。

        fix(omni-g-tonewords-10/-11, 2026-06-11): 注入目标从全局 jieba.dt 改为
        ``_get_tone_tokenizer()`` 的独立实例 — 全局分词器保持纯净, posseg 词性
        (lexical_complexity) 与 FLS 双门控 (forward_looking) 不再受注入副作用污染。

        [并发机理与锁机制依据]:
        jieba 底层维护字典树 (Trie tree)。在 joblib 或 concurrent.futures
        等多线程/多进程后端调用 add_word 时，若没有严格的互斥锁保护，会导致字典树的内部指针状态
        损坏 (Race Condition)，引发 KeyError 或分词结果不可逆的碎片化。
        此处严格采用 Double-Checked Locking (DCL) 模式保证只执行一次 O(n) 的插入操作。
        - Schmidt, D. C., & Harrison, T. (1997). Double-checked locking: An optimization pattern
          for efficiently initializing and accessing thread-safe objects. Pattern Languages of Program Design 3, 363-375.

        [领域词库基石依据]:
        Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks.
        The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
        """
        logger.info("正在将自定义领域词汇注入独立 tone tokenizer (全局 jieba 保持纯净)...")
        tk = _get_tone_tokenizer()
        added_count = 0

        # 1. 注入所有情感词典中的词汇
        for dict_name, sentiment_dict in ALL_DICTIONARIES:
            if sentiment_dict:
                for word in sentiment_dict.keys():
                    tk.add_word(word)
                    added_count += 1

        # 2. 注入银行名称库 (11_news_bank.py 的同源字典)
        bank_dict_path = CONFIG['paths'].get(
            'bank_names_file',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'bank_names.json')
        )
        if os.path.exists(bank_dict_path):
            try:
                with open(bank_dict_path, 'r', encoding='utf-8') as f:
                    bank_data = json.load(f)
                    if isinstance(bank_data, list):
                        for bank in bank_data:
                            if not isinstance(bank, dict): continue
                            std_name = bank.get('standard_name')
                            if std_name:
                                tk.add_word(str(std_name).strip())
                                added_count += 1
                            for variant in bank.get('variants', []):
                                if variant:
                                    tk.add_word(str(variant).strip())
                                    added_count += 1
            except Exception as e:
                logger.warning(f"未能加载银行词典注入jieba: {e}")

        # 3. 注入金融科技词典 (12_news_fintech.py 的同源字典)
        fintech_dict_path = CONFIG['paths'].get(
            'fintech_dict_file',
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'fintech_dict.json')
        )
        if os.path.exists(fintech_dict_path):
            try:
                with open(fintech_dict_path, 'r', encoding='utf-8') as f:
                    fintech_data = json.load(f)
                    if isinstance(fintech_data, list):
                        for word in fintech_data:
                            if word:
                                tk.add_word(str(word).strip())
                                added_count += 1
                    elif isinstance(fintech_data, dict):
                        for category, words_list in fintech_data.items():
                            if isinstance(words_list, list):
                                for word in words_list:
                                    if word:
                                        tk.add_word(str(word).strip())
                                        added_count += 1
            except Exception as e:
                logger.warning(f"未能加载金融科技词典注入jieba: {e}")

        # 4. 注入否定词与程度词增强规则库
        for word in NEGATION_WORDS:
            tk.add_word(word)
        for word in DEGREE_WORDS:
            tk.add_word(word)
        for word in ADVERSATIVE_WORDS:
            tk.add_word(word)

        # 5. 注入清晰度词典 (You & Zhang 2009 / You 2018)
        # fix(clarity_cn-01): 多字 clarity definite/ambiguous 词此前从未 add_word →
        # 被 jieba 切碎 (实测 67/541 多字词不可匹配, 12.4%), clarity_score 系统性低估。
        try:
            _def_set, _amb_set = load_clarity_dictionaries()
            for word in (_def_set | _amb_set):
                w = str(word).strip()
                if len(w) >= 2:  # 单字不受切分影响, 仅多字词需防碎
                    tk.add_word(w)
                    added_count += 1
        except Exception as e:  # noqa: BLE001
            logger.warning(f"未能加载清晰度词典注入jieba: {e}")

        # 6. 注入 LM 2011 JF 4 子词典 (uncert/litig/constr/modal)
        # fix(completeness-02): 与 clarity_cn-01 同型缺陷 — 多字 LM(18.5%) 词此前从未
        # add_word, 被 jieba 切碎永不命中, 致 LM frac 系统性漏匹配下偏。
        # fix(omni-g-tonewords-11, 2026-06-11): Li 2010 JAR FLS 前瞻词注入已**移除** —
        # 注入复合 FLS 标记 (如 '中长期目标') 会吞掉 forward_looking 双门控的 2 字
        # 门控 token ('目标'/'战略' 等, ≥3 字 substring 兜底无法补救), 正面冲突
        # forward-looking-jieba (2026-06-10) "刻意不用 add_word" 的修复设计; FLS 判定
        # 走全局纯净分词器 + 自带 ≥3 字 substring 兜底, 无需任何注入。
        try:
            from news_process.pipeline.sentiment.lm_non_sentiment import (
                load_lm_non_sentiment_dicts,
            )
            for _subset in load_lm_non_sentiment_dicts().values():
                for word in _subset:
                    w = str(word).strip()
                    if len(w) >= 2:
                        tk.add_word(w)
                        added_count += 1
        except Exception as e:  # noqa: BLE001
            logger.warning(f"未能加载 LM 非情感词典注入jieba: {e}")

        logger.info(f"成功注入 {added_count} 个领域自定义词汇到独立 tone tokenizer。")
        _JIEBA_INJECTED = True

# 注入操作延迟到 main() 中执行
# _inject_custom_dicts_to_jieba()


def _compute_lm_non_sentiment_for_text_tone_tok(
    text: str,
    dicts: dict[str, frozenset[str]],
) -> dict[str, float]:
    """LM 4 子词典扫描 — tone tokenizer 版 (fix omni-g-tonewords-10/-11 配套, 2026-06-11).

    与只读模块 ``lm_non_sentiment._compute_lm_non_sentiment_for_text`` 逐项同语义
    (lmfls-01 word-token 分母 / 空文本 NaN / 返回键结构), 唯一差异 = 分词器:
    用注入了 LM 多字词的独立 tone tokenizer (``_get_tone_tokenizer``) 而非全局
    jieba。注入隔离后全局分词器无 LM 复合词 — 若仍走全局, 多字 LM 词 (~18.5%)
    会被切碎永不命中, completeness-02 修复将静默回归。``lm_non_sentiment.py``
    按修复纪律只读, 故在本文件做 tokenizer 替换包装。

    Args:
        text: 待分析的中文文本。
        dicts: ``load_lm_non_sentiment_dicts()`` 的 4 子词典 dict。

    Returns:
        与 ``_compute_lm_non_sentiment_for_text`` 同构:
        {'n_tokens', 'n_uncert', 'frac_uncert', 'n_litig', 'frac_litig',
         'n_constr', 'frac_constr', 'n_modal_strong', 'frac_modal_strong'}
    """
    empty = {
        'n_tokens': 0,
        'n_uncert': 0, 'frac_uncert': float('nan'),
        'n_litig': 0, 'frac_litig': float('nan'),
        'n_constr': 0, 'frac_constr': float('nan'),
        'n_modal_strong': 0, 'frac_modal_strong': float('nan'),
    }
    if not text or not text.strip():
        return empty

    tokens = list(_get_tone_tokenizer().cut(text))
    # lmfls-01 同口径: 分母 = word-token 数 (排除纯标点/纯数字)
    word_tokens = [t for t in tokens if t.strip() and not _LMFLS_NONWORD_RE.fullmatch(t.strip())]
    n_tokens = len(word_tokens)
    if n_tokens == 0:
        return empty

    subsets = ('uncertainty', 'litigious', 'constraining', 'modal_strong')
    counts = {s: 0 for s in subsets}
    for tok in tokens:
        for s in subsets:
            if tok in dicts.get(s, frozenset()):
                counts[s] += 1

    return {
        'n_tokens': n_tokens,
        'n_uncert': counts['uncertainty'],
        'frac_uncert': counts['uncertainty'] / n_tokens,
        'n_litig': counts['litigious'],
        'frac_litig': counts['litigious'] / n_tokens,
        'n_constr': counts['constraining'],
        'frac_constr': counts['constraining'] / n_tokens,
        'n_modal_strong': counts['modal_strong'],
        'frac_modal_strong': counts['modal_strong'] / n_tokens,
    }


def _empty_article_result() -> dict:
    """空/无效/全空 token 文本的统一返回 (fix omni-g-tonewords empty-text contract, 2026-06-11).

    契约对称化: score / ratio / msent 空文本 → NaN (缺失语义, 与 clarity/LM/FLS
    的空文本 NaN 契约一致; 旧实现回填 0.0 伪中性, 在 panel 聚合中压低均值)。
    label 维持 '中性' (类别列, 供 stats 计数), 可读性三列维持 0.0 (长度类, 空文本
    长度为 0 是真值而非缺失)。
    """
    result: dict[str, Any] = {}
    for dict_name, _ in ALL_DICTIONARIES:
        result[f'{dict_name}_score'] = float('nan')
        result[f'{dict_name}_label'] = '中性'
        result[f'{dict_name}_pos_ratio'] = float('nan')
        result[f'{dict_name}_neg_ratio'] = float('nan')
    result['sentiment_details'] = ''

    result['avg_sentence_len'] = 0.0
    result['type_token_ratio'] = 0.0
    result['char_per_word'] = 0.0
    result['pos_ratio'] = float('nan')
    result['neg_ratio'] = float('nan')
    result['msent_score'] = float('nan')
    # IDF 加权列一致性初始化（确保所有行返回相同 key 结构）
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            result[f'{dict_name}_idf_score'] = float('nan')
            result[f'{dict_name}_idf_label'] = '中性'
    return result


def _analyze_single_article(content: str) -> dict:
    """对单篇文章执行所有词典的情感分析。

    分词只执行一次（独立 tone tokenizer, 见 ``_get_tone_tokenizer``），然后对每个
    词典独立计分。

    聚合列语义 (fix omni-g-tonewords-01/-05/-06, 2026-06-11):
        - ``pos_ratio`` / ``neg_ratio`` / ``msent_score`` / ``sentiment_details``
          的计数基 = 5 词典固定 **union 词典** (``build_union_dictionary``), 替代旧
          "逐篇匹配数最多的词典" (best-dict, 测量工具跨观测漂移)。
        - 全部比率分母 = **word-token** 数 (排除纯标点/纯数字 token, 复用
          ``lm_non_sentiment._LMFLS_NONWORD_RE``, 与 lmfls-01 修复同口径)。
        - 空文本契约: score/ratio/msent → NaN (见 ``_empty_article_result``)。

    Args:
        content: 文章内容文本。

    Returns:
        dict: 包含各词典的得分、标签和 union 词典匹配详情。
    """
    if not isinstance(content, str) or not content.strip():
        return _empty_article_result()

    # 分词（单次调用，所有词典共享分词结果; fix omni-g-tonewords-10: 用独立
    # tone tokenizer, 领域词注入不再污染全局 jieba）
    tokens = list(_get_tone_tokenizer().cut(content))

    # 防御：极端文本（纯符号、纯控制字符）可能产生全空分词结果
    tokens = [t for t in tokens if t.strip()]
    if not tokens:
        return _empty_article_result()

    result: dict[str, Any] = {}

    # fix(omni-g-tonewords-02/-06, 2026-06-11): 比率分母 word-token 化 — 排除纯标点/
    # 纯数字 token (盘上实测占全 token 均值 ~19%, 逐篇 13–26% 非常数稀释), 与
    # lm_non_sentiment lmfls-01 的 LM/FLS 分母修复同口径 (Garcia 2013 JF / LM 2011 JF
    # 的 "fraction of words" 分母均为词数而非物理 token 数)。分子为词典词 (真词,
    # 标点/数字本不命中), 仅分母收紧。
    n_word_tokens = sum(1 for t in tokens if not _LMFLS_NONWORD_RE.fullmatch(t.strip()))

    # 对每个词典计算情感
    for dict_name, sentiment_dict in ALL_DICTIONARIES:
        if not sentiment_dict:
            result[f'{dict_name}_score'] = 0.0
            result[f'{dict_name}_label'] = '中性'
            # 词典缺失 → 比率不可测, NaN (与 fix omni-g-tonewords-13 缺失语义一致)
            result[f'{dict_name}_pos_ratio'] = float('nan')
            result[f'{dict_name}_neg_ratio'] = float('nan')
            continue

        raw_score, norm_score, pos_cnt, neg_cnt, matched = \
            _compute_sentiment_with_rules(tokens, sentiment_dict)

        result[f'{dict_name}_score'] = round(norm_score, 4)
        result[f'{dict_name}_label'] = _score_to_label(norm_score)

        # --- 单词典正/负面词频分离 ---
        # 学术依据: Garcia, D. (2013). Sentiment during recessions.
        #   The Journal of Finance, 68(3), 1267-1300.
        #   DOI: 10.1111/jofi.12027
        #   → 将正负面词汇分离为独立协变量, 避免净情感指标的极性对冲掩蔽
        # 用途: 下游 disag (情感分歧) 指标的单词典变体输入
        # 分母 = word-token 数 (fix omni-g-tonewords-06); 纯标点/数字文本 → NaN
        result[f'{dict_name}_pos_ratio'] = (
            round(pos_cnt / n_word_tokens, 6) if n_word_tokens > 0 else float('nan'))
        result[f'{dict_name}_neg_ratio'] = (
            round(neg_cnt / n_word_tokens, 6) if n_word_tokens > 0 else float('nan'))

    # ── 固定 union 词典扫描 (fix omni-g-tonewords-01/-05, 2026-06-11) ──
    # pos_ratio / neg_ratio / msent_score / sentiment_details 的计数基从"逐篇匹配数
    # 最多的词典" (best-dict, 胜出词典逐篇切换 → 测量工具跨观测不固定) 改为 5 词典
    # 固定 union 词典 — 全样本同一词表, 兑现 Tetlock 2007 / Garcia 2013 / Henry 2008
    # 的固定词表构念。
    union_dict = _get_union_dictionary()
    if union_dict:
        _, _, union_pos_count, union_neg_count, union_matched = \
            _compute_sentiment_with_rules(tokens, union_dict)
    else:
        union_pos_count, union_neg_count, union_matched = 0, 0, []

    # 仅保留 Top-20 匹配词（按绝对影响力降序; union 词典口径）
    top_detail = sorted(union_matched, key=lambda x: abs(x['final']), reverse=True)[:20]
    result['sentiment_details'] = json.dumps(top_detail, ensure_ascii=False) if top_detail else ''



    # ── 文本可读性控制变量 ──
    # Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. 
    # The Journal of Finance, 69(4), 1643-1671.
    # https://doi.org/10.1111/jofi.12162
    readability = _compute_readability(content, tokens)
    result['avg_sentence_len'] = readability['avg_sentence_len']
    result['type_token_ratio'] = readability['type_token_ratio']
    result['char_per_word'] = readability['char_per_word']

    # ── 词汇/句法复杂度 $0 测度族 (批 #2–#6, 2026-06-05) ──
    # rare_word/hard_char/nominalization/function_word/specificity/redundancy/adversative
    # (单次 jieba.posseg pass)。空/哨兵文本的 nan 兜底由 compute_lexical_complexity 入口
    # guard + 列提取 .get(k, nan) 负责, 不依赖本函数早返 (早返分支本就不含 lexical 键)。
    result.update(compute_lexical_complexity(content))

    # ── 正/负面词频分离（稳健性检验）──
    # 学术依据: 将正负面词汇分离作为独立的协变量，能有效缓解传统净情感指标可能带来的极性对冲掩蔽问题。
    # Garcia, D. (2013). Sentiment during recessions.
    # The Journal of Finance, 68(3), 1267-1300.
    # https://doi.org/10.1111/jofi.12027
    #
    # Loughran, T., & McDonald, B. (2011). When is a liability not a liability?
    # Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65.
    # https://doi.org/10.1111/j.1540-6261.2010.01625.x
    # fix(omni-g-tonewords-01/-05/-06, 2026-06-11): 分子 = 固定 union 词典计数
    # (替代 best-dict); 分母 = word-token 数 (排除纯标点/纯数字)。
    result['pos_ratio'] = (
        round(union_pos_count / n_word_tokens, 6) if n_word_tokens > 0 else float('nan'))
    result['neg_ratio'] = (
        round(union_neg_count / n_word_tokens, 6) if n_word_tokens > 0 else float('nan'))

    # ── 计数型情感指标 MSENT ──
    # 学术依据: 经典的基于净负面值占比的情感计量方法，提供稳健性交叉验证。
    # Henry, E. (2008). Are investors influenced by how earnings press releases are written?
    # Journal of Business Communication, 45(4), 363-407.
    # https://doi.org/10.1177/0021943608319388
    #
    # Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market.
    # The Journal of Finance, 62(3), 1139-1168.
    # https://doi.org/10.1111/j.1540-6261.2007.01232.x
    # MSENT = (Negative Words − Positive Words) / (Positive Words + Negative Words)
    # 注意: 此处使用**原始词典极性**计数 (base 字段), 而非语言学规则处理后的
    # 极性 (final 字段)。论文的 MSENT 基于词典查找, 不考虑否定/程度/转折修饰。
    # 例: "不好" 中 "好" 在词典中为正面词 → 计为 Positive, 即使 final_score < 0。
    # 与管道主得分 (normalized_score, 语言学加权) 互为稳健性检验。
    # fix(omni-g-tonewords-01/-05, 2026-06-11): 计数基 = 固定 union 词典匹配
    # (替代 best-dict); 全文无 word-token 时 → NaN (与 ratio 契约对称)。
    raw_pos = sum(1 for m in union_matched if m['base'] > 0)
    raw_neg = sum(1 for m in union_matched if m['base'] < 0)
    total_raw = raw_pos + raw_neg
    if n_word_tokens == 0:
        result['msent_score'] = float('nan')
    else:
        result['msent_score'] = round(
            (raw_neg - raw_pos) / total_raw, 6
        ) if total_raw > 0 else 0.0

    # ── IDF 加权并行度量 (Gentzkow et al. 2019, JEL §2.2) ──
    # 复用同一次 tone tokenizer 切词的 tokens，零额外分词开销
    if IDF_DICTIONARIES is not None:
        for dict_name, idf_dict in IDF_DICTIONARIES:
            if not idf_dict:
                result[f'{dict_name}_idf_score'] = 0.0
                result[f'{dict_name}_idf_label'] = '中性'
                continue
            _, idf_norm, _, _, _ = _compute_sentiment_with_rules(tokens, idf_dict)
            result[f'{dict_name}_idf_score'] = round(idf_norm, 4)
            result[f'{dict_name}_idf_label'] = _score_to_label(idf_norm)

    return result


# ============================================================================
# 6. 批处理和统计
# ============================================================================

def classify_batch(df_batch: pd.DataFrame) -> tuple:
    """对单个批次执行词典法双轨情感分析（全文 + 上下文片段）。

    Args:
        df_batch: 待分析的 DataFrame 批次（需含 'content_ctx' 列，
                  由阶段 13 ctx_materializer 物化、随 21 输出下传）。

    Returns:
        tuple: (processed_df, stats_dict)
    """
    stats = {'total': 0}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            stats[f'{dict_name}_正面{track}'] = 0
            stats[f'{dict_name}_中性{track}'] = 0
            stats[f'{dict_name}_负面{track}'] = 0

    if df_batch.empty:
        return df_batch, stats

    df = df_batch.copy()
    stats['total'] = len(df)

    # 对每篇文章执行双轨情感分析
    # content_ctx 由阶段 13 ctx_materializer 物化为列 (随上游输出下传)，直接读取以确保三种方法输入一致
    # v3.5.1 A1: 加载 clarity 词典 (lazy, batch 内 1 次)
    _def_set, _amb_set = load_clarity_dictionaries()
    # v3.5.2 PR #3: 加载 LM 4 子词典 (lru_cache 全局单例; 第 2 次调用 O(1))
    _lm_dicts = load_lm_non_sentiment_dicts()

    def _dual_analyze(row):
        # remove-title-track: full / ctx 两轨文本均注入标题 (prepend_title); title 轨已取消
        from news_process.core.text.entity_context import prepend_title
        _title = str(row.get('标题', '') or '')
        content_full = prepend_title(_title, str(row.get('内容', '')))
        content_ctx = prepend_title(_title, str(row.get('content_ctx', str(row.get('内容', '')))))

        res_full = _analyze_single_article(content_full)
        res_ctx = _analyze_single_article(content_ctx)

        # 合并：为每个键追加轨道后缀
        merged = {}
        for k, v in res_full.items():
            merged[f'{k}_full'] = v
        for k, v in res_ctx.items():
            merged[f'{k}_ctx'] = v

        # v3.5.1 A1 真双轨 clarity (per plan v0.3 §2.1.1 修 R3-C1):
        # 对 content_full + content_ctx **独立扫描** (title 轨不纳入, 修 R3-H1
        # 锁定排除 — title 文本 < 50 字符分母不稳).
        clarity_full = _compute_clarity_for_text(content_full, _def_set, _amb_set)
        clarity_ctx = _compute_clarity_for_text(content_ctx, _def_set, _amb_set)
        for k, v in clarity_full.items():
            merged[f'clarity_{k}_full'] = v
        for k, v in clarity_ctx.items():
            merged[f'clarity_{k}_ctx'] = v

        # v3.5.2 PR #3 (A1): LM 4 non-sentiment 子词典真双轨扫描.
        # 关键 4 panel 列: uncert_frac_{full,ctx} / litig_frac_{full,ctx} /
        # constr_frac_{full,ctx} / modal_strong_frac_{full,ctx}.
        # fix(omni-g-tonewords-10/-11, 2026-06-11): 改走 tone tokenizer 包装 —
        # lm_non_sentiment 原函数内部用全局 jieba, 注入隔离后会把多字 LM 词切碎。
        lm_full = _compute_lm_non_sentiment_for_text_tone_tok(content_full, _lm_dicts)
        lm_ctx = _compute_lm_non_sentiment_for_text_tone_tok(content_ctx, _lm_dicts)
        for k in ('uncert', 'litig', 'constr', 'modal_strong'):
            merged[f'{k}_frac_full'] = lm_full.get(f'frac_{k}', float('nan'))
            merged[f'{k}_frac_ctx'] = lm_ctx.get(f'frac_{k}', float('nan'))

        # v3.5.2 PR #3 (A2): Forward-Looking Statements 比例真双轨.
        fls_full = compute_fls_for_text(content_full)
        fls_ctx = compute_fls_for_text(content_ctx)
        merged['frac_fls_full'] = fls_full.get('frac_fls', float('nan'))
        merged['frac_fls_ctx'] = fls_ctx.get('frac_fls', float('nan'))

        return merged

    results = df.apply(_dual_analyze, axis=1)

    # 提取各列（双轨）。先攒成一个列字典, 再一次性 concat, 避免大量
    # ``df[col] = ...`` 造成 pandas block fragmentation。
    new_columns = {}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            score_key = f'{dict_name}_score{track}'
            label_key = f'{dict_name}_label{track}'
            label_series = results.apply(lambda r, k=label_key: r.get(k, '中性'))
            new_columns[score_key] = results.apply(
                lambda r, k=score_key: r.get(k, 0.0))
            new_columns[label_key] = label_series

            label_counts = label_series.value_counts()
            stats[f'{dict_name}_正面{track}'] = int(label_counts.get('正面', 0))
            stats[f'{dict_name}_中性{track}'] = int(label_counts.get('中性', 0))
            stats[f'{dict_name}_负面{track}'] = int(label_counts.get('负面', 0))

            # 单词典 pos/neg ratio 提取 (Garcia 2013, JF)
            pos_key = f'{dict_name}_pos_ratio{track}'
            neg_key = f'{dict_name}_neg_ratio{track}'
            new_columns[pos_key] = results.apply(lambda r, k=pos_key: r.get(k, 0.0))
            new_columns[neg_key] = results.apply(lambda r, k=neg_key: r.get(k, 0.0))

    new_columns['sentiment_details_full'] = results.apply(
        lambda r: r.get('sentiment_details_full', ''))
    new_columns['sentiment_details_ctx'] = results.apply(
        lambda r: r.get('sentiment_details_ctx', ''))

    # ── 提取 IDF 加权列（双轨）──
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx']:
                score_key = f'{dict_name}_idf_score{track}'
                label_key = f'{dict_name}_idf_label{track}'
                new_columns[score_key] = results.apply(
                    lambda r, k=score_key: r.get(k, 0.0))
                new_columns[label_key] = results.apply(
                    lambda r, k=label_key: r.get(k, '中性'))

    # ── 提取新增指标列（双轨）──
    new_metric_cols = [
        'avg_sentence_len', 'type_token_ratio', 'char_per_word',
        'pos_ratio', 'neg_ratio',
        'msent_score',  # He et al. (2024, IRFA), Eq. 1
    ]
    for col in new_metric_cols:
        for track in ['_full', '_ctx']:
            col_key = f'{col}{track}'
            new_columns[col_key] = results.apply(lambda r, k=col_key: r.get(k, 0.0))

    # ── v3.5.1 A1 真双轨 clarity 列提取 (per plan v0.3 §2.1.1 + §2.1.3) ──
    # title 轨不纳入 (R3-H1 锁定); 仅 full + ctx 双轨独立扫描.
    clarity_metric_cols = [
        'n_definite', 'n_ambiguous', 'n_tokens_clarity_base',
        'frac_definite', 'frac_ambiguous', 'clarity_score',
    ]
    for col in clarity_metric_cols:
        for track in ['_full', '_ctx']:
            col_key = f'clarity_{col}{track}'
            new_columns[col_key] = results.apply(lambda r, k=col_key: r.get(k, float('nan')))

    # ── v3.5.2 PR #3 (A1 LM 4 子词典 + A2 FLS) 真双轨列提取 ──
    # A1: uncert_frac_{full,ctx} / litig_frac_{full,ctx} / constr_frac_{full,ctx}
    #     / modal_strong_frac_{full,ctx}
    # A2: frac_fls_{full,ctx}
    # title 轨不纳入 (与 clarity 同款决策, R3-H1 锁定 — title 文本 < 50 字符).
    lm_a2_metric_cols = [
        'uncert_frac', 'litig_frac', 'constr_frac', 'modal_strong_frac',
        'frac_fls',
    ]
    for col in lm_a2_metric_cols:
        for track in ['_full', '_ctx']:
            col_key = f'{col}{track}'
            new_columns[col_key] = results.apply(
                lambda r, k=col_key: r.get(k, float('nan'))
            )

    # ── 词汇/句法复杂度 $0 测度族 (批 #2–#6) + 词级长度 n_words_real (批 #7) 双轨列提取 ──
    for col in (*LEXICAL_COMPLEXITY_KEYS, WORD_COUNT_KEY):
        for track in ['_full', '_ctx']:
            col_key = f'{col}{track}'
            new_columns[col_key] = results.apply(
                lambda r, k=col_key: r.get(k, float('nan'))
            )

    if new_columns:
        df = pd.concat([df, pd.DataFrame(new_columns, index=df.index)], axis=1).copy()

    return df, stats


def merge_stats(stats_list: list) -> dict:
    """合并多个批次的统计结果。

    Args:
        stats_list: 各批次返回的统计字典列表。

    Returns:
        dict: 合并后的统计字典。
    """
    merged = {'total': 0}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            merged[f'{dict_name}_正面{track}'] = 0
            merged[f'{dict_name}_中性{track}'] = 0
            merged[f'{dict_name}_负面{track}'] = 0

    for s in stats_list:
        merged['total'] += s['total']
        for dict_name, _ in ALL_DICTIONARIES:
            for track in ['_full', '_ctx']:
                merged[f'{dict_name}_正面{track}'] += s.get(f'{dict_name}_正面{track}', 0)
                merged[f'{dict_name}_中性{track}'] += s.get(f'{dict_name}_中性{track}', 0)
                merged[f'{dict_name}_负面{track}'] += s.get(f'{dict_name}_负面{track}', 0)
    return merged


def log_classification_report(stats: dict, logger, track_suffix: str = ''):
    """输出词典法情感分析统计报告。

    Args:
        stats:         合并后的统计字典。
        logger:        日志记录器。
        track_suffix:  轨道后缀 ('_full' 或 '_ctx')，用于区分报告。
    """
    track_label = '全文' if track_suffix == '_full' else '上下文片段' if track_suffix == '_ctx' else ''
    logger.info("=" * 70)
    logger.info(f"===      词典法情感分析统计报告 [{track_label}]      ===")
    logger.info("=" * 70)

    total = stats['total']
    logger.info(f"总记录数: {total:,}")
    logger.info(f"使用词典数: {len(ALL_DICTIONARIES)} 个")
    logger.info(
        f"语言学规则: 否定词({len(NEGATION_WORDS)}个), "
        f"程度副词({len(DEGREE_WORDS)}个), "
        f"转折连词({len(ADVERSATIVE_WORDS)}个)"
    )

    logger.info("-" * 70)
    logger.info(f"{'词典名称':<20} {'正面':>8} {'中性':>8} {'负面':>8} {'正面占比':>10} {'中性占比':>10} {'负面占比':>10}")
    logger.info("-" * 70)

    for dict_name, d in ALL_DICTIONARIES:
        pos = stats.get(f'{dict_name}_正面{track_suffix}', 0)
        neu = stats.get(f'{dict_name}_中性{track_suffix}', 0)
        neg = stats.get(f'{dict_name}_负面{track_suffix}', 0)
        pos_pct = f"{pos / total * 100:.1f}%" if total > 0 else "N/A"
        neu_pct = f"{neu / total * 100:.1f}%" if total > 0 else "N/A"
        neg_pct = f"{neg / total * 100:.1f}%" if total > 0 else "N/A"
        dict_label = f"{dict_name}({len(d)}词)"
        logger.info(f"  {dict_label:<20} {pos:>8,} {neu:>8,} {neg:>8,} {pos_pct:>10} {neu_pct:>10} {neg_pct:>10}")

    logger.info("=" * 70)


def _zscore_or_nan(series: pd.Series, col_label: str) -> pd.Series:
    """单列 Z-score 标准化; σ 退化时整列 NaN (fix omni-g-tonewords-13, 2026-06-11).

    μ/σ 按 pandas 默认 skipna 计算; 正常分支 (σ>0) 中源 NaN 行自然传播为 NaN。
    退化分支 (σ=0 常数列 / 全 NaN 列致 σ=NaN, ``NaN>0`` 为 False) 旧实现对**整列**
    回填 0.0 — 全 NaN 列被静默抹成"恰均值"伪零分, 与正常分支的缺失语义不一致。
    现退化 → 整列 NaN + logger.error 降级披露 (与 fintech_intensity F11 同款口径);
    z-score 对常数列本就数学未定义 (0/0)。

    Args:
        series: 待标准化的得分列。
        col_label: 日志用列标签 (如 ``"jiang_2021 [_full]"``)。

    Returns:
        pd.Series: z-score 列; σ 退化时为全 NaN 列。
    """
    mean_val = series.mean()
    std_val = series.std()
    if std_val > 0:
        logger.info(f"  {col_label}: Z-score 标准化完成 (μ={mean_val:.4f}, σ={std_val:.4f})")
        return (series - mean_val) / std_val
    logger.error(
        f"  {col_label}: Z-score 退化 (μ={mean_val!r}, σ={std_val!r}) → 整列置 NaN "
        f"(fix omni-g-tonewords-13; 旧行为整列回填 0.0 伪零分, 缺失被抹成'恰均值')")
    return pd.Series(np.nan, index=series.index)


# ============================================================================
# 7. 主函数
# ============================================================================

def main():
    """词典法情感分析阶段主入口。"""
    global ALL_DICTIONARIES, IDF_DICTIONARIES
    
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     使用五部中文金融情感词典对每篇新闻进行情感打分。")
    logger.info("     每部词典独立计算正/负词频比, 并通过语言学规则(否定/程度/转折)修正。")
    logger.info("     采用双轨模式: 全文(_full)和上下文片段(_ctx)分别计算, 供下游三角验证。")
    logger.info("")
    logger.info("  📖 方法论依据")
    logger.info("     · IDF 加权: Gentzkow, Kelly & Taddy (2019, JEL 57(3):535-574) §2.2")
    logger.info("       → 降低高频常见词的权重, 提升稀有金融术语的区分度")
    logger.info("     · 语言学规则参考: Jia et al. (2009), Pang & Lee (2008),")
    logger.info("       Li et al. (2010), Liu (2012), Kennedy & Inkpen (2006)")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · Z-score 标准化: 均值=0, 标准差=1。正值=正面倾向, 负值=负面倾向")
    logger.info("     · IDF 权重分位数: P25-P75 的范围越窄 → 词典词汇区分度越均匀")
    logger.info("     · 正/中/负面占比: 若某词典负面>60%, 可能存在负面偏差")
    logger.info("")

    # 延迟加载词典和注入 jieba（避免 import 时的副作用）
    ALL_DICTIONARIES = load_all_dictionaries()
    _inject_custom_dicts_to_jieba()

    non_empty_dicts = [(name, d) for name, d in ALL_DICTIONARIES if len(d) > 0]
    if not non_empty_dicts:
        logger.error("所有情感词典均为空！请检查词典文件。")
        raise SystemExit(1)

    logger.info(f"有效词典: {len(non_empty_dicts)}/{len(ALL_DICTIONARIES)} 个")

    # 定义输入输出
    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet'))
    output_path = os.path.join(CONFIG['paths']['output_dir'],
                               CONFIG['filenames'].get('output_22_words_tone', '22_tone_words.parquet'))

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"正在从 {input_path} 加载数据...")
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    logger.info(f"已加载 {input_rows:,} 行数据。")
    log_memory_usage(logger, "数据加载后")

    # ── IDF 加权稳健性检验初始化 ──
    IDF_DICTIONARIES = None
    idf_enabled = SENTIMENT_PARAMS.get('idf_weighting', True)
    if idf_enabled:
        logger.info("═" * 60)
        logger.info("IDF 加权稳健性检验 (Gentzkow et al. 2019, JEL §2.2)")
        logger.info("═" * 60)

        # fix(tone-words-idf-corpus, metric-audit 2026-06-10): IDF 的 document-frequency 须在
        # 与 TF 加权**同一语料**上统计 (Gentzkow-Kelly-Taddy 2019 JEL §2.2)。TF 打分文本是
        # 含标题的 content_full (病根A 修后), 故 IDF 亦应在 content_full 上算, 而非裸 '内容'
        # (无标题) → 否则 IDF 语料 ≠ TF 语料, 标题词的 df 被低估。缺 content_full 回退 '内容'。
        _idf_text_col = 'content_full' if 'content_full' in df.columns else '内容'
        idf_weights = build_idf_weights(df, ALL_DICTIONARIES, text_col=_idf_text_col)
        IDF_DICTIONARIES = [
            (name, _build_idf_weighted_dict(d, idf_weights.get(name, {})))
            for name, d in ALL_DICTIONARIES
        ]

        # 诊断日志：IDF 分位数 + Top5/Bottom5 词
        for dict_name in idf_weights:
            w = idf_weights[dict_name]
            if w:
                vals = np.array(list(w.values()))
                logger.info(
                    f"  {dict_name}: {len(w)} 词, "
                    f"IDF [min={vals.min():.3f}, P25={np.percentile(vals, 25):.3f}, "
                    f"P50={np.percentile(vals, 50):.3f}, P75={np.percentile(vals, 75):.3f}, "
                    f"max={vals.max():.3f}]"
                )
                sorted_w = sorted(w.items(), key=lambda x: x[1], reverse=True)
                top5 = [(k, f"{v:.2f}") for k, v in sorted_w[:5]]
                bot5 = [(k, f"{v:.2f}") for k, v in sorted_w[-5:]]
                logger.info(f"    IDF 最高 (稀有→高权重): {top5}")
                logger.info(f"    IDF 最低 (常见→低权重): {bot5}")

        # 保存 IDF 权重到 JSON（可复现性，AER/QJE 标准）
        idf_save_path = os.path.join(
            CONFIG['paths']['output_dir'], '22_idf_weights.json')
        try:
            serializable = {
                k: {word: round(val, 6) for word, val in v.items()}
                for k, v in idf_weights.items()
            }
            serializable['_meta'] = {
                # fix(omni-g-tonewords-04, 2026-06-11): N = 唯一文档数, 与
                # build_idf_weights 内部去重后公式中的 N 一致 (旧值 = article×bank
                # 展开行数, 与实际公式分子不符); 展开行数另存 n_rows 供对账。
                'N': int(df[_idf_text_col].fillna('').astype(str).nunique()),
                'n_rows': int(len(df)),
                'dedup': 'unique documents by text content (fix omni-g-tonewords-04)',
                'formula': 'log10(N / (1 + df(w)))',
                'normalization': 'mean=1 then Winsorize P1/P99',
                'reference': 'Gentzkow, Kelly & Taddy (2019, JEL) §2.2',
            }
            with open(idf_save_path, 'w', encoding='utf-8') as f:
                json.dump(serializable, f, ensure_ascii=False, indent=2)
            logger.info(f"  IDF 权重已保存: {idf_save_path}")
        except Exception as e:
            logger.warning(f"  保存 IDF 权重失败: {e}")

        logger.info(f"  IDF 加权词典构建完成: {len(IDF_DICTIONARIES)} 个")
    else:
        logger.info("IDF 加权已在配置中禁用 (idf_weighting: false)")

    # 执行词典法情感分析
    logger.info(f"开始执行词典法情感分析...")
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    all_stats = []
    processed_dfs = []
    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    logger.info(f"使用 joblib 并行处理: n_jobs={n_jobs}, 共 {num_batches} 个批次")

    results = Parallel(n_jobs=n_jobs, prefer='threads')(
        delayed(classify_batch)(batch) for batch in df_batches
    )
    for res_df, res_stats in results:
        processed_dfs.append(res_df)
        all_stats.append(res_stats)

    # 合并全部结果
    processed_df = pd.concat(processed_dfs, ignore_index=True)

    # P1-4: 为每个词典的得分列添加 Z-score 标准化列（双轨独立计算）
    # 解决跨词典量纲不一致问题，供 34_tone_validation.py 的 Cronbach's Alpha 分析使用
    # 注意：_full 和 _ctx 的 μ 和 σ 必须独立计算，因文本长度差异导致数值分布本质不同
    # fix(omni-g-tonewords-13, 2026-06-11): σ 退化分支改整列 NaN (见 _zscore_or_nan),
    # 不再回填 0.0 伪零分; 正常分支 NaN 传播行为不变。
    zscore_columns = {}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx']:
            score_col = f"{dict_name}_score{track}"
            zscore_col = f"{dict_name}_zscore{track}"
            if score_col in processed_df.columns:
                zscore_columns[zscore_col] = _zscore_or_nan(
                    processed_df[score_col], f"{dict_name} [{track}]")

    # IDF 列 Z-score 标准化
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx']:
                score_col = f"{dict_name}_idf_score{track}"
                zscore_col = f"{dict_name}_idf_zscore{track}"
                if score_col in processed_df.columns:
                    zscore_columns[zscore_col] = _zscore_or_nan(
                        processed_df[score_col], f"{dict_name}_idf [{track}]")

    if zscore_columns:
        processed_df = pd.concat(
            [processed_df, pd.DataFrame(zscore_columns, index=processed_df.index)],
            axis=1,
        ).copy()

    # v3.5.1 A3: Numerical Intensity 真双轨 post-processor (per plan v0.3 §2.2.3 修 R3-C2 + H4).
    # 对 content_full + content_ctx 各调用 compute_num_intensity 一次, 写入
    # num_intensity_full / num_intensity_ctx 两 article 列. 锚定: 数值披露强度
    # (Davis & Tama-Sweet 2012 CAR; 原引 Hales 2011 系误归, 见 numerical_intensity 模块 docstring).
    # 依赖方向: tone_words → numerical_intensity (单向).
    try:
        from news_process.pipeline.sentiment.numerical_intensity import (
            enrich_with_num_intensity_dual_track,
        )
        # fix(genA-01/V4): full 轨须读 content_full(含标题, v3.8.0 两轨契约), 不再用
        # 默认裸 '内容' — 否则 num_intensity_full 是唯一不含标题的 *_full 情感族指标,
        # 与同 stage 的 clarity/LM/FLS(均已读 content_full)轨道不对称。
        _ni_full_col = 'content_full' if 'content_full' in processed_df.columns else '内容'
        processed_df = enrich_with_num_intensity_dual_track(
            processed_df, full_col=_ni_full_col)
        logger.info(f"v3.5.1 A3: num_intensity 真双轨派生完成 (full 轨={_ni_full_col} + ctx 独立扫描)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"v3.5.1 A3 num_intensity enrich 失败 (graceful skip): {e}")

    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    save_parquet_with_metadata(
        df=processed_df,
        output_path=output_path,
        stage_name="22_tone_words",
        config=CONFIG,
        input_files=[input_path],
    )

    # 统计报告（双轨分别打印）
    if all_stats:
        merged_stats = merge_stats(all_stats)
        log_classification_report(merged_stats, logger, track_suffix='_full')
        log_classification_report(merged_stats, logger, track_suffix='_ctx')



    # 生成预览
    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (双轨模式) ---")


if __name__ == "__main__":
    main()
