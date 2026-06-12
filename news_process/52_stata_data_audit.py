"""52_stata_data_audit.py — CLI 适配层 shim (Phase 7a-8 迁移后).

实现正文已迁至 ``news_process.pipeline.audit.stata_audit:main``。
为向后兼容 ``python news_process/52_stata_data_audit.py`` 外部 CLI 契约保留;
**不在 STAGES_MAIN/STAGES_VALIDATION 中, 编排器不会触发**
(见 ``news_process/core/schemas.py:156`` 显式排除注释)。

由用户按需手动调用 (Stata 导出后数据审计); 推荐入口:
    python -m news_process.pipeline.audit.stata_audit
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stata_audit import main
    main()
