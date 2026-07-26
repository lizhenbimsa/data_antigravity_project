"""tests/test_embedding_split_postcondition.py — F21 gate: 切块后置条件。

**为何需要 (2026-07-26 生产实弹)**: stage 40 (strategic_diff bank-year 超级文档) 跑 2 小时后
崩于 `RuntimeError: Embedding 单条输入超限: 8192 > 8191` —— `split_text_for_embedding`
切出的块在下游 `get_embeddings_api` 重新 encode 时算出 **8192** token, 违反该函数自身契约,
而下游那条守卫是**致命不可重试**的 raise ⟹ 整阶段报废、2 小时作废。

⚠ 诚实说明: 触发条件**未能复现** (试过真实语料滑动 292 个切点 + 复刻 2017 年 428 条
bank-year 超级文档, 均未命中) → 成因未定位。因此整改思路不是「修某个机理」而是
**直接强制后置条件**: 无论漂移由什么引起, 每个返回块都实测回编码 ≤ EMB_MAX_TOKENS。
本文件即该后置条件的可执行契约。

不变量:
  ① 每个返回块回编码 ≤ EMB_MAX_TOKENS (**核心**, 违反即下游致命 raise);
  ② 块非空且拼接覆盖原文 token 全集 (不丢内容);
  ③ 短文本 (≤上限) 原样单块返回 —— 保证既有缓存键零漂移。
"""
from __future__ import annotations

import os
import sys

import pytest

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.pipeline.text import embedding_engine as eng  # noqa: E402

LIM = eng.EMB_MAX_TOKENS


def _ntok(s: str) -> int:
    return len(eng._EMB_ENCODING.encode(s, disallowed_special=()))


# ── ③ 短文本原样返回 (缓存键零漂移的前提) ──

@pytest.mark.parametrize('text', [
    '', ' ', '短文本', '银行金融科技新闻正文' * 10,
])
def test_short_text_returned_verbatim_single_chunk(text):
    out = eng.split_text_for_embedding(text)
    assert len(out) == 1, '短文本必须单块返回'
    expected = str(text) if str(text) else ' '
    assert out[0] == expected, (
        '短文本必须**原样**返回 —— 任何改写都会使既有缓存键全体失效并触发付费重嵌')


# ── ①② 超长文本: 后置条件 + 覆盖性 ──

def _long_text(n_chars: int) -> str:
    base = ('某银行发布金融科技战略规划, 推进数字人民币试点与智能风控体系建设。'
            'The bank released a fintech strategy covering digital RMB pilots. ')
    return (base * (n_chars // len(base) + 1))[:n_chars]


@pytest.mark.parametrize('n_chars', [20000, 60000, 150000])
def test_every_chunk_within_token_limit(n_chars):
    """核心不变量: 每个块回编码 ≤ 上限 —— 违反即下游 get_embeddings_api 致命 raise。"""
    chunks = eng.split_text_for_embedding(_long_text(n_chars))
    assert len(chunks) > 1, '本用例应触发切块'
    over = [(i, _ntok(c)) for i, c in enumerate(chunks) if _ntok(c) > LIM]
    assert not over, (
        f'{len(over)} 个块回编码超限 (上限 {LIM}): {over[:5]} —— '
        f'这正是 2026-07-26 stage 40 崩溃 (8192>8191) 的直接原因')


@pytest.mark.parametrize('n_chars', [20000, 60000])
def test_chunks_are_nonempty_and_cover_input(n_chars):
    """块非空且无内容丢失 (拼接后 token 数不少于原文, 允许边界重编码带来的微增)。"""
    text = _long_text(n_chars)
    chunks = eng.split_text_for_embedding(text)
    assert all(c for c in chunks), '不得产出空块'
    assert sum(_ntok(c) for c in chunks) >= _ntok(text) * 0.999, '切块疑似丢内容'


def test_pathological_shrink_terminates(monkeypatch):
    """病态输入下收缩循环必须有界终止 (不死循环、不无限重编码)。

    把上限压到极小以放大边界效应, 验证函数仍返回且每块合规。"""
    monkeypatch.setattr(eng, 'EMB_MAX_TOKENS', 16)
    out = eng.split_text_for_embedding(_long_text(4000))
    assert len(out) > 1
    assert all(
        len(eng._EMB_ENCODING.encode(c, disallowed_special=())) <= 16 for c in out), \
        '压低上限后仍须满足后置条件'


def test_downstream_guard_message_is_diagnosable():
    """下游致命守卫的消息必须可定位 —— 旧消息只有两个数字, 排查只能靠猜。"""
    import inspect
    src = inspect.getsource(eng.get_embeddings_api)
    for token in ('missing_texts 第', '全局行号', '首 80 字', 'model='):
        assert token in src, f'致命守卫消息缺少可定位字段: {token}'
