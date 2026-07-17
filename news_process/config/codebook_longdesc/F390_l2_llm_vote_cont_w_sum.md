---
family_id: F390
columns:
- llm_vote_cont_w_sum_ctx
- llm_vote_cont_w_sum_full
- llm_vote_cont_w_sum_ss
unit: 无量纲加权求和 (mention_density 权重 × 情感连续编码之和, bank-year 分子量)
formula: 'llm_vote_cont_w_sum{track} = Σ_i (llm_vote_cont{track}_i × mention_density_i), 其中 llm_vote_cont{track}_i = llm_vote_score{track}_i × llm_agreement_rate{track}_i, mention_density_i = target_bank_mention_count_i / doc_length_i; 求和跨该 bank-year 下全部文章 i (含未通过留篇门控的行, 其贡献视 llm_vote_cont 缺失/NaN 自然传播); 下游 llm_vote_cont_vw{track} = llm_vote_cont_w_sum{track} / sum_mention_density 完成 value-weighted 均值化'
producer: pipeline\panel\encode.py (agg 字典组装, L992-L994) + pipeline\panel\runner.py (文章级 _w 权重列预计算, L747-L758)
upstream:
- pipeline\filtering\news_bank.py (mention_density 原语)
- pipeline\sentiment\tone_llms.py (llm_vote_score{track}/llm_agreement_rate{track} 三家 LLM 投票)
citations:
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: 'FinBERT: A large language model for extracting information from financial text'
  venue: Contemporary Accounting Research
  vol: '40'
  issue: '2'
  pages_or_artno: 806-841
- doi: "10.1609/aaai.v39i18.34120"
  type: "journal"
  authors: "Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C."
  year: 2025
  title: "Calibrating Large Language Models with Sample Consistency"
  venue: "Proceedings of the AAAI Conference on Artificial Intelligence"
  vol: "39"
  issue: "18"
  pages_or_artno: "19260-19268"
- doi: "10.1287/mnsc.2024.08999"
  type: "journal"
  authors: "Burtch, G., McFowland, E., Yang, M., & Adomavicius, G."
  year: 2026
  title: "EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables"
  venue: "Management Science"
  pages_or_artno: "mnsc.2024.08999"
new_dois: []
---

## CORE

【构念与来源】
本家族三列是 P1 (`bank_fintech_tone`) 情感三轨体系下的 value-weighted (VW) 连续情感聚合分子量, 母体是逐篇 LLM 三家投票 (gpt54nano/gemini31/deepseekv4) 多数共识产出的连续编码 `llm_vote_cont{track}`。构念动机分两层: 第一层是"用连续量而非离散 ±1/0 三分类刻画情感强度"——`llm_vote_cont{track}` = `llm_vote_score{track} × llm_agreement_rate{track}`, 即离散共识方向乘以三家投票一致率, 一致率越高说明信号越可信, 一致率越低 (三家分歧大) 则把该篇的贡献向 0 收缩, 这是对纯多数票"赢者通吃"离散化损失信息的补偿, 呼应 Kamen & Kamen (2025) 关于 LLM 集成投票优于单模型裁决的发现, 也与 de Kok (2025, *Management Science*) 强调的生成式 LLM 用于会计/金融文本分析须搭配可信度加权的建议一致。第二层是"用注意力权重而非等权平均刻画银行在报道中的重要性"——`mention_density` = 该银行在该文章中的提及次数 / 文档总字数 (`pipeline/filtering/news_bank.py` 物化), 是 Hassan, Hollander, van Lent & Tahoun (2019, *QJE*) firm-level political risk 测度所用 value-weighted (VW) 聚合思路在本项目的移植: 一篇文章若用大篇幅反复提及目标银行, 其情感信号对该银行更具代表性, 理应比"顺带提一句"的报道权重更高。`llm_vote_cont_w_sum{track}` 正是把这两层权重相乘后逐篇累加, 是构造 VW 情感均值的分子, 本身不是一个可直接解释的"情感水平"指标, 而是聚合链条的中间量。

