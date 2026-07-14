---
family_id: F312
columns:
- fintech_intensity_mean
- fintech_share
unit: fintech_share = 份额比率 ∈ [0,1] (无量纲); fintech_intensity_mean = 连续技术强度得分 (无量纲, 双重对数标尺)
formula: "fintech_share = ft_n_articles_dedup / (ft_n_articles_dedup + nf_n_articles), 分子分母同按 (target_bank, 标题, 日期) 复合键去重同基, 分母为零 → NaN 并配套 zero_coverage 指示; fintech_intensity_mean = 银行-年内 fintech_intensity_score 的均值, 文章级 Score_d = 对满足 TF(d,i)>0 的金科词 i 求和 [(1 + ln TF(d,i)) / (1 + ln L_d)] × W_i, 其中 W_i = IDF_i × CosSim_scaled_i, TF(d,i) 为词 i 在文档 d 的词频, L_d 为文档长度, 聚合域 = semi-join 24_herd_decay 的 LLM-verified 集"
producer: pipeline/falsification/controls.py::build_non_fintech + merge_to_panel (fintech_share) ; pipeline/filtering/fintech_intensity.py (文章级 fintech_intensity_score) + pipeline/panel/runner.py (bank-year 聚合 fintech_intensity_mean)
upstream:
- 12_fintech_news_full.parquet (过滤前全量银行新闻, 与 11_bank_news 逐行 1:1, 含 is_fintech_news 标注)
- 40_article_bank_level.parquet (已进面板的金融科技文章)
- 40_panel_yearly.parquet (bank-year 面板骨架)
- 15_fintech_intensity.parquet (文章级技术强度得分)
- 24_herd_decay.parquet (LLM-verified 聚合域锚)
citations:
- doi: 10.1002/ijfe.3105
  type: journal
  authors: Liu, J., Chen, S., Su, F., & Liu, J.
  year: 2025
  title: "Digital transformation disclosure and bank loans: An information heterogeneity perspective"
  venue: International Journal of Finance & Economics
  vol: 30
  issue: 4
  pages_or_artno: 4004-4038
- doi: 10.1016/j.ribaf.2024.102613
  type: journal
  authors: Liu, H., & Hu, J.
  year: 2025
  title: "Bank Fintech and firm leverage adjustment speed: Evidence from China"
  venue: Research in International Business and Finance
  vol: 73
  pages_or_artno: 102613
- doi: 10.1080/1351847X.2025.2468481
  type: journal
  authors: Li, T., Stasinakis, C., Yeo, W. M., & Da Silva Fernandes, F.
  year: 2025
  title: "Fintech, financial development and banking efficiency: Evidence from Chinese commercial banks"
  venue: The European Journal of Finance
  vol: 31
  issue: 10
  pages_or_artno: 1245-1295
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2618-2646
- doi: 10.1016/j.pacfin.2024.102276
  type: journal
  authors: Liu, S., Wang, B., & Zhang, Q.
  year: 2024
  title: "Fintech regulation and bank liquidity creation: Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 84
  pages_or_artno: 102276
- doi: 10.1016/j.econmod.2023.106445
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: "Bank fintech, liquidity creation, and risk-taking: Evidence from China"
  venue: Economic Modelling
  vol: 127
  pages_or_artno: 106445
- doi: 10.1016/j.jfs.2020.100836
  type: journal
  authors: Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L.
  year: 2021
  title: "Fintech: What's old, what's new?"
  venue: Journal of Financial Stability
  vol: 53
  pages_or_artno: 100836
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: International Review of Economics & Finance
  vol: 74
  pages_or_artno: 468-483
- doi: 10.1080/1351847x.2020.1805782
  type: journal
  authors: Wang, R., Liu, J., & Luo, H.
  year: 2021
  title: "Fintech development and bank risk taking in China"
  venue: The European Journal of Finance
  vol: 27
  issue: 4-5
  pages_or_artno: 397-418
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1016/j.jfi.2019.100833
  type: journal
  authors: Thakor, A. V.
  year: 2020
  title: "Fintech and banking: What do we know?"
  venue: Journal of Financial Intermediation
  vol: 41
  pages_or_artno: 100833
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: Cheng, M., & Qu, Y.
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 63
  pages_or_artno: 101398
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: Journal of Business Economics
  vol: 87
  issue: 5
  pages_or_artno: 537-580
