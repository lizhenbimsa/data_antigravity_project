---
family_id: F370
columns:
  - llm_peer_count
  - llm_peer_count_70
  - llm_peer_count_75
  - llm_peer_count_80
  - llm_peer_count_85
  - llm_peer_count_90
unit: 篇数/计数 (count)
formula: "llm_peer_count = |peer_map(bank, year)|, peer_map 由 LLM 对每个 (bank, year) 直接输出的二元同行名单 JSON ({\"peers\":[...]}) 经 _normalize_peer_names 归一化 (精确匹配/简称变体映射/唯一子串匹配三策略, OOV 拒绝) 后去重计数; 后缀 _70/_75/_80/_85/_90 是历史遗留的 difflib.get_close_matches cutoff 参数标签, 该参数自 fix omni-g-llm-peer-04 (2026-06-11) 移除 difflib 兜底策略后已完全惰性 (inert)、不参与任何归一化判定, 六列在同一 peer_map 逻辑下结构性逐位相同 (盘上实证: nonnull 数与 mean 六档全同), 保留仅为 Stata schema 兼容 (derivative_replication.py CUTOFF_VARS 消费), 不构成 TNIC/Cao 式连续相似度阈值敏感性梯子"
producer: news_process/pipeline/panel/llm_peer_iv.py::compute_llm_peer_iv (下游注册名映射见 news_process/pipeline/panel/export.py)
upstream:
  - 21_tone_llms.parquet (LLM 三家投票留篇集, full-only 门控)
  - 40_panel_yearly.parquet (bank-year 面板骨架, 在册银行清单)
citations:
- doi: 10.1007/s11142-025-09892-6
  type: journal
  authors: Cao, Y., Chen, L., Tucker, J. W., & Wan, C.
  year: 2025
  title: "Can generative AI help identify peer firms?"
  venue: Review of Accounting Studies
  vol: 30
  issue: 4
  pages_or_artno: 3344-3386
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: "Text-based network industries and endogenous product differentiation"
  venue: Journal of Political Economy
  vol: 124
  issue: 5
  pages_or_artno: 1423-1465
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
  vol: 60
  issue: 3
  pages_or_artno: 531-542
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: "Identification of peer effects through social networks"
  venue: Journal of Econometrics
  vol: 150
  issue: 1
  pages_or_artno: 41-55
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: "10.1016/j.jeconom.2022.10.004"
  title: "Peer effects and endogenous social interactions"
  authors: "Jochmans, K."
  year: 2023
  venue: "Journal of Econometrics"
  type: "journal"
  one_sentence_zh: "提出无需为同行选择过程建模、仅利用固有约束构造条件矩条件来处理同行自选择问题的新方法, 深化 Manski 反射问题在内生社交网络下的可识别性讨论。"
- doi: "10.1016/j.jeconom.2023.02.013"
  title: "Efficient peer effects estimators with group effects"
  authors: "Kuersteiner, G. M., Prucha, I. R., & Zeng, Y."
  year: 2023
  venue: "Journal of Econometrics"
  type: "journal"
  one_sentence_zh: "为群组内同行效应线性模型 (含未观测随机组效应与可观测固定组效应) 提出高效 GMM 估计量族, 为 llm_peer_count 下游同行均值 IV 的估计效率提供最新方法论参照。"
new_dois:
  - "10.1016/j.jeconom.2022.10.004"
  - "10.1016/j.jeconom.2023.02.013"
---

## CORE

【构念与来源】

llm_peer_count 家族刻画的是"由大语言模型直接查证得到的银行同行名单规模"——对每一家焦点银行 i、每个年份, llm_peer_iv.py 用固定 prompt 版本、温度 0 向 LLM 发起一次查证请求 (结果落地到 `_llm_cache.db` 供跨 run 复现), 要求模型直接返回一份二元的同行银行名单 JSON (形如 `{"peers": [...]}`), 而不是对每一对 (i, j) 银行输出连续的 0–1 相似度打分。名单中的原始名称字符串经 `_normalize_peer_names` 归一化——依次尝试策略 1 精确匹配、策略 2 简称/变体映射 (如"工行"→"中国工商银行")、策略 3 唯一子串匹配 (命中恰好一家规范名才接受, 命中 >1 家的行业泛称一律拒绝), 三策略均未命中的名称按 OOV (out-of-vocabulary) 直接拒绝丢弃——归一化、去重后得到 peer_map(bank, year), llm_peer_count 即该 peer_map 的基数 (`|peer_map(bank, year)|`)。

