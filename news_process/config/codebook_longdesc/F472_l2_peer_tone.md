---
family_id: F472
columns:
- peer_tone_2nd_lag1_ctx
- peer_tone_2nd_lag1_full
- peer_tone_2nd_lag1_ss
- peer_tone_lag1_ctx
- peer_tone_lag1_full
- peer_tone_lag1_ss
unit: 网络加权同行情感 (无量纲连续值, 与 llm_vote_tone 同标度约 [-1,1]; bank-year 面板列)
formula: "peer_tone_lag1{trk} = Σ_j W[i,j](t-1)·tone_j(t-1)·1{obs_j} / Σ_j W[i,j](t-1)·1{obs_j}; peer_tone_2nd_lag1{trk} = Σ_j W2[i,j]·tone_j(t-1)·1{obs_j} / Σ_j W2[i,j]·1{obs_j}, W2 = (W·W) 去对角, W 为共现邻接的行随机标准化, tone = llm_vote_tone{trk}"
producer: news_process/pipeline/panel/network_spillover.py::compute_network_spillovers
upstream:
- 21_tone_llms.parquet (llm_vote_tone_full/ctx/ss)
- 41_panel_encode_aggregate.parquet (target_bank, year, llm_vote_tone_*)
- df_exploded 篇章级共现 (co_mentioned_banks, both-verified 邻接)
citations:
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D., Buchner, A., & Zareei, A.
  year: 2026
  title: "The persistence of news sentiment: Implications for return predictability"
  venue: Economics Letters
  vol: 260
  pages_or_artno: 112803
- doi: 10.1016/j.jcorpfin.2025.102772
  type: journal
  authors: Schwenkler, G., & Zheng, H.
  year: 2025
  title: "News-driven peer co-movement in crypto markets"
  venue: Journal of Corporate Finance
  vol: 93
  pages_or_artno: 102772
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: "Diamond cuts diamond: News co-mention momentum spillover prevails in China"
  venue: Journal of Banking & Finance
  vol: 171
  pages_or_artno: 107356
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: Emerging Markets Review
  vol: 64
  pages_or_artno: 101234
- doi: 10.1002/ijfe.3025
  type: journal
  authors: Ahmad, M., Hall, S. G., Law, S. H., & Nayan, S.
  year: 2024
  title: "Spillover effects in the nexus of finance-institutions-growth: New insights from spatial Durbin analysis on emerging economies"
  venue: International Journal of Finance & Economics
  vol: 30
  issue: 3
  pages_or_artno: 2470-2491
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: 103870
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2015.02.003
  type: journal
  authors: Lee, C. M. C., Ma, P., & Wang, C. C. Y.
  year: 2015
  title: "Search-based peer firms: Aggregating investor perceptions through internet co-searches"
  venue: Journal of Financial Economics
  vol: 116
  issue: 2
  pages_or_artno: 410-431
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: "10.1016/j.najef.2024.102307"
  type: journal
  authors: "Klaucke, K."
  year: 2025
  title: "Text Spillover: Measuring connectedness of financial institutions based on news text data"
  venue: "The North American Journal of Economics and Finance"
new_dois:
  - "10.1016/j.najef.2024.102307"
---

## CORE

【构念与来源】
本家族刻画的是同行网络溢出情感 (network peer sentiment spillover): 对每一家目标银行 i, 在年份 t, 用其在新闻共现网络中的同行去年 (t-1) 的媒体情感, 按网络权重加权平均, 得到一个"同行舆论压力"标量。构念要回答的经济学问题是: 一家银行当年的行为与结果, 是否受到与它同处一个舆论场、被媒体一起提及的同行去年舆论境况的牵引。这既是同行效应 (peer effects) 文献的核心问题, 也是把媒体情感从"单主体信号"推广到"网络传导信号"的自然延伸。以往银行级情感度量把每家银行视作孤立个体, 只用它自身被报道的语调; 但现实中金融机构的融资成本、存款稳定、市场估值都嵌入在一个相互关联的舆论生态里 —— 同业负面消息会经由投资者的类比推断、媒体的连带报道、以及监管注意力的外溢, 传导到本来并无直接经营问题的同行身上。本家族正是要把这种"横向舆论传导"显式量化为一个可进入回归右端的连续变量。同行效应对公司金融决策的牵引由 Grieser, Hadlock, LeSage & Zekhnini (2022) 在网络框架下系统刻画, 他们证明公司财务政策存在显著的网络溢出且网络结构本身承载识别信息; 媒体情感作为可定价、可传导的信息载体则由 Tetlock (2007) 奠基, 他证明媒体语调对市场收益有内容性 (非纯噪声) 影响。本家族把两支文献接合, 用新闻共现邻接构造同行集、用银行级媒体情感填充节点值, 得到一个"谁和谁在舆论上被绑定、被绑定者去年的语调如何"的加权聚合。

