---
family_id: F376
columns:
- llm_prob_score_hw_sum_ctx
- llm_prob_score_hw_sum_full
- llm_prob_score_hw_sum_ss
unit: 无量纲加权得分和 (银行-年层面, 逐篇 llm_prob_score 乘以羊群/时效衰减权重后求和)
formula: 'llm_prob_score_hw_sum_{track} = Σ_i (llm_prob_score_{track,i} × herd_weight_{track,i}), i 遍历该银行-年下 llm_verified_full 留篇门控通过的报道; herd_weight 来自 stage 24 herd_decay_processor, 三轨独立权重存在时逐轨对齐 (herd_weight_full/ctx/ss), 否则回退单轨 legacy herd_weight 同源复用于三轨 (runner.py fake 多轨语义)'
producer: pipeline\panel\encode.py (聚合注册, L1195) + pipeline\panel\runner.py (逐篇加权列 _build_llm_valid_masked_weights/weighted_cols 物化, L844-901)
upstream:
- 21_tone_llms.py
- 24_herd_decay_processor.py
- 40_panel_export_main.py
citations:
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: ["Gilardi, F.", "Alizadeh, M.", "Kubli, M."]
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
- doi: "10.1016/j.frl.2024.105227"
  type: journal
  authors: ["Kirtac, K.", "Germano, G."]
  year: 2024
  title: "Sentiment trading with large language models"
  venue: "Finance Research Letters"
  vol: "62"
  issue: ""
  pages_or_artno: "105227"
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: ["Tetlock, P. C."]
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: ["de Kok, T."]
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
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
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (llm_prob_score_hw_sum_full / _ctx / _ss) 是银行-年面板层面的羊群加权 (herd-weighted) 逐篇 LLM 概率语调得分之和, 属 Logit-to-Score 概率映射情感体系下的加权稳健性辅助测度, 而非独立构念。其上游是文章级列 llm_prob_score{track}, 由 stage 21 tone_llms 对每篇报道调用 LLM 输出正面/负面概率 P(正面)、P(负面), 定义 llm_prob_score = P(正面) − P(负面) ∈ [−1, +1] (呼应 Gilardi et al., 2023 关于零样本 LLM 标注可比肩甚至超越人工/众包标注的发现, 以及 Kirtac & Germano, 2024 用 LLM 输出的类别概率构造连续情感交易信号的做法, 相对硬标签投票能保留 LLM 内部置信度信息, 是 llm_vote_tone 之外的第二条情感量化路径, 二者互为稳健性并排, 不分主次)。本家族对该逐篇得分乘以 herd_weight 后在银行-年层面求和, herd_weight 是 stage 24 herd_decay_processor 产出的羊群/时效衰减权重, 刻画同一时间窗口内报道数量的"扎堆"程度与信息衰减速度: 短期内同题材报道越密集, 单篇报道的边际信息增量按衰减函数递减, herd_weight 相应调低该篇在聚合中的分量, 以抑制媒体羊群效应 (herding) 对语调测度的机械放大。

【方法学与计算】
计算分两步。第一步在 runner.py 逐篇层面完成: 对每篇文章的三轨 llm_prob_score{track} 乘以对应的 herd_weight{track} 得到逐篇加权列 llm_prob_score_hw{track} (若源数据仅有单轨 legacy herd_weight, 则三轨共用同一权重列, 即"伪多轨"语义, 三轨的差异此时完全来自 llm_prob_score 本身而非权重)。第二步在 encode.py 聚合层面完成: 按银行-年分组对 llm_prob_score_hw{track} 求 sum, 得到本家族三列。该和值本身是聚合中间量, 不直接作为可比语调水平使用; 面板下游会将其除以配套的加权分母 sum_wd_hw_prob{track} (银行-年内该轨 llm_prob_score 非缺失篇的 herd_weight 之和, 由 encode-01 valid-mask 机制预计算) 得到归一化的加权均值 llm_vote_tone_hw_prob{track}, 该归一化列才是研究者常用的可比语调指标; 本家族三列作为分子留在面板中供审计、重算权重口径或替换分母定义时复用, 也便于研究者手动核验聚合链路。留篇门控采用 full-only 口径 (2026-06-29 起): 一篇报道是否计入"该银行-年的一篇有效银行金科报道", 只看 llm_verified_full == True 决定的行宇宙; ctx/ss 轨在同一行宇宙上各自计算 llm_prob_score_ctx/_ss 及对应 herd_weight, 属 conditional-on-full 的测度稳健性轨, 不单独扩大或缩小样本范围。若源列缺失 (例如未跑三轨独立权重的旧 parquet), aggregate_panel 的 valid_agg 机制会自动跳过对应聚合项, 不引发 KeyError, 该银行-年对应列以 NaN 优雅降级而非报错崩溃。

