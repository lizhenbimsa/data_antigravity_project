---
family_id: F548
columns:
- symb_frac
- symb_frac_sc
- symb_frac_ss
unit: 比率 (proportion, [0, 1] ∪ NaN)
formula: 'symb_frac = n_articles_symb / n_articles_llm_valid (分母=0 → NaN); symb_frac_sc
  = n_articles_symb_sc_ctx / n_articles_llm_valid_ctx; symb_frac_ss = n_articles_symb_ss_ss
  / n_articles_llm_valid_ss'
producer: pipeline\panel\encode.py::aggregate_panel (Bank-Year 聚合); pipeline\panel\codebook.py::_FRAC_SPECS
  (元数据注册); pipeline\panel\runner.py (总装调度)
upstream: []
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and symbolism in CEOs' long-term incentive plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367–390
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: The symbolic management of stockholders. Corporate governance reforms and
    shareholder reactions
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127–153
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate
    emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1287/stsc.2023.0188
  type: journal
  authors: Westphal, J. D.
  year: 2023
  title: 'Systemic symbolic management, corporate social responsibility, and corporate
    purpose: A cautionary tale'
  venue: Strategy Science
  vol: '8'
  issue: '2'
  pages_or_artno: 221–232
- doi: 10.48550/arXiv.2510.01222
  type: arxiv
  authors: Hassani, B. K., Bahini, Y., & Mushtaq, R.
  year: 2025
  title: 'Discourse vs emissions: Analysis of corporate narratives, symbolic practices,
    and mimicry through LLMs'
  venue: arXiv
- doi: "10.1016/j.jsis.2026.101971"
  type: "journal"
  authors: "Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E."
  year: 2026
  title: "Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?"
  venue: "The Journal of Strategic Information Systems"
  vol: "35"
  issue: "2"
  pages_or_artno: "101971"
- doi: "10.1108/ara-01-2025-0031"
  type: "journal"
  authors: "Guan, J., & Zhuang, X."
  year: 2025
  title: "Do digital words reflect real innovation? Evidence from post-M&A earnings conference"
  venue: "Asian Review of Accounting"
  pages_or_artno: "1-44"
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
symb_frac 家族测度的是 Bank-Year 层面「象征性创新报道」在该银行当年全部有效金融科技相关报道中的占比, 是 LLM 三家投票 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 对每篇文章做出的 `innovation_substantiveness` 二分类标签 (「实质性」vs「象征性」) 在银行-年聚合层的比例展开。构念源头是组织理论中的「实质-象征脱耦」(substantive-symbolic decoupling) 传统: Westphal & Zajac (1994, ASQ) 首次系统区分企业治理/激励安排中「真正改变行为」的实质性举措与「仅为外部合法性表演」的象征性举措, 其 1998 年后续研究 (Westphal & Zajac, 1998, ASQ) 进一步表明市场对两者的反应存在系统差异。本仓库把这一区分从公司治理搬到银行金融科技报道语境: 一篇报道若描述银行已投入具体资源、上线系统、达成可验证的技术/业务成果 (如落地某项区块链结算系统、完成某笔金融科技并购交易), 判为「实质性」; 若报道停留在战略宣示、愿景表态、口号式跟风 (如仅表态"高度重视金融科技转型"而无具体动作), 判为「象征性」。symb_frac 即为「象征性」一端在分母中的份额, 与其互补的 sub_frac (实质性占比) 构成同一分类维度的两端, 二者之和理论上等于 1 (由 encode.py 的 `_check_partition_identity` 恒等式校验强制); 该恒等式校验与本家族共享同一上游 `innovation_substantiveness` 标签列, 但 sub_frac/symb_frac 各自单列成家族 (本家族仅覆盖 symb 侧)。
象征性报道占比的经济含义是"言行不一致"或"漂绿式"金融科技叙事强度的代理: 一家银行若在样本期内象征性报道份额显著偏高, 意味着其对外传播中金融科技话语与可验证的实质行动之间可能存在系统性落差, 呼应组织理论对"系统性象征管理"(systemic symbolic management) 的延伸讨论 (Westphal, 2023, Strategy Science 提出企业社会责任与公司宗旨表态本身也可能沦为脱离实质行为的象征性工具) 以及近期基于大语言模型对企业叙事中"象征性实践与模仿"(symbolic practices and mimicry) 的自动识别证据 (Hassani, Bahini & Mushtaq, 2025)。金融科技披露的"廉价谈话"(cheap talk) 特征也在气候披露文献中有平行证据 (Bingler, Kraus, Leippold & Webersinke, 2024, Journal of Banking & Finance)。

