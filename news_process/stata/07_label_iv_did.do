/*==============================================================================
  文件: 07_label_iv_did.do
  目的: 为Bartik IV和DID指标添加变量标签
  作者: Claude Code
  日期: 2026-05-10
==============================================================================*/

* ============================================================================
* 20. Bartik IV指标 (阶段44: Bartik IV + DID)
* ============================================================================

* 20.1 银行类型Bartik IV
label variable bank_type "银行类型"
label variable bartik_type_iv_full "银行类型Bartik IV(全文)"
label variable bartik_type_iv_ctx "银行类型Bartik IV(上下文)"
label variable bartik_type_iv_title "银行类型Bartik IV(标题)"
label variable bartik_type_iv_full_t0 "银行类型Bartik IV t0(全文)"
label variable bartik_type_iv_ctx_t0 "银行类型Bartik IV t0(上下文)"
label variable bartik_type_iv_full_t1 "银行类型Bartik IV t1(全文)"
label variable bartik_type_iv_ctx_t1 "银行类型Bartik IV t1(上下文)"
label variable bartik_type_iv_full_t01 "银行类型Bartik IV t01(全文)"
label variable bartik_type_iv_ctx_t01 "银行类型Bartik IV t01(上下文)"

* 20.2 银行规模Bartik IV
label variable bank_scale "银行规模"
label variable bartik_scale_iv_full "银行规模Bartik IV(全文)"
label variable bartik_scale_iv_ctx "银行规模Bartik IV(上下文)"
label variable bartik_scale_iv_title "银行规模Bartik IV(标题)"

* 20.3 金融科技Bartik IV
label variable digital_frontier "数字前沿银行"
label variable bartik_fintech_share_app "金融科技应用份额"
label variable bartik_fintech_share_tech "金融科技技术份额"
label variable bartik_fintech_iv_full "金融科技Bartik IV(全文)"
label variable bartik_fintech_iv_ctx "金融科技Bartik IV(上下文)"
label variable bartik_fintech_iv_title "金融科技Bartik IV(标题)"

* 20.4 媒体类型Bartik IV
label variable bartik_media_share_comp "综合媒体份额"
label variable bartik_media_share_fin "金融媒体份额"
label variable bartik_media_iv_full "媒体类型Bartik IV(全文)"
label variable bartik_media_iv_ctx "媒体类型Bartik IV(上下文)"
label variable bartik_media_iv_title "媒体类型Bartik IV(标题)"

* 20.5 媒体权威性Bartik IV
label variable bartik_mauth_share_high "高权威媒体份额"
label variable bartik_mauth_share_low "低权威媒体份额"
label variable bartik_mauth_share_mid "中权威媒体份额"
label variable bartik_mauth_iv_full "媒体权威Bartik IV(全文)"
label variable bartik_mauth_iv_ctx "媒体权威Bartik IV(上下文)"
label variable bartik_mauth_iv_title "媒体权威Bartik IV(标题)"

* 20.6 地理邻近性Bartik IV
label variable bartik_geoprox_share_local "本地媒体份额"
label variable bartik_geoprox_share_nonlocal "外地媒体份额"
label variable bartik_geoprox_iv_full "地理邻近Bartik IV(全文)"
label variable bartik_geoprox_iv_ctx "地理邻近Bartik IV(上下文)"
label variable bartik_geoprox_iv_title "地理邻近Bartik IV(标题)"

* ============================================================================
* 21. DID政策冲击指标
* ============================================================================

* 21.1 数字货币试点 (DCEP)
label variable dcep_treat_year "DCEP试点年份"
label variable dcep_treated "DCEP处理组"
label variable dcep_post "DCEP试点后"
label variable dcep_rel_year "DCEP相对年份"
label variable dcep_lead3 "DCEP前3年"
label variable dcep_lead2 "DCEP前2年"
label variable dcep_lag0 "DCEP当年"
label variable dcep_lag1 "DCEP后1年"
label variable dcep_lag2 "DCEP后2年"
label variable dcep_lag3 "DCEP后3年"
label variable dcep_lead4plus "DCEP前4年及以上"
label variable dcep_lag4plus "DCEP后4年及以上"

* 21.2 监管沙盒试点 (Sandbox)
label variable sandbox_treat_year "沙盒试点年份"
label variable sandbox_treated "沙盒处理组"
label variable sandbox_post "沙盒试点后"
label variable sandbox_rel_year "沙盒相对年份"
label variable sandbox_lead3 "沙盒前3年"
label variable sandbox_lead2 "沙盒前2年"
label variable sandbox_lag0 "沙盒当年"
label variable sandbox_lag1 "沙盒后1年"
label variable sandbox_lag2 "沙盒后2年"
label variable sandbox_lag3 "沙盒后3年"
label variable sandbox_lead4plus "沙盒前4年及以上"
label variable sandbox_lag4plus "沙盒后4年及以上"

* 21.3 DDD交互项
label variable dcep_ddd_digfront "DCEP×数字前沿DDD"
label variable sandbox_ddd_digfront "沙盒×数字前沿DDD"

* 21.4 其他政策冲击
label variable depins_post "存款保险制度后"
label variable stress_period "压力时期"
label variable tone_x_stress_full "情感×压力时期(全文)"
label variable tone_x_depins_full "情感×存款保险(全文)"

