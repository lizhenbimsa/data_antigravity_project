---
family_id: F163
columns:
- constr_frac_ctx
- constr_frac_full
- constr_frac_ss
unit: 词频占比 (proportion, 无量纲, 理论域 [0,1]; 文章级比率经银行-年均值聚合入面板)
formula: "constr_frac_{trk} = n_constr_{trk} / n_word_tokens_{trk}; n_constr = 命中 LM 2011 constraining 子词典 (174 词) 的 token 数, n_word_tokens = 剔除纯数字与标点后的真词 token 数 (jieba 切分); trk ∈ {full, ctx, ss}"
producer: news_process/pipeline/sentiment/tone_words.py::_compute_lm_non_sentiment_for_text_tone_tok (由 pipeline/sentiment/tone_words.py::_dual_analyze 三轨集成调用; 与只读模块 pipeline/sentiment/lm_non_sentiment.py::_compute_lm_non_sentiment_for_text 逐项同语义)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet
citations:
- doi: 10.1142/S1094406025500064
  type: journal
  authors: Liu, T., Zhang, J., & Wu, J.
  year: 2026
  title: "Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach"
  venue: The International Journal of Accounting
  vol: 61
  issue: 1
  pages_or_artno: 2550006
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.frl.2025.106996
  type: journal
  authors: Xu, J., & Luo, Q.
  year: 2025
  title: "Controlling shareholder equity pledging, financing constraints, and corporate social responsibility"
  venue: Finance Research Letters
  vol: 76
  pages_or_artno: 106996
- doi: 10.48550/arXiv.2302.09432
  type: arxiv
  authors: Lu, D., Wu, H., Liang, J., Xu, Y., He, Q., Geng, Y., Han, M., Xin, Y., & Xiao, Y.
  year: 2023
  title: "BBT-Fin: Comprehensive construction of Chinese financial domain pre-trained language model, corpus and benchmark"
  venue: arXiv
  pages_or_artno: 2302.09432
- doi: 10.1093/rfs/hhy007
  type: journal
  authors: Buehlmaier, M. M. M., & Whited, T. M.
  year: 2018
  title: "Are financial constraints priced? Evidence from textual analysis"
  venue: Review of Financial Studies
  vol: 31
  issue: 7
  pages_or_artno: 2693-2728
new_dois: []
---

## CORE

【构念与来源】
本家族 constr_frac 度量的是"约束"(constraining) 语义在一篇银行金融科技报道文本中的词频占比, 是 Loughran & McDonald (2011) 在 Journal of Finance 上提出的 10-K 文本非极性 (non-sentiment) 词典体系里六个子类之一在中文语料上的落地。约束类词汇指向对企业行为形成硬性限制、绑定或不可回旋的表述, 典型语义包括受限、必须、不得、强制、绑定、义务、契约条款等; 与情感极性 (正面/负面) 不同, 约束词刻画的是文本所披露的经营与融资"回旋余地"被压缩的程度。Loughran & McDonald (2011) 的核心发现是: 通用心理学词典 (如 Harvard IV-4) 在财经文本上大量误判, 财经语境需要专门词典, 而非极性子类 (uncertainty / litigious / constraining / modal / complexity) 携带的信息与纯情感极性正交, 能独立预测市场反应与企业结果。本项目据此把约束词频作为一条与语气 (tone) 正交的文本硬度信号纳入银行-年面板, 用以刻画媒体报道在描述银行金融科技活动时所呈现的受限、合规压力与承诺刚性语气强度。

【方法学与计算】
计算在文章级完成, 三轨集成入口 _dual_analyze 位于 tone_words.py, 它对 content_full / content_ctx / content_ss 三条轨道各调用一次的实际接线函数是 tone_words.py 内的同语义包装 _compute_lm_non_sentiment_for_text_tone_tok; 该包装与只读模块 lm_non_sentiment.py 的 _compute_lm_non_sentiment_for_text 逐项同语义 (共用同一 constraining 子词典与命中口径), 只读模块函数供审计参照, 并非 _dual_analyze 直接调用的实体。分子 n_constr 为文本经 jieba 切分后命中 constraining 子词典 (中文实现共 174 词) 的 token 计数; 分母 n_word_tokens 为剔除纯数字与纯标点 token 后的真词 token 总数。此处分母口径是一处经过审计校正的关键约定 (lmfls-01, 2026-06-10): 早期分母含逗号、句号与纯数字 token, 约占全部 token 的近两成, 导致约束占比被系统性下偏; 现分母只数含字母或汉字的真词 token, 分子不变 (词典词均为真词, 标点与数字本就不命中), 仅使比例回归无偏。文章级比率再经 tone_words 聚合 (银行-年均值) 落入面板列 constr_frac_{full,ctx,ss}。约束词频与本词典体系另外五个子类 (uncertainty / litigious / modal_strong / modal_weak / complexity, 各自成族) 共享同一切分与分母口径, 但分子取各自子词典, 互不重叠; 该 LM 非极性 6 子类是 v3.10.0 由原 4 子类扩为 6 子类的结果 (新增 weak_modal 与 complexity)。

