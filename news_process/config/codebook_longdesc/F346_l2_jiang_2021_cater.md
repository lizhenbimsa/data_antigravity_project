---
family_id: F346
columns:
- jiang_2021_cater_ctx
- jiang_2021_cater_full
- jiang_2021_cater_ss
unit: 无量纲差分得分 (词典语调 - LLM 语调, 值域约 [-2, 2])
formula: 'jiang_2021_cater{track} = jiang_2021_tone{track} - llm_vote_tone{track}'
producer: pipeline\panel\runner.py (§8d 算法迎合度 Algorithmic Catering 全展开区块)
upstream:
- 22_tone_words (jiang_2021_tone_full/_ctx/_ss, 词典语调)
- 21_tone_llms (llm_vote_tone_full/_ctx/_ss, 三家 LLM 多数投票共识语调)
citations:
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: '36'
  issue: '9'
  pages_or_artno: 3603-3642
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: "10.1080/21697213.2024.2337262"
  type: "journal"
  authors: "Meng, Q., Du, X., & Gong, X."
  year: 2024
  title: "Does operational disclosure curb textual tone manipulation by corporate management?"
  venue: "China Journal of Accounting Studies"
  vol: "12"
  issue: "2"
  pages_or_artno: "247-275"
- doi: "10.1515/econ-2022-0129"
  type: "journal"
  authors: "Wang, H."
  year: 2024
  title: "Media Tone and Earnings Management before the Earnings Announcement: Evidence from China"
  venue: "Economics"
  vol: "18"
  issue: "1"
  pages_or_artno: "20220129"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 jiang_2021_cater_full / _ctx / _ss 衡量的是"算法迎合度"(algorithmic catering) 这一构念在 jiang_2021 词典单一测度上的实现: 报道文本的词典语调分与同一文本的三家 LLM 多数投票语调共识之间的系统性偏离。构念脉络承自 Cao, Jiang, Yang & Zhang (2023, RFS) 对企业信息披露的洞察——当撰写者预期读者(或市场算法)会用某种固定规则(例如简单词典计数)处理文本情绪时, 撰写者有动机策略性地堆砌该规则能识别的正面/负面词汇, 使词典读数偏离一个更接近"真实"语义理解的深层模型读数, 这种偏离本身构成对算法的迎合行为信号。本项目将该构念从企业信息披露场景迁移到新闻报道场景: jiang_2021 是姜富伟、孟令超、唐国豪 (2021, 经济学季刊) 构建的中文财经媒体情绪专用词典, 提取自媒体文本预测股票回报的实证研究, 词表贴合中国财经新闻的用词习惯; llm_vote_tone 是本项目 stage 21 三家商用大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 对同一文本做语义级情绪判读后取多数投票的共识语调, 在方法论谱系上更接近"深层语义模型"一端, 不依赖固定词表规则, 能捕捉语境、反讽、复杂句式对情绪的调节。两者之差 jiang_2021_tone − llm_vote_tone 若持续为正, 说明该词典口径下报道文本"看起来"比大模型语义判读更正面, 提示该词典可能对某些正面词汇(如政策套话、行业景气用语)过度敏感, 或文本存在词汇堆砌式的正面用词但语义层面并不必然正面的现象; 若为负则相反。该差分不是一个"孰对孰错"的裁决, 而是一个诊断性、方法论敏感性指标, 用于揭示词典法与语义模型法在中国财经新闻语境下系统性分歧的方向与幅度, 服务于稳健性审查与测度选择的透明披露, 而非直接作为研究假设检验中的处理变量或结果变量使用。

【方法学与计算】
计算发生在面板导出阶段 (`pipeline/panel/runner.py` §8d "算法迎合度 (Algorithmic Catering)" 区块), 是纯粹的面板列间算术差分, 不涉及任何额外的模型推理或 API 调用, 因而边际成本为零。producer 逻辑对三轨 (full/ctx/ss) 分别循环: 对每个轨道 track ∈ {_full, _ctx, _ss}, 取该轨道下 jiang_2021 词典的语调列 `jiang_2021_tone{track}` (由 stage 22 词典法情感产出, 逐句/逐篇按语言学规则——否定翻转、程度副词、转折——聚合正负词命中并归一化, jiang_2021 是该规则族六部词典之一) 与该轨道下三家 LLM 多数投票共识语调列 `llm_vote_tone{track}` (由 stage 21 三家 LLM 各自判读后经多数投票机制产出), 逐 bank-year 行做减法: `jiang_2021_cater{track} = jiang_2021_tone{track} - llm_vote_tone{track}`。两个被减列均在文章级各自完成聚合后进入面板层, 差分本身不改变行覆盖 (skipna 规则由上游各自的聚合口径决定, 若任一被减列在该行为 NaN, 差分结果亦为 NaN, producer 对存在性做前置守卫: 只有当两个上游列均存在于 panel.columns 时才计算, 否则该轨道该列整体缺席而非报错, 优雅降级)。三个轨道 (full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句±N窗) 各自独立完成该差分运算, full 轨的 `jiang_2021_tone_full` 与 `llm_vote_tone_full` 相减产出 `jiang_2021_cater_full`, ctx/ss 同理, 三条轨道之间没有任何交叉引用或借用, 是三条并行、互不依赖的计算流水线的产物, 而非同一次计算的三个切面。值域上, 由于 jiang_2021_tone 与 llm_vote_tone 各自的理论值域大致落在类似区间内 (词典语调经归一化落在有限区间, LLM 投票语调按离散标签映射到相近数值区间), 差分结果的经验值域也集中在一个较窄的对称区间内, 0 附近表示两法高度一致, 偏离 0 越远表示分歧越大, 符号指示分歧方向。

