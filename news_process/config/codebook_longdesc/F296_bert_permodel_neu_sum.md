---
family_id: F296
columns:
- fin_sent_zh_neu_sum_ctx
- fin_sent_zh_neu_sum_full
- fin_sent_zh_neu_sum_ss
- finbert_cn_neu_sum_ctx
- finbert_cn_neu_sum_full
- finbert_cn_neu_sum_ss
unit: 无量纲计数 (bank-year 内被判为"中性"类别的文章篇数加总; 非概率、非比率)
formula: 文章级 BERT 三分类 argmax 标签 == 中性 的示性函数在 bank-year 内求和; 三轨 (full/ctx/ss) 各自独立按对应轨道文本重新推理后加总
producer: "pipeline/sentiment/tone_berts.py ; pipeline/panel/encode.py (第808行附近 groupby-agg 聚合: agg[f'{short}_neu_sum{track}'] = (f'{short}_中性{track}', 'sum'))"
upstream:
- 14_materialize_ctx (content_ctx/content_ss 物化)
- 21_tone_llms (llm_verified_full 留篇门控)
- 23_tone_berts (逐模型逐轨 BERT 推理)
citations:
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1145/3711896.3737219"
  type: wp
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.24963/ijcai.2020/622"
  type: wp
  authors: "Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J."
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: "Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)"
  pages_or_artno: "4513-4519"
- doi: "10.18653/v1/N19-1423"
  type: wp
  authors: "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K."
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1"
  pages_or_artno: "4171-4186"
- doi: "10.1007/s00521-024-10603-6"
  type: journal
  authors: "Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y."
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: "Neural Computing and Applications"
  vol: "37"
  issue: "30"
  pages_or_artno: "24883-24892"
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
本家族 F296 度量的是"中性判定的量"而非语调水平: bank-year 面板单元内, 某一 BERT 情感分类模型把文章判为"中性"(既非明显正面也非明显负面) 的篇数总和。它与同源家族 (如 `_pos_sum`/`_neg_sum`) 构成互补的三分类计数三件套, 三者之和在无缺失/无 fallback 的理想情形下等于该单元参与该模型该轨推理的有效文章篇数。中性计数本身承载两层构念含义: 第一, 它是"语调强度"的反面刻度 — 一个 bank-year 单元中性篇数占比越高, 说明该行内媒体报道对涉事银行的情感表达越克制、越偏事实陈述或程序性叙述, 而非鲜明褒贬; 第二, 它是模型置信区间外溢的自然产物 — 当模型在正/负两端把握不足、或原文本身语气中立 (如公告转载、监管程序性报道、人事任免消息) 时, argmax 落在中性类的概率上升。本列族服务于两类下游用途: (a) 作为 washing/漂白稳健性检验的分母校准信号 (中性篇数高的行, 净语调统计量的可靠样本量相应收缩); (b) 作为文本"实质性 vs 象征性" (Westphal & Zajac, 1994, 1998) 判别的辅助佐证 — 中性占比系统性偏高的银行-年份, 可能意味着媒体报道以程序性通稿为主, 应结合 `sub_frac`/`symb_frac` 等分类维度联合解读, 而非孤立使用。

本家族两个 BERT 模型分别是: `fin_sent_zh` (bardsai/finance-sentiment-zh-base, 中文金融短语级情感分类器) 与 `finbert_cn` (yiyanghkust/finbert-tone-chinese, 基于中文语料微调的 FinBERT-Tone)。二者均输出三分类概率分布 {正面, 中性, 负面}, `_neu_sum` 计的是 argmax 落在中性类的文章篇数在 bank-year 内的加总, 而非中性类概率的加总 (概率加总属于另一独立测度族, 若存在应以 `_neu_mean`/`_neu_prob_sum` 等区分命名; 本族 `_neu_sum` 语义严格锚定"计数")。第三个 BERT 模型 FinBERT2 (本地微调, `FINBERT2_MODEL_DIR` 环境变量控制) 若在生产环境未配置该私有模型路径则会优雅跳过, 因此不出现在本家族两模型清单内 — 这是设计使然的 per-model 独立降级, 而非遗漏。

