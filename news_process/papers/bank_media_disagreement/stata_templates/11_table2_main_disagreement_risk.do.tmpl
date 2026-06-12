* news_process v3.7.0 — 第 10 篇 Table 2: Disagreement → Risk-Taking 主回归 M1-M6
*
* Treatment (DC1 path B = SSRN + _full main):
*   DV  = z_score   (CAR-based Z-score 变体, cf. Laeven-Levine 2009 JFE;
*         fix(omni-g-zscore-papers-01, 2026-06-11): 资本项=监管 Basel CAR 非
*         L&L 原版账面 equity/assets, 见 paper_spec.yaml outcome 更正)
*   TX  = cross_outlet_tone_variance_full   (V4 R3 critical 修复, M2-M3 新建字段)
*
* M1-M6 progressive (V4 F2.2 boundary condition + F-P1.1 implicit guarantee):
*   M1: 主解释 only
*   M2: + Bank FE
*   M3: + Bank FE + Year FE
*   M4: + bank controls (ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth)
*   M5: + year controls (gdp_growth, m2_growth, shibor)
*   M6: + SOE × TX 交互 (Acharya 2016 RFS implicit guarantee 框架)

version 19
clear all
set maxvar 32767
set linesize 120

* 加载共享 outcome panel (stage 49 输出)
* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
use "data/processed/49_risk_taking_outcomes.dta", clear

* xtset 声明 panel
encode target_bank, gen(bank_id)
xtset bank_id year

* 加载 bank metadata (is_soe, bank_type_id, tier from bank_list.yaml)
merge m:1 target_bank using "data/processed/bank_metadata.dta", keep(match master) nogen

* 主变量
local DV     z_score
local TX     cross_outlet_tone_variance_full
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

* ── fail-loud guard fix(omni-g-zscore-papers-04, 2026-06-11) ─────────────
* stage 49 导出的 49_risk_taking_outcomes.dta 仅含 outcome 列
* (risk_taking_outcomes.py::OUTPUT_OUTCOME_COLS), 不含任何 treatment/controls;
* 缺列时给可读报错并指明数据装配点, 不再让 M1 直接 r(111) 无诊断崩溃。
local REQUIRED_VARS `DV' `TX' `CTRL_B' `CTRL_Y' is_soe
local MISSING_VARS ""
foreach v of local REQUIRED_VARS {
    capture confirm variable `v'
    if _rc != 0 local MISSING_VARS "`MISSING_VARS' `v'"
}
if "`MISSING_VARS'" != "" {
    display as error "Table 2 缺失变量:`MISSING_VARS'"
    display as error "原因: 49_risk_taking_outcomes.dta 仅含 stage 49 outcome 列。"
    display as error "修复: 先跑 01_data_prep.do (merge 40_panel_yearly.dta 生成"
    display as error "  data/processed/_paper10_working.dta), 再将本脚本 use 行指向"
    display as error "  该 working dataset; 或自行 merge 上述缺失列后重跑。"
    error 111
}

* ──────────────────────────────────────────────────────────────────────────
* M1: 主解释 only (no FE, OLS)
* ──────────────────────────────────────────────────────────────────────────
eststo M1: reghdfe `DV' `TX', noabsorb vce(cluster bank_id year)

* M2: + Bank FE
eststo M2: reghdfe `DV' `TX', absorb(bank_id) vce(cluster bank_id year)

* M3: + Bank FE + Year FE
eststo M3: reghdfe `DV' `TX', absorb(bank_id year) vce(cluster bank_id year)

* M4: + bank controls
eststo M4: reghdfe `DV' `TX' `CTRL_B', ///
    absorb(bank_id year) vce(cluster bank_id year)

* M5: + year controls
eststo M5: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

* M6: + SOE × TX 交互 (V4 F-P1.1 implicit guarantee 框架)
eststo M6: reghdfe `DV' c.`TX'##i.is_soe `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

* ──────────────────────────────────────────────────────────────────────────
* 输出 Table 2
* ──────────────────────────────────────────────────────────────────────────
esttab M1 M2 M3 M4 M5 M6 ///
    using "papers/bank_media_disagreement/output/table2_main_disagreement_risk.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 2: Media Disagreement and Bank Risk-Taking (Z-score)") ///
    mtitles("OLS" "Bank FE" "Bank+Year FE" "+Bank Ctrl" "+Year Ctrl" "+SOE Int.") ///
    keep(`TX' 1.is_soe c.`TX'#1.is_soe) ///
    addnotes("Cluster-robust SE in parentheses (bank+year two-way)." ///
             "Z-score: CAR-based variant (capital term = regulatory CAR, not book equity/assets); cf. Laeven-Levine 2009 JFE." ///
             "SOE × disagreement interaction per Acharya 2016 RFS implicit guarantee framework.")

eststo clear
