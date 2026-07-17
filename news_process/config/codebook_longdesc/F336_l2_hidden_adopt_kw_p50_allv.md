---
family_id: F336
columns:
- hidden_adopt_kw_p50_allv
- hidden_adopt_kw_p50_allv_ctx
- hidden_adopt_kw_p50_allv_ss
unit: 银行-年内篇均占比 (0-1 之间的比例, 分母=该银行-年内已测量 sim 与 freq 均非缺失的报道篇数)
formula: 'bank-year 层聚合 mean(_is_hidden), 其中逐篇指示 _is_hidden = 1{词频列 < 年度 P50 分位数} AND 1{相似度列 >= 年度 P50 分位数}, 仅对 sim 与 freq 双双非缺失的行分类, 未测量行记 NaN (groupby mean 自动跳过, 不进分母)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (逐篇象限分类) + 同文件象限循环 (bank-year 聚合)
upstream:
- pipeline\filtering\policy_alignment.py (article_policy_alignment stage 15/16, 产 policy_cosine_sim_allv/_allv_full/_allv_ctx/_allv_ss 全语料静态锚点)
- pipeline\filtering\news_fintech.py (调用 core\text\ahocorasick.py::analyze_fintech_matches/load_fintech_dict 的 AC 自动机, 产 fintech_distinct_keywords 逐篇关键词计数)
citations:
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2618-2646
- doi: 10.1073/pnas.2203150119
  type: journal
  authors: Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al.
  year: 2022
  title: Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty
  venue: Proceedings of the National Academy of Sciences
  vol: '119'
  issue: '44'
  pages_or_artno: e2203150119
- doi: 10.1111/ecin.12992
  type: journal
  authors: Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al.
  year: 2021
  title: The influence of hidden researcher decisions in applied microeconomics
  venue: Economic Inquiry
  vol: '59'
  issue: '3'
  pages_or_artno: 944-960
- doi: "10.1016/j.frl.2026.109668"
  type: "journal"
  authors: "Chen, M., Zhang, Z., & Liu, Y."
  year: 2026
  title: "Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China"
  venue: "Finance Research Letters"
  vol: "95"
  pages_or_artno: "109668"
- doi: "10.1016/j.ipm.2025.104383"
  type: "journal"
  authors: "Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F."
  year: 2026
  title: "Measuring policy diffusion intensity: A text-driven analysis of government documents"
  venue: "Information Processing & Management"
  vol: "63"
  issue: "2"
  pages_or_artno: "104383"
- doi: "10.1016/j.rmal.2025.100272"
  type: "journal"
  authors: "Hemelstrand, S., & Inoue, T."
  year: 2025
  title: "Stop splitting hairs: The problems with dichotomizing continuous data in language research"
  venue: "Research Methods in Applied Linguistics"
  vol: "4"
  issue: "3"
  pages_or_artno: "100272"
new_dois: []
---

## CORE

【构念与来源】
hidden_adopt_kw_p50_allv 家族测的是"沉默式/隐性政策采纳" (hidden adoption) —— 一篇银行-金科报道在关键词层面对金融科技提及很少 (词频落在该年度分布的下半段, 即低于年度中位数 P50), 但在语义层面 (报道全文的向量表征与监管政策文本向量表征的余弦相似度) 却与政策取向高度贴合 (相似度不低于该年度中位数)。这类文章的典型画像是: 银行的公开报道并不高频堆砌"金融科技""数字化转型"这类显性词汇, 但报道所描述的具体举措 (如网点智能化改造、供应链金融线上化、开放银行 API 对接) 在语义空间上已经与官方政策导向的表述方式趋同。这正是政策"言"与"行"解耦研究关注的核心张力: 组织的对外话语频次未必与其实质行为的政策一致性同步。本家族与 token_adopt (高词频、低语义相似度, 象征性提及但未真正对齐政策方向) 和 subst_adopt (高词频、高相似度, 显性且实质性的政策响应) 共同构成一个二维象限分类体系的三个非重叠格子 (第四格"低频低相似"未单独命名, 代表既不提及也不对齐)。四象限的分类逻辑源自组织行为学与制度理论中"象征性遵从 vs 实质性遵从" (symbolic vs substantive compliance) 的经典二分, 本项目将其操作化为可从文本双重信号 (词频、语义相似度) 交叉构造的定量测度。三个逗号分隔的具体列对应完全一致的分类算法在三个不同文本轨道 (full/ctx/ss) 上各自独立重复执行的结果, 三轨"各自 just-identified 并排、互为稳健性、不分主次" (不可混入同一 over-identified Hansen J 设定), 详见下方各 VAR: 节的轨道差分说明。

