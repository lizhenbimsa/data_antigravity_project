---
family_id: F297
columns:
- fin_sent_zh_nt_iytrend_ctx
- fin_sent_zh_nt_iytrend_full
- fin_sent_zh_nt_iytrend_ss
- fin_sent_zh_nt_iyvol_ctx
- fin_sent_zh_nt_iyvol_full
- fin_sent_zh_nt_iyvol_ss
- finbert2_nt_iytrend_ctx
- finbert2_nt_iytrend_full
- finbert2_nt_iytrend_ss
- finbert2_nt_iyvol_ctx
- finbert2_nt_iyvol_full
- finbert2_nt_iyvol_ss
- finbert_cn_nt_iytrend_ctx
- finbert_cn_nt_iytrend_full
- finbert_cn_nt_iytrend_ss
- finbert_cn_nt_iyvol_ctx
- finbert_cn_nt_iyvol_full
- finbert_cn_nt_iyvol_ss
unit: "无量纲 (net_tone = P(正面)−P(负面) ∈ [−1,1] 派生; iyvol = 噪声校正后的月均值标准差, ≥0; iytrend = 月度 OLS 斜率, 量纲 = 净语调/月)"
formula: "m_t = 月内文章级 net_tone 均值; iyvol = sqrt(max(0, Var1(m_t) − (1/T)·Σ_t σ̂²/n_t)), σ̂² = Σ_{n_t≥2}(n_t−1)s²_t / Σ_{n_t≥2}(n_t−1) (双 ddof=1); iytrend = Σ(x−x̄)(m−m̄)/Σ(x−x̄)², x = 实际月号 ∈ {1..12}; 门槛 iyvol: T≥3 且 ≥1 月 n_t≥2; iytrend: T≥6"
producer: news_process/pipeline/panel/bert_distribution.py::compute_intrayear_dynamics
upstream:
- 23_bert_tone.parquet (三模型 x 三轨概率列 {b}_正面{trk} / {b}_负面{trk}; producer = pipeline/sentiment/tone_berts.py)
- 40_article_bank_level (文章级 target_bank/year/日期 键, runner 步骤内存 frame)
citations:
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: "102325"
- doi: 10.1016/j.jfineco.2025.104218
  type: journal
  authors: Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C.
  year: 2026
  title: "Social media as a bank run catalyst"
  venue: Journal of Financial Economics
  vol: 176
  pages_or_artno: "104218"
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: "101126"
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: "1373-1403"
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
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: "103870"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: "1150-1172"
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: "105227"
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: "e1549"
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: "e2305016120"
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: "806-841"
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: "673-719"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: "5514-5532"
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: "2135-2202"
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: "1139-1168"
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: "1187-1230"
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
本家族 (F297, bertdist_intrayear) 是 BERT 分布形状五族中的年内动态族, 由 18 列构成: 三个中文金融 BERT 模型 (finbert_cn, fin_sent_zh, finbert2) 乘以两个年内动态指标 (iyvol 年内波动, iytrend 年内趋势) 再乘以三条文本轨道 (full, ctx, ss)。其测量的构念是: 一家银行在一个日历年之内, 媒体对其金融科技活动的净语调是否稳定、是否存在系统性的月度漂移。传统的银行-年语调面板只保留年度一阶矩 (全年语调均值), 把十二个月内部的叙事起伏全部压平; 然而对银行这类高度依赖公众信心的机构, 语调路径本身携带独立信息 — 同样是全年均值为零的两家银行, 一家可能全年平稳中性, 另一家可能上半年被密集唱多、下半年被密集唱空, 两者的信息环境与储户、投资者面对的信号极不相同。Tetlock (2007) 开创的媒体语调文献证明媒体悲观度的时间序列变动对市场有预测力, Fang, Wang, Wang & Yuan (2024) 进一步在中国银行业场景证明媒体情感波动与存款稳定性、系统性风险相关联, Cookson, Fox, Gil-Bazo, Imbet & Schiller (2026) 则用硅谷银行事件证明社交媒体叙事的短窗剧烈变动可以成为挤兑催化剂 — 这些证据共同说明语调的二阶矩与趋势分量是独立于均值的风险相关构念。本家族把这一构念落地为两个逐 (银行, 年) 格的标量: iyvol 度量月度语调均值序列在扣除抽样噪声之后的真实离散度 (叙事不稳定性), iytrend 度量月度语调均值对月号回归的斜率 (年内叙事方向漂移, 即该年媒体口径是转暖还是转冷)。数据来源链条为: stage 23 (tone_berts) 对每篇通过共现过滤的银行-金科新闻用三个 BERT 模型逐轨推理, 输出各类别概率列; 本家族在 panel 组装期 (runner 步骤 7h-net 之后) 以纯后处理方式从这些概率列派生, 不发生任何新的模型调用或 API 调用, 增量成本为零。三个模型分别是: finbert_cn (HuggingFace yiyanghkust/finbert-tone-chinese, 三分类 正面/负面/中性), fin_sent_zh (HuggingFace bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 思路微调的中文金融三分类), finbert2 (本项目私有微调的本地二分类模型, 负面/正面, 经环境变量 FINBERT2_MODEL_DIR 解析, 缺席时优雅跳过)。文章级净语调统一定义为 net_tone = P(正面) − P(负面), 取值范围 [−1, 1], 对二分类的 finbert2 同样成立 (其中性概率列是全 NaN 占位, 计算路径只读正负两列)。用白话说, 这一族回答的是两个直观问题: 第一, 这家银行今年被媒体谈论金融科技时, 口风是不是一个月一个样 (iyvol); 第二, 从年初到年尾, 口风整体上是越来越好听还是越来越难听 (iytrend)。年度均值只告诉我们全年平均口风, 这两列补上了均值背后被抹掉的路径信息。之所以值得单独测量, 是因为银行经营高度依赖公众信心, 口风反复无常本身就是一种信息环境风险信号: 储户与投资者面对摇摆的叙事更难形成稳定预期, 监管沟通与银行自身的信息披露也更容易被媒体节奏放大或对冲。把这两个量做成逐银行逐年的标准面板列之后, 研究者不需要接触任何文章级数据即可直接在年度回归中使用。

