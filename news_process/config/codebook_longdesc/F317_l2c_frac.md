---
family_id: F317
columns:
- frac_front_page
- frac_front_section
- frac_target_in_lead
unit: 比率/占比 (proportion ∈ [0,1] ∪ NaN; bank-year 内 article 级 0/1 指示列的均值)
formula: "frac_front_page = mean(is_front_page); frac_front_section = mean(is_front_section); frac_target_in_lead = mean(target_in_lead) — 三列均为 bank-year groupby 对 stage 11 物化的 article 级 0/1/NaN 指示列取算术均值, NaN 行自动跳过 (字段不适用不计入分母)"
producer: news_process/pipeline/filtering/news_salience.py::compute_news_salience (article 级物化, 由 stage 11 news_bank 调用) + news_process/pipeline/panel/encode.py (F3 新闻体裁显著性聚合块, agg['frac_front_page'] 等)
upstream:
- 11_bank_news.parquet (is_front_page / is_front_section / target_in_lead article 级源列)
- 21_tone_llms.parquet (留篇行宇宙, full-only 门控)
citations:
- doi: 10.1111/jofi.13287
  type: journal
  authors: Fedyk, A.
  year: 2024
  title: "Front-page news: The effect of news positioning on financial markets"
  venue: The Journal of Finance
  vol: 79
  issue: 1
  pages_or_artno: 5-33
- doi: 10.3982/QE2350
  type: journal
  authors: Hahn, J., Hughes, D. W., Kuersteiner, G., & Newey, W. K.
  year: 2024
  title: "Efficient bias correction for cross-section and panel data"
  venue: Quantitative Economics
  vol: 15
  issue: 3
  pages_or_artno: 783-816
- doi: 10.1561/104.00000112
  type: journal
  authors: Chen, A. Y., & Zimmermann, T.
  year: 2022
  title: "Open source cross-sectional asset pricing"
  venue: Critical Finance Review
  vol: 11
  issue: 2
  pages_or_artno: 207-264
- doi: 10.1093/rfs/hhy083
  type: journal
  authors: Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M.
  year: 2019
  title: "Information, trading, and volatility: Evidence from firm-specific news"
  venue: The Review of Financial Studies
  vol: 32
  issue: 3
  pages_or_artno: 992-1033
- doi: 10.1093/rfs/hhy030
  type: journal
  authors: Linnainmaa, J. T., & Roberts, M. R.
  year: 2018
  title: "The history of the cross-section of stock returns"
  venue: The Review of Financial Studies
  vol: 31
  issue: 7
  pages_or_artno: 2606-2649
- doi: 10.1093/rfs/hhv059
  type: journal
  authors: Harvey, C. R., Liu, Y., & Zhu, H.
  year: 2016
  title: "… and the cross-section of expected returns"
  venue: The Review of Financial Studies
  vol: 29
  issue: 1
  pages_or_artno: 5-68
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2008.01362.x
  type: journal
  authors: Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S.
  year: 2008
  title: "More than words: Quantifying language to measure firms' fundamentals"
  venue: The Journal of Finance
  vol: 63
  issue: 3
  pages_or_artno: 1437-1467
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1540-6261.2006.00885.x
  type: journal
  authors: Baker, M., & Wurgler, J.
  year: 2006
  title: "Investor sentiment and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 61
  issue: 4
  pages_or_artno: 1645-1680
- doi: 10.1111/0022-1082.00490
  type: journal
  authors: Diether, K. B., Malloy, C. J., & Scherbina, A.
  year: 2002
  title: "Differences of opinion and the cross section of stock returns"
  venue: The Journal of Finance
  vol: 57
  issue: 5
  pages_or_artno: 2113-2141
- doi: 10.1111/j.1540-6261.1995.tb05171.x
  type: journal
  authors: Kothari, S. P., Shanken, J., & Sloan, R. G.
  year: 1995
  title: "Another look at the cross-section of expected stock returns"
  venue: The Journal of Finance
  vol: 50
  issue: 1
  pages_or_artno: 185-224
- doi: 10.1016/j.iref.2024.04.020
  type: journal
  authors: "Yu, C., Song, A., & Yu, F."
  year: 2024
  title: "Media attention and corporate risk-taking: Evidence from China"
  venue: International Review of Economics & Finance
  one_sentence_zh: "该文以中国上市公司为样本证明媒体关注度(报道显著程度)通过信息不对称与披露质量渠道影响公司风险承担,为本家族版位与主角性显著度向银行经营和融资结果传导的移植路径提供了同一制度背景下的最新实证支持。"
