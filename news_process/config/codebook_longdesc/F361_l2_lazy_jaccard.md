---
family_id: F361
columns:
- lazy_jaccard_ctx
- lazy_jaccard_full
- lazy_jaccard_ss
unit: 无量纲 Jaccard 距离得分, 值域 [0,1] (1=前后两期年度文本词集完全不重合即"改动量最大", 0=完全重合即"零改动"; 注意本列是相似度的补数——距离而非相似度, 数值越高代表文本变动越大)
formula: 'lazy_jaccard_track_{i,t} = 1 − |W_{i,t} ∩ W_{i,t-1}| / |W_{i,t} ∪ W_{i,t-1}|; W_{i,t} 为银行 i 第 t 年该轨道 (full/ctx/ss) 聚合年度文本经分词/去重后的词集合 (集合运算, 与词频加权余弦无关); 括号内的比值 |交集|/|并集| 是 Jaccard 相似度, 落盘前经 1 − 相似度 转换为 Jaccard 距离 (源码 strategic_diff.py::_compute_lazy_distances, "距离 = 1 − 相似度"); 相邻期 (t, t-1) 面板内滚动配对, t 为样本首年时该行前值缺失 (无 t-1 可比, 非计算错误)'
producer: pipeline\features\strategic_diff.py::_compute_lazy_distances (经 pipeline\panel\export.py 变量标签表落盘)
upstream:
- 14_materialize_ctx (content_ctx/content_ss 物化)
- 40_panel_export_main (bank-year 年度文本聚合 _aggregate_bank_year_texts)
citations:
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: Lazy prices
  venue: The Journal of Finance
  vol: '75'
  issue: '3'
  pages_or_artno: 1371-1415
- doi: 10.1126/sciadv.abj9204
  type: journal
  authors: Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F.
  year: 2022
  title: "A better index for analysis of co-occurrence and similarity"
  venue: Science Advances
  vol: 8
  issue: 4
  pages_or_artno: Article eabj9204
- doi: 10.1016/j.econlet.2024.111823
  type: journal
  authors: Liu, Y., Cao, Z., & Wen, F.
  year: 2024
  title: "Textual similarity between firm and government: Measurement and pricing"
  venue: Economics Letters
  vol: 241
  pages_or_artno: Article 111823
- doi: "10.1111/acfi.13076"
  type: "journal"
  authors: "Wang, Y., Ye, Q., Wang, J. J., & Wang, Y."
  year: 2023
  title: "Earnings manipulation and similarity of annual report disclosure: Evidence from China"
  venue: "Accounting & Finance"
  vol: "63"
  issue: "S1"
  pages_or_artno: "1137-1156"
new_dois: []
---

## CORE

