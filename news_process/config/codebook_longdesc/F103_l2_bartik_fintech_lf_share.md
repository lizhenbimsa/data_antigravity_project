---
family_id: F103
columns:
- bartik_fintech_lf_share_app
- bartik_fintech_lf_share_tech
unit: 基期份额 (proportion, [0,1]; 同一银行 app 与 tech 两列在剔除 other 后按行归一, 和为 1)
formula: "share_{i,k,T0} = 银行 i 在基期 T0 文章中 innovation_locus_full=k 的篇数 / 银行 i 基期文章在保留类别 {tech,app} 上的总篇数; k ∈ {tech(底层技术), app(应用场景)}; 剔除 other/未映射后归一"
producer: news_process/pipeline/panel/iv_did.py::compute_bartik_iv_fintech (runner.py 步骤 7e 以 group_prefix='fintech_lf' / category_col='innovation_locus_full' 调用)
upstream:
- 40_panel_yearly.parquet (target_bank, year 面板行宇宙)
- df_exploded 文章级长表 (target_bank, year, innovation_locus_full — LLM locus 分类, full 轨)
citations:
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: 102306
- doi: 10.1016/j.jfi.2019.100833
  type: journal
  authors: Thakor, A. V.
  year: 2020
  title: "Fintech and banking: What do we know?"
  venue: Journal of Financial Intermediation
  vol: 41
  pages_or_artno: 100833
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: Strategic Management Journal
  vol: 31
  issue: 3
  pages_or_artno: 306-333
new_dois: []
---

## CORE

【构念与来源】
本家族是金融科技类型维度 Bartik (shift-share) 工具变量的【基期份额】分量, 落在 innovation_locus_full 这一"创新落点"分类之上。金融科技报道被大语言模型分类阶段判为两种互斥落点: 底层技术 (tech, 对应文章级 innovation_locus_full 取值"底层技术") 与应用场景 (app, 对应"应用场景"), 另设 other 兜底类不进入份额分子分母。对每家目标银行, 在冻结的基期窗 T0 内统计其被报道文章在这两类上的篇数分布, 再在剔除 other 与未映射后按行归一, 得到该银行"技术侧暴露占比"与"应用侧暴露占比"两个数。这两列即 bartik_fintech_lf_share_tech 与 bartik_fintech_lf_share_app, 是 shift-share 设计里冻结不动的"份额" (share) 向量, 后续与"同类别里其他银行的留一 (leave-one-out) 年度情感推力" (shift) 相乘求和, 合成金融科技类型维度的 Bartik 工具变量 bartik_fintech_lf_iv_full / bartik_fintech_lf_iv_ctx / bartik_fintech_lf_iv_ss (合成端 shift 循环覆盖 full/ctx/ss 三轨, ss 轨消费银行∧金科同句情感 llm_vote_score_ss, 缺列时守卫置 NaN 优雅跳过, 镜像 ctx 回退语义; 三轨各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J)。前缀 lf 记号 = locus=full, 表示份额基于 full 轨的 innovation_locus_full; 与之并列另有一套 lc (locus=ctx) 基于 innovation_locus_ctx 的孪生份额 (bartik_fintech_lc_share_*), 二者以不同文本轨的落点分类为基期锚, 互为稳健性、不分主次。

【方法学与计算】
计算严格遵循 Goldsmith-Pinkham 等 (2020) 与 Adão、Kolesár、Morales (2019) 阐明的 shift-share 识别逻辑, 并采用预处理期 (pre-treatment) 冻结基期公理: 基期年 T0 取 max(面板最小年, 2010), 且工具构造前设 cutoff≤T0 的强制守卫, 使份额在处理发生之前即被冻结, 事后不随内生的报道量或情感变化而漂移。份额分母只含保留类别 {tech, app} 之和 (排除 other 与未映射的 NaN), 使每家银行两列之和恒为 1, 与 type/scale 等其他 Bartik 维度的"份额和=1"归一化口径可比。基期无文章、或基期文章全部落入 other/未映射的银行, 其份额与由此派生的工具变量保持 NaN (而非 fillna(0) 伪零暴露), 避免制造虚假的零工具值; 份额>0 但该类别当年 shift 因留一后组内仅剩自身而不可计算时, 工具变量亦沿 NaN 传播。识别诊断走 share 路径 (Rotemberg 权重) 而非 shift 准随机路径: 本项目的 shift 是同组其他银行留一情感均值, 属内生量, 故论文不主张"冲击准随机"的双重识别, 仅以份额外生性 (基期冻结 + 落点分类先于处理) 作为识别根。金融科技类型维度仅两类, 只提供一个有效工具自由度 (2 类 1 IV), 两列在数值上互补且高度共线, 建模时选其一进入方程即可, 另一由和为 1 的约束决定。

