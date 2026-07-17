---
family_id: F215
columns:
- du_2022_idf_score_mw_sum_ctx
- du_2022_idf_score_mw_sum_full
- du_2022_idf_score_mw_sum_ss
unit: 媒体权威加权的 IDF 情感得分年度合计 (无量纲聚合分值)
formula: "du_2022_idf_score_mw_sum{track} = Σ_{i∈bank-year}( du_2022_idf_score{track}_i × media_authority_weight_i ); 篇章级 du_2022_idf_score = 语言学规则归一化净语调, 词典为 IDF 加权版 du_2022 (base_score × idf_weight); idf_weight(w) = Winsorize( log10(N/(1+df(w))) / mean(raw_idf), P1, P99 ); media_authority_weight = raw_weight / mean(raw_weight)"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _analyze_single_article ; news_process/pipeline/panel/runner.py (步骤3c 媒体权威加权) ; news_process/pipeline/panel/encode.py (_mw_sum 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_idf_score{track})
- 22_idf_weights.json (逐词典 IDF 权重快照)
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
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
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  issue: ""
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  issue: ""
  pages_or_artno: 100148
- doi: 10.1017/CBO9780511809071
  type: book
  authors: Manning, C. D., Raghavan, P., & Schütze, H.
  year: 2008
  title: "Introduction to information retrieval"
  venue: Cambridge University Press
  no_doi_ack: F215-book-manning-iir
  alt_link: "https://nlp.stanford.edu/IR-book/ (ISBN 9780521865715)"
- doi: "10.1016/j.jcorpfin.2025.102835"
  type: "journal"
  authors: "Schweizer, D., Wang, X., Wu, G., & Zhang, A."
  year: 2025
  title: "Political connections and media bias: Evidence from China"
  venue: "Journal of Corporate Finance"
  vol: "94"
  pages_or_artno: "102835"
- doi: "10.1287/orsc.2022.17237"
  type: "journal"
  authors: "Dewan, Y., Simons, T., & Wernicke, G."
  year: 2024
  title: "The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms"
  venue: "Organization Science"
  vol: "35"
  issue: "5"
  pages_or_artno: "1930-1955"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是银行—年层面的"媒体权威加权 · IDF 稀有度加权"金融情感合计。它把每篇涉及目标银行的新闻先用 Du et al. (2022) 中文金融情感词典打出一个净语调分值, 该分值在打分前已对词典逐词乘上逆文档频率 (IDF) 权重以压低高频泛词、放大稀有信号词的贡献; 随后在聚合到银行—年时, 又给每篇报道乘上媒体权威性权重 (media authority weight), 让权威财经媒体的语调比小报的语调在合计中占更大分量; 最后对同一银行同一年内的全部报道求和 (sum), 得到本家族的三条列。三条列分别对应 full / ctx / ss 三条文本轨。构念上它属于"信息量校正后的情感强度存量"——不是平均语调 (mean), 而是加权求和 (weighted sum), 因此同时携带了该银行当年被报道的数量维度与语调维度, 是一个规模敏感的年度情感暴露量, 与同族的 idf_tone (mean) / idf_tone_std (离散度) 互补而不重复。

词典来源为 Du et al. (2022) 发表于 Review of Finance 的中文金融情感词典。该词典的显著特征是在普通正面词 (2,235) 与负面词 (2,986) 之外, 单列了一类政治正面词 (1,434), 并依据其"政治正面词的市场信号弱于普通正面词"的实证发现, 对该类词以降低后的 0.5 权重计入正侧。需要说明的是, 本家族固定采用政治词权重 0.5 的生产口径 (canonical), 而政治词权重 {0.0, 0.5, 1.0} 三臂敏感性检验是另一独立家族 (du_2022_score_polw{00,05,10}) 的职责; 本家族不展开权重梯子, 二者正交不交叉。IDF 权重则来自对全语料的一次性文档频率统计, 三轨共享同一份 content_full 语料的 IDF 权重 (绝不按轨分语料), 以保证跨轨可比。

