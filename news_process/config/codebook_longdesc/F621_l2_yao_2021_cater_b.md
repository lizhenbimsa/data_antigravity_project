---
family_id: F621
columns:
- yao_2021_cater_b_ctx
- yao_2021_cater_b_full
- yao_2021_cater_b_ss
unit: 无量纲差分得分 (词典语调分 减 BERT净情感分, 取值范围近似 [-2, 2])
formula: 'yao_2021_cater_b{track} = yao_2021_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track}); track ∈ {_full, _ctx, _ss}; bert_avg_pos/neg{track} = 三个 BERT 模型 (finbert_cn/fin_sent_zh/finbert2) 在该轨上 argmax 判正/判负占比的算术平均'
producer: pipeline\panel\runner.py (8d algo_cater 区块, L2457-L2497) ; 标签见 pipeline\panel\export.py (HEURISTIC_LABELS `{d}_cater_b{s}` 生成式, L1322-L1324) ; pipeline\panel\stata_export.py (.dta 变量标签落盘)
upstream:
- 22_words_tone.parquet (yao_2021_tone{track} 来自 stage 22 词典打分链路的中间产物, 经面板聚合为 yao_2021_tone{track})
- 23_tone_berts.parquet (bert_avg_pos{track}/bert_avg_neg{track} 来自 stage 23 三 BERT 模型 argmax 判类后的跨模型均值)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: 'Sentiment analysis of economic text: A lexicon-based approach'
  venue: Economic Inquiry
  vol: '63'
  issue: '1'
  pages_or_artno: 125-143
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
new_dois: []
---

## CORE

【构念与来源】
本家族测度"算法迎合" (algorithmic catering) 构念: 词典法与深度学习模型法对同一篇报道给出的情感判读之间的系统性缺口。具体到本家族, 比较对象是姚加权等 (2021) 构建的中文金融情绪词典 (`yao_2021`, 融合年报语料与社交媒体语料两个子语料库、去重后正面词 3,844 个 / 负面词 2,074 个) 与三个中文金融 BERT 模型 (`finbert_cn`/`fin_sent_zh`/`finbert2`) 跨模型均值的判类结果。该构念的方法学动机来自两条既有文献: 一是词典法本质是"词袋+人工赋极性"的静态规则, 对语境、否定、反讽等结构不敏感; 二是深度模型 (含 BERT 类预训练语言模型) 能捕捉上下文依赖的语义, 但训练语料与微调目标可能引入与词典正交的系统性偏差。Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习与词典两类情感度量在披露文本上的分歧模式, 发现二者并非同一构念的噪声版本, 而是各自捕捉了文本情感的不同侧面, 这正是本家族"词典减 BERT"设计差分而非直接互相替代的方法学依据。van Atteveldt, van der Velden & Boukes (2021) 进一步在跨方法效度比较中指出, 词典法、人工标注、众包与机器学习四类情感测度彼此的一致性受文本类型、领域专业词汇密度调节, 中文金融新闻报道这一领域文本正是词典与深度模型分歧可能被放大的场景, 为本家族的"迎合缺口"构念提供了外部效度佐证。命名沿用项目内 `algo_cater`/`{dict}_cater`/`{dict}_cater_b` 系列的一致语义: 后缀 `_b` 标记比较对象为 BERT (而非无后缀的 `_cater` 比较对象为 LLM 三家投票), 前缀 `yao_2021` 标记词典侧取自姚加权词典而非综合词典均值 `dict_avg_tone`。

