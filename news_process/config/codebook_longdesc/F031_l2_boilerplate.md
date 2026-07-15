---
family_id: F031
columns:
- avg_boilerplate_ctx
- avg_boilerplate_full
- avg_boilerplate_ss
unit: 比率 [0,1] (无量纲; 跨文档套话 n-gram 命中占比)
formula: "boilerplate_phrase_ratio_trk = 命中套话集的 char_wb(4,6)-gram 出现总数 / 该篇全部 char_wb(4,6)-gram 出现总数; 套话集 = 本轨语料上 DF/N >= 0.10 的 n-gram (语料级 exact two-pass, 逐轨独立构建); avg_boilerplate_trk = bank-year mean(boilerplate_phrase_ratio_trk), trk 属于 full/ctx/ss"
producer: "news_process/pipeline/sentiment/boilerplate.py::enrich_with_boilerplate (stage 22 tone_words 派生增强子步骤, 文章级三列) ; news_process/pipeline/panel/encode.py (stage 40 bank-year mean 聚合)"
upstream:
- 14_news_with_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_words_tone.parquet (boilerplate_phrase_ratio_full / _ctx / _ss 文章级三列)
citations:
- doi: 10.1007/s11142-026-09950-7
  type: journal
  authors: "Gietzmann, M., Grossetti, F., & Lewis, C. M."
  year: 2026
  title: "Investor distraction and multi-dimensional financial narrative"
  venue: Review of Accounting Studies
  vol: 31
  issue: 1
  pages_or_artno: 334-373
- doi: "10.1016/j.accinf.2026.100775"
  type: "journal"
  authors: "Haapamäki, E., & Sihvonen, J."
  year: 2026
  title: "Mandatory cybersecurity disclosure: Early evidence from 10-K reports"
  venue: "International Journal of Accounting Information Systems"
- doi: 10.1057/s41599-024-04169-w
  type: journal
  authors: "Zhu, X., Li, J., & Wang, Y."
  year: 2024
  title: "Are risk disclosures in financial reports informative? A text mining-based perspective"
  venue: Humanities and Social Sciences Communications
  vol: 11
  issue: 1
  pages_or_artno: "1653"
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: "Cao, S., Jiang, W., Yang, B., & Zhang, A. L."
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.2139/ssrn.4425527
  type: wp
  authors: "Kim, A. G., Muhn, M., & Nikolaev, V. V."
  year: 2023
  title: "Bloated disclosures: Can ChatGPT help investors process information?"
  venue: SSRN Working Paper No. 4425527
- doi: 10.1016/j.pacfin.2023.102074
  type: journal
  authors: "Li, F., Yang, M., & Zhang, T."
  year: 2023
  title: "Does prospectus readability matter for bond issuance pricing? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 80
  pages_or_artno: "102074"
- doi: 10.1016/j.jacceco.2020.101344
  type: journal
  authors: "Blankespoor, E., deHaan, E., & Marinovic, I."
  year: 2020
  title: "Disclosure processing costs, investors' information choice, and equity market outcomes: A review"
  venue: Journal of Accounting and Economics
  vol: 70
  issue: 2-3
  pages_or_artno: "101344"
- doi: 10.1111/jofi.12885
  type: journal
  authors: "Cohen, L., Malloy, C., & Nguyen, Q."
  year: 2020
  title: "Lazy prices"
  venue: The Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1111/1475-679X.12179
  type: journal
  authors: "Bushee, B. J., Gow, I. D., & Taylor, D. J."
  year: 2018
  title: "Linguistic complexity in firm disclosures: Obfuscation or information?"
  venue: Journal of Accounting Research
  vol: 56
  issue: 1
  pages_or_artno: 85-121
- doi: 10.1016/j.jacceco.2017.07.002
  type: journal
  authors: "Dyer, T., Lang, M., & Stice-Lawrence, L."
  year: 2017
  title: "The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation"
  venue: Journal of Accounting and Economics
  vol: 64
  issue: 2-3
  pages_or_artno: 221-245
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: "Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K."
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.2308/acch-51240
  type: journal
  authors: "Cazier, R. A., & Pfeiffer, R. J."
  year: 2016
  title: "Why are 10-K filings so long?"
  venue: Accounting Horizons
  vol: 30
  issue: 1
  pages_or_artno: 1-21
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: "Hope, O.-K., Hu, D., & Lu, H."
  year: 2016
  title: "The benefits of specific risk-factor disclosures"
  venue: Review of Accounting Studies
  vol: 21
  issue: 4
  pages_or_artno: 1005-1045
- doi: 10.1016/j.jacceco.2015.09.002
  type: journal
  authors: "Lang, M., & Stice-Lawrence, L."
  year: 2015
  title: "Textual analysis and international financial reporting: Large sample evidence"
  venue: Journal of Accounting and Economics
  vol: 60
  issue: 2-3
  pages_or_artno: 110-135
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: "Li, F."
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
- doi: "10.1111/ijau.12343"
  type: journal
  authors: "Seebeck, A."
  year: 2024
  title: "Back to where it started?—Do expanded auditor's reports become sticky, generic and boilerplate over time?"
  venue: "International Journal of Auditing"
