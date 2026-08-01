---
family_id: F064
columns:
- avg_rare_word_c2_ctx
- avg_rare_word_c2_full
- avg_rare_word_c2_ss
- avg_rare_word_c5_ctx
- avg_rare_word_c5_full
- avg_rare_word_c5_ss
- avg_rare_word_ctx
- avg_rare_word_full
- avg_rare_word_ss
unit: 无量纲比率 (银行-年内文章级低频词占比的均值, 理论值域 [0,1])
formula: "avg_rare_word{track} = mean_{article in bank-year}(rare_word_ratio{track}); rare_word_ratio = n_rare / n_real; n_rare = #{token w : FREQ(w) <= cutoff and not non_lexical(w)}; n_real = 非标点实词 token 数; cutoff = 3.0 (jieba 0.42.1 冻结词典正词频第 20 百分位实测值); c2/c5 变体取 cutoff in {2.0, 5.0}; track in {full, ctx, ss}; 文章级比率 round 6 位, den<=0 或过短文本返 NaN, 面板 'mean' 自动跳过 NaN"
producer: "news_process/pipeline/sentiment/lexical_complexity.py::compute_lexical_complexity (文章级, 三轨由 tone_words 驱动) ; news_process/pipeline/panel/encode.py (bank-year 'mean' 聚合)"
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 22_tone_words.parquet (文章级 rare_word_ratio 及 rare_word_ratio_c2 / rare_word_ratio_c5 变体臂, 三轨物化)
citations:
- doi: 10.1057/s41599-025-06094-y
  type: journal
  authors: Lesmy, D., Muchnik, L., & Mugerman, Y.
  year: 2025
  title: "Lost in the fog: growing complexity in financial reporting—a comparative study"
  venue: Humanities and Social Sciences Communications
  vol: 12
  issue: 1
  pages_or_artno: 1813
- doi: "10.3390/bdcc9100263"
  type: "journal"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
- doi: 10.1057/s41310-024-00240-9
  type: journal
  authors: Du, Y.-G., Li, S., Kuo, N.-T., & Li, D.
  year: 2025
  title: "Does the annual report readability improve corporate R&D investment? Evidence from China"
  venue: International Journal of Disclosure and Governance
  vol: 22
  issue: 2
  pages_or_artno: 440-460
- doi: 10.1103/rxxz-lk3n
  type: journal
  authors: Rosillo-Rodes, P., San Miguel, M., & Sánchez, D.
  year: 2025
  title: "Entropy and type-token ratio in gigaword corpora"
  venue: Physical Review Research
  vol: 7
  issue: 3
  pages_or_artno: 033054
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
- doi: 10.1016/j.ribaf.2024.102220
  type: journal
  authors: Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y.
  year: 2024
  title: "Annual report readability and trade credit financing: Evidence from China"
  venue: Research in International Business and Finance
  vol: 69
  issue: ''
  pages_or_artno: 102220
- doi: 10.1057/s41599-024-03162-7
  type: journal
  authors: Jiang, Z., Hu, L., & Wang, Z.
  year: 2024
  title: "Better or worse? Revealing the impact of common institutional ownership on annual report readability"
  venue: Humanities and Social Sciences Communications
  vol: 11
  issue: 1
  pages_or_artno: 688
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.1016/j.pacfin.2023.102074
  type: journal
  authors: Li, F., Yang, M., & Zhang, T.
  year: 2023
  title: "Does prospectus readability matter for bond issuance pricing? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 80
  issue: ''
  pages_or_artno: 102074
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: China Journal of Accounting Studies
  vol: 7
  issue: 3
  pages_or_artno: 407-437
- doi: 10.1111/1475-679X.12179
  type: journal
  authors: Bushee, B. J., Gow, I. D., & Taylor, D. J.
  year: 2018
  title: "Linguistic complexity in firm disclosures: Obfuscation or information?"
  venue: Journal of Accounting Research
  vol: 56
  issue: 1
  pages_or_artno: 85-121
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: "Annual report readability, tone ambiguity, and the cost of borrowing"
  venue: Journal of Financial and Quantitative Analysis
  vol: 52
  issue: 2
  pages_or_artno: 811-836
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: The Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
- doi: 10.1111/j.1540-6261.2008.01362.x
  type: journal
  authors: Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S.
  year: 2008
  title: "More than words: Quantifying language to measure firms' fundamentals"
  venue: The Journal of Finance
  vol: 63
  issue: 3
  pages_or_artno: 1437-1467
- doi: "10.1111/fima.70003"
  type: journal
  authors: "Abbassi, W., Ben-Nasr, H., Boubaker, S., & Eshraghi, A."
  year: 2025
  title: "Financial Statement Readability and Firm Debt Choice"
  venue: "Financial Management"
- doi: "10.1177/27533743251349221"
  title: "Text Analysis of Corporate Cryptocurrency Disclosures in Varying Market Conditions"
  authors: "Elitzur, R., & Rotenberg, W."
  year: 2025
  venue: "Journal of Alternative Finance"
  type: "journal"
- doi: "10.1057/s41599-025-05560-x"
  title: "Lexical richness in Chinese university students' EFL writing: a corpus-based comparison"
  authors: "Yang, Y., & He, X."
  year: 2025
  venue: "Humanities and Social Sciences Communications"
  type: "journal"
new_dois:
  - "10.3390/bdcc9100263"
  - "10.1111/fima.70003"
  - "10.1177/27533743251349221"
  - "10.1057/s41599-025-05560-x"
---

## CORE

