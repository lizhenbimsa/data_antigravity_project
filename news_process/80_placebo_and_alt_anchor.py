"""80_placebo_and_alt_anchor.py — thin shim。

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
仅审计用 (audit-only) 流水线, 合并两项稳健性检验:
  - benefit_society_alt_anchor (J-L-M Appendix A 5 对替代锚点族)
  - benefit_society_placebo (4 业务线 + 1 中性过滤安慰剂)

只写单一产物 `data/processed/80_alt_anchor_and_placebo_panel.parquet`,
供下游 Stata 模板 (P2.S1, P2.A2) 消费。**不**修改主面板
`40_panel_yearly.parquet` 及其 golden snapshot。

详见底层模块 news_process/pipeline/features/benefit_society_audit_combined.py 的模块 docstring 末「阶段功能权威说明」段（摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md）。
"""

from __future__ import annotations

import pathlib
import sys

# F-5 (N15, 2026-07-18): sys.path 注入先于包导入 (81/82 同款) — 未 editable install 的
# 裸解释器直跑本 shim 也能解析 news_process 包; 注入必须在 from-import 之前才有效。
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

if __name__ == "__main__":
    from news_process.pipeline.features.benefit_society_audit_combined import main
    sys.exit(main())
