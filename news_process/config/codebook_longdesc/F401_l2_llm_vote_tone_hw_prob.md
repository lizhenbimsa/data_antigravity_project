---
family_id: F401
columns:
- llm_vote_tone_hw_prob_ctx
- llm_vote_tone_hw_prob_full
- llm_vote_tone_hw_prob_ss
unit: 语调得分 (连续, 理论区间约 [-1,1]; 分子分母均在 bank-year 层聚合, 属 herd-decay 加权均值)
formula: 'llm_vote_tone_hw_prob{track} = llm_prob_score_hw_sum{track} / hw_denom_llm{track} (herd-decay 权重 w_hw 与三家 LLM Logit-to-Score 概率分ADD 的加权和, 除以三家 LLM 共用的 valid-mask 加权分母; {track} ∈ {_full, _ctx, _ss})'
producer: pipeline\panel\encode.py ; pipeline\panel\export.py
upstream: []
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: Federal Reserve Board FEDS Working Paper
  vol: '2026-020'
new_dois: []
---

## CORE

【构念与来源】
`llm_vote_tone_hw_prob` 家族衡量的是「以 herd-decay 时间权重折现后、由三家 LLM 概率化打分聚合而成的银行—金科报道语调」, 是 stage 21 三家 LLM 情感投票 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 输出经 Logit-to-Score 概率映射后, 在 bank-year 面板层用 herd 衰减权重 (herd decay weight, `hw`) 加权聚合的 tone 测度。三家 LLM 是并排的 co-equal 稳健性 (「互为稳健性、不分主次, 各自 just-identified」), 不存在孰主孰次; 本族的 `hw_prob` 是三家投票共识 (`llm_vote_*`) 之下、"prob" 口径分支的 herd 加权版本, 与同一 stage 21 输出族内的"离散多数票版本" (`llm_vote_tone_hw`, 逐篇取三家多数分类 -1/0/1 再加权) 及"简单均值权重版本" (`llm_vote_tone_vw_prob`/`llm_vote_tone_mw_prob`) 并排存在、互为稳健性, 不作为彼此的替代或优化。
"prob" 来源于文献所称的 Logit-to-Score 映射: 与直接取三分类标签 (负/中/正 → {-1,0,1}) 不同, prob 口径让每篇文章的 LLM 情感判断保留连续概率信息 (源码注释标注对应 Törnberg 2023 / Shapiro 2022 的方法论谱系), 即模型输出的类别概率分布经变换映射为一个 [-1,1] 区间上的连续分数 `llm_prob_score`, 而非离散投票结果 (`llm_vote_score`)。因此 `hw_prob` 与家族之外的 `llm_vote_tone_hw` 在"分子来源列"上就已经分道: 前者累加 `llm_prob_score_hw_sum{track}` (概率化连续分), 后者累加 `llm_vote_score_hw_sum{track}` (多数投票离散分), 两者共享同一套 herd-decay 权重体系 (`hw`) 与 valid-mask 分母思路, 但不是同一构念的两种写法, 而是"投票 vs 概率"两条并行的语调编码策略。
herd-decay 权重的经济学直觉是: 银行—金科舆论存在"羊群效应" (herding) — 密集报道期内单篇文章的边际信息含量会随同期报道数量的增多而衰减, 若不加权直接简单平均, 会让"扎堆报道"的时点在 bank-year 聚合中获得不成比例的权重, 掩盖真正具有独立信息含量的报道。herd-decay 加权体系通过对每篇文章赋予随同期"同伴报道密度"衰减的权重 `w_hw`, 抑制这种拥挤效应, 使聚合语调更贴近"信息含量加权"而非"篇数加权"的均值。这一权重体系与 vw (view/简单等权) 、mw (media-weight, 媒体权威加权) 并列为三套并行的聚合权重方案, 同样互为稳健性、不分主次, 不构成对彼此的替代。
本族列名承接 `llm_vote_tone_{hw}_{prob}` 的三段式命名法: 首段 `llm_vote_tone` 标识"三家 LLM 投票共识语调"这一构念族; 中段 `hw` 标识聚合权重方案 (herd-decay); 末段 `prob` 标识分子编码口径 (Logit-to-Score 概率映射, 与 vw/mw 版本共用相同的 prob 后缀语义)。三轨后缀 `_full`/`_ctx`/`_ss` 附加在末尾, 标识文本窗口口径。

