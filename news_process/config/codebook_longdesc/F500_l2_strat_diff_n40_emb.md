---
family_id: F500
columns:
- strat_diff_n40_emb
- strat_diff_n40_emb_ctx
- strat_diff_n40_emb_lg
- strat_diff_n40_emb_lg_ctx
- strat_diff_n40_emb_lg_ss
- strat_diff_n40_emb_ss
unit: 无量纲距离得分 (值域约 [0,2], 余弦距离=1-cos(θ))
formula: 'strat_diff_n40_emb = mean_{j∈N40(i)}(1 - cos(v_i, v_j)); 先按银行-年度聚合该行该年度全部留篇报道文本为单一 agg_text, 再对同一批银行-年度文档两两编码取余弦相似度矩阵; N40(i) = 与银行-年度 i 的聚合文档余弦相似度最高的 40 个同期其它银行-年度聚合文档, 对这 40 个余弦距离取均值; 近邻检索发生在银行-年度层面, 不在文章层面'
producer: pipeline\panel\stata_export.py (标签装配) 上游算子见 pipeline\features\strategic_diff.py (`_emb_main` 主嵌入入口 + top-k N 扩展派生循环)
upstream: [25_article_sbert]
citations:
- doi: "10.1287/mnsc.2022.4369"
  type: journal
  authors: "Guzman, J., & Li, A."
  year: 2023
  title: "Measuring Founding Strategy"
  venue: "Management Science"
  vol: "69"
  issue: "1"
  pages_or_artno: "101-118"
- doi: "10.1086/688176"
  type: journal
  authors: "Hoberg, G., & Phillips, G."
  year: 2016
  title: "Text-Based Network Industries and Endogenous Product Differentiation"
  venue: "Journal of Political Economy"
  vol: "124"
  issue: "5"
  pages_or_artno: "1423-1465"
- doi: "10.1002/smj.2978"
  type: journal
  authors: "Haans, R. F. J."
  year: 2019
  title: "What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories"
  venue: "Strategic Management Journal"
  vol: "40"
  issue: "1"
  pages_or_artno: "3-27"
- doi: "10.1007/s11142-024-09821-z"
  type: "journal"
  authors: "Li, N."
  year: 2025
  title: "Labor market peer firms: understanding firms’ labor market linkages through employees’ internet “also viewed” firms"
  venue: "Review of Accounting Studies"
  vol: "30"
  issue: "1"
  pages_or_artno: "384-435"
- doi: "10.1080/1540496x.2025.2479064"
  type: "journal"
  authors: "Wang, Q., Xiang, C., Xin, Z., & Li, C."
  year: 2025
  title: "The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China"
  venue: "Emerging Markets Finance and Trade"
  vol: "61"
  issue: "11"
  pages_or_artno: "3595-3611"
- doi: "10.1109/cifer62890.2024.10772990"
  type: "journal"
  authors: "Vamvourellis, D., Tóth, M., Bhagat, S., Desai, D., Mehta, D., & Pasquali, S."
  year: 2024
  title: "Company Similarity Using Large Language Models"
  venue: "2024 IEEE Symposium on Computational Intelligence for Financial Engineering and Economics (CIFEr)"
  pages_or_artno: "1-9"
new_dois: []
---

## CORE

【构念与来源】
strat_diff_n40_emb 是本项目"文本战略距离/差异化"测度族 (strat_diff_*) 在 top-k 近邻梯子 N=40 档位上的具体实现, 度量银行 i 在给定年度的涉该行金融科技相关报道, 在嵌入语义空间中与其"最近的 40 篇同期报道"平均余弦距离有多远。距离越大, 说明该行的报道文本在语义上与整个报道语料池中最相似的一批同侪越不趋同, 可解读为该行在媒体呈现的战略/业务叙事上越"独树一帜"; 距离越小, 说明该行的报道文本落在语义高密度区, 与大量其它报道高度雷同 (常见于模板化、套话化的通稿型报道, 或该行业务定位与同业高度同质)。这一构念直接承袭 Guzman & Li (2023, Management Science)"Measuring Founding Strategy"提出的文本近邻距离法: 用企业文本描述的嵌入向量, 计算其与语料库中最近 K 个邻居的平均距离, 以此刻度企业战略的独特性/差异化程度, 越远越独特。本项目将该方法从企业招股书/简介文本迁移到银行金融科技相关新闻报道文本, 用同一逻辑度量"银行在媒体叙事中的战略辨识度", 呼应 Hoberg & Phillips (2016, Journal of Political Economy) 文本网络产业与内生产品差异化的思路——二者共享"文本相似度矩阵→距离/差异化得分"的方法学骨架, 但 Hoberg & Phillips 用于产业分类与竞争边界界定, 本项目用于刻画单一银行相对于全体报道语料的媒体叙事差异化程度, 是同一方法家族在不同应用场景下的具体化。

