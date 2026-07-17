---
family_id: F367
columns:
- llm_models_avg_cont_sum_ctx
- llm_models_avg_cont_sum_full
- llm_models_avg_cont_sum_ss
unit: 无量纲连续型情感强度加总 (跨三家 LLM 均值)
formula: 'mean_over_m({m}_cont_sum{track}) for m in LLM_MODELS={gpt54nano, gemini31, deepseekv4}; track in {_full, _ctx, _ss}; 缺列经 _safe_mean 优雅返回 NaN'
producer: pipeline\panel\geography.py
upstream:
- 21_tone_llms.parquet
- 40_panel_yearly.parquet (bank-year 聚合前的文章级 cont_sum 上游)
citations:
- doi: "10.1111/1475-679X.12123"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2016
  title: "Textual Analysis in Accounting and Finance: A Survey"
  venue: "Journal of Accounting Research"
  vol: "54"
  issue: "4"
  pages_or_artno: "1187-1230"
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A Large Language Model for Extracting Information from Financial Text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, F., Alizadeh, M., & Kubli, M."
  year: 2023
  title: "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
- doi: "10.1177/00491241251325243"
  type: journal
  authors: "Chae, Y., & Davidson, T."
  year: 2026
  title: "Large Language Models for Text Classification: From Zero-Shot Learning to Instruction-Tuning"
  venue: "Sociological Methods & Research"
  vol: "55"
  issue: "2"
  pages_or_artno: "501-567"
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
本家族衡量的是银行—年度面板层面, 三家大语言模型 (gpt54nano / gemini31 / deepseekv4) 对该银行金科相关报道给出的连续型情感强度得分之加总 (cont_sum) 的跨模型均值, 三轨 (full/ctx/ss) 并行。它属于 stage 21 情感 LLM 三家投票产出族 (`llm_vote_tone` 及其配套连续测度) 在 `pipeline/panel/geography.py` 内的跨模型综合层, 直接消费的上游是逐模型逐篇的 `{model}_cont_mean{track}` 聚合到银行—年度后的 `{model}_cont_sum{track}` 列 (每家模型对每篇留篇报道输出一个连续置信/强度分数, cont_mean 是篇内多次采样或 logit 概率的均值, cont_sum 是该银行—年度全部相关报道上的加总, 量纲随报道条数增长, 是「强度」而非「均值语气」)。产出函数 `_safe_mean` 对存在的模型列取行方向 (即跨模型) 简单算术平均: 若 `{m}_cont_sum{track}` 三列全部存在则等权平均; 若某家模型因缓存缺失、离线守卫或播种未覆盖而缺列, `_safe_mean` 优雅跳过缺列而非报错, 用剩余可用模型的均值填充, 全部缺失则整格为 NaN。这一设计使得该家族在生产语料尚未全量播种三家模型缓存时也能安全产出中间态数值而不中断下游面板导出。

三家模型是 CLAUDE.md「LLM 三家互为稳健性」铁律下的 co-equal 跨厂商稳健测度 (gpt-5.4-nano / gemini-3.1-flash-lite 两家经 yunwu 代理, deepseek-v4-flash 直连官方 API), 各自独立 just-identified, 互为稳健性而非分主次; 本家族对三家取算术均值, 属于「均值-ensemble」层, 与三家各自的逐模型子测度 (`{model}_cont_sum{track}`) 及多数投票共识 `llm_vote_tone{track}` 是并列而非替代关系, 三者均落盘保留供研究者按需选用。与三家投票共识测度 (离散多数票语气 -1/0/1) 不同, 本家族是连续型强度加总, 保留了模型输出的置信程度信息而非仅方向; 与 `llm_models_avg_cont{track}` (跨模型均值的 cont_mean, 即「每篇平均强度」的跨模型均值) 不同, 本家族是 `cont_sum` 的跨模型均值, 即「银行—年度全部报道强度总和」的跨模型均值, 二者构念不同不可互换 — 前者反映单篇平均语气强度水平, 本家族则同时携带了报道数量的尺度信息 (报道越多、每篇强度越高, cont_sum 越大), 因而更接近「该银行—金科议题在媒体上被以多强的语气反复渲染」的复合暴露度量, 使用者若要控制报道数量效应, 应同时纳入 `n_articles` 或改用 `llm_models_avg_cont{track}`。

