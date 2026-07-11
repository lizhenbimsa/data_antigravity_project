---
family_id: F015
columns:
- attention_pct_full
- attention_pct_full_j70w10
- attention_pct_full_j70w5
- attention_pct_full_j75w5
- attention_pct_full_j80w10
unit: "比例 (proportion, 无量纲, 值域 [0, 1])"
formula: "attention_pct_full = N_ft / N_all; N_ft = 该行该年经 stage-21 验证 (full-only 留篇门控) 的金融科技报道篇数, N_all = 12_fintech_news_full 该行该年全部银行新闻篇数 (未门控); 变体 attention_pct_full_jXXwY = 同式在更严去重存活集上重算 (Jaccard=0.XX, 窗口=Y 工作日; 分子=verified∩存活, 分母=变体存活银行新闻; 生产锚点 j80w5=无后缀列)"
producer: "news_process/pipeline/panel/attention_media.py::compute_attention_treatments (canonical); news_process/pipeline/panel/dedup_sensitivity.py::compute_dedup_sensitivity_treatments (jXXwY 变体, 步骤 6b-3)"
upstream:
- 12_fintech_news_full.parquet (分母 N_all + bank-year 全集脊柱; 变体 MinHash 判重语料)
- 15_fintech_intensity.parquet (分子 fintech 文章集)
- 24_herd_decay.parquet (stage-21 verified 门控宇宙, 经 restrict_to_verified semi-join)
citations:
- doi: 10.1002/mde.70100
  type: journal
  authors: "Li, Y."
  year: 2026
  title: "The textual tone of annual reports and market attention: Evidence from Chinese listed companies"
  venue: "Managerial and Decision Economics"
- doi: 10.1016/j.jempfin.2025.101670
  type: journal
  authors: "Chen, Z., Li, Z., Liu, J., & Liu, X."
  year: 2026
  title: "Information salience, investor attention, and stock price crash risk"
  venue: "Journal of Empirical Finance"
  vol: 85
  pages_or_artno: "Article 101670"
- doi: 10.1093/qje/qjaf002
  type: journal
  authors: "Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A."
  year: 2025
  title: "The diffusion of new technologies"
  venue: "The Quarterly Journal of Economics"
  vol: 140
  issue: 2
  pages_or_artno: "1299-1365"
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: "Marchetti, S., Tarducci, E., & Branzoli, N."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "SSRN Working Paper"
- doi: 10.1111/jofi.13377
  type: journal
  authors: "Bybee, L., Kelly, B., Manela, A., & Xiu, D."
  year: 2024
  title: "Business news and business cycles"
  venue: "The Journal of Finance"
  vol: 79
  issue: 5
  pages_or_artno: "3105-3147"
- doi: 10.1111/acfi.13328
  type: journal
  authors: "Ni, Y."
  year: 2024
  title: "Media coverage and disclosure of short-termism tone: Evidence from China"
  venue: "Accounting & Finance"
  vol: 64
  issue: S1
  pages_or_artno: "5107-5131"
- doi: 10.1111/jofi.13219
  type: journal
  authors: "Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R."
  year: 2023
  title: "Firm-level climate change exposure"
  venue: "The Journal of Finance"
  vol: 78
  issue: 3
  pages_or_artno: "1449-1498"
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A."
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: "The Review of Financial Studies"
  vol: 36
  issue: 12
  pages_or_artno: "4919-4964"
- doi: 10.1093/restud/rdab030
  type: journal
  authors: "Borusyak, K., Hull, P., & Jaravel, X."
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: "The Review of Economic Studies"
  vol: 89
  issue: 1
  pages_or_artno: "181-213"
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: "Li, K., Mai, F., Shen, R., & Yan, X."
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: "The Review of Financial Studies"
  vol: 34
  issue: 7
  pages_or_artno: "3265-3315"
- doi: 10.1287/mnsc.2020.3682
  type: journal
  authors: "Bellstam, G., Bhagat, S., & Cookson, J. A."
  year: 2021
  title: "A text-based analysis of corporate innovation"
  venue: "Management Science"
  vol: 67
  issue: 7
  pages_or_artno: "4004-4031"
- doi: 10.1257/aer.20181047
  type: journal
  authors: "Goldsmith-Pinkham, P., Sorkin, I., & Swift, H."
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: "American Economic Review"
  vol: 110
  issue: 8
  pages_or_artno: "2586-2624"
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: "Cheng, M., & Qu, Y."
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: "Pacific-Basin Finance Journal"
  vol: 63
  pages_or_artno: "101398"
- doi: 10.1093/qje/qjz021
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A."
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: "The Quarterly Journal of Economics"
  vol: 134
  issue: 4
  pages_or_artno: "2135-2202"
- doi: 10.1257/jel.20181020
  type: journal
  authors: "Gentzkow, M., Kelly, B., & Taddy, M."
  year: 2019
  title: "Text as data"
  venue: "Journal of Economic Literature"
  vol: 57
  issue: 3
  pages_or_artno: "535-574"
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: "Chen, M. A., Wu, Q., & Yang, B."
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: "The Review of Financial Studies"
  vol: 32
  issue: 5
  pages_or_artno: "2062-2106"
- doi: 10.1257/aer.20170947
  type: journal
  authors: "Qin, B., Strömberg, D., & Wu, Y."
  year: 2018
  title: "Media bias in China"
  venue: "American Economic Review"
  vol: 108
  issue: 9
  pages_or_artno: "2442-2476"
