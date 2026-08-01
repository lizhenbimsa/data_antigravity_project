---
family_id: F415
columns:
- loughran_idf_score_hw_sum_ctx
- loughran_idf_score_hw_sum_full
- loughran_idf_score_hw_sum_ss
unit: 无量纲加权得分之和 (herd-weighted 情感得分在银行-年内的求和分子, 无量纲)
formula: "loughran_idf_score_hw_sum{track} = Σ_{i∈bank-year} ( loughran_idf_score{track}_i × herd_weight{track}_i ); 其中 article 级 loughran_idf_score{track} = normalize( Σ token final 极性 × idf_weight ), idf_weight(w) = Winsorize( log10(N/(1+df(w))) / mean_{w'∈dict(w)}(raw_idf(w')), P1, P99 ); 均值归一化以 loughran_mcdonald_zh_2026 词典自身的 raw_idf 均值为除数 (per-dictionary), 非跨全体六部词典情感词的单一均值"
producer: news_process/pipeline/panel/encode.py::build_aggregation_dict (聚合 sum) ; news_process/pipeline/sentiment/tone_words.py::build_idf_weights + compute_sentiment_features (article 级 idf_score) ; news_process/pipeline/sentiment/herd_decay.py (herd_weight)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_idf_score{track})
- 24_herd_decay_processor 产 herd_weight{track}
- 40_panel_export_main (银行-年聚合)
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: "10.1016/j.econlet.2026.113002"
  type: "journal"
  authors: "Nakatsuka, H., & Suimon, Y."
  year: 2026
  title: "How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures"
  venue: "Economics Letters"
  vol: "265"
  pages_or_artno: "113002"
---

## CORE

【构念与来源】
本家族三列 (loughran_idf_score_hw_sum 的 full/ctx/ss 三轨) 是银行-年面板层的一个求和型中间量: 它把每篇报道用 loughran_mcdonald_zh_2026 词典 (Loughran & McDonald 2011 十–K 情感词典的中文主译本) 算出的 IDF 加权语调得分, 先按羊群衰减权重 (herd weight) 逐篇缩放, 再在同一银行-同一年度的报道集合内求和。换成大白话: 先给每篇新闻打一个"这篇报道对该银行是偏正面还是偏负面"的情感分, 打分用的词典是把 Loughran 与 McDonald (2011) 为美国十–K 文件编制的英文金融情感词典翻译并本土化后的中文主译本 (词典列前缀别名 loughran, positive 1,295 词 / negative 3,729 词, 另含五类非极性词类), 并对词典里每个情感词按其"稀有程度"(IDF) 加权, 让"违约""挤兑"这类罕见而信息量大的词说话更重、"发展""提高"这类几乎逢文必现的词说话更轻; 然后再乘上一个介于零到一之间的羊群折扣因子, 把疑似互相抄稿、跟风转载的报道压低权重; 最后把一个银行一年内所有报道的"加权得分"直接加总, 得到本列。需要强调的是, 本列是一个分子 (numerator) 量, 而非最终的加权平均语调: 真正可解释的 herd-weighted 平均语调 = 本列 ÷ 同银行同年的羊群权重之和 (sum_herd_weight)。把分子单独落列, 是为了让下游 Stata 端能自由地重组分母、做加权口径的稳健性检验, 也让审计层能逐块核对分子分母的一致性。数据来源链条为: stage 14 物化三轨文本 (content_full / content_ctx / content_ss) → stage 22 tone_words 在每篇报道上算出 article 级 loughran_idf_score{track} → stage 24 herd_decay 产出每篇每轨的 herd_weight{track} → 面板导出阶段 encode.build_aggregation_dict 以 sum 聚合规则生成本列。词典本身溯源 Loughran 与 McDonald (2011) 建立的英文金融情感词典谱系, 经中文主译并本土化扩充后成为项目六部中文情感词典之一, 是本家族区别于 jiang_2021、yao_2021、bian_2021、du_2022、you_2018 五部本土原生中文词典的构念根: 后五部是直接面向中文金融/通用语料构建, loughran 一支则携带 L&M 十–K 分类学 (positive/negative 之外另含 uncertainty/litigious/constraining 等五类非极性词类) 经翻译落地, 二者语义来源不同但同属"词典法情感测度"这一大类, 各自 just-identified 并排、互为稳健性、不分主次。加载阶段对 positive∩negative 跨类重叠词 (loughran 原 61 词经 2026-06-24 消歧, 38 词已归单侧、余 23 词不可约简保留) 采取"两侧保留"而非剔除, 即重叠词同时计入 pos/neg 两侧计数, 该决定不改变本列的加权求和口径, 仅影响底层逐词极性判定的边界处理。

