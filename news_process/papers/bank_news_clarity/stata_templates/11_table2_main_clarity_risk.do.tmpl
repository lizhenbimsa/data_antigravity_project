* news_process v3.7.0 — 第 11 篇 Table 2: Clarity → Risk-Taking 主回归 M1-M6
*
* Treatment (DC1 path C = No-SSRN + _ctx G3 解锁, V4 reframe external info env):
*   DV  = z_score   (Laeven-Levine 2009 JFE)
*   TX  = mean_clarity_score_ctx   (You 2018 词典, _ctx 轨 G3 严谨路线)
*
* M1-M6 progressive:
*   M1: 主解释 only
*   M2: + Bank FE
*   M3: + Bank FE + Year FE
*   M4: + bank controls
*   M5: + year controls
*   M6: + SOE × clarity 交互 (Acharya 2016 RFS framework)
*
* Anchor: Bushman-Williams 2012 JAE info environment → bank risk-taking framework
* Reframe: clarity = external info env quality (Bushee 2010 JAR), NOT 银行透明度

version 19
clear all
set maxvar 32767
set linesize 120

* 加载共享 outcome panel (与第 10 篇共用 stage 49 输出)
* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
use "data/processed/49_risk_taking_outcomes.dta", clear
encode target_bank, gen(bank_id)
xtset bank_id year
merge m:1 target_bank using "data/processed/bank_metadata.dta", keep(match master) nogen

* 主变量 (与第 10 篇 outcome 共享, treatment 完全不同 → 学术独立)
local DV     z_score
local TX     mean_clarity_score_ctx
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth credit_rating
local CTRL_Y gdp_growth m2_growth shibor term_spread

* ──────────────────────────────────────────────────────────────────────────
* M1-M6 progressive
* ──────────────────────────────────────────────────────────────────────────
eststo M1: reghdfe `DV' `TX', noabsorb vce(cluster bank_id year)

eststo M2: reghdfe `DV' `TX', absorb(bank_id) vce(cluster bank_id year)

eststo M3: reghdfe `DV' `TX', absorb(bank_id year) vce(cluster bank_id year)

eststo M4: reghdfe `DV' `TX' `CTRL_B', ///
    absorb(bank_id year) vce(cluster bank_id year)

eststo M5: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

eststo M6: reghdfe `DV' c.`TX'##i.is_soe `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

* ──────────────────────────────────────────────────────────────────────────
* Bushman-Williams 2012 JAE direct match: LLP discretion as alternative outcome
* ──────────────────────────────────────────────────────────────────────────
eststo M_BW: reghdfe loan_loss_provision_discretion `TX' `CTRL_B' `CTRL_Y', ///
    absorb(bank_id year) vce(cluster bank_id year)

* ──────────────────────────────────────────────────────────────────────────
* 输出
* ──────────────────────────────────────────────────────────────────────────
esttab M1 M2 M3 M4 M5 M6 M_BW ///
    using "papers/bank_news_clarity/output/table2_main_clarity_risk.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 2: Media Clarity and Bank Risk-Taking (Z-score / LLP Discretion)") ///
    mtitles("OLS" "Bank FE" "Bank+Year FE" "+Bank Ctrl" "+Year Ctrl" "+SOE Int." "BW2012 LLP") ///
    keep(`TX' 1.is_soe c.`TX'#1.is_soe) ///
    addnotes("Cluster-robust SE (bank+year two-way)." ///
             "Treatment = mean_clarity_score_ctx (You 2018 词典 _ctx 轨)." ///
             "Reframe: clarity = external info env quality (Bushee 2010 JAR), not bank disclosure transparency." ///
             "Anchor: Bushman-Williams 2012 JAE info → risk-taking framework.")

eststo clear
