---
family_id: F599
columns:
- tone_x_stress_ctx
- tone_x_stress_full
- tone_x_stress_ss
unit: 交互项得分 (连续, 情感语调 × 0/1 压力期哑元, 理论域近似 [-1,1]; bank-year 面板行)
formula: 'tone_x_stress{track} = llm_vote_tone{track} * stress_period, 其中 stress_period = 1{year ∈ {2015, 2018, 2020}}, track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\runner.py (交互项生成, 三轨循环) ; pipeline\panel\export.py (Stata 变量标签映射, 经核实仅覆盖 tone_x_stress_full/tone_x_stress_ctx 两列, tone_x_stress_ss 无对应标签映射条目)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
- stress_period
citations:
- doi: 10.1111/jofi.70034
  type: journal
  authors: Drechsler, I., Savov, A., Schnabl, P., & Wang, O.
  year: 2026
  title: Deposit Franchise Runs
  venue: The Journal of Finance
  vol: '81'
  issue: '3'
  pages_or_artno: 1573-1617
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: 'Beyond the headlines: Sentiment divergence and financial distress'
  venue: Global Finance Journal
  vol: '66'
  pages_or_artno: Article 101126
- doi: 10.1093/rfs/hhu072
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2015
  title: The sum of all FEARS investor sentiment and asset prices
  venue: The Review of Financial Studies
  vol: '28'
  issue: '1'
  pages_or_artno: 1-32
new_dois: []
---

## CORE

【构念与来源】
本家族刻画"银行金融科技报道语调"与"宏观/行业压力期"之间的交互效应, 用于检验情感测度对负面公共事件的非对称响应假设。三个列共享同一构造公式: 逐轨 LLM 投票共识语调 `llm_vote_tone{track}` 乘以压力期哑元 `stress_period`, 其中 `stress_period` 由 `panel['year'].isin({2015, 2018, 2020}).astype(int)` 生成 (`pipeline/panel/runner.py`)。三个锚定年份对应 2015 年 A 股股灾及汇改冲击、2018 年资管新规去杠杆、2020 年新冠疫情初期银行体系流动性与资产质量压力, 均为公开可查、非银行个体特质的系统性压力事件, 因此 `stress_period` 是纯时间维度的确定性哑元, 不因银行个体而异, 也不构成处理组/对照组划分 (区别于双重差分设计)。交互项本身不改变语调的符号或量纲, 只是在压力年将语调值原样保留, 在常规年将其置零, 数学上等价于"压力年子样本的语调"这一分段变量, 便于在含 bank-year 面板固定效应的回归中直接以单一回归系数估计压力期语调效应对结果变量 (如融资成本、存款稳定性、股价波动) 的边际调节作用, 无需额外拆分样本或分层回归。
本家族的理论动机源于金融文本情感文献中一个反复被证实的现象: 情感信息在市场承压/危机时期的定价效力与常规时期存在系统性差异, 且压力期本身往往由存款/流动性冲击这一具体渠道驱动。Drechsler, Savov, Schnabl & Wang (2026, Journal of Finance) 系统刻画了存款特许权在利率/流动性冲击下的"挤兑"动态, 说明压力事件对银行体系的冲击并非均匀分布于全部年份, 而是集中于若干可识别的系统性压力窗口, 为本家族"压力年离散哑元"而非连续压力指数的建模选择提供了机制层面的支持 (三个锚定年份中 2015、2018、2020 均伴随不同程度的银行体系流动性/资产质量压力, 与该文讨论的存款特许权承压渠道相呼应)。Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 在中国银行业场景下进一步论证媒体情感对存款稳定性与系统性风险的影响存在压力期放大效应, 与本项目"银行×金融科技报道语调"的研究对象高度贴近, 是构念层面最切题的同域文献。Garcia (2025, Global Finance Journal) 与 Da, Engelberg & Gao (2015, Review of Financial Studies) 分别从情感分歧度与恐慌指数角度补充说明危机/压力时期情感信号的统计特征 (方差、持久性、跨来源分歧) 系统性偏离常规期, 为"压力期需要单独估计交互效应而非假设常数效应"提供跨市场证据。
本家族与家族 `tone_x_soe`(所有制异质性)、`tone_x_scale`(规模异质性)、`tone_x_highcov`(媒体覆盖度异质性)、`tone_x_depins`(存款保险制度断点)共享同一批 `Angrist & Pischke (2009)` / `Brambor, Clark & Golder (2006)` 交互项设计传统 (源码注释标注), 均以 `llm_vote_tone{track}` 为被交互的核心语调测度, 区别仅在于第二个调节因子。本家族的调节因子 `stress_period` 是时间断点型而非个体截面型 (与 `tone_x_soe`/`tone_x_scale` 的银行属性型调节因子形成对照), 也与 `tone_x_depins` 的单一时间断点(2015 年存款保险条例实施)不同 —— 后者是单向永久断点 (`year >= 2015`), 而 `stress_period` 是离散多点脉冲型(仅 2015/2018/2020 三个孤立年份为 1, 其余年份含 2016/2017/2019/2021 等均为 0), 二者构念不可混同, 亦不应放入同一 over-identified 设定联合估计, 因两者对同一批年份 (尤其 2015/2018/2020 均 ≥2015) 存在机械共线性。

