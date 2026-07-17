---
family_id: F291
columns:
- fin_sent_zh_neg_count_ctx
- fin_sent_zh_neg_count_full
- fin_sent_zh_neg_count_ss
- finbert2_neg_count_ctx
- finbert2_neg_count_full
- finbert2_neg_count_ss
- finbert_cn_neg_count_ctx
- finbert_cn_neg_count_full
- finbert_cn_neg_count_ss
unit: 篇数/计数 (count)
formula: bank-year 内该 BERT 模型判为负面 (argmax label = 负面) 的文章篇数, 分轨 (full/ctx/ss) 独立统计; 与三家概率均值/net_tone 系列同源但取计数口径而非概率口径
producer: pipeline\sentiment\tone_berts.py ; pipeline\panel\encode.py ; pipeline\panel\codebook.py
upstream: []
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
- doi: "10.1111/1911-3846.12825"
  type: journal
  authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W."
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "765-805"
- doi: "10.1111/1475-679X.12123"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: "Journal of Accounting Research"
  vol: "54"
  issue: "4"
  pages_or_artno: "1187-1230"
- doi: "10.1016/j.jbankfin.2026.107698"
  type: "journal"
  authors: "Turetken, A. C., & Leippold, M."
  year: 2026
  title: "Battle of transformers: Adversarial attacks on financial sentiment models"
  venue: "Journal of Banking & Finance"
  vol: "188"
  pages_or_artno: "107698"
- doi: "10.1007/s11135-026-02832-9"
  type: "journal"
  authors: "Hsu, H.-Y., & Hsu, M.-L."
  year: 2026
  title: "Semantic stability protocol: intercoder reliability for zero-shot classification via AI coders"
  venue: "Quality & Quantity"
- doi: "10.3982/qe1825"
  type: "journal"
  authors: "Ke, S., Montiel Olea, J. L., & Nesbit, J."
  year: 2024
  title: "Robust machine learning algorithms for text analysis"
  venue: "Quantitative Economics"
  vol: "15"
  issue: "4"
  pages_or_artno: "939-970"
- doi: "10.1016/j.pacfin.2025.102721"
  type: "journal"
  authors: "Wang, Y., Xiao, J., Wang, L., & Wang, D."
  year: 2025
  title: "News sentiment and the cost of debt"
  venue: "Pacific-Basin Finance Journal"
  vol: "91"
  pages_or_artno: "102721"
- doi: "10.1016/j.chieco.2025.102568"
  type: "journal"
  authors: "Zhu, D., Wang, X., & Zhang, Y."
  year: 2025
  title: "Narrative monetary policy expectation in China"
  venue: "China Economic Review"
  vol: "94"
  pages_or_artno: "102568"
new_dois: []
---

## CORE

【构念与来源】
本家族 F291 (`bert_permodel_neg_count`) 度量的是 bank-year 层面某一篇章级 BERT 情感模型把新闻判为「负面」的篇数, 而不是概率强度或语调均值。它属于本项目情感三条独立测量路线 (大模型 LLM 投票 / 词典法 / BERT 分类) 中 BERT 一路的逐模型计数支线。三个模型 —— `finbert_cn` (yiyanghkust/finbert-tone-chinese, 3 分类含中性)、`fin_sent_zh` (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3 分类模型)、`finbert2` (项目自研私有模型 FinBERT2, 2 分类无中性档) —— 各自独立对每篇文章的三轨文本 (`full`=标题+全文, `ctx`=标题+银行实体窗口, `ss`=标题+银行∧金科同句±N 窗口) 做 argmax 分类, 得到逐篇 `{model}_label_{track}`; F291 家族的 9 列即把该逐篇标签在 bank-year 内聚合为「label=负面」的计数, 按 `{model}_neg_count_{track}` 命名, model ∈ {finbert_cn, fin_sent_zh, finbert2}, track ∈ {full, ctx, ss}, 3×3=9 列。这与同源的 `{model}_neg_sum`/`{model}_neg`(概率均值)/`{model}_net_tone` 等列是同一上游标签/概率矩阵的不同聚合口径: neg_count 是离散计数(可解释为"负面报道篇数", 便于做 Poisson/negative binomial count-data 回归或直接看比例), neg_sum/neg 是概率强度的求和/均值(保留模型的置信度信息, 适合线性 OLS)。二者互补而非互相替代: count 口径抗极端概率值的杠杆效应, 概率口径保留了模型"多确定"的分级信息。

