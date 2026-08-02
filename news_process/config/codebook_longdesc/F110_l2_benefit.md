---
family_id: F110
columns:
- benefit_neg_frac_ctx
- benefit_neg_frac_full
- benefit_neg_frac_lg_ctx
- benefit_neg_frac_lg_full
- benefit_neg_frac_lg_ss
- benefit_neg_frac_ss
- benefit_pos_frac_ctx
- benefit_pos_frac_full
- benefit_pos_frac_lg_ctx
- benefit_pos_frac_lg_full
- benefit_pos_frac_lg_ss
- benefit_pos_frac_ss
- benefit_std_ctx
- benefit_std_full
- benefit_std_lg_ctx
- benefit_std_lg_full
- benefit_std_lg_ss
- benefit_std_ss
unit: 无量纲比例/离散度 (pos_frac 与 neg_frac 为文章占比 ∈ [0,1]; std 为 bank-year 内投影得分样本标准差, 理论域 [0,1], 单观测 bank-year 为 NaN)
formula: "文章级 a_j = cos(s_j, p), p = mean(POSITIVE_ANCHORS 嵌入) - mean(NEGATIVE_ANCHORS 嵌入) (Jha-Liu-Manela 双极锚点投影); bank-year 聚合: benefit_pos_frac = mean(a_j > c), benefit_neg_frac = mean(a_j < c), c = 冻结 pooled median (每 score 列独立条目, _benefit_center_sidecar.json, 记 model_id 且不匹配即 fail-loud); benefit_std = std(a_j, ddof=1), 单观测保持 NaN 不 fillna(0)"
producer: news_process/pipeline/features/benefit_society.py::compute_benefit_society_panel (审计对照链路 = pipeline/features/benefit_society_audit_combined.py, audit-only, 产 80_alt_anchor_and_placebo_panel.parquet, 不触碰主面板)
upstream:
- 14_materialize_ctx 物化的三轨文本列 content_full / content_ctx / content_ss (含 ss_is_fallback)
- embedding_engine.embed_texts 统一嵌入引擎 (canonical = Qwen/Qwen3-Embedding-8B 4096 维; _lg = text-embedding-3-large 3072 维)
- 27_benefit_direction 方向向量 .npy 与 _lg 对偶 (各带 .sidecar.json 记 model_id/dim)
- data/processed/_benefit_center_sidecar.json (pos/neg_frac 阈值中心冻结 sidecar)
citations:
- doi: 10.1093/rfs/hhaf012
  type: journal
  authors: Jha, M., Liu, H., & Manela, A.
  year: 2026
  title: "Does finance benefit society? A language embedding approach"
  venue: Review of Financial Studies
  vol: 39
  issue: 5
  pages_or_artno: 1227-1266
- doi: "10.1080/07421222.2023.2301176"
  type: "journal"
  authors: "Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y."
  year: 2024
  title: "The Effects of Sentiment Evolution in Financial Texts: A Word Embedding Approach"
  venue: "Journal of Management Information Systems"
- doi: 10.48550/arXiv.2506.05176
  type: arxiv
  authors: Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J.
  year: 2025
  title: "Qwen3 Embedding: Advancing text embedding and reranking through foundation models"
  venue: arXiv
- doi: 10.18653/v1/2025.emnlp-main.179
  type: journal
  authors: Tang, Y., & Yang, Y.
  year: 2025
  title: "FinMTEB: Finance massive text embedding benchmark"
  venue: Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 3620-3638
- doi: 10.3386/w33651
  type: wp
  authors: Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M.
  year: 2025
  title: "Asset embeddings"
  venue: NBER Working Paper
  pages_or_artno: "33651"
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
  vol: 80
  issue: 2
  pages_or_artno: 699-754
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1146/annurev-economics-082222-074352
  type: journal
  authors: Ash, E., & Hansen, S.
  year: 2023
  title: "Text algorithms in economics"
  venue: Annual Review of Economics
  vol: 15
  pages_or_artno: 659-688
- doi: 10.1287/stsc.2023.0188
  type: journal
  authors: Westphal, J. D.
  year: 2023
  title: "Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale"
  venue: Strategy Science
  vol: 8
  issue: 2
  pages_or_artno: 221-232
- doi: 10.1093/ej/ueab104
  type: journal
  authors: Gennaro, G., & Ash, E.
  year: 2022
  title: "Emotion and reason in political language"
  venue: The Economic Journal
  vol: 132
  issue: 643
  pages_or_artno: 1037-1059
- doi: 10.1146/annurev-financial-101521-112042
  type: journal
  authors: Berg, T., Fuster, A., & Puri, M.
  year: 2022
  title: "FinTech lending"
  venue: Annual Review of Financial Economics
  vol: 14
  pages_or_artno: 187-207
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1016/j.pacfin.2020.101398
  type: journal
  authors: Cheng, M., & Qu, Y.
  year: 2020
  title: "Does bank FinTech reduce credit risk? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 63
  pages_or_artno: "101398"
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1177/0003122419877135
  type: journal
  authors: Kozlowski, A. C., Taddy, M., & Evans, J. A.
  year: 2019
  title: "The geometry of culture: Analyzing the meanings of class through word embeddings"
  venue: American Sociological Review
  vol: 84
  issue: 5
  pages_or_artno: 905-949
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: "Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure"
  venue: Organization Science
  vol: 26
  issue: 3
  pages_or_artno: 705-723
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: 67
  issue: 2
  pages_or_artno: 561-598
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
- doi: "10.1111/eufm.12509"
  type: journal
  authors: "Gorovaia, N., & Makrominas, M."
  year: 2025
  title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing"
  venue: "European Financial Management"
  one_sentence_zh: "该文用自然语言处理方法识别企业社会责任报告中的漂绿式文本策略, 为本家族占比测度中\"正面叙事高企不等于真实效益改善\"这一构念澄清提供了同期方法论近邻证据。"
- doi: "10.1057/s41310-026-00371-1"
  type: journal
  authors: "Okeke, A."
  year: 2026
  title: "Green claims and grey areas: a diagnostic tool for assessing corporate environmental misrepresentation"
  venue: "International Journal of Disclosure and Governance"
  one_sentence_zh: "该文提出一套诊断工具用于识别企业环境信息披露中的夸大与误导性表述, 为本家族\"正面叙事占比高企不必然等于真实经营效益改善\"这一构念澄清提供了最新同期证据。"
- doi: "10.3390/bdcc9100263"
  type: journal
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
  one_sentence_zh: "该文系统比较多种词嵌入与语言模型在中文财经新闻情感分类与短期股价预测任务上的表现, 为本家族在中文语料上采用嵌入投影法测度报道态度提供了同期方法论对照证据。"
new_dois:
- 10.1177/0003122419877135
- "10.1111/eufm.12509"
- "10.1057/s41310-026-00371-1"
- "10.1080/07421222.2023.2301176"
- "10.3390/bdcc9100263"
---

## CORE

该文用词嵌入方法追踪金融文本中情感表达随时间的演化及其对企业结果的影响,为本家族以嵌入投影法测度报道态度随语料演化的稳健性提供了同期方法论近邻证据。

