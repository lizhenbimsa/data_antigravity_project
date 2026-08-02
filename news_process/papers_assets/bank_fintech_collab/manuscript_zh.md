# 自主研发与外部协同：中国银行金融科技战略中的开放式创新

**Paper ID**: `bank_fintech_collab` (P5)
**状态**: M3 骨架 (M0 G0 spec 已冻结 2026-05-17, manuscript 实施延后到 M5/M6)
**总规划**: B-route 主规划文档 (原 docs/plan/B_route_master_plan_v2.md) 已随 docs/ 目录整体删除 (commit 1698bda5); 当前版本/特性真值以仓库根 CLAUDE.md 顶部 "Current version" 段为准。

---

## 摘要

在位银行的金融科技创新究竟应当自建还是外购？本文把中国商业银行金融科技新闻报道的**组织来源**编码为二元属性——自主研发（内部 R&D）对外部协同（与金融科技公司/科技巨头的合作、许可、并购、战略投资、开放 API 与行业联盟）——并聚合为银行-年外部协同新闻占比 `collab_frac` 作为处理变量，理论上锚定 Chesbrough (2003) 开放式创新框架与 Laursen & Salter (2006) 搜索广度-深度分类法。语料来自一次覆盖 2007-2025 年、18,198,978 条媒体报道、3,740 家媒体来源的原始普查；进入管线的生产目标语料即取该普查总量口径——18,198,978 条媒体报道（2007-2025，T=19）；该语料随后经 stage 13 银行-金科共现硬过滤（硬过滤后留存篇数为生产统计，TODO: 待生产机重跑后回填），再聚合为 110 家中国商业银行的银行-年面板。文章级分类由三家大语言模型（gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash）在 temperature=0、字节级冻结的 prompt v8 下多数投票产生，缓存全命中时可离线字节级复现。主识别策略为同类型同业 leave-one-out 外部协同占比工具变量的 2SLS（单一 confirmatory 规格），并以广义 Bartik 工具、三轨文本口径、跨厂商 per-model 分类等一系列互为稳健性、各自恰好识别（just-identified）的并列设定做稳健性检验。

> TODO: 主结果句（collab_frac → m_and_a_fintech 的符号、量级与显著性）待生产回归后回填。

> TODO: 机制与异质性结果句待生产回归后回填。

本文贡献在于：为金融科技创新文献补上"组织来源"这一被忽视的二元维度；并与同管线的实质性（P3）与技术位点（P4）维度构成 2³=8 单元的正交饱和分解，给出该维度边际信息量的结构性证据。

---

## 1. 导论

数字化冲击下，在位银行面临一个真实而尚未解决的战略选择：面对金融科技的技术与商业模式竞争，是依靠内部研发自建能力，还是通过合作、投资乃至并购从外部获取能力（Vives, 2019）？在中国，这一选择尤为尖锐：一方面，大型银行纷纷设立金融科技子公司走自建路线；另一方面，助贷、联合贷、开放 API 与战略联盟等外部协同安排在中小银行中广泛扩散。媒体是记录这一战略选择的高频信息中介——每一则"某银行与某金融科技公司签署战略合作协议"或"某银行自主研发核心系统上线"的报道，都是该银行创新组织来源的一次可观测披露。

然而，既有金融科技创新实证文献几乎全部以单一维度刻画银行创新——数量（专利数、投入额）、质量（引用加权）、或技术位点——而忽视了创新的**组织来源**：这项创新是在组织边界内完成的（closed），还是跨越边界与外部伙伴共同完成的（open）？开放式创新理论早已论证组织来源是独立于数量与质量的战略维度（Chesbrough, 2003; Laursen & Salter, 2006），而 Lerner, Seru, Short, & Sun (2024) 用美国专利数据区分金融创新的内部与外部产出归属，说明该维度在金融业同样可测且重要。但对于银行业金融科技转型这一场景，尚缺乏一个大样本、面板结构、可复现的组织来源测度。

本文用文本即数据（text-as-data; Gentzkow, Kelly, & Taddy, 2019）的方法补上这一缺口。我们从一次覆盖 18,198,978 条媒体报道、3,740 家媒体来源的原始语料普查出发（2007-2025；其中报纸类型占全部行 92.93%），以该普查总量为进入管线的生产目标语料——18,198,978 条媒体报道（2007-2025，T=19），该语料随后经 stage 13 银行-金融科技共现硬过滤（硬过滤后留存篇数为生产统计，TODO: 待生产机重跑后回填）；对每篇通过验证门控的银行金融科技报道，由三家大语言模型在 Chesbrough 框架下做二元分类（0=自主研发, 1=外部协同）并多数投票，聚合为 110 家中国商业银行的银行-年外部协同新闻占比 `collab_frac`。整个测度管线在 temperature=0、seed=42、prompt v8 字节级冻结下运行，缓存全命中时可离线零成本字节级复现——测度本身即满足可复现性纪律（de Kok, 2025; Hansen & Kazinnik, 2023）。

