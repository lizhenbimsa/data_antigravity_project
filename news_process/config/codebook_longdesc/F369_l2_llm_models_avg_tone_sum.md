---
family_id: F369
columns:
- llm_models_avg_tone_sum_ctx
- llm_models_avg_tone_sum_full
- llm_models_avg_tone_sum_ss
unit: 语调净得分之和 (连续, 逐年逐轨对篇均得分再求和; 三家 LLM 跨模型均值)
formula: 'panel[f"llm_models_avg_tone_sum{track}"] = mean_over_s_in_LLM_MODELS(panel[f"{s}_tone_sum{track}"]), track ∈ {_full, _ctx, _ss}; 逐 bank-year 行按存在列取算术均值 (geography.py::_safe_mean, 缺列优雅 NaN)'
producer: pipeline\panel\geography.py
upstream:
- 21_tone_llms.parquet
- pipeline\sentiment\tone_llms.py
- pipeline\panel\encode.py
citations:
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: 'Large language models: An applied econometric framework'
  venue: NBER Working Paper No. 33344
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: 'FinBERT: A large language model for extracting information from financial text'
  venue: Contemporary Accounting Research
  vol: '40'
  issue: '2'
  pages_or_artno: 806-841
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: Chinese fine-grained financial sentiment analysis with large language models
  venue: Neural Computing and Applications
  vol: '37'
  issue: '30'
  pages_or_artno: 24883-24892
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: "10.18653/v1/2024.law-1.13"
  type: "journal"
  authors: "Rønningstad, E., Velldal, E., & Øvrelid, L."
  year: 2024
  title: "A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation"
  venue: "Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII)"
  pages_or_artno: "133-139"
- doi: "10.48550/arxiv.2406.04692"
  type: "arxiv"
  authors: "Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J."
  year: 2024
  title: "Mixture-of-Agents Enhances Large Language Model Capabilities"
  venue: "arXiv"
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
本家族衡量的是三家大语言模型 (LLM) 对同一篇银行—金融科技共现报道所打分的语调净得分之和, 跨模型取算术均值, 逐三轨落盘。三家模型分别是 `gpt-5.4-nano` (内部短名 gpt54nano)、`gemini-3.1-flash-lite` (内部短名 gemini31, 二者均经由 OpenLux 网关调用) 与 `deepseek-v4-flash` (内部短名 deepseekv4, 直连 api.deepseek.com)。stage 21 (`pipeline/sentiment/tone_llms.py`) 让三家模型各自独立读取同一篇文章 (标题 + 正文, 依轨道不同而窗口不同), 输出结构化判断: 是否为一篇有效的"银行×金融科技"报道 (`llm_verified`)、语调分类 (正面/中性/负面 三分类) 与置信度; encode 层 (`pipeline/panel/encode.py`) 把逐篇判断在 bank-year 单元内聚合为 `{model}_tone_sum{track}` (该 bank-year 下, 该模型认定的正面篇数减负面篇数, 未加权原始计数和, 区别于 `{model}_tone{track}` 的篇均语调) 与其他若干统计量。`llm_models_avg_tone_sum{track}` 就是这个"净得分之和"跨三家模型取均值 — 与相邻家族 `llm_models_avg_tone` (篇均语调跨模型均值) 是同一聚合思路在不同分子上的两个投影, 后者衡量"平均一篇报道有多正面/负面", 本家族衡量"该 bank-year 单元里正面篇数减负面篇数的规模, 跨模型求均值后再看"。

聚合发生在 `pipeline/panel/geography.py` 的一段循环里, 对 `['_full', '_ctx', '_ss']` 三轨逐一执行: 对每个轨道, 先收集 `LLM_MODELS` (SSOT 定义在 `encode.py`, 即三家模型短名列表) 各自的 `{s}_tone_sum{track}` 列, 用 `_safe_mean` 取行内 (即该 bank-year 观测) 算术均值。`_safe_mean` 的设计考量是容错: 若某一模型的对应列因为上游未跑完/未落盘而缺失, 不会报错崩溃, 而是仅对实际存在的列取均值; 若三列全缺, 返回全 NaN 的 Series (与观测行数对齐)。这意味着本列在生产环境下的取值域并不天然假设三家模型必须同时在场 — 但在正常生产语料下三家模型应同时落盘, 缺列属异常状态需在日志中排查, 而非常态。

