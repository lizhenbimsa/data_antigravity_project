---
family_id: F085
columns:
- bank_cogn_mean
- bank_cogn_mean_ctx
- bank_cogn_mean_ss
unit: 无量纲相似度得分 (银行间 TF-IDF 余弦相似度的行均值; 值域闭区间 0 到 1)
formula: "bank_cogn_mean_{i,t} = mean_{j != i} cosine( tfidf(D_{i,t}), tfidf(D_{j,t}) ); D_{i,t} = 银行 i 在年 t 全部报道的超级文档; full 轨 D = (标题 + 空格 + 正文) 逐篇拼接, ctx/ss 轨 D = content_{ctx,ss} 逐篇原样拼接 (剔 *_is_fallback==True 行、禁 title 通道); TF-IDF = char_wb analyzer, ngram_range=(2,4), max_features=5000, min_df=min(2,n_valid), max_df=0.95, dtype=float32, 逐年独立向量化; cosine 对角置 NaN 后取行 nanmean; 超级文档短于 100 字符或当年有效银行 < 2 则该格置 NaN; 非负 TF-IDF 保证值域闭区间 0 到 1"
producer: "news_process/pipeline/panel/network_spillover.py::compute_cognitive_proximity (Stage 40 面板派生, 步骤 7h-cogn) ; news_process/pipeline/panel/export.py (Stata 变量标签)"
upstream:
- 14_materialize_ctx.parquet (content_ctx / content_ss + ctx_is_fallback / ss_is_fallback; ctx 与 ss 两轨超级文档源)
- 篇章级展开帧 df_exploded (原始 标题 / 内容 列 + target_bank + year; full 轨超级文档源)
- 41_panel_encode_aggregate (bank-year 面板骨架: target_bank × year 键, 供 merge 落列)
citations:
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: "You, K."
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
  pages_or_artno: "arXiv:2504.16318"
- doi: 10.18653/v1/2025.emnlp-main.1135
  type: journal
  authors: "Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S."
  year: 2025
  title: "Interpretable text embeddings and text similarity explanation: A survey"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 22314-22330
- doi: 10.3982/ECTA21048
  type: journal
  authors: "Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y."
  year: 2024
  title: "Toward a general theory of peer effects"
  venue: Econometrica
  vol: 92
  issue: 2
  pages_or_artno: 543-565
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: "Liu, Y., Cao, Z., & Wen, F."
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: "111823"
- doi: 10.1145/3589335.3651526
  type: journal
  authors: "Steck, H., Ekanadham, C., & Kallus, N."
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.1093/rfs/hhae026
  type: journal
  authors: "Han, M., Kim, S. H., & Nanda, V."
  year: 2024
  title: "Institutional brokerage networks: Facilitating liquidity provision"
  venue: The Review of Financial Studies
  vol: 37
  issue: 9
  pages_or_artno: 2903-2935
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1126/sciadv.abj9204
  type: journal
  authors: "Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F."
  year: 2022
  title: "A better index for analysis of co-occurrence and similarity"
  venue: Science Advances
  vol: 8
  issue: 4
  pages_or_artno: "eabj9204"
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: "Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M."
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: "Bramoullé, Y., Djebbari, H., & Fortin, B."
  year: 2020
  title: "Peer effects in networks: A survey"
  venue: Annual Review of Economics
  vol: 12
  pages_or_artno: 603-629
- doi: 10.1162/tacl_a_00134
  type: journal
  authors: "Levy, O., Goldberg, Y., & Dagan, I."
  year: 2015
  title: "Improving distributional similarity with lessons learned from word embeddings"
  venue: Transactions of the Association for Computational Linguistics
  vol: 3
  pages_or_artno: 211-225
- doi: 10.1111/jofi.12094
  type: journal
  authors: "Leary, M. T., & Roberts, M. R."
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: "Bramoullé, Y., Djebbari, H., & Fortin, B."
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.2307/2298123
  type: journal
  authors: "Manski, C. F."
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1007/s40821-024-00270-x"
  type: journal
  authors: "Marra, A., Cucculelli, M., & Cartone, A."
  year: 2024
  title: "So far, yet so close. Using networks of words to measure proximity and spillovers between firms"
  venue: "Eurasian Business Review"
new_dois:
  - "10.1007/s40821-024-00270-x"
---

## CORE