- doi: "10.1016/j.ememar.2024.101237"
  title: "FinTech: The disruptive force reducing bank competition pressure"
  authors: "Zhang, X., & Li, Z."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
- doi: "10.1080/23322039.2023.2267270"
  title: "Does financial inclusion moderate the effect of digital transformation on banks' performance in China?"
  authors: "Yang, F., & Masron, T. A."
  year: 2023
  venue: "Cogent Economics & Finance"
  type: "journal"
- doi: "10.1080/13602381.2024.2434010"
  title: "Beyond binary: exploring the interplay of China's digital transformation and firm performance through dual mechanism analysis"
  authors: "Chen, S., Alexiou, C., & Lee, S."
  year: 2024
  venue: "Asia Pacific Business Review"
  type: "journal"
new_dois:
- 10.1093/rfs/hhaa079
- 10.1093/qje/qjz021
- "10.1016/j.ememar.2024.101237"
- "10.1080/23322039.2023.2267270"
- "10.1080/13602381.2024.2434010"
---

## CORE

【构念与来源】
本家族 (家族键 l2c_fintech) 承载 bank-year 面板上刻画银行媒体形象之金融科技属性的两个互补测度: fintech_share 度量金融科技报道在该银行全部媒体报道中的相对占比 (广延边际, extensive margin), fintech_intensity_mean 度量已判定为金融科技报道的文章在技术内容上的平均含金量 (集约边际, intensive margin)。二者共同回答一个在银行数字化实证文献里反复出现、却常被单一计数变量粗暴合并的问题: 一家银行在公共信息环境中被感知为金融科技参与者, 究竟是因为金融科技话题在其媒体叙事中占据了多大的份额, 还是因为那些金融科技报道本身谈得有多深、多技术化。构念的理论出发点是 Gomber et al. (2017) 对数字金融与金融科技研究疆域的系统划界与 Thakor (2020) 对金融科技与银行业关系的综述框架: 金融科技不是一个二元的有或无, 而是沿采纳广度与技术深度两个维度连续分布的银行特征。Boot et al. (2021) 进一步指出金融科技浪潮中信息与沟通渠道的变化才是相对于历史金融创新的真正新颖之处, 这为用媒体文本 (而非专利、财报或 App 下载量) 来测度银行金融科技暴露提供了概念正当性: 媒体报道是银行技术战略被外部利益相关者观察、解读与定价的一手信息界面。在中国场景下, 以文本挖掘构造银行金融科技指数已是成熟惯例: Cheng and Qu (2020) 用文本词频构造银行金融科技指数并考察信用风险, Wang et al. (2021) 与 Lee et al. (2021) 分别把类似指数用于银行风险承担与效率, Fang et al. (2023) 与 Liu et al. (2024) 将其延伸到流动性创造与监管互动, Liu and Hu (2025) 用于企业杠杆调整速度, Li et al. (2025) 在构造银行数字化测度时同样依赖文本挖掘惯例。本家族与这一支文献同构念、同数据介质, 但在两处刻意更进一步: 其一, 份额测度显式借用 Hassan et al. (2019) 的 PRisk 对 NPRisk 相对占比范式, 把绝对计数转换为同一计数域内的相对份额, 剥离银行规模与媒体总曝光的机械混杂; 其二, 强度测度借用 Li et al. (2021) 以机器学习嵌入度量企业文化的思路, 用语义加权词频代替裸词频, 使得分反映技术话语的区分度而非篇幅或复读。

