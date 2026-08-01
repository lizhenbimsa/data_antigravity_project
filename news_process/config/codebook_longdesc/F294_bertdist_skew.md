---
family_id: F294
columns:
- fin_sent_zh_net_tone_skew_ctx
- fin_sent_zh_net_tone_skew_full
- fin_sent_zh_net_tone_skew_ss
- finbert2_net_tone_skew_ctx
- finbert2_net_tone_skew_full
- finbert2_net_tone_skew_ss
- finbert_cn_net_tone_skew_ctx
- finbert_cn_net_tone_skew_full
- finbert_cn_net_tone_skew_ss
unit: 样本偏度 (无量纲三阶标准化矩, 理论上无界; bank-year 格级)
formula: "skew = G1 偏度校正样本偏度, 对象 = 该 bank-year 格内逐篇净语调 nt_art = P(正面) − P(负面) ∈ [-1,1] (逐模型 × 逐轨); n < SKEW_MIN_N=10 的格 post-agg 掩为 NaN (n 口径 = nt_art 非 NaN 篇数计数, 禁用 pos_count)"
producer: pipeline/panel/bert_distribution.py::compute_article_distribution_cols + iter_agg_entries('skew') ; pipeline/panel/encode.py (SKEW_MIN_N post-agg 掩码块)
upstream:
- 23_bert_tone.parquet (三模型 × 三轨概率列 正面/负面[/中性])
- 22_words_tone.parquet (stage 23 输入基座)
- 14_materialize_ctx.parquet (content_ctx / content_ss 三轨文本物化)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: "Article 101126"
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: "24883-24892"
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: "105227"
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: "e1549"
- doi: 10.1016/j.jbef.2023.100809
  type: journal
  authors: Nițoi, M., Pochea, M.-M., & Radu, Ș.-C.
  year: 2023
  title: "Unveiling the sentiment behind central bank narratives: A novel deep learning index"
  venue: Journal of Behavioral and Experimental Finance
  vol: 38
  pages_or_artno: "100809"
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: "673-719"
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: "173-228"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: "43-96"
- doi: 10.1016/j.irfa.2014.02.006
  type: journal
  authors: Kearney, C., & Liu, S.
  year: 2014
  title: "Textual sentiment in finance: A survey of methods and models"
  venue: International Review of Financial Analysis
  vol: 33
  pages_or_artno: "171-185"
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: "1237-1282"
- doi: 10.1016/S0304-405X(01)00066-6
  type: journal
  authors: Chen, J., Hong, H., & Stein, J. C.
  year: 2001
  title: "Forecasting crashes: Trading volume, past returns, and conditional skewness in stock prices"
  venue: Journal of Financial Economics
  vol: 61
  issue: 3
  pages_or_artno: "345-381"
new_dois: []
---

## CORE

【构念与来源】
本家族九列测度的构念是银行—年份格内媒体语调分布的不对称性: 把某家银行某一年全部通过留篇门控的银行金融科技报道, 逐篇由中文金融 BERT 模型打出净语调分数, 再对这一分数在格内的截面分布取三阶标准化矩, 即样本偏度。它回答的问题与均值型语调测度截然不同。均值只告诉研究者这一年媒体对该银行的报道总体上偏正面还是偏负面, 但两家均值完全相同的银行, 其舆情结构可以天差地别: 一家全年被平稳温和地正面报道, 另一家大部分时间被正面报道、却夹杂少数几篇极端唱衰的深度负面稿件。后者的净语调分布呈现长的负向尾巴, 偏度显著为负; 前者近似对称, 偏度接近零。这种坏消息是否以集中爆发的方式出现, 恰恰是均值和标准差都无法还原的分布形状信息。方法论的移植源头是 Chen, Hong 和 Stein (2001) 在股价崩盘风险文献中确立的条件偏度传统, 该文证明收益率分布的负偏度承载了与均值和波动率正交的独立信息。本家族把偏度这一统计工具从收益率对象移植到逐篇媒体情感得分对象上, 但必须强调两点刻意的口径切割: 其一, 本列是原始样本偏度, 正值表示右偏即正面极端更长, 负值表示左偏即负面极端更长, 没有像崩盘文献的 NCSKEW 那样加负号翻转, 也不做任何条件化处理; 其二, 构念含义不从收益率文献继承, 偏度在这里刻画的是媒体叙事的不对称结构而非资产价格的崩盘概率, 二者只共享数学形式。为什么媒体语调的不对称结构在中国银行业语境下值得单独测度, 有三层依据。第一, You, Zhang 和 Zhang (2018) 证明中国媒体的报道倾向受制度性激励塑造, 官方背景媒体与市场化媒体的批评能力不对称, 这使得针对银行的负面报道更可能以离散、集中爆发的形态出现而非均匀分布, 偏度正是捕捉这种爆发形态的最直接统计量。第二, Cookson, Fox, Gil-Bazo, Imbet 和 Schiller (2026) 表明社交媒体上集中的负面叙事可以直接催化银行挤兑, Fang, Wang, Wang 和 Yuan (2024) 用中国数据证明媒体情感与存款稳定性和银行系统性风险相连, 极端负面报道的尾部集中度因而具有超出均值的政策相关性。第三, Cookson 和 Niessner (2020) 与 Garcia (2025) 分别证明意见分布的分歧与发散形状本身对金融结果有预测力, 支持把分布形状作为独立于一阶矩的测度族纳入面板。