【方法学与计算】
公式为 `yao_2021_cater_b{track} = yao_2021_tone{track} - (bert_avg_pos{track} - bert_avg_neg{track})`。被减数 `yao_2021_tone{track}` 是姚加权词典在给定轨道上对文章打出的语调分, 计算口径遵循项目词典打分族的通用规则 (正负词计数经否定翻转/程度副词/转折规则调整后归一化, 详见 tone_words 模块), 是一个已在词典自身尺度上完成归一化的语调分。减数 `bert_avg_pos{track} - bert_avg_neg{track}` 是三个 BERT 模型在该轨道上 argmax 判正/判负占比先各自求出, 再跨模型取算术平均后相减得到的"BERT 净情感分", 数学形式与项目内 `{bert}_net_tone{track}` (mean(pos) - mean(neg)) 同构, 但此处是先跨模型平均概率再作差, 而非先逐模型作差再跨模型平均 (两种顺序在线性期望下代数等价, 因均值算子与减法可交换)。差分为正值表示词典判读比 BERT 综合判读更正面 (词典侧"迎合"倾向); 差分为负值表示词典判读比 BERT 综合判读更负面。三个 track 后缀 (`_full`/`_ctx`/`_ss`) 对应项目统一的三轨文本架构: `_full` 使用标题+正文全文, `_ctx` 使用标题+银行与金科实体窗口截取文本, `_ss` 使用标题+银行与金科词同句 (±N 句窗口, 默认 N=1) 截取文本; 若某篇报道无银行∧金科同句共现, `_ss` 轨回退为全文 body 且 `ss_is_fallback` 置真 (镜像 `_ctx` 轨在无实体窗口时的回退语义, 二者共享 `n_articles` 分母口径)。三轨测度各自独立 just-identified, 互为稳健性、不分主次, 铁律上禁止把三轨结果混入同一 over-identified 的 Hansen J 过度识别检验。留篇门控口径遵循 2026-06-29 起生效的 full-only 规则: 一篇报道是否计入"银行金科报道"样本只看 `llm_verified_full` 判定, ctx/ss 轨的迎合度测度是在 full 轨留篇集合的子集上按各自轨道文本重新计算, 而非独立留篇。生产环境中 BERT 三模型任一缺席 (如 `FINBERT2_MODEL_DIR` 未设导致 finbert2 缺失) 按 per-model 独立降级处理, `bert_avg_pos`/`bert_avg_neg` 仅在缺席模型不参与时基于剩余可用模型计算均值, 与嵌入族 both-or-neither 的整族降级语义不同。

【文献定位】
"算法迎合"这一比较设计的直接方法学先例是 Du, Huang, Wermers & Wu (2022, Review of Finance) 关于中文金融文本领域专属情感词典构建的研究, 该文强调通用情感词典 (含直译自英文的 L&M 词典) 在中文金融语境下存在系统性误判, 是本项目并行维护多部中文金融情感词典 (含 `yao_2021`) 并逐一与深度模型交叉比较的直接动机来源。Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 对基于词典的经济文本情感分析方法做了系统评述, 明确指出词典法的规则透明性与深度模型的语境敏感性之间存在权衡, 支持本家族把二者差分作为一个独立可解释的测度维度、而非简单选边站队。van Atteveldt et al. (2021, Communication Methods and Measures) 的跨方法效度比较研究为"词典与机器学习方法测的不是同一件事"这一前提提供了实证支撑, 呼应本家族刻意保留差分符号方向 (而非取绝对值) 以保留"谁更正面"的方向性信息。Frankel, Jennings & Lee (2022, Management Science) 是本家族命名与解读框架的直接文献锚点: 该文比较机器学习与词典两类披露情感度量, 发现二者的分歧本身携带增量信息, 而非纯噪声, 支持本项目把 `*_cater`/`*_cater_b` 系列作为面板测度族正式保留、而非仅作诊断中间量丢弃。本家族三列在项目测度体系中定位为"词典-深度模型分歧诊断"辅助测度, 与主线情感测度 (`llm_vote_tone{track}`、`dict_avg_tone{track}`、三 BERT per-model 净情感分) 平行存在, 不作为任一 paper 的 canonical treatment/outcome, 供研究者在稳健性检验或测量误差讨论中选用。

## VAR: yao_2021_cater_b_ctx

【变体差分】
本列是 `_ctx` 轨的迎合缺口: `yao_2021_tone_ctx` 与三 BERT 跨模型均值净情感分 `(bert_avg_pos_ctx - bert_avg_neg_ctx)` 之差。`_ctx` 轨的文本口径为"标题+银行与金科实体窗口"截取文本 (stage 14 `ctx_materializer` 物化 `content_ctx`, `prepend_title` 拼接标题), 与 `_full` 轨的差别仅在于输入文本范围更聚焦于目标实体周边语境, 不改变减数/被减数的计算逻辑本身: 分母侧词典打分与 BERT 判类均在同一段较短的 `content_ctx` 文本上独立重新执行, 而非从 `_full` 轨结果截取或加权。这一设计的方法学意义在于剥离与目标银行/金科主题无关段落对情感判读的稀释效应——当一篇报道篇幅较长而涉及目标实体的段落只占一小部分时, `_full` 轨的词典分与 BERT 分都可能被无关段落的语调拉偏, `_ctx` 轨通过聚焦实体窗口缓解该问题, 使得词典与 BERT 之间的迎合缺口更贴近"针对目标实体报道本身"的分歧, 而非全文整体分歧。行样本集合是 full 轨留篇集合 (`llm_verified_full == True`) 的子集, 按 `_ctx` 轨文本重新计算词典分与 BERT 判类分, 而非独立留篇判定 (full-only 门控铁律, 2026-06-29 起生效): 即一篇文章是否进入"银行金科报道"分析样本, 仍完全由 full 轨的 LLM 校验结果决定, `_ctx` 轨不参与留篇判定, 只在留篇之后按自身文本口径重算测度值。若某篇文章无法定位到有效实体窗口 (例如实体识别未能在给定窗口半径内锚定目标银行或金科词), 依据项目 ctx 轨回退语义按 `ctx_is_fallback` 标记降级处理, 此时该行的 `_ctx` 轨测度退化为使用与 `_full` 轨相同的全文文本计算, 但仍保留独立列位与独立标记, 不与 `_full` 轨的数值直接等同看待。本列与同家族 `_full`/`_ss` 两列各自 just-identified 并排, 互为稳健性、不分主次, 三轨结果禁止混入同一 over-identified Hansen J 过度识别检验。

