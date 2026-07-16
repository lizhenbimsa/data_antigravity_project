---
family_id: F422
columns:
- loughran_pos_substvalid_count_ctx
- loughran_pos_substvalid_count_full
- loughran_pos_substvalid_count_ss
unit: 篇数/计数 (count, bank-year 聚合)
formula: 'loughran_pos_substvalid_count{track} = Σ_{articles in bank-year} 1[loughran_score{track} > 0] · 1[innovation_substantiveness_full ∈ {"象征性","实质性"}] (词典正面判定按各自轨道 track ∈ {full,ctx,ss}; 实质性已测量掩码固定取 _full 轨, 见下)'
producer: pipeline\panel\runner.py (`_pool_svd_substvalid_counts` 聚合 `_svd_{loughran}_pos{track}` 篇章级指示 → bank-year 计数); 上游词典打分 pipeline\sentiment\tone_words.py
upstream:
- loughran_score_full
- loughran_score_ctx
- loughran_score_ss
- innovation_substantiveness_full
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: 'Textual analysis in accounting and finance: A survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187-1230
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
- doi: "10.1111/eufm.12509"
  title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing"
  authors: "Gorovaia, N., & Makrominas, M."
  year: 2025
  venue: "European Financial Management"
  type: "journal"
- doi: "10.1016/j.techfore.2025.124511"
  title: "Unveiling AI washing: Bridging corporate technological gaps through a cognitive dissonance lens"
  authors: "Sun, Z., Wen, Y., Zhao, L., Almugren, I., & Galgotia, A."
  year: 2026
  venue: "Technological Forecasting and Social Change"
  type: "journal"
new_dois:
  - "10.1111/eufm.12509"
  - "10.1016/j.techfore.2025.124511"
---

## CORE

【构念与来源】
本家族三列 (loughran_pos_substvalid_count_full / _ctx / _ss) 度量的是"洗稿率" (washing ratio) 测度族里一个特定词典分支——Loughran-McDonald 中文主译本 (loughran_mcdonald_zh_2026, 下称 loughran 词典)——的分母计数, 即 bank-year 层面"loughran 词典判为正面语调、且该篇报道的创新实质性 (innovation_substantiveness) 已被 LLM 成功测量出象征性或实质性标签"的文章篇数。它不是一个独立设计的构念, 而是洗稿率族"方法 D2 (单个词典)"路径在 pipeline/panel/runner.py 中为保证分子分母同域而派生出的分母口径, 计入 codebook 是因为它作为独立列物化在面板中并被 washing_ratio_dict_loughran{track} 系列消费, 具备独立可审计价值。构念渊源可追溯两条线: 一是词典法情感度量本身, 源自 Loughran & McDonald (2011) 在 10-K 文本分析中确立的"金融专用词典优于通用词典"范式, loughran 词典是该谱系词表 (positive 1,295 / negative 3,729 词, 另含 uncertainty/litigious/strong_modal/weak_modal/constraining/complexity 共 6 类非极性词表) 的中文主译本, 在 config/tone_dicts.json 中登记, 由 pipeline/sentiment/tone_words.py 加载并对每篇报道逐轨打分; 二是"实质性 vs 象征性"披露区分, 源自组织理论中真实行动 (substance) 与话术管理 (symbolism) 的经典对立 (呼应 decoupling 文献脉络), 在本项目里体现为 LLM 对每篇报道的 innovation_substantiveness 三分类 (象征性/实质性/或测量失败)。二者交叉产生洗稿率的核心问题意识: 一家银行如果频繁被正面词语言包装、但报道内容缺乏可验证的实质性金融科技投入细节, 则其媒体形象与实际行为之间存在"洗稿"缺口。substvalid_count 正是为量化这一缺口而必须精确定义的分母。