【方法学与计算】
计算发生在两个阶段。stage 21 (`tone_llms.py`) 逐篇产出三家 LLM 的原始判断与经 Logit-to-Score 变换的概率分 `llm_prob_score{track}`, 同时结合当期同伴报道密度算出 herd-decay 权重 `w_hw{track}`; 面板聚合层 (`pipeline\panel\encode.py`) 对每个 bank-year 单元, 先把已按 herd-decay 权重加权的分子汇总为 `llm_prob_score_hw_sum{track}`, 再由赋值行 `panel_new_cols[f'llm_vote_tone_hw_prob{track}'] = panel[w_prob] / _llm_denom('hw', 'prob', track, hw_denom)` (源码摘录 L2311-L2314) 一步完成除法, 分母是该 bank-year 单元内三家 LLM 共用的 valid-mask 加权分母, 得到最终的 `llm_vote_tone_hw_prob{track}`。分母函数名里 `'prob'` 标识这是概率口径专属的有效样本掩码 (valid-mask): 只累计三家 LLM 中确实给出有效判断的样本对应的 herd-decay 权重, 避免某篇文章因某家 LLM 缺席判断而被错误地稀释或放大分母。这一"分子分母同域"设计与家族外的 `{short}_tone_hw{track}` (单模型版本, 分母走各自模型专属的 `_llm_denom('hw', short, track, hw_denom)`) 是同一套设计模式, 但本族 `prob` 分母专属于概率口径, 与单模型分母、离散投票分母互不通用 (禁止跨口径混用分子分母)。
`hw_denom` 本身来自面板中已算好的 `sum_herd_weight{track}` 列 (对 0 值以 NaN 替换以避免除零), 三轨各自维护独立的 herd-decay 权重和, 不共享分母 — 这与三轨"各自 just-identified 并排"的铁律一致: full/ctx/ss 三条文本窗口各自形成一套完整的分子-分母配对, 不允许把某一轨的分子除以另一轨的分母。stage 21 的留篇门控是 full-only 口径 (2026-06-29 起): 一篇报道是否计入"银行—金科报道"样本只看 `llm_verified_full == True`, ctx/ss 两轨是在 full 已确认留篇的行宇宙子集上计算的 conditional-on-full 测度/稳健性轨, 而非独立样本。
`_ss` 轨的回退语义镜像 `_ctx`: 当某篇文章没有银行∧金科词同句共现时, `content_ss` 退化为全文正文 (`ss_is_fallback=True`), 该篇文章仍参与 `_ss` 轨的语调计算, 但使用的文本窗口实质等同全文轨; 若上游 `FINTECH_AC` 词典对象为 `None`, 则 `_is_fallback` 列全体置 True, 三轨优雅降级为等价的全文计算而非报错清空。

【文献定位】
本族聚合体系呼应 de Kok (2025, *Management Science*) 对生成式 LLM 用于会计/金融文本分析的方法论规范: 温度固定为 0、prompt 版本冻结、结果可离线复现缓存, 与本仓库 stage 21 的确定性锚点设计 (prompt v8 字节级冻结、`NEWS_PROCESS_LLM_OFFLINE=1` 离线可复现) 同源。三家 LLM 并排投票而非单一模型专断的设计, 对应 Kamen & Kamen (2025) 关于"LLM 集成 (ensemble) 优于单模型"的多数票聚合思路; 三家互为稳健性、不设主次的定位, 又与 Hansen (2026, FEDS WP) 在无金标准场景下用一致性指标 (κ/α) 验证 LLM 标注质量的思路呼应 — 本仓库对应的多模型一致性度量 (Krippendorff's α、Cohen's κ) 在 `tone_validation.py` 落地。概率化 (prob) 相对离散投票 (vote) 的取舍, 承接文本情感测量三角中"词典法 vs 机器学习法"关于信息颗粒度的经典对比 (Frankel, Jennings & Lee, 2022, *Management Science*): 保留连续概率而非坍缩为三分类标签, 让下游回归可以捕捉语调强度而非仅方向。herd-decay 加权对拥挤报道的降权处理, 延续 Du et al. (2022, *Review of Finance*) 关于中文金融情感测度需针对中国媒体语境做定制化权重设计的方法论精神 (该文也是本仓库政治词权重敏感性设计的原始出处)。

## VAR: llm_vote_tone_hw_prob_ctx

【变体差分】
本列是 `llm_vote_tone_hw_prob` 家族在 ctx (context) 轨的实现: 分子分母均限定在实体窗口文本 (`content_ctx` = 标题 + 目标银行实体前后窗口) 上计算, 即 `llm_prob_score_hw_sum_ctx` 除以 ctx 轨专属的 herd-decay 加权 valid-mask 分母 `_llm_denom('hw', 'prob', '_ctx', hw_denom_ctx)`。ctx 轨与 full 轨、ss 轨各自独立维护 `sum_herd_weight_ctx` 权重和, 不与另外两轨共享分母, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。
留篇门控口径 (2026-06-29 起) 是 full-only: 一篇文章是否被判定为"一篇有效的银行—金科报道"完全由 `llm_verified_full` 决定, 本列 (ctx 轨) 的行宇宙是 full 轨留篇集合的子集, 属于 conditional-on-full 的测度/稳健性轨, 而非独立抽样样本; 因此本列不能单独用来重新定义样本口径, 只能在 full 轨已确定的留篇集合内部提供"缩窄到实体窗口文本"的语调稳健性参照。与 full 轨相比, ctx 轨的文本窗口更聚焦, 剔除了与目标银行实体距离较远的段落, 因而对无关新闻噪声更不敏感, 但也可能因窗口过窄丢失部分上下文信息 (例如否定/转折结构跨窗口边界时的语义完整性); 这正是 ctx 轨作为 full 轨稳健性参照而非替代的设计初衷: 若 hw_prob 的 full 与 ctx 两轨方向一致、量级相近, 说明结论不依赖窗口宽窄的具体选取, 也不因裁窗而引入系统性的语调偏移。

