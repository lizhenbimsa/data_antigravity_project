---
family_id: F220
novelty_exempt_rationale: "政治词权重敏感性梯子 (w_pol∈{0.0,0.5,1.0}) 是 du_2022 词典语调测度的消融/敏感性检验变体族, 非独立新构念, 其测度定义与权重取值依据已在母族文献 Du et al. (2022, Review of Finance) 中给出, 无需额外追新文献。"
columns:
- du_2022_polw00_tone_ctx
- du_2022_polw00_tone_full
- du_2022_polw00_tone_ss
- du_2022_polw05_tone_ctx
- du_2022_polw05_tone_full
- du_2022_polw05_tone_ss
- du_2022_polw10_tone_ctx
- du_2022_polw10_tone_full
- du_2022_polw10_tone_ss
unit: 语调得分 (无量纲, 幅度归一化, 约 [-1,1]; 聚合后为 bank-year 篇均值)
formula: "du_2022 词典逐篇幅度归一化语调 score, 政治正面词 (political_positive, 1,434 词) 权重 w_pol ∈ {0.0, 0.5, 1.0} 计入正侧 → 三轨 (full/ctx/ss) 内 bank-year 均值 (mean, 跳过 NaN)"
producer: news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (逐篇 score) ; news_process/pipeline/panel/encode.py (bank-year mean 聚合) ; news_process/pipeline/panel/stata_export.py (标签)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (du_2022_score_polw{00,05,10}{track})
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/jofi.12027
  type: journal
  authors: Garcia, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是同一条构念——银行相关金融报道的词典法语调倾向——在一个特定自由度上的敏感性:中文金融情感词典 du_2022 里"政治正面词"这一类词条计入正侧时应赋予多大权重。du_2022 词典源自 Du et al. (2022) 为中文金融文本构建的领域专用情感词典,其区别于英文经典词典与其他中文词典的关键特征,是把政治色彩浓厚的正面表述 (political_positive, 共 1,434 词) 单列为第三类,与普通正面词 (2,235 词)、负面词 (2,986 词) 并置。之所以要单列,是因为该文实证发现:政治正面词所携带的市场信号弱于普通正面词——它们更像是套话式、仪式化的表态,而非对企业基本面的真实积极判断。基于这一发现,生产口径对政治正面词赋予降低的 0.5 权重计入正侧,而非与普通正面词等同的 1.0 权重。本家族把这一权重取值作为一条独立的稳健性轴显式物化。

【方法学与计算】
逐篇得分在 tone_words.py 的 compute_dict_scores 内计算:文章分词 (jieba 0.42.1 冻结) 后,按情感词典逐词累加带号强度,普通正面词记 +1.0、负面词记 -1.0、政治正面词记 +w_pol,再叠加否定翻转、程度副词六级、转折 boost 三条全语言学规则,末以该篇 Σ|final| 幅度归一化得到约落在 [-1,1] 的连续 score。三个权重臂共用完全相同的全语言学规则,只改政治正面词这一个权重自由度:w_pol=0.0 把政治正面词视作非情感词完全剔除、不进任何计数与幅度;w_pol=0.5 为生产 canonical 折中口径 (与无后缀 du_2022_score 字节一致,不重算);w_pol=1.0 把政治正面词等同普通正面词全权计入正侧。逐篇三权重 score 落 22_tone_words.parquet,随后在 encode.py 的 bank-year 聚合层对每条轨道取篇均值 (mean, 自动跳过 NaN 短空文本),得到面板列 du_2022_polw{00,05,10}_tone{track}。列名 SSOT = tone_words.POLITICAL_WEIGHT_VARIANTS (byte-sync encode.POLITICAL_WEIGHT_SUFFIXES),唯一含政治正面词类的词典登记于 POLITICAL_WEIGHT_DICTS = {du_2022}。空文本或词典缺失时逐权重回填 NaN/0.0,与规则消融梯度分支对称。

【文献定位】
词典法语调测度的可信度长期是文本金融计量的核心议题。Loughran & McDonald (2011) 指出通用情感词典移植到金融文本会系统性误判,催生领域专用词典这一范式;Loughran & McDonald (2016) 的综述进一步把词典构造、加权与验证列为方法学关键环节。Tetlock (2007) 与 Garcia (2013) 确立了媒体语调对市场的可测量影响,是纯词频与加权语调计量的经典参照。就"词典法是否稳健"这一问题,Frankel et al. (2022) 在 Management Science 上系统比较了机器学习与词典法情感度量,论证不同测量选择应互为稳健性对照而非彼此取代——这正是本家族并排三权重臂的方法论依据。Du et al. (2022) 关于政治正面词弱信号的实证发现,则是 0.5 权重取值本身的直接来源。

