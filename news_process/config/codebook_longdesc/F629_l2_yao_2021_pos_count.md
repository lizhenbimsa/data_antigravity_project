---
family_id: F629
columns:
- yao_2021_pos_count_ctx
- yao_2021_pos_count_full
- yao_2021_pos_count_ss
unit: 篇数 (count of articles)
formula: 'pos_count = bank-year 内该轨 yao_2021_score_{track} (逐词典否定翻转+程度副词+转折三规则已加权的 normalized_score) > 0 的文章篇数; 篇章级二值指示 `_is_yao_2021_positive{track}` = (yao_2021_score{track} > 0) 在 pipeline/panel/runner.py 洗稿率前置段 (方法 D2, 单个词典, 引 Gentzkow et al. 2019 JEL) 构造, 再由 sum 聚合到 bank-year 面板; 是"净分类为正"的文章计数, 不是逐词命中原始计数'
producer: "pipeline/sentiment/tone_words.py (计算 yao_2021_score{track} 归一化语调分, 含否定翻转/程度副词/转折三规则) ; pipeline/panel/runner.py (方法 D2: 由 score{track}>0 构造 _is_yao_2021_positive{track} 篇章级指示列, 洗稿率前置段) ; pipeline/panel/encode.py (agg[f'{d}_pos_count{track}'] = (f'_is_{d}_positive{track}', 'sum') 聚合为面板列) ; pipeline/panel/stata_export.py (面板标签)"
upstream:
- 14_materialize_ctx (content_ctx/content_ss 物化)
- 22_tone_words (词典打分产出 yao_2021_score{track} 归一化语调分)
- 40_panel_export_main (runner.py 方法 D2 篇章级指示列构造 + encode.py sum 聚合)
citations:
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  pages_or_artno: "1150-1172"
- doi: "10.1080/21697213.2019.1701259"
  type: journal
  authors: "Xu, W., Yao, Z., & Chen, D."
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: "China Journal of Accounting Studies"
  vol: "7"
  issue: "3"
  pages_or_artno: "407-437"
- doi: "10.2139/ssrn.3446388"
  type: wp
  authors: "Bian, S., Jia, D., Li, F., & Yan, Z."
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: "SSRN Working Paper"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: "10.1016/j.jaccpubpol.2024.107181"
  type: "journal"
  authors: "Cheng, C. A., Jiang, L., & Song, W.-L."
  year: 2024
  title: "Media coverage and debt financing choice"
  venue: "Journal of Accounting and Public Policy"
  vol: "44"
  pages_or_artno: "107181"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是 bank-year 内被 yao_2021 中文金融情感词典判为"净正面"的报道篇数, 属 pipeline 词典法情感打分体系 (stage 22 `tone_words`) 与面板洗稿率 (washing ratio) 前置构造 (方法 D2, 见 `pipeline/panel/runner.py`) 共同产出的一列, 并非词典逐词命中的原始计数。yao_2021 与 jiang_2021、bian_2021、du_2022、you_2018、loughran (L&M 中译) 并列, 是项目"词典消融梯度"体系下的一员; 各词典独立构造正面词表/负面词表/否定翻转规则/程度副词规则/转折规则, 对同一段文本各自打分, 彼此互为稳健性、不设主次。真正承载"正面词/负面词逐词命中原始计数"的中间量是 stage 22 `tone_words.py` 内部函数返回的 `pos_cnt`/`neg_cnt` (用于计算 `{dict}_pos_ratio` 等固定词表聚合测度), 但该原始计数从未以 `pos_count` 之名写入面板列。本列 `{dict}_pos_count{track}` 的真实构造路径是: stage 22 先算出已完成否定翻转/程度副词加权/转折规则处理的归一化语调分 `yao_2021_score{track}` (`normalized_score`, 值域 [-1,1]); 面板构造阶段 (`pipeline/panel/runner.py` 洗稿率前置段, 方法 D2, 引 Gentzkow, Kelly & Taddy 2019, Journal of Economic Literature 的文本计量方法论) 用 `yao_2021_score{track} > 0` 对每篇文章打一个二值指示 `_is_yao_2021_positive{track}`, 再由 `pipeline/panel/encode.py` 对该指示列在 bank-year 内求和, 得到"净语调为正的文章篇数"。因此本列单位是"篇数"而非"词条出现次数", 且其分类依据恰恰是经过语言学规则加权之后的分数符号, 与"未经否定翻转/程度加权的原始命中数"这一朴素计数概念在方法论上是两回事——它衡量的是文章级情感分类结果的分布 (有多少篇被词典整体判为正面), 而非词表匹配密度。项目在面板层保留这一列, 是为了支撑洗稿率 (washing ratio) 等下游构造: 洗稿率的分子进一步区分"正面且象征性用语" (`pos_symb`) 与"正面且实质性" (subst-valid) 两类子集, `pos_count` 是这套多方法 (LLM 投票/反向/词典/BERT argmax) × 三轨洗稿率变体共用的分母/基准计数之一。

