---
family_id: F569
columns:
- tone_gap_comp_other_ctx
- tone_gap_comp_other_full
- tone_gap_comp_other_ss
unit: 语调缺口 (连续, 两个 [-1,1] 语调均值之差, 理论区间 [-2,2]; bank-year 聚合)
formula: 'tone_gap_comp_other{track} = mean(llm_vote_score{track} | 媒体类型=综合类 comp) - mean(llm_vote_score{track} | 媒体类型=其他类 other), 逐 (target_bank, year) 分组计算; track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- llm_vote_score_full
- llm_vote_score_ctx
- llm_vote_score_ss
- _media_type
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: Media Bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
new_dois: []
---

## CORE

【构念与来源】
本家族刻画同一银行-年度窗口内, 综合类媒体 (comp) 与其他类媒体 (other) 对同一目标银行报道语调的系统性差异, 是媒体异质性 (media heterogeneity) 测度族的第②维缺口指标。上游 `_media_type` 由 `pipeline/panel/attention_media.py` 对报道来源 (媒体中文名) 做三分类映射 {fin, comp, other}: fin 对应财经/金融专业媒体, comp 对应综合类 (面向大众议题的都市报/门户/通讯社等), 其余归入 other (行业垂类、地方小报、非主流渠道等剩余类)。这一分类学承袭 You, Zhang & Zhang (2018) 关于中国媒体"谁执掌笔杆子"的机构异质性框架 — 不同属性的媒体在报道立场、专业审核强度、编辑独立性上系统不同, 因而对同一事件的语调表达不是随机噪声, 而是媒体机构属性的函数。综合类媒体覆盖面广、读者基数大, 议题选择更受市场关注度和大众可读性驱动; other 类多为专业性与审核强度更弱、议题来源更碎片化的剩余渠道。三类占比 (`fin_media_frac`/`comp_media_frac`, other 为补集) 与三类情感均值 (`tone_fin_media{track}`/`tone_comp_media{track}`/`tone_other_media{track}`) 在同一循环中一并产出, 本家族的三个缺口列 `tone_gap_comp_other{track}` 是其中 comp − other 一支; 姊妹族 `tone_gap_fin_other{track}` (fin − other) 与 `tone_gap_fin_comp{track}` (fin − comp) 覆盖另两个两两对比, 三者共同穷尽三类媒体两两差异的完整信息集, 互不冗余。

【方法学与计算】
计算发生在 `attention_media.py` 的媒体异质性主循环: 先以 `df['_media_type'] == mt` 布尔掩码切出该类别子样本, 按 `(target_bank, year)` 分组对语调列 `llm_vote_score{track}` 取均值, 得到 `tone_{sfx}_media{track}`; comp 与 other 两支均值算出后, 逐格相减得到 `tone_gap_comp_other{track} = tone_comp_media{track} - tone_other_media{track}`。语调源列 `llm_vote_score{track}` 是 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票产出的篇章级共识语调, 值域约 [-1,1]; 三轨分别对应 full/ctx/ss 三种文本窗口 (见下文口径说明), 循环内用 `if src not in df.columns: continue` 优雅跳过缺失轨道, 三轨互不依赖。差值本身理论区间 [-2,2], 但因两侧均值都是同一 LLM 共识分布的子样本均值, 实践中集中在更窄区间; 正值表示综合类媒体对该银行的语调系统性优于其他类媒体, 负值反之, 接近 0 表示两类媒体对该银行的报道基调无系统差异。分组内若某类别在该 (银行, 年) 格内样本为空 (如某银行某年完全没有 comp 类报道), 对应 `tone_comp_media{track}` 为缺失, 缺口列随之缺失并向下游透传 (NaN, 而非 0), 不做人为填补; 这一"零篇即缺失"处理与家族②③④维度 (占比/央地/官方-市场等) 的所有情感均值列共享同一 groupby-mean 实现模式, 是本 producer 的统一约定, 非本列独有设计。

