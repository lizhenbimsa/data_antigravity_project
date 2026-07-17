---
family_id: F305
columns:
- fin_sent_zh_正面_hw_sum_ctx
- fin_sent_zh_正面_hw_sum_full
- fin_sent_zh_正面_hw_sum_ss
- finbert2_正面_hw_sum_ctx
- finbert2_正面_hw_sum_full
- finbert2_正面_hw_sum_ss
- finbert_cn_正面_hw_sum_ctx
- finbert_cn_正面_hw_sum_full
- finbert_cn_正面_hw_sum_ss
unit: 无量纲加权概率和 (羊群权重加权后的正面概率累加值, 无自然单位/无上下界封顶)
formula: bank-year 内逐篇 {model}_正面_{track} 概率 (BERT softmax 输出) 先乘该篇羊群权重 hw, 再对同 bank-year 求和; 三模型 (finbert_cn/fin_sent_zh/finbert2) × 三轨 (full/ctx/ss) 全排列产 9 列
producer: pipeline\sentiment\tone_berts.py (阶段23, 文章级 BERT 推理产逐篇正面概率) ; pipeline\panel\codebook.py (panel 聚合层 _BERT_MODEL_RE 匹配 pos_sum 族 + hw 加权尾缀, herd_decay 权重来自阶段24)
upstream:
- 22_words_tone.parquet (阶段22 词典法情感输出, 提供 标题/内容/content_ctx/content_ss 文本源)
- 23_bert_tone.parquet (阶段23 三模型三轨 BERT 概率列)
- 24_herd_decay 羊群权重 (herd weight, 用于 hw 加权臂)
citations:
- doi: "10.1145/3711896.3737219"
  type: wp
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
  venue: Contemporary Accounting Research
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1093/rfs/hhad044"
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: The Review of Financial Studies
  vol: "36"
  issue: "12"
  pages_or_artno: "4919-4964"
- doi: "10.18653/v1/N19-1423"
  type: wp
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: "Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)"
  pages_or_artno: "4171-4186"
- doi: "10.1287/mnsc.2022.00261"
  type: "journal"
  authors: "Chen, L., & Mankad, S."
  year: 2025
  title: "A Structural Topic and Sentiment-Discourse Model for Text Analysis"
  venue: "Management Science"
  vol: "71"
  issue: "7"
  pages_or_artno: "5767-5787"
- doi: "10.1007/s42521-024-00107-2"
  type: "journal"
  authors: "Groß-Klußmann, A."
  year: 2024
  title: "Learning deep news sentiment representations for macro-finance"
  venue: "Digital Finance"
  vol: "6"
  issue: "3"
  pages_or_artno: "341-377"
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

【构念与来源】
本家族刻画的构念是「银行—金科报道正面情感强度的羊群加权累计量」, 由阶段23 (`pipeline/sentiment/tone_berts.py`) 产出的文章级 BERT 概率列出发, 在 bank-year 面板聚合层 (`pipeline/panel/codebook.py`) 累加而成。三个中文金融领域 BERT 模型 — finbert_cn (yiyanghkust/finbert-tone-chinese, 3 分类 中性/正面/负面)、fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3 分类模型)、finbert2 (FinBERT2, 项目自持的 2 分类 负面/正面私有微调模型, 经 .env `FINBERT2_MODEL_DIR` 解析, 未配置时优雅跳过仅剩两个 HF 公开模型照跑) — 各自对每篇文章输出一个 softmax 正面类概率 (记 `{model}_正面_{track}`)。该概率并非直接落入面板, 而是先乘以阶段24 (herd_decay) 计算出的羊群权重 (herd weight, `_hw` 尾缀), 再在同一 bank-year 单元内对全部满足留篇门控的文章求和, 得到本家族的 9 个 `{model}_正面_hw_sum_{track}` 列。羊群权重的经济含义是「压低同期媒体扎堆报道、同质化叙事对语调测度的机械放大」——当某银行在短窗口内被大量媒体几乎同时以相似措辞报道 (羊群效应/媒体跟风), 直接等权累加会让这类扎堆报道的情感信号被过度放大, 羊群加权臂通过降低高度同质化窗口内单篇文章的边际权重来抵消这一放大效应, 与不加权的裸 `pos_sum` 臂 (F304 或邻近家族) 构成同一构念下的两个稳健性梯级, 二者并排比较、互不替代。

