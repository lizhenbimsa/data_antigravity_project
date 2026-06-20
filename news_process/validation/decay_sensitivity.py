"""
news_process.validation.decay_sensitivity — 距离衰减权重敏感性检验 (G-14)

v3.6.0 (Plan E P7 C4 stub):
    当前单轨实现. 多轨稳健性应对 full / ctx / ss 各跑一遍 3 种 decay 函数,
    输出 Pearson/Spearman 相关度矩阵 (3 decay × 3 track = 9×9 matrix).
    多轨实施 (full/ctx/ss 各跑 3 decay → 9×9 相关矩阵) 推迟到 P7.b 单独 PR (TODO)。
    注(三轨, 2026-06-14): 本模块是 track-agnostic 的距离衰减权重族扫描 (只动句级
    距离权重函数, 读原始 `内容` 全文 body, 不切换 LLM 情感轨), 故 _ss 第三轨同 _ctx
    一样落入此 TODO; 本轮三轨化无需改本模块逻辑, 仅同步术语 双轨→多轨。
    当前模块不阻塞 Plan E 主线; 推迟到 P7.b 单独 PR 实施。

迁移说明 (Phase 7b)：
    本模块由原 root script ``38b_decay_sensitivity.py`` body 迁入。
    规范调用方式: ``python -m news_process.validation.decay_sensitivity``

=======================================================

功能：
    比较均匀权重 vs 距离衰减权重对词典法情感得分的影响。
    验证词典情感得分在衰减权重族内 (radius=2) 是否稳健。

设计定位：
    稳健性变体 — 不替换现有 full/ctx/ss 三轨设计，
    仅作为论文 Appendix 的一行结论。

与生产主测度的口径差异 (fix(omni-g-val-robust-04, 2026-06-11) 披露):
    本检验的 uniform 列 **不是** 生产 ctx 测度的数值锚点, 存在三重口径差异:
      1. 窗口半径: 本模块 sentence_radius=2, 生产 ctx 轨 = 1
         (config/filtering.yaml: sentence_radius);
      2. 估计量: 本模块 = 句级归一化 tone 的加权平均 (mean-of-ratios),
         生产 22_tone_words = 整窗 token 池化 score/(pos+neg) (ratio-of-sums) —
         1 个命中词的句与 10 个命中词的句在前者等权、后者按命中数加权,
         数学上非同一估计量;
      3. 输入文本: 本模块读原始 `内容` 列, 生产三轨 (full/ctx/ss) 自 v3.8.0 起读
         prepend_title 注入标题后的文本。
    因此本检验的结论只支持 "词典得分在 radius=2 的衰减权重族内稳健",
    不可直接表述为 "主结果对权重方案不敏感"。

衰减函数 (3 种固定形式，不做超参搜索):
    1. uniform:     w(d) = 1          (族内等权基准 — 非生产 ctx 口径, 见上方披露)
    2. inverse:     w(d) = 1/(1+d)    (倒数衰减 — 调和递减)
    3. exponential: w(d) = exp(-0.5d)  (指数衰减 — 半生命期 ≈ 1.4 句)

    设计思路:
      - 固定 3 种函数形式避免超参搜索带来的"研究者自由度"问题
        (Simmons, Nelson & Simonsohn, 2011, Psychological Science)
      - 指数衰减的 λ=0.5 选取依据: 使 d=1 时权重为 ~0.61 (保留 >50%),
        d=3 时权重为 ~0.22 (快速衰减), 在 sentence_radius=2 的窗口下
        提供足够对比度但不至于使远程句子权重趋零

学术依据:
    Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023).
      Firm-level climate change exposure.
      The Journal of Finance, 78(3), 1449-1498.
      https://doi.org/10.1111/jofi.13219
      — §2.2: "We weight each bigram token by its inverse distance to
        the nearest climate change keyword."
      本模块将 Sautner 的 token 级距离衰减适配为句级距离衰减,
      以与管道的实体特异性上下文提取 (entity_context.py) 保持一致。

    Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019).
      Firm-level political risk: Measurement and effects.
      The Quarterly Journal of Economics, 134(4), 2135-2202.
      https://doi.org/10.1093/qje/qjz021
      — proximity-based attribution 方法论框架:
        "We identify the relevant text surrounding each keyword hit
         and assign sentiment based on the local context."

    Loughran, T., & McDonald, B. (2016).
      Textual analysis in accounting and finance: A survey.
      Journal of Accounting Research, 54(4), 1187-1230.
      https://doi.org/10.1111/1475-679X.12123
      — §3: 讨论了加权方案对文本度量稳健性的影响

输入：
    阶段21 输出 (含 target_bank 和内容列)

输出：
    1. 衰减 vs 均匀权重的 Pearson/Spearman 相关性报告
    2. eval_reports/38b_decay_sensitivity.csv

白话:
    计算情感分时, 离银行名字越远的句子是否应该"打折"计入? 本检验把
    "不打折 / 按距离倒数打折 / 按指数打折" 三种方案各算一遍情感分,
    再看三套分数的相关性。相关性很高 (≥0.9) 就说明打折方式怎么选都
    不影响结论, 论文附录交代一句即可。注意: 这里的"不打折"版本和生产
    主指标在窗口大小、算法、输入文本上都有差别, 所以只能说"打折方式
    不敏感", 不能说"主结果不敏感"。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 38b_decay_sensitivity.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**核心问题**: 计算情感时, 离银行名越远的句子是否该按距离'打折'计权? 本阶段比较 3 种距离衰减权重方案下词典情感得分的相关性。

**输入**: `21_tone_llms_full.parquet` (CONFIG['filenames']['output_21_tone_llms_full'], 回退 glob `21_*.parquet` 取字典序末位)。过滤 `llm_verified_full == True` 仅保留已验证的金科新闻。

**处理步骤**:
1. 加载 6 套词典 (jiang/yao/bian/du/you/loughran; 正面+1/负面-1/政治正面+0.5; positive∩negative 跨类重叠双侧剔除) + 注入 jieba (与 stage 35 词典集一致; 语言学规则参数与 22_tone_words 一致)。2026-06-20 起本模块已对齐生产 22_tone_words 的 6 词典 union 口径 (含第 6 部 loughran)。
2. `run_analysis` 逐文: `core.text.entity_context.extract_entity_context_with_distances(content, aliases, sentence_radius=2)` 提取 [(句文本, 句级距离 d), ...] (radius=2 大于生产 ctx 的 1, 给衰减留空间); 每句 jieba 分词一次 (3 衰减函数共享预分词)。
3. 对 6 词典 × 3 衰减函数 = 18 组合调 `compute_decay_sentiment`。

**关键算法/公式**: 衰减函数 (3 种固定形式, 不做超参搜索以避免研究者自由度, DECAY_FUNCTIONS): uniform w(d)=1 / inverse w(d)=1/(1+d) / exponential w(d)=exp(−0.5d)。距离加权得分 = Σ w(d_s)·tone(s) / Σ w(d_s), 其中 tone(s)=单句归一化得分 (`_sentence_tone`, 否定/转折/程度三规则状态机, 与 22_tone_words 对齐)。`log_correlation_report` 算 uniform vs inverse/exponential 的 Pearson/Spearman + 均值差; 两类守卫行为相反: 缺列 / 有效样本 n<10 → 直接剔除 (不入表, 令对数减少); 零方差 / 异常 → 置 0.0 sentinel 但仍入表 (注: 与 35 选 NaN 路线不同, 这里是 0.0 sentinel)。判定: min Pearson≥0.95 高度不敏感 / ≥0.90 基本不敏感 / <0.90 正文讨论。

**重要口径披露 (fix omni-g-val-robust-04)**: uniform 列**不是**生产 ctx 测度的数值锚点 — 三重差异: ①半径 2 vs 生产 1 ②估计量 mean-of-ratios vs 生产 ratio-of-sums ③读原始 `内容` vs 生产读 prepend_title 文本。故结论只能表述为'词典得分在 radius=2 衰减权重族内稳健', 不可说'主结果对权重不敏感'。

**外部依赖**: jieba (必需, 缺则 raise); scipy.stats。无 LLM/缓存/timeout。确定性: 纯词典+确定提取, 全确定。

**学术依据**: Sautner et al. (2023, JF §2.2) 倒数距离衰减; Hassan et al. (2019, QJE) proximity attribution; Loughran & McDonald (2016, JAR) 加权方案稳健性; Simmons et al. (2011) 研究者自由度。

■ 白话说明

**这一步在做什么**: 给一篇新闻算银行情感分时, 银行名字所在那句话和离它三句远的句子, 该不该一视同仁? 直觉上越近越相关。这一步用三种打折方式各算一遍: '不打折'(远近句子一样重)、'按距离倒数打折'、'按指数打折', 再看三套分数的相关性高不高。

**为什么需要它**: '远的句子要不要打折、打多少折'又是一个人为选择, 审稿人会问。如果三种打折方式算出的分数高度相关 (≥0.9), 说明怎么打折都不影响结论, 论文附录交代一句即可。模块特别老实地标注了一点: 这里的'不打折'版本和论文真正用的主指标在窗口大小、算法、是否含标题上都有差别, 所以只能说'打折方式不敏感', 不能偷换成'主结果不敏感'。

**对面板和论文的影响**: 它是情感测量的又一道稳健性检查, 确保银行-年度面板里的语调变量不是靠某种'巧妙的加权技巧'凑出来的。做得好, 论文能多一条'我们对句子加权方案做了敏感性分析'的方法论背书; 做得草率或夸大口径, 反而会被审稿人抓住'过度声称'的把柄。
========================================================================
"""