## VAR: llm_vote_tone_hw_prob_full

【变体差分】
本列是 `llm_vote_tone_hw_prob` 家族在 full 轨的实现, 也是三轨中的留篇门控锚 (full-only gate, 2026-06-29 起): 一篇报道是否算作"一篇被留下的银行—金科报道"只看 `llm_verified_full == True`, 这一判定同时决定了 full/ctx/ss 三轨共同的行宇宙, ctx 与 ss 是该行宇宙子集上的 conditional-on-full 稳健性轨。本列的分子分母口径为标题+全文正文 (`content_full`) 上累计的 `llm_prob_score_hw_sum_full` 除以 full 轨专属的 `_llm_denom('hw', 'prob', '_full', hw_denom_full)`, herd-decay 权重和 `sum_herd_weight_full` 是 full 轨独立维护的分母来源, 不与 ctx/ss 轨共享。
在 P1 (`bank_fintech_tone`) 论文主线中, 与本列同构的 `llm_vote_tone_full`/`llm_vote_tone_hw_full` (离散投票版本) 是主处理变量 (treatment.primary) 的口径锚, 而 `hw_prob_full` 作为概率化 (Logit-to-Score) 分支的 herd 加权版本, 与之并排提供"连续强度信息 vs 离散方向信息"的互补稳健性视角 — 二者共享同一套 full-only 留篇门控和同一套 herd-decay 权重体系, 差异仅在于分子来自概率分还是投票分, 不构成互为主次的替代关系, 而是同一构念下两条并行的编码策略。
由于本列是三轨中唯一直接决定行宇宙 (留篇门控) 的一轨, 它同时承担两个角色: 一是作为 hw_prob 家族三轨并排稳健性中的一支, 二是作为整条留篇判定链的锚点, 后一角色不因"三轨并排、不分主次"的铁律而被削弱 — 三轨"不分主次"仅指测度层面的稳健性地位平等, 不改变 full 轨在样本选择层面的锚定角色。分析时若只报告一条主结果, 通常以本列 (或与之同构的离散投票版本) 作为 headline 数字, ctx/ss 两轨作为附录稳健性表呈现, 三者在识别策略上互不替代, 但样本口径统一继承自本列所定义的留篇集合。

## VAR: llm_vote_tone_hw_prob_ss

【变体差分】
本列是 `llm_vote_tone_hw_prob` 家族在 ss (same-sentence) 轨的实现: 分子分母均限定在"目标银行∧金科关键词同句共现窗口" (`content_ss`, 标题 + 同句窗口, 半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句) 上计算, 即 `llm_prob_score_hw_sum_ss` 除以 ss 轨专属的 `_llm_denom('hw', 'prob', '_ss', hw_denom_ss)`, 权重和 `sum_herd_weight_ss` 由 ss 轨独立维护, 不与 full/ctx 两轨共享分母。ss 轨在三轨判据严格性上最紧: 要求银行实体与金科关键词在同一句 (或其邻近半径窗口) 内共现, 是三轨中口径最"贴身"的一支, 与 ctx 轨"实体前后窗口"、full 轨"全文"形成从紧到松的判据梯度, 三者仍是各自 just-identified 并排的稳健性关系, 而非严格性排序意义上的主次。
本列继承 ss 轨对 ctx 轨的回退语义: 当某篇文章不存在银行∧金科词同句共现时, `content_ss` 退化为全文正文, 该篇文章的 `ss_is_fallback` 标记为 True, 但仍参与 hw_prob 的 ss 轨计算 (共享同一 `n_articles` 分母口径, 不因回退而被剔除样本)。若上游 `FINTECH_AC` 分词自动机不可用 (`None`), 三轨的 `*_is_fallback` 全部置 True, 即 ss 轨此时优雅退化为与 full 轨等价的全文计算, 而非清空报错, 与 ctx 轨在同一场景下的降级行为完全对称。留篇门控依旧遵循 full-only 铁律, ss 轨的行宇宙是 full 轨留篇集合的子集, 属于 conditional-on-full 的判据敏感性稳健性轨, 与网络三轨/建构判据敏感性 (2026-07-03) 中"判据后缀 ≠ 三轨文本后缀"的既有区分并列, 但本族 ss 轨本身就是"文本窗口口径", 不属于判据后缀家族, 二者互不冲突亦互不可替代。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
</content>
