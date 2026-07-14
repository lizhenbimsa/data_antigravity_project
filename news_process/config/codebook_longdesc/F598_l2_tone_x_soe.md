---
family_id: F598
columns:
- tone_x_soe_ctx
- tone_x_soe_full
- tone_x_soe_ss
unit: 交互项得分 (连续, 理论域约 [-1,1] × {0,1} 退化为 [-1,1]; bank-year 面板层面, 无新闻覆盖年份为 NaN)
formula: 'tone_x_soe{track} = llm_vote_tone{track} * is_soe, track ∈ {_full, _ctx, _ss}; is_soe 为国有银行 0/1 哑变量, llm_vote_tone{track} 为三家 LLM 多数投票语调共识列'
producer: pipeline\panel\runner.py (交互项构建, L1595-1605) ; pipeline\panel\export.py (dta 标签映射, L905-906; 仅 tone_x_soe_full/_ctx 有标签行, tone_x_soe_ss 无对应 dta 标签行, 导出时沿用列名本身)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
- is_soe
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1111/j.1540-6261.2009.01493.x"
  type: journal
  authors: "Fang, L.; Peress, J."
  year: 2009
  title: "Media Coverage and the Cross-Section of Stock Returns"
  venue: "The Journal of Finance"
  vol: "64"
  issue: "5"
  pages_or_artno: "2023-2052"
- doi: "10.1016/j.jeconom.2020.07.053"
  type: journal
  authors: "Shapiro, A. H.; Sudhof, M.; Wilson, D. J."
  year: 2022
  title: "Measuring News Sentiment"
  venue: "Journal of Econometrics"
  vol: "228"
  issue: "2"
  pages_or_artno: "221-243"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y.; Wang, Q.; Wang, Y.; Yuan, Y."
  year: 2024
  title: "Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  issue: ""
  pages_or_artno: "1150-1172"
- doi: "10.1111/j.1540-6261.2010.01625.x"
  type: journal
  authors: "Loughran, T.; McDonald, B."
  year: 2011
  title: "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks"
  venue: "The Journal of Finance"
  vol: "66"
  issue: "1"
  pages_or_artno: "35-65"
new_dois: []
---

## CORE

【构念与来源】
本家族 (F598, l2_tone_x_soe) 度量的是"银行报道语调"与"是否国有银行"这一结构性调节变量的乘积, 用于在 bank-year 面板回归中检验语调—结果关系是否因所有权性质而系统性不同, 即异质性效应 (heterogeneous treatment effect) 的检验工具, 而非独立构念。三列共享同一生成公式, 唯一差别是分母上语调来源所依附的文本轨道 (full/ctx/ss)。产生位置在 `pipeline/panel/runner.py` 的面板派生阶段 (标注为"(d) 交互项构建"), 紧邻同一循环内生成的 tone_x_scale/tone_x_highcov 两个姊妹交互族, 三者共用同一段 for-loop 骨架, 仅右侧调节变量不同 (is_soe / bank_scale_ord / high_coverage)。乘数项 is_soe 是银行层面静态属性 (国有商业银行、政策性银行等归为 1, 其余股份制/城商/农商归为 0), 与年份无关, 因此交互项的时序变动完全来自语调本身而非调节变量。语调项 llm_vote_tone{track} 是 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票共识, 值域理论上约 [-1, 1] (负面/中性/正面三分类映射), 在无该银行该年新闻覆盖时为 NaN, 交互项据此继承缺失 (而非误填 0), 避免把"无报道"误判为"零语调"这一常见陷阱 (见下方【方法学与计算】的冗余提示)。构念定位上, 该族属于典型的调节效应 (moderation) 设计变量, 学理依据 Aiken & West (1991) 式的乘积项交互建模, 项目内注释亦援引 Angrist & Pischke (2009) 与 Brambor, Clark & Golder (2006) 关于交互项模型设定与边际效应解读的规范性建议——交互项系数本身不能孤立解读, 须结合两个构成项的主效应及边际效应图 (marginsplot) 联合报告, 这是使用本家族三列做回归时必须遵守的解读铁律, 而非该家族列本身携带的信息缺陷。

