---
family_id: F194
columns:
- dict_pos_symb_count_ctx
- dict_pos_symb_count_full
- dict_pos_symb_count_ss
unit: 篇数/计数 (count)
formula: "dict_pos_symb_count{track} = Σ_{article ∈ bank-year} _is_dict_pos_symb{track}; _is_dict_pos_symb = 1 当且仅当该篇被词典均值判为正面 (_is_dict_positive=1) 且其正面情感被判为象征性 (symbolic, 非实质性 substantive)"
producer: news_process/pipeline/panel/encode.py::（K. 洗稿率聚合块）; 下游消费 news_process/pipeline/panel/runner.py::（方法 D 词典均值 washing_ratio_dict）
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (六词典均值极性 _is_dict_positive)
- 21_tone_llms.parquet (实质性/象征性判别信号)
citations:
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  issue: ""
  pages_or_artno: 102776
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
new_dois: []
---

## CORE

【构念与来源】
本家族 dict_pos_symb_count 计量的是「被词典法判为正面、且该正面情感属象征性 (symbolic) 而非实质性 (substantive)」的银行-年报道篇数。它是情感「洗稿率 (washing ratio)」测度体系里方法 D (词典均值臂) 的分子输入之一, 服务于把银行金融科技报道中的正面情绪拆解成「有实质内容支撑的正面」与「仅停留在措辞层面的象征性正面」两类, 从而刻画报道正面基调里究竟有多大比例是空泛表态。构念的直接思想来源是实质与象征之辩 (substance versus symbolism): 组织行为学与信息经济学长期观察到, 主体会以象征性言辞回应外部期待而不必伴随实质行动, 这一「便宜话 (cheap talk)」与「摘樱桃 (cherry-picking)」现象在企业气候披露的文本研究中被 Bingler 等 (2022) 系统刻画——他们发现披露文本中大量正面陈述缺乏可验证的具体承诺, 呈现出象征性堆砌特征。本项目把该思想迁移到银行金融科技报道语境: 一篇被词典判为正面的报道, 若其正面信号缺乏实质性事实/承诺锚定, 则计入 pos_symb; 洗稿率的分母并非笼统的总正面篇数, 而是词典判正且实质性已被测量的同域计数 dict_pos_substvalid_count (阳性∧实质有效), 象征性正面计数与该 substvalid 分母之比即为词典臂的洗稿率, 从而只在「正面且实质性可判定」的可比子域内度量象征化占比。

【方法学与计算】
计算分两层。文章层: 对每一篇进入银行-年宇宙的报道, 先由六词典均值 (config 词典族的逐词打分再取跨词典均值) 给出极性判别, 得到指示列 _is_dict_positive; 再由象征性/实质性判别信号确定该篇正面情绪是否属象征性, 得到 _is_dict_pos_symb (取值 0/1)。面板层: 在 encode.py 的洗稿率聚合块 (源码 K 段) 内, 对每条银行-年逐轨执行 agg[f'dict_pos_symb_count{track}'] = (f'_is_dict_pos_symb{track}', 'sum'), 即对该银行-年内所有留篇报道的象征性正面指示做求和, 得到本列的篇数计数。下游 runner.py 的方法 D (词典均值) 把本列作为分子, 以 dict_pos_substvalid_count (词典判正且实质有效的篇数) 经 _svd_denom 加固后为分母, 用 _safe_ratio 计出 washing_ratio_dict, 度量词典口径下正面报道的象征化比重。本列是计数而非比率, 单位为篇数, 因此天然随该银行-年留篇总量放缩, 使用时须结合同轨分母或篇数控制。词典法与另两条并行臂 (LLM 投票臂的 pos_symb_count、单模型 BERT 臂的 bert_pos_symb_count) 互为稳健性: 三法各自 just-identified 并排, 不分主次, 严禁把不同方法的洗稿率分子混进同一 over-identified Hansen J。这一并排原则与词典选择本身的稳健性同构——中文金融情感词典的构造与领域专用性对结果的敏感性由 Du 等 (2022) 论证, 提示单一词典的极性判别须以多词典均值降低特异性风险。

