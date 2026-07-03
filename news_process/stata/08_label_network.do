/*==============================================================================
  文件: 08_label_network.do
  目的: 为网络指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 22. 同行网络溢出指标 (阶段46: 网络溢出)
* ============================================================================

* 22.1 滞后同行情感
label variable peer_tone_lag1_full "同行情感滞后1期(全文)"
label variable peer_tone_2nd_lag1_full "二阶同行情感滞后1期(全文)"
label variable peer_tone_lag1_ctx "同行情感滞后1期(上下文)"
label variable peer_tone_2nd_lag1_ctx "二阶同行情感滞后1期(上下文)"
label variable peer_fintech_exposure_lag1 "同行金融科技暴露滞后1期"

* 22.2 银行网络中心度指标
label variable bank_degree_cent "银行度中心度"
label variable bank_strength_cent "银行强度中心度"
label variable bank_eigen_cent "银行特征向量中心度"
label variable bank_katz_cent "银行Katz中心度"
label variable bank_subgraph_cent "银行子图中心度"
label variable bank_cfbetween_cent "银行流介数中心度"
label variable bank_clustering "银行聚类系数"
label variable bank_constraint "银行结构洞约束"
label variable bank_ego_density "银行自我网络密度"
label variable bank_effective_size "银行有效规模"
label variable bank_avg_nbr_deg "银行邻居平均度"
label variable bank_coreness "银行核心度"
label variable bank_between_cent "银行介数中心度"
label variable bank_harmonic_cent "银行调和中心度"
label variable bank_closeness_cent "银行接近中心度"
label variable bank_eccentricity "银行离心率"
label variable bank_ci "银行集体影响力"
label variable bank_is_hub "银行是否为枢纽"

* 22.3 网络整体指标
label variable net_density_yr "网络密度(年度)"
label variable net_avg_cluster_yr "网络平均聚类系数(年度)"
label variable net_avg_path_yr "网络平均路径长度(年度)"
label variable net_degree_gini_yr "网络度基尼系数(年度)"

* 22.4 认知邻近性 (三轨 2026-07-03: ctx 手写; _ss 按 01 号约定留给
*      stage-46 自动生成的 46_panel_yearly_labels.do)
label variable bank_cogn_mean "银行认知邻近性均值"
capture label variable bank_cogn_mean_ctx "银行认知邻近性均值(上下文窗口文本)"

* 22.5 网络构造判据敏感性 (2026-07-03): 33 指标 × {_win1,_sent} 共 66 个
*      判据变体 (银行∧银行 ±1句窗/严格同句边; 判据后缀≠三轨文本后缀) 的标签
*      由 stage-46 自动生成文件 (46_panel_yearly_labels.do) 机械覆盖
*      (bank-bank 限定措辞), 本手写源刻意不逐条手抄 (镜像 _ss 约定精神)。

* ============================================================================
* 23. 经纪网络指标 (阶段47: 经纪网络)
* ============================================================================

label variable brokerage_eigen_cent "经纪网络特征向量中心度"
* shock 三轨 (2026-07-03): 同期版含年FE精确共线, 回归请用 lag1 变体
label variable industry_neg_shock "行业负面冲击"
capture label variable industry_neg_shock_ctx "行业负面冲击(上下文轨)"
capture label variable industry_neg_shock_lag1_ctx "行业负面冲击滞后1期(上下文轨)"
label variable brokerage_fire_sale "经纪网络火灾甩卖"

* ============================================================================
* 24. 嵌入同行网络指标 (W-轨扩展 2026-07-03: legacy=W取全文文本; diag=W与情感同轨)
* ============================================================================

label variable emb_peer_tone_lag1_full "嵌入同行情感滞后1期(全文)"
capture label variable emb_peer_tone_lag1_ctx "嵌入同行情感滞后1期(W=全文,情感=上下文)"
capture label variable emb_peer_tone_diag_lag1_ctx "嵌入同行情感对角滞后1期(W=上下文)"
label variable bank_emb_sim_mean_lag1 "银行嵌入相似度均值(滞后1期)"
capture label variable bank_emb_sim_mean_lag1_ctx "银行嵌入相似度均值(滞后1期,W=上下文)"

* ============================================================================
* 25. LLM同行IV指标 (阶段48: LLM同行IV)
* ============================================================================

* 25.1 不同阈值的LLM同行IV
label variable llm_peer_count_70 "LLM同行数量(阈值70%)"
label variable llm_peer_tone_iv_full_70 "LLM同行情感IV(阈值70%,全文)"
label variable llm_peer_coverage_iv_70 "LLM同行覆盖IV(阈值70%)"

label variable llm_peer_count_75 "LLM同行数量(阈值75%)"
label variable llm_peer_tone_iv_full_75 "LLM同行情感IV(阈值75%,全文)"
label variable llm_peer_coverage_iv_75 "LLM同行覆盖IV(阈值75%)"

label variable llm_peer_count_80 "LLM同行数量(阈值80%)"
label variable llm_peer_tone_iv_full_80 "LLM同行情感IV(阈值80%,全文)"
label variable llm_peer_coverage_iv_80 "LLM同行覆盖IV(阈值80%)"

label variable llm_peer_count_85 "LLM同行数量(阈值85%)"
label variable llm_peer_tone_iv_full_85 "LLM同行情感IV(阈值85%,全文)"
label variable llm_peer_coverage_iv_85 "LLM同行覆盖IV(阈值85%)"

label variable llm_peer_count_90 "LLM同行数量(阈值90%)"
label variable llm_peer_tone_iv_full_90 "LLM同行情感IV(阈值90%,全文)"
label variable llm_peer_coverage_iv_90 "LLM同行覆盖IV(阈值90%)"

* 25.2 默认阈值LLM同行IV
label variable llm_peer_count "LLM同行数量(默认阈值)"
label variable llm_peer_tone_iv_full "LLM同行情感IV(默认阈值,全文)"
label variable llm_peer_coverage_iv "LLM同行覆盖IV(默认阈值)"

* 25.3 同行竞争指数
label variable peer_compete_idx_70 "同行竞争指数(阈值70%)"
label variable peer_compete_idx_75 "同行竞争指数(阈值75%)"
label variable peer_compete_idx_80 "同行竞争指数(阈值80%)"
label variable peer_compete_idx "同行竞争指数(默认阈值)"
label variable peer_compete_idx_85 "同行竞争指数(阈值85%)"
label variable peer_compete_idx_90 "同行竞争指数(阈值90%)"

