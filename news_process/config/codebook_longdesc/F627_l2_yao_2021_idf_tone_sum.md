---
family_id: F627
columns:
- yao_2021_idf_tone_sum_ctx
- yao_2021_idf_tone_sum_full
- yao_2021_idf_tone_sum_ss
unit: 语调得分 (连续, IDF 加权正负词计数之差; 篇章级量纲后聚合为 bank-year 加权计数总和 sum, 非均值; 理论上不做 [-1,1] 归一)
formula: 'idf_tone_sum = Σ_{w∈正面词} idf(w)·count(w) − Σ_{w∈负面词} idf(w)·count(w) (词典=yao_2021, 否定翻转/程度副词/转折等语言学规则先作用于原始计数; idf(w) 三步流程 = ① raw_idf(w)=log10(N/(1+df(w))) smooth IDF ② normalized_idf(w)=raw_idf(w)/mean(raw_idf) 均值归一化 ③ final_idf(w)=Winsorize(normalized_idf, P1, P99) 双侧缩尾; 篇章级不做长度归一, 聚合到 bank-year 时对同行样本内文章取算术求和 sum, 与同模块 mean 口径的 idf_tone 姊妹列区分)'
producer: pipeline\sentiment\tone_words.py::build_idf_weights (逐篇 IDF 权重计算与加权打分) ; pipeline\panel\encode.py (bank-year 聚合, agg[f'{d}_idf_tone_sum{track}']=('...', 'sum')) ; pipeline\panel\stata_export.py (面板标签)
upstream: []
citations:
- {doi: '10.1093/rof/rfab036', type: journal, authors: 'Du, Z., Huang, A. G., Wermers, R., & Wu, W.', year: 2022, title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary', venue: 'Review of Finance', vol: '26', issue: '3', pages_or_artno: '673-719'}
- {doi: '10.1093/rfs/hhx055', type: journal, authors: 'You, J., Zhang, B., & Zhang, L.', year: 2018, title: 'Who Captures the Power of the Pen?', venue: 'The Review of Financial Studies', vol: '31', issue: '1', pages_or_artno: '43-96'}
- {doi: '10.1016/j.jfineco.2013.08.018', type: journal, authors: 'Jegadeesh, N., & Wu, D.', year: 2013, title: 'Word Power: A New Approach for Content Analysis', venue: 'Journal of Financial Economics', vol: '110', issue: '3', pages_or_artno: '712-729'}
- {doi: '10.1287/mnsc.2021.4156', type: journal, authors: 'Frankel, R., Jennings, J., & Lee, J.', year: 2022, title: 'Disclosure Sentiment: Machine Learning vs. Dictionary Methods', venue: 'Management Science', vol: '68', issue: '7', pages_or_artno: '5514-5532'}
- {doi: '10.1257/jel.20181020', type: journal, authors: 'Gentzkow, M., Kelly, B., & Taddy, M.', year: 2019, title: 'Text as Data', venue: 'Journal of Economic Literature', vol: '57', issue: '3', pages_or_artno: '535-574'}
- {doi: '10.1017/CBO9780511809071', type: book, authors: 'Manning, C. D., Raghavan, P., & Schütze, H.', year: 2008, title: 'Introduction to Information Retrieval', venue: 'Cambridge University Press'}
- doi: "10.1016/j.intfin.2023.101920"
  type: "journal"
  authors: "Aysan, A. F., Caporin, M., & Cepni, O."
  year: 2024
  title: "Not all words are equal: Sentiment and jumps in the cryptocurrency market"
  venue: "Journal of International Financial Markets, Institutions and Money"
  vol: "91"
  pages_or_artno: "101920"
new_dois: []
novelty_exempt_rationale: "该家族是 yao_2021 词典语调测度的聚合算子变体(idf 加权+sum 聚合, 与同模块 mean 口径的 idf_tone 姊妹列共享同一篇章级打分, 仅聚合算子不同), 属于词典加权/聚合谱系的技术性衍生测度而非独立新构念, 其学术依据已由母族词典文献(Du 2022)及 word power/IDF 加权方法学文献(Jegadeesh & Wu 2013; Gentzkow et al. 2019)在正文中充分给出。"
---

## CORE

【构念与来源】
本家族测度中文银行/金科新闻报道的语调 (media tone), 词典来源为 yao_2021 (中文金融情感词典之一, 与词典消融梯度 SSOT 中其余五部词典 jiang_2021/bian_2021/du_2022/you_2018/loughran 并列, 同属 tone_words 模块统一的正负词表结构)。与家族 canonical 无后缀的等权求和口径不同, 本家族的差分维度是 idf (逆文档频率) 加权: 词典命中词不再按等权计入语调分, 而是按该词在语料内的稀缺程度加权后再求和, 思路对应 Jegadeesh & Wu (2013) 提出的 word power 方法——在文本内容分析中, 罕见但情感极性明确的词往往比常见泛化词携带更多信息, 用逆文档频率对词频加权可以提升测度对真实语调的区分力, 抑制高频套话词稀释信号。idf_tone_sum 是词典消融/加权谱系里的一支「稀有度敏感」测度, 与词典本身的语言学规则消融梯度 (否定翻转/程度副词/转折的 powerset, `{dict}_score_{raw,negonly,degonly,advonly,...}`) 正交——idf 加权作用于计数环节而非规则环节, 二者可以叠加但本家族聚焦纯粹的加权维度, 不与规则消融交叉验证同一自由度。

【方法学与计算】
计算流程分两层。篇章层: 先按 yao_2021 词典对文章分词结果做正/负面词命中扫描, 命中词计数经否定翻转、程度副词、转折等中文语言学规则调整后得到原始计数; 随后对每个命中词乘以其经三步流程算出的 idf 权重, 得到 idf 加权计数。IDF 权重构造 (`tone_words.py::build_idf_weights`) 并非简单的 ln(N/df(w)), 而是 smooth-IDF + 均值归一化 + Winsorization 三步: 第一步在全语料唯一文档 (按文本内容去重, 防同篇文章展开成多行虚增 N 与 df(w)) 上算 raw_idf(w)=log10(N/(1+df(w))) (以 10 为底、分母加 1 平滑, 区别于不带平滑项的朴素 IDF 定义); 第二步把每部词典内全部 raw_idf 值除以其自身均值做归一化, 使 idf 加权后的得分量级与未加权版本大致可比、可共享同一套阈值; 第三步对归一化后的权重做 P1/P99 双侧 Winsorization, 削平最极端 1% 的权重, 防止个别超稀有词的权重畸高而单点主导整篇语调分, 也防止极高频词权重被压到接近零而完全失去区分力。语调分 idf_tone_sum = 正面加权计数之和 − 负面加权计数之和, 不做篇幅长度归一 (与家族内其它 `_sum` 后缀测度口径一致, 量纲随文章篇幅与命中词稀有度联合变化, 区别于按篇幅归一的 `_tone`/`_score` 系列)。bank-year 面板层: `pipeline/panel/encode.py` 对同一银行-年份样本内全部留篇文章的篇章级 idf_tone_sum 取算术求和 (sum), 得到面板列 — 这一点须与同模块紧邻的姊妹列 `{dict}_idf_tone{track}` 明确区分: 后者对同一篇章级底层分数取的是算术均值 (mean), 二者共享同一篇章级 idf 加权打分, 仅面板聚合算子不同, 命名后缀 `_sum` 正是为区分两种聚合口径而设, 不可混淆。三轨列 (`_full`/`_ctx`/`_ss`) 分别在全文、银行∧金科实体窗、银行∧金科同句±N窗三种文本范围上独立重复上述扫描与加权, 彼此各自 just-identified 并排、互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 设定; 三轨的行样本口径遵循全库 full-only 留篇门控 (2026-06-29 起): 一篇报道是否计入"银行金科报道"样本只看 `llm_verified_full`, ctx/ss 是 conditional-on-full 的测度轨、行宇宙是 full 留篇集的子集, 不单独扩样本。ss 轨在银行∧金科无同句共现时镜像 ctx 的回退语义, 退化为全文 body 扫描并置 `ss_is_fallback=True`, 与 ctx 共享 `n_articles` 分母, 保证退化情形下三轨仍可比。IDF 权重本身按设计在三轨间共享同一份基于 content_full 语料计算的权重表, 不按轨分语料重算, 三轨差异只体现在扫描文本范围, 不体现在权重口径上。

【文献定位】
词典法度量金融文本语调是文本分析文献的主干范式之一, Du et al. (2022, Review of Finance) 构建了本项目采用的中文金融情感词典族之一, 强调通用情感词典 (如英文 Loughran-McDonald) 直接迁移到中文金融语境会因领域特异性和语言结构差异而失真, 需专门构建/校准中文金融词典——这也是本项目并行采用六部中文词典互为稳健性的方法学依据。idf 加权计数的整体设计思路对应 Jegadeesh & Wu (2013, Journal of Financial Economics) word power 方法的核心洞见, 即词的信息含量应随其在语料中的稀缺度调整而非等权处理, 高频泛化词 (如"发展""合作") 携带的情感辨识力弱, 低频特定词往往语调信号更强。本家族权重计算的具体数学形式则更直接依据信息检索与文本计量文献的标准做法: Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 在其"Text as data"综述 §2.2 中系统阐述了 TF-IDF 方法学在经济学文本分析中的适用性与构造规范, 是本家族 IDF 权重构造的直接方法学依据; smooth IDF 的具体公式 raw_idf(w)=log10(N/(1+df(w))) (分母加 1 平滑, 避免 df(w)=0 时除零) 采用了 Manning, Raghavan & Schütze (2008, *Introduction to Information Retrieval*) 第 6.2.1 节的经典定义, 是信息检索教材文献中最广泛采用的 IDF 平滑写法之一。均值归一化与 P1/P99 Winsorization 这两步保险性后处理, 遵循稳健统计中对极端观测值双侧缩尾以防单点主导的通行做法, 目的是让 idf 加权版语调分与等权版语调分量级可比、共享同一套下游阈值。You, Zhang & Zhang (2018, Review of Financial Studies) 在研究媒体报道对中国上市公司资本市场影响时同样采用词典法度量语调并强调方法多元化对结论稳健性的重要性, 与本项目"词典/LLM/BERT 三法互为稳健性"的总体设计取向一致。Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习法与词典法在披露文本情感测度上的差异, 指出词典法的可解释性与稳定性优势, 也提示了不同加权/规则设定 (如本家族的 idf 加权臂) 对结果的敏感性需要专门披露与检验, 这正是本项目为每部词典设置消融梯度、权重梯度与本 idf 加权测度并行披露的方法学考量。 Aysan、Caporin 与 Cepni (2024) 为本家族这一加权臂的基本前提补上了近期实证注脚: 该文以日内跳跃检测配合 logistic 回归, 发现信息发布提高跳跃概率, 且只有情绪类或关涉市场基本面的情感维度比其它维度更易引发跳跃, 并据此提出 "words are not all created equal", 支持了"词典命中词不应等权计入语调分"这一本家族赖以成立的动机。援引时须严守其射程: 该文的"非等权"落在情感维度/类别 (情绪 vs 基本面) 层面, 而非本家族按语料稀有度施加的词项级 idf 加权 (raw_idf(w)=log10(N/(1+df(w))) 经均值归一化与 P1/P99 双侧 Winsorization), 二者仅在"反对等权计数"这一动机上相通, 权重的函数形式与信息来源完全不同; 其标的为加密货币市场的日内跳跃与英文新闻, 既无中文金融词典口径, 也不涉及本家族篇章级不做长度归一、再在 bank-year 内求和的聚合设定。故该文只为差异化赋权的动机提供旁证, 不构成对 idf 权重三步构造 (smooth IDF / 均值归一化 / 双侧缩尾) 或 sum 聚合算子的直接证成; 其定位与本家族既有的 Jegadeesh & Wu (2013)、Gentzkow, Kelly & Taddy (2019) 等加权方法学锚点属互补而非替代, 各自锚定不同环节。
## VAR: yao_2021_idf_tone_sum_full

【变体差分】
`_full` 轨在全文文本 (标题+正文全部内容, `content_full`, stage 14 物化, `prepend_title` 拼接标题与正文) 范围内执行 yao_2021 词典的 idf 加权语调扫描, 是三轨中样本覆盖最广、也最贴近记者原始叙事结构的一支——既包含开篇背景铺垫、行业综述性段落, 也包含直接涉及目标银行与金科业务关系的核心叙述, 因此其 idf 加权计数天然会把与银行-金科关系无直接关联的段落词汇也纳入扫描范围。留篇门控 (是否计入银行金科报道样本) 直接以本轨 `llm_verified_full` 为准, 即 `_full` 轨的行样本定义了整个 idf_tone_sum 家族的行样本口径上限; `_ctx`/`_ss` 两轨的行样本是本轨留篇集的子集 (conditional-on-full), 不会反向扩大或收窄 `_full` 轨自身的样本范围。该轨与 `_ctx`/`_ss` 两轨各自 just-identified、互为稳健性并排, 三者共同构成 idf 加权测度对文本窗口宽窄的稳健性谱系, 但不构成同一识别方程内的过度识别工具组合, 不应被同时塞进单一 over-identified Hansen J 检验。就 idf 加权本身而言, `_full` 轨的语料范围最大, 逆文档频率 idf(w) 的分母 df(w) (含词 w 的文章数) 统计口径与另外两轨在同一语料上共享, 但因扫描文本范围不同, 命中词的具体计数结果不同, 三轨语调分不可直接相减比较绝对水平, 只适合比较标准化后的方向与显著性。

## VAR: yao_2021_idf_tone_sum_ctx

【变体差分】
`_ctx` 轨仅在标题+目标银行与金科实体窗口范围内 (`content_ctx`, 由 stage 14 `ctx_materializer` 物化) 执行同一套 yao_2021 idf 加权扫描, 聚焦报道中直接围绕银行与金科关联实体的局部文本, 意在剔除全文中与银行-金科关系无关的背景段落 (如行业综述、监管政策通稿式铺垫) 对语调分的稀释, 从而得到更贴近"记者在描述该银行与该金科业务/机构时用词倾向"这一构念的测度。行样本是 `_full` 轨留篇集的子集 (conditional-on-full), 分母 `n_articles` 与 `_ss` 轨共享同一口径, 便于两轨在退化情形下互相比对。判定不对称口径在本轨同样成立: 银行侧命名判定包含否定+短名过滤, 金科侧判定为裸 AC 自动机 1506 词表匹配, 这一不对称性由上游实体窗口构造阶段决定, idf_tone_sum 计算本身不额外引入新的不对称规则。与 `_full`/`_ss` 互为稳健性并排、不分主次, 差异主要体现为文本窗口范围收窄而非计算规则或词典本身发生变化——正因为词典、加权公式、否定/程度副词/转折规则三者在三轨间完全一致, `_ctx` 与 `_full`/`_ss` 之间的差异才可以被干净地归因于"扫描范围"这一单一维度, 是稳健性检验设计上刻意保持的控制变量。

## VAR: yao_2021_idf_tone_sum_ss

【变体差分】
`_ss` 轨在标题+银行∧金科实体同句 (±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 默认 1 控制) 范围内执行同一套 yao_2021 idf 加权扫描, 是三轨中文本范围最窄、局部性最强的一支, 用于检验语调测度在极端聚焦设定 (仅取银行与金科关键词真正同句共现的那句话及其邻近窗口) 下是否仍与 full/ctx 两轨定性一致。当一篇报道中银行与金科实体不存在同句共现时 (即未通过 stage 13 严格同句共现判据, 而只满足更宽松的段落级/篇章级共现放行标准), 本轨镜像 `_ctx` 的回退语义, 退化为对全文 body 扫描并将该行标记为 `ss_is_fallback=True`, 与 `_ctx` 共享同一 `n_articles` 分母口径, 避免回退情形下产生单边孤儿列或分母失配——这一回退设计的意义在于: 即便某篇文章没有真正的"同句"证据, 也不能因此把该篇文章从 `_ss` 轨的分母中静默剔除, 否则会导致 `_ss` 轨样本量系统性小于 `_full`/`_ctx` 轨, 破坏三轨可比性。与 `_full`/`_ctx` 两轨各自 just-identified 并排, 互为稳健性、不分主次, 三轨禁止混入同一 over-identified Hansen J 设定; 在 T=2 的本机开发样本上, `_ss` 轨往往因严格同句证据稀少而呈现较高比例的回退标记, 这属于开发样本规模下的预期退化现象, 不代表生产全量语料 (T=19) 下同样稀疏。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Jegadeesh, N., & Wu, D. (2013). Word Power: A New Approach for Content Analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as Data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
Aysan, A. F., Caporin, M., & Cepni, O. (2024). Not all words are equal: Sentiment and jumps in the cryptocurrency market. Journal of International Financial Markets, Institutions and Money, 91, 101920. https://doi.org/10.1016/j.intfin.2023.101920
<!-- rendered-citations:end -->