必须澄清的是: 本家族六列共享的不是一套连续相似度打分矩阵配阈值门槛, 而是同一份 LLM 二元同行名单经同一套归一化逻辑得到的同一个 peer_map——canonical 无后缀列与 `_70`/`_75`/`_80`/`_85`/`_90` 五个后缀列的差异, 源自源码中一个历史遗留参数: 该参数最初 (2026-06-11 之前) 是归一化流程"策略 4"里 `difflib.get_close_matches(cutoff=...)` 的字符串模糊匹配严格度, 用于在精确/变体/子串三策略都未命中时把 LLM 吐出的银行名近似"吸附"到规范名清单; fix omni-g-llm-peer-04 (2026-06-11) 因该兜底策略存在错配问题而将其整体移除, 归一化只保留策略 1–3 (精确匹配/变体映射/唯一子串匹配) 与 OOV 拒绝, 策略 4 及其 cutoff 参数不复存在。源码在步骤 5 (peer_map 解析) 与步骤 6 (命名勘误) 两处用大写注释明确披露: "此 cutoff 原是 difflib.get_close_matches 的字符串匹配严格度 (银行名归一), 不是 TNIC 的同行语义相似度阈值, 勿将 cutoff 扫描标注为 TNIC/Cao 相似度阈值", 且"策略 1-3 与 cutoff 无关 → 五档后缀列结构性逐位相同 (盘上实证: nonnull 数与 mean 五档全同)"。也就是说, `_70`/`_75`/`_80`/`_85`/`_90` 五个后缀列在当前实现下对结果完全惰性 (inert)、不产生任何识别力上的差异, 六列 (含无后缀 canonical) 理论上应逐行数值恒等; 保留这五个后缀列仅出于 Stata schema 兼容 (`derivative_replication.py::CUTOFF_VARS` 下游消费遍历需要完整的 {70,75,80,85,90} 后缀集合), 不构成、也不应被误读为一条 TNIC/Cao 式连续相似度阈值敏感性梯子。任何把这六列当作"阈值越高同行集合越小"的单调因果链条来解读或汇报的做法, 都直接违背源码的显式反向披露, 论文表注若引用这一族列, 必须如实注明该灵敏度维度无识别变差; 真正有识别力的稳健性维度 (如同行名单上限 max peers / 单模型 vs 多模型查证 / 句子口径) 须另行扫描, 不由本家族提供。

llm_peer_count 本身不是模型估计使用的工具变量, 而是一个诊断/披露变量: 它衡量的是"LLM 直接给出的同行名单里有多少家银行"——这个数字覆盖的是全部在册银行 (包含未必落在 bank-year 面板样本内的银行), 而真正进入 `llm_peer_tone_iv_*` 均值计算的同行集合还要求该同行本身在当期面板内且有可用的滞后一期语调观测, 这个"实际参与均值计算"的子集数量另由 llm_peer_n_effective 记录——两者刻意区分, llm_peer_count 是网络连通度的上界口径, llm_peer_n_effective 是 IV 有效识别域的下游口径, 二者不可混用互代。此外 llm_peer_queried 列区分"LLM 已完成查证但同行集合恰好为空"与"该银行尚未查证"两种零值成因, llm_peer_count 本身的零值需要配合 llm_peer_queried 判读, 不能把未查证的缺失当作"零同行"的实质性结论。