【方法学与计算】
计算链路是纯粹的零成本后处理, 不重跑任何模型推理。上游 stage 23 已为三个中文金融 BERT 模型在三条文本轨道上逐篇落盘分类概率列, 即每篇文章每个模型每条轨道各有正面概率与负面概率, 三分类模型另有中性概率。本家族的文章级中间量是逐篇净语调, 定义为正面概率减负面概率, 取值介于负一与正一之间; 该中间量由 bert_distribution 叶模块的 compute_article_distribution_cols 函数产出, 正负概率任一缺失则该篇记缺失, 绝不填零。聚合层由 iter_agg_entries 声明: 对每个银行—年份格, 面板引擎按 pandas 的 skew 聚合函数对格内全部非缺失逐篇净语调取偏度, 其实现是带小样本偏差校正的 Fisher-Pearson 调整偏度 G1, 即三阶中心矩除以标准差立方后再乘以依赖样本量的校正因子。聚合之后在 encode 层执行一道承重的 post-agg 掩码: 格内有效篇数小于常量 SKEW_MIN_N 即十篇时, 该格偏度改写为缺失。掩码的动机是小样本偏度纯属噪声, 样本偏度的绝对值存在机械上界, 三篇时上界约为根号三, 四篇时约为二, 此时数值主要反映样本量而非分布形状, 若放任其进入回归会作为含测量误差的解释变量引入衰减偏误, 宁缺勿噪。有效篇数的口径经过刻意的反事实排雷: 采用逐篇净语调非缺失篇数的专用辅助计数列, 与偏度聚合看到的样本量逐格恰好同源; 明确禁用另一个表面可用的篇数列 pos_count, 因为后者的语义是 argmax 判为正面的篇数, 以语调结果为条件筛样本属于内生选择, 一个五十篇全负面报道的格在该口径下会被误判为零篇而错掩。辅助计数列在掩码完成后即刻从面板删除, 绝不落入导出数据。掩码只改写偏度列本身, 因此逐篇净语调的格内均值与面板净语调列的恒等关系在包括被掩格在内的全部格上保持可断言, 这是回归前数据体检的机械锚点。架构上 bert_distribution 是零仓内依赖的真叶模块, 模型清单由调用方参数注入, 模块自身绝不反向引用 encode 以免形成循环引用; 文章级中间列在落盘前由 runner 单点删除, 不进入文章级 parquet。全链路只依赖 numpy 与 pandas 的确定性算子, 不涉及任何随机源或 BLAS 特征分解, 可逐位复现。守卫测试为 tests/test_bert_distribution_metrics.py, 其中锚死了阈值字面量与禁用 pos_count 的口径。对偏度公式再作一点直觉展开: 三阶中心矩把每篇净语调对格内均值的偏离取立方, 立方运算保留符号且放大远端偏离, 因此格内若存在少数远低于均值的极端负面稿件, 立方后的大负值会主导求和使统计量为负; 除以标准差立方使其无量纲化, 不随分布整体的线性平移与正比例缩放改变, 这正是它能在净语调方差不同的模型之间保持形状可解释性的原因; 小样本校正因子则修正三阶矩估计在有限样本下的系统性偏差。缺失处理贯彻逐篇级别的严格掩码: 推理失败哨兵篇与空文本篇的概率为缺失, 自动被排除在偏度样本之外, 不做任何插补。

