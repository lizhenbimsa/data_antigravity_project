---
family_id: F597
columns:
- tone_x_scale_ctx
- tone_x_scale_full
- tone_x_scale_ss
unit: 情感语调得分 × 银行规模序数的交互项 (连续, 无固定上下限; 符号与量纲随 bank_scale_ord∈{1,2,3,4} 缩放)
formula: 'tone_x_scale{track} = llm_vote_tone{track} * bank_scale_ord, track ∈ {_full, _ctx, _ss}; bank_scale_ord 为银行规模四分序数 (XS=1, S=2, M=3, L=4), llm_vote_tone{track} 为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票语调共识, 取值区间约 [-1,1]'
producer: pipeline\panel\runner.py (交互项生成, 三轨循环块) ; pipeline\panel\export.py (.dta 变量标签映射)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
- bank_scale_ord
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L. & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y. & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from
    China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M. & Wilson, D. J.
  year: 2022
  title: Measuring news sentiment
  venue: Journal of Econometrics
  vol: '228'
  issue: '2'
  pages_or_artno: 221-243
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J. & Moshfeghi, Y.
  year: 2024
  title: 'Text-based sentiment analysis in finance: Synthesising the existing literature
    and exploring future directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: "10.1080/1540496x.2026.2698629"
  type: "journal"
  authors: "Zheng, Y., Li, R., Ren, S., & He, F."
  year: 2026
  title: "The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience"
  venue: "Emerging Markets Finance and Trade"
  pages_or_artno: "1-17"
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
`tone_x_scale_{full,ctx,ss}` 是本项目异质性分析 (heterogeneity analysis) 板块中「语调 × 银行规模」交互项族, 由 `pipeline\panel\runner.py` 在面板导出前的交互项构建块 (三轨循环, 见 `pipeline\panel\runner.py` L1595 起) 一次性生成, 并由 `pipeline\panel\export.py` 赋予 .dta 变量标签 (`Tone x Bank Scale (Full/Ctx)`)。构念动机是回答一个比「银行整体是否受媒体语调影响」更细的问题: 语调对银行经营/融资结果的边际效应, 是否随银行规模系统性变化。这是典型的调节变量 (moderator) 设计, 而非独立处理变量——`tone_x_scale{track}` 本身不是一次测量, 而是两个既有测量 (`llm_vote_tone{track}` 与 `bank_scale_ord`) 的逐行乘积, 用于在回归方程中以「主效应 + 交互效应」联合识别规模异质性, 遵循计量经济学中交互项设计须与两个构成因子的主效应同时纳入方程、方可无偏识别调节效应的通行规范。

被乘的两个因子各有独立来源。分子端 `llm_vote_tone{track}` 是三家大语言模型 (`gpt-5.4-nano`/gpt54nano、`gemini-3.1-flash-lite`/gemini31 两家走 OpenLux 网关, `deepseek-v4-flash`/deepseekv4 直连 `api.deepseek.com`) 对「一篇报道对目标银行是正面/中性/负面」的多数投票语调共识, 是 P1 (`bank_fintech_tone`) 论文的 canonical headline 处理变量 (`treatment.primary`), 取值区间约 [-1,1]、聚合到 bank-year 层为该行覆盖文章的均值。乘数端 `bank_scale_ord` 是银行规模四分序数 (XS=1、S=2、M=3、L=4), 依据资产规模/机构类型分层构造, 是横截面时不变 (within-bank 常量, 除非跨年发生规模跃迁) 的分组变量。两者相乘后, 交互项在数值上等价于「把语调按规模档位线性放大」——规模档位越高 (L=4) 的银行-年观测, 同样的语调水平会得到绝对值更大的交互项取值; 规模档位为 1 (XS) 的银行, 交互项数值上等于语调本身。这一算术特性提醒使用者: `tone_x_scale{track}` 不是「规模调整后的语调」或「按规模归一化的语调」, 而是未归一化的原始交互乘积, 其系数解读须结合回归方程中同时纳入的 `bank_scale_ord` 主效应项 (`bank_scale_ord`) 与 `llm_vote_tone{track}` 主效应项, 三者缺一不可地共同进入模型, 否则交互系数会因遗漏主效应 (低阶项) 而产生偏误——这是交互项/三重差分 (DDD) 计量设计中「须完整纳入所有低阶项」的通行规范, 本家族 producer 源码同一函数块内生成的三重差分交互项 `*_ddd_digfront` 遵循同一设计原则。

