---
family_id: F293
columns:
- fin_sent_zh_net_tone_ctx
- fin_sent_zh_net_tone_full
- fin_sent_zh_net_tone_ss
- finbert2_net_tone_ctx
- finbert2_net_tone_full
- finbert2_net_tone_ss
- finbert_cn_net_tone_ctx
- finbert_cn_net_tone_full
- finbert_cn_net_tone_ss
unit: 符号化净语调 (连续, [-1,1]; bank-year 篇均正面概率减篇均负面概率)
formula: "{model}_net_tone{track} = mean_articles(P_pos^{model,track}) - mean_articles(P_neg^{model,track}); 文章级 P 来自 stage 23 BERT 滑动窗口置信度加权推理, bank-year 聚合后 post-agg 作差 (encode.py Phase 2, 2026-07-02); model ∈ {finbert_cn, fin_sent_zh, finbert2}, track ∈ {full, ctx, ss}"
producer: pipeline/sentiment/tone_berts.py (stage 23 文章级概率推理) ; pipeline/panel/encode.py (bank-year 聚合 + net_tone post-agg 作差) ; pipeline/panel/codebook.py::_bert_model_match (per-model 列族识别)
upstream:
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss 三轨文本 + *_is_fallback)
- 22_words_tone.parquet (stage 23 直接输入载体)
- 23_bert_tone.parquet (文章级 {model}_正面/负面/中性 概率列 + infer_failed 哨兵)
citations:
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: "5117-5128"
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
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: "Article 20"
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: "Article 101126"
- doi: 10.48550/arXiv.2507.01991
  type: arxiv
  authors: Zafar, M. B.
  year: 2025
  title: "FinAI-BERT: A transformer-based model for sentence-level detection of AI disclosures in financial reports"
  venue: arXiv
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: "e1549"
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: "105227"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1111/1475-679X.12560
  type: journal
  authors: Xu, G.
  year: 2024
  title: "News bias in financial journalists' social networks"
  venue: Journal of Accounting Research
  vol: 62
  issue: 4
  pages_or_artno: "1145-1182"
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: "102776"
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: "673-719"
- doi: 10.1007/978-3-030-32381-3_16
  type: book
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science
  vol: 11856
  pages_or_artno: "194-206"
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of EMNLP-IJCNLP 2019
  pages_or_artno: "3980-3990"
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: "43-96"
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: "1237-1282"
new_dois: []
---

## CORE

【构念与来源】
本家族测度的构念是银行在媒体新闻叙事中的符号化净语调 (signed net tone), 由领域微调的中文金融 BERT 神经网络模型直接从整段文本的语言理解中提取, 而非依赖关键词计数。每列的取值定义为: 在给定银行-年份格内, 该模型对留篇集内每篇新闻输出的正面概率的篇均值, 减去负面概率的篇均值, 落在负一到正一的闭区间内; 正值表示该银行当年新闻叙事整体偏正面, 负值表示整体偏负面, 绝对值大小刻画倾向强度。家族共九列, 由三个相互独立的中文金融 BERT 模型 (finbert_cn、fin_sent_zh、finbert2) 与三条文本轨道 (full 全文、ctx 实体上下文窗、ss 银行与金融科技词同句窗) 的笛卡尔积构成。构念层面, 本家族是项目情感测度三大方法路线 (大模型投票、词典规则、BERT 神经网络) 中的第三条: 词典法把语调还原为词表命中的加权计数, 大模型法依赖生成式模型的少样本判断, 而 BERT 路线用在海量金融语料上预训练并经情感标注微调的双向编码器, 对句子和篇章的整体语气做判别式分类, 天然处理否定、转折、程度修饰等词典法必须靠人工规则逼近的语言现象 (Punetha 和 Jain (2025) 系统论证了否定处理对情感测度效度的一阶影响)。三条路线在测量层面互为三角验证: Todd、Bowden 和 Moshfeghi (2024) 的综述指出, 金融文本情感研究的可信度前沿正在从单一方法转向多方法交叉印证, 本家族正是该设计中 BERT 一翼的 per-model 展开。数据来源链条为: 原始中文银行与金融科技新闻语料经预处理、银行实体识别、金融科技词识别与共现硬过滤后, 在 stage 14 物化三轨文本列, stage 23 (tone_berts) 对每篇文章跑三个 BERT 模型乘三条轨道的批量推理, 产出文章级各标签概率; 面板层在 encode 聚合后以 post-agg 作差得到本家族九列。

