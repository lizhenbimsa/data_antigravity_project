---
family_id: F476
columns:
- pos_hc_substvalid_count_ctx
- pos_hc_substvalid_count_full
- pos_hc_substvalid_count_ss
unit: 篇数/计数 (count)
formula: 'pos_hc_substvalid_count{track} = Σ_{i∈bank-year} 1[ pos_count{track}_i=1 ∧ llm_agreement_rate{track}_i ≥ (2/3 − 1e-9) ∧ innovation_substantiveness{track}_i ∈ {实质性, 象征性} ]; 逐篇指示列 `_svd_pos_hc{track}` (runner.py 步骤 7h 洗稿率前置区块生成) 由 runner.py 步骤 5 内部函数 `_pool_svd_substvalid_counts` 逐篇求和聚合到银行-年, 再 merge 回 panel'
producer: pipeline\panel\runner.py (前置指示列 `_svd_pos_hc{track}` 生成于步骤 7h 洗稿率区块; 聚合函数 `_pool_svd_substvalid_counts` 定义并调用于步骤 5 内部, 自聚合不经 encode.py::build_aggregation_dict)
upstream:
- 24_herd_decay.parquet (df_exploded, stage 21 语义精筛后 article×bank 级 verified 集)
- llm_vote_tone{track} / is_positive{track} (LLM 多数票情感共识)
- llm_agreement_rate{track} (LLM 三家投票一致度)
- innovation_substantiveness{track} (LLM 实质性/象征性二分类判定)
citations:
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: Count (and count-like) data in finance
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 529-551
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as Data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
new_dois: []
---

## CORE

【构念与来源】
`pos_hc_substvalid_count` 家族是洗稿率 (washing ratio) 多方法族群中「方法 F: 高置信度子样本」测度的同域 (same-domain) 分母计数。washing ratio 整体度量一家银行在某年被媒体报道中「正面情感声明的象征性 (symbolic) 占比」——即声明是否伴随可验证的实质性 (substantive) 内容, 抑或仅是无实质支撑的正面措辞。该构念直接对应 Bingler, Kraus, Leippold & Webersinke (2024, *Journal of Banking & Finance*) 提出的 cheap talk / cherry-picking 框架: 企业 (在本项目语境中为银行金融科技相关报道) 可能通过高频释放正面但空洞的表态来管理外部感知, 而不必然伴随可验证的创新实质。方法 F 在此基础上叠加「高置信度」限定: 只保留三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 情感判定一致度 `llm_agreement_rate{track}` ≥ 2/3 (代码常量 `HC_AGREEMENT_THRESHOLD = 2/3 − 1e-9`, 浮点容差确保唯一多数票档 2/3 = 0.6667 精确纳入而非被浮点比较误判排除) 的文章子样本, 呼应 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 对基于机器学习/多标注者构造高置信度子样本以控制标注噪声的一般性方法论主张: 当多个独立标注来源 (本项目为三家 LLM) 高度一致时, 该子样本的情感/实质性标签测量误差被认为显著低于全样本, 从而为洗稿率估计提供一条对标注噪声更稳健的替代口径。

`pos_hc_substvalid_count` 本身不是「高置信度正面文章数」(那是 `pos_hc_count`), 而是其同域分母: 在 `pos_hc_count` 的基础上, 进一步要求该文章的实质性判定 `innovation_substantiveness{track}` 落在有效标签集合 (「实质性」或「象征性」二选一, 而非因 LLM 分类失败/未测量而缺失) 之内。这一「同域化」(same-domain denominator) 设计源自项目内部修复 fix(omni-g-runner-10/14, 2026-06-11): 洗稿率的分子 `pos_symb_hc_count` (高置信度且被判为「象征性」的正面文章数) 隐式要求该文章已被成功分类为「象征性」或「实质性」二者之一 (未成功分类的文章 NaN → 转字符串后恒为 False, 不会被计入象征性), 但历史实现的分母却仍沿用未过滤实质性缺失的物理计数 `pos_hc_count`。当 LLM 实质性分类失败率随时间/样本波动时, 这一分子分母域不对齐会使洗稿率产生系统性向下偏误 (分子的有效测量样本更小, 分母未同步收缩)。`pos_hc_substvalid_count` 正是修复后的分母: 与分子共享同一「实质性判定已成功测量」的样本域, 使 `washing_ratio_hc{track} = pos_symb_hc_count{track} / pos_hc_substvalid_count{track}` 成为条件比例 (conditional proportion), 而非被未测量样本稀释的比率。

