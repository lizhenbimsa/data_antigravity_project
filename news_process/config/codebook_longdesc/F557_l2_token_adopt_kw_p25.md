---
family_id: F557
columns:
- token_adopt_kw_p25
- token_adopt_kw_p25_ctx
- token_adopt_kw_p25_ss
unit: 银行-年占比 (measured 篇数为分母的比例, 取值域 [0,1], 无数据年份为 NaN)
formula: 'groupby(target_bank, year) 上 mean(⟙[fintech_distinct_keywords_{trk} ≥ 年度P25分位] AND ⟙[policy_cosine_sim_{trk} < 年度P25分位]), 仅对 sim/freq 双双 notna 的文章计入分子分母 (measured 掩码)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (逐篇四象限分类原语) + 同文件象限占比聚合循环 (L1978 起, Track A/B × P{25,50,75} × full/ctx/ss × 全年份锚点 _allv 双变体)
upstream:
- 15_article_policy_alignment.parquet (policy_cosine_sim_{full,ctx,ss})
- 12_news_fintech.parquet (fintech_distinct_keywords, 经 14 三轨物化后带 _ctx/_ss 变体)
- 24_herd_decay.parquet (verified 域 semi-join 键 docid/target_bank)
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
- doi: 10.1086/730053
  type: journal
  authors: Fan, H., Liu, Y., Qian, N., & Wen, J.
  year: 2024
  title: "Technological adoption and taxation: The case of China's Golden Tax reform"
  venue: Tax Policy and the Economy
  vol: '38'
  pages_or_artno: 101-122
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: "The symbolic management of strategic change: Sensegiving via framing and decoupling"
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: "10.1016/j.pacfin.2024.102493"
  type: "journal"
  authors: "Liu, Y., Wang, J., Wen, F., & Wu, C."
  year: 2024
  title: "Corporate responses to systemic risk: Talk and action"
  venue: "Pacific-Basin Finance Journal"
  vol: "87"
  pages_or_artno: "102493"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行在金融科技 (fintech) 新闻报道中的"象征性/口惠而实不至"式响应强度: 一篇报道若在措辞层面高频堆砌金融科技相关关键词、却在语义层面与官方政策文本的余弦相似度偏低, 即被归入"Token Adoption"(token, 象征采纳) 象限; 与之互斥的另外两个象限 ("Hidden Adoption" 隐性采纳 = 关键词低频但政策相似度高, "Substantive Adoption" 实质采纳 = 两者皆高) 属兄弟家族, 三者共享同一构造原语但不在本家族列清单内。这一"言 (talk) 与行 (walk) 分离"的测量取向呼应组织理论中象征性合规 (symbolic compliance) 与实质性合规 (substantive compliance) 的经典二分: 组织为回应外部制度压力可能仅在话语层面做出姿态性调整而未落实到与政策议程真正对齐的实质行动, 这一"框架化-脱耦"(framing-decoupling) 机制在组织理论中已有系统刻画: Fiss & Zajac (2006, *Academy of Management Journal*) 分析企业战略变革的符号化管理时指出, 组织可以通过对外话语框架 (sensegiving/framing) 单方面塑造利益相关方对其战略采纳程度的感知, 而这种话语层面的框架化可以与真实的战略实施相脱耦 (decoupling), 二者并非必然同步——本列族的"关键词高频但政策语义低对齐"象限正是这一脱耦机制在银行金融科技新闻话语中的经验对应物: 高词频代表报道话语层面的框架化强度, 低政策余弦相似度代表该框架化未能在语义结构上锚定真实政策议程, 二者的交叉刻画使得单纯的词频计数无法区分"真实采纳"与"符号性采纳"。Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 在压力测试银行数字化能力时同样强调, 银行对外披露/报道中呈现的数字化姿态与其真实数字资本储备可能并不一致, 需要用独立测度加以区分而非直接采信话语频率。本列族即以此为方法论出发点, 用"关键词频率高但政策语义相似度低"这一交叉条件, 从新闻报道流中筛出疑似姿态性响应的篇目占比, 为面板回归中检验"银行是否真的在做金融科技转型, 还是仅在媒体语境中被塑造/自我塑造为如此"提供一个可与其余测度对照的结构化指标。

