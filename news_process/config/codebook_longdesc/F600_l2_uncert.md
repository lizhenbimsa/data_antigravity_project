---
family_id: F600
columns:
  - uncert_frac_ctx
  - uncert_frac_full
  - uncert_frac_ss
unit: 比率/占比 (proportion, [0,1]; 词频数计, 未百分比化)
formula: "uncert_frac_{trk} = count(uncertainty_words in content_{trk}) / total_word_count(content_{trk}), trk ∈ {full, ctx, ss}"
producer: news_process/pipeline/sentiment/lm_non_sentiment.py::_compute_lm_non_sentiment_for_text (词典命中计数) ; news_process/pipeline/sentiment/tone_words.py::_dual_analyze (三轨调度与集成)
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - 22_tone_words.parquet
citations:
- doi: 10.1080/01621459.2025.2526700
  type: journal
  authors: Rambachan, A., & Roth, J.
  year: 2025
  title: "Design-based uncertainty for quasi-experiments"
  venue: Journal of the American Statistical Association
  vol: 121
  issue: 553
  pages_or_artno: 477-491
- doi: 10.1111/fire.12430
  type: journal
  authors: Black, J. R., Irtisam, R., & Jain, P. K.
  year: 2025
  title: "Textual uncertainty in financial disclosures and information asymmetry among investors"
  venue: Financial Review
  vol: 60
  issue: 3
  pages_or_artno: 799-829
- doi: 10.1111/jofi.13293
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2024
  title: "The global impact of Brexit uncertainty"
  venue: The Journal of Finance
  vol: 79
  issue: 1
  pages_or_artno: 413-458
- doi: 10.1257/aer.20131193
  type: journal
  authors: Jurado, K., Ludvigson, S. C., & Ng, S.
  year: 2015
  title: "Measuring uncertainty"
  venue: American Economic Review
  vol: 105
  issue: 3
  pages_or_artno: 1177-1216
- doi: 10.3982/ECTA6248
  type: journal
  authors: Bloom, N.
  year: 2009
  title: "The impact of uncertainty shocks"
  venue: Econometrica
  vol: 77
  issue: 3
  pages_or_artno: 623-685
new_dois: []
---

## CORE

【构念与来源】

uncert_frac 家族衡量一篇银行/金融科技相关新闻报道在文本层面表达"不确定性"语气的词频强度, 是 Loughran & McDonald (2011) 面向 10-K 文本设计的六本非情感 (non-sentiment) 子词典之一在本项目里的中文实现。six 子词典分别捕捉 uncertainty(不确定性)、litigious(诉讼/监管风险)、constraining(约束性)、modal_strong(强势模态)、modal_weak(弱势模态, v3.10.0 新增)、complexity(复杂度, v3.10.0 新增) 六种与"传统褒贬情感"正交的语用维度; uncert 是其中的"不确定性"子集, 抓取诸如"可能""或许""不确定""存在风险"等表达认知不确定或信息不完备的措辞。这套词典与 stage 21 三家 LLM 投票情感 (gpt54nano/gemini31/deepseekv4) 以及 stage 22 的褒贬向词典 (如 du_2022 六词典) 分工明确: LLM 与褒贬词典回答"这篇报道对银行是褒是贬", uncert_frac 回答"这篇报道的措辞有多"打太极"、多含糊、多留有余地", 是一种独立于情感极性的文本语用信号, 在计量上常被用作媒体/管理层沟通模糊度或信息不对称的代理变量。

数据来源上, 中文词典本体经用户 directive 于 2026-06-18 由原手工 stub v0.1.5 (314 词, AWAITING_EXPERT_AUDIT 状态) 替换为经审校的正式中文译本 (载于 tone_dicts.json, 与 L&M 系列其它子词典同一 SSOT 文件), 覆盖 Loughran & McDonald (2011, Journal of Finance) 原始英文 10-K 词表的核心语义, 并在审校过程中人工校准了部分边界词的取舍 (即高强度不确定表达与普通模糊措辞的区分), 使中文译本在语用强度分级上与原始英文词表保持一致的区分粒度。

【方法学与计算】

