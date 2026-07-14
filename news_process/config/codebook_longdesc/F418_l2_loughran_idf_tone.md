---
family_id: F418
columns:
- loughran_idf_tone_app_ctx
- loughran_idf_tone_app_full
- loughran_idf_tone_app_ss
- loughran_idf_tone_ctx
- loughran_idf_tone_full
- loughran_idf_tone_hw_ctx
- loughran_idf_tone_hw_full
- loughran_idf_tone_hw_ss
- loughran_idf_tone_mw_ctx
- loughran_idf_tone_mw_full
- loughran_idf_tone_mw_ss
- loughran_idf_tone_ss
- loughran_idf_tone_std_ctx
- loughran_idf_tone_std_full
- loughran_idf_tone_std_ss
- loughran_idf_tone_tech_ctx
- loughran_idf_tone_tech_full
- loughran_idf_tone_tech_ss
- loughran_idf_tone_vw_ctx
- loughran_idf_tone_vw_full
- loughran_idf_tone_vw_ss
unit: 语调得分 (连续, 逐篇 IDF 加权极性分聚合后取 bank-year 均值/加权均值, 理论上界约 [-1,1], 实际因 IDF 缩放略窄)
formula: "逐篇: loughran_idf_score{track}(a) = Σ_{w∈loughran词典命中(a,track)} sign(w)×idf(w)×ling_rule(w,a) / Σ_{w∈loughran词典命中(a,track)} idf(w)×ling_rule(w,a) 的语料级归一化版本 (idf(w)=smooth-IDF 在 content_full 语料上计算, 经均值归一化使量级 ≈ 等权版、并 Winsorize; ling_rule 含否定翻转/程度副词/转折规则叠加, 与 IDF 权重正交); bank-year 聚合: loughran_idf_tone{track} = mean_{a∈bank-year} loughran_idf_score{track}(a) (canonical, 等权跨篇均值); loughran_idf_tone_std{track} = Z-score 标准化版 (loughran_idf_score 逐篇先在全样本标准化, 再取 bank-year 均值); loughran_idf_tone_hw{track} = Σ herd_weight{track}(a)×loughran_idf_score{track}(a) / Σ herd_weight{track}(a) (herd_weight=1/(1+n_similar_articles{track}), 出自 stage 24 herd_decay_processor); loughran_idf_tone_mw{track} = Σ media_weight(a)×loughran_idf_score{track}(a) / Σ media_weight(a) (media_weight 出自 config/media_weights.json 按来源媒体权威度排名百分位, 缺表则退默认权重); loughran_idf_tone_vw{track} = Σ mention_density(a)×loughran_idf_score{track}(a) / Σ mention_density(a) (mention_density 出自 stage 11 news_salience 逐篇银行提及密度); loughran_idf_tone_app{track} / loughran_idf_tone_tech{track} = 与 canonical 同聚合式, 但求和域限定于该 bank-year 内 LLM 三家投票裁定金科落点 (locus) = 应用场景('app', 对应 encode.py 硬编码 cat_mapping[('应用场景','_app')]) 或 底层技术('tech', cat_mapping[('底层技术','_tech')]) 的子样本 (locus 分类只在 P4/Gomber locus 维度门控通过的文章上有效, n<某最小样本时该 bank-year 取 NaN)。"
producer: pipeline/sentiment/tone_words.py (§4B build_idf_weighted_dictionaries / apply_idf_weighting, 逐篇 loughran_idf_score{full,ctx,ss} 及其规则消融/权重列) ; pipeline/panel/encode.py (第1540-1589行, `innovation_locus_full` 列 + 独立硬编码 `cat_mapping=[('底层技术','_tech'),('应用场景','_app')]` 完成 app/tech locus 切分聚合; 另含 F 段 hw/mw/vw 聚合分子分母、std Z-score) ; pipeline/panel/runner.py (步骤3d 逐篇 herd_weight 乘入 hw 变体; 该文件另有的 `fintech_map` 仅供 Bartik IV 工具变量构造使用, 与本家族 app/tech locus 切分是两套互不相干的代码路径)
upstream:
- 22_tone_words.parquet (逐篇 loughran_score_full/_ctx/_ss + loughran_idf_score_full/_ctx/_ss 及否定/程度/转折全规则消融列)
- 24_herd_decay.parquet (herd_weight_full/_ctx/_ss, 供 _hw 变体)
- 11_news_bank (news_salience mention_density, 供 _vw 变体)
- config/media_weights.json (媒体权威度权重表, 供 _mw 变体)
- 21_tone_llms.parquet (三家 LLM 投票 locus 落点 = 应用场景/底层技术, 供 _app/_tech 子样本切分)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss, IDF 语料统一在 content_full 上计算)
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
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.1002/isaf.1549"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
本家族衡量的构念是"银行—金科新闻报道的语调 (media tone), 以 Loughran & McDonald (2011, Journal of Finance)《When is a Liability Not a Liability?》建立的金融文本情感范式为方法学根基, 经中文主译本 loughran_mcdonald_zh_2026 (positive 1,295 词 / negative 3,729 词, 另含 5 类非极性词类) 本土化后, 叠加逆文档频率 (IDF) 加权稳健性检验"。loughran 是本项目 tone_words.py 六部中文金融/通用情感词典之一 (另五部为 jiang_2021/yao_2021/bian_2021/du_2022/you_2018, 见 config/tone_dicts.json), loughran_idf_tone 系列是六词典中唯一以 loughran 词表为底座、并叠加 IDF 稀有度加权的家族; 家族名中的 "idf" 显式标注其区别于家族 F127 一族 "bian_2021_*" (bian 词典无 idf 前缀变体) 的方法学分支——loughran 词典同时存在无 idf 前缀的等权版 (另一家族) 与本家族的 idf 加权版, 二者互为稳健性并排, 不构成同一 over-identified 设定的两条约束。语调构念服务于 P1 (`bank_fintech_tone`) 主线论文: 银行与金科相关新闻的语气正负, 是否会传导为银行的融资成本 (funding_cost) 及市场对银行—金科合作的定价反应; loughran_idf_tone_full 属于该论文 treatment 侧多方法互为稳健性梯子中"词典法×IDF 加权×loughran 词表"这一具体组合分支, 与三家 LLM 投票 (`llm_vote_tone_full`, P1 canonical) 及三 BERT 模型情感构成"词典/LLM/BERT 三法互为稳健性"三角 (Frankel, Jennings & Lee 2022, Management Science 对该三角设计有直接方法学先例)。

