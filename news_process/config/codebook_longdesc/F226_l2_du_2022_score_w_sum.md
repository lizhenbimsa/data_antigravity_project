---
family_id: F226
columns:
- du_2022_score_w_sum_ctx
- du_2022_score_w_sum_full
- du_2022_score_w_sum_ss
unit: 无量纲加权情感得分之和 (银行-年聚合, value-weighted, 无归一化)
formula: "du_2022_score_w_sum{track} = Σ_{a ∈ 银行-年} ( du_2022_score_a{track} × mention_density_a ); du_2022_score = pos_weighted − neg, pos_weighted = pos_ordinary + 0.5 × pos_political"
producer: news_process/pipeline/sentiment/tone_words.py (文章级 du_2022_score) → news_process/pipeline/panel/runner.py (mention_density 提及密度加权) → news_process/pipeline/panel/encode.py (银行-年求和)
upstream:
- 22_tone_words.parquet (文章级 du_2022_score{track})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (mention_density 加权与银行-年聚合)
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
- doi: 10.1016/j.jcorpfin.2025.102813
  type: journal
  authors: Campbell, J. L., Zheng, X., & Zhou, D.
  year: 2025
  title: "Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?"
  venue: Journal of Corporate Finance
  vol: 94
  pages_or_artno: 102813
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: 113917
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.18653/v1/d16-1057
  type: wp
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: 10.1017/CBO9780511809071
  type: book
  authors: Manning, C. D., Raghavan, P., & Schütze, H.
  year: 2008
  title: "Introduction to information retrieval"
  venue: Cambridge University Press
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是以「提及密度」为价值权重、在银行-年层面加总的 Du et al. (2022) 词典情感原始得分之和 (value-weighted score sum, 简写 w_sum)。其构念定位在情感测度体系里介于「文章级原始极性」与「银行-年归一化语调」之间: 它不是最终喂入回归的归一化语调, 而是构造价值加权语调 (VW tone) 时的分子——即一个银行在某一年被媒体提及的所有报道, 各自的 Du 词典有向情感分被其在该报道内的提及强度加权后累加所得的总量。分母侧的对偶量 (加权提及总量) 另列, 二者相除得到价值加权语调; 单独保留分子 w_sum 是为让研究者能在稳健性检验中自由重组分子分母、或以其作为「情感冲击的绝对体量」而非「相对倾向」进入模型。

Du 词典来源于 Du, Huang, Wermers 与 Wu (2022) 发表于 Review of Finance 的中文金融情感词典构建工作, 该文强调金融文本情感的语言特异性与领域特异性, 指出通用词典直接套用于中文金融语料会系统性失真, 并构造了含普通正面词与政治正面词两类正向词的扩充词表。在本流水线中, du_2022 部署为正面词 2,235、负面词 2,986、政治正面词 1,434 的规模。政治正面词以 0.5 的降低权重计入正侧: 依据 Du et al. (2022) 关于政治正面词信号弱于普通正面词的发现, 对该类词赋予折减权重; 0.5 为研究者选择, 并配套敏感性检验, 令政治词权重取 {0.0, 0.5, 1.0} 三值互为稳健性、不分主次、各自 just-identified 并排, 证明主结论不被这一取值驱动, 三权重禁混进同一 over-identified Hansen J。本 w_sum 家族固定采用生产口径的 0.5 政治权重下的 du_2022_score 作为被加权对象; 政治词权重梯子由另一列族承载, 与本家族正交不交叉。

【方法学与计算】
计算链路分三段。第一段 (stage 22, tone_words.py): 对每篇报道在给定文本轨上跑 du_2022 词典打分, 得到文章级有向原始分 du_2022_score{track} = pos_weighted − neg, 其中 pos_weighted = 普通正面词计数 + 0.5 × 政治正面词计数, neg = 负面词计数; 该原始分在语言学规则 (否定翻转、程度副词、转折) 全开下计算, 是有向的净极性体量而非归一化比率。跨类重叠词按用户 2026-06-24「保留并两侧计数」决策处理, 不武断选边。第二段 (runner.py 步骤 3b): 以文章级 mention_density (目标银行在该报道内的提及密度, value-weighted exposure 权重) 作为权重 w, 逐轨构造 du_2022_score_w{track} = du_2022_score{track} × w; 提及密度加权的思想承袭金融文本计量中以银行在文本内的注意力份额度量其暴露程度的传统, 使一篇高度聚焦目标银行的深度报道比一篇顺带提及的报道贡献更大的情感体量。第三段 (encode.py): 在银行-年分组上对 du_2022_score_w{track} 求和, 得 du_2022_score_w_sum{track}。因此本量是「提及密度加权后有向情感分」在银行-年内的算术和, 量纲为无量纲得分, 无归一化, 可正可负, 其绝对量随该银行-年报道条数与提及强度共同放大。