【方法学与计算】
计算链路分三层。第一层是篇章级 IDF 情感打分 (tone_words.py)。IDF 权重由 build_idf_weights 计算: 对每个词 w, raw_idf(w) = log10(N / (1 + df(w))), 其中 N 为去重后唯一文档数、df(w) 为包含该词的唯一文档数 (按文本内容自身去重, 防止"一篇报道提及多家银行被展开成多行"虚增计数); 再做均值归一化 raw_idf / mean(raw_idf) 使加权后量级近似等权版、可共用阈值; 最后做 P1/P99 Winsorization 削平极端稀有词与极高频词, 防一词定乾坤。IDF 与词频统计使用同一注入态的 tone tokenizer 并行分词, 严格语义同构, 坚决废弃 Aho-Corasick 子匹配以免把"大家"误计为"大"。得到 IDF 加权词典后 (base_score × idf_weight, 保留极性符号与政治词 0.5 幅值), 用带语言学规则 (否定翻转 / 程度副词 / 转折) 的 _compute_sentiment_with_rules 打出归一化净语调 idf_norm, 落篇章级 du_2022_idf_score{track}。第二层是媒体权威加权 (runner.py 步骤 3c): 从 media_weights.json 载入每家媒体的静态权威性评分, 归一化为 media_authority_weight = raw_weight / mean(raw_weight), 再逐篇令 du_2022_idf_score_mw{track} = du_2022_idf_score{track} × media_authority_weight。第三层是银行—年聚合 (encode.py): 对同一银行—年内全部报道的 du_2022_idf_score_mw{track} 求 sum, 即本家族列 du_2022_idf_score_mw_sum{track}。因是求和口径, 列值随报道条数与权威性同向放大, 量纲上是无量纲分值的加权累加, 不落在 [-1, 1] 内。

三轨 (full / ctx / ss) 与后续可能并列的加权口径 (vw 提及密度 / mw 媒体权威 / hw 跟风衰减) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把它们混进同一 over-identified 的 Hansen J 过度识别检验; 留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入银行—年宇宙只看 full 轨留篇判定, ctx / ss 为 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集; ss 轨回退语义镜像 ctx——当无银行与金科同句共现时 content_ss 回退全文正文并置 fallback 标志。