【方法学与计算】
symb_frac 家族的计算链条起于 stage 21 (`tone_llms`) 三家 LLM 对每篇留篇文章做出的多维分类标注, 其中包含 `innovation_substantiveness` 维度 (取值「实质性」/「象征性」), 与情感极性 (`llm_vote_score`) 是并列但独立的分类维度。stage 40 (`panel/encode.py::aggregate_panel`) 在银行-年分组内, 按全文 (full) 轨源列 `innovation_substantiveness_full == '象征性'` 过滤子集 (ctx/ss 轨则分别切换到 `innovation_substantiveness_ctx`/`innovation_substantiveness_ss` 源列, 与三轨文本命名后缀完全对齐, 而非共用一个不分轨的 `innovation_substantiveness` 列), 用 `groupby(['target_bank', 'year']).agg(n_articles_symb=('llm_vote_score_full', 'count'))` 得到该 cell 内象征性报道篇数, 再除以同一 cell 的 `n_articles_llm_valid` (LLM 有效投票总篇数, 即该 Bank-Year 全部三家 LLM 均给出有效判定的文章数) 得到占比; 分母为 0 (该 Bank-Year 无有效 LLM 判定文章) 时置 NaN 而非 0, 避免"未报道"与"报道但均非象征性"两种状态被混同。
本家族三列对应「留篇门控 = full-only」铁律下的三种轨道/子集口径, 三者各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定: `symb_frac` 是 canonical 全文 (full) 轨, 分子分母均取自全文文本上的 LLM 判定, 分母为 `n_articles_llm_valid`; `symb_frac_sc` 是标题+实体窗口 (ctx) 轨的分类对角线, 分子分母均切换为 ctx 轨独立标注结果 (`n_articles_symb_sc_ctx` / `n_articles_llm_valid_ctx`), 而非用 ctx 分子除以 full 分母 (2026-06-02 的 metric-audit 修正了此前轨道不对称导致占比可能大于 1 的问题); `symb_frac_ss` 同理是银行∧金科同句共现 (ss) 轨的分类对角线, 分子分母均取自 ss 轨独立标注 (`n_articles_symb_ss_ss` / `n_articles_llm_valid_ss`)。ss 轨遵循镜像 ctx 的回退语义: 若某篇文章没有银行与金科词的同句共现, 其 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 但该文章仍参与 ss 轨的 LLM 判定与 `n_articles_llm_valid_ss` 分母计数, 三轨的行宇宙口径均以 stage 21 `llm_verified_full == True` 的留篇集合为上界 (full-only 门控, 2026-06-29 起 ctx/ss 降级为 conditional-on-full 的测度/稳健性轨)。
分类恒等式方面, `_check_partition_identity` 会校验 `n_articles_sub + n_articles_symb == n_articles_llm_valid` (以及 ctx/ss 轨各自对角线的对应恒等式), 确保「实质性/象征性」二分类穷尽且互斥, 这是 symb_frac 数值可解释为"占比"而非任意计数比的前提。与 symb_frac 同源但不同构念的 `tone_gap_sub_symb` (及其 ctx/ss 镜像变体) 是取「实质性」子集与「象征性」子集各自的平均语调 (`llm_vote_tone`) 之差, 度量"言行两端情感纯度差距", 施加 min-n≥5 的 cell 最小样本量守门 (避免单篇驱动伪差距); symb_frac 本身不受此守门约束, 只要分母大于 0 即出值。

