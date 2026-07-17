---
family_id: F295
columns:
- fin_sent_zh_neu_app_ctx
- fin_sent_zh_neu_app_full
- fin_sent_zh_neu_app_ss
- fin_sent_zh_neu_ctx
- fin_sent_zh_neu_full
- fin_sent_zh_neu_ss
- fin_sent_zh_neu_tech_ctx
- fin_sent_zh_neu_tech_full
- fin_sent_zh_neu_tech_ss
- finbert_cn_neu_app_ctx
- finbert_cn_neu_app_full
- finbert_cn_neu_app_ss
- finbert_cn_neu_ctx
- finbert_cn_neu_full
- finbert_cn_neu_ss
- finbert_cn_neu_tech_ctx
- finbert_cn_neu_tech_full
- finbert_cn_neu_tech_ss
unit: 无量纲概率均值 (0-1 区间, bank-year 层对文章级 softmax 中性概率取算术平均)
formula: bank-year 内该模型该轨该(可选)分类子集下文章级 neu 概率的算术平均; 分母为该模型自身 verified 篇数 (per-model 独立分母, 非共识 n_articles_llm_valid)
producer: pipeline\sentiment\tone_berts.py (文章级推理) ; pipeline\panel\codebook.py::_BERT_MODEL_RE / _bert_model_match (面板列识别与标注)
upstream: [22_words_tone.parquet, 23_bert_tone.parquet]
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
- doi: "10.18653/v1/N19-1423"
  type: book
  authors: "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K."
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)"
  pages_or_artno: "4171-4186"
- doi: "10.1080/07421222.2018.1440766"
  type: journal
  authors: "Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W."
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: "Journal of Management Information Systems"
  vol: "35"
  issue: "1"
  pages_or_artno: "220-265"
- doi: "10.1145/3711896.3737219"
  type: book
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.1287/mnsc.2022.00261"
  type: "journal"
  authors: "Chen, L., & Mankad, S."
  year: 2025
  title: "A Structural Topic and Sentiment-Discourse Model for Text Analysis"
  venue: "Management Science"
  vol: "71"
  issue: "7"
  pages_or_artno: "5767-5787"
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
本家族测度"中性概率" (neu), 即中文金融 BERT 模型对一篇报道判为"既非正面也非负面"的 softmax 概率, 在 bank-year 层取算术平均。中性概率与净语调 (net_tone = pos − neg) 测度的是完全不同的构念维度: net_tone 捕捉语气的方向与强度, 而 neu 捕捉的是语气强度本身的缺席——即市场关注到某银行×金科事件、媒体确实报道了, 但报道语气本身未被模型判为明显偏向褒或贬的"事实陈述型"占比。高 neu 均值意味着该银行当年的相关报道以中性叙事为主 (如公告、数据披露、监管备案类新闻), 低 neu 意味着报道语气两极分化更明显。这一维度是三条独立情感测量路线 (LLM 投票 / 词典法 / BERT 神经网络) 之一——BERT 路线——的天然副产品: 三分类模型输出的 softmax 本身就含正/负/中性三个概率, neu 只是此前 F 系列已覆盖的 pos/neg 概率族之外, 对第三个类别概率的对称补齐, 供研究者检验主结论是否被"中性样本占比"这一构成性因素驱动。

本家族仅覆盖 fin_sent_zh 与 finbert_cn 两个三分类模型; FinBERT2 是本项目自训练的二分类模型 (仅负面/正面), 无原生中性类别, 其 neu 列在文章级恒为 NaN、不落入本家族的 18 列组合。这是 per-model 独立降级的直接体现: 三模型 co-equal 互为稳健性、不分主次, 但每个模型的类别体系是模型自身架构决定的, 不强行对齐——finbert2 缺席中性维度不影响另外两个模型照常提供该测度, 也不代表 finbert2 本身推理失败或被跳过 (finbert2 在 pos/neg net_tone 等家族中正常参与)。

【方法学与计算】
上游 stage 23 (`tone_berts.py`) 依次为 fin_sent_zh、finbert_cn、finbert2 三个模型执行批量推理: 文本先经 `prepend_title` 按轨拼接 (full=标题+全文正文, ctx=标题+content_ctx 银行实体窗口, ss=标题+content_ss 银行∧金科同句窗口), 超长文本按 `WINDOW_STRIDE_RATIO=0.5` 半重叠滑窗切片 (单窗 ≤512 token 含特殊符, 有效正文 ≤510 token), 各窗 logits 按置信度加权池化 (`Σ(conf_k·logits_k)/Σconf_k`) 合并为文章级单一 softmax 分布, 三分类模型的第三个分量即为 neu 概率; 批级推理异常先逐篇重试一次, 仍失败才写失败哨兵 (标签 None / 概率 NaN), 与真正的空文本 (`bert_num_windows_{track}=0`) 严格区分, 二者不可混淆为同一种缺失。

