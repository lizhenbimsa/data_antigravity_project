---
family_id: F516
columns:
- subst_adopt_int_p75
- subst_adopt_int_p75_ctx
- subst_adopt_int_p75_ss
unit: 比例 (0-1 之间的年度截面占比, bank-year 层级)
formula: 'subst_adopt_int_p{P}{track} = mean_i[ 1(intensity_i >= Q_year(intensity, P)) AND 1(sim_i >= Q_year(sim, P)) | 该行 intensity 与 sim 均已测量 ], 其中 P=75, intensity=fintech_intensity_score{track} (TF-IDF x SIF 加权), sim=policy_cosine_sim{track} (Distel et al. 2026 政策余弦相似度), 年度分位数阈值 Q_year 逐 (track, P) 组合按年份分组计算 (pandas groupby(year).quantile)。'
producer: pipeline\panel\runner.py (`_classify_policy_quadrants` 逐篇分类 + 四象限占比聚合循环, L1978-L2090)
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score{track})
- 16_article_policy_alignment.parquet (policy_cosine_sim{track})
citations:
- doi: '10.2307/2393295'
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: '10.5465/amj.2006.23478255'
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: The Symbolic Management of Strategic Change Sensegiving via Framing and Decoupling
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: '10.1007/s11573-017-0852-x'
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: Digital Finance and FinTech Current Research and Future Research Directions
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: '10.1111/jofi.13412'
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: Sustainability or Greenwashing Evidence from the Asset Market for Industrial Pollution
  venue: The Journal of Finance
new_dois: []
---

## CORE

【构念与来源】
本家族测度银行金科新闻报道中「言行一致的实质性采纳」(substantive adoption) 占该行该年已测量报道的比例, 是四象限文本-语义交叉分类法在 Track B (intensity, 词频强度轨) 上、以年度 P75 (第 75 百分位) 为阈值的一个分位数变体。四象限法源自组织理论「实质与象征」(substance vs. symbolism) 传统 (Westphal & Zajac 1994; Fiss & Zajac 2006): 企业对外沟通可能名实相符 (实质性采纳), 也可能名不符实 (象征性/漂绿式表态)。本项目把这套判据搬到银行金科报道语料上, 用两个正交维度刻画每篇文章: 纵轴是「该文章金科词频强度高不高」(词面上谈金科谈得多不多), 横轴是「该文章与官方金科政策文本语义像不像」(policy_cosine_sim, 参见 Distel et al. 2026 的政策对齐方法学); 词频高且语义像 = Substantive (言行一致); 词频高但语义不像 = Token (洗科技/蹭热点); 词频低但语义像 = Hidden (闷声干大事, 低调但方向对); 词频低且语义也不像 = Irrelevant (与政策无关)。本家族只取 Substantive 这一格, 报的是「该行该年落入 Substantive 象限的文章占比」。

【方法学与计算】
判据以「该年」为参照系逐年重估阈值: 对每一年份, 分别对 intensity 序列与 sim 序列取年度 P75 分位数作为该年的高低分界线 (pandas groupby('year').quantile, 而非跨年固定阈值), 目的是防止行业整体报道热度或政策相似度基线的时间趋势 (如 2020 年后金科报道整体密度上升) 机械抬高或压低"高低"判定, 让"高"始终是相对同年同侪的相对位置而非绝对水平。逐篇分类要求 intensity 与 sim 两列都已实测 (`notna`) 才参与分类, 任一缺测 (如 stage 15/16 优雅早退产出全 NaN) 的行被排除出分类域, 不会被静默计为"低"; 银行-年层面用 groupby mean 聚合逐篇 0/1 指示, pandas mean 天然跳过 NaN, 因此分母是该行该年"两项均已测量"的文章数, 而非全部报道数 — 全年无一篇测量成功的行输出面板级 NaN, 而非伪零 (Allison 2001 关于缺失值不应强填零污染 TWFE 系数的告诫, runner.py 注释明确援引)。Track B (int) 用的词频侧测度是 `fintech_intensity_score`, 一个 TF-IDF 权重与 SIF (smooth inverse frequency) 平滑相结合的连续强度分, 与另一条平行的 Track A (kw, 基于 AC 自动机原始去重关键词计数的离散词频) 互为稳健性并排、不分主次, 分属另一家族 (`subst_adopt_kw_p*`), 本家族只覆盖 int 轨。分位阈值集合是 {25, 50, 75} 三档 (`article_alignment.quadrant_percentiles`), P50 是机制检验基准 (与项目内十余处采用中位数分割的既有惯例一致), P25/P75 是稳健性检验; 本家族固定在 P75, 即"高词频/高相似度"门槛设得更严, 落入 Substantive 象限需要同时排进当年词频与相似度分布的前四分之一, 因此该占比数值上通常低于 P50/P25 版本, 反映的是"高度确信的实质性采纳"这一更保守的子群体。