【方法学与计算】
逐篇打分分两步: 第一步是标准 Loughran-McDonald 词典查表, 对文章命中的 loughran 词典词汇按其极性 (positive/negative) 累加, 并叠加三条中文本土化语言学规则——否定翻转 (否定词紧邻情感词时翻转极性)、程度副词 (放大/缩小极性幅度)、转折连词 (转折从句后情感词权重调整), 这与 F127 (bian_2021) 等六词典家族共享同一套规则消融基础设施 (`_RULE_ABLATION_VARIANTS`); 第二步是本家族特有的 IDF 加权稳健性检验 (方法学根基可追溯至 Spärck Jones 1972, Journal of Documentation 提出的词项特异性统计解释): 在 content_full 语料上用 jieba 分词统一计算每个 loughran 词典情感词的文档频率 (DF), 转为平滑 IDF (smooth IDF, 避免零频除零), 再做均值归一化 (使 IDF 加权后的得分量级 ≈ 未加权等权版, 保证两者可共享同一判定阈值) 并 Winsorize 极端值。IDF 语料之所以统一在三轨共享的 content_full 上计算而非裸"内容"列, 是因为 fix(tone-words-idf-corpus) 发现三轨 (full/ctx/ss) 各自独立算 DF 会让标题词的文档频率被系统性低估 (标题只在 full 轨天然出现)——本项目选择让 IDF 权重字典在三轨间共享同一份基于 content_full 计算的词频统计, 只在应用到具体轨道文本时用该轨自身的词计数与规则分数相乘, 从而"IDF 稀有度"这把尺子对三轨保持同构、不因轨道切换而漂移。计算出的逐篇 loughran_idf_score{full,ctx,ss} 落在 22_tone_words.parquet, 随后在 panel runner/encode.py 里按六种聚合方式再加工为本家族 21 列: 等权均值 (canonical _full/_ctx/_ss)、Z-score 标准化均值 (_std)、羊群 (herd) 加权均值 (_hw, 出自 stage 24 herd_decay_processor 对高度相似报道的衰减加权)、媒体权威加权均值 (_mw, 出自 config/media_weights.json 按来源媒体排名分位赋权, 呼应 Holzman, Miller & Twedt 2023, The Accounting Review 关于媒体权威在情感传导中作用的发现)、提及密度加权均值 (_vw, 出自 stage 11 news_salience 的 mention_density, 篇幅/提及越密集权重越高)、以及按金科落点 (locus) 二分的子样本均值 (_app=应用场景子样本, _tech=底层技术子样本, 落点判定来自三家 LLM 投票, 呼应 P4 Gomber locus 维度构念)。

【文献定位】
本家族方法学谱系直接承袭 Loughran & McDonald (2011, The Journal of Finance) 建立的"词典法情感分析对金融文本语境敏感"这一奠基性发现——该文证明通用情感词典 (如 Harvard-IV) 在 10-K 文本中大量误判 (如"liability""tax"在金融文本中并非负面词), 从而催生了金融领域专用情感词典的研究传统; 本项目将其英文词表本土化翻译并中文语境重构为 loughran_mcdonald_zh_2026。IDF 加权分支的方法学依据是信息检索经典 Spärck Jones (1972, Journal of Documentation) 对"词项特异性" (term specificity) 的统计解释——稀有但高区分度的词项理应获得比高频常见词更大的权重, 情感词的稀有度与其区分力正相关这一原理是本家族 IDF 加权设计的直接理论来源, 这与 Du, Huang, Wermers & Wu (2022, Review of Finance) 强调"中文金融文本存在语言与领域特异性、通用情感度量会引入系统性偏误"的论点相互印证 (Du et al. 2022 是本项目六词典中 du_2022 词典的直接来源, 与 loughran 词典互为稳健性并排)。多方法三角验证的设计哲学参照 Frankel, Jennings & Lee (2022, Management Science) 对"机器学习法 vs 词典法"两类情感测度方法论差异及其经济后果的系统比较——本项目进一步将词典法内部拆分为词典—权重两个维度的梯子 (六词典 × IDF-有无 × 规则消融 × hw/mw/vw/std/app/tech 多种聚合权重), 使得任何单一测度选择都不会独立驱动主结论。IDF/TF-IDF 词袋加权这一文本分析的通用方法论基础可追溯至信息检索经典 Spärck Jones (1972, Journal of Documentation) 对"词项特异性"统计解释的原始提出, 本家族 IDF 权重的数学定义 (文档频率倒数的对数平滑) 与该文一脉相承。Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 近期对词典法经济文本情感分析的系统评述进一步确认了本家族所采用的"规则叠加 + 权重加权"词典法路径在当代文献中仍是词典法情感测度的主流范式, 与 LLM/BERT 等新兴方法互为稳健性、并非被取代关系。Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献(词典法/机器学习/深度学习三代方法),为本家族词典法+IDF加权路径在当代文献中的定位提供综述性支撑。Xu, Hua & Zhang (2025, Emerging Markets Review) 以中国官方权威媒体情感指数预测股市收益反转,证明媒体来源权威度对信息传导效力有系统性影响,支撑本家族媒体权威加权(_mw)变体的构念动机。

