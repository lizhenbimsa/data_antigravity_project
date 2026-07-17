---
family_id: F443
columns:
- msent_sum_ctx
- msent_sum_full
- msent_sum_ss
unit: 无量纲计数得分 (银行-年内逐篇 msent_score 求和, 非比率非均值)
formula: 'msent_score{track}_i = (raw_neg{track}_i − raw_pos{track}_i) / (raw_pos{track}_i + raw_neg{track}_i), 基于 6 词典固定 union 词表的原始极性计数 (base 字段, 零语言学规则), 分子分母同为词典命中计数、非幅度; 数值越大代表负面词占优 (越正=越负面, 与直觉相反), 值域约 (-1,+1); msent_sum{track} = Σ_i msent_score{track}_i, 对属于同一银行-年 bank-year 单元的全部有效文章 i 求和 (agg 使用 pandas groupby.sum, 缺失值随 sum 语义自动跳过而非以 0 记)'
producer: "pipeline/panel/encode.py (agg[f'msent_sum{track}'] = (f'msent_score{track}', 'sum')) ; pipeline/panel/codebook.py (元数据发射 + v3.10.0 六词典披露 _DICT6_AFFECTED_RE 命中)"
upstream:
- "pipeline/sentiment/tone_words.py (article 级 msent_score{track} 生成)"
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: "Pröllochs, N., Feuerriegel, S., & Neumann, D."
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
- doi: "10.1016/j.chieco.2025.102541"
  type: "journal"
  authors: "Wei, L., Wei, M., Wu, Y., & Jing, Z."
  year: 2025
  title: "Does party organization construction improve chinese banks' stability? Evidence from a new textual index"
  venue: "China Economic Review"
  vol: "94"
  pages_or_artno: "102541"
- doi: "10.1016/j.jbankfin.2025.107501"
  type: "journal"
  authors: "Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N."
  year: 2025
  title: "Newswire tone-overlay commodity portfolios"
  venue: "Journal of Banking & Finance"
  vol: "178"
  pages_or_artno: "107501"
new_dois: []
---

## CORE

【构念与来源】
msent_sum 是计数型情感测度 MSENT 在银行-年面板上的加总口径, 家族含三条并排轨道 msent_sum_full / msent_sum_ctx / msent_sum_ss。MSENT 承袭 Tetlock (2007, Journal of Finance) 开创的"媒体情绪内容"传统: 对每篇报道逐词命中词典正/负极性词表, 得到该篇的净极性计数分 msent_score = (负面命中计数 − 正面命中计数) / (正面命中计数 + 负面命中计数), 是把词典命中计数归一化到约 (-1, +1) 区间的比例差分, 而非未归一化的原始计数差; 数值越大代表负面词占优、越偏负面 (与直觉相反的符号方向须特别留意), 未做否定翻转/程度副词/转折等语言学规则修正 (零规则口径), 与同族 avg_msent 的"篇均"口径互补。再在 bank-year 层面对同一银行同一年份的全部有效文章按 sum 聚合, 得到本家族的 msent_sum。与家族内已有的 avg_msent(均值) / avg_msent_std(标准差) 三兄弟并列, msent_sum 反映的是"总量"信息而非"平均强度"信息: 在文章篇数 n_articles 不受控的比较场景下 (例如跨银行、跨年份原始篇幅差异悬殊时), msent_sum 会同时混入"该行当年被报道的密集度"与"每篇报道的净极性水平", 因此在解释力上更接近媒体关注度与情绪方向联合驱动的合成量, 而非纯粹的情绪水平度量; 使用者若只关心情绪水平应优先看 avg_msent, 若关心情绪的"总暴露量"或作为 n_articles 的加权变体则用 msent_sum。

