---
family_id: F233
novelty_exempt_rationale: "exc_ 前缀家族为'剔除疑似退出覆盖媒体'这一样本选择稳健性稳健变体, 测度定义与词典依据均沿用母族 bian_2021_score 及 Bian et al.(2021) 词典原始文献, 非独立新构念, 无需追新文献。"
columns:
- exc_bian_2021_score_ctx
- exc_bian_2021_score_full
- exc_bian_2021_score_hw_ctx
- exc_bian_2021_score_hw_full
- exc_bian_2021_score_hw_ss
- exc_bian_2021_score_ss
- exc_bian_2021_score_w_ctx
- exc_bian_2021_score_w_full
- exc_bian_2021_score_w_ss
unit: 无量纲 (剔除疑似退出覆盖媒体后, 银行-年度内 Bian 2021 词典情感得分的组内均值; 基线臂落在 [-1,1], 加权臂为得分×权重的均值不再归一)
formula: "bian_2021_score{track} = Σ(final_score)/Σ|final_score| ∈ [-1,1] (Bian 2021 词典极性 + 否定/程度/转折全语言学规则); bian_2021_score_w{track} = bian_2021_score{track} × mention_density_weight (VW); bian_2021_score_hw{track} = bian_2021_score{track} × herd_weight{track} (HW); exc_bian_2021_score[_hw|_w]{track} = mean_{article ∈ bank-year ∧ media ∉ ceased_set} (对应文章级得分); ceased_set = confirmed ∪ suspected (last_year < sample_max - 2 ∧ n_articles ≥ 10)"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性块 C.4, mean over df_alive; ceased 判定见 detect_defacto_cessation)
upstream:
- 22_tone_words.parquet (bian_2021_score_full / _ctx / _ss)
- 24_herd_decay.parquet (herd_weight_full / _ctx / _ss, 供 _hw 臂)
- runner 步骤 3b/3d 预计算文章级加权列 (bian_2021_score_w / _hw)
citations:
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画一个银行-年度层面的媒体幸存者偏差稳健性测度: 在剔除疑似退出话题覆盖的媒体来源之后, 用 Bian et al. (2021) 中文金融情感词典逐篇算得的报道情感得分, 在同一银行同一年度内对存活媒体的报道求组内均值。名称四段各有所指: exc 是 exclusion 的缩写, 指本量的样本域已剔除疑似停止覆盖银行-金科话题的媒体来源, 是相对全样本情感均值的保守替代口径; bian_2021 指底层词典为 Bian, Jia, Li 与 Yan (2021) 面向会计与金融文本构建的中文金融情感词典; score 指文章级测度是该词典的归一化情感极性得分, 基线取值落在 [-1, +1]; 无后缀 (基线)、_hw、_w 三支则区分文章级得分进入组内均值前是否先施加权重。因此本家族不是全样本情感, 而是"排除疑似退出覆盖媒体"这一稳健性维度上的替代情感: 它与配套的 ceased_media_frac (退出媒体文章占比)、n_articles_exc (排除后文章数) 共同支持 Stata 侧对媒体来源消失所致选择偏误的系数稳定性检验。

【构念与来源续】
之所以要构造这一排除口径, 是因为以媒体情感为核心解释变量的面板研究里, 覆盖某银行-金科话题的媒体来源会随时间进入或退出; 若某些来源在样本后期悄然停止覆盖 (无论是真实停刊, 还是只是不再报道该话题), 而分析仅用存活来源, 则情感度量会向存活媒体的语气系统性倾斜, 引入幸存者偏差, 并污染以媒体暴露为基础的 Bartik 型工具变量。本家族把疑似退出的媒体保守地整体剔出后重算情感均值, 使研究者可将其与含全部媒体的基准情感并列, 检验主结论是否被媒体退出这一样本选择所驱动。诚实披露口径: 排除集 ceased_set = confirmed ∪ suspected, 其中 suspected 由数据驱动规则判定 (某媒体在银行-金科子集上的最后出现年份早于样本末年减两年, 且累计报道数不少于十篇), 未经外部登记核验的 suspected 亦全量进入排除集; 度量的是"话题覆盖退出"而非经证实的报纸停刊, 故下游列只可解读为疑似退出覆盖的保守稳健性口径, 不可在论文中表述为严格停刊口径。