## VAR: loughran_idf_tone_full

【变体差分】
本列是 loughran_idf_tone 家族在 full 轨 (标题+全文正文) 上的 canonical 版本: 逐篇 loughran_idf_score_full 在 bank-year 内取等权算术均值, 不施加任何额外权重 (无 herd/media/value 加权, 无 Z-score 标准化, 不按金科落点切分子样本)。作为 P1 论文 treatment 侧词典法梯子的默认代表, 该列与家族内其余 20 个变体各自 just-identified 并排、互为稳健性、不分主次——full 轨与 ctx/ss 两轨也遵循同一铁律, 三轨禁止混入同一 over-identified Hansen J 设定。留篇门控口径 = full-only (2026-06-29 起): 一篇报道是否计入"银行—金科报道"的判定只看 stage 21 `llm_verified_full`, 本列作为 full 轨测度直接落在该门控口径的行宇宙上, 是家族内唯一不依赖 ctx/ss 条件-on-full 子集收缩的分支——ctx/ss 两轨的行宇宙都是本列行宇宙的子集。逐篇 loughran_idf_score_full 的 IDF 权重字典虽在三轨间共享同一份基于 content_full 语料计算的文档频率统计 (避免标题词文档频率因轨道切换被低估), 但应用到 full 轨文本时使用的是 full 轨自身的逐词命中与语言学规则叠加分数, 因此本列并非其余两轨的简单加权平均, 也不与 ctx/ss 构成可加分解关系。作为词典法—loughran 词表—IDF 加权—full 轨这一具体测度组合, 它是家族内被 P1 论文正文最常引用的分支, 但方法学地位上与其余 20 列平权, 不应被解读为"更优"或"主"测度。

## VAR: loughran_idf_tone_ctx

【变体差分】
本列是 ctx 轨 (标题+实体窗口文本) 版本, 逐篇打分只在银行/金科实体窗口内的文本上计算, 而非全文。ctx 轨是 conditional-on-full 的稳健性/测度轨: 其行宇宙是 full 轨留篇集合的子集 (留篇门控只认 full), 每篇文章各轨分别计分, 不存在 ctx 单独扩充行宇宙的情形。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J——三轨互为稳健性的判定不以相关系数高低为准, 即便 ctx 与 full 的相关性很高, 也不能因此把二者塞进同一右手边或同一 GMM 矩条件系统。本列不施加 herd/media/value 加权, 不做 Z-score 标准化, 不按金科落点切分子样本, 是 ctx 轨内的默认代表, 与本家族其余 6 个 ctx 后缀变体 (app_ctx/tech_ctx/hw_ctx/mw_ctx/std_ctx/vw_ctx) 共享同一套 content_ctx 文本口径, 差异只体现在聚合权重或子样本限定。content_ctx 由 stage 14 ctx_materializer 在 stage 21 情感打分之前物化 (prepend_title, 标题拼接进实体窗口文本), 使 15/16 等下游阶段在情感打分前即可消费真三轨文本。构念上, ctx 轨的存在理由是: 一篇报道即便整体篇幅很长, 也未必通篇都在谈论目标银行—金科业务这件事, 全文语调 (full 轨) 可能被文章中与银行—金科关系无关的段落稀释或污染; ctx 轨通过只截取实体附近窗口, 试图更贴近"报道对该银行金科议题本身的语气"这一狭义构念。但这也意味着 ctx 轨牺牲了上下文完整性 (窗口外的转折、总结性论断可能被切断), 因此本项目坚持 full 与 ctx 互为稳健性并排, 而非以 ctx 取代 full 作为默认口径——两者对"哪些文本片段才算数"给出不同但均合理的操作化定义, 结果若在两轨上方向一致则增强结论稳健性, 若不一致则需要在论文正文中报告并讨论差异来源, 而非择一隐藏。

## VAR: loughran_idf_tone_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句±N窗) 版本。ss 回退语义镜像 ctx: 当某篇文章不存在"银行实体与金科词同句共现" (窗口半径见 config/filtering.yaml::context_window.ss_sentence_radius, 默认1; 与 stage 13 硬过滤的 `cooccurrence_filter.sentence_radius` 是不同配置键, 二者判据口径不同不可混用) 时, content_ss 回退为全文 body, 对应的 ss_is_fallback=True 标记该行为降级样本 (回退样本仍计入 n_articles 分母, 与 ctx 共享同一"优雅降级"哲学; FINTECH_AC=None 的极端情形会让 ss_is_fallback 对全体行取 True)。本列不加权、不标准化、不切子样本, 是 ss 轨内的默认代表, 与 full/ctx 两轨互为稳健性并排, 各自 just-identified、禁止混入同一 Hansen J。ss 轨判定原语 (`extract_bank_fintech_cooccurrence`) 与 stage 13 硬过滤所用的邻近共现原语 (`has_bank_fintech_cooccurrence_within_radius`) 是两套不同判据, 前者要求严格同句、后者允许句子邻域, 二者刻意不互相复用, 因此 ss 轨的留篇子集与 stage 13 通过硬过滤的行集合在判据粒度上也不完全一致。构念上, ss 轨是三轨中操作化定义最严格的一支: 只有当银行实体名与金科词汇在同一句话内共现时, 才认为这句话 (及其窗口) 是"真正在谈论银行与金科的关系", 从而把语调测度收窄到最贴近因果叙事的文本片段; 但这种严格性也带来更高的回退率——多数报道即便涉及银行与金科, 也未必把两者写进同一句话, 因此本列在生产 T=18 语料上预计有相当比例的 bank-year 单元依赖回退口径 (等同 full 轨文本)。这一权衡是 ss 轨作为稳健性分支而非默认口径的核心原因: 它在窄口径子样本上提供最强的构念效度, 代价是样本量与统计效力的损失。

## VAR: loughran_idf_tone_app_ctx