【方法学与计算】
计算全部实现于 pipeline/panel/bert_distribution.py::compute_intrayear_dynamics, 该模块是刻意设计的叶模块 (BERT_MODELS 等以参数注入, 禁反向 import encode 成环)。第一步, 从文章级 frame 取 日期 列解析出月号, 对每个 (模型, 轨道) 组合计算逐篇 net_tone = 正面概率减负面概率, 丢弃月号或 net_tone 为 NaN 的行; 第二步, 按 (target_bank, year, month) 分组得到月度统计: 月均值 m_t, 月内篇数 n_t, 月内文章级样本方差 s²_t (ddof=1, 单篇月为 NaN); 第三步, 按 (target_bank, year) 聚合出年格。iyvol 的公式为 sqrt(max(0, Var1(m_t) − (1/T)·Σ_t σ̂²/n_t)): 其中 Var1 是月均值序列的样本方差 (ddof=1), T 是有效月数 (有效月 = 该月至少一篇非 NaN 净语调, 含单篇月), σ̂² 是池化的文章级方差 Σ(n_t−1)s²_t / Σ(n_t−1) (仅对 n_t≥2 的月估计, 双 ddof=1, 池化隐含月间文章级方差同质假设), 而校正项对全部有效月求和 — 包括 n_t=1 的月, 因为单篇月的均值抽样噪声最大, 恰恰最需要校正。这一噪声校正是本指标区别于朴素月度标准差的方法学核心: 直接取月均值序列的标准差, 会把报道稀少月份的均值本身不准确当成真实语调波动, 使低媒体覆盖银行的波动指标机械性虚高, 与银行规模、知名度产生虚假负相关; 扣除项 (1/T)·Σ σ̂²/n_t 在双 ddof=1 设定下满足 E[Var1(m_t)] = Var1(μ_t) + (1/T)Σσ²/n_t 的无偏分解 (对逐月异质的 n_t 与 σ²_t 均成立, 无偏性仅指开方与 max(0,·) 截断之前的方差差)。门槛为 T ≥ 3 (IYVOL_MIN_MONTHS) 且至少一个月 n_t ≥ 2 (否则池化方差不可估, 宁缺勿噪, 置 NaN)。iytrend 的公式为月均值对实际月号 x ∈ {1..12} 的闭式 OLS 斜率 Σ(x−x̄)(m−m̄)/Σ(x−x̄)², 门槛 T ≥ 6 (IYTREND_MIN_MONTHS, 三点回归自由度仅 1 纯属噪声, 半年跨度起判); 斜率分母严格为正由月号互异加门槛的结构保证。实现上刻意用求和项闭式计算而禁用 numpy.linalg.lstsq 或 polyfit — LAPACK 路径会引入 BLAS 浮点非确定性, 破坏 golden 逐位复现口径 (先例是网络中心性列的 _KNOWN_BLAS_RE 问题族)。schema 合同: 零行输入也返回含 target_bank/year 与全部 18 个 float64 指标列的 frame (wire-ahead, 防空 object 列导出崩溃先例); 某 (模型, 轨道) 概率列缺席时该 2 列全 NaN 但在位 (finbert2 未配置目录时即此路径, per-model 独立降级, 仅掉自身族, 不连坐另两模型 — 注意这与 co-primary 嵌入的 both-or-neither 口径不同)。merge 时序在 balance_panel 零填之后, 以 how='left' 并入 (并入前 pre-drop 既存同名列防 _x/_y 后缀), 因此本族列结构上不经零填充: 无新闻的 (银行, 年) 格天然为 NaN 而非 0, 计量上不会把缺失误读为零波动、零趋势。上游测量细节对本族的解释有直接影响, 故在此一并交代: stage 23 为 always-on 阶段, 对每篇文章按模型自身分词器分窗推理, 超过单窗长度上限的长文以百分之五十重叠的滑动窗口切片, 各窗结果按置信度加权池化聚合; 空文本与推理失败分别以窗口数零与负一哨兵区分, 失败篇的概率列为 NaN, 自然被本族的丢行步骤剔除而不污染月度均值。逐篇 net_tone 因此是整篇文章级的单一净值, 月度聚合不对文章长度加权 — 长文与短讯在月均值中权重相同, 这是与注意力加权类测度的刻意口径差异。确定性方面, 本族全部算子为分组聚合与逐元素闭式运算, 不经特征分解路径, 不在 BLAS 浮点漂移名单内, golden 逐位可复现; 文章级与月度级的全部中间量均为运行期临时对象, 不落任何 parquet, 面板是本族唯一持久化层。

【文献定位】
本家族在三支文献的交汇处。第一支是金融文本情感测量方法学: Loughran & McDonald (2016) 的综述确立了从词典到机器学习的测量谱系, Frankel, Jennings & Lee (2022) 系统比较了机器学习与词典法在披露情感上的相对优势, Huang, Wang & Yang (2023) 证明领域预训练的 FinBERT 在金融文本上显著优于通用模型与词典, Todd, Bowden & Moshfeghi (2024) 对金融情感分析文献做了最新综合并指出情感动态是未充分开发的方向。中文场景下, Du, Huang, Wermers & Wu (2022) 构建了语言与领域双特异的中文金融情感词典并示范了跨语言直译词典的失效, Ma, Zhang & Zhang (2025) 构建了面向中国本土投资者的细粒度情感词典, Lan, Wu, Xu, Feng & Zhang (2025) 展示了大模型在中文金融实体级细粒度情感上的能力 — 本项目以 LLM 三家投票、六词典、三 BERT 的三方法三角互证结构回应这条线, 本家族属其中 BERT 支的分布形状扩展。第二支是媒体语调与银行稳定: Tetlock (2007) 与后续研究确立媒体语调的信息含量, Fang, Wang, Wang & Yuan (2024) 给出中国银行级媒体情感影响存款稳定与系统性风险的直接证据, Cookson, Lu, Mullins & Niessner (2024) 证明社交媒体信号的横截面与时序结构含有超越均值的信息, Cookson, Fox, Gil-Bazo, Imbet & Schiller (2026) 记录叙事动态在银行挤兑中的催化作用, Marchetti, Tarducci & Branzoli (2025) 则直接以银行融资条件为对象测量媒体语调的时间漂移, 与 iytrend 的构念高度同源。第三支是文本派生二阶矩作为风险测度的传统: Hassan, Hollander, van Lent & Tahoun (2019) 示范了从文本份额构造企业级风险 (本质是波动性构念) 测度的范式, Gutknecht (2025) 证明媒体负面覆盖与企业股权风险 (波动) 的联系, Garcia (2025) 证明情感分歧 (离散度构念) 对财务困境有预测力。此外 Gilardi, Alizadeh & Kubli (2023) 与 Kirtac & Germano (2024)、Chen, Granville & Matousek (2026) 代表的 LLM 文本标注与解码文献, 构成本项目 BERT 支与 LLM 支互为稳健性设计的方法学背景。

【识别策略定位】
本家族在全部 11 篇论文的识别设计中均不担任 treatment 主轨 (P1 的 treatment 是 llm_vote_tone_full), 而是三重角色: 其一, 作为语调二阶矩与动态通道的机制变量 — 若主效应经由信息环境不确定性起作用, 则 iyvol 应在机制回归中显著; 其二, 作为均值语调结果的稳健性维度 — 主结论若仅由年均语调驱动而对语调路径不敏感, 可通过控制 iyvol/iytrend 后主系数稳定来证明; 其三, 作为异质性切分变量 (高叙事不稳定银行子样本)。计量口径受多重铁律约束。第一, per-model 铁律: 三个 BERT 模型的年内动态列互为稳健性、不分主次, 无 ensemble headline, 各自 just-identified 并排进入各自的回归, 禁止把不同模型的同名指标混进同一个 over-identified 方程去做 Hansen J 检验 — 三模型测的是同一构念的三个有噪代理, 混入同一工具集在概念上就违反排除性设定, 这与三轨、co-primary 嵌入双轨、政治词权重梯度是同款铁律。第二, 三轨铁律: full/ctx/ss 三条文本轨道同样各自 just-identified 并排、互为稳健性不分主次、禁混同一 over-identified Hansen J。第三, 留篇门控口径 (2026-06-29 full-only): 一篇文章是否计入银行金科报道宇宙只看 llm_verified_full, ctx/ss 是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集的子集; 本家族继承该文章宇宙。第四, 跨模型多重检验用根级 rwolf 模板 (Romano & Wolf (2005) 逐步法) 控制 FWER, 而非事后挑选显著模型; 跨模型比较系数时须 z-score 标准化, 因为二分类与三分类模型的 net_tone 原始方差不同。第五, 本族为非嵌入测度 (BERT 概率派生), 属 carve-out, 无 _lg 孪生列, 亦与嵌入模型更换完全解耦。回归实操口径: 本族两指标进入年度面板回归时建议与其它文本测度一致做样本内标准化, 使系数可读为一个标准差叙事不稳定或叙事漂移对应的结果变化; 银行与年份双固定效应下, 年份固定效应会吸收全行业共同的季节-年度成分 (如全行业监管周期造成的普遍年内转冷), 留下的识别变异是银行相对于同年同业的异质年内动态, 这恰是本族构念的目标层次; 聚类标准误按银行聚类, 与主线设定一致。此外, 由于 iyvol 的可估性门槛造成的样本缺失与媒体覆盖相关, 涉及本族的回归应报告门槛通过率, 并以覆盖强度控制或子样本稳健性佐证缺失非随机性不驱动结论。

