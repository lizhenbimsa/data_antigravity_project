---
family_id: F575
columns:
- tone_gap_homeprov_nonprov_ctx
- tone_gap_homeprov_nonprov_full
- tone_gap_homeprov_nonprov_ss
unit: 语调差值 (连续, 理论域约 [-2,2], 实践中集中在 [-1,1]; bank-year 面板行, 由文章级三家 LLM 投票共识语调聚合后作差)
formula: 'tone_gap_homeprov_nonprov_{trk} = tone_homeprov_media_{trk} − tone_nonprov_media_{trk}; 其中 tone_homeprov_media_{trk} = 该银行-年度、总部所在省份媒体子集报道文章的 llm_vote_score_{trk} (文章级三家 LLM 投票共识三元语调分, ∈{-1,0,1}) 均值, tone_nonprov_media_{trk} = 非该省媒体子集报道文章的同一文章级测度均值; 银行总部省份取自银行主体地理标识字典 (config/bank_list.yaml 及地理六键匹配), 媒体所属省份取自媒体来源元数据; 分省判定、子集均值计算与三轨切分均在 attention_media.py 地理异质性维度⑨模块内完成 (`src_tone = llm_vote_score{trk}`, 逐银行-年度 groupby mean), 面板导出标签由 export.py 统一注入; 家族名中 llm_vote_tone_{trk} 是 encode.py 已完成的 bank-year 级全样本(不分省份子集)聚合列, 与本族"省份子集内取均值"操作在颗粒度上不同源, 不应混同'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms
- 40_panel_export_main
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., Wu, Y.
  year: 2018
  title: Media Bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: 'The Media and the Diffusion of Information in Financial Markets: Evidence
    from Newspaper Strikes'
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from
    China'
  venue: International Review of Economics & Finance
  vol: '91'
  issue: ''
  pages_or_artno: 1150-1172
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., Ren, P.
  year: 2024
  title: Is the tone of the government-controlled media valuable for capital market?
    Evidence from China's new energy industry
  venue: Energy Policy
  vol: '184'
  issue: ''
  pages_or_artno: '113917'
- doi: "10.1016/j.frl.2024.105024"
  type: "journal"
  authors: "Huang, W., Liu, J., & Zhang, R.-Z. (."
  year: 2024
  title: "Local newspaper closures and non-GAAP reporting quality"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105024"
- doi: "10.1111/1911-3846.12935"
  type: "journal"
  authors: "Huang, Y., Li, F., Li, T., & Lin, T."
  year: 2024
  title: "Local information advantage and stock returns: Evidence from social media"
  venue: "Contemporary Accounting Research"
  vol: "41"
  issue: "2"
  pages_or_artno: "1089-1119"
- doi: "10.1111/irfi.70009"
  type: "journal"
  authors: "Chen, H., Chen, Y., & Li, D."
  year: 2025
  title: "Local bias under natural disasters"
  venue: "International Review of Finance"
  vol: "25"
  issue: "1"
  pages_or_artno: "e70009"
new_dois: []
---

## CORE

【构念与来源】
`tone_gap_homeprov_nonprov` 族刻画的是同一家银行在同一年度里, 「本埠/本省媒体」与「异地/非本省媒体」在语调评价上的系统性落差, 是地理邻近性—媒体偏向 (media slant) 文献中「本地偏袒」(home bias / local favoritism) 假说在中国银行业情境下的直接实证化。构念来源可追溯至地方性媒体因归属地关系、广告依赖、政企联系而对辖区内企业/机构呈现更正面 (或更少负面) 的报道倾向这一经典发现 (You, Zhang & Zhang 2018, *The Review of Financial Studies*, 研究中国分析师"谁掌权笔"揭示地方媒体的信息把关人角色; Qin, Strömberg & Wu 2018, *American Economic Review*, 系统刻画中国媒体在政治敏感议题上因归属地和审查压力产生的系统性偏向)。在本项目语境下, 该族属于 `attention_media.py` 地理异质性九维度模块中的第⑨维 (Gurun & Butler 2012 式本地媒体研究在银行业媒体语境下的中国化落地), 与 `tone_gap_homecity_noncity_*`(同城/非同城口径, 比省份更细的地理粒度)、`tone_gap_fin_other_*`(财经/其他媒体类型口径)、`tone_gap_central_local_*`(中央级/地方级口径)、`tone_gap_official_nonoff_*`(官方/非官方口径) 等并列, 共同构成 `bank_media_disagreement` 论文的核心 TREATMENT 变量族: 这些 gap 并非噪声, 而是媒体分歧本身的测度对象。gap>0 表示本省媒体相对更正面地报道该行, gap<0 表示本省媒体反而更负面 (例如舆论监督/属地问责压力更大时可能出现的"家丑外扬")。该差值变量的构念定位与地方政府隐性担保、属地监管俘获、地方国资持股关联等银行治理文献的关注点高度契合: 若本省媒体系统性更正面, 是本地信息优势 (熟悉度更高、报道更细致) 还是本地利益捆绑 (审查/广告/关系网络) 所致, 是该测度族本身无法单独回答、须结合外部工具变量或准实验设计进一步甄别的开放问题, 这也是本族被定位为 provisional 论文 `bank_media_disagreement` 分析对象而非某主线论文核心 DV 的原因。

