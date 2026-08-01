---
family_id: F648
columns:
- you_2018_pos_symb_count_ctx
- you_2018_pos_symb_count_full
- you_2018_pos_symb_count_ss
unit: 篇数 (bank-year 内文章计数, 非负整数, dtype double)
formula: "you_2018_pos_symb_count{track} = Σ_{i∈bank-year} 1[ you_2018_score{track}_i > 0 ∧ innovation_substantiveness_full_i == '象征性' ]; track ∈ {_full,_ctx,_ss}; 象征性判据恒取 full 轨 (track-agnostic), 仅词典极性符号逐轨变"
producer: news_process/pipeline/panel/runner.py (篇章级 _is_{d}_pos_symb 标记, 洗稿率 K 块) ; news_process/pipeline/panel/encode.py::build_aggregation_dict (K 块 sum 聚合) ; news_process/pipeline/sentiment/tone_words.py (词典极性侧上游 you_2018_score{track})
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (innovation_substantiveness_full)
- 22_tone_words.parquet (you_2018_score_full / _ctx / _ss)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: "10.1016/j.jsis.2026.101971"
  type: "journal"
  authors: "Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E."
  year: 2026
  title: "Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?"
  venue: "The Journal of Strategic Information Systems"
  vol: "35"
  issue: "2"
  pages_or_artno: "101971"
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是一个复合计数: 在给定银行-年内, 同时满足「按 You, Zhang 与 Zhang (2018) 中文金融情感词典判为正面语调」且「被大模型实质性分类器判为象征性 (象征性 vs 实质性)」的报道篇数。列名里的 you_2018 指词典底本作者与年份, pos 指词典极性为正 (you_2018_score 大于零), symb 指实质-象征二元框架中的象征侧 (symbolic), count 指银行-年层的篇章求和。它不是语调分值也不是占比, 而是一个非负整数计数, 落盘为 double 类型。You 词典本身收录 positive(1,425) / negative(1,583) 两类极性词, 另有 definite(388) / ambiguous(178) 两类确定性词类 (后者用于 clarity 族, 与本家族的极性侧无关)。本家族的构造动机来自实质性-象征性脱耦 (substantive-symbolic decoupling) 文献: 当一家银行的金融科技相关报道在措辞上呈现积极正面, 却在内容实质上停留于象征性表态 (发布会、战略口号、意向签约) 而非实质性投入 (系统上线、资本承诺、可核验产出) 时, 这类「正面且象征」的报道即构成一种叙事包装的信号, 与 You, Zhang 与 Zhang (2018) 揭示的媒体"谁在执笔、笔法如何"的权力配置命题在方法论上相呼应——词典法所捕捉的正面措辞未必等价于内容实质。把这类报道数出来, 是构造银行-年「洗稿率 / 脱耦率」分子的原料之一; 本家族给出的正是该分子在单一词典 (You et al. 2018) 口径下的逐轨计数, 与本项目并置的另外五部中文金融情感词典 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / loughran_mcdonald_zh_2026) 各自的同名 pos_symb_count 列互为稳健性、不分主次。

【方法学与计算】
篇章级判定分两步交乘。第一步词典极性: 上游 stage 22 (tone_words) 对每篇报道按 You, Zhang 与 Zhang (2018) 词典算出逐轨情感分 you_2018_score{track}, 大于零即记为正面 (词级正负词加权净分, 归一化到闭区间, 经语言学规则——否定翻转、程度副词、转折——调整后取符号)。词典加载时对 positive∩negative 跨类重叠词 (you_2018 计 5 词) 采取「保留而非剔除」的用户决策 (2026-06-24): 重叠词同时计入正负两侧, 打分时对该词典个体 you_2018_score 净语调拉向中性而非武断选边; union/msent/ratio 等聚合测度因重叠词以 (+1,−1) 平衡双票喂入固定 union 词典而不受影响。第二步象征性判定: stage 21 的大模型对每篇报道给出 innovation_substantiveness 的类别标签 (实质性 / 象征性 / 不适用), 落在象征性者记为象征侧。runner.py 的洗稿率 K 块把两个布尔逐元素求交, 生成篇章级指示列 _is_you_2018_pos_symb{track} (方法 D2, 单词典臂); encode.py 的聚合规格再按银行-年对该指示列 sum, 得到本家族三列。一个承重的口径细节: 象征性判据恒取 innovation_substantiveness_full 这一 full 轨标签 (track-agnostic), 三列共用同一象征掩码, 逐轨变化的只有词典极性符号那一侧。这与全项目 full-only 留篇门控 (2026-06-29) 一致——一篇报道是否算「一篇银行金科报道」只看 full 轨大模型核验, ctx/ss 是 conditional-on-full 的子集测度; 象征侧既然来自 full 轨分类, 就不随文本轨切换而重判。词典极性侧则真正逐轨: full 用标题拼接后的全文, ctx 用标题加实体窗口文本, ss 用标题加银行与金科同句共现窗口文本。缺列 (某轨词典分不存在) 由 valid_agg 自动跳过而非报错, NaN 情感经 fillna 视为非正、永不误入分子。三轨互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 象征掩码的 full-only 属性也意味着不应把三列当作三套独立象征测度对待, 它们只在词典极性通道上分轨。

