---
family_id: F545
columns:
- sum_wd_vw_prob_ctx
- sum_wd_vw_prob_full
- sum_wd_vw_prob_ss
unit: 无量纲权重和 (herd_weight 的银行-年加总, 与跟风衰减权重同量纲)
formula: 'sum_wd_vw_prob{track} = Σ_i∈{有效 prob 分数的报道} herd_weight{track}_i (bank-year 内对 herd_weight{track} 求和, 求和域限定在 llm_prob_score 非缺失的报道子集)'
producer: pipeline/panel/encode.py::build_aggregation_dict (聚合字典登记, 逐 track/权重类别/分组生成 sum_wd_{wtag}_{grp}{track} 族, 本家族 wtag=vw、grp=prob) + aggregate_panel (下游 _llm_denom 消费本列作除法分母)
upstream:
- 24_herd_decay_processor (herd_weight_full/_ctx/_ss 三轨跟风衰减权重生产)
- 21_tone_llms (llm_prob_score 有效性掩码, 决定本列求和域)
citations:
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: 'Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy'
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: 10.1145/1102351.1102430
  type: wp
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: Predicting good probabilities with supervised learning
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: "10.1371/journal.pone.0323064"
  type: "journal"
  authors: "Wright, D., & Augenstein, I."
  year: 2025
  title: "Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift"
  venue: "PLOS One"
  vol: "20"
  issue: "6"
  pages_or_artno: "e0323064"
- doi: "10.2139/ssrn.4842086"
  type: "wp"
  authors: "Battaglia, L., Christensen, T., Hansen, S., & Sacher, S."
  year: 2024
  title: "Inference for Regression with Variables Generated from Unstructured Data"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "4842086"
- doi: "10.1093/rfs/hhq141"
  type: "journal"
  authors: "Tetlock, P. C."
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: "The Review of Financial Studies"
  vol: "24"
  issue: "5"
  pages_or_artno: "1481-1512"
new_dois: []
---

## CORE

【构念与来源】
F545 三列 (`sum_wd_vw_prob_full`/`_ctx`/`_ss`) 不是独立构念, 而是 VW (value-weighted, 跟风衰减加权) Tone 测度族里 LLM 概率子测度 (`prob`, 即基于 logit-to-score 概率化情感分数的报道级测度) 的分母原材料: 银行-年内、在该报道有有效 `llm_prob_score` 的子集上, 对 stage 24 产出的跟风衰减权重 `herd_weight{track}` 求和。三轨 (`_full`/`_ctx`/`_ss`) 分别对应银行金科三种正文文本口径 (full=标题+全文; ctx=标题+实体窗口; ss=标题+银行∧金科同句±N窗)。本列本身在面板里不作为回归自变量出现, 它的唯一下游消费者是 `pipeline/panel/encode.py::aggregate_panel` 内的私有函数 `_llm_denom`, 用来把分子 `llm_prob_score_w_sum{track}` (Σ herd_weight · llm_prob_score, 报道级乘积后求和) 除成 `llm_vote_tone_vw_prob{track}` —— VW 口径下、以 LLM 概率化打分为测度基础的银行-年语调指数。因此理解 F545 必须放在"分子/分母配对"的框架下: F545 是配对里的分母半边, 缺了它, VW-prob Tone 就无法从报道级权重×分数聚合成银行-年比率。

跟风衰减权重 `herd_weight` 的构造理念来自 Tetlock (2011, RFS) "跟风衰减"(herding decay) 的操作化: 单篇报道在信息集里的边际信息含量, 会随同期同主题报道数量增加、内容相似度上升而衰减 — 一篇报道如果只是重复既有报道的论调 ("抄稿"), 它对市场/投资者认知的边际贡献理应打折扣, 而非与首发独家报道同权重计入银行-年语调均值。stage 24 (`herd_decay_processor`) 按此思路给每篇报道打出 `herd_weight{track}` ∈ (0, 1], 越像"抄稿"权重越低、独家或首发报道权重越高。VW Tone 正是用这个权重做加权平均 (而非算术平均, 即 EW/等权口径), 是 herd-attention 稳健性轨的核心构造。

