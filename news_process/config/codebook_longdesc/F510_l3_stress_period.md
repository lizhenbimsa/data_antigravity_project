---
family_id: F510
columns:
- stress_period
unit: 二元哑变量 (0/1, 年度层面)
formula: 'panel[''stress_period''] = panel[''year''].isin({2015, 2018, 2020}).astype(int); 年份 ∈ {2015 股灾去杠杆前夜, 2018 资管新规去杠杆, 2020 新冠疫情冲击} 记 1, 其余年份记 0'
producer: pipeline\panel\runner.py (L1633-1634, STRESS_YEARS 常量与主构造)；pipeline\panel\export.py L916 (dta 标签 'Stress Period (2015/2018/2020)')
upstream:
- year
citations:
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2618-2646
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: 'Beyond the headlines: Sentiment divergence and financial distress'
  venue: Global Finance Journal
  vol: '66'
  issue: ''
  pages_or_artno: Article 101126
- doi: 10.1108/JED-06-2025-0296
  type: journal
  authors: Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.
  year: 2025
  title: Investor negativity derived from news shapes firm distress dynamics under bounded rationality
  venue: Journal of Economics and Development
  vol: '27'
  issue: '4'
  pages_or_artno: 309-321
- doi: "10.1016/j.ceqi.2024.06.003"
  type: "journal"
  authors: "Ji, Z., Ye, N., & Kong, D."
  year: 2024
  title: "The contraction of Chinese shadow banking and corporate investment behavior: Evidence from the background of the “New Rules on asset management”"
  venue: "China Economic Quarterly International"
  vol: "4"
  issue: "2"
  pages_or_artno: "119-132"
new_dois: []
---

## CORE

【构念与来源】
stress_period 是一枚年度层面的银行业系统性压力期二元哑变量, 用于在银行-年面板回归中标定「非常规冲击年份」, 支撑对情感测度非对称效应的检验。其构念动机来自新闻情感与企业困境动态之间存在期间异质性这一发现: Pham, Huynh, Nguyen & Luu (2025, Journal of Economics and Development) 证明新闻负面情感在有限理性框架下对企业困境动态的塑造作用并非在样本期内均匀分布, 而是随宏观状态发生系统性强弱变化; Garcia (2025, Global Finance Journal) 进一步刻画了情感度量之间的「分歧」(sentiment divergence) 如何随企业财务困境程度加剧而扩大, 意味着单一样本期内情感与困境/压力状态的关系并非线性齐次, 若将全样本期笼统地作单一线性关系估计, 会掩盖压力期特有的非对称反应, 也会使常规期的估计系数被压力期的极端观测拖拽偏移。stress_period 正是为分离出这种非对称效应而设的时间断点标记: 令样本期内三个具体年份取 1, 其余年份取 0, 供研究者在回归设定中以交互项形式检验「情感 (或其他处理变量) 的边际效应是否在压力期发生结构性改变」。

三个压力年份的选取严格锚定中国银行业过去十余年的三次公认系统性冲击: 2015 年对应「股灾」——当年 6 月至 8 月沪深两市剧烈波动, 叠加同期人民币汇改引发的资本市场连锁反应, 银行体系流动性与资产质量同时承压; 2018 年对应「去杠杆」——资管新规 (《关于规范金融机构资产管理业务的指导意见》) 正式落地叠加中美贸易摩擦升温, 银行表外业务收缩、影子银行治理进入攻坚阶段; 2020 年对应「新冠疫情」——公共卫生危机导致宏观经济骤停, 银行让利实体经济、不良贷款拨备计提压力集中显现。三者共同点是: 均为全国性、非银行个体特质驱动的系统性冲击, 而非某家银行的个别经营事件, 这保证了 stress_period 作为「时间固定的宏观状态标记」在银行-年面板中的外生性——它不随任何一家银行自身的经营决策变化, 仅由日历年份决定。