【文献定位】
测度的词典脊柱来自 You, Zhang 与 Zhang (2018) 发表于顶级金融学期刊 Review of Financial Studies 的 "Who captures the power of the pen?", 该文构建并使用了一部覆盖正负情感极性的中文金融文本词典, 系统检验媒体措辞对资本市场信息传递的影响, 是本项目六部并置中文情感词典之一; 其"笔法/措辞权力"命题为本家族"词典判正面"与"大模型判象征"两把尺子的交乘构造提供了直接的构念支撑——正面措辞本身并不保证内容实质。象征侧的构念根植于实质性-象征性脱耦研究: Bingler, Kraus, Leippold 与 Webersinke (2022) 以 ClimateBert 揭示企业气候披露中「廉价表态与挑肥拣瘦」的象征化倾向, 正是本家族把「正面但象征」单独数出来的直接动机——语调为正不等于实质投入, 需要一个能把象征包装从实质行动中剥离的计数。与之同源的中文细粒度情感词典构造思路见 Ma, Zhang 与 Zhang (2025) 对国内投资者情感词典 CN-FSD 的系统化构建, 与 Du, Huang, Wermers 与 Wu (2022) 对中文金融情感词典相对英文词典直译的领域优越性论证, 二者共同支撑「中文金融语料需专用词典而非英文词典直译」的方法论立场, 与本项目并置多部中文词典 (含 You 词典) 互为稳健性的做法同源。词典法文本测度的大样本效度边界另见 You 与 Zhang (2009) 关于财报文本复杂度与投资者反应不足的经典发现, 提示文本测度 (无论复杂度或情感极性) 的经济后果须与内容实质分开检验, 这正是本家族「词典极性 × 象征分类」交乘设计的旨趣所在。本家族即在这一谱系下, 把「词典极性 × 象征分类」的交乘计数作为脱耦分子的单词典实现。 近期证据进一步表明, 这一二分本身是可被实证裁决的经验问题而非预设结论: Chen、Hajiheydari、Zhang 与 Lin (2026) 基于注意力基础观构造企业数字化转型关注度 (CDTA), 以中国上市公司 2007–2020 年样本在「战略实质承诺」与「象征性信号」两个对立解释间做检验, 发现 CDTA 仅与突破式创新相关而与渐进式创新及研发支出无关, 从而支持实质承诺说、未支持象征性信号说, 且数字话语与创新的一致性在高问责情境下最强。该文对本家族的锚定是理论框架与反面参照: 象征化并非可默认成立的前提, 故须像本家族这样把「正面但象征」显式数出来交由数据判定; 须明确原文并未提供支持象征性解释的证据, 本家族亦不据此宣称象征包装普遍存在。迁移边界在于: 原文以「话语关注度 vs 实际创新产出」的推断性对比间接判定象征性, 而本项目的 innovation_substantiveness 是 LLM 对单篇报道的直接话语分类标签, 判定机制不同; 原文文本源为公司自述披露, 本项目为第三方新闻; 原文层级为公司-年, 本项目为银行-年且分三轨 (象征判据恒取 full 轨, 仅词典极性符号逐轨变)。
## VAR: you_2018_pos_symb_count_full

【变体差分】
本列是三轨中的 full 轨实现, 也是家族语义上的基准轨。它的词典极性侧取 you_2018_score_full: 上游 stage 14 把标题 prepend 到全文正文 (content_full), stage 22 在这条最完整的文本上按 You, Zhang 与 Zhang (2018) 词典算出正负词加权净分, 净分大于零即计为正面。象征侧取 innovation_substantiveness_full, 与另外两列完全相同 (象征判据本就恒为 full 轨, track-agnostic), 因此本列相对 ctx/ss 的唯一差分完全落在词典极性的文本供给上——full 轨读的是整篇报道, 极性信号最充分、召回最高, 但也最容易被与目标银行金科主题无关的旁支段落稀释。由于全项目留篇门控是 full-only (2026-06-29), 本列的银行-年行宇宙即留篇集本身 (非子集), ctx/ss 两列是在此基础上的 conditional-on-full 收窄。作为家族基准, 本列常作主轨进入脱耦率分子, ctx/ss 作并排稳健性轨; 三轨各自 just-identified, 禁混进同一 over-identified Hansen J。计数为非负整数, 缺词典分列时该轨聚合被 valid_agg 跳过而非置零, 象征分类 NaN 或判为实质性/不适用者不入分子。需要强调的是, 本列与家族里其它单词典 pos_symb_count 列 (如 jiang_2021、yao_2021、bian_2021、du_2022、loughran) 属同一方法 D2 谱系, 区别仅在采用的词典不同; 本列锁定 You, Zhang 与 Zhang (2018) 中文金融词典, 与词典均值臂 dict_pos_symb_count 及大模型投票臂 pos_symb_count 各自成轨, 用途是在单一权威中文词典口径下给脱耦率分子提供一个可与其它词典交叉验证的读数。full 轨因文本最全, 通常给出三轨中最大的计数, 但这一「更大」并不天然等于「更准」——它以牺牲主题聚焦为代价, 正是需要 ctx/ss 两轨并排稳健性检验的原因所在。