import json
import logging
import math
import os
import sys
import time

import numpy as np
import pandas as pd

# Phase 7b: 注入项目父目录, 让 ``news_process.core.*`` 在任意 cwd 解析
# (从 news_process/validation/decay_sensitivity.py 出发, 上溯 2 层抵达项目父目录)
_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config
from news_process.core.logging import log_stage_summary, setup_logging
from news_process.core.text.entity_context import (
    extract_entity_context_with_distances,
    get_target_aliases,
)

try:
    import jieba
    jieba.setLogLevel(logging.WARNING)
except ImportError:
    raise ImportError("请安装 jieba: pip install jieba")

# ============================================================================
# 1. 全局配置
# ============================================================================
# 设计说明:
#   CONFIG 为全局单例, 在模块加载时执行一次 load_config()。
#   所有路径通过 CONFIG['paths'] 获取, 确保与管道其他模块路径一致。
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "38b_decay_sensitivity"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

OUTPUT_DIR = CONFIG["paths"]["output_dir"]
EVAL_DIR = os.path.join(OUTPUT_DIR, 'eval_reports')
os.makedirs(EVAL_DIR, exist_ok=True)

# ── 词典情感参数 (复用 22_tone_words 配置) ──
# 确保与 22_tone_words.py 使用完全相同的语言学规则参数:
#   - 否定词集合、否定窗口大小
#   - 程度副词映射及权重
#   - 转折连词集合及提升倍数
#   - 句末标点集合 (状态重置边界)
#
# 学术依据:
#   否定词: Jia, Yu & Meng (2009, CIKM), DOI: 10.1145/1645953.1646241
#   程度副词: Li, Huang & Zhu (2010, AAAI), DOI: 10.1609/aaai.v24i1.7523
#   转折连词: Ding, Liu & Yu (2008, WSDM), DOI: 10.1145/1341531.1341561
# ============================================================================
SENTIMENT_PARAMS = CONFIG.get('sentiment_analysis', {}).get('tone_words', {})

# 否定词集合 (frozenset: 不可变 + O(1) 查找)
# 遇到否定词时, 将其后 NEGATION_WINDOW 个分词单元内的情感词极性翻转
NEGATION_WORDS = frozenset(SENTIMENT_PARAMS.get('negation_words', []))

# 程度副词映射 {word: multiplier}
# 权重含义: >1 程度加强, <1 程度减弱
# 显式类型转换确保 YAML 解析后值为 float (YAML 可能将 "2.0" 解析为 int 2)
DEGREE_WORDS = {
    str(k): float(v)
    for k, v in SENTIMENT_PARAMS.get('degree_words', {}).items()
}

