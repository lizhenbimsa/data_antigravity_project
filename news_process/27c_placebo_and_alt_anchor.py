"""27c_placebo_and_alt_anchor.py — thin shim。

V2.0 J-L-M 2026 robustness alignment plan §3 Phase 1 P1.6:
仅审计用 (audit-only) 流水线, 合并两项稳健性检验:
  - benefit_society_alt_anchor (J-L-M Appendix A 5 对替代锚点族)
  - benefit_society_placebo (4 业务线 + 1 中性过滤安慰剂)

只写单一产物 `data/processed/27c_alt_anchor_and_placebo_panel.parquet`,
供下游 Stata 模板 (P2.S1, P2.A2) 消费。**不**修改主面板
`40_panel_yearly.parquet` 及其 golden snapshot。
"""

from __future__ import annotations

import sys

from news_process.pipeline.features.benefit_society_audit_combined import main

if __name__ == "__main__":
    sys.exit(main())