【文献定位】
llm_prob_score 的连续概率映射思路直接呼应 Gilardi et al. (2023, PNAS) 关于零样本 LLM 标注可比肩甚至超越人工标注/众包标注的发现, 以及 Kirtac & Germano (2024, Finance Research Letters) 用 LLM 概率输出构造连续情感交易信号的方法学先例 — 二者共同支撑"用 LLM 输出的类别概率而非硬标签构造连续语调分数"这一方法论选择。de Kok (2025, Management Science) 则为本家族方法学底座中的 temperature=0、prompt 版本冻结、结果可复现缓存范式提供了会计与金融文本分析场景下使用生成式 LLM 的操作规范依据, 与本项目 stage 21 的确定性锚点设计 (v8-2026-05-17 prompt 冻结 + `_llm_cache.db` 缓存) 一致。herd_weight 加权本身处理的是媒体报道扎堆导致的信息重复问题, 在方法论上呼应 Tetlock (2007) 关于媒体语调需要经过合理加总/去噪才能转化为可信投资者情绪信号的经典设定 — 若不对同题材扎堆报道做权重调整, 单一事件驱动的密集报道簇会机械抬高或压低银行-年语调均值, 掩盖真实的语调信息含量, 这正是本家族所服务的加权聚合环节要防范的问题。三轨 full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁将三轨或权重梯度混入同一 over-identified 的 Hansen J 检验; ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, content_ss 退化为全文正文 (即与 full 同源文本), 且 ss_is_fallback 标记为 True, 该行为在 herd_weight 与 llm_prob_score 两条上游链路上是一致的。 就本家族分子所乘的逐篇 llm_prob_score 赖以成立的置信度前提而言, 尚可上溯两条方法学锚点。Tian 等 (2023) 证明, 对经 RLHF 微调的模型, 直接用自然语言索要所得的口头概率比模型内部 logit 条件概率更为校准, 这为该源列以 prompt 结构化字段取置信度、再作 logit-to-score 映射提供了实证依据; 该文在英文事实型 QA 数据集上度量 ECE, 模型为 2023 年 GPT-3.5/GPT-4 代次, 本项目既未在中文银行金科新闻语料上复测 ECE, 也未验证该校准优势能否迁移至 deepseekv4/gemini31 两家非 OpenAI 模型, 原文更不涉及 herd 加权求和与银行-年面板聚合。Kadavath 等 (2022) 则更早证明较大模型在格式恰当的多选/判断题上自评校准良好, 并提出让模型先作答再自评 P(True) 的范式, 为"LLM 自评概率携带真实信息"这一前提提供奠基性支持; 但该文自评经由专门的 P(True)/P(IK) 探针与 logit 读数而非结构化输出字段, 模型代次与本项目三家生产模型不可比, 且原文只论证到自评概率具备校准性为止, 并未提出把余量 (1−confidence) 在非主类间均分再作差的映射 — 该映射及其后的 herd_weight 加权求和均系本项目的研究者选择, 非原文成果。
## VAR: llm_prob_score_hw_sum_ctx

【变体差分】
本列是 ctx 轨的银行-年羊群加权概率语调得分和: Σ_i (llm_prob_score_ctx,i × herd_weight_ctx,i), 其中 llm_prob_score_ctx 来自 stage 21 对 content_ctx (标题 + 实体窗口文本) 而非全文的 LLM 概率打分, herd_weight_ctx 是 stage 24 在 ctx 轨独立算出的羊群衰减权重 (若源数据只有单轨 legacy herd_weight, 则退化为与 full/ss 轨共用同一权重列, 差异仅来自 llm_prob_score_ctx 本身)。行宇宙遵循 full-only 留篇门控: 是否计入某银行-年由 llm_verified_full 决定, ctx 轨在该行宇宙子集上计算, 属 conditional-on-full 的测度稳健性轨而非独立扩样。ctx 文本窗口聚焦于目标银行/金科实体附近的语境片段, 相比 full 轨的整篇正文更贴近"报道对该实体本身的语调", 但也更依赖实体窗口截取算法的准确性; 当上游未产出 herd_weight_ctx (数据未跑三轨独立权重版本) 时, 本列由 valid_agg 自动跳过对应银行-年聚合项, 以 NaN 呈现而非报错。本列与 llm_prob_score_hw_sum_full / _ss 是三轨并排稳健性关系, 不构成主辅或替代, 差异来源仅限于输入文本窗口与 (若存在) 权重轨道本身, 计算公式与聚合逻辑完全一致。使用本列时应清楚意识到它是未归一化的加权和而非可比语调水平, 直接跨银行-年比较时须先除以对应的加权分母 sum_wd_hw_prob_ctx 得到归一化均值, 否则报道篇数越多的银行-年数值会机械偏大, 掩盖真实语调差异。

