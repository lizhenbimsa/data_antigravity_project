---
family_id: F624
columns:
- yao_2021_idf_score_mw_sum_ctx
- yao_2021_idf_score_mw_sum_full
- yao_2021_idf_score_mw_sum_ss
unit: 无量纲加权得分之和 (IDF 语调分乘媒体权威权重后按银行-年求和; 分子列, 需除以 sum_media_authority_weight 才得到均值化语调 idf_tone_mw)
formula: 'article: idf_score{trk} = Σ_{w∈matched(yao_2021,article,trk)} idf(w)·polarity(w) (词典命中层面的 IDF 加权语调分, 与本列后缀 mw 无关); article: idf_score_mw{trk} = idf_score{trk} × media_authority_weight (media_authority_weight 由 compute_media_authority_weights 按报道来源媒体的权威性/影响力分层计算, 与该篇文本内容无关); panel: yao_2021_idf_score_mw_sum_{trk} = sum over articles(bank,year, 留篇门控=full-only) of idf_score_mw{trk} (SUM 而非 mean, 是分子列; 下游 {d}_idf_tone_mw{trk} = 本列 / sum_media_authority_weight 才是均值化的媒体权威加权语调), 逐轨 (full/ctx/ss) 独立扫描独立聚合'
producer: pipeline\panel\runner.py (compute_media_authority_weights 调用 + weighted_cols 相乘构造 idf_score_mw) ; pipeline\sentiment\tone_words.py (上游 idf_score 计算) ; pipeline\panel\encode.py (groupby sum 聚合为 idf_score_mw_sum, 及下游 idf_tone_mw 均值化) ; pipeline\panel\export.py ; pipeline\panel\stata_export.py
upstream:
- 11_news_bank
- 12_news_fintech
- 13_cooccurrence_filter
- 14_materialize_ctx
- 22_tone_words
- 媒体权威权重计算 (compute_media_authority_weights, 依据报道来源媒体列做权威性/影响力分层, 独立于 22_tone_words 词典扫描结果)
citations:
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11-21
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: Word power A new approach for content analysis
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: Language and domain specificity A Chinese financial sentiment dictionary
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: Disclosure sentiment Machine learning vs dictionary methods
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: Sentiment analysis of economic text A lexicon-based approach
  venue: Economic Inquiry
  vol: '63'
  issue: '1'
  pages_or_artno: 125-143
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing enthusiasm Media sentiment and the disciplining role of quarterly earnings announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
- doi: "10.3390/electronics12071632"
  title: "TF-TDA: A Novel Supervised Term Weighting Scheme for Sentiment Analysis"
  authors: "Alshehri, A., & Algarni, A."
  year: 2023
  venue: "Electronics"
  type: "journal"
- doi: "10.3390/jrfm18080412"
  title: "News Sentiment and Stock Market Dynamics: A Machine Learning Investigation"
  authors: "Davidovic, M., & McCleary, J."
  year: 2025
  venue: "Journal of Risk and Financial Management"
  type: "journal"
new_dois:
  - "10.3390/electronics12071632"
  - "10.3390/jrfm18080412"
---

## CORE

