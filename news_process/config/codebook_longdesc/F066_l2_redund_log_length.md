---
family_id: F066
columns:
- avg_redund_log_length_ctx
- avg_redund_log_length_full
- avg_redund_log_length_ss
unit: ln(去空白字符数) 的银行-年均值 (对数字符长度, 无独立量纲)
formula: "article: log_length = ln(去空白字符数); panel: avg_redund_log_length_{track} = mean_over_articles( log_length_{track} )  (mean-of-ln, 逐轨聚合)"
producer: news_process/pipeline/panel/codebook.py ; news_process/pipeline/panel/export.py (Stage 22 lexical_complexity + Stage 40)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet
citations:
- doi: 10.1093/qje/qjad054
  type: journal
  authors: Chen, J., & Roth, J.
  year: 2024
  title: "Logs with zeros? Some problems and solutions"
  venue: Quarterly Journal of Economics
  vol: 139
  issue: 2
  pages_or_artno: 891-936
- doi: 10.1037/a0033242
  type: journal
  authors: Simonsohn, U., Nelson, L. D., & Simmons, J. P.
  year: 2014
  title: "P-curve: A key to the file-drawer"
  venue: "Journal of Experimental Psychology: General"
  vol: 143
  issue: 2
  pages_or_artno: 534-547
- doi: 10.1037/h0046016
  type: journal
  authors: Campbell, D. T., & Fiske, D. W.
  year: 1959
  title: "Convergent and discriminant validation by the multitrait-multimethod matrix"
  venue: Psychological Bulletin
  vol: 56
  issue: 2
  pages_or_artno: 81-105
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
本家族三列 avg_redund_log_length_{full,ctx,ss} 是"篇内冗余度配对长度控制"(redundancy paired ln-length control): 它不是一个独立的可读性或信息量测度, 而是专门为回归中的 within-document redundancy 测度 (avg_within_doc_redund 家族) 量身配备的长度协变量。构念动机是一个已被文本会计学反复记录的机械事实: 一篇文本越长, 其字符 n-gram 的重复概率越高, 因此"篇内自重复率"与"篇幅"之间存在结构性正相关。若在回归中只放入冗余度而不控制长度, 冗余度系数会混入纯粹由篇幅驱动的伪变异。为此我们构造一个与冗余度定义域严格对齐的长度控制, 使研究者能在同一定义域内净化掉长度的机械成分, 只保留"给定长度下, 文本自我重复到何种程度"这一真正的构念变异。

【方法学与计算】
文章级原语为 log_length = ln(去空白字符数), 即先剔除文章中的空白符再取字符总数, 随后取自然对数。银行-年聚合采用 mean-of-ln 口径: 对该银行该年度落入留篇集的每篇报道各自计算 ln 长度, 再取算术平均, 得到 avg_redund_log_length_{track}。这一聚合顺序是刻意选择且承重的: 它与 geography 家族的 ln-of-mean 口径 (ln_word_count = ln(1 + avg_word_count) / ln_han_count) 数学上不等价——由 Jensen 不等式, 先取对数再平均严格不大于先平均再取对数, 两者相差一个与篇长离散度相关的凸性缺口。项目刻意让两套口径并存: mean-of-ln 用作冗余度回归的配对控制 (因为冗余度本身是逐篇计算再平均的篇级测度, 其长度混杂也发生在篇级, 故长度控制须同为篇级 mean-of-ln, 才能与被控制变量同域); ln-of-mean 则服务于把"典型篇幅"当作年度水平特征的地理面板。对数变换本身的取舍——尤其是零值与小值处理、以及对数点弹性解释在存在大量零或极端偏态时的失真——是 Chen & Roth (2024) 系统讨论的问题; 本列因作用于去空白字符数 (对留篇报道恒为正、无零值病态), 规避了其记录的零值陷阱, 但仍继承其关于"对数尺度下均值不可随意互换"的告诫, 这正是本项目坚持 mean-of-ln 与 ln-of-mean 分列不混用的直接依据。计算落地在 Stage 22 (lexical_complexity) 产出篇级长度、Stage 40 面板导出层完成逐轨 bank-year 聚合; codebook 单位登记为 ln(chars), 值域 [0, +∞) ∪ NaN, 与其所控制的 avg_within_doc_redund 同定义域配对。

