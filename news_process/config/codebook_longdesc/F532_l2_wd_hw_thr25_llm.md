---
family_id: F532
columns:
- sum_wd_hw_thr25_llm_ctx
- sum_wd_hw_thr25_llm_full
- sum_wd_hw_thr25_llm_ss
unit: 无量纲权重和 (跟风衰减权重之银行-年加总, 值域 (0, n_articles{track}])
formula: 'sum_wd_hw_thr25_llm{track} = Σ_{article ∈ (bank,year)} herd_weight{track}_thr25 · 1[llm_vote_score{track} 非缺失]; 其中 herd_weight{track}_thr25 由 stage 24 (herd_decay_processor) 按 herd_detection.sensitivity_thresholds 网格中 tag=thr25 (相似度门槛 τ=0.25) 逐篇算出, 是与生产口径 τ=0.35 并排的阈值敏感性权重变体'
producer: pipeline\panel\runner.py (阈值敏感性 HW 加权列, 步骤 3d-2) ; pipeline\panel\encode.py (面板级聚合, F5b 段)
upstream:
- 24_herd_decay_processor (herd_weight{track}_thr25 篇章级列)
- 21_tone_llms (llm_vote_score{track})
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1016/j.frl.2024.105227"
  type: journal
  authors: "Kirtac, K., & Germano, G."
  year: 2024
  title: "Sentiment trading with large language models"
  venue: "Finance Research Letters"
  vol: "62"
  issue: ""
  pages_or_artno: "105227"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, F., Alizadeh, M., & Kubli, M."
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1093/restud/rdaf037"
  type: "journal"
  authors: "Kwon, S. Y., & Tang, J."
  year: 2026
  title: "Extreme Categories and Overreaction to News"
  venue: "Review of Economic Studies"
  vol: "93"
  issue: "2"
  pages_or_artno: "1137-1166"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 sum_wd_hw_thr25_llm_full / _ctx / _ss 度量的是"银行-年"层面, LLM 投票语调 (llm_vote_score) 在跟风衰减加权聚合中所用权重之和, 且该权重取自阈值敏感性网格里相似度门槛 τ=0.25 的变体 (标签 thr25), 与生产口径 τ=0.35 的 herd_weight{track} 并排、互为稳健性、不分主次。跟风衰减权重的构念根源是 Tetlock (2007) 对媒体情绪与股票收益关系的开创性度量框架中隐含的一个方法论问题: 同一时间窗内大量报道相互转载、改写或跟风同一论调时, 简单等权平均会让"抄稿多"的论调在面板中被系统性放大, 掩盖真实的独立信息含量。本项目的跟风检测 (herd_detection) 采用文本相似度阈值判定一篇报道是否与同期同银行报道高度雷同 (疑似抄稿/跟风) 的思路 — 用文本相似度阈值判定一篇报道是否与同期同银行报道高度雷同, 并据此给每篇文章赋一个 [0,1] 区间的衰减权重: 越像被大量转载的雷同论调, 权重越低; 越独特, 权重越接近 1; 这一相似度衰减设计与近年"用大语言模型直接从新闻文本提取交易信号"文献 (如 Kirtac & Germano, 2024, Finance Research Letters) 所强调的"重复报道会稀释信息含量、须在信号构造阶段加以控制"的方法论关切相呼应。sum_wd_hw_thr25_llm{track} 正是把这套逐篇权重, 按 (bank, year, track) 分组求和, 构成后续加权平均语调 (avg = 加权分子和 / 本列分母和) 的除数, 因此它本身不是一个"情感强度"指标, 而是一个纯粹的权重规模控制列, 属于面板构造的中间会计量, 但因其直接决定下游加权均值的稳健性, 被单独物化并纳入 codebook。