【方法学与计算】
计算分两步、跨两个上游产出。第一步 (篇章级, tone_words.py): loughran 词典对每篇报道的三轨文本 (full=标题+正文、ctx=标题+实体窗口、ss=标题+银行∧金科同句±N窗) 各自独立打分, 得到 loughran_score_full / _ctx / _ss; 正面判定为 loughran_score{track} > 0 (词典法采用净语调计分, 不做绝对阈值切分, 符号即判定)。第二步 (面板聚合, runner.py): 对每篇报道构造一个篇章级布尔指示列 `_svd_loughran_pos{track}` = (loughran_score{track} > 0) AND (innovation_substantiveness_full 已被 LLM 判为"象征性"或"实质性"、非缺失), 随后 `_pool_svd_substvalid_counts` 按 (target_bank, year) 分组求和, 重命名为 `loughran_pos_substvalid_count{track}` 并左连接进 bank-year 面板。这里有一个关键的口径细节须写清: "实质性已测量"掩码 `_subst_measured` 固定基于 innovation_substantiveness_full 轨 (LLM 对全文的创新实质性判定), 不随 track 变化——即便 loughran_score 本身按 ctx/ss 轨分别打分, 判定"该篇是否已被成功测量实质性"的掩码始终取 full 轨结果。需要澄清的是, 创新实质性分类本身在 tone_llms.py 中三轨 (full/ctx/ss) 均各自独立跑了一次 LLM 分类、各自产出 innovation_substantiveness_full / _ctx / _ss 三个独立列 (三轨口径下三份文本、三份解析结果、三份多数投票), 并非只在 full 轨算了一次; 但 pipeline/panel/runner.py 在构造 substvalid_count 的分母掩码时, 出于口径收敛与留篇门控 (full-only, 2026-06-29 起) 对齐的考虑, 三条 substvalid_count 列 (full/ctx/ss) 一律固定选用 innovation_substantiveness_full 这一份结果作为"是否测量成功"的判据, 而不各自取用同轨的 innovation_substantiveness_ctx / _ss。这是 runner.py 层面的聚合口径选择, 不是 ctx/ss 轨"没有独立跑分类"; 三轨 substvalid_count 之间的差异因而完全来自分子端 (loughran_score{track} 的符号在三个文本窗口下可能不同), 分母掩码本身是同一批"full 轨已测量成功"的篇目集合。之所以要构造这个同域分母而非直接用"该轨全部正面文章数", 是修复了 omni-g-runner-10/g-runner-14 记录的一个系统性偏差: 洗稿率的分子 (正面∧象征性) 天然要求 innovation_substantiveness 非缺失 (NaN 经 astype(str) 变 'nan' 字符串, 恒不等于'象征性', 故 LLM 分类失败的文章永远进不了分子); 但旧版分母若仍数"全部正面文章"(不管实质性是否测出), 则每当 LLM 实质性分类失败率上升, 分子端"合法丢失"而分母端"照常计入", 洗稿率会被系统性稀释走低——这是一个测量假象, 不是银行真实洗稿行为变化。substvalid_count 用"分子分母同域"原则堵上这个漏洞: 分母只数"LLM 确实对其做出了实质性/象征性判定"的那批正面文章, 使得 washing_ratio_dict_loughran{track} = loughran_pos_symb_count{track} / loughran_pos_substvalid_count{track} 的比值不再因分类失败率漂移而虚假波动。该列同时也是 balance_panel 步骤"计数零填正则"的命中对象: 零新闻覆盖的 bank-year 会被填 0, 下游 `_safe_ratio` 遇到 0 分母时正确返回 NaN 而非除零或虚假 0 值。

【文献定位】
词典法情感测度的方法学基础是 Loughran & McDonald (2011, The Journal of Finance) 对通用词典 (如 Harvard-IV) 误判金融文本极性的系统性批判, 及其提出的金融专用正负面词表——这也是 loughran 词典 (中文主译本) 的直接理论来源, 其"negative 显著大于 positive"的不对称词表规模 (3,729 vs 1,295) 正是该文强调的金融文本负面语汇远比正面语汇丰富这一发现的中文映射。Loughran & McDonald (2016, Journal of Accounting Research) 对文本分析在会计与金融领域应用的系统综述, 进一步确立了词典法情感计数 (包括正面词计数这类原子测度) 作为该领域标准工具箱的方法学地位, 也是本项目在消融敏感性设计上的方法论参照。Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 对"文本作为数据"的方法论综述则从更宏观角度确立了词典法与机器学习/LLM 法互为稳健性对照臂的正当性, 呼应本项目"三家 LLM 投票 / 六词典 / 三 BERT 模型互为稳健性、不分主次"的整体设计哲学——substvalid_count 族正是词典法在洗稿率这一具体应用场景下, 与 LLM 法 (A/A2) 及 BERT 法 (E/E2) 并排的稳健性分支之一。loughran 词典本身与 bian_2021 (Bian, Jia, Li & Yan, 2021) 等其他五部中文金融情感词典同属一个"固定 union 词典 + 六词典互不替代"体系: build_union_dictionary 步骤将六部词典求并集用于 msent/pos_ratio/neg_ratio 等聚合测度, 但 substvalid_count 族刻意保留逐词典独立计数 (方法 D2), 使得 loughran、bian_2021、du_2022 等各词典各自的正面判定及其洗稿率分母互为跨词典稳健性对照, 不因求并集而抹平差异。需要特别强调的是三轨口径: full/ctx/ss 三条文本窗口下的词典打分各自独立、各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一个 over-identified 的 Hansen J 检验框架; 留篇门控 (2026-06-29 起) 采用 full-only 口径, 即 stage 21 是否判定"一篇报道构成有效银行-金科报道"只看 llm_verified_full, ctx/ss 轨的行宇宙是 full 轨留篇集合的子集, per-track 列各自照算——substvalid_count 的三轨列同样遵循这一行宇宙约束: ctx/ss 轨的分子 (loughran_score{track}>0) 只在 full-only 留篇集合内计算, 而非独立扩样。

