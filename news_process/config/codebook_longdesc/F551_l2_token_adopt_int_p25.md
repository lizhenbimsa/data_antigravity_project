---
family_id: F551
columns:
- token_adopt_int_p25
- token_adopt_int_p25_ctx
- token_adopt_int_p25_ss
unit: bank-year 层面连续占比 [0,1] (文章级二值指示 groupby(['target_bank','year']).mean() 聚合结果, 非逐行 0/1 标量)
formula: '文章级: I(fintech_intensity_score_{trk} >= P25_year(fintech_intensity_score_{trk})) AND I(policy_cosine_sim_{trk} < P25_year(policy_cosine_sim_{trk})), 阈值按 groupby(year) 逐年分位数估计 (非样本内整体分位); bank-year 层面: token_adopt_int_p25{trk} = mean(该二值指示, over articles in (target_bank, year))'
producer: pipeline\panel\runner.py
upstream:
- pipeline/filtering/policy_alignment.py
- pipeline/filtering/fintech_intensity.py
- pipeline/panel/export.py
citations:
- doi: '10.1016/j.econmod.2023.106445'
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: 'Bank Fintech, Liquidity Creation, and Risk-Taking: Evidence from China'
  venue: Economic Modelling
  vol: '127'
  pages_or_artno: '106445'
- doi: '10.1016/j.iref.2021.03.009'
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does Fintech Innovation Improve Bank Efficiency? Evidence from China's Banking Industry"
  venue: International Review of Economics & Finance
  vol: '74'
  pages_or_artno: 468-483
- doi: '10.1006/jfin.2000.0282'
  type: journal
  authors: Boot, A. W. A.
  year: 2000
  title: 'Relationship Banking: What Do We Know?'
  venue: Journal of Financial Intermediation
  vol: '9'
  issue: '1'
  pages_or_artno: 7-25
- doi: '10.1002/smj.821'
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: 'Value Creation in Innovation Ecosystems: How the Structure of Technological Interdependence Affects Firm Performance in New Technology Generations'
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306-333
- doi: '10.1007/s11573-017-0852-x'
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital Finance and FinTech: Current Research and Future Research Directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: '10.1002/isaf.1549'
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: 'Text-Based Sentiment Analysis in Finance: Synthesising the Existing Literature and Exploring Future Directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: "10.1111/1467-8551.12879"
  title: "FinTech Adoption and Corporate Greenwashing: A Technology Affordance Perspective"
  authors: "Sun, Z., Liu, L., Johan, S., & Zhao, L."
  year: 2025
  venue: "British Journal of Management"
  type: "journal"
- doi: "10.1016/j.iref.2024.05.023"
  title: "Substantive digital innovation or symbolic digital innovation: Which type of digital innovation is more conducive to corporate ESG performance?"
  authors: "Wang, Z., & Tang, P."
  year: 2024
  venue: "International Review of Economics & Finance"
  type: "journal"
new_dois:
  - "10.1111/1467-8551.12879"
  - "10.1016/j.iref.2024.05.023"
---

## CORE

