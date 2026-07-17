---
family_id: F441
columns:
- modal_strong_frac_ctx
- modal_strong_frac_full
- modal_strong_frac_ss
unit: 词频占比 (proportion, 无量纲, 理论域 [0,1]; 文章级比率经银行-年均值聚合入面板)
formula: "modal_strong_frac_{trk} = n_modal_strong_{trk} / n_word_tokens_{trk}; n_modal_strong = 命中 LM 2011 strong_modal 子词典 (54 词, 经 _SUBSET_SOURCE 映射为 modal_strong 键) 的 token 数, n_word_tokens = 剔除纯数字与标点后的真词 token 数 (jieba 切分); trk ∈ {full, ctx, ss}"
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
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
new_dois: []
---

## CORE

【构念与来源】
本家族 modal_strong_frac 度量的是"强势模态"(strong modal) 语义在一篇银行金融科技报道文本中的词频占比, 是 Loughran & McDonald (2011) 在 Journal of Finance 上提出的 10-K 文本非极性 (non-sentiment) 词典体系里六个子类之一在中文语料上的落地。强势模态词指向不容置疑、必然发生或高度确信的措辞, 典型语义包括必将、一定、始终、务必、坚决、绝不改变等表达确定性与承诺力度的用词; 与之相对的是同一词典体系内的弱势模态子类 (modal_weak, 另成一族), 二者共同构成 Loughran & McDonald 原始 6 类模态强度的对仗轴。模态强度与情感极性 (正面/负面) 是两个正交维度: 一句话既可以用强势模态表达正面承诺 ("坚决支持"), 也可以用强势模态表达负面警示 ("绝不姑息"), 强势模态只刻画措辞的确定性程度, 不携带方向信息。Loughran & McDonald (2011) 在 Journal of Finance 上论证通用词典在金融语境下会把大量中性、程序性用语误判为负面, 必须用领域专属词典重新界定语义类别; 强势/弱势模态正是该文在负面/正面二元之外划出的非极性类别之一, 用以单独捕捉措辞的确信/断言强度而非情感方向, 这为把模态强度作为一条与语气正交的面板协变量单列提供了直接的方法学理据。Bochkay, Brown, Leone & Tucker (2023) 在 Contemporary Accounting Research 的综述中把会计与财务文本分析方法统一组织为"词典法 → 词袋机器学习 → 上下文化预训练语言模型"的演进框架, 并指出词典法子类别 (如模态强度) 因其透明、可审计、零训练成本, 在与统计学习方法并行时仍具独立价值, 这为本项目在 stage 21 (LLM) / 23 (BERT) 之外仍保留 stage 22 词典法非极性子类作为并行测度而非被取代的基准提供了综述级理据。本项目据此把强势模态词频作为一条与语气正交的文本硬度/确信度信号纳入银行-年面板, 用以刻画媒体报道在描述银行金融科技活动时所呈现的斩钉截铁程度, 可用于检验措辞确信度是否影响读者/市场对银行金融科技战略的感知与后续融资、合作等结果。

【方法学与计算】
计算在文章级完成, 三轨集成入口 _dual_analyze 位于 tone_words.py, 它对 content_full / content_ctx / content_ss 三条轨道各调用一次的实际接线函数是 tone_words.py 内的同语义包装 _compute_lm_non_sentiment_for_text_tone_tok; 该包装与只读模块 lm_non_sentiment.py 的 _compute_lm_non_sentiment_for_text 逐项同语义 (共用同一 strong_modal 子词典与命中口径), 只读模块函数供审计参照, 并非 _dual_analyze 直接调用的实体。子词典的键名存在一处历史命名不对称: LM 原始类别键用 strong_modal/weak_modal, 而本模块内部子集标识沿用 modal_strong/modal_weak, 二者经模块内 _SUBSET_SOURCE 映射表对应, 面板列名最终采用 modal_strong_frac 这一形式。分子 n_modal_strong 为文本经 jieba 切分后命中 strong_modal 子词典的 token 计数 (中文实现共 54 词, 系 2026-06-18 依用户 directive 替代原 314 词手工 stub 的 325-agent 审计全本翻译产物; 该 54 词/325-agent 数字是代码库内部工程维护记录 lm_non_sentiment.py 注释所载的施工口径, 非外部文献可查证的统计量, 不作为文献引用支持); 分母 n_word_tokens 为剔除纯数字与纯标点 token 后的真词 token 总数, 这一分母口径经过审计校正 (lmfls-01, 2026-06-10): 早期分母含逗号、句号与纯数字 token, 约占全部 token 的近两成, 导致各子类占比被系统性下偏; 现分母只数含字母或汉字的真词 token, 分子不变, 仅使比例回归无偏。文章级比率再经 tone_words 聚合 (银行-年均值) 落入面板列 modal_strong_frac_{full,ctx,ss}。强势模态词频与本词典体系另外五个子类 (uncertainty / litigious / constraining / modal_weak / complexity, 各自成族) 共享同一切分与分母口径, 但分子取各自子词典, 互不重叠; 该 LM 非极性 6 子类是 v3.10.0 由原 4 子类扩为 6 子类的结果 (新增 weak_modal 与 complexity)。