【方法学与计算】
计算分文章级与面板级两层。文章级 (stage 23, pipeline/sentiment/tone_berts.py): 首先从 config/sentiment.yaml 读入三个模型配置并一次性预加载到 GPU, 以 FP32 权重加 AMP 自动混合精度做推理; 对每条轨道, 用 prepend_title 约定把标题拼在轨道正文之前形成推理文本 (full 等于标题加全文正文, ctx 等于标题加实体上下文窗, ss 等于标题加银行与金融科技词同句窗)。超过单窗长度上限 (512 个 token 含特殊符, 有效正文约 510 token) 的长文按 50% 重叠率滑动开窗, 各窗独立前向后按置信度加权池化聚合 logits, 即高置信窗口获得更大权重, 避免长文中一段平淡文字稀释关键段落的信号; 聚合后 softmax 得到各标签概率, argmax 得到离散标签。工程细节上, 各模型按自身 tokenizer 独立分窗 (词表指纹不一致的模型不共享分词, 防止 token id 跨词表错配), 批级推理异常先逐篇重试一次, 仍失败才写失败哨兵 (标签置空、概率置 NaN、窗口数记负一), 与空文本 (窗口数为零) 严格区分; 每模型每轨道另落 infer_failed 指示列, 供下游审计。面板级 (pipeline/panel/encode.py): 先把文章级各标签概率在银行-年份格内取均值得到 {model}_pos{track} 与 {model}_neg{track} 等概率均值列, 再于 2026-07-02 的 Phase 2 改造中以 post-agg 作差直接生成本家族: {model}_net_tone{track} 等于面板正面概率均值列减负面概率均值列。这一作差在数学上恰等于篇级符号化净语调的均值, 因为 BERT 推理失败是逐篇原子性的 (同一篇的正负概率同置 NaN), 正负两列的篇级缺失掩码完全一致, 均值之差与差之均值恒等; 该恒等式同时是相邻分布形状族偏度掩码的可断言不变量, 即使个别格因样本不足被掩去偏度, 本家族的均值列在同格仍保持恒等可验。聚合层的另一个口径细节是分母语义: 每格分母为该模型该轨道概率非缺失的篇数, 推理失败篇与空文本篇自动出分母, 因此三模型在同一格的有效篇数允许不同, 这是 per-model 独立降级在格内的自然延伸。刻意的设计取舍有三: 其一, 只产均值不产标准差孪生, 因为差的标准差不等于标准差之差, 硬造会产生语义混淆; 其二, 不产 _sum 与市值、媒体、羊群加权 (_vw/_mw/_hw) 孪生, 控制列爆炸; 其三, 本家族是纯 $0 后处理, 不重跑任何付费或耗时阶段。留篇口径遵循 2026-06-29 的 full-only 门控铁律: 一篇文章是否计入"银行金融科技报道"只看 llm_verified_full 是否为真, ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 各轨概率列在该宇宙内按轨道自身非缺失篇数取均值。ss 轨回退语义与全仓一致: 当一篇文章不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 与 full 共享 n_articles 分母; 金融科技词自动机不可用时优雅降级为全篇回退。确定性来源是冻结的模型权重加 argmax 判别 (AMP 混合精度对分类结果无影响, 概率数值在容差内稳定); 本地重跑须设 HF_HUB_OFFLINE 与 TRANSFORMERS_OFFLINE 环境变量走本地缓存。

【文献定位】
本家族在三支文献的交汇处。第一支是领域自适应 Transformer 情感测度方法学。Sun、Qiu、Xu 和 Huang (2019) 系统给出了 BERT 在文本分类任务上的微调配方, 是所有下游金融情感 BERT 的方法基座; Reimers 和 Gurevych (2019) 展示了 BERT 系编码器在句子级语义表示上的能力边界, 说明为何篇章级情感需要滑窗加池化而非简单截断。金融领域化方面, Xu 等 (2025) 提出的 FinBERT2 证明了在金融语料上继续预训练的专用双向编码器在情感分类等判别任务上仍系统性优于通用大模型, 为本家族保留 BERT 路线 (而非全面转向生成式大模型) 提供了直接依据; Bingler、Kraus、Leippold 和 Webersinke (2022) 用 ClimateBert 示范了领域 BERT 如何把"廉价谈话"从实质披露中分离, 是领域微调判别器测度构念效度的经典应用; Zafar (2025) 的 FinAI-BERT 进一步说明句子级 Transformer 判别器在金融披露检测任务上的持续生命力。第二支是中文金融文本情感资源与测度。Du、Huang、Wermers 和 Wu (2022) 论证了情感词典的语言与领域双重特异性, 直接刻画了中文金融语境下通用工具失效的机理, 也是本项目词典轨的锚文献; Ma、Zhang 和 Zhang (2025) 构建了面向中国投资者的细粒度中文金融情感词典, 与 BERT 轨形成方法互补; Lan 等 (2025) 给出了中文金融细粒度情感的大模型方案, 恰当界定了 BERT 判别器与生成式大模型在中文金融情感任务上的相对位置; Kirtac 和 Germano (2024) 则量化了情感信号在交易策略中的经济价值, 支撑媒体语调作为处理变量的经济显著性。第三支是媒体语调与银行结果的实证金融文献。You、Zhang 和 Zhang (2018) 确立了中国媒体报道倾向的政治经济学基准, 说明中国场景下媒体语调既有信息含量也有俘获噪声, 多模型测度可以稀释单一测度被系统性写作风格污染的风险; Fang、Wang、Wang 和 Yuan (2024) 直接以中国银行业为对象, 证明媒体情感影响存款稳定性与系统性风险, 是本家族处理变量到银行结果变量因果链的最近邻证据; Cookson、Fox、Gil-Bazo、Imbet 和 Schiller (2026) 展示了负面叙事在社交媒体时代如何催化银行挤兑, Garcia (2025) 发现情感分歧本身预测财务困境, 两者共同说明净语调的水平与跨来源分歧都承载独立信息; Xu (2024) 揭示了金融记者社交网络导致的报道偏差, 为"测量层多模型、来源层控媒体"的双保险设计提供动机。推断方法上, Romano 和 Wolf (2005) 的逐步多重检验程序是本家族跨模型族错误率控制 (根级模板 27_tableA12) 的方法学依据。