三个模型互为独立评分者, 而非彼此校准或蒸馏的关系: 三家来自不同厂商 (OpenAI 系 / Google 系经 OpenLux / DeepSeek 直连), 独立提示词、独立 API 调用、独立 `temperature=0.0` 确定性采样, 仅共享同一套 prompt 模板 (`v8-2026-05-17`, 冻结锚点, 缓存命中键的一部分) 与同一篇待判定文本。这符合项目铁律「LLM 三家互为稳健性、不分主次」——不存在一个"主模型"由另外两个模型做稳健性检验的从属关系, 三者是并列的、各自独立可用的语调测度, `llm_models_avg_tone_sum` 是把三者揉成一个单一综合指标供主分析使用, 而各模型的单独列 (`{model}_tone_sum{track}`) 仍完整保留供跨模型稳健性核验。

【方法学与计算】
计算链条起点是 stage 21 `tone_llms.py`。该阶段对每篇通过 stage 13 共现硬过滤、且 stage 14 已物化出 `content_full`/`content_ctx`/`content_ss` 三种文本窗口的文章, 分别构造三条独立 prompt (对应三轨), 调用三家 LLM 各自打分。留篇门控是 full-only 口径 (2026-06-29 起生效): 一篇文章是否被计入"一篇有效的银行×金融科技报道"仅取决于 `llm_verified_full == True`; ctx/ss 两轨在此意义上是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 但各轨自身的语调判断、`_tone_sum` 等统计量仍逐轨独立计算, 不借用彼此的分子分母。这一点对理解 `llm_models_avg_tone_sum_ctx`/`_ss` 尤为关键: 它们不是把 full 轨的结果照抄一份, 而是在 (full 留篇的子集上) 用各自轨道的文本窗口重新让三家模型判断一次。

模型层面的原始输出经 `encode.py` 聚合两步: 第一步文章级 → 逐模型逐轨的语调标签折算为数值符号 (正面=+1/中性=0/负面=-1, 或类似映射, 具体折算规则见 `tone_llms.py`/`encode.py` 源码); 第二步文章级 → bank-year 面板级, 在同一 bank-year 单元内对该模型判定为正面的篇数与负面的篇数相减, 得到 `{model}_tone_sum{track}`, 是一个未经篇数归一化的净计数差, 量纲上随该 bank-year 报道量的增大而增大 (与 `{model}_tone{track}` 的篇均口径形成对照, 后者除以有效篇数、量纲是 [-1,1] 区间的强度)。本家族的三家均值 `llm_models_avg_tone_sum{track}` 就是在这个"净计数差"的意义上, 对三家模型的判断取简单算术平均, 单位仍是"篇数差"量纲 (并非归一化到 [-1,1] 的比例), frontmatter 中标注的语调得分单位描述沿用家族整体口径, 但使用者在解读时应留意其分母未被显式归一化, 与报道总量 `n_articles` 强相关, 实证使用中通常需要额外控制或除以篇数。

