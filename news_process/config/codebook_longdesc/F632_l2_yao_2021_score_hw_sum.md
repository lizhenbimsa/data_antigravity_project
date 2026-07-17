---
family_id: F632
columns:
- yao_2021_score_hw_sum_ctx
- yao_2021_score_hw_sum_full
- yao_2021_score_hw_sum_ss
unit: 无量纲加权语调分之银行-年求和 (跟风衰减加权分子, 非归一化比率)
formula: 'panel[f"yao_2021_score_hw_sum{track}"] = groupby(bank, year)[f"yao_2021_score_hw{track}"].sum(); 其中 yao_2021_score_hw{track} = yao_2021_score{track} * herd_weight{track} (herd_weight 取值 stage 24 三轨独立衰减权重, 缺列时回退 herd_weight_full 或 legacy 单轨 herd_weight, 均先 fillna(1.0))'
producer: pipeline\panel\runner.py (步骤3d 预计算 yao_2021_score_hw{track} 逐篇加权列) ; pipeline\panel\encode.py (L1068 groupby-sum 聚合为 panel 列, L2301-L2304 供下游加权均值消费)
upstream:
- 22_tone_words (yao_2021_score{track} 篇章级词典打分)
- 24_herd_decay_processor (herd_weight_{full,ctx,ss} 跟风衰减权重)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: 'Sentiment analysis of economic text: A lexicon-based approach'
  venue: Economic Inquiry
  vol: '63'
  issue: '1'
  pages_or_artno: 125-143
- doi: "10.1016/j.econlet.2026.113002"
  type: "journal"
  authors: "Nakatsuka, H., & Suimon, Y."
  year: 2026
  title: "How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures"
  venue: "Economics Letters"
  vol: "265"
  pages_or_artno: "113002"
new_dois: []
---

## CORE

【构念与来源】
yao_2021_score_hw_sum 家族刻画的是姚加权等 (2021) 金融领域中文情绪词典打分在银行-年层面的"跟风衰减加权求和" — 它不是一个独立设计的新构念, 而是 stage 22 词典打分 (yao_2021_score) 与 stage 24 跟风衰减权重 (herd_weight) 相乘后在 panel 聚合阶段做 groupby(bank, year).sum() 得到的中间分子列, 与本仓库内其余 5 部情感词典 (jiang_2021/bian_2021/du_2022/you_2018/loughran) 的同构 `*_score_hw_sum` 家族、以及 LLM 投票测度族的 `llm_vote_score_hw_sum`/`llm_vote_cont_hw_sum` 遵循同一构造范式 (统一 SSOT 见 `pipeline/panel/encode.py` 的加权聚合逻辑块)。设计动机源于两条独立文献线索的交汇: 一是媒体语调测度的"跟风"(herding)/羊群关注衰减问题 — 同一事件短时间内被多家媒体反复转述报道, 若不做衰减处理会人为放大该事件方向的语调信号, 这是 Tetlock (2011, RFS) 提出的经典问题, 本仓库的处理落地在 stage 24 herd_decay_processor 产出的三轨 (full/ctx/ss) 独立衰减权重; 二是中文金融文本情绪词典本身的构造与校验文献, yao_2021 (姚加权、张锟澎、王攀娜、杨昆 (2021)) 是针对中国金融市场语境专门构建的中文情绪词典, 与 Du et al. (2022, Review of Finance) 提出的"语言与领域特异性 (language and domain specificity)"论点同源 — 后者论证了通用英文情感词典 (如 Loughran-McDonald) 直接翻译移植到中文语境会显著损失效度, 必须构造领域特异的中文金融词典, yao_2021 与本仓库同期纳入的 bian_2021 (Bian, Jia, Li & Yan, 2021, SSRN) 均是这一论证脉络下的具体实现。
本列族在数值上的直接含义是: 对给定银行-年单元内的全部相关报道 (full/ctx/ss 三轨各自的相关篇集合), 逐篇计算 yao_2021 词典打分 (yao_2021_score, 语言学规则全量版, 非消融变体) 后乘以该篇文章在其所属跟风衰减权重轨道下的衰减权重 (值域一般在 (0, 1] 附近, 同期同事件密集报道的文章权重被压低, 孤立报道权重接近 1), 再对银行-年单元内所有加权后的篇章分求和。该列本身不是一个归一化的语调均值或比率, 而是加权求和后的分子量 — 数值大小同时受"该银行-年被报道篇数"和"每篇的词典打分与其衰减权重"共同驱动, 篇数越多、正负向情绪越强、衰减权重越接近未衰减 (即报道越分散不扎堆), 该列绝对值越大。

