/*==============================================================================
  文件: 10_label_benefit_token.do
  目的: 为社会效益和代币采纳指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 28. 社会效益指标 (papers/benefit_society)
* ============================================================================

* 28.1 全文轨道
label variable benefit_mean_full "社会效益均值(全文)"
label variable benefit_std_full "社会效益标准差(全文)"
label variable benefit_pos_frac_full "社会效益正面占比(全文)"
label variable benefit_neg_frac_full "社会效益负面占比(全文)"

* 28.2 上下文轨道
label variable benefit_mean_ctx "社会效益均值(上下文)"
label variable benefit_std_ctx "社会效益标准差(上下文)"
label variable benefit_pos_frac_ctx "社会效益正面占比(上下文)"
label variable benefit_neg_frac_ctx "社会效益负面占比(上下文)"

* ============================================================================
* 29. 文章相似度指标
* ============================================================================

label variable article_sim_mean "文章相似度均值"
label variable article_sim_std "文章相似度标准差"

* ============================================================================
* 30. 代币采纳指标 (papers/benefit_society - 隐藏采纳)
* ============================================================================

* 30.1 基于关键词的代币采纳 (分位数)
label variable token_adopt_kw_p25 "代币采纳P25(关键词)"
label variable hidden_adopt_kw_p25 "隐藏采纳P25(关键词)"
label variable subst_adopt_kw_p25 "替代采纳P25(关键词)"

label variable token_adopt_kw_p50 "代币采纳P50(关键词)"
label variable hidden_adopt_kw_p50 "隐藏采纳P50(关键词)"
label variable subst_adopt_kw_p50 "替代采纳P50(关键词)"

label variable token_adopt_kw_p75 "代币采纳P75(关键词)"
label variable hidden_adopt_kw_p75 "隐藏采纳P75(关键词)"
label variable subst_adopt_kw_p75 "替代采纳P75(关键词)"

* 30.2 基于强度的代币采纳 (分位数)
label variable token_adopt_int_p25 "代币采纳P25(强度)"
label variable hidden_adopt_int_p25 "隐藏采纳P25(强度)"
label variable subst_adopt_int_p25 "替代采纳P25(强度)"

label variable token_adopt_int_p50 "代币采纳P50(强度)"
label variable hidden_adopt_int_p50 "隐藏采纳P50(强度)"
label variable subst_adopt_int_p50 "替代采纳P50(强度)"

label variable token_adopt_int_p75 "代币采纳P75(强度)"
label variable hidden_adopt_int_p75 "隐藏采纳P75(强度)"
label variable subst_adopt_int_p75 "替代采纳P75(强度)"