【方法学与计算】
计算全程发生在 `pipeline/panel/runner.py` 单文件内部, 分两步串联但不经过 `pipeline/panel/encode.py::build_aggregation_dict` (该聚合注册字典是面板主聚合的通用入口, 但本家族刻意绕开它, 在 runner 内部自聚合): 第一步, 逐篇指示列在洗稿率前置区块 (步骤 7h 上游, 变量名 `_svd_pos_hc{track}`) 生成, 布尔逻辑为「该篇 `pos_count{track}` (LLM 多数票判正) 等于 1」且「`llm_agreement_rate{track}` ≥ 2/3 − 1e-9 (高置信度)」且「`_subst_measured` (即 `innovation_substantiveness{track}` 落在 `{实质性, 象征性}` 有效标签集合, 由 `_tt.isin(_SUBST_VALID_LABELS)` 判定, 缺失/未测量则为 False)」三者的合取。第二步, 步骤 5 (`aggregate_panel` 主聚合完成之后) 内部另调用一个专用辅助函数 `_pool_svd_substvalid_counts`, 对逐篇 `_svd_*` 指示列 (含 `_svd_pos_hc{track}`) 做银行-年 groupby-sum, 产出 `{name}_substvalid_count{track}` 系列列后经 `panel.merge(_svd_panel, on=['target_bank', 'year'], how='left')` 并回主面板, 得到本家族三列。该函数的源码注释明确写明此聚合「属 g-encode 组文件, runner 内自聚合」——即刻意与 encode.py 的通用聚合注册路径分离, 单独处理这一批同域分母计数。聚合完成后, 该计数在 `runner.py` 步骤 7h 内被 `_svd_denom()` 辅助函数消费——若面板中存在 `pos_hc_substvalid_count{track}` 列, 则 `washing_ratio_hc{track}` 的分母取该列; 若因旧 schema 缺失, 才优雅回退为未同域化的物理计数 `pos_hc_count{track}` 并写入 WARNING 日志 (保底行为, 非当前生产口径)。`_safe_ratio()` 对分母 ≤ 0 的银行-年格返回 NaN (使用 `np.divide` + `where` 掩码, 避免除零 RuntimeWarning), 因此当某银行-年在高置信度子样本下无一篇实质性判定成功的正面文章时, `washing_ratio_hc{track}` 该格为缺失而非人为 0。

`_full`/`_ctx`/`_ss` 三轨复用统一的三轨文本架构 (CLAUDE.md「三轨文本架构」): full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句 ±N 窗口 (回退语义镜像 ctx: 无同句共现时 `content_ss` 退化为全文 body 且 `ss_is_fallback=True`)。三轨各自独立跑三家 LLM 情感投票与实质性分类, 因此 `llm_agreement_rate{track}`、`innovation_substantiveness{track}`、`pos_count{track}` 均为逐轨独立测量, 本家族三列亦逐轨独立计数, 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否被计入「银行金科报道」样本只看 `llm_verified_full == True`, ctx/ss 轨的洗稿率测度是该留篇集合的条件子测度/稳健性轨 (行宇宙为 full 留篇集的子集, per-track 逐轨照算), 而非独立扩样。

