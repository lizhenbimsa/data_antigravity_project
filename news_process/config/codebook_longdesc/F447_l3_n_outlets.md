---
family_id: F447
columns:
- n_outlets
unit: 篇数/计数 (count, 非负整数)
formula: 'nunique(媒体(中文)) over 该银行-年度内全部 fintech 文章 (extensive-margin outlet 计数; 详见下文两处产出路径的口径差异)'
producer: pipeline\audit\cross_media_alpha.py ; pipeline\panel\codebook.py
upstream:
- 12_news_fintech
- 21_tone_llms
citations:
- doi: 10.1111/j.1911-3846.2011.01125.x
  type: journal
  authors: Davis, A. K., & Tama-Sweet, I.
  year: 2012
  title: "Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A"
  venue: Contemporary Accounting Research
  vol: '29'
  issue: '3'
  pages_or_artno: 804-837
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media coverage and the cross-section of stock returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1080/19312450709336664
  type: journal
  authors: Hayes, A. F., & Krippendorff, K.
  year: 2007
  title: Answering the call for a standard reliability measure for coding data
  venue: Communication Methods and Measures
  vol: '1'
  issue: '1'
  pages_or_artno: 77-89
- doi: "10.1371/journal.pone.0315137"
  type: "journal"
  authors: "Ananyev, M., & Volkova, E."
  year: 2024
  title: "Media ownership and ideological slant: Evidence from Australian newspaper mergers"
  venue: "PLOS ONE"
  vol: "19"
  issue: "12"
  pages_or_artno: "e0315137"
- doi: "10.1016/j.frl.2024.105128"
  type: "journal"
  authors: "Zhang, Z., & Shen, D."
  year: 2024
  title: "Not all the news fitting to reprint: Evidence from price-volume relationship"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105128"
new_dois: []
---

## CORE

【构念与来源】
n_outlets 是一个诊断/覆盖度计数变量, 衡量某银行在某一年度全部 fintech 相关新闻报道中, 报道该银行的相异媒体来源(媒体(中文)字段)的去重个数(nunique)。它不是一个情感或语调测度, 而是刻画"这家银行的 fintech 报道被多少家不同媒体触达过"的曝光广度(coverage breadth)指标, 属于 extensive-margin 家族的辅助诊断列, 与情感三轨(full/ctx/ss)完全无关、也不参与任何 Hansen J 过度识别检验。它的直接学理源头是媒体覆盖(media coverage)文献: Fang & Peress (2009, Journal of Finance) 证明媒体覆盖广度本身(而非仅仅内容语调)会影响股票横截面收益, 是本项目 attention 族(n_fintech_articles/attention_pct/attention_disp 等)共同的 extensive coverage 主锚; Davis & Tama-Sweet (2012, Contemporary Accounting Research) 进一步指出管理层在不同披露渠道(press release vs. MD&A)间的语言策略存在系统性差异, 提示"媒体来源的异质性"本身是需要单独控制的结构性因素, 而不能假定所有 outlet 同质可替代——这正是 n_outlets 作为诊断列存在的方法学理由。

【方法学与计算】
计算原语是 pandas 的 nunique, 作用对象是"媒体(中文)"这一原始来源字段(而非任何情感衍生列), 计数范围限定在该 bank-year 的全部 fintech 文章子集上(与 attention 族 n_fintech_articles 共享同一行宇宙口径)。该家族在仓库内存在两处产出路径, 二者字面同名但计算语境不同, 使用前须留意: 其一是 `pipeline/panel/codebook.py` 中登记的面板级诊断列 n_outlets, 定义为 nunique(媒体(中文) over fintech 文章), 零-fintech 的 bank-year 记为 NaN(而非 0, 避免"无 fintech 报道"与"恰好只有 0 家媒体报道"混淆); 其二是 `pipeline/audit/cross_media_alpha.py`(验证阶段 stage 39f, thin shim 75_cross_media_alpha.py)在事件窗口(episode window, ±3d、按 bank 的 p90 峰值日合并重叠窗)内部计算的 outlet 计数, 用作 Krippendorff α 与跨媒体方差(cross_outlet_tone_variance)的可算性前提(要求窗内 outlet 数≥2 才纳入)——这一事件窗版本是"条件子样本"意义下的中间量, 与本条目登记于面板并对外发布的 n_outlets(全年无条件截面计数)是两个不同粒度的量, 不可互相替代或混用于同一回归设定。本条目对应的是后者, 即面板级、全年无条件的 outlet 计数诊断列。该列本身不涉及三轨切分(full/ctx/ss)、不涉及 co-primary 双轨嵌入、也不涉及任何权重或阈值梯子, 是一个 track-agnostic 的单一计数列; 若未来该口径衍生出按轨切分的变体, 各轨版本之间将各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 设定, 但截至当前版本尚无此需求。

