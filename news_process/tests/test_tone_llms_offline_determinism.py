"""tests/test_tone_llms_offline_determinism.py — 问题3 离线确定性守卫单测.

覆盖 stage 21 的"golden 跨-run 确定性"机制 (见 caching / tone_llms):
  1. 离线模式 (NEWS_PROCESS_LLM_OFFLINE=1) 缓存 miss → raise LLMCacheMissError
     (杜绝静默付费 / 投票漂移), 且 raise 发生在任何网络调用之前。
  2. 离线模式缓存 hit → 正常返回缓存响应 (零 API)。
  3. iter_article_track_prompts 是 prompt 构造的单一事实源: 双轨、可重复、
     与 stage 21 生产路径同源 → 缓存键稳定 (确定性的前提)。

全程零网络: session 传 None, hit/raise 都发生在 session.post 之前。
"""
from __future__ import annotations

import asyncio

import pandas as pd
import pytest

from news_process.core.caching import LLMCache
from news_process.pipeline.sentiment import tone_llms


def _model_cfg():
    return {'model_name': 'unit-test-model', 'short_name': 'utm',
            'base_url': 'http://invalid.localhost', 'api_key': 'k'}


def test_offline_guard_raises_on_cache_miss(tmp_path, monkeypatch):
    """离线模式 + 空缓存 → LLMCacheMissError (绝不落到付费 API)。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', True)
    cache = LLMCache(str(tmp_path / 'c.db'))  # 空 → 必 miss
    try:
        with pytest.raises(tone_llms.LLMCacheMissError):
            asyncio.run(tone_llms.fetch_llm_async(
                None, asyncio.Semaphore(1),
                'some-uncached-prompt', _model_cfg(), 0, 'full',
                cache=cache, prompt_version=tone_llms.PROMPT_VERSION,
            ))
    finally:
        cache.close()


def test_offline_guard_returns_cached_on_hit(tmp_path, monkeypatch):
    """离线模式 + 命中 → 返回缓存响应, 不抛、不调 API。"""
    monkeypatch.setattr(tone_llms, 'LLM_OFFLINE', True)
    cache = LLMCache(str(tmp_path / 'c.db'))
    cfg = _model_cfg()
    prompt = 'cached-prompt'
    cached_text = '{"sentiment": "正面", "verified": true}'
    # 用与 fetch_llm_async 内 get() 完全一致的键参数写入
    cache.put(cfg['model_name'], prompt, cached_text,
              prompt_version=tone_llms.PROMPT_VERSION,
              temperature=tone_llms.TEMPERATURE,
              random_seed=tone_llms.RANDOM_SEED)
    try:
        out = asyncio.run(tone_llms.fetch_llm_async(
            None, asyncio.Semaphore(1),
            prompt, cfg, 7, 'ctx',
            cache=cache, prompt_version=tone_llms.PROMPT_VERSION,
        ))
    finally:
        cache.close()
    assert out == (7, cfg['model_name'], cached_text, 'ctx')


def test_offline_flag_parsing_truthy():
    """LLM_OFFLINE 仅识别 1/true/yes/on (大小写无关), 其余 → False。"""
    import os

    # 复刻模块里的解析表达式, 守护"默认关闭 / 不误开"契约
    def parse(v):
        return v.strip().lower() in ('1', 'true', 'yes', 'on')

    assert parse('1') and parse('TRUE') and parse('Yes') and parse(' on ')
    assert not parse('') and not parse('0') and not parse('false') and not parse('no')
    # 真实环境默认 (CI / 生产) 不设此变量 → 模块常量应为 False
    if 'NEWS_PROCESS_LLM_OFFLINE' not in os.environ:
        assert tone_llms.LLM_OFFLINE is False


def test_iter_article_track_prompts_dual_track_and_deterministic():
    """单一事实源: 每行 yield (full, ctx, ss) 三轨, 且重复调用字节级一致。

    v3.9.0 三轨: 新增第三轨 ss (银行+金科同句); content_ss 缺列时 iter 内部
    回退 content_full, 仍 yield 'ss' 轨 (轨结构三元, 确定性不变)。
    """
    df = pd.DataFrame([
        {'内容': '招商银行上线区块链。', 'content_ctx': '招商银行区块链窗口。',
         'content_ss': '招商银行上线区块链。',
         '标题': '招行科技', 'target_bank': '招商银行', 'co_mentioned_banks': '无'},
        {'内容': '工商银行布局数字货币。', 'content_ctx': '工行数字货币窗口。',
         'content_ss': '工商银行布局数字货币。',
         '标题': '工行数币', 'target_bank': '工商银行', 'co_mentioned_banks': '无'},
    ])
    first = list(tone_llms.iter_article_track_prompts(df))
    second = list(tone_llms.iter_article_track_prompts(df))
    # 2 行 × 3 轨 (full/ctx/ss) = 6 条
    assert len(first) == 6
    tracks = [t for _, t, _ in first]
    assert tracks == ['full', 'ctx', 'ss', 'full', 'ctx', 'ss']
    # 确定性: 两次构造完全一致 (缓存键稳定的前提)
    assert first == second
    # 每条 prompt 非空字符串
    assert all(isinstance(p, str) and p for _, _, p in first)
