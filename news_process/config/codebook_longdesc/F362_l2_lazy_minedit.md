---
family_id: F362
columns:
- lazy_minedit_ctx
- lazy_minedit_full
- lazy_minedit_ss
unit: 无量纲比率, 取值区间 [0, 1] (0=与上一年度文本完全相同, 1=与上一年度文本完全不同)
formula: 'lazy_minedit_{trk} = normalized_Levenshtein(doc_t[:2000], doc_{t-1}[:2000]) = edit_distance(prefix_t, prefix_{t-1}) / max(len(prefix_t), len(prefix_{t-1})); doc 为同一银行同一轨道 (full/ctx/ss) 在年度内聚合拼接 (groupby 保序、组内不按日期排序) 的年度文本, 实际参与计算的仅为该文本前 _LEVEN_MAX_CHARS=2000 字符前缀'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\export.py
upstream: []
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
new_dois: []
---

## CORE

【构念与来源】
lazy_minedit 家族衡量某银行相邻两个年度 (t 与 t-1) 的年度聚合报道文本之间的"改动量", 用归一化编辑距离 (normalized Levenshtein distance) 作为度量算子。构念直接迁移自 Cohen, Malloy & Nguyen (2020, The Journal of Finance) 提出的"懒惰定价" (lazy prices) 文档变化度量方法论: 该文发现公司年报 (10-K/10-Q) 相邻期文本改动越少, 市场对新信息的定价反应越滞后、股价对该"懒惰"信号存在可预测的漂移。本项目将该方法论从"公司年报相邻期改动"迁移到"银行年度新闻报道文本相邻期改动", 用编辑距离量化某银行关于自身的媒体叙事在年度间的变化幅度: 数值越接近 1, 说明该行当年的新闻文本相对上一年"改写"越多、媒体叙事更新越活跃; 数值越接近 0, 说明媒体年复一年地重复相近的表述、叙事呈现"惰性"或高度程式化。producer 源码注释中给出的白话表述是"看每家银行今年和去年的新闻改了多少", 与欧阳志刚 & 胡雯华 (2024) 的余弦相似度连贯性度量 (coh_* 家族) 共享同一相邻期比较框架, 但两者构念方向相反且互为补充: coh_* 度量"像不像" (相似度, 越高越连贯), lazy_minedit 度量"改没改" (差异量, 越高越变化), 二者并非同一构念的重复表达, 而是从"稳定性"与"变化量"两个互补视角刻画同一相邻期文本对比问题, 详见下文【与相邻测度的构念区分】。