【文献定位】
本家族的方法论根基是 Cao, Jiang, Yang & Zhang (2023, The Review of Financial Studies) 提出的"迎合听众的语言"(talk when a machine is listening) 框架——该文首次系统论证企业管理层在预期到自动化文本分析工具会解读披露文本情绪时, 会策略性调整措辞以迎合算法读数, 并提出用词典法读数与更复杂模型读数的偏离度作为迎合行为的代理测度, 是本家族"词典 − 深层模型"差分构造思路的直接学理来源。jiang_2021 词典本身取自姜富伟、孟令超、唐国豪 (2021, 《经济学(季刊)》) 对中文财经媒体文本情绪预测股票回报的研究, 是本项目六部中文财经情感词典之一, 在词表构建上聚焦媒体报道场景 (相对于面向年报/公告文本的词典), 与本项目"银行×金融科技报道"的应用场景语域较为贴近。Du, Huang, Wermers & Wu (2022, Review of Finance) 对中文财经情感词典领域方法论的系统性论证 (语言与领域特异性对情感词典效度的影响) 为"不同词典在同一中文财经语料上可能产生系统性不同读数"这一前提提供了独立的方法论支撑, 说明词典与深层模型间的分歧未必是任一方"错误", 而更可能反映测度构念本身的领域敏感性。Frankel, Jennings & Lee (2022, Management Science) 直接比较机器学习情感测度与词典法情感测度在企业披露文本上的分歧模式, 是"词典法 vs. 更复杂模型法互为稳健性、系统性分歧值得独立报告"这一方法论立场的近期同行先例, 支持本家族将该差分作为独立诊断列而非临时中间变量保留在面板中的设计选择。 两项中国情境的近期研究可在被减数一侧与构念前提上进一步补强本家族的外部效度。Meng、Du 与 Gong (2024) 以中国上市公司年报文本测度管理层的文本语调操纵 (textual tone manipulation), 即语调正面程度超出基本面可解释的部分, 并检验经营性披露对该操纵的约束效应; 其"语调 − 基准语调"的差分思路与本家族 `jiang_2021_tone − llm_vote_tone` 在测度形态上同属"以语调相对某一参照基准的偏离量化策略性书写"一类, 从而为 Cao, Jiang, Yang & Zhang (2023) 源自美国披露场景的迎合机制补上了一项中国语境下的同域行为学前提。迁移边界须如实标明: 该文的参照基准是基本面回归的拟合值 (残差法) 而非第二套语义读取引擎, 文本为企业自述年报、观测单位为公司-年, 原文既未使用大语言模型, 亦未做词典与深层模型的读数对照, 因此它只锚定本家族被减数 `jiang_2021_tone` 一侧与"语调偏离可作为策略性书写信号"这一构念前提, 不能被援引为本家族以 LLM 三家投票共识作减数的方法学依据。Wang (2024) 以中文媒体报道语调测度检验其与盈余管理的关联, 提供了"中文媒体报道的语调经词典类方法可测且承载经济含义"的同域应用证据, 与 jiang_2021 面向媒体语料 (相对于面向年报/公告文本) 的构建定位相互呼应, 支撑本家族词典端读数的构念效度; 但该文只用单臂词典语调, 无 BERT/LLM 任何对照臂, 分析层级为公司-事件窗而非 bank-year, 报道对象亦为一般财经报道而非银行×金融科技共现报道, 且载文期刊层级一般, 故仅可按"词典端同域佐证"的降级口径引用, 不构成对本家族 LLM 减数端或该差分诊断用途的任何支持。
## VAR: jiang_2021_cater_full

