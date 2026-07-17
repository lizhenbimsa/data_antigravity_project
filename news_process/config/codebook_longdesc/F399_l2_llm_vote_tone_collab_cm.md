---
family_id: F399
columns:
- llm_vote_tone_collab_cm_ctx
- llm_vote_tone_collab_cm_ss
unit: 语调得分 (连续, 约 [-1,1]; bank-year 聚合均值)
formula: llm_vote_tone_collab_cm_{ctx,ss} = mean(llm_vote_score_{ctx,ss} | innovation_collab_mode_{ctx,ss} == '外部协同'), 分子为文章级投票分 (-1/0/1) 在该判类子集上的均值, 分母为该 bank-year 落在"外部协同"判类下的合格文章数 n_articles_collab_cm_{ctx,ss}; 结果落入面板列 llm_vote_tone_collab_cm_{ctx,ss} (面板层聚合列名, 与文章级源列 llm_vote_score 是不同命名层级)
producer: pipeline\panel\encode.py
upstream:
- pipeline\sentiment\tone_llms.py
- pipeline\panel\encode.py::_aggregate_ctx_diagonal
citations:
- doi: '10.1111/jpim.12710'
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: '41'
  issue: '4'
  pages_or_artno: 793-815
- doi: '10.48550/arXiv.2511.15714'
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: '10.1287/mnsc.2023.03253'
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: '10.1007/s00521-024-10603-6'
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: 'Chinese fine-grained financial sentiment analysis with large language models'
  venue: Neural Computing and Applications
  vol: '37'
  issue: '30'
  pages_or_artno: 24883-24892
- doi: '10.17016/FEDS.2026.020'
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: 'Federal Reserve Board FEDS Working Paper No. 2026-020'
- doi: "10.1017/psrm.2024.64"
  type: "journal"
  authors: "Ornstein, J. T., Blasingame, E. N., & Truscott, J. S."
  year: 2025
  title: "How to train your stochastic parrot: large language models for political texts"
  venue: "Political Science Research and Methods"
  vol: "13"
  issue: "2"
  pages_or_artno: "264-281"
- doi: "10.18653/v1/2025.findings-acl.744"
  type: "journal"
  authors: "Wang, W., Wang, Y., & Huang, H."
  year: 2025
  title: "Ranked Voting based Self-Consistency of Large Language Models"
  venue: "Findings of the Association for Computational Linguistics: ACL 2025"
  pages_or_artno: "14410-14426"
- doi: "10.1007/s42001-025-00388-6"
  type: "journal"
  authors: "Abraham, L., Arnal, C., & Marie, A."
  year: 2025
  title: "Prompt selection matters: enhancing text annotations for social sciences with large language models"
  venue: "Journal of Computational Social Science"
  vol: "8"
  issue: "3"
  pages_or_artno: "73"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行—金融科技报道中"外部协同"(external collaboration) 合作模式子样本内的 LLM 三家投票语调, 是 P5 (bank_fintech_collab, Chesbrough 2003 开放式创新框架) 论文族的核心测度分支之一。上游 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 对每篇留篇文章逐轨输出 (a) 语调判断 (正/负/中性经多数投票合成 `llm_vote_tone_{track}`)、(b) 合作模式判类 `innovation_collab_mode_{track}` ∈ {自主研发, 外部协同, ...} (LLM 分类维度, 与情感判断共享同一次调用产出的结构化解析结果, 但属两套独立标签空间)。`encode.py::_aggregate_ctx_diagonal` 在 bank-year 聚合阶段做"对角线"筛选: 先按 `innovation_collab_mode_{track} == '外部协同'` 划出文章子集, 再对该子集计算语调均值, 得到本家族列 `llm_vote_tone_collab_cm_{ctx,ss}`; 与之对角互补的是 `llm_vote_tone_indep_cm_{track}` (自主研发子集语调, 另立家族), 二者相减构成 `tone_gap_indep_collab_cm_{track}` (需 `n_articles_indep_cm_{track} >= 5` 且 `n_articles_collab_cm_{track} >= 5` 双边最小样本量守卫, 才不致单篇 cell 伪造机制断言)。命名后缀 `_cm` (collab mode) 标识该列来自"合作模式对角线切片", 区别于家族无条件全样本 `llm_vote_tone_{track}` 及分母口径不同的 `collab_frac_cm` (外部协同占比, 分子=n_articles_collab_cm_{track}, 分母=n_articles_llm_valid_{track})。