【方法学与计算】
fintech_share 由 falsification 阶段的 controls 模块生产, 计算链条分三步。第一步构造对照组: 以过滤前全量银行新闻底库 (该文件与上游银行新闻分类输出逐行一比一, 命名虽带 fintech 字样但实为全量底库, 额外携带金融科技标注列以便把对照组细分为关键词未匹配与匹配但被大模型拒绝两类) 减去已进入面板的金融科技文章, 得到非金融科技银行新闻集合; 减法用 anti-join 实现, 复合键为目标银行、标题与日期三元组, 且两侧先各自按该键去重再取集合差, 这一互补划分直接对标 Hassan et al. (2019) 对政治风险与非政治风险语料的处理。第二步分别聚合: 非金融科技侧按银行乘年份数出去重稿件数, 金融科技侧同样以相同复合键去重后数出去重篇数并经数据框属性通道传递给合并函数。第三步在面板上构造份额: 分子为去重金融科技篇数, 分母为去重金融科技篇数与去重非金融科技篇数之和, 即同一把尺子数出的全部银行新闻; 分母为零 (该银行该年全年零新闻) 时份额在数学上是零比零, 记为缺失而非零, 并配套 zero_coverage 指示列标记这些无定义行, 避免把未定义份额与有新闻但全为非金融科技的真实零份额混为一谈。计数基统一是该测度的命门: 早期实现曾用面板物理篇数 (同一稿件被多家媒体转载计多篇) 作分子、去重稿件数作分母, 份额被系统性抬高; 现行口径经两轮修复后分子分母份额弹性对全部统一到去重基, 仅当去重聚合不可用时才回退到物理加去重的混合基并在注释中如实披露, 且运行时逐行校验去重金融科技计数不超过物理篇数。fintech_intensity_mean 的计算分文章级与聚合级两层。文章级得分在金融科技强度阶段生产: 对每篇经邻近共现硬过滤后的金融科技文章, 在标题拼接正文的全文轨文本上统计约一千五百个金融科技词表词的词频, 按双重对数核公式打分, 即对每个出现的关键词取一加词频对数、除以一加文档长度对数、再乘以该词权重后求和; 权重为逆文档频率乘以经缩放的语义纯度余弦相似度, 后者来自关键词嵌入向量与逆文档频率加权词表质心的余弦, 嵌入走统一引擎的双 API 模型。对数词频压制复读机刷分, 长度对数分母消除长文体量偏差, 逆文档频率与语义纯度权重恢复术语区分度, 三者分别针对文本测度文献里三类已知系统偏差。文中出现的不同关键词数低于最小阈值 (默认两个) 时得分记缺失且验证标记置否, 使未验证文章在下游均值中被自动剔除而不是被当作零强度拉低均值。聚合级在面板 runner 中完成: 年份从日期列现场派生, 随后关键的一步是把文章集合半连接到羊群衰减阶段所代表的大模型已验证宇宙 — 强度阶段的输出基于规则预筛候选集, 含相当比例经语义验证被否决的假阳性文章, 若不收敛聚合域, 这些文章会污染 bank-year 均值并制造幽灵银行年; 半连接后按银行乘年份对文章级得分取算术平均得到 fintech_intensity_mean。用白话说, 这两个量的分工是: 份额回答这家银行的新闻里有多大比例在谈金融科技, 强度均值回答那些谈金融科技的新闻平均谈得有多专业 — 前者数篇数算比例, 关键是分子分母用同一把尺子数; 后者给每篇文章打一个技术含金量分再取平均, 关键是打分时既不让长文占便宜、也不让把同一个词复读一百遍的稿子刷高分、还要让真正有区分度的专业术语比人人都在用的泛化词权重更高。两个量各自的坑也不同: 份额的坑在计数口径与零的语义, 强度的坑在词表权重的退化与聚合宇宙的污染, 上文的实现细节即分别针对这两组坑设防。

