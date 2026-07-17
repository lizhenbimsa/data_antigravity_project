---
family_id: F451
columns:
- neg_frac_homeprov_ctx
- neg_frac_homeprov_full
- neg_frac_homeprov_ss
unit: 比率/占比 (proportion, [0,1]; 分母=该银行-年在"本省媒体"子样本内的报道篇数)
formula: 'neg_frac_homeprov_{trk} = mean(is_negative{trk}) , 在 outlet 省份 == 银行总部所在省份 的本省媒体子样本内按 target_bank×year 分组计算; is_negative{trk} 是由 llm_vote_tone{trk} 预先派生的负面判定布尔列 (取值 1=负面/0=非负面), 分母为该子样本内的有效篇数; 与家族 F 同源的 homeprov_media_frac (媒体来源地理占比) 是分母口径的姊妹列但非同一构念'
producer: pipeline\panel\export.py ; pipeline\panel\attention_media.py
upstream:
- 21_tone_llms
- 11_news_bank
- config/bank_addresses.json (银行总部省份映射)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: Investor negativity derived from news shapes firm distress dynamics under bounded rationality
  venue: Journal of Economics and Development
  vol: '27'
  issue: '4'
  pages_or_artno: 309-321
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: '88'
  pages_or_artno: 67-75
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量"本地媒体负面报道占比"——在总部注册地媒体子样本内, 银行-年被判定为负面基调的报道篇数占比。构念根植于 Gurun & Butler (2012, Journal of Finance) 关于地方媒体偏好本地企业("home bias")的经典发现: 本地媒体因熟悉度、广告依赖、读者情感联结等机制, 在报道口径上系统性区别于外埠媒体, 既可能表现为更宽容(整体基调更正面, 参见家族 F 中 tone_gap_homeprov_nonprov 系列), 也可能表现为更尖锐的负面聚焦(本地丑闻更具新闻价值、监督动机更强)。neg_frac_homeprov 家族与 tone_gap_homeprov_nonprov(均值基调差)是互补而非重复的两把尺子: 后者衡量整体情感水平的地理落差, 前者专门刻画负面报道的浓度, 二者对同一"本地媒体是否偏袒"问题给出不同侧面的证据——一家银行可能在本地媒体处获得更高的平均基调, 但负面报道的绝对占比未必更低(例如正面报道数量放大稀释了均值, 负面篇数并未减少)。

分母口径是本家族的关键校对点: 本省媒体子样本由 outlet 注册省份(来自媒体来源元数据)与银行总部省份(读取 `config/bank_addresses.json` 得到的 target_bank→province 映射)匹配确定, 与 homeprov_media_frac(该银行-年报道中本省媒体篇数占全部媒体篇数之比)共享同一"本省"判据但服务不同分子——homeprov_media_frac 的分子是"本省媒体篇数", 分母是"全部媒体篇数"; 而 neg_frac_homeprov 的分母已收窄到本省媒体子样本内部, 分子是该子样本内被判负面的篇数。换言之 neg_frac_homeprov 回答的是"本省媒体报道这家银行时, 有多大比例是负面的", 而非"全部报道中本省媒体贡献的负面比例"——两者不可混淆, 后者需要额外一步与全样本负面篇数相除才能得到, 本家族并不产出该口径。

情感基调判定沿用留篇门控 full-only 铁律(2026-06-29): 一篇报道是否计入"负面"分子, 依据的是三家 LLM(gpt54nano/gemini31/deepseekv4)多数投票共识 llm_vote_tone, 且门控判据(是否是一篇有效的银行金科报道)取自 `llm_verified_full`——即无论本列自身取哪条轨道计算基调, 参与统计的文章行宇宙(是否落入分子分母的候选池)均以 full 轨的留篇判定为准, ctx/ss 是在该行宇宙子集上的 conditional-on-full 测度/稳健性轨, 不会引入 full 轨未覆盖的新文章。

【方法学与计算】
计算分三步: 第一步, 依据 stage 11(`news_bank`)确定的目标银行与该银行-年报道池, 结合 config 银行地理映射得到该银行总部所在省份; 第二步, 对每篇候选报道读取其发布媒体(outlet)的注册省份元数据, 保留 outlet省份==银行总部省份 的子集(即"本省媒体"子样本), 分母 n = 该子样本篇数; 第三步, 在该子样本内依据 stage 21 产出的 llm_vote_tone{trk} 预先派生出布尔列 is_negative{trk}(取值 1 表示该篇被判为负面基调、0 表示非负面), 对该子样本按 target_bank×year 分组求 is_negative{trk} 的均值, 即得 neg_frac_homeprov_{trk} ∈ [0,1]——分子等价于该子样本内 is_negative{trk}=1 的篇数, 分母为子样本篇数, 但代码实际消费的是预先派生的中间布尔列而非在聚合步骤内临时对 llm_vote_tone 逐篇重新判负, 这一实现细节不改变构念含义, 仅影响可追溯的计算路径。若某银行-年在本省无任何媒体报道(分母为 0), 该格取 NaN(而非 0), 避免"零负面"与"无本省媒体覆盖"两种截然不同的情形被误记为同一数值——这一 NaN 语义与家族内 tone_homeprov_media_full 等均值类测度共享同一空样本处理惯例。