识别上，银行-年外部协同倾向显然内生于未观测的战略偏好与投资机会。我们的主识别策略是同类型同业 leave-one-out 外部协同占比工具变量的 2SLS：以同一银行类型内其它银行的平均外部协同占比（剔除自身）作为该银行 `collab_frac` 的工具，动机源自同业效应文献（Manski, 1993; Bramoullé, Djebbari, & Fortin, 2009），构造上同构于金融学中的 LOO 同业工具先例（Leary & Roberts, 2014），并如实披露其排他性约束的局限。备选工具为广义 Bartik 移-份额工具（Borusyak, Hull, & Jaravel, 2025）。所有稳健性梯子——三轨文本口径、三家 LLM 的 per-model 分类、IV 两引擎（LOO 与 Bartik）及 lag1 前定性变体——均为互为稳健性、不分主次的并列设定，各自进入恰好识别的独立回归，绝不合并进同一过度识别的 Hansen J 检验。

> TODO: 结果预览段（基线 2SLS 系数、经济量级换算、机制与异质性摘要）待生产回归后回填。

> TODO: 事件研究（E1 余额宝 2013-06-13 / E3 资管新规 2017-04-27 / E4 蚂蚁 IPO 暂停 2020-11-03）围绕外生冲击的动态证据句待生产回归后回填。

本文与同管线其余论文的差异化边界清晰：P5 度量新闻公告的**组织来源二元属性**——它既不是 P1 的连续情感基调（tone），不是 P2 的注意力暴露量（attention），不是 P3 的 Westphal & Zajac（1994, 1998）意义上的实质性（substantiveness），也不是 P4 的 Gomber 技术位点（locus）。组织来源与实质性、位点在概念上正交，三维交叉构成 2³=8 单元的饱和分解（§2.4 与 Table 6），这既是本文边际贡献的结构性证据，也是对"多篇论文切分同一语料"这一常见质疑的直接回应。

本文余下结构如下：§2 建立理论框架并发展假设；§3 描述语料、测度构造与识别策略；§4 报告主要实证结果；§5 呈现稳健性检验体系；§6 讨论机制与含义；§7 总结。

---

## 2. 理论框架

### 2.1 开放式创新 (Chesbrough 2003)

Chesbrough (2003) 提出的开放式创新框架，把创新过程按知识流动方向区分为由外向内（inbound / outside-in：许可引入、技术并购、联合研发）、由内向外（outbound / inside-out：技术授权、分拆）与耦合（coupled：联盟、共创平台）三类模式，其核心命题是：有价值的创意可以且应当跨越组织边界流动，纯粹依赖内部研发的"封闭式"范式在知识分布日益分散的环境中会系统性地错失外部机会。二十年积累的实证证据总体支持开放度与创新绩效之间的稳健关联，但也强调其边界条件——收益依赖吸收能力、治理安排与环境动态性（Zhang, Ma, Liang, & Garrett, 2024 的 meta-analysis）。落到银行金融科技场景：银行的"外部协同"公告（合作、许可、并购、战略投资、开放 API、行业联盟）对应 inbound 与 coupled 模式，"自主研发"公告对应封闭式内部 R&D 路径——这正是本文二元编码的理论根基。Dehghani, Brauneis, & Karavidas (2026) 对金融机构知识产权管理与开放式创新实践的研究表明，这一谱系已直接进入金融机构语境。

### 2.2 搜索广度与深度 (Laursen & Salter 2006)

Laursen & Salter (2006) 把企业的外部知识搜索策略操作化为广度（外部知识源的种类数）与深度（对关键知识源的依赖强度），并发现两者对创新绩效呈倒 U 形关系——过度搜索会带来注意力稀释与整合成本。该分类法为本文提供了两点支撑。第一，测度层面：银行-年外部协同新闻占比 `collab_frac` 可以解读为该银行在年度尺度上外部搜索强度的媒体映像——外部协同报道占比越高，说明该银行创新活动越多地依赖组织边界之外的知识源。第二，理论层面：搜索-整合逻辑预言外部搜索强度高的银行会积累更多关于潜在标的、伙伴质量与整合难度的私有信息，而这类信息正是并购决策的关键投入。吸收能力理论（Cohen & Levinthal, 1990）进一步指出，先前的协作经验本身会提高对外部知识的识别与整合能力，形成"协同→更强吸收→更深度协同（含并购）"的累积路径。

### 2.3 企业间 R&D 伙伴关系与并购式协同 (Hagedoorn 2002)

Hagedoorn (2002) 对 1960 年以来企业间 R&D 伙伴关系的系统梳理表明，伙伴安排存在从松散契约型（联合研发协议、许可）到紧密股权型（合资、少数股权、并购）的连续谱，且高技术产业中契约型安排的兴起并未取代股权型安排，两者更多呈阶梯递进关系：契约型合作是股权深化的信息收集与信任建立阶段。最新的战略管理证据把这一阶梯直接推进到并购端——Burford, Shipilov, & Furr (2025) 证明生态系统协同是并购的重要驱动：当焦点企业与生态伙伴的互补性上升时，收购成为内化协同收益的手段；Chen, Yang, & Wei (2025) 则表明联盟战略与技术相互依赖共同塑造生态内新创企业的成长路径，联盟网络位置决定了后续更深度绑定（含被收购）的可达性。银行业的对应含义是：外部协同倾向高的银行沿"合作→投资→并购"阶梯上行的概率更高，其金融科技并购活动应当系统性地更活跃。银行-金融科技并购本身也已形成一支新兴实证文献：金融机构股价对金科并购公告的反应（Kueschnig & Schertler, 2024）、银行商业模式在金科并购中的角色（Alfhaili, Bakoush, & Wolfe, 2025）、金科股权投资与银行创新的关联（Alfhaili, Bakoush, & Wolfe, 2026）、银行对金融科技公司的风险/少数股权投资（Puri, Qian, & Zheng, 2024；其证据与并购相邻但不同范畴，此处仅作平行参照），以及金科并购的总体图景（Zheng & Mao, 2024）——但这支文献以已实现的并购事件为起点，缺少本文所度量的事前外部协同倾向这一前置变量。

