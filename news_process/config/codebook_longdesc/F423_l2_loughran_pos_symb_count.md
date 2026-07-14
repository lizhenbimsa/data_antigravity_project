---
family_id: F423
columns:
- loughran_pos_symb_count_ctx
- loughran_pos_symb_count_full
- loughran_pos_symb_count_ss
unit: 篇数 (bank-year 内文章计数, 非负整数)
formula: 'loughran_pos_symb_count_{trk} = sum over articles in bank-year : 1[(loughran_score_{trk}
  > 0) AND (innovation_substantiveness_full == ''象征性'')]; 即"该轨道下 loughran 词典判定净正面"
  与"LLM P3 创新实质性分类判为象征性" 两个跨方法学条件同时成立的文章篇数 (0/1 篇章级指示求和, 每篇至多贡献 1,
  非词级频次); innovation_substantiveness_full 恒取自 full 轨 LLM 分类结果 (不随 trk 切换),
  trk 仅切换 loughran_score 的文本轨道来源; 该列是洗稿率 (washing ratio) 计算的分子部件之一,
  分母为姊妹家族 loughran_pos_substvalid_count_{trk} (F422)'
producer: news_process/pipeline/panel/runner.py::aggregate_panel (`_is_loughran_pos_symb{track}`
  篇章级指示构造, `pipeline/panel/encode.py::build_aggregation_dict` 按 sum 聚合到 bank-year)
upstream:
- 21_tone_llms.parquet (innovation_substantiveness_full, P3 创新实质性 LLM 分类)
- 22_tone_words.parquet (loughran_score_{full,ctx,ss}, 词典净情感极性)
citations:
  - doi: 10.1016/j.frl.2022.102776
    type: journal
    authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
    year: 2022
    title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
    venue: Finance Research Letters
    vol: 47
    pages_or_artno: 102776
  - doi: 10.1111/j.1540-6261.2010.01625.x
    type: journal
    authors: Loughran, T., & McDonald, B.
    year: 2011
    title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
    venue: The Journal of Finance
    vol: 66
    issue: 1
    pages_or_artno: 35-65
  - doi: 10.1111/1475-679X.12123
    type: journal
    authors: Loughran, T., & McDonald, B.
    year: 2016
    title: "Textual analysis in accounting and finance: A survey"
    venue: Journal of Accounting Research
    vol: 54
    issue: 4
    pages_or_artno: 1187-1230
  - doi: 10.1287/stsc.2023.0188
    type: journal
    authors: Westphal, J. D.
    year: 2023
    title: "Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale"
    venue: Strategy Science
    vol: 8
    issue: 2
    pages_or_artno: 221-232
  - doi: 10.2139/ssrn.3446388
    type: wp
    authors: Bian, S., Jia, D., Li, F., & Yan, Z.
    year: 2021
    title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
    venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
loughran_pos_symb_count 家族衡量单个 bank-year 内, 同时满足两个跨方法学条件的文章篇数: 一是 Loughran-McDonald 中文主译本 (loughran_mcdonald_zh_2026, 见 config/tone_dicts.json) 在给定轨道文本上给出净正面判定 (loughran_score_{trk} > 0), 二是 LLM P3 创新实质性分类 (innovation_substantiveness, 三分类取值域含"实质性"/"象征性") 将该篇文章判定为"象征性"。这不是词典内部的词表二分子类计数, 而是"词典法情感极性" (方法学一) 与"LLM 创新表述实质性分类" (方法学二) 两条独立测度管线的交叉计数, 方法学根基直接对应 runner.py 源码注释点名的 Bingler, Kraus, Leippold & Webersinke (2022, Finance Research Letters) "cheap talk and cherry-picking" 框架——该文用 ClimateBert 识别企业气候信息披露中"言辞正面但缺乏实质承诺锚定"的文本, 本项目将其方法论移植到银行/金科新闻语境: 一篇报道若在情感基调上呈现净正面 (词典判定), 但其创新/业务表述被 LLM 独立判定为"象征性宣示"而非"实质性可验证行动", 即构成一次"洗稿" (washing) 观测——正面措辞与实质内容之间存在断裂, 是印象管理/cheap talk 现象在中文财经报道语料上的操作化。