- doi: "10.3390/ijfs11040147"
  type: journal
  authors: "Su, F., Zhai, L., & Liu, J."
  year: 2023
  title: "Do MD&A Risk Disclosures Reduce Stock Price Crash Risk? Evidence from China"
  venue: "International Journal of Financial Studies"
  vol: "11"
  issue: "4"
  pages_or_artno: "147"
# citations_pool.md 关键词 'boilerplate, template' 检索 top-0 且所属论文 refs 段空
# (pipeline 级家族无 manuscript 映射) — 按 pool 首行铁律走 new_dois 台账申报如下 15 条。
# 逐条已核验均属全仓 874-DOI 白名单锚点 (LITERATURE_ANCHORS_2026-06-13 / SUPPLEMENT_III /
# EXPANSION 等), 非白名单外新增 DOI; 申报供 Crossref 回比与对抗五元组复核。
new_dois:
- 10.1007/s11142-026-09950-7
- 10.1057/s41599-024-04169-w
- 10.1093/rfs/hhad021
- 10.2139/ssrn.4425527
- 10.1016/j.pacfin.2023.102074
- 10.1016/j.jacceco.2020.101344
- 10.1111/jofi.12885
- 10.1146/annurev-financial-012820-032249
- 10.1111/1475-679X.12179
- 10.1016/j.jacceco.2017.07.002
- 10.1016/j.jacceco.2017.03.002
- 10.2308/acch-51240
- 10.1007/s11142-016-9371-1
- 10.1016/j.jacceco.2015.09.002
- 10.1016/j.jacceco.2008.02.003
- "10.1111/ijau.12343"
- "10.1016/j.accinf.2026.100775"
- "10.3390/ijfs11040147"
---

## CORE

该文用文本分析考察美国上市公司在SEC强制网络安全披露新规下Item 1C披露的长度、冗余度(套话/redundancy)与具体性,发现披露质量受公司规模、财务表现、审计师质量与同业惯例驱动,为跨文档冗余/套话类文本测度在新兴强制披露情境下的应用提供了2026年的最新证据。

【构念与来源】
avg_boilerplate 家族度量的是"跨文档套话比率"(boilerplate phrase ratio): 一篇银行金融科技报道之中, 命中"跨语料高频公式化短语集合"的字符 n-gram 出现次数, 占该篇全部字符 n-gram 出现次数的比例, 取值域为零到一的闭区间, 数值越高说明该篇报道的措辞越模板化、公式化, 原创信息含量越低。用白话说, 这个指标回答的问题是: 这篇新闻里有多大比例的文字是"车轱辘话"——诸如"本报讯""记者报道""有限公司""股份制商业银行"这类在整个语料库里高频反复出现的固定搭配——而不是记者针对这家银行、这件事写出的新内容。构念的学术源头在会计学的叙事披露质量文献: Lang 与 Stice-Lawrence (2015) 在跨国财务报告大样本上首次把 boilerplate 操作化为"同语料内跨公司共享的高频四元词组句", 并证明套话占比更高的披露对应更差的市场流动性与更弱的信息含量, 这是把"模板化语言"从修辞批评转为可计量测度并给出经济后果的奠基工作; Dyer、Lang 与 Stice-Lawrence (2017) 在对上市公司年报文本三十年演化的追踪中给出了"由至少四分之三公司共享的四元词组"这一具名阈值口径, 并显示监管披露要求的层层加码使年报套话逐年膨胀; Cazier 与 Pfeiffer (2016) 则从文档长度分解的角度论证, 年报越写越长的主要驱动正是模板化、重复性内容而非增量信息。本项目把这一构念从英文年报语料移植到中文银行新闻语料: 中文财经新闻的生产端存在显著的通稿文化与格式化写作惯例, 大量报道由固定导语、机构简介模板与监管话术拼接而成, 套话命中率天然构成"这篇报道有多少是媒体流水线产物"的代理变量。Cao、Jiang、Yang 与 Zhang (2023) 提示在机器读者时代, 文本生产者会针对算法调整措辞, 对文本特征的机器化测量必须考虑生产方的策略性写作, 而套话检测正是对模板化、策略化写作的直接应对之一; Kim、Muhn 与 Nikolaev (2023) 用大语言模型摘要构造信息冗胀测度并证明其资本市场后果, 为本项目以机器管线 (而非人工编码) 批量产出套话类测度提供了最新的方法正当性。数据来源与计算链路: stage 14 的 ctx_materializer 先物化三轨文本列 (content_full、content_ctx、content_ss, 标题一律前置拼接); stage 22 词典情感阶段末端的派生增强子步骤调用 boilerplate 模块, 对三轨文本逐轨执行语料级两遍统计, 产出文章级列 boilerplate_phrase_ratio_full、_ctx、_ss 并落盘 22_tone_words.parquet; stage 40 面板导出时由 encode 聚合器对文章级比率取银行-年算术均值, 得到本家族三列 avg_boilerplate_full、avg_boilerplate_ctx、avg_boilerplate_ss; stage 46 导出 Stata 时分别挂中文标签"跨文档套话比率"的全文轨、实体窗轨与同句轨。

