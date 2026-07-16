---
family_id: F581
columns:
- tone_homecity_media_ctx
- tone_homecity_media_full
- tone_homecity_media_ss
unit: 语调得分 (连续, 理论区间约 [-1,1]; article 级三轨情感度量聚合到 bank-year 面板均值)
formula: 'tone_homecity_media_{trk} = mean(article_tone_{trk} | outlet_city == bank_homecity, year, bank), trk∈{full,ctx,ss}; 本地媒体子样本口径, 分子分母均限定在总部同城媒体子集内, 与 homecity_media_frac (总部同城媒体报道占比) 是姊妹但不同构念的两个量'
producer: pipeline\panel\attention_media.py
upstream:
- pipeline/panel/attention_media.py
- pipeline/sentiment/tone_llms.py
- pipeline/text/ctx_materializer.py
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: 'Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy'
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
`tone_homecity_media_{full,ctx,ss}` 度量的是"银行总部所在城市的本地媒体, 在其对该银行的全部报道中所流露的平均语调", 属地理邻近性维度⑨ (Gurun & Butler 2012, JF) 项下的语调子测度, 与该维度另外两个姊妹家族——`homecity_media_frac` (总部同城媒体报道量占该银行全部报道的比例, 度量的是"多少") 与 `tone_gap_homecity_noncity_full` (同城媒体语调减去异地媒体语调之差, 度量的是"落差")——共同构成一个三角: 前者度量本地媒体的注意力份额, 本家族度量本地媒体自身的情感倾向水平, 后者度量本地相对异地的情感落差。三者中只有本家族是"绝对水平"量, 后两者是"占比"或"相对差"量, 三者不可互相替代, 在回归设定里也不应同时作为同一构念的多重代理变量塞进同一右手边——它们各自承载不同的经济含义 (注意力集中度、情感水平、情感偏向), 混用会导致系数解读混乱。构念动机源于本地新闻业理论: 地方性银行的经营信息 (网点动态、地方监管互动、地方性负面事件如挤兑传闻或分支行诉讼) 更容易被总部所在城市的媒体首先捕获、深度追踪, 而这些本地媒体同时也更可能与地方政府、地方广告商存在利益纠葛 (Gurun & Butler 2012 的"local advertising, local media slant" 机制), 因而本地语调既可能反映信息优势 (本地记者更了解实情), 也可能反映软约束 (本地媒体倾向于为本地企业说好话, 或反过来因竞争关系刻意苛责)。这正是为什么本家族被设计为与 `tone_gap_homecity_noncity_full` 并列而非相互替代: 若只看绝对水平, 无法区分"本地媒体整体乐观"是行业景气驱动还是本地偏向驱动; 引入异地媒体作为对照组之后, 落差项才能部分剥离掉行业共同冲击。数据来源上, 本家族参与聚合求均值的文章级打分列是 `llm_vote_score{trk}` (三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票产出的连续语调打分, 与用于门控/分类展示的标签列 `llm_vote_tone_{trk}` 是同一情感体系下的两个不同列——前者是可直接取 groupby 均值的连续数值, 后者是分类语调标签, 本家族真正参与聚合运算的是前者), 城市归属判据来自 `pipeline/panel/attention_media.py::compute_media_heterogeneity` 内对媒体来源 outlet 所在城市字段与银行总部城市字段做字符串精确清洗匹配后产出的布尔列 `_is_homecity` (同城=1/异城=0), 二者在面板导出阶段的该函数内按 (target_bank, year) 分组、限定在 `_is_homecity==1` 的子样本内对 `llm_vote_score{trk}` 求均值。