【与相邻测度的构念区分】
与本面板既有的语调离散测度相比, 本家族的独特性在于时间结构。tone_volatility 族是跨年 rolling 波动, 度量银行语调在多个年度之间的漂移, 与 iyvol 的年内月度构念真正交 — 一家银行可以跨年稳定但年内剧烈起伏, 反之亦然。{b}_pos_std 等概率离散列度量的是同年内文章与文章之间的截面离散 (文章级异质性), 不含任何时间排序信息; iyvol 度量的是月均值序列的时序波动且显式扣除了文章级截面噪声的贡献, 两者在校正之后仅近似正交 (producer 文档的正交声明口径)。同为 BERT 分布形状五族的兄弟测度中: tone_entropy 是文章级判类模糊度 (单篇内部概率分布的形状) 的年均, xneg_frac 是极端负面文章的占比 (尾部质量), net_tone_skew 是年内文章级净语调分布的偏度 (截面不对称), bert_xmodel_lblhet/disp 是三模型间标签分歧 — 五族分别对应分布的模糊度、尾部、不对称、跨模型分歧与时间动态五个不重叠的形状维度, 本家族独占最后一个。与 LLM 支的 llm_vote_tone 及词典支的 du_2022_tone 等年均语调相比, 本家族是同一文本宇宙上的高阶矩补充而非替代。iytrend 与 iyvol 彼此也构念可分: 前者捕捉有方向的系统漂移 (斜率), 后者捕捉无方向的离散 (标准差), 一个全年线性转冷的银行可以有高 iytrend 绝对值而中等 iyvol, 一个月度锯齿震荡的银行则相反。还须说明本族在三方法三角结构中的不对称性: LLM 支与词典支在本面板中均没有对应的年内动态列 — 这不是遗漏而是刻意取舍, LLM 逐篇标注成本高且其面板列族已承担 treatment 主轨职责, 词典支则以消融与权重梯子承担规格稳健性职责; BERT 支概率输出的连续性与零边际成本使其成为承载分布形状扩展的唯一合适支线。因此本族不存在跨方法的同名孪生列, 跨方法互证发生在年均语调层而非年内动态层。

【已知局限与稳健性梯子】
第一, 池化方差假设月间文章级方差同质; 若真实方差随月份系统变化 (如财报季更极化), 校正项有偏, 但方向性偏误在三模型三轨的并排稳健性下可被交叉检验。第二, max(0,·) 截断与开方使 iyvol 在真实波动接近零时呈非负偏 — 截断前的方差差才是无偏对象, 使用时应避免把 iyvol=0 精确解读为零波动。第三, 门槛设计 (T≥3 且 ≥1 月 n_t≥2; 趋势 T≥6) 使低覆盖银行系统性缺失, 样本选择与媒体关注度相关, 回归中须意识到该缺失非随机; 这是宁缺勿噪的刻意取舍, 备选的放松门槛版本被评审否决因为三点回归与不可估池化方差只产噪声。第四, 开发机早期试跑 T=2 语料上本族大量格因月覆盖不足而 NaN 属预期退化, 生产 T=19 语料上正常出值; 严禁以 dev 快照的缺失率推断生产数据质量。第五, finbert2 是二分类模型, 其 net_tone 的方差结构与三分类模型不同, 跨模型禁比水平只比标准化系数; finbert2 缺席时其 6 列全 NaN 而另两模型照常, per-model 独立降级。第六, 月号斜率把年内趋势限定为线性, 非线性叙事路径 (先扬后抑) 会被斜率抹平, 此时 iyvol 高而 iytrend 近零, 两指标联用可部分识别该形态。第七, 季节性混淆: 中国财经媒体的报道节奏存在系统季节成分 (年报季、政策窗口期), 若该成分对全部银行同质, 会被年份固定效应吸收; 若与银行特征交互 (如上市银行财报季曝光更集中), 则 iyvol 部分反映披露日历而非叙事不稳定, 解释时须以上市状态等特征做异质性检验。第八, 本族把年内信息压缩为两个标量是研究设计选择 — 备选方案是直接构建银行-月面板, 但月度面板在财务结果变量年度频率的约束下无法对接主线识别设计, 且月度格稀疏问题远比年度严重; 两标量方案以可控的信息损失换取与主面板的无缝对接。第九, 测量误差随有效月数 T 递减, 回归中可用 T 或年篇数作精度权重的稳健性检验, 但主口径刻意不加权以保持列语义的简洁可审计性。稳健性梯子上, 本家族自身即是 3 模型 x 2 指标 x 3 轨的并排矩阵, 与相邻的阈值梯子 (xneg 的 t80/t95)、政治词权重梯子、词典消融梯子彼此正交不交叉, 全部服从各自 just-identified 并排、禁混同一 over-identified Hansen J 的总口径。第十, iyvol 与银行媒体关注度存在残余相关: 噪声校正剥除了抽样噪声造成的机械虚高, 但真实叙事摇摆本身仍可能与银行规模、上市状态、系统重要性相关 (大行被更密集报道也可能被更频繁重估), 因此本族在横截面回归中不宜单独解读为纯粹的信息环境外生冲击, 而应与银行固定效应联用、以行内时间变异为识别源。第十一, 确定性口径须实证守护: 本族全部算子为分组聚合与逐元素闭式运算, 不落 BLAS 特征分解路径, 理论上 golden 逐位可复现, 但生产语料重生时仍须以 PYTHONHASHSEED=0 与全 BLAS 线程钉一的受控环境验证零字节漂移, 不可因本族不在网络中心性 BLAS 漂移名单内就免验。守门测试为 tests/test_bert_distribution_metrics.py, 锚死月门槛字面量 (T≥3/T≥6)、闭式斜率禁 lstsq、噪声校正双 ddof=1、零行 wire-ahead schema 等命门, 任一命门回归即红灯。

## VAR: fin_sent_zh_nt_iytrend_ctx

【变体差分】
本列是 fin_sent_zh 模型年内净语调趋势 iytrend 的 ctx 轨变体, tier=standard。区别于家族 canonical (full 轨) 的唯一差分维度是文本轨道: ctx 轨的输入文本为标题 prepend 加银行实体上下文窗口 (content_ctx, 由 stage 14 ctx_materializer 物化), 即只保留目标银行实体附近的正文片段, 剔除同篇中与该银行无关的段落。因此本列度量的是专门谈论该银行的那部分文本的净语调月度线性漂移, 对多银行合报、行业综述类长文的语调污染更不敏感, 但可用文本更短、单篇 net_tone 噪声更大。计算公式、月门槛 (有效月 T≥6)、闭式斜率实现与 full 轨逐字相同, 仅概率输入列换为 fin_sent_zh_正面_ctx 与 fin_sent_zh_负面_ctx。行宇宙口径: 留篇门控为 full-only (2026-06-29), ctx 轨是 conditional-on-full 的测度轨, 其行宇宙为 full 留篇集的子集。与 full/ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。fin_sent_zh 为 HuggingFace 公开三分类模型, 缺席场景仅限推理失败哨兵, 无 per-model 目录降级路径。使用定位: 本列的典型角色是 full 轨趋势结论的窗口稳健性复认 — 若 full 轨的叙事漂移效应在剔除非实体邻近文本后消失, 提示原效应部分由同篇他行或行业背景语调驱动; 两轨结论一致则强化漂移确属该银行自身叙事的解读。ctx 轨有效月分布继承 full 轨的月度覆盖 (同一留篇集), 但单篇噪声更大使斜率标准误偏宽, 功效低于 full 轨属结构性预期而非异常。

## VAR: fin_sent_zh_nt_iytrend_full

