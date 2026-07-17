---
family_id: F477
columns:
- pos_substvalid_count_ctx
- pos_substvalid_count_full
- pos_substvalid_count_ss
unit: 篇数/计数 (count)
formula: 'pos_substvalid_count{track} = 该银行-年内满足「LLM 三家投票正面(pos) 按 track 逐轨取值 且 innovation_substantiveness_full 已被成功测量(非缺失/非 NaN 字符串化, 该分母有效性判据恒取 full 轨, 循环内三轨共用, 非逐轨读取 innovation_substantiveness{track})」两个条件的文章篇数之和; track ∈ {_full, _ctx, _ss} 分子逐轨加总, 空集计 0 而非 NaN'
producer: pipeline\panel\runner.py (聚合函数 _pool_svd_substvalid_counts 定义于该文件行227, 调用与消费方 washing_ratio 系列分母均在同一文件内自聚合, 刻意不落入 encode.py)
upstream:
- 21_tone_llms.parquet (llm_vote_pos, 三家 LLM 投票正面判定)
- 16_article_policy_alignment.parquet / 相邻阶段的 innovation_substantiveness{track} 实质性分类列 (P3 W&Z 实质性 vs 象征性判据)
citations:
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
- doi: 10.1287/mnsc.2024.07420
  type: journal
  authors: Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C.
  year: 2026
  title: '"Glossy Green" Banks: The Disconnect Between Environmental Disclosures and Lending Activities'
  venue: Management Science
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as Data
  venue: Journal of Economic Literature
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
- doi: "10.1016/j.technovation.2023.102880"
  type: "journal"
  authors: "Granados, C., Ayala, Y., & Ramos-Mejia, M."
  year: 2024
  title: "Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation"
  venue: "Technovation"
  vol: "129"
  pages_or_artno: "102880"
new_dois: []
---

## CORE

【构念与来源】
本家族 F477 (`pos_substvalid_count_full` / `_ctx` / `_ss`) 度量的是「同域有效正面篇数」——在银行-年面板层面, 统计满足两个联合条件的文章篇数: 其一, 该篇文章的情感被 stage 21 三家 LLM (gpt54nano / gemini31 / deepseekv4) 多数投票判为正面 (`llm_vote_pos == True`); 其二, 该篇文章的 `innovation_substantiveness{track}` (实质性 vs 象征性分类, 对应 P3 W&Z substance-vs-symbol 传统的文本化操作) 已被成功测量, 即分类流程未因 LLM 解析失败、格式异常或该篇未进入实质性分类子样本而留空。二者的合取 (AND) 是本列的关键: 它不是简单的正面篇数, 也不是简单的实质性判定成功篇数, 而是两个判定同时成立的交集计数, 按 full/ctx/ss 三条文本轨分别独立累加。这一构念的直接使命是充当 `washing_ratio{track}` 系列(「洗稿率」/象征性正面披露占比)的分母, 而非独立作为处理变量或结果变量出现在任何 paper 的核心回归中。

「洗稿」(washing) 在本项目语境下特指: 银行金科相关报道被 LLM 判为正面情感, 但其内容在实质性维度上被判定为象征性 (symbolic) 而非实质性 (substantive) 陈述——即媒体渲染的正面语气缺乏具体、可验证的技术/业务实质支撑。这一构念传承自组织理论中「实质与象征」(substance and symbolism) 的经典区分(Westphal & Zajac, 1994), 该文献传统关注企业治理实践的采纳究竟反映真实的战略调整, 抑或只是应对制度压力/合法性诉求的符号性姿态; 本项目将其文本化操作应用于金融科技相关新闻报道的正面框架 (framing) 分析, 以 LLM 判读的「实质性成分是否可辨识」区分实质性正面与象征性正面。