【方法学与计算】
上游 stage 23 `tone_berts.py` 对每篇留篇文章、每个已配置 BERT 模型、每条文本轨道 (full/ctx/ss) 独立跑一次推理。核心算法是滑动窗口切片 + 置信度加权池化: 给定文本 T 与模型最大 token 长度 L, 若 tokenize 后长度超过 L, 则以步长 S=⌊L×stride_ratio⌋ 切出 K 个重叠窗口, 每个窗口独立前向得到 logits_k 与置信度 confidence_k=softmax(logits_k).max(), 再按置信度加权池化 logits*=Σ(confidence_k·logits_k)/Σ(confidence_k), 最终 probs*=softmax(logits*), label*=argmax(probs*)。这一设计使得长文章 (超过约 512 token 的正文) 不会因截断丢失后段信息, 也不会让低置信度窗口 (如夹杂在正文中的无关段落) 过度左右整体判定。文章级中性判定即 label*==中性 的 0/1 示性变量; encode 聚合层在 bank-year 分组内对该示性变量求和, 得到 `{model}_neu_sum_{track}`。

三轨 full/ctx/ss 各自使用独立物化的文本 (`content_full`/`content_ctx`/`content_ss`, 由 stage 14 `ctx_materializer` 产出) 重新推理, 因此三轨的中性计数不是同一次推理结果的重新计数, 而是三次独立的模型前向计算: full 轨吃标题+全文正文, ctx 轨吃标题+目标实体窗口文本, ss 轨吃标题+银行∧金科同句±N窗文本 (窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1)。ss 回退语义镜像 ctx: 当某篇文章无银行∧金科同句共现时, `content_ss` 回退为全文 body (等同 full), 对应行的 `ss_is_fallback` 标记为 True, 但该行依旧参与 `_ss` 轨的 BERT 推理与中性计数, 只是此时其推理输入与 full 轨趋同, 不构成独立信息增量。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨的中性计数混进同一 over-identified Hansen J 设定式 — 三轨差异反映的是"分析窗口选择"这一构念维度, 不是可加总的独立矩条件。

留篇门控口径 (2026-06-29 起) 为 full-only: 一篇文章是否计入某银行-年份的"有效报道" 只看 `llm_verified_full == True` 这一单一判据, 与 BERT 模型自身的三分类判定无关。ctx/ss 两轨的中性计数行宇宙是 full 轨留篇集合的子集 (即先由 stage 21 LLM 门控筛出留篇文章, 再对该子集分别跑 full/ctx/ss 三轨 BERT 推理), 因此三轨分母 (`n_articles_llm_valid_*`) 理论上应共享同一批文章, 差异只体现在推理输入文本、而非样本容量本身 (fallback 情形除外)。

【文献定位】
本家族方法学根基是预训练语言模型情感分类范式。Devlin et al. (2019) 提出的 BERT 双向编码器是本族两模型的共同技术底座; Liu et al. (2020) 与 Huang, Wang & Yang (2023, Contemporary Accounting Research) 分别提出了英文金融语境下的 FinBERT 变体, 确立了"预训练语言模型微调用于金融文本情感分类优于通用词典法" 这一方法学共识, 本项目沿用其三分类 (正/中/负) 输出范式。中文语境下, Xu et al. (2025) 的 FinBERT2 与本项目使用的 `finbert_cn`/`fin_sent_zh` 同属为中文金融文本量身微调的编码器路线; Lan et al. (2025, Neural Computing and Applications) 进一步展示了中文细粒度金融情感分析中实体级判定的可行性, 佐证了本族"文章级 argmax 分类" 设计的合理性边界 (即分类粒度是全文而非句子/实体级, 与 Lan et al. 的更细粒度设计构成互补而非等价关系)。中性类作为三分类体系的第三极, 其计数在文献中通常被视为"信息含量弱/情感表达克制"的补充信号, 与本项目将 `_neu_sum` 定位为语调强度反面刻度的用法一致。BERT 深层模型相较词典法在情感/语调判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型能更准确识别语义层面的中性与非中性表达, 优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担中性/非中性判定主力提供了顶刊层级的方法学背书。