【构念与来源】
本家族度量银行与金融科技新闻报道的低频词占比 (rare word ratio, 亦称罕见词率), 是"披露可读性与文本复杂度"这一信息集里的词汇难度维度。构念的直觉很朴素: 一篇报道若充斥低频、专业、生僻的词汇, 各类读者 (投资者、储户、监管者、同业机构) 的阅读理解成本就会上升, 信息被延迟消化甚至错误消化的概率随之上升; 反之若报道以高频常见词为主, 内容更易被快速处理、更快进入决策。金融科技报道恰恰是这一构念的高价值应用场景: 区块链、供应链金融、生物识别、开放银行、监管沙盒、隐私计算这类新兴术语密度高、演化快, 罕见词率因此能敏感地刻画一家银行被报道文本的专业化与晦涩程度, 而这种晦涩既可能来自真实的技术含量, 也可能来自刻意的信息模糊。文章级度量把一篇报道切成实词序列, 统计其中"词频不高于某个阈值"的词所占的比重; 家族列再把这一文章级比率在银行与年份 (bank-year) 维度上取算术平均, 得到某家银行在某一年被媒体报道文本的平均词汇稀有度。构念的方法学母锚是 You 与 Zhang (2009): 他们证明财务报告复杂度会引发投资者对 10-K 信息的欠反应, 复杂度越高, 信息进入价格的速度越慢; 本家族把这条"复杂度阻碍信息处理"的核心逻辑, 从企业自我披露的年报场景迁移到第三方新闻报道场景, 度量的不是银行自己怎么写, 而是媒体怎么写它。数据来源是本项目的中文银行与金科新闻语料, 经三轨文本物化 (content_full 全文、content_ctx 实体窗口、content_ss 银行与金科同句共现, 由 stage 14 ctx_materializer 生成), 在 stage 22 tone_words 内对每一轨各计算一次文章级低频词率, 再由面板导出阶段的 encode 做银行-年均值聚合。整个度量族是零成本的: 无付费大模型、无新增第三方依赖、不触碰 M0 审批门、不改动 Prompt v8, 完全基于冻结的 jieba 0.42.1 词典及其词频分布确定性派生, 属于可完整复现的 $0 词汇测度, 也正因如此可以稳定地作为跨版本一致的文本难度基线。

【方法学与计算】
文章级计算的核心是对一篇报道做一次 jieba.posseg 词性标注 pass。为保证确定性, 分词与词频读取都走一个独立、未被任何领域词注入污染的 jieba Tokenizer 实例 (即 jieba-isolation 隔离), 使同一段文本无论全局分词器处于何种注入态, 都恒定返回同一取值, 不受其它阶段 add_word 领域词注入所带来的词频与切分漂移。具体流程是: 一篇报道先被切成"词与词性"配对序列, 剔除词性标为标点或未知 (x) 的 token, 得到实词序列, 其长度记为 n_real, 充当所有比率的公共分母; 若 n_real 为零 (空文本或纯标点), 则整篇直接返回 NaN。分子 n_rare 统计同时满足两个条件的实词: 其一, 该词在冻结词典中的正词频不高于 cutoff 阈值 (词典外的 OOV 词其词频记为零, 因而也被判为低频); 其二, 该词不是纯数字或纯拉丁字母的 token。第二个排除谓词是关键的构念纯化 (修 omni-g-numlex-04): 阿拉伯数字、年份、英文缩写、带百分号的数值这类 token, 因为不在中文词典而词频为零, 会机械地命中"低频"判据, 但它们与词汇难度这一构念毫无关系, 且与数字密度测度机械同源, 若计入就会同时污染两个构念的独立性, 故一律排除; 与此同时分母 n_real 的口径保持不变, 与家族内其余各比率完全一致, 保证各比率可比。cutoff 阈值由 jieba 冻结词典正词频分布的第 20 百分位派生而来; 但由于低频侧存在巨量并列 (词频恰等于 2 的词约有四万个、词频恰等于 3 的词约有十六万个), 这个百分位在 jieba 0.42.1 上的实测落点恰为 3.0, 并由门控测试锚死 _rare_word_cutoff 恒等于 3.0, 以防词典升级带来的阈值漂移。文章级比率等于 n_rare 除以 n_real, 结果保留六位小数; 面板聚合采用 'mean' 聚合器, 它会自动跳过短文本或空文本产生的 NaN, 因而这些无效样本不会污染银行-年均值。三轨的驱动逻辑值得强调: 文章级函数本身对轨道无感, 输入单一文本、输出一份 per-text 字典, 三轨的 per-track 循环由调用方 tone_words 用 content_full、content_ctx、content_ss 三份文本各调用一次实现, 因而底层计算完全一致, 三轨之间的差异纯粹来自输入文本的取材范围。面板聚合口径需要专门说明: 家族列取的是"文章级比率在银行-年内的算术平均" (即先算每篇的比率再取均值), 而不是"银行-年内所有报道合并成一个超级文档后再算一次比率" (即先合并分子分母再算比率); 两种口径在数学上并不等价, 前者给每篇报道等权、后者给长报道更大权重, 本家族一律采用前者 (mean-of-ratios), 与 lexical_complexity 家族其余成员保持口径统一, 也与 encode 层的 'mean' 聚合契约一致。这样做的一个直接好处是: 单篇极短或极长的报道不会主导某个银行-年的取值, 度量更贴近"这一年关于该银行的报道通常有多难读"这一群体平均的解读。文章级比率保留六位小数, 是为了在跨运行复现时消除浮点尾数的抖动, 与 jieba-isolation 隔离一起, 共同保证本族列在冻结环境下逐位可复现。