【方法学与计算】
计算发生在两个阶段。第一阶段(生产实质性分类原语)在文章级流水线中, 对每篇通过 stage 13 共现硬过滤且落入 stage 21 LLM 情感投票的文章, 由 `innovation_substantiveness{track}` 判定器逐轨(full/ctx/ss)输出该篇是否具备可辨识的实质性技术/业务内容; 该判定器本身以 track 对应的物化文本 (`content_full`/`content_ctx`/`content_ss`, stage 14 `ctx_materializer` 产出) 为输入, 与 stage 21 三家 LLM 情感投票共享同一批文章池但是两个独立的分类任务。第二阶段(面板层聚合)在 `pipeline/panel/runner.py` 内由 `_pool_svd_substvalid_counts`(SVD 取 substantiveness-valid 之义, 与线性代数奇异值分解无关, 纯变量命名巧合; 该函数注释明确"v3.2.0 BREAKING: 裸 innovation_substantiveness 删除, 单独使用 _full 作 main spec")对银行-年分组执行, 其真实公式是「情感判定逐轨、实质性门槛 full-only」的非对称结构而非三轨各自独立门控: 分子条件是逐轨的, 为「该篇 `llm_vote_pos{track}` 为真」(is_positive{track} 按 track 分别取值); 但分母有效性掩码只在循环外计算一次, 唯一来源是 full 轨的 `innovation_substantiveness_full` 是否成功测量(非缺失), for track in [_full, _ctx, _ss] 三轨循环内共用同一个基于 full 轨算出的实质性有效性掩码, ctx/ss 轨并不各自读取 `innovation_substantiveness_ctx`/`_ss` 作分母门槛。换言之, `pos_substvalid_count_ctx`/`_ss` 与 `pos_substvalid_count_full` 三者共享同一「该篇是否具备可测量实质性内容」的门控判据(该判据恒由 full 轨给出), 三轨之间真正独立变化的只是分子(该篇在对应轨道文本上是否被判正面情感), 而非通常意义上「分子分母均逐轨独立」的完整三轨并排。真正逐轨读取 `innovation_substantiveness_ctx`/`_ss` 的判据用于另一族列(`_is_pos_symb{track}_sc` 等 4-way 交叉列), 并不进入本列所属的 `pos_substvalid_count{track}` 族。

这一列的引入直接修复了此前 `washing_ratio{track}` 分母口径的系统性偏误 (fix(omni-g-runner-10/g-runner-14), 2026-06-11 记录于 `pipeline/panel/runner.py` 源码注释)。旧口径的分母是「全部阳性(正面)文章的物理计数」`pos_count{track}`, 但分子(象征性正面篇数)隐式要求 `innovation_substantiveness{track}` 已被成功测量——`NaN` 经 `astype(str)` 后变为字符串 `'nan'`, 在布尔判据中恒为 `False`, 从而被系统性地排除出象征性正面的分子; 当 LLM 实质性分类失败率(因解析异常/格式漂移等原因)上升时, 分子的有效样本量收缩, 但旧分母仍数入全部正面文章(含分类失败的), 于是「洗稿率」= 分子/分母 出现系统性下偏——分类失败率越高, 表面上洗稿率越低, 这是测量误差而非真实信号, 与该批次修复的另一同族问题 encode-01 属同一类分子分母失配 bug。修复方案将分母改为本列 `pos_substvalid_count{track}` (阳性 ∧ 实质性已测量的同域计数), 使分子与分母定义在同一有效样本上, 消除该项系统性偏误。旧 schema 若缺失本列(向后兼容路径), 消费端 `runner.py::_svd_denom` 回退到物理分母 `pos_count{track}` 并输出 WARNING 告警, 以保持旧行为可追溯而非静默失真。

本列并非只服务 `washing_ratio` 一处: `runner.py` 中「方法 A: LLM 投票极化条件法」用其作 `washing_ratio{track}` 分母; 「方法 A2: 单个 LLM」对每家 LLM(`{llm}_pos_substvalid_count{track}`) 各自构造同构分母, 保证跨厂商稳健性度量互不借用彼此的有效样本; 「方法 B: 反向验证」构造对称的 `neg_substvalid_count{track}`(负面 ∧ 实质性已测量) 作 `neg_sub_ratio{track}` 的分母, 并据此计算 `washing_asymmetry{track}` 度量正负两侧洗稿倾向的不对称性; 「方法 C: 情感纯度缺口」进一步比较实质性与象征性两侧的情感纯度差异。本列因而是整个洗稿率测度族(washing_ratio / washing_ratio_{llm} / neg_sub_ratio / washing_asymmetry)共享的分母基石之一, 其三轨版本(full/ctx/ss)保证下游各条测度都能在对应轨道内自洽计算, 不发生跨轨错配。

