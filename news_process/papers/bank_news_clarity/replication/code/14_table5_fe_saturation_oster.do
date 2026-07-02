* news_process — 第 11 篇 (bank_news_clarity, PROVISIONAL) Table 5:
*   Panel A — 固定效应饱和阶梯 (FE saturation ladder)
*   Panel B — Oster (2019) δ 选择性偏误 (unobservable selection)
*
* ── NC-TABLE-NUMBERING-04 (仅注释, 勿改 spec/文件名) ─────────────────────────
*   本表内部 title 标 "Table 5", 但 paper_spec 的 t5 主表槽已被占用 → manuscript
*   排版时应把本表编入 **附录 tA-series** (如 Table A-FE-Saturation / Table A?),
*   避免与正文主表 Table 5 撞号。此处只标注, 不改 paper_spec / 文件名 / 00_master
*   (那些由主控统一处理)。
*
* ----------------------------------------------------------------------------
* 是什么 / 为什么 / 影响 (一行大白话):
*   是什么: 给主回归"层层加更细的固定效应", 再用 Oster δ 量化"看不见的遗漏
*           变量得多强才能推翻结论"。
*   为什么: 现有主表 (11_table2) 最高只到 bank+year 双向 FE; clarity 处理可能
*           与"区域媒体生态 / 银行类型监管周期 / 省级宏观冲击"混淆, 须证主系数
*           吸收掉这些混淆维度后仍稳。Oster δ 是观察性识别的标配选择性偏误诊断。
*   影响: 纯消费在盘列, 不写回任何 processed/golden 产物; DV=z_score 为 sentinel
*         (外部财务面板待接入), 缺列时整 panel 优雅 wire-ahead 跳过, 不报错中断。
*
* ----------------------------------------------------------------------------
* Panel A — FE saturation ladder (Gormley & Matsa 2014 framework):
*   M0: bank + year 双向 FE (= 主表基线)
*   M1: + province × year   (i.bank_province#i.year)  省级时变宏观冲击
*   M2: + bank_type × year  (i.bank_type#i.year)      类型监管周期
*   M3: + bank_zone × year  (i.bank_zone#i.year)      区域媒体生态
*   M4: + bank-specific linear trend (c.year#i.bank_id)  T≥3 守卫 (盘面 T=2 退化跳过)
*
* Panel B — Oster (2019) δ:
*   psacalc delta TREAT, rmax(1.3 * R²_controlled) mcontrol(<受控回归里的 FE 哑变量项>)
*   ⚠ mcontrol = "始终包含、不参与识别 δ 的 nuisance"。受控回归 = reg DV TX
*     CTRL_B CTRL_Y i.bank_id i.year, 要让 δ 由可观测 substantive 财务/宏观控制
*     (CTRL_B+CTRL_Y) 相对 FE 基线的 R²-movement 驱动 → mcontrol 只放 FE 哑变量
*     项 (i.bank_id i.year), 不放 substantive 控制。复用 11_table2 的 CTRL_B /
*     CTRL_Y 控制集 (它们进受控回归 RHS 但不进 mcontrol); capture which psacalc 守卫。
*
* 文献锚点 (Anchor):
*   Gormley, T. A., & Matsa, D. A. (2014). Common errors: How to (and not to)
*     control for unobserved heterogeneity. Review of Financial Studies, 27(2),
*     617-661. doi:10.1093/rfs/hht047
*   Oster, E. (2019). Unobservable selection and coefficient stability: Theory
*     and evidence. Journal of Business & Economic Statistics, 37(2), 187-204.
*     doi:10.1080/07350015.2016.1227711
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

* 处理变量在盘是硬前提 (面板核心列), 缺则整表跳过 (不应发生)
capture confirm variable `TX'
if _rc {
    display as error "  [WARN] 处理变量 `TX' 不在面板; Table 5 整表跳过"
    exit 0
}

* ── DV sentinel 守卫 (wire-ahead): z_score 为外部财务面板列, 当前盘缺 ──────
* 缺列时本表全部回归无法跑, 优雅跳过 (production 财务接入后自动激活)。
capture confirm variable `DV'
local DV_OK = (_rc == 0)
if !`DV_OK' {
    display "  [WIRE-AHEAD] 结果变量 `DV' 未物化 (外部财务面板待接入);" ///
            " Table 5 Panel A/B 守卫跳过, 仅占位。"
}

* ── FE 分组列守卫: 缺列则该阶梯项不加 (degrade) ─────────────────────────
* bank_province / bank_type / bank_zone 在盘为字符串 → encode 为数值 id 供
* factor-variable 交互 (i.var#i.year)。
foreach g in bank_province bank_type bank_zone {
    capture confirm variable `g'
    if !_rc {
        capture confirm numeric variable `g'
        if _rc {
            capture confirm string variable `g'
            if !_rc {
                capture encode `g', gen(`g'_id)
            }
        }
        else {
            capture clonevar `g'_id = `g'
        }
    }
}

