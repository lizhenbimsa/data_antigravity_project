---
family_id: F493
columns:
- strat_diff_ctx
- strat_diff_full
- strat_diff_lg_ctx
- strat_diff_lg_full
- strat_diff_lg_ss
- strat_diff_n10
- strat_diff_n10_ctx
- strat_diff_n10_ss
- strat_diff_n10_w
- strat_diff_n10_w_ctx
- strat_diff_n10_w_ss
- strat_diff_n20
- strat_diff_n20_ctx
- strat_diff_n20_ss
- strat_diff_n20_w
- strat_diff_n20_w_ctx
- strat_diff_n20_w_ss
- strat_diff_n3
- strat_diff_n30
- strat_diff_n30_ctx
- strat_diff_n30_ss
- strat_diff_n30_w
- strat_diff_n30_w_ctx
- strat_diff_n30_w_ss
- strat_diff_n3_w
- strat_diff_n4
- strat_diff_n40
- strat_diff_n40_ctx
- strat_diff_n40_ss
- strat_diff_n40_w
- strat_diff_n40_w_ctx
- strat_diff_n40_w_ss
- strat_diff_n4_w
- strat_diff_n5
- strat_diff_n50
- strat_diff_n50_ctx
- strat_diff_n50_ss
- strat_diff_n50_w
- strat_diff_n50_w_ctx
- strat_diff_n50_w_ss
- strat_diff_n5_ctx
- strat_diff_n5_ss
- strat_diff_n5_w
- strat_diff_n5_w_ctx
- strat_diff_n5_w_ss
- strat_diff_n6
- strat_diff_n6_w
- strat_diff_n7
- strat_diff_n7_w
- strat_diff_ss
unit: 无量纲战略差异度得分; TF-IDF 轨 (char/word) 距离 ∈ [0,1], Embedding 契约别名轨 (Qwen/large) 质心距离 ∈ [0,2]
formula: "strat_diff_n{N}(_w)(_track) = (1/N) Σ_{j∈KNN(i,N)} δ_ij, δ_ij = 1 − cos(v_i, v_j); v = 年内银行文本聚合 TF-IDF 向量 (char_wb / jieba+1506金科词); strat_diff(_lg)_{full,ctx,ss} = centroid_diff_emb(_lg) 逐值别名 = 1 − cos(v_i, 年度行业质心)"
producer: news_process/pipeline/features/strategic_diff.py::compute_strategic_differentiation ; news_process/pipeline/panel/stata_export.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_sbert.parquet (co-primary Qwen 与 _lg 嵌入向量)
- 40_panel_yearly.parquet (bank-year 聚合宿主)
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
- doi: 10.3386/w33168
  type: wp
  authors: Cong, L. W., Liang, T., Zhang, X., & Zhu, W.
  year: 2024
  title: "Textual factors: A scalable, interpretable, and data-driven approach to analyzing unstructured information"
  venue: NBER Working Paper No. 33168
- doi: 10.3386/w32934
  type: wp
  authors: Ganguli, I., Lin, J., Meursault, V., & Reynolds, N.
  year: 2024
  title: "Patent text and long-run innovation dynamics: The critical role of model selection"
  venue: NBER Working Paper No. 32934
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
  vol: 67
  issue: 7
  pages_or_artno: 4004-4031
- doi: 10.1093/rfs/hhz023
  type: journal
  authors: Hanley, K. W., & Hoberg, G.
  year: 2019
  title: "Dynamic interpretation of emerging risks in the financial sector"
  venue: The Review of Financial Studies
  vol: 32
  issue: 12
  pages_or_artno: 4543-4603
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
  vol: 69
  issue: 1
  pages_or_artno: 293-324
new_dois: []
---


## CORE