【文献定位】
symb_frac 家族的构念锚点是组织理论中实质-象征脱耦的经典范式 (Westphal & Zajac, 1994, ASQ; Westphal & Zajac, 1998, ASQ), 后者尤其确立了"象征性举措用于管理外部利益相关者印象而非实质改变治理结构"的核心命题, 本仓库将其运用到银行金融科技新闻叙事这一新的经验场域。在测度层面, 用 LLM 分类给文本打"实质 vs 象征"标签的做法呼应了近年文本分析文献对企业气候/ESG披露"廉价谈话"成分的系统识别 (Bingler et al., 2024, Journal of Banking & Finance), 组织理论后续文献亦将"系统性象征管理"的分析框架扩展到企业社会责任与公司宗旨表态领域, 警示此类对外表态本身也可能沦为脱离实质行为的象征性工具 (Westphal, 2023, Strategy Science), 而基于大语言模型对企业文本叙事中象征性实践与制度性模仿的自动化识别, 是本家族方法学思路 (用 LLM 对报道文本做"实质/象征"二分类) 在近期文献中的平行印证 (Hassani, Bahini & Mushtaq, 2025)。三轨设计 (full/ctx/ss) 与本仓库全线情感/分类测度共享同一"文本窗口敏感性"稳健性哲学: 全文轨捕获整篇报道语境, ctx 轨聚焦实体邻近窗口降低无关段落噪声, ss 轨要求银行与金融科技词汇同句共现以最严格化归因; 三者互为稳健性并排比较, 而非彼此嵌套或互相替代。 近年文献进一步把这一二分从组织理论的构念推进为可被实证证伪的经验命题, 并在数字化/金融科技议题与中国语境下反复检验, 构成本家族最贴近的同域参照。Chen、Hajiheydari、Zhang 与 Lin (2026) 基于注意力基础观构造企业数字化转型关注度, 以中国上市公司 2007–2020 年样本在「战略实质承诺 vs 象征性信号」两个对立解释之间做检验, 发现该关注度与突破式创新相关而与渐进式创新及研发支出无关, 从而支持实质承诺说、未支持象征性信号说, 且数字话语与创新的一致性在高问责情境下最强; 该文对本家族的价值在于确立该二分是当代数字话语研究的主流理论框架, 并证明「话语是否只是象征」是可被实证证伪的经验问题, 因而同时充当构念锚点与反面参照 —— 不可据此宣称原文为象征性解释提供了支持。其象征性判定基于「话语关注度 vs 实际创新产出」的推断性对比, 与本家族由 LLM 对单篇报道直接给出实质/象征分类标签的判定机制不同; 原文文本源为公司自述披露、分析层级为公司-年, 而本家族为第三方新闻报道且分 full/ctx/ss 三轨。Guan 与 Zhuang (2025) 在中国并购语境下以并购后业绩说明会文本追问「数字化措辞是否对应真实创新」, 检验数字化词汇与后续创新产出的对应关系, 与 symb_frac 所刻画的「科技话语中象征性成分份额」高度同域; 但原文以「数字词汇量 vs 实际创新指标」间接推断象征性, 未提出象征性/实质性的逐篇标注方案, 文本源亦为管理层自述而非新闻报道, 分析单元为并购事件/公司-年。Huang 与 Ma (2024) 则把该二分直接落在金融科技议题上, 检验金融科技发展对企业实质性绿色创新与象征性绿色创新的差异化影响, 在中国情境中明确采用「实质性 vs 象征性」创新二分, 是与本家族在概念与中文表述上最直接对应的同域应用; 惟其实质/象征由专利类型 (发明 vs 实用新型/外观) 客观划分而非由文本判定, 研究主体为非金融上市公司且金融科技是解释变量, 而本家族中金融科技是被报道的议题本身、主体为商业银行, 原文亦未构造任何比率型 washing 指标。Granados、Ayala 与 Ramos-Mejia (2024) 从组织理论一侧补足了构念界定: 该文系统刻画技术创新语境下的「创新剧场」现象, 即象征性展演与实质性投入的分野, 为本家族的二分标签提供当代组织理论层面的机制阐述; 但原文为组织层面的构念化研究, 未提供文本自动分类算法, 非中国语境、非银行业、亦无面板计量, 本家族把该构念操作化为逐篇 LLM 标签并按银行-年计算份额, 操作化层级与数据类型均已超出原文所验证的范围。
## VAR: symb_frac

