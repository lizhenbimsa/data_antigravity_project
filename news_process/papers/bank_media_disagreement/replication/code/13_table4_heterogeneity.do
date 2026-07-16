* news_process v3.7.0 — 第 10 篇 Table 4: 按 implicit_guarantee_tier (隐性担保层级) 的异质性
*
* V4 F2.2 boundary condition + F-P1.1 implicit guarantee 5-tier 异质性
* Tier 5 (国有大行 + 政策性): channel 弱 (LOLR 主导)
* Tier 4 (D-SIB 股份制): channel 中
* Tier 3-1 (其他): channel 强 (market discipline 起作用)

version 19
clear all
set maxvar 32767

* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
* (stage 49 已移除; outcome 待财务面板接入)
capture confirm file "data/processed/49_risk_taking_outcomes.dta"
if _rc {
    display as error "============================================================"
    display as error "[复现暂不可跑] stage 49 (risk_taking_outcomes) 已于 2026-06-12 整体移除:"
    display as error "  其结果变量 (z_score / npl_formation / rwa_to_ta) 依赖银行财务面板, 该数据尚未接入;"
    display as error "  本 provisional 论文复现包待财务面板 onboarding 后方可跑通 (详见 README / CLAUDE.md)。"
    display as error "============================================================"
    exit 198
}
use "data/processed/49_risk_taking_outcomes.dta", clear
encode target_bank, gen(bank_id)
xtset bank_id year
merge m:1 target_bank using "data/processed/bank_metadata.dta", keep(match master) nogen

local DV     z_score
local TX     cross_outlet_tone_variance_full
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

* ── fail-loud guard fix(omni-g-zscore-papers-04, 2026-06-11) ─────────────
* stage 49 导出的 49_risk_taking_outcomes.dta 仅含 outcome 列, 不含 treatment/
* controls; 缺列时给可读报错并指明数据装配点, 不再让 Panel A 直接 r(111)。
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
    display as error "  data/processed/_paper10_working.dta), 再将本脚本 use 行指向"
    display as error "  该 working dataset; 或自行 merge 上述缺失列后重跑。"
    error 111
}

* ── Panel A: 按隐性担保层级 (tier) 分样本 ────────────────────────────────
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

* ── Panel B: 分时段 (regime 切换, V4 F-Comp.3) ───────────────────────────
local PERIODS "2007-2011 2012-2015 2016-2019 2020-2025"
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
    mtitles("2007-2011" "2012-2015" "2016-2019" "2020-2025") ///
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

* ── Panel D: 正式分时代稳定性 (era×treatment 交乘 + Wald 跨时代相等检验; CY-2-PARTIAL 修复 2026-06-15) ──
* 3 时代 (2007-2012 / 2013-2018 / 2019-2025, 与 8 篇 fully-coded era-stability 一致), 镜像
* 34_tableA11: Panel B 已做分段回归, 此处补【正式跨时代斜率相等 Wald 检验】(主效应在三时代
* 间是否稳定 = 跨年制度变迁稳健性)。capture 守卫: 单一时代在场 (T<3 试跑盘) 优雅跳过, 全量 T=19 激活。
capture {
    gen byte era = .
    replace era = 1 if year >= 2007 & year <= 2012
    replace era = 2 if year >= 2013 & year <= 2018
    replace era = 3 if year >= 2019 & year <= 2025
    quietly levelsof era if !missing(`DV', `TX'), local(eras_present)
    local n_eras : word count `eras_present'
    if `n_eras' >= 2 {
        eststo era_interact: reghdfe `DV' c.`TX'##i.era `CTRL_B' `CTRL_Y', ///
            absorb(bank_id year) vce(cluster bank_id year)
        capture testparm c.`TX'#i.era
        if !_rc {
            scalar era_wald_F = r(F)
            scalar era_wald_p = r(p)
            display "  [era-stability] Wald 跨时代斜率相等 F=" r(F) " p=" r(p)
            estadd scalar era_wald_p = r(p)
        }
        esttab era_interact ///
            using "papers/bank_media_disagreement/output/table4d_era_stability.tex", ///
            replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) b(%9.4f) se(%9.4f) ///
            title("Table 4 Panel D: Era-Stability (treatment-by-era interaction; CY-2)") ///
            stats(N r2 era_wald_p, fmt(0 3 3) labels("N" "R2" "Wald cross-era p")) ///
            addnotes("Eras: 2007-2012 / 2013-2018 / 2019-2025, chosen ex ante to align with China FinTech policy phases (2013 互联网金融元年/余额宝; 2019 DCEP 强监管), NOT data-driven breaks; cross-era stability assessed via Wald slope-equality, cf. Hansen 2001 JEP on structural-change inference; for data-driven break dates see Bai-Perron 1998 ECMA / optional xtbreak diagnostic." ///
                     "Wald cross-era p tests equal treatment slopes across eras; pooled era-by-treatment interaction on the full bank-year panel.")
        eststo clear
    }
    else {
        display "  [era-stability] 单一时代在场 (T<3 试跑盘), Panel D 优雅跳过 (全量 T=19 自动激活)"
    }
    drop era
}
if _rc display as error "  [WARN] Panel D era-stability 跳过 (rc=`=_rc'); 续跑"
