---
family_id: F579
columns:
- tone_gap_official_nonoff_ctx
- tone_gap_official_nonoff_full
- tone_gap_official_nonoff_ss
unit: 语调缺口 (连续, 两侧均值之差, 理论域约 [-2,2], 实践中集中于 [-1,1]; bank-year 面板层)
formula: 'tone_gap_official_nonoff{track} = mean(llm_vote_score{track} | _is_official=1) - mean(llm_vote_score{track} | _is_official=0), 逐 (target_bank, year) 分组计算, track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\attention_media.py (维度⑤ 官方 vs 非官方 情感缺口, tone_gap_official_nonoff{track} 构造块); pipeline\panel\export.py (面板列标签映射, 不改变数值)
upstream:
- llm_vote_score_full
- llm_vote_score_ctx
- llm_vote_score_ss
- 媒体(中文)
- OFFICIAL (NPPA 主管单位=党政机关 名单)
- MARKET (市场化媒体名单)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political Incentives to Suppress Negative Information: Evidence from Chinese Listed Firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: Does Official Media Sentiment Matter for the Stock Market? Evidence from China
  venue: Emerging Markets Review
  vol: '64'
  pages_or_artno: '101234'
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: Is the Tone of the Government-Controlled Media Valuable for Capital Market? Evidence from China's New Energy Industry
  venue: Energy Policy
  vol: '184'
  pages_or_artno: '113917'
new_dois: []
---

## CORE

