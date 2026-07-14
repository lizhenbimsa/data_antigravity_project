---
family_id: F222
columns:
- du_2022_pos_substvalid_count_ctx
- du_2022_pos_substvalid_count_full
- du_2022_pos_substvalid_count_ss
unit: 篇数/计数 (count, 非负整数)
formula: "du_2022_pos_substvalid_count{track} = Σ_{article ∈ bank-year} 1[ du_2022_score{track} > 0 ∧ innovation_substantiveness_full ∈ {实质性, 象征性} ]"
producer: news_process/pipeline/panel/runner.py::main (篇章级 washing_cols 块内联构造 _svd_du_2022_pos{track}, D2 词典分支) → news_process/pipeline/panel/runner.py::_pool_svd_substvalid_counts (bank-year 聚合)
upstream:
- 22_tone_words.parquet (du_2022_score_full / du_2022_score_ctx / du_2022_score_ss)
- 21_tone_llms.parquet (innovation_substantiveness_full)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking & Finance
  vol: 164
  pages_or_artno: 107191
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
- doi: "10.1016/j.eswa.2024.125739"
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  authors: "Ma, Y., Zhang, T., & Zhang, P."
  year: 2025
  venue: "Expert Systems with Applications"
  type: "journal"
- doi: "10.1111/eufm.12509"
  title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing"
  authors: "Gorovaia, N., & Makrominas, M."
  year: 2024
  venue: "European Financial Management"
  type: "journal"
new_dois:
  - "10.1016/j.eswa.2024.125739"
  - "10.1111/eufm.12509"
---

## CORE

【构念与来源】
本家族三列 du_2022_pos_substvalid_count{track} 度量的不是情感强弱, 而是一个 bank-year 层面的"同域分母计数": 在某银行某年度的报道集合里, 有多少篇文章同时满足两个条件 — 一是被 du_2022 金融情感词典判为正面语调 (du_2022_score{track} > 0), 二是该篇文章的创新实质性维度 (innovation_substantiveness) 已被大模型成功测量 (取值落在"实质性"或"象征性"两个有效标签内, 而非缺测的 NaN)。这个计数存在的唯一理由, 是为洗稿率 (washing ratio, 即"正面且象征性"文章占正面文章的比例) 提供一个语义自洽的分母。构念根源在 Westphal & Zajac (1998) 的实质—象征二分框架: 企业对外披露既可能反映真实的战略投入 (substance), 也可能只是迎合利益相关者预期的符号性修辞 (symbolism); 把银行金科报道里"看起来正面但实为象征性表态"的比例识别出来, 正是本项目 P3 (bank_fintech_substance) 主线关切的构念。

【方法学与计算】
计算分两步落在 runner.py。第一步在篇章级: 对每篇文章、每条轨道构造 _svd_du_2022_pos{track} 指示列, 其值 = 1[du_2022_score{track} > 0] 与 1[innovation_substantiveness_full ∈ {实质性, 象征性}] 的逻辑与再转整数。此处有一个必须写清的口径不对称: 词典正面判定 du_2022_score{track} 是逐轨的 (full/ctx/ss 各用自身轨道的词典打分), 但实质性测量掩码恒取 innovation_substantiveness_full 单一来源 (full 轨), 三列共享同一实质性门。须辨明这里有两个彼此独立、不可混为一谈的机制: 其一是项目 2026-06-29 确立的 full-only 留篇门控, 它专指"一篇文章是否算作一篇银行金科报道 (是否留篇进入行宇宙)"由 llm_verified_full == True 单独裁定, 与本计数无直接接线; 其二是本计数自身的实质性掩码之所以只取 full 轨, 并非因为 innovation_substantiveness 这一 LLM 分类维度缺乏 ctx/ss 逐轨副本 — stage 21 实际上齐全产出 innovation_substantiveness_full / _ctx / _ss 三轨列, runner.py 亦确有消费 innovation_substantiveness_ctx 的下游分支 (P3 的 _sc 4-way 稳健性变体) — 而是 runner.py 中记载的 v3.2.0 BREAKING 设计决策: 洗稿率 washing 系列指标单独选用 _full 作为唯一 main spec 分母口径, 刻意不为 washing/substvalid 分母再展开 ctx/ss 逐轨版本, 以避免与三轨本身的稳健性梯度混淆。三列共用 full 轨实质性门, 根源是这一显式的口径取舍, 而非数据不可得。在此约束下, 轨道差异只体现在词典正面性一侧。第二步在聚合级: _pool_svd_substvalid_counts 按 (target_bank, year) 对全部 _svd_* 篇章指示求和, 并把列名从 _svd_du_2022_pos{track} 重写为 du_2022_pos_substvalid_count{track}。零新闻的 bank-year 经 balance_panel 笛卡尔补全后计数填 0, 下游 _safe_ratio 遇 0 分母安全返回 NaN 而非除零崩溃。之所以要"只数判出来的那批", 是因为分子 (正面且象征性) 隐含要求实质性已测量: 若旧实现用全部正面文章作分母, 则大模型实质性分类失败率越高、洗稿率被稀释得越低, 制造出与事实相反的假象 (fix omni-g-runner-10/g-runner-14 修正的正是这一 valid 分子 / physical 分母失配)。

