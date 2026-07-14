---
family_id: F301
columns:
- fin_sent_zh_pos_sum_ctx
- fin_sent_zh_pos_sum_full
- fin_sent_zh_pos_sum_ss
- finbert2_pos_sum_ctx
- finbert2_pos_sum_full
- finbert2_pos_sum_ss
- finbert_cn_pos_sum_ctx
- finbert_cn_pos_sum_full
- finbert_cn_pos_sum_ss
unit: 无量纲得分 (bank-year 内文章级正面概率之和, 值域下界为零、上界随当年报道篇数增长)
formula: 单篇正面标签概率 (softmax 输出) 逐窗置信度加权池化得到文章级 pos 概率, 再按 bank-year × 轨道 × 模型对全部文章求和
producer: pipeline\sentiment\tone_berts.py ; pipeline\panel\codebook.py
upstream:
- 22_words_tone.parquet
citations:
- doi: "10.1145/3711896.3737219"
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.18653/v1/N19-1423"
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)"
  pages_or_artno: "4171-4186"
- doi: "10.24963/ijcai.2020/622"
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: "Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)"
  pages_or_artno: "4513-4519"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"某一个中文金融 BERT 模型在某一篇报道里读出的正面语气有多强, 累加到银行-年这个单位上有多大总量"。它属于情感三条路线 (大模型投票、词典打分、BERT 神经网络) 里的第三条, 而在 BERT 这条路线内部又进一步拆到三个独立模型: finbert_cn (yiyanghkust/finbert-tone-chinese, 面向通用中文金融文本训练的三分类模型, 输出正面/负面/中性三个概率)、fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的三分类模型) 与 finbert2 (项目自有的私有微调模型, 二分类, 只输出正面/负面, 经 `.env` 的 `FINBERT2_MODEL_DIR` 解析本地权重路径; 该变量未配置或路径失效时该模型优雅跳过, 另两个基于 HuggingFace Hub 的公开模型照常运行, 不影响整条 pipeline)。三个模型互不共享词表也互不共享分词结果 (`tone_berts.py` 内注释明确记载修复过"历史按 max_length 分组导致不同词表模型 token id 跨词表错配"的缺陷, 现按各自词表独立分词), 因此三者给出的正面概率在数值上并不直接可比, 只能各自在自身量纲内做时间序列或截面比较, 三者之间是并列稳健性关系而非可加成分。

【方法学与计算】
文章级正面概率的产生过程分两层。第一层是单窗口推理: 每篇报道的文本 (标题 + 正文, 三轨分别用 `prepend_title` 拼出的 full/ctx/ss 三份文本) 若超出模型单次输入上限 (有效正文 ≤510 token, 含特殊 token 后单窗 ≤512), 用滑动窗口切片, 窗口步幅比例 `WINDOW_STRIDE_RATIO=0.5`, 即相邻窗口重叠 50% 以避免信息在切口处丢失。第二层是窗口间池化: 各窗口 softmax 输出的 logits 按该窗口自身分类置信度加权平均后再取正面维度概率, 即高置信度窗口对文章级概率的贡献更大, 这一步保证长文章不会被机械平均稀释掉局部强烈的语气段落。文章级正面概率算出后, 在 `pipeline/panel/codebook.py` 的面板聚合层, 对同一家银行同一年份内的全部合格文章 (由该模型自身该轨道的推理成功状态决定, 与其它模型/轨道相互独立) 求和, 得到本家族的 `{model}_pos_sum_{track}` 九列。批级推理若发生异常, 引擎会先逐篇重试一次, 仍失败才写入失败哨兵 (标签为 None、概率为 NaN、`bert_num_windows_{track}=-1`), 与真正的空文本情形 (`bert_num_windows_{track}=0`) 严格区分, 二者在求和聚合时都不计入分子, 避免把工程性失败误记为"无正面语气"的实质判断。