【口径铁律】
三权重臂 (polw00/polw05/polw10) 各自 just-identified 并排,互为稳健性、不分主次;polw05 ≡ canonical 只是历史命名产物,并非语义上的"主轨"。三者证明主结论不被政治词权重这一取值驱动,禁止把不同权重臂混进同一 over-identified Hansen J 过度识别检验。该权重梯子与规则消融梯度正交、不交叉:三权重均在全语言学规则下算,避免 3×8 列组合爆炸。三轨 full/ctx/ss 同款铁律——三轨各自 just-identified 并排、互为稳健性,禁混同一 over-identified Hansen J。留篇门控为 full-only 口径 (2026-06-29):是否判为一篇银行金科报道只看 full 轨 llm_verified,ctx/ss 降为 conditional-on-full 的测度/稳健性轨,行宇宙为 full 留篇集子集,但 per-track 篇均值照各轨自身分母算。ss 轨语义镜像 ctx:无银行与金科同句共现时 content_ss 回退为全文 body。gate 测试见 tests/test_political_weight_ladder.py。

## VAR: du_2022_polw00_tone_ctx

【变体差分】
本列 = 政治词权重 w_pol=0.0 臂 × ctx 轨的 bank-year 篇均语调。权重维度上,它把 du_2022 词典的 1,434 个政治正面词完全剔除,视作非情感词,既不进正侧计数也不进幅度归一化的分母 (as-if-absent);因此本列度量的是"仅凭普通正面词与负面词"的语调,是政治表态被彻底剥离后的下界情形。轨道维度上,ctx 轨的文本载体是 content_ctx (标题 prepend + 实体上下文窗口),只保留目标银行实体邻近窗口的正文,而非全文;它相对 full 轨过滤掉了与银行无关的段落,是聚焦性更强的稳健性轨。本列与同权重的 polw00_full、polw00_ss 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨的 polw05_ctx、polw10_ctx 构成权重梯子并排。三轨与三权重两个维度均禁混进同一 over-identified Hansen J。ctx 轨受 full-only 留篇门控约束,为 conditional-on-full 测度轨,篇均值分母取 ctx 轨自身有效篇数。当某银行-年在 ctx 轨无有效文本时该格为 NaN,聚合 mean 自动跳过不污染。
 就解读而言,本列相对同轨 polw05_ctx 的系统性差,反映政治正面词从 ctx 焦点文本剔除后语调整体下移的程度;因 ctx 轨已聚焦银行邻近段落,政治表态类词条密度往往低于全文轨,故 polw00_ctx 与 polw05_ctx 之差在 ctx 轨上通常小于 full 轨对应差。这一跨轨差异本身即是权重敏感性与文本聚焦度交互的稳健性信息,但仍须逐轨逐权重各自 just-identified 使用,不得跨轨或跨权重拼进同一过度识别检验。

## VAR: du_2022_polw00_tone_full

【变体差分】
本列 = 政治词权重 w_pol=0.0 臂 × full 轨的 bank-year 篇均语调。权重语义同上:政治正面词全部剔除、视作非情感词,度量剥离政治表态后的语调下界。轨道维度上,full 轨的文本载体是 content_full (标题 prepend + 全文正文),是三轨中信息最完整、覆盖面最宽的载体,也是 full-only 留篇门控的判定轨——一篇报道是否计入银行金科报道宇宙由 full 轨决定,故 full 轨的篇均值分母即该银行-年的留篇总数。因此本列在三轨中承担 canonical 承重角色,ctx/ss 是其 conditional-on-full 的下位稳健性轨。本列与 polw05_full、polw10_full 构成权重梯子,三权重各自 just-identified 并排、互为稳健性不分主次,polw00 是政治词权重取零的极端臂,用于检验主结论是否被政治正面词的纳入所驱动;与 polw00_ctx、polw00_ss 构成三轨并排。两维度均禁混进同一 over-identified Hansen J。政治正面词占 du_2022 正侧词条相当比例,polw00 与 polw10 的差即刻画了该类词对整体语调的边际贡献幅度。
 在下游回归中若以本列替换 canonical polw05_full 作 treatment 或 control,系数应在符号与显著性上定性不变,方能支持主结论不被政治正面词纳入所驱动的稳健性论断。若 polw00_full 与 polw05_full 系数出现方向翻转,则提示该银行-年语调对政治表态类词条高度敏感,须在稳健性叙事中显式披露,而非隐入单一 canonical 列。full 轨作为留篇门控判定轨,其分母口径与 ctx/ss 轨不同,跨轨比较系数时须先在各自轨内标准化。