从识别策略的角度看, 本家族服务于 llm_peer_iv.py 模块实现的"同行网络语调 IV"识别设计: 该设计的方法论参照系是 Hoberg & Phillips (2016) 提出的 TNIC (Text-based Network Industry Classification) 文本网络产业分类方法论, 后者用文本相似度而非人工行业代码来界定产品市场竞争同行; 但本模块与 TNIC 在实现路径上有实质差异——TNIC 计算的是连续的文本余弦相似度并配以阈值切分, 本模块则是让生成式 LLM 在给定候选银行清单与业务画像描述的前提下, 一次性直接输出该焦点银行的二元同行名单 (而非对每一对银行输出连续相似度分数), 属于"生成式判定"而非"连续打分+阈值切分"的范式, 二者只在"用文本/语义信息界定同行, 而非沿用人工行业代码"这一大方向上呼应, 具体计算机制并不相同。这一"让 LLM 直接判定同行归属"的做法呼应 Cao, Chen, Tucker & Wan (2025, Review of Accounting Studies) 关于生成式 AI 能否识别同行企业的直接研究发现——该文的核心结论是 LLM 在识别产品市场竞争同行方面相较传统文本网络方法具有增量信息含量, 这正是本模块选择以 LLM 直接查证同行名单、而非沿用连续文本相似度网络方法的方法学依据。de Kok (2025, Management Science) 则为"用生成式 LLM 做会计与金融文本分析任务"这一大类方法论提供了操作规范参照, 包括温度设为 0、prompt 版本冻结、结果可复现缓存等实践, 本项目在 stage 21 情感 LLM 与 llm_peer 查证任务上均遵循同一套确定性锚点纪律 (对照 CLAUDE.md「确定性/golden」条目)。

在同行效应识别的理论脉络上, llm_peer_count 及其派生的同行语调 IV 面对的核心挑战是 Manski (1993, The Review of Economic Studies) 提出的"反射问题" (reflection problem): 当同一群体内的个体相互影响、又共同受到相同的外生冲击时, 无法从群体均值行为反推因果方向。本模块的应对策略是以滞后一期同行语调 (而非同期) 作为工具, 并在计算同行均值时做文章级 leave-out (剔除与焦点银行在同一篇报道中被共同提及的文章), 以缓解"共享报道"带来的机械相关。提出无需为同行选择过程建模、仅利用固有约束构造条件矩条件来处理同行自选择问题的新方法, 深化 Manski 反射问题在内生社交网络下的可识别性讨论, 引用格式 Jochmans (2023, Journal of Econometrics)。为群组内同行效应线性模型 (含未观测随机组效应与可观测固定组效应) 提出高效 GMM 估计量族, 为 llm_peer_count 下游同行均值 IV 的估计效率提供最新方法论参照, 引用格式 Kuersteiner, Prucha, & Zeng (2023, Journal of Econometrics)。这一策略的局限性直接呼应 Leary & Roberts (2014, The Journal of Finance) 对同行效应工具变量的经典讨论——该文指出同行结果的均值本身很难满足排除约束 (同行均值容易通过未观测的共同冲击渠道而非纯粹的同行传导渠道影响焦点企业结果), 因此转而借助同行特质性收益冲击构造工具。本模块的滞后+leave-out 组合是在数据可得性约束下对这一批评的部分回应, 但剩余的识别假设——"在情感持续性 (sentiment persistence) 的前提下, 同行 t-1 期的特质性报道冲击对焦点银行 t 期结果仅经由同行渠道发生作用, 不存在遗漏的共同冲击渠道"——仍然是一个需要在论文中明确披露、无法被数据本身检验的先验假设。Bramoullé, Djebbari & Fortin (2009, Journal of Econometrics) 进一步从网络计量经济学角度给出了同行效应可识别的结构条件 (网络结构的传递性中断点), 为理解 peer_map 这一离散、二元的同行认定方式如何影响下游同行效应可识别性提供了背景; 需要明确的是, 本家族的 `_70`/`_75`/`_80`/`_85`/`_90` 后缀并不改变 peer_map 的网络稀疏度 (五档结构性逐位相同), Bramoullé et al. 的结构条件讨论应理解为对 peer_map 本身 (相对于其它同行认定方式) 的一般性理论背景, 而非本家族阈值后缀之间的对比框架。

与相邻测度的构念区分上, llm_peer_count 与面板中另一族"Bartik 型" IV (`bartik_*_iv`) 和"LOO 同组均值" IV (`leave_one_out_peer_*_iv`) 分属不同的同行识别原语: LOO 均值 IV 用的是同一类型-年份分组内的算术平均, 不依赖 LLM 查证; Bartik IV 用的是初始暴露份额与后续冲击的交互构造, 同样不经过 LLM 查证环节; 唯有 llm_peer 系列 (`llm_peer_tone_iv_*`/`llm_peer_coverage_iv`/`llm_peer_count*`/`llm_peer_n_effective`/`llm_peer_queried`) 共享同一份 LLM 直接输出的二元同行名单 peer_map。三条同行识别路径在 IV 扩展模块 (`pipeline/panel/iv_extensions.py`) 中并列产出, 服务于"同一因果问题、多套识别策略互证"的稳健性设计思路, 不应互相替代或加总, 各自的有效性依赖各自独立的排除约束论证。