【方法学与计算】
文章级概率的产生流程见 `tone_berts.py`: 三模型一次性预加载到 GPU (FP32 权重 + AMP autocast 混合精度推理), 三轨文本 (full=标题+全文正文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句±N窗) 各自 `prepend_title` 拼接后独立分词分批推理; 超长文本用 50% 重叠的滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5`, 单窗 ≤512 token 含特殊符, 有效正文 ≤510 token), 各窗 logits 按置信度加权池化 (`logits *= Σ(conf_k·logits_k)/Σconf_k`) 合成篇级 logits 再 softmax 得正面类概率。批级异常先逐篇重试一次, 仍失败才写失败哨兵 (概率置 NaN, 与空文本的 num_windows=0 严格区分), 因此 `pos_sum` 求和天然跳过失败篇不引入偏误分子。面板聚合层的 `_BERT_MODEL_RE` 正则以模型名锚定行首 (`^model_`) 匹配 `pos_sum` 等 metric 加可选加权尾缀 `(vw|mw|hw)` 再加可选轨道尾缀, hw 对应 `_PER_MODEL_WEIGHT_ZH['_hw'] = ' [羊群加权]'`; 与 `pos`(均值)、`pos_std`(离散) 等同族 metric 相比, `pos_sum` 是未做篇数归一化的总量测度, 量纲随 bank-year 内文章篇数与羊群权重规模同步变化, 不宜跨银行/跨年份直接比较水平值 (适合作回归中的暴露强度控制, 或先做篇数/市值归一化再比较)。

【文献定位】
本家族方法学谱系直接承接 BERT 的通用预训练-微调范式 (Devlin et al., 2019) 与其金融领域适配: FinBERT2 (Xu et al., 2025) 是本项目采用的三模型之一, 面向中文金融场景弥合通用大模型与金融专用部署之间的差距; Huang, Wang & Yang (2023) 在 *Contemporary Accounting Research* 上验证了 FinBERT 类模型在提取财务文本信息上相对词典法与人工标注的增量价值, 是本项目「LLM 三家投票/词典法/BERT 三模型」三条独立测度路线互相印证设计的方法学依据之一。羊群加权臂的构念动机可与文本信号需按暴露/密度校正后才能跨期跨主体比较这一更广泛的方法学传统作启发式类比: Hassan et al. (2023, *Review of Financial Studies*) 基于财报电话会议文本关键词占比、按通话长度归一化构造了企业层面流行病暴露测度——该文的具体研究对象 (电话会议文本 × 疫情暴露) 与本文的具体研究对象 (新闻报道 × 情感强度羊群效应) 并非同一构念, 二者严格意义上不可直接对应, 此处仅取其"原始文本计数信号若不做归一化/校正, 会被样本自身的非均匀密度机械放大, 需引入校正项才能获得可比测度"这一方法学共性作为类比参照, 本家族的 hw 加权臂是在情感强度累加这一环节针对媒体扎堆报道引入的对应校正, 与 Hassan et al. (2023) 的通话长度归一化并非同一操作, 仅思路上可类比。⚠ 三轨 (full/ctx/ss) 与三模型 (finbert_cn/fin_sent_zh/finbert2) 均各自 just-identified 并排、互为稳健性、不分主次, 证明结论不被单一文本范围或单一厂商模型驱动, 禁混进同一 over-identified Hansen J 设定; 三模型属 per-model 独立降级 (finbert2 缺席仅掉自身族, 不连坐 finbert_cn/fin_sent_zh), 与 co-primary 嵌入的 both-or-neither 语义不同。凡涉及 n_articles 分母/留篇门控, 均遵循 2026-06-29 起生效的 full-only 口径: 阶段21 是否判定某篇为"一篇银行金科报道"只看 `llm_verified_full == True`, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集; ss 轨若上游未发现银行∧金科同句共现, 回退语义镜像 ctx——`content_ss` 退化为全文 body、`ss_is_fallback` 置 True 且与 ctx 共享同一 `n_articles` 分母口径, 而非另起独立分母。 就本家族赖以成立的两个环节——以篇级概率而非硬标签作为加权基数、以及按强度加权而非等权计数加总——近期文献可提供有限旁证。Chen 与 Mankad (2025) 提出结构化主题-情感话语模型, 以文档级的连续情感-话语潜变量承载文本信息并允许其被文档级协变量解释, 使情感量可进入正式统计推断, 说明以篇级连续量而非 argmax 硬标签作为测度基数在前沿是被接受的做法; 惟其连续量为贝叶斯生成模型的后验潜变量, 与 BERT softmax 概率的校准含义不同, 原文无中性档、无篇级量在实体-期内的聚合步骤, 更无羊群权重一类的加权口径, 故只作基数口径的弱锚。Groß-Klußmann (2024) 以监督式自编码器对已聚合的新闻情感时间序列抽取潜在经济因子, 并在 GDP nowcasting、资产类别收益面板解释与时序动量三项应用上优于 PCA/PLS 等线性降维, 同样佐证连续取值的情感信号进入金融实证的常规性; 但原文作用于已聚合的时间序列而非产出篇级情感, 其表征是压缩潜因子而非三分类 softmax 概率, 层级为英文新闻的宏观时序, 无三轨切分、无 hw 加权, 与本家族的加权求和并非同一操作。Hirshleifer、Mai 与 Pukthuanthong (2025) 以半监督主题模型对跨 160 年、约 700 万篇《纽约时报》报道逐篇抽取战争话语强度, 并把篇级强度按强度 (而非等权计数) 加总为可用于资产定价检验的文本暴露量, 为本家族"篇级信号先乘权重再在 bank-year 内求和"这一加权聚合形态提供了顶刊层级的先例。须严格界定: 原文测度的是战争话语主题暴露 (topic exposure), 不含情感极性与分类概率输出, 因而不为本家族概率和的概率语义提供任何依据, 此处仅锚加权聚合这一形态本身; 其权重来自话语强度而非媒体扎堆报道的羊群程度, 聚合层级为市场/组合而非银行-年, 语料为美国英文新闻, 亦无 per-model 并排与三轨文本范围切分。
## VAR: fin_sent_zh_正面_hw_sum_ctx

【变体差分】
本列在家族三模型×三轨 3×3 网格中取模型=fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的中文金融 3 分类 BERT)、轨道=ctx (标题+银行实体窗口文本)。fin_sent_zh 与 finbert_cn 同为 HuggingFace 公开权重、3 分类体系 (中性/正面/负面), 但预训练语料与微调数据集不同 (fin_sent_zh 源自英文 Financial PhraseBank 迁移微调, finbert_cn 是原生中文金融语料微调), 二者对同一篇报道给出的正面概率并非恒等, 差异本身即是"跨厂商/跨微调路径稳健性"的信息来源, 不应被视为噪声而合并。ctx 轨的文本范围是标题加银行实体所在窗口 (而非全文), 相比 full 轨剔除了与目标银行无关的段落, 使得 BERT 推理更聚焦于银行相关语境, 代价是当窗口过窄时可能丢失篇章级的转折/让步语气, 因此 ctx 轨与 full 轨互为稳健性并排, 不设孰主孰次。羊群加权 (hw) 臂在此列上的含义与家族 CORE 一致: 对同一 bank-year 内、被大量媒体同质化跟风报道的窗口, 单篇边际权重被压低后再求和, 抵消扎堆报道对 ctx 轨正面概率总量的机械放大。ctx 轨若该篇文章未通过 full-only 留篇门控 (`llm_verified_full != True`), 则不进入本列的求和行宇宙; ctx 轨自身若无独立回退标记 (回退标记 `*_is_fallback` 是 ctx/ss 物化阶段14 的产物, 与阶段23 BERT 推理是否成功的失败哨兵是两套独立机制, 二者不可混淆), BERT 推理失败篇 (概率 NaN) 天然被求和跳过不计入分子。本列与 fin_sent_zh 同模型的 full/ss 轨、以及 finbert_cn/finbert2 同轨异模型的 6 个邻近列共同构成家族的完整稳健性梯子, 任一单列的高低都不能单独作为主结论证据, 须结合梯子整体一致性判断。

## VAR: fin_sent_zh_正面_hw_sum_full

【变体差分】
本列取模型=fin_sent_zh、轨道=full (标题+全篇正文, `prepend_title` 拼接后整体喂入模型, 超长文本走滑动窗口切片+置信度加权池化)。full 轨是三轨中信息量最完整的一支, 覆盖全文语境, 是家族内 canonical headline 意义上的默认参照轨 (2026-06-29 起 full-only 门控也以 full 轨的留篇判定为唯一分母口径的锚点), 但 full 轨同时也最容易混入与目标银行/金科主题无直接相关的段落语气, 这正是 ctx/ss 轨存在的动机——三者并非替代关系而是互补的稳健性并排。fin_sent_zh 模型本身对长文本的滑动窗口切分次数 (`bert_num_windows_full`) 通常高于 ctx/ss 轨 (因文本更长), 窗口数越多、置信度加权池化对最终概率的平滑作用越强, full 轨的 `正面` 概率相对 ctx/ss 轨往往波动更小但对局部强烈情感段落更不敏感, 这一特性差异是三轨互为稳健性设计的具体体现之一, 不宜简单认为 full 轨"更准"。hw 加权求和的语义与家族其余 8 列一致: 羊群权重来自阶段24 herd_decay 的输出, 按 bank-year 单元对齐后逐篇相乘再求和, 校正媒体扎堆报道对累计情感强度的放大。本列作为 full 轨代表, 常被用作与词典法 (阶段22)、LLM 三家投票法 (阶段21) 的 full 轨测度做跨方法交叉验证的锚点之一, 三条方法学路线 (大模型/词典/BERT) 各自独立、互相印证, 但仍需强调本列本身与另外两个模型的 full 轨、以及本模型的 ctx/ss 轨共同构成 just-identified 并排梯子, 不可单独作为唯一证据来源。

## VAR: fin_sent_zh_正面_hw_sum_ss

【变体差分】
本列取模型=fin_sent_zh、轨道=ss (标题+银行∧金科同句共现窗口, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句)。ss 轨的判定原语是逐句扫描银行实体与金科词是否在同一句 (或半径窗口内) 共现, 与阶段13 硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` 判据接近但服务对象不同——阶段13 是决定文章是否留在样本里的硬过滤, ss 轨物化 (阶段14) 是在留下的文章内部截取一段更紧凑的文本喂给下游测度模型, 二者不可互相替代复用。若某篇文章通过了硬过滤但在句子层面找不到银行∧金科同句共现 (可能因为共现发生在不同句、或阶段13 用的是段落级/更宽半径的判据), ss 轨回退语义严格镜像 ctx 轨: `content_ss` 退化为全文 body, `ss_is_fallback` 置 True, 且与 ctx 共享同一 `n_articles` 分母口径而非另立分母。本列在 ss 轨且 fin_sent_zh 模型上求出的加权正面概率和, 相对 ctx/full 轨通常样本内文本更短、模型对句子级局部语气更敏感, 若该 bank-year 内多数文章触发 ss 回退 (即找不到同句共现), 本列在数值上会趋近于对应的 ctx 轨列而非独立信号, 使用时应结合 `ss_is_fallback` 占比一并解读, 避免把"回退到全文"误读为"同句语境本身正面"。hw 加权求和逻辑与家族其余列一致, 不再赘述; 本列与同模型 ctx/full 轨、以及 finbert_cn/finbert2 的 ss 轨共同构成互为稳健性的并排梯子。