【识别策略定位】
在识别设计中, 本家族的九列全部是"互为稳健性、不分主次"的 co-equal 测量臂, 而非主测度加陪衬的主从结构。BERT 路线刻意不设 ensemble headline: 与 LLM 三家有投票共识列 llm_vote_tone 作 canonical 不同, 三个 BERT 模型的 net_tone 平行并列, 各自单独进入自己的回归规格, 用以证明任何以媒体语调为处理变量的主结论不被任一单个模型的架构、预训练语料或标注体系驱动。铁律有三条, 全部源自 CLAUDE.md 当前状态铁律并在此复述: 第一, 三个模型各自 just-identified 并排, 禁止把不同模型的同构念测度混进同一个 over-identified 的 Hansen J 检验 — 它们是同一构念的替代测量而非相互独立的工具变量, 混用会让过度识别检验在概念上失效; 第二, 三条文本轨道 (full/ctx/ss) 同样各自 just-identified 并排、互为稳健性不分主次, 禁混同一 Hansen J, 该铁律与 co-primary 双轨嵌入、政治词权重梯度、词典消融梯度共用同一句式; 第三, 真正的族错误率控制不靠声明式文档而靠根级 Romano-Wolf 模板 27_tableA12_cross_model_fwer, 把跨模型的同一假设族纳入逐步降压程序 (Romano 和 Wolf (2005)), paper_spec 里的 cross_bert_model 字段仅是声明式记录, 运行时无消费者。跨模型系数比较另有一条量纲铁律: finbert2 是二分类模型而另两个是三分类, 三者 net_tone 的原始方差与刻度天然不同, Table A5 类的跨模型系数并排必须先做 z-score 标准化再比较 β, 直接比较原始系数属于口径错误。模型间一致性的量化不进回归, 走 tone_validation 的 Krippendorff α (名义测度、缺标感知, 容忍二分类对三分类) 与 Cohen κ (须先把负一缺标哨兵重映射为非负码, 防止与负面标签码冲突) 两条独立通道。降级语义是 per-model 独立降级: finbert2 为本地私有模型, FINBERT2_MODEL_DIR 未配置时优雅跳过, 只掉 finbert2 自身列族, 另两个模型的六列照常产出 — 这与 co-primary 嵌入双轨的 both-or-neither 语义是刻意区分的两种口径, 不可混淆。在回归规格的具体摆放上还有一条容易被忽视的操作性推论: 稳健性并排的正确形态是"同一规格换测度重跑、逐列出表", 而不是把多个模型的净语调同时放进同一方程右端作为多个回归元 — 后者因三列高度相关会引入严重共线, 且系数失去"该测度下总效应"的解释, 属口径错误; 也不允许把某一模型的净语调充当另一模型净语调的工具变量, 因为同构念替代测量的测量误差高度相关, 排除性约束天然不成立。处理变量与结果变量在项目中是两套独立空间: 本家族只候选处理变量一侧, 各论文的结果变量 (融资成本、金融科技投资、成本收入比变动等) 另行定义, 不因换用本家族哪一列而改变。

【与相邻测度的构念区分】
本家族须与至少五组相邻列族在构念上划清边界。其一, 与同为 stage 23 产物的原始概率均值列 ({model}_pos/neg/neu{track}) 的区别: 概率列是单侧强度, net_tone 是双侧净差, 只有后者与 LLM 轨的 tone (取值负一、零、一的篇均) 同刻度可比, 这正是 Phase 2 增设本家族的动机 — 让三方法在同一 [-1,1] 尺度上并排。其二, 与 LLM 逐模型语调 ({gpt54nano,gemini31,deepseekv4}_tone{track}) 的区别: 两者构念同为净语调, 但测量机理分属判别式微调编码器与生成式指令模型, 属跨方法三角验证的不同顶点, 各自的 per-model 梯子内部并排、梯子之间正交不交叉。其三, 与词典族 (du_2022_tone、loughran 系及其消融与政治词权重变体) 的区别: 词典分数是词频加权的构造性测度, 可完全审计但对语序与否定敏感度有限 (Du 等 (2022); Ma 等 (2025)), BERT 净语调是黑箱程度更高但语言理解更强的判别测度, 两族互为方法论稳健性。其四, 与 BERT 分布形状五族 (熵、极端负面占比、净语调偏度、跨模型标签异质性、年内波动与趋势) 的区别: 五族全部以本家族的篇级净语调或概率分布为基材做二阶统计, 刻画的是不确定性、尾部与时间形状, 而本家族只刻画一阶水平; 尤其注意偏度列的最小样本掩码与熵列的模型内可比性告诫属于五族的口径, 不应回写到本家族。其五, 后缀语义辨析: 本家族的 _full/_ctx/_ss 是三轨文本后缀, 与网络判据后缀 (_win1/_sent)、加权后缀 (_vw/_mw/_hw) 是互不相干的命名空间; 面板列族识别由 codebook 的锚定正则 (以模型短名开头、metric 含 net_tone) 完成, 天然排除 llm_vote 系列。另须记录一条负面清单: 本家族是非嵌入测度, 属 carve-out, 不存在也不应补 _lg (text-embedding-3-large) 孪生列 — _lg 后缀专属 co-primary 嵌入双轨。

