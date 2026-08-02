---
family_id: F550
columns:
- tech_frac
- tech_frac_lc
- tech_frac_ls
unit: 比率/占比 (proportion, 取值域 [0,1]; 分母为零时置 NaN)
formula: "tech_frac = n_articles_tech / n_articles_llm_valid (full 轨); 分子 = 该银行-年内 innovation_locus_full == '底层技术' 的文章数, 分母 = full 轨 LLM 判定有效篇数。_lc 变体换 innovation_locus_ctx 分子配 n_articles_llm_valid_ctx 分母; _ls 变体换 innovation_locus_ss 分子配 n_articles_llm_valid_ss 分母。"
producer: pipeline/panel/encode.py (locus 分类维度 bank-year 聚合)
upstream:
- 21_tone_llms.parquet (innovation_locus_full / innovation_locus_ctx / innovation_locus_ss + n_articles_llm_valid{,_ctx,_ss})
- 40_panel_yearly.parquet
citations:
- doi: 10.1287/mnsc.2024.04608
  type: journal
  authors: He, Z., Jiang, S., Xu, D., & Yin, X.
  year: 2026
  title: "Investing in lending technology: IT spending in banking"
  venue: Management Science
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: "Investing in fintech equity and bank innovation"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 108
  pages_or_artno: 102306
- doi: 10.1016/j.techfore.2026.124581
  type: journal
  authors: Dehghani, M. A., Brauneis, A., & Karavidas, D.
  year: 2026
  title: "Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions"
  venue: Technological Forecasting and Social Change
  vol: 226
  pages_or_artno: 124581
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2023.02555
  type: journal
  authors: Ahnert, T., Doerr, S., Pierri, N., & Timmer, Y.
  year: 2026
  title: "Information technology in banking and entrepreneurship"
  venue: Management Science
  vol: 72
  issue: 3
  pages_or_artno: 1796-1813
- doi: 10.1016/j.jfineco.2024.103957
  type: journal
  authors: Vives, X., & Ye, Z.
  year: 2025
  title: "Information technology and lender competition"
  venue: Journal of Financial Economics
  vol: 163
  pages_or_artno: 103957
- doi: 10.1086/727712
  type: journal
  authors: Lerner, J., Seru, A., Short, N., & Sun, Y.
  year: 2024
  title: "Financial innovation in the twenty-first century: Evidence from US patents"
  venue: Journal of Political Economy
  vol: 132
  issue: 5
  pages_or_artno: 1391-1449
- doi: 10.1016/j.jfi.2024.101101
  type: journal
  authors: Kutzbach, M. J., & Pogach, J.
  year: 2024
  title: "Financial technology and relationship lending: Complements or substitutes?"
  venue: Journal of Financial Intermediation
  vol: 59
  pages_or_artno: 101101
- doi: 10.1016/j.jmoneco.2022.04.001
  type: journal
  authors: Pierri, N., & Timmer, Y.
  year: 2022
  title: "The importance of technology in banking during a crisis"
  venue: Journal of Monetary Economics
  vol: 128
  pages_or_artno: 88-104
- doi: 10.1257/aeri.20190499
  type: journal
  authors: Kelly, B., Papanikolaou, D., Seru, A., & Taddy, M.
  year: 2021
  title: "Measuring technological innovation over the long run"
  venue: "American Economic Review: Insights"
  vol: 3
  issue: 3
  pages_or_artno: 303-320