【文献定位】
本家族在文本情感金融文献中的位置可以沿两条轴线刻画。第一条轴线是测度技术从词典计数到深度模型的演进。Kearney 和 Liu (2014) 的经典综述总结了词袋与词典法主导的第一代文本情感测度, 并明确指出从文章级得分到公司期间级聚合时的信息压缩是该文献的薄弱环节; Todd, Bowden 和 Moshfeghi (2024) 的新一代综述则记录了神经网络与预训练语言模型对金融情感测度的系统性替代。在中文金融语料这一特定域上, Du, Huang, Wermers 和 Wu (2022) 证明了语言与领域双重特异性的重要性, 通用译制词典在中文财经文本上系统性失真, 领域定制是必需而非可选; Ma, Zhang 和 Zhang (2025) 构建的中文细粒度情感词典与 Lan, Wu, Xu, Feng 和 Zhang (2025) 的中文金融大模型细粒度情感分析分别代表了词典路线与生成式模型路线在中文域上的当前前沿。本项目的三个中文金融 BERT 模型属于判别式预训练路线, 与词典法和大模型投票法在同一面板中三法并立互为印证。第二条轴线是从一阶矩向分布形状的扩展。Nițoi, Pochea 和 Radu (2023) 用深度模型构建央行叙事情感指数, Kirtac 和 Germano (2024) 证明模型型情感信号具有超出传统测度的经济价值, 但这两支文献的落点仍是均值型指数; Cookson 和 Niessner (2020) 与 Garcia (2025) 则证明分布的分歧与发散含有均值之外的独立信息。本家族的边际贡献正是在银行—年份面板上把逐篇模型概率的三阶矩物化为可直接进入回归的列, 与同一执行计划下的归一化熵、极端负面占比、跨模型分歧和年内动态共同构成五族分布形状测度, 偏度族承担其中有符号不对称性这一维。值得强调的是, 这一扩展在测度经济学意义上并非装饰性的: 如果媒体语调对银行结果的作用机制经由注意力集中与恐慌传导, 那么起作用的应当是少数极端稿件的存在与集中程度而非全年平均语气, 此时均值型测度会把机制信号稀释进大量中性报道的海洋里, 而偏度恰好把这一信号从均值中分离出来单独呈现; 反之, 若主效应完全由均值携带、形状族系数不显著, 也构成对爆发机制解释的反向证据。两种结果都有信息量, 这正是分布形状族作为机制判别工具的价值所在。

【识别策略定位】
在识别设计中, 本家族定位为处理变量侧的辅助测度与稳健性轨, 不充当任何论文的 canonical headline 处理变量。其主要用法有三。第一, 作为均值型语调回归的形状控制或替代解释变量, 检验主结论是否被舆情爆发结构而非平均水平驱动; 第二, 作为负面尾部集中度的有符号补充, 与固定阈值的极端负面占比族互相印证; 第三, 在跨模型三角验证框架下, 三个模型各自的偏度列并排提供同构念的三次独立测量。计量口径上有四条铁律必须复述。其一, 三个 BERT 模型的偏度列互为稳健性、不分主次, 各自 just-identified 并排进入各自的回归, 严禁把多个模型的同族列混进同一个 over-identified 的 Hansen J 检验, 这一禁令与三轨、co-primary 双轨嵌入、政治词权重梯度共用同一款铁律; 其二, 三条文本轨道 full、ctx、ss 之间同样各自 just-identified 并排, 禁混同一 Hansen J; 其三, 行宇宙遵循 full-only 留篇门控口径, 一篇文章是否计入银行金融科技报道的判定只看 llm_verified_full 为真, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集; 其四, 跨模型比较只允许比较各自回归的标准化系数, 因为二分类与三分类模型的净语调原始方差不同, 直接比较未标准化系数或水平值没有构念意义。多重检验方面, 三模型乘三轨共九列同族测度天然构成检验族, 家族层面的真 FWER 控制依托 Romano 和 Wolf (2005) 的逐步降序方法, 项目内由根级跨模型 rwolf 模板承接; 偏度族本身属于规格稳健性并排, 镜像政治词权重与词典消融先例。

【与相邻测度的构念区分】
本家族与同源相邻列的边界必须逐条划清。与净语调均值列相比, 偏度是三阶矩, 均值是一阶矩, 二者在被掩格之外共享完全相同的逐篇输入与缺失掩码, 差异纯粹在矩的阶数; 与语调标准差族相比, 标准差刻画分散程度但对称地对待两侧尾巴, 偏度专门刻画两侧尾巴的不对称; 与归一化熵列相比, 熵是文章内的测度, 刻画单篇文章上模型在各类别之间的犹豫程度, 而偏度是文章间的测度, 刻画格内多篇文章得分的截面形状, 两者的聚合单元根本不同; 与极端负面占比族相比, 占比在固定概率阈值处度量尾部质量, 是对分布单侧的局部快照, 偏度则是整个分布的全局有符号形状统计量, 二者互为印证而非替代; 与跨模型分歧双轨相比, 分歧度量的是同一篇文章上不同模型之间的意见离散, 偏度度量的是同一模型内不同文章之间的形状, 维度正交; 与年内波动和年内趋势列相比, 后两者引入月度时间维度, 偏度对格内文章的时间顺序完全不敏感, 打乱篇序不变。最后再次与崩盘文献的 NCSKEW 划界: 本列无负号、无条件化、对象是情感得分而非收益率, 引用崩盘文献仅锚定统计方法的出处, 不主张本列可直接解释为崩盘风险。与词典法语调族的关系上, 词典分数在本面板中没有平行的偏度列, 本家族是分布形状五族中唯一挂在 BERT 概率输出上的偏度测度。