【构念与来源】
本家族刻画的是"银行间认知邻近度" (cognitive proximity), 即两家银行在信息空间中所调用的知识基础与话语主题彼此相似的程度。构念的理论源头是 Boschma (2005) 提出的五维邻近度框架: 该框架把主体之间的邻近性拆解为认知、组织、社会、制度与地理五个维度, 其中认知邻近度专指知识基础 (knowledge base) 的相似性——两个主体越是依赖相近的技术、概念与话语资源, 它们在认知上就越接近, 既更容易相互学习与吸收, 也更容易陷入同质化而丧失差异化优势。本项目把这一原本用于区域创新研究的构念迁移到中国银行业的新闻话语场域: 对每一家目标银行, 把它在某一年内被媒体报道的全部文本聚合成一份"超级文档", 再用 TF-IDF 向量化后的两两余弦相似度衡量任意两家银行超级文档之间的话语接近度, 最后对每家银行取它与当年其余所有银行相似度的均值, 得到该行当年的认知邻近度得分 bank_cogn_mean。得分高意味着这家银行的新闻主题与行业整体高度趋同, 处于"认知锁定"的风险区; 得分低意味着这家银行在信息空间中具有独特性, 呈现差异化特征。

必须郑重声明操作化归属: TF-IDF 余弦均值只是本项目对 Boschma (2005) 认知邻近度构念的自定义操作化, 并非该文原文给出的算法。源码注释中已记录一处引文勘误 (network-metrics-audit, 2026-06-13): 早期版本曾把这套"两两 TF-IDF 余弦相似度求均值"的做法归因于某篇用 transformer 从企业网站文本识别人工智能采纳、并构建企业间超链接网络度中心度的近期文献, 该归因不成立——那篇文献并不含此操作化。因此本家族在方法层面把 TF-IDF 余弦定位为"新闻话语相似度"的度量, 它是否严格等同于"知识基础相似度"这一构念, 仍需经由业务相似度基准的外部效度检验才能坐实 (Jaffe 技术邻近度、Bloom-Schankerman-Van Reenen 的技术接近度可作为可选的外部对照锚点); 这是本测度自带的构念效度前提, 写入本档以约束下游解读, 避免把话语层面的趋同直接读作知识结构层面的趋同。数据来源上, 超级文档取自篇章级展开帧: full 轨用原始的标题与正文拼接, ctx 与 ss 两轨用 stage 14 物化的 content_ctx 与 content_ss 逐篇拼接; 银行-年面板骨架来自 41_panel_encode_aggregate, 认知邻近度以 target_bank 与 year 为键 merge 落列。

从经济含义上看, 认知邻近度的高低对应两种截然不同的竞争态势。当一家银行的得分逼近上区间, 说明它的新闻话语——被报道的业务重点、风险叙事、战略提法——与同业高度重叠, 意味着它处在信息层面的认知锁定状态: 既可能因为跟随行业共识而降低被市场误读的风险, 也可能因为丧失话语独特性而在差异化竞争中落于下风; 源码在日志解读里以约 0.7 为高同质警示带、约 0.3 为高差异化带来标注这一梯度, 但这些只是解读性阈值而非硬性判据, 不构成任何面板实测断言。当得分落在下区间, 说明这家银行在信息空间中占据相对独特的话语位置, 被报道的主题结构与行业整体拉开距离, 呈现差异化特征。把这一构念放进银行面板的价值在于: 银行所处信息环境的同质性本身是一个可能同时驱动媒体情感与银行行为的混淆源, 显式度量并控制它, 有助于把同行溢出的净效应从共享话语环境的伪相关中剥离出来, 这也解释了本测度为何被定位为控制而非处理。

