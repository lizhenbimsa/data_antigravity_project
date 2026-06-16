/*==============================================================================
  文件: 01_label_variables.do
  目的: 为所有文本生成的指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

/*------------------------------------------------------------------------------
  ⚠ 轨道覆盖披露 (S11-04 / D12-ss-labels, 2026-06-16)

  本手工维护标签集 (stata/01_..15_label_*.do, 供 scripts/convert_parquet_to_stata.py
  路径使用) 仅覆盖 **_full / _ctx 两轨**。v3.9.0 新增的第三主轨 `_ss`
  (银行+金科同句共现, Bank+FinTech same-sentence) 的变量标签 **不在此手工维护**。

  原因: 为 _ss 手写数十行并行标签块极易腐烂 (与 _full/_ctx 不同步)。

  _ss 标签的权威来源 = stage 46 自动生成的 `46_panel_yearly_labels.do`
  (由 news_process.pipeline.panel.stata_export.write_labels_do_file 产出,
   build_variable_labels 直接遍历实际面板列 → 已对 full/ctx/ss 三轨**全覆盖且命名正确**)。

  使用约定: 走 convert_parquet_to_stata.py + 本手工标签集时, _ss 列标签请从
  stage-46 输出的 46_panel_yearly_labels.do 取用 (勿在此手写 _ss 标签行)。
------------------------------------------------------------------------------*/

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

label variable gemini31111_tone_full "Gemini3情感得分(全文)"
label variable gemini31111_tone_sum_full "Gemini3情感总和(全文)"
label variable gemini31111_cont_mean_full "Gemini3连续情感均值(全文)"
label variable gemini31111_cont_sum_full "Gemini3连续情感总和(全文)"
label variable gemini31111_tone_std_full "Gemini3情感标准差(全文)"

label variable deepseekv4_tone_full "DeepSeek-V4情感得分(全文)"
label variable deepseekv4_tone_sum_full "DeepSeek-V4情感总和(全文)"
label variable deepseekv4_cont_mean_full "DeepSeek-V4连续情感均值(全文)"
label variable deepseekv4_cont_sum_full "DeepSeek-V4连续情感总和(全文)"
label variable deepseekv4_tone_std_full "DeepSeek-V4情感标准差(全文)"

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

* 2.3 标题轨道已停产 (remove-title-track, v3.8.0 BREAKING)

