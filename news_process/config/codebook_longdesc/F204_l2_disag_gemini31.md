---
family_id: F204
novelty_exempt_rationale: "disag_ 前缀家族, 是情感分歧指数按三家LLM(gemini31/gpt54nano/deepseekv4)分厂商拆分的稳健性变体, 测度定义(disag=√(1-r²))与学术依据已在CORE正文引用的Cookson & Niessner (2020)等分歧文献中给出, 本列仅是同一构念在不同模型口径下的重算, 非独立新构念, 无需为其单独追加新颖文献。"
columns:
- disag_gemini31_ctx
- disag_gemini31_full
- disag_gemini31_ss
unit: 无量纲分歧指数, 值域 [0, 1]
formula: "disag = sqrt(1 - ((P - N) / (P + N))^2); P = gemini31 判为正面的篇数, N = gemini31 判为负面的篇数 (逐轨、逐银行-年); P+N=0 时置 NaN"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag)
upstream:
- 21_tone_llms.parquet (gemini31 逐篇情感标签, 三轨)
- 24_herd_decay.parquet (df_exploded, verified article×bank 集)
citations:
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: "10.2139/ssrn.6307940"
  type: "wp"
  authors: "Wang, Z., & Zhang, H."
  year: 2026
  title: "Large Language Models, Investor Disagreement, and Trading Volume"
  venue: "SSRN"
  pages_or_artno: "6307940"
- doi: "10.2139/ssrn.7027983"
  type: "wp"
  authors: "Yi, K., & Wu, F."
  year: 2026
  title: "What Investors Disagree About: LLM-Decomposed Retail Disagreement and the Cross-Section of Stock Returns"
  venue: "SSRN"
  pages_or_artno: "7027983"
- doi: "10.2139/ssrn.4921479"
  type: "wp"
  authors: "Kwon, J., Lee, S. H., & Yoo, Y."
  year: 2024
  title: "Disagreement, Subjective Uncertainty, and the Stock Market"
  venue: "SSRN"
  pages_or_artno: "4921479"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"围绕某一家银行的金融科技报道, 在情感极性上意见分裂的程度", 即分歧指数 (disagreement)。它不是问某家银行被报道得好不好, 而是问对同一家银行、同一年内, 媒体的正面声音与负面声音之间是否针锋相对、势均力敌。当一年里既有大量看多的报道又有大量看空的报道时, 分歧最大; 当报道口径高度一致 (清一色正面, 或清一色负面) 时, 分歧最小。该构念承接金融经济学里关于意见分歧的研究传统: Hong 与 Stein (2007) 把投资者之间的信念异质性作为解释交易量、价格泡沫与崩盘的核心机制; Carlin, Longstaff 与 Matoba (2014) 用债券市场数据证明分歧本身是被定价的风险来源; Cen, Wei 与 Yang (2017) 进一步刻画了分歧如何伴随反应不足并预测后续收益。Cookson 与 Niessner (2020) 系统地把"投资者为什么不能达成一致"分解为跨群体与群内两层结构, 为本项目以正负篇数比构造分歧分数提供了直接的框架依据。Li 与 Luan (2025) 则把这一思路推进到新闻文本层面, 用基于新闻的投资者分歧度量预测股票收益, 与本家族"从新闻计数出发度量分歧"的路线高度同构。

【方法学与计算】
分歧指数在面板总装阶段的步骤 8b (pipeline/panel/runner.py) 由银行-年度聚合后的正负篇数闭式算出, 公式为 disag = √(1 − ((P − N) / (P + N))²), 其中 P 为该银行-该年内被判为正面的报道篇数, N 为被判为负面的篇数。把 (P − N) / (P + N) 记作净语调比 r, 则 disag = √(1 − r²): 当报道一边倒时 r 趋近 ±1, disag 趋近 0; 当正负篇数相等 (r = 0) 时 disag 取最大值 1。因此该指标是一条以净语调为轴、开口向下的半椭圆, 度量的是极性分布相对于"完全一致"的偏离幅度, 而非语调水平本身——两家净语调相同的银行可以有截然不同的分歧值。分母 P + N 只计入被明确判为正面或负面的篇数, 中性篇章不进入分子分母 (它们既不制造一致也不制造对立), P + N = 0 时该银行-年缺乏有极性的报道, 分歧无从定义, 置 NaN 而非 0, 以免把"没有意见"误当成"意见一致"。这一 NaN 语义与整条流水线"未报道即缺失、不得强行填零"的口径一致。本家族的 P、N 特指来自 gemini-3.1-flash-lite (下称 gemini31) 这一家大语言模型的逐篇情感标签: stage 21 情感环节由三家 LLM (gpt-5.4-nano、gemini31、deepseek-v4-flash) 各自独立判读并投票, 其中 gemini31 与 gpt-5.4-nano 两家经 yunwu 路由 (deepseek-v4-flash 则直连 api.deepseek.com), gemini31 的逐篇输出既参与三家共识, 也被单独抽出计数, 供本家族按"单一厂商模型"口径复算分歧。

