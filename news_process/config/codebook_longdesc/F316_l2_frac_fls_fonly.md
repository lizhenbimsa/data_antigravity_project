---
family_id: F316
columns:
- frac_fls_fonly_ctx
- frac_fls_fonly_full
- frac_fls_fonly_ss
unit: "比例 (proportion, 无量纲, 值域 [0, 1]; 单门前瞻句数占全部句数之比)"
formula: "文章级 frac_fls_fonly_{trk} = n_fonly_sentences / n_sentences, trk ∈ {full, ctx, ss}; 句 s 判为单门前瞻句当且仅当 ∃w∈s: w∈D_future (仅未来动作词门, 不要求未来时间标记同句共现; jieba 精确 token 匹配, ≥3 字标记加性 substring 补漏); 空文本或 n_sentences=0 → NaN; 逐句蕴含 frac_fls_fonly_{trk} ≥ frac_fls_{trk} (单门是双门 canonical 的超集); panel 列 = 文章级同名列按 bank-year 简单均值聚合 (dst=src 同名直聚合, 非 avg_ 前缀范式)"
producer: "news_process/pipeline/sentiment/forward_looking.py::_fls_gates (句级双门原语拆分, 返回 has_future 与 has_time 两个门控) 与 compute_fls_for_text (聚合出 frac_fls 与 frac_fls_fonly 两个统计量); news_process/pipeline/sentiment/tone_words.py::_dual_analyze (stage 22 三轨逐篇调用, merged['frac_fls_fonly_{full,ctx,ss}'] 写出); news_process/pipeline/panel/encode_collab.py::apply_v3_5_2 (bank-year 同名 mean 聚合)"
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨物化文本 + ss_is_fallback)
- 22_tone_words.parquet (文章级 frac_fls_fonly_{full,ctx,ss})
- config/tone_dicts.json::forward_looking_statements (双门控词表 SSOT, future/time 两个子词表, 本家族只消费 future_words 一半)
citations:
- doi: 10.1142/S1094406025500064
  type: journal
  authors: "Liu, T., Zhang, J., & Wu, J."
  year: 2026
  title: "Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach"
  venue: "The International Journal of Accounting"
  vol: 61
  issue: 1
  pages_or_artno: "Article 2550006"
- doi: 10.1016/j.irfa.2024.103484
  type: journal
  authors: "Abedin, M. Z., Goldstein, M. A., Huang, Q., & Zeng, H."
  year: 2024
  title: "Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis"
  venue: "International Review of Financial Analysis"
  vol: 95
  pages_or_artno: "Article 103484"
- doi: 10.1287/mnsc.2014.1921
  type: journal
  authors: "Muslu, V., Radhakrishnan, S., Subramanyam, K. R., & Lim, D."
  year: 2015
  title: "Forward-looking MD&A disclosures and the information environment"
  venue: "Management Science"
  vol: 61
  issue: 5
  pages_or_artno: "931-948"
- doi: 10.1111/j.1475-679X.2010.00382.x
  type: journal
  authors: "Li, F."
  year: 2010
  title: "The information content of forward-looking statements in corporate filings: A naïve Bayesian machine learning approach"
  venue: "Journal of Accounting Research"
  vol: 48
  issue: 5
  pages_or_artno: "1049-1102"
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2020
  title: "Textual analysis in finance"
  venue: "Annual Review of Financial Economics"
  vol: 12
  issue: 1
  pages_or_artno: "357-375"
- doi: "10.1111/1475-679x.12540"
  type: "journal"
  authors: "THOMAS, W. B., WANG, Y., & ZHANG, L."
  year: 2024
  title: "Algorithmic Trading and Forward‐Looking MD&A Disclosures"
  venue: "Journal of Accounting Research"
  vol: "62"
  issue: "4"
  pages_or_artno: "1533-1569"
- doi: "10.1016/j.bar.2024.101431"
  type: "journal"
  authors: "Chen, J. J., Song, P., & Loi, F. L."
  year: 2024
  title: "Strategic forward-looking nonearnings disclosure and overinvestment"
  venue: "The British Accounting Review"
  vol: "56"
  issue: "6"
  pages_or_artno: "101431"
new_dois: []
---

## CORE

