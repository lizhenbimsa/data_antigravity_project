---
family_id: F595
columns:
- tone_x_depins_ctx
- tone_x_depins_full
- tone_x_depins_ss
unit: 交互项得分 (连续, 理论范围约 [-1,1]; llm_vote_tone 三分类共识票 × depins_post 0/1 断点哑变量, 逐年逐轨相乘, 无需再聚合)
formula: 'tone_x_depins{track} = llm_vote_tone{track} × depins_post, 其中 track ∈ {_full, _ctx, _ss}; depins_post = 1[year >= 2015] (《存款保险条例》国务院令第660号 2015-05-01 全国统一施行)'
producer: pipeline\panel\runner.py (L1651 depins_post 断点哑变量赋值, L1653-L1656 三轨循环生成 tone_x_depins{track}); pipeline\panel\export.py (L920-921, 变量标签映射; 仅收录 full/ctx 手列, _ss 由第三轨机械派生循环补全标签)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
- depins_post
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks
  venue: Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1093/rof/rfac052
  type: journal
  authors: Goldstein, I.
  year: 2023
  title: Information in Financial Markets and Its Real Effects
  venue: Review of Finance
  vol: '27'
  issue: '1'
  pages_or_artno: 1-32
new_dois: []
---

## CORE

【构念与来源】
tone_x_depins 家族是"银行舆论语调 × 存款保险制度时间断点"的调节项 (moderator interaction), 用于检验 2015 年《存款保险条例》(国务院令第660号, 2015-05-01 全国统一施行) 实施前后, 媒体报道语调对银行结果变量的边际效应是否发生结构性变化。构念上它回答的问题不是"语调本身多正面/多负面", 而是"同样一单位语调冲击, 在存款保险制度覆盖后 vs. 覆盖前, 对下游变量 (如资金成本、存款稳定性) 的传导强度是否不同"。这类调节项设计遵循计量经济学中交互项作为异质性效应估计工具的通行做法 (export.py 注释显式引用其构造逻辑), 即交互项系数须与其构成项 (constituent terms) 一并解读, 不能孤立看待。存款保险制度的选取理由: 它是一项全国统一实施的制度性断点, 理论上系统性改变了储户/投资者对银行负债端 (存款) 风险的先验认知——保险覆盖后, 储户对银行负面消息的敏感度理应下降 (道德风险/存款人纪律削弱的经典命题), 因此语调对银行的边际影响在断点前后可能不对称。这与 Goldstein (2023, Review of Finance) 关于金融市场信息与其真实效应的一般性讨论, 以及 depositor discipline/bank run 文献 (如 Fang et al. 2024, International Review of Economics & Finance, 中国银行级媒体情感样本同域先例) 中"信息冲击的传导强度依赖于制度安排"的核心命题相呼应。

