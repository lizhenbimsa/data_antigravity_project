---
family_id: F229
columns:
  - dummy_no_positive_news
unit: 二值虚拟变量 (0/1 指示, 无量纲)
formula: "dummy_no_positive_news = 1[ pos_count_full.fillna(0) <= 0 ]; pos_count_full = 全年 full 轨被 LLM 多数投票判为正面的银行金科报道篇数"
producer: news_process/pipeline/panel/runner.py (步骤 7 washing/dummy 段, L2304-2308) ; news_process/pipeline/panel/export.py (标签 'No Positive News Dummy')
upstream:
  - 21_tone_llms.parquet (llm_vote_tone_full → pos_count_full)
  - 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.1016/j.jfineco.2019.06.003
  type: journal
  authors: Gao, P., Lee, C., & Murphy, D.
  year: 2020
  title: "Financing dies in darkness? The impact of newspaper closures on public finance"
  venue: Journal of Financial Economics
  vol: 135
  issue: 2
  pages_or_artno: 445-467
- doi: 10.1016/j.jfineco.2023.04.008
  type: journal
  authors: Fedyk, A., & Hodson, J.
  year: 2023
  title: "When can the market identify old news?"
  venue: Journal of Financial Economics
  vol: 149
  issue: 1
  pages_or_artno: 92-113
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: "10.1016/j.jempfin.2024.101512"
  type: "journal"
  authors: "Kim, J.-B., Tseng, K., Wang, J. (., & Xi, Y."
  year: 2024
  title: "Policy uncertainty, bad news disclosure, and stock price crash risk"
  venue: "Journal of Empirical Finance"
  vol: "78"
  pages_or_artno: "101512"
new_dois: []
---

## CORE

【构念与来源】
本家族只含单列 dummy_no_positive_news, 是一个银行-年 (bank-year) 层面的二值虚拟变量, 用以标识"该银行在该年度的银行金科报道语料中完全没有出现过任何一篇被判定为正面的报道"这一信息状态。构念上它刻画的不是情感的强弱或方向, 而是正面信号的彻底缺席 (absence / silence): 当一家银行整年被媒体在金融科技议题上"零正面提及"时, 该列取值为 1, 否则取值为 0。这一状态本身即携带经济学含义——它既可能反映银行在数字化转型叙事中的低能见度 (low visibility), 也可能反映负面或中性报道对正面叙事的挤出, 或反映银行公关与媒体投放策略在正面塑造上的失效。正面信号缺席是一个离散的、门槛式的事件, 用连续的情感均值 (如 llm_vote_tone_full) 或洗稿率 (washing_ratio) 都无法干净地表达, 因此需要单独物化为一个哑变量, 供下游作为解释变量、被解释变量或样本分层维度使用。

数据来源上, 该列的唯一上游是 full 轨情感计数 pos_count_full。full 轨 = 标题 prepend 到正文的完整文本轨, 其正面判定来自 stage 21 三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 的多数投票共识列 llm_vote_tone_full: 一篇报道在 full 轨被多数票判为正面时计入 pos_count_full。这里严格遵循 full-only 留篇门控铁律 (2026-06-29): 是否算作"一篇银行金科报道"只看 llm_verified_full == True, ctx/ss 轨降为 conditional-on-full 的稳健性测度轨, 不参与本哑变量的分母口径。因此 dummy_no_positive_news 天然是一个 full 轨专属指标, 不设 ctx/ss 孪生列, 也不属于三轨并排族——它的行宇宙就是 full 留篇集本身。

【方法学与计算】
计算链路极短且确定: 在 runner.py 步骤 7 的 washing/dummy 段, 当 pos_count_full 列存在于 panel 时, 引擎对其执行 fillna(0) 后与 0 比较, 令 dummy_no_positive_news = (pos_count_full.fillna(0) <= 0).astype(int)。这里 fillna(0) 是承重的语义设定: pos_count_full 由 Int8 逐篇求和聚合而来, 在 nullable Int64 语义下可能为 NaN (表示该银行-年在 full 轨下没有任何被判正面的观测, 即无观测), 代码显式地把 NaN 与真实的 0 都归为"无正面新闻", 二者在本构念下等价——无论是"有报道但无一篇正面"还是"聚合缺值", 结果都是正面信号缺席, 故 <= 0 的判据把二者一并置 1。取值域严格 {0, 1}, int64 存储, 无量纲。引擎在写列后打印 dummy_no_positive_news=1 的 bank-year 计数作诊断日志。需要强调本列不做任何阈值梯子、权重梯子或轨道分叉: 它就是 pos_count_full 的一个确定性门槛变换, 因此不涉及"梯子各自 just-identified 并排"的口径; 但作为 full 轨留篇门控的产物, 其分母与 n_articles 的 full-only 口径完全一致, 若误用 ctx/ss 计数重算会破坏门控一致性, 属 P0 级错误。

