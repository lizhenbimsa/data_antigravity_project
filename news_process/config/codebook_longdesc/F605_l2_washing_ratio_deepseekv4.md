---
family_id: F605
columns:
- washing_ratio_deepseekv4
- washing_ratio_deepseekv4_ctx
- washing_ratio_deepseekv4_ss
unit: 比率 (proportion, 定义域 [0,1]; 分母为零时置缺失, 不强制填零)
formula: 'washing_ratio_deepseekv4{track} = pos_symb_count_deepseekv4{track} / pos_count_deepseekv4{track} (银行-年聚合); 篇章级: _llm_pos{track} = (deepseekv4_score{track}.fillna(0) > 0); _svd_deepseekv4_pos{track} = _llm_pos{track} & (innovation_substantiveness_full 已成功测出 ∈ {"实质性","象征性"}); 分子= _svd_deepseekv4_pos{track} 篇中 innovation_substantiveness_full=="象征性" 的篇数加总, 分母= _svd_deepseekv4_pos{track} 篇数加总 (同域分母, 二者共享同一 deepseekv4 正面且实质性分类成功测出的文章子集)'
producer: "pipeline/panel/runner.py (方法 A2 单模型洗稿率: src_col=f'{llm}_score{track}'; _llm_pos=(_src>0); washing_cols[f'_svd_{llm}_pos{track}']=(_llm_pos and _subst_measured), 面板层由 {llm}_pos_count{track}/{llm}_pos_symb_count{track} 聚合出 washing_ratio_{llm}{_sfx}) ; pipeline/panel/export.py (变量标签/聚合装配)"
upstream:
- deepseekv4_score_full
- deepseekv4_score_ctx
- deepseekv4_score_ss
- innovation_substantiveness_full
citations:
- doi: "10.1111/eufm.12509"
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: "31"
  issue: "1"
  pages_or_artno: 427-462
- doi: "10.1016/j.pacfin.2024.102600"
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: Ownership concentration and corporate greenwashing in China's capital markets- Based on a multi-actors perspective
  venue: Pacific-Basin Finance Journal
  vol: "89"
  pages_or_artno: Article 102600
- doi: "10.1111/jofi.13412"
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: Sustainability or greenwashing- Evidence from the asset market for industrial pollution
  venue: The Journal of Finance
  vol: "80"
  issue: "2"
  pages_or_artno: 699-754
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_deepseekv4 一族测度的是"媒体报道中银行金融科技创新话语的象征性占比", 借用企业环境社会治理研究中"漂绿"(greenwashing)构念的方法学骨架, 迁移到金融科技话语场景, 可称为"洗稿" (washing) 测度: 一家银行在某一年被媒体正面刻画的报道里, 有多大比例仅停留在"象征性"表态(口号式、宣示性、无具体项目/产品/合作落地信息), 而非"实质性"披露(有具体技术、产品、投入、合作方等可验证内容)。该构念呼应 Duchin, Gao & Xu (2025, Journal of Finance) 关于"可持续性抑或漂绿"的资产市场证据, 以及 Fan, Tang, Huang & Yang (2025, Pacific-Basin Finance Journal) 对中国资本市场股权集中度与企业漂绿关系的检验: 两文的共同逻辑是"正面话语"本身不能等价于"实质行动", 必须用一个可分解的指标把话语的"表态成分"与"落地成分"分开计量, 否则会把纯粹的公关宣示误读为战略投入。washing_ratio_deepseekv4 把这一逻辑应用到银行-金融科技新闻语料: 分子锁定"被判定为正面 且 被判定为象征性"的报道篇数, 分母锁定"被判定为正面 且 实质性/象征性二分类本身已被成功测出"的报道篇数, 比值越高说明该银行当年的正面曝光越"虚", 越依赖口号式宣传而非可验证的技术/合作细节。方法学上直接对应 Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法从企业社会责任报告中识别漂绿信号的做法: 二者都不满足于情感极性本身, 而是在情感极性之上再叠加一层"内容是否具体/可验证"的判据, 用两层判据的组合比率而非单层情感均值来刻画传播质量。