### 2.4 与 P3 (substantiveness) / P4 (locus) 的概念正交性

本文的组织来源维度（自主研发 vs 外部协同）与同管线 P3 的实质性维度（实质性 vs 象征性，Westphal & Zajac（1994, 1998）谱系）、P4 的技术位点维度（底层技术 vs 应用场景，Gomber 谱系）在概念上正交：一项公告可以是实质性的且自主研发的，也可以是象征性的且外部协同的，三个维度的任意组合都有意义。三维交叉构成 2³ = 8 个单元的完整枚举：

1. **实质性 × 底层技术 × 自主研发** → 真实内部技术能力建设（internal-tech 路径，最接近传统银行 IT 自建范式）；
2. **实质性 × 底层技术 × 外部协同** → 深度技术联盟/技术并购（获取核心技术的 inbound 开放式创新）；
3. **实质性 × 应用场景 × 自主研发** → 内部业务数字化（自建渠道与场景应用）；
4. **实质性 × 应用场景 × 外部协同** → 生态系统协作（开放 API + 业务侧共建，典型的 coupled 模式）；
5. **象征性 × 底层技术 × 自主研发** → 技术叙事包装（宣称自研核心技术但无落地细节）；
6. **象征性 × 底层技术 × 外部协同** → 联盟签署即止的技术合作（decoupling, Fiss & Zajac 2006 延伸）；
7. **象征性 × 应用场景 × 自主研发** → 场景营销化披露（应用侧宣传性报道）；
8. **象征性 × 应用场景 × 外部协同** → 战略合作签署但未执行（symbolic alliance signaling）。

若组织来源维度不携带超出 P3/P4 的边际信息，则以 8 单元指示变量饱和的回归中，collab 维度内的单元间差异应不可区分；Table 6 的饱和分解（§4.4）即检验这一点。

### 2.5 假设发展

**H1（主假设，confirmatory 单一规格）。** §2.2-§2.3 的搜索-整合逻辑与联盟-并购阶梯逻辑共同指向同一预期：外部协同倾向高的银行，经由联盟与股权合作管道积累了标的信息、伙伴信任与生态协同互补性（Chesbrough, 2003; Burford, Shipilov, & Furr, 2025），其把协作关系深化为并购交易的边际成本更低、边际收益更高。据此：

> **H1**: 银行-年外部协同新闻占比（`collab_frac`, full 轨）对该银行金融科技并购事件计数（`m_and_a_fintech`）的效应为正。主识别为同类型同业 leave-one-out 工具变量 2SLS。此为理论预期，非已得结果。

**H2（风险代价通道，exploratory secondary）。** 外部协同并非无代价：它把第三方操作风险、合作方信用风险与监管合规暴露引入银行资产负债表——中国的助贷与联合贷款监管收紧正是对这一暴露的政策回应。Wu, Shen, Wu, & Shao (2025) 提供了中国银行-金融科技战略合作提高银行风险承担的方向一致证据；自主研发路径则不产生此类第三方暴露。据此：

> **H2**: `collab_frac` 对银行稳定性指标 `z_score` 的效应为负（更高外部协同 → 更低稳定性/更高风险承担）。此为理论预期，非已得结果。

**H3（自主研发路径，exploratory secondary）。** 若组织来源编码捕捉到了真实的创新组织方式差异，则自主导向银行的创新落点应体现在内部投入与专利产出上——Lerner, Seru, Short, & Sun (2024) 表明金融创新的内部产出归属可由专利记录识别。据此：

> **H3**: 自主导向净差 `independent_minus_collab_gap`（= indep_frac − collab_frac）对研发强度 `r_and_d_intensity` 与金融科技专利计数 `patent_fintech_count` 的效应为正。此为理论预期，非已得结果。

**H4（网络位置调节，依赖生产 T=19 面板）。** 已居于同业新闻共现网络经纪/中介位置的银行，接触异质信息与潜在标的的管道更多，外部协同经验转化为并购的效率更高。据此：

> **H4**: 交互项 `collab_x_btwn`（= collab_frac × L.bank_between_cent）对 `m_and_a_fintech` 的效应为正。该假设依赖生产 T=19 面板方可检验。此为理论预期，非已得结果。
>
> TODO: H4 检验结果待生产面板回填。

---

## 3. 数据与方法

### 3.1 样本

**原始语料普查。** 测度管线始于一次过滤与去重**之前**的全量普查（stage 00 raw_census）：183 个去重后的源文件，共 **18,198,978 条**媒体报道，时间跨度 2007-01-01 至 2025-12-31，覆盖 **3,740 家**媒体来源（全类型未过滤口径）。其中媒体类型为报纸的报道占全部行的 **92.93%**（16,912,361 行）予以保留，通讯社、杂志、政府公报、网页等其余类型按行剔除；精确唯一记录 18,177,370 条，重复率 0.12%。

