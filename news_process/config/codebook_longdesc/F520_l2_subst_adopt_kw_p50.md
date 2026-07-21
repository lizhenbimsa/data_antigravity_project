---
family_id: F520
columns:
- subst_adopt_kw_p50
- subst_adopt_kw_p50_ctx
- subst_adopt_kw_p50_ss
unit: 无量纲二值/比例型采纳分类指标 (银行-年面板层面为 [0,1] 区间占比; 详见下方公式)
formula: 'article-level (2x2 象限分类, _classify_policy_quadrants): high_freq_i = 1{fintech_distinct_keywords_i >= Q_year(freq, P50)}, high_sim_i = 1{policy_cosine_sim_i >= Q_year(sim, P50)} (两阈值均按年度 groupby 分别重算, 非全语料一次性阈值), subst_adopt_kw_i = 1{high_freq_i AND high_sim_i}, 仅当 sim/freq 双双非缺失时参与分类 (measured 掩码, 否则记 NaN 不进分母); panel-level: subst_adopt_kw_p50 = mean_i(subst_adopt_kw_i) 按银行-年聚合 (stage 40 runner.py::_classify_policy_quadrants 计算 + export.py 仅负责标签映射)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (计算逻辑, 步骤 7h-token 调用点 L2069-2087) ; pipeline\panel\export.py (仅列标签/名称注册, 非计算) ; papers\_common\derivative_replication.py (下游消费者, MECHANISM_SUBST 占位符, 非计算)
upstream:
- 12_news_fintech (fintech_distinct_keywords, 金科关键词 AC 去重命中数, high_freq 轴来源)
- 15_fintech_intensity (int 轨并排信号来源, 非本列直接依赖)
- 16_article_policy_alignment (policy_cosine_sim, high_sim 轴唯一来源; 步骤 7h-token 硬读该 parquet, 缺列 raise RuntimeError 非静默跳过)
- 40_panel_export_main (银行-年聚合)
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: 'Substance and Symbolism in CEOs'' Long-Term Incentive Plans'
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: 'The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions'
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: 'The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling'
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
  vol: ''
  issue: ''
  pages_or_artno: ''
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: 'How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk'
  venue: Journal of Banking & Finance
  vol: '164'
  issue: ''
  pages_or_artno: '107191'
- doi: "10.1057/s41599-024-02921-w"
  title: "Does corporate digital transformation restrain ESG decoupling? Evidence from China"
  authors: "Chen, X., Wan, P., Ma, Z., & Yang, Y."
  year: 2024
  venue: "Humanities and Social Sciences Communications"
  type: "journal"
- doi: "10.1111/eufm.12424"
  title: "How valuable is FinTech adoption for traditional banks?"
  authors: "Bian, W., Wang, S., & Xie, X."
  year: 2023
  venue: "European Financial Management"
  type: "journal"
new_dois:
  - "10.1057/s41599-024-02921-w"
  - "10.1111/eufm.12424"
---

## CORE

