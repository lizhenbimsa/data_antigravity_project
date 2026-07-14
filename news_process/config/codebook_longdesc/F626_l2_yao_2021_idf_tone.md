---
family_id: F626
columns:
- yao_2021_idf_tone_app_ctx
- yao_2021_idf_tone_app_full
- yao_2021_idf_tone_app_ss
- yao_2021_idf_tone_ctx
- yao_2021_idf_tone_full
- yao_2021_idf_tone_hw_ctx
- yao_2021_idf_tone_hw_full
- yao_2021_idf_tone_hw_ss
- yao_2021_idf_tone_mw_ctx
- yao_2021_idf_tone_mw_full
- yao_2021_idf_tone_mw_ss
- yao_2021_idf_tone_ss
- yao_2021_idf_tone_std_ctx
- yao_2021_idf_tone_std_full
- yao_2021_idf_tone_std_ss
- yao_2021_idf_tone_tech_ctx
- yao_2021_idf_tone_tech_full
- yao_2021_idf_tone_tech_ss
- yao_2021_idf_tone_vw_ctx
- yao_2021_idf_tone_vw_full
- yao_2021_idf_tone_vw_ss
unit: 语调得分 (连续, 词级 IDF 加权版; canonical 口径下约在 [-1,1] 邻域, vw/mw/hw 变体分母不同故量纲随之漂移, std 变体为离散度非语调水平)
formula: 'article 层: yao_2021_idf_score = 逐词命中 Yao et al. (2021) 中文金融情感词典正/负条目后, 以该词在语料 (bank-fintech 报道全库, 以 content_full 唯一文档去重计) 上的三步 IDF 权重 (而非等权 1) 计入正负计数再做 (pos-neg)/(pos+neg) 归一化: 先算 raw_idf(w)=log10(N/(1+df(w))) (以 10 为底、分母 Laplace +1 平滑, N=唯一文档总数、df(w)=含该词的唯一文档数), 再做全词典均值归一化 normalized_idf(w)=raw_idf(w)/mean(raw_idf), 最后做 P1/P99 缩尾 final_idf(w)=Winsorize(normalized_idf(w), P1, P99); 三轨 (full/ctx/ss) 共享同一份基于 content_full 语料算出的 idf 权重表 (稀有情感词加权、高频泛用词降权, 呼应 tf-idf 词加权传统); bank-year 层 canonical: yao_2021_idf_tone_{full,ctx,ss} = mean(yao_2021_idf_score) over 该 bank-year 下 llm_verified_full==True 留篇集合的对应轨道文章 (encode.py agg dict[f"{d}_idf_tone{track}"]=(f"{d}_idf_score{track}","mean")); _std = 同集合上 std(yao_2021_idf_score) (年内跨篇离散度, ddof 默认 pandas std); _vw/_mw/_hw = 以 volume-weight/media-weight/herd-weight 对逐篇 idf_score 加权求和后除以对应加权分母 (panel[w_col]/_llm_denom(...)), 三者互为稳健并排、非同一权重的三种命名而已; _tech/_app = 限定在 P4 (Gomber locus 维度) LLM 分类判为「底层技术」/「应用层」的子集文章上重复上述 mean 聚合, 分母缩窄为该子集留篇数。'
producer: pipeline\panel\encode.py (article 层 idf_score 计算与 sum/std/vw/mw/hw 权重聚合; C2/F2 段) ; pipeline\panel\geography.py (dict_avg 跨词典综合与 _tech/_app 分类子集综合) ; pipeline\panel\stata_export.py (Stata 变量标签)
upstream: pipeline\sentiment\tone_words.py (Yao 2021 词典底层评分引擎, 词级极性判定 + 否定/程度副词/转折语言学规则) ; pipeline\sentiment\herd_decay.py (herd_weight 羊群衰减权重来源) ; pipeline\panel\encode.py (media_weight/volume_weight 分母口径)
citations:
- doi: "10.1016/j.jfineco.2013.08.018"
  type: journal
  authors: "Jegadeesh, N., & Wu, D."
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: "Journal of Financial Economics"
  vol: "110"
  issue: "3"
  pages_or_artno: "712–729"
- doi: "10.1108/eb026526"
  type: journal
  authors: "Spärck Jones, K."
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: "Journal of Documentation"
  vol: "28"
  issue: "1"
  pages_or_artno: "11–21"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673–719"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514–5532"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J."
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: "The Accounting Review"
  vol: "98"
  issue: "7"
  pages_or_artno: "315–345"
- doi: "10.1080/07421222.2018.1440766"
  type: journal
  authors: "Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W."
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: "Journal of Management Information Systems"
  vol: "35"
  issue: "1"
  pages_or_artno: "220–265"
new_dois: []
---

## CORE

【构念与来源】
本家族测度银行-金科共现报道的媒体语调 (media tone), 底层情感判定引擎是 Yao et al. (2021) 中文金融情感词典 (家族命名前缀 `yao_2021`, 与本仓库并行落地的另外五部中文金融情感词典 —— `jiang_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran` (中译版) —— 构成词典法情感测度的跨词典稳健性集合, 六部词典各自独立评分、互不覆盖、互为方法学稳健性验证, 详见 `pipeline/sentiment/tone_words.py::DICT_NAMES`)。与家族基名 `yao_2021_tone`/`yao_2021_negonly_tone` (等权词计数版语调) 不同, 本家族在词级极性计数之上叠加了 IDF (inverse document frequency, 逆文档频率) 加权: 每个命中情感词条不再等权计 1, 而是按该词在银行-金科报道全语料 (以 content_full 唯一文档去重) 中的稀有程度加权计入, 具体是先算 raw_idf(w) = log10(N/(1+df(w))) (以 10 为底、Laplace +1 平滑), 再做全词典均值归一化, 最后做 P1/P99 缩尾三步处理得到最终权重 (详见【方法学与计算】)。直觉是: 若某个"负面"词 (例如"下降"、"风险") 在几乎所有财经报道里都高频出现, 它对区分某一篇报道是否格外负面的边际信息很少; 反之若某词罕见但一旦出现则往往伴随强烈情绪 (例如"暴雷"、"塌方式"), 它应被赋予更高权重。这一权重设计直接继承自信息检索领域 tf-idf 词加权的经典思想 (Spärck Jones, 1972, 首次系统提出词特异性的统计解释及其在检索中的应用), 并在金融文本分析文献中有明确先例: Jegadeesh & Wu (2013, *Journal of Financial Economics*) 提出的 "word power" 方法即以词在语料中的相对信息含量而非等权词典计数来度量文档语调, 是本家族 IDF 加权分支在实证金融文献中的直接方法学锚点。

