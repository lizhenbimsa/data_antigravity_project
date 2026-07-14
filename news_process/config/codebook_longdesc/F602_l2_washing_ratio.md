---
family_id: F602
columns:
- washing_ratio
- washing_ratio_ctx
- washing_ratio_ss
unit: 比率 (proportion, [0,1]; 分子分母同域计数比, 非百分比)
formula: 'washing_ratio{track} = pos_symb_count{track} / pos_substvalid_count{track} (分母缺失时回退 pos_count{track} 并告警); track ∈ {full(无后缀), ctx, ss}'
producer: "pipeline/panel/runner.py (方法 A: LLM 投票极化条件洗稿率, 三轨循环); pipeline/panel/export.py (Stata 标签写入)"
upstream:
- pos_count{track}
- pos_symb_count{track}
- pos_substvalid_count{track}
citations:
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
  vol: '80'
  issue: '2'
  pages_or_artno: 699-754
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: Ownership concentration and corporate greenwashing in China's capital markets - Based on a multi-actors perspective
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: '102600'
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: Political bias in corporate news - The role of conglomeration reform in China
  venue: The Journal of Law and Economics
  vol: '60'
  issue: '1'
  pages_or_artno: 173-207
new_dois: []
---

## CORE

【构念与来源】
washing_ratio 家族测度报道层面「洗稿」倾向, 即媒体在描述银行与金融科技相关联的新闻时, 有多大比例的正面报道属于象征性 (symbolic) 表态而非实质性 (substantive) 内容支撑。该家族的理论出发点是 Weick & Zajac (1998, Academy of Management Journal) 提出的象征性管理 (symbolic management) 与实质性行动 (substantive action) 二分: 当一篇报道被判定为对银行持正面情感 (pos), 但同时又被 LLM 分类为象征性 (symb, 即缺乏可验证事实、数据或行动细节的空泛表态) 而非实质性 (sub), 则该篇构成一次「正面且象征性」的观测, 本项目称之为「洗稿」(washing), 借用与公司金融文献中 "greenwashing"(漂绿) 测度同构的言语姿态 vs 可验证行动二分逻辑, 但不特指某一篇具体文献首创该词。washing_ratio 就是这种「正面且象征性」计数占「正面且实质性分类已测量」计数的比例, 数值越高说明该银行—年度的正面报道中越多是缺乏实质内容支撑的空洞表态, 存在被误读为真实业务改善信号的风险。这与公司金融文献中 "greenwashing"(漂绿) 测度的逻辑同构: 二者都试图从文本中区分「言语姿态」与「可验证行动」, 区别仅在于本家族的判据来源是本项目 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 投票产生的情感与实质性双重分类, 而非 ESG 报告关键词计数。

【方法学与计算】
washing_ratio 由 `pipeline\panel\runner.py` 在面板聚合阶段 (方法 A: LLM 投票极化条件法) 计算, 分子 `pos_symb_count{track}` = 该银行—年度内被 LLM 投票判定为正面情感 (pos) 且同时判定为象征性 (symb, W&Z 1998 分类) 的文章篇数; 分母 `pos_substvalid_count{track}` = 该银行—年度内正面情感 (pos) 且实质性分类结果已成功测量 (即 LLM 未因解析失败或缺标而缺席) 的文章篇数。这一分母口径是 2026-06-11 (fix omni-g-runner-10/g-runner-14) 的一次修正: 分子隐式要求 innovation_substantiveness 字段已被测量 (缺测 NaN 经 astype(str) 转字符串后恒为 'nan', 布尔判定恒 False, 天然被分子排除), 但旧版分母却用全部正面文章的物理计数 (即包含实质性分类失败的文章), 导致分子分母不同域 — 当某年 LLM 实质性分类失败率系统性上升时, washing_ratio 会被机械低估 (分母虚高)。修正后分母改用 `pos_substvalid_count{track}` (正面且实质性已测量), 与分子严格同域; 若面板中缺失该同域计数列 (旧 schema), 则回退到物理计数分母 `pos_count{track}` 并写日志告警, 以保持向后兼容但明确标注口径降级。除以零或双侧 NaN 由内部 `_safe_ratio` 工具函数 (numpy.divide + mask) 统一处理为 NaN, 不做隐式补零。

