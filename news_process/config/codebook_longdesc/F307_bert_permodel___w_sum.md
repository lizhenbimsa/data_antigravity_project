---
family_id: F307
columns:
  - fin_sent_zh_正面_w_sum_ctx
  - fin_sent_zh_正面_w_sum_full
  - fin_sent_zh_正面_w_sum_ss
  - finbert2_正面_w_sum_ctx
  - finbert2_正面_w_sum_full
  - finbert2_正面_w_sum_ss
  - finbert_cn_正面_w_sum_ctx
  - finbert_cn_正面_w_sum_full
  - finbert_cn_正面_w_sum_ss
unit: 无量纲加权概率总和 (value-weighted 正面概率和; 归一化前的分子中间量)
formula: "{model}_正面_w_sum_{track} = Σ_{i∈bank-year} ({model}_正面_i,{track} × mention_density_i); 下游除以 sum_mention_density_{track} 得 {model}_pos_vw_{track} (不在本家族)"
producer: news_process/pipeline/panel/encode.py::build_bank_year_panel (聚合); news_process/pipeline/sentiment/tone_berts.py (文章级概率来源)
upstream:
  - 22_words_tone.parquet (content_full/content_ctx/content_ss)
  - 23_bert_tone.parquet ({model}_正面_{track} 文章级概率, mention_density)
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
- doi: 10.1145/3711896.3737219
  type: wp
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: 5117-5128
- doi: 10.18653/v1/N19-1423
  type: wp
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019), Volume 1"
  pages_or_artno: 4171-4186
- doi: 10.24963/ijcai.2020/622
  type: wp
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: "Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)"
  pages_or_artno: 4513-4519
- doi: 10.1007/978-3-030-32381-3_16
  type: wp
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science"
  vol: 11856
  pages_or_artno: 194-206
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
- doi: "10.1016/j.ememar.2024.101234"
  title: "Does official media sentiment matter for the stock market? Evidence from China"
  authors: "Xu, Z., Hua, X., & Zhang, T."
  year: 2025
  venue: "Emerging Markets Review"
  type: "journal"
new_dois:
  - "10.1002/isaf.1549"
  - "10.1016/j.ememar.2024.101234"
---

## CORE

【构念与来源】
本家族承载三个中文金融 BERT 模型 (fin_sent_zh / finbert2 / finbert_cn) 在"正面"类别上的 value-weighted (VW) 概率总和, 三轨 (full/ctx/ss) 各一列, 共 3 模型 × 3 轨 = 9 列。它是 stage 40 bank-year 面板构造过程中的一个中间加总量, 而非最终归一化的语调指标: 数据来自 stage 23 (`23_bert_tone.parquet`), 该阶段对 stage 22 (`22_words_tone.parquet`) 输出的三轨文本 (`标题+content_full`/`content_ctx`/`content_ss`, prepend_title 拼接) 分别喂给三个独立训练的中文金融 BERT 分类器做文章级推理, 得到每篇文章在"正面"类别上的 softmax 概率 (finbert_cn/fin_sent_zh 为 3 分类, finbert2 为 2 分类, 均含"正面"标签)。stage 40 聚合时把该文章级概率乘以 `mention_density` (文章内目标银行提及密度权重, 沿用"按相关密度加权而非简单等权平均"这一在企业层面文本度量文献中常见的加权方案) 后在 bank-year 内求和, 即得到本家族列。

