---
family_id: F223
columns:
- du_2022_pos_symb_count_ctx
- du_2022_pos_symb_count_full
- du_2022_pos_symb_count_ss
unit: 篇数 (bank-year 内文章计数, 非负整数, dtype double)
formula: "du_2022_pos_symb_count{track} = Σ_{i∈bank-year} 1[ du_2022_score{track}_i > 0 ∧ innovation_substantiveness_full_i == '象征性' ]; track ∈ {_full,_ctx,_ss}; du_2022_score 的正侧含 political_positive 词以 0.5 权重计入; 象征性判据恒取 full 轨 (track-agnostic), 仅词典极性符号逐轨变"
producer: news_process/pipeline/panel/runner.py (篇章级 _is_{d}_pos_symb 标记, 洗稿率 K 块) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (K 块 sum 聚合)
upstream:
  - 14_materialize_ctx.parquet (content_ctx / content_ss)
  - 21_tone_llms.parquet (innovation_substantiveness_full)
  - 22_tone_words.parquet (du_2022_score_full / _ctx / _ss)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
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
  venue: SSRN Working Paper No. 3446388
- doi: "10.1016/j.jsis.2026.101971"
  type: "journal"
  authors: "Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E."
  year: 2026
  title: "Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?"
  venue: "The Journal of Strategic Information Systems"
  vol: "35"
  issue: "2"
  pages_or_artno: "101971"
- doi: "10.1108/ara-01-2025-0031"
  type: "journal"
  authors: "Guan, J., & Zhuang, X."
  year: 2025
  title: "Do digital words reflect real innovation? Evidence from post-M&A earnings conference"
  venue: "Asian Review of Accounting"
  pages_or_artno: "1-44"
new_dois: []
---

## CORE

【构念与来源】
本家族的三列度量的是一个复合计数: 在给定银行-年内, 同时满足「按 Du et al. (2022) 中文金融情感词典判为正面语调」且「被大模型实质性分类器判为象征性 (象征性 vs 实质性)」的报道篇数。列名里的 pos 指词典极性为正 (du_2022_score 大于零), symb 指实质-象征二元框架中的象征侧 (symbolic), count 指银行-年层的篇章求和。它不是一个语调分值, 也不是占比, 而是一个非负整数计数, 落盘为 double 类型。它的构造动机来自实质性-象征性脱耦 (substantive-symbolic decoupling) 文献: 当一家银行的金融科技相关报道在措辞上呈现积极正面, 却在内容实质上停留于象征性表态 (发布会、战略口号、意向签约、政策口径复述) 而非实质性投入 (系统上线、资本承诺、可核验产出) 时, 这类「正面且象征」的报道即构成一种叙事包装的信号。把这类报道数出来, 是构造银行-年「洗稿率 / 脱耦率」分子的原料之一; 本家族给出的正是该分子在单一词典 (Du 2022) 口径下的逐轨计数。之所以专为 Du et al. (2022) 词典单列一族, 是因为该词典相对其它中文金融情感词典有一处独有结构: 它把政治正面词 (political_positive, 1,434 词) 单独成类, 生产口径以 0.5 权重计入正侧。这一取舍直接影响本家族「正面」那一半判据的边界——某些以政治或政策口吻表达的褒义措辞, 在 Du 2022 口径下被折价计权而非等同普通正面词, 从而使「正面且象征」的交乘更贴近「实质性积极行动」而非「政策表态式积极」。因此本家族既是脱耦率分子的一个单词典读数, 也隐含了对政治化正面措辞的降权处理, 与其它五部词典的同名计数并排构成跨词典交叉验证。