【构念与来源】
本家族测量的构念是"媒体报道对银行金融科技活动之经营效益的态度分布形状"。它不是问媒体报道了多少金融科技 (那是注意力/曝光测度), 也不是问报道笼统上是正面还是负面 (那是通用情感测度), 而是沿着一条特定的语义轴发问: 在这篇报道的叙述里, 金融科技或数字化转型对这家银行自身的经营活动究竟是"利好"还是"损害"。方法论蓝本是 Jha, Liu 与 Manela (2026) 在其"金融是否有益社会"研究中提出的双极连续余弦投影框架: 研究者先书写若干对语义严格对偶的正极与负极锚点句 (每对之间只改动承载态度方向的关键词, 即所谓 single-word-change 对偶), 把两极锚点句分别嵌入到高维语义空间, 以正极均值向量减负极均值向量得到一条"利好经营"方向轴, 再把每篇新闻的嵌入向量对这条轴做余弦投影, 得到一个连续的文章级态度分值。该做法的更上游思想来自文化社会学中的"文化几何学"传统: Kozlowski, Taddy 与 Evans (2019) 论证了在词嵌入空间中用正负端点的差分向量可以稳定地定义诸如富裕对贫穷、高雅对通俗这类语义维度, 并且维度方向对语料扰动具有可复现性。本家族把这一"差分向量即语义维度"的思想移植到银行金融科技语境: 正极锚点句形如"金融科技提升该银行的经营效率", 负极锚点句形如"金融科技降低该银行的经营效率" (fix(D10, 2026-07-14): 示例句原带"了"字, 与实际锚点设计规则相悖——锚点须表达一般性态度/信念而非描述已完成的过去事件, 见 pipeline/features/benefit_society.py 锚点表附近注释; 十对真实锚点均无"了"字, 此处示例已订正对齐), 共十对严格对偶, 差分平均后构成本家族全部十八列的共同投影轴。家族内三个基名分工明确: benefit_pos_frac 是 bank-year 内投影得分高于阈值中心的文章占比, 捕捉"利好叙事的相对频率"; benefit_neg_frac 是低于阈值中心的文章占比, 捕捉"损害叙事的相对频率"; benefit_std 是 bank-year 内文章投影得分的样本标准差, 捕捉"媒体在该银行金融科技效益问题上的态度分歧程度"。三者与同族的连续均值测度 benefit_mean (另族登记) 互补: 均值刻画位置, 占比对刻画两尾质量, 标准差刻画散布, 合起来近似还原了 bank-year 内态度分布的形状。数据来源是本项目银行金融科技新闻语料经 stage 13 共现硬过滤与 stage 14 三轨文本物化之后的文章集合, 生产语料为 2007 至 2025 年约一千八百一十九万条中文媒体报道过滤后的银行金融科技子集; 早期试跑盘上仅有早期两年试跑切片, 覆盖率与方差结构均不能外推到生产规模。

【方法学与计算】
计算链路分文章级投影与 bank-year 聚合两段。文章级: 生产函数 compute_benefit_society_panel 对每个嵌入规格与每条文本轨道循环。嵌入规格有二, 构成 co-primary 双轨: canonical 无后缀槽使用 Qwen3-Embedding-8B 模型经硅基流动 API 取 4096 维向量 (Zhang et al. 2025 报告了该系列模型在多语言嵌入基准上的训练细节与对齐策略), _lg 槽使用 text-embedding-3-large 取 3072 维向量; 两规格各自独立嵌入锚点句、独立计算方向向量、独立投影, 全程由嵌入矩阵实际列数驱动, 维度无关, 互不掺混。选择中文能力强的嵌入模型并保留跨厂商对照, 与 Tang 与 Yang (2025) 在金融领域嵌入基准中的核心发现一致: 嵌入质量在金融文本上高度依赖领域与语言适配, 单一模型的结论需要第二嵌入空间交叉验证。方向向量计算时有锚点轴锐利度守卫: 逐对检查正极句在轴上的投影须显著为正、负极句须显著为负 (符号容差 0.03), 且每对正负投影之间的间隔不得小于 0.02, 违背即告警, 防止某对锚点在当前嵌入空间中退化失效。文本轨道有三: full 轨读 content_full (标题 prepend 到正文, 与词典法和 BERT 法同源), ctx 轨读 content_ctx (标题加目标银行实体窗口), ss 轨读 content_ss (标题加"目标银行与金融科技词同句共现"的句子及其前后一句窗口)。ss 轨回退语义镜像 ctx: 若一篇文章不存在银行与金科词同句共现, content_ss 回退为全文正文并置 ss_is_fallback 为真, 与其余轨共享同一篇数分母。行宇宙遵循 full-only 留篇门控口径: 一篇文章是否算作"银行金融科技报道"只由 full 轨的 LLM 验证结论决定, ctx 与 ss 是 conditional-on-full 的测度轨, 其行集合是 full 留篇集的子集。空文本在投影前被过滤并以 NaN 回填, 保证得分向量与文章行序等长, 由此落盘的全长嵌入矩阵与方向向量 (各带记录模型标识与维数的 sidecar) 可供审计链路在同一嵌入空间复算。聚合段: 按目标银行与年份分组, 均值与标准差直接聚合, 标准差用 ddof 为 1 的样本口径, 单观测 bank-year 保持 NaN 而非填零, 因为"只有一篇报道"与"多篇报道完全一致"在统计上不可区分, 填零会混淆两者且与同面板 LLM 情感标准差族的 NaN 口径冲突。占比对的阈值中心是本家族最重要的一处工程决策: 由于嵌入空间各向异性, 以零为界的符号阈值会使利好占比接近饱和, 作为回归自变量信息量趋零; 生产口径改以全样本投影的合并中位数为中心, 由构造保证文章级高于中心的概率约为一半, 对投影分布的左偏形态稳健。源码注释明确澄清: 这是针对偏态分布的操作化处理, 并非实现了文献中的去主成分或白化式各向异性校正, 不得作方法归属误述。中位数中心并非每次运行现算, 而是首跑计算后冻结持久化到 _benefit_center_sidecar.json, 键为具体得分列名并记录嵌入模型标识; 后续运行读冻结值, 保证语料增量不会平移全历史占比 (跨运行可比), 但披露成本是冻结值只是首跑语料的样本内中位数; 若更换嵌入模型而 sidecar 中模型标识不匹配, 程序 fail-loud 拒跑, 换嵌入前必须删除对应条目重新冻结, 防止跨嵌入空间误用旧阈值。还需注意占比列存在 mean-of-fractions 的 Jensen 效应: 各 bank-year 文章数不均, 使面板层面占比的简单平均系统性偏离文章级的一半基线, 这是聚合口径的固有性质而非缺陷。工程与可复现性层面还有四个承重细节。其一, 嵌入取数走统一引擎的纯 API 路径, 零本地模型, 超长文本按分词器口径切块后取块级向量, 单条输入的令牌上限为八千一百九十一; 全部嵌入请求经统一缓存层持久化, 缓存即复现性台账, 在离线守卫环境变量开启时缓存未命中直接抛错而不调用付费接口, 保证已播种语料可零成本字节级复算。其二, co-primary 双槽的 parity 由专门守卫段机械执行: 每条轨道检查两嵌入槽的产出覆盖, 若恰有一侧存在有效列 (另一侧因方向向量计算失败被整体跳过), 则该轨两族列一并置缺失, 从结构上排除"单边孤儿列"进入面板 — 这使任何消费两槽对照的下游分析在缺数情形下自动对称降级, 而不是静默地拿单空间结果冒充双空间验证。其三, 锚点句集合与方向向量随运行落盘并带记录模型标识、行数与维数的 sidecar 文件, 陈旧输入 fail-loud, 使审计管线 (替代锚点与安慰剂) 能严格在同一嵌入空间内复算, 排除"审计结论差异来自嵌入空间漂移"的解释。其四, 家族全部列在早期试跑切片与生产语料两种环境下的统计性状差异显著: 开发切片年份极短、覆盖稀疏, 占比与标准差的缺失率和方差均不具外推性, 任何以开发切片数值评估本家族信息量的做法都会系统性误判, 相关数值评估一律以生产面板的注入统计为准。

