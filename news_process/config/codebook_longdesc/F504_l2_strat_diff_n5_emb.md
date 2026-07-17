---
family_id: F504
columns:
- strat_diff_n5_emb
- strat_diff_n5_emb_ctx
- strat_diff_n5_emb_lg
- strat_diff_n5_emb_lg_ctx
- strat_diff_n5_emb_lg_ss
- strat_diff_n5_emb_ss
unit: 无量纲语义距离得分 (余弦距离口径, 值域 [0,2])
formula: "strat_diff_n5_emb = (1/N) · Σ_{j ∈ NN5(i)} (1 − cos(e_i, e_j)), N=5; e_i = 银行 i 当年新闻文档嵌入向量, NN5(i) = 语义空间中与 i 余弦相似度最高的 5 个同行银行; MAIN 轨 e 来自 Qwen3-Embedding-8B (4096 维), _lg 轨来自 text-embedding-3-large (3072 维)"
producer: pipeline\panel\stata_export.py ; pipeline\features\strategic_diff.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_sbert.parquet (co-primary 双轨嵌入向量)
citations:
- doi: 10.1002/smj.3687
  type: journal
  authors: Arts, S., Cassiman, B., & Hou, J.
  year: 2025
  title: "Technology differentiation, product market rivalry, and M&A transactions"
  venue: Strategic Management Journal
  vol: 46
  issue: 4
  pages_or_artno: 837-862
- doi: 10.18653/v1/2025.emnlp-main.179
  type: arxiv
  authors: Tang, Y., & Yang, Y.
  year: 2025
  title: "FinMTEB: Finance Massive Text Embedding Benchmark"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 3620-3638
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
- doi: 10.1080/07421222.2023.2301176
  type: journal
  authors: Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y.
  year: 2024
  title: "The effects of sentiment evolution in financial texts: A word embedding approach"
  venue: Journal of Management Information Systems
  vol: 41
  issue: 1
  pages_or_artno: 178-205
- doi: 10.1145/3589335.3651526
  type: journal
  authors: Steck, H., Ekanadham, C., & Kallus, N.
  year: 2024
  title: "Is cosine-similarity of embeddings really about similarity?"
  venue: Companion Proceedings of the ACM Web Conference 2024
  pages_or_artno: 887-890
- doi: 10.48550/arXiv.2401.00368
  type: arxiv
  authors: Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F.
  year: 2024
  title: "Improving text embeddings with large language models"
  venue: arXiv
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: "Measuring founding strategy"
  venue: Management Science
  vol: 69
  issue: 1
  pages_or_artno: 101-118
- doi: 10.18653/v1/2023.eacl-main.148
  type: arxiv
  authors: Muennighoff, N., Tazi, N., Magne, L., & Reimers, N.
  year: 2023
  title: "MTEB: Massive text embedding benchmark"
  venue: Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics
  pages_or_artno: 2014-2037
- doi: 10.1086/715162
  type: journal
  authors: Rodriguez, P. L., & Spirling, A.
  year: 2022
  title: "Word embeddings: What works, what doesn't, and how to tell the difference for applied research"
  venue: The Journal of Politics
  vol: 84
  issue: 1
  pages_or_artno: 101-115
- doi: 10.48550/arXiv.2201.10005
  type: arxiv
  authors: Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., ... Weng, L.
  year: 2022
  title: "Text and code embeddings by contrastive pre-training"
  venue: arXiv
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: 40
  issue: 1
  pages_or_artno: 3-27
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing
  pages_or_artno: 3980-3990
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: "10.1007/s10479-026-07305-8"
  type: journal
  authors: "Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y."
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: "Annals of Operations Research"
new_dois:
  - "10.1007/s10479-026-07305-8"
---

## CORE

