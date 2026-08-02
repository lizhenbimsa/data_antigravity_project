---
family_id: F185
columns:
- deepseekv4_tone_sum_ctx
- deepseekv4_tone_sum_full
- deepseekv4_tone_sum_ss
- gemini31_tone_sum_ctx
- gemini31_tone_sum_full
- gemini31_tone_sum_ss
- gpt54nano_tone_sum_ctx
- gpt54nano_tone_sum_full
- gpt54nano_tone_sum_ss
unit: 语调符号净加总 (整数; 单模型对 bank-year 内每篇报道三分类语调码求和)
formula: "{short}_tone_sum{track} = Σ_i {short}_score{track}_i, 对 groupby(bank, year) 内该轨样本篇 i 求和; {short}_score ∈ {-1, 0, +1} (负/中性/正), short ∈ {deepseekv4, gemini31, gpt54nano}, track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py::(agg 'sum' on {short}_score{track}) ; news_process/pipeline/sentiment/tone_llms.py (article-level 三分类语调)
upstream:
- 21_tone_llms.parquet ({short}_score_full / _ctx / _ss, llm_verified_full 门控)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: FEDS Working Paper No. 2026-020, Federal Reserve Board
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.48550/arXiv.2503.03612
  type: arxiv
  authors: Kirtac, K., & Germano, G.
  year: 2025
  title: "Large language models in finance: What is financial sentiment?"
  venue: arXiv
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
  venue: SSRN Working Paper No. 4412788
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画三家大语言模型 (LLM) 各自对某银行某年全部报道所判语调码的年内加总, 是逐模型情感强度的整数汇总度量。九列由供应商短名 (deepseekv4、gemini31、gpt54nano) 与文本轨 (full、ctx、ss) 二维笛卡尔积构成, 每列都是先在文章层由单一模型对报道给出三分类语调判定 (负面记 -1、中性记 0、正面记 +1), 再按 bank-year 分组对该模型该轨的语调码求和得到。上游文章层判定产于阶段 21 (tone_llms.py): 每条报道以统一的思维链 Prompt 同时向三家模型逐条并发请求, 单次调用即返回真伪精筛与情感判定; 三家模型分别是直连 api.deepseek.com 的 DeepSeek V4 Flash、经 OpenLux 路由的 gemini-3.1-flash-lite 与 gpt-5.4-nano。这一逐模型加总不同于多数投票共识轨 (llm_vote_tone_sum), 也不同于逐模型均值轨 (deepseekv4_tone 等); 它保留了整数计数尺度, 使得同一分母 (该行报道篇数) 下净语调倾向与报道密度的耦合关系在建模时可显式拆解。

【方法学与计算】
计算链路分两级。第一级在阶段 21 文章层: 模型对每条报道输出三分类语调, 落列 {short}_score{track} ∈ {-1, 0, +1}。第二级在面板编码 encode.py: 对 groupby(bank, year) 内该轨样本篇执行 pandas 聚合的 sum, 即 agg[f'{short}_tone_sum{track}'] = (f'{short}_score{track}', 'sum'), 因而得到 int64 的语调符号净加总。留篇门控采 full-only 口径 (2026-06-29): 一条报道是否算作一篇银行金科报道只由 llm_verified_full 为真判定, ctx 与 ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集, 各轨列在其自身样本上照算。加总为整数, 其符号与量级同时编码了该模型对该银行该年舆论的净倾向 (正负号) 与被判为非中性报道的净条数 (绝对值上界为该行样本篇数)。因加总未除以篇数, 它与逐模型均值轨互补而非冗余: 均值消去了规模、加总保留了规模。