下游 stage 40 面板聚合 (`codebook.py::_BERT_MODEL_RE`) 用正则在候选列名前锚定模型短名 (`^(fin_sent_zh|finbert_cn|finbert2)_`), 匹配 `neu` 等 metric 关键字, 并识别可选的三轨后缀 (`_full/_ctx/_ss`)。本家族的 `_app`/`_tech` 中缀是 P4 (Gomber 2018 视角) 分类维度的产物: LLM 分类 (locus 维度) 依据文章正文关键词将验证通过的文章判入"应用场景" (app, 面向客户/业务功能的金科应用) 与"底层技术" (tech, 支撑应用的底层技术基础设施) 两个互斥子集; BERT neu 概率在这两个子集内部分别取均值, 与不带 `_app`/`_tech` 中缀的全样本 (canonical) 均值并排, 供研究者检验中性语气占比是否随报道聚焦的技术层次 (前台应用 vs 后台技术) 系统性变化。这一切分与三轨 (full/ctx/ss) 正交——三轨切的是文本抽取范围, `_app`/`_tech` 切的是文章主题子集, 二者可同时施加于同一列名 (如 `fin_sent_zh_neu_app_ctx`)。

三轨的既有铁律在本家族同样适用: full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁止把同一构念的三轨版本混入同一 over-identified Hansen J 检验。留篇门控口径遵循 2026-06-29 起的 full-only 规则——一篇报道是否被计入"一篇银行金科报道"只看 `llm_verified_full == True`, ctx/ss 轨的样本行集合是 full 轨留篇集合的子集, 各轨 per-track 独立算列; ss 轨若上游未准备好银行∧金科同句共现窗口 (`content_ss` 回退为全文 body, `ss_is_fallback=True`), 则该篇的 ss 轨 neu 值实质退化为该模型在全文上的推理结果, 与 ctx 轨的回退语义完全镜像——这不是缺陷, 而是三轨架构对"当年没有同句窗口可用"这一常见情形的优雅降级。

【文献定位】
BERT 类神经网络文本情感分类方法的方法学基础见 Devlin et al. (2019) 提出的双向 Transformer 预训练范式, 以及 Huang, Wang & Yang (2023) 在 *Contemporary Accounting Research* 上验证的金融领域专用 FinBERT 架构——本项目采用的 finbert_cn (yiyanghkust/finbert-tone-chinese) 与 finbert2 均沿此路线针对中文金融语料微调。三条独立情感测量路线 (LLM 投票 / 词典法 / BERT) 互相印证的方法学立场延续了 Huang, Wang & Yang (2023) 在验证 FinBERT 有效性时所强调的跨方法比对精神——该文将 FinBERT 输出与人工标注及传统词典法系统比对以确立效度, 本项目将这一比对逻辑扩展为三条并行路线共同为媒体语调这一核心构念提供互证, 而非仅以单一模型的输出作为最终定论。将文章按"应用场景"与"底层技术"两个分析层次切分的做法呼应 Gomber, Kauffman, Parker & Weber (2018) 在 *Journal of Management Information Systems* 上对金融科技创新的分层框架——该文区分了金融科技的技术使能层与业务应用层, 本项目据此构造 P4 (Gomber locus) treatment 维度, 中性概率的 app/tech 子集均值即是该分层框架在情感测度层面的自然延伸。 在测度形态的选择上, Chen 与 Mankad (2025) 提出的 STS 结构主题-情感模型引入文档级的连续情感-话语潜变量并允许其被文档级协变量解释, 使篇级情感以连续量而非硬标签进入正式统计推断; 本家族保留篇级 softmax 中性概率再于 bank-year 内取均值、而非仅用 argmax 标签, 与这一以连续情感量为基本单位的前沿做法同向。⚠ 边界: 该文的情感量是贝叶斯生成模型的连续后验潜变量, 与 BERT softmax 的类别概率语义不同, 其模型不设中性类别, 亦不存在篇级概率在实体-期内取均值的聚合步骤 (其用法是潜变量对协变量回归), 语料为评论/话语文本而非中文银行新闻, 故仅为连续概率口径提供一般性佐证, 不构成本族中性概率均值的方法来源。三模型各自 just-identified 并排、不折算为单一 ensemble 的处理, 在方法论立场上可参照 Ke 与 Nesbit (2024): 该文证明 LDA 参数不可识别、文本派生量的后验结论会随先验设定改变, 并给出刻画结论取值区间的算法, 主张把建模者未被数据识别的选择显式化并报告结论在其上的取值范围, 而非只报一个点估计。⚠ 原文研究的是单一 LDA 模型内的先验敏感性, 而非不同分类器之间的模型选择, 未评估任何 BERT 或神经情感分类器, 亦不涉及概率均值口径与中文语料, 故只提供立场层面的支持, 不是本族 per-model 并排的 method-origin。
## VAR: fin_sent_zh_neu_app_ctx

【变体差分】
本列取模型 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的三分类金融情感模型), 中性概率 neu, 限定在"应用场景" (app) 分类子集内, 文本抽取轨道为 ctx (标题+银行实体窗口正文)。与不带 `_app` 中缀的 `fin_sent_zh_neu_ctx` 相比, 本列的分母是该银行当年被 LLM locus 分类判为"应用场景"报道且 fin_sent_zh 推理成功的篇数, 而非该模型 ctx 轨全部 verified 篇数, 二者样本量不同、不可直接比较绝对水平, 只可比较标准化系数或占比结构。ctx 轨相对 full 轨的差异在于文本抽取范围收窄到围绕目标银行实体的窗口, 剔除了同篇报道中与该银行无关的段落, 因此更聚焦于该银行本身在"应用场景"叙事下的中性语气占比; 与同模型 full/ss 轨的 app 子集列互为稳健性并排, 禁止混入同一 over-identified 识别方程。