【方法学与计算】
公式为 `{model}_正面_w_sum_{track} = Σ_{i∈bank-year} ({model}_正面_i,{track} × mention_density_i)`, 其中 i 遍历该 bank-year 单元内所有满足留篇门控的文章, `{model}_正面_i,{track}` 是模型对第 i 篇文章某轨文本给出的正面概率 (值域 [0,1]), `mention_density_i` 是该文章的目标银行提及密度权重 (非负实数, 提及越集中权重越大)。求和后的量纲取决于样本文章数与权重规模, 本身不是概率或比率——它是构造下游 value-weighted 语调指标的分子中间量: 面板构造函数在算出本列后立即用同一 bank-year 单元的 `sum_mention_density_{track}` (mention_density 在该单元内的总和) 去除, 得到 `{model}_pos_vw_{track}` (VW 正面概率, 该列不在本家族, 属另一家族)。之所以把分子与分母的除法拆成两步 (先落地 `_w_sum` 再在下游做除法), 是为了让分子本身也可审计、可复用 (例如与 `_负面_w_sum` 联合构造 net-tone VW 版本), 并与 LLM 三家、词典六家的同款 `_score_w_sum` 加权求和范式保持结构一致 (`pipeline/panel/encode.py` 同一循环内并列产出)。计算发生在文章级推理之后、bank-year groupby-agg 阶段, 用 pandas 的 `('col', 'sum')` 聚合原语实现, 不涉及额外的模型推理或 API 调用, 是纯后处理的确定性算术。三个模型彼此独立训练、独立推理、独立聚合, 不共享参数或分词器 (fix g-berts-01 修复了历史上按 `max_length` 分组导致的跨词表 token id 错配问题, 修复后不同词表模型不再共享分词批次), 因此三模型的 `_w_sum` 数值层不可直接跨模型比较水平 (不同模型的 softmax 概率分布形状不同), 只适合各自与对应的语调水平指标 (`{model}_pos_vw_{track}`) 或组内跨模型标准化后的一致性统计联用。
文章级"正面"概率在遇到超长文本时经过滑动窗口切片 (窗口重叠比例 50%, 单窗 ≤512 token 含特殊符号) 与置信度加权池化合并各窗 logits 后取 softmax, 因此即便原文远超模型单次可处理长度, 每篇文章仍得到一个稳定的正面概率估计, 该估计随后原样进入本家族的加权求和。推理失败 (哨兵 `{model}_infer_failed_{track}=True`) 的文章其正面概率为 NaN, 参与 pandas `sum` 聚合时被自动跳过 (不计入分子也不应计入分母), 与"空文本"(`bert_num_windows=0`) 情形区分对待。

【文献定位】
本家族方法学根基有二: 一是 BERT 架构本身 (Devlin et al., 2019), 双向 Transformer 编码器通过掩码语言建模预训练, 微调后在文本分类任务 (含金融文本情感三分类) 上取得当时最优表现, 为后续所有领域微调 BERT 变体奠定基础; Sun et al. (2019) 系统评估了微调 BERT 用于文本分类的各类超参数与层选取策略, 为 finbert_cn/fin_sent_zh 这类"通用 BERT 权重 + 领域语料微调"路线提供操作规范。二是金融领域专用化: Liu et al. (2020) 的 FinBERT 首次系统展示了在金融语料上继续预训练/微调 BERT 能显著提升金融文本情感分类效果; Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 进一步把这一思路系统化并在会计与金融文本抽取任务上做出顶刊级验证, 是本项目采用"预训练语言模型作情感打分器"这一测度路线的方法学锚点; finbert2 模型本身直接对应 Xu et al. (2025) 在 KDD '25 上发表的 FinBench2 双向编码器, 针对中文金融部署场景专门优化, 是本项目三 BERT 之一的原始出处。value-weighted 加权求和的设计思路是让提及目标银行更集中、信号更强的文章在聚合语调中占更大权重, 而非对该 bank-year 单元内所有文章简单等权平均, 这类"按相关密度加权"的构造在企业层面文本度量文献中已有先例; 这一权重构造与本项目 LLM 三家、词典六家的 `_score_w_sum` 加权求和范式共享同一原语, 三条独立测度路线 (LLM/词典/BERT) 因此在"是否加权"这一维度上保持结构对称, 便于跨路线做 value-weighted vs. equal-weighted 的稳健性对照。
需要强调的是: 本列是中间分子, 不是可直接解读的语调水平指标; 三模型 (finbert_cn/fin_sent_zh/finbert2) 之间互为稳健性、不分主次 (无 ensemble headline, 与 LLM 三家的多数投票共识 `llm_vote_tone` 设计不同), finbert2 因依赖本地私有权重 (`.env` 配置 `FINBERT2_MODEL_DIR`) 在该配置缺失时会优雅跳过, 仅该模型自身相关列 (含本家族 finbert2 三列) 整体降级为缺失, 不影响另外两个基于公开 HuggingFace 权重的模型继续产出。凡涉及跨模型比较, 必须各模型各自 just-identified 并排、互为稳健性、不分主次, 禁止把三模型 (或同模型三轨) 混入同一个 over-identified 的 Hansen J 过度识别检验, 这是与三轨文本架构、co-primary 双轨嵌入、政治词权重梯度同款的项目铁律, 目的在于防止把本质上互为稳健性替代的多个测度错误地当作可联合矩条件叠加的多工具变量使用。BERT 深层模型相较词典法在情感判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担情感分类主力提供了顶刊层级的方法学背书。此外, Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融领域文本情感分析文献并展望未来方向, 为本家族采用 BERT 类模型作情感打分器的路线提供近期文献坐标; Xu, Hua & Zhang (2025, Emerging Markets Review) 构建基于文本分析与 BERT 的中国官方媒体情感指数并检验其对股市的影响, 为中文金融 BERT 情感打分在中国市场语境下的应用提供近期实证支持。

