* news_process — 第 10 篇 (bank_media_disagreement) Table A1:
*   FE 饱和阶梯 (Panel A) + Oster (2019) 选择性偏误 δ (Panel B)
*
* ⚠ [MD-A1-006 表号撞车 — 仅注释] 本文件标题用 "Table A1", 但 paper_spec.yaml::tables
*   的 tA1 槽已被 llm_vote_tone_std_robustness 占用 (spec:313)。撰稿/manuscript
*   归位时本表应填入 spec 的空槽 tA7 (tA7/tA8/tA9 现 template: null, spec:319-324),
*   避免与既有 tA1 撞号。此处不改 paper_spec, 不改文件名 (主控统一处理); 仅留注释提示。
*
* ============================================================================
* 这张表干什么 (一行白话)
* ----------------------------------------------------------------------------
* Panel A: 不断往回归里塞"同省/同类型/同区域在同一年共同遭受的冲击"以及
*          "每家银行自己的线性时间趋势", 看跨媒体语调分歧→风险的主系数还稳不稳。
* Panel B: 算一个 δ 值 = "把这个系数压到 0 所需的不可观测因素要比已控制因素强多少倍",
*          δ>1 (Oster 经验法则) 就说明结论对'剩余看不见的选择性'稳健。
* ============================================================================
*
* 为何需要 (动机 / spec-promise 缺口):
*   - paper_spec.yaml::specification.fixed_effects = [bank_fe, year_fe, province_fe],
*     即 province_fe 在 spec 里被承诺, 但 Table 2/4 全部只 absorb(bank_id year),
*     province_fe 从未落地 — 这是 spec 承诺与模板实现之间的直接缺口, 也是审稿人
*     对 disagreement→risk 因果最常见的"未观测地域/类型共同冲击"反驳。
*   - Map 指出本篇此前"无任何 psacalc/honestdid 注释脚手架" → 选择性偏误检验是
*     真缺口而非已注释待激活; 本表首次为本篇落地 Oster δ (live, 非注释脚手架)。
*
* 主处理 (DC1 path B = SSRN + _full main, 见 paper_spec governance.main_track=_full):
*   TX = cross_outlet_tone_variance_full   (跨媒体语调分歧, stage 39f; 在盘)
*   DV = z_score                            (CAR-based Z-score 变体; 当前为 sentinel,
*                                            外部财务面板待接入 → capture-confirm 守卫,
*                                            缺列时整表优雅跳过, wire-ahead)
*
* 消费列 (全部在盘, golden-safe):
*   TX  cross_outlet_tone_variance_full
*   FE  bank_province / bank_type / bank_zone (string → encode), bank_id / year
*   Oster substantive 可观测控制 (δ-drivers, 对齐 paper_spec, MD-A1-002):
*         is_soe (controls.bank_level) + bank_degree_cent + brokerage_eigen_cent
*         (network_roles.control.columns) + 任何在盘财务控制
*         → 进受控回归右手边; FE 哑变量 (i.bank_id i.year) 才是 psacalc 的 mcontrol。
*   controls (sentinel, capture-confirm 守卫): ln_assets leverage capital_ratio
*         npl_ratio deposit_growth gdp_growth m2_growth shibor
*
* ⚠ 早期试跑 T=2 退化守卫: 早期试跑盘曾为 T=2 (2017-2018, ~174 行)。province#year / type#year /
*   zone#year / 银行线性趋势 (c.year#i.bank_id) 在早期试跑 T=2 下会过度吸收 (共线 / 无残余
*   变异), 但全语料 T=19 下功效充分。每级设定均 'quietly count e(sample)' + N/参数
*   守卫: 退化时该列优雅跳过 (eststo 不存), 不报错中断。
*
* 学术锚点 (DOI 已核验):
*   Gormley, T. A., & Matsa, D. A. (2014). Common errors: How to (and not to)
*     control for unobserved heterogeneity. Review of Financial Studies, 27(2),
*     617-661. doi:10.1093/rfs/hht047
*     → group×time FE (province#year 等) 是吸收未观测共同冲击的正确做法;
*       提醒 demeaning 类捷径的常见错误。
*   Oster, E. (2019). Unobservable selection and coefficient stability: Theory
*     and evidence. Journal of Business & Economic Statistics, 37(2), 187-204.
*     doi:10.1080/07350015.2016.1227711
*     → δ = 使系数归零所需的不可观测/可观测选择性比; rmax 经验取 1.3·R²_controlled。
*
* 输出: $tables_dir/tableA1_fe_saturation_oster.{tex,csv} (默认 output/tables/)
* ============================================================================

version 19
clear all
set more off
set maxvar 32767
set linesize 120
eststo clear

* ── 输出目录 ($tables_dir) + nested mkdir (MD-A1-005: fresh clone / dry-run 防 r(603)) ──
* 白话: 主链 master 通常已建好 output/tables/, 但 fresh clone 或独立 dry-run 重跑时
*       该目录可能不存在, 此前直接 esttab using "output/tables/..." 会 r(603) 崩。
*       这里设 $tables_dir 宏 + 逐级 capture mkdir (Stata mkdir 不递归 → 父子各建一次)。
if "$tables_dir" == ""  global tables_dir "output/tables"
capture mkdir "$tables_dir/.."
capture mkdir "$tables_dir"

* ── 数据装配 (修陈旧输入: 主控指令统一指向 01_data_prep 产出的 working dataset;
*    缺则回退到全量面板, 复刻 11/12/13 的 bank_id/xtset 装配) ──────────────────
capture confirm file "data/processed/_paper10_working.dta"
if !_rc {
    use "data/processed/_paper10_working.dta", clear
}
else {
    use "data/processed/46_panel_yearly_full.dta", clear
}
capture confirm variable bank_id
if _rc {
    encode target_bank, gen(bank_id)
}
xtset bank_id year

* ── 主变量 (硬编码 local, 沿用本篇 11/12/13 约定) ─────────────────────────────
local DV     z_score
local TX     cross_outlet_tone_variance_full
local CTRL_B ln_assets leverage capital_ratio npl_ratio deposit_growth
local CTRL_Y gdp_growth m2_growth shibor

* ── 在盘的财务控制 (sentinel) 动态收集: 缺列不进 $controls, 不报错 ──────────────
* 白话: 财务面板还没接入时, ln_assets 等控制列暂缺; 这里逐列探测, 只把真在盘的
* 放进 $ctrl, 让 FE 阶梯仍能在"无财务控制"下跑通 (province#year 等吸收力是重点)。
local CTRL_AVAIL ""
foreach v of local CTRL_B {
    capture confirm variable `v'
    if !_rc local CTRL_AVAIL "`CTRL_AVAIL' `v'"
}
foreach v of local CTRL_Y {
    capture confirm variable `v'
    if !_rc local CTRL_AVAIL "`CTRL_AVAIL' `v'"
}
display "  [INFO] 在盘财务控制: `CTRL_AVAIL'  (缺列已自动剔除, wire-ahead)"

* ── 前置守卫: 主处理 / DV 任一缺 → 整表优雅跳过 (golden-safe) ──────────────────
capture confirm variable `TX'
if _rc {
    display "  [WARN] 主处理 `TX' 不在面板 (stage 39f validation 未先行); Table A1 跳过"
    exit 0
}
capture confirm variable `DV'
if _rc {
    display "  [WARN] DV `DV' 未物化 (外部财务面板待接入 — 见 CLAUDE.md stage 49 移除记录);"
    display "         Table A1 (FE-SAT + OSTER 均需 DV) 优雅跳过 (wire-ahead)。"
    exit 0
}