【文献定位】
洗稿率整体框架的核心锚点是 Bingler, Kraus, Leippold & Webersinke (2024, *Journal of Banking & Finance*) 提出的 cheap talk 度量方法, 该文以气候信息披露为背景, 区分企业沟通中的空洞承诺与可验证行动, 与本项目将「银行对金融科技的正面表态」拆解为象征性/实质性两类的思路同构。高置信度子样本的方法论依据参考 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 对文本即数据 (text as data) 研究范式的系统综述——该文强调基于机器学习/多标注来源的文本分类天然伴随可量化的置信度/一致性信号, 显式利用该信号构造更可靠的子样本 (多标注器一致时保留、分歧时视为噪声较高的边界样本) 是文本计量测度控制标注误差的常见策略, 本家族三家 LLM 投票一致度阈值即是该策略在洗稿率测度上的具体落地。Loughran & McDonald (2011, *The Journal of Finance*) 关于词典/文本分类在金融披露语境下容易产生系统性误判的经典发现, 为本家族「同域化分母」这一修正逻辑提供了背景动机: 未与分子共享测量成功域的粗糙分母, 会人为压低或抬高比率类文本测度的可靠性, 这与 Cohn, Liu & Wardlaw (2022, *Journal of Financial Economics*) 关于计数类金融数据构造需谨慎处理分母定义的方法论提醒相呼应。综合而言, 将「实质性判定已成功测量」显式纳入分母定义 (而非简单假定分类结果零噪声), 是文本计量测度构造中的稳健实践, 本家族「高置信度且实质性判定成功」的双重限定正是这一实践的具体落地。

## VAR: pos_hc_substvalid_count_ctx

【变体差分】
本列取 track=`_ctx` (标题+银行/金科实体窗口文本), 是该家族在 ctx 轨的实现: 逐篇合取条件「`pos_count_ctx`=1」∧「`llm_agreement_rate_ctx` ≥ 2/3 − 1e-9」∧「`innovation_substantiveness_ctx` 已成功测量」, 三个上游变量均在 ctx 文本轨上独立由三家 LLM 重新投票/分类得出, 与 `_full`/`_ss` 轨互不借用彼此的情感或实质性判定结果。作为条件-on-full 稳健性轨 (行宇宙 = full 留篇集子集), 其分母语义与 `_full` 轨完全一致 (同域化, 高置信度阈值相同), 唯一差异是喂入 LLM 的文本窗口范围更窄 (聚焦实体邻近上下文而非全文), 因而可能因上下文信息不足而改变个别边界文章的实质性/情感判定, 进而改变高置信度子样本的规模。该列与 `pos_hc_substvalid_count_full`/`pos_hc_substvalid_count_ss` 互为稳健性并排使用, 三者各自 just-identified, 不应混入同一过度识别 (over-identified) 检验。使用者须留意: ctx 轨的样本行宇宙是 full 轨留篇集合 (`llm_verified_full == True`) 的条件子集, 而非独立抽样得到的第二套文章池, 因此该列所反映的高置信度正面实质性可测样本规模天然受 full 轨留篇结果约束; 当某银行-年在 full 轨留篇集合极小 (例如小型银行报道稀疏) 时, ctx 轨的高置信度子样本可能进一步收缩至个位数甚至为零, 对应 `washing_ratio_hc_ctx` 该格取 NaN 而非 0, 反映的是「信息不足以做出可靠判定」而非「洗稿率为零」。此外, ctx 窗口聚焦实体邻近文本而非全文, 部分依赖跨句语境理解创新实质性的报道 (例如描述先于命名实体出现的技术细节段落) 在 ctx 轨可能被判定为「无法测量」(NaN) 而非全文轨下的「实质性」标签, 这是该列相对 `_full` 轨规模可能系统性更小的一个已知机制, 应在稳健性附表中以并排三轨方式呈现而非取三者均值合并。

## VAR: pos_hc_substvalid_count_full