【方法学与计算】
计算核心是语料级 exact two-pass (精确两遍) 算法。第一遍在本轨全部有效文档上, 用 char_wb 分析器统计四至六字符长度的全部 n-gram 的文档频率 (document frequency), 凡 DF 除以文档总数不低于百分之十者 (即出现在至少一成文档中的 n-gram) 构成该轨的"套话集"; 第二遍逐篇统计命中套话集的 n-gram 出现总数, 除以该篇全部 n-gram 出现总数, 即得该篇的套话比率。选四至六字符这一 n-gram 窗宽有中文构词学依据: 中文以双字词、三字词为基本成词单位, 四到六字符恰好覆盖"双字词接双字词""三字机构简称接功能词"这一层级的固定搭配 (如"股份有限""商业银行""本报讯记者"), 短于四字符的片段多为单字或碎词, 几乎篇篇出现而丧失区分力, 长于六字符则命中过稀、文档频率难以稳定越过阈值, 四到六因此是套话短语在中文语料里的自然承载尺度, 与英文以音节或整词为单位的可读性口径不同, 本项目顺应中文无词边界的特性改按字符窗统计。阈值百分之十是设计参数而非文献硬值——文献中的具名阈值是 Dyer、Lang 与 Stice-Lawrence (2017) 在英文年报场景下的"四分之三公司共享"口径, 本项目以"至少一成文档共享"的中文新闻落地变体复刻其阈值思想, 生产全量语料上该阈值可经稳健性网格微调, 此点已作为设计参数如实披露。工程实现上有一组被测试闸锁死的确定性命门: 向量器由单一工厂函数构造, 并以类型感知断言锁死最小文档频率为整数一、最大文档频率为浮点一点零、最大特征数为空——即无任何语料级剪枝, 这是"分块两遍与单遍逐字节等价"这一不变量成立的隐性前提, 断言把它从注释约定升格为运行时硬约束 (整数一与浮点一点零在数值上相等但在 sklearn 语义上天壤之别, 后者意味着百分之百剪枝); 套话集词表经字典序排序后传入第二遍向量器, 结果保留六位小数, 全程无哈希种子依赖, 纯 CPU 计算零 API 费用, 跨机器逐位可复现。分析器选 char_wb 而非 char 是为与 herd_decay 模块的既有范式保持一致; 中文文本基本不含词边界空格, 两种分析器在真实语料上的实测相关接近于一, 边界空格的影响可忽略。输入守卫方面: 非字符串、空串、哨兵字符串, 以及剔除零宽字符与各类空白 (含全角空格) 后实字数不足 n-gram 长度下界的退化文本, 一律记缺失值而非伪零; 守卫的退化判定在文本副本上进行, 对非退化文本原样返回, 保证喂给向量器的字节与旧实现完全一致。即便是真实盘面上篇幅最短的报道, 其实字数也远在字符 n-gram 下界 (四字符) 的退化边界之上, 因此正常语料几乎不触发退化缺失, 退化守卫主要拦截空串、哨兵字符串以及清洗后实字不足下界的畸形输入, 而非正常短报道; 这也意味着缺失率的跨轨差异主要由子窗轨 (ctx/ss) 的文本被截短所致, 而非 full 轨的正常报道被误判退化。安全语义方面: 若某轨语料上没有任何 n-gram 达到阈值 (套话集为空), 该轨整列置缺失并高声告警, 镜像金融科技词表缺失时"绝不静默清空"的全仓公理; 若某轨文本列在输入表中缺席, 该轨同样整列缺失加告警, 优雅降级不阻断整个阶段。内存硬化 (2026-07-06 执行计划) 把原始的单遍全词表拟合改造为分块精确两遍: 第一遍分块流式地精确累加全局文档频率字典, 顺带缓存每篇的 n-gram 总数; 第二遍用固定的小套话词表逐块变换统计命中, 与单遍实现逐字节等价 (golden 零漂移, 经字节等价参照臂与模糊测试双重验证)。默认分块两万篇, 内存档位 in_memory 为已实现的一级方案, 旧单遍实现冻结为字节等价参照臂受测试保护禁删 (安全规模上界五万篇, 超之高声告警); disk 与 auto 档位显式以 SystemExit 拒跑——刻意不用 NotImplementedError, 因为后者属于普通异常, 会被上游词典阶段的宽异常捕获吞成静默丢列。需要如实记录的工程边界是: 一级方案只消除了随语料线性增长的稀疏矩阵驱动项, 真正绑定内存的全局词频字典仍随语料规模增长, 其词条软预算与硬上限目前是未经校准的占位值, 生产全量语料首次播种前必须先实测单词条字节开销并按机器内存反推校准硬闸, "一级档位已落地"不等于"生产内存问题已解决"。聚合口径: encode 聚合器对文章级比率取银行-年算术均值, 均值自动跳过缺失值, 短文与退化文不污染格值; 旧版 parquet 未回填 ctx/ss 文章列时, 对应面板列经有效聚合过滤优雅缺席, 不阻断面板构建。

