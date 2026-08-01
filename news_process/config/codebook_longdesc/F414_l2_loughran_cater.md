---
family_id: F414
columns:
- loughran_cater_ctx
- loughran_cater_full
- loughran_cater_ss
unit: 无量纲差分 (两个已归一化情感测度的算术差, 值域约 [-2, +2])
formula: 'loughran_cater_{track} = loughran_tone{track} - llm_vote_tone{track} (bank-year
  面板层面对差, track ∈ {full, ctx, ss}); 其中 loughran_tone{track} 是词典 loughran (L&M
  2011 JF 中文主译本) 的逐篇 msent 式归一化得分聚合到 bank-year 的均值, llm_vote_tone{track}
  是三家 LLM (gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 多数投票共识语调聚合到
  bank-year 的均值'
producer: pipeline\panel\runner.py (8d algo_cater 步骤, panel[f'{d}_cater{track}'] =
  panel[d_col] - panel[lc]) ; 上游词典打分 pipeline\sentiment\tone_words.py ; 上游 LLM
  投票 pipeline\sentiment\tone_llms.py
upstream:
- loughran_tone_full
- loughran_tone_ctx
- loughran_tone_ss
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: 'Textual analysis in accounting and finance: A survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187-1230
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: Textual analysis in finance
  venue: Annual Review of Financial Economics
  vol: '12'
  issue: '1'
  pages_or_artno: 357-375
- doi: "10.1016/j.frl.2024.105227"
  title: "Sentiment trading with large language models"
  authors: "Kirtac, K., & Germano, G."
  year: 2024
  venue: "Finance Research Letters"
  type: "journal"
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
new_dois:
  - "10.1016/j.frl.2024.105227"
  - "10.1002/isaf.1549"
---

## CORE

【构念与来源】
本家族三列衡量的不是情感水平本身, 而是"两种独立测量工具对同一篇报道语调判断之间的系统性分歧", 借用会计与金融文献里"算法迎合" (algorithmic catering) 这一构念名。母概念来自两支并行文献: 一支关注管理层/媒体在知道存在自动化文本分析工具会读取披露文本时, 是否倾向于调整措辞去"迎合"该工具的打分规则 (词典法作为廉价、规则透明、易被针对性措辞影响的浅层工具); 另一支关注深度学习/大语言模型情感分类器相对词典法在语义消歧、反讽识别、上下文理解上的相对优势, 由此产生"词典读数系统性偏离深层模型读数"的可预测缺口。本项目把该缺口构造成显式面板列: 对每个 bank-year 观测, 用词典 6 部之一 (loughran, 即 Loughran & McDonald 2011 JF 词表的中文主译本 loughran_mcdonald_zh_2026, 经列前缀别名映射为 'loughran') 的语调均值, 减去三家 LLM 多数投票共识语调均值, 得到一个有符号差分。差分为正, 说明该词典在该银行-年份的报道语料上系统性地比 LLM 共识更"看多"(更正面); 差分为负, 说明词典系统性更"看空"。差分本身不判断哪一方"更准", 它衡量的是工具间分歧的方向与幅度, 是一种测量方法学诊断量, 而非独立的经济构念。
本列名里的 "loughran" 精确指代 config/tone_dicts.json 中 loughran_mcdonald_zh_2026 词典 (L&M 2011 Journal of Finance 原创英文金融词典的中文主译本; positive 1,295 词 / negative 3,729 词, 另含 5 类非极性词类如不确定性/诉讼/弱模态等未在本情感打分中启用)。该词典与项目内其余 5 部中文金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018) 并列, 各自独立打分、互不覆盖, 6 部词典各有一套同构的 {dict}_cater{track} 三轨列 (loughran_cater_* 是其中一套); 本 codebook 家族仅覆盖 loughran 对应的三列。

