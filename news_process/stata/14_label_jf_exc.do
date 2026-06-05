/*==============================================================================
  文件: 14_label_jf_exc.do
  目的: 为JF系数和排除性指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 42. JF系数 (Jaffe-Feldman Coefficient)
* ============================================================================

label variable jf_coefficient_full "JF系数(全文)"
label variable jf_coefficient_ctx "JF系数(上下文)"

* ============================================================================
* 43. 排除性指标 (Exclusivity Indicators)
* ============================================================================

* 43.1 排除性新闻数量和情感
label variable n_articles_exc "排除性新闻数量"
label variable exc_tone_full "排除性情感(全文)"
label variable exc_tone_ctx "排除性情感(上下文)"

* 43.2 排除性词典情感
label variable exc_jiang_2021_score_full "排除性江2021得分(全文)"
label variable exc_jiang_2021_score_ctx "排除性江2021得分(上下文)"

label variable exc_yao_2021_score_full "排除性姚2021得分(全文)"
label variable exc_yao_2021_score_ctx "排除性姚2021得分(上下文)"

label variable exc_bian_2021_score_full "排除性卞2021得分(全文)"
label variable exc_bian_2021_score_ctx "排除性卞2021得分(上下文)"

label variable exc_du_2022_score_full "排除性杜2022得分(全文)"
label variable exc_du_2022_score_ctx "排除性杜2022得分(上下文)"

label variable exc_you_2018_score_full "排除性尤2018得分(全文)"
label variable exc_you_2018_score_ctx "排除性尤2018得分(上下文)"

* 43.3 排除性LLM情感
label variable exc_gpt54nano_score_full "排除性GPT5nano得分(全文)"
label variable exc_gemini311_score_full "排除性Gemini3得分(全文)"
label variable exc_deepseekv4_score_full "排除性Grok4.1得分(全文)"

label variable exc_gpt54nano_score_ctx "排除性GPT5nano得分(上下文)"
label variable exc_gemini311_score_ctx "排除性Gemini3得分(上下文)"
label variable exc_deepseekv4_score_ctx "排除性Grok4.1得分(上下文)"


* 43.4 排除性跟风衰减加权
label variable exc_gpt54nano_score_hw_full "排除性GPT5nano得分HW(全文)"
label variable exc_gemini311_score_hw_full "排除性Gemini3得分HW(全文)"
label variable exc_deepseekv4_score_hw_full "排除性Grok4.1得分HW(全文)"
label variable exc_jiang_2021_score_hw_full "排除性江2021得分HW(全文)"
label variable exc_yao_2021_score_hw_full "排除性姚2021得分HW(全文)"
label variable exc_bian_2021_score_hw_full "排除性卞2021得分HW(全文)"
label variable exc_du_2022_score_hw_full "排除性杜2022得分HW(全文)"
label variable exc_you_2018_score_hw_full "排除性尤2018得分HW(全文)"

label variable exc_gpt54nano_score_hw_ctx "排除性GPT5nano得分HW(上下文)"
label variable exc_gemini311_score_hw_ctx "排除性Gemini3得分HW(上下文)"
label variable exc_deepseekv4_score_hw_ctx "排除性Grok4.1得分HW(上下文)"
label variable exc_jiang_2021_score_hw_ctx "排除性江2021得分HW(上下文)"
label variable exc_yao_2021_score_hw_ctx "排除性姚2021得分HW(上下文)"
label variable exc_bian_2021_score_hw_ctx "排除性卞2021得分HW(上下文)"
label variable exc_du_2022_score_hw_ctx "排除性杜2022得分HW(上下文)"
label variable exc_you_2018_score_hw_ctx "排除性尤2018得分HW(上下文)"