【文献定位】
词典本体锚定 Du et al. (2022, Review of Finance): 该文系统论证了中文金融文本情感测度的语言与领域特异性, 指出直译英文词典 (如 Loughran-McDonald) 在中文语料上系统偏误, 并构建了含政治正面词分层权重的本土词典, 是本家族 0.5 政治词权重与词典词表的直接依据。IDF 加权的方法学正当性锚定 Jegadeesh & Wu (2013, Journal of Financial Economics): 该文"Word power"提出以词的市场信息含量为权重的内容分析法, 论证均权词频会被高频低信息词稀释, 与本家族用 IDF 压高频、抬稀有词的动机同构; 信息检索侧的 smooth-IDF 平滑公式 (分母取 1 + df(w) 以避免零除并压缩极稀有词的对数放大) 参照 Manning, Raghavan & Schütze (2008) 的经典教科书口径; 而权重端的 P1/P99 Winsorization 削尾并非源自该教科书, 而是稳健统计中防极端值主导的通行做法, 在本家族用以削平极稀有词与极高频词两端的权重尖峰、避免一词定乾坤, 与 smooth-IDF 分属不同的方法学来源。词典法的当代演进由 Ma et al. (2025) 的中文细粒度投资者情感词典 CN-FSD 与 Sun et al. (2025) 融合词典知识与中性特征的预训练模型情感分析所代表, 二者共同表明词典基线在中文金融情感测度中仍是不可或缺的可解释、可复现锚, 支持本家族将词典法作为 LLM / BERT 情感的互为稳健性平行轨保留。 媒体权威加权这一层的文献定位须与词典侧严格区分, 且其锚点只到前提为止。Schweizer、Wang、Wu 与 Zhang (2025) 以中国非国有上市公司新闻报道大样本实证发现, 有政治关联的企业获得显著更正面的媒体报道, 并借 Rule 18 反腐规定强制政治关联董事辞职这一监管冲击做 DiD 确证该因果链, 且丑闻期政治关联企业面临更软化的媒体审视、声誉惩罚被削弱; 该文为本家族锚定的是「中国的媒体报道语调并非中性的信息镜像, 而是可被系统性因素预测地偏移」这一同域前提, 用以说明本项目不把报道当作等同、无偏的信息载体处理。须显式声明其限度: 该文实证的异质性维度是被报道企业的政治关联属性, 而非媒体来源之间的异质性, 因此不可据以主张「媒体来源不同质故须按来源赋权」; 该文亦未构造任何权重函数, 未做权重与词典分相乘再求和, 样本为中国上市公司而非银行—年三轨。outlet 级异质性的直接依据须另引 Dewan、Simons 与 Wernicke (2024): 该文考察企业 CSR 行为如何影响新闻媒体对该企业的报道及报道倾向, 并表明这一映射受媒体自身意识形态调节, 即不同来源对同一事实的呈现存在系统性差异 —— 这正是 media_authority_weight 按媒体名逐篇赋权所预设的前提。其边界同样明确: 该文语境为美国媒体与美国企业 CSR, 媒体报道量与倾向是结果变量而非加权基, 不构造任何权重函数, 故只锚定「媒体报道非中性、来源有别」这一前提, 不锚定本家族 raw_weight 除以均值的归一化公式, 更不触及 IDF 稀有度加权层。
## VAR: du_2022_idf_score_mw_sum_full

【变体差分】
本列是 full 轨变体, 即三轨中的全文轨。其篇章级 du_2022_idf_score_full 在"标题 prepend + 全文正文"这一最完整文本上打分: 文本由 stage 14 ctx_materializer 物化的 content_full 提供, 等于把原始标题拼接到正文之前后的完整报道体。相对 ctx / ss 两轨, full 轨捕获信息量最大、噪声也最高, 因而是本家族的 canonical 主轨, 也是留篇门控的唯一判据轨——一篇报道是否计入某银行—年的加权求和, 只取决于该报道在 full 轨上的留篇判定 (full-only 门控, 2026-06-29), ctx / ss 两轨的同名列仅在 full 已留篇的行宇宙子集上取值。IDF 权重亦以 content_full 语料统计, 三轨共享此权重不按轨分语料, 故 full 轨的 IDF 缩放与 ctx / ss 完全一致, 三轨差异纯粹来自打分文本范围而非权重体系。聚合口径为媒体权威加权求和: 先逐篇令 idf_score_full 乘 media_authority_weight, 再对银行—年内全部报道求 sum, 得到规模敏感的年度加权情感暴露量。本列与同轨的 idf_tone_full (mean) / idf_tone_std_full 互补: 前者含数量维度, 后者仅语调水平与离散度。因 full 轨采集了整篇报道的全部情感词命中, 其 IDF 加权后的净语调在信息量上最饱满, 但也最易受与目标银行弱相关段落的语调裹挟, 这正是 ctx / ss 两轨作为收窄稳健性轨存在的动机。就聚合的经济含义而言, 本列的年度合计值同时随该银行当年报道条数与权威媒体占比放大, 因而适合作为"加权情感暴露存量"进入需要规模敏感度的规格, 而非需要单位化语调的规格。full / ctx / ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J, 亦不与 vw / mw / hw 其他加权口径混作过度识别工具组。

## VAR: du_2022_idf_score_mw_sum_ctx

