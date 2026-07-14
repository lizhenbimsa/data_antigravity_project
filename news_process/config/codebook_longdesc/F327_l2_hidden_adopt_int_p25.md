---
family_id: F327
columns:
- hidden_adopt_int_p25
- hidden_adopt_int_p25_ctx
- hidden_adopt_int_p25_ss
unit: 占比 (0-1), bank-year 内已测量文章中归入"隐性采纳"象限的份额
formula: 'per-article 指示 hidden_int_p25 = 1{fintech_intensity_score < P25(year) AND policy_cosine_sim >= P25(year)} (双双非缺测行), 否则 NaN; bank-year 聚合 hidden_adopt_int_p25 = groupby(target_bank, year)[hidden_int_p25].mean() (NaN 跳过, 分母=已测量篇数)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (聚合于 runner 步骤 7h-token 四象限循环)
upstream:
- 15_article_policy_alignment.parquet (policy_cosine_sim / fintech_intensity_score)
- 24_herd_decay.parquet (verified 语义精筛域, semi-join 对齐)
citations:
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: 'Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations'
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306-333
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: 'Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: 10.1016/j.irfa.2014.02.006
  type: journal
  authors: Kearney, C., & Liu, S.
  year: 2014
  title: 'Textual sentiment in finance: A survey of methods and models'
  venue: International Review of Financial Analysis
  vol: '33'
  pages_or_artno: 171-185
- doi: 10.1016/j.econmod.2023.106445
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: 'Bank fintech, liquidity creation, and risk-taking: Evidence from China'
  venue: Economic Modelling
  vol: '127'
  pages_or_artno: '106445'
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行—年度层面"报道话语与金融科技政策的隐性对齐"占比: 一篇报道若金融科技关键词密度(强度)不高、但其文本语义与监管/产业政策文件的余弦相似度却高, 即被判为"隐性采纳" (hidden adoption) —— 报道并不高频堆砌金融科技热词, 但其叙事方向已经与政策话语同频。这是 stage 15 (`article_policy_alignment`) 产出的逐篇政策对齐分数 `policy_cosine_sim` 与逐篇金融科技强度分数 `fintech_intensity_score` 交叉构造的四象限分类之一(另三格为 `token_adopt`「高频堆词但不像政策」、`subst_adopt`「既高频又像政策」、以及未命名的第四格「低频且不像政策」——后者不产出独立列, 是象限分类下的"沉默"补集)。四象限的构造哲学呼应组织理论对"象征性采纳(symbolic/decoupled adoption)"与"实质性采纳(substantive adoption)"的经典区分: 组织/媒体话语层面的采纳意愿表达(词频)与其实际制度嵌入深度(与既定政策议程的语义贴合度)未必同步, "隐性"格恰是话语稀薄却语义趋同的一类, 常见于报道并未直接罗列"金融科技""区块链""开放银行"等术语、却在叙事框架(风控、普惠、监管科技合规)上已复述政策原文语汇的文章。家族名 `hidden_adopt` 中的 `hidden` 取此"隐而不显"之义, 区别于 `token_adopt` 的"显而不实"。
本家族属 `pending_external_financial_dvs` 之外的机制检验/稳健性测度族, producer 定位在 `pipeline/panel/runner.py::_classify_policy_quadrants` 与其外层的 Track/百分位双重循环 (runner 步骤 7h-token, 紧随 `article_sim_mean`/`fintech_intensity_mean` 连续型聚合之后)。逐篇指示列先在文章层生成 (`_is_hidden_{...}` 临时列, 不落文章级 parquet), 再按 `(target_bank, year)` groupby mean 聚合为占比, 随即由 runner 主流程 drop 掉临时列, 只保留聚合后的面板列。

