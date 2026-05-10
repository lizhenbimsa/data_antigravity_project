/*==============================================================================
  文件: 04_label_media.do
  目的: 为媒体注意力和异质性指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 9. 媒体注意力指标 (阶段42: 金融科技注意力 + 媒体异质性)
* ============================================================================

* 9.1 金融科技注意力指数
label variable ft_attn_yr "金融科技注意力指数(年度)"
label variable ft_attn_prov "金融科技注意力指数(省级)"
label variable ft_attn_city "金融科技注意力指数(市级)"
label variable has_coverage "是否有新闻覆盖"

* 9.2 媒体广度
label variable media_breadth "媒体广度(独立媒体数)"
label variable media_hhi "媒体集中度HHI指数"

* 9.3 媒体类型异质性 - 金融vs综合媒体
label variable fin_media_frac "金融媒体占比"
label variable comp_media_frac "综合媒体占比"
label variable tone_fin_media_full "金融媒体情感(全文)"
label variable tone_comp_media_full "综合媒体情感(全文)"
label variable tone_other_media_full "其他媒体情感(全文)"
label variable tone_gap_fin_other_full "金融-其他媒体情感差(全文)"
label variable tone_gap_comp_other_full "综合-其他媒体情感差(全文)"
label variable tone_gap_fin_comp_full "金融-综合媒体情感差(全文)"

* 9.4 媒体层级异质性 - 中央vs地方
label variable central_media_frac "中央媒体占比"
label variable tone_central_media_full "中央媒体情感(全文)"
label variable tone_local_media_full "地方媒体情感(全文)"
label variable tone_gap_central_local_full "中央-地方媒体情感差(全文)"

* 9.5 媒体性质异质性 - 官方vs非官方
label variable official_media_frac "官方媒体占比"
label variable tone_official_media_full "官方媒体情感(全文)"
label variable tone_nonoff_media_full "非官方媒体情感(全文)"
label variable tone_gap_official_nonoff_full "官方-非官方媒体情感差(全文)"

* 9.6 媒体市场化程度
label variable market_media_frac "市场化媒体占比"
label variable tone_market_media_full "市场化媒体情感(全文)"
label variable tone_nonmkt_media_full "非市场化媒体情感(全文)"
label variable tone_gap_market_nonmkt_full "市场化-非市场化媒体情感差(全文)"

* 9.7 媒体深度报道
label variable deepdive_media_frac "深度报道媒体占比"
label variable tone_deepdive_media_full "深度报道媒体情感(全文)"
label variable tone_nondeep_media_full "非深度报道媒体情感(全文)"
label variable tone_gap_deepdive_nondeep_full "深度-非深度媒体情感差(全文)"

* 9.8 媒体发行频率
label variable daily_media_frac "日报媒体占比"
label variable tone_daily_media_full "日报媒体情感(全文)"
label variable tone_nondaily_media_full "非日报媒体情感(全文)"
label variable tone_gap_daily_nondaily_full "日报-非日报媒体情感差(全文)"

* 9.9 地理邻近性 - 本省vs外省
label variable homeprov_media_frac "本省媒体占比"
label variable tone_homeprov_media_full "本省媒体情感(全文)"
label variable neg_frac_homeprov_full "本省媒体负面占比(全文)"
label variable tone_nonprov_media_full "外省媒体情感(全文)"
label variable neg_frac_nonprov_full "外省媒体负面占比(全文)"
label variable tone_gap_homeprov_nonprov_full "本省-外省媒体情感差(全文)"

* 9.10 地理邻近性 - 本市vs外市
label variable homecity_media_frac "本市媒体占比"
label variable tone_homecity_media_full "本市媒体情感(全文)"
label variable neg_frac_homecity_full "本市媒体负面占比(全文)"
label variable tone_noncity_media_full "外市媒体情感(全文)"
label variable neg_frac_noncity_full "外市媒体负面占比(全文)"
label variable tone_gap_homecity_noncity_full "本市-外市媒体情感差(全文)"

* 9.11 媒体存续状态
label variable ceased_media_frac "已停刊媒体占比"