【文献定位】
本家族嵌在会计与金融的文本可读性与复杂度测量传统之中。以词频权重承载信息含量的文本经济学谱系 (词频与逆文档频率的思路), 为"用词的稀有度反映信息量与阅读成本"提供了方法学底座。在披露可读性一侧, Li (2008) 最早把年报可读性 (Fog 指数) 与当期盈余、盈余持续性联系起来, 开辟了可读性影响信息处理的实证路线; Loughran 与 McDonald (2014) 则系统批判了 Fog 指数在金融文本上的失灵, 指出其中的复杂词计数在金融语境高度失真, 并提出以文件体量等更稳健的可读性代理, 二者共同界定了本项目"报道难读程度"这一构念的测量边界与陷阱。Bonsall、Leone、Miller 与 Rennekamp (2017) 提出的 Bog 指数从句法层面细化了可读性, Bushee、Gow 与 Taylor (2018) 对披露语言复杂度做了"混淆抑或信息"的两面性辨析, Ertugrul、Lei、Qiu 与 Wan (2017) 提供了可读性与借款成本相关的证据——它们共同表明文本复杂度既可能是刻意混淆的产物, 也可能是必要专业性的自然结果, 因此本家族刻意不预设符号, 把低频词率当作中性的词汇难度信号交给下游识别策略处理。在词内容分析一侧, Tetlock、Saar-Tsechansky 与 Macskassy (2008) 以及 Jegadeesh 与 Wu (2013) 确立了"以词衡量企业基本面与情感"的范式, García、Hu 与 Rohrer (2023) 进一步刻画了金融词汇的语义色彩, 这些工作把"词"本身作为经济信息的载体, 与本家族用词频稀有度提取信息负荷的思路同源。中文语境下的对应工作尤为贴近本项目: Xu、Yao 与 Chen (2019) 系统构建并检验了中文年报可读性测度, 为中文文本难度的度量提供了本土参照; Li、Yang 与 Zhang (2023) 检验招股书可读性对债券发行定价的作用, Li、Yang、Xue 与 Liu (2024)、Jiang、Hu 与 Wang (2024)、Du、Li、Kuo 与 Li (2025) 则分别把中文年报可读性与商业信用融资、机构共同持股、企业研发投资相连, 共同证明中文披露可读性具有实质经济后果。在近期方法学一侧, Loughran 与 McDonald (2024) 提出了企业复杂度的直接测度, Lesmy、Muchnik 与 Mugerman (2025) 以比较研究记录了财务报告复杂度的持续增长趋势, Siano (2025) 展示了以大模型捕捉词语上下文的新闻披露测量, Rosillo-Rodes、San Miguel 与 Sánchez (2025) 从熵与类符-形符比角度刻画大规模语料的词汇统计规律; Abbassi、Ben-Nasr、Boubaker 与 Eshraghi (2025, Financial Management) 则考察财务报表可读性对企业债务融资选择的影响, 为披露文本难度 (与本家族罕见词率同属可读性与复杂度测量谱系) 如何传导至融资结果提供了 2025 年的最新实证证据。这些近作共同勾勒出本家族的坐标: 它位于"传统词频稀有度"与"新一代语境嵌入"之间, 以最低成本、最强可复现性承担词汇难度的基线测量。近期还有两支旁证值得一提: Elitzur 与 Rotenberg (2025, Journal of Alternative Finance) 研究企业加密货币相关信息披露文本在不同市场条件下的可读性与复杂度差异, 发现涉及加密货币的段落比同一报告其余部分更易读, 提示企业存在选择性简化叙述的策略, 为"披露主体可能对特定新兴议题段落做差异化文本处理"提供了跨市场证据; Yang 与 He (2025, Humanities and Social Sciences Communications) 以语料库方法比较中国大学生英语写作中的词汇丰富度 (含词汇稀有度与复杂度维度), 为中文语境下以低频词占比刻画文本词汇难度提供方法学参照。

【识别策略定位】
本家族在识别策略上的定位可以分五层来理解。第一层是成本与正交性: 它是零成本、纯词典派生的词汇难度信号, 与需要付费大模型或嵌入接口的语境测度 (例如 Siano (2025) 式的大模型上下文捕捉) 相互正交——更换 canonical 嵌入模型 (由 Google 系嵌入迁至阿里 Qwen)、更换情感大模型三家投票里的任一厂商, 都不会改动本族的任何一个取值, 因为整条计算链只依赖冻结的 jieba 0.42.1 词典及其确定性派生, 与嵌入空间、与情感大模型完全解耦。正因如此, 它可以作为跨版本稳定、不随模型漂移的可读性代理稳定地进入回归方程, 承担"锚"的角色: 当论文需要一个不随测量技术升级而共动的文本难度控制变量时, 低频词率恰好满足这一要求, 也因此能充当"换模型稳健性检验"里的安慰剂式对照——它对更换嵌入或情感大模型本应毫无反应, 一旦有反应反而提示接线错误。第二层是构念的重构 (reframe): 本族被明确定位为"第三方新闻报道的词汇难度", 而不是企业自我披露的信息具体性——语料是媒体报道而非年报或 10-K, 因此论文措辞必须与此一致, 不能直接照搬年报可读性文献的因果解读。报道的难读可能有三种彼此无法在测度上自动区分的来源: 一是媒体的专业化叙述 (记者认真拆解某项金融科技的机制), 二是议题本身的技术门槛 (区块链、隐私计算、监管沙盒等术语天然生僻), 三是通稿式的机构语言堆砌; 归因因此须由识别设计承担而非由测度本身承担。第三层是它在论文组合中的角色: 作为 bank_news_clarity (银行新闻清晰度, provisional) 一线的核心构念之一, 低频词率既可以作为解释变量直接刻画报道的可读性渠道 (难读的报道是否延缓了信息进入价格、抬高了融资成本), 也可以作为可读性控制变量, 吸收文本难度对其它测度 (如情感、注意力) 的混杂影响, 使那些测度的系数不被"这一年关于该银行的报道恰好更难读"这一维度污染; 作为解释变量时须结合报道后的市场反应、分析师行为或融资成本共同识别符号, 作为控制变量时则以中性姿态进入、不承载因果解读。第四层是留篇门控与行宇宙: 行宇宙的口径严格遵循 full-only 留篇门控 (2026-06-29), 一篇报道是否计入"银行金科报道", 只看 full 轨的大模型核验结果 (llm_verified_full 为真), 而 ctx 与 ss 两轨是条件在 full 留篇集之上的 conditional-on-full 测度与稳健性轨, 它们的 per-track 列在这个固定子集内照常计算。这一点在识别上尤为关键: 因为三轨共享同一个由 full 决定的行宇宙, full 轨与 ctx/ss 轨之间的差异是纯粹的测量差异 (取材范围不同), 而不是样本构成差异 (留篇集不同), 因此把三轨并排解读为"取材敏感性"是干净的, 不会与样本选择效应混淆; 分母 n_articles 亦按 full-only 留篇集统计并由三轨共享。第五层是确定性与解释的双向性: 度量的确定性来自 jieba-isolation 隔离与冻结词典, 对全局分词器的注入保持字节不变, 因此本族列可以作为 golden 可复现测试中的确定性锚定成分, 不引入非确定漂移 (与政治词权重、BERT 分布形状等纯后处理 $0 测度同属可逐位复现层)。需要额外提醒的是, 罕见词率在解释上是双向的: 一方面, 高罕见词率可能对应真实的技术含量与专业深度 (报道认真讨论了某项金融科技的机制), 是信息丰富的信号; 另一方面, 它也可能对应刻意的术语堆砌与信息模糊 (用生僻词包装以掩盖实质), 是混淆的信号——这正是 Bushee、Gow 与 Taylor (2018) 所辨析的"混淆抑或信息"两面性。本族因此刻意不预设方向, 把符号的确定交给具体论文的识别设计 (例如结合报道后的市场反应、分析师行为或融资成本来判断难读到底帮助还是妨碍了信息处理), 而不在测度层面强加解读; 这也意味着做稳健性并排时应把三阈值、三轨各自 just-identified 地并排报告, 而不是把它们塞进同一个 over-identified 设定去追求单一"最优"系数。