## VAR: fin_sent_zh_neu_sum_ctx

【变体差分】
本列使用模型 `fin_sent_zh` (bardsai/finance-sentiment-zh-base) 在 ctx 轨文本 (标题+目标银行/金科实体窗口, 由 stage 14 物化 `content_ctx`) 上独立推理后, 在 bank-year 内对"argmax=中性"示性变量求和。与 `_full` 轨的差异在于输入文本范围收窄到实体邻近上下文, 剔除了与目标银行、金科议题无直接关联的段落; 这意味着 ctx 轨的中性判定更聚焦于"围绕目标实体的语句本身是否语气克制", 而非整篇文章 (可能包含大段与银行无关的行业背景介绍) 的整体基调。ctx 轨与 full/ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J。样本行宇宙为 full-only 留篇门控下的子集, `ctx_is_fallback` 为 False 时输入文本与 full 轨有实质差异, 为 True 时 (无法定位实体窗口) 回退为全文, 此时 ctx 与 full 轨该行输入趋同。

在实际读数解释上, ctx 轨的中性计数一般会与 full 轨呈现方向一致但幅度不同的走势: 当一篇文章正文冗长、夹杂大量与目标银行无关的行业综述或宏观背景段落时, 这些段落若整体语气偏中性 (常见于程序性/统计性叙述), 会拉高 full 轨的中性判定概率; 而 ctx 轨因剔除了这部分稀释文本, 更直接反映实体本身邻近语境的情感强度, 中性占比可能低于 full 轨 (若实体窗口内语气鲜明) 或高于 full 轨 (若窗口本身就是程序性提及, 如"某银行在本次发布会上介绍了…")。使用者在做 full/ctx 对比时, 应把二者差异读作"文本范围收窄对语调判定的敏感性", 而非其中一轨"更准确"; 二者是并排的稳健性检验对象, 结果若稳定应作为主结论的支撑证据, 若出现分歧应在稳健性附录中如实披露并讨论可能成因 (如实体窗口边界规则、句子切分误差) 而非择优汇报。

## VAR: fin_sent_zh_neu_sum_full

【变体差分】
本列是家族 canonical 轨: 模型 `fin_sent_zh` 在 full 轨文本 (标题+完整正文, `content_full`) 上推理后的中性篇数加总, 覆盖该银行-年份下 `llm_verified_full==True` 留篇集合内的全部文章, 不做实体窗口或同句共现的范围收窄。作为三轨中的 canonical 参照点, 它是留篇门控 (2026-06-29 起 full-only) 直接对应的轨道, 也是稳健性对比 (ctx/ss 相对 full 的偏离) 的基准线, 但铁律要求三轨互为稳健性、不分主次, 本列不因"canonical"标签而获得计量上的优先权重, 仅在样本行宇宙定义上处于锚点位置。

full 轨的输入文本长度通常最长, 因此触发滑动窗口切片 + 置信度加权池化机制的概率也最高: 一篇超过模型 max_length (约 512 token) 的正文会被切成多个重叠窗口分别推理, 再按各窗口置信度加权融合为单一 logits, 最终 argmax 决定该文章的三分类标签。这意味着 full 轨的中性判定实际上是"整篇多段落语气的加权综合", 相较 ctx/ss 两轨 (输入更短、多数情形单窗口即可覆盖) 更容易受长文本中段落异质性的影响 — 例如一篇文章前半段是中性的监管政策解读、后半段才涉及对目标银行的正面评价, full 轨的最终判定取决于两段各自的置信度权重, 而非简单的"哪段提到银行"。使用者在把 full 轨中性计数与 ctx/ss 轨对照时, 应意识到三者不仅是"文本范围"差异, 也隐含"是否触发窗口切片"的推理机制差异, 这是三轨互为稳健性而非互为冗余的另一层依据。