【文献定位】
四象限判据的理论根基是组织与战略管理文献中「实质 vs 象征」的经典区分: Westphal & Zajac (1994, *Administrative Science Quarterly*) 最早系统区分了企业对外承诺的采纳 (adoption) 与执行 (implementation) 可以脱耦, 部分企业只做象征性承诺而不落实; Fiss & Zajac (2006, *Academy of Management Journal*) 进一步刻画了战略变革中"框定与脱耦"(framing and decoupling) 的机制, 即企业如何通过语言沟通策略性地管理利益相关者对其实际行为的感知, 这正是本项目区分"词频高但语义不像政策"(Token, 蹭热点式脱耦) 与"词频高且语义像政策"(Substantive, 名实相符) 的理论对应。将该框架应用到中国银行业金融科技语境, 直接的构念出处是 Gomber, Koch & Siering (2017, *Journal of Business Economics*) 对金科 (FinTech) 研究议程的界定, 本项目媒体文本对齐官方政策文件的做法呼应了近年文本-语义"言行是否一致"实证研究的方法学取向, 如 Duchin, Gao & Xu (2025, *The Journal of Finance*) 在可持续发展披露文献中检验企业环境信息披露与其真实资产市场行为是否脱钩的证据设计思路; 本家族的 Substantive/Token/Hidden 三分法在测度逻辑上与该类"披露-行为一致性"检验同构, 只是把披露文本换成了第三方媒体报道、把行为验证换成了与官方政策文本的语义相似度。

【与相邻测度的构念区分】
本家族与同族 `token_adopt_int_p75` (Token 象限)、`hidden_adopt_int_p75` (Hidden 象限) 共享同一次逐篇分类过程, 三者互斥且穷尽 (加上未落格的 Irrelevant), 但各自独立作为面板列输出, 不应把三者相加视为单一构念的分解; 与平行的 Track A (kw) 版本 `subst_adopt_kw_p75` 互为稳健性并排, 二者分子逻辑相同、词频侧测度不同, 禁止混入同一 over-identified 设定同时作为工具或控制。与全年份锚点稳健孪生 (`_allv` 后缀, sim 改用跨全语料静态锚点 `policy_cosine_sim_allv` 而非逐年 vintage 锚点) 也是并排关系, 本家族 (无 `_allv`) 是 vintage 主轨。

## VAR: subst_adopt_int_p75

【变体差分】
本列是 full 轨 canonical 版本: 词频侧取 `fintech_intensity_score` (无三轨后缀的原始篇章强度分, 基于全文文本), 相似度侧取 `policy_cosine_sim` (无后缀, 全文-政策余弦相似度)。年度 P75 双门槛联合判定, 参与分类的文章范围与 full-only 留篇门控 (2026-06-29 铁律) 一致 — 后续 15/16 阶段的 fintech_intensity 与 policy_cosine_sim 计算本身仍按各自 stage 的产出行范围, 但该行是否被视为"一篇有效银行金科报道"最终以 stage 21 `llm_verified_full` 为准, 三轨 (full/ctx/ss) 在此意义上共享同一行宇宙, 只是各轨内部文本片段与测度值不同。作为 int 轨三档分位数 (P25/P50/P75) 之一, 本列与 `subst_adopt_int_p25`/`subst_adopt_int_p50` 各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定; P75 相对 P25/P50 的差分含义是"高置信度实质性采纳"子样本, 门槛更高、占比数值系统性更低, 用于检验主结论 (通常以 P50 为基准) 是否对分位数选择敏感。

full 轨是"以整篇正文为分析单元"的默认视角: 不做实体窗口截取、不做同句共现约束, intensity 与 sim 两侧测度都建立在文章全文之上, 因此对"这篇报道到底在多大篇幅、多大范围内谈及金科与政策的关系"给出的是最不挑剔、覆盖面最广的估计, 代价是可能把与银行-金科核心叙事无关的段落 (如文末免责声明、行情快讯、无关业务简介) 也计入词频与语义相似度的分母, 从而稀释"高词频/高相似度"的判定强度。与词典消融梯度、政治词权重梯度等其它梯子正交, 不与本列同轨混算。本列在四象限体系里与 `token_adopt_int_p75_full`(隐含 full, 无后缀)、`hidden_adopt_int_p75` 共享同一批逐篇分类结果, 三者互斥占比可在同一图表中并列展示"言行一致/洗科技/闷声干大事"三种媒体呈现模式在银行-年层面的相对权重, 但计量设定中应各自单独进入回归, 不建议把三者作为同一 RHS 的共线变量同时纳入。