【文献定位】
在财经文本的约束/融资约束测量脉络中, Buehlmaier & Whited (2018) 于 Review of Financial Studies 直接以文本分析构造融资约束指标并证明其被资产定价, 为"约束语义可从公开文本中抽取并具信息含量"提供了顶刊层面的方法学与经济学锚点, 与本家族以词频占比抽取约束语气的思路同源。Liu, Zhang 与 Wu (2026) 进一步用机器学习从年报前瞻性陈述中识别融资约束, 说明约束相关文本信号在中文披露语境下仍可预测企业融资约束状态, 支持把此类词频信号纳入面板。Xu 与 Luo (2025) 记录了控股股东股权质押与融资约束、企业社会责任的关联, 为约束语气作为企业外部环境代理的经济意义提供背景。词典本身的中文可迁移性方面, Ma, Zhang 与 Zhang (2025) 构造面向中国投资者的细粒度中文情感词典, 而 Lu 等 (2023) 的 BBT-Fin 提供中文金融领域预训练语料与基准, 二者共同界定了在中文财经文本上做词典化与嵌入化测度的可行边界与已知误差来源。约束词频作为一条与语气正交的信号, 其价值恰在于不被情感极性驱动, 而是独立刻画报道所披露的刚性与受限强度。三轨口径下 (full/ctx/ss), 三条轨道各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一条 over-identified 的 Hansen J 检验; 面板行宇宙由 full-only 留篇门控 (2026-06-29) 界定, ctx 与 ss 为 conditional-on-full 的稳健性轨。

## VAR: constr_frac_full

【变体差分】
本列为全文轨 (full) 的约束词频占比。full 轨的文本 = 标题 prepend 到正文之前再拼接的全篇报道 body (content_full), 即在 stage 14 ctx_materializer 物化时把原始标题前置到正文, 覆盖整篇文章而非任何实体窗口。在三轨体系中 full 轨承担特殊地位: 它是面板留篇门控的唯一判据 (full-only, 2026-06-29) —— 一篇报道是否被判为"银行金融科技报道"并进入银行-年面板行宇宙, 只看该文的 full 轨 LLM 判定, 因此 full 轨也是约束词频信息量最充分、分母最大的轨道 (覆盖全文所有真词 token)。相对 ctx 与 ss, full 轨不做实体邻近或同句裁剪, 语义覆盖最广但也最易被与银行金融科技无直接关系的段落稀释。full 与 ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一条 over-identified Hansen J; 主分析通常以 full 轨为首要读数, ctx/ss 作 conditional-on-full 的稳健性对照。分母采用剔除纯数字与标点后的真词 token 数 (lmfls-01 校正口径), 分子为命中 constraining 174 词子词典的 token 数。需要强调的是, 这里的三轨后缀是银行金融科技共现口径下的文本裁剪维度, 与结构网络指标所用的判据后缀 (同篇/句窗/同句) 是两个正交的概念空间, 二者不可混淆亦不可互相复用; constr_frac 家族只沿三轨文本维度分列, 不再叠加判据维度。full 轨因覆盖全文, 在生产语料 (T=18) 上分母最稳、缺失最少, 是本家族在时序上信息量最充分的一列; 在开发语料 (T=2) 的极小样本上, full 轨仍能给出非退化读数, 而 ctx/ss 更易出现零方差或大量回退。因此把 full 轨作为主读数, 既符合留篇门控口径, 也与其统计稳定性一致。

## VAR: constr_frac_ctx