【方法学与计算】
篇章级判定分两步交乘。第一步词典极性: 上游 stage 22 (tone_words) 对每篇报道按 Du et al. (2022) 词典算出逐轨情感分 du_2022_score{track}, 大于零即记为正面。Du 2022 的正侧分子结构为 pos_weighted = pos_ordinary + 0.5 × pos_political, 即普通正面词全权计入、政治正面词以 0.5 折价计入, 净分再经否定翻转、程度副词、转折等语言学规则调整并归一化; 该 0.5 权重取值是研究者选择, 并配有权重 ∈ {0.0, 0.5, 1.0} 三臂敏感性梯子 (三者互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J), 但本家族的 pos 判据锁定生产口径的 0.5 权重臂 (canonical du_2022_score), 不随权重梯子分裂列。第二步象征性判定: stage 21 的大模型对每篇报道给出 innovation_substantiveness 的类别标签 (实质性 / 象征性 / 不适用), 落在象征性者记为象征侧。runner.py 的洗稿率 K 块把两个布尔逐元素求交, 生成篇章级指示列 _is_du_2022_pos_symb{track} (方法 D2, 单词典臂); encode.py 的聚合规格再按银行-年对该指示列 sum, 得到本家族三列。一个关键且承重的口径细节: 象征性判据恒取 innovation_substantiveness_full 这一 full 轨标签 (track-agnostic), 三列共用同一象征掩码, 逐轨变化的只有词典极性符号那一侧。这与全项目 full-only 留篇门控 (2026-06-29) 一致——一篇报道是否算「一篇银行金科报道」只看 full 轨大模型核验, ctx/ss 是 conditional-on-full 的子集测度; 象征侧既然来自 full 轨分类, 就不随文本轨切换而重判。词典极性侧则真正逐轨: full 用标题拼接后的全文, ctx 用标题加实体窗口文本, ss 用标题加银行与金科同句共现窗口文本。词级极性判定采用词典裸计数经语言学规则调整后的净分符号, 缺列 (某轨词典分不存在) 由 valid_agg 自动跳过而非报错, NaN 情感经 fillna 视为非正、永不误入分子。三轨互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 象征掩码的 full-only 属性也意味着不应把三列当作三套独立象征测度对待, 它们只在词典极性通道上分轨。

【文献定位】
测度的词典脊柱来自 Du et al. (2022), 发表于 Review of Finance, 是面向中文金融文本、强调语言与领域特异性 (language and domain specificity) 的专用情感词典, 其贡献不仅在于覆盖正负情感词, 更在于识别并单列了政治正面词这一在中国资本市场话语中信号偏弱的类别, 并给出对该类词降权处理的实证依据; 本家族「正面」判据里 political_positive 的 0.5 权重正是对 Du et al. (2022) 这一发现的直接落地。与之同源的中文细粒度情感词典构造思路见 Ma et al. (2025) 对国内投资者情感词典 CN-FSD 的系统化构建, 二者共同支撑「中文金融语料需专用词典而非英文词典直译」的方法论立场, 也说明不同团队构建的中文词典在极性判据上会有系统性差异——这正是把 Du 2022 与 Bian et al. (2021) 等其它词典的同名计数并排、互作跨词典稳健性检验的意义所在。象征侧的构念根植于实质性-象征性脱耦研究: Bingler et al. (2022) 以 ClimateBert 揭示企业气候披露中「廉价表态与挑肥拣瘦」(cheap talk and cherry-picking) 的象征化倾向, 正是本家族把「正面但象征」单独数出来的直接动机——语调为正不等于实质投入, 需要一个能把象征包装从实质行动中剥离的计数。综合而言, 本家族即在中文专用情感词典谱系与实质-象征脱耦框架的交叉点上, 把「词典极性 × 象征分类」的交乘计数作为脱耦分子的单词典 (Du 2022) 实现, 并因该词典的政治词降权结构而对政策化正面措辞天然更为审慎。 象征侧的理论框架在近期中国情境研究中得到进一步锚定与校准。Chen、Hajiheydari、Zhang 与 Lin (2026) 基于注意力基础观构造企业数字化转型关注度, 以中国上市公司 2007–2020 年样本在「战略实质承诺」与「象征性信号」两个对立解释间做检验, 发现该关注度与突破式创新相关而与渐进式创新及研发支出无关, 从而支持实质承诺说、未支持象征性信号说, 且话语与创新的一致性在高问责情境下最强。引用它的意义恰在于: 该二分是当代科技话语研究的主流理论框架, 且「话语是否只是象征」是可被实证证伪的经验问题, 故它是本家族正面×象征交乘计数的理论锚点与反面参照, 而非象征性解释成立的证据。其迁移边界为: 原文以「话语关注度 vs 实际创新产出」间接推断象征性, 本项目以大模型对单篇报道直接标注实质性/象征性, 判定机制不同; 原文文本源为公司自述披露, 本项目为第三方新闻; 分析层级亦由公司-年改为银行-年且分三轨。Guan 与 Zhuang (2025) 则直接追问数字化措辞是否对应真实创新, 在中国并购语境下以文本测度检验数字词汇与后续创新产出的对应关系, 与本家族「在正面科技话语中剥离象征性叙事」的构念高度同域; 但该文只做了词汇与产出的对应检验, 未提出象征性/实质性的逐篇标注方案, 其文本源为并购后业绩说明会的管理层自述、分析单元为并购事件与公司-年, 与本家族第三方新闻、银行-年三轨并排的口径存在系统差异。
## VAR: du_2022_pos_symb_count_full

