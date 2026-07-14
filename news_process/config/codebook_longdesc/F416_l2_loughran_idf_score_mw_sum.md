---
family_id: F416
novelty_exempt_rationale: "该家族是 loughran_idf_score 的媒体权威加权 (MW) 求和分子, 属于 MW/VW/HW 三种加权口径并列的机械聚合变体, 测度定义依据已在母族 IDF 打分 (loughran_idf_score) 及 Loughran & McDonald 词典原始文献中给出, 非独立新构念, 无需单独追新文献。"
columns:
- loughran_idf_score_mw_sum_ctx
- loughran_idf_score_mw_sum_full
- loughran_idf_score_mw_sum_ss
unit: 无量纲加权分值之和 (银行-年层面, 媒体权威性加权 IDF 情感分的求和分子; 与 sum_media_authority_weight 搭配相除后得媒体权威加权语调, 单独看无自然单位)
formula: 'article: loughran_idf_score_mw{track} = loughran_idf_score{track} * media_authority_weight (media_authority_weight 由 compute_media_authority_weights 逐篇算, 缺失填 1.0); panel: loughran_idf_score_mw_sum{track} = groupby(bank, year)[loughran_idf_score_mw{track}].sum() (encode.build_aggregation_dict, sum 聚合); 下游 MW 语调 = loughran_idf_score_mw_sum{track} / sum_media_authority_weight'
producer: pipeline\sentiment\tone_words.py (article 级 loughran_idf_score{track} 打分, build_idf_weights IDF 权重构建) ; pipeline\panel\runner.py (loughran_idf_score_mw{track} = loughran_idf_score{track} * media_authority_weight 逐篇预乘) ; pipeline\panel\encode.py (build_aggregation_dict 银行-年 sum 聚合为 loughran_idf_score_mw_sum{track})
upstream:
- loughran_idf_score_full
- loughran_idf_score_ctx
- loughran_idf_score_ss
- media_authority_weight
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11-21
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: Textual analysis in finance
  venue: Annual Review of Financial Economics
  vol: '12'
  issue: '1'
  pages_or_artno: 357-375
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列同属一个银行-年层面的加权求和分子: `loughran_idf_score_mw_sum_full` / `_ctx` / `_ss`, 分别对应三轨文本 (full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗) 下, 逐篇文章「Loughran & McDonald (2011) 词典中文主译本 (`loughran_mcdonald_zh_2026`) 的 IDF 加权情感分」乘以「该篇文章所属媒体来源的权威性权重 (`media_authority_weight`)」后, 在银行-年内求和。它不是一个独立构念, 而是「情感强度 × 语料稀有度加权 × 媒体权威加权」三层构造叠加之后的一个中间求和量 (numerator), 生产用途是配上分母 `sum_media_authority_weight` (同一银行-年内媒体权威权重之和) 相除, 得到「媒体权威性加权 (media-weighted, MW)」版本的 loughran 语调测度, 与等权 (unweighted)、提及密度加权 (VW, mention-density weighted) 与跟风衰减加权 (HW, herd-weighted) 三种其它加权口径并列, 是本仓库「多种加权口径互为稳健性」谱系的一支。词典本体 `loughran_mcdonald_zh_2026` 是 Loughran & McDonald (2011, JF) 面向美国 10-K 文本构建的正/负情感词典 (含 6 大类, 本仓库落地正面 1,295 词/负面 3,729 词, 另含 5 类非极性词) 的中文主译本, 收录于 `config/tone_dicts.json`, 与 jiang_2021/yao_2021/bian_2021/du_2022/you_2018 五部中文原生金融情感词典并列构成 6 词典打分体系 (`pipeline/sentiment/tone_words.py`)。IDF 加权 (Inverse Document Frequency 逆文档频率) 的构念依据是: 一个情感词若在整个语料中出现得越稀少 (文档频率 df 越低), 它承载的边际信息量越大, 反之常见套话词的情感信号被稀释, 理应降权 (Spärck Jones, 1972 提出 IDF 原始统计解释; Jegadeesh & Wu, 2013, JFE 在"word power"框架下同样用逆文档频率类稀有度加权改进传统词典法, 是本仓库 IDF 加权分支的直接方法学参照)。媒体权威性加权 (media authority weighting) 的构念依据则是: 不同新闻来源对读者/市场的影响力不对称, 权威媒体 (如全国性财经报纸) 一篇报道的市场冲击力显著高于地方性小报同类报道, 因此在从「文章级」汇总到「银行-年级」时按来源权威性给文章赋权更贴近真实的信息传导强度, 这一构念在本仓库设计上与词典法本身的稀有度加权正交、可叠加。本家族三列即是这两层加权 (IDF 词汇稀有度 + 媒体权威性) 叠加之后, 在银行-年层面求和得到的分子量。

