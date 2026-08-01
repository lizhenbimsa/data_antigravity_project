* news_process — 第 11 篇 (bank_news_clarity, PROVISIONAL) Table 6:
*   结构性分样本外部效度 (structural split-sample external validity)
*
* ── NC-TABLE-NUMBERING-04 (仅注释, 勿改 spec/文件名) ─────────────────────────
*   本表内部 title 标 "Table 6", 但 paper_spec 的 t6 主表槽已被占用 → manuscript
*   排版时应把本表编入 **附录 tA-series**, 避免与正文主表 Table 6 撞号。此处只
*   标注, 不改 paper_spec / 文件名 / 00_master (那些由主控统一处理)。
*
* ----------------------------------------------------------------------------
* 是什么 / 为什么 / 影响 (一行大白话):
*   是什么: 按银行的"结构属性"把样本切成几组, 分别跑主回归, 看 clarity 效应
*           在不同类型/网络枢纽地位/规模的银行里是否一致。
*   为什么: 现有 Table 4 的分样本全基于 sentinel 列 (隐性担保层级 / listed 幻影列)
*           或 sub-period; **没有**用在盘结构列做的分样本。结构性分组是
*           treatment-side 当下即可跑的外部效度检验, 与 Table 4 任何 panel 不重叠
*           (Table 4 M6 的 SOE 是全样本交互项而非按结构真正切样本)。
*   影响: 纯消费在盘列, 不写回 processed/golden; DV=z_score 为 sentinel
*         (外部财务面板待接入), 缺列时整表 wire-ahead 跳过, 不报错。
*
* ----------------------------------------------------------------------------
* Panel A: 按 bank_type 分类型 (city / rural / joint / private / soe / foreign)
* Panel B: 按 bank_is_hub 枢纽 vs 非枢纽 (媒体关注网络中心地位 0/1)
* Panel C: 按 bank_effective_size 中位切 (大行 vs 小行; T 小/样本小守卫)
*
* 文献锚点 (Anchor):
*   标准子样本构成稳健性 (split-sample external validity) — 顶刊实证常规做法,
*   无单一 canonical DOI; 方法学综述见
*   Angrist, J. D., & Pischke, J.-S. (2009). Mostly Harmless Econometrics.
*     Princeton University Press. (subsample / heterogeneity 外部效度讨论)
*
* 处理 (treatment): mean_clarity_score_full (You 2018 词典, _full 主轨; full-only
*   gating 2026-06-29 后 headline 处理轨 = 决定留篇的全文轨, _ctx 降为 robustness)
* 结果 (outcome):  z_score (CAR-based Z-score 变体, sentinel → wire-ahead 守卫)
* ============================================================================

version 19
clear all
set more off
set maxvar 32767
set linesize 120
eststo clear

* ── 数据: 优先 working dataset (01_data_prep 产出), 缺则直接用全量面板导出 ──
capture confirm file "data/processed/_paper11_working.dta"
if !_rc {
    use "data/processed/_paper11_working.dta", clear
}
else {
    use "data/processed/46_panel_yearly_full.dta", clear
}
capture confirm variable bank_id
if _rc {
    egen bank_id = group(target_bank)
}
xtset bank_id year

* ── 主变量 (与 11_table2 / 13_table4 共享口径) ───────────────────────────
local TX     mean_clarity_score_full
local DV     z_score
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

capture confirm variable `TX'
if _rc {
    display as error "  [WARN] 处理变量 `TX' 不在面板; Table 6 整表跳过"
    exit 0
}

* ── DV sentinel 守卫 (wire-ahead) ────────────────────────────────────────
capture confirm variable `DV'
if _rc {
    display "  [WIRE-AHEAD] 结果变量 `DV' 未物化 (外部财务面板待接入);" ///
            " Table 6 全部分样本守卫跳过, 仅占位。"
    display ""
    display "=========================================="
    display "Table 6 (structural subsamples) 跑完 (DV sentinel 跳过)"
    display "=========================================="
    exit 0
}