- doi: "10.1111/jofi.13377"
  title: "Business News and Business Cycles"
  authors: "Bybee, L., Kelly, B., Manela, A., & Xiu, D."
  year: 2024
  venue: "The Journal of Finance"
  type: "journal"
  one_sentence_zh: "该文以80万篇华尔街日报文章的主题模型量化商业新闻的注意力分配随经济周期变化,为本家族“报道显著性反映媒体与编辑部对经济相关性判断”这一论点提供了另一维度(新闻内容主题配给而非版位配给)的最新实证参照。"
- doi: "10.3390/journalmedia5010003"
  title: "Media Output Score, a New Indicator for Measuring Online Media Coverage"
  authors: "Oliveira, U., Soares, C., & Trigo, M. R."
  year: 2023
  venue: "Journalism and Media"
  type: "journal"
  one_sentence_zh: "该文提出综合媒体能见度、favorability与读者规模的媒体产出分数以衡量品牌在线媒体覆盖强度,与本家族把版位显著性和导语主角性作为集约边际测度的思路相呼应,补充了数字媒体语境下的可见度量化视角。"
new_dois:
- 10.1111/j.1540-6261.2008.01362.x
- 10.1111/j.1540-6261.2007.01232.x
- "10.1016/j.iref.2024.04.020"
- "10.1111/jofi.13377"
- "10.3390/journalmedia5010003"
---

## CORE

【构念与来源】
本家族三列 frac_front_page、frac_front_section、frac_target_in_lead 共同刻画同一个上位构念: 新闻体裁显著性 (news salience), 即一条银行报道在报纸物理版面与文本结构中被赋予的显著程度, 以及目标银行在该报道叙事中的主角地位。其理论出发点是: 媒体对一家银行的影响力不仅取决于报道了多少条 (数量维度, 由 n_articles、attention_pct 等计数族承担), 更取决于这些报道被放在哪里、写给谁看、把谁当主角。同一条负面消息, 登在头版要闻与埋在后叠中缝, 触达的读者规模与由此引发的注意力冲击可以相差极大。Tetlock (2007) 关于媒体悲观情绪栏目影响市场的开创性研究, 其识别力量部分正来自所研究专栏在华尔街日报中的固定显著版位; Fedyk (2024) 则利用彭博终端新闻在首屏"头版"位置摆放的准随机变化, 给出了目前最干净的因果证据: 内容完全相同的新闻, 仅仅因为被放到更显著的位置, 就引发显著更强、更快的市场价格与交易量反应。这一因果事实是本家族的核心正当性来源 —— 版位不是内容的冗余包装, 而是独立于内容的注意力配给机制。与之互补, Boudoukh, Feldman, Kogan 与 Richardson (2019) 证明区分"与公司真正相关的新闻"与顺带提及的噪声报道, 能大幅提高新闻对基本面与价格的解释力, 其 relevance 与 centrality 概念直接对应本家族第三列: 目标银行是否在导语中被点名, 即该行是不是这篇报道的主角而非文末路人。Fang 与 Peress (2009) 从覆盖广度维度证明媒体覆盖本身承载定价信息 (无覆盖股票存在收益溢价), 本家族则在其"是否被覆盖"的粗放边际之上, 进一步在集约边际上度量"被怎样覆盖"。数据来源上, 三列全部取自原始语料自带的结构化字段 —— 版面、页号、作者、标题、正文 —— 这些字段在本管道早期版本中仅用于广告过滤, 从未被派生为计量特征; 2026-06-05 顶刊文本测度缺口盘点 (批次八至十) 将其激活为零成本测度族: 纯字符串与正则解析, 不调用任何 LLM 或嵌入 API, 不引入新依赖, 在 stage 11 news_bank 分类阶段逐篇物化为 article 级列, 再由 stage 40 encode 聚合为 bank-year 面板列。