【变体差分】
本列取 track=`_full` (标题+正文全文文本), 是该家族三轨中的主测度轨 (canonical/primary): full 轨承担留篇门控职责 (`llm_verified_full == True` 决定一篇报道是否被计入银行金科报道样本), 因此 `_full` 轨的行宇宙即为分析样本全集, 而 `_ctx`/`_ss` 轨均是该集合的条件子测度。计算上, 该列合取「`pos_count_full`=1」∧「`llm_agreement_rate_full` ≥ 2/3 − 1e-9」∧「`innovation_substantiveness_full` 已成功测量 (落在实质性/象征性二选一标签内)」, 三个上游变量均基于全文文本由三家 LLM 独立投票/分类。它是 `washing_ratio_hc` (无后缀, 主指标) 的分母, 也是入口处必检列 `llm_sentiment_full`/`llm_agreement_rate_full` 所在数据链路的下游派生。作为三轨之一, 它与 `_ctx`/`_ss` 两列互为稳健性、不分主次, 但在留篇口径与论文正文报告惯例上通常被列为首要报告轨: `run_pipeline_function.py::_stage21_skip_is_compatible` 与 `tone_llms.py::df_filtered` 两处门控副本均以 `llm_verified_full` 判定一篇报道是否计入分析样本, 而非以 ctx/ss 轨各自的验证状态判定, 因此本列的分母规模 (以及分子 `pos_symb_hc_count_full`) 直接决定了 `washing_ratio_hc` 主指标在多少银行-年格上有非缺失取值。相较 ctx/ss 两轨窗口更宽, 该列在多数银行-年格上高置信度子样本规模最大、NaN 比例最低, 是稳健性附表中信息量最充分的一轨; 但同时也最易受与金融科技完全无关的正面段落 (标题+全文中泛泛而谈的正面公关辞令) 干扰, 这正是 ctx/ss 两条更窄轨道存在的构念动机——以更强的实体/共现约束换取更聚焦的信号纯度, 三轨并排恰好覆盖「样本量-信号纯度」权衡的两端。

## VAR: pos_hc_substvalid_count_ss

【变体差分】
本列取 track=`_ss` (标题+银行∧金科同句 ±N 句窗口文本, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1), 是该家族在最严格共现窗口下的实现: 逐篇合取「`pos_count_ss`=1」∧「`llm_agreement_rate_ss` ≥ 2/3 − 1e-9」∧「`innovation_substantiveness_ss` 已成功测量」。ss 轨的回退语义镜像 ctx 轨: 当一篇文章内银行实体与金融科技词汇不存在同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 此时该篇在 ss 轨上的 LLM 判定实质上退化为对全文的重新分类 (与 ctx 轨窗口逻辑不同但退化结果类似), 该篇仍计入 `n_articles` 分母 (共享分母, 不因回退而被剔除)。作为三轨中窗口最窄、对「同句强共现」要求最严格的一轨, 其高置信度子样本规模通常对文章内银行-金科语句邻近程度最敏感, 与 `_full`/`_ctx` 两列并排构成互为稳健性的第三条测度路径, 三者严禁混入同一过度识别 Hansen J 检验。ss 轨的判据原语与 stage 13 共现硬过滤 (`entity_context.has_bank_fintech_cooccurrence_within_radius`) 及 stage 14 `content_ss` 物化共用「同句」这一核心概念, 但严格同句抽取 (`extract_bank_fintech_cooccurrence`) 与 stage 13 的 ±1 句窗过滤是两个不同判据口径 (禁互相复用), 本列继承的是 `content_ss` 文本物化结果之上再跑 LLM 分类的下游产物, 而非直接复用 stage 13 的硬过滤标签。由于 ss 窗口是三轨中信息量最受限的一支 (退化时等价于全文, 未退化时仅覆盖同句及其紧邻上下文), 该列在实践中往往表现出比 ctx 轨更极端的规模收缩: 当银行-年报道量本就稀疏 (T=2 开发样本典型场景) 时, `pos_hc_substvalid_count_ss` 可能整格为零, 对应的 `washing_ratio_hc_ss` 全部退化为 NaN, 这是样本设计下的预期退化而非实现缺陷, 生产语料 (T=18, 全量 1700 万条) 上样本密度显著提升后该退化预计大幅缓解。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance. https://doi.org/10.1016/j.jbankfin.2024.107191
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as Data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
<!-- rendered-citations:end -->
</content>
