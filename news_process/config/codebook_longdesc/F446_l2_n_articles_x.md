---
family_id: F446
columns:
- n_articles_llm_valid
- n_articles_llm_valid_ctx
- n_articles_llm_valid_ss
unit: 篇数/计数 (count, 非负整数)
formula: "n_articles_llm_valid{track} = count(llm_vote_score{track})  (groupby bank-year, 跳过 NA); track ∈ {_full(无后缀), _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py::aggregate_panel ; news_process/pipeline/panel/codebook.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / _ctx / _ss, llm_verified{track})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: Finance and Economics Discussion Series (FEDS Working Paper No. 2026-020), Federal Reserve Board
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1016/j.intfin.2026.102325
  type: journal
  authors: Chen, K., Granville, B., & Matousek, R.
  year: 2026
  title: "Decoding central bank communications with large language models"
  venue: Journal of International Financial Markets, Institutions and Money
  vol: 109
  pages_or_artno: 102325
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv (NBER Working Paper No. 33344)
- doi: 10.1038/s42256-023-00783-6
  type: journal
  authors: Ollion, É., Shen, R., Macanovic, A., & Chatelain, A.
  year: 2024
  title: "The dangers of using proprietary LLMs for research"
  venue: Nature Machine Intelligence
  vol: 6
  issue: 1
  pages_or_artno: 4-5
- doi: 10.1073/pnas.2308950121
  type: journal
  authors: Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J.
  year: 2024
  title: "GPT is an effective tool for multilingual psychological text analysis"
  venue: Proceedings of the National Academy of Sciences
  vol: 121
  issue: 34
  pages_or_artno: e2308950121
- doi: 10.1080/19312458.2023.2285765
  type: journal
  authors: Birkenmaier, L., Lechner, C. M., & Wagner, C.
  year: 2024
  title: "The search for solid ground in text as data: A systematic review of validation practices and practical recommendations for validation"
  venue: Communication Methods and Measures
  vol: 18
  issue: 3
  pages_or_artno: 249-277
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族三列刻画同一个底层构念的三轨投影: 某家银行在某一年里, 被大语言模型 (LLM) 情感投票判为有效、因而进入分类占比运算定义域的银行金科报道篇数。它不是"物理篇数", 而是"有效标注篇数"。要理解这一区分, 须回到面板里两种计数口径的刻意分家。第一种是 n_articles, 由 encode.aggregate_panel 以 groupby bank-year 对 llm_vote_score_full 取 size 得到, 计入该组全部行、含 LLM 调用失败 / 未定义 / 未通过校验 (verified=False) 的 NA 行, 语义是"该银行该年物理上有多少篇金科报道", 供 ln_news_coverage、媒体关注度代理、证伪检验等 coverage 消费者使用。第二种即本家族 n_articles_llm_valid, 由同一 groupby 对 llm_vote_score_full 取 count (跳过 NA) 得到, 只数 LLM 真正打出有效标签的那部分。两口径的差集正是 LLM 未能有效标注的报道; 之所以必须把它们分开, 是因为一切分类组成型比率 (tech / app / sub / symb / indep / collab 及其 frac 变体) 的分子都来自"有效标注"子集, 若分母混入无标签行, 占比会被系统性拉低、并破坏"分子分母同口径"这一恒等式前提。本家族由此成为整张面板里所有分类占比测度的"正确分母中枢", 兼具门控计数与规模控制两重身份。数据来源链条为: 原始媒体报道经 stage 00 预处理、11/12 银行与金科实体识别、13 共现硬过滤、14 三轨文本物化后, 进入 stage 21 tone_llms 由三家大模型逐篇投票并校验, 产出各轨的 llm_vote_score 与 llm_verified 列; 最终在 stage 40/46 面板聚合阶段按 bank-year 折叠为本家族三列。须格外强调的是, 本家族之所以被列为 core 家族, 正因其 canonical 列同时兼任三重要角色: 它是分类占比测度的分母中枢、是 full-only 留篇门控的计数落地、又是回归里最常见的报道规模控制项; 任何对分类 frac 或对语调 / 属性处理变量的解读, 只要涉及"占比"或"人均"概念, 其正确性都回溯到本家族分母口径是否被正确理解。换言之, 本家族不是一个边缘计数, 而是把"新闻文本"转成"银行年面板"这一转换过程中的规模会计基准。它记录的是一个朴素但极易被误用的事实: 面板每一格背后有多少篇报道真正被模型有效读懂, 而这一数目既不等于物理报道数, 也在三条文本轨上各不相同。再从计量直觉上打一个白话比方: 若把每个 bank-year 想成一只装报道的篮子, n_articles 数的是篮子里总共有多少篇 (含模型没读懂、扫描仪读花的那些), 本家族数的是其中被模型清清楚楚打上标签的那些; 后面凡是要算"这些报道里有百分之多少谈的是底层技术 / 外部协同", 分母都只能用后者, 因为分子只从"打上标签的"里数, 分母若掺进没标签的, 百分比就被稀释得偏低。这个看似显然的道理, 在早期实现里恰恰因分母口径混用而出过越界至数倍于一的错, 足见其承重。三条文本轨则对应"用多宽的上下文喂给模型": full 给全文、ctx 给实体附近、ss 给银行与金科同一句里的窗; 上下文越窄, 模型能确定判定的篇数就系统性不同, 于是同一只篮子在三条轨上被有效读懂的篇数各不相同, 这正是三列并存、互为稳健性而不可相互替代的根由。