【文献定位】
方法学上, 本控制列服务于两条文献脉络的交汇。其一是文本计量中的"篇幅混杂"传统: 冗余、样板化、可读性等篇级文本属性普遍与文档长度机械相关, 若不配对控制长度, 相应系数不可解释为构念效应而是长度的影子。其二是稳健性与规格透明度传统: 一个测度是否稳健, 取决于它在纳入合理协变量后是否仍存活, 配对长度控制正是把"冗余效应"与"长度效应"分离的最小必要规格。Simonsohn, Nelson & Simmons (2014) 提出的 p-curve 方法, 从一组研究结果的 p 值分布形状即可诊断该结论是否掺入 p-hacking 与文件抽屉式的选择性报告: 若一批系数依赖事后的规格搜寻而非真实效应, 其显著性的分布会留下可被检出的畸变。这一诊断逻辑对配对控制的启示是直接的——一个冗余度系数若靠事后择取长度变量 (例如临时挑一支能压出想要的冗余度显著性的长度协变量) 才成立, 恰属该文所警示的规格搜寻情形; 唯有以预先声明、与被控变量严格同域的方式固定长度控制, 才能杜绝这一自由度。本列的定义域对齐与 mean-of-ln 口径的事前固定, 正是对这一告诫的制度化回应。构念判别上, Campbell & Fiske (1959) 的多质多法框架提供了恰当的检验逻辑: 冗余度与长度是两个不同的"质"(trait), 二者虽机械相关但不应被视为同一构念——配对长度控制的作用, 正是在回归里把这两个质从混杂中解耦, 使冗余度得以作为收敛-判别意义上独立的构念被估计。需要强调, 本家族三列彼此是三轨 (full/ctx/ss) 稳健性变体: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 它们服务于同一个"冗余度回归需要长度控制"的目的, 只是分别匹配 full/ctx/ss 三条文本轨上各自计算的冗余度, 从而保证长度控制与被控冗余度逐轨同源。 把长度与冗余解耦这一前提, 在测度学层面另有直接支撑: Bestgen (2024) 基于三个英语学习者文本数据集系统检视常用词汇多样性指数, 提出『双重长度问题』——第一重是 type-token 比率类指数对文本长度的固有依赖; 第二重是即便把所有文本以概率或算法方法削减至等长从而消解第一重, 指数仍对决定该等长长度的参数取值高度敏感, 所检指数无一幸免。本列所配对的 avg_within_doc_redund 在数学上即 1 减去一个 n-gram type-token 比率, 故该文正面锚定了冗余度系数须在给定长度条件下方可识别这一前提, 也印证了长度控制必须与被控量事前同域固定、而非事后择取的规格纪律。迁移边界须明示: 该文是字母语言词级、学习者语料上的方法学分析, 未涉及金融新闻文本, 亦未涉及本项目的字符级 n-gram 口径与 mean-of-ln 聚合口径; 其提出的等长削减类校正本项目并未实施——引用意在披露长度依赖仍然存在, 而非声称其已被校正掉。
## VAR: avg_redund_log_length_ctx

【变体差分】
本列是配对长度控制的 ctx 轨变体, 对应 content_ctx 文本轨: 该轨文本为标题 prepend 后拼接实体上下文窗口 (标题与目标银行邻近的实体上下文片段), 而非全文正文。因此本列度量的是 ctx 轨报道在去空白后的字符长度取对数、再作 bank-year mean-of-ln 的结果, 其唯一职责是在以 avg_within_doc_redund_ctx 为解释变量的回归中充当逐轨同源的配对长度控制。与 full 轨相比, ctx 文本经实体窗口裁剪, 篇幅系统性更短且更集中于银行相关段落, 故本列水平通常低于同银行-年的 full 轨值; 这一系统性差异恰是需要逐轨各配一支长度控制的原因——不能拿 full 轨长度去控制 ctx 轨冗余度, 否则控制变量与被控变量的定义域错配, 长度净化失效。本列与 full/ss 两轨长度控制互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁三轨长度控制混进同一 over-identified Hansen J。ctx 轨遇实体窗口降级 (ctx_is_fallback) 时文本回退为全文正文, 此时本列篇级取值与 full 轨趋同, 属预期而非缺陷。需再次强调本列仅为长度协变量而非独立构念: 它不进入任何以银行结果变量为被解释变量的主回归右端, 只在冗余度回归中与 avg_within_doc_redund_ctx 配对出现; 单独解读其水平高低无经济含义, 其价值完全体现在净化 ctx 轨冗余度系数的长度混杂上。聚合口径同为 mean-of-ln, 与地理面板 ln-of-mean 刻意不混用。