【方法学与计算】
计算发生在两个阶段。第一阶段在 `pipeline/panel/runner.py` (文章级预计算, 步骤3b): 若源数据存在 `mention_density` 列, 则取 `w = mention_density.fillna(0)`, 对三轨分别构造文章级列 `llm_vote_cont_w{track} = llm_vote_cont{track} × w`; `mention_density` 缺失的文章 `w=0`, 对应贡献恒为 0 (而非 NaN), 这是刻意设计——保证零权重文章不会因缺失把整个 bank-year 的和污染成 NaN。第二阶段在 `pipeline/panel/encode.py` (bank-year 聚合, `agg` 字典组装 L992-L994): 对三轨分别执行 `agg[f'llm_vote_cont_w_sum{track}'] = (f'llm_vote_cont_w{track}', 'sum')`, 即 groupby(bank, year) 后对文章级加权列取 sum。`llm_vote_cont{track}` 本身在无效篇 (未通过 LLM 验证/调用失败/undefined) 上是 pandas nullable NaN, 与权重相乘后按 NaN 传播规则仍为 NaN, pandas `sum` 聚合默认跳过 NaN (skipna=True), 故实际分子只累计"有效篇×权重"的贡献, 与下游分母 `sum_mention_density` (跨全部文章, 含 mention_density>0 但情感无效的文章) 存在口径上的细微不对称——这也是为何该列被设计为聚合中间量而非终端指标 (终端指标 `llm_vote_cont_vw{track}` 见下)。下游用法 (encode.py L2196-L2202): `denom = panel['sum_mention_density'].replace(0, np.nan)`, 再 `llm_vote_cont_vw{track} = llm_vote_cont_w_sum{track} / _llm_denom('vw', 'llm', track, denom)`, `_llm_denom` 是本项目统一的分母守卫函数, 对零新闻/全缺失 bank-year 走优雅退化 (NaN 而非除零报错)。三轨 (full/ctx/ss) 严格并排各自独立计算, 互不借用彼此的权重或分子: `_full` 用全文, `_ctx` 用标题+实体窗口, `_ss` 用标题+银行∧金科同句±N窗 (回退语义镜像 `_ctx`: 无同句共现时 `content_ss` 退化为全文 body, `ss_is_fallback=True`); 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨列混进同一个 over-identified Hansen J 检验。留篇门控自 2026-06-29 起收紧为 full-only, 即"是否算作一篇银行×金科报道"只看 `llm_verified_full`, ctx/ss 轨的本列在此约束下是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集合的子集, 但 per-track 分子分母仍各自独立计算, 不借用 full 轨的分子或分母。

【文献定位】
本家族方法学定位横跨两条文献线。VW 聚合思路直接对标 Hassan et al. (2019, *QJE*) 的 firm-level political risk 测度框架, 该文用"每篇电话会议记录中政治风险相关 bigram 的占比"作分子、通话总长度作分母构造暴露度, 本项目将其迁移到"银行提及密度 × LLM 情感连续编码"的场景, 用意相同: 让报道篇幅/显著度大的文章对聚合结果贡献更大, 而非把一句带过的提及与整篇专题报道等权平均。三家 LLM 多数投票 + 一致率折算连续编码的做法, 一方面借鉴 de Kok (2025, *Management Science*) 关于生成式 LLM 文本分析方法论的规范讨论 (temperature=0/prompt 冻结/缓存范式与本项目 stage 21 的确定性锚点设计一致), 另一方面呼应 Kamen & Kamen (2025) 关于 LLM 集成 (ensemble) 优于单模型多数投票裁决稳健性的发现——本项目三家模型 (gpt54nano/gemini31/deepseekv4) 各自独立产出情感判断, 一致率本身即是集成分歧度的度量, 并被内嵌进连续编码的构造中。作为对照, FinBERT (Huang, Wang & Yang, 2023, *Contemporary Accounting Research*) 代表财经文本情感测量的另一条技术路线 (监督微调 BERT 而非 zero-shot LLM 投票), 本项目在 stage 23 并行产出三家 BERT 模型的情感测度与本 LLM 家族互为稳健性, 二者共享 mention_density VW 加权聚合的下游逻辑但不共享上游模型, 体现"情感三法各自的 per-model 子测度并排为互为稳健性、不分主次轨"的项目级铁律。 在"以一致率折算连续置信权重"这一具体构造上, Lyu 等 (2025) 提供了更直接的方法学依据: 该文系统比较多种置信度来源, 实证表明由多次采样输出之间的一致性导出的置信度, 其校准性优于模型自报置信度与 logit 概率——这正是本项目不取模型自报分数、而以 `llm_agreement_rate{track}` 充当连续权重的理由。迁移边界须诚实标明: 原文的一致性来自同一模型在正温度下的重复采样, 本项目 temperature=0.0 且不重复采样, `agreement_rate` 是三家不同厂商模型的跨模型投票一致率 ∈[1/3,1], 属跨模型而非跨采样的一致性, 其校准性质未被原文覆盖; 且原文任务为英文推理/QA 基准, 非中文新闻三分类情感, 亦不涉及 `mention_density` 加权与 bank-year 求和, 故该文只锚定"用一致性而非自报分数作置信度"这一层, 不能外推为对本列权重已校准的举证。沿聚合链条向下游看, Burtch、McFowland、Yang 与 Adomavicius (2026) 触及的是本列这类量最终进入回归时的推断问题: 该文利用集成学习器内部各成员预测之间的差异构造工具变量, 以缓解 ML 生成变量作为回归元时的测量误差偏误, 与本项目"多个异构模型对同一篇文章各自打分、成员间存在系统性差异"的结构同构, 为下游用这些聚合量做回归提供了一条已发表的处理路径。迁移边界同样明确: 原文的集成成员是同一训练流程下的 ML 预测器, 成员差异有明确的重采样来源, 而本项目成员是三家闭源 LLM, 差异来源不可控亦不可重采样, 原文构造 IV 的前提未必成立; 本项目未实施 EnsembleIV, 该文仅作为下游推断路径的参照存档, 不得据以把三家 per-model 子测度混进同一个 over-identified Hansen J (与桶内各自 just-identified 并排、互为稳健性不分主次的铁律冲突)。
## VAR: llm_vote_cont_w_sum_ctx

