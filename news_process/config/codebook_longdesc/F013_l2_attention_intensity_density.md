---
family_id: F013
columns:
- attention_intensity_density_ctx
- attention_intensity_density_full
- attention_intensity_density_ss
unit: 强度加权曝光密度 (无量纲, 每篇平均金科技术强度; 下界 0, 上不封顶)
formula: "attention_intensity_density_{track} = ( Σ_d fintech_intensity_score_{track} ) / N_all; track ∈ {full, ctx, ss}; d 遍历经 restrict_to_verified 门控后的 stage-21 verified 金科文章 (分子域门控, 剔约四分之一被判伪); N_all = 该银行-年在 12_full 内的全部新闻篇数 (分母未门控)"
producer: news_process/pipeline/panel/attention_media.py::compute_attention_treatments
upstream:
- 12_news_fintech.parquet (12_full 全部银行新闻, 提供分母 N_all)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 15_fintech_intensity.parquet (fintech_intensity_score_full / _ctx / _ss)
- 40_panel_yearly.parquet (银行-年聚合宿主)
citations:
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3105-3147
- doi: 10.1111/jofi.13219
  type: journal
  authors: Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R.
  year: 2023
  title: "Firm-level climate change exposure"
  venue: The Journal of Finance
  vol: 78
  issue: 3
  pages_or_artno: 1449-1498
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: "In search of attention"
  venue: The Journal of Finance
  vol: 66
  issue: 5
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.jfineco.2023.103745"
  type: journal
  authors: "Babina, T., Fedyk, A., He, A., & Hodson, J."
  year: 2024
  title: "Artificial intelligence, firm growth, and product innovation"
  venue: "Journal of Financial Economics"
new_dois:
  - "10.1016/j.jfineco.2023.103745"
---

## CORE

【构念与来源】
本家族三列度量的是「金融科技注意力强度密度」(attention intensity density): 把某家银行在某一年内每篇新闻的金融科技技术强度加总, 再除以该银行-年的全部新闻篇数, 得到「平均每篇新闻承载多少金科技术强度」这一强度归一化的曝光密度。它服务于 P2 论文 bank_fintech_attention 的处理变量族, 与同一生产函数产出的累积曝光指数 attention_index 构成一对互补测度: attention_index 取 ln(1 + Σ 强度) 是 extensive (广延) 累积曝光, 会随报道体量上升而机械放大; 本密度列则把强度总量按篇数摊薄, 是 intensive (强度) 归一化的每篇平均, 剥离了「单纯报道多」这一体量通道, 更贴近报道内容本身的技术密度。用大白话说: attention_index 回答「这家银行今年被写了多少金科的量」, 本密度列回答「平均每篇写得有多深」。数据源头为经过 stage 13 银行∧金科邻近共现硬过滤、stage 14 三轨文本物化、stage 15 金科强度打分后的文章级测度 fintech_intensity_score, 再在 stage 40 面板聚合时按银行-年求和并除以分母 N_all。分母 N_all 取自 12_full 内该银行该年的全部新闻篇数 (议程分母, track-agnostic), 而非仅金科文章, 使密度带有「金科议程在整体新闻议程中的占位深度」含义。零金科曝光的银行-年, 分子为 0, 密度取真零 (0.0), 属真实的「无金科覆盖」而非缺失。

需显式披露一处分子分母不对称的样本域口径 (顶刊 P2 data/sample 要求, 与去重披露同级): 分子并非该银行-年的全部金科文章, 而是经 restrict_to_verified 门控后仅保留 stage-21 verified 集内的金科文章。生产函数 compute_attention_treatments 在求和前对文章级强度帧 s14 施加 (docid, target_bank) 的 semi-join, 把未通过 stage-21 验证 (LLM 判伪) 的金科文章从分子中剔除, 剔除率约为四分之一; 分母 N_all 则保持未门控的全部新闻篇数。因此本密度更精确的语义是「每篇 (全体) 新闻平均承载多少经验证为真的金科技术强度」, 分子域 (verified 金科) 与分母域 (全部新闻) 不同层, 属刻意的口径选择而非缺陷: 分子门控意在剔除判伪文章带来的强度虚增, 分母未门控意在保留「金科议程在整体议程中的占位」这一议程分母含义。ss 轨无额外门控代码, 因 s14 门控发生在 track-agnostic 的文章级帧上, 三轨分子自动落入同一 verified 宇宙, 与政策对齐族 (runner 内 _filter_to_verified_universe) 同域。论文 data/sample 段与 Table 1 注须报告该 verified 宇宙及其剔除率。