- doi: 10.1111/jofi.12179
  type: journal
  authors: "Peress, J."
  year: 2014
  title: "The media and the diffusion of information in financial markets: Evidence from newspaper strikes"
  venue: "The Journal of Finance"
  vol: 69
  issue: 5
  pages_or_artno: "2007-2043"
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: "Da, Z., Engelberg, J., & Gao, P."
  year: 2011
  title: "In search of attention"
  venue: "The Journal of Finance"
  vol: 66
  issue: 5
  pages_or_artno: "1461-1499"
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: "Tetlock, P. C."
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: "The Review of Financial Studies"
  vol: 24
  issue: 5
  pages_or_artno: "1481-1512"
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: "Engelberg, J. E., & Parsons, C. A."
  year: 2011
  title: "The causal impact of media in financial markets"
  venue: "The Journal of Finance"
  vol: 66
  issue: 1
  pages_or_artno: "67-97"
- doi: 10.1111/j.1475-679X.2009.00357.x
  type: journal
  authors: "Bushee, B. J., Core, J. E., Guay, W., & Hamm, S. J. W."
  year: 2010
  title: "The role of the business press as an information intermediary"
  venue: "Journal of Accounting Research"
  vol: 48
  issue: 1
  pages_or_artno: "1-19"
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: "Bramoullé, Y., Djebbari, H., & Fortin, B."
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: "Journal of Econometrics"
  vol: 150
  issue: 1
  pages_or_artno: "41-55"
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: "Fang, L., & Peress, J."
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: "The Journal of Finance"
  vol: 64
  issue: 5
  pages_or_artno: "2023-2052"
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: "The Journal of Finance"
  vol: 62
  issue: 3
  pages_or_artno: "1139-1168"
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: "Romano, J. P., & Wolf, M."
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: "Econometrica"
  vol: 73
  issue: 4
  pages_or_artno: "1237-1282"
- doi: 10.2307/2298123
  type: journal
  authors: "Manski, C. F."
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: "The Review of Economic Studies"
  vol: 60
  issue: 3
  pages_or_artno: "531-542"
new_dois:
- 10.1093/rfs/hhq141
- 10.1111/j.1475-679X.2009.00357.x
---

## CORE

【构念与来源】本家族承载的构念是银行层面的金融科技媒体议程份额, 即一家银行在一个日历年度内的全部媒体报道之中, 经大语言模型验证确属银行与金融科技主题的报道篇数所占的比例。它回答的问题是: 在媒体关于这家银行的全部叙事里, 金融科技议题挤占了多大份额的版面。媒体注意力文献存在两条经典测量范式。第一条是覆盖总量范式, 以 Fang & Peress (2009) 为代表, 直接以报道篇数或累积曝光强度度量注意力的绝对水平, 本仓库同族的强度指数走这一条路线, 属 extensive 边际。第二条是归一化份额范式, 以 Hassan et al. (2019) 的企业级政治风险测度为代表, 把主题命中量除以文本总量, 得到与企业媒体总曝光规模无关的相对配置测度, 属 intensive 边际。本家族明确属于后者: 分子是该行该年经验证的金融科技报道篇数, 分母是该行该年全部银行新闻篇数, 商结构性落在零到一的闭区间, 天然免疫于银行之间媒体总覆盖规模的巨大差异。大型国有银行与城市商业银行的年报道量可以相差数个数量级, 水平计数在截面上不可直接比较, 而议程份额可以。这一 intensive 份额范式在其后的企业级文本暴露文献中被反复复用: Sautner et al. (2023) 以电话会议文本中气候议题命中占比构造企业级气候暴露, Hassan et al. (2023) 以同构方法构造疫情暴露, 均以份额而非水平作为跨企业可比的暴露测度, 本列与它们在归一化逻辑上同构, 只是语料由电话会议换成中文银行新闻、议题由气候疫情换成金融科技。Da et al. (2011) 把注意力代理区分为间接代理与直接代理两类, 新闻覆盖属于前者, 搜索量属于后者, 并论证两类代理捕获的注意力时点与主体不同; 按其分类, 本家族是媒体供给侧的间接注意力代理, 度量的是媒体议程对金融科技议题的配置强度, 而非投资者的主动信息检索行为, 解读回归系数时必须保持这一构念定位, 不能把议程份额直接说成投资者注意力。Bybee et al. (2024) 用主题模型把全量商业新闻分解为可解释的议题注意力配置结构, 并证明新闻语料中的议题份额序列携带真实的宏观经济周期信息, 为议程份额这一测量对象的经济含义提供了当代基准; Chen et al. (2026) 进一步表明信息显著性与投资者注意力的联动影响股价尾部风险, 支持议程份额作为显著性代理的资产定价相关性。在中国语境一侧, Qin et al. (2018) 刻画了中国报业市场的偏倚结构与商业化梯度, 提示中文银行报道的议程构成受媒体属性系统性影响, 这正是本仓库以媒体来源风格暴露构造工具变量的动机之一; Ni (2024) 与 Li (2026) 分别以中国上市公司为对象研究媒体覆盖、文本语调与市场注意力的联动, 说明中文财经文本的议程与语调测度已进入主流实证议程, 本列是同一方法论传统在银行样本上的实现。构念的金融科技一侧, Chen et al. (2019) 用文本方法度量金融科技创新的价值分布, Cheng & Qu (2020) 给出中国银行业金融科技应用影响信用风险的直接证据, Kalyani et al. (2025) 用文本二元词组追踪新技术在企业与地区间的扩散, 三者共同支撑本仓库以金融科技词汇命中识别银行技术议题暴露的测量前提。测量前提的效度还有两条平行证据: Bellstam et al. (2021) 证明从分析师报告文本提取的创新测度即使对没有专利与研发支出记录的企业也能预测其后续增长与创新产出, 说明文本命中确实携带传统结构化指标之外的技术信息增量, 这正是本仓库在财务指标之外另建媒体文本测度的存在理由; Li et al. (2021) 则示范了以词向量从种子词自动扩展领域词表的机器学习构词范式, 并证明由此得到的企业文化测度具备跨企业效度, 本仓库金融科技词表的大模型辅助扩展与人工审校流程在方法学上与之同谱系, 词表覆盖度的时变漂移风险也因此须按同一标准披露。