【方法学与计算】
计算分两步。第一步 (媒体归属分省): 对每篇通过 stage 13 共现硬过滤、且在 stage 21 情感 LLM 三家投票下 `llm_verified_full == True` 的报道, 依据其发布媒体的地理元数据判定该媒体是否属于目标银行总部所在省份; 银行总部省份取自 `config/bank_list.yaml` 及配套地理六键匹配字典 (银行实体地理标识主清单), 与媒体来源省份做严格字符串/编码匹配, 无法解析的媒体地理归属按缺失处理、不强行归入任一子集。第二步 (子集内均值作差): 在 bank-year 单元格内, 对「本省媒体子集」与「非本省媒体子集」分别取该银行当年被这些媒体报道文章的 `llm_vote_score_{trk}` (文章级三家 LLM gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash 多数投票共识三元语调分, ∈{-1,0,1}, 见 CLAUDE.md「LLM 三家 / BERT 三模型互为稳健性」条) 简单算术平均, 得到 `tone_homeprov_media_{trk}` 与 `tone_nonprov_media_{trk}` 两个中间列 (均已单独落盘为面板列, 供研究者直接比较水平值), 再取二者之差即为本族 `tone_gap_homeprov_nonprov_{trk}`。需特别澄清的是, 面板中已存在的 bank-year 级聚合列 `llm_vote_tone_{trk}` (由 encode.py 对该银行-年度全部留篇文章、不分省份子集地取 `llm_vote_score_{trk}` 均值得到) 与本族两个中间列不是同一操作的产物: `llm_vote_tone_{trk}` 本身已经是聚合完成的 bank-year 单值, 不具备可供二次按省份子集切分再平均的文章级颗粒度; 本族真正消费的是聚合之前的文章级 `llm_vote_score_{trk}`, 按省份子集分别聚合, 因此 `tone_homeprov_media_{trk}` + `tone_nonprov_media_{trk}` 并不满足以文章数加权后等于 `llm_vote_tone_{trk}` 的简单可加关系 (二者分母口径不同: 前者是省份子集内文章数, 后者是银行-年度全部文章数)。当某一子集在该银行-年度内报道篇数为零时, 对应中间均值为缺失, gap 亦随之置缺失 (不做插补, 不借用另一子集或另一年度的值)。三轨 `_full`/`_ctx`/`_ss` 分别对应家族铁律定义的三种正文口径 (full=标题+全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗); 三轨的 gap 计算逻辑完全一致, 唯一差异是喂入的文章级 `llm_vote_score` 取自哪一轨的情感测度。三轨之间是各自独立、并排的稳健性口径, 而非嵌套或主副关系: full 轨对应留篇门控口径 (2026-06-29 起, `llm_verified_full == True` 是"是否算一篇银行金科报道"的唯一判据), ctx/ss 轨的行宇宙是 full 留篇集的子集、按各自轨的语调值重算, 三者禁止混入同一 over-identified 的 Hansen J 检验, 只能作为互为稳健性、不分主次的并排规格出现在同一研究设计里。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行与金科词的严格同句共现, 则该文章的 `content_ss` 回退为全文正文、`ss_is_fallback` 置真, 但该文章依然计入 ss 轨的语调聚合分母, 不因回退而被排除出本族的省份子集划分。

