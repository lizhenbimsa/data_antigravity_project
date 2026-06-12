* news_process v3.7.0 — 第 11 篇 Table 2: Clarity → Risk-Taking 主回归 M1-M6
*
* Treatment (DC1 path C = No-SSRN + _ctx G3 解锁, V4 reframe external info env):
*   DV  = z_score   (CAR-based Z-score 变体, cf. Laeven-Levine 2009 JFE;
*         fix(omni-g-zscore-papers-01, 2026-06-11): 资本项=监管 Basel CAR 非
*         L&L 原版账面 equity/assets, 见 paper_spec.yaml outcome 更正)
*         白话: Z-score 越高表示银行离资不抵债越远、风险越低; 此处资本项用监管
*         资本充足率 (CAR), 与原版账面口径不同, 故称"变体"。
*   TX  = mean_clarity_score_ctx   (You 2018 词典, _ctx 轨 G3 严谨路线)
*
* M1-M6 渐进设定 (progressive):
*   M1: 主解释 only
*   M2: + Bank FE
*   M3: + Bank FE + Year FE
*   M4: + bank controls
*   M5: + year controls
*   M6: + SOE × clarity 交互 (Acharya 2016 RFS framework)
*
* 理论锚点 (Anchor): Bushman-Williams 2012 JAE 信息环境 → 银行风险承担框架
* 重新定位 (Reframe): clarity = 外部信息环境质量 (Bushee 2010 JAR), 而非银行透明度

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

* ── fail-loud guard fix(omni-g-zscore-papers-04, 2026-06-11) ─────────────
* stage 49 导出的 49_risk_taking_outcomes.dta 仅含 outcome 列
* (risk_taking_outcomes.py::OUTPUT_OUTCOME_COLS), 不含任何 treatment/controls;
* 缺列时给可读报错并指明数据装配点, 不再让 M1 直接 r(111) 无诊断崩溃。
local REQUIRED_VARS `DV' `TX' `CTRL_B' `CTRL_Y' is_soe loan_loss_provision_discretion
local MISSING_VARS ""
foreach v of local REQUIRED_VARS {
    capture confirm variable `v'
    if _rc != 0 local MISSING_VARS "`MISSING_VARS' `v'"
}
if "`MISSING_VARS'" != "" {
    display as error "Table 2 缺失变量:`MISSING_VARS'"
    display as error "原因: 49_risk_taking_outcomes.dta 仅含 stage 49 outcome 列。"
    display as error "修复: 先跑 01_data_prep.do (merge 40_panel_yearly.dta 生成"
    display as error "  data/processed/_paper11_working.dta), 再将本脚本 use 行指向"
    display as error "  该 working dataset; 或自行 merge 上述缺失列后重跑。"
    display as error "注: credit_rating 需外部评级数据 (仅上市子样本可得, 见 paper_spec"
    display as error "  controls); term_spread 需自行 merge 国债收益率曲线 (01_data_prep"
    display as error "  仅生成全缺失占位列) — 管道任何数据源均不产出这两列。"
    error 111
}

* ──────────────────────────────────────────────────────────────────────────
* M1-M6 渐进设定
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
* LLP ratio as alternative outcome fix(omni-g-zscore-papers-02, 2026-06-11) (与 paper_spec outcome
* 2026-06-10 更正一致): 列 loan_loss_provision_discretion 当前实现是裸 LLP/贷款
* 比率, **非** Bushman-Williams 2012 JAE 的残差式 discretion (基本面残差回归未
* 实现) — 勿当 BW2012 discretion 呈现; BW2012 仅作 framework anchor。
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
    title("Table 2: Media Clarity and Bank Risk-Taking (Z-score / LLP Ratio)") ///
    mtitles("OLS" "Bank FE" "Bank+Year FE" "+Bank Ctrl" "+Year Ctrl" "+SOE Int." "LLP Ratio") ///
    keep(`TX' 1.is_soe c.`TX'#1.is_soe) ///
    addnotes("Cluster-robust SE (bank+year two-way)." ///
             "Treatment = mean_clarity_score_ctx (You 2018 词典 _ctx 轨)." ///
             "Z-score: CAR-based variant (capital term = regulatory CAR, not book equity/assets); cf. Laeven-Levine 2009 JFE." ///
             "LLP outcome = raw LLP/loans ratio, not the Bushman-Williams 2012 JAE residual-based discretion measure." ///
             "Reframe: clarity = external info env quality (Bushee 2010 JAR), not bank disclosure transparency." ///
             "Anchor: Bushman-Williams 2012 JAE info → risk-taking framework.")

eststo clear