- doi: 10.1287/mnsc.2020.3682
  type: journal
  authors: Bellstam, G., Bhagat, S., & Cookson, J. A.
  year: 2021
  title: "A text-based analysis of corporate innovation"
  venue: Management Science
  vol: 67
  issue: 7
  pages_or_artno: 4004-4031
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: International Review of Economics & Finance
  vol: 74
  pages_or_artno: 468-483
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: The Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: Strategic Management Journal
  vol: 31
  issue: 3
  pages_or_artno: 306-333
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是银行金融科技报道中"创新落点"(locus of innovation) 维度上偏向底层技术一侧的相对强度, 面板列基名为 tech_frac。构念直接承接 Gomber 等 (2018) 对金融科技革命的解剖框架: 金融科技既可以表现为对底层技术基础设施 (区块链、人工智能、云计算、大数据、分布式账本等) 的投入与叙事, 也可以表现为对应用场景 (支付、信贷、财富管理、保险、理财等面向终端用户的业务形态) 的部署与叙事。前者是"技术在何处发生"这一问句里指向底层能力构建的一端, 后者指向业务落地的一端。tech_frac 正是把每一篇银行-金融科技报道经大语言模型判入"底层技术"或"应用场景"两类之后, 在银行-年 (bank-year) 面板格内计算落入底层技术一类的报道占该格内有效判定报道总数的比例。它回答的问题是: 在给定银行、给定年份被媒体报道的金融科技活动中, 有多大份额被叙述为指向底层技术能力, 而非单纯的应用场景铺开。

数据来源与文章级前置。每篇进入面板的文章先经三轨文本物化 (full/ctx/ss) 与 stage 21 情感与分类大语言模型处理, 产出文章级 innovation_locus_full / innovation_locus_ctx / innovation_locus_ss 三列, 取值为"底层技术"或"应用场景"的中文类别标签 (亦可为空表示该轨未判出)。locus 判定与情感判定同源于 stage 21 的多模型投票, 但属于分类通道而非情感通道: 它衡量报道内容"讲的是什么层面的金融科技", 与讲得"好不好"(情感 tone) 正交。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否被计为"一篇银行金融科技报道"只看 full 轨的 llm_verified_full 是否为真; ctx 与 ss 轨在此被降格为 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集合的子集, 但每条轨道各自的分子分母仍按本轨口径独立计算, 不借用 full 轨的分母。

为什么要把创新落点拆成底层技术与应用场景两端, 而不是笼统数金融科技报道的多寡, 这是本家族区别于纯曝光度量的关键。用大白话讲: 同样是"某银行搞金融科技"的一条新闻, 一种是讲这家银行自己建了区块链底座、上了大模型、铺了云原生核心系统这类地基性的技术能力, 另一种是讲这家银行开了个手机支付入口、上线了一款理财 App、推了个线上贷款产品这类面向用户的应用。两者对银行未来的技术积累、专利产出、长期竞争力的含义差别很大: 地基性投入往往前瞻性更强、更难被竞争对手快速复制, 应用铺开则见效快但技术护城河浅。tech_frac 就是把一家银行某一年被媒体讲到的金融科技活动里"讲地基"的那一份额单独拎出来。它不是数金融科技报道有多少条 (那是曝光度 attention 家族的事), 也不是判金融科技报道说得好不好 (那是情感 tone 家族的事), 而是判这些报道的落点结构偏向哪一端。

计量单位与取值域。tech_frac 是一个无量纲的份额, 取值域为闭区间 [0,1]: 值为 0 表示该银行-年内有效判定的金融科技报道全都被归为应用场景 (或残余未归类), 值为 1 表示全都被归为底层技术。当该银行-年内没有任何有效 LLM 判定报道 (分母为零) 时, tech_frac 取 NaN 而非 0, 以区分"无信息"与"确有报道但零底层技术份额"两种本质不同的情形 —— 这一 NaN 语义在下游二元化与回归样本筛选时至关重要, 把无信息格错置为零会人为拉低底层技术主导的银行-年比例。

