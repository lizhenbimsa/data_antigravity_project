---
family_id: F011
columns:
- attention_attr_share
- attention_disp_full
- attention_gap_full_ctx
unit: "无量纲: attention_disp_full 为跨媒体来源集中度 HHI ∈ (0,1]; attention_attr_share 为有界归因占比 ∈ [0,1]; attention_gap_full_ctx 为篇级强度差的组内均值 (实数, 无界)"
formula: "attention_disp_full = Σ_o (n_o / Σ_o n_o)² over 媒体(中文) (verified fintech 篇 outlet 份额平方和); attention_attr_share = Σ_d intensity_ctx / (Σ_d intensity_ctx + Σ_d intensity_full) = r/(1+r); attention_gap_full_ctx = mean_d(intensity_full − intensity_ctx); 零-(verified-)fintech bank-year → 三列均 NaN"
producer: "news_process/pipeline/panel/attention_media.py::compute_attention_treatments (面板 runner 步骤 6b-2; 值域校验 _validate_attention_treatments; codebook 条目 pipeline/panel/codebook.py::_ATTN_TREAT)"
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score_full / fintech_intensity_score_ctx)
- 12_fintech_news_full.parquet (is_fintech_news, 媒体(中文), 日期; 全集脊柱)
- 24_herd_decay.parquet (stage-21 verified 宇宙, (docid,target_bank) semi-join 门控)
citations:
- doi: 10.1002/mde.70100
  type: journal
  authors: Li, Y.
  year: 2026
  title: "The textual tone of annual reports and market attention: Evidence from Chinese listed companies"
  venue: Managerial and Decision Economics
- doi: "10.1287/mnsc.2023.02247"
  type: "journal"
  authors: "Dyer, T., Lang, M., & Oh, J."
  year: 2025
  title: "Media Conglomeration, Local News, and Capital Market Consequences"
  venue: "Management Science"
- doi: "10.1002/smj.3600"
  type: "journal"
  authors: "Meyer, T., Kerkhof, A., Cennamo, C., & Kretschmer, T."
  year: 2024
  title: "Competing for attention on digital platforms: The case of news outlets"
  venue: "Strategic Management Journal"
- doi: 10.1016/j.jempfin.2025.101670
  type: journal
  authors: Chen, Z., Li, Z., Liu, J., & Liu, X.
  year: 2026
  title: "Information salience, investor attention, and stock price crash risk"
  venue: Journal of Empirical Finance
  vol: 85
  pages_or_artno: "101670"
- doi: 10.1093/qje/qjaf002
  type: journal
  authors: Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A.
  year: 2025
  title: "The diffusion of new technologies"
  venue: The Quarterly Journal of Economics
  vol: 140
  issue: 2
  pages_or_artno: 1299-1365
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN
- doi: 10.2139/ssrn.5648287
  type: wp
  authors: Li, K., Lu, L. Y., & Wang, K.
  year: 2025
  title: "From firms to faces: How journalist-manager relationships shape corporate media coverage"
  venue: SSRN
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: "103870"
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3105-3147
- doi: 10.1111/acfi.13328
  type: journal
  authors: Ni, Y.
  year: 2024
  title: "Media coverage and disclosure of short-termism tone: Evidence from China"
  venue: Accounting & Finance
  vol: 64
  issue: S1
  pages_or_artno: 5107-5131
- doi: 10.1111/jofi.13219
  type: journal
  authors: Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R.
  year: 2023
  title: "Firm-level climate change exposure"
  venue: The Journal of Finance
  vol: 78
  issue: 3
  pages_or_artno: 1449-1498
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: The Review of Financial Studies
  vol: 36
  issue: 12
  pages_or_artno: 4919-4964
- doi: 10.48550/arXiv.2308.03531
  type: arxiv
  authors: Färber, M., Schwade, J., & Jatowt, A.
  year: 2023
  title: "Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election"
  venue: arXiv
- doi: 10.1257/aer.20191823
  type: journal
  authors: Caldara, D., & Iacoviello, M.
  year: 2022
  title: "Measuring geopolitical risk"
  venue: American Economic Review
  vol: 112
  issue: 4
  pages_or_artno: 1194-1225
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1287/mnsc.2020.3682
  type: journal
  authors: Bellstam, G., Bhagat, S., & Cookson, J. A.
  year: 2021
  title: "A text-based analysis of corporate innovation"
  venue: Management Science
  vol: 67
  issue: 7
  pages_or_artno: 4004-4031
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: "Media bias in China"
  venue: American Economic Review
  vol: 108
  issue: 9
  pages_or_artno: 2442-2476
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: "The media and the diffusion of information in financial markets: Evidence from newspaper strikes"
  venue: The Journal of Finance
  vol: 69
  issue: 5
  pages_or_artno: 2007-2043
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: "In search of attention"
  venue: The Journal of Finance
  vol: 66
  issue: 5
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: "The causal impact of media in financial markets"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 67-97
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: W.E. Upjohn Institute for Employment Research
- doi: 10.1038/163688a0
  type: journal
  authors: Simpson, E. H.
  year: 1949
  title: "Measurement of diversity"
  venue: Nature
  vol: 163
  issue: 4148
  pages_or_artno: "688"