【变体差分】
本列是 fin_sent_zh 模型年内净语调趋势的 full 轨, tier=core, 系本家族 iytrend 指标在该模型下的 canonical 列 (类别6扩围①, 2026-07-10 签核: 年内趋势与年内波动并列为分布形状族第二测度)。模型侧: fin_sent_zh 对应 HuggingFace 公开模型 bardsai/finance-sentiment-zh-base, 是基于 Financial PhraseBank 范式在中文金融语料上微调的三分类模型 (正面/负面/中性), 三模型中它与 finbert_cn 同为公开可复现臂, 与私有的 finbert2 形成公开-私有互证结构; 其净语调 net_tone = P(正面) − P(负面), 中性概率不进入净值但通过归一化间接压缩正负概率的量级, 这一点与二分类 finbert2 的方差结构差异是跨模型只比标准化系数、禁比原始水平的根本原因。轨道侧: full 轨输入为标题 prepend 加全文正文 (未做实体窗口裁剪), 是信息最完整、单篇噪声最小的轨道, 也是留篇门控 (full-only, 2026-06-29) 所定义的文章宇宙本身, 因此 full 轨无 conditional-on-full 的子集缩减, 月覆盖在三轨中最优, iytrend 的 T≥6 有效月门槛在 full 轨最容易满足。指标侧: 本列为该银行该年月度净语调均值对实际月号 x ∈ {1..12} 的闭式 OLS 斜率, 量纲为净语调每月, 正值表示该年媒体对该银行金科叙事逐月转暖, 负值表示逐月转冷; 斜率用求和项闭式计算而非 lstsq/polyfit, 以保住 golden 逐位确定性。有效月不足 6 时为 NaN; 无新闻格因 merge 时序在零填之后而天然 NaN, 不会被误置 0。解释与使用要点: 量级上乘以十一即得年初至年末拟合口径的总漂移幅度; 由于净语调有界于正负一之间, 斜率的可行域随均值水平收缩, 极端均值年份的斜率天然偏小, 这是有界测度的机械性质而非叙事平静的证据。回归使用上建议标准化后进入, 并与年份固定效应联用 — 全行业共同的年内转向由年份效应吸收, 本列的识别变异是该银行相对同年同业的异质漂移。与事件研究的衔接: 若研究者关心特定冲击年份 (如重大金融科技监管事件年) 的叙事响应, 本列提供了比年均语调更灵敏的一阶动态代理, Marchetti, Tarducci & Branzoli (2025) 对银行融资条件报道语调漂移的测量正是这一用法的外部对应。另须留意本列与词典支、LLM 支年均语调列的关系: 年内趋势层没有跨方法孪生列, 本列与另两 BERT 模型的同名列即该构念的全部测量, 三者一致性承担了通常由跨方法互证承担的效度职责, 这也是趋势列被签核提升为 core 的理由之一。使用口径: 与 finbert_cn/finbert2 的同名 full 列互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型联合推断走根级 rwolf FWER 模板。与同模型的 iyvol_full 联用可区分有向漂移与无向震荡: 高斜率绝对值低波动是单调转向, 低斜率高波动是往复震荡。本列无 _lg 孪生 (非嵌入 carve-out), 与嵌入模型更换零耦合。最后交代与门槛相关的入样机制: 有效月门槛六个月意味着年中才进入样本框的新上市银行或更名银行首年多为 NaN, 面板早期年份的覆盖率解释须留意这一机制; 本列继承 stage 23 推理失败哨兵的剔除逻辑, 失败篇不进入月度均值, 空文本与失败篇分别以窗口数哨兵区分, 均不污染斜率估计。描述统计中本列的缺失因此混合了无新闻、门槛不足与失败剔除三种来源, 细分解读时以年篇数与有效月数两个辅助量判别, 不可笼统归为数据稀疏。

## VAR: fin_sent_zh_nt_iytrend_ss

【变体差分】
本列是 fin_sent_zh 模型年内净语调趋势的 ss 轨变体, tier=standard。差分维度为文本轨道: ss 轨输入为标题 prepend 加目标银行与金融科技词出现在同一句 (含 ±1 句窗, 生产默认半径 1) 的句级片段 (content_ss), 是三轨中语义靶向最窄、与银行金科议题绑定最紧的轨道。回退语义须严格按项目口径复述: ss 轨镜像 ctx 的回退设计 — 当一篇文章不存在银行与金科词同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True, 与 full 轨共享 n_articles 分母; 上游 FINTECH_AC 不可用时全部行 fallback 为 True 优雅降级。因此本列在高 fallback 占比的年份实际趋近 full 轨语义, 解释时应意识到其窄靶性质是逐篇条件性的。计算公式与门槛 (T≥6) 同家族 canonical, 概率输入列为 fin_sent_zh_正面_ss / fin_sent_zh_负面_ss。行宇宙为 full-only 留篇集的子集 (conditional-on-full)。与 full/ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。使用定位: 本列检验叙事漂移是否在银行与金科被同句并提的最强关联语境中成立, 是三轨中对构念纯度要求最高、对功效要求最宽容的一臂; 其与 full 轨的差异由两部分构成 — 真实的窄靶语义差与 fallback 稀释, 逐年 fallback 占比是区分两者的必读诊断量。生产语料上同句共现率随金科议题热度逐年上升, ss 轨的窄靶解释力在后期年份更强。

## VAR: fin_sent_zh_nt_iyvol_ctx

【变体差分】
本列是 fin_sent_zh 模型年内净语调波动 iyvol 的 ctx 轨变体, tier=standard。差分维度为文本轨道: 输入概率列为 fin_sent_zh_正面_ctx / fin_sent_zh_负面_ctx, 文本为标题 prepend 加银行实体上下文窗口。度量该银行该年实体邻近文本净语调月均值序列在噪声校正后的标准差。方法学与 canonical 逐字相同: 先按月聚合 net_tone 均值 m_t, 再算 sqrt(max(0, Var1(m_t) − (1/T)·Σ σ̂²/n_t)), 池化方差仅对 n_t≥2 的月估计而校正项对全部有效月求和; 门槛 T≥3 且至少一月 n_t≥2, 否则 NaN。ctx 轨文本更短, 文章级 net_tone 的截面方差 σ̂² 通常更大, 噪声校正项因此更大 — 这正是校正设计的价值所在: 若不校正, ctx 轨波动会因文本短噪声大而机械性高于 full 轨, 校正后两轨差异才可解释为真实的窗口内外语调动态差。行宇宙为 full-only 留篇集子集 (conditional-on-full 测度轨)。与 full/ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列复认 full 轨波动结论对文本窗口的稳健性; 若实体邻近文本的语调摇摆显著弱于全文口径, 提示全文波动部分来自背景段落 (行业评论、政策综述) 的语调起伏而非针对该银行的叙事摇摆。因单篇噪声大、校正项大, 本列可估格数与量级均低于 full 轨属结构性预期, 解释时不与 full 轨比原始水平, 只比标准化效应。

## VAR: fin_sent_zh_nt_iyvol_full

【变体差分】
本列是 fin_sent_zh 模型年内净语调波动的 full 轨, tier=core, 系本家族 iyvol 指标在该模型下的 canonical 列 (类别6签核: BERT 分布形状族年内波动 canonical)。模型侧: fin_sent_zh (bardsai/finance-sentiment-zh-base) 是公开三分类中文金融情感模型, 其训练范式承袭 Financial PhraseBank 句级标注传统, 对新闻句式的适配性与 finbert_cn 的 finbert-tone 谱系形成模型架构与训练语料双重差异化, 因此两者的 iyvol 并排是真正独立训练路径上的互证而非同源复制。轨道侧: full 轨为标题 prepend 加全文正文, 是留篇门控 (full-only, 2026-06-29) 定义文章宇宙的轨道, 月覆盖最优、单篇 net_tone 噪声最小, 因此本列是三轨中 iyvol 的统计功效最高版本, 也是机制回归与异质性切分的首选列。指标侧: 本列度量该银行该年月度净语调均值序列扣除抽样噪声后的真实波动, 公式 sqrt(max(0, Var1(m_t) − (1/T)·Σ_t σ̂²/n_t)), 其中月均值方差与池化文章级方差均取 ddof=1, 校正项覆盖含单篇月在内的全部有效月 — 单篇月均值噪声最大恰最须校正; 门槛 T≥3 且至少一月 n_t≥2, 不满足置 NaN 宁缺勿噪。经济含义: 高值表示该年媒体对该银行金科叙事月度口径反复摇摆 (信息环境不稳定), 低值表示叙事平稳; 与均值语调正交的这一二阶矩通道在 Fang, Wang, Wang & Yuan (2024) 与 Cookson, Fox, Gil-Bazo, Imbet & Schiller (2026) 所代表的银行叙事-稳定性文献中有直接构念对应。机制回归中本列的典型角色是信息环境不确定性通道的代理: 若银行金科叙事的均值效应部分经由预期不稳定起作用, 控制年均语调后 iyvol 应保留独立解释力; 反之若控制均值后不显著, 则支持效应集中于叙事水平而非叙事路径的解读。与结果变量的对接上, 存款端与融资成本类结果对叙事摇摆的敏感度有直接文献先例, 而投资与创新类结果更可能仅响应叙事水平, 本列在不同论文中的预期作用强度因此不同。白话说, 这一列衡量的是今年媒体夸它骂它是不是变来变去: 扣噪声的意义在于, 报道少的银行哪怕口风稳定, 少数几篇的偶然措辞也会让原始月度波动看起来很大, 校正就是把这种样本少造成的假波动从真实口风摇摆里剥掉, 剥完还剩下的才算数。使用口径: 与 finbert_cn/finbert2 的同名列互为稳健性、不分主次, 三模型各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型推断走 rwolf FWER, 比较只用标准化 β。与跨年 rolling 的 tone_volatility 真正交, 与同年截面离散的 pos_std 仅校正后近似正交。非嵌入 carve-out, 无 _lg 孪生。开发机早期试跑 T=2 下本列全 NaN 属预期退化, 生产 T=19 正常出值。门槛与样本框补充: 本列要求有效月三个月以上且至少一个月两篇以上, 低覆盖银行系统性缺失, 涉及本列的回归应报告门槛通过率并做覆盖强度控制的稳健性; merge 时序在零填之后, 无新闻格为 NaN 而非零, 描述统计的缺失率读数因此混合了无新闻与门槛不足两种机制, 细分时以年篇数辅助判别。另外, 本列与本模型 iytrend_full 的联合读法值得单独一提: 高波动低斜率提示往复震荡型叙事, 低波动高斜率绝对值提示单调重估型叙事, 两种形态对信息环境不确定性的含义不同, 机制解释时不应只看单列, 联合呈现两列的散点分域是描述统计部分的推荐图式。