【构念与来源】
tone_gap_official_nonoff 家族刻画同一银行同一年度内, 官方媒体 (党政机关主管) 与非官方媒体 (含全部市场化媒体) 在报道语调上的系统性落差, 是 attention_media 模块"媒体异质性"六维度中第⑤维的产出。其理论前提是中国媒体存在双重属性谱系: 一端是接受党政机关直接主管、承担舆论引导职能的官方媒体, 另一端是依赖发行和广告收入、面向市场竞争的市场化媒体; 二者在报道对象、议程设置和语调选择上存在系统性差异, 这一差异已被 You, Zhang & Zhang (2018) 记录并证明具有真实治理后果——官方媒体的负面报道不能显著预测高管更替, 而市场化媒体的负面报道能。tone_gap_official_nonoff 把这一构念从"媒体身份分类"进一步落到"语调水平差异"这一连续量度上, 是对同一构念(官方/市场化媒体的系统性报道倾向差异)的语调维度延伸测度。
本列族的分组判据 _is_official 定义为 OFFICIAL 减去 MARKET 的差集(即 official := OFF − MKT), 而非简单的 OFF 名单二分。这是 2026-06-11 (fix omni-g-attention-02) 的一次口径修正: 早期版本直接用 NPPA 的 OFF 判据 (2,208 家, 覆盖近全量媒体来源) 做官方组标签, 但 OFF 与市场化名单 MKT (471 家) 存在 386 家的重叠 (企业主办但主管单位挂靠党政机关的媒体), 导致旧口径下 official_media_frac 的均值高达 0.873, 近乎退化为常数, 且 nonoff 对照组反而系统性剔除了大部分真正市场化的媒体, 使官方/非官方的语调对比失去区分力。修正后的互斥构造把 OFF∩MKT 的双判据媒体 (主管为党政机关且主办为企业) 排除出官方组, 该批媒体连同纯市场化媒体一起落入 nonoff 对照组, 因此 nonoff 现在包含"全部市场化媒体"。此构造与维度⑥ market := MKT − OFF (市场化组同样排除双判据媒体, 落入 nonmkt) 是结构性互斥的镜像操作化, 满足 official_frac + market_frac ≤ 1 的校验约束。需要向论文读者披露的一点是: 该操作化采用"主管单位 vs 主办单位"两个非互斥的判据轴, 与 You, Zhang & Zhang (2018) 原始设计中"党委机关报 vs 市场化报"这一互斥窄集构念并不完全对齐——本测度是在 NPPA 数据库约束下对该经典构念的最接近映射, 论文正文应重述这一操作化差异, 而非直接等同于原文分类。
【方法学与计算】
计算分两步: 第一步是分组语调均值。对每个 (target_bank, year) 单元, 分别在官方媒体子样本 (_is_official=1) 与非官方媒体子样本 (_is_official=0) 上, 取文章级语调分 llm_vote_score{track} 的算术均值, 得到 tone_official_media{track} 与 tone_nonoff_media{track} 两个分组均值列。第二步是相减取差: tone_gap_official_nonoff{track} = tone_official_media{track} − tone_nonoff_media{track}, 正值表示该银行当年官方媒体报道语调更正面, 负值表示官方媒体语调更负面(相对非官方组)。两组均值列均以 how='left' 合并回主面板, 当某侧子样本在该 (银行, 年) 单元内为空 (例如该年该银行完全未被官方媒体报道)时, 对应分组均值为 NaN, 相减结果随之传播为 NaN, 不做隐式填零, 避免把"无报道"误判为"零语调"。
底层语调来源 llm_vote_score{track} 是三家大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 多数投票共识分数(与三家各自的 per-model 子测度互为稳健性, 不分主次), 门控口径遵循 2026-06-29 起生效的 full-only 规则: 一篇文章是否计入"银行金科报道"留篇集合, 只看 llm_verified_full 是否为真; full 轨的行宇宙是留篇集合本身, ctx/ss 轨则是该留篇集合的 conditional-on-full 子集测度, 各轨在自身留篇子集内独立分组求均值。
三轨 full/ctx/ss 分别对应标题+正文全文、标题+实体窗口、标题+银行∧金科同句±N窗三种文本口径, 在源码中以 `for track in ['_full', '_ctx', '_ss']: src = f'llm_vote_score{track}'; if src not in df.columns: continue` 的方式逐轨独立处理——任一轨的语调来源列缺失时该轨优雅跳过, 不影响其余轨的产出, 不做跨轨借补。_ss 轨的回退语义镜像 _ctx: 当一篇文章不存在银行与金科关键词的同句共现时, 其 content_ss 退化为使用全文 body(ss_is_fallback=True), 该回退共享 n_articles 分母, 不做单独剔除。三轨在语调缺口这一构念上各自 just-identified 并排, 互为稳健性、不分主次, 严禁在同一 over-identified 的 Hansen J 检验中混用三轨的仪器/矩条件。
本家族属"媒体异质性"六维度体系的一支, 与同一模块产出的中央/地方缺口 (tone_gap_central_local)、市场化/非市场化缺口 (tone_gap_market_nonmkt)、深度报道/非深度报道缺口 (tone_gap_deepdive_nondeep)、日频/非日频缺口 (tone_gap_daily_nondaily) 共享同一构造范式(分组均值相减), 但分组判据各不相同——本家族的判据轴是"媒体主管单位性质"(党政机关 vs 非党政机关主管), 是六维度中唯一直接映射政治控制强度的一支。
【文献定位】
本测度的构念根基是 You, Zhang & Zhang (2018, The Review of Financial Studies) "Who Captures the Power of the Pen?" 一文——该文首次系统证明中国官方媒体与市场化媒体在负面报道的公司治理效应上存在显著差异: 官方媒体的负面报道未能显著预测高管更替, 而市场化媒体的负面报道具有显著的公司治理纠偏效应, 这一发现是本家族"官方/非官方语调是否存在系统性差异"这一命题的直接理论来源与实证先例。分组判据的操作化进一步参照 Piotroski, Wong & Zhang (2015, Journal of Accounting Research) 对政治激励如何压制关联企业负面信息传播的分析框架, 该文提供了"主管单位性质影响信息披露倾向性"这一机制层面的支持证据。就测度语调差异这一统计操作本身, Xu, Hua & Zhang (2025, Emerging Markets Review) 在讨论官方媒体情感对中国股票市场的影响时同样采用了分组语调对比的构造方式, 是本家族在近期文献中的方法论呼应; Xu, Li, Hua & Ren (2024, Energy Policy) 则在新能源行业情境下验证了政府控制媒体语调对资本市场的独立信息含量, 二者共同支持"官方 vs 非官方语调缺口"是具有可操作性、可复制性的实证测度而非本项目特设构造。就语调底层来源本身的可靠性, Holzman, Miller & Twedt (2023, The Accounting Review) 在媒体权威性加权情境下验证了媒体情感测度对盈余公告后市场反应的解释力, 为本家族所依赖的 llm_vote_score 基础语调分提供了外部效度佐证。

## VAR: tone_gap_official_nonoff_full

【变体差分】
本列为家族 canonical 轨, 分组均值差的两侧输入均取 llm_vote_score_full——即标题+正文全文口径下的三家 LLM 多数投票语调分。该轨的行宇宙即为留篇门控 (llm_verified_full==True) 直接定义的银行金科报道集合本身, 不存在"以 full 为门控、以其它轨为条件测度"的二次筛选, 是本家族在样本覆盖度上最完整的一轨。全文口径纳入了文章中除标题实体窗口和金科银行同句片段之外的全部正文信息, 因而对语调的刻画最不依赖局部句法窗口的选取, 但也因此更容易受与目标银行、金科话题无关的段落语调"稀释"或"污染"。作为主轨, tone_gap_official_nonoff_full 是本家族在下游 stata_export/panel 汇总列标签(Tone Gap: Official-NonOff (Full))中列于首位的版本, 但与 ctx/ss 两轨在识别策略上完全并排、互为稳健性, 不构成孰主孰次的层级关系。
在分组构造上, tone_gap_official_nonoff_full 与家族同源的三轨一样, 依赖 _is_official 这一互斥判据(official := OFF − MKT); 由于 full 轨覆盖的文章样本量在三轨中最大(不受实体窗口或同句共现能否成功抽取的限制), 该轨下官方组与非官方组各自的样本容量通常也最充分, 分组均值的抽样噪声相对更小, 这是它在实践中常被优先呈现的原因之一, 但这只是样本效度上的优势, 不构成识别策略上的优先级。当某银行某年官方媒体或非官方媒体任一侧在 full 轨下完全无报道时, 对应分组均值为缺失, tone_gap_official_nonoff_full 随之缺失, 不做隐式插补。