本家族与家族核心「LLM 三家 / BERT 三模型互为稳健性」的项目铁律直接对应: `finbert_cn`/`fin_sent_zh`/`finbert2` 三个模型 co-equal, 无 ensemble headline (不像 LLM 侧有 `llm_vote_tone` 投票共识作 canonical), 因此三模型的 neg_count 各自并排作为独立稳健性测度, 用于证明"银行的媒体负面报道计数"这一结论不被任一模型的分类边界/训练语料偏好单独驱动。这是三角验证 (triangulation) 方法学的直接落地: 同一构念 (新闻负面度) 由架构、预训练语料、类别数完全不同的三个神经网络模型独立估计, 若三者对同一 bank-year 样本给出方向一致的负面计数走势, 结论的稳健性显著增强于单模型证据。

【方法学与计算】
上游 stage 23 (`23_tone_berts.py`, thin shim, 逻辑在 `pipeline/sentiment/tone_berts.py`) 读取 stage 22 词典法输出 (`22_words_tone.parquet`), 用 `MultiModelSentimentEngine` 一次性把三个 BERT 模型权重加载到 GPU (FP32 + AMP 自动混合精度推理)。对每篇文章的三轨文本 (`prepend_title` 拼接标题+对应内容列), 各模型按自身 tokenizer 独立分词分窗 (fix g-berts-01 后, 不同词表模型不再共享分词结果以防 token id 跨词表错配); 超过 max_length (512, 有效正文 ≤510 token) 的长文本用 50% 重叠的滑动窗口切片, 各窗 logits 按置信度加权池化 (`Σ(conf_k·logits_k)/Σconf_k`, 高置信窗口权重更大) 合并为该篇的最终 logits, 再 argmax 得到 `{model}_label_{track}`。批级推理异常时逐篇重试一次, 仍失败才写失败哨兵 (label=None, 概率列 NaN, `bert_num_windows_{track}`=-1), 与空文本 (`bert_num_windows_{track}`=0) 严格区分, 二者都不计入 F291 的负面计数分母。

F291 的下游聚合真正发生在 `pipeline/panel/encode.py`: 该模块在把逐篇标签展开为逐篇布尔哨兵列 `_is_{model}_negative{track}` (label 命中该模型的负面枚举时为 True, 空文本/失败哨兵不计入) 之后, 在 bank-year 分组聚合阶段执行 `agg[f'{model}_neg_count{track}'] = ('_is_{model}_negative{track}', 'sum')`, 即对该布尔标志逐篇求和得到本家族的计数列; 这是标准的 pandas groupby-agg sum, 而非对标签字符串做条件计数的正则匹配。`pipeline/panel/codebook.py` 里的 `_BERT_MODEL_RE` 是一个独立的、职责完全不同的正则匹配器: 它只在生成 codebook 元数据/家族标签、以及 `_infer_source_stage` 做列名→来源阶段的宽前缀路由时被使用, 不参与也不触碰任何面板数值的聚合计算, 二者在代码库中是两条互不调用的路径 (encode 层管数, codebook 层管元数据标签), 不应混为一谈。三个模型的负面标签阈值边界 (argmax 而非固定概率阈值) 完全由各自训练时的 softmax 输出决定, 不做跨模型统一校准 —— 这是刻意设计: 强行校准会抹去模型间"不同架构对同一文本判断分歧"这一稳健性检验本身想捕捉的信息。