在解读上, 本列适用于研究者想要控制"文本抽取范围"这一潜在混淆因素、同时仍关心应用场景叙事下中性语气占比的场景: 相较 full 轨, ctx 轨剔除了同篇报道中可能提及其他银行或无关主题的段落, 理论上应更贴近该银行本身的应用场景相关叙事; 但由于 ctx 轨的实体窗口截取算法本身也可能引入截断噪声 (窗口边界处的句子被硬切), 该列不应被当作比 full 轨"更准确"的版本, 而应与 full/ss 轨并列汇报以展示结论的稳健性边界。样本覆盖上, 本列继承留篇门控 full-only 铁律: 只要某篇报道通过 `llm_verified_full` 且被 locus 分类判入应用场景子集, 无论其 ctx 轨窗口是否命中该银行, 都计入分母 (fin_sent_zh 推理若失败则计入失败哨兵而非静默丢弃), 这保证了 app 子集在 ctx/full/ss 三轨间的行宇宙一致, 便于跨轨比较结构而非仅比较均值水平。

## VAR: fin_sent_zh_neu_app_full

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 限定在"应用场景"分类子集, 文本轨道为 full (标题+全文正文, 留篇门控的锚定轨)。这是本家族中 app 子集三轨里的主口径列: 由于留篇判定 (`llm_verified_full`) 只看 full 轨, 本列的样本行集合即为该银行当年被判入应用场景子集的全部报道 (无 ctx/ss 的窗口截断), 是 app 子集测度中信息保留最完整的一支。与不带 `_app` 中缀的 `fin_sent_zh_neu_full` 相比, 差异纯粹在于样本子集范围 (应用场景子集 vs 全样本), 二者共享同一模型、同一轨、同一分母口径逻辑 (仅子集大小不同); 与同列的 ctx/ss 轨版本、以及 tech 子集版本共同构成互为稳健性、不分主次的并排族, 各自 just-identified, 不得混入同一 Hansen J 检验框架。

本列的实践意义在于: 由于 full 轨是留篇门控的锚定轨, 该银行当年被判入应用场景子集的报道数量本身 (即分母大小) 就是一个有信息量的辅助量——若某银行某年应用场景报道极少, 说明媒体当年对该银行的金科叙事更多聚焦在底层技术或未被 locus 分类覆盖的其他角度, 此时本列的中性概率均值应结合样本量一并解读, 避免把小样本下的极端值误读为系统性语气变化。本列与词典法 (F 系列词典族) 及 LLM 投票法 (P4 locus 相关族) 在应用场景子集上的对应测度构成跨方法三角验证的一环, 三条路线若在同一子集上给出方向一致的信号, 可显著增强"应用场景报道语气结构"这一具体经验发现的稳健性。

## VAR: fin_sent_zh_neu_app_ss

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 限定在"应用场景"分类子集, 文本轨道为 ss (标题+银行∧金科同句共现窗口)。ss 轨是三轨中文本抽取范围最窄、判据最严格的一支——只保留银行实体与金科词在同一句 (±1 句半径可配) 内共现的窗口; 若该银行当年在应用场景子集下某篇报道不存在这样的同句窗口, 则该篇的 `content_ss` 回退为全文 body、`ss_is_fallback=True`, 此时该篇对本列的贡献实质上退化为该模型在全文上的中性概率推理结果, 这一回退语义与 ctx 轨镜像对称、非缺陷。本列与 `fin_sent_zh_neu_app_full`/`fin_sent_zh_neu_app_ctx` 互为稳健性并排; 三轨分母 (verified 篇数) 亦逐轨独立计, ss 轨若回退比例较高, 该列数值会更接近 full 轨版本, 属预期现象。

研究者在使用本列时应留意: ss 轨的严格同句判据 (银行实体与金科词汇在同一句内共现, 句半径可经 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1) 天然筛选出的是"银行与金科高度绑定叙事"的语句片段, 相较 full/ctx 轨捕捉的文本范围更小、更聚焦, 因此本列理论上应比同模型 full/ctx 轨版本更敏锐地反映"银行与金科同框叙事"本身的中性语气占比, 但也因样本行文本更短而增加窗口切片和推理噪声的相对权重。本列与 `finbert_cn_neu_app_ss` 构成跨模型对照, 二者共享相同的样本子集定义 (应用场景 + 同句判据), 是检验"应用场景×同句叙事"这一具体交叉构念是否被单一模型驱动的关键对照列。研究者在跨轨比较时还应留意窗口切片机制本身的影响: full 轨与 ctx 轨文本更长, 超过 510 token 有效正文的概率更高, 触发滑动窗口切片与置信度加权池化的比例也相应更高; ss 轨文本 (标题+同句窗口) 通常更短, 多数篇一次前向即可覆盖全文, 无需切片, 因此本列的推理机制相对更"干净", 较少受窗口池化权重估计误差的干扰, 这是 ss 轨相对 full/ctx 轨在方法论上的一个隐性优势, 尽管样本量代价与之相抵。

