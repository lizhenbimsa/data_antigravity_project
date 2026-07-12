---
family_id: F168
columns:
- deepseekv4_cont_hw_sum_ctx
- deepseekv4_cont_hw_sum_full
- deepseekv4_cont_hw_sum_ss
- gemini31_cont_hw_sum_ctx
- gemini31_cont_hw_sum_full
- gemini31_cont_hw_sum_ss
- gpt54nano_cont_hw_sum_ctx
- gpt54nano_cont_hw_sum_full
- gpt54nano_cont_hw_sum_ss
unit: 羊群衰减加权的连续情感数值之和 (无量纲; bank-year 内逐篇 置信度×符号情感×herd_weight 求和的分子量, 非 [-1,1] 有界比值)
formula: "{short}_cont_hw_sum{track} = Σ_{i∈bank-year} ({short}_cont{track}_i × herd_weight{track}_i); 其中 {short}_cont{track} = {short}_score{track} × {short}_sentiment_confidence{track}, score ∈ {-1,0,1}; herd_weight{track} = 1/(1+n_similar{track}), n_similar = 该篇发布前 7 天窗口内同轨 TF-IDF 余弦相似度 ≥ 阈值的前驱篇数"
producer: news_process/pipeline/panel/runner.py (步骤 3d HW 加权物化 {short}_cont_hw{track}) ; news_process/pipeline/panel/encode.py (bank-year sum 聚合 {short}_cont_hw_sum{track}) ; 上游 news_process/pipeline/sentiment/tone_llms.py (stage 21 逐模型情感与置信度) + news_process/pipeline/sentiment/herd_decay.py (stage 24 herd_weight)
upstream:
- 21_tone_llms.parquet
- 24_herd_decay.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: arXiv
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"单一大模型判定的、经羊群抄袭衰减加权后的连续情感数值在 bank-year 内的分子和"。它衔接三个独立环节: 第一环是文章级的逐模型连续情感 {short}_cont{track}, 由 stage 21 (pipeline/sentiment/tone_llms.py) 产出; 第二环是 stage 24 (pipeline/sentiment/herd_decay.py) 给每篇报道估计的羊群衰减权重 herd_weight{track}; 第三环是 bank-year 聚合时对二者乘积逐篇求和。三个模型分别是 gpt54nano (gpt-5.4-nano, 经 yunwu 中转)、gemini31 (gemini-3.1-flash-lite, 经 yunwu 中转) 与 deepseekv4 (deepseek-v4-flash, 直连 api.deepseek.com); 三家在 stage 21 各自独立对同一篇报道并发打分, 是刻意保留的跨厂商稳健性轨, 与它们经多数投票合成的共识测度 (llm_vote 族, 见姊妹家族 F383) 分处两个命名域, 不可相互替代。所谓"连续"是相对于三值离散码 {-1,0,1} 而言: 文章级 {short}_cont{track} = {short}_score{track} × {short}_sentiment_confidence{track}, 即把模型给出的符号情感乘以它自报的置信度, 得到落在 [-1,1] 的实值信号; 情感码本身在该模型自报 verified=False 时被置为缺失, 从而使不可信判定不进入下游任何求和。所谓"羊群加权"来自这样一个事实: 同一家银行的同一条消息常被多家媒体在数日内反复转抄, 若逐篇等权计入, 情感指标会被转抄件注水; herd_decay 对每篇报道数出"它发布前 7 天窗口内有多少篇同轨 TF-IDF 余弦足够相似的前驱", 记为 n, 再把权重打折为 1/(1+n)——原创首发权重为 1, 第十篇抄稿权重仅约十分之一。本家族的九列即三模型 × full/ctx/ss 三轨的该分子和; 它们是构造羊群加权情感比值 {short}_tone_hw{track} 的分子部件 (分母是同轨有效篇数的羊群权重之和), 因此本身不是有界比值, 而是可随篇数增长的加总量, 使用时通常与对应分母同取或直接改用已归一的 tone 列。

