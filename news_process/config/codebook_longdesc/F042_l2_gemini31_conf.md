---
family_id: F042
columns:
- avg_gemini31_conf_ctx
- avg_gemini31_conf_full
- avg_gemini31_conf_ss
unit: 无量纲置信度均值 (LLM 自报概率, 值域约束于 [0,1] 区间)
formula: "avg_gemini31_conf_{track} = mean_{i in valid-vote domain of bank-year, track} conf_gemini31_i; conf_gemini31_i = Gemini-3.1-Flash-Lite 对第 i 篇报道情感判定的自报置信度; 有效分母 = 该轨该银行-年内 gemini31 情感得分有效 (score.notna(), 即掩码列 _conf_valid_gemini31_{track} 非空) 的报道数 — mean 跳 NaN, 故 invalid 票不计入分母"
producer: news_process/pipeline/panel/encode.py
upstream:
- 21_tone_llms.parquet (gemini31 逐篇情感标签与置信度)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.48550/arXiv.2408.15204
  type: arxiv
  authors: Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D.
  year: 2024
  title: "Can unconfident LLM annotations be used for confident conclusions?"
  venue: arXiv
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics
  pages_or_artno: 6577-6595
- doi: 10.24963/ijcai.2020/622
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence
  pages_or_artno: 4513-4519
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: Proceedings of the 22nd International Conference on Machine Learning
  pages_or_artno: 625-632
- doi: 10.1111/jofi.12027
  type: journal
  authors: García, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: Journal of Finance
  pages_or_artno: 1267-1300
- doi: "10.48550/arxiv.2306.13063"
  type: "arxiv"
  authors: "Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B."
  year: 2023
  title: "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"
  venue: "arXiv"
- doi: "10.1007/978-981-96-1710-4_10"
  type: "journal"
  authors: "Ni, S., Bi, K., Yu, L., & Guo, J."
  year: 2025
  title: "Are Large Language Models More Honest in Their Probabilistic or Verbalized Confidence?"
  venue: "Lecture Notes in Computer Science"
  pages_or_artno: "124-135"
- doi: "10.18653/v1/2024.trustnlp-1.13"
  type: "journal"
  authors: "Groot, T., & Valdenegro - Toro, M."
  year: 2024
  title: "Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models"
  venue: "Proceedings of the 4th Workshop on Trustworthy Natural Language Processing (TrustNLP 2024)"
  pages_or_artno: "145-171"
- doi: "10.1162/tacl.a.739"
  type: "journal"
  authors: "Ulmer, D., Lorson, A., Titov, I., & Hardmeier, C."
  year: 2026
  title: "Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing"
  venue: "Transactions of the Association for Computational Linguistics"
  vol: "14"
  pages_or_artno: "1505-1540"
- doi: "10.1016/j.chb.2026.108988"
  type: "journal"
  authors: "Liu, J."
  year: 2026
  title: "Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation"
  venue: "Computers in Human Behavior"
  vol: "181"
  pages_or_artno: "108988"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是 Gemini-3.1-Flash-Lite 这一家大语言模型在情感判定任务上「自报置信度」在银行-年层面的聚合均值。管道的情感判定环节 (stage 21) 并非依赖单一模型, 而是由三家跨厂商的大语言模型共同投票: gpt-5.4-nano (gpt54nano) 与 gemini-3.1-flash-lite (gemini31) 两家经由 yunwu 网关调用, deepseek-v4-flash (deepseekv4) 直连 api.deepseek.com。三家各自对每一篇「银行∧金融科技」报道输出一个情感标签, 同时附带一个对该标签的自报置信度。本家族只抽取其中 gemini31 一家的逐篇置信度, 按银行-年取算术平均, 得到该行该年 Gemini 家判定的平均把握程度。它衡量的不是情感倾向本身 (那由 tone 家族承载), 而是模型对自身判断的确信程度, 因此在计量上是一条「元信息 / 判定质量」通道, 用于诊断某银行某年的报道语料对该家模型而言是否语义清晰、是否存在系统性的模糊或歧义。数据来源是 21_tone_llms.parquet 中 gemini31 的逐篇输出, 文本轨道则由 14_materialize_ctx 物化的 content_full / content_ctx / content_ss 三列供给。逐模型置信度的银行-年聚合 (取算术平均) 定义并执行于 pipeline/panel/encode.py 的聚合字典构造与 groupby.agg 环节 (即为每家模型登记 avg_short_conf_track 为该模型置信度源列的 mean, 再按 target_bank 与 year 分组聚合); pipeline/panel/export.py 只负责下游的 .dta 导出与变量标签映射, 并不承担置信度的求均逻辑。因此本家族列的产出真源是 encode.py, frontmatter 的 producer 亦据此指向 encode.py。