【方法学与计算】
`llm_vote_tone{track}` 是三家大语言模型 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 逐篇多数投票产生的共识语调测度 (取值离散映射到 [-1, 1] 区间的连续聚合均值), 在 stage 21 情感 LLM 环节产出, 并按 bank-year 聚合进入面板。`stress_period` 是纯 `panel['year']` 派生的静态哑元, 与语调测度本身的计算过程完全解耦, 因此交互项的所有跨轨/跨模型稳健性均直接继承自 `llm_vote_tone{track}` 本身的稳健性梯子, 不产生新的测量误差来源。三轨 (full/ctx/ss) 循环在 `pipeline/panel/runner.py` 内以统一 for 循环实现 (`for track in ['_full', '_ctx', '_ss']`), 逐轨检查 `llm_vote_tone{track}` 列是否存在于面板中, 存在则生成同轨交互列, 三轨互不依赖、互不覆盖。需特别注意: 本项目的留篇门控口径 (2026-06-29 起) 为 full-only —— 一篇报道是否计入"银行-金融科技"报道样本, 只由 `llm_verified_full == True` 判定; ctx/ss 两轨在此口径下降级为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集, 但每轨各自独立计算语调值与交互项。三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一个 over-identified Hansen J 检验。ss 轨的文本回退语义镜像 ctx 轨: 当某篇报道不存在银行∧金融科技词汇同句共现时, `content_ss` 回退为全文正文 (`ss_is_fallback=True`), 该回退口径不改变 `tone_x_stress_ss` 的构造公式, 只影响上游 `llm_vote_tone_ss` 本身的样本构成。
`stress_period` 盘上处于 T=2 (2017、2018) 开发样本时表现为几乎恒定的稀疏哑元 (仅 2018 年触发, 2017 年为 0), 交互项在此样本规模下识别力天然受限; 生产语料 T=18 (2007–2024) 完整覆盖三个压力年份及其邻近常规年份后, 交互项才具备充分的组内时间变异用于识别压力期非对称效应。