【方法学与计算】
计算公式极简: 对每一条 track ∈ {full, ctx, ss}, 取该 track 对应的 `llm_vote_tone{track}` 列与 `is_soe` 列逐行相乘, 得到 `tone_x_soe{track}`。源码中紧邻一条重要的方法学注记 (runner.py 内部注释): 原始设计中曾用二元的 has_coverage (0/1) 与语调相乘, 但该交互项被证明是冗余的——零新闻覆盖行的语调本身即为 NaN, 相乘后仍为 NaN (不会退化成 0); 有新闻覆盖行 tone × 1 = tone, 交互项完全退化为语调本身, 不携带任何超出语调主效应之外的增量信息。这条注记虽然是关于 has_coverage 交互族的历史教训, 但其逻辑同样提醒使用者: is_soe 是静态哑变量而非覆盖强度哑变量, tone_x_soe 之所以有意义, 恰恰是因为 is_soe 在样本内既有 0 组也有 1 组、且不与语调本身共线, 而不是简单的"语调乘以任意 0/1 变量"都天然有效。三轨语调来源 full/ctx/ss 严格对齐 CLAUDE.md 「三轨」铁律: full=标题+正文全文语调, ctx=标题+银行/金科实体窗口语调, ss=标题+银行∧金科词严格同句 (±1 句默认半径) 窗口语调, 三者共享的口径基础是 stage 21 的 full-only 留篇门控 (2026-06-29 起生效)——一篇报道是否计入"银行金科报道"的判定只看 `llm_verified_full`, ctx/ss 语调是在该 full 留篇行子集之上的条件测度 (conditional-on-full), 因此 tone_x_soe_ctx/_ss 的样本行宇宙是 tone_x_soe_full 的子集而非独立采样; ss 轨若某年某行无银行∧金科同句共现, 语调回退为镜像 ctx 的口径——`ss_is_fallback=True` 标记下语调改用全文 body 计算, 与 ctx 的实体窗口回退语义对称, 而非留空。三条列各自是 just-identified 并排的稳健性轨道, 彼此互为稳健性检验、不分主次, 在回归设定中严禁把三条轨道同时塞进同一个 over-identified 的 Hansen J 过度识别检验框架——每条轨道应各自跑一次交互效应回归, 用跨轨道系数符号/显著性的一致性作为稳健性证据, 而不是把它们当作同一模型里的多个工具变量并做联合过度识别检验。

【文献定位】
交互项/调节效应的计量设定规范, 项目内部注释直接援引 Angrist & Pischke (2009, *Mostly Harmless Econometrics*) 与 Brambor, Clark & Golder (2006, *Political Analysis*) 关于交互项模型"低阶项必须同时纳入、边际效应须图示而非仅读系数"的建议。语调本身作为媒体情感测度构念的方法学基础可追溯 Tetlock (2007, *Journal of Finance*) 关于媒体语调对股票市场定价含量的经典发现, 以及 Fang & Peress (2009, *The Journal of Finance*) 关于媒体覆盖强度与横截面收益关系的研究——后者也是本家族姊妹交互族 tone_x_highcov 的直接学理来源, 侧面印证本项目将媒体测度维度 (语调、覆盖强度) 与银行结构属性 (所有权、规模) 交叉建模的设计脉络与主流金融文献一致。就中国银行业情境下国有属性作为调节变量的合理性而言, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 对中国银行媒体情感与系统性风险关系的研究提供了同一制度背景下的直接参照, 其研究设计同样关注媒体情感效应在银行异质性 (含所有权结构) 上的分化, 与本家族"语调 × 国有属性"交互设计的实证动机高度吻合。语调测度本身的方法学谱系另见 Loughran & McDonald (2011, *The Journal of Finance*) 关于文本情感字典法的经典基准与 Shapiro, Sudhof & Wilson (2022, *Journal of Econometrics*) 关于新闻语调测度构造的方法论综述, 二者共同构成语调主效应 (llm_vote_tone) 的测度学理基础, 本交互族继承其构念效度, 仅在此基础上叠加国有属性调节。

## VAR: tone_x_soe_ctx

【变体差分】
本列取 `llm_vote_tone_ctx` (标题 + 银行/金科实体窗口语调) 与 `is_soe` 的逐行乘积。相较 canonical 全文轨 tone_x_soe_full, 本列的语调来源聚焦在报道中提及目标银行与金科相关实体的局部文本窗口, 剔除全文中与银行—金科关系无关的背景段落干扰, 因而更贴近"报道对银行—金科关系本身的评价语气", 是 tone_x_soe_full 的互为稳健性并排轨道而非替代或加强关系——二者应分别估计交互效应系数, 用符号与显著性模式的一致性作为构念效度证据, 不得混入同一 over-identified 设定联合估计。样本行宇宙上, 本列继承 full-only 留篇门控: 是否计入回归样本仍由 `llm_verified_full` 判定, ctx 语调只在该子集内部按实体窗口重新计算, 因此本列不会引入独立于 full 轨的新增文章行。is_soe 侧无差分 (国有属性判定与文本轨道无关, 是银行层面静态标签)。

在应用层面, 本列适合作为"报道中银行—金科关系本身的评价语气是否因所有权而分化"这一更聚焦研究问题的度量。相较全文轨可能混入的宏观背景、行业综述性段落, ctx 窗口把语调判定收窄到与目标银行、金科实体直接相关的句段, 因此在语义纯度上通常被认为优于全文轨, 但代价是窗口截取依赖实体识别的准确性, 若实体抽取存在漏检或误检, 窗口边界的抖动会引入额外测量噪声。使用本列做回归时, 应将其系数与 tone_x_soe_full、tone_x_soe_ss 两列并列报告在同一张稳健性表格中, 而非取代 full 轨作为唯一结果; 三者符号一致、显著性同向即可视为国有属性调节效应稳健, 出现方向分歧则需在文中讨论窗口口径差异可能的解释力, 而非简单取其一忽略另两者。

