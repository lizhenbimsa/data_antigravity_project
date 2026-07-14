---
family_id: F614
columns:
- washing_ratio_jiang_2021
- washing_ratio_jiang_2021_ctx
- washing_ratio_jiang_2021_ss
unit: 比率/占比 (proportion, [0,1]; 分母为零的银行-年记为缺失, 不做 0 填充)
formula: 'washing_ratio_jiang_2021{track} = 篇章级 count(jiang_2021_score{track}>0 且 innovation_substantiveness_full=="象征性") / count(jiang_2021_score{track}>0 且 innovation_substantiveness_full 已测量∈{"象征性","实质性"}), 聚合至银行-年; track∈{"", "_ctx", "_ss"} 对应 full/ctx/ss'
producer: pipeline\panel\runner.py (方法 D2 单词典洗稿率, 步骤 7h 篇章级标记与银行-年聚合) ; pipeline\panel\export.py (Stata 变量标签)
upstream:
- pipeline/sentiment/tone_words.py::jiang_2021 词典打分 (jiang_2021_score{track})
- pipeline/panel/encode.py::DICT_NAMES (jiang_2021 为 6 部词典之一)
- pipeline/panel/runner.py::innovation_substantiveness_full (LLM P3 象征性/实质性分类, 三LLM共识)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., Yang, K.
  year: 2025
  title: 'Ownership concentration and corporate greenwashing in China''s capital markets: Based on a multi-actors perspective'
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: '102600'
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., Zhou, G.
  year: 2019
  title: Manager sentiment and stock returns
  venue: Journal of Financial Economics
  vol: '132'
  issue: '1'
  pages_or_artno: 126-149
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., Webersinke, N.
  year: 2022
  title: 'Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures'
  venue: Finance Research Letters
  vol: '47'
  issue: Part B
  pages_or_artno: '102776'
- doi: 10.1177/014920630002600602
  type: journal
  authors: Deephouse, D. L.
  year: 2000
  title: "Media reputation as a strategic resource: An integration of mass communication and resource-based theories"
  venue: Journal of Management
  vol: '26'
  issue: '6'
  pages_or_artno: 1091-1112
new_dois:
- 10.1177/014920630002600602
---

## CORE

【构念与来源】
本家族 F614 度量的是一种"洗稿率"(washing ratio): 在某银行-年的新闻语料中, 被文本判为"正面基调"的报道里, 有多大比例同时被 LLM 判为"象征性"(symbolic) 而非"实质性"(substantive) 表述。这是把公司传播文献中"漂绿/洗白"(greenwashing / cheap talk) 的识别逻辑, 从环境信息披露迁移到银行与金融科技(金科)合作报道场景: 一篇报道如果基调正面, 但内容停留在口号式、概念式的"拥抱创新""积极布局"等表述, 而没有可验证的实质性举措描述(如具体产品、合作协议、投入规模), 就被记为"洗稿"。姜富伟等(2021, 经济学季刊)提出并验证了媒体文本情绪对股票回报的预测力, 其构建的中文情感词典是本仓库 `DICT_NAMES` 六部词典之一, 在流水线内部以 `jiang_2021` 命名; 本家族即以该词典对 full/ctx/ss 三轨文本打分(`jiang_2021_score{track}`)得到的正负极性作为"正面"判据, 区别于 `washing_ratio`(不带词典后缀的家族)以三家 LLM 多数投票 `is_positive{track}` 作正面判据的方法 A。二者在流水线注释里分别记为方法 A(LLM 投票)与方法 D2(单词典), 两者是同一"洗稿率"构念在不同"正面"判定引擎下的并排稳健性变体, 互不隶属、互不替代。