【方法学与计算】
stress_period 的计算是最简形式的确定性年份映射, 无任何统计估计、平滑或阈值搜索过程: 对面板中的 year 列执行集合成员判定 year.isin({2015, 2018, 2020}), 结果转 int64 类型后写入 stress_period 列, 值域严格为 {0, 1}。该常量集合 STRESS_YEARS 在代码中以 Python 集合字面量硬编码于 runner.py 主构造函数内, 与紧邻的 tone_x_stress_{full,ctx,ss} 交互项构造共用同一份年份定义, 保证同一次面板构建流程内「压力期标记」与「压力期交互项」使用的是同一份年份口径, 不存在跨模块的常量漂移风险。若研究者需要调整压力年份的定义 (例如追加或剔除某一年份), 应在该唯一定义处修改, 由下游所有消费该常量的交互项与标签自动继承, 而非在多处分别硬编码后手工同步。

stress_period 本身是外生给定的确定性构造量, 不依赖任何模型输出、不涉及情感测度的三轨 (full/ctx/ss) 或 co-primary 双轨嵌入架构, 也不涉及 LLM 三家投票或 BERT 三模型的任何环节——它纯粹是从 year 列派生的日历年份标记, 因此不存在梯子/多模型并排、不适用「各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J」的铁律 (该铁律约束的是同一构念的多种测量口径互为替代, 而 stress_period 是唯一口径的宏观状态哑变量, 无替代口径)。stress_period 生成后被用作构造下游交互项 tone_x_stress_full / tone_x_stress_ctx / tone_x_stress_ss (家族外, F511 或邻近家族) 的乘数因子, 三轨情感变量各自与 stress_period 相乘, 三条交互项彼此仍遵循三轨并排互为稳健性的口径, 但 stress_period 自身作为共同的时间标记, 在三条交互项中是恒等复用而非分轨构造。

在数据规模层面需特别说明: 早期试跑盘面样本年份仅覆盖 2017-2018 两年 (T=2 切片), 落入 STRESS_YEARS={2015,2018,2020} 交集的只有 2018 一年, 因此早期试跑盘面上曾曾 stress_period 呈现出「2018 年全部记 1、2017 年全部记 0」的确定性二分, 不构成方差不足问题, 而是样本年份窗口与压力年份定义的自然交集结果。生产全量语料覆盖 2007-2025 (T=19), 三个压力年份 2015/2018/2020 均落在样本窗口内, stress_period 将呈现三段离散 1 值与十五段离散 0 值的完整分布, 交互项的识别力在生产规模下显著优于早期试跑盘面。

【文献定位】
stress_period 的构念设计呼应三支文献。其一是压力测试与银行数字化韧性文献: Kwan, Lin, Pursiainen & Tai (2024, Journal of Financial and Quantitative Analysis) 以新冠疫情这一系统性冲击为准自然实验, 检验银行数字化能力在压力期的差异化表现, 其研究设计同样依赖于「明确标定的压力期时间窗口」这一构造思路, 印证了将疫情年份 (2020) 与其他系统性金融冲击年份并列纳入压力期定义在银行业实证研究中的方法学合理性, 该文发表于金融学顶刊之一的 Journal of Financial and Quantitative Analysis, 为本指标的构造范式提供了顶刊级方法学锚点。其二是 Pham, Huynh, Nguyen & Luu (2025, Journal of Economics and Development) 关于新闻负面情感如何在有限理性下塑造企业困境动态的研究, 证明新闻情感对企业困境的边际影响并非期间齐质, 支持了「新闻情感效应存在期间异质性、压力期需单独识别」这一构念前提。其三是 Garcia (2025, Global Finance Journal) 关于情感度量分歧 (sentiment divergence) 与企业财务困境关系的研究: 该文发现不同来源情感指标之间的分歧程度会随企业困境加深而系统性放大, 意味着「压力期」不仅是情感水平发生位移的时段, 也是不同情感测度之间一致性发生结构性变化的时段, 这为 stress_period 在稳健性检验中与 llm_vote_tone / dict-based tone 等多种情感口径分别交互、观察各口径在压力期表现是否一致提供了额外的构念依据。 在三个压力年份的具体设定依据上, Ji、Ye 与 Kong (2024) 以中国资管新规引致的影子银行收缩为背景识别其经济后果, 为本指标把 2018 年认定为中国金融体系去杠杆压力年份提供了实证依据。迁移边界须诚实标明: 该文的因变量是企业投资行为、分析单位为企业, 与本项目银行×年层面的年份哑变量不同; 更关键的是它仅覆盖 2018 资管新规这一个事件, 对 stress_period 另外两个年份 (2015 股灾去杠杆前夜、2020 新冠冲击) 不提供任何依据——将三年并置为单一压力期标记属本项目的研究者设定, 该文不予背书。
## VAR: stress_period

