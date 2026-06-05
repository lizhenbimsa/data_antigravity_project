/*==============================================================================
  文件: 05_label_advanced.do
  目的: 为高级文本分析指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 10. 金融科技分类指标 (技术vs应用)
* ============================================================================

label variable n_articles_tech "技术类新闻数量"
label variable n_articles_app "应用类新闻数量"
label variable tech_frac "技术类新闻占比"
label variable app_frac "应用类新闻占比"
label variable avg_category_confidence "分类平均置信度"

label variable llm_vote_tone_tech_full "技术类LLM情感(全文)"
label variable llm_vote_cont_tech_full "技术类LLM连续情感(全文)"
label variable llm_vote_tone_app_full "应用类LLM情感(全文)"
label variable llm_vote_cont_app_full "应用类LLM连续情感(全文)"

* ============================================================================
* 11. 实质性vs象征性新闻 (Substantive vs Symbolic, Westphal & Zajac 1994 ASQ)
* ============================================================================

label variable n_articles_sub "实质性新闻数量"
label variable n_articles_symb "象征性新闻数量"
label variable sub_frac "实质性新闻占比"
label variable symb_frac "象征性新闻占比"

label variable llm_vote_tone_sub_full "实质性新闻LLM情感(全文)"
label variable llm_vote_tone_symb_full "象征性新闻LLM情感(全文)"
label variable tone_gap_sub_symb "实质性-象征性情感差"
label variable tone_gap_tech_app "底层技术-应用场景情感差"

label variable pos_symb_count_full "象征性正面新闻数(全文)"
label variable neg_sub_count_full "实质性负面新闻数(全文)"

* ============================================================================
* 12. 媒体权威性加权指标 (Holzman et al. 2023, TAR)
* ============================================================================

label variable sum_media_authority_weight "媒体权威性权重总和"
label variable llm_vote_tone_mw_full "LLM投票情感MW(全文)"
label variable llm_vote_cont_mw_full "LLM投票连续MW(全文)"
label variable llm_vote_tone_mw_prob_full "LLM投票概率MW(全文)"

* ============================================================================
* 13. 跟风衰减权重指标 (阶段24: 跟风衰减权重)
* ============================================================================

label variable avg_herd_weight "平均跟风衰减权重"
label variable min_herd_weight "最小跟风衰减权重"
label variable sum_herd_weight "跟风衰减权重总和"

label variable llm_vote_tone_hw_full "LLM投票情感HW(全文)"
label variable llm_vote_cont_hw_full "LLM投票连续HW(全文)"
label variable llm_vote_tone_hw_prob_full "LLM投票概率HW(全文)"

* ============================================================================
* 14. 标题-全文情感差异
* ============================================================================


* ============================================================================
* 15. 概率分数指标 (Logit-to-Score)
* ============================================================================

label variable avg_llm_prob_score_full "LLM平均概率分数(全文)"
label variable avg_llm_prob_score_std_full "LLM概率分数标准差(全文)"
label variable llm_prob_score_sum_full "LLM概率分数总和(全文)"
label variable llm_prob_score_w_sum_full "LLM概率分数VW总和(全文)"
label variable llm_prob_score_mw_sum_full "LLM概率分数MW总和(全文)"
label variable llm_prob_score_hw_sum_full "LLM概率分数HW总和(全文)"