【方法学与计算】
计算分三步。第一步, 年度聚合: 对每家银行、每个年度、每条轨道 (full/ctx/ss), 由 `_aggregate_bank_year_texts` 把该行该年落在该轨道下的全部文章文本拼接为一份"年度文档" (agg_df / agg_ctx / agg_ss)。该函数暴露一个稳健开关 `co_mention_downweight`, 用于按 1/n_banks 对多行同篇 (一篇报道同时提及多家银行) 的重复计权做降权处理; 生产口径下该开关默认值为 False (维持原口径, 即不降权), 是否启用取决于 `config/features.yaml` 或调用方显式传参, 并非年度聚合过程内置生效的默认行为, 使用本家族数据前应先核实当次运行的 `co_mention_downweight` 实际取值, 否则可能低估共提及文章对年度文档内容与后续编辑距离的重复计权影响。第二步, 相邻期配对: 对同一银行, 取年度 t 的年度文档与年度 t-1 的年度文档配对 (bank 固定, year 与 year-1 逐年滚动), 缺上一年年度文档的银行-年度观测该列取缺失值。第三步, 归一化编辑距离: producer 源码 (`_compute_lazy_distances`) 自曝一项对该算子有效性构成实质性限制的截断处理——受 Levenshtein 距离 O(L²) 复杂度制约, 参与计算的并非两份完整年度文档, 而仅是各自前 `_LEVEN_MAX_CHARS=2000` 字符的前缀; 该前缀由 `groupby` 保序拼接产生, 组内文章不按日期排序, 因此前缀实际内容取决于上游 parquet 的原始行序, 上游若重排/去重即会改变该列取值。producer 源码原话披露: 此设计下 minedit 实质度量的是"两个任意头部文章片段的编辑距离", 而非整份年度文档的改写幅度; 且盘上实测该列已明显退化——均值贴近上限 (mean≈0.95) 且变异极小, 反映的更接近"任意两段不同中文前缀"的噪声而非有意义的年际叙事变化信号。producer 明确建议: 回归端应优先使用不受该截断影响的全文 token 集算子 lazy_jaccard/lazy_overlap, lazy_minedit 仅作三算子稳健性矩阵的披露性补充, 不应单独作为主回归的解释变量使用。该算子与 lazy_jaccard (集合层面的 Jaccard 距离)、lazy_overlap (词集重叠率) 共同构成 producer 注释所称的"多距离 adjacent-period document-change" 三算子族, 三者形式上并排互证同一构念、互为稳健性、不分主次, 但受限于上述截断/乱序/近天花板退化问题, lazy_minedit 在实际解释力上明显弱于另外两个未受长度截断影响的算子, 研究者引用本家族做稳健性检验时应在正文注明这一测量效度局限, 不宜脱离 lazy_jaccard/lazy_overlap 单独据其得出叙事变化结论。

【文献定位】
Cohen, Malloy & Nguyen (2020, The Journal of Finance) 是该方法论的直接来源: 原文用相邻期公司年报的文本相似度/改动量刻画"懒惰"信息披露行为, 发现改动少的公司未来股票回报存在可预测的负向漂移, 揭示了市场对文本变化这一软信息处理不足的现象。本项目在同一逻辑下, 把度量对象从公司自身披露的年报文本替换为第三方媒体关于银行的报道文本, 关注的是媒体叙事层面的年度更新幅度而非公司自我披露的更新幅度, 是对该文献度量工具向媒体文本领域的方法论迁移, 而非对原始构念 (公司信息披露懒惰) 的直接复制。欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究) 的余弦相似度连贯性框架 (coh_tfidf_c/coh_tfidf_w/coh_lda/coh_emb 家族) 为本家族提供了"相邻期文本比较"这一分析设计的本地文献支撑与三轨/多算子并列的实现范式参照。最小编辑距离作为文本相似度指数的方法学基础另有 Mainali, Slud, Singer & Fagan (2022, Science Advances) 的顶刊支撑: 该文系统比较了多种共现与相似度指数各自的统计性质, 为本列在 Jaccard/重叠度之外并列采用编辑距离类指数提供了方法学正当性。Liu, Cao & Wen (2024, Economics Letters) 在公司与政府文本相似度的实证研究中同样采用序列层面的文本相似度量, 印证此类指数在金融文本计量中的可行性与外部效度。

lazy_minedit_full / lazy_minedit_ctx / lazy_minedit_ss 三列对应本项目三轨文本架构 (full=标题+正文全文; ctx=标题+实体窗口; ss=标题+银行∧金科同句±N窗)。三轨在年度聚合与相邻期编辑距离计算上使用完全相同的算子, 唯一差异是喂入 `_aggregate_bank_year_texts` 的源文本列 (content_full / content_ctx / content_ss), full 轨复用主聚合函数顶部已生成的 agg_df 以避免冗余计算, ctx 与 ss 轨各自新建聚合。三轨严格遵循项目铁律: 各自 just-identified 并排、互为稳健性、不分主次, 禁止混进同一 over-identified 的 Hansen J 检验。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行与金科词同句共现, 则该篇的 content_ss 回退为全文 body (与 content_full 相同), 对应的 ss_is_fallback 标记为 True, 该回退在年度聚合层面共享 full 轨的 n_articles 分母口径; 若 content_ctx 或 content_ss 列在上游因故不存在 (例如 FINTECH_AC 词典未加载导致优雅降级), 对应轨道整体跳过、以日志 WARNING 记录, 该行该年度该轨道的 lazy_minedit 取缺失值, 不做静默填 0 处理。三列的留篇口径与全体情感/属性测度一致遵循 full-only 门控 (2026-06-29 起): 是否判定"一篇银行金科报道"只看 full 轨的 llm_verified_full 结果, ctx/ss 轨的年度文档聚合行宇宙是 full 轨留篇集合的子集, 在此子集上各轨分别聚合、分别计算编辑距离, 不存在 ctx/ss 独立扩大样本的情形。