【变体差分】
本列在 ctx 轨基础上, 额外将求和域限定于该 bank-year 内被三家 LLM 投票裁定"金科落点=应用场景" (源码 `pipeline/panel/encode.py` 硬编码 `cat_mapping = [('底层技术','_tech'), ('应用场景','_app')]` 中的 'app' 分支) 的子样本文章, 其余计算逻辑 (逐篇 IDF 加权词典打分、等权均值聚合) 与 loughran_idf_tone_ctx 完全一致。该 app/tech 二分呼应 P4 (Gomber locus 维度) 关于金科创新落点区分"应用场景创新"与"底层技术创新"的构念——落点为空 (locus 判定未过 LLM 门控) 的文章不计入任何一侧, 子样本文章数过少的 bank-year 单元取 NaN 而非用全样本均值顶替, 避免子样本稀疏导致的伪精度。落点判定本身建立在三家 LLM (gpt54nano/gemini31/deepseekv4) 的多数票共识之上, 与本家族的词典法测度是两条独立的方法学轨——词典法负责语调打分, LLM 分类负责落点归类, 二者在本列上耦合但不构成同一构念的重复度量, 因此不违反禁混同一 Hansen J 的铁律 (落点是切分维度而非另一组内生回归量)。ctx 轨自身的行宇宙又受 full-only 留篇门控约束, 因此本列的最终样本 = full 留篇集合 交 ctx 轨有效文本 交 落点=app 判定通过, 三重条件叠加后样本量通常明显小于家族内不切子样本的三个 canonical 变体, 使用时应留意小样本单元的方差膨胀问题。

## VAR: loughran_idf_tone_app_full

【变体差分】
本列是 full 轨 + 应用场景 (app) 落点子样本组合: 求和域限定于该 bank-year 内 `llm_verified_full` 留篇且金科落点判定为"应用场景"的文章, 在此子集上计算逐篇 IDF 加权 loughran 语调均值。作为落点切分梯子在 full 轨上的分支, 与 loughran_idf_tone_tech_full 互为稳健性并排 (二者行宇宙互斥, 加总覆盖该 bank-year 内所有落点已判定文章, 但本身不构成加权分解恒等式——两者各自独立取均值, 非可加分量; 落点缺失或未过分类门控的文章两侧均不计入, 故 app 与 tech 子样本之和一般小于该 bank-year 的留篇总数)。由于 full 轨本身就是留篇门控的行宇宙, 本列的样本收缩幅度仅取决于落点分类通过率, 不像 ctx/ss 变体那样叠加轨道自身的条件收缩, 是三轨落点子样本中样本量相对最大、噪声相对最小的一支, 常被用作落点梯子的默认参照对象。落点分类 (locus) 与语调打分 (tone) 是两个正交的操作化维度: 前者回答"这篇报道讲的是应用场景类金科还是底层技术类金科", 后者回答"这篇报道的语气正负如何"; 本列把二者交叉, 得到"应用场景类金科报道的语调均值", 用于检验银行在应用场景侧 (如手机银行、智能投顾) 与底层技术侧 (如系统对接、云计算基础设施) 获得的媒体评价是否存在系统性差异——这一差异本身可能是有意义的经济发现 (例如应用场景类创新更贴近消费者认知、易获正面评价, 而底层技术类创新因不可见性更强而语调更中性)。

## VAR: loughran_idf_tone_app_ss

【变体差分】
本列是 ss 轨 + 应用场景落点子样本组合。ss 轨本身的回退语义 (无银行∧金科同句共现时回退全文、`ss_is_fallback=True`) 在此处照常适用——落点子样本切分是在 ss 轨的逐篇分数之上再做一次子集限定, 不改变 ss 轨自身的文本口径, 也不改变回退样本判定 (回退样本若被判定落点=app, 仍计入本列, 其打分依据的是回退后的全文 body 而非严格同句窗口)。与 loughran_idf_tone_app_ctx / loughran_idf_tone_app_full 构成落点子样本梯子在三轨上的并排复刻, 三者互为稳健性、禁混同一 Hansen J。本列是家族 21 列中样本收缩幅度最深的几支之一 (full 留篇 交 ss 有效文本 交 落点=app), 解释系数时应结合该 bank-year 单元的有效样本数一并披露, 避免把小样本波动误读为经济含义上的语调差异。使用者若要在回归中同时纳入本列与其余落点子样本列 (如 tech_ss), 应意识到二者行宇宙互斥 (同一篇文章只能落一侧), 因此两列在同一 bank-year 内的均值差异反映的是"该银行—年内应用场景类与底层技术类报道语调孰高孰低", 而非同一批文章按权重拆分出的两个分量; 若某 bank-year 单元只有一侧存在有效样本 (另一侧全为 NaN), 差分运算会自动传播为 NaN, 这是设计使然而非缺陷。

## VAR: loughran_idf_tone_tech_ctx

【变体差分】
本列在 ctx 轨基础上, 将求和域限定于金科落点判定为"底层技术" (`cat_mapping[('底层技术','_tech')]`) 的子样本文章, 呼应银行金科合作中"技术基础设施投入" (如核心系统对接、API 平台建设) 这一构念侧面 (区别于 app 侧的"面向客户应用场景", 如手机银行、智能投顾类报道)。计算式与 loughran_idf_tone_ctx 一致, 仅求和域收窄; 与 loughran_idf_tone_app_ctx 互斥并排, 不构成加权分解关系, 两者是同一落点维度下两个各自独立估计的稳健性分支, 而非同一测度的正交分量。底层技术类报道在中文财经媒体语料中通常占比低于应用场景类报道 (技术基建报道天然比面向消费者的产品报道更少见), 因此本列在多数 bank-year 单元上的有效样本量小于 loughran_idf_tone_app_ctx, 使用时应交叉核对 avg_category_confidence 等分类置信度诊断列, 谨慎解读极端值。ctx 轨的实体窗口截取在底层技术类报道上尤须留意: 此类报道常涉及较长的技术描述段落 (系统架构、接口协议等), 若情感词恰好出现在窗口边界之外, ctx 轨打分可能与 full 轨产生更大分歧——这正是三轨互为稳健性设计要捕捉的现象之一, 而非需要修正的偏误; 若 ctx 与 full 在 tech 子样本上的相关性明显低于在 app 子样本上的相关性, 值得在稳健性附录中单独报告并讨论。

