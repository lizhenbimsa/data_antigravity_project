---
family_id: F035
columns:
- avg_deepseekv4_conf_ctx
- avg_deepseekv4_conf_full
- avg_deepseekv4_conf_ss
unit: 无量纲自报置信度 (verbalized confidence ∈ [0,1]) 的银行-年算术均值
formula: "avg_deepseekv4_conf{track} = mean_{i ∈ B,t 且 deepseekv4 情感票有效}( deepseekv4_sentiment_confidence{track,i} ); track ∈ {_full,_ctx,_ss}; 掩码源列 _conf_valid_deepseekv4{track} (缺失时回退物理域 deepseekv4_sentiment_confidence{track})"
producer: news_process/pipeline/panel/encode.py::encode_sentiment (文章级 valid-vote 掩码) + build_agg_spec (Bank-Year mean 聚合)
upstream:
  - 21_tone_llms.parquet (deepseekv4_sentiment_confidence_full / _ctx / _ss)
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
  venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)
  pages_or_artno: 6577-6595
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.24963/ijcai.2020/622
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)
  pages_or_artno: 4513-4519
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  pages_or_artno: 535-574
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
- doi: "10.1162/tacl.a.739"
  type: "journal"
  authors: "Ulmer, D., Lorson, A., Titov, I., & Hardmeier, C."
  year: 2026
  title: "Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing"
  venue: "Transactions of the Association for Computational Linguistics"
  vol: "14"
  pages_or_artno: "1505-1540"
- doi: "10.18653/v1/2024.trustnlp-1.13"
  type: "journal"
  authors: "Groot, T., & Valdenegro - Toro, M."
  year: 2024
  title: "Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models"
  venue: "Proceedings of the 4th Workshop on Trustworthy Natural Language Processing (TrustNLP 2024)"
  pages_or_artno: "145-171"
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
本家族度量单一大语言模型 DeepSeek-V4 Flash 在为银行金科报道打情感标签时所自报的置信度 (verbalized confidence), 逐篇取值后在银行-年层面取算术均值, 得到三条轨道的面板列 avg_deepseekv4_conf_full、avg_deepseekv4_conf_ctx、avg_deepseekv4_conf_ss。构念上, 它回答的不是"这批报道的语气有多正面", 而是"给这批报道打语气标签这件事本身有多可靠"——即情感测度的信噪比。置信度越低, 意味着该银行该年的报道对模型而言语义越模糊、极性越难判定, 对应到计量上就是更大的测量误差, 会把语气变量对因变量的估计系数向零方向衰减 (attenuation bias)。因此本家族既是情感主测度的质量诊断量, 也可作为调节变量或样本分层依据进入稳健性设计。DeepSeek-V4 Flash 是 stage 21 情感三家投票中直连 api.deepseek.com 的一家 (另两家 gpt-5.4-nano 与 gemini-3.1-flash-lite 走 yunwu), 与嵌入模型体系完全无关, 换嵌入时本家族零误改。数据来源为 stage 21 输出的 21_tone_llms.parquet 中该模型的逐篇 deepseekv4_sentiment_confidence 字段, 三轨文本 (content_full/content_ctx/content_ss) 由 stage 14 ctx_materializer 物化后分别喂入同一提示模板。

