---
family_id: F208
columns:
- disag_loughran_ctx
- disag_loughran_full
- disag_loughran_ss
unit: 无量纲分歧指数, 取值区间 [0, 1]
formula: "disag_loughran = sqrt(1 - ((P - N) / (P + N))^2); P = avg_loughran_pos_ratio, N = avg_loughran_neg_ratio (即逐篇 loughran 正/负词比率 loughran_pos_ratio/neg_ratio 的银行-年逐轨均值); P+N=0 时置 NaN"
producer: news_process/pipeline/panel/runner.py::main (步骤 8b disag; 均值输入由 encode.py M 块聚合)
upstream:
- 24_herd_decay.parquet (loughran_pos_ratio / loughran_neg_ratio, 逐篇词比率, 逐轨)
- 22_tone_words.parquet (loughran 词典命中 → 逐篇词比率源)
citations:
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1007/s11142-025-09897-1"
  type: journal
  authors: "Li, S. Z., & Luan, Z."
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: "Review of Accounting Studies"
new_dois:
  - "10.1007/s11142-025-09897-1"
---

## CORE

【构念与来源】
本家族刻画的是一家银行在某一年度全部相关金融科技报道内, 由 loughran 财经词典判定的正面语调与负面语调之间的"分歧程度"或"混杂程度"。构念的直觉是: 若这一年针对该银行的报道口径高度一致 (几乎全正或全负), 舆论对该银行金融科技进展的评价就是共识性的; 若正面词与负面词旗鼓相当, 报道内部呈现相互抵触的语调, 则舆论处于分歧状态。这一"语调离散度"是对单一均值型语调测度 (如净语调) 的正交补充: 两家银行可以拥有完全相同的净语调均值, 却因一家报道口径整齐、另一家报道褒贬交织而在信息环境上截然不同。分歧本身是资产定价与信息经济学中的一阶变量, Hong 与 Stein (2007) 将投资者意见分歧作为解释交易量、动量与崩盘的核心机制, Carlin、Longstaff 与 Matoba (2014) 进一步给出分歧驱动风险溢价与波动的实证证据; 在信息生产侧, Cookson 与 Niessner (2020) 用社交网络投资者的语调离散直接构造分歧代理, 本家族沿用其"以文本语调的内部离散度度量分歧"的思路, 但将测量对象从投资者贴文迁移到主流媒体的银行金融科技报道语料。

【方法学与计算】
词典底座为 loughran (Loughran 与 McDonald, 2011) 的正负情感类别, 经本项目 tone_words 阶段汉化落地为 tone_dicts.json 中的 loughran 正面/负面词表, 在 stage 22 逐篇统计命中并归一化为逐篇词比率 loughran_pos_ratio 与 loughran_neg_ratio (每篇正/负词命中数占该篇有效词数之比), 并在 stage 21 语义精筛留篇后进入 24_herd_decay 的 article×bank verified 集。面板装配阶段先在 encode.py 的 M 聚合块上对每一银行-年、逐轨求这两个逐篇词比率的算术均值, 得到 avg_loughran_pos_ratio 与 avg_loughran_neg_ratio; 随后 runner.py 步骤 8b 把这两个均值分别作为 P 与 N 代入闭式 disag = 平方根下 (1 减去 ((P 减 N) 除以 (P 加 N)) 的平方)。须强调 P、N 是逐篇词比率的银行-年均值而非命中计数的求和——命中计数求和 (pos_count/neg_count) 是 LLM 篇章计数分支 disag_llm 及各单模型分支的输入口径, 与本词典族的词级比率口径彼此独立, 不可混用。该式的性质为: 当 P 等于 N 时净语调比 (P−N)/(P+N) 为 0, disag 取上界 1, 代表褒贬完全对冲的极端分歧; 当某一侧比率均值为 0 (报道单边化) 时净语调比为正负 1, disag 取下界 0, 代表零分歧的语调共识; 取值单调地随净语调比绝对值增大而下降, 因而是净语调"幅度"的严格递减变换, 与净语调的"符号/方向"信息正交。分母 P+N 为 0 (该银行-年在该轨的 loughran 正负词比率均值同时为 0, 即无任何 loughran 情感词命中) 时置 NaN 而非 0, 以免把"无信息"误编码为"零分歧"。本测度不作跨词典可加分解, 与 bian_2021、du_2022 等其他词典的同名 disag 变体互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

