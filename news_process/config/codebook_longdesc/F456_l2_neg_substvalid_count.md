---
family_id: F456
columns:
- neg_substvalid_count_ctx
- neg_substvalid_count_full
- neg_substvalid_count_ss
unit: 篇数/计数 (count)
formula: 'bank-year 求和: sum(is_negative{track}==1 且 innovation_substantiveness_full 已测量 ∈ {SUBST_VALID_LABELS})，三轨共用同一实质性掩码 (仅消费 _full 轨的 innovation_substantiveness_full, ctx/ss 轨不各自消费 innovation_substantiveness_ctx/_ss)，仅分子的情感判定 is_negative{track} 逐轨切换，聚合自篇章级指示列 _svd_neg{track}（_pool_svd_substvalid_counts 按 target_bank×year groupby-sum）'
producer: pipeline\panel\runner.py (步骤 5 aggregate_panel 后紧随调用 _pool_svd_substvalid_counts 完成聚合; 步骤 7h 洗稿率构造区仅消费本列作除法分母, 不产出本列)
upstream:
- is_negative_full
- is_negative_ctx
- is_negative_ss
- innovation_substantiveness_full
citations:
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: Count (and count-like) data in finance
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 529-551
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: 'When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks'
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
new_dois: []
---

## CORE

【构念与来源】
本家族 neg_substvalid_count 是 P3 substance (实质性 vs 象征性) 洗稿率测度族的同域分母计数, 三列分别对应 full/ctx/ss 三轨。它不是一个独立经济构念的直接测度, 而是"方法 B 反向验证"(runner.py 步骤 7h)分母同域化修复的产物: 度量一家银行在给定年份、给定文本轨道下, 被 LLM 判为负面 (is_negative{track}==1) 且实质性/象征性分类已成功输出 (innovation_substantiveness{track} 落在 SUBST_VALID_LABELS 有效标签集合内, 而非 LLM 拒答/平局/缺席导致的 NaN) 的报道篇数。它与分子列 neg_sub_count{track} (负面∧实质性) 搭配构成比率 neg_sub_ratio{track} = neg_sub_count{track} / neg_substvalid_count{track}, 回答"在所有'负面且实质性分类可信'的报道里, 有多少确实被判为实质性内容, 而非泛泛负面表态"。

【方法学与计算】
构造分两步, 且有一处三轨口径上须精确澄清的实现细节: 实质性掩码本身并不逐轨切换。第一步在文章级 (encode 阶段消费的 df) 中, runner.py 只从 innovation_substantiveness_full 一列派生 _subst_measured = innovation_substantiveness_full.astype(str).str.strip().isin(SUBST_VALID_LABELS) (即该篇报道基于 full 轨全文的 LLM 三分类输出是否成功落地为"实质性"或"象征性"之一, 排除因文本不足/模型拒答导致 astype(str) 变成字符串 'nan' 的失败案例), 随后在 for track in ['_full','_ctx','_ss'] 循环内, 三轨共同复用这同一个基于 full 轨的 _subst_measured 掩码来构造 _svd_neg{track} = (is_negative{track}.fillna(0)==1) & _subst_measured。也就是说, neg_substvalid_count_ctx 与 neg_substvalid_count_ss 的"实质性已测量"这一半判据, 实际取自 innovation_substantiveness_full 而非各自轨道的 innovation_substantiveness_ctx / innovation_substantiveness_ss (后两者存在于面板但用于其他 4-way 交叉构造, 与本列无关); 三列真正逐轨切换的只有分子情感判定 is_negative{track}。is_negative{track} 是 nullable Int8, NaN 表示情感判定本身失败或平局, fillna(0) 后与 1 比较可把 NaN 行安全排除在分子外。第二步是 runner.py::_pool_svd_substvalid_counts 在步骤 5 (aggregate_panel 之后紧随调用) 按 (target_bank, year) groupby-sum 把所有 _svd_* 前缀列聚合为 bank-year 计数, 并重命名 _svd_neg{track} → neg_substvalid_count{track}, 与 balance_panel 步骤 6a 的计数零填正则兼容 (零新闻 bank-year 落 0, 供 _safe_ratio 判 <=0 时返回 NaN, 而不是被 0/0 撑出 RuntimeWarning)。步骤 7h 洗稿率构造区不产出本列, 只作为 neg_sub_count{track} 的同域分母被 _svd_denom 读取消费, 二者是同一比率的分子/分母搭配关系而非上下游派生关系。

本列的存在直接来自一处已知的历史缺陷修复 (fix omni-g-runner-10/g-runner-14, 2026-06-11): 早期洗稿率分母直接用全部负面文章的物理计数 (neg_count{track}), 但分子 neg_sub_count{track} 隐式要求实质性分类已测量成功 (NaN 经 astype(str) 变 'nan' 恒判 False, 永不进分子)。这造成"valid 分子 / physical 分母"的口径失配: 当 LLM 实质性分类失败率上升时 (例如文本过短、ctx/ss 轨窗口截断导致上下文不足), 分子系统性缩水而分母不变, neg_sub_ratio 被人为拉低, 制造"负面报道更象征性"的假象, 而真实原因只是分类失败率抬升。neg_substvalid_count{track} 就是把分母也限定在"负面∧实质性已测量"这一同域子集, 修复该系统性下偏。_svd_denom 辅助函数在消费端保留了向后兼容: 若某次重跑面板 schema 中缺失该列 (旧 schema), 会告警后回退到物理计数 neg_count{track}, 但生产管线在本列存在时恒走同域分母, 不静默混用两种口径。

