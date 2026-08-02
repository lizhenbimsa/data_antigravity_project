---
family_id: F375
columns:
- llm_prob_score_collab_ctx
- llm_prob_score_collab_full
- llm_prob_score_collab_ss
unit: 无量纲连续分, 值域 [0, 1]
formula: 'avg_collab_prob_score{track} = mean_over_models( compute_prob_score_binary(innovation_collab_mode_label, confidence) ), 三 LLM (gpt54nano/gemini31/deepseekv4) 逐模型 P2_BIN/P3_BIN 概率分求算术平均 (stage 21 文章级, 分母域 = 该轨 verified 有效票); 面板列 = encode.py 对该文章级列做 bank-year 跨文章 mean/std 聚合'
producer: pipeline\sentiment\tone_llms.py (跨模型均值, 文章级) ; pipeline\panel\encode.py (跨文章聚合, bank-year)
upstream:
- 15_fintech_intensity.parquet
- 21_tone_llms.parquet
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: '41'
  issue: '4'
  pages_or_artno: 793-815
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: 'Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms'
  venue: Strategic Management Journal
  vol: '27'
  issue: '2'
  pages_or_artno: 131-150
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: 'The use of LLMs to annotate data in management research: Foundational guidelines and warnings'
  venue: Strategic Management Journal
  vol: '47'
  issue: '3'
  pages_or_artno: 699-725
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: 'Federal Reserve Board, FEDS Working Paper No. 2026-020'
- doi: "10.48550/arxiv.2306.13063"
  type: "arxiv"
  authors: "Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B."
  year: 2023
  title: "Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs"
  venue: "arXiv"
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
- doi: "10.18653/v1/2024.emnlp-main.173"
  type: "journal"
  authors: "Zhang, M., Huang, M., Shi, R., Guo, L., Peng, C., Yan, P., Zhou, Y., & Qiu, X."
  year: 2024
  title: "Calibrating the Confidence of Large Language Models by Eliciting Fidelity"
  venue: "Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing"
  pages_or_artno: "2959-2979"
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
本家族衡量的是每篇银行-金科报道中"合作模式"这一创新维度的 LLM 概率化打分, 底层构念承袭 Chesbrough (2003) 开放式创新框架与 Laursen & Salter (2006, *Strategic Management Journal*) 对企业创新开放度的经典二分刻画: 一端是企业依靠自身研发能力独立完成的"自主研发", 另一端是通过对外联盟、股权投资、并购或技术许可等方式获取外部能力的"对外合作"。项目在 stage 21 (`pipeline/sentiment/tone_llms.py`) 让三个独立 LLM 家族 (`gpt-5.4-nano`/gpt54nano、`gemini-3.1-flash-lite`/gemini31, 两家走 OpenLux 网关; `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com) 各自阅读同一篇报道, 对报道所描述的银行-金科关系给出 `innovation_collab_mode` 分类标签 (自主研发/对外合作二元判据, 平局 tie_default='自主研发', 保守降级 uniform-prior MAP), 并同时给出一个置信度 (confidence)。`compute_prob_score_binary` 函数 (P2_BIN/P3_BIN 分支) 把这个离散标签与置信度联合映射为 [0,1] 区间内的连续概率分: 标签越倾向"对外合作"且置信度越高, 分数越接近 1; 标签倾向"自主研发"且置信度越高, 分数越接近 0; 置信度低则分数向 0.5 收缩, 体现测量不确定性的合理衰减, 是 `compute_prob_score_binary` 函数内置的保守化设计, 在项目其他信噪比诊断段落中亦有复用。stage 21 (`pipeline/sentiment/tone_llms.py`) 在逐篇层面先为每个模型算出 `{short}_prob_score_collab{track}` 存档值, 再在同一函数内按该轨该篇文章实际给出有效判定的模型子集求算术平均, 产出文章级列 `avg_collab_prob_score{track}` (即本家族列 `llm_prob_score_collab{track}` 的内部命名); `pipeline/panel/encode.py` 只是在这一已经是"跨模型均值"的文章级列基础上, 做 bank-year 维度的跨文章 pandas `mean`/`std` 聚合 (生成 `avg_collab_prob_score{track}` 与 `avg_collab_prob_score_std{track}` 两个面板列), 并不重复或改变跨模型求均值这一步。三模型 ensemble 而非单模型输出, 目的是降低单一厂商的系统性偏误、提升标注稳健性, 这一思路与 de Kok (2025, *Management Science*) 对生成式 LLM 用于会计/金融文本分析时需交叉验证与温度冻结的方法学建议一致; 本项目在生产环境统一采用 temperature=0.0 的确定性推理并配合 prompt v8 字节级冻结与 SQLite 缓存 (`_llm_cache.db`), 以保证同一篇文章多次重跑得到完全一致的概率分。

【方法学与计算】
`compute_prob_score_binary` 的输入域限定在该模型该轨该篇文章的有效判定范围内: 若某模型在某轨对某篇文章的 `{short}_verified{track}` 判定为不成立 (即该模型认为这篇文章根本不构成一次有效的"银行-金科报道"), 则该模型在该轨对该篇文章不贡献 `{short}_prob_score_collab{track}` 有效值, 记为 <NA>; stage 21 (`tone_llms.py`) 内的跨模型求均值只对该轨该篇文章实际给出有效判定的模型子集求算术平均, 分母是该轨的有效票数而非固定为 3, 由此产出文章级 `avg_collab_prob_score{track}`。`encode.py` 只在这一文章级列之上做 bank-year 维度的跨文章聚合 (`mean`/`std`), 不重复跨模型均值这一步, 也不改变分母口径。这意味着 `llm_prob_score_collab{track}` 的有效性域与该轨的 `n_valid_votes{track}`/verified 状态直接挂钩, 而非独立于情感/精筛判定之外的孤立指标。需要特别强调的是, 留篇门控 (是否把一篇文章计入"一篇有效银行-金科报道"从而进入后续面板聚合) 采用 full-only 口径 (2026-06-29 用户决策): 只有 `llm_verified_full == True` 才决定该篇文章是否被保留, ctx/ss 两轨的 verified 判定退化为 conditional-on-full 的测度/稳健性轨, 不参与留篇本身的决定。因此 `llm_prob_score_collab_ctx`/`_ss` 的样本行宇宙是 full 轨留篇集合的子集, 而非各轨独立的样本框; 三轨在留篇集合确定之后各自按自己的取材范围重新计算 collab 概率分, 互为稳健性、不分主次, 严禁把三轨系数并入同一个 over-identified 的 Hansen J 检验框架 (三轨应各自 just-identified 并排呈现)。

【文献定位】
本家族的方法论定位介于两条文献之间: 一是创新管理领域关于"开放式创新"程度测量的经典构念传统 (Chesbrough, 2003; Laursen & Salter, 2006, *Strategic Management Journal*; Zhang, Ma, Liang & Garrett, 2024, *Journal of Product Innovation Management* 对 20 年开放式创新前因后果的元分析确认了"自主研发 vs. 对外合作"这一二分维度在实证文献中的持续生命力与稳健性), 二是近年方兴未艾的"用大语言模型做文本标注替代人工编码"的方法学文献 (de Kok, 2025, *Management Science*; Carlson & Burbano, 2026, *Strategic Management Journal*, 对管理学研究中使用 LLM 标注数据给出了基础性指引与风险警示; Hansen, 2026, FEDS Working Paper, 讨论无金标准场景下如何通过多模型一致性设计验证 LLM 标注质量)。本项目把这两条线索结合起来: 用三家独立 LLM 复现传统人工编码员对"合作模式"这一定性维度的判断, 再用连续概率分 (而非硬性 0/1 标签) 保留判断的强度信息, 便于后续面板回归以连续变量形式而非离散哑变量形式纳入这一构念, 减少因人为设定切分阈值带来的信息损失。 这一以置信度驱动的连续化设计, 其上游依据可追溯至 LLM 置信度诱导 (confidence elicitation) 的方法学谱系。Xiong 等 (2023) 在黑箱访问条件下系统评测了直接向 LLM 索取自报置信度的基准协议, 并记录了模型普遍过度自信, 是本家族 confidence 字段取数方式的方法原点; 该文评测对象为当时的 GPT/LLaMA 系模型与英文常识、算术推理任务, 不含本项目的 gemini31/deepseekv4, 亦无面板聚合环节。Tian 等 (2023) 进一步证明, 对经 RLHF 微调的模型, 以自然语言索要的口头概率比模型内部 logit 条件概率更为校准, 这正是本项目在商用 RLHF 类模型上以 prompt 结构化字段取 confidence、再送入 `compute_prob_score_binary` 的实证依据; 但该文在英文事实型 QA 数据集上度量 ECE, 本项目未在中文银行金科新闻语料上复测 ECE, 也未验证该校准优势能否迁移至两家非 OpenAI 模型。更早的 Kadavath 等 (2022) 系统检验语言模型能否自评答案正确性, 证明较大模型在格式恰当的多选/判断题上校准良好, 为"LLM 自评概率携带真实信息、具备一定校准性"这一前提提供了奠基性证据; 须澄清其边界: 该文自评走的是专门的 P(True)/P(IK) 探针与 logit 读数而非结构化输出字段, 模型代次与本项目三家生产模型不可比, 且原文并未提出把余量 (1−confidence) 在非主类间按最大熵均分的映射 — 该映射系研究者选择, 非原文成果。Zhang 等 (2024) 把 LLM 置信度分解为对问题的不确定性与对自身答案的保真度, 提出 UF Calibration 并在 6 个 RLHF-LM × 4 个 MCQA 数据集上验证, 表明置信度原则上可被进一步分解与校准; 该方法需要选项集/参考答案来定义保真度, 本家族的分类任务缺少此结构, 故未实施该校准算子, 现口径仍为原始自报值经映射后取跨模型均值, 属已知局限而非已排除的风险。Gligoric、Zrnic、Lee、Candes 与 Jurafsky (2025) 提出 confidence-driven inference, 以 LLM 自报置信度决定哪些样本值得付费人工复标, 并给出统计有效的点估计与置信区间, 证明低置信标注在恰当处理下仍可支撑可信结论, 为本家族"保留而非丢弃低置信信息、令分数向 0.5 收缩"的保守化处理提供前沿依据; 但该文的有效推断必须配套人工标注子样本作为 ground truth, 本项目无人工标注回路, 未实施其抽样-推断设计, 且此处 confidence 经三家投票的一致/分歧调整, 与原文单模型口径不同。金融领域一侧, Kim、Muhn 与 Nikolaev (2024) 向 GPT-4 提供刻意剥离叙事与行业信息的标准化匿名财务报表、令其判断企业未来盈余的变动方向, 实证其方向性预测准确率超过人类分析师、与窄训练的机器学习模型相当, 并可据以构建更高 Sharpe 比率的策略, 是"令 LLM 作离散判断、再把该判断聚合为可用经济量"这一范式在金融研究中的存在性证明; 其输入为报表数字而非中文新闻叙事, 单位为公司-季度盈余方向而非银行-年创新维度, 采用单一模型无跨厂商投票, 摘要亦未载其对自报置信度的使用, 因此不构成对本家族 logit-to-score 映射的背书。
## VAR: llm_prob_score_collab_ctx

【变体差分】
本列是"实体窗口轨" (ctx) 版本: 三 LLM 阅读的原始文本是 stage 14 物化的 `content_ctx` (标题 + 目标银行实体附近窗口的正文片段, `prepend_title` 拼接, 而非全文), 该轨的合作模式概率分只依据这一截断窗口内可见的信息作出判断。样本行宇宙受 full-only 留篇门控约束, 即仅覆盖 `llm_verified_full == True` 的文章子集; 若该文章在 ctx 轨下 `gpt54nano_verified_ctx`/`gemini31_verified_ctx`/`deepseekv4_verified_ctx` 均判定不成立 (即三家模型看窗口文本都认为构不成有效报道), 则该篇文章在 ctx 轨的贡献模型数为 0, `llm_prob_score_collab_ctx` 记为缺失。ctx 轨与 full/ss 轨互为稳健性、并排呈现, 不作为 full 轨的替代或补充加总对象; 因窗口截断可能遗漏叙述合作细节的上下文句子 (例如合作对象、合作深度等信息可能出现在窗口之外), ctx 轨相对 full 轨在合作模式这一维度上存在信息损失的系统性风险, 解读时应结合 full 轨互证而非单独采信。

从计算链路上看, ctx 轨与 full 轨共用同一套 `compute_prob_score_binary` 概率映射函数与同一批三家 LLM 模型配置, 唯一差异变量是喂给模型的输入文本范围; 这保证了跨轨对比时差异可以干净地归因于"取材范围"这一个因子, 而不会掺入模型选择或打分函数差异带来的混淆。stage 21 在跨模型求均值时同样遵循逐模型独立降级原则: 若 `gpt54nano_prob_score_collab_ctx` 缺失但另外两家模型在 ctx 轨给出有效值, 仍以现存有效值的均值填入文章级 `avg_collab_prob_score_ctx`, 不因单一模型缺席而整列清空; `encode.py` 随后对这一文章级列做的 bank-year 跨文章聚合不改变这一降级逻辑。此外, ctx 轨的 verified 判定与 collab 概率打分共享同一次模型调用产出 (18 元组聚合的一部分), 缓存键锁定 prompt v8 + `iter_article_track_prompts` 单一事实源, 因此该列在 `_llm_cache.db` 全命中条件下可离线 $0 字节级复现, 无需重新调用付费 API。

## VAR: llm_prob_score_collab_full

【变体差分】
本列是"全文轨" (full) 版本, 也是三轨中唯一承担留篇门控职能的轨: 三 LLM 阅读的是 stage 00 预处理后的完整正文 (标题 + 全文 `内容` 字段拼接), 在此基础上先做 `verified_full` 三角投票 (判定这篇文章是否构成一次有效的银行-金科报道), 只有该判定为 True 的文章才进入面板聚合的留篇集合 (full-only 口径, 2026-06-29 用户决策)。`llm_prob_score_collab_full` 即是该留篇集合内, 三家模型基于全文视角对合作模式给出的概率分之逐模型均值; 由于是全文视角, 该列在信息完整度上通常最优, 是本家族在多数下游分析 (含 P5 collab paper 的处理变量口径参照) 中的主要参照轨, 但按照项目"三轨互为稳健性、不分主次"的铁律, full 轨在统计设定上仍与 ctx/ss 轨并列呈现, 不单独赋予结构性优先权重, 三轨系数各自 just-identified、不得混入同一 over-identified Hansen J 框架。

full 轨承担留篇门控职能这一点, 决定了它在样本行宇宙上具有特殊地位: `llm_verified_full` 的三角投票结果不仅决定该篇文章是否进入 `21_tone_llms.parquet` 的留篇输出, 也间接决定了 ctx/ss 两轨的可观测样本范围 (二者只在 full 留篇集合内取值)。但这种"决定样本框"的角色与"测度构念优先"的角色是两回事: full 轨对合作模式的概率打分本身, 与 ctx/ss 轨的打分一样, 都只是三家 LLM 阅读某一取材范围文本后的独立判断, 三者在方法论意义上地位对等, 差异只在于可见文本的完整度。全文视角固然信息量最大, 但也可能引入与目标银行-金科关系无关的干扰段落 (例如同一篇报道中夹杂其他新闻事件), 这是全文轨潜在的噪声来源, 恰是 ctx/ss 两轨聚焦式取材的价值所在, 三轨并列呈现正是为了让读者同时观察"信息完整度"与"聚焦精度"两个方向的权衡, 而非简单地把 full 轨当作唯一正确答案。

## VAR: llm_prob_score_collab_ss

【变体差分】
本列是"同句窗口轨" (ss, sentence-same) 版本: 三 LLM 阅读的原始文本是 stage 14 物化的 `content_ss` (标题 + 目标银行与金科关键词在同一句或 ±N 句半径窗口内共现的片段, `sentence_radius` 配置见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1)。若一篇文章不存在银行∧金科词同句共现, `content_ss` 按镜像 ctx 轨的回退语义退化为全文 body, 并置位 `ss_is_fallback=True`, 与 ctx 轨共享 `n_articles` 分母口径; 若 `FINTECH_AC=None` (金科 AC 自动机未加载), 则 `*_is_fallback` 全体置 True, 该轨优雅降级为等同 full 轨的取材范围。样本行宇宙同样受 full-only 留篇门控约束。ss 轨是三轨中取材范围最窄、判据最严格的一轨 (要求银行与金科表述在同一叙述单元内紧邻出现), 因而对"合作模式"这类需要跨句叙述合作细节 (如合作对象名称、合作形式) 的判断天然更容易遗漏信息, 概率分向 0.5 (不确定) 收缩的倾向可能强于 full/ctx 两轨; 该列与 full/ctx 两轨互为稳健性并排呈现, 不作加总或替代处理, 亦不得混入同一 over-identified Hansen J 检验。

需注意 ss 轨的回退语义并非"数据缺失"而是有意设计的优雅降级: 当某篇文章确实不存在银行∧金科同句共现时, `content_ss` 自动退化为等同全文的取材范围并置 `ss_is_fallback=True`, 此时该篇文章在 ss 轨下的合作模式概率打分实质上是基于全文文本作出的判断, 与 full 轨的输入高度重合 (但仍由独立的模型调用产生, 缓存键不同, 不与 full 轨列共享数值)。这意味着 `llm_prob_score_collab_ss` 内部实际上混合了两类样本: 一类是真正基于"同句紧邻共现"这一严格判据取材的窄窗口打分, 另一类是回退到全文取材的打分, 二者共享 `n_articles` 分母口径但取材范围截然不同。下游若需要区分这两类样本, 应结合 `ss_is_fallback` 指示列做子样本切分, 而不宜把 `llm_prob_score_collab_ss` 当作单一同质构念直接使用。这一回退设计镜像了 ctx 轨的对称回退语义, 目的是避免因取材窗口过窄导致大量文章无法产出有效判断, 从而在样本覆盖率与判据严格性之间取得平衡。
<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board, FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2306.13063
Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
Zhang, M., Huang, M., Shi, R., Guo, L., Peng, C., Yan, P., Zhou, Y., & Qiu, X. (2024). Calibrating the Confidence of Large Language Models by Eliciting Fidelity. Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, 2959-2979. https://doi.org/10.18653/v1/2024.emnlp-main.173
Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D. (2025). Can Unconfident LLM Annotations Be Used for Confident Conclusions? Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 3514-3533. https://doi.org/10.18653/v1/2025.naacl-long.179
Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
<!-- rendered-citations:end -->