【数据来源与样本宇宙】本家族五列全部在 stage 40 面板构建期物化, 消费三份上游产物。第一份是 12_fintech_news_full.parquet, 即共现硬过滤之后的全部银行新闻, 粒度为文章乘银行, 既含金融科技行也含非金融科技行, 为本列提供分母篇数与 bank-year 全集脊柱, 同时也是去重敏感性变体的判重语料。第二份是 15_fintech_intensity.parquet, 提供金融科技文章集合, 本家族只消费其行集与篇数, 不消费其强度分值。第三份是 stage-21 验证链路派生的 verified 宇宙, 落盘于 24_herd_decay.parquet, 经 restrict_to_verified 以 docid 与 target_bank 双键的 inner-join 半连接把分子收敛到经大模型验证确属银行金融科技报道的文章集合; 之所以用双键而非 docid 单键, 是因为验证发生在文章乘银行粒度上, 同一篇文章对甲银行可判真、对乙银行可判伪。留篇门控与全仓 full-only 口径完全一致: 一篇文章是否算作一篇银行金融科技报道, 只看 llm_verified_full 是否为真, ctx 与 ss 轨是 conditional-on-full 的测度轨, 不参与留篇判定; 24_herd_decay 的行宇宙即这一 full-only 留篇集, 分子因此天然锚定 full 轨验证结果。与分子形成刻意不对称的是, 分母与全集脊柱保持未门控: 非金融科技的银行新闻从不进入 stage 21 验证, 物理上不存在可门控的验证标记; 而且构念本身要求分母是全部银行报道, 议程份额等于已验证金融科技报道除以全部银行报道, 若把分母也收缩到金融科技子集, 份额恒等于一, 测度直接退化。这一分子门控、分母全集的组合才是干净的议程份额语义, 这一非对称口径与面板政策对齐族的 verified 域收敛完全同源, 由中性 helper 模块统一实现, 刻意与面板 runner 的同名内部函数解耦以避免循环 import。

【方法学与计算】canonical 列的计算分四步。第一步, 从两份输入各自以日期列派生年份, 无法解析的日期行剔除, 保证分组键完整。第二步, 在 12_full 上以银行乘年份去重得到全集脊柱, 并按同键分组计数得到分母篇数; 脊柱来自真实存在银行新闻的 bank-year 集合, 分母因此结构性大于等于一, 不存在除零。第三步, 分子帧经 verified 半连接门控后按银行乘年份分组计数得到金融科技篇数。第四步, 在全集脊柱上左连接分子, 分子缺失的格点填零, 有银行新闻但零金融科技报道是真实的零曝光, 信息性零参与回归; 随后以分子除分母得到本列。面板主表是平衡笛卡尔积, 可能包含全集脊柱之外的 bank-year, 即该银行该年完全没有任何银行新闻, 这些行在最终左连接后自然得到缺失值。于是形成一条必须牢记的非对称契约: 缺失值表示注意力不可测, 零值表示可测且真零, 两者语义不同, 回归中前者被逐行删除是正确行为, 后者保留。产出后有值域校验, 本列须落在零与一的闭区间内, 校验带微小数值容差, 越界记为错误日志。模块还会在日志中披露本列与同族强度指数的相关系数作为两测度同向性诊断, 但这仅是诊断信息: 强度与份额是 extensive 与 intensive 两个不同边际的测度, 按仓库口径各进各自的回归, 不同时进入一个右手边。