【方法学与计算】
构造在流水线中横跨三个阶段: 第一步 stage 22 (tone_words) 对每篇文章的 content_{full,ctx,ss} 三轨文本各自独立跑 yao_2021 词典打分算法 (含否定翻转/程度副词/转折三条语言学规则的全量组合, 即 canonical `_score` 而非任一消融子集变体), 产出篇章级 `yao_2021_score{track}`; 第二步 stage 24 (herd_decay_processor) 基于同一事件/主题的报道时间聚集度独立计算三轨衰减权重 `herd_weight_{full,ctx,ss}` (ss 轨镜像 ctx 轨产出, 缺列时按运行时惯例回退 hw_full); 第三步在 runner.py 步骤3d 中逐篇相乘得到 `yao_2021_score_hw{track}` (命名遵循 MW 族的既有约定, `_hw` 后缀插在轨道后缀之前), 再在 encode.py 里对每个 (bank, year) 分组做 `.sum()` 聚合, 得到本家族三列 `yao_2021_score_hw_sum_{full,ctx,ss}`。下游用途上, 该求和列并非终点, 而是构造"跟风衰减加权平均语调"这一更高阶测度的分子部件 — 分母是对应轨道的 herd_weight 之和 (即 `hw_sum` 型分母列, 与本列同构但缺少词典分数因子), 分子除以分母即得加权均值口径的 yao_2021 跟风衰减调整语调, 该除法运算落在 encode.py 的下游消费代码块 (与 llm_vote 族的 `w_col`/`w_idf` 逻辑同构)。
本列族与三轨架构的一般铁律一致: full (标题+正文全文) / ctx (标题+实体窗) / ss (标题+银行∧金科同句±N窗, 无共现时镜像 ctx 语义回退全文 body 并置 `ss_is_fallback=True`) 三条轨道各自独立完整走完打分→加权→求和全链路, 互为稳健性、不分主次并排比较, 严禁将三轨数值混入同一个 over-identified 的 Hansen J 检验框架 (三轨应各自 just-identified 使用)。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇报道是否被计入某银行-年的"银行金科报道"行列, 由 `llm_verified_full` 单一门控决定, ctx/ss 两轨的加权求和是在 full 留篇集合的行宇宙子集上按各自轨道分别计算的 conditional-on-full 稳健性测度, 而非独立的留篇标准。跟风衰减权重本身的设计依据 Tetlock (2011, RFS) 关于媒体重复报道会稀释单篇信息含量的经典发现, 本仓库据此设计权重随同期报道密度递减; 权重构造的合理性还通过 decay_sensitivity 验证阶段做 uniform 权重与 inverse-distance 权重两种衰减核之间的 Pearson 相关检验 (高相关意味着衰减核选择对结果不敏感), 这一"权重设定须显式披露稳健性"的方法论关切与 Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 对词典法情感测度构造选择 (包括词表范围、极性规则、加总方式) 敏感性的系统讨论精神一致, 后者同样强调词典法测度不应把某一构造选择当作唯一正确设定, 而应显式检验替代设定间的一致性。