【方法学与计算】
分类的两个输入信号: (1) 词频侧 —— 本家族固定用 kw 轨 (Track A), 即 AC 自动机对报道全文做严格无重叠扫描后得到的去重金融科技关键词命中数 fintech_distinct_keywords (与另一并行轨 int/Track B 的 fintech_intensity_score 强度分是姊妹但不同的构念, 后者对应家族 hidden_adopt_int_p50_allv 系列, 二者不作合并统计而是并列呈现互为稳健性); (2) 语义侧 —— 报道全文向量与监管政策文本向量的余弦相似度 policy_cosine_sim 系列列。本家族列名中的 allv 后缀标记该相似度取自"全年份锚点" (全语料静态政策向量锚点 policy_cosine_sim_allv), 与不带 allv 后缀的"vintage 主轨" (逐年度动态更新的政策向量锚点) 构成一对稳健性孪生: vintage 锚点会随每年新发布的政策文本滚动更新参照系, allv 锚点则固定用全样本期内的静态汇总政策向量, 用以检验分类结果是否对锚点选取的时间窗口设定敏感。两个锚点变体同样"互为稳健性、不分主次、禁止混入同一 over-identified 设定"。词频与相似度两个信号各自先在年度内做 P50 (中位数) 切分 —— 即分别用该银行-金科报道全样本在当年的经验分布五十分位数作阈值, 而非跨年度固定绝对阈值, 这样可以吸收语料规模、报道风格随年份的趋势性漂移; 与之并列的稳健性梯子还有 P25/P75 两档更严格/更宽松的切分点 (对应家族 hidden_adopt_kw_p25_allv 与 hidden_adopt_kw_p75_allv, 本文件仅覆盖 P50 中位数切分, 三档阈值互为稳健性、不分主次)。逐篇分类严格遵循"双测才分类"契约: 仅当该篇报道的相似度列与词频列同时非缺失时才参与四象限归类, 任一方缺失 (常见于 stage 15 政策对齐早退路径或该轨文本缺失场景) 该篇记为 NaN 而非静默归入某一格子, 这是 2026-06-11 的一处修复 (`fix(omni-g-runner-03/g-runner-11)`) —— 旧实现里 `NaN >= 阈值` 在 pandas 语义下恒为 False, 会把测量失败的文章错误地整体计入"低相似度"格, 制造出并不存在的系统性偏差。聚合层面按 (target_bank, year) 分组对逐篇 0/1 指示取均值, 由于 pandas 的 mean 聚合天然跳过 NaN, 分母自动收窄为"该银行-年内 sim 与 freq 均已测量的报道篇数", 而非全部报道篇数; 若某银行-年报道全部未测量 (如完全缺失该轨文本或政策向量抽取失败), 对应 bank-year 的四象限占比全部输出 NaN, 与项目"无可测数据即输出 NaN 而非伪零"的通用契约 (F3 红线) 一致, 不会把"未测量"和"测量为 0" 混淆。此外, 全部聚合前会先做一次"验证域"过滤 (`_filter_to_verified_universe`, 2026-06-11 引入): 用 (docid, target_bank) 与 stage 21 语义精筛后的 LLM-verified 文章集做内连接, 剔除 stage 15 规则预筛阶段尚未经过 LLM 语义核实的候选报道 (曾占约 26.8% 假阳性), 以保证四象限族与面板其余文本测度共享同一 verified 聚合域, 不会因分母口径不一致而产生 phantom bank-year。

