---
family_id: F518
columns:
- subst_adopt_kw_p25
- subst_adopt_kw_p25_ctx
- subst_adopt_kw_p25_ss
unit: 银行-年内文章占比 (0-1 区间无量纲比率)
formula: 'subst_adopt_kw_p{trk} = mean_i[ (freq_i >= Q_year(freq, 0.25)) AND (sim_i
  >= Q_year(sim, 0.25)) | freq_i, sim_i notna ], 其中 freq = fintech_distinct_keywords
  (Track A 关键词轨, 逐轨变体优先 {ctx,ss} 本轨列, kw 轨为 track-agnostic 元数据则回退
  full 列), sim = policy_cosine_sim{_ctx,_ss} (Stage 15 文章-政策余弦相似度), 分位阈值 Q 为年度内样本分位数
  (groupby year transform quantile), 分母 = 该银行-年内 freq 与 sim 双双非缺测的文章数'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (L312-335) + 面板聚合循环
  (L1997-2090)
upstream:
- 15_fintech_intensity (fintech_distinct_keywords)
- 16_article_policy_alignment (policy_cosine_sim / _ctx / _ss)
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
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions"
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: "The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling"
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial
    Pollution'
  venue: The Journal of Finance
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: 'Stress Testing Banks'' Digital Capabilities: Evidence from the COVID-19
    Pandemic'
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2618-2646
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability
    Disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"银行金融科技相关新闻报道里, 究竟有几成是言行一致的实质性投入报道"这一构念, 落在项目四象限机制检验体系里的"Substantive"(实质采纳)格。四象限的理论出处是组织理论里"实质与象征管理"(substance vs. symbolism) 传统: Westphal & Zajac (1994, ASQ) 最早区分了公司治理措施在"采纳"(adopt) 与"落实"(implement) 之间的脱耦, 其后续 (1998, ASQ) 与 Fiss & Zajac (2006, AMJ) 把这一区分系统化为"象征管理"(symbolic management) 分析框架; 本项目把这一逻辑搬到银行金融科技报道的文本测度上, 用两个独立信号交叉分类每篇文章: 一是"说得多不多"(词频信号, freq), 二是"说得像不像官方政策"(语义对齐信号, sim)。词频高且语义对齐也高的文章, 被判定为"言行一致"的实质采纳报道 (Substantive); 词频高但语义对齐低的, 是"洗科技"式的空话报道 (Token, 对应 greenwashing 文献里 "cheap talk" 的操作化, 参见 Duchin, Gao & Xu 2025, JoF 对可持续性资产市场里 "sustainability vs. greenwashing" 的甄别思路, 以及 Kim & Lyon 2015, Organization Science 关于 greenwash/brownwash 的经典区分); 词频低但语义对齐高的, 是"闷声干大事"型报道 (Hidden); 两者都低的则与政策议题无关 (Irrelevant, 未单独出面板列)。本家族 (F518, subst_adopt_kw_p25) 是这四象限中的 Substantive 格、词频侧走 Track A (kw, 关键词计数) 轨、分位阈值取 P25 (第 25 百分位)、政策相似度锚点取 vintage 主轨 (非 _allv 全年份静态锚点变体) 的三个文本轨版本; 姊妹家族在 P50/P75 阈值、Track B (int) 词频轨、_allv 锚点变体、以及 token_adopt_/hidden_adopt_ 前缀上逐一铺开, 构成完整的稳健性梯子矩阵。

【方法学与计算】
计算发生在 `pipeline/panel/runner.py::_classify_policy_quadrants` 与其调用方 (面板聚合循环 L1997-2090)。逐篇分类分两步: 第一步在年度内对词频列 (freq, kw 轨=`fintech_distinct_keywords`, Stage 15 产出的 AC 自动机去重关键词数) 与相似度列 (sim, `policy_cosine_sim`, Stage 16 政策对齐产出) 各自算出该年样本的 25 分位阈值 (`groupby('year').transform(lambda x: x.quantile(0.25))`); 第二步逐篇比较: freq ≥ 该年 P25 阈值记为"高词频", sim ≥ 该年 P25 阈值记为"高对齐", 两者同时为真记为 Substantive 指示 = 1, 否则 = 0。关键的边界处理是"未测量"语义: 只有 freq 与 sim 同时非缺测 (notna) 的文章才参与 0/1 分类, 任一缺测则该文章的指示值保持 NaN 而非被误判为 0 (`.where(measured)`) — 这是 2026-06-11 (fix omni-g-runner-03/g-runner-11) 修复的一处历史缺陷: 旧实现把 `NaN >= threshold` 隐式当作 False, 会把 Stage 15 优雅早退产生的全 NaN `policy_cosine_sim` 静默计成"低对齐", 从而把大量高词频文章错分进 Token 格。第三步是银行-年聚合: 按 `(target_bank, year)` 分组对逐篇 0/1/NaN 指示取 `mean`, pandas 的 `mean` 天然跳过 NaN, 因此聚合结果的隐含分母是"该银行-年内 freq 与 sim 均已测量的文章数", 而非该银行-年的全部文章数; 若某银行-年全部文章都未测量 (例如政策锚点缺失), 聚合结果为面板级 NaN 而非人为填零的 0, 这是 v6/F3 修复移除 `fillna(0.0)` 后确立的"无数据=未测量"契约 (Allison 2001 §3 关于强填 0 会污染 TWFE 系数的论述), 避免下游回归把测量缺失误读为"零实质采纳"。

