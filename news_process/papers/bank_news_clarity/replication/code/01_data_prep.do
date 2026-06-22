* news_process v3.7.0 — 第 11 篇 数据准备
*
* 输入: 49_risk_taking_outcomes.dta (stage 49 已移除; outcome 待财务面板接入)
*       + bank_metadata.dta + 40_panel_yearly.dta
* (含 mean_clarity_score_{full,ctx} 等 v3.5.1 frozen 字段, 已在主 panel)

version 19
clear all

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

capture merge m:1 target_bank using "data/processed/bank_metadata.dta", ///
    keep(master match) nogen

* Merge clarity treatment from main panel (v3.5.1 已 frozen mean_clarity_score)
capture merge 1:1 target_bank year using "data/processed/40_panel_yearly.dta", ///
    keep(master match) nogen ///
    keepusing(mean_clarity_score_full mean_clarity_score_ctx ///
              mean_frac_definite_full mean_frac_definite_ctx ///
              frac_amb_articles_full frac_amb_articles_ctx ///
              mean_num_intensity_full mean_num_intensity_ctx)
if _rc != 0 {
    display "WARNING: 40_panel_yearly.dta 不可读 — main treatment 不可用"
}

* fix(omni-g-replication-08, 2026-06-11): 原条件 `"total_assets" != ""` 是两个字符串
* 字面量比较, 恒为真 (意图是检查变量存在性) → 在无 total_assets 的正典 stage 49
* 输出上无守卫执行 gen ln(total_assets) 即 r(111) 崩溃。改为 capture confirm 嵌套守卫。
capture confirm variable ln_assets
if _rc {
    capture confirm variable total_assets
    if !_rc {
        gen ln_assets = ln(total_assets) if total_assets > 0
    }
    else {
        display "WARNING: ln_assets/total_assets 均缺失 — 银行财务面板待接入 (config/银行面板2007-2025年.xlsx); ln_assets 控制不可用"
    }
}

* 第 11 篇额外: term_spread (10y - 1y 国债利差)
capture confirm variable term_spread
if _rc != 0 {
    gen term_spread = .   // placeholder; user 自行 merge 国债 yield curve
}

sort bank_id year
save "data/processed/_paper11_working.dta", replace
display "  Working dataset saved: data/processed/_paper11_working.dta"