【构念与来源】
本家族刻画银行"战略差异化"这一构念在嵌入语义空间中的度量, 核心列为 strat_diff_n5_emb 与其跨厂商对偶 strat_diff_n5_emb_lg。其研究直觉源自战略管理与文本经济学交叉领域的一个基本命题: 一家机构在同业中的"独特程度"可以由它的文本画像与最相似同行之间的距离来刻画。距离越大, 说明该银行的新闻叙事在语义上越难被同业模仿或覆盖, 战略定位越发独特; 距离越小, 说明其叙事高度趋同、扎堆于行业主流话语。这一"以文本邻近度反推战略相似度"的思路, 直接承接 Guzman & Li (2023) 在创业战略度量中提出的最近邻距离方法: 把每个主体的文本表征投影到统一向量空间, 以其到 N 个最近邻的平均距离作为"战略差异度"的连续代理。Hoberg & Phillips (2016) 更早在产品市场层面证明, 用招股书文本余弦相似度构造的"文本网络行业"能内生地刻画产品差异化, 并预测并购与竞争后果; 本家族把这一文本网络逻辑从产品市场迁移到银行的新闻叙事场域, 以银行-年为观测单元。构念层面它还与 Haans (2019)、Su 等 (2024) 讨论的"最优独特性"传统相通: 差异化并非越高越好, 过度独特会损失合法性、过度趋同会丧失辨识度, 因此本列作为连续测度, 既服务于线性效应估计, 也可支撑非线性 (倒 U) 假设检验。数据来源上, 本列所依赖的文本为银行-年聚合的新闻文档: 由 stage 14 物化的三轨文本 (content_full / content_ctx / content_ss) 经 stage 25 article_sbert 的 co-primary 双轨嵌入引擎编码为稠密向量, 再在 strategic_diff 特征模块内按银行-年聚合并计算最近邻距离; 面板标签与列落盘由 stata_export 负责。需要说明本家族在整个项目度量体系中的位置: 它属于战略文本刻画这一大类, 与情感 (tone)、注意力 (attention)、政策对齐 (policy alignment)、套话率 (boilerplate)、语义陈旧度 (staleness) 等文本派生度量并列, 共同构成银行-年面板的文本特征层。相较那些逐篇打分再聚合的度量, 本家族的特殊性在于它是一个"关系型"度量 — 单看一家银行的向量无法算出差异度, 必须放在同期同业的相对位置里才有意义, 因此它对样本框 (哪些银行进入当年横截面) 的定义高度敏感, 这也是后文反复强调样本深度约束的原因。构念的中文直觉可以用一句大白话概括: 如果把每家银行当年被媒体报道的金融科技故事压缩成一个"语义指纹", 那么本列衡量的就是这枚指纹与最像它的五家同行指纹之间的平均差距 — 差距大说明这家银行讲了一个别人讲不出的故事, 差距小说明它的故事和同行高度撞款。

【方法学与计算】
计算链路分三步。第一步是文本编码: 对每篇银行金科报道, 按轨取对应文本 (full=标题 prepend + 全文正文; ctx=标题 + 实体窗口; ss=标题 + 银行∧金科同句±N 窗), 交由嵌入引擎的纯 API 通道编码。MAIN 无后缀轨走硅基流动 Qwen3-Embedding-8B, 输出 4096 维向量; _lg 轨走 OpenAI/yunwu 的 text-embedding-3-large, 输出 3072 维向量。引擎维度无关, 由返回矩阵的列数驱动, 内部按 cl100k 分词以 8191 token 为界切块后再聚合, 因此单篇超长报道也能稳定编码。第二步是银行-年聚合: 把同一银行同一年的文档向量聚合为一个银行-年语义画像 (质心方向), 得到该主体在语义空间中的坐标; 聚合以银行-年为最小观测粒度, 与最终面板的行键一致, 避免把篇级噪声直接传导到主体级差异度。第三步是最近邻差异度: 对目标银行 i, 在同年所有其它银行中检索余弦相似度最高的 N=5 个同行, 取 i 到这 5 个最近邻的平均余弦距离作为 strat_diff_n5_emb。之所以只在同年横截面内检索最近邻, 是因为差异化是一个相对概念 — 银行是否独特只能相对同期同业而言, 跨年混检会把宏观语义漂移误读为战略变化。值域口径须特别澄清: 嵌入轨的余弦相似度真值域为 [−1,1], 因此相似度类列 (strat_sim_max_emb、coh_emb) 落在 [−1,1], 而距离类列 (本家族 strat_diff_*_emb、centroid_diff_emb) 落在 [0,2]; 此前对嵌入轨统一 clip 到 [0,1] 的做法会把负余弦地板到 0、造成值域删失, 现已按真值域保留。这一点与 TF-IDF/LDA 轨不同: 后者基于非负向量或概率分布, 距离天然落在 [0,1]; 嵌入轨则允许语义方向相反 (负余弦), 因而距离可超过 1。当两家银行的新闻叙事在语义上不仅不相似、而是系统性对立 (例如一家主打自建金科、一家主打外部合作) 时, 余弦可为负, 距离超过 1, 这一信息在旧的 clip 口径下会被抹平, 是本家族改用真值域的直接收益。之所以固定 N=5, 是因为最近邻数 N 是一个可调超参数: N 越小越强调与最相似同行的贴近程度、对孤立异常点越敏感, N 越大越平滑、越接近到整个同业分布的中心距离。本家族的 canonical 取 N=5 (承接 Guzman & Li 的常用设定), 而 stage 25/strategic_diff 另行物化了 N∈{10,20,30,40,50} 的大邻域孪生列 (top-k N 扩展) 作为稳健臂; 因大邻域列只是同一嵌入矩阵的后处理, 其物化不产生额外 API 成本, 因此可以低成本地把 N 敏感性做满。整个家族的输出列约定亦须留意命名的历史特殊性: n5_emb、sim_max_emb、centroid_diff_emb 三族的 full 轨为裸名 (无 _full 后缀), 其余轨与其余族才带完整后缀, 这一不对称是历史命名产物, 与"主次"无关。