【文献定位】
本家族的构造思路借鉴 Drechsler et al. (2026) 揭示的存款特许权承压渠道, 并结合 Fang et al. (2024) 在中国银行业场景下的媒体情感-压力期交互设计, 将其迁移到"银行×金融科技"报道语调这一细分构念上。Garcia (2025) 与 Da, Engelberg & Gao (2015) 进一步佐证危机/压力时期情感信号的分布特征 (分歧度、持久性) 与常规期存在系统性差异, 支持将压力期单独设定交互项而非假设常数边际效应的建模选择。三个压力年份的锚定 (2015 股灾去杠杆前夕、2018 资管新规去杠杆、2020 疫情冲击) 均为中国银行体系历史上公认的系统性压力事件, 定义来源为 `pipeline/panel/runner.py` 中 `STRESS_YEARS = {2015, 2018, 2020}` 的显式硬编码常量 (源码行内注释标注"股灾、去杠杆、疫情")。经核实, `51_falsification_test.py` 为 thin shim, 其真实逻辑委托给 `pipeline/falsification/controls.py`, 该文件当前并不含独立的压力年份常量或 `stress_period` 派生逻辑, 因此本家族无法声称与该验证脚本存在可验证的跨脚本口径对齐; `stress_period` 的唯一权威定义即 `pipeline/panel/runner.py` 本处常量, 后续若 `pipeline/falsification/controls.py` 补入同名压力年份定义, 应另行核实两处取值是否一致, 而非默认继承。
经同等核实, `pipeline/panel/export.py` 内负责 Stata 变量标签映射的字典条目, 实读仅含 `tone_x_stress_full` 与 `tone_x_stress_ctx` 两条, 缺 `tone_x_stress_ss` 对应条目; 该列在导出 `.dta` 时因此不带专属英文变量标签 (退化为默认标签或沿用字段名本身), 与 full/ctx 两轨在 Stata 端的可读性存在实际差异, 但不影响该列在面板 parquet 层的数值构造与三轨并排的稳健性关系, 使用者在读取 `.dta` 变量标签时应留意此缺口, 不应默认三列标签映射对称完整。

## VAR: tone_x_stress_full

【变体差分】
本列是家族 canonical 轨, 以 full 轨情感测度 `llm_vote_tone_full` (标题+正文全文, 留篇门控唯一判定轨) 与 `stress_period` 相乘。因 full 轨是本项目留篇门控口径下唯一决定"是否计入银行-金融科技报道样本"的轨道, `tone_x_stress_full` 的行宇宙即为面板全体 bank-year 观测 (受 `llm_vote_tone_full` 缺失值影响时随之缺失, 无额外筛选)。该列是本交互项族的主测度 (primary), 在下游回归模板中作为默认解释变量出现; ctx/ss 两轨作为并列的稳健性轨, 三者互不隶属, 不构成主/次关系, 只是行宇宙覆盖范围与文本窗口不同。计算时机上, `stress_period` 先于三轨交互项循环单独生成一次 (非逐轨重算), 因此三列共享完全相同的压力期哑元取值, 差异只来自分子 `llm_vote_tone{track}` 本身。
从解释角度看, 该列的系数在一个含银行固定效应与年份固定效应的双向固定效应回归中, 度量的是"压力年相对常规年, full 轨语调对结果变量边际影响的额外增量", 而非语调本身的主效应 (主效应已被 `llm_vote_tone_full` 单独一列吸收, 两列在同一回归方程中通常同时出现以满足低阶交互项完整性要求, 详见 `pipeline/panel/runner.py` 中对 Wooldridge (2010) §10.4 三重差分完整低阶项要求的注释引用, 同一逻辑适用于二阶交互)。由于 full 轨是留篇门控口径, 该列的样本量在三轨中理论上最大, 也因此是稳健性梯子中最贴近论文正文汇报口径的一支; ctx/ss 更适合用于展示"结论对文本窗口选择的敏感性"这一附加检验, 而非替代 full 轨本身的解释力。使用者在解读该列回归系数时, 应同时报告 `stress_period` 单独项与 `llm_vote_tone_full` 单独项的系数, 避免遗漏低阶项导致交互系数含义漂移。

## VAR: tone_x_stress_ctx