【文献定位】
本家族在文本测度谱系中的位置, 处于可读性文献与披露信息含量文献的交汇带。可读性一支由 Li (2008) 奠基——用迷雾指数类长句长文测度证明可读性与盈余持续性的关联, 开启"披露文本形态本身有信息"的研究纲领; Bonsall、Leone、Miller 与 Rennekamp (2017) 的 Bog 指数把句长、难词、被动语态等多维平实语言属性合成为单一可读性测度, 确立了"多词法特征并行合成"的方法路线; Loughran 与 McDonald (2020) 的权威综述则系统清点了可读性与复杂度测度的陷阱清单, 告诫研究者单一公式在财务文本上的失效模式, 支持本项目以十余族互补文本测度并行产出而非择一的总体设计。套话率不是可读性——模板句式往往平滑易读, 高套话完全可以对应低阅读难度——它属于叙事披露质量中"信息含量与原创性"的维度, 直接谱系是前述 Lang 与 Stice-Lawrence (2015)、Dyer 等 (2017)、Cazier 与 Pfeiffer (2016) 三部曲。Bushee、Gow 与 Taylor (2018) 把语言复杂度分解为信息成分与遮蔽成分的做法, 对套话解读同样成立: 部分套话承载法定披露格式与机构标识信息, 并非纯噪音, 因此本家族在回归中作为环境特征而非直接的"坏文本"评分使用。近期应用锚: Zhu、Li 与 Wang (2024) 以文本挖掘评估金融报告风险披露的信息含量, 把跨企业高频短语意义上的套话、具体性与相似度并列操作化为清晰度维度, 与本模块口径直接同法; Gietzmann、Grossetti 与 Lewis (2026) 在顶级会计期刊以多维叙事文本特征 (含可读性、数字含量与套话样维度) 度量披露并联结投资者注意力与市场反应, 是套话类多维度量的最新顶刊应用; 中文情境下, Li、Yang 与 Zhang (2023) 为债券募集说明书构造平实中文可读性指数并证明其定价后果, 为把英文文本形态框架适配到中文金融文本 (按字符与句式而非音节) 提供了同语言先例, 本项目的字符级 n-gram 口径正是顺应中文无词边界特性的同类适配。Su, Zhai & Liu (2023, International Journal of Financial Studies) 以中国A股上市公司MD&A风险披露为样本, 证明管理层可通过更复杂、更套话化的模糊表述策略性隐匿负面信息, 可读性更高的风险披露对应更低的未来股价崩盘风险, 为中文情境下套话/模板化语言的市场后果提供本土证据。理论骨架上, Blankespoor、deHaan 与 Marinovic (2020) 的信息处理成本框架 (知晓、获取、整合三阶段) 给出套话率的经济学解释: 套话降低单位文本的信息增量, 抬高投资者与储户从新闻中提取增量信号的整合成本; Cohen、Malloy 与 Nguyen (2020) 的懒惰价格研究证明文本"不变"本身就是被市场定价不足的信号, 与套话率构成互补的两面——前者量跨期的篇间重复, 后者量截面的跨文档模板命中。Seebeck (2024, International Journal of Auditing) 则以年度间相似度(粘性)、同业间相似度(通用性)与套话语言三重量表追踪审计报告文本随时间趋同的现象, 与本家族跨文档套话比率的测量取向直接同源。

【识别策略定位】
在多论文组合的识别设计中, avg_boilerplate 家族不担任任何一篇论文的主处理变量, 其角色定位有三重。第一重是信息环境质量控制变量: 在以情感、关注度为主处理变量的银行-年回归中, 套话率吸收"报道数量多但内容模板化"的银行-年格点, 防止把通稿灌水误读为媒体真实关注或真实情感信号——两家银行同样各有百篇报道, 若其一的报道套话率系统性更高, 其媒体测度的有效信息含量并不相同, 遗漏该维度会使报道数量类变量的系数混入媒体生产方式的异质性。这一控制在以媒体关注度为核心自变量的设定 (如以金融科技投资强度为结果变量的关注度篇) 里尤为吃紧: 报道计数是主回归的关键右手侧变量, 套话率能在同一计数水平上把"由通稿转载堆高的计数"与"由独立采写堆高的计数"区分开, 前者是媒体流水线的机械复制、后者是真实的媒体聚焦, 二者对存款人认知与银行融资行为的传导强度并不相等, 若不并入套话维度, 关注度系数便会把两种截然不同的媒体生产模式混为一谈。第二重是机制叙事的文本侧证据: 在信息处理成本渠道下, 套话率是"新闻可用性"的调节变量, 模板化报道对存款人与投资者行为的边际影响预期弱于原创报道, 该测度使处理成本机制可以在文本特征层面被直接刻画而非停留在叙述。第三重是测量效度审计维度: 与情感测度联合判读时, 高套话子样本上词典法与大模型法的情感分歧预期更大 (模板文本的情感词往往是程式化礼貌用语), 该列为跨方法一致性诊断提供了分层变量。面板行宇宙与全仓口径一致: 留篇门控为 full-only 口径 (2026-06-29 裁决), 一篇报道是否计入银行金融科技报道宇宙只看 llm_verified_full 是否为真, ctx 与 ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集; 本家族三列的银行-年聚合域与 avg_specificity 等同族文本控制变量完全一致, 注入时的覆盖闸即以两者缺失值掩码相等锁定。处理变量与结果变量分属两套体系, 本家族属文本特征控制族, 不进入三引擎工具变量扩展, 也不需要跨模型族际错误率校正——后者的先例只覆盖同一构念的替代性主测量, 本家族三列是同一算法在三种文本窗口上的规格并排, 属规格稳健性而非测量替代。

