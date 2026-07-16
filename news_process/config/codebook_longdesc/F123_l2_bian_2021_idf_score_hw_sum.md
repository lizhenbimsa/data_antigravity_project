---
family_id: F123
columns:
- bian_2021_idf_score_hw_sum_ctx
- bian_2021_idf_score_hw_sum_full
- bian_2021_idf_score_hw_sum_ss
unit: 无量纲加权得分之和 (herd-weighted 情感得分在银行-年内的求和分子, 无量纲)
formula: "bian_2021_idf_score_hw_sum{track} = Σ_{i∈bank-year} ( bian_2021_idf_score{track}_i × herd_weight{track}_i ); 其中 article 级 bian_2021_idf_score{track} = normalize( Σ token final 极性 × idf_weight ), idf_weight(w) = Winsorize( log10(N/(1+df(w))) / mean_{w'∈dict(w)}(raw_idf(w')), P1, P99 ); 均值归一化以每部词典各自的 raw_idf 均值为除数 (per-dictionary), 非跨全体情感词的单一均值"
producer: news_process/pipeline/panel/encode.py::build_aggregation_dict (聚合 sum) ; news_process/pipeline/sentiment/tone_words.py::build_idf_weights + compute_sentiment_features (article 级 idf_score) ; news_process/pipeline/sentiment/herd_decay.py (herd_weight)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_idf_score{track})
- 24_herd_decay_processor 产 herd_weight{track}
- 40_panel_export_main (银行-年聚合)
citations:
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
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
- doi: "10.1016/j.eswa.2024.125739"
  type: "journal"
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: "Expert Systems with Applications"
- doi: "10.1007/s00521-024-10603-6"
  type: "journal"
  authors: "Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y."
  year: 2024
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: "Neural Computing and Applications"
new_dois:
  - "10.1016/j.eswa.2024.125739"
  - "10.1007/s00521-024-10603-6"
---

## CORE

【构念与来源】
本家族三列 (bian_2021_idf_score_hw_sum 的 full/ctx/ss 三轨) 是银行-年面板层的一个求和型中间量: 它把每篇报道用 Bian et al. (2021) 中文金融情感词典算出的 IDF 加权语调得分, 先按羊群衰减权重 (herd weight) 逐篇缩放, 再在同一银行-同一年度的报道集合内求和。换成大白话: 先给每篇新闻打一个"这篇报道对该银行是偏正面还是偏负面"的情感分, 这个分用的是一部专门为中文会计与金融文本编制的情感词典 (Bian 2021), 并对词典里每个情感词按其"稀有程度"(IDF) 加权, 让"违约""挤兑"这类罕见而信息量大的词说话更重、"发展""提高"这类几乎逢文必现的词说话更轻; 然后再乘上一个介于零到一之间的羊群折扣因子, 把那些疑似互相抄稿、跟风转载的报道压低权重; 最后把一个银行一年内所有报道的"加权得分"直接加总, 得到本列。需要强调的是, 本列是一个分子 (numerator) 量, 而非最终的加权平均语调: 真正可解释的 herd-weighted 平均语调 = 本列 ÷ 同银行同年的羊群权重之和 (sum_herd_weight)。把分子单独落列, 是为了让下游 Stata 端能自由地重组分母、做加权口径的稳健性检验, 也让审计层能逐块核对分子分母的一致性。数据来源链条为: stage 14 物化三轨文本 (content_full / content_ctx / content_ss) → stage 22 tone_words 在每篇报道上算出 article 级 bian_2021_idf_score{track} → stage 24 herd_decay 产出每篇每轨的 herd_weight{track} → 面板导出阶段 encode.build_aggregation_dict 以 sum 聚合规则生成本列。词典本身来自 Bian, Jia, Li 与 Yan (2021) 公开的中文金融情感词典, 是本家族区别于英文 Loughran-McDonald 谱系与其余五部中文词典的构念根。