【文献定位】
负面报道的"数量 vs 实质性"区分呼应 Piotroski, Wong & Zhang (2015, JAR) 对中国上市公司政治关联企业压制负面信息的实证研究——该文的核心发现是政治关联/激励会系统性压低负面信息的对外披露频次与力度, 说明观测到的负面报道数量本身可能是被压制、被稀释后的结果, 并非负面信息真实存在与否的可靠代理; 这与本家族区分"泛泛负面表态"和"实质性可信的负面报道"的分母限定精神相呼应——二者共同的方法论警示是: 单纯的负面报道计数容易被制度性/激励性因素扭曲, 需引入额外维度 (该文用政治关联强度, 本家族用实质性分类掩码) 加以校正才能得到可信测度。count 型经济计量变量本身的构造与推断陷阱可参照 Cohn, Liu & Wardlaw (2022, JFE) 对金融研究中计数与类计数数据的系统性讨论, 其核心告诫正是分子分母域不一致会产生系统性偏误, 本家族的历史 bug 修复正是该告诫的一个实证案例。文本挖掘中"实质性 vs 象征性"披露的区分传统上溯 Loughran & McDonald (2011, JoF) 关于文本分析中字典/语境判定可靠性的方法论基础, 以及更晚近的 Duchin, Gao & Xu (2025, JoF) 对可持续性披露"洗绿" vs 真实资产市场行为脱钩的实证设计——本家族所在的洗稿率族正是该"披露-行为脱钩"研究范式在中国银行金科新闻语境下的应用。实质性分类由 LLM 三分类输出, 其标注可靠性与"已测量/未测量"掩码逻辑呼应 Gilardi, Alizadeh & Kubli (2023, PNAS) 关于 LLM 文本标注质量与失败模式的讨论, 为 SUBST_VALID_LABELS 掩码机制 (排除拒答/平局导致的伪 NaN) 提供方法学依据。

【口径铁律】
本家族三列对应 full/ctx/ss 三轨文本, 各自独立聚合、各自 just-identified 并排, 属互为稳健性、不分主次的规格集合, 严禁混入同一 over-identified Hansen J 检验。full 轨对应留篇门控 (2026-06-29 起 llm_verified_full==True 为唯一留篇判据) 下的主指标, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集。ss 轨遵循镜像 ctx 的回退语义: 当某篇报道无银行∧金科同句共现时, content_ss 退化为全文 body (ss_is_fallback=True), 与 ctx 共享 n_articles 分母口径; FINTECH_AC 缺失时三轨的 *_is_fallback 全部为 True, 优雅降级而非报错。三轨互相之间不可合并进同一右手侧回归或同一识别方程, 只能作为独立稳健性检验并列呈现。

## VAR: neg_substvalid_count_ctx

【变体差分】
本列是 neg_substvalid_count 家族在 ctx (标题+实体窗口) 文本轨上的实现: 分子指示列 _svd_neg_ctx 由 is_negative_ctx 与实质性掩码共同判定, 聚合口径与 full/ss 完全一致 (按 target_bank×year groupby-sum)。需精确澄清的是, 该实质性掩码实际上并非基于 innovation_substantiveness_ctx, 而是与 full/ss 两列共用同一个源自 innovation_substantiveness_full 的 _subst_measured 掩码 (runner.py 只对 full 轨全文输出做一次 SUBST_VALID_LABELS 判定, 三轨循环内直接复用); 因此 ctx 与 full/ss 在"实质性已测量"这一半判据上并不各自独立, 三列间真正逐轨切换、构成本列差异化来源的只有分子情感判定 is_negative_ctx 本身所消费的文本窗口不同。ctx 轨的文本物化 (content_ctx) 在 stage 14 ctx_materializer 完成, 以标题 (prepend_title) + 目标银行实体窗口拼接而成, 相较 full 轨 (标题+全文正文) 语境更窄、更聚焦于目标银行被提及的局部上下文, 相较 ss 轨 (银行∧金科同句±N窗) 语境更宽、不要求金科词与银行严格邻近。这意味着 neg_substvalid_count_ctx 捕捉的"负面且实质性可信"篇数, 其判定依据是围绕银行实体的局部语境而非全文, 当一篇报道标题/整体基调负面但涉及目标银行的具体段落语气中性或正面时, ctx 轨与 full 轨的负面判定可能出现分歧, 该列因此不是 full 轨的子集或简单缩放, 而是一个独立的、just-identified 的稳健性测度。