【文献定位】
本家族站在三支文献的交汇处。第一支是经济学文本方法论: Gentzkow, Kelly 与 Taddy (2019) 系统化了文本即数据的测量框架, Ash 与 Hansen (2023) 进一步综述了嵌入表征相对词袋方法在构念效度上的优势与陷阱; 在具体的"轴投影"技术上, Gennaro 与 Ash (2022) 用情绪极与理性极的中心差向量对国会演说做余弦投影, 与本家族的双极锚点投影在数学形式上同构, Li, Mai, Shen 与 Yan (2021) 则示范了用词嵌入从财报电话会议中提取企业文化维度的完整测量流水线, Gabaix, Koijen, Richmond 与 Yogo (2025) 把嵌入表征进一步推向资产定价对象本身, 说明嵌入式测度已进入金融学主流工具箱。第二支是媒体与金融市场文献: Tetlock (2007) 确立了媒体语气对市场的预测内容, Fang 与 Peress (2009) 证明媒体覆盖本身影响股票收益截面, Gurun 与 Butler (2012) 与 You, Zhang 与 Zhang (2018) 分别揭示了地方媒体倾向与中国语境下媒体监督的俘获问题, 提示占比测度的解释须考虑媒体激励; Fang, Wang, Wang 与 Yuan (2024) 直接在中国银行样本上把媒体情感与存款稳定性和系统性风险联系起来, 是本家族因变量端应用的近邻; Gutknecht (2025) 则显示负面企业社会责任报道的覆盖强度载有独立于均值语气的风险信息, 为把 neg_frac 与 pos_frac 分开入模而非只用净值提供了依据。第三支是银行金融科技与象征性披露文献: Berg, Fuster 与 Puri (2022) 综述了金融科技信贷的实证图景, Cheng 与 Qu (2020) 在中国银行样本上估计了银行金融科技对信用风险的影响, 界定了本家族态度测度所指向的真实经营后果; Kim 与 Lyon (2015), Westphal (2023) 与 Duchin, Gao 与 Xu (2025) 关于夸大与漂绿的证据则提醒: 媒体正面叙事占比高不等于真实效益高, pos_frac 应解释为"叙事环境"而非"经营事实", 这正是本项目把态度测度与财务结果变量分置两侧的原因。构念源头 Jha, Liu 与 Manela (2026) 与文化几何学源头 Kozlowski, Taddy 与 Evans (2019) 共同构成锚定引用。Gorovaia 与 Makrominas (2025, European Financial Management) 用自然语言处理方法识别企业社会责任报告中的漂绿式文本策略, 为本家族占比测度中"正面叙事高企不等于真实效益改善"这一构念澄清提供了同期方法论近邻证据。Okeke (2026, International Journal of Disclosure and Governance) 提出一套诊断工具用于识别企业环境信息披露中的夸大与误导性表述, 为本家族"正面叙事占比高企不必然等于真实经营效益改善"这一构念澄清提供了最新同期证据。Chuang, He 与 Hu (2025, Big Data and Cognitive Computing) 系统比较多种词嵌入与语言模型在中文财经新闻情感分类与短期股价预测任务上的表现, 为本家族在中文语料上采用嵌入投影法测度报道态度提供了同期方法论对照证据。

【识别策略定位】
在本项目的多论文架构中, 本家族三个 full 轨列是 benefit_society 衍生论文验证轨中的回归变量, 其中 pos_frac 与 neg_frac 的 full 轨列各进入三个机制与稳健性正文表模板, std 的 full 轨列作为态度分歧的 canonical 分散度统计进入分歧机制检验; 它们通常不是处理变量本身, 而是作为机制中介、分布形状控制或异质性切分变量出现, 与作为连续位置测度的 benefit_mean 并排。识别口径上须严格遵守本仓库铁律: full, ctx, ss 三条文本轨互为稳健性、不分主次, 各自以 just-identified 规格并排估计, 严禁把多轨测度混进同一条 over-identified 的 Hansen J 检验; canonical 嵌入槽与 _lg 嵌入槽是 co-primary 双轨, 同为主测度、互为稳健性, 同样各自 just-identified 并排, 严禁跨嵌入空间混进同一工具变量组; 占比对与标准差亦不应与其均值测度同时塞入一条过度识别方程去"增加工具", 因为三者由同一投影得分构造, 相关结构是机械的。列间 parity 由 both-or-neither 守卫保证: 任一轨道若只有单侧嵌入槽产出有效列, 两族同置缺失, 不留单边孤儿, 使双轨对照在任何样本切片上都成对可比。面板接入回归时, 标准差列的 NaN (单观测格) 经 listwise deletion 自然处理, 研究者应意识到这会使分歧度回归的样本偏向报道密集的银行年, 必要时以文章数加权或设最低篇数门槛做敏感性。计量形态上还有两点定位须写明。其一, 占比对是取值于零到一闭区间的有界变量, 作为解释变量入线性固定效应模型无碍, 但若研究设计把它转到被解释侧 (例如检验何种银行特征吸引更高利好叙事占比), 线性概率式近似在占比贴近边界的银行年会失真, 稳健性方向是分数响应类设定或对占比做经验分位变换后复核符号。其二, 家族全部列都是年度聚合统计, 年内的叙事时序动态 (例如负面叙事集中爆发于某一季度) 被抹平, 这既是与年度财务面板对接的口径要求, 也意味着本家族无法用于识别月度级事件研究; 涉及事件窗的假设应转用文章级投影得分自行聚合, 而不是对年度列做内插。

【与相邻测度的构念区分】
与同面板近邻测度的边界如下。其一, 与通用情感族 (LLM 三家投票、六词典、三 BERT) 的区别: 通用情感测量"这篇报道整体语气正负", 本家族测量"报道叙述中金融科技对经营的作用方向", 一篇语气克制的深度报道完全可能在通用情感上中性而在效益轴上强烈为负; 两类测度在论文中分属不同构念, 不互为替代测量。其二, 与 stage 15 金融科技强度及 stage 16 政策对齐的区别: 那两族用单极锚点算"像不像" (相似度), 本家族用双极对偶锚点算"偏向哪一端" (方向), 单极相似度没有符号语义。其三, 与 benefit 四维度六轨分解 (dimension_analysis 产出) 的区别: 维度分解把效益构念拆成若干子维度方向向量分别投影, 本家族是总轴上的分布形状统计, 两者共享嵌入引擎但方向向量与列名体系彼此独立。其四, 与 audit-only 对照面板的区别: 合并审计管线用 Jha-Liu-Manela 原文的五对 canonical 锚点与四条业务线安慰剂加一条中性基线重算平行指标, 落到独立的 80 号 parquet, 关键约束是绝不触碰主面板, 主面板消费者不应误引审计列。其五, std 与 LLM 情感 std 族的关系: 二者聚合口径刻意对齐 (ddof 为 1, 单观测 NaN), 但前者是嵌入投影的散布, 后者是离散情感标签的散布, 构念层面一个是"效益叙事分歧", 一个是"语气分歧"。

