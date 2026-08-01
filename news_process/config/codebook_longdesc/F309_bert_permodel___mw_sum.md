---
family_id: F309
columns:
- fin_sent_zh_负面_mw_sum_ctx
- fin_sent_zh_负面_mw_sum_full
- fin_sent_zh_负面_mw_sum_ss
- finbert2_负面_mw_sum_ctx
- finbert2_负面_mw_sum_full
- finbert2_负面_mw_sum_ss
- finbert_cn_负面_mw_sum_ctx
- finbert_cn_负面_mw_sum_full
- finbert_cn_负面_mw_sum_ss
unit: 无量纲 [0, n_articles] 区间概率总和 (media-weighted 求和, 非归一化占比)
formula: bank-year 内该模型该轨道逐篇"负面"标签概率 neg_i, 按媒体权重 w_i 加权后求和; sum_i (w_i × neg_i), 三模型 (finbert_cn/fin_sent_zh/finbert2) × 三轨 (full/ctx/ss) 并排产出
producer: pipeline\sentiment\tone_berts.py (文章级三轨概率); pipeline\panel\encode.py::BERT_MODELS 驱动的显式聚合循环 (`agg[f'{b}_负面_mw_sum{track}'] = (f'{b}_负面_mw{track}', 'sum')`, 本家族 9 列的真实 producer); pipeline\panel\codebook.py 的通用回退标签/描述生成器 (非 `_BERT_MODEL_RE`/`_bert_model_match` 路径——该正则要求英文 metric token 如 `neg_sum` 且顺序为 model_metric_weight_track, 与本家族"中文 metric token '负面' + metric→weight→'sum'→track"的真实列名顺序不匹配, 对本家族 9 列恒返回 None, 不会命中"BERT 逐模型..."专用标签分支)
upstream:
- 22_words_tone.parquet (词典法阶段输出, 提供三轨文本来源)
- 23_bert_tone.parquet (BERT 阶段输出, 本家族的直接文章级来源)
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
- doi: "10.18653/v1/N19-1423"
  type: journal
  authors: "Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K."
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1"
  pages_or_artno: "4171-4186"
- doi: "10.24963/ijcai.2020/622"
  type: wp
  authors: "Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J."
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
- doi: "10.1016/j.jbankfin.2025.107542"
  type: "journal"
  authors: "Lehkonen, H., Heimonen, K., & Pukthuanthong, K."
  year: 2025
  title: "Media tone is a priced risk factor in currency markets"
  venue: "Journal of Banking & Finance"
  vol: "180"
  pages_or_artno: "107542"
- doi: "10.1287/mnsc.2021.02218"
  type: "journal"
  authors: "Dechow, P., Lawrence, A., Luo, M., & Stamenov, V."
  year: 2024
  title: "Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics"
  venue: "Management Science"
  vol: "70"
  issue: "8"
  pages_or_artno: "5157-5186"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"某一 BERT 情感模型判定某篇报道为负面的概率强度, 在 bank-year 层面按媒体权重累加"这一构念, 属 news_process 情感测度"三条独立路线" (大模型 LLM / 词典法 / BERT 神经网络) 之一的 BERT 路线, 在 per-model 维度上的具体实现。stage 23 (`tone_berts.py`) 用三个中文金融领域预训练 BERT 模型 —— finbert_cn (yiyanghkust/finbert-tone-chinese, 3-class 中性/正面/负面)、fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3-class 模型)、finbert2 (项目私有微调模型, 经 `.env::FINBERT2_MODEL_DIR` 解析, 2-class 负面/正面) —— 各自独立对文章打分, 输出每篇每模型每轨的"负面"标签概率 (记为 neg_i∈[0,1])。这与词典法 (关键词计数/情感词典打分) 和 LLM 三家投票 (语义理解式判定) 在方法论上完全独立: BERT 不依赖人工词表, 而是通过预训练语言模型对整段文本的上下文语义做端到端分类, 三条路线互相印证同一潜在构念 (媒体语调), 共同支撑"结论不依赖单一测量技术"的稳健性论证。本家族在此基础上再加一层"跨模型 per-model 并排": finbert_cn / fin_sent_zh / finbert2 三个模型互为稳健性、不分主次, 不设跨模型 ensemble headline (与 LLM 三家有共识投票 headline `llm_vote_tone` 不同, BERT 路线刻意不做跨模型汇总, 因为三模型训练语料/标签体系/类别数 (2-class vs 3-class) 不完全可比, 强行 ensemble 会引入额外假设)。