## VAR: tone_x_soe_full

【变体差分】
本列是家族 canonical 轨道, 取 `llm_vote_tone_full` (标题 + 正文全文语调, P1 主线 treatment 主轨) 与 `is_soe` 的逐行乘积。相较 ctx/ss 两条并排稳健性轨道, 本列语调来源覆盖整篇报道正文, 不做实体窗口或同句范围裁剪, 是三轨中信息覆盖面最宽、也是留篇门控判定 (`llm_verified_full`) 直接依附的轨道——ctx/ss 两轨的样本行宇宙均是本列样本行宇宙的子集 (conditional-on-full)。在 P1 (bank_fintech_tone) 论文主线中, `llm_vote_tone_full` 是处理变量 (treatment) 的主轨, 因此 tone_x_soe_full 通常作为异质性检验表格的首列 (headline) 结果呈现, ctx/ss 两列作为紧随其后的稳健性并排列, 三者仍应各自 just-identified 估计、不混入同一过度识别检验。

由于 full 轨覆盖整篇正文, 语调判定既受到与银行—金科关系直接相关的段落影响, 也可能受到同一篇报道中与主题弱相关的段落 (如行业背景铺垫、无关业务条线的并列陈述) 拉低或拉高整体语调分数, 因而 full 轨语调可以理解为对"整篇报道基调"的度量, 而非专门针对"银行—金科关系"评价语气的窄口径度量——这是它与 ctx/ss 两轨在构念上的关键区别, 也是三轨互为稳健性而非互相替代的根本原因。在国有 vs 非国有银行的异质性检验中, 若某类银行 (如国有大行) 恰好在报道中更多地与宏观政策、监管表态等背景性内容同篇出现, full 轨的整体语调可能比 ctx/ss 两轨更容易吸收此类背景信息, 分析者在解读 tone_x_soe_full 系数时应对此保持警觉, 并以 ctx/ss 两条并排轨道的结果作为交叉验证。

## VAR: tone_x_soe_ss

【变体差分】
本列取 `llm_vote_tone_ss` (标题 + 银行∧金科词严格同句共现窗口语调, 默认 ±1 句半径, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 与 `is_soe` 的逐行乘积, 是三轨中文本范围最窄、判定最严格的一支——只捕捉银行与金科实体在同一句子内共同出现时的语调评价, 排除报道中银行与金科分别独立出现、语义上未必存在直接关联的段落。回退语义镜像 ctx 轨: 若该行报道通过了 full-only 留篇门控但未检出银行∧金科同句共现, `ss_is_fallback` 标记为 True, 此时语调改用全文 body 重新计算 (与全文轨 tone_x_soe_full 的数值来源趋同, 但分母/分子的 n_articles 计数口径仍与 ctx 共享), 而非将该行语调置为缺失, 因此 tone_x_soe_ss 不因严格同句要求而产生系统性样本流失。作为与 full/ctx 并排的第三条互为稳健性轨道, 本列常用于检验"语调 × 国有属性"效应是否在最严格的语义关联判据下依然成立, 三轨结果的方向一致性构成对主结论稳健性的额外支撑, 但同样禁止与 full/ctx 混入同一 Hansen J 过度识别设定联合估计。

严格同句判据的实践意义在于最大限度压低"银行—金科关系"语调判定中的噪声: 只要一篇报道存在真正把目标银行与金科实体写进同一句话的段落 (例如某句直接评价该行金科合作项目的成效或风险), 本列语调就直接来自该句及其邻句, 排除了报道中可能存在的、与银行—金科关系无关的大段其他内容干扰。这使得 tone_x_soe_ss 在理论上最贴近"报道对该银行金科布局本身持何种态度"的构念, 但也因为判据严格, 在没有同句共现的报道占比较高的样本 (如金融科技报道多为泛泛而谈、银行与金科词分处不同段落) 中, 回退触发频率会显著高于 ctx 轨, 此时该列的边际增量信息会向 tone_x_soe_full 收敛。使用者在解读三轨系数差异时, 应结合 `ss_is_fallback` 的触发率一并报告, 以帮助判断严格同句轨的结果是主要由真实同句证据驱动, 还是较大比例上退化为全文轨的重复信息。另需说明: export.py 的 dta 标签映射目前仅为 tone_x_soe_full/_ctx 两列配置了可读标签, tone_x_soe_ss 未见对应标签行, 导出 Stata 数据集时该列沿用原始列名而非人工标签, 这是导出脚本的标签覆盖不对称, 不影响本列数值口径与计算逻辑本身。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, L.; Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Shapiro, A. H.; Sudhof, M.; Wilson, D. J. (2022). Measuring News Sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Fang, Y.; Wang, Q.; Wang, Y.; Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Loughran, T.; McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
<!-- rendered-citations:end -->
</content>
</invoke>
