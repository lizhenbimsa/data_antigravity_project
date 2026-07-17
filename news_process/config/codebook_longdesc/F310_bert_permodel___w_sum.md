---
family_id: F310
columns:
- fin_sent_zh_负面_w_sum_ctx
- fin_sent_zh_负面_w_sum_full
- fin_sent_zh_负面_w_sum_ss
- finbert2_负面_w_sum_ctx
- finbert2_负面_w_sum_full
- finbert2_负面_w_sum_ss
- finbert_cn_负面_w_sum_ctx
- finbert_cn_负面_w_sum_full
- finbert_cn_负面_w_sum_ss
unit: 无量纲提及密度加权和 (银行-年内 p_neg × mention_density 逐篇求和, 未除以篇数, 非原始概率和)
formula: bank-year 内某 BERT 模型对每篇文章判出的负面类概率 p_neg, 先乘以该篇的提及密度权重 mention_density (Value-weighted Exposure, 呼应 Hassan et al. 2019 QJE 的加权暴露构造), 再逐篇求和 (Σ p_neg·mention_density), 三轨×三模型独立计算, 不做篇数归一; 与未加权的原始概率和 (neg_sum 系列) 是两条并行列族
producer: pipeline\sentiment\tone_berts.py (文章级 BERT 三分类/二分类概率) ; pipeline\panel\runner.py (mention_density 加权列预计算, runner.py:751/779-783) ; pipeline\panel\codebook.py, pipeline\panel\encode.py (对已加权列 bank-year 求和聚合与列命名, encode.py:1006-1007)
upstream:
- 22_words_tone.parquet
- 23_bert_tone.parquet
citations:
- doi: "10.1145/3711896.3737219"
  type: journal
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.18653/v1/N19-1423"
  type: journal
  authors: "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K."
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1"
  pages_or_artno: "4171-4186"
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.24963/ijcai.2020/622"
  type: journal
  authors: "Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J."
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: "Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)"
  pages_or_artno: "4513-4519"
- doi: "10.1093/qje/qjz021"
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A."
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: "Quarterly Journal of Economics"
  vol: "134"
  issue: "4"
  pages_or_artno: "2135-2202"
- doi: "10.1111/jofi.13482"
  type: "journal"
  authors: "Hirshleifer, D., Mai, D., & Pukthuanthong, K."
  year: 2025
  title: "War Discourse and the Cross Section of Expected Stock Returns"
  venue: "The Journal of Finance"
  vol: "80"
  issue: "6"
  pages_or_artno: "3589-3637"
new_dois: []
---

## CORE

【构念与来源】本家族衡量的是三个独立训练的中文金融 BERT 分类器 (finbert_cn、fin_sent_zh、finbert2) 各自给出的"文章负面概率"在银行-年内的加权和, 度量的是一家银行在某一年被媒体以负面语气报道的"总量级", 而非"平均语气"。数据源头是 pipeline\sentiment\tone_berts.py (thin shim 23_tone_berts.py, always-on stage): 该阶段读入 stage 22 词典法情感分析产出的 22_words_tone.parquet, 用 config\sentiment.yaml::sentiment_analysis.tone_berts.models 配置的三个模型逐篇推理, 对超过单窗上限 (≤510 token 有效正文, 含特殊 token 后 ≤512) 的长文本用 50% 重叠的滑动窗口切片, 各窗输出的 logits 按置信度加权池化 (logits_agg = Σ conf_k·logits_k / Σconf_k) 合并为整篇的分类概率, 再对负面这一类取出概率值写入文章级 parquet。三个模型彼此独立分词 (fix g-berts-01 后不再跨词表共享 batch), 独立加载到 GPU, 独立失败降级: finbert_cn 与 fin_sent_zh 是公开 HuggingFace 模型 (strict_models=true 下加载失败会 fail-loud), finbert2 是项目自研的本地私有模型, 经 .env 的 FINBERT2_MODEL_DIR 解析, 该环境变量未设置或路径不存在时优雅跳过, 不影响另外两个模型继续产出。这解释了 finbert2 在盘上覆盖率天然低于另两模型的现象, 属预期降级而非缺陷。