【方法学与计算】
计算公式为 attention_intensity_density_{track} = Σ_d fintech_intensity_score_{track} / N_all, 其中 d 遍历该银行-年经 restrict_to_verified 门控后落在 stage-21 verified 集内的金科文章 (分子域门控, 见上文样本域披露), track ∈ {full, ctx, ss}; 分母 N_all 为未门控的全部新闻篇数。生产函数 compute_attention_treatments 内对该列施加值域守卫 [0, +inf): 由于强度非负、篇数为正, 密度恒非负但不设上界 (故命名用「density」而非「share」, 明确它不是有界 [0,1] 份额)。三轨的分子严格逐轨取用各自轨道的强度打分: full 轨用 fintech_intensity_score_full (标题 prepend 后的全文正文), ctx 轨用 _ctx (标题加实体上下文窗口), ss 轨用 _ss (标题加银行∧金科同句共现窗口); 分母 N_all 三轨共享同一议程分母。缺列时生产函数以 `if col not in panel.columns: continue` 优雅跳过, 不伪造零值。该密度概念上对应 Hassan et al. (2019) 政治风险测度里 intensive 归一化份额 (命中量除以文本总量) 的思路, 而非 Fang & Peress (2009) 式的覆盖量本身; 二者的区分在本仓库的 metric-audit 中被显式锚定并写入生产函数注释, 避免把广延曝光误当强度份额。

【文献定位】
金融媒体覆盖对资产价格与真实企业行为具有可度量后果, 是这条测度线的文献母体: Fang & Peress (2009) 证明媒体覆盖度进入股票横截面定价, Da et al. (2011) 用搜索量给「投资者注意力」一个可观测代理, Tetlock (2007) 则把媒体内容 (语气) 与市场反应联系起来。本密度列在这一谱系里取「强度归一化」而非「体量」路线, 方法论直接呼应 Hassan et al. (2019) 把公司层暴露定义为命中片段占文本比重的做法, 以及 Sautner et al. (2023) 把气候暴露构造为归一化文本频次的范式。文本作为数据的一般方法学基础见 Gentzkow et al. (2019); Bybee et al. (2024) 从商业新闻中提取主题强度并与宏观周期关联, 为「新闻强度密度」这类聚合量提供了近期的度量学支撑。三轨 (full/ctx/ss) 在本家族内互为稳健性、不分主次, 各自 just-identified 并排进入各自回归, 严禁把不同轨道混入同一 over-identified Hansen J 检验; 留篇门控采用 full-only 口径 (2026-06-29), 即某文章是否算作一篇银行金科报道只看 full 轨判定, ctx/ss 为条件于 full 留篇集的测度轨与稳健性轨。Babina, Fedyk, He & Hodson (2024, Journal of Financial Economics) 构造企业层面人工智能投资强度的文本/记录派生测度并将其加总为强度指标, 方法论上呼应本家族把逐篇金科技术强度加总并按篇数归一为密度的强度量化思路。

## VAR: attention_intensity_density_full

【变体差分】
本列为家族的 canonical 轨 (full)。full 轨文本 = 标题 prepend 到全文正文后的完整文章体, 分子取 fintech_intensity_score_full 在该银行-年金科文章上的加总, 分母 N_all 为该银行-年在 12_full 内的全部新闻篇数。它对应 P2 attention 处理变量族里强度归一化路线的主口径: 与同族累积曝光指数 attention_index_full (ln(1+Σ强度), extensive 广延) 相比, 本列把强度总量按篇数摊薄为每篇平均, 剥离报道体量通道, 是 intensive 强度密度; 与有界份额 attention_pct (N_ft/N_all ∈ [0,1]) 相比, 本列以「强度」而非「篇数」为分子, 故非有界、命名用 density 而非 share。full 轨是留篇门控 (full-only, 2026-06-29) 的判定轨, 也是行宇宙的定义轨, ctx/ss 两列在此基础上作条件测度。full 与 ctx/ss 互为稳健性、不分主次, 各自 just-identified 并排进各自回归, 禁混入同一 over-identified Hansen J。零金科曝光银行-年密度取真零 0.0 而非 NaN, 表示真实无覆盖。值域守卫 [0, +inf) 在生产函数 compute_attention_treatments 内校验。之所以选 full 轨作 canonical, 一方面是它与留篇门控判定轨一致 (行宇宙即由 full 轨的 llm_verified_full 定义), 概念上「一篇被算作银行金科报道的文章, 其整篇技术强度都可归入本行注意力」这一最宽归因是最保守、最不易漏计的基准; 另一方面 ctx/ss 是在 full 定义的留篇集上进一步收窄归因, 逻辑上从属于 full, 故以 full 为主轨、以 ctx/ss 为并排稳健性对照最自然。使用时应将本列理解为「平均每篇报道承载的金科技术密度」, 与体量口径 attention_index、有界议程份额 attention_pct 一并进入描述与稳健性, 但不与它们混入同一 over-identified 联合矩条件, 亦不与 ctx/ss 孪生列混入同一 Hansen J。

## VAR: attention_intensity_density_ctx

