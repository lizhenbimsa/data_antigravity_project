---
family_id: F209
columns:
- disag_yao_2021_ctx
- disag_yao_2021_full
- disag_yao_2021_ss
unit: 分歧指数 (无量纲, 有界 [0, 1])
formula: "disag_yao_2021{track} = sqrt(1 - ((avg_yao_2021_pos_ratio{track} - avg_yao_2021_neg_ratio{track}) / (avg_yao_2021_pos_ratio{track} + avg_yao_2021_neg_ratio{track}))^2); 分母为 0 时置 NaN; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py::_compute_disag (步骤 8b, 支路 b 单词典)
upstream:
- 24_herd_decay.parquet
- 22_tone_words.parquet
citations:
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: China Journal of Accounting Studies
  vol: 7
  issue: 3
  pages_or_artno: 407-437
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: "10.1093/rfs/hhac075"
  type: journal
  authors: "Daniel, K., Klos, A., & Rottke, S."
  year: 2023
  title: "The Dynamics of Disagreement"
  venue: "Review of Financial Studies"
- doi: "10.1016/j.ememar.2024.101234"
  type: journal
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  venue: "Emerging Markets Review"
new_dois:
  - "10.1093/rfs/hhac075"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
本家族测度"银行-年度层面, 以 Yao 等 (2021) 金融领域中文情绪词典逐词判定为基础的语调分歧程度"。构念上的"分歧"(disagreement) 不是语调的高低或方向, 而是同一银行在同一年度内被媒体报道时, 正面词与负面词共存的均衡程度: 当一年的报道几乎全是正面 (或几乎全是负面) 时, 语调是一致的、无争议的, 分歧接近 0; 当正面词量与负面词量势均力敌时, 说明媒体对该银行金融科技活动的评价在拉锯、莫衷一是, 分歧接近上界 1。这一构念直接对接金融学"意见分歧"文献: Hong 与 Stein (2007) 把投资者意见分歧作为解释交易量、价格泡沫与随后收益的核心状态变量; Carlin、Longstaff 与 Matoba (2014) 用分歧刻画资产定价中的风险溢价; Cen、Wei 与 Yang (2017) 记录高分歧样本的收益反应不足; Cookson 与 Niessner (2020) 进一步把分歧分解为跨投资群体的意见离散, 是本家族 disag_* 分歧分解框架的直接方法论先例。本家族把这类"意见分歧"从投资者信念转译到媒体文本语调层面, 作为银行舆情环境的一个二阶矩 (离散度) 特征, 与一阶矩 (平均语调) 正交。

【方法学与计算】
计算分两级。第一级在文章级: stage 22 (tone_words.py) 用 Yao 2021 词典 (positive = 年报正面 3,592 词 ∪ 社媒正面 912 词去重后 3,844 词; negative = 2,074 词) 对每篇报道数出正面词与负面词命中, 除以文本词数得到该篇的 pos_ratio 与 neg_ratio。第二级在面板聚合: 按银行-年度对文章级词率取均值得 avg_yao_2021_pos_ratio 与 avg_yao_2021_neg_ratio, 再由 runner.py 步骤 8b 的通用函数 _compute_disag 代入闭式 disag = sqrt(1 - ((P - N) / (P + N))^2), 其中 P、N 分别为该轨道下的 avg_pos_ratio 与 avg_neg_ratio。该式几何上等价于 1 减去归一化极性 (P - N)/(P + N) 的平方后开方: 归一化极性取值域 [-1, 1], 越靠两端 (全正 = +1 或全负 = -1) 分歧越小、越靠 0 (正负持平) 分歧越大, 故 disag 恰好是极性绝对值的补的一种度量, 有界于 [0, 1]。边界处理上, 当 P + N = 0 (该银行年度既无正面亦无负面词命中, 分母归零) 时函数返回 NaN 而非 0, 以免把"无信息"错记成"完全一致"。这一分子分母同域、边界置 NaN 的口径与家族综合轨 disag、LLM 投票轨 disag_llm、BERT 轨 disag_bert 完全一致, 仅词源替换为 Yao 2021 单词典。词典法与机器学习法在披露情感度量上的系统比较见 Frankel、Jennings 与 Lee (2022), 二者互为稳健性而非从属, 本家族选择词典法正是取其可复现、可审计、跨样本稳定之长。

