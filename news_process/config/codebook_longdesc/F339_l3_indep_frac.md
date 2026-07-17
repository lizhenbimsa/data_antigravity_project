---
family_id: F339
columns:
- indep_frac
unit: 比率/占比 (proportion, [0, 1])
formula: 'indep_frac = n_articles_indep / n_articles_llm_valid (bank-year 分组; 分子=full 轨 LLM 判为「自主研发」创新来源模式的文章数, 分母=full 轨 LLM 有效投票篇数; 分母为 0 或缺失时置 NaN)'
producer: pipeline\panel\encode.py (aggregate_panel, innovation_collab_mode 二分类块) ; pipeline\panel\codebook.py (元数据装配)
upstream:
- innovation_collab_mode_full (article 级, stage 21 LLM 三家投票产出)
- n_articles_llm_valid (article 级有效投票计数聚合)
citations:
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: 'Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms'
  venue: Strategic Management Journal
  vol: '27'
  issue: '2'
  pages_or_artno: 131-150
- doi: 10.1287/mnsc.2024.04608
  type: journal
  authors: He, Z., Jiang, S., Xu, D., & Yin, X.
  year: 2026
  title: 'Investing in lending technology: IT spending in banking'
  venue: Management Science
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: "10.1080/00036846.2026.2651341"
  type: "journal"
  authors: "Sun, J., Liu, M., & Huang, X."
  year: 2026
  title: "Technology adoption or independent innovation? Bank competition and SMEs’ incremental innovation strategies"
  venue: "Applied Economics"
  pages_or_artno: "1-16"
new_dois: []
---

## CORE

【构念与来源】
indep_frac 度量某银行在某年度全部金科相关报道中,被 LLM 三家投票判定为「自主研发」创新来源模式的文章占比,是 P5 (Chesbrough 开放式创新框架, provisional collab 论文) 创新来源维度 (locus of innovation source) 的核心构念之一,与其互补对偶列 collab_frac (外部协同占比) 共同构成 innovation_collab_mode 二分类的完整刻画。该分类的理论出发点是开放式创新 (open innovation) 文献对企业技术能力来源的经典二分: 一端是银行依靠自身研发团队、内部实验室或子公司独立推进金融科技能力建设 (自主研发, in-house/closed innovation), 另一端是通过与外部金科公司、科技厂商合作、战略投资、联合实验室等方式获取能力 (外部协同, open/collaborative innovation)。indep_frac 越高, 说明该银行的金科相关报道叙事中「自主研发」框架越占主导, 可用作银行技术自主性/内部化战略倾向的媒体侧代理测度, 在 P5 的 identification 中充当 treatment 侧刻画之一, 与 collab_frac 成对进入机制分析或异质性分组。
【方法学与计算】
分类判据来自 stage 21 情感 LLM 三家投票 (gpt54nano/gemini31/deepseekv4) 在 full 轨 (标题+正文, 留篇门控口径 2026-06-29 起严格限定 llm_verified_full == True 的文章集合) 上对每篇文章打出的 innovation_collab_mode_full 标签, 该标签是与情感极性并列的另一分类维度 (与 P3 substantiveness / P4 locus 维度平行, 详见 SSOT `encode.LLM_CLASS_SPEC` 三元映射, collab 维度目标面板列即 collab_frac、目标类别标签为「外部协同」、解析源列为 innovation_collab_mode)。该三元映射是文章级基名与面板级 metric 命名两个命名域之间唯一的互锁点, 不存在字符串变换可达的捷径, 修改需同步两侧。计算在 pipeline/panel/encode.py::aggregate_panel 中按 (target_bank, year) 分组聚合: 先统计 n_articles_indep (被判「自主研发」的篇数, 缺失填 0 并转 int), 再除以该 bank-year 的 n_articles_llm_valid (LLM 有效投票篇数, 而非物理篇数 n_articles) —— 这一分母选择是 metric-audit 2026-06-02 修复的关键点: 早期实现误用含 NA 行的物理篇数作分母, 导致占比系统性偏低; 现行口径保证分子分母同定义域 (均限定在 LLM 成功打出 collab_mode 标签的文章内), 数学上确保 indep_frac、collab_frac 各自落在 [0, 1] 区间, 且二者之和 ≤ 1 (差额为 LLM 对 collab_mode 维度打标失败但整体有效投票的文章, 由恒等式校验 `_check_partition_identity` 以 `n_articles_llm_valid >= n_articles_indep + n_articles_collab` 的弱不等式形式持续监控, 而非早期脆弱的严格等式, 因为 LLM 可能在情感投票有效但 collab_mode 维度判定失败)。该列本身只在 full 轨物化 (无后缀); 家族内另存在 ctx/ss 对角线稳健臂 (indep_frac_cm / indep_frac_cm_ss, 命名规则源自 substantiveness/locus 维度共用的 `_lc`/`_sc`/`_cm` 对角后缀模式), 分别使用 innovation_collab_mode_ctx / innovation_collab_mode_ss 标签配上各自轨道独立的有效投票分母 n_articles_llm_valid_ctx / n_articles_llm_valid_ss, 修正了早期 ctx 分子配 full 分母导致占比越界至 3.0 的轨道不对称除法缺陷。full/ctx/ss 三轨在识别策略上各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified 的 Hansen J 检验; ss 轨遵循「回退语义镜像 ctx」的家族口径 —— 若某文章无银行∧金科同句共现, 其 content_ss 退化为全文 body 并标记 ss_is_fallback=True, 与 ctx 共享同一套回退机制哲学但轨道文本窗口不同 (ctx=实体窗口, ss=严格同句 ±N)。留篇门控 (2026-06-29 起) 明确规定「一篇文章是否计入某银行某年的金科报道」只看 full 轨 llm_verified_full, ctx/ss 是 conditional-on-full 的行宇宙子集测度, 因此 indep_frac 系无后缀主轨、承担 canonical 角色, ctx/ss 对角变体为稳健性复算而非替代测量。
【文献定位】
创新来源二分类的理论根基是开放式创新范式 (Chesbrough 2003) 对企业技术能力自主研发 vs 外部协同获取的经典划分, 本列将该理论构念操作化为媒体报道文本层面的 LLM 分类占比, 是文本挖掘/媒体分析方法在公司创新战略测度上的应用延伸。Laursen & Salter (2006, Strategic Management Journal) 在制造业企业样本中系统刻画了「外部搜索广度」(external search breadth) 对创新绩效的影响, 是本列「自主研发 vs 外部协同」二分构念的直接方法学源头之一, 其对开放度 (openness) 的操作化逻辑与 indep_frac/collab_frac 的对偶设计一脉相承 —— 该研究把企业的创新搜索策略划分为依赖内部资源的封闭式与广泛借助外部信息源的开放式两端, indep_frac 的「自主研发」一端在概念谱系上正对应其封闭式一端, 而 collab_frac 对应其开放式一端。作为银行业技术投资侧的实证参照, He, Jiang, Xu & Yin (2026, Management Science) 关于银行信贷技术 IT 投入的研究将银行技术支出拆分为通信类与软件类两个层面, 并证明金科行业竞争会诱发银行加码软件类 IT 投入, 为 indep_frac 所刻画的「自主研发」媒体叙事提供了银行实际技术投资行为层面的互证 —— 即媒体报道中「自主研发」框架的相对权重, 在方向上应与银行自身软件类 IT 资本开支的扩张存在协同变动, 这为 indep_frac 的外部效度提供了来自银行真实技术投入数据的间接检验思路, 也提示后续研究可将 indep_frac 与银行财务报表中的 IT 资本化支出/研发费用化科目做交叉验证。Zhang, Ma, Liang & Garrett (2024, Journal of Product Innovation Management) 对近二十年开放式创新研究做的框架性元分析进一步系统梳理了开放式创新的前因与后果, 印证「自主研发/外部协同」二分在管理学文献中已积累充分实证证据支撑, 为 indep_frac 与 collab_frac 的对偶操作化提供了跨大样本研究的元层级效度背书。本列引文以此三篇为限, 未强行借用 citations_pool.md 白名单内与本构念主题不符的独立董事治理文献, 以避免 claim-fit 失真。 就上句所称的引文范围而言, 银行情境下针对同一二分构念的直接检验近期已可增补一篇 claim-fit 契合者: Sun、Liu 与 Huang (2026) 把企业创新策略明确二分为「技术引进/采纳」与「自主创新」两种互斥模式, 并检验银行竞争如何在二者之间推动切换, 为 indep_frac 判定创新来源是否属「自主研发」的二分类构念提供了直接的构念出处与银行情境关联。迁移边界须诚实标明: 该文的自主创新 vs 技术引进由企业专利与研发投入等结构化指标判定, 而 indep_frac 是 full 轨文本经 LLM 判定创新来源模式后除以同轨 LLM 有效投票篇数所得的报道占比, 属媒体叙事层的份额而非企业实际创新行为; 且其研究主体为中小企业 (SME)、银行处于解释变量侧, 与本列以银行自身为主体的设定恰相反, 故该文只锚构念层面而不锚测度层面。该增补仍以 claim-fit 为准绳, 与上句「不强行借用主题不符文献」的原则一致。
## VAR: indep_frac