【文献定位】
在财经文本的语言强度与词典法方法论脉络中, Loughran & McDonald (2011) 本身在 Journal of Finance 上确立了强势/弱势模态子类的原始定义与 10-K 文本命中口径, 是整套 6 子类非极性词典体系 (包括本家族) 的方法学源头, 也是本家族最贴近的顶刊构念锚点。Bochkay, Brown, Leone & Tucker (2023) 于 Contemporary Accounting Research 的综述把词典法置于"词典 → 机器学习 → 上下文化预训练语言模型"演进谱系中定位, 说明模态强度这类透明、可审计的词典子类在与统计学习方法并行比较时仍具方法学存在价值, 支撑本项目词典 (stage 22) / BERT (stage 23) / LLM (stage 21) 三法并行而非相互取代的总体测度架构。约束与融资约束测量脉络方面, Buehlmaier & Whited (2018) 于 Review of Financial Studies 用文本分析构造融资约束指标并证明其被资产定价, 为"确信度/硬度类语义可从公开文本抽取并具信息含量"这一更一般命题提供了顶刊层面的佐证; Liu, Zhang & Wu (2026) 用机器学习从年报前瞻性陈述中识别融资约束, 说明相邻语义类别的文本信号在中文披露语境下仍具预测力; Xu & Luo (2025) 于 Finance Research Letters 研究控股股东股权质押场景下的融资约束与企业社会责任披露, 其设定同样落在"披露文本中的确信/承诺语气与融资约束状态相关联"这一更宽的构念脉络内, 提示强势模态占比作为确信度信号在中国上市公司/银行披露语境下的外部效度并非孤例。词典本身的中文可迁移性方面, Ma, Zhang & Zhang (2025) 构造面向中国投资者的细粒度中文情感词典, Lu 等 (2023) 的 BBT-Fin 提供中文金融领域预训练语料与基准, 二者共同界定了在中文财经文本上做词典化测度的可行边界与已知误差来源, 对本家族 54 词强势模态子词典的中文翻译质量与覆盖边界具有方法学参照意义。强势模态词频作为一条与语气正交的信号, 其价值恰在于不被情感极性驱动, 而是独立刻画报道措辞的确信/断言强度。三轨口径下 (full/ctx/ss), 三条轨道各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一条 over-identified 的 Hansen J 检验; 面板行宇宙由 full-only 留篇门控 (2026-06-29) 界定, ctx 与 ss 为 conditional-on-full 的稳健性轨。

## VAR: modal_strong_frac_full

【变体差分】
本列为全文轨 (full) 的强势模态词频占比。full 轨的文本 = 标题 prepend 到正文之前再拼接的全篇报道 body (content_full), 即在 stage 14 ctx_materializer 物化时把原始标题前置到正文, 覆盖整篇文章而非任何实体窗口。在三轨体系中 full 轨承担特殊地位: 它是面板留篇门控的唯一判据 (full-only, 2026-06-29) —— 一篇报道是否被判为"银行金融科技报道"并进入银行-年面板行宇宙, 只看该文的 full 轨 LLM 判定, 因此 full 轨也是强势模态词频信息量最充分、分母最大的轨道 (覆盖全文所有真词 token)。相对 ctx 与 ss, full 轨不做实体邻近或同句裁剪, 语义覆盖最广, 能捕捉全文整体的确信语气, 但也最易被与银行金融科技无直接关系的段落 (如行业背景、宏观政策转述) 稀释。full 与 ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一条 over-identified Hansen J; 主分析通常以 full 轨为首要读数, ctx/ss 作 conditional-on-full 的稳健性对照。分母采用剔除纯数字与标点后的真词 token 数 (lmfls-01 校正口径), 分子为命中 strong_modal 54 词子词典的 token 数。这里的三轨后缀是银行金融科技共现口径下的文本裁剪维度, 与结构网络指标所用的判据后缀 (同篇/句窗/同句) 是两个正交的概念空间, 二者不可混淆亦不可互相复用; modal_strong_frac 家族只沿三轨文本维度分列, 不再叠加判据维度。full 轨因覆盖全文, 在生产语料 (T=19) 上分母最稳、缺失最少, 是本家族在时序上信息量最充分的一列; 在开发语料 (T=2) 的极小样本上, full 轨仍能给出非退化读数, 而 ctx/ss 更易出现零方差或大量回退。