【方法学与计算】
计算公式对三轨完全同构: n_articles_llm_valid{track} 等于 groupby(bank, year) 对 llm_vote_score{track} 的 count 聚合, 其中 track 取无后缀 (full)、_ctx、_ss 三者。count 聚合天然跳过 NA, 因此一篇报道要计入本列, 须在该轨上同时满足未发生 LLM 调用失败、模型给出可解析的确定性判定、且通过 verified 校验三个条件——这三类失败在上游 encode_sentiment 阶段被显式合并为掩码, 将对应 vote_score 强制置 NA, 与"真实中性"严格区分, 从而不污染有效计数。full 轨的分母口径承担了留篇门控职责: 依 2026-06-29 定稿的 full-only 口径, 一篇报道是否算作"一篇银行金科报道"只看 llm_verified_full 是否为真, 行宇宙由此锚定为 full 留篇集; ctx 与 ss 两轨降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 但各自的 per-track 有效计数照常独立计算。因此 n_articles_llm_valid_ctx 与 _ss 并非对 full 计数的简单复制, 而是各轨 LLM 成功率不同所致的独立数目: ctx 轨输入是标题加实体窗口、ss 轨输入是标题加银行与金科同句共现窗, 文本更短、信息更聚焦, 模型的可判定率与 full 轨系统性不同, 故三列数值通常互不相等。ss 轨在物理篇数层面刻意不另设 n_articles_ss, 而是共享 n_articles 物理分母, 其回退语义镜像 ctx: 当某篇无银行与金科同句共现时 content_ss 退化为全文正文、ss_is_fallback 置真; 但在分类占比的分母层面, ss 仍以自身的 n_articles_llm_valid_ss 为正确分母, 保证 ss 对角分类 frac 的分子分母严格逐轨。全部 _ss 与部分 _ctx 聚合入口由下游 valid_agg 按源列存在性过滤: 当 stage 21 未跑同句轨或某轨源列缺失时, 对应计数列优雅缺席而非报错, 使离线 / 降级重放不致中断。这一优雅降级并非可有可无的工程细节, 而是与 per-model 独立降级、co-primary 双轨嵌入的 both-or-neither 守卫构成一整套一致的缺失哲学: 计数类度量按源列存在性各自独立缺席, 兄弟列不连坐。此外须澄清确定性口径: 本家族计数虽是整数、看似天然确定, 但其上游 llm_vote_score 依赖 LLM 缓存命中; 在缓存三轨零 miss 时以 NEWS_PROCESS_LLM_OFFLINE 离线守卫可字节级复现, 缓存键锁定 prompt v8、温度置零, 从而本家族三列在冻结锚点下逐位可复现——这与部分 BLAS 浮点非确定的网络列不同, 本家族属确定性列, golden 比对时无须排除。最后须区分本家族与"篇数密度"或"覆盖强度"类衍生度量: 本家族是原始有效计数, 任何取对数、标准化、除以样本框规模的变换都是下游派生, 不落在本家族口径内, 读者不应把派生列的性质回投到本家族。