【方法学与计算】
置信度均值的计算遵循严格的逐轨口径。对给定银行-年与给定文本轨道, 分子是该轨内所有 gemini31 情感得分有效的报道的自报置信度之和, 分母是同一轨该银行-年内这些有效报道的计数, 二者相除即为该轨的 avg_gemini31_conf。此处须精确说明分母的域对齐: 聚合并非对全部报道求平均, 而是优先取 valid-vote 域掩码列 _conf_valid_gemini31_track (即该模型 score 非空、真正投出有效票的那部分文章), mean 运算跳过 NaN, 因此有效分母等于该模型自身投出有效票的报道篇数, 而非该银行-年的全部报道数; 仅当该掩码列缺失 (legacy parquet 或未过 encode_sentiment 的合成测试 df) 时才回退到原始物理域列。此设计与该模型的 tone 列同口径, 刻意排除无效票 (invalid 票的自报置信度系统性偏低, 约在 0.66 一档, 而有效票约在 0.88 一档), 以避免无效票把置信度均值向下拉偏、产生 Shapiro 式的衰减偏误。置信度是模型自报的、值域约束在零到一之间的概率型标量, 因此聚合结果保留概率量纲, 而非任意无界得分。三条文本轨道 full / ctx / ss 分别对应「标题加全文正文」「标题加实体上下文窗口」「标题加银行与金融科技同句±N窗」三种文本切法, 由 stage 14 一次性物化并各自带 is_fallback 标记。留篇门控采用 full-only 口径 (2026-06-29): 某篇报道是否算作一篇「银行金融科技报道」只看 llm_verified_full 是否为真, ctx 与 ss 因此降为 conditional-on-full 的条件测度轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的置信度均值仍逐轨独立计算、不借用 full 轨的分子分母。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文, ss_is_fallback 置真, 并与其它轨共享 n_articles 分母, 从而实现优雅降级而非静默丢列。三条轨道互为稳健性、不分主次, 各自 just-identified 并排使用, 铁律是禁止将三轨的置信度混进同一条 over-identified 的 Hansen J 过度识别检验。同理, 本家族只取 gemini31 一家, 它与 gpt54nano、deepseekv4 两家的同名置信度构成跨厂商的 co-equal 互为稳健性轨, 三家各自 just-identified 并排, 同样禁止混入同一 over-identified Hansen J; 某一家缺席只导致该家自身族列降级, 不牵连其余两家 (per-model 独立降级, 区别于 co-primary 嵌入双轨的 both-or-neither 强绑定)。

【文献定位】
把大语言模型的自报置信度作为一条可用的标注质量信号, 其方法学正当性来自近年对 LLM 置信度估计与校准的系统梳理。Geng et al. (2024) 综述了大语言模型置信度估计与校准的多种范式, 指出自报置信度虽非完美校准、却在相对排序意义上携带关于判定难度的信息, 为把它当作银行-年语义清晰度的代理提供了依据。Gligorić et al. (2024) 进一步论证, 即便是「不自信」的 LLM 标注, 只要恰当地纳入不确定性, 仍可支撑可信的下游统计结论, 这正是本家族被设计为诊断/审计通道而非直接处理变量的原因。更早的概率校准传统由 Niculescu-Mizil & Caruana (2005) 奠定, 他们系统比较了各类监督学习器输出概率的校准质量, 提醒我们模型自报概率的绝对水平在跨模型比较时不可直接采信, 只有经标准化后的相对信号才稳健——这一警示直接约束了本家族的使用方式: 只比标准化后的跨模型差异, 不比原始置信度的绝对水平。金融文本情感判定的领域背景则由 Liu et al. (2020) 的 FinBERT 代表, 说明金融语料上的情感/极性判定本身是一项有噪声、需专门表征的任务, 从而置信度的银行-年异质性天然携带信息。在顶刊层面, García (2013) 以媒体报道的情感语调作为可度量的经济状态信号, 证明从金融新闻文本中提取的情感测度在横截面与时间维上均携带真实的、可用于资产定价与经济诊断的信息, 为本家族把金融报道的机器情感判定 (及其自报把握程度) 当作一条有信息量的银行-年计量通道提供了一线金融文献的直接背书。综合而言, 本家族在文献坐标中处于「LLM 标注质量诊断」与「金融情感计量」的交叉处, 服务于对三家投票共识可靠性的横截面与时间维稳健性核验。 就取数方式的原点而言, Xiong 等 (2023) 是黑箱场景下直接索取自报置信度这一 elicitation 范式的奠基性系统评测, 确立了 verbalize-based confidence 的基准协议并记录了模型普遍过度自信, 交代了本家族 conf 列的方法来源; 该文系 arXiv 预印本, 评测对象为当时的 GPT/LLaMA 系模型, 不含 Gemini-3.1-Flash-Lite, 任务亦为英文常识与算术推理而非中文金融情感, 且无面板层聚合。Ni、Bi、Yu 与 Guo (2025) 直接比较同一模型的 token 概率派生置信度与自报置信度在诚实性上的表现, 为本项目因黑箱 API 不返回 logprob 而只能采用 verbalized 一支提供了最新的实证权衡依据 — 该文报告两者各有优劣, 并未论证自报法更优; 其任务为有客观答案的知识型问答, 置信度对应答对与否, 而本列置信度对应无 ground truth 的情感极性判定, 校准概念不能平移。Groot 与 Valdenegro - Toro (2024) 横向评测多个 LLM/VLM 的自报不确定性质量, 实证发现各模型系统性过度自信且过度自信程度随模型而异, 直接支撑上文"只比标准化后的跨模型差异、不比原始置信度绝对水平"的使用约束, 也是把 gemini31 与 deepseekv4、gpt54nano 的同名 conf 列并排为 per-model 互为稳健性轨 (各自 just-identified 并排、不分主次, 严禁混进同一 over-identified 的 Hansen J 过度识别检验) 而非合并为单一指标的事实基础; 原文单位为英文通用/视觉问答基准上的逐题置信度, 所测模型不含本项目所用的 Gemini-3.1-Flash-Lite, 亦未讨论银行-年面板与 valid-vote 掩码分母。Ulmer、Lorson、Titov 与 Hardmeier (2026) 综述人类不确定性沟通研究与 NLP 中的 verbalized uncertainty 研究, 并补充实证了自报不确定性中若干此前未被充分探讨的偏倚, 提示本列的绝对水平须审慎解读; 惟原文立足于面向人类用户的沟通质量与可信度, 未针对把自报置信度当作研究变量的测量效度问题, 也未提出可替换本列的算子, 本家族的银行-年均值聚合与三轨设计均在其讨论范围之外。Liu (2026) 在主观标注任务上以固定 rubric 提示单一模型重标注语料, 报告模型不确定性在人类标注分歧较大处系统性更高, 支持"把握度可被度量且随判定难度变化"这一构念前提; 但其不确定性载体为类别概率向量的 Shannon 熵而非标量自报值, 单模型设计不涉及跨厂商比较, 故不支持本项目的 per-model 并排口径, 语料为英文社交媒体仇恨言论而非中文银行报道, 亦无实体-年聚合。
## VAR: avg_gemini31_conf_full