【方法学与计算】
计算严格逐年独立进行, 目的是规避跨年的词汇漂移: 每一年重新构建当年的 TF-IDF 词表与向量空间, 使同一年内各行的相似度处于同一坐标系下可比, 而不同年份之间因为重新拟合词表, 水平值并不直接跨年可比。具体链路如下。第一步, 按银行聚合文本: 在 full 轨上, 把每家银行当年每一篇报道的标题与正文用空格拼接后再整体串接成一份超级文档, 尽量最大化单行的信息量。第二步, 短文本守卫: 超级文档长度不足 100 个字符 (约相当于 50 个中文词) 的银行被判为文本过短、TF-IDF 会退化, 该行当年得分直接置 NaN; 若某年通过守卫的有效银行不足 2 家, 则当年全部置 NaN, 因为余弦相似度至少需要一对主体才有定义。第三步, TF-IDF 向量化: 采用 char_wb 分析器配合 2 到 4 元的字符 n-gram, 这一选择对中文特别友好——字符级 n-gram 无需依赖分词器 (不引入 jieba 的分词边界与未登录词问题), 又能捕获中文里以字组词、以词组短语的搭配结构; 向量化参数固定为最多 5000 个特征、min_df 取 2 与有效银行数的较小值、max_df 为 0.95、数据类型 float32, 在压制超高频与极低频噪声的同时控制内存。第四步, 余弦相似度: 在稀疏 TF-IDF 矩阵上计算两两余弦相似度得到相似度方阵, 把对角线 (银行与自身的相似度恒为 1) 置为 NaN 以排除自身, 再对每一行取 nanmean, 即得到该行与当年其余所有银行的平均相似度。第五步, 值域断言: 由于 TF-IDF 权重非负, 余弦相似度必落在闭区间 0 到 1, 代码用显式 raise (而非裸 assert, 以免在 python -O 下守卫被剥离而错误值静默落盘) 校验值域, 容差放宽到 1e-6 以适配 float32 的舍入边界。整套计算不调用任何外部 API, 是纯本地的 TF-IDF 运算, 零调用成本。

关于向量化的几处设计值得展开。TF-IDF 的逆文档频率项会压低在多数银行超级文档中普遍出现的字符 n-gram (如通用金融套话、监管高频词) 的权重, 抬高只在少数银行文本里出现的判别性 n-gram 的权重, 从而让余弦相似度更多由这家银行独有的话语指纹驱动, 而非通用词噪声; max_df 设为 0.95 进一步剔除出现在超过 95% 银行中、几乎无判别力的高频项, min_df 取 2 与有效银行数的较小值则剔除仅在单一银行出现、无法支撑跨行比较的孤立 n-gram。char_wb 分析器只在词边界内滑动字符窗口而不跨越空白拼接, 配合 2 到 4 元窗口, 在中文语境下等价于捕获单字、双字词与三四字短语的搭配, 既回避了分词器的边界误差与未登录词问题, 又保留足够的语义颗粒度。稀疏矩阵上的余弦相似度只在非零特征的交集上做内积, 内存与计算都可控; float32 在精度与内存之间取平衡, 也正是值域断言把容差放宽到 1e-6 的原因——float32 舍入可能让边界值略微越过 1.0。合并回面板时按 target_bank 与 year 做左连接, 未能进入向量化 (文本过短或当年有效银行不足两家) 的银行-年格自然落 NaN, 全程不做任何伪零填充, 以免把无法计算误读成相似度为零, 这与全仓网络列去伪零的口径一致。

【文献定位】
本测度处在三条文献脉络的交叉点上。其一是文本相似度与余弦方法脉络: 用中文金融文本的 TF-IDF 余弦对齐来度量主体间接近度, 最贴近的先例是 Liu, Cao 与 Wen (2024) 对企业与政府文本相似度的测量与定价研究, 其正是在中国情境下以文本余弦刻画主体间对齐并接入资产定价; 方法论上余弦相似度并非无懈可击, Steck 等 (2024) 与 You (2025) 分别指出余弦相似度在某些 (尤其是学习到的稠密嵌入) 空间中可能失真、"看似度量相似其实未必", 提醒使用者对余弦读数保持审慎; Levy, Goldberg 与 Dagan (2015) 关于分布式相似度的经验、Opitz 等 (2025) 对可解释文本嵌入与相似度解释的综述, 以及 Mainali 等 (2022) 对共现与相似度指数的改进, 共同界定了"文本相似度作为构念代理"的方法边界。Marra, Cucculelli 与 Cartone (2024, Eurasian Business Review) 用词语网络刻画企业间文本邻近度并度量溢出效应, 与本家族用 TF-IDF 银行超级文档余弦相似度刻画认知邻近度的操作化思路高度一致, 可作为该测度在企业层面的直接文献先例。本项目在 TF-IDF 这一稀疏、非负、可解释的空间内使用余弦, 值域良态落在 0 到 1, 相对稠密嵌入更少踩中上述失真陷阱, 但它终究仍是表层话语度量。其二是同行效应与网络计量脉络: 认知邻近度所服务的更大模块是同行网络与信息经纪, Leary 与 Roberts (2014) 证明同行企业确实影响公司金融政策, Grieser 等 (2022) 刻画公司金融政策中的网络效应, Manski (1993) 的反射问题、Bramoullé, Djebbari 与 Fortin (2009) 关于社会网络中同行效应的识别、以及 Boucher 等 (2024) 的同行效应一般理论, 共同规定了在网络中做因果识别时必须处理的内生性与反射难题。其三是中国银行业媒体情境脉络: Fang 等 (2024) 关于媒体情绪、存款稳定与银行系统性风险的中国证据, 与 Han 等 (2024) 的机构经纪网络研究, 说明媒体话语在银行网络中的传导具有现实经济后果, 为把"新闻话语趋同"纳入银行面板提供了外部相关性。