【方法学与计算】
构造分两层。第一层是逐篇二值分类, 由 `_classify_policy_quadrants` 完成: 对给定文本轨道 (full/ctx/ss) 与词频轨道 (Track A=kw, 即 AC 自动机去重命中的金融科技关键词数 `fintech_distinct_keywords`; 本家族固定取 kw 轨, Track B=int 强度分数属另一家族), 先按年度分组分别对政策余弦相似度列 (`policy_cosine_sim_{trk}`) 与关键词频率列在组内取 P25 分位阈值 (`groupby('year').transform(quantile)`), 得到逐年、逐轨的动态阈值 (而非跨年度固定阈值, 以吸收政策议程本身逐年漂移); 再判定单篇是否 `high_freq = freq ≥ 阈值` 且 `high_sim = sim ≥ 阈值`, token 象限取 `high_freq & ~high_sim`。第二层是银行-年聚合: 仅对 sim 与 freq 两列同时非缺失 (measured) 的文章参与分类与均值计算, 缺失行的象限指示置 NaN 而非 False, 使 `groupby(['target_bank','year']).mean()` 的隐式分母恰为该银行该年"已测量"的报道篇数, 而非全体报道篇数——这是 2026-06-11 (fix omni-g-runner-03/g-runner-11) 修复的一处历史缺陷: 旧实现把 `NaN >= 阈值` 判为 False, 使 stage 15 早退产生的全 NaN 相似度年份被误判为"低政策对齐", 连带把全部高词频文章错误计入 Token 象限, 制造了本不存在的伪信号; 修复后未测量的银行-年整体输出 NaN, 与项目 F3 缺失值红线 (Allison 2001; Heckman 1979 提示的样本选择/不可测量应显式标记而非隐式填零) 对齐, 也与本仓一贯的"无数据=未测量"契约一致, 下游面板导出阶段刻意删除了曾经存在的 `fillna(0.0)` 兜底, 因为 0 值在此处具有歧义 (既可能是"确实无关键词/低相似度", 也可能是"该年份根本没有可用相似度测量"), 强填零会向双向固定效应回归注入系统性噪声。此外, 分类前会先经 verified 域 semi-join (24_herd_decay 的 docid/target_bank 键) 过滤, 使象限占比与其余面板测度共享同一"LLM 已验证为真实银行-金科报道"的行宇宙, 但若 verified 键缺失该过滤会优雅降级为在 pre-verification 全集上聚合并记日志告警。
【文献定位】
本列族的构念定位介于三条文献线之间: 一是组织理论中的符号管理/脱耦传统, 二是新闻文本量化中的话语-行动分离测量传统, 三是银行数字化转型的实证识别文献。Fiss & Zajac (2006, *Academy of Management Journal*) 确立的框架化-脱耦机制为本列"高词频交叉低政策相似度"这一判定条件提供了组织理论根基: 企业对外话语的框架化强度与其战略实施的实质对齐程度是两条可分离的轴线, 本列族正是用可复算的文本测度 (关键词频率×政策语义相似度) 将这一理论上的可分离性操作化为逐篇二值分类与银行-年占比。Kwan et al. (2024, *Journal of Financial and Quantitative Analysis*) 对银行数字能力的压力测试提示, 仅凭披露话语强度无法可靠代理银行真实的技术资本存量, 支持本列以"话语强度 (关键词频率) 交叉政策语义对齐度"双重条件而非单一词频阈值来界定象征性响应; Fan, Liu, Qian & Wen (2024, *Tax Policy and the Economy*) 在研究金税工程强制性技术采纳时展示了"政策驱动的技术采纳"存在名义合规与实质执行的可分离性, 为本列"高频提及但低政策相似度"这一象限的经济含义 (企业/银行在报道话语层面响应了政策议程但未必真正嵌入政策语义) 提供跨情境的外部佐证。三轨 (full/ctx/ss) 与 P{25,50,75} 分位、Track {kw,int} 词频口径、`_allv` 全年份静态锚点四组维度构成一个完整的规格网格, 本家族仅覆盖 kw 轨 × P25 × full/ctx/ss 三个格点, 其余格点分属兄弟家族, 彼此各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一 over-identified 识别策略 (如 Hansen J 过识别检验) 中同时纳入多个格点作为多重工具或多重内生解释变量的重复来源。 在测度族的更一般层面上, Liu、Wang、Wen 与 Wu (2024, *Pacific-Basin Finance Journal*) 把企业对系统性风险的回应显式拆为 talk (文本表述强度) 与 action (实际举措) 两条可分别测量的维度并检验二者关系, 与本列族以"关键词词频高低"×"政策语义对齐高低"交叉切出 token 象限同属"言—行两维并置"的测度传统, 支持将话语强度与实质对齐视作需分开测量再交叉的两轴而非单一连续量。迁移边界须诚实标注: 该文考察的是企业层面对系统性风险的回应而非银行金融科技采纳, 其 talk 取自公司披露文本、action 取自财务与公司行为代理, 属跨数据源的言行对照; 本列两维则同出于新闻报道文本 (关键词频率 vs 政策余弦相似度), 缺少独立于文本的行动侧证据, 且该文不含年度分位阈值梯子与 bank-year 篇均占比聚合。因此它只为本列的两维交叉构造思路提供同族旁证, 不构成 P25 阈值取值、measured 分母口径或三轨并排安排的直接依据。
## VAR: token_adopt_kw_p25

