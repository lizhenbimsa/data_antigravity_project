---
family_id: F607
columns:
- washing_ratio_du_2022
- washing_ratio_du_2022_ctx
- washing_ratio_du_2022_ss
unit: 比率/占比 (proportion, [0,1]; 分子分母同为文章计数)
formula: 'washing_ratio_du_2022{track} = count(du_2022_score{track} 判正 ∧ innovation_substantiveness_full == 象征性) / count(du_2022_score{track} 判正 ∧ innovation_substantiveness_full 已测量(∈{实质性,象征性}))'
producer: pipeline\panel\runner.py (方法 D2 单词典洗稿率构造, 步骤 7h 篇章级标记 + 面板聚合) ; pipeline\panel\export.py (变量标签挂载)
upstream:
- du_2022_score_full
- du_2022_score_ctx
- du_2022_score_ss
- innovation_substantiveness_full
- is_positive_full / is_positive_ctx / is_positive_ss (仅作族内交叉核对, 非本列直接分子)
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
- doi: "10.1016/j.pacfin.2024.102600"
  type: journal
  authors: "Fan, X., Tang, Z., Huang, W., & Yang, K."
  year: 2025
  title: "Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective"
  venue: "Pacific-Basin Finance Journal"
  vol: "89"
  pages_or_artno: "102600"
- doi: "10.1111/eufm.12509"
  type: journal
  authors: "Gorovaia, N., & Makrominas, M."
  year: 2024
  title: "Identifying greenwashing in corporate-social responsibility reports using natural-language processing"
  venue: "European Financial Management"
  vol: "31"
  issue: "1"
  pages_or_artno: "427-462"
- doi: "10.1287/orsc.2014.0949"
  type: journal
  authors: "Kim, E.-H., & Lyon, T. P."
  year: 2015
  title: "Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure"
  venue: "Organization Science"
  vol: "26"
  issue: "3"
  pages_or_artno: "705-723"
- doi: "10.1016/j.iref.2026.104974"
  type: "journal"
  authors: "Li, Y., & Zhu, C."
  year: 2026
  title: "Govern digitalization with digitalization: government digital governance and corporate false digital disclosure"
  venue: "International Review of Economics & Finance"
  vol: "106"
  pages_or_artno: "104974"
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_du_2022 家族衡量的是"银行金科相关报道中, 被词典判为正面的文章里, 有多大比例其实只是象征性表态而非实质性内容", 白话讲就是"嘴上说得好听、实际动作没跟上"的报道占比, 借用企业传播文献里的"洗白/漂绿"(washing/greenwashing)构念, 迁移到银行金融科技语境下衡量报道文本层面的"言实分离"。该家族与 export.py 中已挂标签的 washing_ratio / washing_ratio_ctx (方法 A, 基于三家 LLM 多数投票 is_positive) 属同一构念族的不同测度实现分支——本家族对应 runner.py 注释中列举的方法 D2("单词典"分支), 即用某一部具体情感词典(此处为 Du et al. 2022 的中文金融情感词典)的判正结果替代 LLM 投票作为分子来源锚点, 而不是对 6 部词典取均值(那是另一家族 washing_ratio_dict, 方法 D)。分母同样锚定"实质性/象征性已被 LLM 测量"的同域子样本(即 innovation_substantiveness_full ∈ {实质性, 象征性}), 而非全部正面文章, 这是 fix(omni-g-runner-10/14) 引入的分母口径修正——如果不做这层限制, LLM 实质性分类失败率越高, 分母里混入越多"根本没被判过实质/象征"的文章, 洗稿率会被系统性稀释拉低, 造成假象而非真实下降。分子逻辑是"该词典判正 ∧ 象征性"; 分母逻辑是"该词典判正 ∧ 已被测量"; 二者共享"词典判正"这一前置门槛, 保证分子严格是分母的子集, 比率天然落在 [0,1] 区间。象征性/实质性的二分类标签本身来自另一家族(innovation_substantiveness_full, W&Z 1998 语言学传统的象征-实质区分), 本家族只是在此基础上叠加"词典正面情绪"这一维度, 用以刻画"正面情绪表达"与"内容实质性"之间的错位程度。

