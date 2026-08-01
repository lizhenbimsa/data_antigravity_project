---
family_id: F609
columns:
- washing_ratio_finbert2
- washing_ratio_finbert2_ctx
- washing_ratio_finbert2_ss
unit: 比率 (proportion, 分子分母皆为篇章计数, 值域 [0,1]; 分母为 0 时该行 NaN)
formula: washing_ratio_finbert2{track} = Σ 1[finbert2 判正面{track} ∧ 象征性] / Σ 1[实质性测量已完成的正面{track}文章]; 分子分母同域限定于 innovation_substantiveness_full 已测量出「实质性/象征性」标签的文章 (方法 E2, BERT_MODELS 中单模型 finbert2, argmax 标签口径, 三轨 full/ctx/ss 各自独立计算)
producer: pipeline\panel\runner.py (步骤 7h washing_cols 篇章级标记构造与聚合) ; pipeline\panel\export.py (Stata 变量标签挂载)
upstream:
- innovation_substantiveness_full
- finbert2_正面_full
- finbert2_正面_ctx
- finbert2_正面_ss
citations:
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
  vol: '80'
  issue: '2'
  pages_or_artno: 699-754
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1145/3711896.3737219
  type: wp
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: 'FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models'
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD 25)
  pages_or_artno: 5117-5128
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: 'The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions'
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_finbert2 测度的是"洗稿"(washing) 现象在 finbert2 单模型情感判读下的相对发生率: 在一批已被本地情感基调判为「正面」的银行金科报道中, 有多大比例同时又被 LLM 内容实质性分类判为「象征性」(symbolic) 而非「实质性」(substantive)。这个构念承袭 Westphal & Zajac (1994, 1998, Administrative Science Quarterly) 关于公司治理仪式性(symbolic)与实质性(substantive)采纳相分离的组织理论传统——企业/银行可以通过媒体曝光"塑造"正面形象, 而这种形象未必对应真实的技术或业务变革。落到金融文本分析的具体操作化, 它更直接呼应两条晚近文献: 一是"漂绿"(greenwashing) 测度文献, 如 Duchin, Gao & Xu (2025, The Journal of Finance) 用资产市场证据区分真实可持续行为与策略性披露, 以及 Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法从企业社会责任报告中识别漂绿信号; 二是最新的"AI 洗稿"文献, 如 Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 关于企业 AI 相关战略性披露与市场反噬的研究。本项目把这条逻辑迁移到银行×金融科技(fintech)报道语境: 如果一家银行大量出现"正面但象征性"的金科报道 (例如泛泛宣称"加快数字化转型""积极拥抱金融科技"却缺乏具体产品/投入/合作细节), 而实质性报道(具体项目、投资额、合作对象、技术落地)占比很低, 该行的媒体曝光就更可能是印象管理而非真实技术能力信号, washing_ratio_finbert2 数值越高, 这种失配越严重。

家族内共有 3 列, 全部 tier=standard: 无后缀 canonical(washing_ratio_finbert2)、_ctx、_ss。三者对应银行金科新闻文本的三种取样口径——full=标题+全文正文, ctx=标题+围绕目标银行/金科实体的窗口文本, ss=标题+银行与金科词同句(±N句窗)共现文本——按 CLAUDE.md「当前状态铁律」的三轨架构, 三者各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定。ss 轨在无银行∧金科同句共现时回退为全文正文 (镜像 ctx 的回退语义, 由 `ss_is_fallback` 指示位标记, 与 ctx 共享 n_articles 分母口径)。留篇门控口径遵循 full-only 铁律 (2026-06-29 起): 一篇报道是否被纳入"银行金科报道"样本只看 `llm_verified_full`, ctx/ss 是在该留篇集合子集上的 conditional-on-full 稳健性测度/per-track 独立计算, 而非独立的样本筛选轨道。

