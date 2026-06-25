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
│                                                            │
│ 6. loughran_mcdonald_zh_2026  L&M 2011 JF 中文主译本          │
│    │  (列前缀别名 loughran)                                  │
│    └─ positive(1,295) / negative(3,729); 另含 5 类非极性词类   │
└────────────────────────────────────────────────────────────┘

词典消歧 (用户决策 2026-06-24「保留并两侧计数」, 逆转 fix omni-g-tonewords-03/-07):
    加载时对每部词典的 positive∩negative 跨类重叠词 (jiang_2021 21 词 / you_2018 5 词 /
    loughran 23 词; loughran 原 61 词经 2026-06-24「两侧保留判断」消歧, 38 词已归单侧、
    余 23 词不可约简而保留, 见 config/tone_dicts.json::loughran 的 _description)
    **保留**而非剔除: 登记到 ``_BOTH_SIDED_BY_DICT``, 打分时同时计入
    pos/neg (对该词典个体 ``{dict}_score`` 净语调拉向中性、不武断选边), 故运行时词条数
    = 原始 |pos∪neg| (不再 < 上表)。clarity 的 definite∩ambiguous 重叠 ('不可') 同样保留,
    在两集合各自计数 (clarity 口径的两侧计入)。
    ⚠ union/msent/ratio 不受影响: 重叠词以 (+1,−1) 平衡双票喂入固定 union 词典 → 极性
      margin 守恒 → union 逐位不变 (见 ``build_union_dictionary``)。
    (历史: fix omni-g-tonewords-03/-07 曾按 LM 2011 JF 惯例双侧剔除, 旧旧实现则 negative
      循环 last-writer-wins 静默判负; 现按用户决策恢复"保留", 但用对称两侧计数取代旧的
      静默单极判负。)

聚合测度的固定词典 (fix omni-g-tonewords-01/-05, 2026-06-11):
    pos_ratio / neg_ratio / msent_score 的计数基从"逐篇匹配数最多的词典"
    (best-dict, 测量工具跨观测漂移) 改为 **6 词典固定 union 词典**
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

**处理步骤**: ①`load_all_dictionaries()` 延迟加载六部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran_mcdonald_zh_2026 = L&M 2011 JF 中文主译本) + 跨类重叠词保留并两侧计数 (用户决策 2026-06-24, 逆转旧双侧剔除; 登记 `_BOTH_SIDED_BY_DICT`) + `_inject_custom_dicts_to_jieba` 注入 jieba 自定义词; ②可选 `build_idf_weights` 在与 TF 同一语料 (caller 传 content_full, 缺则回退 '内容') 上算 IDF 文档频率 (Gentzkow-Kelly-Taddy 2019 JEL §2.2), 公式 `log10(N/(1+df(w)))`, 均值归一(mean→1) 后 P1/P99 Winsorize, 文档级去重统计 N/df, 存 22_idf_weights.json; ③joblib 线程并行分批 `classify_batch`, 每批对每篇文章三轨调用打分; ④对每部词典每轨的 score 列做 Z-score 标准化 (`_zscore_or_nan`, σ 退化→整列 NaN); ⑤调 `enrich_with_num_intensity_dual_track` (外部模块导入) 三轨派生 `num_intensity_{full,ctx,ss}` (数值披露强度, Davis & Tama-Sweet 2012 CAR); ⑥写 parquet + 预览 CSV + 三轨分类报告。

**关键算法/公式**: 核心是 `_compute_sentiment_with_rules(tokens, dict, apply_negation, apply_degree, apply_adversative)` —— 逐 token 状态机施加语言学规则: 否定词翻转极性 (窗口 NEGATION_WINDOW=2 个分词单元)、程度副词六级权重缩放 (HowNet 六级体系 + Liu 2012, DEGREE_WORDS 由 config 注入)、转折连词后权重 ×ADVERSATIVE_BOOST(默认 1.5)、句末标点重置作用域 (Ding 2008 从句级)。最终分 = self-normalized Σ(final)/Σ|final| ∈ [-1,+1]。**negonly 消融变体**: `apply_degree=False & apply_adversative=False` 只保留否定翻转, 产 `{dict}_score_negonly`/`msent_negonly`, 用作'主结果对去掉程度/转折两条规则是否敏感'的稳健性 (实测 corr(full,negonly)≈0.998-0.999 高度共线, 是稳健性对照非独立信号)。另产 `pos_ratio`/`neg_ratio` (固定 union 词典计数 / word-token 数)、`msent_score`=(raw_neg−raw_pos)/(raw_pos+raw_neg) 原始极性计数 (零规则; framing ≈ Tetlock 2007/Garcia 2013/Henry 2008; 代码注 He et al. 2024 IRFA Eq.1)、clarity/可读性/词汇复杂度等 $0 测度族。

**输出列**: 每部词典 × 三轨的 `{dict}_score/zscore/idf_score/idf_zscore`、**规则消融梯度 `{dict}_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}`** (v3.11.1 全 powerset, 见 `_RULE_ABLATION_VARIANTS`)、跨词典 `pos_ratio/neg_ratio/msent_score/msent_negonly` (计数口径不入梯度: 程度/转折不翻号)、`num_intensity_{full,ctx,ss}`、可读性/复杂度列。

**外部依赖**: jieba (`==0.42.1` 冻结); 纯 CPU, 无 LLM/网络/API, $0; 无缓存锚点 (确定性来自 jieba 版本 + 词典文件)。

**DAG 位置**: 上游 stage 21 (`21_tone_llms.parquet`); 下游 stage 23 (BERT 读 `22_words_tone.parquet`)。STAGES_MAIN 阶段22。

■ 白话说明

这一步是'查字典版'的情绪打分: 准备好六本专门的中文金融情绪词典 (含 Loughran-McDonald 2011 中文主译本) (里面标好哪些词是褒义、哪些是贬义), 然后逐字逐词扫每篇新闻, 数褒义词、贬义词, 还会按中文语法做修正——遇到'不'就把后面词的好坏反过来 (不乐观=负面), 遇到'非常'就把强度放大, 遇到'但是/然而'就更看重转折后那半句话 (因为作者真实立场常在转折之后)。为什么需要它: 大模型那一步虽然聪明但也可能有偏差或'幻觉', 用一套透明、可解释、谁来跑都一样的词典法另算一遍, 等于给大模型的结论找了个独立的旁证 (论文里叫'稳健性检验')。如果两种方法算出的银行情绪走势一致, 结论就更可信; 如果只用一种, 审稿人会质疑是不是方法本身的偏差。它还专门留了一个'只做否定、不做程度和转折'的简化版本, 用来回答'我的主结果是不是过度依赖那两条修饰规则'——实测发现两者几乎一模一样, 正好证明结论稳。这一步不花钱、不联网, 同样按全文/银行相关段落/银行金科同句段落三种范围各算一遍。
========================================================================
"""

import json
import logging
import math
import os
import platform
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

# v3.5.2 PR #3 集成: A1 LM 6 子词典 (uncert/litig/constr/modal_strong/modal_weak/complexity) + A2 FLS.
# 复用 v3.5.1 三轨架构 (_dual_analyze 内对 content_full + content_ctx + content_ss 各扫一次).
# 三轨 (full/ctx/ss): full=标题+全文; ctx=标题+含目标银行句±1句窗; ss=标题+
# 同句内同时含 目标银行∧金科词 的句±N句窗 (银行+金科同句, suffix '_ss'; 缺/无共现
# →content_ss 镜像 ctx 回退至全文 body, ss_is_fallback=True)。
from news_process.core.config import load_config
from news_process.core.logging import (
    log_memory_usage,
    log_stage_summary,
    pct4,
    setup_logging,
    sig4,
)
from news_process.core.reporting import safe_save_preview_csv
from news_process.pipeline.sentiment.forward_looking import (  # noqa: E402
    compute_fls_for_text,
)
from news_process.pipeline.sentiment.lexical_complexity import (  # noqa: E402
    HAN_COUNT_KEY,
    LEXICAL_COMPLEXITY_KEYS,
    WORD_COUNT_KEY,
    compute_lexical_complexity,
)
from news_process.pipeline.sentiment.lm_non_sentiment import (  # noqa: E402
    _LMFLS_NONWORD_RE,
    _SUBSETS,
    SUBSET_PREFIX,
    SUBSET_PREFIXES,
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

# 列名短别名 (v3.10.0, loughran 接入第 6 部主情感词典)：唯一桥接常量。
# 动机：JSON 键 'loughran_mcdonald_zh_2026' 作列前缀会得 'loughran_mcdonald_zh_2026_score_full'
# = 36 字符 > Stata 32 上限。故 dict_keys 用 JSON 键 (喂 JSON 加载)，但列前缀 / 下游
# DICT_NAMES 一律用别名 'loughran' (≤32, 可读)。translation 仅发生在 load_all_dictionaries
# 的 append 处 (下方)；encode.py::DICT_NAMES / export.py::dict_names 直接硬编码别名 'loughran'
# 与此一致 (两侧 byte-for-byte 相同，否则 stage 45 聚合静默漏列 → 全 NaN)。
DICT_COLUMN_ALIAS = {'loughran_mcdonald_zh_2026': 'loughran'}

# 跨类重叠词「两侧计数」注册表 (用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03 的双侧剔除)。
# 键 = 列前缀别名 (与 ALL_DICTIONARIES 元组的 name 同口径, 经 DICT_COLUMN_ALIAS 映射),
# 值 = 该词典 positive∩negative 同时出现的词集 frozenset。由 load_all_dictionaries 每次
# 加载时重建 (单一事实源)。消费方: ① _compute_sentiment_with_rules 经 both_sided_words 形参
# 对这些词两侧计数; ② build_union_dictionary 把它们当作 (+1,−1) 双票 → union 极性 margin
# 守恒, msent/ratio 字节不变 (见该函数注释)。空 dict 时所有 .get 回退空集 → 退化为旧行为。
_BOTH_SIDED_BY_DICT: dict[str, frozenset[str]] = {}


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
#       https://doi.org/10.1561/1500000011
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
# 与现有 6 词典 (positive/negative score) 并存; clarity 走独立 frozenset 路径以 O(1) 查找
_CLARITY_DICTS: tuple[frozenset, frozenset] | None = None


def load_clarity_dictionaries() -> tuple[frozenset, frozenset]:
    """加载 you_2018 Panel C (definite) + Panel D (ambiguous) 词典 (v3.5.1 A1 三轨激活).

    Returns:
        tuple[frozenset, frozenset]: ``(definite_set, ambiguous_set)``
            definite_set = 388 词 (Panel C, You 2018);
            ambiguous_set = 178 词 (Panel D, You 2018).
            注 (用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03): definite∩ambiguous
            跨类重叠词 ('不可' 1 词) **保留并两侧计数** (不再剔除) → 实际仍为 388 / 178 词,
            重叠词同时存于两集合 (clarity 口径下天然两侧计入, 见加载段日志披露)。

    锚定文献:
        - Loughran & McDonald (2011) JF 66(1) uncertain dictionary
        - You et al. (2018) hhx055 中文金融情感词典 Panel C/D
        - Bonsall et al. (2017) JAE 63(2-3) 信息环境模糊度框架

    与 v3.4.0 及之前差异: 此前 you_2018.definite/ambiguous "仅存档" (tone_dicts.json
    含 keys 但无消费); v3.5.1 激活为三轨 (full/ctx/ss) 独立扫描指标.
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
                # 跨类重叠词「保留并两侧计数」(用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03
                # 的双侧剔除): definite∩ambiguous (实测 '不可' 1 词) 不再剔除, 而是同时保留在
                # 两个集合中。_compute_clarity_for_text 对两集合各自独立计数 → 重叠词天然两侧
                # 计入 (n_definite 与 n_ambiguous 各 +1), 在 clarity_score = frac_def − frac_amb
                # 中净抵消、但两侧 fraction 各自抬升 (= "两侧计数" 在 clarity 口径的自然体现)。
                _cross = def_set & amb_set
                if _cross:
                    logger.info(
                        f"clarity definite∩ambiguous 跨类重叠 {len(_cross)} 词保留并两侧计数 "
                        f"(用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03 的双侧剔除): "
                        f"{sorted(_cross)}")
        except Exception as e:
            logger.error(f"v3.5.1 A1 clarity 词典加载失败: {e}")

    if def_set or amb_set:
        logger.info(f"v3.5.1 A1 clarity 词典加载: definite={len(def_set)} 词, ambiguous={len(amb_set)} 词")
    else:
        logger.warning("v3.5.1 A1 clarity 词典空 (you_2018 Panel C/D 未找到)")

    _CLARITY_DICTS = (def_set, amb_set)
    return _CLARITY_DICTS