【方法学与计算】
strat_diff_n40_emb 家族的计算流程分三步, 关键之处在于近邻检索发生在银行-年度层面而非文章层面: 第一步, 对每个年度, 先把该行该年度全部满足留篇条件的报道文本 (依轨道不同取 full/ctx/ss 三种预处理口径) 聚合拼接成一份该银行-年度专属的聚合文档 agg_text (即"把一整年这家银行的所有涉金科报道揉成一篇长文"), 再用 co-primary 嵌入引擎把这份聚合文档编码为定长稠密向量, 主轨引擎为 Qwen/Qwen3-Embedding-8B (硅基流动 API, 4096 维) ——因此每个银行-年度只产生一个向量, 而非每篇报道各自一个向量; 第二步, 对同一年度内全部银行-年度聚合向量两两计算余弦相似度, 对每个银行-年度取相似度最高的 N=40 个其它银行-年度邻居 (N 是本梯子固定的近邻规模超参, 家族名中的 "n40" 即此), 对这 40 个余弦距离 (1 减余弦相似度) 取算术平均, 直接得到该银行-年度的 strat_diff_n40 分数; 第三步, 由于第一步已在银行-年度层面聚合完毕, 此处不再有文章级到银行-年度级的再聚合环节, 该分数即为面板级 strat_diff_n40_emb 及其各变体列的最终取值。换言之, "40 个最近邻"检索的对象是该年度池中另外 40 个"最像的银行", 而不是 40 篇报道; 一家银行某年度全部报道先被压缩为一个语义代表点, 再拿这个代表点去和同期其它银行的代表点比较距离。top-k 近邻规模本身构成一条稳健性梯子, N=5 为 Guzman & Li (2023) 论文推荐的基准值 (baseline), N∈{3,4,6,7}∪{10,20,30,40,50} (含本家族 N=40) 均属敏感性/稳健性检验档位, 与基准 N=5 并非对等地位——本家族 N=40 是非基准梯子成员之一, 而非另一个基准。梯子内各 N 值档位彼此各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定——这是本项目对全部梯子型测度族 (含消融梯度、阈值梯子、per-model 子测度) 统一奉行的识别铁律, 目的是避免把本质上是同一构念的不同刻度选择错误地当作独立工具变量堆叠进单一超识别系统, 从而制造虚假的过度识别检验通过率。N=40 在这条梯子里是偏大邻域档位, 相较 N=5 基准把比较对象扩到更大范围的同期银行, 邻域越宽越可能把原本不太相似的银行也纳入近邻集合, 从而在一定程度上稀释差异化信号的区分度, 在稳健性附表中通常与 N=10/N=20/N=30 等其它大 N 档位并列呈现, 用以检验"差异化排序结论是否随邻域宽度单调漂移"。

家族内 6 列沿两个正交维度展开: 一是文本轨道 (full 全文/ctx 实体窗口/ss 银行∧金科同句窗口), 三轨各自独立聚合出银行-年度文档、独立计算相似度矩阵与近邻集合, 不互相借用, 各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J; 二是嵌入引擎 (无后缀=Qwen3-Embedding-8B 硅基流动主轨, `_lg`=text-embedding-3-large OpenAI/OpenLux 端点), 两条嵌入引擎彼此 co-primary、both-or-neither (任一银行-年度聚合文档嵌入失败, 同族两条轨道列同置缺失, 不产生单边孤儿), 严格 parity、互为稳健性不分主次, 同样禁止混入同一 over-identified Hansen J。ctx/ss 轨道的分母遵循留篇门控 full-only 口径 (2026-06-29 起): 是否判定"一篇银行金科报道"只看 full 轨 LLM 情感验证结果, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 其纳入聚合文档的文章行宇宙是 full 留篇集合的子集, 但每轨自身聚合文档、相似度矩阵与 top-40 银行-年度近邻集合仍按该轨自身文本独立计算。ss 轨若某篇纳入聚合的文章无银行∧金科同句共现, 回退语义镜像 ctx: 该篇对应文本片段退化为全文 body 文本 (`ss_is_fallback=True`), 与 ctx 的回退处理对称一致, 不额外制造语义偏差。