【文献定位】
以 LLM 直接对金融文本判语调, 承接文本情感测度从词典法、监督式机器学习到生成式模型的方法学演进。Tetlock (2007) 奠定媒体语调进入资产定价的经典范式, 说明报道语调本身携带增量信息; Holzman, Miller 与 Twedt (2023) 进一步论证媒体语调的加权与规范化对经济含义至关重要, 为本家族保留整数加总 (规模敏感) 尺度提供了度量学理由。生成式模型侧, Gilardi, Alizadeh 与 Kubli (2023) 证明 ChatGPT 在文本标注任务上可超越众包工人, de Kok (2025) 给出会计研究中用生成式 LLM 做文本分析的规范流程 (temperature=0、Prompt 冻结、缓存复现), 本管道正据此冻结 Prompt v8 并温度置零以求可复现。Kirtac 与 Germano (2025) 与 Lopez-Lira 与 Tang (2023) 检验 LLM 金融情感的预测效度。方法学告诫方面, Carlson 与 Burbano (2026) 与 Hansen (2026) 分别就管理学 LLM 标注的基础守则与无金标准时的标注验证 (κ/α 一致性设计) 提出要求, Ludwig, Mullainathan 与 Rambachan (2025) 给出把 LLM 输出纳入计量框架的应用经济学范式。三家模型逐列并排正是回应上述文献对跨模型稳健性与三角验证的诉求: 三家各自的逐模型子测度并排为互为稳健性、不分主次的轨, 各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J 检验; 同理三轨 (full/ctx/ss) 亦各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。

## VAR: deepseekv4_tone_sum_ctx

【变体差分】
本列锁定 DeepSeek V4 Flash 模型 (供应商短名 deepseekv4, 直连深度求索接口, 与经 OpenLux 路由的另两家不同源) 在 ctx 轨的语调符号净加总。ctx 轨输入文本等于标题前置拼接加上目标银行实体窗口的上下文片段, 采用实体邻近口径圈定与目标银行相关的语境, 由阶段 14 的上下文物化器物化 (实体窗口口径不同于同句共现轨的正负一句窗)。相对家族全文轨的规范列, 本列差在两处: 一是供应商固定为深度求索单独一家 (既非三家投票共识, 也非三家均值集成), 二是文本轨为实体窗口而非全文正文。留篇门控仍是仅看全文的口径: 行宇宙是全文留篇集的子集, 本列在其上下文轨样本上按分组求和对该模型该轨的三分类语调码相加, 得到整数净值。整数尺度使该模型对该行舆论的净倾向 (符号) 与被判非中性报道的净条数 (绝对值) 同时可读, 这与仅保留倾向、消去规模的均值轨形成互补而非冗余。它与本家族其余八列 (另两家模型、另两条轨) 互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验; 跨模型一致性由科恩卡帕与克里彭多夫阿尔法度量, 而非把三家读数并入单一回归式。开发语料期数为二时上下文轨样本稀疏, 加总可能退化为小整数或零, 属预期退化而非缺陷, 生产语料期数为十八时区分度恢复。

## VAR: deepseekv4_tone_sum_full

【变体差分】
本列是深度求索模型在全文轨的语调符号净加总, 也是本家族深度求索支族的规范轨。全文轨输入等于标题前置拼接加上全文正文, 是留篇门控的判定文本轨: 依据仅看全文的口径, 一条报道是否算作一篇银行金科报道只看该模型在全文轨的验证标记是否为真。本列对分组内全文样本篇的该模型三分类语调码求和得到整数。它相对家族其他列的差分维度是供应商 (深度求索单独一家, 既非三家投票共识, 也非三家均值集成) 与文本轨 (全文正文, 既非实体窗口, 也非同句共现)。作为规模敏感的加总度量, 其绝对值上界为该行全文样本篇数, 符号编码该模型对该行舆论的净倾向, 量级则编码被判为非中性报道的净条数。由于加总未除以篇数, 它与逐模型均值轨互补: 均值消去规模、加总保留规模, 在需要显式拆解净语调倾向与报道密度耦合关系的建模场景各有用途。本列与另两家模型的同轨列、与本模型另两条轨列均互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验; 跨模型真正的族错误率校正走根级步进式模板 (即跨模型稳健性表), 而非把三家加总塞进同一过度识别检验。逐模型独立降级: 某家缺席仅掉其自身族列, 不触发嵌入双轨那种同置缺失的连坐。

## VAR: deepseekv4_tone_sum_ss