【已知局限与稳健性梯子】
第一, 分类粒度异质: finbert_cn 与 fin_sent_zh 是三分类 (含中性), finbert2 是二分类 (仅正负), 后者的正负概率近似互补, 其 net_tone 近似等于二倍正面概率减一, 分布形状与三分类模型系统不同; 补救是跨模型只比标准化系数、一致性走缺标感知的 α 与重映射后的 κ。第二, 长文信息压缩: 滑窗加置信度加权池化虽优于截断, 但对情感在文中分布极不均匀的长稿仍是有损聚合; 三轨设计本身就是对"哪一段文本承载银行相关语调"的规格稳健性梯子, ss 轨把测量收窄到银行与金融科技词同句的最小语境, ctx 轨居中, full 轨最宽。第三, 训练语料域移: 三个模型的微调语料 (分析师报告、金融短语库、金融领域再预训练语料) 与本项目的新闻体裁存在域差, 单模型的系统性偏置无法在模型内部检验, 只能靠三模型并排与跨方法 (LLM、词典) 印证稀释 — 这正是家族存在的理由。第四, 失败与缺失: 推理失败哨兵与空文本严格区分, 失败篇的正负概率原子性同缺, 保证 net_tone 无单侧污染; finbert2 环境性缺席走 per-model 独立降级, 不牵连兄弟模型。第五, 开发态退化: 当前盘上为 T=2 的开发面板, ctx 与 ss 轨在部分格可能样本极薄, 生产 T=18 全量语料下方差结构将实质改善, 开发态的薄格数值不应被解读为测度失效。第六, 语调与结果变量的联立性: 媒体净语调既可能反映银行基本面也可能反向影响银行行为 (存款人情绪、监管注意力), 本家族自身不解决内生性, 只解决测量误差的模型依赖问题; 因果识别须叠加项目的工具变量扩展 (同组留一均值、广义 Bartik、媒体来源风格暴露三引擎) 与固定效应设计, 测量稳健与识别稳健是两层相互独立的防线, 不可用前者替代后者。第七, 概率标定漂移: BERT 输出的 softmax 概率并非严格标定的频率意义概率, 不同模型的置信度分布形状不同, 因此篇均概率之差在模型间只有序数层面的可比性, 这从另一个角度强化了跨模型只比标准化系数的量纲铁律。整个家族的稳健性梯子小结: 模型维 (三 BERT 并排, 外加 LLM 三家与词典多族的跨方法梯子)、文本维 (三轨)、推断维 (跨模型 Romano-Wolf 族错误率控制), 三个维度正交展开、各自 just-identified、任何维度内部与之间都禁止拼进同一 over-identified Hansen J。用白话概括本家族: 让三个各自独立训练的"金融新闻情绪识别器"分别给每篇报道打一个从负一到正一的净情绪分, 再按银行按年取平均; 三个识别器出身不同门派 (一个读研报长大, 一个背标准金融短语题库长大, 一个是项目自家在金融语料上重新训练的私房模型), 谁也不是老大, 结论必须三个都点头才算数; 打分时既可以读整篇文章, 也可以只读提到这家银行的那几段, 甚至只读银行和金融科技词出现在同一句话里的那几句, 三种读法各出一列, 相互对照防止某一种读法带来的偏差被当成事实。之所以费这么大力气做九列而不是一列, 是因为顶刊审稿的核心质疑之一就是"你的结论会不会只是你选的那一个情感模型的人为产物", 本家族用制度化的多模型多轨道并排把这个质疑在数据层面提前封死。

## VAR: fin_sent_zh_net_tone_ctx

【变体差分】
本列是 fin_sent_zh 模型净语调在 ctx 轨 (实体上下文窗) 上的测量臂, 相对家族 canonical 口径 (同模型 full 轨) 的唯一差分维度是文本轨道: 推理文本为标题 prepend 加 content_ctx, 即围绕目标银行实体命中位置的上下文窗口拼接, 而非全文正文。构念含义是"银行实体邻近语境的净语调", 它剔除了同篇新闻中与目标银行无关段落 (如同稿并报的其他机构、宏观背景段) 对语调的稀释与污染, 代价是窗口截断可能丢失远距离的评价性表述。模型口径与 full 列完全一致: bardsai/finance-sentiment-zh-base, 三分类, 篇均正面概率减篇均负面概率。留篇口径遵循 full-only 门控: 本列的行宇宙是 llm_verified_full 留篇集的子集, ctx 轨是 conditional-on-full 的测度轨, 列内均值按 ctx 轨自身非缺失篇数计算。与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。典型用法是作 full 轨主规格的文本口径稳健性检验: 若 full 轨系数由无关段落噪声驱动, ctx 轨应显著衰减; 两者同向且量级相近则支持语调信号确实锚定在银行相关语境上。窗口截断对本列还有一个模型交互效应: ctx 文本通常短于单窗上限, 多数篇目为单窗推理、不经滑窗池化, 因此本列的篇级概率比 full 轨少一层加权平滑, 格级均值对个别窗口的判别噪声略敏感, 在篇数充足的生产语料下该噪声被大数定律稀释。本列无 _lg 孪生 (非嵌入 carve-out), 无加权与 _std/_sum 孪生; 跨模型比较须 z-score 标准化。

## VAR: fin_sent_zh_net_tone_full