【文献定位】
本列的构念根植于"媒体缺席的信息后果"这一文献脉络。Heese, Pérez-Cavazos 和 Peter (2022) 在 Journal of Financial Economics 上证明, 当本地报纸退出后, 当地企业的违规行为显著上升——媒体监督的缺席本身是一个有经济后果的处理, 而不只是数据缺失; 这为"正面报道缺席"作为一个独立可分析状态提供了直接的理论正当性。Gao, Lee 和 Murphy (2020) 同样发现报纸关闭后地方政府融资成本上升、信息环境恶化, 进一步说明覆盖度与正面能见度的消失会通过信息渠道传导到真实的金融结果。在测量层面, Shapiro, Sudhof 和 Wilson (2022) 系统论证了新闻情感的可测性与聚合方法, 支撑了本列以 LLM 正面计数为基元、再门槛化为缺席哑变量的做法; Fedyk 和 Hodson (2023) 关于"旧闻"与信息新鲜度的识别则提醒我们, 正面报道的有无还需与信息的时效性区分, 本列刻意只取当年 full 轨的正面计数, 避免把陈旧转载误计为新增正面信号。综合而言, dummy_no_positive_news 把"正面叙事的彻底缺席"这一在媒体经济学中被反复验证为有后果的状态, 物化为可直接进入银行-年面板的稳健信号。 就此构念在更广信息环境层面的延伸, Kim、Tseng、Wang 与 Xi (2024) 在经济政策不确定性背景下检验管理层坏消息披露与股价崩盘风险的关系, 表明负面信息在时间上的分布本身携带信息含量, 可作为本列「正面叙事的彻底缺席亦是信息环境的一种可分析状态」这一构念动机的背景性参照。但边界须诚实标明: 该文的坏消息源自公司自主披露的时点选择 (发送方内生的隐藏行为), 本列的 pos_count_full 则来自第三方媒体报道经 LLM 三家多数投票的正面判定计数, 被报道银行并不直接控制文本, 故原文的坏消息囤积机制不可直接迁移; 原文 DV 为股价崩盘风险、层级为美国一般上市公司的公司-年, 本列既不作 DV 亦不涉股价数据, 其 pos_count_full.fillna(0) <= 0 的机械角点在 T=19 生产语料上的零值频率与原文样本不可比。该文因此只锚定构念动机层面, 不构成本列的测度来源、阈值依据或效度证据。
## VAR: dummy_no_positive_news

【变体差分】
本列是家族唯一列, 亦是 canonical 列, 不存在同族其它变体, 因此差分语义体现在它相对于家族内相邻连续测度的定位, 而非轨道/模型/阈值分叉。与情感均值列 llm_vote_tone_full 相比: 后者是 full 轨全部留篇报道的情感倾向连续均值, 会因少量强正面或强负面报道而漂移, 且在样本量极小时方差极大; 本列则把信号压缩为一个门槛事件, 只问"是否连一篇正面都没有", 对情感强度不敏感、对正面信号的存在与否高度敏感, 因而在极稀疏语料下比连续均值更稳健、更可解释。与洗稿率族 (washing_ratio*) 相比: 洗稿率刻画的是象征性正面报道占实质性正面报道的比例 (媒体粉饰强度), 分母恰恰要求有正面报道存在; 而本列覆盖的正是洗稿率无定义的那一端——当正面报道为零时洗稿率退化为缺值, dummy_no_positive_news 却恰好在此取 1, 两者在语义上互补而非重叠。

关于轨道: 本列严格 full-only, 无 ctx/ss 孪生, 这是留篇门控铁律 (2026-06-29) 的直接产物——判定"一篇银行金科报道"只看 llm_verified_full, ctx/ss 为 conditional-on-full 的稳健性轨, 不构成本哑变量独立的行宇宙, 故本列不进入"三轨各自 just-identified 并排、禁混同一 over-identified Hansen J"的三轨族口径, 也不设 co-primary 嵌入的 both-or-neither 孪生。关于分母: pos_count_full 的 NaN 与真实 0 经 fillna(0) 统一归为"缺席", 这一设定意味着"整年无任何留篇报道"的银行-年同样被判为 1 (无正面新闻是无新闻的必然子集), 使用者若需把"完全无报道"与"有报道但无正面"区分, 应额外联用 n_articles_full 或相应留篇计数列作条件。取值仅 {0, 1}, int64, 无量纲; 在下游可直接作为处理指示、结果指示或异质性分组维度进入回归。

<!-- rendered-citations:begin -->
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. Journal of Financial Economics, 135(2), 445-467. https://doi.org/10.1016/j.jfineco.2019.06.003
Fedyk, A., & Hodson, J. (2023). When can the market identify old news?. Journal of Financial Economics, 149(1), 92-113. https://doi.org/10.1016/j.jfineco.2023.04.008
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Kim, J.-B., Tseng, K., Wang, J. (., & Xi, Y. (2024). Policy uncertainty, bad news disclosure, and stock price crash risk. Journal of Empirical Finance, 78, 101512. https://doi.org/10.1016/j.jempfin.2024.101512
<!-- rendered-citations:end -->
