---
family_id: F280
novelty_exempt_rationale: "exc_ 前缀为停刊媒体稳健性排除聚合、negonly 为词典规则消融变体, 是 yao_2021 词典族的双重技术变体, 测度定义依据母族词典与消融/排除机制本身, 非独立新构念, 无需追加新文献。"
columns:
- exc_yao_2021_score_negonly_ctx
- exc_yao_2021_score_negonly_full
- exc_yao_2021_score_negonly_ss
unit: 情感倾向分值 (无量纲, 自归一化于闭区间 [-1, 1]; bank-year 文章均值)
formula: "exc_yao_2021_score_negonly_{track} = mean_{article ∈ 存活媒体} yao_2021_score_negonly_{track}; 文章级 yao_2021_score_negonly = Σ final_score / Σ|final_score|, 其中 final_score 在 yao_2021 词典上以 apply_negation=True、apply_degree=False、apply_adversative=False 的仅否定规则计得; 存活媒体 = 非 (confirmed ∪ suspected) 疑似退出覆盖媒体"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (exc_ 停刊稳健性聚合; 先经 detect_defacto_cessation 剔除疑似退出覆盖媒体, 再对 df_alive 按 target_bank/year 分组对 yao_2021_score_negonly_{track} 等符合 _SCORE_PATTERNS 前缀的列取均值动态生成; 文章级分数由 news_process/pipeline/sentiment/tone_words.py::_compute_sentiment_with_rules 经 _RULE_ABLATION_VARIANTS 物化)
upstream:
- 22_tone_words.parquet (yao_2021_score_negonly_full / _ctx / _ss 文章级词典分数)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 21_tone_llms.parquet (llm_verified_full 留篇门控 + 媒体来源字段供停刊检测)
citations:
- doi: 10.1111/jofi.13498
  type: journal
  authors: Derrien, F., Krüger, P., Landier, A., & Yao, T.
  year: 2025
  title: "ESG news, future cash flows, and firm value"
  venue: Journal of Finance
  vol: 80
  issue: 6
  pages_or_artno: 3499-3554
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
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
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: 10.1145/1341531.1341561
  type: journal
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: Proceedings of the International Conference on Web Search and Web Data Mining
  pages_or_artno: 231-240
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"剔除疑似退出覆盖媒体后, 用 Yao 加权等 (2021) 金融领域中文情绪词典、且只启用否定翻转一条语言学规则计得的银行-年度文本语调均值"。列名 exc_yao_2021_score_negonly_{track} 由三个正交部件拼接: 前缀 exc_ 是停刊稳健性口径 (仅纳入未被判为覆盖退出的存活媒体报道); 词典部件 yao_2021 指六部中文金融情绪词典之一的姚加权等 (2021) 词典; 规则部件 negonly 指仅否定翻转、关闭程度副词加权与转折增强的消融变体。构念的实质是一条稳健性并排轨, 而非主结果测度: 它把"主结果是否被幸存媒体样本偏误驱动"与"主结果是否被程度/转折规则驱动"两个稳健性维度叠合在同一列上, 用于回答审稿人对样本选择与词典规则敏感性的双重质疑。

数据来源链条自上游三轨文本发起。stage 14 (ctx_materializer) 先物化 content_full (标题 prepend 全文正文)、content_ctx (标题加银行实体窗口) 与 content_ss (标题加银行与金融科技同句共现窗) 三条真实文本列及其 *_is_fallback 标记; stage 22 (tone_words) 在这三条文本上按 jieba 分词后逐篇跑词典法, 经规则消融梯度谱 _RULE_ABLATION_VARIANTS 物化出 yao_2021_score_negonly_{track} 文章级分数; stage 21 (tone_llms) 提供 llm_verified_full 留篇门控与媒体来源字段。最终在 panel 导出阶段 (attention_media.compute_media_heterogeneity) 先经 detect_defacto_cessation 识别疑似退出媒体集合 (confirmed ∪ suspected), 再对存活媒体子集按 (target_bank, year) 取文章均值, 落地为本家族三列。