【变体差分】
本列以 ctx 轨情感测度 `llm_vote_tone_ctx` (标题+实体窗口, 而非全文) 与 `stress_period` 相乘。在 2026-06-29 起生效的 full-only 留篇门控口径下, ctx 轨降级为 conditional-on-full 的稳健性测度: 其行宇宙是 full 轨留篇集合的子集, 语调计算窗口收窄为围绕目标银行与金融科技实体的局部文本片段, 用于检验语调交互效应是否对"全文 vs. 局部实体窗口"的文本粒度选择敏感。该列与 `tone_x_stress_full` 共享同一份 `stress_period` 取值, 二者在压力期定义上完全一致, 唯一差异是分子语调测度的文本来源窗口。与 `tone_x_stress_full` 及 `tone_x_stress_ss` 三者各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 联合估计。
ctx 轨的实体窗口构造逻辑在 stage 14 `ctx_materializer` 完成, 只截取围绕目标银行与金融科技实体的局部段落 (而非全文), 目的是排除同一篇报道中与银行-金融科技关系无关的段落对语调测度的稀释效应; 该设计假设是"局部实体窗口的语调信号更纯净、噪声更小", 但代价是样本量与文本上下文完整性均有所损失。在压力期解读上, ctx 轨交互项检验的问题是: "当压力事件发生时, 报道正文中围绕银行本身的局部语调 (而非泛泛而谈的宏观段落) 是否呈现出与 full 轨一致方向、一致显著性的非对称响应"。若 full 轨与 ctx 轨系数方向一致但显著性有差异, 通常提示效应主要由报道中的宏观/行业背景段落驱动而非银行自身局部语调驱动, 这本身即是一项有信息量的稳健性发现, 而非某一轨"更对"某一轨"更错"。

## VAR: tone_x_stress_ss

【变体差分】
本列以 ss 轨情感测度 `llm_vote_tone_ss` (标题+"银行∧金融科技"同句±N窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 与 `stress_period` 相乘, 是三轨中文本窗口最窄、判定最严格的一支。ss 轨的回退语义镜像 ctx 轨: 当某篇报道内不存在银行与金融科技词汇的同句共现时, 其底层 `content_ss` 回退为全文正文并置 `ss_is_fallback=True`, 该回退共享与 ctx 轨相同的分母口径 (`n_articles`), 但不改变本列的交互公式本身, 仍是 `llm_vote_tone_ss * stress_period`。与 full/ctx 两轨同样作为并列稳健性轨存在, 三者行宇宙均受各自上游语调列缺失值约束 (ss 轨因回退逻辑通常缺失率与 ctx 轨相近, 但两者独立计算、互不借用对方分母)。同样适用三轨互为稳健性、禁混同一 Hansen J 的铁律。
ss 轨判定采用不对称口径: 银行侧需经否定词过滤与短名过滤, 金融科技侧则用裸 Aho-Corasick 1506 词表命中即可, 该判定不对称性是全项目三轨架构的既定设计 (非本家族独有), 目的是在保证金融科技相关性召回的同时控制银行实体误配率。对本列而言, 判定不对称意味着 `llm_vote_tone_ss` 的样本构成 (哪些报道被判定为"同句共现") 本身即带有一定的召回/精确率权衡, 使用者在将该列结果与 full/ctx 轨对照时, 应把"同句共现判定的严格程度差异"作为潜在的解释因素之一, 而不仅仅归因于语调测度的信息含量差异。由于压力期 (2015/2018/2020) 涉及的报道往往篇幅更长、段落更多, 银行与金融科技词汇同句共现的概率相对更低, 因此 `tone_x_stress_ss` 在压力年份的缺失率或回退率可能高于常规年份, 解读该列压力期系数时应留意此结构性差异。

<!-- rendered-citations:begin -->
Drechsler, I., Savov, A., Schnabl, P., & Wang, O. (2026). Deposit Franchise Runs. The Journal of Finance, 81(3), 1573-1617. https://doi.org/10.1111/jofi.70034
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Da, Z., Engelberg, J., & Gao, P. (2015). The sum of all FEARS investor sentiment and asset prices. The Review of Financial Studies, 28(1), 1-32. https://doi.org/10.1093/rfs/hhu072
<!-- rendered-citations:end -->
</content>
