* news_process v3.7.0 — 第 10 篇 Table 2: Disagreement → Risk-Taking 主回归 M1-M6
*
* Treatment (DC1 path B = SSRN + _full main):
*   DV  = z_score   (CAR-based Z-score 变体, cf. Laeven-Levine 2009 JFE;
*         fix(omni-g-zscore-papers-01, 2026-06-11): 资本项=监管 Basel CAR 非
*         L&L 原版账面 equity/assets, 见 paper_spec.yaml outcome 更正)
*         白话: Z-score 越高表示银行离资不抵债越远、风险越低; 此处资本项用监管
*         资本充足率 (CAR), 与原版账面口径不同, 故称"变体"。
*   TX  = cross_outlet_tone_variance_full   (V4 R3 critical 修复, M2-M3 新建字段)
*         ⚠ 同名异构披露: 盘上 cross_outlet_tone_variance_{full,ctx,ss} 实为 stage 39f
*         (cross_media_alpha.py) 的【事件窗条件构造】(逐 episode 跨 outlet 方差按文章数
*         再加权), **非** paper_spec 冻结的【全年无条件】跨 outlet 截面方差 (后者 M2-M3
*         待 encode.py 新建, 尚未物化)。39f 列缺位时 01_data_prep 回退 llm_vote_tone_std_full
*         (亦非 spec 测度)。两者均不应当作 spec 全年口径 disagreement 主处理呈现。
*
* M1-M6 渐进设定 (V4 F2.2 边界条件 + F-P1.1 隐性担保 implicit guarantee):
*   M1: 主解释 only
*   M2: + Bank FE
*   M3: + Bank FE + Year FE
*   M4: + bank controls (ln_assets, leverage, capital_ratio, npl_ratio, deposit_growth)
*   M5: + year controls (gdp_growth, m2_growth, shibor)
*   M6: + SOE × TX 交互 (Acharya, Anginer & Warburton 2016 working paper implicit guarantee 框架)

version 19
clear all
set maxvar 32767
set linesize 120

* 加载共享 outcome panel (stage 49 输出; stage 49 已移除, outcome 待财务面板接入)
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
* S10-04/S12-004: 少聚类 wild cluster bootstrap 推断 (headline 列 M3)
* ──────────────────────────────────────────────────────────────────────────
* 主表用 vce(cluster bank_id year) 双向聚类, 但 year 维聚类数 G_year≈13 偏小
* (production T=19; 早期试跑 T=2 更小)。按 MacKinnon-Webb 2017 (Econometrics Journal)
* / Roodman et al. 2019 (SJ), G<~30 时渐近聚类 SE 在该维不可靠 → 对 year 维
* 改报 wild cluster bootstrap p 值 (boottest, cluster(year), reps(999)) 作为
* 该维首选推断。boottest 不改写 e(b)/e(V), wild p 在 r(p) → estadd 注入后
* 进表 (镜像 14_table5_advanced_robustness 既有 idiom)。
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
* 输出 Table 2
* ──────────────────────────────────────────────────────────────────────────
esttab M1 M2 M3 M4 M5 M6 ///
    using "papers/bank_media_disagreement/output/table2_main_disagreement_risk.tex", ///
    replace booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
    b(%9.4f) se(%9.4f) ///
    title("Table 2: Media Disagreement and Bank Risk-Taking (Z-score)") ///
    mtitles("OLS" "Bank FE" "Bank+Year FE" "+Bank Ctrl" "+Year Ctrl" "+SOE Int.") ///
    keep(`TX' 1.is_soe#c.`TX') ///
    addnotes("Cluster-robust SE in parentheses (bank+year two-way)." ///
             "Z-score: CAR-based variant (capital term = regulatory CAR, not book equity/assets); cf. Laeven-Levine 2009 JFE." ///
             "Treatment on disk is the stage-39f EVENT-WINDOW-CONDITIONAL cross-outlet tone variance (per-episode, article-count re-weighted), NOT the paper_spec full-year UNCONDITIONAL cross-section measure (still to be built in M2-M3); when 39f is absent it falls back to llm_vote_tone_std_full — neither is the spec measure. Pending spec alignment / rename." ///
             "`_wild_p_note'" ///
             "SOE × disagreement interaction per Acharya, Anginer & Warburton (2016, working paper) implicit guarantee framework.")

eststo clear
