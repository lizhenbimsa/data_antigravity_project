---
family_id: F596
columns:
- tone_x_highcov_ctx
- tone_x_highcov_full
- tone_x_highcov_ss
unit: 交互项得分 (连续, 理论范围约 [-1,1]; 语调 × 0/1 高覆盖哑变量, 无覆盖行为 NaN)
formula: 'tone_x_highcov{track} = llm_vote_tone{track} * high_coverage, track ∈ {_full, _ctx, _ss}; high_coverage 由 _base_year_median_split(panel, value_col=n_articles, by=None) 在面板最早年 (基年) 对 n_articles 取中位数一次性切分并跨年固定 (predetermined split, 不随年内报道量翻转)'
producer: pipeline\panel\runner.py (high_coverage 基年固定切分 L1588-1593, 交互项赋值循环 L1595-1604, tone_x_highcov{track} 具体赋值 L1603; _base_year_median_split 函数定义 L255-284) ; pipeline\panel\export.py (tone_x_highcov_full/_ctx 手写标签 L909-910; tone_x_highcov_ss 由 L1451-1455 处 '_ctx→_ss' 机械派生逻辑生成, 非独立手写条目)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
- n_articles
- high_coverage
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L. H., & Peress, J.
  year: 2009
  title: Media coverage and the cross-section of stock returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: "10.1111/abac.12322"
  type: "journal"
  authors: "Wang, K. T., Zhu, N. Z., & Luo, G."
  year: 2024
  title: "Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China"
  venue: "Abacus"
  vol: "60"
  issue: "4"
  pages_or_artno: "709-751"
new_dois: []
---

## CORE

【构念与来源】
本家族的三列 (tone_x_highcov_full/_ctx/_ss) 是「银行-金科语调 × 高媒体覆盖」的调节效应交互项, 用于检验媒体报道语调对银行结果变量的影响是否随媒体关注强度的高低而呈现非线性/异质性。构念上它回答的问题不是"语调本身有多正/负", 而是"在高关注度环境下, 语调每单位变化带来的边际效应是否与低关注度环境不同", 对应 Fang & Peress (2009, Journal of Finance) 关于媒体覆盖边际效应递减、需要按覆盖强度分组检验的核心发现——该文用 t 期覆盖排序预测 t+1 收益 (predetermined sort), 本交互项在设计上刻意对齐这一"基于前定分组、避免同期内生"的识别逻辑。交互项本身不是独立测度, 而是异质性分析框架 (Angrist & Pischke 2009 的思路; Brambor, Clark & Golder 2006 的交互项解读规范) 里 tone × 分组哑变量族 (tone_x_soe / tone_x_scale / tone_x_highcov / tone_x_stress / tone_x_depins) 中的一支。

高覆盖哑变量 high_coverage 由 _base_year_median_split 在面板最早基年 (panel['year'].min()) 对 n_articles 取一次性中位数切分, 并将该组员资格跨全部年份固定不变——这是一处经过修正的设计决策 (fix(omni-g-runner-13, 2026-06-11)): 旧实现按同年中位数切分 (含自身观测), 导致组员资格随内生的年度报道量逐年翻转 (盘上观测到 87 家银行中有 20 家跨年翻转组别), 与同年语调相乘后, 调节变量与结果变量处于完全同期、互为因果的内生环境。现行实现改为基年固定切分, 使 high_coverage 满足前定 (predetermined) 条件, 与 Fang & Peress (2009) 的排序时序对齐, 避免调节变量本身被同期语调或报道量反向影响。生产口径上 high_coverage 对全部年份的同一家银行取值恒定 (0 或 1), 交互项的年度变异全部来自 llm_vote_tone{track} 一侧。

原始设计说明文档还特别指出一处冗余陷阱: has_coverage (0/1 是否有报道) 与 tone 的交互项本身不携带增量信息——零新闻行 tone=NaN, 故 tone×has_coverage 恒为 NaN 而非 0; 有新闻行 has_coverage=1, tone×1 退化为 tone 本身。high_coverage 与 has_coverage 不同: 前者是仅在"有报道的银行子样本"内部再按报道量中位数二次切分的高/低覆盖强度分组 (而非有/无报道的二元哑变量), 因此 tone_x_highcov 不会退化为 tone 本身, 携带的是"语调效应在高关注度组是否被放大或压缩"的边际信息, 这正是本交互项族存在的意义。

【方法学与计算】
三列的生成逻辑完全并列于同一循环 (runner.py L1577-1584): 对 track ∈ {_full, _ctx, _ss} 依次取 llm_vote_tone{track}, 若该列在面板中存在则计算 tone_x_highcov{track} = llm_vote_tone{track} * panel['high_coverage']; 若某轨的 llm_vote_tone{track} 不存在 (例如上游门控导致该轨缺失) 则整轨跳过, 不补 0 不插值。high_coverage 是标量层面 (逐银行固定) 的 0/1 哑变量, 乘子层面看交互项的缺失模式完全继承 llm_vote_tone{track} 自身的缺失模式——凡语调为 NaN (该轨该行无有效留篇观测) 的行, 交互项亦为 NaN, 不因 high_coverage 有定义而被误"补全"为 0。