【方法学与计算】
文章级计算发生在 stage 23: 对每篇文章, 三轨文本 (full=标题+全文正文 prepend_title 拼接、ctx=标题+银行实体窗口内文本、ss=标题+银行∧金科同句±N窗文本) 各自独立喂入三个 BERT 模型推理。超长文本经滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5`, 50% 重叠, 单窗含特殊 token ≤512、有效正文 ≤510 token), 各窗输出 logits 按置信度加权池化聚合 (`logits *= Σ(conf_k · logits_k) / Σconf_k`, 置信度更高的窗口权重更大), 最终得到该篇该模型该轨的"负面"标签概率。批级推理异常触发逐篇重试一次, 仍失败则写失败哨兵 (概率置 NaN、`{model}_infer_failed_{track}`=True), 与"空文本"(`bert_num_windows_{track}`=0) 严格区分, 不静默污染均值。

面板层聚合的真实 producer 在 `pipeline/panel/encode.py` —— 该模块以 `BERT_MODELS` (finbert_cn/fin_sent_zh/finbert2, per-model SSOT) 为循环变量, 对每个模型/每条轨道显式写出聚合表达式 `agg[f'{b}_负面_mw_sum{track}'] = (f'{b}_负面_mw{track}', 'sum')`, 即把文章级"负面概率 × 媒体权重" (`{b}_负面_mw{track}`) 逐篇求和聚合到 bank-year。需澄清: `pipeline/panel/codebook.py` 内确有一个 `_BERT_MODEL_RE` 正则 (识别形如 `{model}_(pos|neg|neu|net_tone|pos_sum|neg_sum|neu_sum|pos_std)((_vw|_mw|_hw)?)(_full|_ctx|_ss)?` 的英文 metric token 列名), 但该正则要求 metric 段用英文 token (如 `neg_sum`) 且顺序固定为 model_metric_weight_track; 本家族列名是`{model}_负面_mw_sum{track}`——metric 段是中文'负面'、且顺序为 metric→weight('_mw')→'sum'→track, 与该正则字面模式不匹配, 对本家族 9 列 `_bert_model_match()` 恒返回 None, 不会走"BERT 逐模型专用标签"分支, 而是落入 codebook.py 的通用回退标签/描述生成路径。即: 文章级概率产出 (tone_berts.py) → 面板聚合 (encode.py 显式写出, 非正则驱动) → codebook 标签 (通用回退, 非 `_BERT_MODEL_RE` 专用分支) 三段各自独立, 不应混称为同一正则机制的产物。本家族对应 metric=`neg_sum`(中文'负面'对应)、weight tail=`_mw` (media-weighted, 按媒体来源权重加权而非等权/市值加权), 即 bank-year 内把该银行当年所有相关报道 (某一轨道下) 的"负面"概率, 按各篇所属媒体的权重 w_i 加权求和: Σ_i (w_i × neg_i)。与常见的"均值型"语调测度 (如 `{model}_neg`, 逐篇负面概率的加权均值) 不同, `_sum` 后缀的量纲随该 bank-year 报道量/加权基数变化而变化, 不做除以篇数的归一化 —— 它同时携带"负面程度"与"负面报道规模/媒体曝光强度"两层信息, 因此更适合作为"总体负面舆论压力"的强度型指标, 而非"平均语调"的水平型指标; 在回归设计中若要控制报道量效应, 通常需与 `n_articles` 类分母变量同时纳入, 或改用非 `_sum` 的均值变体作对照。留篇门控口径遵循 2026-06-29 起的 full-only 铁律: 一篇报道是否计入"银行金科相关报道"的判定只看 `llm_verified_full`, ctx/ss 轨的行宇宙是 full 留篇集的子集, per-track 列各自照算, 不因某轨缺失而回填 full 值 (BERT 路线本身不产 `_verified` 门控列, 但其纳入的文章行宇宙继承自 full-only 门控后的样本框)。ss 轨遵循镜像 ctx 的回退语义: 若一篇文章无银行∧金科同句共现, `content_ss` 回退为全文 body、`ss_is_fallback`=True, 与 `content_ctx` 的银行实体窗口回退共享同一套"缺共现即退化为更宽文本窗"的设计哲学, 而非直接产生缺失值; `FINTECH_AC=None` 时全体 `*_is_fallback` 置 True, 优雅降级。

【文献定位】
方法论上, 本家族的 BERT 路线直接对应文本情感分析中"预训练语言模型微调"范式, 其 Transformer 双向编码器基础见 Devlin et al. (2019) 提出的 BERT 架构。金融领域专用微调模型的构念先例包括 Huang, Wang & Yang (2023) 在 *Contemporary Accounting Research* 提出的 FinBERT (英文金融文本大语言模型抽取信息), 以及 Liu et al. (2020) 的中文金融 FinBERT。本家族三模型之一 finbert2 的模型来源见 Xu et al. (2025, KDD '25) 关于面向金融领域部署缺口的双向编码器 FinBERT2。三模型并排、互为稳健性不设 ensemble headline 的设计哲学呼应"多方法三角验证" (multi-method triangulation) 传统, 与本项目 LLM 三家投票 (Wang et al. 2023 self-consistency 多模型验证) 共享同一逻辑起点, 但 BERT 路线因模型间标签体系不完全可比 (2-class vs 3-class) 而未设共识 headline。⚠ 口径铁律: BERT 三模型 (finbert_cn/fin_sent_zh/finbert2) 各自 just-identified 并排, 互为稳健性、不分主次, 证明主结论不被任一模型驱动, 禁混进同一 over-identified Hansen J (与三轨 full/ctx/ss、co-primary 嵌入双轨、政治词权重梯度同款铁律); per-model 独立降级 (finbert2 因 `FINBERT2_MODEL_DIR` 未配置而缺席时仅掉自身族, 另两个 HF 模型 finbert_cn/fin_sent_zh 照常产出, 不做 both-or-neither 连坐)。三轨 (full/ctx/ss) 同样各自 just-identified 并排, 禁止混入同一过度识别检验。BERT 深层模型相较词典法在情感判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担情感分类主力提供了顶刊层级的方法学背书。 在测度形态与经济含义层面, 近期两项研究可为本族的媒体加权求和口径提供前沿参照。Lehkonen、Heimonen 与 Pukthuanthong (2025) 以 Refinitiv MarketPsych 指数 (覆盖 2000 家全球媒体与 800 家社交站点的约 700 万篇文本) 构造媒体语调, 证明其是可跨截面定价货币的真实风险因子, 表明由跨媒体文本聚合而成的语调量具备可检验的经济内容, 支撑本族把逐篇负面概率按媒体权重汇总为银行-年语调量的做法。⚠ 该锚点仅止于此一上位命题: 原文语调为比率型 (正负提及净额/总提及) 且取自专有商业 NLP 指数, 构造细节不可复核, 而本族是未归一化的加权概率和; 原文层级为货币 (国别) 聚合、语料为英文国际财经新闻、DV 为汇率收益的因子定价, 与本项目银行×年层级及中文报道语料均不同, 亦未按媒体来源结构赋权。Dechow、Lawrence、Luo 与 Stamenov (2024) 检视五届夏季奥运会, 识别被媒体炒作为奥运受益的概念股, 发现其在奥运周期内收益更高、彼此共动更强, 并在媒体有报道关联该公司的交易日出现成交量与波动率上升, 佐证涉及某主体的媒体报道量是可独立测量、且会驱动市场后果的注意力构念——这正是本族取未归一化求和而非占比的构念理由: 其取值同时随报道篇数与负面程度增长, 刻画的是曝光总量而非平均语气。⚠ 原文以报道篇数/媒体炒作刻画关注, 未见去重来源媒体家数计数, 亦无对数变换与逐年度截面 z 标准化, 主体为 A 股概念股与特定事件窗口而非银行-年全样本, 故不为本族媒体权重的具体构造提供依据。
## VAR: fin_sent_zh_负面_mw_sum_ctx

【变体差分】
本列取模型 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3-class 中文金融情感模型)、轨道 ctx (标题+银行实体窗口文本, `content_ctx` prepend_title 拼接)。ctx 轨相较 full 轨的关键差异是文本范围收窄到银行实体出现位置附近的窗口, 意在剔除长篇报道中与目标银行无关段落对语调判定的稀释/污染, 更聚焦"文中提到该银行处"的局部语气而非全篇整体基调。留篇门控仍以 full-only 判定 (`llm_verified_full`) 为准, ctx 轨行宇宙是该门控下留篇集的子集; ctx 轨若上游 `content_ctx` 缺失该实体窗口 (罕见, 一般由实体识别失败导致), 对应行的该列取值为空, 不回退借用 full 轨数值。作为负面概率的媒体加权总和 (`_mw_sum`), 本列衡量该银行当年在"实体邻近文本"意义下的负面舆论累积强度, 与 fin_sent_zh_负面_mw_sum_full/ss 互为稳健性并排, 不作为彼此的替代或加总关系。使用本列做实证检验时, 应将其理解为"该银行当年在报道中提及处附近的负面情绪总强度", 与全文轨相比它对"报道虽长但涉及该银行的段落很短且负面"这类情形更敏感 —— 全文若被大量与该银行无关的正面或中性内容稀释, full 轨的整体负面概率可能被拉低, 而 ctx 轨会更贴近文本中"关于该银行"的真实语气。由于 fin_sent_zh 模型本身是 3-class 结构 (中性/正面/负面三者概率加总为 1), 本列取值与同模型的中性/正面概率列存在此消彼长关系, 不能脱离该约束单独解读为独立维度。作为 media-weighted 求和量, 本列同时对"报道条数多"与"单篇负面程度高"两种情形给出较高数值, 在解释回归系数时应注意与仅反映水平的均值型语调列 (`fin_sent_zh_neg_ctx` 一类) 区分, 二者虽同源但捕捉的信息侧重不同。

## VAR: fin_sent_zh_负面_mw_sum_full

【变体差分】
本列取模型 fin_sent_zh、轨道 full (标题+全篇正文, prepend_title 拼接原始"内容"列, 不做任何截取), 是三轨中范围最宽的一支, 也是 stage 21 留篇门控 (`llm_verified_full`) 直接锚定的轨道 —— 即"一篇报道是否算作银行金科相关报道"的判定仅看 full 轨的 LLM 验证结果, ctx/ss 轨的行宇宙均为该 full 留篇集的子集。因此 full 轨天然是样本量最大、覆盖最完整的一支, 常被用作三轨中的首要/基准参照, 但按项目铁律三轨仍是"互为稳健性、不分主次"的并排关系, 而非以 full 为主、ctx/ss 为附属稳健性检验。本列的负面概率来自 fin_sent_zh 模型对全篇文本的滑动窗口推理 (长文本超过 510 token 有效正文时切窗、置信度加权池化合并), 按媒体权重加权求和到 bank-year。因 full 轨样本量最大, 该列在跨 bank-year 单元的方差通常也最大, 报道条数悬殊的银行之间数值可比性受报道规模差异影响明显, 若研究设计关注"平均语调"而非"总体舆论压力", 建议同时纳入 `n_articles_llm_valid_full` 一类分母控制或改用非 `_sum` 均值列作对照回归。fin_sent_zh 模型基于 Financial PhraseBank 微调, 该语料源自英文金融文本人工标注, 中文场景下的迁移效果与本土训练的 finbert_cn 存在系统性差异, 在解释本列与 finbert_cn_负面_mw_sum_full 的差异时应优先归因于模型训练语料/决策边界不同, 而非简单视为噪声。本列与 finbert2_负面_mw_sum_full、finbert_cn_负面_mw_sum_full 共同构成 full 轨 BERT 三模型并排族, 三者应作为互为稳健性的三条并行检验汇报, 不建议在同一张表中把三者简单平均或加总为单一"BERT 综合负面度"指标。

## VAR: fin_sent_zh_负面_mw_sum_ss

【变体差分】
本列取模型 fin_sent_zh、轨道 ss (标题+银行∧金科关键词同句或 ±N 句窗内文本, `content_ss` prepend_title 拼接, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1)。ss 轨是三轨中范围最窄、语义最聚焦的一支, 专门捕捉银行与金科词汇同时出现的局部语境语气, 与 ctx 轨 (仅银行实体窗口, 不要求金科词共现) 的判据不同。ss 轨的回退语义镜像 ctx: 若某篇文章不存在银行∧金科同句共现, `content_ss` 回退为全文 body 且 `ss_is_fallback`=True (与 ctx 共享同一 `n_articles` 分母口径); 若上游 `FINTECH_AC` 未配置 (词典缺失), 则全体 `*_is_fallback` 置 True 优雅降级为等同 full 文本, 而非产生缺失。stage 23 的白话说明特别指出"同句段那一路如果上游没准备好就自动只跑前两路", 即 ss 轨在极端情形下可能整体缺席而不阻断 full/ctx 两轨产出。本列作为负面概率媒体加权和, 是三轨中对"银行-金科议题联动语境"最敏感的测度, 与 fin_sent_zh_负面_mw_sum_full/ctx 并排互为稳健性。因 ss 轨的判据比 ctx 轨更严格 (要求银行与金科关键词同句或近句共现, 而非仅要求银行实体出现), 本列在很多 bank-year 单元上会因样本行数少于 ctx/full 轨而波动更大, 尤其在开发/测试环境的短面板 (如早期试跑 T=2) 下容易出现方差退化或恒定值, 属预期现象而非缺陷; 生产语料 (T=19、全量 约 1,819 万条) 规模下该问题显著缓解。研究设计上, 本列适合用于回答"银行与金科议题联动报道的语气是否比泛泛提及更负面"这类更精细的问题, 与 ctx/full 轨形成互补而非替代关系。使用者应留意 `ss_is_fallback` 列: 当该列为 True 时, 对应行的 ss 轨文本实际等同全文, 此时本列与 fin_sent_zh_负面_mw_sum_full 的取值来源高度重叠, 在解读跨轨差异时应结合回退比例判断该差异是否具有实质信息量。

## VAR: finbert2_负面_mw_sum_ctx

【变体差分】
本列取模型 finbert2 (项目私有微调 2-class 模型, 仅区分负面/正面、无独立中性类别, 经 `.env::FINBERT2_MODEL_DIR` 解析加载)、轨道 ctx。finbert2 与另两个模型的关键差异是类别体系为 2-class 而非 3-class, 意味着其"负面"概率与 finbert_cn/fin_sent_zh 的"负面"概率在概念上并非严格同构 (2-class 下负面/正面概率互补加总为 1, 3-class 下负面概率与中性/正面概率三者加总为 1, 中性类别的存在会稀释 3-class 模型的负面概率绝对水平), 这也是本项目刻意不设跨 BERT 模型 ensemble headline 的直接原因之一 —— 三模型的原始概率水平不可直接跨模型比较, 只可比较标准化后的效应量或跨模型一致性方向。finbert2_负面_mw_sum_ctx 衡量 finbert2 模型在银行实体窗口文本上的负面概率媒体加权和。若 `FINBERT2_MODEL_DIR` 未配置或路径无效, stage 23 会优雅跳过该模型 (仅本模型三轨全体缺席, 不影响 finbert_cn/fin_sent_zh 两个公开 HF 模型的产出), 属 per-model 独立降级而非 both-or-neither 连坐。finbert2 是本项目自行微调的私有模型, 相较两个公开 HuggingFace 模型, 其训练语料更贴近本项目所处理的中文银行金科新闻场景, 理论上判定精度更高, 但因其 2-class 类别体系不含中性档, 对语气温和/中性偏正面的报道容易被强制归入正面或负面两端之一, 概率分布形态 (方差、极端值占比) 与 3-class 模型存在系统性差异, 这也是本项目在 BERT 分布形状五族 (`bert_distribution.py`) 中特别对 finbert2 的熵指标做跨模型不可比标注的原因。使用本列时应避免与 finbert_cn_负面_mw_sum_ctx/fin_sent_zh_负面_mw_sum_ctx 直接相减或做差值检验, 而应各自独立汇报回归系数方向与显著性, 以三者一致性而非数值接近程度作为稳健性证据。

## VAR: finbert2_负面_mw_sum_full

【变体差分】
本列取模型 finbert2、轨道 full。作为私有 2-class 模型在最宽文本范围 (标题+全篇正文) 上的负面概率媒体加权和, 本列继承 full 轨的留篇门控基准地位 (`llm_verified_full`), 覆盖样本最完整。因 finbert2 依赖本机私有模型文件, 在未配置 `FINBERT2_MODEL_DIR` 的环境下 (如本机 dev/CI 环境) 本列及其 ctx/ss 姊妹列会整体缺席, 而 finbert_cn_负面_mw_sum_full/fin_sent_zh_负面_mw_sum_full 两个基于公开 HF 模型的列不受影响, 照常产出——这是 per-model 独立降级设计的直接体现, 区别于 co-primary 嵌入双轨的 both-or-neither 连坐语义。在 finbert2 模型正常可用的环境下, 本列理应是三模型 full 轨中唯一基于本土训练语料 (而非迁移自英文语境或通用中文语料微调) 的负面强度测度, 对中国银行业新闻中的行业术语、监管用语、地方性表述有更好的覆盖, 使用者若要论证结果对"模型是否为本地化训练"这一维度稳健, 应重点对照本列与 finbert_cn/fin_sent_zh 两个公开模型对应列的方向一致性, 而非期待数值高度接近。因 finbert2 权重文件不随代码仓库分发, 复现本列结果需要额外获取 `FINBERT2_MODEL_DIR` 所指的私有模型文件, 若无法获取, 该列及其 ctx/ss 姊妹列在复现环境中会整体缺席, 复现者应以 finbert_cn/fin_sent_zh 两族继续验证主结论的稳健性。

## VAR: finbert2_负面_mw_sum_ss

【变体差分】
本列取模型 finbert2、轨道 ss。作为三模型 × 三轨组合中最聚焦 (2-class 私有模型 + 银行金科同句窗口) 的一支, 本列同时叠加两层缩窄: 模型层面 finbert2 的负面概率不含中性类别稀释, 轨道层面 ss 轨仅覆盖银行与金科词汇同句/邻近共现的局部语境。两层缩窄使得本列在样本覆盖 (受 ss 轨回退语义与 finbert2 可用性双重影响) 与概率水平量纲 (2-class vs 3-class) 上均与家族内其余 7 列存在系统性差异, 解读时须同时留意"该银行当年是否有充分的银行-金科联动报道"与"finbert2 模型本身是否在当次运行中可用"两个前提条件, 二者缺一都会使本列退化为缺失或全轨回退到 full 文本口径。作为家族 9 列中信息最"局部"的一支, 本列的经济含义可概括为"银行与金科话题在同一语境中被同时提及时, 项目自训练本土模型判定为负面的强度累积"; 它对识别"金科相关负面报道是否集中在某些特定语境" (如监管处罚、诉讼纠纷等具体事件) 有一定的指向性, 但因样本行数受限, 单独使用时统计效力 (power) 通常弱于 full/ctx 轨对应列, 更适合作为方向性佐证而非主要检验对象。在跨 bank-year 面板回归中, 若某银行当年 ss 轨全部回退为 full 文本 (`ss_is_fallback` 恒为 True), 本列会退化为与 finbert2_负面_mw_sum_full 高度相关但非恒等的序列, 使用者应在稳健性附录中披露该银行-年份的回退比例。

## VAR: finbert_cn_负面_mw_sum_ctx

【变体差分】
本列取模型 finbert_cn (yiyanghkust/finbert-tone-chinese, 公开 HuggingFace 3-class 中文金融语调模型)、轨道 ctx。finbert_cn 是三模型中类别体系与主流英文 FinBERT (Huang, Wang & Yang 2023) 最接近的一支 (3-class 中性/正面/负面), 其负面概率与 fin_sent_zh 的负面概率量纲上可比 (同为 3-class), 但两模型训练语料与微调目标不同 (finbert_cn 面向通用中文金融语调, fin_sent_zh 基于 Financial PhraseBank 微调), 判定口径仍存在系统性差异, 因此二者仍需按 per-model 并排原则各自看待, 不做加总或平均。本列衡量 finbert_cn 在银行实体窗口文本上的负面概率媒体加权和。finbert_cn 由 yiyanghkust 团队公开发布, 是学术界较早、引用较广的中文金融领域 BERT 之一, 其"语调" (tone) 而非单纯"情感" (sentiment) 的训练目标设定, 使其在判定新闻语气 (而非仅判定情绪极性) 上与银行声誉/舆论风险的构念更契合。需要澄清的是, `strict_models=true` 下要求非预期加载失败 fail-loud (而非优雅跳过) 是 `config/sentiment.yaml` 中对全部公开 HF 模型统一生效的全局配置约束, fin_sent_zh 同样受此约束覆盖, 并非 finbert_cn 独有的特性; finbert_cn 在本家族及 `encode.BERT_MODELS` 中位列三模型之首, 只是配置条目物理排列顺序的结果, 与其是否触发 fail-loud 之间不存在因果关系——真正决定分流路径的是"公开 HF 模型 (finbert_cn/fin_sent_zh, 加载失败即 fail-loud)"与"私有微调模型 (finbert2, `FINBERT2_MODEL_DIR` 未设/无效时优雅跳过)"之间的判据, 而非模型在列表中的排位。本列作为 ctx 轨结果, 相较 full 轨更能反映"银行被提及处附近"的具体语气, 在存在同一篇报道内多家银行被提及、且语气不一致的场景下 (如"A银行表现稳健, B银行则面临风险"), ctx 轨比 full 轨更能准确归因到目标银行本身, 而非被同篇报道中其他银行的语气交叉污染。

## VAR: finbert_cn_负面_mw_sum_full

【变体差分】
本列取模型 finbert_cn、轨道 full。finbert_cn 作为三模型中率先加载且被 `strict_models=true` 默认要求 fail-loud (非预期加载失败即报错, 而非静默跳过) 的公开 HF 模型之一, 其 full 轨列在正常运行环境下应始终产出 (除非上游 22 阶段词典法输出或 21 阶段留篇门控导致行宇宙为空)。本列是家族内样本覆盖最完整、量纲与主流金融 BERT 文献最直接可比的一支, 常作为三模型跨模型一致性检验 (Cohen's κ / Krippendorff's α, 见 `tone_validation.py`) 中的参照对象之一, 但铁律仍要求其与 fin_sent_zh_负面_mw_sum_full/finbert2_负面_mw_sum_full 三者并排、不分主次, 禁止在同一过度识别的 Hansen J 检验中混用。由于 finbert_cn 加载失败会触发 fail-loud (直接报错终止而非静默跳过), 本列在任何成功完成的 stage 23 运行中都应有完整产出, 缺失通常指向上游 22 阶段词典法输出或 21 阶段留篇门控导致该 bank-year 无符合条件的文章行, 而非模型本身的可用性问题——这与 finbert2 因私有权重缺失而缺席的情形在诊断路径上应加以区分。研究者若在稳健性附录中汇报"三 BERT 模型 full 轨负面强度总和"的一致性检验, 本列通常是解释力最稳定、跨模型比较基准意义最强的一支, 但仍需遵守本家族反复强调的"各自 just-identified 并排"铁律, 不应仅凭本列结果就替代另外两模型的独立汇报。

## VAR: finbert_cn_负面_mw_sum_ss

【变体差分】
本列取模型 finbert_cn、轨道 ss。作为公开 3-class 模型在银行-金科同句局部语境上的负面概率媒体加权和, 本列继承 ss 轨的回退语义 (无同句共现 → 回退全文 body 且标记 `ss_is_fallback`) 与 finbert_cn 模型本身相对稳定的可用性 (公开 HF 模型, 非私有权重依赖), 在家族 9 列中属于"轨道缩窄但模型可用性最有保障"的组合, 适合作为 ss 轨内跨模型比较的锚点之一, 但解读跨模型差异时仍须遵守"只比标准化效应量方向、不比原始概率水平"的既定口径, 因 finbert_cn 与 fin_sent_zh 即便同为 3-class, 训练语料与决策边界仍不同构。作为家族最后一列, 本列与 finbert_cn_负面_mw_sum_ctx/full 共同构成该模型的三轨并排组, 三者应联合汇报以展示"负面语调结论是否随文本范围收窄而改变方向"这一稳健性证据链: 若三轨系数方向一致、显著性随文本收窄 (full→ctx→ss) 逐步增强, 通常可解读为该负面语调确实与银行-金科议题的具体语境相关, 而非泛化自整篇报道的噪声; 反之若仅 full 轨显著而 ctx/ss 轨消失, 则应审慎对待该发现是否受报道中非目标段落驱动。ss 轨小样本情形下 (尤其早期试跑 T=2 短面板) 出现的零方差或极端值应在稳健性表格脚注中明确标注为轨道特性而非数据质量问题。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1, 4171-4186. https://doi.org/10.18653/v1/N19-1423
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20) No. 4513-4519 [Working Paper]. https://doi.org/10.24963/ijcai.2020/622
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
Dechow, P., Lawrence, A., Luo, M., & Stamenov, V. (2024). Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics. Management Science, 70(8), 5157-5186. https://doi.org/10.1287/mnsc.2021.02218
<!-- rendered-citations:end -->