【构念与来源】
subst_adopt_kw_p50 家族衡量银行在给定年度的金融科技新闻报道中, "实质性采纳" (substantive adoption) 相对于"象征性/符号性提及" (symbolic/token mention) 的占比强度, 其理论谱系来自组织理论的实质—象征二分传统 (Westphal & Zajac, 1994, 1998; Fiss & Zajac, 2006)。该传统的核心洞见是: 组织对外部制度压力或流行实践的响应可以是"解耦" (decoupling) 的——采取表面符合话语但不改变实际行为的姿态——也可以是内化到组织实际运营中的实质响应。本项目 P3 (bank_fintech_substance, 对标 W&Z 与 Gomber et al. 2018 IS 领域三分类框架) 将该二分法移植到银行—金融科技新闻文本域: 一篇报道中若仅泛泛提及金科关键词而缺乏与银行业务实质结合的信号 (token/hidden), 记为"象征性"; 若同时出现关键词命中与业务实质信号 (如与该银行策略对齐度、金科强度等测度联动), 记为"实质性" (subst)。家族名 kw 指该分类词频轴所依赖的信号来源是 stage 12 `news_fintech` 生产的金科关键词 AC 自动机去重命中数 fintech_distinct_keywords (即不同关键词种类数, 非含重复计数的命中次数; Track A, "KW" track), 与依赖 fintech_intensity 连续得分的 Track B ("INT" track, 对应 `subst_adopt_int_p50` 等平行家族) 构成两条并排的构念操作化路径, 二者互为稳健性、不分主次、绝不应混入同一 over-identified 设定联合估计。
p50 后缀表明该指标是"象征/实质"象限判定所依赖的连续测度 (article_sim / fintech_intensity 等) 按分位数阈值 P50 (即样本中位数) 二值化切分的产物; 家族并排还有 p25/p75 两个更宽松/更严格阈值变体 (`subst_adopt_kw_p25`/`subst_adopt_kw_p75`), 判据是 x_col >= quantile(pct/100): pct 越小切点越低、越容易达标 (p25 更宽松, 更多文章落入 high_freq/high_sim 进而落入 subst), pct 越大切点越高、越难达标 (p75 更严格, 仅取分布上四分之一以上视为高); 三者构成一条阈值敏感性梯子, 各自 just-identified, 用以证明"实质采纳"的分类结论不被单一分位数取值人为驱动——这与本项目其它梯子 (政治词权重 {0,0.5,1}、词典消融 powerset、罕见词频次 cutoff {2,3,5}) 遵循同一稳健性哲学: 梯子内各档并排呈现, 不设主档, 更不得把梯子的多档系数并入同一个过度识别的 Hansen J 检验。
该家族与 `token_adopt_kw_p50`(纯象征/未采纳, token-only)、`hidden_adopt_kw_p50`(隐性/未披露采纳) 构成一组互斥的三分类象限 (象征/隐性/实质), 三者面板聚合值理论上和为 1 (不含双低象限时; 各银行-年内三分类占比归一, 双低象限即 high_freq 与 high_sim 均未达标的文章不计入任一分类, 真实数据中该象限普遍存在, 故三者之和一般小于 1)。这一三分类设计直接呼应 Westphal & Zajac (1994) 关于 CEO 长期激励计划"实质"与"符号"成分并存、以及 Fiss & Zajac (2006) 关于战略变革的"意义赋予" (sensegiving) 如何通过框定与解耦共同作用的经典发现: 企业对外部创新压力 (本项目情境下即金融科技浪潮) 的公开姿态未必等于其内部实质行动, 二者需要独立测量而非相互替代。

