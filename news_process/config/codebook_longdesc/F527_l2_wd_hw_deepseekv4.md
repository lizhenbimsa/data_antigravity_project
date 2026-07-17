---
family_id: F527
columns:
- sum_wd_hw_deepseekv4_ctx
- sum_wd_hw_deepseekv4_full
- sum_wd_hw_deepseekv4_ss
unit: 无量纲权重和 (跟风衰减权重 herd_weight 之和, 域 ≥0, 与该银行-年分组内文章数量级相关)
formula: 'sum_wd_hw_deepseekv4{track} = Σ_i herd_weight{track}_i · 1[deepseekv4_score{track}_i is not NaN], 其中 i 遍历该银行-年分组内全部文章; herd_weight{track} 为 stage 24 (herd_decay_processor) 按 Tetlock (2011) 式跟风相似度衰减算出的三轨独立权重 (银行-年组内同话题相似文章按发布时序衰减打折), track ∈ {full, ctx, ss}'
producer: pipeline\panel\runner.py::_build_llm_valid_masked_weights (构造篇章级 _wd_hw_deepseekv4{track} 掩码列) ; pipeline\panel\encode.py (聚合为 sum_wd_hw_deepseekv4{track}, L1197-1203)
upstream:
- 21_tone_llms.parquet (deepseekv4_score_full / deepseekv4_score_ctx / deepseekv4_score_ss — 篇章级 deepseek-v4-flash 情感打分, 提供有效性掩码)
- 24_herd_decay_processor.parquet (herd_weight_full / herd_weight_ctx / herd_weight_ss — 三轨独立跟风衰减权重)
citations:
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: It pays to write well
  venue: Journal of Financial Economics
  vol: '124'
  issue: '2'
  pages_or_artno: 373-394
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: 'Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1'
  venue: The Review of Financial Studies
  vol: '36'
  issue: '12'
  pages_or_artno: 4919-4964
- doi: 10.1016/j.jcorpfin.2025.102772
  type: journal
  authors: Schwenkler, G., & Zheng, H.
  year: 2025
  title: News-driven peer co-movement in crypto markets
  venue: Journal of Corporate Finance
  vol: '93'
  issue: ''
  pages_or_artno: Article 102772
- doi: 10.2139/ssrn.3320859
  type: wp
  authors: Schwenkler, G., & Zheng, H.
  year: 2019
  title: The Network of Firms Implied by the News
  venue: SSRN Working Paper
  vol: ''
  issue: ''
  pages_or_artno: ''
- doi: "10.1080/19312458.2024.2378690"
  type: "journal"
  authors: "Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K."
  year: 2025
  title: "On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions"
  venue: "Communication Methods and Measures"
  vol: "19"
  issue: "1"
  pages_or_artno: "46-62"
- doi: "10.2139/ssrn.5395056"
  type: "wp"
  authors: "Liu, Y., Liu, J., & Wang, T."
  year: 2025
  title: "Large Language Model Disagreement"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "5395056"
new_dois: []
---

## CORE

【构念与来源】
本家族 sum_wd_hw_deepseekv4_{full,ctx,ss} 不是一个独立的情感或语调测度, 而是"跟风衰减加权 (herd-weighted, HW) deepseek-v4-flash 语调"这一稳健性测度族的匹配分母 (valid-mask denominator)。它的构造动机来自一个具体的度量修正问题: LLM 情感打分 (本处特指三家投票 LLM 之一的 deepseek-v4-flash, `deepseekv4_score{track}`) 对部分文章无法给出有效判断时会返回缺失值 (NaN), 而按银行-年分组聚合"跟风衰减加权语调"时, 如果分子只累加有效文章的 weight×score, 分母却仍沿用该组全部文章 (含无效文章) 的权重和, 会造成分子分母数的不是同一批文章 — 权重被系统性稀释, 加权语调随 LLM 判空比例增大而机械地向 0 偏移, 这是一种与真实语调水平无关的度量噪声。本家族三列正是给"跟风衰减 (HW) 加权" 这一权重体系配的匹配分母: 只累加 deepseekv4 模型在该行给出有效打分的那些文章的 herd_weight, 从而让加权均值的分子分母覆盖同一文章集合。这一"分子分母同域" (numerator-denominator domain matching) 的思路是描述性统计中加权平均处理缺失值的标准做法, 本项目内部记为 fix(encode-01), 源码注释明确标注为 2026-06-10 的一次 metric-audit 修正 — 修正前的加权语调存在随 LLM-invalid 占比增大系统性向 0 衰减的缺陷, 本家族三列即该修正引入的配套基础设施列。
跟风权重 (herd_weight) 本身承载的经济学构念是媒体报道的跟风/抄稿行为会稀释单篇报道的信息含量 — 与同一话题、同一时段内高度相似的其他报道, 其边际信息增量更低, 若不加处理地等权纳入语调聚合, 会让抄稿聚集的话题在银行-年层面被过度加权。stage 24 (herd_decay_processor) 按文本相似度阈值判定抄稿相似文章簇, 并对簇内文章按发布时序施加衰减权重, 使较早、原创性更高的报道保留更高权重, 较晚的跟风复述报道权重递减。sum_wd_hw_deepseekv4{track} 就是把这套跟风衰减权重, 限定在 deepseekv4 模型给出了有效情感判断的文章子集上求和, 供 encode 阶段计算 deepseekv4 模型专属的 HW 加权语调时作分母使用。同一权重体系下, 还并行存在面向三家投票共识 (llm)、另外两家单模型 (gpt54nano、gemini31) 以及概率映射测度 (prob) 的同构分母列, 本家族只覆盖 deepseekv4 一支。