【与相邻测度的构念区分】
低频词率必须与 lexical_complexity 家族的其余成员严格区分, 以避免共线误用与构念混淆; 该家族在同一次 posseg 词性标注 pass 上派生出多个互补测度, 彼此机械相关但刻画不同的语言构念。相对难字率 (hard_char_ratio), 本族在词的层面统计术语稀有度, 而难字率在字的层面统计非常用汉字的占比, 二者的计量粒度不同 (词对字), 可以互补但绝非同一构念——一篇报道可能用词生僻但用字常见 (由常见字拼出的专业新词), 也可能用字艰深但用词平常; 机械上二者虽同源于 jieba 冻结词典的频率派生, 却分别落在词轴与字轴上, 不应同时进入同一回归方程以免重复计入。相对类符-形符比 (type_token_ratio, 面板 avg_ttr), 那是词汇多样性维 (不重复词数除以总词数), 度量"用词丰富程度", 而本族度量"用词稀有程度": 一篇报道完全可以类符-形符比很高 (几乎不重复用词) 但所有词都是高频常见词 (稀有度低), 也可以反过来反复使用少数几个生僻术语 (类符-形符比低但稀有度高), 两者在同一篇上可以正交甚至反向。Rosillo-Rodes、San Miguel 与 Sánchez (2025) 特别提醒, 重尾的词频分布 (齐夫式并列) 会同时影响类符-形符比与稀有度统计量的行为, 因此这两个统计量虽都源于词频分布, 却仍刻画不同的语言维度, 不可互相替代。相对每词字符数 (char_per_word, 面板 avg_cpw), 那度量的是词的平均长度, 而稀有度与词长并不等价——很多长词是高频常见词 (如常见机构全称), 很多短词却是低频专有词, 因此词长与稀有度是两条独立的难度线索。相对硬信息密度 (specificity_index) 与纯具名实体密度 (named_entity_ratio), 那两者度量的是报道中实体与硬数量信息的密度, 即信息的具体性, 与词汇难度处在不同的轴上 (具体性对难度); 尤其要强调的是, 低频词率的分子已经刻意剔除了纯数字与纯拉丁 token (修 omni-g-numlex-04), 因此它与数字密度类测度在机械层面已经脱钩, 不会因为一篇报道数字多就虚高, 而 specificity 恰恰把"硬"数词计入其分子, 二者构造方向相反; named_entity_ratio 又是 specificity 的真子集 (只留具名实体、不含硬数词), 与 specificity 高度共线, 但那一对共线关系与本族无关。相对名词化率 (nominalization_ratio) 与功能词比率 (function_word_ratio), 前者刻画句法层面的抽象化 (动词或形容词憋成抽象名词的官腔程度), 后者刻画虚词与实词的配比 (LIWC Analytic 维的中文近似), 都属于句法或语体维度, 而稀有度纯粹是词汇频率维度: 一段官腔十足、名词化严重的文字完全可以全用高频常见词写成 (稀有度低), 反之亦然。相对逆接连词密度 (adversative_ratio), 那捕捉转折、让步的论证结构密度, 与用词稀有度毫无重叠。相对文档内冗余 (within_doc_redundancy 及其汉字口径孪生) 以及跨文档套话比率 (boilerplate) 与陈旧度 (staleness), 那些测度捕捉的是重复: within_doc_redundancy 是单篇内部的字符或汉字 3-gram 自重复 (篇内重复), boilerplate 与 staleness 是文章之间的雷同与陈旧 (篇间重复), 而本族捕捉的是单篇文章内部的词汇难度, 与"重复"这一维正交——一篇零重复的报道可以极难读, 一篇高度自重复的报道也可以极易读。特别地, within_doc_redundancy 有强机械长度依赖 (文档越长, 常用 3-gram 重复概率机械上升), 回归时须配套控制 ln 长度; 而本族是比率, 对长度的机械依赖弱得多 (仅极短文本因分母过小导致比率粒度变粗), 这也是二者在稳健性面板中角色不同的一个体现。识别上的纪律因此是明确的: 这些相邻测度可以各自并排进入稳健性面板, 各刻画各的构念面, 但机械上高度共线的成对 (例如低频词率与难字率同源于词频派生) 不应同时进入同一个回归方程, 以免把同一信息重复计入、扭曲系数与显著性。就本家族内部而言, 九列构成一个"三阈值 (2、3、5) 乘以三轨 (full、ctx、ss)"的三乘三网格: 阈值轴刻画"多罕见才算罕见"的口径敏感性, 轨道轴刻画"从报道哪一部分取材"的取材敏感性, 两轴彼此正交、含义不同。同一阈值不同轨的三列 (如 c2 的 full、ctx、ss) 差在取材范围, 同一轨不同阈值的三列 (如 full 轨的 c2、canonical、c5) 差在罕见门槛; 这张网格既让研究者能沿任一轴单独做敏感性检验, 也提醒使用者切勿把同网格里高度相关的多列一并塞进单一 over-identified 设定, 而应遵循"各自 just-identified 并排、互为稳健性不分主次"的纪律逐一并排报告。