【方法学与计算】
计算分两步, 分别发生在两个不同的 stage/文件, 不可混为一处: 第一步在 stage 22 `tone_words.py` 的词典打分主循环内完成——对每篇文章的三条文本轨 (`content_full`/`content_ctx`/`content_ss`, 由 stage 14 `ctx_materializer` 在 stage 21 情感环节之前统一物化, 三轨均已 `prepend_title` 拼接标题) 分别执行 jieba 分词 (版本冻结为 0.42.1 以保证跨次重跑分词结果确定性), 与 yao_2021 词典 (SSOT = `config/tone_dicts.json`, 结构化正面词/负面词/否定词/程度副词/转折词五类词表, 项目内不读取原始 `dicts_excel` 语料) 逐词匹配, 应用否定翻转 (词前出现否定词则该词情感符号翻转)、程度副词加权 (强化/弱化情感强度) 与转折规则 (转折连词后语义优先) 三套语言学规则, 汇总得到 `total_score`/`total_abs_score`, 归一化为 `yao_2021_score{track} = total_score / total_abs_score ∈ [-1, 1]`。第二步发生在面板构造阶段: `pipeline/panel/runner.py` 的洗稿率前置段 (标注"方法 D2: 单个词典 (Gentzkow et al. 2019, JEL)") 对每篇文章、每条轨道判定 `_is_yao_2021_positive{track} = (yao_2021_score{track} > 0)`, 生成一个 0/1 篇章级指示列; `pipeline/panel/encode.py` 随后按 bank-year 分组对该指示列求 `sum`, 即为面板列 `yao_2021_pos_count{track}`。这一构造与同源的 `pos_symb_count` (指示列进一步与"是否含象征性/符号化表述"标记做逻辑与) 共用同一批 `_is_{dict}_positive{track}` 上游指示列, 但与 `pos_substvalid_count` (以 LLM 实质性分类结果同域化分母) 走的是不同的分母口径。三轨 (full/ctx/ss) 各自独立完成分词、打分与二值化, 互不借用彼此的分词结果或分类结果, 因为 `content_ctx`/`content_ss` 与 `content_full` 在文本跨度上本就不同 (ctx=标题+实体窗口摘录, ss=标题+银行∧金科同句±N窗口, full=标题+全文), 逐轨独立计数才能保证每轨测度真实反映该轨文本本身的语调分类结果, 不产生轨间信息泄漏; 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。面板层的标签体系与其余 5 部词典的对称衍生列 (`neg_count`/`std`/`vw`/`mw`/`hw`/`tech`/`app`/`idf` 等) 共用同一套泛型推断规则, 保持六部词典命名与聚合口径的完全对称, 便于跨词典横向比较"净正面文章占比"而不引入结构性度量偏差; 需要词典原始命中密度 (未经净分类) 的研究者应转向 `pos_ratio` 一类固定词表聚合测度, 而非本列。