【文献定位】
文本近邻距离刻度差异化的方法源头是 Guzman & Li (2023, Management Science)"Measuring Founding Strategy": 该文用企业自我描述文本的嵌入表示与其 K 近邻的平均距离度量创业战略独特性, 是本家族 top-k 近邻算子的直接方法出处。Hoberg & Phillips (2016, Journal of Political Economy) 的文本网络产业分类同样以两两余弦相似度为底层原语构造产业边界与产品差异化度量, 为"文本相似度矩阵→差异化得分"这一方法路径提供了更早的顶刊范式确认, 是本家族方法学谱系上的另一关键锚点。Haans (2019, Strategic Management Journal) 则从战略管理理论侧提出"最优显著性"框架, 指出组织在同质与异质类别情境下, 差异化对绩效的边际效应并非单调, 为 strat_diff 类测度在下游回归中的非线性/情境依赖设定提供了理论支持, 呼应本项目后续对该测度族做异质性分析时的理论预期。三条文献分别覆盖"方法算子出处—方法学范式确认—构念的经济/组织理论解释", 共同支撑 strat_diff_n40_emb 从"能算出一个数"到"这个数在经济学上意味着什么"的完整论证链。 近年三条文献分别加固该链的不同环节。Li (2025) 由员工在职业社交平台上"也浏览了"的共现关系导出一套不依赖 SIC/GICS 的同业集合, 并实证证明该数据驱动 peer 集合与传统行业分组仅部分重叠、且在解释股票收益与会计业绩共动上具增量解释力, 捕捉了行业代码遗漏的企业间联结, 据此锚定本族"同业集合由相似度检索给定、而非由行业代码外生指定"的核心设计前提; 边界在于其 peer 来源为浏览行为网络共现而非文本嵌入余弦相似度, 样本为美国上市公司-年, 且原文不构造任何差异化得分, 更未取 top-k 邻域内的距离均值。Wang、Xiang、Xin 与 Li (2025) 在中国上市公司样本上以产品文本相似度定义同业集合并据此识别同业间影响, 提供"文本相似度定义的同业集合在中国语境下可用且有解释力"的同域应用证据; 但其语料为公司自述的年报产品描述、向量化为 TF-IDF 词频空间, 与本族的第三方媒体报道 (他述) 及神经嵌入表征在文本生成机制与向量空间上均不同, 且原文将同业集合用于 peer effect 回归, 而非取余弦距离均值作差异化得分。Vamvourellis、Toth、Bhagat、Desai、Mehta 与 Pasquali (2024) 用 LLM 从企业业务描述学习公司嵌入, 并以嵌入余弦相似度重建 GICS 行业分类作为效度检验, 证明神经嵌入空间中的公司余弦相似度确实承载行业与业务可比性信息, 这正是本族 _emb 轨以 1−cos(v_i, v_j) 度量银行-年度间战略距离所依赖前提的方法学效度证据; 该条边界尤须明示: 语料是 SEC 备案的英文业务描述而非按银行-年度聚合的中文报道超级文档, 嵌入模型为其自训/微调 LLM 而非本项目的 Qwen3-Embedding-8B 与 text-embedding-3-large, 效度标尺为 GICS 复现而本族无对应行业分类标尺, 且原文止于相似度检索、未取 top-N 距离均值作差异化得分, 故只锚嵌入相似度的构念效度、不锚本族算子。
## VAR: strat_diff_n40_emb

【变体差分】
本列是 strat_diff_n40_emb 家族的 canonical 基准: 文本轨道取 full (标题+正文全文), 嵌入引擎取主轨 Qwen/Qwen3-Embedding-8B (硅基流动 API, 4096 维), top-k 近邻规模 N=40。计算上, 先把该银行该年度在留篇门控 (full-only, 以 llm_verified_full 判定) 后保留的全部报道文本 (物化列 content_full) 聚合拼接成一份该银行-年度专属的聚合文档, 再用 Qwen 主轨嵌入引擎把这份聚合文档编码为一个向量 (每个银行-年度恰一个向量, 而非每篇报道各自编码); 随后在同一年度全体银行-年度聚合向量构成的相似度矩阵中, 为该银行-年度检索余弦相似度最高的 40 个其它银行-年度邻居, 取这 40 个余弦距离的均值即为本列取值——近邻检索的对象是"另外 40 家最像的银行(-年度)", 不是 40 篇报道, 该银行-年度自身也不会先在文章层面各自寻邻后再取均值。本列在家族内二维 (轨道×嵌入引擎) 设计中占据"full×Qwen 主轨"这一格, 是下游回归表中通常作为 headline 陈述的档位, 但按本项目梯子测度统一铁律, 它与家族内其余 5 列仍是互为稳健性、不分主次的并排关系, 不因"常作为表头呈现"而在识别策略上享有特权地位, 也不得与其余轨道/引擎列混入同一超识别系统; 与本家族外的 N=5 基准档位相比, 本列 N=40 属敏感性检验梯子成员, 非基准。