## VAR: finbert2_正面_hw_sum_ctx

【变体差分】
本列取模型=finbert2 (项目自持私有微调 BERT, 2 分类体系 负面/正面, 不含独立中性类别; 模型路径经 .env `FINBERT2_MODEL_DIR` 解析, 未配置或路径不存在时该模型在阶段23 被优雅跳过, 本列及同模型其余 8 列全部置为 NaN, 但不影响 finbert_cn/fin_sent_zh 两个 HuggingFace 公开模型照常产出对应列)、轨道=ctx。finbert2 与另两个模型最大的结构性差异是 2 分类而非 3 分类——由于没有独立中性类别, finbert2 的正面概率在数学上等于 1 减负面概率, 不存在"中性吸收"效应, 因此 finbert2 的正面概率分布与 finbert_cn/fin_sent_zh 的 3 分类正面概率分布在统计特性上不完全可比 (3 分类模型的正面概率会被中性判定分走一部分质量), 这也是三模型必须 co-equal 并排、不设 ensemble headline 的原因之一——直接跨模型比较概率水平值会引入结构性偏差, 更稳妥的做法是分别标准化后再比较跨模型一致性 (呼应家族 CORE 提及的 Table A5 类跨模型 z-score 标准化惯例)。ctx 轨含义与家族其余 ctx 列一致 (标题+银行实体窗口), finbert2 若因 .env 未配置而缺席, 本列直接为空, 属于 per-model 独立降级而非 both-or-neither 连坐, 不影响同 bank-year 单元内 finbert_cn/fin_sent_zh 两列的正常产出与下游面板回归的可用性。hw 加权求和语义同家族 CORE。