【方法学与计算】
family 内的 `int_p25` 三字面对应两个正交的构造维度: `int` 表示词频侧使用 Track B (强度测度 `fintech_intensity_score`, TF-IDF × SIF 加权连续分数, 与 Track A `kw`——`fintech_distinct_keywords` 原始去重关键词计数——互为稳健性并排, 见姊妹家族 `token_adopt_kw_*`/`hidden_adopt_kw_*`); `p25` 表示年度内以 25 百分位数作为高/低分割阈值 (与 `p50`/`p75` 互为稳健性并排, `p50` 是机制检验基准分割、`p25`/`p75` 是稳健性检验的非对称分割)。分类算法逐年独立计算: 对 `policy_cosine_sim` 与 `fintech_intensity_score` 各自在当年样本内取分位数变换 (`groupby('year').transform(quantile)`), 再逐篇比较该篇实际值是否 ≥ 当年阈值, 得到 `high_sim`/`high_freq` 两个布尔量; `hidden = (~high_freq) & high_sim`。仅当 `policy_cosine_sim` 与所用词频列同时非缺测的行才参与分类, 其余行指示值置 NaN 而非 False——这是 2026-06-11 的 `omni-g-runner-03/g-runner-11` 修复: 旧实现把测量失败 (stage 15 优雅早退写出的全 NaN `policy_cosine_sim`) 静默当作"低对齐", 导致高词频文章批量误判为 `token`; 现在未测量的文章在 bank-year 聚合的 `.mean()` 中被自动跳过, 分母是"当年当行已测量篇数", 而不是全部报道篇数——这与本项目对情感/网络类"率/均值"测度的统一契约一致 (无数据=未测量=NaN, 不强填零, 避免 Allison 2001 §3 所述的伪零污染双向固定效应估计)。
分类前置的行域也经过一次域对齐: `_filter_to_verified_universe` 把 stage 15 的候选集 (stage 14 规则预筛, 可能含 26.8% 的 LLM 验证未通过的假阳性文章) 通过 `(docid, target_bank)` 半连接收敛到 stage 24 (`24_herd_decay`) 的语义精筛 verified 集, 使四象限族与项目内其余全部文本测度共享同一聚合域, 不再因未验证文章污染分位阈值与占比分母。
canonical (无 `_ctx`/`_ss` 后缀) 的相似度输入取全文轨 `policy_cosine_sim` (对应 full-only 留篇门控口径, 2026-06-29 起), `hidden_adopt_int_p25_ctx` 与 `hidden_adopt_int_p25_ss` 是把相似度输入替换为 `policy_cosine_sim_ctx`/`policy_cosine_sim_ss` (标题+实体窗口 / 标题+银行∧金科同句窗口) 后的孪生构造; 三轨在同一行宇宙(留篇门控=full-only 确定的 verified 集)上各自独立计算, 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨系数混进同一 over-identified Hansen J 设定。词频侧 (`fintech_intensity_score`) 若存在同轨变体 (`fintech_intensity_score_ctx`/`_ss`) 则优先使用同轨版本, 否则退化复用全文版本 (代码注释标注为"词频列无同轨变体 (track-agnostic)"的优雅降级, 而非静默 NaN)。`_ss` 轨遵循与 `_ctx` 相同的镜像回退语义: 当某篇文章不存在银行∧金科同句共现时, 其 `content_ss` 回退为全文正文 (`ss_is_fallback=True`), 但该回退发生在 stage 15 政策相似度打分与 stage 14 文本物化层, 四象限分类本身只负责消费已算好的 `policy_cosine_sim_ss` 列, 不重复处理回退逻辑。
另需注意: 家族内三列共享的 `_p25` 阈值percentile 与三轨后缀是两个独立、正交的梯子——三轨表示"用哪段文本算相似度", `p25/p50/p75` 表示"用多严的分位数门槛切高低"; 二者笛卡尔积展开为多个姊妹家族 (`hidden_adopt_int_p50*`/`hidden_adopt_int_p75*` 等), 互不嵌套、互为稳健性。

