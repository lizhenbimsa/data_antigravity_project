---
family_id: F205
columns:
- disag_gpt54nano_ctx
- disag_gpt54nano_full
- disag_gpt54nano_ss
unit: 无量纲分歧指数 (取值区间 0 到 1, 归一化)
formula: "disag = sqrt(1 - ((P - N) / (P + N))^2); P = gpt54nano 判正篇数, N = gpt54nano 判负篇数 (逐轨、单模型口径)"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag)
upstream:
- 24_herd_decay.parquet (df_exploded, stage 21 verified 篇集)
- 21_tone_llms.parquet (gpt54nano 逐篇三分类标签)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: "Learning from disagreement: A survey"
  venue: Journal of Artificial Intelligence Research
  vol: 72
  issue: ''
  pages_or_artno: 1385-1470
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
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
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是同一构念在不同文本轨道上的三个并排实现: 某家银行在某一年内, 关于它的新闻报道在情感极性上呈现的"分歧程度"(disagreement / ambivalence), 且情感标签只取单一大语言模型 gpt54nano 的逐篇三分类结果。构念的直觉是: 如果这一年针对该银行的报道要么普遍正面、要么普遍负面, 那么外部信息环境是"共识化"的, 分歧低; 如果正面报道和负面报道旗鼓相当、势均力敌, 那么信息环境是"撕裂"的, 分歧高。分歧不是情感水平 (tone) 本身, 而是情感在正负两侧的分散/平衡状态——一个银行可以在均值语调接近中性的同时, 既有极高的分歧 (大量强正面与强负面并存), 也有极低的分歧 (报道普遍中性、乏善可陈)。因此本指数刻意与语调均值正交, 捕捉的是情感的二阶结构而非一阶水平。

【方法学与计算】
计算在面板总装阶段 (runner.py 步骤 8b disag) 完成, 是纯后处理、不额外调用任何 LLM。设该银行-年-轨道单元内, gpt54nano 判为正面的篇数为 P, 判为负面的篇数为 N (中性篇不进入本式), 则分歧指数定义为 disag = 根号下 (1 减去 ((P 减 N) 除以 (P 加 N)) 的平方)。括号内 (P−N)/(P+N) 是标准化的净极性 (net polarity), 取值落在 −1 到 +1: 全正面时为 +1, 全负面时为 −1, 正负相等时为 0。对其取平方再用 1 减、再开方, 就把"极性的绝对偏离"翻译成"分歧": 当报道一边倒 (净极性为 ±1) 时 disag=0 (零分歧), 当正负两侧完全对半 (净极性为 0) 时 disag=1 (最大分歧)。该式在几何上等价于以净极性为横坐标的单位半圆上半支, 是一条把 [−1,1] 的极性映射到 [0,1] 分歧的确定性平滑变换, 与 Janis–Fadner 系数 (步骤 7i) 共享同一 (P,N) 输入但走不同的非线性 (J-F 保号并按篇数缩放, 本式对称且无量纲、只依赖极性比而不依赖篇数绝对量)。上游篇集来自 24_herd_decay.parquet 的 df_exploded (stage 21 语义精筛后的 verified article×bank 集), 逐篇标签来自 21_tone_llms.parquet 中 gpt54nano 单模型的三分类输出。