【方法学与计算】
canonical 列 tech_frac 的计算落在 pipeline/panel/encode.py 的 locus 分类聚合块内。第一步按 target_bank × year 分组, 对 innovation_locus_full == '底层技术' 的文章计数得 n_articles_tech, 对 '应用场景' 计数得 n_articles_app; 两者经 merge 后回填缺失为零并转整型。第二步取 full 轨有效判定分母 n_articles_llm_valid (该银行-年内 LLM 情感/分类判定有效的报道篇数), 当分母大于零时令 tech_frac = n_articles_tech / n_articles_llm_valid, 分母为零时置 NaN。同一分母下并行产出 app_frac = n_articles_app / n_articles_llm_valid。构造上 tech_frac 与 app_frac 并非互补到 1 的严格二分: 恒等式校验以放宽后的口径核对, 允许存在既非底层技术亦非应用场景的残余判定 (与 collab 维度按 R6 放宽的处理一致)。这一点在解读时须谨记: tech_frac 不能简单地由 1 减 app_frac 复原。

由 tech_frac 衍生的下游还包括语调差距 tone_gap_tech_app, 即在 min-n≥5 的合格 cell 内取底层技术类内 LLM 投票情感均值减去应用场景类内均值 (正值表示底层技术报道更乐观), 该量是 P4 locus 的一个 headline 情感测度, 与 tech_frac 的占比构念互补但不同层。tech_frac 本身是纯份额量, 不含情感符号。

分类判定的多模型共识机制值得展开。文章级 innovation_locus 标签并非某单一模型的输出, 而是 stage 21 三家大语言模型 (gpt54nano 与 gemini31 经 OpenLux 路由、deepseekv4 直连 api.deepseek.com) 投票后的共识: 先各家给出 locus 判定, 再经 verified 门控 (剔除未通过银行金融科技留篇校验的判定)、final_v 清票 (统一有效票口径) 与 locus 关键词回退 (当模型未明确判类时以底层技术/应用场景关键词命中作兜底) 三层处理, 取多数结果作为共识标签。因此本家族的 tech_frac 是"共识轨"的份额, 与各家单独判定的 per-model 份额 (家族 F181 的 gpt54nano/gemini31/deepseekv4 各自 tech_frac_full) 有别; 共识 ≠ 裸多数票, 因为其间插入了门控与回退。这一设计的效度依据见 Carlson 与 Burbano (2026): 用大语言模型标注管理学数据时, 多模型交叉与一致性报告是抵御单模型幻觉与系统性偏置的必要环节。

聚合层的实现细节还包括对 merge 后缺失的处理与恒等式核对。分组计数经 pandas merge 回面板后, n_articles_tech / n_articles_app 的缺失被回填为零并转整型 (无该类报道即计零), 随后才做除法得份额。恒等式校验以 n_articles_llm_valid 为分母对 n_articles_tech 与 n_articles_app 之和做放宽口径核对 (与 collab 维度按 R6 放宽一致), 允许存在既非底层技术亦非应用场景的残余判定, 因此 tech_frac + app_frac 不必等于 1。这一放宽是刻意的: 二分类的严格互补会把模型的"无法归类"强行摊入某一侧, 反而引入噪声。

【文献定位】
tech_frac 服务于把"金融科技创新的落点结构"从非结构化中文新闻文本中量化出来这一测量任务, 属于以文本为基础度量企业创新的方法学谱系。Bellstam、Bhagat 与 Cookson (2021) 用分析师报告的文本相似度构造企业创新的文本代理, 证明文本信号能捕捉专利与研发之外的创新信息; Kelly、Papanikolaou、Seru 与 Taddy (2021) 以专利文本的新颖度与影响力构造长跨度技术创新指标, 说明"什么算技术性创新"可以从语料的语义结构中读出。本家族把这一思路迁移到中文银行新闻: 用大语言模型对每篇报道做 locus 归类, 再在银行-年层聚合成份额。Carlson 与 Burbano (2026) 对在管理学研究中用大语言模型标注数据给出方法学指引与警示, 正是 tech_frac 这类 LLM 派生测度须正视的效度基础 —— 标注一致性、跨模型稳健性、分母口径都需交代清楚。