本家族与家族基名 `yao_2021_score`/`yao_2021_tone` 系列的关系是"同一底层词典 (Yao 2021) 之上的两套聚合权重方案互为稳健性"而非替代: 等权版回答"命中了多少褒贬词", IDF 加权版回答"命中的褒贬词有多罕见/多具信息量"。二者不应被视为互相印证正确性的重复测度, 而应被视为对"词该不该等权计入语调"这一测度设计选择的敏感性检验 —— 若两版本高度相关, 说明结论不依赖于该设计选择; 若出现系统性偏离, IDF 加权版本更适合捕捉罕见但信息量高的措辞冲击。

上游 `pipeline/sentiment/tone_words.py::build_idf_weights` 的实现注释将该测度的方法学锚点明确追溯至 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 关于 text-as-data 中 tf-idf 词加权 (§2.2) 的综述性论证, 并同时参照 Manning, Raghavan & Schütze (2008, *Introduction to Information Retrieval*) 第 6.2.1 节的 smooth IDF 公式设计以及 Fama & French (1993) 式的 P1/P99 Winsorization 惯例。Gentzkow et al. (2019) 的 DOI 不在本仓库文献锚点白名单池内, 故未被提升为本条目正式 citations 条目 (以避免臆造/超白名单引用), 但为保证代码自述锚点与文档描述不漂移, 特此在正文披露该出处; 本节下方仍以已入白名单的 Jegadeesh & Wu (2013) 作为 IDF 加权在实证金融文献中的直接方法学锚点, 二者分属信息检索方法论溯源与金融文本分析实证先例两个不同层次, 互不替代。

【方法学与计算】
计算分两层。article 层: 先按 `pipeline/sentiment/tone_words.py` 中 Yao 2021 词典条目扫描文章文本, 命中正/负情感词后不再单纯计数, 而是以该词在全语料库 (bank-fintech 共现报道全体, 以 content_full 唯一文档去重后统计) 上的 IDF 权重加权累加至正/负两侧加权计数。该 IDF 权重并非单步的 ln(N/df(w)), 而是三步处理: 先算 raw_idf(w) = log10(N/(1+df(w))) (以 10 为底, 分母 Laplace +1 平滑以避免 df(w)=0 时除零), 再做全词典均值归一化 normalized_idf(w) = raw_idf(w)/mean(raw_idf) (使 IDF 加权后得分量级 ≈ 等权版、可共享同一套阈值), 最后做 P1/P99 缩尾 final_idf(w) = Winsorize(normalized_idf(w), P1, P99) (防止极端稀有词权重过大或极高频词权重被压至零); N=唯一文档总数, df(w)=含该词的唯一文档数。加权正负计数再做 (加权正-加权负)/(加权正+加权负) 归一化得到逐篇 `yao_2021_idf_score{track}`。IDF 权重表本身在 content_full 语料上算一次并被三轨共享 (词的稀有度是语料级常量, 不随轨道切换重新估计), 但正负计数的逐词扫描仍按各轨各自的文本窗口 (full/ctx/ss) 独立进行, 三轨互不借用彼此的扫描结果。词级语言学规则 (否定翻转/程度副词/转折句式) 与等权版共用同一套规则引擎, 唯一差异是词命中后的计数权重从等权 1 换成 idf(w); 因此本家族与词典消融梯度家族 (`{dict}_score_{raw,negonly,degonly,...}`) 是正交的两条不同稳健性维度, 不互相嵌套。

bank-year 层聚合再分裂出五条并排子测度: canonical `yao_2021_idf_tone{full,ctx,ss}` = 该 bank-year、该轨道下留篇文章 idf_score 的算术均值 (留篇门控 = full-only 铁律: 是否计入"一篇银行-金科报道"只看 `llm_verified_full==True`, ctx/ss 轨道行宇宙是 full 留篇集合的子集, 详见 CLAUDE.md 「留篇门控 = full-only」); `_std` 是同一集合上的年内跨篇标准差, 度量语调的年内离散/波动而非水平, 不能与均值口径的其余四条并列比较大小; `_vw`/`_mw`/`_hw` 分别是按报道量权重 (volume-weight, 反映覆盖密度)、媒体权威权重 (media-weight, 反映发布媒体的影响力/可信度分层) 与羊群衰减权重 (herd-weight, 源自 `herd_decay.py` 对扎堆报道的时间衰减折算, 详见 CLAUDE.md 羊群衰减相关铁律) 对逐篇加权求和再除以对应口径的加权分母得到, 三者是彼此独立的三种加权方案, 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; `_tech`/`_app` 是在 P4 (Gomber locus) LLM 分类维度下, 将样本限定在被判定为「底层技术」(tech, infrastructure-layer fintech 报道) 或「应用层」(app, application-layer fintech 报道) 的子集文章上重复相同的 mean 聚合, 用以检验语调结果是否被某一类金科报道 (如支付/信贷应用层新闻 vs 区块链/云计算底层技术新闻) 系统性驱动, 二者同样是并排稳健性切分而非层级关系。

三轨 (full=标题+正文全文、ctx=标题+实体窗口、ss=标题+银行∧金科同句±N窗) 是本家族与仓库内几乎所有情感测度共享的正交切分维度, 与上述 IDF 加权/权重方案/分类子集三条维度彼此独立、可自由组合 (例如 `yao_2021_idf_tone_hw_ss` = 同句轨 × 羊群加权); ss 轨在无银行∧金科同句共现时回退为全文 body 并置 `ss_is_fallback=True` (镜像 ctx 回退语义)。铁律: 三轨之间、五条权重/子集变体之间, 均只应各自并排作为稳健性检验或互补测度, 不得混入同一过度识别 (over-identified) 的 Hansen J 检验设定。