# 转折连词集合
# 转折后的内容更能反映作者真实立场 ("末尾效应")
# Ding, Liu & Yu (2008, WSDM): 转折效应作用域为从句级别
ADVERSATIVE_WORDS = frozenset(SENTIMENT_PARAMS.get('adversative_words', []))

# 转折后权重提升倍数 (默认 1.5x)
ADVERSATIVE_BOOST = float(SENTIMENT_PARAMS.get('adversative_boost', 1.5))

# 否定词有效作用窗口 (向后影响的分词单元数)
# 设为 2: 覆盖 "不 [程度副词] 情感词" 结构 (如 "不太 乐观")
NEGATION_WINDOW = SENTIMENT_PARAMS.get('negation_window', 2)

# 句末标点集合 (句法边界标记)
# 遇到句末标点时重置转折/否定/程度状态, 确保作用域限定为当前句
# 学术依据: Ding, Liu & Yu (2008, WSDM) — 转折效应限定为从句级 (Clause-level)
# 注意: 不包含逗号(，)和顿号(、) — 它们连接同一复句内的从句, 转折效应理应跨越
SENTENCE_END_MARKERS = frozenset(
    SENTIMENT_PARAMS.get('sentence_end_markers', ['。', '！', '？', '!', '?', '；', ';'])
)

# 词典文件路径
TONE_DICTS_FILE = CONFIG['paths'].get(
    'tone_dicts_file',
    os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config', 'tone_dicts.json')
)


# ============================================================================
# 2. 衰减函数
# ============================================================================
# 三种固定形式的距离衰减函数, 映射 句级距离 d ∈ {0,1,2,...} → 权重 w ∈ (0,1]。
#
# 数学性质:
#   ┌─────────────┬─────────────┬──────────┬──────────┬──────────┐
#   │ 函数        │ 公式        │ w(0)     │ w(1)     │ w(2)     │
#   ├─────────────┼─────────────┼──────────┼──────────┼──────────┤
#   │ uniform     │ 1           │ 1.000    │ 1.000    │ 1.000    │
#   │ inverse     │ 1/(1+d)     │ 1.000    │ 0.500    │ 0.333    │
#   │ exponential │ exp(-0.5d)  │ 1.000    │ 0.607    │ 0.368    │
#   └─────────────┴─────────────┴──────────┴──────────┴──────────┘
#
# 设计考量:
#   - 所有函数在 d=0 时权重 = 1.0 (命中句本身获得最大权重)
#   - uniform 作为族内基准 (fix(omni-g-val-robust-04, 2026-06-11): 非生产主测度
#     数值锚点 — 窗口/估计量/输入文本三重口径差异见模块 docstring 披露),
#     inverse 和 exponential 作为对比
#   - inverse 衰减较快 (调和级数), exponential 衰减适中
#   - lambda 参数使用 closure, 无运行时开销
#
# 学术依据:
#   Sautner et al. (2023, JF §2.2) 使用倒数衰减 1/(1+d)
#   本模块额外加入指数衰减作为交叉验证
# ============================================================================

DECAY_FUNCTIONS = {
    'uniform':     lambda d: 1.0,
    'inverse':     lambda d: 1.0 / (1.0 + d),
    'exponential': lambda d: math.exp(-0.5 * d),
}


# ============================================================================
# 3. 词典加载
# ============================================================================

# 列前缀别名: loughran_mcdonald_zh_2026 → 'loughran' (镜像生产 tone_words.DICT_COLUMN_ALIAS;
# 此处本地复制以避免 import 22_tone_words 触发模块级副作用)。
_DICT_COLUMN_ALIAS = {'loughran_mcdonald_zh_2026': 'loughran'}


def load_dictionaries() -> list:
    """从 tone_dicts.json 加载与 22_tone_words 完全一致的 6 套中文金融情感词典。

    加载与 22_tone_words.py 共有的 6 套中文情感词典 (jiang/yao/bian/du/you/loughran)。2026-06-20 起本验证模块已对齐生产 union 口径: 含第 6 部 loughran_mcdonald_zh_2026 + positive∩negative 跨类重叠词双侧剔除 (LM 2011 惯例), 不再是早期刻意保留的 5 套子集:
      1. jiang_2021 — 姜富伟等 (2021) 中文金融情感词典
      2. yao_2021  — 姚加权等 (2021) 金融领域情绪词典
      3. bian_2021 — Bian et al. (2021) LM 中文扩充版
      4. du_2022   — Du et al. (2022) 含政治正面词扩充
      5. you_2018  — You et al. (2018) 中文金融情感词典
      6. loughran  — Loughran-McDonald (2011 JF) 中文主译全本 (列前缀别名 'loughran')

    词典结构: {word: score}
      - 正面词: score = +1.0
      - 负面词: score = -1.0
      - 政治正面词 (du_2022 特有): score = +0.5

    Returns:
        list[tuple[str, dict]]: [(dict_name, {word: score}), ...] (dict_name 经别名映射)

    Raises:
        无 — 词典文件不存在时返回空词典列表, 并记录警告日志。
    """
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
        except json.JSONDecodeError as e:
            logger.error(f"词典文件 JSON 解析失败: {e}")
        except Exception as e:
            logger.error(f"加载 {TONE_DICTS_FILE} 失败: {e}")
    else:
        logger.warning(f"词典文件未找到: {TONE_DICTS_FILE}")

    dictionaries = []
    for key in ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018',
                'loughran_mcdonald_zh_2026']:
        entry = all_dict_data.get(key, {})
        d = {}
        # positive∩negative 跨类重叠词双侧剔除 (LM 2011 惯例), 与生产 22_tone_words 一致;
        # sorted 保证 dict 插入序确定 (可复现性)。
        pos_words = {str(w).strip() for w in entry.get('positive', []) if str(w).strip()}
        neg_words = {str(w).strip() for w in entry.get('negative', []) if str(w).strip()}
        cross_overlap = pos_words & neg_words
        if cross_overlap:
            logger.warning(
                f"  {key}: positive∩negative 跨类重叠 {len(cross_overlap)} 词已双侧剔除 "
                f"(LM 2011 惯例): {sorted(cross_overlap)}")
        for w in sorted(pos_words - cross_overlap):
            d[w] = 1.0
        for w in sorted(neg_words - cross_overlap):
            d[w] = -1.0
        # 政治正面词 → +0.5 (仅 du_2022, 不覆盖已有正面/负面词)
        for w in entry.get('political_positive', []):
            w = str(w).strip()
            if w and w not in d:
                d[w] = 0.5
        dictionaries.append((_DICT_COLUMN_ALIAS.get(key, key), d))
        logger.info(f"  {key}: {len(d)} 词")

    return dictionaries


