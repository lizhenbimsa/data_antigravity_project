---
family_id: F043
columns:
- avg_gpt54nano_conf_ctx
- avg_gpt54nano_conf_full
- avg_gpt54nano_conf_ss
unit: 无量纲置信度 (LLM 自报, 归一化至 [0,1], 银行-年内篇均)
formula: "avg_gpt54nano_conf_track = mean_i( conf_gpt54nano_i ), i 取该银行-年、该 track 下 full-only 留篇集 ∩ gpt54nano 该轨 score 有效 (per-model valid-score 掩码 _conf_valid_gpt54nano_track = conf.where(score.notna())) 的报道; conf 为 gpt5.4-nano 单模型对本篇情感判定所自报的置信度"
producer: "news_process/pipeline/panel/encode.py (银行-年 mean_i 篇均聚合真源: LLM_MODELS 循环对 _full/_ctx/_ss 三轨执行 avg_{short}_conf{track}=(conf_src,'mean'), conf_src 优先取 per-model 有效性掩码列 _conf_valid_{short}{track}); news_process/pipeline/panel/export.py (仅面板列装配与显示标签, 不计算篇均); 上游逐篇置信来自 news_process/pipeline/sentiment/tone_llms.py"
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 21_tone_llms.parquet (逐篇 gpt54nano 情感判定 + 自报置信)
citations:
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics
  pages_or_artno: 6577-6595
- doi: 10.48550/arXiv.2408.15204
  type: arxiv
  authors: Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D.
  year: 2024
  title: "Can unconfident LLM annotations be used for confident conclusions?"
  venue: arXiv
- doi: 10.24963/ijcai.2020/622
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)
  pages_or_artno: 4513-4519
- doi: 10.18653/v1/N19-1423
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics
  pages_or_artno: 4171-4186
- doi: 10.1145/1341531.1341561
  type: journal
  authors: Ding, X., Liu, B., & Yu, P. S.
  year: 2008
  title: "A holistic lexicon-based approach to opinion mining"
  venue: Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08)
  pages_or_artno: 231-240
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  pages_or_artno: 1139-1168
- doi: "10.1016/j.pacfin.2024.102632"
  type: journal
  authors: "Chiu, I.-C., & Hung, M.-W."
  year: 2025
  title: "Finance-specific large language models: Advancing sentiment analysis and return prediction with LLaMA 2"
  venue: "Pacific-Basin Finance Journal"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, F., Alizadeh, M., & Kubli, M."
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: "Proceedings of the National Academy of Sciences"
new_dois:
  - "10.1016/j.pacfin.2024.102632"
  - "10.1073/pnas.2305016120"
---

## CORE

【构念与来源】
本家族刻画的是情感判定阶段第一家大模型 gpt5.4-nano (面板短名 gpt54nano) 在对单篇银行金融科技报道做情感极性判定时所自报的置信度 (self-reported confidence), 经银行-年、按文本轨聚合后得到的篇均置信序列。项目的情感 LLM 环节采用三家投票机制: gpt5.4-nano 与 gemini-3.1-flash-lite 两家经 yunwu 中转, deepseek-v4-flash 直连 api.deepseek.com; 三家各自对每篇报道输出一个情感标签及一个对该标签把握程度的置信数值。本家族只截取其中 gpt54nano 一家的置信数值, 是「情感 LLM 三家互为稳健性」体系在置信维度上的单厂商切片, 而非三家共识。置信数值本身不是被解释变量, 而是一个元测度 (meta-measure): 它衡量模型对自身判定的把握, 在计量上多用作情感信号质量的加权、异质性分组或稳健性诊断, 而非直接的处理变量或结果变量。数据链路上, 逐篇置信在 stage 21 (`21_tone_llms.parquet`) 由 `tone_llms.py` 随情感标签一并落盘; 银行-年 mean_i 篇均聚合这一核心公式的真源是 `pipeline/panel/encode.py`, 其在 LLM_MODELS 循环内对 full/ctx/ss 三轨逐轨执行 `avg_{short}_conf{track} = (conf_src, 'mean')`, 聚合源列 conf_src 优先取 per-model 有效性掩码列 `_conf_valid_{short}{track}` (定义见下段); `pipeline/panel/export.py` 只负责把 encode 算好的列装配进最终面板并挂显示标签, 不参与篇均计算。三处文件各司其职, 切勿把聚合真源误记为 export.py。