**过滤链条。** 进入管线的生产目标语料取普查总量口径，为 **18,198,978 条**媒体报道（2007-2025，T=19）——注意该口径为 stage 13 共现硬过滤**之前**的进入管线量；报纸保留行数（16,912,361 行）为中间处理统计量，不可与之混用。该语料随后经银行实体识别、金融科技词表匹配，进入 stage 13 共现硬过滤：仅保留"目标银行与至少一个金融科技词在 ±1 句窗口内邻近共现"的文章（生产口径 `sentence_radius=1`，且判据同时覆盖标题与正文，`match_in_title=true`）。

> TODO: stage 13 硬过滤后留存篇数为生产统计，待生产机重跑后回填。

**三轨文本物化。** 对每篇留存文章，管线物化三条平行文本轨：full（标题+正文）、ctx（标题+实体上下文窗口）、ss（标题+银行与金科词同句 ±1 句窗），三轨在下游作为互为稳健性的并列测度口径（§3.4、§5）。

**面板。** 文章级分类聚合为 **110 家中国商业银行**的银行-年面板（2007-2025, T=19）。

> TODO: 生产面板实测行数、列数与各变量非缺失观测数待生产机重跑后回填（spec 设计目标为 obs ≥ 3000；本机 dev 环境仅早期试跑 T=2 数据，不构成实测口径）。

### 3.2 度量：创新协作模式

- LLM 三模型集成（gpt-5.4-nano + gemini-3.1-flash-lite + deepseek-v4-flash）多数投票
- Prompt v8（v7 的 additive supplementation；专属 git tag prompt-v8-supplementation-released 尚未打，当前唯一已打的 prompt tag 是 prompt-v7-released）
- 二元编码: 0 = 自主研发, 1 = 外部协同
- 三轨两两一致性 κ ≥ 0.45（full/ctx/ss 两两 3 对；与 P3 实质性同阈值，fair-to-moderate；阈值定义见 `pipeline/audit/inter_track_kappa.py::_THRESHOLDS`，依据 Landis & Koch 1977）

**留篇门控（full-only）。** 一篇文章是否被判为"银行金融科技报道"进而进入测度宇宙，唯一依据 full 轨的验证结论（`llm_verified_full == True`）；ctx 与 ss 轨是 conditional-on-full 的测度/稳健性轨——其行宇宙是 full 留篇集的子集，各轨列照常计算但不独立扩充样本。

**`collab_frac` 构造。** 文章级二元分类（stage 21, Chesbrough 框架: 0=自主研发, 1=外部协同）由三家 LLM 各自独立判定后多数投票为共识标签；银行-年聚合（encode.py）取