【方法学与计算】
计算发生在两处。第一处在 pipeline/panel/runner.py 步骤 3d-2: 对 herd_detection.sensitivity_thresholds 配置里的每个候选阈值标签 (_tag, 本列对应 tag="thr25", 即相似度判定门槛设为 0.25 而非生产用的 0.35), 逐轨 (full/ctx/ss) 取出 stage 24 已算好的篇章级 herd_weight{track}_thr25 列, 用 fillna(1.0) 补齐 (未参与跟风检测或无同期可比样本的文章视为权重 1, 即不打折), 再与该篇章 llm_vote_score{track} 是否非缺失做逐元素掩码 (`.where(df[f'llm_vote_score{track}'].notna())`), 得到中间列 `_wd_hw_thr25_llm{track}` — 只在该篇文章的 LLM 投票语调本身有效时才计入权重分母, 否则记为缺失, 保证分子分母在同一有效样本域上匹配 (encode-01 分子分母同域惯例)。第二处在 pipeline/panel/encode.py 的 F5b 聚合段: 按 (bank, year) 分组对 `_wd_hw_thr25_llm{track}` 求 sum, 写入 `sum_wd_hw_thr25_llm{track}`。该列与同批产出的 `llm_vote_score_hw_thr25_sum{track}` (加权分子和) 配对使用, 下游 Stata/Python 端可据此重构 avg_llm_vote_score_hw_thr25{track} = 分子和 / 本列, 得到阈值 τ=0.25 下的银行-年加权平均 LLM 语调。整套阈值敏感性网格刻意只覆盖 LLM 投票这一条主回归 DV 测度族 (score/cont), 而非对词典/BERT 等全部 11 个测度族都展开阈值网格, 因为后者会造成列数爆炸; 具体网格取值 (含 thr25) 由 herd_sensitivity_grid(CONFIG) 从 config/*.yaml 的 herd_detection.sensitivity_thresholds 读出, 缺失阈值标签或缺失源列时该列自动被 valid_agg 过滤跳过, 不会静默产生全零或全 NaN 的假列。

【文献定位】
本家族在方法论上处于两条文献线的交叉点。其一是媒体情绪度量的经典传统, 以 Tetlock (2007) 在 Journal of Finance 提出的"用文本情绪预测市场反应"框架为源头, 后续研究反复关注同题材报道相互转载导致的信息重复计数问题, 本项目用相似度阈值衰减权重直接回应这一关切, 方法论上呼应 Kirtac & Germano (2024, Finance Research Letters) 在用大语言模型从新闻文本抽取交易信号时对"重复报道稀释信息含量"这一现象的强调, 二者共同指向同一个测度设计问题: 简单等权汇总同题材报道会系统性放大转载/跟风论调, 须在权重构造阶段主动衰减。其二是近年兴起的"用大语言模型做金融文本情感标注"文献: llm_vote_score 本身是三家商用 LLM 多数投票的产物, 其可靠性论证依赖 Gilardi et al. (2023, PNAS) 关于 ChatGPT 类模型在文本标注任务上可比甚至优于众包工的实证发现, 以及 de Kok (2025, Management Science) 对会计与金融研究中生成式 LLM 文本分析规范流程 (温度=0、提示词冻结、结果缓存) 的方法论综述, 二者共同支撑了本项目 stage 21 三家 LLM 投票 + 缓存复现的设计。Du et al. (2022, Review of Finance) 提出的中文金融情感词典方法论, 则作为词典法与 LLM 法的对照参照系, 提示不同测度方法各有偏差来源, 而阈值敏感性网格 (thr25 与生产口径 thr35 并排) 正是回应"结论是否依赖单一超参数选择"这一稳健性关切的具体落地。 阈值取值的非中性尚有一条构念侧的旁证。Kwon 与 Tang (2026) 在诊断性预期 (基于代表性启发的信念形成模型) 框架下推导并检验类别化的过度反应: 当新闻事件分属基本面分布尾部厚度不同的类别时, 模型预测投资者对极端类别的新闻过度反应更强; 作者在涵盖 24 类企业新闻 (业绩公告、产品发布、并购、业务扩张、客户相关等) 的数据库上检验, 发现基本面分布越极端的新闻类别, 公告后收益反转与成交量放大越明显。可迁移者仅为一条构念层提示: 新闻的类别归属并非无信息含量的标签, 类别边界本身携带经济含义并系统性关联到反应强度, 因而在测度构造中把连续量映射为类别或子集时, 边界取值不宜被当作中性的技术细节, 值得并排检验——本项目把跟风相似度门槛 τ 在 0.25 / 0.30 / 0.45 上并排做敏感性 (三者与生产口径互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J), 即出于这一考虑。迁移边界须严格声明并不得回退: 原文的类别是语料中外生既有的新闻题材, 其机制是投资者信念形成中的行为偏误, 与研究者在跟风相似度检测网格上的口径选择是两种性质完全不同的离散化; 本处明确不主张原文做过连续信号的离散化, 亦不主张原文提出了"研究者须显式检验阈值"这一方法学规范; 原文更未涉及文本相似度、跟风衰减权重、LLM 或加权分母, 其类别边界与本项目的 τ 无对应物、数值不可比, 故该文只作旁证, 不构成本家族阈值网格设计的直接实证支撑。
## VAR: sum_wd_hw_thr25_llm_full

【变体差分】
本列取 full 轨: 上游 herd_weight_full_thr25 与 llm_vote_score_full 均基于"标题+正文全文"的完整篇章文本计算。三轨 (full/ctx/ss) 是本项目情感与权重体系的公共架构基座, 彼此各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一过度识别 (over-identified) 的 Hansen J 统计量中混用同一构念的不同轨道列。full 轨自 2026-06-29 起是"留篇门控"的唯一判据轨: 一篇报道是否被计入"银行-金科报道"样本, 只看 llm_verified_full == True; ctx/ss 是相对 full 留篇集合的条件测度轨, 行宇宙是 full 留篇集的子集, 但各轨 per-track 列仍照常独立计算。因此 sum_wd_hw_thr25_llm_full 是三轨中样本覆盖最广的一支 (等于该银行-年内 llm_verified_full 为真且 llm_vote_score_full 非缺失的全部文章, 按 τ=0.25 跟风衰减权重之和), 也是与生产口径 τ=0.35 对应主列 sum_wd_hw_llm_full 直接可比的稳健性对照。使用时应保持"同轨同门槛"配对: 若要重构 τ=0.25 下的加权平均语调, 必须用本列作分母、llm_vote_score_hw_thr25_sum_full 作分子, 不可跨轨或跨阈值标签混配, 否则加权平均在分子分母上口径不一致, 数值失去经济含义。此外, 生产口径 τ=0.35 与本列所属的阈值敏感性变体 τ=0.25 应视为同一构念在不同超参数下的稳健性对照组, 二者并排呈现于稳健性附表而非并入主回归同一设定, 目的是让读者直接判断"跟风检测门槛调紧或调松, 是否改变银行-年加权语调的方向与显著性", 而不是提供另一个独立经济含义的新变量。

## VAR: sum_wd_hw_thr25_llm_ctx

【变体差分】
本列取 ctx 轨: 上游 herd_weight_ctx_thr25 与 llm_vote_score_ctx 基于"标题+目标实体窗口"的语境化文本片段计算, 而非全文, 用以剥离与目标银行不直接相关的段落对跟风相似度判定与语调评分的干扰。ctx 轨自 full-only 留篇门控切换后, 行宇宙收窄为 full 轨已留篇文章的子集 (即只对已通过 llm_verified_full 判定的文章计算 ctx 侧的权重与语调), 属于条件测度/稳健性轨而非独立门控轨。与 sum_wd_hw_thr25_llm_full 相比, 本列的差分点在于: 其一, 文本窗口更窄, 使得相似度判定 (从而 herd_weight_ctx_thr25) 与语调评分 (从而是否计入分母) 都可能与 full 轨在同一篇文章上给出不同数值, 是常规现象而非异常; 其二, 与 sum_wd_hw_thr25_llm_ss 同为"互为稳健性"的并排轨, 二者均不应被视为 full 轨的从属或补充。ctx 轨依旧遵守三轨铁律: 各轨各自 just-identified, 不得混入同一 Hansen J 检验；使用者若要验证阈值 τ=0.25 下 LLM 加权语调结论对文本窗口选择是否敏感, 应把 sum_wd_hw_thr25_llm_ctx 与 sum_wd_hw_thr25_llm_full、sum_wd_hw_thr25_llm_ss 三者并排比较, 而不是相加或替代。同时须注意: 本列的分母规模天然小于等于 full 轨 (语境窗口更窄导致更多篇章的 llm_vote_score_ctx 可能缺失), 若发现某银行-年该列显著小于 full 轨对应列, 应先核实是否为语境窗口内实体提及稀疏所致的正常现象, 而非管道故障。

## VAR: sum_wd_hw_thr25_llm_ss

【变体差分】
本列取 ss 轨: 上游 herd_weight_ss_thr25 与 llm_vote_score_ss 基于"标题+银行与金科词同句 (±N 句窗口, 默认 N=1) 共现片段"的最严格文本子集计算, 是三轨中语境粒度最细的一支。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行与金科词的同句共现时, content_ss 退化为使用全文 body (与 content_ctx 无共现时退化为全文的处理逻辑对称), 并标记 ss_is_fallback=True, 此时该篇在 ss 轨上计算出的 herd_weight_ss_thr25 与 llm_vote_score_ss, 本质上是在退化后的全文文本上得到的, 与 full 轨在数值上可能高度重合但概念上仍是独立的一轨, 不可等同视之。ss 轨同样只对 full 留篇集合内的文章计算 (full-only 门控), 且与 ctx、full 两轨严格并排、互为稳健性、禁止混入同一 Hansen J。sum_wd_hw_thr25_llm_ss 作为该轨在阈值 τ=0.25 下的银行-年权重和, 其经济意义是: 在"银行与金科话题真正同句相关"这一最严苛的语境约束下, 跟风衰减加权平均语调的有效权重规模有多大; 当样本量较小 (如早期试跑 T=2) 时, ss 轨因共现条件苛刻, 权重和可能明显小于 full/ctx 两轨, 属预期的稀疏退化现象, 并非数据缺陷。在生产规模 (全量 约 1,819 万条报道、T=19) 语料上, ss 轨样本量随语料扩大而回升, 但其"同句共现"约束始终比 ctx 的"实体窗口"约束更严, 因此三轨权重和之间 sum_wd_hw_thr25_llm_full ≥ sum_wd_hw_thr25_llm_ctx ≥ sum_wd_hw_thr25_llm_ss 的排序在多数银行-年内成立, 可作为数据质量的一个粗略交叉校验, 但不构成强制断言, 因回退语义可能使个别年份出现例外。
<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kwon, S. Y., & Tang, J. (2026). Extreme Categories and Overreaction to News. Review of Economic Studies, 93(2), 1137-1166. https://doi.org/10.1093/restud/rdaf037
<!-- rendered-citations:end -->
