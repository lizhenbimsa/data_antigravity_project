"""LOG-COLOR 不变量回归守护 (2026-06-25):

**任何落盘日志文件都不得含 ANSI 转义码。**

根因 (历史): 阶段子进程的 stdout 被 orchestrator 以 ``subprocess.PIPE`` 捕获时
(非 TTY), 子进程的 ``_ColoredFormatter`` 仍输出 ANSI 着色, orchestrator 经
``_reader_thread`` 把这些彩色行原样转发进 ``run_pipeline_*.log``, 转义码污染落盘日志。

两道防线 (本测试逐一锁死):
  1. 源头 — ``core/logging.py``: console 着色受 TTY 闸控 (``_should_colorize``),
     被管道/重定向时退化为与文件 handler 一致的无色纯文本。
  2. 边界 — ``core/stage.py``: ``_reader_thread`` 转发前剥离任何残留 ANSI 序列,
     保证 orchestrator 落盘日志恒为纯文本 (即使子进程因第三方库等仍输出转义码)。
"""
from __future__ import annotations

import io
import logging

import pytest

from news_process.core.logging import (
    _PLAIN_LINE_FMT,
    _ColoredFormatter,
    _should_colorize,
    setup_logging,
)
from news_process.core.stage import _ANSI_ESCAPE_RE, _reader_thread

ESC = "\x1b"


class _FakeStream:
    """最小流替身: 仅暴露可控的 ``isatty()``。"""

    def __init__(self, isatty: bool):
        self._isatty = isatty

    def isatty(self) -> bool:
        return self._isatty


# ---------------------------------------------------------------------------
# 防线 1: TTY 闸控
# ---------------------------------------------------------------------------
class TestShouldColorize:
    def test_tty_enables_color(self, monkeypatch):
        monkeypatch.delenv("NO_COLOR", raising=False)
        assert _should_colorize(_FakeStream(isatty=True)) is True

    def test_non_tty_disables_color(self, monkeypatch):
        """被管道捕获 / 重定向到文件 (非 TTY) → 不着色 (核心修复)。"""
        monkeypatch.delenv("NO_COLOR", raising=False)
        assert _should_colorize(_FakeStream(isatty=False)) is False

    def test_no_color_env_overrides_tty(self, monkeypatch):
        """遵循 NO_COLOR 事实标准: 即便是 TTY, 设了 NO_COLOR 也不着色。"""
        monkeypatch.setenv("NO_COLOR", "1")
        assert _should_colorize(_FakeStream(isatty=True)) is False

    def test_stream_without_isatty_is_safe(self, monkeypatch):
        """流无 isatty (如某些捕获对象) → 保守判为非终端, 不抛异常。"""
        monkeypatch.delenv("NO_COLOR", raising=False)
        assert _should_colorize(object()) is False


# ---------------------------------------------------------------------------
# _ColoredFormatter: use_color 双路径
# ---------------------------------------------------------------------------
class TestColoredFormatter:
    def _record(self, msg="hello") -> logging.LogRecord:
        return logging.LogRecord(
            name="probe", level=logging.INFO, pathname=__file__, lineno=1,
            msg=msg, args=(), exc_info=None,
        )

    def test_use_color_false_emits_no_ansi(self):
        out = _ColoredFormatter(use_color=False).format(self._record())
        assert ESC not in out

    def test_use_color_false_matches_file_formatter(self):
        """无色 console 路径必须与 setup_logging 里真实文件 handler 字节一致。

        镜像 setup_logging: 文件 handler = Formatter(_PLAIN_LINE_FMT,
        datefmt='%Y-%m-%d %H:%M:%S') 且 default_msec_format='%s.%03d';
        无色 console = _ColoredFormatter(同 datefmt, use_color=False)。两者
        对同一 record 必须产出逐字节相同的行 (orchestrator 捕获的无色子进程行
        与普通文件行无法区分)。
        """
        rec = self._record("一致性")
        colored_off = _ColoredFormatter(
            datefmt='%Y-%m-%d %H:%M:%S', use_color=False)
        file_fmt = logging.Formatter(
            _PLAIN_LINE_FMT, datefmt='%Y-%m-%d %H:%M:%S')
        file_fmt.default_msec_format = '%s.%03d'
        assert colored_off.format(rec) == file_fmt.format(rec)

    def test_use_color_true_emits_ansi(self):
        """着色路径 (交互式终端用) 仍须输出 ANSI —— 特性未被误删。"""
        out = _ColoredFormatter(use_color=True).format(self._record())
        assert ESC in out