- doi: "10.2139/ssrn.5279231"
  type: "wp"
  authors: "Cao, Z., Geman, H., & Wunkaew, W."
  year: 2025
  title: "The Hype Index: an NLP-driven Measure of Market News Attention"
  venue: "SSRN"
- doi: "10.2139/ssrn.4768558"
  type: "wp"
  authors: "Guo, X., Macaulay, A., & Song, W."
  year: 2024
  title: "The Allocation of Corporate News"
  venue: "SSRN Electronic Journal"
new_dois:
- "10.1287/mnsc.2023.02247"
- "10.1002/smj.3600"
- "10.2139/ssrn.5279231"
- "10.2139/ssrn.4768558"
---

## CORE

研究本地媒体所有权集中化(报业集团整合)如何削弱本地新闻覆盖的独立性与信息含量,并进而影响被覆盖公司的资本市场结果(如信息不对称与融资成本),为本家族的来源集中度构念提供直接的实证对照。 考察新闻媒体在数字平台上争夺读者注意力的竞争动态与由此产生的报道供给结构,呼应本家族用媒体来源分布集中度刻画'由谁来写'这一供给侧结构问题的构念。

【构念与来源】
本家族 (F011, 家族键 l2c_attention) 是 P2 论文 bank_fintech_attention 注意力处理变量族中的结构与归因派生支, 共三列: 跨媒体曝光集中度 attention_disp_full (家族 canonical, core 列)、归因纯度 attention_attr_share 与归因借位 attention_gap_full_ctx。它们与同一生产函数产出的量级测度 (attention_index 累积曝光、attention_pct 议程份额、attention_intensity_density 强度密度) 构成互补分工: 量级测度回答"这家银行的金融科技议题被媒体报道了多少", 本家族回答两个更深一层的结构问题。其一是供给结构问题: 这些报道由怎样的媒体结构供给, 是集中在少数几家媒体手里反复出现, 还是广泛分散于众多相互独立的媒体; 这是集中度维度。其二是内容归因问题: 报道正文里的金融科技内容, 有多大比例真正归因于目标银行自身的业务与动作, 而不是借了同篇报道中其他主体、行业综述段落或政策背景铺陈的"光"; 这是归因维度。前者由集中度列承载, 后者由归因占比与归因差两列以相对与绝对两种口径共同承载。三列同产于面板 runner 步骤 6b-2 的处理变量物化函数, 共享同一个银行乘年份分组、同一个 stage-21 verified 样本宇宙与同一套缺失契约, 因此在构念上是一组而非三个孤立测度。

媒体注意力文献里, 覆盖量的一阶后果早有充分证据: Fang & Peress (2009) 证明媒体覆盖在股票截面上被定价, 无覆盖股票相对高覆盖股票存在系统性收益差; Da 等 (2011) 用检索量刻画投资者的直接注意力并与媒体覆盖对照; Tetlock (2007) 证明媒体内容本身携带可定价的情绪信息; Bybee 等 (2024) 进一步表明新闻语料的主题结构足以复现宏观经济周期的主要状态变量, 说明新闻文本不仅是噪声也是可提取的经济状态载体。但同等数量的报道, 其信息生产结构可以截然不同: 一条被单一媒体反复报道的议题与一条被众多独立媒体各自报道的议题, 前者的信号更可能反映单个编辑部的立场或与被报道方的关系, 后者则更接近独立多源验证。Cookson 等 (2024) 表明分布在不同平台、不同受众之间的信号结构本身携带独立于信号均值的信息; Färber 等 (2023) 在媒体覆盖测量方法学上系统化了多样性、均衡性与差异性三个互不可替代的分布维度, 本家族的集中度列正落在该框架的均衡性维度上。集中度用 Herfindahl-Hirschman 指数操作化, 即来源份额的平方和, 数学上等价于 Simpson (1949) 在生态多样性测量中提出的经典统计量, 是分布均匀程度的二阶泛函, 具有对来源合并与拆分敏感、对零份额来源不敏感的良好性质。

归因维度的构念动机来自本管道的三轨文本架构: full 轨等于标题加全文正文, ctx 轨等于标题加目标银行的实体窗口文本, ss 轨等于标题加银行与金融科技词同句共现的窗口句。全文强度天然混入"非本行段落"的金融科技词命中 — 一篇同时报道多家银行、或以行业综述为主体只顺带提及目标银行的文章, 其全文金融科技强度可能远高于真正谈及目标银行的部分。归因差与归因占比两列把 full 与 ctx 两轨篇级强度的差值与占比物化为面板测度, 分别以绝对量纲与无量纲相对口径刻画这种借位的程度。该构念在中文财经媒体场景中尤为要紧: 中国媒体报道多综述体、多主体并列成文, 且媒体结构本身带有系统性偏倚 (Qin 等 (2018) 对中国媒体偏倚的刻画); 中国上市语境下媒体覆盖与文本语调测度的近期实证见 Ni (2024) 与 Li (2026)。不加归因修正的全文口径测度, 在这类语料上更容易高估个体银行的真实曝光, 本家族的两个归因列正是对这一测量风险的显式建模, 使研究者可以在稳健性阶段用归因修正过的口径复核主处理变量的构念效度。