## VAR: fin_sent_zh_neu_ctx

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 不限定分类子集 (canonical 全样本), 文本轨道为 ctx。这是本家族 fin_sent_zh 一侧的基准测度之一: 分母为该银行当年 fin_sent_zh 在 ctx 轨上 verified 且推理成功的全部篇数, 不做 app/tech 主题切分。与 `_app_ctx`/`_tech_ctx` 两个子集版本相比, 本列的样本范围是二者的并集 (在 LLM locus 分类覆盖到的报道范围内), 因此其数值介于两个子集版本之间, 可用作衡量子集切分是否改变整体中性语气结构的对照基准。与同模型 full/ss 轨的全样本版本共同构成三轨并排族, 互为稳健性、不分主次。

作为全样本基准, 本列的一个重要用途是校验 app/tech 子集切分是否引入选择性偏误: 若 `fin_sent_zh_neu_app_ctx` 与 `fin_sent_zh_neu_tech_ctx` 的加权平均 (按各自样本量加权) 明显偏离本列, 说明 locus 分类未覆盖到的报道 (既非明确应用场景亦非明确底层技术的报道, 例如纯监管政策解读类新闻) 在中性语气上具有系统性特征, 这类"剩余样本"的存在正是本列 (全样本) 与两个子集列不能相互替代的原因——全样本列涵盖 locus 分类无法归类的边界报道, 子集列则聚焦可明确归类的核心样本, 二者服务于不同的稳健性检验目的。

## VAR: fin_sent_zh_neu_full

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 不限定分类子集, 文本轨道为 full。本列是本家族 18 列中信息含量最完整的一支: 样本范围覆盖该银行当年全部通过留篇门控 (`llm_verified_full`) 且 fin_sent_zh 推理成功的报道, 文本抽取不做实体窗口或同句窗口截断。作为 canonical 全样本 + 主轨的组合, 本列常被用作 app/tech 子集列、以及 ctx/ss 轨版本的参照基准, 但在识别策略上仍与其余 17 列 co-equal 并排, 不构成任何意义上的"更优先"版本——三轨与主题子集之间均是互为稳健性关系。分母口径遵循 per-model 独立分母原则, 与共识层面的 `n_articles_llm_valid` 不是同一个量。

由于 full 轨是留篇门控锚定轨且文本抽取范围最完整, 本列在方法论上承担了"最少信息损失版本"的角色: 相较 ctx 轨可能因实体窗口截断丢失上下文, 相较 ss 轨可能因严格同句判据大幅缩水样本, full 轨保留了记者写作时的完整叙事结构, 神经网络模型能够利用更长的上下文进行分类, 理论上分类置信度 (滑动窗口池化权重) 也更稳定。但完整文本也意味着无关段落 (如同篇报道提及其他银行或宏观背景) 会被一并纳入推理输入, 这是 full 轨相对 ctx/ss 轨在"聚焦度"上让渡的代价, 三轨互为稳健性设计正是为吸收这一权衡而存在, 不存在单一"最优"轨道。

由于本列不做任何 app/tech 主题子集限定, 其分母恰为该银行当年 fin_sent_zh 模型在 full 轨上 verified 且成功推理的全部篇数, 与 pos/neg 概率对应列共享完全相同的行宇宙——三个类别概率理论上对每一篇文章恒和为 1, 因此本列可与其余两个概率类别列联合构成一个完整的三元单纯形 (simplex) 描述, 用于更细致的分布形状分析 (如是否存在类似 BERT 分布形状族的熵、偏度等衍生统计量, 尽管本家族本身只提供一阶均值而非高阶矩)。这一构念区分提示: 若研究者的真实兴趣是"语气强度"而非"语气方向", 应优先选用本列而非 pos/neg 差值构造的 net_tone 类测度, 二者服务于不同的理论问题, 不可相互替代或混用。

本列的分母与该银行当年 `fin_sent_zh_pos_ss`/`fin_sent_zh_neg_ss` (归属其他家族) 的分母完全一致, 三列共享同一行宇宙 (ss 轨、全样本), 仅提取的 softmax 分量不同, 因此在同一份面板中并列这三个概率列不会引入任何额外的样本选择差异, 是本项目跨家族列联合使用时较为安全的一种组合方式。

## VAR: fin_sent_zh_neu_ss

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 不限定分类子集, 文本轨道为 ss。ss 轨要求银行与金科词严格同句共现, 是三轨中判据最严的一支; 无同句共现的报道其 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 分母仍以该银行当年全部 verified 且推理成功的篇数计 (与 full 轨共享分母口径基础, 但个别篇的输入文本因回退而与 full 轨趋同)。本列与 `fin_sent_zh_neu_full`/`fin_sent_zh_neu_ctx` 并排互为稳健性; 三者禁止混入同一 over-identified Hansen J 方程, 亦不与 `_app`/`_tech` 子集列混同 (子集切分与轨道切分是两个正交维度)。

本列在实证使用上宜作为"银行与金科紧密绑定叙事"下中性语气占比的最严格版本: ss 轨判据本身即是 stage 13 共现硬过滤生产口径 (`sentence_radius=1`) 在情感测度层面的进一步收紧应用, 只是 stage 13 是硬过滤丢行、本列是同轨内的软测度差异。若某银行当年 ss 轨回退比例 (即 `ss_is_fallback=True` 的篇数占比) 很高, 说明该银行的报道虽然通过了银行∧金科邻近共现的硬过滤, 但银行实体与金科词汇很少真正落在同一句内, 此时本列的信息增量相对 full 轨有限, 应结合回退比例本身 (若面板中留存) 一并解读研究结论的稳健性。本列与该银行当年的 `fin_sent_zh_pos_ss`/`fin_sent_zh_neg_ss` (归属其他家族) 共享完全相同的行宇宙 (ss 轨全样本), 三列联合使用时不会引入额外的样本选择差异, 是本项目跨家族列联合分析时较为安全的一种组合方式, 可用于构造该银行—年份"报道语气强度是否显著偏离中性"的辅助判据。