【方法学与计算】
计算分三层。第一层是 IDF 权重的语料级估计: 对全语料按唯一文档去重 (以文本内容自身为键, 避免"一篇提到八家银行被展开成八行"虚增文档数), 令 raw_idf(w) = log10(N / (1 + df(w))), 再逐词典 (per-dictionary) 各自求本部词典内全体情感词 raw_idf 的均值, 以该词典自身的均值为除数做归一化 (故 Bian 词典的每个词除以 Bian 词典内部 raw_idf 均值, 而非跨全体六部词典情感词的单一总均值——源码 tone_words.py 对 dictionaries 逐部循环, 每部先算 mean_val 再归一), 最后对归一化值做 P1/P99 Winsorize 截尾, 得到每个情感词的最终 IDF 权重。逐词典均值归一化的目的是让每部词典 IDF 加权后的得分量级各自与该词典等权版大体相当, 从而各词典轨共享同一套阈值; 采用词典内均值而非全体均值, 是因不同词典的稀有度分布与词表规模不同, 用各自的分布中心归一才能保证跨词典可比性。Winsorize 则防止某个超稀有词一词定乾坤或极高频词被压成零。三轨在这一步共享同一份基于 content_full 语料估得的 IDF 权重, 绝不按轨分语料重估——ss 轨也复用此权重。第二层是 article 级得分: 复用同一次 tone tokenizer 的切词结果 (零额外分词开销), 对匹配到的情感词施加语言学规则 (否定翻转、程度副词、转折), 用 IDF 权重缩放各词的 final 极性幅值后归一化, 得到 bian_2021_idf_score{track} ∈ 有界区间; IDF 仅缩放幅值不改极性归属, 空文本或无情感词时取零或中性。第三层是羊群加权求和: 每篇乘 herd_weight{track} (stage 24 依 Tetlock 传统对疑似跟风、抄稿的报道逐篇降权, 权重落在零到一), 再在银行-年内 sum 聚合成本列。方法学上须复述三轨铁律: full / ctx / ss 三条轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混进同一条 over-identified 的 Hansen J 过度识别检验。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入某银行的报道宇宙, 只看 full 轨的 LLM 留篇判定; ctx / ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的得分与羊群权重仍逐轨独立计算。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真。

【文献定位】
本列的三条方法学支柱各有其经典出处。词典构念锚是 Bian, Jia, Li 与 Yan (2021): 他们针对中文会计与金融文本编制情感词典, 论证英文词典直译到中文金融语境会系统性失真, 为本家族选用中文本土词典提供了直接依据; 这与 Du, Huang, Wermers 与 Wu (2022) 在 Review of Finance 上关于"语言与领域特异性——中文金融情感词典"的发现同源, 后者进一步量化了领域专用中文词典相对通用词典在中国市场文本上的增量效度。IDF 加权的思想上溯 Spärck Jones (1972) 关于词项特异性的统计诠释——越稀有的词区分力越强, 这一逆文档频率原理是本列"稀有情感词加权更重"的方法根; 在金融文本分析语境中, Jegadeesh 与 Wu (2013) 的"词力量"框架示范了如何按词的信息含量而非简单计数来加权情感词, 是本列 IDF 臂的金融学先例。至于词典法本身的地位, Frankel, Jennings 与 Lee (2022) 在 Management Science 上系统比较了机器学习与词典方法的披露情感度量, 表明两类方法各有所长、互为稳健性——这正是本项目保留词典轨 (含 Bian 词典的 IDF 加权变体) 与 LLM 轨、BERT 轨并排作互证的方法论根据。羊群加权分子的设计意在把跟风转载、抄稿式报道的过度计权剥离, 使加总后的加权语调更贴近"独立信息"的口径, 与上述词典效度文献形成互补。Ma, Zhang 与 Zhang (2025, Expert Systems with Applications) 构建了面向中国本土投资者的细粒度中文情感词典并验证其市场预测效度, 呼应本家族选用中文本土 (而非英文直译) 情感词典并按词权重差异化打分的构念取向; Lan, Wu, Xu, Feng 与 Zhang (2024, Neural Computing and Applications) 用大语言模型对中文金融文本做细粒度情感分析并与传统词典法比较, 为本家族在词典轨之外并排设置 LLM 轨、互为稳健性的设计提供了新近的方法论参照。

## VAR: bian_2021_idf_score_hw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨。与 full 轨的唯一差别在于 article 级 bian_2021_idf_score 所依据的文本范围: ctx 轨的文本 = 标题 prepend + 实体上下文窗口 (content_ctx), 即只截取目标银行与金科实体附近的窗口文本, 而非整篇正文。因此本列在同一银行-年内加总的, 是"仅看实体邻近语境"算出的 IDF 加权 Bian 语调乘以 ctx 轨羊群权重 (herd_weight_ctx) 之和。羊群权重按轨独立: ctx 轨用 herd_weight_ctx, 不借用 full 轨权重。ctx 轨在项目定位上是 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 留篇集的子集 (留篇门控 full-only), 但 per-track 的得分列照常逐轨独立计算与聚合。与 full 轨、ss 轨的关系是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁把 ctx 与 full/ss 混进同一条 over-identified 的 Hansen J。使用时应把 ctx 轨视作"窄口径语境"下对同一 Bian-IDF-羊群加权语调分子的规格稳健性变体: 若主结论在 full 与 ctx 上定性一致, 说明它不依赖于是否把无关正文段落纳入情感打分。需再次提醒本列是分子而非平均量, 单独使用无直接可解释性, 须配 sum_herd_weight_ctx 作分母还原为 ctx 轨的 herd-weighted 平均语调。开发期 T=2 小样本上, ctx 轨在部分银行-年可能因实体窗内无情感词而退化为零或缺失, 属预期行为, 生产 T=19 全量语料下该退化基本消失。此外须留意 ctx 与 full 在数值上高度相关但并非冗余: 二者差异恰好度量了"把无关正文段落纳入情感打分"这一口径选择对加权语调分子的边际影响, 因而两轨并排承载的是可审计的规格稳健性信息, 不应因相关性高而合并入同一识别方程。