【变体差分】
本列是 fin_sent_zh 模型净语调的 full 轨 (全文轨) 列, tier=core, 是本家族三个跨模型 co-equal 主轨列之一, 也是根级跨模型族错误率模板 27_tableA12_cross_model_fwer 的直接参与者。模型口径: bardsai/finance-sentiment-zh-base, 一个在 Hugging Face 公开发布、以 Financial PhraseBank 类金融短语情感标注体系微调的中文金融情感三分类模型 (标签为正面、负面、中性)。文本口径: full 轨等于标题 prepend 加全文正文 (content_full), 是三轨中信息最全、语境最宽的一条, 承载"整篇报道的总体净语调"构念; 2026-06-29 起项目留篇门控为 full-only, 即行宇宙由 llm_verified_full 决定, full 轨因此也是三轨中样本宇宙的定义轨。计算链路: stage 23 对每篇文章的 full 文本按该模型自身 tokenizer 分窗 (512 token 上限、50% 重叠滑窗)、置信度加权池化聚合窗口 logits、softmax 得三标签概率; encode 聚合层先算 bank-year 篇均正面概率与篇均负面概率, 再 post-agg 作差得本列, 取值范围 [-1,1]。差分定位: 相对家族内另两个 full 轨兄弟列, 本列的唯一差分维度是模型 — fin_sent_zh 的微调基材偏向标准化金融短语标注, 与 finbert_cn 的分析师报告风格语料、finbert2 的金融领域再预训练形成训练分布上的三角互补; 三者 co-equal 互为稳健性、不分主次, 无 ensemble headline, 各自 just-identified 并排, 禁混同一 over-identified Hansen J, 真 FWER 控制走 Romano-Wolf 逐步程序 (Romano 和 Wolf (2005))。跨模型系数比较须 z-score 标准化 (本列为三分类, 与二分类的 finbert2 原始方差不同刻度)。作为三分类模型, 本列的正负概率不互补 (中性吸收中间概率质量), 其 net_tone 对"明确表态"的敏感度高于二分类模型, 温和中性报道对本列的贡献接近零而非被强制二分, 这是解读跨模型量级差异时的首要机理。金融短语库式的标注体系有其独特的测量性格: 它以孤立短语的投资者视角情感为标注单元, 强调"这句话对持有人是好消息还是坏消息"的判断, 因此本列对财务数字方向性表述 (增长、下滑、超预期、不及预期) 的捕捉尤其敏锐, 而对叙事性、评论性的长段落语气相对保守, 这与 finbert_cn 的研报语体敏感性形成互补 — 两个三分类模型在同一篇新闻上的分歧本身就是有信息量的测量学信号, 由相邻分布形状族的跨模型标签异质性列专门刻画。在识别策略中的具体角色: 当以媒体净语调为处理变量的主规格采用某一测度作 headline 时, 本列与另外两个 full 轨兄弟列各自单独替换进同一规格重跑, 三份系数表并排呈现; 任何"三分之二显著、一家翻转"的格局都必须如实报告并经 Romano-Wolf 程序检验是否幸存于族错误率控制, 而不允许事后挑选表现最好的模型充当唯一证据。金融短语库标注体系与新闻体裁之间存在一层可预期的域移: 短语库以孤立句子的投资者情感为标注单元, 而新闻正文常把关键判断嵌入叙事性长句与背景铺陈之间, 因此本列在长篇通讯稿上更依赖滑窗置信度加权把关键段落的信号从平淡段落中抬升出来; 这一机理决定了本列与 ctx、ss 两条收窄轨的差分往往比 finbert_cn 更明显, 因为语境收窄恰好帮它剔除了标注分布外的叙事噪声。作为跨方法三角验证的 BERT 顶点之一, 本列与 LLM 三家的逐模型语调、词典族的分数在同一 [-1,1] 尺度上并排时, 三方法的系统性分歧本身即是构念效度的证据来源 (Todd、Bowden 和 Moshfeghi (2024)): 若三方法在同一格系统同号, 则净语调水平稳健; 若某一方法系统偏离, 则提示该方法的测量机理与银行新闻语体存在特异性摩擦, 须在稳健性叙事中定位而非掩盖。本列无 _lg 孪生 (非嵌入 carve-out), 无加权臂与 _std/_sum 孪生 (Phase 2 设计取舍), 降级语义为 per-model 独立: 本列依赖的 HF 模型在 strict_models 默认下加载失败会 fail-loud (公开模型缺席属故障须排查), 与 finbert2 的优雅跳过 (私有模型缺席属预期) 语义相反; 本地重跑须设 HF 离线环境变量走本地缓存, 否则外网拉取失败会中断整个阶段。确定性来自冻结权重加 argmax, 混合精度推理不改变分类结果, 概率数值在容差内稳定, 面板层作差为纯确定性算术。

## VAR: fin_sent_zh_net_tone_ss

【变体差分】
本列是 fin_sent_zh 模型净语调在 ss 轨 (银行与金融科技词同句窗) 上的测量臂, 相对家族 canonical 的差分维度是文本轨道: 推理文本为标题 prepend 加 content_ss, 即仅保留目标银行与金融科技词在同一句 (或配置半径内相邻句, 默认半径一句) 共现的最小语境窗口, 是三轨中语境最窄、构念指向最锐的一条, 测量"银行的金融科技叙事本身的净语调"而非整篇报道的泛化语调。ss 轨回退语义须严格按全仓口径理解: 当一篇文章不存在银行与金融科技词的同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 与 full 共享 n_articles 分母; 金融科技词自动机不可用时全篇回退、优雅降级。因此本列在回退占比高的格上向 full 轨收敛, 解读窄语境效应时应结合回退指示列。留篇口径为 conditional-on-full: 行宇宙是 full 留篇集子集。模型与计算口径同家族 (三分类, 篇均正面概率减篇均负面概率)。与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。开发态 T=2 下本轨样本最薄, 部分格数值退化属预期, 生产 T=18 下方差结构将改善。本列的独特证据价值在构念锐度: 若研究假设主张"银行的金融科技叙事语调" (而非银行整体媒体形象) 驱动结果变量, 本列是三轨中与该假设语义对齐最紧的测量; full 轨显著而本列不显著的格局提示效应可能来自银行整体声誉通道而非金融科技叙事本身, 这一区分对机制解释有直接价值。本列无 _lg 孪生, 无加权与 _std/_sum 孪生。

