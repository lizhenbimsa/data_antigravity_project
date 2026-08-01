---
family_id: F530
columns:
- sum_wd_hw_llm_ctx
- sum_wd_hw_llm_full
- sum_wd_hw_llm_ss
unit: 无量纲权重和 (跟风衰减权重之逐篇加总, 银行-年层面)
formula: 'sum_wd_hw_llm{track} = Σ_i herd_weight{track}_i · 1[llm_vote_score{track}_i 非缺失], 其中 i 遍历该银行-年内全部留篇文章 (full-only 留篇门控); herd_weight 由 stage 24 跟风衰减处理器按篇龄/衰减半衰期算出'
producer: pipeline\panel\encode.py::aggregate_panel (第1197-1203行, wtag/grp 通用循环块, fix(encode-01, metric-audit 2026-06-10) 注释头; 物理位置在 F5b 阈值敏感性块之后、MW 汇总块之前, 未挂 F- 字母段标签; 三轨 sum 循环) ; pipeline\panel\runner.py::_build_llm_valid_masked_weights (valid-mask 分母构造)
upstream:
- 24_herd_decay_processor
- 21_tone_llms
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
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L.; Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E.; Parsons, C. A.
  year: 2011
  title: The Causal Impact of Media in Financial Markets
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 67-97
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F.; Alizadeh, M.; Kubli, M.
  year: 2023
  title: ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J.; Mullainathan, S.; Rambachan, A.
  year: 2025
  title: 'Large Language Models: An Applied Econometric Framework'
  venue: NBER Working Paper No. 33344
new_dois: []
---

## CORE

【构念与来源】
本家族三列 `sum_wd_hw_llm_ctx` / `sum_wd_hw_llm_full` / `sum_wd_hw_llm_ss` 是"跟风衰减加权 (herd-weighted) LLM 投票语调"这一族测度在银行-年层面的权重分母, 而非语调本身。其构念依据 Tetlock (2007, *Journal of Finance*) 开创、Tetlock (2011) 延伸的媒体语调聚合传统: 单篇报道对银行-年整体语调的贡献不应等权计入, 而应按其"跟风程度"降权 — 一篇报道若在短时间窗内被大量同题材、同论调的其它报道跟随/复述 (herd 现象), 其边际信息含量被稀释, stage 24 (`herd_decay_processor`) 据此为每篇文章算出一个 ∈(0,1] 的衰减权重 `herd_weight{track}`, 报道越接近"抄稿/跟风潮"的高峰、权重越低。三列的字面语义是: 对每个银行-年、每条文本轨道 (full/ctx/ss), 把"该篇 LLM 投票语调 `llm_vote_score{track}` 非缺失"的全部文章的 `herd_weight{track}` 累加求和, 得到一个纯权重量 (无正负号、无情感极性), 单位是"篇数当量" — 若全部报道权重恒为 1 (无跟风衰减), 该列数值上等于当期 LLM 有效留篇篇数; 一旦存在跟风衰减, 该列会小于篇数, 差额即被"折价"的重复报道贡献。
本列本身不是任何回归中直接使用的语调自变量, 而是分母角色: 面板层面真正的跟风衰减加权语调均值 `avg_hw_llm_tone{track}` (或类似列) = `llm_vote_score_hw_sum{track} / sum_wd_hw_llm{track}`, 是分子 (逐篇语调 × 权重之和) 除以本列分母 (逐篇权重之和, 仅对语调非缺失的文章计权) 后得到的加权平均。之所以要单独物化分母列而不是让下游直接除以简单篇数, 是因为分子求和时隐含"仅对 `llm_vote_score` 非缺失的文章计入权重" (valid-mask, 见 `runner.py::_build_llm_valid_masked_weights`) — 若某篇报道被三家 LLM 均判定 `llm_verified{track}` 为假 (未通过留篇门控) 或情感字段本身缺失, 它既不进分子也不进本列分母, 保证分子分母同域, 避免"用全篇篇数当分母、却只对部分篇数求和当分子"造成的系统性向下偏误。