【已知局限与稳健性梯子】
已知局限与对应的稳健性安排逐条如下。第一, 锚点句选择是研究者自由度: 十对锚点由项目自拟而非 Jha-Liu-Manela 原文照搬, 对应梯子是审计链路的替代锚点臂 (原文五对 canonical 锚点重算) 与安慰剂臂 (住房贷款、信用卡、中间业务、网点渠道四条与金融科技无关的业务线轴加中性基线), 若主结论在替代锚点下翻转或在安慰剂轴上重现, 即为红旗。第二, 阈值中心的样本内冻结: 冻结保证跨运行可比但令占比定义锚定首跑语料, 语料结构大变时应重冻结并披露; 敏感性方向是以均值中心或分位数带宽复算占比。第三, 嵌入空间依赖: 单一嵌入模型的各向异性与训练语料偏好可能塑造投影分布, 对应梯子即 co-primary 双轨 — canonical 与 _lg 两个异源厂商嵌入空间并排复算全部十八列, 结论须在两空间方向一致。第四, 轨道归因宽窄: full 轨信号完整但可能混入同篇文章中与目标银行无关的叙述, ss 轨归因最严但样本经回退稀释, 三轨并排即是归因强度的敏感性梯子。第五, 分布形状统计对文章数敏感: 少篇 bank-year 的占比与标准差噪声大, 早期试跑切片上标准差列大量为 NaN 属预期退化, 生产规模下应报告按篇数分层的稳健性。第六, 中位数中心化的方法归属: 如前述, 不得声称实现了各向异性校正文献的具体算法, 论文写作须按操作化处理披露。第七, 留篇门控的厂商与口径依赖: 行宇宙由 full 轨 LLM 验证结论决定, 门控模型组合或提示词版本变更会平移全家族分母, 项目以提示词字节级冻结与缓存命中键固定来钉死该自由度, 论文披露时须说明门控口径切换 (由多轨门控收敛为 full-only) 对篇数类分母的收缩性副作用属口径变更而非数据错误。第八, 占比对的两列并非机械互补: 恰在中心上的文章两侧都不计入, 且须澄清一处易误述的实现细节: 同轨的正负两列并非各自独立冻结中心, 而是共享同一冻结中心 — 冻结 sidecar 以该轨的 benefit_score 得分列名为键, 每 score 列仅一条目, 正占比取该篇投影高于此中心、负占比取低于此中心, pos 与 neg 消费同一个 _center 值。两列之和不必为一的真实来源不是两个不同的中心, 而是严格不等式排除了恰落在中心上的文章 (高于中心用 x 大于 c, 低于中心用 x 小于 c, 等于中心 x 等于 c 者两侧皆不计入); 同表并排时应披露其高负相关的机械来源, 避免读者把两列系数解读为独立信息。第九, 单语料单语言依赖: 全部测度建立在中文媒体语料之上, 锚点句亦为中文书写, 嵌入模型的中文语义对齐质量直接进入测量误差; 跨语言迁移本家族口径时锚点须重写重验锐利度, 不能直译套用, 这也是把嵌入模型选型 (中文能力强的 canonical 槽) 与跨厂商第二空间并列为工程决策而非细节的原因。第十, 反向因果与共同冲击: 媒体效益叙事与银行真实经营间存在双向反馈, 行业级监管事件会同时驱动全体银行的叙事分布平移, 本家族列本身不承诺任何因果识别, 因果规格须依赖研究设计侧的固定效应、工具变量与事件外生性论证, 家族梯子只负责测量层面的稳健性。上述梯子彼此正交, 不交叉组合, 每一臂各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: benefit_neg_frac_ctx

【变体差分】
本列是负面效益叙事占比的 ctx 轨变体, canonical 嵌入槽 (Qwen3-Embedding-8B, 4096 维)。与家族 canonical 的 full 轨列 benefit_neg_frac_full 的唯一差分是文本轨道: 投影对象不是标题加全文, 而是 content_ctx, 即标题 prepend 之后围绕目标银行实体提及位置抽取的上下文窗口文本。ctx 轨的构念意图是消除同篇文章中与目标银行无关段落的态度污染 — 一篇综述多家银行的行业报道, 其对别家银行金融科技失败案例的负面叙述不应记到目标银行头上; ctx 轨通过只嵌入目标银行邻近语段, 把负面占比的归因收窄到"谈论该银行时的效益叙述"。代价是文本变短、语义信号变稀, 且实体窗口切割可能截断跨段落的因果论证, 使投影得分噪声升高。阈值中心与 full 轨不共享: 冻结 sidecar 的键是具体得分列名, 本列使用 ctx 轨自身投影分布的首跑合并中位数, 因此本列占比与 full 轨占比不可直接做水平比较, 只能比较各自回归中的标准化系数方向与显著性。行宇宙遵循 full-only 留篇门控: 本列的文章集合是 full 轨留篇集中 content_ctx 非空的子集, 属 conditional-on-full 测度轨。识别口径上本列与 full, ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排入模, 禁混进同一 over-identified Hansen J; 与 _lg 对偶列 benefit_neg_frac_lg_ctx 受 both-or-neither parity 守卫约束, 任一侧无效则两侧同置缺失。

## VAR: benefit_neg_frac_full

【变体差分】
本列是家族负面占比基名的 canonical 主列: full 轨, canonical 嵌入槽 (Qwen3-Embedding-8B 经硅基流动 API, 4096 维), tier 为 core, 核定依据是它作为验证轨回归变量实际进入三个机制与稳健性正文表模板。语义构成逐层拆解如下。文本层: 投影对象为 content_full, 即 stage 14 物化的"标题 prepend 到全文正文"文本, 与词典法、BERT 法及 LLM 法的 full 轨严格同源, 保证跨方法比较时文本口径恒定; 若上游缺列则回退为内联的标题拼正文构建, 语义等价。得分层: 每篇文章的嵌入向量对十对严格对偶锚点句的差分方向轴做余弦投影, 得分为正表示该篇叙事偏向"金融科技利好该行经营", 为负表示偏向"损害经营"。聚合层: 按银行年分组, 本列等于投影得分低于冻结中位数中心的文章占比, 域为零到一。中心值来自 _benefit_center_sidecar.json 中以本列对应得分列名为键的条目, 冻结自首跑全样本合并中位数并记录嵌入模型标识, 模型不匹配即 fail-loud; 因此本列的"负面"是相对语料中枢而非绝对零点的相对概念 — 低于中心意味着该篇在全语料的效益叙事光谱中落在偏损害的一半。构念解释上, 本列刻画 bank-year 报道环境中损害叙事的相对频率, 与均值测度互补: 均值可能被少数极端正面报道拉高, 而本列对两尾质量的左尾单独敏感, 呼应 Gutknecht (2025) 关于负面覆盖强度载有独立风险信息的证据; 在银行语境下, Fang, Wang, Wang 与 Yuan (2024) 显示负面媒体叙事与存款稳定性相关, 提示本列在机制检验中的位置。使用注意有三: 其一, 本列与 benefit_pos_frac_full 并非机械互补 (两者之和不必为一, 恰等于中心的文章两边都不计入), 且须澄清: 同轨的正负两列共享同一冻结中心而非各自独立中心 — 冻结 sidecar 以该轨 benefit_score 得分列名为键, 一条目, 本列与 benefit_pos_frac_full 取同一个 _center, 两列之和不必为一仅源于严格不等式排除了恰在中心上的文章, 而非两个不同中心; 回归中可同时入模但须意识到高负相关; 其二, mean-of-fractions 聚合下面板层面均值系统性偏离文章级一半基线, 属 Jensen 效应而非数据缺陷; 其三, 本列是三轨与双嵌入槽梯子的 canonical 交点, 其 ctx, ss 轨变体与 _lg 对偶各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两条并进同一 over-identified Hansen J; 留篇门控为 full-only 口径, 本列行宇宙即门控后的留篇集全体, 分母为该 bank-year 有效投影文章数。作为 core 列, 本列的审计可追溯链是家族中最完整的: 文章级全长嵌入矩阵与方向向量随运行落盘并带模型标识 sidecar, 替代锚点臂 (Jha-Liu-Manela 原文五对 canonical 锚点) 与安慰剂臂 (住房贷款、信用卡、中间业务、网点渠道四条业务线轴加中性基线) 在同一嵌入空间对本列做平行复算, 落于独立的审计 parquet 而绝不回写主面板 — 若本列的回归效应能在安慰剂轴的对应占比上重现, 说明效应源自泛化负面语气而非金融科技效益构念, 是最直接的证伪检验。经济解释上还有一个分寸须把握: 本列升高既可能反映真实经营恶化被媒体如实报道, 也可能反映媒体立场或报道议程的转移 (Gurun 与 Butler 2012 与 You, Zhang 与 Zhang 2018 记录的媒体激励问题在负面报道端同样存在), 因此涉及因果解释的规格应搭配媒体来源构成控制或来源风格类工具, 并以 ctx 与 ss 窄轨复核"负面叙事确实指向该行金融科技"而非文章其他内容。分歧于均值测度的信息增量在左尾: 当均值不变而本列上升时, 叙事分布正在向双峰演化, 此形态信号只有占比对与标准差联合才能捕捉, 这正是三个 core 列在机制表中成组出现的原因。

## VAR: benefit_neg_frac_lg_ctx