## VAR: llm_prob_score_hw_sum_full

【变体差分】
本列是家族的 full 轨版本, 也是 full-only 留篇门控所锚定的行宇宙来源轨: Σ_i (llm_prob_score_full,i × herd_weight_full,i), 其中 llm_prob_score_full 来自 stage 21 对 content_full (标题 + 完整正文, prepend_title 拼接) 的 LLM 概率打分, herd_weight_full 是 stage 24 在 full 轨算出的羊群衰减权重。full 轨的特殊地位在于: 一篇报道是否被判定为"该银行-年的一篇有效银行金科报道"仅由 llm_verified_full == True 决定 (2026-06-29 起的门控切换), 这意味着本列所加总的样本行宇宙就是 ctx/ss 两轨行宇宙的来源, ctx/ss 轨的样本永远是 full 轨行宇宙的子集而非独立扩样。相应地, 本列若使用单轨 legacy herd_weight (即历史数据未拆分三轨独立权重前的兼容路径), 与 ctx/ss 两列共用同一权重来源, 此时三列的差异完全体现在 llm_prob_score 本身而非权重轨道。full 轨因覆盖整篇正文, 通常样本量与信息密度最高, 是研究者构造 llm_vote_tone_hw_prob_full 归一化指标 (本列除以 sum_wd_hw_prob_full) 时最常引用的分子来源, 但方法论地位上仍与 ctx/ss 并排, 不构成"主轨凌驾"稳健轨的关系, 三轨均须各自 just-identified 呈现, 不得混入同一 over-identified 设定。研究者若需比较三轨的加权语调水平差异, 应统一先各自除以对应轨道的加权分母得到归一化均值, 再做跨轨比较或稳健性并排展示, 直接比较未归一化的和值会因样本篇数与权重规模不同而失去可比性。

## VAR: llm_prob_score_hw_sum_ss

【变体差分】
本列是 ss (同句共现) 轨的银行-年羊群加权概率语调得分和: Σ_i (llm_prob_score_ss,i × herd_weight_ss,i), 其中 llm_prob_score_ss 来自 stage 21 对 content_ss (标题 + 银行∧金科同句 ±N 窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 的 LLM 概率打分, herd_weight_ss 是 stage 24 在 ss 轨独立算出的羊群衰减权重 (三轨独立权重不存在时退化为与 full/ctx 共用同一权重列)。ss 轨判定口径最严格, 要求银行与金科词在同一句 (或窗口半径内) 共现; 当某篇文章不存在这种同句共现时, content_ss 按镜像 ctx 的回退语义退化为全文正文 (与 content_full 同源), 同时该篇的 ss_is_fallback 标记为 True, 此时该篇在 ss 轨的 llm_prob_score_ss 与 herd_weight_ss 实质上复用了全文口径的信息, 但分母 (n_articles) 与 fallback 标记共享同一套统计口径, 便于研究者在下游区分"真同句共现驱动"与"回退到全文驱动"的观测。行宇宙同样受 full-only 门控约束, 只对 llm_verified_full == True 的报道计入。本列与 full/ctx 两列在方法论上严格并排, 互为稳健性、不分主次, 均不得混入同一 over-identified Hansen J 设定; 若源数据缺失 herd_weight_ss 或 llm_prob_score_ss, 本列在对应银行-年上以 NaN 呈现, 由 valid_agg 自动跳过而非报错崩溃。使用本列做跨银行-年或跨轨比较前, 同样须先除以对应的加权分母 sum_wd_hw_prob_ss 得到归一化均值, 避免因回退比例、篇数规模不同而产生虚假差异; 尤其在样本量较小的窗口 (如开发期 T=2 数据) 上, ss 轨零方差或大比例回退属预期退化现象, 不代表测度失效。

<!-- rendered-citations:begin -->
['Gilardi, F.', 'Alizadeh, M.', 'Kubli, M.']. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
['Kirtac, K.', 'Germano, G.']. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
['Tetlock, P. C.']. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
['de Kok, T.']. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
<!-- rendered-citations:end -->
