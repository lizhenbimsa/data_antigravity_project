---
family_id: F573
columns:
- tone_gap_fin_other_ctx
- tone_gap_fin_other_full
- tone_gap_fin_other_ss
unit: 语调缺口 (连续, 两个媒体类型子样本情感均值之差; 单位与 llm_vote_score{track} 一致, 约 [-2,2] 理论域, 实测集中于 [-1,1] 窄区间; bank-year 面板粒度)
formula: 'tone_gap_fin_other{track} = tone_fin_media{track} - tone_other_media{track}; 其中 tone_fin_media{track} = mean(llm_vote_score{track} | _media_type=="fin"), tone_other_media{track} = mean(llm_vote_score{track} | _media_type=="other"), 分组键 (target_bank, year); _media_type 由 媒体(中文) 名称经 _classify_content 规则分派为 {fin, comp, other} 三类之一'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet
- 00_preprocessing.parquet
citations:
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: "The Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who captures the power of the pen?"
  venue: "The Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  pages_or_artno: "1150-1172"
- doi: "10.2139/ssrn.5220056"
  type: wp
  authors: "Marchetti, S., Tarducci, E., & Branzoli, N."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "SSRN Working Paper"
new_dois: []
---

## CORE

【构念与来源】
tone_gap_fin_other 家族衡量同一银行同一年度内, 财经专业媒体 (fin) 与非财经/非公司类媒体 (other) 在报道语调上的系统性落差, 是 attention_media 模块"媒体异质性"分析块下的第②维度产物。上游 `21_tone_llms.parquet` 提供逐篇 `llm_vote_score{track}` (三家 LLM: gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash 多数投票得到的语调连续分, 非双极中性均值; 详见 CLAUDE.md「LLM 三家…互为稳健性」段), `00_preprocessing.parquet` 提供文章的原始「媒体(中文)」字段。`attention_media.py::_classify_content` 依据媒体名称的规则字典把每条报道的媒体来源分派为三类之一: fin (财经专业媒体, 如证券时报、金融时报一类以财经报道为主业的outlet)、comp (综合性大报, 一般性时政/社会类主流媒体)、other (二者之外的剩余类, 含地方都市报、行业细分刊物等)。分类完成后, 模块先算 `fin_media_frac`/`comp_media_frac` 两个占比控制变量, 再在同一循环体内对 (target_bank, year) 分组分别求 fin/comp/other 三类子样本的语调均值 `tone_{fin,comp,other}_media{track}`, 最后两两作差得到三组缺口: fin-other (本家族)、comp-other、fin-comp。三者共享同一构造逻辑, 仅媒体类别配对不同, 互为并列指标而非层级关系。tone_gap_fin_other 的实质解读是: 值为正表示该银行当年在财经专业媒体上获得的报道语调比在非财经/非综合类媒体上更正面 (即专业媒体更"给面子"或掌握更多软信息优势), 值为负则相反。这一构念呼应 You, Zhang & Zhang (2018, Review of Financial Studies) 关于媒体异质性影响信息含量的发现——不同类型媒体在信息生产动机、专业能力与商业模式上系统性不同, 导致同一标的物在不同媒体渠道下的报道基调可能出现结构性偏离, 而非随机噪声。

【方法学与计算】
计算分两步。第一步是媒体类型分派: `_classify_content` 对每条报道的「媒体(中文)」名称做字符串规则匹配 (非 NLP 模型), 输出互斥的三分类标签 `_media_type ∈ {fin, comp, other}`; 该分派与情感度量本身完全解耦, 分派错误只影响分组归属不影响语调分值本身。第二步是分组均值差分: 对给定轨道 track (取值 `_full`/`_ctx`/`_ss` 之一), 源列 `src = llm_vote_score{track}`; 模块先做守卫 `if src not in df.columns: continue`, 即若该轨道的上游情感列在当次运行中缺席 (例如上游未产出或被裁剪), 则整条轨道 (含三个缺口列) 优雅跳过, 不写入面板, 而非填充 0 或强制报错。若列存在, 则按 (target_bank, year) 分组、按 `_media_type` 子集分别取 `llm_vote_score{track}` 均值, 得到 `tone_fin_media{track}` 与 `tone_other_media{track}`, 二者逐 bank-year 相减写入 `tone_gap_fin_other{track}`。任一侧子样本在某 bank-year 内为空 (即该年该行该类媒体零篇报道) 时, `.mean()` 返回 NaN, 经 `panel.get(..., np.nan)` 与减法运算自然传播为该 bank-year 该缺口列的 NaN, 是稀疏子样本下的正常缺失, 不代表异常。三轨口径的语义边界至关重要: full 轨为标题+全文语调 (2026-06-29 起 full-only 门控下的留篇判定主轨), ctx 轨为标题+银行/金科实体窗口语调, ss 轨为标题+银行∧金科同句共现窗口语调 (无共现证据时按 CLAUDE.md 记载的 ss 回退语义, 镜像 ctx 的降级规则, 以全文 body 兜底并标记 `ss_is_fallback=True`, 但门控判定与留篇集口径始终以 full 轨为准, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集); 因此三条 tone_gap_fin_other 列衡量的是"同一构念在三种不同文本窗口下的媒体类型语调缺口", 而非三个独立构念, 三者应各自 just-identified 并排使用、互为稳健性、不分主次, 严禁把三轨系数混入同一 over-identified Hansen J 检验。

