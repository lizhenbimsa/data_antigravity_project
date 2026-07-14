"""
tests/test_prompt_audit_s2_s12.py — S2/S12 专属断言
======================================================

背景 (PROMPT_ASSETS_AUDIT_EXECUTION_PLAN_2026-07-12.md §2 表 S2/S12 行 + §12
台账 + §6-7 验收标准"批次 D 各代码项须各配 ≥1 条专属断言"):

- S2: ``LLMs_for_FinTech_dic/00_LLMs_for_dic.py`` 词表判别阈值由
  ``>= len(JUDGE_MODELS)*0.5``（=≥4，含平票）收紧为 ``> len(JUDGE_MODELS)*0.5``
  （严格多数=≥5/8），对齐发表词表 1506 实证口径。
- S12①: 同文件 :599 附近 ``int(item.get("score", 0))`` 裸转换在 LLM 返回畸形
  score（非数字/None/list 等）时会 ValueError/TypeError 炸穿整个判别主循环，
  改为 try/except 记 warning 并跳过坏项。
- S12②: ``LLMs_for_FinTech_dic/02_analyze_log.py`` 的生成阶段失败正则漏计
  "达到最大重试次数，任务失败"（00_LLMs_for_dic.py:449）一类失败信息，且
  多处硬编码 ``/26``（历史领域数）与实际 ``DOMAINS`` 长度（现为 1）不符，
  已改用 ``len(DOMAINS)`` 动态取值。
- S12③: ``LLMs_for_FinTech_dic/config.py`` 中 "26 个领域" 的写死注释已改为
  动态措辞。

⚠ 设计约束 (§6-7 + 任务纪律): ``LLMs_for_FinTech_dic/`` 不在 pytest
testpaths 且有独立缓存/离线开关 ``LLMS_DIC_OFFLINE``。00_LLMs_for_dic.py 在
模块顶层会创建独立 SQLite LLM 缓存文件（``LLMCache(CACHE_DB_FILE)``）并注册
SIGINT 信号处理器 —— 这些对单测而言都是不必要的真实副作用。因此本文件
**绝不 import** 00_LLMs_for_dic.py / 02_analyze_log.py 这两个脚本模块本体，
全部断言改用纯文本读取 + 正则提取（结构断言），仅 test (c) 对提取出的最小
代码片段做沙盒 ``exec``（不触发任何 API 调用、不写任何缓存/磁盘文件）。这是
计划 §6-7 明确允许的"源码结构断言"与行为验证的折衷方案，非对完整模块的
集成测试——若未来两文件结构大改，本文件的正则/切片锚点需同步更新。
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path
from typing import Callable

import pytest

pytestmark = pytest.mark.fast

_NEWS_PROCESS_DIR = Path(__file__).resolve().parent.parent
_DIC_DIR = _NEWS_PROCESS_DIR / "LLMs_for_FinTech_dic"
_MAIN_SRC_PATH = _DIC_DIR / "00_LLMs_for_dic.py"
_LOG_SRC_PATH = _DIC_DIR / "02_analyze_log.py"
_CONFIG_SRC_PATH = _DIC_DIR / "config.py"


def _read(path: Path) -> str:
    assert path.exists(), f"源文件缺失，S2/S12 断言基础不成立: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# (a) S2: 词表阈值严格多数 (> 而非 >=)
# ---------------------------------------------------------------------------

def test_s2_threshold_is_strict_majority():
    """S2: judge_ok_set 的阈值须为严格 `>`（=≥5/8），不得回退为 `>=`（=≥4/8 含平票）。"""
    src = _read(_MAIN_SRC_PATH)
    m = re.search(
        r'df_final\["total_score"\]\s*(>=|>)\s*len\(JUDGE_MODELS\)\s*\*\s*0\.5',
        src,
    )
    assert m is not None, "未找到 judge_ok_set 阈值比较表达式，源码结构已变化"
    assert m.group(1) == ">", (
        f"阈值回退为 {m.group(1)!r}（含平票）—— S2 要求严格多数 '>' "
        "（对齐发表词表 1506 实证口径），防止未来无意中改回宽松阈值"
    )
    assert "fix(S2" in src, "S2 阈值改动缺 fix-tag 注释（§0-5 纪律）"
    # 阈值不进 LLM 缓存键的口径声明也须同批留痕（防后人误以为要清缓存重跑）
    assert "不进" in src and "缓存键" in src, "S2 缺'阈值不进缓存键'的口径声明"


# ---------------------------------------------------------------------------
# (b) S12②: 02_analyze_log.py 失败正则须能捕获"达到最大重试次数"型失败
# ---------------------------------------------------------------------------

def test_s12_fail_regex_catches_max_retries_message():
    """
    S12②: 原正则要求 "]" 后紧跟 "失败" 二字，漏计 00_LLMs_for_dic.py:449 的
    "达到最大重试次数，任务失败"（"]" 与 "失败" 之间夹了"达到最大重试次数，
    任务"字样）一类失败信息。修复后须放宽为可跨中间文本匹配，且不能误吞
    成功行。
    """
    src = _read(_LOG_SRC_PATH)
    m = re.search(r'm_fail\s*=\s*re\.search\(\s*r"([^"]+)"', src)
    assert m is not None, "未找到 02_analyze_log.py 的 m_fail 正则定义，源码结构已变化"
    pattern = m.group(1)
    compiled = re.compile(pattern)

    # 回归样例: 曾经能匹配的"]"紧邻"失败"格式，修复后必须仍能匹配（不破坏既有覆盖）
    legacy_ok_line = (
        "[2026-07-14 10:00:00] [ERROR] "
        "[任务 gpt-5.2/金融科技 (3)] 失败：解析重试 100 次后仍未提取到关键词列表"
    )
    assert compiled.search(legacy_ok_line) is not None, "修复后不应丢失原本已覆盖的失败格式"

    # 本次要修的样例: 00_LLMs_for_dic.py:449 的真实日志格式
    max_retries_line = (
        "[2026-07-14 10:00:01] [ERROR]   "
        "[任务 gpt-5.2/金融科技 (3)] 达到最大重试次数，任务失败"
    )
    assert compiled.search(max_retries_line) is not None, (
        "S12 未修复: 失败正则仍漏计'达到最大重试次数'型失败，"
        "会导致 total_gen_fail 统计低估"
    )

    # 反例: 纯成功行不应被误判为失败 (防正则放宽过度、误吞其他行)
    success_line = "[2026-07-14 10:00:02] [INFO] [任务 gpt-5.2/金融科技 (3)] 成功获取 42 个词"
    assert compiled.search(success_line) is None, "放宽后的正则不应误吞成功行"

    assert "fix(S12" in src, "S12 正则改动缺 fix-tag 注释（§0-5 纪律）"


def test_s12_analyze_log_uses_dynamic_domain_count():
    """S12②(续): 硬编码 `/26`（历史领域数）须改为 `len(DOMAINS)` 动态取值。"""
    src = _read(_LOG_SRC_PATH)
    assert "DOMAINS" in src.split("\n\n", 1)[0] or re.search(
        r"from config import [^\n]*DOMAINS", src
    ), "02_analyze_log.py 未导入 DOMAINS，无法动态取领域数"
    # 精确匹配曾经的两种硬编码模式（f-string 内 "}/26" 与裸文本 "26个领域"），
    # 不误伤 fix-tag 注释里作为历史记录出现的 "/26" 字样。
    assert not re.search(r"\}/26\b", src), "S12②: 仍残留 f-string 内硬编码 /26"
    assert "26个领域" not in src, "S12②: 仍残留硬编码文本 '26个领域'"
    assert "len(DOMAINS)" in src, "S12②: 未见 len(DOMAINS) 动态用法"


def test_s12_config_comment_no_longer_hardcodes_domain_count():
    """S12③: config.py 中 DOMAINS 定义上方的注释不得再写死"26 个领域"。"""
    src = _read(_CONFIG_SRC_PATH)
    m = re.search(r"# 领域定义.*?\n(?:#.*\n)*", src)
    assert m is not None, "未找到 DOMAINS 定义上方的注释块，源码结构已变化"
    comment_block = m.group(0)
    assert "26 个领域" not in comment_block, (
        "S12③: 注释仍写死'26 个领域'，应改动态措辞或实测数"
    )
    assert "len(DOMAINS)" in comment_block or "DOMAINS" in comment_block, (
        "S12③: 注释未提及以 DOMAINS 实际长度为准"
    )


# ---------------------------------------------------------------------------
# (c) S12①: 00_LLMs_for_dic.py:599 坏 score 项不炸穿判别主循环
# ---------------------------------------------------------------------------

class _StubLogger:
    """最小 logger 替身：只记录 warning 调用次数与内容，不落盘不触发真实 logging。"""

    def __init__(self) -> None:
        self.warnings: list[str] = []

    def warning(self, msg: str) -> None:
        self.warnings.append(msg)


def _extract_result_map_block(src: str) -> str:
    """
    从源码中截取 "for item in results_list: ... result_map[kw] = (sc, rs)"
    这一段（S12①修复现场），保留原始缩进供后续 dedent。见模块 docstring 关于
    "为何不直接 import 00_LLMs_for_dic.py" 的局限声明。
    """
    start_marker = "for item in results_list:"
    end_marker = "result_map[kw] = (sc, rs)"
    start = src.index(start_marker)
    end = src.index(end_marker, start) + len(end_marker)
    return src[start:end]


def _build_extracted_function(block: str) -> Callable:
    """把截取出的代码片段包装成可调用函数，在隔离命名空间内 exec（无 import、无 IO）。"""
    dedented = textwrap.dedent(block)
    body = textwrap.indent(dedented, "    ")
    func_src = (
        "def _run(results_list, logger, task_id):\n"
        "    result_map = {}\n"
        f"{body}\n"
        "    return result_map\n"
    )
    namespace: dict = {}
    exec(compile(func_src, "<s12_extracted_block>", "exec"), namespace)  # noqa: S102
    return namespace["_run"]


def test_s12_result_map_block_has_try_except_guard():
    """结构断言: int(item.get('score', 0)) 的转换必须被 try/except(TypeError, ValueError) 包裹。"""
    src = _read(_MAIN_SRC_PATH)
    block = _extract_result_map_block(src)
    assert "try:" in block and "except" in block, (
        "S12①: int(item.get('score', 0)) 附近未见 try/except，坏项仍会炸穿判别主循环"
    )
    assert re.search(
        r"except\s*\((?:TypeError,\s*ValueError|ValueError,\s*TypeError)\)", block
    ), "S12①: except 子句未显式捕获 (TypeError, ValueError)"
    assert "fix(S12" in block, "S12①改动缺 fix-tag 注释（§0-5 纪律）"


def test_s12_bad_score_item_is_skipped_not_raised():
    """行为断言: 对提取出的真实代码片段做沙盒执行——坏 score 项须被跳过而非 raise，好项正常入 result_map。"""
    src = _read(_MAIN_SRC_PATH)
    block = _extract_result_map_block(src)
    run = _build_extracted_function(block)

    logger = _StubLogger()
    results_list = [
        {"keyword": "好词", "score": "3", "reason": "正常"},
        {"keyword": "坏词-非数字", "score": "abc", "reason": "畸形"},
        {"keyword": "坏词-None", "score": None, "reason": "畸形2"},
        {"keyword": "坏词-列表", "score": [1, 2], "reason": "畸形3"},
    ]

    # 核心断言: 不应 raise（修复前的裸 int() 会在第二个坏项上直接 ValueError 炸穿循环）
    result_map = run(results_list, logger, "unit-test-task")

    assert result_map.get("好词") == (3, "正常"), "正常项应正确解析入 result_map"
    assert "坏词-非数字" not in result_map, "坏 score 项不应被塞入 result_map（应跳过）"
    assert "坏词-None" not in result_map
    assert "坏词-列表" not in result_map
    assert len(logger.warnings) == 3, f"应对 3 条坏项各记 1 条 warning，实得 {len(logger.warnings)}"
