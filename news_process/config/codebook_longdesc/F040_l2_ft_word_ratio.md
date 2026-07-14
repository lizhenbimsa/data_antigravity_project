---
family_id: F040
columns:
- avg_ft_word_ratio
- avg_ft_word_ratio_std
unit: 相对披露密度 (无量纲比率, 篇章级 ∈ [0,1]); avg_ft_word_ratio 为组内均值 (同量纲 [0,1]), avg_ft_word_ratio_std 为组内样本标准差 (同量纲, ≥0)
formula: "篇章级 _ft_word_ratio = fintech_total_count / doc_length (doc_length==0 置 NaN); avg_ft_word_ratio = mean_{i in bank-year}(_ft_word_ratio_i); avg_ft_word_ratio_std = std_{i in bank-year}(_ft_word_ratio_i), ddof=1"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (篇章级 _ft_word_ratio 预计算 + agg mean/std); 标签 news_process/pipeline/panel/export.py
upstream:
- 11_news_bank.parquet (doc_length = len(str(内容)) 字符数)
- 12_news_fintech.parquet (fintech_total_count 金科词命中总次数)
citations:
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: The Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: "Political bias in corporate news: The role of conglomeration reform in China"
  venue: The Journal of Law and Economics
  vol: 60
  issue: 1
  pages_or_artno: 173-207
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1080/09296171003643098
  type: journal
  authors: Covington, M. A., & McFall, J. D.
  year: 2010
  title: "Cutting the Gordian knot: The moving-average type-token ratio (MATTR)"
  venue: Journal of Quantitative Linguistics
  vol: 17
  issue: 2
  pages_or_artno: 94-100
- doi: "10.1016/j.irfa.2025.104121"
  type: journal
  authors: "Fengler, M. R., & Phan, T. M."
  year: 2025
  title: "Unveiling themes in 10-K disclosures: A new topic modeling perspective"
  venue: "International Review of Financial Analysis"
- doi: "10.1016/j.jcae.2023.100395"
  type: journal
  authors: "Yu, X., & Zhao, L."
  year: 2024
  title: "Textual disclosure complexity and analysts' weighting of information"
  venue: "Journal of Contemporary Accounting & Economics"
- doi: "10.1287/mnsc.2024.05417"
  type: journal
  authors: "Siano, F."
  year: 2025
  title: "The News in Earnings Announcement Disclosures: Capturing Word Context Using LLM Methods"
  venue: "Management Science"
new_dois:
  - "10.1016/j.irfa.2025.104121"
  - "10.1016/j.jcae.2023.100395"
  - "10.1287/mnsc.2024.05417"
---

## CORE

【构念与来源】
avg_ft_word_ratio 家族刻画的是"银行相关报道文本内部, 金融科技词汇所占的相对篇幅密度"这一构念。它回答的问题不是"有多少篇报道谈到金科"(那是报道层面的占比构念), 而是"在一篇既定的银行报道里, 作者把多大比例的笔墨投向了金科话题"。这是一个词汇层面 (word-level) 的相对披露强度, 而非文档层面 (document-level) 的存在与否。构念上它对应披露研究中的"相对披露密度 (relative disclosure density)"传统: 一段文本中某主题词汇的出现频次, 需要除以文本自身的长度做归一化, 才能在长短不一的文档之间横向可比。若不归一化, 长报道天然堆更多命中词, 会把"报道更长"误读成"金科更受关注"。Jegadeesh 与 Wu (2013) 在内容分析测度中系统论证了以文本长度对主题词计数做归一化的必要性, 指出未经长度校正的原始计数会把文档篇幅混入主题强度信号, 本家族"命中计数 / 文本长度"的比率口径正是这一相对密度构念在银行×金科情境下的平移, 而非照搬任何单篇研究的具体分子分母定义。