【文献定位】
在测度谱系上, 本家族属"词典法情感的二阶矩"分支。Yao 2021 是六部并行中文金融情绪词典之一 (另有 Jiang 2021、Bian 2021、Du 2022、You 2018、Loughran-McDonald 中译), 各词典各自独立算一套 disag_{dict} 分歧列, 互为稳健性、不分主次: 六套分歧列各自 just-identified 并排, 严禁把不同词典的分歧列混进同一个 over-identified 的 Hansen J 过度识别检验 (镜像政治词权重与三轨口径的同一铁律)。Du 等 (2022, Review of Finance) 关于中文金融词典的域特异性论证, 说明为何要保留多部词典并排而非合并成单一"最优"词典。须特别澄清词源以杜绝张冠李戴: 本家族逐词判定所依据的词典本体是姚加权等 (2021) 编制的"金融领域中文情绪词典" (词表 SSOT 落在本仓 tone_words.py 的 Yao 2021 正负词集, 由年报正面词与社交媒体正面词去重合并的正面集及负面集构成), 该词典本体在本家族白名单引文池中暂无对应 DOI 条目、因而无法在此以规范引注形式列出, 但其身份与出处以仓内源码词表为准、不容与他文混淆。与之姓氏相同却分属不同工作的 Xu、Yao 与 Chen (2019) 是一篇中文年报可读性测度论文, 度量的是文本可读性而非情绪极性, 既非本家族词典的来源、亦不参与本列任何一步计算, 此处引之仅为标示"中文财经文本量化"这一更广的方法学脉络, 读者切不可据同姓氏而误认其即 Yao 2021 词典的出处。将新闻文本的意见分歧作为解释变量的最新实证见 Li 与 Luan (2025), 其"新闻驱动的投资者分歧"与本家族"媒体语调分歧"是同一构念在不同数据源上的实现。Daniel、Klos 与 Rottke (2023, Review of Financial Studies) 刻画投资者信念分歧随信息冲击的动态演化路径, 为本家族以银行-年度为单位的语调分歧二阶矩测度提供最新的分歧动态化理论参照; Xu、Hua 与 Zhang (2025, Emerging Markets Review) 用文本分析构造中国官方媒体情绪指数并考察其对股市的影响, 与本家族以中文媒体文本词典法度量银行语调分歧的中国市场情境高度相关。本家族三轨 (full/ctx/ss) 亦各自 just-identified 并排、互为稳健性、禁混同一 over-identified Hansen J; 留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否算作"该银行金融科技报道"只由 full 轨的 LLM 判定决定, ctx/ss 是 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集的子集, ss 轨在无银行与金科同句共现时镜像 ctx 优雅回退为全文口径。

## VAR: disag_yao_2021_full

【变体差分】
本列是 Yao 2021 词典分歧指数的 full (全文) 轨, 是本家族的 canonical 轨。full 轨的文本口径 = 标题 prepend 后拼接全文正文 (content_full), 即对整篇报道数 Yao 2021 正面/负面词命中并求词率, 再在银行-年度上取均值代入分歧闭式。之所以以 full 轨为 canonical, 是因为留篇门控在 2026-06-29 后统一采 full-only 口径: 判定一篇报道是否计入某银行某年度的"金融科技报道"宇宙, 只看该篇 full 轨的 LLM 判定 (llm_verified_full == True), 因此 full 轨的行宇宙即银行-年度面板的留篇集本身, ctx 与 ss 两轨是在此宇宙内的条件轨。数值语义上, disag_yao_2021_full 越接近 0 表示该银行该年的全文语调高度一致 (报道要么普遍正面、要么普遍负面), 越接近 1 表示正负语调势均力敌、媒体评价存在拉锯; 当全年全文中 Yao 词典正负词均零命中时该列为 NaN (无信息, 非零分歧)。需强调本列与同家族语调均值类列的正交性: 一年语调可以整体偏正而分歧很高 (正面词略多但负面词也大量存在), 也可以整体中性而分歧很低 (正负词都极少、比例接近但绝对量小), 故不可用平均语调倒推分歧, 二者度量的是分布的一阶矩与离散度两件事。本轨与 ctx、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混入同一 over-identified 的 Hansen J 过度识别检验; 亦与其他五部词典的 disag_{dict}_full 各自独立并排、不可合并到同一过度识别式。作为 canonical 轨, 论文正文优先报告本列, ctx/ss 仅进稳健性表以证结论不被文本窗口口径驱动。

