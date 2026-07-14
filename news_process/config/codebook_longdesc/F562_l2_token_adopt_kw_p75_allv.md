---
family_id: F562
columns:
- token_adopt_kw_p75_allv
- token_adopt_kw_p75_allv_ctx
- token_adopt_kw_p75_allv_ss
unit: 银行-年占比 (0-1, 文章级二元象限指示的年度均值)
formula: 'token_adopt_kw_p75_allv = mean_articles[ 1{fintech_distinct_keywords >= thresh_p75(freq)} AND 1{policy_cosine_sim_allv < thresh_p75(sim)} ]; 阈值 thresh_p75 取全语料该分布的第 75 百分位 (>= 判高频、< 判低相似, 与 runner.py::_classify_policy_quadrants 的 >=/~>= 布尔代数一致), sim 用全年份静态锚点 policy_cosine_sim_allv (而非逐年滚动 policy_cosine_sim), freq 用 stage 15 AC 去重金科关键词计数 fintech_distinct_keywords'
producer: pipeline\panel\runner.py (象限分类循环, _classify_policy_quadrants 前置掩码 + P{25,50,75} 阈值梯子 + _allv 锚点外层循环) ; pipeline\panel\export.py (STATA_LABELS 象限列注册)
upstream:
- 16_article_policy_alignment.parquet::policy_cosine_sim_allv(_ctx/_ss) (stage 16, Distel et al. 2026 全年份静态政策锚点)
- 15_fintech_intensity.parquet::fintech_distinct_keywords (stage 15, AC 自动机去重金科关键词计数, track-agnostic 元数据)
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
- doi: 10.1080/07350015.2025.2544190
  type: journal
  authors: Kwon, O., Yoon, J., & Yotov, Y. V.
  year: 2025
  title: A generalized Poisson-pseudo maximum likelihood estimator
  venue: Journal of Business & Economic Statistics
  vol: '44'
  issue: '2'
  pages_or_artno: 560-573
- doi: 10.1086/730053
  type: journal
  authors: Fan, H., Liu, Y., Qian, N., & Wen, J.
  year: 2024
  title: "Technological adoption and taxation: The case of China's Golden Tax reform"
  venue: Tax Policy and the Economy
  vol: '38'
  pages_or_artno: 101-122
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列 (token_adopt_kw_p75_allv / _ctx / _ss) 属"银行政策响应象限分类"测度簇的一支, 度量一家银行在某一年度的报道语料中被归入"Token Adoption"(象征性回应/表态式采纳) 象限的文章占比。象限分类的构念来自战略管理与传播学文献里对"cheap talk vs. substantive action"的经典区分: 组织可以在文本层面高频提及某项政策或技术议程 (高关键词密度), 却并不真正与该议程的语义内核对齐 (低政策余弦相似); 反过来也可以在语义上高度贴合政策叙事, 却几乎不使用相关关键词表层符号。生产口径把每篇文章放进一个二维平面: 横轴是与政策/金科议程锚点的语义相似度 (policy_cosine_sim 族, 源自 stage 16 article_policy_alignment, 沿用 Distel et al. (2026) 的文本-政策对齐方法), 纵轴是 AC 自动机扫描出的去重金科关键词计数 (fintech_distinct_keywords, 源自 stage 15 fintech_intensity)。以此平面切出四个象限, 其中 Token Adoption 对应"高关键词表层密度 + 低语义对齐"这一格 (真实源码 runner.py::_classify_policy_quadrants 内联注释直书"洗科技") — 直觉上是银行在文本表层频繁堆叠金科相关词汇, 却并未在语义内核上真正贴合政策/金科议程叙事, 更接近词面蹭热点、表态先行而语义空转的象征性响应; 与之互为对照的是同一象限体系里的 Hidden Adoption("高语义对齐、低关键词表层密度", 源码注释"闷声干大事"——语义已经贴近政策叙事却几乎不使用关键词表层符号, 更像低调落地) 及 Substantive Adoption("两者皆高", 语义与表层同步落地)。三者共同构成一个穷尽的象限划分 (第四格"两者皆低"不计入这三个具名象限), 服务于银行"是否只是嘴上说说"这一机制识别问题, 呼应 Kwan et al. (2024, JFQA) 关于银行数字能力压力测试中"宣称能力"与"实际能力"存在系统性缺口的发现——本象限体系正是把这一"言"与"行"缺口在文本层面量化为可回归的银行-年指标, Token Adoption 一格即对应"言"显著多于"行"的表态式响应。