【文献定位】
在方法谱系上, 本家族坐落于三支文献的交汇处。第一支是文本测度方法学: Hassan et al. (2019) 确立了从会议纪要文本构造企业层面暴露份额的范式, 其核心纪律 — 分子分母必须在同一计数域内、份额而非水平才能剥离总量混杂 — 被 fintech_share 逐条继承; Li et al. (2021) 则示范了如何用词嵌入把词典法从二元匹配升级为连续语义加权, fintech_intensity_mean 的逆文档频率乘余弦权重正是这一路线在金融科技词表上的实现。第二支是银行金融科技实证: 中国样本上的主流做法是把新闻或年报中金融科技词频加总为指数再进入银行结果回归, Cheng and Qu (2020)、Wang et al. (2021)、Lee et al. (2021)、Fang et al. (2023)、Liu et al. (2024)、Liu and Hu (2025) 构成从信用风险、风险承担、效率到流动性创造与杠杆传导的完整结果谱; 本家族相对于该谱系的增量在于把计数指数拆解为份额与强度两个语义正交的分量, 并对计数基、缺失语义与聚合域这三个在既有文献中普遍未披露的实现细节给出可审计口径。第三支是数字能力与信息披露: Kwan et al. (2024) 用外生冲击检验银行数字能力的真实价值, Liu et al. (2025) 从信息异质性角度考察数字化披露对银行信贷的影响, 二者共同说明外部可观察的数字化信号 (无论来自压力测试还是披露文本) 具有经济实质; 媒体报道份额与强度作为第三方生成的数字化信号, 与自愿披露互为镜像, 天然规避了披露操纵的内生性来源之一。Li et al. (2025) 关于文本挖掘构造银行数字化测度的做法进一步佐证本家族在构造惯例上处于该文献的常规做法区间之内。Zhang and Li (2025, Emerging Markets Review) 用中国二百七十六家银行二零一一至二零二二年新闻文本构造银行层面金融科技指数并考察其对银行间竞争压力的缓解效应, 与本家族以媒体报道文本构造银行金融科技份额与强度测度的方法学路径高度同构, 可作为文献定位段的最新佐证。Yang and Masron (2023, Cogent Economics & Finance) 考察金融普惠对中国银行数字化转型与经营绩效关系的调节效应, 采用文本挖掘构造银行数字化转型指数, 与本家族以媒体文本构造银行金融科技暴露测度的方法学路径同构。Chen, Alexiou and Lee (2024, Asia Pacific Business Review) 用双重机制分析考察中国企业数字化转型对绩效的非线性影响, 呼应本家族份额与强度两分量拆解广延/集约边际的构念设计思路。

【识别策略定位】
本家族两列在识别设计中承担双重角色。其一是伪造检验 (falsification) 的核心构件: fintech_share 所在的阶段本身就是为主线语调结论设计的打假对照实验, 假设框架为零假设 (金融科技语调的解释力完全来自一般媒体关注度) 对备择假设 (语调含金融科技特异性增量信息) 的赛马 — 把金融科技语调与非金融科技新闻覆盖量同时放进回归, 若控制一般关注度后语调依然显著, 则语调携带的确是金融科技维度的独特信息而非新闻多的副产品, 这正是 Hassan et al. (2019) 用总体风险暴露对政治风险暴露做区分效力检验的移植。配套诊断包括情感测度与非金融科技覆盖的相关矩阵 (弱相关支持备择假设) 与金融科技对非金融科技对数篇数的挤出弹性检测 (排除份额分子分母的机械负相关)。其二是处理强度的连续刻画: 相对于二元的是否有金融科技报道, fintech_share 提供银行间与银行内跨年的连续变异, fintech_intensity_mean 提供条件于有报道之后的深度变异, 二者可分别作为处理变量的稳健性替身或调节维度进入各论文规格。需要强调的聚合域纪律: fintech_intensity_mean 的聚合域已收敛到大模型验证宇宙, 与面板其余文本测度同域, 而留篇门控自二零二六年六月末起为 full-only 口径 — 一篇文章是否算作银行金融科技报道只看全文轨验证标记; fintech_share 的分子基集 (已进面板文章) 同受该门控约束, 因此换嵌入或改门控口径都会机械改变本家族取值, 属预期数值副作用而非缺陷, manuscript 披露时应说明。