## VAR: loughran_pos_substvalid_count_ctx

【变体差分】
本列是家族在 ctx (context) 轨下的实现: 分子端 loughran_score_ctx 取标题 + 目标银行实体窗口内正文片段 (config/filtering.yaml::context_window 控制窗口大小) 打分, 与 full 轨的差异在于文本范围收窄到银行实体周边——若某篇报道整体基调偏正面但金科相关段落偏中性或负面 (或反之), ctx 轨的 loughran_score_ctx 符号可能与 full 轨不一致, 导致该篇是否计入本列分子会与 loughran_pos_substvalid_count_full 产生分歧。分母端 (是否"实质性已测量") 与 full/ss 两轨完全相同, 均固定取 innovation_substantiveness_full 掩码——即三列共享同一批"LLM 判过实质性"的篇目集合, 差异纯粹来自分子。ctx_is_fallback 语义: 若某篇报道没有可识别的银行实体窗口 (fallback 触发), content_ctx 回退为全文 body, 此时 loughran_score_ctx 在效果上等价于 loughran_score_full 的一个近似 (但两者由独立打分调用产生, 不做数值层面的强制相等)。本列与 _full、_ss 两列互为稳健性并排关系, 不设定单向包含或替代, 三者共同支撑 washing_ratio_dict_loughran_ctx 这一稳健性分支的分母, 禁止在同一 over-identified 设定中把三轨混入同一工具变量集合。使用建议上, ctx 轨适合作为"聚焦银行相关段落而非整篇通稿基调"的稳健性检验: 当研究者担心 full 轨的正面判定被文章中与目标银行无关的段落 (例如同篇报道里提及其他机构、宏观政策背景等) 污染时, ctx 轨提供一个把打分范围收紧到银行实体窗口的替代口径, 可用于比较 washing_ratio_dict_loughran_full 与 _ctx 两个分支的结果是否定性一致; 若二者高度一致, 说明洗稿率的度量对文本窗口选择不敏感, 增强主结论的可信度; 若出现分歧, 则提示窗口选择本身是一个值得披露的测量维度, 而非可以随意二选一的实现细节。

## VAR: loughran_pos_substvalid_count_full

【变体差分】
本列是家族的 canonical/主规格轨: 分子端 loughran_score_full 基于"标题 + 完整正文"打分, 是三轨中信息量最完整、不依赖实体窗口识别或同句共现判定成功与否的轨道, 因而在稳健性梯子中通常作为默认呈现的口径 (镜像 P1 treatment 的 full-only 主轨切换先例)。分母端"实质性已测量"掩码本身就直接来自 innovation_substantiveness_full, 与本列分子同源于 full 轨文本, 是三列中分子分母文本口径最内在一致的一支 (ctx/ss 两列的分子虽用各自轨文本, 分母仍借用 full 轨的实质性判定, 存在跨轨借用)。留篇门控 (full-only, 2026-06-29 起) 的行宇宙定义直接以本列所属的 full 轨为准: stage 21 是否留用一篇报道只看 llm_verified_full, 因此本列的分子分母都天然落在这个门控之内, 不存在"轨道扩样"的额外复杂度。本列与 _ctx、_ss 两列同为 just-identified 并排、互为稳健性、不分主次, 是文献定位段所述"词典法内部三轨稳健性网格"的中心节点, 但不构成对另两轨的统计优先级。在下游消费上, washing_ratio_dict_loughran_full (以本列为分母、以对应的 pos_symb_count_full 为分子) 通常是研究者报告主结果表格时首选呈现的口径, 原因不在于其统计优先级更高, 而在于其与留篇门控行宇宙、与创新实质性判定文本口径三者共享同一个 full 轨、内在一致性最强、最便于读者追踪"这一篇报道是怎么被计数的"这条审计链路; ctx/ss 两轨的结果应作为并列稳健性检验一并披露, 而非仅在附录一笔带过。