【方法学与计算】
象限阈值不是单一固定切点, 而是一条稳健性阶梯: 生产口径同时物化 P25/P50/P75 三档百分位阈值 (家族基名 token_adopt_kw_p{25,50,75}), 阈值取自 sim 分布与 freq 分布各自的样本百分位数, 三档阈值各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified 设定 (镜像政治词权重梯子/词典消融梯子先例)。本家族固定在 P75 一档: 相似度与关键词计数两个维度都以第 75 百分位为"高/低"切点, 是该阶梯里门槛最严格的一档 (进入"高"区间需要排在语料前 25% 分位之外)。`_allv` 后缀标记锚点变体: 与不带 `_allv` 的姊妹列 (token_adopt_kw_p75) 相比, 本列的相似度分子不取逐年滚动重估的 policy_cosine_sim, 而取全年份静态锚点 policy_cosine_sim_allv (2026-06-21 引入的全语料稳健孪生, 消除锚点随年份漂移带来的跨年不可比问题); 两个锚点变体 (vintage / _allv) 同样各自 just-identified 并排, 不设主次。计算前置一道 NaN 安全掩码: 仅当 sim 与 freq 双双非缺失的文章才参与象限分类, 未测量的文章 (如 stage 15 优雅早退产生的全 NaN policy_cosine_sim) 不会被静默误判进任一象限, 而是从分类分母中剔除 (分母 = 该银行-年内 sim/freq 双观测的文章数), 避免测量失败被错误折算成"低对齐"或"低采纳"的伪证据。文章级二元命中结果按银行-年取均值, 得到该银行-年报道语料中落入 Token Adoption 象限的文章占比, 值域 [0,1], 亦可读作"象征性响应强度"。三轨版本 (无后缀/_ctx/_ss) 见下方各 VAR 节。

【文献定位】
该象限构念定位在文本分析与组织采纳/合规响应文献的交叉处: 一方面继承 Distel et al. (2026) 的语义-政策对齐方法论作为纵深维度, 另一方面把关键词表层密度 (对应更传统的词典法/关键词法信号) 作为正交的第二维度, 二者交叉切分而非相互替代, 从而把"文本提及"与"文本对齐"两种常被混为一谈的信号显式分离。这一设计呼应 Kwan et al. (2024, JFQA) 在银行数字化压力测试文献中揭示的"能力声称"与"能力实证"之间的鸿沟——本象限体系提供了一个基于公开报道文本、无需依赖银行自我披露的替代性识别策略, 用以刻画银行政策响应的真实性梯度而非仅仅其发声频率, Token Adoption 一格 (高关键词表层密度、低语义对齐) 正对应"声称多于实证"的那一端。Fan et al. (2024) 在中国金税改革情境下考察企业"技术采纳"的表层合规与实质落地之间的分离——企业可以在报表/流程层面完成形式上的技术接入却未真正改变实质经营行为, 这一"表态先行、语义/实质空转"的现象与 Token Adoption 象限"高表层符号密度、低深层语义对齐"的构念方向直接对应, 为本象限体系提供跨情境的构念效度佐证; 需明确该文献研究的是税收征管情境下的技术合规行为而非银行金科报道文本, 佐证限于"表态-落地分离"这一一般性机制类比, 不构成同一实证设定的直接检验。阈值梯度设计 (P25/P50/P75) 采用不依赖单一任意切点的多档并排稳健性检验思路, 这一"不把结论押在单一设定上"的方法论取向与计量文献中对估计量在多种规格设定下做系统性稳健性复核的一般实践相通 (参见 Kwon, Yoon & Yotov 2025, JBES, 该文虽处理的是广义 Poisson-PML 估计量而非文本阈值梯子, 但其对"结论不应依赖单一规格选择"的验证逻辑可类比迁移到本家族的百分位阶梯设计上, 此处引用取其方法论一般性而非实证内容直接对应)。