【方法学与计算】
构造分两步。第一步在文章级(篇章级)生成两个 0/1 标记: 分子标记 = (jiang_2021_score{track} > 0) 且 (innovation_substantiveness_full == "象征性"); 分母标记(同域计数, "svd" = substantiveness-valid denominator) = (jiang_2021_score{track} > 0) 且 (innovation_substantiveness_full 已被 LLM 成功测量, 即取值属于 {"象征性","实质性"} 而非 NaN)。第二步在银行-年层面聚合: washing_ratio_jiang_2021{track} = Σ分子标记 / Σ分母标记。分母刻意排除"象征性/实质性"分类失败的文章, 这是 2026-06-11 的一次修复(fix omni-g-runner-10/14): 若分母仍沿用"全部正面文章"而不扣除测量失败样本, 当 LLM 分类失败率因样本特征系统性上升时(例如某类银行报道文风更晦涩), 洗稿率会被虚假拉低——不是真的洗稿变少了, 而是测不出来的文章被错误地计入了"未洗稿"的分母。这一"同域分母"处理与仓库内 encode-01 号已知问题同族, 是本家族区别于早期朴素实现的关键设计。三轨(full/ctx/ss)在该分子分母逻辑上完全平行, 唯一差异是文本窗口不同: full 用标题+全文正文, ctx 用标题+银行/金科实体窗口, ss 用标题+银行∧金科同句(±N 句, 默认 N=1)窗口; 若某银行-年在 ss 轨缺乏同句共现, 该文章的 ss 文本回退为全文 body(镜像 ctx 的回退语义, `ss_is_fallback=True`)。留篇门控口径与全仓一致, 为 full-only(2026-06-29 起): 一篇报道是否计入分母、分子, 首先取决于其在 full 轨被 LLM 判定为"已核实的银行-金科报道"(`llm_verified_full==True`); ctx/ss 轨的洗稿率是在该留篇集合子集上的条件测度(conditional-on-full), 而非独立样本重新筛选。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定。

【文献定位】
洗稿率这一构念的直接方法学祖先是 Bingler et al.(2022, Finance Research Letters)对企业气候信息披露"言辞廉价、挑拣披露"(cheap talk / cherry-picking)的识别框架, 该文用语言模型区分"言辞承诺"与"具体行动"披露, 本仓库注释直接引用其"洗稿率"命名。Gorovaia & Makrominas(2024, European Financial Management)进一步用自然语言处理方法在企业社会责任报告中识别漂绿, 为"象征性 vs 实质性"文本二分提供了可操作的判据设计参照; Fan, Tang, Huang & Yang(2025, Pacific-Basin Finance Journal)则在中国资本市场情境下研究股权集中度与企业漂绿的关系, 为本家族"银行-金科洗稿"这一中国制度背景下的应用提供了同源文献支撑。词典层面, 姜富伟等(2021, 经济学季刊)构建的中文媒体情绪词典是本家族"正面"判据的直接来源, 与 Jiang, Lee, Martin & Zhou(2019, Journal of Financial Economics)提出的经理人情绪词典属于同一"文本情绪测度先于事件研究"传统, 但二者是相互独立的两套中英文词典构建工作(仓库内曾有过一次勘误: 2026-06-05 发现另一处 `jf_coefficient`(Janis-Fadner 极性系数)列的注释误标为"Jiang 2019"实为 Deephouse(2000, Journal of Management)基于 Janis & Fadner(1965)方法的媒体声誉度量, 与本家族 jiang_2021 词典及 Jiang 2019 均属不同构念, 三者在本仓库文档体系内已分别厘清出处, 不应再度混淆)。Deephouse(2000)提出的"负面且实质性"反向验证逻辑(方法 B)与本家族"正面且象征性"逻辑互为镜像, 共同构成 washing_ratio 家族体系内多方法并排的稳健性矩阵的一部分, 帮助读者理解本家族在该矩阵中的确切位置: 单一中文词典(jiang_2021)驱动的正面判据 × 三文本轨道。

## VAR: washing_ratio_jiang_2021

【变体差分】
本列是家族的 full 轨(无轨道后缀), 文本窗口为标题+正文全文, 是 jiang_2021 词典驱动洗稿率的 canonical 主测度。"正面"判据完全来自 `jiang_2021_score` 在全文文本上的打分是否为正, 不涉及 LLM 投票、不涉及否定翻转以外的语言学规则消融(词典消融梯度是另一条正交的稳健性轴, 不在本列内叠加); "象征性/实质性"判据则统一来自 LLM 在 full 轨上的三家共识分类结果 `innovation_substantiveness_full`——这里有一处需要精确辨析的设计: 分子/分母的"正面"来源(词典, 按 track 变化)与"象征性"来源(LLM, 恒定 full)并非同一轨道, 三轨变体之间真正变化的只是词典打分所用的文本窗口, LLM 实质性判定始终锚定 full 轨, 这与留篇门控"只看 full 轨是否留篇"的口径保持一致, 避免把"文本窗口切换"与"测量口径切换"两件事混为一谈。样本口径上, 分母只计入 LLM 象征性/实质性分类成功(非 NaN)的文章, 这意味着若某银行-年报道整体上难以被 LLM 明确归类为象征性或实质性(例如纯事实通稿、无明显倾向性表述), 该银行-年的洗稿率将建立在更小的有效样本之上, 使用者在解释跨银行差异时应同时参考分母(有效正面文章数)避免小样本噪声误读。该列与不带词典后缀的 canonical `washing_ratio`(方法 A, LLM 投票判正面)构成方法论对照: 二者若高度一致, 说明"正面"这一判断在 LLM 与传统词典两套引擎间是稳健的; 若出现系统性分歧, 则提示词典与 LLM 在识别中文金融新闻正面基调上存在方法学张力, 值得作为稳健性检验的自然实验对象报告, 而非直接取二者均值合并使用。