值得强调的是, 本项目选择 TF-IDF 而非稠密嵌入来操作化认知邻近度, 恰好规避了 Steck 等 (2024) 与 You (2025) 所警示的稠密空间余弦失真: 在学习到的嵌入空间里, 余弦读数会被表示学习的正则化与各向异性扭曲, 未必对应人类直觉的相似; 而 TF-IDF 是稀疏、非负、每一维都对应可解释字符 n-gram 的空间, 余弦的几何含义清晰、值域良态。Mainali 等 (2022) 对共现与相似度指数的改进则从统计角度提醒: 两两相似度的绝对水平会受样本组成 (当年进入向量化的银行集合) 影响, 这也是本测度逐年独立、且不宜跨年横比水平的方法学根据之一。同行网络脉络方面, 认知邻近度并不直接承担 Leary 与 Roberts (2014)、Grieser 等 (2022) 意义上的同行处理效应识别, 而是作为同期话语环境控制服务于该识别; Boucher 等 (2024) 的一般理论与 Bramoullé 等 (2009) 的网络识别结果共同界定了在网络中区分内生同行效应、外生情境效应与相关效应的条件, 本测度的同期控制角色正是为了净化其中的相关效应通道。

【识别策略定位】
必须厘清 bank_cogn_mean 在识别框架中的角色: 它是同期 (当年文本) 度量, 定位为信息环境同质性的控制变量, 而非处理变量。源码注释 (network_spillover.py 第 1793 行附近) 特意警示, 不要把 bank_cogn_mean (当年文本) 与滞后一期的 bank_emb_sim_mean_lag1 混淆口径——后者由 t 减一期超级文档算出、与 emb_peer_tone_lag1 共用同一相似度方阵、服务于滞后同行溢出的处理度量, 前者用当年文本、服务于同期的话语同质性控制。这一分工直接呼应网络计量的识别铁律: 同行溢出的处理度量采用严格滞后 (Lag Y 减一) 的行随机化权重矩阵乘以滞后一期的同行情感——权重矩阵 W[i,j] 由银行 i 与 j 在去年新闻共现篇数经行随机标准化 (每行归一到和为 1) 得到, 既类比空间计量里的空间权重矩阵、又压制大银行凭报道体量主导网络权重的规模效应, 且采用 both-verified 计数 (每篇文章对每条边只计一次、且仅当两家银行的 twin 行均通过 verification 过滤幸存)。以去年的权重乘去年的同行情感, 才能规避 Manski (1993) 的反射问题与同期反向因果。

Manski (1993) 把社会互动效应拆为三条通道: 内生效应 (同行的结果反过来影响自身)、外生或情境效应 (同行的特征影响自身) 与相关效应 (同处一个环境而共享未观测冲击所导致的伪相关)。认知邻近度作为同期控制叠加在滞后处理度量之上, 正是用来吸收其中的相关效应通道——嵌入相似话语空间的银行很可能同时暴露于相同的未观测行业冲击, 若不显式度量并控制这一话语同质性, 滞后溢出系数就会把相关效应误读为内生同行效应。Bramoullé, Djebbari 与 Fortin (2009) 证明, 在线性均值模型里非传递三元组 (朋友的朋友并非自己的朋友) 所提供的网络结构变异能打破反射问题、使内生效应重新可识别; Bramoullé, Djebbari 与 Fortin (2020) 的同行效应网络综述系统梳理了这一识别路径的适用边界, Boucher, Rendall, Ushchev 与 Zenou (2024) 的一般理论则进一步界定了在数据中区分上述三类效应各自所需的条件。本测度的同期控制角色, 就是为这套识别净化相关效应这一混淆通道, 而不承担识别因果本身的重任。