【已知局限与稳健性梯子】
已知局限有六点, 均已在设计层面记账。第一, 小样本噪声: 偏度是对样本量最敏感的低阶矩之一, 十篇的掩码门槛是研究者选择, 门槛本身未做梯子化, 使用者应知晓掩码会系统性删去报道稀少的银行年份格, 使可估计样本向高曝光银行倾斜, 这是宁缺勿噪与样本选择之间的权衡。第二, 有界支撑的机械关联: 逐篇净语调被压缩在负一到正一的闭区间内, 均值靠近区间端点的格其同侧尾巴被机械压缩, 偏度与均值之间存在有界分布固有的负向机械关联, 解释系数时应与均值列同时入模或明示这一混杂。第三, 二分类模型的支撑差异: finbert2 是两类模型, 其净语调是单一正面概率的仿射变换, 偏度虽对正仿射变换不变从而在形状意义上可定义, 但其概率经过两类重归一化, 与三分类模型的净语调生成机制不同, 水平不可比, 只比标准化系数。第四, 早期试跑环境退化: 在仅两年的该面板上多数格达不到十篇门槛, 偏度大面积缺失属预期退化而非缺陷, 生产规模十九年语料下正常出值。第五, 本家族属非嵌入列, 依照 carve-out 口径没有对应的下划线 lg 孪生列, 也不受嵌入换轨影响。第六, per-model 独立降级: finbert2 依赖本地私有模型目录, 缺席时仅该模型自身的偏度三列不产, 另两个模型照常, 不搞同族连坐。稳健性梯子的完整形态是三模型乘三轨的九列并排, 加上同计划内的阈值梯子族与双轨分歧族在相邻构念上的旁证; 各梯子之间刻意正交不交叉, 不做模型乘轨道乘阈值的全笛卡尔展开以避免列爆炸。除上述六点外, 还有两条与面板计量交互的实务提醒。其一是掩码与固定效应的交互: 十篇门槛的掩码使偏度列的缺失模式与银行曝光度相关, 在含银行固定效应与年份固定效应的规格中, 组内可识别样本进一步收缩到同一银行跨年都达标的观测, 使用者在报告样本量时应说明偏度回归的估计样本是主回归样本的选择子集, 且该选择由报道数量这一前定变量驱动而非由结果变量驱动, 选择机制本身是可辩护的。其二是测量误差的方向: 即便通过了十篇门槛, 偏度作为三阶矩的抽样方差仍显著大于均值的抽样方差, 把它放在解释变量位置时的经典测量误差会使系数向零衰减, 因此形状族系数的不显著不能直接解读为机制不存在, 应结合样本量分层的敏感性检验与仅保留高篇数格的子样本回归共同判断; 这也是本家族在识别设计中定位为辅助测度与稳健性轨而非 canonical 处理变量的深层原因。所有形状族列的口径变更均须同步守卫测试与执行计划文档, 后者完整记录了五轮评审史。

## VAR: fin_sent_zh_net_tone_skew_ctx

【变体差分】
本列是 fin_sent_zh 模型偏度测度的 ctx 轨变体, tier 为 standard。与家族 canonical 即同模型 full 轨列的唯一差分维度是文本轨道: ctx 轨的逐篇输入文本是 content_ctx, 即标题加目标银行实体上下文窗口截取的正文片段, 由 stage 14 物化, 标题以 prepend 方式并入; 模型、净语调定义、偏度公式、十篇掩码门槛与 full 轨逐项相同。构念上, ctx 轨把模型的注意力约束在银行实体附近的语句上, 剔除同篇文章中与目标银行无关段落的语调污染, 因此本列度量的是银行针对性语境内语调分布的不对称, 而非全文层面的不对称; 当一篇长稿只在个别段落点名批评某银行时, ctx 轨的净语调更可能捕捉到该负面片段, 使本列对针对性负面爆发更敏感。口径上须谨记: ctx 轨是 conditional-on-full 的稳健性轨, 行宇宙为 full-only 留篇门控通过集的子集, 是否算一篇银行金科报道只看 llm_verified_full; 本列与同模型 full、ss 轨列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。有效篇数按 ctx 轨自身概率列非缺篇数计, 不借 full 轨分母, 不足十篇的格掩为缺失。解释上, 本列与同模型 full 轨列的系数对照可用于判别负面爆发信号究竟来自银行针对性语句还是来自文章整体氛围: 若 ctx 轨系数更强, 说明机制经由点名式批评而非泛行业悲观。