【文献定位】
本家族坐落于"文本即数据"测量方法学的两条主线交汇处。其一是媒体关注度的计数传统: Fang & Peress (2009) 与 Tetlock (2007) 确立了以报道篇数与语调作为信息中介强度代理的范式, 本家族的物理孪生 n_articles 正是这一传统的直接落地, 而 n_articles_llm_valid 则是其"经有效标注筛滤"后的精炼版本。其二是 LLM 标注有效性的新兴文献: Gilardi et al. (2023) 证明 ChatGPT 在文本标注任务上可超越众包工人, Rathje et al. (2024) 将其推广到多语心理文本分析, Lan et al. (2025) 专门针对中文细粒度金融情感验证了大模型的可用性, 三者共同支撑"以 LLM 有效投票作为报道是否进入分类域的判据"这一设计。van Atteveldt et al. (2021) 更早地把人工标注、众包、词典法与机器学习的情感测量效度并置比较, 提示不同方法给出的"可用样本"口径本就不同, 这为本项目在 LLM、BERT、词典三法各设独立有效计数分母提供了直接方法学理由——若强行用一套分母跨方法, 就抹去了各方法可读性差异这一真实信号。与此同时, Hansen (2026) 给出无金标准时以 κ / α 一致性验证 LLM 标注的框架, Birkenmaier et al. (2024) 系统综述了文本测量的验证实践, Carlson & Burbano (2026) 与 Ollion et al. (2024) 则分别就管理学研究中 LLM 标注的操作规范与专有模型的可复现风险提出警示; 这些工作共同界定了本家族计数的效度边界——它衡量的是"模型可有效判定"而非"人类必然同意"的篇数。de Kok (2025) 关于 temperature=0、prompt 冻结与缓存的范式, 恰是本项目 stage 21 以 prompt v8 字节冻结、温度置零、缓存命中键锁定得以复现的方法学依据。更宏观地看, Ludwig, Mullainathan & Rambachan (2025) 提出的 LLM 应用计量框架强调, 当 LLM 作为测量工具嵌入下游回归时, 其输出的测量误差结构会直接影响识别与推断, 这为"把有效标注篇数显式建为分母、并将其误差传导讲清楚"提供了理论支撑; Chen, Granville & Matousek (2026) 对央行沟通的 LLM 解码、以及 Huang, Wang & Yang (2023) 的 FinBERT 则从金融文本这一具体域印证了机器标注可作为大规模面板构造的可靠输入。综观这批文献, 一条共识浮现: LLM / 机器标注的价值不在于替代人类判断, 而在于以可复现、可审计的方式把海量文本压成结构化度量, 而"有多少篇被有效标注"正是这一压缩过程的规模刻度。本家族的存在, 使得下游任何一个占比或强度度量都能追溯到"分母到底数了哪些篇", 从而让 LLM 测量的透明度落到可查的面板列上, 而非停留在方法学承诺。

【识别策略定位】
作为分母与规模控制变量, 本家族在识别策略中扮演双重角色。其一, 它是所有分类组成型 frac 的除数: 在计量设定中, 若把 frac 作为处理变量, 则本计数进入其构造的分母, 其测量误差会传导为 frac 的乘性噪声, 故披露其口径对理解 frac 的信噪比至关重要。其二, 它常以对数形式 (ln) 或原始值进入回归作为报道规模 / 注意力控制项, 吸收"报道多少"对结果变量的机械影响, 使语调 / 属性类处理变量的估计不被单纯的曝光量混淆。须强调三轨口径铁律: full / ctx / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨的对应计数混进同一个 over-identified Hansen J 过度识别检验; 三轨提供的是规格稳健性的并排证据 (镜像政治词权重梯度、词典消融梯度、co-primary 双轨嵌入的同款铁律), 而非可叠加的多重工具。同理, ctx 与 ss 分类 frac 必须各用同轨分母: 早期实现曾错用 full 轨 n_articles_llm_valid 作 ctx frac 分母, 因 ctx 有效篇数与 full 不等而致 frac 越界至数倍于一, 该缺陷已由分轨分母修复, 这段历史正说明"分母逐轨严格对齐"是本家族的承重约束。其三, 本家族在证伪 / 安慰剂检验中亦有用武之地: 以物理篇数 n_articles 与有效篇数 n_articles_llm_valid 的比值可粗略刻画 LLM 在某银行某年语料上的标注成功率, 若该成功率与处理变量系统相关, 则提示存在选择性可读性偏误, 须在稳健性叙事中排除。须再次锚定三轨与相邻梯子的正交关系: 三轨 (full / ctx / ss) 之间、co-primary 双轨嵌入之间、per-model 三家之间、政治词权重三档之间、词典消融各变体之间, 均是"各自 just-identified 并排、互为稳健性、不分主次、禁混同一 over-identified Hansen J"的同款铁律, 且各梯子彼此正交不交叉; 本家族的三轨计数只在"文本轨"这一维度上展开稳健性, 不与其他梯子叠乘。