【方法学与计算】
逐篇置信的产生遵循冻结 prompt 契约 (prompt_version v8, temperature=0.0), 模型在返回结构化情感判定时同时给出一个把握度字段, 经解析归一化至 [0,1] 连续区间, 数值越大表示模型对本篇极性判定越有把握。银行-年聚合采用无权算术平均, 篇均而非篇加权是为与其余情感面板列 (极性、类别占比) 的分母口径保持一致。分母口径须精确到 per-model 有效性掩码这一层: encode.py 在聚合前先对每家模型每轨物化掩码列 `_conf_valid_{short}{track} = df[{short}_sentiment_confidence{track}].where(df[{short}_score{track}].notna())`, 即只保留该模型该轨 score 判定成功 (非 <NA>) 的行的置信, 其余行置 NaN; 随后 `avg_gpt54nano_conf{track}` 以此掩码列取 'mean', pandas mean 跳过 NaN, 因此本家族篇均的实际域 = 该轨 full-only 留篇集 ∩ gpt54nano 该轨 score 有效行, 分母是这个交集的行数, 而非该轨进入情感样本的全部报道篇数。这一 per-model 掩码保证置信与其调节的同模型 `{short}_tone` 严格同口径 (只在该模型确实打出有效极性的篇上取置信均值), 避免把模型判定失败 (score=<NA>) 的篇的残留置信混入分母。掩码列缺失 (legacy parquet 或未过 encode_sentiment 的合成测试 df) 时回退 raw 物理域列 `{short}_sentiment_confidence{track}` 向后兼容。三家 (gpt54nano/gemini31/deepseekv4) 各自持有独立掩码, 逐轨、逐模型独立计算, 不借 full 轨置信、不借他家有效域。留篇门控采用 full-only 口径 (2026-06-29 铁律): 一篇报道是否算作「一篇银行金融科技报道」只看 `llm_verified_full == True`, 即以 full 轨的模型核验结果决定留篇集; ctx 与 ss 两轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但各轨的置信仍按该轨自身文本重新判定、逐轨独立计算, 不借用 full 轨的置信数值。三轨文本在 stage 14 物化: full = 标题 prepend 全文正文; ctx = 标题加实体窗口; ss = 标题加银行与金融科技同句共现窗口。ss 的回退语义镜像 ctx: 当某篇不存在银行与金融科技的同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 与 full 共享 `n_articles` 分母; 当金融科技词库缺席 (`FINTECH_AC=None`) 时优雅降级为全 fallback。

【文献定位】
把 LLM 自报置信当作一项可分析的信号, 呼应了近年对大模型置信估计与校准的系统梳理: Geng et al. (2024) 综述了大模型置信估计与校准的多种范式, 指出自报置信虽便捷但可能系统性偏高或偏低, 需谨慎当作概率解读; Gligorić et al. (2024) 进一步探讨了在标注置信不足时如何仍得出稳健结论, 为把置信当作加权或分组信号而非硬阈值提供了方法学间接支撑。置信作为分类质量代理的思路可上溯至监督学习概率校准研究: Niculescu-Mizil & Caruana (2005) 系统比较了不同学习器输出概率的可靠性, 提示原始模型分数与真实后验之间常存在偏差, 这正是本家族只把置信用作稳健性维度、不直接解读其绝对水平的依据。把新闻媒体情感当作可量化并与真实经济后果相联结的信号, 这一范式的金融学奠基工作是 Tetlock (2007): 他以媒体语调构造情感序列并实证其对市场的预测作用, 确立了「媒体文本情感 → 面板计量」的研究路径, 本项目把银行金融科技报道情感聚合为银行-年面板正沿此传统, 而 LLM 自报置信则是该传统在生成式判定阶段新增的、用于诊断情感信号可靠性的元维度。在情感判定这一具体任务上, 早期词典式意见挖掘 (Ding et al. 2008) 与随后的预训练语言模型 (Devlin et al. 2019 的 BERT, Liu et al. 2020 的 FinBERT) 奠定了从符号规则到深度表征的判定范式演进, 本项目的 LLM 三家投票是该演进在生成式模型阶段的延伸, 而置信数值则是生成式判定相较词典法与判别式 BERT 新增的一项自省信号。需强调: 置信 (conf) 与情感极性 (tone) 是两个正交构念, 高置信不等于正面, 二者在计量上分列不同 RHS。Chiu & Hung (2025, Pacific-Basin Finance Journal) 用自训练金融专用大模型对10-K文本做情感判定并驱动交易策略, 呼应本家族把生成式LLM情感判定质量(以自报置信为代理)当作可分析信号的思路; Gilardi, Alizadeh & Kubli (2023, Proceedings of the National Academy of Sciences) 系统比较大模型与人工标注在多项文本标注任务上的准确率与一致性, 为本家族用LLM自报置信刻画判定把握、并以跨模型/跨轨稳健性检验其可靠性提供了实证参照。

