---
family_id: F535
columns:
- sum_wd_hw_thr45_llm_ctx
- sum_wd_hw_thr45_llm_full
- sum_wd_hw_thr45_llm_ss
unit: 无量纲权重和 (跟风衰减权重在阈值 thr45 标签下的银行-年求和, 用作加权平均语调的有效分母)
formula: 'sum_wd_hw_thr45_llm{track} = Σ_i∈bank-year herd_weight{track}_thr45_i · 1[llm_vote_score{track}_i 非缺失], 其中 herd_weight{track}_thr45 由 stage 24 herd_decay_processor 按敏感性网格阈值 τ=0.45 (sensitivity_thresholds 网格标签 thr45) 逐篇算得的跟风衰减权重; track ∈ {full, ctx, ss}'
producer: pipeline\panel\encode.py::aggregate_panel (F5b 阈值敏感性 HW 聚合块) ; pipeline\panel\runner.py (步骤 3d-2 阈值敏感性 HW 加权列生成, `_wd_hw_{tag}_llm{track}` 逐篇列)
upstream:
- pipeline\sentiment\herd_decay.py (stage 24, herd_weight{track}_thr45 逐篇跟风衰减权重, sensitivity_thresholds 网格)
- pipeline\panel\tone_llms.py (llm_vote_score{track}, 三家 LLM 多数投票语调分)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating Large Language Model Annotations
  venue: 'FEDS Working Paper No. 2026-020, Federal Reserve Board'
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
new_dois: []
---

## CORE