【与相邻测度的构念区分】
有四组相邻测度必须与本家族划清构念边界, 这也是源码文档字符串开宗明义强调的内容。第一, 与 within_doc_redundancy (篇内字符三元组自重复率) 正交: 篇内冗余量的是"这一篇自己有多啰嗦"——同一篇内部片段的自我重复; 套话率量的是"这一篇与全语料共有模板的重合度"——分母虽都是本篇 n-gram, 但判据集合一个来自篇内、一个来自跨文档统计, 一篇可以毫不自我重复却满纸通稿套话, 反之亦然, 两列在回归中分别提供独立变异。第二, 与 surface_staleness (基于 MinHash 的整篇两两相似度) 不同构念: 表层陈旧度问"这篇与既往某篇整体有多像", 是篇间成对结构上的相似度; 套话率问"这篇命中全语料高频短语库的比率", 没有成对结构, 不指认相似对象。两者同属非嵌入 carve-out 家族——纯字符统计, 与嵌入模型无关, 因此都没有 _lg 孪生列, 换嵌入模型时本家族全仓零改动。第三, 与 semantic_staleness (嵌入余弦相似度) 不同层次: 后者在语义空间度量内容相近, 本测度在表层字符空间度量短语命中, 一篇报道可以换尽措辞而语义陈旧 (语义陈旧度高、套话率不必高), 也可以满纸套话而所述事件全新。第四, 与 avg_specificity 及 avg_named_entity (Hope、Hu 与 Lu (2016) 的命名实体具体性口径) 构念互为镜像但非机械互补: 具体性量硬信息密度 (人名、地名、数量、时间), 套话量通用软模板占比, 一篇报道完全可以既多实体又多套话 (通稿常同时罗列机构全称与模板话术), 因此两列不是同一维度的正反面, 回归中不同进一式但也不能互相替代。此外与可读性族 (罕见词率、难字率、句长) 的区分前文已述: 套话文本往往极易读, 高套话不等于低可读, 二者在构念上正交, 在数据上的相关性是经验问题而非定义使然。第五, 与同一派生子步骤里的同胞测度 num_intensity (数值披露强度) 划界: 数值强度量的是报道中数字、比例、金额等硬量化信息的密度, 与具体性同处"硬信息含量"一侧, 与套话率恰成反面; 但两列不必在数据上负相关, 因为通稿常常同时堆砌模板话术与法定数字, 构念上它们分居软模板与硬数字两条独立轴, 回归中并列出现而不互相替代。最后须澄清一个纯工程巧合: 套话模块与 stage 24 的 herd_decay 处理器共用 char_wb 字符分析器范式, 但共享分析器绝不等于共享构念——herd_decay 度量的是新闻显著性沿时间的衰减, 与跨文档套话命中在测量对象上毫无交集, 分析器一致仅出于代码风格统一, 解读与设定时不可因两者代码近似而混同二者。