def _compute_clarity_for_text(text: str, def_set: frozenset, amb_set: frozenset, _precut: list | None = None) -> dict[str, float]:
    """对**单一文本**独立扫描派生 clarity 指标 (v3.5.1 A1 三轨核心).

    此函数是三轨的关键: ``_dual_analyze`` 对 content_full / content_ctx / content_ss 各调用一次,
    得到独立的 clarity_score_full_i / clarity_score_ctx_i / clarity_score_ss_i — 与项目现有
    ``_analyze_single_article`` 的三轨契约一致 (per stage3_v3_5_1 plan v0.3 §2.1.1 修 R3-C1).

    分词流: tone tokenizer (独立 jieba.Tokenizer 实例, 见 ``_get_tone_tokenizer``) +
    去空字符 token (与 ``_analyze_single_article`` 一致).
    分母 (fix omni-g-tonewords-02/-12, 2026-06-11) = **word-token** 数 — 排除纯标点/
    纯数字 token (复用 ``lm_non_sentiment._LMFLS_NONWORD_RE``, 与 2026-06-10 lmfls-01
    的 LM/FLS 分母修复同口径; 旧分母含 ~19% 标点/数字 token, 逐篇 14.5–25% 非常数稀释)。
    仍为"未去停用词"版 (paper §3.4 disclosure 不变)。

    Args:
        text: 任意单一文本 (典型为 content_full / content_ctx / content_ss).
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

    # [G] 复用调用方预切的 raw token (同文本同 tokenizer → 逐字节等价), 否则内部切
    tokens = _precut if _precut is not None else list(_get_tone_tokenizer().cut(text))
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

    # 每次加载重建跨类重叠词注册表 (单一事实源; 防跨调用陈旧残留)。
    _BOTH_SIDED_BY_DICT.clear()

    dictionaries = []
    # v3.10.0: 第 6 部 = L&M 2011 JF 中文主译全本 (positive 1295 / negative 3729, 2026-06-24
    # 极性消歧后; 原 1310/3752 含 61 跨类重叠, 现 38 词归单侧、余 23 词保留两侧并计数;
    # 第二轮同类内最小词元主用版, 另含 uncertainty/litigious/modal/constraining/complexity 非极性类)。
    # 用 JSON 键加载，但列前缀经 DICT_COLUMN_ALIAS 映射为 'loughran' (见上常量注释)。
    dict_keys = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018',
                 'loughran_mcdonald_zh_2026']
    _both_total = 0  # 全词典跨类重叠词累计 (供加载汇总日志)

    for dict_key in dict_keys:
        entry = all_dict_data.get(dict_key, {})
        dict_name = entry.get('name', dict_key)
        alias = DICT_COLUMN_ALIAS.get(dict_key, dict_key)
        d = {}

        # 从 JSON 中的 positive/negative 列表构建 {word: score}
        # 跨类重叠词「保留并两侧计数」(用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03
        # 的双侧剔除): positive∩negative 同时出现的词不再剔除, 而是保留在词典里 (幅值 1.0
        # 占位, 极性由 _BOTH_SIDED_BY_DICT 标记决定两侧计数, 见 _compute_sentiment_with_rules),
        # 不武断把它判成单极。同时登记到注册表供打分引擎与 union 构建消费。
        pos_words = {str(w).strip() for w in entry.get('positive', []) if str(w).strip()}
        neg_words = {str(w).strip() for w in entry.get('negative', []) if str(w).strip()}
        cross_overlap = pos_words & neg_words
        if cross_overlap:
            logger.info(
                f"  {dict_key}: positive∩negative 跨类重叠 {len(cross_overlap)} 词保留并两侧计数 "
                f"(用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03 的双侧剔除): "
                f"{sorted(cross_overlap)}")
            _BOTH_SIDED_BY_DICT[alias] = frozenset(cross_overlap)
            _both_total += len(cross_overlap)
        # sorted 保证 dict 插入序确定 (可复现性)。先正极专属词 → 负极专属词 → 重叠词
        # (重叠词置 1.0 占位幅值, 不参与单极极性, 仅作为 both_sided 命中键)。
        for word in sorted(pos_words - cross_overlap):
            d[word] = 1.0
        for word in sorted(neg_words - cross_overlap):
            d[word] = -1.0
        for word in sorted(cross_overlap):
            d[word] = 1.0  # 占位幅值 |1.0|; 两侧计数时取 abs, 符号无意义
        # 数量断言: 保留全部词后词条数 = 正负并集大小 (防回归静默覆盖/漏词)
        assert len(d) == len(pos_words | neg_words), (
            f"{dict_key}: 跨类重叠词保留后词条数不等于 |pos∪neg| (存在残余覆盖/漏词)")

        # Du et al. (2022) 特有：政治正面词以较低权重 0.5 加入
        for word in entry.get('political_positive', []):
            word = str(word).strip()
            if word and word not in d:  # 避免覆盖已有正面/负面/重叠词
                d[word] = 0.5

        # 列前缀用别名 (loughran_mcdonald_zh_2026 → 'loughran'); 其余词典恒等映射。
        dictionaries.append((alias, d))

        # 计数按集合显式区分: 正极专属 / 负极专属 / 跨类两侧 / 政治正面 (避免 d.values()
        # 把 1.0 占位的重叠词误并入正面)。
        both_cnt = len(cross_overlap)
        pos_cnt = len(pos_words - cross_overlap)
        neg_cnt = len(neg_words - cross_overlap)
        pol_cnt = sum(1 for v in d.values() if v == 0.5)

        if d:
            _both_str = f", 跨类两侧计数={both_cnt}" if both_cnt else ""
            logger.info(f"  {dict_key} ({dict_name}): {len(d)} 个词汇 "
                        f"(正面={pos_cnt}, 负面={neg_cnt}{_both_str})")
            # 各词典子类别详细统计
            if dict_key == 'du_2022' and pol_cnt > 0:
                logger.info(f"    └─ political_positive: {pol_cnt} 词 (权重=0.5)")
        else:
            logger.info(f"  {dict_key} ({dict_name}): 空（待填充）")

    total_loaded = sum(len(d) for _, d in dictionaries)
    non_empty = sum(1 for _, d in dictionaries if len(d) > 0)
    logger.info(f"词典加载完成: {non_empty}/{len(dict_keys)} 个词典有效, 共 {total_loaded} 个词汇条目"
                f" (含 {_both_total} 个跨类重叠词保留并两侧计数, "
                f"分布于 {len(_BOTH_SIDED_BY_DICT)} 部词典)")

    return dictionaries


def build_union_dictionary(
    dictionaries: list[tuple[str, dict[str, float]]],
    both_sided_by_dict: dict[str, frozenset[str]] | None = None,
) -> dict[str, float]:
    """构造 6 词典固定 union 词典 (fix omni-g-tonewords-01/-05, 2026-06-11).

    动机: pos_ratio / neg_ratio / msent_score 旧实现取"逐篇匹配数最多的词典"
    (best-dict), 测量工具跨观测漂移 (盘上实证: 胜出词典逐篇切换, yao 51%/du 41%),
    与所引 Tetlock 2007 JF / Garcia 2013 JF / Henry 2008 的**固定词表**构念冲突。
    本函数把 6 部词典合并为单一固定词表, 全样本统一使用。

    极性消解规则 (确定性, 与词典顺序无关):
        1. 每词收集其出现的所有词典的 score;
        2. 极性 = 正/负出现次数的**多数票**;
        3. 平票 (正负词典数相同) → 极性歧义, 剔除 (LM 2011 惯例);
        4. 幅值 = 胜出极性内最大 |score| (政治正面词 0.5 仅当无 ±1.0 同向词时保留)。

    跨类重叠词「两侧计数」对 union 的处理 (用户决策 2026-06-24):
        某词典 positive∩negative 同时出现的词 (登记在 ``both_sided_by_dict``) 不再被
        各词典悄悄丢弃, 而是作为 **(+1.0, −1.0) 一对平衡票** 喂入。关键性质: 一对
        (+1,−1) 对 (n_pos − n_neg) 的 margin 贡献恒为 0 → 既不改变其它词典已决出的
        多数票方向, 也不改变平票判定 → **union 词典与剔除版逐位一致** (仅出现在某词典
        且全 both-sided 的词仍因 margin=0 落入平票剔除, 不进 union)。因此 msent /
        pos_ratio / neg_ratio (均走 union 口径) **完全不受本次保留改动影响**, 改动只
        作用于各词典个体 ``{dict}_score`` 列。

    Args:
        dictionaries: ``load_all_dictionaries()`` 的输出 [(name, {word: score}), ...]。
        both_sided_by_dict: {dict_name: frozenset(跨类重叠词)}; None → 读模块全局
            ``_BOTH_SIDED_BY_DICT`` (生产路径)。命中词以 (+1,−1) 双票替代其占位 score。

    Returns:
        dict[str, float]: 固定 union 词典 {word: score}。

    白话: 以前算总体正负词占比时, 每篇文章各自挑"匹配词最多的那部词典"
    来数, 等于不同文章用不同的尺子量长度, 结果不可比。现在把 6 部词典
    合成一张固定大词表, 全部文章统一用它。同一个词若在不同词典里有的
    判正有的判负, 就按"判正的词典多还是判负的多"投票定极性; 票数打平
    说明这词本身有歧义, 干脆不要。
    """
    bs_map = both_sided_by_dict if both_sided_by_dict is not None else _BOTH_SIDED_BY_DICT
    polarity_votes: dict[str, list[float]] = {}
    for _name, d in dictionaries:
        both = bs_map.get(_name, frozenset())
        for word, score in (d or {}).items():
            if word in both:
                # 跨类重叠词 → (+1,−1) 平衡双票 (margin 贡献 0 → union 逐位不变)
                polarity_votes.setdefault(word, []).append(1.0)
                polarity_votes[word].append(-1.0)
            else:
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

def _compute_sentiment_with_rules(
    tokens: list[str],
    sentiment_dict: dict[str, float],
    apply_negation: bool = True,
    apply_degree: bool = True,
    apply_adversative: bool = True,
    both_sided_words: frozenset[str] = frozenset(),
) -> tuple[float, float, int, int, list[dict[str, Any]]]:
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
        apply_negation: 是否应用否定翻转 (默认 True, 保留现行为)。False = 不翻号但**仍保留**
                        否定词识别 / continue / 窗口递减骨架 (与 degree/adversative 同款铁律,
                        只锁数值效应不动 scoping) — 用于 raw/degonly/advonly/degadv 等"无否定"
                        消融变体 (rule-ablation ladder, v3.11.1; 见 ``_RULE_ABLATION_VARIANTS``)。
        apply_degree:   是否应用程度副词加权 (默认 True, 保留现行为)。False = 程度倍率
                        锁 1.0 — 用于"仅否定"规则消融稳健性 (rule-ablation negonly)。
        apply_adversative: 是否应用转折 ×ADVERSATIVE_BOOST 加权 (默认 True)。False =
                        不放大转折后情感 — 同为"仅否定"稳健性变体。
                        注 (方案 a): 二者为 False 时仍**保留**程度/转折 token 的识别与
                        continue/句末重置骨架, 仅锁数值效应 → 与全规则共享 scoping,
                        否定窗口到达距离不被副作用改变 (删检测则会, 见方案 b 陷阱)。
        both_sided_words: 跨类重叠词集 (该词典 positive∩negative 同时出现, 用户决策
                        2026-06-24 "保留并两侧计数", 逆转 fix omni-g-tonewords-03 的双侧剔除)。
                        命中其中的 token → **同时**计入 pos_count 与 neg_count, 对
                        total_score 净贡献 0 (+final 与 −final 抵消), 对归一化分母
                        total_abs_score 贡献 2|final| → 把该词的语调拉向中性而非剔除。
                        否定/程度/转折规则正常作用于 |final| (否定对 ±对称的两侧无净效应,
                        程度/转折等比缩放两侧, 仍净 0)。默认空集 → 行为与旧版逐位一致
                        (union 词典/IDF 非重叠路径均传空集, golden-safe)。
                        ⚠ (full − negonly) 反映程度+转折对最终归一化语调的**联合净效应**,
                        非可加分解: full/negonly 各自 self-normalize (Σ|final| 分母随倍率
                        变化), 且否定×程度作用于同一词时倍率乘的是翻转后幅度 → 含
                        negation×degree 交互, 不可解读为程度/转折的纯因果贡献 (audit MATH-1)。

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
        # fix(rule-ablation negonly, 2026-06-13): apply_degree=False (仅否定稳健性) 时仍
        # **识别**程度副词并 continue — 保留否定窗口 passthrough (degree token 不消费
        # negation_remaining, 窗口递减位于本 if/elif 链之后), 仅把倍率锁为 1.0。若改为
        # 整段删除检测 (方案 b), 程度词会落入末尾 else 分支触发窗口递减, 副作用缩短否定
        # 有效到达距离, 污染"纯否定"语义。
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token] if apply_degree else 1.0
            continue

        # 检查情感词
        if token in sentiment_dict:
            base_score = sentiment_dict[token]

            # 应用否定词翻转
            # fix(rule-ablation v3.11.1): apply_negation=False (raw 等无否定变体) 时不翻号,
            # 但上方 NEGATION_WORDS 分支的识别/continue 与下方窗口递减 (L663-664) 一律保留
            # → 共享 scoping 骨架, 仅锁翻号数值效应 (与 degree/adversative 同款铁律, audit MATH-1)。
            if negation_remaining > 0 and apply_negation:
                base_score = -base_score

            # 应用程度副词
            final_score = base_score * degree_multiplier

            # 应用转折加权
            # fix(rule-ablation negonly, 2026-06-13): apply_adversative=False 时不放大,
            # 但上方 ADVERSATIVE_WORDS 分支仍 reset negation/degree (维持从句边界骨架)
            # → 与全规则共享 scoping (从句边界在两种打分变体抵消, 不污染 negonly 纯否定语义)。
            if adversative_active and apply_adversative:
                final_score *= ADVERSATIVE_BOOST

            if token in both_sided_words:
                # ── 跨类重叠词「两侧计数」(用户决策 2026-06-24, 逆转 fix omni-g-tonewords-03) ──
                # 该词在本词典 positive∩negative 同时出现 → 保留且不武断选边: 同时计入
                # pos/neg, 分子净贡献 0 (+mag 与 −mag 抵消), 分母进 2×|mag| → 语调拉向中性。
                # 否定翻号对 ±对称两侧无净效应, 程度/转折等比缩放两侧, 仍净 0、分母随之缩放。
                mag = abs(final_score)
                total_abs_score += 2.0 * mag
                pos_count += 1
                neg_count += 1
                # matched_words 记两条对称项 (base 取 ±|原始幅值|); 仅供 union 口径消费,
                # 当前 union 路径传空集故不会进入本分支, 此处为防御性正确 (若未来对个体
                # 词典取 matched 亦能正确双计)。
                _base_mag = abs(sentiment_dict[token])
                matched_words.append({'word': token, 'base': _base_mag,
                                      'final': round(mag, 4), 'boosted': adversative_active})
                matched_words.append({'word': token, 'base': -_base_mag,
                                      'final': round(-mag, 4), 'boosted': adversative_active})
                degree_multiplier = 1.0  # 已消费程度副词
                if negation_remaining > 0:
                    negation_remaining -= 1
                continue

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


# ============================================================================
# 4A. 规则消融梯度变体谱 (rule-ablation ladder) — 单一事实源 (v3.11.1)
# ============================================================================
# 把状态机三条语言学规则 (① 否定翻转 / ② 程度六级权重 / ③ 转折增强) 的**全 powerset**
# 组合物化为独立自归一化的中间得分列, 兑现"每经过一个步骤都要留存中间变量作为稳健性
# 检验"。每个变体 = (suffix, apply_negation, apply_degree, apply_adversative)。
#   article 列名 = ``{dict}_score_{suffix}{track}``  (写入 22_words_tone.parquet)
#   panel  列名 = ``{d}_{suffix}_tone{track}``       (encode.py bank-year mean)
#
# ⚠ 计数口径 (msent) **不入此谱**: 程度②/转折③ 是严格正乘子、永不翻号 → 对
#   (neg−pos)/(pos+neg) 计数零影响, msent_raw≡msent_score / msent_negdeg≡msent_negonly
#   全退化。msent 口径已由 msent_score (零规则) + msent_negonly (仅否定) 完整覆盖,
#   故**不新增任何 msent_* 列** (范围收敛关键)。
#
# ⚠ 非可加分解 (audit MATH-1): 每个变体各自 self-normalize (Σ|final| 分母随启用规则
#   变化), 且否定×程度作用同一词含交互 → 相邻级差**非**"某规则纯贡献", 仅作 ablation
#   稳健性对照。披露须报四级 corr + 逐级变号占比, 论文表述"定性不变"。
#
# full (T,T,T) = 主列 ``{dict}_score`` (不在本谱, 单独物化)。本谱含 negonly 在内的全部
# **非-full** 组合 (7 项); negonly (T,F,F) 经本谱物化的值与既有 ``{dict}_score_negonly``
# **字节一致** (相同 flag → 相同输出 → golden-safe, 旧手写 call site 已折入本谱)。
_RULE_ABLATION_VARIANTS: list[tuple[str, bool, bool, bool]] = [
    # (suffix,    apply_negation, apply_degree, apply_adversative)
    ('raw',       False, False, False),  # L0 零规则基线
    ('negonly',   True,  False, False),  # L1 仅否定 (既有, 折入)
    ('degonly',   False, True,  False),  # 仅程度
    ('advonly',   False, False, True),   # 仅转折
    ('negdeg',    True,  True,  False),  # L2 否定+程度 (= full − adversative)
    ('negadv',    True,  False, True),   # 否定+转折 (= full − degree)
    ('degadv',    False, True,  True),   # 程度+转折 (= full − negation)
]

# panel 聚合 / 标签 / 测试跨模块复用的 suffix 列 (单一事实源派生)。
RULE_ABLATION_SUFFIXES: list[str] = [v[0] for v in _RULE_ABLATION_VARIANTS]


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
         '内容'）上统一计算一次，**三轨 (full/ctx/ss) 共享同一份 content_full 语料 IDF**
         (绝不按轨分语料; ss 轨亦复用此权重) (fix 2026-06-10: 原裸 '内容' 与 TF 打分语料不一致)。
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
# fix(ss-deadlock, 2026-06-15): 用**可重入** RLock 而非 Lock。死锁路径:
# _inject_custom_dicts_to_jieba 持 _JIEBA_LOCK (L942) 后在锁内调
# _get_tone_tokenizer (L967), 若 _TONE_TOKENIZER 仍为 None, 后者会**再次**
# acquire 同一把 _JIEBA_LOCK (L931) → 同线程重入非可重入 Lock 即永久死锁
# (实测 stage 22 卡在"注入领域词汇"步、CPU 仅 ~1s 冻结; 仅当注入时 tokenizer
# 尚未惰性创建才触发, 故偶发: 首跑 tokenizer 已建则跳过重入侥幸不锁)。
# RLock 允许同线程重入, 彻底消除该死锁; 跨线程互斥语义不变。
_JIEBA_LOCK = threading.RLock()

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
    / ``build_idf_weights`` (DF 统计) / LM 6 子词典扫描
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

        # 6. 注入 LM 2011 JF 6 子词典 (uncert/litig/constr/modal_strong/modal_weak/complexity)
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
    _precut: list | None = None,
) -> dict[str, float]:
    """LM 6 子词典扫描 — tone tokenizer 版 (fix omni-g-tonewords-10/-11 配套, 2026-06-11).

    与只读模块 ``lm_non_sentiment._compute_lm_non_sentiment_for_text`` 逐项同语义
    (lmfls-01 word-token 分母 / 空文本 NaN / 返回键结构), 唯一差异 = 分词器:
    用注入了 LM 多字词的独立 tone tokenizer (``_get_tone_tokenizer``) 而非全局
    jieba。注入隔离后全局分词器无 LM 复合词 — 若仍走全局, 多字 LM 词 (~18.5%)
    会被切碎永不命中, completeness-02 修复将静默回归。``lm_non_sentiment.py``
    按修复纪律只读, 故在本文件做 tokenizer 替换包装。

    Args:
        text: 待分析的中文文本。
        dicts: ``load_lm_non_sentiment_dicts()`` 的 6 子词典 dict。

    Returns:
        与 ``_compute_lm_non_sentiment_for_text`` 同构 (v3.10.0 起 6 子集):
        {'n_tokens', 'n_uncert', 'frac_uncert', 'n_litig', 'frac_litig',
         'n_constr', 'frac_constr', 'n_modal_strong', 'frac_modal_strong',
         'n_modal_weak', 'frac_modal_weak', 'n_complexity', 'frac_complexity'}
    """
    # v3.10.0 泛型化: 与只读模块 _compute_lm_non_sentiment_for_text 同口径按 _SUBSETS 循环
    # 构建 empty/return (取代逐子集硬编码; 对现有 4 子集字节等价)。
    empty = {'n_tokens': 0}
    for s in _SUBSETS:
        p = SUBSET_PREFIX[s]
        empty[f'n_{p}'] = 0
        empty[f'frac_{p}'] = float('nan')
    if not text or not text.strip():
        return empty

    # [G] 复用调用方预切的 raw token (同文本同 tokenizer → 逐字节等价), 否则内部切
    tokens = _precut if _precut is not None else list(_get_tone_tokenizer().cut(text))
    # lmfls-01 同口径: 分母 = word-token 数 (排除纯标点/纯数字)
    word_tokens = [t for t in tokens if t.strip() and not _LMFLS_NONWORD_RE.fullmatch(t.strip())]
    n_tokens = len(word_tokens)
    if n_tokens == 0:
        return empty

    counts = {s: 0 for s in _SUBSETS}
    for tok in tokens:
        for s in _SUBSETS:
            if tok in dicts.get(s, frozenset()):
                counts[s] += 1

    result = {'n_tokens': n_tokens}
    for s in _SUBSETS:
        p = SUBSET_PREFIX[s]
        result[f'n_{p}'] = counts[s]
        result[f'frac_{p}'] = counts[s] / n_tokens
    return result


def _empty_article_result() -> dict:
    """空/无效/全空 token 文本的统一返回 (fix omni-g-tonewords empty-text contract, 2026-06-11).

    契约对称化: score / ratio / msent 空文本 → NaN (缺失语义, 与 clarity/LM/FLS
    的空文本 NaN 契约一致; 旧实现回填 0.0 伪中性, 在 panel 聚合中压低均值)。
    label 维持 '中性' (类别列, 供 stats 计数), 可读性三列维持 0.0 (长度类, 空文本
    长度为 0 是真值而非缺失)。

    三轨契约 (full/ctx/ss): 本函数返回 **无轨道后缀** 的键, 轨道后缀 (_full/_ctx/_ss)
    由 ``_dual_analyze`` 对各轨结果统一追加 → 三轨自动获得完整的 _ss 空文本键集合
    (含 content_ss 回退/空文本场景, 与 ctx 镜像), 无需在此显式枚举轨道。
    """
    result: dict[str, Any] = {}
    for dict_name, _ in ALL_DICTIONARIES:
        result[f'{dict_name}_score'] = float('nan')
        result[f'{dict_name}_label'] = '中性'
        result[f'{dict_name}_pos_ratio'] = float('nan')
        result[f'{dict_name}_neg_ratio'] = float('nan')
        # rule-ablation 梯度 (v3.11.1, 全 powerset): 空文本 → NaN (缺失语义, 与 _score 对称)
        for _abl_sfx in RULE_ABLATION_SUFFIXES:
            result[f'{dict_name}_score_{_abl_sfx}'] = float('nan')
    result['sentiment_details'] = ''

    result['avg_sentence_len'] = 0.0
    result['type_token_ratio'] = 0.0
    result['char_per_word'] = 0.0
    result['pos_ratio'] = float('nan')
    result['neg_ratio'] = float('nan')
    result['msent_score'] = float('nan')
    result['msent_negonly'] = float('nan')  # rule-ablation 计数口径变体, 空文本 NaN
    # IDF 加权列一致性初始化（确保所有行返回相同 key 结构）
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            result[f'{dict_name}_idf_score'] = float('nan')
            result[f'{dict_name}_idf_label'] = '中性'
    return result


def _analyze_single_article(content: str, _precut: list | None = None) -> dict:
    """对单篇文章执行所有词典的情感分析。

    分词只执行一次（独立 tone tokenizer, 见 ``_get_tone_tokenizer``），然后对每个
    词典独立计分。

    聚合列语义 (fix omni-g-tonewords-01/-05/-06, 2026-06-11):
        - ``pos_ratio`` / ``neg_ratio`` / ``msent_score`` / ``sentiment_details``
          的计数基 = 6 词典固定 **union 词典** (``build_union_dictionary``), 替代旧
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
    # [G] 复用调用方预切的 raw token (同文本同 tokenizer → 逐字节等价), 否则内部切
    tokens = _precut if _precut is not None else list(_get_tone_tokenizer().cut(content))

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
            # rule-ablation 梯度: 词典缺失时与 _score 一致回填 0.0 (本分支语义)
            for _abl_sfx in RULE_ABLATION_SUFFIXES:
                result[f'{dict_name}_score_{_abl_sfx}'] = 0.0
            continue

        # 该词典的跨类重叠词集 (两侧计数; 用户决策 2026-06-24)。非重叠词典 → 空集 → 旧行为。
        _bs = _BOTH_SIDED_BY_DICT.get(dict_name, frozenset())

        raw_score, norm_score, pos_cnt, neg_cnt, matched = \
            _compute_sentiment_with_rules(tokens, sentiment_dict, both_sided_words=_bs)

        result[f'{dict_name}_score'] = round(norm_score, 4)
        result[f'{dict_name}_label'] = _score_to_label(norm_score)

        # ── 规则消融梯度 (rule-ablation ladder, v3.11.1; 旧 negonly 折入此谱) ──
        # 全 powerset 中间变体, 各自独立 Σ|final| 自归一化 (与 {dict}_score 同口径)。framing:
        # raw(零规则, **幅度口径** Σ|base| 归一化, 加权 ±1.0 vs ±0.5 政治正面词, **非计数**);
        # **计数口径**零规则 (msent_score) 才 ≈ Tetlock 2007/Garcia 2013/Henry 2008 纯词频档
        # (raw 与 msent_score 同为零规则但口径不同, 勿混); negonly(仅否定)≈LM 2011 JF 档;
        # full 叠加 degree 六级权重 + 转折 boost (valence-shifter 谱系: Kennedy-Inkpen 2006/
        # Ding-Liu-Yu 2008/Taboada 2011)。用途 = 检验主语调对每条规则是否敏感 (论文表述
        # "定性不变"), 非声称某变体更优。⚠ 非可加分解 + 计数口径不入谱: 见 _RULE_ABLATION_VARIANTS
        # 注释 (audit MATH-1/MATH-3; 实测 corr(full,negonly)≈0.998-0.999 高度共线)。
        # negonly 变体经本谱物化的值与旧手写 call site 字节一致 (相同 flag → 相同输出, golden-safe)。
        for _abl_sfx, _abl_neg, _abl_deg, _abl_adv in _RULE_ABLATION_VARIANTS:
            _, _abl_norm, _, _, _ = _compute_sentiment_with_rules(
                tokens, sentiment_dict,
                apply_negation=_abl_neg, apply_degree=_abl_deg, apply_adversative=_abl_adv,
                both_sided_words=_bs)
            result[f'{dict_name}_score_{_abl_sfx}'] = round(_abl_norm, 4)

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
    # 最多的词典" (best-dict, 胜出词典逐篇切换 → 测量工具跨观测不固定) 改为 6 词典
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

    # ── 仅否定计数口径变体 msent_negonly (rule-ablation, 2026-06-13) ──
    # 与 msent_score (零规则, m['base'] 原始极性计数) 配对; 但对固定 union 词典施加否定
    # 翻转后再计数 (apply_degree/adversative=False → final 极性 = 否定翻转后极性):
    #   msent_negonly = (neg − pos) / (pos + neg)
    # 计数口径 (非 Σ|final| 幅度) → (msent_negonly − msent) 是**不混入归一化口径变更**的
    # 纯否定边际贡献 (见 redundancy 裁决: negation 只翻号不改 |final|, 若用 Σ|final| 口径
    # 与 msent 比会混入口径差)。空文本 → NaN (与 msent_score 契约对称)。
    if union_dict and n_word_tokens > 0:
        _, _, neg_pos_cnt, neg_neg_cnt, _ = _compute_sentiment_with_rules(
            tokens, union_dict, apply_degree=False, apply_adversative=False)
        neg_total = neg_pos_cnt + neg_neg_cnt
        result['msent_negonly'] = round(
            (neg_neg_cnt - neg_pos_cnt) / neg_total, 6) if neg_total > 0 else 0.0
    else:
        result['msent_negonly'] = float('nan')

    # ── IDF 加权并行度量 (Gentzkow et al. 2019, JEL §2.2) ──
    # 复用同一次 tone tokenizer 切词的 tokens，零额外分词开销
    if IDF_DICTIONARIES is not None:
        for dict_name, idf_dict in IDF_DICTIONARIES:
            if not idf_dict:
                result[f'{dict_name}_idf_score'] = 0.0
                result[f'{dict_name}_idf_label'] = '中性'
                continue
            # 跨类重叠词集与 raw 词典同口径 (IDF 仅缩放幅值, 不改极性归属; 两侧计数取 abs)
            _, idf_norm, _, _, _ = _compute_sentiment_with_rules(
                tokens, idf_dict, both_sided_words=_BOTH_SIDED_BY_DICT.get(dict_name, frozenset()))
            result[f'{dict_name}_idf_score'] = round(idf_norm, 4)
            result[f'{dict_name}_idf_label'] = _score_to_label(idf_norm)

    return result


