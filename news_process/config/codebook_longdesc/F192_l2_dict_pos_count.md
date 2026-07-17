---
family_id: F192
columns:
- dict_pos_count_ctx
- dict_pos_count_full
- dict_pos_count_ss
unit: 篇数/计数 (count, 非负整数计数; 银行-年为聚合单元)
formula: "dict_pos_count{track} = Σ_{i ∈ bank-year} _is_dict_positive_i{track}; 其中 _is_dict_positive{track} = 1[六词典均值极性判为正面], track ∈ {_full, _ctx, _ss}"
producer: "news_process/pipeline/panel/runner.py (washing_cols 块: 由 stage 22 的 {d}_score{track} 现算文章级 _is_dict_positive{track} 并作方法 D 银行-年 sum 聚合) ; news_process/pipeline/panel/encode.py (方法 D 计数域协同, washing_ratio_dict 下游消费)"
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- "22_tone_words.parquet (六词典逐词典文章级极性打分 {d}_score{track}; 注: 文章级 _is_dict_positive{track} 指示列不在本 parquet, 而在 runner.py washing_cols 块由这些 score 列现算)"
citations:
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
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
- doi: "10.1016/j.jaccpubpol.2024.107181"
  type: "journal"
  authors: "Cheng, C. A., Jiang, L., & Song, W.-L."
  year: 2024
  title: "Media coverage and debt financing choice"
  venue: "Journal of Accounting and Public Policy"
  vol: "44"
  pages_or_artno: "107181"
- doi: "10.1111/abac.12322"
  type: "journal"
  authors: "Wang, K. T., Zhu, N. Z., & Luo, G."
  year: 2024
  title: "Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China"
  venue: "Abacus"
  vol: "60"
  issue: "4"
  pages_or_artno: "709-751"
new_dois:
  - "10.1002/isaf.1549"
---

## CORE

【构念与来源】
本家族测度的是"词典法在银行-年层面判为正面的报道篇数"。对于给定银行-年的每一篇目标报道, 上游 stage 22 (tone_words) 先用六部中文金融情感词典对文本逐词打分, 在 22_tone_words.parquet 里逐词典物化文章级极性分列 {d}_score{track}; 需要澄清 provenance: 文章级二值指示列 _is_dict_positive{track} (1=判为正面, 0=其他) 并不落在 stage 22 parquet, 而是在 runner.py 的 washing_cols 块由这六个 {d}_score{track} 现场取均值 (_dict_avg = 六词典 score 逐行 mean) 再判 _dict_avg > 0 现算得到。随后仍在 runner.py 的方法 D 计数域里把这一指示列在银行-年内按 sum 求和, 得到 dict_pos_count{track} (encode.py 的方法 D 计数域负责协同同域分母)。因此该列本质是一个非负整数计数: 它统计"在多部词典的均值共识下被判为正面情绪"的报道数量, 而非情绪强度或占比。它是"洗稿率 / 实质性-象征性"分析机制的一个分母基座——下游 runner.py 用 dict_pos_count{track} 作为 washing_ratio_dict 的回退分母 (通过 _svd_denom 在 dict_pos_substvalid_count 缺失时兜底), 与 dict_pos_symb_count (象征性正面篇数) 构成"正面报道中有多少属于实质性 vs 象征性"的比率。数据来源链条为: 14_materialize_ctx 物化三轨文本 (content_full/ctx/ss) → 22_tone_words 逐词典打分产 {d}_score{track} → runner.py washing_cols 块现算词典均值极性指示列并作方法 D 银行-年 sum 聚合成篇数。

【方法学与计算】
计算分两级。文章级: 词典法对一篇报道给出 pos/neg/neutral 三态判定。这里采用的是"多词典均值共识"口径, 即不依赖任何单一词典, 而是先各词典独立算分再取均值后定极性, 从而降低单部词典覆盖偏倚对判定的影响 (对应源码方法 D "词典均值"; 单部词典的对应族是方法 D2 的 {dict}_pos_count)。银行-年级: 对该单元内所有留篇报道的 _is_dict_positive{track} 做 sum。分母口径遵循留篇门控 = full-only 铁律 (2026-06-29): 一篇报道是否算作"一篇银行金科报道"只由 llm_verified_full == True 决定, ctx/ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但每轨的正面篇数各自按本轨文本重新判定。词典法本身是确定性的 (给定冻结的 jieba==0.42.1 分词与冻结词典), 不调用付费 LLM, 因此该家族在离线复现下逐字节稳定。