【与相邻测度的构念区分】
与 n_articles 及注意力族 (attention_pct 等) 的区分: 那些列度量媒体曝光的绝对水平或跨行排名, 本家族的份额列度量的是构成 — 同样一百篇报道, 九成谈金融科技与一成谈金融科技的银行在 n_articles 上无差别, 在 fintech_share 上天壤之别; 份额天然对银行规模与媒体总盘子的时序波动免疫, 这正是引入它的动机。与 ln_ft_articles 及 ln_nf_articles 挤出弹性对的区分: 弹性对保留两侧水平信息用于检测机械挤出, 份额把两侧压缩为单一相对量, 二者由同一去重基派生但服务于不同诊断。与 policy 对齐族 (article_sim_mean 等) 的区分: 政策对齐度量文章语义与政策文本锚点的余弦贴近度, 强度均值度量文章内部金融科技术语的密度与区分度, 两者虽同出强度阶段的输出文件且同受验证宇宙半连接约束, 构念上一个朝向外部政策坐标、一个朝向内部技术话语。与情感三法 (词典、大模型、BERT) 的区分: 情感度量报道的方向与色彩, 本家族度量报道的话题构成与深度, 在回归中前者是处理变量主轨、后者常作控制或伪造对照。与文章级三轨强度列族的区分: 强度阶段在文章级并列产出全文轨、实体窗口轨、同句共现轨三轨得分及 text-embedding-3-large 的 lg 孪生族, 面板层另有对应聚合列; 本家族的 fintech_intensity_mean 是无后缀 canonical 槽, 语义等于全文轨主模型均值, 与其余轨道及孪生列互为稳健性、不分主次。

【已知局限与稳健性梯子】
第一, 去重键的粒度局限: 以银行、标题、日期三元组判同稿件, 对标题微改的转载稿会漏去重, 对同日同题的真实两稿会误合并; 该键是在无全文指纹条件下的务实选择, 方向性影响是份额的分子分母同受影响故偏差部分相消。第二, 对照组构造依赖上游分类质量: anti-join 的减数是已进面板文章, 若大模型验证存在系统性漏检, 漏检篇会滞留在非金融科技侧同时抬高分母压低份额; 阶段内建的分类一致性收敛效度诊断与别名匹配质量诊断即为监测此风险而设。第三, 混合基回退: 去重聚合属性缺席时总量退回物理加去重的混合基, 该路径仅为向后兼容旧调用与测试保留, 生产口径不应触发, 触发即在日志如实披露。第四, 强度得分的退化守卫: 文档频率为空、逆文档频率均值非正、余弦全同等数据退化路径会把语义加权降级为纯词频或纯逆文档频率并以错误级日志披露, 嵌入 API 硬失败则不降级而走 both-or-neither — 主模型族与 lg 族得分同置缺失, 绝不留单边孤儿列; 降级态数值不可用于发表对比。第五, 稳健性梯子与口径铁律: 强度测度沿三个正交维度铺设梯子 — 文本轨道 (全文、实体窗口、同句共现三轨, 同句轨在无银行与金融科技同句共现时回退镜像实体窗口轨语义即回退为全文正文并置回退标记)、嵌入模型 (canonical 主模型与 lg 大模型 co-primary 双轨, 严格列名双射、同损同有)、验证门控 (full-only 留篇门控下的验证宇宙)。凡此三轨、co-primary 双轨及任何梯子变体, 铁律是各自 just-identified 并排、互为稳健性、不分主次, 禁止把不同轨道或不同模型的测度混进同一 over-identified 的 Hansen J 检验 — 它们是同一构念的替代测量而非相互独立的工具变量, 混用会使过度识别检验在构造上自相关而失效。第六, 缺失语义纪律: 份额的分母为零记缺失、强度的单篇不足最小关键词数记缺失、聚合后无数据记缺失, 全家族遵循无数据即未测量的契约, 任何环节不得以零冒充缺失; 使用者在回归中应让缺失自然剔除, 并可用 zero_coverage 指示列做条件化或样本敏感性分析。第七, 外部效度边界: 本家族两列均以媒体报道为信息介质, 度量的是被公共信息环境感知的金融科技暴露, 而非银行内部真实的技术投入; 若研究问题关注真实投入 (系统采购、研发支出、专利), 应以本家族为感知侧代理并与投入侧数据交叉验证, Kwan et al. (2024) 用疫情冲击下的实际业务连续性检验数字能力真伪的思路可作为这类交叉验证的模板。第八, 语料代表性: 上游语料按媒体类型只保留报纸报道, 通讯社、杂志、政府与网页类来源按行剔除, 份额与强度的解释均应限定在报纸媒体口径内; 报纸对金融科技话题的选题偏好若随年份漂移, 会同时进入分子分母, 份额设计对这类共同漂移部分免疫, 但强度均值不具备该免疫性, 跨年比较强度时宜辅以年份固定效应吸收语料层漂移。

