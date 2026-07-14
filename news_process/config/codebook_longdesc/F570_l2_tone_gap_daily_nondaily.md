---
family_id: F570
columns:
- tone_gap_daily_nondaily_ctx
- tone_gap_daily_nondaily_full
- tone_gap_daily_nondaily_ss
unit: 语调缺口 (连续, 两组情感均值之差; 理论范围约 [-2,2], 实务集中于 [-1,1]; bank-year 面板列)
formula: 'tone_gap_daily_nondaily{track} = mean(llm_vote_score{track} | is_daily=1) - mean(llm_vote_score{track} | is_daily=0), 分组均值均在 (target_bank, year) 单元内先算, 再作差'
producer: pipeline\panel\attention_media.py (维度⑧ 高频日报 vs 非日报, 三轨循环) ; pipeline\panel\export.py (标签映射)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track} 三家 LLM 多数投票语调分)
- config/bank_addresses.json 相邻维度使用同一 df['媒体(中文)'] 列, 本家族直接消费 DAILY 出版周期名单
- 14_materialize_ctx.parquet (content_ctx / content_ss 三轨文本物化, 供 stage 21 三轨情感产出)
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
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
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
本家族衡量同一银行-年度单元内, 高频日报媒体报道语调与非日报媒体报道语调之间的系统性落差, 属于「媒体来源异质性」测度簇下的第⑧维度 (出版频率异质性), 与本簇内的官方/市场媒体缺口、深度/非深度期刊缺口、央地媒体缺口构念平行、生成逻辑同构。构念动因来自新闻传播学与金融文本分析交叉领域的一个稳定经验事实: 出版周期不同的媒体在信息生产的时效压力、编辑筛选强度、受众定位上系统不同, 日报因高频出版必须持续追踪突发与常规经营动态, 报道节奏贴近事件本身; 非日报 (周刊/半月刊/深度期刊等) 则有更长的采编与核实周期, 倾向于事后综合评述或深度调查, 语调形成机制与日报存在结构性差异。若二者语调系统性偏离, 意味着银行的媒体情感画像对「所选媒体出版频率」敏感, 进而影响任何以媒体语调作为银行声誉/风险代理变量的推断稳健性。生产者代码在 `pipeline/panel/attention_media.py` 维度⑧注释中直接援引 Tetlock (2007, Journal of Finance) 关于道琼斯《华尔街日报》"Abreast of the Market"专栏悲观度指数可预测市场收益率的经典发现, 支撑「日频媒体语调具有独立信息含量、值得与非日频语调分离度量」这一构念设计选择。

本列所在的 `tone_gap_daily_nondaily{track}` 由两条并列分支合成: 先在原始文章级数据 `df` 上依据 `媒体(中文)` 列是否命中 `DAILY` (基于 NPPA 备案出版周期为"日报"的出版物集合) 生成布尔标记 `_is_daily`, 再按 `(target_bank, year)` 分组、按 `_is_daily` 取值再分组, 分别取 `llm_vote_score{track}` (三家 LLM——`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`——多数投票共识语调分) 的组内均值, 生成中间列 `tone_daily_media{track}` 与 `tone_nondaily_media{track}`; 二者相减即得本家族三个成员列。数据来源上, 语调分本身产自 stage 21 情感 LLM 阶段, 出版频率标签则来自外部媒体名录静态匹配 (与内容无关的元数据特征), 两条信息流在 panel 构建阶段 (`attention_media.py`) 于 bank-year 粒度汇合。

【方法学与计算】
计算严格遵循「先分组求均值、再作差」的顺序, 而非先逐篇求差再聚合, 这保证了 gap 的分母 (各组内文章篇数) 相互独立、不因某一子组样本稀疏而放大噪声; 若某银行-年度单元内某一子组 (日报或非日报) 无任何报道命中, 对应中间列取 `NaN`, merge 后落入面板即为缺失, 本列同样传播为 `NaN` (非 0), 避免把"该类型媒体零覆盖"误读为"零语调差异"。三轨循环 (`for track in ['_full', '_ctx', '_ss']`) 在源码中显式带有防御性判断: 若某轨道对应的 `llm_vote_score{track}` 源列在文章级数据框缺失 (例如 `_ss` 轨在两侧文本均无同句共现、降级为全文回退语义, 或该轨情感未产出), 该轨整体跳过, 不制造半截列; 因此三个成员列在跨轨上不存在互相借补, 均为各轨独立管线产出。语调分 `llm_vote_score{track}` 本身是三家 LLM 对同一篇文章-轨道文本给出情感判断后的多数投票共识分, 值域理论上落在 [-1,1] (负面/中性/正面三分类映射的连续化处理), 因此两组均值之差理论范围约 [-2,2], 但由于日报与非日报报道量在多数银行-年度上都非零且语调分布重叠度高, 实务观测值通常收缩在更窄区间。