## VAR: tone_gap_official_nonoff_ctx

【变体差分】
本列的分组均值差两侧输入取 llm_vote_score_ctx, 即标题+实体窗口口径下的语调分——文本范围收窄到目标银行实体附近的局部窗口, 而非整篇正文。该窗口化处理的动机是降低"文章中与银行无关段落语调"对整体语调判断的稀释效应, 使语调测度更贴近"文章对该银行本身的评价倾向", 而非文章的整体基调。ctx 轨的行宇宙是 full 轨留篇集合的 conditional-on-full 子集(该文章仍须先通过 llm_verified_full 门控才纳入 ctx 轨分组), 若某篇文章缺少 llm_vote_score_ctx 列(即该文章未能构造出有效实体窗口), 则该文章在 ctx 轨的分组均值计算中被跳过, 不借用 full 轨数值填补, 也不影响 full/ss 两轨各自独立的均值计算。ctx 轨与 full、ss 两轨在本构念下互为稳健性并排, 不分主次, 三轨严禁混入同一 over-identified 的 Hansen J 矩条件。
需要注意 ctx 轨与 full 轨在样本宇宙上的关系是包含而非独立: 一篇文章只要通过 llm_verified_full 门控即已纳入留篇集合, 但该文章是否在 ctx 轨的分组均值中贡献一个观测, 还取决于其是否成功抽取出围绕目标银行实体的窗口文本并产出 llm_vote_score_ctx。因此 ctx 轨的官方组/非官方组样本量在理论上不超过 full 轨对应组的样本量, 二者之差即为"通过留篇门控但未能构造有效实体窗口"的文章数。这一结构性子集关系是三轨"conditional-on-full"设计的直接体现, 也是解读 tone_gap_official_nonoff_ctx 与 tone_gap_official_nonoff_full 数值差异时应优先排查的机械性成因, 而非默认将差异解释为"局部窗口语调与全文语调存在实质性分歧"。

## VAR: tone_gap_official_nonoff_ss

【变体差分】
本列的分组均值差两侧输入取 llm_vote_score_ss, 即标题+"银行∧金科关键词同句"窗口(±N 句半径, 默认 N=1, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制)口径下的语调分, 是三轨中文本范围最窄、构念最贴近"该句是否同时谈及银行与金融科技"的一轨。当一篇文章中银行与金科关键词从未出现在同一句(或半径窗口内)时, 该文章的 content_ss 按镜像 ctx 的回退语义退化为使用全文 body, 并置 ss_is_fallback=True 标记该行是回退产物, 该类回退行仍计入 n_articles 分母(与 ctx 回退共享同一分母口径), 不做单独剔除或重新加权。ss 轨同样是 full 轨留篇集合上的 conditional-on-full 测度, llm_vote_score_ss 列缺失的文章在该轨分组均值计算中被跳过, 不做跨轨借补。ss 轨与 full、ctx 两轨在本构念下互为稳健性并排, 不分主次, 三轨严禁混入同一 over-identified 的 Hansen J 矩条件; 需要特别注意的是, ss 轨判据(银行∧金科同句共现)与 stage 13 硬过滤所用的共现半径判据是两个不同的配置键(`filtering.yaml::context_window.ss_sentence_radius` vs `cooccurrence_filter.sentence_radius`), 二者数值即便相同也不应被视为同一处口径设定。
与 ctx 轨类似, ss 轨的官方组/非官方组样本量在理论上不超过 full 轨对应组样本量, 缺口来自两部分: 一是文章通过留篇门控但未能产出 llm_vote_score_ss(极少见, 因回退机制已保证绝大多数情形下该列有值); 二是回退产生的观测虽然计入分母但其底层文本已退化为全文, 使得该文章在 ss 轨的语调贡献在信息内容上趋近于 full 轨而非严格意义上的"同句窗口"语调。解读 tone_gap_official_nonoff_ss 时应留意, 当某银行某年该银行∧金科关键词的同句共现比例很低(即回退比例高)时, ss 轨与 full 轨的数值会天然趋同, 这属于回退机制的预期行为, 不应被误读为"同句窗口未能捕捉到额外信息"。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political Incentives to Suppress Negative Information: Evidence from Chinese Listed Firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Xu, Z., Hua, X., & Zhang, T. (2025). Does Official Media Sentiment Matter for the Stock Market? Evidence from China. Emerging Markets Review, 64, 101234. https://doi.org/10.1016/j.ememar.2024.101234
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the Tone of the Government-Controlled Media Valuable for Capital Market? Evidence from China's New Energy Industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
<!-- rendered-citations:end -->