数据来源有两路且必须严格区分, 二者在构念上分工明确: 一路给"网络的形状", 一路给"节点的取值"。第一路是节点情感值, 取自 21_tone_llms 的 llm_vote_tone 列 (三家 LLM 多数投票共识: gpt54nano · gemini31 · deepseekv4 各自出票、取多数), 再经 41_panel_encode_aggregate 聚合为 bank-year 面板。选用 LLM 投票共识而非单一词典分, 是为了让节点情感对否定、程度、转折等中文语言学结构更稳健, 与词典轨互为稳健性 (Du, Huang, Wermers & Wu, 2022 的中文金融情感词典代表词典范式)。第二路是网络结构本身, 取自篇章级 df_exploded 的 co_mentioned_banks: 若两家银行 i 与 j 在同一篇报道中被共同提及 (both-verified 口径: 仅当两家银行的 twin 行均通过 verification 过滤幸存时, 该篇文章对这条边只计 1 次, 修复 omni-g-net-spill-01 的重复计边), 则在年份 t-1 的邻接矩阵 A 上 A[i,j] 累加该年两家共同出现的报道篇数。这一"新闻共现即同行"的操作化, 与 Lee, Ma & Wang (2015) 用投资者共搜构造 search-based peer firms、以及 Ge, Li & Zheng (2025) 用中国新闻共现刻画企业关联的效度证据同源。留篇门控沿用全项目 full-only 口径 (2026-06-29): 一篇报道是否算作"银行金科报道"只看 llm_verified_full, 故共现网络的边计数以 full 轨留篇集为准、与 n_articles 分母一致; ctx/ss 轨仅在节点情感值的填充上换用对应轨的 llm_vote_tone, 而网络结构 (邻接与权重) 三轨共享同一 full 口径的 co-mention 骨架, 绝不逐轨重建 —— 这是理解本家族三轨差异的关键: 三轨只在"节点取什么值"上分叉, 不在"谁连谁"上分叉。

【方法学与计算】
计算分四步, 逐年独立执行。其一, 构造滞后年 t-1 的银行共现邻接矩阵 A(t-1), 对角置零 (一家银行不与自身共现)。其二, 行随机标准化: W[i,j] = A[i,j] / Σ_k A[i,k], 使每一行的权重和为 1, 类比空间计量中的行标准化空间权重矩阵。行标准化的目的是防止被媒体高频提及的大银行 (工农中建交等) 凭其巨大的共现度数主导网络权重, 使 peer_tone 沦为"大行去年情感"的代理; 行标准化后, 每家银行的同行权重都归一到单纯形上, 度量的是"相对同行结构"而非"绝对共现规模" —— 这一 row-stochastic 空间滞后设定与新兴市场金融溢出的空间 Durbin 分析 (Ahmad, Hall, Law & Nayan, 2024) 同源。其三, 构造同行情感向量: 对邻接矩阵覆盖的每一家银行 j, 取其 t-1 年的 llm_vote_tone 值; 未被观测到情感 (去年无有效票、或不在面板) 的同行以布尔掩码 obs_mask 标记。其四, 计算网络加权同行均值。

一阶溢出 peer_tone = (W @ tone_obs) / denom1, 其中 tone_obs 把未观测同行置 0, denom1 = W 仅对观测同行列的权重和 —— 这是本家族的关键度量修复 (netspill-peertone-fillna, metric-audit 2026-06-10): 早期实现用 tone_vec.fillna(0), 把"在网但去年情感缺失"的同行以 0 注入分子, 而其权重仍留在行和 (=1) 分母, 导致加权均值系统性向 0 衰减 (伪零 / attenuation bias, 会人为压低 peer_tone 的横截面方差、削弱第一阶段强度); 正确做法是只对 observed-tone 同行求加权均值并按其权重和重新归一化, 无任何观测同行则整格置 NaN (孤立银行守卫, network-03), 而非伪零。这一修复直接影响 IV 的弱工具诊断, 故不是无关痛痒的实现细节。二阶溢出 peer_tone_2nd 刻画"邻居的邻居"的舆论传导 (LeSage-Pace 空间计量的高阶空间滞后思想): W2 = W·W, 再 np.fill_diagonal(W2, 0.0) 去掉对角自反馈, denom2 = W2 对观测同行的权重和, peer_tone_2nd = (W2 @ tone_obs) / denom2, 同样按观测同行重归一, 使其标度从旧的"路径概率加权和"变为"二阶邻居加权均值"(更可解释、与一阶同口径)。去对角是排他性识别的机械前提: 若保留 W² 对角, 二阶工具会含本行自身的滞后情感, 违背作为工具变量的排他约束 —— 这正是 Bramoullé, Djebbari & Fortin (2009) 通过社会网络识别 peer 效应所要求的、二阶邻居须剔除经 W² 回流到自身的路径。须精确披露标度语义: W² 去对角后行和不再恒为 1, 本重归一是对工具的逐观测 (row-specific) 确定性变换, 不是全局标量缩放; 2SLS 仅对工具集的全局非奇异线性变换不变, 行特定除数会改变工具的截面变异、第一阶段系数与 F 统计量, 故旧注释"相关性不变"不成立 (omni-g-net-spill-06 勘误)。最后, 所有列一律取 lag1 (Lag(Y-1)): 权重矩阵与情感向量都用去年 t-1 的值, 严格错开当期, 这是规避 Manski 反射问题 (焦点与同行同期互相决定导致的不可识别) 与同期反向因果的标准做法; 用去年舆论解释今年结果之所以合理, 依赖情感的时间持续性, 而新闻情感确有可预测的持续性 (Aksoy-Yurdagul, Buchner & Zareei, 2026)。这里须强调一个易被误读的实现细节: 网络的形状 (谁与谁共现、行随机权重多大) 和节点的情感值双双取自 t-1, 因此本家族的每一列都是一个纯滞后的、外生于当期结果的横向舆论强度; 当期 t 的共现结构与情感完全不进入计算。逐年循环 (for year in years) 内, 若某滞后年 t-1 的共现数据不足 (邻接为空或少于 2 家银行), 该年整体跳过、不产伪值, 这与孤立银行的 NaN 守卫共同保证了列的稀疏是"诚实的缺失"而非填充的噪声。