【方法学与计算】
计算链路分四段。第一段在 stage 22 词典法: 对每篇报道分词后在 Bian et al. (2021) 词典上逐词匹配, 命中情感词依次施加三条语言学规则 —— 否定词在其后固定窗口内翻转极性、程度副词按倍率缩放幅值、转折词在从句作用域内放大后半句, 遇句末标点重置规则状态; 每个情感词得 final_score, 文章级得分归一化为 Σ(final_score)/Σ|final_score| ∈ [-1, +1]。第二段在面板 runner 预计算文章级加权列: VW 臂 (步骤 3b) 令文章级得分乘以提及密度权重 mention_density_weight 得 bian_2021_score_w{track}; HW 臂 (步骤 3d) 令其乘以羊群衰减权重 herd_weight{track} = 1/(1 + n_similar_articles{track}) 得 bian_2021_score_hw{track}; 基线臂不加权。第三段是停刊检测 (detect_defacto_cessation): 按媒体聚合首末出现年份与报道数, 标记疑似退出集 ceased_set。第四段在 attention_media 停刊稳健性块 C.4: 取存活子集 df_alive (媒体不在 ceased_set 的报道), 对匹配 _SCORE_PATTERNS 且非 mw/idf 变体的文章级得分列, 按目标银行-年度分组求均值, 冠以 exc_ 前缀落盘。注意本家族聚合口径是组内均值 (mean) 而非求和, 与 hw_sum 家族的分子求和口径不同; 留篇门控采用 full-only 口径 (2026-06-29), 报道是否计入某银行某年宇宙由其 full 轨是否被判为一篇银行金科报道决定, 三轨在该留篇集合上分别计列。

【文献定位】
本测度的方法学谱系由三支文献锚定。词典本身取 Bian et al. (2021): 通用英文金融词典直译到中文会因语言与制度差异失准, 该文据此构建中文金融领域专用情感词典。词典的领域特异性价值在顶刊层面由 Du et al. (2022) 进一步确证 —— 他们指出语言与领域特异性对中文金融情感度量至关重要, 通用词典在中文语料上系统性偏误, 这正是本管道选用中文金融专用词典而非直译词典的依据。逐词施加否定、程度、转折规则并作从句级作用域重置, 遵循 Taboada et al. (2011) 确立的词典法情感分析范式。将词典法结果单独成轨并与机器学习及大模型法并置互证, 呼应 Frankel, Jennings 与 Lee (2022) 关于披露情感的机器学习法与词典法互为稳健性的先例, 以及 van Atteveldt, van der Velden 与 Boukes (2021) 对人工标注、词典法与机器学习法效度的横向比较; Barbaglia et al. (2025) 亦重申词典法在经济文本上的可解释与可复现优势。需强调: 本家族的三条聚合权重臂 (基线均值、HW 羊群加权均值、VW 提及密度加权均值) 与三条文本轨 (full/ctx/ss) 均各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同权重臂、不同轨或不同词典混进同一 over-identified Hansen J 检验。排除疑似退出媒体这一样本口径本身亦是相对全样本情感的规格稳健性并排, 而非主口径的替代。 就此一样本口径的现实动机, Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 表明媒体退出并非无害的样本损耗, 而是有经济后果的样本组成变化, 这正锚定本族先剔除 ceased_set 中的媒体、再在银行-年度内取均值这一环节的构念动机。迁移边界须诚实说明: 该文的停刊判定取自外部事件数据、DV 为本地股票交易活动, 且以停刊作为识别冲击使用; 而本族 ceased_set 由 detect_defacto_cessation 自语料内部推断 (confirmed ∪ suspected: last_year < sample_max − 2 且 n_articles ≥ 10), 是「疑似退出覆盖」的保守代理而非严格停刊事实, 用途仅限稳健性子样本, 不承担任何识别功能; 该文为工作论文, 尚未经同行评审。
## VAR: exc_bian_2021_score_full