## VAR: finbert2_net_tone_ctx

【变体差分】
本列是 finbert2 模型净语调在 ctx 轨上的测量臂, 差分维度有二且相互独立: 模型维为 finbert2 (本地私有、金融领域再预训练的二分类模型, 仅正面与负面两标签), 文本维为 ctx 轨 (标题 prepend 加银行实体上下文窗)。二分类特性使本列的正负概率近似互补, net_tone 近似等于二倍正面概率减一, 取值倾向于远离零点 — 没有中性类吸收概率质量, 温和报道也会被推向正或负一侧, 因此本列的原始方差刻度与三分类兄弟列系统不同, 跨模型比较必须 z-score 标准化后比 β, 禁止直接比较原始系数或均值水平。ctx 轨语义与家族其余 ctx 列一致: 剔除与目标银行无关段落的稀释, conditional-on-full 行宇宙。降级语义为 per-model 独立: finbert2 经 FINBERT2_MODEL_DIR 环境变量解析本地路径, 未配置或路径无效时该模型整族 (含本列) 优雅缺席, 另两模型六列照常, 不适用 co-primary 嵌入的 both-or-neither 口径。与同模型 full、ss 列及跨模型 ctx 列均互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。解读上须把两个差分维度分开归因: 本列与 finbert2 的 full 列之差纯粹是文本口径效应 (语境收窄), 与三分类模型的 ctx 列之差纯粹是模型效应 (分类粒度与训练分布), 二者不可混谈; 当本列与两类参照都出现分歧时, 应先用同模型跨轨比较定位是语境还是模型驱动。本列无 _lg 孪生, 无加权与 _std/_sum 孪生, 确定性来自冻结权重加 argmax。

## VAR: finbert2_net_tone_full

【变体差分】
本列是 finbert2 模型净语调的 full 轨列, tier=core, 家族三个跨模型 co-equal 主轨列之一, 27_tableA12_cross_model_fwer 跨模型族错误率检验的直接参与者。模型口径: FinBERT2 是项目可获取的本地私有中文金融 BERT, 属在大规模金融语料上继续预训练再做情感微调的专用双向编码器谱系 — Xu 等 (2025) 的同名公开工作系统论证了此类金融专用编码器在情感分类等判别任务上相对通用大模型的持续优势, 是本列保留判别式路线的方法学锚点。区别于两个 HF 兄弟模型的关键结构差分是分类粒度: finbert2 为二分类 (负面、正面), 无中性标签, 正负概率近似互补, 篇级 net_tone 近似为二倍正面概率减一, 篇级分布呈双峰、远离零点; 由此产生两条解读铁律 — 其一, 本列与三分类兄弟列的原始方差不同刻度, Table A5 类跨模型并排必须 z-score 标准化后比较 β; 其二, 相邻分布形状族中 finbert2 的熵列是 Bernoulli 熵、与三分类模糊度构念不可比, 该告诫属五族口径但根源正是本列的二分类结构。文本口径: full 轨等于标题 prepend 加全文正文, 行宇宙由 full-only 留篇门控 (llm_verified_full) 定义。计算链路与家族一致: 滑窗 512、50% 重叠、置信度加权池化, encode 聚合后 post-agg 作差。降级语义是本列最独特的运维差分: finbert2 经 .env 的 FINBERT2_MODEL_DIR 解析, 未配置或路径不存在时优雅跳过 (per-model 独立降级, 仅掉 finbert2 自身列族, 兄弟模型不受影响), 这与两个 HF 模型在 strict_models 默认下加载失败即 fail-loud 的语义相反 — 私有模型缺席是预期状态, 公开模型缺席是故障。识别定位: 与 finbert_cn、fin_sent_zh 的 full 列 co-equal 互为稳健性、不分主次, 无 ensemble headline, 三模型各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与三轨、LLM 三家、词典多族梯子正交不交叉。本列在三兄弟中的独特证据价值恰在其"私有"属性: 两个公开 HF 模型的训练数据与标注体系是研究者不可控的外生给定, 若某种系统性标注偏好恰与银行新闻的语体相关, 两个公开模型可能同向偏置; finbert2 的领域再预训练路线提供了训练分布上真正独立的第三点, 三点不共线才构成有效的测量三角。同时私有属性也带来可复现性成本: 外部复现者无法获取该模型时, 本列整族缺席, 论文附录须以另两个模型的结果作可复现下界, 并在数据披露中说明该列的可获得性边界 — 这正是 per-model 独立降级语义在学术披露层的对应物。跨模型一致性检验中, 本列与三分类兄弟的比较须走缺标感知的 Krippendorff α (天然容忍二对三分类) 与重映射后的 Cohen κ (负一缺标哨兵先映射为非负码, 防与负面标签码冲突), 一致性系数只作测量质量披露, 不进回归。本列无 _lg 孪生 (非嵌入 carve-out), 无 _std/_sum 及加权孪生; 确定性来自冻结本地权重加 argmax, 混合精度对分类无影响。二分类模型无中性类的另一个实证后果是: 在以中性通稿为主的年份格上, 本列的均值会被强制推离零点, 其符号由通稿措辞的细微倾向决定, 解读薄格符号时应交叉参照三分类兄弟列与篇数分母。领域再预训练路线相对纯下游微调的方法学意义在 Xu 等 (2025) 中有直接论证: 在金融语料上继续预训练使编码器的底层表示先行适配金融术语与句法分布, 再做情感微调时标注信号只需校准判别边界而非从零学习领域语义, 这正是 finbert2 在训练分布上独立于两个公开 HF 模型的根源 — 后两者共享通用中文预训练底座, 其领域知识全部来自各自的下游标注集, 若两套标注集恰好共享某种针对财经文本的系统性偏好, 两模型可能同向偏置, 而 finbert2 的独立再预训练为三角测量提供了不共线的第三顶点。此外, 二分类结构使本列对"是否存在明确评价倾向"这一二元问题最敏感, 与三分类兄弟对"倾向是否强到脱离中性带"的判别形成互补: 同一篇弱倾向报道, 三分类模型倾向归入中性、贡献近零净语调, 而本列被迫二分、贡献一个方向明确但幅度由细微措辞决定的值, 这一系统性差异是相邻分布形状族的跨模型标签异质性列的直接构念来源, 也解释了为何本列在跨模型一致性系数上通常与三分类兄弟的分歧最大。