【方法学与计算】
计算分三层。第一层是 IDF 权重的语料级估计: 对全语料按唯一文档去重 (以文本内容自身为键, 避免"一篇提到八家银行被展开成八行"虚增文档数), 令 raw_idf(w) = log10(N / (1 + df(w))), 再逐词典 (per-dictionary) 各自求本部词典内全体情感词 raw_idf 的均值, 以该词典自身的均值为除数做归一化 (loughran 词典的每个词除以 loughran 词典内部 raw_idf 均值, 而非跨全体六部词典情感词的单一总均值——源码 tone_words.py 对 dictionaries 逐部循环, 每部先算 mean_val 再归一), 最后对归一化值做 P1/P99 Winsorize 截尾, 得到每个情感词的最终 IDF 权重。逐词典均值归一化的目的是让每部词典 IDF 加权后的得分量级各自与该词典等权版大体相当, 从而各词典轨共享同一套阈值; 采用词典内均值而非全体均值, 是因不同词典的稀有度分布与词表规模不同, 用各自的分布中心归一才能保证跨词典可比性。第二层是 article 级得分: 复用同一次 tone tokenizer 的切词结果 (零额外分词开销), 对匹配到的 loughran 情感词依次施加否定翻转、程度副词缩放、转折权重放大三条语言学规则 (遇句末标点重置作用域), 用 IDF 权重缩放各词的 final 极性幅值后归一化, 得到 loughran_idf_score{track} ∈ 有界区间; IDF 仅缩放幅值不改极性归属, 空文本或无情感词时取零或中性。第三层是羊群加权求和: 每篇乘 herd_weight{track} (stage 24 依 Tetlock 传统对疑似跟风、抄稿的报道逐篇降权, 权重落在零到一, herd_weight = 1/(1 + n_similar_articles), n_similar_articles 由同年同银行报道间 TF-IDF 余弦相似度统计), 再在银行-年内 sum 聚合成本列。方法学上须复述三轨铁律: full / ctx / ss 三条轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一条 over-identified 的 Hansen J 过度识别检验。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行的报道宇宙, 只看 full 轨的 LLM 留篇判定; ctx / ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的得分与羊群权重仍逐轨独立计算。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 的 fallback 契约一致。三轨共享同一份基于 content_full 语料估得的 IDF 权重, 绝不按轨分语料重估——ss 轨也复用此权重。