## VAR: subst_adopt_int_p75_ctx

【变体差分】
本列是 ctx 轨: 相似度侧改用 `policy_cosine_sim_ctx` (标题+实体窗口文本算出的政策余弦相似度), 词频侧优先取同轨变体 `fintech_intensity_score_ctx` (若该列存在于对齐后的文章级表, 否则代码路径记录日志后仍复用 full 列 `fintech_intensity_score`, 因其在当前 schema 下已产出同轨变体, 故实际生产口径下 int 轨词频亦走 ctx 版本, 与 full 轨相似度/词频均不同源)。ctx 轨与 full/ss 轨互为稳健性并排、不分主次, 禁止混入同一 over-identified Hansen J; ctx 文本窗口聚焦标题与目标银行/金科实体邻近上下文, 剔除全文中与银行-金科关系无关的噪声段落, 因而该轨算出的相似度与词频强度理论上比 full 轨更聚焦于"报道是否真的在谈该行的金科举措", Substantive 占比在 ctx 轨下可能因噪声降低而与 full 轨产生系统性差异, 属预期的测度口径差异而非矛盾结果。年度 P75 分位阈值仍按 ctx 轨自身的 intensity/sim 分布逐年独立估计, 不与 full 轨共享阈值。

从构念动机上看, ctx 轨的存在是为了回应"全文轨可能被无关段落稀释"的担忧: 如果一篇报道只在导语提到某银行推出金科产品, 后续大段篇幅转去讨论宏观利率政策或其它无关业务, full 轨的 intensity/sim 会把这些无关段落也纳入计算, 而 ctx 轨通过截取标题与银行/金科实体邻近窗口, 理论上能更精准地捕捉"报道核心是否确实在谈该行的金科实践", 因此 ctx 轨下的 Substantive 判定被认为对"标题党/蹭热点"式报道更敏感、更不容易把噪声误判为高强度采纳信号。留篇门控仍以 stage 21 `llm_verified_full` 为准, ctx 轨行宇宙是 full 留篇集合的子集测度, 不额外扩大或缩小样本范围, 只改变同一批文章内部的文本片段与由此派生的强度/相似度数值。ctx 轨与 kw 轨对应列 `subst_adopt_kw_p75_ctx` 同样互为稳健性并排。

## VAR: subst_adopt_int_p75_ss

【变体差分】
本列是 ss 轨 (同句共现轨): 相似度侧改用 `policy_cosine_sim_ss`, 词频侧优先取同轨变体 `fintech_intensity_score_ss`; ss 轨是 ctx 轨的同句共现孪生, 其底层文本 `content_ss` 定义为标题 + 目标银行∧金科词在同一句 (±N 句窗, 默认 N=1) 内共现的句窗摘录, 语义上比 ctx 更严格地要求银行与金科概念在同一叙述单元内出现。ss 轨回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 退化为全文 body (`ss_is_fallback=True`), 此时 ss 轨的 intensity/sim 测度实质上退化为对全文的重新计算, 不等价于 full 轨列 (可能因下游 stage 独立重跑而数值略有差异), 但构念上仍标注为"未能满足同句共现条件"的优雅降级而非缺失。ss 轨与 full/ctx 轨同样互为稳健性并排、不分主次, 三轨禁止混入同一 over-identified Hansen J 设定; 与 full/ctx 轨相同, 年度 P75 阈值按 ss 轨自身分布逐年独立估计, 分母为该行该年 ss 轨下 intensity 与 sim 均已测量的文章数 (含回退全文的行, 只要测度非 NaN 即计入)。

ss 轨是三轨中最严格的一层: 它要求银行主体与金科概念不只是"同篇出现"(full)、也不只是"同一实体窗口内出现"(ctx), 而是"同一句话里出现", 这对应文本分析中"共指强度"最高的判据, 目的是排除那些标题谈银行、正文谈金科但两者从未在同一叙述单元里被联系起来的报道。对于确实满足同句共现条件的文章, ss 轨下的 Substantive 判定被认为最能代表"报道明确把该行与某项金科实践直接挂钩、且用词像政策文本"这一强证据情形; 而对回退到全文的文章, ss 轨占比退化为与 full 轨高度相关但不完全相同的量 (因为 stage 15/16 各轨独立计算, 不共享中间产物)。使用者若关心"共指强度"本身对结果的影响, 应结合 `ss_is_fallback` 指示列做子样本切分, 而非直接把 ss 轨占比与 full/ctx 轨占比相减来解读"共指效应"的大小, 三轨差异更适合作为方向一致性的稳健性证据, 而非点估计的可加分解。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital Finance and FinTech Current Research and Future Research Directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
<!-- rendered-citations:end -->