【方法学与计算】
msent_score 的生成发生在 tone_words.py 的词典法情感引擎内, 是 6 部词典体系 (v3.10.0 由 5 部扩为 6 部) 中专属 MSENT 计数口径的产物, 与 avg_pos_ratio/avg_neg_ratio 等"比率口径"并非同一分子分母结构 —— MSENT 分子是正负命中计数之差, 分母是正负命中计数之和 (自归一化的净极性比例), 比率口径的分母则是全体 word-token 总数。encode.py 在批量聚合阶段对三条文本轨道 (_full/_ctx/_ss) 各自独立调用 groupby(...).sum(), 因此 msent_sum_full / msent_sum_ctx / msent_sum_ss 三列共享同一生成算子与同一词典基, 差异只在于上游喂入的文本窗口不同。三轨彼此是互为稳健性、不分主次的并排测度, 各自 just-identified, 严禁在同一 over-identified Hansen J 检验中把三轨系数混进同一超识别方程; 三者应作为三条独立稳健性证据链分别汇报, 而不是相加或取平均后合并使用。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇报道是否被计入"该银行当年一篇有效金科报道"的判定只看 full 轨的 llm_verified_full 标记, ctx/ss 两轨的行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 因此 msent_sum_ctx / msent_sum_ss 的样本篇数分母与 msent_sum_full 完全一致, 不会因为 ctx/ss 轨自身的文本可得性而扩大或缩小分母。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在"目标银行与金科词同句共现"窗口时, content_ss 退化为全文正文 (与 content_ctx 的实体窗口缺失退化逻辑对称), 对应 ss_is_fallback 标记为真, 此时该篇纳入 msent_score_ss 计算所用的文本实质上等同于全文, 但仍与 full 轨的原始未截断正文存在提示词拼接差异, 不可视为完全等价替代。

【文献定位】
本家族在方法学谱系上直接对接 Tetlock (2007, Journal of Finance) 开创的媒体情绪净极性计数传统: 以固定词表对逐篇报道做正/负词命中计数, 用命中计数之差除以命中计数之和构造篇级净极性分数, 该"净负面占比"式构造是本家族 msent_score/msent_sum 计数口径的直接理论与方法学来源。msent_sum 在 bank-year 层面对篇级 msent_score 求和, 因此同时承载"报道密度"与"净极性方向"两重信息, 与 avg_msent 的纯篇均口径形成互补的总量-强度分解。v3.10.0 六词典扩张披露 (词表由 5 部扩为 6 部, Pearson r(5,6)=0.985, 符号翻转 0.13%, 均值微变约 3.5%) 对本家族三列均适用, 数值层面的历史可比性因此存在一次已披露的、方向明确的测度口径调整, 属词表覆盖改善而非方法误差, 用户在做跨版本比较时应留意这一断点。词典法本身的方法学根基另有 Loughran & McDonald (2011, Journal of Finance) 的支撑: 该文论证通用情感词典迁移到金融文本会系统性误分类, 主张构造金融专用词表并以简单词频计数 (而非复杂加权) 度量语气, 是本项目六部中文金融词典并集构造与固定计数口径 (msent_score 分子分母均为词典命中计数、非幅度加权) 的直接方法学正当性来源。逐篇计数在遇到否定词时的翻转处理则参照 Pröllochs, Feuerriegel & Neumann (2016, Decision Support Systems) 对否定作用域检测在新闻驱动情感度量中价值的系统研究, 支撑本项目在 msent 计数管线里显式引入否定翻转规则的做法。 就「中文文本 → 银行层面指数 → 银行面板回归」这一整体链路, Wei、Wei、Wu 与 Jing (2025) 构造新的中文文本指数度量中国银行的党组织建设, 并将其接入银行层面面板检验其对银行稳定性的影响, 为本家族所处的应用同域 (中国银行 × 中文文本计量) 提供近期范例。举证限度须诚实标注: 该文的文本源与指数构造口径未经核实 (极可能为银行自身披露文件的主题或关键词计数), 并非六部中文金融词典并集的净极性计数在银行-年层面求和, 其银行稳定性为结果变量, 亦不涉及三轨文本范围与本仓的多层加权口径。就「逐篇语调按标的求和聚合为单元级语调量」这一聚合步骤本身, Fernandez-Perez、Fuertes、Miffre 与 Zhao (2025) 以新闻通讯社 (newswire) 语调叠加构造商品组合信号, 为该求和聚合口径提供近期存在性; 其迁移边界同样须写明: 该判断系据题名保守认定, 原文语料为英文 newswire, 聚合层级为商品-期而非银行-年三轨, 既无 IDF、媒体权威或羊群衰减加权层, 亦不涉及中文六词典并集与本家族的固定命中计数口径。
## VAR: msent_sum_ctx

