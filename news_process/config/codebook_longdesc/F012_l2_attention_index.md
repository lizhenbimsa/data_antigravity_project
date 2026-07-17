---
family_id: F012
columns:
- attention_index_ctx
- attention_index_ctx_j70w10
- attention_index_ctx_j70w5
- attention_index_ctx_j75w5
- attention_index_ctx_j80w10
- attention_index_full
- attention_index_full_j70w10
- attention_index_full_j70w5
- attention_index_full_j75w5
- attention_index_full_j80w10
- attention_index_ss
- attention_index_ss_j70w10
- attention_index_ss_j70w5
- attention_index_ss_j75w5
- attention_index_ss_j80w10
unit: 无量纲对数曝光强度 (ln(1+Σ intensity), 值域 [0, +∞))
formula: "attention_index_{trk} = ln(1 + Σ_d fintech_intensity_score_{trk,d}), d ∈ (stage-21 verified ∩ fintech) 文章集, 按 (target_bank, year) 分组求和后 log1p; trk ∈ {full, ctx, ss}; 求和前 Σ 经 clip(lower=0) 非负防御; 变体 attention_index_{trk}_jJJwWW = 同式在更严两阶段去重存活集 (MinHash LSH Jaccard ≥ 0.JJ × WW 工作日窗口, keep-first) 上重算; 生产锚点 = j80w5 (即无后缀列本身)"
producer: pipeline/panel/attention_media.py::compute_attention_treatments (三轨生产锚点, runner 步骤 6b-2); pipeline/panel/dedup_sensitivity.py::compute_dedup_sensitivity_treatments (jXXwYY 去重敏感性变体, 步骤 6b-3)
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score_{full,ctx,ss} 文章级强度分子)
- 12_fintech_news_full.parquet (bank-year 全集脊柱 + MinHash 判重语料 + 媒体来源列)
- 24_herd_decay.parquet (stage-21 verified 集, restrict_to_verified (docid,target_bank) semi-join 门控)
citations:
- doi: 10.1002/mde.70100
  type: journal
  authors: Li, Y.
  year: 2026
  title: "The textual tone of annual reports and market attention: Evidence from Chinese listed companies"
  venue: Managerial and Decision Economics
- doi: "10.1016/j.iref.2024.103583"
  type: "journal"
  authors: "Zhou, W., Chen, F., Zhu, Y., Xiang, L., & Lei, L."
  year: 2024
  title: "Media attention, negative reports and textual information of banks' ESG disclosure"
  venue: "International Review of Economics & Finance"
- doi: "10.1111/jofi.70009"
  type: "journal"
  authors: "Kwan, A., Liu, Y., & Matthies, B."
  year: 2026
  title: "Institutional Investor Attention"
  venue: "The Journal of Finance"
- doi: 10.1016/j.jempfin.2025.101670
  type: journal
  authors: Chen, Z., Li, Z., Liu, J., & Liu, X.
  year: 2026
  title: "Information salience, investor attention, and stock price crash risk"
  venue: Journal of Empirical Finance
  vol: 85
  pages_or_artno: Article 101670
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
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3105-3147
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: Article 103870
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: "FinTech credit and entrepreneurial growth"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3309-3359
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
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1287/mnsc.2020.3682
  type: journal
  authors: Bellstam, G., Bhagat, S., & Cookson, J. A.
  year: 2021
  title: "A text-based analysis of corporate innovation"
  venue: Management Science
  vol: 67
  issue: 7
  pages_or_artno: 4004-4031
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: Cheng, M., & Qu, Y.
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 63
  pages_or_artno: Article 101398
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/rfs/hhy130
  type: journal
  authors: Chen, M. A., Wu, Q., & Yang, B.
  year: 2019
  title: "How valuable is FinTech innovation?"
  venue: The Review of Financial Studies
  vol: 32
  issue: 5
  pages_or_artno: 2062-2106
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
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
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
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
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: "10.1111/ajfs.12496"
  title: "Media Attention and Labor Investment Efficiency"
  authors: "Park, S., & Cho, M."
  year: 2024
  venue: "Asia-Pacific Journal of Financial Studies"
  type: "journal"
new_dois:
- "10.1016/j.iref.2024.103583"
- "10.1111/jofi.70009"
- "10.1111/ajfs.12496"
---

## CORE

以文本分析构造中国银行媒体关注度指数, 发现媒体关注度越高银行ESG信息披露文本情感越正面而可读性越低, 与本家族以曝光强度累积测量银行媒体关注的构念高度同源。 提出机构投资者关注度的新测度并检验其对资产定价与信息扩散的影响, 与本家族对媒体/投资者关注度构念的文献定位相呼应。

【构念与来源】
本家族测量银行×年份层面媒体对特定银行金融科技活动的公众关注度, 构念定位是 extensive 累积曝光强度: 一家银行在一个日历年内被多少篇经过验证的金融科技相关报道覆盖, 这些报道各自的金融科技技术含量有多高, 两者相乘再累加, 取对数后即为该银行该年的关注度指数。分析单元是 bank-year, 面板经 balance_panel 补齐为银行与年份的笛卡尔积, 生产语料覆盖 2007 至 2025 年 (T=19); 盘上开发样本仅 T=2 约两百个 bank-year, 是全量语料的极小试跑切片, 解释统计特征时须以生产规模为准而非试跑退化态。经项目 2026-06-10 metric-audit 锚点更正, 本指数的规范学术表述是 Fang 与 Peress (2009) 意义上的媒体覆盖加权曝光量: 该文以报纸是否覆盖及覆盖多少来刻画公司层面的媒体关注, 并证明覆盖本身携带横截面定价含义; 本指数把"是否覆盖"的零一计数升级为"覆盖强度"的连续累加, 属同一构念谱系的加权推广。必须与之明确区分的是 Hassan 等 (2019) 的 intensive 归一化份额范式, 后者以命中词组占文档总词组的比例度量暴露, 分子分母同文档, 天然是"密度"而非"总量"; 本家族刻意不做该归一化, 未按文章数或语料规模缩放, 因此它回答的是"这家银行该年在媒体上累积了多少金融科技曝光", 而不是"金融科技议题在该银行的媒体形象中占多大比重"。项目内与 Hassan 范式严格对齐的近邻测度是 attention_pct_full 与 attention_intensity_density 族, 分工见下文构念区分节。数据来源为本项目中文银行新闻语料: 经 stage 00 预处理与去重, stage 11/12 银行与金融科技双侧识别, stage 13 银行×金融科技邻近共现硬过滤 (只保留目标银行与至少一个金科词邻近共现的文章; 该过滤在金科自动机不可用时保留全部行并响亮告警、绝不静默清空, keep 率过低则直接失败退出), stage 14 三轨文本物化, stage 15 文章级金融科技强度打分, 最终在 panel 构建步骤 6b-2 聚合为 bank-year 指数。指数量纲为无量纲的对数曝光强度, 值域 [0, +∞), 因是对累积强度和取 log1p, 单位不可与任何份额型或密度型测度直接比大小。原始语料以报纸报道为绝对主体, 中国媒体环境下报道供给存在体制性结构 (Qin, Strömberg 与 Wu, 2018), 这既是使用媒体文本度量关注度的现实土壤, 也是解释系数时须记住的语境; 中文语料上文本测度与市场注意力的可用性有近期证据支持 (Li, 2026; Ni, 2024), 商业新闻文本承载可测经济信息的一般性证据见 Bybee 等 (2024)。本列族属论文 P2 (bank_fintech_attention) 的处理变量家族, canonical 主列为 attention_index_full, 其余十四列均为围绕它展开的稳健性轨与去重敏感性变体, 全部服从同一套 verified 门控、脊柱组装与零/NaN 契约。

