---
family_id: F360
columns:
- jiang_2021_tone_sum_ctx
- jiang_2021_tone_sum_full
- jiang_2021_tone_sum_ss
unit: 语调总和 (连续, 无界符号量; bank-year 内逐篇归一化语调分的算术和, 量纲与篇数正相关)
formula: 'jiang_2021_tone_sum_{track} = Σ_articles jiang_2021_score_{track}; 其中逐篇
  jiang_2021_score_{track} = Σ final_score / Σ|final_score| ∈ [-1,1] (final_score
  = base_score × degree_multiplier × 转折加成, base_score 取自姜富伟等(2021)词典正负极性,
  经否定翻转/程度副词六级/转折句式三条语言学规则叠加; 该 sum 由 pipeline\panel\encode.py::build_aggregation_dict
  对 {jiang_2021}_score{track} 做 groupby(bank,year).sum() 得到, 与均值口径 jiang_2021_tone_{track}
  共用同一逐篇分子, 仅聚合算子由 mean 改 sum)'
producer: pipeline\panel\encode.py (build_aggregation_dict, 聚合层) ; pipeline\sentiment\tone_words.py
  (score_text_sentiment, 逐篇打分层) ; pipeline\panel\stata_export.py ; pipeline\panel\export.py
upstream:
- jiang_2021_score_full
- jiang_2021_score_ctx
- jiang_2021_score_ss
- 21_tone_llms.parquet (留篇门控 llm_verified_full)
- 22_tone_words.parquet (逐篇词典打分)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, Paul C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Ma, Yuanyuan; Zhang, Tianjie; Zhang, Pingping"
  year: 2025
  venue: "Expert Systems with Applications"
  type: "journal"
  one_sentence_zh: "该文构建面向中国境内投资者的中文细粒度情感词典 (CN-FSD), 与本家族姜富伟词典同属中文财经文本情感词典构建方法论谱系, 佐证词典法情感测度在中文语境下仍是活跃研究方向。"
- doi: "10.1002/fut.70037"
  title: "Media Sentiment and Volatility Index Futures Returns: Evidence from Textual Analysis of News, Blogs, and Online Discussions"
  authors: "Wu, Ming-Hung; Chen, Chun-Yo; Cheng, Nai-Wen; Tsai, Wei-Che"
  year: 2025
  venue: "Journal of Futures Markets"
  type: "journal"
  one_sentence_zh: "该文对新闻、博客、论坛文本做情感总量式文本分析并检验其对波动率期货收益的预测力, 呼应本家族 tone_sum 度量所承载的\"媒体情绪总暴露量\"构念定位。"
new_dois:
  - "10.1016/j.eswa.2024.125739"
  - "10.1002/fut.70037"
---

## CORE

【构念与来源】
本家族三列 jiang_2021_tone_sum_{full,ctx,ss} 是词典法情感测度族中「求和」聚合口径的一支, 底层词典为姜富伟、孟令超、唐国豪 (2021, 《经济学(季刊)》) 面向中文财经文本构建的情感词典 (jiang_2021)。与 F360 姊妹家族的均值口径 jiang_2021_tone_{track} (bank-year 内逐篇归一化语调分的算术平均) 不同, tone_sum 是同一逐篇分子在 bank-year 分组内的算术求和 (groupby(bank, year).sum()), 而非算术平均。这意味着 tone_sum 同时承载两个信息: 语调方向 (符号) 与报道体量 (篇数), 二者纠缠在同一标量里——某银行某年若报道篇数多、每篇语调温和正面, 其 tone_sum 可能与另一银行报道篇数少但每篇语调强烈正面的 tone_sum 数值接近甚至更大, 这与 tone (均值) 度量的"平均语气强弱"是两种不同的经济学构念。tone_sum 更接近 Tetlock (2007, JF) 意义上"媒体情绪总暴露量"(aggregate sentiment exposure) 的构造思路, 适合作为报道体量与语调方向联合作用的稳健性测度, 而非替代均值主测度。