【变体差分】
本列是家族的 full 轨 canonical 口径: 政策余弦相似度取 `policy_cosine_sim` (无后缀, 基于全文 full-text 计算的文章-政策语义对齐度), 关键词频率取 `fintech_distinct_keywords` (AC 自动机在全文上去重命中的金融科技关键词数, Track A/kw 轨), 两者均在年度内独立取 P25 分位作动态阈值, 象限判定为"关键词频率达到或超过该年 P25 分位 (高频) 且政策余弦相似度低于该年 P25 分位 (低对齐)"。年度分组聚合到银行-年层面得到 measured 篇数占比, 该占比是本项目留篇门控 (2026-06-29 后已切换为 full-only) 下的主要识别口径: 是否算作"一篇银行金科报道"仅看 `llm_verified_full`, full 轨的 Token 占比因此对应最完整、门控最严格的行宇宙。取值为 NaN 表示该银行该年无任何已测量 (sim 与 freq 同时非缺失) 的报道, 而非"该银行该年 Token 占比为零"; 与该银行-年份下的 `hidden_adopt_kw_p25` 与 `subst_adopt_kw_p25` 三者互斥且 (在共同的 measured 子集上) 加总为 1, 三者拼接可还原完整的政策对齐-词频交叉分布, 但本身作为面板回归自变量时应各自独立进入模型, 不建议同时把三个互斥占比都塞进同一 RHS (会产生完全共线, 通常保留其中两个并以第三个为基准组)。在留篇门控 full-only 的前提下, 本列的 measured 分母天然是三轨中最大的一个, 因此也是回归样本量最充裕、最适合作为基线设定的轨道; ctx/ss 两轨作为并排的稳健性检验, 分母通常小于等于本列, 三者共同展示的是"象征性响应"这一构念在不同文本窗口宽度下是否稳定存在, 而非彼此嵌套或递进的层级关系。

## VAR: token_adopt_kw_p25_ctx

【变体差分】
本列与 canonical full 轨共享完全一致的分类算法与 P25 分位阈值构造逻辑, 唯一差别是文本作用域切换为 ctx 轨: 政策余弦相似度取 `policy_cosine_sim_ctx` (基于标题+目标银行实体窗口文本计算的对齐度), 关键词频率优先取该轨的同轨变体 `fintech_distinct_keywords_ctx`——若该变体在当期 schema 中不存在 (kw 轨的去重关键词计数在部分历史 schema 下是 track-agnostic 元数据, 无逐轨版本), 则退化复用 full 轨的 `fintech_distinct_keywords` 并在日志中披露此复用, 不会静默产生虚假的"ctx 专属"信号。三轨 (full/ctx/ss) 在本项目铁律下是各自 just-identified 并排的互为稳健性测度, ctx 轨并非 full 轨的替代或升级, 而是用更窄的实体窗口文本重新独立扫描后得到的平行结果, 用于检验 Token 象限占比是否对"文本作用域选取"敏感; 二者数值上的差异本身构成有信息量的稳健性证据, 不应被简单平均或相加。2026-06-29 起的留篇门控 (full-only) 改动后, ctx 轨的分类行宇宙仍是 full 轨 verified 集合的子集 (conditional-on-full), 即 ctx 轨占比的分母同样锚定在 full 轨已验证为真实银行-金科报道的篇目范围内, 只是相似度与词频的测量文本换成了实体窗口; 若某银行-年在 ctx 轨全部行的 sim 或 freq 缺失 (例如该年 stage 15 ctx 相似度计算优雅早退), 则该银行-年在本列输出 NaN, 与 full 轨 NaN 语义完全一致但触发条件相互独立。

## VAR: token_adopt_kw_p25_ss

【变体差分】
本列同样复用与 canonical 完全相同的四象限分类算法与年度 P25 分位阈值构造, 文本作用域切换为 ss 轨 (同句轨): 政策余弦相似度取 `policy_cosine_sim_ss`, 关键词频率优先取同轨变体 `fintech_distinct_keywords_ss`, 缺失时同样退化复用 full 轨词频列并记录日志。ss 轨的构造语义镜像 ctx 轨: 若某篇报道不存在目标银行与金融科技关键词在同一句 (±N 句窗口由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 共现, 则该篇的 `content_ss` 回退为全文正文、`ss_is_fallback` 标记为 True, 相似度与词频测量退化为在全文尺度上进行, 但回退发生在上游 stage 14/15 的文本物化与政策对齐计算阶段, 与本家族的象限分类逻辑本身无关——本列只是消费已经算好的 `policy_cosine_sim_ss`/`fintech_distinct_keywords_ss`, 不重新判定回退。ss 轨是三轨中窗口最窄、对"银行与金融科技话题真正同句出现"要求最严的口径, 因此其 Token 象限占比可读作"在银行与金科议题紧密并置的语境下, 仍然呈现高词频低政策对齐特征"的篇目比例, 相对 full/ctx 轨更贴近严格语境下的象征性响应信号, 但样本可用性 (measured 分母) 通常小于 full 轨。与 ctx 轨一样, ss 轨与 full 轨、彼此之间均是并排的稳健性测度而非层级替代关系, 三者禁止混入同一过识别 (over-identified) 检验框架作为多重内生解释变量或多重工具变量的来源。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Liu, Y., Wang, J., Wen, F., & Wu, C. (2024). Corporate responses to systemic risk: Talk and action. Pacific-Basin Finance Journal, 87, 102493. https://doi.org/10.1016/j.pacfin.2024.102493
<!-- rendered-citations:end -->
</content>
</invoke>