【去重敏感性梯子的方法学】预处理阶段的生产去重口径是精确去重叠加 MinHash 局部敏感哈希近重判定, Jaccard 相似度阈值零点八零, 配五个工作日的保留贪心时间窗: 近重簇内按日期升序, 后发文章若落在任一已保留文章的窗口之内即被删除。这一口径直接决定了所有计数型注意力测度的计数基。Tetlock (2011) 证明转载与陈旧信息会引发市场对同一信息的重复反应, 计数型媒体测度若不去重会把信息到达构念系统性高估; Hassan et al. (2019) 的份额范式也隐含排斥机械重复计数。与之相对, Bushee et al. (2010) 意义上的商业媒体作为信息中介的传播广度构念恰恰要求保留转载, 一条新闻被多少渠道重发本身就是广度信息, 该构念由控制变量模块的媒体广度测度另行实现, 刻意不去重, 两套口径并存是分工而非矛盾。顶级期刊的审稿惯例要求作者披露去重规则并证明主结论对去重参数扰动稳健, 去重敏感性模块把这一义务物化为四个更严格方向的重去重变体列: 阈值降到零点七零配五个工作日窗、阈值降到零点七五配五个工作日窗、阈值保持零点八零但窗口拉长到十个工作日、以及阈值与窗口双向同时收紧到零点七零配十个工作日的组合臂; 生产锚点即无后缀 canonical 列本身, 记为 j80w5。机制上, 模块在 12_full 文章全集按 docid 去重后一次性计算 MinHash 签名, 签名与判重参数无关, 因此四个变体之间复用同一批签名并配内容寻址缓存, 纯本地计算不产生任何大模型或嵌入调用费用; 随后按变体参数追加判重得到各自的存活集, 在存活集上按 bank-year 重算分子与分母, 分子是 verified 集合与变体存活集的交集篇数, 分母是变体存活的全部银行新闻篇数。分子分母同基是家族级不变量, 保证每个变体列仍然是语义干净的议程份额, 而不是分子分母口径错配的混合物。单调性不变量随之成立: 更严格的参数只会删除更多文章, 变体存活篇数不得超过生产存活篇数, 违反即报错误日志。变体网格可经 config 面板域覆盖, 但加载器会拒绝任何不严格于生产锚点的参数组合, 宽松方向在已去重语料上不可识别, 因为被生产去重删除的原文已经不可恢复, 想往宽松方向扰动必须从原始数据重跑预处理, 这一限制按口径诚实原则在论文中如实披露。

【口径诚实声明】变体列携带三条必须随行披露的方法学限定。第一, 两阶段近似: 变体是在已去重产物之上叠加更严去重, 其存活集不严格等于在原始语料上直接按该严参数去重的存活集, 机理在于时间窗判重是保留贪心的, 而低阈值下的近重簇是高阈值簇的超集, 某篇文章可能在生产参数的小簇里被删, 却会在直接重跑的大簇里因簇锚点更早或超出窗口而存活, 两阶段流程已经永久丢弃它, 无法复活; 因此变体结果应表述为在生产去重之上施加更严扰动的保守下界, 而非等价于从头重导, 相应标记落入语料层诊断 sidecar 供 Stata 表脚注引用。第二, 跨语料盲区: 生产去重在分类之前的全语料上进行, 变体只在银行新闻子集上重判重, 银行新闻与非银行新闻之间的跨子集近似重复在本敏感性中不可见, 会系统性低估直接重跑本会捕获的剔除量, 这是对银行新闻覆盖构念的有意范围限定。第三, 开发样本警示: 当前盘上是极小年份深度的试跑样本, 变体只追加剔除很小比例的文章, 变体列与生产锚点的面板内相关必然接近一, 这是低剔除率之下的预期平凡结果, 不构成稳健性证据; 真正的稳健性结论必须来自主回归系数在各变体下的符号与显著性稳定, 且全量语料上的剔除率与相关性都可能与试跑很不相同, 当前诊断数字不可外推。另须澄清一处域别: sidecar 报告的存活篇数与存活率是全 docid 域的去重存活率诊断, 与分子的验证交存活双重收敛域不同, 两者勿混读。

【文献定位】本家族在三支文献的交汇处。第一支是媒体与资产价格的因果文献: Tetlock (2007) 首次系统证明媒体内容对市场情绪与收益的预测力, Fang & Peress (2009) 证明媒体覆盖本身在股票截面上定价, Engelberg & Parsons (2011) 用地方报纸投递的地理差异分离媒体报道对交易行为的因果作用, Peress (2014) 用报纸罢工作为自然实验证明媒体在金融市场信息扩散中的因果角色。这一支确立了媒体测度作为处理变量的合法性, 也提示媒体覆盖内生于企业基本面, 识别须依赖外生变异。第二支是企业级文本暴露测度文献: Hassan et al. (2019)、Sautner et al. (2023)、Hassan et al. (2023) 把份额型文本暴露发展为跨企业跨期可比的标准测度构造, Kalyani et al. (2025) 把词组命中方法扩展到技术扩散测量, Gentzkow et al. (2019) 则给出文本即数据的方法论总纲, 强调文本测度的构造自由度必须以透明披露与敏感性检验约束, 本家族的去重梯子正是这一原则的落地。第三支是银行与金融科技文献: Chen et al. (2019)、Cheng & Qu (2020) 提供金融科技作为银行研究对象的价值与风险证据, Marchetti et al. (2025) 展示了把新闻文本聚合到银行乘年份粒度研究银行融资条件的口径先例, 与本仓库的 bank-year 聚合骨架直接同构。中国媒体市场的制度背景由 Qin et al. (2018) 提供, 中文财经文本测度的近期应用由 Ni (2024) 与 Li (2026) 提供, 商业新闻议题份额携带宏观信息的当代基准由 Bybee et al. (2024) 提供, 显著性与注意力的资产定价后果由 Chen et al. (2026) 提供。

