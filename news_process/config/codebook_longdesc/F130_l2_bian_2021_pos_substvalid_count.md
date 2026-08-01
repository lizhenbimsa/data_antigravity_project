---
family_id: F130
novelty_exempt_rationale: "该家族是洗稿率(washing ratio)指标的同域分母技术变体(仅数'Bian词典正面且实质性已测量'的报道篇数),非独立学术构念,其测度定义依据已在母族词典文献(Bian et al. 2021)与洗稿率/cheap-talk母指标文献中给出,故豁免新颖度追新。"
columns:
- bian_2021_pos_substvalid_count_ctx
- bian_2021_pos_substvalid_count_full
- bian_2021_pos_substvalid_count_ss
unit: 篇数/计数 (count, 非负整数)
formula: "bian_2021_pos_substvalid_count{track} = Σ_{article ∈ bank-year} 1[ bian_2021_score{track} > 0 ∧ innovation_substantiveness_full ∈ {实质性, 象征性} ]  (极性得分逐轨, 实质性已测量掩码恒为 full 轨)"
producer: news_process/pipeline/panel/runner.py::_pool_svd_substvalid_counts (聚合篇章级 _svd_bian_2021_pos{track}; 篇章指示由 runner 洗稿率 washing_cols 构造)
upstream:
- 22_tone_words.parquet (bian_2021_score{track})
- 24_herd_decay_processor.parquet (innovation_substantiveness{track}, 源自 stage 21 三家投票)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking and Finance
  vol: 164
  pages_or_artno: 107191
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
new_dois: []
---

## CORE

【构念与来源】
本家族是一个 bank-year 层的篇数计数, 度量在给定银行-年度内, 同时满足两个条件的银行金科报道篇数: 其一, 该篇报道在 Bian et al. (2021) 中文金融情感词典下被判为正面 (词典极性得分严格大于零); 其二, 该篇报道的"金融科技创新实质性" (innovation_substantiveness) 已被成功测量 — 即三家大模型投票判定给出了合法取值 (实质性 或 象征性) 而非缺测。之所以要把"正面"与"实质性已测量"两个条件叠在一起数, 是因为本计数不是一个独立的研究终点变量, 而是洗稿率 (washing ratio) 这一 cheap-talk 指标的同域分母 (same-domain denominator)。洗稿率的分子是"正面且象征性"的报道篇数, 分母若直接数全部正面报道, 就会把那些实质性分类失败 (投票平局、模型拒答、解析失败) 的报道也计入分母, 而这些报道因缺测永远进不了分子; 分类失败率一旦上升, 洗稿率就会被系统性稀释下偏, 制造出"银行没有洗稿"的假象。本家族正是为消除这一失配而构造的"分母只数被真正判读过的那批"计数, 使分子分母落在同一可测域上。

【方法学与计算】
计算分两级。篇章级: runner 在洗稿率前置步骤中, 对每篇报道构造指示列 _svd_bian_2021_pos{track}, 其值为 1 当且仅当两条件同时成立 — 该篇 Bian 词典得分大于零 (正面, _d_pos) 且该篇实质性已被成功测量 (实质性已测量掩码 _subst_measured)。这里存在一个关键的口径不对称, 必须准确理解: 只有正面判据是逐轨的, 实质性掩码不是。极性判据复用 Bian 词典的连续极性得分 bian_2021_score{track}, 逐轨在各自文本窗口 (full/ctx/ss) 上计算, 其构造遵循经典词典法 — 统计文本中正面与负面情感词的加权出现, 经否定翻转/程度副词/转折等语言学规则后归一, 得分为正即整体正面。而实质性已测量掩码 _subst_measured 在源码中恒由 innovation_substantiveness_full 单列派生 (runner 取 df['innovation_substantiveness_full'], 判其是否落在合法标签集 {实质性, 象征性} 内), 三轨的 _svd_bian_2021_pos_full/_ctx/_ss 共用这同一个 full 轨掩码, 并不存在 innovation_substantiveness_ctx 或 innovation_substantiveness_ss 的逐轨实质性标签参与本计数。这是 v3.2.0 的刻意设计 (裸 innovation_substantiveness 已删, 单独以 _full 作 main spec): 实质性是一篇报道的整体属性, 由 full 轨全文语境判读最稳, 无需随文本窗口重判。实质性标签本身来自 stage 21 三家大模型 (gpt54nano / gemini31 / deepseekv4) 对 W&Z (1994/1998) 实质性-象征性二分构念的多数投票; 缺测行经 astype(str) 会落到 'nan' 因而恒不入合法集, 自动被排除。bank-year 级: runner 的 _pool_svd_substvalid_counts 把同一 (target_bank, year) 内所有篇章的 _svd_bian_2021_pos{track} 按 sum 聚合, 并重命名为 bian_2021_pos_substvalid_count{track}。因列名以 _count_{track} 结尾, 它命中 balance_panel 的计数零填规则: 零新闻的银行-年度补零, 下游洗稿率除法在分母为零时经 _safe_ratio 优雅返回缺失而非报错。该列本身恒为非负整数, 但落盘 dtype 为 double 以容纳缺失哨兵。本计数是 Bian 词典这一"逐词典 (D2) 洗稿率通道"的分母, 与 LLM 投票 (方法 A)、单模型 (A2)、词典均值 (D)、BERT (E/E2)、高置信子样本 (F) 等并列方法各自的同域分母互不混用。

