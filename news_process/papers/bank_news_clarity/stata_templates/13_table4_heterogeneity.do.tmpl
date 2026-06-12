* news_process v3.7.0 — 第 11 篇 Table 4: 异质性分析 (本模板实际落地 Panel A-D 四维度)
*
* V4 F2.2 边界条件 (boundary condition):
* Panel A: implicit_guarantee_tier 隐性担保层级 (Acharya 2016 RFS, 5 档)
* Panel B: 上市 vs 非上市 (listed; V4 F-P1.3)
* Panel C: 分时段 regime 切换 (V4 F-Comp.3)
* Panel D: 剔除 top 6 国有大行 (V4 F-P1.2)

version 19
clear all
set maxvar 32767

* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
use "data/processed/49_risk_taking_outcomes.dta", clear
encode target_bank, gen(bank_id)
xtset bank_id year
merge m:1 target_bank using "data/processed/bank_metadata.dta", keep(match master) nogen

local DV     z_score
local TX     mean_clarity_score_ctx
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

* ── fail-loud guard fix(omni-g-zscore-papers-04, 2026-06-11) ─────────────
* stage 49 导出的 49_risk_taking_outcomes.dta 仅含 outcome 列, 不含 treatment/
* controls; 缺列时给可读报错并指明数据装配点, 不再让 Panel A 直接 r(111)。
* (listed 单独在 Panel B 守卫: 缺失时跳过该 panel 而非整表崩溃。)
local REQUIRED_VARS `DV' `TX' `CTRL_B' `CTRL_Y' implicit_guarantee_tier
local MISSING_VARS ""
foreach v of local REQUIRED_VARS {
    capture confirm variable `v'
    if _rc != 0 local MISSING_VARS "`MISSING_VARS' `v'"
}
if "`MISSING_VARS'" != "" {
    display as error "Table 4 缺失变量:`MISSING_VARS'"
    display as error "原因: 49_risk_taking_outcomes.dta 仅含 stage 49 outcome 列。"
    display as error "修复: 先跑 01_data_prep.do (merge 40_panel_yearly.dta 生成"
    display as error "  data/processed/_paper11_working.dta), 再将本脚本 use 行指向"
    display as error "  该 working dataset; 或自行 merge 上述缺失列后重跑。"
    error 111
}

* ── Panel A: 按隐性担保层级 (tier) 分样本 ────────────────────────────────
forvalues t = 1/5 {
    eststo A_tier`t': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
        if implicit_guarantee_tier == `t', ///
        absorb(bank_id year) vce(cluster bank_id year)
}

esttab A_tier1 A_tier2 A_tier3 A_tier4 A_tier5 ///
    using "papers/bank_news_clarity/output/table4_panel_A_tier.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel A: Clarity Effect by Implicit Guarantee Tier") ///
    mtitles("Tier 1" "Tier 2" "Tier 3" "Tier 4 (D-SIB)" "Tier 5 (TBTF)") ///
    keep(`TX')

eststo clear

* ── Panel B: 上市 vs 非上市 (listed) ─────────────────────────────────────
* fix(omni-g-zscore-papers-04, 2026-06-11): listed 是幻影列 — stage 49 输出 /
* bank_metadata / 40_panel 均不产出, 需外部上市状态数据。缺失时可读警告 + 跳过
* Panel B (其余 panel 不受影响), 不再 r(111) 崩整个 do-file。
capture confirm variable listed
if _rc != 0 {
    display as error "WARNING: 变量 listed 不存在 (管道任何数据源均不产出," ///
        " 需外部上市状态数据) — Table 4 Panel B 跳过。"
}
else {
    eststo B_listed: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' if listed == 1, ///
        absorb(bank_id year) vce(cluster bank_id year)
    eststo B_unlisted: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' if listed == 0, ///
        absorb(bank_id year) vce(cluster bank_id year)

    esttab B_listed B_unlisted ///
        using "papers/bank_news_clarity/output/table4_panel_B_listed.tex", ///
        replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
        b(%9.4f) se(%9.4f) ///
        title("Table 4 Panel B: Listed vs Non-Listed") ///
        mtitles("Listed (n ≈ 60)" "Non-Listed (n ≈ 440)") ///
        keep(`TX')

    eststo clear
}

* ── Panel C: 分时段 (sub-period) ─────────────────────────────────────────
* v3.7.0 (M17 修复): 用更可靠的 foreach 写法替代嵌套 backtick eval
local i = 0
foreach range in "2007 2011" "2012 2015" "2016 2019" "2020 2024" {
    local ++i
    local lo = word("`range'", 1)
    local hi = word("`range'", 2)
    eststo C_p`i': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
        if year >= `lo' & year <= `hi', ///
        absorb(bank_id year) vce(cluster bank_id year)
}

esttab C_p1 C_p2 C_p3 C_p4 ///
    using "papers/bank_news_clarity/output/table4_panel_C_period.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel C: Sub-Period Heterogeneity") ///
    mtitles("2007-2011" "2012-2015" "2016-2019" "2020-2024") ///
    keep(`TX')

eststo clear

* ── Panel D: drop top 6 国有大行 ─────────────────────────────────────────
eststo D_full: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)
eststo D_drop6: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' if implicit_guarantee_tier < 5, ///
    absorb(bank_id year) vce(cluster bank_id year)

esttab D_full D_drop6 ///
    using "papers/bank_news_clarity/output/table4_panel_D_drop_top6.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 4 Panel D: Drop Top 6 国有大行 Robustness") ///
    mtitles("Full Sample" "Drop Top 6 (Tier 5)") ///
    keep(`TX')

eststo clear
