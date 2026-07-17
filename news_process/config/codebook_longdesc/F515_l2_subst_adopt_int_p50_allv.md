---
family_id: F515
columns:
- subst_adopt_int_p50_allv
- subst_adopt_int_p50_allv_ctx
- subst_adopt_int_p50_allv_ss
unit: 银行-年占比 (0至1 之间的分数, 分母=该银行该年已测量篇数)
formula: 逐篇二值指示 subst_i = 1{fintech_intensity_score_i >= 年度P50} AND 1{policy_cosine_sim_allv_i
  >= 年度P50}, 仅 sim/freq 双双非缺失的文章参与分类; 面板列 = groupby(target_bank, year) 对 subst_i 取
  mean (NaN 自动跳过, 分母=已测量篇数, 全未测量银行-年输出 NaN 而非伪零)
producer: pipeline\panel\runner.py (_classify_policy_quadrants + 7h 四象限循环, L312-L335,
  L1997-L2089) ; pipeline\panel\export.py (STATA 标签映射)
upstream:
- 15_fintech_intensity.py (fintech_intensity_score, policy_cosine_sim_allv)
- 14_materialize_ctx.py (content_ctx / content_ss 三轨文本物化)
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: The Symbolic Management of Strategic Change - Sensegiving via Framing and
    Decoupling
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1016/j.jfi.2024.101101
  type: journal
  authors: Kutzbach, M. J., & Pogach, J.
  year: 2024
  title: 'Financial Technology and Relationship Lending: Complements or Substitutes?'
  venue: Journal of Financial Intermediation
  vol: '59'
  issue: ''
  pages_or_artno: Article 101101
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial
    Pollution'
  venue: The Journal of Finance
  vol: ''
  issue: ''
  pages_or_artno: ''
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate
    Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
  vol: '164'
  issue: ''
  pages_or_artno: Article 107191
- doi: "10.2139/ssrn.6922688"
  type: "wp"
  authors: "Xu, F."
  year: 2026
  title: "Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks"
  venue: "SSRN"
  pages_or_artno: "6922688"
- doi: "10.1177/01708406241295505"
  type: "journal"
  authors: "Kaufmann, L., Krlev, G., & Brown, M. (."
  year: 2025
  title: "In Plain Sight: Mechanisms of means–ends decoupling in impact investing"
  venue: "Organization Studies"
  vol: "46"
  issue: "5"
  pages_or_artno: "667-692"
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
- doi: "10.1016/j.frl.2024.105401"
  type: "journal"
  authors: "Zhang, Z., Hou, Y., Li, Z., & Li, M."
  year: 2024
  title: "From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105401"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行在单篇报道层面「金科词汇密度」与「政策语言相似度」是否同步偏高, 用来把每篇报道逐篇归入 Westphal & Zajac (1994) 意义上的实质采纳 (substantive adoption) 象限, 再按银行-年聚合为占比。构念上属于 substance-versus-symbol / decoupling 谱系: 组织可以只在言语层面追随流行做法而不改变实际行为 (象征性采纳), 也可以言行一致 (实质性采纳), 二者的区分正是 Westphal 与 Zajac 一系列研究、以及 Fiss & Zajac (2006) 对战略变革象征化管理的核心论点。落到本项目的银行-金科语境, 「行为强度」由报道中金科相关词汇的加权密度 (fintech_intensity_score, TF-IDF × SIF 加权的连续测度) 代理, 「言语/立场对齐」由报道文本与官方金科政策文本的余弦相似度 (policy_cosine_sim_allv) 代理; 二者同时处于年度高分位, 才被记为「言行一致的实质采纳」报道, 呼应 Kutzbach & Pogach (2024) 关于金融科技与关系型信贷「互补还是替代」需要用真实业务强度而非公告措辞来甄别的思路, 也呼应 Duchin, Gao & Xu (2025) 用「披露-行动脱钩」而非披露本身来识别漂绿/漂科技的方法论立场。

