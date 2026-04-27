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
*   --- N-最近邻 Full 轨 ---
*   strat_diff_n{3..7}    TF-IDF char N-最近邻差异度, 值域 [0,1]
*   strat_diff_n{3..7}_w  TF-IDF jieba 词级差异度, 值域 [0,1]
*   strat_sim_max{_w}     最大同行相似度
*   strat_fluidity{_w}    市场流动性 (Hoberg et al. 2014)
*   strat_diff_n5_lda     LDA+JSD N=5 差异度
*   strat_diff_n5_emb     Embedding N=5 差异度
*   --- N-最近邻 Ctx 轨 (N=5 only) ---
*   strat_diff_n5_ctx     TF-IDF char Ctx 轨 N=5 差异度
*   strat_diff_n5_w_ctx   TF-IDF jieba Ctx 轨 N=5 差异度
*   strat_sim_max_ctx     Ctx 轨最大同行相似度
*   --- 全行业向量法 (谢佳松 2025) ---
*   centroid_diff_tfidf_c{_ctx}  TF-IDF char Full/Ctx centroid 距离
*   centroid_diff_tfidf_w{_ctx}  TF-IDF jieba Full/Ctx centroid 距离
*   centroid_diff_lda{_ctx}      LDA Full/Ctx centroid 距离
*   centroid_diff_emb{_ctx}      Embedding Full/Ctx centroid 距离
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

* =========================================================================
* 8. 全行业向量法: Centroid Distance (谢佳松 2025, 经济研究, 图1/表2)
*    centroid_diff_i = 1 - CosineSim(vec_i, industry_centroid)
*    学术依据:
*      谢佳松, 樊嘉诚, & 林建浩. (2025). 信息摩擦、公共数据与
*        企业创新边界. 经济研究, (11).
*      图 1: BERTopic 余弦相似度 → 技术布局引导
*      (本项目迁移至 TF-IDF/LDA/Embedding, 行业质心替代公共数据基准)
* =========================================================================

* ── 8a. 描述性统计 ──
sum centroid_diff_tfidf_c centroid_diff_tfidf_w ///
    centroid_diff_lda centroid_diff_emb, detail

* ── 8b. 与 N-最近邻法相关性 (收敛效度) ──
*    期望: 正相关但 r < 1 (度量不同经济概念)
pwcorr strat_diff_n5 centroid_diff_tfidf_c centroid_diff_emb, ///
    sig star(0.05)

* ── 8c. Centroid 基准回归 (双向 FE + 银行聚类) ──
reghdfe Y centroid_diff_tfidf_c $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo cd1

* ── 8d. 多方法稳健性 ──
foreach method in tfidf_c tfidf_w lda emb {
    reghdfe Y centroid_diff_`method' $controls, ///
        absorb(bank_id year) vce(cluster bank_id)
    eststo cd_`method'
}
esttab cd_tfidf_c cd_tfidf_w cd_lda cd_emb ///
    using "output/centroid_robustness.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("TF-IDF char" "TF-IDF jieba" "LDA" "Embedding")

* =========================================================================
* 9. 双轨对比: Full vs Ctx
*    若 Ctx 轨系数更大 → 核心上下文比全文噪声更具信息量
* =========================================================================

* ── 9a. N-最近邻 Full vs Ctx ──
reghdfe Y strat_diff_n5 $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo nn_full

reghdfe Y strat_diff_n5_ctx $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo nn_ctx

esttab nn_full nn_ctx using "output/nn_full_vs_ctx.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("N-NN (Full)" "N-NN (Ctx)")

* ── 9b. Centroid Full vs Ctx ──
reghdfe Y centroid_diff_tfidf_c $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo cd_full

reghdfe Y centroid_diff_tfidf_c_ctx $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo cd_ctx

esttab cd_full cd_ctx using "output/centroid_full_vs_ctx.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("Centroid (Full)" "Centroid (Ctx)")

* ── 9c. N-NN vs Centroid Horse Race ──
*    检验两种距离度量是否包含独立信息
reghdfe Y strat_diff_n5 centroid_diff_tfidf_c $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo horse_race

* =========================================================================
* 10. 权威政策战略响应度 (Stage 26: Authoritative Policy Alignment)
*     【学术方法论】
*     - 先将银行新闻按年聚合(Pool-then-Vectorize), 与政策基准(如《关于促进
*       互联网金融健康发展的指导意见》等)一同映射入当年的 TF-IDF / LDA / 
*       Embedding 特征空间, 作为 "Ghost Anchor" (虚拟锚点)。随后提取最后一行
*       切片，计算高维空间中的余弦相似度。
*     【白话解释】
*     - 简单来说，就是把国家政策当成“满分标准答案”，看看各大银行当年的新闻
*       和这个标答有多像。越像，说明银行越听话、越紧跟国家战略步伐。
*     【参考文献】
*     - Hassan, T. A., et al. (2019). Firm-level political risk: Measurement 
*       and effects. QJE. https://doi.org/10.1093/qje/qjz021
*     - Hoberg, G., & Phillips, G. (2016). Text-based network industries and 
*       endogenous product differentiation. JPE. https://doi.org/10.1086/688176
* =========================================================================

* ── 10a. 描述性统计与方法论收敛效度 (Convergent Validity) ──
sum auth_sim_*_full, detail
pwcorr auth_sim_tfidf_c_full auth_sim_tfidf_w_full ///
       auth_sim_lda_full auth_sim_emb_full, sig star(0.05)

* ── 10b. 四维度并行基准回归 ──
* 这里仍使用示例 Y
foreach m in tfidf_c tfidf_w lda emb {
    reghdfe Y auth_sim_`m'_full $controls, ///
        absorb(bank_id year) vce(cluster bank_id)
    eststo auth_`m'_f
}

esttab auth_tfidf_c_f auth_tfidf_w_f auth_lda_f auth_emb_f ///
    using "output/auth_sim_full_robustness.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    b(%9.3f) t(%9.2f) compress label ///
    mtitles("TF-IDF(c)" "TF-IDF(w)" "LDA" "Emb") ///
    title("Table: Multidimensional Robustness of Authoritative Policy Alignment")

* ── 10c. 权威政策响应度 (Centroid) 与 N-最近邻 (N-NN) 的 Horse Race ──
reghdfe Y auth_sim_tfidf_c_full strat_diff_n5 $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo auth_horse_race