【构念与来源】
本家族测度银行在给定年度的“战略差异度”(strategic differentiation), 即某家银行的金融科技相关新闻文本组合, 相对同年其余所有银行的文本组合在语义空间中的独特程度。构念的直觉是: 若一家银行被媒体叙述的金科战略与同业高度雷同, 则其在文本网络中拥有大量近邻, 差异度低; 若其叙事组合罕见、少有同业与之靠近, 则差异度高。该测度的方法学血脉直接承自 Guzman 与 Li (2023) 提出的创业战略最近邻距离法, 以及 Hoberg 与 Phillips (2016) 的文本相似度产业网络 (TNIC) 范式: 前者给出以到 N 个最近邻的平均文本距离刻画个体战略独特性的算子, 后者给出逐年重建文本相似度网络、以内生产品差异化定位企业的框架。观测单元为银行-年 (bank-year), 落于最终面板 40_panel_yearly.parquet。数值越大代表该银行当年的金科叙事在同业中越独特, 越小代表越趋同。构念上它属于定位类变量 (positioning), 刻画银行在被媒体建构的金科战略空间中的相对生态位, 而非情感、强度或网络溢出。之所以以新闻文本而非财报或专利文本承载该构念, 是因为本项目的语料是长时段、宽覆盖的中文银行金科报道, 媒体叙事在中国情境下既反映银行对外披露的战略姿态, 也反映市场与监管对其金科定位的集体建构, 恰是刻画银行在金科空间中如何被区分的自然载体。

【方法学与计算】
计算在 pipeline/features/strategic_diff.py::compute_strategic_differentiation 中逐年展开。对每一年度, 先把该年内每家银行的相关报道文本按银行聚合为一份超级文档, 再用多种方法把文档映射为向量并两两求余弦相似度, 构成年度相似度矩阵。对目标银行 i, 取相似度最高的 N 个同业作为其最近邻集合 KNN(i,N), 令距离 delta_ij = 1 - cos(v_i, v_j), 则战略差异度 S_i = (1/N) 求和_{j in KNN(i,N)} delta_ij, 即与最像的 N 家同行的平均文本距离。本家族含三条并排的向量化方法轨与两类算子。其一为 char 级 TF-IDF (char_wb 字符 n-gram, 不依赖分词, 列名裸 strat_diff_n{N}); 其二为 word 级 TF-IDF (以注入 1506 个金融科技领域复合词的独立 jieba 分词器切分, 领域整词如金融科技、区块链整体保留, 列带 _w 后缀); 二者的非负 TF-IDF 向量余弦落在 [0,1], 故距离列值域为 [0,1]。TF-IDF 权重采用 sublinear tf 与标准逆文档频率, 依据 Manning、Raghavan 与 Schuetze (2008) 及 Salton 与 Buckley (1988) 的经典词权范式。此外家族含 Embedding 契约别名轨 strat_diff_{full,ctx,ss} 与其跨厂商孪生 strat_diff_lg_{full,ctx,ss}: 二者并非 N 最近邻算子, 而是到年度行业质心的距离 (centroid_diff_emb 与 centroid_diff_emb_lg 的逐值别名), 底层为稠密语义嵌入, 余弦真值域 [-1,1], 故质心距离值域为 [0,2] (此前对嵌入轨统一 clip 到 [0,1] 属值域删失, 已修正)。N 邻域取值构成梯子 {3,4,5,6,7} 并 {10,20,30,40,50}, 其中 TF-IDF char/word 的 full 轨覆盖全部十档, 而 ctx/ss 轨与 LDA/嵌入方法覆盖 {5} 并 {10,20,30,40,50}。文本轨的口径遵循全项目三轨架构: full = 标题 prepend 后的全文正文; ctx = 标题加实体上下文窗; ss = 标题加银行与金科同句共现窗。稠密嵌入的编码统一由 stage 25 article_sbert 供给, 主轨为 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动), co-primary 孪生为 text-embedding-3-large (3072 维), 二者在线缺失受 NEWS_PROCESS_LLM_OFFLINE 离线闸约束、miss 即 raise 零网络。

