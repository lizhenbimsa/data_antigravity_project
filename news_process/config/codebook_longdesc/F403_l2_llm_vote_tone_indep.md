---
family_id: F403
columns:
- llm_vote_tone_indep_ctx
- llm_vote_tone_indep_full
- llm_vote_tone_indep_ss
unit: 语调得分 (连续, 三分类多数票 {-1, 0, 1} 映射后取 bank-year 均值, 理论区间 [-1,1])
formula: llm_vote_tone{track} 在 innovation_collab_mode=='indep' 子样本上按 (target_bank, year) 分组取均值; 上游 llm_vote_tone{track} 本身取自三家 LLM (gpt54nano/gemini31/deepseekv4) 逐篇多数投票 (2/3 一致才计非零, 否则记 0/弃权) 后映射到 {-1,0,1} 的文章级共识标签
producer: pipeline\panel\encode.py
upstream:
- pipeline\panel\tone_llms.py
- pipeline\panel\encode.py::LLM_MODELS
- pipeline\panel\encode.py::_check_partition_identity
citations:
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
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: '41'
  issue: '4'
  pages_or_artno: 793-815
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"银行—金科报道语调, 限定在银行以自主研发 (非外部协同) 模式推进金融科技的文章子样本"这一构念, 即 P5 (Chesbrough 开放式创新框架下的 collab/indep 二分类, `innovation_collab_mode`) 与 P1 (三家 LLM 多数投票语调 `llm_vote_tone`) 两条测度链在 encode 层的交叉切片。列名 `llm_vote_tone_indep_{full,ctx,ss}` 由三段拼成: 语调测度前缀 `llm_vote_tone` (即三家大语言模型 gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash 对每篇文章逐条判定正面/负面/中性, 2/3 及以上一致才落地非零共识标签、否则记为弃权/中性) + 协作模式后缀 `_indep` (该文章被上游 collab_mode 分类器判定为"独立自主研发"银行金科新闻, 与判定为"外部协同"的 `_collab` 互斥) + 三轨后缀 `{_full,_ctx,_ss}` (文本窗口口径)。源码摘录显示, encode.py 在 `innovation_collab_mode` 聚合循环内, 对每个 `suffix ∈ {_indep, _collab}` 与每条轨道 `track ∈ {_full, _ctx, _ss}`, 若文章级列 `{short}_score{track}` 存在, 则以 `groupby(['target_bank','year'])` 对该 collab_mode 子样本内的文章取均值, 生成 `{short}_tone{suffix}{track}` (每家模型独立轨) 与聚合共识列 `llm_vote_tone{suffix}{track}`; 本家族即后者的 `_indep` 分支。这一构念服务于论文 P5 (以及作为 P1 的稳健性切片): 银行披露"自主研发金融科技"相关新闻时, 媒体语调是否系统性不同于披露"与外部金科企业协同"相关新闻的语调, 是检验企业沟通策略 (Chesbrough 开放式创新 vs. 内生能力叙事) 是否被媒体差异化解读的直接测度。