【文献定位】
本家族的构造逻辑呼应组织与制度理论中区分"言语层面的合规姿态"与"行为层面的实质响应"的长期传统, 也与近年来文本挖掘方法在金融监管遵从研究中兴起的"言行不一致度量"取径相接; Kwan, Lin, Pursiainen & Tai (2024, Journal of Financial and Quantitative Analysis) 用银行对压力情境 (COVID-19) 的数字化能力压力测试说明, 银行公开披露的数字化叙事与其实际技术准备度之间存在可观测的落差, 这与本家族"低词频提及但高语义对齐"的隐性采纳格恰好对应同一类识别问题——报道频次不能替代实质对齐程度的度量。本家族对 P50 分位阈值、kw/int 双轨与 allv/vintage 双锚点的并列稳健性设计, 也受到方法学文献中关于研究者任意选择 (researcher degrees of freedom) 会显著影响结论的警示所驱动: Huntington-Klein et al. (2021, Economic Inquiry) 系统记录了应用微观计量研究中"隐藏的研究者决策" (如阈值切分点、样本窗口选取) 对复现结果的实质性影响, Breznau et al. (2022, Proceedings of the National Academy of Sciences) 的多团队同数据同假设复现实验进一步证明, 即便面对完全相同的数据与研究问题, 分析路径上的隐性选择也会制造出一个此前被低估的"不确定性隐藏宇宙"。本项目正是在这一方法学共识下, 把每一个可能引入任意性的构造决策 (阈值分位数、锚点时间窗、词频轨道) 都显式地并列产出为互为稳健性的多个变体列, 而非只报告单一"最优"设定, 使读者可以直接比较结论对这些决策的敏感度, 而不必信任某一次隐性的、未披露的选择。 在上述一般性方法学共识之外, 另有三条近期文献可分别锚定本家族公式的三个环节。其一, 就 Hidden 格本身的构念而言, Chen、Zhang 与 Liu (2026) 在中国语境下专门刻画企业创新披露中的"多行动少言说 (more action-less talk)"沉默型态——实质投入不低而文本声量偏低的一格——并检验其与商业信用融资的关联, 为本家族"词频低于年度 P50 且政策相似度不低于年度 P50"所捕捉的低声量高实质型态提供 2026 年的存在性证据; 迁移边界在于该文层级为上市公司-年, 其沉默由年报披露文本与专利/研发投入的落差界定 (属言—行的外部对照), 而本家族两维皆取自新闻文本、判据为双分位交叉, 该文既无 allv/vintage 锚点孪生, 亦无三轨与阈值梯子。其二, 就语义侧输入而言, Chen、Wen、Deng、Chen 与 Ma (2026) 以政府文件文本构造政策扩散强度的文本驱动测度, 为 policy_cosine_sim_allv 所属的"以政策文本相似度刻画政策对齐"测度族提供近期方法学锚点; 但该文测的是政府—政府层级的文件间扩散强度而非媒体—政策层级的报道对锚点相似度, 且不做二值象限分类、不设年度分位阈值, 亦无全年份静态锚点与逐年滚动锚点的对照, 故不能作为本家族 allv 孪生设计的方法出处。其三, 就"把连续量按分位二值化"这一核心动作而言, Hemelstrand 与 Inoue (2025) 用三组模拟系统论证了二分连续数据的代价: 标准误几乎普遍被抬高、显著性检验因此失准、R² 等效应量因信息量削减而被压低, 其明确立场是建议不要二分。本家族把连续的 fintech_distinct_keywords 与 policy_cosine_sim_allv 按年度中位数切成 0/1 指示, 正落在该文的告诫射程之内, 故须将其作为反向方法学锚点直面披露: 采用象限设计的理由是构念上需要言—行两维交叉后的离散格子而非单维连续效应, 代价则是上述统计效率与推断精度的损失。须特别声明的是, 该文并未提出"若必须二分则做多切点敏感性检验"一类补救建议, 因此 P25/P50/P75 三档阈值梯子属本项目自设的稳健性措施, 不得援引该文作为其正当性依据; 三档阈值仍按互为稳健性、不分主次、各自 just-identified 并排的口径解读, 不混入同一 over-identified Hansen J。
## VAR: hidden_adopt_kw_p50_allv

【变体差分】
本列是家族在 full 文本轨、kw 词频轨、P50 分位切分、allv 全年份静态锚点这一组合下的基准版本, 列名不带 _ctx/_ss 轨道后缀即代表使用 full 轨: 词频侧取全文扫描得到的 fintech_distinct_keywords (未加轨道后缀的基础列), 相似度侧取全文向量与全年份静态政策锚点的余弦相似度 policy_cosine_sim_allv (同样未加轨道后缀)。full 轨的文本口径为"标题+正文全文" (`content_full`, stage 14 物化), 是三轨中信息覆盖面最宽的一支, 但也因此可能包含与银行-金科议题无关的冗余上下文, 稀释关键词密度与语义相似度信号。需要强调的是, full 轨在本项目 2026-06-29 起的留篇门控口径下地位特殊: 一篇报道是否被判定为"一篇银行金科报道"、从而进入 verified 聚合域, 仅取决于 `llm_verified_full`, 即门控判定只看 full 轨的 LLM 精筛结果; ctx/ss 两轨则退化为"以 full 留篇集为行宇宙的条件测度/稳健性轨", 其分母行集合是 full 留篇集的子集而非独立留篇集。这意味着本列 (full 轨版本) 天然对应门控本身所依据的那一支文本, 是三轨并排中承担"主口径"角色但不改变各轨"互为稳健性、不分主次"的横向并列关系——三轨仍各自 just-identified, 不可混入同一 over-identified Hansen J 识别设定中联合估计。与不带 allv 后缀的 vintage 锚点版本 (hidden_adopt_kw_p50) 相比, 本列的相似度阈值判据锚定在全样本期静态政策向量上, 不随年份滚动更新, 用以检验"逐年更新政策语料参照系"这一设计选择本身是否驱动了隐性采纳占比的时间趋势。