【方法学与计算】
构造分两步。第一步 (stage 24 上游): 对每篇报道、每条轨道 `{track}`, 计算 `herd_weight{track}_i ∈ (0, 1]`, 衡量该报道相对同期同族报道的"独家度/边际信息量"。第二步 (`encode.py::build_aggregation_dict`, 本家族的真实产出点): 在 bank-year groupby 聚合阶段, 对每个 (轨道, 权重类别, LLM 分组) 三元组注册一条聚合规则, 即 `agg[f'sum_wd_{wtag}_{grp}{track}'] = (f'_wd_{wtag}_{grp}{track}', 'sum')`。其中 `wtag='vw'` (本家族固定值)、`grp='prob'` (本家族固定值, 表示 LLM 概率化打分族)、`track ∈ {'_full','_ctx','_ss'}`。中间列 `_wd_vw_prob{track}` 是报道级掩码化权重: 当该报道 `llm_prob_score{track}` 有效 (非缺失、通过 stage 21 留篇门控) 时取值 `herd_weight{track}`, 否则为缺失/被 groupby-sum 自动跳过。这一步的动机记录在源码 encode-01 修复注记 (2026-06-10): LLM 族的分子 `llm_prob_score_w_sum{track}` = Σ(herd_weight · llm_prob_score) 是 nullable 求和, 无效行 (llm_prob_score 缺失) 会被自动跳过求和 — 若此时分母仍用"物理全量" Σ herd_weight (不管该报道 llm_prob_score 是否有效都计入), 就会出现分子只计有效样本、分母却含全部样本的系统性错配, 导致算出的语调值被人为压向 0 (因为分母偏大)。F545 三列正是为修正这一错配而生的"valid-mask 分母" —— 分子分母严格同域: 只对 `llm_prob_score{track}` 有效的报道子集求 herd_weight 之和, 保证 `llm_vote_tone_vw_prob{track} = Σ_valid(herd_weight·llm_prob_score) / Σ_valid(herd_weight)` 是真正的加权平均, 值域落在概率化分数的取值范围内, 不会因分母虚高而失真收缩。

需要特别强调的口径边界: 这一 valid-mask 分母修正仅适用于 LLM 族 (`llm`/三家 per-model/`prob` 分组), 不适用于词典族与 BERT 族。源码注记 (reaudit-2026-07-12 WP-A5) 明确前提: 词典族因 stage 13 硬过滤 + `prepend_title` 保证存活行必含真实 token, 不存在"空文本导致分数缺失"的分支, 每篇存活报道必有词典分数, 不需要这个修正; BERT 族仅在推理失败时才无分数 (实测样本为 0 篇), 有观测闸监控, 修正留待重生窗口处理。因此 F545 (`_wd_vw_prob`) 与其姊妹家族 `sum_wd_vw_llm`/`sum_wd_hw_*_llm` (F544 及邻近家族) 都专属 LLM 族, 是同一套"valid-mask 分母"机制在不同权重类别 (vw=价值加权 herd 权重 / hw=阈值敏感性版 herd 权重) 、不同分组 (llm=共识投票 / per-model=三家各自 / prob=概率化打分) 上的并排实例。

三轨口径遵循项目铁律: full/ctx/ss 三条文本轨道各自独立构造分子分母、各自 just-identified, 互为稳健性、不分主次, 严禁把三轨的 VW-prob Tone 混进同一个 over-identified 的 Hansen J 检验框架。`_ss` 轨遵循与 `_ctx` 对称的回退语义: 若某篇报道在标题窗口内找不到银行∧金科词的同句共现, 则 `content_ss` 回退为全文正文 (`ss_is_fallback=True`), 该报道的 `llm_prob_score_ss` 依旧照常计算 (回退是文本口径层面的降级, 不是"该报道无效"), 因此 `sum_wd_vw_prob_ss` 的求和域与 `_full`/`_ctx` 遵循同一条"该报道 prob 分数有效即计入"规则, 不因文本回退而额外剔除。留篇门控本身在全部三轨上统一采用 full-only 口径 (2026-06-29 起): 一篇报道是否被认定为"有效的银行-金科报道"只看 `llm_verified_full`, ctx/ss 轨是 full 留篇集合的条件测度子集, 三轨的行宇宙相同、只是文本口径与由此产生的 `llm_prob_score{track}` 有效性掩码不同。