从量纲上理解, 本列取值范围理论上落在 [0,2] 区间 (余弦距离=1-余弦相似度, 余弦相似度理论范围 [-1,1]), 但在真实新闻文本的高维语义嵌入空间中, 绝大多数聚合文档彼此的相似度都是正的, 因此实证观测值通常集中在较窄的中低区间, 数值越接近上限意味着该行该年度的聚合叙事与语料池中最相似的 40 家同期银行仍相去甚远, 属语义上的"孤例"战略叙事; 数值越接近下限意味着该行该年度的聚合叙事高度雷同于大量其它银行同期的报道, 常见于监管公告转载、格式化业绩快报、通稿型软文等模板化报道占比高的银行-年度。full 轨作为门控轨道, 其近邻检索池是当期全部满足留篇条件的银行-年度聚合文档 (不限于单一银行), 因此本列同时刻画了两层信息: 一是该行自身各篇报道压缩为单一叙事代表点后的整体语义定位, 二是该代表点相对于整个行业媒体叙事池的边际独特性, 两者在 full 轨上不作拆分, 由后续研究者按需在回归设定中控制年度或行业固定效应加以分离。

## VAR: strat_diff_n40_emb_ctx

【变体差分】
本列与 canonical 列 strat_diff_n40_emb 的唯一差分维度是文本轨道: 由 full 换为 ctx (实体窗口轨, 标题+目标银行/金科实体上下文窗口拼接, 由 stage 14 ctx_materializer 物化的 content_ctx 列), 嵌入引擎仍为 Qwen 主轨, top-k 规模仍为 N=40。ctx 轨的相似度矩阵与近邻检索均在该轨自身的向量空间内独立完成, 不与 full 轨共享近邻集合。行宇宙口径遵循留篇门控 full-only: 具体某篇文章是否计入"该行金融科技报道"仍由 full 轨 LLM 情感验证结果决定, ctx 只是在这一固定行集合上换用更聚焦实体窗口的文本重新编码与重新检索近邻, 属 conditional-on-full 的稳健性轨。若该篇文章无法构造有效实体窗口 (回退), content_ctx 按物化阶段既定回退规则处理, 相应 ctx_is_fallback 标记随之传递, 分母口径与 full 轨共享 n_articles 分母的处理保持项目统一约定。本列与 canonical 列、与同轨其它嵌入引擎列均为互为稳健性并排关系, 不分主次。

由于 ctx 轨的文本窗口比 full 轨窄得多 (只保留标题与目标实体附近的局部上下文, 而非全文), 其嵌入向量所携带的语义信息更聚焦于"银行与金科要素如何被并置描述", 相似度矩阵在这一更窄的语义子空间内构造, 因此本列与 full 轨 canonical 列的数值水平通常不完全一致——即便同一篇报道, 全文视角下可能因大量背景性、无关的段落内容而与其它报道产生更高的表面相似度, 实体窗口视角下则更容易凸显该行报道在"银行-金科关系描述"这一狭义主题上的独特措辞。这一差异正是设立 ctx 轨的意义所在: 检验 strat_diff_n40 的差异化排序结论是否仅是全文噪声的产物, 还是在聚焦核心叙事片段后依然成立。ctx 轨近邻检索池同样是当期全部满足留篇条件银行-年度的 ctx 聚合文档集合 (每银行-年度一份聚合文档、一个向量), 与 full 轨近邻池互不混用。

## VAR: strat_diff_n40_emb_lg