【构念与来源】
本家族测量的构念是媒体报道文本中单门控识别的弱前瞻取向强度, 即一篇关于目标银行与金融科技的新闻报道中, 含有未来动作词但不要求未来时间标记同句共现的句子占全部句子的比例。它是 frac_fls 双门 canonical 家族 (F315) 在同一句级双门判定框架内拆出的单门稳健臂, 二者共享同一个前瞻性陈述构念 (forward-looking statement intensity), 差别仅在判定门控的松紧: 双门要求句中同时出现未来动作词 (D_future, 如将、拟、预计、计划、有望、力争、致力于、展望) 与未来时间标记 (D_time, 如未来、明年、下季、三年内、中长期、下一阶段), 单门只要求前者。设计动机记录在 producer 源码注释 "2026-07-03 §5 D2: 单门 (仅 future 词) 稳健臂 — 双门 canonical 的互为稳健性对照" 中, 属 2026-07-03 稳健性缺口补齐批次 (五条新梯子/轨之一) 的落地成果, 与政治词权重梯度、词典消融梯度等同期新增的并排稳健性轨共享同一设计范式: 研究者在识别构念时面对一个客观存在的自由度 (此处是"要不要求显性未来时间锚"), 与其挑一个值当作唯一正确答案, 不如把自由度两端都物化成列, 用主结论在两端间的稳定性证明结论不被这一自由度驱动。这一构念的理论根基仍是 Li (2010) 建立的经典命题: 披露文本的时间取向 (谈论未来而非既成事实) 本身携带独立于语气正负的信息含量, 本家族与 F315 是该命题在中文媒体报道语料上的同一次操作化尝试的两种门控强度实现。数据来源上, 本家族消费 stage 14 物化的三轨文本 (content_full 与 content_ctx 与 content_ss), 在 stage 22 词典情感阶段与双门 canonical 同一次逐篇调用中一并计算 (compute_fls_for_text 单次调用同时返回 frac_fls 与 frac_fls_fonly 两个统计量, 避免重复分句与重复分词), 最终经 panel 构建步骤聚合为银行-年面板列, 全程确定性纯 CPU 计算, 不涉及任何 LLM 或嵌入调用, 零 API 成本。

【方法学与计算】
判定规则的原语函数是 forward_looking.py::_fls_gates, 该函数对每个句子返回一对布尔门控 (has_future, has_time), 而非直接返回单一判定结果; 这一 2026-07-03 的重构把原本内联在 _is_fls_sentence 里的双门合取拆成了可独立消费的两个门控, 使得双门 canonical (has_future and has_time) 与单门稳健臂 (has_future 单独) 可以在不重复实现匹配逻辑的前提下并排产出, 从工程实现角度保证了二臂除门控合取方式外逐字节共享同一套分词、匹配与长标记补漏细节, 差异只锁定在"是否要求 has_time"这一个比特上。has_future 的判定本身分两步: 先用中文分词器 jieba 把句子切成 token 集合, 与未来动作词表 D_future (frozenset, 收录于 config/tone_dicts.json::forward_looking_statements::future_words) 求交, 命中即置真; 若未命中, 对长度不低于三字的词表词补充原句字面子串匹配, 因为 jieba 默认词典常把下一财年、中长期目标等多字标记切碎成多个 token, 拆碎后的成分若不在词表则整词漏判, 子串补漏是纯加性操作, 只会把门控从假变真, 不会撤销任何既有的 token 命中, 一字与二字短词仍只走精确分词匹配以延续 P-038 修复 (子串误命中希望、绝望、瞭望、将其等非前瞻语境) 建立的精度约束。分句用中文分句器把整段文本切成句子序列, 分母 n_sentences 为句子总数; 分子 n_fonly_sentences 为 has_future 为真的句数 (与是否同时 has_time 无关); 比值即 frac_fls_fonly, 值域零到一, 空文本或零句文本返回缺失值而非零。因为单门判定条件 has_future 是双门判定条件 has_future and has_time 的必要而非充分条件, 每一个被双门计入分子的句子必然也被单门计入分子, 逐句蕴含关系在聚合层直接推出 frac_fls_fonly_{trk} ≥ frac_fls_{trk} 对任意文章任意轨道恒成立, 这是一条可用于 gate 测试断言的数学不变量, 而非仅凭经验观察到的近似关系。三轨调用与 F315 完全同构: 对 content_full 与 content_ctx 与 content_ss 各调用一次同一个 track-agnostic 的计算函数, 轨道差异完全由输入文本驱动, 判定逻辑三轨逐字节一致。面板聚合同样在 encode_collab 步骤按银行-年简单均值完成, 输出列与文章级源列同名, 聚合的文章宇宙遵循全流水线 full-only 留篇门控口径 (2026-06-29): 一篇文章是否计入银行金融科技报道宇宙只由 full 轨的 LLM 验证结论决定, ctx 与 ss 轨列在该宇宙上条件计算。确定性保障与 F315 一致: 词表层由外置单一事实源 config/tone_dicts.json 与成员锁定测试保证任何修订都显式留痕; 分词层由 jieba 0.42.1 版本冻结保证同一文本在任何机器任何时点切出同一 token 序列; 数值层分子分母均为整数计数, 比值无浮点累加次序问题, 不在 BLAS 浮点漂移的非确定列清单内, golden 对照可逐位复现。本家族无独立的阈值或权重参数, 唯一的研究者自由度就是"单门抑或双门", 已由二臂并排设计穷尽。