【方法学与计算】
构造分两步, 分别在 runner.py 与 encode.py 完成。第一步 (runner.py::_build_llm_valid_masked_weights) 在篇章级生成掩码列 _wd_hw_deepseekv4{track}: 对每条文章, 若该文章在对应轨道下的 deepseekv4_score{track} 非缺失, 则该掩码列取值为该文章在该轨道下的 herd_weight{track}; 若 deepseekv4_score{track} 为缺失 (表示 deepseekv4 模型对该文章未给出有效判断), 则掩码列本身也置为 NaN。第二步 (encode.py 聚合阶段) 按银行-年分组对该掩码列求和 (pandas groupby.sum 默认跳过 NaN), 得到 sum_wd_hw_deepseekv4{track} = Σ herd_weight{track}_i, 仅对 deepseekv4_score{track} 非缺失的文章 i 求和。这一先掩码后求和的两步实现, 使得最终列值天然等价于该银行-年组内、deepseekv4 有效打分的文章集合上的 herd_weight 总和 — 与分子 deepseekv4_score_hw_sum{track} (= Σ herd_weight{track}_i·deepseekv4_score{track}_i, 同一有效文章集合上求和) 严格同域, 两者相除即得 deepseekv4 模型的跟风衰减加权平均语调, 不受 LLM 判空率的机械稀释影响。
三列差分完全由轨道 (track) 决定, 无其他自由参数。full/ctx/ss 三轨分别对应三条独立的文本抽取口径与三条独立的 herd_weight 序列 (stage 24 对三轨分别计算文本相似度并分别衰减), 而不是同一权重序列在三种文本上复用。因此 sum_wd_hw_deepseekv4_full、_ctx、_ss 三列既反映 deepseekv4 有效打分文章的分布随轨道变化 (因为不同轨道下 deepseekv4 对同一篇文章可能给出不同的有效性判定, 尤以 ss 轨道的回退语义为甚), 也反映 herd_weight 权重取值随轨道变化 (因为三轨的相似度判定文本不同, 抄稿簇划分可能不同)。三列均为无量纲的权重和, 数值上界受该银行-年分组内文章总数与单篇 herd_weight 上界共同约束, 数值本身不直接具备语调方向或强度含义, 仅作分母使用。
口径上必须强调三条铁律。其一, full/ctx/ss 三轨是各自 just-identified 并排的稳健性测度, 互为稳健性、不分主次, 三者严禁被混入同一个 over-identified 的 Hansen J 检验框架 — 每条轨道各自构成一套独立可识别的加权语调及其分母, 不应把三轨分母或三轨分子混合累加成单一统计量。其二, deepseekv4 是三家投票 LLM (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 两家走 yunwu、deepseek-v4-flash/deepseekv4 直连 api.deepseek.com) 之一, 三家模型的对应分母族 (sum_wd_hw_gpt54nano{track}、sum_wd_hw_gemini31{track}、sum_wd_hw_deepseekv4{track}) 同样各自 just-identified 并排、互为跨厂商稳健性, 不构成同一 Hansen J 检验的过度识别工具集。其三, 留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入银行金科报道样本只看 llm_verified_full == True, ctx/ss 分母降为 conditional-on-full 的测度轨道, 其行宇宙是 full 留篇集合的子集, 但 herd_weight 与 deepseekv4 有效性判定仍按各轨道独立计算, 不借用 full 轨的权重或有效性标记。ss 轨的回退语义镜像 ctx: 当某篇报道在 stage 14 未能识别出银行∧金科同句共现时, content_ss 回退为全文正文, ss_is_fallback 置 True, 该篇文章依旧参与 herd_weight_ss 的计算与 deepseekv4 有效性判定, 不因回退而被剔除。

