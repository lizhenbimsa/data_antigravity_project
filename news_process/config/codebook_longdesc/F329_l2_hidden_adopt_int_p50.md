---
family_id: F329
columns:
- hidden_adopt_int_p50
- hidden_adopt_int_p50_ctx
- hidden_adopt_int_p50_ss
unit: 银行-年份占比 (0–1 之间已测量文章份额; 未测量则为 NaN)
formula: 'hidden_adopt_int_p{50} = mean_i[ 1{ fintech_intensity_score_i < Q_year(freq, 50%) AND policy_cosine_sim_i >= Q_year(sim, 50%) } ], 逐篇仅在 sim 与 freq 同时非缺失(measured)时纳入分类, 否则该篇指示设为 NaN 并被 groupby(mean) 自动跳过 (即分母 = 该银行-年已测量篇数, 非全部报道篇数)'
producer: pipeline\panel\runner.py
upstream:
- pipeline\panel\article_policy_alignment.py (policy_cosine_sim / policy_cosine_sim_ctx / policy_cosine_sim_ss, stage 16)
- pipeline\panel\fintech_intensity.py (fintech_intensity_score, stage 15, int 轨连续强度)
- 24_herd_decay.parquet (verified 域 semi-join, 决定进入四象限分类的文章全集)
citations:
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital finance and FinTech: Current research and future research directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: 'Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations'
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306-333
- doi: 10.1006/jfin.2000.0282
  type: journal
  authors: Boot, A. W. A.
  year: 2000
  title: 'Relationship banking: What do we know?'
  venue: Journal of Financial Intermediation
  vol: '9'
  issue: '1'
  pages_or_artno: 7-25
- doi: 10.1073/pnas.2203150119
  type: journal
  authors: Breznau, N., Rinke, E. M., Wuttke, A., et al.
  year: 2022
  title: Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty
  venue: Proceedings of the National Academy of Sciences
  vol: '119'
  issue: '44'
  pages_or_artno: e2203150119
- doi: "10.1007/s11135-024-02045-y"
  title: "An Analysis of the news coverage of Fintech in Africa: a natural language processing approach"
  authors: "Nach, H."
  year: 2025
  venue: "Quality & Quantity"
  type: "journal"
- doi: "10.1002/bse.71079"
  title: "Costly Signals and Cheap Talk: Measuring the Decoupling of ESG Routinisation and Greenwashing Risk"
  authors: "Zatini, G., Torricella, N., & della Porta, A."
  year: 2026
  venue: "Business Strategy and the Environment"
  type: "journal"
new_dois:
  - "10.1007/s11135-024-02045-y"
  - "10.1002/bse.71079"
---

## CORE

【构念与来源】
本家族刻画银行-金科新闻在"政策语言相似度 × 金科强度"二维平面上落入 Hidden 象限的年度份额, 是 P4 (Gomber 等 locus 维) 论文族"创新采纳位置 (locus of adoption)"四象限分类体系的一支。四象限构造以每篇通过 stage 21 LLM 三家投票留篇门控的文章为分析单元, 在纵轴上用金科相关强度衡量报道"提及金科的密度", 在横轴上用该文章与监管政策文本的余弦相似度衡量报道"贴合官方政策话语的程度"; 以银行所在年度内二者各自的样本分位数 (canonical P50, 家族同胞另设 P25/P75 三级敏感性梯子, 不在本家族之内) 作阈值, 把文章切成四格: 高强度·高相似 = Substantive (实质采纳, 既做又说); 高强度·低相似 = Token (表面采纳, 蹭热点但不贴政策); 低强度·高相似 = Hidden (隐性采纳, 语言上高度贴合官方政策叙事但金科具体着墨很少 — 字面上像在讲政策合规, 实则并未展开金科业务的实质性描述); 低强度·低相似 = Irrelevant (未落入其余三格, 面板未单列输出该占比, 可由 1 减其余三者补足)。hidden_adopt_int_p50 即 Hidden 象限在"int 轨"(连续强度分数轨, 与另一条 kw 轨——不重复关键词计数——并行, 互不替代) 下、以 P50 为分位阈值时, 该银行-年份已测量文章中落入该象限的占比。本列衡量的不是"银行有没有做金科", 也不是"银行提了多少次金科", 而是一种更微妙的沟通策略信号: 银行在对外新闻叙事里刻意使用与监管政策高度贴合的措辞、却在金科业务的实质性描述上着墨甚少, 可解读为象征性合规姿态或"语言先行、业务滞后"的采纳模式, 对应企业沟通/制度理论里"象征性遵从 (symbolic conformity)"与"实质性采纳 (substantive adoption)"的经典区分, 现被移植到银行金科语境刻画媒体报道所呈现的采纳位置。