关于取值范围与经济解读: 因节点情感 llm_vote_tone 取值约在 [-1,1] (负面到正面), 而 W 与 W² 行归一后是同行的凸组合权重, 故 peer_tone 与 peer_tone_2nd 都落在同行情感的凸包内、量纲与 llm_vote_tone 一致 (无量纲连续值)。一个较正的 peer_tone 意味着焦点银行去年的共现同行整体被媒体正面报道, 焦点银行处于"友善舆论邻里"; 较负则处于"负面舆论邻里", 可能承受同业负面消息的连带压力 (如挤兑传染的舆论前兆)。这一横向传导的下游经济后果 —— 存款稳定、融资成本、系统性风险 —— 在中国银行样本上有直接证据 (Fang, Wang, Wang & Yuan, 2024), 也与社群情感信号本身可定价的发现 (Cookson, Lu, Mullins & Niessner, 2024) 一致, 说明本家族并非纯统计构造而承载可检验的经济机制。

【文献定位】
本家族坐落在三支文献的交汇处。一是媒体情感的信息与定价文献: Tetlock (2007) 证明媒体语调对市场有内容性影响, Shapiro, Sudhof & Wilson (2022) 给出可复现、可迁移的新闻情感测度范式 (本家族节点情感的测量学参照), Holzman, Miller & Twedt (2023) 刻画媒体情感与硬信息披露 (季度盈余公告) 的相互纪律作用, 说明媒体语调并非独立于基本面而是与之动态互纠; 在中国情境下, Xu, Hua & Zhang (2025) 证明官方媒体语调对股市有解释力, Fang, Wang, Wang & Yuan (2024) 直接在银行层面把媒体情感与存款稳定、系统性风险相连 —— 后者与本项目"银行×媒体情感"对象、语种完全同域, 是本家族外部效度最贴近的锚, 也提示 peer_tone 的下游结局 (融资成本、存款流) 有坚实的经济渠道。二是同行网络与共现传导文献: Grieser 等 (2022) 的网络效应证明网络结构承载识别信息、Lee, Ma & Wang (2015) 基于投资者共搜的 search-based peer firms 证明"感知同行"可由行为数据揭示、Ge, Li & Zheng (2025) 关于中国新闻共现动量溢出、Schwenkler & Zheng (2025) 关于新闻驱动的同行共动, 共同支撑"用新闻共现构造同行集"的效度并说明共现网络能传导可定价的横向信号。三是社会信号与舆论传染文献: Cookson, Lu, Mullins & Niessner (2024) 的 social signal 说明社群层面的情感聚合本身可定价, 为把个体情感升维为网络加权聚合提供微观依据。节点情感的测量学基础另由 Du, Huang, Wermers & Wu (2022) 的中文金融情感词典代表, 本项目 LLM 投票轨与其词典轨互为稳健性。三支文献的交汇点正是本家族的贡献所在: 既有的银行媒体情感研究多止于"银行 i 自身的语调 → 银行 i 的结果", 属单节点信号; 既有的同行网络研究多聚焦财务政策 (投资、杠杆、股利) 的横向模仿, 节点值是财务量而非舆论量。本家族把"舆论量"放进"同行网络"的节点, 得到一个既承载媒体信息、又承载网络传导结构的复合度量, 用以检验银行是否会因同业去年的舆论境况 (而非仅自身舆论) 而调整行为 —— 这在银行业尤为重要, 因为存款人、监管者、投资者对"谁像谁"的类比推断, 会让一家健康银行因同业负面新闻而承压。空间计量方法学上, 行随机 W 的空间滞后 W×y 是新兴市场金融溢出研究的标准工具 (Ahmad 等, 2024), 而把它用于媒体情感节点则是本项目对该方法的领域迁移。Klaucke (2025, The North American Journal of Economics and Finance) 用新闻文本构造金融机构间的连接性/溢出度量, 与本家族用新闻共现网络刻画银行同行舆论传导的操作化思路直接同源, 为文本溢出网络的效度提供最新佐证。