【已知局限与稳健性梯子】
第一条必须诚实披露的局限是覆盖口径问题: 由于冻结词典低频侧存在巨量并列 (词频恰等于 2 的词约有四万个、词频恰等于 3 的词约有十六万个), 名义上的"第 20 百分位"cutoff 在 jieba 0.42.1 上的实测落点是 3.0, 而用"不高于"谓词判定时会把词频不超过 3 的词全部计入, 使 canonical 低频词率实际覆盖冻结词典约 57% 的 distinct 词类 (若把词典外的 OOV 词一并计入, 覆盖率进一步升至约 70%), 因此它度量的其实是"非高频词率", 而不是紧致的最稀有 20% 尾部; 论文与 spec 必须如实这样表述, 绝不能声称它是"低频 20% 阈值"或"最稀有五分之一词", 否则就是对度量口径的夸大, 这是本族在方法学诚实性上最容易被误读、也最需要守住的一点。第二条是词典年份 (vintage) 偏差: 冻结的 jieba 0.42.1 词典是一份定格于某一时点的词表, 而语料横跨 2007 至 2025 年 (生产 T=19)。金融科技领域术语演化极快, 后期出现的新造词 (新平台名、新监管概念、新技术缩略) 很可能不在这份定格词典中而被判为 OOV (词频记零、必然命中低频), 于是稀有度可能随年份出现一个部分源于词典年份而非报道本身的系统性上升趋势。这一偏差在解释上有两面: 一方面新技术术语本就应当被视为罕见 (与构念方向一致, 属可接受近似), 另一方面它意味着跨年份比较须谨慎, 时间固定效应或年份趋势项能吸收其中与词典年份同步的成分, 论文若做时间维解读须显式控制并披露这一点。第三条是分词近似与短文本粒度: 稀有度以 jieba.posseg 的分词结果为"词"的单位, 而 posseg 走词典加 HMM, 其切分与词性边界是一种近似 (对专名与歧义的处理精度低于专用工具), 不同切分会把同一串字重新归类进不同的频率档, 因此本族度量的是"给定 jieba 0.42.1 切分口径下的词稀有度"——冻结词典与 jieba-isolation 隔离保证了这一口径的确定性与可复现, 但它是对"词汇难度"这一抽象构念的一个具体化近似而非唯一真值。对极短文本 (ctx 或 ss 窗口在无共现回退前可能很短), 分母 n_real 很小会使比率粒度变粗 (取值跳跃), 而 n_real 为零时整篇返回 NaN、由面板 'mean' 聚合器自动跳过, 不污染银行-年均值; 面板采用 mean-of-ratios (每篇等权) 而非合并超级文档口径, 好处是单篇极端长度不主导取值, 代价是长报道与短报道在银行-年均值里权重相同, 这一加权选择须与家族口径一致地理解。第四条是频次 cutoff 梯子: 为了检验可读性结论不被单一截断阈值驱动, 家族在 canonical (cutoff 等于 3) 之外, 额外物化了 cutoff 为 2 与 5 的两条变体臂 (文章级的 rare_word_ratio_c2 与 rare_word_ratio_c5, 以及面板级的 avg_rare_word_c2 与 avg_rare_word_c5)。之所以按频次而不是按分位来参数化, 是因为冻结词典的低频并列使分位梯子发生数学退化——第 30 百分位与第 20 百分位在这个冻结词典上逐字节恒等, 会构成一条毫无信息增量的假稳健臂; 而按频次取 2、3、5 时, 三个阈值在词典上分别覆盖约 11.6%、57.2%、63.4% 的 distinct 词类, 三条臂真正互异, 才构成有意义的稳健性梯子。cutoff 为 2、3、5 的三条臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; 该梯子与词典规则消融梯度、政治词权重梯子彼此正交、不交叉 (三种权重与三套规则都在各自维度上独立计算, 以避免维度相乘导致列数爆炸)。canonical 采用无后缀命名, 这是历史命名的产物而非语义上的"主", 恰如政治词权重梯子里 polw05 等于 canonical 的口径。第五条是三轨稳健性: full、ctx、ss 三轨同为本家族的规格稳健性并排轨, full 轨是承担留篇门控的 headline canonical, ctx 与 ss 是互为稳健的条件轨, 三轨各自 just-identified 并排、互为稳健性不分主次, 同样严禁混进同一个 over-identified Hansen J。ss 轨的回退语义严格镜像 ctx: 当一篇报道不存在银行词与金科词的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真; 若金科自动机整体缺失 (FINTECH_AC 为空), 则各轨的 is_fallback 全部置真、优雅降级, 分母共享 n_articles。门控测试 test_rare_word_cutoff_ladder.py 锚死 canonical 的分位派生 cutoff 恒等于 3.0 (词典漂移即红), 并校验三条频次臂的 cutoff 取值两两互异 (2、3、5, 防退化假臂), 从而同时防住词典漂移与假稳健臂两类隐患。此外, 本族在极短早期试跑样本 (T=2) 上的行为会退化 (银行-年内文章极少时均值不稳), 属该样本的预期现象, 真实生产语料 (T=19) 下不构成问题。

## VAR: avg_rare_word_c2_ctx

【变体差分】
本列是频次 cutoff 梯子最紧一臂 (cutoff 等于 2) 与 ctx 轨的交叉, 相对家族 canonical (avg_rare_word_full, cutoff 等于 3 且 full 轨) 在阈值与轨道两个轴上同时偏移。阈值轴上, cutoff 取 2 意味着只把冻结词典正词频不高于 2 的词 (含词典外的 OOV 零频词) 判为低频, 对应词典上约 11.6% 的 distinct 词类, 是三条频次臂里覆盖最窄、判定最严格的一臂——它更靠近"真正罕见、极低频的专业术语"这一直觉, 相比 canonical 排除了词频恰为 3 的那一大批中低频词, 因此对普通书面语用词更不敏感, 只在报道真正使用生僻术语时才升高。轨道轴上, ctx 轨的文本是 content_ctx, 即标题 prepend 之后拼接实体窗口内的正文片段 (目标银行邻近上下文), 而不是整篇正文; 因此本列度量的是"在围绕目标银行的上下文片段里, 极罕见词的占比在银行-年上的均值", 它只关心报道谈及该银行时的那些段落, 对整篇里与银行无关的内容不敏感。相对同为 c2 臂的 avg_rare_word_c2_full, 本列把文本取材从全文收窄到实体上下文窗口, 数值反映的是报道在谈及该银行的局部段落中的词汇稀有度; 相对同为 ctx 轨的 avg_rare_word_ctx 与 avg_rare_word_c5_ctx, 本列在同一取材范围上把阈值收到最严, 三者共同构成 ctx 轨内的阈值梯子最严端。作为 cutoff 等于 2 的臂与 ctx 轨的组合, 本列与 c3、c5 各臂以及 full、ss 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁与其它阈值臂或其它轨混进同一个 over-identified Hansen J 检验。ctx 轨在留篇口径上是条件于 full 留篇集的 conditional-on-full 轨, 其行宇宙是 full 轨留篇集的子集。

## VAR: avg_rare_word_c2_full