【构念与来源】
lazy_jaccard 家族测度的是同一家银行相邻两个年度 (t 与 t-1) 的媒体报道文本"改动了多少"——数值越高代表改动量越大, 数值越低代表改动量越小 (趋近 0 即"零改动")。构念直接移植自 Cohen, Malloy & Nguyen (2020, 简称 CMN) 提出的"懒惰定价" (lazy prices) 框架: 该文发现公司在两次连续年报/10-K 之间对文本改动越少, 市场对其中隐含信息的反应越滞后、越不充分, "文本改动量"本身构成一个可观测、可预测收益的信号。本仓库将这一"公司披露文本年度改动量"的构念从公司自主撰写的监管文件 (10-K) 迁移到本项目情境下的银行-年度媒体报道聚合文本: 银行每年被媒体报道的全部文章经聚合形成一份"年度文本"; 计算内部先求银行 i 在年份 t 的年度文本与其上一年 (t-1) 年度文本之间的 Jaccard 相似度 (|交集|/|并集|), 但落盘前对该相似度取补 (1 − 相似度), 因此本列本身是 Jaccard 距离而非相似度——这一取补步骤是理解本家族取值方向的关键, 不可省略或倒置。与 CMN 原始研究关注"企业主动选择改写多少年报措辞"不同, 本项目的年度文本是媒体书写而非银行自撰, 因此 lazy_jaccard 度量的更准确地说是银行在媒体叙事层面的"年度话题/措辞改动量", 低值意味着媒体对该行的报道口径、议题结构、常用表述年复一年高度重合 (可能反映该行经营常态、媒体关注惯性、或该行公关口径稳定), 高值意味着报道内容发生实质性转向 (新事件、新议题、新表述大量涌入)。这一构念与本家族同批次产出的 coh_* (相邻期文本连贯性, 余弦相似度, 未取补——高值=连贯) 是姊妹测度但方法学根本不同且取值方向不镜像: coh_* 借道欧阳志刚与胡雯华 (2024) 的"连贯性→降低不确定性→提升传导效率"逻辑链, 用词频/嵌入向量的余弦相似度衡量语义层面的连贯程度, 数值越高代表越连贯; lazy_jaccard 及其同族算子 (lazy_overlap、lazy_minedit, 不在本家族但共享同一计算入口 `_compute_lazy_distances`, 均以"距离"形式落盘) 则完全基于离散词集合运算或字符串编辑距离, 不涉及向量空间或语义嵌入, 是纯粹的"表层文本改动量"测度, 数值越高代表改动越大, 与语义连贯性测度形成方法学互补而非替代 (二者取值方向相反, 联合解读时须留意符号)。

【方法学与计算】
计算发生在 `pipeline/features/strategic_diff.py` 的 `_compute_lazy_distances` (由主函数在"改进 B: 相邻期文本连贯性"代码块内, 三轨循环调用)。上游先由 `_aggregate_bank_year_texts` 把该轨道下同一银行同一年份的全部文章文本聚合为一份年度文本 (聚合逻辑与 coh_* 家族共用同一聚合函数, 可选 co-mention 降权 `co_mention_downweight`), 再对聚合文本分词、转为词集合, 逐年份与其紧邻的上一年份文本求 Jaccard 相似度: 分子为两期词集合的交集大小, 分母为并集大小。函数内部随即对该相似度取补 (1 − 相似度) 再落盘为 `lazy_jaccard{track_suffix}` 列 (源码注释明确写"距离 = 1 − 相似度"), 因此最终列值是 Jaccard 距离: 值越接近 1 表示两期词集合越不重合、改动量越大, 值越接近 0 表示两期词集合越重合、改动量越小。这是纯粹的"存在性"集合运算——只关心某个词在两期是否都出现过, 不关心其出现频次或位置, 因此 lazy_jaccard 对"高频常用词大量重复但具体措辞已实质改写"这类情形不敏感, 需与同一入口产出的 lazy_overlap (集合重叠度的另一种归一化, 同样以距离形式落盘) 与 lazy_minedit (归一化编辑距离, 对词序/局部替换更敏感) 相互印证, 三算子不分主次、各自独立成列 (lazy_overlap/lazy_minedit 属另外的家族条目, 不在本文档范围内)。由于运算以"相邻期配对"为单位, 面板内每家银行的样本首年 (无 t-1 可比) 该行取值缺失, 这是设计使然而非缺陷; 本项目面板样本跨度较短的开发/测试子集上, 缺失比例会显著高于生产语料 (T=19) 下的稳态表现, 不应误读为测度失效。三个轨道 full/ctx/ss 使用完全独立的年度文本聚合与独立的相邻期配对, 互不借用彼此的词集合, 且三轨均遵循同一"取补落盘"规则, 取值方向一致可比。