【变体差分】
本列是基线权重臂的 full (全文) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的未加权文章级 bian_2021_score_full 求银行-年度组内均值。文本口径为标题 prepend 后的报道全文正文, 情感词典在完整标题加正文上匹配 Bian et al. (2021) 词典并施加否定/程度/转折全规则得 bian_2021_score_full ∈ [-1, +1]; 因是均值聚合基线臂, 本列同样落在 [-1, +1], 直接可读为"存活媒体对该银行该年的平均语调"。与配套的 exc_bian_2021_score_w_full (提及密度加权臂) 与 exc_bian_2021_score_hw_full (羊群加权臂) 的差别只在进入均值前是否加权: 本列不加权, 每篇报道等权贡献。full 轨在三轨中承担留篇门控职责 (full-only 口径, 2026-06-29), 故其行宇宙是全集、ctx 与 ss 轨在其子集上条件计列。本列与全样本情感 (不带 exc_ 前缀的对应列) 的唯一差别是样本域: 本列已把 ceased_set 内媒体的报道整体剔除, 因而是媒体退出稳健性并排轨, 与全样本情感各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。作为基线权重臂, 本列口径最直白, 是解读另两条加权臂 (HW/VW) 的参照系: 若排除退出媒体后本列与全样本情感符号一致、量级相近, 则说明主结论未被媒体退出的样本选择驱动; 若两者显著背离, 则提示存在幸存者偏差, 需谨慎解读以全样本情感为核心变量的回归。本列聚合口径为组内均值而非分子求和, 故可直接读作平均语调, 无需再除以权重合计还原。

## VAR: exc_bian_2021_score_ctx

【变体差分】
本列是基线权重臂的 ctx (实体窗) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的未加权文章级 bian_2021_score_ctx 求银行-年度均值。文本口径为标题 prepend 后的实体上下文窗片段 content_ctx, 只保留银行等目标实体邻近窗口内的文本, 剔除与实体无关段落, 再在此片段上算 Bian et al. (2021) 词典得分。与本家族 full 轨的差别在文本轨而非权重: 本列把情感信号收窄到实体近旁, 削弱远端无关文本对语调的稀释, 是 full 轨的规格稳健性并排轨; 因取均值聚合基线臂, 本列同样落在 [-1, +1]。ctx 轨不承担留篇门控 (门控为 full-only), 其行宇宙是 full 留篇集的子集, 按 ctx 轨自身列照算。本轨情感判据所用的实体窗与 stage 13 共现硬过滤、以及 ss 轨的严格同句判据是三套不同口径, 彼此不可复用。与全样本 ctx 情感的差别仅在样本域已剔除 ceased_set。ctx 与 full、ss 各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J。相对 full 轨, 本列把情感读数聚焦在与银行直接相关的文本片段上, 因而对识别"针对该银行的语调"更具构念针对性, 但代价是有效文本更短、组内方差更高; 当某银行某年存活报道稀疏时, 本列可能因分母小而不稳。作为基线权重臂的 ctx 轨, 本列亦是同轨 HW 列与 VW 列的未加权参照系, 三臂并读可分离"媒体退出""跟风降权""提及密度"三条独立稳健性通道各自对情感均值的影响。

## VAR: exc_bian_2021_score_ss