【文献定位】
du_2022 词典本身来自 Du et al. (2022, Review of Finance), 该文构建了领域与语言双重专用的中文金融情感词典, 论证通用英文词典直译到中文金融语料会系统性失真; 本家族的正面判定即以其正面词表 (含 political_positive 以 0.5 权重计入) 打分为准。词典法情感度量的方法学规范可追溯至 Loughran & McDonald (2011, Journal of Finance) 对 10-K 文本词典构建与负债类词误判的经典处理, 以及 Gentzkow et al. (2019, Journal of Economic Literature) 对"文本即数据"高维稀疏计数方法的系统综述 — 本计数正是一个受语义掩码约束的文档级计数统计量。构念一侧, Westphal & Zajac (1998) 的象征性治理框架与 Bingler et al. (2024, Journal of Banking & Finance) 的"廉价言辞" (cheap talk) 披露研究共同支撑了"正面表态未必对应实质投入"这一识别动机, 使本分母计数在语义上锚定于洗稿率而非泛化的情感计数。Ma, Zhang, & Zhang (2025, Expert Systems with Applications) 构建面向中国国内投资者的细粒度中文情感词典 (CN-FSD), 验证词典法情感测度在中文金融文本上的领域适配性, 呼应本家族 du_2022 词典正面判定的方法学谱系。Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法识别企业社会责任报告中的漂绿(即正面披露与实质行动脱钩)现象, 直接支撑本家族"正面且象征性"洗稿率分母背后的实质—象征二分构念。

## VAR: du_2022_pos_substvalid_count_full

【变体差分】
本列取 full 轨: 词典正面判定 du_2022_score_full > 0 施于"标题 prepend + 全文正文"文本, 即 content_full。它是三轨中信息量最大、覆盖最全的轨道, 也是 P3 主线洗稿率 washing_ratio_du_2022 (无后缀 full 口径) 所消费的规范分母。语义上, 本列计数 = 某 bank-year 内被 du_2022 词典按全文打分判为正面、且创新实质性维度已被大模型成功测量的报道篇数。需要强调的是: 即便本列是 full 轨, 其实质性掩码来源 innovation_substantiveness_full 与词典轨道恰好同为 full, 因此本列是三列中"词典轨道与实质性门轨道天然对齐"的一列, 无跨轨借用问题。与 ctx/ss 两列的关系是: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨计数或其派生的三条洗稿率混进同一 over-identified Hansen J 过度识别检验。作为分母, 本列不进入主回归右手边, 只服务于 _safe_ratio 除法; 零新闻 bank-year 计数为 0 并使洗稿率安全落 NaN, 是设计内的优雅降级而非缺陷。还需说明本列与相邻计数族的构念边界: 本列只统计 du_2022 这一部词典的正面判定, 与 dict_pos_substvalid_count (六词典均值口径) 及 pos_substvalid_count (LLM 投票口径) 分属不同判定引擎, 三者是多引擎稳健性并排而非可加分解 — du_2022 因含政治正面词权重梯度, 其正面词表口径与其余五部词典系统性不同, 故必须保留独立的 du_2022 专属分母以支撑 washing_ratio_du_2022 单引擎洗稿率, 不能用词典均值分母代偿。此外, du_2022 词典的正面侧在生产口径下以 political_positive 词表 0.5 权重计入, 本列继承该 canonical 权重设定 (polw05), 权重敏感性梯度 {0.0,0.5,1.0} 只作用于连续 tone 分值族, 不再对本离散分母计数另开三臂列以避免列爆炸。

## VAR: du_2022_pos_substvalid_count_ctx