【方法学与计算】
article 级构造由 news_salience.py 的 compute_news_salience 一次性完成, 分三个解析器。第一, parse_front_page 消费版面与页号两个字段: is_front_section 检查版面字符串是否命中头版、封面、要闻、头条、焦点五个高显著关键词之一; 页号经正则 (可选叠字母加前导零加页码数字, 如 A05、B2、03) 解析出叠字母与页码, page_rank 记为叠字母序乘一百加页码 (越小越靠前); is_front_page 则在 is_front_section 命中之外, 额外把"A 叠或无叠字母的第一页"计入头版, 即 is_front_page 是 is_front_section 的逻辑超集。第二, target_in_lead 判定目标银行是否出现在导语: 标题命中即记一, 否则取正文经中文分句后的前两句 (k_sentences=2) 拼接为 lead 再匹配; 匹配对象是该行全部名称变体集合 (规范行名自动并入), 且每次命中都逐 occurrence 套用与 stage 11 银行判定同款的否定词与短名排除逻辑 (has_unexcluded_occurrence, 上下文窗口五字符), 防止"光大"作普通形容、"施工行"包含"工行"这类字符串巧合被误计。此处有一个方法学上承重的修订史: 2026-06-11 之前的实现仅匹配规范行名, 实测发现由此产生的偏差完全由各银行的媒体命名惯例决定 —— 国有大行的全称规范名媒体几乎不用, 导致其导语命中被系统性低估达数倍, 且这种低估在银行间高度不均匀, 不能以"统一保守下界"辩护, 故改为全变体集匹配。第三, 缺失语义采取"字段不适用不等于不显著"公理: 版面与页号同时缺失 (典型为无版面概念的网络媒体源) 时三个版位列全记 NaN 而非零, 否则线上源占比高的银行年份会因媒体构成差异被机械拉低版位显著性, 造成混杂; encode 的 mean 聚合自动跳过 NaN, 即分母只含字段在场的报道。面板聚合层面, encode.py F3 块以 bank-year groupby 对三个 0/1/NaN 指示列取算术均值, 得到本家族三列; 聚合行宇宙与面板其他文章级测度完全一致, 受 full-only 留篇门控 (2026-06-29 口径) 约束 —— 一篇文章是否计入某银行年份的报道集合, 只看 llm_verified_full 是否为真。须特别说明本家族的轨道属性: 三列是 track-agnostic 单轨元数据测度, 不存在 _full/_ctx/_ss 三轨分身, 也没有 _lg 嵌入孪生 —— 版面位置与导语命中取决于报纸排版和记者写作结构, 与情感测度所依附的文本窗口选择 (全文、实体窗口、同句窗口) 在概念上正交, 强行分轨只会制造语义为空的重复列。这正是本项目"唯一不做双轨的类别是 track-agnostic 元数据度量"约定的典型适用。

进入面板后的工程细节还有三点值得写明。其一, encode 的聚合注册走 valid_agg 过滤: 若上游 parquet 因故缺失某个源列, 该列的聚合条目被优雅跳过而非报错, 面板中该列整列缺席 —— 消费端 (Stata 模板与 codebook) 须以列存在性探测而非硬引用处理这一优雅降级。其二, 中国报业语境给版位测度附加了一层制度含义: 在党报与主流财经报纸的编辑惯例中, 头版与要闻版的选题须经更高层级的编辑决策, 头版占比因此不仅是读者注意力的代理, 也部分反映编辑部乃至监管沟通层面对该银行新闻价值与政策相关性的判断, 论文解释系数时须对这两种机制保持并列开放而非武断归一。其三, 三列的年度均值形式意味着它们对报道总量不敏感 —— 一个只有两篇报道但其中一篇上头版的银行年份, 其 frac_front_page 高于一个有百篇报道其中十篇上头版的年份 —— 这正是集约边际测度的设计意图, 但也要求小样本年份 (留篇数极少的银行) 的取值以较大方差解读, 回归中可按留篇数加权或对低报道年份做敏感性剔除。