【文献定位】
洗稿率式"正面且象征性 vs. 正面且实质性"文本分类方法论, 直接呼应 Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 关于文本计量在经济学应用中的方法论综述——本列所依赖的方法 D2 构造在项目代码注释中即明确引述该文, 将"语调分是否为正"这一二值分类作为下游洗稿率、象征性用语占比等测度的基础分子/分母来源。项目内六部词典中的 bian_2021 (Bian, Jia, Li & Yan, 2021, SSRN working paper) 同为中文金融情感词典构造的直接同类工作, 与 yao_2021 并列构成本项目词典法情感测度的方法学互证基础; Xu, Yao & Chen (2019) 在 China Journal of Accounting Studies 讨论中文年报可读性度量的构造与检验方法, 与本族共享中文财务文本词法层测度对分词稳定性、词表匹配信度的基本方法论关切。更贴近本列实际用途的外部效度锚点是 Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 对中国银行层面媒体情感、存款稳定性与系统性风险传导关系的实证研究——该文直接在"银行级媒体文本语调分类"这一构念层面为本族测度提供了应用场景参照, 说明将逐篇语调净分类结果 (而非词表命中密度) 聚合为 bank-year 篇数, 是刻画银行相关媒体报道情感分布、进而检验其对银行经营/风险结果传导效应的合理中间测度。六部词典并列、否定翻转/程度副词/转折三规则加权在先、篇章级净分类计数在后的分层设计, 均服务于同一目标: 让"净正面文章占比"这一构念在传导到面板结果之前保持逐环节可拆解、可稳健性检验, 而非依赖单一词典单一规则组合的合成分数。词典法计数在情感判定质量上相较机器学习方法的定位另有 Frankel, Jennings & Lee (2022, Management Science) 的顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 为本项目在词典法之外并列引入 LLM 三家投票与 BERT 三模型作跨方法稳健性对照提供了顶刊层级的方法学正当性。 这一「逐篇极性判定→按主体-年求和」的聚合范式在近期前沿实证中亦有直接用例: Cheng、Jiang 与 Song (2024) 把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量与新闻情感, 并以此进入债务融资方式选择回归, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率; 但须注意其极性来自 RavenPack 专有事件情感分析 (既非公开情感词典、亦非人工编码), 主体为美国上市公司而非商业银行, 故该文只锚定本列「对文章级极性指示按主体-年求和」的聚合形态, 不锚定其极性来源。以银行为归集主体的同域前沿应用则见 Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026): 该文构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 说明把新闻情感按银行主体归集后进入银行层面实证已为顶级金融稳定期刊所接受; 其语境为美国银行监管 (以监管评级/监管行动为 DV), 情感测度的构造细节与本项目六部词典并列、三规则加权在先的口径不同, 亦无 full/ctx/ss 三轨设计, 因而仅作构念层面的应用参照。
## VAR: yao_2021_pos_count_ctx

【变体差分】
本列取自实体窗口轨 `content_ctx` (标题 + 目标银行/金科实体上下文窗口摘录, `prepend_title` 拼接), 是"净正面文章篇数" (`yao_2021_score_ctx > 0` 的文章数, 方法 D2) 家族在 ctx 轨上的独立分类计数结果, 与 full/ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。ctx 轨的文本跨度显著窄于 full 轨 (仅截取实体附近窗口而非全文), 词典打分所依赖的上下文信息更少, 因此本列所反映的是"在实体窗口摘录范围内被判为净正面"的篇数, 与 `_full` 列可能因文本跨度差异而对同一批文章给出不同的正负分类结果, 二者不可直接视为同一构念的水平对照, 只应作为互为稳健性的并列测度使用。留篇门控口径遵循 full-only 铁律 (2026-06-29 起): 一篇报道是否计入"银行金科报道"样本仅由 `llm_verified_full` 判定, ctx 轨的行宇宙是 full 留篇集合的子集, 本列在该子集内按 ctx 文本独立完成打分与二值分类, 不会因 ctx 轨自身判定结果扩大或缩小样本范围。当某篇文章缺乏可识别的实体窗口摘录 (即 ctx 轨退化为回退状态) 时, 该行的 ctx 分类仍按回退文本 (退化为与 full 轨相同的全文) 计算, 由 `ctx_is_fallback` 标记该行的回退状态, 供下游做稳健性剔除或加权处理之用。本列在跨词典比较中的定位是: 若某篇文章在 yao_2021 词典下的 ctx 语调净分类为正, 而在 jiang_2021/bian_2021/du_2022/you_2018/loughran 五部词典的 ctx 语调净分类为负或中性, 提示该篇文本的分类结果对词典选择敏感, 这类分歧是词典选择敏感性检验中值得单独披露的观察点, 也是本项目坚持六部词典并列而非只保留单一"标准"词典的直接理由——不同词典对同一文本的正面/负面用词识别边界并不完全重合, 单一词典结论存在被词表构造偏好驱动的风险。

