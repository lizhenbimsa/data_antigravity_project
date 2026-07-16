---
family_id: F275
novelty_exempt_rationale: "exc_ 前缀家族是'剔除疑似退出覆盖媒体'的样本稳健性衍生变体, 其情感测度定义直接沿用母族 yao_2021 词典 (及三重轨道/加权梯子), 本身不构成独立新构念, 学术依据已由母族词典文献及词典法情感分析文献覆盖, 无需单独追新引文。"
columns:
- exc_yao_2021_score_ctx
- exc_yao_2021_score_full
- exc_yao_2021_score_hw_ctx
- exc_yao_2021_score_hw_full
- exc_yao_2021_score_hw_ss
- exc_yao_2021_score_ss
- exc_yao_2021_score_w_ctx
- exc_yao_2021_score_w_full
- exc_yao_2021_score_w_ss
unit: 无量纲情感得分 (bank-year 聚合均值, 值域约 [-1, +1]; 排除疑似退出覆盖媒体子样本)
formula: "exc_yao_2021_score{sfx}{track} = mean_{i in bank-year, media not ceased}( yao_2021_score{sfx}{track}_i ); 其中 sfx='' 为原始归一化得分, sfx='_hw' 为跟风衰减加权 (article score × herd_weight{track}), sfx='_w' 为提及密度价值加权 (article score × mention_density); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (detect_defacto_cessation + C.4 exc_* 动态聚合); 文章级 yao_2021_score 由 news_process/pipeline/sentiment/tone_words.py::classify_batch 产出; 加权乘积列在 news_process/pipeline/panel/runner.py 预计算
upstream:
- 22_tone_words.parquet (yao_2021_score{track} 文章级归一化得分)
- 24_herd_decay.parquet (herd_weight{track} 跟风衰减权重)
- 40_article_bank_level.parquet (mention_density 提及密度权重 + _is_ceased_media 退出媒体标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"在剔除疑似退出覆盖的媒体之后, 目标银行当年金融科技相关报道所呈现的字典法情感语调水平", 是主线情感测度的一条媒体样本稳健性轨。构念由两个正交的部件叠合而成: 其一是词典侧的情感极性, 采用姚加权等 (2021) 编制的金融领域中文情绪词典 (代号 yao_2021), 该词典是本项目并列装载的六部中文金融情感词典之一 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran 中文主译本), 各词典独立打分、互为稳健性、不分主次; 其二是样本侧的退出媒体剔除, 即把在样本期内疑似停止对该话题进行覆盖的媒体来源整体从聚合分母中移除, 只保留仍在持续覆盖的"存活"媒体所贡献的报道。前缀 exc_ 即 "excluding ceased media" 的缩写, 标示这条稳健性口径。之所以要构造这样一条轨, 是因为媒体的进入与退出会系统性地改写银行被报道的语调结构: 若某些立场偏正面或偏负面的媒体在样本后期停止覆盖, 未加处理的全样本均值就会掺入由样本构成变动 (composition change) 驱动的伪趋势, 而非银行基本面或市场情绪的真实变化。把疑似退出媒体剔除后重算同一情感均值, 就为核心情感变量提供了一个"样本构成不因媒体退出而漂移"的对照读数, 用以检验主结论是否被少数退出媒体的语调所驱动。

【方法学与计算】
计算分三层。第一层是文章级词典打分: tone_words.py 的 classify_batch 对每篇报道逐轨调用打分函数, 在分词后遍历命中词, 对每个情感词取其基准极性得分, 并施加三条中文语言学规则——否定词翻转符号、程度副词调节幅值、转折词 (adversative) 提升被强调分句的权重; 逐词的最终贡献累加为 total_score, 归一化得分 = total_score / Σ|final_score| ∈ [-1, +1], 即以加权幅度和为分母, 使净贡献为零的词把语调拉向中性而非被硬性剔除。第二层是加权变体: runner.py 在聚合前预计算两种文章级加权乘积——跟风衰减加权 (_hw) 把文章得分乘以该文的 herd_weight (对与既往报道高度相似、疑似"跟风"的冗余报道降权, 削弱媒体羊群效应对语调的重复计入), 价值加权 (_w) 把文章得分乘以 mention_density (提及密度, 让银行被更密集提及的报道获得更大权重, 是暴露度价值加权的实现)。第三层是 bank-year 聚合: attention_media.py 先经 detect_defacto_cessation 以"话题覆盖退出"为停刊的保守代理识别退出媒体集 (数据实测退出 ∪ 与 NPPA 名录交叉验证, 保守取并集), 标记 _is_ceased_media, 再在存活媒体子样本 (df_alive) 上按 (target_bank, year) 对相应文章级列取均值, 动态发现所有以情感前缀开头的列并生成对应 exc_* 列。需强调该退出识别是"覆盖退出"而非经证实的出版停刊, 论文中应表述为保守的稳健性口径而非严格停刊口径。缺样本格保持 NaN (不零填), 以免把"该银行当年无存活媒体报道"误读为语调为零。

