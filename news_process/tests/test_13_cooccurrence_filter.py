"""test_13_cooccurrence_filter — stage 12b 银行×金科邻近共现硬过滤单测.

覆盖:
  - 窗口化原语 has_bank_fintech_cooccurrence_within_radius (同句/邻句/远隔/单侧/
    radius 单调/短文本字符回退/FINTECH_AC=None)。
  - filter_cooccurrence (逐行 keep/drop / 空 target_bank 丢弃 / schema 保留 /
    逐 (docid,target_bank) 行粒度)。
  - SAFE-1 优雅降级 (FINTECH_AC=None → 保留全部行 + WARNING)。
  - min_keep_frac 守卫 (真实零共现近全删 → SystemExit)。
"""
from __future__ import annotations

import ahocorasick
import pandas as pd
import pytest

from news_process.core.text.entity_context import (
    has_bank_fintech_cooccurrence_within_radius as _cooccur,
)


def _make_ac(words):
    """构建小型 Aho-Corasick 自动机 (与 load_fintech_dict 同款 API)。"""
    ac = ahocorasick.Automaton()
    for w in words:
        ac.add_word(w, w)
    ac.make_automaton()
    return ac


FT_AC = _make_ac(["区块链", "移动支付"])
BANK = "工商银行"


# ── 窗口化原语 ───────────────────────────────────────────────────────────────

def test_keep_same_sentence():
    text = "工商银行大力发展区块链技术。今天天气很好。市场反应平稳。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is True


def test_keep_adjacent_within_radius1():
    # 银行在 S0, 金科在 S1 (邻句) → radius=1 命中
    text = "工商银行召开发布会。会上推出区块链平台。市场反应平稳。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is True


def test_radius0_requires_same_sentence():
    # 邻句共现: radius=0 (严格同句) 丢弃, radius=1 保留
    text = "工商银行召开发布会。会上推出区块链平台。市场反应平稳。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=0) is False
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is True


def test_drop_far_apart_radius1():
    # 银行在 S0, 金科在 S3 (隔 ≥2 句) → radius=1 丢弃
    text = "工商银行发展战略。今天天气很好。空气十分清新。市场推出区块链平台。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is False


def test_radius_monotone_keeps_when_widened():
    # 同一远隔文本 (银行 S0, 金科 S3, 距离=3): radius 单调不减
    text = "工商银行发展战略。今天天气很好。空气十分清新。市场推出区块链平台。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=2) is False  # 距离=3 > 2, 仍不够 (钉死 off-by-one 边界)
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=3) is True   # radius=3 恰好覆盖 → 保留


def test_drop_bank_only():
    text = "工商银行召开发布会。今天天气很好。市场反应平稳。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is False


def test_drop_fintech_only():
    text = "市场推出区块链平台。今天天气很好。反应平稳。"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is False


def test_short_text_charfallback_keep():
    # <3 句走字符级回退: 银行字符窗口内含金科 → 保留
    text = "工商银行推出区块链钱包"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1) is True


def test_short_text_charfallback_drop_fintech_far():
    # ⚠ 占位文本【不含句号】→ 强制 nsent=1 (<3 句) → 真正走 _char_level_fallback 字符回退分支。
    #   银行(pos 0) 与金科(末尾) 相隔 > fallback_char_radius=10 → 字符窗口不覆盖 → 丢弃。
    text = "工商银行" + ("占位文本" * 60) + "区块链"
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1,
                    fallback_char_radius=10) is False
    # 同文本放大字符窗 → 银行窗口覆盖到金科 → 保留 (证 fallback_char_radius 确为 load-bearing 参数)
    assert _cooccur(text, [BANK], FT_AC, sentence_radius=1,
                    fallback_char_radius=999) is True


def test_fintech_ac_none_returns_false():
    text = "工商银行大力发展区块链技术。今天天气很好。市场反应平稳。"
    assert _cooccur(text, [BANK], None, sentence_radius=1) is False


def test_empty_inputs_return_false():
    assert _cooccur("", [BANK], FT_AC) is False
    assert _cooccur("工商银行区块链。a。b。", [], FT_AC) is False


# ── filter_cooccurrence / main (需导入模块, 触发 CONFIG 加载) ──────────────────

@pytest.fixture()
def cf(monkeypatch):
    """导入 12b 模块并把匹配相关 global 钉死为受控小词典 (隔离真盘词典/排除表)。"""
    from news_process.pipeline.filtering import cooccurrence_filter as mod
    monkeypatch.setattr(mod, "FINTECH_AC", FT_AC)
    monkeypatch.setattr(mod, "_FINTECH_KEYWORDS", ["区块链", "移动支付"])
    monkeypatch.setattr(mod, "NEGATION_AC", None)
    monkeypatch.setattr(mod, "SHORT_NAME_EXCLUSIONS", None)
    return mod