【方法学与计算】
构造分两步、分居两个源文件, 但共享同一权重来源与同一有效性判据。第一步在 `pipeline/panel/runner.py` 的 3d 步骤: 对每条轨道 `track ∈ {_full, _ctx, _ss}`, 取该轨道的跟风衰减权重列 `herd_weight{track}` (若面板是历史遗留的单轨 legacy 权重场景则退化处理, 但生产口径三轨独立), 与该轨道的 `llm_vote_score{track}` 逐行相乘得到加权分子候选列, 同时用 `.where(df[f'llm_vote_score{track}'].notna())` 对权重本身做掩码, 得到 `_wd_hw_llm{track}` (或按敏感性 tag 命名的 `_wd_hw_{tag}_llm{track}`) 这一篇章级中间列 — 凡该篇 LLM 投票语调缺失 (通常源于该篇未通过留篇门控 `llm_verified_full`, 或三家 LLM 情感解析失败), 对应行的掩码权重记为缺失, 不参与后续求和。第二步在 `pipeline/panel/encode.py` 第1197-1203行一个独立的通用循环块 (注释头 `fix(encode-01, metric-audit 2026-06-10)`, 遍历 `wtag ∈ {vw, mw, hw}` 与 `grp ∈ {llm, *LLM_MODELS, prob}`), 用 pandas groupby-agg 语法 `agg[f'sum_wd_hw_llm{track}'] = (f'_wd_hw_llm{track}', 'sum')` 把上一步的篇章级掩码权重列, 按银行-年分组求和, sum 聚合默认跳过 NaN, 于是天然实现"仅对语调非缺失文章计权求和"的语义。该块物理位置紧接在 F5b (阈值敏感性变体, 第1073-1086行) 之后、MW 汇总块之前, 但并未被赋予独立的 F- 字母段标签, 与其上方真正的"F5. 跟风衰减加权聚合"段落 (第1056-1072行, 覆盖 `sum_herd_weight_*` 与 hw_sum 分子) 是两个不同的代码块, 不应混同归属。该分母与同一循环块内的 `llm_vote_score_hw_sum{track}` (加权分子) 共享同一批被保留的行、同一批 `herd_weight{track}` 取值, 二者相除即为跟风衰减加权 LLM 语调均值, 这是"分子分母同域"设计的直接体现, 避免了简单地拿全篇篇数 `n_articles{track}` 当分母时可能引入的、由留篇/缺失导致的偏误。
留篇门控口径须与全仓铁律一致: 2026-06-29 之后, 一篇报道是否被判定为"一篇有效银行-金科报道"只看 `llm_verified_full`, 即行宇宙的门槛判定是 full-only 的; `_ctx`/`_ss` 两条轨道退化为"以 full 留篇集为行宇宙的 conditional-on-full 测度/稳健性轨", 逐轨照算 herd_weight 与 valid-mask, 但不独立决定该篇文章是否进入留篇集合。三轨 (full/ctx/ss) 的权重分母因此各自独立计算、各自 just-identified 并排, 互为稳健性、不分主次, 三条轨道禁止混进同一 over-identified Hansen J 检验。`_ss` 轨的回退语义镜像 `_ctx`: 当一篇报道内不存在"银行实体与金科词同句共现"时, `content_ss` 回退取全文 body (与 `content_ctx` 共享 `n_articles` 分母口径), `ss_is_fallback` 标记为真; 若 `FINTECH_AC` 词表未加载, 三轨的 `*_is_fallback` 会全部退化为真, 此时权重构造仍按既定公式跑, 只是分子分母的实际取值会趋同于"无金科过滤"的粗口径, 属优雅降级而非报错。
本家族与阈值敏感性梯子 (`herd_detection.sensitivity_thresholds`, 2026-06-13 引入) 共享同一构造骨架, 但本家族三列取的是默认门槛下的权重分母 (无 `_thrNN` 后缀), 敏感性网格下逐 τ 版本的分母列命名为 `sum_wd_hw_{tag}_llm{track}`, 与本三列同构但属于不同家族, 二者不应混淆——本家族是敏感性网格里 τ=0.35 (生产默认阈值) 这一格的具名产物。