【方法学与计算】"_w_sum" 是本项目 panel 层面聚合命名法里"加权和"这一档的落点, 与同源家族里出现的 _hw_sum (羊群/herd 加权和)、_mw_sum (媒体来源加权和) 是并列的加权方案, 彼此互为稳健性、不分主次, 均是把文章级负面概率在 bank-year 分组内做加权求和, 唯一区别是权重来源不同; _w_sum 取的权重是提及密度 mention_density (即该篇文章内目标银行被提及的密度), 这一权重方案在 pipeline\panel\runner.py 中预计算为 Value-weighted Exposure, 方法学上呼应 Hassan et al. (2019, Quarterly Journal of Economics) 度量企业层面政治风险暴露时采用的"按提及密度加权"思路——把一篇文章对目标实体的语气信号, 按该实体在文中被提及的相对密度做加权, 而非对每篇文章一视同仁地等权计入。这与词典法家族 F132-F134 的 score_hw_sum/score_mw_sum/score_w_sum 三兄弟同一命名逻辑, 但本家族的底层信号来自 BERT 概率而非词典打分。计算上, 对某银行在某年满足留篇门控 (llm_verified_full == True, 2026-06-29 起门控口径为 full-only) 的每篇文章, 先取该 BERT 模型输出的负面类概率 p_neg, 乘以该篇的 mention_density 权重, 得到该篇的"提及密度加权负面暴露"; 再在银行-年分组内把各篇的加权负面暴露求和, 得到一个既随篇数与语气强度、又随该银行在各篇文章中被提及密度共同放大的量级指标; 这一构造与"未加权原始概率和" (neg_sum 系列, 逐篇 p_neg 直接求和不乘 mention_density) 是两条并行且不可互相替换的列族, w_sum 额外把"该银行在文中被提及得有多密集"这一维度纳入权重, neg_sum 则是纯粹的语气量级求和; 二者与同族常见的 neg 或 net_tone 均值型指标又形成进一步互补——均值刻画"平均有多负面", (加权) 和刻画"负面报道总的分量有多大", 在识别策略上分别对应集约边际 (intensive margin) 与总量效应, 不可相互替代。三个模型 (finbert_cn 三分类含中性、fin_sent_zh 三分类、finbert2 二分类无中性类需补 NaN 占位) 在概率标度与类别粒度上并不完全一致, 因此禁止跨模型直接比较 w_sum 的绝对水平, 只应比较标准化后的系数或方向。三个文本轨道 (full=标题+全文正文, ctx=标题+银行实体窗口, ss=标题+银行与金科同句±N窗口, 回退语义镜像 ctx: 无银行∧金科同句共现时 content_ss 退化为全文 body 且 ss_is_fallback=True) 各自独立跑推理、独立聚合, 三轨与三模型构成一个 3×3 的稳健性网格, 各自 just-identified 并排, 互为稳健性、不分主次, 证明结论不被某一家模型或某一种文本范围窗口驱动, 禁止把不同模型或不同轨道的 w_sum 混入同一个 over-identified 的 Hansen J 检验。

