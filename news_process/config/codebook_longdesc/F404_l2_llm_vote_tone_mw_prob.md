---
family_id: F404
columns:
- llm_vote_tone_mw_prob_ctx
- llm_vote_tone_mw_prob_full
- llm_vote_tone_mw_prob_ss
unit: 语调得分 (连续, 理论上界约 [-1,1]; bank-year 面板列, 由文章级 logit 概率分加权聚合而来)
formula: 'panel[llm_vote_tone_mw_prob{track}] = panel[llm_prob_score_mw_sum{track}] / _llm_denom(''mw'', ''prob'', track, sum_media_authority_weight.replace(0,NaN)); 其中 llm_prob_score_mw_sum{track} 是文章级 llm_prob_score{track}(=P(正面)-P(负面) 的 logit-to-score 概率映射) 按 media_authority_weight 加权求和后聚合到 bank-year, 分母为该 bank-year 上 llm 三家投票均验证通过样本对应的 media_authority_weight 之和 (0 记 NaN 防除零)'
producer: pipeline\panel\encode.py ; pipeline\panel\export.py
upstream:
- pipeline\panel\encode.py::_llm_denom
- pipeline\sentiment\tone_llms.py
- pipeline\panel\encode.py (media_authority_weight 逐篇赋值与 sum_media_authority_weight 聚合逻辑内嵌于该模块, 非独立文件)
citations:
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: 'Negation scope detection in sentiment analysis: Decision support for news-driven trading'
  venue: Decision Support Systems
  vol: '88'
  pages_or_artno: 67-75
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (llm_vote_tone_mw_prob_full / _ctx / _ss) 是"媒体权威性加权 (media-authority weighted, MW) 的 LLM 概率语调 (prob tone)"面板测度, 属 stage 21 三家 LLM 投票情感体系与 stage 40 面板聚合体系的交叉产物。与家族命名中 "vote" 字面暗示的多数票离散计数不同, 本族的底层不是投票计数本身, 而是投票之后落到文章级的一个连续概率分数 llm_prob_score(记作 P(正面) − P(负面) 的 logit-to-score 映射, 呼应 de Kok (2025, Management Science) 关于善用生成式大语言模型输出的置信结构、而非仅取离散硬标签的方法学建议, 而非直接对离散标签取均值)。三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash, 分别记 gpt54nano / gemini31 / deepseekv4) 各自输出一次逐篇情感判定, llm_prob_score 在文章级把三家的判定汇总为一个连续概率语调分, 再经媒体权威性 (media authority) 加权求和、按 bank-year 聚合、除以有效样本的权重之和, 得到本族的 bank-year 语调分。"vote" 前缀在本仓库命名习惯里标识"该测度属于 LLM 三家共识/投票体系产出的族群", 与紧邻的 llm_vote_tone(离散多数票语调)、llm_vote_score_mw_sum(等权求和分子)共享同一构念家族但计算路径不同, 使用者须依据列名后缀 mw_prob 精确定位到"媒体权威加权 + 概率映射"这一具体组合, 不可与同族的 vw_prob (成交量/篇幅加权概率)、hw_prob (跟风衰减加权概率)、裸 mw (等权 vote tone 的媒体权威加权版) 混同。

媒体权威性权重 sum_media_authority_weight 的构念依据 Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体情感对盈余公告后市场反应的"节制热情"效应的证据: 该文发现不同媒体来源的权威性/可信度差异会系统性调节情感信息对市场定价的影响强度, 权威媒体的语调对投资者决策的边际影响显著大于边缘/低权威媒体。本仓库据此将每篇报道所属媒体来源映射为一个权威性权重 (来源于媒体分级/影响力指标, 由 pipeline\panel\media_authority.py 产出并汇总为 sum_media_authority_weight), 在聚合 bank-year 语调时用该权重代替简单等权平均或篇幅加权, 使得来自更具影响力媒体来源的报道在 bank-year 语调分中获得更大权重, 更贴近真实的信息传导强度而非机械的样本计数。

【方法学与计算】
文章级 llm_prob_score 的构造遵循"三家独立判定 → 概率化 → 一致性加总"的路径: 三家 LLM 各自对同一篇报道 (同一轨道文本) 输出情感判断 (正面/负面/中性三分类, 或对应的置信概率), llm_prob_score 将其转换为一个位于约 [-1,1] 区间的连续分数, 与仅取多数票离散标签相比, 该概率化处理保留了模型内部的置信度信息, 缓解了三分类硬投票在决策边界附近的信息损失, 呼应 de Kok (2025, Management Science) 关于在会计与金融文本分析中善用生成式 LLM 输出的置信结构而非仅取硬标签的方法学建议, 以及 Kamen & Kamen (2025) 关于多模型集成 (ensemble) 优于单模型直接分类的实证发现——本族的三家投票机制正是这种集成范式在情感度量上的具体落地。