已知局限与稳健性梯子方面, 首先, LLM 直接输出同行名单本身继承生成式模型的不确定性——同一 prompt 版本、同一温度设置下重复查证理论上应给出确定性结果 (本项目以缓存锚点保证跨 run 复现), 但模型本身对银行业务边界的判断可能与人类专家或传统文本网络方法系统性偏离, 这是采用 LLM 直接判定同行相较传统连续相似度网络方法在效度上的固有权衡; Cao et al. (2025) 的研究为此提供了外部效度参照, 但不能保证在中国银行业这一具体情境下的判断质量与其研究样本完全一致。其次, 必须明确披露: `_70`/`_75`/`_80`/`_85`/`_90` 这一族后缀不是一条有识别力的阈值敏感性梯子——源码显式披露该 cutoff 参数是归一化流程中已废弃的 `difflib.get_close_matches` 字符串匹配严格度遗留物, 自 2026-06-11 移除对应兜底策略后已完全惰性, 五档后缀列与 canonical 列结构性逐位相同 (盘上实证 nonnull 数与 mean 全同), 不应被论文正文或表注误引为"证明主结论不被相似度阈值取值驱动"的敏感性检验; 真正对 llm_peer_count 有影响力的设计选择——同行名单上限 (max peers)、单模型 vs 多模型查证、句子/篇章查询口径——目前未在本家族的六列结构中体现, 需要另行扫描才能构成真正的稳健性梯子。第三, llm_peer_count 覆盖全部在册银行而非仅面板内银行, 这意味着高 count 值不必然转化为高 llm_peer_n_effective——两者的比值本身可作为"同行网络在样本框架内的覆盖充分度"诊断, 使用时应同时报告二者以避免读者误判识别强度。

【方法学与计算】

计算链路上, llm_peer_count 的产出发生在 llm_peer_iv.py 内部一个"查证→归一化→计数"的三步流程: 第一步对每个 (bank, year) 调用 LLM 完成同行查证, 要求模型一次性直接返回该银行的二元同行名单 JSON (受 `NEWS_PROCESS_LLM_OFFLINE` 缓存守卫约束, 命中即离线复现、未命中才在线付费查询); 第二步用 `_normalize_peer_names` 对名单中的原始字符串做归一化 (精确匹配→变体映射→唯一子串匹配三策略, 依次尝试, 均未命中则按 OOV 拒绝), 得到该银行在该年份的 peer_map; 第三步取 peer_map 的基数作为 llm_peer_count。历史遗留的 cutoff 参数 (五档后缀 70/75/80/85/90 的由来) 原本作用于归一化流程中已删除的"策略 4"(difflib 模糊匹配兜底), 现行归一化逻辑 (策略 1–3 + OOV 拒绝) 与 cutoff 值完全无关, 因此六档列在代码层面共享完全相同的 peer_map 计算路径, 差异仅体现在列名标签而非任何计算自由度上——这也是为何盘上实证六列结果结构性恒等的直接原因; 六档列名在导出层 (`export.py`) 以列表推导批量生成, 目的是与 `derivative_replication.py::CUTOFF_VARS` 等下游遍历代码的 schema 契约保持一致, 而非承载真实的敏感性检验信息。

【文献定位】

本家族的方法学定位是"生成式 AI 直接识别产品市场/业务同行" (Cao et al. 2025) 与"文本网络产业分类" (Hoberg & Phillips 2016 TNIC 传统, 作为对照参照系而非本模块实现路径) 的交汇点, 计算实现细节 (温度冻结、prompt 版本、缓存复现) 遵循 de Kok (2025) 为会计与金融领域 LLM 文本分析研究总结的操作规范; 其下游用途——服务于同行效应因果识别——则根植于 Manski (1993) 反射问题的经典表述, 并直接回应 Leary & Roberts (2014) 对同行均值 IV 排除约束脆弱性的批评, 辅以 Bramoullé, Djebbari & Fortin (2009) 关于网络结构如何影响同行效应可识别性的结构性讨论。这四条文献脉络共同构成了 llm_peer_count 存在的方法论正当性: 既要证明"用 LLM 直接判定同行归属"这一构造本身站得住脚, 也要正视"同行效应识别"这一更古老的计量经济学难题并给出可披露、可检验的应对策略; 需要如实说明的是, `_70`/`_75`/`_80`/`_85`/`_90` 后缀本身并非上述任一文献脉络所对应的方法论产物, 而是源码中已废弃字符串匹配参数的遗留标签, 不应在文献综述或方法论段落中把这五档后缀包装为与 TNIC 阈值敏感性或 Cao et al. (2025) 相似度打分敏感性可比的检验设计。

