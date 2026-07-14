---
family_id: F142
columns:
- cater_finbert_cn_ctx
- cater_finbert_cn_full
- cater_finbert_cn_ss
unit: 无量纲情感差值 (词典 net tone 与 FinBERT_CN net tone 同标度相减, 理论区间约 [-2, 2])
formula: "cater_finbert_cn{track} = dict_avg_tone{track} - (finbert_cn_pos{track} - finbert_cn_neg{track}); track in {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (step 8d, algo_cater 块) ; news_process/pipeline/panel/export.py (Stata 标签)
upstream:
- pipeline/panel/geography.py:227 (dict_avg_tone{track}, panel 装配阶段由六词典 {d}_tone{track} 跨词典均值合成; 底层信号源=22_tone_words.parquet 的 {d}_tone{track})
- 23_tone_berts.parquet (finbert_cn_pos{track}, finbert_cn_neg{track})
- 24_herd_decay.parquet (篇章级 verified 集聚合分母)
citations:
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
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1093/rfs/hhad021"
  type: journal
  authors: "Cao, S., Jiang, W., Yang, B., & Zhang, A. L."
  year: 2023
  title: "How to Talk When a Machine Is Listening: Corporate Disclosure in the Age of AI"
  venue: "The Review of Financial Studies"
- doi: "10.1016/j.frl.2024.105227"
  title: "Sentiment trading with large language models"
  authors: "Kirtac, K., & Germano, G."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
- doi: "10.1080/16081625.2025.2551345"
  title: "Unlocking disclosure narratives: readability, length, and sentiment cues as indicators of bankrupt Japanese companies"
  authors: "Tsunogaya, N., Shinozawa, Y., & Togashi, A."
  year: 2025
  venue: "Asia-Pacific Journal of Accounting & Economics"
  type: "journal"
new_dois:
  - "10.1093/rfs/hhad021"
  - "10.1016/j.frl.2024.105227"
  - "10.1080/16081625.2025.2551345"
---

## CORE

【构念与来源】
本家族 cater_finbert_cn 度量的是"算法迎合度"(algorithmic catering) 中的一个具体切片: 对同一批银行金融科技报道, 中文金融情感词典给出的净语调 (net tone) 与深度语言模型 FinBERT_CN 给出的净语调之间的方向性落差。经济学与会计学近年的一条线索认为, 当信息生产者知道下游读者越来越多是"机器"(自动化情感抓取、算法交易、监管文本挖掘) 而非人类时, 会有动机把文本雕琢成对某一类阅读器更"讨喜"的形态; 落差因此可被读作一个代理变量: 词典阅读器与深层模型阅读器对同一文本的情绪估计出现系统性分歧, 往往意味着文本里存在只对某一类抽取器起作用的表层修辞 (堆砌词典正面词而语义并不正面, 或反之)。本测度取词典侧减模型侧: 正值表示词典比 FinBERT_CN 读得更正面, 即文本更可能是"面向关键词抽取器的迎合"; 负值表示深层模型比词典读得更正面, 即语义层面的积极信号未被词表捕获。它不是情绪本身的水平度量, 而是两种测量范式之间的残差型对齐度量, 与家族外的 tone 水平列构念不同。

【方法学与计算】
计算落在面板总装阶段 (stage 40, runner.py 步骤 8d 的 algo_cater 块), 而非情感打分阶段本身——它是纯后处理的两列相减, 不重新调用任何模型或 API。逐轨公式为 cater_finbert_cn{track} = dict_avg_tone{track} − (finbert_cn_pos{track} − finbert_cn_neg{track}), 其中 dict_avg_tone 是六部中文金融词典的篇均综合净语调 (来自 stage 22 tone_words), finbert_cn_pos/finbert_cn_neg 是 FinBERT_CN 模型在该轨上的正/负类概率均值 (来自 stage 23 tone_berts), 二者之差即模型侧 net tone。两侧都已在各自阶段完成篇章级到银行年度的聚合, 分母口径统一采用 stage 21 语义精筛后的 verified 篇集 (经 24_herd_decay 传导); 留篇门控遵循 full-only 口径 (2026-06-29): 一篇是否算作银行金融科技报道只看 full 轨的 llm_verified_full, ctx/ss 是条件于 full 留篇集的子集测度。三轨 full/ctx/ss 用完全相同的减法内核逐轨独立计算: full = 标题 prepend 加全文正文; ctx = 标题加实体上下文窗口; ss = 标题加银行与金融科技同句共现窗口 (回退语义镜像 ctx——无同句共现时 content_ss 退化为全文 body 并置 ss_is_fallback)。任一侧输入列缺失时该轨该列静默不产出而非零填充, 保留自然缺失 NaN (listwise 原则)。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把三轨混进同一 over-identified Hansen J。