【文献定位】
本族方法学谱系有两条主线交汇。其一是媒体分歧/媒体偏向的实证测度传统: Peress (2014, *Journal of Finance*) 以报社罢工的准实验证明媒体信息扩散对资产定价的因果作用, 隐含媒体覆盖强度与来源结构本身携带可识别信息; You, Zhang & Zhang (2018, *The Review of Financial Studies*) 与 Qin, Strömberg & Wu (2018, *American Economic Review*) 则直接刻画了中国媒体因政治/地方联系产生的系统性报道偏向, 是本族「省份归属→语调系统性差异」这一构念假设的直接理论支撑。其二是中国银行业媒体情感的应用先例: Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 以媒体情感研究中国银行存款稳定性与系统性风险, 是与本项目样本单位(中国银行)、测度对象(媒体语调)最贴近的同域实证参照; Xu, Li, Hua & Ren (2024, *Energy Policy*) 则在另一行业情境下检验"官方主导媒体口径是否对资本市场有增量信息", 逻辑结构 (机构属性→语调差异→是否携带增量信息) 与本族「本省 vs 非本省」的二分设计同构, 可作为方法论对照。需要强调的是, 本族三个列均为 tier=standard 的三轨并排差分变量, 不单独承载识别策略或与相邻测度的构念区分讨论 (该部分留给核心测度族 `llm_vote_tone` 及 `tone_gap_*` 姊妹家族的 core 长文), 本文聚焦于交代该差值变量本身的构造逻辑、口径边界与缺失处理规则, 供下游研究者在解读 `bank_media_disagreement` 论文的媒体分歧回归系数时准确理解分子分母的来龙去脉。 在此基础上, 另有三条近期文献可为本族「媒体省份归属→语调系统性差异」的构念前提作补充锚定, 但均须按其原始设计的边界谨慎引用。Huang、Liu 与 Zhang (2024) 以本地报纸停刊作为本地媒体监督减弱的冲击, 检验公司非 GAAP 披露质量的变化, 其核心前提正是「总部所在地的本地媒体与异地媒体在监督功能上不可替代」, 与本族本省/非本省媒体二分的构念假设同源; 边界在于该文的本地口径为总部同城报纸 (较本族的省份口径更细)、识别策略为停刊事件的 DiD 而本族仅作横截面子集对比, 且该文只把本地媒体当作监督强度的处理变量、并未度量本地媒体的报道语调, 故只锚定「本地媒体是独立构念」这一半, 不锚定本族的语调聚合与作差算法。Huang、Li、Li 与 Lin (2024) 用社交媒体用户地理位置识别本地信息发布者, 按发帖者与公司总部的地理关系切分样本比较两组信息含量, 其子样本二分再作组间对比的设计与本族同构; 但该文文本源为散户发帖而非正式媒体报道, 地理归属基于用户 IP/自报位置而非媒体来源省份元数据, 且以股票收益为被解释变量、按同城而非同省二分, 研究对象为一般上市公司而非银行。Chen、Chen 与 Li (2025) 以逾 24,000 名散户的账户级日度持仓记录证明本地投资者在灾害冲击下更多增持本地股票, 且效应由信息优势驱动, 为「地理二分确实承载真实信息差异」提供近期证据; 其「本地」是投资者持仓与标的之间的关系而非媒体来源地与银行总部之间的关系, 原文有灾害外生冲击设计而本族无, 亦无任何媒体文本或语调测度, 因而仅锚定二分前提本身。
## VAR: tone_gap_homeprov_nonprov_ctx

【变体差分】
本列是 `tone_gap_homeprov_nonprov` 族在 ctx 轨 (标题+实体窗口正文) 下的实现: 分子端的两个中间均值 `tone_homeprov_media_ctx`、`tone_nonprov_media_ctx` 均取自 stage 21 ctx 轨的文章级 `llm_vote_score_ctx` 情感测度按省份子集分别聚合, 而非 full 轨全文测度、亦非 bank-year 级已聚合的 `llm_vote_tone_ctx`。ctx 轨的正文范围窄于 full 轨 (仅围绕目标银行/金科实体的邻近文本窗口, 而非整篇报道), 因此同一篇文章在 ctx 轨下的语调值可能与 full 轨不同 (通常方差更大, 因为窗口截取带来的信息损失使语调判定更依赖局部措辞而非全文语境)。行宇宙上, ctx 轨遵循留篇门控 full-only 铁律: 是否计入某银行-年度的报道集合仍以该文章的 `llm_verified_full == True` 为准, ctx 轨不单独产生额外的留篇/删篇判定, 只是在 full 已确认留篇的文章集合上换算 ctx 轨语调值参与分省聚合。该列与 `_full` 列互为稳健性并排规格 (二者刻画同一构念, 用不同宽度的正文窗口验证结论是否对文本截取方式敏感), 不构成主副关系, 亦不可与 `_full`/`_ss` 列同时放入同一 over-identified 的 Hansen J 过度识别检验中。若该银行-年度的本省或非本省媒体子集在 ctx 轨下报道篇数为零 (含全部回退为 fallback 情形对分母的正常计入), 对应 gap 值置缺失, 不做跨轨或跨年度插补。研究者在解读该列时应注意: ctx 轨窗口截取会削弱那些"银行在文中被提及但语调实际由文章其他段落塑造"的信息, 因此本省-非本省语调差在 ctx 轨下的量级未必与 full 轨一致, 差异本身也具有诊断价值——若 gap 在窄窗口下依然稳健存在, 说明本地偏袒并非仅由全文篇幅结构(如篇幅更长、背景介绍更详尽)驱动, 而是直接体现在紧邻实体的措辞选择上。

## VAR: tone_gap_homeprov_nonprov_full