【方法学与计算】
计算分两步。第一步是文章级情感打分, 与家族无关的上游共享: stage 21 `tone_llms.py` 对每篇通过留篇门控 (`llm_verified_full == True`, full-only 口径, 2026-06-29 起生效) 的报道产出三轨 (full/ctx/ss) 语调分, full 轨用标题+全文正文, ctx 轨用标题+实体窗口截取正文, ss 轨用标题+银行∧金科同句±N窗截取正文 (无同句共现则回退为全文 body 并置 `ss_is_fallback=True`, 语义上镜像 ctx 轨的回退规则)。第二步是同城子样本聚合: `pipeline/panel/attention_media.py::compute_media_heterogeneity` 先给每篇文章打上"该篇报道的发布媒体所在城市是否等于该篇报道所指银行的总部城市"的二元标签 `_is_homecity` (经字符串清洗后的精确匹配), 再按 (target_bank, 年份) 分组, 仅在该标签为真的子集内对 `llm_vote_score{trk}` 取均值, 得到 `tone_homecity_media_{trk}`; 面板导出模块 `pipeline/panel/export.py` 在此列产出后只承担中英文标签映射工作, 不参与该聚合计算本身。三轨 (full/ctx/ss) 各自独立完成上述两步, 各自 just-identified 并排, 互为稳健性、不分主次, 禁止把三轨混进同一个 over-identified 的 Hansen J 检验框架。样本量上须注意: 该指标的有效性依赖于"该银行-年份是否存在足够数量的同城媒体报道"这一分母条件, 若某银行总部城市当年无本地媒体报道该行, 则该 (bank, year) 单元的本家族三列均应为缺失 (NaN), 而非 0——0 与"无本地报道"在经济含义上完全不同 (0 表示本地媒体报道但语调恰好中性, NaN 表示无本地样本可算)。留篇门控是 full-only 口径: 一篇报道是否被计入"银行×金科"报道体系, 只由 `llm_verified_full` 决定; ctx/ss 轨道的行宇宙是 full 留篇集合的子集, 在此子集之上各轨再各自计算其语调打分与城市归属聚合, 而非独立门控。

【文献定位】
本家族方法学谱系直接承袭 Gurun & Butler (2012, *The Journal of Finance*) 关于"本地媒体倾向 (local media slant)" 的经典设计——该文首次系统性证明本地报纸对本地上市公司的报道语气显著更正面, 且这种偏向与本地广告收入依赖度正相关, 为地理邻近性会系统性扭曲媒体语调这一命题提供了因果层面的实证基础, 是本家族"同城 vs 异城"划分逻辑的直接理论来源。语调本身的测度传统则追溯到 Tetlock (2007, *The Journal of Finance*) 对"媒体语调赋予投资者情绪以实质内容"的开创性论证, 确立了将新闻文本转化为可用于资产定价与公司金融研究的连续情感量表这一方法论范式, 本家族的语调打分虽由 LLM 而非词典产生, 但延续的正是这一"文本→情感标量→经济结果"的测量哲学。在中国银行业情境下, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 的研究提供了最直接的同域参照: 该文考察媒体情感如何通过影响存款人信心传导为银行系统性风险, 其分析单元同为中国银行-年面板, 与本项目的银行×金科新闻情感面板在数据结构上高度可比, 佐证了在中国银行业场景下本地媒体语调这一构念的可操作性与解释力。方法工具层面, Marchetti, Tarducci & Branzoli (2025, SSRN) 提出的银行×年语气聚合口径与本家族"文章级打分→(bank,year)子样本均值"的两步聚合方式相互印证, 说明这一简单平均聚合并非本项目独有的临时处理, 而是文献中处理银行-媒体语调面板数据的常见做法。

## VAR: tone_homecity_media_ctx

【变体差分】
`_ctx` 是三轨中的语境窗口轨: 上游文章级语调来自 stage 21 对 `content_ctx` (标题+实体窗口截取正文, 而非全文) 的 LLM 打分, 其余聚合逻辑 (按 (bank, year) 分组、仅在同城子样本内求均值、无本地样本则缺失) 与 `_full` 完全一致。与 `_full` 相比, `_ctx` 的信息输入更聚焦于银行实体周边的局部语境, 剔除了报道正文中与该银行不直接相关的段落, 因而更能反映"文章中直接涉及该银行的那部分内容的语调", 而非全文整体基调 (全文可能包含大段行业背景、宏观政策叙述等与银行本身情感无直接关系的内容)。行宇宙上, `_ctx` 的样本行是 full 轨留篇门控 (`llm_verified_full == True`) 结果集合的子集——是否计入"一篇银行×金科报道"这一判定完全由 full 轨完成, `_ctx` 只在此基础上重新打分与聚合, 属于 conditional-on-full 的测度/稳健性轨, 而非独立门控产生的另一套样本。经济解读上, `_ctx` 与 `_full`、`_ss` 三者互为稳健性、不分主次, 各自 just-identified, 三者数值若系统性偏离, 提示该银行相关报道中"局部涉行文字"与"全文整体基调"存在张力 (例如全文标题耸动但涉行段落本身克制), 这本身即是有信息量的诊断; 但在计量设定中三轨绝不可混入同一个 over-identified 的 Hansen J 过度识别检验框架内联合使用。

