---
family_id: F589
columns:
- tone_nonoff_media_ctx
- tone_nonoff_media_full
- tone_nonoff_media_ss
unit: 语调得分 (连续, 约 [-1,1]; 银行-年聚合均值, 缺组样本时为 NaN)
formula: tone_nonoff_media{track} = mean(llm_vote_score{track} | _is_official==0), groupby [target_bank, year]; _is_official = 1{媒体(中文) ∈ OFFICIAL − MARKET} (NPPA 名单差集); track ∈ {_full, _ctx, _ss}
producer: pipeline\panel\attention_media.py (维度⑤ 官方/非官方情感均值分组聚合); pipeline\panel\export.py (面板列标签装配)
upstream:
- 21_tone_llms.parquet::llm_vote_score_full/_ctx/_ss (三家 LLM 多数投票共识语调分)
- config 媒体名录 (NPPA 主管单位判据 OFFICIAL 名单) 与 MARKET (主办企业判据) 名单差集
citations:
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who Captures the Power of the Pen?"
  venue: "Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "The Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1257/aer.20170947"
  type: journal
  authors: "Qin, B., Strömberg, D., & Wu, Y."
  year: 2018
  title: "Media Bias in China"
  venue: "American Economic Review"
  vol: "108"
  issue: "9"
  pages_or_artno: "2442-2476"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  pages_or_artno: "1150-1172"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J."
  year: 2023
  title: "Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements"
  venue: "The Accounting Review"
  vol: "98"
  issue: "7"
  pages_or_artno: "315-345"
- doi: "10.1016/j.energy.2025.139126"
  type: "journal"
  authors: "Hua, X., Dong, D., Xu, Z., & Huang, W."
  year: 2025
  title: "Official media sentiments toward energy and equity returns: Evidence from China"
  venue: "Energy"
  vol: "340"
  pages_or_artno: "139126"
- doi: "10.1371/journal.pone.0315137"
  type: "journal"
  authors: "Ananyev, M., & Volkova, E."
  year: 2024
  title: "Media ownership and ideological slant: Evidence from Australian newspaper mergers"
  venue: "PLOS ONE"
  vol: "19"
  issue: "12"
  pages_or_artno: "e0315137"
new_dois: []
---

## CORE