【变体差分】
本列为实体上下文轨 (ctx) 的约束词频占比。ctx 轨的文本 = 标题 prepend 加上正文中目标银行实体邻近窗口内的内容 (content_ctx), 相较 full 轨把语义范围收窄到与银行实体真正共现的局部段落, 目的在于滤除全文里与银行金融科技活动无关的噪声, 使约束语气的测量更贴近报道对该银行的具体表述。因此在同一篇文章上, ctx 轨的分母 (真词 token 数) 通常小于 full 轨, 约束占比对局部措辞更敏感、波动更大。ctx 轨为 conditional-on-full 的测度轨: 只在该文已由 full 轨门控留篇后, 才对其 ctx 文本单独计算本列; 若 ctx 文本触发回退 (ctx_is_fallback), 则退化为对应的全文口径。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一条 over-identified Hansen J 检验; ctx 常作为 full 轨结论的首要稳健性对照。分子分母口径与家族一致 (constraining 174 词命中数 / 真词 token 数, lmfls-01 校正分母)。ctx 轨的设计意图是回答一个与 full 轨略有差别的问题: 当报道把镜头对准该银行本身时, 其措辞的约束/受限强度如何, 而非整篇文章 (可能含大量行业背景、宏观政策或其它主体) 的平均约束语气。因此在同一篇多主体报道上, ctx 与 full 的读数可能明显背离, 这种背离本身是有信息量的, 也正是把两轨并排作互为稳健性对照的意义所在。实现上, ctx 文本在 stage 14 与 ss 文本一并物化, 使 stage 15/16 等下游在情感 stage 21 之前即可消费真三轨文本; 若某文 ctx 触发回退, 本列退化为对应全文口径并由 ctx_is_fallback 标记, 面板聚合时与家族共享 n_articles 分母, 不制造单边孤儿列。

## VAR: constr_frac_ss

【变体差分】
本列为同句共现轨 (ss) 的约束词频占比。ss 轨的文本 = 标题 prepend 加上正文中银行与金融科技词同句共现且落在句子半径窗口内的内容 (content_ss, 窗口由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。ss 轨是三轨中语义最聚焦的一条, 只保留银行与金科真正同句发生关系的片段, 从而把约束语气测量锁定在报道对"该银行的金融科技"这一交汇点的具体描述上。ss 轨的回退语义镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True (与家族共享 n_articles 分母); 当金科自动机 FINTECH_AC 为 None 时, 所有轨的 fallback 标记优雅置 True, 整体降级而非静默清空。因此 ss 轨在同句共现稀疏的语料上分母偏小、缺失更多, 属预期退化。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一条 over-identified Hansen J; ss 为 conditional-on-full 的最聚焦稳健性轨。分子分母口径与家族一致 (constraining 174 词命中数 / 真词 token 数)。ss 轨回答的是三轨中最狭窄也最直接的问题: 在报道明确把该银行与金融科技放在同一句话里讨论的那些片段中, 约束/受限语气有多强。由于这一裁剪把与"该银行的金融科技"无直接语法邻接的内容全部剔除, ss 轨对报道口吻中就该交汇点表达的合规压力、承诺刚性或政策约束最为敏感, 但代价是样本文本量最小、缺失与回退最多, 在同句共现稀疏的语料或极小样本上退化最明显。需要再次区分: ss 轨的同句半径 (ss_sentence_radius) 与 stage 13 共现硬过滤的 sentence_radius 是两个不同的配置键, 分属不同判定原语, 互不联动、禁互相复用。ss 与 full、ctx 三轨在计量上各自 just-identified 并排, 只能作为并列的规格稳健性对照, 绝不并入同一条 over-identified Hansen J。

<!-- rendered-citations:begin -->
Liu, T., Zhang, J., & Wu, J. (2026). Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach. The International Journal of Accounting, 61(1), 2550006. https://doi.org/10.1142/S1094406025500064
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Xu, J., & Luo, Q. (2025). Controlling shareholder equity pledging, financing constraints, and corporate social responsibility. Finance Research Letters, 76, 106996. https://doi.org/10.1016/j.frl.2025.106996
Lu, D., Wu, H., Liang, J., Xu, Y., He, Q., Geng, Y., Han, M., Xin, Y., & Xiao, Y. (2023). BBT-Fin: Comprehensive construction of Chinese financial domain pre-trained language model, corpus and benchmark. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2302.09432
Buehlmaier, M. M. M., & Whited, T. M. (2018). Are financial constraints priced? Evidence from textual analysis. Review of Financial Studies, 31(7), 2693-2728. https://doi.org/10.1093/rfs/hhy007
<!-- rendered-citations:end -->