在金融科技实体经济学一侧, 底层技术投入与应用场景铺开的区分具有实质经济含义。He、Jiang、Xu 与 Yin (2026) 度量银行的贷款技术 IT 支出, Pierri 与 Timmer (2022) 证明危机中技术密度高的银行表现更稳健, Vives 与 Ye (2025) 刻画信息技术如何重塑放贷竞争, Ahnert、Doerr、Pierri 与 Timmer (2026) 把银行 IT 与创业活动联系起来 —— 这些工作共同表明"银行在底层技术上投入几何"是一个独立于其零售应用铺开的经济维度。Kutzbach 与 Pogach (2024) 进一步辨析金融科技与关系型放贷是互补还是替代, 呼应 locus 二元对照的必要性。Lee、Li、Yu 与 Zhao (2021) 以中国银行业为样本证明金融科技创新提升银行效率, 与本项目样本 (中国银行新闻语料) 直接同域。Chen、Wu 与 Yang (2019) 评估金融科技创新的价值, Alfhaili、Bakoush 与 Wolfe (2026) 与 Dehghani、Brauneis 与 Karavidas (2026) 分别从股权投资和专利/开放式创新角度审视银行的金融科技创新, Lerner、Seru、Short 与 Sun (2024) 以美国专利刻画二十一世纪金融创新的版图。理论落点上, Adner 与 Kapoor (2010) 关于技术互依结构如何决定企业绩效的创新生态框架, 为"底层技术 vs 应用场景"这一分层提供了产业组织层面的理据: 底层技术处于价值创造链条的上游组件位置, 其叙事强度与应用场景的叙事强度捕捉的是生态位上不同的信号。

把这些文献串起来看, tech_frac 在因果链上的位置是一个前置的"叙事结构"信号, 它先于并可能预示后置的技术产出。He 等 (2026) 与 Pierri 与 Timmer (2022) 关心的是银行实际的 IT/技术投入及其绩效后果, Lerner 等 (2024) 与 Kelly 等 (2021) 关心的是技术创新的最终产出 (专利及其影响力), 而本项目关心的是介于两者之间、公开可观测且高频的一层: 媒体如何叙述银行的金融科技落点。这一层的价值在于, 在专利授权、财报 IT 支出这类低频、滞后、且往往被战略性披露扭曲的硬指标之外, 提供一个基于第三方媒体、逐年更新的软信号。P4 的核心检验正是问: 底层技术主导的媒体叙事 (locus_layer_full) 是否前瞻性地对应更高的引用加权专利产出 (citation_weighted_patent)。若成立, 则 tech_frac 捕捉到的叙事结构是银行真实技术积累的一个先行指标; 若不成立或反向, 则提示媒体叙事可能更多反映公关姿态而非实质投入 —— 这本身也是有价值的发现。Bellstam 等 (2021) 与 Carlson 与 Burbano (2026) 的方法学工作在此提醒: 任何基于文本的创新代理都须先过效度关, 交代其与硬指标的相关性及测量误差结构。

【识别策略定位】
tech_frac 是论文 bank_fintech_locus (P4) 的处理变量家族的核心构造原料。P4 的主处理并非直接以 tech_frac 连续值入回归, 而是由 tech_frac 与 app_frac 二元化得到一对指示变量: locus_layer_full = (tech_frac > app_frac) 表示该银行-年报道以底层技术为主导, locus_scenario_full = (app_frac > tech_frac) 表示以应用场景为主导 (平票即 tech_frac == app_frac 时两者均为缺失/零, 值域已补齐)。这对 primary_pair 由 Stata 侧 01_data_prep.do 从面板真实列 tech_frac / app_frac 推导, 不落 parquet。主假设为 locus_layer_full → citation_weighted_patent (银行固定效应 + 年份固定效应), 即底层技术主导的媒体叙事是否前瞻性地对应更高的引用加权专利产出。识别层面 P4 配备同业留一 (leave-one-out) 工具 leave_one_out_peer_locus_iv (同银行类型×年的同业 tech_frac 均值, 剔除本行自身) 处理媒体叙事与银行创新的联立性, 并辅以 Bartik 与媒体来源 house-style 暴露两类工具作为并排稳健性引擎。三轨各配自己的同业 LOO 工具 (full 轨 leave_one_out_peer_locus_iv、ctx 轨 lpeer_locus_iv_ctx、ss 轨 lpeer_locus_iv_ss), 每轨各自 just-identified, 严禁跨轨拼成过度识别检验。这套识别设计的经济逻辑是: 媒体对某银行金融科技落点的叙述强度既可能反映其真实技术投入 (我们想估计的通道), 也可能被该银行自身的绩效、专利、公关活动反向驱动 (内生通道); 用同类同业在同一年的平均底层技术叙事作工具, 借助行业层面共同的技术叙事潮流 (如某年区块链/大模型成为全行业热词) 作为对个体银行外生的冲击, 从而剥离反向因果。这与 shift-share/Bartik 工具的思想一脉相承。