【构念与来源】
token_adopt_int_p25 家族属于文章级政策对齐 (Article-level Policy Alignment, stage 15/16) 派生的四象限离散分类体系中的「Token / 空谈型」象限, 与并列的 hidden_adopt (隐性型) / subst_adopt (实质型) 三族共同覆盖同一交叉表, 但本家族并非本家族成员的 hidden/subst 两族不在本文档内展开。四象限的构造逻辑由 `pipeline/panel/runner.py::_classify_policy_quadrants` 定义: 纵轴是词频/强度 (银行金科话语的技术细节丰富程度), 横轴是政策相似度 (该行金科话语与监管/政策导向语料的余弦对齐程度), 两轴各自按年度分位数二值化后交叉, 得到「言」(话语强度) 与「行」(政策方向贴合度) 两个正交维度上的四种组合。Token 象限对应「词频高但政策相似度低」这一格: 文章在金科相关词汇/语义强度上表现活跃 (纳入当年强度前 75% 高区间), 但其话语内容与政策/监管导向语料的余弦相似度却排在当年后 25% 低区间——即报道「说得多」但「说得不对题」, 话语热度未能与政策方向对齐。生产代码内嵌白话注释将该象限称为「洗科技」, 呼应企业传播文献中「唱高调却无的放矢」的空谈型信号: 银行金科报道大量堆砌关键词、渲染技术强度以制造「积极拥抱金融科技」的观感, 却未在话语层面真正对齐监管所引导的方向 (如普惠金融、风险防控、合规科技等政策议题), 更接近符号性的自我宣传而非与政策议程呼应的实质表达。这一构念定位与 Adner & Kapoor (2010) 关于创新生态系统中「技术互依结构如何影响企业绩效」的分析框架相呼应: 该文强调单纯拥有或宣称拥有某项技术能力 (component competence) 不等于该能力被有效整合进与生态位互补方 (此处可类比为政策/监管导向) 相协调的价值创造路径中, 技术强度与生态协同方向是两个需要分别度量的正交维度, 只在两者同时高企时才构成真正的「整合式」技术采纳——这正是本象限体系区分 Token (强度高、协同低) 与 Substantive (强度高、协同高) 的方法论依据。
【方法学与计算】
token_adopt_int_p25 在盘上真实的构造分两层。第一层是文章级二值化——由两个连续型上游测度在每篇文章 (而非 bank-year 聚合均值) 上分别二值化后组合, 其一是 fintech_intensity_score (及其 _ctx/_ss 同名轨道变体), 产出于 stage 15 fintech_intensity (TF-IDF × SIF 加权的金科语义强度得分, 区别于同一象限体系内基于关键词计数的 Track A "kw" 轨); 其二是 policy_cosine_sim (及其 _ctx/_ss 同名轨道变体), 即文章文本与政策/监管语料的余弦相似度, 产出于 stage 16 article_policy_alignment (co-primary Qwen 嵌入主轨, 无后缀)。二值化阈值按年份分组 (`groupby('year')`) 分别对当年样本内的 fintech_intensity_score 与 policy_cosine_sim 逐年估计第 25 百分位切点 (而非对聚合后的 fintech_intensity_mean/article_sim_mean 计算样本内整体分位数), `_classify_policy_quadrants` 内部统一记 `high_freq = freq >= yfreq_p25`、`high_sim = sim >= ysim_p25`, Token 象限的文章级指示定义为 `high_freq & ~high_sim` (词频高且相似度不高, 即相似度低于当年 P25 切点), 记 1; 否则记 0。sim 或 freq 任一测量缺失 (NaN) 的文章不参与分类, 指示值记 NaN (`.where(measured)`), 分母因此是"已测量篇数"而非全部篇数——这是 fix(omni-g-runner-03/g-runner-11, 2026-06-11) 修正的历史缺陷: 旧实现把 `NaN >= thresh` 静默判为 False, 会在 stage 15 优雅早退产出全 NaN parquet 时把全部高词频文章误判为 Token, 制造由零测量伪造的面板值; 现行实现严格区分「未测量」(NaN) 与「测量后判为低相似度」(0), 两者在物理域分母层面不再混淆。第二层是 bank-year 聚合——盘上真正落入面板的 token_adopt_int_p25{_ctx,_ss} 列, 是把上述文章级 0/1/NaN 指示按 (target_bank, year) 做 `.mean()` 聚合 (pandas groupby mean 自动跳过 NaN) 得到的连续占比, 语义是「该行该年被测量文章中, 落入 Token 空谈象限的文章占比」, 取值范围 [0,1] 而非离散 {0,1}; 当该行该年全部文章均未测量时, 该占比列本身也是 NaN, 与 CLAUDE.md 「NaN 保持、listwise 处理」的项目通用口径一致, 不做 fillna(0) 处理。命名中的 "int" 标识该列属于「Track B (intensity 连续测度)」象限体系, 与并列的 "kw" (Track A, 基于关键词计数的离散测度) 形成方法学对照的两条独立象限化路径, 二者各自 just-identified, 互为稳健性、不分主次, 不可混入同一 over-identified 设定 (如同一 Hansen J 检验)。"p25" 标识文章级二值化所用的年度分位阈值为第 25 百分位, 是该象限体系三档阈值梯度 {P25, P50, P75} 中最宽松的一档; 项目口径上 P50 (中位数切分) 是与项目 10+ 处中位数分割惯例一致的机制检验基准档, P25/P75 是围绕该基准展开的阈值敏感性稳健性检验档——三档在计量设定上各自 just-identified 并排, 互为稳健性检验、禁止混入同一 over-identified 设定, 但在"何档作为正文机制检验的默认呈现"这一叙事选择上, 项目约定以 P50 为基准、P25/P75 供稳健性附表引用。
【文献定位】
Token 象限的构念定位可归入企业传播/信息披露文献中「话语热度与实质对齐脱节」的识别传统。Adner & Kapoor (2010, Strategic Management Journal) 建立的创新生态系统互依框架指出, 单一环节 (此处即"金科话语的技术强度") 的能力提升若未与互补方 (此处即"政策/监管导向") 的协同方向对齐, 并不必然转化为整合式的价值创造, 为本象限「强度高但对齐低」的构念划分提供了理论依据。Gomber, Koch & Siering (2017, Journal of Business Economics) 对数字金融/FinTech 研究现状与未来方向的系统梳理, 界定了「金融科技话语」作为可观测研究对象的边界与维度, 是本项目 locus 维度 (P4) 与本象限体系共享的构念溯源。经验层面, Fang, Wang, Wang & Zhao (2023, Economic Modelling) 考察中国银行金融科技投入与流动性创造、风险承担之间的关系, 其研究设计将金融科技投入的"强度"与投入所伴随的经营/监管取向分开处理, 为「强度」与「政策对齐」需分离度量的构念划分提供了经验层面的旁证; Lee, Li, Yu & Zhao (2021, International Review of Economics & Finance) 关于金融科技创新对中国银行业效率影响的研究同样在实证设计上区分了投入规模与转化效果两个环节, 提示单纯的话语/投入强度本身并非「实质采纳」的充分信号, 支持本象限体系不以单一强度指标而以强度×对齐交叉分类刻画"空谈"构念的设计选择。Boot (2000, Journal of Financial Intermediation) 对关系型银行业的经典综述强调, 银行的实质经营行为 (包括对监管/合规方向的响应) 往往嵌入在长期、稳定、未必高调的关系与流程中, 而非体现为高频次的对外话语宣示——这一洞见构成 Token (话语强度高) 与 Hidden (话语强度低但政策对齐高, 对应 Boot 所述"闷声干大事") 两象限区分的经济学旁证。方法论层面, Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 对金融文本情感分析文献的系统综述指出, 单一文本测度 (如整体情感极性或关键词计数) 难以捕捉披露内容的多维语义结构, 呼应本象限体系采用「强度」×「对齐」双测度交叉分类而非单一综合指数的设计选择。该文从技术可供性视角考察金融科技采纳与企业漂绿行为的关系, 为「技术话语高但实质对齐低」的空谈型构念提供直接的金融科技情境经验支持, 引用格式为 Sun, Liu, Johan, & Zhao (2025, British Journal of Management)。该文区分实质性与象征性数字创新对企业ESG绩效的差异化影响, 证实象征性创新无法有效抑制漂绿, 支持本象限体系以「强度×对齐」交叉分类而非单一强度指标刻画空谈构念的设计, 引用格式为 Wang & Tang (2024, International Review of Economics & Finance)。