【识别策略定位】本家族属于注意力论文 (P2, bank_fintech_attention) 的处理变量族, 该论文的主处理变量是累积曝光强度指数, 即强度累积和的对数化, 属 extensive 边际, 本列是同族 intensive 边际的并行测度: 强度指数回答银行被金融科技叙事覆盖的总量有多大, 本列回答金融科技议题在该行媒体议程中的相对占比有多高, 两者刻画同一现象的不同边际, 各进各自的回归规格, 不同时进入一个右手边; 该论文的结果变量另定于外部财务哨兵即金融科技投资的对数, 处理变量与结果变量分属两套, 本列是处理变量侧 intensive 边际的并行 headline, 而非被解释变量。识别层面须先厘清内生性的三条来源。其一是反向因果: 银行自身的金融科技战略与投入会主动吸引甚至制造媒体报道, 议程份额部分是战略的果而非因, 直接回归会把因果方向混淆。其二是遗漏变量: 银行规模、产权属性、区域禀赋与经营绩效同时驱动金融科技投入与媒体曝光, 使份额与结果的关联混入共同的前定因素。其三是测量误差: 分子的机器验证与分母的共现硬过滤都非无误, 分类噪声按经典衰减方向系统性压低估计系数。为此仓库在面板层物化了三类工具变量引擎, 论文规格以两阶段最小二乘配合它们缓解上述内生性, 每类引擎的识别假设各不相同, 须分别论证而非一揽子宣称外生。第一类是同组剔除自身的均值工具: 以同组同侪的金融科技议程份额均值为工具, 识别假设是同侪议程只通过共同的行业级金融科技冲击影响本行, 不经其他渠道直接作用于本行结果; 这一剔除自身的构造正是 Manski (1993) 反射问题的标准应对, 把本行排除出均值以打破内生的同时性联立, 而 Bramoullé et al. (2009) 证明当采用剔除自身的邻域均值时同侪效应可借网络结构获得识别。第二类是广义 Bartik 份额转移工具: 以全国金融科技议程的时间趋势乘以本行前定期的暴露份额构造, 其识别合法性有两种互补视角, Goldsmith-Pinkham et al. (2020) 把识别力归于暴露份额的外生性, Borusyak et al. (2022) 则把识别力归于冲击本身的外生性, 两种视角对本工具的排他性约束提出不同但可交叉检验的前提, 论文须择一或并陈其识别根据。第三类是媒体来源风格暴露工具: 以本行接触的媒体来源在金融科技报道倾向上的系统性差异构造供给侧暴露, 其准实验根据是 Engelberg & Parsons (2011) 用地方报纸投递的地理差异分离媒体因果, 以及 Peress (2014) 用报纸罢工作为外生的媒体供给冲击。三类工具各自 just-identified, 每个内生回归元只配一个工具, 因此单引擎内部不做 over-identified 的 Hansen J 过度识别检验。铁律必须复述: 生产锚点与四个去重变体各自 just-identified 并排, 互为稳健性、不分主次, 严禁把任意两臂混进同一个 over-identified 的 Hansen J 检验; 这一口径与三轨、co-primary 双轨嵌入、政治词权重梯子的处理完全一致。多重检验层面, 本家族的去重梯子属于规格稳健性并排, 镜像政治词权重与词典消融先例, 不设跨模型族际错误率模板; 真正的族际错误率控制由根级 rwolf 模板承担, 其方法学根据是 Romano & Wolf (2005) 的逐步多重检验形式化数据窥探框架, 而该模板只覆盖同一构念的替代 headline 测量如跨模型比较, 本族的去重扰动是同一测量在参数维度的稳健性而非替代测量, 故不纳入该 FWER 模板。去重梯子与其他梯子之间正交不交叉, 不做参数网格的笛卡尔积展开, 避免列爆炸与虚假自由度。