【文献定位】
方法学上本家族坐落在"文本即数据"的经济学传统 (Gentzkow, Kelly, & Taddy, 2019) 与稠密嵌入语义度量传统的交汇处。相较于早期基于词袋/TF-IDF 的文本相似度, 稠密句嵌入 (Reimers & Gurevych, 2019) 能捕捉同义改写与领域复合词的语义等价, 因而对"叙事趋同"这一构念更敏感; Neelakantan 等 (2022) 与 Wang 等 (2024) 进一步证明对比预训练与大模型驱动的嵌入在检索与聚类任务上的显著增益, 支撑本项目以 API 级大模型嵌入替代本地小模型的技术选择。嵌入模型的选择本身会影响下游度量, 这一"模型敏感性"已被 Rodriguez & Spirling (2022) 在应用研究场景系统论证, 也正是本家族维持 co-primary 双轨 (Qwen 与 text-embedding-3-large) 的根本动机; MTEB (Muennighoff 等, 2023) 与面向金融文本的 FinMTEB (Tang & Yang, 2025) 提供了跨模型效度评估的基准框架, 后者尤其提示通用嵌入基准上的排名未必迁移到金融领域文本, 因而本项目在选轨时既参考通用榜也重视金融语料上的表现, 并最终以双轨并置而非单一"最优模型"来对冲选型不确定性。方法学谱系上, 本家族亦与稠密语义检索的近期进展呼应: Wang 等 (2024) 展示大语言模型驱动的嵌入在低资源与多语言场景的增益, 与本项目为中文金融新闻选用支持中文的大模型嵌入的技术判断一致; Neelakantan 等 (2022) 确立的对比预训练范式则是当代通用文本嵌入 (含本项目两轨) 的共同技术底座。Zheng 等 (2024) 在金融文本情感演化上验证了词嵌入方法的外部效度, 与本家族把嵌入距离用于战略叙事的做法同源。战略内容上, 本家族接续 Hoberg & Phillips (2016) 的文本网络差异化、Haans (2019) 与 Su 等 (2024) 的最优独特性、以及 Arts 等 (2025)、Miller & Wang (2024) 关于技术差异化与产品数字化如何驱动并购与战略变革的最新证据, 把"文本可度量的独特性"这一实证抓手迁移到中国银行业与金融科技叙事的语境。值得强调的是, 上述战略管理文献多以专利文本、产品描述或招股书为语料, 而本家族的语料是第三方新闻报道 — 这一语料切换既是优势也是约束: 优势在于新闻叙事覆盖广、时效强、不受企业自我披露口径的操纵, 能捕捉外部观察者眼中的银行战略画像; 约束在于新闻语义混入了媒体框架与报道偏好, 因此本家族对差异化的度量本质上是"媒体所呈现的战略独特性", 而非银行内部战略文档的独特性, 使用时须在构念效度上明确这一层媒介。正因如此, 本项目才在同一构念上并置 TF-IDF、LDA、嵌入三种方法与三条文本轨, 用方法与轨道的交叉稳健性来抵御任一单一表征基底的系统偏差。

【识别策略定位】
在识别层面, strat_diff_n5_emb 及其对偶多作为处理变量 (treatment) 或机制变量进入 strategic_diff 论文的回归, 其外生性并非天然成立: 一家银行的新闻叙事独特性可能与其规模、业务结构、市场地位等未观测异质性相关。因此该家族的因果解读依赖固定效应吸收 (银行与年份) 与工具变量策略 (面板 IV 列族: 同组 LOO 均值、广义 Bartik、媒体来源 house-style 暴露), 由 paper_spec 的 identification.iv 与对应 2SLS 模板承接。三条工具的直觉各不相同: 同组 LOO 均值利用同类同行的差异化水平作为暴露代理, 假设同组媒体环境冲击相关而个体特质外生; 广义 Bartik 把行业层面的语义冲击按各银行的初始暴露份额加权, 承接 Goldsmith-Pinkham 等与 Borusyak 等的份额/冲击外生性框架; 媒体来源 house-style 暴露则利用不同媒体固有的叙事风格差异, 把银行被哪些媒体报道视为准随机的暴露渠道。需要清醒认识到, 新闻叙事的独特性可能同时是银行真实战略选择的结果、也是媒体报道偏好的产物, 因此把本列当作纯粹外生的处理变量会有反向因果与遗漏变量之虞 — 正是这一内生性顾虑决定了本家族在 strategic_diff 论文中必须搭配固定效应与工具变量, 而非直接做 OLS 的因果解读。一个必须反复强调的口径铁律是: 本家族天然是多轨、多模型、多邻域 N 的规格族, 但这些平行测度彼此是"各自 just-identified 并排、互为稳健性、不分主次"的关系, 严禁把 MAIN 轨与 _lg 轨、或不同 N、或不同文本轨的多个孤儿工具混进同一个 over-identified 的 Hansen J 过度识别统计里 — 那样做会用同一构念的不同测量制造虚假的过度识别自由度, 破坏检验的可解释性。两条 co-primary 嵌入轨各自并排跑 just-identified 规格, 互为跨厂商稳健性佐证, 这与项目在情感 LLM 三家、BERT 三模型、政治词权重梯子上的纪律完全一致。一个具体的操作后果是: 在编写 strategic_diff 论文的复现 do 文件时, 若研究者希望同时展示 MAIN 与 _lg 两轨的结果, 正确做法是分列两张并排的 just-identified 回归表 (或同表两栏并置), 而非把两轨工具塞进同一 ivreg2 的工具集去做过度识别检验; 后者会人为制造并不存在的过度识别自由度, 并让 Hansen J 的拒绝/不拒绝失去构念意义。因为 MAIN 与 _lg 测的是同一"战略差异化"构念的两次不同嵌入实现, 它们在总体层面共享同一潜在真值, 用一个去工具化另一个既无外生性依据、也违背 co-primary 对等互证的设计初衷。

