---
family_id: F377
columns:
- llm_prob_score_indep_cm_ctx
- llm_prob_score_indep_cm_ss
unit: 无量纲连续情感概率分, 值域 [-1, 1] (条件均值; 子集为空时为 NaN)
formula: 'per(bank, year, track): 先在文章级子集上按 innovation_collab_mode_{trk} == "自主研发" 过滤 (innovation_collab_mode_{trk} 是三家 LLM 对该篇合作模式维度多数决后的共识标签); 再对该子集内每篇文章的 llm_prob_score{trk} (三分类情感 logit-to-score, compute_prob_score(sentiment_label, sentiment_confidence), 与 collab_mode 标签无关) 取 bank-year 组内算术均值: llm_prob_score_indep_cm_{trk} = mean_{article in subset}(llm_prob_score{trk}); 由 encode.py::_aggregate_ctx_diagonal 以 dim_col=innovation_collab_mode_{trk} 分组聚合完成, 分类判据与被聚合的情感分是两条独立源列'
producer: pipeline\sentiment\tone_llms.py (compute_prob_score 三分类情感 logit-to-score 计分原语, 产文章级 llm_prob_score{trk} 源列; innovation_collab_mode_{trk} 由三家 LLM 多数决聚合产生) ; pipeline\panel\encode.py::_aggregate_ctx_diagonal (对角线分组聚合/面板落列)
upstream:
- 15_fintech_intensity.parquet (stage 14 物化 content_ctx/content_ss)
- 21_tone_llms.parquet (innovation_collab_mode_{trk} 三家投票标签 + collab_mode_confidence_{trk})
citations:
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: "71"
  issue: "9"
  pages_or_artno: "7888–7906"
- doi: "10.1080/07421222.2018.1440766"
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services"
  venue: Journal of Management Information Systems
  vol: "35"
  issue: "1"
  pages_or_artno: "220–265"
- doi: "10.1145/1102351.1102430"
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: "Proceedings of the 22nd International Conference on Machine Learning (ICML)"
  pages_or_artno: "625–632"
- doi: "10.17016/FEDS.2026.020"
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: "Federal Reserve Board FEDS Working Paper No. 2026-020"
new_dois: []
---

## CORE

【构念与来源】
llm_prob_score_indep_cm 家族衡量的是: 在"被三家大语言模型 (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31、deepseek-v4-flash/deepseekv4) 多数决共识判定为银行自主研发型金融科技合作模式" (innovation_collab_mode 标签体系里的"自主研发"类, cm=collab_mode 的缩写) 这一文章子集内, 三家 LLM 对情感极性打出的连续概率分的 bank-year 组内条件均值, 而不是对合作模式标签本身做二元置信度映射。构念上分两层: 第一层是"分类"——一篇报道所描述的银行-金科关系, 究竟是银行内部自建团队/自主技术攻关, 还是借助外部合作伙伴 (联合研发、股权投资、技术采购、生态合作等) 实现的, 承袭 Chesbrough (2003) 开放式创新 (open innovation) 框架与 Lichtenthaler & Ernst (2006, SMJ) 对企业技术获取模式 (自主研发 vs. 对外合作/引进) 的三分类刻画; stage 21 (`tone_llms.py`) 让三家 LLM 各自阅读文章后对 `innovation_collab_mode` 做多分类投票, 少数服从多数确定该篇的合作模式共识标签, 平局或空票按用户既定的保守降级策略 tie_default='自主研发' 处理。第二层是"情感"——对被划入"自主研发"子集的每一篇文章, 取其独立于 collab_mode 维度、由三家 LLM 各自的三分类情感标签+置信度经 `compute_prob_score` logit-to-score 映射得到的文章级情感概率分 `llm_prob_score{trk}` (值域 [-1, 1]), 再在 bank-year 单元内对该子集求算术均值。两层构念不是同一次计分: 分类判据 (collab_mode) 只决定"这篇文章算不算自主研发相关", 分数本身 (llm_prob_score) 度量的是这些文章在情感维度上偏正面还是偏负面, 与 collab_mode 标签的置信度无关。

`compute_prob_score` (与逐模型专用的二元版本 `compute_prob_score_binary` 同源但目标不同: 后者只服务 substantiveness/locus/collab 三个分类维度的逐模型存档列, 如 `{short}_collab_prob_score`, positive_class 取"外部协同") 把"情感标签 + 置信度"压缩成 [-1, 1] 区间上的连续分: 正面标签随置信度升高分数趋近 +1, 负面标签随置信度升高分数趋近 -1, 中性标签恒为 0; 置信度缺失、越界 (∉[0,1]) 或该轨在 verified 门控下未通过留篇判定时该篇分数记为 NaN 而非强行插值 (P3_INV 拒绝语义)。这样设计的核心动机是: 离散三分类情感标签会把"高置信正面"和"勉强正面"压扁成同一个类别值, 而连续概率分保留了这层信噪比信息; 本家族进一步把这一文章级连续情感分, 限定在"合作模式已被判定为自主研发"这一子样本内取条件均值, 用于回答"银行被描述为自主研发技术路线的报道, 其舆论口径整体偏正面还是偏负面"这一构念问题, 而非"自主研发这个标签本身有多确定"。

