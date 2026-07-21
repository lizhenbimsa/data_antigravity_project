---
family_id: F505
columns:
- strat_diff_n5_lda
- strat_diff_n5_lda_ctx
- strat_diff_n5_lda_ss
unit: 无量纲差异度得分 ∈ [0,1] (银行-年层面, 越大越战略疏离)
formula: "strat_diff_n5_lda = 1 - mean_{j∈N5(i)} sim(θ_i, θ_j); sim = 1 - JSD(θ_i, θ_j); θ = LDA 主题分布; JSD 为 base-2 Jensen-Shannon 散度 ∈ [0,1]; N5(i) = 主题相似度最高的 5 个同业文档"
producer: news_process/pipeline/features/strategic_diff.py ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1111/jofi.13400
  type: journal
  authors: Hoberg, G., & Phillips, G. M.
  year: 2025
  title: "Scope, scale, and concentration: The 21st-century firm"
  venue: The Journal of Finance
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
- doi: 10.1002/smj.3549
  type: journal
  authors: Su, J., Gao, X., & Tan, J.
  year: 2024
  title: "Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment"
  venue: Strategic Management Journal
  vol: 45
  issue: 2
  pages_or_artno: 333-361
- doi: 10.1177/10591478241245144
  type: journal
  authors: Banker, R. D., Huang, R., Li, X., & Yan, Y.
  year: 2024
  title: "Strategy typology and cost structure: A textual analysis approach"
  venue: Production and Operations Management
- doi: 10.3386/w33168
  type: wp
  authors: Cong, L. W., Liang, T., Zhang, X., & Zhu, W.
  year: 2024
  title: "Textual factors: A scalable, interpretable, and data-driven approach to analyzing unstructured information"
  venue: NBER Working Paper No. 33168
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: "Measuring founding strategy"
  venue: Management Science
  vol: 69
  issue: 1
  pages_or_artno: 101-118
- doi: 10.1287/mnsc.2020.3682
  type: journal
  authors: Bellstam, G., Bhagat, S., & Cookson, J. A.
  year: 2021
  title: "A text-based analysis of corporate innovation"
  venue: Management Science
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: 40
  issue: 1
  pages_or_artno: 3-27
- doi: 10.1093/rfs/hhz023
  type: journal
  authors: Hanley, K. W., & Hoberg, G.
  year: 2019
  title: "Dynamic interpretation of emerging risks in the financial sector"
  venue: The Review of Financial Studies
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1111/jofi.12050
  type: journal
  authors: Hoberg, G., Phillips, G., & Prabhala, N.
  year: 2014
  title: "Product market threats, payouts, and financial flexibility"
  venue: The Journal of Finance
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
- doi: 10.3386/w32934
  type: wp
  authors: Ganguli, I., Lin, J., Meursault, V., & Reynolds, N.
  year: 2024
  title: "Patent text and long-run innovation dynamics: The critical role of model selection"
  venue: NBER Working Paper No. 32934
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
- doi: "10.1007/s10490-026-10113-0"
  type: journal
  authors: "Manikandan, K. S., & Balaji, V. V."
  year: 2026
  title: "Ownership form, strategy distinctiveness, and firm performance"
  venue: "Asia Pacific Journal of Management"
- doi: "10.1177/14413582251399667"
  title: "Comparative Analysis of BERTopic Versus LDA: Topic Modelling in Marketing Research"
  authors: "Mishra, M."
  year: 2025
  venue: "Australasian Marketing Journal"
  type: "journal"
- doi: "10.1016/j.indmarman.2024.11.010"
  title: "Coopetition: A vehicle for business model distinctiveness"
  authors: "Bouncken, R. B., & Fredrich, V."
  year: 2025
  venue: "Industrial Marketing Management"
  type: "journal"
new_dois:
  - "10.1007/s10490-026-10113-0"
  - "10.1177/14413582251399667"
  - "10.1016/j.indmarman.2024.11.010"
---

## CORE

【构念与来源】
本家族刻画银行在公开媒体文本中所呈现的战略差异度 (strategic differentiation / distinctiveness), 即一家银行的年度报道文本在主题构成上偏离其同业群体的程度。构念根植于战略管理与产业组织中的最优差异化 (optimal distinctiveness) 与文本化产品市场竞争传统: Hoberg 和 Phillips (2016) 以年报文本余弦相似度构建内生产品差异化与文本网络产业分类, 开创了以非结构化文本度量企业竞争位置的范式; Haans (2019) 与 Su 等 (2024) 进一步论证差异化本身对绩效的非线性影响 (在同质范畴中差异化溢价高、在异质范畴中溢价衰减), 使"离群程度"成为可与绩效、并购、创新产出对接的一阶战略变量; Arts 等 (2025) 与 Miller 和 Wang (2024) 则把技术差异化与数字化转型下的差异化策略变迁纳入并购与市场竞争框架。本家族把这一思想迁移到银行-金融科技语境: 当一家银行在报道中所谈论的金融科技主题 (支付、区块链、开放银行、智能风控、数据中台等) 与同业趋同时, 差异度低; 当其主题组合罕见、独树一帜时, 差异度高。该测度不是情感, 也不是关注强度, 而是战略内容的空间位置。