* 小样本回归 helper: 子样本观测数过少时不跑 (防 reghdfe 退化 / r(2000))
* 阈值取 20 (银行年度面板; 远低于则 cluster SE 无意义)。
local MINOBS 20

* ── NC-TWOWAY-CLUSTER-T2-05: year 簇数 (双向 cluster 第二维) ─────────────────
* 各 Panel 用 vce(cluster bank_id year); year 簇早期试跑盘面 T=2 / 生产 ~18, 少簇 →
* cluster-robust SE 渐近近似差 → addnotes 显式披露 year 簇数 + 少簇 caveat。
quietly levelsof year, local(_yrs_cl)
local NYR_CL : word count `_yrs_cl'

* ── NC-NGUARD-LISTWISE-02: post-est e(N) 守卫阈值 ───────────────────────────
* 子样本 count 守卫只 count treatment 非缺, 未防 8 个财务/宏观控制 listwise-
* delete 后估计样本塌缩 → 每个 eststo 后读 e(N), 太小则 drop 该退化列。
local MINEST 20

* ============================================================================
* Panel A — 按 bank_type 分类型
* ============================================================================
capture confirm variable bank_type
if _rc {
    display "  [SKIP] bank_type 缺 — Panel A 跳过"
}
else {
    * bank_type 在盘为字符串 → levelsof 取各类型逐组回归
    quietly levelsof bank_type, local(_types)
    local k = 0
    foreach tp of local _types {
        local ++k
        * 子样本观测数守卫
        quietly count if bank_type == "`tp'" & !missing(`TX')
        local n_tp = r(N)
        if `n_tp' >= `MINOBS' {
            capture noisily eststo A_t`k': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
                if bank_type == "`tp'", absorb(bank_id year) vce(cluster bank_id year)
            * NC-NGUARD-LISTWISE-02: 控制 listwise 后 e(N) 塌缩则 drop 退化列
            if _rc==0 & e(N) < `MINEST' {
                display "  [N 守卫] bank_type==`tp' 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — drop"
                capture estimates drop A_t`k'
            }
            else if _rc==0 {
                estadd local btype "`tp'"
            }
        }
        else {
            display "  [N 守卫] bank_type==`tp' 仅 `n_tp' obs (<`MINOBS') — 跳过该组"
        }
    }

    * esttab 名单动态化 (缺估计不点名, 防 r(111) 丢整表)。
    * 注意: `: list X in Y' 的 X 须是"内容为待查项的 local 名", 不能直接写字面
    * 估计名 (字面名会被当作空 local → 空串恒被判 in, 反致 r(111))。故先把
    * 候选名赋给 local m 再判 — 与 12_table3 / 14_table5 一致的安全写法。
    qui estimates dir
    local stored `r(names)'
    local models ""
    forvalues i = 1/`k' {
        local m A_t`i'
        if `: list m in stored' local models `models' `m'
    }
    if "`models'" != "" {
        esttab `models' ///
            using "output/tables/table6_panelA_bank_type.tex", replace ///
            booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
            b(%9.4f) se(%9.4f) compress ///
            stats(btype N r2, fmt(%12s 0 3) labels("Bank type" "N" "R²")) ///
            title("Table 6 Panel A: Clarity Effect by Bank Type (split sample)") ///
            keep(`TX') ///
            addnotes("Each column = one bank-type subsample; cluster-robust SE (bank+year)." ///
                     "Treatment = mean_clarity_score_full (You 2018 dict, _full main track; full-only gating 2026-06-29, _ctx twin = primary robustness)." ///
                     "Two-way cluster on (bank, year): year clusters = `NYR_CL'; few-cluster caveat (asymptotic cluster-robust SE unreliable with small year-cluster count; production T=19 should report wild-cluster-bootstrap)." ///
                     "Subsamples with <`MINOBS' obs (or post-est e(N)<`MINEST' after control listwise deletion) skipped (degenerate SE).")
        esttab `models' ///
            using "output/tables/table6_panelA_bank_type.csv", replace ///
            plain b(%9.4f) se(%9.4f) stats(N r2, fmt(0 3)) keep(`TX')
        display "[OK] 15_table6 Panel A -> output/tables/table6_panelA_bank_type.{tex,csv}"
    }
    else {
        display "  [WARN] Panel A 无任何有效分组估计 — 表跳过"
    }
    eststo clear
}

