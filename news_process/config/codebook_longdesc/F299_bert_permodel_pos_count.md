---
family_id: F299
columns:
- fin_sent_zh_pos_count_ctx
- fin_sent_zh_pos_count_full
- fin_sent_zh_pos_count_ss
- finbert2_pos_count_ctx
- finbert2_pos_count_full
- finbert2_pos_count_ss
- finbert_cn_pos_count_ctx
- finbert_cn_pos_count_full
- finbert_cn_pos_count_ss
unit: 篇数/计数 (count)
formula: 单模型 bank-year 内 argmax 标签判为正面(label=正面)的文章篇数, 按 full/ctx/ss 三轨分文本范围各自统计
producer: pipeline\sentiment\tone_berts.py (文章级三轨概率/标签) ; pipeline\panel\encode.py (bank-year 聚合, build_aggregation_dict groupby-sum)
upstream: []
citations:
- doi: "10.1145/3711896.3737219"
  type: wp
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1016/j.jfineco.2022.08.004"
  type: journal
  authors: "Cohn, J. B., Liu, Z., & Wardlaw, M. I."
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: "Journal of Financial Economics"
  vol: "146"
  issue: "2"
  pages_or_artno: "529-551"
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
- doi: "10.1016/j.pacfin.2025.102721"
  type: "journal"
  authors: "Wang, Y., Xiao, J., Wang, L., & Wang, D."
  year: 2025
  title: "News sentiment and the cost of debt"
  venue: "Pacific-Basin Finance Journal"
  vol: "91"
  pages_or_artno: "102721"
- doi: "10.3982/qe1825"
  type: "journal"
  authors: "Ke, S., Montiel Olea, J. L., & Nesbit, J."
  year: 2024
  title: "Robust machine learning algorithms for text analysis"
  venue: "Quantitative Economics"
  vol: "15"
  issue: "4"
  pages_or_artno: "939-970"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是三个中文金融领域 BERT 分类器 (finbert_cn、fin_sent_zh、finbert2) 各自在 bank-year 层面判定为「正面」的报道篇数, 三轨 (full/ctx/ss) 各自独立统计, 一共 3 模型 × 3 轨 = 9 列, 全部 standard tier。这一族的构念定位是「离散计数旁证」: 它不直接回答某银行某年报道语调有多正面 (那是 net_tone/pos/pos_sum 概率族的任务), 而是回答有多少篇报道被模型硬性归到正面这一类, 是情感测度体系里"频次视角"对"强度视角"的补充。上游来自 stage 23 (`tone_berts.py`, thin shim `23_tone_berts.py`): 三个模型预先加载到 GPU, 对每篇文章的 full(标题+全文)/ctx(标题+银行实体窗口)/ss(标题+银行∧金科同句窗口) 三种文本范围分别推理, 得到各模型各轨的 `{sn}_label` (argmax 分类标签) 与对应类别概率列; 超长文本经滑动窗口切片 (50% 重叠) + 置信度加权池化聚合多窗 logits 后再取 argmax。stage 23 的输出 (`23_bert_tone.parquet`) 在下游 `pipeline/panel/encode.py` (`build_aggregation_dict`) 里被聚合到 bank-year: 对每个 (银行, 年份) 单元, 以 `_is_{model}_positive{track}` 布尔中间列为基础做 groupby-sum, 统计该模型该轨下判定为正面的文章篇数, 得到本家族的 `{model}_pos_count_{track}` 九列; `pipeline/panel/codebook.py` 只负责该列的元数据标签/描述文本, 不参与任何 groupby/聚合计算。