【构念与来源】
本家族的正确构念名称应读作"IDF 语调分的媒体权威加权求和" (idf_score, media-weighted, sum), 而不是望文生义的"逐个匹配词的加权求和"。列名后缀 mw 在本仓库源码注释里明确写作 media-weight (媒体权威性加权), 出处直接标注为 Holzman, Miller & Twedt (2023, *The Accounting Review*): 该文发现不同媒体来源在盈余公告等公司信息事件中的情感报道对市场反应的约束力不同, 权威性/影响力更高的媒体来源发出的情感信号应赋予更大权重。本家族把这一思想应用到银行-金融科技共现报道上: 先按 yao_2021 中文金融情感词典对每篇报道做逆文档频率 (IDF) 加权的语调打分 (下称 idf_score), 得到一个已经完成篇级聚合的单一数值; 再把该数值乘以这篇报道所属媒体来源的权威性权重 (media_authority_weight), 得到本列真正的构造对象 idf_score_mw。换言之, mw 加权发生在"篇"这一层, 加权对象是整篇文章的 IDF 语调分, 而不是发生在"词"这一层去逐个给命中词乘权重再求和——文档本身没有"匹配词各自的媒体权威权重"这回事, 媒体权威性是报道来源 (outlet) 的属性, 与文章内部具体命中了哪些情感词无关。
IDF 加权本身 (即 idf_score 这一底层构念) 才是继承 Spärck Jones (1972) 对词项特异性 (term specificity) 统计诠释的部分: 对某个情感词在全体语料中出现得越普遍, 其对语调判断的边际贡献 (区分力) 越弱, 边际权重就越低, 反之罕见但高辨识度的情感词获得更高权重, 该框架后来被检索式 TF-IDF 广泛采用。Jegadeesh & Wu (2013) 的 word power 方法是"不对所有命中词一视同仁"这一思路在金融文本情感测度中的代表性先例, 与本家族的 IDF 加权在方法论精神上同源, 但权重来源不同 (Jegadeesh & Wu 用价格反应校准权重, IDF 用纯语料统计, 不掺入结果变量信息)。但必须区分: IDF 加权是"词"层面的操作 (决定 idf_score 怎么算), 媒体权威加权是"篇/来源"层面的操作 (决定 idf_score 如何再被放大或压低), 两者叠加才构成 idf_score_mw 这一复合测度, 是词典法与媒体来源可信度两条独立加权逻辑的串接, 而非同一层面的两次加权。
本列在面板层的真实身份是分子中间列, 不是可直接解读的均值化语调测度: 面板聚合把银行-年内全部合格报道的 idf_score_mw 求和 (SUM, 而非取均值) 得到 idf_score_mw_sum, 随后下游再除以该组内媒体权威权重之和 (sum_media_authority_weight) 才得到均值化、媒体权威加权后的语调测度 idf_tone_mw。因此本家族 (idf_score_mw_sum) 本身承载的是"分子": 它随该银行-年报道篇数与各篇媒体权威权重的乘积规模增长, 不能脱离分母单独解读为"该银行-年的平均语调水平"——若需要跨银行-年可比的加权语调水平, 应查阅 idf_tone_mw 而非本列。
yao_2021 词典本身是中文金融文本情感分析中与 jiang_2021、bian_2021、du_2022、you_2018、loughran (LM 中文译本) 并列的六部词典之一, 在 config/codebook_longdesc 体系中作为"词典消融梯度"(见 CLAUDE.md「词典消融梯度」条款) 的一员参与语言学规则全 powerset 消融检验; 但本家族 (idf_score_mw_sum) 的媒体权威加权维度与该消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 完全正交——媒体权威加权是在"该篇 idf_score 算出来之后如何按来源可信度再加权求和"这一新增维度, 与"用哪些语言学规则判定命中词极性"是两个互不相关的选择, 本仓库当前未落地两者的交叉组合, 与政治词权重敏感性 (du_2022 专属) 类似地保持"新增维度不与既有梯度交叉爆炸列数"的克制原则。

