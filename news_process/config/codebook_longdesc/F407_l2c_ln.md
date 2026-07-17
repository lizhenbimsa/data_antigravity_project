---
family_id: F407
columns:
- ln_ft_articles
- ln_nf_articles
unit: 无量纲对数变换计数 (媒体报道篇数经 ln(1+n) 压缩后的银行-年尺度指标)
formula: 'ln_ft_articles = ln(1 + ft_dedup_n_articles); ln_nf_articles = ln(1 + nf_n_articles); 其中 ft_dedup_n_articles 取自 40_article_bank_level 经 (target_bank, 标题, 日期) 去重后的金融科技报道计数, nf_n_articles 取自 build_non_fintech anti-join 输出经同一去重基聚合的非金融科技报道计数; all_n_articles = ft_dedup_n_articles + nf_n_articles 为同基总量, fintech_share = ft_dedup_n_articles / all_n_articles'
producer: pipeline\falsification\controls.py
upstream:
- 12_fintech_news_full.parquet
- 40_article_bank_level.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: 'Shift-share designs: Theory and inference'
  venue: The Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 1949-2010
- doi: 10.1016/j.jfineco.2024.103957
  type: journal
  authors: Vives, X., & Ye, Z.
  year: 2025
  title: Information technology and lender competition
  venue: Journal of Financial Economics
  vol: '163'
  pages_or_artno: Article 103957
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: 'Meet the press: Survey evidence on financial journalists as information intermediaries'
  venue: Journal of Accounting and Economics
  vol: '73'
  issue: 2-3
  pages_or_artno: '101455'
- doi: 10.1016/j.irfa.2024.103223
  type: journal
  authors: Yu, M., Hu, X., & Zhong, A.
  year: 2024
  title: Network centrality, information diffusion and asset pricing
  venue: International Review of Financial Analysis
  vol: '93'
  pages_or_artno: '103223'
- doi: "10.1111/abac.70024"
  type: "journal"
  authors: "Cho, M., & Choi, A."
  year: 2025
  title: "Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone?"
  venue: "Abacus"
  pages_or_artno: "abac.70024"
new_dois: []
---

## CORE

【构念与来源】
本家族 F407 (`l2c_ln`) 收录 stage 51 落假检验 (falsification test) 阶段产出的一对对数计数控制变量: `ln_ft_articles` 与 `ln_nf_articles`。两列共同的构念是"银行-年层面的媒体报道强度", 但分别度量两个互斥且相加为总体的子集: 前者是已进入面板的金融科技报道计数经去重后的对数形式, 后者是与之互补的非金融科技银行报道计数经同一变换后的对数形式。二者的存在理由不是描述媒体关注度本身 (那是 P2 attention 论文的领地), 而是作为 Hassan 等 (2019) 式"信息量对照赛马"的一对挤出弹性 (crowding-out elasticity) 控制项: 论文的核心主张是金融科技语调 (`llm_vote_tone_full` 等) 对银行结果变量 (如融资成本) 具有超出"新闻数量效应"的增量解释力; 若不把普通新闻的规模也放进同一回归, 读者无法排除"只要报道多、不论内容, 银行结果就会变化"这一竞争性解释 (H0)。ln_ft_articles 与 ln_nf_articles 正是把这两类报道规模都转成可比尺度后并列挂入面板, 供稳健性回归同时控制。

产出该列的 producer 是 `pipeline/falsification/controls.py` (thin shim `51_falsification_test.py` 调用), 处理链条分五步: (1) `build_non_fintech` 用 anti-join 从"过滤前全量银行新闻" (`12_fintech_news_full.parquet`, 与 `11_bank_news.parquet` 逐行 1:1、仅多出 `is_fintech_news` 等 7 列金融科技标注) 中减去已进面板的金融科技文章 (`40_article_bank_level.parquet`), 复合键为 (target_bank, 标题, 日期), 双侧先各自 `drop_duplicates` 再取集合差集, 对应 Hassan (2019, QJE) Table 7 的互补划分思路; (2) `aggregate_non_fintech` 按 (target_bank, year) 聚合出 `nf_n_articles`; (3) `merge_to_panel` 把这两条计数序列同时 left join 回 `40_panel_yearly.parquet`, 并在此步生成 `ln_ft_articles = ln(1 + ft_dedup_n_articles)` 与 `ln_nf_articles = ln(1 + nf_n_articles)`。这一步同时构造 `all_n_articles`(两者之和, 同基) 与 `fintech_share = ft_dedup / all_n_articles`, 三者共享同一套"去重计数"分子分母口径, 避免出现"一个按物理篇数、一个按去重篇数"的尺度不一致问题——这正是本文件 producer 源码注释中反复强调的"数新闻要用同一把尺子"。