【变体差分】
本列是负面占比的 ctx 轨 _lg 变体: 文本轨道与 benefit_neg_frac_ctx 完全相同 (标题加目标银行实体窗口, conditional-on-full 行宇宙), 唯一差分是嵌入空间 — 使用 co-primary 第二槽 text-embedding-3-large (3072 维, OpenAI 系经 OpenLux 通道), 锚点句、文章文本与方向向量全部在该空间内独立重算, 与 canonical 槽零共享中间量, 维度由嵌入矩阵实际列数驱动。列名遵循 lg 中缀置于轨道后缀之前的家族命名法。阈值中心独立冻结: sidecar 键为本列对应的 _lg ctx 得分列名, 中心是该嵌入空间投影分布自身的首跑中位数, 故本列与 canonical ctx 列的占比水平不可直接比较, 跨空间只比较标准化系数的方向与稳健性。本列的方法论职能是双重稳健性交点: 相对 full 轨检验"实体窗口归因收窄是否改变结论", 相对 canonical 槽检验"结论是否被单一嵌入模型的空间几何驱动" — Tang 与 Yang (2025) 的金融嵌入基准表明不同模型在金融语义上的表征差异足以影响下游测度, 双空间并排即为此风险的显式对冲。铁律口径: canonical 与 _lg 两槽同为主测度、互为稳健性、严格 parity (both-or-neither, 本轨任一侧失效则两族同置缺失, 无单边孤儿); 两槽各自 just-identified 并排, 禁混进同一 over-identified Hansen J, 三轨之间亦同。更换嵌入模型前须删除盘上冻结中心 sidecar 对应条目, 否则模型标识守卫 fail-loud 拒跑。

## VAR: benefit_neg_frac_lg_full

【变体差分】
本列是负面占比的 full 轨 _lg 变体, 即 core 列 benefit_neg_frac_full 的 co-primary 嵌入对偶: 文本口径与之逐字节相同 (content_full, 标题 prepend 全文, full-only 留篇门控后的全体行宇宙), 唯一差分是全部嵌入运算发生在 text-embedding-3-large 的 3072 维空间 — 十对锚点句在该空间重嵌入、差分方向轴在该空间重算并通过同一套锚点锐利度守卫 (符号容差 0.03, 对间隔下限 0.02), 文章投影与冻结中心亦独立。因此本列与 canonical 列的差异纯粹反映两个嵌入空间对同一批文本与同一构念轴的几何编码差异, 是家族内最干净的"测量工具敏感性"对照: 若某一回归结论在 benefit_neg_frac_full 上显著而在本列上符号翻转, 应优先怀疑结论被 Qwen 空间的各向异性或训练语料偏好驱动, 而非经济机制本身。作为主测度之一 (co-primary 语义: 同为主测度, 非从属稳健轨), 本列在论文中的规范用法是与 canonical 列各自单独入模并排报告, 两列严禁同时作为工具或测度混进同一 over-identified Hansen J 方程; 与三轨梯子的关系同理, full, ctx, ss 各自 just-identified 并排。parity 守卫保证本列与 canonical full 列 both-or-neither: 任一嵌入槽在 full 轨失败 (如方向向量计算失败整 spec 跳过), 两族列同置缺失。占比水平因中心独立冻结而与 canonical 列不可直接比较; 跨模型汇报一律用标准化系数。审计链路对本列同样成立: _lg 方向向量与全长嵌入矩阵随 sidecar 落盘, 替代锚点与安慰剂对照在同一 _lg 空间可复算。

## VAR: benefit_neg_frac_lg_ss

【变体差分】
本列是负面占比在归因最严轨道上的 _lg 变体: 文本对象为 content_ss, 即只保留"目标银行与金融科技词出现在同一句"的句子及其前后各一句的窗口拼接 (窗口半径由过滤配置的 ss 句半径键控制, 默认一句), 嵌入与投影全部在 text-embedding-3-large 空间完成, 冻结中心以本列得分列名独立入 sidecar。ss 轨的构念意图是把效益叙事的归因锁死到"明确同时谈及该银行与金融科技"的语句邻域, 最大限度排除同篇文章中其他主题的负面情绪渗漏; 其代价由回退语义承担 — 无任何同句共现的文章, content_ss 镜像 ctx 轨回退规则退回全文正文并置 ss_is_fallback 为真, 与其余轨共享同一篇数分母, 因此本列在回退占比高的样本切片上会向 full 轨语义漂移, 解释时应结合回退率报告。行宇宙为 conditional-on-full: full 轨 LLM 门控留下的篇集中 content_ss 非空者。本列同时叠加两级稳健性差分 (最窄归因轨 × 第二嵌入空间), 是家族梯子中距 canonical 最远的角点, 其价值在于三角验证: 若 canonical full 列、canonical ss 列与本列三点符号一致, 结论对文本归因宽窄与嵌入空间选择同时稳健。铁律不变: 三轨互为稳健性不分主次, 双嵌入槽 co-primary 严格 parity (本轨 both-or-neither 守卫), 每列各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与 canonical ss 列的占比水平因中心独立不可直接比较。

## VAR: benefit_neg_frac_ss

【变体差分】
本列是负面占比的 ss 轨 canonical 嵌入变体 (Qwen3-Embedding-8B, 4096 维)。与 full 轨 core 列的差分在文本轨道: 投影对象为 content_ss — 标题 prepend 后, 仅保留目标银行与金融科技词同句共现的句子及其前后一句窗口。这是三轨中金融科技归因最严格的一条: full 轨回答"报道该银行的文章怎样叙述金融科技效益", ctx 轨回答"谈论该银行的语段怎样叙述", 本轨回答"把该银行与金融科技绑在同一句里的语句怎样叙述", 逐级收窄了"负面叙事究竟是否指向该行金融科技"的归因半径。回退语义须牢记: 无同句共现的文章不丢行, content_ss 回退为全文正文且 ss_is_fallback 置真, 共享篇数分母 — 因此本列不是"仅共现文章子样本上的占比", 而是"共现文章按窄文本投影、其余文章按全文投影"的混合占比, 回退率高时向 full 轨收敛; 若金融科技词典不可用, 回退标志全体置真, 属优雅降级而非错误。判定口径不对称: 银行侧匹配含否定与短名过滤, 金科侧为裸词典命中; 且此处的"同句共现"与 stage 13 硬过滤所用的邻近共现半径是两个不同配置键、两套原语, 禁互相复用口径。阈值中心以本列得分列名独立冻结, 与其他轨不可比水平。识别铁律: 本列与 full, ctx 轨互为稳健性不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与 _lg 对偶列受 both-or-neither parity 约束。

## VAR: benefit_pos_frac_ctx

【变体差分】
本列是正面效益叙事占比的 ctx 轨变体, canonical 嵌入槽。相对 core 列 benefit_pos_frac_full 的唯一差分是文本轨道: 投影对象为 content_ctx (标题 prepend 加目标银行实体上下文窗口), 把"利好叙事"的计数收窄到谈论目标银行的语段, 剔除同篇文章中对行业整体或其他机构的正面渲染 — 这对正面占比尤其重要, 因为金融科技报道常见"行业前景光明"式的泛化吹捧, full 轨会把这类段落的正面投影记入目标银行, 而 ctx 轨在构造上免疫此类溢出。聚合口径与家族一致: bank-year 内投影得分高于冻结中位数中心的文章占比, 中心以本列得分列名为键独立冻结于 sidecar, 记录嵌入模型标识, 换模不删条目即 fail-loud。因中心独立, 本列与 full 轨列的水平不可直接比较, 只比较各自回归的标准化效应。行宇宙为 conditional-on-full 子集 (full 轨 LLM 门控留篇集中 content_ctx 非空者), 分母为该 bank-year 在本轨的有效投影篇数。解释警示与 core 列共享: 正面叙事占比高是媒体叙事环境的性质, 不是经营效益的事实陈述, Kim 与 Lyon (2015) 与 Duchin, Gao 与 Xu (2025) 的夸大与漂绿证据在窄轨上同样适用。识别口径: 与 full, ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 benefit_pos_frac_lg_ctx 构成 co-primary 对偶, 受 both-or-neither parity 守卫。