【文献定位】
本家族坐落于文本即数据的计量方法学传统 (Gentzkow, Kelly 与 Taddy, 2019) 与以文本刻画企业战略与创新的实证脉络交汇处。就构念本体而言, 它对接最优独特性 (optimal distinctiveness) 与战略生态位定位文献: Haans (2019) 论证独特性对绩效的价值随品类同质度而变, Su, Gao 与 Tan (2024) 刻画企业在竞争与制度压力下如何定位最优独特性, 二者直接锚定本家族到同业的战略距离这一生态位构念。就近期同范式应用而言, Arts, Cassiman 与 Hou (2025) 以 TNIC 式技术差异度研究并购市场, Miller 与 Wang (2024) 以文本测度数字化如何改变企业差异化战略, 后者与本家族以金科新闻文本测银行战略差异高度同构。就文本创新与语义向量方法而言, Bellstam, Bhagat 与 Cookson (2021) 的文本创新度量、Hoberg, Phillips 与 Prabhala (2014) 的竞争流动性 (fluidity)、Hanley 与 Hoberg (2019) 的新兴风险动态解读, 共同支撑本家族以逐年文本网络刻画企业相对定位的合法性。就嵌入模型选择的稳健性关切而言, Ganguli 等 (2024) 关于专利文本长期创新动态中模型选择关键作用的告讫、Cong 等 (2024) 的可扩展可解释文本因子方法, 为本家族保留 char/word/LDA/Qwen/large 多方法与 co-primary 双嵌入的设计提供了方法论依据。上述文献并非松散罗列: 战略定位文献界定构念、文本方法文献界定测量、嵌入模型文献界定稳健性设计, 三者恰好对应本家族是什么、怎么测、如何证稳健三层逻辑。

【识别策略定位】
本家族的 core 列 strat_diff_n5 是 strategic_diff 论文的正文级主处理变量 (treatment.primary): 论文以 N=5 (Guzman 与 Li 2023 推荐的基准邻域) 的 char 级 full 轨战略差异度为主回归处理变量, 检验银行金科战略独特性对其市场估值/绩效结果 (如 tobin_q 等外部财务哨兵列, 财务面板接入时构造) 的因果影响。识别层面, 该处理变量接入项目统一的 IV 扩展三引擎 (同组留一均值 leave_one_out_peer / 广义 Bartik / 媒体来源 house-style 暴露), 各自形成 just-identified 的一阶段; 其中留一同组均值利用同组其余银行的战略差异度均值作为外生变动源, Bartik 借助份额-移动分解, 媒体 house-style 暴露以来源特有的叙事风格构造工具。铁律: 家族内所有稳健性轴 (N 邻域梯子、char/word 分词、full/ctx/ss 三轨、Qwen 与 large 双嵌入契约别名) 均须各自 just-identified 并排使用, 互为稳健性、不分主次, 严禁把不同 N、不同轨、不同嵌入的差异度列混进同一个 over-identified 的 Hansen J 过度识别检验——这与三轨、co-primary 双嵌入、政治词权重梯子的铁律完全一致。留篇口径遵循 full-only 门控 (2026-06-29): 是否判为一篇银行金科报道只看 full 轨的 llm_verified_full, ctx/ss 是 conditional-on-full 的子集测度, 行宇宙为 full 留篇集的子集。

【与相邻测度的构念区分】
须将本家族与 strategic_diff 模块内的相邻测度严格区分, 避免构念混淆。其一, strat_sim_max 系列是与最像的那一家同行的相似度 (单一最近邻的相似度水平), 而本家族是到 N 个最近邻的平均距离, 前者是相似度、后者是差异度, 方向相反且聚合口径不同。其二, Embedding 契约别名 strat_diff_{full,ctx,ss} 度量的是到年度全行业质心的距离 (全行业向量法, 参照谢佳松等 2025 经济研究图 1 的行业质心距离迁移), 刻画的是相对整个行业中心的偏离, 而 char/word 的 strat_diff_n{N} 是到局部 N 近邻的距离, 刻画的是相对最相似少数同业的偏离——质心距离与局部近邻距离在同质年份可能同向、在多极分化年份可能背离, 二者是不同的独特性构念。其三, strat_fluidity (Hoberg 等 2014 竞争流动性) 度量的是相邻期竞争环境的时间变化, 属动态变化量而非本家族的截面定位量。其四, LDA+JSD 轨 (strat_diff_n5_lda 等, 不在本家族) 以主题分布的 Jensen-Shannon 散度度量差异, 与 TF-IDF 词频空间、嵌入语义空间是三条不同的度量几何。厄清这些边界的意义在于: 本家族回答的是某银行的金科叙事相对最相似少数同业有多不同, 而非相对全行业中心多偏离、与最像一家多接近、相邻年变化多大、主题分布差多远——混用会导致构念漂移与解释失焦。