【文献定位】
本家族在文献谱系中处于媒体经济学"注意力配给"分支与文本资产定价"相关性过滤"分支的交汇点。注意力分支的锚点链条是: Tetlock (2007) 确立报纸内容影响市场的基准事实并隐含版位显著性的作用; Fedyk (2024) 用位置的准随机变化把"显著位置导致更强反应"从相关提升为因果; Fang 与 Peress (2009) 证明覆盖本身的存在与否已在横截面定价中留下痕迹。相关性分支的锚点是 Tetlock, Saar-Tsechansky 与 Macskassy (2008) 与 Boudoukh 等 (2019): 前者证明公司特定新闻的语言内容含有关于基本面的真实信息, 后者进一步证明只有当公司处于新闻的语义中心时这种信息含量才充分显现, 把"提及"与"主角"区分开来。行为金融维度上, Baker 与 Wurgler (2006) 的投资者情绪框架为显著性提供了传导机制: 显著位置的报道触达更广、更少专业化的读者群体, 情绪敏感型投资者的参与被放大; Diether, Malloy 与 Scherbina (2002) 关于意见分歧与横截面收益的证据则提示, 高显著性报道通过扩大异质信念持有者的接触面, 可能同时放大分歧的形成与其价格含义。本家族把这些为股票市场发展的构念移植到中国银行业的银行-年面板: 被解释对象从日频价格反应换成银行年度经营与融资结果, 显著性从事件研究的调节变量转为面板中的持续暴露强度测度。近年中国本土证据进一步强化了这一移植的制度适配性: Yu, Song 与 Yu (2024, International Review of Economics & Finance) 以中国上市公司为样本证明媒体关注度即报道显著程度通过信息不对称与披露质量渠道影响公司风险承担, 为本家族版位与主角性显著度向银行经营和融资结果传导的移植路径提供了同一制度背景下的最新实证支持。这一移植有两处非平凡的口径转换须交代。第一, 频率转换: 股票市场文献的显著性效应多在日频甚至分钟频事件窗内识别, 银行-年面板把逐篇显著性平均到年度, 度量的不再是单次冲击的瞬时强度而是该银行全年媒体呈现方式的稳态分布 —— 相应地, 理论预期从"价格对单条头版新闻反应更强"变为"常年被头版式报道的银行, 其融资成本、存款人行为与监管关注对媒体语调的敏感度系统性更高"。第二, 对象转换: 上市股票的显著性效应经由交易者注意力传导, 而中国商业银行样本中相当部分主体未上市或股权交易稀薄, 显著性的传导更多经由存款人、同业交易对手与监管者的注意力, 这使得版位与导语测度作为"公众可见度"的解释在本面板中比"交易者注意力"更准确, 也解释了为何本家族在论文组合中主要以调节与控制角色出现, 而非直接复刻资产定价文献的收益预测规格。Bybee, Kelly, Manela 与 Xiu (2024, The Journal of Finance) 以80万篇华尔街日报文章的主题模型量化商业新闻的注意力分配随经济周期变化, 为本家族"报道显著性反映媒体与编辑部对经济相关性判断"这一论点提供了另一维度即新闻内容主题配给而非版位配给的最新实证参照。Oliveira, Soares 与 Trigo (2023, Journalism and Media) 提出综合媒体能见度、favorability 与读者规模的媒体产出分数以衡量品牌在线媒体覆盖强度, 与本家族把版位显著性和导语主角性作为集约边际测度的思路相呼应, 补充了数字媒体语境下的可见度量化视角。

【识别策略定位】
在本项目的多论文组合中, 本家族的识别角色是"媒体处理强度的质量调节器"而非独立处理变量。主线各论文的 treatment 是情感与属性测度 (如 P1 的 llm_vote_tone_full), 本家族三列进入三类规格: 其一, 作为暴露强度的交互调节 —— 同样的年均语调, 头版占比高的银行年份对应更强的公众触达, 语调效应的斜率应随 frac_front_page 增大, 这一异质性预测直接由 Fedyk (2024) 的因果证据背书; 其二, 作为注意力通道的控制变量, 把"报道显著性"从"报道内容"中剥离, 防止情感系数吸收纯注意力效应; 其三, 作为 P2 注意力论文中注意力构念的物理测度臂, 与基于计数的 attention_pct 并排互证。须遵守的口径铁律: 本家族三列与同批产出的 avg_page_rank、staff_written_frac、wire_frac 等兄弟测度是并排的显著性信号族, 各自 just-identified 进入各自的回归规格, 互为稳健性、不分主次, 严禁把多个显著性测度当作同一内生变量的多工具混进同一个 over-identified 的 Hansen J 检验 —— 它们度量的是显著性构念的不同物理侧面, 排除性约束互不嵌套, 合并检验只会制造不可解释的过度识别拒绝。同理, 三列之间 (头版、版面关键词、导语) 也各走各的规格, 以规格并排而非工具堆叠的方式呈现。多测度族的统计纪律另有一层: Harvey, Liu 与 Zhu (2016) 证明金融学因子发现的海量多重检验已使传统显著性阈值失效, Linnainmaa 与 Roberts (2018) 用样本外历史数据证明大量已发表横截面关系在数据窥探之外即衰减, Chen 与 Zimmermann (2022) 则示范了以开源可复现方式约束测度族膨胀的实践标准。本家族对这三重警告的回应是: 测度构造在看到任何回归结果之前由 2026-06-05 缺口报告预先声明并冻结, 全部解析规则以源码形式公开可审计, 且论文报告中显著性族的多列结果须作为一个 family 整体呈现而非择优挑列。

