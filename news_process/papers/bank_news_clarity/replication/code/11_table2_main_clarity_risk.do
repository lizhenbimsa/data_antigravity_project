* news_process v3.7.0 — 第 11 篇 Table 2: Clarity → Risk-Taking 主回归 M1-M6
*
* Treatment (DC1 path C = No-SSRN + _ctx G3 解锁, V4 reframe external info env):
*   DV  = z_score   (CAR-based Z-score 变体, cf. Laeven-Levine 2009 JFE;
*         fix(omni-g-zscore-papers-01, 2026-06-11): 资本项=监管 Basel CAR 非
*         L&L 原版账面 equity/assets, 见 paper_spec.yaml outcome 更正)
*         白话: Z-score 越高表示银行离资不抵债越远、风险越低; 此处资本项用监管
*         资本充足率 (CAR), 与原版账面口径不同, 故称"变体"。
*   TX  = mean_clarity_score_full  (You 2018 词典, _full 主轨; full-only gating
*         2026-06-29 后 headline 处理轨 = 决定留篇的全文轨, paper_spec
*         treatment.primary; entity-attributed _ctx 降为首要 robustness 孪生)
*
* M1-M6 渐进设定 (progressive):
*   M1: 主解释 only
*   M2: + Bank FE
*   M3: + Bank FE + Year FE
*   M4: + bank controls
*   M5: + year controls
*   M6: + SOE × clarity 交互 (Acharya, Anginer & Warburton 2016 working paper framework)
*
* 理论锚点 (Anchor): Bushman-Williams 2012 JAE 信息环境 → 银行风险承担框架
* 重新定位 (Reframe): clarity = 外部信息环境质量 (Bushee 2010 JAR), 而非银行透明度

version 19
clear all
set maxvar 32767
set linesize 120

* 加载共享 outcome panel (与第 10 篇共用 stage 49 输出; stage 49 已移除, outcome 待财务面板接入)
* v3.7.0 (C1 修复): 直接 use .dta (risk_taking_outcomes.py main 已 pyreadstat 导出)
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

* 主变量 (与第 10 篇 outcome 共享, treatment 完全不同 → 学术独立)
local DV     z_score
local TX     mean_clarity_score_full
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
* S10-04/S12-004: 少聚类 wild cluster bootstrap 推断 (headline 列 M3)
* ──────────────────────────────────────────────────────────────────────────
* 主表用 vce(cluster bank_id year) 双向聚类, 但 year 维聚类数 G_year≈13 偏小
* (production T≈18; T=2 试跑更小)。按 MacKinnon-Webb 2017 (Econometrics Journal)
* / Roodman et al. 2019 (SJ), G<~30 时渐近聚类 SE 在该维不可靠 → 对 year 维
* 改报 wild cluster bootstrap p 值 (boottest, cluster(year), reps(999)) 作为
* 该维首选推断。boottest 不改写 e(b)/e(V), wild p 在 r(p) → estadd 注入后
* 进表 (镜像 14_table5 / 14_table5_advanced_robustness 既有 idiom)。
* 白话: 年份只有十来个, 普通"按年聚类"的 p 值在统计上不够稳; 这里对最关键的
* 第 (3) 列 (银行+年份双固定效应) 用 wild bootstrap 重抽样重算 p, 给出更可信的
* 显著性, 并在表注里如实披露这一少聚类隐患与首选推断方式。
* ⚠ boottest 仅支持 reghdfe 单组吸收 FE (help boottest: "one set of absorbed
* fixed effects"); headline 双向 FE (absorb(bank_id year)) 会令 boottest 报
* "Doesn't work after reghdfe with more than one set of absorbed fixed effects"
* → 故 boottest 上游回归改为吸收 bank (单组) + year 显式哑变量 i.year, 与双向
* 吸收的 M3 点估计等价, 而 boottest 可正常对 year 维做 wild bootstrap。
* capture-guarded: 缺 boottest 包 / 缺列时优雅跳过, 绝不 hard-error 丢整表。
local _wild_p_note ""
capture confirm variable `TX'
if !_rc {
    capture which boottest
    if !_rc {
        * 为 boottest 重设 headline 上下文: 吸收 bank (单组 FE, boottest 兼容)
        * + year 显式哑变量 i.year (点估计同双向吸收 M3), cluster(year)
        capture noisily reghdfe `DV' `TX' i.year, absorb(bank_id) vce(cluster year)
        if !_rc {
            capture noisily boottest `TX'=0, reps(999) cluster(year) seed(2026) nograph
            if !_rc {
                scalar p_wild_year = r(p)
                estadd scalar p_wild_year = r(p): M3
                display "  [S10-04] M3 wild cluster bootstrap p (cluster=year, G_year≈13, reps=999): " r(p)
                local _wild_p_note "Few-cluster caveat: year clusters G_year≈13 (small); asymptotic cluster-robust SE on the year dimension are unreliable (Roodman et al. 2019 SJ). Preferred year-dimension inference = wild-cluster-bootstrap p (boottest, cluster(year), reps=999), reported as p_wild_year for the headline column M3."
            }
        }
    }
    else {
        display "  [S10-04][WARN] boottest 未安装 (ssc install boottest, replace); wild bootstrap p 跳过, 仅报聚类 SE。"
    }
}
if "`_wild_p_note'" == "" {
    local _wild_p_note "Few-cluster caveat: year clusters G_year≈13 (small); asymptotic cluster-robust SE on the year dimension are unreliable (Roodman et al. 2019 SJ). Production should report wild-cluster-bootstrap (boottest, cluster(year), reps=999) p-values as the preferred year-dimension inference (boottest unavailable / TX missing here → not computed)."
}

* ──────────────────────────────────────────────────────────────────────────
* 输出
* ──────────────────────────────────────────────────────────────────────────
esttab M1 M2 M3 M4 M5 M6 M_BW ///
    using "papers/bank_news_clarity/output/table2_main_clarity_risk.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 2: Media Clarity and Bank Risk-Taking (Z-score / LLP Ratio)") ///
    mtitles("OLS" "Bank FE" "Bank+Year FE" "+Bank Ctrl" "+Year Ctrl" "+SOE Int." "LLP Ratio") ///
    keep(`TX' 1.is_soe#c.`TX') ///
    addnotes("Cluster-robust SE (bank+year two-way)." ///
             "Treatment = mean_clarity_score_full (You 2018 dict, _full main track; full-only gating 2026-06-29 — the headline treatment track coincides with the track that determines article retention; the entity-attributed _ctx twin is the primary robustness variant)." ///
             "Z-score: CAR-based variant (capital term = regulatory CAR, not book equity/assets); cf. Laeven-Levine 2009 JFE." ///
             "LLP outcome = raw LLP/loans ratio, not the Bushman-Williams 2012 JAE residual-based discretion measure." ///
             "Reframe: clarity = external info env quality (Bushee 2010 JAR), not bank disclosure transparency." ///
             "`_wild_p_note'" ///
             "Anchor: Bushman-Williams 2012 JAE info → risk-taking framework.")

eststo clear
