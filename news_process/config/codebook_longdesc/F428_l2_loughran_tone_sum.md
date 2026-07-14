---
family_id: F428
columns:
- loughran_tone_sum_ctx
- loughran_tone_sum_full
- loughran_tone_sum_ss
unit: 语调净得分 (连续, 未按词量归一化的原始正负计数差; bank-year 面板层对跨文章文章级取值求和 sum, 而非均值, 量纲随该 bank-year 单元文章数增长而线性增大)
formula: 'loughran_tone_sum = pos_count(L&M中文主译本) - neg_count(L&M中文主译本), 逐篇计, 经语言学规则(否定翻转/程度副词/转折句式)修正后的正负词命中计数之差; 与同族已归一化的 loughran_tone (= tone_sum / max(1, pos_count+neg_count) 或等价的比例型语调) 相对, tone_sum 保留原始计数量纲不做词量归一化; 面板层聚合 (encode.py agg[f"{d}_tone_sum{track}"]=(f"{d}_score{track}", "sum")) 对 bank-year 单元取跨文章求和 (sum), 与同族 loughran_tone 的跨文章均值 (mean) 聚合口径不同, 使用时须留意 sum 会随单元内文章数线性增长而非围绕稳定水平波动'
producer: pipeline\sentiment\tone_words.py ; pipeline\panel\stata_export.py
upstream: []
citations:
- {doi: "10.1111/j.1540-6261.2010.01625.x", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2011, title: "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks", venue: "The Journal of Finance", vol: "66", issue: "1", pages_or_artno: "35-65"}
- {doi: "10.1093/rof/rfab036", type: journal, authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W.", year: 2022, title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary", venue: "Review of Finance", vol: "26", issue: "3", pages_or_artno: "673-719"}
- {doi: "10.1111/1475-679X.12123", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2016, title: "Textual Analysis in Accounting and Finance: A Survey", venue: "Journal of Accounting Research", vol: "54", issue: "4", pages_or_artno: "1187-1230"}
- {doi: "10.1287/mnsc.2021.4156", type: journal, authors: "Frankel, R., Jennings, J., & Lee, J.", year: 2022, title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods", venue: "Management Science", vol: "68", issue: "7", pages_or_artno: "5514-5532"}
- {doi: "10.1016/j.eswa.2024.125739", type: journal, authors: "Ma, Y., Zhang, T., & Zhang, P.", year: 2025, title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application", venue: "Expert Systems with Applications", vol: "264", pages_or_artno: "125739"}
- doi: "10.1016/j.procs.2025.04.477"
  title: "Enhancing Financial Sentiment Analysis: Integrating the Loughran-McDonald Dictionary with BERT for Advanced Market Predictive Insights"
  authors: "Sheetal, R., & Aithal, P. K."
  year: 2025
  venue: "Procedia Computer Science"
  type: "journal"
- doi: "10.1142/s2282717x25500069"
  title: "When Words Backfire: Tone Management and Crash Risk in Banking"
  authors: "Meles, A., Pellegrino, L. R., & Rega, F. G."
  year: 2025
  venue: "Journal of Financial Management, Markets and Institutions"
  type: "journal"
new_dois:
  - "10.1016/j.procs.2025.04.477"
  - "10.1142/s2282717x25500069"
---

## CORE

【构念与来源】
本家族衡量的是银行∧金融科技共现报道中, 基于 Loughran & McDonald (2011) 情感词典中文主译本 (loughran_mcdonald_zh_2026, 别名前缀 loughran) 计算出的语调净得分之"未归一化和"版本 (tone_sum), 用以捕捉每篇报道正负词汇净计数的原始规模信息。词典来源、加载与消歧规则的 SSOT 是 `config/tone_dicts.json` 与 `pipeline/sentiment/tone_words.py`: loughran 词典含 positive(1,295 词)、negative(3,729 词), 另含 6 类非极性词类 (uncertainty/litigious/strong_modal/weak_modal/constraining/complexity, 用于同族其它衍生列, 与本三列 tone_sum 无关)。词典加载时对该词典内部 positive∩negative 跨类重叠词 (loughran 原 61 词经用户 2026-06-24「两侧保留判断」消歧, 38 词已归单侧、余 23 词不可约简而保留) 采用"保留而非剔除"策略: 登记到 `_BOTH_SIDED_BY_DICT`, 打分时对该 23 词同时计入 pos 与 neg 两侧计数, 使净语调向中性拉近而非武断选边; 该策略仅影响该词典个体的 `{dict}_score` 类净语调测度 (含本 tone_sum 家族), 不影响 pos_ratio/neg_ratio/msent_score 等使用 6 词典固定 union 词典的聚合测度 (union 层面重叠词以 (+1,−1) 平衡双票喂入, 极性 margin 守恒, 逐位不变)。
本家族与家族 canonical `loughran_tone_{full,ctx,ss}` (归一化语调, 已收录于 stata_export 的 curated headline 标签表) 构念同源、量纲不同: tone_sum 是该篇报道正负词命中计数之差的原始值 (可跨行大幅波动, 随文章长度/词汇密度而变), 未按总匹配词数或文章长度做归一化; 而 canonical loughran_tone 是经归一化 (通常以 pos_count+neg_count 或全文词量为分母) 后落在有界区间的比例型语调分。二者构念意图一致 (均衡量净情感极性方向与强度), 但 tone_sum 额外携带"报道涉及该词典情感词汇的绝对丰富程度"信息, 在稳健性检验中可用来交叉验证归一化是否引入了长度混淆; 因此 tone_sum 应被理解为归一化语调测度的一个未归一化姊妹口径, 而非独立构念。
情感语言学规则修正 (否定翻转/程度副词/转折句式三类规则, SSOT 见 `tone_words.py` 头部注释) 在计算 pos_count/neg_count 时已生效, 即本三列的正负计数已吸收句法层面的极性翻转与强度调整, 而非对词袋做简单计数; 这与该家族在词典消融梯度 (`{dict}_score_{raw,negonly,degonly,advonly,...}`) 中的 full 变体口径一致 — 本 tone_sum 家族对应全规则 (full) 变体的净计数版本, 不涉及消融子集。

【方法学与计算】
计算流程: 对每篇文章的三条文本轨 (full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗) 分别运行 jieba 分词 (冻结版本 0.42.1, 保证跨 run 确定性) → 逐词匹配 loughran 词典 positive/negative 集合 → 应用否定翻转/程度副词/转折三类语言学规则修正命中权重 → 加总得到该篇该轨的 pos_count 与 neg_count → tone_sum = pos_count − neg_count (整数或经规则修正后的连续加权和, 未做任何除法归一化)。三轨的扫描文本互不相同 (full 覆盖全文, ctx 限定在实体窗口内, ss 严格限定银行∧金科同句共现窗口), 因此同一篇文章在三轨下的 tone_sum 数值一般不同, 且不可直接相加或平均跨轨合并。
面板聚合层 (`pipeline/panel/encode.py`, 见 `agg[f"{d}_tone_sum{track}"] = (f"{d}_score{track}", "sum")`) 将文章级 tone_sum 按 bank-year 单元取跨文章求和 (sum), 得到本三列在 bank-year 面板中的取值; 这与家族 canonical `loughran_tone{track}` 在同一段代码中采用的 'mean' 聚合口径明确不同 —— tone_sum 是原始计数之和, 量纲会随该 bank-year 单元内文章数增多而线性增大, 不能被解读为"该单元的平均语调水平", 也不能与 tone 的均值口径直接混用比较。分母/行宇宙口径遵循 stage 21 已确立的 full-only 留篇门控 (2026-06-29 起): 是否判定"一篇银行∧金科报道"只看 `llm_verified_full == True`, ctx/ss 两轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集, 各轨分别在该子集上独立求和。ss 轨遵循"镜像 ctx"的回退语义: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 回退为全文 body (`ss_is_fallback=True`), 该回退行仍计入求和参与 bank-year 聚合, 不做静默剔除。
三轨 (full/ctx/ss) 是互为稳健性、不分主次的并排测度轨道: 三者各自作为 just-identified 回归设定并排使用, 严禁将三轨的 tone_sum 混入同一个 over-identified Hansen J 检验框架 (与 CLAUDE.md「当前状态铁律」三轨口径一致)。此外该家族的原始计数与归一化 loughran_tone 之间, 以及未来若引入的政治词权重梯度、词典消融梯度等, 均需保持各自独立、并排比较, 不应交叉混用同一识别方程。

【文献定位】
Loughran & McDonald (2011) 在 The Journal of Finance 提出金融文本情感词典应针对领域专属语义构造 (而非直接借用通用心理学词典), 是本词典族方法学的顶刊锚点; 其 2016 年 Journal of Accounting Research 综述进一步系统化了文本分析在会计与金融研究中的应用规范, 为本家族的词典法定位提供方法论背景。Du et al. (2022, Review of Finance) 针对中文金融文本构造领域专属情感词典, 并证明通用词典直译到中文语境会产生系统性偏误, 这一发现是本项目在词典层面采用多词典并排 (6 部) 而非单一词典的直接理据, 也是本 loughran 家族之外仍并行维护 du_2022/jiang_2021/yao_2021/bian_2021/you_2018 五部词典的方法论依据。Frankel, Jennings & Lee (2022, Management Science) 系统比较了词典法与机器学习法在文本情感测量上的表现差异, 为本项目将词典法 tone_sum/tone 与 LLM 三家投票、BERT 三模型并列作为"互为稳健性"轨道提供了实证支持。Ma, Zhang & Zhang (2025, Expert Systems with Applications) 近期构造中文细粒度情感词典并验证其在中国投资者语境下的效度, 佐证了中文金融文本情感测量仍处于活跃方法学演进期, 本家族的多词典并排策略与之呼应。Sheetal & Aithal (2025, Procedia Computer Science) 该文将 Loughran-McDonald 词典法与 BERT 深度学习模型融合用于金融文本情感分析, 佐证词典法与机器学习法并排互验的方法论定位。Meles, Pellegrino & Rega (2025, Journal of Financial Management, Markets and Institutions) 该文用词典法测度银行管理层文本语调, 发现策略性乐观语调与银行未来股价崩盘风险正相关, 支持语调测度在银行情境下的构念效度。

## VAR: loughran_tone_sum_full

【变体差分】
本列为全文轨 (full) 版本: 情感词命中扫描覆盖文章标题+全文正文 (prepend_title 拼接), 不限定于银行∧金科实体窗口或同句共现范围。作为 stage 21 留篇门控的口径来源, full 轨是"是否判定为一篇银行金科报道"的唯一门控依据 (`llm_verified_full == True`), 因此本列在 bank-year 聚合时纳入求和的文章集合即为该门控下的留篇集合 (其规模对应 `n_articles`), 是三轨中样本覆盖最完整、口径最不受实体窗口/同句范围限制的一列; 面板层聚合口径为跨文章求和 (sum) 而非均值 (mean), 与家族 canonical `loughran_tone_full` 的 mean 聚合不同, tone_sum 数值会随该 bank-year 单元留篇文章数增多而线性增大。与 ctx/ss 相比, full 轨捕捉的是报道整体基调, 可能包含与银行-金科关系无直接关联的段落情感 (如报道中穿插的宏观经济评论、行业整体展望、监管政策解读等与本文核心关系并不直接相关的语句), 因而在测量目标构念 (银行对金科议题的情感倾向) 上引入的噪声理论上高于 ctx/ss, 但样本量与统计效力最大, 且不存在实体窗口划定失败或同句共现缺失所导致的降级/回退问题, 是三轨中数据完整度最高的一列。
在数值量级上, full 轨扫描文本长度通常显著长于 ctx/ss 两轨 (覆盖全文而非窗口片段), 因此在其它条件不变时, 同一篇文章的 full 轨 pos_count 与 neg_count 绝对值往往大于 ctx/ss 轨的对应取值, tone_sum 的跨篇标准差与极值范围也相应更大; 这是未归一化和口径 (tone_sum, 区别于按词量归一化的 canonical tone) 在三轨间比较时需要特别留意的量纲差异, 不应直接把三轨 tone_sum 数值放在同一张表内做水平比较, 而应各自与该轨自身的历史或截面基线比较。full 轨的 tone_sum 与家族 canonical `loughran_tone_full` 共享同一批 pos_count/neg_count 原始计数, 仅在是否除以归一化分母上有差异, 二者构念一致、量纲不同, 可作为交叉验证归一化处理是否引入长度混淆的直接参照。三轨互为稳健性并排使用, full 轨不因门控地位而在识别策略上"优先"于 ctx/ss, 三者仍需分别汇报、禁止混入同一 over-identified Hansen J 检验。

## VAR: loughran_tone_sum_ctx

【变体差分】
本列为实体窗轨 (ctx) 版本: 情感词命中扫描限定在标题+目标银行与金融科技实体共同出现的窗口文本内 (`content_ctx`, stage 14 `ctx_materializer` 物化, `prepend_title`), 而非全文。该轨的行宇宙是 full-only 留篇门控下的子集 (conditional-on-full), 即只在已被 full 轨判定为银行金科报道的文章内计算, 不单独承担留篇判定职能; ctx 轨本身也不再触发独立的门控逻辑, 是"条件于 full 留篇"的测度/稳健性轨。相较 full 轨, ctx 轨通过收窄扫描范围排除了与银行-金科议题无关的段落噪声 (如报道正文中与本次银行-金科关系无关的其它业务线描述、无关企业动态等), 理论上更贴近"该报道对银行金科关系的情感基调"这一构念, 但样本文本长度更短, 单篇 pos_count/neg_count 绝对量级通常小于 full 轨的同篇取值, tone_sum 数值不可与 full 轨直接比较或相加, 二者的量纲差异源自扫描窗口大小不同而非情感极性判定规则不同 (否定翻转/程度副词/转折三类语言学规则在两轨内均同样生效)。
若某篇文章无法确定有效实体窗口 (例如银行实体与金科实体在正文中距离过远、无法圈定合理窗口), ctx 轨遵循优雅降级规则 (`content_ctx_is_fallback` 标记), 降级行的扫描范围回退为可用的最大文本 (与 full 轨口径趋同), 但降级行仍计入该轨求和参与 bank-year 聚合 (面板层聚合口径为跨文章求和 sum, 与家族 canonical `loughran_tone_ctx` 的 mean 聚合不同), 不做静默剔除。ctx 轨与家族 canonical `loughran_tone_ctx` 共享同一批底层 pos_count/neg_count, 仅归一化与聚合算子不同。ctx 与 full、ss 三轨互为稳健性并排, 不分主次, 三者的 tone_sum 严禁混入同一 over-identified Hansen J 检验框架。

## VAR: loughran_tone_sum_ss

【变体差分】
本列为同句轨 (ss) 版本: 情感词命中扫描限定在标题+目标银行与金融科技词汇同句 (±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 共现的文本范围内 (`content_ss`), 是三轨中扫描范围最窄、构念上最贴近"银行与金科在同一叙述单元中被共同评价"这一严格共现口径的一列; 判定原语 `extract_bank_fintech_cooccurrence` 要求银行词与金科词在同一句 (或相邻 ±N 句) 内出现, 与 stage 13 共现硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` (半径窗口口径) 是两个不同的判据, 不可混用。ss 轨行宇宙同样是 full-only 留篇门控下的子集, 只在 full 轨已判定为银行金科报道的文章内计算, 不单独承担留篇判定职能。
ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 回退为全文 body, `ss_is_fallback=True`, 该回退行仍计入求和参与 bank-year 聚合 (面板层聚合口径为跨文章求和 sum, 与家族 canonical `loughran_tone_ss` 的 mean 聚合不同), 不做静默剔除, 以避免因严格同句条件不满足而导致的样本选择性丢失偏误。由于扫描范围最窄 (通常仅一到两句话), ss 轨单篇 pos_count/neg_count 绝对量级通常是三轨中最小的, tone_sum 的跨篇方差也可能因窗口截断而放大, 在小样本 (如本项目 T=2 开发集) 上易出现较大波动、部分单元甚至可能出现零值或高度稀疏的情况, 生产语料 (T=18, 全量) 上预期随样本量增大而更稳定; 且 tone_sum 作为求和口径, 其绝对量级也会随该 bank-year 单元的留篇文章数量本身变化, 不宜孤立解读为语调强弱。ss 轨与家族 canonical `loughran_tone_ss` 共享同一批底层 pos_count/neg_count, 仅归一化与聚合算子不同。ss 与 full、ctx 三轨互为稳健性并排, 不分主次, 三者的 tone_sum 严禁混入同一 over-identified Hansen J 检验框架。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2016). Textual Analysis in Accounting and Finance: A Survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sheetal, R., & Aithal, P. K. (2025). Enhancing Financial Sentiment Analysis: Integrating the Loughran-McDonald Dictionary with BERT for Advanced Market Predictive Insights. Procedia Computer Science. https://doi.org/10.1016/j.procs.2025.04.477
Meles, A., Pellegrino, L. R., & Rega, F. G. (2025). When Words Backfire: Tone Management and Crash Risk in Banking. Journal of Financial Management, Markets and Institutions. https://doi.org/10.1142/s2282717x25500069
<!-- rendered-citations:end -->
</content>