## VAR: fin_sent_zh_neu_sum_ss

【变体差分】
本列使用模型 `fin_sent_zh` 在 ss 轨文本 (标题+银行∧金科同句±1句窗口, `content_ss`, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`) 上推理后的中性篇数加总。ss 轨是三轨中范围最窄的判据: 只保留银行实体与金科词汇在同一句 (或邻近句窗) 内共现的局部文本, 试图捕捉"两者被同时谈及时"的即时语气, 排除掉可能稀释语调信号的大段无关叙述。回退语义镜像 ctx: 若某篇文章无银行∧金科同句共现, `content_ss` 回退为全文 body 且 `ss_is_fallback` 标记为 True, 该行仍计入本列的中性计数分母, 但此时输入实质上等同 full 轨, 不额外增加信息。ss 轨与 full/ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。

由于 ss 轨输入文本极短 (通常只有标题加同句±1窗内的一到两句话), 模型在该轨上极少触发滑动窗口切片, 推理近似单窗口直接 softmax, 判定结果对句子边界切分算法 (`entity_context.extract_bank_fintech_cooccurrence`) 高度敏感。若目标银行与金科词虽处同一自然段但因标点或句法结构被切到不同"句子"单元, 该篇文章会被判定为无同句共现而触发 fallback, 使 ss 轨该行退化为 full 轨输入; 这类 fallback 行在 bank-year 加总时仍计入 `_ss` 中性计数, 但已不再携带"局部即时语气"这一构念的独立信息, 解读时应结合 `ss_is_fallback` 的行占比综合判断该银行-年份的 ss 轨读数可信度, 而非直接假定 ss 与 ctx/full 三轨样本口径完全对齐。

## VAR: finbert_cn_neu_sum_ctx

【变体差分】
本列使用模型 `finbert_cn` (yiyanghkust/finbert-tone-chinese) 在 ctx 轨文本上推理后的中性篇数加总。`finbert_cn` 与 `fin_sent_zh` 是两个独立训练/微调的三分类器, 二者对同一段文本给出的中性判定不保证一致, 二者构成 per-model 互为稳健性的跨厂商/跨训练语料对照, 而非同一测度的重复。ctx 轨语义同上 (`fin_sent_zh_neu_sum_ctx` 一节): 输入收窄至实体邻近窗口, fallback 行回退为全文, 三轨各自 just-identified 并排。`finbert_cn` 是 per-model 独立降级设计中相对稳定的一支 (不依赖本地私有模型路径, 与需要 `FINBERT2_MODEL_DIR` 的 FinBERT2 不同), 因此本列在生产环境中缺失的概率低于假设中的第三模型。

`finbert_cn` 底层是 yiyanghkust/finbert-tone-chinese, 其训练语料与微调目标 (面向财经新闻/公告语气标注) 与 `fin_sent_zh` (bardsai/finance-sentiment-zh-base, 偏短语级金融情感) 存在结构性差异, 二者在中性类的判定阈值与训练标注口径上并不共享同一套标准; 因此 `finbert_cn_neu_sum_ctx` 与 `fin_sent_zh_neu_sum_ctx` 即便使用完全相同的输入文本 (同一批 `content_ctx`), 也不应期待逐行数值相等, 只应期待方向性、排序性上的一致趋势。跨模型一致性诊断应使用 `tone_validation.py` 中复用的 Krippendorff's alpha 或经缺标重映射后的 Cohen's kappa 等专门统计量, 而非直接比较两列的原始计数差值; 后者混淆了"模型分歧"与"训练目标差异"两种不同性质的变异来源, 容易误导为测度设计缺陷。

## VAR: finbert_cn_neu_sum_full

【变体差分】
本列是 `finbert_cn` 模型在 full 轨 (标题+完整正文) 上的中性篇数加总, 是该模型侧的 canonical 参照轨, 与 `fin_sent_zh_neu_sum_full` 构成同轨、跨模型的 per-model 稳健性对照 — 二者若在同一批银行-年份上给出方向一致的中性占比趋势, 可视为"中性判定"这一构念在两套独立训练模型下的收敛证据; 若出现系统性分歧, 应归因于训练语料/微调目标差异而非本项目测度设计缺陷。样本行宇宙同样受 full-only 留篇门控约束, 分母为该模型该轨自身的有效篇数指示列, 不与 `fin_sent_zh` 分母混用。

与 `fin_sent_zh_neu_sum_full` 相同, 本列在长文本上同样会触发滑动窗口切片 + 置信度加权池化机制, 但由于 `finbert_cn` 与 `fin_sent_zh` 的 tokenizer 词表、max_length 参数、微调语料不同, 二者对同一篇文章的切窗方式与各窗口置信度分布也会不同, 导致最终加权融合后的中性判定即便在极端一致的输入下也可能出现分歧。本列与家族内另外两个 `finbert_cn_neu_sum_{ctx,ss}` 构成同模型跨轨对照, 三者共同刻画"finbert_cn 视角下文本范围收窄对中性判定的敏感性", 应联合解读而非孤立使用单一轨道下结论。在跨模型 FWER (家族错误率) 校正的场景下 (根级模板 `27_tableA12_cross_model_fwer`), 本列与 `fin_sent_zh_neu_sum_full` 应被纳入同一 rwolf 检验族, 而不是分别独立报告显著性。

## VAR: finbert_cn_neu_sum_ss

【变体差分】
本列使用模型 `finbert_cn` 在 ss 轨文本 (标题+银行∧金科同句±1句窗口) 上推理后的中性篇数加总, 是三轨中范围最窄、对"局部即时语气是否中性"最敏感的一支。回退语义镜像 ctx: 无同句共现时 `content_ss` 退化为全文, `ss_is_fallback=True`, 该行计入分母但输入信息量收缩为 full 轨水平。本列与 `fin_sent_zh_neu_sum_ss` 构成同轨跨模型对照, 与 `finbert_cn_neu_sum_{full,ctx}` 构成同模型跨轨对照; 两个对照维度 (跨模型、跨轨) 正交, 均应各自 just-identified 并排解读, 禁止合并进同一 over-identified 设定式或同一 Hansen J 检验。

本列是本家族六列中输入文本最短、最贴近"共现瞬间局部语气"这一构念的一列: 当银行实体与金科词汇在同一句中出现且该句本身语气克制 (例如"某银行与某金融科技公司签署合作协议" 这类程序性表述), `finbert_cn` 极可能将其判为中性, 从而推高本列在该银行-年份下的计数。这类中性判定与该篇文章整体 (可能在后续段落转为正面评价) 的语调走向未必一致, 因此本列不宜单独用来代表"该银行-年份整体报道基调偏中性", 只能在与 `finbert_cn_neu_sum_full`、以及情感三分类的正/负两侧计数联合解读时, 用于刻画"共现瞬间"这一更细粒度构念的分布特征。使用者若要评估该银行-年份 finbert_cn 三分类的完整分布形状 (含偏度、极端占比等), 应参照本仓库 F296 之外的 BERT 分布形状五族衍生指标 (`{b}_tone_entropy`/`{b}_xneg_frac`/`{b}_net_tone_skew` 等), 本列仅提供三分类计数三件套中的一支, 不单独构成分布形状测度。
<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20) No. 4513-4519 [Working Paper]. https://doi.org/10.24963/ijcai.2020/622
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 No. 4171-4186 [Working Paper]. https://doi.org/10.18653/v1/N19-1423
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