【方法学与计算】
逐篇分子 jiang_2021_score_{track} 由 pipeline\sentiment\tone_words.py 的状态机打分函数产出: 先用姜富伟词典对切词结果做正负极性标注 (base_score), 再依次叠加否定规则 (否定词翻转极性)、程度副词六级乘子 (degree_multiplier)、转折句式加成 (ADVERSATIVE_BOOST) 三条语言学规则得到 final_score, 逐词累加得 total_score = Σ final_score, 并以加权幅度和 total_abs_score = Σ|final_score| 归一化, 得 normalized_score = total_score / total_abs_score ∈ [-1, 1] (若 total_abs_score = 0, 即全文无匹配词, 该篇取 0.0)。这一逐篇归一化分即 jiang_2021_score_{track}, 是 tone_sum 与 tone (均值)、tone_std (标准差) 三个聚合口径共享的唯一分子来源, 三者仅聚合算子不同 (sum / mean / std)。聚合层 pipeline\panel\encode.py::build_aggregation_dict 对 full/ctx/ss 三轨分别执行相同的 groupby-sum, 三轨 SSOT 为同一份聚合字典构造循环, 不存在轨间口径漂移。行样本口径遵循 2026-06-29 起生效的留篇门控: 是否计入某篇报道由 llm_verified_full (仅看 full 轨 LLM 判定) 决定, ctx/ss 轨的 tone_sum 行样本因此是 full 留篇集合的子集而非独立样本, 三轨互为稳健性测度、不分主次, 严禁把三轨并入同一 over-identified 的 Hansen J 检验中联合识别。ss 轨若某 bank-year 内无任何一篇报道满足"银行∧金科同句共现", 该篇的 content_ss 回退为全文 body (ss_is_fallback=True), 语义上镜像 ctx 轨的回退规则, 但仍计入 tone_sum 的求和分母 (即回退不改变是否入样本, 只改变该篇文本窗口)。

【文献定位】
词典求和法情感度量的方法论根基见 Tetlock (2007, Journal of Finance) 对媒体情绪与股票回报关系的开创性研究, 该文首次系统论证媒体文本中情绪总量对资产定价的解释力; 中文财经语境下姜富伟等 (2021, 《经济学(季刊)》) 构建的情感词典专门针对中国财经媒体报道的用词习惯与语言结构标注正负极性词表, 是本项目词典法六部词典之一, 亦是本家族的直接词源。Du et al. (2022, Review of Finance) 进一步指出中文金融文本情感分析须兼顾语言特异性 (与英文 Loughran-McDonald 词典不可简单迻译), 为本项目并行维护姜富伟、Du 等多部中文词典、并对每部词典分别输出 sum/mean/std 三种聚合口径提供了方法论依据。Frankel, Jennings & Lee (2022, Management Science) 系统比较机器学习与词典法情感度量的信息含量, 指出二者互为稳健性检验而非互相替代, 与本项目"词典法/LLM 投票法/BERT 分类法三方法并排、互为稳健"的设计哲学一致——tone_sum 与 tone (均值) 同属词典法内部的聚合口径梯度, 二者也应互为稳健性看待, 不应把 sum 简单等同于 mean 的加权放大版本。Ma, Zhang & Zhang (2025, Expert Systems with Applications) 构建面向中国境内投资者的中文细粒度情感词典 (CN-FSD), 与本家族姜富伟词典同属中文财经文本情感词典构建方法论谱系, 佐证词典法情感测度在中文语境下仍是活跃研究方向。Wu, Chen, Cheng & Tsai (2025, Journal of Futures Markets) 对新闻、博客、论坛文本做情感总量式文本分析并检验其对波动率期货收益的预测力, 呼应本家族 tone_sum 度量所承载的"媒体情绪总暴露量"构念定位。

## VAR: jiang_2021_tone_sum_ctx

【变体差分】
本列是 jiang_2021_tone_sum 家族中的实体上下文轨 (ctx)。分子文本窗口 content_ctx = 标题 + 目标银行实体窗口内的正文片段 (而非全文), 由 stage 14 ctx_materializer 在 stage 21 情感打分之前物化, 与 full 轨共享同一份词典规则引擎但输入文本范围更窄, 聚焦在银行实体被提及的局部语境。若某篇报道未能定位到银行实体窗口 (无法圈出上下文片段), content_ctx 回退为全文 body, 由 ctx_is_fallback=True 标记, 该回退不改变该篇是否计入 tone_sum 求和 (行样本仍由 full 轨 llm_verified_full 门控决定), 只改变参与打分的文本内容。与均值口径 jiang_2021_tone_ctx 相比, 本列 (求和) 的经济学解释是"该银行该年内, 聚焦实体上下文窗口后的语调总暴露量", 更贴近"媒体围绕该银行核心叙事的情绪总量"而非"平均语气"。ctx 轨与 full/ss 两轨互为稳健性并排关系, 三者对同一构念给出不同文本粒度下的重复测量, 不设主次高低, 也不应把三轨系数联合塞进同一 over-identified 的 Hansen J 检验框架中做过度识别检验——每一轨各自 just-identified, 分别汇报回归系数与显著性作横向对照即可。使用者若关心"排除无关正文噪声后银行相关语调总量是否与 full 轨一致", 应把本列与 jiang_2021_tone_sum_full 并列汇报而非相减或加权合并。