## VAR: disag_yao_2021_ctx

【变体差分】
本列是 Yao 2021 词典分歧指数的 ctx (实体窗) 轨, 是 full 轨的 conditional-on-full 稳健性轨。ctx 轨的文本口径 = 标题 prepend 后, 仅取目标银行实体命中位置附近窗口内的正文 (content_ctx), 从而把 Yao 词典正负词命中限定在"与银行实体在语境上邻近"的片段, 剔除全文中与该银行无关的语调噪声。与 full 轨相比, 唯一差分维度是文本轨道 (实体窗口 vs 全文), 词典 (Yao 2021)、聚合口径 (银行-年度均值)、分歧闭式与 NaN 边界处理均相同。ctx 轨行宇宙是 full 留篇集的子集: 一篇报道能否进入 ctx 轨的分歧计算, 前提仍是它在 full 轨被判为该银行金融科技报道 (full-only 门控), 再在此前提下按实体窗口重算词率。构念意义上, ctx 分歧刻画的是"聚焦到银行本身的那部分文本, 其语调是否存在分歧", 相较 full 更贴近对该银行的直接评价、对通稿式全文背景语调的敏感度更低。与 full 轨的经验差异往往体现在: 若某银行全年报道多为背景语调偏正的通稿而正文对该行本身着墨不多, full 分歧会被通稿背景语调稀释, ctx 则因聚焦实体窗口而更能捕捉针对该行的真实评价拉锯, 两轨的背离本身即是一条可解读的信号。本轨与 full、ss 各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混进同一 over-identified 的 Hansen J; 同理与其余五词典的 disag_{dict}_ctx 各自独立并排不可合并到同一过度识别式。

## VAR: disag_yao_2021_ss

【变体差分】
本列是 Yao 2021 词典分歧指数的 ss (同句) 轨, 是三轨中判据最严的 conditional-on-full 稳健性轨。ss 轨的文本口径 = 标题 prepend 后, 仅取"目标银行与金融科技词在同一句 (± ss_sentence_radius 句窗, 默认 1) 共现"的句子片段 (content_ss), 把 Yao 词典正负词命中进一步收紧到银行与金科真正同句耦合的语境, 是对"金融科技相关语调"最保守的度量。与 full、ctx 的差分维度同样只在文本轨道 (银行∧金科同句窗 vs 全文/实体窗)。回退语义遵循 CLAUDE.md 铁律, ss 镜像 ctx: 当某篇报道不存在银行与金科同句共现时, content_ss 优雅回退为全文正文、ss_is_fallback 置 True, 该篇按全文口径进入词率计算, 分母仍与 full 共享 n_articles, 从而避免行宇宙塌缩。ss 轨行宇宙同为 full 留篇集子集 (full-only 门控)。构念上 ss 分歧回答的是"当报道确实把这家银行与金融科技放在同一句里谈时, 这种最贴身的语境里语调是否存在分歧"。dev 阶段早期试跑 T=2 短面板上 ss 轨可能出现共现稀疏导致的退化 (方差偏小), 属预期, 生产 T=19 语料下正常。相较 full 与 ctx, ss 轨对"银行与金科同句耦合"这一严判据最敏感, 因此在样本量足够时它给出的分歧最能排除掉与金融科技无关的语调噪声, 但代价是回退篇数增多会使其向 ctx 靠拢; 三轨并置正是为了在"贴身程度"与"样本充分度"之间给出可比的稳健性梯子。本轨与 full、ctx 各自 just-identified 并排、互为稳健性不分主次, 三轨严禁混进同一 over-identified 的 Hansen J; 与其余五词典的 disag_{dict}_ss 亦各自独立并排、不可合并到同一过度识别式。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Daniel, K., Klos, A., & Rottke, S. (2023). The Dynamics of Disagreement. Review of Financial Studies. https://doi.org/10.1093/rfs/hhac075
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