## VAR: tone_homecity_media_full

【变体差分】
`_full` 是三轨中的规范 (canonical) 轨、也是家族的默认基准: 上游文章级语调来自 stage 21 对 `content_full` (标题+完整正文, 无截取) 的 LLM 三家投票多数共识打分, 是否纳入"银行×金科报道"体系的留篇门控 (`llm_verified_full == True`, full-only 口径) 直接在本轨完成判定, ctx/ss 两轨的行宇宙均以本轨的留篇结果为基础子集。相比 `_ctx`/`_ss`, `_full` 使用报道全文作为语调打分的输入文本, 语调分数反映的是文章整体基调 (包括标题、导语、正文全部段落), 不做任何窗口截取或句子级筛选, 因而最贴近"一篇报道读者读完全文后的总体印象"这一直觉构念。作为家族默认轨, `_full` 是各下游 paper 模块 (如 P1 `bank_fintech_tone`) 在处理变量设计中优先采用的口径 (P1 主轨 `llm_vote_tone_full`), 但这不改变三轨"互为稳健性、不分主次"的铁律定位——`_full` 只是文献沿用最广、最贴合直觉的基准点, 而非在统计意义上优于 `_ctx`/`_ss` 的"真值"。聚合口径与另外两轨相同: 按 (银行, 年份) 分组, 仅在总部同城媒体报道子集内取语调均值, 无本地样本则本单元缺失。使用者须留意一个常见误读: `_full` 作为默认基准并不意味着它比 `_ctx`/`_ss` 更"准确", 三者只是对"语调"这一构念采用了不同的文本窗口口径, 各自捕获的信息侧重不同——`_full` 捕获全文整体基调 (含大量与银行本身无直接关系的背景叙述), `_ctx`/`_ss` 则分别捕获实体窗口与同句共现窗口内的局部语调。在稳健性检验或规格曲线分析中, 应将三轨结果并列报告, 而非把 `_full` 当作单一"真值"、其余两轨仅作为附属检验, 这一点与家族内另外两个地理邻近性姊妹测度 (`homecity_media_frac`、`tone_gap_homecity_noncity_full`) 在设计哲学上是一致的: 每个测度都各自 just-identified, 共同拼出银行与其总部所在城市媒体生态之间关系的多面图景。

## VAR: tone_homecity_media_ss

【变体差分】
`_ss` 是三轨中的严格同句共现轨: 上游文章级语调来自 stage 21 对 `content_ss` (标题+"银行"与"金科"关键词落在同一句子±N窗内的片段, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认1) 的 LLM 打分。若某篇报道内银行实体与金科实体从未在同一句子的邻近窗口内共现, 则该篇的 `content_ss` 回退为全文 body、`ss_is_fallback` 置为 True——这一回退语义严格镜像 `_ctx` 轨的回退规则 (无实体窗口可截取时同样回退全文), 二者共享同一套"缺构造条件即优雅降级为全文, 而非丢弃该行"的设计哲学, 保证 `n_articles` 分母口径在三轨间一致、不产生单边孤儿行。行宇宙同样是 full 轨留篇门控结果集合的子集, `_ss` 只是在该子集之上采用最严格的"同句局部证据"重新打分与聚合。经济含义上, `_ss` 相比 `_ctx` 进一步收窄了输入文本的语境范围, 只保留银行与金科词汇真正紧邻出现的句子片段, 因而对"该报道是否在实质性讨论银行与金科的互动关系"这一构念最为敏感, 但也因样本窗口更窄, 在回退触发率较高的银行-年份单元上退化为接近 `_full` 的度量, dev 样本 (T=2) 上因语料稀薄, `_ss` 与 `_full`/`_ctx` 之间的方差区分度可能较弱, 属预期的小样本退化而非构造缺陷, 生产语料 (T=19, 约 1,819 万条) 规模下三轨区分度应显著回升。三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
<!-- rendered-citations:end -->
</content>