## VAR: modal_strong_frac_ctx

【变体差分】
本列为实体上下文轨 (ctx) 的强势模态词频占比。ctx 轨的文本 = 标题 prepend 加上正文中目标银行实体邻近窗口内的内容 (content_ctx), 相较 full 轨把语义范围收窄到与银行实体真正共现的局部段落, 目的在于滤除全文里与银行金融科技活动无关的噪声, 使模态强度的测量更贴近报道对该银行的具体表述确信程度。因此在同一篇文章上, ctx 轨的分母 (真词 token 数) 通常小于 full 轨, 强势模态占比对局部措辞更敏感、波动更大。ctx 轨为 conditional-on-full 的测度轨: 只在该文已由 full 轨门控留篇后, 才对其 ctx 文本单独计算本列; 若 ctx 文本触发回退 (ctx_is_fallback), 则退化为对应的全文口径。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一条 over-identified Hansen J 检验; ctx 常作为 full 轨结论的首要稳健性对照。分子分母口径与家族一致 (strong_modal 54 词命中数 / 真词 token 数, lmfls-01 校正分母)。ctx 轨的设计意图是回答一个与 full 轨略有差别的问题: 当报道把镜头对准该银行本身时, 其措辞的确信/断言强度如何, 而非整篇文章 (可能含大量其它主体或背景陈述) 的平均模态语气; 在同一篇多主体报道上, ctx 与 full 的读数可能明显背离, 这种背离本身具有信息量, 也正是把两轨并排作互为稳健性对照的意义所在。实现上, ctx 文本在 stage 14 与 ss 文本一并物化, 使 stage 15/16 等下游在情感 stage 21 之前即可消费真三轨文本; 若某文 ctx 触发回退, 本列退化为对应全文口径并由 ctx_is_fallback 标记, 面板聚合时与家族共享 n_articles 分母, 不制造单边孤儿列。

## VAR: modal_strong_frac_ss

【变体差分】
本列为同句共现轨 (ss) 的强势模态词频占比。ss 轨的文本 = 标题 prepend 加上正文中银行与金融科技词同句共现且落在句子半径窗口内的内容 (content_ss, 窗口由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。ss 轨是三轨中语义最聚焦的一条, 只保留银行与金科真正同句发生关系的片段, 从而把模态强度测量锁定在报道对"该银行的金融科技"这一交汇点的具体断言口吻上。ss 轨的回退语义镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True (与家族共享 n_articles 分母); 当金科自动机 FINTECH_AC 为 None 时, 所有轨的 fallback 标记优雅置 True, 整体降级而非静默清空。因此 ss 轨在同句共现稀疏的语料上分母偏小、缺失更多, 属预期退化。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一条 over-identified Hansen J; ss 为 conditional-on-full 的最聚焦稳健性轨。分子分母口径与家族一致 (strong_modal 54 词命中数 / 真词 token 数)。ss 轨回答的是三轨中最狭窄也最直接的问题: 在报道明确把该银行与金融科技放在同一句话里讨论的那些片段中, 措辞的斩钉截铁程度有多强。由于这一裁剪把与"该银行的金融科技"无直接语法邻接的内容全部剔除, ss 轨对报道就该交汇点表达的确信、承诺或不容置疑口吻最为敏感, 但代价是样本文本量最小、缺失与回退最多, 在同句共现稀疏的语料或极小样本上退化最明显。需要再次区分: ss 轨的同句半径 (ss_sentence_radius) 与 stage 13 共现硬过滤的 sentence_radius 是两个不同的配置键, 分属不同判定原语, 互不联动、禁互相复用。ss 与 full、ctx 三轨在计量上各自 just-identified 并排, 只能作为并列的规格稳健性对照, 绝不并入同一条 over-identified Hansen J。

<!-- rendered-citations:begin -->
Liu, T., Zhang, J., & Wu, J. (2026). Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach. The International Journal of Accounting, 61(1), 2550006. https://doi.org/10.1142/S1094406025500064
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Xu, J., & Luo, Q. (2025). Controlling shareholder equity pledging, financing constraints, and corporate social responsibility. Finance Research Letters, 76, 106996. https://doi.org/10.1016/j.frl.2025.106996
Lu, D., Wu, H., Liang, J., Xu, Y., He, Q., Geng, Y., Han, M., Xin, Y., & Xiao, Y. (2023). BBT-Fin: Comprehensive construction of Chinese financial domain pre-trained language model, corpus and benchmark. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2302.09432
Buehlmaier, M. M. M., & Whited, T. M. (2018). Are financial constraints priced? Evidence from textual analysis. Review of Financial Studies, 31(7), 2693-2728. https://doi.org/10.1093/rfs/hhy007
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next? Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
<!-- rendered-citations:end -->