【变体差分】
本列取 `_ctx` 轨: 文章级源文本为 `content_ctx` (标题 + 银行/金科实体窗口物化文本, stage 14 `ctx_materializer` 产出), 分子逐篇取 `llm_vote_cont_ctx = llm_vote_score_ctx × llm_agreement_rate_ctx` 再乘以 `mention_density` 后按 bank-year 求和。`_ctx` 轨与 `_full`/`_ss` 轨严格并排各自独立跑三家 LLM 投票, 不共享情感判断结果, 也不共享权重来源 (三轨共用同一个 `mention_density` 权重列, 该列本身是 track-agnostic 的文章级元数据, 不随文本轨切换)。2026-06-29 起留篇门控收紧为 full-only, 本列的行宇宙是 `llm_verified_full == True` 的留篇集合的子集 (conditional-on-full), 是 full 轨主测度的稳健性/测量替代轨, 用以检验"聚焦实体窗口而非全文"是否改变情感聚合方向与量级; 与 `_full`/`_ss` 互为稳健性、不分主次, 三者禁止混入同一个 over-identified Hansen J 检验框架。本列若 `mention_density` 或 `llm_vote_cont_ctx` 缺失, 对应文章贡献按上文 CORE 所述规则处理 (权重缺失 → 0; 情感缺失 → NaN 被 sum 跳过), 该列自身不直接构成可解释的情感水平, 须除以 `sum_mention_density` 得到 `llm_vote_cont_vw_ctx` 才是终端可解释测度。选择实体窗口而非全文的动机是控制"无关段落噪声稀释情感信号"——一篇长文可能只有一两句真正涉及银行与金科业务的实质判断, 其余段落谈其他议题, 全文轨会把这些无关段落一并纳入 LLM 情感判断的上下文, 而 `_ctx` 轨把上下文收窄到实体窗口, 理论上应得到更"聚焦"但样本量/信息量更少的情感估计; 二者孰优孰劣是经验问题, 故设计为并排稳健性轨而非互相替代。本列与三家 LLM 逐模型 `_ctx` 子列 (`{short}_cont_w_sum_ctx`) 同样是并排关系, 逐模型子列反映跨厂商稳健性, 本列是三家共识汇总, 二者不应混入同一识别方程。

## VAR: llm_vote_cont_w_sum_full

