---
family_id: F197
columns:
- disag_bian_2021_ctx
- disag_bian_2021_full
- disag_bian_2021_ss
unit: 无量纲分歧指数 (∈ [0, 1], 归一化)
formula: "disag_bian_2021 = sqrt(1 - ((P - N) / (P + N))^2); P = avg_bian_2021_pos_ratio (每篇 bian_2021 词级正面比率跨篇取均值), N = avg_bian_2021_neg_ratio (词级负面比率跨篇均值); P + N = 0 时置 NaN"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag, DICT_NAMES 分支喂词级比率)
upstream:
- 22_tone_words.parquet (bian_2021 pos_ratio / neg_ratio, encode 步 M 聚合为 avg_bian_2021_pos_ratio / avg_bian_2021_neg_ratio)
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"媒体语调分歧度"这一构念: 对某家银行在某一年内的全部金融科技相关报道, 用 Bian 等 (2021) 构建的中文金融情感词典逐篇算出正面词级比率与负面词级比率, 跨篇取均值后据正负两个比率的相对平衡程度算出一个介于零到一之间的分歧指数。须特别厘清本家族的正负输入口径: 这里的 P、N 不是原始正负词计数 pos_count/neg_count (那是 LLM 投票轨 disag_llm 的篇章计数输入, 见 runner 步骤 8c 分支), 而是词级比率聚合量——每篇报道先算 bian_2021_pos_ratio (该篇命中正面词数占该篇总词量或情感词量的比率) 与 bian_2021_neg_ratio, 再在银行×年内对所有篇章取算术均值, 得到 avg_bian_2021_pos_ratio 与 avg_bian_2021_neg_ratio, 这两个跨篇均值比率才是代入分歧公式的 P 与 N。词典综合轨与本家族单词典轨走的是 runner._compute_disag 的 DICT_NAMES 分支 (喂词级比率), 与喂原始篇章计数的 LLM 分支在输入变量上系统性不同。构念定义上, 分歧度回答的不是"报道整体偏正还是偏负" (那是语调净值 tone 的任务), 而是"围绕这家银行的正负叙事有多不一致、多相互抵触"。当一年内的报道正负词级比率势均力敌时分歧度趋近于一, 表示舆论对该银行的评价高度分裂、缺乏共识; 当报道压倒性地一边倒 (词级比率全正或全负) 时分歧度趋近于零, 表示叙事高度一致。因此这是一个专门刻画情感极化、观点离散的一维标量, 与情感水平正交。数据来源上, 逐篇的 bian_2021 正负词级比率来自 stage 22 词典情感阶段对 Bian 等 (2021) 词典的机械匹配 (对应 F128/F129 的 bian_2021 neg / pos 基元族), 其跨篇均值 avg_bian_2021_pos_ratio / avg_bian_2021_neg_ratio 在 encode 聚合步 M 生成, 分歧指数本身则在 stage 40 面板总装的步骤 8b (disag) 由 runner 就地闭式算出, 不额外调用任何 LLM 或嵌入接口。

【方法学与计算】
计算公式为 disag = 根号下 (1 减去 ((P 减 N) 除以 (P 加 N)) 的平方), 其中 P 为跨篇正面词级比率均值 avg_bian_2021_pos_ratio、N 为跨篇负面词级比率均值 avg_bian_2021_neg_ratio。可以把 (P 减 N) 除以 (P 加 N) 理解成一个落在负一到正一之间的"净倾向比率": 正负比率中负面压倒时趋向负一, 正面压倒时趋向正一, 正负相等时取零。把这个比率平方后用一减去、再开方, 就把"倾向的绝对强度"翻转成"倾向的模糊程度"——净倾向越接近零 (最分裂), 指数越接近一; 净倾向越接近正负一 (最一致), 指数越接近零。这一函数形式与 Janis-Fadner 系数、log_sent 等 stage 40 步骤 7i/8b/8c 的同族衍生指标共享同一批正负计数原语, 但各自的非线性变换不同, 刻画的构念侧面也不同 (分歧 vs 净失衡 vs 覆盖加权语调)。边界处理上, 当某银行某年 P 加 N 等于零 (即该口径下正负词级比率均值之和为零、无任何情感词命中) 时, 分歧指数置为缺失值 NaN 而非零, 以避免把"无信息"误当成"高度一致", 这一点对下游回归的分子分母口径对齐至关重要。

【文献定位】
本指数在方法学上承袭金融学"分歧度"(disagreement / difference of opinion) 文献。Hong 与 Stein (2007) 系统梳理了投资者意见分歧如何进入资产定价, 指出分歧度是独立于均值信念的二阶矩信息; Carlin、Longstaff 与 Matoba (2014) 进一步用实证证据表明分歧度对资产价格与流动性有可度量的解释力; Cen、Wei 与 Yang (2017) 则展示分析师层面的分歧度与反应不足、随后收益之间的关联。与这些主要基于分析师预测离散度或调查数据的分歧度量不同, 本家族沿用 Cookson 与 Niessner (2020) 开创的"从文本信号直接分解分歧"的思路, 把分歧度从投资者社群网络的观点差异, 迁移到单一媒体语料内部正负叙事的相对失衡上, 因而属于"文本内生分歧"(within-text sentiment dispersion) 的操作化。词典选择上采用 Bian 等 (2021) 的中文金融情感词典, 是因其针对中文会计与金融文本专门构建、覆盖行业术语, 相较通用情感词典在本语料上误匹配更少。同时须承认词典法本身的局限: Frankel、Jennings 与 Lee (2022) 在《Management Science》上系统比较了机器学习与词典法的情感抽取效力, 提示词典法在捕捉语境化、反讽化表达上弱于监督式模型——这正是本项目为何将词典分歧度定位为与 LLM 三家投票、BERT 三模型等多套测度"互为稳健性、不分主次"的一条并排轨道, 而非唯一权威口径。三套测度各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J 检验。