【已知局限与稳健性梯子】
第一项如实披露: 套话集建在 stage 22 的输入语料上, 即经过 21_tone_llms 留篇门控后的银行金融科技报道子集, 而非原始全量新闻语料; Lang 与 Stice-Lawrence (2015) 的原始做法是在全量报告母体上建集。这一偏离是流水线结构的产物 (套话派生位于门控之后), 后果是套话集刻画的是"银行金科报道这一体裁内部的高频短语"而非"中文新闻总体的高频短语", 解释时应表述为体裁内模板化程度, 项目在模块文档与本条目中均如实披露。第二, 文档频率阈值与 n-gram 长度区间均为自定义设计参数, 非文献硬值; 生产全量语料上可对阈值做网格敏感性, 该敏感性臂目前未物化为面板列, 属刻意不做并记录在案的取舍。第三, 小语料饱和退化: 当本轨有效文档数低于阈值的倒数 (百分之十的倒数即十篇) 时, 任何出现过一次的 n-gram 都满足文档频率判据, 套话集坍缩为全词表, 比率饱和趋一而不可解释——这一退化与年份跨度无关, 任何过小的输入子集皆然; 模块对此设有高声告警守卫, 其触发条件恰为有效文档数低于阈值倒数 (十篇)——开发环境的两年期迷你语料约有一千一百余篇, 远高于该阈值, 正常开发跑并不会触发此告警, 守卫真正拦截的是审计切片、单元测试夹具之类的极小输入子集; 生产十八年全量语料更不受影响。第四, 三轨梯子的读法: full 为 canonical 主轨, ctx 与 ss 为稳健性轨, 各轨独立在各自轨道语料上建各自的套话集, 逐轨顺序执行、词表不跨轨叠加 (峰值内存等于单轨峰值); 套话集口径在 ctx 与 ss 的子窗口短文本上信号较弱, 这一解释性限定原本是三轨化被搁置的理由, 三轨化落地后转为编码手册披露——ctx 与 ss 轨系数应作稳健性对照解读, 不宜单独承重。口径铁律必须复述: 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J 检验; 这与全仓三轨文本、co-primary 双轨嵌入、各类参数梯子的处理纪律完全一致。第五, 本家族无 _lg 孪生列 (非嵌入 carve-out), 与 co-primary 嵌入双轨体系无关, 属刻意设计而非遗漏。第六, 生产内存边界: 分块两遍的一级方案未解决词表绑定项, 硬闸校准与可能的二级方案受生产机审批门约束, 在校准完成前不应在全量语料上直接首播本模块所在阶段。第七, 分析器选择本身的稳健性须记录在案: char_wb 会在词与边界处保留前后空白标记, char 则为纯字符滑窗, 中文文本基本无词间空格使二者在真实语料上实测高度相关, 边界标记的影响可忽略; 选用 char_wb 纯为与 herd_decay 范式对齐, 该选择不驱动任何结论, 若改用 char 结论应当不变, 此点可作分析器敏感性的定性对照, 项目刻意未把它物化为独立面板列以免列爆炸。第八, 内存档位梯子的现状须与三轨梯子分清: 三轨是测量口径 (文本窗口) 的稳健性并排, 内存档位则是同一测量的工程实现档次 (in_memory 一级已落地并为默认、disk 与 auto 二级 DEFERRED), 二者正交, 后者的落地不改变任何一列的数值只改变可承载的语料规模, 不应被误读为又一条测量梯子。

## VAR: avg_boilerplate_ctx

【变体差分】
本列是套话比率的实体窗轨 (ctx) 稳健性变体, tier 为 standard。与家族 canonical (avg_boilerplate_full) 的差分只在输入文本与套话集语料, 算法、阈值、n-gram 区间、守卫与聚合完全同构: 文章级源列 boilerplate_phrase_ratio_ctx 读取 stage 14 物化的 content_ctx——标题前置拼接目标银行实体上下文窗口文本——并在 ctx 轨自身的语料上独立执行两遍建集与命中统计, 不与 full 轨共享套话集。这一"逐轨独立建集"是构念上的关键设计: ctx 文本是从全文抽取的实体邻域窗口, 其 n-gram 分布与全文本质不同 (机构名、职务称谓等实体伴随语的密度系统性更高), 若借用 full 轨套话集会造成判据与语料错配。差分后果有三点需要在解读时记住。其一, ctx 文本显著短于全文, 每篇的 n-gram 总数分母更小, 比率的抽样噪声更大, 且剔零宽与空白后实字数不足 n-gram 下界的退化判定更易触发, 缺失率预期高于 full 轨。其二, 回退语义: 按三轨物化契约, 无法构造实体窗口的报道其 content_ctx 回退为全文正文并置 ctx_is_fallback 标志为真 (ss 轨的回退即镜像此 ctx 语义), 回退行的 ctx 比率实际计算在全文文本上、但对照的是 ctx 轨语料的套话集, 存在轻微的口径混合, 属已知并披露的回退代价。其三, 套话集口径在实体窗口这类子窗短文本上信号较弱, 该列定位为 conditional-on-full 的稳健性对照 (行宇宙是 full-only 留篇集的子集), 不作主轨承重。还有两点解读要领。第一, 实体窗口的锚定判据继承全仓不对称口径的银行侧: 窗口围绕经否定过滤与短名过滤后仍成立的目标银行提及展开, 因此 ctx 语料剔除了"不良银行名单""XX 银行否认"这类被否定语境包裹的伪提及邻域, 其套话集刻画的是"银行被正面提及处的邻域固定搭配", 构念上比 full 轨更贴近"围绕目标银行的报道话术模板"。第二, 本列存在的实质意义是排除性检验: 若 full 轨的套话率效应主要由报道中与目标银行无关的外围段落 (行业综述、政策背景板) 的模板文字驱动, 则 ctx 轨系数应显著衰减; ctx 轨与 full 轨方向一致且量级可比, 是"套话信号确实附着在银行叙述邻域"的证据。跨轨比较仍只限轨内变异, 水平差异是窗口构造的机械产物。缺 content_ctx 列时本列整列缺失并高声告警, 优雅降级, 不阻断 full 与 ss 轨。口径铁律: 与 full、ss 两轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。Stata 标签为"跨文档套话比率(实体窗轨)"。