【方法学与计算】
计算分两步。第一步逐篇打两个连续分数: freq 侧取 stage 15 产出的 fintech_intensity_score (int 轨, 基于金科词典命中密度的连续强度度量, 与 kw 轨"去重关键词数"是同一构念的两种测量口径, 二者并列互为稳健性、不设主次); sim 侧取 stage 16 产出的 policy_cosine_sim (该文章嵌入与政策文本锚点集合的余弦相似度均值, 三轨 full/ctx/ss 分别独立测算)。第二步在 `_classify_policy_quadrants` (`pipeline/panel/runner.py`) 内按银行所在年度分别对 freq 与 sim 取 P50 分位阈值 (`groupby('year').transform(quantile)`, 阈值逐年重估, 不跨年混算), 仅对 sim 与 freq 同时非缺失的文章 (measured 掩码) 做布尔判定, 未测量文章的四象限指示显式设为 NaN 而非归零假分类 (fix omni-g-runner-03/11 修正的历史缺陷: 旧实现把 stage 15 三条优雅早退路径产出的全 NaN policy_cosine_sim 误判为"低相似", 静默把全部高词频文章错记进 Token 象限)。逐篇 0/1/NaN 指示按 (target_bank, year) 分组取 mean, pandas 的 mean 对 NaN 自动跳过, 因而占比分母等于该银行-年内 sim 与 freq 均可测的文章数, 而非报道总篇数; 若某银行-年全部文章均未测量 (如整年 policy_cosine_sim 缺失), 该格输出 NaN 而非伪零, 与本项目"无数据=未测量"的 F3 红线口径 (Allison 2001; Heckman 1979 缺失机制处理原则) 保持一致。上游进入该分类的文章全集经 24_herd_decay 语义域 semi-join 过滤到 LLM 三家投票已验证的留篇集合, 与 full-only 门控 (2026-06-29) 口径一致——即"是否算一篇银行-金科报道"只看 full 轨 `llm_verified_full`, ctx/ss 是该留篇集合内的条件测度轨, 不独立扩大或缩小分母。

