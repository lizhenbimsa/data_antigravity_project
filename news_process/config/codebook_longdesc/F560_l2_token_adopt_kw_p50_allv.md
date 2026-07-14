---
family_id: F560
columns:
- token_adopt_kw_p50_allv
- token_adopt_kw_p50_allv_ctx
- token_adopt_kw_p50_allv_ss
unit: 银行-年占比 (0–1 区间, 已测量篇数为分母的逐篇二值指示均值)
formula: 'token_adopt_kw_p50_allv{trk} = mean_i(1{freq_kw_i≥Q50_year(freq_kw)} ∧ {sim_allv_i<Q50_year(sim_allv)}), 逐篇分类仅在 sim/freq 双双非缺失 (measured) 的行上定义, 年度分位阈值按年份分组 quantile(0.5) 计算, 银行-年聚合取 mean 自动跳过未测量行'
producer: pipeline\panel\runner.py (`_classify_policy_quadrants` 逐篇分类 + 四象限占比聚合循环, L1978-L2104) ; pipeline\panel\export.py (面板列标签登记, L1394-L1403)
upstream:
- 16_article_policy_alignment.parquet (`policy_cosine_sim_allv`/`policy_cosine_sim_allv_ctx`/`policy_cosine_sim_allv_ss`; stage 15/16 产)
- 12_news_fintech.parquet (`fintech_distinct_keywords`; AC 自动机去重命中金融科技关键词数)
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
- doi: 10.1080/09296171003643098
  type: journal
  authors: Covington, M. A., & McFall, J. D.
  year: 2010
  title: "Cutting the Gordian knot: The moving-average type-token ratio (MATTR)"
  venue: Journal of Quantitative Linguistics
  vol: '17'
  issue: '2'
  pages_or_artno: 94-100
- doi: 10.1016/j.rmal.2024.100168
  type: journal
  authors: Bestgen, Y.
  year: 2025
  title: "Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons"
  venue: Research Methods in Applied Linguistics
  vol: '4'
  issue: '1'
  pages_or_artno: '100168'
new_dois: []
---

## CORE

【构念与来源】
本家族 (F560) 属于 stage 16 政策对齐四象限体系的一支, 度量银行-年层面"表面化 (token) 金融科技采纳"的占比。构念直觉来自监管/文本挖掘文献中一个常见现象: 企业或银行可能在新闻话语里大量堆砌金融科技相关热词 (借"金融科技""数字化转型"等标签蹭概念热度), 却在与官方产业政策的语义对齐程度上表现平庸——即"言而不实、话语先于行动"。四象限构造把每篇报道按两条正交轴切分: 一条是关键词密度轴 (本家族 `kw` 轨, 用 `fintech_distinct_keywords`, 即 Aho-Corasick 自动机对该篇报道命中的去重金融科技关键词数), 另一条是政策语义对齐轴 (`policy_cosine_sim_allv` 系列, 即该篇报道文本 embedding 与官方产业政策文本 embedding 的余弦相似度, 见 F550 前置家族)。`token_adopt` = 高词频 (≥年度中位数) 且低政策相似度 (<年度中位数) 的两分类交集占比, 与之对偶的还有 `hidden_adopt`(低词频高相似度, "低调但语义贴合政策") 与 `subst_adopt`(高词频高相似度, "既高频提及又语义贴合政策"的"实质性采纳")。三者均为逐篇二值指示在银行-年内的均值, 天然落在 [0,1] 区间, 可解读为"该银行该年被归为该象限的报道占比"。本家族命名中的 "token" 借用了语料语言学 type-token 区分的隐喻: token 指语言表层的具体出现次数 (surface repetition), 与承载深层语义多样性的 type 相对 (Covington & McFall, 2010; Bestgen, 2025 对 MATTR 型-例比方法的评述即讨论了这一表层重复 vs 语义多样性的张力)。本处借该隐喻表达"高频出现金融科技字面词汇, 但语义上未真正贴合政策方向"的采纳形态, 呼应 Kwan et al. (2024, JFQA) 用文本方法度量银行数字能力时区分"话语层面提及"与"实质能力信号"的做法, 也呼应 Fan, Liu, Qian & Wen (2024) 在技术采纳测度中强调采纳广度 (词频/覆盖) 需与采纳深度 (与政策/技术标准的匹配程度) 分开刻画的思路。