## VAR: benefit_pos_frac_full

【变体差分】
本列是家族正面占比基名的 canonical 主列: full 轨, canonical 嵌入槽, tier 为 core, 核定依据是作为验证轨回归变量实际进入三个机制与稳健性正文表模板, 与负面占比 core 列构成两尾对偶。构造分三层。文本层: content_full, 标题 prepend 全文正文, 与全部情感方法的 full 轨同源, full-only 留篇门控 (2026-06-29 口径) 决定行宇宙 — 是否算一篇银行金融科技报道只看 full 轨 LLM 验证结论, 本列分母即该 bank-year 门控后有效投影篇数。得分层: 文章嵌入对十对严格对偶锚点差分轴的余弦投影, 正向即"金融科技利好该行经营"的叙事方向。聚合层: 投影得分高于冻结中位数中心的文章占比。中心的工程史值得展开, 因为它决定本列的可用性: 早期以零为界的符号阈值下, 嵌入空间各向异性使绝大多数文章投影为正, 正面占比接近饱和, 作为自变量信息量趋零; 生产口径改为全样本投影中位数中心化, 由构造把文章级正负两半拉回平衡, 再经冻结 sidecar 固定 (键为本列得分列名, 记模型标识, 不匹配 fail-loud), 语料增量不再平移全历史占比。两点披露随之而来: 中心是首跑样本内中位数, 文章级平衡性质只对首跑语料严格成立; 面板层面因各 bank-year 篇数不均的 mean-of-fractions Jensen 效应, 占比的简单均值系统性略低于一半, 属聚合口径性质。构念解释上, 本列度量报道环境中利好叙事的相对频率, 与均值测度互补 — 均值对极端值敏感而占比对两尾计数稳健; 高正面占比的解释须谨慎: You, Zhang 与 Zhang (2018) 与 Gurun 与 Butler (2012) 提示媒体正面倾向可能被广告与关系俘获, Westphal (2023) 与 Kim 与 Lyon (2015) 提示企业有系统性动机制造象征性正面叙事, 故本列在论文中定位为叙事环境测度与机制变量, 不作经营效益的事实代理。识别铁律: 本列的 ctx, ss 轨变体与 _lg 对偶各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 与负面占比列可同表并排但须披露机械负相关; 与 _lg full 对偶受 both-or-neither parity 守卫, 无单边孤儿。本列区别于负面占比 core 列的构念重心在正尾的信号性质: 中文银行金融科技报道的正面叙事供给受成绩汇报体裁与政策呼应传统的结构性抬升, 正尾计数中"信息性利好"与"仪式性褒扬"混合比例天然高于负尾, 因此本列的文献对话对象是象征性披露研究 — Westphal (2023) 论证了系统性象征管理如何让正面叙述与实质行动脱钩, Kim 与 Lyon (2015) 给出企业在可持续披露中同时存在夸大与刻意低调两个方向的证据, Duchin, Gao 与 Xu (2025) 则显示资产市场能够部分识破漂绿式正面叙事。落到计量上, 这意味着本列的机制角色更常是被解释侧或调节侧: 检验"什么样的银行获得更高利好叙事占比" (媒体俘获、广告投放、政企关系) 与检验"利好叙事占比是否预测后续真实经营改善" (叙事的信息含量检验) 是两条须分开设定的路径, 后者若不成立并不否定本列效度, 恰是构念按设计工作的表现 — 它测的是叙事而非事实。审计侧, 替代锚点臂与安慰剂臂对本列的复算逻辑与负面列对称: 若正面占比效应在中性基线轴上同样出现, 说明捕捉的是泛化正面语气而非效益构念。窄轨复核对本列同样必要且方向明确: ctx 与 ss 轨在构造上剔除行业泛化吹捧, 若 full 轨效应在窄轨全面消失, 应将解释收窄为"报道环境的行业性正面氛围"而非"该行金融科技的特异性利好叙事"。

## VAR: benefit_pos_frac_lg_ctx

【变体差分】
本列是正面占比的 ctx 轨 _lg 变体: 与 benefit_pos_frac_ctx 共享完全相同的文本口径 (标题加实体窗口, conditional-on-full 行宇宙) 与聚合定义, 唯一差分是嵌入空间切换为 co-primary 第二槽 text-embedding-3-large (3072 维): 锚点重嵌入、方向轴重算、投影重做、中位数中心以本列得分列名独立冻结, 与 canonical 槽零共享。其职能是在实体归因收窄的轨道上执行跨嵌入空间对照: 正面叙事的识别对嵌入模型选择可能比负面更敏感, 因为中文财经报道的正面用语高度模板化 (成绩汇报体、政策呼应体), 不同模型对这类模板语的语义编码差异较大, Tang 与 Yang (2025) 的金融嵌入基准正是此类差异的系统证据; 若 canonical ctx 列的效应在本列上不可复现, 优先怀疑模板语编码而非机制。铁律口径完整复述: canonical 与 _lg 两槽同为主测度 (co-primary), 互为稳健性、不分主次, 列名双射严格 parity — 本轨任一侧嵌入失败则两族列同置缺失 (both-or-neither), 无单边孤儿; 两槽各自 just-identified 并排, 与 full, ss 轨梯子同理, 任意组合禁混进同一 over-identified Hansen J。水平比较仅限同列自身的时序与截面变异, 跨槽跨轨一律以标准化系数汇报。换嵌入模型须先删冻结中心 sidecar 对应条目, 否则模型标识守卫 fail-loud。

## VAR: benefit_pos_frac_lg_full

【变体差分】
本列是正面占比 core 列的 co-primary 嵌入对偶: full 轨文本与 benefit_pos_frac_full 逐字节相同 (content_full, full-only 留篇门控行宇宙), 全部嵌入运算切换到 text-embedding-3-large 的 3072 维空间独立完成 — 锚点句重嵌入并过同一套锐利度守卫, 方向轴独立差分, 文章投影独立计算, 中位数中心以本列得分列名独立冻结并记模型标识。本列与 canonical core 列构成家族正尾测度的最干净仪器对照: 文本、行宇宙、聚合函数、锚点句全同, 仅嵌入几何不同, 任何两列间的结论分歧可唯一归因于嵌入空间。co-primary 语义须准确理解: 本列不是从属的稳健性附件, 而是与 canonical 并列的主测度之一, 论文中两列各自单独入模、并排报告, 结论以两空间方向一致为准; 严禁把两列同时塞进一条 over-identified Hansen J 方程借"多工具"过度识别, 也禁与 ctx, ss 轨变体混入同一方程 — 每列各自 just-identified 并排是家族全部十八列的统一识别口径。parity 由 both-or-neither 守卫机械保证: 任一 spec 在 full 轨方向向量计算失败整体跳过时, canonical 与 _lg 两族同置缺失。占比水平因中心独立冻结不可跨列直接比较。审计维度: _lg 空间的全长文章嵌入与方向向量随 sidecar 落盘, 替代锚点与安慰剂审计在同一空间可复算, 使本列的锚点敏感性梯子与嵌入敏感性梯子正交可分。嵌入模型选型依据见 Zhang et al. (2025) 与 Tang 与 Yang (2025)。

## VAR: benefit_pos_frac_lg_ss

