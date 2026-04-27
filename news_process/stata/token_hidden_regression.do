/*
 * token_hidden_regression.do
 * ============================================================================
 * Token/Hidden 采纳行为三层回归架构
 *
 * 【学术支撑】
 *   Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to impact.
 *   Research Policy, 55(3), 105426.
 *   https://doi.org/10.1016/j.respol.2026.105426
 *   → §3.2.1: Token (象征性采用) vs Hidden (实质性采用) 解耦
 *
 *   Westphal, J. D. & Zajac, E. J. (2001). Decoupling policy from practice.
 *   ASQ, 46(2), 202–228. https://doi.org/10.2307/2667086
 *   → Token Adoption 的制度理论基础
 *
 * 【白话说明】
 *   三层回归：
 *     层1 (主回归)：用连续变量看"政策对齐度"对银行绩效的影响
 *     层2 (机制检验)：用离散变量看"洗科技"和"闷声干大事"各自的影响
 *     层3 (稳健性)：换不同阈值和度量方式，看结论是否稳定
 * ============================================================================
 */

clear all
set more off

* --- 依赖检查 ---
* 需要安装以下用户编写的 Stata 命令 (首次运行时执行):
*   ssc install reghdfe, replace
*   ssc install ftools, replace
*   ssc install estout, replace

* --- 数据加载 ---
* 文件名与 45_panel_export_main.py L337-343 的导出逻辑一致:
*   panel_path = '40_panel_yearly.parquet' -> dta_path = '40_panel_yearly.dta'
use "40_panel_yearly.dta", clear

* --- 面板设定 ---
* encode: 将字符串型银行名转换为数值 ID (Stata 面板命令的要求)
encode target_bank, gen(bank_id)
xtset bank_id year

* --- 用户自定义控制变量 ---
* 请根据研究需要替换以下占位符:
*   Y (ROA / CAR / Z_score 等) 和 controls (控制变量组)
* global controls "ln_news_coverage media_breadth n_articles"

* ============================================================================
* 层 1: 主回归 — 连续变量 (零阈值争议)
* ============================================================================
* 【术语】使用连续变量消除阈值选择偏差
*   Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Statistics in
*   Medicine, 25(1), 127-141. https://doi.org/10.1002/sim.2331
* 【白话】直接用连续的"政策对齐分"做回归，不人为划线

* 主回归 1: 语义对齐度 → 银行绩效
reghdfe ROA article_sim_mean $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m1_sim

* 主回归 2: 交互项 — 词频 × 语义
*   假设: "说得多且做得真" 的乘积效应
gen freq_x_sim = fintech_intensity_mean * article_sim_mean
reghdfe ROA fintech_intensity_mean article_sim_mean freq_x_sim ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m2_interact

* ============================================================================
* 层 2: 机制检验 — P50 离散分类 (与项目中位数分割惯例一致)
* ============================================================================
* 【术语】使用四分位中位数 (P50) 离散分类
*   Li, K., Mai, F., Shen, R., & Yan, X. (2021). RFS, 34(7), 3265–3315.
*   https://doi.org/10.1093/rfs/hhaa079
*   → Tercile 分组在机制检验中的应用
* 【白话】用中位数把银行分成"洗科技多"和"真干事多"两组，看各自对绩效的影响

* Token (象征性采用) → 短期市场反应
reghdfe CAR token_adopt_kw_p50 $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m3_token_car

* Hidden (实质性采用) → 长期基本面
reghdfe ROA hidden_adopt_kw_p50 $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m4_hidden_roa

* Substantive (言行一致)
reghdfe ROA subst_adopt_kw_p50 $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m5_subst_roa

* ============================================================================
* 层 3: 稳健性检验
* ============================================================================
* 【白话】换不同的阈值 (P25/P75) 和度量方式 (INT轨)，看系数是否稳定

* 稳健性 A: P25 阈值 (宽松)
reghdfe ROA token_adopt_kw_p25 hidden_adopt_kw_p25 ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m6_p25

* 稳健性 B: P75 阈值 (严格)
reghdfe ROA token_adopt_kw_p75 hidden_adopt_kw_p75 ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m7_p75

* 稳健性 C: INT 轨 (TF-IDF×SIF 加权)
reghdfe ROA token_adopt_int_p50 hidden_adopt_int_p50 ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m8_int_track

* ============================================================================
* 输出回归表
* ============================================================================
esttab m1_sim m2_interact m3_token_car m4_hidden_roa m5_subst_roa ///
    m6_p25 m7_p75 m8_int_track ///
    using "token_hidden_results.tex", replace ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    se(3) b(3) ///
    title("Token/Hidden Adoption and Bank Performance") ///
    label compress