## VAR: fin_sent_zh_net_tone_skew_full

【变体差分】
本列是家族三个 core 列之一, fin_sent_zh 模型在 full 轨上的净语调偏度, 属分布形状族的 canonical 轨道形态。模型维度: fin_sent_zh 对应 HuggingFace 公开模型 bardsai/finance-sentiment-zh-base, 是在金融短语库语料传统上微调的中文金融三分类情感模型, 输出正面、负面、中性三类概率; 其逐篇净语调取正面概率减负面概率, 中性概率不进入净语调但通过概率归一化间接压缩两端, 使该模型的净语调分布在三个模型中通常最向零收缩, 由此其偏度对温和语调海洋中的少数极端稿件相对更敏感, 这是解释本列系数时应带入的模型特征。轨道维度: full 轨文本为标题 prepend 加全文正文, 是三轨中信息最完整、也是留篇门控所依据的轨道, 门控口径为 full-only, 即一篇文章是否计入银行金融科技报道只看 llm_verified_full 为真, 因此本列的行宇宙就是留篇宇宙本身, 无需子集条件化, 这也是 full 轨列被列为 core 而 ctx 与 ss 轨列为 standard 的结构性原因。计算细节与家族 CORE 节完全一致: 文章级中间量为该模型 full 轨正负概率之差, 正负概率任一缺失则该篇缺失; 格内非缺篇数不足十篇时格值掩为缺失, 篇数口径为专用辅助计数列而非 argmax 判正篇数; 偏度实现为带小样本校正的 G1。与同格相邻列的分工: 本列与 fin_sent_zh_net_tone_full 共享逐篇输入, 前者取三阶矩后者取一阶矩; 与同模型极端负面占比列在负尾构念上互证, 与归一化熵列在聚合单元上正交。铁律复述: 本列与 finbert_cn、finbert2 的同轨偏度列构成 per-model 三元并排, 互为稳健性、不分主次, 各自 just-identified, 禁混同一 over-identified Hansen J; 跨模型只比标准化系数。本列无下划线 lg 孪生, 属非嵌入 carve-out。早期试跑面板上仅达到十篇门槛的格出值, 大面积缺失属预期退化, 生产规模语料下正常。关于模型来源与域适配还须补充两点。第一, 该模型的训练谱系源自金融短语库这一以英文财经新闻短句人工标注为起点的语料传统, 中文迁移版本继承了其以句子级语调判断为目标的标注哲学, 与本项目逐篇全文推理的用法之间存在粒度差, stage 23 通过滑动窗口切片加置信度加权池化把句子级模型能力延伸到长文, 本列的逐篇净语调因此是全文各窗口判断的加权综合而非单句快照, 这对偏度的含义是有利的: 长篇负面调查稿的多个窗口一致判负会产生高置信的深负净语调, 恰好落在本列意在捕捉的左尾上。第二, 解释系数时的方向约定: 本列取值为负表示该银行该年的报道语调分布左偏, 即存在相对于自身年内平均语气更极端的负面稿件集群, 数值越负集中爆发结构越明显; 取值为正表示正面极端更突出, 在中国银行业媒体语境下常对应表彰性专题报道的批量投放。回归中建议与同模型净语调均值列同时入模以吸收有界支撑带来的均值与偏度机械关联, 并在表格中报告标准化系数以便与另两个模型的平行规格对照。

## VAR: fin_sent_zh_net_tone_skew_ss

【变体差分】
本列是 fin_sent_zh 模型偏度测度的 ss 轨变体, tier 为 standard。与家族 canonical 的差分维度仍是文本轨道: ss 轨逐篇输入为 content_ss, 即标题加银行实体与金融科技词在同一句及其正负一句窗口内共现的句段拼接, 是三轨中语境约束最严格的一轨, 度量的是银行与金融科技被同句谈论的最小语境内语调分布的不对称。回退语义是本列区别于 ctx 轨的承重细节, 且严格镜像 ctx 的回退设计: 当一篇留篇文章内不存在银行与金融科技的同句共现时, content_ss 回退为全文正文, 同时该篇的 ss_is_fallback 标记为真, 回退篇与非回退篇共享同一 n_articles 分母, 不因回退而缩减行宇宙; 极端情形下金科词表不可用时全部篇标记回退, 属优雅降级而非报错。因此本列在共现稀疏的银行年份格上会向 full 轨语义收敛, 解释时可结合回退占比理解其与 full 轨列的差值来源。其余口径与家族一致: 行宇宙为 full-only 留篇门控通过集的子集, ss 轨是 conditional-on-full 稳健轨; 有效篇数按 ss 轨自身概率非缺篇数计, 十篇门槛下不足即掩缺失; 本列与同模型 full、ctx 轨列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。解释上, 本列在共现密集格上提供最强的针对性语境证据, 其与 full 轨列的系数分离度是判别同句并置语调是否携带独立信息的直接对照。