【方法学与计算】
三个模型的输出结构不完全对称: finbert_cn 与 fin_sent_zh 是三分类 (负面/中性/正面), finbert2 是二分类 (负面/正面, 无中性类, 概率列补 NaN 中性占位以对齐 schema)。计数口径统一为「该模型该轨 argmax 标签落在正面类的篇数」——三分类模型正面类是 softmax 三选一里的赢家, 二分类模型正面类是 sigmoid/softmax 二选一里的赢家, 二者在"谁被判正面"这一问题上语义一致, 但因类别数不同, 同等条件下二分类模型的正面判出率结构性高于三分类模型 (少了中性这一竞争类别), 因此本家族只在同模型跨年/跨行/跨轨比较有意义, 不建议直接跨模型比较绝对计数水平, 三模型是互为稳健性的并排轨而非可加总的同尺度指标。分母口径: 计数的样本基础是该模型该轨下已成功推理 (未落入 `{sn}_infer_failed_{track}` 失败哨兵) 的文章集合, 推理失败的文章标签为 None、不计入任何类别的计数, 与"该文章被判为非正面"严格区分——这一点是本家族区别于用概率阈值切分的其它测度族的关键: pos_count 是标签层面的硬计数, 不是概率层面的软累加 (软累加对应家族外的 `{model}_pos_sum_{track}` — 各文章正面概率的加总)。三轨语义遵循项目统一约定: full=标题+正文全文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句窗口 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认±1句); 若某篇文章无银行∧金科同句共现, `content_ss` 回退为全文 (`ss_is_fallback=True`, 镜像 ctx 回退语义); FINTECH_AC 词典未加载时 `*_is_fallback` 全 True、ctx/ss 优雅退化为对 full 文本的重复推理。留篇门控 (是否算作"一篇银行金科报道"计入分析样本) 采用 full-only 口径 (2026-06-29 定案): 只看该文章 `llm_verified_full == True`, ctx/ss 轨的 pos_count 是在这一 full-only 行宇宙子集之上、各自对不同文本范围重新推理并计数的条件稳健性轨/测度轨, 不额外扩大或缩小样本行宇宙。