无后缀主轨 (subst_adopt_kw_p25) 使用词频与相似度均为 full 文本轨 (标题+正文全文) 的信号; `_ctx`/`_ss` 两个姊妹变体则分别切到 ctx (标题+实体窗口) 与 ss (标题+银行∧金科同句±N窗) 文本轨的词频、相似度信号重新独立分类与聚合, 三者互为稳健性、各自 just-identified 并排、禁止混进同一 over-identified Hansen J 估计。⚠ 需要特别说明的是"词频轨"内部的一个非对称: kw 轨的 `fintech_distinct_keywords` 在项目里被视为 track-agnostic 元数据 (即该指标本身不区分 full/ctx/ss 三个文本窗口, 只有 int 轨 `fintech_intensity_score` 才产出真正的 `_ctx`/`_ss` 独立词频变体), 因此 `_ctx`/`_ss` 后缀列在词频侧实际上复用的是 full 轨的 kw 词频列, 只有相似度信号 (sim) 是真正切到对应文本轨的 `policy_cosine_sim_ctx`/`policy_cosine_sim_ss`; 这一"部分轨道化"处理在源码注释中被明确记录并逐条日志披露, 不构成静默口径漂移。此外, 本家族只覆盖 vintage 锚点 (相似度阈值来自动态更新的 `policy_cosine_sim`), 与之并排的还有 `_allv` 全年份静态锚点变体 (阈值改用 `policy_cosine_sim_allv`), 两个锚点变体同样是互为稳健性、不分主次的并排测度, 落在其他家族文件里, 本家族条目不涉及。

【文献定位】
四象限分类法的构念根基是组织理论里区分"名义采纳"与"实质落实"的经典脱耦 (decoupling) 传统。Westphal & Zajac (1994, ASQ) 首次系统展示公司治理层面的长期激励计划存在"采纳但不落实"现象, 揭示了单纯观测"是否宣布采纳某项措施"会高估实际治理变革的风险; 其后续研究 (1998, ASQ) 进一步刻画了公司如何通过象征性治理改革安抚股东而不必真正改变行为, 而 Fiss & Zajac (2006, AMJ) 把这一逻辑扩展为"象征管理"的一般理论, 强调框架化 (framing) 与脱耦 (decoupling) 是组织应对制度压力的两种并行机制。本项目把银行新闻报道中的"词频"信号类比为组织的"宣称/采纳"信号、"政策语义对齐"信号类比为"落实/实质"信号, 借用这一分类逻辑构造文章级的实质-象征甄别。在金融文献里, 与之平行的经验设计是 greenwashing/cheap talk 甄别: Kim & Lyon (2015, Organization Science) 区分了企业可持续性披露中的"过度渲染"(greenwash) 与"过度谦逊"(brownwash), Duchin, Gao & Xu (2025, JoF) 在资产市场层面甄别可持续性投入的真实性与漂绿的边界, 两者与本家族"词频高但语义不对齐=Token/洗科技"的构造思路同构。银行数字化转型的实证背景则参考 Kwan, Lin, Pursiainen & Tai (2024, JFQA) 关于银行数字能力压力测试的证据, 该文说明银行在报道/宣称层面的数字化投入未必与实际韧性能力对齐, 与本家族甄别报道"言行是否一致"的核心问题意识一致。本家族测度的直接上游信号 (词频=Stage 15 fintech_intensity 关键词计数; 相似度=Stage 16 article_policy_alignment 余弦相似度) 各自在其所属家族文件里另有独立方法学与文献定位, 本节聚焦四象限分类本身的构念来源, 不重复展开上游信号的构造细节。

## VAR: subst_adopt_kw_p25