之所以选择新闻文本而非年报或专利来度量银行的战略差异化, 有三点考量。其一, 中国上市与非上市银行的战略披露在年报中高度模板化、同质化, 而媒体报道对不同银行的金融科技动作有更细粒度、更及时的差异化呈现, 能捕捉战略在执行层面的实际展开而非纸面表述。其二, 媒体文本天然带有第三方视角与竞争性框架, Fang 和 Peress、You 等一系文献表明媒体在刻画企业竞争位置上具有增量信息含量。其三, 银行的金融科技战略往往通过合作公告、产品发布、机构设立等事件在媒体上被反复报道, 这些事件的主题构成正是战略离群性的可观测代理。因此本家族把"一家银行在年度媒体叙事中的主题组合有多罕见"操作化为可计算的战略差异度, 使抽象的战略定位成为面板可回归的连续变量。需要强调, 差异度是相对量而非绝对量: 它衡量的是相对同业群体的离群程度, 因此同一主题组合在不同年度、不同同业结构下可以对应不同的差异度值, 这一相对性正是最优差异化理论所要求的 — 差异化的经济含义只有在同业参照系中才成立。也正因如此, 本家族的差异度不能脱离其所在年度的同业池被跨年直接比较绝对水平, 而应通过银行与年度固定效应吸收参照系的系统性移动, 使回归识别落在同一参照系内的相对离群变化上; 这是把媒体文本战略差异度接入面板计量时的首要设定纪律。

【方法学与计算】
本家族的计算路径是"LDA 主题模型 + Jensen-Shannon 散度 (JSD) + N-最近邻距离"。首先, 对每家银行-年的报道文档 (三轨文本之一, 见下) 用潜在狄利克雷分配 (Latent Dirichlet Allocation, Blei 等 2003 的经典生成式主题模型) 估计一个主题分布 θ, θ 是定义在 K 个隐主题上的概率单纯形向量。两家银行-年之间的战略接近度用其主题分布的 Jensen-Shannon 散度度量: JSD 是 Kullback-Leibler 散度的对称、有界化版本, base-2 口径下 JSD ∈ [0,1], 值越小两分布越接近; 相应地相似度定义为 sim = 1 − JSD ∈ [0,1]。战略差异度的聚合遵循 Guzman 和 Li (2023) 的最近邻创业策略度量思路: 对目标银行-年 i, 在全样本其余文档中取主题相似度最高的 N=5 个邻居 (故名 n5), 差异度 = 1 − 这 5 个最近邻相似度的均值。直觉是: 若一家银行连"最像它的 5 个同业"都不太像它, 它就是战略离群者。分词层面 (口径披露, 2026-06-21) LDA 轨与词级 TF-IDF 轨一致地改用注入 607 个金融科技词的独立分词器, 使"金融科技""区块链"等领域复合词整词保留, 与 char 轨、embedding 轨的领域感知口径对齐; 该改动只影响 word/LDA 轨, char/embedding 轨字节不变。值域上, LDA 轨作为非负分布之间的散度天然落在 [0,1], 与 embedding 轨余弦真值域 [−1,1]、距离 [0,2] 的口径不同 — 后者曾被错误统一 clip 到 [0,1] 而地板掉负余弦, 已修正; LDA 轨不涉此问题。

在方法学上还需说明三点计算细节。其一, 为何选用 Jensen-Shannon 散度而非余弦或 Kullback-Leibler 散度作为 LDA 主题分布之间的距离: 主题分布是概率单纯形上的点, KL 散度不对称且当某分量为零时发散, 不适合直接作距离; JSD 是 KL 的对称化、平滑化版本, 有界 (base-2 下 ∈ [0,1])、满足度量的平方根为真度量, 是分布间距离的自然选择, 也与本项目其它主题分布距离列 (centroid_diff_lda、coh_lda) 保持口径一致。其二, 最近邻聚合而非全样本平均的动机来自 Guzman 和 Li (2023): 战略差异化的经济含义在于"与最像自己的少数几个同业有多不同", 而非"与全行业平均有多不同", 因为后者会被行业规模与主题偏斜稀释; 取 N=5 个最近邻的均值在噪声抑制 (单一邻居易受估计误差影响) 与局部聚焦 (过大 N 退化为全样本均值) 之间取得平衡, 并由 top-k N 梯子系统检验其敏感性。其三, LDA 主题分布 θ 的估计对随机种子与推断算法有确定性要求: 本项目在 golden 重生时须钉死 PYTHONHASHSEED 与全部 BLAS 线程数为 1, 以保证 θ 与由此派生的差异度列跨 run 可复现; 涉及浮点归约的相似度矩阵在不同 BLAS 后端上可能有末位漂移, 属已知非确定源, 验零漂移时按列名排除。