【文献定位】
BERT 类预训练语言模型作为文本编码器的方法学基础见 Devlin et al. (2019) 与 Liu et al. (2020) 提出的 FinBERT 系列; 本项目所用三模型分别对应通用中文金融预训练路线与私有领域微调路线, 后者的架构与训练细节参照 Xu et al. (2025) 提出的 FinBERT2, 该模型专门针对中文金融语境下的部署缺口做了双向编码器改造, 是 finbert2 一列的直接方法学出处。Huang, Wang & Yang (2023) 在顶刊 Contemporary Accounting Research 上系统论证了基于 BERT 架构的语言模型在金融文本信息抽取任务上相较传统词典法的增量价值, 是本家族"神经网络语调优于关键词硬数"这一构念定位的顶刊锚点。三模型并行、互不设定唯一权威输出, 呼应了多模型三角验证 (Denzin 2017 经典方法论意义上的方法三角) 的一般原则, 也与本项目 LLM 三家投票、词典六族消融梯度共享同一"多测度并排互证"的设计哲学: 单一模型的系统性偏差 (训练语料覆盖面、领域适配程度、分类粒度) 不应该单独决定实证结论的方向与显著性, 结论须在三个独立训练出身的模型上都能重现才可信。BERT 深层模型相较词典法在情感判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担情感分类主力提供了顶刊层级的方法学背书。

【三轨与模型并排的铁律复述】
本家族横跨两条互相独立的梯子: 一条是三轨文本范围 (full=标题+全文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句±N窗), 另一条是三个 BERT 模型 (finbert_cn/fin_sent_zh/finbert2)。两条梯子交叉产生 3×3=9 列, 但组合出的九个测度各自都是 just-identified 并排关系, 互为稳健性、不分主次, 绝不可混进同一个 over-identified 的 Hansen J 检验联合识别——这与项目内 co-primary 嵌入双轨、政治词权重梯度、词典消融梯度遵循同一条铁律。ss 轨若上游未准备好银行∧金科同句共现 (`FINTECH_AC=None` 或该句无共现), 回退为镜像 ctx 的语义: `content_ss` 退化为全文 body、`ss_is_fallback` 标记为真, 分母 (n_articles) 与 full 轨共享, 这一行为在三模型上是统一的降级方式。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入"银行金科相关报道"只看 `llm_verified_full`, ctx/ss 是 conditional-on-full 的测度轨、行宇宙是 full 留篇集的子集, 因此 ctx/ss 两列的求和范围天然比 full 更窄, 三者之间的数值差异部分来自这一行宇宙差异而非纯粹的文本范围差异, 解读时须一并考虑。此外, per-model 降级是独立的: finbert2 因本地模型未配置而缺席时, 只影响 finbert2 那一族三列, 不连坐 finbert_cn 与 fin_sent_zh, 这与嵌入 co-primary 双轨"任一缺失则同族两列同置 NaN"的 both-or-neither 规则形成鲜明对比, 使用时不应混淆两种降级语义。

## VAR: fin_sent_zh_pos_sum_ctx

【变体差分】
本列由 fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的三分类中文金融情感模型) 在 ctx 轨道 (标题 + 银行实体窗口文本 `content_ctx`, 经 `prepend_title` 拼接) 上推理得到的文章级正面概率, 按 bank-year 求和。与 full 轨相比, ctx 轨的输入文本范围更窄, 只保留银行实体出现处的上下文窗口而非全文, 因此单篇文章的正面概率往往聚焦在与目标银行直接相关的语句段落, 减少了长文章中与银行无关段落 (如宏观背景介绍、其它机构报道穿插) 对整体语气判断的稀释效应; 但也因为窗口更短, 单篇推理更依赖窗口切分是否恰好覆盖了关键语气句。与 finbert_cn/finbert2 两个同轨列相比, fin_sent_zh 是三家里训练语料来源与分类头设计都独立的第三方模型, 其正面概率的数值尺度不与另外两家直接可比, 只可在互为稳健性的意义上比较符号与显著性方向是否一致。本列的行宇宙是 conditional-on-full 的留篇子集 (只统计 `llm_verified_full=True` 的文章), 若该篇文章在 ctx 轨推理失败 (哨兵 `fin_sent_zh_infer_failed_ctx=True`) 或窗口数为 0, 则不计入求和; 与 ss 轨不同, ctx 轨不涉及"同句共现回退"语义, 其上下文窗口来源是银行实体位置窗, 与 ss 轨的银行∧金科同句窗是两个不同的构造原语, 不应混淆二者的文本来源逻辑。ctx 与 full/ss 三者各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified 联合识别设定。实证使用中, 本列常用于验证"银行相关叙事本身的正面语气"是否稳健, 排除文章中与银行无关的其它段落 (如整体行业景气介绍、监管政策综述) 对语气判断的干扰; 若该银行-年份内相关报道篇数偏少, 求和值的波动也会相应放大, 解读绝对水平时应结合当期报道篇数一并考量, 更适合做跨期或跨行的相对比较而非孤立看单一数值。