## VAR: fintech_intensity_mean

【变体差分】
本列 tier 为 standard, 是家族强度维度的 bank-year 聚合代表: 对该银行该年所有进入验证宇宙的金融科技文章, 取文章级 fintech_intensity_score 的算术平均。差分要点有四。其一, 轨道: 本列聚合的是无后缀文章级得分, 即全文轨 (标题前置拼接正文) 的 canonical 别名; 实体窗口轨与同句共现轨的文章级孪生列及 text-embedding-3-large 的 lg 孪生族不在本列内, 各自另聚合为带后缀的面板列, 与本列互为稳健性、不分主次、各自 just-identified 并排, 禁混同一 over-identified Hansen J。其二, 模型: 关键词语义纯度权重来自 canonical 嵌入槽的主模型, 质心与余弦数学全程维度无关; 嵌入硬失败时依 both-or-neither 契约与 lg 族同置缺失。其三, 聚合域: 经半连接收敛到羊群衰减阶段代表的大模型验证宇宙, 与面板其余文本测度同域; 修复前本列曾在规则预筛全集上聚合, 假阳性文章污染均值并制造幽灵银行年, 现行口径已消除该结构性不一致。其四, 缺失语义: 单篇文章不同关键词数低于最小阈值时得分为缺失且不进入均值分母; 某银行年无任何验证文章时本列缺失而非零, 与家族无数据即未测量契约一致。年份由日期列在聚合时现场派生, 上游文章级文件不携带年份列。使用建议: 本列刻画条件于有金融科技报道之后的技术深度, 与 fintech_share 的构成占比正交, 二者同入回归时分别吸收集约与广延边际。

## VAR: fintech_share

【变体差分】
本列 tier 为 core, 是家族乃至全仓的全局 headline 份额测度: 该银行该年金融科技报道占其全部银行新闻的比例, 落在零到一闭区间。区别于家族强度列与仓内计数列的精确语义如下。第一, 计数基: 分子为去重金融科技篇数 (已进面板文章按银行、标题、日期复合键去重后计数), 分母为该去重分子加上同键去重的非金融科技稿件数, 分子分母严格同基 — 这是对 Hassan et al. (2019) 份额范式中同一计数域要求的逐字执行; 早期物理分子对去重分母的混基口径已被修复取代, 现行代码仅在去重聚合不可用的向后兼容路径上才回退混合基并如实披露。第二, 对照组来源: 分母的非金融科技侧由过滤前全量银行新闻底库 anti-join 已进面板文章得到, 底库与银行新闻分类输出逐行一比一且携带金融科技标注列, 使对照组可细分为关键词未匹配与匹配但被大模型否决两类, 供收敛效度诊断。第三, 缺失与零的语义分野: 分母为零 (全年零新闻) 时本列为缺失并由 zero_coverage 指示列标记, 真实零 (有新闻但全为非金融科技) 才取零值; 回归中缺失自然剔除, 使用者不得以零填充。第四, 门控一致性: 分子基集是经 full-only 留篇门控 (只看全文轨大模型验证标记) 进入面板的文章集合, 因此本列取值随门控口径与嵌入换代而机械变动, 属预期数值副作用, 与 n_articles 等同源列的收缩同理, 披露时须说明厂商与门控维度。第五, 无轨道与模型后缀: 本列是计数构成量而非语义嵌入量, 不存在实体窗口轨、同句轨或 lg 孪生 — 它属于非嵌入 carve-out, 份额本身没有嵌入模型可换; 其稳健性梯子体现在与 ln_ft_articles 及 ln_nf_articles 弹性对、all_ln_coverage 总覆盖以及 fintech_intensity_mean 强度维度的并排规格上, 各规格互为稳健性、不分主次、各自 just-identified 并排, 禁混同一 over-identified Hansen J。第六, 识别角色: 本列既是伪造检验赛马中剥离一般媒体关注度的构成量, 也是主线论文里银行金融科技媒体暴露的连续处理强度替身; 相对占比设计使其对银行规模、媒体总盘子扩张及语料年度密度波动免疫, 这是它取代绝对计数成为 headline 测度的根本理由。跨源一致性校验 (去重金融科技计数逐行不超过物理篇数) 与挤出弹性三档阈值诊断为本列的数据质量提供运行时防线: 弹性诊断把金融科技对数篇数与非金融科技对数篇数的相关系数分为机械约束、中等负相关与非机械关联三档, 用以排除份额变异只是分子分母此消彼长的会计恒等式的可能。第七, 解释方向的白话提示: 本列上升可能来自分子增加 (金融科技报道变多) 也可能来自分母中非金融科技侧收缩 (常规报道变少), 单看份额无法区分两种路径, 结论对路径敏感时应同时报告 ln_ft_articles 与 ln_nf_articles 两个水平量的系数, 让读者看到份额变动究竟由哪一侧驱动; 这也是本阶段把弹性对与份额一并落盘的设计意图。第八, 与家族强度列的搭配用法: 份额高而强度低的银行年, 媒体叙事广而浅, 常见于营销驱动的数字化宣传期; 份额低而强度高的银行年, 报道少而专, 常见于技术落地但曝光克制的阶段 — 两列交叉提供的这一象限结构是单一计数指数无法表达的信息, 也是本家族把广延与集约边际拆开测量的最终回报。