【文献定位】
本家族的方法学根基是 Cohen, Malloy & Nguyen (2020, Journal of Finance) 关于企业文本"懒惰"改动与信息滞后反应的开创性发现——该文构造的年报文本增量比较框架 (含 Jaccard 相似度在内的多种文本距离度量) 已成为公司文本分析文献中衡量"披露文本动态变化"的标准工具之一。本仓库对该构念做了两处适配: 其一是应用对象从企业自撰监管文件迁移到媒体报道聚合文本 (信息来源方由被评价对象本身变为第三方媒体), 因此其经济学解释也随之从"企业主动隐藏坏消息的懒惰披露行为"调整为"媒体报道议题与用词的年度延续性"; 其二是三轨并行 (full/ctx/ss), 让同一构念在不同文本口径 (全文、目标实体上下文窗口、银行∧金科同句共现窗口) 下各自独立估计, 便于检验该测度对文本截取口径的敏感性。文本相似度指数的方法学基础另有 Mainali, Slud, Singer & Fagan (2022, Science Advances) 的顶刊支撑: 该文系统比较了包括 Jaccard 在内的多种共现与相似度指数, 论证不同指数对样本量、稀疏度的敏感性存在系统差异, 为本列采用 Jaccard 相似度并将其纳入多指数并排稳健性矩阵提供了方法学依据。Liu, Cao & Wen (2024, Economics Letters) 在公司与政府文本相似度的实证研究中亦采用类 Jaccard 重叠度量, 印证文本重叠指数在金融文本计量中的可行性与外部效度。 在中文语料层面, Wang、Ye、Wang 与 Wang (2023) 提供了与本家族最贴近的同域先例: 该文在 2008-2020 年中国 A 股 13,679 家样本上, 以 MD&A 文本与上一年文本的相似度作为核心测度, 记录了"高相似度即低增量信息"的经验规律, 说明中文分词后的词集/词袋重合度在相邻期自比设定下是可操作且承载信息量的测度, 从而为本家族把中文年度聚合文本切分为词集合后做相邻期 Jaccard 比对的路线提供外部佐证。援引口径须作三重限定: 其一, 该文发表于 2023 年, 不属近三年前沿, 仅作方法可行性的同域旁证; 其二, 其语料为公司自撰年报 MD&A、单位为公司-年, 本家族为银行-年第三方媒体报道聚合文本, 文本作者身份不同, 上文已申明的"媒体议题延续性而非企业主动披露选择"这一解释调整同样适用于此处; 其三, 也是方向上最关键的一点, 该文使用的是相似度且将其解释为盈余操纵动机的显示, 而本列落盘的是相似度的补数即 Jaccard 距离 (值越高代表改动量越大, 与该文测度的取值方向相反), 且本家族是中性的表层改动量测度, 既不承接其操纵动机解释, 也不因该文的发现而对本列高值或低值预设任何行为学含义, 联合解读时须先完成取补方向的对齐。
## VAR: lazy_jaccard_ctx

【变体差分】
本列取 ctx 轨: 年度聚合文本来自 `content_ctx` (标题 + 目标银行实体上下文窗口拼接文本, 在 stage 14 `ctx_materializer` 物化), 而非全文正文。计算入口与 full/ss 完全相同 (同一 `_compute_lazy_distances` 函数、同一相邻期配对逻辑、同一 Jaccard 定义), 唯一差异是喂入的年度文本聚合源不同: ctx 轨聚合的是每篇文章中围绕目标银行实体截取的局部窗口文本, 而非整篇报道。这意味着 ctx 轨的"改动量" (取值方向与家族一致: 越接近 1 改动越大、越接近 0 改动越小) 衡量的是媒体谈论该行时紧邻实体名的措辞与话题年复一年的变动程度, 相对 full 轨排除了文章其余部分 (可能与该行无直接关系的背景信息、其他机构、宏观评论等) 对底层 Jaccard 集合运算的稀释或干扰, 在理论上应比 full 轨对"该行相关叙事"本身的变化更敏感。若某篇文章不存在可提取的实体上下文窗口 (即无法判定目标实体位置), 该篇在物化阶段的回退语义由 stage 14 统一处理, 不在本列计算逻辑内单独处理。ctx 轨与 full 轨、ss 轨在本项目口径下是各自 just-identified 并排、互为稳健性、不分主次的三个平行估计, 三者不得混入同一个 over-identified 的 Hansen J 检验框架联合估计, 也不应把某一轨视为另两轨的"更优版本"取而代之——三者共同构成对文本口径选择的稳健性检验梯子。

