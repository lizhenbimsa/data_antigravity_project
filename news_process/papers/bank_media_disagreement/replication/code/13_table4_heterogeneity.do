* news_process v3.7.0 — 第 10 篇 Table 4: Heterogeneity by implicit_guarantee_tier
*
* V4 F2.2 boundary condition + F-P1.1 implicit guarantee 5-tier 异质性
* Tier 5 (国有大行 + 政策性): channel 弱 (LOLR 主导)
* Tier 4 (D-SIB 股份制): channel 中
* Tier 3-1 (其他): channel 强 (market discipline 起作用)

version 19
clear all
set maxvar 32767

* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
use "data/processed/49_risk_taking_outcomes.dta", clear
encode target_bank, gen(bank_id)
xtset bank_id year
merge m:1 target_bank using "data/processed/bank_metadata.dta", keep(match master) nogen

local DV     z_score
local TX     cross_outlet_tone_variance_full
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

* ── Panel A: Sample split by tier ────────────────────────────────────────
forvalues t = 1/5 {
    eststo tier`t': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
        if implicit_guarantee_tier == `t', ///
        absorb(bank_id year) vce(cluster bank_id year)
}

esttab tier1 tier2 tier3 tier4 tier5 ///
    using "papers/bank_media_disagreement/output/table4_heterogeneity_tier.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel A: Heterogeneity by Implicit Guarantee Tier") ///
    mtitles("Tier 1 (Lowest)" "Tier 2" "Tier 3" "Tier 4 (D-SIB)" "Tier 5 (TBTF)") ///
    keep(`TX')

eststo clear

* ── Panel B: Sub-period (regime shift, V4 F-Comp.3) ──────────────────────
local PERIODS "2007-2011 2012-2015 2016-2019 2020-2024"
local i = 0
foreach p of local PERIODS {
    local ++i
    local y_lo = real(substr("`p'", 1, 4))
    local y_hi = real(substr("`p'", 6, 4))
    eststo period`i': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
        if year >= `y_lo' & year <= `y_hi', ///
        absorb(bank_id year) vce(cluster bank_id year)
}

esttab period1 period2 period3 period4 ///
    using "papers/bank_media_disagreement/output/table4_heterogeneity_period.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel B: Sub-Period Heterogeneity (Regime Shift)") ///
    mtitles("2007-2011" "2012-2015" "2016-2019" "2020-2024") ///
    keep(`TX')

eststo clear

* ── Panel C: Drop top 6 国有大行 (V4 F-P1.2 robustness) ──────────────────
eststo full_sample: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

eststo drop_top6: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' if implicit_guarantee_tier < 5, ///
    absorb(bank_id year) vce(cluster bank_id year)

esttab full_sample drop_top6 ///
    using "papers/bank_media_disagreement/output/table4_heterogeneity_drop_top6.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel C: Drop Top 6 国有大行 Robustness") ///
    mtitles("Full Sample" "Drop Top 6 (Tier 5)") ///
    keep(`TX')

eststo clear