本列继承项目三轨架构的通用语义: full 轨以标题+全文正文为判定文本, ctx 轨以标题+实体窗口截取文本为判定文本, ss 轨以标题+银行∧金科同句(±N 句窗, 默认 N=1)共现片段为判定文本。需注意本列的三轨并非「分子分母均逐轨独立」的完整并排结构——三轨在分子(该篇是否被判正面情感)上各自独立取值, 但分母有效性门槛(该篇 `innovation_substantiveness` 是否成功测量)恒由 full 轨给出并在三轨间共用, 这一非对称结构是 `_pool_svd_substvalid_counts` 的真实实现口径, 与「逐轨读取 innovation_substantiveness{track}」的直觉表述不同。即便如此, 三轨计数在下游(如 washing_ratio{track})各自 just-identified 并排、互为稳健性、不分主次, 铁律是三轨结果禁止混入同一 over-identified Hansen J 检验框架。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body(与 `content_full` 相同文本), 对应 `ss_is_fallback` 标记为真, 该情形下 `pos_substvalid_count_ss` 的计入逻辑与 full 轨共享同一批文章池, 但计数本身仍按 ss 轨独立累加, 不借用 full 轨的计数结果。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇文章是否被认定为「一篇银行金科报道」只取决于 `llm_verified_full == True`, ctx/ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 轨留篇集合的子集; 因此 `pos_substvalid_count_ctx`/`_ss` 的样本篇数上限不会超过 `pos_substvalid_count_full` 对应的留篇集合规模。

【文献定位】
本列所服务的洗稿率(washing ratio)测度族, 其构念根源是组织理论中实质与象征的区分传统。Westphal & Zajac (1994, *Administrative Science Quarterly*) 提出企业治理实践采纳存在「实质性执行」与「象征性姿态」的分野, 这一区分被后续文献扩展到 ESG/可持续发展披露领域的「漂绿」(greenwashing)研究: Duchin, Gao & Xu (2025, *The Journal of Finance*) 通过资产市场证据区分可持续性实践的真实性与象征性; Giannetti, Jasova, Loumioti & Mendicino (2026, *Management Science*) 记录了银行环境披露与实际放贷行为之间的脱钩现象, 与本项目「情感正面但实质性缺失」的洗稿构念高度同构, 均以「话语层面的正面表述」与「可验证的实质行为/内容」之间的落差作为核心识别标的。本列作为该类测度的分母基石, 其方法学定位对应文本量化研究中「以 LLM 标注承担分类任务、并以有效样本(而非全样本)作比率分母」的通用规范, Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 对文本作数据(text as data)的方法论综述强调了此类比率测度必须保证分子分母定义域一致, 这正是本列存在的直接方法学动机。 在金融科技这一具体议题下, Huang 与 Ma (2024) 检验金融科技发展对企业实质性绿色创新与象征性绿色创新的差异化影响, 明确采用「实质性 vs 象征性」二分, 与本列分母有效性判据所依赖的 innovation_substantiveness 标签在概念与中文表述上直接对应, 说明该二分在金融科技语境下已具备既有实证基础; 迁移边界在于, 原文的实质/象征由专利类型 (发明 vs 实用新型/外观) 客观划分、主体为非金融上市公司且金融科技是解释变量, 本项目则由 LLM 对新闻文本逐篇判定、主体为银行且金融科技是被报道的议题本身, 原文亦未构造任何比率型 washing 指标, 因此它只锚定二分标签的构念合法性, 不锚定本列作为比率分母的构造方式。构念的理论界定则可参照 Granados、Ayala 与 Ramos-Mejia (2024) 对「创新剧场」(innovation theater) 的系统刻画, 即技术创新的象征性展演与实质性投入之分野, 这为本列「唯有实质性判定被成功给出的报道才具备进入分母的资格」提供了理论上的必要性依据 —— 若实质与象征之别本身不成立, 该有效性判据即无构念意义; 须诚实标明的是, 原文为组织层面的构念研究, 并未提供文本自动分类算法, 非中国语境、非银行业、亦无面板计量, 本项目把该构念操作化为 LLM 对新闻报道话语的逐篇标签并按银行-年计数, 操作化层级与数据类型均与原文不同。
## VAR: pos_substvalid_count_full