【方法学与计算】
构造流程分两层, 且严格是一个二维 2x2 象限分类, 而非"关键词命中数>0"叠加单一连续阈值门的简化判定。文章层 (article-level, 由 pipeline/panel/runner.py::_classify_policy_quadrants 实际计算, 步骤 7h-token 调用): 词频轴取 stage 12 `news_fintech` 输出的金科关键词 AC 自动机 (裸词典, 607 词, 无否定/短名过滤; 与银行侧判定不对称) 去重命中数 fintech_distinct_keywords (kw 轨, Track A 命名依据); 相似轴取 stage 16 `article_policy_alignment` 输出的 policy_cosine_sim (文章—政策文本余弦相似度)。两轴各自独立按年度分组计算分位阈值: high_freq_i = 1{fintech_distinct_keywords_i >= 该年度 fintech_distinct_keywords 分布的 P50 分位数}, high_sim_i = 1{policy_cosine_sim_i >= 该年度 policy_cosine_sim 分布的 P50 分位数} — 词频轴本身也是分位数阈值门, 并非"命中数>0"这一宽松判据。当且仅当 high_freq_i 与 high_sim_i 同时为真时, 该篇文章记 subst_adopt_kw_i = 1 (双高象限, "实质采纳"); 高频低相似记 token (象征提及但未测得政策对齐), 低频高相似记 hidden (隐性对齐但关键词命中不足); 双低象限既不算 token/hidden 也不算 subst。仅当 policy_cosine_sim 与 fintech_distinct_keywords 在该篇文章上双双非缺失 (measured 掩码) 时才参与分类, 否则该篇记 NaN, 不进入任何一个象限的分子分母 (stage 15 早退产生 policy_cosine_sim 全 NaN 的极端情形下, 该年度四象限面板列将整体输出 NaN 而非静默归零)。
面板层 (bank-year, stage 40 runner.py 在同一步骤内聚合、export.py 仅负责标签/列名注册非计算): 对每家银行—年度内的所有留篇文章 (full-only 门控, 详见下节) 取 subst_adopt_kw_i 的均值 (measured 掩码内 groupby mean, 自动跳过未测量行), 得到 subst_adopt_kw_p50 ∈ [0,1], 解读为"该银行—年度金科报道中经关键词与政策对齐双高判定为实质性采纳的文章占比"。三个象限指标 (token/hidden/subst) 共享同一分母 (该银行—年度内经留篇门控且 sim/freq 双双可测的金科相关文章数), 三者面板均值理论上加总归一 (不含双低象限时), 可联合用于机制检验 (如 benefit_society 论文 `MECHANISM_TOKEN`/`MECHANISM_HIDDEN`/`MECHANISM_SUBST` 三元占位符消费该三家族, 见 papers/_common/derivative_replication.py L105-107)。
分位阈值 P50 的计算样本口径为逐年重算 (按 year 分组分别对 policy_cosine_sim 与 fintech_distinct_keywords 取分位数), 而非全语料一次性阈值——这一设计使得"实质采纳"的判定标准随年度分布内生调整 (某年度金科报道整体更密集时, 当年的高频门槛相应抬高), 而非跨年固定的绝对切点; 解读跨年趋势时需注意分母基准本身逐年浮动这一特性。p25/p75 阈值变体同样逐年独立重算切点、独立生成三分类标签, 不与 p50 共享中间量, 因此三档阈值互为并排稳健性检验而非同一构造的派生列。

【文献定位】
本家族的理论根基直接来自 Westphal & Zajac (1994, 1998) 与 Fiss & Zajac (2006) 建立的"实质—象征"二分传统: 前两篇论文以 CEO 长期激励计划与公司治理改革为经验场景, 揭示组织对外部治理压力的响应存在系统性的实质—象征分野, 且这种分野本身是可测量、可预测的组织现象而非测量噪声; 后一篇进一步说明战略变革的"意义赋予"过程如何通过框定 (framing) 与解耦 (decoupling) 两种机制共同塑造利益相关者对变革的感知, 为本家族"报道语言可能脱耦于实际业务采纳"的识别策略提供了直接的构念先例。Kim & Lyon (2015) 将该框架推进到"漂绿/漂棕"(greenwash/brownwash) 的对称形式, 说明夸大 (greenwash) 与过度谦抑 (brownwash) 是同一解耦逻辑的两个方向, 提醒本家族在解读"未达到实质阈值"的报道时不应默认其为策略性掩饰, 也可能是真实的保守披露。Duchin, Gao & Xu (2025, 顶刊 Journal of Finance) 提供了金融市场层面区分"真实可持续行动"与"漂绿"的资产定价证据, 印证了实质—象征区分在金融经济学语境下的可检验性与经济后果显著性, 是本家族方法论从公司治理领域迁移到银行金融科技领域的合法性支撑之一。Bingler, Kraus, Leippold & Webersinke (2024, Journal of Banking & Finance) 则展示了基于语言模型的"廉价谈话" (cheap talk) 侦测方法学如何应用于企业气候披露的实质性甄别, 为本家族依赖关键词/语言信号进行采纳类型判定的操作化路径 (kw track) 提供了同源方法学参照, 说明"文本信号驱动的实质性分类"在临近领域已具备成熟的方法学先例, 而非本项目独创的临时启发式。基于中国上市公司文本分析证据, 陈曦、万攀兵、马壮壮与杨圆圆 (2024, Humanities and Social Sciences Communications) 研究数字化转型如何缓解ESG披露话语与实质行动之间的解耦, 为本家族"实质—象征"文本分类方法论提供了同源的最新经验参照; 边卫红、王胜邦与谢星 (2023, European Financial Management) 利用机器学习文本挖掘方法统计银行年报中金融科技相关词汇的提及强度, 检验金科采纳对传统银行价值的影响, 与本家族基于文本关键词信号判定采纳类型的操作化路径高度同源。