【文献定位】
字典法情感度量在会计与金融文本分析中久经检验: Hwang & Kim (2017) 证明文本层面的书写质量与市场估值系统相关, 确立了从公开文本抽取情感/风格信号具有资产定价含义这一命题; Taboada 等 (2011) 系统阐述了基于词典的情感分析方法学, 尤其是否定、程度副词与转折结构对极性合成的作用, 正是本项目三条语言学规则的方法论原型。就中文金融语域而言, Du 等 (2022) 指出通用情感词典在专业金融语境下会失真, 需要领域与语言双重专用的中文金融情感词典, 这一论证为本项目并列装载多部中文金融词典 (含 yao_2021) 并令其互为稳健性提供了直接依据; 近期的 Ma 等 (2025) 与 Sun 等 (2025) 进一步在细粒度中文投资者情绪词典构建与"词典知识 + 中性特征"融合方向上推进, 说明词典法在深度学习时代仍是可解释、可复现的基线测度。Barbaglia 等 (2025) 展示了词典法在经济文本上的稳健表现, Frankel 等 (2022) 则以机器学习与词典法的直接对照说明两类方法各有效度边界, van Atteveldt 等 (2021) 通过人工标注、众包、词典与机器学习的效度比较提醒任何单一情感测度都需要交叉验证——这为本项目将词典法、LLM 三家投票、BERT 三模型并置为互为稳健性的多测度架构提供了外部依据。退出媒体剔除的样本稳健性动机则呼应了媒体覆盖的进入退出会改写被报道主体信息环境的一支实证文献。

## VAR: exc_yao_2021_score_full

【变体差分】
本列是家族的参照读数: 未加权 (无 _hw / _w 后缀)、full 轨。full 轨的文本口径 = 标题 prepend 到全文正文, 即银行相关报道的完整篇章。聚合口径 = 在剔除疑似退出覆盖媒体后的存活媒体子样本上, 对文章级 yao_2021_score_full 按 bank-year 取算术均值。相对家族其它列, 本列的区别在于: 权重维度取"等权"(每篇存活报道等权重进入均值, 不乘 herd_weight 也不乘 mention_density), 轨道维度取 full (最宽文本, 信噪比高但可能掺入与银行金科主题弱相关的段落)。full 轨对应留篇门控的判定基准——一篇报道是否算作"银行金科报道"由 full 轨 LLM 判定 (llm_verified_full, 2026-06-29 full-only 口径), ctx/ss 是 conditional-on-full 的子集轨; 因此 full 轨的行宇宙即留篇集本身。三轨 (full/ctx/ss) 与三种加权 (等权/hw/w) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨或不同加权的同名列混入同一 over-identified Hansen J 方程。本列宜作为该家族在回归中的首要读数, 其余八列作为围绕它的样本×轨道×加权稳健性梯子。在实证使用上, 建议先用本列建立基准回归系数, 再依次替换为 ctx/ss 轨与 hw/w 加权变体, 逐一比较系数符号与显著性是否一致, 若九列结论方向一致但幅度有别, 即构成"退出媒体剔除下语调结论稳健"的有力证据; 若某一维度 (轨道或加权) 使结论逆转, 则需在稳健性表中如实披露该维度对识别的敏感性, 而非选择性汇报。本列与未剔除退出媒体的对应版本 (yao_2021_score) 相比, 差异纯粹来自样本构成——退出媒体的报道被整体移出分母, 因此若两者数值高度接近, 说明退出媒体的语调结构与存活媒体并无系统性差异, 反之则提示论文正文的核心结果部分依赖于已退出覆盖的媒体样本, 应在稳健性章节明确讨论。

## VAR: exc_yao_2021_score_ctx