【文献定位】
本家族的方法论定位紧贴 F315 双门 canonical 家族: Li (2010) 的机器学习法与 Muslu, Radhakrishnan, Subramanyam 与 Lim (2015) 的关键词规则法共同确立了前瞻性陈述作为独立于语气的信息维度这一构念, 本家族与 F315 是该构念在词典规则端、以不同门控松紧度实现的一对操作化。Loughran 与 McDonald (2020) 在其文本分析综述中强调, 任何单一词典映射都隐含一个未被显式检验的自由度, 稳健的做法是在合理范围内并排报告替代规格而非只呈现一个点估计, 这正是本家族存在的方法论理由: 双门是精度优先的研究者选择 (要求未来时间锚同句出现以压低误报), 单门是召回优先的替代选择 (放宽时间锚要求以纳入更多隐性前瞻表达), 二者的差值捕捉的正是那些语义上前瞻但缺少显性时间标记的句子, 这类句子在 Liu, Zhang 与 Wu (2026) 关于年报前瞻性陈述与企业融资约束关系的机器学习研究中被证明并非噪声: 该研究以机器学习方法自动抽取年报前瞻性陈述, 抽取标准并不强制要求显性未来时间标记同句共现, 却仍能在融资约束这一实质经济结果上找到系统性关联, 说明放宽时间锚要求后新纳入的弱前瞻句子并非单纯稀释信号的噪声, 而是携带独立信息含量的前瞻表达, 这为本家族单门臂纳入"弱前瞻但语义仍然前瞻"的句子提供了独立于本项目内部设计考量的外部实证支持。Abedin, Goldstein, Huang 与 Zeng (2024) 在中国上市公司 MD&A 文本上的前瞻披露测度进一步表明, 前瞻强度对股票流动性的效应会被披露的时间具体度所调节, 呼应了本家族与 F315 二臂对照所要检验的方向: 若结论仅在时间锚要求严格的双门下成立而在放宽后的单门下消失, 说明效应可能是由具体时间承诺 (而非泛泛的未来导向叙事) 驱动, 这本身是一条有实质经济含义的解读, 而非单纯的测量误差敏感性检验。 在 FLS 句类识别本身的顶刊前沿存在性上, THOMAS、WANG 与 ZHANG (2024) 以算法交易为自变量、MD&A 前瞻性披露的逐年修订程度为因变量, 并在稳健性中另以「前瞻句数」与语调修订作替代测度, 表明前瞻句的机器识别与计数在顶刊层面是被接受的构念操作化, 这为本家族以句为判定单元、以词门命中与否直接计数的做法提供了同期存在性依据。边界须写明: 原文标的为美国上市公司 10-K/10-Q 的 MD&A 章节 (公司自主披露文本, 英文), 其前瞻句判定为单一关键词门且未拆分未来动作词门与未来时间标记门, 既未构造「前瞻句数 / 全部句数」的占比测度, 亦无单门/双门二臂对照, 故不构成本家族分母口径或二臂设计的 method-origin; 层级上原文为公司-报告级, 本家族为文章级比例再按 bank-year 简单均值聚合, 且原文的前瞻披露是因变量, 本家族三列则是右手侧文本特征列。Chen、Song 与 Loi (2024) 以美国上市公司 2003-2019 的前瞻性语句为文本对象, 度量非盈利类定性 FLS 的异常语调并检验其与过度投资的关系, 同属该构念族的应用存在性参照; 但原文的落地测度是异常语调而非前瞻句占比, 且其关注的是发送者对前瞻披露的战略性选择 (公司自主披露的内生取舍), 本家族度量的则是第三方中文媒体撰稿人的前瞻表述、不假设被报道方直接控制文本, 故该文同样不构成 D_future 词门或句级占比构造的操作化参照, 亦未做单/双门对照。两文合观只确立「FLS 句级识别与计数是被顶刊接受的成熟操作化」这一层, 本家族单门臂与 F315 双门 canonical 的松紧度二臂仍是本项目自身的研究者选择, 二臂各自 just-identified 并排、互为稳健性, 不得混入同一 over-identified Hansen J。
【识别策略定位】
本家族不承担任何论文的主处理变量角色, 其角色是 F315 双门 canonical 家族的强制伴生稳健性臂: 凡在回归设定中使用 frac_fls_{trk} 作为叙事属性控制变量、机制切割变量或安慰剂佐证的场合, 若研究者希望证明结论不被"是否要求未来时间锚同句共现"这一门控松紧度自由度驱动, 应在稳健性表中并排报告以 frac_fls_fonly_{trk} 替换 frac_fls_{trk} 的平行估计。二者是同一构念在同一句级判定框架下门控收紧程度不同的两个测度, 各自 just-identified 并排、互为稳健性不分主次, 禁止把双门与单门同时塞进同一个 over-identified 的 Hansen J 检验或同一回归方程的解释变量集合 (二者高度共线且存在逐句蕴含的确定性关系, 联合入方程会引发严重的多重共线性而非提供额外识别信息)。与三轨 (full/ctx/ss) 的正交关系为: 门控松紧维度 (双门/单门) 与文本窗口维度 (全文/实体窗口/同句窗口) 是两个独立的稳健性自由度, 本家族在三个轨道上各自都有对应的单门列, 因此完整的稳健性报告空间是三轨乘二臂共六个并排规格, 覆盖窗口选择与门控选择两条自由度, 报告时应保持这两条自由度分别陈述而非交叉合并为单一联合检验。