【变体差分】
本列是 ctx 轨变体, 即实体窗轨。其篇章级 du_2022_idf_score_ctx 在"标题 prepend + 实体上下文窗口"文本 (content_ctx) 上打分, 该窗口只保留目标银行实体邻域内的句子, 剔除与目标银行无关的报道段落, 因而语调更聚焦于对该银行的直接评价、削弱了整篇报道中其他主体带来的语调噪声。相对 full 轨的全文口径, ctx 轨是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, 只有在 full 轨已判定留篇的银行—年报道行上才取值, 本列不独立决定留篇。IDF 权重与 full 轨共享同一份 content_full 语料统计结果 (不按轨分语料), 故 ctx 与 full 的差异只来自打分文本范围收窄, 而非权重差异。聚合仍为媒体权威加权求和: 逐篇 idf_score_ctx × media_authority_weight 后对银行—年求 sum。由于 ctx 轨文本更短、命中情感词更少, 本列的量级通常小于 full 轨同名列, 二者的差异本身即构成"报道语调是否集中于目标银行邻域"的稳健性证据。换言之, 若 full 与 ctx 轨的年度加权合计给出一致的符号与显著性, 则可排除"结论由报道中与目标银行无关的段落语调驱动"这一替代解释; 反之二者背离则提示语调信号来自外围语境, 需谨慎解读。政治词权重仍固定为 0.5 生产口径, 不在本家族展开梯子; IDF 权重的 Winsorization 与均值归一化确保 ctx 轨即便命中稀有词也不会因权重尖峰而失真。full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified 的 Hansen J 过度识别检验; ctx 轨与 full / ss 只并列进各自回归, 不同时作为同一方程的多个工具。

## VAR: du_2022_idf_score_mw_sum_ss

【变体差分】
本列是 ss 轨变体, 即银行与金科同句轨 (sentence-shared)。其篇章级 du_2022_idf_score_ss 在"标题 prepend + 银行与金融科技词同句共现窗口"文本 (content_ss) 上打分: 只保留目标银行与金科关键词落在同一句 (或 config 指定的同句半径窗) 内的句子, 因而语调最贴近"该银行与金融科技相关"这一狭义语境, 是三轨中文本范围最窄、信噪比取向最激进的一轨。回退语义镜像 ctx: 当某报道不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文并置 ss_is_fallback 标志 (与 ctx 的回退契约一致), 保证不因窗口为空而丢篇。与 ctx 相同, ss 轨是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集, 不独立决定留篇门控; IDF 权重同样复用 content_full 语料统计, 三轨共享。聚合口径不变: 逐篇 idf_score_ss × media_authority_weight 后对银行—年求 sum, 得媒体权威加权的同句情感合计。因大量报道触发回退、且非回退窗口极短, 在浅面板 (T 较小) 上 ss 轨可能出现零方差或近似退化, 属预期行为而非缺陷, 生产全量语料上恢复正常区分度。ss 轨的价值在于把语调测度收窄到"银行—金科"最狭义的话题交叉点上, 是三轨中对"该银行的金融科技相关舆论语调"这一构念最贴合、也最保守的操作化; 当它与 full / ctx 轨给出方向一致的加权合计时, 可最有力地排除语调信号来自泛金融报道背景的可能。IDF 权重与政治词 0.5 权重的处理与其余两轨完全一致, ss 与 full / ctx 的唯一差异仍是打分文本范围。full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; ss 仅作与 full / ctx 平行的稳健性测度轨而非独立识别工具。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
Schweizer, D., Wang, X., Wu, G., & Zhang, A. (2025). Political connections and media bias: Evidence from China. Journal of Corporate Finance, 94, 102835. https://doi.org/10.1016/j.jcorpfin.2025.102835
Dewan, Y., Simons, T., & Wernicke, G. (2024). The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms. Organization Science, 35(5), 1930-1955. https://doi.org/10.1287/orsc.2022.17237
<!-- rendered-citations:end -->