【方法学与计算】
上游链条从语料治理开始: stage 00 预处理完成两级去重。第一级是精确去重, 以标题加正文完全匹配为键, 在完全重复簇内按日期升序保留首发副本 (媒体权重降序、docid 升序仅作同日 tiebreak, 缺日期副本排末), 刻意让年度归属锚定首发时间而非最高权重版本以免跨年转载错配面板年份。第二级是近似去重, 用 MinHash LSH 识别转载与通稿簇: 对每篇算字符三元组的 MinHash 指纹, 由 LSH 生成候选簇, 簇内成员仅当其与触发它的已保留文的真实字符三元组 Jaccard 相似度达到阈值 0.8、且落在首发文起五个工作日窗口内的后发稿, 才被判为重复删除; 间隔更久的 (如周年回顾) 保留。须知阈值 0.8 是概率性近似阈值而非硬阈值: 在当前 MinHash 排列数与分带下, 有效的百分之五十检出阈值略高于 0.8, 去重整体偏保守 — 偏向漏删轻度改写的转载而非误删独立文章, 因此本家族的注意力测度更可能低估而非高估集中与借位。去重口径服务于"信息到达"构念: 通稿与转载不携带新信息, 计入会系统性高估注意力; 与之分工的"传播广度"构念 (转载次数本身就是构念) 由 falsification 侧的 nf_media_breadth 在去重之前的物理行集上另行实现, 两套口径并存、各管各的构念, 不是矛盾而是分工。

随后 stage 11 与 stage 12 完成银行识别与金融科技识别, stage 13 做银行与金融科技词邻近共现的硬过滤, stage 14 物化三轨文本 (标题 prepend 进正文), stage 15 产出篇级金融科技强度分 (full、ctx、ss 三轨孪生)。该强度分是逆文档频率加权的金融科技词命中经文长归一化后的分值, 其"词命中即技术关注"的操作化与 Kalyani 等 (2025) 用文本词组识别新兴技术并追踪其扩散的当代范式同源。文长归一化是理解归因两列的关键: 因为 ctx 文本比 full 短, 同一命中在密度口径下的贡献可以更大, 这使得 ctx 轨强度密度合法地可以高于 full 轨, 这一事实直接决定了下文归因占比的构造选择。

面板聚合发生在 runner 步骤 6b-2 的处理变量物化函数, 分组键为银行乘年份。本家族三列的输入均收敛到 stage-21 verified 宇宙, 但门控是不对称的双层设计。强度分子帧 (取自 15_fintech_intensity) 与集中度的媒体来源分布 (取自 12_fintech_news_full 的金融科技子集) 都经 (docid, target_bank) 半连接对齐 24_herd_decay 所承载的 verified 集, 剔除被大模型三家投票判伪的"非真实银行金融科技文章"; 与此相对, 议程份额一类量级测度的分母 (该行该年全部银行新闻计数) 刻意保持未门控以维系份额语义, 但那属于本家族之外的列。经盘面实测 verified 集是金融科技子集的子集, 故门控后媒体来源分布的非空银行年集合与强度帧的非空银行年集合恒一致, 这保证了篇数为零与集中度缺失的等价契约由回归测试锁定。留篇门控执行 full-only 口径 (2026-06-29 裁定): 一篇文章是否算作银行金融科技报道只看 llm_verified_full 一个旗标, ctx 与 ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集。

三列公式如下。集中度列: 对每个银行年, 先按媒体(中文)字段数各来源的 verified 金融科技篇数, 用组内变换求该银行年总篇数, 逐行算来源份额并平方, 再组内求和; 实现为向量化的分组变换而非逐组 apply, 这是刻意规避性能陷阱的工程设计, 取值与逐组实现逐位一致。归因占比列: 等于 ctx 轨强度总和除以 ctx 与 full 两轨强度总和之和; 记两轨总强度之比为 r, 该占比恒等于 r 除以一加 r, 是 r 的严格单调变换, 保序且无删失, 结构性落于零一闭区间。归因差列: 等于篇级强度 full 减 ctx 之差在银行年内的算术均值。归因占比的现行构造有一段须知的撤回史: 旧口径直接取 ctx 与 full 总强度之比再截尾到零一区间, 但因两轨各自做文长归一化、ctx 短文本的强度密度合法地可以高于全文, 该比值在结构上可以大于一, 截尾把越界质量右删失到端点并破坏删失区内的排序 — 这是系统性的测度后果而非浮点边角, 故于 2026-06-11 修订为现行的有界占比构造, 面板列语义自此变更, 复现旧版结果须注意版本断代。