【方法学与计算】
washing_ratio_deepseekv4 的分子构造分两步: 第一步取情感判定, 第二步取实质性判定, 二者做逻辑与(AND)后计数。与家族 canonical `washing_ratio`(方法 A, LLM 三家多数投票)不同, `_deepseekv4` 后缀对应 producer 代码里明确实现的"方法 A2: 单个 LLM"变体 —— 即不取三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票后的正面判定, 而是只取 deepseekv4 单模型自身的逐篇连续情感打分 `deepseekv4_score{track}`, 经 `fillna(0)` 后以 `>0` 二值化为正面标记(`_llm_pos{track}`); 该二值化判据是 producer 就地计算的中间量, 不落盘为独立列, 与家族三家共识版所用的门控式 `llm_verified_full`/多数票是两条不同但同构的正面判定路径。情感打分来源是浮点型逐篇量表分, `fillna(0)` 语义下 NaN/测量失败/未评分一律折算为 0 分, 因不满足 `>0` 而不计入正面, 不会被误判为反面或正面。实质性判定 `innovation_substantiveness_full` 取值"实质性"/"象征性"两类字符串标签, 该判定固定用 full 轨(不随本家族三轨切换, 判据主体是整篇文章的创新话语归类, 与 washing_ratio 三轨各自独立的"正面情感"判据是两个不同的维度)。分母口径是本家族的一处关键校正: 早期实现曾把分母设为"全部正面文章数", 但若 LLM 对实质性/象征性的分类本身存在测量失败(NaN), 这些失败篇目永远进不了分子(因为分子要求象征性=True 且失败篇目 astype(str) 后变成字符串 'nan', 不等于'象征性'也不等于'实质性'), 却仍会被计入旧分母, 导致"分类失败越多, 洗稿率被系统性稀释得越低"这一测量假象。当前实现改用"同域分母"(`_svd_{llm}_pos{track}`, subst-valid denominator): producer 就地构造 `washing_cols[f"_svd_deepseekv4_pos{track}"] = (_llm_pos{track} & _subst_measured)`, 分母只统计"正面 且 实质性/象征性分类已成功测出"的文章, 与分子处在同一个可测量子空间内, 避免分类失败率的波动机械地压低比率; 面板层最终由 `deepseekv4_pos_count{track}`(分母, 该子域内文章篇数加总)与 `deepseekv4_pos_symb_count{track}`(分子, 该子域内象征性文章篇数加总)聚合到银行-年层级, 相除得到本列。

【文献定位】
washing_ratio_deepseekv4 与三家 LLM 多数投票版本 `washing_ratio` 之间的关系, 完全遵循本项目 CLAUDE.md 载明的口径铁律: 三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 各自的 per-model 子测度是"co-equal 跨厂商稳健性轨", 互为稳健性、不分主次, 与多数投票共识测度并排存在, 目的是验证洗稿率不是被某一家 LLM 的判定偏差单独驱动的产物, 而是三家厂商独立判定下都能复现的稳定信号 —— 这与 Gorovaia & Makrominas (2024) 强调 NLP 方法应做跨模型/跨方法稳健性检验的建议一致。真实的跨模型一致性 FWER 校正落在根级模板 `27_tableA12_cross_model_fwer`(Panel C 情感族), 而非本家族自身承担多重检验校正职责。同时须遵守铁律: `washing_ratio_deepseekv4`、`washing_ratio`(共识)、以及另外两家单模型变体(`washing_ratio_gpt54nano`/`washing_ratio_gemini31`, 若存在于其他家族)各自 just-identified 并排使用, 禁止将它们混入同一个 over-identified 的 Hansen J 过度识别检验, 因为它们本质上是同一构念的多个替代测量, 而非相互独立的额外识别信息源。

## VAR: washing_ratio_deepseekv4

【变体差分】
本列是家族 canonical 三轨中的 full 轨(无 `_ctx`/`_ss` 后缀), 即"标题+正文全文"轨道: 情感判据取自 deepseekv4 单模型对整篇文章全文(标题拼正文)所做的连续打分 `deepseekv4_score_full`, `fillna(0)` 后 `>0` 二值化为正面标记, 实质性判据同样用 `innovation_substantiveness_full`。该轨的行宇宙遵循 2026-06-29 起生效的"留篇门控 = full-only"铁律: 一篇报道是否算作"一篇银行-金科报道"只看 `llm_verified_full == True`, 因此 full 轨天然是三轨里样本量最完整、无需从其他轨借用留篇判定的基准轨, ctx/ss 轨是在 full 轨留篇集合的子集上分别计算的条件测度/稳健性轨。该列作为 deepseekv4 单模型下的主口径, 与三家共识版 `washing_ratio` 全轨互为稳健性并排, 二者一致上升或一致下降是"洗稿率信号非模型伪影"的证据; 若二者出现系统性背离(如仅 deepseekv4 单模型显著高于共识), 应结合 `27_tableA12` 的跨模型一致性检验(Krippendorff's alpha / Cohen's kappa)审慎解读, 而不能默认取信任一单模型口径。分母的同域校正逻辑(仅计入实质性分类成功测出的正面文章)在本列同样适用, 且实质性判据固定引用 full 轨字段, 不随情感轨道切换。使用者在解读本列时应留意: deepseekv4 与 gpt54nano/gemini31 分属不同厂商与不同训练/推理路径, 三家单模型口径对同一批文章的情感判定不可能逐篇完全一致, 差异本身不代表哪一家更"正确", 而是提供了一个跨厂商的测量误差分布信息; 当研究结论仅在某一家单模型口径下成立、在另外两家或共识版下不显著时, 应将其明确标注为对该模型的敏感性发现, 而非整体结论。本列在面板层面按银行-年聚合, 分子分母的加总域完全一致(均限定在 deepseekv4 判定为正面的文章子集内), 因此比率本身不会因为某一年该银行报道总量骤增/骤减而产生机械性偏移, 但样本量过小的银行-年格(正面文章数很低)仍应结合 `n_articles`/留篇率一并解读, 避免把个位数样本上的比率波动当作稳定信号。