## VAR: du_2022_polw00_tone_ss

【变体差分】
本列 = 政治词权重 w_pol=0.0 臂 × ss 轨的 bank-year 篇均语调。权重语义同 polw00 家族:政治正面词完全剔除、as-if-absent,度量语调下界。轨道维度上,ss 轨的文本载体是 content_ss (标题 prepend + 银行与金科同句共现窗口 ±N 句,N 由 config filtering.yaml context_window.ss_sentence_radius 控制,默认 1),是三轨中最严格的聚焦轨——只取银行与金科词严格同句 (含邻近窗) 的片段。其回退语义镜像 ctx:当某篇无银行与金科同句共现时 content_ss 回退为全文 body,ss_is_fallback 置 True,与 ctx 共享 n_articles 分母口径。本列与 polw00_full、polw00_ctx 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨 polw05_ss、polw10_ss 构成权重梯子并排。三轨与三权重两维度均禁混进同一 over-identified Hansen J。在开发期 T=2 小样本上 ss 轨可能因回退比例高而退化,属预期现象;生产 T=19 语料下 ss 轨提供最贴近银行-金科语义焦点的语调测度。ss 轨受 full-only 门控约束,为 conditional-on-full 测度轨,分母取 ss 轨自身有效篇数。
 由于 ss 轨取材最窄,单篇有效词数往往偏少,幅度归一化后 score 的方差通常大于 full/ctx 轨,篇均值也更易受少数长文主导;因此 polw00_ss 与其余两轨的差异既含权重效应也含取材粒度效应,解读时须与同权重的 polw00_full/polw00_ctx 并置对照,而非孤立判读。政治正面词在严格同句共现片段中的出现频率通常低于全文,故 ss 轨上 polw00 与 polw10 的极端差往往是三轨中最小的,这与 ss 轨聚焦银行-金科事实性语句、政治表态密度较低的语义直觉一致。

## VAR: du_2022_polw05_tone_ctx

【变体差分】
本列 = 政治词权重 w_pol=0.5 臂 × ctx 轨的 bank-year 篇均语调。权重维度上,0.5 是生产 canonical 口径:依据 Du et al. (2022) 政治正面词信号弱于普通正面词的发现,对该类词赋予折半权重计入正侧;本臂逐篇 score 与无后缀 du_2022_score 字节一致 (同词典同规则 → 不重算,直接复用),故 polw05 是历史命名产物意义上的默认臂,而非语义上凌驾其余两臂的"主轨"。轨道维度上,ctx 轨载体为 content_ctx (标题 prepend + 银行实体上下文窗口),相对 full 轨聚焦银行邻近段落。本列与 polw05_full、polw05_ss 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨 polw00_ctx、polw10_ctx 构成权重梯子并排,0.5 臂居于 0.0 剔除臂与 1.0 全权臂之间的折中位置。三轨与三权重两维度均禁混进同一 over-identified Hansen J。权重梯子与规则消融梯度正交:本列在全语言学规则 (否定/程度/转折) 下计算,只让政治词权重这一个自由度变动。ctx 轨受 full-only 门控,为 conditional-on-full 测度轨。
 作为 canonical 权重与聚焦轨的组合,本列常用作 ctx 轨的首要语调稳健性对照:当 full 轨主结果建立后,以 polw05_ctx 复现可检验语调效应是否由银行无关段落的噪声驱动。若 ctx 轨系数与 full 轨定性一致,则支持效应源自银行邻近文本的真实语调而非全文泛化情绪。本列逐篇 score 与无后缀 du_2022_score 在 ctx 轨上字节一致,故不产生额外计算开销,是零成本复用生产 canonical 逻辑的稳健性轨;它与规则消融梯度的 ctx 轨列彼此正交,分别隔离权重自由度与语言学规则自由度。

## VAR: du_2022_polw05_tone_full