【变体差分】
symb_frac 是家族的 canonical 全文 (full) 轨口径: 分子 `n_articles_symb` 与分母 `n_articles_llm_valid` 均基于全文文本 (标题+正文) 上三家 LLM 的多数投票分类结果, 未做实体窗口截取或同句共现限定。它衡量的是"该银行当年全部有效判定报道中, 被 LLM 判定为象征性创新叙事的比例", 是三轨 (full/ctx/ss) 并排设计中互为稳健性、不分主次的一支, 也是留篇门控 (是否算作"一篇银行金科报道") 的口径来源 —— stage 21 的留篇判定只看 `llm_verified_full == True`, 因此 full 轨的分母 `n_articles_llm_valid` 天然构成 ctx/ss 两轨行宇宙的上界。分母为 0 (该 Bank-Year 没有任何全文 LLM 有效判定文章) 时置 NaN, 区别于象征性报道数为 0 的情形 (后者出值为 0.0)。与其互补的 `sub_frac` 共用同一分母且理论上二者相加为 1 (由 `_check_partition_identity` 强制校验), 但两者各自单列成不同家族, 互不合并计算。作为 canonical 口径, symb_frac 是三轨并排设计中样本量最大、覆盖最广的一支: 它不要求实体窗口截取, 也不要求银行与金融科技词汇同句共现, 因此在样本稀疏的银行-年 cell (如报道量本就不多的中小银行早期年份) 中仍能相对稳定地出值, 而 ctx/ss 两轨在同等稀疏条件下更容易因分母骤降或缺列而置 NaN。使用者在把 symb_frac 作为回归自变量或机制变量时, 应注意它反映的是"分类判定"层面的比例, 与同名情感语调列 (如 `llm_vote_tone`) 是并列但独立的构念: 一篇报道即便被判定为「象征性」创新叙事, 其情感极性仍可能是正面、负面或中性, 二者不构成同一维度的不同表达, 不应相互替代解读。

## VAR: symb_frac_sc

【变体差分】
symb_frac_sc 是标题+实体窗口 (ctx) 轨的分类对角线口径, 与 canonical `symb_frac` 的区别在于分子分母均切换到 ctx 轨: 分子为 `n_articles_symb_sc_ctx` (ctx 轨文本上 LLM 判定为「象征性」的篇数), 分母为 `n_articles_llm_valid_ctx` (ctx 轨 LLM 有效投票总篇数), 二者严格同轨配对 (2026-06-02 metric-audit 修正了此前"ctx 分子除以 full 分母"导致占比可能超过 1 的轨道不对称错误)。命名后缀 `_sc` 源自"substantive/symbolic × ctx"对角线编码惯例 (与 `tech_frac_lc`/`indep_frac_cm` 等其它分类维度的 ctx 对角线后缀并列, `_sc`≡subst-ctx), 与三轨文本命名后缀 `_ctx` 是同一构念在不同命名层的两种写法, 不应与政治词权重梯度或规则消融梯度的后缀混淆。ctx 轨的分类判定以标题+银行实体邻近窗口文本为输入, 相比全文轨降低了无关段落引入的分类噪声, 但也可能因窗口截断丢失关键的"实质性证据"描述段落, 是 full 轨的互为稳健性并排轨、非替代关系, 二者禁止混入同一 over-identified Hansen J 设定中联合估计。若上游缺失 `n_articles_llm_valid_ctx` 分母列, 本列整体置 NaN 并记录 warning, 优雅降级而非报错中断。ctx 轨的实体窗口截取原理呼应 Hassan, Hollander, van Lent & Tahoun (2019, QJE) 提出的"实体邻近"(entity-proximity) 文本处理思路, 即只保留目标实体附近的上下文而非整篇文档, 以缓解长文档中主题漂移带来的分类噪声; 在 symb_frac_sc 的语境下, 这意味着 LLM 只看到银行名附近的段落来判断该处叙事是"实质性"还是"象征性", 相比全文轨更聚焦但也更依赖窗口边界的选取是否恰当。与情感三轨的用法一致, symb_frac_sc 不应被理解为对 symb_frac 的"修正版"或"升级版", 二者是同一构念在不同文本处理策略下的平行估计, 使用者若要报告稳健性检验, 应将 full/ctx/ss 三轨结果并列呈现而非只报告其中一支。