【构念与来源】
`tone_nonoff_media` 家族衡量银行-年维度上, 由「非官方媒体」(即不满足 NPPA 主管单位官方判据的报道来源) 所产出的银行相关报道的平均语调, 是本仓库媒体异质性维度⑤ (官方 vs 非官方) 情感分组均值的对照组测度。该维度的政治经济学立论承自 You, Zhang & Zhang (2018, *Review of Financial Studies*) 对"谁掌握了笔杆子的力量"的经典追问: 官方媒体 (党委机关报等) 与市场化/非官方媒体在报道动机、独立性与批判尺度上存在系统性差异, 后者更多受发行量、广告收入与读者关注度驱动, 报道倾向更贴近市场信息需求而非宣传口径; 该分野进一步与 Qin, Strömberg & Wu (2018, *American Economic Review*) 关于中国媒体偏向的制度性证据、以及 You et al. (2018) 本身发现的"媒体笔锋"对公司治理的规训效应相呼应——非官方媒体的负面报道更能触发管理层更替等治理后果, 因为读者与市场对其信息内容的信任度与关注弹性不同于官方喉舌。
本仓库对"官方"判据的操作化并非直接照搬 You et al. (2018) 或 NPPA 名录的字面口径, 而是经过一次结构性修正 (fix omni-g-attention-02, 2026-06-11 记录于 `attention_media.py` 源码注释): NPPA 数据库中「主管单位为党政机关」的 OFFICIAL 判据集 (约 2,208 家, 覆盖率近全集) 与「主办单位为企业/商业集团」的 MARKET 判据集 (约 471 家) 存在 386 家的交叉重叠——这些媒体主管单位是党政机关但主办单位是企业, 若直接用 OFFICIAL 原始并集划分官方组, 会把大量实际市场化经营的媒体错误计入官方组, 导致 `official_media_frac` 均值高达 0.873 的近退化现象, 且掩盖了 You, Zhang & Zhang (2018) 意在刻画的官方/市场对立构念。修正后的操作化定义为纯官方 `official := OFF − MARKET` 与纯市场化 `market := MKT − OFF` 两个互斥集合 (`official_frac + market_frac ≤ 1`, 该不等式作为源码内建校验); 本家族 `tone_nonoff_media` 的对照组 (`_is_official == 0`) 因此是"OFF − MARKET 差集之外的全部媒体", 即包含全部市场化媒体、也包含既非官方主管又非企业主办的中间地带媒体 (如事业单位主办、行业协会主办等)。双判据媒体 (OFF∩MKT, 主管党政但主办企业) 依此定义规则不计入官方处理组, 而是落入 `tone_nonoff_media` 与 `tone_nonmkt_media` 两个对照组——这是一处需要在论文层显式披露的操作化细节 (主管 vs 主办双判据非互斥, 交集样本双重计入对照组而非被剔除或单列)。
【方法学与计算】
计算管线分两步: 第一步在文章级数据上打官方/非官方标签, `df['_is_official'] = df['媒体(中文)'].isin(OFFICIAL - MARKET).astype(int)`, 该标签基于报道来源媒体名称本身的机构属性, 与报道内容语调无关, 是外生分组变量; 第二步在银行-年层面对 `_is_official == 0` 的子样本分组求 `llm_vote_score{track}` 均值, `llm_vote_score{track}` 是三家大模型 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票产生的逐篇语调共识分 (P1 主线情感测度, 与词典/BERT 两条平行测度并行、互不混用), 三家投票的方法学细节与「LLM 三家互为稳健性、不分主次」的铁律见仓库情感测度总纲, 本家族不重复该分组内部机制, 只消费其产出的 `llm_vote_score{track}` 作为待聚合的因变量。分组聚合以 `groupby(['target_bank', 'year'])[src].mean()` 实现, 再以 left merge 拼回面板; 若某银行-年组合下非官方媒体报道篇数为零, 该单元格聚合结果为 NaN (无隐式填零, 保留真实缺失以避免虚假精度)。语调分本身的取值区间约在 [-1, 1] (负面到正面), 银行-年聚合均值继承该区间但因均值收缩效应实际分布更集中。三轨 (`_full`/`_ctx`/`_ss`) 均从各自的 `llm_vote_score{track}` 独立聚合而来, 采用统一的 `for track in ['_full','_ctx','_ss']: src = f'llm_vote_score{track}'; if src not in df.columns: continue` 优雅跳过模式——若某轨源列缺席 (例如上游三轨物化未完整覆盖), 该轨的 `tone_nonoff_media{track}` 及其配对的 `tone_gap_official_nonoff{track}` 缺口列一并不产出, 而非以其他轨回填, 保证轨间不发生隐性借用。
本家族与同一维度⑤下的 `tone_official_media{track}` (官方组镜像) 及 `tone_gap_official_nonoff{track}` (官方减非官方缺口, 属另一独立 family) 共享同一 `_is_official` 分组变量与同一批源数据, 三者在概念上构成一个完整的分组-对照-缺口三元组, 但本 family 仅覆盖对照组 (非官方) 均值本身。按仓库口径, 三轨 full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 型识别设定——full 轨是标题+正文全文语调, ctx 轨是标题+银行实体窗口语调, ss 轨是标题+银行∧金科同句±N 窗口语调 (无该同句共现时回退为全文 body, 并以 `ss_is_fallback=True` 标记, 语义上镜像 ctx 轨的回退逻辑, 共享 `n_articles` 分母)。留篇门控 (即"是否判定为一篇银行金科报道") 统一以 full 轨 `llm_verified_full == True` 为准 (2026-06-29 起 full-only 门控铁律), ctx/ss 两轨的 `tone_nonoff_media` 在此意义上是 full 轨留篇集合下的条件测度/稳健性轨, 其行宇宙是 full 轨留篇集的子集, 每轨各自独立完成分组聚合计算。
【文献定位】
除 You, Zhang & Zhang (2018, *Review of Financial Studies*) 提供的官方/市场化媒体二元对立核心构念外, 本家族的分组聚合方法论与媒体语调作为银行信息中介渠道的立论, 同样借鉴 Tetlock (2007, *Journal of Finance*) 首创的"给投资者情绪以内容"的文本情感度量框架——该文将媒体语调作为可观测的市场信息补充变量、并证实其对股价的可预测影响, 是本仓库整条媒体语调聚合管线的方法论源头。中国语境下的银行业媒体情感应用可参照 Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 对媒体情感与银行系统性风险、存款稳定性关系的实证, 该文与本仓库同为中国银行-年层面的媒体情感测度, 在样本构造与识别策略上具有直接可比性。媒体权威性与来源异质性的分组处理思路亦部分呼应 Holzman, Miller & Twedt (2023, *The Accounting Review*) 对媒体情感在盈余公告披露中约束作用的研究, 该文强调不同媒体来源的信息权威度差异应被显式建模而非笼统平均, 与本仓库将官方/非官方媒体拆分为独立子样本聚合的处理思路一致。 近期同域证据方面, Hua、Dong、Xu 与 Huang (2025) 以 BERT 对中国官方/政府控制媒体的新能源报道文本构建官方媒体语调指数, 并检验其与权益回报及企业融资投资行为的关系, 表明"按媒体官方属性切出子样本、在子样本内对文章级语调取均值"这一构造在前沿文献中已被独立采用, 与本家族按 _is_official 判据分组聚合的动作同构; 惟须诚实标明该文只构建官方一侧的指数、并未度量非官方补集这一侧, 其官方名单依中国国家控股报纸清单而非本家族 NPPA 主管/主办单位判据下的 OFFICIAL−MARKET 差集, 情感由文本指数法而非三家 LLM 投票得到, 层级为行业-日频而无 bank-year 面板, 故仅锚"按官方属性分组取均值"这一环, 其非官方侧的对称构造仍属本项目的补集推广。Ananyev 与 Volkova (2024) 利用 2016-2019 年三起澳大利亚报业并购、以逾三千万篇报道的语言构建 slant 测度, 并以合成双重差分识别媒体所有权变更对报纸政治 slant 的因果影响, 为本家族"媒体归属/控制权系统性决定报道倾向、因而非官方子样本的语调须独立聚合而非与官方样本笼统平均"这一前提提供了准实验层面的证据; 其所有权维度为私人资本集中度而非中国的官方/市场化主管主办单位, slant 以政治意识形态量表度量而非本家族的银行-金科报道语调, 层级为报纸-时期而无主体-年面板, 故只锚分层前提, 不锚本列的具体公式。本家族三条文本轨道下的列与官方一侧的对应列互为稳健性、不分主次, 各自 just-identified 并排使用, 不应被并入同一 over-identified 的 Hansen J 矩条件。
## VAR: tone_nonoff_media_full