## VAR: subst_adopt_kw_p50

【变体差分】
本列是家族的 full 轨 canonical 版本, 文本扫描范围为完整正文 (`content_full` = 标题 + 全文, prepend_title 物化), 对应留篇门控口径: stage 21 是否判定"一篇银行金科报道"仅看 `llm_verified_full == True`, 因此该列所依赖的分母 (银行—年度内留篇文章数) 与情感/态度类主测度共享同一 full-only 行宇宙。该列是三轨中的主轨, 亦是 papers/_common/derivative_replication.py 中 `MECHANISM_SUBST` 占位符默认消费的列 (benefit_society 论文机制检验模板)。阈值取 P50 (中位数二值化), 与并排的 p25 (更宽松, 切点更低、更容易达标进而更多文章落入 subst) 、p75 (更严格, 仅取分布上四分之一以上视为高) 构成阈值敏感性梯子; 三档各自 just-identified 并排呈现, 用以说明"实质采纳"结论不依赖某个具体分位数的武断选择, 不设主档, 更不得把三档系数塞进同一个过度识别的 Hansen J 联合检验。
本列还与同族并排的 Track B (int) 变体 `subst_adopt_int_p50` 构成信号来源维度上的稳健性对照: kw 轨依赖离散的关键词去重命中数 (distinct keyword count, 非含重复计数的命中次数) 作为词频轴信号来源, int 轨则改用连续的 fintech_intensity 强度得分作为切分依据。二者在概念上度量同一个理论构念 (是否存在超越表面提及的实质业务结合), 但操作化路径彼此独立、互不借用中间量, 因此二者之间的相关程度本身即是对该构念稳健性的一项经验证据, 而非可以相互替代或加权平均的重复测量; 论文侧机制检验 (如 benefit_society 的 `MECHANISM_SUBST` 占位符) 默认消费本列 (kw, p50) 作为主报告规格, int 轨与 p25/p75 阈值变体则留作附录稳健性表的并排陈列, 不改变研究设计的过度识别结构。

## VAR: subst_adopt_kw_p50_ctx

【变体差分】
本列是家族的 ctx (entity-context) 轨稳健性版本: 文本扫描范围收窄为标题 + 目标银行实体窗口 (`content_ctx`), 而非完整正文。ctx 轨与 full 轨、ss 轨三者各自 just-identified 并排, 互为稳健性、不分主次, 铁律上禁止把三轨的系数混进同一个过度识别的 Hansen J 联合检验。需要特别注意的是: 2026-06-29 起留篇门控 (即"是否算作一篇银行金科报道") 已切换为 full-only 单一口径, ctx/ss 两轨降级为"以 full 留篇集为行宇宙的条件测度" (conditional-on-full) ——本列的分母不是"ctx 轨自身认定的留篇文章数", 而是与 full 轨完全相同的银行—年度留篇文章子集, 在该子集内部实质信号阈值分类的两根轴中, 相似轴 (high_sim) 确实改用实体窗口文本重新计算 (policy_cosine_sim_ctx); 但词频轴 (high_freq) 依赖的 fintech_distinct_keywords 在 stage 12 `news_fintech` 只生产单一 track-agnostic 列, 无 `_ctx` 同轨变体 (runner.py::_classify_policy_quadrants 在 kw 轨、`_sim_sfx='_ctx'` 时找不到 `fintech_distinct_keywords_ctx`, 优雅回退复用 full 轨的 `fintech_distinct_keywords` 列并记日志披露), 因此本列 ctx 轨的"稳健性"实际只体现在相似轴, 词频轴仍是基于完整正文重新计的关键词去重命中数, 并非在实体窗口内重新扫描。这一设计保证了三轨面板值的可比性 (相同分母下的测度替代), 但也意味着 ctx 轨相对 full 轨的差异全部来自相似轴收窄, 而非两轴同步收窄; 若某项结论在 full 与 ctx 两轨下方向一致、幅度相近, 构成该结论不依赖于相似轴文本抓取窗口选择的证据, 但不能据此推断词频轴同样经过了窗口收窄的检验。
使用本列做机制稳健性检验时应注意: ctx 轨的相似轴取自标题 + 目标银行实体窗口, 与 full 轨的整篇正文相比, 天然更容易漏掉那些"政策对齐信号出现在文章后段、与银行主体提及并不紧邻"的报道——例如先叙述宏观金融科技行业趋势、再在文末落回具体银行业务落地细节的写作结构, 在 ctx 窗口下可能只捕捉到前者的泛化提及而非后者的实质业务信号。这意味着 ctx 轨相对 full 轨可能系统性低估相似轴达标率、进而拉低"实质"占比、抬高"象征/token"占比的可能性应在解读回归系数时纳入考量, 而词频轴 (由于复用 full 列) 不引入这一方向的偏差; 这正是本项目将三轨设计为并排稳健性检验而非单一权威测度的方法论初衷。