【文献定位】
四象限"位置/深度"分类框架直接对应 Gomber, Koch & Siering (2017) 提出的金融科技创新分类维度中"采纳位置 (locus)"的操作化, 该文把创新按其发生于企业内部流程/外部产品/合作生态等不同位置分层, 本项目借此思路把"叙事位置"(报道措辞贴合政策 vs. 贴合具体业务) 映射为可从文本大规模测量的连续指标。象征性/实质性的行为二分渊源可追溯至组织理论中制度趋同与"解耦 (decoupling)"研究传统对采纳-实施缺口的刻画, 也呼应创新生态位研究 Adner & Kapoor (2010, *Strategic Management Journal*) 关于技术互依结构如何影响新技术世代表现的分析框架——银行在生态系统中所处的位置与其对外沟通策略密切相关。银行关系与信息生产的经典文献 Boot (2000, *Journal of Financial Intermediation*) 则为"银行对外沟通如何折射其战略姿态"提供理论背景。分位数阈值分类法本身对测量口径 (词典/嵌入模型/时间窗) 高度敏感, 大规模多分析者复现研究 Breznau et al. (2022, *Proceedings of the National Academy of Sciences*) 揭示同一数据+同一假设下不同建模选择可产生实质性不一致的结论, 提示本家族分位阈值梯度 (P25/P50/P75) 与 kw/int 双轨并行设计正是为回应这一"隐藏的不确定性宇宙"而设的稳健性检验, 单一阈值/单一强度口径下的结论不应被过度解读为唯一真值。Nach (2025, Quality & Quantity) 用NLP文本挖掘方法分析非洲金融科技十年英文新闻报道的主题、叙事与情感演变, 为本家族基于新闻文本连续测量金科强度与政策语言相似度的方法提供直接的媒体报道文本分析先例。Zatini, Torricella, & della Porta (2026, Business Strategy and the Environment) 提出区分"低成本承诺信号(说)"与"高成本组织运营变革(做)"的解耦测量框架, 为本家族象征性合规(语言贴合政策)与实质性采纳(业务着墨)的四象限区分提供最新方法论对照。

## VAR: hidden_adopt_int_p50

【变体差分】
本列是家族的 canonical 无后缀成员, 取 full 轨 (标题+正文全文) 文本测得的 policy_cosine_sim 与 fintech_intensity_score (int 轨) 在 P50 (中位数) 分位阈值下分类得到的 Hidden 象限占比。sim 侧固定用不带后缀的 policy_cosine_sim (vintage 年度锚点, 而非 `_allv` 全语料静态锚点孪生——后者是另一条不在本家族的 anchor 变体, 用于检验政策锚点集合本身随年度滚动是否驱动结论); freq 侧固定用 fintech_intensity_score 本列 (无 track-agnostic 复用问题, int 轨每条 track 都有独立测算)。该列是三轨中的主参照, full 轨对应 stage 21 留篇门控所锚定的同一文本口径, 三轨 (full/ctx/ss) 之间各自 just-identified 并排, 互为稳健性、不分主次, 禁止把三条轨道的测度混入同一 over-identified Hansen J 设定。与本列同族并列的还有 kw 轨版本 (hidden_adopt_kw_p50, 用去重关键词数取代 fintech_intensity_score 作为纵轴强度输入) 与 P25/P75 两个更宽/更窄的分位阈值版本, 均不在本家族收录范围内, 但理解本列时应知道它只是"P50 阈值 × int 强度轨 × full 文本轨"这一具体组合切片, 阈值本身逐年份重新估计而非跨年固定常数, 因而同一银行在不同年份即便报道内容特征不变, 其落入 Hidden 象限的判定也可能因当年同业整体强度/相似度分布位移而改变——这是分位数化方法固有的相对性, 不代表测量误差。分母只计已测量 (sim 与 freq 同时非缺失) 的文章, 缺失文章既不计入分子也不计入分母, 与其余象限占比列 (token_adopt_int_p50/subst_adopt_int_p50) 共享同一批已测量样本与同一年度阈值, 三者理论上应大致互补 (加上未单列的 Irrelevant 象限占比之和趋近 1, 允许因四舍五入及测量掩码边界产生的微小偏差)。

## VAR: hidden_adopt_int_p50_ctx