【方法学与计算】
计算链路严格分三步落地。stage 21 对每篇报道以三种输入文本分别请求三家模型: full 轨输入为标题拼接全文正文, ctx 轨为标题拼接含目标银行句的上下文窗口, ss 轨为标题拼接"银行与金科词同句共现"的句窗 (无共现时镜像 ctx 回退全文正文并置 ss_is_fallback=True)。三轨文本在 stage 14 (ctx_materializer) 统一以 prepend_title 物化, 标题已内嵌, 下游不再另设独立标题轨。请求在 temperature=0 下进行, prompt 冻结为 v8 版本并按命中键缓存, 从而保证跨 run 的字节级可复现。encode 层先把各家情感码映射为 {-1,0,1}, 乘以自报置信度得到 {short}_cont{track}; runner 步骤 3d 再逐篇乘以同轨 herd_weight{track} 得到 {short}_cont_hw{track}; 最终在 bank-year groupby 上对该列求和得到本家族列。羊群权重来自逐轨独立的 TF-IDF 余弦: full 轨看标题加全文的相似, ctx 轨只看与目标银行相关那段文字的相似, ss 轨只看银行与金科同句那段文字的相似, 三轨各自打分互不借用。留篇门控采用 full-only 口径: 一篇报道是否被计为"一篇银行金科报道"只看 full 轨的 llm 精筛结果, ctx 与 ss 因此是"条件于 full 留篇"的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但各轨的 per-track 列仍按各自文本独立计算。

【文献定位】
本家族的方法学定位落在"用生成式大模型做金融文本标注与情感度量"这一近年迅速成熟的方法族。de Kok (2025) 在 Management Science 系统论证了如何把生成式大模型规范地用于会计研究文本分析, 明确提出温度归零、提示冻结与结果缓存这一套可复现范式, 与本家族在 stage 21 的 temperature=0、prompt v8 冻结、命中键缓存做法完全同构; Siano (2025) 同刊进一步展示大模型在捕捉词语上下文语义上相对词典法的增益, 支撑本项目在词典法之外并置大模型情感轨的设计。Gilardi 等 (2023) 用大样本证据表明生成式模型在标注任务上可超过众包工人, 为大模型作情感标注器提供效度背书; Carlson 与 Burbano (2026) 则从管理学研究规范角度给出使用大模型标注数据的操作指南与风险警示, 呼应本项目对 verified 门控与置信度加权的谨慎处理。跨模型三角验证与多家投票的思路可追溯到 Kamen 与 Kamen (2025) 对大模型集成多数投票的实证支持——但需强调, 本家族是各家 per-model 的独立轨而非投票共识, 二者刻意分列。针对中文语料, Lan 等 (2025) 展示了大模型在中文细粒度金融实体级情感上的可用性, 与本项目的中文银行金科语境相契合。作为方法学对照, Huang、Wang 与 Yang (2023) 的 FinBERT 代表判别式微调路线, 本项目将其保留为 BERT 情感轨作交叉印证。至于羊群加权所要抑制的"媒体转抄放大情感信号"这一现象, 其经济学根源可回到 Tetlock (2007) 关于媒体语调如何进入市场的经典证据: 正因媒体报道的信息含量会被重复传播放大, 才需要用衰减权重把转抄件的边际贡献压低。就识别纪律而言, 本家族三个模型的九列构成两条正交的稳健性维度 (跨模型 × 三轨), 每一维内的各成员各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同模型或不同轨的列混进同一个 over-identified 的 Hansen J 过度识别检验; per-model 的降级也各自独立, 某一家缺席仅使其自身族列缺失, 不牵连其它家。

## VAR: deepseekv4_cont_hw_sum_ctx