【方法学与计算】
计算分两层。第一层是文章级标记(runner.py 步骤 7h 内联构造, 属临时中间列, 不落文章级 parquet), 对每一轨(full/ctx/ss)分别判断 du_2022_score{track} 是否判正(词典打分口径遵循 du_2022 家族自身的正负判定规则, 含政治词权重敏感性口径 polw05 canonical), 再与 innovation_substantiveness_full 的象征性/实质性标签做逻辑与运算, 生成 `_is_du_2022_pos_symb{track}` 与 `_svd_du_2022_pos{track}`(subst-valid denominator, 即"该词典判正且实质性已测量")两组 0/1 指示列——注意这组中间列名带有 du_2022 词典标识前缀, 与方法 A(LLM 投票分支)专用的 `_is_pos_symb{track}`/`_svd_pos{track}` 并非同一列、分子来源也不同(前者锚定 du_2022_score{track} 判正, 后者锚定 is_positive{track} 即 LLM 多数投票判正), 二者互不复用、互不覆写。第二层是面板聚合(export.py 前置的面板构建阶段), 对每个银行-年份单元分别加总 `_is_du_2022_pos_symb{track}` 与 `_svd_du_2022_pos{track}`, 相除得到 washing_ratio_du_2022{track} = Σ(判正∧象征性) / Σ(判正∧已测量)。三轨(full/ctx/ss)口径独立并行: full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科同句±N窗(config/filtering.yaml::context_window.ss_sentence_radius); 三者严格按 CLAUDE.md 三轨铁律各自 just-identified 并排、互为稳健性不分主次, 绝不可混进同一 over-identified Hansen J 或同一 RHS 回归式。ss 轨若某银行-年份单元内文章无银行∧金科同句共现, 该文章的 content_ss 回退为全文 body(镜像 ctx 的回退语义), ss_is_fallback=True, 但仍共享同一 n_articles 分母, 不改变本家族分子分母的计数逻辑。留篇门控遵循 2026-06-29 起的 full-only 口径: 一篇文章是否算作"一篇有效银行金科报道"只看 llm_verified_full, ctx/ss 轨的 washing_ratio 变体是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集的子集; 若 du_2022_score{track} 或 innovation_substantiveness_full 缺测(词典引擎失败或 LLM 分类拒绝作答), 该文章既不进分子也不进分母, 而不是被计为负例, 避免测量失败被误读为"未洗稿"。若某银行-年份单元完全没有满足"词典判正"前置门槛的文章, 分母为零, 比率记为缺失而非 0, 防止零分母除法产生虚假的极端值。

【文献定位】
本家族的方法论根基有二: 一是 Du, Huang, Wermers & Wu (2022, Review of Finance) 构建的中文金融情感词典, 本家族直接复用其判正判负输出作为测度锚点, 而不是像方法 A 那样依赖 LLM 投票, 目的是在稳健性检验中提供一条不依赖大模型主观判断、完全规则化可复现的平行轨道; 二是企业传播与可持续信息披露文献中"言实分离/漂绿"(greenwashing/washing)的构念传统——Kim & Lyon (2015, Organization Science) 提出的"漂绿 vs. 漂棕"框架区分了企业在环境信息披露上"言过其实"与"讳莫如深"两种偏误方向, 本家族借用其中"言过其实"(正面言辞与实质行动脱节)的核心逻辑, 把分析对象从企业自我披露迁移到第三方新闻报道; Gorovaia & Makrominas (2024, European Financial Management) 运用自然语言处理方法识别企业漂绿信号, 为本家族"用文本挖掘量化言实分离程度"的做法提供了方法学参照; Fan, Tang, Huang & Yang (2025, Pacific-Basin Finance Journal) 从股权集中度与多主体治理视角考察中国资本市场企业漂绿现象的成因, 补充了漂绿构念在公司治理侧的实证证据, 与本家族聚焦文本测度的路径互为补充而非同一方法论谱系。washing_ratio_du_2022 家族与同构念族的 LLM 投票版 washing_ratio、6 词典均值版 washing_ratio_dict、BERT 均值版 washing_ratio_bert、高置信度子样本版 washing_ratio_hc 共同构成"多方法互证"的稳健性矩阵——各方法测的是同一构念的不同操作化实现, 数值不应期望逐一相等, 而应期望方向一致、量级可比。 在中文语境下, 该构念的最新前沿测度可进一步补足本家族的存在性依据: Li 与 Zhu (2026) 构造中国企业"虚假数字化披露"(false digital disclosure)测度并检验政府数字治理对其的抑制作用, 其构念内核——数字化叙事强度与实质数字化不匹配——与本家族分子端"词典判正面 ∧ 实质性缺席"的交集定义同义, 为本家族在中国制度背景下的构念可测性提供了同期证据。迁移边界须明示: 该文测度对象为企业年报自我披露文本, 参照系为企业内部数字资产与投入, 观测单位为公司-年; 本家族对象为第三方媒体报道, 实质性由 LLM 逐篇判定而非与财务投入比对, 观测单位为银行-年。该文亦未涉及以中文情感词典分层筛出判正面样本这一环, 故本处只取其构念层锚定, 不作 du_2022 判定器口径的方法学依据。
## VAR: washing_ratio_du_2022