必须再强调处理用滞后、混淆用同期的分工不可互换: 认知邻近度作为信息环境控制, 应与被建模结果所在的当期同步测量, 才能吸收当期共享话语环境的混淆; 若错误地把它也改造成滞后处理变量, 就会与滞后溢出度量争夺同一识别变异、稀释因果解释力, 这正是源码在口径注释里反复警示不要混淆两者 lag 语义的根本原因。样本层面须再次提示本机开发样本 (T=2, 2017-2018) 的局限: 在如此浅的面板上, 去除伪零后一阶同行网络覆盖极稀, 滞后结构使有值格集中收缩到单一年度截面, 经纪 2SLS 在银行与年份双固定效应吸收下有效样本急剧收缩、银行固定效应趋于饱和、不足以识别, 论文不得在开发样本上宣称因果, 须待生产样本扩到 T 大于等于 3 并接入结局变量 (如 ROA) 后重估。认知邻近度本身因为逐年对全部达标银行计算, 覆盖面比一阶溢出网络更宽, 但其水平的经济解读同样要等生产语料才稳。

【与相邻测度的构念区分】
认知邻近度与面板中若干近邻测度形态相近而口径迥异, 须沿单元、聚合、表征、方向、符号、时态六条轴逐一切割以免下游误用。第一, 相对嵌入同业相似度 bank_emb_sim_mean_lag1: 后者用稠密语义嵌入 (且带 co-primary 的 _lg 孪生轨、并有 full/ctx/ss 三条 W 轨) 捕获更深层语义、且是滞后一期口径; 认知邻近度用 TF-IDF 表层字符 n-gram 话语、是同期口径, 更关键的是它是非嵌入测度、没有 _lg 孪生 (属非嵌入 carve-out, 与 boilerplate、surface_staleness 同类, 不参与 co-primary 双轨的 both-or-neither 契约)。表征轴上一个是稀疏可解释的字符 n-gram 空间、另一个是稠密学习嵌入空间, 时态轴上一个同期、一个滞后。第二, 相对战略差异化族 strat_diff 与 strat_sim (含 char / jieba / LDA / embedding 多法, 以及对行业质心的 centroid_diff): 那些度量的是一家银行与其最相似的前 N 个同行、或与行业质心之间的距离或最大相似度, 落点在与最近邻或质心的差距; 认知邻近度取的是与全部其余银行的均值, 刻画整个话语空间的同质化水平, 聚合轴上是均值对全体、而非取最近邻或对质心。第三, 相对相邻期文本连贯性 coh 族 (t 期对 t 减一期的文本余弦): 那是同一家银行跨年的纵向自相似度, 认知邻近度是同一年内跨行的横向相似度, 单元与时态都不同。第四, 相对篇章级相似度 article_sim 族: 那是文章级两两相似度的另一种单元与聚合口径, 不在 bank-year 网络层。第五, 相对同行情感网络压力 emb_peer_tone 与 emb_peer_tone_diag 族: 那是行随机化权重矩阵乘以同行情感的有向溢出, 方向轴上有向、符号轴上带情感正负; 认知邻近度是纯结构的话语同质性, 不加载任何情感权重、无方向、无符号。一言以蔽之, 本测度的独特性在于它是面向全体同行的、无向无符号、纯结构的、同期的平均两两相似度, 度量的是话语空间的整体趋同, 既不是有向有符号的情感溢出, 也不是与最近邻或质心的差异化缺口, 更不是跨年的自连贯。

【已知局限与稳健性梯子】
第一层稳健性梯子是三轨 (full / ctx / ss)。full 轨为历史 canonical 口径, 用原始标题加正文构建超级文档、显式开启标题通道; ctx 与 ss 两轨是 2026-07-03 扩展加入的规格稳健性轨, 超级文档改为 content_ctx 与 content_ss 逐篇原样拼接, 并且刻意剔除 *_is_fallback 为真的行 (只保留纯轨文本)、禁用 title 通道 (因为 stage 14 的 prepend_title 已把标题内嵌进 content_ctx 与 content_ss, 若再拼标题即双标题污染付费缓存)。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一个 over-identified 的 Hansen J 检验; 三轨属规格稳健性并排 (镜像政治词权重梯度、词典消融梯度的先例), 本族刻意不设跨轨 FWER 模板, 因为跨模型 rwolf 的先例只覆盖对同一构念的替代性 headline 测量, 而三轨是同一构念在不同文本窗口下的规格稳健, 不适用该 FWER 框架。