【方法学与计算】
上游 stage 15 (fintech_intensity) 逐篇产出两个原语: 词频侧 fintech_distinct_keywords (AC 自动机原始去重关键词数, kw 轨) 与 fintech_intensity_score (TF-IDF × SIF 加权强度, int 轨), 以及余弦相似度侧 policy_cosine_sim (vintage 主锚点, 按报道所在年份匹配同期政策文本锚点) 与 policy_cosine_sim_allv (全年份静态锚点, 用全语料汇总构造的固定锚点, 不随报道年份变化)。runner.py 的 _classify_policy_quadrants 对每篇文章、按年度分别计算 fintech_intensity_score 与 policy_cosine_sim_allv 各自的分位数阈值 (本家族固定 P50, 即年度中位数分割, 与项目内 10 余处中位数分割惯例一致), 词频与相似度同时高于阈值记为 Substantive (言行一致), 词频高但相似度低记为 Token (洗科技/象征性采纳), 词频低但相似度高记为 Hidden (闷声干大事), 二者皆低为 Irrelevant (不落入本家族任何一列)。分类严格限定在 sim 与 freq 双双非缺失的文章上进行 (fix omni-g-runner-03/11, 2026-06-11 修复): 早期实现把测量失败 (NaN) 误判为「低于阈值」, 导致 stage 15 优雅早退产生的全 NaN 相似度列被错误地全部归入 Token 象限; 现行实现对未测量文章输出 NaN 指示, 经 groupby mean 聚合时自动跳过, 分母只计已测量篇数, 全年份无有效测量的银行-年输出 NaN 而非伪零, 避免污染双向固定效应回归系数 (Allison 2001 关于缺失值强填零会产生偏误的告诫, 在 runner.py v6/F3 修复注释中被明确引用)。家族名中的 int 表示词频侧走 Track B (fintech_intensity_score 连续加权强度), 与 Track A (kw, 裸关键词计数) 并行但不混用; p50 表示分位阈值取年度中位数 (P25/P75 是另两级稳健性阶梯, 不属本家族); allv 表示相似度阈值一侧使用全年份静态锚点 policy_cosine_sim_allv, 而非按年匹配的 vintage 主锚点 policy_cosine_sim (无 allv 后缀的姊妹家族)。

【文献定位】
象征性与实质性采纳的区分是组织理论中长期成熟的构念, Westphal & Zajac (1994) 首次在 CEO 长期激励计划的「采用但不使用」现象上系统化了这一区分, Fiss & Zajac (2006) 进一步把象征化管理机制化为「框架-脱钩」的战略变革传导链条。本家族把这一理论谱系移植到中国银行业金融科技报道语境, 用词频强度代理「行为」、用政策语言相似度代理「言语立场」, 属于近年金融文本挖掘文献中「言行是否脱钩」测度的一支, 与 Bingler et al. (2024) 在气候信息披露中区分「廉价谈话」与真实排放/声誉风险敞口的方法论同构, 也与 Duchin, Gao & Xu (2025) 通过资产市场证据甄别可持续性叙事与漂绿行为的识别策略呼应。Kutzbach & Pogach (2024) 则从金融科技与关系型信贷互补/替代关系的角度提示: 仅凭报道措辞无法判断银行金融科技投入究竟是渐进补充存量业务, 还是实质性替代传统关系型信贷模式, 这正是本家族用「词频×相似度」双维度交叉分类、而非单维度阈值分割的动机所在。