【方法学与计算】
文章级仅否定分数在状态机 _compute_sentiment_with_rules 中生成。引擎遍历分词序列, 维护否定窗口、程度倍率与转折激活三个状态; negonly 变体的开关组合为 (apply_negation=True, apply_degree=False, apply_adversative=False)。关键工程铁律是: 关闭程度与转折的数值效应时, 引擎仍保留对程度副词、转折连词、句末标点的识别与 continue 骨架 (只把倍率锁为 1.0、把转折增强锁为不放大), 从而保证否定窗口的到达距离、从句边界的重置时机在仅否定与全规则两种打分变体之间共享同一 scoping。若改为整段删除程度/转折检测, 程度词会落入末尾分支触发否定窗口递减, 副作用缩短否定有效距离, 污染"纯否定"语义 —— 该实现已刻意规避此陷阱。归一化采用自归一化口径: 文章分数等于加权分数之和除以加权幅度之和, 恒落在闭区间正负一之间, 与 LLM 三家投票、BERT 三模型的有界语调轨可比。银行-年度聚合是存活媒体子集内的简单文章均值; 零文章或全为疑似退出媒体的单元按情感类契约保持缺失 (不与计数类的零填连坐)。

疑似退出媒体的识别遵循保守代理口径。detect_defacto_cessation 以媒体在银行-金融科技话题上的覆盖跨度 (首末出现年份) 为依据, 把末次覆盖显著早于样本末年且累计报道达阈值的媒体标记为疑似覆盖退出, 并与国家新闻出版署注销/停办/休刊名单交叉验证; 但交叉验证仅改报告标签, 未经证实的 suspected 仍全量进入排除集。因此下游 exc_ 列须解读为"疑似退出覆盖媒体保守剔除"稳健性口径, 不可在论文中表述为严格停刊 (publication cessation) 口径。这一保守剔除的因果动机是媒体来源消失引入的幸存者偏差会使情感指标向存活媒体倾斜, 并污染以媒体来源分布为暴露权重的 Bartik 类工具变量。

【文献定位】
本家族坐落在三支文献交汇处。其一是中文金融情绪词典的构建与效度支流: Yao 加权等 (2021) 词典与 Du et al. (2022, Review of Finance) 提出的领域特定中文金融情绪词典、Ma et al. (2025) 面向国内投资者的细粒度中文情绪词典同属"通用英文词典迁移到中文金融语境会失真、须领域重建"这一共识, 本家族选用姚词典正是六词典互为稳健性设计的一员。其二是词典法的规则化与效度评估支流: Taboada et al. (2011) 系统论证词典法中否定、程度、转折等语义修饰规则的价值, Ding et al. (2008) 把转折效应限定在从句级作用域 (本引擎句末重置状态的直接方法学来源), Pröllochs et al. (2016) 专门研究新闻驱动交易中否定范围检测对情感极性的影响 —— negonly 变体正是把这三条规则中仅保留否定、剥离程度与转折, 检验主结果对规则集的敏感性。Barbaglia et al. (2025) 与 Frankel et al. (2022, Management Science) 进一步在经济文本与信息披露语境下比较词典法与机器学习法, van Atteveldt et al. (2021) 则以人工标注为金标准量化词典法的效度边界, 共同支撑"词典法须并排多规则变体、并与其它方法互证"的稳健性叙事。其三是媒体停刊与样本选择支流: 媒体来源退出覆盖会系统性改变以媒体情感为核心变量的面板估计, Derrien et al. (2025, Journal of Finance) 关于新闻情感与企业价值的研究亦提示新闻语调测度须审慎处理来源构成, exc_ 口径即对这一选择偏误的保守稳健性应答。

三轨 (full/ctx/ss)、规则消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv 等)、六词典与 exc_ 停刊口径彼此正交并排: 它们各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨、不同规则变体、不同词典或存活/全样本口径混进同一 over-identified 的 Hansen J 过度识别检验。留篇门控统一为 full-only 口径 (2026-06-29): 一篇报道是否被判为银行-金融科技报道只看 llm_verified_full 是否为真, ctx 与 ss 轨的行宇宙是 full 留篇集的子集, 属 conditional-on-full 的测度轨与稳健性轨。

## VAR: exc_yao_2021_score_negonly_ctx

【变体差分】
本列是三轨中的 ctx (实体上下文窗) 轨。它与家族其余两列共享完全相同的词典 (yao_2021)、相同的仅否定规则组合 (apply_negation=True、apply_degree=False、apply_adversative=False) 与相同的 exc_ 存活媒体保守剔除口径, 唯一差分维度是底层文本轨: 本列的文章级分数在 content_ctx 上计得。content_ctx 由 stage 14 物化为"标题 prepend 加银行实体上下文窗口"文本 —— 相对 full 轨的全文正文, ctx 轨只保留围绕目标银行实体的邻近窗口, 从而把语调测度聚焦于与该行直接相关的语境, 削弱同篇报道中其它主体段落的语调串味。