【文献定位】
IDF 加权词典法情感测度植根于两条方法学脉络的交汇: 一是信息检索传统下的词特异性加权 —— Spärck Jones (1972) 首次系统提出以逆文档频率刻画词的检索区分力, 该统计解释后被广泛移植入文本情感分析, 成为 tf-idf 词加权范式的奠基性引用; 二是金融文本分析中显式采用信息量加权而非等权词典计数的先例 —— Jegadeesh & Wu (2013, *Journal of Financial Economics*) 的 "word power" 方法证明, 以词在语料库中的相对信息含量 (而非固定词典赋分) 度量文档语调, 相比等权 Loughran-McDonald 式词典法能更贴近市场对披露文本的实际定价反应, 是本家族 IDF 加权设计的核心方法学锚点。就中文金融文本而言, Du et al. (2022, *Review of Finance*) 系统论证了语言与领域特异性对情感词典效度的重要性, 构建了专用中文金融情感词典并证明领域特异词典优于通用/翻译词典, 为本仓库六部词典 (含 Yao 2021) 并排互为稳健性的设计取向提供了直接的实证支撑 —— 单一词典 (无论加权与否) 都可能因词库覆盖偏误而产生测度误差, 多词典 × 多权重方案的并排设计正是针对这一已知局限的稳健性对冲。Frankel, Jennings & Lee (2022, *Management Science*) 进一步比较了机器学习与词典法两条情感测度路径的分歧来源, 指出词加权方案的选择本身即是词典法测度误差的重要来源之一, 呼应本家族将等权版与 IDF 加权版并列作为两种设计选择下的敏感性检验、而非孰优孰劣替代关系的处理方式。

## VAR: yao_2021_idf_tone_full

【变体差分】
本列是家族 canonical 口径: 全文轨 (full, 标题+正文全文扫描) × 未加权聚合 (bank-year 内逐篇 idf_score 简单算术均值) × 不限定分类子集。逐篇 `yao_2021_idf_score_full` 的计算方式是先在标题+正文全文范围内扫描 Yao et al. (2021) 词典条目, 命中正/负情感词后以该词在银行-金科报道全语料上的三步 IDF 权重 (raw_idf 对数 + 均值归一化 + P1/P99 缩尾, 详见【方法学与计算】) 而非等权 1 计入正负两侧加权计数, 再做 (加权正-加权负)/(加权正+加权负) 归一化; 语言学规则 (否定翻转/程度副词/转折句式) 与等权版共用同一规则引擎。作为 P1 (`bank_fintech_tone`) 论文体系下词典法情感测度的 IDF 加权臂之一, 是与三家 LLM 投票 (`llm_vote_tone_full`)、三个 BERT 模型 (`finbert_cn`/`fin_sent_zh`/`finbert2`)、以及等权词典版 (`yao_2021_tone_full`) 并排的互为稳健性测度, 不作为任何回归的默认唯一 treatment; 与其余五部词典 (`jiang_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran`) 各自的 IDF 加权版共同构成跨词典稳健性集合。分母 = 该 bank-year 下 `llm_verified_full==True` 的留篇文章数 (full-only 门控, 2026-06-29 铁律), ctx/ss 两轨的行宇宙均是本列所定义留篇集合的条件子集 (conditional-on-full)。若某 bank-year 该轨道下无留篇文章, 本列取值为 NaN 而非 0, 避免把"无报道"误判为"零语调/中性"。本列与家族内 std/vw/mw/hw/tech/app 六条并排子测度共同构成 IDF 加权分支下的完整梯子, 全部以本列的全文轨口径为基准参照, 但"基准"仅指代 canonical 命名习惯 (无后缀即家族默认展示口径), 并不意味着其余变体在识别策略或稳健性权重上处于从属地位; 在实证使用时, 建议将 `_full`/`_ctx`/`_ss` 三轨结果并列报告于同一稳健性附表, 而非只报告本列并将其余列压缩为脚注。

## VAR: yao_2021_idf_tone_ctx

【变体差分】
与 canonical `yao_2021_idf_tone_full` 的唯一差异是扫描文本窗口: 本列用标题+实体窗口 (ctx, 目标银行/金科实体周边窗口文本, stage 14 `ctx_materializer` 物化的 `content_ctx`) 而非全文正文计算逐篇 idf_score 再做 bank-year 均值聚合; idf(w) 权重仍按银行-金科报道全语料计算 (词的稀有度定义是语料级常量, 不随轨道切换而重新估计, 三轨共享同一份 idf 权重表)。行宇宙是 full 留篇集合的子集 (conditional-on-full: 是否计入"一篇银行-金科报道"只看 `llm_verified_full`, ctx 轨只是在该留篇集合上换一个更聚焦的扫描窗口重新计分), 与 `_full`/`_ss` 互为三轨稳健性并排, 不应混入同一 over-identified Hansen J 设定。相比全文轨, ctx 轨剔除了文章中与目标银行/金科实体无直接关联的段落 (例如同一篇报道中涉及其他机构或宏观背景的段落), 理论上更贴近"针对该银行本身的语调"而非"整篇报道通篇语调的稀释均值", 是全文轨在窗口选择维度上的稳健性对照, 二者若结论一致则说明语调结果不依赖于是否纳入无关段落; 若二者出现系统性偏离, 则提示全文轨可能混入了与目标银行本身无关的背景段落语调 (例如同一篇综述性财经报道中涉及多家机构或宏观政策评论的部分), 此时 ctx 轨更适合作为构念效度更高的替代口径纳入正文表格而非仅作附录稳健性检验。本列的物化时点在 stage 14, 早于 stage 21 情感 LLM 判定, 使 stage 15/16 等下游阶段也能在 stage 21 完成前消费该三轨文本, 与词典法本身的计算顺序无关。

## VAR: yao_2021_idf_tone_ss