在面板导出的零填契约里, F545 三列属于"计数/和类"列 (与 `sum_herd_weight_*`、`sum_mention_density`、`n_articles_*` 等同一处理组): 银行-年若无任何符合条件的报道 (即该行是零新闻或零有效样本的银行-年), 该列填充为 0 而非缺失, 与 `sum_herd_weight_full/_ctx/_ss` 采用完全相同的"前缀式命名, 末尾为 `weight_<track>` 而非 `_sum_<track>`"式零填修复历史 (encode.py 内 `wd_cols = [c for c in panel.columns if c.startswith('sum_wd_')]` 精确捕获本家族三列纳入零填批处理)。下游消费该列做除法时, 面板层还会做一次 `replace(0, np.nan)` 的除零保护 (`_llm_denom` 函数), 因此"零新闻/零有效样本银行-年"最终在语调比率列上呈现为缺失而非除零溢出, 但 F545 本身作为原始权重和列, 契约上仍以 0 呈现零样本情形。

【文献定位】
本家族的方法学定位横跨两条文献线。其一, VW (价值加权/跟风衰减加权) 与 EW (等权) 并列作为舆情/文本情感测度的构造选择, 呼应文本情感分析方法学综述中对不同聚合权重方案效度差异的系统梳理 (van Atteveldt et al., 2021, *Communication Methods and Measures*: 比较人工标注、众包编码、词典法与机器学习算法在情感分析效度上的系统性差异, 强调聚合权重与测度构造选择会实质性影响下游效度)。其二, 本家族服务的是 LLM 概率化打分 (`llm_prob_score`, 即由 LLM logit/置信度转成的连续概率分数, 而非离散多数投票标签) 这一测度分支的分母基础设施, 这类"多 LLM 集成打分聚合到银行-年"的构造理念呼应 LLM 集成预测能力的实证证据 (Schoenegger et al., 2024, *Science Advances*: LLM 集成预测能力可比拟人类众包准确度的"硅基群体智慧"), 支持本项目采用三家 LLM 概率化打分并加权聚合而非单模型硬标签的设计选择。概率化打分本身 (logit-to-score) 的方法学根基在于监督学习中"良好概率预测"的经典处理 (Niculescu-Mizil & Caruana, 2005, ICML: 讨论如何从监督学习模型获得校准良好的概率预测), 为本项目把 LLM 输出转成连续概率分数、再据此加权聚合提供方法论参照。LLM 概率化打分相较词典法在情感判定质量上的优势另有 Frankel, Jennings & Lee (2022, Management Science) 的顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 LLM 概率化打分承担情感测度主力而非词典法提供了顶刊层级的方法学背书。 在此之上, 还有两条更贴近本家族"分母侧"构造本身的前沿线索。Wright 与 Augenstein (2025) 在 NLP 标注聚合基准上系统比较了把多位标注者的软标签 (概率) 汇总成训练/评估目标的若干方案, 发现分布偏移下软标签聚合比硬标签多数投票给出更好的不确定性估计; 这正对应本项目 prob 分组 (LLM 概率化打分) 与 llm 分组 (三家硬多数投票共识) 两条并排轨的构造分野, 说明"保留概率而非先塌缩成标签"在测度层有其独立价值。迁移边界须诚实交代: 该文的标注者是人类众包工人而非三家商用 LLM, 其目标是分类器不确定性校准而非银行-年面板分母的权重求和, 亦无三轨文本口径、跟风衰减权重与银行-年聚合层, 语料为英文基准集; 故它只提供构念层面的参照, 不构成 prob 轨优于 llm 轨的证据 —— 两组分母仍互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J。Battaglia、Christensen、Hansen 与 Sacher (2024) 则为"先从非结构化文本生成变量、再把该变量代入回归"这一两步流程建立了推断理论, 证明朴素代入会产生系统性偏误并给出修正估计量与有效标准误; 本家族恰是该流程的分母半边: LLM 从新闻文本生成 llm_prob_score, 其有效性掩码决定哪些报道进入加权求和, 因而这条线索是本列构造必须正视的方法学警示。迁移边界同样明确: 该文处理的是回归中生成型变量本身的偏误, 本列则是"有效性掩码构成的权重分母", 层级不同; 其例证以英文非结构化语料为主, 不涉及中文银行金科新闻、银行-年面板与三轨设定, 亦未处理多模型投票共识; 且本项目 F545 目前只做有效性掩码同域求和以消除分子分母错配, 并未实施该文的偏误修正估计量, 故此处引用限于方法学参照与已知缺口的登记, 不应被读作本列已获该文意义上的偏误校正。
## VAR: sum_wd_vw_prob_ctx