def _inject_custom_dicts_to_jieba(dictionaries: list) -> None:
    """将所有领域词汇注入 jieba 分词器, 防止专业词汇被切碎。

    注入范围与 22_tone_words.py / 35_radius_sensitivity.py 保持一致:
      1. 所有情感词典中的词汇
      2. 银行名称词典 (bank_names.json)
      3. 金融科技词典 (fintech_dict.json)
      4. 语言学规则词汇 (否定词、程度词、转折词)

    设计说明:
      jieba 在分词时优先使用用户词典中的词条。如果不注入, 多字情感词
      (如 "严重关切") 可能被切分为 "严重" + "关切", 导致:
        - 情感词命中率下降
        - 与 22_tone_words 的分词结果不一致
        - 距离衰减权重计算偏差

    Args:
        dictionaries: 词典列表 [(name, {word: score}), ...]
    """
    added = 0

    # 1. 注入情感词典词汇
    for _, sdict in dictionaries:
        for w in sdict:
            jieba.add_word(w)
            added += 1

    # 2. 注入银行名称词典
    bank_path = CONFIG['paths'].get('bank_names_file', '')
    if bank_path and os.path.exists(bank_path):
        try:
            with open(bank_path, 'r', encoding='utf-8') as f:
                bank_data = json.load(f)
            for bank in bank_data:
                if not isinstance(bank, dict):
                    continue
                # 使用 bank_name 字段 (与 entity_context.py 的 get_target_aliases 一致)
                std_name = bank.get('bank_name')
                if std_name:
                    jieba.add_word(str(std_name).strip())
                    added += 1
                for v in bank.get('variants', []):
                    if v:
                        jieba.add_word(str(v).strip())
                        added += 1
        except Exception as e:
            logger.warning(f"加载银行名称词典失败: {e}")

    # 3. 注入金融科技词典
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

    # 4. 注入语言学规则词汇 (否定词、程度词、转折词)
    for word in NEGATION_WORDS:
        jieba.add_word(word)
    for word in DEGREE_WORDS:
        jieba.add_word(word)
    for word in ADVERSATIVE_WORDS:
        jieba.add_word(word)

    logger.info(f"成功注入 {added} 个领域词汇到 jieba 分词器。")


# ============================================================================
# 4. 逐句词典情感计算
# ============================================================================
# 规则对齐: 与 22_tone_words.py 的 _compute_sentiment_with_rules() 完全一致,
# 包含否定词、转折词、程度词三重语言学规则。
#
# 状态机设计 (与 22_tone_words.py 逐行对齐):
#   遍历 token 序列, 维护三个状态变量:
#     ① negation_remaining: 否定窗口剩余 token 数 (>0 则极性翻转)
#     ② degree_multiplier:  当前程度副词倍率 (碰到情感词时消费并重置为 1.0)
#     ③ adversative_active:  是否处于转折后区域 (遇句末标点重置为 False)
#
#   状态转移规则 (优先级从高到低):
#     token ∈ SENTENCE_END_MARKERS → 重置全部状态 (句法边界)
#     token ∈ ADVERSATIVE_WORDS    → 激活转折, 重置否定和程度
#     token ∈ NEGATION_WORDS       → 设置否定窗口 = NEGATION_WINDOW
#     token ∈ DEGREE_WORDS         → 设置程度倍率
#     token ∈ sentiment_dict       → 计算 score = base × degree × negation × adversative
#     其他                          → 重置程度副词 (未被消费)
#
# 归一化:
#   score / matched_count (matched_count = 命中的情感词总数)
#   等价于 22_tone_words 的 score / (pos_count + neg_count)
#
# 学术依据:
#   Jia, Yu & Meng (2009, CIKM): 否定词极性翻转
#     DOI: 10.1145/1645953.1646241
#   Li, Huang & Zhu (2010, AAAI): 程度副词缩放
#     DOI: 10.1609/aaai.v24i1.7523
#   Ding, Liu & Yu (2008, WSDM): 转折连词增强
#     DOI: 10.1145/1341531.1341561
# ============================================================================

def _sentence_tone(tokens: list, sentiment_dict: dict) -> float:
    """计算单句的归一化情感得分。

    与 22_tone_words._compute_sentiment_with_rules() 对齐的三重规则:
      1. 否定词翻转 (negation_remaining 计数器, 窗口 = NEGATION_WINDOW)
      2. 转折词增强 (adversative_active 标志, 倍率 = ADVERSATIVE_BOOST)
      3. 程度词缩放 (degree_multiplier 乘数, 消费后重置为 1.0)

    Args:
        tokens: 分词后的 token 列表 (已过滤空白 token)。
        sentiment_dict: 情感词典, 格式为 {word: base_score}。

    Returns:
        float: 归一化情感得分。无命中时返回 0.0。

    Note:
        该函数处理的是**单个句子**的 token 序列, 而非全文。
        句子切分由上游 extract_entity_context_with_distances() 完成。
        因此 SENTENCE_END_MARKERS 在正常情况下不会出现在 tokens 中,
        但保留该逻辑以处理句子切分不完美的边缘情况。
    """
    score = 0.0
    matched = 0
    negation_remaining = 0
    degree_multiplier = 1.0
    adversative_active = False

    for token in tokens:
        # ── 句法边界: 句末标点重置全部句法级状态 ──
        # Ding et al. (2008): 转折效应限定为从句级 (Clause-level)
        if token in SENTENCE_END_MARKERS:
            adversative_active = False
            negation_remaining = 0
            degree_multiplier = 1.0
            continue

        # ── 转折连词: 激活转折增强, 重置其他状态 ──
        if token in ADVERSATIVE_WORDS:
            adversative_active = True
            degree_multiplier = 1.0
            negation_remaining = 0
            continue

        # ── 否定词: 设置否定窗口 ──
        if token in NEGATION_WORDS:
            negation_remaining = NEGATION_WINDOW
            continue

        # ── 程度副词: 设置程度倍率 (等待后续情感词消费) ──
        if token in DEGREE_WORDS:
            degree_multiplier = DEGREE_WORDS[token]
            continue

        # ── 情感词: 计算加权得分 ──
        if token in sentiment_dict:
            base = sentiment_dict[token]
            # 1. 应用否定词翻转
            if negation_remaining > 0:
                base = -base
            # 2. 应用程度副词缩放
            final = base * degree_multiplier
            # 3. 应用转折增强
            if adversative_active:
                final *= ADVERSATIVE_BOOST
            score += final
            matched += 1
            # 4. 消费程度副词 (重置为 1.0)
            degree_multiplier = 1.0
        else:
            # 非情感词: 程度副词未被消费, 重置
            degree_multiplier = 1.0

        # ── 否定窗口递减 (句末/转折/否定/程度词因 continue 不执行此行) ──
        if negation_remaining > 0:
            negation_remaining -= 1

    return score / matched if matched > 0 else 0.0