【方法学与计算】
逐篇置信度是 LLM 在返回三分类语气标签的同时以文本形式生成的数值, 约束在闭区间零到一。这类自报置信度在校准意义上并不等同于真实后验概率——Geng et al. (2024) 的综述指出 verbalized confidence 普遍存在系统性校准偏差, 但通常仍保留排序有效的不确定性信息, 因此本家族只把它当作银行-年之间相对信噪比的诊断量与分层依据, 不作绝对概率解释, 也不在本文档手填任何取值区间或分布形状 (统计特征由引擎注入的统计段呈现, 且须待生产 T=19 语料跑通后方可实测, 早期试跑 T=2 样本不足以刻画其经验分布)。面板聚合发生在 encode.py: 先在文章级把该模型置信度按 valid-vote 域掩码——只保留 DeepSeek-V4 情感票有效 (即成功产出可用极性分数) 的那些报道, 掩码源列为 _conf_valid_deepseekv4{track}; 该掩码列在 legacy parquet 或合成测试数据缺失时优雅回退到物理域原始列 deepseekv4_sentiment_confidence{track}, 保证向后兼容。掩码之所以关键, 是因为验证失败或语气未定义的无效票往往系统性地带着极低置信度, 若不剔除会机械拉低银行均值, 造成测度域与被调节的语气测度域错位。掩码之后, 按银行-年分组取算术均值即得本家族三列; 本家族只产出该均值, 不派生组内标准差之类的二阶矩配套列。整个流程是纯后处理 (无新增付费 LLM 调用), 在 stage 21 缓存零 miss 时可离线字节级复现。

【文献定位】
把语言模型自报的置信度当作可用信号而非噪声, 有明确文献支撑。Geng et al. (2024) 系统综述了大语言模型置信度估计与校准的方法与陷阱, 指出 verbalized confidence 虽存在校准偏差却携带排序有效的不确定性信息; Gligorić et al. (2024) 进一步论证即便是"不自信"的 LLM 标注, 经恰当的不确定性处理后仍可支撑可信的下游统计结论, 为把低置信样本纳入而非一律丢弃提供了依据。校准问题的经典源头可追溯到 Niculescu-Mizil and Caruana (2005) 对监督学习输出概率质量的分析——模型输出的分数需经校准才等同于真实概率, 这解释了为何本家族只把置信度用作相对信噪比诊断与分层依据、而非绝对概率解释。在金融文本这一具体领域, Liu et al. (2020) 的 FinBERT 表明领域预训练能显著改善金融语料上的情感判别可靠性, 佐证了以模型置信度刻画报道语义清晰度的合理性。从计量经济学把文本当数据的方法学总纲看, Gentzkow, Kelly and Taddy (2019) 系统论证了以文本构造的量化测度天然带有测量误差、需以其信噪比与不确定性为一等公民纳入设计, 这为本家族把 LLM 自报置信度作为语气测度的信噪比诊断量、并据以评估语气变量衰减风险提供了方法论支撑。需强调铁律: 三轨 full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨置信度混进同一 over-identified 的 Hansen J 过度识别检验; 同理本家族刻画的是 DeepSeek-V4 单家置信度, 与 gpt-5.4-nano、gemini-3.1-flash-lite 两家的同名置信列构成 per-model 互为稳健性并排 (每家 per-model 独立降级, 某家缺席只掉自身族, 非 co-primary 嵌入的 both-or-neither), 亦禁三家混入同一过度识别式。留篇门控口径遵循 2026-06-29 的 full-only 裁决: 一篇报道是否算作银行金科报道只看 full 轨的 llm_verified_full, ctx 与 ss 轨降为 conditional-on-full 的条件测度, 其行宇宙是 full 留篇集的子集。 就自报置信度这一取数方式本身, Xiong 等 (2023) 是黑箱场景下直接向 LLM 索取 verbalized confidence 的奠基性系统评测, 建立了该范式的基准协议并记录了模型普遍过度自信, 可用以交代本家族 conf 列的方法原点; 该文为 arXiv 预印本, 评测对象为当时的 GPT/LLaMA 系模型, 任务为英文常识与算术推理, 既不含 deepseekv4, 亦无面板层聚合。Ni、Bi、Yu 与 Guo (2025) 直接对比同一模型的 token 概率派生置信度与自报置信度在诚实性上的差异, 是本项目因 API 黑箱不返回 logprob 而只能取 verbalized 一支的最新实证权衡依据——该文报告两种置信度各有优劣, 并未论证自报法优于概率法; 其任务为知识型问答, 置信度对应答对与否, 而本家族置信度对应情感极性这一无客观 ground truth 的主观判定, 校准概念不能平移。Ulmer、Lorson、Titov 与 Hardmeier (2026) 综述人类不确定性沟通与 NLP 中的 verbalized uncertainty 研究, 并补充实证了其中若干此前未被充分探讨的偏倚, 支撑"自报不确定性本身带有系统性偏倚"这一实证层; 惟原文关注的是面向人类用户的沟通质量与可信度, 未针对把自报置信度当作研究变量的测量效度问题, 亦未提出可替换本列算子的方案, 本家族的银行-年均值聚合与三轨设计均在其讨论范围之外。Groot 与 Valdenegro - Toro (2024) 横向评测多个 LLM/VLM 自报不确定性的质量, 实证发现各模型系统性过度自信且过度自信程度随模型而异, 这正是本项目把 deepseekv4 与 gemini31、gpt54nano 的同名 conf 列并排为 per-model 互为稳健性轨、而非合并为单一指标的事实基础; 原文单位是英文通用/视觉问答基准上的逐题置信度, 所测模型不含 DeepSeek-V4-Flash, 亦未讨论银行-年面板或 valid-vote 掩码分母。Liu (2026) 以固定 rubric 提示单一模型重标注仇恨言论语料, 检验 LLM 标注与人类众包标注的一致性及模型不确定性与人类分歧的关系, 可锚定"在与情感判定同类的主观标注任务中, 模型自我报告的把握度可被度量, 且在人类标注分歧较大处系统性更高"这一层; 但其不确定性载体是类别概率向量的 Shannon 熵而非标量自报置信度, 且全程只用一个模型、不涉及跨厂商比较, 故不支持本项目的 per-model 并排口径, 语料亦为英文社交媒体文本而非中文金融新闻, 并无实体-年聚合。
## VAR: avg_deepseekv4_conf_ctx

