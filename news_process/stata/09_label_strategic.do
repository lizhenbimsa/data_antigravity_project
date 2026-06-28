/*==============================================================================
  文件: 09_label_strategic.do
  目的: 为战略差异度和政策对齐度指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 26. 战略差异度指标 (阶段25: strategic_diff, 主体为 TF-IDF/LDA/Embedding 同行差异度;
*     v3.14.0 起本地 text2vec 稳健轨 *_t2v 已整体移除; Qwen⟂large co-primary 双轨的 *_lg
*     列标签由 pipeline/panel/stata_export.py::HEURISTIC_LABELS 自动派生, 不在此手工 .do 重复)
* ============================================================================

* 26.1 TF-IDF战略差异度 (全文轨道)
label variable strat_diff_n3 "战略差异度N3(TF-IDF字符)"
label variable strat_diff_n3_w "战略差异度N3加权(TF-IDF字符)"
label variable strat_diff_n4 "战略差异度N4(TF-IDF字符)"
label variable strat_diff_n4_w "战略差异度N4加权(TF-IDF字符)"
label variable strat_diff_n5 "战略差异度N5(TF-IDF字符)"
label variable strat_diff_n5_w "战略差异度N5加权(TF-IDF字符)"
label variable strat_diff_n6 "战略差异度N6(TF-IDF字符)"
label variable strat_diff_n6_w "战略差异度N6加权(TF-IDF字符)"
label variable strat_diff_n7 "战略差异度N7(TF-IDF字符)"
label variable strat_diff_n7_w "战略差异度N7加权(TF-IDF字符)"

label variable strat_sim_max "战略最大相似度(TF-IDF字符)"
label variable strat_sim_max_w "战略最大相似度加权(TF-IDF字符)"

* 26.2 LDA战略差异度
label variable strat_diff_n5_lda "战略差异度N5(LDA)"
label variable strat_sim_max_lda "战略最大相似度(LDA)"

* 26.3 Embedding战略差异度
label variable strat_diff_n5_emb "战略差异度N5(Embedding)"
label variable strat_sim_max_emb "战略最大相似度(Embedding)"

* 26.4 质心差异度
label variable centroid_diff_tfidf_c "质心差异度(TF-IDF字符)"
label variable centroid_diff_tfidf_w "质心差异度(TF-IDF词)"
label variable centroid_diff_lda "质心差异度(LDA)"
label variable centroid_diff_emb "质心差异度(Embedding)"

* 26.5 战略流动性
label variable strat_fluidity "战略流动性(TF-IDF字符)"
label variable strat_fluidity_w "战略流动性(TF-IDF词)"

* 26.6 文本连贯性 (全文轨道)
label variable coh_tfidf_c_full "文本连贯性(TF-IDF字符,全文)"
label variable coh_tfidf_w_full "文本连贯性(TF-IDF词,全文)"
label variable coh_lda_full "文本连贯性(LDA,全文)"
label variable coh_emb_full "文本连贯性(Embedding,全文)"

* 26.7 上下文轨道战略差异度
label variable strat_diff_n5_ctx "战略差异度N5(TF-IDF字符,上下文)"
label variable strat_diff_n5_w_ctx "战略差异度N5加权(TF-IDF字符,上下文)"
label variable strat_sim_max_ctx "战略最大相似度(TF-IDF字符,上下文)"
label variable strat_sim_max_w_ctx "战略最大相似度加权(TF-IDF字符,上下文)"
label variable strat_diff_n5_lda_ctx "战略差异度N5(LDA,上下文)"
label variable strat_sim_max_lda_ctx "战略最大相似度(LDA,上下文)"
label variable strat_diff_n5_emb_ctx "战略差异度N5(Embedding,上下文)"
label variable strat_sim_max_emb_ctx "战略最大相似度(Embedding,上下文)"

label variable centroid_diff_tfidf_c_ctx "质心差异度(TF-IDF字符,上下文)"
label variable centroid_diff_tfidf_w_ctx "质心差异度(TF-IDF词,上下文)"
label variable centroid_diff_lda_ctx "质心差异度(LDA,上下文)"
label variable centroid_diff_emb_ctx "质心差异度(Embedding,上下文)"

label variable coh_tfidf_c_ctx "文本连贯性(TF-IDF字符,上下文)"
label variable coh_tfidf_w_ctx "文本连贯性(TF-IDF词,上下文)"
label variable coh_lda_ctx "文本连贯性(LDA,上下文)"
label variable coh_emb_ctx "文本连贯性(Embedding,上下文)"

* ============================================================================
* 27. 政策对齐度指标 (阶段15: 文章级政策语义对齐度)
* ============================================================================

* 27.1 权威政策相似度 (全文轨道)
label variable auth_sim_tfidf_c_full "权威政策相似度(TF-IDF字符,全文)"
label variable auth_sim_tfidf_w_full "权威政策相似度(TF-IDF词,全文)"
label variable auth_sim_lda_full "权威政策相似度(LDA,全文)"
label variable auth_sim_emb_full "权威政策相似度(Embedding,全文)"

* 27.2 权威政策相似度 (上下文轨道)
label variable auth_sim_tfidf_c_ctx "权威政策相似度(TF-IDF字符,上下文)"
label variable auth_sim_tfidf_w_ctx "权威政策相似度(TF-IDF词,上下文)"
label variable auth_sim_lda_ctx "权威政策相似度(LDA,上下文)"
label variable auth_sim_emb_ctx "权威政策相似度(Embedding,上下文)"