在结果层面, P4 还把 tech_frac 与网络溢出联系起来: 底层技术主导的银行往往处于跨群知识经纪 (between centrality) 的位置, 经由 bank_between_cent 这类结构指标传导到 citation_weighted_patent, 构成一条从叙事落点经网络位置到技术产出的机制链。这条机制检验与主回归并列, 不改变 tech_frac 作为处理变量原料的核心地位。

【与相邻测度的构念区分】
须严格区分本家族与三组相邻测度。其一, tech_frac 与 substantiveness 维度的 sub_frac (家族 F511) 正交: locus 问的是"技术落在底层还是应用", substantiveness 问的是"报道是实质性举措还是象征性表态", 两者是 W&Z 实质性框架与 Gomber locus 框架的不同轴。其二, tech_frac 与 collab 维度的 collab_frac (家族 F159) 正交: 后者刻画自主研发 vs 开放协作 (Chesbrough 开放式创新)。三维分类共享同一批 stage 21 判定但走各自的解析键 (LLM_CLASS_SPEC 三元映射把文章级基名 locus 映射到面板 metric 基名 tech_frac, 二者无字符串变换可达, 该映射是唯一互锁点)。其三, tech_frac 与其 per-model 跨厂商孪生族 (gpt54nano/gemini31/deepseekv4 各自的 tech_frac_full, 家族 F181) 区分: 本家族是三家投票共识轨 (verified 门控 + final_v 清票 + locus 关键词回退后的多数判定), per-model 族是各家单独判定的跨厂商稳健臂。共识 ≠ 裸多数票。此外还须与曝光度家族划清: tech_frac 的分母 n_articles_llm_valid 虽与曝光度量共享"报道数"这一原料, 但 tech_frac 是份额而非计数, 它对报道总量的水平不敏感 —— 一家银行无论被报道 5 篇还是 500 篇, 只要其中底层技术报道占比相同, tech_frac 就相同。这正是把 locus 落点从曝光强度中剥离出来的构念意图: 我们要问的是叙事的"结构组成", 不是叙事的"体量大小"。体量大小由 attention 家族的 ln_coverage、attention_pct 等列承担, 与本家族正交并列, 二者在回归中可同时入模而不冲突。把结构与体量分列, 也让研究者能分别检验"银行被讲得多"与"银行被讲的是地基还是应用"这两个各自独立的经济假设, 而不至于把两种截然不同的信息混为一谈。

【已知局限与稳健性梯子】
tech_frac 的三轨结构 (full 无后缀 / ctx 的 _lc / ss 的 _ls) 构成本家族的规格稳健性梯子。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨列混进同一 over-identified 的 Hansen J 过度识别检验 —— 这是三轨、co-primary 双轨嵌入、per-model、各类梯子共同的铁律。full 轨是 canonical 主轨 (P4 treatment 主处理), ctx (_lc) 与 ss (_ls) 是 conditional-on-full 的稳健性轨。已知局限有三: 其一, locus 判定继承大语言模型分类的测量误差, 须以 Carlson 与 Burbano (2026) 所倡的跨模型一致性 (Krippendorff α / Cohen κ) 佐证效度; 其二, 分母 n_articles_llm_valid 在小样本银行-年 (早期试跑 T=2 样本) 下可能很小, 导致 tech_frac 方差偏大, 生产 T=19 全量语料下稳定; 其三, tech_frac 与 app_frac 因存在残余未归类而非严格互补, 二元化时须显式处理平票与双缺失。稳健性叙事上, 除三轨梯子外还有 per-model 跨厂商孪生、同业 LOO/Bartik/outlet 三引擎工具、以及基于 tone_gap_tech_app 的情感差距侧向验证, 共同支撑 locus 落点构念不被单一测量选择驱动。