【方法学与计算】
计算分两步。第一步逐篇分类 (`_classify_policy_quadrants`): 对给定相似度列 `sim_col` 与频次列 `freq_col`, 按 `year` 分组各自求年度 P50 分位阈值 (`groupby('year').transform(quantile)`), 得到当年的高低切分线; `measured = sim_col.notna() & freq_col.notna()`, 仅对该双非缺失掩码内的行输出 0/1 浮点指示, 掩码外行显式置 NaN (而非静默归为低词频/低相似度的假阴性)——这是 2026-06-11 的一次修复 (旧实现把测量失败误判为"低对齐低词频", 会在 stage 15 优雅早退产出全 NaN 相似度时把全部高词频文章错误地整体归入 Token 象限, 是本项目 F3 铁律"无测量=NaN, 禁伪零"的一次典型违反后修复案例)。第二步银行-年聚合: `groupby(['target_bank','year']).agg(mean)` 对逐篇指示取均值, pandas `mean` 默认跳过 NaN, 故分母天然是"该银行该年已测量 (sim 与 freq 均非缺失) 的报道篇数", 而非该行原始报道总篇数; 若某银行某年全部报道都未测量, 聚合结果本身为 NaN 而非 0, 与面板整体"无数据=未测量"的缺失语义契约保持一致 (Allison, 2001 §3 讨论的强制填零对固定效应估计的偏误动机, 是该契约在项目内反复引用的方法论依据)。

【文献定位】
四象限政策对齐构造的相似度轴方法学根基是 Hassan et al. (2019) 式的文本-政策语义相似度测量传统 (见前置家族 F550/F551 codebook), 本家族只消费其产出而不重复计算; 本家族独有的贡献是把"提及广度"(kw 词频轴) 与"语义对齐深度"(sim 轴) 交叉分类为离散象限, 这一"广度 vs 深度"分离测度的做法可类比 Kwan et al. (2024, JFQA) 用文本方法压力测试银行数字能力时对"披露/提及"与"能力信号"的区分, 以及 Fan et al. (2024) 在技术采纳研究里对采纳广度和采纳质量分别建模的处理。

`allv` (all-vintage) 锚点后缀标记本家族相似度轴使用的是"全语料静态政策锚点" (`policy_cosine_sim_allv`) 而非按发文年份滚动更新的"vintage 主轨"锚点 (无 `_allv` 后缀的同构家族), 两者是互为稳健性、不分主次的并排口径, 分别捕捉"相对当年政策文本的对齐度"与"相对全样本期政策文本静态基准的对齐度", 二者共用完全相同的 track(full/ctx/ss)×词频(kw/int)×分位(P25/P50/P75) 四象限构造逻辑, 禁止在同一个 over-identified Hansen J 检验中混用 vintage 主轨与 allv 锚点的对齐占比列 (与三轨/co-primary 嵌入铁律同构)。词频侧后缀 (`_ctx`/`_ss`) 只随文本轨道变化、与锚点选择无关, 因为 `fintech_distinct_keywords` 是 track-agnostic 元数据 (AC 自动机去重关键词计数不区分正文截取窗口), kw 轨在 `_ctx`/`_ss` 下会复用 full 轨词频列而只切换相似度列。

## VAR: token_adopt_kw_p50_allv

【变体差分】
本列是家族 canonical 无轨道后缀变体, 相似度轴取 `policy_cosine_sim_allv` (全语料静态政策锚点, 无 `_ctx`/`_ss`), 频次轴取 `fintech_distinct_keywords` 的 full 文本轨扫描结果 (kw 轨, 即标题+正文全文范围内的 AC 去重金融科技关键词计数), 分位阈值取年度 P50 (中位数切分, 与同族 `_p25`/`_p75` 分位家族互为敏感性梯子, 三者同样各自 just-identified 并排、不分主次)。取值域为该银行该年被同时判定为"高词频且低政策相似度"的报道占比, 分母为该银行该年 sim/freq 双双非缺失的已测量报道篇数; 若该银行该年无任何已测量报道, 本列输出 NaN 而非 0。

本列作为 full 轨基准, 是三轨姊妹变体 (`_ctx`/`_ss`) 共同比对的参照系: 它使用未经实体窗口或同句窗口裁剪的完整报道正文 (标题+全文), 覆盖面最广、样本损耗最少, 因而在报道稀疏的银行-年组合上分位阈值估计相对更稳定; 代价是文本中与目标银行、金融科技均无直接关联的段落 (背景介绍、无关业务叙述等) 会一并进入 embedding 表征, 对政策语义相似度产生稀释效应, 使 `token_adopt` 相比 ctx/ss 轨可能更容易把"泛泛提及金融科技但报道主体并非该银行金融科技业务"的文章误判入高词频低相似度象限。P50 分位与 P25/P75 分位家族相比切分更居中、样本量在四象限间分布更均衡, 是三档分位梯子中的默认参照点, 但不代表比 P25/P75 更"正确", 三者仅是构造判据敏感性检验的并排臂。

## VAR: token_adopt_kw_p50_allv_ctx