【与相邻测度的构念区分】本列与同族及邻域多个测度名近而义异, 须逐一辨明。第一, 与同族强度指数区分: 强度指数是强度累积和的对数化, 属 extensive 总量, 受报道多寡与每篇技术浓度双重驱动; 一处必须牢记的锚点更正是, 强度指数是 Fang & Peress (2009) 式的覆盖累积量, 并非 Hassan et al. (2019) 式的 intensive 归一化份额, 真正对应 Hassan 份额范式的 intensive 测度恰恰是本列与强度密度, 而非强度指数, 引用时切勿把强度指数误挂 Hassan 归一化传统。本列是纯篇数份额, 不加权强度, 一篇浅提金融科技的报道与一篇深度技术报道在分子中同权。第二, 与强度密度区分: 强度密度以强度累积和除以全部银行新闻篇数, 分子是强度而非篇数, 值域不封顶于一, 故按仓库命名规约不冠以份额之名; 本列分子分母都是篇数, 是严格意义的比例, 结构性落在零到一。第三, 与 encode 层的金融科技份额区分: 那一列的分母构造走文章银行层去重与全量减面板的另一条链路, 两列名称相近但分母口径不同, 引用时不可混写。第四, 与媒体广度类测度区分: 广度测度按 Bushee et al. (2010) 商业媒体作为信息中介的传播广度构念刻意不去重, 一条新闻被多少渠道重发本身即广度信息, 与本列的去重计数构念方向相反, 两套口径分工并存而非矛盾。第五, 与跨媒体集中度区分: 同族的集中度列是各媒体来源报道份额平方和构成的赫芬达尔指数, 虽同落零到一区间, 但度量的是曝光在渠道之间的集中程度, 高值代表集中于少数媒体而非议程份额高, 单一来源时取一, 与本列是正交的两个维度。第六, 与地理注意力指数族区分: 那一族按年、省、市三档聚合媒体邻域的金融科技曝露, 构念是银行所处媒体地理邻域的二阶曝露而非银行自身议程份额——省市两档以剔除自身的邻域聚合配曝露加权构造, 度量的是同地理单元其他银行金融科技报道对本行的溢出暴露, 与本列度量本行自身媒体议程中的金融科技占比是完全不同的因果角色, 前者常作同侪暴露或工具变量素材, 后者是本行处理变量。门控口径上两族已经对齐而非相异: 地理族的分子早前一度直读未验证全集, 但已按面板宇宙一致性审计整改, 对金融科技子集以文章与目标银行双键半连接到与本列相同的 verified 宇宙, 把未通过验证的行就地重标为非金融科技, 行数不变, 因此其分子与本列分子收敛到同一个经大模型验证的集合, 分母也同样保持未门控的全部银行新闻全集, 两族的分子门控、分母全集非对称结构完全同构, 论文样本节应按同一门控口径统一披露, 不得再表述为门控状态不同; 唯一须随行披露的边界是, 该门控在 verified 宇宙文件缺席时会响亮地放开为未门控全集, 属刻意的 fail-open 语义而非静默回退。真正的区分维度因此只剩聚合几何: 本列的分组键是银行自身乘年份, 地理族的分组键是地理单元乘年份再经邻域映射回银行, 勿因名称同含注意力而把二阶邻域曝露误作本行议程份额混用。最后须点明测度定位: 按 Da et al. (2011) 的分类, 本列连同同族计数骨架都属媒体供给侧的间接注意力代理, 度量的是媒体议程对金融科技议题的配置强度, 而非投资者主动检索的直接注意力代理如搜索量, 两类代理捕获的注意力时点与主体不同, 解读系数时须锁定间接代理定位。

【已知局限与稳健性梯子】第一, 分子的机器验证误差: 分子经大模型 full-only 门控收敛, 但验证并非无误, 假阴性即真金融科技报道被判伪会压低分子与份额, 假阳性会抬高, 且门控只认 full 轨判定, ctx 与 ss 轨的分歧不进入分子, 这是 full-only 口径的刻意取舍而非缺陷; 论文须披露有相当比例的候选文章在验证阶段被判伪剔除, 剔除比例的确切数字由引擎统计段注入而非正文手填。第二, 分母未门控的结构性不对称: 分母取自共现硬过滤后的全部银行新闻且不经验证, 若硬过滤仍放进少量误判的银行文章, 它们进入分母而不进入分子, 份额被轻微稀释, 论文样本节须披露分母是未经大模型验证的全部银行新闻。第三, 份额测度的分母驱动风险: 议程份额的变动既可能来自金融科技报道增减, 也可能来自银行总报道量的涨落, 一个金融科技报道数不变而总报道量萎缩的银行会被动录得份额上升, 解读时须对照强度指数与总篇数列交叉验证变动来源, 不可把分母收缩误读为议题热度上升。第四, 单轨 track-agnostic 的局限: 本列按篇计数, 三条文本轨在计数层坍缩为同一篇文章集合, 因此本列没有 full、ctx、ss 三轨孪生, 无法像强度指数那样以轨内替换做稳健性交叉验证, 这是计数构念的自然结果而非疏漏, 但也意味着本列的稳健性证据只能来自去重梯子而非文本轨梯子。第五, 去重梯子的方向性与近似性限制: 梯子只能向更严格方向扰动, 宽松方向在已去重语料上不可识别, 因为被生产去重删除的原文已不可恢复; 且变体是两阶段近似的保守下界, 其存活集不严格等于在原始语料上直接按该严参数去重的结果, 保留贪心的簇锚点效应使某些文章无法复活, 同时变体只在银行新闻子集上重判重, 跨子集的近似重复不可见, 这两条限定须随稳健性表脚注披露, 不可表述为从头重跑等价。第六, 媒体覆盖本身的内生性与工具的排他性代价: Fang & Peress (2009) 与 Engelberg & Parsons (2011) 表明媒体覆盖内生于企业基本面, 本列作处理变量时须靠工具变量识别, 而三类工具各有其排他性约束的脆弱处, 同侪均值面临相关冲击的威胁, Bartik 依赖份额或冲击的外生性, 来源风格依赖供给侧外生性, 论文须对每个工具的识别假设分别论证。第七, 语调维度的缺席: 本列按篇计数不含情感符号, 高份额既可能是正面转型叙事也可能是负面风险叙事, 语调维度由情感族测度另行承载, 议程份额与语调须组合解读方能定性。第八, 开发样本的诊断不可外推: 当前盘上是极小年份深度的试跑样本, 变体只追加剔除很小比例文章, 变体列与生产锚点面板内相关必然接近一, 这是低剔除率下的预期平凡结果, 不构成稳健性证据; 时间维的注意力异常与月度爆发度测度在此样本上亦不可估, 全量语料后再选择性开启。稳健性梯子的用法: 主回归以 canonical 列入模, 随后逐一以四个变体列替换复跑, 系数符号与显著性稳定即证明结论不被去重参数的研究者自由度驱动, 表格以并列形式呈现并在脚注引用两阶段近似与跨语料盲区两条限定; 每臂各自 just-identified, 禁混同一 over-identified Hansen J。

