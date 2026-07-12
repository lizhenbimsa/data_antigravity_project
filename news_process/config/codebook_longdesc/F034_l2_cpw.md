---
family_id: F034
columns:
- avg_cpw_ctx
- avg_cpw_full
- avg_cpw_ss
unit: 字符/词 (平均词长, 无量纲比率)
formula: "char_per_word = (sum_{t in real_tokens} len(t)) / max(len(real_tokens), 1); avg_cpw{track} = bank-year mean of char_per_word{track} (mean 自动跳过 NaN)"
producer: news_process/pipeline/sentiment/tone_words.py (article-level char_per_word) ; news_process/pipeline/panel/encode.py (bank-year avg_cpw{track})
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (char_per_word{track})
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: Growing complexity in financial reporting—A comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  pages_or_artno: "06094"
- doi: 10.1016/j.rmal.2024.100168
  type: journal
  authors: Bestgen, Y.
  year: 2025
  title: "Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons"
  venue: Research Methods in Applied Linguistics
  vol: 4
  issue: 1
  pages_or_artno: "100168"
- doi: 10.1016/j.jcae.2023.100395
  type: journal
  authors: Yu, F., & Zhao, Y.
  year: 2024
  title: "Textual disclosure complexity and analysts' weighting of information"
  venue: Journal of Contemporary Accounting & Economics
  pages_or_artno: "100395"
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: The Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
new_dois: []
---

## CORE

【构念与来源】
本家族 avg_cpw (average characters per word, 平均词长) 度量的是一家银行在给定年度所获媒体报道的用词专业化程度, 是一个文本可读性 (readability) 的字符级代理指标。其构念根植于会计与金融文本分析的一条经典发现: 用词越冗长、越倾向术语化, 文本认知负荷越高、读者理解成本越大。Loughran 与 McDonald (2014) 在系统评估年报可读性度量时指出, 传统的 Fog 指数把长词与长句一并计入, 但在金融语境里长词 (多音节、专业术语) 才是真正推高理解成本的成分, 而句长的信息量很弱; 由此可读性研究把"词的复杂度"单列为一个正交维度。avg_cpw 正是这一维度在中文语料上的落地: 中文没有天然的音节切分, 我们改以"平均每个词包含多少个汉字/字符"作为词复杂度的代理——一个词占用的字符越多, 越可能是复合专业术语 (如"资产证券化""普惠金融")而非日常口语词。该指标与同族的平均句长 (avg_sentence_len)、词汇丰富度 (type_token_ratio) 构成一个三维可读性剖面, 三者各自捕捉句法、词汇多样性与词长三个不相互替代的侧面。数据来源为项目主语料——2007 至 2024 年中国银行/金融科技新闻报道 (生产规模约 1700 万条、面板深度 T=18); 每篇报道先经 stage 14 物化出 full/ctx/ss 三轨文本, 再由 stage 22 的词典法引擎逐篇计算 char_per_word, 最终在 stage 40 面板导出时聚合为 bank-year 均值 avg_cpw{track}。

【方法学与计算】
文章级 char_per_word 的计算见 tone_words.py 的可读性代理函数: 先以 jieba 对报道正文分词, 随后彻底剔除标点与空白 token (标点集覆盖 ASCII 标点与全角中文标点、换行/制表/回车), 仅保留真实词汇 token (real_tokens); 分子为所有真实 token 的字符长度之和 total_chars, 分母为真实 token 数 n_real_tokens (以 max(len, 1) 防零除), 商即平均词长, 保留四位小数。之所以先剔标点, 是为了防止无意义标点被当作独立"词"稀释或夸大字符/词计数——这一去标点口径与同族 type_token_ratio 严格一致, 保证词长与词汇丰富度共享同一分词底盘。面板聚合在 encode.py 的可读性控制块 (H 段, 注明依据 Loughran & McDonald 2014) 完成: avg_cpw{track} = 该 bank-year 内所有留篇文章 char_per_word{track} 的算术均值。此处须精确澄清本列的缺失语义, 以免与"填 NaN 后由 mean 跳过"的一般口径混淆: 文章级 char_per_word 恒为数值, 从不产出 NaN——分母以 max(len(real_tokens), 1) 兜底, 故真实词 token 为空时商为 total_chars/1=0.0; 整篇空文本走哨兵初始化路径亦显式置 char_per_word=0.0。换言之极短或空文本得到的是一个真实计算出的 0.0 并计入年度均值, 而非一个被聚合层跳过的缺失值。pandas 的 mean 聚合在泛化意义上确会跳过 NaN, 但对本列而言 producer 已在文章级把 NaN 来源消除, 该跳过分支在本列上实际不被触发。因此该列是一个纯 $0 后处理测度 (无 LLM、无 API、无嵌入调用), 在 prompt 与 jieba 版本冻结下逐位可复现。留篇口径遵循 2026-06-29 起的 full-only 门控: 一篇报道是否计入某银行某年的分母, 只由 llm_verified_full 判定; full 轨在留篇全集上计算, ctx/ss 轨则在其 full 留篇子集上以各自轨文本条件计算 (conditional-on-full), 三轨共享同一 n_articles 分母定义但各读各轨文本。