## VAR: you_2018_pos_symb_count_ctx

【变体差分】
本列是 ctx (实体窗口) 轨实现。与 full 轨的唯一实质差分在词典极性侧的文本供给: 词典分取 you_2018_score_ctx, 其底层文本是 stage 14 物化的 content_ctx——标题 prepend 后再截取围绕目标实体 (银行、金科词) 的上下文窗口, 而非整篇正文。这样得到的正面判定更聚焦于与银行金科主题相邻的措辞, 削弱了全文轨里无关段落对极性符号的稀释, 代价是召回下降、窗口外的情感线索被舍弃。象征侧仍取 innovation_substantiveness_full (与 full/ss 三列共用同一 full 轨象征掩码, 不随文本轨改判), 所以本列绝非「另算一套象征分类」, 它只是把「是否正面」这一半的证据换成实体窗口文本。ctx 与 full 互为稳健性、不分主次, 两轨各自 just-identified 并排进各自回归, 禁混进同一 over-identified Hansen J。行宇宙为 full 留篇集的 conditional-on-full 子集, per-track 计数照算。缺 content_ctx 或该轨词典分列时聚合被 valid_agg 优雅跳过; NaN 情感 fillna 后视为非正, 象征分类未判为象征性者不入分子。计数为非负整数, 落盘 double。相对 full 轨, 本列的经济含义是「在贴近银行金科语境的措辞上仍呈正面且实质上仍属象征」的报道数, 它对全文中游离于主题之外的正面辞藻更不敏感, 因此当 full 与 ctx 两轨给出的脱耦率分子出现系统性背离时, 往往提示正面信号来自与银行金科无关的段落, 这一背离本身即是一个可披露的稳健性诊断。ctx 轨在 You, Zhang 与 Zhang (2018) 词典之外不引入任何新的语言学规则或阈值, 与家族其它 ctx 变体保持严格 parity, 使得跨词典的 ctx 读数可直接比较。

## VAR: you_2018_pos_symb_count_ss

【变体差分】
本列是 ss (同句共现) 轨实现, 三轨中窗口最窄。词典极性侧取 you_2018_score_ss, 底层文本 content_ss 由 stage 14 物化为「标题 prepend + 目标银行与金科词同句共现的 ±N 句窗口」(窗宽由 filtering.yaml 的 context_window.ss_sentence_radius 控, 默认 1), 只有当报道里银行与金科词落在同一句 (或近邻句窗) 时才计入该轨正面证据, 极性判定因此最贴近「银行确实在谈金科」的语境, 但也最易受召回不足影响。承重的回退语义 (镜像 ctx): 当某篇报道没有银行与金科的同句共现时, content_ss 优雅回退为全文正文 body 且 ss_is_fallback 置 True (与 ctx 回退口径一致, 共享 n_articles 分母); 若上游金科 AC 自动机为空 (FINTECH_AC=None), 则整轨 fallback 标记为真, 优雅降级不静默清空。象征侧同样恒取 innovation_substantiveness_full (三列共用 full 轨象征掩码, ss 轨绝不另判象征性), 故本列相对 full/ctx 的差分仍只在词典极性的文本供给这一半。ss 与 full/ctx 互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 行宇宙为 full 留篇集的 conditional-on-full 子集。缺列由 valid_agg 跳过, NaN 情感视为非正, 非象征侧不入分子; 计数非负整数, dtype double。由于 ss 轨窗口最窄且带回退, 在早期试跑期浅面板 (T 极小) 上本列的方差可能显著小于 full/ctx, 甚至在同句共现极稀时逼近退化, 这属于窗口收窄的预期表现而非缺陷; 在生产规模语料上, ss 轨给出的是三轨中主题最纯净的脱耦率分子读数, 适合作为「银行确实在正面谈论金科却止于象征」这一最严格构念的下界估计。ss 与 ctx 的回退口径严格镜像, 保证两轨在无共现时不会各自漂移, 三轨间的差异因此可干净地归因于窗口宽窄而非回退规则差异。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E. (2026). Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling? The Journal of Strategic Information Systems, 35(2), 101971. https://doi.org/10.1016/j.jsis.2026.101971
<!-- rendered-citations:end -->