【变体差分】
本家族仅含 stress_period 一列, tier=standard, 无同家族其他成员构成差分对照, 因此本节说明的是该列自身相对于「无压力期区分的基准设定」的精确语义, 而非与家族内其他列的差异。stress_period 与家族外最邻近的 depins_post (存款保险制度时间断点调节项, 另一 runner.py 同代码块产出的年度哑变量) 在构造哲学上高度相似——两者都是「日历年份到二元状态」的确定性映射, 都用于构造与情感变量的交互项——但二者的识别设计存在本质差异: depins_post 是单一时间断点 (year>=2015 前后二分), 刻画的是一项全国统一实施的制度变更 (《存款保险条例》2015 年 5 月 1 日施行) 前后的结构性调节效应, 由于是全国无差别统一施行, 不构成处理组/控制组划分, 只是时间断点调节项而非双重差分设计; stress_period 则是三个离散、非连续的孤立年份并集, 刻画的是若干次相互独立的系统性冲击事件, 二者在样本期内可能同时为 1 (如 2018 年恰好落在 depins_post=1 且 stress_period=1 的交集), 使用时需注意二者交互项在同一回归中同时纳入可能引发的共线性风险——尤其在本机开发早期试跑盘面 T=2 的极窄年份窗口下, 2018 年单一样本点会使 stress_period 与 depins_post 在观测层面高度重合, 该退化现象在生产 T=19 的完整年份跨度下会自然消解, 因为压力年份 (2015/2018/2020) 中只有 2018/2020 落在 depins_post=1 区间内, 2015 年恰好落在 depins_post 断点之前, 两个哑变量在生产规模下具备真实的独立变异来源, 不再是同一子样本的重复标记。

进一步区分的是 stress_period 与依赖它派生的下游交互项 tone_x_stress_{full,ctx,ss} 之间的层级关系: stress_period 本身是不含情感信息的纯宏观状态哑变量, 可独立作为面板固定效应设定中的年份分组变量或稳健性检验的子样本划分依据使用; 而 tone_x_stress_* 系列是将 stress_period 与三轨情感测度 llm_vote_tone_{full,ctx,ss} 逐一相乘得到的交互项, 用于估计「情感效应在压力期是否发生边际改变」这一具体的非对称性假设, 二者不可混用——stress_period 单独进入回归只能吸收压力期的整体均值差异 (类似压力期固定效应), 无法识别情感的状态依赖交互效应; 只有搭配 tone_x_stress_* 交互项, 才能将「压力期整体水平位移」与「压力期情感敏感度变化」两种效应分离估计, 这也是交互项设定须同时纳入所有低阶项这一常见计量原则的体现——stress_period 作为低阶项与 tone_x_stress_* 交互项须同时出现在设定中, 缺失低阶项会导致交互系数的解释产生偏误。
<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309-321. https://doi.org/10.1108/JED-06-2025-0296
Ji, Z., Ye, N., & Kong, D. (2024). The contraction of Chinese shadow banking and corporate investment behavior: Evidence from the background of the “New Rules on asset management”. China Economic Quarterly International, 4(2), 119-132. https://doi.org/10.1016/j.ceqi.2024.06.003
<!-- rendered-citations:end -->