【变体差分】
本列是深度求索模型在同句共现轨的语调符号净加总。此轨输入等于标题前置拼接加上同一句内同时含目标银行与金科词的句及其正负一窗口片段, 是三轨中语义边界最窄、共现约束最严的一条。当某报道无银行金科同句共现时, 该轨镜像上下文轨的回退语义: 输入退回全文正文, 同句回退标记置真, 并与上下文轨共享同一篇数分母, 以保证优雅降级而非静默清空。本列相对家族规范轨差在供应商 (深度求索单独一家) 与文本轨 (最严格的同句共现口径)。留篇门控仍是仅看全文, 本列在全文留篇集的同句共现子样本上对该模型三分类语调码求和得到整数。三条轨各自恰好识别并排、互为稳健性、不分主次, 严禁混进同一过度识别的汉森 J 检验; 同句共现轨是三轨中语义最窄的稳健性轨, 全文轨是判定报道归属的主轨, 上下文轨与同句共现轨则是条件于全文留篇的测度与稳健性轨。开发语料期数为二时, 此轨因同句共现稀疏与回退频繁, 加总常退化为接近全文轨的读数或小整数, 属预期退化; 生产语料期数为十八时, 语料密度提升使三轨区分度恢复。

## VAR: gemini31_tone_sum_ctx

【变体差分】
本列锁定谷歌闪电轻量模型 (供应商短名 gemini31, 经 OpenLux 路由, 与直连的深度求索不同源) 在上下文轨的语调符号净加总。文本轨等于标题前置拼接加上目标银行实体窗口的上下文, 由阶段 14 物化 (实体窗口口径, 非同句共现轨的正负一句窗)。相对家族全文规范轨, 差分维度为供应商 (谷歌单独一家, 与深度求索、开放智能跨厂商并列构成三家稳健性梯子) 与文本轨 (实体窗口, 非全文正文)。留篇门控仍是仅看全文: 行宇宙是全文留篇集子集, 本列对该行上下文样本的该模型三分类语调码按分组求和得到整数。作为跨模型稳健性梯子的一支, 本列与另两家模型的同轨列、与谷歌本家另两条轨列互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验。它保留规模 (整数加总而非除以篇数), 与逐模型均值轨互补: 前者同时携带净倾向与净条数, 后者只留净倾向。模型间一致性由克里彭多夫阿尔法与科恩卡帕在语调验证环节度量, 而非把三家读数并入单一回归式。开发语料期数为二时上下文样本稀疏, 加总可能仅为小整数, 属预期退化, 生产语料期数为十八时区分度恢复。

## VAR: gemini31_tone_sum_full

【变体差分】
本列是谷歌闪电轻量模型 (经 OpenLux 路由) 在全文轨的语调符号净加总, 是谷歌支族的规范轨。全文轨输入等于标题前置拼接加上全文正文, 承载仅看全文的留篇门控: 该模型全文轨验证标记判定一条报道是否算作一篇银行金科报道。本列相对家族其余列差在供应商 (谷歌单独一家的跨厂商轨, 既非三家投票共识, 也非三家均值集成) 与文本轨 (全文正文)。对分组内全文样本篇的该模型三分类语调码求和得到整数, 绝对值上界为该行全文样本篇数, 符号编码谷歌对该行舆论净倾向, 量级编码被判非中性报道净条数。三家模型逐列并排是刻意设计的跨厂商稳健性: 本列与深度求索、开放智能的同轨列互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验; 跨模型族错误率校正走根级步进式模板。与本家族逐模型均值轨的区别在于本列保留规模 (不除篇数), 从而能显式拆解净语调倾向与报道密度的耦合。逐模型独立降级: 某家缺席仅掉其自身族列, 不触发跨主测度嵌入双轨那种同置缺失的连坐。

## VAR: gemini31_tone_sum_ss

【变体差分】
本列是谷歌闪电轻量模型在同句共现轨的语调符号净加总。此轨文本等于标题前置拼接加上同一句内同时含目标银行与金科词的句及其正负一窗口, 是三轨中共现约束最严的一条; 无同句共现时镜像上下文轨的回退语义, 输入退回全文正文、同句回退标记置真、并与上下文轨共享同一篇数分母, 以保证优雅降级。相对家族规范轨, 差分维度为供应商 (谷歌单独一家) 与文本轨 (最严格同句共现口径)。留篇门控仍是仅看全文, 本列在全文留篇集的同句共现子样本上对该模型三分类语调码求和得到整数, 绝对值上界为该子样本篇数。三条轨各自恰好识别并排、互为稳健性、不分主次, 严禁混进同一过度识别的汉森 J 检验; 同句共现轨是语义最窄的稳健性轨, 全文轨为判定报道归属的主轨, 上下文轨与同句共现轨为条件于全文留篇的测度轨。本列与另两家模型的同句共现列并排, 构成跨厂商稳健性的一支。开发语料期数为二时, 因同句共现稀疏与回退频繁, 加总常退化为接近全文轨或小整数, 属预期退化; 生产语料期数为十八时, 语料密度提升使区分度恢复。