【文献定位】
在文本情感度量的方法学谱系中, 本家族属于"词典法离散度"分支。Loughran 与 McDonald (2011) 奠定了以财经专用词典替代通用心理学词典的范式, 其后续综述 (Loughran 与 McDonald, 2016; 2020) 系统梳理了词典法相对机器学习法的可解释性与可复现优势, 也明确指出词典命中计数对语料清洗与分母口径高度敏感——本家族据此坚持"留篇门控 full-only、分母逐轨严格对齐"的口径纪律。就构念本身, Cookson 与 Niessner (2020) 是最贴近的先例, 他们证明语调离散型分歧代理能预测收益与波动, 与均值型语调携带互补信息; Hong 与 Stein (2007)、Carlin 等 (2014) 则从理论与资产定价侧论证了分歧作为独立状态变量的经济意义。本家族并非直接复制 Cookson 与 Niessner (2020) 的分歧公式, 而是采用 Antweiler 与 Frank (2004) 提出的平方根标准化分歧测度壳 (disag = 平方根下 (1 减去净语调比平方)), 使 disag 落在有界区间 [0,1] 便于跨银行-年比较; 这一测度壳与 step 7i 的 Janis-Fadner 系数是两个不同的闭式, 本家族刻意采用前者而非后者, 二者不可混同。近年 Li 与 Luan (2025, Review of Accounting Studies) 以新闻文本构造投资者分歧代理并检验其对横截面收益的预测力, 呼应本家族以媒体文本语调离散度刻画银行金融科技报道分歧的构念思路。

## VAR: disag_loughran_full

【变体差分】
本列为 full 轨变体, 也是三轨中的 canonical 留篇门控轨。full 轨的文本单元 = 标题 prepend 后的全文正文 (content_full), 覆盖整篇报道的全部 loughran 情感词命中, 因而逐篇的 loughran 正/负词比率覆盖面最完整、进入银行-年均值 P 与 N 的样本篇数最多、统计噪声最小 (须重申 P、N 是逐篇词比率 loughran_pos_ratio/neg_ratio 的银行-年均值 avg_loughran_pos_ratio/neg_ratio, 而非命中计数求和)。按项目 full-only 留篇门控口径 (2026-06-29), 一篇报道是否计入某银行-年的报道宇宙, 仅由 full 轨 llm_verified_full 为真判定; 故 full 轨参与均值的篇章域直接对应留篇集本身, 而 ctx/ss 两轨降为 conditional-on-full 的行子集测度。作为 canonical 轨, 本列进入主回归时承担基准分歧信号角色, 与 ctx、ss 两轨互为稳健性、不分主次: 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。full 轨的优势在于对语调分歧的完整刻画——它捕捉整篇报道在正负两侧的全部证据; 其代价是可能纳入与"银行×金融科技"共现语境无关的段落语调, 故需 ctx/ss 两轨提供更聚焦的稳健性对照。当某银行-年在 full 轨无任何 loughran 情感词命中时本列置 NaN, 与 ctx/ss 各自独立降级, 不相互连坐。需强调本列与净语调型 loughran 测度的正交关系: 分歧是净语调比绝对值的严格递减变换, 只携带"报道内部褒贬是否对冲"的离散信息, 而不携带方向信息; 因此本列可与同轨 loughran 净语调列并列进入回归而不构成机械共线, 二者刻画舆论环境的两个独立维度——语调水平与语调分歧。在 T=2 开发面板上因留篇稀疏, 本列在部分银行-年可能退化取值; 生产 T=19 语料下 full 轨计数基数充足, 分歧信号方差正常, 这一退化属预期而非缺陷。