【方法学与计算】
三轨 full/ctx/ss 是 CLAUDE.md 铁律下三份并行文本口径产出的三条独立测度: `_full` = 标题+全文正文; `_ctx` = 标题+银行/金科实体窗口截取文本; `_ss` = 标题+银行∧金科同句 (或 ±N 句窗口) 共现片段, 缺失同句共现时镜像 `_ctx` 的回退语义, 退化为全文 body 并置 `ss_is_fallback=True`, 与 `_ctx` 共享 `n_articles` 分母。三轨在 stage 14 `ctx_materializer` 统一物化文本列, stage 21 情感 LLM 对三轨分别独立跑取分, 因此三条 `llm_models_avg_cont_sum{track}` 各自 just-identified 并排, 互为稳健性、不分主次, 严禁在同一 over-identified Hansen J 或单一 GMM 矩条件系统中混用多轨。留篇门控 (即一篇报道是否计入该银行—金科相关样本) 采用 full-only 口径 (2026-06-29 起): 是否留篇只看 `llm_verified_full == True`, ctx/ss 轨的行宇宙是 full 留篇集合的子集, 三轨各自独立算自己的 cont_sum, 不因 ctx/ss 判定不同而扩大或缩小样本。计算链条为: stage 21 对每篇留篇报道由三家模型分别输出连续强度分 (`{m}_cont_mean{track}`, 篇级); panel 构建阶段按银行—年度对篇级值加总得到 `{m}_cont_sum{track}`; 本家族再对三家模型的 `cont_sum` 取跨模型简单算术均值, 无加权、无 winsorize、无对数变换, 是纯粹的算术平均聚合, 计算成本为 $0 (对已落盘列的行方向平均, 不调用任何 LLM/embedding API)。

【文献定位】
财务文本情感的三角测量传统 (词典法 / 机器学习 / 大语言模型) 早已认识到单一测度方法存在系统性偏误, Loughran & McDonald (2016, *Journal of Accounting Research*) 系统综述了会计与金融文本分析中不同方法各自的优劣与适用边界, 为多方法并行、互为稳健性的设计取向提供了方法论基础。Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 提出的 FinBERT 表明面向金融领域微调的语言模型能够更精准提取文本中的情感信息, 但也隐含单一模型可能带有厂商/训练语料特异性偏差的风险, 这正是本家族坚持三家模型 (而非单家) 跨厂商综合的动机所在。de Kok (2025, *Management Science*) 系统讨论了在会计研究中使用生成式大语言模型进行文本分析的方法论规范, 强调 temperature=0、prompt 版本冻结等确定性锚点对结果可复现性的重要性, 本项目 stage 21 的 prompt v8 字节级冻结与三家模型缓存命中即可离线 $0 复现的设计正对应这一规范要求。Gilardi, Alizadeh & Kubli (2023, *PNAS*) 的实证表明大语言模型在文本标注任务上可以媲美甚至超过众包人工标注者, 为以 LLM 而非纯词典法作为情感强度的主测度提供了外部效度支撑; 但跨模型一致性并非自动成立, Chae & Davidson (2026, *Sociological Methods & Research*) 综述指出零样本与指令微调的大语言模型在文本分类任务上的表现存在模型间差异, 进一步支持了本项目「三家模型互为稳健性、禁止把跨模型差异误当作单一真值噪声」的设计立场——本家族的跨模型均值正是对这种模型间差异的一种保守综合, 而非替代对三家逐模型子测度的单独审视。 沿这一取向, 近年前沿进一步给出了跨模型集成本身的存在性依据与下游处理路径。Wang、Wang、Athiwaratkun、Zhang 与 Zou (2024) 实证表明聚合多个异构大语言模型的输出优于任何单一成员模型, 并刻画了模型间的协作性, 为本家族以三家异构厂商模型并列打分、再对连续强度取跨模型算术均值的架构提供了前沿参照; 惟该文的聚合是分层生成式的 (后层模型读取前层模型的完整回答再合成), 与本家族对连续分直接取算术均值的机械聚合并非同一机制, 其评测亦限于英文指令跟随基准而非中文银行—金融科技新闻情感, 更未讨论 per-model 独立降级与缺列优雅返回 NaN 的语义。Burtch、McFowland、Yang 与 Adomavicius (2026) 则利用集成学习器内部各成员预测之间的差异构造工具变量, 以缓解 ML 生成变量充当回归元时的测量误差偏误, 其「多个成员对同一对象各自打分、成员间存在系统性差异」的结构与本家族同构, 提示跨模型离散度本身可能携带关于测量误差的信息; 但原文的集成成员是同一训练流程下可重采样的 ML 预测器, 差异来源明确, 而本家族成员是三家不可控、不可重采样的闭源商用 LLM, 其构造 IV 的前提未必成立 — 本项目并未实施该方案, 三家子测度仍各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。
## VAR: llm_models_avg_cont_sum_full