【方法学与计算】
LLM 多数投票语调 `llm_vote_tone` 是三家独立商业化大语言模型 (gpt-5.4-nano / gemini-3.1-flash-lite 经 yunwu 中转 / deepseek-v4-flash 直连 api.deepseek.com) 在冻结 prompt (`prompt_version='v8-2026-05-17'`, temperature=0.0) 下对每篇文章逐轨给出的三分类语调判断, 经多数投票合成一票共识; 该共识列是 P1 (bank_fintech_tone) 的 headline treatment (`llm_vote_tone_full`), 本家族则是其在合作模式维度上做条件切片后的衍生子测度。`innovation_collab_mode` 是同批 LLM 调用输出的另一结构化字段 (P5 substantiveness/locus/collab 三元分类体系之一, SSOT = `encode.LLM_CLASS_SPEC`)。按 CLAUDE.md 稳健性缺口补齐条目口径, 文章级 `innovation_collab_mode_{full,ctx,ss}` 本身是不门控审计存档 (源码 `tone_llms.py` 在解析出分类标签后无条件写回 df, 不因 `llm_verified_full` 真假而取舍是否落 archive); verified 门控真正生效的位置在 encode 聚合层——本家族分母 `n_articles_collab_cm_{track}` 只计入该模型/该轨自身 verified 篇数范围内的行, 从而把"是否计入 bank-year 均值分母"这一步骤限定在验证子集上, 而非在 archive 写入阶段就过滤掉未验证文章的标签。留篇门控口径按 CLAUDE.md「留篇门控 = full-only」(2026-06-29) 生效于哪些文章进入"一篇银行金科报道"的文章级判定 (行宇宙 = full 留篇集子集), ctx/ss 轨的分类/语调列在该行宇宙子集上逐轨各算, 不额外叠加 ctx/ss 自身的二次门控。聚合公式先在文章级筛出 `innovation_collab_mode_{track} == '外部协同'` 的行, 再对该子集内 `llm_vote_tone_{track}` 取 bank-year 算术均值; 分母同步落地为 `n_articles_collab_cm_{track}` (先 `fillna(0).astype(int)` 保证整数计数不带 NaN 污染)。`_aggregate_ctx_diagonal` 的"对角线"命名指该函数同时处理 ctx 与 ss 两条轨道各自独立的分类-语调联合聚合, 与 substantiveness (`_sc`)、locus (`_lc`) 两个姊妹分类维度共享同一 helper 逻辑与守卫模式 (fix omni-g-encode-05, 2026-06-11 统一收口), 三者互不混算但代码路径同构。分母口径经 2026-06-02 metric-audit 修正: ctx 轨的合作模式判类只配 ctx 轨自身的验证篇数分母 (`n_articles_llm_valid_ctx`), ss 轨同理配 `n_articles_llm_valid_ss`, 修复了此前跨轨错配导致 frac 类指标可能 >1 的轨道不对称问题; 缺该分母列时整族置 NaN 并 loud WARNING, 不做静默零填充。

【文献定位】
本家族测度设计承接 Chesbrough (2003) 开放式创新范式对"自主研发 vs. 外部协同"两条技术获取路径的经典二分, 并将其映射为可从中文财经新闻文本中判类的 LLM 分类构念, 呼应 Zhang, Ma, Liang & Garrett (2024, *Journal of Product Innovation Management*) 对开放式创新前因后果二十年 meta-analysis 中协同二分变量构造方式的最新综述定位。多家商用 LLM 独立投票再合成共识的方法学设计, 借鉴 Kamen & Kamen (2025) 关于 LLM ensemble 多数投票在内容分类任务上优于单模型的证据, 以及 de Kok (2025, *Management Science*) 就 temperature=0/prompt 冻结/结果缓存构成会计与金融文本分析中 LLM 应用可复现性范式的方法论建议 (本仓库 stage 21 缓存架构与之同构)。语调判断本身作为财经文本情感测度, 与 Lan, Wu, Xu, Feng & Zhang (2025, *Neural Computing and Applications*) 面向中文金融细粒度实体级情感分析的 LLM 方案在任务定义上高度对应 (本仓库亦对中文语料逐实体、逐轨调用大模型判类)。在缺乏金标准标注时如何验证 LLM 输出标签质量的问题上, 参照 Hansen (2026, FEDS Working Paper) 提出的一致性度量框架 (κ/α), 本仓库跨模型一致性检验 (`tone_validation.py`) 采用同源思路。 在「LLM 产出文本级标签、再逐单元聚合」这一测量链路的社会科学先例上, Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度与主题建模等多项政治学文本即数据任务上做预注册评估, 结论是该做法优于传统有监督学习基线, 并以极低成本达到与专家及众包编码员相当 (comparable, 而非超过) 的水平; 本族先由 LLM 逐篇产出语调标签与创新模式判类、再在「外部协同」判类子集上取均值, 正属同族链路。迁移边界: 原文语料为英文政治文本 (立法、演讲等), 采用单一模型而非三家投票, 亦无 bank-year 面板聚合、留篇门控与三轨文本切分。在投票规则一侧, Wang、Wang 与 Huang (2025) 以排序投票 (ranked voting) 取代朴素多数票聚合 LLM 的候选输出并实证其聚合质量提升, 说明投票规则本身是一处设计自由度而非唯一解; 惟其投票单元是同一模型多次采样所得的候选答案 (self-consistency) 而非跨厂商标签投票, 任务为推理/生成而非三分类情感, 本族仍维持朴素多数票、未采纳排序投票。此外, Abraham、Arnal 与 Marie (2025) 实证 prompt 选择对社科文本标注质量有显著且非平凡的影响, 这对本族尤为切题: 本族同时依赖类目判定与语调打分两组由同一冻结 prompt 产出的输出, prompt 敏感性经条件均值的子集选择被二次传导; 惟原文的核心贡献是遍历 prompt 网格择优, 而本项目 prompt v8 已字节级冻结并作为缓存键, 刻意不做 prompt 网格 (改 prompt 即全缓存作废), 故该文提示的 prompt 敏感性在本项目属未量化的已知局限, 而非已排除的风险。
## VAR: llm_vote_tone_collab_cm_ctx