## VAR: washing_ratio_deepseekv4_ctx

【变体差分】
本列是三轨中的 ctx 轨: 情感判据取 `deepseekv4_score_ctx`(`fillna(0)` 后 `>0` 二值化), 该字段是 deepseekv4 对"标题+目标银行实体窗口文本"(而非全文)所做的连续打分, 目的是把注意力集中在银行主体附近的语境, 剔除文章中与该银行无关段落对情感极性的干扰。ctx 轨内容由 stage 14 `ctx_materializer` 物化生成的 `content_ctx` 列供 stage 21 LLM 情感消费, 若某篇文章缺乏可界定的实体窗口(即无法定位到目标银行的有效上下文), 则该篇的 `ctx_is_fallback` 标记为 True, 此时 `content_ctx` 退化为等同全文, 情感/实质性判定不因此中断但样本失去了"聚焦银行语境"这一层额外信息含量。行宇宙上, ctx 轨是 full 轨留篇集合的条件子集(仅统计 `llm_verified_full == True` 的文章, 但情感判据换用 ctx 版), 而非独立的留篇门控; 分母仍是本轨内部的同域校正分母(deepseekv4 正面 ctx 且实质性成功测出), 不与 full 轨分母混用。本列与家族 canonical full 轨、以及与之并排的三家共识版 ctx 轨互为稳健性, 依 CLAUDE.md 铁律各自 just-identified, 不得混入同一 over-identified Hansen J 设定。与 full 轨相比, ctx 轨的价值在于排除掉一篇长报道中与目标银行完全无关的段落(例如同一篇稿件同时报道多家银行或多个不相干话题)对情感/象征性判定的稀释或污染, 从而更精确地捕捉"媒体在描述这家银行时"的话语姿态, 而不是整篇稿件的笼统语气。这一设计尤其适用于金融科技相关报道常见的"综述式"写法: 一篇文章罗列多家银行的金融科技动态, 若不做实体窗口截取, 全文轨的情感判定可能被其他银行的正负面消息带偏; ctx 轨通过聚焦目标银行的实体窗口, 使 washing_ratio_deepseekv4_ctx 相对于 full 轨版本对这类"多主体稀释"更为稳健。但 ctx 轨并非全面优于 full 轨: 当实体窗口过窄时也可能丢失必要的上下文信息(例如某项技术合作的具体细节出现在窗口外), 这正是本项目坚持三轨并排、互为稳健性而非以 ctx 单独取代 full 的方法论理由。

## VAR: washing_ratio_deepseekv4_ss

【变体差分】
本列是三轨中的 ss 轨(sentence-level co-occurrence): 情感判据取 `deepseekv4_score_ss`(`fillna(0)` 后 `>0` 二值化), 该字段基于"标题+目标银行∧金融科技词同句(或按 `context_window.ss_sentence_radius` 配置的窗口半径, 默认±1句)共现"截取出的文本 `content_ss` 计算, 是三轨中语境最窄、聚焦度最高的版本, 直接刻画银行与金融科技话题在同一句/邻近句中被共同提及时的情感倾向, 而非泛泛的银行相关段落情感。ss 轨的回退语义严格镜像 ctx 轨: 若一篇文章不存在银行∧金融科技的同句(或窗口内)共现, 则该篇 `content_ss` 退化为全文 body, `ss_is_fallback` 标记为 True, 与 ctx 轨共享同一个"退化时按全文计, 分母不因此单独失真"的处理原则; 若上游金融科技词库 `FINTECH_AC` 为 None(未加载), 则所有文章的 `*_is_fallback` 全部为 True, 情感判定优雅降级为等同全文轨而非报错中断。本列的行宇宙同样是 full 轨留篇集合的条件子集, 分母采用本轨内部同域校正(deepseekv4 正面 ss 且实质性已测出), 与 full、ctx 两轨分母各自独立核算互不借用。三轨(full/ctx/ss)在本家族及其余全部 `washing_ratio*` 变体族中永远各自 just-identified 并排比较, 互为稳健性、不分主次, 严禁混入同一个 over-identified Hansen J 设定, 也不得与三家 LLM 共识版/其他单模型版本的跨轨列直接叠加进同一识别方程。

<!-- rendered-citations:begin -->
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets- Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing- Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
<!-- rendered-citations:end -->