【与相邻测度的构念区分】
与家族 F315 (frac_fls 双门 canonical) 的区分已在【方法学与计算】与【识别策略定位】中详述: 二者是同一原语函数 _fls_gates 产出的一对门控组合, 单门是双门的逐句超集, 数学关系恒定不因样本变化。与 LM 非情感六子集中的强弱情态词族的区分与 F315 相同: 情态测度承诺强度与确定性程度, 不要求未来时间指向, 一句当期的强承诺 (如本行郑重承诺执行既定方案) 命中情态词但既不满足单门也不满足双门的未来动作词门; 本家族即便门控已放宽至单门, 仍严格锚定在 D_future 未来动作词表上, 与情态词表完全独立不重叠。与六部情感语气词典的区别是维度正交, 单门放宽不改变这一正交性。与套话比率、罕见词比率等形式测度的区别同样是构念维度完全独立, 计算原语互不复用。

## VAR: frac_fls_fonly_full

【变体差分】
本列是家族三轨中的 full 轨, 是唯一与家族 canonical 相邻的 core 类比列 (家族本身 3 列全为 standard tier, 无 core 列; 本列在 F315 体系中对应的同轨双门列 frac_fls_full 是该家族的 core 列, 因此本列在使用上应优先与 frac_fls_full 配对呈现)。文本口径为 content_full, 即 stage 14 物化的标题前置加全文正文, 标题作为文本第零句参与分句与门控扫描, 原始内容列不动, 分母句数在三轨中最大, 单句判定翻转对比例的扰动最小。与双门 canonical 同轨列 frac_fls_full 的精确差分是唯一变量: 本列只要求句中出现未来动作词 (has_future), 不要求未来时间标记同句共现 (has_time 不参与判定), 因此本列的分子恒不小于 frac_fls_full 的分子, 本列取值逐篇恒不小于 frac_fls_full 取值。构念上本列回答的问题是: 就这篇报道的完整文本而言, 有多大比例的句子含有指向未来的动作词, 不论该动作是否配有显性的时间坐标; 相对双门 canonical, 本列会额外纳入诸如该行拟推进数字化转型这类有前瞻动词但缺少明确时间承诺的句子。与家族内另两列 (ctx/ss 轨) 的差分是窗口口径, 与双门 canonical 家族内 full 与 ctx 与 ss 三轨的差分逻辑完全同构: full 轨无实体窗口约束, 覆盖整篇报道包括背景段落与行业展望段落。本列行宇宙即全部留篇文章 (留篇门控本身由 full 轨 LLM 验证结论决定, 本列与该门控同轨, 不存在条件测度的问题)。面板层由文章级同名列按银行-年简单均值聚合。使用本列时的推荐规格是与 frac_fls_full 同时呈现于稳健性表, 证明相关结论在门控松紧两端保持方向与显著性一致; 若二者结论出现分歧, 应解读为效应集中在具体时间承诺的句子上而非泛化到所有弱前瞻表达, 这本身是有信息量的发现而非测量瑕疵。