【方法学补充: 逐轨与逐年的独立性】
须再澄清两个方法学不变量, 它们决定了家族六列如何相互关系。其一, 逐年独立: 每个目标年 t 的邻接、权重、情感向量都只从 t-1 单年数据构造, 年份间不共享 W, 故某年共现稀疏不会污染其它年 —— 这既是 lag1 设定的自然结果, 也让面板在纵向上可解释为"每年的同行舆论快照"。其二, 逐轨仅在节点分叉: full/ctx/ss 三轨的分叉点唯一地落在"节点取哪条 llm_vote_tone", 网络的邻接与行随机权重恒由 full 口径的 co-mention 构造; 这一设计选择意味着三轨列的差异纯粹反映"节点情感测量的文本范围"敏感性, 而非"网络结构"敏感性, 使三轨成为节点测量的干净稳健性梯子, 不与网络结构的稳健性混淆。这也是为何本家族不设"逐轨重建邻接"的变体: 那会同时改变节点与结构两个维度, 破坏梯子的正交性。

【识别策略定位】
本家族在识别上有双重身份, 这也是它同时含 core-treatment 列与 core-IV 列的原因。peer_tone_lag1_full 是 brokerage_network 论文声明的正文级主处理变量 (treatment): 它度量同行去年舆论对焦点银行的直接网络压力, 是被解释的经济机制的载体。peer_tone_2nd_lag1_full 则是同一论文 2SLS 的显式工具变量 (IV): 用二阶邻居 (去对角 W²) 的滞后情感作工具, 满足 Bramoullé-Djebbari-Fortin (2009) 的社会网络排他约束 —— 二阶邻居经网络间接影响焦点银行, 但 (在去对角与滞后设定下) 不直接进入焦点银行当期结果方程, 从而在结构上可作一阶同行压力的工具。二阶 IV 的横截面离散度 (std/min/max) 是弱工具诊断的直接输入: 工具的截面变异越大, 第一阶段 F 越可能强; 这正是为何 producer 在日志中专门打印 peer_tone_2nd_lag1_full 的分布作弱工具体检。多重检验纪律 (跨阶数/跨轨/跨规格并排提交时) 依 Romano & Wolf (2005) 的 stepwise 方法在根级 rwolf 模板处理, 而非在单一 over-id 检验里混装。须坦白披露样本约束: 当前盘上 T=2 (2017-2018) dev 语料在去伪零后, 一阶 peer 网仅约 32 个 bank-year 有值且全部落 2018 单截面, brokerage 2SLS 有效 N≈22 (含 DV), 在 absorb(bank_id year) 下 bank FE 饱和、不足以识别; 论文绝不在此样本声称因果, 须待 production run 扩 T≥3 且结局变量 (ROA 等) 取数后重估。

【与相邻测度的构念区分】
本家族须与三组相邻列严格划清界限, 混用会造成度量语义漂移。其一, 与嵌入网 emb_peer_tone_lag1_full/ctx/ss (及 _lg 协主孪生) 区分: 后者的网络权重 W_emb 来自银行超级文档的嵌入余弦相似度 (语义/认知邻近), 而本家族的 W 来自新闻共现频次 (同现/舆论邻近); 两者是不同的"邻近"定义, 一个问"谁和谁讲的东西像", 一个问"谁和谁被一起报道", 不可互相替代, 更不可并入同一权重矩阵。其二, 与 llm_peer_iv 模块的 llm_peer_tone_iv_* 区分: 后者是 LLM 直接判定的产品市场竞争同行的等权 (文章级 leave-out) 情感均值 IV, 同行集由 LLM 生成 (TNIC 式上限 10 家)、权重等权; 本家族同行集由新闻共现生成、权重行随机加权。两者都叫 "peer tone" 但同行定义与加权口径不同, 是刻意并排的互为稳健性工具, 不得混用, 也不得并入同一 over-id Hansen J。其三, 与 peer_fintech_exposure_lag1 区分: 后者节点值填 ln_news_coverage (声量) 而非情感, 度量的是同行金科声量溢出而非语调溢出, 与本家族共享同一 W 与同型 obs_mask 修复但节点语义不同。