【方法学与计算】
构造上, tone_x_depins{track} 是两个已存在列的逐行乘积, 不引入新的测量误差或建模假设, 是纯粹的机械交互项 (非 DID 设计, 无处理组/对照组分割——制度全国统一施行, 无法用 `merge_policy_shocks()` 的 `bank_province.isin(provs)` 匹配逻辑实现, 因为"全国"不是有效省份名, 见 44_panel_iv_did.py L513-517 的显式排除说明)。第一构成项 llm_vote_tone{track} 是 stage 21 三家 LLM (`gpt-5.4-nano`/gpt54nano · `gemini-3.1-flash-lite`/gemini31 两家走 yunwu · `deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com) 多数投票的语调共识分, 值域约 [-1, 1] (负面/中性/正面三分类编码后聚合)。第二构成项 depins_post 是时间断点哑变量, `year >= 2015` 时取 1, 否则取 0, 全库统一、与地理/银行属性无关。三轨循环 (`for track in ['_full','_ctx','_ss']`) 逐轨检查 `llm_vote_tone{track}` 列是否存在于面板, 存在才生成对应交互列, 因此三条轨道各自独立、互不依赖——full 缺失不影响 ctx/ss 的生成, 反之亦然。本口径与本仓库三轨架构的通用铁律一致: full=标题+正文全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗口 (回退语义镜像 ctx——无银行∧金科同句共现时 content_ss 退化为全文 body, `ss_is_fallback=True`); 三轨情感留篇门控口径为 full-only (2026-06-29 起), 即"是否算作一篇有效银行金科报道"只看 `llm_verified_full==True`, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集合的子集。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁在同一 over-identified Hansen J 检验中混用三轨交互项。producer 源码内嵌了一条显式的退化守卫 (fix log-reaudit-2026-06-20, P2-C): 若 `depins_post.nunique() <= 1`, 即样本年份未跨越 2015 断点 (本机开发盘面 T=2, 样本年份为 {2017, 2018}, 全部 ≥2015), depins_post 退化为常量 1, 此时 tone_x_depins* 交互项在数学上等价于 tone×1, 即语调本身, 完全丧失识别力 (会被面板固定效应或与母项的共线性吸收), 此时会打印显式 WARNING 提醒不可用作断点效应估计。生产语料 T=19 (2007–2025) 天然跨越 2015 断点, 该守卫不会触发, depins_post 恢复应有方差, 交互项获得可识别的断点前/断点后对比。

【文献定位】
sentiment-and-interaction 设计的方法学基础主要来自两支文献汇流: 一支是文本情感测量本身的构造有效性文献, 另一支是交互项/调节效应的计量规范文献。前者的奠基性工作是 Loughran & McDonald (2011, Journal of Finance) 对财报文本情感词典构造有效性的系统检验, 该文奠定了"文本语调需以领域特定词典/规则校准, 而非套用通用情感词典"的方法学共识, 本仓库 stage 22 词典轨与 stage 21 LLM 轨均直接承袭这一传统; 后者的规范做法要求交互项系数的因果解读须以构成项 (tone、depins_post) 同时进入模型为前提, 且断点前/后的边际效应差异应通过交互系数而非分组均值直接比较来识别。存款保险制度作为负债端风险感知的结构性断点这一构念, 与 Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 关于中国银行级媒体情感、存款稳定性与系统性风险关系的研究在样本对象 (中国银行业) 与理论机制 (媒体情感的负债端传导) 上高度贴合, 是本交互项设计最直接的同域先例。

## VAR: tone_x_depins_ctx

【变体差分】
本列取 track=_ctx, 即语调构成项来自 `llm_vote_tone_ctx`——该情感测度基于"标题+实体窗口"文本轨 (银行/金科实体前后固定窗口截取, 而非全文), 与 tone_x_depins_full 的全文语调、tone_x_depins_ss 的同句语调构成互为稳健性并排的测量口径, 不分主次, 不应放入同一 over-identified 识别策略。留篇门控口径为 full-only, 因此本列的行宇宙 = full 留篇集合的子集, 计算在该子集上逐年 (含 2015 前后) 按 ctx 轨语调值与 depins_post 相乘。第二构成项 depins_post 三轨共享同一个哑变量 (无轨道差异)。本机开发盘面 T=2 (样本年份 {2017,2018} 全部 ≥2015) 下, 本列与其余两轨同样退化为常量语调本身、无识别力, producer 已显式 WARNING; 生产 T=19 (2007–2025) 跨越 2015 断点后本列与 full/ss 轨恢复独立方差, 可用于比较"实体窗口语调"与"全文语调"在断点效应估计上的稳健性一致程度。

实体窗口 (ctx) 语调的构造前提是 stage 14 `ctx_materializer` 对 `content_ctx` 的物化——围绕目标银行/金科实体截取固定窗口的正文片段并前置标题 (prepend_title), 而非直接沿用全文, 因此其信息集比 full 更窄、更聚焦于实体周边语境, 理论上对无关段落的噪声更不敏感, 但也可能丢失全文层面的语境信息 (如段落间的转折/让步关系)。在存款保险断点效应的应用场景下, ctx 语调回答的问题是"围绕银行实体本身的近距离语调, 在制度覆盖前后传导强度是否不同", 与 full 语调回答的"整篇报道语调"是一个相近但不完全等价的构念。二者预期方向一致但幅度可能不同, 差异本身即是稳健性检验的一部分, 不应把二者中的任何一方视为另一方的"真值"。研究者在报告断点效应时应同时呈现 full/ctx/ss 三轨结果并比较符号与显著性的一致性, 而非仅报告单一轨道。

## VAR: tone_x_depins_full

【变体差分】
本列取 track=_full, 语调构成项来自 `llm_vote_tone_full`——基于标题+全文正文的语调共识分, 是留篇门控 (2026-06-29 起) 直接锚定的口径, 即三轨中唯一决定"是否算作一篇有效银行金科报道"的轨道, 其行宇宙即为 full 留篇集合本身 (ctx/ss 是其子集上的稳健性轨)。作为 P1 paper (`bank_fintech_tone`) 的主 treatment `llm_vote_tone_full` 的直接衍生交互项, tone_x_depins_full 是三轨中在多数下游 replication 模板里被优先引用的口径, 但这并不构成"主轨"意义上的优先——三轨在识别策略上仍各自 just-identified 并排, 互为稳健性。与 tone_x_depins_ctx/tone_x_depins_ss 的区别仅在语调构成项的文本窗口不同, depins_post 断点哑变量本身完全相同、无轨道差异。同样受本机 T=2 盘面 (年份全部 ≥2015) 的常量退化守卫约束, 生产 T=19 语料恢复方差后方具备断点前/后对比识别力。

之所以 tone_x_depins_full 常被下游 replication 模板优先引用, 是因为 llm_vote_tone_full 是 P1 paper 主 treatment 的规范口径, 且 full-only 门控意味着它的行宇宙即为面板的完整留篇集合, 不存在 ctx/ss 因窗口截取或严格同句判据未命中而产生的子集收缩问题——因此它在样本量与覆盖率上通常最大。但这不改变三轨"各自 just-identified 并排、互为稳健性不分主次"的识别策略定位: 若某项分析仅报告 tone_x_depins_full 的断点效应而不附带 ctx/ss 的稳健性对照, 应在稳健性附录中补齐, 而不能把 full 轨结果直接当作跨轨已验证的结论。此外须注意, tone_x_depins_full 与 tone_x_stress_full (压力年份 {2015,2018,2020} 交互项, 同一 producer 代码段紧邻生成) 是两个不同的调节变量家族——前者刻画制度性时间断点, 后者刻画宏观压力冲击年份, 二者虽共享同一语调构成项但断点定义与理论机制完全独立, 不可混淆或替代使用。

## VAR: tone_x_depins_ss

【变体差分】
本列取 track=_ss, 语调构成项来自 `llm_vote_tone_ss`——基于"标题+银行∧金科同句±N窗口" (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1) 的语调共识分, 是三轨中判定口径最严格的一支: 若某篇文章中银行实体与金科词不出现在同一句 (或未落入回退窗口), 则该篇的 content_ss 按镜像 ctx 的回退语义退化为全文 body, 并置 `ss_is_fallback=True` (与 ctx 共享 `n_articles` 分母口径)。行宇宙同样受 full-only 留篇门控约束, 是 full 留篇集合的子集。depins_post 断点哑变量与 full/ctx 两轨完全共享、无差异, 交互项的构造机制 (逐行相乘) 与另外两轨一致。producer 端的三轨循环对 ss 轨与 full/ctx 轨一视同仁地检查列存在性并生成交互列 (无优先级差异); export.py 的变量标签字典只手列了 full/ctx 两轨标签, ss 轨标签由"第三轨机械派生循环"在字面量闭合后自动补全 (与 herd_weight 等其它三轨族的标签补全机制相同, 非本列独有的例外处理)。本列同样受本机 T=2 盘面常量退化守卫约束, 生产 T=19 语料下与 full/ctx 两轨互为稳健性并排, 用于检验"银行∧金科严格同句语调"在存款保险制度断点前后的边际效应是否与更宽松窗口 (ctx) 或全文 (full) 口径保持方向一致。

ss 轨的构造判据 (银行∧金科同句共现) 与 stage 13 `cooccurrence_filter` 的硬过滤判据 (`sentence_radius`=1 邻近共现) 属两套不同原语 (`extract_bank_fintech_cooccurrence` 严格同句 vs. `has_bank_fintech_cooccurrence_within_radius` ±1 句窗口), 二者禁止互相复用, 但共同作用的结果是: ss 轨语调是三轨中最"贴近实体共现瞬间"的测度——它捕捉的是记者在同一句话内同时提及银行与金科话题时所使用的措辞语调, 理论上比 ctx (实体窗口, 允许银行与金科分处不同句) 或 full (全文) 更直接地反映"银行与金科同时被提及时的舆论评价"。在存款保险制度断点效应的检验中, ss 轨交互项适合用作"最严格判据下效应是否依然存在"的加严稳健性检验: 若 full/ctx 均显著而 ss 因回退样本占比高、有效方差不足而不显著, 不应被解读为效应不存在, 而应结合 ss_is_fallback 占比一并报告, 避免误判。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Goldstein, I. (2023). Information in Financial Markets and Its Real Effects. Review of Finance, 27(1), 1-32. https://doi.org/10.1093/rof/rfac052
<!-- rendered-citations:end -->