【方法学与计算】
producer 定位于 `pipeline\panel\runner.py` 步骤 7h (篇章级 washing_cols 构造) 与 `pipeline\panel\export.py` (Stata 变量标签挂载)。该 stage 注释把洗稿率变体家族标注为方法 A/A2/B/D/D2/E/E2/F 共 8 类构造原语的笛卡尔组合(方法 C、G 直接复用面板级已有变量, 不产生篇章级标记); washing_ratio_finbert2 属于方法 E2——「单个 BERT 模型」变体, 与方法 E(BERT 均值/多数票, 3 模型均值)相对, 是 canonical BERT-Avg 口径 washing_ratio_bert 的单模型稳健性拆解。E2 对每篇文章直接用 finbert2 该模型自身的 argmax 三分类标签判定「正面」, 不经过投票或均值聚合, 因此该列的口径粒度是 encode.BERT_MODELS 三模型互为稳健性梯子(finbert_cn/fin_sent_zh/finbert2)中最细的一支, 与三 LLM per-model 稳健性列(gpt54nano/gemini31/deepseekv4)呼应同一"per-model 独立、不设 ensemble 主轨"设计原则。

具体计算分两步。第一步(runner.py 步骤 7h)在文章级 DataFrame 上逐轨构造篇章级布尔标记: 分子标记 `_is_pos_symb{track}` = (finbert2 该轨判正面 == 1) ∧ (innovation_substantiveness_full 判「象征性」); 分母标记 `_svd_pos{track}`(subst-valid denominator, 分母同域计数) = (finbert2 该轨判正面 == 1) ∧ (innovation_substantiveness_full 已完成测量, 即标签属于「实质性」或「象征性」二者之一, 不含缺失/拒绝)。这里的 `_svd_*` 后缀命名直接对应 2026-06-11 的一次修复(fix omni-g-runner-10/14): 早期实现的分母是"全部正面文章", 但 innovation_substantiveness 判读本身会失败(LLM 拒绝分类、平局等), 失败样本的分子贡献恒为 0(因为进不了「象征性」这一支), 若分母仍照旧数入这些失败样本, 洗稿率就会被系统性稀释——分类失败越多, 洗稿率被人为拉低, 这是测量伪影而非真实事实。`_svd_*` 把分母收窄到"实质性/象征性标签确实测出来了"的正面文章子集, 分子分母同域, 避免了这种失配。这一修复对全部方法 A/A2/E/E2 等以「正面 ∧ 象征性 / 正面(已测量)」为结构的分支同等生效。

第二步在面板聚合阶段, 对同一银行-年份分组求和后相除: washing_ratio_finbert2{track} = Σ`_is_pos_symb{track}` / Σ`_svd_pos{track}`, 该银行-年该轨若分母为 0(无任何"实质性已测量的正面 finbert2 文章"), 该格记 NaN(而非人为置 0 或跳过), 避免零除稀释解读为洗稿率极低。三轨 (full/ctx/ss) 各走一遍上述两步, 互相独立、互不借用彼此分母, 严格遵循三轨架构铁律。

is_positive 相关判读列在流水线中是 nullable Int8, NaN 代表测量失败/平局/被拒绝而非"非正面"; 判定式用 `fillna(0) == 1` 显式把 NaN 视为「非正面」参与分子(不参与)判定, 但不参与分母的正面计数(因为分母同样要求 `== 1`), 这一写法避免了把测量失败误算作正面文章的隐性偏误。

家族内还存在多个平行方法构造出的其它洗稿率列(washing_ratio 无模型后缀=方法 A LLM 多数投票、washing_ratio_dict=方法 D 词典均值、washing_ratio_bert=方法 E BERT 均值、washing_ratio_hc=方法 F 高置信度子样本), 它们与 washing_ratio_finbert2 分属不同的构造方法笛卡尔轴, 彼此是互为稳健性的并排测度而非同一测度的不同精度, 不应在回归中同时作为多重内生解释变量塞入同一识别方程。