第二层须明确本测度没有 _lg co-primary 孪生: 认知邻近度是 TF-IDF 而非嵌入, 属非嵌入 carve-out, 不进入 co-primary 双轨的 both-or-neither 契约; 这与前述带 _lg 孪生的 bank_emb_sim_mean_lag1 形成对照, 也意味着换嵌入模型时本族零误改。第三层是构念效度局限: TF-IDF 新闻话语相似度未必等同 Boschma (2005) 意义上的知识基础相似度, 建议以业务相似度基准做外部效度检验 (Jaffe 提出的技术邻近度、Bloom-Schankerman-Van Reenen 的技术接近度可作为可选对照锚点, 见源码注释)。方法学上, Steck 等 (2024) 与 You (2025) 提醒稠密嵌入空间中的余弦读数会被表示学习的正则化与各向异性扭曲、看似度量相似其实未必, 本项目正因此选用稀疏、非负、每维对应可解释字符 n-gram 的 TF-IDF 空间来规避该失真, 但读数终究仍是话语表层信号; Mainali 等 (2022) 则从统计角度提醒两两相似度的绝对水平会受样本组成 (当年进入向量化的银行集合) 影响, 这也是本测度逐年独立、且不宜跨年横比水平的方法学根据之一。

第四层是可扩展但当前固定的实现超参: char_wb 的 n-gram 阶数 (2 到 4)、max_features (5000)、min_df、max_df (0.95) 与 100 字符短文本守卫阈值原则上都可做敏感性梯子, 当前生产口径将其固定, 未来若开梯子仍须遵各变体各自 just-identified 并排、禁混同一 over-identified Hansen J 的铁律。第五层是逐年独立带来的跨年不可比: 每年重拟合词表以规避跨年词汇漂移, 代价是水平值不宜跨年直接横比。第六层是短文本退化与浅面板局限: 超级文档不足 100 字符或当年有效银行不足 2 家会落 NaN——且是真 NaN 而非伪零填充, 以免把无法计算误读成相似度为零, 与全仓网络列去伪零的口径一致; 开发样本 T=2 下退化更明显, 且 ss 文本最短、三轨中最易触发短文本守卫。最后须披露一处刻意的口径不对称: full 轨用原始文本 (含标题通道), ctx 与 ss 轨用 stage 14 文本 (禁标题通道), 两者文本来源不同源属刻意设计而非缺陷, 已在此完整披露; 此外值域守卫由显式 raise 而非裸 assert 完成 (裸 assert 在 python -O 下会被剥离、守卫静默失效、错误值悄悄落盘), 容差放宽到 1e-6 以适配 float32 余弦的舍入边界。

## VAR: bank_cogn_mean

【变体差分】
本列是家族的 canonical 无后缀列, 也是整个认知邻近度测度在网络溢出族中的 headline (tier 为 core), Stata 变量标签为"Cognitive Proximity (TF-IDF)"。它区别于两条孪生轨的精确差分只在文本来源与标题通道: 本列在 full 轨上构建超级文档, 即对每家目标银行当年的每一篇报道, 把原始"标题"列与原始"内容"列用空格拼接, 再把当年该行全部报道如此串接成一份长文档; 换言之, 本列显式开启标题通道 (标题 + 正文一并进入向量化), 使用的是未经三轨物化的原始文本列, 这是它与 ctx、ss 两轨最本质的口径区别——那两轨读取的是 stage 14 已 prepend_title 的 content_ctx 与 content_ss、并禁用标题通道以避免双标题。其余计算与家族 CORE 所述完全一致: 逐年独立向量化、char_wb 分析器配 2 到 4 元字符 n-gram、最多 5000 特征、min_df 取 2 与有效银行数较小值、max_df 为 0.95、float32; 100 字符短文本守卫与当年有效银行至少 2 家的守卫逐格生效; 余弦方阵对角置 NaN 后取行 nanmean; 非负 TF-IDF 保证值域落在闭区间 0 到 1, 由显式 raise 校验 (容差 1e-6 适配 float32 舍入)。口径定位上, 本列是同期 (当年文本) 度量, 承担信息环境同质性控制的角色, 而非滞后处理变量; 它与滞后一期的 bank_emb_sim_mean_lag1 口径不可混淆 (源码第 1793 行附近的显式警示), 也不同于战略差异化族的最近邻距离与同行情感网络压力的有向溢出。作为规格稳健性梯子的 canonical 轨, 本列与 bank_cogn_mean_ctx、bank_cogn_mean_ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一个 over-identified 的 Hansen J 检验; 本列为 TF-IDF 非嵌入测度, 属非嵌入 carve-out, 没有 _lg co-primary 孪生, 不进入 co-primary 双轨的 both-or-neither 契约。解读时须记住: 高值指向新闻话语与行业整体趋同的认知锁定风险, 低值指向信息空间独特性的差异化特征, 而话语层面的趋同是否等同知识结构趋同, 仍待业务相似度基准的外部效度检验。