## VAR: loughran_idf_tone_tech_full

【变体差分】
本列是 full 轨 + 底层技术落点子样本组合, 求和域 = `llm_verified_full` 留篇且落点判定为"底层技术"的文章集合。作为落点梯子中 full 轨的一个分支, 与同轨 loughran_idf_tone_app_full 互为稳健性并排, 与另两轨 (_tech_ctx/_tech_ss) 同构复刻。该列与 codebook.py 中已落地的 `llm_vote_tone_tech_full - llm_vote_tone_app_full` (locus gap 指标) 属于姊妹结构——后者是 LLM 情感投票口径下的 tech-app 语调差, 本列是词典法 loughran-IDF 口径下的对应子样本均值, 两条测度路径 (LLM vs 词典) 互为跨方法稳健性, 不应被误读为同一指标的重复列; 若要构造词典法版本的 tech-app 语调差, 使用者须自行在下游做 `loughran_idf_tone_tech_full - loughran_idf_tone_app_full`, 本 codebook 家族不预先物化该差分列。词典法与 LLM 法在落点子样本切分上的经济学动机一致 (均检验应用场景 vs 底层技术两类报道语调是否存在系统性差异), 但两者对"语调"的操作化路径截然不同: 词典法依赖静态词表的极性累加加 IDF 稀有度加权, 而 LLM 法依赖模型对整篇文章语境的整体判读, 二者结果的一致或分歧本身就是一项有信息量的稳健性证据。本列的样本收缩幅度与 loughran_idf_tone_app_full 对称——两者共享同一 full 轨行宇宙 (`llm_verified_full` 留篇集合), 差异只在落点判定结果指向哪一侧, 因此二者的样本量之和上界等于该 bank-year 内所有通过落点分类门控的文章数 (未通过门控的部分既不进 app 也不进 tech)。

## VAR: loughran_idf_tone_tech_ss

【变体差分】
本列是 ss 轨 + 底层技术落点子样本组合, 在 ss 轨的银行∧金科同句/全文回退口径基础上再限定落点子集。与 loughran_idf_tone_app_ss 互斥并排, 完成落点梯子 (app/tech) × 三轨 (full/ctx/ss) 的完整 6 列矩阵。本列是家族内因"轨道收缩 (ss 条件-on-full) + 落点收缩 (tech 子集本身占比更低)"双重叠加而样本量最小的分支之一, 在生产 T=18 全量语料上仍需关注部分小银行—年单元因样本不足而系统性缺失 (取 NaN), 使用前建议核对该银行—年是否存在足够数量的底层技术类报道再纳入回归, 否则易把抽样噪声误判为系统性语调差异。本列完成 loughran_idf_tone 家族落点子样本梯子 (app/tech) 在三轨 (full/ctx/ss) 上的最后一格, 与 loughran_idf_tone_app_ss 构成该 bank-year 内 ss 轨落点二分的完整互斥对; 使用者若在同一张回归表中同时报告 app 与 tech 两侧系数, 应在表格脚注中明确说明二者行宇宙互斥、并非同一样本的加权分解, 避免读者误以为两个系数存在算术加总关系。本列同时叠加 ss 轨 (银行∧金科同句判据, 含全文回退) 与落点子样本切分 (底层技术) 两层条件, 因此其覆盖率对回退率与落点分类通过率均敏感, 是家族 21 列中经济学解释门槛相对较高的一支, 建议仅在稳健性附录而非正文主表中呈现。

## VAR: loughran_idf_tone_hw_ctx

【变体差分】
本列是 ctx 轨的羊群 (herd) 加权版本: 聚合分子分母均乘以 herd_weight_ctx (出自 stage 24 herd_decay_processor, 定义为 1/(1+n_similar_articles_ctx), 与该 bank-year 内高度相似/转载报道的数量成反比衰减), 用以降低"同一事件被多家媒体近乎复制转载"对语调均值的重复计权偏误。与 loughran_idf_tone_ctx (无权重版) 互为稳健性并排, 不应视为后者的更优替代——羊群加权本身也引入了"相似度判定阈值"这一额外自由度, 是稳健性梯子的一支而非默认口径。herd_weight_ctx 的相似度比较对象是 ctx 轨自身的实体窗口文本 (而非 full 轨全文), 因此 _hw_ctx 与 _hw_full 的羊群权重不同源、不可交叉复用 (三轨 herd_weight 各自独立计算)。聚合层面, 本列与家族内另有 `bian_2021_score_hw_sum` 等家族共享同一套"逐篇分乘以 herd_weight 再在 bank-year 内求和/求均值"聚合基础设施 (panel runner 步骤 3d), 差异仅在情感打分方法 (loughran-IDF vs bian 词典) 与聚合形态 (本列输出均值语调, 而非未归一化的 sum 分子)。羊群加权与本家族的落点子样本切分 (app/tech) 是两条正交的梯子——前者调整"每篇文章计入均值时的权重", 后者调整"哪些文章进入求和域", 二者理论上可交叉组合但本项目刻意不物化交叉列 (如 hw_app_ctx), 以控制家族列数与梯子复杂度, 使用者若确需该组合须自行在下游用逐篇中间列重新聚合。

## VAR: loughran_idf_tone_hw_full