【文献定位】
"底层技术 vs 应用场景"的二分并非本项目独造, 而与金融科技研究里"技术能力"与"业务应用/场景落地"的经典划分同源。Gomber、Kauffman、Parker 与 Weber (2018) 在其对金融科技革命诸推力的框架中, 明确区分了底层技术创新与面向业务功能的应用创新, 是本落点维度最贴近的构念出处; Gomber、Koch 与 Siering (2017) 进一步给出数字金融/金融科技的分类学与研究议程, 直接支撑 locus 维的类别切分。Chen、Wu 与 Yang (2019) 以专利文本刻画金融科技创新的价值, 论证不同技术门类的创新在市场估值上异质, 为把"技术侧"与"应用侧"暴露分列而非合并提供了经济学理由。Adner 与 Kapoor (2010) 从创新生态系统的技术互依结构出发, 说明"底层技术组件"与"下游应用/互补品"处于价值创造链的不同位置、对企业绩效的作用机制不同, 呼应本家族把两类落点作为独立暴露维度的做法。方法学上, Adão、Kolesár 与 Morales (2019) 给出 shift-share 设计的推断理论, 是本工具份额外生性与标准误校正的规范参照。Thakor (2020) 与 Alfhaili、Bakoush 与 Wolfe (2026) 则从银行—金融科技互动与银行创新投入角度, 佐证以金融科技报道结构构造银行层面暴露的合理性。凡涉 full/ctx 双轨、lf/lc 双基期以及份额与 shift 两条识别路径, 本项目一律遵循"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"的口径, 避免把互补或高共线的工具堆进同一过度识别检验而伪造识别力。

## VAR: bartik_fintech_lf_share_app

【变体差分】
本列是金融科技类型维度 Bartik 份额向量中的【应用场景】分量。它统计每家目标银行在冻结基期 T0 内被报道文章中, LLM 落点分类 innovation_locus_full 判为"应用场景" (app) 的篇数, 除以该银行基期文章在保留类别 {tech, app} 上的总篇数 (剔除 other 与未映射), 得到该银行的"应用侧暴露占比"。语义上它刻画一家银行在基期被媒体聚焦于金融科技"业务应用、场景落地"一侧的相对强度, 而非底层技术能力一侧。它与家族孪生列 bartik_fintech_lf_share_tech 严格互补: 二者按行归一后和恒为 1, 因此本列 = 1 − share_tech, 两者高度共线, 只贡献一个有效工具自由度, 建模时二选一进入方程。轨道与基期口径上, 本列的 lf 记号锁定 full 轨落点 (innovation_locus_full), 与基于 ctx 轨落点的 bartik_fintech_lc_share_app 是两套独立基期份额, 二者互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。缺失语义与家族一致: 基期无文章或基期全 other 的银行本列保持 NaN, 不作零插补; 份额冻结于预处理期, 事后不随内生报道量漂移。本列只是"份额"而非工具本身, 须与同类别其他银行留一情感 shift 相乘求和后才合成 bartik_fintech_lf_iv_full / bartik_fintech_lf_iv_ctx / bartik_fintech_lf_iv_ss 工具变量 (合成端 shift 循环产 full/ctx/ss 三轨, ss 消费 llm_vote_score_ss 缺列则守卫置 NaN 镜像 ctx, 三轨各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J); 识别诊断走 Rotemberg 份额权重路径而非 shift 准随机路径, 论文不主张冲击外生的双重识别, 仅以基期冻结与落点分类先于处理作为份额外生性根据。

## VAR: bartik_fintech_lf_share_tech

【变体差分】
本列是金融科技类型维度 Bartik 份额向量中的【底层技术】分量。它统计每家目标银行在冻结基期 T0 内被报道文章中, LLM 落点分类 innovation_locus_full 判为"底层技术" (tech) 的篇数, 除以该银行基期文章在保留类别 {tech, app} 上的总篇数 (剔除 other 与未映射), 得到该银行的"技术侧暴露占比"。语义上它刻画一家银行在基期被媒体聚焦于金融科技"底层技术能力" (如支付清算、风控、区块链、云计算等技术根) 一侧的相对强度, 与应用场景一侧相对。它与家族孪生列 bartik_fintech_lf_share_app 严格互补: 二者按行归一后和恒为 1, 本列 = 1 − share_app, 两者高度共线, 类型维度整体只提供一个有效工具自由度 (2 类 1 IV), 建模时二选一进入方程即可。轨道与基期口径上, 本列的 lf 记号锁定 full 轨落点 (innovation_locus_full), 与基于 ctx 轨落点的 bartik_fintech_lc_share_tech 是两套独立基期份额, 二者互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。缺失语义与家族一致: 基期无文章或基期文章全落 other 的银行本列保持 NaN, 不作 fillna(0) 伪零; 份额冻结于预处理期 T0, 事后不随内生的报道结构或情感变化漂移。本列同为"份额"分量而非工具本身, 须与该类别里其他银行的留一年度情感 shift 相乘求和, 才合成金融科技类型维度的 Bartik 工具变量 bartik_fintech_lf_iv_full / bartik_fintech_lf_iv_ctx / bartik_fintech_lf_iv_ss (合成端 shift 循环覆盖 full/ctx/ss 三轨, ss 轨消费银行∧金科同句情感 llm_vote_score_ss, 缺列时守卫置 NaN 优雅跳过镜像 ctx 回退语义; 三轨各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J)。

<!-- rendered-citations:begin -->
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Thakor, A. V. (2020). Fintech and banking: What do we know?. Journal of Financial Intermediation, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation?. Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
<!-- rendered-citations:end -->