【变体差分】
本列是 F339 家族唯一列, 亦是该家族的 canonical 无后缀主轨表示: 轨道=full (标题+正文, 受 2026-06-29 留篇门控约束, 行宇宙=llm_verified_full==True 的文章子集); 分类判据来源=innovation_collab_mode_full (LLM 三家投票在情感极性之外并列输出的创新来源分类标签, 与 collab_frac 共用同一分类体系互为二分互补); 分母口径=n_articles_llm_valid (LLM 有效投票篇数, 而非物理覆盖篇数 n_articles), 这一分母选择是本列与其余分类组成型比率 tech_frac/app_frac/sub_frac/symb_frac/collab_frac 共享的家族级铁律, 保证分子分母同定义域。本列不携带轨道后缀、不携带模型后缀、不携带阈值或权重梯子后缀, 是家族内识别策略最简的 baseline 测度; 其 ctx/ss 对角稳健臂 (indep_frac_cm、indep_frac_cm_ss) 归属于本源码块相邻但命名不同的输出列, 不在本列的物化范围内, 二者与本列共同构成「同一构念、三条各自 just-identified 并排」的稳健性阶梯, 但本列作为无后缀主轨是三者中承担 canonical 角色、供下游 P5 分析与相关论文模板默认消费的那一支。零 LLM 有效投票 (n_articles_llm_valid=0) 的 bank-year 置 NaN 而非 0, 避免把「无法分类」与「分类为零占比」的语义混淆, 下游回归须显式处理该缺失模式 (通常随 min-n 门槛一并施加, 与 tone_gap_indep_collab 等衍生列共用的 min-n≥5 单元格质量守门是相邻但独立的过滤逻辑, 不直接作用于 indep_frac 本身)。

<!-- rendered-citations:begin -->
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
He, Z., Jiang, S., Xu, D., & Yin, X. (2026). Investing in lending technology: IT spending in banking. Management Science. https://doi.org/10.1287/mnsc.2024.04608
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Sun, J., Liu, M., & Huang, X. (2026). Technology adoption or independent innovation? Bank competition and SMEs’ incremental innovation strategies. Applied Economics, 1-16. https://doi.org/10.1080/00036846.2026.2651341
<!-- rendered-citations:end -->