【变体差分】
`pos_substvalid_count_full` 是本家族三轨中的 full 轨, 判定文本为标题+全文正文 (`content_full`, stage 14 物化), 是留篇门控的门控轨——一篇文章是否进入「银行金科报道」样本, 仅由该篇在 full 轨的 `llm_verified_full == True` 决定 (2026-06-29 起生效的 full-only 铁律)。因此 `pos_substvalid_count_full` 对应的分子(`llm_vote_pos_full`)与分母有效性条件(`innovation_substantiveness_full` 非缺失)均定义在该门控留篇集合的全集上, 是三轨中样本量最大、覆盖最完整的一支, 也是 `washing_ratio` 主口径(无后缀 `washing_ratio` 对应 full 轨, 按项目「full 不加后缀」的变量命名约定)所依赖的分母。与 ctx/ss 两支相比, full 轨基于全文判定, 覆盖文章中可能出现在实体窗口/共现句之外的实质性描述或象征性措辞, 因此其正面∧实质性联合计数在信息完整度上最高, 但也可能因全文噪声(如与银行金科无关的段落)引入判定噪声; ctx/ss 是在此基础上的聚焦化稳健性检验, 三者按铁律各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified Hansen J。

作为 washing_ratio 主口径的分母, `pos_substvalid_count_full` 在数值上通常大于或等于 `pos_substvalid_count_ctx`/`_ss`(因判定文本覆盖面更广、更少触发象征性判定的信息不足情形), 但这并不意味着 full 轨在构念上优先于其余两轨——三轨的定位是并列的稳健性对照, 而非「主指标+补充检验」的层级关系; 唯一的层级差异体现在留篇门控职责上, 即只有 full 轨承担样本纳入/排除的决定权, 三轨的洗稿率联合分母计数本身互不隶属。方法 A2(单个 LLM)的 `{llm}_pos_substvalid_count_full` 版本与本列共享同一 full 轨判定文本, 但各家 LLM(gpt54nano/gemini31/deepseekv4)独立判定正面, 因此跨厂商稳健性检验与本列(三家投票共识版)是另一组互为稳健性、不分主次的并排关系, 同样禁止混入同一 Hansen J 检验框架。

## VAR: pos_substvalid_count_ctx

【变体差分】
`pos_substvalid_count_ctx` 是 ctx 轨版本, 判定文本为标题+实体窗口截取文本 (`content_ctx`, stage 14 物化), 相比 full 轨聚焦于银行/金科实体周边的局部语境, 意在降低全文中无关段落对正面情感判定的干扰。行宇宙上, ctx 轨是 conditional-on-full 的测度轨——参与计数的文章必须先通过 full 轨的留篇门控 (`llm_verified_full == True`), ctx 轨本身不承担门控职责, 只在门控通过的子集内独立进行 ctx 文本上的正面判定并计数。⚠ 需澄清一个易误解之处: 本列的分母有效性判据(该篇「实质性」是否被成功测量)并非取自 ctx 轨自身的 `innovation_substantiveness_ctx`, 而是与 full 轨、ss 轨共用同一个恒由 `innovation_substantiveness_full` 给出的有效性掩码(`_pool_svd_substvalid_counts` 在 for track 循环外一次性算出, 循环内三轨复用); 真正逐轨读取 `innovation_substantiveness_ctx` 的判据用于另一族列(`_is_pos_symb{track}_sc` 4-way 交叉列), 不进入本列。因此 `pos_substvalid_count_ctx` 与 `pos_substvalid_count_full` 之间的数值差异, 完全来自「该篇在 ctx 文本上是否被判正面情感」这一分子端的轨间差异, 而非实质性判定输入文本的轨间差异, 这是本列区别于其余稳健性检验族(如 `_is_pos_symb{track}_sc`)的关键口径。

