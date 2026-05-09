"""Plan-r3 P1-8: 6 个历史无单元测试 stage 的 import + main() smoke 测试.

历史空白
--------
截至 v2.1.x post-recode round 2, 以下 6 个 stage 的 backing module 既无
专门 ``test_<sid>_*.py``, 在其它测试中也无内容引用, 即处于 *零测试覆盖* 状态:

    sid               backing module
    ────────────────  ───────────────────────────────────────────────
    30                news_process.validation.text2vec
    32a               news_process.validation.dedup_threshold
    38                news_process.validation.media_diversity
    38a               news_process.validation.temporal_mask
    52                news_process.pipeline.audit.stata_audit
    53                news_process.pipeline.audit.stats_excel

本文件提供两类最低限度保护:

1. ``test_<short>_module_importable`` — 模块本身可 import (无 import-time
   副作用 / 顶层数据 I/O / 循环依赖崩溃).
2. ``test_<short>_main_callable`` — 模块暴露 ``main`` 可调用对象
   (CLI 入口契约: 上层 ``run_pipeline_*`` 与 thin shim 都依赖此契约).

不做端到端跑 stage 的强测试 (那需要构造合成上游 parquet 输入, 体量大);
但任何 import 失败 / 顶层 KeyError / 拼写错误都会立刻被 CI 抓到, 这是
v2.1.x 之前完全没有的保护.
"""

from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest

# Phase 5a: 注入 news_process 父目录, 确保 ``news_process.*`` 可解析.
_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


# ----------------------------------------------------------------------------
# stage_id → backing module (与 news_process/<sid>_*.py thin shim 一一对应).
# ----------------------------------------------------------------------------

UNTESTED_STAGES: dict[str, str] = {
    "stage30":  "news_process.validation.text2vec",
    "stage32a": "news_process.validation.dedup_threshold",
    "stage38":  "news_process.validation.media_diversity",
    "stage38a": "news_process.validation.temporal_mask",
    "stage52":  "news_process.pipeline.audit.stata_audit",
    "stage53":  "news_process.pipeline.audit.stats_excel",
}


@pytest.mark.parametrize("short, dotted", sorted(UNTESTED_STAGES.items()))
def test_module_importable(short: str, dotted: str) -> None:
    """backing module 可 import (无 import-time 副作用崩溃)."""
    mod = importlib.import_module(dotted)
    assert mod.__name__ == dotted


@pytest.mark.parametrize("short, dotted", sorted(UNTESTED_STAGES.items()))
def test_module_exposes_main(short: str, dotted: str) -> None:
    """backing module 必须暴露可调用的 ``main`` (CLI 入口契约)."""
    mod = importlib.import_module(dotted)
    main = getattr(mod, "main", None)
    assert main is not None, (
        f"{dotted} 缺少 main; thin shim {short[5:]}_*.py 的 "
        f"``from {dotted} import main`` 会 ImportError"
    )
    assert callable(main), f"{dotted}.main 不可调用 (type={type(main).__name__})"