【变体差分】
本列是 gemini31 置信度均值的 full 轨版本, 也是本家族的参照锚轨, 因为留篇门控采用 full-only 口径: 一篇报道是否算作银行金融科技报道只由 llm_verified_full 决定, 须注意此处的分母仍受 valid-vote 域对齐约束: 具体计入均值的是 gemini31 在 full 轨上真正投出有效票 (score 非空) 的报道, 由掩码列 _conf_valid_gemini31_full 界定, mean 跳 NaN, 故 full 轨的有效分母等于该银行-年 gemini31 有效票的报道数, 而非物理报道总数; 由于 full 又是 full-only 门控主轨, 这一有效集在三轨中最完整、最少受回退污染。文本轨道口径为 content_full, 即标题 prepend 到全文正文之后, gemini31 在整篇文本上给出情感标签与自报置信度, 本列取这些逐篇置信度在银行-年内的算术平均。与同家族 ctx / ss 两列相比, 差分点纯在文本切法与门控地位: full 轨读整篇正文、是门控主轨; ctx / ss 读收窄的上下文、是 conditional-on-full 的条件稳健轨。与跨厂商同名列 avg_gpt54nano_conf_full、avg_deepseekv4_conf_full 相比, 差分点在于模型厂商——本列只取 Gemini-3.1-Flash-Lite 一家的自报置信度, 三家 co-equal、各自 just-identified 并排, 禁止混入同一 over-identified Hansen J。使用时须注意置信度的绝对水平带有 model-specific 的自报偏置, 跨模型只可比标准化后的相对信号, 不可直接比水平; full 轨与 ctx / ss 亦属规格稳健性并排, 同样不得混进一条过度识别检验。在实证叙事中, 本列既可作为报道语义清晰度的横截面代理, 也可作为对三家投票共识可靠性的时间维核验通道: 当 full 轨置信度在某银行-年系统性偏低时, 提示该行该年语料对 Gemini 家而言存在较多歧义或模糊报道, 从而为共识标签附加一层可审计的质量注解, 而非直接改变情感倾向本身的取值。本列在生产 T=19 语料上定义最完整、回退污染最少, 故被列为家族参照锚轨。

## VAR: avg_gemini31_conf_ctx

