* news_process v3.7.0 — 第 10 篇 数据准备
*
* 输入:
*   data/processed/49_risk_taking_outcomes.dta (stage 49 输出, V2 E2E 修复)
*   data/processed/bank_metadata.dta           (bank_list.yaml 派生)
*   (可选) data/processed/40_panel_yearly.dta  (stage 45 主面板, 含 treatment)
*
* 输出 (内存中):
*   working dataset 含 z_score / npl_formation / rwa_to_ta + treatment +
*   bank metadata (is_soe / bank_type_id / tier).
*
* V4 audit F-P1.1 必备: implicit_guarantee_tier merge.

version 19
clear all

* 主 outcome panel
use "data/processed/49_risk_taking_outcomes.dta", clear

* Encode bank_id (Stata xtset 需要数值 ID)
encode target_bank, gen(bank_id)
xtset bank_id year

* Merge bank metadata (V4 F-P1.1: SOE/tier for implicit guarantee 异质性)
* 注: bank_metadata.dta 已包含 is_soe/bank_type_id/tier; 若 stage 49 输出已含
* 这些列, 此 merge 为 no-op (Stata merge keep 行为正确处理).
capture merge m:1 target_bank using "data/processed/bank_metadata.dta", ///
    keep(master match) nogen
if _rc != 0 {
    display "WARNING: bank_metadata.dta 不可读, 使用 stage 49 内嵌 metadata"
}

* Treatment 列: cross_outlet_tone_variance (V4 R3 critical 修复)
* 注: 主 panel 中暂无此列, M2-M3 创建后启用.
* 当前 placeholder: 用现有 llm_vote_tone_std 作为 fallback.
capture merge 1:1 target_bank year using "data/processed/40_panel_yearly.dta", ///
    keep(master match) nogen keepusing(llm_vote_tone_std_full ///
    cross_outlet_tone_variance_full)
if _rc != 0 {
    display "WARNING: 40_panel_yearly.dta 不可读 — main treatment 不可用"
}

* 派生 controls (V4 F-P1.1)
capture confirm variable ln_assets
if _rc != 0 & "total_assets" != "" {
    gen ln_assets = ln(total_assets) if total_assets > 0
}

* 排序保证 xtset 顺序
sort bank_id year

* Save instrumented dataset
save "data/processed/_paper10_working.dta", replace
display "  Working dataset saved: data/processed/_paper10_working.dta"
display "  N = " _N ", banks = " _N / (2024 - 2007 + 1)