【文献定位】
在度量层面, 本项目沿用 Cookson 与 Niessner (2020) 在《Journal of Finance》上确立的分歧分解范式: 把分歧还原为可观测信号 (此处为正负极性篇数) 的失衡, 而不诉诸未观测的信念参数。这一选择使分歧成为一个可从新闻计数直接构造、可跨银行-年比较的透明标量。与其相邻的网络溢出文献 (Grieser, Hadlock, LeSage 与 Zekhnini, 2022) 提醒我们, 同行之间的政策与信息会相互传染, 因而单家银行的报道分歧既可能是自身基本面不确定的映射, 也可能是同业分歧外溢的结果——本家族只负责度量分歧水平, 不承担识别其来源的任务, 来源识别交由面板中的网络与工具变量列族。需要强调的是, gemini31 只是三家 LLM 之一; 三家各自的逐篇标签各自算出一套分歧指数, 彼此互为稳健性、不分主次, 每一套各自 just-identified 并排使用, 严禁把不同厂商模型的分歧列混进同一个 over-identified 的 Hansen J 过度识别检验。同理, 下文三条 full/ctx/ss 文本轨也各自 just-identified 并排、互为稳健性, 禁混进同一 Hansen J。 在最近的前沿工作中, 以大语言模型标签构造分歧指数已成为活跃做法: Wang 与 Zhang (2026) 用 LLM 从文本中构造投资者分歧代理并检验其与交易量的关系, 为本家族由 LLM 逐篇极性标签合成分歧标量这一路线提供了同期存在性佐证; 但该文系未经同行评审的 SSRN 工作论文, 其文本来源与构造式均与本项目不同, 因变量为交易量、层级为股票-日, 并未使用本家族的闭式, 故仅作路线锚定而非公式出处。Yi 与 Wu (2026) 用大语言模型阅读中国最大股票论坛的 2.2 亿条散户发帖, 按内容把分歧分解为基本面分歧与噪声分歧, 发现前者产生 Miller 型高估 (高分歧股月度风险调整收益低约 0.7%) 而后者更多反映情绪, 并指出加总的与词典法的分歧指标因与情绪高度绑定而可能混同两类相反内容、甚至指向错误方向; 这一发现对本家族构成方法论提醒: 本列是不区分内容来源的加总标量, 无法分辨分歧究竟源自基本面判断还是噪声。该文同为未经评审的 SSRN 工作论文, 语料虽同为中文但体裁是散户股票论坛发帖而非报纸报道, 分析层级为股票-横截面收益, 亦无本项目 P + N = 0 置 NaN 的处理约定。Kwon、Lee 与 Yoo (2024) 则在公司 × 财季层面分别量化横截面分歧与主观不确定性 (取自分析师盈余指引与预测离散度), 论证二者虽在实证研究中常被互换使用, 混同却会导致误导甚至相反的结论 (主观不确定性在分歧较低时与波动率正相关, 分歧较高时该关系反转为负), 这为本项目把分歧指数与把握度类测度分列而非合并提供了金融学依据; 须注意该文为未经评审的工作论文, 其分歧与主观不确定性均由分析师预测数据测得, 完全不涉及 LLM, 因而不对本项目由 LLM 标签派生的口径构成方法学支持, 分析层级亦为公司-财季而非银行-年。
## VAR: disag_gemini31_full

【变体差分】
本列是 gemini31 分歧指数的 full 文本轨, 也是本家族的 canonical 首要轨。full 轨的文本单元为"标题 prepend 到全文正文"后的完整报道 (content_full): stage 14 把标题拼接到正文之前, 原始正文列不动, gemini31 在这一完整文本上给出逐篇情感极性。因此本列的 P、N 计数覆盖该银行-年内全部被判为有极性的报道, 分母最宽、样本最充分。之所以以 full 为 canonical, 是因为自 2026-06-29 起留篇门控采用 full-only 口径: 一篇报道是否算作"该银行的一篇金融科技报道"只看 full 轨的 llm_verified_full 判定, 因而 full 轨的行宇宙就是全部留篇集, ctx 与 ss 轨的行宇宙是它的子集。分歧在 full 轨上定义得最完整, ctx/ss 轨则是条件于 full 留篇集之上、按各自更窄文本重算的稳健性度量。本列与同名 gpt54nano、deepseekv4 的 full 轨分歧列构成跨厂商稳健性对照, 三者各自 just-identified 并排, 禁混同一 over-identified Hansen J; 也不得与本家族的 ctx/ss 轨混入同一过度识别检验。需要提醒的是, 本列度量的是极性的分裂程度而非语调水平, 因此它与同轨的 gemini31 情感均值列在构念上正交: 一家常年被清一色正面报道的银行分歧接近 0, 一家毁誉参半的银行分歧接近 1, 二者的语调均值却可能相同。分歧值域 [0, 1], P + N = 0 时该银行-年缺乏有极性报道而置 NaN, 不填 0, 以免把"无极性报道"错读成"意见高度一致"。作为 canonical 轨, 本列在下游回归中通常充当分歧的首要测度, ctx/ss 轨则退居稳健性对照。