【与相邻测度的构念区分】
本家族最易与三类相邻测度混淆, 须逐一厘清。第一是物理篇数 n_articles: 二者共用同一 groupby, 差别仅在 size (含 NA) 与 count (跳 NA), 语义分别是"物理覆盖"与"有效标注域", 前者供 coverage 消费者、后者供 frac 分母, 绝不可互换。第二是 per-model 版本的有效篇数: per-model 分类维度 frac 的分母是"该模型自身 verified 篇数", 而非本家族的共识 n_articles_llm_valid; 三家大模型各自的成功率不同, 故 per-model frac 用各自分母、共识 frac 用共识分母, 两套分母并排互为稳健、禁混同一 Hansen J。第三是各分类维度的分子计数 (如 tech_count / collab_count): 它们是"有效且属某类"的篇数, 恒为本家族计数的子集, 分子分母同口径由此保证 frac 落在闭区间内、对子和不超过一 (残余为有效但无该维标签的报道, 属正确语义)。此外, 本家族与语调均值类测度 (llm_vote_tone 等) 正交: 前者数"多少篇有效", 后者算"有效篇的平均语调", 一为规模一为强度, 在自回归与控制项中承担不同职能。第四是与 BERT / 词典法有效计数的区分: 本家族的"有效"以 LLM 投票校验为准, BERT 与词典法各有自己的可算篇数口径 (词典法几乎对每篇都可出分、BERT 依模型可用性), 三法互为 cross-method 稳健臂, 其分母不可跨方法混用; 本家族专指 LLM 法这一支。第五是与 stage 13 共现硬过滤后的行数区分: stage 13 丢弃"银行与金科不邻近共现"的报道, 决定的是进入 stage 21 的候选池大小, 而本家族数的是候选池中 LLM 有效标注的子集, 两者是先后两道筛而非同一口径; 共现过滤是"文本是否相关", LLM 有效是"模型是否读懂", 概念层次不同。厘清这五重区分, 本家族的语义边界才算封死: 它精确地指"经共现过滤入池、并在指定文本轨上被 LLM 有效投票"的 bank-year 报道篇数, 不多不少。第六, 须与 per-model 版有效篇数再作一次收束: per-model 分类维度 frac 的分母是某一家大模型自身 verified 的篇数, 门控在 encode 层完成, 三家各自的这一分母彼此不等、也不等于共识的本家族计数; 共识计数取的是投票机制下的有效篇, 而非任一单模型的 verified 篇。二者一为共识、一为单模型, 各服务于共识 frac 与 per-model frac 两套并排的稳健性证据, 严禁互换分母, 更禁把两套 frac 混进同一 over-identified Hansen J。这层区分与前述文本轨、聚合方式、标注方法、筛滤阶段四组共同构成使用本家族时必须同时锁定的坐标; 缺任一坐标, "有效篇数"这个词就是欠定的。