【方法学与计算】
计算发生在 stage 40 面板导出阶段的对角线聚合环节 (`pipeline\panel\encode.py::_aggregate_ctx_diagonal`, 由 innovation_collab_mode 对角线块在同文件内调用), 而非 stage 21 内部。对每个文本轨道 (`_ctx`/`_ss`, 该 helper 亦服务 substantiveness/locus 等姊妹家族, full 轨对角线走另一条内联路径不经此 helper), 先取文章级 DataFrame 中 `innovation_collab_mode_{trk} == "自主研发"` 的子集 `df_cat`, 再对该子集按 (target_bank, year) 分组, 对源列 `llm_prob_score{trk}` (三家 LLM 多数决前已在 stage 21 逐篇算好的三分类情感概率分, 与合作模式标签是并行的独立源列) 取组内均值, 落为 `llm_prob_score_indep_cm_{trk}`。该 helper 对两个源列 (`llm_vote_score{trk}` 计数/均值, `llm_prob_score{trk}` 概率分均值) 分别做存在性守卫: 若 `llm_prob_score{trk}` 因 stage 21 logit 探针未启用而缺席, 本列整体以 NaN 占位而非崩溃; 若子集在某 bank-year 单元内为空, 同样占位为 NaN (而非 0), 与 `n_articles_indep_cm_{trk}` 记 0 的语义区分开。留篇门控遵循 full-only 铁律 (2026-06-29 用户决策): 一篇报道是否被计入"银行-金科报道"样本只看 `llm_verified_full`, `_ctx`/`_ss` 两轨的 `llm_prob_score_indep_cm` 是在 full 轨已确定留篇的行宇宙子集上, 各轨独立按各自文本重新分类 (collab_mode) 与重新计分 (情感 prob_score) 得到的 conditional-on-full 测度/稳健性轨, 不参与是否留篇的决定, 也不与 full 轨的对应分数混合或加权平均。

本家族只落 `_ctx`/`_ss` 两列 (无 `_full` 同名列, `_aggregate_ctx_diagonal` 目前只被 ctx/ss 两处调用, full 轨对角线走另一条内联路径产出的是 `n_articles_indep`/`llm_vote_tone_indep` 等无 `_full` 后缀的列, 未产 `llm_prob_score_indep_cm_full`)。但两列背后的分类判据 (collab_mode) 与被聚合的情感源列 (`llm_prob_score{trk}`) 仍各自独立地在 full/ctx/ss 三个文本轨道上跑一遍, 是本项目"三轨互为稳健性、不分主次"铁律下的并排测度: 三轨各自 just-identified, 绝不允许混进同一个 over-identified 的 Hansen J 检验框架。ss 轨若在给定窗口半径内找不到银行与金科词的同句共现, 回退语义严格镜像 ctx 轨——`content_ss` 退化为全文正文, 对应 `ss_is_fallback=True`, 该行的 `n_articles` 分母口径与 ctx 轨共享处理约定; `FINTECH_AC=None` (金科词自动机未构建) 时 `*_is_fallback` 全体置 True, 全流水线优雅降级而不是报错中断。缓存确定性锚点是 `_llm_cache.db`: prompt 构造单一事实源 `iter_article_track_prompts` 生产/审计共用, temperature=0.0 下缓存命中即可字节级复现, `NEWS_PROCESS_LLM_OFFLINE=1` 离线守卫下缓存 miss 抛 `LLMCacheMissError` 而不再调用付费 API。

【文献定位】
把 LLM 输出的离散情感标签转换成校准过的连续概率分, 方法学根基是 Niculescu-Mizil & Caruana (2005) 关于监督学习模型输出概率校准 (probability calibration) 的经典论证——分类器的置信度分数只有经过恰当映射才能被当作有意义的连续测度使用, 而不是直接拿 softmax/投票比例这类"生分数"做统计推断; 本家族被聚合的 `llm_prob_score{trk}` 源列正是这一映射的产物。在把大语言模型当作文本标注器使用这一更晚近的方法学谱系里, de Kok (2025, *Management Science*) 系统论证了会计与金融研究中使用生成式 LLM 做文本分析时, temperature 锁定、prompt 冻结、结果缓存等确定性约束的必要性, 与本项目 stage 21 的整体设计范式直接呼应; Hansen (2026, FEDS 工作论文) 进一步讨论了在缺乏人工金标准时如何验证 LLM 标注质量, 呼应本项目多家 LLM 独立投票 + 一致性诊断 (agreement_rate) 的三角验证设计思路。"自主研发 vs. 对外合作"这一分类构念本身承袭 Chesbrough (2003) 开放式创新框架对企业技术获取路径的二元区分, 并借鉴 Gomber, Kauffman, Parker & Weber (2018, *Journal of Management Information Systems*) 对金融科技创新维度体系 (locus/substantiveness/collaboration mode) 的系统化界定——本项目 `innovation_collab_mode` 三维分类标签体系 (locus/substantiveness/collab_mode) 中的 collab_mode 维度即直接对应该文献框架里"合作模式"这一轴, 在本家族中只充当分组判据、不进入被聚合的分值本身。llm_prob_score_indep_cm 家族因此是把"分类维度的 LLM 判定结果"用作条件筛选器, 度量该子样本上情感连续暴露测度的组内均值, 供研究银行金融科技创新战略 (是否倾向自建技术能力) 与舆论口径之间关联的相关命题使用; 与家族内情感维度的 llm_prob_score (基于 logit-to-score 的三分类情感连续分) 共享的是同一个源列而非同一套映射目标——本家族并未对 collab_mode 标签本身再套一层"标签+置信度→连续分"映射, 目标构念是"自主研发子样本内的情感均值"而非"自主研发这一判定有多确定"。