三条文本轨严格并排: full=标题 prepend 后的全文正文; ctx=标题+实体窗口文本; ss=标题+银行与金科同句±N 窗文本。三轨各自独立打分、独立加权、独立求和, 互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一 over-identified Hansen J。ss 轨回退语义镜像 ctx: 无银行与金科同句共现时 content_ss 回退为全文 body, 相应 is_fallback 置真。留篇门控采 full-only 口径 (2026-06-29): 是否判为一篇银行金科报道只看 full 轨的 llm_verified_full, ctx/ss 降为 conditional-on-full 的测度轨, 其行宇宙为 full 留篇集的子集, 但 per-track 的 w_sum 仍逐轨照算。

【文献定位】
词典法情感测度的方法学正当性建立在领域特异词典优于通用词典这一实证共识上。Du et al. (2022) 在 Review of Finance 上系统论证了中文金融情感的领域与语言双重特异性, 是本词典的直接来源, 也是政治词折减权重的依据。Ma, Zhang 与 Zhang (2025) 进一步为中国境内投资者构造细粒度中文情感词典, 说明面向具体人群与语境定制词表能提升下游预测力, 佐证了本流水线并置多部中文金融词典 (jiang/yao/bian/du/you/loughran) 互为稳健的设计。Hamilton et al. (2016) 提出从无标注语料诱导领域特定情感词表的方法, 为词典扩充的可复现性提供方法学参照。Sun, Yuan 与 Xu (2025) 将词典知识与中性特征注入预训练语言模型, 反向印证词典信号在深度模型时代仍具增量价值。在应用层面, Xu et al. (2024) 证明媒体语调对资本市场具有信息含量, Campbell, Zheng 与 Zhou (2025) 则从定量披露比例角度讨论文本信息风险, 二者共同支撑「以银行-年加权情感体量刻画信息环境」的经济学意图。提及密度作为价值权重的思路与信息检索中以词频-逆文档频率衡量相关性的加权传统相通, 见 Manning, Raghavan 与 Schütze (2008)。

## VAR: du_2022_score_w_sum_ctx

【变体差分】
本列是 w_sum 家族的实体窗轨 (ctx) 变体。其与家族另两轨的唯一差分在文本轨道: ctx 轨的被打分文本为 content_ctx, 即标题 prepend 后拼接目标银行实体上下文窗口的文本, 而非全文正文 (full) 或银行金科同句窗 (ss)。据此, 文章级 du_2022_score_ctx 只在实体窗口内扫描 du_2022 正面/负面/政治正面词, 再乘以同一 mention_density 权重, 在银行-年内求和得本列。相对 full 轨, ctx 轨聚焦于目标银行周边的语境, 剔除与银行无关的段落噪声, 使加权情感体量更贴近「关于该银行的」情感而非「该报道整体的」情感; 相对 ss 轨, ctx 窗更宽, 不要求银行与金科词严格同句共现, 因而保留更多语境。在 full-only 留篇门控下, ctx 为 conditional-on-full 的测度轨, 其非空行是 full 留篇集的子集。本列与 full、ss 两轨互为稳健性、不分主次、各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J; 政治词权重固定为生产口径 0.5, 权重梯子由另一列族承载, 与本轨正交。作为分子量, 本列本身不做归一化, 其绝对体量随该银行-年 ctx 轨报道条数与提及强度共同放大, 因此在跨银行比较时通常需与对偶的加权提及总量相除转为价值加权语调, 或在模型中显式控制报道规模; 单独保留本分子列的意义在于让研究者能自由重组分子分母、或以其直接刻画「实体语境情感冲击的绝对体量」。使用时须注意 ctx 轨在实体窗裁剪下的词频较全文轨稀疏, 加权求和的方差结构与 full 轨不同, 跨轨系数比较前宜先标准化。