【文献定位】
在中文金融文本情感测度文献谱系中, yao_2021 与本仓库并置使用的 du_2022 (Du, Huang, Wermers & Wu, 2022, Review of Finance)、bian_2021 (Bian, Jia, Li & Yan, 2021, SSRN 工作论文) 属于同一代际的中文领域特异词典构建尝试, 三者均针对通用英文词典 (Loughran-McDonald 体系) 直译到中文语境后失效的问题给出各自的解决方案, 在措辞覆盖率、极性判定规则、以及与市场反应的相关性验证上各有侧重, 本仓库将六部词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran) 并排作为互为稳健性的语调测度来源, 不设单一"canonical"词典, 这与 Frankel, Jennings & Lee (2022, Management Science) 提出的"机器学习方法与词典方法应互为稳健性对照"的方法论建议在精神上一致——本仓库进一步在词典内部也做多引擎 (跟风衰减加权/媒体权威加权/普通均值等) 并排, 而非把某一权重方案当作唯一正确设定。跟风衰减这一处理步骤本身呼应了媒体经济学中对"重复报道稀释边际信息含量"的经典关切 (Tetlock, 2011 一脉), 是文本情感测度从"简单加总"迈向"结构化加权"的必要一步, 也是本仓库在 HW/MW/VW 三套加权体系中专门为"媒体扎堆报道"这一数据特征设计的对症下药。使用者在解读本列时应牢记它是分子部件而非最终语调指标, 直接对比不同银行-年之间该列的绝对值大小意义有限 (因为篇数规模效应未被归一化), 更合适的用法是配合对应的 hw 权重求和分母构造加权均值语调、或在控制篇数固定效应后作为语调强度的辅助诊断变量。 就跟风衰减这一「情感 × 新颖性」乘性结构的近期文献支撑, Nakatsuka 与 Suimon (2026) 在 Economics Letters 上对日本公司披露文本联合分析文本相似度 (新颖性) 与情感, 检验市场对文本新颖性的反应, 其核心发现是相似度与情感须联合而非各自单独看待, 这恰好锚定了本列把逐篇 yao_2021 极性分乘以跟风衰减权重后再于银行-年内求和这一构造中「情感强度须由新颖性调制」的环节。迁移边界须诚实标明: 原文语料为日文公司披露文件而非第三方媒体报道, 其相似度是披露文本之间的连续相似度并与情感做交互式联合分析, 并非本项目 1/(1+n_similar_articles) 这一具体倒数衰减函数形式, 亦未把二者相乘折叠成单一加权分再作实体-期聚合, 其分析层级是披露事件而非银行-年三轨, 故该文只支撑「二者须联合」这一一般性判断, 不构成对本列具体衰减函数设定的效度背书。
## VAR: yao_2021_score_hw_sum_full

【变体差分】
本列取轨道后缀 `_full`, 分子逐篇文本口径为标题+正文全文 (content_full, prepend_title 拼接), 权重口径为该轨道自身的跟风衰减权重 herd_weight_full (若仅存在 v3.5.0 及更早的 legacy 单轨 herd_weight 列, 则退化为全部三轨共用同一权重, 并在日志中记 WARN 提示重跑 stage 24 以升级到三轨独立权重)。该轨在留篇门控体系中处于核心地位: 2026-06-29 起生效的 full-only 铁律规定, 一篇报道是否计入银行-年"相关报道"行列 (即是否进入 `llm_verified_full == True` 的留篇集合) 完全由 full 轨判定, 因此本列所对应的分组求和行宇宙即为该留篇门控的定义域本身, 而非 ctx/ss 两轨那样的子集条件测度。数值上, 由于 full 轨文本量最大 (含正文全部段落), 相比 ctx/ss 两轨往往覆盖更广的措辞与语境, 该列的逐篇 yao_2021_score 输入方差与均值水平通常与 ctx/ss 轨不同, 三者应作为互为稳健性、不分主次的并排测度对待, 不应把 full 轨简单视为"更完整因而更优"的版本, 而应视为三条各自 just-identified 的独立识别路径之一, 禁止将三轨混入同一个 over-identified Hansen J 检验框架中联合识别。实务上, 研究者若只能报告一条主轨道的跟风衰减加权语调结果, full 轨是最贴近"原始报道口径"的默认选择, 因为它未对文本做任何实体窗或同句截断, 最大程度保留了记者行文的完整语境, 但这也意味着该轨最容易受无关段落措辞的干扰, 需要与 ctx/ss 两条更聚焦的轨道对照解读, 三者数值出现方向一致但幅度不同是预期现象, 方向不一致则应作为潜在测度稳健性问题在稳健性附录中披露而非简单取舍其一。