## VAR: fin_sent_zh_neu_tech_ctx

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 限定在"底层技术" (tech) 分类子集内, 文本轨道为 ctx。tech 子集对应 LLM locus 分类中判为聚焦底层技术基础设施 (而非面向客户的应用层) 的报道, 与 app 子集互斥、共同覆盖 locus 分类可判定的全部报道。本列与 `fin_sent_zh_neu_app_ctx` 构成同轨对照——二者样本互斥, 若研究者关心"面向底层技术的报道是否比面向应用场景的报道更倾向中性叙事" (如技术升级公告类新闻本身即偏事实陈述), 可比较二者标准化系数, 但不应将其直接相减当作单一构念的差值使用 (家族内已有专门的 `tone_gap_tech_app` 族处理该类差值构念, 本列不承担该角色)。与同模型 full/ss 轨的 tech 子集列互为稳健性并排。

从构念区分的角度, 本列与 pos/neg 概率对应的 tech 子集列 (属其他家族) 共同刻画该银行当年"底层技术"叙事下的完整情感分布结构: neu 高、pos 与 neg 均低意味着底层技术类报道多为技术规格介绍或系统升级公告等事实陈述; 而若 neu 低、pos 或 neg 单侧偏高, 则说明底层技术报道本身也承载了明显的评价色彩 (如安全事件曝光或技术突破宣传)。本列单独看只反映情感强度的缺席维度, 完整解读需与同模型同轨的 pos/neg 概率列联合考察, 三者构成同一 softmax 分布的互补切面, 理论上三者之和恒为 1 (数值实现受浮点精度影响可能有极小偏差)。

## VAR: fin_sent_zh_neu_tech_full

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 限定在"底层技术"分类子集, 文本轨道为 full。作为 tech 子集三轨中信息保留最完整的一支 (留篇门控锚定轨), 本列是 tech 侧的主口径列, 与 app 侧的 `fin_sent_zh_neu_app_full` 在同一轨、同一模型下并排对照。分母为该银行当年被判入 tech 子集且 fin_sent_zh 推理成功的篇数; 若该银行当年 tech 子集报道量很少, 均值的抽样噪声会相应更大, 这是子集切分固有的样本量代价, 与全样本版本 `fin_sent_zh_neu_full` 并排使用可缓解该问题。

本列作为 tech 子集主口径, 也是 `tone_gap_tech_app` 族在 full 轨上做差值构造时的潜在参照对象之一 (尽管该差值族目前主要消费的是 LLM 语调而非 BERT 概率), 提示两条测量路线在"应用—技术叙事差异"这一具体研究问题上具备并行扩展的空间。使用本列时应注意: tech 子集样本量若在某些银行×年份接近于零 (例如某小型银行当年报道全部集中在应用场景, 未见底层技术相关报道), 该银行—年份的本列观测值应为缺失而非人为填零, 面板层面的缺失处理逻辑由下游分析脚本负责, 本列本身不做任何形式的强制填补。

## VAR: fin_sent_zh_neu_tech_ss

【变体差分】
本列取 fin_sent_zh 模型的中性概率 neu, 限定在"底层技术"分类子集, 文本轨道为 ss。同时施加两层收窄: 主题上限定到 tech 子集, 文本范围上限定到银行∧金科同句共现窗口 (无共现则回退全文、镜像 ctx 语义)。这是 fin_sent_zh 一侧 18 种组合中样本量通常最小的几列之一, 数值噪声相对更大, 使用时应结合同模型的 `_tech_full`/`_tech_ctx` 版本一并解读, 三者互为稳健性、不分主次, 禁止单独进入 over-identified 识别方程。

本列是 fin_sent_zh 一侧 18 种组合中主题 (tech) 与文本范围 (ss 同句判据) 双重收窄的极端点, 其数值波动主要来自两个来源: 一是子集样本量本身偏小带来的抽样噪声, 二是同句共现判据本身相对严格导致高比例回退到全文推理。研究者若在正式实证中使用本列, 建议同时报告该银行—年份的分母篇数 (若在面板中留存或可从上游 parquet 复原), 以便读者判断均值的可靠程度; 单纯依赖点估计而不披露样本量, 容易在极端稀疏的银行—年份组合上得出被少数几篇报道驱动的伪结论。ss 轨在同句判据下的窗口切片需求通常远低于 full/ctx 轨, 绝大多数样本一次前向即可完成推理, 但这一优势建立在样本量大幅缩水的代价之上, 是否值得优先采用取决于具体研究问题对"叙事聚焦度"与"统计效力"的权衡取舍, 并无普适的最优答案。

## VAR: finbert_cn_neu_app_ctx

