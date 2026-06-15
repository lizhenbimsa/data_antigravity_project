"""53_export_stats_excel.py — CLI 适配层 shim (Phase 1.4b 迁移 pilot 后).

实现正文已迁至 ``news_process.pipeline.audit.stats_excel:main``。
为向后兼容 ``python news_process/53_export_stats_excel.py`` 外部 CLI 契约保留;
**不在 STAGES_MAIN/STAGES_VALIDATION 中, 编排器不会触发**
(见 ``news_process/core/schemas.py:156`` 显式排除注释)。

由用户按需手动调用 (导出描述性统计 Excel); 推荐入口:
    python -m news_process.pipeline.audit.stats_excel

详见底层模块 news_process/pipeline/audit/stats_excel.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""

import pathlib
import sys

# 将项目父目录置于 sys.path, 使任意 cwd 下 ``import news_process`` 均可解析。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


if __name__ == "__main__":
    from news_process.pipeline.audit.stats_excel import main
    main()