【变体差分】
本列取三轨中的 `_full` 轨, 即标题+全文正文口径下三家 LLM 连续强度分 `{m}_cont_sum_full` 的跨模型算术均值。全文轨是留篇门控的唯一依据轨 (2026-06-29 起 full-only 铁律): 一篇报道是否被判定为「该银行—金科相关」只看 `llm_verified_full == True`, 因此本列对应的行宇宙 (即参与加总的篇目集合) 是三轨中最完整、最不受实体窗口截取或同句共现约束影响的一支, 也是 P1 `bank_fintech_tone` 主线 treatment 所依托的核心文本口径。相较 `_ctx`/`_ss` 两轨, `_full` 轨让模型接触到报道的完整上下文 (包括可能与银行—金科议题弱相关的背景段落), 因而其强度均值往往捕捉的是整篇报道的总体语气渲染强度, 而非聚焦于银行与金科实体紧邻处的语气; 这既是优势 (信息完整、不因窗口截断丢失语境) 也是局限 (可能混入与核心议题无关段落的语气噪声), 与 `_ctx`/`_ss` 两轨构成互为稳健性而非互相替代的关系, 三轨务必并排报告, 不得挑选单轨结果作为唯一证据。由于 `_full` 轨同时是留篇门控的判定依据轨, 本列的样本量 (即参与跨模型均值加总的银行—年度—模型三元组数目) 在三轨中最大且不受任何下游筛选影响, 是最适合作为基线 (baseline) 汇报的一支; 研究者在撰写主表时应以本列 (或其配套的多数投票共识 `llm_vote_tone_full`) 作为 P1 `bank_fintech_tone` 主线 treatment 的默认口径, 再以 `_ctx`/`_ss` 两列作为文本窗口选择的稳健性附表, 三者数值方向一致方可支持结论不依赖窗口构造这一具体选择。

## VAR: llm_models_avg_cont_sum_ctx