三轨 full/ctx/ss 的文本范围差异见项目铁律: full=标题+全文 (留篇门控口径, 2026-06-29 起 stage 21 是否判定为"一篇银行金科报道"仅看 `llm_verified_full`, ctx/ss 是 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集); ctx=标题+银行实体窗口; ss=标题+银行∧金科同句±1 句窗口 (无该共现时回退为全文, `ss_is_fallback=True`, 与 ctx 的回退语义镜像对称)。三轨各自独立计算 neg_count, 互为稳健性并排, 禁止混入同一 over-identified Hansen J —— 这与三轨文本架构、co-primary 嵌入双轨、政治词权重梯度等其它梯子适用完全相同的铁律: 每一条轨/每一个模型都应作为 just-identified 的独立设定单独估计, 而不是把多条轨的矩条件塞进一个过度识别系统联合检验, 否则会把"稳健性证据"错误地包装成"额外的识别约束", 混淆了两者截然不同的推断逻辑。

FinBERT2 是项目私有微调模型, 依赖 `.env` 的 `FINBERT2_MODEL_DIR` 解析本地权重路径; 该变量留空或路径失效时该模型被优雅跳过 (`finbert2_neg_count_{track}` 三列整体缺失/为 NaN), 另两个 HuggingFace 公开模型 (finbert_cn, fin_sent_zh) 照常运行不受影响 —— 这正是"per-model 独立降级"的具体例证: 三模型稳健性梯子中任一模型的可用性问题只影响该模型自身的列族, 不会像 co-primary 嵌入 both-or-neither 守卫那样连坐拖垮整族。本地重跑 stage 23 须设 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` (两个 HF 模型连不上外网但本地已有缓存权重, 否则会因联网拉取失败而报错)。整个 stage 23 无 LLM API 调用, 不受 `NEWS_PROCESS_LLM_OFFLINE` 缓存守卫约束, 确定性完全来自模型权重 + argmax 判定逻辑 (AMP 混合精度对最终分类结果无影响, 只影响推理速度)。

【文献定位】
BERT 类预训练语言模型在金融文本情感分类上的适用性已由 Huang, Wang & Yang (2023) 的 FinBERT 建立方法学范式: 相较通用领域词典或早期机器学习分类器, 金融领域微调过的 BERT 编码器能更好捕捉专业术语的上下文语义, 这正是本家族选用 finbert_cn 与 finbert2 (均为金融领域专用架构) 而非通用情感分类器的理据。finbert2 对应 Xu et al. (2025, KDD '25) 提出的双向编码器架构, 该文献强调"面向金融场景部署的专业化编码器"与通用大模型相比在特定分类任务上仍有独立价值, 支持本项目把 finbert2 作为与两个 HuggingFace 公开模型并列的第三条独立测量路线, 而非把它视为冗余。Bochkay, Brown, Leone & Tucker (2023) 在 *Contemporary Accounting Research* 对会计文本分析方法学做系统综述, 明确指出神经网络分类模型与传统词典法应"互为印证"而非相互替代, 这为项目 LLM/词典/BERT 三条路线并行、以及 BERT 内部三模型并行的设计提供了方法学正当性。Loughran & McDonald (2016) 的文本分析综述进一步指出, 单一情感测量方法的度量误差会系统性地衰减回归系数并可能误导推断, 多方法三角验证是缓解该问题的推荐做法 —— 本家族的三模型 neg_count 并排正是这一建议在计数口径上的直接实现。

三家 BERT 模型的负面计数 neg_count 与同族的负面概率均值/求和 (neg/neg_sum)、net_tone (正−负) 属于同一逐篇标签/概率矩阵的不同聚合函数, 二者在回归表中应作为互补稳健性证据分别呈现, 而不是彼此替代或相加: neg_count 更贴近"篇数曝光"这一直觉概念 (类似 tone_words 词典法的 pos_count/neg_count 计数族), neg_sum/net_tone 更贴近"情感强度加权曝光"。跨模型一致性 (Krippendorff's α / Cohen's κ) 的检验由 `tone_validation.py` 统一实现, 用于报告三模型在负面判定上的一致程度, 与本家族的面板列是不同层次的产出 (逐篇一致性 vs bank-year 聚合计数), 不应混淆。 近期文献从三个方向进一步强化了本家族多模型并排的必要性。Turetken 与 Leippold (2026) 对 FinBERT 与生成式 Fin-GPT 施加语义保持的白盒对抗扰动, 发现二者的情感标签预测均被大比例翻转, 说明金融情感分类器的 argmax 标签并非稳固不变, 任一模型单独的 neg_count 都不应被视作构念真值 —— 这正是本家族保留三模型各自计数并排的直接理据; 原文为英文基准数据集上的句/篇级对抗鲁棒性评测, 其结论是两模型均脆弱而非报告模型间脆弱性差异, 所涉 Fin-GPT 亦非 BERT 架构, 且不涉及中文语料、bank-year 聚合与 count/sum 两种口径之分。Hsu 与 Hsu (2026) 以 DeepSeek Reasoner 对 424 篇中文新闻做五分类、每篇重复 100 次, 用 Krippendorff's α 量化零样本分类的模型内随机性 (原始输出 α=0.8485, 约 20 次多数票聚合后 α>0.94), 表明把 α/κ 类编码者间信度指标施用于 AI 分类器在中文新闻语料上的标注输出, 是方法学上已被接受的效度前置程序, 佐证本家族借 tone_validation.py 报告三模型负面判定一致程度的做法; 但其"AI coders"实为同一模型的多次重复运行, 全文未做任何跨模型比较, 故不构成本项目模型间一致性这一维度的直接先例, 且其对象为零样本生成式 LLM 而非微调 BERT (本项目各模型还存在 2 vs 3 分类基数差异)。Ke 与 Nesbit (2024) 证明 LDA 参数不可识别、文本派生量的下游结论会随先验设定改变, 并给出刻画该结论取值区间的算法; 本家族仅取其一般性方法论立场 —— 建模者未被数据识别的选择应被显式化并报告结论在其上的取值范围, 对应三个 BERT 的 neg_count 各自 just-identified 并排、互为稳健性不分主次、严禁混入同一 over-identified Hansen J 的设计; 原文研究的是单一 LDA 内的先验敏感性而非不同分类器之间的模型选择, 未评估任何 BERT 或神经情感分类器, 亦不涉及计数口径与中文语料。在应用语境一侧, Wang、Xiao、Wang 与 Wang (2025) 在中国语境下从新闻报道抽取情感并聚合到企业层面用于债务成本实证, 是"中文新闻情感 → 实体-年测度"应用同域的近期实例, 用以锚定本家族正负面篇数列族的应用语境而非其具体算法; Zhu、Wang 与 Zhang (2025) 则对逾 100 万篇中文经济新闻做语义分析构造中国叙事型货币政策预期指数, 并以宏观/微观调查类预期指标验证其收敛效度, 说明在中文文本上构造计量化测度并以外部指标做效度检验, 在近期国际期刊上是既有且被接受的做法。迁移边界须一并写明: 前者实体为一般上市公司、DV 为债务成本, 未区分 count 与 probability-sum 口径, 无 per-model 子测度与三轨文本范围; 后者层级为宏观货币政策叙事而非银行-年微观面板, 测度对象是政策方向预期而非情感极性, 未设中性档, 亦未使用 BERT 或多模型并排。
## VAR: fin_sent_zh_neg_count_full

【变体差分】
本列取 `fin_sent_zh` 模型 (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的中文金融 3 分类模型) 在 full 轨 (标题+全文, 留篇门控主口径) 上的逐篇 argmax 负面标签, 在 bank-year 内计数。`fin_sent_zh` 与 finbert_cn 同为 3 分类 (正面/中性/负面), 但两者的预训练语料、微调数据集与分词词表都不相同 (fin_sent_zh 溯源自英文 Financial PhraseBank 迁移微调, finbert_cn 是直接在中文金融语料上预训练), 因而在同一批文章上对"负面"的分类边界并不一致, 二者提供彼此独立的判定证据。作为 full 轨列, 本列使用 stage 21 `llm_verified_full` 门控下的留篇集合作为行宇宙的上游文本来源, 是本家族在样本覆盖面上最完整的一列 (ctx/ss 是其 conditional-on-full 的稳健性轨, 行宇宙是 full 留篇集的子集)。full 轨输入文本未做任何银行实体窗口截断或同句共现过滤, 因此本列的负面计数最容易受到文章中与目标银行无关段落 (例如同篇提及的宏观经济评论、其它公司新闻) 的语气拖累, 这正是设立 ctx/ss 两条更聚焦轨道的动因。与本模型的 ctx/ss 两列互为稳健性并排, 三者共享同一模型权重、同一 argmax 判定逻辑与同一滑动窗口置信度池化算法, 差异仅来自输入文本的范围截断; 与 finbert_cn/finbert2 在 full 轨上的对应列则构成跨模型稳健性, 差异根源是模型本身的架构与训练数据, 而非文本范围。按照项目通用铁律, 上述所有并排列均应各自 just-identified 单独估计, 不得混入同一 over-identified Hansen J。

## VAR: fin_sent_zh_neg_count_ctx

【变体差分】
本列取 `fin_sent_zh` 模型在 ctx 轨 (标题+银行实体窗口文本, `content_ctx`, stage 14 `ctx_materializer` 物化) 上的逐篇负面标签计数。ctx 轨聚焦于目标银行实体出现处附近的局部上下文窗口, 相比 full 轨过滤掉了文章中与银行无关的段落, 用于检验"负面"判定是否被文章中与银行无关的其它内容 (例如同篇提及的宏观政策、其它公司或行业整体评论) 稀释或污染, 从而更贴近"该银行本身在报道中被如何评价"这一构念。2026-06-29 起留篇门控已切换为 full-only, 本列的行宇宙不再独立判定, 而是 full 留篇集的子集, 属于 conditional-on-full 的测度/稳健性轨, 不再具备独立留篇口径的地位。ctx 轨与 full 轨的差异纯粹来自输入文本的截断范围 (银行实体窗口 vs 全文), 模型权重、argmax 判定逻辑、滑动窗口池化算法完全相同, 因此二者数值上的系统性差异可解释为"聚焦银行局部语境是否改变了负面判定"这一实证问题本身, 而非测量工具误差。与该模型的 full/ss 两条轨互为稳健性并排, 三者不分主次, 不作为主要识别依据单独使用, 也不得混入同一 over-identified Hansen J 联合矩条件估计。本列与 finbert_cn_neg_count_ctx、finbert2_neg_count_ctx 共享同一批 `content_ctx` 输入文本 (同一 stage 14 物化产物), 三者的判定分歧完全来自模型架构与训练语料, 是本家族内"同轨异模型"最纯净的跨模型对照组之一。

## VAR: fin_sent_zh_neg_count_ss

【变体差分】
本列取 `fin_sent_zh` 模型在 ss 轨 (标题+银行∧金科同句±1 句窗口文本, `content_ss`, 半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 上的逐篇负面标签计数。ss 轨判据比 ctx 更严格, 要求银行实体与金科词在同一句 (或窗口半径内) 共同出现, 是三轨中对"银行—金科交叉议题"最聚焦的一条; 当某篇文章不满足该共现条件时, `content_ss` 按项目铁律回退为全文 body 且 `ss_is_fallback=True` (回退语义镜像 ctx 轨, 共享 `n_articles` 分母), 此时该篇在 ss 轨的负面判定实质上退化为对 full 轨全文的判定, 与 full 轨在回退子样本上高度重合、非回退子样本上则反映更严格的语境筛选。ss 轨最贴近"银行与金融科技议题同时被提及且语境负面"这一具体构念, 在本机 dev T=2 小样本上可能因银行∧金科同句共现条件本身稀疏而出现较高比例的回退, 使 ss 轨数值向 full 轨收敛; 生产 T=19 全量语料上样本量大幅提升, 回退比例预期显著降低, ss 轨与 full/ctx 轨之间的判定分歧才能更充分展开。与该模型的 full/ctx 两条轨互为稳健性并排, 三者共享模型权重与判定算法, 差异仅来自输入文本范围, 不作为主要识别依据单独使用。本列可与 finbert_cn_neg_count_ss、finbert2_neg_count_ss 联合观察: 三者共享同一批 `content_ss` 输入 (含相同的回退子样本), 若三模型在 ss 轨上呈现方向一致的负面计数走势, 即构成"银行∧金科同句负面报道"这一严格构念不被模型选择驱动的有力证据。

## VAR: finbert2_neg_count_ctx

【变体差分】
本列取 `finbert2` 模型 (项目自研私有 FinBERT2, 2 分类无中性档, `.env::FINBERT2_MODEL_DIR` 解析本地权重) 在 ctx 轨 上的逐篇负面标签计数。finbert2 与另两个模型的关键区别是类别体系不同: finbert2 只有正/负二分类, 不设中性档, 因此其"负面"判定本质上等价于一个二元 softmax 边界 (label=0 侧), 而 finbert_cn/fin_sent_zh 的负面判定需要先在正/负/中性三档中 argmax 选出负面档, 一部分本会落入负面区间的边界样本会被三分类模型分流到中性档而不计入其 neg_count。这意味着 finbert2 的 neg_count 与另两个 3 分类模型的 neg_count 在概念上不完全对齐, 跨模型比较应侧重"方向一致性"(三模型是否同向反映某银行某年负面报道增多) 而非"占比数值直接可比"。ctx 轨聚焦银行实体窗口文本, 是该模型三轨中 conditional-on-full 的稳健性测度之一。本列同时受 `FINBERT2_MODEL_DIR` 环境变量控制的 per-model 独立降级机制约束: 该路径未配置或指向无效路径时, finbert2 整族三轨列 (含本列) 一并缺失 (优雅跳过), 另两个 HuggingFace 公开模型 (finbert_cn, fin_sent_zh) 的对应列不受任何影响, 这是"per-model 独立降级"而非 co-primary 嵌入 both-or-neither 守卫的具体例证。与该模型的 full/ss 两条轨互为稳健性并排。ctx 轨的银行实体窗口截断在 finbert2 上与在另两个 3 分类模型上的作用机制完全一致 (同一 stage 14 物化的 `content_ctx` 输入), 因此本列与 finbert_cn/fin_sent_zh 的 ctx 轨对应列可以在"文本聚焦效应"这一维度上做交叉验证, 但不能因为文本相同就把三者的负面标签强行对齐或加总, 类别体系差异始终是跨模型比较的第一约束。

## VAR: finbert2_neg_count_full

【变体差分】
本列取 `finbert2` 模型在 full 轨 上的逐篇负面标签计数, 使用留篇门控主口径 (`llm_verified_full`) 下的完整文本, 是 finbert2 三轨中样本覆盖面最完整的一列。由于 finbert2 是 2 分类模型, 本列的"负面"判定不存在中性档分流问题, 计数在数值上通常会高于同样本、同轨下 finbert_cn/fin_sent_zh 两个 3 分类模型的负面计数 (因为 3 分类模型会把一部分本应落入负面的边界样本分流到中性档), 这是模型架构差异导致的预期系统性水平差, 不代表银行媒体语调这一底层构念本身发生变化, 跨模型比较时应关注方向与统计显著性的一致性而非绝对计数水平的相等。finbert2 作为项目自研模型, 权重不公开分发, 其训练语料与超参数细节仅项目内部可追溯, 这决定了本列 (以及该模型的 ctx/ss 两轨) 在复现性上依赖 `FINBERT2_MODEL_DIR` 指向的本地权重快照; 该路径缺失时本列整体缺失, 另两 HuggingFace 模型照常运行。与该模型的 ctx/ss 两条轨互为稳健性并排, 不分主次。作为留篇门控主口径下样本最全的一列, 本列在三模型跨厂商/跨架构稳健性对照表中通常与 finbert_cn_neg_count_full、fin_sent_zh_neg_count_full 并列呈现, 三者共同回答"银行媒体负面报道计数是否被任一 BERT 模型的分类边界单独驱动"这一稳健性问题, 缺一不可。

## VAR: finbert2_neg_count_ss

【变体差分】
本列取 `finbert2` 模型在 ss 轨 (银行∧金科同句窗口, 回退语义镜像 ctx, 共享 `n_articles` 分母) 上的逐篇负面标签计数。作为 finbert2 三轨中判据最严格的一列, 它同时叠加了两层稀释/收敛效应: 一是二分类无中性档带来的架构性水平差 (较三分类模型系统性偏高), 二是 ss 轨判据严格导致的高回退率 (尤其在本机 dev T=2 小样本上, 银行∧金科同句共现条件本身出现频率低, 大量文章的 `content_ss` 会回退为全文, 使 ss 轨数值趋近 full 轨)。若 `FINBERT2_MODEL_DIR` 未配置或路径失效, 本列随该模型整族 (含 full/ctx 两轨) 一并缺失, 不影响 finbert_cn/fin_sent_zh 的对应列。与该模型的 full/ctx 两条轨互为稳健性并排, 不单独作为识别依据。本列与 fin_sent_zh_neg_count_ss、finbert_cn_neg_count_ss 共享同一批已回退处理的 `content_ss` 输入, 三者在 ss 轨上的差异同样归因于模型架构, 是判断"银行∧金科同句负面报道"这一严格构念是否跨模型稳健的直接依据。由于 finbert2 无中性档且 ss 轨判据最严格, 本列在三轨×三模型九列矩阵中属于"双重收窄"的一格: 文本范围最窄 (仅同句窗口或其回退全文) 叠加类别体系最简单 (二分类无缓冲), 解读时应格外留意小样本下的高方差, 不宜单独据此得出强结论, 须与其余八列联合观察走势是否一致。

## VAR: finbert_cn_neg_count_ctx

【变体差分】
本列取 `finbert_cn` 模型 (yiyanghkust/finbert-tone-chinese, HuggingFace 公开权重, 3 分类含中性档) 在 ctx 轨 上的逐篇负面标签计数。finbert_cn 是三模型中预训练语料公开可查、被后续文献引用最广的中文金融 BERT 之一, 常被其它研究用作基准对照模型, 这使得本列 (以及该模型的 full/ss 两轨) 在跨研究可比性上具备一定优势, 但项目内部并不因此赋予它优先地位 —— 三模型 co-equal 是明确铁律。ctx 轨聚焦银行实体窗口, 与该模型 full 轨的差异纯粹来自输入文本截断范围, 是 conditional-on-full 的稳健性测度, 用于检验负面判定是否被文章中与银行无关的段落拖累。finbert_cn 与 fin_sent_zh 同为 3 分类体系但底层预训练/微调数据完全不同, 两者的负面判定边界存在系统性差异, 构成本家族内跨模型稳健性检验的核心对比对之一; finbert_cn 与 finbert2 则额外存在类别体系差异 (3 分类 vs 2 分类)。与该模型的 full/ss 两条轨互为稳健性并排, 不作为主要识别依据单独使用。finbert_cn 与 fin_sent_zh 在 ctx 轨上共享相同的 `content_ctx` 输入与相同的 3 分类体系, 二者对应列构成"同判据、同轨道、异模型权重"的最纯净跨模型对照, 是检验负面判定是否被特定预训练语料偏好驱动的理想对比列。本列在 full 轨上还可与 finbert2_neg_count_full 对照, 后者因无中性档而在同一文本上通常给出更高的负面计数水平, 二者的水平差是类别体系差异的预期结果而非测量误差。

## VAR: finbert_cn_neg_count_full

【变体差分】
本列取 `finbert_cn` 模型在 full 轨 上的逐篇负面标签计数, 使用留篇门控主口径下的完整文本, 是本项目方法学综述文献 (Huang, Wang & Yang 2023; Bochkay, Brown, Leone & Tucker 2023) 中被讨论最多的一种金融 BERT 架构在最完整样本上的负面计数产出, 常作为三模型 BERT 稳健性检验里最先被读者关注的一列。但项目铁律明确三模型 co-equal 不分主次、无 ensemble headline, 本列不构成优先于 fin_sent_zh/finbert2 对应列的"主 BERT 测度", 三者在正文表格中应并排呈现而非以本列替代另外两列。finbert_cn 是 HuggingFace 公开托管模型, 联网重跑时依赖外部下载或本地缓存 (须设 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` 复现本机结果), 与 finbert2 依赖项目私有 `.env` 路径的复现方式不同, 这是两模型在可复现性工程细节上的差异, 不影响构念本身的可比性。与该模型的 ctx/ss 两条轨互为稳健性并排。作为三模型中知名度最高、被后续文献直接沿用最多的架构, finbert_cn 的 full 轨列也常被用作"最保守/最容易被审稿人接受"的单模型基准, 但这只是外部认可度上的优势, 不改变项目内部三模型 co-equal 的设计立场; 报告结果时应与 fin_sent_zh_neg_count_full、finbert2_neg_count_full 一并列出, 而非以本列单独作为正文主表。本列的 argmax 判定阈值继承自 yiyanghkust/finbert-tone-chinese 原始预训练 softmax 输出, 项目未做任何跨模型概率再校准, 三家模型的负面边界各自独立, 这也是"各自 just-identified 并排、禁混同一 over-identified Hansen J"铁律在本列上的具体体现: 本列与 fin_sent_zh_neg_count_full、finbert2_neg_count_full 应分别单独估计, 不得把三者的负面标签矩条件合并进一个联合系统。