## VAR: loughran_pos_substvalid_count_ss

【变体差分】
本列是家族在 ss (same-sentence) 轨下的实现: 分子端 loughran_score_ss 基于"标题 + 目标银行∧金科关键词同句 (±N 句窗口, 默认 N=1, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制) 拼接文本"打分, 是三轨中文本范围最窄。相关方法脉络上, Gorovaia & Makrominas (2025, European Financial Management) 用自然语言处理与词典法从企业社会责任报告文本中识别"洗绿"的语言标记, 呼应本家族以词典正面判定与实质性掩码构造洗稿率分母的方法学思路; Sun, Wen, Zhao, Almugren & Galgotia (2026, Technological Forecasting and Social Change) 以认知失调理论量化企业"AI 洗白"(话术与实际技术能力的落差) 对技术差距的影响, 与本家族"象征性 vs 实质性"披露区分构念直接对应、判据最严格的一支——要求银行与金科词汇在同一句 (或邻近窗口) 内共现才纳入该轨的"实体窗口"文本, 因此对语调符号的敏感度与 ctx 轨、full 轨都可能不同。回退语义镜像 ctx 轨: 若某篇报道不存在银行∧金科同句共现 (常见于 dev T=2 小样本下), content_ss 回退为全文 body 且 ss_is_fallback=True, 此时 loughran_score_ss 实际读取的文本与 full 轨相同, 但仍由独立调用产生独立数值, 且该回退状态由 n_articles 分母共享的方式在下游标注 (与 ctx 轨共享同一套 fallback 记账口径)。分母端同样固定借用 innovation_substantiveness_full 掩码, 与 _ctx、_full 两列一致, 三列的分母口径不因分子轨道收窄而收窄。本列与另两轨互为稳健性并排, 是词典法洗稿率分母族里判据最严格因而通常样本量 (非零计数的 bank-year) 最小的一支, 在 dev T=2 小样本上可能出现较多零值或 fallback 主导的退化观测, 属该判据下的预期表现而非缺陷; 与 _full、_ctx 一样, 禁止混入同一 over-identified Hansen J 设定。判据后缀须与三轨文本后缀区分开: ss 轨的"同句"判据是分子端 loughran_score_ss 打分文本的构造规则, 与网络结构指标族 (如 bank_clustering 等) 中另一套独立的 {同篇/±1句窗/严格同句} 判据后缀体系 (config/panel.yaml::network_criteria) 是完全不同的两套后缀命名空间, 不可混淆; 本列后缀 `_ss` 属于三轨文本架构 (full/ctx/ss), 语义固定为"标题+银行∧金科同句±N窗", 不随下游网络指标的判据梯子变化。使用建议上, ss 轨因判据最严格、样本覆盖面最窄, 在生产全量语料 (T=19, 18,198,978 条报道) 下预期仍能保留可观的非零观测, 但在本机 dev T=2 (110 家银行 × 2 年) 小样本上很可能出现大量 fallback 触发 (回退为全文口径) 或零计数——这是判据本身在稀疏样本下的预期退化, 不应被误读为代码缺陷或数据丢失; 生产语料上的实际非零率须以实测为准, 不应据 dev 样本外推。

<!-- rendered-citations:end -->

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Gorovaia, N., & Makrominas, M. (2025). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management. https://doi.org/10.1111/eufm.12509
Sun, Z., Wen, Y., Zhao, L., Almugren, I., & Galgotia, A. (2026). Unveiling AI washing: Bridging corporate technological gaps through a cognitive dissonance lens. Technological Forecasting and Social Change. https://doi.org/10.1016/j.techfore.2025.124511
<!-- rendered-citations:end -->