【变体差分】
本列是 full 轨羊群加权版本, herd_weight_full 出自同一 stage 24 产物、在 full 轨全文文本口径下重新计算相似度。作为 hw 权重梯子在三轨上的 full 分支, 与 _hw_ctx / _hw_ss 并排、与该轨无权重版 loughran_idf_tone_full 互为稳健性。羊群衰减的经济含义是: 若某年份大量媒体几乎逐字转载同一篇关于某银行金科合作的通稿, 未加权的等权均值会让这条通稿的情感倾向被重复计权、放大其对 bank-year 语调均值的影响; herd_weight 通过 1/(1+n_similar_articles) 的衰减函数压低相似报道群组的合计权重, 使得聚合语调更接近"独立信息事件数"而非"报道条数"的加权。该衰减处理在 full 轨上覆盖的文本范围最广 (全文相似度比较), 因此对转载/通稿密集型样本的衰减效果通常最明显, 是三轨 hw 变体中样本收缩最不敏感、但相似度判定最保守的一支。羊群加权服务于中文财经新闻语料的一个已知特征: 同一条银行公告或金科合作通稿常被数十家地方媒体或行业垂类媒体近乎逐字转载, 若不加权处理, 这类"高转载度但信息含量单一"的事件会在 bank-year 均值中获得与"独立报道多篇不同角度"的事件同等甚至更高的权重, 系统性扭曲语调测度对信息多样性的刻画; herd_weight 的衰减函数正是为纠正这一权重失衡而设计, 与 vw (提及密度) 加权在动机上互补而非替代——vw 关注单篇文章内的关注深度, hw 关注跨篇章之间的重复度。

## VAR: loughran_idf_tone_hw_ss

【变体差分】
本列是 ss 轨羊群加权版本, herd_weight_ss 建立在 ss 轨 (银行∧金科同句窗口, 含回退) 文本相似度之上。ss 轨若发生回退 (`ss_is_fallback=True`), 其 herd_weight_ss 的相似度比较对象同样是回退后的全文 body, 与 ctx 轨镜像语义一致 (回退样本不因回退而豁免羊群衰减计算, 只是相似度比较基于全文而非严格同句片段)。若某 bank-year 内 ss 轨样本大量发生回退 (即银行∧金科同句共现稀少), 本列的 herd_weight_ss 实质上退化为与 loughran_idf_tone_hw_full 高度相关的度量 (因为二者此时都基于全文相似度比较), 但两列仍各自 just-identified 并排、不构成同一构念的重复列, 高相关不等于可替代——ss 轨的行宇宙筛选逻辑 (银行∧金科同句判据) 始终独立于 full 轨。本列是家族内叠加维度最多的分支之一, 同时承载"ss 轨文本口径 (含回退)"与"羊群衰减聚合权重"两层设计: 前者决定哪些文本片段参与词典打分, 后者决定不同文章在跨篇聚合时的相对权重, 二者作用于流水线的不同环节 (文本物化 vs 面板聚合), 互不干扰但共同决定最终数值, 使用者在追溯某个异常值的成因时应分别检查这两个环节而非笼统归因于"ss 轨"或"羊群加权"其中之一。

## VAR: loughran_idf_tone_mw_ctx

【变体差分】
本列是 ctx 轨的媒体权威加权版本: 聚合权重取自 config/media_weights.json 中该篇文章来源媒体的权威度排名分位 (未登记来源退回默认权重 `media_weights.json::default`), 呼应 Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体权威影响信息传导效力的发现——权威媒体的负面报道对市场纪律的约束效应通常更强。与 loughran_idf_tone_ctx 互为稳健性并排。当媒体权威表未登记某来源 (多数落默认权重) 时, MW 语调会向等权版收敛, 因此 mw 变体在权威覆盖度低的语料子集上与 canonical 变体高度相关是预期结果、非测度失效; 覆盖度诊断以生产运行日志中的"多数落默认权重, MW Tone 接近等权"提示为准。媒体权威加权与本家族的提及密度加权 (vw)、羊群衰减加权 (hw) 是三条正交的聚合权重轨——分别刻画"信源权威度""报道深度""重复报道稀释", 互不嵌套, 也不构成同一构念在不同粒度上的分解。媒体权威加权的方法学动机源自新闻传播学与金融文本文献的共识: 不同媒体来源对市场参与者的说服力/可信度并不均等, 全国性权威财经媒体的负面报道通常比地方小报或自媒体转载更能引发实际的市场纪律效应, 因此在聚合银行—年语调时按来源权威度加权比简单等权更贴近"市场实际接收到的加权信息" 这一构念。media_weights.json 的权威度排名分位是外生给定的静态配置, 不随本项目样本或时间窗变化, 因此本列的加权结构在跨年份比较时具有稳定的可比性。

## VAR: loughran_idf_tone_std_ss

【变体差分】
本列是 ss 轨 Z-score 标准化版本, 标准化基准建立在 ss 轨 (含同句回退) 的逐篇分数分布上。完成 std 权重梯子在三轨的复刻, 与 _std_ctx / _std_full 互为稳健性并排。因 ss 轨样本量通常小于 full 轨 (受同句共现判据收窄) 、且回退样本与非回退样本的文本长度/词典命中密度分布可能不同, 该轨内标准化的均值/方差估计在小样本 bank-year 单元上更容易受极端值影响, 使用时建议核对该轨全样本标准化的分母 (跨 bank-year 样本量) 是否充足, 避免把标准化噪声误读为经济含义上的语调波动。Z-score 标准化对逐篇分数的处理发生在跨 bank-year 的全样本层面 (而非 bank-year 内部), 因此本列衡量的是"该 bank-year 内文章的平均语调, 相对于全样本 ss 轨语调分布所处的相对位置", 与未标准化版本 (原始极性词计数比) 相比, 标准化版本更适合用于跨方法系数量级比较 (如与三 BERT 模型的 net_tone 系数对照), 而未标准化版本更适合直接经济学解读 (如"语调每提高 0.1 个单位")。本列的标准化基准建立在 ss 轨全体样本 (含回退与非回退两类) 混合分布之上, 不区分回退状态单独标准化——这意味着若回退样本与非回退样本的分数分布存在系统性差异 (例如回退样本因文本更长而词典命中更密集), 该差异会被吸收进全局标准化参数中, 而非在本列内被识别或分离; 若研究者需要区分回退状态的影响, 应转而使用 `ss_is_fallback` 指示列做交互项分析, 而非依赖本列自身的数值差异。

