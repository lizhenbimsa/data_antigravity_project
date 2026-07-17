---
family_id: F065
columns:
- avg_redund_han_log_length_ctx
- avg_redund_han_log_length_full
- avg_redund_han_log_length_ss
unit: 自然对数汉字数 (ln han chars, 无量纲对数标度)
formula: "avg_redund_han_log_length_<track> = 银行-年内对 content_<track> 各篇文章取 ln(该篇 CJK 汉字数) 后的等权均值 (mean-of-ln); 汉字数=is_cjk 计数, 剔数字/标点/拉丁"
producer: "news_process/pipeline/panel/encode.py (Stage 40 银行-年 mean-of-ln 聚合点: agg[f'avg_redund_han_log_length{track}'] = (f'redundancy_han_log_length{track}', 'mean')) ; news_process/pipeline/panel/export.py (面板落盘) ; news_process/pipeline/panel/codebook.py (码本元数据); 上游文章级汉字长度由 Stage 22 lexical_complexity 产出"
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - 22_tone_words.parquet (lexical_complexity 汉字口径长度与冗余中间列; 文章级 redundancy_han_log_length<track>)
  - pipeline/panel/encode.py (银行-年 mean 聚合 → avg_redund_han_log_length<track>)
  - 40_panel_yearly.parquet
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting — a comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: "826"
- doi: 10.1002/smj.3586
  type: journal
  authors: Miller, C. D., & Wang, R. D.
  year: 2024
  title: "Product digitization and differentiation strategy change: Evidence from the book publishing industry"
  venue: Strategic Management Journal
  vol: 45
  issue: 7
  pages_or_artno: 1241-1272
- doi: 10.1016/j.jcae.2023.100395
  type: journal
  authors: Yu, X., & Zhao, Y.
  year: 2024
  title: "Textual disclosure complexity and analysts' weighting of information"
  venue: Journal of Contemporary Accounting & Economics
  vol: 20
  issue: 1
  pages_or_artno: "100395"
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1002/j.1538-7305.1948.tb01338.x
  type: journal
  authors: Shannon, C. E.
  year: 1948
  title: "A mathematical theory of communication"
  venue: Bell System Technical Journal
  vol: 27
  issue: 3
  pages_or_artno: 379-423
- doi: "10.1111/lang.12630"
  type: "journal"
  authors: "Bestgen, Y."
  year: 2024
  title: "Measuring Lexical Diversity in Texts: The Twofold Length Problem"
  venue: "Language Learning"
  vol: "74"
  issue: "3"
  pages_or_artno: "638-671"
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的不是文本本身的语义或语气, 而是"篇内冗余"这一诊断量在回归中所必需的配对长度控制。上游诊断量 avg_within_doc_redund_han 以 1 减去唯一汉字 3-gram 占全部汉字 3-gram 的比例来刻画一篇报道在字符层面自我重复的程度: 一篇把同一套措辞反复摊开的报道, 其 3-gram 唯一率低、冗余值高。问题在于这一冗余量与文本长度之间存在机械耦合——文章越长, 汉字 3-gram 的总量越大、可复用的组合被重复触及的概率越高, 于是长文天然偏向更高的测得冗余, 即便作者并未刻意套话。信息论对这一耦合早有刻画: Shannon (1948) 把冗余定义为实际编码相对于同一符号表最大熵编码的差额, 而这一差额本身随消息长度而系统漂移, 长消息更易逼近符号统计的稳态、呈现更高的可压缩冗余。因此若把 avg_within_doc_redund_han 直接放进解释银行-年报道文本质量的回归, 未加长度控制的系数会把"报道更长"混同为"报道更套话", 造成构念污染。本家族三列正是为消解这一污染而设的成对协变量: 与所控冗余量严格同域、同汉字口径、同聚合层级, 使冗余系数在给定文本长度条件下被识别, 从而分离出"给定篇幅下的自重复倾向"这一净构念。

【方法学与计算】
计算分两级。文章级由 Stage 22 的 lexical_complexity 对每篇 content_<track> 先剔除数字、标点与拉丁字符、按 is_cjk 判据计出该篇的纯汉字数 n_han, 再取 ln(n_han) 作为该篇的对数汉字长度。银行-年级由 Stage 40 export 对同一银行同一年度内的全部在轨文章, 把这些文章级对数长度做等权算术平均, 即 mean-of-ln。这里的聚合次序刻意是"先取对数再求均值", 与 geography 模块里 ln_han_count / ln_word_count 采用的"先求均值再取对数"(ln-of-mean)在数学上不等价——由 Jensen 不等式, mean-of-ln 不大于 ln-of-mean, 二者之差随银行-年内篇幅离散度增大而扩张。本家族刻意选用 mean-of-ln 而非 ln-of-mean, 是因为所控冗余量 avg_within_doc_redund_han 本身也是"文章级先算比率、再跨篇求均值"的同型聚合; 唯有让长度控制与冗余量落在同一聚合域, 二者在回归中的机械对消才成立, 否则聚合次序错配会在长度控制里引入一个与冗余量不共享的非线性残差, 反而制造新的偏误。这也解释了本家族与 geography 长度列 (ln_han_count) 的刻意并存: 后者是描述性篇幅代理、走 ln-of-mean, 服务于长度本身的稳健性叙事; 前者是冗余回归的成对控制、走 mean-of-ln, 二者定义域不同、用途正交, 不可相互替代。取值域为 [0, +∞) 并集 NaN: 某银行-年在某轨下无任何在轨文章时该列为 NaN, 系分母缺失的诚实缺省而非零填充。汉字口径的采用 (剔数字/标点/拉丁) 与所控冗余量的汉字 3-gram 口径同源, 使分子分母同为汉字度量, 避免混入阿拉伯数字与拉丁缩写对长度的稀释, 这是中文文本落地相对英文原始做法的必要调整。