【文献定位】
词典法作为金融文本情感测量的基石可追溯至 Loughran & McDonald (2011), 他们指出通用心理学词典 (如 Harvard IV) 在金融语境下系统误判, 主张构建领域专用词典; Loughran & McDonald (2016) 的综述进一步把词典法确立为可复制、透明、无监督的主流测度范式。本项目在中文语境下沿用这一逻辑: 词典均值口径融合了包括 Du et al. (2022) 与 Bian et al. (2021) 在内的多部为中文金融文本专门构建的情感词典, 以对冲任一单部词典的领域偏差。Frankel et al. (2022) 系统比较了词典法与机器学习法在披露情感度量上的差异, 论证二者各有系统性偏误、宜并置互证而非彼此替代; Huang et al. (2023) 的 FinBERT 则代表基于深度模型的第三条测量路径。本项目正是据此把词典 (方法 D)、LLM 投票、BERT 三条测量轨并置为互为稳健性、不分主次的测量三角——三法各自 just-identified 并排, 严禁把跨方法的篇数计数混进同一 over-identified Hansen J。dict_pos_count 家族是这三角中"词典均值"一支在正面篇数维度的落点。Todd, Bowden, & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 的综述系统梳理了金融文本情感测量的词典法与机器学习法各自的适用边界与互补关系, 为本家族采用多词典均值共识判正的设计选择提供了最新文献定位。 就「文章级极性判定 → 按主体-年对极性指示求和」这一聚合形态本身, Cheng、Jiang 与 Song (2024) 提供了前沿实证用例: 该文把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量与新闻情感变量, 作为解释变量进入债务融资方式选择回归, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率。须诚实标注其锚定射程: 原文的极性来自 RavenPack 的专有事件情感分析 (ESS), 既非公开情感词典、亦非人工编码, 因此它只锚定本家族「对极性指示逐主体-年求和」的聚合形态, 不锚定本家族赖以判正的六词典均值共识; 且原文主体为美国上市公司而非商业银行。在中文语料一侧, Wang、Zhu 与 Luo (2024) 用逾 188,000 篇出自中国最具影响力报纸、由记者撰写的公司特定报道, 把新闻按公司-年归集为计数型暴露变量以检验其对企业创新产出的影响, 印证了中文报纸报道的主体-年计数本身即可作为一个独立的文本暴露测度。其锚定同须限定: 该文未构造任何语调或情感变量, 锚定只及于「报道量计数化」这一环, 本家族在其上叠加的词典极性判正门不在其射程之内; 原文主体亦为 A 股非金融企业, 且无三轨文本设计。
## VAR: dict_pos_count_full

【变体差分】
本列是 full 轨落点, 也是本家族的 canonical 计数轨。full 轨文本 = 标题 prepend + 全文正文 (content_full), 即在 stage 14 把标题拼接到正文前后对整篇做词典均值极性判定, 再在银行-年内对 _is_dict_positive_full 求和。按留篇门控 full-only 铁律 (2026-06-29), 一篇报道是否计入"一篇银行金科报道"的判定完全由 full 轨的 llm_verified_full 决定, 因此本列的行宇宙与分母口径正是标准的银行-年留篇集, 是家族三轨中语义最完整、覆盖最全的口径。相对 ctx/ss 两轨, 本列采用整篇文本, 捕捉的正面情绪信号不受实体窗口或同句共现窗口的裁剪, 因而在任一银行-年上其计数通常 ≥ ctx/ss 对应列 (信号面更宽)。本列与 ctx/ss 互为稳健性、不分主次: 三轨各自 just-identified 并排进入下游washing_ratio_dict 等构造, 严禁把三轨的篇数计数混进同一 over-identified Hansen J。作为家族 canonical 轨, 本列既直接是"词典判正面报道量"的水平测度, 又充当下游洗稿率 washing_ratio_dict 的回退分母基座 (dict_pos_symb_count / _svd_denom(dict_pos_substvalid_count, dict_pos_count))。需要强调的是, 本列的正面判定采用六词典均值共识而非任一单部词典, 因此与方法 D2 的单词典族 (如 du_2022_pos_count、bian_2021_pos_count) 在构念上互补: 单词典族刻画特定领域词表的敏感度, 而本 canonical 均值族刻画多词表交叉验证后的稳健正面信号量, 二者不可相互替代。full 轨作为整篇口径, 也是与 ctx/ss 两收窄轨对照时的信息上界, 承担规格稳健性梯子的锚点角色。