## VAR: fin_sent_zh_nt_iyvol_ss

【变体差分】
本列是 fin_sent_zh 模型年内净语调波动的 ss 轨变体, tier=standard。差分维度为文本轨道: 输入为 fin_sent_zh 在 ss 轨 (标题 prepend 加银行与金科词同句 ±1 句窗片段) 上的正负概率列。ss 回退语义严格镜像 ctx 口径: 无银行金科同句共现的文章其 content_ss 回退为全文 body 且 ss_is_fallback=True, 与 full 共享 n_articles 分母; FINTECH_AC 不可用时全行 fallback 优雅降级。因此本列的同句窄靶波动解释强度随该年非 fallback 占比而变。计算与门槛同 canonical: 噪声校正月均值标准差, T≥3 且 ≥1 月 n_t≥2。ss 轨文本最短、截面噪声最大, 校正项相应最大, 校正设计对本轨的价值最高 — 未校正的朴素月度标准差在 ss 轨会严重虚高。行宇宙为 full-only 留篇集子集。与 full/ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列是波动构念在最窄靶语境下的极限检验臂, 与 full/ctx 的梯度对照可粗略分解叙事摇摆的来源层次 (全文背景、实体邻近、同句并提三层)。fallback 占比高的年份本列语义向 full 收敛, 梯度解读须逐年结合 fallback 诊断量; 可估格数在三轨中最少、功效最低属结构性预期, 空结果不构成反证, 主结论亦从不依赖本列单独显著。生产语料后期年份同句共现率上升, 本列可估覆盖随之改善; 报告层只用标准化系数, 原始量级不作解释对象。

## VAR: finbert2_nt_iytrend_ctx

【变体差分】
本列是 finbert2 模型年内净语调趋势的 ctx 轨变体, tier=standard。双重差分维度: 模型侧, finbert2 是本项目私有微调的本地二分类模型 (负面/正面, 经 FINBERT2_MODEL_DIR 解析), 其 net_tone = P(正面) − P(负面) 因无中性类吸收概率质量而方差结构系统性大于三分类模型, 跨模型禁比原始水平只比标准化系数; per-model 独立降级口径下, FINBERT2_MODEL_DIR 未配置或路径无效时该模型优雅跳过, 本列全 NaN 但在位, 不连坐另两模型 (区别于 co-primary 嵌入的 both-or-neither)。轨道侧, ctx 轨输入为标题 prepend 加银行实体上下文窗口文本上的推理概率, 度量实体邻近文本净语调的月度线性漂移。公式与门槛 (闭式 OLS 斜率, 有效月 T≥6, 禁 lstsq/polyfit) 同家族 canonical。行宇宙为 full-only 留篇集子集 (conditional-on-full)。与 finbert2 的 full/ss 轨及另两模型的同名列均互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列把私有模型臂与实体窗口轨相交, 检验域内最适模型口径下的叙事漂移是否在剔除背景文本后保留; 与 finbert2 的 full 轨对照隔离窗口效应, 与另两模型的 ctx 轨对照隔离模型效应, 两个方向的对照各自并排检验, 不做联合工具。二分类极化叠加 ctx 短文本使本列的斜率标准误在十八列中偏宽, 显著性门槛难度最高属结构性预期。

## VAR: finbert2_nt_iytrend_full

【变体差分】
本列是 finbert2 模型年内净语调趋势的 full 轨, tier=core (类别6扩围①, 2026-07-10 签核, 年内趋势与 iyvol 并列第二测度)。模型侧差分是本列解释的重心: finbert2 是三模型中唯一的项目私有微调臂, 本地二分类 (负面/正面), 经环境变量 FINBERT2_MODEL_DIR 解析加载, 与两个 HuggingFace 公开模型构成私有-公开互证结构 — 私有模型在本项目银行金科语料分布上适配最好, 公开模型保证第三方可复现性, 两类并排是 per-model 稳健性设计的核心价值。二分类结构的三点计量后果必须写明: 其一, net_tone 在二分类归一化下两概率和恒为 1, net_tone = 2P(正面) − 1, 原始方差天然大于有中性类吸收概率质量的三分类模型, 因此跨模型比较本列与 finbert_cn/fin_sent_zh 同名列只准比 z-score 标准化后的回归系数, 禁比原始水平与原始斜率大小; 其二, 其中性概率列是全 NaN 占位 (tone_berts 刻意非 0), 计算路径只读正负两列, 凭列存在判类数会静默清零, 这是被 gate 封死的历史缺陷路径; 其三, per-model 独立降级 — FINBERT2_MODEL_DIR 缺席时仅本模型 6 列全 NaN 在位, 另两模型照常, 不适用 both-or-neither。轨道与指标侧: full 轨为标题 prepend 加全文, 即留篇门控 (full-only) 的宇宙轨道, 月覆盖最优; 指标为月度净语调均值对月号的闭式 OLS 斜率 (T≥6, 禁 lstsq 保确定性), 度量该年私有模型口径下媒体叙事的逐月转向速度。解释与使用要点: 本列的独特价值与独特义务同源于模型的私有性 — 价值在于 finbert2 的微调语料与本项目语料分布最接近, 其判类的域内效度预期最高; 义务在于可复现性披露, 论文数据附录须说明该模型不可公开分发, 第三方复现只能核对另两个公开模型臂, 这正是三模型矩阵设计中公开臂存在的理由, 也是本列永远不单独承担结论的原因。三模型符号一致而量级有序 (二分类最大) 是标度差异的正常表现, 符号冲突才构成测量分歧信号, 后者应触发对该年该银行文章的逐篇审计。白话说, 这一列用项目自家训练的判官看今年口风是越来越好还是越来越坏: 自家判官最懂这批语料, 但外人没有这个判官, 所以它的结论必须与两个公开判官的结论摆在一起看, 谁也不压谁一头。与本模型 iyvol_full 联用同样可区分单调转向与往复震荡两种叙事形态。使用口径: 与另两模型同名列互为稳健性、不分主次, 三模型各自 just-identified 并排, 禁混同一 over-identified Hansen J; 跨模型联合显著性走根级 rwolf FWER 模板。非嵌入 carve-out 无 _lg; 开发机早期试跑 T=2 全 NaN 属预期退化。门槛与缺失口径补充: 有效月不足六个月置 NaN 之外, 本列还多一层模型级缺席 — 生产环境未配置模型目录的运行批次中本列整列 NaN, 使用前应以列级非缺失率确认该批次模型在位; 由此本列的缺失来源有四种 (无新闻、门槛不足、推理失败剔除、模型缺席), 是十八列中缺失机制最复杂的趋势列, 描述统计与样本框叙述须逐一区分, 不可笼统归为数据稀疏, 复现包文档对该四分类缺失口径有对应说明段。最后就本列的外部对话价值再补一句: 私有二分类臂在本项目银行金科语料上的域内适配虽最优, 但正因不可分发, 它在与 Huang, Wang & Yang (2023) FinBERT 谱系或 Chen, Granville & Matousek (2026) 大模型解码路线的对表中无法充当引用锚, 该职责由公开的 finbert_cn 与 fin_sent_zh 臂承担; 本列的贡献是把公开臂的趋势结论在最贴合语料的私有测量上再复认一遍, 三者符号一致才构成完整证据链, 这也是本列被签核为 core 却永不单独承担结论的方法学理由。