【文献定位】
本测度的方法学锚点是词典法与机器学习法在金融文本情感测量上的系统性分歧这一实证事实。Frankel, Jennings 和 Lee (2022) 在其披露情感研究中直接比较了机器学习与词典方法, 表明两者对同一文本的情绪判断可以显著背离, 且这一背离本身携带增量信息——这正是本家族把"词典减模型"当作一个可解释变量而非误差的依据。Loughran 和 McDonald (2016) 的综述系统梳理了词表法在金融会计文本分析中的适用边界与失真来源, 为词典侧读数的偏差方向提供了先验。深层模型侧的 FinBERT_CN 是一个独立的中文金融领域微调语言模型, 它与 Huang, Wang 和 Yang (2023) 所刻画的英文 FinBERT 并非同一模型, 只是同属"在通用预训练语言模型之上叠加金融领域微调"这一更宽的方法学路径 (该路径的更早源头可追溯到金融领域情感建模与领域自适应的一系列工作, 本家族不以某一篇为唯一开创者)。Huang 等 (2023) 的价值在于系统论证了此类领域微调模型相对纯词表法在捕捉上下文与否定/转折等语义结构上的增量, 本测度据此把 FinBERT_CN 读数与词典侧读数的落差合理归因于表层修辞而非模型噪声, 而不主张 finbert_cn 出自该文所开创的谱系。词典侧的中文金融情感词表则以 Du, Huang, Wermers 和 Wu (2022) 的领域专用词典为代表, 说明了语言与领域特异性如何塑造词表读数。更早的 Tetlock (2007) 奠定了媒体文本语调进入金融实证的范式基础, 而 Gilardi, Alizadeh 和 Kubli (2023) 则从另一端提示大模型类标注器与规则型标注器在一致性上的差异, 二者共同界定了本测度所处的测量范式对照坐标。Cao, Jiang, Yang 和 Zhang (2023, The Review of Financial Studies) 首次系统证明公司在知晓算法读者日益增多后会主动调整文本措辞以迎合机器抓取, 是本家族"算法迎合度"这一构念的直接命名与实证源头。Kirtac 和 Germano (2024, Finance Research Letters) 比较大语言模型情感打分与传统词典法(Loughran-McDonald)在预测股票收益上的表现差异, 发现二者读数系统性背离且大语言模型侧携带增量信息, 为本家族"词典减模型"落差型测量提供了词典与大语言模型分歧本身具信息量的最新实证支持。Tsunogaya, Shinozawa 和 Togashi (2025, Asia-Pacific Journal of Accounting & Economics) 对比词典法与机器学习法两种情感测量路径在公司叙事性披露中的表现, 发现主题型情感模型无论采用哪种测量范式均优于句法型模型, 呼应本家族把词典侧与深度模型侧读数差异当作可解释残差而非噪声的处理思路。

## VAR: cater_finbert_cn_ctx

【变体差分】
本列为 ctx 轨 (上下文窗口轨) 的算法迎合度落差。其文本口径为标题 prepend 加银行实体上下文窗口: 只保留目标银行实体邻近窗内的正文, 而非整篇报道。相对 full 轨, ctx 轨刻意收窄到与银行实体直接相关的语境, 用以剥离整篇报道中与该银行无关的段落对情绪测量的稀释, 是一条聚焦式稳健性轨。落差本身的减法内核与其余两轨完全一致: dict_avg_tone_ctx 减去 FinBERT_CN 在 ctx 轨的净语调 (finbert_cn_pos_ctx − finbert_cn_neg_ctx)。在 full-only 留篇门控下, ctx 轨为条件于 full 留篇集的子集测度, 其行宇宙不超过 full 轨。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把它与另两轨混入同一 over-identified Hansen J: 三者是对同一"词典与模型分歧"构念在不同文本裁剪口径下的平行测量, 应各自进入独立设定作稳健性对照, 而不是当作可叠加的多重工具变量。任一侧 ctx 列缺失时本列该行留 NaN 不零填充。需特别提示读法方向: 本列与家族公式一致取词典侧减模型侧, 因此正值仍读作"词典比 FinBERT_CN 读得更正面"、疑似面向关键词抽取器的表层迎合, 负值读作"深层模型比词典读得更正面"、语义积极信号未被词表捕获; ctx 轨因窗口收窄、样本量小于 full 轨, 其落差水平不宜与 full/ss 直接比较绝对值, 只宜在各自设定内比标准化后的回归系数。ctx 轨与 full、ss 的落差取自完全同源的两个上游阶段 (词典侧 stage 22、模型侧 stage 23), 差别仅在于喂给两个阶段的文本裁剪口径不同, 故三轨之间的差异纯由文本窗口而非测量算法引入。