【文献定位】
方法学上本家族站在文本即数据 (text-as-data) 的方法论综述 (Gentzkow 等 2019) 与文本化企业战略度量两条脉络的交叉处。一支是 TF-IDF/余弦的产品市场文本网络 (Hoberg 和 Phillips 2016; Hoberg 等 2014 的产品市场流动性 fluidity; Hoberg 和 Phillips 2025 对 21 世纪企业范围、规模与集中度的最新刻画); 另一支是主题模型化的企业创新与战略文本分析 (Bellstam 等 2021 用主题模型从分析师报告抽取创新度; Banker 等 2024 用文本分析刻画战略类型与成本结构; Hanley 和 Hoberg 2019 用动态主题解读金融部门新兴风险; Cong 等 2024 的可扩展文本因子)。LDA+JSD 方法臂正是"主题模型化"这一支在本项目内的落点, 与 TF-IDF char/word 的词面余弦臂、稠密语义 embedding 臂并列为对同一战略差异化构念的多重文本表征。差异度作为战略离群性的一阶度量, 其经济含义在 Haans (2019)、Su 等 (2024)、Arts 等 (2025) 的差异化-绩效/并购文献中得到理论支撑, 使本家族可以作为处理变量或稳健性协变量进入银行-金融科技的战略、绩效与并购回归。

三种文本表征各有其偏倚与盲区, 这正是并排保留的理由。TF-IDF char/word 臂捕捉词面重叠, 对同义改写、领域术语的表述差异敏感, 可能把"说法不同但战略相同"误判为差异化。稠密 embedding 臂 (Qwen 与 co-primary text-embedding-3-large) 捕捉分布式语义, 对同义与近义稳健, 但可能把细粒度的战略差别平滑掉, 且嵌入空间随模型厂商 (阿里 Qwen 4096 维 / OpenAI 3072 维) 而异。LDA+JSD 臂捕捉主题层面的构成差异, 对文档级的话题混合敏感, 但受主题数 K 与语料规模影响、在短文本上估计噪声大。三臂对同一战略差异化构念给出相关但不完全一致的排序, 恰好互为偏倚对冲。Ganguli 等 (2024) 关于专利文本长期创新动态中模型选择的批判性作用、Cong 等 (2024) 的可扩展文本因子, 都强调了文本表征选择本身是一个需要稳健性检验的自由度 — 本家族的多臂并排设计正是对这一方法学告诫的直接回应。此外, 以行业向量与主题余弦相似度引导技术布局的行业向量思路 (见本项目 strategic_diff 模块源码所载中文文献出处), 是本项目全行业质心距离列 (centroid_diff_*) 的迁移来源, 与本家族的最近邻差异度构成两种互补的战略空间投影; 该迁移来源属源码内记录的方法思路, 本文档不对其单独作具名年份引用, 以免逸出白名单引文池。Manikandan 和 Balaji (2026, Asia Pacific Journal of Management) 检验企业所有权形式与战略差异度对绩效的联合影响, 与本家族把媒体文本主题构成的战略离群度接入银行绩效/并购回归的实证逻辑直接呼应, 进一步支持最优差异化理论在差异化-绩效关系上的边界条件。Mishra (2025, Australasian Marketing Journal) 对比 BERTopic 与 LDA 两种主题建模算法在营销研究文本中的表现, 发现 BERTopic 在语义捕捉上优于 LDA, 为本家族 LDA 方法臂的设定选择提供了最新的方法学参照。Bouncken 和 Fredrich (2025, Industrial Marketing Management) 基于跨行业 R&D 联盟的纵向调查数据, 发现企业可通过合作竞争 (coopetition) 学习实现商业模式差异化, 为本家族战略差异度构念的经济含义提供了实证支持。

在银行-金融科技这一具体经济场景中, 本家族的战略差异度还与竞争、绩效与并购三条实证脉络相接。竞争维度上, Hoberg 等 (2014) 的产品市场流动性与 Hoberg 和 Phillips (2016、2025) 的文本网络产业刻画表明, 一家企业在文本空间中的相对位置直接关联其面临的竞争威胁强度; 一家战略高度差异化的银行, 其金融科技动作较少被同业直接复制, 因而在短期内享有更低的竞争压力, 但也可能承担更高的路径不确定性。绩效维度上, Haans (2019) 与 Su 等 (2024) 的最优差异化理论提示差异度与绩效之间可能存在倒 U 形或范畴调节关系, 使本家族适合作为非线性设定 (含平方项、与市场同质度交互项) 的核心解释变量。并购维度上, Arts 等 (2025) 关于技术差异化驱动并购的发现, 与本项目 P5 银行-金融科技并购结果变量直接呼应 — 战略差异度可作为预测银行金融科技并购倾向的文本先行指标。这些接口使本家族不止是一个描述性文本指标, 而是可嵌入结构性研究设计的战略变量; 但所有这些用法都须遵守前述五臂/三轨/N 梯子的互为稳健性纪律, 主结论锚定单一 canonical 设定并以其余表征并排复现。