## VAR: llm_peer_count

【变体差分】

本列是 llm_peer_count 家族的 canonical 无后缀列。它的值取自 LLM 对该焦点银行、该年份直接查证得到的二元同行名单 JSON, 经 `_normalize_peer_names` (精确匹配→变体映射→唯一子串匹配, OOV 拒绝) 归一化去重后的 peer_map 基数, 单位是纯计数 (整数值, 面板中以 double 类型存储以兼容缺失值编码)。历史上 "_80" 这个数字曾对应归一化流程里一个 `difflib.get_close_matches` 字符串匹配严格度参数 (cutoff=0.80), 但该兜底策略已在 fix omni-g-llm-peer-04 (2026-06-11) 中整体移除, 现行归一化逻辑 (策略 1–3 + OOV 拒绝) 完全不使用任何 cutoff 数值, 因此本列的 "canonical=0.80" 定位并非"某个连续相似度阈值恰好取在中段偏上位置"的研究者选择, 而是源码保留至今的历史命名产物: `export.py` 中把无后缀列映射为最初对应 c=0.80 的历史标签、同时另建一个数值恒等的 `_80` 后缀列以维持下游遍历契约。使用本列时应清楚: 与 `_70`/`_75`/`_80`/`_85`/`_90` 五个后缀列相比, 本列在计算逻辑上不存在任何"门槛更严/更松"的差异, 六列理论上应逐行数值恒等 (五档结构性逐位相同), 不构成、也不应被引用为一条阈值敏感性梯子。本列作为诊断变量, 覆盖全部在册银行 (含未必落在当期 bank-year 面板样本内者), 与真正进入 `llm_peer_tone_iv_full/ctx/ss` 均值计算的有效同行数 (llm_peer_n_effective, 后者额外要求同行在当期面板内且有可用滞后一期语调观测) 是两个不同的口径, 不可互代使用; 解读本列零值或低值时, 应同时参照 llm_peer_queried 以区分"查证后确无同行"与"尚未查证"两种成因, 避免把未查证误读为零同行的实质性结论。

## VAR: llm_peer_count_70

【变体差分】

本列曾在源码历史上对应 `difflib.get_close_matches` 字符串匹配严格度 cutoff=0.70——归一化流程中已废弃的"策略 4"模糊匹配兜底, 用于把 LLM 吐出的、精确/变体/子串三策略都未命中的银行名近似"吸附"到规范名清单, cutoff 越低, 兜底策略吸附成功的概率越高。但 fix omni-g-llm-peer-04 (2026-06-11) 已将该"策略 4"整体移除, 现行归一化只保留策略 1–3 (精确匹配/变体映射/唯一子串匹配) 与 OOV 拒绝, 均不消费任何 cutoff 数值, 因此本列在当前代码路径下与 canonical 列 (以及 `_75`/`_80`/`_85`/`_90` 其余四档) 共享完全相同的 peer_map 计算逻辑, 不产生任何"放宽认定标准、纳入更多同行"的实质差异, 五档后缀列理论上应与 canonical 逐行数值恒等 (盘上实证 nonnull 数与 mean 全同)。因此本列不应被解读或使用为"阈值梯子最宽松臂"、不构成"若放宽同行认定标准结论是否依然稳健"这一方向的敏感性检验工具——那是一条源码明确披露不存在的构念。