【变体差分】
本列 = 政治词权重 w_pol=0.5 臂 × full 轨的 bank-year 篇均语调,是整个家族最接近生产 canonical 语调的单列:权重取生产默认 0.5 (逐篇 score ≡ 无后缀 du_2022_score),轨道取信息最完整、承担 full-only 留篇门控判定的 full 轨。因此在下游若需要一条"代表 du_2022 词典法语调"的默认列,本列即是首选;但须强调 polw05 的默认地位来自历史命名与研究者对 0.5 权重的选择,并非它在识别上优于 polw00 或 polw10——三权重仍是各自 just-identified 并排、互为稳健性不分主次的关系。full 轨的篇均值分母为该银行-年的留篇总数 (full 轨 llm_verified 判定)。本列与 polw05_ctx、polw05_ss 构成三轨并排;与 polw00_full、polw10_full 构成权重梯子并排。三轨与三权重两维度均禁混进同一 over-identified Hansen J;权重梯子与规则消融梯度正交不交叉。0.5 权重的两句话依据 (弱信号折中 + 敏感性检验) 是论文与审稿披露的单一事实源 POLITICAL_WEIGHT_RATIONALE。
 在实务中,若论文正文只报告一条 du_2022 词典法语调,通常即引用本列,并在附录以 polw00_full 与 polw10_full 两端臂展示权重敏感性、以 ctx/ss 两轨展示文本聚焦度稳健性。须再次强调:本列的默认地位纯属历史命名 (无后缀即 0.5 权重、full 轨) 与研究者对 0.5 权重的选择,并非识别意义上的优越;三权重、三轨在计量上完全平权,任何把本列当作唯一真值、把其余臂当作次要校验的表述都与本项目"互为稳健性、不分主次"的口径相悖。

## VAR: du_2022_polw05_tone_ss

【变体差分】
本列 = 政治词权重 w_pol=0.5 臂 × ss 轨的 bank-year 篇均语调。权重维度取生产 canonical 折中 0.5,逐篇 score 与无后缀 du_2022_score 字节一致。轨道维度上,ss 轨载体为 content_ss (标题 prepend + 银行与金科同句共现 ±N 句窗口,默认 N=1),是三轨中语义焦点最严格的轨:它只在银行与金科词真正同句 (含邻近窗) 处取材,最贴近"银行-金科报道语调"这一目标构念。回退语义镜像 ctx:无同句共现时 content_ss 回退为全文 body,ss_is_fallback 置 True,共享 n_articles 分母。本列与 polw05_full、polw05_ctx 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨 polw00_ss、polw10_ss 构成权重梯子并排。三轨与三权重两维度均禁混进同一 over-identified Hansen J。在开发期 T=2 上 ss 轨因回退比例高可能与 ctx 轨高度相关甚至退化,属预期;生产 T=19 下本列提供 0.5 权重口径下最聚焦的语调稳健性证据。ss 轨受 full-only 门控,为 conditional-on-full 测度轨。
 因 ss 轨取材最严格,本列在开发期 T=2 上有效样本稀薄、可能与 polw05_ctx 高度相关甚至数值退化,此时不应据其单独下结论;须待生产 T=19 语料下有效篇数充足后,本列方能作为 0.5 权重口径下语义焦点最集中的语调稳健性证据。回退机制保证即使无同句共现,该篇仍以全文 body 参与聚合并标记 ss_is_fallback,避免样本骤减导致的选择性偏误;分析时可据 ss_is_fallback 比例判断本列在特定银行-年的可信度,回退比例过高的格应审慎解读。

## VAR: du_2022_polw10_tone_ctx

【变体差分】
本列 = 政治词权重 w_pol=1.0 臂 × ctx 轨的 bank-year 篇均语调。权重维度上,1.0 把政治正面词等同普通正面词全权计入正侧,是权重梯子的上界臂:它假设政治表态与普通积极表述携带同等强度的市场信号,与 Du et al. (2022) 弱信号发现相反,因而用于检验若不折减政治词权重、主结论是否改变。polw00 (剔除) 与 polw10 (全权) 两端之差即刻画政治正面词对整体语调的最大可能边际贡献。轨道维度上,ctx 轨载体为 content_ctx (标题 prepend + 银行实体上下文窗口),聚焦银行邻近段落。本列与 polw10_full、polw10_ss 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨 polw00_ctx、polw05_ctx 构成权重梯子并排。三轨与三权重两维度均禁混进同一 over-identified Hansen J;权重梯子与规则消融梯度正交,本列在全语言学规则下计算。ctx 轨受 full-only 门控,为 conditional-on-full 测度轨,分母取 ctx 轨自身有效篇数,空格 NaN 被聚合 mean 跳过。
 就解读而言,本列相对同轨 polw05_ctx 的系统性上移,量化了若不折减政治词权重会使 ctx 轨语调被高估的幅度;该幅度越大,说明政治表态类词条在银行邻近焦点文本中越活跃,主结论对权重取值的依赖也越强。因此 polw10_ctx 与 polw00_ctx 的跨臂差是 ctx 轨上政治正面词边际贡献的上界估计,与 full 轨对应差并置可判断这一贡献是否随文本聚焦度而变。三权重臂在 ctx 轨内各自 just-identified 并排,禁止把上界臂与折中臂拼进同一 over-identified Hansen J。