【变体差分】
本列取模型 = deepseekv4 (即 deepseek-v4-flash, 在 stage 21 三家中唯一直连 api.deepseek.com 而不经 yunwu 中转), 轨道 = ctx。ctx 轨的文本是标题拼接"含目标银行句的上下文窗口", 只保留与目标银行邻近的那段文字送模型判定, 因此比 full 轨更聚焦于涉及该银行的局部语境, 相应地其羊群权重也只依据 ctx 段文字的同轨 TF-IDF 余弦相似度计算。该列的数值是 bank-year 内逐篇 (deepseekv4 的符号情感 × 自报置信度 × ctx 轨 herd_weight) 之和, 属分子加总量而非有界比值, 与其分母 (ctx 轨有效篇数的羊群权重和) 配合才还原为羊群加权情感比值 deepseekv4_tone_hw_ctx。因留篇门控为 full-only, 本列的行宇宙是 full 留篇集的子集, 仅对同时具备 ctx 判定的报道累加。

用大白话说, ctx 轨相当于给模型一副"只看银行附近文字"的眼镜: 一篇长报道里往往夹着大量与目标银行无关的行业背景与宏观议论, ctx 轨把这些噪声段落先剔掉, 只让模型对紧挨着银行名出现的那几句话表态, 从而得到一个更贴近"这家银行本身"的情感读数。与 full 轨相比, 它牺牲了少量跨段落的语境信息, 换来对无关情感串扰的抑制, 因此常作为 full 轨结果的稳健性对照。就识别纪律而言, deepseekv4 与 gemini31、gpt54nano 属跨厂商稳健性并排, ctx 与 full、ss 属三轨稳健性并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨的同名列混进同一个 over-identified Hansen J 过度识别检验; deepseekv4 若整体缺席仅使本族列缺失而不牵连另两家。

## VAR: deepseekv4_cont_hw_sum_full

【变体差分】
本列取模型 = deepseekv4 (deepseek-v4-flash, 直连 api.deepseek.com), 轨道 = full。full 轨的文本是标题拼接全文正文, 是三轨中信息量最完整的输入, 也是 full-only 留篇门控的判定所在——一篇报道能否进入 bank-year 累加, 取决于其 full 轨的大模型精筛结果, 故本列的行宇宙即该模型在 full 轨留篇集上的取值。数值为 bank-year 内逐篇 (deepseekv4 符号情感 × 自报置信度 × full 轨 herd_weight) 之和; 其中 full 轨羊群权重依据标题加全文的同轨 TF-IDF 余弦, 对被多家媒体在 7 天内反复转抄的原文按 1/(1+n) 打折, 抑制转抄件对情感总量的注水。该列是分子加总量, 与 full 轨羊群权重分母配合还原为 deepseekv4_tone_hw_full。识别纪律上, deepseekv4 与另两家跨厂商并排、full 与 ctx/ss 三轨并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨列混入同一 over-identified 的 Hansen J 过度识别集; per-model 独立降级, deepseekv4 缺席不牵连 gemini31、gpt54nano。

用大白话说, 这一列相当于让唯一走独立厂商通道的 deepseekv4 通读整篇报道后打分, 再按抄袭衰减折算后在全年层面加总。把它单列出来的意义在于: 若三家模型在 full 轨上得到的银行金科情感走势一致, 说明结论不是某一家模型或某一条网络通道的偶然产物; deepseekv4 因路由独立, 恰好为这种跨通道稳健性提供了最干净的一票。连续编码同时让模型高把握的判定贡献接近满分、模棱两可的判定只贡献很小的绝对值, 使加总后的情感总量更能反映确凿判定而非勉强的猜测。

## VAR: deepseekv4_cont_hw_sum_ss