【与相邻测度的构念区分】
本面板中与"媒体如何对待该银行"相关的测度族有数支, 论文须明写区分以防变量农场质疑, 此处给出构念边界。与 media_authority 加权族的区分: 后者是媒体机构级权威度 (哪家报纸说的), 本家族是同一媒体内部的版面与叙事位置 (说的时候放在哪、把谁当主角), 一条权威大报后叠的顺带提及与地方小报头版的专题报道在两族测度上取值方向相反, 二者正交。与 herd_decay 跟风衰减权重的区分: 后者刻画产出端的内容重复 (同一消息被多家转载时的信息衰减), 本家族刻画单篇报道的呈现方式, 与内容是否新鲜无关。与同批产出的署名族 (staff_written_frac、wire_frac) 的区分: 署名度量投入端原创性 (谁写的、是否通稿), 版位与导语度量产出端显著性 (登在哪、主角是谁), 一篇通讯社通稿完全可以登上头版。与 target_bank_in_title、headline_frac 等标题信号的区分: frac_target_in_lead 的判定域是标题加正文前两句的并集, 语义是倒金字塔写作规范下的"报道主角性", 比纯标题命中更宽且更贴合中文新闻的导语惯例; 标题族信号仍独立保留 (v3.8.0 删除的是标题独立情感轨, 非这些元数据信号)。与 staleness 语义陈旧度族的区分: 后者度量内容与历史报道的语义重复, 本家族对内容不做任何语义判断。与 n_articles、fintech_share 等计数份额族的区分: 计数族是粗放边际 (报道了多少), 本家族是集约边际 (报道得多显著), 二者相乘才构成完整的媒体暴露强度。

【已知局限与稳健性梯子】
第一, 版位解析的单一近似: 不同报纸的叠号语义并不统一 (某些报纸 B 叠是财经要闻而非次级版面), 本版以叠字母序乘一百加页码的统一规范化处理全部报源; 多字母叠号 (如 AII06) 按首个字母加数字序列解析, 可能被误析为后续单字母叠使 page_rank 偏大。这两点是写入论文的诚实披露项, 全量语料下的改进方向是先做各报源叠语义映射表再解析。第二, 媒体构成漂移: 尽管 NaN 语义已把无版面概念的网络源从分母中剔除, 银行年份之间"有版面字段的报道占比"本身仍可能随媒体结构变迁 (纸媒衰退) 系统性变化, 面板回归须以年份固定效应吸收共同趋势, 且解释系数时以银行内变异为主。原始语料普查显示语料以报纸类型为绝对主体, 版位字段的适用面有基本保障, 但年度间适用率漂移仍属披露项。第三, 命名惯例残差: 全变体匹配修订已消除规范名偏差的主体, 但别名词典本身的覆盖完备性仍随 config 主清单的维护质量变化, 属于测量误差而非系统偏差; 档案类数据的字段选择与留存偏误问题在资产定价文献中由 Kothari, Shanken 与 Sloan (1995) 经典地论证过, 本家族的对应风险是版面字段的留存质量与媒体数字化进程相关。第四, 短面板动态规格: 若在 T=18 的生产面板上对本家族列跑动态规格或带滞后被解释变量的模型, Nickell 型偏误不可忽略, 宜按 Hahn, Hughes, Kuersteiner 与 Newey (2024) 的高效偏差校正思路处理或改用长差分。稳健性梯子方面, 本家族自带三重互稳结构: frac_front_page 与 frac_front_section 构成宽窄二臂 (超集与关键词纯净臂), frac_target_in_lead 提供叙事维度的独立侧面, 连续型 avg_page_rank (兄弟家族) 提供二值化的敏感性对照; 三列各自 just-identified 并排进入平行规格, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J, 结论须在全族方向一致时方可声称显著性通道成立。此外还有一条与全库测度演进相关的稳定性保证: 本家族的解析规则全部作用于原始结构化字段与未经情感处理的标题正文, 不消费任何 LLM、嵌入或词典产物, 因此对情感测度层的任何换模、换词典、换嵌入空间的受控变更天然免疫, 是面板中少数在测度体系大版本迁移间逐字节稳定的列族; 唯一能改变其取值的上游变更是留篇门控口径与银行别名主清单, 二者均有独立的 gate 测试与变更台账约束。

## VAR: frac_front_page