【识别策略定位】
本家族在识别框架中属于文本构造的自变量/稳健性轨, 而非结果变量。它与本项目其它文本测度共享同一套多重表征-多重稳健性纪律: LDA 方法臂 (strat_diff_n5_lda 及其三轨) 与 TF-IDF char 臂 (canonical strat_diff_n5)、TF-IDF word 臂 (_w)、Qwen 嵌入臂 (_emb) 及 co-primary text-embedding-3-large 嵌入臂 (_lg) 是对同一战略差异化构念的五种平行文本度量, 各自 just-identified、互为稳健性、不分主次; 铁律是它们禁混进同一 over-identified 的 Hansen J 过度识别检验 — 五臂并排提供的是测量稳健性 (measurement robustness) 而非可叠加的多工具集, 把语义高度相关的五个表征塞进同一 GMM 过度识别式会制造伪过度识别并污染 J 统计量。同理, top-k N 邻域梯子 (N=5 为 canonical, 另有 N∈{10,20,30,40,50} 大邻域孪生, 2026-07-02 扩展) 三轨 (full/ctx/ss) 亦各自 just-identified 并排, 互为稳健性、禁混同一 Hansen J。若需要构造工具变量, 应在单一臂、单一轨、单一 N 上做 just-identified 设定, 再以其它臂/轨/N 做规格稳健性并排复现, 而不是把它们聚合进过度识别式。

在因果识别层面还须直面本家族作为文本构造自变量的三重内生性来源。其一是同时性/反向因果: 战略差异度由当期媒体报道的主题构成度量, 而媒体对一家银行的报道又可能被该银行的绩效、并购动作或监管事件所驱动, 因此差异度与结果变量之间可能存在双向决定 — 一家近期完成金融科技并购的银行会同时在报道中呈现更罕见的主题组合 (高差异度) 并在结果变量上有异动。缓解路径是把差异度取滞后期进入回归 (以 t−1 期文本差异度解释 t 期结果), 并辅以银行与年度双固定效应吸收不随时间变化的银行异质性与全样本共同冲击。其二是测量误差: LDA 主题分布 θ 是带估计噪声的隐变量, 由此派生的最近邻差异度含经典测量误差, 在作自变量时会引致向零的衰减偏误 — 这恰是五臂并排的又一价值: 若 char/word/emb/_lg 四臂对同一银行给出一致的相对排序, 则可用一臂作另一臂的工具以纠正经典测量误差 (在满足工具外生性的前提下), 但这属于单一内生变量的 just-identified 设定, 仍不得把五臂当五个工具堆进过度识别式。其三是样本选择: 差异度只在被 full-only 门控留下的银行-金科报道集上有定义, 门控本身可能与银行特征相关, 因此把差异度接入全样本回归时须交代留篇宇宙的边界, 并以是否留篇作为一阶选择环节纳入稳健性讨论。若确需外生变异, 移位份额 (shift-share/Bartik) 类工具的构造须遵循 Goldsmith-Pinkham 等 (2020) 与 Borusyak 等 (2022) 对份额外生性与冲击外生性的识别假设分解, 在单一臂-轨-N 上做 just-identified 设定, 而非以多臂充数过度识别。本家族在下游既可作处理变量 (检验战略差异化对绩效/并购/创新的影响), 也可作稳健性协变量 (在以情感或关注度为主处理变量的模型中控制战略内容位置), 两种角色下的识别纪律不同, 但共享"单臂 just-identified、多臂多轨多 N 并排稳健"的同一底线。

【与相邻测度的构念区分】
本家族须与三类相邻文本测度严格区分。其一, 与最大同行相似度 strat_sim_max_lda 互补而非等同: 后者取"与最相似的单一同业"的相似度 (峰值接近度), 本家族取"最近 5 个同业的平均差异度", 分别刻画战略空间的局部拥挤度与邻域疏离度。其二, 与全行业向量法 centroid_diff_lda 区分: 后者度量文档主题分布到全行业质心 (行业向量迁移思路, 见源码所载方法出处) 的距离 (对全体的离心度), 本家族度量到 k 个最近邻的距离 (对局部邻域的离群度) — 质心距离对样本规模与行业主题偏斜更敏感, 最近邻距离对局部同业结构更敏感, 二者是差异化的两种几何投影。其三, 与相邻期文本连贯性 coh_lda 区分: 后者是同一银行相邻两期文本的 JSD 时序自相似 (战略稳定性/漂移), 本家族是横截面上的银行间差异 (战略离群性) — 一个是时间维、一个是截面维, 不可混用。此外本家族与情感 (tone)、关注强度 (attention/fintech_share) 正交: 战略差异度只看"谈什么主题的组合有多罕见", 不看"谈得正面还是负面""谈得多不多"。这一正交性在实证上很重要: 一家银行可以被大量正面报道 (高关注、正情感) 却战略高度趋同 (低差异度), 也可以被稀少报道却战略独树一帜; 把差异度与情感、关注度并列进模型时, 三者刻画的是媒体叙事的不同侧面 (内容位置 vs 情感极性 vs 声量), 不构成机械共线。同理, 本家族与本项目的战略稳定性/漂移测度不同: 差异度是某一年横截面上的银行间比较, 而战略漂移 (由 coh_lda 时序自相似刻画) 是同一银行跨年的主题连续性; 一家银行可以年年高差异度却战略稳定 (持续做别人不做的事), 也可以低差异度但战略剧烈漂移 (跟风但年年换风向)。厘清这些相邻测度的坐标, 是避免把战略差异度误读为"被关注度""正面度"或"战略变动"的前提。

