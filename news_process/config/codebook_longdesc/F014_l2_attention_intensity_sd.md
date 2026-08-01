---
family_id: F014
columns:
- attention_intensity_sd_ctx
- attention_intensity_sd_full
- attention_intensity_sd_ss
unit: 金融科技技术强度得分的银行-年篇间样本标准差 (无量纲, 二阶矩, ddof=1)
formula: "attention_intensity_sd_track = std_d(fintech_intensity_score_track), ddof=1 (银行-年内按篇聚合; N<2 → NaN); track ∈ {full, ctx, ss}"
producer: news_process/pipeline/panel/attention_media.py::compute_attention_treatments ; news_process/pipeline/panel/codebook.py
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_ctx / content_ss)
- 40_panel_yearly.parquet
citations:
- doi: 10.1016/j.jfineco.2024.103870
  type: journal
  authors: Cookson, J. A., Lu, R., Mullins, W., & Niessner, M.
  year: 2024
  title: "The social signal"
  venue: Journal of Financial Economics
  vol: 158
  pages_or_artno: 103870
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3105-3147
- doi: 10.1111/jofi.13219
  type: journal
  authors: Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R.
  year: 2023
  title: "Firm-level climate change exposure"
  venue: The Journal of Finance
  vol: 78
  issue: 3
  pages_or_artno: 1449-1498
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: "In search of attention"
  venue: The Journal of Finance
  vol: 66
  issue: 5
  pages_or_artno: 1461-1499
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: "10.1111/fire.70002"
  title: "Tone Distance: Managerial Tone Divergence and Market Reaction to Earnings Announcements"
  authors: "Angelo, B., Johnston, M., Singh, A., & Wan, Y. Q."
  year: 2025
  venue: "Financial Review"
  type: "journal"
- title: "The Impact of News Media Coverage on Voluntary Disclosure"
  authors: "Lock, B."
  year: 2024
  venue: "Contemporary Accounting Research"
  doi: "10.1111/1911-3846.12982"
  type: "journal"
  one_sentence_zh: "媒体报道强度上升会促使管理层更多披露自愿性信息, 印证媒体覆盖强度承载独立经济信息的构念基础。"
- title: "How Media Coverage Elicits Strategic Change: The Moderating Role of the Business Model Design"
  authors: "Klein, S. P., Spieth, P., Ricart, J. E., & Noble, C. H."
  year: 2024
  venue: "Strategic Management Journal"
  doi: "10.1002/smj.3688"
  type: "journal"
  one_sentence_zh: "媒体报道的内容与强度异质性驱动企业战略变革, 支持报道内容层面 (而非仅数量) 的分散度承载独立信息的观点。"
new_dois:
  - "10.1111/fire.70002"
  - "10.1111/1911-3846.12982"
  - "10.1002/smj.3688"
---

## CORE

【构念与来源】
本家族刻画的是一个银行在一个年度内, 其金融科技新闻报道所承载的技术强度的篇间离散程度, 即 attention_intensity_sd (注意力强度标准差)。它属于 P2 论文 bank_fintech_attention 的关注度处理变量族, 与该族的一阶矩测度 (累积曝光 attention_index、曝光密度 attention_intensity_density) 互补: 前两者刻画注意力的量与均值, 本测度刻画注意力所覆盖内容在技术强度维度上的散布。构念上的直觉是, 两家银行即便在同一年获得等量的金融科技报道 (相同曝光总量与相同平均强度), 其报道内容仍可能在技术含量上截然不同: 一家可能被密集报道于同一类深度技术话题 (篇间强度趋同, 标准差小), 另一家则被跨越支付、风控、区块链、监管科技等异质话题分散报道 (篇间强度分化, 标准差大)。该二阶矩因此承载了单纯计数与均值无法识别的信息, 是关注度构念的离散度侧面。数据来源为上游 stage 15 fintech_intensity 阶段逐篇物化的金融科技技术强度得分 fintech_intensity_score, 该得分由金科词命中在文章文本上的强度归一化产生; 文本轨道由 stage 14 ctx_materializer 物化的三轨内容 (content_full / content_ctx / content_ss) 分别驱动, 因而本测度天然三轨化。

【方法学与计算】
计算在 attention_media.py 的 compute_attention_treatments 中完成: 将逐篇 fintech_intensity_score 按银行-年分组, 对组内各篇取样本标准差 (pandas std, ddof=1), 落为 sd_full / sd_ctx / sd_ss 三列。样本标准差采用无偏 (ddof=1) 口径, 直接后果是单篇银行-年 (N=1) 因自由度为零而返回 NaN, 而非返回 0; 这是刻意的, 因为单篇报道不存在篇间离散这一构念, 以 NaN 表达"不可算"优于以 0 冒充"离散为零"。取值域为非负半轴, 值域校验函数 _validate_attention_treatments 对 attention_intensity_sd_{full,ctx,ss} 施加 (0.0, None) 下界断言。零-fintech 银行-年 (无任何金融科技报道) 与单篇银行-年一样落 NaN (disp/sd/gap/share 类离散测度对零覆盖统一置 NaN, 区别于 index/density 类对真零曝光置 0)。三轨在方法学上互为稳健性、不分主次: full 轨为 canonical 主轨 (标题 prepend + 全文正文), ctx/ss 为分离复跑的稳健性载体, 三者各自 just-identified 并排进入各自回归, 严禁把三轨列混进同一个 over-identified 的 Hansen J 过度识别检验 (CLAUDE.md 三轨铁律)。留篇门控依 full-only 口径 (2026-06-29): 一篇报道是否算作银行金融科技报道只看 full 轨的 llm_verified_full, ctx/ss 是 conditional-on-full 的子集轨, ss 回退语义镜像 ctx (无银行∧金科同句共现时 content_ss 退回全文 body)。