* ============================================================================
* Panel A — 固定效应饱和阶梯
* ============================================================================
if `DV_OK' {

    * ── NC-NGUARD-LISTWISE-02 / NC-TWOWAY-CLUSTER-T2-05 共用量 ───────────────
    * MINEST: post-est e(N) 守卫阈值。上游守卫仅确认 treatment 在盘, 未防 8 个
    *   财务/宏观控制 (CTRL_B+CTRL_Y) listwise-delete 后估计样本塌缩 → 每个 eststo
    *   后读 e(N), 太小则 estimates drop 该退化列 (esttab 名单据 estimates dir 动态
    *   收集 → drop 后自然不进表)。
    * _nyr_cl: year 簇数 (双向 cluster(bank_id year) 的第二维)。盘面 T=2 / 生产
    *   ~18, 少簇 → cluster-robust SE 渐近近似差, addnotes 显式披露 + caveat。
    local MINEST 20
    quietly levelsof year, local(_yrs)
    local _nyr : word count `_yrs'
    local _nyr_cl `_nyr'

    * M0: bank + year 双向 FE (= 主表基线)
    capture noisily eststo A_m0: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
        absorb(bank_id year) vce(cluster bank_id year)
    if _rc==0 & e(N) < `MINEST' {
        display "  [N 守卫] M0 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — 退化, drop"
        capture estimates drop A_m0
    }

    * M1: + province × year (省级时变宏观冲击)
    capture confirm variable bank_province_id
    if !_rc {
        capture noisily eststo A_m1: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
            absorb(bank_id i.bank_province_id#i.year) vce(cluster bank_id year)
        if _rc==0 & e(N) < `MINEST' {
            display "  [N 守卫] M1 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — 退化, drop"
            capture estimates drop A_m1
        }
    }
    else {
        display "  [SKIP] bank_province 缺/不可 encode — Panel A M1 跳过"
    }

    * M2: + bank_type × year (类型监管周期)
    capture confirm variable bank_type_id
    if !_rc {
        capture noisily eststo A_m2: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
            absorb(bank_id i.bank_type_id#i.year) vce(cluster bank_id year)
        if _rc==0 & e(N) < `MINEST' {
            display "  [N 守卫] M2 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — 退化, drop"
            capture estimates drop A_m2
        }
    }
    else {
        display "  [SKIP] bank_type 缺/不可 encode — Panel A M2 跳过"
    }

    * M3: + bank_zone × year (区域媒体生态)
    capture confirm variable bank_zone_id
    if !_rc {
        capture noisily eststo A_m3: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
            absorb(bank_id i.bank_zone_id#i.year) vce(cluster bank_id year)
        if _rc==0 & e(N) < `MINEST' {
            display "  [N 守卫] M3 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — 退化, drop"
            capture estimates drop A_m3
        }
    }
    else {
        display "  [SKIP] bank_zone 缺/不可 encode — Panel A M3 跳过"
    }

    * M4: + bank-specific linear trend (c.year#i.bank_id) — 需 T≥3
    * T=2 退化守卫: 每个银行只 2 个时点时银行特定线性趋势完美共线 → 跳过。
    if `_nyr' >= 3 {
        capture noisily eststo A_m4: reghdfe `DV' `TX' `CTRL_B' `CTRL_Y', ///
            absorb(bank_id year c.year#i.bank_id) vce(cluster bank_id year)
        if _rc==0 & e(N) < `MINEST' {
            display "  [N 守卫] M4 控制 listwise 后 e(N)=`=e(N)' (<`MINEST') — 退化, drop"
            capture estimates drop A_m4
        }
    }
    else {
        display "  [T=2 退化] 仅 `_nyr' 个年度 (<3) — Panel A M4 银行线性趋势跳过" ///
                " (production T≥3 才有功效)"
    }

    * ── esttab 名单动态化 (缺估计不点名, 防 r(111) 丢整表) ──────────────
    qui estimates dir
    local stored `r(names)'
    local cand_models A_m0 A_m1 A_m2 A_m3 A_m4
    local cand_titles `""+Bank+Year" "+Prov#Year" "+Type#Year" "+Zone#Year" "+Bank trend""'
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

    if "`models'" != "" {
        esttab `models' ///
            using "output/tables/table5_panelA_fe_saturation.tex", replace ///
            booktabs label se star(* 0.10 ** 0.05 *** 0.01) ///
            b(%9.4f) se(%9.4f) compress ///
            stats(N r2, fmt(0 3) labels("N" "R²")) ///
            title("Table 5 Panel A: FE Saturation Ladder (Clarity -> Risk-Taking)") ///
            mtitles(`mtitles') ///
            keep(`TX') ///
            addnotes("Progressive high-dimensional FE absorbed via reghdfe; cluster-robust SE (bank+year two-way)." ///
                     "Treatment = mean_clarity_score_full (You 2018 dictionary, _full main track; full-only gating 2026-06-29, _ctx twin = primary robustness)." ///
                     "M1 absorbs province x year; M2 bank-type x year; M3 zone x year; M4 adds bank-specific linear trend (needs T>=3)." ///
                     "Two-way cluster on (bank, year): year clusters = `_nyr_cl' (current panel); few-cluster caveat applies when year clusters are small (T=2 trial / production T~18). With <~30 clusters in a dimension, asymptotic cluster-robust SE are unreliable; production should report wild-cluster-bootstrap (boottest) p-values for the year dimension." ///
                     "Controls (CTRL_B+CTRL_Y) listwise-deleted; columns with post-estimation e(N) < `MINEST' are dropped as degenerate." ///
                     "Framework: Gormley & Matsa (2014, RFS 27(2):617-661, doi:10.1093/rfs/hht047) on controlling for unobserved heterogeneity.")
        * CSV side-channel (parse_esttab_csv 消费)
        esttab `models' ///
            using "output/tables/table5_panelA_fe_saturation.csv", replace ///
            plain b(%9.4f) se(%9.4f) ///
            stats(N r2, fmt(0 3)) keep(`TX')
        display "[OK] 14_table5 Panel A -> output/tables/table5_panelA_fe_saturation.{tex,csv}"
    }
    else {
        display as error "  [WARN] Panel A 无任何已存储估计 — 表跳过 (FE 列或 DV 全缺)"
    }

    eststo clear
}