【已知局限与稳健性梯子】
须诚实披露的局限有三。其一, 有效计数受 LLM 可判定率驱动, 而可判定率随模型版本、prompt、语料难度漂移; 项目以 prompt v8 字节冻结、温度置零、缓存复现锚定这一漂移, 但换厂商 / 换模型仍会使 full-only 口径下的 n_articles 与有效篇数系统性收缩 (Google 至阿里 Qwen 的迁移即产生此类数值副作用, 属 by-design 而非缺陷, manuscript 须披露)。其二, ctx / ss 两轨在开发期 T=2 小样本上可能出现零方差或大量缺格的退化, 属预期现象, 生产期 T=18 全语料下恢复正常; 读者不应据 T=2 试跑值推断生产分布。其三, 有效性以"模型可判定"为准, 与人类金标准的一致性须另由 κ / α (Hansen 2026; van Atteveldt et al. 2021) 与人工盲标协议独立评估, 本计数本身不含人机一致性信息。对应的稳健性梯子即三轨并排: full 为 canonical 门控与分母, ctx / ss 为互为稳健的旁证轨, 三者各自 just-identified、禁混同一 over-identified Hansen J; 换测度类改动须受控全量重生 golden, 并按 PYTHONHASHSEED=0 与全 BLAS 线程钉一的确定性协议复现。第四类局限关乎口径普查的可比性: 本项目的原始语料普查报告了去重前后的全量报道规模与媒体来源数, 但那是递归全量口径, 与本家族所依据的过滤后、非递归实处理量不可混用; 读者若要把本家族篇数与外部普查数字对照, 须先对齐口径边界, 否则会得出"有效篇数远小于普查数"的表面矛盾——该差距实由共现过滤、去重、留篇门控层层筛滤所致, 属设计而非丢数。第五类局限关乎测量误差在下游回归中的传导结构: 当有效篇数作为分母进入分类 frac、而 frac 又作处理变量时, 分母的抽样波动会以乘性形式注入 frac, 在小分母 (少报道 bank-year) 格上尤为剧烈——一两篇有效标注的增减即可令占比大幅跳变, 这一异方差性质须在推断阶段以聚类稳健标准误或对小分母格加权 / 剔除来处理。Ludwig, Mullainathan & Rambachan (2025) 的 LLM 应用计量框架正提示: 把 LLM 输出嵌入回归时, 其测量误差并非经典的、与真值独立的加性噪声, 而可能与被测文本特征相关, 从而对识别构成非平凡威胁; 就本家族而言, 若"模型可判定率"本身随报道语调或银行属性系统变动, 则有效篇数分母会携带内生性, 需在稳健性叙事中以物理篇数比值探针加以体检。第六, 须区分有效性的两种效度证据: 本计数只保证"模型给出了可解析且通过校验的判定", 属过程效度 (process validity), 而判定与人类金标准是否一致的构念效度 (construct validity) 须另由 κ / α 一致性 (Hansen 2026; van Atteveldt et al. 2021) 与人工盲标协议 (Birkenmaier et al. 2024 综述的验证实践) 独立背书; 两类效度不可相互替代, 高有效计数不等于高人机一致。综上, 本家族虽是一个整数计数, 却承载了从原始文本到结构化面板的全部筛滤记账, 其正确使用须同时把握"哪种聚合 (size 对 count)"、"哪条文本轨 (full / ctx / ss)"、"哪种标注方法 (LLM 对 BERT 对词典)"、"哪一道筛 (共现过滤对留篇门控)" 四组区分; 任何一组混淆都会让下游占比或规模控制失真。这也是本家族被定为 core、须以长文详述而非一行注释带过的根本原因。

## VAR: n_articles_llm_valid