【变体差分】
本列是 F545 家族在 `_ctx` 轨 (标题+实体窗口正文) 上的实例: `sum_wd_vw_prob_ctx = Σ_i∈{llm_prob_score_ctx 有效} herd_weight_ctx_i`, 即在 ctx 文本口径下、对该银行-年内所有 `llm_prob_score_ctx` 非缺失的报道, 求其 `herd_weight_ctx`(ctx 轨跟风衰减权重) 之和。ctx 轨的权重来源 (`herd_weight_ctx`, stage 24 产出) 与有效性掩码 (`llm_prob_score_ctx` 是否缺失) 均取 ctx 口径下的值, 与 `_full`/`_ss` 两轨完全独立构造, 互不借用彼此的权重或掩码。ctx 轨行宇宙是 full 留篇集合 (`llm_verified_full=True`) 的条件子集, 该子集内报道若在 ctx 窗口下产生了有效 prob 分数, 才计入本列求和; 若 stage 21 对该报道未产出 ctx 轨分数或分数被判无效, 则不计入, 与 `sum_wd_vw_prob_full` 的求和域可能不完全重合 (即便行宇宙相同, 各轨"有效"的判定各自独立)。本列是分母半边, 唯一下游用途是与同轨分子 `llm_prob_score_w_sum_ctx` 相除得到 `llm_vote_tone_vw_prob_ctx`, 作为 ctx 轨 VW-prob Tone 的构造中间量, 不建议直接作为回归自变量单独解读经济含义; 若需要跨轨比较权重和规模本身 (而非语调比率), 应同时报告 full/ctx/ss 三列并说明其分别为 just-identified 并排稳健性口径, 不构成单一 over-identified 检验的联合矩条件。实践上, ctx 轨的求和域通常小于等于 full 轨: 因为 ctx 轨要求实体窗口内存在可供 LLM 判读的有效上下文片段, 部分在 full 轨被判有效的报道, 在 ctx 窄窗口下可能因上下文不足而未产出有效 `llm_prob_score_ctx`, 使得 `sum_wd_vw_prob_ctx` 的样本覆盖度天然收缩于 `sum_wd_vw_prob_full`; 这一收缩是三轨稳健性设计的预期特征, 而非缺陷 —— 它恰恰检验了"语调结论是否依赖于喂给 LLM 的正文长度/上下文窗口选择"这一构念效度问题。

## VAR: sum_wd_vw_prob_full

