---
family_id: F358
columns:
- jiang_2021_score_w_sum_ctx
- jiang_2021_score_w_sum_full
- jiang_2021_score_w_sum_ss
unit: 无量纲加权得分和 (value-weighted 分子, 未归一; bank-year × 轨道)
formula: "jiang_2021_score_w_sum{track} = Σ_{a ∈ bank-year} jiang_2021_score_w{track}(a); 其中逐篇加权分 jiang_2021_score_w{track}(a) = jiang_2021 逐篇未加权词典极性分(a, 出自 stage 22 tone_words) × mention_density(a, 出自 stage 11 news_bank 独立计算列, 与 news_salience 体裁显著性特征组并列非从属) 由 panel runner 步骤 3b 计算; 下游 jiang_2021_tone_vw{track} = jiang_2021_score_w_sum{track} / sum_mention_density"
producer: news_process/pipeline/panel/encode.py (F 段 value-weighted 聚合 agg[f'{d}_score_w_sum{track}'], d='jiang_2021') ; news_process/pipeline/panel/stata_export.py (标签导出)
upstream:
- 22_tone_words.parquet (逐篇未加权 jiang_2021_score_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 11_news_bank.parquet (mention_density 逐篇提及密度权重列, news_bank.py 独立计算, 与同阶段 NEWS_SALIENCE_KEYS 体裁显著性特征组并列而非从属; 供 panel runner 步骤 3b 加权)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: "10.1016/j.frl.2024.105227"
  title: "Sentiment trading with large language models"
  authors: "Kirtac, K., & Germano, G."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  venue: "Expert Systems with Applications"
  type: "journal"
new_dois:
  - "10.1016/j.frl.2024.105227"
  - "10.1016/j.eswa.2024.125739"
---

## CORE

【构念与来源】
本家族三列 jiang_2021_score_w_sum{full,ctx,ss} 是姜富伟、孟令超、唐国豪 (2021,《经济学(季刊)》) 媒体文本情绪词典在银行-年层面的「提及密度加权得分和」, 即 value-weighted (VW) 情感聚合的未归一分子。姜富伟等 (2021) 原文以媒体文本情绪预测股票回报为出发点构建了针对中文财经语料的情绪词典, 本仓将其移植到银行-金融科技共现报道语料上, 用以在词典轨内部提供一支独立于 Bian (2021)/Du (2022)/Yao (2021)/You (2018)/Loughran-McDonald 中译本 (loughran) 的中文情感测度, 六部词典彼此互为稳健性、不分主次。所谓构念, 是要回答一个比「一年内平均语调多正」更细的问题: 当把每篇报道按其对目标银行的着墨强度赋权后, 该银行当年全部涉金融科技报道的 Jiang 词典净极性分累加起来是多少。它刻意不做除法归一, 而作为 value-weighted 语调 jiang_2021_tone_vw{track} 的分子存档在面板中, 与分母 sum_mention_density 并置。之所以要保留未归一的加权和作为独立列, 是因为它同时承载了「方向」(净极性符号) 与「体量」(被加权的报道规模), 在稳健性核对、加权口径复算与零新闻年份的退化判定上比归一后的比值更透明: 当某银行当年无任何留篇报道时, 该和是空集求和, 按 Σ over ∅ = 0 的契约落 0 而非缺失, 从而与 sum_mention_density 等兄弟权重和保持同一「和」语义、避免 .dta 中零新闻行残留为点号。

【方法学与计算】
计算须辨明三个阶段的分工, 不可把加权乘法误挂在情感词典阶段。第一步在情感词典阶段 (stage 22 tone_words) 完成: 对每篇报道先按姜富伟等 (2021) 词典匹配正负情感词, 并叠加本仓统一的三条语言学规则 (否定翻转/程度副词/转折) 得到逐篇净极性分 jiang_2021_score{track}; 须强调 22_tone_words.parquet 落盘的只是这一未加权逐篇极性分, 其中并不含任何提及密度权重, 也不存在名为 jiang_2021_score_w 的逐篇落盘列。第二步的加权乘法实际发生在面板装配阶段, 由 panel runner 步骤 3b 执行: runner 把 stage 22 的未加权极性分 jiang_2021_score{track} 与来自 stage 11 news_bank.py 独立计算 (与体裁显著性特征组 news_salience 并列而非从属) 的逐篇提及密度权重 mention_density 逐行相乘, 现算出加权逐篇分 jiang_2021_score_w{track}, 此列是运行期的中间量而非 stage 22 的落盘列。提及密度权重来自 news_salience, 度量目标银行在该篇文本中被提及的相对强度, 使着墨越重的报道对全年聚合贡献越大, 这与 Hassan et al. (2019, QJE) 以文档相关度/提及强度对逐篇信号赋权的做法一脉相承。第三步在面板聚合阶段 (encode.py 的 value-weighted F 段) 完成: 对同一银行-年-轨道内所有留篇报道由步骤 3b 现算的 jiang_2021_score_w{track} 直接求和, 即得 jiang_2021_score_w_sum{track}。故完整链路是「stage 22 出未加权分 → stage 11 news_salience 出 mention_density → panel runner 步骤 3b 做加权乘法 → encode.py F 段做银行-年求和」四环, 加权环节位于面板 runner 而非词典阶段, 这一归属直接影响复算加权口径时应去哪个阶段核对源列。随后同段以 sum_mention_density 为分母作除法, 派生出归一化的 jiang_2021_tone_vw{track}, 故本家族三列在数学上是该 VW 语调的分子。单位为无量纲加权得分和: 词典极性分本身无量纲, 乘以同样无量纲的提及密度权重后求和, 结果不落在固定区间, 其量纲随报道条数与提及强度伸缩, 因而只可在同口径下横向比较、不可与归一化语调直接比水平。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入银行-年宇宙由 full 轨的 LLM 判定决定, ctx 与 ss 轨为条件于 full 留篇集的子集测度, 三轨各自逐轨算列。本家族与词典轨内其他加权口径 (等权 tone_sum、媒体权威加权 score_mw_sum、跟风衰减加权 score_hw_sum) 并排存在, 均以同一逐篇未加权分 jiang_2021_score{track} 为起点, 只是权重来源不同 (提及密度 vs 媒体权威 vs 跟风衰减), 各口径互为稳健性、不分主次, 各自 just-identified, 禁混进同一 over-identified Hansen J。

【文献定位】
词典来源姜富伟、孟令超、唐国豪 (2021) 以媒体文本情绪预测股票回报为切入点, 构建并验证了面向中文财经语料的情绪词典, 是本家族极性分的唯一词典依据 (DOI: 10.13821/j.cnki.ceq.2021.04.10)。将词典法置于更广的效度谱系中, van Atteveldt et al. (2021) 系统比较人工标注、众包、词典法与机器学习, 指出词典法在特定语域下的偏差与适用边界, 为本项目把词典轨与 LLM 轨、BERT 轨并置为互为稳健性证据提供了方法学理由; Frankel, Jennings & Lee (2022) 在 Management Science 上以披露文本对比机器学习与词典法情感, 是本仓「三方法互为稳健、不分主次」设计的直接先例。就中文金融语域的词典专用性, Du, Huang, Wermers & Wu (2022) 在顶刊 Review of Finance 论证语言与领域专用性对中文金融情感测度的必要性 (语言/领域越贴近目标语料, 词典越能捕捉细微极性), 与姜富伟等词典同属为中文财经文本定制情感资源的谱系, 也是本仓政治词权重敏感性设计的既有依据源。就机器可读文本情绪与资本市场关系这一更宏观脉络, Cao, Jiang, Yang & Zhang (2023) 发表于顶刊 The Review of Financial Studies 的研究考察企业在 AI 阅读者存在时如何调整信息披露语调, 与本家族「文本情绪 → 银行-年面板测度」的构念方向一致, 佐证情绪型文本特征在中国及跨市场语境下具有稳定的实证相关性, 是本家族 value-weighted 聚合口径的顶刊文献锚点。需强调铁律: 本 VW 加权和只是词典轨内部的一种加权口径 (相对于等权 tone 与媒体权威加权 mw、跟风衰减加权 hw), 各加权口径互为稳健性、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 同理三轨 full/ctx/ss 亦各自 just-identified 并排、禁混同一 Hansen J, 词典轨与 LLM/BERT 轨之间同样只作互为稳健性对照而不合并识别。Kirtac and Germano (2024, Finance Research Letters) 提出并检验基于大语言模型的金融文本情绪交易信号,证明其相对传统词典法在预测股票收益上的增量效力,呼应本家族词典法情感测度作为多方法互为稳健性对照之一的定位。Ma, Zhang and Zhang (2025, Expert Systems with Applications) 面向中国境内投资者构建细粒度中文情感词典并验证其在预测市场波动与异常现象上的效力,与姜富伟等(2021)同属为中文财经语料定制情感词典资源的谱系。

## VAR: jiang_2021_score_w_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨的 Jiang 词典提及密度加权得分和。相对于家族的 full 轨 canonical, 唯一差分在于底层文本域: ctx 轨的逐篇文本 content_ctx 由 stage 14 ctx_materializer 物化, 取标题 (prepend_title 前置) 加上以银行/金融科技实体为中心的上下文窗口, 而非全文正文。因此本列的逐篇加权分 jiang_2021_score_w_ctx 只在实体邻近窗口内统计 Jiang 词典命中, 再乘以提及密度权重并在银行-年内求和。语义上它衡量「把注意力收窄到实体上下文后, 该银行当年报道的 value-weighted 词典净极性体量」, 与 full 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。留篇宇宙受 full-only 门控约束: 行集是 full 轨留篇集的子集, ctx 逐轨自算分子与分母。当某银行-年无实体窗文本或该轨源列缺失时, 逐项守卫使聚合优雅跳过、按空集求和落 0, 不借用 full 轨分母也不产生单边孤儿列。与归一化的 jiang_2021_tone_vw_ctx 相比, 本列保留未除分母的加权和, 便于在实体窗口口径下复算权重与核对体量方向。需要区分的是, ctx 轨与 full 轨的差别不在词典、不在提及密度权重、也不在滞后阶数, 而仅在参与词典命中统计的文本跨度: full 覆盖整篇正文, ctx 只覆盖实体邻近窗口。这一收窄使得当报道大量篇幅与目标银行无关时, ctx 轨能滤掉窗口外噪声, 从而与 full 轨形成规格稳健性对照; 但收窄也可能因窗口过小而丢失有效极性信号, 故二者只作互为稳健性并排, 不以相关性高低择一为主、不合并进同一识别式。在早期试跑 T=2 的极小样本上, 实体窗轨可能因命中稀疏而呈现较大波动, 属预期退化, 生产期 T=19 语料下方回归正常。

## VAR: jiang_2021_score_w_sum_full

【变体差分】
本列是 full (全文) 轨, 为家族的 canonical 加权和列。其底层文本域 content_full = 标题 prepend 后拼接全文正文, 是留篇门控 (2026-06-29 full-only) 的判定轨: 一篇报道是否计入银行-年宇宙, 由 full 轨的 LLM 判定决定, 因而 full 轨的留篇集是 ctx/ss 两轨的母集。逐篇加权分 jiang_2021_score_w_full = Jiang 词典逐篇全文极性分 × mention_density, 在银行-年内求和即得本列; 随后除以 sum_mention_density 得 jiang_2021_tone_vw_full。作为 canonical, 它给出「以提及密度加权、覆盖整篇正文」的词典净极性体量, 是 value-weighted 词典轨的主口径分子。相对于同族 ctx/ss, 差分仅在文本域覆盖范围 (整篇正文 vs 实体窗 vs 同句窗), 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。相对于同轨其他加权口径 (等权 tone、媒体权威加权 mw、跟风衰减加权 hw), 本列专属 value-weighting (提及密度) 口径, 各口径同样互为稳健性并排、禁混同一 Hansen J。零新闻银行-年按 Σ over ∅ = 0 落 0, 与权重和兄弟列同契约。之所以称本列为 canonical 而非另两轨, 原因不在测度地位高低, 而在门控职责: full 轨承担留篇判定, 决定了整个银行-年样本框, ctx/ss 只能在其子集上取值, 故 full 的加权和天然是最完整的分子。使用时须注意本列是未归一分子, 其数值随当年报道条数与提及强度同向伸缩, 不可直接与其他银行-年的归一化语调比水平, 只能在同口径下比方向与相对体量; 若研究关心可跨样本比较的语调, 应改用下游 jiang_2021_tone_vw_full。本列与逐篇 LLM 判定的 full-only 门控保持一致, 二者同步, 确保分子求和所遍历的报道集恰为被判为「一篇银行金融科技报道」的 full 留篇集。

## VAR: jiang_2021_score_w_sum_ss

【变体差分】
本列是 ss (同句) 轨的 Jiang 词典提及密度加权得分和, 三轨中文本域最窄。ss 轨逐篇文本 content_ss 取标题 prepend 后, 保留银行与金融科技词在同一句子及其 ±N 句窗内共现的片段 (窗半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。因此本列的逐篇加权分 jiang_2021_score_w_ss 只统计银行∧金科严格同句共现语境内的 Jiang 词典命中, 乘以提及密度权重后在银行-年内求和。回退语义镜像 ctx: 当某篇无银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True, 与 ctx 共享 n_articles 分母口径; 若上游金融科技 AC 词典为空则 ss_is_fallback 全 True 优雅降级。语义上本列衡量「把注意力收窄到银行与金科同句共现语境后, value-weighted 的词典净极性体量」。它与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 留篇宇宙同为 full-only 门控下 full 留篇集的子集, ss 逐轨自算, 缺源列或空集时按 Σ over ∅ = 0 落 0, 不借邻轨分母。与 ctx 轨的差别在于共现判据的严格程度: ctx 只要求实体落入邻近窗口, ss 要求银行与金融科技词严格同句 (或同句 ±N 窗) 共现, 因而 ss 是三轨中信号最聚焦、也最易触发回退的一轨。这一严格判据使 ss 轨在「银行确实被放在金融科技语境下讨论」这一前提下才计入词典命中, 从而与 full/ctx 构成由宽到窄的规格阶梯, 三轨互为稳健性、不分主次。需强调回退不是缺失: 回退篇仍以全文 body 参与, 只是 ss_is_fallback 标记其非真同句共现, 供下游按需剔除。在早期试跑 T=2 上 ss 轨常因同句共现稀疏而大面积回退甚至零方差, 属预期退化, 生产期 T=19 语料下恢复正常, 不影响本列作为 value-weighted 分子的口径定义。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters. https://doi.org/10.1016/j.frl.2024.105227
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
<!-- rendered-citations:end -->