【方法学与计算】
计算分三层。第一层是文章级强度分子: stage 15 (pipeline/filtering/fintech_intensity.py) 对每篇通过共现过滤的文章计算 fintech_intensity_score, 采用双重对数核公式, 对约 1,506 词金融科技词典中每个在文中命中 (词频为正) 的关键词 i, 取 (1+ln TF) 除以 (1+ln L_d) 再乘以关键词权重 W_i, 逐词累加; 对词频取对数抑制复读机式刷分, 以文档长度对数做分母抑制长文机械占优。权重 W_i 为 IDF 与语义纯度的预乘积 (W_i = IDF_i × CosSim_scaled_i): IDF 在全量参考语料上按 log10(N/(1+df)) 计算后均值归一化并 Winsorize (默认第 1 至 99 分位), 语义纯度用关键词嵌入对 IDF 加权质心的余弦相似度经 min-max 重标定得到。该"词命中×稀缺度×语义纯度"的操作化与 Kalyani 等 (2025) 用文本词组识别新兴技术并追踪其扩散的范式同源, 也与 Li 等 (2021) 和 Bellstam 等 (2021) 以词典与文本相似度构造公司级软属性测度的方法论一脉相承。分词器锁定 jieba 0.42.1 并对全部关键词做幂等注入以保证跨机确定性 (含空格或顿号的少数关键词因 jieba 天然切不出、从权重宇宙剔除并披露, 不改任何单篇 TF 命中); 命中不同关键词种数不足二次熔断阈值 (min_distinct_keywords_jieba, 默认 2) 的文章其 score 置 NaN 且 intensity_verified 置伪, 在下游 bank-year 求和中自动剔除, 避免把未验证文章当零强度系统性拉低。关于嵌入: 强度权重的语义纯度因子在 stage 15 由 co-primary 双轨嵌入构造 — canonical 无后缀槽 Qwen/Qwen3-Embedding-8B (4096 维) 与 _lg 槽 text-embedding-3-large (3072 维), 两轨各把词表编码一遍、各构一套权重, 同为主测度、互为稳健性、严格 parity, 任一嵌入硬失败 (embed_texts 返回 None) 则该 spec 的 fintech_intensity_score 三轨列 both-or-neither 同置 NaN、绝不留单边孤儿; 质心与余弦数学全程维度无关。须精确界定的是: 本 attention_index 家族只消费 MAIN (Qwen 无后缀) 轨的强度分作分子, 因此家族自身没有 _lg 孪生列 — co-primary 的 both-or-neither parity 与禁混 Hansen J 铁律作用在 stage 15 的 intensity 层, attention_index 经 MAIN 轨继承其语义纯度权重。第二层是 verified 域门控与 bank-year 聚合: 分子帧 15_fintech_intensity 经 restrict_to_verified 以 (docid, target_bank) semi-join 收敛到 stage-21 LLM 验证集 (24_herd_decay 落盘), 剔除被三家 LLM 投票判伪的非真实银行金融科技报道 (剔除比例以生产日志与审计文档为准); 留篇门控自 2026-06-29 起为 full-only 口径, 即一篇文章是否算"银行金融科技报道"只看 llm_verified_full 是否为真, ctx 与 ss 轨为 conditional-on-full 的子集测度轨。门控后按 (target_bank, year) 分组对三轨强度分各自求和得 sum_full、sum_ctx、sum_ss。第三层是全集脊柱组装与变换: bank-year 全集脊柱取自 12_fintech_news_full 全部银行新闻 (含非金融科技, 刻意不门控, 因非金融科技行从不经 stage 21 验证、物理上不可门控, 且这是 Fang-Peress 式关注度的合法分母域), 在该脊柱上 LEFT-join 分子, 缺失的 sum 填 0 表示真零曝光, 随后 clip(lower=0) 做非负防御 (IDF 在极端文档频率下理论可为负、会经求和传染出 log1p 负输入, clip 是结构性保证, 对当前非负数据为 no-op), 最终取 ln(1+Σ) 得 attention_index_{full,ctx,ss}, 值域 [0, +∞)。对数变换应对媒体关注典型的右偏重尾分布。NaN 与零的非对称契约是本族刻意设计: 若某 bank-year 完全没有任何银行新闻 (不在 12_full 全集), LEFT-join 天然得 NaN, 语义是"关注度不可测"; 若有银行新闻但零篇验证金融科技报道, 指数为 0, 语义是"真零曝光"。回归中前者 listwise 删除、后者作为信息性零保留, 两者绝不混淆。产后校验 _validate_attention_treatments 断言三轨指数下界为 0。此外, 步骤内另对每个平衡媒体窗口的平衡子集计算 full 轨语调分布诊断 (只读已并入 panel 的列、结果丢弃), 供审稿与非平衡基准对照判断幸存者偏差是否驱动结论, 属 golden-safe 的日志富集而非新列。确定性方面: jieba 分词器版本冻结、关键词嵌入经 LLMCache 以模型标识加文本加版本为键穿透, 三轨全命中时可在离线守卫下字节级复现, 换嵌入模型或改测度类改动的 golden 零漂移须在生产语料机受控重生并披露厂商与维度变更的数值副作用 (n_articles、fintech_share、attention_pct 收缩均非缺陷)。去重敏感性变体列 (j 后缀十二列) 由步骤 6b-3 (dedup_sensitivity.py) 生产: 生产语料已在 stage 00 按 MinHash LSH Jaccard 0.80 加 5 工作日窗口保留首发去重, 该模块在 12_full 文章全集上复用一次计算、参数无关的 MinHash 签名, 按更严参数网格 {j70w5, j75w5, j80w10, j70w10} 追加判重, 对每个变体的存活集镜像生产锚点口径重算三轨指数 (同样 verified 门控分子、变体内全集脊柱、零填充、clip、log1p), 生产锚点 j80w5 即无后缀列本身。单调性不变量为变体存活篇数不超过生产存活篇数, 违反即报错。