三轨 full/ctx/ss 差异仅体现在情感判定所依据的文本窗口与 llm_vote_tone_{trk} 取值, 分母(本省媒体子样本的确定)不随轨道变化——地理归属是文章级客观元数据属性, 与文本窗口无关。full 轨基于标题+全文正文判定基调; ctx 轨基于标题+银行实体窗口判定; ss 轨基于标题+银行∧金科同句±N窗判定(默认 N=1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`), 若某篇文章不存在银行∧金科同句共现, ss 轨回退为镜像 ctx 的全文 body 语义(`ss_is_fallback=True`, 与 ctx 共享同一 n_articles 分母口径)。三轨作为地理媒体偏好构念在不同文本粒度下的测度实现, 严格遵循「各自 just-identified 并排、互为稳健性、不分主次」的家族铁律, 三条估计禁止混入同一 over-identified Hansen J 检验框架内联合识别。

【文献定位】
本家族的方法论谱系直接对接 Gurun & Butler (2012, Journal of Finance) 的地方媒体炒作(local media hype)研究设计——该文用本地广告收入依赖度作为媒体偏袒本地企业的识别工具, 发现本地报纸系统性对本地企业采取更正面、更少负面的报道基调, 进而影响股票估值与融资成本。本家族将该逻辑迁移到中国银行业新闻情境, 用"总部注册省份是否与媒体注册省份一致"作为本地/非本地的划分依据, 用负面报道占比而非均值基调作为观测量, 意在捕捉本地媒体在负面信息筛选上的独特行为模式。Piotroski, Wong & Zhang (2015, Journal of Accounting Research) 关于中国上市公司政治动机压制负面信息的证据为这一构念提供了制度背景支撑: 若地方政府与本地媒体存在治理关联, 本省媒体的负面报道占比理应系统性低于非本省媒体, 这正是 neg_frac_homeprov 与 neg_frac_nonprov 对照差分要检验的假说。负面基调的识别本身继承了 stage 21 三家 LLM 投票的判定框架, 而负面信息在情感分析中的度量稳健性问题(否定处理、语义范围界定)另见 Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 关于新闻驱动交易情境下否定范围检测的方法论讨论, 以及 Pham et al. (2025, Journal of Economics and Development) 关于新闻负面性与企业困境动态关系的近期实证, 后者为本家族"负面报道占比"这一构念在企业层面结果变量上的经济含义提供了当代实证参照。 与上述文献互补, Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度, 并将其应用于意大利银行的融资条件这一银行层级实证问题, 为"新闻语调→银行层级结果"这一链条提供了近期同域的前沿实践参照, 支撑本家族把本省媒体子样本内的负面报道占比视作可进入银行层级结果方程的解释变量。迁移边界须如实披露: 该文语料为意大利媒体 (意/英文), 非中国中文新闻; 其语调测度既不经由本项目 stage 21 三家 LLM 投票的判定框架, 也未做本省/非本省的媒体注册地切分, 更不含负面篇占比这一离散化处理, 且无 full/ctx/ss 三轨文本切分; 其 DV 为银行融资条件, 与本项目 P1 的 funding_cost 相近但口径与数据源不同。因此该文锚定的是应用域与构造链路的同构性, 而非 neg_frac_homeprov 公式中的任何具体一步。
## VAR: neg_frac_homeprov_ctx

【变体差分】
ctx 轨: 情感判定依据的文本窗口是"标题+银行实体窗口"(stage 14 `ctx_materializer` 物化的 `content_ctx`), 而非全文正文。分母(本省媒体子样本的界定)与 full 轨完全一致, 差异仅出现在分子——同一篇文章在 ctx 窗口下可能因文本范围收窄而被判定为不同的基调类别(例如全文中夹杂的其他银行负面信息在 ctx 窗口被剥离, 该银行相关句段基调偏中性或正面, 从而使这篇文章不落入 ctx 轨的负面分子, 但会落入 full 轨的负面分子; 反之亦然)。ctx 轨的候选文章行宇宙仍以 `llm_verified_full` 门控确定(conditional-on-full), 即 ctx 轨不会纳入 full 轨判定为"非有效银行金科报道"的文章, 只是在该固定行宇宙内换用更聚焦的文本窗口重新做基调判定。作为家族内三轨并排稳健性检验的一支, ctx 轨与 full/ss 轨互为稳健性、不分主次, 适合在正文包含大量与目标银行无关的背景信息(如综合财经新闻中提及多家机构)时, 检验负面占比结论对文本窗口选择的敏感度; 若三轨方向一致, 可增强本省媒体负面报道占比这一发现的稳健性论证力度。

从经济含义看, ctx 轨对本地媒体研究尤其重要, 因为 Gurun & Butler (2012) 强调的本地偏袒效应往往体现在与目标企业直接相关的段落而非泛泛的行业背景叙述中——若一篇综述性报道笼统提及区域金融业整体承压, 但涉及目标银行的实体窗口段落语气中性甚至正面, full 轨可能因整体负面氛围而将该文计入负面分子, ctx 轨则更贴近"媒体在谈论这家银行本身时说了什么"这一更严格的构念界定。使用者在解读 ctx 与 full 两轨差异时, 应将差异本身视为文本窗口选择的稳健性证据, 而非孰优孰劣的排他性判断, 三轨结果方向一致才是本家族地理偏好结论可信度的关键支撑。

## VAR: neg_frac_homeprov_full

【变体差分】
full 轨是本家族的 canonical 口径: 情感判定依据"标题+全文正文"完整文本(stage 21 `llm_vote_tone_full`), 分母与分子均在此文本窗口下计算得到。full 轨同时也是留篇门控的锚点——`llm_verified_full` 判定的有效报道集合是 ctx/ss 两轨的行宇宙上界, 换言之 full 轨自身的候选文章池即为家族三轨共享的最大行宇宙, 不存在被其余两轨"借用"分母的情形。在 P1(`bank_fintech_tone`)等下游论文模块中, full 轨相关的情感测度是各自主处理变量(treatment.primary)的口径基准, neg_frac_homeprov_full 承接这一惯例, 是本家族在跨论文引用、跨模型稳健性比对(与 neg_frac_nonprov_full/neg_frac_homecity_full 等家族并列列)中被优先援引的版本。使用者若只需单一版本刻画"本地媒体是否更少/更多报道负面消息", 应默认取 full 轨; 三轨并排本身不构成主次关系, 但 full 轨承担了行宇宙锚定的额外角色, 这一点在跨家族对比时须留意。

full 轨的另一实践优势在于覆盖率最完整——由于其文本窗口是全文正文, 不存在类似 ss 轨"银行金科同句缺失即回退"的语义分支, 也不受 ctx 轨实体窗口提取失败(如实体识别边界误差)的潜在噪声影响, 因而 full 轨的负面占比估计在样本量层面通常最稳定, 尤其在本省媒体子样本本身篇数就偏少(分母小)的银行-年格中, 这一稳定性优势更为突出。在与家族 F 内 tone_gap_homeprov_nonprov_full(均值基调地理落差)联合解读时, neg_frac_homeprov_full 提供的是"负面报道浓度"维度的互补证据: 二者若同时显示本省媒体更温和(均值更高、负面占比更低), 则地方媒体偏袒本地银行的证据链条更为完整; 若二者方向不一致(例如均值基调更高但负面占比未见下降), 则提示本地媒体可能只是在正面报道数量上加码而非系统性压制负面信息, 两种情形对应截然不同的媒体行为机制解释。

## VAR: neg_frac_homeprov_ss

【变体差分】
ss 轨: 情感判定依据"标题+银行∧金科同句±N窗"文本(默认 N=1, `config/filtering.yaml::context_window.ss_sentence_radius`), 是三轨中文本粒度最窄的一支, 专门捕捉银行与金科概念在同一句(或相邻句)内共现时的紧邻语境基调。分母口径与 full/ctx 两轨一致, 仍是本省媒体子样本篇数, 不因文本窗口收窄而改变地理归属判定。差分的关键在于回退语义: 若某篇候选文章不存在银行∧金科词在同句(或窗口内)共现, ss 轨严格镜像 ctx 轨的回退规则——退回全文 body 文本参与基调判定, 并置位 `ss_is_fallback=True`, 与 ctx 共享同一 n_articles 分母口径(而非静默剔除或另开分母)。这意味着在金科语境稀薄的银行-年样本中, ss 轨的负面占比可能与 full 轨高度趋同(因大量文章触发回退退到全文), 此时 ss 轨的边际信息量主要来自那些确实存在银行金科同句共现的文章子集。ss 轨与 full/ctx 轨同样遵循互为稳健性、just-identified 并排的家族铁律, 尤其适合在检验"本地媒体负面报道是否集中在金科相关议题"这一更细粒度假说时作为辅助证据, 但不应单独作为识别策略的排他性支柱。

由于回退比例在不同银行-年格中会有系统性差异(金科新闻密度高的年份/银行, 触发同句共现的文章占比更高, 回退比例更低; 反之在金科议题冷门的早期样本年份, 绝大多数文章会回退到全文口径), ss 轨的负面占比估计的信息含量本身随时间/银行异质。使用者在跨期比较 ss 轨结果时应留意这一非平稳的回退比例背景, 必要时可结合 `ss_is_fallback` 指示列的均值作为辅助诊断, 判断某一时期 ss 轨估计是否实质上退化为 full 轨的重复计算; 若回退比例接近 1, ss 轨与 full 轨在数值上高度重合并不构成额外的稳健性证据, 而是应当预期的机械结果。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