## VAR: fin_sent_zh_pos_sum_full

【变体差分】
本列是 fin_sent_zh 模型在 full 轨道 (标题 + 全文正文, 无实体窗口裁剪) 上推理得到的文章级正面概率之和, 是本家族三轨中信息覆盖面最完整的一支, 也是留篇门控 (`llm_verified_full`) 唯一直接锚定的轨道——一篇报道是否被计入"银行金科相关报道"的判定只看 full 轨的 LLM 校验结果, ctx/ss 轨是在 full 轨已确认相关的文章子集上再做的测度收窄, 因此 full 轨天然拥有最大的行宇宙, n_articles 分母不会因窗口裁剪而进一步缩小。相较 ctx/ss 两轨, full 轨的正面概率计算覆盖了全文所有段落, 意味着与目标银行无关的正面语气 (例如文章顺带提及行业整体向好、其它公司业绩亮眼) 也会被计入该篇文章的正面概率, 这是 full 轨的固有权衡: 覆盖面最大但归因精度相对 ctx/ss 更弱。作为三个 BERT 模型 (finbert_cn/fin_sent_zh/finbert2) 各自 full 轨列的其中一支, 本列与另两个模型的 full 轨列互为稳健性、co-equal, 不设唯一权威 ensemble headline (与 LLM 三家投票不同, BERT 三模型之间没有共识合成列); 若三个 full 轨列在符号与显著性方向上高度一致, 说明"媒体报道对该银行整体语气偏正面"这一结论不依赖于任一模型的特异性偏差。full 与 ctx/ss 各自 just-identified 并排, 禁止混入同一 Hansen J 联合识别设定。由于 full 轨行宇宙最大, 本列在三轨中通常数值上界最高, 与 ctx/ss 两轨比较时应留意这种规模差异主要源于分母 (合格文章数) 不同, 而非单纯语气强弱本身的差异; 建议下游回归中优先用篇均 (总和除以文章数) 或标准化后的版本做跨轨比较, 原始求和列更适合作为构造篇均指标的中间输入。

## VAR: fin_sent_zh_pos_sum_ss

【变体差分】
本列由 fin_sent_zh 模型在 ss 轨道 (标题 + 银行∧金科同句±N窗文本 `content_ss`) 上推理得到的文章级正面概率之和。ss 轨的文本来源判据是"银行实体与金科词在同一句子内共现" (窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1 句), 与 ctx 轨的银行实体窗判据是两套不同原语, ss 轨的文本范围通常比 ctx 更窄、更聚焦在银行与金融科技话题直接交织的语句。当某篇文章不存在这种同句共现关系时 (包括金科自动分类器 `FINTECH_AC=None` 的极端情形), ss 轨镜像 ctx 轨的回退语义: `content_ss` 退化为全文 body、`ss_is_fallback` 置为真, 该篇文章在 ss 轨的正面概率实质上等价于对全文推理的结果, 而非真正意义上"银行金科同句"窗口的结果; 分母 n_articles 在这种情形下与 full 轨共享。因此本列在解读时应留意 fallback 比例, fallback 比例过高会削弱 ss 轨相较 full 轨的增量识别力。本列同样只统计 full 轨留篇门控通过的文章子集, 是 conditional-on-full 的稳健性测度而非独立留篇标准。与 fin_sent_zh 的 full/ctx 两列、以及 finbert_cn/finbert2 的 ss 轨列相比, 本列各自 just-identified 并排、互为稳健性不分主次, 不进入同一 over-identified Hansen J。fin_sent_zh 是三分类模型, 本列的正面概率与同轨中性、负面两个概率之和恒为一, 若下游分析同时纳入本家族的负面/中性 ss 轨姊妹列 (`fin_sent_zh_neg_sum_ss`/`fin_sent_zh_neu_sum_ss`), 三者之间存在机械互补关系, 不应把三者当作相互独立的自变量同时放入同一回归右端, 否则会引入完全共线性; 更稳妥的做法是只取正面份额或改用 net_tone (正减负) 这类单一综合指标。