【方法学与计算】
计算分两步, 严格遵循"先分后合 (compute-then-aggregate)"次序。第一步在篇章级: 对每一篇报道, 取上游 12_news_fintech 阶段产出的金科词命中总次数 fintech_total_count 作分子, 取 11_news_bank 阶段产出的文档长度 doc_length (= len(str(内容)), 即全文 内容 列的字符数) 作分母, 逐篇算出 _ft_word_ratio = fintech_total_count / doc_length; 当 doc_length 为 0 时置 NaN 以避免除零。第二步在 aggregate_panel() 中按 bank-year 分组聚合: avg_ft_word_ratio 取组内均值 (mean), avg_ft_word_ratio_std 取组内样本标准差 (std, pandas 默认 ddof=1)。这里的次序不可颠倒: 比率必须在 groupby 之前逐篇算好再取均值, 因为 mean(a/b) 一般不等于 mean(a)/mean(b) (Jensen 不等式); 若先把分子分母各自跨报道加总再相除, 得到的是"银行-年全体报道拼成一篇超级文档"的整体密度, 语义与"逐篇密度的集中趋势"不同, 且对长文档过度加权。源码注释 (encode.py L1370) 亦显式标注了这一 Jensen 陷阱。分母用字符数而非分词后词数, 是对中文文本免受分词器版本漂移影响的稳健选择——命中计数与长度口径都建立在原始 内容 列之上, 保证跨-run 确定性。

【文献定位】
本家族属于 text-as-data 计量传统里的"主题词频归一化"分支。以词频作为文本内容的可量化代理, 是内容分析的经典进路: Jegadeesh 与 Wu (2013) 的 word power 方法即以词频构造文本得分, 论证了词级计数在金融文本中的信息含量; Hansen、McMahon 与 Prat (2018) 在 FOMC 透明度研究中用计算语言学从文本频次里提取审议行为信号, 示范了"频次即行为强度代理"的识别逻辑。归一化环节则与词汇密度、type-token ratio 一脉相承: Covington 与 McFall (2010) 讨论了以文本长度对词汇计数做归一化时的口径问题, 提醒长度敏感性会污染未归一化的原始计数——这正是本家族坚持除以 doc_length 的动因。在词典与词汇口径的选择上, García、Hu 与 Rohrer (2023) 对金融词汇的信息色彩做了系统刻画, 支持"以特定主题词表逐词命中"这一测量前提。就中国媒体语料的构念效度而言, Piotroski、Wong 与 Zhang (2017) 揭示了中国上市公司新闻报道存在政治倾向与选择性, 提示本家族的密度读数须与情感、态度类测度分开解读: ft_word_ratio 只测"谈了多少金科", 不测"谈得好不好", 是纯粹的主题聚焦度而非语调。Fengler 与 Phan (2025, International Review of Financial Analysis) 对 10-K 文本主题相对显著度按文档长度做归一化建模, 与本家族以字符数归一化金科词命中密度的先分后合口径构念相通, 进一步印证了主题词密度须经文档长度校正才可跨文档比较这一测量原则。Yu 与 Zhao (2024, Journal of Contemporary Accounting & Economics) 考察 10-K 文本复杂度对分析师信息加权的影响, 支持本家族以文本篇幅归一化主题密度以确保跨文档可比的测量前提; Siano (2025, Management Science) 用 LLM 方法从盈余公告文本中捕捉词语语境信息含量, 呼应本家族以词汇命中密度作为主题聚焦强度代理的测量逻辑。需强调本家族与 fintech_share 是两个不同构念: fintech_share 分母是 bank-year 去重后的报道篇数, 度量的是"多少比例的报道涉金科"(报道层面存在性占比); ft_word_ratio 分母是单篇字符长度, 度量的是"单篇内部金科着墨密度"(词汇层面强度), 两者互补而非替代, 不可混用。本家族无三轨 (full/ctx/ss) 分裂、无 co-primary 双轨嵌入、无阈值/权重梯子——它是单一 track-agnostic 的元数据密度测度, 因此不涉及"多轨并排各自 just-identified、禁混同一 over-identified Hansen J"的稳健性梯子口径; 其稳健性来自与 fintech_share、avg_ft_intensity (TF-IDF 加权技术重度) 等平行密度/强度族的构念三角互证。

## VAR: avg_ft_word_ratio