【变体差分】
本列是 gemini31 置信度均值的 ctx 轨版本。与作为门控主轨的 full 列的唯一构念差分在于文本切法与门控地位: ctx 轨读取的是 content_ctx, 即标题 prepend 之后再拼接实体上下文窗口, 而非整篇正文, 因此 gemini31 只在围绕银行与金融科技实体的收窄文本上作情感判定并自报置信度。由于留篇门控是 full-only, 本列是 conditional-on-full 的条件测度轨, 其行宇宙是 full 留篇集的子集, 但置信度均值仍严格逐轨计算, 分子是 ctx 轨内逐篇置信度之和、分母是 ctx 轨该银行-年内 gemini31 有效票 (由掩码列 _conf_valid_gemini31_ctx 界定、mean 跳 NaN) 的报道计数, 既不借用 full 轨的分母、也不把 gemini31 未投有效票的报道纳入分母。当 ctx 上下文因实体窗口为空而回退时, is_fallback 标记会随之置真, 保证降级可追溯而非静默丢列。本列与 full、ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 铁律是禁止三轨混进同一 over-identified Hansen J; 与跨厂商 avg_gpt54nano_conf_ctx、avg_deepseekv4_conf_ctx 亦为 co-equal 跨厂商稳健轨, 同禁混检验。置信度绝对水平受模型与文本轨双重影响, 解读时只比标准化后的相对差异。在开发期 T=2 的短面板上, ctx 轨可能因上下文极度收窄而呈现退化, 属预期现象, 生产期 T=19 语料上恢复正常信息量。相对 full 轨而言, ctx 轨的价值在于剔除与银行金科主题无关的正文噪声后, 观察 Gemini 家在纯实体上下文上的判定把握是否更高或更低, 从而为「置信度是否被无关正文稀释」这一假设提供并排稳健性证据; 二者作为规格稳健性并排使用, 结论若在 full 与 ctx 上一致方视为稳健。

## VAR: avg_gemini31_conf_ss

【变体差分】
本列是 gemini31 置信度均值的 ss 轨版本, 文本轨道口径最严: content_ss 为标题 prepend 之后拼接「银行与金融科技同句±N窗」的文本 (窗半径由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认为一句), gemini31 只在银行与金科真正同句邻近的最窄语境上判定情感并自报置信度。与 full、ctx 两列的构念差分即在此文本切法: ss 是三轨中语境最收窄者。其关键特性是回退语义镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真, 并与其它轨共享 n_articles 分母, 实现优雅降级。因此 ss 轨的置信度均值在共现稀疏的银行-年会较多地由回退文本贡献, 使用时须结合 fallback 比例审读。留篇门控仍是 full-only, 本列同为 conditional-on-full 的条件稳健轨, 置信度逐轨独立计算不借 full 分母; 其分母同样对齐 valid-vote 域, 只计 ss 轨内 gemini31 有效票 (掩码列 _conf_valid_gemini31_ss, mean 跳 NaN) 的报道, 无效票不入分母。本列与 full、ctx 三轨互为稳健性、各自 just-identified 并排, 禁止混进同一 over-identified Hansen J; 与跨厂商 avg_deepseekv4_conf 等同名列 co-equal 并排, 同禁混检验。开发期 T=2 上 ss 轨常因同句共现稀疏而高度退化, 属预期, 生产 T=19 恢复。作为三轨中语境最严者, ss 轨提供的是「最保守文本切法」下的置信度读数: 若 Gemini 家在仅剩银行与金科同句邻近的极窄语境上仍给出高置信度, 则该判定对文本删减的鲁棒性得到最强背书; 反之置信度显著下滑则提示原判定依赖了同句之外的旁证。ss 与 full、ctx 并排构成从最宽到最窄的语境梯度稳健性叙事, 三者各自 just-identified, 结论须在梯度上一致方为稳健。

<!-- rendered-citations:begin -->
Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv [Preprint]. https://doi.org/10.48550/arXiv.2408.15204
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics, 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence, 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning, 625-632. https://doi.org/10.1145/1102351.1102430
García, D. (2013). Sentiment during recessions. Journal of Finance, 1267-1300. https://doi.org/10.1111/jofi.12027
Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2306.13063
Ni, S., Bi, K., Yu, L., & Guo, J. (2025). Are Large Language Models More Honest in Their Probabilistic or Verbalized Confidence? Lecture Notes in Computer Science, 124-135. https://doi.org/10.1007/978-981-96-1710-4_10
Groot, T., & Valdenegro - Toro, M. (2024). Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models. Proceedings of the 4th Workshop on Trustworthy Natural Language Processing (TrustNLP 2024), 145-171. https://doi.org/10.18653/v1/2024.trustnlp-1.13
Ulmer, D., Lorson, A., Titov, I., & Hardmeier, C. (2026). Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing. Transactions of the Association for Computational Linguistics, 14, 1505-1540. https://doi.org/10.1162/tacl.a.739
Liu, J. (2026). Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation. Computers in Human Behavior, 181, 108988. https://doi.org/10.1016/j.chb.2026.108988
<!-- rendered-citations:end -->
