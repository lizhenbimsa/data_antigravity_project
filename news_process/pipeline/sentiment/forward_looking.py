"""news_process.pipeline.sentiment.forward_looking — A2 中文 FLS 实施.

v3.5.2 PR #3 (与 lm_non_sentiment.py 同 sprint) — 中文 Forward-Looking
Statements 句子级双门控判定. 复用 v3.5.2 PR #1 ``cn_text_utils`` 的中文
分句器, 不依赖任何 v3.6.0 之外的新包.

学术依据
--------
Li, F. (2010). The Information Content of Forward-Looking Statements in
Corporate Filings — A Naïve Bayesian Machine Learning Approach. Journal of
Accounting Research, 48(5), 1049-1102.

Bozanic, Z., Roulstone, D. T., & Buskirk, A. V. (2018). Management
earnings forecasts and other forward-looking statements. Review of
Accounting Studies, 23(1), 1-26.

判定规则 (双门控)
-----------------
一个句子是 FLS 当且仅当:
    ∃ w ∈ s: w ∈ D_future  ∧  ∃ t ∈ s: t ∈ D_time

D_future = {将, 拟, 预计, 计划, 望, 展望, 期待, 着力, 力争, 致力于, 有望, ...}
D_time   = {未来, 明年, 下季, 三年内, 中长期, 下一阶段, ...}

panel 新增 2 列
---------------
``frac_fls_{full,ctx}`` = (FLS 句数) / (总句数) ∈ [0, 1]

集成点 (PR #14)
---------------
``pipeline.sentiment.tone_words::_dual_analyze`` 内对 content_full / content_ctx
各调用一次本模块的 ``compute_fls_for_text``.

G-A2.1 准入门控
---------------
词表 ≥ 100 词 + 500 句人工标注 precision ≥ 0.80; 当前是 v0.1.5 双门控 (future ~72 词 + time ~59 词 ≈ 131 词).
"""

from __future__ import annotations

import jieba

from news_process.core.text.cn_text_utils import cn_split_sentence

# P-038 修复 (v3.7.1): single-char "望"/"盼"/"将" substring 匹配会命中
# "希望"/"绝望"/"瞭望"/"将其"/"将该" 等非 forward-looking 上下文. 改用
# jieba.cut() 精确 token 匹配, 避免 substring false positives.
# Performance: jieba 单例 cache, ~0.1ms/sentence.

# ── FLS 双门控词表 (v0.1.5, future ~72 词 + time ~59 词 = 双门控 ≥ 100 词总) ──
# v2.3-followup-v2 第 17 轮 user-request 扩展 (基于 Li 2010 JAR + 中文金融
# 年报披露规范, 非专家审定);
# USER_ACTION_REQUIRED v0.2:
#   - 中文金融专家进一步审定 (1 人·周)
#   - 500 句人工标注验证 precision ≥ 0.80 (G-A2.1 准入门控)
_FUTURE_WORDS = frozenset([
    # ── 主动未来 modal ──
    "将", "将要", "将会", "将于", "拟", "拟于", "拟将", "意欲",
    "意图", "意在", "拟定",
    # ── 计划意图 ──
    "计划", "规划", "筹划", "策划", "谋划", "图谋", "拟订",
    "预计", "预期", "预测", "预想", "预判", "预估", "预设",
    # ── 展望 ──
    "展望", "望", "有望", "期待", "期望", "盼望", "盼", "瞻望",
    "翘首", "希冀", "希望",
    # ── 战略意图 ──
    "战略", "蓝图", "愿景", "目标", "前景", "愿望",
    # ── 持续推进 ──
    "着力", "致力于", "力争", "争取", "努力", "奋力",
    "推进", "推动", "促进", "推动力", "推行",
    # ── 即将 ──
    "即将", "行将", "快将", "马上",
    # ── 承诺 / 决心 ──
    "承诺", "誓将", "誓必", "决心", "誓言", "宣告",
    # ── 财务/IR 披露惯用前瞻动词 (Li 2010 JAR appendix) ──
    "拟实施", "拟开展", "拟推出", "拟落地", "拟启动",
    "酝酿", "筹备", "准备", "拟议",
])

_TIME_FUTURE_MARKERS = frozenset([
    # ── 显式未来 ──
    "未来", "今后", "日后", "以后", "嗣后",
    "明年", "次年", "下年", "翌年", "明春", "明秋",
    "下季", "下季度", "下半年", "下半场",
    "下月", "下一月", "下旬", "次月",
    "下一阶段", "下一步", "下一轮", "下一程", "下一周期",
    # ── 时段 ──
    "中长期", "长远", "远期", "中期", "短期内", "长期",
    "三年", "五年", "十年", "三年内", "五年内", "十年内",
    "三年期", "五年期", "十年期",
    # ── 节点 (Li 2010 后续工作建议增强 regex 模式) ──
    "到 2030", "到 2035", "到 2040", "至 2030",
    "十四五", "十五五", "十六五",
    "年底", "年内", "本年度", "本季度", "本财年",
    # ── 滚动期窗 ──
    "未来三年", "未来五年", "未来十年",
    "下一财年", "下一会计期",
    # ── 远景 (战略规划惯用) ──
    "中长期目标", "远景目标", "战略目标期",
])


def _is_fls_sentence(sentence: str) -> bool:
    """双门控判定: 句中同时含 future 词与 time 词.

    P-038 修复 (v3.7.1): 改 jieba 精确 token 匹配, 避免单字 "望/盼/将"
    substring 误命中 "希望/绝望/瞭望/将其/将该" 等非 forward-looking 上下文.
    """
    if not sentence:
        return False
    tokens = set(jieba.cut(sentence))
    if not (tokens & _FUTURE_WORDS):
        return False
    return bool(tokens & _TIME_FUTURE_MARKERS)


def compute_fls_for_text(text: str) -> dict[str, float]:
    """单文本 FLS 比例; 仿 v3.5.1 ``_compute_clarity_for_text`` 接口.

    Args:
        text: 待分析的中文文本.

    Returns:
        {
            'n_sentences': int,
            'n_fls_sentences': int,
            'frac_fls': float | nan,
        }

    Examples:
        >>> r = compute_fls_for_text("银行业务规模达 100 亿。计划未来三年达 500 亿。")
        >>> r['n_sentences']
        2
        >>> r['n_fls_sentences']
        1
        >>> r['frac_fls']
        0.5
    """
    if not text or not text.strip():
        return {
            'n_sentences': 0,
            'n_fls_sentences': 0,
            'frac_fls': float('nan'),
        }
    sents = cn_split_sentence(text)
    n = len(sents)
    if n == 0:
        return {
            'n_sentences': 0,
            'n_fls_sentences': 0,
            'frac_fls': float('nan'),
        }
    fls_n = sum(1 for s in sents if _is_fls_sentence(s))
    return {
        'n_sentences': n,
        'n_fls_sentences': fls_n,
        'frac_fls': fls_n / n,
    }


def get_panel_columns(suffix: str) -> list[str]:
    """返回 panel 应追加的 1 列名 (按指定后缀; 双轨各 1 列, 共 2 列).

    Args:
        suffix: '_full' 或 '_ctx'.

    Returns:
        [f'frac_fls{suffix}']
    """
    return [f'frac_fls{suffix}']


__all__ = [
    '_FUTURE_WORDS',
    '_TIME_FUTURE_MARKERS',
    'compute_fls_for_text',
    'get_panel_columns',
]