【方法学与计算】
对数变换采用 Fang & Peress (2009) 在媒体覆盖度文献中确立的标准做法 `ln(1+count)`, 而非直接对原始计数取自然对数, 目的是容纳银行-年格中报道数为零的情形 (零 + 1 = 1, ln(1)=0, 避免 ln(0) 未定义或需要人为丢行)。两列的计数基均为"去重后的稿件数", 而非物理篇数——物理篇数会把同一稿件在多家媒体的转载都计入广度维度 (对应另一独立列 `nf_media_breadth`), 与"稿件数"这一时间序列口径混为一谈会系统性夸大挤出关系的统计显著性。producer 通过 `attrs` 机制在 anti-join 阶段就暴露 `nf_media_breadth_physical`(物理口径, 转载计入) 与 `ft_dedup_agg`(去重口径) 两条并行统计, 供 `aggregate_non_fintech` 与 `merge_to_panel` 分别按各自用途正确取用, 且下游有逐行断言校验"去重 fintech 计数 ≤ 物理 n_articles"以防口径倒挂。计算全程为纯 pandas/numpy 确定性运算, 不依赖 LLM 或嵌入 API, 无随机性、无缓存 miss 风险, 跨机重跑理应逐位可复现 (除非上游 anti-join 的输入文件本身变化)。若某银行-年格全年无任何该类报道, 计数为 0、对数值为 0——这并不等价于"零分享 (zero coverage) 未定义"这一独立诊断标记 (由 `merge_to_panel` 单独维护的 `zero_coverage` 指示列承担, 二者用途不同, 不应混淆)。

【文献定位】
该对数计数对照组的构造逻辑直接承袭 Hassan 等 (2019) 处理"政治风险语调是否只是新闻量的副产品"的做法, 也呼应更广泛的媒体覆盖度-资产定价文献传统 (Fang & Peress, 2009 关于媒体覆盖度与横截面收益的开创性发现)。就信息中介角色而言, Call, Emett, Maksymov & Sharp (2022, *Journal of Accounting and Economics*) 通过对财经记者的问卷调查证实, 记者在决定报道数量与角度时存在系统性的信息筛选行为, 这意味着"报道篇数"本身就是携带信息的选择结果, 而非中性的关注度噪声——这构成了本列作为控制变量而非单纯噪声吸收项的理论合法性。就报道规模在信息扩散网络中的作用而言, Yu, Hu & Zhong (2024, *International Review of Financial Analysis*) 发现网络中心性与信息扩散强度共同驱动资产定价异象, 提示报道规模的挤出效应需要在网络/媒体结构层面加以控制才能得到干净的识别。就方法论周边, Adão, Kolesár & Morales (2019, *The Quarterly Journal of Economics*) 关于 shift-share 设计推断的系统性讨论, 为本仓库并行存在的 Bartik 式暴露度量与本列这类简单计数对照控制提供了统计推断上的谨慎参照——即便 ln_ft_articles/ln_nf_articles 本身不是工具变量, 但其与核心处理变量共线时的推断问题遵循同一族"加总层面构造变量标准误易被低估"的一般性告诫。就信息技术如何重塑金融机构竞争格局而言, Vives & Ye (2025, *Journal of Financial Economics*) 的分析框架呼应了本仓库"金融科技报道是否携带增量信息"这一核心问题意识: 若信息技术确实重塑了银行间竞争与信贷配置, 则金融科技相关报道的语调理应比单纯的报道数量携带更多定价相关信息, 这正是 ln_ft_articles/ln_nf_articles 这对挤出弹性控制变量存在的经验必要性所在。 就“报道量与语调分列建模”这一范式的近期存在性而言, Cho 与 Choi (2025) 在 *Abacus* 的研究把客户公司的媒体报道量与报道语调作为两个并列的公司-年媒体变量, 用以解释审计师的劳动投入配置, 其变量分工恰与本项目把报道篇数 (ln_ft_articles/ln_nf_articles) 与语调 (log_sent) 分列为两族指标的做法同构, 构成该建模范式的近期存在性证明。迁移边界须如实标明: 原文覆盖计数基于英文商业新闻数据库的公司-年匹配、语调为正负词占比类构造, 本列则基于中文媒体语料经 (target_bank, 标题, 日期) 去重且区分金科/非金科两类分子, 层级为 bank-year 而非 firm-year、DV 亦不同; 故该文仅锚定“量-调分列”这一建模范式的存在性, 不锚定具体测度公式。
## VAR: ln_ft_articles