【变体差分】
本列取模型 finbert_cn (yiyanghkust/finbert-tone-chinese, HuggingFace 公开三分类中文金融情感模型), 中性概率 neu, 限定在"应用场景"分类子集, 文本轨道为 ctx。finbert_cn 与 fin_sent_zh 是两个独立训练来源、独立词表的三分类模型 (fix g-berts-01 后二者分词互不共享, 避免跨词表 token id 错配), 二者的 neu 概率在同一篇文章上可能出现系统性差异, 这正是 per-model 稳健性设计的用意所在——若某一结论仅在其中一个模型上成立, 说明结论可能被该模型特有的判别边界驱动而非真实构念信号。本列与 `finbert_cn_neu_app_full`/`finbert_cn_neu_app_ss` 并排互为稳健性, 亦与 `fin_sent_zh_neu_app_ctx` 构成跨模型稳健性对照, 呼应 Huang, Wang & Yang (2023) 在效度验证中采用的多来源比对思路在 BERT 侧的体现。

finbert_cn 采用的 yiyanghkust/finbert-tone-chinese 是公开发布、被广泛引用的中文金融情感基座模型, 其训练语料与标注体系与 fin_sent_zh 所用的 Financial PhraseBank 微调路线不完全相同, 二者对"中性"这一类别的判别阈值天然存在模型特异性差异——这正是本项目坚持 per-model co-equal 并排、不做 ensemble 折叠的核心理由: 中性判定本身比正/负极性判定更依赖模型对"是否存在明确情感倾向"这一决策边界的把握, 不同预训练语料和微调策略会系统性影响该边界的位置, 单一模型的中性概率不足以支撑稳健结论。

## VAR: finbert_cn_neu_app_full

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 限定在"应用场景"分类子集, 文本轨道为 full。作为 finbert_cn 一侧 app 子集的主口径列, 分母为该银行当年被判入应用场景子集且 finbert_cn 推理成功 (未落入失败哨兵) 的篇数。finbert_cn 若因外部依赖失败 (`strict_models=true` 默认下非预期加载失败会 fail-loud), 该模型整族列 (含本列) 会随之缺席, 但这与 finbert2 因 `FINBERT2_MODEL_DIR` 未配而优雅跳过是两种性质不同的缺失路径——前者是硬故障, 后者是预期降级, 二者均不影响 fin_sent_zh 一侧照常产出。本列与同模型 tech 子集、以及不同轨版本互为稳健性并排。

本列与 `fin_sent_zh_neu_app_full` 构成本家族里 app 子集 + full 轨的跨模型直接对照, 是判断"应用场景报道语气结构"这一具体经验发现是否具备跨模型稳健性的核心一对列。若研究结论 (例如"应用场景报道的中性占比在金科投入较高的银行更低") 在两个模型上方向一致、统计显著性相近, 可较有信心地将其视为真实构念信号而非模型伪影; 若两个模型给出方向相反或显著性差异悬殊的结果, 应在稳健性讨论中如实披露这一分歧, 而非选择性只报告支持假设的模型。

## VAR: finbert_cn_neu_app_ss

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 限定在"应用场景"分类子集, 文本轨道为 ss。同时叠加主题子集收窄 (app) 与文本范围收窄 (银行∧金科严格同句), 是 finbert_cn 一侧组合样本量偏小的列之一; 无同句共现窗口的报道回退为全文推理结果, 回退比例随银行/年份的报道密度而变, 属结构性特征非数据缺陷。与 `finbert_cn_neu_app_full`/`finbert_cn_neu_app_ctx` 并排互为稳健性、不分主次, 三者禁止混入同一 over-identified Hansen J。

与 fin_sent_zh 一侧的对应列 `fin_sent_zh_neu_app_ss` 相比, 本列在同一子集 (应用场景) 与同一轨 (ss) 下提供跨模型对照; 由于 finbert_cn 与 fin_sent_zh 的分词器互不共享 (fix g-berts-01 的直接后果), 即便输入同一段 `content_ss` 文本, 二者的滑窗切分边界也可能不同, 导致窗口级池化权重分布存在差异, 这是跨模型比较时需要意识到的技术层面差异来源, 与模型本身语义判别能力的差异是两回事, 不应混为一谈。

本列在样本量上是本家族 18 列组合中的极端点之一——同时施加应用场景子集限定与银行∧金科严格同句判据两重收窄, 加之 finbert_cn 与 fin_sent_zh 相比在部分银行—年份组合上的推理成功率存在细微差异 (受各自失败哨兵触发条件影响), 实际可用观测的银行—年份数可能进一步少于同轨全样本列, 使用前应核实该银行—年份组合是否确有足够篇数支撑一个有意义的均值估计。

## VAR: finbert_cn_neu_ctx

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 不限定分类子集, 文本轨道为 ctx。作为 finbert_cn 一侧的全样本基准列之一, 分母为该银行当年 finbert_cn 在 ctx 轨上 verified 且推理成功的全部篇数。与 fin_sent_zh 对应列 (`fin_sent_zh_neu_ctx`) 构成跨模型对照: 二者理论上应测度同一构念 (中性语气占比), 若二者相关性高则增强该构念测度的信度, 若出现系统性偏离则提示模型特异性判别边界的存在, 这正是三 BERT 模型 co-equal 并排设计而非简单取 ensemble 均值的原因——中性概率不像 pos/neg net_tone 那样有对应的 ensemble headline, 保留原始 per-model 差异本身即是设计意图。

