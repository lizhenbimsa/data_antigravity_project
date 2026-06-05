/*==============================================================================
  文件: 13_label_standardized.do
  目的: 为标准化指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 41. 标准化指标 (Z-scores)
* ============================================================================

* 41.1 LLM情感标准化
label variable llm_vote_tone_full_z "LLM投票情感标准化(全文)"
label variable llm_vote_tone_ctx_z "LLM投票情感标准化(上下文)"
label variable llm_vote_cont_full_z "LLM投票连续标准化(全文)"
label variable llm_vote_cont_ctx_z "LLM投票连续标准化(上下文)"

* 41.2 LLM模型平均标准化
label variable llm_models_avg_tone_full_z "LLM模型平均情感标准化(全文)"
label variable llm_models_avg_tone_ctx_z "LLM模型平均情感标准化(上下文)"
label variable llm_models_avg_cont_full_z "LLM模型平均连续标准化(全文)"
label variable llm_models_avg_cont_ctx_z "LLM模型平均连续标准化(上下文)"

* 41.3 词典情感标准化
label variable dict_avg_tone_full_z "词典平均情感标准化(全文)"
label variable dict_avg_tone_ctx_z "词典平均情感标准化(上下文)"
label variable dict_avg_idf_tone_full_z "词典平均IDF情感标准化(全文)"
label variable dict_avg_idf_tone_ctx_z "词典平均IDF情感标准化(上下文)"

* 41.4 BERT情感标准化
label variable bert_avg_pos_full_z "BERT平均正面标准化(全文)"
label variable bert_avg_pos_ctx_z "BERT平均正面标准化(上下文)"
label variable bert_avg_neg_full_z "BERT平均负面标准化(全文)"
label variable bert_avg_neg_ctx_z "BERT平均负面标准化(上下文)"

* 41.5 加权情感标准化
label variable llm_vote_tone_vw_full_z "LLM投票情感VW标准化(全文)"
label variable llm_vote_tone_vw_ctx_z "LLM投票情感VW标准化(上下文)"

label variable llm_vote_tone_mw_full_z "LLM投票情感MW标准化(全文)"
label variable llm_vote_tone_mw_ctx_z "LLM投票情感MW标准化(上下文)"
label variable dict_avg_tone_mw_full_z "词典平均情感MW标准化(全文)"
label variable dict_avg_tone_mw_ctx_z "词典平均情感MW标准化(上下文)"

label variable llm_vote_tone_hw_full_z "LLM投票情感HW标准化(全文)"
label variable llm_vote_tone_hw_ctx_z "LLM投票情感HW标准化(上下文)"
label variable dict_avg_tone_hw_full_z "词典平均情感HW标准化(全文)"
label variable dict_avg_tone_hw_ctx_z "词典平均情感HW标准化(上下文)"

* 41.6 其他指标标准化
label variable avg_msent_full_z "平均情感强度标准化(全文)"
label variable avg_msent_ctx_z "平均情感强度标准化(上下文)"

label variable fintech_exposure_full_z "金融科技暴露标准化(全文)"
label variable fintech_exposure_ctx_z "金融科技暴露标准化(上下文)"

label variable avg_llm_conf_full_z "LLM平均置信度标准化(全文)"
label variable avg_llm_conf_ctx_z "LLM平均置信度标准化(上下文)"

label variable ln_news_coverage_z "新闻覆盖度标准化"
label variable media_breadth_z "媒体广度标准化"
label variable avg_article_length_z "平均文章长度标准化"