## VAR: finbert2_pos_sum_ctx

【变体差分】
本列由 finbert2 模型 (项目自有私有微调模型, 二分类, 只输出正面/负面两个概率、无中性类别) 在 ctx 轨道上推理得到的文章级正面概率之和。finbert2 与另两个基于 HuggingFace Hub 的公开模型 (finbert_cn/fin_sent_zh) 存在两个关键差异: 一是模型来源为本地私有权重, 经 `.env` 的 `FINBERT2_MODEL_DIR` 解析路径加载, 若该环境变量未配置或路径失效, 该模型会优雅跳过 (本列及同族其余五列在该次运行中全部缺失, 但不影响另外两个 HF 模型继续产出), 这是 per-model 独立降级的典型例证, 与嵌入 co-primary 双轨的 both-or-neither 规则语义不同、不应混淆; 二是分类头是二分类而非三分类, 意味着 finbert2 的正面概率与中性类别之间不存在显式的概率划分, 正面/负面两个概率直接互补求和为一, 这使得 finbert2 的 pos_sum 在数值分布形态上可能与另两个三分类模型系统性不同, 比较三模型时应留意这一结构性差异而非误判为噪声。ctx 轨的输入文本范围裁剪到银行实体窗口, 与 full 轨相比降低了无关段落对该模型正面判断的稀释。本列各自 just-identified, 与 finbert2 的 full/ss 轨及另两模型的 ctx 轨互为稳健性并排, 不混入同一 Hansen J。使用本列时须先确认当次运行 `FINBERT2_MODEL_DIR` 是否已正确解析到本地权重目录, 若该运行日志显示 finbert2 已跳过, 本列 (及同族其余五列) 应整体识别为缺失而非真实的零值, 下游聚合与回归若未对此做显式的缺失值处理, 会把模型不可得误判为"该银行-年份完全无正面语气报道", 造成系统性测量偏误。

## VAR: finbert2_pos_sum_full

【变体差分】
本列是 finbert2 模型在 full 轨道 (标题+全文) 上推理得到的文章级正面概率之和, 覆盖 finbert2 一族里行宇宙最完整的测度 (行宇宙由 full 轨留篇门控 `llm_verified_full` 直接锚定, 不像 ctx/ss 是在此基础上的子集测度)。finbert2 是三个 BERT 模型中唯一的私有二分类模型, 其权重路径依赖 `.env::FINBERT2_MODEL_DIR`, 未配置时优雅跳过、整族 (含本列) 在该次运行中缺席, 另两个基于公开 HuggingFace 权重的模型 (finbert_cn/fin_sent_zh) 不受影响照常产出, 体现 per-model 独立降级而非 all-or-nothing 的联动降级。本列与 finbert_cn_pos_sum_full、fin_sent_zh_pos_sum_full 三者构成"BERT 三模型 full 轨互为稳健性"的核心比较单元: 三者若在符号与显著性方向上趋同, 是媒体语气结论不依赖单一厂商/单一训练语料模型的直接证据; 三者之间没有 ensemble 合成的共识列 (与 LLM 三家投票有 `llm_vote_tone` 明确不同), 使用者若需要单一"BERT 综合语调"须自行在下游分析阶段做三模型层面的稳健性汇报, 而非在数据层预先合成。本列与同模型 ctx/ss 轨、与另两模型的 full 轨各自 just-identified 并排, 禁止混入同一 Hansen J。二分类结构意味着本列与三分类模型 (finbert_cn/fin_sent_zh) 的 full 轨列在"正面概率"的定义边界上略有差异: 三分类模型的正面概率是在正面/负面/中性三者中占据的份额, 二分类模型的正面概率是在正面/负面二者中占据的份额, 中性语气在 finbert2 中会被强制摊入正面或负面两端, 这一结构性差异是解释三模型数值不完全一致的重要来源之一, 不宜简单归因为模型质量优劣。