【与相邻测度的构念区分】
本家族须与三类相邻测度严格区分。其一, 与同在 strategic_diff 模块的 TF-IDF 轨 (strat_diff_n5、strat_diff_n5_w) 和 LDA 轨 (strat_diff_n5_lda) 区分: 三类方法测的是同一"最近邻战略差异度"构念, 但表征基底不同 — char/word 级 TF-IDF 捕捉表层词汇重合、LDA 捕捉主题分布距离、嵌入捕捉稠密语义等价; 三者互为稳健性检验, 且值域口径不同 (TF-IDF/LDA∈[0,1], 嵌入∈[0,2]), 不可直接比水平, 只可比标准化系数。其二, 与相似度类列 strat_sim_max_emb 区分: 后者取"到任一同行的最大相似度"、方向相反 (相似度高=差异化低), 且值域 [−1,1]; 本家族是"到 5 个最近邻的平均距离", 是聚合而非极值口径。其三, 与全行业质心距离 centroid_diff_emb 区分: 后者度量的是银行到整个行业质心的距离 (相对全行业中心的偏离), 本家族度量的是到局部最近邻簇的距离 (相对最相似同行的偏离); 前者是全局独特性、后者是局部独特性, 在同业高度分层时两者可显著背离。Steck 等 (2024) 提醒余弦相似度在某些嵌入几何下未必对应直觉的语义相似, 这也是本项目不单押一种测度、而以 TF-IDF/LDA/嵌入三方法并置互证的方法论审慎所在。第四, 与家族外相邻族的构念边界: 本家族测的是"银行 vs 银行"的战略差异化, 与网络溢出族测的"银行∧银行"结构指标、或情感族测的语调倾向属完全不同的构念空间, 命名上虽同带 strat 前缀却不可混用; 尤其须注意 strat_fluidity (市场流动性, 承接 Hoberg 等 2014 年的产品市场威胁度量) 测的是相邻期文本变动幅度而非同期同业差异, 与本家族的横截面最近邻距离正交。方法学上还可与近年基于文本风险披露构造企业间语义网络的研究相互印证: Li, Yuan, Zhu, Emrouznejad, Hao, & Jin (2026, Annals of Operations Research) 用文本风险披露构造企业间语义网络与连通性测度, 与本家族以新闻文本嵌入距离刻画银行间战略差异化的最近邻思路方法学同源, 两者都把"文本语义空间中的相对位置"作为主体间关系强弱的连续代理。