【方法学与计算】
计算分三步, 分属三个不同的 producer 文件, 逐步下沉。第一步 (`pipeline/sentiment/tone_words.py`, stage 22): 逐篇文章打出未加权的 `loughran_score{track}` 之后, 若配置启用 IDF 加权 (`idf_weighting: true`, 默认启用), 调用 `build_idf_weights` 在与 TF (词频) 相同的语料 (调用方传入 `content_full`, 缺失时回退裸 `内容`) 上, 对该词典所有情感词逐词计算文档频率 df(w), 套用平滑 IDF 公式 `log10(N / (1 + df(w)))` (N=去重后文档总数), 对全体词的 IDF 值做均值归一化 (使加权后量级 ≈ 等权版, 便于共享阈值), 再做 P1/P99 缩尾 (Winsorize) 抑制极端稀有词的权重爆炸。归一化后的 IDF 权重乘入该词的 base_score (`_build_idf_weighted_dict`), 由此得到 IDF 加权后的词典, 再逐篇、逐轨 (full/ctx/ss) 重新打分, 得到 `loughran_idf_score{track}` (家族外的兄弟列, 是本家族的直接上游)。⚠ IDF 的文档频率统计口径是「三轨共享同一份 content_full 语料上算一次」, 而非每轨各自独立算 df, 这样保证三轨之间稀有度权重可比, 差异只来自各轨文本本身覆盖的词是否命中。第二步 (`pipeline/panel/runner.py`): 先由 `compute_media_authority_weights` 逐篇文章计算 `media_authority_weight` (基于媒体来源的权威性度量归一化到均值 1 的连续权重, 缺失媒体信息的文章权重填 1.0, 即视同"中性权威度"参与、不做隐式剔除), 随后把该权重逐篇乘进上一步的 `loughran_idf_score{track}`, 得到文章级中间列 `loughran_idf_score_mw{track}` (`_mw` = media-weighted 的后缀标记, 与 `_w`〈mention-density 加权〉、`_hw`〈herd-weight 跟风衰减加权〉是同一构造模式的三个平行加权后缀, 互不覆盖)。第三步 (`pipeline/panel/encode.py::build_aggregation_dict`): 把文章级 `loughran_idf_score_mw{track}` 在银行-年 (`groupby(bank, year)`) 内做 `sum` 聚合, 即得到本家族三列 `loughran_idf_score_mw_sum{track}`。该求和列本身不是最终情感测度, 而是分子: 生产环节随后会以银行-年内 `sum_media_authority_weight` (同一批文章媒体权威权重的和) 作分母相除, 构造出媒体权威加权版本的 loughran 语调 (镜像 VW/HW 的除法构造, 三种加权口径的分母各不相同——mention_density 之和 / media_authority_weight 之和 / herd_weight 之和——但分子构造范式一致, 均是"文章级加权分值先乘权重再求和")。