【变体差分】
本列是基线权重臂的 ss (同句) 轨, 三轨中文本判据最严: 剔除疑似退出覆盖媒体后, 对存活报道的未加权文章级 bian_2021_score_ss 求银行-年度均值。文本口径为标题 prepend 后的银行与金科同句共现片段 content_ss, 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本。回退语义镜像 ctx: 当某报道无银行与金科同句共现时 content_ss 回退为全文正文、ss_is_fallback 置 True。ss 轨的构念最贴近"银行与金融科技在同一句子内被同时提及时的情感倾向", 但也最易受回退稀释; 在早期试跑 T=2 小样本上, ss 轨因同句共现稀疏可能大面积回退或零方差, 属预期退化, 生产期 T=19 恢复正常。与本家族其余轨的差别在文本轨 (最严同句判据) 而非权重臂 (本列仍为未加权均值基线臂)。ss 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集。ss 的严格同句判据与 ctx 的实体窗判据、stage 13 的邻近共现判据均为不同口径, 三者不可互相复用。ss 与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。作为基线权重臂的 ss 轨, 本列是同轨 HW 列与 VW 列的未加权参照系。ss 轨的立意是把情感读数锁定在银行与金融科技被同时提及的那句话上, 从而最直接刻画银行-金科关联报道的语气; 但正因判据最严, 本列对回退最敏感, 在存活报道少或同句共现稀疏时最易退化为全文口径, 因此它在三轨中提供的是最保守、也最需配合回退率披露的稳健性证据。

## VAR: exc_bian_2021_score_hw_full

【变体差分】
本列是羊群加权 (HW) 臂的 full (全文) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的羊群加权文章级得分 bian_2021_score_hw_full 求银行-年度均值。相对同轨的基线列 exc_bian_2021_score_full, 唯一差别是文章级得分进入均值前先乘以 full 轨羊群衰减权重 herd_weight_full = 1/(1 + n_similar_articles_full): 系统按同年早前存在多少篇高度相似 (疑似转抄、回声式跟风) 的报道对该篇降权, 转抄越多权重越低、越接近独立首发权重越接近 1。因此本列是"排除退出媒体"与"羊群降权"两条稳健性维度的叠加: 既剔除疑似退出媒体, 又对跟风转抄式报道降权, 使得情感均值更贴近独立首发信息。因乘了小于等于 1 的权重, 本列不再严格归一到 [-1, +1], 是加权得分的均值。羊群相似度在全文空间统计, 通常最密, 故 full 轨的降权幅度往往强于 ctx/ss 轨。HW 臂与 VW 臂 (提及密度加权)、基线臂刻画不同稳健性维度: HW 按信息独立性降权, VW 按提及密度加权, 三臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 三轨与排除口径同理。本列的构念可读作"在只看存活媒体、且对跟风转抄降权之后, 该银行该年的加权平均语调": 它同时抑制了两类可能扭曲情感的力量 —— 退出媒体带来的样本选择、以及回声式报道带来的信息重复计数。若本列与同轨基线列 exc_bian_2021_score_full 走势一致, 说明羊群降权未实质改变情感结论; 若两者背离, 则提示跟风转抄在该样本中密集, 情感均值被回声报道放大, 须以羊群加权口径为更稳健的读数。

## VAR: exc_bian_2021_score_hw_ctx