【已知局限与稳健性梯子】
已知局限有四。第一, 嵌入几何依赖: 不同模型的向量空间各向异性程度不同, 余弦距离的绝对水平不可跨模型比较, 只能比经标准化的回归系数 — 这是 co-primary 双轨设计的直接后果, 也是 Steck 等 (2024) 与 Rodriguez & Spirling (2022) 反复警示的陷阱。第二, 邻域 N 的选择敏感性: N=5 是承接文献的常用设定而非唯一真值, 故物化了 N∈{10,20,30,40,50} 大邻域梯子作为稳健臂, 各 N 值各自 just-identified 并排、禁混同一 Hansen J。第三, 文本轨口径: 三轨 (full/ctx/ss) 分别对应全文、实体窗口与同句共现三种信噪权衡; full 轨信息最全但可能稀释银行金科主题, ss 轨最聚焦但在无同句共现时按镜像 ctx 的回退语义退化为全文 body (ss_is_fallback=True, 共享 n_articles 分母)。第四, 样本深度: 在 T=2 的本机开发面板上, 同年可比同行数量偏少时最近邻集合不稳定 — 当同期银行总数逼近或不足 N+1 时, 最近邻集合几乎覆盖全体同业, 差异度退化为到全行业的平均距离, 失去"局部独特性"的鉴别力; 生产 T=19、覆盖 2007–2025 全量语料的面板方能充分识别, 届时同期横截面银行数量充足, N=5 邻域才真正落在同业分布的局部。第五, 聚合口径的选择敏感性: 银行-年画像由篇级向量聚合而来, 聚合方式 (等权平均 vs 报道量加权) 会影响头部媒体密集报道年份的画像, 这一维度当前固定, 未展开为独立梯子, 属刻意的复杂度收敛而非疏漏, 后续若有必要可作为增量梯子单独物化, 但须警惕与既有轨/模型/N 维度的列数组合爆炸。第六, 嵌入缓存与确定性: 嵌入族受 NEWS_PROCESS_LLM_OFFLINE 守卫, 缓存 0-miss 时可离线零成本字节级复现, 但换嵌入模型属受控全量重生事件, 须先删盘上冻结阈值文件并披露厂商与维度变更的数值副作用。稳健性梯子因而是多维正交并置的: co-primary 双轨 (Qwen 与 text-embedding-3-large) × 三文本轨 (full/ctx/ss) × 邻域 N 梯子 × 三表征方法 (TF-IDF/LDA/嵌入); 每一维的各臂都是"互为稳健性、不分主次"的 just-identified 规格并排, 跨模型的正式族错误率控制由根级 rwolf 模板承担, 而本族内部的多轨多 N 属规格稳健性并排, 不设 FWER 模板, 更严禁把任意两臂的工具混进同一 over-identified Hansen J。

## VAR: strat_diff_n5_emb

【变体差分】
本列是家族的 canonical 核心列, 也是 co-primary 双轨中的 MAIN 无后缀轨。其精确语义为: 以硅基流动 Qwen3-Embedding-8B (4096 维) 编码的 full 轨文本 (content_full = 标题 prepend + 全文正文) 为基底, 在银行-年聚合后计算目标银行到同年语义空间中 5 个最近邻同行的平均余弦距离, 值域 [0,2]。相对家族内其它列, 它的三项定位标记全部取"基准值": 嵌入模型=Qwen (无后缀即 MAIN 轨); 文本轨=full (承接留篇门控 full-only 口径, 无 _ctx/_ss 后缀); 邻域 N=5 (canonical 邻域数)。命名上须注意生产列约定: n5_emb 族的 full 轨为裸名 (无 _full 后缀), 这与其它带 _full 的族不同, 属历史命名产物而非"主次"含义 — 无后缀绝不意味它比 _lg 或 ctx/ss 更"主", 双轨与三轨均为并排的 just-identified 测度。作为 strategic_diff 论文的处理变量 candidate, 本列进入以银行与年份固定效应吸收的回归, 并由面板 IV 列族提供外生变异。它与其 _lg 对偶 strat_diff_n5_emb_lg 构成跨厂商 both-or-neither parity: 两轨列名严格双射, 任一嵌入为 None 时两列同置 NaN, 无单边孤儿。铁律复述: 本列与 _lg 对偶、与 ctx/ss 三轨、与 N∈{10..50} 大邻域梯子各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 其余轨/模型/N 的绝对水平不可跨轨直接比较, 只可比标准化系数。相较相似度列它是距离口径 (高=差异化高), 相较质心距离列它是局部最近邻口径 (相对最相似同行而非全行业中心)。在使用上, 本列适合作为战略差异化的首选连续代理进入基线回归, 并以其 _lg 对偶、三文本轨、N 梯子的对应列作为并排的稳健性佐证。须再次澄清"canonical"一词在此处的确切含义: 它指本列是家族无后缀的基准命名与首选报告轨, 而非指它在测量上优于其它轨或模型 — 双轨为 co-primary、三轨为并排规格、各 N 为并排邻域, 谁也不从属于谁。对读者最容易产生的误解是把无后缀等同于"主指标、其余为稳健性检查", 这一误解在项目口径下是错误的: 生产标签刻意以 co-primary 对称标注表达对等, 严禁 robust/robustness check 措辞。最后重申工程契约: 本列与 strat_diff_n5_emb_lg 严格 parity, 二者列名双射、缺失同置 NaN、无单边孤儿; 编码所依赖的 full 轨文本、Qwen 嵌入、银行-年聚合与 N=5 最近邻检索四要素中的任一项发生口径变更, 都会同时影响本列及其全部轨/模型/N 亲缘列, 属牵一发动全身的家族级改动, 须走受控全量重生并披露数值副作用。从解读角度补充一层大白话: 本列取值越大, 说明这家银行当年在金融科技叙事上越"离群"、越难在同业里找到跟它讲同一个故事的伙伴; 取值越小, 说明它的报道语义高度扎堆于行业主流话语, 缺乏辨识度。落到实证假设上, 战略管理的最优独特性传统提醒我们, 差异化与绩效未必单调正相关 — 过度独特会损失合法性、过度趋同会失去辨识, 因此本列既可用于线性效应检验, 也可平方项进入回归以检验倒 U 型关系, 具体设定由 strategic_diff 论文的理论假设决定。还需强调本列与同族 strat_sim_max_emb 的方向相反关系: 后者是"到任一同行的最大相似度", 与本列的"到最近邻的平均距离"在构念上互补但非简单取负, 因为一个取极值 (最像的那一家)、一个取局部聚合 (最像的五家均值), 在同业分层明显时二者可给出不同排序, 因此二者并列而非互替。最后从数据血缘角度收束: 本列的每一次取值都可追溯到 stage 14 物化的 content_full、stage 25 的 Qwen 嵌入向量、strategic_diff 的银行-年聚合与最近邻检索这条完整链路, 任一环节的口径变动都须经受控重生并在手稿的数据附录中如实披露, 尤其是从 Google/Gemini 系嵌入迁移到阿里 Qwen 系所带来的向量空间与厂商维度变更, 属必须向读者交代的方法学事实。