【文献定位】
本测度的理论根基是组织社会学的"解耦"(decoupling)传统——Westphal & Zajac (1994, 1998, Administrative Science Quarterly) 最早系统区分了公司治理实践的"采纳"(symbolic adoption, 姿态性)与"实施"(substantive implementation, 实质性), 指出组织可以为满足外部制度压力而仪式性采纳某种做法, 却在实际运营中不落实, 这正是本家族"正面但象征性"文章占比构念的直接理论来源, 也支撑了从新闻文本反推企业印象管理强度这一操作化路径。在识别洗稿/漂绿的具体计量文献中, Duchin, Gao & Xu (2025, The Journal of Finance) 提供了资产市场证据区分真实可持续性投资与策略性披露的顶刊范例, Gorovaia & Makrominas (2024, European Financial Management) 展示了用 NLP 从企业文本中识别漂绿信号的可操作路径, 二者共同为"用文本分类交叉表构造洗稿率"这一方法论提供了当代校验; Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 把这一逻辑延伸到 AI 相关披露语境, 印证了 washing 构念向金融科技领域迁移的合理性。finbert2 模型本身出自 Xu et al. (2025, KDD '25), 是面向中文金融文本专门微调的双向编码器, 相较通用 BERT 或英文金融 BERT, 更贴合本项目银行×金科中文新闻语料的领域特征, 是三 BERT 模型稳健性梯子中的国产金融领域专用模型代表。BERT 情感底层测度的领域方法学地位另可追溯到词典法与机器学习法的比较文献(Du et al. 2022, Review of Finance 之中文金融情感词典即为词典轨的对照基准), washing_ratio_finbert2 与词典轨 washing_ratio_dict、LLM 轨 washing_ratio 共同构成方法三角互证。

## VAR: washing_ratio_finbert2

【变体差分】
本列是家族 canonical 无轨道后缀列, 采用 full 轨文本(标题+全文正文)。它把 finbert2 单模型在全文语境下的正面判定 (源自文章级 2-class 概率列 `finbert2_正面_full`, 经 argmax 极性指示函数转为布尔标记, 而非独立的 signed tone 列) 与 innovation_substantiveness_full 的象征性/实质性标签相交, 分子 = 全文正面且象征性文章数, 分母 = 全文正面且实质性已测量文章数。作为三轨中的一支, 它与 _ctx/_ss 并排、互为稳健性、不分主次, 对应留篇门控 full-only 铁律下的主口径样本(该行是否入选"银行金科报道"由 `llm_verified_full` 单独决定, 与本列自身情感判定无耦合)。方法轴上, 它区别于家族其它 E/E2/A/D/F 方法列的关键在于「单模型 finbert2 + argmax」——不经跨模型投票或均值平滑, 因此比 washing_ratio_bert(BERT 3 模型均值)更贴近 finbert2 这一具体模型的判读噪声与偏误特征, 是跨模型稳健性检验中的一个独立观测点, 须与 finbert_cn/fin_sent_zh 对应的同族列并列报告而非相互替代。

在解读上须留意两个刻度。第一, finbert2 是面向中文金融文本专门微调的双向编码器(Xu et al. 2025, KDD '25), 相较 fin_sent_zh、finbert_cn 两个平行 BERT 情感模型, 它在正面/负面/中性三分类的判读阈值和领域先验并不完全一致, 因此本列与另两个单模型 washing_ratio 变体(finbert_cn/fin_sent_zh 后缀列)在绝对水平上不必然可比, 跨模型比较应优先看标准化后的回归系数而非原始占比水平, 这一提醒与 CLAUDE.md「BERT 分布形状五族」条目下阈值/占比不可跨模型直接比较的铁律一脉相承。第二, 该列的分母同域限定(`_svd_pos_full`)意味着它只在"实质性/象征性标签已被 LLM 成功测出"的正面文章子集上计算, 一家银行若该子集样本量很小(例如某年报道总量本就稀少, 或多数报道被判定为中性/负面而非正面), 该格更容易因小样本波动而不稳定, 使用者在做横截面比较或构造滞后项时应结合分母端的 `_svd_pos_full` 计数一并核查, 避免把分母稀薄导致的噪声误读为真实洗稿信号的变化。

## VAR: washing_ratio_finbert2_ctx

【变体差分】
本列采用 ctx 轨文本(标题+围绕目标银行/金科实体的窗口文本), 分子分母的判正面来源换成文章级 2-class 概率列 `finbert2_正面_ctx`(经 argmax 极性指示函数转为布尔标记), 象征性/实质性标签仍固定引用 innovation_substantiveness_full(该分类维度在流水线中只在 full 轨判定, 未逐轨复算), 三轨差异仅体现在"正面"判定所依赖的文本窗口, 而非象征性/实质性标签本身的轨道。ctx 轨的行样本是 full 留篇集合的子集(conditional-on-full), 在无法定位实体窗口或窗口退化为空文本时该文章的 ctx 情感判定按 `ctx_is_fallback` 指示的规则回退为全文口径。本列与 canonical 列(_full)、_ss 列各自 just-identified 并排, 是同一构念在更聚焦局部语境下的稳健性平行测度, 用于检验洗稿率结论是否被全文中大段无关内容稀释或掩盖。

ctx 轨的实质意义在于把"正面"判定的证据来源收窄到实体窗口附近, 而不是让 finbert2 在一整篇可能夹杂大量无关新闻背景、行业综述、其它银行事迹的长文里去提炼语气。若一家银行的正面语气主要来自与自身、金科业务紧密相关的段落, full 轨与 ctx 轨的判定应大体一致; 若两者出现系统性分歧(例如 ctx 轨判正面比例明显低于 full 轨), 则提示该行的正面色彩更多来自文章泛泛的行业景气叙事而非其自身报道段落, 这本身也是一种值得关注的洗稿信号补充维度, 但不应被单独当作对 canonical 列的"修正"或"更精确版本"使用——三轨在方法论上地位对等, 差异是信息而非误差。使用者在做跨轨敏感性检验时, 应把 washing_ratio_finbert2、washing_ratio_finbert2_ctx 作为并列稳健性列同时报告, 而不是取其一作为主设定、另一作为附录检验。

## VAR: washing_ratio_finbert2_ss

【变体差分】
本列采用 ss 轨文本(标题+银行与金科词同句或 ±N 句窗共现的文本片段, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1), 分子分母的判正面来源为文章级 2-class 概率列 `finbert2_正面_ss`(经 argmax 极性指示函数转为布尔标记)。当某篇文章不存在银行∧金科同句共现时, ss 轨镜像 ctx 轨的回退语义: `content_ss` 退化为全文正文, `ss_is_fallback` 置 True, 与 ctx 共享 n_articles 分母口径, 这类回退文章在 ss 轨情感判定上等价于 full 轨(信息集相同), 但仍作为独立的 ss 轨观测参与聚合, 不与 full 轨的分子分母混算。ss 轨相较 ctx 轨的判定窗口更窄——要求银行与金科实体真正同句(或紧邻句)出现, 是三轨中共现约束最严格的一支, 用于检验洗稿率结论是否依赖于把银行与金科话题"硬拉"到同一句所带来的语境紧凑性, 是 full/ctx 之外的第三条并排稳健性检验路径, 三者共同构成互为稳健性、禁止混入同一识别方程的完整三轨族。

由于 ss 轨的共现约束比 ctx 轨更严, 在早期试跑 T=2 样本这类报道基数较小的语料上, 该列比 canonical 列与 ctx 列更容易出现分母 `_svd_pos_ss` 稀薄甚至为零(整年该行没有一篇"银行与金科同句共现且判为实质性已测量正面"的文章), 此时该银行-年格记 NaN 属预期表现而非缺陷, 使用者不应将其误读为"零洗稿"。在真实生产语料(T=19, 千万级报道量)上, 随着单行样本量增大, ss 轨分母稀薄问题预期显著缓解。ss 轨的方法论价值在于剥离"银行与金科被同时提及但实际相隔甚远、语义上并不真正相关"的噪声个案, 是三轨中对"洗稿"构念界定最保守、最不容易把泛泛提及误记为真实曝光的一支, 应与 full/ctx 两轨一并报告, 三者的一致性或分歧共同构成对洗稿率结论稳健性的完整证据链。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD 25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
<!-- rendered-citations:end -->