【文献定位】
本家族站在三支文献的交汇点。第一支是媒体与金融市场文献: Tetlock (2007) 开创性地把媒体文本内容引入资产定价, Fang 与 Peress (2009) 确立媒体覆盖量的横截面定价效应并成为本指数的构念主锚, Engelberg 与 Parsons (2011) 与 Peress (2014) 分别用地方媒体覆盖差异与报纸罢工的准实验证明媒体报道对交易与价格扩散有因果作用而非纯粹镜像, Cookson 等 (2024) 进一步区分社交媒体信号与传统新闻的信息含量, Gutknecht (2025) 证明负面议题的媒体覆盖对公司股权风险有独立解释力, Bybee 等 (2024) 则以大规模商业新闻文本刻画宏观状态、佐证新闻语料承载可测量的经济信息。这支文献共同确立了"媒体覆盖是值得测量的独立经济变量"。第二支是投资者注意力文献: Da, Engelberg 与 Gao (2011) 用搜索量构造直接注意力代理, 是本指数的对照锚 — 媒体覆盖是注意力的供给侧, 搜索是需求侧, 两者相关但不可互替; Chen 等 (2026) 表明信息显著性驱动的注意力配置影响崩盘风险, Li (2026) 在中国上市公司语料上连接文本语调与市场注意力。以媒体报道量构造公司层面的媒体关注度测度,发现媒体关注度提升会通过过度雇佣或滞后解雇降低企业劳动投资效率,与本家族以曝光量刻度累积关注度的构念思路同源, 引用格式 Park, S., & Cho, M. (2024, Asia-Pacific Journal of Financial Studies)。第三支是 text-as-data 的公司级暴露测度范式: Gentzkow, Kelly 与 Taddy (2019) 给出方法论总纲, Hassan 等 (2019) 的政治风险份额、Sautner 等 (2023) 的气候暴露、Hassan 等 (2023) 的疫情暴露构成 intensive 归一化谱系, Kalyani 等 (2025) 的技术扩散测度则最接近本指数"词命中即技术关注"的操作化, Li 等 (2021) 与 Bellstam 等 (2021) 展示词典与文本相似度如何构造可验证的公司级软属性。应用语境上, 银行金融科技转型的经济后果由 Chen, Wu 与 Yang (2019)、Hau 等 (2024) 与中国场景下的 Cheng 与 Qu (2020) 提供实证基准, 本指数即为在该问题上做媒体视角识别的处理变量; 中国媒体供给的政策性结构由 Qin, Strömberg 与 Wu (2018) 记录, 是本语料生成过程的重要背景。

【识别策略定位】
attention_index_full 是论文 P2 (bank_fintech_attention) paper_spec 钦定的 treatment 主列, 结果变量为银行金融科技投入 (ln_fintech_investment, 外部财务面板接入时构造), 基准设定为银行与年份双向固定效应下的面板回归。把该识别的内生性拆成三条互不相同的通道, 有助于对号入座地评估各自的补救手段而非笼统地"上工具变量"。第一条是双向因果与同时性: 媒体覆盖既可能驱动银行的金融科技投入, 也可能只是银行既有战略被动引发的报道镜像, Engelberg 与 Parsons (2011) 正是以地方媒体覆盖差异这一准实验辨析媒体的因果作用与纯粹镜像之别, 确立"覆盖并非战略的被动倒影"这一识别前提。第二条是遗漏变量: 银行规模、上市地位、总部所在地的媒体密度等因素可能同时驱动覆盖量与投入, 中国语境下还叠加媒体供给的政策性结构 (Qin, Strömberg 与 Wu, 2018), 若不吸收会污染系数。第三条是测量误差: 覆盖强度的操作化涉及去重口径、归因窗口、词典与嵌入权重等多个研究者自由度, 会以经典 (向零衰减) 或非经典形式扭曲系数。前两条通道由工具变量应对, 第三条由本家族两条稳健性梯子直接约束, 二者分工不可混淆 — 这是本条目最须强调的一点, 因为把梯子当 IV 或把 IV 当稳健性都会破坏识别叙事。项目在面板层配备三引擎 IV 扩展, 每一引擎各自锚定一支识别文献: 同组 leave-one-out 同伴均值 IV (leave_one_out_peer_*_iv) 以同组其他银行的媒体暴露作外生变动, 其识别前提可追溯到 Manski (1993) 对同伴效应中反射问题 (个体与群体互为因果导致联立不可识别) 的经典刻画, 以及 Bramoullé, Djebbari 与 Fortin (2009) 经社会网络结构识别同伴效应的思路 — 留一构造正是为绕开自身对自身的反射性联立而设。广义 Bartik 暴露 IV (bartik_*_iv) 以份额乘冲击的移位份额 (shift-share) 结构生成外生变动, 方法学依据为 Goldsmith-Pinkham, Sorkin 与 Swift (2020) 对 Bartik 工具识别假设 (外生性落在份额还是冲击) 的解构, 以及 Borusyak, Hull 与 Jaravel (2022) 的准实验移位份额设计。媒体来源 house-style 暴露 IV (outlet_*_iv) 以银行所接触媒体来源的固有报道风格作供给侧外生变动, 思路上呼应 Peress (2014) 用报纸罢工这一外生供给冲击隔离媒体效应的策略。三引擎生成的 IV 列族供各 2SLS 模板消费, 分别应对同时性与遗漏变量两条通道。
稳健性维度上本家族提供两条正交梯子, 二者共同刻画本 extensive 测度在测量误差通道上的两个主要研究者自由度。其一是三轨文本梯子 (full/ctx/ss), 固定留篇文章集、只变动金融科技强度的归因窗口, 检验"强度归因口径是否稳健"; 其二是去重参数梯子 (j70w5/j75w5/j80w10/j70w10 对照生产锚点 j80w5), 固定归因口径、只变动存活文章集, 检验"关注度水平是否被转载虚增所驱动"。两条梯子服从同一条口径铁律: 各臂互为稳健性、不分主次, 每臂各自 just-identified 并排进入独立回归, 严禁把不同轨或不同去重变体混进同一个 over-identified 设定去跑 Hansen J — 它们是同一构念的替代测量而非互相独立的工具变量, 混用会把测量误差伪装成过度识别检验的通过, 是识别层面的实质性错误而非风格问题。喂入强度权重的 co-primary 双轨嵌入 (语义纯度层, 作用在 stage 15 intensity 而非本家族列) 同受此铁律约束: Qwen 无后缀轨与 text-embedding-3-large (_lg) 轨严格 parity、各自 just-identified、禁混同一 over-identified Hansen J。两条梯子在设计上正交互补: 三轨梯子固定文章集、变动归因窗口, 去重梯子固定归因口径、变动存活文章集, 二者不交叉, 恰好覆盖 extensive 关注度构念的两类主要自由度; 而 verified 留篇门控因是 full-only 单一口径 (2026-06-29)、不随轨道或去重参数变化, 不额外贡献自由度, 故刻意不设为第三条梯子。text-as-data 测度的整体构造效度与识别方法论依据见 Gentzkow, Kelly 与 Taddy (2019) 的总纲。多重检验层面, 去重与轨道变体属规格稳健性并排, 论文以系数符号与显著性跨臂稳定性为证据形态, 不以面板内变体间相关性充当稳健性证明 (低剔除率下该相关性接近平凡, 见 dedup_sensitivity 模块 METHOD-3 披露); 真正的跨模型族级 FWER 校正另由根级 rwolf 模板承担, 与本家族的规格稳健性并排是两套不同的证据形态, 不可互相替代。