【变体差分】
本列与参照列 exc_yao_2021_score_full 的唯一差异在文本轨道: 由 full 改为 ctx。ctx 轨 = 标题 prepend + 实体上下文窗口, 即只保留标题加上目标银行实体附近的局部文本 (而非全文), 在 stage 14 ctx_materializer 物化为 content_ctx。其构念用意是把语调计算聚焦到"确实谈及该银行"的局部, 剔除全文中与银行金科弱相关的背景段落对情感的稀释或污染, 因而相对 full 轨更保守、更贴近银行本身的语调, 代价是可用文本更短、方差更大、极端值更易出现。权重维度仍取等权 (不乘 herd_weight, 不乘 mention_density), 聚合仍为存活媒体子样本上的 bank-year 均值。ctx 轨在 full-only 门控下降为 conditional-on-full 的稳健性测度轨, 其行宇宙是 full 留篇集的子集, per-track 列照常计算。本列与 full / ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J; 它回答的稳健性问题是"把情感读取范围收窄到银行实体上下文后, 剔除退出媒体的语调结论是否依然成立"。ctx 窗口的边界由实体识别模块框定, 窗口大小并非任意选择, 而是与银行实体在文本中的出现位置绑定, 因此不同报道的 ctx 文本长度天然参差不齐, 这也是 ctx 轨方差通常大于 full 轨的结构性原因。使用者应留意: 当某银行当年存活媒体报道数偏少且 ctx 窗口极短时, 单篇极端情感词的命中会对 bank-year 均值产生比 full 轨更大的杠杆效应, 因此在小样本 bank-year 格点上宜同时参照 full 轨读数, 避免把 ctx 轨的噪声误读为真实语调变化; 在生产 T=19 全量语料下, 报道密度上升, 该杠杆效应会显著减弱。

## VAR: exc_yao_2021_score_ss

【变体差分】
本列与参照列的差异同样在文本轨道: 取 ss (同句共现) 轨。ss 轨 = 标题 prepend + 目标银行与金融科技词在同一句子内共现的窗口 (句半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 ±1 句), 是三轨中最严格的文本口径, 只在银行与金科概念真正同句耦合处读取语调, 力图刻画"银行—金科"这一特定关系上的情感, 而非银行泛报道情感。ss 的回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True; 当金科 AC 自动机为 None 时该轨全部优雅降级。因此 ss 轨在稀疏语料 (如盘上 T=2 开发样本) 上可能大量回退甚至零方差退化, 属预期行为, 生产 T=19 语料下才充分展开。权重维度取等权, 聚合为存活媒体子样本 bank-year 均值。ss 与 full / ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J。本列回答"把语调读取收紧到银行与金科同句关系上后, 退出媒体剔除的结论是否稳健"。需特别提醒使用者: 由于回退语义共享 n_articles 分母 (回退与非回退报道均计入同一分母), 当某银行当年的银行∧金科同句共现比例很低时, ss 轨实质上退化为接近 full 轨的读数, 此时 ss 与 full 的差异主要来自"哪些报道触发了回退"而非语调本身的测度差异; 论文正文引用 ss 轨结果时应结合 ss_is_fallback 的回退占比一并披露, 避免把回退主导的样本误解读为"银行—金科关系语调"的精确刻画。该列在生产语料下随金科覆盖密度上升而更具区分力。

## VAR: exc_yao_2021_score_hw_full

【变体差分】
本列在参照列 exc_yao_2021_score_full 的基础上增加跟风衰减 (herd-decay) 加权维度: 文章级得分先乘以该文的 herd_weight_full 再进入 bank-year 均值。herd_weight 由 stage 24 herd_decay 计算, 对与同期既往报道 TF-IDF 相似度高、疑似"跟风转载/复述"的冗余报道赋予较小权重 (权重 = 1/(1+相似邻居计数)), 从而抑制媒体羊群效应把同一条语调重复计入面板。相对等权的 full 参照列, 本列把"独立原创报道"相对"跟风报道"的语调贡献放大, 度量的是去冗余后的净情感信号。文本轨道仍取 full (标题 + 全文), 样本仍为剔除退出媒体后的存活子样本。跟风衰减加权 (_hw)、价值加权 (_w) 与等权三种加权方案互为稳健性、不分主次, 各自 just-identified 并排, 与三轨铁律同构——严禁把 hw / w / 等权同名列或不同轨列混入同一 over-identified Hansen J。本列回答"当把疑似跟风的重复报道降权后, 剔除退出媒体的情感结论是否依然成立"。构念上, herd_weight 处理的是媒体生态中常见的"一稿多发/转载摘编"现象——同一事件经不同媒体近乎逐字复述会在未加权均值中被重复计入多次, 人为放大该事件语调对 bank-year 均值的影响; 本列通过降权抑制这一重复计入, 更贴近"独立信息事件数量加权"的语调测度。若本列与等权 full 列的系数高度接近, 说明该银行—年份格点上跟风转载现象不严重, 语调结论对报道原创性不敏感; 若两者出现系统性偏离, 则提示跟风报道对全样本语调有实质性拉动, 应在稳健性讨论中结合媒体集中度指标一并说明。

