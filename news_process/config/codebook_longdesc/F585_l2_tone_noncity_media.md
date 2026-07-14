---
family_id: F585
columns:
- tone_noncity_media_ctx
- tone_noncity_media_full
- tone_noncity_media_ss
unit: 语调得分 (连续, 约 [-1,1]; 逐年按银行加总为 bank-year 均值)
formula: 'tone_noncity_media_{trk} = 该银行-年 by 非属地媒体 (报道来源城市≠银行注册地/总部所在城市, 市级颗粒度 _is_homecity, 与省级并行的 homeprov/nonprov 层级不同) 发出的报道子集上, 逐篇语调 llm_vote_score{trk} 的算术均值; 若该银行-年不存在任何非属地来源报道, 该格记为缺失 (非 0)。'
producer: pipeline\panel\attention_media.py
upstream:
- 21_tone_llms.parquet
- 11_news_bank.parquet
- config/bank_addresses.json
citations:
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What drives media slant? Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: Media bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving content to investor sentiment; The role of media in the stock market
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: The media and the diffusion of information in financial markets; Evidence from newspaper strikes
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: Media sentiment, deposit stability and bank systemic risk; Evidence from China
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"非属地媒体"对目标银行报道的平均语调, 属于地理邻近性维度下与 tone_homecity_media 严格互补的对照组测度。地理邻近性这条测度线的出发点是: 媒体机构的报道立场并非中性传声筒, 而系统性地受到属地关系影响——总部或注册地所在城市/省份的本地媒体, 因存在广告依赖、监管接触、地方政府关系乃至读者利益认同等多重渠道, 更可能对本地企业产生"护航"式的正面偏向; 反之, 非本地(跨省或跨市)媒体缺乏这种利益纠葛, 更可能保持独立立场乃至体现出竞争性负面报道倾向。Gentzkow & Shapiro (2010, Econometrica) 的经典发现是报纸的政治与商业立场高度稳定并系统性响应其读者群体构成, 为"媒体来源身份→报道倾向"这条因果链提供了方法论基础; You, Zhang & Zhang (2018, The Review of Financial Studies) 进一步在中国资本市场语境下证明媒体的监督/合谋角色高度依赖其与被报道对象的地理及政治距离, 是 tone_homecity/tone_noncity 这对构念在中国制度背景下最直接的文献锚点。tone_noncity_media 与其孪生列 tone_homecity_media、以及差值列 tone_gap_homecity_noncity 共同构成一组三元对照测度: 非属地语调本身是"外部独立观察者"视角下银行声誉的代理变量, 差值列则是"属地偏向"程度的直接量化。

【方法学与计算】
计算口径分三步。第一步, 在文章级面板 (11_news_bank.parquet 提供的银行匹配结果 + 21_tone_llms.parquet 提供的逐篇语调) 上, 依据报道来源媒体的注册省份/城市与目标银行总部所在省份/城市 (取自 config/bank_addresses.json 银行地理字典, 逐银行给出 province/city 字段) 做二分类划分: 凡来源城市 ≠ 银行总部城市的报道 (标记列 _is_homecity=0) 计入"非属地"(noncity) 子集, 其余 (_is_homecity=1) 计入"属地"(homecity) 子集; 该划分与省级维度的 homeprov/nonprov (标记列 _is_homeprov) 是并行的两级地理颗粒度, 城市层级更细, 二者不可混用互代。第二步, 在非属地子集内部, 逐篇语调取文章级列 llm_vote_score (三家 LLM——gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash——多数投票共识, 与嵌入模型无关, 取值 {-1,0,1}), 该值继承 stage 21 的留篇门控: 只有 llm_verified_full == True 的篇目才计入分母与分子 (full-only 门控, 2026-06-29 起生效); 注意 llm_vote_score 是文章级逐篇量, 与同名衍生的面板级列 llm_vote_tone (由文章级 llm_vote_score 按银行-年 groupby 均值聚合得到) 是两个不同层级的对象, 本家族的聚合输入是前者而非后者。第三步, 按银行-年对非属地子集内的语调取算术均值, 得到 tone_noncity_media 本列; 若某银行-年不存在任何非属地来源的合格报道(例如样本期内该行只被本地媒体报道过), 该格记为缺失而非 0, 避免把"无观测"误读为"零语调"。
本家族严格遵循全项目三轨口径: _full/_ctx/_ss 三个后缀分别对应标题+正文全文、标题+实体窗口、标题+银行∧金科同句±N窗三种文本物化方式(物化于 stage 14 ctx_materializer), 三者的语调输入 llm_vote_score{trk} 各自独立计算, 而地理筛选(是否属地)这一步骤本身与文本轨道选择正交、不因轨道而变。_ss 轨在回退语义上镜像 _ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 退化为全文 body 且 ss_is_fallback 标记为 True, 该规则同样适用于本家族的非属地子集聚合(降级篇目仍计入分母, 但其"同句窗口"语义已退化为全文语义, 解读时须留意)。三轨测度之间是并排的互为稳健性关系, 不分主次, 严禁将三轨语调同时纳入同一个 over-identified 的 Hansen J 检验框架——三者应各自独立进入 just-identified 设定, 分别报告结果作为交叉验证, 而非当作可自由替换的工具变量集合共同使用。