【变体差分】
本列是 F545 家族在 `_full` 轨 (标题+全文正文) 上的实例, 也是三轨中口径覆盖面最广的一支: `sum_wd_vw_prob_full = Σ_i∈{llm_prob_score_full 有效} herd_weight_full_i`。由于留篇门控本身即以 full-only 口径判定"是否为一篇有效的银行-金科报道" (`llm_verified_full`, 2026-06-29 起生效), `_full` 轨的行宇宙就是完整的留篇集合本身, 不像 ctx/ss 是其条件子集意义上的"降维稳健性轨"。因此 `sum_wd_vw_prob_full` 及其配对的 `llm_vote_tone_vw_prob_full` 是本项目 P1 (`bank_fintech_tone`) 及相邻 paper 模块里 VW-prob Tone 测度的主参照口径 (canonical 覆盖面意义上, 但与 ctx/ss 仍严格并排、不构成主次判定); 三轨依旧遵循"各自 just-identified、互为稳健性、禁混同一 Hansen J"的项目铁律, `_full` 只是行宇宙最完整而非方法论上凌驾于 ctx/ss 之上。本列的求和域 (哪些报道的 `llm_prob_score_full` 被判定有效) 完全由 stage 21 三家 LLM 投票流水线的 full 轨输出决定, 与 herd_weight 的具体数值无关 —— herd_weight 只决定"计入多重"、有效性掩码只决定"计入与否", 两者是本列构造里两个独立的筛选/加权维度。在面板导出的零填契约里, 本列若对应银行-年无任何有效报道 (例如该银行该年新闻覆盖为零, 或该银行该年虽有报道但 stage 21 未能对任何一篇产出有效 full 轨概率分数), 会被填充为数值 0 而非缺失, 使其与 `sum_herd_weight_full` 等同族权重和列在契约层面保持一致语义; 但下游相除得到 `llm_vote_tone_vw_prob_full` 时, 该行会经过 `_llm_denom` 的除零保护 (0 → NaN) 转为语调比率缺失, 因此在 F545 本列层面看到的"0"不应被误读为"该行语调为零", 而应理解为"该行无有效样本可供加权"。

## VAR: sum_wd_vw_prob_ss

【变体差分】
本列是 F545 家族在 `_ss` 轨 (标题+银行∧金科同句±N窗) 上的实例: `sum_wd_vw_prob_ss = Σ_i∈{llm_prob_score_ss 有效} herd_weight_ss_i`, 权重取值与有效性掩码均严格取 ss 口径。`_ss` 轨的关键差异在于其底层文本 `content_ss` 存在回退语义, 镜像 `_ctx` 的回退设计: 若某篇报道的标题窗口内找不到目标银行与金科词的同句共现, 则 `content_ss` 退化为全文正文 (与 `content_full` 内容相同), 并标记 `ss_is_fallback=True`; 但这一回退只影响喂给 LLM 的文本内容, 不影响该报道是否被计入本列求和域 — 只要该报道在 full 轨留篇门控下有效、且 stage 21 在 ss 轨(不论是否回退)产出了非缺失的 `llm_prob_score_ss`, 就照常计入 `sum_wd_vw_prob_ss` 及其对应的 `herd_weight_ss`。换言之, ss 轨回退改变的是"用什么文本估计分数", 不改变"这篇报道是否进入 VW-prob 分母的求和域"这一判定逻辑, 二者是正交的两层机制。若上游 `FINTECH_AC`(金科词自动机)为 None, 则全部报道的 `*_is_fallback` 优雅降级为 True, ss 轨退化为等同 full 轨的文本内容, 但求和域判定逻辑不变。与 `_full`/`_ctx` 一样, 本列是纯粹的分母中间量, 与配对分子相除后才产出可解释的 `llm_vote_tone_vw_prob_ss` 语调比率; 三轨互为稳健性并排, 不设主次。由于 `_ss` 判据 (银行∧金科同句共现) 比 `_ctx` 判据 (实体窗口) 更窄, 触发回退的报道占比通常高于 ctx 轨, 但如上文所述回退不改变求和域判定, 因此 `sum_wd_vw_prob_ss` 的样本覆盖度理论上应接近 `sum_wd_vw_prob_full` (而非因回退而系统性收缩), 与 ctx 轨因窗口不足直接产生无效分数的收缩机制不同; 若实测中 ss 轨覆盖度显著低于 full 轨, 应优先排查 stage 21 ss 轨本身的分数产出成功率, 而非归因于回退语义。研究者在使用本列做样本量核算或稳健性披露时, 应同时报告三轨各自的覆盖度差异及其成因, 避免把窗口构造差异误判为语调结论的不稳健。

<!-- rendered-citations:begin -->
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML) No. 625-632 [Working Paper]. https://doi.org/10.1145/1102351.1102430
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Wright, D., & Augenstein, I. (2025). Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift. PLOS One, 20(6), e0323064. https://doi.org/10.1371/journal.pone.0323064
Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for Regression with Variables Generated from Unstructured Data. SSRN Electronic Journal No. 4842086 [Working Paper]. https://doi.org/10.2139/ssrn.4842086
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information? The Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
<!-- rendered-citations:end -->