【变体差分】
本列是家族 canonical 无后缀主列, 对应聚合入口 agg['avg_ft_word_ratio'] = ('_ft_word_ratio', 'mean'), 即银行-年组内所有报道的篇章级金科词密度 _ft_word_ratio 的算术均值。它刻画的是该银行在该年度报道里"金科着墨密度的集中趋势 (中心水平)": 值越高, 表示平均而言每篇银行报道把越大比例的字符篇幅投向了金融科技话题。与同族的 _std 列相比, 本列回答"密度有多高", _std 回答"密度在报道间有多不齐"。取值范围继承篇章级比率的 [0,1] 无量纲区间, 均值天然落在该区间内。NaN 语义: 当某银行-年下所有报道的 doc_length 均为 0 (退化文本) 或该 bank-year 无任何报道时, 组内无有效比率, 均值为 NaN; 单篇报道也能给出有效均值 (等于该篇比率本身)。因分母采用原始字符长度而非分词词数, 本列对 jieba 分词器版本冻结不敏感, 具备跨-run 位级确定性, 不属于 BLAS-FP 非确定网络列, 可纳入 golden 逐列哈希核验。本列不带轨道后缀, 是 track-agnostic 元数据密度测度, 不参与三轨/双轨嵌入的 both-or-neither parity 约束; 其分子 fintech_total_count 走裸金科词表命中口径 (与 stage 13 共现硬过滤的邻近判据不同源, 是全文逐词命中计数), 分母 doc_length 复用 11_news_bank 已落列, 二者均在 stage 21 情感门控之前物化, 故本列不受 full-only 留篇门控 (2026-06-29) 的行宇宙收缩以外的额外条件约束——它落在留篇集之上按 bank-year 直接聚合。

## VAR: avg_ft_word_ratio_std

【变体差分】
本列是家族的离散度伴生列, 对应聚合入口 agg['avg_ft_word_ratio_std'] = ('_ft_word_ratio', 'std'), 即同一银行-年组内篇章级金科词密度 _ft_word_ratio 的样本标准差 (pandas std, ddof=1)。它与 canonical 均值列共享完全相同的篇章级输入 _ft_word_ratio, 唯一差分在于聚合算子: 均值列取一阶矩 (中心水平), 本列取二阶中心矩的平方根 (组内跨报道波动)。构念上本列度量的是"该银行该年度的金科报道密度是否稳定": 值越大, 说明该 bank-year 下不同报道对金科的着墨强度越参差——有的报道几乎通篇金科、有的仅偶尔带过; 值越小, 说明各篇密度趋于一致。它是对 canonical 均值的二阶补充, 可用作叙事异质性 (coverage heterogeneity) 的代理, 与均值列正交刻画分布的位置与形状。关键的 NaN 语义须留意: 样本标准差在组内有效报道数为 1 时无法定义 (ddof=1 分母为 n-1=0), 故任何"该银行-年仅一篇有效报道"的格子, 本列必然为 NaN, 而 canonical 均值列在同一格子仍有值——这是两列覆盖率天然不等的结构性原因, 下游回归若纳入本列会因单篇格子被剔除而缩减有效样本, 须在样本口径披露中说明。取值下界为 0 (所有报道密度相同), 无固定上界但受 [0,1] 篇章比率约束而有限。与均值列一致, 本列同样是 track-agnostic 无后缀元数据测度, 不带三轨/双轨/梯子语义, 具跨-run 确定性, 可纳入 golden 核验; 其数值随 golden 重生按盘上语料实测漂移, 在 T=2 开发面板上因多数 bank-year 仅少量报道而大面积 NaN 属预期退化, 生产 T=18 语料下方能给出稳定的组内离散读数。

<!-- rendered-citations:begin -->
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94-100. https://doi.org/10.1080/09296171003643098
Fengler, M. R., & Phan, T. M. (2025). Unveiling themes in 10-K disclosures: A new topic modeling perspective. International Review of Financial Analysis. https://doi.org/10.1016/j.irfa.2025.104121
Yu, X., & Zhao, L. (2024). Textual disclosure complexity and analysts' weighting of information. Journal of Contemporary Accounting & Economics. https://doi.org/10.1016/j.jcae.2023.100395
Siano, F. (2025). The News in Earnings Announcement Disclosures: Capturing Word Context Using LLM Methods. Management Science. https://doi.org/10.1287/mnsc.2024.05417
<!-- rendered-citations:end -->