【文献定位】
媒体作为信息中介、其自身机构属性系统影响新闻语调这一命题, 在金融文本分析文献中已有成熟脉络。You, Zhang & Zhang (2018, *The Review of Financial Studies*) 在中国背景下证明媒体的所有权/属地/市场化程度会系统影响其报道倾向 ("谁执掌笔杆子"), 是本家族"按媒体类别拆分语调并比较缺口"这一设计范式的直接理论出处。Tetlock (2007, *Journal of Finance*) 确立了媒体语调是可计量、可预测市场结果的信息载体这一基础命题, 使"语调差异"本身成为有经济含义的构念而非纯描述统计。Qin, Strömberg & Wu (2018, *American Economic Review*) 进一步在中国媒体制度背景下刻画不同媒体类型 (官方/市场化) 的系统性偏向, 为本家族"综合类 vs 其他类"的二分对比提供了制度背景支撑。Holzman, Miller & Twedt (2023, *The Accounting Review*) 显示媒体语调的约束作用因媒体权威性/覆盖面不同而异质, 呼应本族"缺口"构念背后"哪类媒体更有纪律约束力"的经济学问题。Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 在中国银行业情境下直接使用媒体情感异质性作为解释变量, 是与本家族对象 (中国银行) 和方法 (媒体分类×语调) 最贴近的同域文献。本家族的经济学价值在于: 简单的银行-年度语调均值会把"综合媒体报道热闹但基调温和"与"专业垂类媒体报道稀少但基调极端"两种迥异情形混为一谈; comp − other 缺口把媒体构成异质性从总体语调中分离出来, 使研究者能够单独检验"哪类媒体驱动了该银行整体语调的走向", 并可作为总体语调的稳健性检验或作为媒体关注结构 (attention composition) 的独立解释变量使用。

## VAR: tone_gap_comp_other_full

【变体差分】
`_full` 轨对应源语调列 `llm_vote_score_full`, 该列以标题+全文正文作为 LLM 判读输入。这是三轨中的 full-only 主口径: 依据 2026-06-29 起生效的留篇门控规则, 一篇报道是否计入"银行-金科相关"样本, 完全由 `llm_verified_full == True` 决定, 与 ctx/ss 轨的验证结果无关; ctx/ss 轨降级为"conditional on full"的测度性/稳健性轨, 其行宇宙是 full 轨留篇集合的子集。因此 `tone_gap_comp_other_full` 是三轨中样本覆盖最完整、分母口径最贴近论文主线留篇标准的一支, 也是最贴近上游 `attention_media.py` 主循环诊断日志 (内容分类占比、行政分类占比等) 所依附的留篇口径。三轨 (full/ctx/ss) 之间彼此互为稳健性、各自 just-identified 并排, 不设主次高下之分; 在计量模型中三轨语调各自独立进入回归、不得混入同一个 over-identified 的 Hansen J 过度识别检验框架 (镜像 co-primary 双轨嵌入、政治词权重梯度等家族的通用铁律)。full 轨的语调判读窗口最宽, 能捕捉正文深处才出现的语气转折与限定条件 (例如先陈述行业性负面事件、后单独澄清目标银行未受波及的报道结构), 但也因此更容易被文章中与银行本身无直接关系的背景段落 (宏观经济评述、行业整体走势) 稀释语调信号, 使得同一篇报道在 full 轨下的语调判读值可能比 ctx/ss 轨更贴近"中性"。使用者若关心的是媒体对银行整体报道基调 (而非仅围绕银行本身的局部措辞), full 轨的 comp − other 缺口是首选参照; 若关心局部措辞精度, 应同时参照 ctx/ss 两轨互为印证, 而非以 full 轨单轨下结论。

## VAR: tone_gap_comp_other_ctx