保留本列的唯一理由是工程契约: 下游批量遍历代码 (`export.py` 的列表推导批量生成, `derivative_replication.py::CUTOFF_VARS` 的消费循环) 假定 `{70, 75, 80, 85, 90}` 是一个完整的五刻度后缀集合, 若单独剔除 `_70` 会打断这一遍历假设、增加下游代码的特判复杂度。研究者若需要真正有识别力的稳健性维度, 应转向源码披露的其它候选方向——同行名单上限 (max peers)、单模型 vs 多模型 LLM 查证、句子/篇章查询口径——而不是把 `_70` 与 canonical 的数值恒等误当作"梯子两端一致、结论稳健"的证据加以引用, 后者是一种系统性的伪证。

## VAR: llm_peer_count_75

【变体差分】

本列的后缀 "_75" 历史上对应归一化流程已废弃"策略 4" (`difflib.get_close_matches` 字符串模糊匹配兜底) 的严格度参数 cutoff=0.75, 位于历史五档 {0.70, 0.75, 0.80, 0.85, 0.90} 中的第二档。fix omni-g-llm-peer-04 (2026-06-11) 移除该兜底策略后, 现行归一化逻辑 (精确匹配→变体映射→唯一子串匹配, OOV 拒绝) 完全不消费 cutoff 数值, 本列因此与 canonical 及其余四档阈值列在计算路径上完全等价, 共享同一份 peer_map, 不因后缀数字不同而产生任何"同行集合更宽松/更严格"的实质差异。必须明确纠正的一种常见误读是: 把本列理解为"位于最宽松与 canonical 之间的过渡点、用于判断阈值变化是渐进还是存在临界突变"——这套叙事整体建立在"存在连续相似度打分随阈值变化"的错误前提上, 源码从未提供这样一个连续打分矩阵, LLM 直接输出的是离散的二元同行名单, 不存在"c=0.75 与 c=0.70 之间的相似度分布疏密"这一诊断维度。

正确的使用方式是: 若研究者需要引用本列, 应把它理解为 canonical 列的一个数值恒等副本, 仅在 Stata 复现脚本按 {70,75,80,85,90} 完整遍历五档后缀标签的工程场景下使用, 不承载独立的敏感性检验信息, 也不应在正文或附录中把它与其余四档并列呈现为"从宽松到严格的连续走势"。若确需检验 llm_peer_count 类同行认定构造的稳健性, 应转向源码明确披露的其它有效维度 (同行名单上限、单模型 vs 多模型查证、句子/篇章查询口径), 这些维度尚未在本家族的六列结构中体现, 需另行扩展。

## VAR: llm_peer_count_80

【变体差分】

本列在数值上与 canonical 无后缀列 llm_peer_count 完全重复, 但这一恒等不是因为"本列恰好取在阈值梯子中段, 与 canonical 门槛相同"这一单一巧合——真实原因是: 归一化流程已废弃的"策略 4" (`difflib.get_close_matches` 字符串模糊匹配兜底) 中原本存在一个 cutoff 参数, 无后缀 canonical 列历史上映射到该参数的 0.80 取值, 而 fix omni-g-llm-peer-04 (2026-06-11) 移除该兜底策略后, cutoff 参数对全部五档后缀 (含 `_80` 本身) 均已完全惰性, 现行归一化逻辑与 cutoff 值无关。也就是说, `_80` 与 canonical 数值恒等只是"全体六列结构性逐位相同"这一更大事实的一个特例, 而非仅 `_80` 与 canonical 两列独有的巧合——`_70`/`_75`/`_85`/`_90` 同样应与 canonical 逐行恒等。保留 `_80` 这一列的唯一理由是工程契约: `export.py` 以列表推导批量生成五档后缀列, `derivative_replication.py::CUTOFF_VARS` 假定 {70,75,80,85,90} 是完整的五刻度集合, 若因数值重复而单独剔除 `_80` 会打断这一遍历假设。

使用建议: 需要"c=0.80 历史标签口径"的同行计数时, 两列 (无后缀 canonical 与本列 `_80`) 在数值上应当逐行恒等; 回归分析或论文正文优先使用无后缀 canonical 列作为主口径引用对象, 本列仅在需要程序化、统一后缀遍历全部五档 (含 0.80) 的工程场景下作为等价副本使用。切勿把本列的存在解读为"阈值梯子中段锚点、承载中段敏感性信息"——它不承载任何独立于 canonical 的敏感性检验信息, 六列在方法学意义上共享同一个 peer_map, 差异仅体现在历史遗留的列名标签上。

## VAR: llm_peer_count_85

【变体差分】