## VAR: cater_finbert_cn_full

【变体差分】
本列为 full 轨 (全文轨) 的算法迎合度落差, 也是留篇门控的定义轨。其文本口径为标题 prepend 加全文正文: 一篇报道是否被判为银行金融科技报道、进而进入本测度的分母, 完全由 full 轨的 llm_verified_full 决定 (full-only 门控, 2026-06-29), 因此 full 轨的行宇宙是三轨中最宽的, ctx 与 ss 均为其子集。落差取 dict_avg_tone_full 减去 FinBERT_CN 在 full 轨的净语调 (finbert_cn_pos_full − finbert_cn_neg_full)。相对 ctx/ss 的窄窗口口径, full 轨覆盖整篇报道的全部措辞, 因而对"通篇堆砌词典正面词而语义中性"这类跨段落的表层迎合最敏感, 是三轨中信息覆盖最完整的一条。full 与 ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified Hansen J。需强调 full 轨在本家族并不承担"主测度、其余为副"的等级含义: 三轨是平行的稳健性并排, full 的特殊性仅在于它同时充当留篇门控的判定轨。任一侧 full 列缺失时本列该行留 NaN。就读法而言, full 轨落差为正表示整篇报道在词典关键词层面比 FinBERT_CN 的语义读数更正面, 提示通篇存在只对词表抽取器起作用的正面措辞堆砌; 为负则表示深层模型从上下文与否定/转折结构中读出了词表遗漏的积极信号。因为 full 轨保留整篇正文, 它对跨段落、跨句的表层迎合最敏感, 也最容易受到与目标银行无关段落的干扰——这正是 ctx 与 ss 两条窄窗轨作为稳健性对照存在的理由。三轨的落差水平不可直接横向比较绝对值 (窗口不同导致分母与文本量不同), 只宜在各自 just-identified 设定内比标准化系数; 把 full 与 ctx、ss 拼进同一 over-identified Hansen J 会错误地把平行稳健性测量当作可叠加的过度识别工具。

## VAR: cater_finbert_cn_ss

【变体差分】
本列为 ss 轨 (同句共现轨) 的算法迎合度落差, 是三轨中口径最严的一条。其文本口径为标题 prepend 加银行与金融科技同句共现窗口: 只保留目标银行与金融科技词在同一句子 (±N 句半径, 由 config 的 ss_sentence_radius 控制, 默认 1) 内共现的语境。ss 轨的回退语义严格镜像 ctx 轨——当某篇报道不存在银行与金融科技的同句共现时, content_ss 优雅退化为全文 body 并置 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母; 当金融科技 AC 自动机整体为空时 ss 全篇进入 fallback 优雅降级。落差减法内核与另两轨一致: dict_avg_tone_ss 减去 FinBERT_CN 在 ss 轨的净语调 (finbert_cn_pos_ss − finbert_cn_neg_ss)。在 full-only 门控下 ss 同为条件于 full 留篇集的子集测度。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified Hansen J。ss 轨的价值在于把"词典与模型分歧"约束到银行金融科技直接同句的最紧语境, 用以检验落差是否由银行金科议题本身而非报道其余部分驱动; 在浅面板 (T 较小) 上 ss 轨可能因共现稀疏而大量回退, 属预期退化。任一侧 ss 列缺失时本列该行留 NaN 不零填充。ss 轨的读法方向与另两轨一致 (词典侧减模型侧, 正值即疑似面向词表抽取器的迎合), 但因回退行的 content_ss 实际等同全文 body, 使用者须结合 ss_is_fallback 标记区分"真同句共现测量"与"回退到全文"的两类行, 避免把大面积回退误读为落差本身的信号。

<!-- rendered-citations:begin -->
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to Talk When a Machine Is Listening: Corporate Disclosure in the Age of AI. The Review of Financial Studies. https://doi.org/10.1093/rfs/hhad021
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters. https://doi.org/10.1016/j.frl.2024.105227
Tsunogaya, N., Shinozawa, Y., & Togashi, A. (2025). Unlocking disclosure narratives: readability, length, and sentiment cues as indicators of bankrupt Japanese companies. Asia-Pacific Journal of Accounting & Economics. https://doi.org/10.1080/16081625.2025.2551345
<!-- rendered-citations:end -->