【变体差分】
`_ctx` 轨对应源语调列 `llm_vote_score_ctx`, 该列以标题+目标银行实体窗口 (实体前后若干句的局部文本) 作为 LLM 判读输入, 而非全文。ctx 轨的行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 不单独门控留篇资格; 当某篇文章缺失 ctx 语调值时, 该篇不参与 comp/other 分组均值的计算, 与 full 轨的样本处理方式一致地遵循"零篇即缺失"约定, 即某 (银行, 年) 格若因样本量不足而使 comp 或 other 任一类别落空, 该格的 `tone_gap_comp_other_ctx` 直接缺失, 不做插补。ctx 轨与 full 轨、ss 轨互为稳健性并排关系, 三者各自 just-identified, 禁止混入同一个过度识别的 Hansen J 检验。相对 full 轨, ctx 轨的语调判读窗口更聚焦于银行实体周边语境, 能减少与银行本身无关的背景段落对语调判读的稀释, 但也可能因窗口过窄而丢失需要跨段落信息才能判断的语气转折 (如"先扬后抑"的论述结构, 或先叙述行业负面再单独澄清个体银行安全的报道套路)。当 `llm_vote_score_ctx` 因文章缺少可识别实体窗口而无法生成时, 该篇的 ctx 语调值缺失, comp/other 分组均值及本缺口列相应传导缺失 (非静默填 0)。与 `_ss` 轨相比, ctx 轨的窗口相对宽松 (实体窗口而非同句窗口), 在样本覆盖率与判读局部化程度之间取一个折中点, 适合作为 full 与 ss 两个极端之间的过渡性稳健性检验。

## VAR: tone_gap_comp_other_ss

【变体差分】
`_ss` 轨对应源语调列 `llm_vote_score_ss`, 该列以标题+银行与金科关键词同句共现窗口 (句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 生产默认 ±1 句) 作为 LLM 判读输入, 是三轨中窗口最窄、判读粒度最精细的一支。`_ss` 轨的回退语义镜像 `_ctx`: 当某篇文章不存在银行与金科词的同句共现时, 该篇的 `content_ss` 退化为全文正文 (等同于 full 轨的文本输入), 并置位 `ss_is_fallback=True`, 与 ctx 轨共享同一套 `n_articles` 分母口径, 优雅降级而非直接判缺失; 若 `FINTECH_AC` 关键词自动机整体不可用 (`None`), 则全体 `*_is_fallback` 置 True, 所有文章统一退化为 full 文本输入。行宇宙同样是 full 轨留篇集合的子集 (conditional-on-full), 不单独承担留篇门控职责。ss 轨与 full、ctx 轨互为稳健性并排, 三者各自 just-identified、禁止混入同一个 over-identified Hansen J 检验。相对 ctx 轨, ss 轨的判读窗口进一步收窄到"同句"这一最严格共现标准, 理论上语调信号与银行-金科关联的相关性最强, 但对存在退化 (fallback) 的文章而言, 其语调判读实际上等同于 full 轨、并非真正的窄窗口判读, 使用时须结合 `ss_is_fallback` 标记区分"真严格同句判读"与"退化为全文判读"两类样本, 避免把退化样本误当作窄窗口精细判读混入解释。ss 轨与 full、ctx 轨同属互为稳健性并排关系, 各自 just-identified, 三者禁止混入同一个过度识别的 Hansen J 检验; 在解释 `tone_gap_comp_other_ss` 与另两轨结果不一致时, 应优先检查该差异是否源于 fallback 比例在 comp 与 other 两类媒体子样本间的不均衡分布, 而非直接归因于窗口宽窄本身的测度差异。当某 (银行, 年) 格的 comp 或 other 子样本在 ss 轨全部退化为 fallback 时, 该格的缺口值等价于 full 轨对应格, 两者应高度一致, 可作为交叉校验的参照。
<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Qin, B., Strömberg, D., & Wu, Y. (2018). Media Bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