<!-- rendered-citations:begin -->
Liu, J., Chen, S., Su, F., & Liu, J. (2025). Digital transformation disclosure and bank loans: An information heterogeneity perspective. International Journal of Finance & Economics, 30(4), 4004-4038. https://doi.org/10.1002/ijfe.3105
Liu, H., & Hu, J. (2025). Bank Fintech and firm leverage adjustment speed: Evidence from China. Research in International Business and Finance, 73, 102613. https://doi.org/10.1016/j.ribaf.2024.102613
Li, T., Stasinakis, C., Yeo, W. M., & Da Silva Fernandes, F. (2025). Fintech, financial development and banking efficiency: Evidence from Chinese commercial banks. The European Journal of Finance, 31(10), 1245-1295. https://doi.org/10.1080/1351847X.2025.2468481
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Liu, S., Wang, B., & Zhang, Q. (2024). Fintech regulation and bank liquidity creation: Evidence from China. Pacific-Basin Finance Journal, 84, 102276. https://doi.org/10.1016/j.pacfin.2024.102276
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Boot, A., Hoffmann, P., Laeven, L., & Ratnovski, L. (2021). Fintech: What's old, what's new?. Journal of Financial Stability, 53, 100836. https://doi.org/10.1016/j.jfs.2020.100836
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Wang, R., Liu, J., & Luo, H. (2021). Fintech development and bank risk taking in China. The European Journal of Finance, 27(4-5), 397-418. https://doi.org/10.1080/1351847x.2020.1805782
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Thakor, A. V. (2020). Fintech and banking: What do we know?. Journal of Financial Intermediation, 41, 100833. https://doi.org/10.1016/j.jfi.2019.100833
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Zhang, X., & Li, Z. (2025). FinTech: The disruptive force reducing bank competition pressure. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101237
Yang, F., & Masron, T. A. (2023). Does financial inclusion moderate the effect of digital transformation on banks' performance in China?. Cogent Economics & Finance. https://doi.org/10.1080/23322039.2023.2267270
Chen, S., Alexiou, C., & Lee, S. (2024). Beyond binary: exploring the interplay of China's digital transformation and firm performance through dual mechanism analysis. Asia Pacific Business Review. https://doi.org/10.1080/13602381.2024.2434010
<!-- rendered-citations:end -->