【方法学与计算】
计算横跨两个阶段、两个不同模块, 需分层理解。第一层 (词典扫描, `22_tone_words.py` 调用的 `pipeline/sentiment/tone_words.py`): 该模块内的 IDF 加权稳健性检验环节在源码注释中反复明确标注方法学出处为 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 对"文本作为数据"(text as data) 一文中§2.2 的 TF-IDF 加权处理规范, 而非仅溯源到检索式 IDF 的最初奠基文献——两者并不矛盾, Spärck Jones (1972) 是逆文档频率这一统计量本身的最初提出者, Gentzkow-Kelly-Taddy (2019) 则是把该统计量系统引入经济学文本分析 (text-as-data) 方法论综述并给出计量经济学场景下的具体加权规范 (如重复文章对文档频率 df(w) 的膨胀问题应如何处理) 的更贴近当代实现的直接出处; 本仓库源码的 IDF 加权稳健性检验环节明确以后者作为其计算规范的直接依据, 因此本节将两篇文献并列标注, 不以早期奠基文献替代当代直接出处。对每篇报道的三条文本轨 (`content_full`/`content_ctx`/`content_ss`, 由 stage 14 `14_materialize_ctx` 物化, 均已 `prepend_title`) 逐轨独立分词、逐轨独立与 yao_2021 词典做词项匹配、逐轨独立应用否定翻转/程度副词/转折等语言学规则判定每个命中词的最终极性, 再计算全体入样报道集合上的逆文档频率, 对篇内命中词的贡献 (IDF(w)×polarity(w)) 求和得到该篇该轨的 idf_score{trk} (与 mw 后缀无关的中间产物, 本身不落本家族的列名)。第二层 (媒体权威加权, `pipeline/panel/runner.py`): `compute_media_authority_weights` 依据报道来源媒体列做权威性/影响力分层, 产出 `media_authority_weight` 列 (缺失来源信息时优雅退化为 1.0, 即等权 EW, 此时 mw 加权名义上存在但实质上等价于裸计数, 日志会提示"多数落默认权重, MW Tone 接近等权"); 随后 `weighted_cols[f'{d}_idf_score_mw{track}'] = df[src_idf] * mw`, 即用该篇所属媒体的权威权重乘以该篇已经算好的 idf_score{trk}, 得到 idf_score_mw{trk} 这一篇级复合数值。第三层 (面板聚合, `pipeline/panel/encode.py`): 按银行-年分组对 idf_score_mw{trk} 做 SUM (而非 mean), 得到本家族列 `yao_2021_idf_score_mw_sum_{trk}`; 同一聚合流程还并行产出该组的 `sum_media_authority_weight` (媒体权威权重本身的组内加总), 下游再用 `idf_score_mw_sum{trk} / sum_media_authority_weight` 得到均值化的 `{d}_idf_tone_mw{trk}` 列 (该除法列不属于本家族)。三条文本轨在词典扫描层各自独立扫描、独立聚合, 媒体权威权重层不分轨 (`media_authority_weight` 是报道级、非轨道相关的属性, 三轨共享同一权重), 这是仓库贯彻的三轨架构铁律在"词典扫描"环节的体现, 而权重叠加环节本身与轨道选择无关。
留篇门控 (`llm_verified_full == True`, 2026-06-29 起口径为 full-only, 详见 CLAUDE.md「留篇门控」条款) 决定哪些文章进入该银行-年的求和范围: 是否计入分母由 full 轨的 LLM 判定结果决定, 与轨道无关; ctx/ss 两轨的 idf_score_mw_sum 是在 full 门控确定的行宇宙 (row universe) 子集上按各自轨的文本重新扫描词典、再乘同一份 media_authority_weight、再求和得到的条件测度 (conditional-on-full), 因此 ctx/ss 的样本量口径与 full 一致 (同一批文章), 但文本窗口带来的命中词集合、IDF 权重取值不同, 媒体权威权重本身相同。
`_ss` 轨遵循与 `_ctx` 轨镜像的回退语义: 当一篇文章不存在银行与金融科技词在同一句 (±N 窗口, 默认 N=1, `config/filtering.yaml::context_window.ss_sentence_radius`) 共现的情形时, `content_ss` 回退为全文正文 (与 `content_full` 相同), 对应的 `ss_is_fallback` 标记为 True; 该情形下该篇的 `_ss` 轨 idf_score 实质上退化为对全文扫描的结果, 与 `_full` 轨数值上可能一致, 但两者在面板聚合分母 (`n_articles`) 的记账上共享同一行, 不会因回退而产生额外的孤儿列或分母不一致问题。当上游金融科技关键词自动扩展 (`FINTECH_AC`) 未成功构建 (`FINTECH_AC=None`) 时, 全部 `*_is_fallback` 标记优雅降级为 True, 三轨退化为等价扫描, 不会导致管道崩溃。