【文献定位】
方法学定位落在金融文本情感测量的三角框架内。词典法的规范性与陷阱由 Loughran 与 McDonald (2016) 的综述系统梳理, 强调通用情感词典迁移到金融文本时的误判风险与领域专用词典的必要性, 这为本家族坚持金融领域中文词典族、并以跨词典均值稳健化提供了方法依据。词典法与机器学习/大模型法孰优的争论上, Frankel、Jennings 与 Lee (2022) 在 Management Science 的研究直接比较了词典法与机器学习情感度量, 表明两类方法在不同情境下各有优势、宜互为印证而非彼此取代——这正是本项目在 dict/LLM/BERT 三臂并置洗稿率分子的直接支撑。BERT 类判别器一侧, Huang、Wang 与 Yang (2023) 的 FinBERT 提供了与词典臂平行的深度学习正负极性来源, 使象征性正面计数得以在词典、LLM、BERT 三口径下交叉验证。实质与象征的拆解思想则以 Bingler 等 (2022) 对气候披露「便宜话」的刻画为构念母版。综合而言, 本家族既非纯情感强度指标、也非纯文本篇幅指标, 而是「正面情绪中象征化成分」这一构念的词典臂计数底料。

## VAR: dict_pos_symb_count_full

【变体差分】
本列是三轨中的 full 轨。full 轨文本口径 = 标题 prepend 到全文正文 (content_full), 即在 stage 14 ctx_materializer 把标题拼接到完整报道正文之首后, 供词典法逐词打分与象征性判别使用。留篇门控采 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技报道宇宙, 只看 llm_verified_full == True, 因此 full 轨的分母 (银行-年留篇集) 是三轨的母集, ctx/ss 轨的行宇宙均为 full 留篇集的条件子集。相应地, dict_pos_symb_count_full 在语义上最贴近「该银行-年全部留篇报道里, 词典判正且正面属象征性的篇数」这一无条件构念, 通常在三轨中取值规模最大、方差最充分, 是词典臂洗稿率分子的首要 (canonical) 轨。full 轨与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨的象征性正面计数混进同一 over-identified Hansen J。它作为分子直接喂入 runner.py 方法 D 的 washing_ratio_dict (无 track 后缀的主聚合口径实由 full 轨驱动)。需强调 full 轨并非天然优于其余两轨, 只是留篇门控与主聚合口径落在 full 上的历史命名产物: 三轨的语义差异全在文本口径 (全文 vs 实体窗 vs 同句窗), 词典打分规则、象征性判别逻辑、求和聚合方式三者完全一致, 因此三轨可视作对同一构念在不同文本粒度上的三次并行测量。使用本列做回归时, 应把 full 轨结果与 ctx、ss 轨结果并列报告为规格稳健性梯子, 而非仅取 full 一轨下结论; 当三轨系数方向一致且量级相近时, 象征化正面这一构念的识别才被视为稳健。本列作分子时, 其配对分母不是笼统的总正面篇数 dict_pos_count_full, 而是同轨的 dict_pos_substvalid_count_full (词典判正且实质性已被测量的篇数, 经 _svd_denom 加固): 两者之比刻画在「正面且实质性可判定」子域内报道的象征化占比结构, 单看本列的绝对篇数会与银行-年报道体量混淆, 须以该 substvalid 分母归一后再作跨行比较。

## VAR: dict_pos_symb_count_ctx