【文献定位】
本列的方法学谱系有三支来源。词典构念锚是 Loughran 与 McDonald (2011) 在 The Journal of Finance 上确立的"何时负债不是负债"框架: 他们证明通用情感词典 (如 Harvard-IV) 在金融文本上系统性误判 ("tax""liability" 等词面负面实为中性财务术语), 据此从十–K 文件出发构建了面向金融文本的情感词表分类学 (positive/negative 之外另设 uncertainty/litigious/constraining 等类); 该谱系其后经 Loughran 与 McDonald (2016, 2020) 的综述性文献进一步确立为文本分析在会计与金融领域的方法论主干, 本项目将其中译本土化正是承接这一脉络、把英文金融词典的领域特异性洞见移植到中文语境。词典跨语言移植的必要性与局限由 Du, Huang, Wermers 与 Wu (2022) 在 Review of Finance 上量化确证: 他们指出中文金融文本的语言与制度语境与英文原生语料存在系统性差异, 直译词典若不经本土化扩充与校准会损失效度, 这是本项目在 loughran 中文主译本之外, 同时并行维护 jiang_2021、yao_2021、bian_2021、du_2022、you_2018 五部中文原生词典、令六部词典互为稳健性的直接依据。IDF 加权的思想上溯 Spärck Jones (1972) 关于词项特异性的统计诠释——越稀有的词区分力越强, 这一逆文档频率原理是本列"稀有情感词加权更重"的方法根; 在金融文本分析语境中, Jegadeesh 与 Wu (2013) 的"词力量"框架示范了如何按词的信息含量而非简单计数来加权情感词, 是本列 IDF 臂的金融学先例。至于词典法本身的地位, Frankel, Jennings 与 Lee (2022) 在 Management Science 上系统比较了机器学习与词典方法的披露情感度量, 表明两类方法各有所长、互为稳健性——这正是本项目保留词典轨 (含 loughran 词典的 IDF 加权变体) 与 LLM 轨、BERT 轨并排作互证的方法论根据。羊群加权分子的设计意在把跟风转载、抄稿式报道的过度计权剥离, 使加总后的加权语调更贴近"独立信息"的口径, 与上述词典效度文献形成互补。 近期文献为这一「情感 × 新颖性」的乘性思路提供了直接旁证: Nakatsuka 与 Suimon (2026) 对日本公司披露文本联合分析文本相似度 (新颖性) 与情感, 检验市场对文本新颖性的反应, 表明二者须联合考察而非各自单独看待, 这与本列把篇级 IDF 加权语调乘以羊群衰减权重后再在银行-年内求和的分子构造同向。迁移边界须诚实标明: 原文语料为日文的公司披露文件而非第三方媒体报道, 其相似度是披露文本间的连续相似度并与情感做交互式联合分析, 并非本列 1/(1+n_similar_articles) 这一具体倒数衰减函数形式, 亦未把二者相乘折叠成单一加权分再作实体-期求和; 其层级为披露事件, 而非本列的银行-年三轨。
## VAR: loughran_idf_score_hw_sum_full

【变体差分】
本列是 full (全文) 轨, 也是本家族的首要轨与留篇门控轨。article 级 loughran_idf_score_full 依据的文本 = 标题 prepend + 完整正文 (content_full), 即对整篇报道做 IDF 加权 loughran 词典情感打分; 本列在银行-年内加总的是该全文得分乘以 full 轨羊群权重 (herd_weight_full) 之和。全文轨之所以是首要轨: 一是留篇门控采用 full-only 口径 (2026-06-29), 一篇报道是否计入该银行的报道宇宙只看 full 轨的 LLM 留篇判定, 故 full 轨的分母 n_articles 与报道宇宙定义天然对齐; 二是 IDF 权重本身就在 content_full 语料上估计, full 轨的打分与 IDF 估计语料严格同构。羊群权重按轨独立取 herd_weight_full, 即在全文 TF-IDF 相似度空间上统计的同年转抄计数所得。与 ctx、ss 两轨的关系仍是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁三轨混进同一条 over-identified 的 Hansen J。本列同样是分子量: 真正的全文轨 herd-weighted 平均语调 = 本列 ÷ sum_herd_weight_full, 分子单列的用意是让下游能自由重组分母口径并逐块审计分子分母一致性。相对 ctx/ss, full 轨纳入了完整正文语境, 信息最全但也最易被与目标银行弱相关的段落稀释, 因此与 ctx (窄语境)、ss (同句最严语境) 并排恰好构成从宽到严的语境粒度稳健性梯子。同一家族内, hw (羊群加权) 聚合与 mw (媒体加权)、w (未加权) 两种聚合方案是彼此正交的权重臂, hw 按信息独立性降权跟风报道, 三种聚合方案同样各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。实践中若主回归以 full 轨为基准, 应在稳健性表里逐轨报告 ctx 与 ss 的同名替代结果, 而不是把三轨强行塞进一条过度识别方程。