【变体差分】
本列是 full 轨(标题+正文全文)下的算法迎合度差分, 计算式为 `jiang_2021_tone_full - llm_vote_tone_full`。full 轨是三条并行轨道之一, 扫描范围覆盖整篇报道正文(含标题前置), 是三轨中文本信息量最完整、上下文最丰富的一条, 因而是本项目多数下游研究 P1 主处理变量 (`llm_vote_tone_full`) 所在的口径基准, 本列继承这一定位, 是三轨中最常被作为主要报告口径参照的一支, 但不因此获得优先于 ctx/ss 两轨的统计学地位——三轨仍是各自独立 just-identified 并排的稳健性测度, 互为稳健性、不分主次, 禁止把 full/ctx/ss 三轨的迎合度差分同时纳入同一个 over-identified 的 Hansen J 过度识别检验。分母/覆盖口径上, full 轨的语调聚合覆盖全文所有句子, 相比 ctx/ss 两轨通常有更少的缺失(因为不依赖实体窗口或同句共现命中), 但仍遵循留篇门控 = full-only 铁律(2026-06-29 起): 一篇报道是否被判定为"银行×金科"报道, 唯一依据是 `llm_verified_full == True`; ctx/ss 两轨的语调及本列在 ctx/ss 轨的对应值, 行宇宙上均是 full 留篇集合的子集(conditional-on-full), 本列作为 full 轨自身则直接对应留篇门控判定的全集行。使用建议上, 当研究者需要一个能代表"整篇报道叙事基调"层面的词典-语义分歧诊断时, 应优先参照本列; 当研究者关心的是分歧是否随语境收窄而放大或收敛(例如判断词典误读是否集中来自与银行×金科主题无关的段落)时, 则应把本列与 ctx/ss 两轨并列比较, 而非仅看本列的绝对水平。

## VAR: jiang_2021_cater_ctx

【变体差分】
本列是 ctx 轨(标题+目标银行/金科实体窗口)下的算法迎合度差分, 计算式为 `jiang_2021_tone_ctx - llm_vote_tone_ctx`, 两个被减列均只在实体窗口范围内的句子上聚合, 而非整篇正文。相较 full 轨, ctx 轨把词典扫描与 LLM 判读都收窄到与目标银行/金科实体在物理位置上更贴近的文本片段, 意在剔除报道中与银行×金科主题无关的段落对语调的稀释或污染, 因此本列衡量的"词典 vs. LLM 分歧"更聚焦于实体相关叙述本身的用词与语义分歧, 而非全文整体基调的分歧, 与 full 轨的分歧构念存在系统性差异, 不能把二者视为同一测度的重复观测。行宇宙上, ctx 轨的语调聚合遵循 conditional-on-full 原则: 只在 full 留篇集合(`llm_verified_full == True`)子集内计算, 若某留篇文章缺乏可识别的实体窗口锚点, 该文章在 ctx 轨的贡献按 stage 14 物化阶段的口径处理(实体窗口缺失场景), 使得 ctx 轨样本量原则上不大于 full 轨。本列与 `jiang_2021_cater_full`、`jiang_2021_cater_ss` 是三条并行、各自 just-identified 的稳健性测度之一, 互为稳健性、不分主次, 三者不得混入同一个 over-identified Hansen J 检验设定。解读上, 若 `jiang_2021_cater_ctx` 相对 `jiang_2021_cater_full` 出现系统性放大(绝对值更大), 提示词典与 LLM 的分歧集中来自实体近旁的用词选择, 而非报道整体基调的宽泛差异, 对研判词典在具体银行/金科语境下是否存在特定用词误判具有诊断价值; 反之若 ctx 轨分歧收窄, 则说明 full 轨的分歧更多来自与目标实体本身关系较远的段落, 提示相关分歧对本项目核心处理变量的直接影响较有限。

## VAR: jiang_2021_cater_ss

【变体差分】
本列是 ss 轨(标题+银行∧金科同句±N窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1)下的算法迎合度差分, 计算式为 `jiang_2021_tone_ss - llm_vote_tone_ss`, 是三轨中判据最严格的一支: 只在银行实体与金科关键词在同一句(或半径 N 内相邻句)共同出现的句子集合上聚合词典语调与 LLM 语调, 而非依赖更宽松的实体窗口。ss 轨遵循"回退语义镜像 ctx"的铁律: 若某留篇文章不存在银行∧金科同句共现, 则该文章的 `content_ss` 回退为全文 body, 对应的 `ss_is_fallback` 标记为 True, 分母仍与其余轨道共享同一 `n_articles`; 若上游 `FINTECH_AC` 词典缺失(None), 则全部 `*_is_fallback` 优雅降级为 True。因此本列在样本中既包含"真同句共现"观测, 也包含按回退规则计入的"全文替代"观测, 二者应结合 `ss_is_fallback` 标记联合解读, 不应把本列的全部取值一概视为"严格同句语境下的迎合度"。本列与 full/ctx 两轨同样是各自独立、just-identified 并排的稳健性测度, 互为稳健性、不分主次, 三轨结果不得混入同一个 over-identified Hansen J 检验; ss 轨作为三轨中语境最窄、判据最严的一支, 通常预期其语调读数(以及由此产生的迎合度差分)对孤立词汇命中的敏感度相对更高, 是识别"词典法在极短语境下是否更容易产生分歧读数"的诊断口径。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Meng, Q., Du, X., & Gong, X. (2024). Does operational disclosure curb textual tone manipulation by corporate management?. China Journal of Accounting Studies, 12(2), 247-275. https://doi.org/10.1080/21697213.2024.2337262
Wang, H. (2024). Media Tone and Earnings Management before the Earnings Announcement: Evidence from China. Economics, 18(1), 20220129. https://doi.org/10.1515/econ-2022-0129
<!-- rendered-citations:end -->
</content>