## VAR: yao_2021_pos_count_full

【变体差分】
本列取自全文轨 `content_full` (标题 + 报道全文正文, `prepend_title` 拼接), 是 pos_count 家族的默认/主轨测度: bank-year 内 `yao_2021_score_full > 0` 的文章篇数 (方法 D2 篇章级净分类计数)。full 轨同时是留篇门控的唯一判据来源: `llm_verified_full == True` 决定一篇报道是否被计入"确证的银行金科报道"样本, 因此本列所对应的行宇宙即为该门控下的全集, ctx/ss 两轨的行宇宙均是本列行宇宙的子集 (conditional-on-full 的测度/稳健性轨)。在词典消融梯度体系中, full 轨的 `yao_2021_score_full` (本列所依赖的归一化语调分) 是否定翻转/程度副词/转折三规则 powerset 消融变体 (`_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}`) 与最终 `yao_2021_tone_full` 语调分的共同上游中间量, `pos_count_full` 本身则是这条语调分链路末端 (方法 D2 洗稿率前置构造) 对全文轨的净分类聚合, 也是六部词典 (`jiang_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran`) 对称衍生列体系中与本词典对应位置的锚点列。由于 full 轨覆盖全文, 其归一化语调分最容易受到与银行-金科主题无关的段落 (如报道结尾的免责声明、机构简介、无关背景铺陈) 稀释或掺杂噪声, 进而影响 `score_full` 的正负号乃至 `pos_count_full` 的分类结果, 这正是项目同时保留 ctx/ss 两条更聚焦轨道作为互为稳健性并排测度的动机所在: 若某篇文章在 `pos_count_full` 与 `pos_count_ctx`/`pos_count_ss` 上出现方向性背离 (例如 full 轨被判为净正面但 ctx/ss 轨被判为净负面或中性), 提示正面语调的判定可能受与目标银行-金科关系无直接关联的段落影响, 使用者在做因果解释时应结合三轨联合观察而非只依赖 full 轨单一数值。

## VAR: yao_2021_pos_count_ss

【变体差分】
本列取自同句轨 `content_ss` (标题 + 目标银行与金科关键词严格同句 ±N 窗口摘录, `config/filtering.yaml::context_window.ss_sentence_radius` 默认半径 1, 与 stage 13 `cooccurrence_filter.sentence_radius` 是两个不同配置键, 不可混用), 语义上镜像 ctx 轨的回退设计: 当某篇文章不存在银行∧金科同句共现窗口时, `content_ss` 回退为全文 body (与 full 轨文本相同), 由 `ss_is_fallback` 标记该行处于回退状态, 与 ctx 轨共享同一套 `n_articles` 分母口径。ss 轨是三轨中文本跨度通常最窄的一轨 (严格同句而非实体宽窗口), 可供词典打分的上下文信息量因此往往少于 ctx 轨、更少于 full 轨, 三轨在同一篇文章上得到不同的净分类结果, 主要反映窗口宽度差异而非情感强度本身有别。本列与 full/ctx 两轨各自独立完成 jieba 分词、语言学规则加权与 `score_ss > 0` 二值分类, 三轨互不借用彼此的分词结果或分类结果, 是词典法情感测度三轨并排体系 (full/ctx/ss 各自 just-identified、互为稳健性、禁混入同一 over-identified Hansen J) 中的严格判据一端, 供研究者检验"净正面语调判定是否集中在银行-金科直接同句提及处"这一构念收敛问题。ss 轨的严格同句判据与 stage 13 共现硬过滤的判据原语并不相同: stage 13 在 `sentence_radius=1` 的更宽窗口下判定一篇文章是否"保留"进入下游样本, 而本列所依赖的 `content_ss` 是逐篇文本层面另行严格同句摘录, 两处半径配置键彼此独立, 不应混为一谈。当研究设计需要一个对"正面语调是否真正紧贴银行与金科并列提及处"最苛刻的检验时, ss 轨是三轨中信息噪声最小、但样本方差 (受回退比例影响) 也可能最大的一端, 应与 full/ctx 两轨的结果联合报告, 而非单独作为定论依据。

<!-- rendered-citations:begin -->
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision?. Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
<!-- rendered-citations:end -->