## VAR: llm_prob_score_indep_cm_ctx

【变体差分】
本列是 llm_prob_score_indep_cm 家族在 ctx 轨 (标题+银行实体窗口文本) 上的实现, 列名后缀 `_ctx` 标示分类判据与被聚合情感分共同取材于围绕目标银行实体的窗口片段 `content_ctx`, 而非全文正文。计算路径: 三家 LLM (gpt54nano/gemini31/deepseekv4) 各自阅读 `content_ctx` 后对 `innovation_collab_mode` 做投票、多数决确定共识标签 `innovation_collab_mode_ctx`; `encode.py::_aggregate_ctx_diagonal` 取该标签 == "自主研发" 的文章子集, 对该子集内每篇文章的情感概率分源列 `llm_prob_score_ctx` (三分类情感 logit-to-score, 与 collab_mode 标签无关的独立列) 按 (target_bank, year) 分组求均值, 落为本列。差分仅在于喂给三家模型判断合作模式与情感的文本来源都换成了实体窗口: ctx 轨截断掉了与目标银行实体距离较远的段落, 因此对"该银行的技术合作模式是否为自主研发"这一判断更聚焦, 但也可能因窗口截断丢失全文中远处出现的关键描述性信息 (例如合作细节写在文章末尾总结段, 而该段落落在实体窗口之外), 进而影响子集划分与子集内情感均值。本列在留篇口径上是 conditional-on-full: 行宇宙限定在 `llm_verified_full` 判定为留篇的样本子集内, 本轨自身不参与是否留篇的判定, 是 full 轨的稳健性/测度补充轨而非替代轨, 三轨间禁止混入同一个 over-identified Hansen J 识别策略, 只能各自 just-identified 并排使用。若三家模型在 ctx 轨给出的 collab_mode 投票出现平局或空票, 按 tie_default='自主研发' 的保守降级规则处理, 与 full/ss 两轨同一套决策口径, 确保三轨间除文本来源外方法学参数完全对齐、差异可完全归因于文本窗口本身; 若该 bank-year 单元在 ctx 轨的自主研发子集为空, 本列记 NaN 而非 0。

## VAR: llm_prob_score_indep_cm_ss

【变体差分】
本列是 llm_prob_score_indep_cm 家族在 ss 轨 (标题+银行∧金科同句共现窗口, 半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句) 上的实现, 是三轨中文本取材范围最窄、判据最严格的一支: 只保留银行实体词与金科相关词在同一句 (或配置半径内相邻句) 共同出现的片段 `content_ss` 喂给三家 LLM, 各自对 `innovation_collab_mode` 投票聚合出共识标签 `innovation_collab_mode_ss`; `_aggregate_ctx_diagonal` (以 track='_ss' 调用) 取该标签 == "自主研发" 的子集, 对子集内 `llm_prob_score_ss` (同一独立情感源列的 ss 轨版本) 按 (target_bank, year) 分组求均值产出本列。这一轨的设计意图是最大程度剥离"银行"和"金科"仅仅共同出现在同一篇文章中、但实际讨论的是两件不相关事情的噪声, 只保留两者被同一句话直接绑定描述的片段来判断合作模式并度量其情感口径。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章在给定句子半径内未找到银行∧金科的同句共现, `content_ss` 退化为全文正文 (等同于 full 轨的文本输入), 对应指示列 `ss_is_fallback` 置 True, 此时该行的 `n_articles` 分母口径与 ctx 轨共享的处理约定一致; 若 `FINTECH_AC` 金科词自动机未构建 (None), 则全体 `*_is_fallback` 置 True, 整条 ss 轨优雅降级为等同 full 轨的输入而非报错中断。与 ctx 轨相同, 本列同样是 conditional-on-full 测度, 行宇宙由 full 轨的 `llm_verified_full` 留篇判定圈定, 平局默认值同为 tie_default='自主研发', 三轨 (full/ctx/ss) 之间互为稳健性、不分主次, 各自 just-identified 并排比较, 严禁混入同一个 over-identified Hansen J 识别框架内联合估计; 该 bank-year 单元 ss 轨自主研发子集为空时同样记 NaN。
<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888–7906. https://doi.org/10.1287/mnsc.2023.03253
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services. Journal of Management Information Systems, 35(1), 220–265. https://doi.org/10.1080/07421222.2018.1440766
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625–632. https://doi.org/10.1145/1102351.1102430
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
