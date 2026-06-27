"""tests/test_tone_llms_logger_redirect.py — 日志覆盖根治回归锁 (2026-06-27).

根因 (诊断): ``tone_llms`` 同时是 stage 21 入口 + 可复用 LLM-fetch 库。其借用层
函数 (fetch_llm_async / AsyncModelAvailability / preflight / _aggregate_track) 全部
经模块级全局 ``logger`` (名 "21_tone_llms", 指向 logs/21_tone_llms.log, file_mode='w'
首写截断) 落盘。stage 66 (entity_masking) / stage 70 (prompt_sensitivity) import 并
在自己的子进程里调用这些借用函数时, **第一条 emit 即截断覆盖真实 stage 21 日志**
(实测把 logs/21_tone_llms.log 覆写成几行 transient-failure)。

根治 = ``tone_llms.redirect_module_logger(new_logger)``: 借用方在跑 LLM 前显式接管
模块 logger, 借用函数日志改落调用方自己的文件, stage 21 日志不再被波及。

本测试锁定:
  1. redirect 正确重绑定并返回原 logger; 传 None 为 no-op; 可恢复。
  2. 重定向后, 借用函数 (note_transient_failure, 复刻 bug 的确切日志行
     "…该次结果将从投票中排除") 落到重定向后的 logger, **不再**落到原
     "21_tone_llms" logger。
  3. 两个验证阶段 main() 顶部确有 redirect_module_logger(logger) 接管调用。
"""
from __future__ import annotations

import asyncio
import logging

from news_process.pipeline.sentiment import tone_llms


class _ListHandler(logging.Handler):
    """把 emit 到的日志消息收集进一个 list, 供断言。"""

    def __init__(self, sink: list):
        super().__init__()
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        self._sink.append(record.getMessage())


def test_redirect_module_logger_rebinds_and_restores():
    original = tone_llms.logger
    sentinel = logging.getLogger("test_tone_llms_redirect_sentinel")
    try:
        returned = tone_llms.redirect_module_logger(sentinel)
        assert returned is original          # 返回原 logger 供恢复
        assert tone_llms.logger is sentinel  # 已重绑定

        # None = no-op: 保持当前 (sentinel) 不变
        ret2 = tone_llms.redirect_module_logger(None)
        assert ret2 is sentinel
        assert tone_llms.logger is sentinel
    finally:
        tone_llms.redirect_module_logger(original)
        assert tone_llms.logger is original


def test_borrowed_emit_goes_to_redirected_not_original():
    """借用函数日志须落重定向后的 logger, 原 "21_tone_llms" logger 收不到 (不被截断覆盖)。"""
    original = tone_llms.logger

    redirected_msgs: list[str] = []
    original_msgs: list[str] = []

    redirected = logging.getLogger("test_tone_llms_redirect_capture")
    redirected.setLevel(logging.DEBUG)
    redirected.handlers.clear()
    redirected.addHandler(_ListHandler(redirected_msgs))
    redirected.propagate = False

    # 给原 logger 也挂一个捕获器, 断言重定向后它绝不再收到借用函数日志
    orig_handler = _ListHandler(original_msgs)
    original.addHandler(orig_handler)

    try:
        tone_llms.redirect_module_logger(redirected)
        # 复刻 bug 的确切日志行: note_transient_failure → "…该次结果将从投票中排除"
        ma = tone_llms.AsyncModelAvailability()
        asyncio.run(ma.note_transient_failure(
            "gemini-3.1-flash-lite", "连续 80 次请求未成功", 148))

        assert any("该次结果将从投票中排除" in m for m in redirected_msgs), redirected_msgs
        assert not any("该次结果将从投票中排除" in m for m in original_msgs), original_msgs
    finally:
        tone_llms.redirect_module_logger(original)
        original.removeHandler(orig_handler)


def test_validation_stages_invoke_redirect_in_main():
    """两个借用 tone_llms fetch 函数的验证阶段 main() 必须接管模块 logger。"""
    import inspect
    from importlib import import_module

    for mod_name in (
        "news_process.validation.entity_masking",
        "news_process.validation.prompt_sensitivity",
    ):
        mod = import_module(mod_name)
        src = inspect.getsource(mod.main)
        assert "redirect_module_logger(logger)" in src, (
            f"{mod_name}.main() 缺少 tone_llms.redirect_module_logger(logger) 接管调用 "
            "— 会回退到截断覆盖 logs/21_tone_llms.log 的旧 bug"
        )