## VAR: lazy_jaccard_full

【变体差分】
本列取 full 轨: 年度聚合文本来自完整文章正文 (标题 + 全文内容), 是本函数顶部已生成的 `agg_df` 直接复用, 不需要为 full 轨单独重新聚合, 因此在实现上 full 轨天然是三轨中计算路径最短的一支。full 轨衡量的是银行年度媒体报道"整篇文本"层面的逐年改动量 (取值方向与家族一致: 越接近 1 改动越大、越接近 0 越无改动), 不做任何实体窗口或共现窗口截取, 覆盖信息量最大也最"嘈杂"——一篇报道里与目标银行无关的背景段落、其他公司或事件的叙述, 同样计入年度文本词集合参与 Jaccard 运算。这是三轨中口径最宽的一支, 在本项目"留篇门控 = full-only"的口径下 (2026-06-29 起, 是否判定为一篇有效银行-金科报道只看 full 轨的 LLM 判定结果), full 轨同时也是决定该银行-年度是否进入样本的把关轨道, 因此 full 轨的年度文本行宇宙是 ctx/ss 两轨的父集, ctx/ss 两轨是在 full 轨留篇集合基础上的条件测度/稳健性轨。full 轨与 ctx、ss 两轨各自独立估计、并排呈现, 互为稳健性、不分主次, 禁止混入同一个 over-identified Hansen J 联合估计框架。使用者若只报告单一轨道结果, 建议优先选取 full 轨作为基准陈述口径 (因其决定留篇门控、样本行宇宙最完整), 同时在稳健性附录中并列 ctx、ss 两轨结果, 而非把三者视为可相互替代、择优汇报的候选测度。

## VAR: lazy_jaccard_ss

【变体差分】
本列取 ss 轨: 年度聚合文本来自 `content_ss` (标题 + 银行与金科关键词落入同一句、且句间半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 参数控制, 默认窗口半径为 1 的最窄口径共现文本), 是三轨中文本覆盖范围最窄、判据最严格的一支。ss 轨的回退语义严格镜像 ctx 轨: 当某篇文章不存在银行与金科关键词同句共现的片段时, 该篇的 `content_ss` 退化为使用全文正文, 并由对应的 `ss_is_fallback` 标记为真, 与 ctx 轨在无可提取实体窗口时的回退处理在语义结构上完全对称、共享同一套 `n_articles` 分母口径。当上游 `FINTECH_AC` (金科关键词自动机) 未装载或为 None 时, 全体样本的 `*_is_fallback` 一并置真, 以保证降级优雅、不中断计算。因此 ss 轨的 lazy_jaccard 值应理解为"银行与金科议题同时出现的最紧密语境下, 年度用词与叙事的逐年改动量" (取值方向与家族一致: 越接近 1 改动越大、越接近 0 越无改动), 当样本中大量文章触发回退时, ss 轨在数值上会趋近于 full 轨, 这是 fallback 机制的预期行为而非计算异常。与 full、ctx 两轨相同, ss 轨在 `_compute_lazy_distances` 中走完全独立的年度聚合与相邻期配对, 三轨互不借用彼此的中间结果, 各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一个 over-identified Hansen J 联合估计。ss 轨判据的主体是"银行∧金科词是否落入同一句", 与 stage 13 共现硬过滤所用的判据 (句间半径窗口, 决定文章是否进入样本) 是不同但相关的两套口径, 使用者引用 ss 轨结果时应明确其窗口半径参数取值, 避免与 stage 13 过滤口径混淆。

<!-- rendered-citations:begin -->
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
Wang, Y., Ye, Q., Wang, J. J., & Wang, Y. (2023). Earnings manipulation and similarity of annual report disclosure: Evidence from China. Accounting & Finance, 63(S1), 1137-1156. https://doi.org/10.1111/acfi.13076
<!-- rendered-citations:end -->