llm_vote_tone_full 是三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票共识的 canonical 情感测度, 留篇门控口径为 full-only (2026-06-29 铁律): 一篇文章是否计入某年该银行的"有效报道", 只看 llm_vote_tone_full 所在的 llm_verified_full 判定; ctx/ss 两轨降级为 full 留篇集合内的 conditional-on-full 测度/稳健性轨, 其行宇宙是 full 集合的子集, 但 per-track 列 (含情感值本身与本交互项) 仍照各自轨道独立计算。ss 轨在"银行∧金科同句"无共现命中时回退为全文 body (content_ss=全文, ss_is_fallback=True), 该回退语义严格镜像 ctx 轨的回退规则, 共享 n_articles 分母口径。三轨 full/ctx/ss 在计量设计上各自 just-identified 并排、互为稳健性、不分主次——本交互项族继承这一铁律: 三条 tone_x_highcov{track} 严禁混入同一个 over-identified Hansen J 检验的工具变量集或联合矩条件, 只应各自独立地作为一条稳健性平行证据线出现在回归表的不同列/不同 panel 中。

需要强调的一点区分是: high_coverage 的分组本身与三轨无关——它只依赖 n_articles (面板层面的年度报道条数), 与是否采用 full/ctx/ss 哪一种文本口径无关, 因此三条交互项列共享同一个 high_coverage 哑变量, 差异全部来自分子侧 llm_vote_tone 的轨道选择, 不存在 high_coverage 本身的三轨版本。

【文献定位】
异质性交互项设计遵循标准的调节效应回归规范 (Angrist & Pischke, 2009; Brambor et al., 2006): 系数解读须结合低阶项 (llm_vote_tone{track} 与 high_coverage 的主效应) 一并纳入模型, 交互项系数捕捉的是语调边际效应在高覆盖组相对低覆盖组的增量差异, 而非高覆盖组本身的语调水平差异。前定分组设计直接对齐 Fang & Peress (2009, The Journal of Finance) 关于媒体覆盖边际递减、需按覆盖强度 (而非单纯有无报道) 分组检验的实证发现, 该文用基期覆盖排序预测后续收益的思路是本交互项族基年固定切分的直接方法论来源。语调测度本身 (被交互的另一侧) 承袭 Tetlock (2007, Journal of Finance) 开创的"媒体语调作为可计量投资者情绪信号"的文本分析传统。在中国银行业媒体情感与系统性风险/储户纪律的具体场景, Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 提供了同域实证参照, 用中国银行层面媒体情感数据检验存款稳定性与系统性风险的关系, 与本项目银行-金科语调 × 覆盖强度框架高度可比。语调测度的语言学基础方法论进一步参照 Du, Huang, Wermers & Wu (2022, Review of Finance) 关于中文金融情感词典的领域特异性研究, 该文是本项目情感测度体系中词典法轨道 (与三家 LLM 投票并行) 的方法学锚点之一, 说明中文语境下情感词的语义强度与英文金融文本存在系统性差异, 佐证了本项目坚持采用中文原生 LLM/词典双轨而非直接套用英文金融情感词表的必要性。 在覆盖强度一侧的测度合法性上, Wang、Zhu 与 Luo (2024) 以逾 188,000 篇出自中国最具影响力报纸、由记者撰写的公司特定报道, 按公司-年归集为报道量计数型暴露变量并检验其对企业创新产出的影响, 为本族 high_coverage 赖以切分的 n_articles (中文报纸报道条数按主体-年计数) 作为文本暴露变量提供了近期同语种实证先例。迁移边界须诚实标明: 该文主体为中国 A 股非金融企业而非商业银行, 其被解释变量是产出侧的创新指标, 且未见其构造任何语调/情感变量 — 因此它只锚定本交互项的覆盖量一侧, 对分子侧 llm_vote_tone{track} 的极性来源不提供任何依据, 亦无三轨文本设计可资对照。
## VAR: tone_x_highcov_ctx

【变体差分】
本列取 llm_vote_tone_ctx (标题 + 实体窗口文本轨的三家 LLM 投票语调) 与 high_coverage 的交互项。行宇宙受 full-only 留篇门控约束: 只在 llm_verified_full == True 的报道范围内计算 (2026-06-29 铁律), 即 ctx 轨是在 full 留篇集合子集上的 conditional-on-full 稳健性测度, 而非独立留篇标准下的平行样本——一篇报道是否算作"该银行该年的一篇有效银行-金科报道", 只看 full 轨的 llm_verified_full 判定, ctx 轨不单独门控留篇, 只在 full 已确认的样本内部提供文本口径切换的平行证据。ctx 轨文本本身在 stage 14 物化 (content_ctx = 标题 prepend + 实体窗口正文, ctx_is_fallback 标记无目标银行/金科实体窗口命中时回退为全文正文, 与 ss 轨回退规则同构但触发条件不同——ctx 只要求实体出现在窗口内, 不要求银行与金科词同句)。若 llm_vote_tone_ctx 在面板中缺失 (例如该轨上游流水线未产出或被跳过), 本列在 runner.py 交互项生成循环里整体跳过不生成, 不会以 0 值或借用 full 轨数值做静默填补, 避免制造虚假的完整覆盖假象。本列与 tone_x_highcov_full / tone_x_highcov_ss 是并排的稳健性轨道关系, 三者共享同一个基年固定、跨年不变的 high_coverage 哑变量分组, 差异只体现在语调测度分子一侧所依赖的文本窗口宽度上 (标题+实体窗口 vs 标题+全文 vs 标题+同句共现窗口), 高覆盖分组本身与文本轨道选择无关。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定中联合估计工具变量或矩条件; 在回归表呈现上, ctx 轨系数与 full 轨系数应作为独立稳健性行并列报告, 而非取二者均值或以其中一者裁决另一者。