## VAR: token_adopt_kw_p75_allv

【变体差分】
本列是家族的无轨道后缀 canonical 版本, 对应 full 全文轨: 相似度维度取 policy_cosine_sim_allv (标题+正文全文与政策锚点的语义相似度, 全年份静态锚点), 关键词计数维度取 fintech_distinct_keywords (AC 自动机在全文上扫描的去重金科关键词数, stage 15 产出, 与相似度所用文本范围一致)。二者均在 full 轨上计算, 不存在 track-agnostic 复用问题。命中判据是"关键词计数达到或超过该分布 P75 (高表层密度) 且相似度低于该分布 P75 (低语义对齐)" (`high_freq & ~high_sim`, 对应源码注释"洗科技"); 阈值仍是 P75 一档 (sim/freq 各自取语料 75 百分位), 象限判定与文章留篇门控独立——需注意留篇门控 (2026-06-29 起) 已收窄为 full-only, 但本列的象限分类掩码只看 sim/freq 是否双双非缺失, 不直接复用留篇标记, 因此分母口径与 llm_verified_full 门控的分母不完全等同, 解读时不应把二者混为一谈。作为 P75/_allv 组合的 full 轨基准, 它与下方 _ctx/_ss 两个姊妹列共同构成三轨并排 (互为稳健性、不分主次, 禁混进同一 over-identified Hansen J), 也与不带 _allv 后缀的 vintage 锚点姊妹列构成锚点维度上的并排稳健性对照。在解读该列的银行-年占比时须留意分母是"sim 与 freq 双双非缺失"的文章集合, 而非留篇门控 (llm_verified_full) 集合, 二者虽高度重叠但不严格相等; 若某银行-年该分母极小 (如政策锚点大面积缺失), 占比估计的抽样噪声会显著放大, 建议配合分母篇数一并报告或做 winsorize 处理。作为阈值梯子里最严格的一档, P75 版本相比 P25/P50 更容易把"边界性响应"文章排除出 Token 象限, 因而在实证上通常表现为更保守 (更低) 的占比估计, 适合用作高置信度稳健性对照而非首选主设定; 具体主设定的选择应由论文侧治理文档而非本 codebook 决定, 本列本身在三档阈值里不预设主次地位。

## VAR: token_adopt_kw_p75_allv_ctx

