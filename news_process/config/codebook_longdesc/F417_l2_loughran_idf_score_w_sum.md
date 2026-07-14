---
family_id: F417
columns:
- loughran_idf_score_w_sum_ctx
- loughran_idf_score_w_sum_full
- loughran_idf_score_w_sum_ss
unit: 无量纲加权得分之银行-年内加总 (IDF 加权语调净值的篇内加权求和)
formula: 'sum_i( w_i * loughran_idf_score_i ), 其中 loughran_idf_score_i 为逐篇净语调分, 已在词项层由
  tone_words.py::build_idf_weights 按 IDF (逆文档频率, 稀有词加权, log10(N/(1+df(w))) 口径) 对 loughran_mcdonald_zh_2026
  词典 (L&M 2011 中文主译本) 命中词条加权得到; w_i 是叠加在其上的第二层权重, 取该篇的 mention_density (提及密度/关注度加权,
  与稀有度 IDF 权重是两个不同构念), 于 pipeline/panel/runner.py 预计算为 {dict}_idf_score_w{track} 列; 加总在银行-年单元内对该年
  (full/ctx/ss 各自口径下) 所有留篇样本求和, 而非取均值'
producer: pipeline/sentiment/tone_words.py ; pipeline/panel/runner.py ; pipeline/panel/encode.py
upstream: []
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35–65
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: Word power - A new approach for content analysis
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712–729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11–21
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: Language and domain specificity - A Chinese financial sentiment dictionary
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673–719
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: 'Textual analysis in accounting and finance: A survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187–1230
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514–5532
- doi: "10.1111/jofi.13219"
  title: "Firm-Level Climate Change Exposure"
  authors: "Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R."
  year: 2023
  venue: "The Journal of Finance"
  type: "journal"
  one_sentence_zh: "该文以词项在句子窗口内与目标关键词的邻近共现频率构造企业层面暴露度测度, 与本家族 mention_density/同句窗口加权求和的方法学思路同源, 均属关注度/邻近度加权而非稀有度加权的文本测度设计。"
new_dois:
  - "10.1111/jofi.13219"
---

## CORE

【构念与来源】
本家族测度的是「银行-年」单元内, 基于 Loughran & McDonald 中文主译本词典 (loughran_mcdonald_zh_2026, 配置 SSOT 见 config/tone_dicts.json) 计算的逐篇净语调分, 经两层不同构念的权重先后作用后在该单元的年度报道集合内求和得到的加总语调指标。第一层权重发生在词项层面: tone_words.py::build_idf_weights 在与 TF 同一语料上按 IDF (逆文档频率, inverse document frequency, log10(N/(1+df(w))) 口径, 均值归一后 P1/P99 Winsorize) 对词典命中词条加权, 产出逐篇的 `{dict}_idf_score{track}` 列——这才是本家族名字里"idf"的真正来源: 用「稀有词/信息密度」加权取代对每一词条等权计数的朴素求和, 使罕见、专属性强的措辞在单篇语调分中获得更高相对权重。第二层权重发生在篇章层面, 且与 IDF 无关: pipeline/panel/runner.py 以该篇的 mention_density (提及密度/关注度) 作为标量 w_i, 对上述已含 IDF 加权的 `{dict}_idf_score{track}` 再做一次加权, 得到 `{dict}_idf_score_w{track}`, 最终由 encode.py 在银行-年单元内求和为本家族三列。mention_density 加权在源码注释中被明确标注为呼应 Hassan et al. (2019, Quarterly Journal of Economics)「Firm-Level Political Risk」一文提出的 value-weighted exposure (VW, 关注度加权) 构造思路——即一篇报道对目标银行的提及越密集/越突出, 其对该银行-年加总语调的贡献权重越大, 这是关于"这篇报道有多聚焦于目标银行"的关注度构念, 而不是关于"这篇报道用词有多稀有"的信息稀有度构念; 二者在计算链路上前后相继、但经济学含义彼此独立, 不可混为一谈。词典本身源自 Loughran & McDonald (2011) 对 10-K 文本分析中通用情感词典 (如 Harvard-IV) 系统性误判金融语境词汇极性问题的开创性诊断——该文指出许多在日常语境中带负面色彩的词 (如 "tax"、"cost"、"liability") 在金融披露文本中往往是中性甚至常规表述, 由此发展出面向金融文本的领域专属词典; 本仓库使用的 loughran_mcdonald_zh_2026 是该词典体系的中文主译本, 含 positive(1,295) / negative(3,729) 两大极性类别, 另含 5 类非极性词类 (不确定性/诉讼/弱模态/强模态/受限等, 未计入本家族净语调分)。IDF 权重的统计学基础可追溯至 Spärck Jones (1972) 对词项区分度的经典阐释——词项在语料中出现得越稀少, 其对文档主题/立场的区分力越强; 本家族名字里的 idf 严格锚定在这一词项层含义上, 与 mention_density/VW 加权在同一列名内叠加但不同源。词典消歧口径遵循用户 2026-06-24 决策: loughran 词典原始 61 个跨类重叠词经两侧保留判断, 38 词已归单侧, 余 23 词因不可约简而在 positive/negative 两侧同时保留计数 (对称两侧计入, 非武断选边、非静默单极判负), 详见 config/tone_dicts.json::loughran 的 _description 字段。三轨 (full/ctx/ss) 铁律: full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定; 三者共享同一词项 IDF 权重计算原语、同一 mention_density 加权口径与同一词典配置, 差异仅在于喂入打分的文本窗口不同 (详见各 VAR 节)。