计算路径分两层: 底层原语 `pipeline/sentiment/lm_non_sentiment.py::_compute_lm_non_sentiment_for_text` 对给定文本做纯词频扫描——先用 `_LMFLS_NONWORD_RE` 清洗非文字符号, 再用 `_SUBSETS`/`SUBSET_PREFIX(ES)` 定义的 uncertainty 词表逐词匹配计数, 输出该子词典命中词数与文本总词数, 该函数本身"轨道无关" (track-agnostic), 不知道自己在处理 full、ctx 还是 ss 文本, 只认输入字符串。真正的三轨调度发生在上层 `pipeline/sentiment/tone_words.py::_dual_analyze` (函数名 `_dual_analyze` 为 v3.5.1 双轨时代遗留命名, 现已扩展为真三轨 full/ctx/ss 架构, 未随口径演进重命名) —— 该函数对 `content_full`、`content_ctx`、`content_ss` 三个文本列各独立调用一次 `_compute_lm_non_sentiment_for_text`, 得到三份互不干扰的词频统计, 再各自算出 `count(uncertainty_words) / total_word_count`, 落为面板列 `uncert_frac_full` / `uncert_frac_ctx` / `uncert_frac_ss`。

这一"上层三轨调度、下层轨道无关原语"的分层设计与家族其它五个 L&M 非情感子词典 (litig_frac、constr_frac、modal_strong_frac、modal_weak_frac、complexity_frac) 完全共用同一套底层与调度代码, 唯一差异是子词典选择的键名不同; 因此 uncert_frac 的方法学与本项目 A1 词典法情感测度 (du_2022 等六词典) 属姊妹血缘, 但在计算上是独立并行的两套指标, 互不影响、互不加总。词典法本身不消费 LLM API、不联网, 计算成本为 $0, 因此可以对全部三轨无条件计算, 不受 stage 21 留篇门控 (full-only, 2026-06-29 起生效) 约束——即 uncert_frac_ctx/ss 不因某篇文章未被 LLM 判定为"银行金科报道"而缺失, 三轨分母 (total_word_count) 各自独立、不共享。

三轨文本口径遵循项目统一定义: full = 标题 prepend + 全文正文; ctx = 标题 prepend + 目标银行实体所在句 ±1 句窗口 (`context_window` 配置); ss = 标题 prepend + 目标银行∧金科词同句共现的句 ±N 句窗口 (`ss_sentence_radius`, 默认 1)。当一篇文章不存在银行∧金科词同句共现时, `content_ss` 按"镜像 ctx"的回退规则退化为全文 body (与 `content_ctx` 在无目标银行句命中时的回退语义结构对称), 同时置位 `ss_is_fallback=True`, 此时该行的 `uncert_frac_ss` 实质上是在全文文本上计算, 数值上会更接近 `uncert_frac_full` 而非真正意义上的"银行金科同句"窗口测度, 下游做面板聚合或回归时应留意 `ss_is_fallback` 标志位以区分真实共现窗口与全文回退两类观测。三轨 (full/ctx/ss) 在计量设计上是互为稳健性的并排测度, 不设主次之分——各自作为独立的 just-identified 解释变量放入各自的回归设定, 严禁把三轨同时塞进同一个 over-identified 的 Hansen J 过度识别检验框架, 这是本项目在三轨/co-primary 双轨/各类消融梯子层面的统一铁律。

【文献定位】

不确定性文本测度的学术传统可追溯到宏观金融文献对"不确定性冲击"的结构化度量, 例如 Bloom (2009, Econometrica) 用行业层面股票收益波动率构造不确定性冲击并考察其对投资与雇佣的非线性动态效应, Jurado, Ludvigson & Ng (2015, American Economic Review) 则批评了简单代理变量 (如 VIX、政策不确定性指数) 混淆了"可预测的波动"与"真正不可预测的不确定性", 提出基于大规模预测误差方差分解的宏观不确定性指数; 这两篇构成了不确定性作为一个独立于情感极性的经济状态变量的理论基础, 也是本家族在计量框架上参照的"不确定性≠负面情感"这一区分立场的依据。在文本分析这一具体方法路径上, uncert_frac 直接承袭 Loughran & McDonald (2011) 建立的会计/金融文本非情感维度分类范式, 而 Black, Irtisam & Jain (2025, Financial Review) 近期的实证进一步确认了文本不确定性测度与信息不对称、投资者关注度之间的因果链条, 支持把 uncert_frac 解读为一种媒体沟通模糊度的可观测代理。Hassan, Hollander, van Lent & Tahoun (2024, The Journal of Finance) 在研究脱欧不确定性全球传导时也采用了文本挖掘构造不确定性暴露度量的思路, 佐证了此类词典法在跨主体、跨时期不确定性度量上的适用性与稳健性。方法论层面, Rambachan & Roth (2025, Journal of the American Statistical Association) 关于准实验设计下不确定性刻画的讨论提醒我们, 文本不确定性变量本身作为解释变量或控制变量进入面板回归时, 其测量误差与识别策略的交互需谨慎处理, 这也是本项目将 full/ctx/ss 三轨设计为并排稳健性检验而非单一"真值"估计的方法论出发点。