缺失值遵守双层不对称契约。第一层: 面板骨架是全银行乘全年份的笛卡尔积, 其中完全没有任何银行新闻的银行年 (不在 12_full 全集之内) 经左连接天然得全列缺失 — 无新闻即注意力不可测, 回归中被 listwise 删除是正确行为而非数据缺陷。第二层: 在全集之内、有银行新闻但零 verified 金融科技报道的银行年, 量级测度 (index、pct、density) 填真实的零 (真零曝光是信息性的), 而本家族三列一律置缺失 — 没有金融科技报道, 就谈不上这些报道的来源集中度, 也谈不上两轨强度的借位与占比, 强行填零会把"不可定义"伪装成"低集中"或"零借位"。工程防御上, 两轨强度总和先做下界为零的截断 (上游逆文档频率权重在某金融科技词近乎全文档出现时理论上可转负的结构性防御, 对当前非负数据是无操作), 归因占比的除零经显式替换为缺失, 集中度与占比两列再经值域校验函数的零一断言 (带数值容差) 与逐列分布日志诊断把关。

【文献定位】
在 text-as-data 的测量谱系 (Gentzkow 等 (2019)) 中, 本家族对应"从水平到分布"的测度深化。同一生产函数的量级测度主锚遵循 extensive 与 intensive 之辨: attention_index 是 Fang & Peress (2009) 式的 extensive 累积曝光 (对数化的强度总和, 未按篇数或文长归一), 刻意区别于 Hassan 等 (2019) 的 intensive 归一化份额范式, 后者的份额语义在本管道中由 attention_pct 与 density 两列承担。公司层文本暴露份额范式此后扩展到气候暴露 (Sautner 等 (2023)) 与疫病暴露 (Hassan 等 (2023)) 等主题维度; 以报纸语料构建可审计的时序与截面指数所须遵循的方法学纪律见 Caldara & Iacoviello (2022)。本家族三列则不落在量与份额的任何一格: 集中度是覆盖供给侧的分布形状统计量, 归因差与归因占比是跨轨的归因泛函, 三者共同构成量级测度之上的结构补层。银行乘年份粒度的媒体文本聚合口径本身另有近期工作可资对照 (Marchetti 等 (2025) 以银行融资条件为对象的媒体语调聚合); 媒体覆盖影响公司股权风险的近期证据见 Gutknecht (2025); 信息显著性与投资者注意力交互的近期证据见 Chen 等 (2026)。

【识别策略定位】
P2 论文的主处理变量是 attention_index_full (extensive 累积曝光, 由篇级金融科技强度总和取对数化), 本家族三列均不担任 primary treatment, 各自有明确的从属识别定位。第一, 集中度列作覆盖结构的调节 (moderation) 与异质性切割变量: 在同等注意力水平下, 集中供给 (少数媒体反复发稿) 与分散供给 (众多相互独立的媒体各自发稿) 所隐含的信息生产独立性截然不同, 前者的信号更可能只反映单一编辑部的立场或其与被报道方的关系, 后者更接近多源独立验证。据此可做异质性检验: 若注意力对结果变量的效应在低集中 (低 HHI、多源独立报道) 子样本中系统性更强, 则支持"信息驱动"的因果解读而非"单一媒体噪声"解读; 反之若效应集中在高 HHI 子样本, 则提示估计可能被个别媒体的选择性报道或议题操纵所污染, 须审慎处置。第二, 归因差与归因占比作机制 (mechanism) 与测量效度 (construct validity) 变量: 若主效应主要由高借位 (差值大、占比低) 的银行年驱动, 提示全文口径的处理变量混入了大量非本行归因的成分 (行业综述、政策铺陈、他行并列成文), 须在稳健性中改以 ctx 轨处理变量复核主结论; 反之若效应在低借位子样本中同样稳健, 则支持全文测度的构念效度。第三, 三列均可进入描述性统计与诊断性表格, 向审稿人提供测度构造的透明度与样本的结构画像, 使处理变量的口径可审。