【变体差分】
本列是 news_salience 显著性族的 canonical 头版占比列, 也是 CLAUDE.md 点名保留的显著性信号: bank-year 内 is_front_page 指示的算术均值, 度量该银行该年份全部留篇报道中登上头版或同等显著位置的比例。article 级判定是家族三列中最宽的合成口径, 由两条充分条件取逻辑或构成: 其一, 版面字段命中头版、封面、要闻、头条、焦点五个关键词之一 (即 is_front_section 命中); 其二, 页号解析为第一页且叠字母为 A 叠或无叠字母 —— 后一条捕捉的是版面字段未标注关键词、但物理上就是报纸第一页的情形, 这在版面命名不规范的地方报源中常见。因此本列相对于家族内的 frac_front_section 是严格超集: 逐篇恒有 is_front_page 大于等于 is_front_section, 聚合后 frac_front_page 恒不小于 frac_front_section, 两列之差即"纯物理首页但版面未挂要闻关键词"的报道占比, 这一差值本身有诊断价值 (衡量版面命名规范化程度)。与家族另两列的差分还体现在数据依赖上: 本列同时消费版面与页号两个字段, 任一在场即可判定 (版面命中关键词时无需页号; 页号解析成功时无需版面关键词), 仅当两字段同时缺失才记 NaN, 故其有效样本面是三列中最宽的版位列。文献定位上, 本列是 Fedyk (2024) 头版位置因果效应的面板直译 —— 该文证明同内容新闻仅因头版摆放即引发更强市场反应, 本列把这一日频事件级事实转译为银行年度的持续头版暴露强度; Tetlock (2007) 的专栏版位隐含识别与 Fang 与 Peress (2009) 的覆盖定价证据构成其上游谱系。使用口径: 本列与 frac_front_section、frac_target_in_lead 及兄弟家族的 avg_page_rank 各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 轨道属性为 track-agnostic 单轨, 无三轨分身与嵌入孪生。局限继承家族层的叠语义单一近似与多字母叠号误析两条披露, 且"A 叠或无叠第一页即头版"的规则对以 B 叠为要闻叠的个别报源会漏判, 属保守方向的测量误差。解释取值时须记住分母语义: 本列均值的分母不是该银行年份的全部留篇报道, 而是其中版面或页号字段至少一个在场的子集, 故跨银行比较隐含"版位字段适用面相近"的假设, 当两家银行的报道媒体构成差异极大 (一家以纸媒为主、一家以网络源为主) 时, 本列的可比性由 NaN 剔除机制保护但分母覆盖率本身不同, 严谨的规格宜同时报告字段在场率或以其为权重。作为家族 canonical, 本列是论文正文默认呈现的显著性主列, frac_front_section 与 frac_target_in_lead 进入稳健性附表; 但 canonical 地位是呈现约定而非统计优先级 —— 三列在识别意义上完全平权, 任何以 canonical 列显著而稳健臂不显著为由的选择性报告都违反家族的多重检验纪律。与连续型兄弟列 avg_page_rank 的搭配用法: 本列回答"是否上头版"的二值问题, page_rank 保留头版之外的全序信息 (第二版与第三十版在本列同为零, 在 page_rank 上可分), 当效应可能沿版位深度连续递减时, 二者并排能区分阈值效应与梯度效应两种机制。还须补充一处工程与经济双重含义的说明: 本列合成口径中的"物理第一页"旁路并非可有可无的技术兜底, 而是中国地方报业版面命名不规范这一制度事实的必要回应 —— 若删去该旁路仅保留关键词命中臂, 则版面标注习惯较松的地方性报源会被系统性判为非头版, 而这类报源恰恰在城商行、农商行等区域性银行的报道构成中占比更高, 于是会引入与银行类型高度相关的选择性测量误差, 使头版占比在国有大行与区域行之间的比较失去可比性。保留旁路以叠字母加页码的统一规范化换取跨报源的判据一致, 是"宁可承担叠语义近似误差, 也要避免与被解释单位特征相关的系统性漏判"这一取舍的落地。相应地, 论文若以本列做区域行与大行的异质性比较, 应同时报告 frac_front_section 纯净臂结果作为该旁路是否驱动结论的稳健性对照; 两臂方向一致时, 头版暴露的经济解释才稳固成立, 这也是本列与其纯净臂在同一家族内并排存在的识别意义所在。

## VAR: frac_front_section