## VAR: exc_yao_2021_score_hw_ctx

【变体差分】
本列同时叠加两个非参照维度: 文本轨道取 ctx (标题 + 银行实体上下文窗口), 加权取跟风衰减 (_hw, 文章得分乘 herd_weight_ctx 后聚合)。相对 hw_full, 差异在文本口径由全文收窄到银行实体局部; 相对等权的 ctx 列, 差异在加入了对跟风冗余报道的降权。herd_weight_ctx 是在 ctx 超级文档上独立计算的三轨权重之一 (stage 24 对 full/ctx/ss 分别算权重, 不共用), 因此本列的降权判据与 ctx 文本口径严格同轨, 不借用 full 轨权重。聚合仍限于剔除退出媒体后的存活媒体子样本, bank-year 取均值。ctx 轨在 full-only 门控下为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集。本列位于"轨道 × 加权"二维稳健性网格的一个格点, 与 full/ss 轨及等权/价值加权诸列互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J。它回答的问题是"在银行实体局部文本上, 对跟风报道降权后, 退出媒体剔除的语调结论是否稳健"。由于 herd_weight_ctx 的相似度判定同样基于 ctx 超级文档 (而非全文) 计算, 两篇报道即便全文差异很大, 只要各自的银行实体窗口高度雷同 (例如都摘引同一段监管公告原文), 仍会被判为跟风并同步降权, 这与 hw_full 基于全文相似度的判定可能给出不同的降权结果; 使用者不宜假设 hw_full 与 hw_ctx 的降权集合重合, 二者是各自轨道内部独立计算的稳健性对照, 系数差异应结合两轨降权比例分别解读, 不作跨轨直接比较的因果推断。

## VAR: exc_yao_2021_score_hw_ss

【变体差分】
本列叠加最严格的文本轨道 ss 与跟风衰减加权 _hw: 文章级 yao_2021_score_ss 先乘以 herd_weight_ss, 再在存活媒体子样本上按 bank-year 取均值。ss 轨只读取银行与金科同句共现窗口的语调 (句半径默认 ±1), 其回退语义镜像 ctx——无同句共现则 content_ss 回退全文且 ss_is_fallback=True, 金科自动机为 None 时整轨优雅降级。herd_weight_ss 由 stage 24 在 ss 超级文档上独立计算, 与 ss 文本口径严格同轨, 不借用 full 权重。本列是本家族约束最强的一格: 既把语调读取收紧到银行—金科同句关系, 又对疑似跟风的冗余报道降权, 同时剔除疑似退出媒体, 三重收紧叠加意味着在稀疏语料上更易出现回退与零方差退化 (T=2 开发样本上属预期, 生产 T=19 下方充分展开)。ss/ctx/full 三轨与 hw/w/等权三加权各自 just-identified 并排, 互为稳健性、不分主次, 禁混入同一 over-identified Hansen J。本列回答"在银行金科同句语调、跟风降权、退出媒体剔除三重最严口径下, 主结论是否仍然稳健"。正因为本列同时叠加三重收紧条件, 其在小样本上的有效观测数往往显著少于 full 轨或等权列, 标准误相应偏大, 论文中若报告本列结果, 应同时给出有效样本量与置信区间, 而非仅比较点估计; 当该列在生产 T=19 全量语料下依然与参照列 exc_yao_2021_score_full 方向一致, 才能构成"结论不依赖任一单一维度选择"的最强稳健性证据链条, 是本家族九列稳健性梯子中信息量最集中但方差也最大的一格。

## VAR: exc_yao_2021_score_w_full