三轨 (full/ctx/ss) 与 vintage/allv 双锚点在本家族内构成两条正交的稳健性阶梯: 三轨各自基于不同文本窗口 (full=标题+全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗) 独立计算词频与相似度, 各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定; allv 全年份静态锚点与不带 allv 后缀的 vintage 按年匹配锚点同理互为稳健性并排, 二者共用完全一致的 track × 词频轨 × 分位数四象限构造, 唯一差异是相似度阈值列的锚点来源, 同样不应混入同一识别方程。需要明确披露的口径铁律 (对照 policy_alignment.py 源码注释): allv 锚点用全部年份汇总的政策文本构造, 对早期年份的报道而言, 其相似度打分实际上包含了发生在报道之后才出台的「未来」政策文本, 因而存在前视偏差, 仅作跨年份比较不受锚点漂移干扰的稳健性对照, 绝不能替换 vintage 主轨作为识别策略的主口径; vintage 按年匹配锚点不含此前视偏差, 是构念上更贴合「报道当时的政策语境」的主轨, 二者互为稳健性并排而非 allv 优于 vintage。留篇门控遵循 full-only 口径 (2026-06-29 起): 一篇报道是否被计入「银行金科报道」样本, 只看 full 轨 llm_verified_full 是否为真, ctx/ss 是本家族的 conditional-on-full 测度/稳健性轨, 行宇宙是 full 留篇集合的子集。_ss 轨的回退语义镜像 _ctx: 若报道中不存在银行与金科词汇的同句共现, content_ss 退化为全文正文, 对应的 ss_is_fallback 标记为真, 与 _ctx 共享同一套 n_articles 分母口径; 若 stage 15 上游 FINTECH_AC 词典缺失 (None), 则 *_is_fallback 全部为真, 呈优雅降级而非崩溃。 近年文献在测度端与理论端分别为本族的两维信号补充了锚点。Xu (2026) 用文本方法构造银行层面的 FinTech intensity 指标并检验其与经营绩效的关系, 与本族 freq 维所用的 fintech_intensity_score 属同一测度族, 说明"银行层面文本金科强度"确有同域应用; 边界在于该文样本为欧洲银行, 文本取自银行自身披露/年报而非第三方中文新闻, 其 intensity 以连续形式直接进入回归, 既不做年度分位二值化, 也不与政策文本相似度交叉形成 2×2 象限, 且属未经同行评审的 SSRN 工作论文, 结论稳健性未定。Kaufmann、Krlev 与 Brown (2025) 以影响力投资为田野系统刻画 means-ends decoupling 的具体机制, 为本族 subst 与 token 两格的理论区分提供了近期组织学依据; 惟该文为定性机制研究, 不构造任何数值指标, 更无分位阈值二值化与 bank-year 聚合, 与本族"政策余弦 × 金科强度"的操作化仅属理论对应而非同一测量。Huang 与 Ma (2024) 在中国情境下检验金融科技发展对企业实质性与象征性绿色创新的差异化影响, 佐证该二分在金科议题下的同域适用性; 其实质/象征由专利类型客观划分、主体为非金融上市公司, 与本族基于新闻文本逐篇判定银行采纳形态的口径不同。Zhang、Hou、Li 与 Li (2024) 研究 ESG 评级如何推动企业创新结构由象征性向实质性迁移, 其以象征性/实质性构成比而非绝对水平为分析对象的做法, 与本族取"双高篇数 / 已测量篇数"这一构成比 (而非强度绝对水平) 的设计逻辑一致; 但原文比例基于专利结构数据, 主体为 A 股非金融企业, 驱动因素为 ESG 评级, 且未使用任何文本判定器, 故仅锚定"以构成比刻画实质性程度"这一构念, 不锚定本族的分位阈值口径与文本测度原语。
## VAR: subst_adopt_int_p50_allv

【变体差分】
本列是家族的无后缀主轨, 对应 full 文本窗口 (标题+全文正文) 计算的 fintech_intensity_score 与 policy_cosine_sim_allv, 二者按年度各自取 P50 中位数为阈值, 逐篇分类为 Substantive 后按银行-年取均值。作为 full-only 留篇门控下的主聚合口径, 本列的行宇宙即当年 llm_verified_full 为真的报道全集, 是三轨中样本量最大、覆盖面最广的一支, 通常作为主回归的处理变量或机制检验变量使用。needs_review=false 表示写手校对阶段未发现该列命名/口径与 producer 源码存在冲突; tier=standard 表示该列不进入 core 家族的加密审查通道, 但仍受本家族字数与引文闸约束。与不带 allv 的姊妹家族 (使用 vintage 按年匹配政策锚点) 相比, 本列相似度阈值一侧固定采用全语料静态锚点, 不随报道所在年份切换比较基准, 更适合用来做跨年份比较不受锚点漂移干扰的稳健性检验; 但须明确披露这一便利的代价——allv 锚点混入了报道发生之后才出台的政策文本, 对早期年份样本构成前视偏差, 因此本列仅作稳健性对照, 绝不替换 vintage 主轨作为识别策略的主口径。与之相对, vintage 主锚点列按报道所在年份匹配同期政策文本、不含前视偏差, 更贴合「报道当年的政策语境」这一构念, 二者互为稳健性并排, 不应视为一方无副作用地优于另一方。本列同族内还须与 P25/P75 两级分位阈值稳健性、以及 kw/int 两条词频轨区分开: P50 取年度中位数分割, 是本项目机制检验的基准分位, P25/P75 是另外两个独立的分位阈值稳健性阶梯, 不与 P50 混入同一识别方程; kw 轨 (裸金科关键词计数) 与 int 轨 (TF-IDF × SIF 加权强度) 同样各自 just-identified 并排, 本列固定属于 int 轨, 不应与同名 kw 轨列相加或替代。