【文献定位】
按篇龄/传播速度对文本信号做衰减加权、以抑制"跟风报道"对聚合语调的稀释效应, 其方法学根源可追溯到 Tetlock (2007, *Journal of Finance*) 关于媒体语调聚合与股票收益可预测性的开创性设计, 后续研究进一步确认媒体语调测度需要处理报道间的相关性/重复性问题而非简单等权平均 (Fang & Peress, 2009, *The Journal of Finance*; Engelberg & Parsons, 2011, *The Journal of Finance*)。本家族的分子 (LLM 投票语调) 本身来自三家大语言模型多数投票的情感判读, 其可靠性依据近年 LLM 文本标注方法学文献: Gilardi, Alizadeh & Kubli (2023, *Proceedings of the National Academy of Sciences*) 证明经过良好提示词设计的 LLM 在文本标注任务上可媲美甚至超越众包人工标注质量, 是本项目采用三家 LLM 投票而非单一人工标注作为情感判读来源的方法学支撑; de Kok (2025, *Management Science*) 进一步为会计与金融文本分析场景下生成式 LLM 的规范使用 (温度参数固定为 0、提示词版本冻结、结果可缓存复现) 提供了实践指引, 与本项目 `NEWS_PROCESS_LLM_OFFLINE` 离线缓存复现锚点、`prompt_version` 字节级冻结的做法一致。权重分母本身不是新颖构念, 而是"跟风衰减加权平均"这一聚合方式在实现上必须显式物化的会计恒等式配件: 唯有分子分母同时按 valid-mask 掩码求和, 才能保证跟风加权均值在文章缺失情感判读的边界情形下不产生系统性偏误, 这一实现纪律呼应 Ludwig, Mullainathan & Rambachan (2025, NBER Working Paper) 关于将 LLM 输出纳入计量经济学框架时须谨慎处理测量误差与缺失机制的应用计量学讨论。

## VAR: sum_wd_hw_llm_ctx

【变体差分】
本列是家族公式在 `_ctx` 轨道 (标题 + 银行/金科实体窗口文本) 上的实现, 求和对象是 `herd_weight_ctx` 这一由 stage 24 跟风衰减处理器基于 `_ctx` 轨道文本相似度/时间衰减算出的篇章级权重, 掩码判据是该篇 `_ctx` 轨道的 `llm_vote_score_ctx` 是否非缺失。`_ctx` 轨道的行宇宙已切换为 conditional-on-full: 一篇报道能否进入 `_ctx` 轨道的求和范围, 首先取决于其是否通过 full-only 的留篇门控 (`llm_verified_full`), `_ctx` 轨道自身不再独立决定留篇与否, 仅在 full 留篇集合内部逐轨复算权重与掩码。该列与 `sum_wd_hw_llm_full`、`sum_wd_hw_llm_ss` 三者互为稳健性并排, 不构成同一构念的三重验证叠加使用, 严禁在同一 over-identified 检验 (如 Hansen J 过度识别检验) 中同时纳入三轨对应的加权均值分子分母组合。若某篇报道不存在银行实体窗口 (即 `_ctx` 抽取失败或该篇没有可界定的实体上下文窗口), 其 `content_ctx` 与相应的 `herd_weight_ctx`/`llm_vote_score_ctx` 按 stage 14 物化时既定的兜底规则处理, 本列的求和逻辑对这类边界情形与主口径一致地跳过缺失行, 不做特殊插补。与家族 canonical (若以 `_full` 为默认参照) 相比, `_ctx` 版本的语义差异纯粹来自输入文本窗口范围的收窄 (标题+实体邻近文本 vs. 标题+全文), 这会改变 stage 24 衰减权重的具体取值 (实体窗口更短, 篇章间的文本相似度判定可能与全文计算结果不同), 因而 `sum_wd_hw_llm_ctx` 的数值一般不等于 `sum_wd_hw_llm_full`, 即便二者对应的银行-年、留篇集合行数相同, 加权求和的结果也会因权重来源不同而分化, 这正是"互为稳健性"设计的意图所在——用不同文本窗口下独立算出的跟风衰减权重, 检验主结论是否对文本窗口选择敏感。

## VAR: sum_wd_hw_llm_full

