"""news_process.papers._common.pipeline_runner — 主流水线调用桥接.

Phase 9b: 替代 5 个 paper analysis.py 中复制 5 份的
``_run_pipeline_via_existing_orchestrator()`` 反射加载块.

恢复 Phase 2a (commit 722bc0e) 的 reflection-purge 不变式 (限生产代码) —
``run_pipeline_function`` 在 v2.0 起属于 ``news_process`` 真包 (由
``pyproject.toml`` setuptools.packages.find 识别), 走规范包导入即可.
``tests/integration/test_dag_consistency.py:37`` 的 spec_from_file_location
属测试有意隔离设计, 不在本子任务范围.

延迟 import (函数体内) 是有意设计: 让 ``papers.<id>.analysis`` 的
import-time 不依赖 ``run_pipeline_function`` 的成功加载 — 例如
``--stage tables`` / ``--stage figures`` 路径不需要触发 pipeline 模块级
副作用 (CONFIG / setup_logging / PipelineLock / generate_run_id).
"""

from __future__ import annotations


def run_main_pipeline(argv: list[str] | None = None) -> None:
    """调用 ``run_pipeline_function.run_pipeline()`` (规范包导入).

    与 ``python news_process/run_pipeline_function.py`` 等价, 但走规范
    包导入路径, 让静态分析器 / IDE 能正确跟随符号. 第一次调用触发
    模块级初始化 (load_config / setup_logging / PipelineLock); 后续
    调用复用 sys.modules 缓存 (与原反射设计的多次重载相比, 更省时).
    """
    # A10 修复 (2026-07-09 五入口诊断): 接受 argv 透传流水线 flag(如 --skip-21-if-exists)。argv 为空/None
    # → run_pipeline() 零参(保持 test_pipeline_runner_bridge 的 assert_called_once_with() 向后兼容);
    # 非空 → 经 run_pipeline 的 strict _parse_cli_args 转 Namespace(拼错 flag 在管道层 SystemExit fail-loud)。
    from news_process.run_pipeline_function import _parse_cli_args, run_pipeline
    if argv:
        run_pipeline(_parse_cli_args(argv))
    else:
        run_pipeline()