进一步厘清本家族在整个文本测度矩阵中的几何位置, 有助于避免下游把它与结构相近但构念不同的列机械混用。第一组要区分的是"聚合算子": 战略空间中同一组两两相似度, 可以取最近邻均值 (本家族)、单一峰值 (strat_sim_max)、全体质心距离 (centroid_diff)、或全体均值离心度, 四种算子对同业池的规模偏斜、主题厚尾、局部拥挤度的敏感性各不相同 — 最近邻均值对局部同业结构敏感而对远端离群点稳健, 峰值对最相似单一竞争者敏感, 质心距离对行业整体主题偏斜敏感; 把它们并列进模型时须理解它们回答的是"离最像的少数几家有多远""离最像的那一家有多近""离行业中心有多偏"三个不同的战略几何问题, 而非同一量的替代估计。第二组要区分的是"表征空间": LDA 主题分布 JSD (本家族)、字符/词 TF-IDF 余弦、稠密嵌入余弦, 分别把文档投影到隐主题单纯形、稀疏词面空间、稠密语义空间, 三者对同义改写、领域术语、话题混合的敏感性互补, 是同一构念的多重表征而非同一测度的多次采样。第三组要区分的是"时间 vs 截面": 本家族是某一年横截面上的银行间离群度, 而相邻期连贯性 coh_lda 是同一银行跨年主题自相似 (战略漂移/稳定); 一家银行完全可以年年高差异度却战略稳定 (持续做别人不做的事), 或低差异度却剧烈漂移 (跟风且年年换赛道), 二者在经济含义上正交, 混用会把"独特"误读为"多变"。最后, 本家族与情感 (tone)、关注强度 (attention/fintech_share) 三者是媒体叙事的三个正交侧面 — 内容位置 (谈什么主题组合有多罕见)、情感极性 (谈得正面还是负面)、声量 (谈得多不多); 高关注高正面的银行可以战略高度趋同, 稀少报道的银行可以战略独树一帜, 三者并列进模型刻画不同机制, 不构成机械共线。把这四组区分内化, 才能在下游设定中正确选列: 检验"独特性溢价"用本家族的最近邻差异度, 检验"竞争威胁强度"更宜用峰值相似或质心距离, 检验"战略稳定性"须回到 coh_lda 时序轨, 三者不可互相顶替。

【已知局限与稳健性梯子】
已知局限有四。其一, LDA 主题数 K 与超参是研究者选择, 主题分布对 K 敏感; 项目以 TF-IDF char/word 与 embedding 臂并排作为对主题模型设定的稳健性对冲 — 若五臂差异度对同一银行给出一致的相对排序, 则结论不被单一表征的设定驱动。其二, JSD 最近邻差异度依赖同业池的构成与规模; 在浅面板 (开发态 T=2、约 220 行) 上邻域稀薄、θ 估计噪声大, ctx/ss 轨可能出现退化 (零方差或全回退), 属预期, 生产态 T=19、约 1,819 万条语料下正常。其三, N=5 的邻域宽度是选择: top-k N 梯子 (N∈{5,10,20,30,40,50}) 系统检验邻域宽度敏感性, canonical N=5 与大 N 孪生互为稳健性、不分主次、禁混同一 Hansen J。其四, 三轨文本边界不同 (见下各 VAR 节), full 轨最宽、ss 轨最窄且带回退, 三轨并排检验"文本窗口选择"对差异度的影响。多重检验层面, 若把 LDA 臂与其它臂/轨/N 联合作为对同一假设的多次检验, 应以 Romano 和 Wolf (2005) 的逐步多重检验 (rwolf) 控制族错误率, 而非各自单独宣称显著。三轨/五臂/N 梯子之间正交、互为稳健性、不分主次, 均禁混进同一 over-identified Hansen J。