【变体差分】
本列是家族版位二臂中的关键词纯净臂: bank-year 内 is_front_section 指示的均值, article 级判定仅看版面字段字符串是否命中头版、封面、要闻、头条、焦点五个高显著关键词之一, 完全不使用页号信息。与 canonical 列 frac_front_page 的精确差分在于判据的收窄方向与语义纯度的取舍: frac_front_page 为覆盖版面命名不规范的报源而纳入"物理第一页"旁路, 代价是把叠号解析的全部近似误差 (统一叠语义假设、多字母叠号误析) 引入判定; 本列则以牺牲覆盖面为代价换取判据的可解释纯净 —— 命中即意味着报纸编辑在版面命名上显式地把该版标记为要闻级, 是编辑部显著性配给决策的直接文字证据, 不经任何数值解析与规范化假设。因此两列构成一对宽窄互稳臂: 若某一效应仅在宽口径下显著而纯净臂方向翻转, 则结果可能由页号解析噪声驱动; 若两臂方向一致而幅度随口径收窄递增, 则符合"关键词命中版位更显著"的剂量反应解释。缺失语义与家族公理一致: 版面与页号同时缺失记 NaN, 分母仅含字段在场报道; 但须注意本列的一个细节 —— 版面字段缺失而页号在场时, is_front_section 记零而非 NaN (页号在场证明版位字段体系适用, 版面未标关键词是真信号), 这与两字段全缺的 NaN 情形不同。文献锚点上, 本列对应 Tetlock (2007) 谱系中"栏目与版面身份"的显著性维度: 该文的媒体情绪度量之所以有市场影响力, 前提是其所在专栏具有稳定的要闻级版面身份, 本列把这种版面身份的编辑标注转为可聚合的面板测度; Boudoukh 等 (2019) 关于新闻分类质量决定信息含量的一般教训, 在此体现为对判据纯净度的偏好。使用口径与家族铁律相同: 与 frac_front_page、frac_target_in_lead 各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; track-agnostic 单轨, 无 full/ctx/ss 分身。局限: 五关键词表为人工枚举而非穷举, 未命中不等于非要闻 (个别报纸用"重点"等未入表词), 该词表冻结于源码常量, 任何扩充须走受控变更以保持跨年可比。与 canonical 列的量化关系可用作内建一致性诊断: 由判据的超集结构, 面板上每个 bank-year 格恒有本列取值不大于 frac_front_page (在两列分母一致的格上严格成立; 当版面缺失而页号在场的报道存在时两列分母不同, 不等式在均值层面仍近似保持), 若消费端观察到反向格, 优先怀疑上游字段解析回归而非经济现象。使用建议上, 本列最适合作为 frac_front_page 结论的判据纯净度检验臂: 当研究者担心页号旁路引入的解析噪声与银行特征相关 (例如大银行更多被全国性大报报道、而大报页号体系更规范) 时, 以本列替换主列重跑同一规格, 系数稳定即可排除该混杂路径; 反之若仅主列显著, 则须补充报告两列分母差异与页号旁路命中率的分解, 说明差异来自覆盖面而非噪声。本列的年度均值同样对报道总量不敏感, 小留篇数年份高方差的解读约束与家族层一致; 其与 frac_target_in_lead 的相关性预期为弱正 (要闻版报道更可能以目标行为主角), 但两者构念正交, 回归中同时进入不构成共线问题。

## VAR: frac_target_in_lead