* ── FE 用的 string 列 encode (bank_province / bank_type / bank_zone) ──────────
* 白话: reghdfe absorb() 需要数值 ID; 这三列是中文/拼音字符串, 先 encode 成整数因子。
foreach fe in bank_province bank_type bank_zone {
    capture confirm numeric variable `fe'
    if _rc {
        capture confirm string variable `fe'
        if !_rc {
            capture confirm variable `fe'_id
            if _rc encode `fe', gen(`fe'_id)
        }
    }
    else {
        capture confirm variable `fe'_id
        if _rc gen `fe'_id = `fe'
    }
}

* ── 判断面板时间深度 (T) — 决定高阶 FE / 趋势项是否可识别 ──────────────────────
quietly levelsof year, local(yrs)
local nyears : word count `yrs'
display "  [INFO] 面板时间深度 T = `nyears' 年 (T<3 时 group#year / 银行趋势过度吸收)"

* ============================================================================
* Panel A: FE 饱和阶梯
*   M0: bank + year (基线, 复刻主表)
*   M1: + province#year (i.bank_province_id#i.year) — 同省同年共同冲击
*   M2: + bank-type#year (i.bank_type_id#i.year)    — 同类型同年共同冲击
*   M3: + zone#year (i.bank_zone_id#i.year)          — 同区域同年共同冲击
*   M4: + 银行特定线性趋势 (c.year#i.bank_id)         — 行内线性时间趋势 (需 T>=3)
* 每级: 跑后 'quietly count if e(sample)' + N/参数守卫; 退化则不存 eststo。
* ============================================================================

* —— M0: 基线 bank + year ——
capture noisily reghdfe `DV' `TX' `CTRL_AVAIL', ///
    absorb(bank_id year) vce(cluster bank_id year)
if !_rc {
    quietly count if e(sample)
    * MD-A1-004: 补 e(df_m)>0 子句, 与 M1-M4 守卫对称 (df_m=0 = 主处理被完全吸收, 无识别)
    if r(N) > 0 & e(df_m) != . & e(df_m) > 0 {
        eststo feM0
    }
    else display "  [SKIP] M0: e(sample) 为空或主处理被完全吸收 (df_m<=0), 跳过"
}
else display "  [SKIP] M0 reghdfe 失败 (rc=`=_rc')"

* —— M1: + province#year ——
capture confirm variable bank_province_id
if !_rc {
    capture noisily reghdfe `DV' `TX' `CTRL_AVAIL', ///
        absorb(bank_id year i.bank_province_id#i.year) vce(cluster bank_id year)
    if !_rc {
        quietly count if e(sample)
        if r(N) > 0 & e(df_m) != . & e(df_m) > 0 {
            eststo feM1
        }
        else display "  [SKIP] M1 (province#year): 过度吸收 / 无残余变异 (T=`nyears' 退化), 跳过"
    }
    else display "  [SKIP] M1 reghdfe 失败 (rc=`=_rc'); T=`nyears' 下 province#year 常过度吸收"
}
else display "  [SKIP] M1: bank_province_id 缺失, 跳过"

* —— M2: + bank-type#year ——
capture confirm variable bank_type_id
if !_rc {
    capture noisily reghdfe `DV' `TX' `CTRL_AVAIL', ///
        absorb(bank_id year i.bank_type_id#i.year) vce(cluster bank_id year)
    if !_rc {
        quietly count if e(sample)
        if r(N) > 0 & e(df_m) != . & e(df_m) > 0 {
            eststo feM2
        }
        else display "  [SKIP] M2 (type#year): 过度吸收 / 无残余变异 (T=`nyears' 退化), 跳过"
    }
    else display "  [SKIP] M2 reghdfe 失败 (rc=`=_rc'); T=`nyears' 下 type#year 常过度吸收"
}
else display "  [SKIP] M2: bank_type_id 缺失, 跳过"

* —— M3: + zone#year ——
capture confirm variable bank_zone_id
if !_rc {
    capture noisily reghdfe `DV' `TX' `CTRL_AVAIL', ///
        absorb(bank_id year i.bank_zone_id#i.year) vce(cluster bank_id year)
    if !_rc {
        quietly count if e(sample)
        if r(N) > 0 & e(df_m) != . & e(df_m) > 0 {
            eststo feM3
        }
        else display "  [SKIP] M3 (zone#year): 过度吸收 / 无残余变异 (T=`nyears' 退化), 跳过"
    }
    else display "  [SKIP] M3 reghdfe 失败 (rc=`=_rc'); T=`nyears' 下 zone#year 常过度吸收"
}
else display "  [SKIP] M3: bank_zone_id 缺失, 跳过"

* —— M4: + 银行特定线性趋势 (需 T>=3 才可识别行内线性趋势) ——
if `nyears' >= 3 {
    capture noisily reghdfe `DV' `TX' `CTRL_AVAIL', ///
        absorb(bank_id year c.year#i.bank_id) vce(cluster bank_id year)
    if !_rc {
        quietly count if e(sample)
        if r(N) > 0 & e(df_m) != . & e(df_m) > 0 {
            eststo feM4
        }
        else display "  [SKIP] M4 (bank linear trend): 无残余变异, 跳过"
    }
    else display "  [SKIP] M4 reghdfe 失败 (rc=`=_rc')"
}
else {
    display "  [SKIP] M4 (银行线性趋势): T=`nyears' < 3, 线性趋势不可识别 → 优雅跳过 (production T=19 才有功效)"
}

* ── Panel A 输出 (esttab 名单动态化, 缺名不点名防 r(111) 丢整表) ───────────────
qui estimates dir
local stored `r(names)'
local cand_models feM0 feM1 feM2 feM3 feM4
local cand_titles `""bank+year" "+prov#yr" "+type#yr" "+zone#yr" "+bank trend""'
local models ""
local mtitles `""'
local nmod : word count `cand_models'
forvalues i = 1/`nmod' {
    local m : word `i' of `cand_models'
    if `: list m in stored' {
        local models `models' `m'
        local t : word `i' of `cand_titles'
        local mtitles `"`mtitles' "`t'""'
    }
}

if "`models'" == "" {
    display as error "  [WARN] Panel A 无任何已存储估计 (T=`nyears' 退化或 DV 缺); Panel A 跳过"
}
else {
    * MD-A1-005: esttab/estout 包 capture noisily — keep(`TX') 在某些退化列下若系数被
    * 吸收/缺失会 r(111); 包 capture 后不丢整表, 仍打印诊断。
    capture noisily esttab `models' ///
        using "$tables_dir/tableA1_fe_saturation_oster.tex", replace ///
        star(* 0.10 ** 0.05 *** 0.01) se booktabs label compress b(4) se(4) ///
        keep(`TX') ///
        stats(N r2_within, fmt(0 4) labels("N" "Within R²")) ///
        title("Table A1 Panel A: FE Saturation Ladder (Disagreement -> Z-score)") ///
        mtitles(`mtitles') ///
        addnotes("Treatment = cross_outlet_tone_variance_full (full track, paper_spec governance.main_track=_full)." ///
                 "Ladder adds group-by-year FE absorbing common shocks to same-province / same-type / same-zone banks within a year, then bank-specific linear trends (c.year#i.bank_id, requires T>=3)." ///
                 "province_fe was promised in paper_spec.fixed_effects [bank_fe,year_fe,province_fe] but never implemented in Tables 2/4 — this table closes that gap." ///
                 "Cluster-robust SE (bank+year two-way) in parentheses." ///
                 "Group-by-year FE / bank trends are over-absorptive at the retired T=2 trial panel (2017-2018) and degrade gracefully; full power at production T=19." ///
                 "Method: Gormley & Matsa (2014, RFS 27(2):617-661, doi:10.1093/rfs/hht047).")

    capture noisily estout `models' using "$tables_dir/tableA1_fe_saturation_oster.csv", replace ///
        delimiter(",") cells(b(star fmt(4)) se(par fmt(4))) ///
        stats(N r2_within, fmt(0 4)) starlevels(* 0.10 ** 0.05 *** 0.01) ///
        keep(`TX')

    display "[OK] Table A1 Panel A (FE-SAT) -> $tables_dir/tableA1_fe_saturation_oster.{tex,csv}"
}

* ============================================================================
* Panel B: Oster (2019) δ (selection on unobservables)
*   受控回归: regress DV TX `SUBST'(可观测 substantive 控制) i.bank_id i.year
*   psacalc delta TX, rmax(1.3 * R²_controlled) mcontrol(i.bank_id i.year)
*   ⚠ 识别口径 (MD-A1-002 订正): δ 由可观测 substantive 控制 (`SUBST') 相对
*     "仅 FE 基线" 的 R²-movement 界定; FE 哑变量项 (i.bank_id i.year) 进 mcontrol
*     作为始终包含、不参与识别 δ 的 nuisance。这与 "standard Oster (2019)" 一致:
*     δ = 把 TX 系数压到 0 所需的不可观测选择性相对**可观测控制**的强度比。
*   δ > 1 (Oster 经验法则) → 结论对'剩余不可观测选择性'稳健。
* 守卫:
*   (i)  capture which psacalc  — SSC 命令, 未装则 Panel B 跳过 (视为正常)
*   (ii) 需至少 1 个 substantive 控制 + DV + TX, 受控回归 e(sample)>0 / R² 可得 /
*        R²<0.9999 (非完全饱和) / T>=3 (非早期试跑 T=2 高阶共线退化)
* ============================================================================

capture which psacalc
if _rc {
    display "  [WARN] psacalc not installed (ssc install psacalc); Panel B (Oster δ) 跳过 (正常)"
}
else {
    * MD-A1-002: 可观测 substantive 控制集对齐 paper_spec (是 δ 的"可观测移动"来源,
    * 不是 psacalc 的 mcontrol)。spec 承诺的控制:
    *   - is_soe (controls.bank_level:148) — implicit-guarantee 框架
    *   - network_roles.control.columns:254 = bank_degree_cent + brokerage_eigen_cent
    *     (覆盖广度混淆控: 防"分歧度=覆盖广度"伪信号; Diether-Malloy-Scherbina 2002 JF)
    * 此前误把 spec-外列 (digital_frontier / bank_effective_size / bank_between_cent)
    * 混入, 且漏了 spec 指定的 brokerage_eigen_cent → 现严格对齐 spec, 仅留 spec 列。
    local SUBST_CAND is_soe bank_degree_cent brokerage_eigen_cent
    local SUBST ""
    foreach v of local SUBST_CAND {
        capture confirm variable `v'
        if !_rc local SUBST "`SUBST' `v'"
    }
    local SUBST "`SUBST' `CTRL_AVAIL'"
    local SUBST : list uniq SUBST

    * 至少需要 1 个 substantive 可观测控制 (δ 由它们相对 FE 基线的 R²-movement 界定)
    local n_subst : word count `SUBST'
    if `n_subst' == 0 {
        display "  [WARN] Panel B: 无任何在盘 substantive 控制 (is_soe / 网络 / 财务全缺); Oster δ 跳过"
    }
    else {
        * ── family-wide Oster mcontrol 修复 (MD-A1-002 核心) ──────────────────────
        * 原理: psacalc 的 mcontrol() = "始终包含、不参与识别 δ 的 nuisance"。要让 δ
        *   由可观测 substantive 控制 (`SUBST') 相对 FE 基线的 R²-movement 驱动, mcontrol
        *   必须只放 FE 哑变量项 (bank / year 哑), 不放 substantive 控制。
        * 此前 mcontrol(`MCTRL') 把 is_soe 等 substantive 控制全塞进 nuisance → δ 不再由
        *   可观测控制移动界定, 与 "standard Oster (2019)" framing 不符。现订正:
        *   受控回归 regress DV TX SUBST <FE哑>; mcontrol(<FE哑>)。
        * ⚠ psacalc 的 mcontrol() 只接受**已展开的实变量名** (e(b) 里的列名), 不接受
        *   factor 语法 i.bank_id (会报 "Unrelated control not in regression" rc=5001)。
        *   故先用 xi 把 i.bank_id / i.year 物化为真哑变量 (_Ibank_id_* / _Iyear_*),
        *   regress 与 mcontrol 同用这组哑变量名 (mcontrol 实名单见下方按 e(b) 筛选)。
        capture drop _Ibank_id_*
        capture drop _Iyear_*
        capture noisily xi i.bank_id i.year
        * 受控回归 (psacalc 紧接其后, 读 e(sample)/R²/e(b)/e(V) 含全部 RHS; regress 而非
        *   reghdfe — 后者吸收变量不入 e(b), psacalc 取不到 FE 系数)。
        capture noisily regress `DV' `TX' `SUBST' _Ibank_id_* _Iyear_*, vce(cluster bank_id)
        if _rc {
            display "  [SKIP] Panel B: 受控回归失败 (rc=`=_rc'; T=`nyears' 退化可能完全共线)"
        }
        else {
            quietly count if e(sample)
            local nsamp = r(N)
            local r2c = e(r2)
            * mcontrol 实名单: 只收 e(b) 中**实际带系数 (非 omitted)** 的 FE 哑变量名。
            * psacalc 拒绝 e(b) 里被 regress 标 omitted (o.) / 完全不在回归的列名 →
            * 直接传 _Ibank_id_* 通配会含被丢哑变量而 rc=5001; 故逐列筛 e(b) 头部名。
            local FE_MCTRL ""
            local _bnames : colnames e(b)
            foreach _c of local _bnames {
                if strpos("`_c'", "_Ibank_id_") == 1 | strpos("`_c'", "_Iyear_") == 1 {
                    * 跳过 omitted (o. 前缀) 与 base (b. 前缀) 标记列
                    if strpos("`_c'", "o.") == 0 & strpos("`_c'", "b.") == 0 {
                        local FE_MCTRL "`FE_MCTRL' `_c'"
                    }
                }
            }
            local n_femc : word count `FE_MCTRL'
            * MD-A1-003: 守卫追加完全饱和检测 — 受控回归展开 ~87 bank 哑变量, 稀疏 TX
            *   子样本必致 R²≈1 (psacalc 在 rmax 接近受控 R² 时 δ 病态/发散)。
            *   r2c>=0.9999 或 nyears<3 时跳过 (早期试跑 T=2 高阶共线退化); FE 哑全被丢 (n_femc=0) 亦跳过。
            if `nsamp' == 0 | `r2c' == . | `r2c' >= 0.9999 | `nyears' < 3 | `n_femc' == 0 {
                display "  [SKIP] Panel B: 受控回归 e(sample) 空 / R² 不可得 / R²≈1 完全饱和 (r2c=`r2c') / T=`nyears'<3 退化 / 无存活 FE 哑变量 (n_femc=`n_femc'), Oster δ 跳过 (production T=19 才有功效)"
            }
            else {
                local rmax = min(1, 1.3 * `r2c')
                display "  [INFO] Oster: 受控 R² = `r2c', rmax = 1.3*R² (capped at 1) = `rmax'"
                display "  [INFO]   δ-drivers (substantive 可观测控制) = `SUBST'"
                display "  [INFO]   mcontrol (FE nuisance, 不参与 δ 识别) = `n_femc' 个 FE 哑变量 (_Ibank_id_* / _Iyear_*)"
                capture noisily psacalc delta `TX', rmax(`rmax') mcontrol(`FE_MCTRL')
                if !_rc {
                    * 立即捕获 r(delta)/r(beta) 为 local (后续 file 操作不清 r(), 但守 SSOT 规约)
                    local oster_delta = r(delta)
                    local oster_beta  = r(beta)
                    display "  [OK] Oster δ (`TX') = `oster_delta'  (>1 => robust to unobservable selection; Oster 2019 rule of thumb)"
                    display "       δ 由可观测 substantive 控制 (`SUBST') 相对 FE 基线的 R²-movement 界定。"
                    * 落盘 Panel B 单行 CSV side-channel (parse_esttab_csv 之外, 标量诊断行)
                    capture file close _psf
                    capture noisily file open _psf using "$tables_dir/tableA1_oster_delta.csv", write replace
                    file write _psf "panel,treatment,DV,oster_delta,beta_controlled,rmax,r2_controlled,n_subst,n_sample" _n
                    file write _psf "OSTER,`TX',`DV',`oster_delta',`oster_beta',`rmax',`r2c',`n_subst',`nsamp'" _n
                    file close _psf
                    display "[OK] Table A1 Panel B (OSTER δ) -> $tables_dir/tableA1_oster_delta.csv"
                }
                else {
                    display "  [SKIP] Panel B: psacalc 计算失败 (rc=`=_rc'; T=`nyears' 退化 / 共线), Oster δ 跳过"
                }
            }
        }
    }
}

display ""
display "=========================================="
display "Table A1 (FE-SAT + OSTER) 完成 (退化项已优雅跳过, 见上 [SKIP] 日志)"
display "=========================================="