【变体差分】
本列是正面占比在最窄归因轨上的 _lg 变体: 文本对象 content_ss (目标银行与金科词同句共现句 ± 一句窗口, 标题 prepend), 嵌入与投影在 text-embedding-3-large 空间完成, 中心独立冻结。构念上, 本列回答"在把该银行与金融科技明确绑定的语句邻域内, 利好叙事占多大比例", 对正面测度而言这是最强的反泛化设计: 行业性吹捧、政策性展望若不与目标银行同句出现, 不进入本列的投影文本。回退语义与 canonical ss 列相同且必须如实解释: 无共现文章回退全文正文 (ss_is_fallback 置真, 共享篇数分母), 金科词典缺失时全体回退, 高回退率切片上本列语义向 full 轨漂移。行宇宙 conditional-on-full。本列叠加最窄轨与第二嵌入空间两级差分, 与 benefit_pos_frac_full 相距最远, 在梯子中的用法是端点三角验证: canonical full, canonical ss 与本列三点方向一致, 则正尾结论对归因半径与嵌入几何同时稳健; 若仅本列失效, 先检查回退率与 ss 轨样本稀释, 再怀疑嵌入空间; 若三点一致则正尾结论可写入正文而把角点列留在稳健性附表。识别铁律复述: 三轨互为稳健性不分主次, co-primary 双槽严格 parity (both-or-neither, 无单边孤儿), 全部变体各自 just-identified 并排, 禁混同一 over-identified Hansen J; 水平跨列不可比, 报告标准化系数。

## VAR: benefit_pos_frac_ss

【变体差分】
本列是正面占比的 ss 轨 canonical 嵌入变体。与 core 列的差分在文本轨道: content_ss 只保留目标银行与金融科技词同句共现的句子及其前后一句, 是三轨中把"利好叙事"归因到该行金融科技的最严口径。其相对 ctx 轨的增量约束是共现要求: ctx 轨只要求语段谈及目标银行, 本轨额外要求金融科技词在同一句内出现, 从而排除"报道该行但正面语句实际在谈网点服务或财报业绩"的错误归因; 判定原语与 stage 13 硬过滤的邻近共现判据是两套不同口径 (本轨严格同句, 过滤器为句半径窗口), 二者禁互相复用。回退语义: 无共现文章镜像 ctx 规则回退全文正文并置 ss_is_fallback 为真, 共享篇数分母, 故本列是窄文本与全文投影的混合占比, 解释时结合回退率; 金科词典不可用时全体回退属优雅降级。银行侧判定含否定与短名过滤, 金科侧为裸词典命中, 口径不对称是刻意设计。中位数中心以本列得分列名独立冻结, 与其余轨水平不可比。行宇宙为 full-only 门控留篇集中 content_ss 非空的子集。识别口径: 与 full, ctx 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 _lg 对偶列受 both-or-neither parity 守卫, 任一侧失效两族同缺。

## VAR: benefit_std_ctx

【变体差分】
本列是态度分歧测度的 ctx 轨变体, canonical 嵌入槽。与 core 列 benefit_std_full 的差分在文本轨道: 分歧的计算对象是各文章 content_ctx (实体窗口文本) 投影得分的 bank-year 内样本标准差 (ddof 为 1), 即"当媒体明确谈论该银行时, 各篇报道对其金融科技效益的叙述方向有多不一致"。相对 full 轨, 本列剔除了由文章其他主题段落带入的伪分歧 — 两篇对目标银行态度一致但对行业其他事件叙述相反的文章, 在 full 轨会被计为分歧而本轨不会; 反向代价是窗口文本短、投影噪声大, 小样本 bank-year 的标准差估计更不稳定。NaN 口径与家族统一: 单观测 bank-year 保持 NaN 不填零, 因为一篇报道无从谈分歧, 填零会与"多篇完全一致"混同, 也与同面板 LLM 情感标准差族的口径冲突; 下游回归经 listwise deletion 自然处理, 分歧度样本因此偏向报道密集银行年, 建议以篇数门槛做敏感性。本列不依赖冻结中心 (标准差与阈值无关), 故不受 sidecar 换模删除流程影响, 但嵌入空间本身仍决定投影尺度, 跨轨跨槽只比标准化效应。行宇宙 conditional-on-full。识别铁律: 与 full, ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; 与 benefit_std_lg_ctx 构成 co-primary 对偶, both-or-neither parity 守卫成立。

## VAR: benefit_std_full

【变体差分】
本列是家族分歧测度的 canonical 主列: full 轨, canonical 嵌入槽, tier 为 core, 核定身份是 benefit 家族分散度统计的 canonical 态度分歧测度。定义: bank-year 内全部有效文章 content_full 投影得分的样本标准差 (ddof 为 1), 理论域零到一 (余弦投影本身有界)。构念定位: 本列测量的不是媒体对该行金融科技的态度位置, 而是态度的凝聚程度 — 低值表示叙事环境高度一致 (无论一致看好还是一致看衰, 位置由均值与占比对刻画), 高值表示媒体在该行金融科技的经营含义上存在实质争议。分歧本身是金融文献中有独立含义的信号: 媒体信号的分散度影响信息环境质量与投资者解读成本, Tetlock (2007) 与 Fang 与 Peress (2009) 确立媒体信息影响市场的基线之后, 分歧维度自然成为"信息影响市场"机制的调节变量; 在本项目论文中, 本列作为态度分歧的 canonical 分散度统计进入机制与异质性检验, 与同面板 LLM 语气标准差族并排提供"效益叙事分歧"对"语气分歧"的构念区分。两个口径决策承重, 均须在使用时复述。其一, 单观测 NaN: 只有一篇有效报道的 bank-year, 样本标准差在 ddof 为 1 下未定义, 保持 NaN 而绝不填零 — 填零会令"信息极少"与"多篇真实零分歧"不可区分, 制造分歧度被系统性低估的假象; 该口径与 LLM 情感标准差族刻意对齐, 早期试跑切片上本列大量 NaN 属预期退化, 生产规模十九年面板下覆盖率应显著回升。其二, 本列不使用冻结中心 (与占比对不同, 标准差对位置平移不变), 因此对中心冻结的样本内披露免疫, 但对嵌入空间几何仍敏感: 各向异性会压缩或拉伸投影分布的尺度, 使分歧度水平跨嵌入空间不可比, 对应梯子即 _lg 对偶列在第二空间重算全量。识别铁律: 本列的 ctx, ss 轨变体与 _lg 对偶各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 本列与同族均值、占比列由同一投影得分构造, 相关结构机械, 亦不应共入一条过度识别方程。回归使用时注意 listwise deletion 使样本偏向多报道银行年, 稳健性方向是篇数加权或最低篇数门槛。进一步的解释框架: 本列与占比对联合可区分四种叙事环境形态 — 低分歧高正占比是一致看好, 低分歧高负占比是一致看衰, 高分歧且两占比接近是实质争议, 低分歧且两占比都低是态度集中于中性带; 单独任何一列都无法完成该分型, 这是把分散度统计设为 core 的实质理由。与相邻分歧测度的边界须写明: 同面板另有跨模型标签异质度与语气标准差族, 前者度量"不同测量工具之间的不一致", 本列度量"不同文章之间的不一致", 二者在构念上是测量分歧对叙事分歧之别, 回归中不可互换; 与媒体分歧衍生论文的核心测度亦不同源, 该论文主轨基于语气法而本列基于效益轴投影。分布性状上, 余弦投影有界使本列天然有界, 无须缩尾; 但 bank-year 篇数与本列的联合分布并非独立 — 报道稀少的银行年往往也是小行或新闻价值低的年份, NaN 缺失因此与银行规模相关, 固定效应内的估计受影响较小, 跨行截面比较则应显式处理该选择性。早期试跑切片上本列仅在多篇格出值属预期退化, 生产十九年面板的覆盖率以注入统计为准。

## VAR: benefit_std_lg_ctx