【口径铁律】
本家族三列同属三轨 (full/ctx/ss) 规格稳健性并排族: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨置信混进同一 over-identified Hansen J。同理, gpt54nano 与另两家 (gemini31, deepseekv4) 的同名置信列构成 per-model 跨厂商稳健性并排, 各家各自 just-identified, 亦禁混同一 over-identified Hansen J。置信不是嵌入测度, 无 co-primary 双轨 `_lg` 孪生; per-model 独立降级 — 某家缺席仅掉该家自身族, 不触发 co-primary 嵌入式的 both-or-neither 连坐。

## VAR: avg_gpt54nano_conf_ctx

【变体差分】
本列是 gpt54nano 单模型置信在 ctx (上下文实体窗口) 轨上的银行-年篇均。与家族内其余两列的唯一差别在于喂给模型的文本轨: ctx 轨的判定文本 = 标题 prepend 加实体窗口正文, 即在原文中围绕目标银行与金融科技实体提及处截取上下文窗口拼接而成, 剥离与银行金融科技主题无关的段落。因此本列的置信反映的是「模型在只看到实体邻近上下文时对情感判定的把握」, 相较 full 轨聚焦、噪声更低但可用语境更短。留篇门控仍是 full-only: 进入本列篇均分母的报道集是 full 轨核验留篇集的子集, 但每篇的 ctx 置信由 gpt54nano 对该篇 ctx 文本重新判定得到, 绝不复用 full 轨的置信。本列与 full/ss 两列各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J。本列亦与 gemini31、deepseekv4 的 ctx 置信构成 per-model 并排, 同禁混同一 Hansen J。当 ctx 文本因实体窗口无有效邻近上下文而退化时, 该篇 ctx 判定按上游降级规则处理, 逐轨独立不借 full 分母。实证使用上, 本列相对 full 轨的价值在于: 若一个基于置信的结论在 full 与 ctx 两轨上同号同量级, 则该结论不因「模型是看全文还是只看实体窗口」而改变, 从而增强测量稳健性; 反之两轨背离往往提示置信对无关语境噪声敏感, 应回到 full canonical 轨为准。置信数值的绝对水平不宜跨轨直接比较, 因为不同轨喂入的文本长度与信息密度不同, 模型的把握基线随之平移, 稳健性检验应比较标准化系数而非置信水平差。gpt54nano 是三家投票中的第一家, 单看本列不构成共识判定, 只是三家在 ctx 轨置信上的一条切片。

## VAR: avg_gpt54nano_conf_full