# ============================================================================
# 6. 批处理和统计
# ============================================================================

def classify_batch(df_batch: pd.DataFrame) -> tuple:
    """对单个批次执行词典法三轨情感分析（全文 + 上下文片段 + 银行+金科同句）。

    Args:
        df_batch: 待分析的 DataFrame 批次（需含 'content_ctx' / 'content_ss' 列，
                  由阶段 13 ctx_materializer 物化、随 21 输出下传；content_ss 缺列时
                  在 _dual_analyze 内回退 ctx/全文，graceful skip）。

    Returns:
        tuple: (processed_df, stats_dict)
    """
    stats = {'total': 0}
    for dict_name, _ in ALL_DICTIONARIES:
        # 三轨 (full/ctx/ss): ss = 银行+金科同句轨, 镜像 ctx 计数初始化
        for track in ['_full', '_ctx', '_ss']:
            stats[f'{dict_name}_正面{track}'] = 0
            stats[f'{dict_name}_中性{track}'] = 0
            stats[f'{dict_name}_负面{track}'] = 0

    if df_batch.empty:
        return df_batch, stats

    df = df_batch.copy()
    stats['total'] = len(df)

    # 对每篇文章执行三轨情感分析 (full/ctx/ss)
    # content_ctx / content_ss 由阶段 13 ctx_materializer 物化为列 (随上游输出下传)，直接读取以确保各方法输入一致
    # v3.5.1 A1: 加载 clarity 词典 (lazy, batch 内 1 次)
    _def_set, _amb_set = load_clarity_dictionaries()
    # v3.5.2 PR #3: 加载 LM 6 子词典 (lru_cache 全局单例; 第 2 次调用 O(1))
    _lm_dicts = load_lm_non_sentiment_dicts()

    def _dual_analyze(row):
        # remove-title-track: full / ctx / ss 三轨文本均注入标题 (prepend_title); title 轨已取消
        from news_process.core.text.entity_context import prepend_title
        _title = str(row.get('标题', '') or '')
        content_full = prepend_title(_title, str(row.get('内容', '')))
        content_ctx = prepend_title(_title, str(row.get('content_ctx', str(row.get('内容', '')))))
        # 第三轨 ss (银行+金科同句): content_ss 由 stage 13 物化; 缺列时回退 content_ctx
        # (其本身缺列时再回退裸 '内容') → graceful skip, 镜像 ctx 回退公理 (ss_is_fallback)。
        content_ss = prepend_title(
            _title, str(row.get('content_ss', row.get('content_ctx', row.get('内容', '')))))

        # [G] 每轨 raw cut 算一次, 主分/clarity/LM 三函数复用 → 省 6/9 次 tone 分词。
        # 同文本同 tone tokenizer 单例 → 逐字节等价 (实测 jieba 确定性); 各函数仍各自做
        # 自己的 whitespace/word-token 过滤 (空白 token 进状态机会改分, 故过滤不可省)。
        _tok_full = list(_get_tone_tokenizer().cut(content_full))
        _tok_ctx = list(_get_tone_tokenizer().cut(content_ctx))
        _tok_ss = list(_get_tone_tokenizer().cut(content_ss))
        res_full = _analyze_single_article(content_full, _precut=_tok_full)
        res_ctx = _analyze_single_article(content_ctx, _precut=_tok_ctx)
        res_ss = _analyze_single_article(content_ss, _precut=_tok_ss)

        # 合并：为每个键追加轨道后缀 (三轨 full/ctx/ss)
        merged = {}
        for k, v in res_full.items():
            merged[f'{k}_full'] = v
        for k, v in res_ctx.items():
            merged[f'{k}_ctx'] = v
        for k, v in res_ss.items():
            merged[f'{k}_ss'] = v

        # v3.5.1 A1 三轨 clarity (per plan v0.3 §2.1.1 修 R3-C1):
        # 对 content_full + content_ctx + content_ss **独立扫描** (title 轨不纳入, 修 R3-H1
        # 锁定排除 — title 文本 < 50 字符分母不稳).
        clarity_full = _compute_clarity_for_text(content_full, _def_set, _amb_set, _precut=_tok_full)
        clarity_ctx = _compute_clarity_for_text(content_ctx, _def_set, _amb_set, _precut=_tok_ctx)
        clarity_ss = _compute_clarity_for_text(content_ss, _def_set, _amb_set, _precut=_tok_ss)
        for k, v in clarity_full.items():
            merged[f'clarity_{k}_full'] = v
        for k, v in clarity_ctx.items():
            merged[f'clarity_{k}_ctx'] = v
        for k, v in clarity_ss.items():
            merged[f'clarity_{k}_ss'] = v

        # v3.5.2 PR #3 (A1): LM 6 non-sentiment 子词典三轨扫描.
        # 关键 panel 列: uncert_frac_{full,ctx,ss} / litig_frac_{full,ctx,ss} /
        # constr_frac_{full,ctx,ss} / modal_strong_frac_{full,ctx,ss}.
        # fix(omni-g-tonewords-10/-11, 2026-06-11): 改走 tone tokenizer 包装 —
        # lm_non_sentiment 原函数内部用全局 jieba, 注入隔离后会把多字 LM 词切碎。
        lm_full = _compute_lm_non_sentiment_for_text_tone_tok(content_full, _lm_dicts, _precut=_tok_full)
        lm_ctx = _compute_lm_non_sentiment_for_text_tone_tok(content_ctx, _lm_dicts, _precut=_tok_ctx)
        lm_ss = _compute_lm_non_sentiment_for_text_tone_tok(content_ss, _lm_dicts, _precut=_tok_ss)
        for k in SUBSET_PREFIXES:  # v3.10.0: 6 子集 (含 modal_weak/complexity)
            merged[f'{k}_frac_full'] = lm_full.get(f'frac_{k}', float('nan'))
            merged[f'{k}_frac_ctx'] = lm_ctx.get(f'frac_{k}', float('nan'))
            merged[f'{k}_frac_ss'] = lm_ss.get(f'frac_{k}', float('nan'))

        # v3.5.2 PR #3 (A2): Forward-Looking Statements 比例三轨.
        fls_full = compute_fls_for_text(content_full)
        fls_ctx = compute_fls_for_text(content_ctx)
        fls_ss = compute_fls_for_text(content_ss)
        merged['frac_fls_full'] = fls_full.get('frac_fls', float('nan'))
        merged['frac_fls_ctx'] = fls_ctx.get('frac_fls', float('nan'))
        merged['frac_fls_ss'] = fls_ss.get('frac_fls', float('nan'))

        return merged

    results = df.apply(_dual_analyze, axis=1)

    # [I] 把 Series-of-dict 一次性展开成宽表 (单次 C 级构建), 取代下方数百次
    # results.apply(lambda r: r.get(k, default)) 的逐列全量 Python 遍历。逐列取值与原
    # .apply(r.get(k, default)) 逐字节等价: 始终存在的键 (score/label 等) recs[k] 即原值;
    # 可缺键 (lexical/clarity/lm 等) 其默认恰为 NaN, 与 DataFrame 缺键填 NaN 一致;
    # 绝不对"已存在的合法 NaN"再 fillna。列序/列集由下方显式枚举循环锁定 (不依赖 recs 列序)。
    # ⚠ 不变量 (须维持): 凡用非-NaN 默认 (_score=0.0/_label='中性'/pos_ratio/msent_*) 提取的键,
    #   必须在空文本与满文本两条返回路径都无条件存在 (_empty_article_result 也产出)。否则
    #   recs 缺键行被 _col 回退为默认 Series 但'部分缺键'会被填 NaN → 破 golden。新增此类键须复核。
    recs = pd.DataFrame(results.tolist(), index=df.index)

    def _col(_k, _default):
        """按键取列: 存在取 recs[_k] (== 原 r.get 口径); 整列缺键回退默认 Series。"""
        return recs[_k] if _k in recs.columns else pd.Series(_default, index=df.index)

    # 提取各列（三轨 full/ctx/ss）。先攒成一个列字典, 再一次性 concat, 避免大量
    # ``df[col] = ...`` 造成 pandas block fragmentation。
    # ss = 银行+金科同句轨: 缺 content_ss 时 _dual_analyze 已回退 → 各 key 必存在,
    # 此处与 full/ctx 同口径提取 (_col 兜底)。
    new_columns = {}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx', '_ss']:
            score_key = f'{dict_name}_score{track}'
            label_key = f'{dict_name}_label{track}'
            label_series = _col(label_key, '中性')
            new_columns[score_key] = _col(score_key, 0.0)
            new_columns[label_key] = label_series

            label_counts = label_series.value_counts()
            stats[f'{dict_name}_正面{track}'] = int(label_counts.get('正面', 0))
            stats[f'{dict_name}_中性{track}'] = int(label_counts.get('中性', 0))
            stats[f'{dict_name}_负面{track}'] = int(label_counts.get('负面', 0))

            # 单词典 pos/neg ratio 提取 (Garcia 2013, JF)
            pos_key = f'{dict_name}_pos_ratio{track}'
            neg_key = f'{dict_name}_neg_ratio{track}'
            new_columns[pos_key] = _col(pos_key, 0.0)
            new_columns[neg_key] = _col(neg_key, 0.0)

            # rule-ablation 梯度 score 提取 (v3.11.1, 全 powerset; Σ|final| 口径; 缺则 NaN)
            for _abl_sfx in RULE_ABLATION_SUFFIXES:
                _abl_key = f'{dict_name}_score_{_abl_sfx}{track}'
                new_columns[_abl_key] = _col(_abl_key, float('nan'))

    # sentiment_details 三轨提取 (full/ctx/ss); ss = 银行+金科同句轨
    new_columns['sentiment_details_full'] = _col('sentiment_details_full', '')
    new_columns['sentiment_details_ctx'] = _col('sentiment_details_ctx', '')
    new_columns['sentiment_details_ss'] = _col('sentiment_details_ss', '')

    # ── 提取 IDF 加权列（三轨 full/ctx/ss）──
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx', '_ss']:
                score_key = f'{dict_name}_idf_score{track}'
                label_key = f'{dict_name}_idf_label{track}'
                new_columns[score_key] = _col(score_key, 0.0)
                new_columns[label_key] = _col(label_key, '中性')

    # ── 提取新增指标列（三轨 full/ctx/ss）──
    new_metric_cols = [
        'avg_sentence_len', 'type_token_ratio', 'char_per_word',
        'pos_ratio', 'neg_ratio',
        'msent_score',  # Henry (2008) JBC / Tetlock (2007) JF — see derivation lines 1324-1348
        'msent_negonly',  # rule-ablation 计数口径变体 (仅否定; 与 msent_score 配对)
    ]
    for col in new_metric_cols:
        for track in ['_full', '_ctx', '_ss']:
            col_key = f'{col}{track}'
            new_columns[col_key] = _col(col_key, 0.0)

    # ── v3.5.1 A1 三轨 clarity 列提取 (per plan v0.3 §2.1.1 + §2.1.3) ──
    # title 轨不纳入 (R3-H1 锁定); full + ctx + ss 三轨各自独立扫描 (ss=银行+金科同句).
    clarity_metric_cols = [
        'n_definite', 'n_ambiguous', 'n_tokens_clarity_base',
        'frac_definite', 'frac_ambiguous', 'clarity_score',
    ]
    for col in clarity_metric_cols:
        for track in ['_full', '_ctx', '_ss']:
            col_key = f'clarity_{col}{track}'
            new_columns[col_key] = _col(col_key, float('nan'))

    # ── v3.5.2 PR #3 (A1 LM 6 子词典 + A2 FLS) 三轨列提取 ──
    # A1: uncert_frac_{full,ctx,ss} / litig_frac_{full,ctx,ss} / constr_frac_{full,ctx,ss}
    #     / modal_strong_frac_{full,ctx,ss}
    # A2: frac_fls_{full,ctx,ss}
    # title 轨不纳入 (与 clarity 同款决策, R3-H1 锁定 — title 文本 < 50 字符); ss=银行+金科同句.
    lm_a2_metric_cols = [f'{p}_frac' for p in SUBSET_PREFIXES] + ['frac_fls']
    for col in lm_a2_metric_cols:
        for track in ['_full', '_ctx', '_ss']:
            col_key = f'{col}{track}'
            new_columns[col_key] = _col(col_key, float('nan'))

    # ── 词汇/句法复杂度 $0 测度族 (批 #2–#6) + 词级长度 n_words_real (批 #7)
    #    + 汉字级长度 n_han_real (HAN_COUNT_KEY, hanzi-char-dual 2026-06-13) 三轨列提取 ──
    for col in (*LEXICAL_COMPLEXITY_KEYS, WORD_COUNT_KEY, HAN_COUNT_KEY):
        for track in ['_full', '_ctx', '_ss']:
            col_key = f'{col}{track}'
            new_columns[col_key] = _col(col_key, float('nan'))

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
        # 三轨 (full/ctx/ss): ss = 银行+金科同句轨
        for track in ['_full', '_ctx', '_ss']:
            merged[f'{dict_name}_正面{track}'] = 0
            merged[f'{dict_name}_中性{track}'] = 0
            merged[f'{dict_name}_负面{track}'] = 0

    for s in stats_list:
        merged['total'] += s['total']
        for dict_name, _ in ALL_DICTIONARIES:
            for track in ['_full', '_ctx', '_ss']:
                merged[f'{dict_name}_正面{track}'] += s.get(f'{dict_name}_正面{track}', 0)
                merged[f'{dict_name}_中性{track}'] += s.get(f'{dict_name}_中性{track}', 0)
                merged[f'{dict_name}_负面{track}'] += s.get(f'{dict_name}_负面{track}', 0)
    return merged