## VAR: fin_sent_zh_正面_w_sum_ctx

【变体差分】
本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的中文金融 3 分类 BERT: 中性/正面/负面) 在 ctx 轨的正面概率 value-weighted 求和。ctx 轨的输入文本是"标题 + content_ctx"(标题 prepend 后接实体上下文窗口), content_ctx 由 stage 14 `ctx_materializer` 物化, 语义是围绕目标银行实体的截取窗口而非全文, 相比 full 轨更聚焦于银行相关段落、剔除文章中与目标银行无关的段落噪声。留篇门控采用 full-only 口径 (2026-06-29 起): 是否判定"一篇银行金科报道"只看 `llm_verified_full==True`, ctx 轨的行宇宙是 full 轨留篇集合的子集, 本列的 per-track 求和照算但不参与是否留篇的裁定。ctx 轨与 full/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁止混入同一 over-identified Hansen J 检验; 三轨差异反映的是"全文语境 vs. 实体局部语境"对同一模型正面概率打分的敏感性, 本列数值若与 full 轨系统性偏离, 提示该模型对上下文窗口大小较敏感, 是稳健性叙事的重要观测点而非测量误差。权重来源 mention_density 与轨道无关, 是逐篇属性, 三轨共享同一权重口径, 差异只体现在被加权求和的正面概率本身。本列不涉及阈值判据或滞后设定, 是家族 canonical 结构 (模型×轨道×w_sum) 在 ctx 轨、fin_sent_zh 模型上的直接实例, 与 full 轨版本相比是同一模型换了输入文本窗口, 与 finbert_cn/finbert2 的 ctx 轨版本相比是同一文本窗口换了打分模型, 两个维度 (模型选择、轨道选择) 相互正交、各自贡献独立的稳健性证据。

## VAR: fin_sent_zh_正面_w_sum_full

【变体差分】
本列 = fin_sent_zh 模型在 full 轨的正面概率 value-weighted 求和, 是家族内该模型的 canonical 轨道版本。full 轨输入文本是"标题 + content_full"(标题 prepend 后接文章全文正文, 原始"内容"列不做截断), 是三轨中信息量最完整、也是留篇门控唯一依据的轨道 (2026-06-29 起 stage 21 是否判为一篇有效银行金科报道仅看 full 轨 LLM 验证结果, `run_pipeline_function.py::_stage21_skip_is_compatible` 与 `tone_llms.py::df_filtered` 两处门控副本须同步)。因此本列的样本行宇宙 (bank-year 单元内哪些文章参与求和) 是 ctx/ss 两轨的超集口径来源, ctx/ss 轨在同一 bank-year 单元内只会是 full 轨样本的子集或对齐子集, 不会引入 full 轨之外的额外文章。full 轨与 ctx/ss 轨在方法学地位上互为稳健性、不分主次, 并非"full 是主测度、ctx/ss 是补充"这一层级关系——是否命名为 canonical 仅描述其在留篇门控中的特殊角色, 不改变三轨各自 just-identified 并排、禁混同一 over-identified Hansen J 的铁律。fin_sent_zh 是三 BERT 模型中基于 Financial PhraseBank 微调的一支, 与另外两模型 (finbert_cn 偏通用中文金融语料微调、finbert2 为项目自研双向编码器) 在预训练语料与微调目标上均不同, 三者的正面概率分布形状因此天然存在差异, 本列的数值水平不应直接与 finbert_cn_正面_w_sum_full / finbert2_正面_w_sum_full 相比较, 只适合观察三者是否在方向上 (随时间、随银行) 保持一致, 作为跨模型三角验证的一个环节。

## VAR: fin_sent_zh_正面_w_sum_ss