【变体差分】
本列是家族公式在 `_full` 轨道 (标题 + 全文正文, prepend_title 拼接) 上的实现, 也是当前项目情感与语调族的 P1 主轨/canonical 参照口径 (`llm_vote_tone_full` 为 treatment.primary)。求和对象是 `herd_weight_full`, 掩码判据是该篇 `llm_vote_score_full` 是否非缺失; 由于留篇门控本身即以 `llm_verified_full` 为唯一判据 (full-only gate, 2026-06-29 生效), `_full` 轨道天然覆盖该银行-年的全部留篇文章, 是三轨中行宇宙最完整、无需再受 conditional-on-full 约束的一支 (`_ctx`/`_ss` 的行宇宙均是 `_full` 留篇集合的子集)。因此 `sum_wd_hw_llm_full` 通常是三列中数值上限最高的一列 (在权重恒为 1 的极端情形下, 它等于该银行-年 `_full` 轨道 LLM 有效留篇篇数); 但由于跟风衰减权重逐篇 ∈(0,1], 实际数值总是小于等于篇数。该列与 `_ctx`/`_ss` 两列的关系是并排的方法学稳健性轨而非层级主从关系——虽然它是各 paper 主线回归 treatment 变量所依赖的分母, 但在稳健性检验语境下三者地位对等, 不应把 `_ctx`/`_ss` 简单理解为对 `_full` 的"辅助修正"。使用该列时须留意: 它是跟风衰减加权语调均值的分母, 而非语调本身, 直接把该列当作解释变量或控制变量放入回归没有经济学意义, 正确用法是与同轨的 `llm_vote_score_hw_sum_full`(等其它 hw 加权分子族) 配对相除, 或作为诊断量观察某银行-年被跟风折价的严重程度 (与简单篇数 `n_articles_llm_valid_full` 对比即可看出折价幅度)。

## VAR: sum_wd_hw_llm_ss

【变体差分】
本列是家族公式在 `_ss` 轨道 (标题 + 银行与金科词严格同句共现窗口, `context_window.ss_sentence_radius` 默认半径 1) 上的实现, 求和对象是 `herd_weight_ss`, 掩码判据是该篇 `llm_vote_score_ss` 是否非缺失。`_ss` 轨道的行宇宙同样是 conditional-on-full (以 `_full` 留篇集合为上界), 且其回退语义严格镜像 `_ctx`: 当某篇报道不存在银行实体与金科词的同句共现时, 该篇的 `content_ss` 回退取全文 body、`ss_is_fallback` 记为真, 此时其 `herd_weight_ss`/`llm_vote_score_ss` 按回退后的文本重新走 stage 21/24 流程算出, 而非被直接剔出求和范围——回退不等于缺失, 只要该篇 `llm_vote_score_ss` 本身非缺失, 权重仍计入本列。`_ss` 是三轨中文本窗口最窄、构造判据最严格的一支 (裸 AC 自动机匹配金科词、同句共现, 无否定/短名过滤——判定不对称口径在银行侧含否定与短名过滤、金科侧不含), 因此在同句共现比例较低的银行-年 (尤其 dev 环境早期试跑 T=2 小样本下), `_ss` 轨大量报道会触发回退, 导致该列在回退占比高的银行-年数值上趋近于 `_full` 版本、而在回退占比低 (同句共现丰富) 的银行-年则体现出与 `_full`/`_ctx` 更明显的分化。与前两列同理, `sum_wd_hw_llm_ss` 与 `sum_wd_hw_llm_ctx`、`sum_wd_hw_llm_full` 三者各自 just-identified 并排, 互为稳健性、不分主次, 不得混入同一 over-identified Hansen J 检验; 若 `FINTECH_AC` 词表整体未加载 (生产环境异常场景), 三轨 `*_is_fallback` 会全部退化为真, 此时 `sum_wd_hw_llm_ss` 与 `sum_wd_hw_llm_ctx`、`sum_wd_hw_llm_full` 三者会趋于数值接近但不保证严格相等 (因权重仍由各自轨道独立算出), 这是优雅降级的预期表现而非缺陷。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, L.; Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Engelberg, J. E.; Parsons, C. A. (2011). The Causal Impact of Media in Financial Markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Gilardi, F.; Alizadeh, M.; Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J.; Mullainathan, S.; Rambachan, A. (2025). Large Language Models: An Applied Econometric Framework. NBER Working Paper No. 33344 [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
<!-- rendered-citations:end -->