【与相邻测度的构念区分】
同函数产出的近邻列须严格分工, 不可混用, 而最容易被误当同义的是 attention_index 与 attention_intensity_density: 两者消费同一个分子 (逐轨强度和 Σ intensity), 差别只在变换与分母 —— 本指数取 log1p(Σ) 得对数化的累积总量, 密度族则以 Σ 除以全部银行新闻篇数 N_all 得每篇平均强度。这一个除法把构念从"这家银行该年在媒体上累积了多少金融科技曝光"(extensive 总量) 翻转为"金融科技议题在该银行的媒体形象中占多重"(intensive 密度), 两者回答的是相反的问题, 因此绝不能因分子同源就替换或并入同一设定。attention_pct_full 是议程份额 (验证金融科技篇数除以全部银行新闻篇数), 属 Hassan 等 (2019) 式 intensive 口径, 分子分母同基, 对去重参数部分免疫但非完全免疫 (分子分母各自受去重影响, 部分相消而非零敏感); attention_intensity_density_{full,ctx,ss} 同属 intensive 谱系。若研究问题是"金融科技在银行媒体形象中的相对权重", 应以 pct 与 density 两族为主而非本指数; 若研究问题是"这家银行该年被金融科技报道覆盖的绝对规模", 才用本指数。attention_disp_full 是跨媒体来源 HHI 集中度 (高值代表报道集中于少数媒体, 因是集中度而非分散度, 勿按 dispersion 字面反向解读符号), attention_intensity_sd_{full,ctx,ss} 是篇间强度二阶矩 (N<2 → NaN), 两者度量报道的分布结构而非总量, 与本指数正交。attention_gap_full_ctx 与 attention_attr_share 锚定 full 与 ctx 的归因对照 (前者为 mean(full−ctx) 归因借位, 后者为 Σctx/(Σctx+Σfull) 有界归因占比, 由旧的 clip(Σctx/Σfull,0,1) 修订而来以消除右删失), 两者刻意只锚定 full/ctx 归因窗口对照、不产 ss 孪生。n_fintech_articles 是未加权 extensive 计数, 即本指数把每篇强度权重全部置一后的退化形态, 二者同为 extensive 但一个计"篇数"、一个计"强度加权曝光", 强度权重是否携带增量信息正可由两列对照检验。地理注意力指数族 (ft_attn_yr/prov/city 比值 + ft_vol_* 总量孪生, 由 compute_fintech_attention_index 另行产出、受最低文章数阈值 _ATTN_MIN_ARTICLES=5 约束、且比值与总量两测度亦互为稳健性不分主次) 度量地理单元而非银行个体的关注度, 与本家族仅共享上游语料、构念层级不同, 勿混; 其内部 ft_attn (比值/intensive) 与 ft_vol (总量/extensive) 的对照恰是本家族 pct 与 index 对照在地理维度的镜像。特别注意 nf_media_breadth (falsification/controls.py): 它度量传播广度, 构念上转载本身就是信号, 因此刻意建立在去重之前的物理行集上; 本指数度量信息到达, 通稿与转载不携带新信息, 因此建立在去重后语料上 — 一条新闻被五十家网站转载, 测"发生了多少事"只能算一件, 测"传得多广"恰恰要数五十次, 两套口径并存是分工而非矛盾, 且本家族的去重参数梯子正是对"信息到达"口径下去重严格度的敏感性检验、与 breadth 的"越多越真"口径方向相反。与 fintech_share 的区别在分母来源与门控口径, 详见该家族条目。

【已知局限与稳健性梯子】
第一, extensive 总量构念天然对预处理夹层敏感: 水平大小随去重参数 (Jaccard 阈值与时间窗口) 变动, 这正是本家族物化十二个 j 变体列的动因; 论文须披露去重规则与剔除比例, 并以变体系数的符号与显著性稳定性作为证据。另须记住 log1p 变换虽压缩右偏重尾, 却也把绝对总量差异非线性地压扁, 故本指数的系数量纲是"对数曝光"而非"曝光篇数", 边际解释须相应措辞。第二, 去重敏感性只能向更严格方向扰动: 生产去重已把被判重文章永久剔除, 宽松方向 (更高阈值、更短窗口) 需从原始语料重跑 stage 00, 本模块不做并在论文中如实披露 —— 这意味着本家族只能回答"去重更狠时结论是否稳", 无法回答"去重更松时会怎样"。第三, 两阶段近似的口径限定 (METHOD-1): 在已去重产物上叠加更严去重, 其存活集不严格等于在原始语料上直接按严参数去重的存活集 —— 时间窗口判重是 keep-greedy 贪心, 低阈值下的 LSH 簇是高阈值簇的超集, 个别文档可能在生产小簇中被删而在假想的 raw-direct 大簇中因锚点更早或超窗反而存活, 已删者不可复活; 故变体结果应表述为"生产去重之上施加更严扰动的保守下界", 而非"等价于从头重导", sidecar 落 two_stage_approximation 标记供 Stata 表脚注引用。第四, 跨语料盲区 (METHOD-2): 生产去重在银行/金融科技分类之前的全语料上做, 变体重判重只在银行新闻子集上做, 银行新闻与非银行新闻之间的跨子集近似重复不可见, 会系统性低估 raw-direct 严格去重的剔除量, 属对关注度构念的有意范围限定。第五, verified 门控依赖 stage 21 三家 LLM (gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash) 多数投票的判真质量, 门控剔除比例以生产日志与审计文档为准; 该门控是留篇层面的 full-only 单一口径, ctx 与 ss 轨作为 conditional-on-full 子测度共享由 full 轨定义的留篇集, 因此三轨共用同一套留篇选择、不随轨道变化, 门控本身不构成额外的研究者自由度, 但也意味着 full 轨判真的任何系统性偏差会同步传染三轨, 不能靠轨道对照检出。第六, 词典与权重的时代漂移: 金融科技词汇随技术演化, IDF 与语义纯度在冻结词典 (jieba 0.42.1, 词表冻结) 上计算, 跨十九年语料的语义漂移只能靠三轨与 co-primary 嵌入双轨稳健性间接约束, 无法完全消除。第七, 结构性非负防御 (clip(lower=0)) 是对上游 IDF 在极端文档频率下理论转负、经求和传染出 log1p 负输入的保护, 对当前非负数据为 no-op, 但一旦生产语料出现负强度, 该 clip 会静默吸收而非报错, 需配合 stage 15 的分布诊断监控。第八, NaN 与零的非对称契约是刻意设计而非缺陷, 但它对下游使用者构成一条硬约束: 用 0 填补 NaN 会把"该年完全无银行新闻"的不可测状态污染成"真零曝光", 系统性拉低无覆盖银行的测量值, 回归中前者必须 listwise 删除、后者必须保留。第九, T=2 开发样本上 ss 轨与部分变体可能出现零方差或全 NaN 的预期退化, 生产 T=19 语料下正常; 试跑样本变体仅追加剔除极小比例文章, 其与生产锚点的相关性接近 1.0 是低剔除率下的平凡结果 (METHOD-3), 不可外推为强稳健性证据 —— 真正的稳健性证据是把每个变体列丢进主回归看系数稳定性, 而非面板内相关性。所有梯子臂 (三轨、四去重变体、intensity 层 co-primary 双嵌入) 一律各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J, 这一铁律在本家族每一列的用法中无例外。

## VAR: attention_index_ctx