【文献定位】
本测度的方法学谱系源自媒体关注度与文本暴露度量的实证传统。Fang 与 Peress (2009) 确立了媒体覆盖量作为横截面定价因子的基础范式, Da、Engelberg 与 Gao (2011) 进一步把"注意力"操作化为可测的关注代理; 本族的一阶矩 attention_index 即锚定于此二者的覆盖量口径。相对而言, 本二阶矩测度更贴近 Hassan、Hollander、van Lent 与 Tahoun (2019) 所倡的 firm-level 文本暴露强度传统, 以及 Sautner、van Lent、Vilkov 与 Zhang (2023) 把主题暴露从计数推进到强度与分布的思路 — 关注度不只是"是否被提及", 而是"以何等技术强度、在多大内容散布下被提及"。Cookson、Lu、Mullins 与 Niessner (2024) 对信息信号跨来源异质性的刻画, 与本测度捕捉篇间强度分化的动机同源。Bybee、Kelly、Manela 与 Xiu (2024) 从商业新闻文本中提取宏观状态的工作, 印证了新闻文本二阶结构 (而非仅计数) 承载独立经济信息的判断。方法论层面, Gentzkow、Kelly 与 Taddy (2019) 的 text-as-data 综述为把非结构化文本聚合为银行-年面板矩提供了统一的计量框架。需强调本测度是内容强度的离散, 与本族另一离散测度 attention_disp (跨媒体来源的 outlet-HHI 集中度) 构念正交: 前者问"报道内容有多异质", 后者问"报道来源有多集中"。Angelo、Johnston、Singh 与 Wan (2025, Financial Review) 构造管理层语调跨来源的离散度量并检验其市场反应, 与本家族用样本标准差捕捉同一银行-年内金科报道技术强度篇间分化的二阶矩思路直接呼应, 均主张离散度而非均值承载独立信息。Lock (2024, Contemporary Accounting Research) 发现媒体报道强度上升会促使管理层更多披露自愿性信息, 印证媒体覆盖强度承载独立经济信息的构念基础; Klein, Spieth, Ricart 与 Noble (2024, Strategic Management Journal) 则发现媒体报道的内容与强度异质性驱动企业战略变革, 支持报道内容层面 (而非仅数量) 的分散度承载独立信息的观点, 二者共同为本测度以篇间强度标准差捕捉内容异质性的构念提供了外部支撑。

## VAR: attention_intensity_sd_full

【变体差分】
本列是本家族的 canonical 主轨, 文本口径为 full 轨: 标题 prepend 到全文正文后的完整文章文本。其逐篇强度输入为 fintech_intensity_score_full, 即金科词命中判据施加在标题加正文的全文本上产生的技术强度得分; 银行-年内按篇取样本标准差 (ddof=1) 即得本列, N<2 或零-fintech 银行-年落 NaN。作为 P2 attention 处理变量的主轨, 留篇门控完全由 full-only 口径界定 (2026-06-29): 是否计入某银行某年的金融科技报道集合仅取决于 full 轨的 llm_verified_full 判定, 因而本列的分母 (参与聚合的篇集) 是留篇门控的规范集合, ctx/ss 两轨的行宇宙均为其子集。相对 ctx/ss 两条稳健性轨, full 轨的文本覆盖面最广 (不受实体窗口或同句共现裁剪), 因而其篇间强度散布刻画的是最宽内容口径下的技术异质性。本列与 sd_ctx、sd_ss 互为稳健性、不分主次, 三轨各自 just-identified 并排进入各自回归, 严禁混入同一 over-identified 的 Hansen J 过度识别检验。回归中若以本列为主处理, ctx/ss 应作分离复跑的稳健性对照, 而非与本列共同塞入同一超识别工具集。构念上还须与本族一阶矩测度区分: attention_index 与 attention_intensity_density 刻画曝光的总量与均值, 本列刻画的是同一批报道在技术强度上的散布 (二阶矩), 二者在同一银行-年可高可低相互独立 — 均值高不必然离散大, 因此本列携带的是均值口径无法识别的内容异质性信息。作为主轨, 本列亦是本族三轨中文本覆盖最完整、缺失最少的一轨: 只要留篇门控判定该行该年至少有两篇金融科技报道, 本列即可算出, 因而在样本可算性上优于受更严判据裁剪的 ctx/ss 两轨。