## VAR: du_2022_polw10_tone_full

【变体差分】
本列 = 政治词权重 w_pol=1.0 臂 × full 轨的 bank-year 篇均语调。权重维度上,1.0 是权重梯子上界:政治正面词与普通正面词同权计入正侧,不作任何折减,度量"政治表态全额计入"情形下的语调上界。它与 polw05 canonical 的差反映 0.5 折减的净影响,与 polw00 的差反映政治正面词的全部边际贡献——三权重臂共同支撑"主结论不被政治词权重取值驱动"这一稳健性论断。轨道维度上,full 轨载体为 content_full (标题 prepend + 全文正文),承担 full-only 留篇门控判定,篇均值分母为该银行-年留篇总数。本列与 polw10_ctx、polw10_ss 构成三轨并排;与 polw00_full、polw05_full 构成权重梯子并排。三权重各自 just-identified 并排、互为稳健性不分主次,polw10 无凌驾其余两臂的地位。三轨与三权重两维度均禁混进同一 over-identified Hansen J;权重梯子与规则消融梯度正交不交叉,本列在全语言学规则 (否定/程度/转折) 下计算,只变政治词权重一个自由度。
 本列与 Du et al. (2022) 政治正面词弱信号发现直接对立,因而在稳健性叙事中承担"反事实"角色:如果主结果在 polw10_full 下依然成立,则表明结论对政治词权重的具体取值不敏感,反而增强了 0.5 折中口径的说服力;如果结果在 polw10_full 下减弱或消失,则提示政治表态类词条的处理方式实质影响语调测度,须在正文中审慎讨论 Du et al. (2022) 弱信号折减的必要性。这一反事实价值正是把 1.0 上界臂纳入权重梯子的方法论理由,而非声称全权计入更优。

## VAR: du_2022_polw10_tone_ss

【变体差分】
本列 = 政治词权重 w_pol=1.0 臂 × ss 轨的 bank-year 篇均语调。权重维度取上界 1.0:政治正面词全权计入正侧,与普通正面词等同,用于检验不折减政治词权重时主结论是否稳健。轨道维度上,ss 轨载体为 content_ss (标题 prepend + 银行与金科同句共现 ±N 句窗口,默认 N=1),是三轨中语义焦点最严格的轨,只在银行与金科词同句处取材。回退语义镜像 ctx:无同句共现时回退为全文 body,ss_is_fallback 置 True,共享 n_articles 分母。本列与 polw10_full、polw10_ctx 三轨各自 just-identified 并排、互为稳健性不分主次;与同轨 polw00_ss、polw05_ss 构成权重梯子并排。三轨与三权重两维度均禁混进同一 over-identified Hansen J。在开发期 T=2 上 ss 轨因回退比例高可能退化,属预期;生产 T=19 下本列提供 1.0 权重口径、最聚焦语义焦点下的语调稳健性上界证据。ss 轨受 full-only 门控,为 conditional-on-full 测度轨,分母取 ss 轨自身有效篇数,空格 NaN 被聚合 mean 跳过不污染。
 综合三权重 × 三轨九列的整体设计意图:政治词权重梯子沿一个理论明确的自由度 (Du et al. 2022 弱信号折减) 提供 0.0/0.5/1.0 三点稳健性剖面,三轨则沿文本聚焦度提供 full/ctx/ss 三点剖面,两组剖面正交交叉但绝不合并进单一过度识别检验,共同支撑"银行金融报道词典法语调的主结论既不被政治词权重取值、也不被文本取材粒度所驱动"这一双重稳健性论断。本列作为最严格取材 × 最高权重的角落格,是九列中数值最易受少数长文与回退主导的一格,须结合 ss_is_fallback 比例与有效篇数谨慎解读。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Garcia, D. (2013). Sentiment during recessions. Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