聚合到 bank-year 层面走两步: 第一步在文章级把 llm_prob_score 乘以该篇报道的 media_authority_weight, 在 bank-year 组内求和得到分子 llm_prob_score_mw_sum{track}; 第二步除以分母, 分母由 `_llm_denom('mw', 'prob', track, mw_denom)` 计算, 核心逻辑是把 sum_media_authority_weight 在 0 值处替换为 NaN (防止除零导致的虚假极端值或运行时错误), 并限定在该 bank-year 组内三家 LLM 均完成有效判定 (verified) 的样本范围内求和, 与家族内其余 mw 加权测度 (如 llm_vote_tone_mw、各词典的 dict_tone_mw) 共享同一个 mw_denom 分母来源, 但因不同上游列 (裸投票语调 vs. 概率分) 分子集合可能不完全重合, `_llm_denom` 对 'mw'/'prob' 场景做了针对 prob 分支的样本口径对齐, 保证分子分母来自同一有效样本集, 避免分子分母口径不一致带来的偏误 (mismatched numerator-denominator bias)。

三个后缀 _full / _ctx / _ss 对应本仓库三轨文本架构: _full 使用标题+全文正文 (prepend_title 后的完整报道文本); _ctx 使用标题+目标银行实体窗口 (围绕银行实体名的局部上下文); _ss 使用标题+银行与金科关键词同句 (或按 config 设定的 ±N 句窗) 共现窗口, 在无银行∧金科同句共现时镜像 _ctx 的回退语义, 退化为使用全文 body 作为 content_ss 且置 ss_is_fallback=True, 与 _ctx 缺失同句证据时的降级处理逻辑完全一致, 分母 n_articles 在回退情形下与非回退情形共享同一计数口径。三轨在留篇门控上遵循 full-only 铁律 (2026-06-29 起生效): 一篇报道是否被判定为"目标银行×金科的有效报道"只由 llm_verified_full 决定, ctx/ss 轨的样本行集合是 full 轨留篇集合的子集, 即 ctx/ss 版本的 llm_vote_tone_mw_prob 只在 full 已确认留篇的文章范围内计算各自轨道的文本内容与权重, 属于"conditional-on-full"的测度/稳健性轨, 不构成独立的留篇判定入口。三轨彼此各自 just-identified 并排, 互为稳健性、不分主次, 严禁将三轨列混入同一个 over-identified 的 Hansen J 检验, 三轨应作为并列稳健性检验呈现, 不应相加或相互替代作为单一识别策略的联立工具。

【文献定位】
本族方法学定位横跨三条文献线索。其一是 LLM 文本情感分析在金融/会计研究中的应用范式, de Kok (2025, Management Science) 系统梳理了生成式大语言模型在会计文本分析中的使用规范 (含 temperature=0、prompt 冻结、结果缓存等可复现性设计, 均已被本仓库 stage 21 的确定性缓存架构采纳), Kamen & Kamen (2025) 论证了多模型多数投票集成相较单模型分类的稳健性优势, 为本族的三家 LLM 共识机制提供直接方法学支撑。其二是媒体权威性/媒体影响力异质性文献, Holzman, Miller & Twedt (2023, The Accounting Review) 是本族媒体权威加权 (mw) 设计的直接实证锚点, 其核心发现是媒体情感的市场影响力随媒体自身权威性/可信度而系统变化, 使得对不同来源报道的简单等权处理会掩盖真实的信息传导强度差异。其三是概率化/连续化情感分数相对离散标签的信息保留优势, 呼应文本情感分析文献中"细粒度情感分数优于粗粒度离散分类"的方法论共识 (如 Pröllochs, Feuerriegel & Neumann (2016) 在否定处理/情感细粒度识别上的工作), 本族用概率映射代替硬投票, 力图在三家 LLM 分类边界模糊的样本上保留更多信息而非強行舍入为单一离散标签。

## VAR: llm_vote_tone_mw_prob_ctx