【已知局限与稳健性梯子】
本家族的核心局限与稳健性设计如下。局限一, N 邻域的选择本身带主观性, 故家族显式物化 {3,4,5,6,7,10,20,30,40,50} 十档梯子: 小 N (3/4) 对最近少数同行极敏感、方差高、易受个别异常同业驱动, 大 N (30/40/50) 趋近全行业平均、更平滑但区分度钝化, N=5 为论文基准, 其余各档为换个邻域数看结论是否稳定的稳健臂。局限二, 分词方式影响词级向量, 故 char (免分词) 与 word (jieba+金科整词) 并排互证。局限三, 文本轨口径影响信号, 故 full/ctx/ss 三轨并排。局限四, 单一嵌入模型可能引入厂商特有偏差 (呼应 Ganguli 等 2024 的模型选择告讫), 故 Qwen (主) 与 text-embedding-3-large (_lg) 构成 co-primary 双轨、both-or-neither parity (任一嵌入失败则两族同列一并置 NaN, 无单边孤儿)。以上所有轴一律各自 just-identified 并排, 禁混同一 over-identified Hansen J。ss 轨回退语义镜像 ctx——当某银行年内无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 full 共享 n_articles 分母。开发期 T=2 语料上, 年内文档高度同质会使差异度近零方差、大 N 因年内同业不足而退化、ctx/ss 在极短面板可能退化, 均属预期现象, 生产期 T=18 恢复正常。本家族列不涉及 BLAS 浮点非确定网络列, golden 复现无需按名 drop, 属逐值可复现的确定性测度族。