def log_classification_report(stats: dict, logger, track_suffix: str = ''):
    """输出词典法情感分析统计报告。

    Args:
        stats:         合并后的统计字典。
        logger:        日志记录器。
        track_suffix:  轨道后缀 ('_full' / '_ctx' / '_ss')，用于区分报告。
    """
    track_label = (
        '全文' if track_suffix == '_full'
        else '上下文片段' if track_suffix == '_ctx'
        else '银行+金科同句' if track_suffix == '_ss'
        else ''
    )
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
        pos_pct = pct4(pos / total) if total > 0 else "N/A"
        neu_pct = pct4(neu / total) if total > 0 else "N/A"
        neg_pct = pct4(neg / total) if total > 0 else "N/A"
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
        logger.info(f"  {col_label}: Z-score 标准化完成 (μ={sig4(mean_val)}, σ={sig4(std_val)})")
        return (series - mean_val) / std_val
    logger.error(
        f"  {col_label}: Z-score 退化 (μ={mean_val!r}, σ={std_val!r}) → 整列置 NaN "
        f"(fix omni-g-tonewords-13; 旧行为整列回填 0.0 伪零分, 缺失被抹成'恰均值')")
    return pd.Series(np.nan, index=series.index)


# ============================================================================
# 7. 主函数
# ============================================================================