最后须交代金字塔式的稳健性梯子彼此正交、互不交叉这一原则。tech_frac 的稳健性来自若干条相互独立的梯子: 三轨梯子 (full/ctx/ss) 改变的是文本取材范围, per-model 梯子 (三家 LLM) 改变的是分类判定的模型来源, 工具变量三引擎改变的是识别外生冲击的构造方式。每条梯子内部的各臂互为稳健性、不分主次、各自 just-identified 并排, 梯子之间则正交组合而非笛卡尔式相乘展开 (避免列数爆炸), 这与政治词权重梯子、词典消融梯度、co-primary 嵌入双轨等本项目其他稳健性设计遵循同一套纪律。真正的跨模型族错误率控制 (FWER) 由根级 rwolf 模板承担, 而非在 tech_frac 自身层面做多重比较校正 —— locus 三轨与三家模型属规格稳健性并排, 镜像政治词权重与词典消融先例, 跨模型 rwolf 仅覆盖同构念替代 headline 测量, 不适用于把本族三轨强行并入同一联合检验。理解这一层纪律, 才能正确解读 tech_frac 家族三列并存的意义: 它们不是三个独立假设, 而是同一 locus 落点构念在三种测量选择下的稳健性映像。

## VAR: tech_frac

【变体差分】
本列是家族 canonical 主列, tier=core, 对应论文 bank_fintech_locus (P4) 的核心处理变量原料。轨道 = full (标题 prepend + 全文正文), 无轨道后缀即代表 full 轨, 这是留篇门控 full-only 口径 (2026-06-29) 下唯一决定"是否计为一篇银行金融科技报道"的判定轨。分子 = 该银行-年内 innovation_locus_full 判为"底层技术"的文章数 n_articles_tech; 分母 = full 轨 LLM 有效判定篇数 n_articles_llm_valid; 分母为零置 NaN。相对于同家族两个变体列, 本列的差分点在于: 分子分母同取 full 轨, 不做实体窗口 (ctx) 或同句共现 (ss) 的收窄, 因此覆盖每篇留篇报道的全文语义, 是三轨中信息面最宽、也是 P4 主回归实际消费的一轨。

本列不直接以连续值进入 P4 主回归, 而是先与 app_frac 比较二元化: locus_layer_full = (tech_frac > app_frac) 表示底层技术主导, locus_scenario_full = (app_frac > tech_frac) 表示应用场景主导, 平票 (tech_frac == app_frac, 含两者皆为零或皆缺失) 时两指示均取零/缺失以避免把无信息格误判为某一侧。这对 primary_pair (locus_layer_full 与 locus_scenario_full) 由 Stata 01_data_prep.do 从本列与 app_frac 现算, 不落 parquet —— 这是刻意的设计: 二元 treatment 配二元对照, 契合 P4 "一篇论文两个处理指标" 的 locus pair 结构, 也规避了在年度数据约束下连续 tech_frac 方差不足的问题。须注意旧式表述"1 if innovation_locus_full == '底层技术'"引用的是文章级字符串, 不在 bank-year 面板内, 正确的推导必须走本列与 app_frac 的比较。主假设 locus_layer_full → citation_weighted_patent 在银行固定效应加年份固定效应下估计, 检验底层技术主导的媒体叙事是否前瞻对应更高引用加权专利。collab_mode 维度仅作 robustness control (Table 5 备择规格), 主回归保持 locus pair 作 treatment。