【方法学与计算】
分子 loughran_tone{track}: 逐篇匹配 loughran 词典的正/负词条 (含否定翻转/程度副词/转折三条语言学规则的 canonical 组合, 即 "full" 规则组), 得到 total_score (加权符号和) 与 total_abs_score (加权幅度和), 归一化为 normalized_score = total_score / total_abs_score ∈ [-1, +1] (total_abs_score=0 时记 0.0, 表示语调中性/无匹配)。该逐篇归一化得分再按 bank-year 聚合 (均值) 得到面板列 loughran_tone{track}。
分母侧参照 llm_vote_tone{track}: 三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 对每篇文章独立打出三分类或连续语调判断, 经多数投票共识后聚合到 bank-year, 得到 llm_vote_tone{track}。该共识列是 P1 (bank_fintech_tone) 论文的主处理变量 (treatment.primary), 已切至 full-only 门控 (2026-06-29): 是否判定"一篇文章属于目标银行-金科报道"这一留篇标准, 只由 full 轨的 LLM 验证结果 (llm_verified_full == True) 决定, ctx/ss 是 conditional-on-full 的测度轨/稳健性轨, 行宇宙是 full 留篇集的子集, 而非独立留篇口径。
本家族 三 列 的差分公式即为 loughran_cater{track} = loughran_tone{track} - llm_vote_tone{track}, 在 runner.py 8d 步骤按 track 循环、逐词典 (DICT_NAMES 含 loughran) 计算; 只在分子分母两列均存在于面板时才写入 (存在性守卫, 缺一不写, 不做 NaN 填充式的"伪计算")。
三轨 full/ctx/ss 分别对应: full=标题+正文全文语料, ctx=标题+实体窗口语料, ss=标题+银行∧金科同句±N窗语料 (无同句共现时回退为全文, 与 ctx 回退语义镜像, 回退标记 ss_is_fallback 共享 n_articles 分母)。三轨测度各自独立计算、并排存在, 互为稳健性检验、不分主次 — 不存在"以 full 为主、ctx/ss 为附属"的层级关系; 计量应用中三轨绝不可混入同一 over-identified 的 Hansen J 过度识别检验 (三轨各自 just-identified 并排使用)。

【文献定位】
词典法与深度学习/LLM 情感分类器之间的系统性差异是文本分析方法学文献长期关注的议题: Frankel, Jennings & Lee (2022, Management Science) 直接比较了机器学习方法与词典法在披露语调测量上的分歧及其经济含义, 是本家族"以差分作为诊断量而非独立构念"这一设计取向最直接的方法学先例。Loughran & McDonald (2011, Journal of Finance) 提出的金融专用词典 (即本家族依赖的 loughran 词表母本) 本身已经证明通用情感词典 (如 Harvard IV-4) 系统性误判金融文本语调, 说明"词典选择/词典与语料领域匹配度"本身就是分歧的一个来源; Loughran & McDonald (2016, Journal of Accounting Research; 2020, Annual Review of Financial Economics) 进一步综述了会计金融文本分析中词典法的适用边界与常见误用, 为解释 loughran_cater 差分的可能来源 (词典规则粗糙 vs 语料本身歧义) 提供了方法论背景。Kirtac & Germano (2024, Finance Research Letters) 比较基于大语言模型(如GPT系列)与传统词典法在金融文本情感提取及其对股票收益预测能力上的差异, 发现LLM情感信号显著优于词典法, 为本家族"词典-LLM 迎合度差分"提供最新的方法学对照证据。Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融领域文本情感分析技术谱系(词典法、机器学习、深度学习/大语言模型), 梳理不同测量工具间系统性分歧的成因与研究趋势, 为本家族词典-LLM 差分构念的文献定位提供最新综述支撑。

## VAR: loughran_cater_full

【变体差分】
本列是 full 轨 (标题+正文全文) 上的词典-LLM 迎合度差分: loughran_cater_full = loughran_tone_full - llm_vote_tone_full。两侧输入均取全文语料上的判断, 是三轨中信息量最完整、也是留篇门控 (llm_verified_full) 直接锚定的一轨。由于 P1 论文主处理变量 llm_vote_tone_full 是 full-only 门控下的 canonical headline 测度, 本列可视为词典与"主口径" LLM 判断之间分歧的直接刻画, 在三轨并排稳健性检验中处于与 ctx/ss 完全对等的地位 (不因门控锚定而被赋予额外权重), 仅是解释时最贴近"全文完整语境下两工具读法差多少"这一直觉。若某 bank-year 观测在该轨下 loughran_tone_full 与 llm_vote_tone_full 任一缺失 (如该年无留篇文章、或词典/LLM 分聚合结果为 NaN), 本列同样缺失, 不做插补。
从计算路径看, loughran_tone_full 的输入文本是 stage 14 物化的 content_full (标题 prepend 至正文), 逐篇经 loughran 词典打分 (含否定翻转/程度副词/转折三条规则的 full 组合, 与消融梯度中 raw/negonly/degonly/advonly 等非-full 变体是并排关系, 本列固定取 full 规则组、不随消融梯度变化); llm_vote_tone_full 的输入是三家 LLM 各自读取同一份 content_full 文本后的独立判断, 经多数投票消解为单一共识值。两侧文本源相同, 判读机制完全独立 (规则词典 vs 语言模型), 因此本列差分不受文本口径不一致这一混淆因素污染, 纯粹反映判读机制层面的分歧, 是解释词典法相对深度模型系统性偏差的最干净一轨。实践中该列可用于诊断: 若某银行在特定年份该列持续偏正, 提示相关报道中存在词典能识别、但 LLM 未同等加权的正面措辞模式 (例如套话式褒义形容词堆砌); 持续偏负则提示词典可能漏判 LLM 能捕捉到的反讽或条件性负面表述, 属于测量工具选择敏感性的直接证据, 应在使用 loughran_tone_full 作为稳健性替代测度时一并披露。