【文献定位】
本家族测度的分子分母双计数结构直接呼应 Weick & Zajac (1998) 对企业「象征性 vs 实质性」行为的经典区分, 并将其应用到银行—金融科技报道的文本分类场景。在方法学上, 本家族与 Gorovaia & Makrominas (2024, *European Financial Management*) 用自然语言处理从企业社会责任报告中识别漂绿的思路高度平行 — 二者都不满足于单纯的情感极性打分, 而是引入第二维度的分类 (该文用 ESG 关键词覆盖度, 本家族用 LLM 实质性判定) 来甄别正面表达背后是否有可验证的行动支撑。Duchin, Gao, & Xu (2025, *The Journal of Finance*) 用资产交易市场证据检验可持续性投资是否为漂绿提供了外部效度校验的范式参照: 该文强调仅凭披露文本本身无法区分真实可持续行为与漂绿, 须结合资产市场的独立信号交叉验证, 这一逻辑提醒本家族的 washing_ratio 应作为报道层面的文本信号, 与银行真实经营行为指标 (如金融科技投资、专利产出) 联合解读, 而非单独作为「洗稿」的充分证据。Fan et al. (2025, *Pacific-Basin Finance Journal*) 与 Song et al. (2026, *Finance Research Letters*) 分别从股权集中度驱动与 AI 相关披露策略角度提供了漂绿测度在中国资本市场与新兴技术叙事场景下的最新应用, 佐证「象征性表态占比」这一构念族在文本驱动金融研究中持续活跃。Piotroski, Wong, & Zhang (2017, *The Journal of Law and Economics*) 关于中国企业新闻中政治性偏向的发现, 提示本家族在解读时应留意中国语境下媒体报道存在系统性正面偏向的制度背景, 这也是象征性正面报道占比可能偏高的结构性原因之一, 而非纯粹企业主动误导。

家族内的三轨 (full/ctx/ss) 结构遵循项目统一口径: full 轨基于标题+全文正面/象征性/实质性判定, ctx 轨基于标题+银行—金融科技实体窗口判定, ss 轨基于标题+银行∧金融科技同句 (±N 窗口, 默认 1) 判定; 三轨分子分母均严格逐轨配对 (不跨轨借用), 各自 just-identified 并排、互为稳健性、不分主次, 禁止将三轨系数混入同一 over-identified Hansen J 检验。留篇门控口径遵循 2026-06-29 起 full-only 铁律, 即一篇报道是否计入「银行—金融科技」文章总体只看 `llm_verified_full`; ctx/ss 轨的洗稿率分子分母行宇宙是 full 留篇集的子集 (conditional-on-full), 而非独立留篇标准。ss 轨若某篇文章不存在银行∧金融科技同句共现, 则该篇的 content_ss 回退为全文 (`ss_is_fallback=True`, 镜像 ctx 的回退语义), 分子分母计数按回退后的实际分类结果计入, 共享 n_articles 分母口径, 不做单独剔除。

## VAR: washing_ratio

【变体差分】
washing_ratio (无后缀) 是家族的 full 轨 canonical 变体, 分子 `pos_symb_count_full` 与分母 `pos_substvalid_count_full` 均基于标题+全文文本进行的正面情感/象征性/实质性三重 LLM 分类。该文本窗口最宽, 覆盖报道全文语境, 因此其洗稿率测度对报道中任何位置出现的象征性表态 (例如开篇泛泛赞誉但正文并无具体业务细节支撑) 都保持敏感, 是本家族在面板 (dta) 中作为主指标呈现的口径 (Stata 标签 "Washing Ratio: LLM Vote (Full)")。与 washing_ratio_ctx / washing_ratio_ss 相比, 该列不依赖实体窗口或同句共现的裁剪规则, 分类判据覆盖信息量最大, 但也因此更容易受到全文中与银行—金融科技核心议题无关的段落 (如企业其他业务介绍、免责声明等套话) 的干扰, 使象征性判定的边界相对宽松。按项目铁律, 该列与 ctx/ss 两个变体各自 just-identified、互为稳健性并排, 三者共同报告以证明洗稿率的结论不依赖于某一特定文本窗口选择, 禁止把三轨系数一并塞入单个 over-identified 检验。分母口径同家族其余两轨一致, 均为 `pos_substvalid_count_full` (缺失时回退 `pos_count_full` 并告警), 与分子的实质性测量状态同域, 避免因 LLM 实质性分类失败率波动而系统性压低或抬高比率。在面板导出的 Stata 变量标签体系中, 该列与 washing_ratio_dict (词典 6 部平均口径)、washing_ratio_bert (BERT 3 模型平均口径)、washing_ratio_hc (高置信度子样本口径) 同属洗稿率大家族但分属不同判据来源, 彼此互为方法学稳健性参照, 不应等同视之或直接相加。