## VAR: disag_gemini31_ctx

【变体差分】
本列是 gemini31 分歧指数的 ctx (entity-context) 文本轨。ctx 轨的文本单元不是整篇正文, 而是"标题 prepend + 围绕目标实体的上下文窗口" (content_ctx): 只截取目标银行实体出现处附近的句子窗, 把远离银行的段落剔除, 使情感判读聚焦于与该银行直接相关的语境。因此在 ctx 轨上, gemini31 对同一批留篇报道给出的极性标签可能与 full 轨不同——一篇整体基调正面、但在提及本银行的局部却带负面措辞的报道, 会在 ctx 轨被计成负面, 从而改变 P、N 计数与分歧值。ctx 轨的行宇宙是 full 留篇集的子集 (条件于 full-only 门控), 其分歧是"聚焦到银行本体语境后, 意见是否仍然分裂"的稳健性测度, 与 full 轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁与 full 或 ss 轨混进同一 over-identified Hansen J。在早期试跑 T=2 的浅面板上, ctx 轨因样本极稀可能大面积退化 (P+N 常为 0 而置 NaN), 属预期现象, 生产期 T=19 语料充分时方能给出有信息量的分歧分布。与 full 轨相比, ctx 轨回答的是一个更苛刻的问题: 当我们把镜头拉近到只谈论这家银行本身的语句时, 舆论的分裂是否依旧存在, 还是仅仅由报道中与本银行无关的段落制造出来的表象。若 full 轨分歧高而 ctx 轨分歧低, 说明分裂主要来自旁涉内容; 若两轨同高, 则分裂确实指向本银行本体, 这正是 ctx 轨作为稳健性轨的诊断价值所在。值域 [0, 1], P + N = 0 置 NaN。

## VAR: disag_gemini31_ss

【变体差分】
本列是 gemini31 分歧指数的 ss (same-sentence) 文本轨, 是三轨中判据最严的一条。ss 轨的文本单元为"标题 prepend + 银行与金融科技同句共现的句子及其前后 N 句窗" (content_ss, 窗宽由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1): 只有当目标银行与金融科技词在同一句内共现时, 才把该句及邻句纳入情感判读文本。回退语义镜像 ctx——当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若金融科技词表整体缺失 (FINTECH_AC=None), 则该轨 *_is_fallback 全 True 优雅降级。因此 ss 轨上的 P、N 反映的是"仅就银行与金融科技直接同句捆绑的语境, 意见是否分裂", 是三轨中最贴近本项目核心构念、也最容易因共现稀疏而退化的稳健性轨。ss 轨行宇宙同样是 full 留篇集的子集。本列与 full、ctx 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 也不得与其它两家 LLM 的分歧列混用于同一过度识别检验。早期试跑 T=2 上 ss 轨常近零方差或大面积 NaN, 属预期退化。三轨由宽到窄依次是 full、ctx、ss: 文本口径越窄, 判读越聚焦银行与金融科技的直接绑定, 但可用篇数越少、越易退化。三者度量的都是"意见分裂"这一同一构念, 只是在不同文本颗粒度下重算, 因而构成一条由粗到细的稳健性梯子, 而非彼此替代的独立测度。研究者应把三轨并排报告以证明分歧结论不被文本截取口径驱动, 但绝不可把三者拼进同一个过度识别方程。值域 [0, 1], P + N = 0 置 NaN, 语义与另两轨一致。

<!-- rendered-citations:begin -->
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Wang, Z., & Zhang, H. (2026). Large Language Models, Investor Disagreement, and Trading Volume. SSRN No. 6307940 [Working Paper]. https://doi.org/10.2139/ssrn.6307940
Yi, K., & Wu, F. (2026). What Investors Disagree About: LLM-Decomposed Retail Disagreement and the Cross-Section of Stock Returns. SSRN No. 7027983 [Working Paper]. https://doi.org/10.2139/ssrn.7027983
Kwon, J., Lee, S. H., & Yoo, Y. (2024). Disagreement, Subjective Uncertainty, and the Stock Market. SSRN No. 4921479 [Working Paper]. https://doi.org/10.2139/ssrn.4921479
<!-- rendered-citations:end -->