【变体差分】
本列与 canonical 列 strat_diff_n40_emb 的唯一差分维度是嵌入引擎: 由硅基流动 Qwen/Qwen3-Embedding-8B (4096 维) 换为 OpenAI/OpenLux 端点 text-embedding-3-large (3072 维), 文本轨道仍为 full, top-k 规模仍为 N=40。`_lg` 轨与无后缀主轨是本项目嵌入架构的 co-primary 双轨设计: 两条嵌入引擎同为主测度、互为稳健性、严格 parity, 列名双射 both-or-neither——即任一篇报道在某一嵌入引擎上编码失败, 该家族两条轨道对应列会同步置为缺失, 不产生只有一侧有值的单边孤儿。本列的相似度矩阵与近邻检索完全在 text-embedding-3-large 的 3072 维向量空间内独立完成, 不与 Qwen 主轨共享任何中间量, 用于验证 strat_diff_n40 的差异化排序结论是否对嵌入模型厂商选择 (阿里 Qwen vs. OpenAI) 稳健。按铁律, 本列与无后缀主轨列 just-identified 并排, 二者不得混入同一 over-identified Hansen J。

text-embedding-3-large 与 Qwen3-Embedding-8B 在训练语料构成、分词粒度、向量维度 (3072 vs. 4096) 上均存在系统性差异, 两者对同一中文金融新闻文本编码出的向量在几何结构上并不同构, 因此本列与 canonical 列的绝对数值水平原则上不可直接比较大小, 只应比较两者在银行-年度截面上的相对排序或标准化后的效应量是否一致。设立 `_lg` 引擎轨的核心动机是防范"differentiation 结论仅是某一厂商嵌入模型特有的几何伪影"这一威胁: 若 strat_diff_n40 在两条独立训练、独立厂商的嵌入引擎上都能得出方向一致的银行差异化排序, 则该测度所刻画的构念更可能是文本本身承载的真实语义差异, 而非模型特异的表征噪声。本列在换模型敏感性检验入口 (config/features.yaml::embedding_api 及其散落硬编码回退) 发生变更时须整体重算, 不与 Qwen 主轨共享缓存。

## VAR: strat_diff_n40_emb_lg_ctx

【变体差分】
本列同时叠加两个差分维度: 文本轨道为 ctx (实体窗口轨), 嵌入引擎为 `_lg` (text-embedding-3-large), top-k 规模仍为 N=40。它是家族内"轨道×引擎"二维设计矩阵中"ctx×_lg"这一格, 用以同时验证差异化得分对"文本预处理口径切换到实体窗口"与"嵌入引擎切换到 OpenAI/OpenLux 大模型"两个维度的联合稳健性。计算上先按 ctx 轨规则把该银行-年度留篇门控 (full 轨验证结果为准) 后的全部报道 content_ctx 文本聚合为一份银行-年度专属聚合文档, 再用 text-embedding-3-large 将该聚合文档编码为一个向量, 并在该轨该引擎专属的向量空间内为该银行-年度检索 40 个最近邻银行-年度, 取 40 个余弦距离的均值即为本列取值。与 strat_diff_n40_emb_ctx (同轨、主引擎) 相比, 二者仅嵌入引擎不同, 互为 co-primary 稳健性一对; 与 strat_diff_n40_emb_lg (同引擎、full 轨) 相比, 二者仅文本轨道不同, 互为三轨稳健性一员。本列与家族内其余 5 列均是并排、不分主次的关系, 任何两两组合都不得混入同一超识别系统。

在四种"轨道×引擎"组合中, 本列与 strat_diff_n40_emb_lg_ss 共享同一嵌入引擎但分处 ctx/ss 两个不同文本粒度的判据, 与 strat_diff_n40_emb 及 strat_diff_n40_emb_ctx 则共享 Qwen 主轨之外的另一条平行验证路径。该格存在的价值在于: 单纯换嵌入引擎或单纯换文本轨道各自只能排除一个维度的构念威胁, 而联合切换 (ctx 语境窗口收窄 + 跨厂商嵌入模型) 能同时压低"全文噪声主导差异化排序"与"结论系某一厂商嵌入模型特有几何伪影"两类威胁同时成立的联合概率, 是稳健性附表中论证力度较强但也最边际的一格, 通常与其余五列一并以规格曲线 (specification curve) 形式呈现, 而非单独作为主设定汇报。

## VAR: strat_diff_n40_emb_lg_ss