【构念与来源】
本家族三列 `sum_wd_hw_thr45_llm_{full,ctx,ss}` 度量的不是情感本身, 而是"用来对情感加权求平均的分母权重之和"——具体讲, 是银行-年样本内、在跟风衰减阈值敏感性网格取 τ=0.45 (网格标签 thr45) 这一档时, 全部 LLM 投票语调 (`llm_vote_score{track}`) 非缺失篇章的跟风衰减权重 (`herd_weight{track}_thr45`) 逐篇求和。它是 `sum_wd_hw_{tag}_llm{track}` 系列 (`pipeline\panel\encode.py` F5b 阈值敏感性 HW 聚合块) 中 tag=thr45 的实现, 与 `llm_vote_score_hw_thr45_sum{track}` (分子: 语调分乘权重后求和) 配对使用, 二者相除即得到"阈值 τ=0.45 口径下、跟风衰减加权的银行-年 LLM 语调均值"。该构念的经济学根基是跟风/媒体羊群 (herding) 文献对新闻价值随时间衰减、且同期同题材报道彼此非独立信息含量的关切: Tetlock (2007, *Journal of Finance*) 最早系统证明媒体语调对资产价格有独立于基本面的短期冲击, 但同一事件被多家媒体反复"转载/跟风"报道会人为放大某一语调方向的样本权重, 若不加权直接对篇章取算术平均, 会把"重复报道次数"误当作"信息强度"。本项目的跟风衰减处理 (stage 24 `herd_decay_processor`) 为每篇报道打一个衰减权重: 与近邻时间窗内高相似度报道越"扎堆", 权重越低; 该权重本身还依赖一个"多相似即算跟风"的判定阈值 τ, 生产口径主阈值另有专门列族, 而 thr45 是该阈值敏感性梯子上 τ=0.45 这一档的权重口径, 用来验证主结论 (通常取另一个默认阈值) 是否对"多相似算跟风"这条判定线的具体取值敏感。
【方法学与计算】
计算链条分两段。第一段在 stage 24: `herd_decay_processor` 按 `config` 中 `herd_detection.sensitivity_thresholds` 网格 (由 `herd_sensitivity_grid(CONFIG)` 解析出多个 `(τ, tag)` 对, 45 对应 τ=0.45) 为每篇报道、每条轨道分别算出 `herd_weight{track}_thr45` 列, 权重值域通常落在 (0,1], 值越低表示该篇报道与窗口内其他报道的语义/主题相似度越高、越像"跟风稿"。第二段在 `pipeline\panel\runner.py` 步骤 3d-2: 对每个阈值标签 `_tag` 与每条轨道 `track`, 先取 `w_src = herd_weight{track}_{tag}`, 用 `hw_t = df[w_src].fillna(1.0)` 把缺失权重回退为 1 (即"无法判定跟风程度时不打折"), 再构造 `_wd_hw_{tag}_llm{track} = hw_t.where(df[f'llm_vote_score{track}'].notna())` ——这一步是本列的核心: 仅当该篇章在对应轨道上有非缺失的 LLM 投票语调分时才保留权重值, 否则整体置缺失 (而非置零), 这样后续 `groupby(bank, year).sum()` 会自动按 pandas 的 NaN 跳过语义排除该篇, 分子分母始终共享同一"有效样本掩码", 避免分子分母行数不对齐导致的加权均值系统性偏误。第三段在 `pipeline\panel\encode.py` 聚合阶段: `agg[f'sum_wd_hw_{_tag}_llm{track}'] = (f'_wd_hw_{_tag}_llm{track}', 'sum')` 对每个银行-年做 groupby-sum, 即本列的最终产出值。三条轨道 full/ctx/ss 的权重列、语调源列、共现判据均各自独立计算, 互不借用彼此的样本或权重, 三轨各自 just-identified 并排、互为稳健性不分主次, 禁止把三轨权重和混入同一个 over-identified 的 Hansen J 过度识别检验框架。ss 轨若某篇报道无银行∧金科同句共现, 按 ss 回退语义镜像 ctx (`content_ss`=全文 body, `ss_is_fallback=True`), 该篇是否进入本列求和仍只取决于 `llm_vote_score_ss` 是否非缺失, 与是否发生 ss 回退无关。留篇门控口径 (2026-06-29 起) 是 full-only: 一篇报道是否被算作"银行金科报道"只看 `llm_verified_full`, ctx/ss 轨的本列求和行宇宙是 full 留篇集的子集, 三轨各自照算权重与分母, 不因 ctx/ss 单独缺席而改变 full 轨的样本。
【文献定位】
方法学上, 本列所依托的"LLM 投票语调 + 权重敏感性网格"设计呼应两条平行文献。其一是 LLM 文本标注可靠性文献: de Kok (2025, *Management Science*) 强调会计/金融文本分析中用生成式 LLM 做标注时须固定 temperature=0、冻结 prompt 版本并做可复现缓存, 本项目 stage 21 的三家 LLM 多数投票语调 (`llm_vote_score`) 正是在该规范下产出, thr45 权重和只是对这一已冻结语调分做敏感性再加权, 不改变底层标注本身; Hansen (2026, FRB FEDS 工作论文) 讨论在缺乏人工金标准时如何验证 LLM 标注的有效性, 本项目用阈值敏感性梯子而非单一权重口径, 正是该验证逻辑在跟风衰减维度上的具体落地; Gilardi, Alizadeh & Kubli (2023, *PNAS*) 证明 ChatGPT 类模型在文本标注任务上可比肩众包人工, 为把 LLM 投票语调当作可信的加权对象提供了外部效度支撑。其二是媒体语调-价格文献的方法论传统: Tetlock (2007) 确立了"媒体语调是独立于基本面的定价信息"这一构念, 本列的跟风衰减权重正是为了防止该信息被同题材重复报道人为放大, 使得银行-年层面的加权语调更接近"独立信息条数"而非"文章条数"的度量。三列共同构成阈值敏感性稳健性梯子中 τ=0.45 这一档的求和分母, 需与其余阈值标签、以及跟风衰减主口径的对应分母列并排比较, 以证明主回归结论不依赖某一个具体的跟风判定阈值取值。

## VAR: sum_wd_hw_thr45_llm_ctx

【变体差分】
本列是 ctx 轨 (标题+实体窗口文本) 在阈值敏感性标签 thr45 (τ=0.45) 下的跟风衰减权重求和分母。权重源列为 `herd_weight_ctx_thr45`, 掩码条件为 `llm_vote_score_ctx` 非缺失, 即只对 ctx 轨有效 LLM 投票语调的篇章计入权重和。ctx 轨的文本窗口 (标题+实体窗口, 非全文) 意味着跟风相似度判定所依赖的文本内容与 full 轨不同——两篇报道即便在 full 轨上高度相似, 在 ctx 轨截取的实体窗口内也可能差异更大 (或更小), 因此 `herd_weight_ctx_thr45` 与 `herd_weight_full_thr45` 是各自独立算出的权重序列, 不能相互替代或折算, 也不能用一轨的权重和去反推另一轨的加权均值。ctx 轨的留篇行宇宙是 full 轨留篇集的条件子集: 依据 full-only 门控, 一篇报道先由 `llm_verified_full` 判定是否为银行金科报道, ctx 轨在该子集内再各自独立计算权重与是否非缺失, 因此本列样本量恒不大于对应的 full 轨列。本列与 full 轨对应列 (`sum_wd_hw_thr45_llm_full`) 互为稳健性并排, 用于验证"缩窄到实体窗口文本后, τ=0.45 口径下的加权语调结论"是否与全文口径一致; 二者以及 ss 轨对应列各自 just-identified, 禁止混入同一个 over-identified Hansen J 检验, 也不应在同一回归方程中同时作为工具变量或加权分母使用。thr45 这一具体阈值取值本身无特殊经济含义, 仅是敏感性网格上的一个采样点, 解读时应结合梯子上其余阈值列的走势, 而非单独依赖本列判断结论稳健性。