须澄清一个容易误读的命名: 本列虽为无后缀列, 但其无后缀并非某些梯子里"历史命名产物、并非主轨"的情形, 而恰恰因为它是认知邻近度最早落地、且开启标题通道读全文的历史 canonical 口径, 在网络溢出族中承担 headline 身份, ctx 与 ss 两轨是后续 2026-07-03 才补入的规格稳健性孪生。在所属的经纪网络 (brokerage_network) 论文里, 本列作为同期信息环境同质性控制进入回归, 叠加在滞后一期的同行溢出处理度量之上, 用来吸收嵌入相似话语空间的银行共享未观测冲击这一混淆通道, 而非充当处理变量或工具变量; 也正因如此, 它以当年文本计算, 与滞后一期口径的 bank_emb_sim_mean_lag1 分工明确、口径不可互换。经济解读上, 本列高值对应认知锁定 (话语与行业趋同)、低值对应差异化 (信息空间独特), 源码日志以约 0.7 与约 0.3 为解读性提示带、非硬判据, 也非面板实测断言。最后重申计算的确定性要点: 逐年重拟合词表使水平不宜跨年横比, 短文本与有效银行不足两家的守卫使部分格落 NaN 而非伪零, 值域由显式 raise (而非在 python -O 下会被剥离的裸 assert) 守死在闭区间 0 到 1; 本列的计算全程不触外部 API, 是零成本的本地 TF-IDF 运算, 因此不受离线缓存守卫约束, 也不进入 co-primary 嵌入的付费播种范畴。

计量使用上还有两点操作提示与逐年独立口径直接相关。其一, 由于每年重拟合词表会带来水平的年度位移, 回归中应始终纳入年份固定效应把这一位移整体吸收掉, 此时估计所用的识别变异恰是同一年内跨银行的相对差异——而这正是逐年独立向量化保证可比的那部分变异, 口径与设计自洽; 若在无年份固定效应的合并回归中直接使用本列水平值, 跨年词表漂移会混入系数, 属误用。其二, 守卫落下的 NaN 格在回归中应任其自然缺失剔行, 不得以零或均值插补——无法计算的格与相似度恰好为零是两个完全不同的事实状态, 插补会把文本过短银行的缺失系统性地伪装成低同质性, 造成向下偏误。此外须说明本列与网络结构指标族的一处口径差异: 三十三个结构指标 (度中心度、聚类系数等) 带同篇、同句窗、严格同句三种共现判据后缀变体, 而本列不带任何判据后缀——认知邻近度的输入是银行各自的超级文档而非银行对银行的共现边, 判据敏感性梯子对它没有定义, 属结构性不适用而非遗漏。

## VAR: bank_cogn_mean_ctx