【变体差分】
本列是家族在 ctx 轨 (标题 + 实体窗口文本) 上的合作模式对角线切片语调均值: 分子为该 bank-year 内 ctx 轨 `innovation_collab_mode_ctx == '外部协同'` 判类文章的 `llm_vote_tone_ctx` 均值, 分母 `n_articles_collab_cm_ctx` 为满足该判类条件的 ctx 轨合格文章数。ctx 轨的语调判断与合作模式判类均来自同一次 LLM 调用对 ctx 文本 (`content_ctx` = 标题 + 实体窗口, 由 stage 14 `ctx_materializer` 物化) 的解析, 与家族姊妹列 `_ss` 在文本窗口构造上严格区分: ctx 是"标题+实体窗口" (较宽的上下文半径), ss 是"标题+银行∧金科同句±N窗" (更窄的严格共现窗口, 无同句共现时回退全文并置 `ss_is_fallback=True`)。按 CLAUDE.md 铁律, ctx 轨与 ss 轨 (以及未在本家族出现的 full 轨) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定; 本列作为 ctx 轨专属子测度, 不应与 `_ss` 或全样本 headline `llm_vote_tone_full` 的合作模式版本混入同一 RHS 做联合识别。分母配比同样是 ctx 专属: `n_articles_llm_valid_ctx` (2026-06-02 metric-audit 修正后的严格轨内配对), 而非借用 full 轨或 ss 轨的验证篇数, 避免跨轨分母错配虚增或虚减占比。当同 bank-year 内 ctx 轨"外部协同"判类样本量不足 (含零篇) 时, 本列聚合结果为 NaN (若参与 `tone_gap_indep_collab_cm_ctx` 差分运算, 另受 `n_articles_indep_cm_ctx>=5` 与 `n_articles_collab_cm_ctx>=5` 双边最小样本量守卫约束, 该守卫是 2026 年 completeness-05 补丁针对第 6 个 tone_gap 缺失守门问题的补齐, 与其余 5 个同族 tone_gap 列口径对齐)。

## VAR: llm_vote_tone_collab_cm_ss

【变体差分】
本列是家族在 ss 轨 (标题 + 银行∧金科同句共现窗口) 上的合作模式对角线切片语调均值: 分子为该 bank-year 内 ss 轨 `innovation_collab_mode_ss == '外部协同'` 判类文章的 `llm_vote_tone_ss` 均值, 分母 `n_articles_collab_cm_ss` 为满足该判类条件的 ss 轨合格文章数, 分母配比同样经 metric-audit 修正为严格轨内自配 (`n_articles_llm_valid_ss`), 不借用 ctx 或 full 轨分母。ss 轨判类的文本输入 `content_ss` 遵循镜像 ctx 的回退语义: 当某篇文章内不存在目标银行与金科词的严格同句共现 (句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 生产默认 ±1 句) 时, `content_ss` 回退为全文 body 并置 `ss_is_fallback=True`, 该回退与 ctx 轨的回退语义结构对称、共享 `n_articles` 分母口径, 使得 ss 轨在共现证据稀薄的银行—年份单元里退化为近似全文测度而非产生系统性缺失。ss 轨判类原语 (`extract_bank_fintech_cooccurrence` 严格同句口径) 与 stage 13 硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` (±1 句窗口口径) 是两个刻意区分、禁止互相复用的判据: 前者服务于 ss 轨文本物化与本列聚合, 后者服务于文章留篇与否的硬过滤决策。本列与 `_ctx` 列同为该合作模式测度族的并排稳健性轨道, 二者互不替代、也不构成同一识别方程内的过度识别工具组合; 当量化"外部协同语调"这一构念的稳健性时, 应将 `_ctx` 与 `_ss` 的估计系数并列报告而非合并为单一联合矩估计。ss 轨样本量普遍小于 ctx 轨 (同句共现条件比实体窗口条件更严格), 因此本列在小样本 bank-year 单元 (尤其 T=2 开发库) 上更易出现零方差或全 NaN 的预期退化, 生产全量语料 (T=19) 下样本量回升后该退化会自然缓解。

<!-- rendered-citations:begin -->
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
Abraham, L., Arnal, C., & Marie, A. (2025). Prompt selection matters: enhancing text annotations for social sciences with large language models. Journal of Computational Social Science, 8(3), 73. https://doi.org/10.1007/s42001-025-00388-6
<!-- rendered-citations:end -->