* ============================================================================
* Panel B — Oster (2019) δ 选择性偏误
* ============================================================================
* psacalc delta TREAT, rmax(1.3 * R²_controlled) mcontrol(<bank+year FE 哑变量>)
* 白话: 估算"看不见的遗漏变量得有多强 (相对已观测的 substantive 财务/宏观控制),
*       才能把主系数解释为零"。δ ≥ 1 通常视为对未观测混淆稳健 (Oster 2019)。
* 识别口径 (订正): δ 由可观测 substantive 控制 (CTRL_B+CTRL_Y) **相对 bank+year
*       FE 基线**的 R²-movement 界定 — 故 mcontrol 只放 FE 哑变量 (bank+year FE,
*       始终包含、不参与识别 δ 的 nuisance), substantive 控制留在受控回归 RHS 但
*       不进 mcontrol。这与"把 substantive 控制塞进 mcontrol"的写法语义相反 (后者
*       会让 FE 而非 substantive 控制驱动 δ, 偏离 OVB 诊断本意)。
*       ⚠ psacalc 不接受 i. factor 记号 → 物化显式 FE 哑变量 (_byr_*/_fyr_*) 传入。
* ----------------------------------------------------------------------------
capture which psacalc
if _rc {
    display "  [SKIP] psacalc 未安装 (ssc install psacalc) — Panel B Oster δ 跳过 (视为正常)"
}
else if !`DV_OK' {
    display "  [WIRE-AHEAD] DV `DV' 未物化 — Panel B Oster δ 跳过"
}
else {
    * 仅保留在盘的控制列 (sentinel 控制缺则不进 mcontrol, 避免 r(111))
    local CTRL_ALL ""
    foreach c in `CTRL_B' `CTRL_Y' {
        capture confirm variable `c'
        if !_rc local CTRL_ALL `CTRL_ALL' `c'
    }
    local nctrl : word count `CTRL_ALL'

    if `nctrl' == 0 {
        display "  [SKIP] 无任何在盘 substantive 控制变量 (sentinel 财务/宏观控制全缺)" ///
                " — Panel B Oster δ 需 substantive 控制驱动 R²-movement, 跳过"
    }
    else {
        * ── psacalc mcontrol 须为受控回归里"按名出现"的回归元 ────────────────
        * psacalc 的 mcontrol() 不接受 factor-variable 记号 (i.bank_id i.year):
        * 那会报 "Unrelated control not in regression" (rc 5001), 因为 i. 展开成
        * 1bn.bank_id / 2017.year 等虚拟名, 与裸名 bank_id/year 不匹配。
        * 解法: 物化显式 FE 哑变量 (_byr_* / _fyr_*, 各去一基组防与常数共线),
        * 受控回归按名纳入它们, mcontrol 传同一批名 → δ 由 substantive 控制
        * (CTRL_ALL) 相对这些 FE 哑变量基线的 R²-movement 驱动。
        capture drop _byr_*
        capture drop _fyr_*
        quietly tabulate bank_id, generate(_byr_)
        quietly tabulate year,    generate(_fyr_)
        * 去基组 (第一档) 防完全共线; psacalc 对完全共线的 mcontrol 亦会失败。
        capture drop _byr_1
        capture drop _fyr_1
        unab _FE_DUM : _byr_* _fyr_*
        local n_fe : word count `_FE_DUM'

        * 受控回归 (controlled): RHS = TX + substantive 控制 (CTRL_ALL) + FE 哑变量
        * (显式 _byr_*/_fyr_*)。取 R²_controlled, rmax = 1.3 × R²_controlled
        * (Oster 2019 建议 rmax ≈ 1.3 × controlled R² 作上界)。
        capture noisily reg `DV' `TX' `CTRL_ALL' `_FE_DUM'
        if _rc == 0 {
            * ── NC-NGUARD-LISTWISE-02: post-est e(N) 守卫 ───────────────────
            * 上游 N 守卫只 count treatment 非缺, 未防 8 个财务/宏观控制 listwise-
            * delete 后实际估计样本 e(N) 塌缩。受控回归后读 e(N): 太小则
            * psacalc 的 R²/δ 无意义 (退化), 优雅跳过 (production 全样本激活)。
            local e_n = e(N)
            local r2c = e(r2)
            local rmax = min(1, 1.3 * `r2c')
            if `e_n' < 20 {
                display "  [N 守卫] 受控回归 listwise 后 e(N)=`e_n' (<20); 8 财务/宏观控制" ///
                        " 大量缺失致样本塌缩 — Panel B Oster δ 退化跳过 (production T=18 激活)"
            }
            else {
            display "  [Oster] R²_controlled = `r2c'; rmax = `rmax' (=min(1, 1.3*R²_c)); e(N)=`e_n'"

            * ── NC-OSTER-MCONTROL-01 (核心 P1) ──────────────────────────────
            * mcontrol = FE 哑变量项 (显式 _byr_*/_fyr_*, 即 bank+year FE) ONLY —
            * 让 δ 由可观测 substantive 控制 (CTRL_ALL) 相对 FE 基线的 R²-movement
            * 驱动。旧写法 mcontrol(`CTRL_ALL') 把 substantive 控制当 nuisance, 反让
            * FE 驱动 δ, 偏离 OVB 诊断本意 → 已订正为 mcontrol(FE 哑变量)。
            * (psacalc 不接受 i. factor 记号 → 用上面物化的显式哑变量名传入。)
            capture noisily psacalc delta `TX', ///
                rmax(`rmax') mcontrol(`_FE_DUM')
            if _rc == 0 {
                * r(delta) 须在任何 estimates restore / 重跑前先 local 捕获
                * (restore/重跑清空 r()); 对齐 substance/24:193 范式。
                local oster_d = r(delta)
                local oster_b = r(beta)
                display "  [Oster δ] mean_clarity_score_full delta = `oster_d' (beta@δ=1 = `oster_b')"
                display "  解读: δ 由 substantive 财务/宏观控制相对 bank+year FE 基线的" ///
                        " R²-movement 界定; δ >= 1 = 主系数对未观测选择性偏误稳健 (Oster 2019)。"

                * CSV side-channel: 写出 δ 标量 (parse_esttab_csv 兼容的简表)
                capture file close _ofh
                file open _ofh using "output/tables/table5_panelB_oster_delta.csv", ///
                    write replace
                file write _ofh "metric,value" _n
                file write _ofh "treatment,mean_clarity_score_full" _n
                file write _ofh "oster_delta,`oster_d'" _n
                file write _ofh "oster_beta_at_delta1,`oster_b'" _n
                file write _ofh "r2_controlled,`r2c'" _n
                file write _ofh "rmax,`rmax'" _n
                file write _ofh "n_subst_controls,`nctrl'" _n
                file write _ofh "e_N,`e_n'" _n
                file write _ofh "n_fe_dummies,`n_fe'" _n
                file write _ofh "mcontrol,bank+year FE dummies only (_byr_*/_fyr_*)" _n
                file close _ofh
                display "[OK] 14_table5 Panel B -> output/tables/table5_panelB_oster_delta.csv"
            }
            else {
                display "  [WARN] psacalc delta 运行失败 (rc=`=_rc'); 可能样本/共线退化 — 跳过"
            }
            }
        }
        else {
            display "  [WARN] 受控回归失败 (rc=`=_rc'); Oster R²_controlled 不可得 — 跳过"
        }
        * 清理临时 FE 哑变量 (不污染下游 / 不写盘)
        capture drop _byr_*
        capture drop _fyr_*
    }
    eststo clear
}

display ""
display "=========================================="
display "Table 5 (FE saturation + Oster δ) 跑完"
display "=========================================="