## VAR: token_adopt_int_p25

【变体差分】
token_adopt_int_p25 是家族的 canonical (full 轨) 版本, 上游 fintech_intensity_mean 与 article_sim_mean 均取自全文文本 (标题+正文原始内容) 扫描结果, 未做实体窗口或同句共现限定。该列是三轨体系 (full/ctx/ss) 中信息覆盖面最广、噪声也最高的一档: 全文扫描会把与目标银行、金科话语不直接相关的段落一并纳入强度与相似度计算, 因此其 Token 占比更接近「整篇报道话语热度与政策对齐脱节程度」的总体基调, 而非「围绕目标银行-金科交集的精确刻画」。在留篇门控 (full-only, 2026-06-29 起生效) 体系下, 一篇文章是否被判定为「银行金科报道」的门控判据只看 llm_verified_full, 因此本 full 轨列所依赖的 n_articles 分母与留篇集合口径完全对齐主门控, 是该象限体系中样本覆盖最完整的一条轨道。full/ctx/ss 三轨在本族中各自独立计算象限阈值 (P25 分位数逐轨重新估计, 不共享切点), 三者互为稳健性并排, 不设主轨优先级, 严禁在同一 over-identified 设定 (如同一 Hansen J 检验) 中混用来自不同轨道的该家族列作为过度识别工具变量。就经济含义而言, 盘上的 token_adopt_int_p25 是 bank-year 层面的连续占比而非逐行 0/1 标量: 其数值 = 该行该年被测量文章中「词频高于当年 P25 分位且政策相似度低于当年 P25 分位」的文章占比, 取值范围 [0,1]。使用者在解读该列时应注意, 底层二值化切点是逐年估计的相对阈值 (`groupby('year')` 分位数), 而非固定绝对水平或跨全样本估计的分位数, 因此不同年份的切点数值不同、该占比列的跨年比较隐含"各年内部相对位置"而非"绝对强度水平"的语义, 也不宜跨样本版本 (如加入新年份数据后重估分位数) 直接比较。该列与并列的 subst_adopt_int_p25 (强度高且对齐也高)、hidden_adopt_int_p25 (强度低但对齐高) 构成同一四象限交叉表中的三个互斥类别 (第四类"低强度低对齐"不设专属列), 三者理论上应满足行内加总不超过 1 (剩余份额归入未列名的"不相关"象限), 研究者在做机制解释时应联合参照三族而非孤立解读单一象限占比。