出版频率标签的判据是静态、外生于文本内容的媒体属性 (类似官方/市场媒体二分、深度/非深度期刊二分), 与本条条目下方相邻的 `tone_gap_official_nonoff`、`tone_gap_market_nonmkt`、`tone_gap_deepdive_nondeep` 等家族共享同一段生产代码框架与 `panel.merge` 拼接顺序, 只是分组判据 (`_is_daily` vs `_is_official` 等) 不同, 体现媒体异质性测度簇"同一构造范式、不同切分维度"的设计哲学。

【文献定位】
本家族的方法学根基直接呼应文本情感测度中「媒体属性异质性驱动语调系统性差异」这一支文献。奠基性证据来自 Tetlock (2007, Journal of Finance) 关于媒体悲观语调的市场信息含量研究, 以及后续 Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体权威性对语调"信息纪律"作用的机制分析——后者是 `pipeline/panel/geography.py` 中媒体权威加权语调 (`llm_vote_tone_mw{track}`) 一族的直接理论锚 (该文献援引锚点位于 `geography.py` 内, 与本家族所在的 `attention_media.py` 是面板构建阶段的两个不同生产模块, 但共享同一媒体来源异质性建模思路), 二者共同说明媒体来源属性 (无论是出版频率还是权威性/官方性) 都不是语调测量的中性背景, 而是需要显式建模的调节变量。You, Zhang & Zhang (2018, The Review of Financial Studies) 关于中国语境下媒体话语权分布 ("谁掌握了笔杆子") 的研究进一步支撑了在中国银行-媒体报道场景中拆分媒体来源异质性的必要性, 该文亦被生产代码在相邻媒体来源占比列的标签中直接援引 (`Official Media Share (You 2018)`)。国内同域证据方面, Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 针对中国银行媒体情感与存款稳定性、系统性风险的实证研究提供了银行-年度层面媒体语调测度的可比先例, 佐证本家族聚合粒度 (bank-year) 与被解释对象 (中国上市银行) 的适配性。

【梯子与并排口径】
本家族三个成员列对应 CLAUDE.md 铁律中的「三轨 full/ctx/ss」结构: `_full` 以标题+全文正文为情感输入文本, `_ctx` 以标题+银行/金科实体窗口为输入, `_ss` 以标题+银行与金科词同句 (±N 窗口, 默认 N=1) 共现片段为输入, 三者共用同一套「日报 vs 非日报」出版频率分组判据, 仅情感输入文本轨道不同。三轨之间是各自 just-identified 并排关系, 互为稳健性、不分主次, 严格禁止把三轨语调缺口列混进同一 over-identified 的 Hansen J 检验; 下游研究设计中应将三轨分别作为独立的稳健性对照臂使用, 而非取平均或联合矩条件。`_ss` 轨遵循与 `_ctx` 镜像的回退语义: 当某篇文章不存在银行与金科关键词同句共现时, 该文章的 `content_ss` 回退为全文 body (`ss_is_fallback=True`), 情感三家投票在回退场景下与 `_ctx`/`_full` 使用相同的兜底策略, 但仍作为独立轨道参与本家族的分组均值计算, 不与 `_full`/`_ctx` 的样本行借补。此外, 本家族的分组变量 `_is_daily` 与情感留篇门控 (2026-06-29 起 full-only, 即"是否算作一篇有效银行-金科报道"仅看 `llm_vote_score_full` 所在文章是否通过 full 轨验证) 是两条独立逻辑: 出版频率分组作用于已通过留篇门控的样本集合之上, 三轨语调分则各自在该样本集合的子集 (per-track 有效样本) 上计算, 不因某轨语调缺失而剔除该文章在其余轨的贡献。

## VAR: tone_gap_daily_nondaily_ctx