## VAR: finbert2_正面_hw_sum_full

【变体差分】
本列取模型=finbert2、轨道=full。作为项目私有微调模型, finbert2 相比两个 HuggingFace 公开模型的优势在于其微调语料更贴近本项目的银行/金科新闻领域分布 (领域内微调通常带来更好的领域内区分度), 但代价是可复现性依赖于 `FINBERT2_MODEL_DIR` 指向的本地权重文件是否可得——若审计方或后续研究者没有该私有权重, 本列及 finbert2 全部 9 列中的对应 3 列将无法重现, 这也是家族强调三模型互为稳健性、finbert_cn/fin_sent_zh 两个公开模型可独立支撑结论的现实考量之一。full 轨在 finbert2 上的滑动窗口切分逻辑与另两模型完全同构 (共享 `WINDOW_STRIDE_RATIO=0.5`、置信度加权池化), 唯一差异是 2 分类输出结构 (`finbert2_中性` 恒为 NaN, 由 `_build_model_configs` 对 2-class 模型补齐占位以保持三模型输出列结构一致, 但该 NaN 中性列不影响正面概率本身的计算)。hw 加权求和语义与家族 CORE 一致: 羊群权重按 bank-year 对齐后逐篇相乘再求和, 压低同质化扎堆报道窗口对累计正面强度的机械放大。本列与同模型 ctx/ss 轨、以及 finbert_cn/fin_sent_zh 的 full 轨共同构成并排稳健性梯子, 且是 full-only 留篇门控直接适用的一支 (行宇宙 = full 留篇集本身, 非其子集)。审阅本列数值时应留意, 由于 2 分类结构没有中性吸收, finbert2 全篇文本上给出的正面概率天然比 3 分类模型更趋极端 (更接近 0 或 1), 这会使得同样的羊群权重乘积在累加后呈现出比 finbert_cn/fin_sent_zh 更大的方差, 属模型结构差异导致的预期现象, 不应被误读为测度不稳定。