$$
\text{collab\_frac}_{it} = \frac{\#\{\text{外部协同篇}\}_{it}}{n\_articles\_llm\_valid_{it}},
$$

分母为该银行-年通过验证门控的文章总数。共识列并非裸多数票：其上游包含验证门控、final_v 清票与（对位点维度的）关键词回退等清洗步骤。

**确定性与可复现性。** 全部 LLM 调用固定 temperature=0.0、seed=42，prompt v8 字节级冻结（缓存键 `prompt_version='v8-2026-05-17'`）；分词器锚定 `jieba==0.42.1`。缓存全命中时，整个分类层可在 `NEWS_PROCESS_LLM_OFFLINE=1` 下离线零成本、字节级复现。这一设计遵循生成式 LLM 文本测度的学科规范（de Kok, 2025），三方法并行与多数投票设计则呼应 Hansen & Kazinnik (2023) 对 GPT 类模型、词典与 BERT 在央行沟通文本（Fedspeak）分类上的系统比较，以及 Gentzkow, Kelly, & Taddy (2019) 的 text-as-data 总体框架。

**跨厂商 per-model 孪生。** 除共识列外，管线为三家模型各自物化 per-model 分类聚合 `{gpt54nano, gemini31, deepseekv4}_collab_frac_full`（分母为该模型自身 verified 篇数，并配 `_src` 指示列）。三条 per-model 臂与共识臂互为稳健性、不分主次，各自进入恰好识别的独立回归（§5）。

**测量效度（承诺而非已证）。** 本文承诺以下效度检验，其证据状态为 pending（须生产语料与真人标注兑现后方可写实）：(i) criterion validity——3 人金标注样本上的 Cohen κ、Gwet AC1 与 Krippendorff α（stage 63, Panel G）；(ii) 跨轨一致性 κ（stage 71，阈值 κ ≥ 0.45 如上）；(iii) 与相邻构念的 NMI（stage 72）与判别效度 |corr|（stage 73，对照 clarity 与数字密度测度）。在真人 κ 兑现之前，本文不声称 collab 分类的效度已被证实。

> TODO: stage 63/71/72/73 效度面板数值待生产语料 + 真人标注后回填。

### 3.3 被解释变量

- 主: `m_and_a_fintech` (Tonghuashun 数据库金融科技 M&A 事件计数)
- 短期: `car_5day_window` (5 日市场调整 CAR, 中证银行指数 benchmark)
- 次: `r_and_d_intensity` (CSMAR), `patent_fintech_count` (IncoPat), `capex_it`
- 风险代价通道: `z_score`（银行稳定性指标，H2 的被解释变量）

上述财务/并购/专利结果变量依赖后续接入的财务数据 enrichment 层（M0.5.11），当前以 capture 自校验的 wire-ahead 列形式接线，财务面板到位后即可计算——此处一句带过，不影响测度层与识别设计的完整性。

`m_and_a_fintech` 为非负偏态含零的事件**计数**变量。与 paper_spec 的 `primary_estimator: iv_2sls_peer_loo` 一致，主报告（唯一 confirmatory 规格）采用线性 2SLS（LOO 同业工具，§3.4）；针对其计数性质，按 Cohn, Liu, & Wardlaw (2022) 的建议以 PPML（ppmlhdfe，模板 `25_collab_ppml`）作为并报的计数模型稳健性，同时报告 log(1+x) OLS 作为对照并披露后者的单位依赖问题（§5）。

### 3.4 识别策略

**基线固定效应。** 基线为 long-panel 银行与年份双向固定效应回归：

$$
Y_{it} = \beta \cdot \text{collab\_frac}_{it} + X_{it}'\gamma + \alpha_i + \lambda_t + \varepsilon_{it},
$$

其中 $\alpha_i$ 为银行固定效应，$\lambda_t$ 为年份固定效应，标准误在银行层聚类。银行 FE 吸收不随时间变化的战略禀赋，年份 FE 吸收行业级冲击（监管周期、技术浪潮）。

**主识别：同类型同业 LOO 工具变量 2SLS。** `collab_frac` 内生于未观测的银行级战略偏好与投资机会。主识别以同一银行类型内**剔除自身**的其它银行平均外部协同占比作为工具（面板列 `leave_one_out_peer_collab_iv`）：

$$
\text{collab\_frac}_{it} = \pi \cdot \overline{\text{collab\_frac}}^{\,(-i)}_{g(i),t} + X_{it}'\delta + \alpha_i + \lambda_t + \nu_{it} \quad (\text{第一阶段}),
$$

$$
Y_{it} = \beta^{IV} \cdot \widehat{\text{collab\_frac}}_{it} + X_{it}'\gamma + \alpha_i + \lambda_t + \epsilon_{it} \quad (\text{第二阶段}),
$$

其中 $g(i)$ 为银行 $i$ 所属类型组。相关性来自同业战略扩散与共同的类型层冲击暴露（Manski, 1993 的反射问题正是动机所在；网络结构下的识别条件见 Bramoullé, Djebbari, & Fortin, 2009）；构造同构于金融学 LOO 同业工具先例（Leary & Roberts, 2014）。**排他性局限须如实披露**：若同业协同直接影响焦点银行的并购机会集（而非仅经由焦点银行自身协同倾向），排他性约束将被削弱——这是 LOO 同业工具的公认局限（Leary & Roberts, 2014 同样披露），我们以 Bartik 备选工具与聚类层对照部分缓解，但不声称完全排除。

**备选工具：广义 Bartik。** fallback 工具为广义 Bartik 移-份额构造（面板列 `bartik_collab_iv_full`）：以银行的基期暴露份额与行业级协同冲击交乘，识别假设转为基期份额外生性（Borusyak, Hull, & Jaravel, 2025）。另有 lag1 变体 `leave_one_out_peer_collab_iv_lag1` 作时序前定性对照。

**恰好识别纪律（铁律）。** 三条文本轨（full/ctx/ss）各配自身的 LOO 工具孪生（`leave_one_out_peer_collab_iv` 与 ctx/ss 对应列），每条轨各自进入**恰好识别**（单工具单内生变量）的独立 2SLS；三轨、两工具引擎及 lag1 变体、三 per-model 臂之间互为稳健性、不分主次，**绝不合并进同一过度识别设定做 Hansen J 检验**——合并会把"测度口径差异"错误地当作"工具有效性检验"处理。

**弱工具稳健推断。** 报告 Kleibergen-Paap F 统计量；当其低于 Stock-Yogo 临界值时，以 Anderson-Rubin 弱工具稳健置信区间为准（附表 tableA_collab_iv_arci）。

**聚类推断。** 主规格单向 bank 聚类；bank×year 双向聚类与 bank_type 类型层聚类（与 LOO 工具的组层对应）作稳健性；生产面板若簇规模高度异质，以 wild cluster bootstrap 补充。

**事件研究。** 围绕三个外生行业冲击做动态检验：E1（2013-06-13 余额宝上线）、E3（2017-04-27 资管新规）、E4（2020-11-03 蚂蚁 IPO 暂停），检验高/低 `collab_frac` 银行在冲击前后的差异轨迹与平行趋势。

**Confirmatory vs exploratory 声明。** 本文唯一 confirmatory 规格为 H1 主规格（collab_frac → m_and_a_fintech, full 轨, LOO IV, 线性 2SLS；PPML 为并报的计数模型稳健性，不属 confirmatory 估计器），不做多重检验校正；异质性与替代测度族（H2/H3、子样本切分、加权变体）全部标注 exploratory，其族内 p 值按 Romano & Wolf (2005) 逐步法做 FWER 校正（List, Shaikh, & Xu, 2019 的实施谱系）；跨模型族的 FWER 由管线根级模板（Table A12 Panel C）统一承担。

---

## 4. 实证结果

> 本节全部系数、标准误与显著性水平待生产回归后回填；以下为各表的呈现结构与解读脚手架。

### 4.1 基线与主识别 (Table 2, M1-M6)

Table 2 按 M1-M6 递进呈现主回归：M1 仅 `collab_frac` 与年份 FE；M2 加银行 FE（双向 FE 基线）；M3 加银行层控制变量；M4 加年份层控制；M5 为 LOO IV 2SLS（第一阶段与 KP F 同表报告）；M6 为 PPML 计数模型（Cohn, Liu, & Wardlaw, 2022 口径）。解读重点：(i) β 在 M1→M4 随控制加密的稳定性（选择性偏误方向的启发式证据）；(ii) M5 IV 估计与 OLS 的相对大小（衡量内生性方向）；(iii) M6 半弹性解释下的经济量级。

> TODO: Table 2 全部系数/SE/KP F/样本量待生产回归回填。
> TODO: 第一阶段 π 的符号与强度（同业扩散证据）待回填。

### 4.2 机制 (Table 3)

Table 3 检验 H2/H3 的机制通道：Panel A 以 `z_score` 为被解释变量（风险代价通道，预期为负）；Panel B 以 `r_and_d_intensity` 与 `patent_fintech_count` 为被解释变量、`independent_minus_collab_gap` 为处理（自主研发路径，预期为正）。若两个 Panel 同时成立，则组织来源维度呈现"外部协同→并购但伴随风险代价；自主研发→内部投入与专利"的分叉路径图景。

> TODO: Table 3 系数与显著性待回填；机制成立与否的结论句待回填。

### 4.3 异质性 (Table 4)

Table 4 按银行属性切分：国有/非国有、枢纽/非枢纽（新闻网络位置）、规模、银行类型与时代（era）。此外检验 H4 交互项 `collab_x_btwn`（协同×滞后中介中心度）。全部切分标注 exploratory 并做 Romano-Wolf 族内校正。

> TODO: Table 4 各切分系数与 RW 校正 p 值待回填；H4 交互项结果待生产 T=19 面板回填。

### 4.4 8-cell 饱和分解 (Table 6)

Table 6 以 `cell_id_full`（= subst×4 + locus×2 + collab + 1）的 8 单元指示变量做饱和回归，检验组织来源维度在控制 P3 实质性与 P4 位点后的边际信息量：若 collab 维度不携带独立信息，则同一 (subst, locus) 组合内 collab=0/1 两单元的系数应不可区分。该表是 §2.4 正交性主张的直接结构性检验。

> TODO: Table 6 单元系数与单元内配对检验待回填。

---

## 5. 稳健性

> 本节各梯子的数值结论全部待生产回归回填。总纪律：以下所有梯子均为**互为稳健性、不分主次**的并列设定，各自进入**恰好识别**的独立回归，绝不合并进同一过度识别的 Hansen J 检验。

**（1）三轨文本口径。** 处理变量按 full（canonical, `collab_frac`）/ ctx（`collab_frac_cm`）/ ss（`collab_frac_cm_ss`）三轨分别估计；留篇门控为 full-only，ctx/ss 是 conditional-on-full 稳健轨；三轨各配自身 LOO 工具孪生，各自恰好识别并排。

> TODO: 三轨系数对照待回填。

**（2）LLM 跨厂商 per-model 梯子。** 以 `{gpt54nano, gemini31, deepseekv4}_collab_frac_full` 三条 per-model 臂分别替换共识处理变量重估主规格，检验结果不被任一单一厂商模型驱动；三臂 co-equal，跨模型族的 FWER 校正由根级 Table A12 Panel C（CLS 族）统一承担。共识列并非裸多数票（含验证门控与清票步骤），故 per-model 臂与共识臂的差异同时反映模型分歧与清洗步骤的贡献。

> TODO: per-model 三臂系数对照与 Table A12 Panel C 校正 p 值待回填。

**（3）IV 两引擎 + lag1 前定性变体与弱工具。** 主 LOO 工具与广义 Bartik fallback（`bartik_collab_iv_full`）两引擎、外加 lag1 前定性变体并排，各自恰好识别；KP F 不足时读 Anderson-Rubin CI（tableA_collab_iv_arci）。（注：管线级"IV 三引擎"术语含媒体来源 house-style 暴露引擎；P5 无 outlet 工具列，故本文为两引擎 + 变体。）

> TODO: 两引擎 + lag1 变体的 IV 估计对照与 AR CI 待回填。

**（4）替代 treatment 与方向反转。** 以自主导向净差 `independent_minus_collab_gap`（Stata 二元化 `collab_gap ∈ {−1,0,+1}`）作方向反转稳健臂：若主结果由外部协同驱动，则净差处理下符号应反转。

> TODO: 方向反转检验待回填。

**（5）计数 outcome 估计器梯子。** `m_and_a_fintech` 的 PPML 与 log(1+x) OLS 对照（Cohn, Liu, & Wardlaw, 2022），披露 log(1+x) 的单位依赖问题。

> TODO: PPML vs log(1+x) 对照待回填。

**（6）聚类推断梯子。** cluster(bank) 主 / bank×year 双向 / bank_type 类型层三级对照；少簇/簇规模异质情形以 wild cluster bootstrap 补充。

> TODO: 聚类梯子 SE 对照待回填。

**（7）子样本与聚合加权。** SOE/枢纽/规模/类型/时代切分与 EW/VW/MW/HW 加权聚合两族，均标注 exploratory、不进入 confirmatory family。

> TODO: 子样本与加权族结果待回填。

**（8）clarity 对照稳健性 (Table A7)。** 对照文本清晰度测度检验 collab 结果的判别性（锚 Loughran & McDonald 2011 谱系的可读性/清晰度文献），排除"协同报道只是更可读/更模板化"的替代解释。

> TODO: Table A7 待回填。

**（9）Romano-Wolf FWER 纪律。** 单一 confirmatory 主规格不校正；异质性/替代测度族按 Romano & Wolf (2005) 逐步法族内校正（List, Shaikh, & Xu, 2019）；跨模型族由根级 Table A12 Panel C 承担。

**不适用梯子的负面声明。** 管线中的词典消融变体、政治词权重梯子 {0.0, 0.5, 1.0}、罕见词 cutoff 梯子、BERT 三模型 net_tone 与网络构造判据梯子属于情感/词典/网络测度族，P5 的处理变量是 LLM 分类而非情感或嵌入，上述梯子不构成本文的稳健性检验；管线的 co-primary 双嵌入轨（Qwen3-Embedding-8B 4096 维 canonical + text-embedding-3-large 3072 维 `_lg`，Spearman ρ≥0.80 语义效度闸）仅在描述管线全貌时作方法背景提及，不进入 P5 的任何回归。

---

## 6. 讨论

**开放 vs 封闭创新的边际收益条件。** 若 §4 的分叉路径图景成立（外部协同→并购、自主研发→内部投入与专利），则开放式创新对银行的边际收益并非无条件为正，而取决于创新落点在业务侧还是技术侧：业务侧（应用场景、渠道、生态）的知识分散于外部伙伴，开放模式的搜索收益高；技术侧（核心系统、底层架构）的知识专用性与安全合规约束强，封闭模式的整合收益高。这与 Zhang et al. (2024) meta-analysis 强调的边界条件一致，也与 8-cell 分解（Table 6）中"实质×技术×自主"与"实质×应用×协同"两个理论上最优单元的对照相呼应。

> TODO: 该段的结果依赖表述待生产回归后按实回填。

**风险代价通道与监管含义。** H2 若成立，外部协同的并购收益伴随稳定性代价——这为中国助贷/联合贷监管收紧提供了微观证据基础：监管的合理目标不是压制银行-金科协同本身，而是为协同引入的第三方风险暴露定价（Wu, Shen, Wu, & Shao, 2025 的方向一致证据；Hau et al., 2024 关于金科信贷实体效应的证据提示协同亦有真实经济收益，权衡而非禁止是恰当框架）。

> TODO: 风险通道量级与政策含义细化待回填。

**管理启示。** 对银行管理者：组织来源选择应与创新落点匹配——生态位/业务侧优先开放协同（并预算第三方风险管理成本），核心技术侧的自建投入不可被协同替代；对处于网络中介位置的银行（H4），协同管道的并购期权价值更高。

**局限。** 第一，二元 proxy 压缩了伙伴强度、伙伴类型与合作范围的信息（Chesbrough/L&S 的谱系本质；详见文末局限性声明）。第二，本文识别是观测性的：LOO 同业工具的排他性约束不可检验，Bartik 备选与聚类对照只能部分缓解；事件研究提供辅助动态证据但不改变观测性本质。第三，媒体报道本身内生——报道倾向高的银行可能系统性不同，`collab_frac` 度量的是"被报道的协同倾向"。第四，年度频率抹平了年内战略调整的动态。第五，中国单一市场的制度特殊性（国有银行主导、强监管周期）限制外推，跨国可比较研究是自然延伸。

---

## 7. 结论

本文为银行金融科技创新文献补上了组织来源这一维度：基于生产目标语料取普查总量口径 18,198,978 条报道（2007-2025）的中国银行金融科技新闻，用三家大语言模型在字节级冻结 prompt 与 temperature=0 下的多数投票，构造了 110 家中国商业银行的银行-年外部协同新闻占比 `collab_frac`，并以同类型同业 LOO 工具变量 2SLS 为主识别，检验开放式创新倾向对金融科技并购（H1）、风险承担（H2）与内部创新产出（H3）的效应。

> TODO: 主结论句（H1-H3 的实证判定）待生产回归后回填。

理论上，本文把 Chesbrough 开放式创新、Laursen-Salter 搜索分类法与联盟-并购阶梯文献带入银行金融科技场景，并以与实质性（P3）、位点（P4）正交的 2³=8 单元饱和分解给出组织来源维度边际信息量的结构性检验。方法上，本文示范了一个确定性、可离线复现、跨厂商三角验证的 LLM 文本测度管线，符合 text-as-data 与生成式 LLM 测度的最新学科规范。政策上，若风险代价通道成立，本文为"给协同风险定价而非禁止协同"的监管框架提供微观证据。

> TODO: 结论段的结果依赖表述待生产回归后回填。

---

## 参考文献

- Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2025). The role of banks' business models in their FinTech acquisitions. *Journal of Financial Services Research*. https://doi.org/10.1007/s10693-024-00442-w
- Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. *Journal of International Financial Markets, Institutions and Money*, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
- Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. *Journal of Economic Perspectives*, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
- Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of peer effects through social networks. *Journal of Econometrics*, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
- Burford, N., Shipilov, A., & Furr, N. (2025). Ecosystem synergies as drivers of acquisitions. *Strategic Management Journal*, 46(13), 3218-3251. https://doi.org/10.1002/smj.3729
- Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence. *Journal of Management Studies*, 62(2), 565-596. https://doi.org/10.1111/joms.13063
- Chesbrough, H. (2003). *Open Innovation: The New Imperative for Creating and Profiting from Technology.* HBS Press.
- Cohen, W. M., & Levinthal, D. A. (1990). Absorptive capacity: A new perspective on learning and innovation. *Administrative Science Quarterly*, 35(1), 128-152.
- Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. *Journal of Financial Economics*, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
- de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. *Management Science*, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
- Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. *Technological Forecasting and Social Change*, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. *Academy of Management Journal*, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
- Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. *Journal of Economic Literature*, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
- Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. *Research Policy*, 31(4), 477-492. https://doi.org/10.1016/S0048-7333(01)00120-2
- Hansen, A. L., & Kazinnik, S. (2023). Can ChatGPT decipher Fedspeak? *SSRN Working Paper No. 4399406*. https://doi.org/10.2139/ssrn.4399406
- Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. *The Journal of Finance*, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
- Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. *Finance Research Letters*, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779
- Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. *Biometrics*, 33(1), 159-174. https://doi.org/10.2307/2529310
- Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. *Strategic Management Journal*, 27(2), 131-150. https://doi.org/10.1002/smj.507
- Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? *The Journal of Finance*, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
- Lerner, J., Seru, A., Short, N., & Sun, Y. (2024). Financial innovation in the twenty-first century: Evidence from US patents. *Journal of Political Economy*, 132(5), 1391-1449. https://doi.org/10.1086/727712
- List, J. A., Shaikh, A. M., & Xu, Y. (2019). Multiple hypothesis testing in experimental economics. *Experimental Economics*, 22(4), 773-793. https://doi.org/10.1007/s10683-018-09597-5
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. *The Journal of Finance*, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
- Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. *The Review of Economic Studies*, 60(3), 531-542. https://doi.org/10.2307/2298123
- Puri, M., Qian, Y., & Zheng, X. (2024). From competitors to partners: Banks' venture investments in fintech. *NBER Working Paper No. 33297*. https://doi.org/10.3386/w33297
- Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. *Econometrica*, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
- Vives, X. (2019). Digital disruption in banking. *Annual Review of Financial Economics*, 11, 243-272. https://doi.org/10.1146/annurev-financial-100719-120854
- Wu, M., Shen, L., Wu, T., & Shao, Y. (2025). Does strategic cooperation between banks and fintech companies increase bank risk-taking? Evidence from China. *Applied Economics* (advance online publication). https://doi.org/10.1080/00036846.2025.2536881
- Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. *Journal of Product Innovation Management*, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
- Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. *Journal of International Money and Finance*, 143, 103076. https://doi.org/10.1016/j.jimonfin.2024.103076