## VAR: strat_diff_ctx

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列与其跨厂商孪生 strat_diff_lg_ctx (text-embedding-3-large) 构成 co-primary 双轨: 二者同为主测度、互为稳健性, 唯一差分在嵌入厂商与维度。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_full

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 full (标题 prepend + 全文正文), 遵循 full-only 留篇门控。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列与其跨厂商孪生 strat_diff_lg_full (text-embedding-3-large) 构成 co-primary 双轨: 二者同为主测度、互为稳健性, 唯一差分在嵌入厂商与维度。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_lg_ctx

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb_lg 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 text-embedding-3-large (3072 维, OpenAI/yunwu 端点) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列是 strat_diff_ctx 的跨厂商 co-primary 孪生: 唯一差分在嵌入模型——由主轨 Qwen 换为 text-embedding-3-large; 保留 _lg 孪生的用意是隔离单一嵌入厂商特有偏差 (呼应 Ganguli 等 2024 关于模型选择关键作用的告讫), 使质心距离的语义结论对嵌入模型选择稳健。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_lg_full

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb_lg 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 text-embedding-3-large (3072 维, OpenAI/yunwu 端点) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 full (标题 prepend + 全文正文), 遵循 full-only 留篇门控。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列是 strat_diff_full 的跨厂商 co-primary 孪生: 唯一差分在嵌入模型——由主轨 Qwen 换为 text-embedding-3-large; 保留 _lg 孪生的用意是隔离单一嵌入厂商特有偏差 (呼应 Ganguli 等 2024 关于模型选择关键作用的告讫), 使质心距离的语义结论对嵌入模型选择稳健。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_lg_ss

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb_lg 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 text-embedding-3-large (3072 维, OpenAI/yunwu 端点) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列是 strat_diff_ss 的跨厂商 co-primary 孪生: 唯一差分在嵌入模型——由主轨 Qwen 换为 text-embedding-3-large; 保留 _lg 孪生的用意是隔离单一嵌入厂商特有偏差 (呼应 Ganguli 等 2024 关于模型选择关键作用的告讫), 使质心距离的语义结论对嵌入模型选择稳健。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n10_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=10, 是 top-k 大邻域扩展 (_TOPK_NN={10,20,30,40,50}, 2026-07-02 引入) 的最小档: 取最相似的 10 家同业求平均距离, 相较基准 N=5 把邻域翻倍, 显著平滑局部噪声、更趋近中等规模同业群的平均定位, 区分度较小 N 钝化但更稳。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n20_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=20, 是 top-k 大邻域扩展的第二档: 取最相似的 20 家同业求平均距离, 相较 N=5/10 进一步扩大邻域、更强平滑局部结构, 定位趋向较大同业子群的中心, 区分度更钝但对个别异常同业更免疫。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n3

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=3 而非 N=5, 即只取与目标银行最相似的 3 家同业求平均距离, 是家族中最局部、最贴近少数最近邻的邻域档位。相较基准 N=5, 它对个别极相似或极异常同业更敏感, 截面方差更高, 在同质年份更易出现近零值; 其价值在于检验把邻域收得最紧、只看最像的极少数同行时, 战略差异度的主结论是否依然成立。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n30_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=30, 是 top-k 大邻域扩展的中间档: 取最相似的 30 家同业求平均距离, 邻域已相当宽, 定位强烈趋向到全行业中心的偏离度, 区分度进一步钝化但对局部噪声与异常同业高度免疫, 适合检验以广域同业为参照时结论是否成立。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n3_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=3 而非 N=5, 即只取与目标银行最相似的 3 家同业求平均距离, 是家族中最局部、最贴近少数最近邻的邻域档位。相较基准 N=5, 它对个别极相似或极异常同业更敏感, 截面方差更高, 在同质年份更易出现近零值; 其价值在于检验把邻域收得最紧、只看最像的极少数同行时, 战略差异度的主结论是否依然成立。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n4

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=4, 取与目标银行最相似的 4 家同业求平均距离, 是介于极局部 N=3 与基准 N=5 之间的过渡档, 用以检验邻域从 3 递增到 5 过程中战略差异度的连续性与稳健性; 相比 N=3 它略降对单个异常同业的敏感度, 相比 N=5 又更贴近局部。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n40_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=40, 是 top-k 大邻域扩展的次大档: 取最相似的 40 家同业求平均距离, 邻域接近本样本可用同业规模上界, 定位几乎等同于到广域行业中心的偏离, 区分度高度钝化但极其稳健于局部扰动, 用以检验邻域推到近全样本时结论的极限稳定性。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n4_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=4, 取与目标银行最相似的 4 家同业求平均距离, 是介于极局部 N=3 与基准 N=5 之间的过渡档, 用以检验邻域从 3 递增到 5 过程中战略差异度的连续性与稳健性; 相比 N=3 它略降对单个异常同业的敏感度, 相比 N=5 又更贴近局部。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n50_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=50, 是 top-k 大邻域扩展的最大档、邻域梯子的极端上界: 取最相似的 50 家同业求平均距离, 邻域达本样本银行规模量级, 战略差异度几乎退化为到全部同业平均的距离, 区分度最钝但对任何局部结构最免疫, 用以界定 N 从 5 推到 50 全程结论的稳定性边界。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5_w_ctx

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ctx: 超级文档由 content_ctx (标题 prepend + 银行/金科实体上下文窗) 原样拼接, 相较 full 聚焦实体邻近语境、剔除报道中与银行金科无关的段落, 使战略差异度信号更贴近金科叙事本体。在 full-only 门控下 ctx 为 conditional-on-full 子集测度, 行宇宙为 full 留篇集的子集。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n5_w_ss

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用基准 N=5, 取最相似的 5 家同业求平均距离, 系 Guzman 与 Li (2023) 推荐的基准邻域: 既能规避 N=3/4 对单个异常同业过度敏感的高方差, 又不至于像大 N 那样把信号平滑成全行业平均而丧失局部区分度。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨差异度混入同一 over-identified Hansen J。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n6

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=6, 取最相似的 6 家同业求平均距离, 是基准 N=5 向上相邻的档位, 用以检验邻域略微放宽一家时结论的稳定性; 它把邻域稍稍扩大、对局部噪声更平滑, 但仍属局部近邻范畴, 尚未趋向大 N 的全行业平均。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n6_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=6, 取最相似的 6 家同业求平均距离, 是基准 N=5 向上相邻的档位, 用以检验邻域略微放宽一家时结论的稳定性; 它把邻域稍稍扩大、对局部噪声更平滑, 但仍属局部近邻范畴, 尚未趋向大 N 的全行业平均。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n7

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=7, 取最相似的 7 家同业求平均距离, 是 char/word full 轨小 N 段 {3,4,5,6,7} 的上界档, 用以检验邻域从基准继续放宽两家时结论是否稳定, 是小 N 段向大 N 段过渡的临界档位。 本列采用 char 级 TF-IDF (字符 n-gram, 免分词), 与同 N 档的 word 版 (_w) 互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_n7_w