## VAR: loughran_idf_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。与 full 轨的唯一差别在于 article 级 loughran_idf_score 所依据的文本范围: ctx 轨的文本 = 标题 prepend + 实体上下文窗口 (content_ctx), 即只截取目标银行与金科实体附近的窗口文本, 而非整篇正文。因此本列在同一银行-年内加总的, 是"仅看实体邻近语境"算出的 IDF 加权 loughran 语调乘以 ctx 轨羊群权重 (herd_weight_ctx) 之和。羊群权重按轨独立: ctx 轨用 herd_weight_ctx, 不借用 full 轨权重; IDF 权重则仍复用 content_full 语料估得的同一份 (三轨共享 IDF, ctx 亦不例外)。ctx 轨在项目定位上是 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 留篇集的子集 (留篇门控 full-only), 但 per-track 的得分列照常逐轨独立计算与聚合。与 full 轨、ss 轨的关系是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁把 ctx 与 full/ss 混进同一条 over-identified 的 Hansen J。使用时应把 ctx 轨视作"窄口径语境"下对同一 loughran-IDF-羊群加权语调分子的规格稳健性变体: 若主结论在 full 与 ctx 上定性一致, 说明它不依赖于是否把无关正文段落纳入情感打分。需再次提醒本列是分子而非平均量, 单独使用无直接可解释性, 须配 sum_herd_weight_ctx 作分母还原为 ctx 轨的 herd-weighted 平均语调。早期试跑 T=2 小样本上, ctx 轨在部分银行-年可能因实体窗内无情感词而退化为零或缺失, 属预期行为, 生产 T=19 全量语料下该退化基本消失。ctx 与 full 在数值上高度相关但并非冗余: 二者差异恰好度量了"把无关正文段落纳入情感打分"这一口径选择对加权语调分子的边际影响, 因而两轨并排承载的是可审计的规格稳健性信息, 不应因相关性高而合并入同一识别方程。

## VAR: loughran_idf_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 语境粒度最严。article 级 loughran_idf_score_ss 依据的文本 = 标题 prepend + 银行与金科同句共现窗口 (content_ss, 以 config filtering ss_sentence_radius 控制的同句±N 窗为界, 默认 ±1 句), 只对目标银行与金科实体真正落在同一 (或相邻 N) 句的片段做 IDF 加权 loughran 情感打分; 本列在银行-年内加总的是该同句得分乘以 ss 轨羊群权重 (herd_weight_ss) 之和。ss 轨的回退语义镜像 ctx 轨: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 的 fallback 契约一致, 并共享 n_articles 分母口径。羊群权重按轨独立取 herd_weight_ss (不借用 full/ctx 权重), IDF 权重则仍复用 content_full 语料估得的同一份 (三轨共享 IDF, ss 亦不例外)。与 full、ctx 两轨的关系是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁把 ss 与 full/ctx 混进同一条 over-identified 的 Hansen J。ss 轨在稳健性梯子上代表"最贴近银行-金科直接语境"的极窄口径: 若主结论在 full/ctx/ss 三轨上一致, 说明它既不靠全文噪声也不靠宽窗噪声, 而是由银行与金科真正同句的表述驱动。本列同为分子量, 须配 sum_herd_weight_ss 还原为 ss 轨 herd-weighted 平均语调; 早期试跑 T=2 上因同句共现稀疏, ss 轨零值/缺失比例偏高属预期退化, 生产全量语料下同句共现样本显著增厚。使用时须结合 ss_is_fallback 标记区分真同句片段与回退全文片段, 避免把回退样本误当作严格同句证据解读; 一旦回退, herd_weight_ss 会趋近 herd_weight_full, 此为预期退化而非缺陷。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Nakatsuka, H., & Suimon, Y. (2026). How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures. Economics Letters, 265, 113002. https://doi.org/10.1016/j.econlet.2026.113002
<!-- rendered-citations:end -->