【变体差分】
本列切到 ctx 轨: 相似度维度取 policy_cosine_sim_allv_ctx (标题+实体窗口文本与政策锚点的相似度, 而非全文), 但关键词计数维度存在不对称——fintech_distinct_keywords 是 stage 15 产出的 track-agnostic 元数据 (AC 去重关键词计数本身不区分扫描窗口大小的三轨变体), 因此本列在词频侧复用与 full 轨相同的 fintech_distinct_keywords 列, 只有相似度侧真正切到 ctx 语义空间。这一不对称在 runner.py 象限分类逻辑里有显式注释披露 ("kw 轨的 AC 去重关键词数为 track-agnostic 元数据…复用 full 列并披露"), 解读时须知晓: ctx 轨象限分类的"表层密度"信号实际上仍锚定在全文关键词计数上, 只有"语义对齐"信号是真正的 ctx 窗口测度。若上游 policy_cosine_sim_allv_ctx 缺失 (旧 schema 或未上线), 该 ctx 孪生会被优雅跳过而非报错。本列与无后缀 full 轨、_ss 轨互为稳健性并排, 三轨口径分歧的解读须结合上述关键词侧的 track-agnostic 复用一并考虑, 不能想当然认为三轨在两个维度上都严格独立测量。ctx 轨的实体窗口范围窄于 full 全文, 窗口收窄会同时压缩相似度信号的分母背景 (更聚焦在实体上下文本身), 语义相似度的分布形态与 full 轨可能出现系统性偏移, 而关键词计数侧因 track-agnostic 复用未随窗口收窄而变化, 二者分布形态的相对漂移会影响 Token (高表层密度、低对齐) 象限占比的绝对水平, 但由于阈值 P75 在两个维度上各自独立取自不同分布的百分位, 三轨之间的绝对占比水平并不适合直接相减解读为处理效应, 只适合各自作为独立的、just-identified 的银行-年协变量并排纳入回归做跨轨一致性检验。P75/_allv/ctx 三重设定叠加意味着本列同时处于阈值梯子最严格档、语义锚点全年份静态档、文本窗口收窄档三条正交维度的交汇点, 解读时应逐一交代三条维度各自的设定含义, 避免读者把某一维度的差异误归因于另一维度。

## VAR: token_adopt_kw_p75_allv_ss

【变体差分】
本列切到 ss 轨 (银行与金科词同句共现窗口): 相似度维度取 policy_cosine_sim_allv_ss, 语义对齐信号锚定在"银行∧金科同句"这一最严格的文本窗口上, 是三轨中语境范围最窄、判据最严格的一支; 与 ctx 轨相同, 关键词计数维度同样复用 track-agnostic 的 fintech_distinct_keywords (全文口径), 象限分类里只有相似度侧切到 ss 窗口。ss 轨遵循与三轨文本物化架构一致的回退语义 (镜像 ctx): 若某篇文章不存在银行∧金科词的同句共现, 其 content_ss 在 stage 14 物化阶段即已回退为全文 body 且 ss_is_fallback=True, 该回退语义在 policy_cosine_sim_allv_ss 的分母侧继承——但象限分类本身只看 sim/freq 双非缺失这一前置掩码, 不额外读取 ss_is_fallback 标记, 因此 ss 轨象限占比里既包含"真同句窗口"命中的文章, 也包含因回退而退化为全文口径的文章, 二者在本列内不可分离。若上游 policy_cosine_sim_allv_ss 缺失 (旧 schema / ss 未上线), ss 孪生同样被优雅跳过。本列与无后缀 full 轨、_ctx 轨三轨并排, 互为稳健性、不分主次, 三者禁混进同一 over-identified Hansen J; 与不带 _allv 的 vintage 锚点姊妹列在锚点维度上再形成一层正交并排的稳健性对照。由于 ss 判据 (银行∧金科同句共现) 比 ctx (实体窗口) 更严格, 满足"真同句"条件的文章占比通常小于 ctx 命中率, 相应地 ss 轨里因回退而落回全文口径的文章比例也更高——这意味着 ss 轨的 Token Adoption 占比里, "回退子样本"对整体估计的权重可能不可忽略, 若需要区分"真同句语境下的象征性响应"与"回退全文语境下的象征性响应", 应结合 stage 14 物化的 ss_is_fallback 标记做子样本分层, 而非直接使用本列的合并占比。三重设定 (P75 阈值梯子最严档 × _allv 全年份静态锚点 × ss 最窄文本窗口) 叠加令本列成为整个象限家族里判据最保守、样本噪声也相对更大的一支, 更适合作为对主设定的下界/严格性稳健性检验, 而非独立解读绝对水平。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Kwon, O., Yoon, J., & Yotov, Y. V. (2025). A generalized Poisson-pseudo maximum likelihood estimator. Journal of Business & Economic Statistics, 44(2), 560-573. https://doi.org/10.1080/07350015.2025.2544190
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
<!-- rendered-citations:end -->