## VAR: finbert2_pos_sum_ss

【变体差分】
本列由 finbert2 模型在 ss 轨道 (标题 + 银行∧金科同句±N窗文本) 上推理得到的文章级正面概率之和, 是 finbert2 一族三轨中文本范围最窄、聚焦度最高的一支。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行与金科词的同句共现时, `content_ss` 退化为全文、`ss_is_fallback` 置真, finbert2 在该情形下实质上是对全文做二分类推理而非对"同句窗口"推理, fallback 比例是解读本列时须核对的辅助诊断量。由于 finbert2 依赖本地私有权重, 该模型缺席时本列与同族另外五列同时缺失, 是 per-model (而非 both-or-neither) 降级语义的又一例证——只影响 finbert2 自身三轨, 不牵连 finbert_cn/fin_sent_zh 的 ss 轨列。本列的行宇宙是 full 轨留篇门控确认后的子集, 且求和分母在 fallback 发生时与 full 轨共享。作为 finbert2 一族中最窄的测度, 本列在实证中通常用于验证"结论是否仅由银行与金科话题真正交织的语句驱动", 是排除无关段落干扰后的一种精炼稳健性检验。本列与家族内其余八列各自 just-identified 并排, 互为稳健性不分主次, 不混入同一 Hansen J。由于 finbert2 权重来源本地私有, 本列与 finbert_cn/fin_sent_zh 各自的 ss 轨列在模型可得性上并不对等: 若某次运行 finbert2 权重目录缺失, 本列缺席不代表 fin_sent_zh_pos_sum_ss/finbert_cn_pos_sum_ss 同样缺席, 使用者在核对面板完整性时应逐模型分别检查缺失模式, 不能假定三个 ss 轨列具有相同的可得性状态。

## VAR: finbert_cn_pos_sum_ctx

【变体差分】
本列由 finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 面向通用中文金融文本训练的三分类公开模型, 输出正面/负面/中性三个概率) 在 ctx 轨道上推理得到的文章级正面概率之和。finbert_cn 与 fin_sent_zh 同为三分类模型、同为 HuggingFace Hub 公开权重, 二者的关键差异在训练语料与微调策略 (finbert_cn 面向更宽泛的中文金融语境, fin_sent_zh 基于 Financial PhraseBank 微调, 后者训练数据源自英文金融语料的中文化改造路径与前者存在实质差别), 因此两者对同一篇文章可能给出方向一致但幅度不同的正面概率, 这正是 per-model 稳健性设计要捕捉的模型间异质性。ctx 轨将输入文本范围裁剪到银行实体窗口, 使 finbert_cn 的正面判断更集中在与目标银行直接相关的语句, 相对 full 轨降低了无关段落语气的稀释。本列的行宇宙是 full 轨留篇门控确认后的子集。finbert_cn 与另两模型 (finbert2/fin_sent_zh) 都是公开模型且都不依赖本地私有权重路径, 因此该模型本身的可得性风险低于 finbert2, 但仍遵循 `strict_models=true` 默认下非预期加载失败 fail-loud 的约束。本列与同模型 full/ss 轨、与另两模型的 ctx 轨各自 just-identified 并排, 禁止混入同一 Hansen J。finbert_cn 作为三分类模型, 其 ctx 轨正面概率还须与同轨的中性、负面两个概率一并理解: 三者在单篇文章内理论上求和为一, 因此正面概率偏高往往对应负面与中性两者之和偏低, 在联合解读语调族群其它测度 (如同家族的 neg_sum、neu_sum) 时应注意这种概率互补关系, 不宜孤立看待正面份额一项。

