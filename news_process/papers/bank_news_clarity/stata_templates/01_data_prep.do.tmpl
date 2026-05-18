* news_process v3.7.0 — 第 11 篇 数据准备
*
* 输入: 49_risk_taking_outcomes.dta + bank_metadata.dta + 40_panel_yearly.dta
* (含 mean_clarity_score_{full,ctx} 等 v3.5.1 frozen 字段, 已在主 panel)

version 19
clear all

use "data/processed/49_risk_taking_outcomes.dta", clear
encode target_bank, gen(bank_id)
xtset bank_id year

capture merge m:1 target_bank using "data/processed/bank_metadata.dta", ///
    keep(master match) nogen

* Merge clarity treatment from main panel (v3.5.1 已 frozen mean_clarity_score)
capture merge 1:1 target_bank year using "data/processed/40_panel_yearly.dta", ///
    keep(master match) nogen ///
    keepusing(mean_clarity_score_full mean_clarity_score_ctx ///
              mean_frac_definite_full mean_frac_definite_ctx ///
              frac_amb_articles_full frac_amb_articles_ctx ///
              mean_num_intensity_full mean_num_intensity_ctx)
if _rc != 0 {
    display "WARNING: 40_panel_yearly.dta 不可读 — main treatment 不可用"
}

capture confirm variable ln_assets
if _rc != 0 & "total_assets" != "" {
    gen ln_assets = ln(total_assets) if total_assets > 0
}

* 第 11 篇额外: term_spread (10y - 1y 国债利差)
capture confirm variable term_spread
if _rc != 0 {
    gen term_spread = .   // placeholder; user 自行 merge 国债 yield curve
}

sort bank_id year
save "data/processed/_paper11_working.dta", replace
display "  Working dataset saved: data/processed/_paper11_working.dta"
