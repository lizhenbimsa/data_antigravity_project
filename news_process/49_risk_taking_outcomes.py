"""Thin shim for stage 49 risk_taking_outcomes (V4 DC2 + C2 deliverable).

v3.7.0: 加载 banking outcome dry-run / full acquisition 输出 + 合并到 panel.
生成 49_risk_taking_outcomes.parquet (bank-year × outcome 字段) 供第 10/11 篇
risk-taking 主回归使用.

Outcome 字段 (per paper_spec.yaml::outcome):
    z_score:                  (ROA + CAR) / σ(ROA, 5y rolling)
    npl_formation_rate:       (NPL_t - NPL_{t-1} + writeoffs_t) / Loan_{t-1}
    rwa_to_ta_ratio:          RWA / Total Assets
    sigma_roa_5y_rolling:     5-year rolling std(ROA)
    loan_loss_provision_discretion: Bushman-Williams 2012 JAE direct match

Delegates to news_process.pipeline.panel.risk_taking_outcomes.main().
"""
from news_process.pipeline.panel.risk_taking_outcomes import main

if __name__ == '__main__':
    main()