【文献定位】
本家族服务的冗余—复杂度研究谱系, 关注的是文本可读性、重复度与信息含量之间的张力。You & Zhang (2009) 指出财务披露的文本复杂度会削弱投资者对信息的即时吸收, 复杂度须与篇幅、可读性等机械维度分离方能识别其独立效应; Yu & Zhao (2024) 进一步显示披露文本复杂度直接影响分析师对信息的加权方式, 强化了对复杂度类测度做长度净化的必要性; Lesmy, Muchnik & Mugerman (2025) 以跨期比较证据刻画财务报告复杂度的系统性增长, 提示重复与冗长是可度量并需控制的文本特征。Shannon (1948) 为"冗余"这一构念提供了信息论根基, 说明本家族所控冗余量的 3-gram 唯一率视角与最大熵冗余的内在一致。在方法迁移层面, Miller & Wang (2024) 以文本差异化度量刻画企业战略随产品数字化的演变, 例示了基于文本的公司层面测度必须在篇幅、词表规模等机械协变量上做净化才能承载因果解读, 与本家族把长度作为冗余的成对控制的用意同构。综上, 本家族并非独立结果变量, 而是使冗余诊断量在给定篇幅条件下可被干净识别的方法学配件。 就长度依赖本身的性质, Bestgen (2024) 提供了直接的测度学依据: 该文基于三个英语学习者文本数据集系统检视常用词汇多样性指数, 提出『双重长度问题』——第一重是 type-token 比率类指数对文本长度的固有依赖; 第二重是即便以概率或算法方法把所有文本削减至等长从而消解第一重, 这些指数仍对『决定该等长长度的参数取值』高度敏感, 所检指数无一幸免。本家族所控的 avg_within_doc_redund_han 在数学上正是 1 减去一个 type-token 比率, 该文因而正面锚定了本家族存在的理由: 长度不是可选协变量, 而是须显式呈现、并与被控量事前同域固定的混淆因子, 否则冗余系数无法在给定篇幅条件下被识别。迁移边界须诚实交代: 该文分析的是字母语言的词级 type-token 关系、语料为学习者文本而非金融新闻, 与本项目的中文汉字 3-gram 阶在语言与 n-gram 阶数上均不同; 其讨论的等长削减类校正本项目并未实施, 本家族采用的 mean-of-ln 长度聚合亦非该文所提出——引用它是为披露长度依赖的存在, 而非主张本项目已消除该依赖。
## VAR: avg_redund_han_log_length_ctx

【变体差分】
本列为 ctx 轨变体, 文本载体为 content_ctx——标题 prepend 后拼接以目标银行等实体为中心的上下文窗口, 而非整篇正文。相对 full 轨, ctx 轨只保留实体邻近文本, 篇幅系统性偏短, 因此本列的对数汉字长度普遍低于同银行-年的 _full 值; 其角色是当冗余诊断量取 ctx 轨 (avg_within_doc_redund_han_ctx) 时的成对长度控制, 二者共享 ctx 轨的文本切分与银行-年 mean-of-ln 聚合口径, 只对进入 ctx 窗口的汉字计长。按项目全库口径, full/ctx/ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified 的 Hansen J; 相应地本列只与 ctx 轨冗余量成对入式, 不得与 full 或 ss 轨冗余量交叉配对, 否则长度控制与被控量落在不同文本域, 机械对消不再成立。留篇门控为 full-only (2026-06-29): 银行-年是否计入取决于 llm_verified_full, ctx 轨的行宇宙是 full 留篇集的子集, 本列在该子集上对 ctx 轨在轨文章按 mean-of-ln 逐轨计算, 分母不借用 full 轨篇数。ctx 窗口为空或该银行-年无 ctx 在轨文章时本列为 NaN。需要强调的是, ctx 轨的截断不是随机抽样而是围绕实体的目的性裁剪, 这使得 ctx 轨的对数长度分布相对 full 轨不仅整体左移、离散度也更小, 因而在回归里它承担的长度净化作用更贴近"实体邻近叙述的篇幅", 与 full 轨"整篇篇幅"是两个语义有别的控制维度; 把二者当作同一控制的替代品会低估轨间差异所携带的信息, 这正是三轨互为稳健性而非彼此冗余的原因。此外 ctx 轨在回退与非回退篇之间不做长度加权区分——每篇一律取自身 ctx 文本的对数汉字数、等权进入 mean-of-ln, 与所控 ctx 冗余量的等权聚合保持逐篇一一对应。