【变体差分】
本列是「日报-非日报语调缺口」家族在 `_ctx` (上下文窗口) 轨道上的产出。`_ctx` 轨的情感输入文本为标题拼接银行/金科实体窗口 (而非全文), 由 stage 14 `ctx_materializer` 在文章级预先物化出 `content_ctx` 列并附带 `ctx_is_fallback` 标记 (若某篇文章无法定位出有效实体窗口, 回退为全文, 该标记置 True)。`llm_vote_score_ctx` 因此度量的是"聚焦实体上下文片段"的情感倾向, 相较 `_full` 轨剔除了正文中与目标银行、金科话题无关的背景段落对语调判断的稀释效应, 理论上应更精准地捕捉媒体对"该银行的金科相关议题"本身的态度, 而非全文通篇语气。分组变量 `_is_daily` 与 `_full`/`_ss` 两轨完全相同 (均来自 `媒体(中文)` 静态名录匹配), 唯一差异点是被分组求均值的语调分来源轨道。留篇门控为 full-only 口径 (仅看 `llm_vote_score_full` 对应文章是否验证通过), `_ctx` 轨此处降级为「conditional-on-full」的测度/稳健性轨: 其行宇宙是 full 留篇集合的子集, 但组内均值计算 (日报组、非日报组) 仍按 `_ctx` 轨自身可用的语调分独立进行, 不借用 `_full` 轨的分组结果。作为家族内三个并排轨之一, 本列应与 `_full`、`_ss` 两列在实证使用中作为互为稳健性的独立臂对待, 不应与它们混入同一 over-identified 矩条件估计。

## VAR: tone_gap_daily_nondaily_full

【变体差分】
本列是「日报-非日报语调缺口」家族在 `_full` (全文) 轨道上的产出, 也是三轨中的 canonical / 主测度口径 (对应 P1 论文 `bank_fintech_tone` 的处理变量主轨 `treatment.primary` 所依赖的 full-only 情感留篇口径)。`_full` 轨的情感输入文本为标题拼接文章全文正文 (`content_full = prepend_title(标题, 原始"内容"列)`), 不做实体窗口裁剪, 因此语调分反映的是整篇报道 (含背景铺陈、行业综述、人物访谈等一切段落) 的综合情感倾向。留篇门控铁律明确: 一篇文章是否计入"银行金科报道"样本, 仅取决于 `llm_vote_score_full` 所在的验证结果 (`llm_verified_full == True`), 因此本列所依赖的日报组/非日报组均值, 其分母样本正是官方留篇口径下的完整有效样本, 不存在 `_ctx`/`_ss` 那样的"子集降级"问题。分组判据 `_is_daily` 与另两轨相同, 均来自静态出版周期名录匹配, 与内容语义无关。尽管本列在留篇门控上处于"主口径"地位, 但在语调缺口测度本身的构念意义上, 三轨依然是并排的互为稳健性关系而非层级关系——即本列不因门控主轨地位而被赋予额外统计权重, 三轨证据应共同报告、共同作为构念效度证据链的一部分, 严禁将三轨语调缺口列混入同一 over-identified Hansen J 矩条件估计。

## VAR: tone_gap_daily_nondaily_ss

【变体差分】
本列是「日报-非日报语调缺口」家族在 `_ss` (同句共现) 轨道上的产出, 三轨中判据最严格的一支。`_ss` 轨的情感输入文本 `content_ss` 要求标题拼接"银行实体与金科关键词落在同一句子内、允许 ±N (默认 N=1) 句窗口"的片段, 判据原语与 stage 13 共现硬过滤所用的邻近共现判据 (`entity_context.py::has_bank_fintech_cooccurrence_within_radius`) 口径不同、不可互相复用: `_ss` 轨要求的是严格同句级共现抽取, 用于决定"喂给情感模型的文本片段", 而 stage 13 的邻近共现窗口判据用于决定"该文章是否进入样本"的硬过滤。当某篇文章不存在这种严格同句共现时, 依据镜像 `_ctx` 的回退语义, `content_ss` 整体回退为全文 body、`ss_is_fallback` 标记为 True, 此时该文章在 `_ss` 轨的情感输入与 `_full` 轨趋同 (但仍走独立的 LLM 调用与独立缓存键, 二者不因输入文本巧合相同而在计算流程上等价)。分组变量 `_is_daily` 与另两轨完全一致。与 `_ctx` 轨相同, `_ss` 轨在 full-only 留篇门控下也是「conditional-on-full」的稳健性测度, 行宇宙为 full 留篇集合的子集, 分组均值在该子集内按 `_ss` 轨自身可用样本独立计算。本列与 `_full`、`_ctx` 两列同样是并排的互为稳健性关系, 三者各自 just-identified, 严禁混入同一 over-identified Hansen J 矩条件估计; 在 `_ss` 轨语调缺口接近零方差或与 `_full`/`_ctx` 明显偏离的场景 (尤其在样本量较小的开发期面板上), 应优先诊断是否为回退比例过高导致的统计退化, 而非直接判定构念失效。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
</content>