【变体差分】
`_full` 后缀标识该列的语调分来源于 full 轨, 即聚合对象为 `llm_vote_score_full`——三家 LLM 基于「标题 + 正文全文」文本对每篇非官方媒体报道所作出的多数投票语调共识分。full 轨是本仓库留篇门控的唯一判据轨: 一篇文章是否被计入"银行金科报道"样本, 完全由该文章在 full 轨上的 `llm_verified_full == True` 决定, 与 ctx/ss 两轨的判定结果无关; 因此本列的分母 (参与 `_is_official==0` 分组求均值的文章集合) 是三轨中口径最宽、覆盖面最完整的一支, 直接对应全文语境下模型能观察到的全部上下文信息 (包括可能与银行、金科皆不直接相关的段落), 而非仅聚焦于银行实体窗口或银行-金科同句共现片段。作为家族内 canonical 轨, `_full` 与 `_ctx`、`_ss` 两个变体各自 just-identified 并排, 三者互为稳健性检验、不存在主次之分, 三者绝不应混入同一个 over-identified 的 Hansen J 型识别设定中联合估计。在实证应用上, full 轨通常作为多数 paper module 的处理变量主口径 (镜像 P1 `llm_vote_tone_full` 作主线处理变量的先例), 本列继承该地位, 是 `tone_nonoff_media` 三轨中信息量最完整但也最可能夹杂非银行-金科核心语境噪声的一支。由于留篇门控恒以本轨判定, `tone_nonoff_media_full` 的样本量在三轨中最大, 与 `tone_official_media_full`、`tone_gap_official_nonoff_full` 共用同一 full 轨留篇集合, 三者可在同一张表内并列呈现而不必担心行宇宙不一致, 是研究者比较官方与非官方媒体语调差异时的默认起点。

