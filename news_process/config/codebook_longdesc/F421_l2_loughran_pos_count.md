---
family_id: F421
columns:
- loughran_pos_count_ctx
- loughran_pos_count_full
- loughran_pos_count_ss
unit: 篇数/计数 (count)
formula: loughran_pos_count_{track} = 文章文本 (content_{track}, prepend_title) 中命中 loughran_mcdonald_zh_2026 词典 positive 类词条的原始命中次数逐篇计数; positive/negative 跨类重叠 23 词按用户决策"两侧保留"同时计入两侧计数 (非last-writer-wins单极判负)
producer: pipeline\sentiment\tone_words.py ; pipeline\panel\export.py
upstream: []
citations:
- {doi: "10.1111/j.1540-6261.2010.01625.x", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2011, title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks", venue: "The Journal of Finance", vol: "66", issue: "1", pages_or_artno: "35-65"}
- {doi: "10.1111/1475-679X.12123", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2016, title: "Textual analysis in accounting and finance: A survey", venue: "Journal of Accounting Research", vol: "54", issue: "4", pages_or_artno: "1187-1230"}
- {doi: "10.2139/ssrn.3446388", type: wp, authors: "Bian, S., Jia, D., Li, F., & Yan, Z.", year: 2021, title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance", venue: "SSRN Working Paper"}
- {doi: "10.1002/isaf.1549", type: journal, authors: "Todd, A., Bowden, J., & Moshfeghi, Y.", year: 2024, title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions", venue: "Intelligent Systems in Accounting, Finance and Management", vol: "31", issue: "1", pages_or_artno: "e1549"}
- {doi: "10.1016/j.eswa.2024.125739", type: journal, authors: "Ma, Y., Zhang, T., & Zhang, P.", year: 2025, title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application", venue: "Expert Systems with Applications", vol: "264", pages_or_artno: "125739"}
- {doi: "10.1016/j.iref.2024.01.067", type: journal, authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.", year: 2024, title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China", venue: "International Review of Economics & Finance", vol: "91", pages_or_artno: "1150-1172"}
new_dois: []
---

## CORE

【构念与来源】
loughran_pos_count 家族记录每篇新闻文本中命中 loughran_mcdonald_zh_2026 词典 positive 类词条的原始次数, 是该词典六族测度体系中最基础的一层——未做任何长度归一或极性合成的裸计数。loughran_mcdonald_zh_2026 是 Loughran & McDonald (2011) 面向美股 10-K 文本构建的英文金融情感词典 (positive/negative 两极外另含 uncertainty/litigious/constraining/weak modal 等五类非极性词类) 的中文主译本, 由 config/tone_dicts.json 统一维护, 在项目内以列前缀别名 loughran 出现, 与 jiang_2021/yao_2021/bian_2021/du_2022/you_2018 并列构成六词典体系中的第六员。中文译本中 positive 词条 1,295 个、negative 词条 3,729 个; 与其余五部词典一样, positive/negative 两类之间存在跨类重叠——loughran 原始重叠 61 词经 2026-06-24「两侧保留判断」逐词消歧, 其中 38 词已归入单侧词表, 余下 23 词因语义确实兼具两极而不可约简, 按项目统一决策保留在两侧同时计数。这一处理取代了历史上 fix omni-g-tonewords-03/-07 采用的"双侧剔除"(遵循 LM 2011 JF 论文惯例) 以及更早的隐式 last-writer-wins 单极判负实现: 现行口径下, 重叠词在该词典个体的 pos_count/neg_count 中都会被计入一次, 使得词典个体层面的净语调被这些多义词拉向中性而非武断选边, 词条覆盖数因此等于原始并集 |pos∪neg|, 不再小于词典说明书标称值。loughran_pos_count 正是这一计数口径下的产物: 它统计的不是"篇内是否出现正面语调", 而是命中的绝对次数, 数值随文本长度自然增长, 因此是一个尺度依存 (scale-dependent) 的原始计数变量, 与同族的比率型/得分型测度 (如 pos_ratio、msent_score) 在解释上互补而非替代。

【方法学与计算】
计算发生在 pipeline/sentiment/tone_words.py (原 root script 22_tone_words.py 迁入), 对每篇文章的三条并行文本轨道逐轨扫描: full 轨 = 标题 + 全文正文 (prepend_title 拼接); ctx 轨 = 标题 + 目标银行实体窗口摘录; ss 轨 = 标题 + 银行∧金科同句 (±N 句窗, 默认 N=1, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制) 摘录, 三轨文本列 (content_full/content_ctx/content_ss 及各自 *_is_fallback 指示列) 由上游 stage 14 ctx_materializer 物化 (stage 13 只做共现硬过滤、不物化文本)。ss 轨回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科的同句共现, 则 content_ss 退化为等同全文 body, 并将 ss_is_fallback 置 True, 分母 n_articles 与 ctx 轨共享同一计算口径; 若上游 FINTECH_AC 词典缺失 (None), 则 *_is_fallback 全体置 True 作为优雅降级, 而非静默产出空值。分词采用固定版本 jieba==0.42.1 (冻结锚点之一, 保证跨次运行的确定性重放), 对分词结果逐词与 loughran positive 词表做精确匹配, 命中一次计数加一, 不做词频截断也不做 TF-IDF 加权——这是与同族 loughran_score/loughran_msent 等合成测度的关键区别: pos_count 是最原始的输入层, 后续的比率化 (除以总词数)、符号化 (pos−neg 判正负) 均建立在这个计数之上, 但 pos_count 本身不做任何归一或组合运算。词典消歧后的重叠词处理规则 (23 个不可约简重叠词两侧计入) 直接体现在 pos_count 的分子里: 若一篇文章命中的词恰好落在重叠集合中, 该次命中会同时被 loughran_pos_count 与 loughran_neg_count 计入, 而不会因先验极性判定被单边吞没。三轨各自独立完成分词、匹配、计数全流程, 互不借用彼此的中间结果或分母, 这与网络三轨、BERT 分布形状族等其余"三轨并排"测度遵循同一工程范式。

【文献定位】
loughran_pos_count 所依托的 Loughran-McDonald 词典源自会计与金融文本分析领域的奠基性工作。Loughran & McDonald (2011, Journal of Finance) 在"When is a liability not a liability?"一文中系统检验了此前财经文本研究广泛借用的哈佛心理社会学词典 (Harvard Psychosociological Dictionary, 一般语域构建) 在 10-K 文本上的适用性, 发现大量被该通用词典标记为"负面"的词汇 (如 tax、cost、liability 等会计术语) 在财报语境中实为中性乃至正面, 由此提出针对金融/会计文本量身定制的领域专属词典, 这正是当前项目采用中文本土化词典族 (而非直接套用通用情感词典或简单机器翻译哈佛词典) 的方法学出发点。Loughran & McDonald (2016, Journal of Accounting Research) 进一步以综述形式系统梳理文本分析在会计与金融研究中的应用范式, 明确了词典法作为可复现、可审计基线测度的地位, 并讨论了词频计数与比率化测度各自的适用场景——这为本家族"保留裸计数作为独立测度层、不与比率型测度相互替代"的设计提供了直接的方法学支持。中文语境下, Bian, Jia, Li & Yan (2021) 在 LM 词典基础上本土化扩充构建了另一部中文金融情感词典 (即六词典体系中的 bian_2021), 与 loughran 中文主译本共同构成"词典移植路径"(逐词翻译扩充) 一支, 与姜富伟等 (2021)、姚加权等 (2021) 代表的"本土原生构建路径"形成方法学对照, 二者并列使用本身即是项目六词典固定 union 体系设计所体现的稳健性考量。近年综述 Todd, Bowden & Moshfeghi (2024) 系统梳理了金融文本情感分析的技术演进脉络, 印证词典法在深度学习时代仍是不可或缺的透明基线; Ma, Zhang & Zhang (2025) 针对中国投资者构建细粒度中文情感词典 (CN-FSD) 的近期工作, 说明中文金融文本情感词典构建仍是活跃的方法学前沿, 项目采用的六词典固定 union 体系正是在这一持续演进的方法生态中做出的多源稳健性设计。应用层面, Fang, Wang, Wang & Yuan (2024) 在中国银行系统性风险研究中使用媒体情感测度作为银行层面舆情暴露的代理变量, 与本项目"银行-金科"新闻情感面板的应用场景高度同域, 印证了词典法计数测度在中国银行业新闻文本研究中的实证适用性。

## VAR: loughran_pos_count_ctx

【变体差分】
本列是 loughran_pos_count 家族的 ctx (context) 轨变体, 扫描文本为 content_ctx——标题与目标银行实体窗口摘录的拼接, 而非全文正文。相较 full 轨, ctx 轨天然聚焦于银行实体周边语境, 文本长度通常显著短于全文, 因此 loughran_pos_count_ctx 的绝对数值分布整体低于 loughran_pos_count_full, 这是文本窗口收窄的直接机械后果, 不应被解读为"语调更正面/更负面"的实质性差异; 正确的跨轨比较应控制文本长度或改用同族比率型测度 (如 loughran_pos_ratio_ctx)。若某篇文章不存在有效的银行实体窗口摘录 (ctx_is_fallback=True), content_ctx 按上游 stage 14 的既定回退规则处理, pos_count_ctx 的计算逻辑本身不因回退状态改变——分词与词表匹配流程与非回退情形完全一致, 仅摘录内容来源不同。需要强调的是, 三轨 (full/ctx/ss) 在计量经济学意义上各自 just-identified 并排, 互为稳健性、不分主次, 三者绝不可混入同一个 over-identified Hansen J 检验的工具变量集合中联合使用; ctx 轨与 full 轨的差异应被理解为"聚焦范围不同的平行测度", 而非"主测度与稳健性检验"的层级关系。此外, 项目 2026-06-29 起的留篇门控 (是否判定一篇报道为"银行-金科"报道) 严格以 llm_verified_full 为准, ctx 轨的行宇宙是 full 轨留篇集合的子集, 即 loughran_pos_count_ctx 只在 full 轨已确认留篇的文章范围内计算, 属于 conditional-on-full 的测度轨道, 这与该家族三轨"并排稳健"的定位并不矛盾——留篇判定与计数测度是两个独立的判据层。

## VAR: loughran_pos_count_full

【变体差分】
本列是 loughran_pos_count 家族的 full 轨变体, 也是三轨中承担留篇门控职责的基准文本轨: 扫描文本为 content_full, 即标题与文章全文正文的拼接 (prepend_title), 不做实体窗口裁剪或同句共现限定。按项目 2026-06-29 起确立的 full-only 留篇门控口径, 一篇报道是否被认定为有效的"银行-金科"报道, 唯一依据是 llm_verified_full 是否为 True, 这一判定发生在 stage 21 情感 LLM 环节, 与 loughran_pos_count 所在的 stage 22 词典打分是并行独立的两套测度体系 (词典法与 LLM 法互不依赖对方的中间结果, 仅共享同一批经 stage 13/14 处理过的三轨文本)。因此 loughran_pos_count_full 覆盖的文章行宇宙即为该银行-年份下全部满足留篇门控的报道全集, ctx 轨与 ss 轨的行宇宙都是这一全集的子集。在计数口径上, full 轨文本长度最长, 覆盖信息最全, 通常给出该家族三轨中数值最大且方差最稳定的绝对命中数, 常被用作后续比率化/聚合测度 (如面板层 loughran_pos_frac、msent_score 等) 的默认参照轨, 但这并不意味着 full 轨在识别策略意义上优于 ctx/ss 轨——三者仍应作为互为稳健性、各自 just-identified 的并排测度对待, 禁止在同一 over-identified 设定中联合使用。分词与匹配环节固定使用 jieba==0.42.1 冻结版本, 与 ctx/ss 两轨完全一致, 三轨之间的唯一差异来源是喂入的文本内容 (窗口范围), 而非分词器版本或词表口径的差异, 这保证了三轨绝对数值的可比性建立在同一测量工具之上, 差异纯粹反映文本窗口收窄或放宽的效应。

## VAR: loughran_pos_count_ss

【变体差分】
本列是 loughran_pos_count 家族的 ss (same-sentence) 轨变体, 扫描文本为 content_ss——标题与"目标银行∧金科关键词同句共现"摘录 (±N 句窗, 默认 N=1) 的拼接, 是三轨中判据最严格、文本粒度最细的一支, 与判定银行∧银行结构指标所用的"同篇/±1句窗/严格同句"三判据体系是两套不同的口径 (后者用于网络自相关测度, 不可混淆)。ss 轨的回退语义严格镜像 ctx 轨: 当某篇文章不存在银行与金科关键词的同句共现时, content_ss 退化为等同全文 body, 对应的 ss_is_fallback 置 True, 且与 ctx 轨共享同一个 n_articles 分母口径; 若上游金科词典 FINTECH_AC 为 None (词典缺失), 则 *_is_fallback 全体置 True, 作为优雅降级而非产出空值或报错。由于同句共现窗口通常比实体窗口 (ctx) 更窄, loughran_pos_count_ss 的绝对命中数往往是三轨中最低且零值占比最高的一支, 在小样本或短文本 (如快讯类报道) 上容易出现大量零计数, 这是判据粒度收窄的机械结果, 解读时须结合 ss_is_fallback 指示列排除回退样本的干扰, 不宜直接与 full/ctx 轨的绝对数值做无条件比较。与 ctx 轨一致, ss 轨同样是 full-only 留篇门控下 conditional-on-full 的行宇宙子集, 且在识别策略上与 full、ctx 两轨构成互为稳健性、各自 just-identified 的并排关系, 禁止混入同一 over-identified Hansen J 设定。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
