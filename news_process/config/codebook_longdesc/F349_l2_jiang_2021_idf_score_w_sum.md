---
family_id: F349
columns:
- jiang_2021_idf_score_w_sum_ctx
- jiang_2021_idf_score_w_sum_full
- jiang_2021_idf_score_w_sum_ss
unit: 无量纲得分 (IDF 加权词条得分之银行-年加总, 非概率非百分比)
formula: 'article: jiang_2021_idf_score(article,track) = sum_over_matched_terms( final_idf(term) * polarity(term) ), 其中 final_idf(term)=Winsorize(normalized_idf(term), P1, P99), normalized_idf(term)=raw_idf(term)/mean(raw_idf), raw_idf(term)=log10(N/(1+df(term))) 由 build_idf_weights (Gentzkow, Kelly & Taddy 2019 JEL §2.2 口径) 在与 TF 同一生产语料上在线计算并写出 22_idf_weights.json (非离线冻结进 tone_dicts.json, 后者只存词典基础极性/base_score), N=文档级去重后语料总文档数, df(term)=含该词条的文档数; polarity(term) 为该词典下情感极性符号 (正向+1/负向-1, 经否定翻转/程度副词/转折三条语言学规则调制)。VW 提及密度加权 (Value-weighted Exposure, Hassan et al. 2019 QJE): jiang_2021_idf_score_w(article,track) = jiang_2021_idf_score(article,track) * mention_density(article), mention_density 为该篇文章中目标银行提及密度 (与 G-14/stage 69 distance decay_sensitivity 无关, 两者是彼此独立的不同验证维度)。面板: panel[c] = sum_over_articles( jiang_2021_idf_score_w(article,track) ), _full/_ctx/_ss 三后缀标定文本轨, sum 聚合到 (银行, 年) 面板格'
producer: pipeline\sentiment\tone_words.py (build_idf_weights 计算 IDF 权重 + article 级 jiang_2021_idf_score 打分) ; pipeline\panel\runner.py (mention_density VW 加权预计算 jiang_2021_idf_score_w, 步骤 3b) ; pipeline\panel\encode.py (build_aggregation_dict F2 IDF VW 聚合, sum 到面板) ; pipeline\panel\stata_export.py (Stata 标签映射)
upstream:
- 22_tone_words.parquet
- config/tone_dicts.json
- 22_idf_weights.json
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
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11-21
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: 'Word power: A new approach for content analysis'
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712-729
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1080/00031305.2025.2539241
  type: journal
  authors: Sheridan, P., Ahmed, Z., & Farooque, A. A.
  year: 2026
  title: A Fisher's exact test justification of the TF-IDF term-weighting scheme
  venue: The American Statistician
  vol: '80'
  issue: '1'
  pages_or_artno: 146-156
- doi: "10.3390/electronics12071632"
  title: "TF-TDA: A Novel Supervised Term Weighting Scheme for Sentiment Analysis"
  authors: "Alshehri, A., & Algarni, A."
  year: 2023
  venue: "Electronics"
  type: "journal"
- doi: "10.1287/mnsc.2020.01180"
  type: "journal"
  authors: "Cong, L. W., Liang, T., Zhang, X., & Zhu, W."
  year: 2025
  title: "Textual Factors: A Scalable, Interpretable, and Data-Driven Approach to Analyzing Unstructured Information"
  venue: "Management Science"
  vol: "71"
  issue: "12"
  pages_or_artno: "10727-10739"
new_dois:
  - "10.3390/electronics12071632"
---

## CORE