## VAR: finbert2_net_tone_skew_ctx

【变体差分】
本列是 finbert2 模型偏度测度的 ctx 轨变体, tier 为 standard, 差分由模型与轨道两个维度叠加。轨道维度与其余 ctx 列相同: 输入为 content_ctx 即标题加银行实体上下文窗口文本, 度量银行针对性语境内的语调分布不对称, 行宇宙为 full-only 留篇集子集的 conditional-on-full 稳健轨。模型维度继承 finbert2 的全部特性: 该模型是项目本地私有微调的二分类模型, 只输出负面与正面两类概率且两类归一化, 其逐篇净语调等价于正面概率的仿射变换, 分布支撑与三分类模型不同, 水平不可比, 跨模型只比标准化系数; 模型经环境变量 FINBERT2_MODEL_DIR 解析, 目录缺席时优雅跳过, 本列与该模型另外八列一同不产, 属 per-model 独立降级, 不连坐其他模型。中性概率列对该模型是全缺失占位, 不参与净语调计算。偏度公式、十篇掩码门槛、篇数口径与家族一致, 有效篇数按本模型 ctx 轨概率非缺篇数计。铁律: 本列与同模型 full、ss 轨列及其他模型同轨列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 本列无下划线 lg 孪生, 属非嵌入 carve-out。由于偏度对正仿射变换不变, 本列在形状层面与三分类模型的 ctx 轨列可作方向性对照, 但由于二分类分布支撑更外扩, 对照仍限于标准化系数的符号与量级, 不及水平。

## VAR: finbert2_net_tone_skew_full

【变体差分】
本列是家族三个 core 列之一, finbert2 模型在 full 轨上的净语调偏度。模型维度是本列最重的差分: finbert2 是项目自行微调的本地私有中文金融 BERT, 二分类结构只输出负面与正面两类概率并在两类上归一化, 没有真实的中性类, 落盘的中性概率列是刻意保留的全缺失占位列而非零值, 以防下游凭列存在误判类数。二分类结构对偏度的含义有两层影响, 须在解释时明确。第一层是可定义性: 逐篇净语调等于正面概率的二倍减一, 是单一概率的正仿射变换, 而样本偏度对正仿射变换严格不变, 故本列在数学上恰好等于格内逐篇正面概率分布的偏度, 形状构念完好; 这一点与同模型的归一化熵列形成鲜明对照, 后者在二分类下退化为净语调绝对值的严格单调递减变换, 构念受损, 而偏度族不受此退化影响, 是 finbert2 分布形状信息保存最完整的一族。第二层是可比性: 二分类模型缺少中性缓冲, 概率质量被迫在正负两端分配, 其净语调分布天然比三分类模型更外扩, 原始方差更大, 因此本列与另两个模型的偏度列之间禁比水平, 只比各自回归的标准化系数。轨道维度: full 轨为标题 prepend 加全文正文, 行宇宙即 full-only 留篇门控通过集本身, 门控只看 llm_verified_full。可得性: 模型目录由环境变量解析, 未配置时本列连同该模型全族列合法缺席, per-model 独立降级不连坐, 这也意味着复现包使用者在无私有模型的机器上应预期本列整列缺席而非报错。其余计算口径与家族一致: 正负概率任一缺失该篇缺失, 格内非缺篇数不足十篇掩为缺失, 篇数口径禁用 argmax 判正计数。铁律复述: 本列与 finbert_cn、fin_sent_zh 的 full 轨偏度列构成 per-model 三元并排, 互为稳健性、不分主次, 各自 just-identified, 禁混同一 over-identified Hansen J; 无下划线 lg 孪生。本列在三元并排中的独特证据价值恰恰来自其模型谱系的独立性: finbert2 是项目在自有语料上微调的私有模型, 与两个公开模型的预训练语料、标注来源和微调流程均不同源, 若本列的偏度系数与公开模型的平行规格给出同号且量级相当的标准化系数, 则可有力排除结论被某个公开模型的训练数据特异性驱动的疑虑; 反之若三者分裂, 分裂模式本身即是测量诊断信息, 应结合跨模型分歧双轨列一并报告。另一个解释细节涉及零点语义: 二分类归一化下正负概率各半时净语调恰为零, 该零点是模型真实可达的中立判断而非缺失占位, 因此格内偏度的符号是围绕这一可达零点附近的均值展开的真实形状陈述。使用建议与另两个 core 列一致: 与同模型净语调均值列同时入模, 报告标准化系数, 并在样本量分层敏感性检验中确认十篇门槛不驱动结论。复现披露方面, 涉及本列的表格须注明私有模型缺席环境下该列整列缺席属设计内合法状态, 对应回归以另两个模型的平行规格呈现即可, 不构成复现失败。