关于稳健性梯子的实证使用, 还需补充四点操作纪律, 以免把"多重表征"误用为"多重工具"或"择优呈报"。第一, 报告规范: 主结论应锚定单一 canonical 设定 (LDA 臂选 strat_diff_n5_lda, full 轨, N=5), 五臂/三轨/大 N 全部作为并排稳健性列同时呈现, 而非在其中挑选显著者作主结果 — 择优呈报即形式化的数据窥探, 正是 Romano 和 Wolf (2005) 所要防范的。第二, 工具变量纪律: 若差异度进入 2SLS 作内生自变量, 工具须在单一臂-轨-N 上构造 just-identified 设定, 不得把 LDA、char、emb 三臂的差异度当作同一内生变量的多个工具塞进过度识别式 — 它们是同一构念的高度相关表征 (相关系数常在 0.9 以上), 伪过度识别会使 Hansen J 失去检验力并给出误导性的不可拒绝。第三, 面板深度约束与小样本告诫: 最近邻差异度的稳定性依赖逐年同业池规模, 这里须严格区分两个口径 — 约 110 家是全面板去重后的银行总数, 而进入某一年最近邻计算的是该年度实际有有效文本的同业池, 其逐年规模远小于总数 (源码局限性明示 strat_diff 逐年有效样本约 54 家/年量级, N=5 邻域约占逐年池的十分之一)。因此不能以全面板 110 家的总数直接推断逐年 N=5 邻域已"足够稳健": 在逐年池偏薄的年度, N=5 最近邻仍可能受小样本偏差影响, 邻域估计方差偏大, 须与其它 N (大邻域孪生) 及其它臂/轨并排比对以判断相对排序是否稳定, 源码亦对此小样本偏差给出显式告诫。生产态 T=19、跨 2007–2025 相对开发态 T=2 的浅面板 (约 220 行) 已大幅缓解逐年池稀薄问题, 但缓解不等于消除 — 早期年份或报道稀疏的银行子样本仍可能触发小样本偏差, 报告时应交代逐年同业池规模而非仅援引全面板总数。审计不得以 T=2 浅面板的退化现象反推生产态完全不可识别, 但同样不得以全面板总数 110 掩盖逐年池的小样本约束; 二者是一体两面的口径纪律。第四, 缺失与降级: 当某银行-年无有效文本或主题分布无法估计时, 差异度为缺失而非零 — 零意味着"与同业完全一致"是一个实质判断, 缺失意味着"无法判断", 二者语义不可混淆, 下游回归须按缺失处理而非填零。这四点连同五臂/三轨/N 梯子的互为稳健性纪律, 共同构成本家族在识别与推断上的使用边界。

关于稳健性梯子本身, 还须补充其结构与彼此正交性, 以免误读为可任意叠加的自由度。本家族张成的稳健性空间是三个正交轴的乘积: 方法臂轴 (LDA/char/word/emb/_lg 五臂)、文本轨轴 (full/ctx/ss 三轨)、邻域宽度轴 (N∈{5,10,20,30,40,50})。三轴各自回答不同的稳健性问题 — 方法臂轴回答"文本表征选择是否驱动结论", 文本轨轴回答"文本窗口宽窄是否驱动结论", 邻域宽度轴回答"局部还是全局参照系是否驱动结论"; 三轴正交意味着可沿单轴移动做单因素稳健性检验, 但不应把三轴的全部笛卡尔积当作独立结果矩阵去逐格挑显著者呈报, 那等于把稳健性检验异化为多重比较的择优。Ganguli 等 (2024) 关于专利文本长期创新动态中模型选择的批判性作用, 正说明文本表征选择本身是一个必须被稳健性检验而非被静默固定的研究者自由度, 本家族的多臂多轨多 N 并排设计是对这一告诫的直接回应, 但回应的方式是"锚定单一 canonical 并证明其余表征给出一致排序", 而非"从全乘积里挑一个显著格"。此外须区分两类退化: 一是数据稀薄导致的估计退化 (浅面板 T=2 上 ctx/ss 轨零方差、θ 噪声大), 属预期且生产态 T=19 消失, 审计不得据此反推生产态不可识别; 二是构念退化 (如 N 增大到接近同业池规模时最近邻差异度数学上退化为全样本离心度、与质心距离趋同), 属方法本身的边界, 须在报告中显式声明大 N 臂的解释力随 N 增大而向质心距离漂移。最后, 多重检验的层级也须交代清楚: 若把五臂/三轨/多 N 视为对同一战略差异化假设的多次并行检验, 族错误率应以 Romano 和 Wolf (2005) 的逐步多重检验 (rwolf) 在根级模板层面统一控制, 而非在每列各自宣称显著; 而 codebook 层面的多臂声明是描述性文档, 运行时并无消费者, 真正的 FWER 控制发生在 Stata 复现包的 rwolf 模板中。三轨、五臂、N 梯子彼此正交、互为稳健性、不分主次, 且一律禁混进同一 over-identified Hansen J — 这是本家族全部稳健性用法不可逾越的底线。

## VAR: strat_diff_n5_lda