## VAR: hidden_adopt_kw_p50_allv_ctx

【变体差分】
本列在家族基准 (full 轨, kw 词频轨, P50, allv 锚点) 的基础上把文本轨换成 ctx: 词频侧优先取该轨的同轨变体列 (若 fintech_distinct_keywords 存在 _ctx 后缀变体则使用之), 相似度侧取 policy_cosine_sim_allv_ctx (全年份锚点在 ctx 轨文本上的余弦相似度)。ctx 轨的文本口径为"标题+实体窗口" (`content_ctx`, stage 14 物化, 围绕目标银行/金科实体截取的局部上下文窗口), 相较 full 轨聚焦度更高、噪声更少, 更适合捕捉与银行-金科主题直接相关的局部语义信号, 但覆盖面比 full 窄, 若报道中银行与金科相关表述分散在实体窗口之外, 该轨的相似度或词频信号可能弱于 full 轨。需要注意, 若 kw 轨的词频列本身是 track-agnostic 元数据 (AC 去重关键词计数在项目设计上未按 ctx/ss 拆分出独立变体), 则本列的词频输入会退化为复用 full 轨基础列并在日志中显式披露该复用, 这不影响相似度侧仍严格取 ctx 轨专属列; 该复用行为是词频侧构念本身的元数据属性所致, 与相似度侧的三轨独立扫描机制是两回事, 不构成口径混淆。ctx 轨在 2026-06-29 起的留篇门控体系下属于"conditional-on-full"的稳健性轨: 其聚合行宇宙是 full 轨 verified 留篇集的子集, 而非依据 ctx 轨自身的 LLM 判定独立圈定, 这保证了三轨占比彼此可比 (分母来源一致), 但也意味着 ctx 轨本身不承担门控职能。本列与 full 轨、ss 轨版本互为稳健性、不分主次, 三者并排检验"隐性采纳"这一构念是否对文本截取范围 (全文 vs 实体局部窗口 vs 同句窗口) 敏感, 不可混入同一 over-identified Hansen J 识别设定中联合使用。

## VAR: hidden_adopt_kw_p50_allv_ss

【变体差分】
本列是家族在 ss 轨、kw 词频轨、P50、allv 锚点组合下的变体: 词频侧优先取同轨变体 (若存在 _ss 后缀的关键词计数列), 相似度侧取 policy_cosine_sim_allv_ss。ss 轨的文本口径为"标题+银行∧金科同句窗口" (`content_ss`, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认±1句), 是三轨中判据最严格的一支——只截取目标银行实体与金科词在同一句 (或指定半径内) 共同出现的局部片段, 因而语义信号最聚焦, 但覆盖率也最容易受回退规则影响。ss 轨遵循"回退语义镜像 ctx"的项目铁律: 当一篇报道中不存在银行与金科的同句共现时, `content_ss` 会退化为使用全文 body (与 full 轨相同文本), 并置位 `ss_is_fallback=True`, 该回退共享与 ctx 轨相同的 `n_articles` 分母口径, 不会因为回退而人为抬高或压低隐性采纳占比的可测样本量; 若上游 stage 15 未产出 FINTECH_AC (金科关键词自动机缺失), 则 `*_is_fallback` 会整体置 True 实现优雅降级, 而非导致该轨列整体缺失。与 ctx 轨相同, ss 轨在留篇门控上同样属于以 full 轨 verified 集为行宇宙子集的条件稳健性轨, 不独立承担门控职能。本列与 full 轨、ctx 轨版本三者并排、互为稳健性、不分主次, 共同检验隐性采纳测度对"同句强共现判据"这一最严格文本截取口径的稳健性, 严禁将三轨混入同一 over-identified Hansen J 联合识别设定; 若某银行-年内绝大多数报道触发同句回退 (即银行与金科词很少真正同句共现), 本列在数值上会趋近于 full 轨版本, 这本身也是判断该银行-年报道中银行-金科议题耦合紧密程度的一个附带诊断信号。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F. (2026). Measuring policy diffusion intensity: A text-driven analysis of government documents. Information Processing & Management, 63(2), 104383. https://doi.org/10.1016/j.ipm.2025.104383
Hemelstrand, S., & Inoue, T. (2025). Stop splitting hairs: The problems with dichotomizing continuous data in language research. Research Methods in Applied Linguistics, 4(3), 100272. https://doi.org/10.1016/j.rmal.2025.100272
<!-- rendered-citations:end -->