## VAR: avg_redund_log_length_full

【变体差分】
本列是配对长度控制的 full 轨变体, 亦为三轨中最贴近"整篇报道篇幅"的一支, 对应 content_full 文本轨: 标题 prepend 后拼接完整正文。它度量目标银行该年度每篇 full 轨报道去空白字符数的自然对数, 再取 bank-year 算术平均 (mean-of-ln)。留篇门控为 full-only 口径 (2026-06-29): 一篇报道是否计入本轨分母, 取决于 llm_verified_full 是否为真, 因此本列的报道宇宙与 full 轨冗余度 avg_within_doc_redund_full 完全同集, 保证配对控制与被控变量逐篇一一对应。其专属用途是在回归 avg_within_doc_redund_full 时净化长度的机械混杂, 而非独立解释银行结果变量。由于 full 轨保留整篇正文, 本列是三轨中篇幅信息最完整、水平通常最高的一支, 也最能吸收冗余度里由"长文更易重复"贡献的伪变异。本列与 ctx/ss 两轨长度控制互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁三轨长度控制同时进入同一 over-identified Hansen J 检验。与 geography 家族 ln_word_count 的 ln-of-mean 口径刻意区分、并存不混用: 前者控制篇级冗余、须 mean-of-ln 同域, 后者刻画年度典型篇幅。字符口径本列另有汉字口径孪生 avg_redund_han_log_length_full (剔数字/标点/拉丁仅计汉字), 二者是双口径长度控制、互为稳健性并各配同口径冗余度, 同样不得混进同一 over-identified Hansen J; 本列走字符口径, 与字符口径冗余度 avg_within_doc_redund_full 配对。

## VAR: avg_redund_log_length_ss

【变体差分】
本列是配对长度控制的 ss 轨变体, 对应 content_ss 文本轨: 标题 prepend 后拼接"目标银行与金科词同句共现 ±N 句窗口"内的片段 (句半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)。它度量 ss 轨报道去空白字符数取对数后的 bank-year mean-of-ln, 专供以 avg_within_doc_redund_ss 为解释变量的回归作逐轨同源长度控制。ss 轨是三轨中裁剪最激进的一支, 仅保留银行∧金科同句邻近片段, 篇幅通常最短, 故本列水平一般为三轨最低。ss 轨回退语义镜像 ctx: 当该篇无银行∧金科同句共现时, content_ss 回退为全文正文、ss_is_fallback=True, 此时本列篇级取值与 full 轨趋同; 若 FINTECH_AC=None 则整轨优雅降级、is_fallback 全真。本列与 full/ctx 两轨长度控制互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁三轨长度控制混进同一 over-identified Hansen J。逐轨各配一支长度控制的必要性在 ss 轨最为突出: 其极短篇幅使冗余度的长度敏感性最强, 若错用 full/ctx 轨长度替代, 定义域错配将使长度净化完全失真。与另两轨相同, 本列仅充当冗余度回归的配对协变量、不作独立测度解读; 其 mean-of-ln 聚合口径与被控的 avg_within_doc_redund_ss 同域, 而与地理面板的 ln-of-mean 篇幅特征刻意分列不混用。开发期 T=2 小样本上 ss 轨因裁剪激进可能出现零方差退化, 属预期而非缺陷, 生产期 T=19 恢复正常变异。

<!-- rendered-citations:begin -->
Chen, J., & Roth, J. (2024). Logs with zeros? Some problems and solutions. Quarterly Journal of Economics, 139(2), 891-936. https://doi.org/10.1093/qje/qjad054
Simonsohn, U., Nelson, L. D., & Simmons, J. P. (2014). P-curve: A key to the file-drawer. Journal of Experimental Psychology: General, 143(2), 534-547. https://doi.org/10.1037/a0033242
Campbell, D. T., & Fiske, D. W. (1959). Convergent and discriminant validation by the multitrait-multimethod matrix. Psychological Bulletin, 56(2), 81-105. https://doi.org/10.1037/h0046016
Bestgen, Y. (2024). Measuring Lexical Diversity in Texts: The Twofold Length Problem. Language Learning, 74(3), 638-671. https://doi.org/10.1111/lang.12630
<!-- rendered-citations:end -->