【已知局限与稳健性梯子】
本家族的稳健性梯子有两条正交坐标轴, 二者都遵守同一条铁律: 各变体各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。第一条轴是传导阶数 (一阶 peer_tone_lag1 vs 二阶 peer_tone_2nd_lag1): 一阶是直接同行压力 / 主处理, 二阶是间接同行工具, 二者角色不同, 不能把一阶与二阶的滞后值塞进同一过度识别检验充当"多工具"。第二条轴是三轨文本 (full/ctx/ss): full = 标题 prepend + 全文正文, ctx = 标题 + 实体窗口, ss = 标题 + 银行金科同句窗 (ss 回退语义镜像 ctx: 无银行金科同句共现时 content_ss 回退全文 body、ss_is_fallback=True, 与 ctx 共享 n_articles 分母); 三轨各自算出的节点情感填入同一 full 口径的共现骨架, 三轨列各自 just-identified 并排, 禁混同一 Hansen J。已知的最重局限不在机械层而在选择层: obs_mask (仅对去年有有效票的同行重归一) 的求和索引集是数据可观测性 / 覆盖选择集, 而媒体覆盖与银行规模、事件强度系统相关 → 空间权重 W 的有效支撑内生于结果相关的选择变量, 违背 SLX/peer-effects 固定外生 W 的前提。须区分"行特定确定性缩放"(保外生) 与"支撑集选择性"(obs_mask 内生于覆盖, 引入选择偏误) 两回事: 去对角 W² 只守住了机械排他 (不含本行自身滞后 tone), 并不涵盖此覆盖选择问题。生产 run 因此须提供"全在网同行 / 平衡覆盖子样本"稳健性对照, 并论证在 W 条件下媒体覆盖满足 MAR (missing at random) 假设; 在 T=2 dev 上这些梯子多因单截面退化而无法有效执行, 属预期而非缺陷。综上, 本家族六列构成一个二维 (阶数 × 三轨) 的规格稳健性网格, 每一格都是一个独立的、just-identified 的度量; 论文应把它们作为"同一横向舆论传导构念在不同测量与识别选择下的一组并排证据"呈现, 而非当作可自由组合的多工具池 —— 后者会违背禁混同一 over-identified Hansen J 的铁律, 并把互为稳健性的设计误用为过度识别。

## VAR: peer_tone_lag1_full

【变体差分】
本列是家族的 canonical 主列, 也是 brokerage_network 论文的正文级主处理变量 (treatment), 家族内的所有其它列都相对本列定义其差分语义。它是一阶网络溢出 (W×tone), 采用 full 轨节点情感: 节点值 = 同行去年的 llm_vote_tone_full, 即由标题 prepend 全文正文喂给三家 LLM (gpt54nano · gemini31 · deepseekv4)、多数投票得到的银行金科报道共识语调。之所以以 full 轨作 canonical 主处理, 是因为轨道选择须与全项目 full-only 留篇门控 (2026-06-29) 一致: 一篇报道是否算作银行金科报道只由 llm_verified_full 判定, 故本列的分母口径、共现网络的边计数、n_articles 分母三者严格同源, 无需也不得借用 ctx/ss 轨的留篇集; 若改用 ctx/ss 判留篇会与全仓门控口径冲突。计算上它是 (W @ tone_obs)/denom1: W 为 t-1 年银行共现邻接经行随机标准化后的权重矩阵 (每行和为 1, 防大行凭规模主导), denom1 仅对去年有观测情感的同行列求权重和 (obs_mask 重归一, 修复早期 fillna(0) 造成的伪零衰减), 无任何观测同行则整格置 NaN (孤立银行守卫, 非伪零)。严格 lag1 意味着权重矩阵与情感向量都取去年 t-1 的值, 以规避 Manski 反射问题与同期反向因果。

本列与家族内其它列的差分沿两条正交轴界定。沿阶数轴, 本列 (一阶, 邻居的直接舆论压力) 区别于 peer_tone_2nd_lag1_full (二阶, 邻居的邻居, 去对角 W², 被用作 brokerage 2SLS 工具): 一阶是主处理、二阶是工具, 两列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。沿三轨文本轴, 本列 (full = 全文正文) 区别于 ctx 孪生 (实体窗口) 与 ss 孪生 (银行金科同句窗); 三轨的唯一差别在节点情感所用文本轨, 而网络结构 (邻接与行随机权重) 三轨共享同一 full 口径骨架、绝不逐轨重建, 三轨列亦各自 just-identified 并排、禁混同一 Hansen J。本列的横截面覆盖率被 producer 用作全家族的健康度探针 (打印 peer_tone 一阶覆盖率与分布), 覆盖率 <5% 判为极稀疏单截面退化、5%–30% 判偏稀疏、≥30% 判充分; 在 T=2 (2017-2018) dev 语料上本列极稀疏且集中于 2018 单截面, 属预期退化而非缺陷, 论文勿在此样本据本列声称因果, 须待 production T≥3 扩样重估。作为主处理变量, 本列在回归中的经济解读是: 焦点银行去年所处共现同行"舆论邻里"的整体语调, 一单位变化对本银行当年结果 (brokerage_network 的 DV 如 roa) 的边际效应即为同行舆论压力的传导强度。它与嵌入网 emb_peer_tone_lag1_full 是刻意并排的两种"邻近"操作化 (共现邻近 vs 语义邻近), 二者互为稳健性、各自 just-identified, 不得并入同一权重矩阵或同一 over-id 检验; 也与 llm_peer_tone_iv_full (LLM 判定竞争同行的等权 leave-out 均值) 定义不同的同行集与加权口径, 同属互稳而不混用。理解这些区分是正确使用本 canonical 列的前提: 凡引用"peer_tone"须明确指的是新闻共现、行随机加权、一阶、full 轨这四个坐标, 任一坐标变化即是家族内另一列。本列在实现上还是 producer 步骤 7f 的首要输出列, 合并回面板后立即被用作一阶覆盖率与分布诊断的 _primary, 其 notna 计数除以面板行数给出覆盖率判读; 若本列全缺 (无任何 bank-year 有观测同行), 则整个网络溢出模块在该 run 无有效识别力, 日志会给出极稀疏告警。因此本列不仅是主处理变量, 也是全家族数据可用性的第一道体检口。