【变体差分】
本列是家族的 canonical 主轨 (tier=core), full 轨 × LDA+JSD 方法臂 × N=5 邻域。文本边界为 full 轨: 标题 prepend 到全文正文 (content_full), 即 stage 14 物化的最宽文本窗口, 覆盖一家银行-年该报道的全部内容。方法臂为 LDA+JSD: 文档先经注入 607 金融科技词的独立分词器分词, 由 LDA 估计 K 维主题分布 θ, 两两接近度以 base-2 Jensen-Shannon 散度定义 (sim = 1 − JSD ∈ [0,1]), 差异度 = 1 − 与主题相似度最高的 N=5 个同业文档相似度的均值, 值域 [0,1], 越大越战略离群。它区别于同家族两条 ctx/ss 轨之处仅在文本窗口 (full 用全文, 后两者用实体窗口/同句窗口); 区别于 TF-IDF char canonical strat_diff_n5 之处在表征方式 (主题分布 JSD vs 字符 n-gram 余弦); 区别于 strat_diff_n5_emb/_lg 之处在表征方式 (离散主题分布 vs 稠密句向量余弦); 区别于 strat_sim_max_lda 之处在聚合算子 (最近 5 邻均值差异 vs 单一峰值相似)。作为 LDA 方法臂的 canonical, 本列与 char/word/emb/_lg 四臂各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与 top-k 大 N 孪生 (n10..n50 的 LDA 版本) 同样各自 just-identified 并排, N=5 无特殊地位, 仅为历史 canonical 锚。就 n_articles 与留篇口径而言, 差异度只在被 full-only 门控留下的银行-金科报道集 (2026-06-29 口径: 留篇判定只看 full 轨 llm_verified_full == True) 上计算文档主题分布, ctx/ss 轨为条件于 full 留篇集的子集测度, 不改变留篇宇宙。生产态该列可作战略差异化的处理变量或稳健性协变量进入回归, 承载 Guzman 和 Li (2023) 最近邻策略度量与 Hoberg 和 Phillips (2016)、Haans (2019)、Su 等 (2024) 差异化-绩效脉络的经济含义。

进一步展开本列相对家族其它列的精确差分坐标。在"方法臂 × 轨道 × 邻域宽度"三维坐标系中, 本列位于 (LDA+JSD, full, N=5), 是整个 strat_diff 大族中被指定为 core 的锚点列 (2026-07-10 签核扩围), 与 TF-IDF char 的 canonical strat_diff_n5 同为各自方法臂的 canonical, 二者 co-equal 互为稳健性。它区别于 word 臂 strat_diff_n5_w (jieba 词级 TF-IDF 余弦, 词面而非主题)、区别于 emb 臂 strat_diff_n5_emb (Qwen 稠密句向量余弦距离)、区别于 co-primary strat_diff_n5_emb 的 _lg 孪生 (text-embedding-3-large 嵌入); 这五条 full 轨 N=5 差异度列构成对同一构念的五重表征, 各自 just-identified、互为稳健性、不分主次, 铁律禁混进同一 over-identified Hansen J。它区别于 top-k 大邻域孪生 (LDA 臂的 n10、n20、n30、n40、n50 版本, 2026-07-02 扩展) 之处仅在 N: 大 N 把邻域从最近 5 个同业放宽到最近数十个, 差异度随 N 增大而系统性平滑、逼近全样本离心度; N=5 与大 N 各自 just-identified 并排, N=5 无本质优先地位, 仅是历史 canonical 命名锚。它区别于最大同行相似度 strat_sim_max_lda 之处在聚合算子 (最近 5 邻的平均差异 vs 单一最相似同业的峰值相似); 区别于全行业质心距离 centroid_diff_lda 之处在参照系 (局部 k 近邻 vs 全行业质心); 区别于相邻期文本连贯性 coh_lda 之处在维度 (横截面银行间离群 vs 时序自相似漂移)。就留篇门控而言, 本列所依赖的银行-金科报道集由 full-only 门控界定 (2026-06-29 口径: 是否判为一篇银行金科报道只看 llm_verified_full == True), 因此 full 轨本列直接在留篇宇宙上计算文档主题分布与最近邻差异度, 是三轨中口径最"正"的一条; ctx/ss 两轨是条件于该 full 留篇集的子集测度。作为 core 锚点, 本列在下游可担任战略差异化的主处理变量, 在稳健性 battery 中则与其它四臂、大 N 孪生、ctx/ss 两轨联袂做规格稳健性并排; 若多臂/多轨/多 N 被联合用于对同一战略差异化假设的多次检验, 应以 Romano 和 Wolf (2005) 的逐步多重检验控制族错误率, 而非逐列单独宣称显著, 且各表征仍禁混进同一 over-identified Hansen J。

## VAR: strat_diff_n5_lda_ctx

【变体差分】
本列 (tier=standard) 是 canonical 的 ctx 轨孪生: LDA+JSD 方法臂、N=5 邻域一律不变, 唯一差分在文本窗口。ctx 轨文本 (content_ctx) 是标题 prepend 到实体上下文窗口 — 只保留围绕目标银行实体的邻近文本片段而非全文, 使主题分布 θ 聚焦于与该银行直接相关的语境, 剔除报道中与该银行无关的背景段落。相对 full 轨 (全文), ctx 轨更窄、更聚焦, 在报道涉及多家主体或含大量宏观背景时能降低主题噪声, 但也可能因文本量缩减而使 θ 估计更不稳定。本列与 full 轨 (strat_diff_n5_lda)、ss 轨 (strat_diff_n5_lda_ss) 构成三轨并排: 三轨各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J — ctx 轨提供的是对"文本窗口选择"这一测量自由度的稳健性检验, 而非可与 full 轨叠加的独立工具。在浅面板 (T=2) 上 ctx 轨因邻域稀薄可能出现退化 (零方差或大量缺失), 属预期, 生产态 T=19 正常。本列与其它方法臂 (char/word/emb/_lg) 的 ctx 轨版本, 以及 top-k N 梯子的 ctx 版本, 同样各自 just-identified 并排、互为稳健性、禁混同一 Hansen J。留篇宇宙不变 (full-only 门控), 本列为条件于 full 留篇集的逐轨测度。需强调 ctx 轨的实体窗口口径与 ss 轨的同句共现口径是两个不同的键与判据, 不可互相复用: ctx 只要求文本落在目标银行实体的邻近窗口, 不要求金融科技词同时出现在窗口内; ss 则严格要求银行与金科词同句共现。因此在同一银行-年上, ctx 轨文本通常宽于 ss 轨、窄于 full 轨, 其 LDA 主题分布介于二者之间, 差异度也相应地是三轨中的中间口径。作为主要稳健性轨之一, ctx 轨检验的核心问题是: 把文本从全文收窄到银行实体语境后, 战略差异度的银行间相对排序是否稳定 — 若稳定, 则 full 轨结论不被无关背景文本驱动。