【文献定位】
"分歧"作为资产定价与信息经济学的一等构念有深厚积累。Carlin、Longstaff 与 Matoba (2014) 直接把分歧刻画为影响资产价格与预期收益的独立状态变量, 论证分歧上升伴随更高的波动率与风险溢价; Hong 与 Stein (2007) 在综述层面把分歧模型确立为解释交易量、动量与泡沫的统一框架, 其"意见分歧"范式正是本指数试图从新闻文本侧近似的对象。Cen、Wei 与 Yang (2017) 进一步给出分歧与随后收益之间的横截面证据, 支持把分歧当作可测量、可回归的银行-年状态量。Cookson 与 Niessner (2020) 提供了分歧分解 (跨群体与群体内) 的经验框架, 提示同一"分歧"总量可由不同来源构成——这正是本家族坚持逐模型、逐轨道分列而非过早汇总的动机。就"用新闻近似投资者分歧"这一测量路径, Li 与 Luan (2025) 展示了基于新闻的分歧代理与股票收益的关联, 为本文用报道极性平衡度构造分歧提供了同源的最新计量先例。而由于本家族的情感标签来自 LLM 标注, Uma 等人 (2021) 关于"从标注分歧中学习"的综述在方法论上尤为切题: 它提醒我们标注者 (此处即不同 LLM) 之间的系统性分歧本身是信号而非噪声, 支持把 gpt54nano 单模型口径作为一条独立的、可与其它厂商并排比较的测量轨, 而不是急于用多数投票把厂商差异抹平。

【与相邻测度、per-model 与三轨口径的关系】
本家族是"逐模型稳健性"设计的一员: gpt54nano 只是情感三家 (gpt54nano / gemini31 / deepseekv4) 之一, 每家各自算出自己的 disag。这三家的同名 disag 列各自 just-identified、并排、互为稳健性、不分主次, 严禁把不同厂商的 disag 混进同一条 over-identified 的 Hansen J 过度识别检验 (CLAUDE.md 铁律); 它们只用于并排展示与跨模型一致性核查, 而不构成一组可堆叠的工具变量。同理, 本家族内部的 full / ctx / ss 三条文本轨也是各自 just-identified 并排、互为稳健性的规格稳健性梯子, 三轨同样禁混同一 over-identified Hansen J。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否计入"银行金科报道"只看 full 轨的 gpt54nano verified 判定, ctx 与 ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但每条轨的 (P,N) 与 disag 仍逐轨独立计数。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技的同句共现时, ss 文本回退为全文正文, 相应的 fallback 标记置真。分歧与语调均值 (tone)、与 Janis–Fadner、与"套话率"等相邻测度构念上正交, 不可互相替代。

## VAR: disag_gpt54nano_full

【变体差分】
本列是 full 轨实现, 也是本家族在 full-only 门控下的 canonical 头列。full 轨的文本口径为"标题 prepend 加全文正文": 在 stage 14 ctx_materializer 物化时把新闻标题拼接到正文之前构成 content_full, 原始正文列不被改动。留篇判定 (该篇是否算一篇银行金融科技报道) 完全由 full 轨的 gpt54nano verified 结果决定, 因此本列的分母篇集正是全家族的锚定宇宙, ctx 与 ss 两列的行集都是它的子集。计数上, 本列的 P 与 N 取 gpt54nano 在 full 文本上给出的正面/负面篇数 (中性篇不计入), 再代入 disag = 根号下 (1 − ((P−N)/(P+N)) 的平方) 得到银行-年分歧值。与同轨的多数投票共识测度不同, 本列刻意只用 gpt54nano 一家的判断, 使它成为一条可与 gemini31、deepseekv4 同名列做跨厂商对照的独立稳健性轨——三家 full 轨 disag 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。当该银行-年在 full 轨的有效正负篇数之和为零 (P+N=0) 时本式分母为零, 该单元分歧无定义、置缺失而非置零, 以免把"无报道"误当"零分歧"。需强调本列度量的是情感的二阶分散结构而非一阶水平: 一个 full 轨语调均值接近中性的银行-年, 既可能因报道普遍平淡而分歧极低, 也可能因强正与强负并存而分歧极高, 二者的 disag 判然不同却可能共享同一均值语调, 因此本列与同轨的 gpt54nano 语调均值列构念正交、不可互相替代。本列在跨模型 kappa 一致性核查中作为 gpt54nano 侧的 full 轨输入, 与 gemini31、deepseekv4 的 full 轨 disag 并排比对时只做水平对照与一致性诊断, 不构成可堆叠工具变量。