## VAR: avg_boilerplate_full

【变体差分】
本列是家族 canonical 主列, tier 为 core, 遴选依据是 boilerplate 家族的 canonical 全文轨、非嵌入 carve-out 无 _lg 孪生。full 轨文本为 content_full——stage 14 的 ctx_materializer 以标题前置方式物化的"标题加全文正文", 原始内容列保持不动; 模块的形参对 (text_col、out_col) 以本列为默认锚, 向后兼容旧调用方回退裸内容列, 但生产口径恒为 content_full, 文章级输出列名 boilerplate_phrase_ratio_full 是模块常量锚, 契约上禁止改名。标题前置的口径意义值得单独说明: 中文新闻的高频套话恰恰集中在导语与标题位置 ("本报讯""讯" 类引导语与固定机构简介), 标题进入字符 n-gram 统计使这类最典型的模板要素被完整捕获; 同一 stage 内的词典情感、清晰度族与数值披露强度族测度均读 content_full, 本列与之轨道对称——项目曾把数值强度指标定性为"唯一不含标题的 full 轨情感族指标"并作为缺陷修复, 本列自设计起即无此不对称。

作为三轨中的 canonical, full 轨相对两个子窗轨有一组结构性特征。其一, full 语料文本最长, 每篇的 char_wb 四至六元组总数最大, 套话集在最大的文档母体上以精确文档频率统计构建, 因此在三轨中样本量最足、套话集最稳定、抽样噪声最低, 这正是把它选为 canonical 而非把某个子窗轨设为主轨的直接理由。其二, 正因语料最长, 模板导语在长正文中被原创内容稀释, full 轨比率的水平预期系统性低于 ctx 与 ss 子窗轨; 这提示跨轨比较只能在同一轨内部比截面与时序变异, 绝不能直接比较三轨的比率水平——水平差异是文本窗口构造的机械产物, 而非信息含量的真实差异。其三, full 语料规模最大, 也使它成为生产十八年全量语料内存硬化的绑定情形: 分块精确两遍的全局文档频率字典在 full 轨上最庞大, 词条软预算告警与硬上限拒跑最可能先在本轨触发, 因此全量首播前的单词条字节实测与硬闸校准应以 full 轨语料为基准。

作为 canonical, 本列还承担三重独占职责。其一, 它是回归中的 headline 轨, ctx 与 ss 轨的系数以其为基准作平行呈现, 在各篇论文的文本控制族里, 本列是进入主设定的那一个, 两个子窗轨仅作稳健性对照。其二, 它是家族质量闸的锚——聚合域一致性审计以本列与 avg_specificity 等同族文本控制变量的缺失值掩码逐格相等作为硬判据, 覆盖闸即锁定两者的银行-年掩码相等。其三, 它是模块结果分析日志的判读对象, 文章级有效率分档、饱和退化告警与分布分位数报告均针对本列的文章级源列 boilerplate_phrase_ratio_full 输出。聚合为银行-年均值时 (encode 聚合器对文章级比率取 mean, 自动跳过缺失值), 行宇宙即 full-only 留篇门控宇宙 (llm_verified_full 为真的报道), 与全仓 n_articles 分母口径完全一致 (2026-06-29 裁决); ctx 与 ss 的行宇宙是本 full 留篇集的子集。

确定性契约以本列为最典型代表: 套话集经字典序排序后传入第二遍向量器, 结果保留六位小数, 全程无哈希种子依赖, 分块两遍 (默认每块两万篇, 内存档位 in_memory) 与旧单遍实现逐字节等价, 本列因此属于 golden 快照中可逐位复验的列, 不落入 BLAS 浮点漂移的豁免清单。这一逐位可复验性对 canonical 尤为要紧——各篇论文复现包在文本控制族里进入主设定的正是本 full 轨列, 若本列在跨机重跑中漂移, 复现包的文本特征项便无法字节复核; 相较之下, 网络中心性族因底层 BLAS 浮点非确定而列入 golden 豁免清单, 本列不在其中, 是复现包文本特征侧最硬的确定性锚之一。也正因如此, 换嵌入模型这类会牵动 co-primary 双轨嵌入列的大改对本列零字节影响 (本列是字符 n-gram 文档频率统计, 与任何嵌入或大模型无关), 换模时本列不需重生、不需披露数值副作用。口径铁律照录: full、ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 本列无 _lg 孪生 (非嵌入的字符 n-gram 文档频率统计, 与嵌入模型无关), 换嵌入模型时本列零改动。Stata 标签为"跨文档套话比率(全文轨)"。

## VAR: avg_boilerplate_ss