【变体差分】
msent_sum_ctx 是三轨中的实体窗口 (context) 轨道, 上游文本来自 stage 14 物化的 content_ctx (标题 + 目标银行实体窗口), 而非全文正文。相较 msent_sum_full, 本列把逐篇 msent_score 的计算范围从整篇报道收窄到围绕目标银行实体的局部窗口, 因此更贴近"报道中直接涉及该银行的段落所携带的情绪总量", 能部分过滤掉与该银行无关的背景叙述、其他机构新闻、行业综述等噪声文本对情绪计数的稀释或污染。当某篇文章不存在可提取的实体窗口 (即银行实体在文中缺乏有效上下文片段) 时, content_ctx 依照既定回退语义退化为全文 body, 对应的 ctx_is_fallback 标记为真, 此时该篇对 msent_sum_ctx 的贡献实质上与 msent_sum_full 一致, 但两列在非回退篇目上的差异恰恰是该差分维度的信息量所在。msent_sum_ctx 与 msent_sum_full、msent_sum_ss 三者共享同一 sum 聚合算子与同一 6 部词典基, 三者互为稳健性并排测度, 不设主次, 亦不应合并进同一超识别方程联合估计。由于窗口收窄通常意味着纳入计数的词元总数低于全文轨, 在文章级极性绝对值本就有限的情况下, msent_sum_ctx 的量级预期整体小于或接近 msent_sum_full, 但方向(正负符号趋势)在多数样本上应保持较高一致性, 二者之间的系统性偏离本身即是可用于稳健性诊断的信息。留篇门控采用 full-only 口径, 本列的样本行宇宙是 full 轨留篇集合的子集, 不因 ctx 文本本身可得性扩大分母。

## VAR: msent_sum_full

【变体差分】
msent_sum_full 是本家族的全文轨道, 也是三轨中样本行宇宙的锚点: stage 21 留篇门控只看 full 轨的 llm_verified_full 判定是否为"一篇有效的银行金科报道", ctx / ss 两轨均是该留篇集合上的条件测度 (conditional-on-full), 分母与本列完全对齐。上游文本是 stage 14 物化的 content_full, 即标题 prepend 后的完整正文, 不做实体窗口或同句共现裁剪, 因此逐篇 msent_score_full 纳入的候选词元数量最多、覆盖面最广, 是三轨中信息量最完整、但同时也最容易掺入与目标银行弱相关背景叙述的版本。msent_sum_full 相对同族 avg_msent_full 是计数总量而非篇均强度, 二者搭配使用可以分解出"篇数效应"与"强度效应": 若某银行-年 msent_sum_full 上升而 avg_msent_full 持平, 则更可能是报道篇数增加驱动而非单篇情绪强化驱动。作为三轨并排测度之一, msent_sum_full 与 msent_sum_ctx、msent_sum_ss 之间应各自独立汇报回归系数、各自 just-identified, 不得混入同一 over-identified Hansen J 联合检验, 也不建议对三轨取加权平均后作为单一"最优"合成指标使用, 因为窗口选择本身承载着不同的构念侧重 (全篇叙事 vs 局部实体语境 vs 严格同句共现), 合并会抹去这一差异化信息。v3.10.0 六词典披露对本列同样适用, 数值存在一次已知方向的历史微调。

## VAR: msent_sum_ss

【变体差分】
msent_sum_ss 是三轨中判据最严格的同句共现 (same-sentence) 轨道, 上游文本 content_ss 只保留标题与"目标银行∧金科词在同一句子内共现" (窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认前后各 1 句) 的片段, 是全文轨到实体窗口轨之后进一步收紧的精炼版本, 用于捕捉"银行与金融科技话题被直接并置讨论"的最强证据情形。若某篇文章不存在银行∧金科同句共现片段, content_ss 依 CLAUDE.md 明确的回退语义退化为全文 body, ss_is_fallback 标记为真, 此时该篇对 msent_sum_ss 的贡献与 msent_sum_full 一致, 与 ctx 轨的回退逻辑对称(镜像 ctx, 而非独立设计的另一套规则)。由于同句共现判据比实体窗口更严苛, 非回退篇目的候选文本量通常是三轨中最小的, msent_sum_ss 因此往往是三者中量级最小、但对"银行-金科强关联叙事情绪"最具针对性的一列, 适合用作 msent_sum_full 主结果的收紧稳健性检验, 用以排除弱相关背景报道对情绪计数总量的稀释。留篇门控同样是 full-only, 本列样本行宇宙不因 ss 判据本身的可得性而独立扩缩。msent_sum_ss 与另外两轨各自 just-identified 并排, 互为稳健性不分主次, 三者严禁混入同一超识别 Hansen J 方程联合估计; v3.10.0 六词典扩张的历史数值披露同样适用于本列。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Wei, L., Wei, M., Wu, Y., & Jing, Z. (2025). Does party organization construction improve chinese banks' stability? Evidence from a new textual index. China Economic Review, 94, 102541. https://doi.org/10.1016/j.chieco.2025.102541
Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N. (2025). Newswire tone-overlay commodity portfolios. Journal of Banking & Finance, 178, 107501. https://doi.org/10.1016/j.jbankfin.2025.107501
<!-- rendered-citations:end -->
