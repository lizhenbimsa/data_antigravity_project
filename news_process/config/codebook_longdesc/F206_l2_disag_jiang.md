---
family_id: F206
columns:
- disag_jiang_2021_ctx
- disag_jiang_2021_full
- disag_jiang_2021_ss
unit: 无量纲分歧指数 (Antweiler-Frank 一致性指标, 值域 [0, 1])
formula: "disag_jiang_2021{track} = sqrt(1 - ((avg_jiang_2021_pos_ratio{track} - avg_jiang_2021_neg_ratio{track}) / (avg_jiang_2021_pos_ratio{track} + avg_jiang_2021_neg_ratio{track}))^2); 分母为 0 → NaN"
producer: news_process/pipeline/panel/runner.py (步骤 8b 情感意见分歧 _compute_disag)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (avg_jiang_2021_pos_ratio / avg_jiang_2021_neg_ratio 三轨)
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
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, & 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
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
本家族刻画的是一个银行在一个年度内, 其相关新闻报道所携带情感信号的内部分歧程度 (disagreement), 而非情感的方向或水平。构念的直觉是: 若一家银行当年的报道在语气上高度一致 (要么普遍偏正面、要么普遍偏负面), 则市场与媒体对该银行的评价共识度高; 反之, 若正面词与负面词的出现比率旗鼓相当, 则报道呈现出显著的意见撕裂, 分歧指数取到最大。分歧本身是一个独立于均值语气的二阶矩性质的信息维度: 两家均值语气相同的银行, 其报道内部的分歧结构可以截然不同, 而这种分歧被大量金融学文献证明对定价、波动与后续回报具有独立的解释力。本家族的命名后缀 jiang_2021 指明其分歧指数的词频输入来自姜富伟、孟令超、唐国豪 (2021) 构建的中文媒体文本情绪词典, 即该分歧刻画的是"用姜富伟等 (2021) 词典读取报道时, 正负词比率之间的对立强度", 是词典法情感体系下按单部词典分解出的 per-method 分歧测度之一, 与用其他词典 (如 du_2022、bian_2021、loughran 等) 或用 LLM 投票、BERT 概率算出的同名分歧测度并列存在。

【方法学与计算】
计算沿用 Antweiler 与 Frank (2004) 提出、并在中文央行沟通与股票预测研究 (姜富伟等) 中被采用的一致性—分歧指标: 令某银行—年度的姜富伟 (2021) 词典正面词平均比率为 p、负面词平均比率为 n, 则分歧指数 = 根号下 (1 减去 ((p 减 n) 除以 (p 加 n)) 的平方)。该式值域严格落在 0 到 1 之间: 当报道全部偏正 (n 趋于 0) 或全部偏负 (p 趋于 0) 时, 括号内比值趋于正负 1, 平方为 1, 分歧指数取 0, 表示完全一致; 当正负比率相等 (p 等于 n) 时, 比值为 0, 分歧指数取 1, 表示最大分歧。分子分母的 p、n 来自上游 stage 22 词典法产出的 avg_jiang_2021_pos_ratio 与 avg_jiang_2021_neg_ratio 两列 (词级比率, 即报道中命中该词典正/负词的归一化频次在银行—年度上的平均), 分母 (p 加 n) 为 0 时函数返回 NaN, 从而对当年无任何姜富伟词典命中的银行—年度优雅缺失而非虚构一个 0 或 1。实现层面有一处防御: 词级比率虽为浮点, 但同族按篇章计数的 disag_llm 变体的输入曾为 Int8, 在正负计数之和达到 128 时会静默整数回绕, 故 _compute_disag 统一先转 float64 再运算, 对本词典比率输入是无副作用的恒等操作, 但保证了口径在生产规模负面覆盖上升后不会翻错符号。计算在 stage 40 面板构造的步骤 8b 一次性对全部六部词典、LLM 投票、单 LLM、BERT 综合与单 BERT 逐轨批量生成, 本家族即其中 jiang_2021 词典切片。

【文献定位】
情感分歧作为独立信息维度的经济学地位由一系列顶刊研究奠定。Hong 与 Stein (2007) 在其被广泛引用的综述中系统论证了异质信念 (disagreement) 是理解成交量、波动与资产价格异象的核心机制, 为把分歧从噪声提升为可定价的一阶经济变量提供了理论纲领。Cen、Wei 与 Yang (2017) 进一步实证发现分析师层面的分歧与市场反应不足交互, 对横截面股票回报有显著预测力, 印证了分歧的二阶矩测度承载着均值语气之外的增量信息。Cookson 与 Niessner (2020) 利用投资者社交网络数据把分歧分解为群体内与群体间成分, 为"用文本比率对立度近似意见分歧"这一测度路线提供了微观效度支撑, 本项目 disag_* 系列的分歧分解思路正与之呼应。在测量方法层面, Frankel、Jennings 与 Lee (2022) 直接对比机器学习与词典法在披露情感上的表现, 结论支持多方法互为稳健、不以单一方法为准的做法, 这正是本项目对同一分歧构念同时保留词典、LLM、BERT 三套 per-method 测度的方法学依据。词频输入的效度则由姜富伟、孟令超、唐国豪 (2021) 的中文媒体情绪词典及其对股票回报的预测能力背书, 而 Li 与 Luan (2025) 最新给出的基于新闻的投资者分歧测度与回报关系, 说明该构念在近期文献中仍属活跃前沿。需要强调铁律: 本家族的三轨 (full/ctx/ss) 以及跨词典/跨模型的各 per-method 分歧测度, 均为各自 just-identified 并排、互为稳健性不分主次的独立测度, 严禁把不同轨道或不同方法的分歧列混进同一个 over-identified 的 Hansen J 过度识别检验。

