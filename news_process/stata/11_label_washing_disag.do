/*==============================================================================
  文件: 11_label_washing_disag.do
  目的: 为洗绿指标和分歧度指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 31. 洗绿指标 (Greenwashing / Washing Ratio)
* ============================================================================

* 31.1 全文轨道洗绿指标
label variable washing_ratio "洗绿比率(全文)"
label variable washing_ratio_gpt54nano "洗绿比率GPT5nano(全文)"
label variable washing_ratio_gemini311 "洗绿比率Gemini3(全文)"
label variable washing_ratio_deepseekv4 "洗绿比率Grok4.1(全文)"

label variable neg_sub_ratio_full "负面实质性比率(全文)"
label variable washing_asymmetry_full "洗绿不对称性(全文)"
label variable tone_gap_symb_sub_full "象征性-实质性情感差(全文)"

label variable washing_ratio_dict "洗绿比率词典平均(全文)"
label variable washing_ratio_jiang_2021 "洗绿比率江2021(全文)"
label variable washing_ratio_yao_2021 "洗绿比率姚2021(全文)"
label variable washing_ratio_bian_2021 "洗绿比率卞2021(全文)"
label variable washing_ratio_du_2022 "洗绿比率杜2022(全文)"
label variable washing_ratio_you_2018 "洗绿比率尤2018(全文)"

label variable washing_ratio_bert "洗绿比率BERT平均(全文)"
label variable washing_ratio_finbert_cn "洗绿比率FinBERT-CN(全文)"
label variable washing_ratio_fin_sent_zh "洗绿比率FinSent-ZH(全文)"

label variable washing_ratio_hc "洗绿比率硬编码(全文)"
label variable washing_tone_shift_full "洗绿情感转移(全文)"

* 31.2 上下文轨道洗绿指标
label variable washing_ratio_ctx "洗绿比率(上下文)"
label variable washing_ratio_gpt54nano_ctx "洗绿比率GPT5nano(上下文)"
label variable washing_ratio_gemini311_ctx "洗绿比率Gemini3(上下文)"
label variable washing_ratio_deepseekv4_ctx "洗绿比率Grok4.1(上下文)"

label variable neg_sub_ratio_ctx "负面实质性比率(上下文)"
label variable washing_asymmetry_ctx "洗绿不对称性(上下文)"
label variable tone_gap_symb_sub_ctx "象征性-实质性情感差(上下文)"

label variable washing_ratio_dict_ctx "洗绿比率词典平均(上下文)"
label variable washing_ratio_jiang_2021_ctx "洗绿比率江2021(上下文)"
label variable washing_ratio_yao_2021_ctx "洗绿比率姚2021(上下文)"
label variable washing_ratio_bian_2021_ctx "洗绿比率卞2021(上下文)"
label variable washing_ratio_du_2022_ctx "洗绿比率杜2022(上下文)"
label variable washing_ratio_you_2018_ctx "洗绿比率尤2018(上下文)"

label variable washing_ratio_bert_ctx "洗绿比率BERT平均(上下文)"
label variable washing_ratio_finbert_cn_ctx "洗绿比率FinBERT-CN(上下文)"
label variable washing_ratio_fin_sent_zh_ctx "洗绿比率FinSent-ZH(上下文)"

label variable washing_ratio_hc_ctx "洗绿比率硬编码(上下文)"
label variable washing_tone_shift_ctx "洗绿情感转移(上下文)"

* ============================================================================
* 32. 分歧度指标 (Disagreement)
* ============================================================================

* 32.1 全文轨道分歧度
label variable disag_full "总体分歧度(全文)"

* 词典分歧度
label variable disag_jiang_2021_full "江2021词典分歧度(全文)"
label variable disag_yao_2021_full "姚2021词典分歧度(全文)"
label variable disag_bian_2021_full "卞2021词典分歧度(全文)"
label variable disag_du_2022_full "杜2022词典分歧度(全文)"
label variable disag_you_2018_full "尤2018词典分歧度(全文)"

* LLM分歧度
label variable disag_llm_full "LLM总体分歧度(全文)"
label variable disag_gpt54nano_full "GPT5nano分歧度(全文)"
label variable disag_gemini311_full "Gemini3分歧度(全文)"
label variable disag_deepseekv4_full "Grok4.1分歧度(全文)"

* BERT分歧度
label variable disag_bert_full "BERT总体分歧度(全文)"
label variable disag_finbert_cn_full "FinBERT-CN分歧度(全文)"
label variable disag_fin_sent_zh_full "FinSent-ZH分歧度(全文)"
label variable disag_finbert2_full "FinBERT2分歧度(全文)"

* 32.2 上下文轨道分歧度
label variable disag_ctx "总体分歧度(上下文)"
label variable disag_jiang_2021_ctx "江2021词典分歧度(上下文)"
label variable disag_yao_2021_ctx "姚2021词典分歧度(上下文)"
label variable disag_bian_2021_ctx "卞2021词典分歧度(上下文)"
label variable disag_du_2022_ctx "杜2022词典分歧度(上下文)"
label variable disag_you_2018_ctx "尤2018词典分歧度(上下文)"

label variable disag_llm_ctx "LLM总体分歧度(上下文)"
label variable disag_gpt54nano_ctx "GPT5nano分歧度(上下文)"
label variable disag_gemini311_ctx "Gemini3分歧度(上下文)"
label variable disag_deepseekv4_ctx "Grok4.1分歧度(上下文)"

label variable disag_bert_ctx "BERT总体分歧度(上下文)"
label variable disag_finbert_cn_ctx "FinBERT-CN分歧度(上下文)"
label variable disag_fin_sent_zh_ctx "FinSent-ZH分歧度(上下文)"
label variable disag_finbert2_ctx "FinBERT2分歧度(上下文)"