【文献定位】三家 BERT 模型分别对应不同的技术谱系: finbert_cn (yiyanghkust/finbert-tone-chinese) 与 finbert2 都承袭自 Devlin et al. (2019) 提出的双向 Transformer 预训练范式 (BERT), finbert2 是项目组按 Xu et al. (2025, KDD '25) 描述的面向金融领域部署缺口而专门训练的双向编码器, 在金融语料上做了针对性的继续预训练与微调; fin_sent_zh 则走的是 Financial PhraseBank 迁移微调路线, 呼应 Liu et al. (2020, IJCAI) 与 Huang, Wang & Yang (2023, Contemporary Accounting Research) 关于金融专用语言模型优于通用情感词典和通用预训练模型的发现——后两篇同属英文 FinBERT 谱系的奠基性工作, 证明领域预训练模型能捕捉词典法遗漏的语境依存语气 (如反讽、条件句、复合修饰)。本家族三模型并行、互不设 ensemble headline (与 LLM 三家投票产生 llm_vote_tone 共识列不同), 是刻意的方法论选择: BERT 概率输出彼此不做投票融合, 而是作为独立的、跨模型三角验证 (Denzin 2017 方法学传统) 的稳健性证据链, 让读者能直接看到某一结论是否依赖单一模型的判别边界。本家族的加权方案本身另有独立的文献定位: _w_sum 所用的 mention_density 加权求和, 方法学上呼应 Hassan et al. (2019, Quarterly Journal of Economics) 在测度企业层面政治风险暴露时提出的 Value-weighted Exposure 思路——不把每一次文本提及一视同仁地等权计入, 而是按目标实体在该文本中被提及的相对密度加权, 使得聚合后的暴露度量能同时反映"提到了多少次""语气有多负面"两个维度的联合信息, 而非仅反映其中之一; 本家族把这一权重构造思路从"企业-政治风险暴露"迁移到"银行-媒体负面语气暴露"场景, 用同一套加权求和逻辑衡量银行在年度内被媒体负面报道的总"分量", 是本项目情感测度体系里少数直接采纳 Hassan et al. (2019) 加权暴露方法学的落点之一 (与 _hw_sum、_mw_sum 的权重来源不同, 后两者分别取羊群/herd 与媒体来源结构作为权重, 三者互为稳健性并排)。 这一加权暴露范式在近期文献另有独立的顶刊先例: Hirshleifer、Mai 与 Pukthuanthong (2025) 用半监督主题模型对跨 160 年、约 700 万篇《纽约时报》报道抽取话语主题, 逐篇得到战争话语强度并按强度 (而非等权计数) 汇总为文本暴露量, 据以构造战争因子解释预期收益截面, 表明「篇级文本强度 → 单元暴露量」的加权汇总构造在前沿是被接受的做法, 与本族按 mention_density 逐篇加权求和的口径同构, 与既有的 Hassan et al. (2019) 加权暴露谱系互为呼应而非替代。⚠ 迁移边界须写实: 原文测度的是战争话语主题暴露 (topic exposure), 无情感极性与分类概率输出, 故仅锚加权汇总这一步, 不为本族的负面概率口径本身提供依据; 其定价检验走因子模拟组合、聚合层级为市场/组合而非银行-年, 语料为美国英文新闻, 亦无 BERT per-model 并排与三轨文本范围切分。
## VAR: fin_sent_zh_负面_w_sum_ctx

【变体差分】本列取 fin_sent_zh (基于 Financial PhraseBank 微调的中文金融 BERT, 三分类含正面/负面/中性) 在 ctx 轨道 (标题+银行实体窗口正文, prepend_title 拼接) 上对每篇文章输出的负面类概率, 在银行-年分组内按基准权重方案求加权和。ctx 轨道相对 full 轨道的核心差别是只把模型的注意力预算集中在围绕目标银行实体的局部窗口文本上, 剔除全文中与该银行无关的段落, 目的是降低"整篇文章基调"对"银行相关段落基调"的稀释噪声, 尤其在长篇报道中银行只是被提及的多个主体之一时更明显, 比如一篇覆盖多家银行同业动态的综述性报道, 若不做实体窗口裁剪, 其他银行的负面事件也会污染目标银行的语气打分。ctx 与 full、ss 三轨在识别策略上各自 just-identified 并排、互为稳健性、不分主次, 不可混入同一 over-identified 的 Hansen J 检验; 三轨共享同一套留篇门控 (full-only, 即是否计入"一篇银行金科报道"只看 llm_verified_full), 因此本列的分母行集合 (哪些文章参与聚合) 与 full 轨道保持一致, 差别仅在于喂给模型的文本范围, 而非样本选取标准。ctx 轨道的窗口边界由上游 stage 14 (materialize_ctx) 物化在 content_ctx 列中, 该阶段在 stage 21 之前即完成物化, 使得 stage 15 fintech_intensity、stage 16 policy_alignment 等下游模块能在情感分析之前就消费到真三轨文本, 本列继承的正是这一套统一物化口径, 与词典法 (stage 22) 和三家大模型 (stage 21) 在同一文本切片上各自独立打分, 三条方法路线互不共享推理结果, 是本项目"情感三角验证"设计的一个具体落点: 词典法给出可解释的规则打分, LLM 给出语用推理级判断, BERT 给出神经网络的整体语气判别, 三者在同一 ctx 窗口上分别产出, 供研究者比较结论是否跨方法一致。加权和这一聚合形式本身也刻意区别于均值型的 fin_sent_zh_neg 或 net_tone 指标: 均值反映"平均负面到什么程度", 而本列反映"负面报道总量对该银行媒体环境的总压力", 两者在解释银行声誉冲击或融资成本传导渠道时对应不同的机制假说, 不可互相替代, 须在稳健性表中并列呈现。

## VAR: fin_sent_zh_负面_w_sum_full

【变体差分】本列取 fin_sent_zh 模型在 full 轨道 (标题+全文正文, 不做实体窗口裁剪) 上输出的负面类概率, 在银行-年分组内做加权求和, 是本家族三轨中的主用/canonical 轨道, 也是留篇门控的判定基准轨道 (llm_verified_full == True 才计入"一篇有效报道"; 2026-06-29 起 full-only 门控收紧, ctx/ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集)。相对 ctx/ss 两个裁剪轨道, full 轨道保留了文章的完整语境, 包括导语、背景铺垫与非银行主体段落, 因而更贴近"记者对整篇报道的总体基调", 代价是可能被与目标银行无关的段落稀释或污染。三轨互为稳健性、不分主次, 本列作为主轨在报告结果时通常置于首位, 但统计推断意义上并不优先于 ctx/ss。full 轨道文本超过单窗上限时同样走滑动窗口切片与置信度加权池化合并, 窗口重叠率固定为 50% (WINDOW_STRIDE_RATIO=0.5), 单窗有效正文上限约 510 token (含首尾特殊 token 后总长 ≤512), 因此篇幅越长的报道分窗越多, 置信度加权机制会让模型判断更笃定的窗口对整篇结论贡献更大的权重, 这是为了避免超长报道中个别噪声段落 (如引用第三方评论或无关背景资料) 主导整体判断。银行-年聚合层面, 加权和会随该银行当年被报道篇数的增加而机械增大, 因此在跨银行或跨年度比较时, 研究者通常需要同时参照同族的篇数归一化指标 (如均值型 net_tone 或 pos/neg 概率均值) 做对照, 单独使用 w_sum 更适合刻画"总曝光负面压力"这一构念, 而非"平均语气"构念, 二者互补而非替代, 应在实证设计里明确各自对应的假说与机制路径。

## VAR: fin_sent_zh_负面_w_sum_ss

【变体差分】本列取 fin_sent_zh 模型在 ss 轨道 (标题+银行与金科关键词同句±N窗口正文, N 由 config\filtering.yaml::context_window.ss_sentence_radius 控制, 默认1) 上输出的负面类概率加权和。ss 轨道是三轨中窗口最窄、判定最严的一档, 只保留银行实体与金科词汇同句共现 (或按半径扩展) 的局部文本, 用于捕捉"银行与金融科技被同时提及那一刻的语气", 是判断银行-金科关系报道基调最精准但样本覆盖最窄的口径, 与银行∧金科同句共现判据 (原语 has_bank_fintech_cooccurrence_within_radius, 与 stage 13 硬过滤共用同一族判据但参数各自独立设定) 直接对应, 因此本列尤其适合刻画"银行的金融科技相关业务本身被负面评价"这一更精细的构念, 而非泛泛的银行整体声誉。回退语义与 ctx 镜像: 若某篇文章不存在银行∧金科同句共现, content_ss 退化为全文 body 且 ss_is_fallback 标记为 True, 与 ctx 轨道共享同一 n_articles 分母, 避免因窄口径导致的样本流失, 这意味着即使某年某银行的报道大多不满足同句共现条件, 本列依然能取得非缺失值, 只是此时其文本口径实质上退化为 full 轨道的内容。ss 与 full、ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 检验; 三轨禁混同一超识别检验这条铁律尤其适用于 ss 轨道, 因为其样本构成 (回退比例) 与 full/ctx 存在系统性差异, 混用会破坏工具变量的排他性假设。

## VAR: finbert2_负面_w_sum_ctx

【变体差分】本列取 finbert2 (项目自研本地私有二分类模型, 无中性类, 呼应 Xu et al. 2025 面向金融领域部署缺口的专用双向编码器路线) 在 ctx 轨道上输出的负面类概率加权和。finbert2 是二分类 (正面/负面), 概率标度与三分类的 finbert_cn、fin_sent_zh 不完全可比, 家族内对齐时会为其补一列恒为 NaN 的中性概率占位, 但本列本身 (负面类概率) 定义清晰、口径一致, 仍可安全参与加权和聚合。finbert2 依赖 .env 的 FINBERT2_MODEL_DIR 本地路径解析, 该变量未配置或路径失效时该模型整体跳过、不产出任何列 (与另两个 HuggingFace 模型的加载失败 fail-loud 策略不同), 因此 finbert2 相关列在某些运行环境或历史快照下可能整体缺失, 这是预期的按模型独立降级, 不代表数据管道故障, 不影响 finbert_cn/fin_sent_zh 两族继续产出。ctx 轨道语义同上, 聚焦银行实体局部窗口, 剔除全文中与目标银行无关的段落再喂给 finbert2 推理。由于 finbert2 是二分类模型, 其内部决策边界 (仅在正面/负面两端之间划分) 相比三分类模型更容易把语气模糊、偏中性的报道推向某一极端, 这一结构性差异会系统性影响 w_sum 的量级与分布形状, 因此在跨模型稳健性表中比较 finbert2_负面_w_sum_ctx 与另两模型对应列时, 应优先关注方向 (符号) 与显著性是否一致, 而非绝对数值大小, 且应在稳健性附注中明确交代二分类与三分类模型结构差异这一警示, 避免读者误读为模型间量级可比。

## VAR: finbert2_负面_w_sum_full

【变体差分】本列取 finbert2 模型在 full 轨道上输出的负面类概率加权和, 是 finbert2 这一模型分支里的主轨/留篇门控判定轨道, 语义与 fin_sent_zh_负面_w_sum_full、finbert_cn_负面_w_sum_full 平行, 三个模型的 full 轨道彼此 co-equal、互为稳健性, 不设跨模型的 ensemble/共识 headline (这与 LLM 三家投票会产出 llm_vote_tone 共识列的做法不同, BERT 三模型刻意不做融合, 让读者直接看到各模型独立结论)。finbert2 作为二分类模型天然没有中性判断, 其负面概率与三分类模型的负面概率在数值分布形状上可能系统性不同 (例如二分类倾向把模糊语气推向两端), 因此跨模型比较务必用标准化后的回归系数而非原始 w_sum 水平值。本列在完整文本上推理, 是 finbert2 分支覆盖率最高、样本量最大的一列 (相对 ctx/ss 两个受实体窗口或同句判据约束的裁剪轨道), 在 FINBERT2_MODEL_DIR 配置有效的运行环境下, 该列应与 finbert2 的其余两轨同时存在或同时缺失, 属于模型层面的整体降级而非按轨道分别降级; 换言之, 若本列在某次快照中缺失, finbert2_负面_w_sum_ctx 与 finbert2_负面_w_sum_ss 也应同时缺失, 这是判断该次快照是否处于"finbert2 本地模型未配置"状态的一个诊断线索。

## VAR: finbert2_负面_w_sum_ss

【变体差分】本列取 finbert2 模型在 ss 轨道 (银行∧金科同句±N窗口, 回退语义镜像 ctx) 上输出的负面类概率加权和, 是本家族里覆盖率最窄、也最容易受 finbert2 本地模型可用性影响的一列: 只有当 (a) FINBERT2_MODEL_DIR 配置有效且模型成功加载, 且 (b) 该银行-年确有文章落入 ss 轨道的同句窗口判定 (或经回退语义计入全文), 该列才会有非缺失值。与 fin_sent_zh_负面_w_sum_ss、finbert_cn_负面_w_sum_ss 三者互为稳健性并排, 但因 finbert2 独立降级机制, 其缺失模式与另两模型不同源, 分析时应对该列的缺失单独做敏感性说明, 不可默认其缺失机制与另两模型一致。回归实证中若需报告 finbert2 分支的 ss 轨道结果, 建议同时列出该轨道当期的有效篇数 (即未回退到 full 的篇数占比), 以说明该系数是在多窄的样本口径上估计出来的, 避免因样本极小而对系数稳健性做过度解读。此外, finbert2 二分类的固有特性 (无中性缓冲区) 叠加 ss 轨道最窄的窗口, 使得本列在少篇幅样本下的负面概率更容易出现两端极化, 建议与同轨道的 finbert_cn/fin_sent_zh 三分类结果并列展示, 便于读者判断极化是模型结构所致还是文本本身语气确实强烈。

## VAR: finbert_cn_负面_w_sum_ctx

【变体差分】本列取 finbert_cn (yiyanghkust/finbert-tone-chinese, HuggingFace 公开三分类模型, 谱系上承袭 Devlin et al. 2019 的 BERT 预训练范式并在金融文本上继续微调) 在 ctx 轨道上输出的负面类概率加权和。finbert_cn 与 fin_sent_zh 同属公开可复现的三分类 HuggingFace 模型, 在 strict_models=true 默认配置下若加载失败会直接 fail-loud 中止阶段 (而非静默跳过), 因此这两个模型的列在正常运行下应始终齐备, 覆盖率不受 .env 私有路径配置影响, 与 finbert2 的降级机制形成对照。ctx 轨道语义同上: 只把银行实体附近窗口内的文本喂给模型推理, 剔除全文中与目标银行无关的段落, 降低长报道中多主体混杂带来的语气稀释噪声。finbert_cn 的训练语料本身即以"finbert-tone"命名, 提示其预训练目标就是金融文本的整体语调判别, 相比通用领域预训练模型天然更贴合本项目"银行媒体语调"这一构念, 是三模型中方法学定位最接近词典法 tone_words 直觉 (整体基调判别) 的一支, 但底层机制是神经网络端到端学习而非人工词表, 二者互为方法学对照。ctx 轨道下 finbert_cn 的推理输入与 fin_sent_zh 完全共用同一份 content_ctx 物化文本 (由 stage 14 统一产出), 二者差别纯粹来自模型权重与训练语料不同, 这使得 finbert_cn_负面_w_sum_ctx 与 fin_sent_zh_负面_w_sum_ctx 之间的差异可以被干净地归因为"模型差异"而非"输入文本差异", 是本项目跨模型三角验证设计里控制变量最干净的一对比较。

## VAR: finbert_cn_负面_w_sum_full

【变体差分】本列取 finbert_cn 模型在 full 轨道上输出的负面类概率加权和, 是 finbert_cn 这一模型分支的主轨/留篇门控判定轨道。finbert_cn 是三模型中训练语料最贴近通用金融新闻语调 (finbert-tone) 的一支, 三分类粒度 (正面/负面/中性) 与 fin_sent_zh 对齐, 便于二者之间做同粒度的跨模型交叉验证; 与 finbert2 的二分类比较则需留意类别数不同带来的标度差异。本列与 fin_sent_zh_负面_w_sum_full、finbert2_负面_w_sum_full 三者 co-equal 互为稳健性、不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J。作为公开可复现的 HuggingFace 模型, finbert_cn 在 full 轨道上的推理结果不依赖任何私有路径配置, 是三模型中最适合作为跨机构复现基准的一列: 只要复现者能连上 HuggingFace 或已有本地缓存并设置 HF_HUB_OFFLINE=1/TRANSFORMERS_OFFLINE=1, 即可复现相同权重下的推理结果, 这也是本项目在 manuscript 稳健性附注中经常优先展示 finbert_cn 结果的实际原因之一——并非其构念优先级更高, 而是可复现门槛最低。full 轨道下 finbert_cn 与另两模型共用同一份 prepend_title 拼接后的标题+全文文本, 三者的差异同样可以纯粹归因于模型本身, 这条 full 轨道也是留篇门控判定 (llm_verified_full) 的基准轨道, 因此 finbert_cn_负面_w_sum_full 的行集合与 fin_sent_zh_负面_w_sum_full、finbert2_负面_w_sum_full 三者理论上完全一致 (仅 finbert2 因模型本身缺席才产生额外缺失), 便于研究者做严格意义上的同样本跨模型对照回归。

## VAR: finbert_cn_负面_w_sum_ss

【变体差分】本列取 finbert_cn 模型在 ss 轨道 (银行∧金科同句±N窗口, 回退语义镜像 ctx, 共享 n_articles 分母) 上输出的负面类概率加权和。作为三模型中覆盖率最稳定的一支 (公开模型、fail-loud 而非优雅跳过) 在最窄文本窗口下的取值, 本列适合用作"finbert2 若因本地模型不可用而缺失时"的替代稳健性参照, 但仍应视为独立并排的一支证据, 而非 finbert2 的直接替代品——三模型架构、训练语料与类别粒度均不同, 结论一致时才构成真正的跨模型三角验证。ss 轨道回退语义下, 部分银行-年的本列取值实质来自全文文本 (ss_is_fallback=True 的情形), 此时其与 full 轨道的相关性会机械升高, 这是解读该列与 full 轨道相关系数时需要考虑的结构性因素, 不应简单等同于"模型判断在两个窗口上高度一致"的证据; 只有在剔除回退样本后仍观察到 full 与 ss 高度相关, 才是真正意义上的跨窗口稳健性证据。由于 finbert_cn 在三模型中覆盖率最完整, 该列常被用作检验"ss 轨道回退比例是否影响结论"这一稳健性问题的首选模型: 研究者可以对比 finbert_cn 在 ss 全样本 (含回退) 与仅严格同句共现子样本 (剔除回退) 两种口径下的估计系数是否方向一致, 这一比较本身即是判据敏感性的一种具体实现, 与 CLAUDE.md 所述"判据后缀 ≠ 三轨文本后缀"的铁律相呼应, 判据主体 (银行∧银行结构指标的三判据) 与本处的三轨文本口径是两套并行但不同的稳健性维度, 不应混淆。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1, 4171-4186. https://doi.org/10.18653/v1/N19-1423
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Hirshleifer, D., Mai, D., & Pukthuanthong, K. (2025). War Discourse and the Cross Section of Expected Stock Returns. The Journal of Finance, 80(6), 3589-3637. https://doi.org/10.1111/jofi.13482
<!-- rendered-citations:end -->
