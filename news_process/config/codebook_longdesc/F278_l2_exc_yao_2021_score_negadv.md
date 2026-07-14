---
family_id: F278
columns:
- exc_yao_2021_score_negadv_ctx
- exc_yao_2021_score_negadv_full
- exc_yao_2021_score_negadv_ss
unit: 无量纲情感倾向得分 (bank-year 均值, 逐篇自归一化到 [-1, 1] 区间)
formula: "exc_yao_2021_score_negadv{track} = mean_媒体 a 的 _is_ceased_media(a) 取 0 (即非疑似退出媒体) yao_2021_score_negadv{track}(a); 其中 yao_2021_score_negadv = (Σ pos_adj − Σ neg_adj) / Σ|final|, 逐 token 状态机仅启用否定翻转+转折增强两条规则 (省略程度副词六级加权), 落在 Yao (2021) 中文金融情感词典命中词上"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (exc_ 聚合); 上游文章级得分 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores
upstream:
- 22_tone_words.parquet (文章级 yao_2021_score_negadv_{full,ctx,ss})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- attention_media.detect_defacto_cessation (_is_ceased_media 标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1145/1341531.1341561
  type: wp
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: "Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)"
  pages_or_artno: 231-240
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
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
本家族度量的是"在剔除疑似覆盖退出媒体之后, 目标银行金融科技相关报道所呈现的词典法情感倾向", 具体以 Yao (2021) 中文金融情感词典为词表 (该词典与 Ma, Zhang 与 Zhang 2025 在 Expert Systems with Applications 上构建的中文细粒度投资者情感词典 CN-FSD 同属"面向中文金融文本、逐字逐句校验命中词极性"的细粒度词典建设谱系, 是本仓对该类词典构建工作的文献锚点)、以否定加转折两条语言学规则消融组合 (negadv) 打分, 并在银行-年维度取均值。三个成员列 exc_yao_2021_score_negadv_full / _ctx / _ss 对应三条文本轨道, 其余口径 (词典、规则组合、剔除媒体子集) 完全一致。构念可拆成三层修饰叠加在同一底层词典情感之上: 第一层是词典与规则 (Yao 2021 词典 + 否定翻转 + 转折增强, 关掉程度副词加权); 第二层是样本约束 (只保留非停刊媒体发布的文章, 即 exc_ 前缀语义); 第三层是文本轨道 (full/ctx/ss)。三层各自独立, 互不改写彼此语义, 这也是本家族在稳健性梯子中被摆放的方式。

【方法学与计算】
文章级得分由 tone_words.py 的 compute_dict_scores 产出。打分内核是一个逐 token 的状态机: 命中 Yao (2021) 情感词后, 根据其前文窗口内是否出现否定词决定是否翻转极性 (否定翻转规则), 根据是否处于"但是/然而"等转折结构之后决定是否放大权重 (转折增强规则); negadv 变体刻意省略程度副词六级加权那一条规则。三条基础规则 (否定翻转、程度加权、转折增强) 的全 powerset 被物化为 raw/negonly/degonly/advonly/negdeg/negadv/degadv 七个非满配变体, negadv 即"开否定、开转折、关程度"的那一格 (等价于满配 full 减去程度那条规则)。每篇文章内, 得分按 (正向调整词权重之和 − 负向调整词权重之和) 除以全部命中词绝对权重之和自归一化到 [-1, 1], 因此不同变体各自拥有不同的归一化分母。exc_ 聚合在 attention_media.py 的 compute_media_heterogeneity 中完成: 先由 detect_defacto_cessation 用"最后覆盖年份显著早于样本末年"的数据驱动判据 (辅以 NPPA 交叉验证仅改标签、不收窄集合) 标出疑似退出覆盖的媒体集合并写入 _is_ceased_media, 随后仅对 _is_ceased_media==0 的文章按 target_bank×year 分组求 yao_2021_score_negadv 的算术均值。零文章的银行-年在情感类列上按契约保持缺失 (不做零填, 与计数类的 n_articles_exc 零填契约区分)。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否算入银行金科报道宇宙, 只看 full 轨的 LLM 判定, ctx/ss 是在 full 留篇集之上的 conditional-on-full 轨道。

【文献定位】
词典法情感测度的方法学基础与效度边界, 在 van Atteveldt et al. (2021) 对人工标注、众包、词典、机器学习四类方法的系统对比, 以及 Frankel et al. (2022) 对机器学习与词典法在披露情感上的横向比较中有系统交代; 二者共同支撑了"词典法作为可解释、可复现的并排测度而非唯一真值"的定位。中文金融领域的专用词典建设可追溯到 Du et al. (2022) 在 Review of Finance 上构建的中文金融情感词典 (强调语言与领域特异性), 以及 Bian et al. (2021) 的中文金融情感词典工作, 并延续至 Ma, Zhang 与 Zhang (2025) 面向中文散户投资者构建的细粒度情感词典 CN-FSD; Yao (2021) 词典即处于这一谱系之中, 与本仓 jiang_2021 / bian_2021 / du_2022 / you_2018 / loughran 六部词典互为并排测度。规则消融所依据的否定处理与转折 (adversative) 增强, 源自 Ding, Liu 与 Yu (2008) 的整体式意见挖掘框架与 Taboada et al. (2011) 对词典法中否定、程度与转折算子的系统梳理; Barbaglia et al. (2025) 进一步在经济文本上验证了基于词典的情感抽取的稳健性。exc_ 子样本背后的因果动机是媒体覆盖退出削弱地方监督进而放大选择偏误的经典发现, 本实现以"话题覆盖退出"作为停刊的保守代理, 并据此保守地把疑似退出媒体剔出样本作为稳健性对照。

【口径铁律】
规则消融梯度七变体属"各条语言学规则是否驱动主结论"的规格稳健性并排: negadv 与 raw/negonly/degonly/advonly/negdeg/degadv 各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同规则变体混进同一 over-identified Hansen J。相邻级差含否定×程度交互与自归一化分母变更, 属非可加分解 (audit MATH-1), 只可解读为"主结果对该规则是否敏感", 不可解读为某条规则的纯边际贡献。三条文本轨道 full/ctx/ss 同样各自 just-identified 并排、互为稳健性, 亦禁混入同一 over-identified Hansen J; ss 轨的回退语义镜像 ctx (无银行∧金科同句共现时 content_ss 退化为全文正文并置 fallback 标志)。exc_ 子样本与全样本口径之间同为稳健性对照 (保守剔除 vs 全量), 不可在论文中把 exc_ 表述为严格停刊 (publication cessation) 口径, 只能表述为"疑似退出覆盖媒体"的保守剔除口径。

## VAR: exc_yao_2021_score_negadv_ctx

【变体差分】
本列取 ctx (实体窗) 文本轨道: 文章文本被裁剪为"标题 prepend + 目标实体前后窗口"的实体上下文, 再落到 Yao (2021) 词典上按 negadv 规则 (否定翻转 + 转折增强, 关程度加权) 打分, 最后在剔除疑似退出覆盖媒体 (_is_ceased_media==0) 后按银行-年求均值。与同族 _full 列的唯一差异是文本轨道: _ctx 只看实体窗内的词典命中, 因而对"银行金科语境的局部情感"更聚焦, 对全文其它段落的情感稀释更不敏感。在 full-only 留篇门控下 (2026-06-29), 本列属 conditional-on-full 轨道 —— 行宇宙是 full 轨留篇集的子集, per-track 均值照常在该子集上逐轨计算。需要强调三条文本轨道各自 just-identified 并排、互为稳健性、不分主次, 禁止把 _ctx 与 _full/_ss 混进同一 over-identified Hansen J; 同理本列所属的 negadv 规则变体也不得与其它规则消融变体混入同一 over-identified 设定。exc_ 前缀表明其为媒体覆盖退出选择偏误的保守稳健性子样本, 只作与全样本口径的规格对照, 不改变词典与规则语义。实体窗的裁剪边界由上游 stage 14 物化的 content_ctx 决定, 与 stage 21 情感 LLM 三轨消费的是同一份物化文本, 因而本列与 llm_vote_tone_ctx 等 LLM 侧 ctx 测度共享同一份底层实体窗口定义, 只是打分内核换成词典状态机而非大模型判别; 这也是"词典法与 LLM 法互为方法学并排"这一更高层稳健性设计在 ctx 轨道上的具体落点。当上游实体识别未能在窗口内截出任何句子时, ctx 轨退化遵循与 stage 14 一致的兜底口径, 不额外引入本列特有的缺失规则。

## VAR: exc_yao_2021_score_negadv_full

【变体差分】
本列取 full (全文) 文本轨道: 文章文本为"标题 prepend + 全文正文", 是三轨中信息量最完整、也是留篇门控唯一裁决所依据的轨道。词典与规则口径与同族其余两列一致 —— Yao (2021) 中文金融情感词典命中词上启用否定翻转与转折增强两条规则、关闭程度副词六级加权 (即 negadv 变体), 逐篇按正负调整词权重之差除以命中词绝对权重之和自归一化, 再在剔除疑似退出覆盖媒体后按银行-年求均值。与 _ctx / _ss 的唯一差异是文本轨道: _full 读取整篇正文, 对全文层面的情感基调最敏感, 也因此承担了 full-only 门控中"这是否算一篇银行金科报道"的判定角色, 而 _ctx / _ss 是在 _full 留篇集之上的 conditional-on-full 稳健性轨道。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; negadv 与其余六个规则消融变体同为规格稳健性并排, 亦禁混入同一 over-identified 设定, 且因非可加分解 (MATH-1) 不可解读为某规则的纯贡献。exc_ 子样本相对全样本口径同为稳健性对照, 表述须限定为"疑似退出覆盖媒体"的保守剔除, 不得表述为严格停刊口径。由于 _full 是留篇门控的裁决轨道, 本列在样本规模上通常与全样本 (非 exc_ 版本) 的 full 轨最接近, 但仍受 _is_ceased_media 过滤的影响而在文章数上略窄于无 exc_ 前缀的对照列; 使用者若要评估媒体覆盖退出对结论稳健性的边际影响, 应把本列与其对应的非 exc_ 版本并列汇报, 而非替代。

## VAR: exc_yao_2021_score_negadv_ss

【变体差分】
本列取 ss (银行∧金科同句共现窗) 文本轨道: 文本被约束为标题与"目标银行和金融科技词在同一句子内共现"的句子及其 ±N 句窗口, 是三轨中语境最严格的一轨。词典 (Yao 2021)、规则 (negadv = 否定翻转 + 转折增强, 关程度) 与 exc_ 剔除疑似退出媒体后按银行-年求均值的聚合口径, 均与同族 _full / _ctx 完全一致, 唯一差异是文本轨道。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行与金科同句共现时, content_ss 优雅退化为全文正文并置 ss_is_fallback 标志, 与 ctx 共享 n_articles 分母; 若金科 AC 自动机缺席则该轨 fallback 标志全 True 优雅降级。在 full-only 门控下本列同属 conditional-on-full 轨道, 行宇宙为 full 留篇集子集。三条文本轨道各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; negadv 规则变体与其余消融变体亦为并排稳健性、禁混同一 over-identified 设定。exc_ 前缀仅标示媒体覆盖退出选择偏误的保守稳健性子样本, 与全样本口径互为规格对照, 论文中须限定为"疑似退出覆盖媒体"保守剔除口径。ss 轨在三轨中对"银行-金科话题是否真正被同一句话谈及"最敏感, 因而其命中词集合往往最小、逐篇归一化分母也随之更薄, 这意味着本列在个别文章上的方差可能高于 _full / _ctx; 该敏感性是设计使然而非缺陷, 使用者在解读 ss 轨系数标准误时应留意这一薄样本特征, 并优先与 _full / _ctx 一并汇报而非单独依赖 ss 轨下结论。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08) No. 231-240 [Working Paper]. https://doi.org/10.1145/1341531.1341561
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
