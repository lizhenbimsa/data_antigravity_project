---
family_id: F378
columns:
- llm_prob_score_indep_ctx
- llm_prob_score_indep_full
- llm_prob_score_indep_ss
unit: 无量纲连续得分, 取值范围 [-1, +1] (bank-year 均值, 由 logit-to-score 概率分数聚合得到)
formula: 'llm_prob_score_indep{track} = mean(llm_prob_score{track}) over articles where innovation_collab_mode_full == "自主研发" (三家 LLM 多数投票的协同模式维度全文轨判定); 其中 llm_prob_score{track} = compute_prob_score(sentiment_label{track}, confidence{track}) 把三分类情感标签 (正面/中性/负面) 结合三家 LLM 多数投票的置信度映射到 [-1, +1] 连续分 (logit-to-score, config sentiment.yaml::logit_to_score.enabled=true)'
producer: pipeline\panel\encode.py (按 innovation_collab_mode_full 分组聚合, cm_mapping 自主研发→_indep 后缀) ; pipeline\sentiment\tone_llms.py (逐篇 compute_prob_score 生成源列 llm_prob_score{track})
upstream:
- 21_tone_llms.parquet (llm_prob_score_full/_ctx/_ss, innovation_collab_mode_full)
- 15_fintech_intensity.parquet (硬依赖上游)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks
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
- doi: "10.18653/v1/2023.emnlp-main.330"
  type: "journal"
  authors: "Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C."
  year: 2023
  title: "Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback"
  venue: "Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "5433-5442"
- doi: "10.48550/arxiv.2207.05221"
  type: "arxiv"
  authors: "Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J."
  year: 2022
  title: "Language Models (Mostly) Know What They Know"
  venue: "arXiv"
- doi: "10.18653/v1/2025.naacl-long.179"
  type: "journal"
  authors: "Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D."
  year: 2025
  title: "Can Unconfident LLM Annotations Be Used for Confident Conclusions?"
  venue: "Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers)"
  pages_or_artno: "3514-3533"
- doi: "10.48550/arxiv.2407.17866"
  type: "arxiv"
  authors: "Kim, A., Muhn, M., & Nikolaev, V."
  year: 2024
  title: "Financial Statement Analysis with Large Language Models"
  venue: "arXiv"
new_dois: []
---

## CORE