---

## 局限性声明 (Pre-registration β supplementation)

本研究采用二元分类（自主研发 vs 外部协同）作为 Chesbrough 开放式创新连续 spectrum 与 Laursen & Salter 连续搜索广度-深度的离散 proxy。二元度量压缩了关于伙伴强度、伙伴类型、合作范围的信息，未来研究可拓展为多类（如 M&A vs 战略投资 vs 开放 API vs 行业联盟）。

本研究使用的 LLM 分类 prompt 模板（prompt v8）是预注册的 v7 prompt（git tag `prompt-v7-released`）的**纯增量补充（additive supplementation）**；v7 中的验证、情感、实质性、位点判定规则完全保留（纯增量、不修订既有判定规则的 additive non-revisionary 补充，遵循预注册增补规范）。新增的创新协作模式维度计划在最终 production 重跑后通过 git tag `prompt-v8-supplementation-released` 锚定（该 tag 尚未创建）。

**实证状态声明。** 本稿撰写环境为开发机（仅早期试跑 T=2 数据），无任何生产回归结果；§4/§5 的全部系数、标准误与显著性均为待回填占位。财务/并购/专利 enrichment 层（M0.5.11）后续接入，相关 outcome 列以 wire-ahead 形式已接线。

**LLM 使用披露（指针）。** 与同管线其余论文一致，本文的 LLM 使用披露包含: (i) LLM 路由——文章级分类由三家模型（gpt-5.4-nano 与 gemini-3.1-flash-lite 经 OpenLux 路由、deepseek-v4-flash 直连）在 temperature=0.0、seed=42、prompt v8 字节级冻结下完成，多数投票聚合; (ii) 留篇门控为 full-only（`llm_verified_full`），ctx/ss 轨为 conditional-on-full; (iii) 管线的 co-primary 双嵌入轨（Qwen3-Embedding-8B canonical + text-embedding-3-large `_lg`）仅作为管线背景，不进入 P5 的处理变量或任何回归。完整披露文本见 `papers/_common/AI_DISCLOSURE_TEMPLATES.md`。 平台迁移说明: 本文数据的 LLM 推理于 2026 年 7 月经本管线当时的聚合中转代理完成; 自 2026 年 8 月起, 管线的聚合中转统一迁移至 OpenLux (`https://api.openlux.ai/v1`)。缓存键由「模型名 + prompt 文本 + prompt 版本 + temperature」四元组构成、不含端点地址, 故本次迁移对既有推理结果逐位无影响。