【文献定位】
本家族方法学谱系直接承袭金融文本 BERT 情感分类的主线: Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 提出的 FinBERT 证明领域微调的 Transformer 编码器在金融文本情感抽取上显著优于通用词典法与通用预训练模型, 是本项目引入 BERT 路线情感测度的方法学锚点; finbert2 模型本身对应 Xu et al. (2025, KDD '25) 面向金融领域部署差距设计的双向编码器, 是项目内自训练/私有模型的方法学来源。三模型并排、per-model 独立降级 (finbert2 缺席仅掉自身族, 另两个 HF 公开模型照跑) 的设计呼应多模型三角验证的方法学传统, 保证结论不被单一分类器的训练语料或架构偏误驱动。将「硬计数」与「软概率累加」并列作为互补测度, 呼应 Loughran & McDonald (2016, *Journal of Accounting Research*) 对文本分析中"计数类"(count-like) 度量与连续强度度量各有信息含量、不应相互替代的方法学讨论, 也与 Cohn, Liu & Wardlaw (2022, *Journal of Financial Economics*) 关于金融研究中计数数据 (count data) 特有分布性质与推断陷阱的提醒相印证——pos_count 本质上是非负整数值的计数变量, 在面板回归中若作为因变量宜留意其分布形态, 不能默认线性高斯假设照搬。⚠ 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨或三模型混进同一 over-identified 的 Hansen J 检验; ss 轨的回退语义严格镜像 ctx 轨 (无共现→全文兜底、标记 fallback 位), 不是独立的第三套判据。 近期前沿文献进一步支撑把分类器选择本身作为并排的规格维度而非取单一模型定论。Turetken 与 Leippold (2026) 对两个主流金融情感模型 (FinBERT 与生成式 Fin-GPT) 施加语义保持的白盒对抗扰动, 发现二者的情感标签预测均被大比例翻转, 说明金融情感分类器的标签输出并非稳固不变——本家族因而对同一构念保留三个模型各自的 argmax 正面篇数并排, 而不把任一模型的判定当作无误差的构念真值。⚠ 该文为英文基准数据集上的句/篇级对抗鲁棒性评测 (其结论是两模型均脆弱, 未报告模型间脆弱性差异), 所涉 Fin-GPT 亦非 BERT 架构, 无 bank-year 面板聚合、无 count 与 probability-sum 之分, 亦不涉及中文语料与三轨文本范围, 故仅支持上述弱结论。Hsu 与 Hsu (2026) 提出 Semantic Stability Protocol, 把同一 LLM 的重复输出视作一组 AI coders, 以 Krippendorff's α 量化并治理零样本分类的模型内随机性: 在 424 篇中文新闻的五分类任务上原始输出 α=0.8485, 约 20 次多数票聚合后 α 升至 0.94 以上, 佐证把 α/κ 类信度指标施用于 AI 分类器在中文新闻语料上的标签输出, 是方法学上已被接受的效度前置程序。⚠ 该文为单模型内的重复运行稳定性 (其 AI coders 即同一模型的多次跑), 未做任何跨模型比较, 故不构成本项目「多个模型间一致性作为效度证据」这一模型间维度的直接先例; 其对象是零样本生成式 LLM 而非微调 BERT (本项目三模型还存在 2 vs 3 分类基数差异), 且全程为标签级信度, 未触及概率口径与面板聚合。应用语境上, Wang、Xiao、Wang 与 Wang (2025) 在中国语境下从新闻报道抽取情感并聚合到企业层面用于债务成本实证, 是「中文新闻情感 → 实体-年测度」这一形态的近期同域实例, 用以锚定本家族正面篇数列族的应用语境而非其具体算法。⚠ 原文实体为一般上市公司、DV 为债务成本, 未区分计数与概率和两种口径, 无 per-model 多模型并排, 亦无三轨文本范围切分。三模型各自 just-identified 并排、既不取平均也不加总的处理, 其一般性方法论立场可参照 Ke 与 Nesbit (2024): 该文证明 LDA 的参数不可识别、文本派生量的后验结论会随先验设定改变, 并给出刻画该结论取值区间的算法, 由此主张把建模者未被数据识别的选择显式化, 报告结论在其上的取值范围而非只报一个点估计。⚠ 原文研究的是单一 LDA 模型内的先验敏感性与不可识别性, 不是不同分类器之间的模型选择问题, 未评估任何 BERT 或神经情感分类器, 亦不涉及计数/概率和口径与中文语料, 因此不是本族 per-model 并排的 method-origin。
## VAR: fin_sent_zh_pos_count_ctx

【变体差分】
本列取模型 fin_sent_zh (基于 Financial PhraseBank 微调的三分类中文金融情感 BERT, 类别=负面/中性/正面) 在 ctx 轨 (标题+银行实体窗口拼接文本, `prepend_title` 物化于 stage 14) 上的推理结果, 统计该 bank-year 单元内 argmax 标签为「正面」的文章篇数。与家族 canonical (full 轨) 相比, ctx 轨只把模型的注意力窗口限定在银行实体出现附近的文本片段, 剔除了正文中与目标银行无关的段落, 因此当一篇报道同时涉及多家机构、多个议题时, ctx 轨给出的正面计数更贴近"围绕该银行本身的语气", 是抵御报道话题稀释噪声的稳健性轨。ctx 与 full 的差异集中体现在长文章、多主体报道场景; 短文章 (全文即银行实体窗口) 两轨数值高度重合。fin_sent_zh 是三分类模型, 正面计数与中性、负面计数三分天下, 结构上不会因为"没有中性类"而系统性偏高, 这一点与二分类的 finbert2 形成对照。样本基础同样限定在该模型 ctx 轨推理未失败、且文章满足 full-only 留篇门控的子集; ctx 轨若因上游 `content_ctx` 缺失而回退全文, 对应文章的 ctx 计数会与 full 计数高度趋同但不必然相等 (回退发生在文本层, 模型仍是独立一次推理, 存在滑动窗口切分边界的微小差异)。⚠ 本列与 full/ss 轨同名列各自 just-identified 并排、互为稳健性, 禁止混入同一 over-identified Hansen J。

## VAR: fin_sent_zh_pos_count_full

【变体差分】
本列是家族 canonical 轨: 模型 fin_sent_zh 在 full 轨 (标题+正文全文) 上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数, 覆盖整篇报道的全部文本信息, 不做实体窗口或同句窗口的裁剪。留篇门控直接作用于 full 轨: 一篇文章是否被计入"银行金科报道"分析样本, 只看其 `llm_verified_full == True` (2026-06-29 full-only 口径定案), 因此 full 轨本身既是文本范围最广的一轨, 也是决定行宇宙的基准轨, ctx/ss 轨是在这一行宇宙子集上的条件稳健性测度, 不反向影响 full 轨的样本构成。fin_sent_zh 是三分类模型 (负面/中性/正面), 正面判出需要在三个类别的 softmax 竞争中胜出, 相比二分类的 finbert2 存在更高的判正门槛, 这是跨模型比较 pos_count 绝对水平时必须留意的结构性差异, 也是本家族坚持"各模型互为稳健性、不分主次"而非取平均或加总的原因。样本基础为该模型 full 轨推理未失败 (未落入 `fin_sent_zh_infer_failed_full` 哨兵) 的文章; 推理失败的文章标签为 None, 既不计入正面也不计入负面/中性, 与"模型判定为非正面"是两回事。full 轨的另一层意义在于它是跨模型、跨三轨比较时的锚定基准: 由于 ctx/ss 均是相对 full 收紧文本范围得到的稳健性轨, 研究者通常先看 full 轨的水平与趋势, 再用 ctx/ss 检验结论是否对文本范围选择敏感, 若三轨方向一致而幅度有差, 属预期的构念收紧效应, 不构成对结论稳健性的挑战; 若三轨方向相反, 才需要回到原文逐篇核查。

## VAR: fin_sent_zh_pos_count_ss

【变体差分】
本列取模型 fin_sent_zh 在 ss 轨 (标题+银行∧金科同句窗口拼接文本) 上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数。ss 轨是三轨中文本范围最窄的一轨, 只保留银行实体与金科词在同一句子 (默认 ±1 句半径, `config/filtering.yaml::context_window.ss_sentence_radius`) 共同出现的片段, 目标是捕捉"银行与金融科技被直接放在一起讨论"这一更严格构念下的语气, 是比 ctx 轨更进一步收紧的稳健性轨。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 退化为全文 body、`ss_is_fallback` 标记为 True (与 ctx 共享同一套 `n_articles` 分母口径), 该文章在 ss 轨上的推理实质上等价于对全文重新跑一次, 因此其正面判定可能与 full 轨接近但不保证相同 (滑动窗口切分点不同、模型仍独立推理一次)。若 FINTECH_AC 词典未加载 (`FINTECH_AC=None`), `*_is_fallback` 全部为 True, ss 轨整体优雅退化为对全文的重复推理, 这一状态在极端配置缺失场景下仍保证不崩溃但会削弱 ss 轨的判别力。⚠ ss 轨与 full/ctx 轨同名列各自 just-identified 并排, 禁止混入同一 over-identified Hansen J, 三轨差异是构念收紧梯度而非可加总的信息源。与三分类的 finbert_cn 相比, fin_sent_zh 在同一 ss 收紧窗口下的正面判定分布可用于交叉校验: 若两个三分类模型在同句共现子样本上给出高度一致的正面计数模式, 说明"银行与金科同时出现的句子倾向正面语气"这一发现不依赖具体模型的训练语料差异, 是本项目多模型三角验证设计的直接应用场景之一。

## VAR: finbert2_pos_count_ctx

【变体差分】
本列取模型 finbert2 (项目自训练/私有微调的二分类中文金融 BERT, 类别仅负面/正面, 无中性类) 在 ctx 轨上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数。finbert2 是二分类模型, 少了中性类别的竞争, 结构上更容易把边缘/中性倾向的文本判为正面或负面二者之一, 因此其 pos_count 绝对水平天然高于同等条件下三分类模型 (finbert_cn、fin_sent_zh) 的 pos_count, 三模型之间刻意不设 ensemble headline、不做加权平均, 正是为了避免这种类别数结构差异被掩盖或错误折算。finbert2 依赖本地私有权重 (经 `.env` 的 `FINBERT2_MODEL_DIR` 解析), 若该路径未配置或无效, 该模型在 stage 23 会被优雅跳过, 此时本列 (以及 finbert2 家族的其余两轨) 全部 bank-year 单元取值为 NaN, 属于 per-model 独立降级 (仅 finbert2 自身族缺席, finbert_cn 与 fin_sent_zh 两个公开 HF 模型照常产出), 而非 co-primary 嵌入那种 both-or-neither 的连坐规则。ctx 轨在 finbert2 上的构念含义与在其它两模型上一致: 把注意力窗口限定在银行实体附近文本, 抵御多主体报道的话题稀释。研究者在使用本列做跨模型稳健性检验时, 应优先关注该列与 full/ss 两轨内部的方向一致性, 而非直接与三分类模型的 ctx 轨绝对水平相比, 后者受类别数结构差异影响、不具备可比的零点与量纲。

## VAR: finbert2_pos_count_full

【变体差分】
本列取模型 finbert2 在 full 轨上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数, 是 finbert2 这一模型分支的 canonical 轨 (覆盖标题+全文)。由于 finbert2 是二分类模型 (负面/正面, 无中性), 其正面概率列直接是 1 减负面概率 (二者互补), 因此本列与该模型的 `finbert2_pos_full`/`finbert2_pos_sum_full` 等概率族列高度相关但构念上不同: 本列是硬计数 (有多少篇被判正面), 概率族列是软强度 (正面把握有多强、加总起来多大), 二者互为频次视角与强度视角的互补, 不可相互替代。finbert2 依赖 `FINBERT2_MODEL_DIR` 本地私有权重解析, 未配置时优雅跳过整个模型 (三轨全部降级为 NaN), 这是 finbert2 相对另两个公开 HF 模型 (finbert_cn、fin_sent_zh) 特有的可用性风险, 复现/审计本列时须先确认该环境变量在生产机上已正确指向本地模型目录。full 轨同时也是留篇门控 (full-only, 2026-06-29) 直接作用的一轨, 决定该 bank-year 单元纳入分析的文章总体。作为 finbert2 分支的基准轨, 本列在稳健性分析中承担与 fin_sent_zh_pos_count_full、finbert_cn_pos_count_full 并排比较的角色: 三者方向一致即可支持"正面报道篇数上升"这一结论不依赖具体 BERT 模型选择, 三者不应被折算为单一均值指标使用。此外, 由于 finbert2 是项目自有私有模型, 其训练语料构成与另两个公开 HF 模型不完全重叠, 本列在实证解读中还承担一层额外功能: 检验私有微调模型与公开模型在同一语料上的判断是否收敛, 若长期观察到系统性偏离, 应作为该私有模型迭代训练的诊断信号予以记录, 而非直接归咎于测度设计本身。

## VAR: finbert2_pos_count_ss

【变体差分】
本列取模型 finbert2 在 ss 轨 (标题+银行∧金科同句窗口) 上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数, 是 finbert2 分支在最严格文本收紧构念下的正面计数。ss 轨回退语义镜像 ctx: 无银行∧金科同句共现时 `content_ss` 退化为全文、`ss_is_fallback=True`, finbert2 在该文章上的推理等价于对全文的又一次独立推理。由于 finbert2 是二分类模型, 结构性判正率高于三分类模型, 这一偏差在 ss 轨 (文本更短、语境信息更稀薄) 下可能被进一步放大——短窗文本中缺乏中性表述的语境线索时, 二分类模型更容易在正/负两极之间做出判断, 这是解读本列时需要留意的度量特性, 也是三模型互为稳健性并排、不设跨模型统一阈值或 ensemble 的设计初衷之一。finbert2 模型本地私有权重未配置时本列整体降级为 NaN, 独立于另两个 HF 模型的 ss 轨产出。由于 ss 轨样本主要由银行∧金科同句共现的短片段构成, finbert2 在该轨上的判正结果对于研究"金科相关表述本身的语气倾向"这一更细粒度问题最具参考价值, 但解读时仍需结合 `ss_is_fallback` 标记, 排除因无共现而回退全文的样本, 避免把"整篇正面"误读为"同句表述正面"。

## VAR: finbert_cn_pos_count_ctx

【变体差分】
本列取模型 finbert_cn (基于 yiyanghkust/finbert-tone-chinese, HuggingFace 公开三分类中文金融情感 BERT, 类别=中性/正面/负面) 在 ctx 轨上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数。finbert_cn 与 fin_sent_zh 同为三分类架构, 但训练语料与调优目标不同 (finbert_cn 面向通用金融文本语调, fin_sent_zh 基于 Financial PhraseBank 微调), 两者在同一篇文章上的判正结果可能不一致, 这正是本项目坚持三模型并排互为稳健性、而非只用单一 BERT 的核心理由: 证明结论不被任一具体模型的训练语料或架构选择驱动。ctx 轨把推理文本范围收紧到银行实体窗口, 相比 full 轨更能剥离与目标银行无关的报道段落的语气干扰, 属于稳健性轨而非替代轨。finbert_cn 是两个公开 HF 模型之一, 生产环境需要 `strict_models=true` 默认下的 fail-loud 加载保证 (非预期加载失败会直接报错终止, 与 finbert2 的"未配置优雅跳过"语义不同), 本地重跑还需设置 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` 避免联网拉取模型失败。finbert_cn 与 fin_sent_zh 在 ctx 轨上的对照是本家族跨模型稳健性检验的核心场景之一: 若两模型在同一收紧文本窗口下产生系统性分歧 (例如一方持续高估正面篇数), 提示需要回到训练语料或标注体系差异做进一步归因, 而不应简单取二者均值掩盖分歧, 这也是家族刻意不设跨模型 ensemble headline 的方法学立场。

## VAR: finbert_cn_pos_count_full

【变体差分】
本列取模型 finbert_cn 在 full 轨上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数, 是 finbert_cn 这一模型分支的 canonical 轨。finbert_cn 是三分类模型, 判正需要在负面/中性/正面三个 softmax 类别中胜出, 与同为三分类的 fin_sent_zh 结构对称、与二分类的 finbert2 结构不对称, 三者之间的计数水平差异部分源自类别数本身而非语调判断力的强弱, 这是解读跨模型比较时的首要注意事项。full 轨样本以留篇门控 (full-only, 2026-06-29) 圈定的行宇宙为基础, 该模型该轨推理失败 (`finbert_cn_infer_failed_full`) 的文章标签为 None, 不计入本列任何计数。finbert_cn 依赖 HuggingFace 公开权重, `strict_models=true` 默认配置下非预期加载失败会 fail-loud 报错而非静默跳过, 保证本列取值在生产环境要么完整产出、要么显式报错, 不存在静默半产出的中间态。作为 finbert_cn 分支的基准轨, 本列与另两模型的 full 轨 (fin_sent_zh_pos_count_full、finbert2_pos_count_full) 并排构成三模型互为稳健性的核心比较组, 三者共同支撑"某银行某年正面报道篇数上升"这一结论不依赖单一分类器的选择; 若三者方向一致但幅度不同, 应归因于类别数结构差异与训练语料差异, 而非视为矛盾证据。finbert_cn 作为最早被引入项目的公开 HF 金融情感模型, 其 full 轨判定长期被用作三模型对照组的参照系, 后续新增模型 (fin_sent_zh、finbert2) 的判正倾向常先与本列比对, 确认差异来源于模型本身而非流水线接入方式的差异 (三模型共用同一套滑动窗口切片与置信度加权池化逻辑, 仅 tokenizer 与权重不同)。

## VAR: finbert_cn_pos_count_ss

【变体差分】
本列取模型 finbert_cn 在 ss 轨上的推理结果, 统计 bank-year 内 argmax 标签为「正面」的文章篇数, 是 finbert_cn 分支在银行∧金科同句最严格文本收紧下的正面计数。ss 轨回退语义与 ctx 轨对称一致: 无银行∧金科同句共现的文章, `content_ss` 退化为全文, `ss_is_fallback=True`, finbert_cn 在该文章上等价于对全文重新推理一次, 与 full 轨结果可能高度接近但不完全相同 (滑动窗口切分边界、独立一次前向推理)。finbert_cn 与另一三分类模型 fin_sent_zh 在 ss 轨上的一致度是跨模型稳健性判断的重要依据: 若两个三分类模型在同一收紧文本窗口下给出高度一致的正面计数模式, 说明结论对具体模型选择不敏感; 若出现系统性分歧, 则提示需要结合原始文本核查。finbert_cn 属于公开 HF 模型, 无需本地私有权重, 但本地离线重跑仍需 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` 环境变量, 否则会因联网请求模型卡片失败而中断该模型的三轨推理 (finbert2 因本地权重不受此影响)。本列的样本基础同样限定在 full-only 留篇门控圈定的行宇宙子集之上, 且要求该文章确实存在银行∧金科同句共现 (否则计入 fallback 而非真正意义上的"同句"样本)。在解读跨行业/跨年份趋势时, 建议同时参照 finbert_cn_pos_count_ctx 与 finbert_cn_pos_count_full 两轨, 三轨呈现的收紧梯度 (full 最宽松、ctx 居中、ss 最严格) 本身也是一种可用于识别语气来源"扩散程度"的辅助信息: 若正面判定在三轨中保持稳定, 说明正面语气弥漫于整篇报道; 若仅在 full 轨出现而 ctx/ss 轨消失, 提示正面语气可能来自与目标银行无直接关联的段落。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Turetken, A. C., & Leippold, M. (2026). Battle of transformers: Adversarial attacks on financial sentiment models. Journal of Banking & Finance, 188, 107698. https://doi.org/10.1016/j.jbankfin.2026.107698
Hsu, H.-Y., & Hsu, M.-L. (2026). Semantic stability protocol: intercoder reliability for zero-shot classification via AI coders. Quality & Quantity. https://doi.org/10.1007/s11135-026-02832-9
Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
Ke, S., Montiel Olea, J. L., & Nesbit, J. (2024). Robust machine learning algorithms for text analysis. Quantitative Economics, 15(4), 939-970. https://doi.org/10.3982/qe1825
<!-- rendered-citations:end -->