## VAR: attention_pct_full

【变体差分】本列是家族 canonical, 即生产去重口径之下的金融科技议程份额本身, 等价于去重梯子中的生产锚点臂 j80w5: 预处理已按 Jaccard 阈值零点八零与五个工作日窗完成近重去重, 本列直接在该生产存活语料上计算, 无需任何追加判重, 而四个带后缀的变体列则是在此基础上继续加严去重后重算的稳健性臂。分子是该行该年经 stage-21 验证的金融科技报道篇数, 验证口径遵循全仓 full-only 留篇门控: 只有 llm_verified_full 为真的文章才计入一篇银行金融科技报道, ctx 与 ss 轨不参与留篇判定; 具体实现是把金融科技强度帧按 docid 与 target_bank 双键与 24_herd_decay 的 verified 宇宙 inner-join, 收敛掉被大模型判伪的非真实银行金融科技文章, 再按银行乘年份计数。分母是该行该年全部银行新闻篇数, 取自 12_full 全集且保持未门控。关于列名需要澄清一处容易误读的语义: 后缀 full 并不意味着本列存在 ctx 或 ss 孪生列。本列按篇计数而非按轨强度加权, 三条文本轨在计数层坍缩为同一篇文章集合, 因此本列是 track-agnostic 的单轨测度, 家族内不产生三轨并排; 后缀的实质含义是分子的留篇判定锚定 full 轨验证结果, 与全仓门控口径一致, 同时保持与同族三轨列的命名对称。这一点与同族强度指数不同, 后者按轨强度求和, 真实存在 full、ctx、ss 三轨孪生, 三轨各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J; 本列没有那一层轨内结构, 但作为去重梯子的锚点臂, 与四个变体列之间同样适用该铁律, 生产锚点与四臂互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一个 over-identified 的 Hansen J。计数粒度需要点明: 分子帧与分母帧都以文章乘银行为行粒度, 同一篇报道若同时提及多家银行会在各家名下各计一行, 分子在门控后按银行乘年份分组计得该行该年经验证的金融科技报道条数, 分母按同键分组计得该行该年全部银行新闻条数, 二者共用同一分组键, 保证份额是同一 bank-year 内部的比例而非跨行错配。数值契约: 本列结构性落在零与一的闭区间, 分母来自真实存在银行新闻的全集脊柱故恒不小于一, 无除零; 有银行新闻但零验证金融科技报道的格点取零, 语义为真零曝光, 信息性零参与回归; 该银行该年完全无银行新闻的面板行为缺失值, 语义为不可测, 回归中被逐行删除是正确行为, 两种取值不可混同, 该契约由专门的面板超集行缺失测试锁定。解读上还须对照分母使用: 议程份额上升既可能因为金融科技报道增多, 也可能因为银行总报道量萎缩而被动抬升, 引用本列时应与同族强度指数及总篇数列交叉验证变动来源, 避免把分母收缩误读为议题热度上升。作为核心列, 本列是注意力论文 intensive 边际的 headline 测度, 与 extensive 强度指数各进各自回归、不同进一个右手边; 去重稳健性表以本列为基准列, 四个变体列逐臂替换复跑, 与本列并列呈现, 而模块日志中变体列与本列的相关性诊断是同域比较, 因为本列分子亦已经过同一 verified 门控。引用本列时的构念表述应为媒体议程中的金融科技份额, 遵循 Hassan et al. (2019) 与 Sautner et al. (2023) 的份额型暴露传统, 并按 Da et al. (2011) 的分类明确它是媒体供给侧间接注意力代理而非投资者直接注意力, 其覆盖计数骨架的资产定价合法性由 Fang & Peress (2009) 奠定。

## VAR: attention_pct_full_j70w10

【变体差分】本列是去重梯子的双向最严格臂: 近重判定的 Jaccard 阈值从生产的零点八零降到零点七零, 保留贪心时间窗从五个工作日拉长到十个工作日, 两个调谐参数同时向严格方向收紧。阈值降低意味着相似度只需达到七成即判为转载, 局部敏感哈希的候选簇随之膨胀为高阈值簇的超集; 窗口拉长意味着晚于簇锚点两个日历周之内的重发都会被删除, 慢转载与跨周末重发一并落入删除范围。因此本臂的追加剔除量在四臂中最大, 是整个梯子的扰动上界: 若主回归系数在本臂下仍保持符号与显著性稳定, 去重参数敏感性的质疑即得到最强证据; 若仅本臂失稳而单参数臂稳定, 则可进一步定位失稳来自阈值与窗口的交互而非单一参数。计算口径与家族不变量完全一致: 在生产存活语料上按本臂参数追加判重, 分子取 verified 集合与本臂存活集的交集篇数, 分母取本臂存活的全部银行新闻篇数, 分子分母同基; 存活篇数不超过生产存活篇数的单调性受校验保护。缺失与零的语义随变体全集脊柱重算: 某 bank-year 在本臂下失去全部银行新闻则整行转为缺失, 有新闻但零金融科技则取零。本臂与生产锚点及其余三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 随行披露两阶段近似保守下界与跨语料盲区两条限定, 以及试跑样本相关性接近一属预期平凡的警示, 其文献依据是 Tetlock (2011) 的陈旧信息重复定价证据。