## VAR: finbert2_net_tone_skew_ss

【变体差分】
本列是 finbert2 模型偏度测度的 ss 轨变体, tier 为 standard, 模型与轨道双维差分。轨道维度: 输入为 content_ss, 即标题加银行与金融科技同句共现句段及正负一句窗口的拼接文本, 是语境约束最严的一轨; 回退语义镜像 ctx 设计, 无银行与金融科技同句共现的篇 content_ss 回退为全文正文并标记 ss_is_fallback 为真, 回退篇与非回退篇共享同一 n_articles 分母, 共现稀疏格上本列语义向 full 轨收敛。行宇宙为 full-only 留篇集的子集, 属 conditional-on-full 稳健轨。模型维度: finbert2 为本地私有二分类模型, 净语调是正面概率的仿射变换, 偏度对仿射变换不变故形状构念完好, 但分布支撑与三分类模型不同, 跨模型禁比水平只比标准化系数; 模型目录缺席时本列随该模型全族合法缺席, per-model 独立降级。计算口径与家族一致: 有效篇数按本模型 ss 轨概率非缺篇数计, 不足十篇掩缺失, 篇数禁用 argmax 判正计数。铁律: 本列与同模型 full、ctx 轨及他模型同轨偏度列各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 非嵌入 carve-out 无下划线 lg 孪生列。解释上, 本列与同模型 ctx 轨列的差值主要由回退占比与同句共现语境的额外收窄共同决定, 在共现密集的大银行格上二者分离最明显, 是判别同句并置语境是否携带独立信号的对照点。

## VAR: finbert_cn_net_tone_skew_ctx

【变体差分】
本列是 finbert_cn 模型偏度测度的 ctx 轨变体, tier 为 standard。差分维度为轨道: 输入文本是 content_ctx, 即标题 prepend 加目标银行实体上下文窗口截取的正文, 由 stage 14 物化; 本列度量银行针对性语境内逐篇净语调分布的不对称, 相对 full 轨剔除了同篇文章中与目标银行无关段落对语调的稀释, 对埋在长稿局部的针对性负面爆发更敏感。模型维度沿用 finbert_cn 即 HuggingFace 公开模型 yiyanghkust/finbert-tone-chinese, 中文金融三分类模型, 输出中性、正面、负面三类概率, 逐篇净语调为正面概率减负面概率。行宇宙口径: ctx 轨为 conditional-on-full 稳健轨, 一篇文章是否计入银行金融科技报道只由 llm_verified_full 判定, 本列行宇宙是 full 留篇集的子集; 有效篇数按 ctx 轨自身概率非缺篇数计, 不借 full 轨分母, 不足十篇的格掩为缺失, 篇数口径禁用 argmax 判正计数。铁律: 本列与同模型 full、ss 轨列互为稳健性、不分主次, 与他模型 ctx 轨列构成 per-model 并排, 各自 just-identified, 禁混进同一 over-identified Hansen J; 跨模型只比标准化系数; 非嵌入 carve-out 无下划线 lg 孪生。由于 ctx 轨文本平均更短, 单窗即可容纳的篇占比更高, 本列受滑动窗口池化影响小于 full 轨列, 其偏度更接近模型对银行邻近语句的单次整体判断的截面形状, 这是与 full 轨列对照时应带入的技术差异。

## VAR: finbert_cn_net_tone_skew_full