【变体差分】
本列是三轨中的 ctx 轨。ctx 轨文本口径 = 标题 prepend 加实体上下文窗口 (content_ctx), 即只保留标题与目标实体 (银行/金融科技词) 邻近的上下文片段, 而非全文正文。因此本列度量的是「在实体相关语境内, 词典判正且正面属象征性的篇数」, 相较 full 轨剔除了与银行金融科技主题无关的正面措辞, 使象征性正面的判别更聚焦于报道中真正涉及目标实体的段落。ctx 轨为条件-on-full 测度: 其行宇宙是 full 留篇集的子集, 是否留篇仍由 full 轨门控决定 (2026-06-29 full-only 口径), ctx 只在留篇集内按自身文本口径重算象征性正面计数。ctx 与 full、ss 三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁三轨混进同一 over-identified Hansen J。在开发期 T=2 小样本上, ctx/ss 轨可能出现较 full 轨更稀疏甚至退化为零方差的情况, 属预期的小样本退化, 生产期 T=18 语料上恢复正常信息量。相较 full 轨, ctx 轨的核心价值在于抑制「报道主体与银行金融科技无关、只是顺带出现正面措辞」这一噪声源: 全文口径下, 一篇泛泛报道里与目标实体无关的正面表态也会被词典计入, 而 ctx 轨通过只保留实体上下文窗, 把象征性正面的判别锚定在真正涉及银行与金融科技的语句上, 因而对「主题相关的象征化」更敏感、对「离题正面」更抗噪。使用者可把 full 与 ctx 两轨系数之差解读为「离题正面措辞」对洗稿率测度的贡献: 若二者高度一致, 说明象征化主要发生在主题相关段落; 若 ctx 轨更强, 则提示实体相关语境内的象征化程度被全文口径稀释。ctx 轨的实体窗判定采银行侧否定加短名过滤、金融科技侧裸 AC 词表的非对称口径, 与 ss 轨的严格同句共现是两个不同键, 不可互相复用。

## VAR: dict_pos_symb_count_ss

【变体差分】
本列是三轨中的 ss (same-sentence, 同句) 轨。ss 轨文本口径 = 标题 prepend 加「银行与金融科技词同句共现 ±N 句窗」片段 (content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨里语境最严的一轨——只有当银行与金融科技词落在同一 (或极近) 句子内时才纳入该片段。因此 dict_pos_symb_count_ss 度量的是「银行∧金融科技强共现语境下, 词典判正且正面属象征性的篇数」, 把象征性正面的计量收窄到银行与金融科技被同句并置的最相关文本上。ss 轨的回退语义镜像 ctx 轨: 当某篇不存在银行∧金融科技同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True; 若金融科技 AC 词表为 None 则 *_is_fallback 全 True 优雅降级。ss 同样是条件-on-full 测度, 行宇宙为 full 留篇集子集, 门控由 full 轨决定。ss 与 full、ctx 三轨互为稳健性、各自 just-identified 并排、不分主次, 严禁三轨混进同一 over-identified Hansen J; T=2 开发样本上 ss 轨可能高度稀疏, 属预期退化。ss 轨在三轨中语境最严, 其价值在于把象征化正面的度量收窄到「银行与金融科技被同一句话直接并置」这一最强共现证据上, 从而最大限度排除两实体各自出现于不同段落、仅在篇章层面松散关联的报道。这使 ss 轨对「银行确实在谈其金融科技动作」的正面表态最为专注, 相应地样本量最小、退化风险最高。与 ctx 轨的回退语义完全平行——同句共现缺失时降级为全文 body 并置 ss_is_fallback 标志——保证了不会因严格窗判据而静默清空样本, 而是以可追踪的回退方式优雅降级, 分母 n_articles 在回退篇上与 ctx 轨共享。实务上, ss 轨宜作为三轨梯子里最保守的一端: 当 full、ctx、ss 三轨的象征化正面计数经归一后仍给出一致结论时, 洗稿率测度对「共现语境严格程度」这一规格选择即被证明不敏感; 三轨间的系统性差异则本身构成关于象征化发生在何种文本粒度上的实证信息。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
<!-- rendered-citations:end -->
