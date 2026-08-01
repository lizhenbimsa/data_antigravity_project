---
family_id: F115
columns:
- bert_avg_pos_sum_ctx
- bert_avg_pos_sum_full
- bert_avg_pos_sum_ss
unit: 无量纲概率质量总量 (跨三分类 BERT 模型均值; 银行-年内加总口径)
formula: "bert_avg_pos_sum{track} = mean_over_b( {b}_pos_sum{track} ), b ∈ 三分类 BERT 模型集 (_BERT3); 每个 {b}_pos_sum{track} = 该银行-年内逐篇正面类概率在轨道 {track} 上的加总"
producer: news_process/pipeline/panel/geography.py
upstream:
- 23_tone_berts.parquet
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
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
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2018
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
- doi: "10.1111/1911-3846.12949"
  type: journal
  authors: "Berger, A. N., Kim, H. H., & Ma, X. (Flora)"
  year: 2024
  title: "Bank sentiment and liquidity hoarding"
  venue: "Contemporary Accounting Research"
- doi: "10.1016/j.najef.2025.102361"
  title: "An early prediction model on systemic risk under global risk: Using FinBERT and temporal fusion transformer to multimodal data fusion framework"
  authors: "Jin, X., & Lin, S.-L."
  year: 2025
  venue: "The North American Journal of Economics and Finance"
  type: "journal"
- doi: "10.1016/j.ribaf.2025.102881"
  title: "Annual report tone and bank risk-taking behavior: Evidence from China"
  authors: "Wei, L., Wei, M., Jing, H., & Jing, Z."
  year: 2025
  venue: "Research in International Business and Finance"
  type: "journal"
new_dois:
  - "10.1016/j.iref.2024.01.067"
  - "10.1111/1911-3846.12949"
  - "10.1016/j.najef.2025.102361"
  - "10.1016/j.ribaf.2025.102881"
---

## CORE

【构念与来源】
本家族三列 bert_avg_pos_sum_{full,ctx,ss} 是银行-年面板上的"正面情感概率质量总量"综合指标, 度量的是一家银行在某一年的金融科技相关报道中, 被 BERT 判定为正面语调的信息强度的累积规模, 而非其逐篇平均水平。它由 stage 23 (tone_berts) 的逐篇 BERT 情感概率, 经 stage 46 综合层 (pipeline/panel/geography.py) 跨模型聚合而成。构念上, 它服务于本项目"银行金融科技报道语调"这一核心测量三角: 词典法、大语言模型投票法与 BERT 预训练判别法三者互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。BERT 一支之所以不可被词典或 LLM 完全替代, 在于它把上下文双向编码的判别能力带入中文金融文本, 对否定、程度、转折等语言学结构的处理不依赖人工规则枚举, 与词典法的可解释规则消融梯度形成方法学互补; Bochkay 等 (2023) 在会计文本分析的方法学综述中明确指出, 深度预训练判别器已成为词典法之外不可或缺的一极, 而 Frankel、Jennings 与 Lee (2022) 则以机器学习情感对比词典情感的系统证据, 论证了两类测度在增量信息上的非冗余性——这正是本项目坚持三法并排、而非择一为主的方法论依据。

【方法学与计算】
计算分两层。底层 (stage 23) 由若干同为三分类 (正面 pos / 中性 neu / 负面 neg 同域输出) 的中文金融 BERT 模型对每篇报道打分, 得到逐篇正面类概率; 该逐篇概率在银行-年内对轨道文本做加总 (sum 而非 mean), 落为各模型自身的 {模型}_pos_sum{track} 列。上层 (geography.py) 对这一组同分类口径的三分类 BERT 模型 (代码内记为 _BERT3) 取跨模型算术均值, 生成本家族列; 聚合函数 _safe_mean 在某模型该列缺失时优雅返回 NaN 而不中断, 因而某一 BERT 模型缺席只连坐其自身族、不拖垮综合列 (per-model 独立降级, 区别于 co-primary 嵌入的 both-or-neither)。需强调 _sum 与同族 _pos 的区别: _pos 是银行-年内正面概率的均值 (强度, intensive), _pos_sum 是同一概率的总量 (规模, extensive), 后者随报道条数放大, 因而在计量上应与报道数量控制变量或对数化处理配合使用, 单独进入回归时其系数吸收了报道规模效应。FinBERT 类模型的判别有效性由 Huang、Wang 与 Yang (2023) 在金融文本信息抽取中系统验证, 是本项目采用预训练判别器打分的直接文献支撑。BERT 家族的双向 Transformer 编码机制则源自 Devlin 等 (2018) 的预训练范式。