【变体差分】
本列是羊群加权 (HW) 臂的 ctx (实体窗) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的羊群加权文章级得分 bian_2021_score_hw_ctx 求银行-年度均值。相对同轨基线列 exc_bian_2021_score_ctx, 差别是先乘以 ctx 轨羊群权重 herd_weight_ctx —— 在 ctx 超级文档 (content_ctx 原样拼接、剔除回退行、不走标题通道以避免双标题污染) 上做 TF-IDF 相似度所得的独立性降权。因此本轨的情感判据 (实体窗) 与降权判据 (实体窗相似度) 同在实体窗空间, 与 full 轨在全文空间的口径系统性不同。相对 full 轨的 HW 列, 本列把情感与降权双双收窄到实体近旁, 在语义上更贴近"关于该银行的这段话是正面还是负面、且是否为跟风转抄", 代价是可用文本更短、方差更高。因乘了权重, 本列不再严格归一到 [-1, +1]。本列同时叠加"排除退出媒体"与"羊群降权"两维稳健性, 并处于 ctx 文本轨。HW/VW/基线三臂、full/ctx/ss 三轨、排除与全样本两口径均各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。相对 full 轨的 HW 列, 本列的一个实质差别是: full 轨在整篇层面统计相似度, 回声报道更易被 TF-IDF 捕获, 降权最强; ctx 轨只在实体窗片段上比相似度, 只有围绕该银行的表述高度雷同才会触发降权, 因此本列对"针对该银行的跟风表述"更敏感、对与银行无关段落的雷同不敏感, 这使它在识别银行专属回声报道上比 full 轨更精准。

## VAR: exc_bian_2021_score_hw_ss

【变体差分】
本列是羊群加权 (HW) 臂的 ss (同句) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的羊群加权文章级得分 bian_2021_score_hw_ss 求银行-年度均值。相对同轨基线列 exc_bian_2021_score_ss, 差别是先乘以 ss 轨羊群权重 herd_weight_ss (在 ss 超级文档上做 TF-IDF 相似度所得)。当 ss 文本大面积回退到全文时 herd_weight_ss 会趋近 herd_weight_full, 此为预期退化: 回退率越高、真三轨独立性越弱, 日志会告知。本列是三轨中文本判据最严 (同句共现) 且叠加羊群降权与排除退出媒体两维稳健性的组合列; 因乘了权重, 不再严格归一到 [-1, +1]。在早期试跑 T=2 上, ss 轨同句共现稀疏叠加羊群降权可能出现零方差或全回退, 属预期退化, 生产期 T=19 恢复正常。解读本列须与回退率一并披露: 一旦回退, 该篇实际用的是全文文本与全文相似度, ss 轨对 full 轨的独立性随回退率上升而衰减。HW/VW/基线三臂、三轨、排除口径均各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。本列是本家族叠加规格最深的组合之一 (最严同句文本轨 × 羊群降权 × 排除退出媒体), 因而在生产 T=19 全量语料上提供的是最保守的情感读数: 它要求报道既来自存活媒体、又在同句层面提及银行与金科、还要在同句相似度空间上非跟风, 才对情感均值作显著贡献; 满足全部条件的报道越少, 本列越接近纯"独立首发的银行金科同句语调"这一理想构念。

## VAR: exc_bian_2021_score_w_full

【变体差分】
本列是提及密度加权 (VW, volume/mention-density weighted) 臂的 full (全文) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的提及密度加权文章级得分 bian_2021_score_w_full 求银行-年度均值。相对同轨基线列 exc_bian_2021_score_full, 唯一差别是文章级得分进入均值前先乘以提及密度权重 mention_density_weight (runner 步骤 3b 预计算): 该权重按报道对目标银行的提及密度加权, 提及越密集的报道对银行-年度情感的贡献越大, 反映"该篇有多聚焦于这家银行"。因此本列是"排除退出媒体"与"提及密度加权"两维稳健性的叠加; 因乘了权重, 本列不再严格归一到 [-1, +1], 是加权得分的均值。VW 臂与 HW 臂 (羊群加权)、基线臂刻画彼此正交的加权维度: VW 按银行提及聚焦度加权, HW 按信息独立性降权, 基线不加权; 三臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。full 轨承担留篇门控 (full-only), 行宇宙为全集。本列与全样本 VW 情感的差别仅在样本域已剔除 ceased_set, 三轨与排除口径同理各自 just-identified 并排。本列的构念可读作"在只看存活媒体、且按报道对该银行的聚焦程度加权之后, 该银行该年的加权平均语调": 它同时抑制了退出媒体的样本选择, 又相对压低了一带而过、蜻蜓点水式提及的报道对情感的稀释。若本列与同轨基线列 exc_bian_2021_score_full 走势一致, 说明提及密度未实质改变情感结论; 若两者背离, 则提示低聚焦报道在该样本中拉偏了等权情感均值, 须以提及密度加权口径为更贴近"关于本行的报道语调"的读数。作为 VW 臂的 full 轨, 本列亦承担该臂的留篇门控参照。