## VAR: tone_x_highcov_full

【变体差分】
本列取 llm_vote_tone_full (标题 + 全文正文轨的三家 LLM 投票语调共识) 与 high_coverage 的交互项, 是本家族在留篇门控意义上的 canonical / 主测度轨: llm_vote_tone_full 承担留篇门控角色 (llm_verified_full 判定是否计入"一篇有效银行-金科报道"的唯一标准, 2026-06-29 铁律), 因此本列的行宇宙即为该口径下的全集, ctx/ss 两列均是本列行宇宙的子集稳健性版本, 不存在超出 full 集合之外的额外观测。P1 (bank_fintech_tone) 论文主轨处理变量 treatment.primary = llm_vote_tone_full 即是本交互项的分子来源, 使得 tone_x_highcov_full 天然对齐主回归设定里的处理变量口径与识别策略假设, 是异质性/调节效应分析表中理应首先呈现的版本, 因其分子测度与主效应回归共享同一处理变量、系数解读最直接衔接主结果的经济含义。但在"互为稳健性、不分主次"的三轨铁律下, full 轨本身在计量地位上仍需与 ctx/ss 并列报告而非单独视为"正确答案"或用以裁决另外两轨——三轨差异反映的是文本窗口宽度对语调测度噪声与遗漏变量偏误的不同权衡 (full 轨信息量最大但可能混入与目标银行无关的段落噪声, ctx/ss 轨窗口更聚焦但存在实体识别/共现判定的自身误差), 结论的稳健性应以三轨系数方向与显著性是否一致来判断, 而非仅报告 full 轨结果。high_coverage 分组本身在三列中完全一致, 均来自同一基年固定切分, 不因文本轨道不同而重新计算。

## VAR: tone_x_highcov_ss

【变体差分】
本列取 llm_vote_tone_ss (标题 + 银行∧金科同句 ±N 窗口文本轨的三家 LLM 投票语调) 与 high_coverage 的交互项。ss 轨的判定口径比 ctx 更严格: 只在同一句子内同时出现目标银行实体与金科词才纳入窗口正文 (窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句), 判定不对称 (银行侧走否定+短名过滤规则, 金科侧走裸 AC 自动机 607 词表匹配, 不做否定翻转或短名过滤)。当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True——该回退语义严格镜像 ctx 轨的回退规则 (无实体窗口命中时同样回退全文), 与 ctx 轨共享同一个 n_articles 分母口径, 保证跨轨的样本规模统计口径一致、便于横向比较缺失率。行宇宙同样受 full-only 门控约束: llm_verified_full 才是判定"该银行该年有效报道"的唯一标准, ss 轨是 full 留篇集合内的条件稳健性轨, 而非按自身共现判据独立筛选留篇的平行样本, 这意味着即便某行在 ss 轨判定为回退 (无同句共现), 只要其 full 轨已通过留篇门控, 该行依然会出现在本列的行宇宙中并参与交互项计算。若 llm_vote_tone_ss 在面板中缺失, 本列在交互项生成循环中整体跳过, 不做借用其余轨道数值的填补。本列与 tone_x_highcov_full / tone_x_highcov_ctx 三者并排、互为稳健性、共享同一个基年固定的 high_coverage 分组, 差异仅体现在分子一侧的共现判据严格程度上; 三轨严禁混入同一 over-identified Hansen J 设定联合估计, 应作为独立并列的稳健性检验行分别呈现于回归表中。本列的 Stata 变量标签与 full/ctx 两列的生成方式不同: full/ctx 标签在 export.py 中逐条手写, 而 ss 标签是由一段独立的机械派生逻辑生成——该逻辑遍历所有以 _ctx 结尾的已知标签, 将变量名中的 _ctx 替换为 _ss、文案中的 Ctx 替换为 SS, 自动产出对应的 ss 标签, 不存在与 full/ctx 并列的手写条目, 但标签文案与命名规则与手写条目保持一致, 不影响读者对该列含义的理解。

<!-- rendered-citations:begin -->
Fang, L. H., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Wang, K. T., Zhu, N. Z., & Luo, G. (2024). Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China. Abacus, 60(4), 709-751. https://doi.org/10.1111/abac.12322
<!-- rendered-citations:end -->
</content>
