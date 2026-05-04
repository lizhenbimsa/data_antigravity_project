/*
 * token_hidden_regression.do
 * ============================================================================
 * Token/Hidden 采纳行为 + 经营效益态度投影 四层回归架构
 *
 * 【学术支撑】
 *   层 1-3:
 *   Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to impact.
 *   Research Policy, 55(3), 105426.
 *   https://doi.org/10.1016/j.respol.2026.105426
 *   → §3.2.1: Token (象征性采用) vs Hidden (实质性采用) 解耦
 *
 *   Westphal, J. D. & Zajac, E. J. (2001). Decoupling policy from practice.
 *   ASQ, 46(2), 202–228. https://doi.org/10.2307/2667086
 *   → Token Adoption 的制度理论基础
 *
 *   层 4:
 *   Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society?
 *   A language embedding approach. Review of Financial Studies, 39(5),
 *   1227–1266. https://doi.org/10.1093/rfs/hhaf012
 *   → §1.3.2 Eq. 1: 双极锚点投影测度经营效益情感态度
 *
 * 【白话说明】
 *   四层回归：
 *     层1 (主回归)：用连续变量看"政策对齐度"对银行绩效的影响
 *     层2 (机制检验)：用离散变量看"洗科技"和"闷声干大事"各自的影响
 *     层3 (稳健性)：换不同阈值和度量方式，看结论是否稳定
 *     层4 (态度投影)：用"利好经营 vs 损害经营"的态度分看对绩效的影响
 * ============================================================================
 */

clear all
set more off

* --- 依赖检查 ---
* 需要安装以下用户编写的 Stata 命令 (首次运行时执行):
*   ssc install reghdfe, replace
*   ssc install ftools, replace
*   ssc install estout, replace

* ----------------------------------------------------------------------------
* Phase 4a 路径前奏 — papers_assets/<paper>/do/ 自包含调用契约
* 默认假设当前工作目录是本 .do 文件所在目录:
*     news_process/papers_assets/benefit_society/do/
* 用户可通过 `global panel_dta "..."` / `global out_dir "..."` 显式覆盖。
* ----------------------------------------------------------------------------
if "$panel_dta" == "" {
    global panel_dta "../../../data_processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
    capture mkdir "$out_dir"
}

* --- 数据加载 ---
* 文件名与 pipeline.panel.runner 的导出逻辑一致:
*   panel_path = '40_panel_yearly.parquet' -> dta_path = '40_panel_yearly.dta'
use "$panel_dta", clear

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
* 层 4: 经营效益情感态度投影 (Jha, Liu & Manela 2026, RFS)
* ============================================================================
* 【术语】双极连续余弦投影 (Bipolar Anchor Projection)
*   核心公式 (§1.3.2 Eq. 1):
*     a_j = cos(s_j, p),  p = mean(pos_emb) - mean(neg_emb)
*   值域 ∈ [-1, 1]: >0 = 利好经营, <0 = 损害经营, =0 = 中性
*
*   Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society?
*     A language embedding approach. Review of Financial Studies, 39(5),
*     1227–1266. https://doi.org/10.1093/rfs/hhaf012
*
*   方法论上游:
*   Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of
*     culture: Analyzing the meanings of class through word embeddings.
*     American Sociological Review, 84(5), 905–949.
*     https://doi.org/10.1177/0003122419877135
*
* 【白话】给每篇金融科技新闻打一个"经营效益态度分":
*   正分 = 新闻把金融科技描述成利好银行经营
*   负分 = 新闻把金融科技描述成损害银行经营
*   然后取每家银行每年的均值/比例作为回归变量

* m9: 主回归 — 态度均值 → 银行绩效
* 【白话】经营效益态度越正面的银行，ROA 是否更高？
reghdfe ROA benefit_mean_full $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m9_benefit

* m10: 交互项 — 态度 × 技术强度
* 【白话】如果一家银行既报道"态度正面"又"技术投入重"，效果是否叠加？
gen benefit_x_intensity = benefit_mean_full * fintech_intensity_mean
reghdfe ROA benefit_mean_full fintech_intensity_mean benefit_x_intensity ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m10_benefit_interact

* m11: 稳健性 A — Ctx 轨 (仅使用提及该银行的段落)
* 【白话】只看"提到这家银行"的段落，排除其他银行的情感干扰
reghdfe ROA benefit_mean_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m11_benefit_ctx

* m12: 稳健性 B — 正/负态度比例分解
* 【白话】不看平均分，而是看"正面新闻占多少" vs "负面新闻占多少"
reghdfe ROA benefit_pos_frac_full benefit_neg_frac_full ///
    $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m12_benefit_frac

* ============================================================================
* 输出回归表
* ============================================================================
esttab m1_sim m2_interact m3_token_car m4_hidden_roa m5_subst_roa ///
    m6_p25 m7_p75 m8_int_track ///
    m9_benefit m10_benefit_interact m11_benefit_ctx m12_benefit_frac ///
    using "token_hidden_results.tex", replace ///
    star(* 0.10 ** 0.05 *** 0.01) ///
    se(3) b(3) ///
    title("Fintech Adoption, Benefit-Operations Attitude, and Bank Performance") ///
    label compress