def _log_environment_and_config(input_path: str, output_path: str) -> None:
    """打印项目/环境信息 + 运行配置 (日志富集, 2026-06-24)。

    目标 (用户要求"在日志文件中提供尽可能多的项目信息、运行期间信息和运行结果信息"):
    把"谁在跑、跑在什么环境、读写哪些文件、用了哪些可调参数"一次性落进日志, 便于
    复现核对 / 审计 / 排错。纯日志, 不改任何产物 (golden-safe)。
    """
    try:
        preview_path = output_path.replace('.parquet', '.csv')
        idf_json = os.path.join(CONFIG['paths']['output_dir'], '22_idf_weights.json')
        bank_file = CONFIG['paths'].get('bank_names_file', '(默认)')
        fintech_file = CONFIG['paths'].get('fintech_dict_file', '(默认)')
        parallel_cfg = CONFIG.get('parallel', {})

        logger.info("  🧭 项目 / 环境信息")
        logger.info(f"     · 阶段: {STAGE_NAME} (词典法情感分析, STAGES_MAIN; 三轨 full/ctx/ss)")
        logger.info("     · 行为版本: 跨类重叠词『保留并两侧计数』(用户决策 2026-06-24, "
                    "逆转 fix omni-g-tonewords-03 的双侧剔除)")
        logger.info(f"     · 模块文件: {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        logger.info(f"     · jieba:    {getattr(jieba, '__version__', '?')} (冻结锚点 0.42.1; "
                    "确定性来源=jieba版本+词典文件)")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
                    "本阶段纯 CPU / 无 LLM·网络·API ($0)")

        logger.info("  📂 输入 / 输出文件")
        logger.info(f"     · 输入:   {input_path}")
        logger.info(f"     · 输出:   {output_path}")
        logger.info(f"     · 预览:   {preview_path}")
        logger.info(f"     · IDF权重:{idf_json}")
        logger.info(f"     · 词典文件: {TONE_DICTS_FILE}")
        logger.info(f"     · 注入词源: 银行名={bank_file} | 金科={fintech_file}")

        logger.info("  ⚙ 运行配置 (config/sentiment.yaml::sentiment_analysis.tone_words 等)")
        logger.info(f"     · IDF 加权: {SENTIMENT_PARAMS.get('idf_weighting', True)} "
                    f"| 否定窗口 NEGATION_WINDOW={NEGATION_WINDOW} "
                    f"| 转折增强 ADVERSATIVE_BOOST={ADVERSATIVE_BOOST}")
        logger.info(f"     · 语言学规则词表: 否定词={len(NEGATION_WORDS)} | 程度副词={len(DEGREE_WORDS)} "
                    f"| 转折连词={len(ADVERSATIVE_WORDS)} | 句末标点={len(SENTENCE_END_MARKERS)}")
        logger.info(f"     · 并行: batch_size={parallel_cfg.get('batch_size', 5000)} "
                    f"| n_jobs={parallel_cfg.get('n_jobs', -1)} (joblib threads)")
        logger.info("     · 标签阈值: 正面>+0.1 / 负面<−0.1 / 其间=中性 (_score_to_label)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  环境/配置信息打印失败 (不影响处理): {e}")


