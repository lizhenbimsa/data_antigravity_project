*================================================================
* 内生性稳健性检验 Stata 模板
* 参考文献:
*   Lewbel, A. (2012). Using heteroscedasticity to identify and
*   estimate mismeasured and endogenous regressor models.
*   JBES, 30(1), 67-80.
*   DOI: 10.1080/07350015.2012.643126
*
*   Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect
*   corporate financial policy? JF, 69(1), 139-178.
*   DOI: 10.1111/jofi.12094
*
*   Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can generative
*   AI help identify peer firms? RAS, 30(4), 3344-3386.
*   DOI: 10.1007/s11142-025-09892-6
*
*   Hoberg, G., & Phillips, G. (2016). Text-based network industries
*   and endogenous product differentiation. JPE, 124(5), 1423-1465.
*   DOI: 10.1086/688176
*================================================================

* 前置安装
* ssc install ivreg2h
* ssc install ivreghdfe

*=== 1. Lewbel (2012) 异方差 IV ===
* 无需外部工具变量, 利用误差项异方差性构造内部 IV
ivreg2h Y controls (llm_vote_tone_full = ), ///
    cluster(bank_province)
estat overid       // Hansen J 过度识别检验
estat firststage   // 第一阶段 F 统计量

*=== 2. 省级 LOO IV ===
ivreghdfe Y (llm_vote_tone_full = prov_leave1out_tone_full) ///
    controls, absorb(target_bank year) cluster(bank_province)
estat firststage
estat overid

*=== 3. LLM-Peer IV ===
ivreghdfe Y (llm_vote_tone_full = llm_peer_tone_iv_full) ///
    controls, absorb(target_bank year) cluster(bank_province)
estat firststage
estat overid

*=== 4. Embedding Peer 作为控制变量 ===
reghdfe Y llm_vote_tone_full emb_peer_tone_lag1_full ///
    controls, absorb(target_bank year) cluster(bank_province)
