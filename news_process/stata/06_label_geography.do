/*==============================================================================
  文件: 06_label_geography.do
  目的: 为地理缓冲和区域指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 16. 地理信息
* ============================================================================

label variable bank_province "银行所在省份"
label variable bank_city "银行所在城市"
label variable bank_zone "银行所在经济区"

* ============================================================================
* 17. 地理缓冲指标 (阶段43: 地理缓冲)
* ============================================================================

* 17.1 50公里缓冲区
label variable prox_50km_n_articles "50km缓冲区新闻数"
label variable prox_50km_frac "50km缓冲区新闻占比"
label variable prox_50km_is_local "50km缓冲区是否本地"
label variable prox_50km_n_media "50km缓冲区媒体数"
label variable prox_50km_tone_full "50km缓冲区情感(全文)"
label variable prox_50km_pos_frac "50km缓冲区正面占比"
label variable prox_50km_neg_frac "50km缓冲区负面占比"

* 17.2 100公里缓冲区
label variable prox_100km_n_articles "100km缓冲区新闻数"
label variable prox_100km_frac "100km缓冲区新闻占比"
label variable prox_100km_is_local "100km缓冲区是否本地"
label variable prox_100km_n_media "100km缓冲区媒体数"
label variable prox_100km_tone_full "100km缓冲区情感(全文)"
label variable prox_100km_pos_frac "100km缓冲区正面占比"
label variable prox_100km_neg_frac "100km缓冲区负面占比"

* 17.3 150公里缓冲区
label variable prox_150km_n_articles "150km缓冲区新闻数"
label variable prox_150km_frac "150km缓冲区新闻占比"
label variable prox_150km_is_local "150km缓冲区是否本地"
label variable prox_150km_n_media "150km缓冲区媒体数"
label variable prox_150km_tone_full "150km缓冲区情感(全文)"
label variable prox_150km_pos_frac "150km缓冲区正面占比"
label variable prox_150km_neg_frac "150km缓冲区负面占比"

* 17.4 200公里缓冲区
label variable prox_200km_n_articles "200km缓冲区新闻数"
label variable prox_200km_frac "200km缓冲区新闻占比"
label variable prox_200km_is_local "200km缓冲区是否本地"
label variable prox_200km_n_media "200km缓冲区媒体数"
label variable prox_200km_tone_full "200km缓冲区情感(全文)"
label variable prox_200km_pos_frac "200km缓冲区正面占比"
label variable prox_200km_neg_frac "200km缓冲区负面占比"

* ============================================================================
* 18. AI模仿渗透率 (区域模仿)
* ============================================================================

label variable ai_reg_province "AI模仿渗透率(省级)"
label variable ai_reg_city "AI模仿渗透率(市级)"
label variable ai_reg_50km "AI模仿渗透率(50km)"
label variable ai_reg_100km "AI模仿渗透率(100km)"
label variable ai_reg_150km "AI模仿渗透率(150km)"
label variable ai_reg_200km "AI模仿渗透率(200km)"

* ============================================================================
* 19. Leave-One-Out情感指标
* ============================================================================

* 19.1 省级LOO
label variable prov_leave1out_tone_full "省级LOO情感(全文)"
label variable prov_leave1out_tone_ctx "省级LOO情感(上下文)"
label variable prov_leave1out_dict_avg_tone_full "省级LOO词典情感(全文)"
label variable prov_leave1out_bert_avg_pos_full "省级LOO BERT正面(全文)"

* 19.2 市级LOO
label variable city_leave1out_tone_full "市级LOO情感(全文)"
label variable city_leave1out_tone_ctx "市级LOO情感(上下文)"
label variable city_leave1out_dict_avg_tone_full "市级LOO词典情感(全文)"
label variable city_leave1out_bert_avg_pos_full "市级LOO BERT正面(全文)"

* 19.3 经济区LOO
label variable zone_leave1out_tone_full "经济区LOO情感(全文)"
label variable zone_leave1out_tone_ctx "经济区LOO情感(上下文)"

