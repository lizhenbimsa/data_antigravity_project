/*==============================================================================
  文件: 12_label_cater_misc.do
  目的: 为迎合指标和其他衍生指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 33. 对数情感指标 (Log Sentiment)
* ============================================================================

label variable log_sent_full "对数情感(全文)"
label variable log_sent_ctx "对数情感(上下文)"

* ============================================================================
* 34. 算法迎合指标 (Algorithmic Catering)
* ============================================================================

* 34.1 全文轨道迎合指标
label variable algo_cater_full "算法迎合指数(全文)"
label variable algo_cater_b_full "算法迎合指数B(全文)"

label variable jiang_2021_cater_full "江2021迎合指数(全文)"
label variable jiang_2021_cater_b_full "江2021迎合指数B(全文)"
label variable yao_2021_cater_full "姚2021迎合指数(全文)"
label variable yao_2021_cater_b_full "姚2021迎合指数B(全文)"
label variable bian_2021_cater_full "卞2021迎合指数(全文)"
label variable bian_2021_cater_b_full "卞2021迎合指数B(全文)"
label variable du_2022_cater_full "杜2022迎合指数(全文)"
label variable du_2022_cater_b_full "杜2022迎合指数B(全文)"
label variable you_2018_cater_full "尤2018迎合指数(全文)"
label variable you_2018_cater_b_full "尤2018迎合指数B(全文)"

label variable cater_gpt54nano_full "GPT5nano迎合指数(全文)"
label variable cater_gemini311_full "Gemini3迎合指数(全文)"
label variable cater_deepseekv4_full "Grok4.1迎合指数(全文)"
label variable cater_finbert_cn_full "FinBERT-CN迎合指数(全文)"
label variable cater_fin_sent_zh_full "FinSent-ZH迎合指数(全文)"
label variable cater_erlangshen_full "Erlangshen迎合指数(全文)"
label variable cater_hw2942_full "HW2942迎合指数(全文)"

* 34.2 上下文轨道迎合指标
label variable algo_cater_ctx "算法迎合指数(上下文)"
label variable algo_cater_b_ctx "算法迎合指数B(上下文)"

label variable jiang_2021_cater_ctx "江2021迎合指数(上下文)"
label variable jiang_2021_cater_b_ctx "江2021迎合指数B(上下文)"
label variable yao_2021_cater_ctx "姚2021迎合指数(上下文)"
label variable yao_2021_cater_b_ctx "姚2021迎合指数B(上下文)"
label variable bian_2021_cater_ctx "卞2021迎合指数(上下文)"
label variable bian_2021_cater_b_ctx "卞2021迎合指数B(上下文)"
label variable du_2022_cater_ctx "杜2022迎合指数(上下文)"
label variable du_2022_cater_b_ctx "杜2022迎合指数B(上下文)"
label variable you_2018_cater_ctx "尤2018迎合指数(上下文)"
label variable you_2018_cater_b_ctx "尤2018迎合指数B(上下文)"

label variable cater_gpt54nano_ctx "GPT5nano迎合指数(上下文)"
label variable cater_gemini311_ctx "Gemini3迎合指数(上下文)"
label variable cater_deepseekv4_ctx "Grok4.1迎合指数(上下文)"
label variable cater_finbert_cn_ctx "FinBERT-CN迎合指数(上下文)"
label variable cater_fin_sent_zh_ctx "FinSent-ZH迎合指数(上下文)"
label variable cater_erlangshen_ctx "Erlangshen迎合指数(上下文)"
label variable cater_hw2942_ctx "HW2942迎合指数(上下文)"

* ============================================================================
* 35. 情感反转指标 (Tone Reversal)
* ============================================================================

label variable llm_vote_tone_full_lag1 "LLM投票情感滞后1期(全文)"
label variable tone_reversal_full "情感反转(全文)"
label variable llm_vote_tone_ctx_lag1 "LLM投票情感滞后1期(上下文)"
label variable tone_reversal_ctx "情感反转(上下文)"

* ============================================================================
* 36. 关注度指标 (Concern Score)
* ============================================================================

label variable concern_score_full "关注度得分(全文)"
label variable concern_score_ctx "关注度得分(上下文)"

* ============================================================================
* 37. 其他虚拟变量
* ============================================================================

label variable dummy_no_positive_news "无正面新闻虚拟变量"
label variable low_conf_flag "低置信度标记"

* ============================================================================
* 38. 银行特征变量
* ============================================================================

label variable is_soe "是否国有银行"
label variable bank_scale_ord "银行规模序数"
label variable high_coverage "高覆盖度"

* ============================================================================
* 39. 交互项
* ============================================================================

label variable tone_x_soe_full "情感×国有(全文)"
label variable tone_x_scale_full "情感×规模(全文)"
label variable tone_x_highcov_full "情感×高覆盖(全文)"
label variable tone_x_soe_ctx "情感×国有(上下文)"
label variable tone_x_scale_ctx "情感×规模(上下文)"
label variable tone_x_highcov_ctx "情感×高覆盖(上下文)"

* ============================================================================
* 40. 金融科技暴露指标 (Fintech Exposure)
* ============================================================================

label variable fintech_exposure_full "金融科技暴露(全文)"
label variable fintech_exposure_ctx "金融科技暴露(上下文)"
label variable fintech_exposure_title "金融科技暴露(标题)"