## VAR: du_2022_score_w_sum_full

【变体差分】
本列是 w_sum 家族的全文轨 (full) 变体, 也是三轨中语料覆盖最全、通常作为首要报告轨的一支。其差分在于被打分文本为 content_full, 即标题 prepend 后的完整报道正文; 文章级 du_2022_score_full 在整篇文本范围内计 du_2022 正面词、负面词与 0.5 权重政治正面词, 得有向原始分, 再乘 mention_density 权重, 于银行-年内求和得本列。相对 ctx/ss 两轨, full 轨不做实体窗或同句窗裁剪, 因此捕获报道全文的情感体量, 信息最全但也可能纳入与目标银行关联较弱的段落情感。留篇门控 (2026-06-29) 正是以 full 轨的 llm_verified_full 判定一篇报道是否计入银行金科报道宇宙, 故 full 轨的行宇宙即门控主集, ctx/ss 为其子集。本列与 ctx、ss 两轨互为稳健性、不分主次、各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J。政治词权重锚定 0.5 生产口径, {0.0,0.5,1.0} 三权重敏感性由 polw 列族独立承载, 与本轨正交不交叉; mention_density 价值加权与非加权 (raw) 聚合亦互为稳健性并排, 不得混入同一过度识别检验。本列作为分子量不做归一化, 其绝对体量与全文轨的报道条数、正文长度、提及强度同向放大, 因而在横截面比较中通常须除以对偶的加权提及总量得价值加权语调, 或在回归中控制报道规模以避免体量混入倾向; 保留裸分子的价值在于让研究者可在稳健性检验中自由拆解分子分母、或以其表征银行-年全文情感冲击的绝对规模, 与归一化语调形成体量维度与倾向维度的互补。

## VAR: du_2022_score_w_sum_ss

【变体差分】
本列是 w_sum 家族的同句轨 (ss) 变体, 三轨中语料裁剪最严的一支。其差分在于被打分文本为 content_ss, 即标题 prepend 后仅保留目标银行与金融科技词在同一句子±N 窗 (由 config filtering ss_sentence_radius 控制, 默认 1) 内共现的文本片段。文章级 du_2022_score_ss 只在这些银行与金科强共现句内计 du_2022 有向情感, 乘以 mention_density 权重后在银行-年内求和得本列。据此 ss 轨度量的是「银行与金科紧邻语境中的」加权情感体量, 语义最聚焦但样本方差最大, 在开发期 T 较小的语料上可能高度退化甚至零方差, 属预期表现而非缺陷。ss 轨回退语义镜像 ctx: 当某报道无银行与金科同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback 置真, 与 ctx 共享 n_articles 分母; 当金科 AC 自动机为空时 is_fallback 全真降级。在 full-only 门控下 ss 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集子集。本列与 full、ctx 两轨互为稳健性、不分主次、各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J; 政治词权重固定 0.5, 权重梯子与价值加权/非加权口径均为并排稳健轨, 与本轨正交。作为分子量本列不做归一化, 因同句窗裁剪最严、非空片段最少, 其加权求和在小样本上极易出现零值或极端尾部, 跨银行比较务必先转为价值加权语调或标准化处理; ss 轨的经济学价值在于提供最贴近银行与金科强共现语境的情感体量, 与 full/ctx 轨形成从宽到窄的语料聚焦谱系, 三轨联合可检验主结论对语境裁剪口径的敏感性。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Campbell, J. L., Zheng, X., & Zhou, D. (2025). Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?. Journal of Corporate Finance, 94, 102813. https://doi.org/10.1016/j.jcorpfin.2025.102813
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing Domain-Specific Sentiment Lexicons from Unlabeled Corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing No. 595-605 [Working Paper]. https://doi.org/10.18653/v1/d16-1057
Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press. https://doi.org/10.1017/CBO9780511809071
<!-- rendered-citations:end -->