【方法学与计算】
本家族的计算分三层: 第一层是 pipeline/sentiment/tone_words.py 中逐篇的 loughran_score 计算——对每篇文章 (在其对应轨道的文本窗口内) 匹配 loughran_mcdonald_zh_2026 词典的正/负词条, 得到该篇净语调分 (正面计数与负面计数经净化/归一处理后的差值口径, 与家族内其余词典族如 jiang_2021/yao_2021/bian_2021/du_2022/you_2018 共享同一计算框架, 仅词典内容不同); 第二层仍在 tone_words.py 内, 由 build_idf_weights 对命中词条按其在全语料的文档频率施加 IDF 权重, 产出 `{dict}_idf_score{track}` (这是本家族"idf"字样的唯一出处, 完成于篇章打分之前的词项层面); 第三层转到 pipeline/panel/runner.py, 对每篇报道依据其 mention_density (提及密度, 与该篇讨论目标银行的密集程度相关, 与词项稀有度无关) 计算一个标量权重 w_i, 再以 w_i 为权重对该银行-年单元内所有留篇样本的 `{dict}_idf_score{track}` 做加权求和 (sum, 非加权均值), 由 encode.py 落盘为本家族三个轨道列的最终数值。求和 (而非取均值) 的选择使该指标同时承载了「语调方向」「词项信息密度」与「报道对目标银行的关注度/规模」三重信息——一个银行-年若报道数量多、措辞信息密度高且报道对该银行的提及密集, 其加总值会系统性高于报道稀少、模板化或提及稀疏的银行-年, 这与家族内以均值为口径的语调测度 (如 avg_ 前缀族) 构念上互补而非替代, 使用者在解读时须注意本家族数值天然与 n_articles、词汇丰富度及 mention_density 三者相关, 不宜脱离样本规模直接跨单元比较水平值。留篇门控口径遵循 2026-06-29 起生产铁律: 是否判定为「一篇银行金科报道」的门控只看 full 轨的 LLM 验证结果 (llm_verified_full == True); ctx/ss 轨的行宇宙是 full 轨留篇集合的子集, 在此子集上各轨分别计算并加总各自的词项 IDF 加权 + mention_density 加权语调分, 定位为 conditional-on-full 的测度/稳健性轨, 而非独立的样本扩展。词项 IDF 加权、mention_density (VW) 加权与朴素平均之间的关系是「互为稳健性」而非「谁更优」: 词典法本身的可复现性和透明度是其相对于机器学习/LLM 方法的核心优势 (Frankel, Jennings & Lee 2022 对比了机器学习与词典法在披露语调测度上的分歧与互补性), 本家族只是在该框架内叠加了两层关于文档信息密度与关注度规模的稳健性检验, 与词典消融梯度 (七种语言学规则子集变体) 正交、不交叉——不应把这些梯子混入同一维度做联合识别。