【文献定位】
本家族在方法论谱系上横跨三条独立传统。一是中文金融情感词典构建传统, yao_2021 词典与 jiang_2021、bian_2021 (Bian, Jia, Li & Yan, 2021)、du_2022 (Du, Huang, Wermers & Wu, 2022, *Review of Finance*) 同属"面向中国资本市场文本定制"的第二代金融情感词典, 相对 Loughran & McDonald (2011) 原版英文词典的直接翻译移植, 更贴合中文财经报道的语用习惯与套话结构。二是词项加权/信息检索传统, 该传统的奠基性文献是 Spärck Jones (1972) 对逆文档频率的统计诠释, 她首次给出了"词项在区分文档方面的信息量应与其文档频率成反比"这一命题的形式化论证, 是当代 TF-IDF 检索权重的最初理论源头; 但本家族底层 idf_score 的计算规范在源码层面更直接的方法学出处是 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 对文本作为数据 (text as data) 这一方法论的系统梳理——该文§2.2 专门讨论了 TF-IDF 加权在经济学文本分析场景下的规范实现 (包括重复文档对文档频率的膨胀问题), 本仓库 IDF 加权稳健性检验环节的代码注释反复以此文作为直接依据; Spärck Jones (1972) 与 Gentzkow-Kelly-Taddy (2019) 因此构成本家族 IDF 加权方法学的"奠基-当代实现"两层出处, 而非互相替代关系。Jegadeesh & Wu (2013, *Journal of Financial Economics*) 的 word power 方法把类似"不同权重"的思路引入金融文本分析, 尽管其权重校准方式 (基于历史价格反应) 与本家族的纯语料统计权重不同, 但两者共同代表了词典法情感分析从"简单计数"向"信息量加权"演进的方法论趋势。三是媒体来源可信度加权传统, 这是本家族 mw 后缀真正的方法学出处: Holzman, Miller & Twedt (2023, *The Accounting Review*) 研究媒体情感对季度盈余公告披露约束作用的强化机制, 论证了不同媒体来源的权威性/覆盖广度会系统性影响其情感报道对市场行为的解释力, 因而在跨来源加总情感信号时应按来源权威性加权而非等权处理; 本家族的 media_authority_weight 正是把这一"来源分层加权"思想移植到银行-金融科技共现报道语料, 与 IDF 加权 (词层面) 相互独立、共同构成 idf_score_mw 的复合权重结构。Barbaglia et al. (2025, *Economic Inquiry*) 系统评述了基于词典的经济文本情感分析方法, 其中专门讨论了词项加权方案对测度稳健性的影响, 为本家族底层 idf_score 的加权设计提供当代方法论参照; Frankel, Jennings & Lee (2022, *Management Science*) 对比机器学习与词典法两条情感测度路线, 为本仓库同时保留裸计数、IDF 加权、媒体权威加权、LLM 三家投票、BERT 三模型等多条并行情感测度路线提供方法论合理性——各路线互为稳健性检验对象, 而非相互替代。Alshehri & Algarni (2023, Electronics) 提出一种新的监督式词项加权方案 TF-TDA 用于情感分析, 与本家族 IDF 词项加权的方法论精神一致, 均主张对情感词按信息量/区分力差异化赋权而非等权计数。Davidovic & McCleary (2025, Journal of Risk and Financial Management) 对新闻情感与股市动态的机器学习研究发现新闻内容中仅小部分承载主观情感信息, 为本家族对报道来源可信度/权威性加权处理稀释信号问题提供当代实证参照。
就本仓库内部定位而言, idf_score_mw_sum 与家族内 score_hw_sum (标题词加权求和)、score_w_sum (裸计数求和)、score_std (标准差) 等姊妹测度共同构成 yao_2021 词典命中信号的多角度切片, 与政治词权重敏感性梯度 (du_2022 专属, {0.0, 0.5, 1.0} 三档) 及词典消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv 七变体) 均属"互为稳健性、不分主次"的并列关系。铁律: 三条文本轨 (full/ctx/ss) 各自 just-identified 并排使用, 严禁将其混入同一个 over-identified 的 Hansen J 过度识别检验, 这是仓库对三轨测度体系的统一约束, 适用于本家族全部三列; 同理, media_authority_weight 与其他权重方案 (若未来引入) 也应各自 just-identified 并排, 不预设 mw 加权优于等权版本。

## VAR: yao_2021_idf_score_mw_sum_ctx

【变体差分】
本列是 idf_score_mw_sum 家族的实体窗轨 (ctx) 实现: 词典扫描层的篇级文本为 `content_ctx`, 即标题加银行/金融科技实体周边窗口 (而非全文正文), 由 stage 14 `14_materialize_ctx` 在 `prepend_title` 规则下物化; ctx 轨的 idf_score (词典层输出, mw 加权前) 命中词集合天然是 full 轨的子集或不同切片 (窗口更窄, 部分情感词可能落在窗口外而不被计入), IDF 权重也因该轨自身命中词集合的统计口径不同而与 full 轨取值不同。媒体权威权重 (media_authority_weight) 不分轨——它是报道来源的属性, 三轨共享同一份权重, 因此 ctx 与 full/ss 三轨在"乘以媒体权威权重"这一步骤上完全相同, 差异只来自词典扫描层各轨独立算出的 idf_score 不同。面板聚合同样是 SUM 而非 mean: 本列 = 该银行-年内全部留篇报道 ctx 轨 idf_score_mw 之和, 是分子列, 需除以同组 sum_media_authority_weight 才得到 ctx 轨的均值化媒体权威加权语调 (该除法结果属于 idf_tone_mw_ctx, 不在本家族)。样本行宇宙 (哪些文章参与求和) 与 full 轨完全一致, 因为留篇门控只看 full 轨判定; ctx 轨仅是在该行宇宙上重新扫描 `content_ctx` 后的条件测度稳健性轨, 用于检验"媒体权威加权后的语调结论是否对文本窗口宽窄敏感"。本列与 `_full`、`_ss` 两列各自独立聚合、并排使用, 不构成同一过度识别方程中的工具变量集合。在稳健性叙事中, 若某一结论在 full 轨显著而在 ctx 轨消失或方向反转, 应被解读为"结论对文本窗口宽窄敏感", 而非直接判定 ctx 轨测度失效——两轨各自反映了不同的构念侧面 (全篇媒体权威加权语调 vs 实体近邻语境媒体权威加权语调)。