## VAR: yao_2021_cater_b_full

【变体差分】
本列是家族的 canonical 轨: `_full` 轨使用"标题+正文全文"作为输入文本, 计算 `yao_2021_tone_full` 与三 BERT 跨模型均值净情感分 `(bert_avg_pos_full - bert_avg_neg_full)` 之差。full 轨同时是本项目留篇门控的唯一判据来源: 一篇报道是否计入"银行金科报道"分析样本仅由 `llm_verified_full` 决定, 因此本列覆盖的行样本即为该门控下的完整留篇集合, 不存在对下游 ctx/ss 子集的依赖, 也不需要像 `_ctx`/`_ss` 两轨那样处理"是否为回退行"的额外标记。作为三轨中信息量最完整的一轨 (未经实体窗口或同句范围截断), `_full` 轨捕捉的是文章整体语调与整体 BERT 判类之间的缺口, 更容易受到与目标银行/金科主题无关段落的稀释影响——例如一篇报道虽涉及目标银行, 但大部分篇幅讨论宏观经济或其他机构, 此时词典与 BERT 各自在全文尺度上的判读都可能偏离对目标实体本身的态度, 这正是项目同时维护 `_ctx`/`_ss` 两条更聚焦轨道作为稳健性检验的动机之一。尽管如此, `_full` 轨仍具备不可替代的方法学价值: 它是唯一未经任何窗口截断的完整文本测度, 不受实体识别失败导致的回退语义影响, 且是 P1 主线情感 treatment `llm_vote_tone_full` 与 provisional `bank_news_clarity` 等主轨共用的文本口径, 便于与项目其他 full 轨测度直接对齐比较。三轨各自 just-identified 并排、互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 过度识别检验; `_full` 轨在此并列关系中不构成"更优先"的判断基准, 仅因其同时承担留篇门控职能而在样本覆盖上更完整。

## VAR: yao_2021_cater_b_ss

【变体差分】
本列是 `_ss` 轨的迎合缺口: `yao_2021_tone_ss` 与三 BERT 跨模型均值净情感分 `(bert_avg_pos_ss - bert_avg_neg_ss)` 之差。`_ss` 轨的文本口径为"标题+银行与金科词同句 (±N 句窗口, `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 N=1) "截取文本, 是三轨中范围最窄、语境最紧凑的一轨, 判定口径为不对称口径 (银行侧经否定词与短名过滤剔除误匹配, 金科侧为裸 AC 自动机对 1506 个金科词表的无条件匹配, 不做否定过滤)。这种极窄窗口设计的目的是把词典分与 BERT 分的计算范围收缩到"银行与金科概念真正同句出现"的最紧凑语境, 使得测度出的迎合缺口最大程度排除文章其余部分 (可能讨论其他主题或其他机构) 对情感判读的干扰, 是三轨中对"目标实体本身态度"信号最纯净、但样本覆盖 (受同句共现是否存在) 最受限的一条稳健性轨道。回退语义镜像 `_ctx` 轨: 若某篇报道不存在银行∧金科同句共现 (即全文中找不到满足半径条件的句子), `content_ss` 回退为全文 body、`ss_is_fallback` 置真, 与 `_ctx` 轨的回退共享 `n_articles` 分母口径, 二者均属"优雅降级"而非硬性丢弃, 保证 `_ss` 轨测度在无同句共现时仍有定义而非产生缺失值。行样本集合同样是 full 轨留篇集合的子集 (full-only 门控铁律, 2026-06-29 起生效), `_ss` 轨的词典分与 BERT 判类分均按 `_ss` 轨文本独立重算, 不借用 `_full`/`_ctx` 两轨的中间结果。本列与同家族 `_full`/`_ctx` 两列各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 过度识别检验。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
<!-- rendered-citations:end -->