## VAR: finbert2_正面_hw_sum_ss

【变体差分】
本列取模型=finbert2、轨道=ss。作为 finbert2 三轨中范围最窄的一支, 其文本输入是标题+银行∧金科同句共现窗口 (半径±1句默认), 若该 bank-year 内多数文章缺乏同句共现而触发回退, `content_ss` 退化为全文 body、`ss_is_fallback` 置 True, 分母与 ctx 轨共享 (镜像语义, 见家族 CORE)。finbert2 若因 `.env` 未配置本地权重路径而在阶段23 被优雅跳过, 本列同样直接置空, 与本模型的 ctx/full 两列同步降级, 但不牵连 finbert_cn/fin_sent_zh 两个模型的 ss 轨——这是家族反复强调的 per-model 独立降级语义在 ss 轨这一具体切面上的体现。由于 finbert2 是 2 分类模型, 在句子级短文本 (ss 轨天然比 ctx/full 轨更短) 上的推理稳定性 (滑动窗口触发频率) 相对 3 分类模型可能不同——文本越短触发滑窗切片的概率越低, 单窗直接出概率的比例越高, 因此 ss 轨与 ctx/full 轨在窗口数分布上通常有系统性差异, 这一差异是判读 ss 轨数值时应纳入考量的背景, 而非本列测度本身的缺陷。ss 轨若触发回退 (`ss_is_fallback=True`), `content_ss` 退化为全文 body, 此时本列的加权正面概率和会在数值上趋近于 finbert2 的 full 轨列而非独立信号, 使用者应结合该 bank-year 单元的回退占比一并解读, 而非孤立比较 ss 轨与 full 轨的差值大小。hw 加权求和语义与家族其余列一致, 不再赘述。