【文献定位】
avg_cpw 属于文本即数据 (text-as-data) 范式下的语言学特征工程。Gentzkow、Kelly 与 Taddy (2019) 把文本特征提取组织为从词计数到高维表征的统一框架, avg_cpw 处在其中最轻量、最可解释的"表层语言学度量"一端。Bochkay、Brown、Leone 与 Tucker (2023) 的会计文本分析综述进一步把词典/词袋方法与上下文化预训练模型并置, 为本项目"词典 (stage 22) 与 BERT (stage 23) 与 LLM (stage 21) 三类方法并行"的总体架构提供了综述级定位——avg_cpw 是其中词典法一侧的非极性 (non-polarity) 语言学控制变量, 服务于"控制文本复杂度后情感信号是否稳健"这一识别关切。可读性度量本身的方法学争议由 Loughran 与 McDonald (2014, 2016) 与 Bonsall、Leone、Miller 与 Rennekamp (2017) 的 plain-English 度量所刻画: 后者论证综合可读性 (含用词) 优于单一 Fog, avg_cpw 取"词长"这一 plain-English 子维度作银行媒体语料的近似。文本复杂度的经济后果在近期文献中持续被验证: Yu 与 Zhao (2024) 发现披露文本复杂度影响分析师对信息的加权, Lesmy、Muchnik 与 Mugerman (2025) 记录了财务报告复杂度的跨期增长及其对可理解性的侵蚀; 二者共同支撑"词长是有经济含义的报道属性"这一前提。需强调 avg_cpw 是词长而非词汇多样性: Bestgen (2025) 对移动平均 type-token ratio 的评估提醒, 词长与词汇丰富度是两个不可相互替代的复杂度轴, 这正是本项目将 cpw、ttr、sentence_len 分列三个面板列而非合成单一可读性分的方法学理由。

## VAR: avg_cpw_full

【变体差分】
本列为 full 轨的银行-年度平均词长, 对应文本轨道 = 标题 prepend + 全文正文 (content_full)。在三轨 (full/ctx/ss) 体系中, full 轨读取的是每篇报道经 stage 14 物化的完整正文 (标题前置拼接、原始正文全量), 因此其 char_per_word 反映整篇报道的整体用词专业化水平, 而非仅围绕银行/金融科技实体的局部片段。就留篇门控而言 (2026-06-29 full-only 口径), full 轨直接定义了本银行本年度的留篇全集——一篇报道是否被判为"一篇银行金融科技报道"只看 llm_verified_full, 故 avg_cpw_full 的分母 n_articles 即该银行年度留篇总数, 无需任何条件化。与 ctx/ss 两轨相比, full 轨文本最长、覆盖面最广, 用词分布最接近报道原貌, 因而通常作为可读性控制的首选参照轨; 但三轨在方法学上是互为稳健性、不分主次的并排关系, 各自 just-identified, 严禁把 avg_cpw_full 与 avg_cpw_ctx/avg_cpw_ss 混入同一个 over-identified Hansen J 检验 (这会人为制造过度识别并污染工具变量诊断)。本轨与家族其余两轨的唯一差分即在于输入文本的取材范围 (整篇 vs 实体窗口 vs 同句窗口), 计算公式、去标点口径、jieba 分词底盘、bank-year mean 聚合方式三者完全一致。作为控制变量, avg_cpw_full 通常与情感/属性主轨一同进入回归以剥离"报道本身更术语化"这一混淆——当某银行某年的媒体报道普遍用词更专业时, 其情感强度或关注度的读取可能受文本复杂度系统性影响, 控制 avg_cpw_full 即吸收这一表层语言学干扰。该列取值恒为正 (字符/词比率), 在中文语料上典型落在单字词与双字/多字复合词的混合水平, 越高表示复合专业术语占比越大、报道越难读。

## VAR: avg_cpw_ctx