【变体差分】
本列是家族 canonical (attention_index_full) 的 ctx 轨孪生, 计算式、verified 门控、全集脊柱、零与 NaN 契约、非负防御与 log1p 变换全部与 full 轨逐字相同, 唯一差异是强度分子换为 fintech_intensity_score_ctx, 即在 stage 14 物化的 content_ctx 文本 (prepend 标题加目标银行实体窗口文本) 上重算的双重对数核强度分。构念含义: full 轨在全文上数金融科技词命中, 一篇同时报道多家银行或以其他主体为主角的文章, 其金融科技强度会被整篇归入目标银行; ctx 轨把计数窗口收缩到目标银行实体出现位置的邻域, 只统计与该银行语境相邻的词命中, 从而剔除同篇内其他主体贡献的错误归因, 是归因更保守的测量臂。代价是窗口截断可能漏掉确属该银行但距实体较远的段落, 且 ctx 文本更短, 文长归一化 (分母 1+ln L_d) 后密度分布与 full 不同, 两轨水平不可直接比大小。行宇宙口径: 留篇门控为 full-only (2026-06-29 口径), ctx 轨是 conditional-on-full 的测度轨, 即哪些文章算"银行金融科技报道"由 full 轨判定, ctx 只改变这些文章的强度度量。产后校验层面, 本列与 full、ss 轨同批接受 _validate_attention_treatments 的下界断言 (值域 [0, +∞)) 监控, 列全为 NaN 时响亮告警而非静默通过; 聚合时 ctx 轨强度与 full 轨同处经 restrict_to_verified 门控的同一 s14 帧, 不存在两轨分子域漂移的可能。T=2 开发切片上本列与 full 高度同向属预期, 生产 T=19 语料上两轨的分歧才携带归因信息。用法: 作为 attention_index_full 的稳健性臂单独替换主列复跑回归, 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁与 full 或 ss 混进同一 over-identified Hansen J, 也不与 full 同进一个 RHS。

## VAR: attention_index_ctx_j70w10

【变体差分】
本列是 ctx 轨指数在去重参数梯子最严端点上的重算: 在生产去重 (Jaccard 0.80 × 5 工作日) 之上, 以 Jaccard 阈值 0.70 且 10 个工作日窗口的双向最严格参数追加 MinHash 判重, 对存活文章集按与生产锚点完全相同的口径 (verified 门控分子 s14、变体内全集脊柱、零填充、clip 非负、log1p) 重算 ctx 轨累积曝光。阈值从 0.80 降到 0.70 意味着相似度七成的文本对即被视为转载合并, 窗口从 5 拉长到 10 个工作日意味着迟发两周的换皮通稿也被捕获, 两把刀同时拧紧, 是四变体中剔除最多、对"转载虚增关注度"最不宽容的臂, 充当梯子的保守极值点。存活集服从单调性不变量 (不超过生产存活集), 分子等于 verified 与变体存活者的交集, 分母与脊柱取变体内全部银行新闻。契约与主列镜像: 变体全集内零金融科技 bank-year 得 0, 失去全部银行新闻的 bank-year 得 NaN。注意两阶段近似口径: 本列是"生产去重之上更严扰动的保守下界", keep-greedy 窗口判重下不等价于从原始语料直接按 0.70/10 去重, 且跨语料盲区使跨子集近似重复不可见。用法: 单独替换 attention_index_ctx 复跑回归看系数稳定性; 各去重变体与生产锚点互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J, 也不与其他臂同进一个 RHS。

## VAR: attention_index_ctx_j70w5

【变体差分】
本列是 ctx 轨指数的去重敏感性变体之一, 参数为 Jaccard 阈值 0.70 × 5 工作日窗口: 相对生产锚点 j80w5 只拧低相似度阈值 (0.80 到 0.70)、保持时间窗口不动, 属"单独扰动阈值维度"的受控臂。其针对的转载形态是同期发出但经过改写的稿件 — 标题微调、段落增删、媒体署名替换的通稿变体, 在 0.80 阈值下可能逃过判重, 在 0.70 下被合并剔除。与 j75w5 一起构成阈值维度的剂量梯度, 与 j80w10 (只扰动窗口) 正交, 便于在结果表中分解"结论对哪个去重参数更敏感"。计算口径与主列完全镜像: MinHash 签名一次计算、参数无关、变体间复用, 存活集上分子经 stage-21 verified 门控 (full-only 留篇口径), 变体内全集脊柱 LEFT-join, 零金融科技 bank-year 填 0 为真零曝光, 无银行新闻 bank-year 为 NaN, sum 先 clip 非负再 log1p, 值域 [0, +∞)。本列继承 ctx 轨的归因语义: 强度只统计目标银行实体窗口邻域内的金融科技词命中, 因此同一批改写转载的剔除, 在 ctx 轨累积和上的相对扰动幅度不一定与 full 轨一致, 须与 full 轨同参数臂并排解读。两阶段近似 (保守下界) 与跨语料盲区两条口径限定同样适用。用法: 替换 attention_index_ctx 单独复跑, 与其余变体各自 just-identified 并排、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J 或与其他臂同进一个 RHS。

## VAR: attention_index_ctx_j75w5

【变体差分】
本列是 ctx 轨指数在 Jaccard 阈值 0.75 × 5 工作日参数下的去重敏感性变体, 是阈值维度梯子的中间档: 生产锚点 0.80 与激进臂 0.70 之间的内插点, 窗口维度保持生产值不动。设置中间档的价值在于剂量反应检验 — 若结论随去重严格程度单调平滑变化, 三点 (0.80, 0.75, 0.70) 应给出有序的系数序列; 若 0.75 处出现跳变, 则提示相似度落在 0.75 到 0.80 区间的那批准转载文章对结果有集中杠杆, 值得单独审视再下稳健性结论。这种三点剂量设计比单一极值对照更能说服审稿人"结论不是靠去重参数凑出来的"。除去重参数外, 本列与 attention_index_ctx 的计算完全镜像: 在变体存活集上以 (target_bank, year) 分组对 fintech_intensity_score_ctx 求和 (分子先经 (docid, target_bank) semi-join 收敛到 stage-21 verified 集, 留篇门控为 full-only 口径), 变体内全集脊柱上 LEFT-join, 缺失和填 0 表真零曝光, clip 非负后 log1p, 值域 [0, +∞); 完全无银行新闻的 bank-year 为 NaN。ctx 轨语义 (实体窗口归因) 与两阶段近似口径 (保守下界, 非 raw-direct 等价) 均继承, 存活集亦服从单调不变量; 变体另落 sidecar 存活率诊断与 two_stage_approximation 标记供 Stata 表脚注引用, 注意 sidecar 的存活率是全 docid 域诊断, 与本列分子的 verified 交存活域不同, 勿混读。用法: 作为独立稳健性臂替换同轨主列复跑, 与生产锚点及其余三变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 报告时与同轨其余臂并列成敏感性表格。

## VAR: attention_index_ctx_j80w10

【变体差分】
本列是 ctx 轨指数在 Jaccard 阈值 0.80 × 10 工作日参数下的去重敏感性变体: 相对生产锚点 j80w5 保持相似度阈值不动、单独把转载判定窗口从 5 个工作日拉长到 10 个, 属"单独扰动时间维度"的受控臂, 与 j70w5/j75w5 (只动阈值) 构成正交分解。其针对的转载形态是高保真但迟发的复制 — 周报月刊的滞后转载、节假日积压后的批量重发、跨地区媒体的周期性摘编, 这类文章与首发稿相似度很高 (0.80 阈值本就能匹配) 但落在 5 个工作日窗口之外而在生产口径下存活; 拉长窗口把它们捕获剔除。若本列系数与主列显著偏离而 j70w5 不偏离, 则说明结论对迟发转载敏感而非对改写转载敏感, 这一诊断信息是设置双维度网格的直接回报。计算口径与同轨主列逐点镜像: 参数无关的 MinHash 签名复用、verified 门控分子 (full-only 留篇口径)、变体内全集脊柱、真零曝光填 0、无银行新闻 NaN、clip 非负、log1p 变换、存活集单调不变量; ctx 轨的实体窗口归因语义与两阶段近似的保守下界口径全部继承。同批另落 n_ft_articles_j80w10 与 n_all_articles_j80w10 两列水平计数供披露, 分子域为 verified 与变体存活的交集、分母域为变体内全部银行新闻, 两域口径不同勿混读; 变体网格本身可经 config/panel.yaml 的 panel_building.dedup_sensitivity.variants 键覆盖。用法: 单独替换 attention_index_ctx 复跑回归, 与其余去重臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: attention_index_full