## VAR: yao_2021_score_hw_sum_ctx

【变体差分】
本列取轨道后缀 `_ctx`, 分子逐篇文本口径为标题+实体窗 (content_ctx, 目标银行实体周边窗口截取的正文片段, 由 stage 14 materialize_ctx 物化), 权重口径为该轨道自身的跟风衰减权重 herd_weight_ctx。ctx 轨的行宇宙是 full-only 留篇门控之后的一个条件子集 (conditional-on-full): 只有先被 full 轨判定为相关的报道, 才会在 ctx 轨上重新计算实体窗文本的 yao_2021 词典打分与加权求和, 因此本列相比 full 轨列, 分子的逐篇文本输入更聚焦于银行实体周边的直接语境描述而非全文通篇内容, 在报道正文包含大量与目标银行无关的背景段落 (如行业综述、宏观政策转述) 时, ctx 轨的打分更能反映针对该银行本身的语调倾向, 而 full 轨可能被无关段落的措辞稀释或污染。作为稳健性并排轨道, 本列与 full/ss 两列互为稳健性对照, 不分主次、各自 just-identified, 严禁混入同一 over-identified Hansen J。使用者应留意 ctx 轨的实体窗截取半径由文本上游 stage 14 物化时的窗口参数决定, 该参数并非本家族的自由调节项, 而是全仓统一配置; 当研究设计需要比较"通篇语调"与"针对性语调"的差异时, full 与 ctx 两列的对照本身即构成一种天然的稳健性检验, 差异越小说明该银行相关报道整体聚焦度越高, 差异越大则提示正文中存在较多与该银行无直接关联的背景性叙述稀释了整体测度。

## VAR: yao_2021_score_hw_sum_ss

【变体差分】
本列取轨道后缀 `_ss`, 分子逐篇文本口径为标题+银行∧金科同句 (content_ss, 要求目标银行实体与金科相关词在同一句子内共现, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认±1句), 权重口径为该轨道自身的跟风衰减权重 herd_weight_ss (由 stage 24 镜像 ctx 轨产出; 若该列在盘上缺失, 运行时按既有惯例回退 hw_full, 与 legacy 单轨退化同一处理口径)。ss 轨在文本层面的回退语义镜像 ctx: 当某篇报道中银行与金科词未出现同句共现时, `content_ss` 退化为全文 body 且置 `ss_is_fallback=True` (与 ctx/ss 共享 n_articles 分母口径), 因此 ss 轨是本仓库中判定标准最严格的一条轨道, 只有真正做到银行与金科概念紧邻共同出现的句子才被纳入窗口文本, 其余情形回退为与 full 轨等价的宽口径。该轨的行宇宙同样是 full-only 留篇门控之下的条件子集, 与 ctx 轨一样属于 conditional-on-full 的稳健性测度而非独立留篇标准。由于共现要求更严格, ss 轨逐篇纳入词典打分的文本片段通常比 ctx 轨更短、更聚焦, 该列与 full/ctx 两列互为稳健性并排、不分主次、各自 just-identified, 严禁混入同一 over-identified Hansen J 检验框架联合识别。由于共现门槛最严, 该轨对样本量最敏感, 在报道稀疏的银行-年单元 (尤其早期年份或规模较小银行) 上 ss 轨回退触发率可能显著高于 ctx 轨, 此时 `ss_is_fallback` 比例本身即是一项值得在稳健性表中报告的诊断信息; 研究者在解释 ss 轨与 full/ctx 轨的差异时应先核对该银行-年单元的回退触发率, 避免把"回退导致的 ss≈full"现象误读为"银行与金科议题高度绑定"的实质性发现。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Nakatsuka, H., & Suimon, Y. (2026). How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures. Economics Letters, 265, 113002. https://doi.org/10.1016/j.econlet.2026.113002
<!-- rendered-citations:end -->