【变体差分】
本列为 ctx 轨的银行-年度平均词长, 对应文本轨道 = 标题 + 实体上下文窗口 (content_ctx)。ctx 轨在 stage 14 物化时仅保留报道中围绕目标实体 (银行、金融科技词) 的上下文窗口片段并前置标题, 因此 avg_cpw_ctx 度量的是"报道谈及该银行时那几段文字"的用词专业化程度, 而非整篇报道 (后者是 full 轨)。相对 full 轨, ctx 轨过滤掉了与目标实体无关的背景叙述, 用词分布更贴近报道对该银行的实质性描写, 是一个把噪声段落剥离后的稳健性轨。就门控而言, ctx 轨为 conditional-on-full 测度: 其行宇宙是 full 留篇集的子集, 逐轨各算各的 char_per_word_ctx, 但计入分母的报道仍由 full-only 门控确定; 当某篇报道缺 content_ctx 列时, 文本层按回退公理回退到全文正文 (content_ctx→'内容') 再前置标题, 故此时 char_per_word_ctx 实际等于以全文文本算出的词长而非缺失值; 当该轨文本为空 (real_tokens 为空) 时, 分母的 max(len,1) 兜底使 char_per_word_ctx=0.0。两种情形均得到一个真实数值而非 NaN——本列从不产 NaN, 亦无需依赖 mean 跳过缺失。与 full/ss 两轨的关系是互为稳健性、不分主次的并排: 三轨各自 just-identified, 严禁把本列与 avg_cpw_full/avg_cpw_ss 混入同一个 over-identified Hansen J。本轨与家族 canonical 的唯一差分即取材范围收窄至实体上下文窗口, 其余计算链路 (去标点、分词、四位小数、bank-year 均值) 与 full/ss 逐条一致。作为稳健性轨, avg_cpw_ctx 的价值在于检验"整篇报道更术语化"这一 full 轨结论是否由与该银行无关的背景段落驱动: 若剥离背景后词长结论逆转, 则说明复杂度并非来自对该银行的实质描写; 若结论一致, 则强化了词长作为报道属性的稳健性。因取材片段更短, ctx 轨在极短文本上更易得到分母兜底下的 0.0 或回退到全文文本的词长值; 须明确该 0.0 是 max(len,1) 兜底下的真实计算结果并如实计入年度均值, 而缺列情形则回退到全文文本, 二者都不是被 mean 跳过的 NaN。故 avg_cpw_ctx 与 avg_cpw_full 在年度均值上的差异, 来自取材范围 (实体窗口 vs 整篇) 本身, 而非两轨在缺失处理口径上的不同。

## VAR: avg_cpw_ss

【变体差分】
本列为 ss 轨的银行-年度平均词长, 对应文本轨道 = 标题 + 银行与金融科技同句共现的 ±N 句窗口 (content_ss, 默认 ss_sentence_radius=1)。ss 轨是三轨中取材最严格的一轨: 仅当报道中出现银行与金融科技词同句共现时, 才截取该共现句及其前后各一句作为 content_ss 并前置标题, 因此 avg_cpw_ss 度量的是"报道把该银行与金融科技并置论述那一小段"的用词专业化程度, 最贴近银行×金融科技这一核心构念的局部文本。回退语义镜像 ctx 轨: 当某报道无银行与金融科技的同句共现时, content_ss 优雅回退为全文 body 并置 ss_is_fallback=True (与 ctx 的 fallback 口径一致, 共享 n_articles 分母); 若上游 FINTECH_AC 为 None 则该轨 *_is_fallback 全 True 全篇回退。就门控而言, ss 轨同为 conditional-on-full 测度, 行宇宙是 full 留篇集子集, 逐轨独算; 缺 content_ss 列时文本层按回退链回退到 content_ctx 再到全文正文 (content_ss→content_ctx→'内容'), 空文本则经 max(len,1) 分母兜底得 char_per_word_ss=0.0, 两种情形均得到真实数值而非 NaN (本列不产 NaN, 不依赖 mean 跳过缺失)。dev 小样本 (T=2) 上 ss 轨可能因共现稀疏而高度回退或方差退化, 属预期现象, 生产 T=18 语料下正常。与 full/ctx 两轨互为稳健性、不分主次, 各自 just-identified, 严禁把本列与 avg_cpw_full/avg_cpw_ctx 混入同一个 over-identified Hansen J。本轨与家族 canonical 的唯一差分即取材范围收窄至银行与金融科技同句±1 窗口 (含回退分支), 其余计算链路与另两轨逐条一致。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: Growing complexity in financial reporting—A comparative study. Humanities and Social Sciences Communications, 12, 06094. https://doi.org/10.1057/s41599-025-06094-y
Bestgen, Y. (2025). Estimating lexical diversity using the moving average type-token ratio (MATTR): Pros and cons. Research Methods in Applied Linguistics, 4(1), 100168. https://doi.org/10.1016/j.rmal.2024.100168
Yu, F., & Zhao, Y. (2024). Textual disclosure complexity and analysts' weighting of information. Journal of Contemporary Accounting & Economics, 100395. https://doi.org/10.1016/j.jcae.2023.100395
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. The Journal of Finance, 69(4), 1643-1671. https://doi.org/10.1111/jofi.12162
<!-- rendered-citations:end -->