## VAR: washing_ratio_ctx

【变体差分】
washing_ratio_ctx 是家族的 ctx (context) 轨变体, 分子 `pos_symb_count_ctx` 与分母 `pos_substvalid_count_ctx` 基于标题+银行—金融科技实体窗口文本 (`content_ctx`, stage 14 物化) 而非全文进行 LLM 三重分类。相较于 washing_ratio 无后缀 (full) 轨, ctx 轨将判据文本收窄到实体共现附近的局部窗口, 目的是过滤掉与银行—金融科技核心议题无直接关系的段落干扰, 从而让「象征性 vs 实质性」的判定更聚焦于报道中真正涉及该银行与金融科技关联的表述本身。这意味着 ctx 轨的洗稿率对报道整体基调不敏感, 只关心实体窗口局部是否存在缺乏具体细节支撑的空泛正面表态; 当一篇报道整体基调正面但银行—金融科技相关段落本身空洞时, ctx 轨更可能捕捉到「洗稿」信号, 而 full 轨可能因全文其他部分的实质性内容而拉低该篇被判为象征性的概率。按 2026-06-29 起的 full-only 留篇门控铁律, ctx 轨的行宇宙 (哪些文章计入分子分母的候选池) 由 full 轨的留篇结果 (`llm_verified_full`) 决定, ctx 轨自身分类结果只决定象征性/实质性/正面与否这一维度, 不独立扩大或收窄留篇集合, 即该列是 conditional-on-full 的测度轨而非独立门控轨。分母同样采用 `pos_substvalid_count_ctx` 同域计数, 缺失时回退 `pos_count_ctx` 并告警, 与 full/ss 两轨口径对称。作为互为稳健性的并排变体, ctx 轨与 full/ss 轨不应被混入同一 over-identified 回归设定, 三者各自独立汇报以支持洗稿率结论对文本窗口选择的稳健性论证。

## VAR: washing_ratio_ss

【变体差分】
washing_ratio_ss 是家族的 ss (same-sentence) 轨变体, 分子 `pos_symb_count_ss` 与分母 `pos_substvalid_count_ss` 基于标题+银行∧金融科技同句共现窗口文本 (`content_ss`, ±N 句半径, 默认 1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 进行 LLM 三重分类, 是三轨中判据文本范围最窄、语境最紧邻的一支。相较 ctx 轨的实体窗口 (可能跨越较宽段落), ss 轨要求银行与金融科技词汇出现在同一句或相邻窗口内才纳入该轨的正式判据文本, 因此其洗稿率测度对「银行与金融科技被直接并列提及」这一更严格共现条件下的象征性表态最为敏感, 是三轨中语境裁剪力度最强的稳健性检验。当某篇文章不存在银行∧金融科技同句共现时, `content_ss` 回退为全文 body (`ss_is_fallback=True`), 此时该篇在 ss 轨下的分类结果实质上等同于 full 轨的分类输入, 但仍计入 ss 轨的分子分母 (共享 n_articles 分母口径, 不做单独剔除), 这一回退语义严格镜像 ctx 轨的回退处理, 确保 ss 轨在无同句共现时不会因数据缺失而人为制造空洞。留篇门控同样遵循 full-only 铁律, ss 轨的行宇宙是 full 轨留篇集的子集, 该列本身不参与是否留篇的判定, 只提供该轨口径下的洗稿率数值。分母同样为 `pos_substvalid_count_ss`, 缺失时回退 `pos_count_ss` 并告警, 与 full/ctx 两轨对称。三轨 (washing_ratio / washing_ratio_ctx / washing_ratio_ss) 各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验, 亦不与本项目其他三轨族 (如判据敏感性、co-primary 双轨嵌入) 交叉混用。

<!-- rendered-citations:begin -->
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets - Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news - The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
<!-- rendered-citations:end -->