【文献定位】
四象限"话语-实质"缺口构造的理论根基可追溯到组织与创新管理文献对采纳行为"符号性/实质性"二分的长期关注: Adner & Kapoor (2010, *Strategic Management Journal*) 在创新生态系统框架下指出企业间技术互依结构会造成采纳节奏(话语宣示 vs. 实际部署)与技术代际成熟度的错配, 为本项目把"报道频率高不代表制度嵌入深"这一直觉形式化为可分类构念提供了生态系统层面的理论支撑。政策对齐分数本身的构造与解释依据 Distel 等 (2026, 源码注释) 的文章级政策—银行余弦相似度方法, 本家族是该连续测度的离散化机制检验分支。方法学层面, 文本情感/主题类测度的"多测度并排作稳健性"惯例参见 Todd, Bowden & Moshfeghi (2024, *Intelligent Systems in Accounting, Finance and Management*) 对金融文本情感分析文献的系统综述, 及 Kearney & Liu (2014, *International Review of Financial Analysis*) 对文本情感测度方法与模型的综述——两者均强调单一文本测度存在构念效度风险, 支持本项目在 kw/int 词频轨与 p25/p50/p75 阈值上做梯子式并排稳健性检验而非依赖单一切分。中国银行业金融科技语境下的实证背景参见 Fang, Wang, Wang & Zhao (2023, *Economic Modelling*) 对银行金融科技、流动性创造与风险承担关系的探讨, 为本家族在中国银行业新闻语料上构造的"隐性采纳"占比提供了行业适用性佐证。

## VAR: hidden_adopt_int_p25

【变体差分】
本列是家族 canonical 主轨: 相似度输入取全文轨 `policy_cosine_sim` (对应 stage 21 留篇门控 full-only 口径下的 verified 文章全文文本), 词频输入取 Track B 强度测度 `fintech_intensity_score` (TF-IDF × SIF 加权连续分数, 而非 Track A 的原始去重关键词计数 `fintech_distinct_keywords`), 分位阈值取年度内 25 百分位 (P25, 三档 P25/P50/P75 中最"宽松"的高相似度门槛、最"严格"的低词频门槛, 更容易把文章划入"隐性"格, 属稳健性梯子的一端而非机制检验基准——机制检验基准是 P50)。与 full/ctx/ss 三轨的其余两列相比, 本列不带轨后缀, 是三者中信息量最完整(标题+全部正文)但也最不聚焦目标银行—金融科技实体邻近上下文的一支, 与 `_ctx`/`_ss` 互为稳健性并排, 不构成主次关系。作为 P4 机制检验/稳健性族的一员, 该列常用于检验"隐性采纳占比高的银行—年是否也表现出更强的实质创新绩效"等假设中的稳健性分支, 与 P50/P75 阈值及 kw 词频轨版本共同构成完整的稳健性梯子。
本列的分母口径值得单独强调: bank-year 聚合分母不是该银行当年全部报道篇数, 而是"当年当行 stage 15 政策相似度与词频强度双双非缺测、且落在 stage 24 语义精筛 verified 集内"的篇数; 若某银行—年全部报道均因 stage 15 优雅早退 (三条早退路径任一触发, 如政策文档语料缺失或嵌入调用失败) 而 `policy_cosine_sim` 全 NaN, 本列输出 NaN 而非伪零, 与项目内其余"率/均值"类文本测度 (`concern_score`/`jf_coefficient`/`disagreement` 等) 共享同一"无数据=未测量"契约, 不会因强填零而污染双向固定效应估计的组内方差。读者在解释系数时应留意该 NaN 语义, 不宜把缺失当作"零采纳"处理。

## VAR: hidden_adopt_int_p25_ctx