本家族因此本质上是"洗稿率" (washing ratio) 计算管线的分子部件之一 (runner.py 步骤 7h `_safe_ratio`), 而非独立自足的情感强度测度。分母是姊妹家族 loughran_pos_substvalid_count (F422; 注意此姊妹关系是同一 loughran 词典下"象征性 (symb)"与"实质性已测量 (substvalid)"两个互补子计数, 与 bian_2021 词典家族 (F130) 无关, 二者仅因同名后缀 pos_substvalid_count 而易被误认, 实际归属不同词典家族), 分母计数口径是"净正面 ∧ LLM 实质性分类已测量成功" (即分类结果落入{实质性, 象征性}两个有效标签之一, 排除 NaN/分类失败观测), 而非全部净正面文章数; 这一同域分母设计 (runner.py fix omni-g-runner-10/g-runner-14, 2026-06-11) 是为修正一个已知偏误: 若分母仍使用"全部净正面文章数"这一物理计数, 则当 LLM 实质性分类失败率上升时, 分子 (要求分类成功且落"象征性") 相对萎缩、分母不变, 洗稿率会被系统性稀释向下, 制造"洗稿现象变少"的假象; 改为同域分母后, 洗稿率的分母也只数"分类成功"的那批, 保证比率的分子分母口径一致。

需要特别澄清的构念边界是: innovation_substantiveness_full 这一 LLM 分类判据恒定取自 full 轨 (标题 prepend 全文) 的分类结果, 不随本家族的 trk (full/ctx/ss) 切换而重新分类——三个轨道之间唯一变化的是 loughran_score 的文本来源 (即"净正面"这一判据在哪个文本窗口上成立), "是否象征性"这一判据本身是全篇统一的单一 LLM 判断。这与本项目其他三轨族 (三轨各自独立完成全部判据计算, 互为稳健性并排) 存在本质差异: 本家族的"象征性"标签不是三轨独立测度, 而是三轨共享的固定锚点, 只有"净正面"一端在三个轨道间变化。研究者据此解读跨轨差异时, 应理解为"文本窗口大小如何影响该篇报道在该窗口下呈现净正面语调的概率", 而非"文本窗口大小如何影响 LLM 对该篇报道创新实质性的判断"——后者的判断口径全轨统一。

【方法学与计算】
计算链路上, 本家族依赖两条独立上游: 词典侧净情感极性来自 stage 22 tone_words.py 产出的 loughran_score_{full,ctx,ss} (word-level 匹配后聚合为篇章级符号); LLM 侧创新实质性分类来自 stage 21 tone_llms.py 产出的 innovation_substantiveness_full (P3 论文所属的创新实质性分类任务, 三家 LLM 投票产出的共识标签)。两条上游在 pipeline/panel/runner.py::aggregate_panel 步骤 4 (洗稿率前置列构造区) 汇合: 先构造篇章级布尔指示 `_is_loughran_pos_symb{track}` = (loughran_score_{track} > 0) & (innovation_substantiveness_full == '象征性'), 随后在同一函数内对每个 bank-year 分组 sum 聚合, 产出本列; 与此并行还构造同域分母指示 `_svd_loughran_pos{track}`, 供步骤 7h 计算 loughran_washing_ratio_{track} = loughran_pos_symb_count_{track} / loughran_pos_substvalid_count_{track} (`_safe_ratio` 零分母保护)。本列本身不做归一化, 是原始篇数计数, 天然随 bank-year 内报道总量增长而增长, 在做跨银行/跨年度比较或用作回归自变量时通常需要配合 n_articles 或洗稿率比值本身 (而非原始计数) 使用, 直接比较不同报道量银行的原始计数会引入虚假的规模效应。

本家族与其余四种"洗稿率"方法学变体 (方法 A: LLM 投票正面 ∧ 象征性; 方法 A2: 单 LLM per-model 正面 ∧ 象征性; 方法 D: 六词典均值正面 ∧ 象征性; 方法 E/E2: BERT argmax/per-model 正面 ∧ 象征性; 方法 F: 高置信 agreement_rate 门控) 属于同一构念族下并排的跨方法学稳健性梯子——loughran 词典是方法 D2 (单词典) 分支下的一员, 与 jiang_2021/yao_2021/bian_2021/du_2022/you_2018 五部姊妹词典各自产出同构的 `{dict}_pos_symb_count{track}` 列并排存在, 互为方法学稳健性, 不分主次; 各词典各自 just-identified, 不应混入同一 over-identified 检验框架。三个文本轨道 (full/ctx/ss) 在"净正面"判据一端各自独立、互为稳健性并排 (full=标题 prepend 全文基准轨; ctx=标题+实体窗口; ss=标题+银行∧金科同句共现窗口, 无共现时镜像 ctx 回退语义退化为全文并置 ss_is_fallback=True, 与非回退观测共享同一 n_articles 分母), 三轨计数严禁混入同一个 over-identified 的 Hansen J 过度识别检验; 但如上文所述, 三轨差异只体现在 loughran_score 一端, "象征性"判据全轨统一取自 innovation_substantiveness_full, 这是本家族独有的、区别于典型三轨族的构造细节, 使用者不应误将本列理解为"innovation_substantiveness 本身也做了三轨独立分类"。