## VAR: peer_tone_2nd_lag1_full

【变体差分】
本列是二阶网络溢出 (W²×tone) 的 full 轨, 也是 brokerage_network 论文 2SLS 的显式工具变量 (IV), 是本家族里唯一被直接声明为结构工具的 full 轨列。与 canonical 一阶列 peer_tone_lag1_full 的唯一构念差别是传导阶数: 一阶度量"直接邻居"的舆论压力, 本列度量"邻居的邻居"的间接传导。计算为 (W2 @ tone_obs)/denom2, 其中 W2 = W·W 再 np.fill_diagonal(W2, 0.0) 去掉对角自反馈, denom2 = W2 对观测同行的权重和 (与一阶同口径的 obs_mask 重归一, 使标度为"二阶邻居加权均值"而非旧的"路径概率加权和")。去对角是把本列用作工具的排他性前提: 若保留 W² 对角, 工具会含本行自身的滞后 llm_vote_tone_full (二阶路径 i→j→i 的回流), 违背排他约束、令工具与被工具化的内生变量直接相关; 去对角后二阶邻居仅经网络间接触及焦点银行, 满足 Bramoullé, Djebbari & Fortin (2009) 通过社会网络识别 peer 效应所要求的、二阶邻居须剔除经 W² 回流到自身的路径这一排他条件。

须精确披露本列的标度语义, 这是它区别于一阶列的又一细节: W² 去对角后行和不再恒为 1, 故本重归一是对工具的逐观测 (row-specific) 确定性变换, 不是全局标量缩放; 2SLS 仅对工具集的全局非奇异线性变换不变, 行特定除数会改变工具的截面变异、第一阶段系数与 F 统计量 (omni-g-net-spill-06 勘误明确否定了旧注"相关性不变")。正因如此, 本列的横截面离散度 (std/min/max) 直接是弱工具诊断输入 —— 离散度越大, 第一阶段越可能强; producer 专门打印本列分布作弱工具体检。节点情感轨为 full (标题 prepend 全文正文), 与 ctx/ss 二阶孪生的差别仅在此文本轨, 而 W、W² 与 obs_mask 骨架三轨共享 full 口径。本列 (二阶 IV) 与一阶主处理列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 与本列同型的覆盖选择性局限 (obs_mask 内生于媒体覆盖, W 有效支撑内生于结果相关选择变量) 与一阶列同病根, 去对角只守机械排他、不涵盖覆盖选择, 生产 run 须配"全在网同行 / 平衡覆盖子样本"对照并论证 MAR。

作为工具变量, 本列的排他性论证链须在论文中完整披露: 一阶主处理 peer_tone_lag1_full 度量直接同行去年舆论压力 (内生, 因焦点与直接同行可能受共同冲击、共享报道), 本列 (二阶邻居去对角滞后舆论) 经网络间接作用于焦点银行, 剩余识别假设是"二阶邻居 t-1 的舆论仅经一阶同行渠道影响焦点银行 t 期结果、不经其它直接路径"。这一假设的可信度取决于网络的稀疏与去对角的彻底; 去对角 W² 已机械保证工具不含本行 i→j→i 回流的自身滞后情感, 但不能排除二阶邻居与焦点银行共享未观测冲击的经济路径, 故本列须与一阶主处理并排报告首阶段 F、并在生产样本上做过度识别与弱工具稳健性检验 (多重检验按 Romano-Wolf stepwise 纪律)。T=2 dev 上本列因单截面退化横截面变异极弱、首阶段不可识别, 属预期而非缺陷, 论文勿据此声称因果。最后须与家族内其它工具语义划清: 本列 (二阶、full) 只是 identification.iv 声明工具集的 full 轨主工具, ctx/ss 二阶孪生是其轨道稳健性对照工具, 三者各自 just-identified、不得并列进同一 over-id 检验充当多工具集; 与嵌入网二阶溢出、以及 llm_peer_iv 的等权 leave-out IV 亦是刻意并排的不同识别策略, 全部互为稳健性、互不混装。

## VAR: peer_tone_2nd_lag1_ctx