## VAR: attention_intensity_sd_ctx

【变体差分】
本列是 ctx (实体上下文窗口) 轨的稳健性载体。其文本口径不取全文, 而取 stage 14 ctx_materializer 物化的 content_ctx: 标题 prepend 到实体窗口文本 (围绕目标银行实体命中位置的上下文窗口) 之后。据此计算逐篇 fintech_intensity_score_ctx, 再于银行-年内取样本标准差 (ddof=1) 得本列, N<2 或零-fintech 落 NaN。与 full 轨相比, ctx 轨把强度评估限定在与目标银行实体邻近的文本片段, 意在过滤掉全文中与本行无关的金融科技泛论所带来的强度噪声, 因而更贴近"针对本行的"技术强度散布。源码注记指出, 在本机三轨实测中 ctx 轨的篇间强度标准差与 full 轨相关最低 (实跑约 0.656), 是本家族三轨里与主轨相关性最弱、因而提供最强增量稳健性的一轨 — 这正是把它作为独立稳健性对照而非冗余副本的价值所在。本列为 conditional-on-full 的子集轨: 行宇宙是 full-only 留篇门控集合的子集, per-track 列在该子集上照常计算。本列与 sd_full、sd_ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。判据口径上须提醒: ctx 轨的实体窗口界定 (围绕银行实体命中位置的上下文窗口) 与 stage 13 共现硬过滤所用的邻近判据、以及 ss 轨的严格同句判据是三套不同口径, 不可互相复用; 本列的强度散布因此只反映实体窗口文本内的技术异质性, 既剔除了全文泛论噪声, 又保留了比同句窗更宽的上下文语境, 处于全文与同句两端之间的中间粒度。这一中间粒度正是 ctx 轨在稳健性谱系里的独特位置: 它既非最宽 (full) 亦非最窄 (ss), 与主轨相关性最低的实测特征, 使其成为检验主结论是否稳健于文本裁剪口径的最有力对照轨。

## VAR: attention_intensity_sd_ss

【变体差分】
本列是 ss (银行∧金科同句共现) 轨的稳健性载体, 是三轨中判据最严的一条。其文本口径取 stage 14 物化的 content_ss: 仅保留目标银行与金融科技词在同一句子 (±N 句窗, 由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1) 内共现的文本片段, 标题 prepend 于其上。据此计算逐篇 fintech_intensity_score_ss, 于银行-年内取样本标准差 (ddof=1) 得本列。ss 轨受软门控: 上游缺 fintech_intensity_score_ss 列时仅本轨优雅跳过 (graceful skip), full/ctx 两轨照常产出, 不连坐。ss 回退语义镜像 ctx: 当某篇不存在银行与金科的同句共现时, content_ss 退回全文 body 且 ss_is_fallback 置 True, 与分母共享 n_articles 口径。相对 ctx 轨的实体窗口, ss 轨要求银行与金科在句法上贴得更近, 因而刻画的是"银行被直接置于金融科技语境下叙述时"的技术强度散布, 是三轨中信噪比最偏保守的一端。需注意在早期试跑 T=2 面板上 ss 轨可能出现零方差退化, 属预期, 生产 T=19 面板恢复正常变异。本列为 conditional-on-full 子集轨, 与 sd_full、sd_ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J 过度识别检验。须辨明 ss 轨的同句共现判据 (extract_bank_fintech_cooccurrence 系严格同句口径) 与 stage 13 共现硬过滤所用的 ±1 句窗判据是两套不同原语, 不可混用: 前者界定 content_ss 的文本内容, 后者只做上游留行的硬过滤, 本列的强度散布严格建立在同句片段之上。正因判据最严, ss 轨在稀疏银行-年上最易触发回退 (退回全文 body), 分析者解读本列时应关注 ss_is_fallback 的占比, 以判断该轨在给定样本上究竟贴近同句语境还是已大面积退化为全文口径; 在生产 T=19 面板上这一回退占比通常可控, 使 ss 轨得以承担最保守一端的稳健性证据。

<!-- rendered-citations:end -->

<!-- rendered-citations:begin -->
Cookson, J. A., Lu, R., Mullins, W., & Niessner, M. (2024). The social signal. Journal of Financial Economics, 158, 103870. https://doi.org/10.1016/j.jfineco.2024.103870
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. The Journal of Finance, 78(3), 1449-1498. https://doi.org/10.1111/jofi.13219
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Angelo, B., Johnston, M., Singh, A., & Wan, Y. Q. (2025). Tone Distance: Managerial Tone Divergence and Market Reaction to Earnings Announcements. Financial Review. https://doi.org/10.1111/fire.70002
Lock, B. (2024). The Impact of News Media Coverage on Voluntary Disclosure. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12982
Klein, S. P., Spieth, P., Ricart, J. E., & Noble, C. H. (2024). How Media Coverage Elicits Strategic Change: The Moderating Role of the Business Model Design. Strategic Management Journal. https://doi.org/10.1002/smj.3688
<!-- rendered-citations:end -->