【变体差分】
本列取模型 = deepseekv4 (deepseek-v4-flash, 直连 api.deepseek.com), 轨道 = ss。ss 轨的文本是标题拼接"目标银行与金科词在同一句内共现"的句窗 (半径由 config 的 ss_sentence_radius 控制, 默认 ±1 句); 当某篇报道全篇没有银行与金科同句共现时, ss 轨镜像 ctx 的回退语义退回全文正文并置 ss_is_fallback=True, 以优雅降级而非清空。因此本列刻画的是"聚焦银行金科交汇语境"下 deepseekv4 判定的连续情感, 其羊群权重亦只依据 ss 段文字的同轨 TF-IDF 余弦。数值为 bank-year 内逐篇 (deepseekv4 符号情感 × 置信度 × ss 轨 herd_weight) 之和, 属分子加总量, 与 ss 轨羊群权重分母配合还原为 deepseekv4_tone_hw_ss。留篇门控为 full-only, 故 ss 轨是条件于 full 留篇的稳健性轨, 行宇宙为 full 留篇集子集。识别纪律上, ss 与 full/ctx 三轨并排、deepseekv4 与另两家跨厂商并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它轨或其它模型列混进同一 over-identified 的 Hansen J; deepseekv4 独立降级不牵连他家。

用大白话说, ss 轨是三轨里最挑剔的一副眼镜, 它只认"银行和金科词出现在同一句话里"的那一小段文字, 最贴近本研究关心的"这家银行在谈金融科技"这一构念; 代价是符合条件的句子相当稀疏, 很多报道会触发回退而退回全文正文。因此本列在样本较薄时波动更大, 应与 deepseekv4 的 full、ctx 两轨并读, 三者相互印证而非彼此替代; 回退语义严格镜像 ctx, 保证无同句共现的报道被优雅降级而非直接清空。

## VAR: gemini31_cont_hw_sum_ctx

【变体差分】
本列取模型 = gemini31 (即 gemini-3.1-flash-lite, 经 yunwu 中转请求), 轨道 = ctx。与 deepseekv4 的直连路由不同, gemini31 与 gpt54nano 同走 yunwu 端点, 但三家在 stage 21 各自独立并发打分, 互不参照, 是刻意保留的跨厂商稳健性成员。ctx 轨文本为标题拼接含目标银行句的上下文窗口, 只对涉及该银行的局部语境判定情感, 其羊群权重依据 ctx 段文字的同轨 TF-IDF 余弦。本列数值为 bank-year 内逐篇 (gemini31 符号情感 × 自报置信度 × ctx 轨 herd_weight) 之和, 是构造 gemini31_tone_hw_ctx 的分子加总量而非有界比值。留篇门控为 full-only, 本列行宇宙为 full 留篇集子集。识别纪律上, gemini31 与 deepseekv4、gpt54nano 跨厂商并排, ctx 与 full/ss 三轨并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨的同名列混进同一 over-identified 的 Hansen J 过度识别检验; gemini31 独立降级, 缺席仅使本族列缺失而不牵连另两家。

用大白话说, 本列是让经 yunwu 中转的 gemini31 戴上"只看银行附近文字"的眼镜后给出的情感, 再按抄袭衰减折算加总。它与 deepseekv4、gpt54nano 的同名列构成 ctx 轨的跨模型三票, 用于检验该轨下的银行金科情感是否稳健于模型选择; 由于三家分属不同厂商、训练语料与判定风格各异, 它们在同一批报道上的一致程度本身就是测度可信度的一个侧写, 也是本项目坚持并置三家而非只信一家的根本理由。

## VAR: gemini31_cont_hw_sum_full

【变体差分】
本列取模型 = gemini31 (gemini-3.1-flash-lite, 经 yunwu 中转), 轨道 = full。full 轨文本为标题拼接全文正文, 是 full-only 留篇门控的判定轨, 故本列行宇宙即 gemini31 在 full 留篇集上的取值。数值为 bank-year 内逐篇 (gemini31 符号情感 × 自报置信度 × full 轨 herd_weight) 之和; full 轨羊群权重依据标题加全文的同轨 TF-IDF 余弦, 把 7 天内被反复转抄的原文按 1/(1+n) 折价, 抑制媒体转抄对情感总量的放大。本列是分子加总量, 与 full 轨羊群权重分母配合还原为 gemini31_tone_hw_full。需强调, gemini31 与 gpt54nano 虽共用 yunwu 路由, 但作为不同厂商的不同模型仍是独立的稳健性轨, 与共识投票列分处两个命名域。识别纪律上, gemini31 与另两家跨厂商并排、full 与 ctx/ss 三轨并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨列混入同一 over-identified 的 Hansen J; per-model 独立降级, gemini31 缺席不牵连 deepseekv4、gpt54nano。