## VAR: symb_frac_ss

【变体差分】
symb_frac_ss 是银行∧金科同句共现 (ss) 轨的分类对角线口径, 命名后缀 `_ss` 既标记三轨文本口径中的 ss 轨, 也承袭"象征性-ss"对角线编码 (镜像 ctx 轨 `_sc` 后缀的构造方式)。分子为 `n_articles_symb_ss_ss` (ss 轨文本上 LLM 判定为「象征性」的篇数), 分母为 `n_articles_llm_valid_ss` (ss 轨独立的 LLM 有效投票篇数, 与 ctx 轨分母并非共享同一分母, 而是各轨各自独立统计的成功率), 分子分母同轨严格配对。ss 轨要求银行名与金融科技词汇出现在同一句 (±0 句半径, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置默认值 1) 才纳入"真实共现", 否则该文章的 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 但仍照常参与 ss 轨的 LLM 分类判定与分母计数, 回退语义严格镜像 ctx 轨。ss 轨是三轨中判据最严格的一支, 理论上应比 full/ctx 更精确地捕捉"银行被直接置于金融科技语境中描述"的报道, 但也因严格共现要求而样本量更小、方差更大; 与 full、ctx 两轨同为互为稳健性、不分主次的并排口径, 三者禁止在同一 over-identified 设定中联合估计。若上游缺失 `n_articles_llm_valid_ss` 分母列, 本列整体置 NaN 并记录 warning。同句共现判据的方法学动机可类比 Gentzkow & Shapiro (2010, Econometrica) 在媒体偏向测度中对"共现窗口"精度与噪声的权衡讨论: 窗口越窄 (本例中窄至单句), 提取到的关联越可能真实反映文本作者意图将银行与金融科技并置讨论, 但同时符合条件的文章数会显著减少, 使 symb_frac_ss 在 T=2 开发样本这类小样本场景下更容易出现零方差或大量缺失。使用者在解读 symb_frac_ss 时应注意其"高精度、低覆盖"的取舍特征, 并将其与 full/ctx 两轨并排比较作为识别策略稳健性的一部分, 而非因样本量较小而弃用或单独赋予更高权重。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367–390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders. Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127–153. https://doi.org/10.2307/2393593
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Westphal, J. D. (2023). Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale. Strategy Science, 8(2), 221–232. https://doi.org/10.1287/stsc.2023.0188
Hassani, B. K., Bahini, Y., & Mushtaq, R. (2025). Discourse vs emissions: Analysis of corporate narratives, symbolic practices, and mimicry through LLMs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2510.01222
Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E. (2026). Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?. The Journal of Strategic Information Systems, 35(2), 101971. https://doi.org/10.1016/j.jsis.2026.101971
Guan, J., & Zhuang, X. (2025). Do digital words reflect real innovation? Evidence from post-M&A earnings conference. Asian Review of Accounting, 1-44. https://doi.org/10.1108/ara-01-2025-0031
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
Granados, C., Ayala, Y., & Ramos-Mejia, M. (2024). Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation. Technovation, 129, 102880. https://doi.org/10.1016/j.technovation.2023.102880
<!-- rendered-citations:end -->