【变体差分】
本列是 gpt54nano 单模型置信在 full (全文) 轨上的银行-年篇均, 是本家族的 canonical 轨。full 轨判定文本 = 标题 prepend 加完整正文 body, 语境最完整、可用信息最多, 因而其置信在概念上是模型「看全文后对本篇情感把握」的直接刻画。full 轨在本项目中承担双重角色: 其一, 它自身是置信的一条测度轨; 其二, 更关键的是, 留篇门控 (2026-06-29 full-only 铁律) 正是以 full 轨的模型核验 `llm_verified_full` 决定整个银行-年情感样本的留篇集, 因此本列的分母 = 该银行-年该轨进入情感样本的报道篇数, 也就是 ctx/ss 两轨行宇宙的母集。本列与 ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J; 与另两家同名 full 置信构成 per-model 跨厂商并排, 同禁混同一 Hansen J。作为 canonical 轨, 本列通常是置信维度实证分析的首选主轨, ctx/ss 留作稳健性对照。置信绝对水平应谨慎解读为概率 (Niculescu-Mizil & Caruana 2005; Geng et al. 2024), 实证中多经标准化后比较跨模型系数, 而非直接比较各家置信的水平值。作为 canonical 轨, 本列与 gemini31、deepseekv4 的同名 full 置信是评估「情感判定质量是否稳健于模型选择」的第一手材料: 三家 full 置信同高的银行-年, 其情感信号可信度更高, 可据以做质量加权或分组稳健性; 三家背离则提示该银行-年报道文本存在判定分歧, 需谨慎解读其情感面板列。由于 gpt5.4-nano 是三家中体量最小、成本最低的一家, 其 full 置信在跨模型比较中兼具「基线模型」参照意义。留篇门控之所以钉在 full 轨而非 ctx/ss, 是因为全文语境判定最不易因窗口截断而漏判一篇真实的银行金融科技报道, 这使 full 轨的核验结果成为整个情感样本框最可靠的锚。

## VAR: avg_gpt54nano_conf_ss

【变体差分】
本列是 gpt54nano 单模型置信在 ss (银行与金融科技同句共现窗口) 轨上的银行-年篇均。ss 轨判定文本 = 标题 prepend 加银行与金融科技词在同句共现处上下 N 句窗口 (半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 拼接, 是三轨中语境最紧、最聚焦于「银行确实在谈金融科技」这一核心语义单元的轨。因此本列置信反映模型在只看到最紧密共现语境时的判定把握。ss 的回退语义严格镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, 其 ss 文本退化为全文 body, `ss_is_fallback=True`, 与 full 共享 `n_articles` 分母; 当金融科技词库缺席时 (`FINTECH_AC=None`), 该轨 `*_is_fallback` 全为 True 优雅降级。留篇门控仍是 full-only: 本列篇均分母的报道集是 full 留篇集的子集, ss 置信由 gpt54nano 对该篇 ss 文本 (或其回退全文) 独立判定, 不借 full 轨置信。本列与 full/ctx 各自 just-identified 并排, 互为稳健性、不分主次, 三轨严禁混进同一 over-identified Hansen J; 与另两家同名 ss 置信构成 per-model 并排, 同禁混同一 Hansen J。本列相对 ctx 轨更进一步收窄语境, 只保留银行与金融科技真正同句共现的片段, 因此其置信更贴近「模型对核心共现事实本身的把握」, 而非对报道整体基调的把握; 当共现片段极短、上下文信息稀薄时, 模型置信可能因证据不足而系统性偏低, 这一退化在开发期短面板 (T=2) 上尤为明显, 属预期而非缺陷。ss 与 ctx 的回退共享同一 `n_articles` 分母口径, 保证三轨篇均在同一样本框上可比。实证中若 ss 轨置信结论与 full/ctx 一致, 说明结论稳健于「语境紧到只剩共现句」这一最严苛的文本收窄, 是三轨稳健性梯子中约束最强的一档。

<!-- rendered-citations:begin -->
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics, 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv [Preprint]. https://doi.org/10.48550/arXiv.2408.15204
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics, 4171-4186. https://doi.org/10.18653/v1/N19-1423
Ding, X., Liu, B., & Yu, P. S. (2008). A holistic lexicon-based approach to opinion mining. Proceedings of the International Conference on Web Search and Web Data Mining (WSDM '08), 231-240. https://doi.org/10.1145/1341531.1341561
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Chiu, I.-C., & Hung, M.-W. (2025). Finance-specific large language models: Advancing sentiment analysis and return prediction with LLaMA 2. Pacific-Basin Finance Journal. https://doi.org/10.1016/j.pacfin.2024.102632
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