【文献定位】
本家族的方法学谱系直接承接 Loughran & McDonald (2011, *The Journal of Finance*) 建立的金融领域专属词典范式——该文是文本分析在会计与金融领域应用的奠基性工作, 系统证明了通用情感词典在金融披露文本上的系统性偏误, 并催生了此后十余年会计金融文本分析文献对领域词典的广泛采用 (综述见 Loughran & McDonald 2016, Journal of Accounting Research, 详述了文本分析方法论在会计金融研究中的演进脉络与常见陷阱)。词项层的 IDF 加权 (`{dict}_idf_score{track}`) 呼应了 Jegadeesh & Wu (2013, Journal of Financial Economics) 提出的"word power"框架——该文论证了并非所有词典词条对市场反应的解释力均等, 应当依据词项的信息含量赋予差异化权重, 而非将词典视为等权计数器; IDF 概念本身则可回溯至 Spärck Jones (1972) 对信息检索中词项区分度的经典统计学阐释, 是本仓库多处 IDF/TF-IDF 相关测度族的共同数理基础。叠加在其上的篇章层 mention_density 加权求和 (`_w_sum` 后缀), 其经济学定位不是稀有度加权, 而是关注度/规模加权——一篇报道对目标银行的提及越密集, 该篇对银行-年加总语调的贡献权重越大, 这一构造思路与 Hassan, Hollander, van Lent & Tahoun (2019, *Quarterly Journal of Economics*) 「Firm-Level Political Risk」一文中按提及频率对文本片段赋权、构造 value-weighted exposure 测度的做法在方法论上同源, 但该文本身不在本仓库文献引注白名单池内, 故此处仅作方法学溯源的文字说明, 不列入结构化 citations。中文语境下的应用还须考虑领域词典跨语言迁移问题: 本仓库另有 du_2022 (Review of Finance) 等专为中文金融文本构建的词典, 与 loughran 的英文原典中译本形成互为稳健性的多词典并排设计, 体现"多词典互证"而非依赖单一词典结论的审慎立场。词项 IDF 加权 + mention_density 加权求和与机器学习/词嵌入类语调测度之间的关系亦须审慎处理: Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习与词典方法在披露语调测度上的表现差异, 提示词典法的透明度优势与机器学习法的适应性优势各有取舍, 本仓库据此将词典法 (含本家族的两层加权变体)、LLM 三家投票法、BERT 三模型法设计为三条互为稳健性、不分主次的并排测度轨, 而非试图用单一"最优"方法替代其余两条。Sautner, van Lent, Vilkov, & Zhang (2023, The Journal of Finance) 以词项在句子窗口内与目标关键词的邻近共现频率构造企业层面暴露度测度, 与本家族 mention_density 及同句窗口加权求和的方法学思路同源, 均属关注度/邻近度加权而非稀有度加权的文本测度设计。

## VAR: loughran_idf_score_w_sum_ctx

【变体差分】
本列是 loughran_idf_score_w_sum 家族在 ctx (context, 实体窗口) 轨道下的实现: 逐篇打分、词项 IDF 加权与 mention_density 加权求和所依据的文本不是全文正文, 而是 stage 14 (materialize_ctx) 物化产出的 content_ctx 列——标题 + 目标银行实体周边窗口文本 (prepend_title 拼接), 而非全文 body; 该轨的 mention_density 亦在此窗口文本上重新计算, 与 full 轨的 mention_density 不共享数值。行宇宙受 full-only 留篇门控约束: 只有在 full 轨被 LLM 判定为有效银行金科报道 (llm_verified_full == True) 的文章才进入 ctx 轨的加总, ctx 轨本身不再独立判定是否留篇, 是 conditional-on-full 的测度/稳健性轨而非独立样本扩展。回退语义 (ctx 特有, ss 轨镜像): 若某篇文章的目标银行实体窗口内未能提取到有效上下文文本, content_ctx 回退为全文 body, 并置 ctx_is_fallback=True (回退计数纳入与 full 轨共享的 n_articles 分母, 不单独另设分母)。ctx 轨与 full 轨、ss 轨三者各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定——不应将三轨语调分同时作为同一工具变量方程的多个内生解释变量并联识别。ctx 轨相对 full 轨的构念增量在于: 通过将打分文本限定在实体周边窗口, 降低了长篇报道中与目标银行无关段落 (如报道中提及的其他机构、宏观背景叙述) 对词项 IDF 加权语调分的稀释/污染, 同时该窗口内的 mention_density 更集中反映"这段文本对目标银行的聚焦程度", 理论上应更贴近"文章对该银行本身的语调倾向", 但代价是窗口提取误差 (回退率) 会引入额外噪声, 需与 full 轨对照解读、以差异幅度而非孤立水平值判断稳健性。