## VAR: finbert_cn_neg_count_ss

【变体差分】
本列取 `finbert_cn` 模型在 ss 轨 (银行∧金科同句窗口, 回退语义镜像 ctx, 共享 `n_articles` 分母) 上的逐篇负面标签计数, 是 finbert_cn 三轨中判据最严格、行文本范围最窄的一列。当同句共现条件不满足时回退为全文判定 (`ss_is_fallback=True`), 与 full 轨在回退子样本上高度重合, 在非回退子样本 (确实存在银行∧金科同句共现) 上则更精确地反映"银行与金融科技交叉议题被负面报道"这一具体构念, 是该家族内构念聚焦度最高的一列之一。finbert_cn 的 3 分类体系 (正/中/负) 意味着 ss 轨上出现的模糊语境更容易被判定为中性而非负面, 相比 finbert2 的 2 分类体系, 本列的负面计数在严格判据下的绝对水平预期系统性更低。与该模型的 full/ctx 两条轨互为稳健性并排, 三轨/三模型均遵循"各自 just-identified 并排, 禁混同一 over-identified Hansen J"的项目通用铁律, 不作跨轨或跨模型的联合矩条件估计。本列与 fin_sent_zh_neg_count_ss、finbert2_neg_count_ss 三者构成本家族在 ss 轨上最完整的跨模型三角验证组, 是判断银行媒体负面报道计数结论是否稳健于模型选择的关键证据来源。作为 finbert_cn 三轨中最靠后被引用的一列, 本列在生产 T=19 全量语料尚未播种前 (本机 dev T=2) 的数值应视为方法学演示而非最终结果, 待生产语料重新推理后方可用于正式稳健性表格。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Turetken, A. C., & Leippold, M. (2026). Battle of transformers: Adversarial attacks on financial sentiment models. Journal of Banking & Finance, 188, 107698. https://doi.org/10.1016/j.jbankfin.2026.107698
Hsu, H.-Y., & Hsu, M.-L. (2026). Semantic stability protocol: intercoder reliability for zero-shot classification via AI coders. Quality & Quantity. https://doi.org/10.1007/s11135-026-02832-9
Ke, S., Montiel Olea, J. L., & Nesbit, J. (2024). Robust machine learning algorithms for text analysis. Quantitative Economics, 15(4), 939-970. https://doi.org/10.3982/qe1825
Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
Zhu, D., Wang, X., & Zhang, Y. (2025). Narrative monetary policy expectation in China. China Economic Review, 94, 102568. https://doi.org/10.1016/j.chieco.2025.102568
<!-- rendered-citations:end -->