## VAR: finbert2_net_tone_ss

【变体差分】
本列是 finbert2 模型净语调在 ss 轨上的测量臂, 双重差分: 模型维为二分类的本地私有 FinBERT2, 文本维为银行与金融科技词同句最小语境窗。构念指向"银行金融科技叙事片段的二分类净语调"。ss 轨回退语义严格同全仓口径: 无银行与金融科技词同句共现时 content_ss 回退为全文正文、ss_is_fallback 置真、与 full 共享 n_articles 分母; 金融科技词自动机不可用时全篇回退优雅降级。二分类结构叠加窄语境有一个值得注意的交互: ss 窗口文本短、常为单窗推理, 无滑窗池化平滑, 且无中性类兜底, 因此本列篇级取值最锐、格级均值对个别强表态篇最敏感, 开发态 T=2 薄格上尤甚, 属预期退化而非缺陷。行宇宙为 conditional-on-full (full 留篇集子集)。降级语义 per-model 独立: FINBERT2_MODEL_DIR 缺席时本列整族优雅缺席, 不牵连兄弟。与同模型 full、ctx 及跨模型 ss 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型比较须 z-score 标准化。本列是全家族九列中测量方差最大的一列 (最窄语境乘最锐分类), 其证据角色因此偏向"方向性佐证"而非"量级估计": 当主规格在本列上保持同号且不失显著时, 说明效应对最极端的测量口径组合也稳健; 反之本列单独失显不足以推翻主结论, 只需在稳健性叙事中如实呈现并归因于测量方差。本列无 _lg 孪生, 无加权与 _std/_sum 孪生。

## VAR: finbert_cn_net_tone_ctx

【变体差分】
本列是 finbert_cn 模型净语调在 ctx 轨上的测量臂, 差分维度为模型加轨道: 模型为 yiyanghkust/finbert-tone-chinese (HF 公开、三分类中性/正面/负面, 微调基材偏向中文分析师报告与研报语体), 文本为标题 prepend 加银行实体上下文窗。构念是"银行实体邻近语境在研报风格情感空间中的净语调"。相对家族 canonical (同模型 full 轨) 的精确差分只有文本口径: ctx 窗剔除同篇中与目标银行无关的段落, 抑制多主体同稿与宏观背景段的稀释, 代价是可能截掉远端评价句。三分类结构使中性类吸收温和表述, 本列对明确正负表态敏感。留篇口径 conditional-on-full, 行宇宙为 full 留篇集子集, 均值按 ctx 轨自身非缺失篇数计。作为 HF 公开模型, 本列在 strict_models 默认下加载失败 fail-loud, 无优雅跳过 (与 finbert2 相反)。与同模型 full、ss 列及跨模型 ctx 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 三轨梯子与模型梯子正交不交叉, 跨模型比较须 z-score 标准化。研报语体与实体窗口的组合有一个值得利用的性质: 银行相关段落往往正是财务表现与监管表态的集中段, 与该模型微调语料的语体重叠度最高, 因此本列的判别置信度在三轨中通常最高, 是该模型三轨中信噪比较优的稳健臂; 本列无 _lg 孪生, 无加权与 _std/_sum 孪生, 确定性来自冻结权重加 argmax。

## VAR: finbert_cn_net_tone_full