## VAR: finbert2_nt_iytrend_ss

【变体差分】
本列是 finbert2 模型年内净语调趋势的 ss 轨变体, tier=standard。双重差分: 模型侧, finbert2 为私有本地二分类模型, net_tone 方差结构与三分类不可比 (跨模型只比标准化系数), FINBERT2_MODEL_DIR 缺席时本列全 NaN 在位、per-model 独立降级不连坐; 轨道侧, ss 轨输入为银行与金科词同句 ±1 句窗片段 (标题 prepend), 回退语义镜像 ctx — 无同句共现时 content_ss 回退全文 body 且 ss_is_fallback=True, 与 full 共享 n_articles 分母, FINTECH_AC 不可用时全行 fallback 优雅降级。因此本列在语义上是私有模型读最窄靶文本的年内趋势, 受 fallback 稀释影响需逐年解释。公式与门槛同 canonical: 月均值对月号闭式 OLS 斜率, 有效月 T≥6, 禁 lstsq/polyfit 保 golden 确定性。行宇宙为 full-only 留篇集子集。与 full/ctx 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列是模型维 (私有二分类) 与轨道维 (同句窄靶) 双重最严苛设定的交点, 在稳健性矩阵中充当压力测试臂 — 若叙事漂移效应连本列都保留符号一致, 结论的测量稳健性证据链最完整; 若仅本列失效, 优先归因于二分类极化与 ss 短文本叠加的噪声, 而非构念失效。fallback 占比与模型在位率是本列使用前的双重诊断项。报告层以与另五个 ss 臂及私有臂并排的符号一致性为主, 无须单独解释量级。

## VAR: finbert2_nt_iyvol_ctx

【变体差分】
本列是 finbert2 模型年内净语调波动的 ctx 轨变体, tier=standard。双重差分: 模型侧, finbert2 私有二分类, net_tone = 2P(正面) − 1 的方差结构系统性偏大, 其 iyvol 原始水平不可与三分类模型直接比较, 只比各自回归的标准化 β; per-model 独立降级, 模型缺席时本列全 NaN 在位。轨道侧, ctx 轨为标题 prepend 加银行实体上下文窗口, 文本较短、文章级截面方差更大, 噪声校正项相应更大, 校正后才可跨轨解释。公式同 canonical: 月均值序列方差减池化抽样噪声后开方, sqrt(max(0, Var1(m_t) − (1/T)·Σ σ̂²/n_t)), 双 ddof=1, 校正项含单篇月; 门槛 T≥3 且 ≥1 月 n_t≥2, 否则 NaN 宁缺勿噪。行宇宙为 full-only 留篇集子集 (conditional-on-full 测度轨)。与 finbert2 的 full/ss 及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列在波动构念上叠加私有模型与实体窗口双重变体, 其原始水平受二分类极化 (抬高) 与噪声校正 (压低) 两股方向相反的力, 净效应不可先验判断, 故本列绝不与任何其它列比原始量级, 只在标准化系数层参与三模型三轨矩阵的符号与显著性一致性检验; 与 finbert2 的 full 轨对照可检验背景文本对私有模型口径波动读数的贡献方向。模型缺席批次整列 NaN, 使用前查列级非缺失率; 可估格数介于同模型 full 与 ss 轨之间, 覆盖诊断随批次报告。

## VAR: finbert2_nt_iyvol_full

【变体差分】
本列是 finbert2 模型年内净语调波动的 full 轨, tier=core (类别6签核, BERT 分布形状族年内波动 canonical 之一)。模型侧: finbert2 是项目私有微调的本地二分类臂, 在三模型矩阵中提供最贴合本语料分布的测量, 与公开可复现的 finbert_cn/fin_sent_zh 构成私有-公开互证; 二分类无中性缓冲使其逐篇 net_tone 更极化, 月均值序列的原始波动水平天然高于三分类模型 — 这不是数据异常而是测量标度差异, 故跨模型铁律为禁比 iyvol 原始水平、只比 z-score 标准化后的回归系数 (Table A5 口径), 跨模型联合推断走根级 rwolf FWER 模板。降级口径: FINBERT2_MODEL_DIR 未配置或无效时该模型整族优雅跳过, 本列全 NaN 但在位, 另两模型照跑, per-model 独立降级明确区别于 co-primary 嵌入的 both-or-neither 连坐。轨道侧: full 轨为标题 prepend 加全文正文, 即留篇门控 (full-only, 2026-06-29) 定义宇宙的轨道, 无 conditional-on-full 缩减, 月覆盖与统计功效在三轨中最高。指标侧: 噪声校正后的月均值净语调标准差, sqrt(max(0, Var1(m_t) − (1/T)·Σ_t σ̂²/n_t)), 月均值方差与池化文章级方差双 ddof=1, 校正项覆盖全部有效月含单篇月, 门槛 T≥3 且至少一月 n_t≥2。解释与使用要点: 二分类结构对波动测量的影响比对趋势测量更深 — 无中性类意味着模棱两可的文章也被迫在正负之间分配全部概率质量, 逐篇 net_tone 向两端扩散, 月内文章级方差与月间均值方差同时被放大, 这是测量标度性质, 噪声校正无法也不应消除它。与此相对, 本列在模型内的跨银行跨年比较完全合法, 且由于私有模型的域内适配, 其对本语料真实语调摇摆的信噪比预期不低于公开模型。使用建议: 在三模型并排的稳健性表中, 本列承担域内最适模型是否复认叙事不稳定效应的检验职责; 若另两模型显著而本列不显著, 优先怀疑二分类极化引入的额外噪声稀释了功效, 而非效应不存在, 此时可报告三模型标准化系数的置信区间重叠作为一致性证据。白话说, 这个模型是非黑即白的判官, 判得更极端, 月度口风的起伏读数天然偏大, 所以看它的数值不能和另外两个允许中立的判官直接比大小, 只能比方向和标准化后的强度。merge 在零填之后, 无新闻格天然 NaN; 开发机早期试跑 T=2 快照下本列全 NaN 属预期退化, 生产 T=19 语料正常出值, 严禁以开发快照缺失率推断生产质量。与另两模型及另两轨的同名指标互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。非嵌入 carve-out 无 _lg。门槛口径与家族一致: 有效月三个月以上且至少一月两篇以上, 否则 NaN 宁缺勿噪; 与本模型 iytrend_full 相同, 本列的缺失来源含模型级缺席一层, 使用前查列级非缺失率确认模型在位。另须留意池化方差同质假设在二分类模型下的含义: 极化分布使月内文章级方差的月间差异可能更大, 同质池化的近似误差在本列相对更高, 这也是本列读数以符号与标准化强度为使用层、不作量级精读的又一理由; 跨模型口径下它与另两列的符号一致性是主要证据形式。

## VAR: finbert2_nt_iyvol_ss