媒体覆盖的内生性是本设计不可回避的首要识别威胁, 且威胁是双重的。其一是覆盖水平与被覆盖对象基本面互为因果的经典反向因果。其二更隐蔽: 覆盖的供给结构本身并非随机分配 —— 记者与管理层之间的关系网络会系统性地塑造哪些公司被谁报道 (Li 等 (2025) 以记者与管理层关系刻画公司媒体覆盖的形成), 使得来源集中度本身内生于公司特征与关系结构。因此集中度不能被当作外生回归元直接作因果解读, 而应在高维固定效应吸收与工具变量框架之内, 作调节或条件变量使用。经典的因果分离设计为处置覆盖内生性提供了范式: Engelberg & Parsons (2011) 借地方媒体对同一事件的差异化转载, 把"报道本身的效应"从"事件的效应"中剥离; Peress (2014) 借报纸罢工构造准实验, 直接切断信息中介渠道以识别媒体的独立作用; 覆盖本身被市场定价的基准事实见 Fang & Peress (2009)。本管道在面板层配备 IV 扩展列族作为识别工具箱, 含三引擎: 同组留一均值 (leave-one-out peer mean)、广义 Bartik (share×shift 暴露) 与媒体来源 house-style 暴露。广义 Bartik 引擎沿用 Bartik (1991) 的份额乘冲击范式, 其识别有效性依赖两条互补路径之一 —— 份额外生 (Goldsmith-Pinkham 等 (2020) 论证的 what/when/why/how 路径, 把识别力寄于暴露份额的准随机分配) 或冲击外生 (Borusyak 等 (2022) 的准实验 shift-share 设计, 把识别力寄于共同冲击的外生性)。本家族三列进入回归时按调节或中介框架处理, 归因两列尤其服务于对全文口径处理变量的测量效度审计, 而非作为外生处理直接读取系数并作因果解读。

口径铁律必须复述: 三轨 (full/ctx/ss)、co-primary 双轨嵌入以及一切梯子 (消融、政治词权重、阈值、判据) 的每一臂各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨或不同臂混进同一个 over-identified 方程去跑 Hansen J 过度识别检验。须特别澄清一个易被误读的边界: 归因差与归因占比虽在构造上同时消费 full 与 ctx 两轨强度, 但它们是跨轨泛函派生出的单一测度列 (一列一值), 与"把 full 与 ctx 两轨各当一个工具塞进同一 over-identified 方程"是两码事 —— 后者才是本仓架构明令禁止的做法, 前者只是用两轨信息合成一个新测度, 完全合规, 二者不可混为一谈。

【与相邻测度的构念区分】
与同一生产函数量级列的分工已如上述, 更易混淆的是若干近邻测度, 逐对辨清如下。第一对, attention_disp_full 对 attention_intensity_sd 族: 后者是篇级金融科技强度分布的标准差 (二阶矩, ddof=1, 篇数小于二时置缺失), 随机对象是"每篇报道写得多深"的内容强度离散, 且随 full、ctx、ss 三轨各产孪生列; 前者是媒体计数分布的份额平方和, 随机对象是"由谁来写"的供给来源集中, 是不依赖轨道文本的单轨测度。两者构念正交: 一个高度集中的媒体结构完全可以搭配高或低的内容强度离散, 反之亦然, 二者可同表并列而不互替。第二对, attention_disp_full 对 attention_pct_full: 二者虽都是 track-agnostic 单轨测度, 但构念与样本口径皆不同 —— pct 测的是金融科技新闻占该行该年全部银行新闻的议程份额, 其分母取自未经验证门控的全部银行新闻 (Fang & Peress (2009) 式的覆盖分母, 非金融科技行物理上不可门控), disp 测的是已门控金融科技子集内部的来源集中, 分母是该子集自身。议程份额高并不蕴含集中度高: 一个份额很高的银行年既可由众多媒体分散报道 (低 HHI), 也可由单一媒体密集报道 (高 HHI)。第三对, attention_disp_full 对 media_hhi: 后者属媒体维度族, 在情感文章帧的全部留存报道上计算来源集中度, 未限定于 verified 金融科技子集, 两列的样本口径不同, 回归中不可互替, 同表并列须在表注写明口径差。第四对, 归因差对归因占比: 二者互为绝对与相对口径 —— 差值保留强度量纲、对两轨水平的共同缩放敏感, 占比无量纲、对共同缩放不变, 且二者不是彼此的单调变换 (差值可正可负、无界, 占比恒落零一区间), 并排提供而非互相替代。

再往外一层, 本家族与两个貌似相关实则异构念的列族须严格区隔。其一, 去重前口径的 nf_media_breadth (falsification 侧, 转载次数本身即"传播广度"构念) 与本家族去重后的"信息到达"口径分工并存、各管各的, 不可互替。其二, 地理注意力指数族 (ft_attn_yr/prov/city 及总量孪生, 银行媒体邻域的省市地理曝露工具, 带小地理单元最低文章数门槛) 是二阶邻域曝露量而非银行自身覆盖计数, 属另一支。喂入归因两列的篇级金融科技强度分本身是文本词命中式的测度, 其"词命中即技术关注"的操作化与当代文本计量范式同源 (Kalyani 等 (2025) 用文本词组识别新兴技术并追踪扩散; Bellstam 等 (2021) 以文本刻画公司创新), 由此可把三个正交的信息维度分辨清楚: 强度与其离散刻画"写得多深", 集中度刻画"由谁来写", 归因差与归因占比刻画"多大程度真正归因于目标银行"。另有 n_outlets 诊断列记录参与集中度计算的独立媒体家数, 至少两家集中度才有跨格变异。命名警示 (修订台账 omni-g-attention-06): attention_disp_full 列名中的 disp 是历史命名, 其语义是集中度而非分散度, 高值等于集中等于低分散, 系数符号的解读切勿按列名字面反向。