【文献定位】
本家族综合了三支方法学文献。其一是词典法情感测度的经典源头: Loughran & McDonald (2011, Journal of Finance) 首次系统指出通用情感词典 (如 Harvard-IV) 在金融/会计文本中大量误判 (如 "liability"、"tax" 等中性财务术语被通用词典误标为负面), 由此构建面向 10-K 文本的金融专用情感词典, 是本词典族 (含中文译本 loughran_mcdonald_zh_2026) 的直接构念依据; Loughran & McDonald (2020, Annual Review of Financial Economics) 对文本分析在金融领域的方法论演进 (含词典法、机器学习法、大语言模型法的谱系) 做了系统综述, 为本仓库「词典法/LLM法/BERT法三方法互为稳健性」的整体设计提供文献定位。其二是 IDF 加权的统计学依据: Spärck Jones (1972, Journal of Documentation) 首次给出词频-逆文档频率 (TF-IDF) 中 IDF 项的统计学解释, 即稀有词承载更多判别信息; Jegadeesh & Wu (2013, Journal of Financial Economics) 在其"word power"框架下把稀有度类加权思路引入金融文本情感度量, 用信息含量而非简单词频给情感词赋权, 是本仓库 `build_idf_weights` 函数所遵循的方法学参照之一。其三是媒体权威性加权的构念依据: 权威媒体报道对读者/市场的信息传导效力不同于地方性小报同类报道, 这一常识性判断是本仓库在从「文章级」汇总到「银行-年级」环节引入 `media_authority_weight` 的设计出发点, 与 IDF 词汇稀有度加权分属两个独立的加权维度, 互不干涉、可叠加。此外, Du, Huang, Wermers & Wu (2022, Review of Finance) 构建的中文金融情感词典 (`du_2022`, 本仓库 6 词典之一) 与本家族所用 loughran 词典是并列而非嵌套关系, 其文中关于中文金融文本情感测度语言特异性的讨论 (如政治词信号强度、语言域特异性) 同样适用于理解本家族 loughran 词典在跨语言迁移 (英文原版→中文主译本) 场景下面临的挑战: 中文财经文本的用词习惯、否定/程度副词处理规则与英文原版词典设计时的假设并不完全一致, 这也是本仓库在 loughran 词典之外仍并列保留 5 部中文原生词典、且三方法 (词典/LLM/BERT) 互为稳健性而非以词典法为单一权威口径的方法论出发点。

## VAR: loughran_idf_score_mw_sum_full

【变体差分】
本列取 track=`_full` (标题+正文全文), 是三轨中的默认/最广覆盖轨。IDF 权重的文档频率统计口径 (第一步) 固定在 content_full 语料上完成 (三轨共享同一份 df 统计), 因此本列在"权重来源"这一维度上是三轨的锚点轨——ctx/ss 两轨虽然各自在自己的窗口文本上重新计算 TF (词频命中数) 并乘以同一套 IDF 权重, 但 IDF 权重本身并不因轨而变。本列的"覆盖面广"体现在: 只要文章被判定为一篇有效的银行∧金科报道 (留篇门控口径已切换为 full-only, 2026-06-29 起是否留篇只看 `llm_verified_full == True`, ctx/ss 两轨的样本行宇宙是 full 留篇集的子集), 本列即在全文范围内统计 loughran 词典命中并按 IDF、媒体权威性双重加权求和, 不受实体窗口或同句共现半径的限制。

在多层加权的堆叠顺序上, 本列的构造是「先词典打分 (loughran_score_full) → 再 IDF 稀有度加权 (loughran_idf_score_full) → 再媒体权威性加权 (loughran_idf_score_mw_full, 逐篇乘 media_authority_weight) → 最后银行-年内求和 (loughran_idf_score_mw_sum_full)」, 四步依次落在 tone_words.py → runner.py → encode.py 三个文件里, 任何一步的缺失都会导致下游列缺席而非报错崩溃 (`build_aggregation_dict` 对源列不存在的情形做优雅跳过)。本列作为分子, 与银行-年层面的 `sum_media_authority_weight` (同一批文章媒体权威权重之和) 相除后得到的比值, 才是最终可解释为"该银行-年内, 按媒体权威性加权后的 loughran 稀有度加权语调均值"的完整测度; 单独看本列的绝对数值会随该银行-年报道篇数、媒体权威权重分布同时波动, 不宜脱离分母单独解释或跨银行-年直接横向比较。⚠ 铁律: full/ctx/ss 三轨在此处是「各自 just-identified 并排、互为稳健性、不分主次」的关系, 禁止把三轨对应列混入同一个 over-identified 的 Hansen J 过度识别检验; 在回归设计中三轨各自进入独立的稳健性表列, 不应合并为单一右手边变量。同理, MW/VW/HW 三种加权口径 (媒体权威/提及密度/跟风衰减) 也应各自并排比较, 不应混入同一识别策略。