【变体差分】
本列是频次 cutoff 梯子最紧一臂 (cutoff 等于 2) 与 full 轨的交叉, 是 canonical 列在"更严格阈值"方向上的稳健臂, 也是三条 c2 臂里唯一覆盖整篇文本的一条。阈值轴上, 相对 canonical 的 cutoff 等于 3, 本列把低频判据收紧到词频不高于 2, 只保留冻结词典里约 11.6% 的最罕见 distinct 词类作为分子候选; 直观上它剔除了词频恰为 3 的那一大批"次低频"词, 使度量更贴近"极罕见专业术语密度", 而不是宽口径的"非高频词率", 因此在解释上更能对应报道使用生僻新术语的程度。轨道轴上, full 轨的文本是 content_full, 即标题 prepend 之后的整篇正文, 与 canonical 完全同轨; 因此本列与 avg_rare_word_full 之间的唯一差异纯粹来自阈值 (2 对 3), 构成最干净、最直接的阈值敏感性对照。它要回答的问题是: 如果把"罕见"的门槛调到最严, 一家银行被报道文本的平均罕见词密度会如何变化, 基于 canonical 的主结论是否依然成立。相对 avg_rare_word_c2_ctx 与 avg_rare_word_c2_ss, 本列覆盖整篇文本而不是实体窗口或金科同句共现窗口, 因此其分母 n_real 最大、样本内信号最平滑、对局部片段的选取最不敏感。作为 cutoff 等于 2 的臂与 full 轨的组合, 本列与 c3、c5 各臂以及 ctx、ss 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; 其行宇宙遵循 full-only 留篇门控, 即以 full 轨大模型核验为准判定一篇报道是否计入。

## VAR: avg_rare_word_c2_ss

【变体差分】
本列是频次 cutoff 梯子最紧一臂 (cutoff 等于 2) 与 ss 轨 (银行与金科同句共现轨) 的交叉。阈值轴上与整个 c2 系列一致: cutoff 取 2, 只把词频不高于 2 的极罕见词 (含词典外 OOV) 计入分子, 覆盖冻结词典约 11.6% 的 distinct 词类, 是最严格的罕见度门槛, 因而只在报道出现真正生僻的术语时才升高。轨道轴上, ss 轨的文本是 content_ss, 即标题 prepend 之后拼接"银行词与金融科技词处于同一句 (以配置的句窗为半径) 共现"的片段, 是三轨里最聚焦银行与金科交汇语境的一轨; 因此本列度量的是"在既提及该银行又提及金科的同句语境里, 极罕见词的占比之银行-年均值", 它最贴近银行谈论金融科技时的用词稀有度。ss 轨的回退语义严格镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真; 若金科自动机整体缺失, 则整轨优雅降级为全真回退, 分母与其它轨共享 n_articles, 保证分母口径一致。相对 avg_rare_word_c2_full 与 avg_rare_word_c2_ctx, 本列把文本进一步从全文、从实体窗口收窄到金科同句共现窗口, 只在无共现时才回退到全文, 因此其信号在三条 c2 臂里最聚焦金科议题; 相对同为 ss 轨的 avg_rare_word_ss 与 avg_rare_word_c5_ss, 本列在同一取材范围上取最严阈值, 三者构成 ss 轨内阈值梯子的最严端。作为 cutoff 等于 2 的臂与 ss 轨的组合, 本列与 c3、c5 各臂以及 full、ctx 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; ss 轨在留篇口径上是条件于 full 留篇集的条件轨。

## VAR: avg_rare_word_c5_ctx

【变体差分】
本列是频次 cutoff 梯子最宽一臂 (cutoff 等于 5) 与 ctx 轨的交叉。阈值轴上, cutoff 取 5 把低频判据放宽到词频不高于 5, 覆盖冻结词典约 63.4% 的 distinct 词类, 是三条频次臂里覆盖最广、判定最宽松的一臂——它在 canonical 的约 57.2% 之上又纳入了词频为 4 和 5 的一批中频词, 因而度量更接近"广义非高频词率", 对纯罕见术语的敏感性下降、对一般书面语用词的敏感性上升, 数值也更平缓。轨道轴上, ctx 轨读取 content_ctx (标题 prepend 加实体窗口正文片段), 因此本列度量的是"在目标银行的上下文片段里, 宽口径低频词占比之银行-年均值", 它只关心报道谈及该银行的那些邻近段落, 对整篇里与银行无关的内容不敏感。相对 avg_rare_word_c5_full, 本列把文本取材从整篇收窄到实体窗口, 因此在同为最宽阈值的前提下更聚焦银行上下文; 相对 avg_rare_word_c2_ctx 与 canonical 的 ctx 臂 (avg_rare_word_ctx), 本列在同一 ctx 轨上把阈值放到最宽, 三者共同构成 ctx 轨内部由严到宽的阈值敏感性梯子。作为 cutoff 等于 5 的臂与 ctx 轨的组合, 本列与 c2、c3 各臂以及 full、ss 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; ctx 轨为条件于 full 留篇集的 conditional-on-full 轨, 其行宇宙是 full 轨留篇集的子集。

## VAR: avg_rare_word_c5_full

【变体差分】
本列是频次 cutoff 梯子最宽一臂 (cutoff 等于 5) 与 full 轨的交叉, 是 canonical 列在"更宽松阈值"方向上的稳健臂, 也是三条 c5 臂里唯一覆盖整篇文本的一条。阈值轴上, 相对 canonical 的 cutoff 等于 3, 本列把低频门槛放宽到词频不高于 5, 覆盖冻结词典约 63.4% 的 distinct 词类, 在 canonical 之上额外纳入词频为 4 与 5 的中频词; 因此本列度量的是"广义非高频词率", 相对 c2 臂 (约 11.6%) 与 canonical (约 57.2%) 更平缓, 数值更多受一般书面用词而非纯罕见术语驱动, 是阈值梯子里最不挑剔的一端。轨道轴上, full 轨读取 content_full (标题 prepend 之后的整篇正文), 与 canonical 完全同轨; 因此本列与 avg_rare_word_full 之间的差异纯粹来自阈值 (5 对 3), 它与 avg_rare_word_c2_full 一起, 与 canonical 共同构成 full 轨上"最严、中值、最宽"三点式的阈值敏感性对照。它要回答的问题是: 如果把"罕见"的门槛放到最宽, 银行被报道文本的平均低频词密度是否仍然给出与 canonical 一致的结论, 从而证明主结论不被截断阈值的具体取值驱动。相对 avg_rare_word_c5_ctx 与 avg_rare_word_c5_ss, 本列覆盖整篇文本, 因此分母 n_real 最大、样本内信号最平滑、对局部片段选取最不敏感。作为 cutoff 等于 5 的臂与 full 轨的组合, 本列与 c2、c3 各臂以及 ctx、ss 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; 行宇宙遵循 full-only 留篇门控。

## VAR: avg_rare_word_c5_ss