## VAR: subst_adopt_kw_p50_ss

【变体差分】
本列是家族的 ss (同句共现) 轨稳健性版本: 文本扫描范围进一步收窄为标题 + 目标银行与金融科技词在同一句子内共现的片段 (`content_ss`, 判据原语为银行∧金科同句, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 是三轨中判据最严格的一支。ss 轨的回退语义镜像 ctx 轨: 若某篇留篇文章内不存在银行∧金科同句共现, 则 `content_ss` 退化为使用全文 body (等同于该篇文章的 full 文本), 并将 `ss_is_fallback` 标记为 True, 该回退文章仍计入与 full/ctx 两轨相同的 `n_articles` 分母, 不做孤儿式剔除。与 ctx 轨相同, 本列同样受 2026-06-29 full-only 留篇门控约束——分母是 full 轨认定的留篇文章集合, 而非 ss 轨自身独立圈定的样本, 即该列是"以 full 留篇集为行宇宙"的条件测度轨。与 ctx 轨的情形完全一致, 本列真正按同句片段重新计算的只有相似轴 (policy_cosine_sim_ss); 词频轴的 fintech_distinct_keywords 在 stage 12 无 `_ss` 同轨变体, runner.py::_classify_policy_quadrants 同样优雅回退复用 full 轨词频列, 因此 ss 轨"仅在该子集内部重新扫描"的表述只对相似轴成立, 词频轴仍基于完整正文的关键词去重命中数, 这一点在解读"同句共现判据是否提供增量信息"时须与相似轴的收窄效果分开归因。ss 轨、ctx 轨、full 轨三者各自 just-identified 并排、互为稳健性、不分主次, 铁律同样禁止把三轨系数混入同一个过度识别的 Hansen J 联合检验; 三者共同构成对"实质采纳"判定是否对文本抓取窗口的宽严选择敏感这一问题的完整稳健性证据链。
由于同句共现判据 (银行∧金科出现在同一句) 比 ctx 轨的实体窗口更为苛刻, 本列在实践中通常呈现比 ctx 轨更高的回退比例——大量报道虽在标题或整体正文层面涉及银行与金融科技的关联, 但二者恰好落入同一句子的情形相对少见, 触发回退后该篇文章即退化为 full 文本重新扫描。这一现象是判据设计的自然结果, 不代表数据质量问题; 分析者若观察到 ss 轨与 full 轨在数值上高度接近, 应首先核对回退比例是否偏高, 而非直接将其解读为"同句共现判据对实质采纳分类没有增量信息"。三判据敏感性 (full/ctx/ss) 与本家族独立于阈值梯子 (p25/p50/p75) 和信号来源梯子 (kw/int) 正交并存, 三条梯子互不交叉组合, 避免了列数爆炸式增长, 也避免了把不同维度的稳健性检验混为一谈。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Chen, X., Wan, P., Ma, Z., & Yang, Y. (2024). Does corporate digital transformation restrain ESG decoupling? Evidence from China. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-024-02921-w
Bian, W., Wang, S., & Xie, X. (2023). How valuable is FinTech adoption for traditional banks? European Financial Management. https://doi.org/10.1111/eufm.12424
<!-- rendered-citations:end -->