【变体差分】
本列是家族三个 core 列之一, finbert_cn 模型在 full 轨上的净语调偏度。模型维度: finbert_cn 对应 HuggingFace 公开模型 yiyanghkust/finbert-tone-chinese, 属金融语调分类模型谱系的中文版本, 在中文金融文本上微调, 输出中性、正面、负面三类概率, 是三个模型中与金融语调这一目标构念在训练目标上最贴合的一个, 也是加载失败时会 fail-loud 报错而非静默跳过的严格模型之一, 保证本列在生产环境中的可得性是强约束而非尽力而为。逐篇净语调为正面概率减负面概率, 中性类概率虽不直接进入差值, 但通过三类归一化决定两端概率的可用质量, 使该模型对模糊语篇倾向给出接近零的净语调; 因此本列的偏度主要由少数被模型高置信判正或判负的文章驱动, 对高置信极端稿件的爆发结构敏感, 这一特征与其作为负面尾部集中度旁证的用法契合。轨道维度: full 轨输入为标题 prepend 加全文正文, 是留篇门控所依据的轨道, 门控口径 full-only, 只看 llm_verified_full, 本列行宇宙即留篇宇宙本身; 超长文章在 stage 23 由滑动窗口切片推理并按置信度加权池化聚合, 保证全文轨的概率对长稿同样有定义, 这一点对偏好长篇深度报道的负面调查稿尤其重要, 因为恰恰是这类稿件构成左尾。计算口径与家族一致: 正负概率任一缺失该篇缺失, 格内非缺篇数不足十篇的格掩为缺失, 篇数口径为专用辅助计数, 禁用 argmax 判正篇数; 偏度为带小样本校正的 G1, 正值右偏、负值左偏, 非 NCSKEW 无负号。铁律复述: 本列与 fin_sent_zh、finbert2 的 full 轨偏度列构成 per-model 三元并排, 互为稳健性、不分主次, 各自 just-identified, 禁混进同一 over-identified Hansen J; 与本列同模型的 ctx、ss 轨列同样并排不混; 跨模型只比标准化系数; 非嵌入 carve-out 无下划线 lg 孪生。早期试跑面板上大面积缺失属十篇门槛下的预期退化。补充两点本列特有的解释脉络。第一, 中性类的缓冲作用使本列的偏度信号更干净: 三分类结构允许模型把语气含混的稿件安置到中性类而不强行摊派正负, 因此进入左尾的深负净语调篇必然是模型以高置信同时压低中性与正面概率的结果, 本列的负偏度由此更接近确凿负面爆发的度量, 而非语气噪声的伪影; 与二分类模型的平行列对照时, 这一结构差异是解读系数差别的第一候选解释。第二, 报告惯例: 本列作为三 core 列中训练目标与金融语调构念最贴合的一列, 在跨模型稳健性表中通常作为列序首位呈现, 但这纯属排版惯例而非计量地位差异, 三列在口径上严格 co-equal, 任何将其中一列升格为主测度、他列降为附录的表述都违背 per-model 互为稳健性的家族口径; 与同模型净语调均值列同时入模、报告标准化系数、按篇数分层做敏感性检验的使用建议同样适用于本列。该模型属严格加载模型, 非预期加载失败会响亮报错而非静默跳过, 因此生产面板上本列的缺失只可能来自十篇门槛掩码, 不存在模型缺席这一缺失来源, 缺失模式的解读比 finbert2 平行列更单纯。

## VAR: finbert_cn_net_tone_skew_ss

【变体差分】
本列是 finbert_cn 模型偏度测度的 ss 轨变体, tier 为 standard。差分维度为轨道: 输入为 content_ss, 即标题加银行实体与金融科技词同句共现句段及其正负一句窗口的拼接, 是三轨中最贴近银行与金融科技被直接并置谈论这一目标语境的一轨, 本列因此度量最小共现语境内语调分布的不对称, 对同句直接负面并置的爆发结构最敏感。回退语义严格镜像 ctx 设计: 留篇文章内无银行与金融科技同句共现时, content_ss 回退为全文正文并将该篇 ss_is_fallback 标记为真, 回退篇与非回退篇共享同一 n_articles 分母; 金科词表整体不可用的极端情形下全篇标记回退, 属优雅降级。共现稀疏的银行年份格上本列向 full 轨语义收敛, 解读其与 full 轨列的差异时应参考回退占比。模型维度沿用 finbert_cn 三分类公开模型, 净语调为正面概率减负面概率。行宇宙为 full-only 留篇集的子集, ss 轨属 conditional-on-full 稳健轨; 有效篇数按 ss 轨自身概率非缺篇数计, 不借 full 轨分母, 不足十篇的格掩为缺失, 篇数口径禁用 argmax 判正计数。铁律: 本列与同模型 full、ctx 轨列及他模型 ss 轨列各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 非嵌入 carve-out 无下划线 lg 孪生列。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Nițoi, M., Pochea, M.-M., & Radu, Ș.-C. (2023). Unveiling the sentiment behind central bank narratives: A novel deep learning index. Journal of Behavioral and Experimental Finance, 38, 100809. https://doi.org/10.1016/j.jbef.2023.100809
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Kearney, C., & Liu, S. (2014). Textual sentiment in finance: A survey of methods and models. International Review of Financial Analysis, 33, 171-185. https://doi.org/10.1016/j.irfa.2014.02.006
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Chen, J., Hong, H., & Stein, J. C. (2001). Forecasting crashes: Trading volume, past returns, and conditional skewness in stock prices. Journal of Financial Economics, 61(3), 345-381. https://doi.org/10.1016/S0304-405X(01)00066-6
<!-- rendered-citations:end -->