【文献定位】
本家族坐落在"计数型金融文本测度"与"象征性披露 (cheap talk / 洗稿) 度量"两条文献脉络的交汇处。词典侧, Loughran and McDonald (2011) 奠定了以领域专用词表而非通用心理学词表度量金融文本极性的范式, 其"负面词未必是负债"的洞见提示中文语境同样需要本土化词典; Bian et al. (2021) 正是在此思路下构造的中文金融情感词典, 为本家族提供正面判据的词表来源。Gentzkow et al. (2019) 在方法学层面系统化了"文本即数据"的统计处理, 强调计数向量作为文本表征基元的地位。作为计数变量, 本家族的下游计量须正视 Cohn et al. (2022) 关于金融中计数 (与类计数) 数据的告诫 — 计数分母的构造口径 (数谁、不数谁) 会直接改变以其为基的比率的分布形态与推断, 这恰是本家族强调"同域分母"的计量根据。构念定位上, 本计数服务的洗稿率属于 Bingler et al. (2024) 所刻画的"廉价话语"实证家族: 用文本测度区分"说了漂亮话"与"做了实质事", 度量披露与行动之间的脱耦。需要强调, 本家族并非情感强度的直接测度, 而是"正面且可判读"报道的规模计数, 它只在与分子配对成洗稿率后才承载 cheap-talk 语义。三轨 (full/ctx/ss) 是同一构念在不同文本窗口上的并排实现, 各自 just-identified、互为稳健性、不分主次, 严禁把三轨计数混入同一 over-identified 的 Hansen J 统计量; 留篇门控采用 full-only 口径 (一篇报道是否算作银行金科报道只看 full 轨语义验证), ctx/ss 为 conditional-on-full 的子集测度。 就实质性—象征性这一二分本身的当代同域应用而言, Huang 与 Ma (2024) 以金融科技发展为解释变量, 检验其对企业实质性绿色创新与象征性绿色创新的差异化影响, 在中国情境下明确采用该二分切分, 与本家族所依赖的 innovation_substantiveness 标签在概念界定与中文表述上直接对应, 表明这一二分在金融科技议题下已是被接受的实证切分方式, 从而为本计数的「实质性已测量」条件所预设的合法标签集提供了构念层的同域佐证。迁移边界须如实写明三点: 其一, 原文的实质与象征由专利类型 (发明专利 vs 实用新型与外观设计) 客观划分, 本家族则由三家大模型对单篇新闻报道的话语作直接判读, 判定机制与数据类型均不同; 其二, 原文主体为非金融上市公司且金融科技处于解释变量位置, 本家族主体为商业银行且金融科技是被报道的议题本身; 其三, 原文未构造任何比率型洗稿指标, 更未处理分类缺测所致的分子分母失配, 因此它只锚定本家族所用二分构念的合法性, 不锚定「同域分母」这一计量构造本身。
## VAR: bian_2021_pos_substvalid_count_full

【变体差分】
本列是 full 轨实现: 篇章级 Bian 词典极性判据 bian_2021_score_full 与实质性标签 innovation_substantiveness_full 均在"标题 prepend + 全文正文"这一最宽文本窗口上计算。full 轨扫描整篇报道全文, 因而"正面"与"实质性已测量"两个条件都在最大信息量的语境下判定, 计数的口径最宽、每格数值通常最大。full 轨在本项目中具有特殊的锚地位: 留篇门控 (2026-06-29 口径) 完全依据 full 轨的语义验证决定一篇报道是否算作"银行金科报道", 因此 full 轨的行宇宙即整个留篇集, ctx 与 ss 轨的行宇宙是它的子集。这意味着 full 轨计数是三轨中口径最完整、分母基数最大的一支, 是洗稿率 full 轨版本 washing_ratio_bian_full 的同域分母。作为分母, 它数的是"Bian 判正面且实质性分类成功"的 full 轨报道数, 与分子 (正面且象征性) 严格落在同一可测域, 消除分类失败导致的洗稿率下偏。本列与 ctx、ss 两列互为稳健性、不分主次: 三者各自 just-identified 并排进入各自的洗稿率通道, 严禁把 full 与 ctx/ss 的计数混入同一 over-identified 的 Hansen J。其与家族内其他词典 (jiang_2021 / yao_2021 / du_2022 / you_2018 / loughran) 的同名计数亦为并排的方法稳健性, 只在正面判据的词表来源上不同 (此处为 Bian 词典), 实质性掩码则三家投票共用。full 轨还具有一层特殊地位: 它所用的 innovation_substantiveness_full 实质性掩码, 正是 ctx 与 ss 两轨 _svd 指示所共用的那一个 full 轨掩码 (源码恒取 innovation_substantiveness_full, 无逐轨实质性标签); 因此三轨之间在实质性维度上完全同源, 仅 Bian 极性得分逐轨随文本窗口变化。