用大白话说, 连续编码让 gemini31 在判定方向之余还报出把握程度, 高把握的负面报道贡献接近负一、模棱两可的只贡献很小的绝对值, 求和后的分子因而对模型的犹豫自动打了折。本列即 gemini31 在信息最全的 full 轨上、经抄袭衰减加权后的这一情感总量, 是三家 full 轨读数中供跨模型比对的一票; 与 gpt54nano 虽共用 yunwu 通道, 但作为不同厂商的不同模型, 二者的判定并不冗余, 一致时更能佐证结论的稳健。

## VAR: gemini31_cont_hw_sum_ss

【变体差分】
本列取模型 = gemini31 (gemini-3.1-flash-lite, 经 yunwu 中转), 轨道 = ss。ss 轨文本为标题拼接"银行与金科词同句共现"的句窗 (默认半径 ±1 句); 无共现篇镜像 ctx 回退全文正文并置 ss_is_fallback=True, 优雅降级不清空。本列刻画的是聚焦银行金科交汇语境下 gemini31 判定的连续情感, 羊群权重只依据 ss 段文字的同轨 TF-IDF 余弦。数值为 bank-year 内逐篇 (gemini31 符号情感 × 置信度 × ss 轨 herd_weight) 之和, 属分子加总量, 与 ss 轨羊群权重分母配合还原为 gemini31_tone_hw_ss。留篇门控为 full-only, ss 轨为条件于 full 留篇的稳健性轨, 行宇宙为 full 留篇集子集。识别纪律上, ss 与 full/ctx 三轨并排、gemini31 与 deepseekv4/gpt54nano 跨厂商并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它轨或其它模型列混进同一 over-identified 的 Hansen J 过度识别集; gemini31 独立降级不牵连他家。

用大白话说, 本列是让 gemini31 只盯着"银行与金科同句"那一小段话打分的结果, 语境最纯而样本最薄, 遇到无同句共现的报道会镜像 ctx 回退到全文正文。把它单列出来, 是为了在最严格的语境窗口下再验一次银行金科情感是否稳健于模型选择, 与 deepseekv4、gpt54nano 的 ss 轨列三票并读; 因样本稀疏, 本列在小样本银行年上尤应谨慎解读, 优先与 full、ctx 两轨相互印证。

## VAR: gpt54nano_cont_hw_sum_ctx

【变体差分】
本列取模型 = gpt54nano (即 gpt-5.4-nano, 经 yunwu 中转), 轨道 = ctx。gpt54nano 与 gemini31 同走 yunwu 端点、与 deepseekv4 的直连路由相区别, 三家在 stage 21 各自独立并发打分, 是跨厂商稳健性的第三个成员。ctx 轨文本为标题拼接含目标银行句的上下文窗口, 聚焦涉及该银行的局部语境, 羊群权重依据 ctx 段文字的同轨 TF-IDF 余弦。本列数值为 bank-year 内逐篇 (gpt54nano 符号情感 × 自报置信度 × ctx 轨 herd_weight) 之和, 是构造 gpt54nano_tone_hw_ctx 的分子加总量而非有界比值。留篇门控为 full-only, 本列行宇宙为 full 留篇集子集。识别纪律上, gpt54nano 与 deepseekv4、gemini31 跨厂商并排, ctx 与 full/ss 三轨并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨的同名列混进同一 over-identified 的 Hansen J 过度识别检验; gpt54nano 独立降级, 缺席仅使本族列缺失而不牵连另两家。

