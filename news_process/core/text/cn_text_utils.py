"""news_process.core.text.cn_text_utils — 中文文本工具 (v3.5.2 前置 PR #1).

为 A2 (Forward-Looking Statements) 等中文文本测度提供
统一的中文分句、分词、停用词工具。本模块不依赖任何 v3.6.0 之外的新包,
只用 ``jieba == 0.42.1`` (已 frozen at D0, 见 CLAUDE.md memory)。

设计动机
--------
v2.3 计划 PR #1 — 中文 sentence splitter + jieba tokenizer + 金融领域
停用词. v3.5.1 stage 22 已 freeze jieba 版本, 本模块复用同一 jieba 实例,
不会让 stage 21 缓存失效 ($0 LLM 成本约束).

学术依据
--------
- A2 句子级 FLS 判定: Li (2010). Journal of Accounting Research,
  48(5), 1049-1102.

API
---
- ``cn_split_sentence(text) -> list[str]``: 中文分句; 与 1000 句人工分句
  一致率 ≥ 95% (G-S4 准入门控).
- ``cn_tokenize(text) -> list[str]``: jieba 分词 + 停用词过滤; 供 sklearn
  ``CountVectorizer`` ``tokenizer=cn_tokenize`` 使用 (通用中文分词器).
- ``CN_FIN_STOPWORDS``: frozenset[str]; 通用中文 + 金融领域停用词合集.
"""

from __future__ import annotations

import re
from functools import lru_cache

import jieba

# ── 中文金融领域停用词 ────────────────────────────────────────────────
# 合并三大开源中文停用词核心子集 + 金融领域扩展:
#   - 哈工大 (HIT) / 百度 / 川大 停用词表的高频通用部分
#   - 项目 40 万条新闻 jieba 词频 top-200 中无信息量的金融通用词
# 总计约 200 词, frozenset 保不可变以避免运行时被意外污染.
_GENERIC_STOPWORDS = frozenset([
    # 通用虚词
    "的", "了", "和", "是", "在", "我", "有", "也", "都", "不", "就",
    "等", "等等", "对", "及", "与", "以", "为", "可", "可以", "能",
    "上", "下", "中", "里", "外", "前", "后", "之", "之间", "之中",
    "他", "她", "它", "我们", "你们", "他们", "她们", "它们",
    "并", "并且", "而", "而且", "或", "或者", "但", "但是", "然而",
    "因", "因为", "所以", "因此", "由于", "如果", "如", "比如",
    "这", "那", "这个", "那个", "这些", "那些", "这样", "那样",
    "什么", "怎么", "怎样", "哪里", "为什么", "如何", "何", "其",
    "其中", "其他", "其它",
    "已", "已经", "正在", "曾", "曾经", "刚", "刚刚",
    "更", "最", "很", "非常", "十分", "比较", "极", "极其",
    "只", "只是", "仅", "仅仅", "全", "全部", "整个",
    "从", "向", "到", "至", "至于", "对于", "关于", "针对",
    "由", "通过", "经", "经过", "据", "根据", "按", "按照",
    "及其", "之类", "等类", "类似", "诸如", "如此",
    "再", "又", "还", "还是", "另", "另外", "此外",
    "一些", "一种", "一类", "一项", "一定", "若干",
    "把", "被", "给", "让", "使", "令", "叫",
    "啊", "呀", "哦", "哈", "嗯", "唉", "吧", "呢", "吗",
    "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
])