## VAR: uncert_frac_ctx

【变体差分】

本列是 uncert_frac 家族在 ctx 轨 (context, 上下文窗口轨) 上的实现, 区别于 canonical 全文轨的核心差异在于喂入 `_compute_lm_non_sentiment_for_text` 的文本对象不同: `content_ctx` 由 stage 14 `ctx_materializer` 物化, 内容为"标题 prepend + 目标银行实体所在句 ±1 句窗口" (窗口半径由 `config/filtering.yaml::context_window` 控制), 而非全文正文。这意味着 `uncert_frac_ctx` 的分子 (不确定性词命中数) 与分母 (总词数) 都只统计与目标银行直接相关的局部语境, 排除了文章中与该银行无关的段落 (例如泛泛的行业综述、其它银行的对比段落、记者背景介绍等), 因此该列刻画的是"作者在谈论这家银行时" 的措辞不确定程度, 相比全文轨对无关段落的稀释更小、信号更聚焦。

当一篇文章找不到目标银行所在句 (即无法定位实体窗口) 时, `content_ctx` 依约定回退为全文 body, 此时该行 `ctx_is_fallback=True`, `uncert_frac_ctx` 数值上退化为等同于在全文上计算的结果, 与 `uncert_frac_full` 高度接近甚至相等; 下游使用该列做回归或描述统计时应结合 `ctx_is_fallback` 标志位判断是真实局部窗口测度还是全文回退观测, 避免把两类异质来源的观测值不加区分地混同解读。

在识别与稳健性设计上, `uncert_frac_ctx` 与 `uncert_frac_full`、`uncert_frac_ss` 三者互为稳健性并排测度, 不存在何者更"主"、何者更"次"的先验排序——它们分别捕捉全文整体、银行局部语境、银行∧金科同句语境三种不同粒度下的不确定性语气, 用于检验主结论是否对文本窗口选择敏感。计量实践上应各轨独立进入各自回归设定 (即各自作为 just-identified 变量), 严禁把三轨同时纳入同一个 over-identified 的 Hansen J 过度识别检验中混用, 这是项目对三轨测度的统一铁律, 也是与 co-primary 双轨嵌入、词典消融梯度、政治词权重梯度等其它"并排稳健性族"共享的设计原则。方法学上该列的底层扫词逻辑与全文轨完全一致 (同一个 `_compute_lm_non_sentiment_for_text` 函数、同一份 tone_dicts.json 不确定性子词典), 唯一变量是输入文本窗口, 因此三轨之间的数值差异纯粹反映"文本范围"效应而非"词典口径"效应, 便于做干净的窗口敏感性分解。

## VAR: uncert_frac_full

【变体差分】

本列是 uncert_frac 家族的全文轨 (full track) 实现, 也是三轨中覆盖面最广、构造最简单的一支: `content_full` 由标题 prepend 之后拼接文章全部正文构成, 不做任何实体窗口截断或共现筛选, 因此 `uncert_frac_full` 的分子 (不确定性词命中数) 与分母 (总词数) 都基于文章完整文本计算, 是对整篇报道"整体语气模糊度"的度量, 覆盖记者在导语、背景铺垫、引用发言、结语评论等各个部分使用的全部不确定性措辞, 而不局限于与目标银行直接相关的段落。

由于统计口径是全文, 该列相比 ctx/ss 两轨更不容易受实体识别或共现窗口划定误差的影响 (无需先定位银行所在句才能计算), 数据完整度最高、缺失率最低, 常被用作三轨稳健性比较中的"基线"参照, 但这并不意味着它在计量地位上高于另外两轨——项目铁律明确三轨各自 just-identified 并排、互为稳健性、不设主次, 全文轨承担的角色是"最少假设、最少信息损失"的一种测度选择, 而非唯一真值。全文轨的一个已知特性是: 当文章篇幅较长且与目标银行相关内容占比较低时 (例如一篇综述多家银行的行业报道), 全文轨的不确定性词频比例会被无关段落"稀释", 数值上可能系统性低于聚焦银行局部语境的 ctx 轨, 这一稀释效应本身也是三轨对比设计想要捕捉和检验的稳健性维度之一, 而非需要修正的偏差。