【方法学与计算】
计算发生在 `pipeline\panel\runner.py` 交互项构建块, 对 `['_full', '_ctx', '_ss']` 三个轨道循环执行同一逻辑: 若面板中存在 `llm_vote_tone{track}` 列, 则逐行计算 `panel[f'tone_x_scale{track}'] = panel[tone] * panel['bank_scale_ord']`, 与同一循环内生成的 `tone_x_soe{track}` (语调 × 国有股权哑变量) 及 `tone_x_highcov{track}` (语调 × 高媒体覆盖哑变量) 是并列的三个异质性交互项族, 共用同一源语调列、只替换调节变量。`bank_scale_ord` 在此前的面板构造步骤中已固定为 (c) 段之前的规模分层结果, 不随语调轨道变化, 因此三轨交互项之间的差异完全来自分子 `llm_vote_tone{track}` 的轨道差异, 乘数端不引入额外变异。

三轨语义严格对齐 P1 论文的三轨文本架构: `_full` 轨的源语调基于标题+全文正文 (`content_full`); `_ctx` 轨基于标题+目标银行实体窗口 (`content_ctx`); `_ss` 轨基于标题+银行∧金融科技词同句 (±N 句窗, 默认 N=1) 共现片段 (`content_ss`)。`_ss` 回退语义镜像 `_ctx`: 当一篇文章内不存在银行与金科词的同句共现时, `content_ss` 回退为全文 body、`ss_is_fallback` 置 True, 该行仍计入 `n_articles` 分母 (共享同一分母, 不因回退而单独剔除)。三轨在缺失语调源列时 (例如某轨情感未计算) 会被循环 `continue` 跳过, 因此不保证三列同时存在——这是 per-track 独立生成而非 both-or-neither 的强制配对, 与 co-primary 双轨嵌入 (Qwen 主测度 + `_lg` OpenAI 稳健轨) 的 both-or-neither 守卫是两种不同的容错哲学, 不可混淆。

留篇门控口径 (2026-06-29 起) 对本交互项族同样适用且具有传递性: stage 21 是否判定「一篇银行-金科报道」只看 `llm_verified_full == True`, `_ctx`/`_ss` 降级为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集。既然 `llm_vote_tone{track}` 本身遵循这一门控, 其派生交互项 `tone_x_scale{track}` 自动继承同一行宇宙约束——`_ctx`/`_ss` 两列的非缺失观测数不会超过 `_full` 列, 使用者在跨轨比较交互效应量级前应先核对各轨有效样本量, 避免把样本组成差异误读为规模异质性差异。

【文献定位】
媒体语调对资产定价与公司决策的横截面异质性效应, 是媒体金融学 (media finance) 文献的核心命题之一。Fang & Peress (2009, *The Journal of Finance*) 的经典发现是媒体覆盖的信息效应在低覆盖度证券上更强、随覆盖强度边际递减——这一"覆盖强度调节效应"逻辑的银行业类比正是 `tone_x_highcov{track}` (同一循环块的姊妹交互项), 而 `tone_x_scale{track}` 是把调节变量从"覆盖强度"替换为"银行自身规模"的平行设计: 大型银行通常拥有更强的信息披露能力、更成熟的投资者关系团队与更高的分析师跟踪覆盖, 理论上媒体语调对其定价/融资成本的边际信息含量可能小于中小银行 (中小银行透明度更低, 媒体是投资者获取增量信息的相对更重要渠道)。Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 在中国银行业情境下直接验证媒体情感对存款稳定性与系统性风险的影响, 是本交互项族在同一制度背景 (中国银行业) 下最直接的构念参照, 其识别策略同样需要控制银行规模等横截面异质性来源。Shapiro, Sudhof & Wilson (2022, *Journal of Econometrics*) 提出以 ELMo 深度学习方法从新闻文本构造宏观经济情感指数、并与独立宏观经济活动指标做外部效度验证的测量学路径, 与本项目「先用模型化方法从文本抽取情感信号、再与独立结果变量做验证」的一般方法论取向相通, 为本项目采用模型化 (而非纯词典) 情感测度的可行性提供旁证; 该文本身并未涉及发行主体异质特征或规模分组下的稳健性检验, 此处仅作为文本情感测量方法论的一般性参照, 不构成对「规模异质性作为语调测度稳健性维度」这一具体设计选择的直接文献支持——本列的规模异质性设计动机主要来自 Fang & Peress (2009) 的覆盖强度调节效应类比与 Fang, Wang, Wang & Yuan (2024) 的中国银行业同域验证, 见上文。Todd, Bowden & Moshfeghi (2024) 对金融文本情感分析文献的系统综述亦指出, 情感测量的经济含义高度依赖被测量对象的异质特征 (规模、行业、透明度), 交互项设计是控制这一依赖性的标准计量工具。