【变体差分】
本列取三轨中的 `_ctx` 轨, 即标题+银行/金科实体窗口截取文本口径下三家 LLM 连续强度分 `{m}_cont_sum_ctx` 的跨模型算术均值。`_ctx` 轨的文本是围绕银行实体与金科相关词在原文中出现位置截取的局部窗口拼接标题而成 (stage 14 `ctx_materializer` 物化, `prepend_title`), 目的是让模型的注意力集中在与研究构念直接相关的语境片段, 降低全文轨可能引入的无关段落噪声, 是 conditional-on-full 的测度/稳健性轨: 其行宇宙是 `_full` 留篇集合的子集 (只对 `llm_verified_full == True` 的篇目再算 ctx 轨强度), 而非独立扩展样本。当某篇报道原文中不存在可截取的实体窗口时, 该篇在 `_ctx` 轨的处理遵循 stage 14 的兜底规则 (由物化环节决定, 与 `_ss` 轨的回退语义不同, `_ctx` 本身即为回退语义的参照基准)。本列与 `_full`/`_ss` 两列各自 just-identified 并排, 是互为稳健性的三点之一, 用以检验主结论是否对文本窗口选择敏感; 与 `_full` 轨相比, 若同一银行—年度的 `_ctx` 与 `_full` 强度均值方向一致但幅度不同, 说明窗口截取主要影响强度尺度而非方向, 支持全文轨作为主口径的稳健性。使用者若关心「窗口截取是否人为放大或缩小了模型输出的强度分数」这一测量误差来源, 应把本列与 `_full` 轨并列汇报相关系数与均值差异, 而不是仅报告其一; 若两轨在方向上出现系统性分歧 (而非仅幅度差异), 则提示全文中存在与银行—金科核心议题方向相反的语气段落, 此时应结合 `bank_fintech_tone` 主线的篇级审计列进一步排查, 而非直接判定某一轨「更准确」——三轨之间没有先验的优劣次序, 只有构念覆盖范围的差异。

## VAR: llm_models_avg_cont_sum_ss

【变体差分】
本列取三轨中的 `_ss` 轨, 即标题+银行∧金科同句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的 ±N 句窗口, 默认 N=1) 共现片段口径下三家 LLM 连续强度分 `{m}_cont_sum_ss` 的跨模型算术均值。`_ss` 轨是三轨中文本口径最严格的一支, 只保留银行与金科词在同一句 (或临近句窗口) 内共现的片段, 目的是最大限度剥离与核心构念 (银行—金科关系) 无关的语境干扰。其回退语义严格镜像 `_ctx` 轨的回退公理: 当某篇留篇报道内不存在满足同句 (或窗口) 共现条件的片段时, `content_ss` 退化为全文 body 文本, 并置 `ss_is_fallback=True`, 与 `_ctx` 轨共享同一 `n_articles` 分母, 而非另建独立分母, 以保证跨轨可比性。同样, 本列的行宇宙是 `_full` 留篇集合的子集, 属 conditional-on-full 的稳健性轨。producer 端 `_safe_mean` 对 `{m}_cont_sum_ss` 三家模型列缺失时优雅返回 NaN, 因此在生产语料三家模型 `_ss` 轨缓存尚未全量播种的阶段, 本列可能呈现比 `_full`/`_ctx` 更高的缺失率, 属预期状态而非产出缺陷。本列与另外两轨严禁混入同一 over-identified Hansen J 或单一 GMM 系统, 应作为独立并排的稳健性检验呈现。由于同句共现要求最严格, `_ss` 轨在三轨中往往对应最小的「有效」文本片段 (`ss_is_fallback=False` 的子集), 其强度加总最贴近「银行与金科被同一句话直接绑定谈论时的语气」这一最窄构念; 与之相对, `ss_is_fallback=True` 的行实质上退化为与 `_ctx` 或 `_full` 相近的宽口径, 使用者若要严格检验「同句共现」本身是否驱动结果, 建议结合 `ss_is_fallback` 指示列做子样本拆分比较, 而非直接把全部行的 `_ss` 均值与 `_full`/`_ctx` 等量齐观地比较系数大小。
<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2016). Textual Analysis in Accounting and Finance: A Survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Chae, Y., & Davidson, T. (2026). Large Language Models for Text Classification: From Zero-Shot Learning to Instruction-Tuning. Sociological Methods & Research, 55(2), 501-567. https://doi.org/10.1177/00491241251325243
Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J. (2024). Mixture-of-Agents Enhances Large Language Model Capabilities. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2406.04692
Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
<!-- rendered-citations:end -->