【变体差分】
本列在参照列 exc_yao_2021_score_full 上增加提及密度价值加权 (_w): 文章级得分先乘以该文的 mention_density (目标银行在该文中的提及密度), 再进入 bank-year 均值, 是暴露度价值加权 (value-weighted exposure) 的实现——让银行被更密集、更核心地提及的报道在语调均值中获得更大权重, 弱化仅一带而过提及银行的报道。与等权 full 列的区别仅在权重维度 (乘 mention_density 而非等权); 与跟风衰减 hw_full 列的区别在权重口径 (价值/暴露度加权而非去冗余降权), 二者度量的是不同意义上的"重要报道"——_w 强调提及强度, _hw 强调原创独立性, 二者互为稳健性、不分主次, 不可相互替代亦不可并入同一 over-identified Hansen J。文本轨道仍取 full (标题 + 全文), 样本仍限于剔除退出媒体后的存活子样本。本列回答"当按银行提及强度对报道加权后, 剔除退出媒体的情感结论是否依然成立", 是价值加权维度上的样本稳健性读数。mention_density 是文章级、track-agnostic 的元数据权重, 由银行实体在全文中的出现次数与文本长度共同决定, 不因文本轨道切换而重新计算, 因此本列与后续 w_ctx / w_ss 列共用同一份权重来源, 差异只体现在被加权的情感得分本身取自哪条轨道。相对未剔除退出媒体的对应价值加权版本, 本列进一步叠加了样本侧的退出媒体剔除, 二者叠加意味着本列同时控制了"报道是否来自持续覆盖媒体"与"银行在该报道中的核心程度"两个维度, 是检验主结论对媒体样本与暴露强度双重选择是否稳健的复合读数。

## VAR: exc_yao_2021_score_w_ctx

【变体差分】
本列叠加 ctx 文本轨道与提及密度价值加权 _w: 文章级 yao_2021_score_ctx 先乘以 mention_density, 再在剔除退出媒体后的存活媒体子样本上按 bank-year 取均值。相对 w_full, 差异在文本口径由全文收窄到银行实体上下文窗口 (标题 + 实体窗); 相对等权 ctx 列, 差异在按银行提及强度对报道加权。价值加权用同一 mention_density 权重跨轨施加 (权重本身是文章级 track-agnostic 元数据), 但被加权的情感得分是 ctx 轨专属, 故本列语义 = "银行实体局部语调 × 提及强度权重"。ctx 轨在 full-only 门控下为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集。本列处于"ctx 轨 × 价值加权"格点, 与 full/ss 轨、等权/跟风加权诸列互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J。它回答"在银行实体局部文本上按提及强度加权后, 退出媒体剔除的语调结论是否稳健"。由于 mention_density 与文本轨道切换正交, 本列相对 w_full 的差异纯粹来自"情感读取范围"这一单一维度的变化, 而非权重口径的变化, 这使得 w_full 与 w_ctx 的对比成为该家族中控制变量最干净的一组轨道敏感性检验; 反之, 本列与 hw_ctx 的差异则同时涉及权重口径与语义 (提及强度 vs 去冗余) 两个维度的变化, 二者不构成单一维度的干净对照, 使用者在设计稳健性表格排布时应注意区分"单维度对照"与"复合维度对照", 避免把系数差异笼统归因于某一个维度。

## VAR: exc_yao_2021_score_w_ss

【变体差分】
本列叠加最严格的 ss 文本轨道与提及密度价值加权 _w: 文章级 yao_2021_score_ss 先乘以 mention_density, 再在剔除退出媒体后的存活媒体子样本上按 bank-year 取均值。ss 轨只读取银行与金科同句共现窗口 (句半径默认 ±1) 的语调, 回退语义镜像 ctx——无同句共现则 content_ss 回退全文且 ss_is_fallback=True, 金科自动机为 None 时整轨优雅降级, 故在稀疏语料上更易大量回退与零方差退化 (T=2 开发样本属预期, 生产 T=19 下充分展开)。价值加权用文章级 mention_density (银行提及强度) 施加, 度量"银行—金科同句关系语调 × 提及强度"。与 hw_ss 的对照在权重意义: _w 放大高提及强度报道, _hw 放大低跟风冗余报道, 二者互为稳健性、不分主次, 不可并入同一 over-identified Hansen J。三轨 (full/ctx/ss) 与三加权 (等权/hw/w) 各自 just-identified 并排, 禁混同一 over-identified Hansen J。本列回答"在银行金科同句语调、提及强度加权、退出媒体剔除三重口径下, 主结论是否仍稳健", 是本家族价值加权维度上约束最强的一格。与 hw_ss 一样, 本列同时叠加三重收紧条件, 有效观测数与自由度在小样本下同样偏紧, 论文引用时宜同步披露回退占比与有效样本量。就本家族九列的整体定位而言, exc_yao_2021_score_w_ss 与 exc_yao_2021_score_hw_ss 构成"轨道最严"这一维度上的一对内部对照, 二者若在生产语料下方向一致, 则说明无论按提及强度还是按原创独立性重新加权, 银行—金科同句关系上的语调结论都不受权重选择驱动, 是九列稳健性梯子收官处最具说服力的交叉验证。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