【方法学与计算】
计算链路自下而上分三层。第一层 (stage 21 `tone_llms.py`): 对留篇门控 (`llm_verified_full==True`, full-only 口径, 2026-06-29 起生效) 通过的每篇文章, 三家 LLM 各自输出 `{short}_score{track} ∈ {-1,0,1}` 逐篇标签; 三家投票后聚合为文章级 `llm_vote_score{track}` (多数一致取该值, 否则记 0)。第二层 (同一文章级表): `innovation_collab_mode` 分类器 (独立于语调判定) 把每篇文章标注为 indep / collab / NaN 三态, NaN 代表该维度 LLM 分类失败或不适用 (未回填的机器拒答), 既不进 `_indep` 也不进 `_collab` 分母, 由 `n_articles_cell_NA_full` 兜底可核; 这解释了源码里 `n_articles >= n_articles_indep + n_articles_collab` 只是逻辑必然性弱等式而非恒等式 (2026-06-11 收敛到 `_check_partition_identity`)。第三层 (panel 聚合, `encode.py`): 关键机制是"子样本成员资格恒由 `_full` 轨判定、语调数值各轨自算" — 源码用 `innovation_collab_mode_full == '自主研发'` (唯一判据, 而非逐轨各判) 掩码筛出子样本 `df_cm`, 再在该同一批文章内, 对 `llm_vote_score{track}` (`track ∈ {_full, _ctx, _ss}`) 分别取算术均值, 写入 `llm_vote_tone_indep{track}`; 也就是说 `llm_vote_tone_indep_ctx`/`llm_vote_tone_indep_ss` 的"谁算 indep 文章"这一样本归属判定并不按 `_ctx`/`_ss` 轨自身文本重新分类, 而是统一沿用 `_full` 轨的 collab_mode 分类结果, 只有落在该子样本内的文章各轨语调标签才各自独立取均值。这与源码同一代码块内另外产出的 track-specific 版本 `llm_vote_tone_indep_cm_ctx`/`llm_vote_tone_indep_cm_ss` (由 `innovation_collab_mode_ctx`/`innovation_collab_mode_ss` 各自逐轨判定成员资格, 属另一家族) 是两套不同列, 不可混淆。 分母为该 bank-year 内 indep 子样本文章数 (即 `n_articles_indep`, 与 `indep_frac = n_articles_indep / n_articles_llm_valid` 共享同一计数口径)。因此本列既继承了三家 LLM 投票共识的测度不确定性, 又叠加了 collab_mode 分类的二次筛选不确定性; 两层任一环节样本量不足 (小 T、稀疏 indep 报道) 都会放大 bank-year 层面的抽样噪声, 这也是为何下游 `tone_gap_indep_collab = llm_vote_tone_indep_full - llm_vote_tone_collab_full` 要求 `n_articles_indep >= 5 且 n_articles_collab >= 5` 才计入 (对齐 `tech_app`/`sub_symb` 的 min-n≥5 守门惯例), 未达标记为 NaN 而非强行输出噪声估计。三轨语义遵循全仓统一口径: `_full` = 标题+全文正文, `_ctx` = 标题+银行/金科实体窗口, `_ss` = 标题+银行∧金科同句 (默认 ±1 句半径) 共现窗口, 三者对 `content_ss` 缺共现时回退全文 body 并置 `ss_is_fallback=True` (镜像 `_ctx` 回退语义, 共享 `n_articles` 分母)。留篇门控口径已切换为 full-only: 一篇文章是否计入"银行金科报道"只看 `llm_verified_full==True`, ctx/ss 轨是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集, 但 per-track 列各自独立计算, 不借用彼此的均值。

【文献定位】
本家族方法学上直接落在"LLM 多数投票作为文本情感标注一致性机制"这一新兴文献脉络上。Kamen & Kamen (2025) 系统论证了多模型集成投票在内容分类任务上相较单模型更稳健, 是 `llm_vote_tone` 命名与设计思路 (多数一致才计非零标签, 弃权而非强制单模型判定) 的直接方法学锚点。de Kok (2025, *Management Science*) 提出的 temperature=0 / prompt 版本冻结 / 缓存复现范式, 是本仓库 stage 21 缓存键 (`prompt_version='v8-2026-05-17'`, `temperature=0.0`) 与三轨 0-miss 离线可复现设计的方法论依据, 该刊亦属本仓库顶刊清单锚点之一。构念层面, Du, Huang, Wermers & Wu (2022, *Review of Finance*) 建立的中文金融情感词典基准, 是本仓库全部中文金融文本语调测度族 (含 LLM 轨与词典轨) 共同对标的构念定义源, 亦是本仓库唯一的政治词权重敏感性锚点; 本家族虽走 LLM 路线而非词典路线, 但共享"媒体语调作为企业融资/声誉信号"这一底层构念, 与 Tetlock (2007, *Journal of Finance*) 开创的"媒体语调预测市场反应"框架及 Holzman, Miller & Twedt (2023, *The Accounting Review*) 的媒体权威加权语调设计一脉相承。协作模式 (`indep` vs `collab`) 切分本身的理论根基并非泛化的金融科技颠覆力量综述, 而是 Chesbrough (2003) 提出的开放式创新 (Open Innovation) 概念——企业既可依赖内部知识独立创新 (对应 `indep`), 亦可通过与外部行为体缔结合作关系获取、整合外部知识 (对应 `collab`)——以及 Laursen & Salter (2006, *Strategic Management Journal*) 对企业外部知识搜寻广度/深度的实证操作化, 二者共同构成 encode.py 源码注释中显式标注的分类依据。Zhang, Ma, Liang & Garrett (2024, *Journal of Product Innovation Management*) 对开放式创新前因后果近 20 年文献所做的框架性元分析, 是本列 indep/collab 二分类判据在该理论脉络下的当代文献坐标, 佐证"内生自主研发 vs. 外部协同"这一二分在开放式创新文献中已是被反复验证的稳定构念区分, 而非本仓库自行发明。