【文献定位】
本家族测度的理论谱系上承 Tetlock (2007, The Journal of Finance) 与 Peress (2014, The Journal of Finance) 关于媒体语调作为投资者情绪代理及信息扩散渠道的奠基性证据, 中间经由 Gentzkow & Shapiro (2010) 关于媒体立场系统性受读者/利益关系驱动的机制性发现, 落地到 Qin, Strömberg & Wu (2018, American Economic Review) 对中国媒体系统性偏向(尤其是官方/地方媒体的正面选择性报道)的直接刻画, 以及 You, Zhang & Zhang (2018, The Review of Financial Studies) 对中国资本市场情境下媒体地理/政治距离如何影响其监督角色的实证检验。银行业情境下, Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 进一步证明媒体情绪对中国银行系统性风险及存款稳定性具有可观测的因果传导, 佐证了本家族"用非属地语调作为外部独立信号"这一构念选择的经济含义——非属地媒体报道更贴近"无利益冲突的第三方评价", 因而在解释存款人/投资者反应时理应具有比属地报道更强的信息含量, 而 tone_gap_homecity_noncity 则可用于检验属地媒体是否存在系统性"护航"偏差, 是银行声誉治理与地方保护主义研究的直接切入点。

## VAR: tone_noncity_media_ctx

【变体差分】
本列使用 _ctx 轨文本(标题+实体窗口物化文本 content_ctx, stage 14 ctx_materializer 产出)计算的逐篇语调 llm_vote_score_ctx 作为聚合输入, 其余步骤(非属地地理筛选、full-only 留篇门控、银行-年算术均值)与家族 canonical 口径完全一致。_ctx 轨相对 _full 轨的关键差异在于所消费的原始文本范围更窄: 只截取标题与目标实体(银行名称)周边的上下文窗口而非全文, 目的是在文章可能夹杂多主体、多话题的情形下降低无关段落对语调判定的稀释或污染。因此 tone_noncity_media_ctx 度量的是"聚焦银行实体局部语境"下非属地媒体给出的语调评价, 与 tone_noncity_media_full 所度量的"通篇整体语境"语调理论上应高度正相关但不必然逐篇一致——尤其当一篇报道整体基调正面但涉及目标银行的具体段落偏负面(或反之)时, 两轨会产生分歧, 这正是三轨并排设计要捕捉的稳健性信息, 而非测量误差。需要强调的是, 本列与 _full/_ss 两个孪生列处于同一 just-identified 并排关系, 三者互为稳健性检验、不分主次, 分析时应分别报告而不应混入同一个 over-identified 工具变量集合(即不可把三轨语调同时作为同一 Hansen J 检验中的多重工具)。地理筛选逻辑(是否属地、城市颗粒度)与文本轨道选择相互正交, _ctx 轨的引入不改变非属地判定本身, 只改变判定之后语调值的计算依据; 留篇门控本身仍以 full-only 口径为准(llm_verified_full == True 才计入), _ctx 轨不单独设门控, 即该列的行样本宇宙是 full 留篇集的子集, 在此子集上按 _ctx 轨文本重新计算语调并聚合, 而非另起炉灶的独立样本框架, 这一点是理解三轨并排结构、避免误将三轨当作三套独立样本的关键。