【变体差分】
本列是频次 cutoff 梯子最宽一臂 (cutoff 等于 5) 与 ss 轨 (银行与金科同句共现轨) 的交叉。阈值轴上与整个 c5 系列一致: cutoff 取 5, 把词频不高于 5 的词全部计入分子, 覆盖冻结词典约 63.4% 的 distinct 词类, 是最宽松的罕见度门槛, 度量偏向"广义非高频词率", 更多受一般书面用词而非纯生僻术语驱动。轨道轴上, ss 轨读取 content_ss (标题 prepend 加银行与金科同句共现片段), 是三轨里最聚焦银行与金科交汇语境的一轨, 因此本列度量的是"在银行谈论金科的同句语境里, 宽口径低频词占比之银行-年均值"。ss 轨的回退语义严格镜像 ctx: 当无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真; 若金科自动机缺失, 则整轨优雅降级为全真回退, 分母与其它轨共享 n_articles。相对 avg_rare_word_c5_full 与 avg_rare_word_c5_ctx, 本列把文本取材从全文、从实体窗口进一步收窄到金科同句共现窗口 (只在无共现时才回退全文), 因此在三条 c5 臂里最聚焦金科议题; 相对 avg_rare_word_c2_ss 与 canonical 的 ss 臂 (avg_rare_word_ss), 本列在同一 ss 轨上把阈值放到最宽, 三者共同构成 ss 轨内部由严到宽的阈值敏感性梯子。作为 cutoff 等于 5 的臂与 ss 轨的组合, 本列与 c2、c3 各臂以及 full、ctx 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; ss 轨为条件于 full 留篇集的条件轨。

## VAR: avg_rare_word_ctx

【变体差分】
本列是 canonical 阈值 (cutoff 等于 3) 在 ctx 轨上的稳健孪生, 即 avg_rare_word_full 的 ctx 轨对照。阈值轴上, 本列采用与 canonical 完全相同的 cutoff 等于 3 (词频不高于 3 计入, 覆盖冻结词典约 57.2% 的 distinct 词类), 不带 c2 或 c5 后缀, 因此它并不是阈值变体, 而是 canonical 度量在另一轨上的本体。与 canonical 的唯一差异落在轨道: 本列读取 content_ctx (标题 prepend 加实体窗口正文片段) 而不是整篇 content_full, 度量的是"在围绕目标银行的上下文片段里, 低频词占比之银行-年均值"。它的意义在于把 canonical 的低频词率从整篇口径收窄到实体邻近上下文, 用以检验主结论是否依赖于对与银行无关段落的纳入——如果一篇报道有大量篇幅在讲与该银行无关的话题, full 轨与 ctx 轨就会分歧, 本列因此是 full 轨的一线规格稳健性对照, 帮助判断词汇难度信号是否来自银行相关的核心叙述。相对 avg_rare_word_c2_ctx 与 avg_rare_word_c5_ctx, 本列在同一 ctx 轨上取中值阈值, 三者共同构成 ctx 轨内阈值梯子的中枢。作为 canonical 阈值的 ctx 轨, 本列与 full、ss 各轨以及 c2、c5 各阈值臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; ctx 轨在留篇口径上是条件于 full 留篇集的 conditional-on-full 轨, 其行宇宙是 full 轨留篇集的子集。

## VAR: avg_rare_word_full

【变体差分】
本列是家族的 canonical 列, 也是本家族唯一的 core 列: cutoff 等于 3 且走 full 轨, 是低频词率家族的规范定义, 其余八列都以它作为参照系来定位自己在阈值轴与轨道轴上的偏移。阈值轴上, 它采用 jieba 0.42.1 冻结词典正词频第 20 百分位的实测 cutoff 3.0——由于低频侧存在巨量并列 (词频恰等于 2 的词约有四万个、恰等于 3 的词约有十六万个), 这个百分位的实测落点恰在 3.0, 再用"不高于"谓词判定, 使其覆盖冻结词典约 57.2% 的 distinct 词类。这里有一条必须诚实披露的口径边界: 该列名义上对应"低频 20% 阈值", 但由于词频并列, 实际覆盖了过半的 distinct 词类, 因此它度量的其实是"非高频词率", 而不是紧致的最稀有 20% 尾部; 论文与 spec 的表述必须与此一致, 不得声称它是紧致的 20% 尾部或"最稀有五分之一词", 这是本列在方法学诚实性上最容易被误读、也最需要守住的一点。无后缀命名 (不带 c2 或 c5) 是历史命名的产物, 而非语义上的"主", 这一点镜像政治词权重梯子里 polw05 等于 canonical 的口径; 它之所以被选为 core, 是因为 cutoff 等于 3 恰是频次梯子 (2、3、5) 的中值臂, 且与项目中既有的无后缀列逐字节一致, 不另发重复列, 因而承担家族的规范锚点。轨道轴上, full 轨读取 content_full (标题 prepend 之后的整篇正文), 它是三轨里唯一承担留篇门控的轨: 一篇报道是否计入"银行金科报道", 只看 full 轨的大模型核验结果 (llm_verified_full 为真), 而 ctx 与 ss 两轨的行宇宙都是这个 full 留篇集的子集, 属于条件在 full 留篇之上的 conditional-on-full 测度。计算细节上, 分子 n_rare 统计词频不高于 3 且既非纯数字又非纯拉丁的实词, 分母 n_real 是整篇文本的非标点实词数; 文章级比率保留六位小数, 面板取银行-年 'mean' 并自动跳过短文本或空文本产生的 NaN。分子对纯数字与纯拉丁 token 的排除 (修 omni-g-numlex-04) 是构念纯化的关键: 这类 OOV token 因词频为零而会机械命中低频判据, 但它们与词汇难度这一构念无关、又与数字密度测度机械同源, 排除之后本列在机械层面与 num_intensity 彻底脱钩, 不会因为报道数字多就虚高。整个计算走一个独立未注入的 jieba Tokenizer, 对全局分词器的领域词注入保持字节不变, 因而本列可以充当 golden 可复现测试里的确定性锚, 不引入非确定漂移。构念上, 本列承接 You 与 Zhang (2009) 关于"复杂度阻碍信息处理"的核心逻辑, 并把它从企业自我披露迁移到第三方新闻报道场景, 与 Loughran 与 McDonald (2014) 界定的金融文本可读性测量边界保持一致, 在论文组合中是 bank_news_clarity 一线刻画报道词汇难度的核心解释变量与可读性控制变量。在阈值梯子上, 本列是 full 轨"最严 (c2)、中值 (canonical)、最宽 (c5)"三点式敏感性对照的中枢参照点, 其余两点 (avg_rare_word_c2_full 与 avg_rare_word_c5_full) 都以它为基准检验"把罕见门槛调严或调宽后主结论是否依然成立"; 在轨道上, 本列又是 ctx 与 ss 两条条件轨 (avg_rare_word_ctx、avg_rare_word_ss) 的规格稳健性基准, 三轨共享同一 full-only 留篇行宇宙, 因此本列与两条轨的差异是取材范围的纯测量差异而非样本构成差异。识别上, 本列因整条计算链只依赖冻结 jieba 词典而与 canonical 嵌入模型、情感大模型三家投票完全解耦, 更换嵌入 (Google 系迁至阿里 Qwen) 或更换任一情感厂商都不会改动其取值, 故它既是跨版本稳定、不随测量技术升级共动的可读性锚, 也可充当"换模型稳健性检验"里的安慰剂式对照 (对更换本应零反应)。就本 full 轨而言, 覆盖整篇正文意味着它承载全文范围内的 OOV token: 冻结词典定格于某一时点, 而语料横跨 2007 至 2025 年, 后期新造的金融科技术语易被判为 OOV (词频记零、必然命中低频), 使跨年份的稀有度可能带有部分源于词典年份的系统性成分, 做时间维解读时须以时间固定效应或年份趋势项吸收并显式披露。聚合与缺失处理上, 文章级比率经 _safe_div 在分母大于零时保留六位小数、否则返回 NaN, 面板取银行-年 'mean' 并自动跳过短文本或空文本产生的 NaN, 采用每篇等权的 mean-of-ratios 口径而非合并超级文档口径, 使单篇极端长度不主导某个银行-年的取值。作为频次梯子的中值臂与 full 轨的组合, 本列与 c2、c5 各阈值臂以及 ctx、ss 各轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; 该频次梯子又与词典规则消融梯度、政治词权重梯子彼此正交、不交叉。门控测试 test_rare_word_cutoff_ladder.py 锚死其分位派生 cutoff 恒等于 3.0 (词典漂移即红), 并校验三条频次臂的 cutoff 取值两两互异 (2、3、5), 用以同时防住冻结词典漂移, 以及分位梯子退化所可能产生的假稳健臂。