本列作为全样本基准, 亦是判断 finbert_cn 侧 app/tech 子集切分是否存在系统性选择偏误的对照点: 与 `finbert_cn_neu_app_ctx`、`finbert_cn_neu_tech_ctx` 按各自样本量加权平均后应大致回收到本列附近, 若出现明显偏离, 提示 locus 分类无法归类的"剩余报道" (既非典型应用场景亦非典型底层技术) 在中性语气上具有区别于两个子集的特征, 这类边界样本本身也是值得进一步定性考察的对象。

本列文本抽取范围为标题+围绕目标银行实体的窗口正文, 相对 full 轨剔除了同篇报道中与该银行无关的段落, 理论上应更聚焦于该银行本身的媒体叙事, 但实体窗口的边界识别依赖上游命名实体识别与规则抽取的准确度, 窗口边界处的句子可能被硬性截断而丢失部分语境, 这是 ctx 轨相对 full 轨在信息完整性上让渡的代价, 与 ss 轨的取舍逻辑相似但收窄程度更温和。

## VAR: finbert_cn_neu_full

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 不限定分类子集, 文本轨道为 full。作为 finbert_cn 一侧信息保留最完整的基准列, 样本覆盖该银行当年全部通过留篇门控且 finbert_cn 推理成功的报道。与 fin_sent_zh 对应的 `fin_sent_zh_neu_full` 构成本家族里两个模型 canonical 全样本、主轨版本的直接对照, 二者均无 ensemble headline (不同于 LLM 三家的 `llm_vote_tone` 共识列), 使用时应逐模型分别汇报、并排陈述稳健性, 而非取平均后当作单一测度使用。

作为 finbert_cn 一侧信息最完整的基准列, 本列与 fin_sent_zh 的对应列 `fin_sent_zh_neu_full` 共同构成本家族"跨模型一致性"评估的第一入口: 项目内建的模型间一致性度量 (`tone_validation.py` 中 Krippendorff's α 与 Cohen's κ, 后者须先重映射非负码以避免与 −1 缺标哨兵冲突) 虽以离散标签 (label) 为主要输入, 但连续概率列 (含本列) 提供了更细粒度的一致性证据——两个模型的 neu 概率若在银行—年份层面高度相关, 说明中性判定这一相对模糊的类别边界在不同模型间仍具有可复制的信号成分, 而非纯粹的模型噪声。

本列的文本输入 (标题+全文正文) 与该银行当年被媒体报道的完整叙事一一对应, 不做任何主题子集或窗口截断, 是本家族方法论光谱中"信息保留最大化"的端点。与之相对, `finbert_cn_neu_tech_ss`/`finbert_cn_neu_app_ss` 等收窄组合列构成"信息保留最小化"的另一端点, 二者及其间的其余 16 列共同构成一个完整的稳健性梯子, 供研究者在正文或附录中系统展示结论对样本范围与主题限定的敏感度。

## VAR: finbert_cn_neu_ss

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 不限定分类子集, 文本轨道为 ss。ss 轨要求银行与金科词严格同句共现, 无共现报道回退为全文推理 (`ss_is_fallback=True`), 分母口径与 full 轨一致 (逐篇成功推理即计入)。本列与 `finbert_cn_neu_full`/`finbert_cn_neu_ctx` 三轨并排互为稳健性, 亦与 `fin_sent_zh_neu_ss` 构成跨模型稳健性对照; 铁律同前——三轨与跨模型两个维度均各自 just-identified, 禁止混入同一 over-identified 识别方程。

ss 轨在 finbert_cn 全样本口径下的表现值得单独关注: 由于 ss 轨判据 (银行∧金科严格同句) 是 stage 13 硬过滤生产口径的软化复刻, 已通过硬过滤留存的文章天然具备较高的同句共现概率, 因此 finbert_cn 全样本 ss 轨的回退比例 (`ss_is_fallback=True` 占比) 预期整体低于任意子集切分后的回退比例——子集切分会使某些银行—年份的报道量本就稀少, 进一步降低命中同句窗口的绝对篇数, 这是本列 (全样本) 与 `_app_ss`/`_tech_ss` 两个子集列在数据质量特征上的一个系统性差异, 解读时应予以考虑。

本列与 fin_sent_zh 对应的全样本 ss 轨列 `fin_sent_zh_neu_ss` 共同构成本家族里"最严判据 + 全样本"组合的跨模型对照, 是检验"银行∧金科高度绑定叙事下中性语气占比"这一具体经验结论是否具备跨模型稳健性的核心一对列; 若二者在方向与显著性上高度一致, 可为该结论提供比单一模型更强的证据支撑。

## VAR: finbert_cn_neu_tech_ctx

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 限定在"底层技术"分类子集, 文本轨道为 ctx。与 `finbert_cn_neu_app_ctx` 构成同轨同模型下 app/tech 两个互斥子集的直接对照, 用于检验 finbert_cn 判定的中性语气占比是否随报道聚焦层次 (前台应用 vs 后台技术) 系统性变化。与 fin_sent_zh 对应的 `fin_sent_zh_neu_tech_ctx` 构成跨模型对照, 二者若方向一致可增强"技术层报道更偏中性叙事"这类假设的证据强度, 若不一致则需谨慎对待, 不可仅凭单一模型下结论下判断。