【变体差分】
本列同时叠加两个差分维度: 文本轨道为 ss (银行∧金科同句窗口轨, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认±1), 嵌入引擎为 `_lg` (text-embedding-3-large), top-k 规模仍为 N=40。ss 轨的文本判定口径比 ctx 更严格: 要求目标银行与金科关键词在同一句 (或半径窗口内) 共现, 若某篇文章不满足该条件, content_ss 回退为全文 body 文本, 回退语义与 ctx 轨镜像对称, 对应 ss_is_fallback 标记为 True, 与 full 轨共享同一 n_articles 分母。本列在 text-embedding-3-large 向量空间内对 ss 轨文本独立计算相似度矩阵与 top-40 近邻, 用于同时验证差异化得分对"共现判据收紧到严格同句"与"嵌入引擎切换到 OpenAI/OpenLux"两个维度的联合稳健性。它与 strat_diff_n40_emb_ss (同轨、主引擎) 构成 co-primary 稳健性一对, 与 strat_diff_n40_emb_lg_ctx (同引擎、ctx 轨) 构成三轨稳健性一对, 家族内全部两两关系均并排、不分主次, 严禁混入同一 over-identified Hansen J。

ss 轨的文本判据是三轨中最严格的一种, 要求目标银行实体与金科关键词落在同一句或极窄窗口内共现, 因此在部分银行-年度上有效样本量会明显小于 full/ctx 两轨 (回退比例较高), 叠加 `_lg` 引擎, 本列在样本极小的银行-年度上其估计噪声可能相对偏大, 使用时应结合有效篇数 (undropped n_articles) 判断该格数值的稳定性, 而非机械照搬。本列作为"最严格判据×跨厂商引擎"这一联合稳健性检验节点, 与 canonical 列的方向一致性若成立, 是该家族测度稳健性证据链中论证力度最强的一环, 但同样不因此获得优先呈现或替代 canonical 主设定的地位。

## VAR: strat_diff_n40_emb_ss

【变体差分】
本列与 canonical 列 strat_diff_n40_emb 的唯一差分维度是文本轨道: 由 full 换为 ss (银行∧金科同句共现窗口轨, 由 stage 14 ctx_materializer 物化的 content_ss 列), 嵌入引擎仍为 Qwen 主轨, top-k 规模仍为 N=40。ss 轨的判定原语与 stage 13 共现硬过滤所用的 "±1 句窗口" 判据不同口径 (ss 轨要求严格同句而非窗口邻近), 两者刻意区分、不可互相复用。留篇门控仍以 full 轨 LLM 验证为准, ss 轨只是在既定行宇宙上换用更严格的同句窗口文本重新编码、重新检索近邻。若该篇文章无银行∧金科同句共现, content_ss 回退为全文 body (回退语义镜像 ctx), ss_is_fallback 置 True, 分母与 full 轨共享。本列与家族内 strat_diff_n40_emb (同引擎、full 轨)、strat_diff_n40_emb_lg_ss (同轨、_lg 引擎) 分别构成三轨与 co-primary 两组稳健性关系, 各自 just-identified 并排、不分主次, 不得混入同一 over-identified Hansen J。

ss 轨相较 ctx 轨的额外价值在于把"银行与金科词是否真的在同一叙事单元 (同句) 里被提及"这一更强的相关性判据纳入文本预处理, 排除了 ctx 轨可能纳入的"实体窗口内但语义上并不直接关联"的干扰句子, 从而让近邻检索所依据的语义信号更纯粹地对应"银行-金科关系"这一核心构念, 而非被窗口内其它无关内容稀释。对该行某年度而言, 若 full/ctx/ss 三轨的差异化排序在方向上高度一致, 可认为 strat_diff_n40 所刻画的战略辨识度并非文本预处理口径选择的产物; 若三轨出现明显分歧, 则提示该行报道的"差异化"信号可能集中在背景性内容 (仅 full 轨捕捉到) 而非核心银行-金科叙事本身, 这一分歧信息本身也具有解释价值, 应在稳健性讨论中如实披露而非取舍。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the Value of Being Different When Everyone Is? The Effects of Distinctiveness on Performance in Homogeneous versus Heterogeneous Categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Li, N. (2025). Labor market peer firms: understanding firms’ labor market linkages through employees’ internet “also viewed” firms. Review of Accounting Studies, 30(1), 384-435. https://doi.org/10.1007/s11142-024-09821-z
Wang, Q., Xiang, C., Xin, Z., & Li, C. (2025). The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China. Emerging Markets Finance and Trade, 61(11), 3595-3611. https://doi.org/10.1080/1540496x.2025.2479064
Vamvourellis, D., Tóth, M., Bhagat, S., Desai, D., Mehta, D., & Pasquali, S. (2024). Company Similarity Using Large Language Models. 2024 IEEE Symposium on Computational Intelligence for Financial Engineering and Economics (CIFEr), 1-9. https://doi.org/10.1109/cifer62890.2024.10772990
<!-- rendered-citations:end -->