【变体差分】
本列取 `_full` 轨: 文章级源文本为标题+全文正文, 是三轨中的 canonical/主测度轨, P1 (`bank_fintech_tone`) 主处理变量 `llm_vote_tone_full` 的姊妹加权量。自 2026-06-29 起, 是否算作"一篇银行×金科报道"这一留篇门控判定唯一以 `llm_verified_full == True` 为准 (`tone_llms.py::df_filtered` 与 `run_pipeline_function.py::_stage21_skip_is_compatible` 两处门控副本须同步, 是本项目的已知易错点), 因此本列所在的行宇宙即为门控本身定义的留篇集合, 不是任何其他轨的子集或超集。分子为 `llm_vote_score_full × llm_agreement_rate_full × mention_density` 逐篇累加, 权重 `mention_density` 与 `_ctx`/`_ss` 两轨共用同一原始列 (提及密度是文章×银行层面的元数据, 不随情感测量所用文本窗口切换)。本列与 `_ctx`/`_ss` 两轨各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一个 over-identified Hansen J; 与三家 LLM 逐模型子列 (`{short}_cont_w_sum_full`, `short∈{gpt54nano,gemini31,deepseekv4}`) 亦是并排关系——本列是三家多数投票共识后的连续编码汇总, 逐模型子列是跨厂商稳健性轨, 二者共享同一 `mention_density` 权重但情感来源不同, 不应混入同一识别方程。作为 P1 主处理变量 `llm_vote_tone_full` (离散均值口径) 的姊妹加权连续量, 本列在其分子构造上多乘了一层 `llm_agreement_rate_full`, 因此即便对应文章的离散共识方向相同, 三家分歧越大的文章对本列的贡献越被压缩, 这是本列与同源离散加权列 `llm_vote_score_w_sum_full` 之间的构念区分——后者只反映方向和篇幅权重, 不反映投票一致性。

## VAR: llm_vote_cont_w_sum_ss

【变体差分】
本列取 `_ss` 轨: 文章级源文本为 `content_ss` (标题 + 银行∧金科同句±N窗物化文本, `config/filtering.yaml::context_window.ss_sentence_radius` 默认1)。`_ss` 轨的回退语义严格镜像 `_ctx`: 若一篇文章中银行与金科词未出现在同一句 (或该句±N窗) 内, `content_ss` 退化为全文 body, 对应 `ss_is_fallback=True`, 该退化标记与 `n_articles` 共享分母, 情感三家 LLM 在此退化文本上仍照常产出 `llm_vote_score_ss`/`llm_agreement_rate_ss`, 进而正常参与本列的加权求和; `FINTECH_AC=None` (金科词典缺失) 时 `*_is_fallback` 全体退化为 True, 本列在此极端情形下等价于对全文文本重复计算, 属已知优雅降级而非静默出错。分子构造与 `_full`/`_ctx` 两轨完全同构 (`llm_vote_score_ss × llm_agreement_rate_ss × mention_density` 逐篇累加), 行宇宙是 `llm_verified_full` 留篇集合的子集 (full-only 门控下的 conditional-on-full 稳健性轨)。本列与 `_full`/`_ctx` 互为稳健性、不分主次, 是三轨中对"银行与金科共现证据最严格"的一支——只用最贴近共现证据的句子窗口来源文本 (退化情形除外) 度量情感, 用以检验主结论是否被更宽松的实体窗口或全文噪声驱动; 三者禁止混入同一个 over-identified Hansen J 识别框架。需注意本列在退化子样本 (`ss_is_fallback=True`) 与非退化子样本上的构念含义并不完全等价: 非退化篇是"同句共现"这一最严格判据下的情感度量, 退化篇实质上复制了 `_full` 轨的文本, 二者混在同一个 bank-year 求和里意味着某些 bank-year 的本列取值更接近 `_full` (退化篇占比高), 另一些更接近纯同句轨 (退化篇占比低), 这一异质性是解读本列时须结合 `ss_is_fallback` 占比一并披露的已知局限, 而非可忽略的实现细节。

<!-- rendered-citations:begin -->
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C. (2025). Calibrating Large Language Models with Sample Consistency. Proceedings of the AAAI Conference on Artificial Intelligence, 39(18), 19260-19268. https://doi.org/10.1609/aaai.v39i18.34120
Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
<!-- rendered-citations:end -->