## VAR: yao_2021_idf_score_mw_sum_full

【变体差分】
本列是 idf_score_mw_sum 家族的全文轨 (full) 实现, 也是仓库当前 (2026-06-29 起) 留篇门控与多数 P1/P3 类主处理变量测度所依赖的行宇宙基准轨: 词典扫描层的篇级文本为 `content_full`, 即标题加全文正文, 命中词集合覆盖该篇报道的完整文本内容, 因而是三轨中信息覆盖面最宽、受窗口截断影响最小的版本, 该 idf_score 随后乘以该篇所属媒体的权威权重 (与轨道无关, ctx/ss 共享同一权重值) 得到 idf_score_mw_full。是否将一篇文章计入某银行-年的求和范围完全由 full 轨的 LLM 判定结果 (`llm_verified_full == True`) 决定, 因此本列的样本行宇宙即为该银行-年全部合格报道的行宇宙本身, ctx/ss 两轨在同一行宇宙上做条件测度。本列同样是 SUM (分子列): 需除以同组 sum_media_authority_weight 才得到均值化的 idf_tone_mw_full。就 IDF 权重而言, full 轨的命中词集合最大, 覆盖的稀有情感词种类也最多, 但也最容易受正文中与银行-金融科技主题无关的段落引入的噪声词干扰。本列与 `_ctx`、`_ss` 两列在测度设计上互为稳健性对照, 不设主次之分, 但作为行宇宙锚点承担着门控职责, 这一点是 full 轨相对另两轨的结构性特殊之处 (而非语义优先级上的特殊之处)。具体研究是否将本列 full 变体设为主设定, 应由各 paper 自身的 treatment 定义决定, 三轨在本家族内部严格并排, 不预设某一轨为"更优"版本。

## VAR: yao_2021_idf_score_mw_sum_ss

【变体差分】
本列是 idf_score_mw_sum 家族的同句轨 (ss, sentence-same) 实现: 词典扫描层的篇级文本为 `content_ss`, 判定原语为银行实体与金融科技词是否在同一句 (±N 窗口, 默认 N=1) 严格共现, 是三轨中文本窗口最窄、判据最严格的版本, 意在捕捉"情感表达确实紧邻银行-金融科技共现语境"的最保守测度。当一篇文章不满足严格同句共现条件时, `content_ss` 回退为全文正文 (镜像 `_ctx` 轨的回退语义), 对应 `ss_is_fallback=True`, 该情形下本列的 ss 轨 idf_score 与 `_full` 轨可能重合, 但仍与 `_full`/`_ctx` 共享同一行宇宙、同一分母 `n_articles`, 不产生单边孤儿列。媒体权威权重同样不分轨, ss 轨与 full/ctx 轨乘的是同一份 media_authority_weight, 差异只来自该轨自身词典扫描算出的 idf_score 不同。本列同样是 SUM: 该银行-年内全部留篇报道 ss 轨 idf_score_mw 之和, 需除以同组 sum_media_authority_weight 才得到均值化的 idf_tone_mw_ss。由于严格同句窗口进一步压缩了命中词数量, 本列数值方差在小样本 (如仓库当前 T=2 开发盘) 下可能出现较多零值或与 full/ctx 轨高度重合的退化表现, 属预期而非缺陷, 生产全量语料 (T=18) 规模下应能呈现更充分的区分度。本列与 `_full`、`_ctx` 两列并排互为稳健性, 禁止混入同一过度识别 Hansen J 方程。需要额外提醒: `_ss` 与 `_ctx` 的回退语义虽然镜像 (均在共现条件不满足时退化为全文), 但两者的触发判据不同——`_ctx` 依赖的是实体窗口宽度设定, `_ss` 依赖的是严格同句共现的判据 (`entity_context.py` 中的逐句扫描原语), 因此同一篇文章可能 `_ctx` 未回退而 `_ss` 回退 (窗口内但不同句), 两个 fallback 标记不必然同步, 使用时应分别检查 `ctx_is_fallback` 与 `ss_is_fallback` 而非假定二者等价。

<!-- rendered-citations:begin -->
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Jegadeesh, N., & Wu, D. (2013). Word power A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment Machine learning vs dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Alshehri, A., & Algarni, A. (2023). TF-TDA: A Novel Supervised Term Weighting Scheme for Sentiment Analysis. Electronics. https://doi.org/10.3390/electronics12071632
Davidovic, M., & McCleary, J. (2025). News Sentiment and Stock Market Dynamics: A Machine Learning Investigation. Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm18080412
<!-- rendered-citations:end -->