【变体差分】
本列是套话比率的同句轨 (ss) 稳健性变体, tier 为 standard。差分维度同样只在文本窗口与独立建集: 文章级源列 boilerplate_phrase_ratio_ss 读取 content_ss——标题前置拼接"目标银行与金融科技词在同一句共现"的句子及其前后若干句的窗口文本, 句半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 键控制 (默认为一句; 注意该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键, 前者管 ss 文本物化窗宽, 后者管留篇判据窗宽, 不可混淆)。共现判定采用不对称口径: 银行侧经过否定与短名过滤, 金融科技侧为裸词表命中。ss 是三轨中语义靶向最强也最短的文本轨——它试图把套话测量收窄到"银行与金科真正同句出现"的核心论述邻域, 检验 canonical 结论是否被报道中与主题无关的外围段落套话驱动。回退语义必须与全仓契约一字不差: ss 镜像 ctx, 当一篇报道不存在银行与金科同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置真, 与 full 轨共享 n_articles 分母; 金融科技词表整体缺失的极端情形下全部行回退、优雅降级不崩溃。回退行的 ss 比率计算在全文文本上、对照 ss 轨语料的套话集, 与 ctx 轨的回退代价同型。解读注意事项: ss 文本最短, 退化判缺失的概率三轨最高, 且套话集建立在"同句窗口拼接体"这一特殊语料上, 其高频 n-gram 更多反映银行金科共现句式的固定搭配而非一般新闻套话, 信号较弱, 该列只作 conditional-on-full 的稳健性对照 (行宇宙为 full 留篇集子集), 不单独承重。解读上还须留意回退行占比对本列的独特影响: ss 的回退触发条件 (无银行金科同句共现) 比 ctx 的回退条件 (无法构造实体窗口) 更常被满足, 回退行占比预期为三轨最高; 回退行的文本即全文正文, 其比率行为向 full 轨收敛, 因此当某银行-年格点的报道大量回退时, 本列的格值实质上是"ss 套话集口径下的准 full 轨均值", 与真同句窗口行的混合比例随共现密度漂移——这正是把 ss_is_fallback 标志一并落盘的原因, 需要严格同句解读的下游分析可按该标志剔除回退行后自行重聚合。本列相对 ctx 轨的增量识别价值在于靶向更极致: ctx 只要求银行实体在场, ss 额外要求金融科技词同句在场, 若套话率与结果变量的关联在 ss 轨仍存, 则可排除"关联仅由银行一般性报道的模板化驱动、与金融科技论述无关"这一替代解释。缺 content_ss 列时整列缺失并高声告警, 不阻断其余两轨。口径铁律: 与 full、ctx 两轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J; 非嵌入 carve-out, 无 _lg 孪生。Stata 标签为"跨文档套话比率(同句轨)"。

<!-- rendered-citations:begin -->
Gietzmann, M., Grossetti, F., & Lewis, C. M. (2026). Investor distraction and multi-dimensional financial narrative. Review of Accounting Studies, 31(1), 334-373. https://doi.org/10.1007/s11142-026-09950-7
Haapamäki, E., & Sihvonen, J. (2026). Mandatory cybersecurity disclosure: Early evidence from 10-K reports. International Journal of Accounting Information Systems. https://doi.org/10.1016/j.accinf.2026.100775
Zhu, X., Li, J., & Wang, Y. (2024). Are risk disclosures in financial reports informative? A text mining-based perspective. Humanities and Social Sciences Communications, 11(1), 1653. https://doi.org/10.1057/s41599-024-04169-w
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Kim, A. G., Muhn, M., & Nikolaev, V. V. (2023). Bloated disclosures: Can ChatGPT help investors process information?. SSRN Working Paper No. 4425527 [Working Paper]. https://doi.org/10.2139/ssrn.4425527
Li, F., Yang, M., & Zhang, T. (2023). Does prospectus readability matter for bond issuance pricing? Evidence from China. Pacific-Basin Finance Journal, 80, 102074. https://doi.org/10.1016/j.pacfin.2023.102074
Blankespoor, E., deHaan, E., & Marinovic, I. (2020). Disclosure processing costs, investors' information choice, and equity market outcomes: A review. Journal of Accounting and Economics, 70(2-3), 101344. https://doi.org/10.1016/j.jacceco.2020.101344
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in firm disclosures: Obfuscation or information?. Journal of Accounting Research, 56(1), 85-121. https://doi.org/10.1111/1475-679X.12179
Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal of Accounting and Economics, 64(2-3), 221-245. https://doi.org/10.1016/j.jacceco.2017.07.002
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Cazier, R. A., & Pfeiffer, R. J. (2016). Why are 10-K filings so long?. Accounting Horizons, 30(1), 1-21. https://doi.org/10.2308/acch-51240
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
Lang, M., & Stice-Lawrence, L. (2015). Textual analysis and international financial reporting: Large sample evidence. Journal of Accounting and Economics, 60(2-3), 110-135. https://doi.org/10.1016/j.jacceco.2015.09.002
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
Seebeck, A. (2024). Back to where it started?—Do expanded auditor's reports become sticky, generic and boilerplate over time?. International Journal of Auditing. https://doi.org/10.1111/ijau.12343
Su, F., Zhai, L., & Liu, J. (2023). Do MD&A Risk Disclosures Reduce Stock Price Crash Risk? Evidence from China. International Journal of Financial Studies, 11(4), 147. https://doi.org/10.3390/ijfs11040147
<!-- rendered-citations:end -->