## VAR: strat_diff_n5_emb_ctx

【变体差分】
本列是 canonical MAIN 轨的 ctx 文本轨稳健性变体。与基准列 strat_diff_n5_emb 的唯一差分在于文本轨: 它以 content_ctx (标题 prepend + 银行/金科实体上下文窗口) 而非全文正文为编码输入, 嵌入模型仍为 MAIN 轨 Qwen3-Embedding-8B (4096 维), 邻域仍为 N=5, 值域仍为 [0,2]。ctx 轨的设计意图是在保留银行金科主题聚焦度的同时压制全文其它无关叙事对语义画像的稀释, 因而是 full 轨的条件稳健性轨 (行宇宙为 full 留篇集的子集, per-track 列照算)。按项目 2026-06-29 确立的 full-only 留篇门控口径, 一篇报道是否被判为"银行金科报道"只看 full 轨的 llm_verified_full, ctx/ss 因而降为 conditional-on-full 的测度轨与稳健性轨, 不参与留篇判定。它与 full 轨、ss 轨构成三轨规格族: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨的工具混进同一 over-identified Hansen J。ctx 与 full 的距离绝对水平因文本口径不同而不可直接比较, 只可比经标准化的回归系数。它同时有跨厂商对偶 strat_diff_n5_emb_lg_ctx, 构成 both-or-neither parity。使用场景上, 本列适合作为 full 轨基准结果的第一道文本轨稳健性检验: 当审稿担心全文正文中的无关叙事稀释了银行金科主题, 从而质疑 full 轨差异度的构念效度时, 以实体窗口聚焦后的 ctx 轨给出方向一致的结果, 即可支撑"结论不由全文噪声驱动"的论断。须再次锚定 full-only 门控口径: ctx 轨本身不参与"是否一篇银行金科报道"的留篇判定, 该判定只看 full 轨 llm_verified_full, 因此 ctx 轨的行宇宙严格是 full 留篇集的子集, per-track 列在此子集上照常计算。

## VAR: strat_diff_n5_emb_lg

