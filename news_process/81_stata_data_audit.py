"""81_stata_data_audit.py — CLI 适配层 shim (Phase 7a-8 迁移后).

实现正文已迁至 ``news_process.pipeline.audit.stata_audit:main``。
为向后兼容 ``python news_process/81_stata_data_audit.py`` 外部 CLI 契约保留;
**不在 STAGES_MAIN/STAGES_VALIDATION 中, 编排器不会触发**
(见 ``news_process/core/schemas.py:160`` 显式排除注释)。

由用户按需手动调用 (Stata 导出后数据审计); 推荐入口:
    python -m news_process.pipeline.audit.stata_audit

详见底层模块 news_process/pipeline/audit/stata_audit.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stata_audit import main
    sys.exit(main())