## VAR: dict_pos_count_ctx

【变体差分】
本列是 ctx 轨落点。ctx 轨文本 = 标题 prepend + 实体窗口 (content_ctx), 即只保留围绕目标银行实体出现处的上下文窗口再做词典均值极性判定, 而非整篇正文。因此本列统计的是"在实体邻近上下文里被词典均值判为正面"的报道篇数, 语义上比 full 轨更聚焦于与目标银行直接相关的表述, 剔除了远离实体的段落可能引入的无关情绪噪声。相对 full 轨, ctx 轨文本面更窄, 同一银行-年上其正面篇数通常 ≤ full 对应列。按留篇门控 full-only 铁律 (2026-06-29), 本轨不独立决定留篇: 其行宇宙是 full 留篇集的子集 (conditional-on-full), 但正面判定按本轨的 content_ctx 文本重新计算, 是 conditional-on-full 的测度轨/稳健性轨而非主门控轨。本列与 full/ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。当上游 content_ctx 缺失或实体窗口为空时按既定优雅降级处理, 不向 full 轨借分母。它服务于"把测量口径从整篇收窄到实体上下文, 主结论是否稳健"的规格稳健性检验。与 full 轨相同, 本列的正面判定同样走六词典均值共识, 差异仅在于输入文本被裁剪到实体窗口这一维度——轨道差异是文本口径的差异, 而非词典构成或极性阈值的差异, 这保证了三轨间的可比性只受"看多少文本"这单一因素驱动。因此本列与 full/ss 的对照, 恰好隔离了"实体邻近上下文相较整篇是否改变词典判正结论"这一效应, 是三轨规格稳健性梯子中承上启下的中间口径。

## VAR: dict_pos_count_ss

【变体差分】
本列是 ss 轨落点。ss 轨文本 = 标题 prepend + 银行∧金科同句±N 窗 (content_ss, 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 即只保留目标银行与金融科技词同句共现 (含前后 N 句) 的最窄上下文, 再做词典均值极性判定。因此本列统计的是"在银行与金科强共现的同句窗口里被词典均值判为正面"的报道篇数, 是三轨中语义最严格、文本面最窄的口径, 最贴近"这篇报道就目标银行的金融科技活动本身给出的情绪"。ss 轨的回退语义镜像 ctx 轨: 当某篇无银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True (与 full 共享 n_articles 分母); 当 FINTECH_AC=None 时 *_is_fallback 全 True 优雅降级。按留篇门控 full-only 铁律 (2026-06-29), 本轨同样是 conditional-on-full 的测度轨, 行宇宙为 full 留篇集子集, 不独立决定留篇。同一银行-年上其正面篇数通常最小 (信号面最窄, 且受回退行影响)。本列与 full/ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。它服务于"把测量口径收窄到最严格的银行-金科同句共现, 主结论是否稳健"的规格稳健性检验。与 full/ctx 一致, 本列词典均值口径与极性阈值完全相同, 唯一变化维度是文本被裁剪到银行∧金科同句共现窗——因此三轨对照严格隔离了"看多少文本"这单一因素。在开发期 T=2 的极浅面板上, 由于同句共现窗口极窄, ss 轨常出现大量回退或零方差退化, 属预期现象而非缺陷; 在生产期 T=19 全语料上该轨方可提供有意义的最严口径稳健性信号。综上, 本列是三轨规格稳健性梯子中最保守的一端, 与 full canonical 端形成上下界夹逼。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
Wang, K. T., Zhu, N. Z., & Luo, G. (2024). Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China. Abacus, 60(4), 709-751. https://doi.org/10.1111/abac.12322
<!-- rendered-citations:end -->