【变体差分】
本列是 canonical 列的跨厂商 co-primary 对偶, 也是家族第二个核心列。与 MAIN 轨 strat_diff_n5_emb 的唯一差分在于嵌入模型: 它以 OpenAI/yunwu 的 text-embedding-3-large (3072 维) 而非 Qwen3-Embedding-8B (4096 维) 编码同一 full 轨文本, 邻域仍为 N=5, 距离口径与值域 [0,2] 完全一致。设立 _lg 轨的根本动机是嵌入模型敏感性: 如 Rodriguez & Spirling (2022) 所论, 下游文本度量会随嵌入空间几何而变, 因此项目对每一嵌入测度维持两条来自不同厂商、不同维度、不同训练语料的主测度轨, 互为跨厂商稳健性佐证。须强调二者是 co-primary 关系 — 两轨同为主测度、互为稳健性、严格 parity, 绝非"主 + 稳健性检查"的从属关系; 生产标签中亦刻意规避 robust/robustness check 措辞, 以 co-primary 对称标注表达对等互证。工程上二者构成 both-or-neither: 列名严格双射, 任一嵌入为 None 时同族两列同置 NaN, 无单边孤儿; _lg 轨的嵌入缓存键固定为 ('text-embedding-3-large', 对应 text_pipeline_version), 不走 MAIN 轨的版本解析。因维度与向量空间不同, _lg 与 MAIN 轨的距离绝对水平不可直接比较, 只可比标准化系数。铁律复述: MAIN 与 _lg 两条 co-primary 各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 这与项目在三轨、政治词权重、LLM 三家/BERT 三模型上的过度识别纪律完全一致。作为核心列, 本列同样是 strategic_diff 论文可选的处理变量, 与 MAIN 轨并排提供跨厂商稳健的差异化测度。之所以把 _lg 轨也列为核心而非附属稳健臂, 恰恰是为了在文档层面固化"跨厂商双轨对等"这一设计承诺 — 若把 _lg 降为普通稳健性列, 就会在心智上重建"主 + 辅"的等级, 与 co-primary 初衷相悖。使用建议是: 当审稿关注嵌入模型选择是否驱动结论时, 并排报告 MAIN 与 _lg 两轨的 just-identified 结果即可给出跨厂商稳健性证据, 二者系数方向与显著性一致则结论稳健, 而其绝对水平因维度与向量空间不同本就不可比。text-embedding-3-large 与 Qwen3-Embedding-8B 分属不同厂商、不同训练语料与不同维度 (3072 vs 4096), 二者在 MTEB/FinMTEB 类基准上各有所长, 正是这种来源异质性使双轨互证具有实质意义, 而非同一模型的两次噪声抽样。工程上再次强调 both-or-neither 的对称降级: 若某银行-年因语料稀疏导致任一轨嵌入为 None, 则本列与 MAIN 轨对应列一并置 NaN, 绝不留下单边有值的孤儿, 以此杜绝双轨样本不一致造成的伪差异。进一步澄清本列与 MAIN 轨核心列 strat_diff_n5_emb 的关系: 二者构念完全相同 (N=5 最近邻 full 轨嵌入距离), 差异仅在编码模型一项, 因此二者的相关性预期很高但不会是 1 — 正是这不完全的一致性携带了"嵌入模型选择是否影响结论"的稳健性信息。若二者高度一致, 说明差异化度量对嵌入模型稳健; 若在某些银行-年出现显著背离, 则提示这些主体的语义画像对模型的向量几何较敏感, 值得在稳健性讨论中单列。text-embedding-3-large 为 3072 维、Qwen3-Embedding-8B 为 4096 维, 维度差本身即意味着两空间的距离刻度不可通约, 这也是本列绝不能与 MAIN 轨列比绝对水平、只能比标准化系数的根本原因。就论文写作而言, 建议在主表报告 MAIN 轨、在稳健性附表并排报告本 _lg 轨, 并以一句话说明二者系数方向与显著性一致, 即完成跨厂商稳健性的交代; 切忌在正文暗示 _lg 是"次要检查", 以免与 co-primary 对等设计自相矛盾。作为核心列, 本列的血缘同样可追溯到 content_full、text-embedding-3-large 嵌入向量、银行-年聚合与 N=5 最近邻检索四要素, 任一变更牵动全族。

## VAR: strat_diff_n5_emb_lg_ctx

【变体差分】
本列在 _lg co-primary 轨内取 ctx 文本轨, 是 strat_diff_n5_emb_lg 的 ctx 稳健性变体, 亦即 strat_diff_n5_emb_ctx 的跨厂商对偶。它相对核心列 strat_diff_n5_emb_lg 的唯一差分是文本轨 (content_ctx: 标题 prepend + 实体上下文窗口), 嵌入模型仍为 text-embedding-3-large (3072 维), 邻域仍为 N=5, 值域 [0,2]。它同时承载两个正交的稳健性维度: 一是嵌入模型维 (_lg 相对 MAIN), 二是文本轨维 (ctx 相对 full)。按 full-only 门控口径, ctx 轨为 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集。它与 strat_diff_n5_emb_ctx 构成 both-or-neither parity: 两列名严格双射, 任一嵌入缺失同置 NaN。铁律复述: 该列所在的 co-primary 双轨、三文本轨、N 梯子诸维的各臂均为各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ctx 与 full、_lg 与 MAIN 的距离绝对水平因口径不同不可直接比较, 只可比标准化系数。它在稳健性矩阵中处于"跨厂商 × ctx 轨"的交叉格: 若 MAIN-full、MAIN-ctx、_lg-full 三格结论一致而唯独本格背离, 通常提示 ctx 轨与 _lg 模型的交互效应值得单独审视, 而非某一维单独的问题。工程契约同前: 与 strat_diff_n5_emb_ctx 严格 parity、缺失同置 NaN、无单边孤儿; _lg 轨嵌入缓存键固定为 text-embedding-3-large 对应版本, 不走 MAIN 轨版本解析, 换模属受控重生事件。铁律再述: 本列所在的双轨、三轨、N 梯子诸维各臂各自 just-identified 并排、互为稳健性、不分主次, 严禁把任意两臂工具混进同一 over-identified Hansen J。

## VAR: strat_diff_n5_emb_lg_ss