【已知局限与稳健性梯子】
局限一, 来源粒度依赖: 集中度以媒体(中文)字段的出版物名称为计数单元, 同一传媒集团旗下多个刊名会被视为不同来源, 机械上低估真实的所有权集中; 语料以报纸为主的构成也使该字段的粒度总体偏"刊"而非"集团", 论文解读时应表述为刊名层集中度而非集团层集中度。且如识别策略节所述, 来源结构本身内生于记者与管理层的关系网络 (Li 等 (2025)), 集中度的跨行差异不宜作外生变异直接解读。局限二, 小样本偏差: verified 金融科技篇数很少时集中度机械偏高 (单一来源恒等于一), 归因差与归因占比在少篇格上也更嘈杂; 为此本函数配套物化 n_outlets 与 n_fintech_articles 两个诊断列, 用于识别并在稳健性中按篇数或家数门槛剔除这类薄样本格。早期试跑盘 T=2 深度下格间波动大属预期退化, 本家族三列的设计功效要在生产 T=19 语料上才充分释放, 不可用 T=2 的浅样本表现否证测度构造。局限三, 参数依赖: 三列都建立在 stage 00 去重后语料上, 对去重参数敏感 —— 精确去重按标题加正文匹配保留首发副本, 近似去重用 MinHash LSH 在 Jaccard 相似度阈值 0.8 与首发起五个工作日窗口内识别转载, 该阈值是概率性近似阈值而非硬阈值 (当前排列数与分带下有效检出阈值略高于名义 0.8), 去重整体偏保守。为量化这一敏感性, 面板在步骤 6b-3 物化了去重阈值敏感性变体列族 (attention 各列在不同 Jaccard 阈值与工作日窗宽下重算的后缀变体), 供复跑对照; 须知该变体族有两处口径限定 —— 它是"生产去重之上的更严两阶段近似"而非 raw-direct 等价, 且只在银行新闻子集内重判重复 (跨语料的近似重复对其不可见)。归因两列还额外依赖 stage 15 的文长归一化设定与 ctx 实体窗口参数。论文须在数据小节披露 verified 门控的剔除比例与去重规则 (具体数值由引擎注入的动态统计与生产日志披露, 本文不手填)。

梯子叙事须与量级姊妹列对照理解。index、density、sd 三个量级姊妹列各产 full、ctx、ss 三轨孪生, 而本家族三列刻意不产 ss 孪生: 归因差与归因占比按定义锚定 full 对 ctx 的归因对照 (ss 是银行与金融科技词同句共现轨, 换入归因对照会替换掉"借位"这一构念本身, 属架构层的有意设计而非遗漏), 集中度与议程份额则为不依赖轨道文本的 track-agnostic 单轨测度, 无三轨概念可言。ss 轨的回退语义 (镜像 ctx) 为: 无银行与金融科技词同句共现时, ss 文本回退为全文正文并置 fallback 旗标, 与产 ss 孪生的姊妹列共享 n_articles 分母 —— 该语义只影响那些产 ss 孪生的姊妹列, 本家族无 ss 列故不直接受其影响, 但研究者在同表解读姊妹列时须知其存在。留篇门控执行 full-only 口径 (2026-06-29 裁定): 一篇文章是否算作银行金融科技报道只看 llm_verified_full 一个旗标, ctx 与 ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集; 本家族的 verified 门控正是通过 (docid, target_bank) 半连接落到这一 full-only 留篇集上, 与 n_articles 分母口径一致。最后重申正交与铁律: 本家族与词典消融梯子、政治词权重梯子、跨厂商 per-model 梯子相互正交、不交叉组合; 一切梯子与轨道的每一臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: attention_attr_share

【变体差分】本列与家族 canonical (attention_disp_full) 的差分在于测量对象整体不同: canonical 测覆盖供给的来源集中度, 本列测报道内容的归因纯度, 是 full 与 ctx 两轨篇级强度的跨轨相对泛函。构造: 对每个银行年, 先在 verified 宇宙内分别求 ctx 轨与 full 轨篇级强度的总和, 本列等于 ctx 总和除以两轨总和之和; 记两轨总强度之比为 r, 则本列恒等于 r 除以一加 r, 是 r 的严格单调变换, 保序、无删失、结构性落于零一闭区间。数值语义: 取值二分之一意味着两轨归一化密度相等, 数值越大代表报道的金融科技强度越集中于目标银行实体窗口之内, 归因越纯; 越小代表全文强度更多来自实体窗口之外的段落, 借位越重。两轨总和为零 (零 verified 金融科技报道的银行年) 时置缺失, 与家族缺失契约一致; 两轨总和已先经非负截断, 故本列无需再做任何截尾。历史差分须知: 旧构造直接取两轨总强度之比并截尾到零一区间, 但 ctx 短文本经文长归一化后密度可合法高于全文, 比值结构上可大于一, 截尾造成右删失并破坏删失区内排序, 于 2026-06-11 撤回并换为现行占比, 面板列语义自此变更, 复现旧结果须注意版本断代。与姊妹列 attention_gap_full_ctx 的差分: 本列是相对占比、对两轨强度的共同缩放不变, 姊妹列是绝对差、保留量纲, 二者非单调一一对应, 并排使用不互替。本列无三轨后缀亦不产 ss 孪生 — 归因构念按定义锚定 full 对 ctx 的对照。用法定位: 归因机制与测量效度变量, 不作主处理; 与其余轨道及梯子臂各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。