由于留篇门控自 2026-06-29 起改为 full-only (仅 llm_verified_full==True 的报道被判定为"一篇银行金科报道"), ctx 轨的行宇宙是 full 留篇集合的子集, neg_substvalid_count_ctx 的分母/计数基数因此与 neg_substvalid_count_full 不完全对齐, 二者差异一部分来自文本窗口本身的判定分歧, 另一部分来自留篇门控产生的样本宇宙收缩。使用该列做稳健性检验时, 应与 neg_substvalid_count_full 并列呈现而非替代, 用以说明主结论 (基于 full 轨) 是否对文本窗口选择敏感; 二者绝不可同时作为工具或内生解释变量塞入同一过度识别方程, 因其不仅共享同一上游情感判定机制 (三轨情感 LLM 本身相关), 更直接共享同一个基于 full 轨的 _subst_measured 实质性掩码 (代码层面的完全同源, 而非仅统计意义上的高相关), 会产生人为的高相关性而非独立识别力。由于 ctx 轨的"实质性已测量"半判据实际来自 innovation_substantiveness_full 而非 innovation_substantiveness_ctx, 本列的测量误差结构在实质性维度上并未独立继承 ctx 轨自身的分类误差, 而是与 full 轨共享该维度的误差来源; 仅情感判定维度 (is_negative_ctx) 是 ctx 轨独立贡献的差异化来源。

## VAR: neg_substvalid_count_full

【变体差分】
本列是家族的 canonical/主指标实现, 对应 full 轨 (标题+全文正文) 文本, 且是留篇门控 (full-only, 2026-06-29 起生效) 的判定依据来源。分子指示列 _svd_neg_full 由 is_negative_full (基于全文情感三家 LLM 多数投票的负面判定) 与实质性掩码 (innovation_substantiveness_full 落在 SUBST_VALID_LABELS) 共同构成, 聚合逻辑与 ctx/ss 相同, 但其分母基数覆盖的样本宇宙是三轨中最完整的一个——因为是否算作"一篇银行金科报道"这一留篇判定本身就以 full 轨的 llm_verified_full 为唯一依据, ctx/ss 只在 full 留篇之后作为条件测度 (conditional-on-full) 附加计算。

在洗稿率族 (washing_ratio 系列) 的构造中, neg_substvalid_count_full 是方法 B (反向验证) 分母同域化后的主分母, 与分子 neg_sub_count_full 搭配得到主指标 neg_sub_ratio_full, 用于回答"银行金科相关的负面报道中, 有多少确实涉及可核实的实质性内容而非泛泛负面表态"这一核心问题。它也是 washing_asymmetry_full (方法 B 相对方法 A 的非对称性指标) 的构造基础之一。作为 full-only 门控下的主轨, 该列在跨模型/跨轨稳健性检验中作为基准参照, ctx/ss 两列的差异幅度均以其为比较对象; 但三轨彼此地位是并列的 just-identified 规格, full 轨"主"的地位仅体现在留篇门控与论文正文默认呈现顺序上, 不代表其在统计推断上优先于 ctx/ss, 三者依然严禁混入同一过度识别方程。

## VAR: neg_substvalid_count_ss

【变体差分】
本列对应 ss 轨 (银行∧金科同句共现窗口, 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 生产默认 ±1 句), 是三轨中语境最窄、判据最严格的一支。分子指示列 _svd_neg_ss 由 is_negative_ss 与实质性掩码共同判定, 聚合方式与 full/ctx 相同; 需精确澄清的是, 该实质性掩码同样并非基于 innovation_substantiveness_ss, 而是与 full/ctx 两列共用同一个源自 innovation_substantiveness_full 的 _subst_measured 掩码, 三轨在"实质性已测量"这一半判据上代码层面完全同源, ss 轨真正独立贡献的差异化来源只有分子情感判定 is_negative_ss 所消费的严格同句窗口文本。ss 轨要求目标银行与金科关键词在同一句 (或指定窗口内) 共现才纳入非回退文本, 因此当一篇报道虽提及银行与金科但二者从未邻近共现时, content_ss 会回退为全文 body (镜像 ctx 轨的回退语义, ss_is_fallback=True, 与 ctx 共享 n_articles 分母), 此时 ss 轨的情感/实质性判定实质上退化为对全文的判定, 与 full 轨高度重合但不完全等价 (仍走独立的 LLM 调用与独立的实质性分类推断)。

neg_substvalid_count_ss 的经济含义是: 在"银行与金科议题真正紧密关联"的最严格语境下, 有多少负面报道的实质性分类是可信的。相较 ctx 轨(实体窗口, 不要求金科词邻近), ss 轨对"洗稿"构念的刻画更保守——它排除了那些仅因文章泛泛提及金科词但与目标银行论述并不紧密关联的报道, 理论上更贴近"该银行在金科议题上被负面且实质性报道"这一构念的严格定义。同样地, ss 轨的行宇宙也是 full 留篇集合的子集 (conditional-on-full), 计数基数天然低于或等于 full 轨对应值; 该列与 neg_substvalid_count_full/_ctx 三者并列构成互为稳健性的规格集合, 三者严禁混入同一 over-identified Hansen J 检验, 亦不应在同一回归右手侧同时出现造成共线性混淆识别力。

<!-- rendered-citations:begin -->
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