## VAR: finbert_cn_pos_sum_full

【变体差分】
本列是 finbert_cn 模型在 full 轨道上推理得到的文章级正面概率之和, 是 finbert_cn 一族里行宇宙最完整、也是留篇门控直接锚定的测度轨。finbert_cn 作为面向通用中文金融语境预训练的三分类公开模型, 在本项目三个 BERT 模型中通常被视为"基准/参照"模型 (训练语料覆盖面相对广泛、不针对特定微调任务), 但本项目的设计立场明确是三模型 co-equal 并排、不指定任一模型为权威 headline, finbert_cn_pos_sum_full 与 fin_sent_zh_pos_sum_full、finbert2_pos_sum_full 在实证使用中应始终并列汇报, 而非选择性只报最显著的那一个 (选择性汇报会破坏稳健性设计的初衷、引入研究者自由度带来的 p-hacking 风险)。本列的求和口径与另两模型的 full 轨列完全一致: 对同一 bank-year 内全部留篇通过的文章, 在该模型该轨道推理成功 (非失败哨兵、非空文本) 的前提下累加正面概率。本列与同模型 ctx/ss 轨、与另两模型的 full 轨各自 just-identified 并排, 禁止混入同一 Hansen J。作为三模型 full 轨比较组的一员, 本列在稳健性汇报表格中通常与 fin_sent_zh_pos_sum_full、finbert2_pos_sum_full 并列一行或一组呈现 (镜像 LLM 三家逐模型语调表的呈现方式), 读者据此可直观判断某一银行-年份的正面语气结论在三个训练出身完全不同的模型上是否一致, 一致程度越高, 该结论对模型选择的敏感性越低、越适合作为论文正文的主结果或核心稳健性证据。

## VAR: finbert_cn_pos_sum_ss

【变体差分】
本列由 finbert_cn 模型在 ss 轨道上推理得到的文章级正面概率之和, 是 finbert_cn 一族三轨中最聚焦"银行与金科同句出现"这一构念的测度。与 ctx 轨的银行实体窗判据不同, ss 轨判据要求银行实体与金科关键词在同一句子 (或半径 N 句窗口) 内共现, 这一构造在方法学上比 ctx 轨更严格, 目标是排除文章虽提及银行、但金科相关表述与银行表述相隔甚远、语义关联薄弱的情形。当不存在这种同句共现时, ss 轨镜像 ctx 的回退语义, 退化为全文推理并标记 `ss_is_fallback=True`, 此时本列的正面概率实质上不再反映"同句窗口"这一严格构念, 使用前应结合该银行-年内 ss 轨 fallback 比例判断本列的构念纯度。finbert_cn 是公开模型, 不受本地私有权重可得性影响, 因此本列的缺席只可能源于该篇文章本身在 ss 轨推理失败或空文本, 而非模型级别的整体降级。本列与家族内 finbert_cn 的 full/ctx 轨、以及 finbert2/fin_sent_zh 的 ss 轨列各自 just-identified 并排, 互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 联合识别设定。作为三分类模型在最严格判据轨道上的正面份额测度, 本列与同轨的中性/负面份额之间仍保持互补求和关系; 与另两个模型的 ss 轨列 (finbert2_pos_sum_ss/fin_sent_zh_pos_sum_ss) 联合汇报时, 建议同时附注各自的 fallback 比例, 因为三个模型共用同一份 `content_ss` 文本与同一套回退判据, fallback 比例理论上应当在三模型间完全一致, 若观测到不一致则提示上游文本物化或推理流程可能存在需要排查的异常。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers), 4171-4186. https://doi.org/10.18653/v1/N19-1423
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