与三个稳健性维度须严格区分: 本列 (locus) 与 sub_frac (substantiveness, 实质 vs 象征)、collab_frac (自主 vs 协作) 各测创新的不同轴, 三维共享 stage 21 判定但走各自解析键。LLM_CLASS_SPEC 三元映射把文章级基名 locus 映射到面板 metric 基名 tech_frac、目标类"底层技术"、解析键 innovation_locus 三者, 文章级基名与面板 metric 基名之间无字符串变换可达 (locus 不能机械变形为 tech_frac), 该映射是两命名域唯一的互锁点, 改动任一侧须同步映射。本列的共识判定是三家 LLM 投票 (gpt54nano/gemini31/deepseekv4) 经 verified 门控、final_v 清票与 locus 关键词回退后的多数结果, 区别于其 per-model 跨厂商孪生 tech_frac_full 族 (各家单独判定, 家族 F181): 共识不是裸多数票, 因其间插入门控与回退。

识别上本列配同业留一工具 leave_one_out_peer_locus_iv (同银行类型×年同业 tech_frac 均值, 剔除本行自身), 处理媒体叙事与银行创新之间的联立性 —— 一家银行专利多可能反过来招致更多底层技术报道, 留一工具用同类同业的叙事强度作外生冲击隔离这一反向通道。此外并排配备广义 Bartik 工具与媒体来源 house-style 暴露工具, 三引擎各自 just-identified、互为稳健。

铁律: 本列与其 ctx (_lc)、ss (_ls) 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J; 与 per-model 孪生、政治词权重梯子、co-primary 嵌入双轨同受此铁律约束 —— 把互为稳健性的并排轨强行塞进同一过度识别检验会制造虚假的过度识别自由度, 是本项目反复申明的禁令。已知局限: 分母在早期试跑 T=2 样本下偏小致方差偏大 (生产 T=19 全量语料下稳定); locus 判定继承 LLM 分类测量误差, 须以跨模型 Krippendorff α 与 Cohen κ 一致性佐证 (Carlson 与 Burbano 2026 所倡); 因残余未归类, 本列与 app_frac 非严格互补, 不可由 1 减 app_frac 复原, 二元化时须显式处理平票 (tech_frac == app_frac) 与双缺失以免把无信息格误判为某一侧主导。

## VAR: tech_frac_lc

【变体差分】
本列 tier=standard, 是 canonical 列 tech_frac 的 ctx 轨稳健性孪生。后缀 _lc 读作 locus × ctx: 分子取文章级 innovation_locus_ctx 判为"底层技术"的报道数 n_articles_tech_lc_ctx, 分母配 ctx 轨有效判定篇数 n_articles_llm_valid_ctx, 分母为零或该分母列缺失时置 NaN。轨道差分在于: ctx (context) 轨的文本 = 标题 prepend + 实体上下文窗口 (银行/金融科技实体附近的正文窗口, 非全文), 因此本列刻画的是"当只看实体邻近语境时"底层技术落点的相对强度。它把 locus 判定收窄到实体邻近上下文窗口内, 剔除远离银行与金融科技实体的无关正文段落, 与 full 轨全文口径互为稳健性: full 轨看整篇, ctx 轨只看实体附近的语义环境, 二者对底层技术落点的判定若一致, 则说明该落点信号不依赖于取材范围的宽窄。

分母口径铁律: ctx 轨分子必须配 ctx 轨分母 (n_articles_llm_valid_ctx), 早期实现曾误用 full 轨分母 n_articles_llm_valid 导致轨道不对称、frac 越界至 3.0, 已修正为逐轨对称。留篇门控仍是 full-only: 本列的行宇宙是 full 留篇集的子集, ctx 降格为 conditional-on-full 的稳健性轨, 但分子分母严格取 ctx 轨口径, 不借 full 分母。本列在 P4 中作为 ctx_track_twin 出现 —— 与 full 轨 tech_frac 高相关的孪生, 属互为稳健性、非独立假设。识别上配 ctx 轨同业 LOO 工具 lpeer_locus_iv_ctx, 与 full/ss 轨各自并排。铁律: 本列 (ctx)、tech_frac (full)、tech_frac_ls (ss) 三轨各自 just-identified、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。已知退化: 开发样本早期试跑 T=2 下 ctx 轨可能出现零方差或大量 NaN (实体窗口内无足量 locus 判定), 属预期; 生产 T=19 全量语料下正常出值。

