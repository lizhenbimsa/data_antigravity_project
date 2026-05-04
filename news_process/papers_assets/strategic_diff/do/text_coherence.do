* =========================================================================
* text_coherence.do — 相邻期文本连贯性回归分析
* =========================================================================
*
* 学术依据:
*   欧阳志刚, 胡雯华. (2024). 央行沟通公告有助于提升政策利率的传导
*     效率吗？数量经济技术经济研究, 41(10), 69–88.
*     https://doi.org/10.13653/j.cnki.jqte.2024.10.004
*     → §三(三)2.(2): 余弦相似度 → 连贯性 → 降低不确定性
*
*   Hoberg, G., & Phillips, G. (2016). Text-based network industries and
*     endogenous product differentiation. Journal of Political Economy,
*     124(5), 1423–1465. https://doi.org/10.1086/688176
*
*   Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market
*     threats, payouts, and financial flexibility. The Journal of Finance,
*     69(1), 293–324. https://doi.org/10.1111/jofi.12050
*
* 前置依赖 (仅首次安装):
*   ssc install reghdfe, replace
*   ssc install ftools, replace
*   ssc install estout, replace
*
* 变量说明:
*   coh_tfidf_c_{full|ctx}  TF-IDF char 相邻期相似度 [0,1], 高=连贯
*   coh_tfidf_w_{full|ctx}  TF-IDF jieba 相邻期相似度 [0,1], 高=连贯
*   coh_lda_{full|ctx}      LDA+JSD 相邻期连贯度 [0,1], 高=连贯
*   coh_emb_{full|ctx}      Embedding 相邻期相似度 [0,1], 高=连贯
* =========================================================================

clear all
set more off

* ----------------------------------------------------------------------------
* Phase 4a 路径前奏 — papers_assets/<paper>/do/ 自包含调用契约
* 默认假设当前工作目录是本 .do 文件所在目录:
*     news_process/papers_assets/strategic_diff/do/
* 用户可通过 `global panel_dta "..."` / `global out_dir "..."` 显式覆盖。
* 历史注: 原 `use "output/40_panel_data.dta"` 路径已纠正为
*         真实落盘文件 `data_processed/40_panel_yearly.dta`。
* ----------------------------------------------------------------------------
if "$panel_dta" == "" {
    global panel_dta "../../../data_processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
    capture mkdir "$out_dir"
}

use "$panel_dta", clear

* ── 面板设定 ──
encode target_bank, gen(bank_id)
xtset bank_id year

* 用户自定义控制变量 (根据研究需要设定)
* global controls "ln_news_coverage media_hhi bank_scale_ord"

* =========================================================================
* 1. 描述性统计
* =========================================================================
summarize coh_tfidf_c_full coh_tfidf_w_full coh_lda_full coh_emb_full, detail

* =========================================================================
* 2. 四方法收敛效度 (期望正相关 > 0.5)
*    如果四种不同方法算出来的"连贯性"高度正相关, 说明结果稳健
* =========================================================================
pwcorr coh_tfidf_c_full coh_tfidf_w_full coh_lda_full coh_emb_full, ///
    sig star(0.05)

* =========================================================================
* 3. 正交性验证 (与情感/差异度低相关 → 独立信息维度)
*    连贯性衡量"稳定性", 情感衡量"内容", 二者应独立
* =========================================================================
pwcorr coh_tfidf_c_full llm_vote_tone_full strat_diff_n5, sig

* =========================================================================
* 4. 基准回归: 连贯性作为解释变量
*    欧阳志刚 (2024): 高连贯 → 低不确定性
* =========================================================================
reghdfe Y coh_tfidf_c_full $controls, absorb(bank_id year) vce(cluster bank_id)
eststo coh1

* =========================================================================
* 5. 机制检验: Tone × Coherence 交互
*    假设: 高连贯 → 情感信号更可信 → 传导效率更高
* =========================================================================
gen tone_x_coh_full = llm_vote_tone_full * coh_tfidf_c_full
reghdfe Y llm_vote_tone_full coh_tfidf_c_full tone_x_coh_full $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
eststo coh2

* =========================================================================
* 6. 稳健性: 四方法 (收敛效度回归验证)
*    分别用四种方法计算的连贯性做回归, 看系数方向和显著性是否一致
* =========================================================================
foreach v in coh_tfidf_c_full coh_tfidf_w_full coh_lda_full coh_emb_full {
    reghdfe Y `v' $controls, absorb(bank_id year) vce(cluster bank_id)
    eststo `v'
}
esttab coh_tfidf_c_full coh_tfidf_w_full coh_lda_full coh_emb_full ///
    using "$out_dir/coh_robustness.tex", ///
    star(* .10 ** .05 *** .01) se replace ///
    mtitles("TF-IDF char" "TF-IDF jieba" "LDA+JSD" "Embedding")

* =========================================================================
* 7. 稳健性: Ctx 轨道 (替换文本范围)
*    Ctx 轨道使用银行提及的上下文窗口, 而非全文
* =========================================================================
reghdfe Y coh_tfidf_c_ctx $controls, absorb(bank_id year) vce(cluster bank_id)
eststo coh_ctx

* =========================================================================
* 8. 异质性: 产权性质交互
*    国有银行 vs 非国有银行的连贯性效应可能不同
* =========================================================================
gen coh_x_soe = coh_tfidf_c_full * is_soe
reghdfe Y coh_tfidf_c_full coh_x_soe is_soe $controls, ///
    absorb(bank_id year) vce(cluster bank_id)