【变体差分】
与 canonical 的差异同为文本窗口切换: 本列用标题+银行∧金科同句 (±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 扫描文本计算逐篇 idf_score, 是三轨中窗口最窄、语境最聚焦的一条 —— 只统计目标银行实体与金科关键词在同一句 (或相邻 N 句) 内共同出现的局部文本。语义上镜像 ctx 轨的回退规则: 若该 bank-year 下某篇文章无银行∧金科同句共现, 则 `content_ss` 回退为全文 body 且该篇的 `ss_is_fallback=True`, 参与本列聚合的分母 (`n_articles`) 与 ctx 轨共享同一优雅降级口径, 避免因窗口过窄导致大量文章被误判为无文本可扫描。与 `_full`/`_ctx` 互为并排稳健性轨道, 三者各自 just-identified, 严禁混入同一 over-identified Hansen J 检验。ss 轨的构念优势在于最大程度剔除"报道提及银行但情绪陈述实际针对金科合作方 (或反之)"的归因混淆, 代价是当同句共现较为稀疏时 (尤其小样本 bank-year) 回退比例可能偏高, 使用时应结合 `ss_is_fallback` 占比判读结果的可信度。判定银行∧金科同句共现的原语与 stage 13 硬过滤所用的窗口共现原语 (`has_bank_fintech_cooccurrence_within_radius`) 是两套不同口径的函数 (`extract_bank_fintech_cooccurrence` 严格同句, 二者不可互相复用), 前者服务于本家族此类三轨文本测度, 后者服务于文章级留存与否的硬过滤判定, 两处口径均以 CLAUDE.md「stage 13 共现硬过滤」段落为准绳, 不应混淆。

## VAR: yao_2021_idf_tone_std_full

【变体差分】
本列不是"语调水平"测度, 而是全文轨下 bank-year 内逐篇 `yao_2021_idf_score_full` 的年内标准差 (跨篇离散度, `encode.py` C2 段 `agg[f'{d}_idf_tone_std{track}']=(f'{d}_idf_score{track}','std')`, pandas 默认 ddof=1)。它回答的问题与 canonical 均值列不同: canonical 问"这家银行这一年的报道整体偏正面还是负面", 本列问"这家银行这一年的报道语调有多不稳定/多两极分化" —— 同样的均值水平下, 一家银行可能全年报道语调平稳一致, 另一家可能正负交替剧烈波动, 二者对市场认知/融资成本等下游结果变量的传导机制未必相同。std 度量常与覆盖量 (ln_coverage) 相乘构造叙事暴露度指标 (fintech_exposure 类似构造思路, 见 `geography.py` 中 Fintech Exposure = ln_coverage × tone_std 的注释, 高覆盖 + 高波动被解读为高叙事暴露, 即该银行不仅被频繁报道且语调起伏大, 意味着市场关注度与叙事不确定性同时偏高)。样本量过小 (单一 bank-year 仅 1-2 篇留篇) 时 std 数值不稳定甚至退化为 NaN (单篇样本无法计算标准差), 使用时须留意年内文章数分母, 不宜与均值口径的 canonical 列直接放入同一张系数比较表格。std 变体是本家族内唯一的"二阶矩"测度, 与其余均值口径的 canonical/vw/mw/hw/tech/app 六条构念上分属两个不同层级 (水平 vs 离散度), 三轨 (`_std_full`/`_std_ctx`/`_std_ss`) 各自独立计算、互为并排稳健性, 严禁混入同一 over-identified Hansen J 设定, 亦不建议直接与其余词典 (`jiang_2021_idf_tone_std`/`bian_2021_idf_tone_std` 等) 的数值跨词典比较绝对水平 (不同词典的极性词覆盖率/idf 权重分布不同, std 的量纲不可比, 更适合比较相对排序或标准化后的 z-score)。

## VAR: yao_2021_idf_tone_std_ctx

【变体差分】
在 `_std_full` 离散度构念基础上叠加 ctx 轨窗口差分: 标准差计算改用标题+实体窗口文本产生的逐篇 idf_score, 而非全文正文的逐篇分数; 与 `_std_full`/`_std_ss` 三轨并排, 且离散度构念本身与非 std 的均值/权重变体族 (canonical/vw/mw/hw/tech/app) 正交, 不可与 canonical 均值列直接比较大小或混入同一回归的同一系数解释。ctx 轨窗口收窄意味着参与标准差计算的逐篇分数本身来自更聚焦的文本段落, 理论上单篇分数的方差成分与全文轨不完全相同 (剔除了无关段落带来的噪声, 但也可能因窗口过窄而放大对个别句子措辞的敏感度), 因而 `_std_ctx` 与 `_std_full` 的相对大小本身即是一项值得报告的稳健性对照, 而非期望二者数值恒等。若某银行的 `_std_ctx` 显著低于 `_std_full`, 一种合理解读是该银行报道中与其自身直接相关的语调较为一致, 波动主要来自报道全文中涉及其他实体或宏观背景的段落; 反之若 `_std_ctx` 高于 `_std_full`, 则提示实体窗口内的措辞本身比全文整体更两极分化, 值得结合具体文章复核。本列同样受 stage 14 `ctx_materializer` 物化的 `content_ctx` 驱动, 与家族内其余 ctx 轨列共享同一物化产物, 不重复扫描原始正文。

## VAR: yao_2021_idf_tone_std_ss

【变体差分】
在 `_std` 离散度构念基础上叠加 ss 轨窗口差分: 标准差计算改用标题+银行∧金科同句窗口文本产生的逐篇 idf_score, 回退语义 (无同句共现→回退全文、`ss_is_fallback=True`) 与其余 ss 轨列一致, 三轨离散度变体互为并排稳健性、不设主次。由于 ss 轨窗口最窄, 在同句共现比例较低的 bank-year 中大量文章会走回退路径而使用与全文轨相同的文本, 此时 `_std_ss` 可能在数值上趋近于 `_std_full`; 反之在同句共现充分的样本中, `_std_ss` 捕捉的是最贴近"银行与金科关系本身"的措辞离散度, 与覆盖度更宽的 `_std_ctx`/`_std_full` 形成窗口宽度上的梯度对照, 三者应联合报告而非只取其一。本列的回退比例 (`ss_is_fallback` 占比) 是判读结果可信度的关键辅助信息: 高回退比例的 bank-year 意味着本列在事实上退化为接近全文轨的离散度测度, 此时不宜将 `_std_ss` 与 `_std_full` 的微小数值差异过度解读为"同句共现语境更聚焦所致", 而应先核查该 bank-year 的回退比例是否偏高。本列在实证使用中的一个常见用法是作为异质性分组变量的构造原料: 将 bank-year 按 `_std_ss` 数值中位数二分为"语调高波动组"与"语调低波动组", 再检验主回归系数是否在两组间存在系统性差异, 这一用法与均值口径的 canonical 列作为主 treatment 的角色截然不同, 不应混淆二者在模型中的建模位置; 本列所属的"离散度构念"三轨组合与家族内均值口径的三轨组合是两条平行但独立的稳健性梯子, 不应被压缩合并为单一梯子解读。

## VAR: yao_2021_idf_tone_vw_full

【变体差分】
在全文轨基础上, 聚合方式从简单算术均值改为按 volume-weight (报道量/覆盖密度权重) 加权: `encode.py` F2 段先累加逐篇 idf_score × volume 权重得到 `{d}_idf_score_vw_sum{track}`, panel 层再除以该权重口径下的加权分母 (`panel_new_cols[f'{d}_idf_tone_vw{track}'] = panel[w_col] / denom`, 分母口径见 `_llm_denom('vw', ...)`), 而非直接除以文章数。与 canonical `_full` 相比, 高覆盖时段/高频报道的文章在本列中获得更大话语权, 用以检验语调结论是否被少数密集报道期系统性驱动 (例如某银行仅因一次舆情事件在短期内被集中报道, 若该事件语调极端, canonical 简单均值与 volume-weight 均值可能出现系统性偏离)。与 `_mw`/`_hw` 权重方案互为并排稳健性, 权重来源互不相同 (volume 权重反映报道密度, media 权重反映来源权威性, herd 权重反映时间衰减折算), 不应混入同一过度识别检验。volume-weight 加权的一个直接应用场景是: 当某银行的年度报道量本身极不均匀 (例如某月因单一事件产生数十篇报道、其余月份几乎无报道) 时, canonical 简单均值会让该事件月份的语调主导全年结果, 而 volume-weight 加权则依据报道密度本身重新校准每篇的边际贡献, 二者对同一份底层数据给出的解读侧重点不同, 应联合报告而非相互替代。volume-weight 的具体权重口径与 `_llm_denom` 函数所服务的 LLM 投票语调族共用同一套加权分母计算逻辑 (`_llm_denom('vw', 'llm', track, denom)` 与 `_llm_denom('vw', short, track, denom)` 等), 说明本仓库内 LLM 法与词典法情感测度在 volume-weight 这一权重维度上采用了统一的实现范式, 便于跨方法比较时不因权重口径不一致而引入额外噪声。

## VAR: yao_2021_idf_tone_vw_ctx

【变体差分】
在 `_vw` volume-weight 加权聚合基础上叠加 ctx 轨窗口差分: 逐篇 idf_score 来自标题+实体窗口文本, 权重与加权分母仍按 volume-weight 口径独立计算 (不借用全文轨的权重列或分母)。三轨 × 加权方案的组合是本仓库正交设计的典型体现: ctx/full/ss 窗口维度与 vw/mw/hw 权重方案维度彼此独立、可自由交叉组合, 均各自并排, 不构成嵌套层级或主次关系; 本列可用于检验"volume-weight 加权是否放大或缩小了窗口收窄带来的语调差异", 是对家族内两条正交稳健性维度交互效应的联合考察。本列与 `_vw_full`/`_vw_ss` 的比较还可用于诊断"高覆盖时段的报道是否恰好也是与银行本身关联度更高的报道" —— 若 `_vw_ctx` 与 `_vw_full` 高度接近而 canonical `_ctx` 与 `_full` 之间有明显差异, 则说明 volume-weight 加权在一定程度上抵消了窗口选择带来的差异, 这类交叉模式对理解测度设计的敏感性边界有参考价值。本列同样服务于家族「留篇门控 = full-only」铁律: 是否计入某篇报道的判定仍只看该篇在 full 轨是否通过 `llm_verified_full` 验证, ctx 轨的 volume-weight 加权仅在此留篇集合的子集上重新计算权重与分数, 不改变留篇口径本身, 三轨、三权重、留篇门控三条铁律在本列上同时叠加体现, 是本仓库正交设计哲学的一个具体缩影。

## VAR: yao_2021_idf_tone_vw_ss

【变体差分】
在 `_vw` 加权聚合基础上叠加 ss 轨窗口差分: 逐篇 idf_score 来自标题+银行∧金科同句窗口文本, 回退语义与其余 ss 轨列一致 (无同句共现→全文回退, 标记 `ss_is_fallback`)。volume-weight 分母与 ctx/full 轨各自独立计算, 不跨轨共享同一权重来源列; 由于 ss 轨样本天然更聚焦, 在同句共现密度本身与报道量高度相关的极端情形下 (例如某银行的金科合作报道恰好也是该年报道量最集中的时段), `_vw_ss` 可能进一步放大 volume-weight 的效应, 使用时建议与 `_vw_full`/`_vw_ctx` 联合报告以判断该效应是否稳健。本列继承 ss 轨的全部回退语义细节: 无同句共现的文章其 `content_ss` 回退为全文 body, 该篇同时参与 volume-weight 权重计算与逐篇 idf_score 计算的文本来源均切换为全文, 二者保持内部一致, 不存在"权重按同句窗口算、分数按全文算"的口径错配。本列是 volume-weight 权重方案下三轨组合 (`_vw_full`/`_vw_ctx`/`_vw_ss`) 中窗口最窄的一条, 与另外两条共同回答"报道量密集时段的语调结论是否稳健于窗口选择", 三者若能在方向上保持一致, 是对该结论稳健性的额外支撑; 若不一致, 应结合各轨的回退占比与样本规模逐一排查原因, 而非直接取三者均值草率合并。

## VAR: yao_2021_idf_tone_mw_full

【变体差分】
在全文轨基础上, 聚合方式改为按 media-weight (发布媒体权威性/影响力权重) 加权求和再除以对应加权分母 (`panel_new_cols[f'{d}_idf_tone_mw{track}'] = panel[w_idf] / mw_denom`), 而非等权文章计数均值。直觉上呼应"权威媒体的语调对市场认知影响更大"的先验, 与 Holzman, Miller & Twedt (2023, *The Accounting Review*) 一类媒体权威加权语调设计思路一致 (该文献研究媒体情绪与季度盈余公告披露约束的互动, 未直接引用本家族但媒体权威加权语调的方法论精神相通, 已列入本条目 citations)。与 `_vw`/`_hw` 权重方案互为并排稳健性检验之一, media-weight 与 volume-weight 的核心区别在于: 前者按发布来源的影响力分层加权 (同一篇文章的权重取决于刊发它的媒体), 后者按报道时段的密度加权 (同一篇文章的权重取决于它所处时段的报道总量), 二者捕捉的是完全不同的信息传导渠道, 不应被视为同一构念的两种实现。media-weight 权重的构造依赖于对发布媒体的某种权威性/影响力分层 (例如全国性财经媒体 vs 地方性都市报), 该分层本身是全语料级别的固定映射, 不随 bank-year 或轨道切换而变化, 变化的只是各篇文章按其发布媒体归属被赋予的权重数值以及参与聚合的样本子集。

## VAR: yao_2021_idf_tone_mw_ctx

【变体差分】
在 `_mw` media-weight 加权聚合基础上叠加 ctx 轨窗口差分: 逐篇 idf_score 取自标题+实体窗口文本, media-weight 权重与加权分母的计算口径与 full 轨相同但基于各自轨道的留篇样本重新计算, 不跨轨复用同一权重列或分母; 换言之, 即便某篇文章在 full 轨与 ctx 轨都被纳入统计, 其在两轨各自聚合中所占的媒体权威权重比例也可能因分母 (该轨道下 media-weight 加权总量) 不同而不同。本列与 `_mw_full`/`_mw_ss` 共同构成"媒体权威加权"这一权重方案下的三轨稳健性组合, 三者均服务于同一个研究问题 —— 权威媒体的语调是否比一般媒体更能预测/解释银行层面的下游结果 —— 只是在窗口选择上给出三种互补答案, 结论若在三轨间保持一致方向, 则该媒体权威效应的稳健性证据更强。本列的权重来源列在 ctx 轨下与 full 轨互相独立计算, 意味着即便某银行在两轨下的留篇集合高度重叠, 二者各自的 media-weight 加权总量 (分母) 也可能因参与聚合的具体文本片段不同而不同, 这是本列区别于简单"换个窗口重新算均值"的关键之处 —— 权重本身也在随窗口重新校准, 而非固定不变。

## VAR: yao_2021_idf_tone_mw_ss

【变体差分】
在 `_mw` 加权聚合基础上叠加 ss 轨窗口差分: 逐篇 idf_score 取自标题+银行∧金科同句窗口文本, 回退语义 (无同句共现→全文回退, `ss_is_fallback=True`) 与其余 ss 轨列一致。media-weight 与 vw/hw 权重方案彼此独立、并排互为稳健性, 不应在同一 Hansen J 设定中混用; 本列的构念意义是"在最聚焦的语境窗口下, 是否仍然是权威媒体的语调对结果驱动更强", 若该效应在 ss 轨依然成立, 则说明媒体权威加权的解释力并非来自窗口收窄前段落中的无关噪声。本列的回退语义 (`ss_is_fallback`) 与其余 ss 轨列一致, 使用者在解读 media-weight 效应强弱时应结合该 bank-year 的回退占比, 避免把回退主导下趋同于全文轨的数值误判为窗口收窄本身带来的效应。本列所属的"离散度构念"三轨组合 (`_std_full`/`_std_ctx`/`_std_ss`) 与家族内均值口径的三轨组合 (canonical/`_ctx`/`_ss`) 是两条平行但独立的稳健性梯子, 二者分别对应"语调水平的三轨稳健性"与"语调离散度的三轨稳健性", 不应被压缩合并为单一梯子看待。本列在实证使用中的一个常见用法是作为异质性分组变量的构造原料: 将 bank-year 按 `_std_ss` 数值中位数二分为"语调高波动组"与"语调低波动组", 再检验主回归系数是否在两组间存在系统性差异, 这一用法与均值口径的 canonical 列作为主 treatment 的角色截然不同, 不应混淆二者的建模位置。与 `_hw_ss`/`_vw_ss` 相比, 本列的权重来源 (媒体权威分层) 是唯一一个不依赖时间序列或报道密度、纯粹取决于发布来源身份的权重方案, 三者并列可分离出"谁说的"(media)、"多久前跟风的"(herd) 与"当时报道多密集"(volume) 三条互相独立的权重解释力来源。

## VAR: yao_2021_idf_tone_hw_full

【变体差分】
在全文轨基础上, 聚合方式改为按 herd-weight (羊群衰减权重, 源自 `pipeline/sentiment/herd_decay.py` 对同题材扎堆报道按时间衰减折算的权重) 加权求和再除以对应加权分母。构念上回答"若剔除/淡化扎堆跟风报道对语调的重复计入影响, 银行的报道语调是否依然成立" —— 当多家媒体在短时间内围绕同一事件密集转载/跟风报道时, 若不加权处理, 该事件的语调会在简单均值中被反复计入、放大其对 bank-year 语调水平的影响; herd-weight 对此类扎堆报道按时间衰减折算, 使距首发时间较近的跟风报道权重递减。与 `_vw`/`_mw` 互为并排稳健性权重方案, herd-weight 的来源列 (`herd_weight_full`) 与轨道严格对齐, 不存在跨轨借用同一权重列的 legacy fallback 风险 (仓库注释中明确警示过该类 bug 模式: 若误将 ctx/ss 轨的权重列指向同一份 `herd_weight` 单列, 会导致三轨的加权求和列在数值上意外相等, 该风险已在 `encode.py` 中修复并有显式回归防护)。羊群衰减权重的经济学直觉与"媒体扎堆报道会放大而非真实反映信息含量"这一叙事密切相关: 若一家银行在短短几天内被十余家媒体转载同一篇原创报道的核心观点, 简单均值会把这十余篇高度雷同的文章视为十余条独立信息, 而 herd-weight 加权版本更贴近"这实质上是一条信息被多次转述"的现实, 是对语调测度中信息重复计入偏误的直接校正尝试。

## VAR: yao_2021_idf_tone_hw_ctx

【变体差分】
在 `_hw` herd-weight 加权聚合基础上叠加 ctx 轨窗口差分: 逐篇 idf_score 取自标题+实体窗口文本, herd-weight 来源列为 `herd_weight_ctx` (与 full/ss 轨的权重来源列严格区分, 不共用同一底层权重, 三轨权重各自基于该轨道下的报道时间序列独立计算羊群衰减)。本列可用于检验"聚焦实体窗口后, 羊群衰减加权是否仍能有效对冲扎堆报道的重复计入", 是窗口维度与权重方案维度交叉稳健性的又一实例。当某银行的扎堆报道恰好集中在与其自身直接相关的段落 (而非无关背景信息) 时, `_hw_ctx` 相对 canonical `_ctx` 的收缩幅度会比 `_hw_full` 相对 `_full` 的收缩幅度更明显, 这类比较有助于定位羊群效应主要发生在文本的哪一层面。本列与 `_vw_ctx`/`_mw_ctx` 共同构成 ctx 轨下的三种权重方案并排组合, 三者均建立在同一份 `content_ctx` 物化文本之上, 分数计算逻辑一致, 唯一差异是聚合阶段所用的加权分母来源不同, 这种"同一份文本、多套权重"的设计使得权重方案本身的效应可以被单独识别, 而不与窗口选择效应混淆。在实证报告中, 建议将 `_hw_ctx`/`_vw_ctx`/`_mw_ctx` 三列并列置于同一张 ctx 轨权重稳健性附表中, 而非分散在不同表格里各自单独出现, 便于读者一眼判断三种权重方案在同一窗口口径下的结论是否收敛。

## VAR: yao_2021_idf_tone_hw_ss

【变体差分】
在 `_hw` 加权聚合基础上叠加 ss 轨窗口差分: 逐篇 idf_score 取自标题+银行∧金科同句窗口文本, herd-weight 来源列为 `herd_weight_ss`, 回退语义 (`ss_is_fallback`) 与其余 ss 轨列一致。三轨 herd-weight 变体互为并排稳健性, 不设主次; 由于 ss 轨的留篇样本更聚焦于银行-金科直接关联报道, 扎堆跟风的可能性理论上应低于覆盖更宽的 full/ctx 轨, 因此 `_hw_ss` 与未加权的 `_ss` canonical 列之间的数值差异, 相对 `_hw_full` 与 `_full` 之间的差异, 可能呈现出不同幅度的收缩, 这一模式本身即是判读羊群效应集中在哪一层级文本关联度上的线索。本列是家族内 herd-weight 加权方案的最后一条轨道变体, 与 `_hw_full`/`_hw_ctx` 联合构成完整的三轨 herd-weight 组合, 使用时应三者并列报告而非选择性地只报告支持某一结论的单一轨道, 这也是全仓库三轨纪律 (禁混同一 Hansen J) 在具体家族层面的落地体现。本列的分母来源列 `herd_weight_ss` 与 ss 轨的文本来源列 `content_ss` 共享同一套回退触发条件 (无银行∧金科同句共现), 二者在实现层面同步回退, 不存在权重列与文本列各自独立回退导致口径错配的风险。本列是家族内 herd-weight 加权方案三轨组合的收官列, 完成了本家族"三种权重方案 × 三轨窗口"九列矩阵 (vw/mw/hw × full/ctx/ss) 中的最后一格, 至此六部词典之一的 Yao 2021 IDF 加权语调测度在权重维度上的稳健性覆盖已完整闭合。

## VAR: yao_2021_idf_tone_tech_full

【变体差分】
在全文轨、未加权聚合基础上, 将聚合样本限定为 P4 (Gomber 2018 locus 维度) LLM 分类判为「底层技术」(infrastructure-layer fintech, 如支付清算底层系统、云计算/区块链基础设施类报道) 的子集文章, 分母相应缩窄为该子集在该 bank-year、该轨道下的留篇文章数 (`geography.py` 分类维度综合段: `if f'n_articles{suffix}' not in panel.columns: continue`, 无该子集分类计数列时优雅跳过整个子集综合)。用以检验语调结论是否集中来自技术底层类报道 —— 例如某银行若在样本期内恰好经历了一次核心系统迁移或数据泄露事件, 相关报道多归入底层技术类, 语调结果可能被这类特定事件驱动而非反映银行金科合作的整体基调。与 `_app_full` (应用层子集) 互为并排的分类维度稳健性切分, 二者共同构成对"语调结果是否被某一类金科报道类型驱动"的敏感性检验, 而非彼此的层级或互补关系; 该分类判据与 P4 论文体系下 `citation_weighted_patent` 等专利产出类结果变量所依托的技术分类逻辑同源, 但本家族聚合仅服务于语调测度本身。本列的分类判定来自 LLM 逐篇标注, 与家族「LLM 三家投票」情感测度共用同一套三家模型基础设施但服务于不同任务 (分类而非语调打分), 二者在 `avg_category_confidence` 等诊断列上共享置信度判读框架 (mean≥0.70 视为高置信、<0.50 视为低置信慎用), 该判读逻辑在 `export.py` G-20 段落有显式日志输出。

## VAR: yao_2021_idf_tone_tech_ctx

【变体差分】
在 `_tech` 底层技术子集限定基础上叠加 ctx 轨窗口差分: 逐篇 idf_score 取自标题+实体窗口文本, 子集判定 (是否属于「底层技术」locus 分类) 与轨道切换相互独立正交, locus 分类结果本身通常在全文层面判定、不随轨道窗口收窄而改变, 变化的仅是用于计算 idf_score 的扫描文本范围。样本量相对 `_tech_full` 进一步受限于该子集内文章是否落入实体窗口有效范围, 小样本 bank-year 数值可能不稳定。本列与 `_app_ctx` 在 ctx 轨下共同构成 locus 分类维度的并排稳健性对照, 二者均建立在同一份 `content_ctx` 物化文本之上、只是分类归属不同, 与 `_tech_full`/`_tech_ss` 一同构成底层技术子集下的三轨完整组合; 若某银行在 `_tech_full` 与 `_tech_ctx` 之间出现方向一致的结论, 则说明底层技术类报道的语调效应不依赖于是否纳入报道全文中的无关背景段落。P4 论文体系下 locus 分类维度的 tech/app 二分本身继承自 Gomber, Kauffman, Parker & Weber (2018, *Journal of Management Information Systems*, 已列入本条目 citations) 对金融科技创新层级的划分框架, 该文献将金融科技力量划分为不同的作用层次, 本仓库借鉴该分层逻辑对银行-金科报道做二元 locus 判定, 底层技术子集近似对应该框架中更偏基础设施与技术平台的创新层, 与应用层子集 (更偏终端产品与服务) 形成互补但不重叠的报道类型划分。

## VAR: yao_2021_idf_tone_tech_ss

【变体差分】
在 `_tech` 子集限定基础上叠加 ss 轨窗口差分: 逐篇 idf_score 取自标题+银行∧金科同句窗口文本, 回退语义 (`ss_is_fallback`) 与其余 ss 轨列一致; 子集样本量在同句窗口下可能进一步缩窄 (需同时满足"银行∧金科同句共现"与"locus 分类为底层技术"两项判据), 是本家族全部 21 列中样本约束最严格的组合之一, 小样本 bank-year 应格外留意 NaN 覆盖率与该子集下 `n_articles_tech` 分母是否过小导致均值不稳定。使用本列时建议同时核查该 bank-year 的 `n_articles_tech` 与 `ss_is_fallback` 占比两项辅助信息: 若前者过小则均值本身不可靠, 若后者过高则本列在事实上退化为 `_tech_full` 的近似值, 二者任一情形出现都应在正文或附录中明确披露, 避免误将退化样本的数值解读为窗口收窄本身的独立效应。本列在本仓库当前 T=2 dev 语料 (110 家银行 × 2 年) 上因双重判据叠加而样本极度稀疏, 属预期退化; 生产 T=18 全量语料下样本量将大幅提升, 使用者在解读本列结果前应先核对所用语料的时间跨度是否足以支撑该子集统计推断。本列与 `_app_ss` 是本家族全部 21 列中构念约束最严格的一对, 二者均要求文章同时满足"银行∧金科同句共现"与"locus 分类归属明确"两项判据, 二者互不重叠 (同一篇文章只能落入 tech 或 app 其一), 联合使用时可精确定位语调结果在窗口维度与分类维度双重收窄下是否仍然稳健。

## VAR: yao_2021_idf_tone_app_full

【变体差分】
在全文轨、未加权聚合基础上, 将聚合样本限定为 P4 (Gomber 2018 locus 维度) LLM 分类判为「应用层」(application-layer fintech, 如支付产品、信贷科技应用、财富管理 App 类报道) 的子集文章。与 `_tech_full` 互为并排的分类维度稳健性切分, 二者分母互不重叠 (同一篇文章通常只归入 tech 或 app 其一, 具体取决于 locus 分类器基于置信度阈值的判定; 极低置信度样本另有 G-20 诊断标记, 详见家族所在 `export.py` 摘录), 二者相加通常不等于 canonical 未分类的全部留篇数 (存在未明确归类或双重归类的边际样本)。应用层报道在中国银行-金科合作语境中往往覆盖更贴近终端用户体验的产品与服务新闻, 与底层技术类报道在措辞风格与情绪基调上可能存在系统性差异, 本列即用于单独考察这一子域的语调表现。相较底层技术类报道, 应用层报道更容易涉及具体的用户投诉、产品体验评价等带有强烈主观色彩的措辞, 理论上其 IDF 加权语调的方差成分可能与底层技术类报道不同, `_app_full` 与 `_tech_full` 的联合报告有助于判断这一差异在实证数据中是否成立, 而非停留在理论推测层面。

## VAR: yao_2021_idf_tone_app_ctx

【变体差分】
在 `_app` 应用层子集限定基础上叠加 ctx 轨窗口差分: 逐篇 idf_score 取自标题+实体窗口文本, 子集判定与轨道切换相互独立正交, 与 `_app_full`/`_app_ss` 及 `_tech_ctx` 均互为并排稳健性, 不构成任何一方对另一方的替代或优先关系。本列同样建立在 stage 14 物化的 `content_ctx` 之上, 分类归属 (应用层 vs 底层技术) 沿用全文层面的 locus 判定结果, 换窗口不改变该篇文章的分类归属, 只改变参与 idf_score 计算的扫描文本范围, 这一"分类归属恒定、扫描窗口可变"的设计原则贯穿本家族全部 `_tech`/`_app` 系列列。由于应用层子集在中国银行-金科合作报道语料中的绝对占比通常与底层技术子集有所差异, `_app_ctx` 相对 `_app_full` 的样本损耗比例 (即多少篇应用层文章未落入实体窗口有效范围) 也是一项值得单独报告的辅助诊断信息, 有助于判断本列的样本代表性是否充分。本列与 `_tech_ctx` 在 ctx 轨下互为并排的分类维度稳健性对照, 二者共用同一份 `content_ctx` 物化文本与同一套实体窗口提取逻辑, 唯一差异是各自限定的 locus 分类子集不同, 结论若能在两条子集上呈现方向一致的语调梯度 (例如两者均随时间趋势同向变化), 则该结论不易被单一分类归属所主导。

## VAR: yao_2021_idf_tone_app_ss

【变体差分】
在 `_app` 子集限定基础上叠加 ss 轨窗口差分: 逐篇 idf_score 取自标题+银行∧金科同句窗口文本, 回退语义 (`ss_is_fallback`) 与其余 ss 轨列一致; 应用层子集在同句共现判据下的样本量同样可能进一步缩窄 (需同时满足同句共现与应用层分类两项判据), 与 `_tech_ss` 构成本家族内窗口最窄、子集划分最细的一对并排稳健性列, 二者联合使用可最大程度定位语调结果的构念来源 (窗口效应 vs 分类子域效应)。本列在 T=2 dev 语料上因双重判据叠加而样本极度稀疏属预期退化, 生产 T=18 全量语料下样本量将大幅提升; 使用者在跨 bank-year 比较本列数值前, 应先核对 `n_articles_app` (或对应子集分母列) 是否达到统计推断所需的最小样本规模, 避免把单篇甚至零篇样本的极端值误判为具有代表性的银行层面语调水平。本列是本家族 21 列中列举顺序上的最后一列, 与 `_app_full`/`_app_ctx` 共同构成应用层子集下的三轨完整组合, 三者所回答的问题始终一致 (应用层金科报道的语调水平如何), 差异只在于文本窗口的选择, 结论若能在三轨间保持方向一致, 即为应用层语调效应的稳健性证据; 若不一致, 则应在稳健性附表中如实披露差异而非选择性报告。

<!-- rendered-citations:begin -->
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712–729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11–21. https://doi.org/10.1108/eb026526
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673–719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514–5532. https://doi.org/10.1287/mnsc.2021.4156
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315–345. https://doi.org/10.2308/TAR-2020-0104
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220–265. https://doi.org/10.1080/07421222.2018.1440766
<!-- rendered-citations:end -->