## VAR: token_adopt_int_p25_ctx

【变体差分】
token_adopt_int_p25_ctx 是三轨体系中的 ctx (context) 轨变体, 其文章级上游 fintech_intensity_score_ctx 与 policy_cosine_sim_ctx (存在同轨变体时优先使用, 否则回退复用 track-agnostic 的 full 列并在日志中披露) 的语义窗口收窄为「标题 + 目标银行实体窗口」文本 (content_ctx, 由 stage 14 ctx_materializer 物化, prepend_title 拼接), 而非全文。相较于 full 轨, ctx 轨的强度与相似度测度更聚焦于目标银行被提及的局部语境, 能过滤掉报道中与该行金科业务无直接关联的背景段落, 理论上应能更精确地捕捉「该行本身」话语热度与政策对齐脱节的信号, 而非整篇报道混杂的话题噪声。ctx 轨的文章级二值化同样按年份分组独立重估 P25 分位阈值 (不复用 full 轨切点), 二值化后再按 (target_bank, year) 聚合为占比, 与 full/ss 轨互为稳健性并排、不分主次。需要注意的是, 留篇门控 (2026-06-29) 下 ctx 轨已降为 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 轨留篇集合的子集, 即只有已通过 full-only 门控判为「一篇银行金科报道」的文章才会在 ctx 轨上计算并参与该列的分位阈值估计与二值化, ctx 轨本身不独立扩展或收缩样本宇宙。方法学上, ctx 轨与 full 轨的差异纯粹来自输入文本窗口的收窄, 二值化逻辑本身 (词频高且相似度低于同轨 P25 分位) 与 full 轨完全一致, 因此该列的价值不在于引入新的判定规则, 而在于用更聚焦的语境窗口检验 full 轨的 Token 判定是否对「报道中与目标银行无关的背景话题噪声」敏感; 若两轨判定高度一致, 说明 full 轨结果具有语境稳健性; 若出现系统性分歧, 则提示 full 轨可能受到报道中非目标银行段落的稀释影响 (例如整篇报道谈及多家银行, 仅其一是"洗科技", 但全文扫描把其他银行的实质表述也计入了强度测度), 此时 ctx 轨提供了更贴近银行本身的替代读数, 供研究者在稳健性表中并列汇报。