def main():
    """词典法情感分析阶段主入口。"""
    global ALL_DICTIONARIES, IDF_DICTIONARIES
    
    stage_start = time.time()
    logger.info(f"--- 开始执行阶段: {STAGE_NAME} ---")
    logger.info("")
    logger.info("  📌 阶段目的")
    logger.info("     使用六部中文金融情感词典对每篇新闻进行情感打分。")
    logger.info("     每部词典独立计算正/负词频比, 并通过语言学规则(否定/程度/转折)修正。")
    logger.info("     采用三轨模式: 全文(_full)、上下文片段(_ctx)和银行+金科同句(_ss)分别计算, 供下游三角验证。")
    logger.info("")
    logger.info("  📖 方法论依据 (核心方法/构念的学术出处, 引文逐字取自经核验注册表)")
    try:
        # IDF 加权 (TF-IDF 文本量化): 降低高频常见词权重, 提升稀有金融术语区分度
        logger.info("     · IDF 加权 (TF-IDF 文本量化) §2.2:")
        logger.info("       Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. "
                    "Journal of Economic Literature, 57(3), 535-574. "
                    "https://doi.org/10.1257/jel.20181020")
        # 否定词翻转: 否定窗口内极性翻号 (中文情感分析的标准 valence-shifter 处理)
        logger.info("     · 语言学规则①否定词翻转 (negation valence shifter):")
        logger.info("       Jia, L., Yu, C., & Meng, W. (2009). The effect of negation on "
                    "sentiment analysis and retrieval effectiveness. In Proceedings of the "
                    "18th ACM Conference on Information and Knowledge Management (CIKM '09) "
                    "(pp. 1827-1830). ACM. https://doi.org/10.1145/1645953.1646241")
        logger.info("       Pang, B., & Lee, L. (2008). Opinion mining and sentiment analysis. "
                    "Foundations and Trends® in Information Retrieval, 2(1-2), 1-135. "
                    "https://doi.org/10.1561/1500000011")
        # 程度副词六级权重: 放大/缩小情感强度的 contextual valence shifter
        logger.info("     · 语言学规则②程度副词六级权重 (degree contextual valence shifter):")
        logger.info("       Li, F., Huang, M., & Zhu, X. (2010). Sentiment analysis with global "
                    "topics and local dependency. Proceedings of the AAAI Conference on "
                    "Artificial Intelligence, 24(1), 1371-1376. "
                    "https://doi.org/10.1609/aaai.v24i1.7523")
        logger.info("       Kennedy, A., & Inkpen, D. (2006). Sentiment classification of movie "
                    "reviews using contextual valence shifters. Computational Intelligence, "
                    "22(2), 110-125. https://doi.org/10.1111/j.1467-8640.2006.00277.x")
        logger.info("       Liu, B. (2012). Sentiment analysis and opinion mining. Synthesis "
                    "Lectures on Human Language Technologies. Morgan & Claypool Publishers. "
                    "https://doi.org/10.2200/s00416ed1v01y201204hlt016")
        # 转折连词增强: 转折后子句权重提升 (holistic lexicon-based opinion mining)
        logger.info("     · 语言学规则③转折连词增强 (adversative reweighting):")
        logger.info("       Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based "
                    "approach to opinion mining. In Proceedings of the International Conference "
                    "on Web Search and Web Data Mining (WSDM '08) (pp. 231-240). ACM. "
                    "https://doi.org/10.1145/1341531.1341561")
        # 固定 union 词典聚合测度 (msent/pos_ratio/neg_ratio) 的金融文本词典法构念
        logger.info("     · 固定词表聚合测度 (msent/pos_ratio/neg_ratio):")
        logger.info("       Tetlock, P. C. (2007). Giving content to investor sentiment: The role "
                    "of media in the stock market. The Journal of Finance, 62(3), 1139-1168. "
                    "https://doi.org/10.1111/j.1540-6261.2007.01232.x")
        logger.info("       García, D. (2013). Sentiment during recessions. The Journal of "
                    "Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027")
        logger.info("       Henry, E. (2008). Are investors influenced by how earnings press "
                    "releases are written? Journal of Business Communication, 45(4), 363-407. "
                    "https://doi.org/10.1177/0021943608319388")
        # 金融文本词典法的权威综述与中文金融情感词典基底
        logger.info("     · 金融文本词典法基底 (Loughran-McDonald):")
        logger.info("       Loughran, T., & McDonald, B. (2011). When is a liability not a "
                    "liability? Textual analysis, dictionaries, and 10-Ks. The Journal of "
                    "Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"  方法论引文打印失败 (不影响处理): {e}")
    logger.info("")
    logger.info("  📊 关键指标解读")
    logger.info("     · Z-score 标准化: 均值=0, 标准差=1。正值=正面倾向, 负值=负面倾向")
    logger.info("     · IDF 权重分位数: P25-P75 的范围越窄 → 词典词汇区分度越均匀")
    logger.info("     · 正/中/负面占比: 若某词典负面>60%, 可能存在负面偏差")
    logger.info("")

    # 定义输入输出 (提前到环境信息块之前, 便于一次性披露读写路径)
    input_path = os.path.join(CONFIG['paths']['output_dir'], CONFIG['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet'))
    output_path = os.path.join(CONFIG['paths']['output_dir'],
                               CONFIG['filenames'].get('output_22_words_tone', '22_words_tone.parquet'))

    # 项目/环境信息 + 运行配置 (日志富集 2026-06-24)
    _log_environment_and_config(input_path, output_path)
    logger.info("")

    # 运行期阶段计时累计 (各主要阶段墙钟耗时, 末尾汇总打印)
    phase_durations: dict[str, float] = {}

    # 延迟加载词典和注入 jieba（避免 import 时的副作用）
    _t = time.time()
    ALL_DICTIONARIES = load_all_dictionaries()
    _inject_custom_dicts_to_jieba()
    phase_durations['①词典加载+jieba注入'] = time.time() - _t

    non_empty_dicts = [(name, d) for name, d in ALL_DICTIONARIES if len(d) > 0]
    if not non_empty_dicts:
        logger.error("所有情感词典均为空！请检查词典文件。")
        raise SystemExit(1)

    # 词典概况富集: union 词典规模 + clarity/LM 子词典规模 (运行期信息)
    try:
        _union_sz = len(_get_union_dictionary())
        _def_set, _amb_set = load_clarity_dictionaries()
        _lm_sz = {k: len(v) for k, v in load_lm_non_sentiment_dicts().items()}
        logger.info(f"词典概况: 固定 union 词典={_union_sz} 词 (跨词典多数票+平票剔除); "
                    f"clarity definite={len(_def_set)}/ambiguous={len(_amb_set)} (含重叠词两侧保留); "
                    f"LM 非极性子集={_lm_sz}")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"词典概况富集失败 (不影响处理): {e}")

    logger.info(f"有效词典: {len(non_empty_dicts)}/{len(ALL_DICTIONARIES)} 个")

    if not os.path.exists(input_path):
        logger.error(f"输入文件未找到: {input_path}")
        raise SystemExit(1)

    logger.info(f"正在从 {input_path} 加载数据...")
    _t = time.time()
    df = pd.read_parquet(input_path)
    input_rows = len(df)
    phase_durations['②读取输入parquet'] = time.time() - _t
    logger.info(f"已加载 {input_rows:,} 行数据。")
    # 运行期信息: 输入列概况 (三轨文本列是否齐备, 直接决定 ctx/ss 轨是否回退)
    _track_cols = [c for c in ('内容', '标题', 'content_ctx', 'content_ss', 'content_full') if c in df.columns]
    logger.info(f"输入列概况: 共 {df.shape[1]} 列; 关键文本列存在={_track_cols}")
    log_memory_usage(logger, "数据加载后")

    # ── IDF 加权稳健性检验初始化 ──
    IDF_DICTIONARIES = None
    idf_enabled = SENTIMENT_PARAMS.get('idf_weighting', True)
    _t = time.time()
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
                    f"  {dict_name}: {len(w):,} 词, "
                    f"IDF [min={sig4(vals.min())}, P25={sig4(np.percentile(vals, 25))}, "
                    f"P50={sig4(np.percentile(vals, 50))}, P75={sig4(np.percentile(vals, 75))}, "
                    f"max={sig4(vals.max())}]"
                )
                sorted_w = sorted(w.items(), key=lambda x: x[1], reverse=True)
                top5 = [(k, sig4(v)) for k, v in sorted_w[:5]]
                bot5 = [(k, sig4(v)) for k, v in sorted_w[-5:]]
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
    phase_durations['③IDF加权构建'] = time.time() - _t

    # 执行词典法情感分析
    logger.info(f"开始执行词典法情感分析...")
    batch_size = CONFIG['parallel'].get('batch_size', 5000)
    num_batches = max(1, (len(df) - 1) // batch_size + 1)
    df_batches = [df.iloc[i * batch_size:(i + 1) * batch_size] for i in range(num_batches)]

    all_stats = []
    processed_dfs = []
    n_jobs = CONFIG['parallel'].get('n_jobs', -1)
    logger.info(f"使用 joblib 并行处理: n_jobs={n_jobs}, 共 {num_batches} 个批次 "
                f"(batch_size={batch_size}; 每篇 6 词典 × 3 轨 × (1 主分+7 消融+IDF) 打分)")

    _t = time.time()
    results = Parallel(n_jobs=n_jobs, prefer='threads')(
        delayed(classify_batch)(batch) for batch in df_batches
    )
    for res_df, res_stats in results:
        processed_dfs.append(res_df)
        all_stats.append(res_stats)
    phase_durations['④三轨词典打分(并行)'] = time.time() - _t

    # 合并全部结果
    processed_df = pd.concat(processed_dfs, ignore_index=True)
    log_memory_usage(logger, "三轨打分完成")

    # P1-4: 为每个词典的得分列添加 Z-score 标准化列（三轨 full/ctx/ss 独立计算）
    # 解决跨词典量纲不一致问题，供 64_tone_validation.py 的 Cronbach's Alpha 分析使用
    # 注意：_full / _ctx / _ss 的 μ 和 σ 必须独立计算，因文本长度差异导致数值分布本质不同
    # ss = 银行+金科同句轨; score_col 缺失时 (理论上 _dual_analyze 必产, 此守卫为防御) 优雅跳过。
    # fix(omni-g-tonewords-13, 2026-06-11): σ 退化分支改整列 NaN (见 _zscore_or_nan),
    # 不再回填 0.0 伪零分; 正常分支 NaN 传播行为不变。
    zscore_columns = {}
    for dict_name, _ in ALL_DICTIONARIES:
        for track in ['_full', '_ctx', '_ss']:
            score_col = f"{dict_name}_score{track}"
            zscore_col = f"{dict_name}_zscore{track}"
            if score_col in processed_df.columns:
                zscore_columns[zscore_col] = _zscore_or_nan(
                    processed_df[score_col], f"{dict_name} [{track}]")

    # IDF 列 Z-score 标准化 (三轨 full/ctx/ss)
    if IDF_DICTIONARIES is not None:
        for dict_name, _ in IDF_DICTIONARIES:
            for track in ['_full', '_ctx', '_ss']:
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

    _t = time.time()  # ⑤ 派生增强 (num_intensity + boilerplate) 计时起点

    # v3.5.1 A3: Numerical Intensity 三轨 post-processor (per plan v0.3 §2.2.3 修 R3-C2 + H4).
    # 对 content_full + content_ctx + content_ss 各调用 compute_num_intensity 一次, 写入
    # num_intensity_{full,ctx,ss} 等 article 列. 锚定: 数值披露强度
    # (Davis & Tama-Sweet 2012 CAR; 原引 Hales 2011 系误归, 见 numerical_intensity 模块 docstring).
    # 依赖方向: tone_words → numerical_intensity (单向); ss 轨 (银行+金科同句) 的实际派生
    # 由 numerical_intensity 模块负责 (本文件仅传 ss_col)。
    try:
        from news_process.pipeline.sentiment.numerical_intensity import (
            enrich_with_num_intensity_dual_track,
        )
        # fix(genA-01/V4): full 轨须读 content_full(含标题, v3.8.0+ 多轨契约 full/ctx/ss), 不再用
        # 默认裸 '内容' — 否则 num_intensity_full 是唯一不含标题的 *_full 情感族指标,
        # 与同 stage 的 clarity/LM/FLS(均已读 content_full)轨道不对称。
        _ni_full_col = 'content_full' if 'content_full' in processed_df.columns else '内容'
        # 三轨: ss 轨读 content_ss (银行+金科同句); 缺列时由 numerical_intensity 内部
        # graceful 回退 (镜像 ctx 回退公理)。num_intensity 模块需支持 ss_col 形参方落地
        # ss 列; 未支持时本调用整体 except 优雅跳过 (wire-ahead, 不阻断 full/ctx)。
        processed_df = enrich_with_num_intensity_dual_track(
            processed_df, full_col=_ni_full_col, ss_col='content_ss')
        logger.info(
            f"v3.5.1 A3: num_intensity 三轨派生完成 (full 轨={_ni_full_col} + ctx + ss 独立扫描)")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"v3.5.1 A3 num_intensity enrich 失败 (graceful skip): {e}")

    # nonpolarity-dims WS-B2: boilerplate_phrase_ratio_full 单轨 post-processor (语料级两遍).
    # 跨文档高频套话短语命中率 (Lang-Stice-Lawrence 2015 JAE; Dyer-LSL 2017 JAE); 单轨 full
    # (套话集口径在 ctx/ss 子窗口意义弱, by-design 延后); 语料=本 stage 输入子集 (如实披露)。
    # 确定性纯 jieba/sklearn $0; 缺列/空套话集 graceful → 全 nan + WARNING (boilerplate 模块内)。
    try:
        from news_process.pipeline.sentiment.boilerplate import enrich_with_boilerplate
        _bp_col = 'content_full' if 'content_full' in processed_df.columns else '内容'
        processed_df = enrich_with_boilerplate(processed_df, text_col=_bp_col)
        logger.info(f"nonpolarity-dims WS-B2: boilerplate 单轨派生完成 (语料={_bp_col})")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"WS-B2 boilerplate enrich 失败 (graceful skip): {e}")
    phase_durations['⑤派生增强(num_intensity+boilerplate)'] = time.time() - _t

    # 使用数据版本控制保存
    from news_process.core.data_versioning import save_parquet_with_metadata
    _t = time.time()
    save_parquet_with_metadata(
        df=processed_df,
        output_path=output_path,
        stage_name="22_tone_words",
        config=CONFIG,
        input_files=[input_path],
    )
    phase_durations['⑥落盘parquet'] = time.time() - _t
    logger.info(f"产物已落盘: {output_path} (形状 {processed_df.shape[0]:,} 行 × {processed_df.shape[1]:,} 列)")

    # 统计报告（三轨 full/ctx/ss 分别打印）
    if all_stats:
        merged_stats = merge_stats(all_stats)
        log_classification_report(merged_stats, logger, track_suffix='_full')
        log_classification_report(merged_stats, logger, track_suffix='_ctx')
        log_classification_report(merged_stats, logger, track_suffix='_ss')



    # 生成预览
    preview_path = output_path.replace('.parquet', '.csv')
    safe_save_preview_csv(processed_df, preview_path, logger)

    # ────────────────────────────────────────────────────────────────────
    # 【结果分析】对本次产出的关键指标逐个打印数值 + 对照阈值/预期方向给判读。
    # 注: 以下全部为纯日志用局部变量, 不回写 processed_df / 不改任何产物 (golden-safe)。
    # ────────────────────────────────────────────────────────────────────
    try:
        n_out = len(processed_df)
        logger.info("-" * 72)
        logger.info("【结果分析】词典法情感分析三轨产出诊断 (查字典版情绪打分, 给 LLM 找独立旁证)")
        logger.info(f"  行数守恒: 输入 {input_rows:,} → 输出 {n_out:,} 行 "
                    f"({'一致, 词典法只加列不删行 (符合预期)' if n_out == input_rows else '⚠ 不一致, 请检查 classify_batch 是否丢行'})")
        _both_n = sum(len(s) for s in _BOTH_SIDED_BY_DICT.values())
        logger.info(f"  有效词典: {len(non_empty_dicts)}/{len(ALL_DICTIONARIES)} 部 "
                    f"(jiang/yao/bian/du/you/loughran 六部金融情感词典; 跨类重叠词共 {_both_n} 个"
                    f"保留并两侧计数, 用户决策 2026-06-24 逆转旧双侧剔除 — 只影响各词典个体 "
                    f"{{dict}}_score, union/msent/ratio 因 (+1,−1) 平衡双票而逐位不变)")

        # ── 指标①: msent_score (零规则原始极性 (neg−pos)/(pos+neg)) 的均值与覆盖率 ──
        # 口径提示: msent = (负面词−正面词)/(正负面词总数), **越大越负面** (与直觉相反)。
        # 判读: 均值 ∈ (-1,+1); 接近 0 = 正负基本平衡; 显著为正(mean>0) = 负面词占优 = 整体偏负面;
        #       显著为负(mean<0) = 正面词占优 = 整体偏正面。(真数据 mean≈-0.79 / 98.2% 正面词 → 偏正面)
        logger.info("  · 指标① msent_score (原始极性计数, 零语言学规则; ≈ Tetlock 2007/Garcia 2013/Henry 2008; 越大越负面):")
        for track, tlabel in [('_full', '全文'), ('_ctx', '上下文片段'), ('_ss', '银行+金科同句')]:
            col = f"msent_score{track}"
            if col in processed_df.columns:
                s = pd.to_numeric(processed_df[col], errors='coerce')
                n_valid = int(s.notna().sum())
                cov = n_valid / n_out * 100 if n_out else 0.0
                mean_v = s.mean()
                if n_valid == 0:
                    logger.warning(f"      [{tlabel}] {col}: 该轨无有效数据(全 NaN, 该轨文本可能整体为空, 优雅降级) — 影响该轨词典情感")
                else:
                    # P0 方向 (msent=(neg−pos)/total, 越大越负面): mean>0 → 负面词占优 → 整体偏负面;
                    # mean<0 → 正面词占优 → 整体偏正面 (两条独立审计 + 真数据 mean=-0.79/98.2%正面词 坐实)。
                    direction = ("整体偏负面" if mean_v > 0.05 else
                                 "整体偏正面" if mean_v < -0.05 else "正负大致平衡")
                    logger.info(f"      [{tlabel}] 均值={sig4(mean_v)} ({direction}), "
                                f"覆盖={n_valid:,}/{n_out:,} ({pct4(cov, fraction=False)})")
            else:
                logger.warning(f"      [{tlabel}] {col} 列缺失 (该轨未产出, 优雅降级)")

        # ── 指标②: negonly 消融变体与全规则的相关性 (主结果对程度/转折规则的敏感性) ──
        # 判读: corr(full规则, negonly) 越接近 1 → 主结果对去掉程度/转折越不敏感 (越稳健)。
        # 参考文档: 全量 T=18/bank-year 聚合参照 corr ≈ 0.998–0.999 高度共线 (稳健性对照, 非独立信号);
        #           T=2 盘面样本小, 实测 r 会偏低 (与 verdict 文案口径一致, 见 ~line 1944)。
        logger.info("  · 指标② 规则消融稳健性 corr(msent_score, msent_negonly) — 仅否定 vs 全规则:")
        for track, tlabel in [('_full', '全文'), ('_ctx', '上下文片段'), ('_ss', '银行+金科同句')]:
            full_col, neg_col = f"msent_score{track}", f"msent_negonly{track}"
            if full_col in processed_df.columns and neg_col in processed_df.columns:
                a = pd.to_numeric(processed_df[full_col], errors='coerce')
                b = pd.to_numeric(processed_df[neg_col], errors='coerce')
                paired = pd.concat([a, b], axis=1).dropna()
                if len(paired) >= 3 and paired.iloc[:, 0].std() > 0 and paired.iloc[:, 1].std() > 0:
                    r = float(paired.iloc[:, 0].corr(paired.iloc[:, 1]))
                    verdict = ("稳健 (r≥0.95, 主结果不依赖程度/转折两规则; 全量 T=18/bank-year 聚合参照≈0.998-0.999, T=2 盘面更低)"
                               if r >= 0.95 else
                               "中等 (程度/转折规则贡献可观, 须在稳健性表披露)"
                               if r >= 0.7 else "偏低 (规则贡献大, 需进一步核查)")
                    logger.info(f"      [{tlabel}] r={sig4(r)} → {verdict} (n={len(paired):,})")
                else:
                    logger.info(f"      [{tlabel}] 样本/方差不足 (n={len(paired):,}), 相关性不可计算 (T=2 盘面常见)")

        # ── 指标③: Z-score 列的退化情况 (σ=0 常数列 → 整列 NaN 哨兵) ──
        # 判读: 退化列越多 → 该轨/词典区分度越差 (小样本 T=2 下高发, 仅验证管道正确性)。
        zcols = [c for c in processed_df.columns
                 if (c.endswith('_zscore_full') or c.endswith('_zscore_ctx') or c.endswith('_zscore_ss'))]
        if zcols:
            n_degraded = sum(1 for c in zcols if pd.to_numeric(processed_df[c], errors='coerce').notna().sum() == 0)
            logger.info(f"  · 指标③ Z-score 标准化列: 共 {len(zcols)} 列, "
                        f"其中退化(全 NaN, σ=0 常数列)={n_degraded} 列")
            if n_degraded > 0:
                logger.warning(f"      ⚠ {n_degraded} 个 Z-score 列退化为全 NaN (σ=0): "
                               f"该词典×轨在本样本无区分度; T=2 小样本下常见, 全量 T=18 应大幅缓解")

        # ── 指标④: num_intensity 三轨 (数值披露强度, Davis & Tama-Sweet 2012 CAR) ──
        # 判读: num_intensity = 数字 token 数 / 句数, 是按句数归一化的**密度** (非原始计数)。
        # 密度高低取决于各窗口内句子相对全文均值的数字密集度, **不存在 full≥ctx≥ss 单调律**
        # (单调性只对原始计数成立; 密度可任意大小)。故偶发不满足 full≥ctx≥ss 非指标异常。
        ni_present = [t for t in ('full', 'ctx', 'ss') if f"num_intensity_{t}" in processed_df.columns]
        if ni_present:
            ni_msg = []
            for t in ni_present:
                s = pd.to_numeric(processed_df[f"num_intensity_{t}"], errors='coerce')
                ni_msg.append(f"{t}={sig4(s.mean())}" if s.notna().any() else f"{t}=NaN")
            logger.info(f"  · 指标④ num_intensity 数值披露强度均值 (三轨): {', '.join(ni_msg)} "
                        f"(注: 为按句数归一化的密度=数字token数/句数, 非原始计数; 三轨高低取决于"
                        f"各窗口内句子相对全文的数字密集度, 不必然单调 full≥ctx≥ss)")
        else:
            logger.warning("  · 指标④ num_intensity 三轨列缺失 (numerical_intensity enrich 已优雅跳过, 见上方告警)")

        # ── 指标⑤: IDF 加权轨道存活情况 (稳健性度量是否落盘) ──
        if idf_enabled and IDF_DICTIONARIES is not None:
            n_idf_cols = sum(1 for c in processed_df.columns if '_idf_score_' in c or '_idf_zscore_' in c)
            logger.info(f"  · 指标⑤ IDF 加权稳健性轨: 已构建 {len(IDF_DICTIONARIES)} 部加权词典, "
                        f"落盘 {n_idf_cols} 个 idf_score/zscore 列 (Gentzkow et al. 2019 JEL §2.2)")
        else:
            logger.info("  · 指标⑤ IDF 加权轨: 未启用 (idf_weighting=false) — 仅 raw 词频, 不影响主轨")

        # ── 三轨分类标签分布 (来自 merged_stats; 负面占比 >60% 提示负面偏差) ──
        if all_stats:
            logger.info("  · 指标⑥ 三轨分类标签分布 (负面占比 >60% 提示词典负面偏差, 详表见上方分类报告):")
            _ms = merge_stats(all_stats)
            _tot = _ms.get('total', 0)
            for track, tlabel in [('_full', '全文'), ('_ctx', '上下文片段'), ('_ss', '银行+金科同句')]:
                neg_sum = sum(_ms.get(f'{dn}_负面{track}', 0) for dn, _ in ALL_DICTIONARIES)
                pos_sum = sum(_ms.get(f'{dn}_正面{track}', 0) for dn, _ in ALL_DICTIONARIES)
                base = _tot * len(ALL_DICTIONARIES)
                if base > 0:
                    neg_pct = neg_sum / base * 100
                    pos_pct = pos_sum / base * 100
                    flag = " ⚠ 负面偏差(>60%)" if neg_pct > 60 else ""
                    logger.info(f"      [{tlabel}] 跨六词典聚合: 正面={pct4(pos_pct, fraction=False)}, "
                                f"负面={pct4(neg_pct, fraction=False)}{flag}")

        # ── 指标⑦: 跨类重叠词「两侧计数」概况 (用户决策 2026-06-24, 逆转旧双侧剔除) ──
        # 判读: 每部词典 positive∩negative 同时出现的词被保留, 打分时两侧计入 → 净语调
        # 拉向中性 (不武断选边)。union/msent/ratio 因 (+1,−1) 平衡双票 margin 守恒, 逐位不变;
        # 仅影响各词典个体 {dict}_score。下列逐词典披露重叠词数, 供审阅与论文附录如实记载。
        if _BOTH_SIDED_BY_DICT:
            _both_total = sum(len(s) for s in _BOTH_SIDED_BY_DICT.values())
            _per = ", ".join(f"{dn}={len(s)}" for dn, s in _BOTH_SIDED_BY_DICT.items())
            logger.info(f"  · 指标⑦ 跨类重叠词保留并两侧计数: 共 {_both_total} 词 "
                        f"(分布 {len(_BOTH_SIDED_BY_DICT)} 部词典: {_per})")
            logger.info(f"      口径: pos_count 与 neg_count 各 +1, 分子净 0、分母 +2|w| → 拉向中性; "
                        f"union/msent/ratio 不变 (平衡双票 margin 守恒)")
        else:
            logger.info("  · 指标⑦ 跨类重叠词: 本次加载无 positive∩negative 重叠 (或词典为空)")

        # ── 指标⑧: 产物列族盘点 (运行结果信息 — 各家族落盘列数, 便于核对 schema 完整性) ──
        _cols = list(processed_df.columns)
        _fam = {
            'score(主分)': sum(1 for c in _cols if c.endswith(('_score_full', '_score_ctx', '_score_ss'))),
            'zscore': sum(1 for c in _cols if '_zscore_' in c),
            'idf_score': sum(1 for c in _cols if '_idf_score_' in c),
            '规则消融梯度': sum(1 for c in _cols for sfx in RULE_ABLATION_SUFFIXES if f'_score_{sfx}_' in c),
            'pos/neg_ratio': sum(1 for c in _cols if '_pos_ratio_' in c or '_neg_ratio_' in c),
            'msent': sum(1 for c in _cols if c.startswith('msent_')),
            'clarity': sum(1 for c in _cols if c.startswith('clarity_')),
            'num_intensity': sum(1 for c in _cols if c.startswith('num_intensity_')),
        }
        logger.info(f"  · 指标⑧ 产物列族盘点 (总列数 {len(_cols):,}): "
                    + ", ".join(f"{k}={v}" for k, v in _fam.items()))

        # ── 小样本 / 确定性提示 ──
        if input_rows < 1000:
            logger.info(f"  ⚠ 小样本 ({input_rows:,} 行, 疑似 T=2 盘面): 上述判读仅验证管道正确性, "
                        f"全量结论以 17M/T=18 实测为准")
        logger.info("  ✓ 确定性: 纯 CPU, 无 LLM/网络/API ($0); 同 jieba==0.42.1 + 同词典文件 → 逐位可复现")
        logger.info("-" * 72)
    except Exception as e:  # noqa: BLE001
        # 结果分析纯属日志增强, 任何异常都不得影响产物落盘 (已在上方完成写盘)。
        logger.warning(f"【结果分析】诊断日志生成失败 (不影响产物, 已写盘): {e}")

    # ── 运行期阶段计时汇总 (各主要阶段墙钟耗时占比, 便于性能定位) ──
    try:
        if phase_durations:
            _tot = sum(phase_durations.values()) or 1.0
            logger.info("⏱ 运行期阶段计时 (墙钟):")
            for _name, _dur in phase_durations.items():
                logger.info(f"     {_name}: {sig4(_dur)}s ({pct4(_dur / _tot)})")
    except Exception as e:  # noqa: BLE001
        logger.warning(f"阶段计时汇总打印失败 (不影响产物): {e}")

    log_stage_summary(logger, STAGE_NAME, stage_start,
                      input_rows=input_rows, output_rows=len(processed_df))
    logger.info(f"--- 阶段执行完毕: {STAGE_NAME} (三轨模式 full/ctx/ss) ---")


if __name__ == "__main__":
    main()