【变体差分】
本列取 ctx 轨 (实体窗轨): 词典正面判定 du_2022_score_ctx > 0 施于 content_ctx, 即"标题 prepend + 目标银行实体上下文窗口"文本, 而非全文。相较 full 列, ctx 列把词典打分限定在银行实体邻近的语境片段上, 更聚焦于与目标银行直接相关的表述, 代价是可能漏掉正文远处的正面语调。关键差分只在词典正面性一侧: 实质性测量掩码仍恒取 innovation_substantiveness_full (full 轨), 即本列是"ctx 轨词典正面 ∧ full 轨实质性已测量"的交集计数 — 掩码轨道与词典轨道刻意不对齐, 原因并非 innovation_substantiveness 分类维度缺乏 ctx 逐轨副本 (stage 21 确有产出 innovation_substantiveness_ctx, runner.py 的 P3 _sc 4-way 分支也确实消费了该列), 而是 runner.py 记载的 v3.2.0 BREAKING 设计决策刻意选定 _full 单轨作 washing/substvalid 分母的 main spec, 不为该分母再铺 ctx 版实质性门。此处不应与 full-only 留篇门控 (llm_verified_full 裁定是否留篇) 混为一谈, 二者是两个独立机制。因此本列并非 full 列的简单子集, 两者分母都由同一实质性门约束, 差异纯粹来自实体窗与全文在正面判定上的口径不同。本列服务于 ctx 轨洗稿率变体 washing_ratio_du_2022_ctx 的分母。它与 full/ss 两列各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。在 T=2 开发样本上 ctx 轨可能出现近零方差退化, 属预期现象, 生产 T=18 语料下方能充分展开。进一步区分本列与 full 列: 二者共享同一 innovation_substantiveness_full 实质性门, 分母候选池的"实质性已测量"约束完全相同, 唯一分歧在词典正面性判据施加的文本域 — full 用全文 content_full, ctx 用实体窗 content_ctx。因此若某篇文章在全文中有正面词但实体窗内没有, 它会计入 full 列却不计入 ctx 列; 反之则不可能 (实体窗是全文子串), 故本列在文档层面通常是 full 列同一实质性子样本上的偏小计数, 但二者并非严格嵌套的银行—年计数关系, 因为聚合发生在求和之后。本列聚合遵循 _pool_svd_substvalid_counts 的统一 groupby 求和路径, 零新闻 bank-year 由 balance_panel 填 0。

## VAR: du_2022_pos_substvalid_count_ss

【变体差分】
本列取 ss 轨 (同句轨): 词典正面判定 du_2022_score_ss > 0 施于 content_ss, 即"标题 prepend + 目标银行与金融科技词同句共现 ±N 窗"文本, 是三轨中语境最窄、判据最严的一轨。其回退语义镜像 ctx 轨: 当某篇文章不存在银行与金科同句共现时, content_ss 优雅回退为全文正文 (ss_is_fallback=True), 与 ctx 轨的回退处理保持对称。相较 full/ctx 列, ss 列只在银行与金科真正同句出现的最强共现语境里做词典正面判定, 因此其正面计数通常更小、信号更集中于银行—金科直接绑定的报道。差分同样只在词典正面性一侧: 实质性测量掩码依旧恒取 innovation_substantiveness_full, 掩码轨道与词典轨道不对齐, 原因并非 innovation_substantiveness 分类维度缺乏 ss 逐轨副本 (stage 21 同样产出 innovation_substantiveness_ss 列), 而是 runner.py 记载的 v3.2.0 BREAKING 设计决策刻意只用 _full 单轨作 washing/substvalid 分母的 main spec, 不为该分母再铺 ss 版实质性门; 这与 full-only 留篇门控 (llm_verified_full 裁定留篇) 是两个独立机制, 不可混同。本列服务于 ss 轨洗稿率变体的同域分母。它与 full/ctx 两列各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J 过度识别检验。同 ctx 轨, ss 轨在 T=2 开发样本上可能因同句共现稀疏而近零方差退化, 属预期, 生产规模语料下方能体现其严判据的鉴别力。要辨明本列的 ss 后缀是三轨文本后缀而非其它敏感性后缀: 它指的是词典打分所用文本轨道 (同句超级文档), 与网络指标族的 _sent 判据后缀 (银行∧银行严格同句) 分属两个正交口径, 不可混淆。ss 轨的回退语义务必与 CLAUDE.md 一致 — 无银行∧金科同句共现时 content_ss 回退为全文 body, ss_is_fallback 置 True, 该回退篇仍按其回退后的全文文本参与 du_2022 词典正面判定, 并共享 full 轨实质性门。因此在同句共现普遍稀疏的语料上, 大量回退会使本列在数值上向 full 列靠拢; 只有当同句共现充分时, ss 列才真正体现比 full/ctx 更严的银行—金科绑定语境筛选。本列服务的 ss 轨洗稿率同样只作稳健性并排, 不与 full/ctx 轨拼进同一过度识别检验。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications. https://doi.org/10.1016/j.eswa.2024.125739
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management. https://doi.org/10.1111/eufm.12509
<!-- rendered-citations:end -->