【文献定位】
n_outlets 的方法学定位紧邻 attention/coverage 一支文献, 而非情感测度一支。CLAUDE.md「当前状态铁律」记载的 ATTN CV-2 构念效度披露明确指出: outlet-HHI(注意力分散度 attention_disp)在低覆盖 bank-year 会机械地退化为 1(单一 outlet → HHI=1), 混淆了"集中度"本身与"覆盖量过低"这两个不同构念; 而 n_outlets 正是用来诊断并纠正这一混淆的配套变量——回归中若要使用 attention_disp 作为解释变量, 必须同时控制 ln(n_outlets) 或将样本限定在 n_outlets≥3 的子样本, 否则 disp 系数吸收的实际上是覆盖广度信息而非真实的媒体集中度信息。这一构念区分同样呼应 Fang & Peress (2009) 对"覆盖广度"本身独立信息含量的强调: 观察到的分歧或集中度指标, 必须先排除"样本覆盖太窄导致的机械性"这一混杂因素, 才能被解读为真实的行为或市场信号, 而非单纯的样本量伪相关。Hayes & Krippendorff (2007) 提供的可靠性测度框架进一步说明, 跨评分员(此处即跨媒体来源)一致性指标(如 α)本身需要足够数量的"评分员"(即 outlet)才具统计意义, n_outlets 因此也是 stage 39f 跨媒体一致性诊断(G-D3.1: valid bank-event 覆盖率是否≥60%)的前置可算性门槛变量。综上, n_outlets 在本项目中扮演的角色是"覆盖广度诊断锚", 供 attention 族与跨媒体分歧族在回归设计阶段做样本筛选与构念澄清之用, 本身不作为任何论文的主处理变量(treatment)或结果变量(outcome)。 晚近证据从两个方向补强了这一诊断定位。Ananyev 与 Volkova (2024) 利用 2016-2019 年三起澳大利亚报业并购、以逾三千万篇报道构建 slant 测度并以合成双重差分识别, 证明媒体所有权变更会因果性地改变报纸的政治 slant, 即 outlet 身份本身系统性地塑造内容、各家媒体不可被视作同质可替代——这正是 n_outlets 需要与文章篇数分列而非被后者吸收的前提; 惟该文情境为澳大利亚报业与私人资本集中度, slant 以政治意识形态量表度量, 层级为报纸-时期而无主体-年面板, 亦未构造任何去重来源家数计数, 故仅锚定「来源异质」这一前提, 不锚本列公式。Zhang 与 Shen (2024) 把新闻明确区分为转载/再刊与非转载两类并证明二者市场含义不同, 提示相异 outlet 计数会同时容纳原创产制与二次分发两种情形, 解读 n_outlets 时宜与 wire_frac / staff_written_frac 等原创性列合看; 该文的转载判定依赖新闻数据库自带标记, 与本项目基于作者字段与电头关键词的规则判据不同, 且分析停在文章级、以价量关系为 DV, 未做任何主体-年度的来源去重计数。
## VAR: n_outlets

【变体差分】
n_outlets 是本家族(F447)在 standard tier 下唯一登记的列, 因此本节说明的重点不是与家族内其他列的差异, 而是精确界定它自身的口径边界, 以防与仓库内两处同名/近名产出混淆。第一, 计算范围是"该银行-年度全部 fintech 文章"这一子集, 与 n_fintech_articles(extensive-margin baseline 计数, 同样 track-agnostic)共享相同的行宇宙定义, 但 n_outlets 计的是相异媒体来源数(nunique), 而 n_fintech_articles 计的是文章篇数(count), 二者不可相互替代——同一家银行可能只有 5 篇 fintech 报道却分散在 5 家不同媒体(n_outlets=5), 也可能有 50 篇报道却集中在 2 家媒体(n_outlets=2), 两种情形对应完全不同的媒体结构含义。第二, 缺失值语义: 该 bank-year 若没有任何 fintech 文章(n_fintech_articles=0), n_outlets 记为 NaN 而非 0, 这一处理与 attention_pct/attention_disp 等同族诊断列保持一致的"零分母不可算"约定, 使用者不应把 NaN 误当作"0 家媒体报道"来做填补或均值插补, 否则会人为压低覆盖广度的真实分布。第三, 与 stage 39f `cross_media_alpha.py` 内部按事件窗(episode window, ±3d 合并峰值日)计算的同名局部 outlet 计数严格区分: 后者是计算 Krippendorff α 与跨媒体方差(cross_outlet_tone_variance_{full,ctx,ss})时的中间可算性门槛(窗内 outlet 数需≥2 才纳入该 episode), 属于事件窗条件子样本口径, 而本列是全年无条件的面板级诊断列, 二者数值一般不相等, 也不应在同一张回归表中被误当作同一变量互换使用。第四, 该列本身不区分 full/ctx/ss 三轨(它统计的是原始"媒体(中文)"来源字段, 与情感文本窗口口径无关), 也不涉及任何嵌入向量或 LLM/BERT 模型选择, 是纯计数型、来源无关(source-field-only)的诊断列, 使用时不需要考虑三轨并排或 co-primary 双轨嵌入的稳健性排列问题, 但在与 attention_disp 联合使用时, 仍需遵循 ATTN CV-2 披露的建议——将其作为控制变量或子样本筛选依据, 而非直接的处理/结果变量纳入主回归设定。

<!-- rendered-citations:begin -->
Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A. Contemporary Accounting Research, 29(3), 804-837. https://doi.org/10.1111/j.1911-3846.2011.01125.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
Ananyev, M., & Volkova, E. (2024). Media ownership and ideological slant: Evidence from Australian newspaper mergers. PLOS ONE, 19(12), e0315137. https://doi.org/10.1371/journal.pone.0315137
Zhang, Z., & Shen, D. (2024). Not all the news fitting to reprint: Evidence from price-volume relationship. Finance Research Letters, 62, 105128. https://doi.org/10.1016/j.frl.2024.105128
<!-- rendered-citations:end -->
</content>