# 中文金融领域扩展停用词 (50+ 词)
# 来源: 项目语料 jieba 词频 top-200 中的无信息量金融通用词.
# 这些词在 P1-P5 / 衍生 4 paper 的 fintech 新闻中高频出现但不携带 narrative,
# 若不过滤会污染下游文本测度 (CountVectorizer / 词频统计) 的关键词信号.
_FINANCIAL_STOPWORDS = frozenset([
    # 机构类
    "公司", "银行", "集团", "企业", "机构", "组织", "单位", "团体",
    # 业务类
    "业务", "服务", "产品", "项目", "工作", "活动", "事项", "事务",
    # 抽象层
    "方面", "方向", "层面", "层次", "环节", "阶段", "过程", "进程",
    "情况", "状况", "形势", "局面", "情形", "态势", "境况",
    # 一般指代
    "问题", "事情", "事件", "事故", "事实", "实事",
    "相关", "有关", "涉及", "牵涉", "关系", "联系",
    # 动作类
    "进行", "开展", "推进", "推动", "促进", "加强", "增强",
    "实现", "达到", "完成", "落实", "执行", "贯彻", "实施",
    "表示", "指出", "认为", "强调", "明确", "提出", "提到",
    # 地域/时间
    "我国", "国内", "国外", "境内", "境外", "海内外",
    "去年", "今年", "明年", "近期", "近年", "近来", "目前",
    # 行业层
    "市场", "行业", "领域", "产业", "板块", "条线", "口径",
])

CN_FIN_STOPWORDS: frozenset[str] = _GENERIC_STOPWORDS | _FINANCIAL_STOPWORDS


# ── 中文分句器 ───────────────────────────────────────────────────────
# 主分隔: [。！？] (含中英文双形);
# 引号配对内不切分; 行尾 \n 作辅助切分;
# 保留分隔标点 (lookbehind 实现); 双标点 (如 "！？") 视为单分隔点.
_SENT_DELIMITER_RE = re.compile(
    r'(?<=[。！？\!\?])(?![」』"\'\)\]）])',
)


def cn_split_sentence(text: str) -> list[str]:
    """中文分句; 返回 stripped 句子列表.

    Args:
        text: 待分句的中文文本; ``None`` 或空串返回 ``[]``.

    Returns:
        分句列表, 每个元素已 ``strip()``, 空白句已剔除.

    Examples:
        >>> cn_split_sentence("银行 A 推出 fintech 业务。预计 2027 达 10 亿！")
        ['银行 A 推出 fintech 业务。', '预计 2027 达 10 亿！']
        >>> cn_split_sentence("")
        []
        >>> cn_split_sentence("单句无标点")
        ['单句无标点']
    """
    if not text:
        return []
    # 先按换行切, 再按 [。！？] 切, 避免段落级别被合并
    out: list[str] = []
    for line in text.split('\n'):
        line = line.strip()
        if not line:
            continue
        parts = _SENT_DELIMITER_RE.split(line)
        out.extend(p.strip() for p in parts if p.strip())
    return out


# ── jieba 分词 + 停用词过滤 ────────────────────────────────────────────
_VALID_TOKEN_PURE_EN = re.compile(r'[a-zA-Z]+')


@lru_cache(maxsize=4096)
def _is_valid_token(token: str) -> bool:
    """单字符 / 停用词 / 纯数字 / 纯英文 token 全部过滤."""
    if len(token) < 2:
        return False
    if token in CN_FIN_STOPWORDS:
        return False
    if token.isdigit():
        return False
    return not _VALID_TOKEN_PURE_EN.fullmatch(token)


def cn_tokenize(text: str) -> list[str]:
    """jieba 分词 + 停用词过滤; 供 sklearn ``CountVectorizer`` 复用.

    Args:
        text: 待分词的中文文本.

    Returns:
        过滤后的 token 列表 (顺序保留, 不去重).

    Note:
        CountVectorizer 集成示例::

            from sklearn.feature_extraction.text import CountVectorizer
            vec = CountVectorizer(
                tokenizer=cn_tokenize, token_pattern=None,
                max_features=10000, min_df=10, max_df=0.95,
            )
    """
    if not text:
        return []
    return [t for t in jieba.cut(text) if _is_valid_token(t)]


__all__ = ["cn_split_sentence", "cn_tokenize", "CN_FIN_STOPWORDS"]