## VAR: lazy_minedit_ctx

【变体差分】
本列取自 ctx 轨: 年度文档由每篇文章的 content_ctx (标题+实体窗口文本) 逐篇拼接聚合而成, 再对相邻两年的 ctx 年度文档计算归一化编辑距离; 与家族 canonical 一致, 实际参与计算的仅是该年度文档前 2000 字符的前缀 (groupby 保序、组内不按日期排序), 而非完整年度文档全文。与 full 轨相比, ctx 轨每篇源文本本身已收窄到围绕目标实体的局部窗口, 因此在同样的 2000 字前缀截断下, ctx 轨前缀相对更可能落在与银行/金科直接相关的表述范围内, 截断带来的信息损失理论上小于 full 轨, 但前缀内容仍取决于上游行序、并非按重要性或日期挑选, 这一局限并未消除。该列的样本行宇宙是 full 轨留篇集合的子集 (full-only 门控, 2026-06-29 起), 若上游 content_ctx 列缺失, 该列整体跳过计算、取缺失值, 不回退借用 full 轨结果。与 lazy_minedit_full、lazy_minedit_ss 是同一算子在不同文本轨道上的并排复现, 三者互为稳健性、不分主次, 不应放入同一过度识别的 Hansen J 检验; 三轨同受 producer 披露的前缀截断/乱序/近天花板退化问题制约, 均不宜单独作为主回归解释变量, 仅作 lazy_jaccard_ctx/lazy_overlap_ctx 的披露性补充。使用时应结合当年 n_articles 一并解读, 样本量过小的行-年度观测建议在稳健性检验中剔除或加权处理; ctx 轨与 coh_emb_ctx 等连贯性测度共享同一份 agg_ctx 聚合中间产物, 二者可视为同一年度文档对在"变化量"与"相似度"两个方向上的镜像度量, 但本列自身的解释力受限见上文, 引用时不宜脱离 lazy_jaccard_ctx/lazy_overlap_ctx 单独立论。

## VAR: lazy_minedit_full

【变体差分】
本列取自 full 轨 (家族 canonical 主轨): 年度文档由每篇文章的 content_full (标题+正文全文) 逐篇拼接聚合而成 (复用相邻期文本连贯性计算流程中已生成的 agg_df, 避免重复聚合开销), 再对相邻两年的 full 年度文档计算归一化编辑距离。作为三轨中信息量最完整的一支, full 轨的年度文档篇幅通常最长, 这意味着 producer 披露的 2000 字前缀截断在 full 轨上造成的信息损失也最大——实际参与编辑距离计算的往往只是该年度文档前若干篇文章 (由上游 parquet 行序决定, 不按日期排序) 的头部内容, 而非该行该年全部报道文本。producer 源码原话对此有明确自曝: 该设计下 minedit 实质度量的是"两个任意头部文章片段的编辑距离", 盘上实测数值已明显退化 (均值贴近上限、变异极小), 不宜脱离该局限直接解读为"媒体叙事改写幅度"。该列的行宇宙即 full-only 留篇门控本身所定义的留篇集合 (llm_verified_full==True), 是 ctx/ss 两轨样本子集所对应的母集合。与 lazy_minedit_ctx、lazy_minedit_ss 并排互为稳健性、不分主次, 不进入同一过度识别的 Hansen J 检验。作为家族 canonical 主轨, full 轨在构念层面最贴近 Cohen, Malloy & Nguyen (2020) 原始方法论中"整篇文档相邻期改动"的立意 (原文比较的是完整年报文本), 但受上述前缀截断限制, 本项目实现并未完整复现原文献"逐字比较全文"的计算口径, 跨研究复现与结果对表时应如实说明这一差异。producer 建议回归端优先使用不受长度截断影响的 lazy_jaccard_full/lazy_overlap_full 两个全文 token 集算子, lazy_minedit_full 仅作三算子稳健性矩阵的披露性补充, 不应单独作为主回归的解释变量; 即便结合 boilerplate 套话比率、staff_written_frac 等控制变量联合解读, 也需在前置文本注明该列已知的截断/乱序退化问题。