【变体差分】
本列是 full 轨的语境窗口 (ctx) 姊妹变体: 相似度轴改用 `policy_cosine_sim_allv_ctx` (标题+目标银行∧金融科技实体窗口截取文本的政策相似度, 全语料静态锚点), 分位阈值仍按年度独立重算 P50 (ctx 轨与 full 轨的年度中位数一般不同, 因为参与分位计算的相似度分布本身随文本截取窗口变化)。kw 轨频次侧: 因 `fintech_distinct_keywords` 为 track-agnostic 元数据 (无 `_ctx` 同轨变体产出), 本列复用 full 轨词频列 `fintech_distinct_keywords`, 仅相似度轴切换为 ctx。ctx 与 full 是互为稳健性、不分主次的并排轨道, 两者各自 just-identified, 禁止混入同一 over-identified Hansen J; ctx 轨捕捉"聚焦实体窗口的局部语义对齐", 相比 full 轨受报道中无关段落 (与银行/金融科技均无关的背景叙述) 稀释效应的影响更小, 但样本量/文本长度也相应更短, 在稀疏报道年份可能带来更大的分位阈值抖动。

需要特别注意的是, 本列的"高词频"判据仍沿用 full 轨的关键词计数, 因此高低词频的切分标准与相似度轴的窗口口径并不完全对称——即便相似度已切换到 ctx 局部窗口, 频次仍是基于全文统计的结果。这意味着 ctx 轨的 `token_adopt` 与 full 轨 `token_adopt` 之间的差异, 严格来说完全来自相似度轴口径切换 (而非频次口径), 便于把"局部语义对齐是否改变象限归属"这一效应单独分离出来考察, 是本项目一贯的"逐维度单点替换"稳健性设计惯例 (与三轨情感/co-primary 嵌入的单变量替换逻辑一致)。当 `policy_cosine_sim_allv_ctx` 上游列缺失 (旧 schema 或该轨未启用) 时, runner 会记录警告并整体跳过 ctx 轨孪生, 此时本列在面板中不产出, 而非以 NaN 占位填充全部行。

## VAR: token_adopt_kw_p50_allv_ss

【变体差分】
本列是 full 轨的同句共现窗口 (ss) 姊妹变体: 相似度轴改用 `policy_cosine_sim_allv_ss` (标题+目标银行与金融科技词同句 ±N 窗口截取文本的政策相似度, 全语料静态锚点), 年度 P50 阈值同样独立重算。频次轴同 ctx 轨规则, 因 kw 词频列本身 track-agnostic 而复用 full 轨 `fintech_distinct_keywords`。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行∧金融科技词的同句共现时, 其 `content_ss` 回退为全文 body (`ss_is_fallback=True`), 对应的 `policy_cosine_sim_allv_ss` 在此类回退行上退化为与 full 轨口径更接近的相似度估计, 而非因窗口缺失产生额外缺失; 若上游 `policy_cosine_sim_allv_ss` 列本身不存在 (旧 schema / ss 未上线), runner 会优雅跳过该轨孪生而不产出本列, 面板中相应表现为该列整体缺失。ss 轨与 full/ctx 同样是并排稳健性口径, 三轨互不隶属、禁止混入同一识别方程; ss 轨相比 ctx 轨窗口更窄 (严格同句而非实体窗口), 对政策语义对齐的度量更聚焦但对句子切分/共现判定 (`entity_context.py::extract_bank_fintech_cooccurrence` 判据) 的噪声更敏感, 尤其在长句或标点不规范的原始报道文本中, 句子边界切分误差可能让本应视为同句共现的表述被误判为不共现, 从而推高该篇的 fallback 比例。

与 ctx 轨相同, 本列的词频轴仍复用 full 轨 `fintech_distinct_keywords` 而非任何同句范围内的关键词计数, 因此 ss 轨 `token_adopt` 与 full 轨的差异同样纯粹来自相似度轴 (`policy_cosine_sim_allv_ss`) 的窗口切换。由于 ss 窗口比 ctx 更窄, 落入回退 (fallback) 分支的报道比例通常更高, 这些回退行的相似度估计会向 full 轨口径靠拢, 使得 ss 轨与 full 轨在高回退比例的银行-年组合上呈现更强的相关性, 这是解读三轨差异时需要纳入考量的机械性特征, 而非语义上的真实趋同。上游 `policy_cosine_sim_allv_ss` 缺失时的处理方式与 ctx 轨一致: runner 整体跳过该轨孪生, 本列不产出。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
Covington, M. A., & McFall, J. D. (2010). Cutting the Gordian knot: The moving-average type-token ratio (MATTR). Journal of Quantitative Linguistics, 17(2), 94-100. https://doi.org/10.1080/09296171003643098
Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. Research Methods in Applied Linguistics, 4(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168
<!-- rendered-citations:end -->