## VAR: loughran_idf_score_w_sum_full

【变体差分】
本列是 loughran_idf_score_w_sum 家族的 full (全文) 轨道实现, 也是三轨中承担留篇门控职责的基准轨: 逐篇打分、词项 IDF 加权与 mention_density 加权求和所依据的文本是标题 + 全文正文 (prepend_title 拼接的完整 content_full), 未做任何实体窗口截取或同句共现限定。生产口径下 (2026-06-29 起) 是否判定"这是一篇银行金科报道"的唯一依据就是本轨的 llm_verified_full 结果, ctx 轨与 ss 轨的行宇宙均是本轨留篇集合的子集; 换言之, full 轨定义了本家族三列共同的样本边界, ctx/ss 轨在此边界内各自独立打分与加总, 不借用 full 轨的分数、也不与 full 轨共享打分文本或 mention_density。词项 IDF 权重的计算基于全语料的词项文档频率分布, 全文轨天然拥有最丰富的词汇覆盖, 因此该列的 IDF 加权语调分通常在三轨中信息密度估计最稳定 (受窗口截断/回退噪声影响最小); mention_density 亦在全文范围内计算, 覆盖面最宽但也最容易被与目标银行无关的段落内容稀释或污染语调方向及关注度权重。该轨与 ctx/ss 轨严格并排, 互为稳健性、不分主次, 三者禁止混入同一 over-identified Hansen J; 与家族内非 IDF 加权、非 mention_density 加权的朴素求和/均值变体亦是互补关系, 而非彼此替代的"更优版本"。使用者若需要一个不依赖实体窗口提取质量、也不依赖同句共现判据严格程度的基准参照, 应优先以本轨作为默认报告口径, 再辅以 ctx/ss 两轨的差异幅度作为窗口设定敏感性的披露; 三轨数值若方向一致、幅度接近, 可视为语调测度对文本窗口选择不敏感的证据, 反之则须在稳健性讨论中如实披露窗口设定对结论的潜在影响, 不应择优挑选单一轨道结果对外报告。

## VAR: loughran_idf_score_w_sum_ss

【变体差分】
本列是 loughran_idf_score_w_sum 家族在 ss (same-sentence, 银行∧金科同句) 轨道下的实现: 逐篇打分、词项 IDF 加权与 mention_density 加权求和所依据的文本是 stage 14 物化的 content_ss 列——标题 + 目标银行与金科关键词落在同一句 (±N 窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 配置, 默认 1) 的句子集合拼接, 是三轨中文本窗口最窄、判据最严格的一支; 该轨的 mention_density 同样在此最窄窗口文本上重新计算, 与 full/ctx 两轨不共享数值。行宇宙同样受 full-only 留篇门控约束, 是 full 轨留篇集合的子集, 不独立判定留篇。回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, content_ss 回退为全文 body, 并置 ss_is_fallback=True, 回退行纳入与 full 轨共享的 n_articles 分母 (不单独另设分母); 若 FINTECH_AC (金科关键词自动机) 为 None, 则该批次 *_is_fallback 全部置 True, 以优雅降级方式退化为等同 full 轨的行为, 而非报错或产生空值。ss 轨与 full/ctx 轨三者各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。ss 轨相对 ctx 轨的构念增量在于判据更为严格——同句共现比"实体窗口"更逼近"这句话确实在讨论银行与金科的关联", 理论上应产生最纯粹的词项 IDF 语调信号与最聚焦的 mention_density 关注度权重, 但也意味着更高的回退率 (更多文章无法满足同句共现条件而退化为全文口径), 因此该轨的样本有效性 (非回退占比) 须结合具体年份/银行的报道语料特征解读, 不宜脱离回退率孤立比较三轨数值差异的经济含义。
<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35–65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Jegadeesh, N., & Wu, D. (2013). Word power - A new approach for content analysis. Journal of Financial Economics, 110(3), 712–729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11–21. https://doi.org/10.1108/eb026526
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity - A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673–719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187–1230. https://doi.org/10.1111/1475-679X.12123
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514–5532. https://doi.org/10.1287/mnsc.2021.4156
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-Level Climate Change Exposure. The Journal of Finance. https://doi.org/10.1111/jofi.13219
<!-- rendered-citations:end -->