【变体差分】
本列是二阶网络溢出 (W²×tone) 的 ctx 轨, 与 core 的 full 二阶列 peer_tone_2nd_lag1_full 构念完全同型 (都是"邻居的邻居"舆论传导、都用去对角 W²、都作 brokerage 2SLS 工具并须满足排他约束), 唯一差别是节点情感所用文本轨。本列的节点值取同行去年的 llm_vote_tone_ctx, 即由标题 prepend 加实体上下文窗口 (银行 / 金科实体附近的正文片段, 而非整篇) 喂三家 LLM 投票得到的共识语调; 相比 full 轨读全文, ctx 轨把节点情感聚焦在实体邻近文本, 削弱与主题无关的正文噪声对语调判定的干扰, 因而作 full 二阶 IV 的轨道稳健性对照。ctx 轨作为 conditional-on-full 的测度 / 稳健性轨, 其行宇宙是 full 留篇集的子集 (留篇门控恒为 full-only, 2026-06-29): 一篇报道是否留篇仍由 llm_verified_full 判定, ctx 只在留下的篇子集上重新给节点算 tone, per-track 列照算。计算链路与 full 二阶列逐字一致: W2 = W·W 再去对角, denom2 对观测同行重归一, 严格 lag1, 逐观测确定性重归一 (行和非 1、非全局缩放)。关键: 网络结构 (共现邻接与行随机权重 W、W²) 三轨共享同一 full 口径骨架, 本列只在填充节点情感向量时换用 ctx 轨的 tone, 绝不重建邻接。本列被列为 core (而非 standard) 是因 brokerage_network 的 identification.iv 把 primary / fallback 工具全收, ctx 轨孪生亦在声明的工具集内。须强调本列相对 full 二阶主工具的定位: 二者度量的是完全相同的"二阶邻居去年舆论"构念, 只在节点情感取全文 (full) 还是取实体邻近窗 (ctx) 上分叉, 因而是节点测量文本轨的稳健性对照, 而非另一个可与 full 二阶工具并列进同一 over-id 检验的独立工具; 二者各自 just-identified、互为稳健性不分主次。若把 full 与 ctx 二阶 IV 塞进同一 Hansen J 充当双工具, 会误把高度相关的同构念测量当作过度识别信息, 违反家族铁律。标度语义与 full 二阶列同型 (W² 去对角行和非 1、denom2 逐观测重归一为 row-specific 确定性变换), 故本列首阶段 F 与 full 二阶列须各自体检、不可假定相等。它与 full/ss 二阶孪生、以及一阶各列, 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J —— 三轨属规格稳健性并排, 二阶与一阶属工具与主处理的角色区分, 均不得塞入同一过度识别检验。作为 identification.iv 声明工具集内的 ctx 轨孪生, 本列的具体用途是: 当 full 二阶 IV 因全文噪声或某些年度覆盖问题表现不稳时, 以实体邻近语境的 ctx 节点情感重算二阶工具, 检验第一阶段强度与 2SLS 系数对节点情感文本轨的敏感性; 若 full 与 ctx 二阶 IV 给出方向一致、量级相近的估计, 则同行舆论传导的识别不依赖具体文本轨的选择, 增强结论稳健性。排他性论证 (二阶邻居仅经一阶同行渠道起作用) 与 full 二阶列完全同型, 去对角 W² 亦已守住机械排他 (不含本行自身滞后 ctx 情感)。标度语义亦同型: W² 去对角后行和非 1, denom2 的逐观测重归一是 row-specific 确定性变换非全局缩放, 会改变工具的截面变异与首阶段 F, 故本列与 full 二阶列的横截面离散度不可假定相等, 须各自体检。覆盖选择性局限 (obs_mask 内生于媒体覆盖) 与 full 二阶列同病根, 去对角只守机械排他不涵盖覆盖选择, 生产须配平衡覆盖子样本对照并论证 W 条件下 MAR。本列 tier=core 而非 standard, 正是因为它被 identification.iv 收入声明工具集; 若某分析只用 full 二阶主工具, 本列则退居轨道稳健性角色。T=2 dev 语料上本列因单截面退化而覆盖极稀疏、横截面变异弱、首阶段不可识别, 属预期而非缺陷, 须待生产 T≥3 扩样重估。

## VAR: peer_tone_2nd_lag1_ss

【变体差分】
本列是二阶网络溢出 (W²×tone) 的 ss 轨, 与 full/ctx 二阶孪生构念同型 (都是"邻居的邻居"传导、都用去对角 W² 满足工具的排他约束), 差别仅在节点情感文本轨: 节点值取同行去年的 llm_vote_tone_ss, 即由标题 prepend 加"银行与金科同句 ±N 窗"共现片段 (config/filtering.yaml::context_window.ss_sentence_radius, 默认 1) 喂三家 LLM 投票得到的共识语调。ss 轨回退语义严格镜像 ctx: 当某篇报道无银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 而非丢篇。ss 是三轨中语义最严的一轨 (要求银行与金科在同一句共现), 因而是对"节点情感是否只由银行金科紧邻语境驱动"最严的稳健性检验, 作 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集 (留篇仍由 llm_verified_full 判定, 2026-06-29)。计算链路 (W2 = W·W 去对角、obs_mask 重归一、逐观测确定性重归一、严格 lag1) 与 full 二阶列一致, 网络骨架仍共享 full 口径的邻接与权重, 本列只换节点情感向量为 ss 轨。本列 tier=standard (非 core), 因其定位是稳健性并排而非主 IV 声明入口 (identification.iv 声明的 primary/fallback 未把 ss 二阶收为主工具)。它与家族内其它阶数 / 轨道变体各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。在 T=2 dev 上, ss 轨因同句共现要求更严, 常出现零方差或全 NaN 退化, 属预期而非缺陷; 生产 T≥3 扩样后方能提供有效横截面变异。