## VAR: llm_vote_tone_indep_ctx

【变体差分】
本列是三轨中的 `_ctx` (实体窗口) 轨: 上游文章级语调判定所消费的文本是 stage 14 `ctx_materializer` 物化的 `content_ctx` (标题 + 银行/金科相关实体所在窗口拼接, `prepend_title` 已内嵌标题, 非独立标题轨), 而非全文正文。与 `_full` 轨相比, `_ctx` 剔除了文章中与目标银行/金科实体不直接相关的背景段落 (如宏观经济综述、无关业务条线报道), 理论上降低了噪声但也可能丢失上下文语调线索 (如"尽管行业承压, 但该行金科业务表现亮眼"这类需要跨句语境才能判读的正确极性)。留篇门控口径 (2026-06-29 起) 已切换为 full-only, 即一篇文章是否计入分母 (`n_articles_indep`) 由 `llm_verified_full` 决定, `_ctx` 轨的行宇宙是该 full 留篇集的子集。此外须注意本列的"indep 子样本成员资格"本身也统一沿用 `_full` 轨判定: encode.py 用 `innovation_collab_mode_full == '自主研发'` (而非 `innovation_collab_mode_ctx`) 筛出子样本 `df_cm`, `llm_vote_tone_indep_ctx` 只是在该同一批文章内改用 `_ctx` 轨自身的逐篇语调标签取均值, 不借用 `_full` 轨的语调数值——但样本"谁在 indep 里"这件事恒由 `_full` 轨决定。若需要 `_ctx` 轨自身文本重新判定 collab_mode 归属的版本, 对应列是另一家族的 `llm_vote_tone_indep_cm_ctx` (由 `innovation_collab_mode_ctx` 逐轨判定成员资格), 与本列是两套不同测度, 不可混淆。本列与 `_full`/`_ss` 两轨在测度设计上是各自 just-identified 并排的互为稳健性测度, 三者互不构成主次关系, 严禁把三轨同时塞进同一个 over-identified Hansen J 过度识别检验 (三轨各自独立进 GMM/IV 稳健性对照表, 不共享同一组矩条件)。`content_ctx` 若该文章无法定位有效实体窗口, 按全仓统一规则回退为全文 body 并标记 `ctx_is_fallback=True` (与 `_ss` 回退共享 `n_articles` 分母口径, 见家族 CORE)。作为 P1 主线的一条条件测度轨, `_ctx` 常被用于交叉验证 `_full` 轨的结论在剔除无关背景段落后是否依然成立, 尤其适合诊断"标题党"或"长篇通稿夹带一句银行金科相关信息"这类可能污染 `_full` 轨语调的情形。

## VAR: llm_vote_tone_indep_full