【变体差分】
本列为实体窗口口径 (ctx) 稳健性轨。与 canonical 的 full 轨唯一差别在文本轨道: ctx 轨文本 = 标题 prepend 到实体上下文窗口 (entity-context 窗口, 只保留银行实体附近的窗口正文而非全文), 分子相应取 fintech_intensity_score_ctx 的银行-年加总, 分母 N_all 仍为共享的全部新闻篇数议程分母。其经济含义是「把注意力强度归因到确实落在本行实体语境附近的文字」, 相比 full 轨的整篇归因更保守, 削弱了「同篇提及多家实体时把强度整体记在本行头上」的借位污染。ctx 轨与 full/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排进各自回归, 严禁三轨混入同一 over-identified Hansen J。在留篇门控 full-only 口径下, ctx 为条件于 full 留篇集的测度轨: 行宇宙由 full 轨判定, ctx 列在该子集上按轨自算, 缺列则优雅跳过不借 full 分子填补。零金科曝光取真零 0.0, 值域守卫 [0, +inf)。设计上 ctx 轨的实体窗口归因比 full 的整篇归因更收窄, 意在提供一条与 full 非冗余的规格对照轨: 当同篇报道同时提及多家实体时, ctx 只把落在本行实体窗口内的强度记入本行, 从而与 full 的整篇归因在「借位归因」维度上形成可对比的宽严差。此为构造层面的设计意图, 不对两轨相关性水平或稳健性排序作任何经验断言 (相关性由样本决定, 且在 T=2 开发面板上 ctx/ss 近零方差, 相关排序在盘上语料不可成立); 三轨是否同向稳健应交由各自 just-identified 回归的实证结果判定, 本文不预判。分子域门控与 CORE 一致: ctx 轨分子同样只累加经 restrict_to_verified 门控后的 verified 金科文章强度, 分母 N_all 为共享的未门控议程分母。需要强调, ctx 与 full 的判别口径不对称: 银行侧采用否定加短名过滤, 金科侧采用裸自动机匹配 607 词; ctx 窗口的实体归因让本列在「同篇同时报道多家银行的金科动向」情形下, 只把落在本行实体窗口内的强度记入本行, 从而与 full 的整篇归因形成规格对照, 用以检验主结论是否被「借位归因」驱动。当某银行-年在 ctx 轨下无有效金科文本时该轨密度取真零, 不回填 full 轨分子, 保证三轨的分子严格逐轨、互不借用。

## VAR: attention_intensity_density_ss

【变体差分】
本列为银行∧金科同句共现口径 (ss) 稳健性轨。与 full/ctx 的差别在文本轨道: ss 轨文本 = 标题 prepend 到银行与金科词在同一句子内共现 (同句 ± N 窗, 半径由 config filtering 的 ss_sentence_radius 控制, 默认 1) 的最窄语境, 分子取 fintech_intensity_score_ss 的银行-年加总, 分母 N_all 仍为共享议程分母。它是三轨中归因最严格的一轨: 只有当银行名与金科词真正同句相邻时该篇强度才被计入, 因而对「银行与金科分处两段、并非直接谈论本行金科业务」的稀释最不敏感。ss 轨的回退语义镜像 ctx: 当某文章无银行∧金科同句共现时, 其 ss 文本降级为全文 body 并标记 ss_is_fallback=True, 与 ctx 共享 n_articles 分母; 当金科自动机 FINTECH_AC 为 None 时 *_is_fallback 全 True 优雅降级。ss 与 full/ctx 三轨互为稳健性、不分主次, 各自 just-identified 并排进各自回归, 禁混入同一 over-identified Hansen J; 在 full-only 留篇门控下 ss 为条件于 full 留篇集的测度轨。零金科曝光取真零 0.0, 值域守卫 [0, +inf); 在 T=2 开发面板上 ss 轨可能因语料稀薄而近零方差, 属预期退化, 生产 T=19 语料下正常。ss 轨的价值在于它把「注意力强度」的归因收窄到银行与金科同句相邻这一最强共现证据上, 因而是三轨中对「稀释性提及」最不敏感、判别最严的一轨: 若主结论在 full (整篇归因)、ctx (实体窗口归因) 与 ss (同句归因) 三种由宽到严的归因口径下同向稳健, 则可较有力地排除结论由某一特定归因宽严度人为造成的担忧。ss 的同句共现原语与 stage 13 邻近共现硬过滤是两个不同口径, 前者严格同句、后者 ± 句窗, 二者不得互相复用。三轨仅作规格稳健性并排, 不设跨轨 FWER 联检模板, 也不把任一轨的密度与其孪生轨密度混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Babina, T., Fedyk, A., He, A., & Hodson, J. (2024). Artificial intelligence, firm growth, and product innovation. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2023.103745
<!-- rendered-citations:end -->