【变体差分】
本列是家族 canonical 与论文 P2 (bank_fintech_attention) paper_spec 钦定的 treatment 主列, 是全家族十五列的锚点: 其余十四列 (两条稳健轨与十二个去重变体) 的语义均以"区别于本列什么"来定义。轨道语义: full 轨文本等于 prepend 标题加全文正文 (stage 14 物化的 content_full, 原始内容列不动), 强度分子 fintech_intensity_score_full 在整篇文章上统计金融科技词典命中, 经 IDF 与语义纯度加权、双重对数核抑制长文与复读偏差后逐词累加; 这是三轨中覆盖最完整、不做任何归因窗口截断的测量, 代表"该文章携带的全部金融科技信息量都记入目标银行"的宽归因假设。留篇门控与本列同轨: 2026-06-29 起项目采用 full-only 口径, 一篇文章是否算"银行金融科技报道"只看 llm_verified_full 是否为真, 因此本列既是构念主列也是行宇宙的定义轨, ctx 与 ss 是它的 conditional-on-full 子测度 — 这一非对称使本列在所有回归里承担定义留篇集的额外角色, 而非仅仅一条并列轨。聚合口径: 在 stage-21 verified 集 (经 (docid, target_bank) semi-join 门控) 上按 (target_bank, year) 对 fintech_intensity_score_full 求和, 在 12_fintech_news_full 全部银行新闻定义的 bank-year 全集脊柱上 LEFT-join, 缺失和填 0, clip 非负后取 ln(1+Σ), 值域 [0, +∞)。对数变换是本列可用性的关键: 媒体关注呈典型右偏重尾, 少数明星银行年份贡献极端累积强度, 原始和直接进回归会被尾部支配, log1p 在保留零值语义 (真零曝光映射到 0) 的同时压缩尾部。NaN 与零的非对称契约务必在使用中保持: 值为 0 的 bank-year 是"有银行新闻但零篇验证金融科技报道"的信息性零, 应保留; 值为 NaN 的 bank-year 是"该年完全无银行新闻"的不可测状态, listwise 删除是正确处理, 用 0 填补 NaN 会把不可测污染成假零曝光, 系统性拉低无覆盖银行的测量值。构念定位: 本列是 Fang 与 Peress (2009) 式 extensive 覆盖加权曝光, 刻意未按文章数归一化, 与 Hassan 等 (2019) 式 intensive 份额 (attention_pct_full、attention_intensity_density_full) 构念分工, 论文表述时不得混称; 与 Da, Engelberg 与 Gao (2011) 的搜索注意力属供给与需求两侧, 引用时注意方向。嵌入口径须精确: 本列强度权重的语义纯度因子来自 stage 15 的 canonical Qwen (MAIN, 无后缀) 嵌入轨; 该 intensity 层另有 co-primary 的 text-embedding-3-large (_lg) 孪生并遵 both-or-neither parity, 但本 attention_index 家族只消费 MAIN 轨、无 _lg 孪生列, co-primary 的禁混 Hansen J 铁律作用在 intensity 层。计量用法: 作为 P2 主回归的 treatment primary 进入银行与年份双向固定效应设定, 系数量纲是"对数曝光"而非"曝光篇数" (log1p 变换所致), 边际解释须相应措辞。内生性由项目三引擎 IV 扩展与去重及三轨敏感性梯子分工约束: 同组 leave-one-out 同伴均值 IV 应对同伴联立, 其识别前提追溯到 Manski (1993) 的反射问题与 Bramoullé, Djebbari 与 Fortin (2009) 经网络识别同伴效应; 广义 Bartik 暴露 IV 依 Goldsmith-Pinkham, Sorkin 与 Swift (2020) 与 Borusyak, Hull 与 Jaravel (2022) 的移位份额识别; outlet house-style 暴露 IV 呼应 Peress (2014) 的外生供给冲击。内生性辨析另可对照 Engelberg 与 Parsons (2011) 的因果媒体效应, 与 Peress (2014) 共同支撑"覆盖非纯粹镜像"的识别前提。须再次强调 IV 应对同时性与遗漏变量两条通道、梯子应对测量误差通道, 两类手段分工不可互相顶替。本列与 attention_pct_full 高度同向但构念不同 (前者 extensive 总量、后者 intensive 份额), 两者各进自回归、不同进一个 RHS; 与 attention_intensity_density_full、attention_disp_full、attention_intensity_sd_full 亦为构念分工而非替代, 混入同一设定会破坏构念一致性。生产端本列由 compute_attention_treatments 在 runner 步骤 6b-2 落盘, 是 _validate_attention_treatments 值域断言 (下界 0) 与产后分布诊断 (含与 attention_pct_full 同向性相关) 的首要监控对象。稳健性铁律: 本列对 ctx/ss 轨、对四个 j 去重变体、对 intensity 层 co-primary 双嵌入, 全部是互为稳健性、不分主次的并排关系, 每臂各自 just-identified, 严禁任意两臂混进同一 over-identified Hansen J; 十二个去重变体在敏感性表中逐一替换本列复跑, 以系数符号与显著性的跨臂稳定性作为对去重参数选择稳健的证据形态, 而非以面板内相关性充数。

## VAR: attention_index_full_j70w10

【变体差分】
本列是 canonical 主列 attention_index_full 在去重参数梯子最严端点的重算, 参数 Jaccard 0.70 × 10 工作日, 阈值与窗口双向同时拧紧, 是四个变体中追加剔除最多的保守极值臂。它回答审稿人对主列最尖锐的质疑: 生产去重的 0.80 与 5 工作日是研究者选择, 若把改写容忍度与迟发容忍度同时推到网格上限, 主回归结论是否翻转。构造上, 在 12_full 文章全集上复用一次计算、参数无关的 MinHash 签名按严参数追加判重, 存活集 (单调不变量: 不超过生产存活集) 内以生产锚点完全相同的口径重算: fintech_intensity_score_full 分子经 stage-21 verified 门控 (full-only 留篇口径), 变体内全集脊柱 LEFT-join, 零金融科技 bank-year 填 0 (真零曝光), 失去全部银行新闻的 bank-year 为 NaN (不可测), sum 先 clip 非负再 log1p, 值域 [0, +∞)。口径限定须随列披露: 其一, 本列是"生产去重之上更严两阶段扰动的保守下界", keep-greedy 窗口判重下不严格等价于从原始语料直接按 0.70/10 去重; 其二, 变体重判重只在银行新闻子集上做, 跨子集近似重复不可见。因是主列的孪生, 本列在去重敏感性表 (Table A 形态) 中通常列于最右端作最严参照。用法: 单独替换 attention_index_full 复跑主回归, 与生产锚点及其余变体互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: attention_index_full_j70w5