三轨 (`_full`/`_ctx`/`_ss`) 依 CLAUDE.md「三轨文本架构」铁律各自 just-identified 并排、互为稳健性、不分主次 — 三者严禁混进同一个 over-identified 的 Hansen J 检验框架。full 轨窗口 = 标题 + 全文正文; ctx 轨窗口 = 标题 + 银行实体所在窗口 (`content_ctx`, 由 stage 14 `ctx_materializer` 物化, `prepend_title` 拼接); ss 轨窗口 = 标题 + 银行与金融科技词同句 (或 ±N 句窗, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 共现的句子集合 (`content_ss`)。ss 轨遵循「镜像 ctx」的回退语义: 当某篇文章在 full-only 留篇集合内、但银行与金融科技词并未出现在同一句 (无同句共现) 时, `content_ss` 退化为使用全文正文作为替代文本、`ss_is_fallback` 标记为 True, 该情形与 ctx 轨"实体窗口取不到时回退全文"的处理原则完全对称, 二者共享同一个"回退时使用全文、并显式标记而非静默丢弃"的设计公理, 且降级不影响该行是否被纳入 `n_articles` 分母的判定 (分母口径由 full 轨门控统一决定)。

【文献定位】
本家族体现的是"多家 LLM 独立评分再取跨模型均值"这一集成 (ensemble) 范式在金融文本情感测度中的应用。Ludwig, Mullainathan & Rambachan (2025) 系统提出了将 LLM 输出作为计量经济学测量工具时应满足的应用经济学框架, 强调独立重复评分、提示词冻结与确定性温度设置对结果可复现性的重要性, 本项目 stage 21 的 `temperature=0.0`、prompt 版本冻结 (`v8-2026-05-17`) 与三家跨厂商并列评分设计与该框架的建议一致。de Kok (2025) 在会计研究情境下讨论了如何在生成式 LLM 用作文本分析工具时保证 prompt 稳定、缓存复现与跨模型稳健性, 为本项目"缓存键=prompt_version+temperature"的确定性锚点设计提供了方法学参照。Huang, Wang & Yang (2023) 提出 FinBERT 面向金融文本抽取信息的大语言模型路径, 是本项目 BERT 三模型稳健性轨的直接方法学来源之一, 也印证了金融文本情感测度存在"词典法/BERT 法/生成式 LLM 法"三足鼎立的测量三角, `llm_models_avg_tone_sum` 家族对应其中生成式 LLM 一支的跨模型集成投影。Gilardi, Alizadeh & Kubli (2023) 的实证发现生成式对话模型在文本标注任务上可以超过众包标注员的准确度与一致性, 为本项目选择以三家商用 LLM 替代/补充人工标注与词典规则的整体设计取向提供了外部效度佐证。Lan, Wu, Xu, Feng & Zhang (2025) 针对中文金融文本细粒度情感分析给出了 LLM 方案在中文语境下的实证表现, 与本项目处理中文银行—金融科技报道的应用场景直接相关, 支持了在中文财经文本上采用 LLM 打分而非仅依赖英文训练的词典或分类器的合理性。 在此基础上, 三条前沿文献分别锚定本家族的构念层、架构层与下游使用层。Rønningstad 与 Velldal (2024) 评估了 LLM 对特定目标实体的情感 (entity-level sentiment) 标注质量并与人工标注对比, 与本家族所测「针对目标银行而非篇章整体的实体级语调」这一构念同族, 是该构念下 LLM 标注可行性的同族实证; 但其语料为挪威语与英语通用新闻及评论, 目标实体非银行, 且仅采用单一 GPT 模型、只报告标注一致性, 既无三家投票与置信度概率化, 亦不涉及 bank-year 面板聚合与三轨 (full/ctx/ss) 文本切分。Wang、Wang、Athiwaratkun、Zhang 与 Zou (2024) 实证聚合多个异构 LLM 的输出优于任何单一模型, 为本家族对三家 per-model tone_sum 子测度取跨模型算术均值的架构提供前沿存在性依据; 惟其聚合为分层生成式合成, 与本家族的机械算术平均并非同一机制, 评测亦在英文指令跟随基准而非中文财经文本。Burtch、McFowland、Yang 与 Adomavicius (2026) 由集成成员间的预测差异构造工具变量, 以缓解 ML 生成变量作回归元时的测量误差偏误, 与本家族跨模型离散度的结构同构, 为聚合量的下游使用提供了一条已发表的处理路径; 但其成员为同一训练流程下可重采样的 ML 预测器, 本家族成员则是三家闭源 LLM, 差异来源不可控亦不可重采样, 该 IV 前提未必成立 — 本项目未实施该方案, 三家子测度仍各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。
## VAR: llm_models_avg_tone_sum_ctx

【变体差分】
本列是 `llm_models_avg_tone_sum` 家族在 ctx (实体窗口) 轨道上的实现: 三家 LLM 各自在 `content_ctx` (标题 + 围绕目标银行实体截取的文本窗口, stage 14 物化) 上独立打分, 得到各自的 `{model}_tone_sum_ctx`, 再取三家算术均值。行宇宙受 full-only 留篇门控约束 (`llm_verified_full == True` 的子集), 但语调判断本身是在 ctx 窗口的独立重新评分, 不是从 full 轨结果里直接复制或按比例折算而来。ctx 轨相对 full 轨的差异在于文本输入更聚焦 (排除了与目标银行实体距离较远的段落), 理论上降低了因文章篇幅长、涉及话题多而引入的语调稀释或噪声, 但也可能因窗口截断而丢失影响整体语气判断的上下文信息 (例如开头总括性评价落在窗口之外)。当银行实体窗口无法确定 (回退触发) 时, ctx 轨照全文语义处理并标记 `is_fallback`, 该行仍计入分母, 不因回退而被剔除, 只是失去了窗口聚焦带来的信息增益。作为三轨并排稳健性轨之一, 本列与 `_full`/`_ss` 两列严格互为稳健性、不分主次, 不应在同一 over-identified 设定中把三者混为一组工具变量或联合矩条件; 实证使用中若同时报告三轨回归系数, 应作为并列稳健性表呈现, 而非把三者同时塞进单一模型的解释变量集合造成多重共线或伪over-identification。

本列继承家族层面"净计数差跨模型均值"的单位特性: 分子是该 bank-year 单元内三家模型 (在 ctx 轨判定下) 各自的正面篇数减负面篇数, 未除以有效篇数, 因此与 `n_articles_ctx` (或与其对应的 full-only 门控下的有效篇数) 高度相关, 报道量越大的银行—年份组合, 本列绝对值天然越可能偏离 0。使用者若要在回归中把 ctx 轨与 full/ss 轨的系数直接比较量级, 建议先按各自的有效篇数做归一化, 或改用篇均口径的 `llm_models_avg_tone_ctx` 作为交叉验证; 本列更适合用于捕捉"讨论热度叠加语调倾向"这一复合信号, 而非纯粹的语调强度测度。ctx 轨窗口边界的确定逻辑与 stage 15 (`fintech_intensity`)、stage 16 (`article_policy_alignment`) 共享同一套实体窗口物化产物 (`content_ctx`), 三个下游消费者对同一份物化文本各自计算独立指标, 互不干扰、互不复用彼此的计算结果。

## VAR: llm_models_avg_tone_sum_full

【变体差分】
本列是 `llm_models_avg_tone_sum` 家族在 full (全文) 轨道上的实现, 也是三轨中的门控基准轨: 一篇文章是否计入某 bank-year 单元的有效报道集合 (即 `n_articles` 分母口径), 唯一取决于该文章在 full 轨上的 `llm_verified_full` 判定 (full-only 留篇门控, 2026-06-29 起生效, 两处门控副本 `tone_llms.py::df_filtered` 与 `run_pipeline_function.py::_stage21_skip_is_compatible` 须同步维护)。三家 LLM 在 `content_full` (标题 + 全文正文, stage 14 `prepend_title` 拼接) 上各自独立评分, `{model}_tone_sum_full` 逐模型计算后取三家均值构成本列。full 轨在语义上覆盖信息最完整 (无窗口截断、无同句共现限制), 但也因此更容易受到与目标银行—金融科技主题无关的段落 (例如同一篇报道里穿插的其他新闻要素、免责声明、记者署名等套话) 拖拽语调判断, 这也是本项目并行维护 ctx/ss 两条更聚焦稳健性轨的动机之一。作为三轨之一, 本列同样遵循「各轨 just-identified 并排、互为稳健性、禁混同一 Hansen J」的铁律, 不因其承担留篇门控职能而被视为唯一的"主轨"用于 identification 层面的强排他性假设; 门控职能与主/稳健轨之分是两个独立维度, 不应混淆。

full 轨在三轨中承担了另一层特殊角色: 因为 `n_articles` 分母口径统一由 full 轨的 `llm_verified_full` 决定, 本列 (`llm_models_avg_tone_sum_full`) 的行宇宙与分母是三轨中最"原始"的一个, ctx/ss 两轨虽然行宇宙是本轨的子集, 但各自的语调判断值并不依赖本列的取值, 三者在数值上互相独立、只在样本选择 (谁被算作一篇有效报道) 层面共享同一把门控标尺。对于关心"整体报道语气"这一构念的研究者, full 轨通常是首选测度, 因为它不受实体窗口截断或同句共现筛选的信息损失; 对于关心"聚焦银行本身/聚焦银行—金融科技直接关联" 这一更窄构念的研究者, ctx/ss 两轨反而更贴切。三者数值上可能出现同号但幅度不同、甚至偶发异号 (例如某银行的报道整体基调偏中性略正, 但涉及金融科技的具体段落偏负面) 的情形, 这本身正是三轨设计要捕捉的异质性信号, 不应被视为测量误差。

## VAR: llm_models_avg_tone_sum_ss

【变体差分】
本列是 `llm_models_avg_tone_sum` 家族在 ss (同句共现) 轨道上的实现: 三家 LLM 各自在 `content_ss` (标题 + 银行与金融科技词同句或 ±N 句窗共现的句子集合, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 上独立打分, 三家 `{model}_tone_sum_ss` 取算术均值构成本列。行宇宙同样受 full-only 留篇门控约束 (在 full 轨留篇子集上计算)。ss 轨相对 ctx 轨判定口径更严格: ctx 轨只要求文本落在目标银行实体窗口内即可, ss 轨进一步要求银行与金融科技词在同一句 (或临近句窗) 内共现, 因此 ss 轨捕捉的是"银行与金融科技被直接并置讨论"这一更强的相关性信号, 理论上语调判断的主题聚焦度最高、但覆盖的样本量 (受回退比例影响) 也可能受限。ss 轨的回退语义严格镜像 ctx: 当一篇文章 (已通过 full-only 门控) 不存在银行—金融科技同句共现时, `content_ss` 退化为使用全文正文替代、`ss_is_fallback` 标记为 True, 且该回退与 ctx 轨共享同一份 `n_articles` 分母、不因回退而改变该文章是否计入统计的资格。`FINTECH_AC` (金融科技关键词自动机) 未初始化的极端情形下, `*_is_fallback` 会对该轨全体记录为 True, 实现优雅降级而非报错。ss 轨与 full/ctx 两轨同为互为稳健性并排轨, 禁止混入同一 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. NBER Working Paper No. 33344 [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J. (2024). Mixture-of-Agents Enhances Large Language Model Capabilities. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2406.04692
Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
<!-- rendered-citations:end -->