## VAR: loughran_idf_tone_mw_full

【变体差分】
本列是 full 轨媒体权威加权版本, 权重定义 (媒体权威分位, 出自 config/media_weights.json) 与 ctx 轨的 mw 版本共享同一权重表——媒体权威度是文章级来源属性、不随文本轨道切换而改变, 因此三轨 mw 变体的权重来源相同, 差异只体现在被加权的逐篇语调分数取自哪条文本轨道 (full 轨=标题+全文正文逐篇打分)。是 mw 权重梯子在三轨上的 full 分支, 与 _mw_ctx / _mw_ss 并排, 与该轨无权重版 loughran_idf_tone_full 互为稳健性。作为 full 轨 (留篇门控本身的行宇宙) 上的媒体权威加权版本, 本列覆盖的文章数量与 loughran_idf_tone_full 完全一致, 只是聚合权重从等权改为权威分位加权, 是三轨 mw 变体中受轨道条件收缩影响最小的一支。经济学上, 本列检验的是"若市场参与者按媒体权威度对信息加权吸收, 银行—金科语调是否与简单等权版本得出不同结论"这一稳健性问题——若两者高度一致, 说明结果不依赖于对媒体权威结构的特定假设; 若出现系统性分歧 (例如权威媒体对某类银行—金科合作报道更负面), 则本身构成一项值得在论文中单独讨论的发现, 而非需要调和的矛盾。

## VAR: loughran_idf_tone_mw_ss

【变体差分】
本列是 ss 轨媒体权威加权版本, 在 ss 轨 (含同句回退语义) 逐篇打分之上叠加媒体权威加权。完成 mw 权重梯子在三轨的复刻, 与 _mw_ctx / _mw_full 互为稳健性并排。媒体权威权重来自文章的来源出处属性, 与该篇文章是否发生 ss 轨回退 (`ss_is_fallback=True`) 无关——即便某篇文章因缺少银行∧金科同句共现而在 ss 轨回退为全文口径, 其媒体权威权重仍按原来源正常取值, 两条信息 (回退状态与来源权威度) 相互独立、不发生耦合。本列与 loughran_idf_tone_hw_ss 都是 ss 轨上的加权变体, 但权重来源不同 (媒体权威 vs 羊群衰减), 二者互为稳健性并排, 不应合并进同一加权公式。作为 mw 权重梯子在 ss 轨上的分支, 本列同时承接 ss 轨严格的银行∧金科同句判据 (及其回退退化语义) 与媒体权威加权两层设计, 是家族内因"轨道收缩+权重再分配"叠加而经济学解释相对复杂的一列——建议在稳健性附录中与 loughran_idf_tone_ss (ss 轨无权重版) 并列报告, 让读者直接对照权重调整前后系数的方向与显著性变化。由于 ss 轨样本量本就受同句判据约束而收窄, 叠加媒体权威加权后, 少数权威度极高或极低的媒体来源在小样本 bank-year 单元上可能对聚合语调产生不成比例的影响, 使用者应结合该单元的有效样本数与权威度分布 (是否集中于少数几家来源) 综合判断本列数值的可靠性, 避免直接采信极端权重下的孤例结果。

## VAR: loughran_idf_tone_std_ctx

【变体差分】
本列是 ctx 轨的 Z-score 标准化版本: 逐篇 loughran_idf_score_ctx 先在全样本 (跨 bank-year) 标准化为均值 0、标准差 1 的分布, 再在 bank-year 内取均值, 用以消除逐篇分数尺度受词典命中密度影响的量纲问题, 便于与其他标准化后的测度 (如三 BERT 模型经 Phase 2 后处理得到的 signed net_tone) 做跨方法系数比较——不同情感测度方法的原始分数量纲往往不同 (词典法是极性词计数比, BERT 是 softmax 概率差), Table A5 一类跨模型系数比较表须先做 Z-score 标准化再比较回归系数, 本列即为词典法一侧提前物化好的标准化版本。与未标准化的 loughran_idf_tone_ctx 互为稳健性并排, 二者相关但非同一构念的可加分解: 标准化改变的是分数的相对量纲、不改变其经济排序, 因此标准化前后两列的显著性检验结论理论上应高度一致, 若出现系统性偏差反而值得追查 (如极端值 Winsorize 参数在标准化前后处理不一致)。作为 std 权重梯子在 ctx 轨上的分支, 本列的标准化参数 (全样本均值/标准差) 只在 ctx 轨内部估计, 与 full/ss 两轨各自独立, 这一设计使得三轨标准化版本之间的相关系数仍可直接反映"轨道选择对语调排序的影响", 而不掺杂"标准化基准不同"这一混淆因素。

## VAR: loughran_idf_tone_std_full