【变体差分】
本列是 canonical 主列在 Jaccard 阈值 0.70 × 5 工作日参数下的去重敏感性变体: 保持转载判定窗口为生产值 5 个工作日不动, 单独把相似度阈值从 0.80 拧低到 0.70, 是阈值维度的激进端。降低阈值意味着更宽松的"算作转载"标准 — 相似度七成的文章对即被合并, 主要捕获经过实质性改写的通稿衍生稿: 换标题、调段序、增删导语的准转载在 0.80 下常以独立文章身份存活并虚增累积曝光, 本变体把这类文章剔除后重算, 若主列系数在本臂下保持符号与显著性, 即证明结论不依赖"把改写转载当独立报道"的测量宽容。与 j75w5 构成阈值剂量梯度, 与 j80w10 (纯窗口扰动) 正交, 与 j70w10 (双向极值) 呈嵌套关系, 四臂合成完整的参数敏感性网格; 本臂与同轨中间档 j75w5、生产锚点无后缀列一起构成 full 轨 (0.80, 0.75, 0.70) 三点剂量序列, 供判读去重严格度对系数的剂量反应。计算细节与主列逐点镜像: MinHash 签名复用、存活集单调不变量、verified 门控分子 (full-only 留篇口径)、变体内脊柱、真零填 0、无新闻 NaN、clip 非负、log1p 变换; 两阶段近似 (保守下界) 与跨语料盲区两条披露义务继承。用法: 单独替换 attention_index_full 复跑, 与其余臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J, 不与任何其他臂同进一个 RHS。

## VAR: attention_index_full_j75w5

【变体差分】
本列是 canonical 主列在 Jaccard 阈值 0.75 × 5 工作日参数下的去重敏感性变体, 承担阈值梯子中间档的剂量反应功能: 生产锚点 0.80 与激进臂 0.70 之间的内插点, 窗口维持生产值。其独立价值在于区分两种敏感性形态 — 若 attention_index_full 的回归系数沿 0.80、0.75、0.70 三点单调平滑移动, 说明去重参数的影响是连续可控的测量噪声; 若在 0.75 处出现非单调跳变, 则提示相似度落在 0.75 到 0.80 区间的那批边缘转载文章对特定银行年份有集中杠杆, 应回查该批文章的分布再下稳健性结论。这种三点剂量设计比单一极值对照更能说服审稿人"结论不是靠去重参数凑出来的"。计算口径与主列完全镜像: 在一次计算、参数无关的 MinHash 签名上按 0.75/5 追加判重, 存活集内 fintech_intensity_score_full 分子经 stage-21 verified 门控 (full-only 留篇口径) 后按 (target_bank, year) 求和, 变体内全集脊柱 LEFT-join, 零金融科技填 0 为真零曝光, 失去全部银行新闻为 NaN, clip 非负后 log1p, 值域 [0, +∞); 存活集服从单调不变量, 两阶段近似的保守下界口径与跨语料盲区限定随列披露。同批落盘的 n_ft_articles_j75w5 与 n_all_articles_j75w5 水平计数列供审稿披露分子分母的实际规模, 分子域为 verified 与变体存活的交集、分母域为变体内全部银行新闻, 两域不可混读。用法: 单独替换主列复跑回归, 与其余去重臂及生产锚点互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: attention_index_full_j80w10

【变体差分】
本列是 canonical 主列在 Jaccard 阈值 0.80 × 10 工作日参数下的去重敏感性变体: 相似度阈值维持生产值不动, 单独把时间窗口从 5 个工作日拉长一倍到 10 个, 是时间维度的独立扰动臂。其针对的测量威胁与阈值臂不同: 高保真迟发转载 — 相似度足以在 0.80 下匹配, 但发布日期落在首发后第 6 至第 10 个工作日的稿件, 典型如周刊摘编、地方媒体的滞后跟进、门户网站的批量补录, 这类文章在生产口径下以独立报道身份计入累积曝光。若银行金融科技新闻的转载周期系统性长于 5 个工作日, 生产口径会高估关注度且高估幅度可能与银行知名度相关 (大银行的稿件被更持久地转载), 形成与结果变量相关的测量误差; 本变体把窗口拉长后重算, 系数稳定即排除该威胁。与 j70w5/j75w5 (纯阈值扰动) 正交, 合成双维度敏感性网格的窗口边。计算口径与主列逐点镜像: MinHash 签名复用、追加判重、存活集单调不变量、verified 门控分子 (full-only 留篇口径)、变体内全集脊柱、真零填 0、无银行新闻 NaN、clip 非负、log1p; 两阶段近似保守下界与跨语料盲区披露继承。用法: 单独替换 attention_index_full 复跑, 与其余臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: attention_index_ss

【变体差分】
本列是家族 canonical 的 ss 轨孪生, 强度分子换为 fintech_intensity_score_ss, 即在 content_ss 文本上重算的强度分。ss 轨是三轨中归因判据最严格的一轨: content_ss 等于 prepend 标题加"目标银行与金融科技词出现在同一句及其前后一句窗口内" (config/filtering.yaml 的 context_window.ss_sentence_radius, 默认 1) 的句子拼接, 判定口径不对称 — 银行侧经否定与短名过滤, 金融科技侧为裸 AC 自动机词典命中。相比 ctx 轨的实体窗口, ss 轨进一步要求银行与金融科技在句法单元内共现, 把"同篇但不同话题"的词命中也排除, 是"这篇报道确实在谈这家银行的金融科技"的最强文本证据。回退语义务必与 CLAUDE.md 口径一致: ss 镜像 ctx 的回退设计, 当一篇文章不存在银行与金融科技同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 与其他轨共享 n_articles 分母; 金融科技自动机不可用 (FINTECH_AC=None) 时全部标回退、优雅降级不崩。生产端 ss 为软依赖: 上游 15_fintech_intensity 无 ss 强度列的旧 schema 下, 本列 graceful skip 整体缺席, full/ctx 照常。留篇门控为 full-only 口径, ss 是 conditional-on-full 测度轨; 聚合、脊柱、零与 NaN 契约、clip 与 log1p 全部镜像主列。软依赖的判定以聚合帧是否含 fintech_intensity_score_ss 列为准, 缺列只掉 ss 族自身、绝不牵连 full 与 ctx 列, 属逐列 graceful skip 而非 co-primary 嵌入那种 both-or-neither 连坐语义, 两种降级机制不可混称; 产后校验中本列同受下界断言 (值域 [0, +∞)) 监控, 全 NaN 时响亮告警。T=2 开发样本上本列可能零方差, 属预期退化。用法: 单独替换主列复跑, 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁与 full/ctx 混进同一 over-identified Hansen J。

## VAR: attention_index_ss_j70w10

【变体差分】
本列是 ss 轨指数在去重参数双向最严端点 (Jaccard 0.70 × 10 工作日) 的重算, 是全家族十五列中口径叠加最深的一列: 同句共现归因 (三轨中最严) 叠加最激进去重 (四变体中剔除最多), 构成"最保守测量"的角点臂。若主结论在本列下仍保持符号与显著性, 等于同时通过了归因严格性与转载剔除两个维度的最强压力测试; 反之若仅本列失效, 应结合同轨其余变体与 full 轨同参数变体定位失效来源是轨道还是去重参数, 而非笼统归因。计算链路: 在参数无关的 MinHash 签名上按 0.70/10 追加判重得存活集 (单调不变量约束), 存活集内 fintech_intensity_score_ss 分子经 stage-21 verified 门控 (留篇 full-only 口径) 后按 (target_bank, year) 求和, 变体内全集脊柱 LEFT-join, 真零填 0、无银行新闻 NaN、clip 非负、log1p, 值域 [0, +∞)。ss 轨语义与回退契约继承主 ss 列: 无同句共现的文章其 content_ss 回退为全文 body 并标记 ss_is_fallback、与其他轨共享 n_articles 分母; 旧 schema 无 ss 强度列时本变体列 graceful skip 整体缺席, 同变体的 full/ctx 列照常落盘。两阶段近似保守下界与跨语料盲区披露同样适用; T=2 开发样本上本列因同句共现叠加激进去重可能出现零方差或全 NaN, 属预期退化, 生产 T=19 语料下正常。用法: 单独替换 attention_index_ss 复跑, 与其余臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: attention_index_ss_j70w5