【变体差分】
本列是三轨中的 `_full` (标题+全文正文) 轨, 是本仓库三轨架构里的默认/主口径文本窗口, 也是全仓留篇门控唯一依据的轨: 是否判定"这是一篇有效的银行金科报道"只看 `llm_verified_full == True` (2026-06-29 起的 full-only 门控口径), 因此 `n_articles_indep` 这一分母、以及 `indep_frac` 计数均以 `_full` 轨的判定结果为准, `_ctx`/`_ss` 两轨是在该 full 留篇集之上的条件测度轨 (conditional-on-full), 行宇宙是其子集。本列还有一层特殊性: encode.py 判定"某篇文章是否属于 indep 子样本"的分类依据 `innovation_collab_mode_full == '自主研发'` 本身就是 `_full` 轨的分类结果, 因此对 `_full` 轨而言, "留篇门控轨"与"子样本成员资格判定轨"恰好重合于同一个 `_full` 后缀; 但这只是巧合式重合, 并非"因为是 full 轨所以门控更权威"——`_ctx`/`_ss` 两轨的语调数值同样各自独立取自对应轨的逐篇标签, 只是其子样本成员资格 (谁算 indep) 依旧沿用这同一个 `innovation_collab_mode_full` 判据, 而非各自轨的 `innovation_collab_mode_ctx`/`innovation_collab_mode_ss`。就语调数值本身而言, `llm_vote_tone_indep_full` 由三家 LLM 各自读取全文正文 (含标题, `prepend_title` 拼接) 逐篇判定情感极性、多数投票后取 indep 子样本 bank-year 均值得到, 未做任何实体窗口或同句共现的裁剪, 因此最大程度保留了文章通篇的语境信息, 代价是可能混入与目标银行/金科业务无关的段落语调 (如文章末尾的行业展望、无关的其他银行动态), 引入测度噪声。作为 P1 (`bank_fintech_tone`) 与 P5 (`bank_fintech_collab`, provisional) 两条论文线的 headline treatment 分支所依赖的口径 (`llm_vote_tone_full` 的 indep 切片), 本列在稳健性表中通常作为默认列呈现, 但按家族 CORE 所述的三轨并排原则, 它与 `_ctx`/`_ss` 两轨仍是互为稳健性、不分主次的并列测度, 不因"门控依据"这一角色而在识别策略意义上高于另外两轨——三者依旧各自 just-identified, 不得混入同一个 over-identified 的 Hansen J 检验。

## VAR: llm_vote_tone_indep_ss

【变体差分】
本列是三轨中的 `_ss` (银行∧金科同句共现) 轨: 上游消费的文本是 stage 14 物化的 `content_ss`, 判定口径比 `_ctx` 更严格——要求目标银行与金融科技相关词汇出现在同一句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 参数, 默认 ±1 句窗口, 该键与 stage 13 `cooccurrence_filter.sentence_radius` 是两个语义相邻但取值/用途独立的不同配置键, 不可混用), 是三轨中窗口最窄、信噪比理论上最高但也最容易因无同句共现而触发回退的一轨。`_ss` 的回退语义严格镜像 `_ctx`: 若某篇文章不存在银行∧金科同句共现, `content_ss` 直接回退为全文 body, 并置 `ss_is_fallback=True`, 与 `ctx_is_fallback` 共享同一个 `n_articles` 分母、不额外抽样。`llm_vote_tone_indep_ss` 的计算是在 indep 子样本行宇宙内, 对 `_ss` 轨自身产出的逐篇三家 LLM 多数投票标签取 bank-year 均值, 与 `_full`/`_ctx` 两列各自独立运算、互不借用彼此的语调中间量; 但与 `_ctx` 轨同理, "谁属于 indep 子样本"这一成员资格判定并不按 `_ss` 轨自身文本重新分类, 而是统一沿用 `innovation_collab_mode_full == '自主研发'` 这一 `_full` 轨判据, `_ss` 轨只贡献语调数值不贡献样本划分。真正按 `_ss` 轨自身文本重判 collab_mode 归属的是另一家族列 `llm_vote_tone_indep_cm_ss` (由 `innovation_collab_mode_ss` 逐轨判定), 与本列口径不同, 不可混淆。由于 `_ss` 窗口最窄, 在 indep 子样本 (本身已是协作模式二分类下的稀疏切片) 中触发 `ss_is_fallback=True` 的比例通常高于全样本, 小样本 (如本机 T=2 开发盘) 下该列方差可能呈现退化 (如与 `_full` 高度重合甚至恒等), 属预期而非缺陷, 生产语料 (T=18, 千万级文章量) 下三轨才能充分展现差异化的信噪比权衡; 该轨与另外两轨依旧是各自 just-identified 并排、互为稳健性不分主次的关系, 禁止混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
<!-- rendered-citations:end -->