【变体差分】
本列是家族 canonical、tier=core, 无轨道后缀即对应 full 轨 (标题 prepend 加全文正文)。计算为 groupby bank-year 对 llm_vote_score_full 取 count, 即该银行该年 LLM 在全文轨上有效投票成功的报道篇数; 与物理篇数 n_articles (对同列取 size、含 NA) 的差集为 LLM 未能有效标注的报道。它是整张面板里所有 full 轨分类组成型 frac (tech / app / sub / symb / indep / collab 及其 frac 变体) 的唯一正确分母, 保证分子 (类内有效篇) 与分母 (全有效篇) 同口径, 从而 frac 落在闭区间内、各对子和不超过一。作为 full-only 留篇门控 (2026-06-29 口径) 的直接产物, 本列承载行宇宙的定义职责: 一篇报道是否算"一篇银行金科报道"只看 llm_verified_full 是否为真, ctx / ss 两轨的有效篇数皆是本 full 留篇集的 conditional-on-full 子集度量。在计量应用中, 本列既作分类 frac 处理变量的隐含分母、又常以对数形式进入回归充当报道规模 / 注意力控制项, 吸收曝光量的机械影响。须复述三轨铁律: 本列与 _ctx / _ss 两个同族列各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J 过度识别检验; 三轨是规格稳健性的并排证据而非可叠加工具。本列亦是 co-primary 双轨嵌入、per-model 稳健梯子在"分母"维度的共识锚: per-model frac 用各模型自身 verified 篇数为分母、共识 frac 用本列为分母, 两套分母并排不相混。因 full 轨承载门控, 本列在换嵌入 / 换模型时会随 full-only 口径系统性收缩, 属披露项而非缺陷。就与物理孪生 n_articles 的关系再作一次精确刻画: 二者共用同一 groupby(bank, year) 与同一源列 llm_vote_score_full, 唯一差别是 size 与 count 两种聚合——size 计全组行数含 NA, count 跳 NA, 二者之差恰为该银行该年 LLM 调用失败、判定未定义或校验未通过的报道数。因此本列永远小于等于 n_articles, 且其比值即为 full 轨的有效标注成功率, 是一个可直接审计的中间量。在实际建模中须警惕两种误用: 其一是把 n_articles (物理) 误用作分类 frac 分母, 会因混入无标签行而系统性低估占比; 其二是把本列误用作 ctx / ss 轨 frac 的分母, 会因跨轨成功率不等而使占比越界或偏移。二者都由"分母必须与分子同口径、同文本轨"这一条铁律禁止。本列在开发期 T=2 小样本上仍能出正常整数值 (不像 ctx / ss 那样易退化), 因为 full 轨语境最宽、可判定率最高; 但读者切勿据 T=2 的绝对量级推断生产分布, T=18 全语料下量级会随语料深度整体抬升。作为面板里被引用最广的分母, 本列的稳定性直接决定了几十个下游占比列的可信度, 故其口径在 codebook 中被反复交叉引用 (encode.aggregate_panel 中各 frac 赋值处、network_brokerage 的 leave-one-out 归一化处均以本列或其同轨兄弟为分母), 任何对本列语义的误读都会沿这些引用链放大。最后就本列的取值性质补一句: 它是非负整数, 下界为零 (该银行该年无任何 LLM 有效标注报道), 无固定上界 (随语料深度增长), 在对数化进入回归前须处理零值 (常用 ln(1+x) 或对零篇 bank-year 的先验剔除, 视论文设定而定); 本 codebook 不硬编码具体变换, 变换属下游派生列范畴。作为 core 列, 本列还是家族对外的唯一 canonical 接口: 凡文档、模板或注释里不带轨道后缀地提及"有效篇数分母", 默认即指本列 (full 轨), ctx / ss 版本须显式带后缀; 这一命名约定与项目里"无后缀即 full / canonical"的全局惯例一致, 避免了下游误把某条稳健性轨当作主轨引用。

## VAR: n_articles_llm_valid_ctx

【变体差分】
本列 tier=standard, 是 ctx (实体上下文窗) 轨的有效投票篇数, 计算为 groupby bank-year 对 llm_vote_score_ctx 取 count。ctx 轨输入文本为标题 prepend 加实体窗口 (银行与金科实体邻近窗), 较 full 轨更短更聚焦, LLM 的可判定率与 full 轨系统性不同, 故本列数值通常不等于 full 轨 canonical。其专职用途是充当 ctx 对角线分类 frac (tech / app_lc、sub / symb_sc、indep / collab_cm) 的正确分母: 分子取 ctx 轨类内计数、分母取本列, 分子分母严格逐轨同口径, 数学上保证 frac 落在闭区间内、对子和不超过一。此处有一段承重历史——早期实现曾错用 full 轨 n_articles_llm_valid 作 ctx frac 分母, 因 ctx 有效篇数与 full 不相等 (ctx_valid 大于 full_valid 时 frac 越界至数倍于一、反之则低估), 造成轨道不对称除法, 该缺陷已由分轨分母修复, 正说明"逐轨分母对齐"是本列存在的核心理由。作为 conditional-on-full 的稳健性轨, 本列与 full canonical、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。开发期 T=2 上本列可能退化 (零方差或缺格), 属预期现象, 生产期 T=18 恢复; 源列缺失时由 valid_agg 按存在性过滤优雅缺席。须补充说明本列与 full canonical 的数值关系无固定序: ctx 有效篇数既可能大于也可能小于 full, 取决于实体窗聚焦是提升还是削弱模型的可判定性, 因此本列不能被视作 full 计数的"打折版", 而是独立测量。在与 ss 轨的对比上, ctx 语境宽于 ss 而窄于 full, 通常有效篇数介于两者之间, 但此为经验倾向而非硬保证。本列的存在使 ctx 三轨稳健性检验得以自洽: 若 full 与 ctx 两轨给出的分类结论一致, 则说明结论不依赖具体文本窗口的选取, 这正是三轨互为稳健性的实证意义所在。