【文献定位】
跟风衰减权重的方法学根基是 Tetlock (2011, *Review of Financial Studies*) 关于媒体报道中低信息含量的重复/抄稿内容会稀释新闻定价效力的经典论证, 本项目 stage 24 的相似度衰减设计正是对这一构念的直接操作化 (源码注释明确标注 Tetlock 2011, RFS 语调聚合块, 与该文献期刊归属一致)。就 deepseekv4 本身的构念定位而言, 采用大语言模型对金融文本做情感/语调打分并以多家模型互证的做法, 近年在文本情感分析文献中已成为与传统词典法、监督分类器并列的第三条主流路径; Hwang & Kim (2017, *Journal of Financial Economics*) 说明可读性与文本处理质量本身会系统性影响金融文本分析结果的可靠性, 这为本项目坚持三家 LLM 互证加有效性掩码而非单一模型裸打分的设计选择提供了间接支持 — 单一模型的缺失值或低质量判断若不加掩码处理直接进入加权聚合, 会引入与 Hwang & Kim 所警示的文本处理质量问题同构的度量偏误。Hassan et al. (2023, *The Review of Financial Studies*) 展示了基于文本的企业层面暴露度量在构造时对缺失或未命中观测的正确处理如何直接决定测度的有效性, 这一原则同样适用于本家族分子分母同域的匹配分母设计。就跟风或同伴信息扩散的经济学定位, Schwenkler & Zheng (2019, SSRN; 2025, *Journal of Corporate Finance*) 关于新闻驱动的同业同伴联动网络的研究, 为同一话题的重复报道构成信息稀释而非独立信息增量这一前提假设提供了实证文献支撑, 与本家族服务的跟风衰减加权语调测度在构念上一脉相承。 就各家 LLM 有效性掩码这一分母构造前提而言, Laurer、Casas 与 Welbers (2025) 以对照实验证明指令/提示设计会实质改变语言模型作为测量工具的效度与偏误, 提示本家族分母所依赖的「deepseekv4 在该轨给出有效判断」这一掩码本身即模型效度的函数; 但该文对象为传播学英文文本分类任务与开源指令微调模型, 其「加指令可提效度」的结论与本项目嵌入侧刻意零 instruct 前缀、情感提示词 v8 已字节冻结的设计取向不同, 且原文不涉及权重加权分母口径, 故只作效度前提的方法学锚定, 不构成对本项目提示词设计的规范依据。Liu、Liu 与 Wang (2025) 以金融文本为对象度量并实证刻画了不同大语言模型判断的分歧程度, 恰可解释本家族与 gpt54nano/gemini31 同名 hw 分母之所以彼此不同——差异完全来自各家有效打分覆盖面的不重合; 但该文系 SSRN 工作论文, 尚未经期刊同行评审, 且其把分歧本身当作信号/噪声加以研究, 本项目则不将分歧入模, 仅以各家有效性掩码构造各自独立的分母, 其模型集合与语料亦与本项目三家 API 模型加中文银行×金融科技语料不同。
## VAR: sum_wd_hw_deepseekv4_ctx

【变体差分】
本列取 track=ctx, 即分母限定在 stage 14 物化的实体窗口文本 (content_ctx = 标题 + 目标银行实体前后窗口文本) 之上计算 deepseekv4 有效性掩码与 herd_weight。它与 _full 的差异体现在两处联动环节: 其一, deepseekv4 模型对同一篇文章在 ctx 窗口文本上给出的情感判断可能与在全文上给出的判断不同 (更短、更聚焦于银行实体上下文, 信息量与噪声结构均不同于全文), 因此该篇文章在 ctx 轨是否被计入有效分母, 与其在 full 轨是否被计入并不严格重合; 其二, stage 24 对 ctx 文本独立计算文本相似度并衰减, herd_weight_ctx 反映的是实体窗口文本层面的跟风抄稿相似度, 与 herd_weight_full 反映的全文层面相似度可能因窗口截断而产生不同的抄稿簇划分 (例如两篇全文差异很大但银行实体窗口高度相似的报道, 在 ctx 轨会被判为抄稿簇而在 full 轨不会)。按项目铁律, ctx 轨在留篇口径上是 conditional-on-full 的稳健性/robustness 轨道 — 行宇宙是 full 轨留篇集合的子集, 但本列的分子分母计算仍按 ctx 轨自身独立完成, 不借用 full 轨的权重或有效性标记, 与 _full、_ss 两列各自 just-identified 并排、互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 检验。实证使用上, 本列与同轨分子 deepseekv4_score_hw_sum_ctx 相除后得到的加权语调, 常与 P1 主口径 (full 轨) 的对应估计并排呈现, 用于检验主结论是否随文本抽取窗口收窄 (从全文收窄到银行实体前后窗口) 而漂移; 若两轨系数方向一致且显著性相近, 支持结论不依赖窗口设定这一具体建模选择。