## VAR: bian_2021_idf_score_hw_sum_full

【变体差分】
本列是 full (全文) 轨, 也是本家族的首要轨与留篇门控轨。article 级 bian_2021_idf_score_full 依据的文本 = 标题 prepend + 完整正文 (content_full), 即对整篇报道做 IDF 加权 Bian 词典情感打分; 本列在银行-年内加总的是该全文得分乘以 full 轨羊群权重 (herd_weight_full) 之和。全文轨之所以是首要轨: 一是留篇门控采用 full-only 口径 (2026-06-29), 一篇报道是否计入该银行的报道宇宙只看 full 轨的 LLM 留篇判定, 故 full 轨的分母 n_articles 与报道宇宙定义天然对齐; 二是 IDF 权重本身就在 content_full 语料上估计, full 轨的打分与 IDF 估计语料严格同构。羊群权重按轨独立取 herd_weight_full。与 ctx、ss 两轨的关系仍是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁三轨混进同一条 over-identified 的 Hansen J。本列同样是分子量: 真正的全文轨 herd-weighted 平均语调 = 本列 ÷ sum_herd_weight_full, 分子单列的用意是让下游能自由重组分母口径并逐块审计分子分母一致性。相对 ctx/ss, full 轨纳入了完整正文语境, 信息最全但也最易被与目标银行弱相关的段落稀释, 因此与 ctx (窄语境)、ss (同句最严语境) 并排恰好构成从宽到严的语境粒度稳健性梯子。实践中若主回归以 full 轨为基准, 应在稳健性表里逐轨报告 ctx 与 ss 的同名替代结果, 而不是把三轨强行塞进一条过度识别方程, 这既是本项目的三轨铁律, 也是词典法与 LLM/BERT 轨互证格局在轨内粒度上的自然延伸。

## VAR: bian_2021_idf_score_hw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 语境粒度最严。article 级 bian_2021_idf_score_ss 依据的文本 = 标题 prepend + 银行与金科同句共现窗口 (content_ss, 以 config filtering ss_sentence_radius 控制的同句±N 窗为界), 只对目标银行与金科实体真正落在同一 (或相邻 N) 句的片段做 IDF 加权 Bian 情感打分; 本列在银行-年内加总的是该同句得分乘以 ss 轨羊群权重 (herd_weight_ss) 之和。ss 轨的回退语义镜像 ctx 轨: 当某篇不存在银行与金科的同句共现时, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与 ctx 的 fallback 契约一致, 并共享 n_articles 分母口径。羊群权重按轨独立取 herd_weight_ss (不借用 full/ctx 权重), IDF 权重则仍复用 content_full 语料估得的同一份 (三轨共享 IDF, ss 亦不例外)。与 full、ctx 两轨的关系是三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁把 ss 与 full/ctx 混进同一条 over-identified 的 Hansen J。ss 轨在稳健性梯子上代表"最贴近银行-金科直接语境"的极窄口径: 若主结论在 full/ctx/ss 三轨上一致, 说明它既不靠全文噪声也不靠宽窗噪声, 而是由银行与金科真正同句的表述驱动。本列同为分子量, 须配 sum_herd_weight_ss 还原为 ss 轨 herd-weighted 平均语调; 开发期 T=2 上因同句共现稀疏, ss 轨零值/缺失比例偏高属预期退化, 生产全量语料下同句共现样本显著增厚。正因 ss 轨口径最严、样本最稀, 它对"结论是否由银行与金科的直接同句表述驱动"这一问题给出的答案最有力, 是三轨稳健性梯子中信息价值与噪声风险都最高的一端, 使用时须结合 ss_is_fallback 标记区分真同句片段与回退全文片段, 避免把回退样本误当作严格同句证据解读。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2024). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications. https://doi.org/10.1007/s00521-024-10603-6
<!-- rendered-citations:end -->