【构念与来源】
llm_prob_score_indep 家族衡量的是"被三家大语言模型判定为自主研发型金融科技创新"这部分银行—金科报道的情感强度均值, 是 stage 21 (`pipeline/sentiment/tone_llms.py`) 情感投票流水线与 stage 40 面板聚合 (`pipeline/panel/encode.py`) 交叉分组的产物, 而非独立测度。它把两条彼此正交的判定链拼接在一起: 第一条链是逐篇的连续情感强度 `llm_prob_score{track}`, 由函数 `compute_prob_score(sentiment_label, confidence)` 把三分类情感标签 (正面/中性/负面) 结合三家 LLM 多数投票的置信度做 logit-to-score 映射, 落在 [-1, +1] 区间 (config `sentiment.yaml::logit_to_score.enabled=true`); 第二条链是逐篇的协同模式分类 `innovation_collab_mode_full`, 由三家 LLM 对"这篇报道所描述的金融科技创新是银行自主研发还是与外部机构协同完成"投票产生, 取值集合为 {自主研发, 外部协同}, 平局按保守 MAP 降级规则默认落入'自主研发' (uniform-prior conservative tie_default)。encode.py 中的 `cm_mapping = [('自主研发', '_indep'), ('外部协同', '_collab')]` 先按 `innovation_collab_mode_full == '自主研发'` 对文章级 DataFrame 做子集切分 (df_cm), 再在该子集内对 bank-year 分组求 `llm_prob_score{track}` 的均值, 得到本家族三个后缀列; 姊妹家族 (后缀 `_collab`) 是外部协同子集上的同一聚合, 二者互为分类互斥的分区均值, 并非同一分布的两端刻度。协同模式维度所刻画的是产业组织文献中一个常见的二元区分——企业创新活动是主要依靠内部资源自建能力, 还是主要依靠外部主体协同完成, 移植到银行—金科语境后, 区分"银行自建科技团队/自有平台"与"银行借助第三方金融科技公司、联合实验室或战略合作"两类创新路径报道 (本项目未就该分类维度本身引入独立于本表所列文献的额外理论出处, 相关的具体来源与效度校核见下文【文献定位】段仅限于本家族 frontmatter 已核验的四篇文献); 情感强度维度的学理依据则是 Tetlock (2007, Journal of Finance) 开创的媒体语调—资产价格传导框架, 以及近年 LLM-as-annotator 文献 (Gilardi, Alizadeh & Kubli 2023, PNAS; de Kok 2025, Management Science) 对大语言模型在文本标注任务上优于关键词词典、且可通过 temperature=0 与逐条缓存做到确定性复现的论证。 就置信度这一环, Tian 等 (2023) 在英文事实型 QA 数据集上比较了两种取得置信度的路径, 实证表明对经 RLHF 微调的模型, 直接以自然语言索要口头概率所得的置信度, 比模型内部 logit 条件概率更为校准; 本家族以 prompt 索取 confidence 字段、再把它当作概率量送入 compute_prob_score 的做法即依据这一结论, 但该文的度量场景是英文事实型 QA 与 2023 年代次的 OpenAI 模型, 未在中文新闻情感或协同模式分类上度量 ECE, 其校准优势能否迁移到 gemini31/deepseekv4 两家非 OpenAI 模型亦未经验证, 本项目也未在自有语料上复测。更早的 Kadavath 等 (2022) 系统研究了语言模型能否自评其答案的正确性, 证明较大模型在格式恰当的多选/判断题上校准良好, 并据此提出先给答案再自评 P(True) 的自评范式, 另研究了无需特定候选答案的 P(IK) 预测, 是"LLM 自评概率携带真实信息、具备一定校准性"这一前提的早期奠基性证据; 但该文并非本家族做法的方法出处 — 原文自评走的是专门的 P(True)/P(IK) 探针与 logit 读数, 与本项目取自 prompt 结构化输出字段的 confidence 不同, 模型代次为 2022 年的内部模型与本项目三家生产模型不可比, 且原文并未提出把剩余概率 (1−confidence) 在非主类间按最大熵均分再作差的映射 — 该映射系研究者选择, 非原文成果。Gligoric、Zrnic、Lee、Candes 与 Jurafsky (2025) 进一步提出 confidence-driven inference: 以 LLM 自报置信度决定哪些样本值得付费人工复标, 并给出统计有效的点估计与置信区间, 实证低置信 LLM 标注在恰当处理下仍可支撑可信结论, 是本家族把逐篇置信度当作可用统计信息而非丢弃这一取向的前沿依据; 迁移边界须诚实写明: 该文的有效推断必须配套人工标注子样本作 ground truth, 本项目无此人工回路, 置信度仅用于打分与越界拒绝标记, 未实施其抽样—推断设计, 且本项目的 confidence 经三家投票的一致/分歧调整后才进入映射, 与原文的单模型自报口径不同。就阶段二把离散判断聚合为可用信号这一环, Kim、Muhn 与 Nikolaev (2024) 向 GPT-4 提供刻意剥离叙事与行业信息的标准化匿名财务报表, 令其判断企业未来盈余的变动方向, 实证其方向性预测准确率超过人类分析师、与窄训练的机器学习模型相当, 且据其预测构建的交易策略取得更高 Sharpe 比率与 alpha, 为"令 LLM 作离散方向性判断、再把该判断聚合为可交易信号"这一范式在金融领域提供了前沿存在性证明; 但其输入是报表数字而非中文新闻叙事, 单位是公司-季度盈余方向而非银行-年语调, 采用单一 GPT-4 无跨厂商投票, 摘要亦未载其对自报置信度的使用, 故不得据以为本家族 (label, confidence) → llm_prob_score 的最大熵均分式映射背书。
【方法学与计算】
本家族的计算是两阶段管道: 阶段一 (stage 21) 逐篇生成两条独立信号, 阶段二 (stage 40 面板导出) 按协同模式分类做条件均值聚合。阶段一中, 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`, 短名 gpt54nano/gemini31/deepseekv4) 对每篇文章的三种取材范围 (全文 full / 银行相关实体窗口 ctx / 银行∧金科同句共现窗口 ss) 分别推理, 情感标签走严格多数决 (`majority_vote_sentiment`), 协同模式标签走分类多数决 (`majority_vote_categorical`, 平局 tie_default='自主研发', conservative=uniform-prior MAP 保守降级, 不产生系统性偏向外部协同的假象)。`compute_prob_score` 把标签+置信度的离散-连续混合信息压缩为单一 [-1, +1] 浮点数: 置信度越高、标签越极端 (正面/负面), 绝对值越接近 1; 置信度低或标签为中性, 越接近 0; NaN 或越界置信度触发 P3_INV 拒绝, 该行该轨记为缺失而非静默清零。阶段二中, `encode.py` 先用 `innovation_collab_mode_full` (仅全文轨判定, 与情感投票所用的三轨各自独立) 对文章级 DataFrame 做布尔子集, 若某银行-年度在该子集内无文章, 对应 `n_articles_indep`=0 且本家族三列该行为 NaN (由 groupby-agg 的天然缺失语义产生, 不强行补零); 若有文章, 则在子集内对三条轨道各自的 `llm_prob_score{track}` 分别取算术均值, 得到 `llm_prob_score_indep_full` / `_ctx` / `_ss` 三列。注意子集切分本身只用全文轨 (`innovation_collab_mode_full`), 而被聚合的分子量 (`llm_prob_score{track}`) 却按轨道各自取值, 这是刻意设计: 协同模式的"是否自主研发"判定采用与留篇门控一致的 full-only 口径 (2026-06-29 用户决策), 保证同一批文章被稳定地分进同一子集, 三轨情感强度再在这一固定子集上互为稳健性对照, 而非用三套不同轨道各自切出三套不同子集再各自算均值 (那样会破坏跨轨可比性)。分母口径上, `n_articles_indep` 是该子集内的文章计数 (`llm_vote_score_full` 的 count), 与家族外的 `n_articles_llm_valid{track}` 分母不是同一集合, 使用时不应混用做比率。

【文献定位】
本家族的方法论谱系上承媒体语调测度的经典传统, 下接 LLM 文本标注方法学的最新进展。Tetlock (2007, Journal of Finance) 首次系统证明媒体语调对股票收益的可预测性, 确立了"逐篇打分—按主体和期间聚合"的基本范式, 本家族的 bank-year 均值聚合正是这一范式在银行-金科语境下的具体化。协同模式分类 ("自主研发 vs. 外部协同") 是本项目在银行-金科报道语境下的操作化构念, 其判定完全交由三家 LLM 多数投票产生, 未额外引入独立于本表所列文献的理论出处佐证该二元划分的构念效度, 使用者应把它理解为一个描述性分组变量而非某一特定理论框架的直接实证检验。方法学层面, de Kok (2025, Management Science) 系统论证了 temperature=0、prompt 版本冻结与逐条缓存等做法是保证生成式大语言模型文本分析结果可复现、可审计的必要条件, 这正是本项目 `_llm_cache.db` 缓存锚点与 Prompt v8 字节级冻结设计所遵循的规范; Gilardi, Alizadeh & Kubli (2023, PNAS) 的对照实验表明经过恰当提示工程的大语言模型在文本标注准确率上可超过众包标注员, 为本家族用 LLM 而非关键词词典判定协同模式与情感强度提供了方法学正当性; Lan, Wu, Xu, Feng & Zhang (2025, Neural Computing and Applications) 针对中文金融文本的细粒度情感分析进一步表明, 面向中文语境的大语言模型情感判定需要专门校准, 这也是本项目采用三家跨厂商模型多数投票 (而非单一模型) 的动机之一, 以降低单一模型语言偏误对协同模式子集内情感均值的系统性影响。
凡涉及三轨 (full/ctx/ss) 的比较: full/ctx/ss 三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一个 over-identified 的 Hansen J 检验; ss 轨在无银行∧金科同句共现时镜像 ctx 的回退语义, 退回全文 body 并置 `ss_is_fallback=True`。本家族的"是否计入自主研发子集"这一分组判据固定用 full-only 口径 (与 stage 21 留篇门控一致), 三条轨道只在子集内的情感强度均值上体现差异, 不应被误读为三套独立的分组样本。

## VAR: llm_prob_score_indep_ctx

【变体差分】
本列是 llm_prob_score_indep 家族的 ctx 轨道成员: 分组判据 (哪些文章属于"自主研发"子集) 仍固定用全文轨 `innovation_collab_mode_full`, 但被聚合求均值的分子量取自 ctx 轨道的逐篇情感强度 `llm_prob_score_ctx`。ctx 轨的文章级取材范围是"标题 + 银行相关实体窗口" (stage 14 `ctx_materializer` 物化的 `content_ctx`, prepend_title 拼接), 而非全文正文; 当某篇文章不存在可识别的实体窗口 (即无法围绕目标银行截出有意义的上下文片段) 时, `content_ctx` 回退为全文 body, 并由 `ctx_is_fallback=True` 标记该回退状态, 三家 LLM 仍照常对这段回退文本推理并产生 `llm_prob_score_ctx`。因此本列与 canonical `_full` 列的差异集中在两点: 其一, 情感强度的输入文本范围更窄 (聚焦银行实体附近语境, 而非通篇报道), 理论上更贴近"就事论事"的局部语气, 但也可能因窗口截断丢失文章后段的转折或总结性表述; 其二, 由于分组判据固定用 full 轨, 本列与 `_full`/`_ss` 两列共享完全相同的行样本 (同一批银行-年度、同一批"自主研发"子集文章), 三者的差异纯粹来自情感强度输入文本范围不同, 而非样本构成不同, 这使得三轨之间的比较是严格意义上的"同题材、不同取景框"对照, 适合直接拿来做互为稳健性的横向比较, 而不需要额外做样本可比性的辩护。按项目铁律, 本列与 `_full`/`_ss` 两条姊妹轨各自 just-identified 并排、互为稳健性、不分主次, 不应混入同一个 over-identified 的 Hansen J 过度识别检验中联合估计; 若某银行-年度在 ctx 轨下的 `ctx_is_fallback` 比例过高, 应结合 `frac_ctx_fallback` 一类诊断列解读本列数值的稳健性, 而不是孤立地看绝对水平。

## VAR: llm_prob_score_indep_full

【变体差分】
本列是 llm_prob_score_indep 家族的 canonical 全文轨成员, 也是分组判据本身所依赖的轨道: 分组子集 (自主研发 vs. 外部协同) 与本列的分子量 (`llm_prob_score_full`) 都来自同一条全文轨, 二者口径完全一致, 不存在轨道错配问题, 因此本列是三者中语义最"干净"、也是理解本家族构念的起点。全文轨的取材范围是文章标题加完整正文 (`内容` 列原样传入, prepend 标题), 三家 LLM 在这一最完整的信息集合上做协同模式与情感强度的联合判定; 更重要的是, 留篇门控 (即判定"这是不是一篇真正在讲银行-金科关系的报道") 在 2026-06-29 之后收紧为 full-only 口径 (`llm_verified_full == True`), 也就是说进入面板聚合的文章样本本身是由全文轨的验证结果筛出的, ctx/ss 两条轨道被相应降级为"conditional on full"的测度/稳健性轨, 行样本是 full 轨留篇集合的子集而非独立宇宙。这一设计意味着本列 (`_full`) 在三轨中承担着"锚定样本口径"的角色: `n_articles_indep` (本家族聚合所用的分母) 由 `innovation_collab_mode_full` 判定, 与留篇门控的判定基准 (`llm_verified_full`) 属于同一条全文轨链路, 二者不会出现"某篇文章被留篇门控保留、却因协同模式判据用了另一条轨道而被错误分进/分出子集"的口径漂移。使用者若只关注单一测度而非三轨稳健性对照, `_full` 列是默认应引用的主列; ctx/ss 两列则应作为稳健性佐证并列报告, 遵循互为稳健性、不分主次、禁混同一 Hansen J 的铁律。

## VAR: llm_prob_score_indep_ss

【变体差分】
本列是 llm_prob_score_indep 家族的 ss (同句共现) 轨道成员: 分组判据同样固定用全文轨 `innovation_collab_mode_full`, 但被聚合的分子量取自 ss 轨道的逐篇情感强度 `llm_prob_score_ss`。ss 轨的取材范围是"标题 + 目标银行与金融科技词汇在同一句子中共同出现的片段" (`content_ss`, stage 14 物化, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1, 与 stage 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同配置键、不可混用), 是三轨中取材范围最窄、判定口径最严格的一支。当一篇文章内不存在银行与金融科技词汇的同句共现时, `content_ss` 回退为全文 body, 并由 `ss_is_fallback=True` 标记 (回退语义严格镜像 ctx 轨的回退设计, 共享 `n_articles` 分母口径), 三家 LLM 仍对回退文本推理产生 `llm_prob_score_ss`; 若 `FINTECH_AC` 词典匹配器不可用 (`FINTECH_AC=None`), 则该轨全体文章的 `*_is_fallback` 一律置 True, 属优雅降级而非报错。ss 轨的取材范围收窄到"同句共现片段"意味着本列反映的是三轨中最贴近"就句论句"的局部语气, 对上下文转折、条件从句等跨句语义结构最不敏感, 因此在协同模式子集内, 本列与 `_full`/`_ctx` 两列之间的数值差异幅度理论上应大于 `_ctx` 与 `_full` 之间的差异幅度 (取材范围收缩幅度更大)。与另两轨相同, 本列与 `_full`/`_ctx` 各自 just-identified 并排、互为稳健性、不分主次, 不应混入同一个 over-identified Hansen J 检验; 解读本列数值时应结合该银行-年度在 ss 轨下的回退比例诊断列, 回退比例过高说明本列在该 cell 上实质上退化为全文轨的重复测量, 稳健性佐证力度相应减弱。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D. (2025). Can Unconfident LLM Annotations Be Used for Confident Conclusions?. Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 3514-3533. https://doi.org/10.18653/v1/2025.naacl-long.179
Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
<!-- rendered-citations:end -->