## VAR: washing_ratio_jiang_2021_ctx

【变体差分】
本列是 ctx 轨变体, 与 canonical full 轨的唯一差异在于 `jiang_2021_score` 的打分文本窗口: ctx 轨采用"标题+银行/金科实体窗口"而非全文正文, 即只在目标银行与金科相关实体出现的局部语境附近截取文本供词典打分, 目的是把"正面"判据聚焦到与银行-金科合作直接相关的语句, 抑制文章中与主题无关段落(如其他业务板块、宏观背景介绍)对词典打分的稀释或污染。分子分母结构与 full 轨完全一致(仍是 jiang_2021_score{ctx}>0 的正面文章中"象征性"占已测量样本的比例), 唯一替换的输入是词典打分所依赖的原始文本; LLM 象征性/实质性判定仍锚定 full 轨结果, 不随 ctx 切换(这是刻意设计, 避免留篇门控与分类口径的重复切轨引入额外自由度)。行样本口径继承 full-only 留篇门控: 进入 ctx 轨计算的文章集合是 full 轨留篇集合的子集, 而非用 ctx 轨自身的实体窗口重新筛选文章, 因此 ctx 轨洗稿率是"条件在 full 已确认为银行-金科报道"之上的一个测度, 不是独立样本下的平行估计。与 canonical full 轨的关系是并排的互为稳健性关系而非替代关系: 若某银行-年的全文洗稿率与 ctx 洗稿率出现较大缺口, 通常意味着该银行-年的报道中"象征性正面表述"更多出现在与银行-金科主题无关的文本区域(全文判正面但局部语境判不明确或偏中性), 这类分歧本身可作为文本"话题聚焦度"的间接信号。三轨(连同下面的 ss 轨)在下游计量设定中必须各自作为独立的 just-identified 回归设定并排报告, 不得在同一 over-identified 设定(如同一 Hansen J 检验的工具变量集合)中混用 full/ctx/ss 三条洗稿率序列。

## VAR: washing_ratio_jiang_2021_ss

【变体差分】
本列是 ss(同句)轨变体, 文本窗口进一步收紧为"标题+银行∧金科同句出现的句子(±N 句窗口, 默认半径 1)", 是三轨中判据最严格、语境最集中的一支。当某篇文章不存在银行与金科词汇的同句共现时, 该文章的 ss 文本回退为全文 body, 并置 `ss_is_fallback=True`(与 ctx 轨的回退语义完全镜像, 共享同一 `n_articles` 分母口径), 这意味着 ss 轨并非对无共现文章直接置空或剔除, 而是优雅降级为等价于 full 轨的宽窗口计算, 避免因严格同句判据过窄而系统性抹去大量有效样本。分子分母结构与 full/ctx 一致, 词典打分对象换成 ss 窗口文本, LLM 象征性判定仍取 full 轨结果不随轨道切换。相较 ctx 轨, ss 轨对"正面"判据的语境要求更苛刻——只有银行与金科词汇同句共现的句子才会进入词典打分范围(未回退情形下), 因此 ss 轨洗稿率更适合刻画"银行与金科被直接并列描述、且描述基调正面而内容空泛"这一更贴近字面意义的"洗稿"现象, 是三轨中语义最贴近"公司在同一句话里空谈合作"这一直觉的稳健性检验版本。使用者在解读三轨差异时应注意: full/ctx/ss 差异反映的是词典打分文本窗口的收紧程度, 不代表样本量差异(留篇门控三轨共享同一 full-only 行样本子集), 三者应作为对同一构念的多角度佐证并列汇报, 而非挑选其中数值"更显著"的一支作为主设定单独呈现; 与 washing_ratio(LLM 投票版)的 ss 变体做交叉比较, 亦是检验中文洗稿判据对测量引擎选择敏感度的自然稳健性路径之一。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Gorovaia, N., Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Fan, X., Tang, Z., Huang, W., Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Jiang, F., Lee, J., Martin, X., Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Bingler, J. A., Kraus, M., Leippold, M., Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47(Part B), 102776. https://doi.org/10.1016/j.frl.2022.102776
Deephouse, D. L. (2000). Media reputation as a strategic resource: An integration of mass communication and resource-based theories. Journal of Management, 26(6), 1091-1112. https://doi.org/10.1177/014920630002600602
<!-- rendered-citations:end -->