## VAR: jiang_2021_tone_sum_full

【变体差分】
本列是 jiang_2021_tone_sum 家族的全文轨 (full), 是三轨中留篇门控的锚定轨: 是否有一篇报道被计入该银行该年的分析样本, 完全由 llm_verified_full (仅基于全文轨 LLM 判定该篇是否确属"一篇银行—金科报道") 决定, ctx/ss 两轨的行样本均是 full 轨留篇集合的子集。分子文本窗口 content_full = 标题 + 完整正文 (prepend_title 拼接, 不做实体窗口截断), 是姜富伟词典规则引擎 (否定/程度副词六级/转折句式三条规则叠加) 扫描的最大文本范围, 因而其逐篇归一化分 jiang_2021_score_full 覆盖信息量最全、但也最可能夹带与目标银行无直接关联的正文噪声词。本列在 sum 口径下的经济学含义是"该银行该年被留篇的全部报道, 在整篇文本粒度下的语调总暴露量", 是三轨 sum 中样本覆盖最完整的一支, 也是 full-only 门控体系下默认的参照锚点。与 ctx/ss 两个稳健性轨并排看待、互不替代, 不构成同一 over-identified Hansen J 中的联合过度识别工具; 与家族内均值口径 jiang_2021_tone_full 的区别在于, 后者衡量"平均语气强弱", 而本列衡量"语调总暴露量", 两者应结合媒体覆盖篇数 (n_articles_full) 一并解读, 避免把 tone_sum 数值差异误读为纯语气差异; 尤其在跨银行比较时, 报道体量本身的差异会直接放大或压缩 tone_sum 的绝对数值, 单看该列而不看篇数容易得出方向错误的结论。

## VAR: jiang_2021_tone_sum_ss

【变体差分】
本列是 jiang_2021_tone_sum 家族的同句共现轨 (ss)。分子文本窗口 content_ss = 标题 + 目标银行与金科词严格同句 (±N 句窗口, 默认半径 1 句, 见 config/filtering.yaml::context_window.ss_sentence_radius) 共现片段, 判定原语与 stage 13 的邻近共现硬过滤 (±1 句窗口) 是同名不同口径的两套判据, 不可互相复用。若某篇报道内不存在银行∧金科词严格同句共现 (即无法圈出 ss 片段), content_ss 回退为全文 body, 由 ss_is_fallback=True 标记, 语义上镜像 ctx 轨的回退规则; 回退同样不改变该篇是否计入 tone_sum 求和的行样本判定 (仍由 full 轨门控决定), 只改变实际参与打分的文本窗口, 二者共享同一分母 n_articles 口径。本列在 sum 口径下的经济学含义是"该银行该年内, 银行与金科议题在同一句被同时提及的段落, 其语调总暴露量", 是三轨中文本窗口最窄、噪声最少但也最可能因窗口过窄而将大量报道退化为 fallback (回退到全文) 的一支——尤其在报道密度较低的开发期样本 (T=2) 上, ss 轨的有效非回退观测可能占比很低, 属预期退化而非缺陷。ss 轨与 full/ctx 两轨各自 just-identified, 三者互为稳健性并排, 严禁混入同一 over-identified Hansen J 联合识别; 使用者应把本列理解为"银行—金科议题共现语境下语调总量"的稳健性检验支路, 而非替代 full/ctx 轨的主测度。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Tetlock, Paul C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Ma, Yuanyuan; Zhang, Tianjie; Zhang, Pingping. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
Wu, Ming-Hung; Chen, Chun-Yo; Cheng, Nai-Wen; Tsai, Wei-Che. (2025). Media Sentiment and Volatility Index Futures Returns: Evidence from Textual Analysis of News, Blogs, and Online Discussions. Journal of Futures Markets. https://doi.org/10.1002/fut.70037
<!-- rendered-citations:end -->