## VAR: subst_adopt_int_p50_allv_ctx

【变体差分】
本列是家族的 ctx 轨变体, 词频侧与相似度侧均改用 ctx 文本窗口 (标题+目标银行实体窗口) 重新独立测量, 而非直接复用 full 轨结果做二次筛选; 若某一侧测度 (词频或相似度) 缺少 ctx 同轨变体 (即为 track-agnostic 元数据), runner.py 会记录一条 info 日志并优雅复用 full 轨对应列, 此时该文章在 ctx 轨的分类实质上退化为对 full 轨该侧测度的复用, 但另一侧若存在真实 ctx 变体仍独立计算, 两侧不会同步降级。本列的行宇宙遵循 full-only 留篇门控: 只对 llm_verified_full 为真的报道计算 ctx 轨指示, 因此 ctx 轨样本量不会超过无后缀主轨, 是 conditional-on-full 的稳健性测度而非独立样本。ctx 窗口聚焦于报道中直接围绕目标银行实体的上下文, 剔除了同篇报道中与目标银行无关的段落对相似度/强度打分的稀释效应, 因而在识别「该银行本身的金科语言/行为强度」上比 full 轨更聚焦、但样本覆盖 (可计算 ctx 窗口的报道占比) 通常小于 full 轨。本列与无后缀主轨、_ss 轨三者 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 回归设定中同时作为工具或解释变量使用。使用者若观察到 ctx 轨与 full 轨在方向上出现分歧, 应优先排查该银行-年是否存在大量 track-agnostic 复用 (即词频侧退化为 full 列) 导致的口径混杂, 而非直接把分歧解读为构念本身的不稳健。

## VAR: subst_adopt_int_p50_allv_ss

【变体差分】
本列是家族的 ss 轨变体, 词频侧与相似度侧改用 ss 文本窗口 (标题+目标银行与金科词汇同句共现±N句窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认1) 独立测量。ss 轨回退语义镜像 ctx 轨: 若报道全文中不存在银行与金科词汇的同句共现, content_ss 退化为等同 full 轨的全文正文, 对应 ss_is_fallback 标记为真, 且与 ctx 轨共享同一套 n_articles 分母口径, 而非另开独立分母; 若上游 FINTECH_AC 词典整体缺失 (None), 则 *_is_fallback 全部为真, 全部报道在 ss 轨优雅降级为等同 full 轨处理。ss 窗口比 ctx 窗口更严苛 (要求银行与金科词汇同句共现, 而非仅共处于同一实体窗口), 因此在能够真实计算 ss 轨 (未回退) 的报道子集内, 相似度与词频测度对「银行与金科话题同时出现」这一构念的捕捉最为精确, 但代价是可用样本进一步收缩、回退比例通常高于 ctx 轨。本列同样遵循 full-only 留篇门控, 行宇宙是 llm_verified_full 留篇集合的子集; 与无后缀主轨、_ctx 轨三者 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 回归设定。由于 ss 轨要求同句共现这一更严格判据, 在实证解读上宜将其视为「言行一致」构念的高精度但低召回稳健性检验: 当 ss 轨与 full/ctx 轨方向一致时, 结果对文本窗口选择不敏感的证据更强; 若 ss 轨因回退比例过高而与 full 轨高度重合 (即多数报道 ss_is_fallback 为真), 则应在稳健性表中同时披露回退比例, 避免读者误把「窗口收窄后的相同结果」解读为独立验证。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change - Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Kutzbach, M. J., & Pogach, J. (2024). Financial Technology and Relationship Lending: Complements or Substitutes?. Journal of Financial Intermediation, 59, Article 101101. https://doi.org/10.1016/j.jfi.2024.101101
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, Article 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Xu, F. (2026). Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks. SSRN No. 6922688 [Working Paper]. https://doi.org/10.2139/ssrn.6922688
Kaufmann, L., Krlev, G., & Brown, M. (. (2025). In Plain Sight: Mechanisms of means–ends decoupling in impact investing. Organization Studies, 46(5), 667-692. https://doi.org/10.1177/01708406241295505
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
<!-- rendered-citations:end -->