【变体差分】
本列与 canonical 列共享同一 P50 分位阈值构造逻辑与相同的留篇分母 (full-only 门控下的已验证文章集合), 差异仅在于 sim 与 freq 两个输入分数均切换为 ctx 轨测量: sim 取 policy_cosine_sim_ctx (标题+目标银行实体窗口文本与政策锚点的余弦相似度), freq 取 fintech_intensity_score_ctx (若该同轨强度列存在则优先使用; 若强度构造本身是 track-agnostic 元数据、无 ctx 独立变体, 则代码按既定回退策略复用 full 轨强度列并在日志中披露, 以避免静默把 track-agnostic 列冒充为轨道特异测量)。ctx 轨聚焦实体窗口而非全文, 更适合捕捉报道中围绕目标银行本身的语言与政策贴合程度, 剔除了全文中其他银行或泛化行业叙事对相似度的稀释, 是与 canonical full 轨互为稳健性的并列测度, 而非其替代或加强版; 二者构念相同但取文范围不同, 差异应被解读为测量口径的稳健性检验而非因果强度差异。三轨间禁止混入同一 over-identified Hansen J 设定的铁律同样适用于本列。就分位阈值本身而言, ctx 轨的年度 P50 阈值是在 ctx 轨自身的 sim/freq 分布上独立重新估计的 (而非沿用 full 轨阈值), 这意味着即便 sim/freq 数值发生轨间迁移, 阈值也随之自适应重新校准, 使得 ctx 轨的 Hidden 占比与 full 轨的 Hidden 占比之间的差异应被解读为"实体窗口叙事 vs. 全文叙事在政策贴合度—强度联合分布上的相对位置差异", 而不是绝对数值尺度上的差异; 二者数值不可直接相减用作某种"实体聚焦溢价", 只应分别作为各自回归设定里的并列稳健性检验出现。ctx 轨对报道正文中夹杂大量与目标银行无关的宏观行业评论或其他银行动态的长文尤其有区分力, 能过滤掉这类"噪声段落"对整体余弦相似度的稀释效应。

## VAR: hidden_adopt_int_p50_ss

【变体差分】
本列在 ctx 的基础上进一步收紧取文范围到"同句轨": sim 取 policy_cosine_sim_ss (标题+银行与金科词同句共现 ±N 句窗口内的文本, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1 句, 与 stage 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个独立配置键不可混用), freq 同理优先取同轨强度列 fintech_intensity_score_ss, 缺失时按既定规则回退复用 full 轨并披露。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章不存在银行与金科词的同句共现, 该篇 content_ss 退化为全文正文 (`ss_is_fallback=True`, 与 ctx 共享同一 n_articles 分母口径), 因而 ss 轨并非"更严格意义上的零结果剔除轨", 而是"同句证据存在时用同句证据、不存在时优雅退回全文"的条件测度。ss 轨代表三轨中取文范围最窄、信噪比假设最强的一端 (只用银行与金科词紧邻出现的语境判定政策语言贴合度), 与 full/ctx 两轨并列互为稳健性, 三者各自 just-identified, 结论的稳健性应体现为三轨方向一致而非把三轨强行合并进单一联合估计。由于 ss 轨的取文范围最窄, 当银行与金科词并未在同一句内共现时该篇即触发回退 (ss_is_fallback=True) 退回全文, 此时该篇在 ss 轨的 sim/freq 测量值实质上与 full 轨相同, 分类结果也随之趋同; 只有在真正存在同句共现证据的文章上, ss 轨才提供区别于 full/ctx 的独立测量信息。因此 ss 轨与 full 轨之间的 Hidden 占比差异幅度天然受制于该银行-年内同句共现文章的比例——同句共现文章占比越低, ss 轨退化为 full 轨镜像的程度越高, 三轨间差异越小属预期现象而非测量失败; 解读本列时应结合该银行-年样本量 (n_articles) 与同句共现覆盖率一并考察, 避免把统计噪声误读为构念差异。

<!-- rendered-citations:begin -->
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Boot, A. W. A. (2000). Relationship banking: What do we know?. Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Breznau, N., Rinke, E. M., Wuttke, A., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Nach, H. (2025). An Analysis of the news coverage of Fintech in Africa: a natural language processing approach. Quality & Quantity. https://doi.org/10.1007/s11135-024-02045-y
Zatini, G., Torricella, N., & della Porta, A. (2026). Costly Signals and Cheap Talk: Measuring the Decoupling of ESG Routinisation and Greenwashing Risk. Business Strategy and the Environment. https://doi.org/10.1002/bse.71079
<!-- rendered-citations:end -->