【构念与来源】
本家族测度银行-年层面新闻文本中 jiang_2021 中文财经情感词典的 IDF 加权情感强度总量 (idf_score_w_sum)。jiang_2021 词典源自姜富伟、孟令超、唐国豪 (2021) 发表于《经济学(季刊)》的媒体文本情绪测度研究, 该文构建了面向中国财经媒体语境的情感词表, 用以刻画媒体文本情绪对股票回报的预测力; 本仓库将该词表并入词典消融梯度的六部词典集合 (与 yao_2021/bian_2021/du_2022/you_2018/loughran 并列), 供跨词典互为稳健性的情感测度比对。与家族内简单计数/等权得分不同, idf_score_w_sum 在逐词条打分时引入逆文档频率 (Inverse Document Frequency, IDF) 权重: 每个匹配到的情感词条不再以等权 ±1 计入, 而是乘以该词条在与 TF 同一生产语料上在线计算出的最终 IDF 权重 (raw_idf=log10(N/(1+df)) 经均值归一化后再 P1/P99 Winsorize 得到, N 为文档级去重后语料总文档数, df 为含该词条的文档数)。IDF 加权的经济学直觉是: 在语料中普遍出现的情感词 (如"上涨""下跌"等高频泛用词) 区分力弱, 应降权; 而在语料中稀有但语义明确的词条 (如某些专业化的负面措辞) 区分力强, 应升权。这一构造思路直接继承自信息检索经典文献 Spärck Jones (1972) 提出的词条特异性统计诠释, 以及 Jegadeesh & Wu (2013) 在金融文本分析中开创的"word power"方法——后者正是用样本内词频加权 (而非简单符号计数) 来提炼十-K 文件中真正驱动股价反应的词汇信号, 本测度族的 IDF 加权可视为该思路在中文财经新闻语境下的移植与延伸。Sheridan, Ahmed & Farooque (2025/2026) 进一步为 TF-IDF 类词条加权方案提供了基于 Fisher 精确检验的统计学证成, 说明稀有词升权并非纯经验直觉而具备可检验的统计基础, 为本测度的加权设计提供了方法学背书。本家族列名 `_w` 后缀 (idf_score_w_sum) 指的是在文章级 IDF 加权得分基础上再叠加的提及密度加权 (Value-weighted Exposure, Hassan et al. 2019 QJE): `jiang_2021_idf_score_w = jiang_2021_idf_score * mention_density`, 与词条 IDF 权重是两层彼此独立的加权, 不可混同; 该提及密度加权与 G-14/stage 69 distance decay_sensitivity 距离衰减敏感性检验无关, 后者是本仓库另一条独立验证阶段。

【方法学与计算】
计算分三层。第一层是 IDF 权重构建 (stage 22 `pipeline\sentiment\tone_words.py::build_idf_weights`): 在与词频统计同一份生产语料上 (调用方传入 `content_full`, 缺则回退"内容"列), 对每部词典逐词条计算 raw_idf=log10(N/(1+df)) (N=文档级去重后语料总文档数, df=含该词条的文档数, Gentzkow, Kelly & Taddy 2019 JEL §2.2 口径), 再做均值归一化 (令均值=1, 使不同词典的权重量纲可比) 与 P1/P99 Winsorize (截尾防止极端稀有词权重失控), 得到 `final_idf`, 并输出到 `22_idf_weights.json` (随当次语料在线计算, 并非离线预计算后冻结进 `config/tone_dicts.json`——后者只存词典基础极性/base_score, 不存 IDF 权重)。第二层是文章级打分: 对每篇文章的候选文本 (三轨 full/ctx/ss 各自独立扫描), 用 jiang_2021 词表做正向/负向词条匹配, 命中词条经否定翻转、程度副词强化/弱化、转折关系降权三条语言学规则调制后, 乘以该词条的 `final_idf` 权重, 再乘以极性符号 (正向 +1、负向 -1) 并求和, 得到该篇文章在该轨道下的 `jiang_2021_idf_score` (IDF 加权得分, 与消融梯度族共用同一套否定/程度/转折三规则全 powerset 消融框架 `_RULE_ABLATION_VARIANTS`, 但本身对应"全语言学规则"版本)。第三层是提及密度加权与面板聚合 (`pipeline\panel\runner.py` 步骤 3b + `pipeline\panel\encode.py::build_aggregation_dict`): 先用该篇文章的提及密度 `mention_density` (Value-weighted Exposure, Hassan et al. 2019 QJE) 对 `jiang_2021_idf_score` 做逐篇加权, 得到 `jiang_2021_idf_score_w`; 再按 (银行, 年) 分组求和 (sum), 得到本家族的银行-年 `idf_score_w_sum` 三个轨道列。列名中的 `_w` 后缀因此对应提及密度加权, 而非词条 IDF 权重本身 (IDF 权重已内嵌在无 `_w` 后缀的 `jiang_2021_idf_score` 基名之中); 读者理解本测度须区分"词条层面的 IDF 加权"与"篇章层面的提及密度加权"两层不同的加权含义。求和而非求均值的选择, 使该测度同时承载"情感强度"与"报道数量/媒体关注度"两重信息——报道越多且措辞越极端, 加总值越高, 这与家族内其它"均值型"情感测度 (如 `_tone`) 构念上互补而非替代。三轨 (full/ctx/ss) 分别对应标题+全文、标题+银行实体窗口、标题+银行∧金科同句±N窗三种文本范围, 各自独立扫描并独立求和, full 为留篇门控主轨 (2026-06-29 起 stage 21 留篇判定 = `llm_verified_full`), ctx/ss 是 conditional-on-full 的测度/稳健性轨、行宇宙为 full 留篇集的子集; 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。ss 轨在无银行∧金科同句共现时按镜像 ctx 的回退语义处理 (`content_ss` 退化为全文 body, `ss_is_fallback=True`, 与 ctx 共享 `n_articles` 分母口径), 保证三轨在缺失样本上有一致的优雅降级行为而非静默清零。本家族与词典消融梯度族 (7 个非-full 语言学规则变体) 正交: idf_score_w_sum 恒定在"全规则"设定下计算, 不参与消融维度的 powerset 展开, 避免梯度维度与加权维度交叉爆炸列数。