【变体差分】
本列是三轨中的 full 轨实现, 也是家族语义上的基准轨。它的词典极性侧取 du_2022_score_full: 上游 stage 14 把标题 prepend 到全文正文 (content_full), stage 22 在这条最完整的文本上按 Du et al. (2022) 词典算出正负词加权净分 (正侧 political_positive 以 0.5 权重计入), 净分大于零即计为正面。象征侧取 innovation_substantiveness_full, 与另外两列完全相同 (象征判据本就恒为 full 轨, track-agnostic), 因此本列相对 ctx/ss 的唯一差分完全落在词典极性的文本供给上——full 轨读的是整篇报道, 极性信号最充分、召回最高, 但也最容易被与目标银行金科主题无关的旁支段落稀释。由于全项目留篇门控是 full-only, 本列的银行-年行宇宙即留篇集本身 (非子集), ctx/ss 两列是在此基础上的 conditional-on-full 收窄。作为家族基准, 本列常作主轨进入脱耦率分子, ctx/ss 作并排稳健性轨; 三轨各自 just-identified, 禁混进同一 over-identified Hansen J。计数为非负整数, 缺词典分列时该轨聚合被 valid_agg 跳过而非置零, 象征分类 NaN 或判为实质性/不适用者不入分子。需要强调的是, 本列与家族外其它单词典 pos_symb_count 列 (如 jiang_2021、yao_2021、bian_2021、you_2018、loughran) 属同一方法 D2 谱系, 区别仅在采用的词典不同; 本列锁定 Du et al. (2022) 中文金融词典, 且其正侧对政治正面词做 0.5 降权处理, 是家族中唯一带这一政治词折价结构的词典臂, 因此在政策口吻密集的报道上, 本列相对不降权的词典臂可能给出略保守的正面判定。full 轨因文本最全, 通常给出三轨中最大的计数, 但这一「更大」并不天然等于「更准」——它以牺牲主题聚焦为代价, 正是需要 ctx/ss 两轨并排稳健性检验的原因所在。

## VAR: du_2022_pos_symb_count_ctx