## VAR: attention_disp_full

【变体差分】本列是家族 canonical 且为 core 列, 承担 P2 注意力分散测度的规范载体职能。构造细节: 对每个银行年, 在 stage-21 verified 宇宙内取该行该年全部金融科技报道 (12_full 的 is_fintech 子集经 (docid, target_bank) 半连接门控, 与强度分子严格同域), 按媒体(中文)字段计各来源篇数, 以组内变换 (groupby transform) 求该银行年总篇数, 逐行算来源份额并平方, 再组内求和即得 Herfindahl-Hirschman 集中度; 实现为向量化的分组变换而非逐组 apply, 这是刻意规避 groupby-apply 性能炸弹的工程设计, 数值上与逐组实现逐位一致。值域为零到一之间且不含零下端: 全部报道出自单一媒体时恒等于一, 来源越均匀数值越低, 均匀分布于 k 家媒体时等于 k 分之一, 随 k 增大趋近于零但永不达零。

两重命名警示是本列解读的第一要务, 二者都源于历史命名而与当前语义不符。其一, 列名中的 disp 字面意为分散 (dispersion), 但本列语义是集中度 (concentration) 而非分散度, 高值等于集中等于低分散 (修订台账 omni-g-attention-06); 若研究设计需要"分散度"方向, 应在回归前显式取补或反号并在表注中说明, 切勿按列名字面把系数符号反向解读。其二, 列名的 full 后缀同样是历史命名产物, 本列实为不依赖轨道文本的 track-agnostic 单轨测度 —— 媒体来源分布只取决于是谁发的稿, 不依赖 full、ctx、ss 任何一轨的正文内容, 金融科技判定来自文章级 is_fintech 旗标而非轨道文本, 因此本列不产 ctx 与 ss 孪生; 输入包 columns.json 里"三轨 full/ctx/ss"的差分提示对本列并不适用, 一律以生产函数注释与 codebook 条目的单轨口径为准。

缺失契约: 零 verified 金融科技报道的银行年置缺失 (无报道即无来源分布可言), 这与同族量级列 (index、pct、density) 在零金融科技银行年填真实零的口径刻意不对称 —— 真零曝光是信息性的、可入回归, 而集中度在无报道时不可定义、强行填零会把"不可定义"伪装成"低集中"。篇数为零与本列缺失的等价关系由回归测试锁定: 经盘面实测 verified 集是金融科技子集的子集, 故门控后媒体来源分布的非空银行年集合与强度分子帧的非空银行年集合恒一致, 保证 n_fintech_articles 为零当且仅当本列缺失。诊断配套: n_outlets 列记录参与计算的独立媒体家数, 至少两家本列才有跨格变异; 少篇格的集中度机械偏高, 稳健性建议按篇数或家数设门槛复跑并报告结果稳定性。

构念谱系: 份额平方和即 Simpson (1949) 在生态多样性测量中提出的经典统计量, 在媒体覆盖测量的多样性—均衡性—差异性三维框架中对应均衡性维度 (Färber 等 (2023)); 来源与受众结构携带独立于信号均值的信息这一近期证据见 Cookson 等 (2024); 覆盖本身被市场定价的基准事实见 Fang & Peress (2009), 与检索量式直接注意力代理的对照见 Da 等 (2011); 而覆盖供给结构本身内生于记者与管理层关系网络的证据见 Li 等 (2025), 故本列宜作调节或条件变量而非外生回归元。与近邻列的差分: 对 attention_intensity_sd 族 (篇间内容强度的二阶矩, 随机对象是每篇写得多深而非由谁来写) 构念正交; 对 attention_pct_full (议程份额, 分母为未门控的全部银行新闻) 构念与样本口径皆不同; 对 media_hhi (媒体维度族在情感文章帧全部留存报道上算的来源集中度, 未限 verified 金融科技子集) 样本口径不同; 三者均不可与本列互替, 同表并列时须在表注中写明口径差。计量用法: 作覆盖结构的调节与异质性变量进入 P2 设计, 不作主处理; 因量纲为纯数且分布通常右偏于高集中端, 建议标准化后解读边际效应; 与三轨及各梯子臂各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。局限提醒: 刊名层粒度会低估集团层集中, 去重参数 (信息到达构念的去重基, Jaccard 阈值为概率性近似且整体偏保守) 影响篇数进而影响份额, 早期试跑盘 T=2 浅样本下的格间波动属预期退化, 生产 T=19 语料上方具设计功效。近期方法学文献进一步丰富了该测度谱系: Cao, Geman, & Wunkaew (2025, SSRN) 提出基于新闻计数份额与市值调整的 Hype Index, 把媒体覆盖强度与语调情感解耦, 用 NLP 方法量化个股与行业获得的相对媒体关注度; Guo, Macaulay, & Song (2024, SSRN Electronic Journal) 记录公司新闻报道在企业间高度集中于大公司的分布结构, 并表明媒体覆盖对小公司融资与投资的边际影响更大, 为覆盖集中度构念提供实证依据。