【变体差分】
本列是家族的 full 轨 canonical 变体, 即 washing_ratio_du_2022 家族在无后缀情形下的默认口径: 分子取 du_2022_score_full 判正且 innovation_substantiveness_full 为象征性的文章数, 分母取 du_2022_score_full 判正且实质性/象征性标签已测量的文章数, 二者在同一银行-年份单元内相除。full 轨的文本窗口是"标题+正文全文"(prepend_title 后的完整 content_full), 覆盖面最广、不依赖实体窗口裁剪, 是三轨中样本量最大、信息损失最小的一支, 也是留篇门控(llm_verified_full)锚定的那一轨——本列继承 full-only 门控下的完整行宇宙, ctx/ss 两个孪生变体则是在此行宇宙子集上的条件测度。作为家族内三轨并排稳健性矩阵的一员, 本列不应被视为"主口径"而 ctx/ss 是"补充"——三者是互为稳健性、不分主次的并列关系, 各自独立支持后续面板回归的 just-identified 设定, 严禁把三轨同时塞进同一个 over-identified 工具变量方程(如 Hansen J 过度识别检验)。本列与方法 A(LLM 投票版 washing_ratio_full)在构念上指向同一现象, 但测度来源不同——本列完全依赖词典规则化打分, 不涉及大模型主观判断, 因此对 LLM 分类失败率、模型厂商切换、prompt 版本迭代等潜在扰动天然免疫, 是该构念族里可复现性最强、成本最低的一支, 适合作为跨模型/跨时期稳健性检验的锚点; 但也因此继承了词典法固有的局限, 例如无法识别反讽、否定嵌套之外更复杂的语用现象, 分子分母的口径边界完全由 Du et al. (2022) 词典的收词范围决定。

## VAR: washing_ratio_du_2022_ctx

【变体差分】
本列是 ctx(实体窗口)轨变体, 与 canonical 全文轨 washing_ratio_du_2022 的唯一区别在于分子分母所依赖的词典打分列换成 du_2022_score_ctx——即词典判正的文本来源从"标题+正文全文"收窄为"标题+银行/金科实体前后窗口"(config/filtering.yaml::context_window 定义的窗口宽度), 目的是排除文章中与银行金科主题无关段落对情感打分的稀释或污染, 让"该文章是否被词典判为正面"更聚焦于目标实体附近的语言表达。分母的实质性/象征性标签仍统一取自 innovation_substantiveness_full(该标签本身不分轨, 是文章整体层面的一次性判定), 因此本列与 canonical 列的差异纯粹来自分子侧词典打分文本窗口的收窄, 而非分母口径的变化。行宇宙继承 full-only 留篇门控, 即仍以 llm_verified_full 为准划定"有效报道"范围, ctx 只是在该范围内的条件测度分支, 不额外扩大或缩小样本; 若某文章缺失有效的实体窗口(如银行/金科实体未能定位), du_2022_score_ctx 按 ctx 轨自身的缺测规则处理, 缺测文章不计入本列的分子分母。本列与 canonical 列、_ss 列三者并排, 各自 just-identified, 互为稳健性不分主次, 不得混入同一过度识别方程。与 ss 轨相比, ctx 轨的窗口边界依据实体位置(银行/金科提及处)划定, 不要求二者出现在同一句话内, 因此对上下文的容纳度介于 full 与 ss 之间, 是三轨里"折中"的一支——既比 full 更聚焦目标实体附近语境, 又比 ss 保留更多周边语句信息, 在稳健性叙事里常用来检验结论是否对文本窗口宽窄的连续变化敏感, 而非仅在两个极端(全文 vs 严格同句)之间跳变。

## VAR: washing_ratio_du_2022_ss

【变体差分】
本列是 ss(银行∧金科同句)轨变体, 分子分母依赖的词典打分列换成 du_2022_score_ss——文本来源收窄为"标题+银行与金科词汇同句出现"的句子集合(±N 窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中文本窗口最窄、判据最严格的一支, 用于检验洗稿率测度是否对"银行与金科话题真正同句共现"这一更苛刻的共现口径敏感。回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, content_ss 回退为全文 body, ss_is_fallback 标记为 True, 但该文章在分母计数(n_articles 口径)上仍与其余轨道共享同一基准, 不因回退而被排除出统计; 换言之词典打分仍照常在回退后的全文上进行, 只是不再享有"严格同句"这一更聚焦的文本窗口优势。分母的实质性/象征性标签同样统一取自 innovation_substantiveness_full, 与 ctx/canonical 两列共享同一分母语义来源, 差异只在分子侧词典判正所依赖的文本窗口。本列继承 full-only 留篇门控划定的行宇宙, 是该宇宙上的条件测度轨, 与 canonical、_ctx 两列构成三轨并排稳健性矩阵的第三支, 各自 just-identified, 互为稳健性不分主次, 三者严禁混入同一过度识别 Hansen J 检验或同一回归右手边。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Li, Y., & Zhu, C. (2026). Govern digitalization with digitalization: government digital governance and corporate false digital disclosure. International Review of Economics & Finance, 106, 104974. https://doi.org/10.1016/j.iref.2026.104974
<!-- rendered-citations:end -->