【变体差分】
本列是 ctx (实体窗口) 轨实现。与 full 轨的唯一实质差分在词典极性侧的文本供给: 词典分取 du_2022_score_ctx, 其底层文本是 stage 14 物化的 content_ctx——标题 prepend 后再截取围绕目标实体 (银行、金科词) 的上下文窗口, 而非整篇正文。这样得到的正面判定更聚焦于与银行金科主题相邻的措辞, 削弱了全文轨里无关段落对极性符号的稀释, 代价是召回下降、窗口外的情感线索被舍弃。词典正侧对 political_positive 的 0.5 折价权重在本轨与 full 轨完全一致 (权重是词典口径不是文本口径, 不随轨切换), 故本列与 full 的差别纯粹是「在哪段文本上数正负词」而非「怎么给正面词计权」。象征侧仍取 innovation_substantiveness_full (与 full/ss 三列共用同一 full 轨象征掩码, 不随文本轨改判), 所以本列绝非「另算一套象征分类」, 它只是把「是否正面」这一半的证据换成实体窗口文本。ctx 与 full 互为稳健性、不分主次, 两轨各自 just-identified 并排进各自回归, 禁混进同一 over-identified Hansen J。行宇宙为 full 留篇集的 conditional-on-full 子集, per-track 计数照算。缺 content_ctx 或该轨词典分列时聚合被 valid_agg 优雅跳过; NaN 情感 fillna 后视为非正, 象征分类未判为象征性者不入分子。计数为非负整数, 落盘 double。相对 full 轨, 本列的经济含义是「在贴近银行金科语境的措辞上仍呈正面且实质上仍属象征」的报道数, 它对全文中游离于主题之外的正面辞藻更不敏感, 因此当 full 与 ctx 两轨给出的脱耦率分子出现系统性背离时, 往往提示正面信号来自与银行金科无关的段落, 这一背离本身即是一个可披露的稳健性诊断。ctx 轨在 Du et al. (2022) 词典之外不引入任何新的语言学规则或阈值, 与家族其它 ctx 变体保持严格 parity, 使得跨词典的 ctx 读数可直接比较。

## VAR: du_2022_pos_symb_count_ss

【变体差分】
本列是 ss (同句共现) 轨实现, 三轨中窗口最窄。词典极性侧取 du_2022_score_ss, 底层文本 content_ss 由 stage 14 物化为「标题 prepend + 目标银行与金科词同句共现的 ±N 句窗口」(窗宽由 filtering.yaml 的 context_window.ss_sentence_radius 控, 默认 1), 只有当报道里银行与金科词落在同一句 (或近邻句窗) 时才计入该轨正面证据, 极性判定因此最贴近「银行确实在谈金科」的语境, 但也最易受召回不足影响。词典正侧对 political_positive 的 0.5 折价权重在本轨同样不变 (与 full/ctx 一致)。承重的回退语义 (镜像 ctx): 当某篇报道没有银行与金科的同句共现时, content_ss 优雅回退为全文正文 body 且 ss_is_fallback 置 True (与 ctx 回退口径一致); 若上游金科 AC 自动机为空 (FINTECH_AC=None), 则整轨 fallback 标记为真, 优雅降级不静默清空。象征侧同样恒取 innovation_substantiveness_full (三列共用 full 轨象征掩码, ss 轨绝不另判象征性), 故本列相对 full/ctx 的差分仍只在词典极性的文本供给这一半。ss 与 full/ctx 互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 行宇宙为 full 留篇集的 conditional-on-full 子集。缺列由 valid_agg 跳过, NaN 情感视为非正, 非象征侧不入分子; 计数非负整数, dtype double。由于 ss 轨窗口最窄且带回退, 在开发期浅面板 (T 极小) 上本列的方差可能显著小于 full/ctx, 甚至在同句共现极稀时逼近退化, 这属于窗口收窄的预期表现而非缺陷; 在生产规模语料上, ss 轨给出的是三轨中主题最纯净的脱耦率分子读数, 适合作为「银行确实在正面谈论金科却止于象征」这一最严格构念的下界估计。ss 与 ctx 的回退口径严格镜像, 保证两轨在无共现时不会各自漂移, 三轨间的差异因此可干净地归因于窗口宽窄而非回退规则差异。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E. (2026). Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?. The Journal of Strategic Information Systems, 35(2), 101971. https://doi.org/10.1016/j.jsis.2026.101971
Guan, J., & Zhuang, X. (2025). Do digital words reflect real innovation? Evidence from post-M&A earnings conference. Asian Review of Accounting, 1-44. https://doi.org/10.1108/ara-01-2025-0031
<!-- rendered-citations:end -->