【变体差分】
本列是 `tone_gap_homeprov_nonprov` 族的 full 轨口径, 即以标题+全文正文的文章级 `llm_vote_score_full` (而非 bank-year 级已聚合的 `llm_vote_tone_full`) 作为语调测度输入, 按省份子集分别取均值, 计算本省媒体均值与非本省媒体均值之差。full 轨是本族在留篇门控意义上的锚定轨: 2026-06-29 起, 「一篇报道是否被判定为银行-金科相关报道并纳入面板分母」这一门控只看 full 轨的 `llm_verified_full` 结果 (`tone_llms.py::df_filtered` 与 `run_pipeline_function.py::_stage21_skip_is_compatible` 两处副本须保持同步, 本列的行宇宙即由该门控决定); ctx/ss 两轨是在此留篇集合基础上换算的 conditional-on-full 测度/稳健性轨。`attention_media.py` 中的媒体分歧结果解读日志块 (2026-06-29 新增, golden-safe) 出于避免三轨 × 九维度冗余打印的考虑, 也仅对 full 轨的 `tone_gap_*` 九个变量 (含本列) 打印分布统计 (n/mean/std/[min,max]), 这一实现细节从侧面印证了 full 轨在整个 `tone_gap_*` 变量族里的锚定/首选展示地位, 但该地位仅限于日志展示与门控依赖, 并不改变三轨互为稳健性、不分主次的分析铁律 —— 研究者在正式回归中仍须将 full/ctx/ss 三列作为并排稳健性设计呈现, 而非把 full 轨当作"主效应"、ctx/ss 轨当作"附加检验"来单向汇报。该列与家族 frontmatter `formula` 字段的关系是: `formula` 字段中的 `{trk}` 占位符在本列取值为 `full`。由于 full 轨同时是留篇门控的判定轨与 `attention_media.py` 唯一打印分布日志的轨, 使用者容易误把该列当成家族"主口径"而把 ctx/ss 两列降格为附属稳健性检验, 这与本项目「三轨各自 just-identified 并排、互为稳健性不分主次」的铁律相悖; 正确的汇报方式是三列并列呈现系数与显著性, 而非仅报告本列并将另外两列压至附录一笔带过。

## VAR: tone_gap_homeprov_nonprov_ss

【变体差分】
本列是 `tone_gap_homeprov_nonprov` 族的 ss 轨 (同句共现窗) 口径, 分子端的两个中间均值取自 stage 21 ss 轨文章级语调测度 `llm_vote_score_ss` 按省份子集分别聚合 (而非 bank-year 级已聚合的 `llm_vote_tone_ss`), 该测度以「标题 + 银行∧金科词严格同句 (±N 句窗, N 取 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1) 共现」为正文范围, 是三轨中文本粒度最窄、对措辞局部性最敏感的一档。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行与金科词的严格同句共现, 则 `content_ss` 回退为全文正文、`ss_is_fallback` 置真, 但该文章依然正常计入 ss 轨语调聚合的分母 (即被并入本省或非本省子集参与均值计算), 不因回退状态被剔除或单独处理; 这一"优雅降级"设计确保即便金科词与银行词从未同句出现, 该文章仍能贡献一个 ss 轨语调观测值 (退化为等同 full 轨全文的判定), 而不是制造额外的系统性缺失。行宇宙同样遵循留篇门控 full-only 铁律, 仅在 `llm_verified_full == True` 的文章集合上换算 ss 轨值。ss 轨与 full/ctx 两轨在分析上严格并排、互为稳健性: 三者分别代表"全文语境"、"实体邻近窗口语境"、"严格同句紧邻语境"三种不同宽窄的文本截取假设下, 本省-非本省语调落差是否依然存在、方向是否一致、幅度是否稳定, 是同一构念在三种测量口径下的交叉验证, 任何将三轨同时纳入一个过度识别 (over-identified) Hansen J 检验的用法都违反项目铁律, 应予避免。
<!-- rendered-citations:begin -->
You, J., Zhang, B., Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Qin, B., Strömberg, D., Wu, Y. (2018). Media Bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Fang, Y., Wang, Q., Wang, Y., Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, Z., Li, J., Hua, X., Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
Huang, W., Liu, J., & Zhang, R.-Z. (. (2024). Local newspaper closures and non-GAAP reporting quality. Finance Research Letters, 62, 105024. https://doi.org/10.1016/j.frl.2024.105024
Huang, Y., Li, F., Li, T., & Lin, T. (2024). Local information advantage and stock returns: Evidence from social media. Contemporary Accounting Research, 41(2), 1089-1119. https://doi.org/10.1111/1911-3846.12935
Chen, H., Chen, Y., & Li, D. (2025). Local bias under natural disasters. International Review of Finance, 25(1), e70009. https://doi.org/10.1111/irfi.70009
<!-- rendered-citations:end -->