【文献定位】
本家族在方法论谱系上直接继承 Tetlock (2007, Journal of Finance) 开创的"媒体语调作为投资者情绪代理"传统, 并借鉴 You, Zhang & Zhang (2018, Review of Financial Studies) 对媒体异质性 (谁在写、写给谁看) 系统性影响报道信息含量的实证发现, 把这一异质性思路应用到中国银行业新闻语料上, 用"财经专业媒体 vs 其他媒体"的语调落差衡量专业媒体是否存在系统性的报道倾向差异。语调本身的度量依赖 stage 21 三家 LLM 多数投票的中文金融语境情感打分, 该测度构造本身独立于任何特定词典方法。此处援引 Du, Huang, Wermers & Wu (2022, Review of Finance) 仅作背景类比而非直接方法基础: 该文的核心论证是中文语境下情感构念需领域特定校准 (通用情感词典与金融专用词典/模型对同一文本片段可能给出系统性不同的极性判断), 本家族借用的是这一"领域特定校准"的一般性论断本身, 并未采用该文的词典或校准参数; 借用该论断只是为了说明: 类似的领域敏感性逻辑同样适用于跨媒体类型语调比较: 财经专业媒体的行文风格、术语密度与语气习惯天然不同于综合类媒体, tone_gap 度量正是要捕捉这种媒体类型层面的系统性落差而非随机文本噪声。在中国银行业情境下, Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 的银行级媒体情感研究提供了同域参照, 确认媒体情感差异对银行系统性风险与存款稳定性具有可观测的经济含义, 支持了把媒体类型异质性纳入银行-年面板作为控制/机制变量的合理性; Marchetti, Tarducci & Branzoli (2025, SSRN) 则示范了银行×年语调聚合的具体操作口径 (子样本分组均值), 与本家族的聚合逻辑一致。

## VAR: tone_gap_fin_other_full

【变体差分】
本列取 track=`_full`, 源列为 `llm_vote_score_full`, 即标题+全文文本轨道下的语调均值。full 轨是 2026-06-29 起「留篇门控 = full-only」铁律下的主轨: stage 21 是否判定一篇报道为"该银行的金科相关报道"仅依据 `llm_verified_full == True`, 因此 tone_gap_fin_other_full 所依赖的分母 (fin/other 两类子样本的篇数与语调均值) 天然对齐留篇集本身, 无需再做 conditional-on-full 的子集限定, 是三轨中样本量最充裕、缺失 (NaN) 出现频率最低的一支。在 P1 主轨语境下, `llm_vote_tone_full` 已是 canonical headline treatment, tone_gap_fin_other_full 作为其媒体异质性分解, 是理解"银行整体语调均值"背后是否存在媒体类型驱动的结构性来源的首选轨道, 通常作为家族内的默认参照口径与后续 ctx/ss 两轨稳健性检验的基准锚点, 但按铁律仍与 ctx/ss 两轨各自 just-identified 并排、不设主次, 不得把三轨系数混入同一 over-identified 设定联合估计。构造上, full 轨语调既包含围绕银行/金科实体的直接评述, 也包含全文其余段落 (行业背景、宏观语境、无关业务条线等) 对整体语气的稀释效应, 因此该列度量的是"整篇报道通读之后的总体印象落差", 与 ctx/ss 两轨"聚焦局部语境的精确落差"构成互补而非替代关系, 三者拼合可近似还原一个从粗到细的语境分辨率梯度。