【变体差分】
本列是 ctx 轨的 DeepSeek-V4 自报置信度银行-年均值。ctx 轨文本 = 标题 prepend 后拼接目标实体上下文窗口 (content_ctx), 只保留银行实体附近的语义片段而非全文, 因此相对 full 轨聚焦度更高、周边无关噪声更少, 但覆盖的信息量也更窄。在 2026-06-29 full-only 门控下, ctx 轨不再参与"是否留篇"的判定, 降为 conditional-on-full 的条件测度/稳健性轨: 其行宇宙是 full 留篇集的子集, 置信度均值 per-track 照算但只在 full 已留篇的报道上定义, 不得反过来扩张留篇集。它与 full 轨、ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混入同一 over-identified 的 Hansen J 过度识别检验。逐篇置信度同样经 valid-vote 域掩码 (源列 _conf_valid_deepseekv4_ctx) 后聚合, 分母是 ctx 轨该模型情感票有效的报道数, 严格逐轨、不借用 full 轨分母。该列刻画的是"仅看银行上下文窗口时 DeepSeek-V4 判语气有多确定", 与 full 轨同期值的差异反映了截取上下文、丢弃全文语境对语义清晰度的边际影响; 若 ctx 置信度系统性高于 full, 提示全文中的旁支内容确在稀释判别信号。与 gpt54nano、gemini31 两家的同轨置信列并列构成 per-model 稳健性, 各家 per-model 独立降级、某家缺席只掉自身族。在早期试跑 T=2 样本上 ctx 轨可能出现零方差退化属预期, 生产 T=19 下恢复正常出值。

## VAR: avg_deepseekv4_conf_full