## VAR: sum_wd_hw_deepseekv4_full

【变体差分】
本列取 track=full, 即分母限定在标题加完整正文文本 (content_full) 之上计算 deepseekv4 有效性掩码与 herd_weight, 是三轨中的 canonical 主口径轨道, 承担留篇门控的判定基准: 一篇报道是否计入银行金科报道样本, 仅看 llm_verified_full == True, ctx/ss 两轨的行宇宙均是 full 轨留篇集合的子集。deepseekv4 模型在全文文本上给出的有效性判断覆盖面通常最广 (全文信息最完整, 模型更少因上下文不足而返回无法判断), 因此本列在同一银行-年分组内的数值通常不小于 ctx/ss 两轨的对应值, 但这只是文本完整度差异的自然结果, 不代表 full 轨在识别策略或统计意义上优先于另两轨 — 三轨仍是并排的稳健性测度, 各自匹配各自的分子 (deepseekv4_score_hw_sum_full) 构成独立可识别的加权语调, 不构成同一过度识别系统的组成部分。herd_weight_full 反映的是全文层面的文本相似度衰减, 是三轨 herd_weight 中信息最完整、也是 stage 24 抄稿簇判定最常被引用为主参照的一条, 但在本家族语境下与 ctx/ss 严格并列, 无主次之分。在实证使用上, sum_wd_hw_deepseekv4_full 与分子 deepseekv4_score_hw_sum_full 相除得到的加权语调, 是 P1 主回归中作为跨厂商稳健性检验的三家单模型语调之一 (与 gpt54nano、gemini31 两支并列), 用于证明主结论不依赖某一家 LLM 厂商的判断; 该列本身在诊断阶段也可单独用于核查某银行-年分组内 deepseekv4 的判空率与该组文章体量、herd 抄稿簇结构是否存在异常波动。

## VAR: sum_wd_hw_deepseekv4_ss

【变体差分】
本列取 track=ss, 即分母限定在银行∧金科同句共现窗口文本 (content_ss = 标题 + 银行与金科词同句共现的句子窗口, 半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 之上计算 deepseekv4 有效性掩码与 herd_weight。ss 轨的回退语义镜像 ctx: 当某篇文章内不存在银行∧金科同句共现时, content_ss 按管道约定回退为全文正文, 对应 ss_is_fallback 标记置 True, 该文章依旧参与本列 herd_weight_ss 的求和与 deepseekv4 有效性判定 (不因文本回退而被排除出分母), 与 ctx 轨共享 n_articles 分母的回退处理原则一致。由于 ss 窗口文本通常比 ctx 窗口更短、更聚焦于银行-金科语义共现片段, deepseekv4 模型在 ss 轨给出有效判断的门槛与 ctx/full 两轨存在系统性差异, 进而使 herd_weight_ss 反映的同句共现层面跟风相似度衰减模式独立于另两轨 — 两篇全文或实体窗口都不相似的报道, 若各自的银行-金科同句片段高度雷同 (例如都在转述同一条监管通稿的某句结论), 仍可能在 ss 轨被判为抄稿簇。本列与 _full、_ctx 两列各自 just-identified 并排、互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 检验。实证使用上, 本列的一个直接效用是可与同轨的分子列相除得到 deepseekv4 模型在同句共现窗口下的跟风衰减加权语调, 用来检验主结论 (通常以 full 轨为门控口径的结论) 是否在"仅取银行与金科词紧邻共现的最窄语境"下依旧稳健, 若三轨估计系数方向与显著性一致, 说明结论不依赖某一条特定文本抽取口径。

<!-- rendered-citations:begin -->
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. Journal of Corporate Finance, 93, Article 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
Schwenkler, G., & Zheng, H. (2019). The Network of Firms Implied by the News. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3320859
Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
Liu, Y., Liu, J., & Wang, T. (2025). Large Language Model Disagreement. SSRN Electronic Journal No. 5395056 [Working Paper]. https://doi.org/10.2139/ssrn.5395056
<!-- rendered-citations:end -->