【变体差分】
本列是家族内唯一的叙事结构测度, 与两个版位列的物理显著性维度正交: bank-year 内 target_in_lead 指示的均值, 度量该银行在其留篇报道中以"导语主角"身份出现的比例。article 级判定遵循中文新闻的倒金字塔写作规范: 标题命中目标银行任一名称变体即记一; 否则对正文做中文分句, 取前两句 (k_sentences=2) 拼接为导语再匹配, 命中记一, 否则记零; 银行名缺失记 NaN。判定的精确性依赖两层与 stage 11 银行识别完全同源的防误报机制: 匹配集是该行全部名称变体 (规范行名自动并入, 修复前仅匹配规范名导致的命名惯例偏差见家族层方法学段), 且每个命中位置逐 occurrence 套用否定词与短名排除 (上下文窗口五字符), 与共现过滤的银行侧口径保持"否定加短名过滤"的同一判定不对称原则。构念上本列直译 Boudoukh, Feldman, Kogan 与 Richardson (2019) 的 relevance 与 centrality: 该文证明只有当公司处于新闻语义中心时, 新闻的量价解释力才充分显现, 顺带提及的报道近于噪声; 倒金字塔规范保证记者把最重要的主体与事实压进标题与首两句, 故导语命中是"本行是这篇报道的主角"的低成本高效度代理, Tetlock, Saar-Tsechansky 与 Macskassy (2008) 关于公司特定新闻语言承载基本面信息的证据是其上游前提 —— 主角性正是"公司特定"程度的操作化。与相邻信号的差分: 与 target_bank_in_title 的区别是判定域从纯标题扩为标题加首两句并集, 对标题惜字如金、主体后置到导语首句的中文财经报道更稳健; 与版位两列的区别是维度正交 —— 一篇头版报道可以只在文末顺带提及某行 (版位高、主角性低), 一篇后叠深度专访可以通篇以某行为主角 (版位低、主角性高), 两维度的交互项在异质性规格中有独立解释价值。使用口径: 与两版位列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; track-agnostic 单轨 —— 尤须强调其判定窗口 (正文前两句) 与情感三轨的 ss 同句窗口是完全不同的原语与口径, 禁互相复用或混淆。局限: 前两句的句读依赖中文分句器对不规范标点的容错, 电头 (如通讯社发稿头) 占据首句时会挤占导语窗口, 属向下的测量误差; 别名词典覆盖完备性随主清单维护质量变化, 继承家族层披露。与版位两列相比本列还有一处数据依赖上的重要差分: 它完全不消费版面与页号字段, 只依赖标题、正文与银行名, 因此对网络媒体源同样适用, 是家族三列中唯一没有"字段不适用"NaN 情形的列 (仅银行名缺失才 NaN), 其分母近似等于该银行年份的全部留篇报道, 跨媒体构成的可比性天然优于版位列 —— 当研究者需要一个对纸媒衰退趋势稳健的显著性测度时, 本列是首选臂。窗口参数 k_sentences=2 与排除逻辑的上下文窗口五字符均为源码冻结常量, 前者对应中文消息体裁"首句导语加次句展开"的标准结构, 加宽窗口会稀释主角性语义使测度向普通提及率退化, 收窄为纯首句则对电头与分句噪声过敏, 二为居中取值; 若未来需要窗口敏感性梯子, 须按项目梯子铁律以并排新列而非改动本列的方式扩展, 保持本列跨版本逐字节稳定。修订史对使用者的提醒: 全变体匹配修复属语义修正而非参数调整, 修复前后的取值不可比, 任何引用历史面板快照的复现工作须确认快照生成于修复之后。

<!-- rendered-citations:begin -->
Fedyk, A. (2024). Front-page news: The effect of news positioning on financial markets. The Journal of Finance, 79(1), 5-33. https://doi.org/10.1111/jofi.13287
Hahn, J., Hughes, D. W., Kuersteiner, G., & Newey, W. K. (2024). Efficient bias correction for cross-section and panel data. Quantitative Economics, 15(3), 783-816. https://doi.org/10.3982/QE2350
Chen, A. Y., & Zimmermann, T. (2022). Open source cross-sectional asset pricing. Critical Finance Review, 11(2), 207-264. https://doi.org/10.1561/104.00000112
Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. The Review of Financial Studies, 32(3), 992-1033. https://doi.org/10.1093/rfs/hhy083
Linnainmaa, J. T., & Roberts, M. R. (2018). The history of the cross-section of stock returns. The Review of Financial Studies, 31(7), 2606-2649. https://doi.org/10.1093/rfs/hhy030
Harvey, C. R., Liu, Y., & Zhu, H. (2016). … and the cross-section of expected returns. The Review of Financial Studies, 29(1), 5-68. https://doi.org/10.1093/rfs/hhv059
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Baker, M., & Wurgler, J. (2006). Investor sentiment and the cross-section of stock returns. The Journal of Finance, 61(4), 1645-1680. https://doi.org/10.1111/j.1540-6261.2006.00885.x
Diether, K. B., Malloy, C. J., & Scherbina, A. (2002). Differences of opinion and the cross section of stock returns. The Journal of Finance, 57(5), 2113-2141. https://doi.org/10.1111/0022-1082.00490
Kothari, S. P., Shanken, J., & Sloan, R. G. (1995). Another look at the cross-section of expected stock returns. The Journal of Finance, 50(1), 185-224. https://doi.org/10.1111/j.1540-6261.1995.tb05171.x
Yu, C., Song, A., & Yu, F. (2024). Media attention and corporate risk-taking: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.04.020
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business News and Business Cycles. The Journal of Finance. https://doi.org/10.1111/jofi.13377
Oliveira, U., Soares, C., & Trigo, M. R. (2023). Media Output Score, a New Indicator for Measuring Online Media Coverage. Journalism and Media. https://doi.org/10.3390/journalmedia5010003
<!-- rendered-citations:end -->