方法学上 `uncert_frac_full` 与 `uncert_frac_ctx`、`uncert_frac_ss` 共享完全相同的底层词典扫描原语与 uncertainty 子词表, 唯一差异是输入文本范围; full 轨不涉及 `ctx_is_fallback`/`ss_is_fallback` 回退语义 (它本身就是回退的目标状态), 因此不存在该列自身的"回退"问题, 数据可用性仅受限于原始文章正文是否为空或缺失。在使用上, 若研究设计需要一个不依赖实体窗口划定质量、样本量最大化的不确定性代理变量, `uncert_frac_full` 是三轨中最稳妥的默认起点, 同时应与 ctx/ss 两轨并列汇报以体现窗口选择的稳健性检验, 三者数值方向一致则增强结论可信度, 出现系统性分歧则需在论文中如实披露并讨论窗口效应的经济学含义。

## VAR: uncert_frac_ss

【变体差分】

本列是 uncert_frac 家族在 ss 轨 (bank∧fintech same-sentence, 银行金科同句共现轨) 上的实现, 是三轨中口径最严格、聚焦度最高的一支: `content_ss` 由标题 prepend 之后拼接"目标银行与金科词同时出现在同一句"的句子及其 ±N 句窗口 (半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 构成, 只统计文章中真正把银行与金融科技话题放在一起讨论的局部语境, 排除了文章中单独谈银行、单独谈金科、或两者虽同篇出现但不在同一句语境中提及的段落。因此 `uncert_frac_ss` 刻画的是"作者在同时谈论这家银行与金融科技时" 措辞的不确定程度, 语义粒度比 ctx 轨 (仅锚定银行实体, 不要求金科词共现) 更进一步收窄到"银行×金科"交叉话题本身。

当一篇文章不存在银行∧金科词同句共现 (即无法定位符合条件的句子) 时, `content_ss` 依约定"镜像 ctx"的回退规则退化为全文 body, 该行同时置位 `ss_is_fallback=True`; 这一回退语义与 ctx 轨在无目标银行句命中时的回退结构完全对称, 保证 `n_articles` 等分母口径在两轨间共享一致的样本覆盖逻辑, 但也意味着 `ss_is_fallback=True` 的观测行, 其 `uncert_frac_ss` 数值实质上是在全文文本上计算得到, 应与 `uncert_frac_full` 做交叉核对, 避免误读为"银行金科同句语境下的真实不确定性水平"。若上游 `FINTECH_AC` (金科词识别的 Aho-Corasick 自动机) 未能正确初始化 (为 None), 则 `*_is_fallback` 全体置 True, 三轨优雅降级为等价于全文轨, 这是项目对金科词典缺失场景的统一容错设计, 而非本列独有行为。

在识别与稳健性叙事上, `uncert_frac_ss` 与 `uncert_frac_full`、`uncert_frac_ctx` 三者互为稳健性并排, 各自 just-identified, 严禁混入同一个 over-identified Hansen J 检验; 与家族其它两轨相比, ss 轨的样本有效覆盖率 (即非回退观测占比) 通常最低, 因为"银行与金科同句共现"是比"银行实体所在句"更严苛的筛选条件, 这一点在小样本 (如本机 T=2 开发环境) 上尤其容易出现大量 fallback 观测甚至零方差退化, 属预期现象; 在生产全量语料 (T=19, 覆盖 2007–2025 年) 上, 随着金融科技话题报道量随时间增长, ss 轨的真实 (非回退) 观测占比预期显著提升, 该列作为"银行×金科交叉话题下的语气模糊度"测度的解释力也随之增强。方法学上该列与另两轨共享同一套 `_compute_lm_non_sentiment_for_text` 底层扫词逻辑与 tone_dicts.json 不确定性子词典, 唯一变量仍是输入文本的窗口界定方式。

<!-- rendered-citations:begin -->
Rambachan, A., & Roth, J. (2025). Design-based uncertainty for quasi-experiments. Journal of the American Statistical Association, 121(553), 477-491. https://doi.org/10.1080/01621459.2025.2526700
Black, J. R., Irtisam, R., & Jain, P. K. (2025). Textual uncertainty in financial disclosures and information asymmetry among investors. Financial Review, 60(3), 799-829. https://doi.org/10.1111/fire.12430
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2024). The global impact of Brexit uncertainty. The Journal of Finance, 79(1), 413-458. https://doi.org/10.1111/jofi.13293
Jurado, K., Ludvigson, S. C., & Ng, S. (2015). Measuring uncertainty. American Economic Review, 105(3), 1177-1216. https://doi.org/10.1257/aer.20131193
Bloom, N. (2009). The impact of uncertainty shocks. Econometrica, 77(3), 623-685. https://doi.org/10.3982/ECTA6248
<!-- rendered-citations:end -->