## VAR: frac_fls_fonly_ctx

【变体差分】
本列是家族的 ctx 轨: 输入文本为 content_ctx, 即 stage 14 物化的标题前置加目标银行实体窗口文本, 只保留目标银行实体提及附近窗口内的句子。与双门 canonical 同轨列 frac_fls_ctx 的精确差分同样是单一门控变量: 本列只要求 has_future 而不要求 has_time, 逐篇取值不小于 frac_fls_ctx。构念重心相对家族内 full 轨列收窄为目标银行叙事邻域中含未来动作词的句子占比, 相对双门同轨列则是把时间锚要求放宽后的邻域弱前瞻密度。分母是 ctx 文本的句数, 系统性小于 full 轨, 短分母使比例对单句翻转更敏感; 面板层银行-年均值聚合部分平滑该噪声。本列行宇宙遵循 full-only 留篇门控口径 (2026-06-29): 文章是否留篇只看 full 轨验证结论, 本列在该宇宙上条件计算 (conditional-on-full), 是条件测度轨而非独立留篇轨, 与家族内 full 轨列及 F315 家族的 ctx 轨列共享同一条件计算约定。句级单门判定逻辑与词表与家族内其余两列逐字节一致, 差异完全由输入文本窗口驱动。使用铁律: 本列与 full 及 ss 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与双门同轨列 frac_fls_ctx 的二臂对照同理并排不混, 不得同时入同一回归方程或同一 Hansen J 检验。

## VAR: frac_fls_fonly_ss

【变体差分】
本列是家族的 ss 轨: 输入文本为 content_ss, 即 stage 14 物化的标题前置加银行与金融科技词同句共现句及其前后各一句的窗口文本 (窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认一句; 该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同键)。与双门 canonical 同轨列 frac_fls_ss 的精确差分是单一门控变量: 本列只要求 has_future, 不要求 has_time 同句共现, 逐篇取值不小于 frac_fls_ss。构念上本列是三轨中窗口最严的一轨, 度量的是银行与金融科技话题交汇处含未来动作词的句子占比, 放宽时间锚要求后能多捕捉一些在同句谈及银行与金融科技但未明示具体时间表的弱前瞻表达。回退语义镜像 ctx 轨的物化约定: 当一篇文章不存在银行与金科词的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置真, 共享同一 n_articles 分母, 回退行上本列取值实质等价于在全文上按单门口径计算; 上游金科词典不可用 (FINTECH_AC 为空) 时全部行回退置真, 属优雅降级而非报错。回退占比越高本列越向 full 轨同类单门列收敛。分母为 ss 文本句数, 三轨中最小, 单句翻转扰动最大, 依赖面板均值聚合平滑。行宇宙同样遵循 full-only 留篇门控 (2026-06-29), 是 conditional-on-full 条件测度轨。判定逻辑与词表与另两轨逐字节一致。使用铁律: 与 full 及 ctx 轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与双门同轨列 frac_fls_ss 的二臂对照亦并排不混, 不得同时入同一回归方程或同一 Hansen J 检验。

<!-- rendered-citations:begin -->
Liu, T., Zhang, J., & Wu, J. (2026). Forward-looking statements in annual reports and firms' financing constraints: A machine learning approach. The International Journal of Accounting, 61(1), Article 2550006. https://doi.org/10.1142/S1094406025500064
Abedin, M. Z., Goldstein, M. A., Huang, Q., & Zeng, H. (2024). Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis. International Review of Financial Analysis, 95, Article 103484. https://doi.org/10.1016/j.irfa.2024.103484
Muslu, V., Radhakrishnan, S., Subramanyam, K. R., & Lim, D. (2015). Forward-looking MD&A disclosures and the information environment. Management Science, 61(5), 931-948. https://doi.org/10.1287/mnsc.2014.1921
Li, F. (2010). The information content of forward-looking statements in corporate filings: A naïve Bayesian machine learning approach. Journal of Accounting Research, 48(5), 1049-1102. https://doi.org/10.1111/j.1475-679X.2010.00382.x
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
THOMAS, W. B., WANG, Y., & ZHANG, L. (2024). Algorithmic Trading and Forward‐Looking MD&A Disclosures. Journal of Accounting Research, 62(4), 1533-1569. https://doi.org/10.1111/1475-679x.12540
Chen, J. J., Song, P., & Loi, F. L. (2024). Strategic forward-looking nonearnings disclosure and overinvestment. The British Accounting Review, 56(6), 101431. https://doi.org/10.1016/j.bar.2024.101431
<!-- rendered-citations:end -->
