---
family_id: F606
columns:
- washing_ratio_dict
- washing_ratio_dict_ctx
- washing_ratio_dict_ss
unit: 比率 (proportion), 值域 [0,1]; 分子分母同域计数比, 无量纲
formula: 'washing_ratio_dict{track} = dict_pos_symb_count{track} / max(dict_pos_substvalid_count{track}, dict_pos_count{track}); 其中 dict_pos_count{track} 为词典法在该银行-年下的正面篇数加总 —— 判正规则是把 6 部词典各自的 score{track} 取算术平均(_dict_avg = mean of 6 dict scores)、均值 >0 即判正(均值阈值法, 而非并集/OR 逻辑), dict_pos_symb_count{track} 为其中经 innovation_substantiveness_full(tone_llms 多模型 LLM 投票产出的实质/象征分类列)判为象征性(symbolic, 非实质性 substantive)的篇数; 分母取 substvalid 口径(仅计入象征/实质判定有效的样本)与 pos_count 两者中的可用值, 避免除零'
producer: pipeline\panel\runner.py (L2190-L2263, 方法 D「词典均值」洗稿率计算区块, 判正逻辑见 L1017-1026); 标签写入 pipeline\panel\export.py (L1034-L1041); provenance/披露注入 pipeline\panel\codebook.py (L143-L203, _DICT6_AFFECTED_RE)
upstream:
- "pipeline/panel/encode.py::DICT_NAMES 聚合 (dict_pos_count/dict_pos_symb_count/dict_pos_substvalid_count 三轨)"
- "pipeline/sentiment/tone_words.py (词典法逐词典打分 {dict}_score{track})"
- "pipeline/panel/runner.py 内联读取 innovation_substantiveness_full (tone_llms 多模型 LLM 投票产出的实质/象征二分类列, 非独立规则模块)"
citations:
- {doi: "10.1093/rof/rfab036", type: journal, authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W.", year: 2022, title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary", venue: "Review of Finance", vol: "26", issue: "3", pages_or_artno: "673-719"}
- {doi: "10.2307/2393295", type: journal, authors: "Westphal, J. D., & Zajac, E. J.", year: 1994, title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans", venue: "Administrative Science Quarterly", vol: "39", issue: "3", pages_or_artno: "367-390"}
- {doi: "10.2307/2393593", type: journal, authors: "Westphal, J. D., & Zajac, E. J.", year: 1998, title: "The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions", venue: "Administrative Science Quarterly", vol: "43", issue: "1", pages_or_artno: "127-153"}
- {doi: "10.1111/j.1540-6261.2010.01625.x", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2011, title: "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks", venue: "The Journal of Finance", vol: "66", issue: "1", pages_or_artno: "35-65"}
- {doi: "10.1287/mnsc.2021.4156", type: journal, authors: "Frankel, R., Jennings, J., & Lee, J.", year: 2022, title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods", venue: "Management Science", vol: "68", issue: "7", pages_or_artno: "5514-5532"}
- {doi: "10.1111/eufm.12509", type: journal, authors: "Gorovaia, N., & Makrominas, M.", year: 2024, title: "Identifying Greenwashing in Corporate-Social Responsibility Reports Using Natural-Language Processing", venue: "European Financial Management", vol: "31", issue: "1", pages_or_artno: "427-462"}
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_dict 测度的是银行-年层面"媒体正面报道中有多少比例只是象征性表态而非实质性举措"的洗稿(washing)倾向, 是本项目「媒体质量」测度体系中词典法(dictionary-based)一支的核心产出。其理论根基是组织理论中的实质与象征区分(substance-symbolism distinction): Westphal & Zajac (1994, ASQ) 首先在公司治理语境下指出, 企业采纳某项治理安排(如长期激励计划)可能是"实质性"地真正改变行为, 也可能只是"象征性"地对外释放合规信号而不改变实际决策; 其后续研究 (Westphal & Zajac 1998, ASQ) 进一步证明股东回应会区分这两类采纳行为的市场反应。本项目把这一区分从"公司治理安排是否落地"迁移到"媒体报道的正面内容是否对应实质性业务/风险变化", 用来诊断银行与金融科技相关报道中是否存在系统性的"表态多于行动"现象, 呼应更广义的文本洗白(washing)研究传统 —— 如企业通过语言操纵而非实质改善来管理外部印象 (Bingler, Kraus, Leippold & Webersinke 式的 washing 测度思路; 亦见 Gorovaia & Makrominas 2024, European Financial Management, 关于企业社会责任报告中 greenwashing 的自然语言处理识别方法)。

washing_ratio_dict 是"词典均值"(Dict-Avg)口径的洗稿率, 与家族外的 washing_ratio(LLM 投票)、washing_ratio_bert(BERT 均值)、washing_ratio_hc(高置信度子样本)以及逐词典的 washing_ratio_{dict}(如 washing_ratio_du_2022)并列, 构成同一构念下按"判正引擎"划分的多方法矩阵。词典法与 LLM 投票、BERT 分类三者是互为稳健性、不分主次的并排测度: 词典法在"是否正面"这一判定环节的优势是规则驱动、可复算、无模型漂移风险, 代价是对语境和反讽的敏感度不如 LLM/BERT; 但须澄清, washing_ratio_dict 的分子还依赖另一半判定——象征/实质二分类, 该分类取自 innovation_substantiveness_full 列, 由 tone_llms 多模型 LLM 投票产生, 并非独立的规则引擎输出, 因此本列并非端到端"完全规则驱动、无模型漂移风险"的纯词典测度, 而是"词典法判正 × LLM 判实质/象征"的混合口径, 与家族外的 washing_ratio(LLM 判正 × LLM 判实质/象征)、washing_ratio_bert(BERT 判正 × 同一 LLM 判实质/象征)共享同一套象征/实质分类底座, 三法并排差异集中于"是否正面"这一判正引擎, 而非实质/象征分类本身; 三法并排恰是为了避免结论依赖单一判正引擎的人工选择。词典法内部本身又依赖 6 部词典(jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran)的均值判正规则(取 6 部词典 score 的算术平均、均值大于零即判正, 是均值阈值法而非任一词典判正即计入的并集/OR 逻辑), 其中第 6 部 Loughran-McDonald(2011, JF)中文主译本是 v3.10.0 新接入(词表由 5 部扩为 6 部), 使本列及其同前缀的跨词典均值族发生了有意的、经审计披露的测度口径变更(详见【方法学与计算】)。上文所称"词典法完全规则驱动"仅指分子分母中"是否正面"这一半判定 —— 象征/实质二分类本身取自 innovation_substantiveness_full 列, 该列由 tone_llms 多模型 LLM 投票产生, 并非本项目自建的规则引擎输出, 因此 washing_ratio_dict 整体上仍部分依赖 LLM 分类结果, 并非"无模型漂移风险"的纯规则测度, 详见【方法学与计算】的澄清。

【方法学与计算】
washing_ratio_dict 的计算发生在银行-年面板聚合之后的派生计算区块(pipeline/panel/runner.py 「方法 D: 词典均值」), 而非文章级逐篇计算, 这与家族命名中的"dict"含义一致——它不是某一部词典的洗稿率, 而是把 6 部词典各自的 score{track} 先在文章级取算术平均、均值大于零即判正(_dict_avg = mean(6 部词典 score); _dict_pos = _dict_avg > 0, 是均值阈值法, 而非任一词典判正即计入的并集/OR 逻辑), 再在银行-年层面汇总计数, 最后取比率。具体地:
第一步, 文章级由词典法(tone_words 规则引擎)对每篇报道逐词典打分(_{dict}_score), runner.py 把 6 部词典的分数取算术平均得到 _dict_avg_score, 均值大于零判为 _is_dict_positive; 与此同时, 每篇文章的实质/象征二分类取自 innovation_substantiveness_full 列(该列不是本项目自建的独立规则模块, 而是由 tone_llms 多模型 LLM 投票产生, 详见 CLAUDE.md「LLM 三家互为稳健性」条目), 判为"象征性"标签的文章记为 _is_symb, 与 _is_dict_positive 相与得到 _is_dict_pos_symb(词典判正且属象征性)标记。
第二步, 银行-年聚合把这些文章级标记求和: dict_pos_count{track} = 该银行-年内词典均值判正(6 部词典 score 均值 >0)的报道篇数, dict_pos_symb_count{track} = 其中被判为象征性的篇数, dict_pos_substvalid_count{track} = 象征/实质判定本身有效(非缺失)的正面报道篇数(用作更严格的分母候选)。
第三步, washing_ratio_dict{track} = dict_pos_symb_count{track} 除以 svd_denom(dict_pos_substvalid_count{track}, dict_pos_count{track})。svd_denom 是一个安全取分母的辅助函数: 优先使用 substvalid 计数(把象征/实质判定缺失的正面报道排除在分母外, 是更严格的口径), 该计数不可用或为零时回退到 pos_count 本身; 分子分母同为零时比率记为缺失(NaN)而非人为置零, 避免把"没有正面报道"误读为"洗稿率为零"。比率值域理论上落在 [0,1], 数值越高表示该银行-年的正面涉银行金科报道中"言过其实"(表态多于实质)的比例越大。
washing_ratio_dict 存在三轨版本(无后缀 full / _ctx / _ss), 对应本项目情感三轨文本口径体系: full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行与金科同句(±N 句窗)共现文本; 三者共享同一套判正与实质/象征分类规则, 唯一差异是喂给规则引擎的文本片段不同(见【VAR】各节)。三轨口径必须各自 just-identified 并排使用、互为稳健性、不分主次, 严禁把三轨列混入同一 over-identified Hansen J 检验。此外, 词典法本身依赖的词典集合在 v3.10.0 由 5 部扩为 6 部(接入 Loughran-McDonald 2011 中文主译本), 这是一次有意的、经内部审计(scripts/audit/measure_dict_union_impact.py)量化过的测度口径变更; 该审计脚本名中的"union"指的是构造合并词表(build_union_dictionary, 多部词典词条合并为单一词表用于计算 msent_score)的词表级并集, 与 washing_ratio_dict 判正逻辑本身(6 部词典 score 取均值判正, 非任一词典判正即计入)是两个不同层面的"union", 不应混淆; 实测 5 部与 6 部词表并集口径的 msent_score 相关系数 r=0.985, 符号翻转率仅 0.13%, 均值级微变约 3.5%, 反映词表覆盖面的改善而非方法误差; 该披露通过列名前缀匹配(_DICT6_AFFECTED_RE, 命中 washing_ratio_dict 及其 _ctx/_ss 变体但不命中逐词典的 washing_ratio_{dict} 单列, 因为后者是"新增列"而非"变值列")机械注入到本列的 codebook 元数据备注中, 使用者在解读跨版本(v3.9.x 之前 vs v3.10.0 之后)数值差异时应留意这一有意的测度演进而非误判为 bug。

【文献定位】
本列在测度谱系上处于两条文献脉络的交点。其一是媒体文本情感测度的词典法传统: Loughran & McDonald (2011, The Journal of Finance) 建立了金融文本专用词典分析范式, 证明通用情感词典(如 Harvard IV-4)在金融/监管文本上会产生系统性误判, 需用领域专属词表; Du, Huang, Wermers & Wu (2022, Review of Finance) 进一步针对中文金融文本构建专属情感词典(本项目 DICT_NAMES 中的 du_2022), 是本项目词典法判正规则的直接方法学来源之一, 也是本家族「词典均值」聚合口径下六部词典之一。其二是实质与象征区分传统: Westphal & Zajac (1994; 1998, 均刊于 Administrative Science Quarterly) 首创并检验了公司治理采纳行为的实质/象征二分框架, 本项目把该框架用于对媒体报道内容(而非公司治理安排本身)做实质/象征分类, 从而把"正面报道占比"进一步细分为"实质性正面"与"象征性正面", 洗稿率即后者在全部正面报道中的占比。两条脉络的合流呼应了近年"文本洗白"(washing)研究的兴起, 如 Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法从企业社会责任报告中识别 greenwashing 现象; 本项目将同一逻辑迁移到银行-金融科技媒体报道语境, 用洗稿率捕捉"媒体渲染的正面形象"与"报道实际反映的业务/风险实质"之间的落差。最后, 词典法与机器学习/LLM 判正法孰优孰劣一直是文本情感测度领域的方法学争论焦点, Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习与词典法在信息披露情感测度上的表现差异, 是本项目坚持词典法/LLM/BERT 三法并排、互为稳健性设计的直接方法学依据 —— washing_ratio_dict 正是这一"三法并排"矩阵中词典法一支的银行-年层面代表性产出。

## VAR: washing_ratio_dict

【变体差分】
本列是家族的 full 轨、无后缀 canonical 变体, 对应银行-年层面全文本口径的词典法洗稿率。其规则引擎输入是 stage 14 物化的 content_full 文本(标题+正文全文, prepend_title 拼接), 不做实体窗口或同句截取。分子 dict_pos_symb_count_full 与分母候选 dict_pos_substvalid_count_full / dict_pos_count_full 均取自同一 full 轨聚合列, 计算公式与家族公式完全一致(track='_full', 后缀为空字符串)。作为三轨中信息量最完整的一支, full 轨覆盖了报道全文的所有正面表态与实质细节, 因而是三轨中样本量(有效正面报道篇数)通常最大、统计功效最高的一支, 但也最容易把与目标银行/金科主题弱相关的正面段落计入分子分母, 引入一定的主题稀释噪声。该列与 washing_ratio_dict_ctx、washing_ratio_dict_ss 三者互为稳健性并排使用, 不设主次之分, 三者在实证中应分别独立进入回归设定或稳健性表格, 禁止混入同一 over-identified 的 Hansen J 过度识别检验框架。在本项目多数 paper 模块的主回归设定中, full 轨因样本量最大、覆盖面最广而常被选作报告的首要口径, 但这只是呈现顺序上的惯例, 并非方法论上的优先地位, 三轨的统计地位在设计上完全对等。留篇门控(是否计入"一篇银行金科报道")遵循 full-only 口径(2026-06-29 起生效): 一篇文章能否进入 washing_ratio_dict 系列的任一轨分母, 取决于其 llm_verified_full 是否为 True, ctx/ss 两轨的样本行宇宙是 full 轨留篇集合的条件子集, 而非各自独立的留篇标准。

## VAR: washing_ratio_dict_ctx

【变体差分】
本列是三轨中的 ctx(context, 实体窗口)变体, 规则引擎输入是 stage 14 物化的 content_ctx 文本, 即"标题 + 目标银行/金科实体周边窗口文本", 而非全文。相较 full 轨, ctx 轨通过截取实体邻近上下文降低了主题稀释噪声, 使判正与实质/象征分类更聚焦于报道中直接涉及目标银行与金融科技的语段, 代价是可用文本量变小, 部分本来能在全文中找到实质性描述的报道, 在窗口截取后可能只剩表态性语句, 从而使象征占比的估计对窗口半径参数更敏感。计算公式与家族公式一致, 仅将 track 换为 '_ctx', 列名后缀相应为 '_ctx': washing_ratio_dict_ctx = dict_pos_symb_count_ctx / svd_denom(dict_pos_substvalid_count_ctx, dict_pos_count_ctx)。ctx 轨与 full、ss 两轨互为稳健性并排, 不分主次; 留篇门控仍以 full 轨的 llm_verified_full 为准, ctx 轨行宇宙是该留篇集合的条件子集, 本轨自身不单独决定一篇文章是否计入洗稿率分母。使用者在比较 full 与 ctx 两轨数值差异时, 应把差异理解为文本截取粒度不同带来的规格稳健性证据, 而非孰对孰错的取舍问题; 若两轨方向一致仅幅度有别, 通常支持洗稿率结论对文本窗口选择不敏感。若 stage 14 未能在报道中定位到银行/金科实体窗口(极端情形下), 该篇在 ctx 轨的判正与分类仍按 content_ctx 的兜底文本(标题+可得片段)计算, 不会跨轨借用 full 轨的分子分母, 保持三轨口径的严格独立并排。实务上 ctx 轨常被用作 full 轨的首要稳健性对照, 在解读回归系数时应同时报告两轨结果并说明方向与显著性是否一致, 而非仅呈现其中一轨。

## VAR: washing_ratio_dict_ss

【变体差分】
本列是三轨中的 ss(same-sentence, 同句)变体, 规则引擎输入是 stage 14 物化的 content_ss 文本, 即"标题 + 目标银行与金融科技词在同一句(±N 句窗, 默认 N=1, 见 config/filtering.yaml::context_window.ss_sentence_radius)共现"的文本片段, 是三轨中文本粒度最细、判据最严格的一支。ss 轨遵循镜像 ctx 的回退语义: 当一篇报道中不存在银行与金科的同句共现时, content_ss 回退为全文 body, 对应的 ss_is_fallback 标记置为 True, 该行仍共享与 ctx/full 一致的 n_articles 分母口径, 不会因回退而被排除出样本; 若上游 FINTECH_AC 词典对象为 None(极端配置缺失情形), 则 *_is_fallback 全部置 True, 各轨优雅降级为等价于全文口径。计算公式同样只是把家族公式中的 track 换为 '_ss': washing_ratio_dict_ss = dict_pos_symb_count_ss / svd_denom(dict_pos_substvalid_count_ss, dict_pos_count_ss)。由于同句共现是三种判据中最严格的一种, ss 轨样本量通常小于 ctx 轨与 full 轨, 且更容易受个别句子措辞风格影响而产生方差, 使用时应结合 full/ctx 两轨交叉验证结论稳健性, 三轨仍是各自 just-identified 并排、互为稳健性、不分主次的关系, 禁止混入同一过度识别的 Hansen J 检验。留篇门控同样以 full 轨的 llm_verified_full 为准, ss 轨行宇宙是该留篇集合的条件子集。ss 轨的价值在于最大限度剔除"银行与金科各自出现但语义无关"的假阳性共现, 因而在需要严格因果归因(而非广义主题覆盖)的场景下是三轨中判据最保守、最不易高估洗稿率的一支。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Gorovaia, N., & Makrominas, M. (2024). Identifying Greenwashing in Corporate-Social Responsibility Reports Using Natural-Language Processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
<!-- rendered-citations:end -->