【变体差分】
本列是 ss 轨指数在 Jaccard 阈值 0.70 × 5 工作日参数下的去重敏感性变体: 窗口维持生产值, 单独把相似度阈值拧低到 0.70, 在同句共现的严格归因轨上检验"改写转载剔除"的影响。ss 轨与阈值扰动的交互有独特诊断含义: 通稿改写往往保留核心句式 — 恰恰是银行名与金融科技词同句共现的那几句最可能被逐字保留, 因此改写转载对 ss 轨强度的虚增可能比对 full 轨更集中; 本变体把相似度七成即算转载的严标准施加后重算, 与 attention_index_full_j70w5 对照可分离"转载虚增是否主要经由共现句复制"这一机制层信息。计算口径逐点镜像同轨主列: MinHash 签名一次计算变体间复用, 存活集服从单调不变量, fintech_intensity_score_ss 分子经 stage-21 verified 门控 (留篇 full-only 口径), 变体内全集脊柱 LEFT-join, 零金融科技 bank-year 填 0 为真零曝光, 完全无银行新闻为 NaN, clip 非负后 log1p, 值域 [0, +∞)。ss 回退语义 (无同句共现回退全文 body 并标 ss_is_fallback、共享 n_articles 分母) 与旧 schema 下 graceful skip 的软依赖行为继承; 两阶段近似保守下界与跨语料盲区口径随列披露, 存活集服从单调不变量 (不超过生产存活集)。用法: 单独替换 attention_index_ss 复跑, 与其余臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J, 亦不与其他臂同进一个 RHS。

## VAR: attention_index_ss_j75w5

【变体差分】
本列是 ss 轨指数在 Jaccard 阈值 0.75 × 5 工作日参数下的去重敏感性变体, 即同句共现轨上阈值梯子的中间档。它与 attention_index_ss_j70w5 和生产锚点 attention_index_ss 一起构成 ss 轨的三点剂量序列 (0.80, 0.75, 0.70), 用于检验严格归因口径下去重敏感性的剂量反应形态: 单调平滑移动指向连续测量噪声, 中间档跳变指向特定相似度区间转载文章的集中杠杆。由于 ss 轨的行为主体是共现句拼接文本、平均长度远短于全文, 强度分的文长归一化分母更小, 同一批转载文章的剔除对 ss 轨累积和的相对扰动可能大于对 full 轨的扰动, 故 ss 轨的剂量序列须与 full 轨同参数序列并排解读, 不可跨轨比较扰动幅度的绝对水平。计算口径与同轨主列完全镜像: 参数无关 MinHash 签名上按 0.75/5 追加判重, 存活集内 fintech_intensity_score_ss 分子经 stage-21 verified 门控 (留篇 full-only 口径) 聚合, 变体内全集脊柱 LEFT-join, 真零填 0、无银行新闻 NaN、clip 非负、log1p; ss 回退语义 (镜像 ctx 设计, 无共现回退全文 body 标 ss_is_fallback) 与旧 schema graceful skip 继承, 存活集单调不变量、两阶段近似保守下界、跨语料盲区披露全部适用。报告形态遵循模块约定: 与同轨其余臂配 esttab 并列成敏感性附表, 以系数符号与显著性的跨臂稳定性为证据形态, 不以变体与锚点的面板内相关性充数 — 试跑样本变体仅追加剔除极小比例文章, 高相关是低剔除率下的平凡结果而非稳健性证明。用法: 单独替换 attention_index_ss 复跑回归, 各臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: attention_index_ss_j80w10

【变体差分】
本列是 ss 轨指数在 Jaccard 阈值 0.80 × 10 工作日参数下的去重敏感性变体: 阈值维持生产值, 单独把转载窗口拉长到 10 个工作日, 在最严归因轨上检验迟发转载的影响。与阈值臂互补, 本臂捕获的是高保真、迟到达的重复文本 — 周期性刊物与门户补录在首发一至两周后重发的稿件; 这类稿件因近乎原样复制, 其中银行与金融科技同句共现的句子几乎必然随稿保留, 落入 ss 轨强度累加, 使 ss 轨对迟发转载的暴露不低于 full 轨。本变体施加长窗口剔除后重算, 与 attention_index_full_j80w10 并排解读可判断迟发转载的虚增是否穿透到最严格的归因口径。计算口径逐点镜像同轨主列: 复用一次计算的 MinHash 签名按 0.80/10 追加判重, 存活集服从单调不变量 (不超过生产存活集), fintech_intensity_score_ss 分子经 stage-21 verified 门控 (留篇 full-only 口径) 后按 (target_bank, year) 求和, 变体内全集脊柱 LEFT-join, 零金融科技填 0 为真零曝光, 完全无银行新闻为 NaN, clip 非负后 log1p, 值域 [0, +∞)。ss 回退语义与软依赖 graceful skip 行为、两阶段近似保守下界口径、跨语料盲区披露义务全部继承; 变体参数网格默认含本臂, 可经 config/panel.yaml 的 panel_building.dedup_sensitivity.variants 键覆盖, 存活率诊断与 two_stage_approximation 标记落 sidecar 供表脚注引用 (sidecar 域为全 docid 去重存活率, 与分子的 verified 交存活域不同)。用法: 单独替换 attention_index_ss 复跑, 与生产锚点及其余变体互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics. https://doi.org/10.1002/mde.70100
Zhou, W., Chen, F., Zhu, Y., Xiang, L., & Lei, L. (2024). Media attention, negative reports and textual information of banks' ESG disclosure. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.103583
Kwan, A., Liu, Y., & Matthies, B. (2026). Institutional Investor Attention. The Journal of Finance. https://doi.org/10.1111/jofi.70009
Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, Article 101670. https://doi.org/10.1016/j.jempfin.2025.101670
Kalyani, A., Bloom, N., Carvalho, M., Hassan, T. A., Lerner, J., & Tahoun, A. (2025). The diffusion of new technologies. The Quarterly Journal of Economics, 140(2), 1299-1365. https://doi.org/10.1093/qje/qjaf002
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, Article 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. The Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. Accounting & Finance, 64(S1), 5107-5131. https://doi.org/10.1111/acfi.13328
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Bellstam, G., Bhagat, S., & Cookson, J. A. (2021). A text-based analysis of corporate innovation. Management Science, 67(7), 4004-4031. https://doi.org/10.1287/mnsc.2020.3682
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, Article 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Chen, M. A., Wu, Q., & Yang, B. (2019). How valuable is FinTech innovation? The Review of Financial Studies, 32(5), 2062-2106. https://doi.org/10.1093/rfs/hhy130
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Park, S., & Cho, M. (2024). Media Attention and Labor Investment Efficiency. Asia-Pacific Journal of Financial Studies. https://doi.org/10.1111/ajfs.12496
<!-- rendered-citations:end -->
