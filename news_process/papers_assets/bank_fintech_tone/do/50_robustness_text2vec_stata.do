/*
  50_robustness_text2vec_stata.do
  数据双轨验证方案：基于 Text2Vec (全文/上下文) 的稳健性特征测试

  ⚠ 现状说明 (2026-06-19 文档审计, legacy 脚本):
    (1) text2vec (_t2v) 稳健性列仍在生产, 但已改由 stage 15/25 内联产出 ——
        独立的 stage 30 编排已于 2026-05-29 退役 (现仅余 30a SBERT), 词典/列本身未删。
    (2) 本 Phase-4a 自包含脚本仅覆盖 full/ctx 两轨; v3.9.0 起项目已加入第三主轨 _ss
        (银行+金科同句), 生产 _t2v 列亦有 *_ss 孪生 (policy_cosine_sim_t2v_ss /
        strat_diff_t2v_ss)。如需三轨稳健性, 以主线 Stata 模板为准。
*/

clear all
set more off

* ----------------------------------------------------------------------------
* Phase 4a 路径前奏 — papers_assets/<paper>/do/ 自包含调用契约
* 默认假设当前工作目录是本 .do 文件所在目录:
*     news_process/papers_assets/bank_fintech_tone/do/
* 用户可通过 `global panel_dta "..."` / `global out_dir "..."` 显式覆盖
* (在 do 本文件之前 set 即可)。
* ----------------------------------------------------------------------------
if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
    capture mkdir "$out_dir"
}

// 1. 挂载数据 (确保 Python 轨已先运行导出 .dta)
use "$panel_dta", clear

// 2. 致命隐患规避：生成数值型面板 ID
encode target_bank, generate(bank_id)
xtset bank_id year

// 宏定义：基础控制变量集 (可依据主回归模型调整)
global controls "bank_scale_ord is_soe"

// 宏定义：被解释变量 DV (默认空, 用户在 do 本文件前 `global DV <列名>` 显式设置)
if "$DV" == "" {
    global DV ""
}
// 守卫：DV 未设置或不在面板中 → 可读跳过, 避免 reghdfe r(111) 未捕获中断
//       (财务会计列 ROA / ln_penalty_amount 等尚未并入 panel, 见 README 待补项)
capture confirm variable $DV
if _rc {
    di as error "DV 未设置或不存在于面板, 跳过 text2vec 稳健性表 (请先 global DV <被解释变量>)"
    exit, clear
}

// 3. 双轨稳健性检验 (双向固定效应 TWFE)
// 【学术机制】Two-Way Fixed Effects Estimator (Gormley & Matsa 2014, RFS)
// 引入 个体固定效应 (bank_id) 控制不随时间变化的不可观测异质性（如企业文化）；
// 引入 时间固定效应 (year) 吸收宏观经济冲击。使用聚类稳健标准误 (vce cluster) 纠正面板异方差与自相关。
// 【通俗应用】把银行天生带有的固有特性（固定效应）剥离掉，只看由于政策或差异化导致的净变化。

// 注意：被解释变量经宏 $DV 注入 (在 do 本文件前 `global DV <列名>`, 如 ln_penalty_amount / ROA 等)

// --- 轨道 1: 权威响应度 (AP) 双轨对比 ---
reghdfe $DV policy_cosine_sim_t2v_full $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_ap_full

reghdfe $DV policy_cosine_sim_t2v_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_ap_ctx

// --- 轨道 2: 战略差异度 (SD) 双轨对比 ---
reghdfe $DV strat_diff_t2v_full $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_sd_full

reghdfe $DV strat_diff_t2v_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_sd_ctx

// 4. 导出 LaTeX 学术表格 (双轨并列呈现)
esttab m_ap_full m_ap_ctx m_sd_full m_sd_ctx using "$out_dir/robustness_t2v_dual_track.tex", ///
    replace label b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    indicate("Bank FE = *bank_id" "Year FE = *year")

// standalone 脚本：终端 exit 收尾, 防 Windows /b 'Done' 完成框卡死 (见 CLAUDE.md Stata 约定)
exit, clear
