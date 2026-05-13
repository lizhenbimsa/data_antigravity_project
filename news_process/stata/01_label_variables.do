/*==============================================================================
  文件: 01_label_variables.do
  目的: 为所有文本生成的指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 1. 基础标识变量
* ============================================================================
label variable target_bank "目标银行名称"
label variable year "年份"

* ============================================================================
* 2. LLM情感分析指标 (阶段21: 统一LLM语义精筛与情感分析)
* ============================================================================

* 2.1 全文轨道 (_full)
label variable gpt54nano_tone_full "GPT5nano情感得分(全文)"
label variable gpt54nano_tone_sum_full "GPT5nano情感总和(全文)"
label variable gpt54nano_cont_mean_full "GPT5nano连续情感均值(全文)"
label variable gpt54nano_cont_sum_full "GPT5nano连续情感总和(全文)"
label variable gpt54nano_tone_std_full "GPT5nano情感标准差(全文)"

label variable gemini311_tone_full "Gemini3情感得分(全文)"
label variable gemini311_tone_sum_full "Gemini3情感总和(全文)"
label variable gemini311_cont_mean_full "Gemini3连续情感均值(全文)"
label variable gemini311_cont_sum_full "Gemini3连续情感总和(全文)"
label variable gemini311_tone_std_full "Gemini3情感标准差(全文)"

label variable deepseekv4_tone_full "Grok4.1情感得分(全文)"
label variable deepseekv4_tone_sum_full "Grok4.1情感总和(全文)"
label variable deepseekv4_cont_mean_full "Grok4.1连续情感均值(全文)"
label variable deepseekv4_cont_sum_full "Grok4.1连续情感总和(全文)"
label variable deepseekv4_tone_std_full "Grok4.1情感标准差(全文)"

label variable llm_vote_tone_full "LLM投票情感得分(全文)"
label variable llm_vote_tone_sum_full "LLM投票情感总和(全文)"
label variable llm_vote_tone_std_full "LLM投票情感标准差(全文)"
label variable llm_vote_cont_full "LLM投票连续情感(全文)"
label variable llm_vote_cont_sum_full "LLM投票连续情感总和(全文)"

label variable pos_frac_full "正面新闻占比(全文)"
label variable neg_frac_full "负面新闻占比(全文)"
label variable pos_count_full "正面新闻数量(全文)"
label variable neg_count_full "负面新闻数量(全文)"

* 2.2 上下文轨道 (_ctx)
label variable llm_vote_tone_ctx "LLM投票情感得分(上下文)"
label variable llm_vote_tone_sum_ctx "LLM投票情感总和(上下文)"
label variable llm_vote_cont_ctx "LLM投票连续情感(上下文)"
label variable llm_vote_cont_sum_ctx "LLM投票连续情感总和(上下文)"

* 2.3 标题轨道 (_title)
label variable llm_vote_tone_title "LLM投票情感得分(标题)"
label variable llm_vote_tone_sum_title "LLM投票情感总和(标题)"
label variable llm_vote_cont_title "LLM投票连续情感(标题)"
label variable llm_vote_cont_sum_title "LLM投票连续情感总和(标题)"