【文献定位】
本测度的方法学谱系有三条并行线索。其一是中文财经情感词典本身的构建传统: 姜富伟等 (2021) 的原始工作是本词典的直接来源, 定义了词表内容与情感极性标注; 与本仓库并存的 yao_2021/bian_2021/du_2022/you_2018 等词典构成跨词典互为稳健性的并排轨道 (镜像政治词权重梯度、词典消融梯度的先例), 六部词典的比较有 Frankel, Jennings & Lee (2022) 关于词典法与机器学习法互为稳健性的方法学讨论作为背书——该文强调不同情感测度方法在解释力上各有侧重, 不存在单一"正确"口径, 应作为并排稳健性证据而非相互替代。其二是 IDF 加权本身的信息检索渊源: Spärck Jones (1972) 首次提出用逆文档频率刻画词条特异性, 是本测度加权公式 log(N/df) 的原始理论出处; 该思路经 Jegadeesh & Wu (2013) 引入金融文本分析领域, 用词频驱动的"word power"权重取代朴素符号计数, 显著提升了情感测度对股价反应的预测力, 是本仓库为财经情感词典引入 IDF 加权这一设计决策的直接方法学先例。其三是加权方案的统计学证成: Sheridan, Ahmed & Farooque (2025/2026) 用 Fisher 精确检验为 TF-IDF 类词条加权提供了假设检验框架下的合理性论证, 说明本测度并非任意的启发式加权, 而是有统计学基础支撑的稀有词升权方案。综合三条线索, idf_score_w_sum 家族在本仓库情感测度体系中定位为"词典法 + IDF 加权"的一个具体实现分支, 与三家 LLM 投票情感 (`llm_vote_tone`)、三模型 BERT 情感互为稳健性、各自 just-identified 并排, 不构成同一识别策略下的过度识别工具组。此外, Alshehri & Algarni (2023, Electronics) 提出监督式词条判别力加权方案 TF-TDA 作为传统 TF-IDF 在情感分析任务中的改进替代, 为本家族 IDF 加权情感打分设计提供同期方法学参照。 作为同期的方法学对照, Cong、Liang、Zhang 与 Zhu (2025) 提出可扩展的文本因子框架 (词向量表示 → LSH 聚类 → 主题建模识别可解释的张成簇), 明确把构造新的文本测度与解释变量列为三类应用之一, 并在宏观新闻预测、公司文件与专利语料上作了演示, 说明由词项级权重折叠出篇级测度、再送入回归这一构造路线在当前文献中仍属活跃前沿。迁移边界须交代清楚: 该文语料为英文, 走的是词嵌入加聚类的数据驱动因子路线, 与本家族固定六词典 × IDF (raw_idf = log10(N/(1+df))) 的逐词加权在信息来源与函数形式上均不相同; 该文亦不做银行-年求和聚合, 更无三轨 (full/ctx/ss) 口径, 故只可作为文本测度构造的前沿存在性参照, 不构成本列加权方案的直接先例。
## VAR: jiang_2021_idf_score_w_sum_ctx

【变体差分】
本列取实体窗口轨 (ctx): 扫描文本为"标题 + 银行实体窗口"(`content_ctx`, stage 14 `ctx_materializer` 物化, 标题经 `prepend_title` 拼接), 而非全文正文。该轨作为 full 轨的 conditional-on-full 测度/稳健性轨, 行宇宙限定在 full 轨留篇判定 (`llm_verified_full==True`) 通过的文章子集之内, 与 full/ss 两轨各自独立求 IDF 加权得分和, 三轨互为稳健性、不分主次, 禁止混入同一过度识别的 Hansen J 设定。当某篇文章缺乏可物化的银行实体窗口文本时, 该篇在 ctx 轨的贡献按 `ctx_is_fallback` 标记的优雅降级口径处理 (不静默清零、不借用 full 轨数值)。ctx 轨相较 full 轨的构念差异在于: 它把情感打分的文本范围收窄到银行实体周边的局部语境, 意在剥离与目标银行不直接相关的段落 (如文章其余部分讨论的其它主体或宏观背景) 对情感强度加总的稀释或污染, 从而更精确地捕捉"针对该银行"的媒体情绪强度, 是全文轨的一种局部化稳健性检验。就 jiang_2021 词典的 IDF 加权机制而言, ctx 轨的窗口收窄同时改变了逐词条 IDF 权重的"有效样本": 由于扫描文本更短, 命中的高频泛用情感词在实体窗口内相对更容易被稀释掉, 而围绕银行主体展开的专业化措辞占比相对上升, 这使 ctx 轨的加总得分在直觉上比 full 轨更"聚焦"、方差结构也可能不同, 因此不应把 ctx 与 full 的数值水平直接相减解读为"窗口效应大小", 而应各自作为独立的 just-identified 测度看待其与结果变量的关联方向与显著性是否一致。