【变体差分】
本列是 full 轨的 DeepSeek-V4 自报置信度银行-年均值。full 轨文本 = 标题 prepend 后的全文正文 (content_full), 是三轨中信息量最完整的轨道, 也是留篇门控的 canonical 轨: stage 21 判定"是否一篇银行金科报道"只看 llm_verified_full, 因此 full 轨的置信度均值定义在该银行该年的全部留篇报道 (且 DeepSeek-V4 情感票有效) 之上, 是本家族的基准轨与首要轨。相对于 ctx/ss 两条条件轨, full 轨分母最大、样本框最稳, 置信度均值的年内方差最小、生产 T=19 下最不易退化; 相对于 gpt54nano 与 gemini31 两家的同名 full 列, 本列专刻画 DeepSeek-V4 这一家 (直连 api.deepseek.com、与另两家走 yunwu 不同源) 的判别可靠性, 三家互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 每家 per-model 独立降级, 与 co-primary 嵌入的 both-or-neither 语义不同。逐篇置信度按 valid-vote 域掩码 (源列 _conf_valid_deepseekv4_full) 后聚合, 剔除无效票的系统性低置信干扰, 与其调节的 deepseekv4 语气测度严格同口径、同定义域。生产语料上该列可作为 full 轨情感信噪比的直接诊断量: 低值银行-年对应更模糊的报道语义、更大的测量误差与更明显的语气系数向零衰减风险, 可据此做样本分层或作为交互项进入调节分析。因 full 轨承担留篇门控与 P1 主轨的双重角色, 本列亦是三家置信度对比的公共基准: 其他两家 full 置信度须与本列并排读, 判断某家是否在特定语境上系统性更保守或更自信。

## VAR: avg_deepseekv4_conf_ss

【变体差分】
本列是 ss 轨 (同句共现轨) 的 DeepSeek-V4 自报置信度银行-年均值。ss 轨文本 = 标题 prepend 后, 取银行与金科词在同一句子及其上下 N 句窗口内共现的片段 (content_ss), 是三轨中语义约束最强、最贴近"银行谈金科"核心语境的轨道。其回退语义严格镜像 ctx 轨: 当某报道不存在银行与金科的同句共现时, content_ss 优雅回退为全文 body 且 ss_is_fallback 置 True (与 ctx 共享 n_articles 分母), 保证不因无共现而空缺。在 full-only 门控下 ss 轨同属 conditional-on-full 条件测度轨, 行宇宙是 full 留篇集子集, 与 full、ctx 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇置信度经 valid-vote 域掩码 (_conf_valid_deepseekv4_ss) 后按银行-年取均值, 分母为 ss 轨该模型有效票数, 严格逐轨不借 full 分母。该列度量在最窄、最聚焦的银行∧金科同句语境下 DeepSeek-V4 判语气的确定程度, 与 ctx/full 的差值揭示语境收窄对判别可靠性的边际影响; 与 gpt54nano、gemini31 两家的同轨置信列并列构成 per-model 稳健性, 各家 per-model 独立降级、某家缺席只掉自身族而非连坐, 早期试跑 T=2 样本上同句共现稀疏导致的退化属预期, 生产 T=19 正常出值。该列宜与 full/ctx 同期值联读: 三轨置信度随语境收窄的单调走势本身即是报道语义是否集中于"银行谈金科"核心的诊断信号。

<!-- rendered-citations:begin -->
Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv [Preprint]. https://doi.org/10.48550/arXiv.2408.15204
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT), 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 535-574. https://doi.org/10.1257/jel.20181020
Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2306.13063
Ni, S., Bi, K., Yu, L., & Guo, J. (2025). Are Large Language Models More Honest in Their Probabilistic or Verbalized Confidence? Lecture Notes in Computer Science, 124-135. https://doi.org/10.1007/978-981-96-1710-4_10
Ulmer, D., Lorson, A., Titov, I., & Hardmeier, C. (2026). Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing. Transactions of the Association for Computational Linguistics, 14, 1505-1540. https://doi.org/10.1162/tacl.a.739
Groot, T., & Valdenegro - Toro, M. (2024). Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models. Proceedings of the 4th Workshop on Trustworthy Natural Language Processing (TrustNLP 2024), 145-171. https://doi.org/10.18653/v1/2024.trustnlp-1.13
Liu, J. (2026). Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation. Computers in Human Behavior, 181, 108988. https://doi.org/10.1016/j.chb.2026.108988
<!-- rendered-citations:end -->