【变体差分】
本列在 _lg co-primary 轨内取 ss (同句共现) 文本轨, 是 strat_diff_n5_emb_lg 的 ss 稳健性变体, 亦即 strat_diff_n5_emb_ss 的跨厂商对偶。它相对核心列 strat_diff_n5_emb_lg 的唯一差分是文本轨: 以 content_ss (标题 prepend + 银行∧金科同句±N 窗) 而非全文为编码输入, 嵌入模型仍为 text-embedding-3-large (3072 维), 邻域 N=5, 值域 [0,2]。ss 轨是三轨中信噪最聚焦的一轨, 仅保留银行与金科词同句共现的语义片段; 其回退语义镜像 ctx 轨 — 当某篇无银行∧金科同句共现时, content_ss 退化为全文 body、ss_is_fallback=True, 且与其它轨共享 n_articles 分母; 若 FINTECH_AC=None 则 ss_is_fallback 全 True 优雅降级。按 full-only 门控, ss 轨同为 conditional-on-full 测度轨, 行宇宙为 full 留篇集子集。它与 strat_diff_n5_emb_ss 构成 both-or-neither parity。铁律复述: 三文本轨与 co-primary 双轨、N 梯子诸维各臂均各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; ss 轨因文本口径最窄, 其距离水平与 full/ctx 尤不可直接比较, 只可比标准化系数。在 T=2 开发面板上, ss 轨因同句共现稀疏而大量回退, 差异度可能退化甚至零方差, 属预期的样本退化而非缺陷; 生产 T=19 语料下同句共现样本充足, ss 轨才能给出与 full/ctx 有实质区分的最聚焦画像。使用上, 本列是"跨厂商 × 最严格文本口径"的交叉稳健臂, 适合回应"结论是否只在宽口径全文下成立"的质疑 — 若在仅保留银行金科同句片段的最窄语义下方向依旧一致, 则构念效度得到最强支撑。

## VAR: strat_diff_n5_emb_ss

【变体差分】
本列是 canonical MAIN 轨的 ss (同句共现) 文本轨稳健性变体。与基准列 strat_diff_n5_emb 的唯一差分在于文本轨: 以 content_ss (标题 prepend + 银行∧金科同句±N 窗, 窗宽由 filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 为编码输入, 嵌入模型仍为 MAIN 轨 Qwen3-Embedding-8B (4096 维), 邻域 N=5, 值域 [0,2]。ss 轨的意图是把语义画像收敛到银行与金融科技真正同句共现的叙事片段, 最大程度剔除无关背景, 因而是三轨中最聚焦、也最易因共现稀疏而退化的一轨。其回退语义镜像 ctx: 无同句共现时 content_ss 退化为全文 body、ss_is_fallback=True, 共享 n_articles 分母。按 2026-06-29 full-only 门控口径, ss 轨为 conditional-on-full 的测度/稳健性轨, 不参与留篇判定, 行宇宙是 full 留篇集子集。它与 full 轨、ctx 轨构成三轨规格族, 并有跨厂商对偶 strat_diff_n5_emb_lg_ss 构成 both-or-neither parity。铁律复述: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨工具混进同一 over-identified Hansen J; ss 轨距离水平因文本最窄, 与 full/ctx 不可直接比较, 只可比标准化系数。须留意 ss 与 ctx 在回退语义上的对称: 二者均在无目标共现时退化为全文 body 并共享 n_articles 分母, 区别仅在于共现判据 (ss=严格同句、ctx=实体窗口), 因此二者不是冗余轨, 而是同句 vs 窗口两种聚焦粒度的并排规格。在 MAIN 轨内, 本列与 full 轨、ctx 轨共同构成三轨规格族的完整闭环, 与 _lg 轨对偶 strat_diff_n5_emb_lg_ss 逐列 parity。

<!-- rendered-citations:begin -->
Arts, S., Cassiman, B., & Hou, J. (2025). Technology differentiation, product market rivalry, and M&A transactions. Strategic Management Journal, 46(4), 837-862. https://doi.org/10.1002/smj.3687
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance Massive Text Embedding Benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing [Preprint]. https://doi.org/10.18653/v1/2025.emnlp-main.179
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The effects of sentiment evolution in financial texts: A word embedding approach. Journal of Management Information Systems, 41(1), 178-205. https://doi.org/10.1080/07421222.2023.2301176
Steck, H., Ekanadham, C., & Kallus, N. (2024). Is cosine-similarity of embeddings really about similarity? Companion Proceedings of the ACM Web Conference 2024, 887-890. https://doi.org/10.1145/3589335.3651526
Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Improving text embeddings with large language models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2401.00368
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics [Preprint]. https://doi.org/10.18653/v1/2023.eacl-main.148
Rodriguez, P. L., & Spirling, A. (2022). Word embeddings: What works, what doesn't, and how to tell the difference for applied research. The Journal of Politics, 84(1), 101-115. https://doi.org/10.1086/715162
Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., ... Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2201.10005
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing, 3980-3990. https://doi.org/10.18653/v1/D19-1410
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research. https://doi.org/10.1007/s10479-026-07305-8
<!-- rendered-citations:end -->