## VAR: finbert_cn_正面_hw_sum_ctx

【变体差分】
本列取模型=finbert_cn (yiyanghkust/finbert-tone-chinese, HuggingFace 公开权重, 原生中文金融语料预训练/微调的 3 分类 BERT, 中性/正面/负面)、轨道=ctx。finbert_cn 是三模型中语料血统最贴近中文金融文本的一支 (相对 fin_sent_zh 的英文迁移微调路径而言), 在中文金融语境下的类别边界判定通常被认为更贴合本地新闻用语习惯, 但这并不意味着 finbert_cn 应被赋予"主模型"地位——家族 CORE 已明确三模型 co-equal 互为稳健性、不设 ensemble headline, finbert_cn 与 fin_sent_zh/finbert2 在具体篇章上给出不同判定恰恰是三角验证价值所在。ctx 轨含义同家族其余 ctx 列。finbert_cn 与 fin_sent_zh 同属 3 分类体系、且均为 HuggingFace 公开模型 (`strict_models=true` 默认下这两个模型非预期加载失败会 fail-loud raise, 与 finbert2 的"未配置优雅跳过"是两种不同的失败语义: 前者是"应该能加载却失败了"的硬错误, 后者是"预期可能不存在"的正常降级路径), 二者在阶段23 的可用性保障级别不同, 但这一差异属于运维/工程层面, 不改变面板层面三模型 co-equal 并排的构念地位。ctx 轨截取的银行实体窗口相比全文剔除了大量与目标银行无直接关联的段落 (例如同篇报道中涉及其他银行或宏观政策背景的段落), 这对 finbert_cn 这类原生中文语料模型而言意味着输入序列更短、模型注意力更集中在目标实体附近, 通常带来更低的滑窗触发次数与更稳定的单窗直出概率, 但也可能因窗口过窄丢失篇章级转折语气 (例如"虽然……但银行本身……"结构横跨窗口边界), 这一权衡与 fin_sent_zh_ctx、finbert2_ctx 两列共享, 是 ctx 轨作为整体稳健性支路的通用特征而非本列独有。hw 加权求和语义与家族 CORE 一致。

## VAR: finbert_cn_正面_hw_sum_full