ctx 轨对分子(正面情感判定)的收窄效应仍然真实: 实体窗口截取会丢弃全文中距离目标实体较远的段落, 使正面情感判定所依赖的语言证据更集中、更少受无关话题(如银行日常公告、非金科相关业务报道)的稀释, 因而 `llm_vote_pos_ctx` 与 `llm_vote_pos_full` 在同一篇文章上可能出现不一致, 这正是三轨在分子端互为稳健性检验而非互相替代的设计初衷: 若某银行的洗稿率(`washing_ratio_ctx`)在 ctx 窄窗口下依然显著高于 full 轨, 则该结果对文本噪声更具稳健性。若两轨计数高度一致, 说明该银行的正面情感信号不依赖全文冗余上下文即可稳定识别; 若出现系统性偏离, 则提示全文噪声或实体窗口截取方式对情感判定存在方向性影响, 值得在稳健性附录中单独报告, 而非直接取其一作为主结果。

## VAR: pos_substvalid_count_ss

【变体差分】
`pos_substvalid_count_ss` 是 ss 轨版本, 判定文本为标题+银行∧金科同句共现片段 (`content_ss`, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 是三轨中判定粒度最细、对「银行与金科词是否在同一句话中被提及」最敏感的一支。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 回退为全文 body(等同 `content_full`), 并置 `ss_is_fallback=True`, 该情形下的正面情感判定实质上退化为在全文文本上进行, 但计数分母(`n_articles` 意义上的分母)与 fallback 标记的处理逻辑与 ctx 轨完全对称, 共享同一套 `*_is_fallback` 全 True 优雅降级机制(当 `FINTECH_AC=None` 即金科词典不可用时触发)。行宇宙同样 conditional-on-full。需与 CORE 澄清的口径一致: 本列的分母有效性判据(实质性是否被成功测量)恒取 `innovation_substantiveness_full`, 与 full/ctx 两轨共用同一掩码, ss 轨并不独立提高该分母门槛; ss 轨对分子(正面情感判定)的收窄效应才是三轨差异的真实来源——非 fallback 状态下参与计数的有效文章子集受限于「是否存在银行∧金科同句共现」, 通常小于或等于 ctx 轨的实体窗口子集, `pos_substvalid_count_ss` 因而是三轨中对「正面情感在同一叙事单元内被捕捉」要求最严格的稳健性度量, 与 full/ctx 两轨各自 just-identified 并排, 不分主次, 严禁混入同一 over-identified Hansen J 检验。

在非 fallback 的严格同句状态下, ss 轨捕捉的是最紧凑的叙事证据——银行与金科词出现在同一句话, 且该句(连同 ±1 句窗口)本身需支撑正面情感判定, 这种紧凑性降低了「情感判定针对银行本身而报道其余部分其实描述的是另一实体」这类错配风险; 但由于实质性判定的输入文本恒为 full 轨全文(而非 ss 轨的同句片段), ss 轨样本相对 full/ctx 两轨的洗稿率差异, 应主要归因于 ss 轨情感判定口径本身对「同句证据是否支撑正面语气」更敏感, 而非实质性判定输入文本随 ss 轨收窄导致的分母效应, 这一区分是解读三轨洗稿率差异方向性时应避免的常见误读。fallback 状态下 ss 轨退化为等同 full 轨的判定, 此时 `pos_substvalid_count_ss` 与 `pos_substvalid_count_full` 在该子集上取值一致, 分析时应结合 `ss_is_fallback` 标记区分「真实同句证据」与「回退全文证据」两类样本, 避免将二者混为同质样本解读。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy Green" Banks: The Disconnect Between Environmental Disclosures and Lending Activities. Management Science. https://doi.org/10.1287/mnsc.2024.07420
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as Data. Journal of Economic Literature. https://doi.org/10.1257/jel.20181020
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly. https://doi.org/10.2307/2393295
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
Granados, C., Ayala, Y., & Ramos-Mejia, M. (2024). Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation. Technovation, 129, 102880. https://doi.org/10.1016/j.technovation.2023.102880
<!-- rendered-citations:end -->
</content>
</invoke>