## VAR: attention_pct_full_j70w5

【变体差分】本列是去重梯子的阈值单参数臂: Jaccard 阈值从生产的零点八零降到零点七零, 保留贪心时间窗维持生产的五个工作日不变, 从而把敏感性扰动隔离到相似度阈值这一个维度上。阈值是近重判定中研究者自由度最大的参数, 七成相似即判重会把改写幅度较大的通稿转载、编辑加工后的二次报道也并入近重簇, 而生产口径的八成阈值只捕获高度雷同的机械转载; 本臂回答的问题因此是: 如果我们对转载的定义更宽泛, 把深度改写也当作重复剔除, 银行的金融科技议程份额及其回归结论是否发生实质变化。与窗口臂对照, 本臂与它构成参数分解设计: 两个单参数臂分别隔离阈值与窗口的边际影响, 组合臂给出交互上界, 生产锚点给出基准, 五列共同构成完整的敏感性证据链。计算口径遵循家族不变量: MinHash 签名与其他臂复用同一批一次性计算的结果, 本臂只改判重阈值; 分子等于 verified 集合与本臂存活集的交集篇数, 分母等于本臂存活的全部银行新闻篇数, 分子分母同基, 存活单调性受校验。零与缺失的非对称契约随本臂全集脊柱重算, 语义与 canonical 一致。本臂与生产锚点及其余三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 论文披露遵循 Gentzkow et al. (2019) 对文本测度构造自由度须以敏感性检验约束的方法论要求。

## VAR: attention_pct_full_j75w5

【变体差分】本列是去重梯子的中间阈值臂: Jaccard 阈值取零点七五, 恰在生产口径零点八零与最激进阈值零点七零之间, 时间窗维持生产的五个工作日。本臂的设计价值在于给阈值维度补上中间格点, 使梯子在阈值方向形成三点序列: 生产锚点、本臂、激进臂。若回归系数沿该序列单调平滑地移动且始终保持符号与显著性, 说明结论对阈值选择连续稳健, 不存在某个临界阈值附近的突变; 反之, 若本臂与锚点接近而激进臂跳变, 则提示七成到七成五之间存在近重簇结构的相变, 需要回到语料层检查是哪一类文本在低阈值下被并簇, 是通稿改写还是主题雷同的独立报道被误并, 后者若被大量误删, 激进臂的份额测度反而引入向下偏误, 中间臂正是定位这一风险的探针。计算口径与家族不变量一致: 复用同一批 MinHash 签名, 仅按本臂阈值追加判重; 分子为 verified 集合与本臂存活集的交集篇数, 分母为本臂存活的全部银行新闻篇数, 分子分母同基; 存活篇数受单调性校验且理论上介于锚点与激进臂之间。零与缺失语义随本臂脊柱重算, 与 canonical 契约相同。本臂与生产锚点及其余三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 去重必要性的构念依据同样落在 Tetlock (2011) 与 Hassan et al. (2019) 的份额范式对机械重复的排斥上。

## VAR: attention_pct_full_j80w10

【变体差分】本列是去重梯子的窗口单参数臂: Jaccard 阈值维持生产的零点八零不变, 保留贪心时间窗从五个工作日拉长到十个工作日, 把敏感性扰动隔离到转载时窗这一个维度。窗口参数针对的是转载的时间结构: 生产口径假设机械转载集中发生在原发后一个工作周之内, 但中文财经媒体生态中存在慢转载现象, 周刊类媒体的滞后重发、门户网站的批量回填、以及跨长假的延迟刊发都可能落在第六到第十个工作日, 五日窗对它们无能为力, 这些漏网转载会虚增计数型测度的分子或分母。本臂把窗口拉长一倍后, 同簇内晚于已保留文章两个日历周以内的重发均被剔除, 回答的问题是: 若慢转载被更彻底地清除, 议程份额及其回归结论是否移动。因为分子分母同基重算, 慢转载若在金融科技子集与非金融科技子集中分布均匀, 份额的两侧同比例收缩、比值近似不动, 本臂的扰动预期温和; 若慢转载系统性集中于金融科技热点报道, 本臂份额将低于锚点, 这一方向性差异本身就是有价值的语料诊断。计算口径遵循家族不变量: 复用同一批 MinHash 签名, 仅改窗口参数追加判重; 分子为 verified 集合与本臂存活集的交集篇数, 分母为本臂存活银行新闻篇数; 存活单调性受校验, 零与缺失契约随本臂脊柱重算。本臂与生产锚点及其余三臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 保留贪心窗口判重的两阶段近似限定即簇锚点效应对本臂同样随行披露。

<!-- rendered-citations:begin -->
Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, Article 101670. https://doi.org/10.1016/j.jempfin.2025.101670
Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. The Quarterly Journal of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. Accounting & Finance, 64(S1), 5107-5131. https://doi.org/10.1111/acfi.13328
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. Management Science, 67(7), 4004-4031. https://doi.org/10.1287/mnsc.2020.3682
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation?. The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information?. The Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Bushee, B. J., Core, J. E., Guay, W., & Hamm, S. J. W. (2010). The role of the business press as an information intermediary. Journal of Accounting Research, 48(1), 1-19. https://doi.org/10.1111/j.1475-679X.2009.00357.x
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
<!-- rendered-citations:end -->