在 full-only 留篇门控下, 本列属 conditional-on-full 测度轨: 行宇宙是 llm_verified_full 为真的留篇集子集, per-track 分数照常在该子集内逐轨计算并按存活媒体子集取银行-年度均值。当某篇报道缺乏可定位的银行实体窗口时, content_ctx 触发 fallback 回退到全文正文, 对应 ctx_is_fallback 标记为真; 本列的聚合分母与 full 轨共享 n_articles 口径但按各自轨文本取值, 缺列或空轨单元按情感类契约保持缺失。三轨互为稳健性、不分主次、各自 just-identified 并排, 严禁把本 ctx 列与 full/ss 列混进同一 over-identified Hansen J。本列的解读定位是"聚焦银行实体语境、仅否定规则、剔除疑似退出媒体"三重稳健性叠合下的姚词典语调, 用以检验主结果既不被全文无关段落的语调污染驱动、也不被程度/转折规则或幸存媒体样本驱动。

## VAR: exc_yao_2021_score_negonly_full

【变体差分】
本列是三轨中的 full (全文) 轨, 也是三列里最接近家族语义主参照的一条。它与 ctx、ss 两列共享同一姚词典、同一仅否定规则组合与同一 exc_ 存活媒体保守剔除口径, 差分维度仍是底层文本轨: 本列的文章级分数在 content_full 上计得, 即"标题 prepend 加全文正文"的完整文本 (原始内容列不动, 标题以 prepend 方式并入而非独立成轨)。相对 ctx 的实体窗口与 ss 的同句共现窗, full 轨保留全部正文, 语调测度覆盖整篇报道, 信息量最充分但也最易受与目标银行弱相关段落的语调影响。

在 full-only 留篇门控下, full 轨承担留篇判定的唯一裁决角色: 一篇报道是否计入银行-金融科技报道宇宙只看 llm_verified_full 是否为真, ctx/ss 轨的行宇宙均是本 full 留篇集的子集。因此本列的存活媒体银行-年度均值直接建立在留篇集之上, 分母 n_articles 口径以 full 轨为准。本列同时叠合三重稳健性维度: exc_ 剔除疑似退出覆盖媒体以防幸存者偏差, negonly 只启用否定翻转以检验主结果对程度副词加权与转折增强规则的敏感性, yao_2021 为六词典互证的一员。full/ctx/ss 三轨、七级规则消融变体与六词典各自 just-identified 并排、互为稳健性、不分主次, 严禁把本列与任何其它轨、规则变体或词典口径混进同一 over-identified 的 Hansen J 过度识别检验。

## VAR: exc_yao_2021_score_negonly_ss

【变体差分】
本列是三轨中的 ss (银行与金融科技同句共现窗) 轨, 语境窗口最窄。它与 full、ctx 两列共享同一姚词典、同一仅否定规则组合与同一 exc_ 存活媒体保守剔除口径, 差分维度是底层文本轨: 本列的文章级分数在 content_ss 上计得。content_ss 由 stage 14 物化为"标题 prepend 加银行与金融科技同句共现窗 (以 ss_sentence_radius 为半径, 默认正负一句)"文本, 只保留目标银行与金融科技词在同一句附近共现的语境, 是三轨里对"银行-金融科技交汇语调"聚焦度最高、噪声最低的一条。

ss 轨的回退语义严格镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文 body, ss_is_fallback 标记为真, 并与 ctx 轨共享 n_articles 分母口径; 当金融科技 AC 自动机为空时 *_is_fallback 全部置真, 优雅降级。在 full-only 留篇门控下, ss 与 ctx 同为 conditional-on-full 测度/稳健性轨, 行宇宙是 llm_verified_full 留篇集的子集, per-track 分数在该子集内逐轨计算后按存活媒体子集取银行-年度均值; 空轨或零文章单元按情感类契约保持缺失, 不与计数类零填连坐。本列的解读定位是"最窄的银行-金科同句语境、仅否定规则、剔除疑似退出媒体"三重稳健性叠合下的姚词典语调。三轨互为稳健性、不分主次、各自 just-identified 并排, 严禁把本 ss 列与 full/ctx 列或其它规则变体、词典口径混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Derrien, F., Krüger, P., Landier, A., & Yao, T. (2025). ESG news, future cash flows, and firm value. Journal of Finance, 80(6), 3499-3554. https://doi.org/10.1111/jofi.13498
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining, 231-240. https://doi.org/10.1145/1341531.1341561
<!-- rendered-citations:end -->