## VAR: attention_gap_full_ctx

【变体差分】本列与家族 canonical 的差分同样在测量对象: 不测来源集中度, 而以绝对口径测 full 与 ctx 两轨强度的归因借位。构造: 对每个银行年, 在 verified 宇宙内取每篇报道的 full 轨强度减 ctx 轨强度之差, 求组内算术均值。数值语义: 正值越大, 全文强度越多来自目标银行实体窗口之外的段落 — 即该行该年的金融科技曝光越多是借同篇报道中行业背景、政策铺陈或其他主体之光, 借位与稀释越重; 接近零表示报道紧扣本行实体语境; 理论上可为负, 因两轨强度各自做文长归一化, ctx 短文本的密度可以合法高于全文, 负值表示实体窗口内的金融科技密度反而更高。值域无界 (实数), 不做任何截断或缩尾; 零 verified 金融科技报道的银行年组内均值不可定义, 置缺失, 与家族缺失契约一致。差分要点有三。第一, 列名后缀 full_ctx 表明本列按定义锚定 full 对 ctx 的归因对照, 刻意不产 ss 孪生 — ss 是银行与金融科技词同句共现轨, 换入 ss 会把"归因借位"换成另一个构念, 这是架构层的有意设计而非遗漏。第二, 与姊妹列 attention_attr_share 互为绝对与相对口径: 本列保留强度量纲、对两轨强度的共同缩放敏感, 姊妹列无量纲、对共同缩放不变, 二者非单调对应, 并排提供各管各的构念侧面。第三, 本列基于篇级均值而非总和, 与量级列的累积口径不同, 对篇数变化的敏感性也不同。用法定位: 机制变量 — 在主效应回归之外检验借位程度是否驱动或稀释注意力效应, 亦可作全文口径处理变量的测量效度审计; 不作主处理, 不与其余轨道或梯子臂混进同一 over-identified Hansen J, 各臂各自 just-identified 并排、互为稳健性、不分主次。

<!-- rendered-citations:begin -->
Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
Dyer, T., Lang, M., & Oh, J. (2025). Media Conglomeration, Local News, and Capital Market Consequences. Management Science. https://doi.org/10.1287/mnsc.2023.02247
Meyer, T., Kerkhof, A., Cennamo, C., & Kretschmer, T. (2024). Competing for attention on digital platforms: The case of news outlets. Strategic Management Journal. https://doi.org/10.1002/smj.3600
Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, 101670. https://doi.org/10.1016/j.jempfin.2025.101670
Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. The Quarterly Journal of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Li, K., Lu, L. Y., & Wang, K. (2025). From firms to faces: How journalist-manager relationships shape corporate media coverage. SSRN [Working Paper]. https://doi.org/10.2139/ssrn.5648287
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. Accounting & Finance, 64(S1), 5107-5131. https://doi.org/10.1111/acfi.13328
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Färber, M., Schwade, J., & Jatowt, A. (2023). Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2308.03531
Caldara, D., & Iacoviello, M. (2022). Measuring geopolitical risk. American Economic Review, 112(4), 1194-1225. https://doi.org/10.1257/aer.20191823
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. Management Science, 67(7), 4004-4031. https://doi.org/10.1287/mnsc.2020.3682
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Bartik, T. J. (1991). Who benefits from state and local economic development policies? W.E. Upjohn Institute for Employment Research. https://doi.org/10.17848/9780585223940
Simpson, E. H. (1949). Measurement of diversity. Nature, 163(4148), 688. https://doi.org/10.1038/163688a0
Cao, Z., Geman, H., & Wunkaew, W. (2025). The Hype Index: an NLP-driven Measure of Market News Attention. SSRN [Working Paper]. https://doi.org/10.2139/ssrn.5279231
Guo, X., Macaulay, A., & Song, W. (2024). The Allocation of Corporate News. SSRN Electronic Journal [Working Paper]. https://doi.org/10.2139/ssrn.4768558
<!-- rendered-citations:end -->