def compute_decay_sentiment(
    tokenized_sentences: list,
    sentiment_dict: dict,
    decay_func: callable,
) -> float:
    """距离加权词典情感得分。

    公式 (加权平均):
        Score = Σ_s w(d_s) · tone(s) / Σ_s w(d_s)

    其中:
        s = 窗口内的第 s 个句子
        d_s = 该句子到最近目标实体提及句的句级距离 (0 = 命中句本身)
        w(d_s) = 衰减函数 (uniform / inverse / exponential)
        tone(s) = 单句归一化情感得分 (由 _sentence_tone() 计算)

    该公式确保:
        - 距离越近的句子对最终得分贡献越大
        - uniform 衰减等价于句级简单平均 (族内基准;
          fix(omni-g-val-robust-04, 2026-06-11): 生产 22_tone_words 为整窗
          token 池化 ratio-of-sums, 与本式 mean-of-ratios 非同一估计量,
          勿当作 "当前管道默认" 的数值锚点 — 见模块 docstring 披露)
        - 分母 Σ w(d_s) 归一化, 使不同衰减函数的得分量级可比

    Args:
        tokenized_sentences: [(tokens_list, distance), ...]
            已预分词的句子列表, 每元素包含:
              - tokens_list: jieba 分词后的 token 列表 (已过滤空白)
              - distance: int, 到最近实体提及句的句级距离
        sentiment_dict: 情感词典 {word: base_score}
        decay_func: 衰减函数 w(d) -> float, d ∈ {0, 1, 2, ...}

    Returns:
        float: 距离加权归一化情感得分。
            无有效句子时返回 0.0。
    """
    if not tokenized_sentences:
        return 0.0

    weighted_sum = 0.0
    weight_total = 0.0

    for tokens, dist in tokenized_sentences:
        tone = _sentence_tone(tokens, sentiment_dict)
        w = decay_func(dist)
        weighted_sum += w * tone
        weight_total += w

    return weighted_sum / weight_total if weight_total > 0 else 0.0


# ============================================================================
# 5. 主分析
# ============================================================================