## VAR: disag_gpt54nano_ctx

【变体差分】
本列是 ctx 轨实现, 是 full 头列的一条 conditional-on-full 稳健性轨。ctx 文本口径为"标题 prepend 加实体上下文窗口": 在 stage 14 物化 content_ctx 时, 只保留标题与围绕目标实体的邻近窗口文本, 而非全文, 意在把情感判定聚焦于真正谈及该银行的语段、削弱长文中无关段落的稀释。因此本列的 (P,N) 取 gpt54nano 在 content_ctx 上给出的正负篇数, 代入同一 disag 平方根式。与 full 列的关键差异在于文本视窗更窄: 同一篇报道在 full 与 ctx 下可能被判出不同极性, 从而使两轨的分歧结构不完全一致——这正是把 ctx 保留为独立轨的价值, 它让研究者能检验分歧结论是否对"看全文还是看实体窗口"敏感。留篇门控为 full-only, 故本列只对已在 full 轨留篇的报道逐轨重算, 行宇宙是 full 留篇集的子集; 在开发期 T=2 的浅面板上 ctx 轨可能出现较多零方差或缺值格, 属预期退化而非缺陷。本列与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 同理它与 gemini31/deepseekv4 的 ctx 同名列构成跨厂商并排稳健性, 亦禁混同一过度识别检验。P+N=0 时置缺失而非置零。相对 full 头列, 本列的经济含义是"当只读真正谈及该银行的实体窗口时, 报道的正负平衡是否依然撕裂": 若结论在 full 与 ctx 两轨间保持一致, 则分歧不是被无关长文段落人为放大或稀释的产物, 从而增强测量的可信度; 若两轨背离, 则提示分歧对文本视窗敏感, 需在稳健性叙事中如实披露。本列同样与 gpt54nano 的 ctx 语调均值构念正交, 捕捉的是极性分散而非极性水平。

## VAR: disag_gpt54nano_ss

【变体差分】
本列是 ss 轨实现, 是三轨中视窗最严格的一条 conditional-on-full 稳健性轨。ss 文本口径为"标题 prepend 加银行与金融科技同句共现的正负 N 句窗" (句半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1): 只有当目标银行与金融科技词在同一句 (或其邻近句窗) 内共现时, 相关语段才进入 content_ss, 使情感判定最贴近"银行—金科"这一被研究关系本身。本列 (P,N) 取 gpt54nano 在 content_ss 上的正负篇数并代入同一 disag 式。ss 轨的回退语义严格镜像 ctx: 若某篇不存在银行与金融科技的同句共现, 则 content_ss 回退为全文正文、ss_is_fallback 置真, 并与家族共享 n_articles 分母; 当上游金融科技 AC 自动机为空 (FINTECH_AC=None) 时全部 fallback 标记置真, 优雅降级。相对 full 与 ctx, ss 视窗最窄, 因此在浅面板上零方差与缺值最常见 (开发期 T=2 常整轨退化为常数或缺失, 生产期 T=18 恢复正常), 属预期而非 bug。留篇门控为 full-only, 行宇宙为 full 留篇集的子集。本列与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 与三厂商同名列亦然, 一律禁混同一 over-identified Hansen J。P+N=0 时分歧无定义, 置缺失不置零。ss 轨的价值在于把情感判定压到"银行与金融科技同句共现"这一最贴近被研究关系的语境上: 若一家银行-年的分歧在如此严格的窗口下仍然显著, 说明撕裂直接源于对该银行金融科技活动本身的评价分歧, 而非泛泛的机构声誉噪声; 这条最窄轨与 full、ctx 并排, 让研究者能沿"视窗由宽到窄"检验分歧结论的稳健性梯度。本列与 gpt54nano 的 ss 语调均值构念正交, 度量极性分散而非水平。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
<!-- rendered-citations:end -->