## VAR: sum_wd_hw_thr45_llm_full

【变体差分】
本列是 full 轨 (标题+全文正文) 在阈值敏感性标签 thr45 (τ=0.45) 下的跟风衰减权重求和分母, 是家族内唯一对应"主留篇门控轨道"的列: 依据 2026-06-29 起生效的 full-only 留篇口径, 一篇报道是否被认定为"银行-金科报道"只看 `llm_verified_full`, 因此本列 (以及配对的分子列 `llm_vote_score_hw_thr45_sum_full`) 所覆盖的样本宇宙即为该门控下的完整留篇集, ctx/ss 两轨的对应列是以此为超集的条件子集稳健性轨, 而非独立的替代样本。权重源列为 `herd_weight_full_thr45`, 掩码条件为 `llm_vote_score_full` 非缺失, 缺失权重先由上游 `.fillna(1.0)` 回退为不打折再参与 `.where` 掩码, 因此本列的数值只受"该篇是否有有效语调分"驱动, 不受"该篇是否成功算出跟风相似度"驱动。该列与主跟风衰减权重和列 (`sum_herd_weight_full`, 无阈值后缀, 对应生产默认阈值口径) 构念相同、阈值取值不同, 二者及其余阈值标签 (如 thr35/thr40 等敏感性网格档次) 对应列共同构成一条"阈值敏感性梯子": 各档次各自 just-identified 并排, 互为稳健性、不分主次, 用于证明主回归结论不依赖 τ=0.45 或其他任一具体判定门槛的取值, 禁止把跨阈值的多个权重和列混入同一个过度识别的 Hansen J 检验框架, 也不应把它们同时纳入同一 IV 方程的多个工具。

## VAR: sum_wd_hw_thr45_llm_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句共现窗口) 在阈值敏感性标签 thr45 (τ=0.45) 下的跟风衰减权重求和分母。权重源列为 `herd_weight_ss_thr45`, 掩码条件为 `llm_vote_score_ss` 非缺失。ss 轨判据比 ctx 更严格: 要求银行实体与金科词汇出现在同一句 (窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1, 与 stage 13 `cooccurrence_filter.sentence_radius` 是不同键, 两者不可混淆), 若某篇报道未满足同句共现, 其 `content_ss` 按镜像 ctx 的回退语义退化为全文 body 且 `ss_is_fallback=True`; 无论是否发生该回退, 本列的求和条件只看对应轨道的 `llm_vote_score_ss` 是否非缺失, 回退篇章仍与共享 `n_articles` 分母口径保持一致地计入, 不会因为触发回退而被单独剔除或单独加权。ss 轨的跟风相似度判定同样基于 ss 轨自身的文本窗口独立计算, 与 full/ctx 两轨的权重列在数值上互不可比、不可混用或相互折算; 若 `FINTECH_AC` 缺失导致金科词典不可用, ss 判据整体优雅降级为 `*_is_fallback` 全 True, 本列仍按上述掩码规则照常求和, 不会静默清空。三轨 (full/ctx/ss) 权重和列各自并排、互为稳健性不分主次, 禁止混入同一个 over-identified Hansen J 检验, 亦不应在同一识别策略中充当互相替代的工具变量集。同 full/ctx 两轨一样, ss 轨的 thr45 权重和只是阈值敏感性梯子上的一个采样点, 判断结论稳健与否须结合梯子上其余阈值标签的对应列走势综合评估, 而非孤立解读本列的绝对数值。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Hansen, A. L. (2026). Validating Large Language Model Annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