def run_analysis(df: pd.DataFrame, dictionaries: list) -> pd.DataFrame:
    """对全部文章计算 uniform/inverse/exponential 情感得分。

    算法流程:
      对每篇文章:
        1. 获取目标银行别名 (走缓存, 避免重复读盘)
        2. 调用 extract_entity_context_with_distances() 获取
           窗口内句子及其到最近实体的句级距离
        3. 对每个句子执行一次 jieba.cut() (预分词)
        4. 对 6 词典 × 3 衰减函数 = 18 个组合, 共享预分词结果
           调用 compute_decay_sentiment() 计算得分

    性能优化:
      - 每篇文章仅分词一次, 相同 tokens 在 3 种衰减函数间共享
      - 银行别名走 alias_cache 避免重复读盘
      - sentence_radius=2: 与 entity_context.py 的默认值一致,
        大于 ctx 轨道的 radius=1, 为衰减提供足够空间

    Args:
        df: 待分析的 DataFrame, 需含 'target_bank' 和 '内容' 列。
        dictionaries: 词典列表 [(name, {word: score}), ...]

    Returns:
        pd.DataFrame: 得分矩阵, 列名格式为 '{dict_name}_{decay_name}'。
    """
    bank_names_file = CONFIG['paths'].get('bank_names_file', '')
    alias_cache = {}
    dict_names = [name for name, _ in dictionaries]
    decay_names = list(DECAY_FUNCTIONS.keys())

    # 结果容器: {(dict_name, decay_name): [scores...]}
    results = {(dn, fn): [] for dn in dict_names for fn in decay_names}

    total = len(df)
    logger.info(f"开始处理 {total:,} 篇文章 × {len(dict_names)} 词典 × {len(decay_names)} 衰减函数")

    t0 = time.time()
    report_interval = max(1, total // 10)

    for i, (_, row) in enumerate(df.iterrows()):
        target_bank = str(row.get('target_bank', ''))
        content = str(row.get('内容', ''))

        # 空内容或无目标银行: 所有组合返回 0.0
        if not target_bank or not content.strip():
            for dn in dict_names:
                for fn in decay_names:
                    results[(dn, fn)].append(0.0)
            continue

        # 获取目标银行别名 (走缓存)
        if target_bank not in alias_cache:
            alias_cache[target_bank] = get_target_aliases(target_bank, bank_names_file)

        # 提取距离结构: [(sentence_text, distance), ...]
        # sentence_radius=2: 大于 ctx 轨道的 1, 为衰减函数提供足够对比度
        swd = extract_entity_context_with_distances(
            content, alias_cache[target_bank], sentence_radius=2
        )

        # 预分词 — 每个句子仅调用一次 jieba.cut()
        # 过滤空白 token (与 22_tone_words.py 的处理一致)
        tokenized_swd = [
            ([t for t in jieba.cut(sent_text) if t.strip()], dist)
            for sent_text, dist in swd
        ]

        # 计算各组合得分 (共享 tokenized_swd, 无额外分词开销)
        for dn, sdict in dictionaries:
            for fn, decay_func in DECAY_FUNCTIONS.items():
                score = compute_decay_sentiment(tokenized_swd, sdict, decay_func)
                results[(dn, fn)].append(round(score, 6))

        # 进度汇报 (每 10% 输出一次)
        if (i + 1) % report_interval == 0:
            elapsed = time.time() - t0
            logger.info(f"  进度: {i+1:,}/{total:,} ({(i+1)/total*100:.0f}%) "
                        f"| {(i+1)/elapsed:.0f} 篇/秒")

    elapsed = time.time() - t0
    logger.info(f"处理完成。耗时: {elapsed:.1f}s")

    # 转为 DataFrame: 列名格式 '{dict_name}_{decay_name}'
    score_df = pd.DataFrame()
    for dn in dict_names:
        for fn in decay_names:
            col = f'{dn}_{fn}'
            score_df[col] = results[(dn, fn)]

    return score_df


# ============================================================================
# 6. 报告
# ============================================================================

def log_correlation_report(score_df: pd.DataFrame, dict_names: list):
    """输出 uniform vs 各衰减函数的 Pearson/Spearman 相关性报告。

    报告设计:
      对每个词典, 计算 uniform 权重得分与 inverse/exponential 权重得分之间的:
        - Pearson 相关系数 (线性关联强度)
        - Spearman 秩相关系数 (单调关联强度, 对异常值稳健)
        - 均值差异 (方向性偏移)

    判定标准:
      - min Pearson ≥ 0.95 → 高度不敏感, Appendix 一句话说明即可
      - min Pearson ≥ 0.90 → 基本不敏感, Appendix 报告相关性表格
      - min Pearson < 0.90 → 有一定影响, 正文中讨论

    阈值学术依据:
      Kline, R. B. (2023). Principles and practice of structural equation
        modeling (5th ed.). Guilford Press, p. 76:
        "r ≥ .90 indicates excellent agreement between two measures."
      Cohen, J. (1988). Statistical power analysis for the behavioral sciences
        (2nd ed.). Lawrence Erlbaum Associates, pp. 79-80:
        "r ≥ .50 is 'large'; in practice, r ≥ .90 typically indicates
         near-interchangeability of two operationalizations."

    论文建议用语:
      当 min Pearson ≥ 0.90 时, 自动生成英文论文建议用语,
      引用 Sautner et al. (2023) 作为方法论依据。
      fix(omni-g-val-robust-04, 2026-06-11): 用语限定为衰减权重族内
      (within the decay-weighting family at radius 2) 的稳健性, 不声称
      "主结果对权重方案不敏感" — 口径差异见模块 docstring 披露。

    Args:
        score_df: 得分矩阵 (由 run_analysis() 生成)。
        dict_names: 词典名称列表。
    """
    from scipy import stats as sp_stats

    logger.info("=" * 70)
    logger.info("G-14: 距离衰减权重敏感性检验报告")
    logger.info("  对标学术框架:")
    logger.info("    Sautner, Z., van Lent, L., Vilkov, G. & Zhang, R. (2023).")
    logger.info("    Firm-Level Climate Change Exposure. JF, 78(3), 1449-1498.")
    logger.info("    DOI: 10.1111/jofi.13219, §2.2")
    logger.info("=" * 70)

    header = f"{'词典':<14} {'对比':<22} {'Pearson':>9} {'Spearman':>9} {'均值差':>9}"
    logger.info(header)
    logger.info("-" * 65)

    all_pearsons = []

    for dn in dict_names:
        uniform_col = f'{dn}_uniform'
        for fn in ['inverse', 'exponential']:
            decay_col = f'{dn}_{fn}'
            if uniform_col not in score_df.columns or decay_col not in score_df.columns:
                continue

            u = score_df[uniform_col].values
            d = score_df[decay_col].values

            # 过滤 NaN 值 (防御性编程)
            valid = ~(np.isnan(u) | np.isnan(d))
            u, d = u[valid], d[valid]

            # 样本量不足时跳过 (Pearson/Spearman 需要足够自由度)
            if len(u) < 10:
                logger.warning(f"  {dn} uniform vs {fn}: 有效样本 < 10, 跳过")
                continue
            
            # 零方差防御 (当序列为常数时，无法计算相关系数)
            if np.std(u) == 0 or np.std(d) == 0:
                logger.warning(f"  {dn} uniform vs {fn}: 数据存在零方差 (Constant Input), 无法计算相关性, 默认赋值为 0.0")
                pr, sr = 0.0, 0.0
            else:
                try:
                    pr, _ = sp_stats.pearsonr(u, d)
                    sr, _ = sp_stats.spearmanr(u, d)
                except Exception as e:
                    logger.warning(f"  {dn} 分布异常: {e}, 默认赋值 0.0")
                    pr, sr = 0.0, 0.0

            mean_diff = np.mean(d - u)
            all_pearsons.append(pr)

            logger.info(f"  {dn:<14} uniform vs {fn:<12} "
                        f"{pr:>8.4f}  {sr:>8.4f}  {mean_diff:>+8.5f}")

    logger.info("-" * 65)

    if all_pearsons:
        avg_pr = np.mean(all_pearsons)
        min_pr = min(all_pearsons)
        logger.info(f"  平均 Pearson = {avg_pr:.4f}, 最低 = {min_pr:.4f}")

        # 稳健性判定 (三级阈值体系)
        # fix(omni-g-val-robust-04, 2026-06-11): 结论措辞限定为 "衰减权重族内
        # (radius=2)" — uniform 列与生产 ctx 测度有三重口径差 (窗口半径 2 vs 1 /
        # mean-of-ratios vs ratio-of-sums / 无标题 prepend), 高相关只证明衰减
        # 权重内部稳健, 不直接证明 "主结果" 对权重不敏感。详见模块 docstring。
        if min_pr >= 0.95:
            logger.info("  ✅ 结论: 词典得分在衰减权重族内 (radius=2) 高度不敏感 (min r ≥ 0.95)")
            logger.info("  → 论文建议: 一句话在 Appendix 中说明即可 (限定族内稳健口径)")
        elif min_pr >= 0.90:
            logger.info("  ✓ 结论: 词典得分在衰减权重族内 (radius=2) 基本不敏感 (min r ≥ 0.90)")
            logger.info("  → 论文建议: Appendix 中报告相关性表格 (限定族内稳健口径)")
        else:
            logger.info("  结论: 衰减权重在族内有一定影响 (min r < 0.90)")
            logger.info("  → 论文建议: 在正文中讨论衰减函数的影响")

        # 论文建议用语 (英文, 供直接复制到论文中)
        logger.info("")
        logger.info("  ── 论文建议用语 ──")
        if min_pr >= 0.90:
            # fix(omni-g-val-robust-04, 2026-06-11): 不再生成 "confirming that our
            # main results are insensitive to the weighting scheme" 的过度声称,
            # 改为限定 within-family + 显式披露与生产测度的口径差异。
            logger.info('  "As a robustness check, we implement Sautner et al. (2023)-style')
            logger.info('   distance decay weighting over sentence windows of radius 2.')
            logger.info('   The Pearson correlation between uniform and decay-weighted')
            logger.info(f'   dictionary sentiment exceeds {min_pr:.2f} across all six')
            logger.info('   dictionaries, indicating that dictionary sentiment is insensitive')
            logger.info('   to the choice of distance-decay weights within this family.')
            logger.info('   This exercise uses sentence-level normalized scores at radius 2')
            logger.info('   and is not numerically anchored to the production')
            logger.info('   context-window measure."')
    else:
        logger.warning("  未能计算任何相关系数 (可能数据量不足)")

    # ── 结果分析 — 写入日志: 逐个产出指标 + 阈值判读 (仿 39c) ──
    # 全部为日志专用局部变量, 不回写 score_df / 不改写盘内容 (golden-safe)。
    # crash-guard: 本块在 main() 中早于 CSV 写盘 (步骤 6 < 步骤 7) 执行, 任何异常
    # (空 Series.min / np.mean(NaN) 等) 都必须被吞掉, 否则会带走整阶段产物 → 证伪
    # golden-safe; 故整块包 try/except, 失败仅 warning, 不影响 to_csv。
    try:
        n_obs = len(score_df)
        # NaN-guard: all_pearsons 理论上仅含有限 0.0 或 pearsonr 结果, 但仍剔除
        # 任何 NaN/inf, 防止 np.mean/min/max 被 NaN 污染、方向 ternary 因 NaN 比较
        # 恒 False 而落到错误档位。
        finite_pearsons = [float(p) for p in all_pearsons if np.isfinite(p)]
        n_nonfinite = len(all_pearsons) - len(finite_pearsons)
        n_pairs = len(finite_pearsons)  # 算成且有限的 uniform-vs-衰减对数 (满编 = 6 词典 × 2 衰减 = 12)
        expected_pairs = len(dict_names) * 2  # inverse + exponential 两对/词典
        logger.info("-" * 72)
        logger.info("【结果分析】距离衰减权重敏感性 (uniform vs inverse/exponential; Pearson 越接近 1 = 越不敏感):")
        if finite_pearsons:
            avg_pr_a = float(np.mean(finite_pearsons))
            min_pr_a = float(min(finite_pearsons))
            max_pr_a = float(max(finite_pearsons))
            # 通过率: min Pearson 三级阈值体系 (Kline 2023 p.76 r≥.90 / Cohen 1988 r≥.50)
            n_ge95 = sum(1 for p in finite_pearsons if p >= 0.95)
            n_ge90 = sum(1 for p in finite_pearsons if p >= 0.90)
            # 注: 两类行为相反, 须分开说 — (1) 缺列 / 有效样本 n<10 → continue 直接
            # 剔除, 不入 all_pearsons, 令 n_pairs 减少 (= 缺口, 不进 mean/min);
            # (2) 零方差 / pearsonr 异常 → pr 置 0.0 但仍 append 入表, 故计入 n_pairs
            # 并被 mean/min 拉低。切勿把"剔除致缺口"与"置 0.0 仍计入"混为同一档。
            n_gap = expected_pairs - n_pairs - n_nonfinite  # 被剔除致缺口的对数 (近似)
            logger.info(
                f"  完成相关对 {n_pairs}/{expected_pairs} (满编 = {len(dict_names)} 词典 × 2 衰减 = {expected_pairs}): "
                f"差额 {n_gap} 对 = 缺列或有效样本 n<10 被直接剔除 (不计入 n_pairs / mean / min); "
                "零方差或异常对则 pr 置 0.0 仍计入 n_pairs 并进 mean/min (二者结果相反)"
            )
            if n_nonfinite:
                logger.info(f"  (另剔除 {n_nonfinite} 个 NaN/inf 相关值, 不计入分布统计)")
            logger.info(
                f"  Pearson 分布: 平均={avg_pr_a:.4f}  最低={min_pr_a:.4f}  最高={max_pr_a:.4f}"
            )
            logger.info(
                f"  命中率: ≥0.95 的对 {n_ge95}/{n_pairs} (高度不敏感)  ≥0.90 的对 {n_ge90}/{n_pairs} (基本不敏感)"
            )
            if min_pr_a >= 0.95:
                logger.info(
                    f"  → 判读: min r={min_pr_a:.4f} ≥ 0.95, 衰减权重族内 (radius=2) 高度不敏感 (好); "
                    "论文 Appendix 一句话即可。"
                )
            elif min_pr_a >= 0.90:
                logger.info(
                    f"  → 判读: min r={min_pr_a:.4f} ∈ [0.90,0.95), 衰减权重族内基本不敏感 (好); "
                    "论文 Appendix 报相关性表格。"
                )
            else:
                logger.info(
                    f"  → 判读: min r={min_pr_a:.4f} < 0.90, 至少一套词典对衰减权重敏感 (临界/不利); "
                    "须在正文讨论衰减函数选择。"
                )
            logger.info(
                "  ⚠ 口径披露: uniform 列非生产 ctx 数值锚点 (半径 2 vs 1 / mean-of-ratios vs ratio-of-sums /"
            )
            logger.info(
                "    无标题 prepend); 高相关只证'衰减权重族内稳健', 不等于'主结果对权重方案不敏感'。"
            )
        else:
            logger.warning(
                f"  ⚠ 优雅降级: 0/{expected_pairs} 个有限相关对算成 — 词典缺失 / 全零方差 / 有效样本不足 "
                "(min Pearson 需有效样本 n≥10, 即 Pearson df=n−2≥8) / 全 NaN, 本阶段无稳健性结论。"
            )
        logger.info(
            f"  ⚠ 样本 = {n_obs:,} 篇 (盘面 T=2 小样本仅验证管道正确性, "
            "全量结论以 17M/T=18 实测为准)"
        )
        logger.info("-" * 72)
    except Exception as _e:
        logger.warning(f"[结果分析] 日志诊断计算异常, 跳过(不影响产物): {_e}")


# ============================================================================
# 7. 主流程
# ============================================================================

def main():
    """38b_decay_sensitivity 主流程。

    执行步骤:
      1. 加载 6 套中文金融情感词典
      2. 注入领域词汇到 jieba 分词器
      3. 加载阶段 21 输出数据
      4. 过滤仅保留 LLM 验证通过的金融科技新闻
      5. 对每篇文章计算 3 种衰减函数 × 6 词典 = 18 组情感得分
      6. 输出 Pearson/Spearman 相关性报告并保存 CSV
    """
    start_time = time.time()

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
    # 去重: 删除旧的短 banner (===  38b_decay_sensitivity ===), 只留本黄金范式单 banner。
    logger.info("=" * 72)
    logger.info("阶段 38b: 距离衰减权重敏感性检验 (Sautner et al. 2023 JF §2.2; G-14)")
    logger.info("=" * 72)
    logger.info("【功能】算银行情感分时, 离银行名越远的句子是否该按距离'打折'计权? 本阶段对")
    logger.info("        6 套词典各用 3 种衰减权重 (不打折/倒数/指数) 算一遍句级加权情感分,")
    logger.info("        看三套分数相关性高不高, 产出 18 列得分矩阵 + Pearson/Spearman 相关报告。")
    logger.info("【方法】句级距离 d (radius=2 窗口) → 权重 w(d): uniform=1 / inverse=1/(1+d) /")
    logger.info("        exponential=exp(-0.5d); 加权得分 = Σ w(d)·tone(s) / Σ w(d), tone(s)=单句")
    logger.info("        否定/转折/程度三规则归一化分 (与 22_tone_words 对齐)。比 uniform vs 衰减的相关。")
    logger.info("【判读】min Pearson≥0.95 高度不敏感(好) / ≥0.90 基本不敏感(好) / <0.90 须正文讨论(临界)。")
    logger.info("        ⚠ uniform 列非生产 ctx 数值锚点 (半径 2 vs 1 / mean-of-ratios vs ratio-of-sums /")
    logger.info("        无标题 prepend 三重口径差), 结论只支持'衰减权重族内稳健', 勿当'主结果不敏感'。")
    logger.info("【确定性】纯词典 + 确定句级提取 + jieba 分词, 无 LLM/Embedding 调用, 逐位可复现。")

    # ── 步骤 1: 加载词典 ──
    dictionaries = load_dictionaries()
    dict_names = [name for name, _ in dictionaries]

    # ── 步骤 2: 注入领域词汇到 jieba ──
    # 确保与 22_tone_words / 35_radius_sensitivity 的分词一致性
    _inject_custom_dicts_to_jieba(dictionaries)

    # ── 步骤 3: 加载数据 (阶段 21 输出) ──
    # 路径查找策略: config → fallback 搜索 output 目录中以 21_ 开头的 parquet 文件
    # audit-fixes 2026-05-29: 此前查 CONFIG['paths'] (仅含目录, 无文件名键) 且
    # 键名 'output_21_tone_llm' 漏 's'、'stage_21_output' 是 schemas.yaml 列约束
    # (不在 load_config merge 范围), 二者皆 dead → 始终退化为 glob sorted()[-1]
    # (靠字典序巧合选中 _full)。改为与同级 validation 模块一致, 直接读
    # CONFIG['filenames'] 的 _full 键 (验证模块用全量 llm_verified=True/False
    # 数据, paths.yaml:62); 下方 glob 仍作为安全网保留。
    input_key = CONFIG['filenames'].get('output_21_tone_llms_full',
                                        '21_tone_llms_full.parquet')
    input_path = os.path.join(OUTPUT_DIR, input_key) if input_key else ''
    if not input_path or not os.path.exists(input_path):
        # 回退: 搜索 output 目录中以 21_ 开头的 parquet 文件
        try:
            candidates = [f for f in os.listdir(OUTPUT_DIR)
                          if f.startswith('21_') and f.endswith('.parquet')]
        except FileNotFoundError:
            candidates = []
        if candidates:
            input_path = os.path.join(OUTPUT_DIR, sorted(candidates)[-1])
        else:
            logger.error("未找到阶段 21 输出文件")
            return

    logger.info(f"加载数据: {input_path}")
    df = pd.read_parquet(input_path)
    logger.info(f"数据量: {len(df):,} 行")

    # ── 步骤 4: 过滤 — 仅处理已验证的金融科技新闻 ──
    if 'llm_verified_full' in df.columns:
        df = df[df['llm_verified_full'] == True].copy()
        logger.info(f"LLM 验证后: {len(df):,} 行")

    # ── 步骤 5: 运行分析 ──
    score_df = run_analysis(df, dictionaries)

    # ── 步骤 6: 输出报告 ──
    log_correlation_report(score_df, dict_names)

    # ── 保存 CSV ──
    output_path = os.path.join(EVAL_DIR, '38b_decay_sensitivity.csv')
    score_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"结果已保存: {output_path}")

    # ── 阶段摘要 ──
    log_stage_summary(
        logger, STAGE_NAME, start_time,
        input_rows=len(df),
        output_rows=len(score_df),
        extra_info={
            '衰减函数': list(DECAY_FUNCTIONS.keys()),
            '词典数': len(dictionaries),
        }
    )


if __name__ == '__main__':
    main()