## VAR: disag_jiang_2021_full

【变体差分】
本列是 full 文本轨上的姜富伟 (2021) 词典分歧指数, 也是本家族的 canonical 首选轨。full 轨的文本口径为"标题 prepend 后的全文正文" (content_full), 即在 stage 14 物化时把新闻标题拼接到正文之前, 让标题词与正文词一并进入姜富伟词典的正负词计数。按 2026-06-29 确立的 full-only 留篇门控口径, 一篇报道是否被判定为"一篇银行金科报道"、从而计入银行—年度的分母, 只看其 full 轨的 LLM 判定结果; 因此 full 轨的分歧指数是行宇宙最完整、样本框最规范的主测度, ctx 与 ss 两轨降为 conditional-on-full 的稳健性轨 (其行宇宙是 full 留篇集的子集, per-track 的正负比率照单轨各自计算)。相对本家族另两列, 本列的差分维度纯粹在文本轨道: 输入的 avg_jiang_2021_pos_ratio_full 与 avg_jiang_2021_neg_ratio_full 覆盖标题加全文的完整词面, 因而对报道全局语气的分歧刻画最充分, 也最不易因窗口截断而在开发期 T=2 的稀疏样本上退化为零方差。就经济含义而言, full 轨分歧读取的是媒体对该银行整体叙事的意见撕裂: 一篇报道可能标题褒扬其金融科技布局而正文质疑其风控, 这种篇内正负并存被 full 轨的宽词面完整捕获, 反映到较高的分歧指数上。也正因为口径最宽, full 列在跨词典比较中作为 jiang_2021 词典切片的基准轨最具代表性, 便于与 du_2022、bian_2021 等其他词典的 full 轨分歧并排作 per-method 稳健性对照, 检验分歧构念是否被单一词典的词表覆盖所驱动。铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 本 full 列与 ctx/ss 列严禁混进同一个 over-identified Hansen J 过度识别检验, 亦不得与其他词典的同名分歧列混入同一 J。

## VAR: disag_jiang_2021_ctx

【变体差分】
本列是 ctx 文本轨上的姜富伟 (2021) 词典分歧指数, 相对 canonical 的 full 轨是一条 conditional-on-full 的稳健性轨。ctx 轨的文本口径为"标题 prepend 加实体上下文窗口" (content_ctx), 即只保留标题与围绕目标实体 (银行、金科词) 一定窗口内的句子, 剔除与目标实体无关的报道段落, 使姜富伟词典的正负词计数聚焦于真正谈及该银行的语境, 从而对"泛泛提及但主体不在银行"的噪声更稳健。与 full 列相比, 本列的唯一差分维度是文本轨道: 输入的正负比率来自 avg_jiang_2021_pos_ratio_ctx 与 avg_jiang_2021_neg_ratio_ctx, 覆盖面窄于 full, 分歧刻画更贴近实体相关语境但样本方差在稀疏年度更易收缩。按 full-only 门控, 本列的行宇宙是 full 留篇集的子集, per-track 正负比率在该子集上各自计算, 不借用 full 轨分母。ctx 轨的稳健性价值在于隔离主体归属噪声: 一篇同时提及多家机构的行业综述, 其对目标银行之外主体的褒贬会污染 full 轨的分歧读数, 而 ctx 轨只保留围绕目标实体窗口的句子, 使分歧指数更纯粹地反映针对该银行本身的意见对立。因此当 full 与 ctx 两轨分歧读数出现系统性背离时, 往往提示样本中存在大量非主体噪声, 这一对照本身即是对 full 主测度的诊断性稳健性检验。铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 本 ctx 列不得与 full/ss 列混入同一 over-identified Hansen J 过度识别检验, 也不得与其他词典或 LLM/BERT 的同名分歧列混入同一 J。

## VAR: disag_jiang_2021_ss

【变体差分】
本列是 ss (same-sentence) 文本轨上的姜富伟 (2021) 词典分歧指数, 是三轨中判据最严格的稳健性轨。ss 轨的文本口径为"标题 prepend 加银行与金科词同句共现正负 N 句窗" (content_ss, 窗半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 即只在目标银行与金融科技词出现在同一句 (含相邻窗) 的语境内取词, 计算最贴近"银行—金科"直接关联叙事的分歧。ss 轨的回退语义镜像 ctx: 当某报道不存在银行与金科词的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 当金科词表 FINTECH_AC 为 None 时该轨优雅整体降级。相对 full/ctx, 本列唯一差分在文本轨道所用的更严判据, 分歧刻画的语境最窄, 因此在开发期 T=2 上最易出现零方差或全 NaN 退化, 属预期而非缺陷 (生产 T=18 恢复正常)。ss 轨的稳健性价值在于把分歧构念收窄到"银行与金融科技直接绑定"的叙事内: 当报道在同一句里把某银行与金科词并置时, 其正负词对立最能代表市场对该银行金融科技转型评价的分歧, 这与本项目银行—金科主线的处理变量语义最贴合; 但代价是可用词面最少, 分歧估计的样本方差最大、最脆弱。因此 ss 列宜作为方向性稳健性证据而非精度基准解读: 若 full/ctx/ss 三轨分歧读数在符号与量级上大体一致, 则可确认分歧结论不被文本轨道选择所驱动。铁律: 三轨各自 just-identified 并排、互为稳健性不分主次, 本 ss 列严禁与 full/ctx 列以及其他词典/模型的同名分歧列混进同一 over-identified Hansen J 过度识别检验。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
<!-- rendered-citations:end -->