三轨/门控口径铁律: `tone_x_scale_full`/`tone_x_scale_ctx`/`tone_x_scale_ss` 三者各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验方程; 三者共同继承 full-only 留篇门控 (2026-06-29) 的行宇宙约束, `_ss` 回退语义镜像 `_ctx`。使用者在 Stata 侧引用本交互项族时, 应同步纳入对应轨道的 `llm_vote_tone{track}` 与 `bank_scale_ord` 主效应项, 以及 (若同时研究覆盖强度调节) `tone_x_highcov{track}`——三个交互项族互不替代, 各自捕捉不同调节维度 (国有属性/媒体覆盖强度/银行规模), 不应在同一回归设定中把它们当作彼此的替代测度混用。 就调节变量一侧的近期同域依据, Zheng、Li、Ren 与 He (2026) 以中国金融科技创新监管试点 (监管沙盒) 为准自然实验, 考察其对银行金融科技发展与风险韧性的影响, 并在银行层面附带讨论了规模异质性, 为「银行规模在金融科技情境下是有经济含义的分组维度」提供前沿参照; 但须严格降级: 规模异质性属该文附带的分组讨论而非其主测度, 其被解释变量为银行金科发展指数与风险韧性、不涉及媒体语调, 更未采用本族 XS/S/M/L 四分序数口径, 故不构成对 bank_scale_ord 具体切分规则的背书。就被乘数一侧, Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度并将其应用于意大利银行融资条件这一银行层级实证问题, 是「新闻语调 → 银行层级结果」链条的近期同域实践, 与本族 llm_vote_tone{track} 聚合至 bank-year 的构造与应用域一致; 迁移边界在于其国别与语料为意大利而非中文新闻, 语调来源既非本项目六词典 union 亦非三家 LLM 投票共识, 无三轨 (full/ctx/ss) 文本切分, 且该文未做任何规模分组的调节检验, 因而只锚定「语调测度—银行层级结果」这一半, 不锚定本族的规模交互设计本身。
## VAR: tone_x_scale_ctx

【变体差分】
本列取 `llm_vote_tone_ctx` (基于「标题+目标银行实体窗口」文本构造的语调共识) 与 `bank_scale_ord` 的逐行乘积, 是 `_ctx` 轨语境窗口对规模异质性效应的稳健性检验分支。`_ctx` 轨的语调来源聚焦银行实体周边文本窗口, 相较 `_full` 轨排除了正文中与目标银行无关的段落噪声, 理论上对语调-规模交互效应的估计噪声更小, 但同时也继承了「留篇门控 = full-only」带来的行宇宙收缩——本列非缺失观测数不超过 `_full` 轨对应列。与 `tone_x_scale_full`、`tone_x_scale_ss` 构成三轨并排稳健性设计, 三者共用同一 `bank_scale_ord` 调节变量, 差异完全来自源语调轨道; 三者各自 just-identified, 禁止在同一过度识别设定中混用。若研究关注「聚焦银行相关文本片段后, 语调对不同规模银行的边际效应是否依然存在」, `_ctx` 轨是相较 `_full` 轨排除无关段落噪声后的首选稳健性验证轨。

在解读层面, `_ctx` 轨与 `_full` 轨的分歧主要来自两个来源: 其一是文本窗口本身的信息密度差异——大型银行 (L=4) 往往在一篇报道中被多次提及、涉及业务面更广, 全文与实体窗口两种截取方式对语调判定的影响可能因规模而异, 这恰是本列存在的价值——用交互效应捕捉"文本截取方式对不同规模银行语调测量误差是否系统不同"这一潜在混淆; 其二是留篇门控的行宇宙约束使 `_ctx` 轨天然是 `_full` 轨的样本子集, 因此两轨交互系数的差异既可能反映真实的规模异质性差异, 也可能部分反映样本构成差异, 使用者在做跨轨系数比较前应先核对分银行规模档位的有效样本量分布, 避免把样本选择效应误读为语境窗口效应。与 `tone_x_scale_full`、`tone_x_scale_ss` 一样, 本列的回归解读须同时纳入 `llm_vote_tone_ctx` 与 `bank_scale_ord` 两个主效应项, 三者缺一不可, 单独报告交互系数而不报告主效应项会违反交互设计的计量学完整性规范。

## VAR: tone_x_scale_full

【变体差分】
本列取 `llm_vote_tone_full` (基于「标题+全文正文」完整文本构造的语调共识) 与 `bank_scale_ord` 的逐行乘积, 是三轨中的 canonical/headline 轨, 对齐 P1 (`bank_fintech_tone`) 论文主处理变量 `llm_vote_tone_full` 的口径。stage 21 留篇门控只看 `llm_verified_full == True`, 即本列所依赖的行宇宙是三轨中最宽的一支 (`_ctx`/`_ss` 均为其子集), 因此在跨轨比较样本量或做主回归设定选择时, `_full` 轨通常是默认起点, `_ctx`/`_ss` 是互为稳健性、不分主次的平行验证轨而非替代关系。本列数值上等于「全文语调 × 规模序数」, 系数解读须联立回归方程中的 `llm_vote_tone_full` 与 `bank_scale_ord` 两个主效应项一并读出, 单独看交互系数、遗漏主效应项容易得出误导性结论。