## VAR: lazy_minedit_ss

【变体差分】
本列取自 ss 轨: 年度文档由每篇文章的 content_ss (标题+银行∧金科同句±N窗文本, N 见 config/filtering.yaml::context_window.ss_sentence_radius) 逐篇拼接聚合而成, 再对相邻两年的 ss 年度文档计算归一化编辑距离。ss 轨是三轨中文本窗口最窄、判定最严格的一支: 只保留银行与金科词在同一句 (±N句) 内共现的局部片段, 因此年度文档比 ctx 轨更短、信噪比理论上更高, 编辑距离度量的是银行与金科紧密关联表述的年度改写幅度。回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 该篇的 content_ss 回退为全文 body (等同 content_full), 对应 ss_is_fallback 标记为 True, 回退发生时该篇在年度聚合中的分母口径与 full 轨共享 n_articles; 若上游 content_ss 列整体缺失 (例如金科词典未加载导致 FINTECH_AC=None), 该列整体跳过计算、取缺失值。该列的样本行宇宙同样是 full 轨留篇集合的子集。与 lazy_minedit_full、lazy_minedit_ctx 并排互为稳健性、不分主次, 不应放入同一过度识别的 Hansen J 检验。三轨之中, ss 轨的判定口径最严格 (要求银行词与金科词严格同句共现, 而非 ctx 轨的实体窗口), 因此该轨的年度文档在多数行-年度观测下会显著短于 ctx 轨甚至频繁触发全文回退, 编辑距离的方差与回退比例都会明显高于 ctx 轨。与另外两轨相同, ss 轨的计算同样受 producer 披露的 2000 字前缀截断限制——但由于 ss 轨年度文档本身较短, 未触及 2000 字上限的行-年度观测比例相对更高, 此时该行截断损失小于 ctx/full 轨; 一旦触及上限, 同样退化为"任意头部片段编辑距离"、盘上实测近天花板 (mean≈0.95) 的已知问题。使用该列时应格外留意 ss_is_fallback 标记比例: 若某银行-年度对的回退比例很高, 说明当年该行的"银行-金科紧密关联报道"本就稀少, ss 轨此时退化为与 full 轨高度重合的度量, 编辑距离的解释力受上述前缀截断制约进一步削弱。producer 明确建议该三算子族中 minedit 仅作 lazy_jaccard_ss/lazy_overlap_ss 的披露性补充, 不宜单独作为主要解释变量来源, 更适合作为 ctx 轨结论的严格性稳健性检验之一环、且须在正文注明其已知的测量效度局限。

<!-- rendered-citations:begin -->
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Mainali, K. P., Slud, E., Singer, M. C., & Fagan, W. F. (2022). A better index for analysis of co-occurrence and similarity. Science Advances, 8(4), Article eabj9204. https://doi.org/10.1126/sciadv.abj9204
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters, 241, Article 111823. https://doi.org/10.1016/j.econlet.2024.111823
<!-- rendered-citations:end -->