## VAR: avg_rare_word_ss

【变体差分】
本列是 canonical 阈值 (cutoff 等于 3) 在 ss 轨 (银行与金科同句共现轨) 上的稳健孪生, 即 avg_rare_word_full 的 ss 轨对照。阈值轴上, 本列采用与 canonical 相同的 cutoff 等于 3 (词频不高于 3 计入, 覆盖冻结词典约 57.2% 的 distinct 词类), 不带 c2 或 c5 后缀, 因此它是 canonical 度量在另一轨上的本体, 而不是阈值变体。与 canonical 的差异纯粹落在轨道: 本列读取 content_ss (标题 prepend 加银行与金科同句共现片段), 是三轨里最聚焦银行与金科交汇语境的一轨, 度量的是"在银行谈论金科的同句语境里, 低频词占比之银行-年均值"。ss 轨的回退语义严格镜像 ctx: 当一篇报道不存在银行与金科的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置真; 若金科自动机整体缺失, 则整轨优雅降级为全真回退, 分母与其它轨共享 n_articles, 保持分母口径一致。相对 avg_rare_word_ctx (canonical 的 ctx 轨), 本列把上下文取材从实体窗口进一步收窄到金科同句共现窗口, 信号更贴近银行与金科交汇的核心语境, 因而对报道是否真正在谈金融科技更敏感; 相对 avg_rare_word_c2_ss 与 avg_rare_word_c5_ss, 本列在同一 ss 轨上取中值阈值, 三者共同构成 ss 轨内阈值梯子的中枢。作为 canonical 阈值的 ss 轨, 本列与 full、ctx 各轨以及 c2、c5 各阈值臂互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一个 over-identified Hansen J 检验; ss 轨在留篇口径上是条件于 full 留篇集的 conditional-on-full 轨。

<!-- rendered-citations:begin -->
Lesmy, D., Muchnik, L., & Mugerman, Y. (2025). Lost in the fog: growing complexity in financial reporting—a comparative study. Humanities and Social Sciences Communications, 12(1), 1813. https://doi.org/10.1057/s41599-025-06094-y
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
Du, Y.-G., Li, S., Kuo, N.-T., & Li, D. (2025). Does the annual report readability improve corporate R&D investment? Evidence from China. International Journal of Disclosure and Governance, 22(2), 440-460. https://doi.org/10.1057/s41310-024-00240-9
Rosillo-Rodes, P., San Miguel, M., & Sánchez, D. (2025). Entropy and type-token ratio in gigaword corpora. Physical Review Research, 7(3), 13868. https://doi.org/10.1103/rxxz-lk3n
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y. (2024). Annual report readability and trade credit financing: Evidence from China. Research in International Business and Finance, 69, 102220. https://doi.org/10.1016/j.ribaf.2024.102220
Jiang, Z., Hu, L., & Wang, Z. (2024). Better or worse? Revealing the impact of common institutional ownership on annual report readability. Humanities and Social Sciences Communications, 11(1), 688. https://doi.org/10.1057/s41599-024-03162-7
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Li, F., Yang, M., & Zhang, T. (2023). Does prospectus readability matter for bond issuance pricing? Evidence from China. Pacific-Basin Finance Journal, 80, 102074. https://doi.org/10.1016/j.pacfin.2023.102074
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in firm disclosures: Obfuscation or information? Journal of Accounting Research, 56(1), 85-121. https://doi.org/10.1111/1475-679X.12179
Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. Journal of Financial and Quantitative Analysis, 52(2), 811-836. https://doi.org/10.1017/S0022109017000187
Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. The Journal of Finance, 69(4), 1643-1671. https://doi.org/10.1111/jofi.12162
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words: Quantifying language to measure firms' fundamentals. The Journal of Finance, 63(3), 1437-1467. https://doi.org/10.1111/j.1540-6261.2008.01362.x
Abbassi, W., Ben-Nasr, H., Boubaker, S., & Eshraghi, A. (2025). Financial Statement Readability and Firm Debt Choice. Financial Management. https://doi.org/10.1111/fima.70003
Elitzur, R., & Rotenberg, W. (2025). Text Analysis of Corporate Cryptocurrency Disclosures in Varying Market Conditions. Journal of Alternative Finance. https://doi.org/10.1177/27533743251349221
Yang, Y., & He, X. (2025). Lexical richness in Chinese university students' EFL writing: a corpus-based comparison. Humanities and Social Sciences Communications. https://doi.org/10.1057/s41599-025-05560-x
<!-- rendered-citations:end -->