作为 headline 轨, 本列在 P1 论文异质性分析表中承担的角色是回答"整体语调效应是否因银行规模而系统性放大或衰减"这一首要问题: 若交互系数为负且显著, 意味着语调的定价/融资成本传导效应在大型银行 (`bank_scale_ord` 取值更高) 中相对更弱, 与 Fang & Peress (2009) 关于媒体信息效应随覆盖/关注度提升而边际递减的经典发现在方向上一致——大型银行本身分析师跟踪、机构关注度更高, 媒体语调作为增量信息渠道的边际贡献相应更小。反之若交互系数为正, 则提示大型银行对媒体语调更敏感, 可能与其融资规模更大、市场关注度放大效应更强有关, 需要结合 `tone_x_highcov_full` (覆盖强度调节) 与 `is_soe` 相关交互项联合诊断, 避免把规模效应与国有属性/覆盖强度效应混淆归因, 三者应在同一回归表中并列报告而非相互替代。

## VAR: tone_x_scale_ss

【变体差分】
本列取 `llm_vote_tone_ss` (基于「标题+银行∧金融科技词同句共现片段」构造的语调共识) 与 `bank_scale_ord` 的逐行乘积, 是三轨中判据最严格的一支——`_ss` 轨要求银行与金科相关词汇在同一句 (默认 ±1 句窗口, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 内共现, 未满足该判据的文章其 `content_ss` 回退为全文 body 且 `ss_is_fallback` 置 True (回退语义镜像 `_ctx`, 该行仍计入 `n_articles` 分母)。本列因此比 `_ctx`/`_full` 更聚焦"银行与金科议题紧密并置"的报道子集, 若某银行-年观测覆盖文章中银行金科同句共现比例很低, 该行 `tone_x_scale_ss` 的有效样本贡献会相应稀薄 (虽仍受回退语义保留观测而非缺失)。与另两轨一样继承 full-only 留篇门控的行宇宙约束, 三轨并排、互为稳健性、禁止混入同一 over-identified Hansen J。

本列的解读还需额外留意 `_ss` 判据本身的选择性: 银行与金科词同句共现要求比 `_ctx` 的实体窗口更严格, 意味着一篇报道即便被 `_ctx` 判定为"与目标银行相关", 也未必满足 `_ss` 的同句共现判据, 此时该篇文章对 `content_ss` 的贡献退化为回退全文 body (`ss_is_fallback=True`)。对于金科议题报道密度本身随银行规模而系统变化的情形 (例如大型银行的金融科技战略报道更多、更易形成银行-金科同句表述), `_ss` 轨的有效 (非回退) 观测占比可能随 `bank_scale_ord` 档位而异, 这构成一种潜在的测量口径与调节变量相关的混淆来源。使用者若发现 `tone_x_scale_ss` 与 `tone_x_scale_full`/`tone_x_scale_ctx` 在符号或显著性上出现分歧, 应优先核查各规模档位下 `ss_is_fallback` 的占比分布, 区分"真实规模异质性"与"同句共现判据的规模相关选择性"两种可能解释, 而非直接以三轨系数的算术平均或简单择优作为定论。

需额外提示一处导出层的不对称: `pipeline\panel\export.py` 的 .dta 变量标签映射字典目前只登记了 `tone_x_scale_full`→`Tone x Bank Scale (Full)` 与 `tone_x_scale_ctx`→`Tone x Bank Scale (Ctx)` 两条, 本列 `tone_x_scale_ss` 并无专属标签条目, 在生成的 .dta 文件中该列会以变量名本身或通用回退展示、缺少 "(Ss)" 后缀的可读标签。这一不对称仅存在于 Stata 变量标签展示层面, 不影响本列在 parquet/面板计算层的取值与 just-identified 并排地位——三轨在数据构造与统计意义上仍严格对等、互为稳健性、不分主次, 但使用者在 Stata 侧按变量标签检索或生成描述性表格时, 需知悉 `_ss` 列可能因缺少专属标签而不便与另两轨并列展示, 建议核查 `.dta` 时以变量名而非标签作为跨轨对齐的可靠依据。

<!-- rendered-citations:begin -->
Fang, L. & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Fang, Y., Wang, Q., Wang, Y. & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Shapiro, A. H., Sudhof, M. & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Todd, A., Bowden, J. & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Zheng, Y., Li, R., Ren, S., & He, F. (2026). The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience. Emerging Markets Finance and Trade, 1-17. https://doi.org/10.1080/1540496x.2026.2698629
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
</content>