## VAR: strat_diff_n5_lda_ss

【变体差分】
本列 (tier=standard) 是 canonical 的 ss 轨孪生: LDA+JSD 方法臂、N=5 邻域不变, 差分同样只在文本窗口, 但 ss 轨是三轨中最窄的语境。ss 轨文本 (content_ss) 是标题 prepend 到银行与金融科技同句共现的 ±N 句窗口 (config filtering.yaml 的 ss_sentence_radius, 默认 1), 即只保留"目标银行与金融科技词出现在同一句 (及相邻 1 句)"的文本片段, 使主题分布 θ 高度聚焦于银行的金融科技叙事本身。关键回退语义 (镜像 ctx 轨, 以 CLAUDE.md 铁律为准): 当某银行-年不存在银行∧金科同句共现时, content_ss 优雅回退为全文 body, 且 ss_is_fallback 置 True, 与 ctx 轨共享 n_articles 分母; 当 FINTECH_AC 词典为 None 时 *_is_fallback 全 True 整体优雅降级。因此 ss 轨在同句共现丰富时提供最聚焦的金融科技战略差异度信号, 在共现稀薄时回退近似 full 轨。本列与 full/ctx 两轨构成三轨并排, 三轨各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; ss 轨是对"最严文本窗口"这一测量端点的稳健性检验。浅面板上 ss 轨退化 (回退占比高、方差趋零) 属预期, 生产态正常。本列与其它方法臂/其它 N 的 ss 版本同样各自 just-identified 并排。留篇宇宙不变 (full-only 门控), 本列为条件于 full 留篇集的逐轨测度。作为三轨中最严的端点, ss 轨检验的核心问题是: 当把文本压缩到只剩"银行谈金融科技的那几句话"时, 战略差异度的银行间相对排序是否仍稳健 — 若稳健, 则 full 轨结论不被报道中与金融科技无关的战略叙事 (如网点扩张、人事变动等) 驱动; 若因回退占比过高而退化, 则说明该样本的金融科技同句共现稀薄, 需谨慎解读 ss 轨结果。ss 轨与 ctx 轨的判据严格区分 (同句共现 vs 实体窗口), 二者的原语不可互相复用。

<!-- rendered-citations:begin -->
Hoberg, G., & Phillips, G. M. (2025). Scope, scale, and concentration: The 21st-century firm. The Journal of Finance. https://doi.org/10.1111/jofi.13400
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Banker, R. D., Huang, R., Li, X., & Yan, Y. (2024). Strategy typology and cost structure: A textual analysis approach. Production and Operations Management. https://doi.org/10.1177/10591478241245144
Cong, L. W., Liang, T., Zhang, X., & Zhu, W. (2024). Textual factors: A scalable, interpretable, and data-driven approach to analyzing unstructured information. NBER Working Paper No. 33168 [Working Paper]. https://doi.org/10.3386/w33168
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. Management Science. https://doi.org/10.1287/mnsc.2020.3682
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Hanley, K. W., & Hoberg, G. (2019). Dynamic interpretation of emerging risks in the financial sector. The Review of Financial Studies. https://doi.org/10.1093/rfs/hhz023
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance. https://doi.org/10.1111/jofi.12050
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Ganguli, I., Lin, J., Meursault, V., & Reynolds, N. (2024). Patent text and long-run innovation dynamics: The critical role of model selection. NBER Working Paper No. 32934 [Working Paper]. https://doi.org/10.3386/w32934
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies. https://doi.org/10.1093/restud/rdab030
Manikandan, K. S., & Balaji, V. V. (2026). Ownership form, strategy distinctiveness, and firm performance. Asia Pacific Journal of Management. https://doi.org/10.1007/s10490-026-10113-0
Mishra, M. (2025). Comparative Analysis of BERTopic Versus LDA: Topic Modelling in Marketing Research. Australasian Marketing Journal. https://doi.org/10.1177/14413582251399667
Bouncken, R. B., & Fredrich, V. (2025). Coopetition: A vehicle for business model distinctiveness. Industrial Marketing Management. https://doi.org/10.1016/j.indmarman.2024.11.010
<!-- rendered-citations:end -->