## VAR: jiang_2021_idf_score_w_sum_full

【变体差分】
本列取全文轨 (full): 扫描文本为"标题 + 正文全文"(`content_full`), 是本仓库情感/态度类测度体系中的留篇门控主轨——stage 21 是否将一篇报道判定为"有效的银行-金科报道"仅依据 `llm_verified_full` 结果, ctx/ss 两轨的行宇宙都是 full 轨留篇集的子集。因此 jiang_2021_idf_score_w_sum_full 在样本覆盖面上最完整, 承载全文档范围内 jiang_2021 词典 IDF 加权情感强度的银行-年加总, 是三轨中信息量最大、覆盖最广的口径, 通常作为跨轨比较的参照锚, 但与 ctx/ss 两轨仍是并排的、就变量本身而言互为稳健性的关系, 而非天然优先的"主"测度——三轨各自 just-identified, 不应合并进同一过度识别方程。由于扫描范围覆盖全文, full 轨的 IDF 加权得分和也最容易受到与目标银行关联较弱的段落 (如文章后半部分转向宏观政策评论或其它机构对比) 拉动, 这正是设置 ctx/ss 两轨作为局部化、语境化稳健性检验的动机所在; 研究者在解读跨轨结果一致或不一致时, 应将其视为构念在不同文本范围颗粒度上的表现差异, 而非某一轨"更正确"。full 轨同时是 P1 主线论文处理变量 (treatment) 族的口径基准之一 (镜像 `llm_vote_tone_full`), 但本列本身作为词典法情感强度加总测度, 与 LLM 投票情感、BERT 情感测度族在方法论谱系上是互为稳健性的并排关系, 不构成同一构念的替代测量。

## VAR: jiang_2021_idf_score_w_sum_ss

【变体差分】
本列取同句轨 (ss): 扫描文本为"标题 + 银行∧金科同句 (±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1)"共现片段。该轨判据比 ctx 更严格——要求银行实体与金科关键词在同一句 (或邻近句窗口) 内共现才纳入扫描范围, 意在把情感打分精确锚定在"银行与金融科技话题被同时论及"的具体语境, 排除同一篇文章里与金科话题无关的银行相关段落对情感加总的干扰。当一篇文章不存在满足银行∧金科同句共现条件的片段时, ss 轨镜像 ctx 轨的回退语义: `content_ss` 退化为全文 body, `ss_is_fallback=True`, 与 ctx 轨共享同一套 `n_articles` 分母口径, 保证退化样本不会静默清零或产生单边孤儿列。ss 轨的行宇宙同样限定在 full 轨留篇集之内, 与 full/ctx 两轨各自独立求和、并排互为稳健性, 不构成同一过度识别 Hansen J 设定下的工具组合。就 jiang_2021 词典的加权机制而言, ss 轨是三轨中文本范围最窄、判据最严格的一支: 只有在同一句 (或 N=1 邻近句窗口) 内同时出现银行实体与金科关键词的片段才纳入 IDF 加权打分, 这使得 ss 轨的加总得分对"银行-金科交叉话题"这一构念的锚定最精确, 但也因此样本量与文本长度受限于共现窗口而普遍小于 ctx/full, 更容易触发 `ss_is_fallback` 回退 (尤其在生产语料 T=19 的早期年份, 金科话题密度较低时)。研究者在使用 ss 轨做稳健性检验时, 应同时关注 `ss_is_fallback` 占比是否随时间或银行类型系统性变化, 以判断 ss 轨结果是否受回退样本主导, 而非仅比较三轨系数符号与显著性。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Sheridan, P., Ahmed, Z., & Farooque, A. A. (2026). A Fisher's exact test justification of the TF-IDF term-weighting scheme. The American Statistician, 80(1), 146-156. https://doi.org/10.1080/00031305.2025.2539241
Alshehri, A., & Algarni, A. (2023). TF-TDA: A Novel Supervised Term Weighting Scheme for Sentiment Analysis. Electronics. https://doi.org/10.3390/electronics12071632
Cong, L. W., Liang, T., Zhang, X., & Zhu, W. (2025). Textual Factors: A Scalable, Interpretable, and Data-Driven Approach to Analyzing Unstructured Information. Management Science, 71(12), 10727-10739. https://doi.org/10.1287/mnsc.2020.01180
<!-- rendered-citations:end -->