【变体差分】
本列取模型=finbert_cn、轨道=full, 是三模型×三轨网格中最贴近"传统全文中文金融 BERT 情感测度"直觉的一列: 原生中文金融预训练模型 + 全篇文本输入。作为 3 分类模型, finbert_cn 的正面概率会与负面、中性概率共同归一至 1, 相比 finbert2 (2 分类) 多出的中性类别意味着同一篇语气模糊/事实陈述型报道更容易被 finbert_cn 判为中性从而拉低正面概率, 这是 3 分类与 2 分类模型结构性差异在 full 轨上的直接体现, 也是家族强调"model-specific 阈值/类别语义禁跨模型直接比水平, 只比标准化后趋势"这一原则的具体理由之一。full 轨滑窗切分/置信度加权池化逻辑同家族 CORE。hw 加权求和语义同家族 CORE: 逐篇乘以阶段24 输出的羊群权重后对 bank-year 求和, 压低同质化扎堆报道对累计正面强度的机械放大, 与不加权的裸 `pos_sum` 臂 (若存在于邻近家族) 构成同一构念下的两个并排稳健性梯级。本列因 full 轨的 canonical 地位, 在三模型×三轨 9 列中常被作为 finbert_cn 一支的默认参照点, 但仍需与 ctx/ss 轨、以及另两个模型的 full 轨联合解读, 不单独作为结论证据。因 full 轨覆盖全文, 其滑窗触发次数 (`bert_num_windows_full`) 在三轨中通常最高, 置信度加权池化对多窗口篇章的平滑效应也最强, 使得本列在同一 bank-year 单元内的篇间方差相对 ctx/ss 轨更低, 这一平滑特性是解读本列与 ctx/ss 轨数值差异时应纳入的背景, 不代表 full 轨测度精度更优。

## VAR: finbert_cn_正面_hw_sum_ss

【变体差分】
本列取模型=finbert_cn、轨道=ss, 是家族 9 列网格中范围最窄、对局部语境最敏感的一支之一 (与 fin_sent_zh_ss、finbert2_ss 并列)。ss 轨文本 = 标题 + 银行∧金科同句 (或±N句窗口) 共现片段, 判定原语与阶段13 硬过滤共现判据是两套独立机制 (前者服务文本物化, 后者服务文章留样, 不可互相复用), 若该篇文章找不到同句共现则回退为全文 body 并置 `ss_is_fallback=True`、与 ctx 轨共享分母口径 (镜像语义)。finbert_cn 作为 3 分类模型在短文本 (ss 轨天然更短) 上的中性判定倾向可能比 full 轨更明显——短句语境往往缺乏足够上下文支撑模型给出高置信度的正/负面判断, 容易被判为中性从而拉低正面概率总量, 这一特性使得 ss 轨在 finbert_cn 上的数值解读需要结合该 bank-year 单元的 `ss_is_fallback` 占比与滑窗触发次数 (`bert_num_windows_ss`) 一并考量, 避免把"模型倾向中性判定"误读为"同句语境情感偏弱"。hw 加权求和语义与家族其余 8 列完全一致。本列与同模型 ctx/full 轨、以及 fin_sent_zh/finbert2 的 ss 轨共同构成家族最末端的稳健性梯子节点, 三轨/三模型两个维度均各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J 设定。作为 3 分类模型在最窄文本范围上的取值, 本列相对 finbert2_ss (2 分类) 更容易出现"高中性、低正面"的组合, 解读跨模型一致性时应优先比较标准化后的方向而非概率水平本身。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT) No. 4171-4186 [Working Paper]. https://doi.org/10.18653/v1/N19-1423
Chen, L., & Mankad, S. (2025). A Structural Topic and Sentiment-Discourse Model for Text Analysis. Management Science, 71(7), 5767-5787. https://doi.org/10.1287/mnsc.2022.00261
Groß-Klußmann, A. (2024). Learning deep news sentiment representations for macro-finance. Digital Finance, 6(3), 341-377. https://doi.org/10.1007/s42521-024-00107-2
Hirshleifer, D., Mai, D., & Pukthuanthong, K. (2025). War Discourse and the Cross Section of Expected Stock Returns. The Journal of Finance, 80(6), 3589-3637. https://doi.org/10.1111/jofi.13482
<!-- rendered-citations:end -->