## VAR: loughran_idf_score_mw_sum_ctx

【变体差分】
本列取 track=`_ctx` (标题+目标银行实体窗口), 计算范式与 `_full` 完全相同 (逐篇 loughran_idf_score_ctx 乘以同一篇文章的 media_authority_weight 后银行-年内求和), 差异仅在于分子分母溯源的文本窗口更窄——只统计目标银行实体附近窗口内的词典命中, 而非全文。该轨的定位是「聚焦银行相关段落, 排除文章中与目标银行无关段落的情感噪声稀释」的稳健性检验轨, 与 `_full` 轨互为稳健性, 不分主次 (镜像 CLAUDE.md「双轨=互为稳健性」的一般原则)。IDF 权重仍沿用在 content_full 语料上统一计算的那一套 (三轨共享 df 统计, 不因窗口收窄而重算文档频率), 因此本列与 `_full` 列的差异纯粹来自 TF 侧 (词典命中位置被限制在实体窗口内) 而非权重侧。

物化实现上, `content_ctx` 文本由 stage 14 `ctx_materializer` 物化 (`prepend_title` 拼接标题与实体窗口正文), 若某篇文章缺乏可用的目标银行实体窗口 (如实体抽取失败或窗口定位不到目标银行提及), 会回退为全文 body 并标记 `ctx_is_fallback=True`; 该回退标记同时供分母口径复用 (`frac_ctx_fallback`), 使得回退比例本身也是一个可审计、可披露的诊断量。因为窗口收窄, 本列在样本方差上通常小于 `_full` 轨 (词典命中数更少、更集中), 但其构念意义是"聚焦相关性更强", 在解读时不应把 ctx 轨数值直接与 full 轨数值做量级比较, 而应看两轨的回归系数符号与显著性是否一致 (稳健性佐证), 而非把两者数值合并平均。留篇门控已切换为 full-only 口径 (2026-06-29), 因此本列所覆盖的样本行宇宙是 full 轨留篇集的子集, 而非独立抽样; 与 `_full`/`_ss` 两列以及 MW/VW/HW 加权口径均各自 just-identified 并排, ⚠ 三轨禁混同一 over-identified Hansen J 的铁律同样适用于本列。

## VAR: loughran_idf_score_mw_sum_ss

【变体差分】
本列取 track=`_ss` (标题+银行∧金科同句±N窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认半径 1), 是三轨中判据最严的一支——只统计目标银行与金科词在同一句 (或邻近 ±N 句) 内共现的文本片段中的 loughran 词典命中, 经 IDF (仍沿用 content_full 语料统一计算的权重) 与媒体权威性双重加权后银行-年内求和。ss 轨的构念意图是最大程度剔除"报道整体提及银行, 但金科相关论述与银行论述并不在同一语境"的噪声, 把情感测度锁定在银行与金融科技话题真正交织的句子片段上, 相比 ctx 轨 (以实体窗口为界, 窗口可能跨越多句甚至包含与金科无关的段落) 判据更严格。

ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, `content_ss` 回退为全文 body, 并标记 `ss_is_fallback=True` (与 ctx 共享同一套 `n_articles` 分母口径, 即回退文章仍计入分母而非被剔除); 若 `FINTECH_AC` (金科词自动机) 未加载为 None, 则 `*_is_fallback` 全部置 True, 优雅降级为等同全文轨, 而非报错中断整个流水线。ss 轨判据的抽取原语 (`entity_context.py` 中同句共现的严格判据) 与 stage 13 共现硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` (±1 句窗口判据, 用于决定文章是否进入样本) 是两套不同原语、服务于两个不同环节 (前者决定"用哪段文字打分", 后者决定"文章是否留篇"), 不可互相复用混淆。本列与 `_full`/`_ctx` 两列同样互为稳健性、不分主次, 三者各自 just-identified 并排, 禁止混入同一 over-identified Hansen J 过度识别检验; 在 T=2 开发样本上 ss 轨的有效 (非回退) 命中量通常显著小于 ctx/full 两轨, 是判据收紧后的预期现象, 不代表数据缺陷。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
<!-- rendered-citations:end -->
