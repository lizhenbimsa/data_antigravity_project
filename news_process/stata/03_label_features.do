/*==============================================================================
  文件: 03_label_features.do
  目的: 为文本特征和衍生指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 5. 文本特征指标
* ============================================================================

* 5.1 基础文本特征
label variable avg_sent_len_full "平均句子长度(全文)"
label variable avg_ttr_full "平均词汇丰富度TTR(全文)"
label variable avg_cpw_full "平均每词字符数(全文)"
label variable avg_pos_ratio_full "平均正面词占比(全文)"
label variable avg_neg_ratio_full "平均负面词占比(全文)"
label variable avg_pos_ratio_std_full "正面词占比标准差(全文)"
label variable avg_neg_ratio_std_full "负面词占比标准差(全文)"

* 5.2 情感强度指标
label variable avg_msent_full "平均情感强度(全文)"
label variable avg_msent_std_full "情感强度标准差(全文)"
label variable msent_sum_full "情感强度总和(全文)"

* 5.3 LLM置信度指标
label variable avg_llm_conf_full "LLM平均置信度(全文)"
label variable avg_llm_conf_std_full "LLM置信度标准差(全文)"
label variable avg_gpt54nano_conf_full "GPT5nano平均置信度(全文)"
label variable avg_gemini311_conf_full "Gemini3平均置信度(全文)"
label variable avg_deepseekv4_conf_full "Grok4.1平均置信度(全文)"

* 5.4 LLM一致性指标
label variable avg_agreement_rate_full "LLM平均一致率(全文)"
label variable avg_agreement_rate_ctx "LLM平均一致率(上下文)"
label variable avg_agreement_rate_title "LLM平均一致率(标题)"

* ============================================================================
* 6. 金融科技强度指标 (阶段14: 金融科技技术重度评分)
* ============================================================================

label variable avg_ft_word_ratio "平均金融科技词汇占比"
label variable avg_ft_word_ratio_std "金融科技词汇占比标准差"
label variable avg_ft_intensity "平均金融科技强度(TF-IDF)"
label variable avg_ft_intensity_std "金融科技强度标准差"
label variable fintech_intensity_mean "金融科技强度均值"

* ============================================================================
* 7. 新闻覆盖度指标
* ============================================================================

label variable n_articles "新闻报道数量"
label variable ln_news_coverage "新闻覆盖度(对数)"
label variable headline_frac "头条新闻占比"
label variable multi_bank_frac "多银行新闻占比"
label variable avg_bank_count "平均提及银行数"
label variable max_bank_count "最大提及银行数"
label variable avg_doc_length "平均文档长度"
label variable avg_article_length "平均文章长度"
label variable sum_doc_length "文档长度总和"
label variable sum_target_mentions "目标银行提及次数总和"

* ============================================================================
* 8. 提及密度加权指标 (Value-weighted Exposure, Hassan 2019 QJE)
* ============================================================================

label variable sum_mention_density "提及密度总和"
label variable llm_vote_score_w_sum_full "LLM投票得分VW总和(全文)"
label variable llm_vote_cont_w_sum_full "LLM投票连续VW总和(全文)"
label variable pos_count_vw_full "正面新闻VW数量(全文)"
label variable neg_count_vw_full "负面新闻VW数量(全文)"

label variable llm_vote_tone_vw_full "LLM投票情感VW(全文)"
label variable llm_vote_cont_vw_full "LLM投票连续VW(全文)"
label variable llm_vote_tone_vw_prob_full "LLM投票概率VW(全文)"