【文献定位】
本测度的经济学意义锚定于银行信息环境与存款人纪律文献。Chen、Goldstein、Huang 与 Vashishtha (2022) 在顶刊证据中表明, 银行信息透明度直接影响存款流动, 媒体所传递的正面语调信息强度是银行外部信息环境的可观测代理, 其累积规模 (而非仅平均语调) 关系到公众对银行的注意力与信心分布。相对于词典法的经典基准 Loughran 与 McDonald (2011), BERT 综合正面总量在方法学上以上下文判别替代词频计数, 二者被本项目刻意并列为互为稳健性的两极而非主从关系。凡涉三轨 (full/ctx/ss)、三法 (词典/LLM/BERT)、跨模型子测度者, 一律遵循"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J"的口径铁律; 真正的跨模型 FWER 校正只在根级 rwolf 模板 (27_tableA12) 内实现, 家族并排本身不构成过度识别。Fang, Wang, Wang 与 Yuan (2024, International Review of Economics & Finance) 以中国银行媒体语调证据表明正面/负面情感的累积暴露直接关联存款稳定与银行系统性风险, 为本家族正面情感总量测度提供中国银行业情境下的经济后果锚点; Berger, Kim 与 Ma (2024, Contemporary Accounting Research) 以文本情感构造银行管理层情绪测度并检验其对流动性囤积行为的影响, 支持本家族将 BERT 情感概率总量视为银行层面可累积经济信号的构念定位。Jin 与 Lin (2025, The North American Journal of Economics and Finance) 用 FinBERT 从多模态新闻文本中提取公众信心情感, 结合时序融合Transformer预测系统性风险, 为本家族 BERT 正面情感总量测度与系统性风险经济后果的关联提供方法学与实证锚点。Wei、Wei、Jing 与 Jing (2025, Research in International Business and Finance) 以中国38家A股上市银行年报语调为文本情感测度, 检验正面语调对银行风险承担行为的影响, 为本家族银行文本正面情感累积规模测度的经济后果解读提供中国银行业情境证据。

## VAR: bert_avg_pos_sum_full

【变体差分】
本列是 full 轨变体, 也是本家族的 canonical 主轨。full 轨文本 = 标题 prepend 到全文正文后的完整报道 (content_full), 覆盖报道全篇语义, 不做实体窗口或同句裁剪。按本项目 2026-06-29 起的留篇门控 full-only 口径, 一篇报道是否被判为"银行金融科技报道"只看 full 轨的 LLM 判定 (llm_verified_full == True); 因而 full 轨的行宇宙即为留篇集全集, ctx 与 ss 两轨是其 conditional-on-full 的子集测度。本列在这一全集上对同为三分类的 BERT 模型的逐篇正面概率总量取跨模型均值, 是三轨中信息最完整、样本最全的一列, 通常作为主回归中的 BERT 正面规模测度, 而 ctx/ss 两轨列作为其规格稳健性并排臂。与家族内 _pos (均值) 列相比, 本列度量的是正面语调的累积规模而非强度, 建议与报道数量或其对数配合使用以剥离规模混淆。就跨模型聚合而言, 本列只对同为三分类 (pos/neu/neg 同域) 的 BERT 模型取均值, 二分类 (Bernoulli) 的 finbert2 因其 pos 概率语义与三分类正面类不可比而不进入本综合列, 这一分类同域约束是 _BERT3 集合的界定原则, 保证跨模型均值在概率语义上可加。因此本列反映的是若干中文金融三分类判别器对"正面语调"这一共识判断的规模化累积, 单一模型的判别偏差被跨模型均值部分平滑, 相较任一 per-model 的 {模型}_pos_sum_full 列更稳健。full 轨与 ctx/ss 轨各自 just-identified 并排, 互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: bert_avg_pos_sum_ctx