## VAR: disag_loughran_ctx

【变体差分】
本列为 ctx 轨变体, 文本单元 = 标题 prepend 后的实体上下文窗口 (content_ctx), 即仅取目标银行实体命中位置附近的窗口文本参与 loughran 正负词比率计算, 而非整篇正文 (逐篇 ctx 轨词比率的银行-年均值即本列的 P、N)。相对 full 轨, ctx 轨把语调证据收窄到与目标银行直接相关的语境, 从而排除同一报道中涉及其他主体或无关议题段落的语调污染; 其代价是每篇参与比率计算的词基数变小、当报道对该银行着墨稀疏时更易触发零命中降级。ctx 轨在本家族中为 conditional-on-full 稳健性轨: 行宇宙是 full 轨留篇集的子集, per-track 的 P、N (即 ctx 轨词比率均值) 严格逐轨对齐, 缺列时跳轨而绝不借用 full 轨口径。本列与 full、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。当 ctx 窗口内无 loughran 情感词命中 (P+N 为 0) 时本列置 NaN, 独立于 full 与 ss 的降级状态。经济上, ctx 轨分歧回答的问题是: 在明确围绕该银行展开的语境中, 报道褒贬是否相互抵触——这是对 full 轨"整篇口径分歧"的更严格实体锚定版本。判定不对称口径沿用项目全局约定: 银行侧命中经否定与短名过滤收窄, 金融科技侧采用裸 AC 词表; 故 ctx 窗口的锚点是目标银行实体位置, 而非金融科技词位置——这与下方 ss 轨的"银行∧金融科技同句共现"是两个不同的语境构造键, 不可互相复用。就稳健性叙事而言, 当 full 与 ctx 两轨分歧结论一致时, 可排除"整篇口径分歧仅由无关段落驱动"的替代解释, 增强主结论的实体归因可信度。

## VAR: disag_loughran_ss

【变体差分】
本列为 ss 轨变体, 文本单元 = 标题 prepend 后的"银行∧金融科技同句±N 窗"文本 (content_ss), 即仅取目标银行与金融科技词在同一句子邻域内共现的最窄语境参与 loughran 正负词比率计算, 窗口半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制 (默认 1)。ss 轨是三轨中语境最聚焦者, 只保留"银行确实在谈金融科技"的句子级证据, 因而对分歧构念的针对性最强, 但每篇参与比率计算的词基数也最小、零命中降级最频繁 (本列 P、N 同为 ss 轨逐篇词比率的银行-年均值)。按 ss 回退语义 (镜像 ctx): 当某报道无银行∧金融科技同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则全轨优雅降级。本列同为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, P、N 分子分母严格逐轨, 缺列跳轨不借 full 分母。本列与 full、ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。当 ss 窗口 (含回退后) 无 loughran 情感词命中时置 NaN, 独立于其余两轨降级。ss 轨分歧回答的是最狭义的问题: 就"银行做金融科技"这一具体话题, 媒体口径是否褒贬交织。由于 ss 轨语境最窄, 它对"分歧究竟来自哪一话题"给出最强的证据锚定: 若 full/ctx/ss 三轨分歧信号一致, 则可层层排除分歧由整篇无关口径或非金融科技段落驱动的可能, 把分歧精确归因到金融科技话题本身。ss 轨与 ctx 轨共享回退语义与 n_articles 分母, 但共现判据严格到同句, 因此在开发 T=2 面板上常呈零方差退化 (同句共现稀疏), 生产 T=19 语料下方能稳定出值——这一退化属结构性预期。三轨在此构成规格稳健性并排, 镜像项目词典消融与政治词权重梯子的先例, 不设跨轨 FWER 模板。

<!-- rendered-citations:begin -->
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies. https://doi.org/10.1007/s11142-025-09897-1
<!-- rendered-citations:end -->