## VAR: tone_nonoff_media_ctx

【变体差分】
`_ctx` 后缀标识该列的语调分来源于 ctx 轨, 即聚合对象为 `llm_vote_score_ctx`——三家 LLM 基于「标题 + 目标银行实体窗口」文本 (而非全文) 所作出的多数投票语调共识分。该文本窗口在 stage 14 (`ctx_materializer`) 物化, 围绕目标银行实体截取局部上下文, 目的是让语调判定更聚焦于与目标银行直接相关的表述, 剔除全文中与该银行无关段落对语调判断的稀释或污染。行宇宙上, ctx 轨在 2026-06-29 起的 full-only 门控铁律下降级为"条件于 full 轨留篇集合"的测度: 一篇文章是否计入分组聚合, 仍由该文章 full 轨的 `llm_verified_full` 决定, ctx 轨本身不参与是否留篇的判定, 只在留篇集合内部提供一个基于局部实体窗口而非全文的独立语调估计, 与 full 轨互为稳健性并排、不分主次。若某银行-年组合下 `llm_vote_score_ctx` 列本身因上游缺失而不存在, 该行的分组聚合按源码 `if src not in df.columns: continue` 逻辑整体跳过, 不产出该轨列, 不借用 full 轨结果填补, 亦不产出对应的 `tone_gap_official_nonoff_ctx`。ctx 轨与 ss 轨的核心区别在于窗口构造粒度: ctx 是"围绕银行实体"的窗口, 未强制要求金科词与银行词同句共现, 因此覆盖面通常宽于 ss 轨。当研究者关心"聚焦银行本身而非泛泛全文"的语调稳健性时, `tone_nonoff_media_ctx` 是三轨中兼顾聚焦度与样本量的折中选择, 常与 `tone_nonoff_media_full` 并列汇报以展示结论对文本窗口收窄的敏感度。

## VAR: tone_nonoff_media_ss

【变体差分】
`_ss` 后缀标识该列的语调分来源于 ss 轨, 即聚合对象为 `llm_vote_score_ss`——三家 LLM 基于「标题 + 银行∧金科同句 (±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1)」文本所作出的多数投票语调共识分, 是三轨中语境窗口最窄、判定条件最严格的一支, 专门刻画"银行与金融科技同一句子内共同出现"这一强共现情形下的报道语调。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章在全文范围内不存在银行与金科词的同句共现, 则该篇的 `content_ss` 回退为全文 body (与 `content_full` 等价), 并以 `ss_is_fallback = True` 标记, 该回退分支与非回退分支共享同一个 `n_articles` 分母, 不做区分统计; 若 `FINTECH_AC` (金科词自动机) 为 None (未配置或加载失败), 则全部文章的 `*_is_fallback` 置 True, 属优雅降级而非崩溃。与 ctx 轨相同, ss 轨在 full-only 门控铁律下同为"条件于 full 轨留篇集合"的稳健性/条件测度轨, 是否留篇仍完全由该文章 full 轨的 `llm_verified_full` 判定, ss 轨本身的存在与否不影响留篇判定, 也不借用 full 轨结果回填缺失。ss 轨与 ctx 轨、full 轨三者各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 型识别设定联合使用; 当研究者希望以最严格的"银行-金科强共现语境"来检验非官方媒体语调结论的稳健性时, `tone_nonoff_media_ss` 是三轨中最贴合该目的的取值, 但代价是有效样本量通常小于 ctx 与 full 两轨, 且回退比例 (fallback 占比) 需要在稳健性讨论中一并披露。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Qin, B., Strömberg, D., & Wu, Y. (2018). Media Bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Hua, X., Dong, D., Xu, Z., & Huang, W. (2025). Official media sentiments toward energy and equity returns: Evidence from China. Energy, 340, 139126. https://doi.org/10.1016/j.energy.2025.139126
Ananyev, M., & Volkova, E. (2024). Media ownership and ideological slant: Evidence from Australian newspaper mergers. PLOS ONE, 19(12), e0315137. https://doi.org/10.1371/journal.pone.0315137
<!-- rendered-citations:end -->