## VAR: loughran_cater_ctx

【变体差分】
本列是 ctx 轨 (标题+实体窗口语料) 上的词典-LLM 迎合度差分: loughran_cater_ctx = loughran_tone_ctx - llm_vote_tone_ctx。ctx 轨截取的是围绕目标实体 (银行/金科词) 的局部窗口文本而非全文, 意味着词典打分与 LLM 打分所依赖的原始文本片段本身比 full 轨更短、更聚焦, 分歧的来源可能既包含"两种方法对同一段文本判读不同", 也包含"实体窗口截取本身引入的语境损失对两种方法的不对称影响" (例如词典法对局部窗口中缺失的转折/让步从句更敏感, 因为否定翻转/转折规则依赖句内邻近词序)。该轨的留篇行宇宙是 full 轨留篇集的子集 (conditional-on-full, 2026-06-29 门控切换后口径), 并非独立样本; 与 loughran_cater_full 互为稳健性并排, 不构成对后者的从属或修正。
ctx 轨的一个具体特点是: 实体窗口截取由 stage 14 ctx_materializer 在 stage 21 情感打分之前物化, 窗口边界由 config/filtering.yaml 中的实体识别与窗口长度参数控制, 与 stage 13 共现硬过滤 (只保留银行∧金科邻近共现的文章) 是两个不同环节 — stage 13 决定"这篇文章要不要保留在语料里", stage 14 决定"保留下来的文章里, ctx 轨具体截取哪一段文本喂给词典/LLM"。因此 loughran_cater_ctx 的分歧不仅来自词典与 LLM 两种判读机制的固有差异, 还叠加了窗口截取对两种机制的不对称影响: LLM 具备一定的指代消解与跨句语义整合能力, 在窗口边界切断某些从句时表现相对稳健; 词典法逐词匹配, 对窗口边界切断否定词/转折连词所在从句更为敏感, 容易在窗口截断处产生极性误判。使用该列做研究设计时应留意: ctx 轨窗口越窄, 词典法产生的边界效应误差理论上越大, 该列偏离 0 的幅度部分反映窗口设计本身的粗糙度, 而非纯粹的语料语调分歧, 建议与 loughran_cater_full/loughran_cater_ss 联合解读而非单独使用。

## VAR: loughran_cater_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句±N窗语料, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 上的词典-LLM 迎合度差分: loughran_cater_ss = loughran_tone_ss - llm_vote_tone_ss。ss 轨要求银行实体与金科词在同一句 (或其 ±1 句窗口) 内共现才纳入该轨专属文本, 是三轨中语境窗口最窄、判据最严格的一轨; 当某篇文章不存在这种同句共现时, 回退语义镜像 ctx 轨 — content_ss 退化为全文 body, ss_is_fallback 标记为 True, 且与 ctx 共享同一套 n_articles 分母口径, 而非另起炉灶的独立分母。因此本列在词典/金科词共现极稀疏的样本 (如小样本早期试跑 T=2 开发集) 上可能大量退化为与 full 轨高度重合的取值, 生产语料 (T=19 全量) 上才能体现同句窄窗口下的真实分歧。与 loughran_cater_full / loughran_cater_ctx 三者并排、互为稳健性, 禁止混入同一 over-identified 的 Hansen J 设定。
ss 轨的判据是"银行实体与金科词是否落在同一句 (或其 ±1 句窗口)"这一比 ctx 轨更严格的共现要求, 判据原语与 stage 13 共现硬过滤所用的 ±1 句窗口判据 (has_bank_fintech_cooccurrence_within_radius) 在参数上接近但函数入口不同, 二者不可互相复用。当同句共现存在时, content_ss 是三轨中语境最窄、信噪比理论上最高的一段文本, 此时 loughran_cater_ss 反映的是"银行与金科词紧邻共现的那一句话"层面的词典-LLM 分歧, 比 full/ctx 两轨更贴近"这句话具体在说什么"这一微观语境; 当同句共现不存在而触发回退时, content_ss 与 content_full 完全相同, 此时 loughran_cater_ss 与 loughran_cater_full 应在数值上高度重合甚至字节相同 (两侧词典打分与 LLM 打分的输入文本一致)。这一回退结构意味着解读 loughran_cater_ss 时必须结合 ss_is_fallback 标记: 若某 bank-year 的绝大多数留篇文章都触发回退 (语料中银行∧金科同句共现稀少, 常见于早期试跑 T=2 开发集小样本), 该列的稳健性检验价值会明显下降, 应以生产语料 (T=19 全量) 下的取值为准。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters. https://doi.org/10.1016/j.frl.2024.105227
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