【变体差分】
本列取 _ctx 轨: 文本输入为"标题 + 目标银行实体窗口"局部上下文 (而非全文), 由 stage 14 ctx_materializer 物化的 content_ctx 提供, 三家 LLM 对该局部窗口独立判定后得到本轨的 llm_prob_score_ctx, 再乘以该篇报道的 media_authority_weight 在 bank-year 组内求和为分子, 除以本轨对应的 mw_denom (取自留篇集合中在 ctx 轨仍有有效样本的 sum_media_authority_weight 之和)。ctx 轨的样本行集合以 full 轨的 llm_verified_full 留篇判定为门控上界 (行宇宙 = full 留篇集子集), 本列因此不构成独立的报道纳入入口, 而是在 full 已确认为"银行×金科相关报道"的前提下, 换用局部实体窗口文本重新度量语调强度, 用于检验语调测度对文本窗口截取范围的敏感性: 若某篇报道语调主要来自围绕银行实体的直接陈述, ctx 与 full 语调应高度一致; 若语调主要来自与银行关系较远的背景段落, 二者会出现系统性偏离, 该偏离本身即是稳健性检验中值得关注的信号。ctx 与 full、ss 三者彼此并排、互为稳健性, 不设主次, 亦不应混入同一 over-identified Hansen J 设定中联合使用。使用者若观察到 ctx 与 full 在同一 bank-year 上出现方向相反或幅度显著不同的语调分, 不应机械取二者均值折衷, 而应将其作为窗口敏感性的证据分别汇报, 并结合该 bank-year 报道量、媒体权威性分布等辅助信息判断哪一轨更贴近研究问题的构念界定; ctx 轨的媒体权威加权分母同样在 0 值处替换为 NaN, 与 full/ss 两轨共享同一套 `_llm_denom` 分母口径构造逻辑, 只是输入的 sum_media_authority_weight 求和范围随 ctx 轨自身可用样本而定。

## VAR: llm_vote_tone_mw_prob_full

【变体差分】
本列取 _full 轨: 文本输入为"标题 + 全文正文" (prepend_title 后的完整报道内容), 是本仓库三轨架构中的默认/主口径轨, 亦是留篇门控 (llm_verified_full) 的判定文本来源本身——一篇报道是否被算作"目标银行与金科科技相关报道"完全由 full 轨三家 LLM 的验证结果决定, ctx/ss 轨的样本范围均以此为上界子集。本列的分子 llm_prob_score_mw_sum_full 汇总的是三家 LLM 在完整报道文本上的概率化情感判定按媒体权威性加权求和的结果, 分母 mw_denom (full 口径) 取该 bank-year 组内所有留篇样本的 sum_media_authority_weight 之和 (0 记 NaN)。在本族三轨"互为稳健性、不分主次"的口径下, full 轨并不因其充当留篇门控的角色而在识别策略上高于 ctx/ss 两轨——三者依然各自 just-identified、并排呈现, 严禁混入同一个 over-identified 的 Hansen J 联立检验; full 轨的特殊性仅体现在样本纳入判定这一预处理环节, 不改变其在稳健性梯子上与 ctx/ss 平级的角色。由于 full 轨文本涵盖整篇报道 (含与目标银行关系较远的背景、行业综述、其他机构对比等段落), 其语调分在直觉上更接近"整体舆论氛围"而非"针对该银行的直接评价", 这正是本仓库设置 ctx/ss 两条更聚焦轨道作为并列稳健性检验的动机——研究者不应默认 full 轨数值天然优于 ctx/ss, 三者的差异本身是可报告、可解释的稳健性证据, 而非需要调和消除的噪声。在实证使用中, 若选择 full 轨作为某一具体回归设定的主口径处理变量 (treatment), 该选择须在方法部分明确披露, 并同时汇报 ctx/ss 两轨的对应回归结果作为并列稳健性附表, 不得只呈现三轨中数值最显著的一支。

## VAR: llm_vote_tone_mw_prob_ss

【变体差分】
本列取 _ss 轨: 文本输入为"标题 + 银行与金科关键词同句 (或按 config `filtering.yaml::context_window.ss_sentence_radius` 设定的 ±N 句窗) 共现窗口", 判定原语与 stage 13 共现硬过滤所用的邻近共现口径 (`has_bank_fintech_cooccurrence_within_radius`) 不同, ss 轨走的是严格同句抽取原语 `extract_bank_fintech_cooccurrence`, 两者刻意区分、禁止互相复用。当某篇留篇文章内不存在银行与金科关键词的同句 (或设定窗口内) 共现证据时, 本列遵循镜像 _ctx 的回退语义: content_ss 退化为使用全文 body, 并置 ss_is_fallback=True, 该情形下的 bank-year 分母 n_articles 与非回退情形共享同一计数口径, 不做额外剔除, 以保证退化处理是"优雅降级"而非静默丢样本。llm_prob_score_ss 由三家 LLM 在 (可能已回退为全文的) ss 轨文本上重新独立判定, 再按 media_authority_weight 加权求和聚合为本列。ss 轨与 full/ctx 两轨一样, 样本行宇宙均以 full 轨 llm_verified_full 留篇判定为上界子集, 属于 conditional-on-full 的稳健性测度, 与 full/ctx 彼此各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 联立设定。ss 轨的构念价值在于把语调度量收窄到银行与金科科技概念真正"同句共现"的最贴近证据处 (而非泛泛的实体窗口或全文), 用于检验语调结论是否依赖于对共现邻近程度的极端严格化假设。

<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
<!-- rendered-citations:end -->