【文献定位】
本家族最直接的方法学锚点是 Bingler, Kraus, Leippold & Webersinke (2022, Finance Research Letters) 提出的 "cheap talk and cherry-picking" 检测框架, 该文用 ClimateBert 在企业气候风险披露文本中识别"言辞正面但缺乏可核验承诺支撑"的表述模式, 为本项目"词典净情感极性 × LLM 创新实质性分类"的交叉构造提供了直接的方法论范式——将"语调是否正面"与"内容是否实质"拆解为两个独立测量维度再取交集, 而非依赖单一维度的判断。词典本体的构建原则则承袭 Loughran & McDonald (2011, The Journal of Finance) 关于"通用情感词典直接套用在专业领域文本上会产生系统性误判"的经典论证, 该文主张情感词表须结合领域语境重新校准, 是本项目并行维护六部中文金融情感词典 (含 loughran 中文本土化译本) 的方法论出发点; Loughran & McDonald (2016, Journal of Accounting Research) 的后续综述进一步系统梳理了文本分析在会计与金融研究中原始计数与归一化比率各自的适用场景, 支持本家族保留原始篇数计数、由分母 (F422) 与洗稿率比值分别承担归一化任务的设计选择。"象征性表述与实质性行动断裂"这一构念的组织理论根基部分呼应 Westphal (2023, Strategy Science) 关于"系统性象征管理" (systemic symbolic management) 的讨论, 该文揭示企业社会责任与公司目标叙事中广泛存在的以言辞替代实质行动的现象, 为"象征性"标签的实证意义提供跨学科理论支撑, 但需注意本家族的"象征性"判据来自 LLM P3 分类任务而非该文的词表或量表, 引用关系是理论动机层面而非方法直接移植。Bian et al. (2021) 关于中文金融情感词典构建的工作方法学是本项目多词典并行架构中 bian_2021 词典 (F130 家族所在) 的直接来源, 此处引用旨在说明"多词典互为稳健性"设计在中文金融文本情感测度领域已有方法学先例, 而非暗示 loughran 与 bian_2021 两部词典之间存在词表层面的姊妹关系。

## VAR: loughran_pos_symb_count_ctx

【变体差分】
本列是 loughran_pos_symb_count 家族在 ctx 轨道上的计数, "净正面"判据的文本基础为 content_ctx (标题 prepend + 实体窗口截取正文), "象征性"判据仍固定取自 innovation_substantiveness_full (不随本列切换), 因此本列与 full 轨列的差异完全来自 loughran_score_ctx 相对 loughran_score_full 的判定差异, 而非 LLM 分类口径变化。当一篇文章篇幅较长、正文中除银行相关段落外还包含大量与目标银行无直接关系的内容时, ctx 轨的 loughran_score 判定范围被限定在实体窗口内, 该篇报道在 ctx 轨呈现净正面的概率可能与 full 轨不同, 使得本列计数与 full 轨列出现分化, 这一分化应被解读为"语境窗口大小对词典净情感判定的影响", 而不能被误读为 LLM 象征性判断本身发生了变化。

当文章无法定位到有效的实体窗口时, ctx 轨按统一回退语义退化为使用全文 body 文本, 对应 ctx_is_fallback 标记置真, 此时该篇观测的 loughran_score_ctx 数值与 loughran_score_full 重合, 本列在该篇观测上的贡献也随之与 full 轨列一致 (但仍作为独立列存在, 不做事后合并); 回退发生时该篇观测仍计入洗稿率计算所用的 n_articles/同域分母口径, 不产生因回退而导致的样本损耗。本列与同家族 full/ss 两列的关系是并排的方法学稳健性检验, 而非主辅关系, 三者均不应被同时纳入同一个 over-identified 的 Hansen J 过度识别检验框架; 正确的稳健性检验做法是分别用 full/ctx/ss 三列各自计算洗稿率并比较系数符号与显著性的一致性。就"象征性"判据本身而言, 因其全轨统一取自 innovation_substantiveness_full, ctx 轨与 full/ss 轨在这一维度上不存在也不应存在差异——若观察到跨轨的洗稿率差异, 应归因于词典净情感极性在不同文本窗口下的判定差异, 而非归因于创新实质性分类的窗口敏感性, 这是解读本列时须严格把持的构念边界。