本列后缀 "_85" 历史上对应归一化流程已废弃"策略 4" (`difflib.get_close_matches` 字符串模糊匹配兜底) 的严格度参数 cutoff=0.85。fix omni-g-llm-peer-04 (2026-06-11) 移除该兜底策略后, 现行归一化只保留策略 1–3 (精确匹配/变体映射/唯一子串匹配) 与 OOV 拒绝, 均不消费 cutoff 数值, 因此本列与 canonical 及其余四档阈值列在计算路径上完全等价, 共享同一份 peer_map, 不因后缀数字更大而产生"同行认定标准更严格"的实质差异。必须明确纠正的一种常见误读是: 把本列理解为"收紧门槛后同行集合基数不高于 canonical、业务同质性更强但样本更薄"——这套叙事整体建立在"存在连续相似度打分随阈值收紧而筛出更严格同行"的错误前提上, 源码从未提供这样一个连续相似度矩阵, 因此不存在"_85 检验收紧标准""_70 检验放宽标准"这样一组方向互补的敏感性问题。

正确的定位是: 本列在方法学意义上是 canonical 列的一个数值恒等副本, 保留原因是 `export.py` 批量生成阈值列标签与 `derivative_replication.py::CUTOFF_VARS` 遍历契约的工程需要, 不承载任何独立于 canonical 的敏感性检验信息, 不应被用来支撑"效率-同质性权衡"或"严格臂/宽松臂三段式呈现"这类具体统计行为主张。若研究者确实需要检验"收紧同行认定标准是否改变结论"这一方向的稳健性问题, 应转向源码明确披露的其它有识别力的维度 (同行名单上限、单模型 vs 多模型查证、句子/篇章查询口径), 这些维度目前未在本家族六列结构中体现。

## VAR: llm_peer_count_90

【变体差分】

本列后缀 "_90" 历史上对应归一化流程已废弃"策略 4" (`difflib.get_close_matches` 字符串模糊匹配兜底) 的严格度参数 cutoff=0.90, 是历史五档中数值最高的一档。fix omni-g-llm-peer-04 (2026-06-11) 移除该兜底策略后, 现行归一化逻辑 (精确匹配→变体映射→唯一子串匹配, OOV 拒绝) 完全不消费 cutoff 数值, 本列因此在计算路径上与 canonical 及其余四档阈值列完全等价, 共享同一份 peer_map, 不因后缀数字最大而产生"门槛最严、同行集合基数最小"的实质差异。必须明确纠正的一种常见误读是: 把本列理解为"阈值梯子最保守口径, 仅纳入相似度极高的严格同行, 适合极端稳健性检验"——这套叙事整体建立在"存在连续相似度打分、阈值越高筛出的同行越少"的错误前提上, 源码从未提供这样一个连续相似度矩阵, LLM 输出的是离散二元同行名单, 不存在"阈值梯子严格端"这一构念。

正确的定位是: 本列在方法学意义上是 canonical 列的一个数值恒等副本, 保留原因是 `export.py` 批量生成阈值列标签、`derivative_replication.py::CUTOFF_VARS` 遍历契约等工程需要, 不承载独立于 canonical 的敏感性检验信息, 不应被用来支撑"梯子两端方向一致即证明结论不依赖同行认定严格程度"或"严格门槛下一阶段 F 统计量更脆弱"这类具体统计行为主张——这些主张预设了一个实际不存在的连续阈值机制。若研究者确实需要检验同行认定构造本身的稳健性, 应转向源码明确披露的其它有识别力的维度 (同行名单上限、单模型 vs 多模型查证、句子/篇章查询口径), 这些维度目前未在本家族六列结构中体现, 需另行扩展并单独校验其识别力。

<!-- rendered-citations:begin -->
Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can generative AI help identify peer firms? Review of Accounting Studies, 30(4), 3344-3386. https://doi.org/10.1007/s11142-025-09892-6
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Jochmans, K. (2023). Peer effects and endogenous social interactions. Journal of Econometrics. https://doi.org/10.1016/j.jeconom.2022.10.004
Kuersteiner, G. M., Prucha, I. R., & Zeng, Y. (2023). Efficient peer effects estimators with group effects. Journal of Econometrics. https://doi.org/10.1016/j.jeconom.2023.02.013
<!-- rendered-citations:end -->