## VAR: bian_2021_pos_substvalid_count_ctx

【变体差分】
本列是 ctx (实体窗) 轨实现, 但其"逐轨"仅落在正面判据一侧, 须先讲清这一不对称。ctx 轨的 Bian 词典极性得分 bian_2021_score_ctx 在"标题 + 实体窗口"文本 (content_ctx, 以银行/金科实体出现处为中心的邻近窗口, 而非全文) 上计算; 而叠加的实质性已测量条件并不在 content_ctx 上重判 — 源码中三轨的 _svd 指示共用同一个由 innovation_substantiveness_full 派生的 full 轨实质性掩码, 不存在 innovation_substantiveness_ctx 这一逐轨实质性标签。因此本 ctx 列的准确语义是: 分子分母都要求"该篇 full 轨实质性分类成功", 而"是否正面"这一维度改用 ctx 窗口的 Bian 得分判定。相比 full 轨, ctx 把极性判读语境收窄到实体周边, 剔除远离核心实体的段落, 对"这篇报道是否在谈论该银行的金科正面进展"给出更聚焦但信息量更小的正面判定; 通常每格计数不大于同格 full 轨, 因为窗口内可触发的正面词更少 (而实质性掩码两轨相同, 差异只来自极性侧)。ctx 轨的行宇宙是 full 留篇集的子集 (conditional-on-full): 一篇报道先由 full 轨决定是否留篇, 留篇后其 ctx 轨极性列才在 ctx 窗口上计算; 若该篇 ctx 窗口内无触发, 相应指示为零而非借用 full 轨分母。本列作为 washing_ratio_bian_ctx 的同域分母, 与其分子 (ctx 轨正面且 full 轨象征性) 落在同一可测域。ctx 轨在本项目多个论文主轨中被刻意保留为首要稳健性轨 (full 切主、ctx 留稳健), 本计数正体现这一角色: 它与 full、ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混入同一 over-identified 的 Hansen J。需注意 ctx 后缀标识的是极性判据所依据的文本窗口, 而非情感强度、阈值或实质性口径的差异 — 词典权重与实质性投票口径 (恒 full) 与另两轨完全一致, 逐轨变化的只有 Bian 极性得分所扫描的文本范围。

## VAR: bian_2021_pos_substvalid_count_ss

【变体差分】
本列是 ss (同句) 轨实现, 同样只有正面判据逐轨、实质性掩码恒 full。ss 轨的 Bian 词典极性得分 bian_2021_score_ss 在"标题 + 银行∧金科同句共现窗口"文本 (content_ss) 上计算; 但叠加的实质性已测量条件仍来自 innovation_substantiveness_full 派生的同一 full 轨掩码, 而非在 content_ss 上重判实质性 (源码无 innovation_substantiveness_ss)。ss 窗口是三轨中最严格的文本范围, 只保留银行与金融科技实体在同一句子 (含 ±N 句半径, 由 config 的 ss_sentence_radius 控制, 默认 1) 内共现的语境, 因而其极性得分捕捉的是"报道在同一句里把该银行与金科并置"时的正面证据。相应地, ss 轨每格计数通常最小, 因为满足"ss 窗口内 Bian 判正面"且"full 轨实质性可判读"双重条件的报道最稀疏; 在早期试跑 T=2 的小样本上 ss 轨甚至可能出现大面积零值或退化, 属预期而非缺陷 (生产 T=19 语料上恢复正常)。ss 轨遵循镜像 ctx 的回退语义: 若某篇报道不存在银行与金科的同句共现, content_ss 回退为全文正文且 ss_is_fallback 置真, 极性得分随之在回退文本上计算, 计数仍以 full 留篇集为行宇宙分母基础。作为 washing_ratio_bian_ss 的同域分母, 本列与其分子 (ss 轨正面且 full 轨象征性) 严格同域。ss 轨的行宇宙同样是 full 留篇集的 conditional-on-full 子集。本列与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁把 ss 计数与其他两轨混入同一 over-identified 的 Hansen J。ss 后缀标识的是极性判据所依据的最严同句文本窗口, 而非独立的阈值、权重、滞后或实质性口径 — 词典与投票口径 (实质性恒 full) 与另两轨全同, 逐轨变化的只有 Bian 极性得分的扫描文本。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking and Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
<!-- rendered-citations:end -->