【变体差分】
`ln_ft_articles` 是"处理组"计数的对数形式: 分子取自已经进入 `40_article_bank_level.parquet` 面板的金融科技相关银行报道, 按 (target_bank, year) 聚合后的去重篇数 (`ft_dedup_n_articles`, 与 `fintech_share` 分子同源), 再经 `ln(1+n)` 变换。该列与家族内的 `ln_nf_articles` 共同构成一对互斥且求和为 `all_n_articles` 的挤出弹性配对: 二者在设计上不是同一构念的不同轨道或不同模型, 而是同一"报道规模"构念下按内容主题 (是否金融科技) 二分后的两个子集, 属于对照组/处理组式的并列关系, 而非本仓库其它家族常见的 full/ctx/ss 三轨或 co-primary 双轨嵌入意义上的"互为稳健性并排"。`ln_ft_articles` 的计数基口径与面板主变量 `fintech_share`(分子) 及三份 stage 21 情感 LLM 输出所依赖的留篇门控 (full-only, 2026-06-29 起生效) 是一致的——即只有 `llm_verified_full == True` 且成功挂入 `40_article_bank_level.parquet` 的文章才计入该分子, 因此该列的样本宇宙隐含继承了 stage 21 的三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 投票门控结果, 不会把 LLM 判定非银行-金融科技相关的候选文章计入。`run_diagnostics` 步骤把该列 (经 ln_ft/ln_nf 相关系数) 用作挤出弹性的机械关联检测项之一, 与情感三轨的 Pearson/Spearman 相关矩阵并列输出诊断, 但两者在回归设计中各自扮演不同角色: 情感三轨是待检验的处理变量族, `ln_ft_articles` 是需要与处理变量做机械关联排查的规模控制项, 二者不应被误当作同一构念的稳健性替代而混入同一 over-identified 设定。

## VAR: ln_nf_articles

【变体差分】
`ln_nf_articles` 是"对照组"计数的对数形式, 分子来自 `build_non_fintech` 反连接 (anti-join) 得到的非金融科技银行报道集合——即全量银行新闻 (`12_fintech_news_full.parquet`, 过滤前, 含 `is_fintech_news` 标注供细分诊断) 剔除掉已进入金融科技面板的报道后剩余的部分, 按 (target_bank, 标题, 日期) 复合键先各自去重再取集合差集, 随后按 (target_bank, year) 聚合为 `nf_n_articles` 并经 `ln(1+n)` 变换。与 `ln_ft_articles` 相对, 该列刻意排除了任何金融科技语义标注, 既包含"关键词未匹配"也包含"关键词匹配但被 stage 21 三家 LLM 投票拒绝"的两类文章 (这正是 producer 特意读取带 `is_fintech_news` 列的 `_full` 版本而非精简版 `11_bank_news.parquet` 的原因, 否则会静默丢失这一诊断细分能力), 从而使 `ln_nf_articles` 成为一个纯粹的"银行一般新闻曝光规模"代理变量, 用于回答"如果控制了银行整体被报道的频率, 金融科技语调是否仍然显著"这一 H1 假设检验问题。该列与 `ln_ft_articles` 共享严格相同的去重基与对数变换公式, 唯一差异是分子所属的内容子集互斥且完备 (两者之和恒等于 `all_n_articles`), 因此在回归设计上二者天然应当同时进入同一个控制变量集合 (而非二选一或分轨稳健性检验), 这与本仓库三轨/co-primary/梯子类"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"的口径要求是两类不同的设计问题——`ln_ft_articles`/`ln_nf_articles` 属于同一控制变量集合内部的互补拆分, 不涉及工具变量的过度识别风险。
<!-- rendered-citations:begin -->
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, Article 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
Cho, M., & Choi, A. (2025). Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone?. Abacus, abac.70024. https://doi.org/10.1111/abac.70024
<!-- rendered-citations:end -->