【变体差分】
本列是分歧测度的 ctx 轨 _lg 变体: 与 benefit_std_ctx 共享文本口径 (实体窗口, conditional-on-full 行宇宙) 与聚合定义 (ddof 为 1 样本标准差, 单观测 NaN 不填零), 唯一差分是投影发生在 text-embedding-3-large 的 3072 维空间 — 锚点、方向轴、文章嵌入全部在该空间独立重算。分歧测度的跨空间对照有其特殊价值: 标准差对嵌入空间的尺度与各向异性双重敏感, 同一批文章在两个空间中的投影散布可能因空间几何而非叙事内容出现水平差异, 因此本列与 canonical ctx 列的水平差异不携带经济含义, 只有各自回归中标准化系数的方向与显著性可比 — 这一点比占比对更须强调, 因为占比经中位数中心化部分吸收了尺度差, 标准差没有任何中心化保护。本列不消费冻结中心 sidecar, 换嵌入流程中无需删条目, 但嵌入缓存与方向向量 sidecar 的模型标识仍须一致。方法论职能: 在实体归因收窄轨道上检验"分歧结论是否被单一嵌入几何驱动", 与 Tang 与 Yang (2025) 记录的模型间金融语义表征差异直接对话。铁律完整复述: canonical 与 _lg 同为主测度 (co-primary), 互为稳健性、不分主次, 严格 parity — ctx 轨任一侧无效则两族同置缺失 (both-or-neither, 无单边孤儿); 两槽与三轨的任意变体各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

## VAR: benefit_std_lg_full

【变体差分】
本列是分歧测度 core 列的 co-primary 嵌入对偶: full 轨文本与 benefit_std_full 逐字节相同 (content_full, full-only 留篇门控行宇宙), 嵌入运算整体切换到 text-embedding-3-large 空间 — 十对锚点句重嵌入并通过同一套锐利度守卫, 方向轴独立差分归一, 文章投影独立计算, bank-year 内样本标准差聚合口径不变 (ddof 为 1, 单观测 NaN)。本列与 canonical core 列构成分歧构念的纯仪器对照: 二者之间的一切差异可唯一归因于嵌入空间几何, 这对标准差测度尤为重要 — 投影分布的散布同时承载"叙事真实分歧"与"空间各向异性伪散布"两种来源, 单一空间无法内部区分, 双空间并排是本家族对该混杂的唯一显式对冲; 若分歧效应仅在一个空间显著, 应报告为不稳健而非择优。co-primary 语义: 本列是并列主测度而非附属稳健轨, 规范用法为各自单独入模并排报告; 严禁与 canonical 列或任何轨道变体混入同一 over-identified Hansen J 方程, 全部变体各自 just-identified 并排。parity 守卫: full 轨任一嵌入槽失效 (如该 spec 方向向量计算失败整体跳过), canonical 与 _lg 两族列同置缺失, 无单边孤儿。本列不依赖冻结中心, 但其嵌入缓存与方向向量 sidecar 记录 _lg 模型标识, 审计链路 (替代锚点、安慰剂) 在同一空间可复算, 保证锚点敏感性与嵌入敏感性两把梯子正交。水平跨空间不可比, 汇报一律标准化系数; 分歧度回归的 listwise deletion 偏样本问题与 canonical 列相同。

## VAR: benefit_std_lg_ss

【变体差分】
本列是分歧测度在最窄归因轨上的 _lg 变体: 文本对象 content_ss (银行与金科词同句共现句 ± 一句窗口), 投影在 text-embedding-3-large 空间完成, bank-year 内样本标准差聚合 (ddof 为 1, 单观测 NaN 不填零)。构念上, 本列测量"把该银行与金融科技明确绑定的语句邻域内, 各篇报道效益叙述的分歧程度", 是家族分歧梯子中归因最严的角点: full 轨分歧可能混入文章其他主题的叙述差异, ctx 轨可能混入谈论该行非金科业务的差异, 本轨把分歧计算收敛到金科归因语句本身。回退语义对分歧测度的影响须特别说明: 无共现文章回退全文正文 (ss_is_fallback 置真), 高回退率的 bank-year 中本列实际混合了窄文本与全文两种投影对象, 其标准差可能因文本口径异质而机械偏高, 解释时应以回退率分层或以低回退子样本复核。行宇宙 conditional-on-full, 且 ss 轨样本经窗口约束后文章更少, 单观测 NaN 与小样本噪声在本列最严重, 早期试跑切片上大面积缺失属预期。本列叠加最窄轨与第二嵌入空间双重差分, 用于分歧结论的端点三角验证。铁律复述: 三轨互为稳健性、不分主次, co-primary 双槽同为主测度、严格 parity (本轨 both-or-neither, 无单边孤儿), 全部变体各自 just-identified 并排, 禁混同一 over-identified Hansen J; 水平跨空间跨轨不可比, 报告标准化系数。

## VAR: benefit_std_ss

【变体差分】
本列是分歧测度的 ss 轨 canonical 嵌入变体。与 core 列的差分在文本轨道: 标准差的计算对象是 content_ss 投影得分 — 只保留目标银行与金融科技词同句共现句及其前后一句窗口的文本, 归因半径为三轨最窄。其构念增量在于分歧的"标的纯度": full 轨分歧混合了对该行金科、该行其他业务乃至行业事件叙述的全部差异, 本轨把分歧锁定在"直接把该行与金科相连的语句"上, 更接近"媒体对该行金融科技战略本身是否有争议"的理论构念。回退语义与占比列相同且对本列解释更关键: 无共现文章镜像 ctx 规则回退全文正文 (ss_is_fallback 置真, 共享篇数分母), 回退文章与真共现文章的投影对象口径不同, 高回退 bank-year 的标准差含文本口径异质带来的机械成分, 建议以回退率分层复核; 金科词典缺失时全体回退属优雅降级。同句判定与 stage 13 过滤器的邻近共现判据是两套原语两个配置键, 禁互相复用; 银行侧含否定与短名过滤, 金科侧裸词典命中。单观测 bank-year 保持 NaN 不填零, 与家族及 LLM 标准差族口径一致; ss 轨样本最稀, 开发切片缺失面最大属预期退化。本列不消费冻结中心。行宇宙为 full-only 门控留篇集的 ss 非空子集。识别口径: 与 full, ctx 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 _lg 对偶受 both-or-neither parity 守卫。

<!-- rendered-citations:begin -->
Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? A language embedding approach. Review of Financial Studies, 39(5), 1227-1266. https://doi.org/10.1093/rfs/hhaf012
Zheng, J., Ng, K. C., Zheng, R., & Tam, K. Y. (2024). The Effects of Sentiment Evolution in Financial Texts: A Word Embedding Approach. Journal of Management Information Systems. https://doi.org/10.1080/07421222.2023.2301176
Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2506.05176
Tang, Y., & Yang, Y. (2025). FinMTEB: Finance massive text embedding benchmark. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 3620-3638. https://doi.org/10.18653/v1/2025.emnlp-main.179
Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M. (2025). Asset embeddings. NBER Working Paper No. 33651 [Working Paper]. https://doi.org/10.3386/w33651
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Ash, E., & Hansen, S. (2023). Text algorithms in economics. Annual Review of Economics, 15, 659-688. https://doi.org/10.1146/annurev-economics-082222-074352
Westphal, J. D. (2023). Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale. Strategy Science, 8(2), 221-232. https://doi.org/10.1287/stsc.2023.0188
Gennaro, G., & Ash, E. (2022). Emotion and reason in political language. The Economic Journal, 132(643), 1037-1059. https://doi.org/10.1093/ej/ueab104
Berg, T., Fuster, A., & Puri, M. (2022). FinTech lending. Annual Review of Financial Economics, 14, 187-207. https://doi.org/10.1146/annurev-financial-101521-112042
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Cheng, M., & Qu, Y. (2020). Does bank FinTech reduce credit risk? Evidence from China. Pacific-Basin Finance Journal, 63, 101398. https://doi.org/10.1016/j.pacfin.2020.101398
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture: Analyzing the meanings of class through word embeddings. American Sociological Review, 84(5), 905-949. https://doi.org/10.1177/0003122419877135
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gorovaia, N., & Makrominas, M. (2025). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management. https://doi.org/10.1111/eufm.12509
Okeke, A. (2026). Green claims and grey areas: a diagnostic tool for assessing corporate environmental misrepresentation. International Journal of Disclosure and Governance. https://doi.org/10.1057/s41310-026-00371-1
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