## VAR: tone_noncity_media_full

【变体差分】
本列是本家族的 canonical/主口径变体, 使用 _full 轨文本(标题+正文全文, prepend_title 拼接后的完整篇章)计算的逐篇语调 llm_vote_score_full 作为聚合输入。留篇门控直接以本轨为准: stage 21 是否判定"一篇银行金科报道"合格只看 llm_verified_full == True(2026-06-29 起的 full-only 门控铁律), 因此 _full 轨不仅是测度口径之一, 更是决定整个三轨行样本宇宙的锚点——_ctx 与 _ss 两个变体的样本行集合均是本列所依赖的 full 留篇集的子集, 在该子集上分别切换文本轨道重算语调。就语调本身的经济含义而言, _full 轨捕捉的是记者/编辑对该篇报道整体基调的把握, 涵盖标题、导语、正文论述逻辑与结论倾向等全部文本信息, 相较 _ctx/_ss 两轨更贴近读者(包括存款人、投资者、监管者)阅读完整篇章后形成的总体印象, 因而在多数 paper 模块(如 P1 bank_fintech_tone)中被设为处理变量的主轨。地理筛选步骤同样在本列适用: 仅纳入来源城市与银行总部城市不一致的报道子集, 按银行-年取算术均值, 无非属地合格报道的银行-年记为缺失。本列与 _ctx/_ss 两个孪生列构成并排的互为稳健性关系而非层级关系——"canonical" 仅指其在样本宇宙构造与门控锚定上的特殊角色, 不代表其数值优先级或统计意义上高于另外两轨; 三者仍须各自 just-identified 独立进入回归设定, 严禁混入同一个 over-identified Hansen J 检验中共同充当工具变量。

## VAR: tone_noncity_media_ss

【变体差分】
本列使用 _ss 轨文本(标题+银行∧金科同句共现窗口, 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认±1句)计算的逐篇语调 llm_vote_score_ss 作为聚合输入, 是三轨中对文本范围要求最严格的一支——只截取银行实体与金科词汇在同一句(及邻近半径内)共同出现的局部片段作为语调判定依据。该轨的回退语义严格镜像 _ctx 轨: 当某篇报道中不存在银行∧金科同句共现关系时, content_ss 退化为全文 body、ss_is_fallback 标记为 True, 此时该篇在 _ss 轨下计算出的语调实质上等同于全文语调, 与真正"同句窗口"语义下产生的语调存在系统性差异, 分析或解读边际效应时需要意识到降级样本占比可能随语料的银行∧金科共现密度而变化。地理筛选(是否属地)与留篇门控(以 full 轨 llm_verified_full 为准)两个环节与另外两轨完全一致, 本列同样只在 full 留篇集的子集上、按非属地来源、逐银行-年取语调算术均值。相较 _ctx 轨的"实体周边窗口", _ss 轨进一步收紧到"银行与金科词汇同句共现"这一更严格的判据, 理论动机是: 只有当一篇报道真正在同一叙述单元中把银行与金融科技话题绑定讨论时, 该处语调才最直接地反映"该银行在金科议题上的媒体评价", 而非泛泛的银行整体报道语调被金科话题稀释或污染。作为三轨之一, tone_noncity_media_ss 与 tone_noncity_media_full、tone_noncity_media_ctx 保持并排的互为稳健性关系, 三者各自独立 just-identified、不分主次, 绝不可混入同一个 over-identified Hansen J 检验共同充当过度识别的工具变量集合; 在稳健性附表中三轨应逐一并列报告, 供读者判断结论是否对文本窗口选择敏感。

<!-- rendered-citations:begin -->
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving content to investor sentiment; The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Peress, J. (2014). The media and the diffusion of information in financial markets; Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk; Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