## VAR: gpt54nano_tone_sum_ctx

【变体差分】
本列锁定开放智能纳米模型 (供应商短名 gpt54nano, 经 OpenLux 路由) 在上下文轨的语调符号净加总。文本轨等于标题前置拼接加上目标银行实体窗口的上下文片段, 由阶段 14 物化 (实体窗口口径, 非同句共现轨的正负一句窗)。相对家族全文规范轨, 差分维度为供应商 (开放智能单独一家, 与深度求索、谷歌跨厂商并列构成三家稳健性梯子) 与文本轨 (实体窗口, 非全文正文)。留篇门控仍是仅看全文: 行宇宙是全文留篇集子集, 本列对该行上下文样本的该模型三分类语调码按分组求和得到整数。作为跨模型稳健性梯子的一支, 本列与另两家模型的同轨列、与开放智能本家另两条轨列互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验。它保留规模 (整数加总而非除以篇数), 与逐模型均值轨互补: 加总同时携带净倾向与净条数, 均值只留净倾向。模型间一致性由克里彭多夫阿尔法与科恩卡帕度量, 而非把三家读数并入单一回归式。开发语料期数为二时上下文样本稀疏, 加总或退化为小整数, 属预期退化而非缺陷, 生产语料期数为十八时区分度恢复。

## VAR: gpt54nano_tone_sum_full

【变体差分】
本列是开放智能纳米模型 (经 OpenLux 路由) 在全文轨的语调符号净加总, 是开放智能支族的规范轨。全文轨输入等于标题前置拼接加上全文正文, 承载仅看全文的留篇门控: 该模型全文轨验证标记判定一条报道是否算作一篇银行金科报道。本列相对家族其余列差在供应商 (开放智能单独一家的跨厂商轨, 既非三家投票共识, 也非三家均值集成) 与文本轨 (全文正文)。对分组内全文样本篇的该模型三分类语调码求和得到整数, 绝对值上界为该行全文样本篇数, 符号编码开放智能对该行舆论净倾向, 量级编码被判非中性报道净条数。本列与深度求索、谷歌的同轨列互为稳健性、不分主次, 各自恰好识别并排, 严禁混进同一过度识别的汉森 J 检验; 跨模型族错误率校正走根级步进式模板 (即跨模型稳健性表), 不把三家加总塞进同一过度识别检验。与逐模型均值轨的区别在于本列保留规模 (不除篇数), 从而能显式拆解净语调倾向与报道密度的耦合关系。逐模型独立降级: 某家缺席仅掉其自身族列, 不触发跨主测度嵌入双轨那种同置缺失的连坐。

## VAR: gpt54nano_tone_sum_ss

【变体差分】
本列是开放智能纳米模型在同句共现轨的语调符号净加总。此轨文本等于标题前置拼接加上同一句内同时含目标银行与金科词的句及其正负一窗口片段, 是三轨中共现约束最严的一条; 无同句共现时镜像上下文轨的回退语义: 输入退回全文正文、同句回退标记置真、并与上下文轨共享同一篇数分母, 以保证优雅降级而非静默清空。相对家族规范轨, 差分维度为供应商 (开放智能单独一家) 与文本轨 (最严格同句共现口径)。留篇门控仍是仅看全文, 本列在全文留篇集的同句共现子样本上对该模型三分类语调码求和得到整数, 绝对值上界为该子样本篇数。三条轨各自恰好识别并排、互为稳健性、不分主次, 严禁混进同一过度识别的汉森 J 检验; 同句共现轨是三轨中语义最窄的稳健性轨, 全文轨是判定报道归属的主轨, 上下文轨与同句共现轨为条件于全文留篇的测度轨。本列与另两家模型的同句共现列并排, 构成跨厂商稳健性的一支。开发语料期数为二时, 因同句共现稀疏与回退频繁, 加总常退化为接近全文轨的读数或小整数, 属预期退化; 生产语料期数为十八时, 语料密度提升使三轨区分度恢复。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Kirtac, K., & Germano, G. (2025). Large language models in finance: What is financial sentiment? arXiv [Preprint]. https://doi.org/10.48550/arXiv.2503.03612
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper No. 4412788 [Working Paper]. https://doi.org/10.2139/ssrn.4412788
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
