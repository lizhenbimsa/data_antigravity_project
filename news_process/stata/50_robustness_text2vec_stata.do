/* 
  50_robustness_text2vec_stata.do
  数据双轨验证方案：基于 Text2Vec (全文/上下文) 的稳健性特征测试
*/

clear all
set more off

// 1. 挂载数据 (确保 Python 轨已先运行导出 .dta)
use "output/40_panel_yearly.dta", clear

// 2. 致命隐患规避：生成数值型面板 ID
encode target_bank, generate(bank_id)
xtset bank_id year

// 宏定义：基础控制变量集 (可依据主回归模型调整)
global controls "bank_scale_ord is_soe" 

// 3. 双轨稳健性检验 (双向固定效应 TWFE)
// 【学术机制】Two-Way Fixed Effects Estimator (Gormley & Matsa 2014, RFS)
// 引入 个体固定效应 (bank_id) 控制不随时间变化的不可观测异质性（如企业文化）；
// 引入 时间固定效应 (year) 吸收宏观经济冲击。使用聚类稳健标准误 (vce cluster) 纠正面板异方差与自相关。
// 【通俗应用】把银行天生带有的固有特性（固定效应）剥离掉，只看由于政策或差异化导致的净变化。

// 注意：请将 'DV' 替换为您实际的被解释变量 (如 ln_penalty_amount, ROA 等)

// --- 轨道 1: 权威响应度 (AP) 双轨对比 ---
reghdfe DV policy_cosine_sim_t2v_full $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_ap_full

reghdfe DV policy_cosine_sim_t2v_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_ap_ctx

// --- 轨道 2: 战略差异度 (SD) 双轨对比 ---
reghdfe DV strat_diff_t2v_full $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_sd_full

reghdfe DV strat_diff_t2v_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
est store m_sd_ctx

// 4. 导出 LaTeX 学术表格 (双轨并列呈现)
esttab m_ap_full m_ap_ctx m_sd_full m_sd_ctx using "output/robustness_t2v_dual_track.tex", ///
    replace label b(3) p(3) star(* 0.10 ** 0.05 *** 0.01) ///
    indicate("Bank FE = *bank_id" "Year FE = *year")