【变体差分】
本列是 full 轨 Z-score 标准化版本, 标准化基准 (全样本均值/标准差) 在 full 轨自身的逐篇分数分布上估计, 不与 ctx/ss 轨共享标准化参数 (三轨各自独立标准化, 保持 just-identified 并排原则; 若跨轨共享标准化参数, 会让某一轨的样本分布特征渗透进另一轨的标准化尺度, 破坏三轨互为稳健性的独立估计前提)。作为 full 轨 (留篇门控行宇宙) 上的标准化版本, 本列覆盖文章数与 loughran_idf_tone_full 一致, 标准化参数估计所依赖的样本量在三轨中通常最大、标准化误差最小, 是词典法—loughran—IDF 加权—标准化这一组合在生产环境中最常被拿来做跨模型系数比较的分支。标准化处理不改变 IDF 加权本身的语义——本列的底层分数仍是经稀有度加权、语言学规则叠加后的 loughran 语调分, 只是把该分数放到全样本分布中定位其相对位置; 因此本列同时携带"词典选择 (loughran)""加权方式 (IDF)""聚合尺度 (标准化)"三层测度选择, 是家族内测度选择维度最丰富的列之一, 解读时应明确各层选择对结果的贡献不可分离拆分, 只能整体作为一个具体测度组合看待。

## VAR: loughran_idf_tone_vw_ctx

【变体差分】
本列是 ctx 轨的提及密度加权 (value-weighted) 版本: 聚合权重取自 stage 11 news_salience 产出的 mention_density_ctx (该篇文章内目标银行被提及的密度/显著性度量), 提及越密集的文章在 bank-year 均值中权重越大, 呼应"报道对银行的关注深度而非仅出现与否"这一构念侧面。与 loughran_idf_tone_ctx 互为稳健性并排。mention_density 的定义域限定在 ctx 轨的实体窗口文本上估计, 而非全文, 因此本列刻画的是"在银行实体附近的局部提及密度", 与 full 轨 vw 版本刻画的"全文范围提及密度"是两个不同粒度的量, 二者互为稳健性、不构成同一测度在不同轨道上的简单重复。提及密度加权与媒体权威加权 (mw)、羊群衰减加权 (hw) 三者是并列而非嵌套的聚合权重轨——三者可以各自独立地对同一篇文章赋予不同权重值, 但本家族刻意不物化任何两两组合 (如同时施加 vw × mw) 的列, 避免梯子数量指数级膨胀。mention_density_ctx 的分子分母定义与 vw 变体在其余家族 (如 bian_2021 系列的 `_tone_vw`) 共享同一套聚合基础设施 (panel encode.py F 段), 因此本列与其他词典的 vw 变体在权重来源上是同构的, 差异只体现在被加权的底层情感打分方法 (loughran-IDF vs 其他词典/LLM/BERT), 使得跨方法比较提及密度加权效应时可以直接对照系数, 无需担心权重定义口径不一致。

## VAR: loughran_idf_tone_vw_full

【变体差分】
本列是 full 轨提及密度加权版本, mention_density_full 在 full 轨 (标题+全文) 文本上计算, 覆盖全文范围内目标银行被提及的密度。是 vw 权重梯子在三轨上的 full 分支, 与 _vw_ctx / _vw_ss 并排, 与该轨无权重版 loughran_idf_tone_full 互为稳健性。作为 full 轨 (留篇门控行宇宙) 上的提及密度加权版本, 本列覆盖文章数与 loughran_idf_tone_full 一致, 加权效应主要体现在报道深度差异较大的样本上——若某 bank-year 内既有仅一笔带过银行名的边角报道、又有整篇聚焦该银行金科业务的深度报道, vw 加权会让后者在语调均值中占更大权重, 更贴近"媒体真正在谈论这家银行"而非"这家银行的名字出现过"的构念。mention_density 的计算源自 stage 11 news_bank 模块的 news_salience 逻辑, 与另一个未加权诊断信号 headline_frac (标题内提及占比) 是不同的量——前者衡量正文层面的提及密度, 后者衡量标题层面的显著性, 两者服务于不同的稳健性问题, 不应混用或相互替代。本列作为 vw 权重梯子在 full 轨上的分支, 是三轨 vw 变体中行宇宙覆盖最广、加权基准估计最稳定的一支, 覆盖文章数与 loughran_idf_tone_full 完全一致。经济学解读上, 本列回答的问题是"若把每篇报道对该银行的关注深度纳入考量, 银行—金科语调的加权均值是否与简单等权版本 (loughran_idf_tone_full) 出现方向性分歧"——若结果一致, 说明主结论不依赖于是否区分'蜻蜓点水式提及'与'深度聚焦报道', 增强了 full 轨 canonical 版本的稳健性基础。

## VAR: loughran_idf_tone_vw_ss

【变体差分】
本列是 ss 轨提及密度加权版本, mention_density_ss 建立在 ss 轨 (银行∧金科同句窗口, 含回退) 文本之上。完成 vw 权重梯子在三轨的复刻, 与家族内 hw/mw/std/app/tech 等权重梯子共同构成 loughran_idf_tone 家族的完整稳健性矩阵——所有梯子之间正交、不交叉, 任何两个梯子的组合列 (如同时施加 hw 与 app 切分) 不在本家族物化范围内。ss 轨若发生回退 (`ss_is_fallback=True`), mention_density_ss 的计算基础是回退后的全文 body, 而非严格同句窗口, 与 ss 轨其余变体的回退语义保持一致——回退不改变提及密度的计算口径, 只改变文本的来源范围。本列作为家族 21 列的最后一列, 完成 loughran_idf_tone 家族"三轨 (full/ctx/ss) × 七种聚合方式 (canonical/std/hw/mw/vw/app/tech)"矩阵的收尾, 家族内任意两列之间不构成加权分解、不构成同一构念的重复度量, 均应各自 just-identified 纳入回归、禁止混入同一 over-identified Hansen J 设定。作为 vw 权重梯子在 ss 轨上的分支, 本列与 loughran_idf_tone_vw_ctx / loughran_idf_tone_vw_full 三者共同验证"提及密度加权是否改变结论"这一稳健性问题在三种不同文本口径 (全文/实体窗口/同句窗口) 下是否保持一致——若三者在方向与显著性上高度一致, 是对 P1 论文核心结论最强的一类跨轨稳健性证据之一。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