## VAR: avg_redund_han_log_length_full

【变体差分】
本列为 full 轨变体, 也是本家族的首要轨。文本载体为 content_full——标题 prepend 后拼接整篇正文, 覆盖最完整的篇幅信息。它是当冗余诊断量取 full 轨 (avg_within_doc_redund_han_full) 时的成对长度控制, 由于 full 轨保留全文, 本列在三轨中取值最高、也最贴近报道的真实篇幅规模。留篇门控 full-only 直接以本轨定义: 一篇是否算作"银行金科报道"只看 llm_verified_full, 因此 full 轨的银行-年行宇宙即留篇集本身, 本列的分母恰为该银行-年 full 轨在轨文章篇数, 无子集折扣。作为项目 full-only 口径下的主轨长度控制, 本列在主设定回归里与 full 轨冗余量成对进入, 是三列中最常被消费的一列。全库三轨铁律同样适用: full/ctx/ss 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J, 本列不得与 ctx 或 ss 轨冗余量跨轨配对。聚合口径为 mean-of-ln、汉字口径剔数字标点拉丁, 与家族 CORE 所述一致; 该银行-年无 full 轨在轨文章时取 NaN。相对 ctx 与 ss 两轨, full 轨保留完整正文使得篇幅的银行间与年份间变异最充分, 长度控制的解释力也最强, 因此在主设定里由本列承担冗余系数的净化任务、由 ctx/ss 两轨的对应列承担稳健性复算, 三者结论一致方可佐证冗余效应不因轨道选择而漂移。还须留意本列与 geography 模块 ln_han_count 的区别: 后者虽同为 full 轨汉字长度, 却走 ln-of-mean 聚合、用于描述篇幅本身, 与本列 mean-of-ln 的成对控制用途不可混用, 硬编码替换会在冗余回归里引入 Jensen 缺口残差。二者刻意并存、各司其职。

## VAR: avg_redund_han_log_length_ss

【变体差分】
本列为 ss 轨变体, 文本载体为 content_ss——标题 prepend 后拼接目标银行与金科词严格同句共现的句子及其 ±N 句窗口 (窗宽由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。ss 轨是三轨中语义最聚焦、篇幅通常最短的一轨, 因此本列取值一般在三轨中最低。其回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 优雅降级为整篇正文、ss_is_fallback 置真, 该篇的对数汉字长度即按全文汉字数计, 并与 ctx 共享 n_articles 分母口径; 因此在 T 较小的开发盘面上, ss 轨可能因大量回退而与 ctx 轨数值高度接近甚至退化, 属预期而非缺陷。本列是当冗余诊断量取 ss 轨时的成对长度控制, 只对进入 ss 文本域 (含回退后的全文) 的汉字计长, 与 ss 轨冗余量共享文本切分与 mean-of-ln 聚合。三轨铁律照旧: ss 与 full/ctx 各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J, 本列仅与 ss 轨冗余量成对配对。留篇门控仍为 full-only: ss 轨行宇宙是 full 留篇集的子集, 逐轨计列、分母不借 full 轨; 该银行-年无 ss 在轨文章时取 NaN。由于 ss 轨在无同句共现时整篇回退, 本列的分布在回退占比高的样本里会向 full 轨靠拢、在共现密集的样本里则显著短于其余两轨, 这一双峰倾向本身携带信息: 它反映了银行金科叙述在报道中是散点提及还是集中成段。因此把本列作为 ss 轨冗余量的成对控制时, 它净化的是"聚焦叙述的篇幅"而非"整篇篇幅", 与 full 轨的控制维度正交。生产语料 T 较大时回退比例下降、ss 轨的独立信息含量上升, 三轨长度控制的差异会更充分地展开, 这也是保留 ss 轨而非仅用 full 轨长度控制的意义所在。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting — a comparative study. Humanities and Social Sciences Communications, 12, 826. https://doi.org/10.1057/s41599-025-06094-y
Miller, C. D., & Wang, R. D. (2024). Product digitization and differentiation strategy change: Evidence from the book publishing industry. Strategic Management Journal, 45(7), 1241-1272. https://doi.org/10.1002/smj.3586
Yu, X., & Zhao, Y. (2024). Textual disclosure complexity and analysts' weighting of information. Journal of Contemporary Accounting & Economics, 20(1), 100395. https://doi.org/10.1016/j.jcae.2023.100395
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Shannon, C. E. (1948). A mathematical theory of communication. Bell System Technical Journal, 27(3), 379-423. https://doi.org/10.1002/j.1538-7305.1948.tb01338.x
Bestgen, Y. (2024). Measuring Lexical Diversity in Texts: The Twofold Length Problem. Language Learning, 74(3), 638-671. https://doi.org/10.1111/lang.12630
<!-- rendered-citations:end -->