* ============================================================================
* Panel B — 按 bank_is_hub 枢纽 vs 非枢纽
* ============================================================================
* ── NC-HUB-CROSSYEAR-03: hub 子样本逐年漂移披露 ─────────────────────────────
* bank_is_hub 名义上是 0/1 切分, 但 hub 在生产中按"年内媒体关注 top-10%"界定 →
* 同一家银行可能某年是 hub、另一年掉出 (跨年翻转), 故子样本成员逐年漂移、非
* 时间不变切分。此处仍按当前盘的 bank_is_hub 值分组 (早期试跑盘面 T=2 时近似不变), 但
* addnotes 显式披露该 within-year top-decile 性质与跨年漂移 (production T=19 时
* 严格做法应改为 pooled interaction clarity#hub 或在每个 bank-year 内重新判 hub)。
capture confirm variable bank_is_hub
if _rc {
    display "  [SKIP] bank_is_hub 缺 — Panel B 跳过"
}
else {
    foreach h in 0 1 {
        quietly count if bank_is_hub == `h' & !missing(`TX')
        local n_h = r(N)
        if `n_h' >= `MINOBS' {
            capture noisily eststo B_h`h': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
                if bank_is_hub == `h', absorb(bank_id year) vce(cluster bank_id year)
            * NC-NGUARD-LISTWISE-02: 控制 listwise 后 e(N) 塌缩则 drop
            if _rc==0 & e(N) < `MINEST' {
                display "  [N 守卫] bank_is_hub==`h' 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — drop"
                capture estimates drop B_h`h'
            }
        }
        else {
            display "  [N 守卫] bank_is_hub==`h' 仅 `n_h' obs (<`MINOBS') — 跳过"
        }
    }

    qui estimates dir
    local stored `r(names)'
    local cand_models B_h1 B_h0
    local cand_titles `""Hub" "Non-hub""'
    local models ""
    local mtitles `""'
    forvalues i = 1/2 {
        local m : word `i' of `cand_models'
        if `: list m in stored' {
            local models `models' `m'
            local t : word `i' of `cand_titles'
            local mtitles `"`mtitles' "`t'""'
        }
    }
    if "`models'" != "" {
        esttab `models' ///
            using "output/tables/table6_panelB_hub.tex", replace ///
            booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
            b(%9.4f) se(%9.4f) compress ///
            stats(N r2, fmt(0 3) labels("N" "R²")) ///
            title("Table 6 Panel B: Hub vs Non-Hub Banks (media-network centrality split)") ///
            mtitles(`mtitles') keep(`TX') ///
            addnotes("Split on bank_is_hub (media-attention network hub status, 0/1)." ///
                     "Hub is defined as the within-year top-10% of media attention; membership therefore drifts year to year (a bank can be a hub in one year and not another), so these subsamples are NOT time-invariant. With production T=19, prefer a pooled clarity#hub interaction (or re-evaluate hub within each bank-year)." ///
                     "Two-way cluster on (bank, year): year clusters = `NYR_CL'; few-cluster caveat applies (small year-cluster count; production should report wild-cluster-bootstrap)." ///
                     "Treatment = mean_clarity_score_full; cluster-robust SE (bank+year). Columns with post-est e(N)<`MINEST' (control listwise) dropped.")
        esttab `models' ///
            using "output/tables/table6_panelB_hub.csv", replace ///
            plain b(%9.4f) se(%9.4f) stats(N r2, fmt(0 3)) keep(`TX')
        display "[OK] 15_table6 Panel B -> output/tables/table6_panelB_hub.{tex,csv}"
    }
    else {
        display "  [WARN] Panel B 无任何有效分组估计 — 表跳过"
    }
    eststo clear
}

* ============================================================================
* Panel C — 按 bank_effective_size 中位切 (大行 vs 小行)
* ============================================================================
capture confirm variable bank_effective_size
if _rc {
    display "  [SKIP] bank_effective_size 缺 — Panel C 跳过"
}
else {
    * 非缺样本计数守卫 (该列盘面大量 NaN; 不足则跳过整 panel)
    quietly count if !missing(bank_effective_size) & !missing(`TX')
    local n_sz = r(N)
    if `n_sz' < (2 * `MINOBS') {
        display "  [N 守卫] bank_effective_size 非缺样本仅 `n_sz' obs (<`=2*`MINOBS'')" ///
                " — 中位切两组各不足, Panel C 跳过 (production 全样本才有功效)"
    }
    else {
        * 中位切: 用非缺样本中位数 (大行=高于中位, 小行=低于等于中位)
        quietly summarize bank_effective_size, detail
        local med = r(p50)
        gen byte _sz_big = (bank_effective_size > `med') if !missing(bank_effective_size)

        foreach b in 1 0 {
            quietly count if _sz_big == `b' & !missing(`TX')
            local n_b = r(N)
            if `n_b' >= `MINOBS' {
                capture noisily eststo C_s`b': reghdfe `DV' `TX' `CTRL_B' `CTRL_Y' ///
                    if _sz_big == `b', absorb(bank_id year) vce(cluster bank_id year)
                * NC-NGUARD-LISTWISE-02: 控制 listwise 后 e(N) 塌缩则 drop
                if _rc==0 & e(N) < `MINEST' {
                    display "  [N 守卫] size group `b' 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — drop"
                    capture estimates drop C_s`b'
                }
            }
            else {
                display "  [N 守卫] size group `b' 仅 `n_b' obs (<`MINOBS') — 跳过"
            }
        }

        qui estimates dir
        local stored `r(names)'
        local cand_models C_s1 C_s0
        local cand_titles `""Large (>median)" "Small (<=median)""'
        local models ""
        local mtitles `""'
        forvalues i = 1/2 {
            local m : word `i' of `cand_models'
            if `: list m in stored' {
                local models `models' `m'
                local t : word `i' of `cand_titles'
                local mtitles `"`mtitles' "`t'""'
            }
        }
        if "`models'" != "" {
            esttab `models' ///
                using "output/tables/table6_panelC_size.tex", replace ///
                booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
                b(%9.4f) se(%9.4f) compress ///
                stats(N r2, fmt(0 3) labels("N" "R²")) ///
                title("Table 6 Panel C: Large vs Small Banks (effective-size median split)") ///
                mtitles(`mtitles') keep(`TX') ///
                addnotes("Median split on bank_effective_size (non-missing sample, median=`med')." ///
                         "Two-way cluster on (bank, year): year clusters = `NYR_CL'; few-cluster caveat applies (small year-cluster count; production should report wild-cluster-bootstrap)." ///
                         "Treatment = mean_clarity_score_full; cluster-robust SE (bank+year). Columns with post-est e(N)<`MINEST' (control listwise) dropped.")
            esttab `models' ///
                using "output/tables/table6_panelC_size.csv", replace ///
                plain b(%9.4f) se(%9.4f) stats(N r2, fmt(0 3)) keep(`TX')
            display "[OK] 15_table6 Panel C -> output/tables/table6_panelC_size.{tex,csv}"
        }
        else {
            display "  [WARN] Panel C 无任何有效分组估计 — 表跳过"
        }
        eststo clear
    }
}

display ""
display "=========================================="
display "Table 6 (structural subsamples) 跑完"
display "=========================================="
