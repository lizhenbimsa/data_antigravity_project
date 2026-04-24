* =========================================================================
* strategic_differentiation.do — 金融科技战略差异度回归分析
* =========================================================================
*
* 学术依据:
*   Guzman, J., & Li, A. (2023). Measuring founding strategy.
*     Management Science, 69(1), 101–118.
*     https://doi.org/10.1287/mnsc.2022.4369
*   Hoberg, G., & Phillips, G. (2016). Text-based network industries
*     and endogenous product differentiation.
*     Journal of Political Economy, 124(5), 1423–1465.
*     https://doi.org/10.1086/688176
*   Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market
*     threats, payouts, and financial flexibility.
*     The Journal of Finance, 69(1), 293–324.
*     https://doi.org/10.1111/jofi.12050
*
* 前置依赖 (仅首次安装):
*   ssc install reghdfe, replace
*   ssc install ftools, replace
*   ssc install estout, replace
*   ssc install ivreghdfe, replace
*
* 变量说明:
*   strat_diff_n{3..7}    TF-IDF char N-最近邻差异度, 值域 [0,1]
*   strat_diff_n{3..7}_w  TF-IDF jieba 词级差异度, 值域 [0,1]
*   strat_sim_max{_w}     最大同行相似度
*   strat_fluidity{_w}    市场流动性 (Hoberg et al. 2014)
*   strat_diff_n5_lda     LDA+JSD N=5 差异度
*   strat_diff_n5_emb     Embedding N=5 差异度
* =========================================================================

clear all
set more off
use "output/40_panel_data.dta", clear

* ── 面板设定 ──
encode target_bank, gen(bank_id)
xtset bank_id year

* 用户自定义控制变量 (根据研究需要设定)
* global controls "ln_news_coverage media_hhi bank_scale_ord"

* =========================================================================
* 1. 描述性统计
* =========================================================================
sum strat_diff_n* strat_sim_max* strat_fluidity*, detail

* =========================================================================
* 2. 四方法相关矩阵 — 收敛效度检验
*    期望: 正相关且显著 → 多方法一致性良好
* =========================================================================
pwcorr strat_diff_n5 strat_diff_n5_w strat_diff_n5_lda strat_diff_n5_emb, ///
    sig star(0.05)

* =========================================================================
* 3. 基准回归 (双向固定效应 + 银行聚类标准误)
*    被解释变量 Y 需用户自行替换为实际变量
*    (Hoberg & Phillips 2016, Table 3)
* =========================================================================
reghdfe Y strat_diff_n5 $controls, absorb(bank_id year) vce(cluster bank_id)
eststo m1

* 加入市场流动性控制 (Hoberg et al. 2014)
reghdfe Y strat_diff_n5 strat_fluidity $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo m2

* 加入最大同行相似度控制
reghdfe Y strat_diff_n5 strat_sim_max strat_fluidity $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo m3

* =========================================================================
* 4. N 值敏感性 (Bresnahan & Reiss 1991, JPE)
*    验证结果对近邻数 N 的选取不敏感
* =========================================================================
foreach n of numlist 3/7 {
    reghdfe Y strat_diff_n`n' $controls, ///
        absorb(bank_id year) vce(cluster bank_id)
    eststo n`n'
}
esttab n3 n4 n5 n6 n7 using "output/strat_n_sensitivity.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("N=3" "N=4" "N=5" "N=6" "N=7")

* =========================================================================
* 5. 稳健性: 替换文本表征方法
*    A = TF-IDF jieba 词级  B = LDA+JSD  C = Embedding
* =========================================================================
reghdfe Y strat_diff_n5_w $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo ra

reghdfe Y strat_diff_n5_lda $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo rb

reghdfe Y strat_diff_n5_emb $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo rc

esttab m1 ra rb rc using "output/strat_robustness.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("TF-IDF char" "TF-IDF jieba" "LDA+JSD" "Embedding")

* =========================================================================
* 6. 异质性: 产权性质交互
*    Angrist, J. D., & Pischke, J.-S. (2009). Mostly Harmless
*    Econometrics. Princeton University Press.
*    Brambor, T., Clark, W. R., & Golder, M. (2006). Understanding
*    interaction models. Political Analysis, 14(1), 63–82.
*    https://doi.org/10.1093/pan/mpi014
* =========================================================================
gen strat_x_soe = strat_diff_n5 * is_soe
reghdfe Y strat_diff_n5 strat_x_soe is_soe $controls, ///
    absorb(bank_id year) vce(cluster bank_id)

* =========================================================================
* 7. 与 Bartik IV 联合回归
*    Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik
*    instruments: What, when, why, and how. American Economic Review,
*    110(8), 2586–2624. https://doi.org/10.1257/aer.20181047
* =========================================================================
ivreghdfe Y (llm_vote_tone_full = bartik_type_iv_full) ///
    strat_diff_n5 strat_fluidity $controls, ///
    absorb(bank_id year) cluster(bank_id)