【变体差分】
本列是 finbert2 模型年内净语调波动的 ss 轨变体, tier=standard。双重差分: 模型侧, finbert2 私有二分类, 逐篇 net_tone 极化、方差标度大, 跨模型禁比原始水平只比标准化系数; FINBERT2_MODEL_DIR 缺席时本列全 NaN 在位, per-model 独立降级不连坐另两模型。轨道侧, ss 轨输入为银行与金科词同句 ±1 句窗片段 (标题 prepend), 回退语义严格镜像 ctx: 无同句共现的文章 content_ss 回退全文 body 且 ss_is_fallback=True, 与 full 共享 n_articles 分母, FINTECH_AC 不可用时全行 fallback。ss 文本最短, 文章级截面噪声最大, 池化校正项在三轨中最大, 未校正的朴素月度标准差在本轨虚高最严重, 故本列必须在校正框架下解读。公式与门槛同 canonical: T≥3 且 ≥1 月 n_t≥2, 否则 NaN。行宇宙为 full-only 留篇集子集。与 full/ctx 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列是十八列矩阵中噪声环境最严苛的一格 (二分类极化、最短文本、最大校正项、最少可估格), 其设计角色是下界检验 — 在最不利测量条件下效应符号是否幸存; 主结论从不依赖本列单独显著。解释本列时三个诊断量缺一不可: 该年 fallback 占比、模型在位率、iyvol 门槛通过率, 三者共同决定该格读数的证据权重; 生产语料后期年份可估覆盖随同句共现率上升而改善。

## VAR: finbert_cn_nt_iytrend_ctx

【变体差分】
本列是 finbert_cn 模型年内净语调趋势的 ctx 轨变体, tier=standard。差分维度为文本轨道 (模型内差分详见 full 轨核心节): finbert_cn 对应 HuggingFace 公开模型 yiyanghkust/finbert-tone-chinese, 三分类 (中性/正面/负面), 是 FinBERT 谱系 (Huang, Wang & Yang (2023) 范式) 的中文语调分支。ctx 轨输入为标题 prepend 加银行实体上下文窗口文本, 度量该银行邻近语境净语调的月度线性漂移, 对合报多家银行的长文语调串扰更稳健, 但单篇文本短、噪声大。公式同 canonical: 月均值对实际月号的闭式 OLS 斜率, 有效月 T≥6, 求和项闭式实现禁 lstsq/polyfit 保 golden 逐位确定性。行宇宙口径: 留篇门控 full-only, ctx 为 conditional-on-full 测度轨, 行宇宙为 full 留篇集子集。与 finbert_cn 的 full/ss 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列以文献主流模型复认窗口稳健性, 是 ctx 轨三个模型臂中外部可比性最强的一列; 与 full 轨结论对照可判别叙事漂移的文本层次归属, 与另两模型 ctx 列对照可判别模型谱系敏感性, 两方向对照均为并排检验不做联合工具。三分类中性缓冲使本列斜率对个别极端文章更钝感, ctx 短文本的噪声放大效应因此比二分类臂温和。实操上本列与 full 轨的斜率符号一致率是窗口稳健性一节的首要报告量, 符号翻转格应逐篇审计背景段落语调后再定性; 可估格数与 full 轨同源但功效略低属预期。

## VAR: finbert_cn_nt_iytrend_full

【变体差分】
本列是 finbert_cn 模型年内净语调趋势的 full 轨, tier=core (类别6扩围①, 2026-07-10 签核: 年内趋势与年内波动并列 BERT 分布形状族第二测度)。模型侧: finbert_cn 对应 yiyanghkust/finbert-tone-chinese, 是学术界使用最广的 FinBERT 中文语调变体, 承袭 Huang, Wang & Yang (2023) 所示范的金融领域预训练加语调微调范式, 三分类输出 (中性/正面/负面); 在三模型矩阵中它是文献主流谱系臂, 与训练路径不同的 fin_sent_zh (Financial PhraseBank 谱系) 和私有 finbert2 形成三条独立测量路径, 三者并排即 BERT 支的 per-model 稳健性梯子。其 net_tone = P(正面) − P(负面), 中性类吸收概率质量使净值分布比二分类模型温和, 跨模型比较须 z-score 标准化。轨道侧: full 轨为标题 prepend 加全文正文, 是留篇门控 (full-only, 2026-06-29) 定义文章宇宙的轨道, 无 conditional-on-full 缩减, 月覆盖与有效月数在三轨中最优, T≥6 的趋势门槛最易满足, 因此本列是 finbert_cn 趋势指标的统计功效首选。指标侧: 该银行该年月度净语调均值对实际月号 x ∈ {1..12} 的闭式 OLS 斜率, 正值为叙事逐月转暖、负值为逐月转冷; 与 Marchetti, Tarducci & Branzoli (2025) 直接测量银行相关媒体语调时间漂移的构念同源。实现用求和项闭式公式, 禁 lstsq/polyfit (LAPACK 破 BLAS 确定性口径); 有效月不足 6 置 NaN; merge 在零填后, 无新闻格天然 NaN。解释与使用要点: 本列在三模型矩阵中承担与外部文献对话的接口职责 — FinBERT 谱系是金融文本情感的事实标准, 审稿人若要求与既有中文金融情感研究对表, 本列是首选引用列; 论文报告三模型结果时本列常被置于稳健性表首列, 但这只是展示顺序惯例, 计量地位上三模型严格 co-equal 不分主次, 不存在以本列为准的层级。测量链条上须留意三分类中性类的作用: 大量金科新闻是中性的事实报道, 中性概率吸收后正负概率均被压缩, 逐篇 net_tone 集中于零附近, 月均值序列相对平缓, 有效月内的斜率估计因此比二分类模型更不易受个别极端文章拉动, 代价是对温和语调变化的灵敏度略低。白话说, 这一列用最主流的金融情绪模型看今年口风从年头到年尾是转好还是转坏, 转好为正、转坏为负, 数值大小是每个月平均变化的速度; 它要求至少六个有效月才出值, 保证读数不是两三个月的偶然连线。使用口径: 与另两模型同名 full 列互为稳健性、不分主次, 三模型各自 just-identified 并排, 禁混同一 over-identified Hansen J, 跨模型联合推断走根级 rwolf FWER; 与本模型 iyvol_full 联用可区分单调转向 (高斜率绝对值、中低波动) 与往复震荡 (低斜率、高波动) 两种叙事形态, 两者对信息环境的含义不同 — 前者是可预期的方向性重估, 后者是持续的不确定性。非嵌入 carve-out 无 _lg; 开发机早期试跑 T=2 全 NaN 属预期退化, 生产 T=19 正常出值。入样机制补充: 有效月门槛六个月使年中新入样银行首年多为 NaN; 本列缺失混合无新闻、门槛不足与失败剔除三种来源, 细分以年篇数与有效月数辅助判别。作为公开模型列, 本列亦是复现包中第三方可完整重算的趋势臂, 与私有 finbert2 臂形成可复现性互补, 数据附录的模型披露段以本列与 fin_sent_zh 臂为公开锚。

## VAR: finbert_cn_nt_iytrend_ss

【变体差分】
本列是 finbert_cn 模型年内净语调趋势的 ss 轨变体, tier=standard。差分维度为文本轨道: ss 轨输入为标题 prepend 加银行与金科词同句 ±1 句窗片段, 是语义靶向最窄的轨道, 度量银行与金科在同一句被并提的语境净语调的月度漂移。回退语义严格镜像 ctx 口径: 无银行金科同句共现的文章其 content_ss 回退为全文 body 且 ss_is_fallback=True, 与 full 轨共享 n_articles 分母; FINTECH_AC 不可用时全部行 fallback 为 True 优雅降级。高 fallback 年份本列语义趋近 full 轨, 窄靶解释须结合 fallback 占比。模型侧 finbert_cn 为公开三分类模型 (yiyanghkust/finbert-tone-chinese), 无目录降级路径。公式与门槛同 canonical: 闭式 OLS 斜率, 有效月 T≥6, 禁 lstsq/polyfit。行宇宙为 full-only 留篇集子集 (conditional-on-full)。与 full/ctx 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列检验主流模型口径下的叙事漂移在同句并提的最强关联语境中是否成立; 中性缓冲加窄靶文本的组合使其读数保守, 显著结果的证据价值因此更高。与 full 轨差异的解读须拆分窄靶语义与 fallback 稀释两个来源, 逐年 fallback 占比为必读诊断; 生产语料后期年份同句共现率上升, 本列窄靶解释力随之增强。本列与 finbert_cn 家族其余五列共享模型谱系, 跨列一致性构成模型内证据链。