【变体差分】
本列是 finbert_cn 模型净语调的 full 轨列, tier=core, 家族三个跨模型 co-equal 主轨列之一, 27_tableA12_cross_model_fwer 的直接参与者。模型口径: yiyanghkust/finbert-tone-chinese, Hugging Face 公开的中文金融情感三分类模型 (中性、正面、负面), 属金融领域 BERT 微调谱系 (方法基座见 Sun、Qiu、Xu 和 Huang (2019) 的 BERT 文本分类微调配方), 其微调语料偏向中文分析师报告与金融研报语体, 与 fin_sent_zh 的金融短语标注体系、finbert2 的领域再预训练形成训练分布三角。文本口径: full 轨等于标题 prepend 加全文正文, 是家族信息最全的轨道, 且行宇宙由 2026-06-29 起的 full-only 留篇门控定义 (llm_verified_full 为真的篇集), ctx 与 ss 是其 conditional-on-full 子集轨。计算链路: 篇级滑窗推理 (512 token 上限、50% 重叠、置信度加权池化各窗 logits) 得三标签概率, encode 层 bank-year 篇均后 post-agg 作差 (篇均正面概率减篇均负面概率), 取值 [-1,1]; 因推理失败逐篇原子 (正负概率同置 NaN), 面板差恒等于篇级净语调均值。差分定位: 相对家族内另两个 full 轨列, 本列唯一差分是模型; 研报语体微调使其在措辞正式、术语密集的银行新闻上判别置信度较高, 但对口语化与社交媒体风格文本的域移较大, 单列系统偏置须靠三模型并排稀释 — 这正是 per-model 家族的存在理由。三分类结构下中性类吸收温和与事实性陈述, 本列的净语调因此主要由明确带评价色彩的篇目驱动, 在通稿密集的银行年份格上取值贴近零而非被强制推向两端, 这一"敢于给零"的性格是它与二分类兄弟最直观的行为差异。三模型 co-equal 互为稳健性、不分主次, 无 ensemble headline, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 真 FWER 走根级 Romano-Wolf 模板, 跨模型 β 比较须 z-score 标准化 (三分类与二分类原始方差不同刻度)。运维口径: HF 公开模型, strict_models 默认下非预期加载失败 fail-loud (区别于 finbert2 的预期性优雅跳过); 本地重跑须设 HF 离线环境变量。本列的证据角色可以从"谁最可能被审稿人点名"来理解: finbert_cn 是中文金融情感研究中被引用与复用最广的公开基线之一, 审稿人复核时最可能自行下载重跑的就是它, 因此本列事实上承担着家族对外可复现性的门面 — 任何主结论若在本列上不成立, 即使另两个模型支持, 也难以通过外部复核, 这也是三列虽 co-equal 但在披露叙事中本列常被置于表格首列的原因 (首列位置是排版惯例而非计量地位, 铁律仍是不分主次)。研报语体微调的另一个可检验推论是: 对监管处罚、风险事件类新闻 (措辞正式、负面信号明确), 本列与词典法的一致性应最高; 对营销软文与产品发布类新闻 (措辞积极但信息稀薄), 本列倾向给出弱正或中性判断, 而无中性类的 finbert2 会被迫二分, 两列分歧在此类文本上系统性放大, 这一模式已内建于跨模型标签异质性列的构念设计。本列无 _lg 孪生 (非嵌入 carve-out), 无 _std/_sum 及 _vw/_mw/_hw 加权孪生 (Phase 2 设计取舍); 模型间一致性经 tone_validation 的 Krippendorff α 与重映射 Cohen κ 通道量化, 不进回归; 确定性来自冻结权重加 argmax, 面板作差为纯算术, 全链路 $0 后处理不触发任何付费调用。研报语体微调的方法学谱系可上溯至 Sun、Qiu、Xu 和 Huang (2019) 给出的 BERT 文本分类微调配方与 Reimers 和 Gurevych (2019) 关于 BERT 系编码器句子级语义表示能力边界的分析 — 后者恰是本项目对篇章级情感采用滑窗加池化而非简单截断的直接依据, 因为单窗表示无法无损承载超过 token 上限的长稿语义。作为中文金融情感研究中被复用最广的公开基线之一, 本列的领域微调语料与银行新闻中财务表现、监管表态段落的语体重叠度最高, 这既是它判别置信度较高的来源, 也是其系统性偏置的来源: 对与研报语体差异较大的社交媒体转述、口语化评论, 本列的域移最大, 单列无法自检该偏置, 只能靠与二分类的 finbert2、金融短语体系的 fin_sent_zh 并排, 以及与 LLM 三家、词典多族的跨方法印证来稀释 — 这正是 per-model 家族与三方法三角验证协同存在的根本理由 (Xu 等 (2025) 论证了保留判别式 BERT 路线相对全面转向生成式模型的持续价值)。

## VAR: finbert_cn_net_tone_ss

【变体差分】
本列是 finbert_cn 模型净语调在 ss 轨上的测量臂, 差分维度为模型 (yiyanghkust/finbert-tone-chinese, 三分类研报语体) 加文本轨道 (标题 prepend 加银行与金融科技词同句窗, 默认半径一句)。构念指向"银行金融科技同句叙事在研报风格情感空间中的净语调", 是该模型三轨中语境最窄、指向最锐的一列。ss 回退语义严格同全仓口径: 篇内无银行与金融科技词同句共现时 content_ss 回退为全文正文且 ss_is_fallback 置真, 与 full 共享 n_articles 分母; 金融科技词自动机不可用时优雅降级为全篇回退, 故本列在高回退格上向 full 轨收敛, 解读时应搭配回退占比。三分类结构下中性类吸收温和句, ss 短文本常为单窗推理、无滑窗池化平滑, 但中性兜底使本列比二分类兄弟 (finbert2 的 ss 列) 在薄格上更平缓。行宇宙 conditional-on-full。与同模型 full、ctx 及跨模型 ss 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 开发态 T=2 薄格退化属预期, 生产 T=18 改善。作为公开可复现模型与最窄语境的组合, 本列是外部复核者验证"金融科技叙事语调"构念最经济的入口: 模型可自由下载、文本窗口定义机械可复算, 复现门槛低于依赖私有模型的兄弟列; 本列无 _lg 孪生, 无加权与 _std/_sum 孪生, 跨模型比较须 z-score 标准化。

<!-- rendered-citations:begin -->
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Zafar, M. B. (2025). FinAI-BERT: A transformer-based model for sentence-level detection of AI disclosures in financial reports. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2507.01991
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, G. (2024). News bias in financial journalists' social networks. Journal of Accounting Research, 62(4), 1145-1182. https://doi.org/10.1111/1475-679X.12560
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science. https://doi.org/10.1007/978-3-030-32381-3_16
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of EMNLP-IJCNLP 2019, 3980-3990. https://doi.org/10.18653/v1/D19-1410
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
<!-- rendered-citations:end -->