用大白话说, 本列是让经 yunwu 中转的 gpt54nano 戴上"只看银行附近文字"的眼镜后给出的情感, 再按抄袭衰减折算加总。它是 ctx 轨跨模型三票中的一票, 与 deepseekv4、gemini31 的同名列并读; 三家判定越接近, 说明 ctx 轨下的银行金科情感越不依赖某一家模型的风格。连续编码同时对模型的把握程度做了折算, 让确凿判定在全年总量里占更大分量, 犹豫判定影响被压低。

## VAR: gpt54nano_cont_hw_sum_full

【变体差分】
本列取模型 = gpt54nano (gpt-5.4-nano, 经 yunwu 中转), 轨道 = full。full 轨文本为标题拼接全文正文, 是 full-only 留篇门控的判定轨, 故本列行宇宙即 gpt54nano 在 full 留篇集上的取值; 在三家 per-model 的 full 轨列中, 本列常作为跨厂商情感度量对照的基准之一。数值为 bank-year 内逐篇 (gpt54nano 符号情感 × 自报置信度 × full 轨 herd_weight) 之和; full 轨羊群权重依据标题加全文的同轨 TF-IDF 余弦, 把 7 天内被反复转抄的原文按 1/(1+n) 折价以抑制情感总量注水。本列是分子加总量, 与 full 轨羊群权重分母配合还原为 gpt54nano_tone_hw_full。识别纪律上, gpt54nano 与另两家跨厂商并排、full 与 ctx/ss 三轨并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它模型或其它轨列混入同一 over-identified 的 Hansen J; per-model 独立降级, gpt54nano 缺席不牵连 deepseekv4、gemini31。

用大白话说, 本列是让 gpt54nano 通读整篇报道后打分、再按抄袭衰减折算加总的全年情感总量。因 full 轨是留篇主轨, 三家的 full 轨列常被当作跨模型比对的基准: 若 gpt54nano 与另两家在此轨上走势一致, 便可排除结论由单一模型驱动的担忧。连续编码让高把握判定贡献更大、犹豫判定贡献更小, 抄袭衰减又把被反复转抄的稿件折价, 两重处理叠加后, 本列比简单的情感篇数计数更能反映真正原创且确凿的银行金科情绪。

## VAR: gpt54nano_cont_hw_sum_ss

【变体差分】
本列取模型 = gpt54nano (gpt-5.4-nano, 经 yunwu 中转), 轨道 = ss。ss 轨文本为标题拼接"银行与金科词同句共现"的句窗 (默认半径 ±1 句); 无共现篇镜像 ctx 回退全文正文并置 ss_is_fallback=True, 以优雅降级替代清空。本列刻画聚焦银行金科交汇语境下 gpt54nano 判定的连续情感, 羊群权重只依据 ss 段文字的同轨 TF-IDF 余弦。数值为 bank-year 内逐篇 (gpt54nano 符号情感 × 置信度 × ss 轨 herd_weight) 之和, 属分子加总量, 与 ss 轨羊群权重分母配合还原为 gpt54nano_tone_hw_ss。留篇门控为 full-only, ss 轨为条件于 full 留篇的稳健性轨, 行宇宙为 full 留篇集子集。识别纪律上, ss 与 full/ctx 三轨并排、gpt54nano 与 deepseekv4/gemini31 跨厂商并排, 两维各自 just-identified、互为稳健性不分主次, 严禁把本列与其它轨或其它模型列混进同一 over-identified 的 Hansen J 过度识别集; gpt54nano 独立降级不牵连他家。

用大白话说, ss 轨对 gpt54nano 也是最挑剔的一副眼镜, 只认银行与金科同句那一小段文字, 语境最纯而样本最薄, 无共现时镜像 ctx 回退全文正文。本列作为 ss 轨跨模型三票中的一票, 与 deepseekv4、gemini31 的 ss 轨列并读, 用于在最严格窗口下再验一次银行金科情感的模型稳健性; 因回退比例较高且样本稀疏, 解读时应结合 full、ctx 两轨与三家的一致程度综合判断, 不宜单独据本列下强结论。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