## VAR: finbert_cn_nt_iyvol_ctx

【变体差分】
本列是 finbert_cn 模型年内净语调波动的 ctx 轨变体, tier=standard。差分维度为文本轨道: 输入为 finbert_cn (公开三分类, yiyanghkust/finbert-tone-chinese) 在 ctx 轨 (标题 prepend 加银行实体上下文窗口) 上的正负概率列, 度量实体邻近文本净语调月均值序列的噪声校正波动。公式同 canonical: sqrt(max(0, Var1(m_t) − (1/T)·Σ σ̂²/n_t)), 月均值方差与池化文章级方差双 ddof=1, 池化仅用 n_t≥2 的月而校正项覆盖全部有效月含单篇月; 门槛 T≥3 且至少一月 n_t≥2, 否则 NaN。ctx 文本短于全文, 逐篇 net_tone 截面噪声更大, 校正项相应更大 — 未校正的朴素标准差会使本轨波动机械性高于 full 轨, 校正后的跨轨差异才可解释为窗口内外真实语调动态差。行宇宙为 full-only 留篇集子集 (conditional-on-full 测度轨)。与 full/ss 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列以主流三分类模型度量实体邻近文本的语调摇摆, 是 ctx 轨波动臂中噪声结构最温和的一列 — 中性缓冲压低逐篇极化, 校正项相对较小, 校正前后差异的诊断意义清晰。与 full 轨对照分解摇摆的文本层次来源, 与另两模型 ctx 列对照检验谱系敏感性, 均为并排检验不做联合工具。报告时以标准化系数与 full 轨并排呈现, 原始量级差异属窗口文本长度的结构性产物, 不作解释对象; 可估格数介于 full 与 ss 轨之间。

## VAR: finbert_cn_nt_iyvol_full

【变体差分】
本列是 finbert_cn 模型年内净语调波动的 full 轨, tier=core (类别6签核, BERT 分布形状族年内波动 canonical 之一)。模型侧: finbert_cn (yiyanghkust/finbert-tone-chinese) 是 FinBERT 主流谱系的中文语调三分类模型, 在三模型矩阵中承担文献可比性角色 — 使用同谱系模型的外部研究最多, 本列的量级与行为可与 Huang, Wang & Yang (2023) 谱系下的既有中文金融情感应用相互印证; 三分类的中性类吸收概率质量, 其 net_tone 分布较二分类 finbert2 温和, 跨模型比较仅限 z-score 标准化系数 (Table A5 口径), 联合显著性走根级 rwolf FWER 模板 (Romano & Wolf (2005))。作为 HuggingFace 公开模型, 无 FINBERT2_MODEL_DIR 类降级路径, 缺失仅来自逐篇推理失败哨兵; 本地重跑须置 HF 离线开关避免外网拉取失败。轨道侧: full 轨为标题 prepend 加全文正文, 即留篇门控 (full-only, 2026-06-29) 定义宇宙的轨道, 月覆盖最优, T≥3 的波动门槛最易满足, 统计功效在三轨中最高。指标侧: 该银行该年月度净语调均值序列扣除抽样噪声后的标准差, 公式 sqrt(max(0, Var1(m_t) − (1/T)·Σ_t σ̂²/n_t)), 双 ddof=1, 校正项含单篇月 (单篇月噪声最大恰最须校正), 门槛不满足置 NaN 宁缺勿噪; 噪声校正消除了低覆盖银行波动虚高的机械偏误, 使本列与媒体覆盖强度的相关性反映真实动态而非抽样噪声。解释与使用要点: 本列是三模型波动指标中与外部文献可比性最高的一列, 其原始量级因中性缓冲而在三模型中最温和, 但这不影响序数信息 — 模型内跨银行跨年的高低排序与标准化系数才是使用层, 原始水平仅供描述统计。使用场景上, 本列适合作机制与异质性分析的工作马: 信息环境不确定性通道的机制回归 (控制年均语调后检验 iyvol 的独立解释力)、高叙事不稳定子样本的异质性切分、以及与年均语调交互 (同样的负面均值, 摇摆路径与单调路径的效应差) 三种用法都以本列为默认起点, 再以另两模型复认。与上游测量的关系: finbert_cn 的判类在中性密集的语料上尤其稳健, 其月均值序列的波动更多来自真实的正负文章构成变化而非单篇概率的抖动, 这使本列的噪声校正项相对较小、校正前后差异温和, 与 ss 轨或二分类模型形成对照 — 校正前后差异的跨列比较本身就是一个有用的诊断: 校正吞掉大半波动的列, 其未校正版本主要在测量抽样噪声。白话说, 这一列是用最主流的金融情绪模型看今年口风稳不稳, 而且已经把报道少导致的假波动扣掉了, 剩下的高读数可以放心解释为媒体口径真的在摇摆。与另两模型及另两轨同名指标互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。非嵌入 carve-out 无 _lg; 开发机早期试跑 T=2 全 NaN 属预期退化, 生产 T=19 正常出值。作为公开模型列, 本列同时是复现包中第三方可完整重算的波动臂, 与私有 finbert2 臂形成可复现性互补。缺失口径: 本列缺失混合无新闻与门槛不足两种机制, 以年篇数辅助判别; 门槛通过率随媒体覆盖强度上升, 生产语料后期年份的可估格覆盖显著更好。补充一点跨轨诊断的可操作用法: 本列 (full 三分类) 的噪声校正项通常在十八列中偏小, 若在某银行某年出现校正吞掉大半原始波动的情形, 则提示该格的未校正波动主要源自抽样噪声而非真实叙事摇摆, 此类格的高原始读数应被判为噪声伪迹而非实质信号; 反之校正前后差异微小的格, 其波动读数的信噪比高、可作为机制回归的重点样本。这一校正吞噬比的跨列比较 (full 对 ss、三分类对二分类) 本身即是一个免费的测量质量诊断量, 建议在描述统计附录中随本列一并报告。

## VAR: finbert_cn_nt_iyvol_ss

【变体差分】
本列是 finbert_cn 模型年内净语调波动的 ss 轨变体, tier=standard。差分维度为文本轨道: ss 轨输入为标题 prepend 加银行与金科词同句 ±1 句窗片段上的 finbert_cn 正负概率, 度量最窄靶语境净语调的月度摇摆。回退语义严格镜像 ctx: 无银行金科同句共现时 content_ss 回退为全文 body 且 ss_is_fallback=True, 与 full 共享 n_articles 分母; FINTECH_AC 不可用时全行 fallback 优雅降级 — 高 fallback 年份本列语义向 full 轨收敛, 窄靶波动解释须结合 fallback 占比。公式与门槛同 canonical: 噪声校正月均值标准差, sqrt(max(0, Var1(m_t) − (1/T)·Σ σ̂²/n_t)), T≥3 且 ≥1 月 n_t≥2。ss 文本最短、截面噪声最大, 池化校正项在三轨中最大, 校正框架对本轨的必要性最高。行宇宙为 full-only 留篇集子集 (conditional-on-full)。与 full/ctx 轨及另两模型同名列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。使用定位: 本列组合主流模型与最窄靶轨道, 在三轨梯度对照 (full 全文、ctx 实体邻近、ss 同句并提) 中提供构念纯度最高的波动读数; 中性缓冲使其在 ss 短文本环境下比二分类臂稳定, 是 ss 轨三个模型臂中的功效首选。fallback 占比与门槛通过率仍是使用前的必读诊断; 空结果在开发快照属预期, 生产语料后期年份的可估格覆盖显著改善。本列与 finbert_cn 家族其余五列的跨列一致性构成模型内证据链, 其中本列承担窄靶下界一环, 空结果不构成反证。

<!-- rendered-citations:begin -->
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, 102325. https://doi.org/10.1016/j.intfin.2026.102325
Cookson, J. A., Fox, C., Gil-Bazo, J., Imbet, J. F., & Schiller, C. (2026). Social media as a bank run catalyst. Journal of Financial Economics, 176, 104218. https://doi.org/10.1016/j.jfineco.2025.104218
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, 101126. https://doi.org/10.1016/j.gfj.2025.101126
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
<!-- rendered-citations:end -->