【变体差分】
本列相对 canonical strat_diff_n5 的差分维度如下: 采用 N=7, 取最相似的 7 家同业求平均距离, 是 char/word full 轨小 N 段 {3,4,5,6,7} 的上界档, 用以检验邻域从基准继续放宽两家时结论是否稳定, 是小 N 段向大 N 段过渡的临界档位。 在同 N 档 char 版的基础上仅差分分词方式: 向量化由字符 n-gram 改为 word 级 TF-IDF (列名 _w 后缀), 使用注入 1506 个金融科技领域复合词的独立 jieba 分词器 (见 _get_diff_tokenizer), 使金融科技、区块链、数字人民币等领域整词整体保留而非被切碎, 词级向量因此更具领域语义精度, 与 char 轨的字符 n-gram 几何形成互证。 文本轨为 full (标题 prepend 后的全文正文), 遵循 full-only 留篇门控 (2026-06-29): 是否算作一篇银行金科报道只由 llm_verified_full 判定。 本列以字符 n-gram (char_wb, 免分词) 把该银行当年文本聚合为 TF-IDF 向量, 距离 delta=1-cos 值域 [0,1], 越大越独特。它与家族内其余各 N 档、word 分词轨 (_w)、ctx/ss 文本轨、以及 Qwen/large 嵌入契约别名列, 构成互为稳健性、不分主次的并排稳健性梯子: 它们各自 just-identified、各自单独进入自回归的一阶段, 严禁把不同 N、不同分词、不同文本轨、不同嵌入模型的差异度列混入同一个 over-identified 的 Hansen J 过度识别检验。 char 与 word 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把二者混入同一 over-identified Hansen J。若领域感知词级切分与字符 n-gram 给出方向一致的战略差异度, 则主结论对文本切分方式稳健。 开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

## VAR: strat_diff_ss

【变体差分】
本列与 char/word 的 N 最近邻列在算子上根本不同: 它并非到 N 个最近邻的平均距离, 而是到年度行业质心的距离 (centroid_diff_emb 的逐值契约别名), 底层为稠密语义嵌入而非 TF-IDF 词频向量。具体地, 用嵌入模型 Qwen/Qwen3-Embedding-8B (4096 维, 硅基流动) 把每家银行当年文本编码为稠密向量, 求该年全体银行向量的质心, 令距离 delta=1-cos(v_i, 质心); 因嵌入余弦真值域为 [-1,1], 质心距离值域为 [0,2] (不同于 TF-IDF 轨的 [0,1])。文本轨为 ss: 超级文档由 content_ss (标题 prepend + 银行与金科同句共现窗, ±句半径由 config filtering ss_sentence_radius 控制, 默认 1) 原样拼接, 是三轨中语境最紧的一轨, 只保留银行与金科在同一句附近共现的文本, 使战略差异度最贴近银行谈金科的直接语义。回退语义镜像 ctx: 当某银行年内无银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 并与 full 共享 n_articles 分母。full-only 门控下 ss 为 conditional-on-full 子集测度。此列存在的意义是把局部近邻独特性 (N-NN) 之外的相对全行业中心偏离度作为并排的稠密语义稳健性轨, 呼应谢佳松等 (2025) 的全行业向量法。本列与其跨厂商孪生 strat_diff_lg_ss (text-embedding-3-large) 构成 co-primary 双轨: 二者同为主测度、互为稳健性, 唯一差分在嵌入厂商与维度。Qwen 主轨与 _lg 孪生为 co-primary 双轨、严格 both-or-neither parity——列名双射, 任一嵌入 None 则同族两列一并置 NaN, 绝无单边孤儿。铁律: Qwen 主轨与 _lg 轨、full/ctx/ss 三轨、以及 TF-IDF N-NN 各列一律各自 just-identified 并排、互为稳健性、不分主次, 严禁把两条 co-primary 嵌入或三轨混进同一个 over-identified 的 Hansen J。开发期 T=2 短面板上, 年内文档同质或年内同业不足会使本列近零方差或退化, 属预期现象, 生产期 T=18 恢复正常。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