## VAR: disag_bian_2021_full

【变体差分】
本列是家族的 full 轨变体, 也是三轨中的 canonical 主轨。full 轨的文本口径 = 标题 prepend 到全文正文之后的完整报道体 (content_full), 即在 stage 14 ctx_materializer 阶段把原始标题拼接到正文之前形成的全篇文本。逐篇的 bian_2021 正负词级比率在这一完整文本上由 Bian 等 (2021) 词典机械匹配得到, 跨篇取均值成 avg_bian_2021_pos_ratio / avg_bian_2021_neg_ratio 作为 P、N, 再代入分歧公式。与另外两轨的关键差分在于文本范围: full 轨吃下整篇报道的每一句话, 不做任何实体窗口截断, 因此对分歧度的估计基于该银行报道内全部出现的情感词, 信息量最大但也最可能纳入与目标银行金融科技主题弱相关的段落情感。按 2026-06-29 起生效的 full-only 留篇门控口径, 一篇报道是否被判为"银行金融科技报道"、从而进入某银行某年的行宇宙, 只由 llm_verified_full 决定; 因此 full 轨的行集合就是留篇集本身, 其分歧度是三轨中样本覆盖最完整、最不受实体窗口收缩影响的度量。正因为吃下整篇文本, full 轨对分歧度的估计在统计上噪声更低、缺失更少, 但也更可能把与目标银行金融科技主题弱相关的背景段落情感纳入正负计数, 这一权衡正是设置更窄语境的 ctx/ss 两轨作为对照的动机。作为 canonical 主轨, 本列在下游是分歧度构念的首要测度, 也是多套情感测度并排比较时词典分歧度一侧的代表列; ctx 与 ss 两轨降为 conditional-on-full 的稳健性轨 (行宇宙是 full 留篇集的子集, 各自按本轨文本重算而不借用 full 的分子分母)。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混入同一 over-identified Hansen J。

## VAR: disag_bian_2021_ctx

【变体差分】
本列是家族的 ctx (context) 轨变体, 属 conditional-on-full 的稳健性轨。ctx 轨的文本口径 = 标题 prepend + 实体上下文窗口 (content_ctx), 即只保留围绕目标银行实体提及的邻近窗口文本, 而非整篇报道。逐篇正负词级比率因此仅在与目标银行邻近共现的语境片段上匹配后跨篇取均值成 P、N, 再代入同一分歧公式 disag = 根号下 (1 减去净倾向比率平方)。与 full 轨的核心差分在于: ctx 轨通过实体窗口把远离银行提及的背景段落情感剔除, 意在过滤掉那些虽然出现在同一篇报道、却与该银行金融科技叙事无直接语义关联的正负词, 从而给出一个"聚焦于银行本体语境"的分歧度估计。代价是文本量更小、情感词命中更稀疏, 当窗口内 P 加 N 等于零时该列置 NaN 的概率高于 full 轨; 在开发期 T=2 的浅面板上, ctx 轨可能因命中稀疏而出现更多缺失或低方差退化, 属预期现象, 生产期 T=18 语料下方差正常。行宇宙方面, ctx 轨受 full-only 留篇门控约束, 只在 full 判为留篇的报道子集上按 ctx 文本重算, 因此是 full 主轨的稳健性对照而非独立留篇判据。ctx 与 full、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。

## VAR: disag_bian_2021_ss

【变体差分】
本列是家族的 ss (same-sentence) 轨变体, 同属 conditional-on-full 的稳健性轨, 是三轨中语境约束最严的一条。ss 轨的文本口径 = 标题 prepend + 银行与金融科技词在同一句 (±N 句窗, 由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 共现的句子集合 (content_ss)。逐篇正负词级比率只在"目标银行与金融科技概念严格同句同现"的最小语境上匹配后跨篇取均值成 P、N, 再代入相同的分歧公式, 因而给出的是最贴近"银行×金融科技交叉叙事本身"的分歧度。与 ctx 轨的关键区别在于约束粒度: ctx 用实体邻近窗口, ss 用银行∧金融科技同句共现这一更窄的双实体判据, 对无关情感的剔除更彻底但保留文本最少。回退语义遵循 ss 镜像 ctx 的口径: 当某报道无银行∧金融科技同句共现时, content_ss 回退为全文正文 body, ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 当金融科技词表 FINTECH_AC 为 None 时 is_fallback 全置 True 优雅降级。因此 ss 轨在共现稀疏的语料上退化为近似 full 文本, 在 T=2 开发面板上 ss 与 ctx 常同时出现零方差退化, 属预期, 不应据此判定该轨失效。行宇宙同样受 full-only 留篇门控约束, 是 full 留篇集的子集, 只在 full 判为留篇的报道上按 ss 文本重算分歧度, 因此 ss 轨是 full 主轨的最严语境稳健性对照, 而非独立的留篇判据。三轨共享同一 Bian 等 (2021) 词典与同一分歧公式, 差异纯粹来自文本范围的宽窄。ss 与 full、ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