## VAR: n_articles_llm_valid_ss

【变体差分】
本列 tier=standard, 是 ss (银行与金科同句共现窗) 轨的有效投票篇数, 计算为 groupby bank-year 对 llm_vote_score_ss 取 count。ss 轨输入为标题 prepend 加银行与金科同句共现窗 (config filtering ss_sentence_radius 默认为一句半径), 是三轨中语境最严格的一轨, 其回退语义镜像 ctx: 当某篇无银行与金科同句共现时, content_ss 退化为全文正文、ss_is_fallback 置真, 并共享 n_articles 物理篇数分母。须区分两个层面——ss 轨在物理篇数层刻意不另设 n_articles_ss (共享 n_articles 物理分母), 但在分类占比层仍以本列 n_articles_llm_valid_ss 为正确分母, 使 ss 对角分类 frac 的分子分母严格逐轨、口径同 ctx。因 ss 轨语境最窄、可判定率与另两轨不同, 本列数值独立于 full 与 ctx。作为 conditional-on-full 的稳健性轨, 本列与 full canonical、ctx 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三者混进同一 over-identified Hansen J。全部 ss 聚合入口由下游 valid_agg 按源列存在性过滤: 当 stage 21 未跑同句轨或缺 llm_vote_score_ss 源列时, 本列优雅缺席而非报错, 保障离线 / 降级重放不中断。开发期 T=2 上 ss 轨常见退化 (同句共现稀疏致零方差), 属预期, 生产期 T=18 全语料下恢复正常分布。须再强调回退与分母的两层分离: 物理层 ss 共享 n_articles 不另设 n_articles_ss, 是因回退镜像 ctx 后 ss 的"物理覆盖"已由全文 body 承载、无独立物理分母之必要; 而占比层 ss 仍需本列作分母, 是因分类 frac 的分子来自 ss 轨有效投票、须与之同口径。这两层看似冗余实则各司其职, 混用会导致 ss 对角 frac 口径漂移。作为三轨中语境最严的一轨, ss 提供的是最保守的稳健性旁证: 若结论在 ss 严格同句窗下仍成立, 则对"银行与金科是否真正共现于同一语义单元"这一最苛刻判据也稳健, 与 full / ctx 各自 just-identified 并排、禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Hansen, A. L. (2026). Validating large language model annotations. Finance and Economics Discussion Series (FEDS Working Paper No. 2026-020), Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Chen, K., Granville, B., & Matousek, R. (2026). Decoding central bank communications with large language models. Journal of International Financial Markets, Institutions and Money, 109, 102325. https://doi.org/10.1016/j.intfin.2026.102325
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv (NBER Working Paper No. 33344) [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Ollion, É., Shen, R., Macanovic, A., & Chatelain, A. (2024). The dangers of using proprietary LLMs for research. Nature Machine Intelligence, 6(1), 4-5. https://doi.org/10.1038/s42256-023-00783-6
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121
Birkenmaier, L., Lechner, C. M., & Wagner, C. (2024). The search for solid ground in text as data: A systematic review of validation practices and practical recommendations for validation. Communication Methods and Measures, 18(3), 249-277. https://doi.org/10.1080/19312458.2023.2285765
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