## VAR: loughran_pos_symb_count_full

【变体差分】
本列是 loughran_pos_symb_count 家族的全文轨道计数, "净正面"判据的文本基础为 content_full (标题 prepend 之后的全篇正文), 不做任何实体窗口或共现窗口截取, 是覆盖范围最宽、最不受截取规则影响的一条轨道。因 innovation_substantiveness_full 本身就是 full 轨的 LLM 分类结果, 本列是三列中"净正面"判据文本与"象征性"判据文本天然同源 (均来自 full 轨) 的唯一一条轨道——ctx/ss 两列的"净正面"判据取自各自截取窗口, 但"象征性"判据仍借用 full 轨分类结果, 存在判据文本来源的跨轨错位; 而本列不存在这一错位, 两项判据均锚定在同一份 full 轨文本上, 在概念一致性意义上是三轨中内部最"干净"的一条。

在本项目 2026-06-29 确立的"留篇门控 = full-only"口径下, full 轨也是判定"一篇文章是否被记为有效银行/金科报道"的门控依据 (llm_verified_full == True), 这意味着 full 轨对应的样本行宇宙是最完整的一个, ctx/ss 两轨在留篇门控意义上是 full 留篇集合的条件子集测度/稳健性轨。作为三轨之一, full 轨与 ctx/ss 两轨在计量地位上完全平等并排, 均属"互为稳健性、不分主次", 尽管因判据同源一致性与样本行宇宙完整性, full 轨常被作为默认呈现轨道, 但这只是叙事习惯而非统计学意义上的"主测度"地位, 研究者不应因样本量最大就默认其系数估计更可信, 而应把三轨 (或洗稿率比值的三轨版本) 的一致性本身作为稳健性证据链的一环。使用建议上, 本列原始计数需配合 n_articles 或洗稿率比值 (与同域分母 loughran_pos_substvalid_count_full 相除) 使用, 未经归一化的原始篇数在跨银行报道量差异较大的样本中会产生虚假的规模效应关联。

## VAR: loughran_pos_symb_count_ss

【变体差分】
本列是 loughran_pos_symb_count 家族在 ss 轨道 (银行∧金科同句共现窗口) 上的计数, "净正面"判据的文本基础为 content_ss, 即标题 prepend 之后叠加"目标银行实体与金科相关词汇在同一句 (或按 config/filtering.yaml::context_window.ss_sentence_radius 配置的句子半径窗口, 默认 ±1 句) 邻近共现"的片段拼接, 是三轨中判据最严格、扫描范围通常最窄的一条轨道; "象征性"判据仍固定取自 innovation_substantiveness_full, 不随本列重新分类。当一篇文章不存在满足"银行∧金科同句"共现条件的片段时, ss 轨镜像 ctx 轨的回退语义, 退化为使用全文 body 文本, 并将 ss_is_fallback 标记置真; 此时该篇观测在 ss 轨的 loughran_score 数值 (进而本列的贡献) 会与 full 轨重合, 但两列在面板中仍各自独立存在, 且回退发生的观测继续计入共享的 n_articles/同域分母口径, 不因回退而被剔除样本。当上游 FINTECH_AC (金科关键词自动机) 为空 (None) 时, 该篇文章的全部 *_is_fallback 标记 (包括 ss) 会统一置真, 属于系统对金科词典缺失时的优雅降级路径, 而非个案错误。

ss 轨的净正面判据来自 stage 13 共现硬过滤所用判据原语 (has_bank_fintech_cooccurrence_within_radius) 的一个相邻但不同的口径: ss 轨物化文本时使用严格同句 (extract_bank_fintech_cooccurrence 口径, 句半径由 ss_sentence_radius 单独配置), 而 stage 13 硬过滤生产口径是 sentence_radius=1 的邻近窗口, 两者是两个不同的配置键, 不可互相复用或混淆。在实证使用上, ss 轨因样本覆盖窄、回退比例可能相对更高, 通常更适合作为"银行-金科议题强相关叙事中洗稿现象"的针对性稳健性检验轨道, 与 full/ctx 两轨并列报告、互为稳健性证据, 三者 (及各自对应的洗稿率比值) 均不应被单独混入同一个 over-identified Hansen J 过度识别框架中使用; 与 ctx 轨相同, ss 轨观察到的跨轨差异应归因于共现窗口对词典净情感判定的影响, 而非归因于创新实质性分类本身的轨道敏感性。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Westphal, J. D. (2023). Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale. Strategy Science, 8(2), 221-232. https://doi.org/10.1287/stsc.2023.0188
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