## VAR: tone_gap_fin_other_ctx

【变体差分】
本列取 track=`_ctx`, 源列为 `llm_vote_score_ctx`, 即标题+银行/金科实体窗口文本轨道下的语调均值。ctx 轨聚焦围绕目标实体 (银行名/金科相关词) 的局部文本窗口而非全文, 意在剥离与银行本体无关的段落对语调打分的稀释或污染。在 full-only 门控下, ctx 轨的行宇宙是 full 留篇集的子集 (conditional-on-full), 即分组均值仅在该 bank-year 于 full 轨已被判定为有效报道的文章范围内计算 ctx 语调, 因此 tone_gap_fin_other_ctx 应理解为"在已确认留篇的报道集合内, 聚焦实体窗口后测得的媒体类型语调缺口", 是 full 轨结果的稳健性检验轨而非独立样本。若目标银行的实体窗口未能定位 (罕见的解析失败场景), 相应 `content_ctx` 回退为全文 body 且标记 `ctx_is_fallback=True`, 该行的 ctx 轨语调退化为与 full 轨趋同, 但分类归属 (`_media_type`) 与分组键不受影响。相比 full 轨, ctx 轨的经济学解读更贴近"当读者只关注与银行直接相关的段落时, 财经专业媒体与其他媒体之间是否仍存在系统性语调落差"——若 tone_gap_fin_other_ctx 与 tone_gap_fin_other_full 符号一致且量级相近, 说明媒体类型效应并非源于全文背景段落的稀释或放大, 而是集中体现在与银行本体直接相关的核心陈述中, 这对排除"缺口只是全文长度/话题分布差异的机械产物"这一替代解释具有辅助价值; 反之若两轨方向相左或量级悬殊, 则提示该缺口的驱动力更多来自报道的宏观背景铺陈而非对银行本体的直接评价, 解读时须结合两轨篇数 (受 `_ctx_is_fallback` 影响的有效窗口覆盖率) 一并核对。

## VAR: tone_gap_fin_other_ss

【变体差分】
本列取 track=`_ss`, 源列为 `llm_vote_score_ss`, 即标题+银行∧金科同句共现窗口文本轨道下的语调均值, 是三轨中窗口最窄、判据最严格的一支: 只有银行实体词与金科相关词出现在同一句 (±N 句窗口, 默认半径 1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`) 内的片段才计入。ss 轨的回退语义镜像 ctx: 当某篇报道内不存在银行∧金科同句共现证据时, `content_ss` 退化为全文 body 且 `ss_is_fallback=True`, 分母 `n_articles` 与 ctx 轨共享同一套统计口径。与 ctx 轨相同, ss 轨的行宇宙同样是 full 留篇集的子集 (conditional-on-full), tone_gap_fin_other_ss 因此衡量"在已确认留篇报道中, 严格限定到银行-金科同句共现的最窄语境下"媒体类型语调缺口是否依然存在或改变符号/量级——若该缺口在三轨间方向一致、量级递减 (full > ctx > ss 或反向单调), 可为"媒体类型效应源自银行-金科强相关表述而非泛泛提及"的解释提供辅助证据; 但由于窗口收窄导致样本进一步稀疏, 空缺口 (NaN) 出现频率通常高于 full/ctx 两轨, 解读时须留意分母篇数是否过小。此外, ss 轨的判据主体是"银行∧金科同句"共现而非"银行∧银行"或纯银行提及, 这意味着 tone_gap_fin_other_ss 实际上更接近"在金科相关叙事最密集的那一句话里, 财经专业媒体与其他媒体的语调是否仍有系统性落差", 与家族其余两轨相比带有更强的金科语境特异性。在生产 T=18 全量语料上, 该轨预计仍会保留一定比例的 `ss_is_fallback=True` 行 (银行提及但无同句金科共现), 这些行的 ss 语调实质上退化为全文口径, 与 full 轨高度重合, 因此三轨之间的边际差异主要来自"非回退"子集贡献, 解读跨轨对比时应结合各轨有效 (非回退) 篇数占比一并核查, 避免把回退子集的机械趋同误读为构念本身的稳健性证据。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
<!-- rendered-citations:end -->