## VAR: tech_frac_ls

【变体差分】
本列 tier=standard, 是 canonical 列 tech_frac 的 ss 轨稳健性孪生, 镜像 tech_frac_lc 的 ctx 块。后缀 _ls 读作 locus × ss: 分子取文章级 innovation_locus_ss 判为"底层技术"的报道数 n_articles_tech_ls_ss, 分母配 ss 轨有效判定篇数 n_articles_llm_valid_ss, 分母为零或缺失时置 NaN。轨道差分在于: ss (same-sentence) 轨的文本 = 标题 prepend + 银行与金融科技在同一句±N 窗内共现的片段, 是三轨中语义最收窄、共现约束最严的一轨, 刻画的是"当银行与金融科技被同句提及时"底层技术落点的相对强度。ss 轨的回退语义镜像 ctx: 当某篇报道无银行∧金融科技同句共现时, 其 ss 文本回退为全文正文并置 fallback 标志, 与 ctx 轨的降级处理对称。

分母口径与 _lc 同律: ss 分子必须配 ss 分母 n_articles_llm_valid_ss, 防止轨道不对称致 frac 越界。留篇门控 full-only: 本列行宇宙为 full 留篇集子集, ss 轨降为 conditional-on-full 稳健性轨, 分子分母严格取 ss 口径不借 full 分母。本列在 P4 中作为 ss_track_twin 出现 —— 三轨中的第三主轨 (银行+金融科技同句共现轨), 与 full/ctx 互为稳健性、非独立假设。识别上配同句同业 LOO 工具 lpeer_locus_iv_ss, 与 full/ctx 轨各自并排。铁律: tech_frac (full)、tech_frac_lc (ctx)、本列 (ss) 三轨各自 just-identified、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 与 per-model 孪生、co-primary 嵌入双轨同律。已知退化: 同句共现约束最严, 开发样本早期试跑 T=2 下 ss 轨极易全 NaN 或零方差 (无足量同句共现的 locus 判定), 属预期退化; 生产 T=19 全量语料下方出稳定值。本列与 tech_frac / app_frac 因残余未归类而非严格互补, 二元化解读须谨慎。

<!-- rendered-citations:begin -->
He, Z., Jiang, S., Xu, D., & Yin, X. (2026). Investing in lending technology: IT spending in banking. Management Science. https://doi.org/10.1287/mnsc.2024.04608
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Ahnert, T., Doerr, S., Pierri, N., & Timmer, Y. (2026). Information technology in banking and entrepreneurship. Management Science, 72(3), 1796-1813. https://doi.org/10.1287/mnsc.2023.02555
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. Journal of Political Economy, 132(5), 1391-1449. https://doi.org/10.1086/727712
Kutzbach, M. J., & Pogach, J. (2024). Financial technology and relationship lending: Complements or substitutes? Journal of Financial Intermediation, 59, 101101. https://doi.org/10.1016/j.jfi.2024.101101
Pierri, N., & Timmer, Y. (2022). The importance of technology in banking during a crisis. Journal of Monetary Economics, 128, 88-104. https://doi.org/10.1016/j.jmoneco.2022.04.001
Kelly, B., Papanikolaou, D., Seru, A., & Taddy, M. (2021). Measuring technological innovation over the long run. American Economic Review: Insights, 3(3), 303-320. https://doi.org/10.1257/aeri.20190499
Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. Management Science, 67(7), 4004-4031. https://doi.org/10.1287/mnsc.2020.3682
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation? The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
<!-- rendered-citations:end -->