【变体差分】
本列是认知邻近度的 ctx (实体上下文窗口) 轨, tier 为 standard, Stata 变量标签为"Cognitive Proximity (TF-IDF, ctx window text)"。它与 canonical full 列的差分只在超级文档的文本来源与标题通道: 本列不读原始"标题"与"内容", 而是读取 stage 14 物化的 content_ctx——即以"标题前置拼接目标实体窗口"方式生成的上下文文本, 把当年该行每一篇报道的 content_ctx 逐篇原样拼接成超级文档。两处刻意设计必须复述准确: 其一, 剔除 ctx_is_fallback 为真的行, 只保留纯 ctx 轨文本参与向量化; 其二, 禁用标题通道, 因为 content_ctx 在 stage 14 已由 prepend_title 内嵌标题, 若再拼一次标题即造成双标题污染。其余计算与家族一致: 逐年独立的 char_wb 2 到 4 元字符 n-gram TF-IDF、最多 5000 特征、min_df 取 2 与有效银行数较小值、max_df 为 0.95、float32; 100 字符守卫与有效银行至少 2 家守卫逐轨独立生效, 缺 content_ctx 列时整轨跳过; 余弦对角置 NaN 后取行 nanmean, 值域闭区间 0 到 1 由显式 raise 校验。构念意图上, ctx 轨把话语相似度收窄到实体上下文邻域, 检验 canonical 的认知同质性结论是否被报道中与目标银行无关的外围段落所驱动。口径铁律: 本列与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J; 属非嵌入 carve-out, 无 _lg 孪生; 与 full 轨文本来源不同源 (full 用原始文本含标题通道, 本轨用 stage 14 文本禁标题通道) 属刻意设计并已披露。本机 T=2 开发样本上, ctx 轨因文本更短更易触发短文本守卫而退化, 属预期现象, 该列只作规格稳健性对照, 不单独承重。

## VAR: bank_cogn_mean_ss

【变体差分】
本列是认知邻近度的 ss (银行与金融科技同句共现窗口) 轨, tier 为 standard, Stata 变量标签为"Cognitive Proximity (TF-IDF, ss same-sent text)"。它与 canonical full 列的差分同样只在超级文档的文本来源与标题通道: 本列读取 stage 14 物化的 content_ss——即以"标题前置拼接目标银行与金融科技词在同一句共现的句子及其前后若干句窗口"方式生成的靶向文本, 把当年该行每一篇报道的 content_ss 逐篇原样拼接。两处刻意设计与 ctx 轨同型: 剔除 ss_is_fallback 为真的行、只保留纯 ss 轨文本; 禁用标题通道, 因为 content_ss 已由 prepend_title 内嵌标题, 再拼即双标题污染。其余计算与家族一致: 逐年独立 char_wb 2 到 4 元字符 n-gram TF-IDF, 参数与 100 字符守卫、有效银行至少 2 家守卫逐轨独立生效, 缺 content_ss 列时整轨跳过; 余弦对角置 NaN 后取行 nanmean, 值域闭区间 0 到 1 由显式 raise 校验。回退语义须与全仓契约一字不差: ss 镜像 ctx, 当一篇报道不存在银行与金融科技同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真——而本列在构建 ss 轨超级文档时正是剔除这些 fallback 行, 只保留真正含同句共现的靶向文本参与相似度计算。构念意图上, ss 是三轨中语义靶向最强也最短的文本轨, 把认知邻近度收窄到"银行与金科真正同句出现"的核心论述邻域, 检验结论是否被外围话语驱动。口径铁律: 本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified 的 Hansen J; 属非嵌入 carve-out, 无 _lg 孪生。解读注意: ss 文本最短, 在 T=2 开发样本上退化判 NaN 的概率三轨最高, 该列只作 conditional-on-full 的规格稳健性对照, 不单独承重; 与 full 轨文本来源不同源属刻意设计并已披露。

<!-- rendered-citations:begin -->
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Opitz, J., Moeller, L., Michail, A., Padó, S., & Clematide, S. (2025). Interpretable text embeddings and text similarity explanation: A survey. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 22314-22330. https://doi.org/10.18653/v1/2025.emnlp-main.1135
Boucher, V., Rendall, M., Ushchev, P., & Zenou, Y. (2024). Toward a general theory of peer effects. Econometrica, 92(2), 543-565. https://doi.org/10.3982/ECTA21048
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, 111823. https://doi.org/10.1016/j.econlet.2024.111823
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity?. Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Han, M., Kim, S. H., & Nanda, V. (2024). Institutional brokerage networks: Facilitating liquidity provision. The Review of Financial Studies, 37(9), 2903-2935. https://doi.org/10.1093/rfs/hhae026
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), eabj9204. https://doi.org/10.1126/sciadv.abj9204
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks: A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Levy, O., Goldberg, Y., & Dagan, I. (2015). Improving distributional similarity with lessons learned from word embeddings. Transactions of the Association for Computational Linguistics, 3, 211-225. https://doi.org/10.1162/tacl_a_00134
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Marra, A., Cucculelli, M., & Cartone, A. (2024). So far, yet so close. Using networks of words to measure proximity and spillovers between firms. Eurasian Business Review. https://doi.org/10.1007/s40821-024-00270-x
<!-- rendered-citations:end -->