【变体差分】
本列是家族的 full-track 主轨, 也是三个 P25 词频=kw 轨版本中信号来源全部取 full 文本 (标题+正文全文) 的一列: 词频信号 = full 轨 `fintech_distinct_keywords` (Stage 15 AC 自动机在全文范围内扫描去重后的金融科技关键词数), 相似度信号 = full 轨 `policy_cosine_sim` (Stage 16 用全文文本与政策文本嵌入算余弦相似度), 分位阈值锚点 = vintage 主轨 (动态更新的政策文本, 非 `_allv` 全年份静态锚点)。分类判据是"freq ≥ 该年 P25 分位数 AND sim ≥ 该年 P25 分位数"双高交叉, 两个阈值都取偏低的第 25 百分位, 意味着相对 P50/P75 姊妹列, 本列对"高词频""高对齐"的门槛更宽松, 因而 Substantive 格纳入的文章比例天然应高于 P50/P75 版本 (阈值越低越容易同时越过两条线), 这是该家族内部 P25/P50/P75 三档阈值梯子彼此互为稳健性、不分主次并排的构造设计, 三档阈值改变的是"实质采纳"判定的严格程度, 而非改变判定逻辑本身; 严禁把三档阈值的分类结果混进同一个 over-identified 工具变量估计。行级分母是该银行-年内 freq 与 sim 同时非缺测的 full 轨文章数, 而非该银行-年全部报道数; 任一信号缺测的文章被排除出分子分母, 全体缺测的银行-年在本列输出面板级 NaN。

## VAR: subst_adopt_kw_p25_ctx

【变体差分】
本列与 canonical 主轨 (subst_adopt_kw_p25) 的唯一差异在相似度信号的文本窗口: 本列的 sim 取 ctx 轨 `policy_cosine_sim_ctx` (标题+实体窗口文本与政策文本的余弦相似度), 而非 full 轨的全文相似度; 阈值同样按年度内 ctx 轨样本重新计算 P25 分位数, 与 full 轨阈值相互独立、不共用同一分位切点。词频信号侧则保持项目既定的"kw 轨 track-agnostic"处理: 由于 `fintech_distinct_keywords` 本身不产出独立的 `_ctx` 变体, 本列词频仍复用 full 轨词频列, 只有相似度一侧真正切到 ctx 文本窗口, 这一点在 producer 源码注释中逐条记录、非静默复用。ctx 轨与 full 轨、ss 轨三者互为稳健性并排比较: ctx 把关注范围收窄到银行与金融科技实体附近的局部语境, 若某篇报道全文夹杂大量与金融科技无关的内容 (如银行常规业务报道里偶然提及金融科技), ctx 轨的相似度信号会比 full 轨更贴近"报道主体是否真谈金融科技政策", 但也可能因窗口过窄丢失全文语境里分散表述的政策关联信息; 与 full/ss 两轨的差异属于测度口径选择, 不隐含优先级, 三轨各自 just-identified、禁止混入同一 over-identified Hansen J 估计。分母同样是该银行-年内 ctx 轨 sim 与 (复用的) full 轨 freq 双双非缺测的文章数, 与 full 轨主列的分母未必相等 (ctx 相似度可能因实体窗口抽取失败而缺测, 即便 full 轨相似度已测量)。

## VAR: subst_adopt_kw_p25_ss

【变体差分】
本列与 canonical 主轨的差异同样局限于相似度信号的文本窗口, 但收窄程度比 ctx 更严格: 本列的 sim 取 ss 轨 `policy_cosine_sim_ss` (标题+银行∧金科同句±N窗文本, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认±1句), 阈值同样按年度内 ss 轨样本独立计算 P25 分位数。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行与金融科技词的同句共现, 则该文章的 `content_ss` 在 Stage 14 物化阶段已回退为全文 body、`ss_is_fallback` 标记为 True, 其相似度计算实质上退化为接近 full 轨的信号 (共享 `n_articles` 分母口径); 若上游 `FINTECH_AC` 词典本身为 None, 则全体文章的 `*_is_fallback` 标记为 True, 整族信号优雅降级但不产生虚假的高置信度分类。词频信号侧同样复用 full 轨 `fintech_distinct_keywords` (kw 轨 track-agnostic, 无独立 ss 变体)。ss 轨相对 ctx 轨的甄别逻辑更严苛: 只有银行与金融科技词在同一句子里紧邻出现的报道, 才被认为是"真正在谈银行的金融科技动作"的强信号语境, 因此 ss 轨的相似度信号理论上比 ctx/full 更少受无关上下文稀释, 但代价是更容易触发回退 (样本覆盖面更窄)。full/ctx/ss 三轨在本列上同样是互为稳健性、各自 just-identified 并排的测度选择, 不设主次, 更不得混入同一个 over-identified 工具变量估计式; 三轨聚焦的是文本窗口口径差异, 与家族内部的 P25/P50/P75 阈值梯子及 kw/int 词频轨选择彼此正交、不交叉组合报告。分母是该银行-年内 ss 轨 sim (含回退样本) 与复用的 full 轨 freq 双双非缺测的文章数。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress Testing Banks' Digital Capabilities: Evidence from the COVID-19 Pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
<!-- rendered-citations:end -->