从软件实现角度, finbert_cn 与 fin_sent_zh 对同一子集 (tech) 的同一轨 (ctx) 文本各自独立分词、独立跑批量推理、独立写回文章级列, 再由 stage 40 codebook 的 `_BERT_MODEL_RE` 正则各自识别为不同的面板列; 两条推理路径除共享上游 `content_ctx` 抽取逻辑与 LLM locus 分类结果外, 在模型层面完全解耦, 不存在任何权重共享或结果相互校准的步骤, 因此本列与 `fin_sent_zh_neu_tech_ctx` 之间的相关性 (若存在) 完全反映的是二者对同一构念的独立测量收敛, 而非算法层面的人为耦合。

从留篇门控角度看, 本列样本行的入选资格由 full 轨的 `llm_verified_full` 决定, ctx 轨本身不参与"是否算一篇银行金科报道"的判定, 只负责在已入选的报道范围内提供另一种文本抽取视角; 这意味着本列与 full 轨的 `finbert_cn_neu_tech_full` 共享完全相同的分母 (同一批被判入 tech 子集且 finbert_cn 推理成功的篇数), 二者差异纯粹来自输入文本范围, 是研究"文本抽取范围本身是否影响测度结果"这一方法论问题的干净对照。

## VAR: finbert_cn_neu_tech_full

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 限定在"底层技术"分类子集, 文本轨道为 full。作为 finbert_cn 一侧 tech 子集的主口径列, 与 `finbert_cn_neu_app_full` 在同一轨下互斥对照, 与 `fin_sent_zh_neu_tech_full` 构成跨模型对照。分母为该银行当年被判入 tech 子集且 finbert_cn 推理成功的篇数, 子集样本量偏小年份该列的抽样噪声相应更大, 建议结合全样本版本 `finbert_cn_neu_full` 一并解读。

本列作为 finbert_cn 侧 tech 子集主口径, 与 fin_sent_zh 对应列 `fin_sent_zh_neu_tech_full` 构成本家族里 tech 子集 + full 轨的跨模型直接对照; 若研究结论涉及"底层技术叙事的中性程度是否随时间或银行规模变化", 应同时报告本列与其跨模型对照列的结果, 而非仅依赖单一模型。此外本列与同模型的 app 子集列 `finbert_cn_neu_app_full` 构成 locus 二分类下的完整对照, 二者样本互斥、共同逼近全样本列 `finbert_cn_neu_full`, 是本家族方法论结构中"轨道×子集×模型"三维组合下最具信息量的一组基准列之一。

在稳健性叙事的写作实践中, 本列常与 `finbert_cn_neu_app_full`、`fin_sent_zh_neu_tech_full`、`fin_sent_zh_neu_app_full` 四列共同出现在同一张附录表格内, 以 2×2 (子集 × 模型) 的形式展示某一具体经验发现在不同主题范围与不同模型选择下是否保持方向一致; 这种并排陈述方式比单独报告任意一列更能说服审稿人相信结论并非某一特定建模选择的产物, 也是本项目 per-model 与 locus 双梯子设计的核心价值所在。

## VAR: finbert_cn_neu_tech_ss

【变体差分】
本列取 finbert_cn 模型的中性概率 neu, 限定在"底层技术"分类子集, 文本轨道为 ss。这是本家族 18 列组合中主题收窄 (tech) 与文本收窄 (ss 严格同句判据) 同时叠加的 finbert_cn 侧对应列, 通常是样本量最小、数值最易受少数篇报道驱动的一支; 无同句共现的报道回退为全文推理结果。使用时须与同模型的 `_tech_full`/`_tech_ctx` 版本、以及 fin_sent_zh 对应列并排解读, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。

本列是本家族 18 列中主题、文本范围、模型三个维度均取"收窄一侧"组合的代表, 其对应的另一极端是全样本 + full 轨 + 另一模型的组合 (如 `fin_sent_zh_neu_full`), 二者在方法论光谱上处于两端, 中间由其余 16 列填补各种组合。研究者若做规格曲线式的稳健性展示 (specification curve), 本列适合作为"最严格设定"一端的代表点, 与"最宽松设定" (全样本 full 轨) 端点共同界定结论在整个规格空间内的稳定区间, 这一用法与本项目其余梯子族 (词典消融、政治词权重、罕见词频次 cutoff) 的规格曲线呈现思路一致。

本列与 fin_sent_zh 对应的 `fin_sent_zh_neu_tech_ss` 共享完全相同的子集定义 (底层技术) 与相同的轨道判据 (银行∧金科严格同句), 二者理论上应测度同一狭窄构念——"银行与金科在同句层面紧密绑定的底层技术叙事"下的中性语气占比。若二者数值高度相关且方向一致, 可作为该细分构念存在真实信号 (而非模型伪影) 的有力证据; 若样本量过小导致二者相关性弱, 亦应如实说明, 不宜强行解读为构念测量失败——小样本下的弱相关本身即是样本量不足的自然结果, 与测度效度问题需加以区分。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT). https://doi.org/10.18653/v1/N19-1423
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25). https://doi.org/10.1145/3711896.3737219
Chen, L., & Mankad, S. (2025). A Structural Topic and Sentiment-Discourse Model for Text Analysis. Management Science, 71(7), 5767-5787. https://doi.org/10.1287/mnsc.2022.00261
Ke, S., Montiel Olea, J. L., & Nesbit, J. (2024). Robust machine learning algorithms for text analysis. Quantitative Economics, 15(4), 939-970. https://doi.org/10.3982/qe1825
<!-- rendered-citations:end -->