## VAR: peer_tone_lag1_ctx

【变体差分】
本列是一阶网络溢出 (W×tone) 的 ctx 轨, 与 canonical 主列 peer_tone_lag1_full 构念同型 (都是直接同行舆论压力、行随机加权同行均值、严格 lag1), 唯一差别是节点情感文本轨: 节点值取同行去年的 llm_vote_tone_ctx, 即标题 prepend 加实体上下文窗口 (银行 / 金科实体附近正文片段) 喂三家 LLM 多数投票得到的共识语调, 而非 full 轨读全文。相对 full canonical, ctx 把节点情感聚焦在实体邻近语境, 削弱无关正文噪声, 作主处理的轨道稳健性对照。ctx 作 conditional-on-full 的测度 / 稳健性轨, 行宇宙是 full 留篇集子集 (留篇门控恒 full-only, 2026-06-29, 留篇仍由 llm_verified_full 判定, ctx 只在留下的篇上重算节点 tone)。计算为 (W @ tone_obs)/denom1, W 为 t-1 年共现邻接的行随机标准化矩阵, obs_mask 仅对去年有观测情感的同行重归一 (修复早期 fillna(0) 的伪零衰减), 无观测同行置 NaN (孤立银行守卫); 网络结构 (邻接与行随机权重) 三轨共享同一 full 口径骨架, 本列只换节点情感向量为 ctx 轨、绝不重建邻接。本列 tier=standard, 定位是一阶主处理列 (full) 的轨道稳健性并排, 而非主 treatment 声明入口。它与 full/ss 一阶孪生、以及二阶各列, 各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J —— 一阶 (直接压力) 与二阶 (工具) 属不同角色, 三轨属规格稳健性并排, 均不得塞入同一过度识别检验。T=2 dev 上 ctx 一阶轨常因单截面退化而覆盖稀疏, 属预期, 须待生产 T≥3 扩样重估。

## VAR: peer_tone_lag1_ss

【变体差分】
本列是一阶网络溢出 (W×tone) 的 ss 轨, 与 canonical 主列 peer_tone_lag1_full 构念同型 (都是直接同行舆论压力、行随机加权同行均值、严格 lag1), 差别仅在节点情感文本轨: 节点值取同行去年的 llm_vote_tone_ss, 即标题 prepend 加"银行与金科同句 ±N 窗"共现片段 (ss_sentence_radius 默认 1) 喂三家 LLM 多数投票得到的共识语调。ss 是三轨中语义最严的一轨, 要求银行与金科在同一句共现, 故本列度量的是"当节点情感只由银行金科紧邻同句语境驱动时, 同行舆论压力是否依然成立"的最严稳健性版本。ss 轨回退语义严格镜像 ctx: 无银行金科同句共现的报道, content_ss 回退全文 body、ss_is_fallback=True, 与 ctx 共享 n_articles 分母而非丢篇。ss 作 conditional-on-full 稳健性轨, 行宇宙为 full 留篇集子集 (留篇仍由 llm_verified_full 判定, 2026-06-29)。计算链路 (W 行随机标准化、obs_mask 仅对观测同行重归一、无观测同行置 NaN、严格 lag1) 与 full 一阶列一致, 网络骨架 (邻接与权重) 仍共享 full 口径, 本列只换节点情感向量为 ss 轨。本列 tier=standard, 定位是一阶主处理列的轨道稳健性并排, 而非主 treatment 声明入口。它与 full/ctx 一阶孪生及二阶各列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。在 T=2 dev 上, ss 一阶轨因同句共现要求更严, 常见零方差或全 NaN 退化, 属预期而非缺陷; 生产 T≥3 扩样后方提供有效横截面变异, 论文勿在当前样本据此列声称因果。

<!-- rendered-citations:begin -->
Aksoy-Yurdagul, D., Buchner, A., & Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, 112803. https://doi.org/10.1016/j.econlet.2025.112803
Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. Journal of Corporate Finance, 93, 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. Journal of Banking & Finance, 171, 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review, 64, 101234. https://doi.org/10.1016/j.ememar.2024.101234
Ahmad, M., Hall, S. G., Law, S. H., & Nayan, S. (2024). Spillover effects in the nexus of finance-institutions-growth: New insights from spatial Durbin analysis on emerging economies. International Journal of Finance & Economics, 30(3), 2470-2491. https://doi.org/10.1002/ijfe.3025
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms: Aggregating investor perceptions through internet co-searches. Journal of Financial Economics, 116(2), 410-431. https://doi.org/10.1016/j.jfineco.2015.02.003
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Klaucke, K. (2025). Text Spillover: Measuring connectedness of financial institutions based on news text data. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2024.102307
<!-- rendered-citations:end -->