# ---------------------------------------------------------------------------
# setup_logging: 非 TTY console 流 → 无色 formatter
# ---------------------------------------------------------------------------
def test_setup_logging_console_no_ansi_when_not_tty(tmp_path, monkeypatch):
    """stdout/stderr 非 TTY 时, setup_logging 的 console handler 不得着色。"""
    monkeypatch.delenv("NO_COLOR", raising=False)
    # pytest 下 sys.stdout 通常已是非 TTY 捕获对象; 显式断言 console handler 无色。
    logger = setup_logging("no_ansi_probe", str(tmp_path / "logs"))
    stream_handlers = [
        h for h in logger.handlers
        if isinstance(h, logging.StreamHandler)
        and not isinstance(h, logging.FileHandler)
    ]
    assert stream_handlers, "应至少有 stdout/stderr 两个 StreamHandler"
    rec = logging.LogRecord(
        name="no_ansi_probe", level=logging.INFO, pathname=__file__,
        lineno=1, msg="探针", args=(), exc_info=None,
    )
    for h in stream_handlers:
        # 在非 TTY 测试环境下, 任一 console handler 的格式化输出都不得含转义码。
        assert ESC not in h.formatter.format(rec)


def test_setup_logging_file_never_has_ansi(tmp_path):
    """文件 handler 落盘内容恒无 ANSI (即便消息体本身带转义码也只是普通字符)。"""
    log_dir = tmp_path / "logs"
    logger = setup_logging("file_probe", str(log_dir))
    logger.info("普通信息")
    logger.warning("警告信息")
    for h in logger.handlers:
        h.flush()
    text = (log_dir / "file_probe.log").read_text(encoding="utf-8")
    assert ESC not in text
    assert "普通信息" in text and "警告信息" in text


# ---------------------------------------------------------------------------
# 防线 2: orchestrator 捕获边界剥离 ANSI
# ---------------------------------------------------------------------------
class TestReaderThreadStripsAnsi:
    def test_regex_matches_real_color_codes(self):
        """正则须覆盖 _ColoredFormatter 实际产出的全部 SGR 序列。"""
        for code in ("\x1b[38;5;245m", "\x1b[0m", "\x1b[32m",
                     "\x1b[1;31m", "\x1b[36m", "\x1b[33m"):
            assert _ANSI_ESCAPE_RE.sub("", f"a{code}b") == "ab"

    def test_reader_thread_forwards_plain_text(self):
        """喂入带 ANSI 的子进程行, 转发到父 logger 的内容与尾缓冲均无转义码。"""
        colored = (
            "\x1b[38;5;245m2026-06-25 16:16:35\x1b[0m - "
            "\x1b[38;5;75m68_media_diversity\x1b[0m - "
            "\x1b[38;5;245mPID:24304\x1b[0m - \x1b[32mINFO\x1b[0m - 媒体多样性\n"
        )
        stream = io.StringIO(colored + "下一行无色\n")

        captured: list[str] = []

        class _Capture(logging.Handler):
            def emit(self, record):
                captured.append(record.getMessage())

        logger = logging.getLogger("reader_probe")
        logger.handlers.clear()
        logger.setLevel(logging.INFO)
        logger.addHandler(_Capture())
        logger.propagate = False

        from collections import deque
        acc: deque[str] = deque()
        _reader_thread(stream, logger, "│", acc, logging.INFO)

        joined = "\n".join(captured)
        assert ESC not in joined, "转发到父 logger 的文本仍含 ANSI"
        assert all(ESC not in line for line in acc), "尾缓冲仍含 ANSI"
        # 文本内容 (剥色后) 完整保留
        assert "68_media_diversity" in joined and "媒体多样性" in joined
        assert "下一行无色" in joined


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(pytest.main([__file__, "-v"]))