## VAR: token_adopt_int_p25_ss

【变体差分】
token_adopt_int_p25_ss 是三轨体系中的 ss (same-sentence) 轨变体, 其文章级上游 fintech_intensity_score_ss 与 policy_cosine_sim_ss 测度基于「标题 + 目标银行与金科词同句 (±N 句窗口, 默认 N=1, 见 config/filtering.yaml::context_window.ss_sentence_radius) 共现」的最严格语境窗口 (content_ss) 计算, 是三轨中语义窗口最窄、判据最严格的一档, 理论上能最大限度剔除「同篇报道提及但与银行金科交集无关」的话语噪声, 使强度与政策相似度的测度更贴近「该行金科话语是否具体且是否对齐监管方向」的严格情境。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则 content_ss 退化为全文 body (与 full 轨相同文本), 并以 ss_is_fallback=True 标记该行为降级样本, 与 ctx_is_fallback 共享 n_articles 分母口径, 不因回退而制造单边孤儿行。与 ctx 轨一致, ss 轨在留篇门控下同为 conditional-on-full 的稳健性轨, 行宇宙是 full 轨留篇集合的子集; ss 轨的文章级二值化同样按年份分组独立重估 P25 分位阈值, 与 full/ctx 轨各自 just-identified 并排, 互为稳健性检验、不分主次, 严禁三轨混入同一 over-identified Hansen J 设定。由于 ss 轨判据比 ctx 轨更严格 (同句 vs. 实体窗口), 其非回退样本 (ss_is_fallback=False) 的强度与相似度测度理论上信噪比最高, 是三轨中对「Token 空谈」构念最精确但样本覆盖也最窄的一档; 当某银行金科话语在报道中零散分布、未与目标银行出现在同一句中时, ss 轨会大量触发回退, 此时其信息量退化为等同 full 轨, 研究者在解读 ss 轨结果时应结合 ss_is_fallback 占比评估该轨判定的实际精度增量, 避免在回退比例过高的子样本中过度依赖 ss 轨作为主要证据。

<!-- rendered-citations:begin -->
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank Fintech, Liquidity Creation, and Risk-Taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does Fintech Innovation Improve Bank Efficiency? Evidence from China's Banking Industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Boot, A. W. A. (2000). Relationship Banking: What Do We Know? Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Adner, R., & Kapoor, R. (2010). Value Creation in Innovation Ecosystems: How the Structure of Technological Interdependence Affects Firm Performance in New Technology Generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital Finance and FinTech: Current Research and Future Research Directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-Based Sentiment Analysis in Finance: Synthesising the Existing Literature and Exploring Future Directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Sun, Z., Liu, L., Johan, S., & Zhao, L. (2025). FinTech Adoption and Corporate Greenwashing: A Technology Affordance Perspective. British Journal of Management. https://doi.org/10.1111/1467-8551.12879
Wang, Z., & Tang, P. (2024). Substantive digital innovation or symbolic digital innovation: Which type of digital innovation is more conducive to corporate ESG performance? International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.05.023
<!-- rendered-citations:end -->