【变体差分】
本列 = fin_sent_zh 模型在 ss 轨的正面概率 value-weighted 求和。ss 轨的输入文本是"标题 + content_ss", content_ss 是银行与金科词严格同句共现 (±N 句窗口, 默认 N=1 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 窗口内的文本, 是三轨中语境最紧凑、判定口径最严的一支; ss 判定原语与 stage 13 共现硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` 是不同函数、不同口径 (stage 13 是文章级硬过滤丢行, ss 轨的同句判据是句子级抽取, 二者刻意不复用)。ss 轨回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 退化为全文 body、`ss_is_fallback=True`, 该情形下本列对该篇文章的贡献与 full 轨等价 (但被加权求和的是 ss 轨模型打分, 非直接复用 full 轨数值), 分母 (`n_articles`) 与 ctx 轨共享同一回退计数口径。ss 轨与 ctx/full 两轨互为稳健性、不分主次, 各自 just-identified 并排、禁混同一 over-identified Hansen J。若上游 `FINTECH_AC` 未初始化 (`FINTECH_AC=None`), ss 轨 (以及 ctx 轨) 的 `*_is_fallback` 全体退化为 True, 相当于 ss/ctx 两轨优雅退化为 full 轨的重复, 此时三轨数值趋同不代表模型稳健, 而是上游配置缺失的信号, 审计时须先核实 `FINTECH_AC` 是否正常加载再解读三轨差异。fin_sent_zh 在 ss 轨的打分行为同样受该模型基于 Financial PhraseBank 微调这一语料出身影响: 同句共现窗口通常比 ctx 窗口更短、语气信号更集中, 若该模型对短句语境的正面判断存在系统性偏移, 会在 ss 轨与 full/ctx 两轨之间形成可观测的差异, 这正是保留三轨并排而非只跑单轨的价值所在。

## VAR: finbert2_正面_w_sum_ctx

【变体差分】
本列 = finbert2 模型 (项目自研的中文金融专用双向编码器, Xu et al. 2025 KDD '25, 2 分类负面/正面) 在 ctx 轨的正面概率 value-weighted 求和。finbert2 与另外两个基于 HuggingFace 公开权重的模型不同, 依赖本地私有模型目录 (`.env` 中 `FINBERT2_MODEL_DIR` 指向), 若该环境变量未设置或路径不存在, stage 23 会对 finbert2 整体优雅跳过 (另外两个 HF 模型照常推理), 此时本列 (以及 finbert2_正面_w_sum_full/_ss 及所有 finbert2 系列面板列) 整体缺失, 属于"per-model 独立降级", 不牵连 finbert_cn/fin_sent_zh 两个模型的产出, 也不影响其余家族列的可用性。finbert2 是 2 分类模型 (仅负面/正面, 无中性标签), 因此其"正面"概率与 finbert_cn/fin_sent_zh 两个 3 分类模型的"正面"概率在概率质量分配上存在结构性差异 (2 分类模型的正面概率天然更接近 0/1 两端, 3 分类模型的正面概率因需与中性类别分享概率质量而更居中), 这是三模型互为稳健性设计中预期且刻意保留的异质性, 不应被误读为某一模型"打分更极端因而更不可靠"。ctx 轨语义 (标题+实体上下文窗口) 与其余两模型的 ctx 轨完全一致, 三模型在同一轨道下的差异纯粹来自模型本身, 便于做跨模型一致性检验 (如 Cohen's κ、Krippendorff's α, 参见 `tone_validation.py`)。finbert2 在 ctx 轨的推理同样经过滑动窗口切片与置信度加权池化处理超长实体窗口文本, 与 full/ss 两轨共享同一套窗口切分与合并算法, 差异仅来自被切分的原始文本内容不同 (ctx 轨截取的是实体附近段落而非全文), 因此本列与 finbert2_正面_w_sum_full 之间的数值差异可以完整归因于"上下文窗口范围"这一单一维度, 不掺杂推理算法层面的额外自由度。

## VAR: finbert2_正面_w_sum_full

【变体差分】
本列 = finbert2 模型在 full 轨 (标题+全文正文, 留篇门控唯一依据轨) 的正面概率 value-weighted 求和, 是 finbert2 在家族内的 canonical 轨道版本。因 finbert2 为项目私有微调模型, 其在 full 轨上的表现是判断"是否值得纳入生产环境的稳健性支柱"的关键观测点——若 `FINBERT2_MODEL_DIR` 配置有效, full 轨样本行宇宙与 fin_sent_zh_正面_w_sum_full / finbert_cn_正面_w_sum_full 严格对齐 (同一留篇集合), 三者可在此轨道上做逐篇正面概率的直接相关性/一致性比较, 这是跨模型三角验证 (方法学意义上的多信息源三角互证, 本项目落地为多模型三角验证) 最主要的落点轨道。若 finbert2 因配置缺失而整体降级, full 轨的跨模型一致性检验会退化为仅 finbert_cn 与 fin_sent_zh 两家, 报告中须显式披露 finbert2 的可用性状态, 不得静默按两模型结果冒充三模型稳健性证据。本列与 fin_sent_zh_正面_w_sum_full/finbert_cn_正面_w_sum_full 在轨道选择、权重口径 (mention_density 加权) 上完全对齐, 唯一差异是打分模型, 是家族内"模型维度"稳健性梯子上最纯净的一组对照。finbert2 作为项目自研模型, 其 full 轨结果也是校验"自研模型是否与公开模型方向一致"这一质量保证问题的第一手材料——若 finbert2_正面_w_sum_full 与另外两模型在 bank-year 层面的相关方向长期背离, 应优先怀疑自研模型的微调数据或标签口径, 而非默认公开模型更权威; 三模型的地位是平等的互为稳健性关系, 不存在事先假定的"更可信"一方。

## VAR: finbert2_正面_w_sum_ss

【变体差分】
本列 = finbert2 模型在 ss 轨的正面概率 value-weighted 求和, 语境窗口为银行∧金科严格同句共现片段 (回退时退化为全文, 语义镜像 ctx 轨)。与该模型的 ctx/full 两轨同受"per-model 独立降级"约束: `FINBERT2_MODEL_DIR` 缺失时本列连同 finbert2 全部面板列一并缺席, 不产生部分轨道可用、部分轨道不可用的不一致状态 (降级发生在模型加载层, 而非逐轨道分别判定)。ss 轨在三轨中样本量通常最受限 (同句共现是最严判据, 命中率低于 ctx 的实体窗口判据), finbert2 的 ss 轨正面概率 value-weighted 求和因此在小样本 bank-year 单元内更容易受个别文章打分波动的影响, 解读时应结合该单元的 `n_articles_for_ss_independence` (真同句共现文章绝对数, 与回退计数区分) 一并核对, 避免把样本稀疏导致的数值跳动误读为模型对紧凑语境的系统性判断差异。ss 轨与 finbert_cn/fin_sent_zh 对应列共享同一同句判据与回退口径, 差异同样只来自打分模型本身。finbert2 的私有权重意味着其推理不依赖外网 HuggingFace Hub, 本机重跑不受 `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE` 环境变量约束 (该约束仅针对 finbert_cn/fin_sent_zh 两个 HuggingFace 托管模型), 但仍需保证 `FINBERT2_MODEL_DIR` 指向的本地目录在重跑机器上可访问, 否则同样触发优雅跳过, 三轨 (含本列) 一并缺失。

## VAR: finbert_cn_正面_w_sum_ctx

【变体差分】
本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, HuggingFace 公开权重, 3 分类中性/正面/负面, 面向中文金融文本语调打分微调) 在 ctx 轨的正面概率 value-weighted 求和。finbert_cn 与 fin_sent_zh 同为 HuggingFace 公开模型、同为 3 分类结构, 但预训练/微调语料来源不同 (finbert_cn 面向更广义的中文金融语调, fin_sent_zh 基于 Financial PhraseBank 微调), 二者在具体新闻语料上的正面概率打分不必然一致, 这正是设立三模型互为稳健性框架 (而非只用单一模型) 的动机——不同模型对同一篇文章的"正面"判断可能出现分歧, 只有当核心结论 (如 bank-year 语调随时间/随事件的变化方向) 在三模型上都稳健成立时才具有更强的说服力。ctx 轨语义 (标题+实体上下文窗口) 与本家族其余两模型的 ctx 轨列共享同一窗口物化来源 (`content_ctx`, stage 14 产出), finbert_cn 的 strict_models 默认配置下若该模型加载失败会 fail-loud 直接 raise (不像 finbert2 缺配置时的优雅跳过), 因此在生产环境中若观测到本列缺失, 通常意味着上游存在需要排查的异常 (而非预期的可选降级), 应先查 `logs/23_tone_berts.log` 定位原因。finbert_cn 的分词器与词表在项目预处理阶段被单独加载 (不与 fin_sent_zh 共享, fix g-berts-01 修复了历史上按 `max_length` 分组导致的跨词表 token id 错配问题), 因此本列所依赖的文章级正面概率是在独立分词、独立批处理流水线下产生的, 与另外两模型互不干扰, 三模型并行加载到同一 GPU 上以消除串行加载/卸载开销, 但推理逻辑彼此隔离。

## VAR: finbert_cn_正面_w_sum_full

【变体差分】
本列 = finbert_cn 模型在 full 轨的正面概率 value-weighted 求和, 是该模型在家族内的 canonical 轨道版本, 样本行宇宙与留篇门控 (`llm_verified_full==True`) 直接对齐。finbert_cn 作为最早被引入项目的 BERT 打分器之一 (与 fin_sent_zh 同属公开权重、strict 加载), 其 full 轨结果是三模型跨模型一致性检验的基准对照之一: 与 fin_sent_zh_正面_w_sum_full 比较可评估"同为 3 分类公开模型、不同微调语料"对正面判断的影响; 与 finbert2_正面_w_sum_full 比较 (在 finbert2 可用时) 可评估"3 分类 vs. 2 分类""公开权重 vs. 私有专用模型"两个维度叠加的差异。三者在 full 轨上均按同一 mention_density 权重口径求和, 差异完全来自模型本身的打分行为, 不掺杂轨道或权重构造上的额外自由度, 是本家族设计上"控制变量最干净"的一组跨模型对照点。finbert_cn 的 3 分类结构 (中性/正面/负面) 意味着本列的正面概率与其"负面"对应列 (`finbert_cn_负面_w_sum_full`, 不在本家族) 之和一般小于该 bank-year 单元的 `sum_mention_density_full`, 差额对应"中性"类别概率的加权求和; 这一点与 finbert2 (2 分类, 正面+负面理论上恰好构成完整概率质量) 存在结构性差异, 在做三模型净语调 (net_tone = pos−neg) 横向比较时应留意这一分类粒度差异, 相关净语调列另有独立家族承载, 本列仅是其中的正面侧分子中间量。

## VAR: finbert_cn_正面_w_sum_ss

【变体差分】
本列 = finbert_cn 模型在 ss 轨的正面概率 value-weighted 求和, 语境为银行∧金科严格同句共现窗口 (回退语义与 ctx 轨镜像: 无同句共现时 `content_ss` 退化为全文, `ss_is_fallback=True`)。作为三模型中唯一同时具备"公开权重"与"strict fail-loud 加载"两个特征的模型 (finbert2 私有可选降级、fin_sent_zh 公开但语料来源不同), finbert_cn 的 ss 轨结果在项目日常回归验证中承担"若本列缺失即视为异常需排查"的角色, 与另外两模型允许的合理缺失情形 (finbert2 未配置本地目录) 有本质区别。ss 轨判据与全部同族列共享 `config/filtering.yaml::context_window.ss_sentence_radius` 控制的窗口半径, 该键与 stage 13 共现硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个独立配置项, 互不联动, 调整其中一个不会自动改变另一个的行为。本列与 fin_sent_zh_正面_w_sum_ss / finbert2_正面_w_sum_ss (可用时) 一起构成 ss 轨上的三模型正面概率加权求和对照组, 三者各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。finbert_cn 因 strict 加载要求, 是三模型中在 ss 轨样本稀疏场景下最不容易出现"模型层面整体缺失"的一支 (缺失只会因该 bank-year 单元本身没有满足留篇门控且同句共现的文章而自然为 NaN, 不会因模型加载失败而系统性缺席), 因此在跨模型交叉核验中, finbert_cn 常被用作判断某 bank-year 单元 ss 轨样本是否本就稀薄 (而非模型故障) 的参照对象: 若 finbert_cn 与 fin_sent_zh 在同一单元同时缺失该列, 大概率是该单元确实没有同句共现文章, 而非某一模型单独出问题。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019), Volume 1 No. 4171-4186 [Working Paper]. https://doi.org/10.18653/v1/N19-1423
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20) No. 4513-4519 [Working Paper]. https://doi.org/10.24963/ijcai.2020/622
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science No. 194-206 [Working Paper]. https://doi.org/10.1007/978-3-030-32381-3_16
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Xu, Z., Hua, X., & Zhang, T. (2025). Does official media sentiment matter for the stock market? Evidence from China. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