【变体差分】
本列是 ctx (实体上下文窗口) 轨变体。ctx 轨文本 = 标题 prepend 到"目标银行实体邻近窗口"内正文片段 (content_ctx), 只保留银行实体附近的局部语境, 剔除与银行实体无关的报道段落, 因而比 full 轨更聚焦于与该银行直接相关的表述。在留篇门控 full-only 口径下, ctx 轨为 conditional-on-full 的稳健性/测度轨: 其行宇宙是 full 轨留篇集的子集, per-track 列在该子集上照常计算。本列对同分类 BERT 模型在 ctx 文本上的逐篇正面概率总量取跨模型均值, 与 full 轨列度量同一构念但在更窄的实体语境上, 用以检验主结论是否被报道中与银行无关的正面表述所驱动。ctx 与 full/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。当 ctx 文本因无实体窗口而回退时, 底层遵循优雅降级, 综合列经 _safe_mean 缺列返回 NaN, per-model 独立降级不连坐其他模型。与 full 轨相比, ctx 轨在正面规模上的收缩幅度可视为报道中"银行无关正面表述"的估计: 若本列相对 full 轨系数大幅衰减, 提示 full 轨的正面信号部分来自与目标银行不直接相关的段落, 这正是实体窗口裁剪意在剥离的混淆。本列同样只对三分类 BERT 模型取均值, 二分类模型不入综合口径, 保证与 full/ss 两轨列的跨模型集合完全一致, 使三轨间差异纯粹归因于文本范围而非模型集合变动。ctx 轨作为 conditional-on-full 的规格稳健性并排臂, 不应被解读为独立于 full 轨的第二主测度。

## VAR: bert_avg_pos_sum_ss

【变体差分】
本列是 ss (银行∧金科同句共现窗口) 轨变体。ss 轨文本 = 标题 prepend 到"目标银行与金融科技词在同一句子及其 ±N 句窗口内共现"的片段 (content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1); 它是三轨中语境最严的一轨, 只保留银行与金科主题真正同句耦合的表述。ss 轨的回退语义严格镜像 ctx: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True 并共享 n_articles 分母; 若金科 AC 自动机为 None 则 ss 优雅整体降级。在 full-only 门控下 ss 亦为 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集。本列对同分类 BERT 模型在 ss 文本上的逐篇正面概率总量取跨模型均值, 用以检验 BERT 正面规模在最严格的银行-金科耦合语境下是否稳健。ss 与 full/ctx 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 在早期试跑 T=2 面板上 ss 轨可能因样本稀薄而退化, 属预期, 生产 T=19 语料上正常。需注意 ss 轨与上游 stage 13 共现硬过滤是不同口径的两个键: stage 13 用 has_bank_fintech_cooccurrence_within_radius 做行级留篇的 ±1 句窗判据, 而 ss 轨文本物化 (stage 14) 走 extract_bank_fintech_cooccurrence 的严格同句口径, 二者禁互相复用。本列与 full/ctx 两轨共用完全相同的三分类 BERT 模型集合, 三轨差异仅来自文本范围的逐级收紧 (全文 → 实体窗口 → 同句共现)。因此 full、ctx、ss 三列可视为 BERT 正面规模测度在语境严格度维度上的稳健性梯子, 主结论若在最严的 ss 轨仍成立, 则对"正面语调来自银行-金科真实耦合"的解释提供最强支持。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next? Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.01.067
Berger, A. N., Kim, H. H., & Ma, X. (Flora). (2024). Bank sentiment and liquidity hoarding. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12949
Jin, X., & Lin, S.-L. (2025). An early prediction model on systemic risk under global risk: Using FinBERT and temporal fusion transformer to multimodal data fusion framework. The North American Journal of Economics and Finance. https://doi.org/10.1016/j.najef.2025.102361
Wei, L., Wei, M., Jing, H., & Jing, Z. (2025). Annual report tone and bank risk-taking behavior: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2025.102881
<!-- rendered-citations:end -->