## VAR: exc_bian_2021_score_w_ctx

【变体差分】
本列是提及密度加权 (VW) 臂的 ctx (实体窗) 轨: 剔除疑似退出覆盖媒体后, 对存活报道的提及密度加权文章级得分 bian_2021_score_w_ctx 求银行-年度均值。相对同轨基线列 exc_bian_2021_score_ctx, 差别是先乘以提及密度权重 mention_density_weight; 相对 full 轨的 VW 列, 差别在文本轨 —— 本列情感得分在标题 prepend 后的实体上下文窗片段 content_ctx 上计算, 把情感信号收窄到实体近旁。因此本列同时处于"排除退出媒体""提及密度加权""实体窗文本轨"三重规格上, 是 full 轨 VW 列的规格稳健性并排轨。因乘了权重, 本列不再严格归一到 [-1, +1]。ctx 轨不承担留篇门控 (full-only), 行宇宙为 full 留篇集子集, 按 ctx 轨自身列照算。ctx 的实体窗判据与 ss 的严格同句判据、stage 13 的邻近共现判据是三套不同口径, 不可复用。VW/HW/基线三臂、full/ctx/ss 三轨、排除与全样本两口径均各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。本列的立意是: 一篇报道若在实体窗内密集提及该银行, 说明它真正聚焦这家银行, 其情感读数应比一带而过的报道更有分量; 提及密度加权正是把这一直觉物化。与 HW 臂正相反, VW 臂不降权任何报道, 而是相对放大高聚焦报道的贡献, 二者刻画的稳健性维度彼此正交: HW 问"是否独立首发", VW 问"是否聚焦本行", 基线则等权。三臂并读可分离这两条正交通道各自对情感均值的移动方向。

## VAR: exc_bian_2021_score_w_ss

【变体差分】
本列是提及密度加权 (VW) 臂的 ss (同句) 轨, 是本家族文本判据最严且加权的组合列: 剔除疑似退出覆盖媒体后, 对存活报道的提及密度加权文章级得分 bian_2021_score_w_ss 求银行-年度均值。相对同轨基线列 exc_bian_2021_score_ss, 差别是先乘以提及密度权重 mention_density_weight; 相对 full/ctx 的 VW 列, 差别在文本轨 —— 情感得分在标题 prepend 后的银行与金科同句共现片段 content_ss 上计算, 仅保留目标银行与金融科技词在同一句子且落在 ss_sentence_radius (默认 ±1 句) 窗内共现的文本。回退语义镜像 ctx: 无同句共现时 content_ss 回退全文、ss_is_fallback 置 True。因此本列同时叠加"排除退出媒体""提及密度加权""最严同句文本轨"三重规格; 因乘了权重, 不再严格归一到 [-1, +1]。在早期试跑 T=2 上同句共现稀疏可能全回退或零方差, 属预期退化, 生产期 T=19 恢复正常; 解读须与回退率一并披露。VW/HW/基线三臂、三轨、排除口径均各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。本列是本家族中同句判据最严且以提及密度加权的组合列: 它把情感读数既锁定在银行与金科同句共现的文本上, 又相对放大对该银行提及密集的报道, 因而对"高聚焦、强关联"的银行金科同句语调最敏感。作为 VW 臂的 ss 轨, 本列与同轨基线列、HW 列并读, 可在最严文本判据下同时观察"提及密度放大"与"羊群降权"两条正交加权通道对情感结论的影响, 是本家族提供的最细粒度稳健性证据之一。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