def test_filter_keeps_and_drops(cf):
    df = pd.DataFrame({
        "docid": ["d1", "d2", "d3"],
        "target_bank": [BANK, BANK, BANK],
        "内容": [
            "工商银行大力发展区块链技术。今天天气很好。市场平稳。",   # keep (同句)
            "工商银行召开发布会。今天天气很好。市场反应平稳。",       # drop (无金科)
            "市场推出区块链平台。今天天气很好。反应平稳。",          # drop (无银行)
        ],
    })
    out = cf.filter_cooccurrence(df)
    assert out["docid"].tolist() == ["d1"]
    assert list(out.index) == [0]  # index 重置


def test_empty_target_bank_dropped(cf):
    df = pd.DataFrame({
        "docid": ["d1", "d2", "d3", "d4"],
        "target_bank": ["", "nan", None, float("nan")],
        "内容": ["工商银行发展区块链。a。b。"] * 4,
    })
    out = cf.filter_cooccurrence(df)
    assert len(out) == 0  # 无有效 target_bank → 全丢


def test_schema_preserved(cf):
    df = pd.DataFrame({
        "docid": ["d1", "d2"],
        "target_bank": [BANK, BANK],
        "内容": [
            "工商银行发展区块链。a。b。",   # keep
            "无关新闻一。无关二。无关三。",  # drop
        ],
        "extra_col": [1, 2],
    })
    out = cf.filter_cooccurrence(df)
    assert list(out.columns) == list(df.columns)  # 列不变
    assert len(out) == 1                            # 行子集
    assert set(out["docid"]).issubset(set(df["docid"]))


def test_per_bank_row_granularity(cf):
    # 同 docid 展开两家银行: 工行与区块链同句(keep), 建行远隔(drop) → 逐行独立
    text = "工商银行发展区块链。天气晴朗。空气清新。建设银行召开会议。"
    df = pd.DataFrame({
        "docid": ["d1", "d1"],
        "target_bank": ["工商银行", "建设银行"],
        "内容": [text, text],
    })
    out = cf.filter_cooccurrence(df)
    assert out["target_bank"].tolist() == ["工商银行"]


def test_graceful_degrade_fintech_ac_none(monkeypatch):
    """SAFE-1: FINTECH_AC=None → 保留全部行 + WARNING (绝不静默清空)。

    直接挂 handler 到模块 logger (项目 logger 自带 handler、不向 root/caplog 传播,
    capfd 也抓不到其预绑定 stream)。
    行为证据: 这两行均【非】共现, 若降级未生效 (走正常过滤) 会被全删→0 行;
    实得全保留 ⇒ 必然走了 SAFE-1 早退分支。
    """
    import logging

    from news_process.pipeline.filtering import cooccurrence_filter as mod
    monkeypatch.setattr(mod, "FINTECH_AC", None)

    records: list[str] = []

    class _Collector(logging.Handler):
        def emit(self, record):
            records.append(record.getMessage())

    handler = _Collector(level=logging.WARNING)
    mod.logger.addHandler(handler)
    try:
        df = pd.DataFrame({
            "docid": ["d1", "d2"],
            "target_bank": [BANK, "建设银行"],
            "内容": ["毫不相关新闻。a。b。", "另一条新闻。c。d。"],
        })
        out = mod.filter_cooccurrence(df)
    finally:
        mod.logger.removeHandler(handler)

    assert len(out) == len(df)                          # 全保留 (非共现行未删 → 证降级生效)
    assert any("SAFE-1" in m for m in records)          # 大声告警


def test_min_keep_guard_raises(cf, monkeypatch, tmp_path):
    """真实零共现近全删 → main() min_keep_frac 守卫 SystemExit (防全库误删)。"""
    import news_process.core.text.entity_context as ec
    # 隔离别名缓存, 避免污染
    monkeypatch.setattr(ec, "_BANK_DATA", None, raising=False)
    monkeypatch.setattr(ec, "_ALIASES_CACHE", {}, raising=False)
    monkeypatch.setattr(cf, "CONFIG", {
        "paths": {"output_dir": str(tmp_path), "bank_names_file": ""},
        "filenames": {},
        "cooccurrence_filter": {"sentence_radius": 1, "min_keep_frac": 0.5},
        "context_window": {"fallback_char_radius": 150},
    })
    # 输入: 两行都无金科共现 → keep_frac=0 < 0.5
    df_in = pd.DataFrame({
        "docid": ["d1", "d2"],
        "target_bank": [BANK, BANK],
        "内容": ["毫不相关新闻。占位一。占位二。", "另一条新闻。占位三。占位四。"],
    })
    df_in.to_parquet(tmp_path / "12_fintech_news.parquet")
    with pytest.raises(SystemExit) as ei:
        cf.main()
    assert ei.value.code == 1  # 确认是 min-N 守卫的 exit(1), 而非其它更早退出