【变体差分】
本列把相似度输入切换为实体窗口轨 `policy_cosine_sim_ctx` (标题 + 目标银行∧金融科技实体邻近窗口文本, 而非全文), 词频输入若存在 `fintech_intensity_score_ctx` 同轨变体则优先取用, 否则退化复用全文版本并在日志中披露 (track-agnostic 元数据的优雅降级, 非静默 NaN)。年度分位阈值 `P25` 与词频轨选择 (Track B `int`) 与 canonical 列保持一致, 唯一差分维度是相似度计算所依据的文本窗口范围收窄到实体邻近上下文, 从而降低无关段落(如同一篇报道中与目标银行无关的其他内容)对相似度分数的稀释。本列与 canonical `hidden_adopt_int_p25` 及 `_ss` 变体各自 just-identified 并排, 是互为稳健性检验的三轨之一, 不应在同一过度识别 (over-identified) 的 Hansen J 设定中同时纳入三轨系数; 若三者结论方向一致, 可作为构念稳健于文本窗口选择的证据。行域仍受 stage 21 full-only 留篇门控约束 (是否计入"一篇银行金科报道"只看 `llm_verified_full`), ctx 轨本身仅作为该留篇集合之上的条件测度/稳健性轨, 不改变样本口径。
实体窗口收窄带来的直觉是: 若一篇长报道整体主题与政策议程契合度不高, 但其中围绕目标银行与金融科技的段落恰好复述了政策语汇, 全文轨的相似度会被无关段落稀释而偏低, 实体窗口轨则能更精确地捕捉到该局部对齐信号, 从而使更多"局部隐性对齐"的文章在 `_ctx` 版本下被划入 hidden 象限, 而在 canonical 全文版本下可能被划入"低频低对齐"的沉默格。这一差异本身是构念稳健性的检验对象而非缺陷: 若 canonical 与 `_ctx` 两列在回归结果上方向一致、量级相近, 说明"隐性采纳"构念不依赖文本窗口选择; 若二者出现系统性偏离, 应结合 `token_adopt`/`subst_adopt` 姊妹家族的 ctx 轨联合诊断, 排查是否为窗口截断导致的度量误差而非真实构念差异。

## VAR: hidden_adopt_int_p25_ss

【变体差分】
本列把相似度输入切换为同句共现轨 `policy_cosine_sim_ss` (标题 + 目标银行与金融科技词汇同句±N窗口, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认1句), 是三轨中文本范围最窄、共现证据最直接的一支。词频输入若存在 `fintech_intensity_score_ss` 同轨变体则优先取用, 否则同样退化复用全文版本。`_ss` 的文本物化遵循镜像 `_ctx` 的回退语义: 当某篇报道不存在银行∧金科同句共现时, 其底层 `content_ss` 在 stage 14 物化阶段即回退为全文正文并标记 `ss_is_fallback=True`, 该回退发生在政策相似度打分之前, 四象限分类环节只是照常消费已经算好的 `policy_cosine_sim_ss`; 回退不改变本列在 bank-year 聚合时"未测量=NaN"的分母口径, 已测量口径仍以 `policy_cosine_sim_ss` 与所用词频列双双非缺测为准。与 canonical 列和 `_ctx` 列一样, 本列取 P25 分位阈值、Track B 强度词频轨, 三轨各自独立计算、互为稳健性并排、禁止混入同一 over-identified Hansen J; 三轨若在 P25/P50/P75 多档阈值上均呈现一致的方向性结果, 可视为构念对文本窗口选择的稳健性证据链。
`_ss` 是三轨中共现证据最直接、但文本量最稀薄的一支: 由于要求银行实体与金融科技词汇同句(或±1句窗口内)出现, 满足该条件的文章子集天然比 `_ctx` 的实体窗口更小, 相应地 `policy_cosine_sim_ss` 的可测量样本 (非 NaN) 篇数往往少于 `_ctx`/canonical, 使得本列在稀疏银行—年组合上出现 NaN 的概率更高, 解释时应结合姊妹家族 `n_articles_llm_valid_ss` 之类的分母披露列一并核查覆盖度, 避免把"未测量"误读为"零隐性采纳"。当同句共现样本量过小导致年度分位阈值本身不稳健时, 建议优先参照 canonical 或 `_ctx` 版本的结果, 把 `_ss` 作为额外的稳健性佐证而非唯一依据, 这也是三轨"互为稳健性、不分主次"原则在小样本场景下的实际应用方式。

<!-- rendered-citations:begin -->
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Kearney, C., & Liu, S. (2014). Textual sentiment in finance: A survey of methods and models. International Review of Financial Analysis, 33, 171-185. https://doi.org/10.1016/j.irfa.2014.02.006
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
<!-- rendered-citations:end -->
