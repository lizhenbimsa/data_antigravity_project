# 文献理论锚点扩充报告 · 第十补编(全指标家族 2024–2026 前沿锚点专项 · 20 主题桶 · **实际接线 328 个指标家族** · APA 第 7 版 · Crossref/DataCite DOI→标题回比 + 权威元数据逐条回填全核验 · 8 维度顶刊标准对抗终审)

- **日期**: 2026-07-17
- **定位**: 本文件是前九份锚点文件之后的 **第十补编**, 十者**合为一套**。前九份 + 两份并入文档 = **1152 个唯一 doi.org DOI**(`audit_dois.py` 本轮起跑前实测: 1,148 OK / 3 既有 benign / 1 已修红灯)。
- **本补编专项**: 前九份补编按**功能模块/新增指标批次**推进, 因而覆盖天然偏向"新上线的指标族"。本补编改从**指标家族全库反查**入手: 对 `config/codebook_longdesc/` 全部 **655 个指标家族**逐族实测引文年代结构, 定位出 **59 个家族零 2024+ 锚点、211 个家族 ≤1 条 2024+ 锚点、268 个家族处于 3–5 条引文地板**, 据此为 **328 个真缺口家族**补齐 2024–2026 最新前沿出处。这是主锚点体系首次以"**指标家族覆盖度**"而非"功能批次"为组织维度的补编。
- **同轮机械闸修复**: `10.1007/s10479-024-06163-6` (Wang et al., *Annals of Operations Research*) 长期以 online-first 年份 2024 入库, 本轮经权威回读定谳其**卷期年为 2026** (357(1), 739-777) —— F463 家族 frontmatter 年份、卷期页、正文引注同步修正, YEAR_DIFF 红灯清零。
- **规模与流水线**: 20 主题桶并行动态多智能体工作流(40 agents)。
  1. **发现层**(20 agents): 每候选提名前实时 `GET api.crossref.org` / `api.datacite.org` 读回标题自比对 —— **发现层自弃 189 条**(查不实 / 题名不符 / 撤稿 / 已在池), 提名 298 条。
  2. **对抗层**(20 agents, 各桶独立, 默认怀疑、举证责任在候选方): 逐条重新回读 DOI + claim-fit 质询。判定分布 = **keep 130 / overclaim 161 / wrong_paper 5 / metadata_error 2**。⚠ **161 条(占提名 54%)的锚定说明被判「夸大」并强制改写为诚实降级版** —— 本补编收录的即降级版, 原始夸大版一律作废。典型判杀: 一篇刊名含 *China* 但样本实为**美国** 5,640 家公司/RavenPack 英文库者被定谳"说明自始建立在错误前提上"; 一篇用 LLM 生成**合成受访者**做问卷模拟者被判**范畴错误**(无真实语料/无极性标注)。
  3. **政策剔除**: wrong_paper 5 条 + 对抗层剔光全部锚定家族者 7 条 = 12 条不予收录。
  4. **主控独立回填**(不信任 agent 任何转写): 逐条直连 Crossref/DataCite 拉权威书目(作者序/年份/卷期/页码/标题/撤稿) —— 246 条唯一 DOI 中丢弃 1 条(权威元数据不全), **agent 自报 vs 权威回读 drift = 1 处**(发现层实时回读纪律的实证)。
  5. **APA 程序化机械拼装**: 复用**生产渲染器** `codebook_longdesc.render_citation_apa`(与家族 md 引文同一函数), 非人工转写。
  6. **接线层**(111 agents)+ **悬空收尾**(16 agents): 逐族相关性复核, 弃用 **840 条**「候选×家族」配对; 最终 **212 条**锚点实际接入 **328 个**家族, **33 条**未接入任何家族(见 §3.3)。
  7. **顶刊标准 8 维度对抗终审**(16 agents: 8 审 + 8 独立复核)→ **18 条 confirmed / 6 条被复核推翻**; 全部 confirmed 项已整改(见 §四)。
  8. 全语料去重(对既有 1152 DOI 池) = **净增 245 条唯一锚点**, 其中 **2024–2026 者 239 条(98%)**。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编经**发现层自核验 + 对抗层独立回读复核 + 主控权威回填 + 全语料机械闸 + 顶刊标准多智能体终审**五道核验; 全语料本地决定性闸 = `scripts/audit/audit_dois.py`。
- **合计**: 1152(前九份 + 两份并入) + **245(本补编净增)** = **1397 个**唯一 doi.org DOI(以 `audit_dois.py` 实测为准)。

---

## 〇、白话导读

**这份补的是什么**: 前九份补编都是"项目又加了什么新功能, 就给这个新功能配文献"。这次反过来: 把项目里**全部 655 个指标**(每个指标一份长文档, 里面列着支撑它的文献)挨个数了一遍它们各自的引文都是哪年的, 结果发现有 **59 个指标一条 2024 年以后的文献都没有**, 还有 211 个只有一条。这些指标本身没问题、文献也不是错的, 只是**配的都是老文献**——比如"数词典里有几个正面词"这种最基础的指标, 配的是 2011 年的经典, 但 2024-2026 年这个领域其实又出了一批新东西(比如大模型能不能替代词典、词典法在深度学习时代还站不站得住)。这份补编就是专门给这些"老文献撑着的指标"补上最新的前沿出处。

**为什么这事有必要**: 项目有一道自动闸门规定"2023 年以后的文献必须占到一半以上", 而实测**正好卡在 50.0%**(2536/5070)——**再多一条老文献就会当场判死**。这次补进来的全是 2024-2026 的新文献, 等于把这条红线的安全余量做厚。

**每一条都不是编的**: 每条文献在被提名之前, 智能体必须先拿 DOI 去官方接口(Crossref/DataCite)把标题读回来核对; 之后另一批**专门唱反调的智能体**再独立读一遍, 专门找"这个 DOI 是真的但内容对不上""这篇文献根本没做过你说的那件事"这类问题; 最后主控**不信任任何智能体的转写**, 逐条自己直连官方接口把作者、年份、卷期、页码原样拉回来, APA 参考文献是**程序自动拼**出来的(用的就是项目生产代码里那个渲染函数), 不经过人手。每条后面的〔回读标题〕就是官方接口实际返回的原文。

**怎么用**: 写论文/codebook 时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。工作论文条目引用时须标注 working paper 状态。

**一句话铁律提醒**: 本补编涉及的多条"梯子"(三轨 full/ctx/ss · 六词典 · 三权重 · 三家 LLM · 三个 BERT · 阈值/分位梯子 · 判据敏感性)**一律是"互为稳健性、不分主次"**——各自 just-identified 并排, **严禁混进同一 over-identified Hansen J**。这条与代码 codebook 铁律一致, 引用时须在方法节写明。

---

## 一、20 主题桶 × 新增已核验锚点(2024–2026 优先; 〔〕内为接口回读标题原值)


### 十补-1. 词典法情感原始计数层 (pos_count / neg_count / *_symb_count / *_substvalid_count / msent)

> 净增 12 条(其中 2024–2026 者 12 条)。**已接线家族** (44): F057, F058, F130, F136, F192, F193, F219, F220, F221, F223, F306, F309, F353, F354, F448, F454, F456, F473, F475, F476, F477, F478, F479, F513, F515, F521, F524, F548, F549, F593, F594, F596, F602, F604, F616, F628, F629, F630, F631, F636, F645, F646, F647, F648

- 【2024–2026】Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
  - *锚定* — 原文构造针对特定银行的媒体情感测度, 并检验其与监管行为的关联, 属「银行为对象的媒体情感计数/极性测度」这一同域前沿应用。它证明了把新闻情感按银行主体归集并进入银行层面实证是当前被顶级金融稳定期刊接受的做法, 但未涉及本项目的三轨文本或 LLM 投票口径。
  - *迁移边界* — 原文为美国银行监管语境(监管评级/监管行动为 DV), 本项目为中国商业银行×金融科技报道语境且 DV 另定; 原文情感测度的构造细节与本项目六词典 union、逐篇 (neg-pos)/(neg+pos) 归一化口径不同; 原文无实质性/象征性创新话语分类维度。
  - 〔Crossref 回读标题: Does media sentiment influence bank supervision?〕
  - 〔已接线家族 (11): F057, F058, F219, F220, F221, F448, F454, F593, F594, F628, F629〕
- 【2024–2026】Battalio, R., Loughran, T., & McDonald, B. (2026). How managers frame capital budgeting in investor communications. Journal of Corporate Finance, 100, 103033. https://doi.org/10.1016/j.jcorpfin.2026.103033
  - *锚定* — Battalio, Loughran & McDonald (2026) 自建 45 个资本预算术语的词表, 对 2010–2020 年业绩说明会文本做逐词命中统计以刻画管理者措辞框架, 是「固定词表逐词命中的原始词次计数 (不做长度归一、不跨词表聚合)」这一构造在金融顶刊仍属活跃做法的直接证据, 且由金融词典法原始提出者参与。仅此: 原文测度的是术语使用频次而非情感极性, 不涉及正/负面判定, 更不涉及按极性符号对篇数分拆, 因此只锚定 F646 的原始命中词次形态。迁移边界同原候选, 但删去「原文并未提出新词典」一句 (原文明确构造了 45 词的资本预算词表), 改为: 原文词表为英文术语表且无否定翻转/程度副词/转折规则层, 本项目为中文情感词表加三规则。
  - 〔Crossref 回读标题: How managers frame capital budgeting in investor communications〕
  - 〔已接线家族 (2): F645, F646〕
- 【2024–2026】Chen, Z., Hajiheydari, N., Zhang, M., & Lin, Y.-E. (2026). Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling? The Journal of Strategic Information Systems, 35(2), 101971. https://doi.org/10.1016/j.jsis.2026.101971
  - *锚定* — Chen 等 (2026, JSIS) 基于注意力基础观提出企业数字化转型关注度 (CDTA), 以中国上市公司 2007–2020 年样本, 在「战略实质承诺 vs 象征性信号」两个**对立**解释间做检验, 发现 CDTA 与突破式创新相关而与渐进式创新及研发支出无关, 从而**支持实质承诺说、未支持象征性信号说**, 且数字话语与创新的一致性在高问责情境下最强。其价值在于: 该二分本身是当代数字化/科技话语研究的主流理论框架, 且证明「话语是否只是象征」是可被实证证伪的经验问题 —— 这正是本桶 symb 系列构念的理论锚点与反面参照 (不可据此宣称原文提供了象征性解释)。迁移边界同原候选 原文以「话语关注度 vs 实际创新产出」间接推断, 本项目以 LLM 对单篇报道直接标注实质性/象征性, 判定机制不同; 原文文本源为公司自述披露, 本项目为第三方新闻; 原文层级=公司-年, 本项目=银行-年且分三轨。
  - 〔Crossref 回读标题: Corporate digital transformation attention and innovation: strategic commitment or symbolic signalling?〕
  - 〔已接线家族 (8): F223, F354, F478, F548, F630, F631, F647, F648〕
- 【2024–2026】Bai, C., Duan, Y., & Goodell, J. W. (2025). Multi-media sentiment to systemic risk: Evidence from COVID-19. International Review of Economics & Finance, 97, 103745. https://doi.org/10.1016/j.iref.2024.103745
  - *锚定* — Bai, Duan & Goodell (2025) 用 2020 年 2–4 月来自官方新闻媒体、新浪微博与微信的 880 万条中文文本构造日度情感指数, 发现媒体情感上升经缓解存款人挤兑而降低系统性风险, 且**渠道间情感分歧**扩大会加剧系统性风险, 提供「中文媒体情感测度进入银行体系风险实证」的近期同域证据, 并佐证多来源情感测度并排后其分歧本身具有信息含量。仅此: 原文情感指数的构造口径 (是否为词表命中计数) 未见披露, 测度单元为日度指数而非按银行-年对篇数做极性符号分拆; 其「多源」指媒体渠道, 与本项目「多词典 × 三文本轨」并排不是同一维度, 不可据此宣称锚定词典并排设计。
  - 〔Crossref 回读标题: Multi-media sentiment to systemic risk: Evidence from COVID-19〕
  - 〔已接线家族 (1): F057〕
- 【2024–2026】Guan, J., & Zhuang, X. (2025). Do digital words reflect real innovation? Evidence from post-M&A earnings conference. Asian Review of Accounting, 1-44. https://doi.org/10.1108/ara-01-2025-0031
  - *锚定* — 原文的核心问题正是「数字化措辞是否对应真实创新」, 即科技话语的象征性与实质性之辨, 并在中国并购语境下用文本测度做实证。这与本桶 symb_frac 及各 *_pos_symb_count 家族的构念(正面科技话语中区分象征性叙事)高度同域。原文只检验了数字化词汇与后续创新产出的对应关系, 未提出象征性/实质性的逐篇标注方案。
  - *迁移边界* — 原文文本源=并购后业绩说明会(管理层自述), 本项目=第三方新闻报道; 原文以「数字词汇量 vs 实际创新指标」间接推断象征性, 本项目以 LLM 逐篇直接标注象征性; 原文分析单元=并购事件/公司-年, 本项目=银行-年三轨并排。
  - 〔Crossref 回读标题: Do digital words reflect real innovation? Evidence from post-M&amp;A earnings conference〕
  - 〔已接线家族 (6): F223, F354, F478, F479, F548, F631〕
- 【2024–2026】Kanagaretnam, K., Li, W., Shi, G., & Zhou, Z. (2025). Ambiguity of tone in annual reports and bank risk taking. Accounting & Finance, 65(1), 935-970. https://doi.org/10.1111/acfi.13353
  - *锚定* — Kanagaretnam 等 (2025) 以银行 10-K 文本的语调模糊度 (由分离混淆/信息成分的语调模型残差估计) 进入银行风险承担面板回归, 提供「银行文本的词表型语调测度可作为银行风险实证解释变量」这一同域前沿应用与效度证据。仅此: 原文的具体语调构造为残差化的模糊度指标, 未见 (neg-pos)/(neg+pos) 比率式极性口径, 亦不涉及按极性符号对多篇文本计数 (10-K 每银行-年仅一份文档)。迁移边界同原候选, 另须补: 原文分析单元为单文档, 与本项目逐篇计数后聚合的分母结构不同。
  - 〔Crossref 回读标题: Ambiguity of tone in annual reports and bank risk taking〕
  - 〔已接线家族 (2): F057, F628〕
- 【2024–2026】Lehkonen, H., Heimonen, K., & Pukthuanthong, K. (2025). Media tone is a priced risk factor in currency markets. Journal of Banking & Finance, 180, 107542. https://doi.org/10.1016/j.jbankfin.2025.107542
  - *锚定* — Lehkonen 等 (2025) 用 Refinitiv MarketPsych 指数 (覆盖 2000 家全球媒体与 800 家社交站点的约 700 万篇文本) 构造媒体语调, 证明比率型媒体语调 (正负提及净额/总提及) 是可跨截面定价货币的真实风险因子, 为「媒体文本→比率型语调」这一测度形态提供近期顶刊级的经济含义论证。仅此: 原文语调取自专有商业 NLP 指数而非自建词表命中计数, 构造细节不可复核; 原文亦无任何按极性符号对主体-期篇数分拆的操作。迁移边界同原候选, 另须补: 原文语调来源为专有指数, 本项目为公开中文词典自建计数, 二者构造透明度不可比。
  - 〔Crossref 回读标题: Media tone is a priced risk factor in currency markets〕
  - 〔已接线家族 (6): F057, F058, F136, F306, F309, F636〕
- 【2024–2026】Zhao, J., & Ren, M. (2025). Innovative or conservative? How clan culture shapes bank digital transformation in China. China Journal of Accounting Research, 18(2), 100406. https://doi.org/10.1016/j.cjar.2025.100406
  - *锚定* — Zhao & Ren (2025, CJAR) 研究中国非正式制度对银行数字化转型 (BDT) 的影响, 发现宗族文化经「短半径信任推高物理网点与人员依赖」与「风险规避降低风险承担意愿」两条供给侧机制、以及「宗族内资源共济削弱信贷需求」的需求侧机制抑制 BDT, 是与本项目**同国别、同行业 (中国商业银行)、同为银行-年文本型变量**的近期同域研究。仅此: 原文的 BDT 测度构造口径 (是否为分词后固定词表逐词命中计数) 在可得材料中**未见披露、未经核实**, 故只能作为「中国银行业以文本型变量构造银行-年测度」的同域存在性参照, **不可据此宣称词表命中频次的技术路线获得背书**; 原文亦无情感极性、无正/负面判定, 因而不锚定任何按极性符号计数篇数的家族。迁移边界同原候选 原文词表 (若有) 为数字化/科技关键词而非情感词表; 文本源=银行年报 (每银行-年单文档), 本项目=第三方新闻报道逐篇后聚合; 原文无否定翻转/程度副词/转折三规则层, 也无 full/ctx/ss 三轨。
  - 〔Crossref 回读标题: Innovative or conservative? How clan culture shapes bank digital transformation in China〕
  - 〔已接线家族 (3): F353, F645, F646〕
- 【2024–2026】Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
  - *锚定* — Cheng, Jiang & Song (2024) 以 RavenPack (Dow Jones Newswires 全量、relevance=100) 把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量 (Total_News) 与新闻情感, 作为解释变量进入债务融资方式选择回归, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率, 是「文章级极性判定 → 按主体-年对极性指示求和/归集」这一聚合范式的前沿实证用例。仅此: 该文只做公司层面的媒体计数与融资选择关联, 未涉及 LLM 判定, 亦无提及密度加权变体。迁移边界 (对抗层更正): 原文主体=美国上市公司 (非银行); **原文极性来自 RavenPack 专有事件情感分析 (ESS), 既非公开情感词典、亦非人工编码, 更非本项目的三家 LLM 多数投票**, 故对 F448/F473 只锚定「按主体-年对极性指示求和」这一聚合形态, 不锚定其极性来源; 原文无 _vw 提及密度加权变体。
  - 〔Crossref 回读标题: Media coverage and debt financing choice〕
  - 〔已接线家族 (11): F192, F221, F448, F454, F456, F473, F475, F628, F629, F630, F647〕
- 【2024–2026】Granados, C., Ayala, Y., & Ramos-Mejia, M. (2024). Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation. Technovation, 129, 102880. https://doi.org/10.1016/j.technovation.2023.102880
  - *锚定* — 原文系统刻画「创新剧场」(innovation theater) 现象, 即技术创新的象征性展演与实质性投入的分野, 为本桶象征性/实质性二分提供当代组织理论层面的构念界定与机制阐述。原文为组织层面的质性/理论化研究, 并未提供文本自动分类算法, 也未做银行样本的计量。
  - *迁移边界* — 原文是组织行为学层面的构念研究(技术创新的象征性展演), 本项目把该构念操作化为 LLM 对新闻报道话语的逐篇标签并按银行-年计数, 操作化层级与数据类型均不同; 原文非中国语境、非银行业、无面板计量。
  - 〔Crossref 回读标题: Is it substantive or just symbolic? Understanding innovation theater in organisations: The case of technology-based innovation〕
  - 〔已接线家族 (6): F476, F477, F478, F479, F524, F548〕
- 【2024–2026】Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
  - *锚定* — 该文以金融科技发展为解释变量, 检验其对企业实质性绿色创新与象征性绿色创新的差异化影响, 在中国情境中明确采用「实质性 vs 象征性」创新二分。这与本项目 innovation_substantiveness 的二分标签在概念与中文表述上直接对应, 是该二分在金融科技议题下的同域应用。
  - *迁移边界* — 原文的实质/象征由专利类型 (发明 vs 实用新型/外观) 客观划分, 主体为非金融上市公司, 金融科技是解释变量; 本项目实质/象征由 LLM 对新闻文本判定 (非专利数据), 主体为银行, 金融科技是被报道的议题本身。原文亦未构造任何比率型 washing 指标。
  - 〔Crossref 回读标题: Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation〕
  - 〔已接线家族 (13): F130, F193, F456, F476, F477, F478, F513, F515, F521, F548, F602, F604, F616〕
- 【2024–2026】Wang, K. T., Zhu, N. Z., & Luo, G. (2024). Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China. Abacus, 60(4), 709-751. https://doi.org/10.1111/abac.12322
  - *锚定* — Wang, Zhu & Luo (2024, Abacus) 用逾 188,000 篇出自中国最有影响力报纸、由记者撰写的公司特定报道, 把新闻报道按公司-年归集为计数型暴露变量, 检验其对企业创新产出的影响 (效应在治理薄弱、披露不透明、研发密集、融资受限的公司更强, 且在创新与治理类报道、政治干预较少与社会关联较弱的媒体更强)。其锚定价值仅限两点: 中文报纸报道的**报道量计数**可作为主体-年层面的文本暴露变量; 以及新闻媒体与创新之间存在实证链条。仅此: 未见原文构造任何语调/情感变量 (摘要与可得材料只披露报道量与报道主题/媒体属性分组), 故不锚定极性来源; 原文的创新是产出侧 DV, 不对报道话语做实质性/象征性分类, 不可用作 symb 系列测量层家族的锚点。迁移边界同原候选。
  - 〔Crossref 回读标题: Does News Media Affect Firm Innovation in Emerging Markets? Evidence from China〕
  - 〔已接线家族 (4): F192, F473, F549, F596〕


### 十补-2. 词典法情感面板求和与加权聚合 (tone_sum / score_{w,hw,mw}_sum / idf_score_*_sum)

> 净增 15 条(其中 2024–2026 者 15 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (42): F118, F124, F125, F127, F134, F136, F191, F215, F225, F291, F292, F295, F299, F301, F305, F308, F320, F347, F349, F356, F415, F416, F417, F424, F426, F443, F536, F539, F541, F544, F568, F623, F625, F627, F632, F633, F634, F636, F642, F644, F650, F651

- 【2024–2026】Harford, J., He, Q., & Qiu, B. (2026). Firm-Level Labor Shortage Exposure. The Review of Financial Studies, hhag049. https://doi.org/10.1093/rfs/hhag049
  - *锚定* — 原文自财报电话会文本提取公司层面'劳动力短缺暴露'测度,并在州/行业/公司三个层级做效度验证,再检验其对CAR/未来收益/经营绩效的预测力。为本桶value-weighted族所用的文本提及型 firm-level exposure 权重(mention_density,Hassan2019同族口径)提供近期构造与验证范例。
  - *迁移边界* — 原文为英文earnings call,度量的是'劳动力短缺暴露'而非情感极性;原文把暴露度直接当自变量,未将其作为乘性权重乘到词典情感分上(本项目 w=mention_density 与 score 相乘后再求和),且无银行-年三轨聚合。
  - 〔Crossref 回读标题: Firm-Level Labor Shortage Exposure〕
  - 〔已接线家族 (5): F125, F134, F417, F634, F651〕
- 【2024–2026】Nakatsuka, H., & Suimon, Y. (2026). How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures. Economics Letters, 265, 113002. https://doi.org/10.1016/j.econlet.2026.113002
  - *锚定* — 原文对日本公司披露文本**联合分析文本相似度(新颖性)与情感**,检验市场对文本新颖性的反应。这是本桶六个 hw(羊群衰减)族当前最贴近的近期锚点: 本项目 score_hw = score × 1/(1+n_similar_articles) 正是'情感 × 新颖性(相似度的减函数)'的乘性结构,原文证明二者须联合而非各自单独看待。
  - *迁移边界* — 原文文本为日本公司**披露文件**(非第三方媒体报道),语言为日文;其相似度是披露文本间的连续相似度,且与情感做**联合分析/交互**,并非本项目 1/(1+n_similar) 这一具体倒数衰减函数形式,也未把二者相乘折叠成单一加权分再在银行-年内求和;层级为披露事件而非银行-年三轨。
  - 〔Crossref 回读标题: How does the market respond to textual novelty: Joint analysis of similarity and sentiment on Japanese corporate disclosures〕
  - 〔已接线家族 (6): F347, F356, F415, F424, F623, F632〕
- 【2024–2026】Turetken, A. C., & Leippold, M. (2026). Battle of transformers: Adversarial attacks on financial sentiment models. Journal of Banking & Finance, 188, 107698. https://doi.org/10.1016/j.jbankfin.2026.107698
  - *锚定* — 原文对两个主流金融情感模型 (FinBERT 与生成式 Fin-GPT) 施加白盒对抗扰动, 发现二者的情感**标签预测**在语义保持的扰动下均被大比例翻转, 说明金融情感分类器的标签输出并非稳固不变。本项目据此仅取一条弱结论: 单一分类器的标签输出不应被当作无误差的构念真值, 因而对同一构念保留三个模型各自的 argmax 标签计数并排 (F291/F299) 作为规格稳健性维度, 而非依赖任一模型。原文为英文基准数据集上的对抗鲁棒性评测, 未比较各模型的 softmax 概率稳定性, 未报告模型间脆弱性差异 (其结论为两模型均脆弱), 所涉 Fin-GPT 亦非 BERT 架构; 原文不构成本项目概率口径 (概率和/中性概率均值) 或 per-model 并排设计的证据。
  - 〔Crossref 回读标题: Battle of transformers: Adversarial attacks on financial sentiment models〕
  - 〔已接线家族 (3): F118, F291, F299〕
- 【2024–2026】Chen, L., & Mankad, S. (2025). A Structural Topic and Sentiment-Discourse Model for Text Analysis. Management Science, 71(7), 5767-5787. https://doi.org/10.1287/mnsc.2022.00261
  - *锚定* — 原文提出 STS 主题模型, 引入文档级的连续情感-话语潜变量并允许其被文档级协变量解释, 使文本情感可进入正式的统计推断而非仅作描述性摘要。本项目据此仅取一条弱锚定: 以篇级**连续**情感量 (而非硬标签) 作为文本测度的基本单位, 在前沿是被接受的做法, 支撑本项目保留篇级概率再入面板 (F292/F301) 而非只用 argmax 标签。原文的情感量是贝叶斯生成模型的连续后验潜变量, 与 BERT softmax 的类别概率语义不同, 且原文无中性类别、无篇级概率在单元内求和/取均值的聚合步骤 (其用法是潜变量对协变量回归), 语料为评论/调查文本非中文银行新闻, 无实体-年面板与加权口径。
  - 〔Crossref 回读标题: A Structural Topic and Sentiment-Discourse Model for Text Analysis〕
  - 〔已接线家族 (5): F292, F295, F301, F305, F308〕
- 【2024–2026】Cong, L. W., Liang, T., Zhang, X., & Zhu, W. (2025). Textual Factors: A Scalable, Interpretable, and Data-Driven Approach to Analyzing Unstructured Information. Management Science, 71(12), 10727-10739. https://doi.org/10.1287/mnsc.2020.01180
  - *锚定* — 原文提出可扩展文本因子框架(词向量表示→LSH聚类→主题建模识别可解释张成簇),明确把'构造新的文本测度与解释变量'列为三类应用之一,并在宏观新闻预测/财报/专利上演示。为本桶IDF加权词项得分求和族(把词项级权重折叠成篇级测度再入面板回归)提供文本测度构造的方法学前沿存在性。
  - *迁移边界* — 原文语料为英文(新闻/公司filing/专利),走词嵌入+聚类的数据驱动因子,非本项目固定六词典×IDF(log10(N/(1+df)))逐词加权;原文不做银行-年求和聚合,亦无三轨(full/ctx/ss)口径。
  - 〔Crossref 回读标题: Textual Factors: A Scalable, Interpretable, and Data-Driven Approach to Analyzing Unstructured Information〕
  - 〔已接线家族 (3): F127, F349, F625〕
- 【2024–2026】Fernandez-Perez, A., Fuertes, A.-M., Miffre, J., & Zhao, N. (2025). Newswire tone-overlay commodity portfolios. Journal of Banking & Finance, 178, 107501. https://doi.org/10.1016/j.jbankfin.2025.107501
  - *锚定* — 原文用新闻通讯社(newswire)语调叠加构造商品组合信号。为'把逐篇通讯社语调按标的聚合成可交易/可回归的单元级语调量'这一求和聚合口径提供近期存在性。
  - *迁移边界* — Crossref无摘要,claim据题名保守认定;原文为商品期货组合、英文newswire,聚合到商品-期而非银行-年三轨;无IDF/媒体权威/羊群加权层,亦非中文六词典。
  - 〔Crossref 回读标题: Newswire tone-overlay commodity portfolios〕
  - 〔已接线家族 (3): F136, F443, F636〕
- 【2024–2026】Lachana, I., & Schröder, D. (2025). Investor sentiment and stock returns: Wisdom of crowds or power of words? Evidence from Seeking Alpha and Wall Street Journal. Journal of Financial Markets, 74, 100970. https://doi.org/10.1016/j.finmar.2025.100970
  - *锚定* — 原文并列比较Seeking Alpha(众包文本)与《华尔街日报》两类来源的投资者情感对股票收益的作用,直接对置'群体智慧'与'文字力量'两条解释。为本项目把多个情感测度族并列为互为稳健性轨、而非独尊单一来源/单一口径,提供近期比较设计范例。
  - *迁移边界* — Crossref无摘要,claim据题名与副题保守认定为两来源比较设计;原文语料为英文,聚合到股票-期做收益预测,不做银行-年求和;其'power of words'臂的具体词典与加权口径未经核实,不可据此声称原文验证过本项目六词典×IDF/mw/hw的任一加权层。
  - 〔Crossref 回读标题: Investor sentiment and stock returns: Wisdom of crowds or power of words? Evidence from Seeking Alpha and Wall Street Journal〕
  - 〔已接线家族 (1): F191〕
- 【2024–2026】Schmeling, M., & Wagner, C. (2025). Does Central Bank Tone Move Asset Prices? Journal of Financial and Quantitative Analysis, 60(1), 36-67. https://doi.org/10.1017/s0022109024000073
  - *锚定* — 原文构造央行沟通的语调测度,证明语调意外显著推动股价与利率上行、信用利差与波动风险溢价下行,且该效应稳健于对政策行动本身与常规货币政策冲击的控制。为'文本语调作为一个可分离测度、在控制混淆源后仍具增量解释力'提供近期效度证据,支撑本桶语调求和族作为独立测度进入面板。
  - *迁移边界* — 原文文本为央行声明/沟通(机构自身发布),非第三方媒体报道;语调聚合到会议-事件层而非银行-年三轨求和;英文语料,无词典×IDF/媒体权威/羊群加权;F191(跨六词典取均值)在此仅锚'语调测度独立性'的一般前提,非原文做法。
  - 〔Crossref 回读标题: Does Central Bank Tone Move Asset Prices?〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Schweizer, D., Wang, X., Wu, G., & Zhang, A. (2025). Political connections and media bias: Evidence from China. Journal of Corporate Finance, 94, 102835. https://doi.org/10.1016/j.jcorpfin.2025.102835
  - *锚定* — 原文以中国非国有上市公司新闻报道大样本实证: 有政治关联的企业获得显著更正面的媒体报道, 并借 Rule 18 反腐规定强制政治关联董事辞职这一监管冲击做 DiD 确证该因果链; 丑闻期政治关联企业面临更软化的媒体审视, 声誉惩罚被削弱, 进而提高重复违规概率。**本条锚定的是'媒体报道语调在中国并非中性信息镜像、而是可被系统性因素预测地偏移'这一同域前提**, 用以说明本项目不把媒体报道当作等同、无偏的信息载体处理。**须显式声明的限度 (承重)**: 原文实证的异质性维度是**被报道企业**的政治关联属性, **不是媒体来源之间的异质性**; 而 mw 族权重恰按 outlet 逐篇赋权 (media_authority_weight = raw_weight/mean(raw_weight), 由 config/media_weights.json 按媒体名查表得 10–100 量表)。因此**不可据本文声称'媒体来源不同质故须按来源赋权'** —— outlet 级异质性的直接依据须另引 (如 Dewan, Simons & Wernicke 2024 OS 的保守派 vs 非保守派报纸对比)。此外原文未构造任何权重函数, 未做'权重×词典分再求和', 样本为中国上市公司而非银行, 层级为公司而非银行-年三轨。
  - 〔Crossref 回读标题: Political connections and media bias: Evidence from China〕
  - 〔已接线家族 (5): F124, F215, F225, F633, F650〕
- 【2024–2026】Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
  - *锚定* — 原文在中国语境下从新闻报道抽取情感并聚合到企业层面用于债务成本实证, 是「中文新闻情感 → 实体-年测度」应用同域的近期实例。用于锚定本项目正负面篇数/概率和列族的应用语境, 而非其具体算法。原文未做 per-model 多模型并排。
  - *迁移边界* — 原文实体是一般上市公司、DV 是债务成本; 本项目实体是银行、构念是银行金融科技报道情感。原文未区分 count 与 probability-sum 两种口径, 无三模型 per-model 子测度, 无三轨文本范围。
  - 〔Crossref 回读标题: News sentiment and the cost of debt〕
  - 〔已接线家族 (7): F136, F191, F291, F292, F299, F636, F650〕
- 【2024–2026】Wei, L., Wei, M., Wu, Y., & Jing, Z. (2025). Does party organization construction improve chinese banks' stability? Evidence from a new textual index. China Economic Review, 94, 102541. https://doi.org/10.1016/j.chieco.2025.102541
  - *锚定* — 原文构造新的中文文本指数度量中国银行的党组织建设,并接入银行层面面板检验其对银行稳定性的影响。为本项目'中文文本→银行层面指数→银行面板回归'这一整体链路提供应用同域(中国银行×中文文本计量)的近期范例。
  - *迁移边界* — Crossref无摘要,claim据题名保守认定其为'新中文文本指数+中国银行稳定性';原文文本源与指数构造口径未经核实(极可能为银行自身披露文件的主题/关键词计数),**非**六部情感词典净极性经语言学规则后的银行-年求和;DV为银行稳定性,无三轨与四层加权。
  - 〔Crossref 回读标题: Does party organization construction improve chinese banks' stability? Evidence from a new textual index〕
  - 〔已接线家族 (4): F136, F191, F443, F636〕
- 【2024–2026】Ashwin, J. (2024). Financial news media and volatility: Is there more to newspapers than news? Journal of Financial Markets, 69, 100896. https://doi.org/10.1016/j.finmar.2024.100896
  - *锚定* — Ashwin 直接把「报纸报道的数量/篇幅维度」与「报道所含的新信息内容」分离, 检验前者是否对波动率有独立于后者的解释力。本项目 sum_wd_mw_* / sum_wd_vw_* 恰恰是把「报道量按来源权威度或提及密度加权」的分母列与语调分子分离的做法, 该文锚定的正是这一分离的必要性。原文真实做的是文本 + 波动率的实证分解。
  - *迁移边界* — 原文语境为英文报纸与股票波动率, 本项目为中文银行金科报道与银行-年面板; 原文的「报道量」是等权计数或版面维度, 未使用媒体权威度权重或实体提及密度权重; 原文波动率是结果变量, 本项目此列是分母。
  - 〔Crossref 回读标题: Financial news media and volatility: Is there more to newspapers than news?〕
  - 〔已接线家族 (9): F134, F320, F426, F536, F539, F541, F544, F642, F651〕
- 【2024–2026】Aysan, A. F., Caporin, M., & Cepni, O. (2024). Not all words are equal: Sentiment and jumps in the cryptocurrency market. Journal of International Financial Markets, Institutions and Money, 91, 101920. https://doi.org/10.1016/j.intfin.2023.101920
  - *锚定* — 原文以日内跳跃检测配合logistic回归,发现信息发布提高跳跃概率,且局限于情绪类或关涉市场基本面的情感维度比其它维度更易引发跳跃,作者据此提出'words are not all created equal'。为本桶IDF加权族'词典词条不应等权计入,须差异化赋权'的基本前提提供近期实证支持。
  - *迁移边界* — **关键边界**: 原文的'非等权'是**情感维度/类别**层面(情绪 vs 基本面)的差异,而非本项目按语料稀有度的**词项级IDF**加权(raw_idf=log10(N/(1+df)),经均值归一化与P1/P99 Winsorize);二者只在'反对等权'这一动机上相通,函数形式与信息来源完全不同。标的为加密货币日内跳跃、英文新闻,无银行-年求和。
  - 〔Crossref 回读标题: Not all words are equal: Sentiment and jumps in the cryptocurrency market〕
  - 〔已接线家族 (5): F127, F417, F625, F627, F644〕
- 【2024–2026】Dewan, Y., Simons, T., & Wernicke, G. (2024). The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms. Organization Science, 35(5), 1930-1955. https://doi.org/10.1287/orsc.2022.17237
  - *锚定* — 该文实证考察企业 CSR 行为如何影响新闻媒体对该企业的报道 (含报道倾向), 表明媒体报道对企业「良好行为」叙事的呈现受媒体自身意识形态调节。这为本项目「以新闻报道而非企业自述为洗稿率测量载体」提供了媒体报道-企业行为映射非中性的组织理论前沿依据。
  - *迁移边界* — 原文为美国媒体与美国企业 CSR, 观测的是媒体报道量/倾向作为结果变量, 不区分象征性/实质性维度, 亦不构造任何比率型 washing 指标; 本项目将媒体报道作为测量面板, 象征-实质由 LLM 判定, 情境为中国银行业金融科技。该文只锚定「媒体报道非中性」这一前提, 不锚定公式本身。
  - 〔Crossref 回读标题: The Ideological Imperative: Corporate Social Responsibility and News Media Coverage of Firms〕
  - 〔已接线家族 (6): F215, F225, F416, F568, F633, F650〕
- 【2024–2026】Nguyen, M., Samarasinghe, A., & Skully, M. (2024). Watchdogs or Petdogs: The role of media freedom on banking system stability. Pacific-Basin Finance Journal, 87, 102499. https://doi.org/10.1016/j.pacfin.2024.102499
  - *锚定* — 原文以跨国样本实证媒体自由度与银行稳定性在**银行层与系统层**均呈正相关 (稳健于内生性处理), 并识别出**存款人纪律渠道**: 更高的媒体自由度向存款人扩散更多关于金融中介的信息, 激励其约束银行的高风险行为; 该效应在发达国家更强, 而**媒体的国有产权会削弱**这一正向关系。**本条为同域动机性引用, 不作 mw 权重的构造或效度锚定**: 仅用以说明媒体环境对银行侧结果具有系统性影响、且媒体自身属性 (如国有产权) 会调节其信息功能, 因而媒体报道不宜被当作与来源无关的同质噪声处理。**须显式声明的限度 (承重)**: ①原文的媒体维度是**国别层面的媒体自由度指数**, 与本项目**逐篇** media_authority_weight (config/media_weights.json 按媒体名查表得 10–100 量表再除以均值) **既非同一层级也非同一构念**, 不可据本文声称 outlet 级权威性加权已获前沿支持; ②样本为跨国银行体系, 非中国单国银行-年三轨; ③原文不涉及词典情感分, 无任何乘性加权求和层。mw 族按来源赋权的直接依据须另引 outlet 级异质性证据 (如 Dewan, Simons & Wernicke 2024 OS)。
  - 〔Crossref 回读标题: Watchdogs or Petdogs: The role of media freedom on banking system stability〕
  - 〔已接线家族 (3): F225, F633, F650〕


### 十补-3. 语言学规则消融梯度 (否定翻转 / 程度副词 / 转折; exc_* 全 powerset 变体)

> 净增 14 条(其中 2024–2026 者 13 条; **3 条未接入任何家族**, 见各条标注)。**已接线家族** (48): F003, F024, F028, F120, F187, F211, F232, F233, F234, F236, F237, F241, F242, F243, F245, F246, F247, F251, F253, F254, F257, F258, F259, F260, F261, F263, F264, F265, F268, F269, F271, F276, F282, F284, F285, F286, F288, F314, F344, F412, F525, F526, F541, F542, F543, F544, F620, F637

- 【2024–2026】Jang, J., & Wu, X. (2026). Non-English textual analysis with large language models: Analysts’ use of MD&A sentiment in earnings forecasting. Journal of Contemporary Accounting & Economics, 22(1), 100524. https://doi.org/10.1016/j.jcae.2025.100524
  - *锚定* — 该文以韩国上市公司年报 MD&A 为语料, 用大语言模型抽取披露语调 (并论证其对训练数据 look-ahead bias 的缓解), 发现正面语调与分析师盈余预测误差负相关、负面语调与预测误差正相关, 表明分析师仅部分利用 MD&A 文本语调。对本项目的锚定环节 = **非英语公司文本上进行语调测度并检验其信息含量, 是当前会计金融文献的活跃前沿**; 该文置身于'词典法 vs 机器学习/LLM'的方法学脉络 (引 Frankel《ML vs. dictionary methods》、Loughran & McDonald、Tetlock), 支持本项目在中文语料上并排保留词典法与模型法两类语调测度的合理性。⚠ 严格边界与举证缺口: **公开摘要未显示该文实施了词典法基准的并置比较**, 故不得据以主张其'检验了词典法与模型法的信息含量差异'; 在全文确认存在词典法对照臂之前, 本文对**词典规则消融族 (F187/F211/F344/F412/F637) 不构成直接依据**, 宜改挂本项目生成式 LLM 语调族。原文语境为韩语 MD&A, 单位=公司-披露文件, DV=分析师盈余预测误差; 本项目为中文银行金融科技新闻, 单位=银行-年度, 核心是否定/程度/转折三规则的 powerset 消融, 原文并未做规则级消融。
  - 〔Crossref 回读标题: Non-English textual analysis with large language models: Analysts’ use of MD&amp;A sentiment in earnings forecasting〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Pokropek, A. (2026). From keyword-based text measures to latent variables: confirmatory factor analysis with word embeddings. EPJ Data Science, 15(1), 51. https://doi.org/10.1140/epjds/s13688-026-00654-1
  - *锚定* — 该文指出: 词典法文本分析中研究者选定的**关键词**极少像量表题项那样接受心理测量学检验 (罕有报告信度、评估内部结构或检验跨子总体/跨时点的测量不变性)。作者提出把**单个关键词视为同一潜变量的观测指标**, 以词嵌入向量间的中心化余弦相似度矩阵作为输入进行验证性因子分析 (CFA), 从而可估计因子载荷与拟合指数 (CFI/TLI/RMSEA/SRMR)、计算信度系数 (Cronbach's α、Omega)、并以多组模型检验测量不变性。对本项目的锚定环节 = **关键词/词表型文本测度可以且应当被当作构念的观测指标加以显式验证与整合, 而非单一取用**——这一心理测量学立场支持本项目不依赖任何单一词典、而并排多部词典 (F344/F412/F620 等 per-dict 族) 并进一步做跨词典整合 (F187) 的总体设计。⚠ 严格边界: ① **指标层级不同**——原文的观测指标是**一部词表之内的单个关键词**, 整合方式是**基于嵌入余弦相似度的 CFA 载荷估计**; 本项目 dict_avg (F187) 整合的是 **6 个词典级语调得分**, 方式为**等权算术平均、未估计因子载荷**, 故本文**不构成 dict_avg 跨词典等权均值这一具体整合方式的方法学依据**; ② 原文语料为社会科学文本 (以 2022 年俄乌战争的战争焦虑话语为实证示例), 非中文金融新闻; ③ 原文未在规则消融的每一臂上分别整合, 不涉及否定/程度/转折规则。
  - 〔Crossref 回读标题: From keyword-based text measures to latent variables: confirmatory factor analysis with word embeddings〕
  - 〔已接线家族 (4): F187, F344, F412, F620〕
- 【2024–2026】Xiang, L., & Wang, W. (2026). Investor sentiment and stock market returns: A comparative analysis of mood, word, and trade. Journal of Financial Research, jfir.70063. https://doi.org/10.1111/jfir.70063
  - *锚定* — 该文把基于情绪、基于词 (文本词典) 与基于交易的三类投资者情绪测度并排比较其对股票收益的解释力。锚定本项目「同一构念的多个测度并排、互为稳健性、不分主次」这一并排比较范式的前沿存在性。
  - *迁移边界* — 原文并排的是三类异源情绪代理 (心情/文本/交易), 而非同一词典内三条语言学规则的 powerset 消融; DV 为股票市场收益, 单位为市场/股票-时间; 本项目 DV 与单位均不同 (银行-年度面板)。
  - 〔Crossref 回读标题: Investor sentiment and stock market returns: A comparative analysis of mood, word, and trade〕
  - 〔已接线家族 (1): F344〕
- 【2024–2026】Zeng, H., & Amaya, D. (2026). From Words to Embeddings: Text Representation and the Information Content of Financial News. SSRN No. 6695678 [Working Paper]. https://doi.org/10.2139/ssrn.6695678
  - *锚定* — 该工作论文以 135,403 篇道琼斯新闻与五类资产 ETF 的高频收益为样本, 比较关键词匹配 / LDA / LLM 嵌入三种**主题分类**表征所能回收的收益相关信息量 (显著关联极端收益的主题占比自 31.4% 升至 54.1% 再升至 67.8%), 结论为'文本表征方式本身是信息抽取量的经济上重要的决定因素'。对本项目的锚定环节 = **文本表征层的研究者选择具有实质后果**这一一般性命题, 因而本项目对同一语料并行保留词典法与嵌入法两类表征轨、互为稳健性, 是有据的设计选择。⚠ 严格边界: 原文任务为**主题分类**, 全文**不构造任何语调/情感极性测度**, 其 'keyword matching' 指主题关键词归类而非词典情感打分, 故本文**不能**用作'词典法语调轨'的锚点, 更不涉及否定/程度/转折规则子集; 语料为英文金融新闻, 单位为新闻/资产-高频时段, 与本项目中文银行-年度面板不同。工作论文, 未经同行评审。
  - 〔Crossref 回读标题: From Words to Embeddings: Text Representation and the Information Content of Financial News〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
  - *锚定* — 该文指出情感分析在**多主体文本中的情感归属**上存在系统性测量误差 (传统方法易将文本误归于错误公司), 提出以共指消解 (coreference resolution) 作为解决方案, 并通过两项研究证明该处理可降低测量误差、提升文本分析的真实性。对本项目的锚定环节 = **一项具体的语言学处理选择会系统性改变文本测度的取值, 并构成实质性的测量误差来源**这一一般命题, 支持本项目对语言学规则不作默认采纳、而是显式处理其后果的立场。⚠ 严格边界: ① 原文规则是**共指消解 (实体指代还原)**, 与本项目三规则 (否定翻转/程度副词/转折增益) **非同一规则**, 亦非本项目消融梯度的方法学来源; ② 原文立场是**规范性的**——主张**采纳**该规则以减少误差 (存在唯一正确做法), 而本项目令七臂**互为稳健性并排、不设主次**, 二者的方法学取向不同, **不得以本文作为 powerset 规则消融设计的同构先例**; ③ 原文的实体归属问题在本项目中对应的是 ctx/ss 实体窗口轨而非规则消融族; ④ 原文语料为英文组织管理文本, 单位为文档/组织。
  - 〔Crossref 回读标题: Using Coreference Resolution to Mitigate Measurement Error in Text Analysis〕
  - 〔已接线家族 (16): F028, F120, F211, F257, F284, F285, F286, F314, F344, F412, F525, F526, F541, F542, F543, F544〕
- 【2024–2026】Kim, J., Koo, S., & Lim, H. (2025). Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 21445-21482. https://doi.org/10.18653/v1/2025.emnlp-main.1088
  - *锚定* — 该会议论文提出并验证「查询否定盲区」(negation blindness on the query): 当模型对肯定式查询的知识掌握准确时, 其对语义被否定翻转的同一查询仍产出相同或近似回答; 作者以 complexity 与 constrainedness 两准则设计四项验证任务, 系统性证据表明当代大语言模型普遍存在该缺陷。对本项目的锚定环节 = **否定是当代 NLP 系统中一条独立、尚未解决的语义处理轴**这一背景性事实, 为把否定单列为一条可独立开关、独立报告的处理规则提供动机。⚠ 严格边界: 原文为英文 NLP 基准评测, 对象是**生成式大语言模型的知识问答与逻辑推理**, **不涉及情感/语调测度, 不涉及词典或状态机, 不涉及中文否定词表**; 本项目的否定翻转是词典状态机内对否定作用域内命中词确定性改号的显式规则, 其'是否正确处理'不构成问题, 消融臂检验的是该规则对结论的影响。故本文仅作构念层背景动机, **词典法否定处理的直接证据应引 Naldi & Petroni (2023)**。
  - 〔Crossref 回读标题: Semantic Inversion, Identical Replies: Revisiting Negation Blindness in Large Language Models〕
  - 〔已接线家族 (5): F211, F247, F263, F271, F288〕
- 【2024–2026】Pinto, J., & Siano, F. (2025). Beyond words: the challenge of measuring financial text across borders. Journal of International Business Studies, 56(7), 921-936. https://doi.org/10.1057/s41267-025-00798-8
  - *锚定* — 该文 (已正式发表于 Journal of International Business Studies) 把 L&M 式**美国基准词表**直接套用到 **85 个国家、200,960 份财报电话会记录** (文本本身即英文), 发现情感-收益关联对非美国公司**弱约 30%**, 并定谳主因是**文化距离** (语言特征仅作文化价值的工具变量)。对本项目的锚定环节 = 美国基准词表**一旦移出美国语境、即使文本仍是英文**其信号强度亦系统性衰减; 而本项目把 L&M 词表移入中国语境是**既跨文化、又另加中文翻译**, 风险只会更大 —— 这是并置多部**本土**中文词典与多个规则臂的动机之一。⚠ 严格边界: 原文语料全为英文、**无任何词表翻译动作、无非英语语料**, 故**不得**据以声称它直接检验了中文主译词表; 原文亦未做否定/程度/转折的规则级消融, 单位为公司-披露文件。
  - *迁移边界* — 原文语料为 **85 国的英文财报电话会记录** (公司-披露文件层级), 全文**无词表翻译动作、无非英语语料**; 本项目为中文银行金融科技新闻、银行-年度层级, 且核心是否定/程度/转折三规则的 powerset 消融 —— 原文并未做任何规则级消融, 亦未涉及银行-年度聚合。
  - 〔Crossref 回读标题: Beyond words: the challenge of measuring financial text across borders〕
  - 〔已接线家族 (6): F187, F211, F265, F268, F269, F412〕
- 【2024–2026】Qiao, M., & Huang, K.-W. (2025). Correcting Measurement Error in Regression Models with Variables Constructed from Aggregated Output of Data Mining Models. MIS Quarterly, 49(1), 29-60. https://doi.org/10.25300/misq/2024/18026
  - *锚定* — 该文针对「由数据挖掘/分类模型逐条输出再聚合而成的回归自变量」给出测量误差的刻画与校正方法。锚定本项目的聚合结构本身: 文章级得分 (词典状态机或 FinBERT 概率) 先逐篇产出、再在银行-年度内取均值, 正是该文所刻画的「聚合型构造变量」。
  - *迁移边界* — 原文聚焦分类模型输出的聚合与误差校正方法, 语境为信息系统研究; 本项目并未实施该文的校正估计量, 仅把它作为聚合型文本变量存在测量误差这一性质的依据, 且本项目同时含词典状态机 (非数据挖掘模型) 产出的臂。
  - 〔Crossref 回读标题: Correcting Measurement Error in Regression Models with Variables Constructed from Aggregated Output of Data Mining Models〕
  - 〔已接线家族 (2): F253, F254〕
- 【2024–2026】Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
  - *锚定* — 该工作论文以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为。锚定本项目 exc_* 家族公式中「剔除疑似退出覆盖媒体 (ceased_set) 后再做银行-年度聚合」这一环节的现实动机: 媒体退出是真实且有经济后果的样本组成变化。
  - *迁移边界* — 原文是美国本地报纸的真实停刊事件, 停刊判定来自外部事件数据, DV 为本地股票交易活动; 本项目的 ceased_set 是由 detect_defacto_cessation 从语料内部推断出的「疑似退出覆盖」保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 且用途仅为稳健性子样本, 而非识别冲击。工作论文, 未经同行评审。
  - 〔Crossref 回读标题: Newspaper Closures and Trading in Local Stocks〕
  - 〔已接线家族 (21): F232, F233, F234, F236, F241, F242, F243, F245, F246, F251, F257, F258, F259, F260, F261, F264, F269, F276, F282, F284, F286〕
- 【2024–2026】Lin, W., & Liao, L.-C. (2024). Lexicon-based prompt for financial dimensional sentiment analysis. Expert Systems with Applications, 244, 122936. https://doi.org/10.1016/j.eswa.2023.122936
  - *锚定* — 该文把情感词典信息注入提示词 (lexicon-based prompt) 以改进金融维度情感分析, 其方法设计的成立前提是: 词典法携带了生成式模型端未能捕捉的信号, 否则注入词典不会带来增益。这对应本桶「综合词典 − LLM」差值族 (F003 = dict_avg_tone{track} − llm_vote_tone{track}) 的构念依据: 两侧信息不完全重合, 故有向差值携带信息而非纯噪声。⚠ 举证限制: 本条三源均无摘要, 标题仅能证实「词典 + 提示词 + 金融维度情感」, **无法证实原文存在 BERT/判别式模型对照臂**, 故本条**不得**用于锚定任何以 BERT 净语调为被减数的家族 (F002 / F140 / 及其它 *_cater_b 族)。原文的做法是融合两侧以提升准确率, 与本项目保留差值为独立迎合测度的方向相反; 语料为金融文本但非中文银行金科新闻; 情感维度为 valence/arousal 连续维, 与本项目 [-1,1] 归一净语调口径不同; 无 bank-year 面板层级。
  - 〔Crossref 回读标题: Lexicon-based prompt for financial dimensional sentiment analysis〕
  - 〔已接线家族 (1): F003〕
- 【2024–2026】Oh, N. (2024). Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries. Proceedings of the International AAAI Conference on Web and Social Media, 18, 2003-2013. https://doi.org/10.1609/icwsm.v18i1.31443
  - *锚定* — 该文指出情感分析在**可解释性**上的困难, 并明确'依赖专家词表的规则法能提供透明性', 但其应用受制于**资源碎片化与缺乏验证**; 据此构建 sentibank, 将 **15 部原始情感词典与 43 部预处理词典**统一整合入库, 覆盖 7 类体裁与 6 个领域。对本项目的锚定环节有二: ① **规则/词典法作为可解释、透明的情感测度分支, 在当代前沿仍被明确背书**, 支持本项目保留词典状态机语调轨 (F344/F412/F620/F637 等 per-dict 族); ② **同一情感构念下并存大量异源词典**是该领域的既成事实, 与本项目并排 6 部中文词典的做法同构。⚠ 严格边界: 原文的问题意识是资源碎片化与验证缺失, **未主张'不同词典给出不同极性故须并排使用'**, 亦**未做任何跨词典整合/均值运算**, 故**不构成 dict_avg (F187) 等权跨词典均值这一整合方式的方法学依据**; 其覆盖为英文 (社交媒体等体裁), 不含本项目所用中文金融词典 (jiang_2021 / you_2018 / yao_2021 / du_2022 / bian_2021), 也未实现否定/程度/转折三规则状态机, 与规则消融稳健性检验无关。
  - 〔Crossref 回读标题: Sentibank: A Unified Resource of Sentiment Lexicons and Dictionaries〕
  - 〔已接线家族 (6): F187, F282, F344, F412, F620, F637〕
- 【2024–2026】Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
  - *锚定* — 该文实证显示功能词 (含连词一类的非内容词) 在文本类型判别上具有独立的信息量。锚定本项目 avg_adversative 家族的构念前提: 转折/逆接连词占比作为一个与内容词极性无关的独立文体维度, 值得单独计量。
  - *迁移边界* — 原文任务是文本类型分类, 不区分转折连词与其他功能词类, 语料非中文金融新闻, 也不涉及银行-年度聚合; 本项目只取独立转折连词表 (_ADVERSATIVE_WORDS) 命中数除以有效词 token 数, 不做分类任务。
  - 〔Crossref 回读标题: Beyond content: discriminatory power of function words in text type classification〕
  - 〔已接线家族 (10): F024, F232, F236, F241, F243, F245, F257, F259, F276, F282〕
- 【2024–2026】Yoo, M. (2024). How Much Should We Trust Large Language Model-Based Measures for Accounting and Finance Research? SSRN No. 4983334 [Working Paper]. https://doi.org/10.2139/ssrn.4983334
  - *锚定* — 该工作论文就会计与金融研究中由**生成式大语言模型**产出的文本测度, 检讨其可信度与稳定性。对本项目的锚定环节 = **模型产出的文本测度须经独立验证、不可直接当作无误差观测采用**这一一般性方法学告诫; 本项目据此对模型法测度不设唯一 headline, 而令其与词典法测度并排互为稳健性。⚠ 严格边界: 原文论域为**生成式 LLM 测度**, 与本项目 exc_finbert2 / exc_finbert_cn 所用的 **FinBERT 类判别式分类器 softmax 概率**不属同一测度类型, 故本文对该两族**不构成直接依据, 仅为类比性背景**; 原文单位为美国公司披露文本, 本项目为中文银行新闻并在银行-年度层剔除疑似退出覆盖媒体后取均值。工作论文, 未经同行评审, 摘要未能自权威源取得。**建议改挂本项目生成式 LLM 语调族 (B06/B07), 而非词典规则消融族。**
  - 〔Crossref 回读标题: How Much Should We Trust Large Language Model-Based Measures for Accounting and Finance Research?&amp;nbsp;〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
  - *锚定* — 该文提出一套测试集方法, 专门评估词典法情感工具对否定的检测与处理能力, 并实证发现各工具的否定处理表现差异显著。这是本项目 negonly 系列消融臂最贴近的方法学锚点: 否定处理是词典法内部可被单独测量、单独失效的模块。
  - *迁移边界* — 原文为英文、通用领域 (非金融) 的词典工具评测, 用人工构造测试集度量否定检测准确率; 本项目不做否定检测准确率评测, 而是把否定规则开/关作为面板测度的一条稳健性臂, 语料为中文金融新闻。发表年为 2023, 非 2024+ 前沿。
  - 〔Crossref 回读标题: A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools〕
  - 〔已接线家族 (18): F234, F236, F237, F243, F245, F246, F247, F259, F260, F261, F263, F269, F271, F276, F284, F285, F286, F288〕


### 十补-4. 政治词权重敏感性梯度 (du_2022 political_positive ∈ {0.0, 0.5, 1.0})

> 净增 10 条(其中 2024–2026 者 10 条; **3 条未接入任何家族**, 见各条标注)。**已接线家族** (16): F162, F220, F248, F249, F250, F343, F449, F450, F451, F452, F453, F563, F565, F567, F581, F597

- 【2024–2026】Bauckloh, T., & Beyer, V. (2026). Non-standard errors in carbon premia. Journal of Banking & Finance, 189, 107727. https://doi.org/10.1016/j.jbankfin.2026.107727
  - *锚定* — 方法学锚 (前沿存在性): 该文把 non-standard errors 框架迁移到碳溢价这一具体实证问题上, 展示了在单一构念的多种合理构造口径下并排报告结果的做法。为本项目在 du_2022 政治词权重这一构造口径上并排三个取值 (而非只报 0.5) 提供了近期同类实践的存在性证明。原文未涉及文本/情感词典, 亦未主张任一权重为正确值。
  - *迁移边界* — 应用领域为碳溢价资产定价 (国际股票样本), 与中文银行金科新闻语调无重叠; 其构造自由度是碳排放度量与因子设定, 非词典子类权重; 无 bank-year 面板层级, 无停刊媒体排除。
  - 〔Crossref 回读标题: Non-standard errors in carbon premia〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Beltran, A., Guariso, D., & Guerrero, O. A. (2026). Paying the piper: government advertising and media bias. European Political Science Review, 1-20. https://doi.org/10.1017/s175577392610054x
  - *锚定* — 构念旁证 (媒体俘获 → 政治性正面表述内生): Beltran, Guariso & Guerrero (2026, European Political Science Review) 以墨西哥八家主要报纸逾 200,000 篇意见专栏为语料, 用情感分析估计报道的负面语调, 并提出以政府广告投放的过度倾斜度量媒体俘获; 发现被俘获媒体对现任总统的负面程度更低、对其主要政治对手的负面程度更高, 并有黑名单的质性证据佐证。即: 媒体的政治性正面表述可能反映资助/俘获关系而非基本面信息。这为本项目『政治正面词信号弱于普通正面词, 故折算 w_pol<1』提供一条独立的机制性外部依据。原文未构造词典权重, 亦未做任何词类降权。边界: 语境为**墨西哥**单一国家 (非中国, 亦非跨国或欧洲样本——期刊为欧洲刊但研究对象是墨西哥), 与中国党媒-市场化媒体的制度结构不同; 其偏向以专栏负面语调与广告投放倾斜度量, 非词级 political_positive 计数; 无银行层级、无 bank-year 面板、无 du_2022 词典; 原文不涉及媒体停刊/退出, 故不作 exc_* 停刊排除的依据。
  - 〔Crossref 回读标题: Paying the piper: government advertising and media bias〕
  - 〔已接线家族 (3): F220, F248, F249〕
- 【2024–2026】Cha, Y., & Wang, T.-X. (2026). Can firms offset information asymmetry shocks? Evidence from local newspaper closures. Applied Economics Letters, 1-7. https://doi.org/10.1080/13504851.2026.2701294
  - *锚定* — 专锚 exc_* 停刊排除: 该文以地方报纸停刊作为信息环境冲击做实证, 直接证实媒体停刊是一个会改变可观测报道集合与信息含量的真实事件。本项目 exc_* 家族按 _is_ceased_media 排除疑似/确证停刊媒体后重算 bank-year 均值, 正是针对这一现象的样本构成稳健性检验; 该文为「停刊媒体值得单独处理」提供了近期实证依据。原文未做情感语调测度, 也未做排除停刊媒体后重算指标的操作。
  - *迁移边界* — 语境为地方报纸停刊 (非中国, 英文媒体市场), 本项目的 ceased_set 是中文媒体源的疑似/确证停刊判定; 原文把停刊当作外生冲击做因果识别, 本项目只把停刊媒体作为样本排除条件做稳健性并排, 不做因果; 原文 DV 为企业信息不对称指标, 非银行语调均值; 层级为公司-年而非 bank-year。
  - 〔Crossref 回读标题: Can firms offset information asymmetry shocks? Evidence from local newspaper closures〕
  - 〔已接线家族 (3): F248, F249, F250〕
- 【2024–2026】Karagiannis, G. (2026). Alternative weighting schemes for the aggregate Malmquist productivity index: A theoretical and empirical comparison. European Review of Agricultural Economics, 53(1), 214-247. https://doi.org/10.1093/erae/jbaf042
  - *锚定* — 方法学锚 (权重方案并排比较): 该文对同一聚合指数的多种可选加权方案做理论与实证的并排比较, 展示不同权重方案下指数取值的差异及其可比性边界。本项目三权重并排 (且铁律要求各自 just-identified 不混入同一 over-identified 检验) 面对的是同型问题: 同一底层测度在不同加权方案下的多个版本如何并置。原文未涉及情感或文本测度。
  - *迁移边界* — 领域为农业生产率 Malmquist 指数聚合, 与情感词典毫无重叠; 其权重来自经济理论 (产出份额等) 而本项目 w_pol 是研究者选择的信号折算系数; 单位 (生产率指数) 与本项目 (归一化语调 ∈[-1,1]) 不可比; 无 bank-year 层级。
  - 〔Crossref 回读标题: Alternative weighting schemes for the aggregate Malmquist productivity index: A theoretical and empirical comparison〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
  - *锚定* — 应用同域 + 前沿存在性: 该文构造媒体报道的语调测度, 并把它应用于银行融资条件这一银行层级的实证问题, 是「新闻语调 → 银行层级结果」这一链条的近期同域实践。本项目 du_2022 三轨语调 → bank-year 均值的构造与应用域一致。原文未做政治词子类的权重处理。
  - *迁移边界* — 国别为意大利 (意/英文语料), 非中国中文新闻; 其语调测度未使用 du_2022 中文词典, 亦无 political_positive 词类概念; DV 为银行融资条件, 与本项目 P1 funding_cost 相近但口径与数据源不同; 无三轨 (full/ctx/ss) 文本切分, 无停刊媒体排除。
  - 〔Crossref 回读标题: Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy〕
  - 〔已接线家族 (11): F162, F249, F250, F343, F449, F450, F451, F452, F453, F581, F597〕
- 【2024–2026】Malik, T. H., Yu, M., & Hou, J. (2025). A Decade of Evolving Sentiment on the Belt and Road Initiative in Elite Magazines. China & World Economy, 33(4), 155-178. https://doi.org/10.1111/cwe.12600
  - *锚定* — 背景性存在证明 (弱锚, 不作 w_pol 依据): Malik, Yu & Hou (2025, China & World Economy) 对 507 篇发表于 The Economist、Financial Times、Foreign Affairs 与 Economic and Political Weekly 的一带一路报道做情感分析, 发现负面情感主导、财经类与政治类刊物的情感呈系统性分野、且 2013-2023 十年间逐步转负。该文佐证『政治-经济议题的媒体情感可被文本方法长期追踪, 且随媒体类型与时间语境系统性变化』, 为本项目把政治性表述与普通经济表述分列观察提供了一条背景性参照。⚠ 须诚实声明: 原文『政治性』是议题属性而非词级标注, 未做政治词与普通正面词的信号强度比较, 亦未做任何词权重折算, 故**不构成** w_pol<1 或权重阶梯做法的依据; 其语料为英文国际精英杂志、层级为议题-年、情感测度非 du_2022 词典, 与本项目中文银行新闻 bank-year 面板无重叠。
  - 〔Crossref 回读标题: A Decade of Evolving Sentiment on the Belt and Road Initiative in Elite Magazines〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Nguyen, V. D., & Gigliarano, C. (2025). Sensitivity-based weighting method for composite indicators. Annals of Operations Research. https://doi.org/10.1007/s10479-025-06558-z
  - *锚定* — method-origin 邻域 (弱锚, 仅证问题存在): Nguyen & Gigliarano (2025, Annals of OR) 指出复合指标聚合中分量权重的取值『争议众多而少有彻底解法』, 并提出一种由输入对输出方差的贡献比例反推权重的统计方法 (sensitivity-based weights)。本项目 du_2022 score 即一个复合加权指标 (pos_ordinary + w_pol·pos_political 对 neg), w_pol 是研究者设定的分量权重, 该文佐证『复合指标分量权重的设定是公认的、不可随手指定的方法学问题』。⚠ 须诚实声明: 原文的取径是为权重导出**单一有原则的解**, 并未主张枚举离散权重阶梯做稳健性, 与本项目 {0.0,0.5,1.0} 三点并排、不分主次的做法**取径不同**, 故本文只作问题存在性的方法学邻域参照, 不作本项目做法的依据。原文不涉情感词典或新闻文本, 无中国语境、无银行层级、无 bank-year 聚合。
  - 〔Crossref 回读标题: Sensitivity-based weighting method for composite indicators〕
  - 〔已接线家族 (1): F249〕
- 【2024–2026】Merkus, E. (2024). Gravity Models in International Trade: A Specification Curve Analysis. Journal of Industry, Competition and Trade, 24(1), 17. https://doi.org/10.1007/s10842-024-00426-5
  - *锚定* — 方法学锚 (规格曲线在经济学的落地): 该文把规格曲线分析 (specification curve analysis) 用于引力模型, 系统枚举设定选择并展示估计量在整条曲线上的分布, 以判断结论是否被某一设定驱动。本项目「三权重互为稳健性、证明主结论不被 0.5 这一取值驱动」的敏感性检验设计与之同源。原文只做贸易引力模型设定枚举, 未涉及文本测度。
  - *迁移边界* — 应用为国际贸易引力模型 (国家对层级), 与银行-年新闻语调面板层级/单位完全不同; 其枚举维度是控制变量与固定效应设定, 本项目枚举维度是词典内政治词子类的权重标量; 原文是完整规格曲线 (上百设定), 本项目仅 3 点阶梯, 规模不可比。
  - 〔Crossref 回读标题: Gravity Models in International Trade: A Specification Curve Analysis〕
  - 〔已接线家族 (4): F220, F248, F249, F250〕
- 【2024–2026】Soebhag, A., Van Vliet, B., & Verwijmeren, P. (2024). Non-standard errors in asset pricing: Mind your sorts. Journal of Empirical Finance, 78, 101517. https://doi.org/10.1016/j.jempfin.2024.101517
  - *锚定* — 方法学锚 (研究者自由度): Soebhag, Van Vliet & Verwijmeren (2024, JEmpFin) 在资产定价因子模型上自行枚举大量构造路径 (断点选择、是否剔除 microcaps、行业调整、再平衡频率), 实证记录这些可自由取值的设计选择带来的结果离散 (non-standard error 与 standard error 之比平均超过 1), 并主张研究者须清楚交代并论证这些选择。本项目 w_pol∈{0.0,0.5,1.0} 三权重互稳并排、不分主次的做法, 即该主张在词典权重这一自由度上的落地。原文对象为资产定价组合排序选择, 与情感词权重无关, 仅提供『枚举并交代研究者选择而非独断取一』的方法学依据。边界: 原文自由度维度为组合排序/断点/加权等资产定价构造选项, 非情感词典权重; 原文以单一团队枚举上百条构造路径估计 NSE, 本项目仅枚举 3 个权重取值, 不构成 NSE 的完整估计; 国别与数据层级 (美股组合 vs 中国 bank-year) 均不同。
  - 〔Crossref 回读标题: Non-standard errors in asset pricing: Mind your sorts〕
  - 〔已接线家族 (4): F220, F248, F249, F250〕
- 【2024–2026】Yan, L., Ma, Y., Li, C., & Tang, G. (2024). Media abnormal tone and cross section of stock returns: Evidence from China. Accounting & Finance, 64(3), 2671-2698. https://doi.org/10.1111/acfi.13230
  - *锚定* — 应用同域 (中国中文媒体语调): 该文在中国语境下用中文媒体报道构造语调测度并做横截面实证, 是与本项目同语言、同媒体类型的近期语调计量实践。为本项目在中文财经新闻上做词典语调测度提供同域前沿参照。原文未使用政治词子类权重, 亦未做权重梯度。
  - *迁移边界* — 层级为上市公司-股票横截面, 非 bank-year 面板; DV 为股票收益, 与本项目 funding_cost 等银行 DV 不同; 其语调为「异常语调」(相对预期的残差) 口径, 与本项目的幅度归一化 score = Σfinal/Σ|final| 不是同一公式; 无 political_positive 折权, 无停刊媒体排除。
  - 〔Crossref 回读标题: Media abnormal tone and <scp>cross section</scp> of stock returns: Evidence from China〕
  - 〔已接线家族 (5): F220, F248, F563, F565, F567〕


### 十补-5. BERT 三模型 per-model 子测度 (finbert_cn / fin_sent_zh / finbert2)

> 净增 7 条(其中 2024–2026 者 7 条)。**已接线家族** (13): F118, F291, F292, F295, F299, F300, F301, F305, F306, F308, F309, F310, F439

- 【2024–2026】Bennett, B., Ham, C., Milbourn, T., & Wang, Z. (2026). Firm-Level Litigation Risk: Measurement and Effects. Management Science, mnsc.2024.05821. https://doi.org/10.1287/mnsc.2024.05821
  - *锚定* — 原文解析 SEC 10-K 年报构造企业层面诉讼风险的简单透明测度, 以对诉讼发生的预测力确立其效度 (控制企业特征、既有诉讼、地理因素与含企业固定效应后仍显著), 并证明该简单测度的表现与资源密集的 AI 生成测度**相当**, 再将其连结至现金持有、资本支出、研发与并购等政策。本项目据此锚定两点: ①文本派生的实体-年计数型指标可作为面板变量, 且其效度应以对外部结果的预测力而非构造精巧度来论证 (对应 F300 门控计数族的效度论证范式); ②同一构念的简单测度与模型生成测度可表现相当, 支持把测度/模型选择显式化为规格维度并排报告, 而非默认复杂模型更优。原文语料为每公司-年一份的美国英文 10-K, 测度由单份文档解析得到, 不存在多篇文本在实体-期内的聚合步骤, 亦无情感 softmax 概率、无提及密度加权求和 (故不锚 F310)、无 BERT 三模型并排与 LLM 实质性判定门控。
  - 〔Crossref 回读标题: Firm-Level Litigation Risk: Measurement and Effects〕
  - 〔已接线家族 (2): F118, F300〕
- 【2024–2026】Hsu, H.-Y., & Hsu, M.-L. (2026). Semantic stability protocol: intercoder reliability for zero-shot classification via AI coders. Quality & Quantity. https://doi.org/10.1007/s11135-026-02832-9
  - *锚定* — 原文提出 Semantic Stability Protocol, 把同一 LLM 的重复输出视作一组"AI coders", 用传统编码者间信度指标 (Krippendorff's α) 量化并治理零样本分类的**模型内随机性**; 在单模型/单语言/单领域配置下以 DeepSeek Reasoner 对 424 篇**中文新闻**做五分类 (每篇 100 次), 原始输出 α=0.8485, 约 20 次聚合后 α>0.94, 并以 Majority Rate 与 Confidence Gap 两个诊断指标做稳定性分层升级 (高稳定直接采纳、中稳定加跑、低稳定转人工复核)。本项目据此锚定两点: ①把 α/κ 类信度指标施用于 AI 分类器在中文新闻语料上的标注输出, 是方法学上已被接受的效度前置程序; ②多次输出经多数票聚合可显著提升一致性, 呼应本项目 LLM 共识投票的聚合逻辑。原文为**单模型内**的重复运行稳定性 (其"AI coders"即同一模型的多次跑), **未做任何跨模型比较**, 故不构成本项目「多个 BERT 模型间一致性作为效度证据」这一模型间维度的直接先例; 其对象为零样本生成式 LLM 而非微调 BERT (本项目各模型分类基数还存在 2 vs 3 分类差异), 且全程为标签级信度, 不涉及概率均值/概率和口径 (故不锚 F295)、无金融构念与面板聚合。
  - 〔Crossref 回读标题: Semantic stability protocol: intercoder reliability for zero-shot classification via AI coders〕
  - 〔已接线家族 (3): F118, F291, F299〕
- 【2024–2026】Hirshleifer, D., Mai, D., & Pukthuanthong, K. (2025). War Discourse and the Cross Section of Expected Stock Returns. The Journal of Finance, 80(6), 3589-3637. https://doi.org/10.1111/jofi.13482
  - *锚定* — 原文用半监督主题模型对 700 万篇《纽约时报》报道 (跨 160 年) 抽取话语主题, 逐篇得到战争话语强度并据此构造战争因子解释预期收益截面, 是「篇级文本强度 → 汇总为可用于资产定价检验的文本暴露量」这一构造范式的顶刊实例。本项目仅据此锚定 F310 提及密度加权暴露列族的一般合法性: 篇级文本信号按强度 (而非等权计数) 加总为单元暴露量, 在前沿有先例。原文测度的是战争话语主题暴露 (topic exposure), 无情感极性与分类概率输出, 故不为本项目任何概率和列族 (F292/F301) 提供依据; 其定价检验走因子模拟组合、聚合层级为市场/组合而非银行-年, 语料为美国英文新闻, 亦无 per-model 并排与三轨文本切分。
  - 〔Crossref 回读标题: War Discourse and the Cross Section of Expected Stock Returns〕
  - 〔已接线家族 (3): F305, F308, F310〕
- 【2024–2026】Zhu, D., Wang, X., & Zhang, Y. (2025). Narrative monetary policy expectation in China. China Economic Review, 94, 102568. https://doi.org/10.1016/j.chieco.2025.102568
  - *锚定* — 原文对逾 100 万篇中文经济新闻做语义分析, 构造中国叙事型货币政策预期指数, 并证明其与宏观/微观调查类预期指标一致 (同时具备更高频率、时效与更低成本), 再以 TVP-VAR 检验其与产出/物价的动态关系。本项目仅据此锚定一条语境级事实: 在中文文本上构造计量化的文本测度、并以外部指标做收敛效度检验, 在近期国际期刊上是既有存在且被接受的做法, 支撑本项目在中文银行新闻上构造篇数/概率类测度的可接受性。原文层级为宏观货币政策叙事、测度对象是政策方向预期而非情感极性概率, 未设中性/无立场档, 未使用 BERT 或多模型并排, 无 per-model 分母、无计数/概率双口径与加权暴露列族; 原文不为本项目中性概率族 (F295) 提供任何依据。
  - 〔Crossref 回读标题: Narrative monetary policy expectation in China〕
  - 〔已接线家族 (1): F291〕
- 【2024–2026】Dechow, P., Lawrence, A., Luo, M., & Stamenov, V. (2024). Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics. Management Science, 70(8), 5157-5186. https://doi.org/10.1287/mnsc.2021.02218
  - *锚定* — 该文检视五届夏季奥运会,识别被媒体炒作为奥运受益的概念股,发现其在奥运周期内收益更高、彼此共动更强,并在媒体有报道关联该公司的交易日出现成交量与波动率上升。锚「涉及某主体的媒体报道量是可独立测量的注意力/曝光度构念、且会驱动市场后果」在中国情境下的前沿存在性,作为 media_breadth 计数基座的参照。⚠ 原文以报道篇数/媒体炒作刻画关注,**未见去重来源媒体家数(nunique outlet)计数**,故不锚 n_outlets 的 extensive-margin 口径;亦无 ln(1+·) 与逐年度截面 z 标准化(n>=3 门槛),不涉及 Fintech/Non-Fintech 补集分层。
  - 〔Crossref 回读标题: Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics〕
  - 〔已接线家族 (3): F306, F309, F439〕
- 【2024–2026】Groß-Klußmann, A. (2024). Learning deep news sentiment representations for macro-finance. Digital Finance, 6(3), 341-377. https://doi.org/10.1007/s42521-024-00107-2
  - *锚定* — 原文对海量新闻分析数据中已有的、跨多个主题的**文本情感时间序列**做潜在经济因子抽取, 用监督式自编码器学习其低维表征, 并在 GDP nowcasting、资产类别收益面板解释与时序动量三个宏观金融应用上证明其优于 PCA/PLS 等线性降维。本项目仅据此取一条弱锚定: 以**连续取值**的情感信号 (而非硬标签) 作为进入宏观/金融实证的文本量, 在前沿是常规做法, 佐证本项目保留篇级概率而非仅用 argmax 标签的口径 (F292/F301) 之合理性。原文的神经模型作用于**已聚合的情感时间序列**做降维, 并不产出篇级情感、也不存在篇级信号在单元内的聚合步骤, 其"表征"是压缩后的潜因子而非 BERT 三分类 softmax 概率; 语料为英文新闻、层级为宏观时序而非中文银行-年面板, 无中性档处理 (故不锚 F295)、无 per-model 独立分母、无三轨与 hw/mw 加权。
  - 〔Crossref 回读标题: Learning deep news sentiment representations for macro-finance〕
  - 〔已接线家族 (3): F292, F301, F305〕
- 【2024–2026】Ke, S., Montiel Olea, J. L., & Nesbit, J. (2024). Robust machine learning algorithms for text analysis. Quantitative Economics, 15(4), 939-970. https://doi.org/10.3982/qe1825
  - *锚定* — 原文证明 LDA 的参数不可识别, 因而文本派生量的后验结论会随先验设定改变, 并给出刻画该结论取值区间的算法。本项目据此仅取一条一般性方法论立场: 文本测度的下游结论可能被建模者未被数据识别的选择所驱动, 故应把这类选择显式化并报告结论在其上的取值范围, 而非只报一个点估计——对应本项目把模型选择视为规格维度、三个 BERT 各自 just-identified 并排的做法。原文研究的是单一 LDA 模型内的**先验**敏感性与不可识别性, 不是不同分类器之间的模型选择问题, 未评估任何 BERT 或神经情感分类器, 亦未涉及计数/概率和口径、金融情感构念与中文语料; 原文不是本项目 per-model 并排的 method-origin。
  - 〔Crossref 回读标题: Robust machine learning algorithms for text analysis〕
  - 〔已接线家族 (5): F291, F292, F295, F299, F301〕


### 十补-6. LLM 三家投票共识 / 概率打分 / 置信度与阈值梯子

> 净增 15 条(其中 2024–2026 者 12 条)。**已接线家族** (36): F032, F035, F042, F047, F174, F367, F369, F374, F375, F376, F377, F378, F379, F381, F383, F384, F385, F386, F387, F388, F390, F391, F392, F393, F394, F395, F396, F397, F399, F400, F401, F402, F404, F405, F406, F429

- 【2024–2026】Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
  - *锚定* — 原文利用集成学习器内部各成员预测之间的差异构造工具变量, 以缓解 ML 生成变量作为回归元时的测量误差偏误。与本项目'多个异构模型对同一篇文章各自打分、成员间存在系统性差异'的结构同构, 对下游用这些聚合量做回归提供了一条已发表的处理路径。
  - *迁移边界* — 原文的集成成员是同一训练流程下的 ML 预测器 (树/神经网络等), 其成员差异有明确的重采样来源; 本项目的成员是三家不同厂商的闭源 LLM, 差异来源不可控且不可重采样, 原文构造 IV 的前提未必成立。本项目未实施 EnsembleIV, 亦不得将该文用于混入本项目的 over-identified Hansen J (与桶内 co-equal 并排铁律冲突)。
  - 〔Crossref 回读标题: EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables〕
  - 〔已接线家族 (6): F367, F369, F390, F396, F397, F405〕
- 【2024–2026】Abraham, L., Arnal, C., & Marie, A. (2025). Prompt selection matters: enhancing text annotations for social sciences with large language models. Journal of Computational Social Science, 8(3), 73. https://doi.org/10.1007/s42001-025-00388-6
  - *锚定* — 原文实证表明 prompt 选择对社科文本标注质量有显著且非平凡的影响, 并给出一套 prompt 选择/评估流程。是'LLM 标注结果对 prompt 敏感、须固定并披露'这一事实的实证依据, 对应本项目单一冻结 prompt (v8) 下产出的全部 LLM 类目/语调列。
  - *迁移边界* — 原文语料为英文社科文本, 且其核心贡献是遍历 prompt 网格择优; 本项目 prompt v8 已字节级冻结并作为缓存键, 刻意不做 prompt 网格 (改 prompt 即全缓存作废), 故原文提示的 prompt 敏感性在本项目属未量化的已知局限, 而非已排除的风险。
  - 〔Crossref 回读标题: Prompt selection matters: enhancing text annotations for social sciences with large language models〕
  - 〔已接线家族 (6): F032, F047, F399, F400, F402, F405〕
- 【2024–2026】Gligoric, K., Zrnic, T., Lee, C., Candes, E., & Jurafsky, D. (2025). Can Unconfident LLM Annotations Be Used for Confident Conclusions? Proceedings of the 2025 Conference of the Nations of the Americas Chapter of the Association for Computational Linguistics: Human Language Technologies (Volume 1: Long Papers), 3514-3533. https://doi.org/10.18653/v1/2025.naacl-long.179
  - *锚定* — 原文提出 confidence-driven inference: 用 LLM 自报置信度决定哪些样本值得付费人工复标, 并给出统计有效的点估计与置信区间, 实证证明低置信 LLM 标注在恰当处理下仍可支撑可信结论。是'把逐篇 LLM 置信度当作可用统计信息而非丢弃'这一做法的前沿存在性与方法依据, 对应本项目以 confidence 驱动的 avg_category_confidence / avg_icm_confidence 与 low_conf_flag 低置信标记。
  - *迁移边界* — 原文场景为社科调查/标注数据集且必须配套人工标注子样本作为 ground truth 来实现有效推断; 本项目无人工标注回路, 置信度仅用于打分与阈值标记, 未实施该文的抽样-推断设计。原文单模型置信度, 本项目 confidence 经三家投票一致/分歧调整 (一致 → min(kw_conf+0.2,1.0); 分歧 → kw_conf×0.5), 与原文口径不同。
  - 〔Crossref 回读标题: Can Unconfident LLM Annotations Be Used for Confident Conclusions?〕
  - 〔已接线家族 (5): F032, F047, F375, F378, F429〕
- 【2024–2026】Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C. (2025). Calibrating Large Language Models with Sample Consistency. Proceedings of the AAAI Conference on Artificial Intelligence, 39(18), 19260-19268. https://doi.org/10.1609/aaai.v39i18.34120
  - *锚定* — 原文系统比较多种置信度来源, 实证表明由多次采样输出之间的一致性 (consistency) 导出的置信度, 在校准性上优于模型自报置信度与 logit 概率。这是'用一致率而非自报分数作为连续置信权重'的直接方法学依据, 对应本项目 llm_vote_cont{track} = llm_vote_score{track} × llm_agreement_rate{track} 的连续化构造。
  - *迁移边界* — 原文的一致性来自同一模型在正温度下多次重复采样; 本项目 temperature=0.0 且不重复采样, agreement_rate 来自三家不同厂商模型 (gpt54nano/gemini31/deepseekv4) 的跨模型投票一致率 ∈[1/3,1], 是跨模型而非跨采样的一致性, 校准性质未被原文覆盖。原文任务为英文推理/QA 基准, 非中文新闻三分类情感, 且不涉及 herd/media 加权与 bank-year 面板求和。
  - 〔Crossref 回读标题: Calibrating Large Language Models with Sample Consistency〕
  - 〔已接线家族 (7): F383, F384, F385, F386, F387, F388, F390〕
- 【2024–2026】Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
  - *锚定* — 原文以 few-shot prompt 在多项政治学文本即数据任务 (情感分析、文档标度、主题建模) 上做预注册评估, 结论是该做法优于传统有监督学习基线、并以极低成本达到与专家及众包编码员**相当** (comparable, 非超过) 的水平, 同时给出社科测量任务的 prompt 适配最佳实践与开源软件包。是'用 LLM 直接产出文本级类目/语调标签再逐单元聚合'这一测量范式在社会科学中的同族方法学先例, 支撑本项目 llm_vote_tone_sum / llm_vote_tone_collab / per-model pos_count 的标签→聚合链路; 不构成对本项目置信度构造 (avg_category_confidence / avg_icm_confidence) 的任何依据。
  - 〔Crossref 回读标题: How to train your stochastic parrot: large language models for political texts〕
  - 〔已接线家族 (8): F174, F393, F394, F395, F399, F400, F402, F405〕
- 【2024–2026】Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
  - *锚定* — 原文以排序投票 (ranked voting) 取代朴素多数票来聚合 LLM 的多个候选输出, 并实证其聚合质量提升。属于'多数票聚合并非唯一选择、投票规则本身是设计自由度'的前沿存在性证明, 对应本项目 llm_vote_score{track} ∈ {-1,0,1} 三家多数票及其 bank-year 求和族。
  - *迁移边界* — 原文的投票单元是同一模型多次采样得到的候选答案 (self-consistency), 而非跨三家厂商模型的标签投票; 任务为推理/生成而非三分类情感标签; 原文只到文章/样本级聚合, 不涉及本项目的 bank-year 分组求和、herd/media/mention_density 加权分子, 也未采纳排序投票 (本项目仍为朴素多数票)。
  - 〔Crossref 回读标题: Ranked Voting based Self-Consistency of Large Language Models〕
  - 〔已接线家族 (9): F383, F391, F392, F393, F394, F395, F396, F399, F405〕
- 【2024–2026】Wen, B., Yao, J., Feng, S., Xu, C., Tsvetkov, Y., Howe, B., & Wang, L. L. (2025). Know Your Limits: A Survey of Abstention in Large Language Models. Transactions of the Association for Computational Linguistics, 13, 529-556. https://doi.org/10.1162/tacl_a_00754
  - *锚定* — 原文是 LLM 弃答 (abstention) 研究的系统性综述, 从 query / model / human values 三视角组织弃答方法、基准与评估指标。本项目并不实施弃答: low_conf_flag = 1{avg_category_confidence < 0.5} 系在面板导出层对事后置信度取固定阈值的哑变量, 模型始终作答。故该文仅作为'低置信输出应被显式识别与特殊处理而非静默采纳'这一一般性思路的背景综述参考, **不是** low_conf_flag 做法的方法学出处, 阈值 0.5 亦为研究者选择而非原文推荐值。
  - 〔Crossref 回读标题: Know Your Limits: A Survey of Abstention in Large Language Models〕
  - 〔已接线家族 (1): F429〕
- 【2024–2026】Kim, A., Muhn, M., & Nikolaev, V. (2024). Financial Statement Analysis with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2407.17866
  - *锚定* — 原文向 GPT-4 提供标准化且匿名的财务报表 (刻意剥离叙事与行业信息), 令其判断企业未来盈余的**变动方向**, 实证其方向性预测准确率超过人类分析师、与窄训练的 SOTA 机器学习模型相当, 且基于 GPT 预测构建的交易策略取得更高 Sharpe 比率与 alpha。是'令 LLM 对企业作离散方向性判断、再把该判断当作可交易信号并聚合'这一范式在金融领域的前沿存在性证明, 与本项目由 LLM 离散标签聚合出 bank-year 语调量的链路同族。**边界**: 原文输入为报表数字而非中文新闻叙事, 单位为公司-季度盈余方向而非银行-年语调, 采用单一 GPT-4 无跨厂商投票; 摘要未载其自报置信度的使用, 故**不得**据此为本项目 (label, confidence) → llm_prob_score 的最大熵均分式 logit-to-score 映射背书 — 该映射系研究者选择, 其金融领域先例须另行举证。
  - 〔DataCite 回读标题: Financial Statement Analysis with Large Language Models〕
  - 〔已接线家族 (7): F375, F378, F393, F394, F395, F400, F405〕
- 【2024–2026】Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
  - *锚定* — 原文评估 LLM 对'针对特定目标实体'的情感 (entity-level / targeted sentiment) 的标注质量并与人工标注对比。本项目的情感构念正是'针对目标银行'的实体级语调而非篇章整体语调, 该文是这一构念下 LLM 标注可行性的同族实证。
  - *迁移边界* — 原文语料为挪威语/英语通用新闻与评论, 目标实体非银行; 采用单一 GPT 模型, 无三家投票、无置信度概率化; 只报告标注一致性, 不做 bank-year 面板聚合、加权分子构造或三轨 (full/ctx/ss) 文本切分。
  - 〔Crossref 回读标题: A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation〕
  - 〔已接线家族 (9): F174, F369, F392, F393, F394, F395, F400, F402, F405〕
- 【2024–2026】Törnberg, P. (2024). Best Practices for Text Annotation with Large Language Models. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2402.05129
  - *锚定* — 原文提出 LLM 文本标注的操作规范, 涵盖 prompt 设计、可复现性 (温度/版本固定)、可靠性与效度的报告要求。是本项目 prompt v8 字节级冻结 + temperature=0.0 + 缓存可复现这一工程口径的同族规范性依据。
  - *迁移边界* — 原文为立场/指南性文章, 不含实证基准也不含金融面板应用; 其建议面向单模型标注流程, 未涉及三家跨厂商投票、置信度概率化与三轨文本切分。本项目遵循其可复现性建议属独立工程选择, 非原文验证过的配置。
  - 〔DataCite 回读标题: Best Practices for Text Annotation with Large Language Models〕
  - 〔已接线家族 (2): F032, F047〕
- 【2024–2026】Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J. (2024). Mixture-of-Agents Enhances Large Language Model Capabilities. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2406.04692
  - *锚定* — 原文实证聚合多个异构 LLM 的输出优于任何单一模型, 并刻画了'模型间协作性'。是本项目采用三家异构厂商模型并对其子测度取跨模型均值/投票这一架构的前沿存在性依据, 对应 llm_models_avg_cont_sum / llm_models_avg_tone_sum 的跨模型算术均值与 per-model pos_count 并排。
  - *迁移边界* — 原文的聚合是分层生成式的 (后层模型读取前层模型的完整回答再合成), 与本项目对离散标签取多数票、对连续分取算术均值的机械聚合是不同机制; 评测在英文指令跟随基准 (AlpacaEval 等), 非中文银行金科新闻情感; 原文未讨论 per-model 独立降级与 _safe_mean 缺列 NaN 语义。
  - 〔DataCite 回读标题: Mixture-of-Agents Enhances Large Language Model Capabilities〕
  - 〔已接线家族 (3): F174, F367, F369〕
- 【2024–2026】Zhang, M., Huang, M., Shi, R., Guo, L., Peng, C., Yan, P., Zhou, Y., & Qiu, X. (2024). Calibrating the Confidence of Large Language Models by Eliciting Fidelity. Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, 2959-2979. https://doi.org/10.18653/v1/2024.emnlp-main.173
  - *锚定* — 原文把语言模型置信度分解为对问题的不确定性 (Uncertainty) 与对自身所生成答案的保真度 (Fidelity), 提出 UF Calibration 并在 6 个 RLHF-LM × 4 个 MCQA 数据集上验证, 另提出 IPR/CE 两个校准评价指标。对 F035/F042 的锚定仅限「LLM 置信度可被分解并校准」这一方法学存在性; 原文的置信度由 UF 分解估计得到, **非**自报置信度, 且其是否适用于仅可访问输出的黑箱 API 场景原文未作声明, 不得据此宣称与本项目生产约束一致。本项目未实施该校准算子, 现口径仍为原始自报值取均值。
  - 〔Crossref 回读标题: Calibrating the Confidence of Large Language Models by Eliciting Fidelity〕
  - 〔已接线家族 (3): F047, F374, F375〕
- Tian, K., Mitchell, E., Zhou, A., Sharma, A., Rafailov, R., Yao, H., Finn, C., & Manning, C. (2023). Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback. Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing, 5433-5442. https://doi.org/10.18653/v1/2023.emnlp-main.330
  - *锚定* — method-origin: 原文证明对经 RLHF 微调的模型, 直接用自然语言索要口头概率所得的置信度, 比模型内部 logit 条件概率更为校准。这正是本项目在 RLHF 类商用模型上以 prompt 索取 confidence 字段、并将其当作概率量送入 logit-to-score 的做法所依据的实证结论。
  - *迁移边界* — 原文在英文事实型 QA 数据集上度量 ECE, 模型为 2023 年的 GPT-3.5/GPT-4 代次; 本项目为中文新闻情感三分类与创新维度分类, 未在本项目语料上复测 ECE, 亦未验证该校准优势能否迁移到 deepseekv4/gemini31 两家非 OpenAI 模型。原文不涉及跨模型投票、herd/media 加权求和与面板聚合。
  - 〔Crossref 回读标题: Just Ask for Calibration: Strategies for Eliciting Calibrated Confidence Scores from Language Models Fine-Tuned with Human Feedback〕
  - 〔已接线家族 (7): F374, F375, F376, F378, F401, F404, F406〕
- Xiong, M., Hu, Z., Lu, X., Li, Y., Fu, J., He, J., & Hooi, B. (2023). Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2306.13063
  - *锚定* — 该文是黑箱场景下「直接向 LLM 索取自报置信度」这一 elicitation 范式的奠基性系统评测, 建立了 verbalize-based confidence 的基准协议并记录了模型普遍过度自信。作为 2023 年方法原点收录, 用于交代 F035/F042 的 conf 列取数方式来自何处; 该文为 arXiv 预印本 (后发表于 ICLR 2024), 此处按回读结果如实标注。
  - *迁移边界* — 2023 年成果, 早于本桶 2024-2026 优先窗口, 仅作 method-origin 收录; 评测对象为当时的 GPT/LLaMA 系模型, 不含本项目的 deepseekv4/gemini31; 任务为英文常识与算术推理, 非中文金融情感; 无面板聚合。
  - 〔DataCite 回读标题: Can LLMs Express Their Uncertainty? An Empirical Evaluation of Confidence Elicitation in LLMs〕
  - 〔已接线家族 (5): F035, F042, F047, F374, F375〕
- Kadavath, S., Conerly, T., Askell, A., Henighan, T., Drain, D., Perez, E., Schiefer, N., Hatfield-Dodds, Z., DasSarma, N., Tran-Johnson, E., Johnston, S., El-Showk, S., Jones, A., Elhage, N., Hume, T., Chen, A., Bai, Y., Bowman, S., Fort, S., ... Kaplan, J. (2022). Language Models (Mostly) Know What They Know. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2207.05221
  - *锚定* — 原文系统研究语言模型能否自评其答案的正确性: 证明较大模型在格式恰当的多选/判断题上校准良好, 并据此提出让模型先给答案再自评 'P(True)' 的自评范式, 报告其在多类任务上的性能、校准与规模效应, 另研究无需特定候选答案的 'P(IK)' 预测。是'LLM 自评概率携带真实信息、具备一定校准性'这一前提的**早期奠基性证据**, 为本项目把 LLM 输出的 confidence 当作概率量送入 compute_prob_score / compute_prob_score_binary 提供一般性支持。**边界**: 该文并非本项目做法的方法出处 — 原文自评经由专门的 P(True)/P(IK) 探针与 logit 读数, 本项目 confidence 来自 prompt 结构化输出字段 (verbalized confidence 一线, 见 Xiong et al. 2023 / Tian et al. 2023); 模型代次为 2022 年 Anthropic 内部模型, 与本项目 2026 年三家生产模型不可比; 原文亦未提出把剩余概率 (1-confidence) 在非主类间按最大熵均分再作差 (P正−P负) 的映射 — 该映射是研究者选择, 非原文成果。
  - 〔DataCite 回读标题: Language Models (Mostly) Know What They Know〕
  - 〔已接线家族 (7): F374, F375, F376, F377, F378, F379, F381〕


### 十补-7. LLM per-model 跨厂商稳健性 (gpt54nano / gemini31 / deepseekv4)

> 净增 12 条(其中 2024–2026 者 12 条; **5 条未接入任何家族**, 见各条标注)。**已接线家族** (5): F035, F042, F204, F474, F524

- 【2024–2026】Bie, S., Feng, G., Guo, N., & He, J. (2026). One News, Two Markets: LLM-Derived Sentiment and Trading Volume. SSRN No. 5994158 [Working Paper]. https://doi.org/10.2139/ssrn.5994158
  - *锚定* — 原文用大型语言模型 (DeepSeek) 从 Dow Jones Newswires (2002-2023) 中提取资产特定的新闻情感强度, 证明该情感强度是异常成交量的稳健预测因子, 并刻画同一公司新闻在权益与公司债两个市场上的异质交易反应 (一标准差新闻幅度使次日成交量冲击债券 +17%、股票 +29%; 债券侧冲击对权益的影响即时而短暂, 权益侧冲击则在流动性较差的债市引发持续交易)。对 F204 仅作**弱的同域背景锚定**: 「新闻文本的 LLM 情感可在实体层聚合并具有可观测的异质后果」; 原文的 'two markets' 指两类资产市场而非解读上的分歧, 未构造任何分歧指数, 故不支持「同一新闻诱发分歧解读」的经验主张。边界: 未经同行评审的 SSRN 工作论文; 语料为英文财经通讯稿, 层级为资产-日, 本项目为中文报纸银行报道的银行-年面板。
  - 〔Crossref 回读标题: One News, Two Markets: LLM-Derived Sentiment and Trading Volume〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Liu, J. (2026). Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation. Computers in Human Behavior, 181, 108988. https://doi.org/10.1016/j.chb.2026.108988
  - *锚定* — 原文以固定 rubric 提示单一模型 (gpt-4o-mini) 重标注 HateXplain 仇恨言论语料, 检验 LLM 标注与人类众包标注的一致性、模型返回的类别概率向量的熵与人类标注分歧的关系, 以及 LLM 标签作为下游分类器监督信号的效果。对 F035/F042 的锚定仅限「在**主观标注**任务 (与情感判定同类) 中, 模型自我报告的把握度可被度量, 且在人类标注分歧较大处系统性更高」这一层; 原文的不确定性载体是类别概率向量的 Shannon 熵而非标量自报置信度, 且全程只用一个模型、不涉及跨厂商比较, 故不支持本项目 per-model 并排口径; 语料为英文社交媒体仇恨言论, 非中文金融新闻, 亦无实体-年聚合。
  - 〔Crossref 回读标题: Rubric-conditioned large language model labeling: Agreement, uncertainty, and label consistency in subjective text annotation〕
  - 〔已接线家族 (4): F035, F042, F474, F524〕
- 【2024–2026】Ulmer, D., Lorson, A., Titov, I., & Hardmeier, C. (2026). Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing. Transactions of the Association for Computational Linguistics, 14, 1505-1540. https://doi.org/10.1162/tacl.a.739
  - *锚定* — 原文系统综述人类不确定性沟通研究与 NLP 中的 verbalized uncertainty 研究, 主张 anthropomimetic uncertainty (可信的不确定性沟通须模仿人类语言行为), 并补充分析实证了 verbalized uncertainty 中若干此前未被充分探讨的**偏倚**。对 F035/F042, 可用的锚定仅限「自报不确定性本身带有系统性偏倚」这一实证层; 原文关注的是面向人类用户的沟通质量与可信度, 未针对把自报置信度当作研究变量的测量效度问题, 亦未提出可替换本项目 conf 列的算子。
  - 〔Crossref 回读标题: Anthropomimetic Uncertainty: What Verbalized Uncertainty in Language Models is Missing〕
  - 〔已接线家族 (2): F035, F042〕
- 【2024–2026】Wang, Z., & Zhang, H. (2026). Large Language Models, Investor Disagreement, and Trading Volume. SSRN No. 6307940 [Working Paper]. https://doi.org/10.2139/ssrn.6307940
  - *锚定* — 工作论文, 用 LLM 从文本中构造投资者分歧代理并检验其与交易量的关系。对 F204 的锚定是前沿存在性: 证明「以 LLM 情感标签构造分歧指数」在 2026 年的金融文献中已是活跃做法。该文并未使用 F204 的 sqrt(1-((P-N)/(P+N))^2) 具体函数形式, 也未涉及银行层面板。
  - *迁移边界* — SSRN 工作论文, 未经同行评审; 分歧的文本来源与构造式与本项目不同 (本项目为报纸新闻的 gemini31 正负篇数); DV 为交易量, 本项目 F204 为面板解释/稳健性变量, 层级为银行-年而非股票-日。
  - 〔Crossref 回读标题: Large Language Models, Investor Disagreement, and Trading Volume〕
  - 〔已接线家族 (1): F204〕
- 【2024–2026】Yi, K., & Wu, F. (2026). What Investors Disagree About: LLM-Decomposed Retail Disagreement and the Cross-Section of Stock Returns. SSRN No. 7027983 [Working Paper]. https://doi.org/10.2139/ssrn.7027983
  - *锚定* — 原文用大型语言模型阅读中国最大股票论坛的 2.2 亿条散户发帖, 按内容把投资者分歧分解为基本面分歧与噪声分歧: 基本面分歧产生 Miller 型高估 (高分歧股月度风险调整收益低约 0.7%), 噪声分歧则不然而更多反映情绪; 加总的与词典法的分歧指标因与情绪高度绑定而会把两类相反内容混同、甚至指向错误方向。对 F204 锚定「LLM 标签可承载分歧信息」及「加总分歧指标混同异质内容」的前沿实证。**边界**: 系未经同行评审的 SSRN 工作论文; 语料同为中文投资者文本但来源为散户股票论坛发帖, 与本项目的报纸银行报道体裁不同; 分析层级为股票-横截面收益 (2016-2024), 本项目为银行-年面板; 该文按内容分解分歧, 而 F204 仅以正负篇数比构造标量指数并约定 P+N=0 置 NaN, 原文无此处理。
  - 〔Crossref 回读标题: What Investors Disagree About: LLM-Decomposed Retail Disagreement and the Cross-Section of Stock Returns〕
  - 〔已接线家族 (1): F204〕
- 【2024–2026】Liu, J., Zong, Q., Wang, W., & Song, Y. (2025). Revisiting Epistemic Markers in Confidence Estimation: Can Markers Accurately Reflect Large Language Models’ Uncertainty? Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), 206-221. https://doi.org/10.18653/v1/2025.acl-short.18
  - *锚定* — 原文定义 marker confidence (模型使用某认知标记时的观测准确率), 在多个问答数据集上检验其稳定性, 发现认知标记在分布内泛化良好、在分布外则与真实不确定性对应不稳。对 F035/F042 的锚定仅为**类比层**: 它提示 LLM 自我表达的把握度其可靠性具有领域依赖性: 但原文的置信度载体是认知标记词, 明确与数值型置信度相对立, 故该结论**不能**直接外推至本项目的 [0,1] 数值 conf 列, 亦未在中文金融文本上检验。
  - 〔Crossref 回读标题: Revisiting Epistemic Markers in Confidence Estimation: Can Markers Accurately Reflect Large Language Models’ Uncertainty?〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Liu, X., Chen, T., Da, L., Chen, C., Lin, Z., & Wei, H. (2025). Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2, 6107-6117. https://doi.org/10.1145/3711896.3736569
  - *锚定* — KDD 2025 综述, 系统归类 LLM 不确定性量化与置信度校准的方法谱系 (含 verbalized confidence 一支) 及其评测协议。对 F035/F042 是定位性锚点: 用于在文中说明本项目所取的自报置信度属于该谱系中的哪一类, 以及该类方法已知的局限。综述本身不含任何银行/新闻实证。
  - *迁移边界* — 综述性文献, 不提供针对具体测度的实证结论; 覆盖领域以通用 NLP 任务为主, 不含中文金融新闻语境, 也不涉及把置信度聚合到实体-年面板的做法。
  - 〔Crossref 回读标题: Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Ni, S., Bi, K., Yu, L., & Guo, J. (2025). Are Large Language Models More Honest in Their Probabilistic or Verbalized Confidence? Lecture Notes in Computer Science, 124-135. https://doi.org/10.1007/978-981-96-1710-4_10
  - *锚定* — 原文直接对比同一模型的 token 概率派生置信度与自报 (verbalized) 置信度在诚实性/校准上的差异。F035/F042 采用的正是 verbalized 一支 (API 黑箱不返回 logprob), 该文是这一取数选择的最新实证权衡依据 — 它报告两种置信度各自的优劣, 并未论证 verbalized 优于概率法。
  - *迁移边界* — 原文任务为知识型问答的正确性判定, 置信度对应「答对与否」; 本项目置信度对应「情感极性判定」这一主观标注任务, 无客观 ground truth, 校准概念不能平移。原文为 NLPCC 会议论文 (LNCS 卷), 非金融期刊。
  - 〔Crossref 回读标题: Are Large Language Models More Honest in Their Probabilistic or Verbalized Confidence?〕
  - 〔已接线家族 (2): F035, F042〕
- 【2024–2026】Vashurin, R., Goloburda, M., Nakov, P., & Panov, M. (2025). UNCERTAINTY-LINE: Length-Invariant Estimation of Uncertainty for Large Language Models. Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing, 7892-7919. https://doi.org/10.18653/v1/2025.emnlp-main.400
  - *锚定* — 原文实证指出**依赖 token 概率**的不确定性量化方法存在系统性输出长度偏倚 (即便在名义上做过长度归一的方法中亦然), 并提出 UNCERTAINTY-LINE: 将不确定性分数对输出长度回归、取残差作为长度不变估计的事后去偏程序。对 F035/F042 只能作**一般性方法学背景**: 原文的偏倚机制限定于 token 概率派生的 UQ, 而本项目 conf 列为自报置信度、不经 token 概率, 且原文所测为输出长度而本项目三轨变动的是输入长度 —— 故原文**不构成**本项目三轨 conf 均值水平差异存在长度混淆的证据, 仅可作为「长度可能污染不确定性估计」这一泛化风险的提示性引用。
  - 〔Crossref 回读标题: UNCERTAINTY-LINE: Length-Invariant Estimation of Uncertainty for Large Language Models〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Groot, T., & Valdenegro - Toro, M. (2024). Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models. Proceedings of the 4th Workshop on Trustworthy Natural Language Processing (TrustNLP 2024), 145-171. https://doi.org/10.18653/v1/2024.trustnlp-1.13
  - *锚定* — 原文横向评测多个 LLM/VLM 自报(verbalized)不确定性的质量, 实证发现各模型系统性过度自信, 且过度自信程度随模型而异。对 F035/F042 而言, 这条锚定的是「自报置信度水平在模型间不可直接比较」这一事实基础 — 恰对应本项目把 deepseekv4 与 gemini31 的 conf 列并排为互稳轨、而非合并为单一指标的口径。原文并未讨论银行-年面板或本项目。
  - *迁移边界* — 原文为英文通用/视觉问答基准上的模型评测, 单位是逐题置信度; 本项目是中文金融新闻情感任务, 单位是银行-年均值, 且置信度受 valid-vote 掩码筛选后才入分母。原文所测模型不含 DeepSeek-V4-Flash / Gemini-3.1-Flash-Lite。
  - 〔Crossref 回读标题: Overconfidence is Key: Verbalized Uncertainty Evaluation in Large Language and Vision-Language Models〕
  - 〔已接线家族 (2): F035, F042〕
- 【2024–2026】Kwon, J., Lee, S. H., & Yoo, Y. (2024). Disagreement, Subjective Uncertainty, and the Stock Market. SSRN No. 4921479 [Working Paper]. https://doi.org/10.2139/ssrn.4921479
  - *锚定* — 原文提出在**公司 × 财季**层面分别量化横截面分歧与主观不确定性的方法 (基于分析师盈余指引与预测离散度), 并论证二者虽在实证研究中常被互换使用, 混同却会导致误导甚至相反的结论: 主观不确定性在分歧较低时与波动率正相关, 分歧较高时该关系反转为负; 二者对收益与成交量有相反且相互交互的效应。对 F204 锚定「分歧作为一个与不确定性**在构念上可分离**的独立可测量对象」这一金融学依据, 支持本项目把分歧指数与把握度类测度分列而非合并。**边界**: 未经同行评审的 SSRN 工作论文; 原文的分歧与主观不确定性均由分析师预测数据测得, **完全不涉及 LLM**, 故对本项目由 LLM 标签派生的口径不构成方法学支持, 亦不锚定 F035/F042 的自报置信度取数; 分析层级为公司-财季, 本项目为银行-年面板。
  - 〔Crossref 回读标题: Disagreement, Subjective Uncertainty, and the Stock Market〕
  - 〔已接线家族 (1): F204〕
- 【2024–2026】Yona, G., Aharoni, R., & Geva, M. (2024). Can Large Language Models Faithfully Express Their Intrinsic Uncertainty in Words? Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing, 7752-7764. https://doi.org/10.18653/v1/2024.emnlp-main.443
  - *锚定* — 原文提出 example 级 faithful response uncertainty 指标, 度量 LLM 在知识密集型问答中**以措辞对冲的方式**传达其内在不确定性的忠实度, 并实证主流对齐模型普遍做不到。对 F035/F042 而言, 它锚定的是「LLM 对自身不确定性的**语言化传达**普遍不忠实」这一邻近证据, 属该测度族的风险提示; 原文所测的是生成答案的对冲措辞, **非**本项目所用的数值型自报置信度, 故不能作为 conf 列的效度前提或方法原点。
  - 〔Crossref 回读标题: Can Large Language Models Faithfully Express Their Intrinsic Uncertainty in Words?〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕


### 十补-8. 媒体与模型分歧测度 (disag_* / tone_reversal / tone_volatility)

> 净增 14 条(其中 2024–2026 者 14 条; **4 条未接入任何家族**, 见各条标注)。**已接线家族** (9): F197, F200, F206, F208, F210, F576, F577, F593, F594

- 【2024–2026】Ferilli, G. B., Palmieri, E., & Cicchiello, A. F. (2026). Bank–FinTech cooperation: what the empirical evidence reveals in Asia–Pacific countries. International Journal of Emerging Markets, 1-26. https://doi.org/10.1108/ijoem-01-2026-0159
  - *锚定* — 原文是对 2015–2024 年 204 篇同行评议文献的结构化整合**综述** (含定性内容编码与共被引/关键词文献计量), 梳理亚太地区银行–金融科技合作的研究图景, 识别出三大研究簇: 合作对银行绩效/效率/风险承担的影响、监管套利与影子银行、以及组织转型与商业模式重构; 并指出**中国**是有关金科整合如何影响在位银行盈利、信贷配置与系统性风险的主要经验基础, 同时揭示「合作提升效率但可能把风险推出监管边界」的结构性张力。对本项目的意义: 为 tone_gap_indep_collab 中「外部协同」这一类目在银行业 (尤以中国为主要证据来源) 的构念存在性与经济重要性提供近期综述级依据。⚠ 原文是文献综述而非实证研究, 分析单位是论文而非银行, 不做媒体语调测量, 亦无银行层合作变量。迁移边界: 本项目在中文新闻篇章上先由 LLM 判定 innovation_collab_mode, 再按类目聚合作语调差分, 国别限于中国。
  - 〔Crossref 回读标题: Bank–FinTech cooperation: what the empirical evidence reveals in Asia–Pacific countries〕
  - 〔已接线家族 (2): F576, F577〕
- 【2024–2026】Fu, J. Y., Huang, A. G., Wermers, R. R., Zhang, J., & Zhang, Y. (2026). The Information Content of Tone Dispersion: Evidence from Earnings Conference Call Q&As. SSRN Electronic Journal No. 6566038 [Working Paper]. https://doi.org/10.2139/ssrn.6566038
  - *锚定* — 原文用 FinBERT (非词典法) 测算盈利电话会 Q&A 环节内分析师之间的语调离散 (tone dispersion), 并证明其信息含量增量于整体语调水平 (摘要明言 'incremental to the overall tone level'), 主题模型所测信息量与语调离散显著相关。对本项目的意义仅在构念层: 支持把「语调的散布」而非语调水平本身立为一条独立测度, 即 disag_* 与 tone 分列两族的必要性。属该测度族的前沿存在性证明, 非公式出处, 且方法路径不同源 (原文=BERT 分类器概率散布; 本项目=词典正负词比率的 Antweiler-Frank 闭式变换)。
  - 〔Crossref 回读标题: The Information Content of Tone Dispersion: Evidence from Earnings Conference Call Q&amp;amp;As〕
  - 〔已接线家族 (5): F197, F200, F206, F208, F210〕
- 【2024–2026】Goulding, C., Harvey, C., & Kurtović, H. (2026). Disagreement of Disagreement. National Bureau of Economic Research No. 35049 [Working Paper]. https://doi.org/10.3386/w35049
  - *锚定* — 原文系统比较了金融学中多种分歧 (disagreement) 代理变量, 指出不同构造方法给出的分歧度量彼此相关性低、结论不一致。该文支持本项目「逐词典各出一条 disag_*、互为稳健性并排」的做法之必要性 (分歧测度对构造方式敏感), 但原文并未评价本项目所用公式。
  - *迁移边界* — NBER 工作论文, 对象=美国市场分析师预测/交易量类分歧代理; 本项目=中文新闻词典命中比率的 AF 一致性指标, 国别/数据源/层级 (银行-年) 均不同。
  - 〔Crossref 回读标题: Disagreement of Disagreement〕
  - 〔已接线家族 (5): F197, F200, F206, F208, F210〕
- 【2024–2026】Jin, X., & Tian, Z. (2026). Online investor disagreement, self-attribution bias, and future stock returns. Financial Innovation, 12(1), 57. https://doi.org/10.1186/s40854-025-00835-3
  - *锚定* — 原文在中国市场用在线文本度量投资者分歧并研究其与后续收益的关系。对本项目而言, 是中文语境下文本分歧测度的近期前沿存在性证明, 支持 disag_* 作为独立信息维度而非语调残差。
  - *迁移边界* — 原文文本源=在线投资者论坛, 主体=上市公司; 本项目=银行新闻语料 + 中文金融情感词典 (bian_2021 / jiang_2021 / you_2018) 词级比率。分歧公式与词典均不同。
  - 〔Crossref 回读标题: Online investor disagreement, self-attribution bias, and future stock returns〕
  - 〔已接线家族 (3): F197, F206, F210〕
- 【2024–2026】Pham, H. (2026). From ESG noise to firm-specific risk: Adverse ESG sentiment trajectories and idiosyncratic volatility. Borsa Istanbul Review, 100863. https://doi.org/10.1016/j.bir.2026.100863
  - *锚定* — 原文把公司层情感的「轨迹」(随时间的路径与变化) 而非单期水平作为解释变量, 与本项目 F593 (语调一阶差分) / F594 (语调滚动标准差) 同属「情感时序动态测度」族。属前沿存在性证明。
  - *迁移边界* — 原文=ESG 新闻情感序列, 频率高于年度, DV=特质波动; 本项目=银行-年 LLM 共识语调, 差分与 rolling std 的窗口 (window=3, min_periods=2) 为本项目自设, 原文未使用同一公式。
  - 〔Crossref 回读标题: From ESG noise to firm-specific risk: Adverse ESG sentiment trajectories and idiosyncratic volatility〕
  - 〔已接线家族 (2): F593, F594〕
- 【2024–2026】Xu, Z., Yang, Y., & Zhang, T. (2026). Investor disagreement and state-dependent mispricing: New evidence on the analyst dispersion anomaly. Journal of Banking & Finance, 182, 107577. https://doi.org/10.1016/j.jbankfin.2025.107577
  - *锚定* — 原文以美国市场分析师预测离散度为投资者分歧代理, 检验分析师离散度异常 (dispersion anomaly) 与错误定价的**状态依赖**关系。对本项目的意义仅在于: 分歧 (离散度) 是一个被持续检验、且其定价含义随市场状态变化的独立构念, 支持在语调水平之外另设 disag_* 一列。⚠ 本条锚定为**标题层构念存在性**: 该文摘要在 Crossref/OpenAlex/Semantic Scholar 三源均不可得, 「分歧携带独立于情绪水平的信息」这一断言未经证实, 且 'state-dependent' 措辞提示原文可能恰恰刻画分歧效应对情绪/乐观状态的条件依赖, 引用时不得声称原文证明了分歧与情绪相互独立。迁移边界: 原文=美国市场分析师数值离散度, DV=股票收益/错误定价; 本项目=中国银行业新闻文本词典分歧, DV 为财务哨兵列, 层级=银行-年。
  - 〔Crossref 回读标题: Investor disagreement and state-dependent mispricing: New evidence on the analyst dispersion anomaly〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Yao, T., & Shi, Y. (2026). When ESG ratings disagree: information uncertainty and firm-specific volatility. Mitigation and Adaptation Strategies for Global Change, 31(4), 34. https://doi.org/10.1007/s11027-026-10307-3
  - *锚定* — 原文实证考察多家 ESG 评级机构评分不一致 (ratings disagreement) 如何经由信息不确定性转化为公司特质波动。对本项目的意义限于一条**类比性**旁证: 评价者之间的不一致可以转化为主体层面的时序波动上升, 提示分歧与波动虽是不同的量、却可能存在传导关系, 因此本项目的 disag_* 与 tone_volatility 不应被当作彼此的替代品而需分别观测其行为。⚠ 举证限制: 该文摘要在 Crossref/OpenAlex/Semantic Scholar 三源均不可得, 锚点仅在标题层成立; 原文刻画的是「分歧→波动」的因果传导, **未**主张二者是可分的并列测度, 不得据此声称原文为「两族并排保留」背书。迁移边界: 原文分歧来自多家 ESG 评级机构评分的离散 (多评价者结构), 波动=股票特质波动; 本项目 tone_volatility=银行-年 LLM 共识语调的三年滚动标准差 (window=3, min_periods=2), 与原文数据源、评价者结构与层级均不同。
  - 〔Crossref 回读标题: When ESG ratings disagree: information uncertainty and firm-specific volatility〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Driskill, M. W. (2025). Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns. Journal of Accounting, Auditing & Finance, 0148558X251384064. https://doi.org/10.1177/0148558x251384064
  - *锚定* — 原文专做分析师分歧测度的构造设计与效度比较, 证明既有离散度测度与盈利公告期异常成交的关联很弱 (与 Beaver 1968 相悖), 根因在预测窗口设定不当; 通过前推 ex ante 窗口 (纳入上一季度盈利后约 90–91 天的密集预测) 与压缩 ex post 窗口, 稳健地恢复了离散度与异常成交的正向关联, 而既有测度的结果 'inconsistent and inconclusive'。对本项目的意义**仅限一般测度学教训**: 分歧指标的构造选择 (窗口、样本纳入规则) 会实质改变其效度与结论方向, 因而 disag_* 的构造细节 (逐轨聚合口径、P+N=0 置 NaN 的样本纳入规则) 需显式披露并做敏感性检验。原文**未**讨论分母标准化或归一化选择, 亦不涉及媒体文本, 故不能作为本项目分母/归一化设定的直接参照。迁移边界: 原文=美国分析师盈利预测数值离散度, 层级=公司-季; 本项目=中文新闻词典正负词比率的 AF 变换, 层级=银行-年。
  - 〔Crossref 回读标题: Building Better Measures of Analyst Disagreement Around Earnings: Implications for Disagreement, Trading Volume, and Returns〕
  - 〔已接线家族 (5): F197, F200, F206, F208, F210〕
- 【2024–2026】Jamshed, A., Oberoi, J. S., & Lawal, T. O. (2025). Speaking with One Voice? The Joint Information Content of Tone in MD&A and Risk Factor Disclosures. SSRN No. 5265813 [Working Paper]. https://doi.org/10.2139/ssrn.5265813
  - *锚定* — 原文 (SSRN 工作论文, 未发表) 研究同一公司年报中 MD&A 与风险因素两节披露语调的联合信息含量, 标题设问 'Speaking with One Voice?' 提示其关注两节语调是否一致。对本项目 tone_gap_indep_collab 的意义仅限于**构念邻近的前沿存在性**: 把同一主体内两个来源的语调分开计算并对照, 是当前文本语调研究中的活跃方向。⚠ 举证限制: 该 WP 的摘要在 Crossref/OpenAlex 均不可得且 Semantic Scholar 未收录, 无法证实原文是否以「两者之差」作为测度; 'joint information content' 亦可能指联合/交互而非差分。引用时不得声称其与本项目「两条件均值相减」的构造同型, 亦不得作为已发表定论援引。迁移边界: 原文两个语调来源=同一份年报的 MD&A 与风险因素两节 (英文); 本项目两个来源=同一银行新闻中「自主研发」与「外部协同」两个 LLM 分类类目下的三家多数投票语调, 且加了双侧 n>=5 门槛。
  - 〔Crossref 回读标题: Speaking with One Voice? The Joint Information Content of Tone in MD&amp;amp;A and Risk Factor Disclosures〕
  - 〔已接线家族 (2): F576, F577〕
- 【2024–2026】Ning, J., Tao, L., Mi, B., & Zhang, L. (2025). The use of managerial tone in corporate disclosure: a literature review in accounting and finance. Journal of Accounting Literature, 1-88. https://doi.org/10.1108/jal-07-2024-0150
  - *锚定* — 原文是管理层语调的结构化文献综述 (SLR), 以 8 项分类标准评估过去 15 年 163 项研究 (其中 78 篇为 2022 年后新增), 梳理语调研究的发展轨迹、主题分布 (37% 考察语调的信息角色、33% 考察其决定因素, 较少涉及说服角色、操纵与后果)、披露媒介 (以 SEC 备案、电话会、新闻稿、年报为主, ESG 报告与社交媒体研究上升) 与地域分布 (以美国为主, 兼及英国、中国与国际市场), 并跨披露媒介、监管环境与研究方法作系统评估。对本项目的意义: 作为语调测量方法学选择与效度争议的总览性参照, 为本项目多词典并排 (loughran / du / bian / jiang / you) 的方法学定位提供文献坐标。⚠ 该综述以英文公司披露的**管理层**语调为对象 (第一方自我披露), 覆盖的词典以 Loughran-McDonald 系为核心; 本项目对象是**第三方新闻**语调 + 中文词典族, 层级为银行-年。⚠ 摘要未显示该综述覆盖语调的时序动态测度 (差分/滚动波动), 故不得作为 tone_reversal/tone_volatility 的方法学依据; 原文亦不涉及分歧测度。
  - 〔Crossref 回读标题: The use of managerial tone in corporate disclosure: a literature review in accounting and finance〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Sun, Z., Sun, Y., Qiao, Q., & Zhang, P. (2025). Independent innovation and collaborative innovation: exploring the impact of digital technology transfer on green innovation from the perspective of innovation element flow. Environment, Development and Sustainability. https://doi.org/10.1007/s10668-025-07107-1
  - *锚定* — 原文以「自主创新 vs 协同创新」为并列的两条创新路径做对照分析, 是本项目 indep/collab 类目划分在中国语境下的近期构念参照 (证明该二分在中国创新研究中是标准且可测的划分)。原文不涉及媒体文本或语调。
  - *迁移边界* — 原文=中国区域/企业绿色创新, 用专利与技术转移数据识别两条路径; 本项目用 LLM 对新闻篇章打 innovation_collab_mode 标签, 主体是银行而非制造业创新主体, 且输出是语调差而非创新产出。
  - 〔Crossref 回读标题: Independent innovation and collaborative innovation: exploring the impact of digital technology transfer on green innovation from the perspective of innovation element flow〕
  - 〔已接线家族 (2): F576, F577〕
- 【2024–2026】Wang, G., Chen, M., Wang, X., Dong, Y., & Wang, Z. (2025). Opinion divergence, investor sentiment, and stock liquidity: Evidence from social media. Investment Analysts Journal, 54(2), 167-186. https://doi.org/10.1080/10293523.2024.2398338
  - *锚定* — 原文以社交媒体数据构建零售投资者观点分歧指数 (由爬取的看多/看空投票构造) 与在线投资者情绪指数 (由机器学习方法从评论文本构造), 检验二者对股票流动性的影响, 发现分歧与情绪均显著影响流动性, 且**情绪对分歧→流动性起中介作用**。对本项目的意义是: 观点分歧与情绪水平是两个可同时测量、彼此关联的测度, 分歧的效应可部分经情绪传导。⚠ 不得据此声称二者「各自独立」—— 原文是中介效应模型, 结论恰恰是二者纠缠; 本项目并排保留 disag_* 与 tone 两族的依据应另寻 (或降为: 二者非同一量, 值得分别观测)。迁移边界: 原文分歧源=看多看空投票 (非文本), 情绪源=社交媒体评论, DV=股票流动性, 层级=公司-期; 本项目=新闻语料词典比率的 AF 变换, 层级=银行-年, DV 为财务哨兵列。
  - 〔Crossref 回读标题: Opinion divergence, investor sentiment, and stock liquidity: Evidence from social media〕
  - 〔已接线家族 (2): F200, F208〕
- 【2024–2026】Huang, Z., Xu, Q., & Wang, X. (2024). Does Investors’ Online Public Opinion Divergence Increase the Trading Volume? Evidence from the CSI 300 Index Constituents. Journal of Risk and Financial Management, 17(8), 316. https://doi.org/10.3390/jrfm17080316
  - *锚定* — 原文在中国 CSI 300 成分股上采集股吧在线公众意见, 构造投资者观点分歧指标并检验其对交易量的影响, 发现在线舆论提升成交但**分歧降低**预期成交, 且高影响力投资者间的分歧抬高成交、低影响力投资者间的分歧加剧成交下滑。对本项目的意义是「中文在线文本 → 观点分歧指标 → 经济后果」这一研究链条的近期同域应用存在性。⚠ 不得称其为 Antweiler-Frank 范式应用: 原文摘要未载其分歧的归一化式, 无证据显示采用 AF 一致性指标。迁移边界: 原文分歧源=股吧投资者自陈看多/看空型公众意见 (非词典对文本的正/负标注), 主体=上市公司股票, 层级=股票-期; 本项目=报纸新闻报道经中文金融情感词典的词级正/负比率再作 AF 变换, 主体=银行, 层级=银行-年。
  - 〔Crossref 回读标题: Does Investors’ Online Public Opinion Divergence Increase the Trading Volume? Evidence from the CSI 300 Index Constituents〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Le, T., Ngo, T., Nguyen, D. T., & Do, T. T. (2024). Fintech and banking: friends or foes? Evidence from bank–fintech cooperation. International Journal of Bank Marketing, 42(7), 1513-1535. https://doi.org/10.1108/ijbm-09-2023-0525
  - *锚定* — 原文用越南银行 2007–2019 年样本 (系统 GMM), 自建跨七个金科细分领域的银行–金融科技**合作**多样性指数, 检验其对银行风险调整后收益的影响: 合作多样性总体提升风险调整后收益, 但效应依金科细分领域与银行所有制而异 (比较型金科领域为正、支付与移动钱包领域为负; 国有商业银行与大型银行、上市银行的正效应更明显)。对本项目的意义: 为 tone_gap_indep_collab 中「外部协同」类目提供银行层可测、且对银行经营有实质后果的构念依据。⚠ 原文**未**检验「合作 vs 竞争」二分 (标题 'friends or foes' 为修辞设问, 实证仅有合作侧指标), 故不能作为「两种模式对银行含义不同」的直接证据; 且「竞争」与本项目的「自主研发」并非同一构念。迁移边界: 原文=**单一国家 (越南)** 银行样本, DV 为风险调整后收益, 合作由跨领域合作事件构造; 本项目=中国银行-年新闻语调差值, 二分来自 LLM 对篇章的 innovation_collab_mode 分类而非公司间合作事件。
  - 〔Crossref 回读标题: Fintech and banking: friends or foes? Evidence from bank–fintech cooperation〕
  - 〔已接线家族 (2): F576, F577〕


### 十补-9. 叙事-行动背离 / 漂绿类比测度 (washing_ratio_* / washing_asymmetry / washing_tone_shift)

> 净增 14 条(其中 2024–2026 者 14 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (20): F122, F212, F345, F346, F515, F521, F559, F560, F601, F602, F604, F605, F607, F610, F611, F612, F613, F615, F617, F618

- 【2024–2026】Duan, Q., Song, Y., Wang, R., Yang, J., & Zhang, R. (2026). The ESG Rating Game: Deviation, Disagreement, and Greenwashing. Mathematical Finance, mafi.70040. https://doi.org/10.1111/mafi.70040
  - *锚定* — 该文建立正式模型, 刻画多个 ESG 评级机构之间的评分偏离与分歧如何与企业漂绿行为相联系。本项目 F613 washing_ratio_hc 以三家 LLM 情感投票一致率 (agreement_rate ≥ 2/3) 划定高置信度子样本, 其「当多个独立评价者对同一对象判定分歧较大时, 该判定的信息含量下降」这一设计动机, 与该文所刻画的分歧-漂绿结构处于相邻问题域, 可作为动机层锚点。⚠ 严格自限: 原文为博弈论/数理金融建模, 评价者为评级机构, 对象为企业环境绩效, 无文本测量、无实证面板、无一致率门槛取值的效度检验; 本项目一致率仅作样本筛选门槛而不进入回归, 亦不做策略均衡推断。不可宣称原文支持 HC_AGREEMENT_THRESHOLD 的具体取值, 亦不锚定 F601 washing_asymmetry (其作差发生在同一评价者的两个效价通道之间, 与跨评价者分歧非同一数学对象)。
  - 〔Crossref 回读标题: The ESG Rating Game: Deviation, Disagreement, and Greenwashing〕
  - 〔已接线家族 (1): F613〕
- 【2024–2026】Huang, Y., Zhang, Y., Li, Y., Ma, S., & Hao, C. (2026). Different effect of positivity and negativity: ESG media sentiment and corporate energy consumption intensity. International Review of Economics & Finance, 108, 105256. https://doi.org/10.1016/j.iref.2026.105256
  - *锚定* — 该文实证表明媒体 ESG 情感的正面侧与负面侧对企业实质行为的影响存在方向与幅度上的不对称。这为本项目 F601 washing_asymmetry 把「正面-象征」通道与「负面-实质」通道分开构造再作差, 提供了媒体情感极性不对称的前沿实证依据。
  - *迁移边界* — 原文的不对称体现在正/负媒体情感对 DV (能耗强度) 回归系数的差异, 属效应侧不对称; 本项目 washing_asymmetry 是在测量侧把两个比率直接相减构成单一指标, 二者不是同一数学对象。原文议题为 ESG/能耗, 主体为非金融企业, 未涉及象征-实质判定。
  - 〔Crossref 回读标题: Different effect of positivity and negativity: ESG media sentiment and corporate energy consumption intensity〕
  - 〔已接线家族 (1): F601〕
- 【2024–2026】Li, Q., Zhang, Y., & Um, G. (2026). Too good to be true: The effect of media coverage on ESG greenwashing via managerial myopia. International Review of Economics & Finance, 107, 105056. https://doi.org/10.1016/j.iref.2026.105056
  - *锚定* — 该文检验媒体报道通过管理层短视渠道影响 ESG 漂绿的机制, 即媒体关注本身可诱发「说得太好」的叙事-实质背离。这为本项目在媒体报道语料上测量 washing 类指标提供了「媒体报道与漂绿内生联结」的前沿机制证据。
  - *迁移边界* — 原文漂绿测度来自企业 ESG 披露与绩效之差 (非文本判定器), 媒体报道为解释变量; 本项目漂绿类比测度完全由媒体报道内部的 LLM/词典/BERT 判定构造, 媒体既是测量载体也是唯一数据源, 因此原文的因果方向与本项目的测量口径不可直接互换。议题为 ESG 而非金融科技。
  - 〔Crossref 回读标题: Too good to be true: The effect of media coverage on ESG greenwashing via managerial myopia〕
  - 〔已接线家族 (1): F602〕
- 【2024–2026】Li, Y., & Zhu, C. (2026). Govern digitalization with digitalization: government digital governance and corporate false digital disclosure. International Review of Economics & Finance, 106, 104974. https://doi.org/10.1016/j.iref.2026.104974
  - *锚定* — 该文构造中国企业「虚假数字化披露」(false digital disclosure) 测度并检验政府数字治理对其的抑制作用。虚假数字披露 = 数字化叙事强度与实质数字化不匹配, 与本项目 washing_ratio 的分子构念 (正面叙事 ∧ 实质性缺席) 同义, 是中文语境下该构念的最新前沿测度。
  - *迁移边界* — 原文测度对象为企业自我披露文本 (年报), 参照系为企业内部数字资产/投入, 单位=公司-年; 本项目对象为外部媒体报道, 实质性由 LLM 逐篇判定而非与财务投入比对, 单位=银行-年。原文未使用中文情感词典分层, 本项目 F604/F607/F617 的词典判定器口径原文未涉及。
  - 〔Crossref 回读标题: Govern digitalization with digitalization: government digital governance and corporate false digital disclosure〕
  - 〔已接线家族 (4): F602, F604, F607, F617〕
- 【2024–2026】Long, H., & Hao, Y. (2026). AI talk–action gaps and ESG rating sensitivity: Evidence from Chinese A-share firms. Oeconomia Copernicana, 17(2), 457-513. https://doi.org/10.24136/oc.4220
  - *锚定* — 该文对中国 A 股企业构造 AI 的 talk–action gap (言论强度与实际行动之差), 并检验其与 ESG 评级敏感性的关系。其 gap 的差分式构造与本项目 washing_asymmetry 的差分式、washing_tone_shift 的子样本减法属同一类「叙事-行动背离」量化, 是该测度族在中国技术话语情境下的前沿存在性证明。
  - *迁移边界* — 原文 talk 侧来自年报文本 AI 词频, action 侧来自企业实际投入/专利, 观测单位=公司-年, 技术域为 AI 且 DV 为 ESG 评级敏感性; 本项目 talk/action 两侧同源于新闻报道内部的 LLM 象征-实质判定 (无外部行动侧数据), 单位=银行-年, 技术域为金融科技。
  - 〔Crossref 回读标题: AI talk–action gaps and ESG rating sensitivity: Evidence from Chinese A-share firms〕
  - 〔已接线家族 (1): F601〕
- 【2024–2026】García Lara, J. M., García Osma, B., Gazizova, I., & Khalilov, A. (2025). Demand-driven corporate social responsibility: Symbolic versus substantive change after environmental disasters. Journal of Corporate Finance, 94, 102816. https://doi.org/10.1016/j.jcorpfin.2025.102816
  - *锚定* — 该文在环境灾难冲击后, 将企业 CSR 反应实证区分为 symbolic change 与 substantive change 两类, 并检验二者受需求侧压力驱动的差异。这是本项目 washing_ratio 分子/分母二分 (象征性 vs 实质性) 在公司金融顶刊中的同构操作化, 属该二分的前沿因果应用存在性证明, 而非对本项目方法的背书。
  - *迁移边界* — 原文为美国/跨国上市公司 CSR 情境, 象征-实质由公司行动与披露判定, 观测单位=公司-事件; 本项目为中国银行-年, 象征-实质由 LLM 对单篇新闻报道的 innovation_substantiveness 判定, 构念载体是媒体报道而非企业行动, 且本项目取比率而非二元分类。
  - 〔Crossref 回读标题: Demand-driven corporate social responsibility: Symbolic versus substantive change after environmental disasters〕
  - 〔已接线家族 (2): F602, F612〕
- 【2024–2026】Gui, K., & Hou, H. (2025). Digital transformation, media coverage, and management tone manipulation. Finance Research Letters, 81, 107440. https://doi.org/10.1016/j.frl.2025.107440
  - *锚定* — 该文同时纳入数字化转型、媒体报道与管理层语调操纵三者, 检验媒体报道对语调操纵的作用。它在中国科技转型语境中把「媒体报道」与「语调操纵」联结, 与本项目在银行金融科技报道上测量语调偏移 (washing_tone_shift) 的构念场景直接同域。
  - *迁移边界* — 原文语调操纵仍以企业自述文本为测量对象, 媒体报道仅作解释/调节变量; 本项目语调本身即从媒体报道中测得, 无企业自述通道, 且偏移定义为象征性子样本与全样本的均值差, 而非原文的操纵残差。主体为非金融上市公司而非银行。
  - 〔Crossref 回读标题: Digital transformation, media coverage, and management tone manipulation〕
  - 〔已接线家族 (2): F212, F618〕
- 【2024–2026】Li, Y. (2025). Can large language models (LLMs) replace human reading? Empirical evidence from sustainability reports. Finance Research Letters, 85, 108096. https://doi.org/10.1016/j.frl.2025.108096
  - *锚定* — 该文以可持续报告为语料, 实证比较 LLM 抽取与人工阅读的结果一致性, 评估 LLM 能否替代人工完成文本内容判定。这直接支撑本项目以 LLM 逐篇判定 innovation_substantiveness 并据以构造 washing_ratio 的判定器效度前提, 是 LLM-as-annotator 在金融文本上的前沿效度证据。
  - *迁移边界* — 原文语料为英文可持续报告, 判定任务为可持续内容抽取, 未涉及象征-实质二分, 亦未做多模型投票; 本项目语料为中文银行新闻, 判定任务为创新实质性三值分类, 且采用 gpt54nano/gemini31/deepseekv4 三家投票共识。原文的效度结论不能直接外推到本项目的中文任务与具体模型版本。
  - 〔Crossref 回读标题: Can large language models (LLMs) replace human reading? Empirical evidence from sustainability reports〕
  - 〔已接线家族 (4): F602, F605, F611, F612〕
- 【2024–2026】Li, Y., Li, J., Zheng, Y., Zheng, G., & Wu, C. (2025). Machine learning detection of manipulative environmental disclosures in corporate reports. Scientific Reports, 15(1), 45011. https://doi.org/10.1038/s41598-025-29621-y
  - *锚定* — 该文用监督式机器学习分类器检测企业报告中的操纵性环境披露, 即以端到端训练的分类器识别「文本宣称与实质不符」的段落/文档。它锚定「披露操纵这一构念可由分类器在大规模文本上自动测量」这一存在性前提, 与本项目在文本判定器之上构造洗稿率的总体思路相邻。⚠ 严格自限: ① 原文分类器直接以「是否操纵」为标签端到端训练, 观测单位=企业报告; 本项目 F603/F610 的 BERT **不**判定操纵, 仅承担情感极性判定 (正面/中性/负面), 象征-实质标签另由 LLM 提供, 二者交叉后在银行-年层聚合为比率 — 因此原文与本项目并非同一方法族, 该文不构成 F603/F610 判定器口径的方法学依据。② 无证据表明原文使用预训练语言模型, 不可宣称其为「预训练分类器」先例。③ 原文为英文企业自述文本与环境议题, 本项目为中文第三方新闻与金融科技议题。
  - 〔Crossref 回读标题: Machine learning detection of manipulative environmental disclosures in corporate reports〕
  - 〔已接线家族 (1): F610〕
- 【2024–2026】Qian, M., Wei, Z., & Bai, R. (2025). Does ESG narrative specificity mitigate rating disagreement? evidence from ESG reports in China. Finance Research Letters, 86, 108430. https://doi.org/10.1016/j.frl.2025.108430
  - *锚定* — 该文以中国 ESG 报告为语料, 把多评级机构间的分歧作为结果变量, 检验叙事具体性 (narrative specificity) 是否降低分歧。它在「多评价者分歧是文本信息质量信号」这一层面, 与本项目 F613 以三家 LLM 投票一致率划定高置信子样本的设计动机相邻。
  - *迁移边界* — 原文评价者是 ESG 评级机构, 分歧是被解释变量且基于评级分数方差; 本项目评价者是三家 LLM, 一致率仅作为样本筛选门槛 (≥2/3), 不进入回归。原文未提供任何一致率门槛取值的效度检验, 因此不可宣称其支持本项目 HC_AGREEMENT_THRESHOLD 的具体取值, 仅为动机层锚点。
  - 〔Crossref 回读标题: Does ESG narrative specificity mitigate rating disagreement? evidence from ESG reports in China〕
  - 〔已接线家族 (1): F613〕
- 【2024–2026】Zhou, H. (2025). Major shareholders' equity pledge and the “All talk and no action” strategy in digital transformation. Economic Analysis and Policy, 87, 1630-1652. https://doi.org/10.1016/j.eap.2025.07.036
  - *锚定* — 该文直接构造并检验中国上市公司数字化转型中的「只说不做」(all talk and no action) 策略, 以股权质押为驱动因素。它证明了在中国数字化/科技话语场景中, 「宣称强度远超实质投入」是可测量、可识别的企业策略, 与本项目 washing_ratio 的构念定义一致。
  - *迁移边界* — 原文测度基于企业自身年报数字化词频与实际数字投入之比, 主体=非金融上市公司, 识别策略=股权质押冲击; 本项目测度基于第三方新闻报道的 LLM 象征性判定占正面报道之比, 主体=商业银行, 且本轮仅取其构念定义与存在性, 不迁移其识别设计。
  - 〔Crossref 回读标题: Major shareholders' equity pledge and the “All talk and no action” strategy in digital transformation〕
  - 〔已接线家族 (4): F602, F605, F611, F612〕
- 【2024–2026】Meng, Q., Du, X., & Gong, X. (2024). Does operational disclosure curb textual tone manipulation by corporate management? China Journal of Accounting Studies, 12(2), 247-275. https://doi.org/10.1080/21697213.2024.2337262
  - *锚定* — 该文在中国情境下测量管理层文本语调操纵 (textual tone manipulation), 即语调正面程度超出基本面可解释部分, 并检验经营性披露的约束作用。其「语调 − 基准语调」的残差/差分思路, 与本项目 washing_tone_shift = 象征性子样本语调 − 全样本语调 属同一类语调偏移量化, 且使用中文金融文本词典化语调测度。
  - *迁移边界* — 原文基准语调来自基本面回归拟合值 (残差法), 语调来源为企业自述年报文本, 单位=公司-年; 本项目基准是同轨全部留篇的 LLM 投票均值语调, 偏移由子样本减法而非回归残差得到, 文本来源为第三方新闻。原文未涉及象征-实质二分, 亦未使用 LLM。
  - 〔Crossref 回读标题: Does operational disclosure curb textual tone manipulation by corporate management?〕
  - 〔已接线家族 (5): F122, F212, F345, F346, F618〕
- 【2024–2026】Sun, Y. (2024). Bank competition and firm greenwashing: Evidence from China. Finance Research Letters, 63, 105279. https://doi.org/10.1016/j.frl.2024.105279
  - *锚定* — 该文在中国情境下检验银行业竞争度对借款企业漂绿行为的影响, 是银行部门变量与漂绿测度同时出现的近期实证之一。本条**仅**作为研究场域的背景引用, 说明中国银行业与漂绿议题的交叉已有实证文献存在。⚠ 严格自限 (强于常规迁移边界): ① 原文中银行是**解释变量** (竞争度), 漂绿主体是借款企业, 漂绿测度基于企业 ESG 披露-绩效差; 本项目中银行是漂绿类比测度的**被测主体**, 测度基于银行金融科技新闻报道的象征性占比 — 主客体互换, 因此该文**并未**建立「银行作为漂绿被测主体」的场域存在性, 不可据其宣称本项目构念已有同域先例。② 原文无文本判定器、无象征-实质二分、无比率型 washing 指标, 对 F603/F610 的 BERT 判定器口径及 F601/F618 的构造均无任何方法学贡献。③ 本条证据强度为背景级, 不承担任何构念或测度的锚定职能。
  - 〔Crossref 回读标题: Bank competition and firm greenwashing: Evidence from China〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
  - *锚定* — 该文研究 ESG 评级如何推动企业创新结构从象征性向实质性迁移, 把「象征性占比」作为可随外部监督变化的结构性比例来处理。其以象征性/实质性构成比 (而非绝对水平) 为分析对象的做法, 与本项目 washing_ratio 取「象征性 / 正面且实质性已测」比率的分母同域设计逻辑一致。
  - *迁移边界* — 原文比例基于专利结构数据, 主体为中国 A 股非金融企业, 驱动因素为 ESG 评级; 本项目比率基于新闻报道计数, 分母限定为「正面判定 ∧ 实质性已被 LLM 测出」的报道, 主体为银行。原文未使用文本判定器, 因此不锚定 F615/F617 的词典口径本身, 仅锚定象征占比构念。
  - 〔Crossref 回读标题: From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure〕
  - 〔已接线家族 (7): F515, F521, F559, F560, F602, F615, F617〕


### 十补-10. 迎合测度 (cater / cater_b)

> 净增 10 条(其中 2024–2026 者 10 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (14): F002, F003, F139, F140, F141, F143, F144, F345, F346, F413, F621, F622, F638, F639

- 【2024–2026】Gielens, E., Sowula, J., & Leifeld, P. (2026). Goodbye human annotators? Content analysis of social policy debates using ChatGPT. Journal of Social Policy, 55(2), 385-404. https://doi.org/10.1017/s0047279424000382
  - *锚定* — 该文评估 ChatGPT (GPT-4 / GPT-4 Turbo) 依预设论点描述对政策辩论文本分类的能力, 以人工编码为基准, 发现其整体准确率虽高、但 precision 与 recall 显著偏低且在不同论点类别间差异极大, 作者据此明确不建议在未经人工校验的情况下直接采用其分类结果。对应本桶「综合词典 − LLM 共识」差值族 (F003 = dict_avg_tone{track} − llm_vote_tone{track}) 的 **LLM 端效度前提**: 提供跨领域证据表明 LLM 的文本判断在类别间存在结构性的不稳定, 因而不能被当作无误差参照, 有向差值不应被单向解读为词典侧偏误。⚠ 举证限制: 原文的对照臂**仅有人工标注者**, 既无任何情感词典, 亦无任何 BERT/监督式模型 —— 故本条**不得**用于锚定以 BERT 净语调为被减数的家族 (F002 及其它 *_cater_b 族), 亦不得声称原文比较了「既有自动化内容分析方法」。领域=社会政策辩论 (荷兰推特全民基本收入辩论 / 德国报纸养老金改革辩论), 非金融、非中文; 结论以准确率/precision/recall 呈现, 不产出连续净语调差值; 无企业或银行层级面板。
  - 〔Crossref 回读标题: Goodbye human annotators? Content analysis of social policy debates using ChatGPT〕
  - 〔已接线家族 (1): F003〕
- 【2024–2026】Wang, Y., Wong, T., & Zhang, T. (2026). Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China. SSRN Electronic Journal No. 6143029 [Working Paper]. https://doi.org/10.2139/ssrn.6143029
  - *锚定* — 该文在中国语境下把两类媒体文本的语调并置, 以其中一方识别另一方的乐观偏差, 方法形态上与本桶「两个同构念语调测度相减、把有向差解读为一方的系统性偏离」同型。对应 F002/F003 两个综合差值族与 yao_2021 迎合族 (F621/F622)。原文比较的是两类媒体来源之间的偏差, 而非同一文本上词典法与深层模型法之间的偏差——同型但不同轴。
  - *迁移边界* — 差值轴不同: 原文=媒体来源 A 与来源 B 的语调差 (来源层偏差), 本项目=同一篇文本上词典测度与深层模型测度之差 (方法层偏差); 语料=国有媒体与社交媒体 (非银行金科报道); 无 BERT/LLM 三家投票口径; 层级=公司/事件层, 非 bank-year。工作论文, 未经期刊同行评议。
  - 〔Crossref 回读标题: Does Social Media Identify the Optimistic Bias of State-Controlled Media? Evidence from China〕
  - 〔已接线家族 (4): F002, F003, F621, F622〕
- 【2024–2026】Bose, I., Hu, N., Liang, P., & Yang, X. (2025). Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment. SSRN No. 5153587 [Working Paper]. https://doi.org/10.2139/ssrn.5153587
  - *锚定* — 该文把 GPT (LLM)、FinBERT (BERT) 与情感词典三类方法在同一管理层文本语料上头对头比较, 报告三者对管理层语调判断的不一致。这正是本桶差值指标两端 (词典侧 vs 深层模型侧) 的直接测度学比较依据: 它实证了三类方法在同一文本上会给出系统性不同的语调评分, 即本桶 cater 差值非零并非噪声。原文只做方法比较, 未把差值本身构造为指标。
  - *迁移边界* — 原文语料=英文管理层沟通文本 (非中文银行/金科新闻报道), 模型侧=GPT 与 FinBERT (非本项目的 gpt54nano/gemini31/deepseekv4 三家投票与 finbert_cn/fin_sent_zh/finbert2 三 BERT), 词典侧为英文词典 (非 loughran 中译及 bian/du/jiang/yao/you 中文词典); 分析层级=文档级方法比较, 非 bank-year 面板聚合。工作论文, 未经期刊同行评议。
  - 〔Crossref 回读标题: Can Larger Language Models Always Perform Better? A Comparison of GPT, FinBERT, and Dictionaries in Evaluating Management Sentiment〕
  - 〔已接线家族 (5): F002, F003, F141, F144, F413〕
- 【2024–2026】Kristensen-McLachlan, R. D., Canavan, M., Kárdos, M., Jacobsen, M., & Aarøe, L. (2025). Are chatbots reliable text annotators? Sometimes. PNAS Nexus, 4(4), pgaf069. https://doi.org/10.1093/pnasnexus/pgaf069
  - *锚定* — 该文系统检验 LLM 作为文本标注器相对于监督式模型与既有基线的可靠性, 结论是 LLM 表现随任务而异、并非一致优于传统方法。这是本桶「词典 − 单家 LLM」差值 (F139/F143/F144) 与「词典 − LLM 共识」(F003) 的效度前提锚点: 它证明把 LLM 判断当作无误差参照并不成立, 因此差值不能被单向解读为词典侧偏误。原文做的是标注可靠性评估, 与本项目指标无关联。
  - *迁移边界* — 原文任务=政治学/社科英文文本标注 (非金融语调, 非中文); 对照臂=监督式微调模型与人工标注, 不含中文金融情感词典; 未涉及 bank-year 聚合或迎合构念; 使用的 LLM 家族与本项目 gpt54nano/gemini31/deepseekv4 不同。
  - 〔Crossref 回读标题: Are chatbots reliable text annotators? Sometimes〕
  - 〔已接线家族 (4): F003, F139, F143, F144〕
- 【2024–2026】Lee, J., Stevens, N., & Han, S. C. (2025). Large Language Models in Finance (FinLLMs). Neural Computing and Applications, 37(30), 24853-24867. https://doi.org/10.1007/s00521-024-10495-6
  - *锚定* — 该文综述金融领域语言模型从 FinBERT 类判别式模型到生成式 FinLLM 的技术谱系与评测数据集。对应本桶差值的 BERT 端 (F002 三 BERT 均值 / F140 fin_sent_zh / F141 finbert2): 为「BERT 族仍是金融情感的独立可用测度族, 与 LLM 并非同一测度」提供综述层面的定位依据。原文是综述, 不含任何实证测度比较结果。
  - *迁移边界* — 综述性质 (非原创实证), 覆盖以英文金融 NLP 为主, 未评测中文金融 BERT (finbert_cn/fin_sent_zh/finbert2 均未纳入); 不含词典对照臂, 不含迎合构念, 无面板层级。引用时只能作技术谱系定位, 不能用作任何数值口径依据。
  - 〔Crossref 回读标题: Large Language Models in Finance (FinLLMs)〕
  - 〔已接线家族 (2): F002, F141〕
- 【2024–2026】Mo, H., & Ouyang, S. (2025). (Generative) AI in Financial Economics. Journal of Chinese Economic and Business Studies, 23(4), 509-587. https://doi.org/10.1080/14765284.2025.2569006
  - *锚定* — 该文是一篇综述, 围绕六大板块梳理生成式人工智能 (尤其是大语言模型) 与金融的交叉文献: (1) 生成式 AI 作为分析工具、外生冲击与自主经济代理的新兴角色; (2) 公司金融; (3) 资产定价; (4) 家庭金融; (5) 劳动经济学; (6) AI 在金融市场中的风险与挑战。对应 F003 (dict_avg_tone − llm_vote_tone) 与 F639 (you_2018_tone − llm_vote_tone) 的 **LLM 端**: 仅作为「生成式 AI / 大语言模型已成为金融经济学中被系统综述的分析工具」这一最弱层级的技术脉络定位引用。⚠ 举证限制一: 该综述按**金融学科领域**组织 (公司金融/资产定价/家庭金融/劳动/风险), 摘要中**不存在**「从词表法到 LLM 的文本测度演进脉络」这一线索 —— 本条**不得**被表述为提供了「词表法与生成式模型法并置评估」的定位依据。⚠ 举证限制二: 该综述覆盖面以英文金融文献为主, 主题范围无中国特定内容; **不得**以其载体期刊 (Journal of Chinese Economic and Business Studies) 的地域取向反推内容的中国相关性。⚠ 举证限制三: 本文是生成式 AI 综述, **不得**用于锚定任何以判别式 BERT 净语调为被减数的家族 (F638 及其它 *_cater_b 族)。综述性质, 非原创实证, 无数据无结果可迁移; 未评测中文金融词典或中文 BERT; 无 bank-year 面板层级; 不能用作任何测度口径或数值依据。
  - 〔Crossref 回读标题: (Generative) AI in Financial Economics〕
  - 〔已接线家族 (1): F639〕
- 【2024–2026】Kim, W., Spörer, J., Lee, C. L., & Handschuh, S. (2024). Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER. Proceedings of the 5th ACM International Conference on AI in Finance, 626-633. https://doi.org/10.1145/3677052.3698675
  - *锚定* — 该文在同一金融沟通语料上并排评测词典法 (VADER)、BERT 族 (FinBERT / FinBERT-FOMC) 与 LLM (GPT-4 / Llama-3-70B), 给出三类方法语调判断的分歧证据。对应本桶「词典 − BERT」(F002/F140/F141) 与「词典 − LLM」(F003) 两类差值的模型端选择依据: 它说明模型规模更大不必然与词典/小模型一致。原文是评测基准工作, 未构造迎合差值。
  - *迁移边界* — 原文语料=美联储 FOMC 英文沟通文本, 非中文银行金科新闻; 词典臂=VADER 通用情感词典, 与本项目 6 部中文金融词典口径不同; BERT 臂=FinBERT/FinBERT-FOMC, 非 finbert_cn/fin_sent_zh/finbert2; 评价目标=分类准确率对齐人工标签, 非本项目的有向差值面板列。会议论文。
  - 〔Crossref 回读标题: Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER〕
  - 〔已接线家族 (4): F002, F003, F140, F141〕
- 【2024–2026】Tan, L., Wu, H., & Zhang, X. (2024). Large Language Models and Return Prediction in China. SSRN Electronic Journal No. 4712248 [Working Paper]. https://doi.org/10.2139/ssrn.4712248
  - *锚定* — 该文在中国市场情境下检验大语言模型对股票收益的预测能力, 是 LLM 方法进入中国金融实证研究的前沿应用之一。对应本桶差值 LLM 端诸族 (F003/F139/F143/F144): 仅作为「LLM 已被用于中国金融场景的信息处理与信号提取」这一地域可行性的弱定位引用。⚠ 举证限制: 本条三源 (Crossref/OpenAlex/Semantic Scholar) 均无摘要, 无法证实原文的模型输入是否为新闻文本 —— 故**不得**据本条主张「LLM 处理中文财经新闻的存在性证明」, 亦不得用于支撑任何语调类测度的构造合法性 (该职能应由 ssrn.4961494 LLM-Measure 承担)。原文做的是收益预测, 未与词典测度作差, 未涉及迎合构念, 无词典对照臂。工作论文, 未经期刊同行评议。
  - 〔Crossref 回读标题: Large Language Models and Return Prediction in China〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Wang, H. (2024). Media Tone and Earnings Management before the Earnings Announcement: Evidence from China. Economics, 18(1), 20220129. https://doi.org/10.1515/econ-2022-0129
  - *锚定* — 该文用中文媒体报道语调测度检验其与盈余管理的关系, 是「中文媒体报道语调经词典类方法可测且具经济含义」的应用同域证据。对应以中文词典为词典端的迎合族 (F345·F346 jiang_2021 / F638·F639 you_2018): 支撑本项目差值词典端所依赖的中文媒体语调测度传统。原文只用单一语调测度, 无任何模型对照。
  - *迁移边界* — 报道对象=中国上市公司一般财经报道 (非银行×金融科技共现报道); 语调=单臂词典测度, 无 BERT/LLM 对照臂, 故只锚定差值的词典端不锚定模型端; DV=盈余管理 (非本项目面板列); 期刊层级一般 (Economics, De Gruyter), 非顶刊; 层级=公司-事件窗, 非 bank-year。
  - 〔Crossref 回读标题: Media Tone and Earnings Management before the Earnings Announcement: Evidence from China〕
  - 〔已接线家族 (4): F345, F346, F638, F639〕
- 【2024–2026】Yang, Y., Duan, H., Liu, J., & Tam, K. Y. (2024). LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research. SSRN No. 4961494 [Working Paper]. https://doi.org/10.2139/ssrn.4961494
  - *锚定* — 该文提出并检验用 LLM 生成社科文本测度的效度、一致性与可复现性框架。对应本桶差值的 LLM 端 (F003 共识轨 与 F139/F143/F144 单家轨) 的测度构造合法性锚点: 它是「把 LLM 输出当作可复现连续测度」这一做法的方法学存在性证明。原文只讨论 LLM 侧测度构造, 未与词典测度作差。
  - *迁移边界* — 原文为通用社科文本测度方法 (非金融语调专用, 非中文语料); 其可复现性依赖隐层表征提取路径, 与本项目「固定 prompt v8 + temperature=0 + 缓存冻结」的可复现路径不同; 未涉及词典对照臂, 也未做 bank-year 聚合。工作论文, 未经期刊同行评议。
  - 〔Crossref 回读标题: LLM-Measure: Generating Valid, Consistent, and Reproducible Text-Based Measures for Social Science Research〕
  - 〔已接线家族 (4): F003, F139, F143, F144〕


### 十补-11. 概率加权聚合方案梯子 (wd_hw / wd_mw / wd_vw × 三家 LLM × 阈值)

> 净增 11 条(其中 2024–2026 者 11 条)。**已接线家族** (17): F527, F528, F529, F531, F532, F533, F535, F536, F537, F538, F539, F540, F541, F542, F543, F544, F545

- 【2024–2026】Eliaz, K., & Spiegler, R. (2026). News media as suppliers of narratives (and information). Theoretical Economics, 21(3), 928-972. https://doi.org/10.3982/te6424
  - *锚定* — Eliaz & Spiegler 建立理论模型, 把新闻媒体刻画为叙事 (而不仅是信息) 的供给者, 并分析不同媒体供给的叙事如何影响受众信念。这为本项目「不同来源媒体的报道不等价、需要按来源加权」提供了理论侧的存在性论证。原文真实做的是理论建模与均衡分析, 无实证测度构造。
  - *迁移边界* — 纯理论文献, 不提供任何可直接迁移的权重赋值方案或经验参数; 原文的媒体差异化维度是叙事内容而非权威度; 与本项目 media_authority_weight 的具体取值口径 (config 登录表 + 未登录来源退默认 + fillna(1.0)) 无对应关系。
  - 〔Crossref 回读标题: News media as suppliers of narratives (and information)〕
  - 〔已接线家族 (3): F537, F539, F540〕
- 【2024–2026】Kwon, S. Y., & Tang, J. (2026). Extreme Categories and Overreaction to News. Review of Economic Studies, 93(2), 1137-1166. https://doi.org/10.1093/restud/rdaf037
  - *锚定* — Kwon & Tang (2026, Review of Economic Studies) 研究诊断性预期 (基于代表性启发的信念形成模型) 的资产定价含义: 在新闻事件来自不同「类别」且各类别的基本面分布尾部厚度不同的设定下, 模型预测投资者对**极端类别 (尾部事件更多的类别)** 的新闻过度反应更强; 作者在涵盖 24 类企业新闻 (业绩公告、产品发布、并购、业务扩张、客户相关等) 的数据库上检验, 发现基本面分布越极端的新闻类别, 公告后收益反转与成交量放大越明显。原文真实做的是理论 + 实证的类别化过度反应检验。对本项目的意义**限于一条构念侧的旁证**: 新闻的「类别归属」并非无信息含量的标签 —— 类别边界本身携带经济含义并系统性地关联到反应强度, 因而在测度构造中把连续量映射为类别/子集的边界取值不是一个中性的技术细节, 值得并排检验。本项目 F532/F533/F535 相应地把跟风相似度门槛 τ 在 {0.25, 0.30, 0.45} 上并排做敏感性, 三者互为稳健性、不分主次。**明确不主张原文做了连续信号的离散化, 亦不主张原文提出了「研究者须显式检验阈值」这一方法学规范**: 原文的类别是语料中外生既有的新闻题材, 机制是投资者信念形成中的行为偏误, 与研究者在跟风相似度检测网格上的口径选择是两种性质完全不同的离散化, 原文的类别边界与本项目的 τ 无对应物、数值不可比。原文亦未涉及文本相似度、跟风衰减权重、LLM 或加权分母。不锚定 F531 (该族公式不含任何阈值或类别切分)。
  - 〔Crossref 回读标题: Extreme Categories and Overreaction to News〕
  - 〔已接线家族 (3): F532, F533, F535〕
- 【2024–2026】Pelletier, J., Korb, M., Alemu, S., Yonis, M. B., Lybbert, T. J., & Stigler, M. (2026). Causal Inference with Predicted Outcomes: Correcting prediction error bias in satellite-based impact evaluation. Journal of Development Economics, 179, 103655. https://doi.org/10.1016/j.jdeveco.2025.103655
  - *锚定* — 该文实证演示了当结果变量由预测模型 (卫星影像) 生成时, 预测误差如何系统性偏置影响评估结果, 并比较了若干修正方案。对本项目 prob 权重族的意义在于: 它是「概率型模型输出被当作测度进入下游估计」的一个独立领域实证案例, 提示预测误差不是随机噪声。原文真实做的是卫星预测产量的影响评估复现与修正比较。
  - *迁移边界* — 领域完全不同 (遥感农业产量 vs 中文银行金科新闻语调), 预测器是 CV 模型而非 LLM; 原文的偏误来自连续预测值, 本项目 prob 侧是三分类概率映射; 原文有实测地面真值做基准, 本项目无。
  - 〔Crossref 回读标题: Causal Inference with Predicted Outcomes: Correcting prediction error bias in satellite-based impact evaluation〕
  - 〔已接线家族 (1): F540〕
- 【2024–2026】Ai, R., Pan, Y., Simchi-Levi, D., Tambe, M., & Xu, H. (2025). Beyond Majority Voting: LLM Aggregation by Leveraging Higher-Order Information. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2510.01499
  - *锚定* — Ai 等 (2025, arXiv 预印本, 未经同行评审) 指出朴素多数投票忽略了各 LLM 的期望准确率与模型间答案相关性, 提出利用这些高阶信息的聚合规则; 原文真实做的是聚合算法设计 + QA/推理基准实验。本项目 F539/F544 的 sum_wd_mw_llm / sum_wd_vw_llm 以 llm_vote_score (三家 LLM 朴素多数投票共识) 的非缺失掩码界定分母求和域, 故本文献锚定的是「多模型投票共识作为一种聚合口径」这一构念的前沿存在性, 提示朴素多数票并非唯一选择。**明确不构成对本项目投票口径的背书**: 本项目生产口径刻意保留朴素多数投票, 未采用原文的高阶聚合器; 原文任务为英文 QA/推理基准, 非中文新闻三分类语调, 且无权重加权分母与银行-年面板聚合。**不锚定 F532/F533/F535**: 该三族的阈值网格 τ∈{0.25,0.30,0.45} 是 stage 24 跟风相似度检测门槛 (作用于 herd_weight 权重侧), 与 LLM 聚合结果的阈值化无任何关系。
  - 〔DataCite 回读标题: Beyond Majority Voting: LLM Aggregation by Leveraging Higher-Order Information〕
  - 〔已接线家族 (2): F539, F544〕
- 【2024–2026】Cuñat, V., & Groen-Xu, M. (2025). Timing Complex News to Target Attention. Management Science, 71(9), 7774-7799. https://doi.org/10.1287/mnsc.2021.03722
  - *锚定* — Cuñat & Groen-Xu (2025, Management Science) 利用美国公司备案系统 5:30 p.m. 的制度断点 (截止前提交立即可见、截止后次晨才可见且吸引更少关注) 证明: 投资者注意力有限且时变, 而发行方会据此策略性择时 —— 把更长、更难处理的复杂新闻放在注意力更高的时段发布, 且此类新闻随后价格收敛更快、流动性更好。原文真实做的是新闻发布时点与新闻复杂度的实证分析。对本项目的意义**仅限于一条一般性的存在性证据**: 新闻条目在受众端的实际吸收强度并非同质, 因而「每篇报道等权计 1」并不是一个无争议的默认口径, 这为本项目 vw 族在分母中引入篇章级显著性权重提供了构念上的合理性空间。**明确不主张原文支持 mention_density 这一具体算子**: 原文的注意力维度是发布时点/日历制度断点与投资者端的注意力约束, 本项目 vw 权重是篇内银行实体提及密度, 两者是完全不同的显著性算子, 原文既未构造也未检验任何文本端权重。迁移边界: 原文层级为公司公告事件与高频市场反应, 本项目为银行-年报道池与面板分母; 原文亦未涉及 LLM 有效性掩码。
  - 〔Crossref 回读标题: Timing Complex News to Target Attention〕
  - 〔已接线家族 (4): F541, F542, F543, F544〕
- 【2024–2026】Kroner, N. (2025). How Markets Process Macro News: The Importance of Investor Attention. Finance and Economics Discussion Series [Working Paper]. https://doi.org/10.17016/feds.2025.022
  - *锚定* — Kroner (2025, Finance and Economics Discussion Series 2025-022, **美联储工作论文, 未经期刊同行评审**) 以宏观公告 × 投资者注意力代理估计高频市场反应, 实证表明同一条宏观新闻在投资者注意力高低不同的时点被市场吸收的程度显著不同。对本项目的意义**仅限于一条一般性的存在性证据**: 新闻条目的有效影响力随其被接收的显著性条件而变, 并非每条等权, 因而在银行-年聚合中对报道施加篇章级权重、而非一律等权计 1, 具有构念上的合理性空间。**明确不主张原文为 mention_density 提供经验依据**: 原文的注意力代理来自市场端 (交易/搜索类指标) 且是外生于文本的状态变量, 本项目 mention_density 是文本端的篇内银行实体提及密度, 两者构造完全不同, 原文未构造亦未检验任何文本端显著性权重, 更未比较加权与等权分母的优劣。迁移边界: 原文语境为美国宏观公告与高频价格反应, 本项目为中文银行报道与银行-年面板分母; 原文不涉及 LLM 有效性掩码与三轨 (full/ctx/ss) 设定。
  - 〔Crossref 回读标题: How Markets Process Macro News: The Importance of Investor Attention〕
  - 〔已接线家族 (2): F541, F542〕
- 【2024–2026】Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
  - *锚定* — Laurer 等系统检验了语言模型作为测量工具的效度问题, 并证明指令/提示设计会实质改变效度与偏误。本项目每个 per-model 分母列 (hw/mw × deepseekv4/gemini31/gpt54nano) 都以「该模型在该轨给出有效判断」为掩码, 该掩码本身即模型效度的函数, 故本文锚定的是这些 per-model 家族的效度前提。原文真实做的是提示/指令对模型测量效度的对照实验。
  - *迁移边界* — 原文对象是传播学英文文本分类任务与开源指令微调模型, 本项目是中文新闻 + 三家商用 API 模型; 原文结论支持「加指令可提效度」, 而本项目嵌入侧刻意零 instruct 前缀且情感提示词 v8 已字节冻结, 二者设计取向不同, 不可直接迁移; 原文无权重加权分母口径。
  - 〔Crossref 回读标题: On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions〕
  - 〔已接线家族 (6): F527, F528, F529, F536, F537, F538〕
- 【2024–2026】Liu, Y., Liu, J., & Wang, T. (2025). Large Language Model Disagreement. SSRN Electronic Journal No. 5395056 [Working Paper]. https://doi.org/10.2139/ssrn.5395056
  - *锚定* — 该文以金融文本为对象度量并分析不同大语言模型给出判断的分歧程度。对本项目的意义在于: F527/F528/F529 三个 per-model hw 分母之所以彼此不同, 完全来自各家 LLM 的有效打分覆盖面与判断差异, 而 F539/F544 的共识掩码则是分歧的折叠结果。原文真实做的是跨模型分歧的度量与实证刻画。
  - *迁移边界* — 工作论文 (SSRN), 尚未经期刊同行评审; 原文关注分歧本身作为信号/噪声, 本项目不把分歧当变量, 只用各家有效性掩码做分母; 原文的模型集合、语料与本项目 gpt54nano/gemini31/deepseekv4 三家 + 中文银行金科语料不同。
  - 〔Crossref 回读标题: Large Language Model Disagreement〕
  - 〔已接线家族 (4): F527, F528, F529, F539〕
- 【2024–2026】Wright, D., & Augenstein, I. (2025). Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift. PLOS One, 20(6), e0323064. https://doi.org/10.1371/journal.pone.0323064
  - *锚定* — Wright & Augenstein 系统比较了把多标注者的软标签 (概率) 聚合成训练/评估目标的若干方案, 发现软标签聚合在分布偏移下比硬标签多数投票给出更好的不确定性估计。这直接对应本项目两条并排轨: prob 分组 (软概率映射) 与 llm 分组 (三家硬多数投票共识)。原文真实做的是 NLP 标注聚合方案的基准比较实验。
  - *迁移边界* — 原文标注者是人类众包工人 (crowd), 本项目是三家商用 LLM; 原文目标是分类器不确定性校准, 本项目是面板分母权重求和; 原文无银行-年聚合层、无跟风/媒体权威/提及密度权重维度; 原文语料为英文 NLP 基准集。
  - 〔Crossref 回读标题: Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift〕
  - 〔已接线家族 (5): F531, F539, F540, F544, F545〕
- 【2024–2026】Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for Regression with Variables Generated from Unstructured Data. SSRN Electronic Journal No. 4842086 [Working Paper]. https://doi.org/10.2139/ssrn.4842086
  - *锚定* — Battaglia-Christensen-Hansen-Sacher 建立了「先用文本/非结构化数据生成变量, 再把该变量放进回归」这一两步流程的推断理论, 证明朴素代入会产生偏误, 并给出偏误修正与有效标准误。本项目 sum_wd_* 族正是这一流程的分母侧: LLM 从新闻文本生成 llm_prob_score / llm_vote_score, 其有效性掩码决定哪些篇章进入加权求和。原文真实做的是理论推导 + 修正估计量, 未涉及权重方案。
  - *迁移边界* — 原文对象是回归中的生成型回归元/被解释变量本身, 本项目这里是「有效性掩码构成的权重分母」, 层级不同; 原文以英文非结构化语料 (含 embedding/topic) 为例, 无中文新闻、无银行-年面板、无三轨 (full/ctx/ss) 设定; 原文未处理多模型投票共识。
  - 〔Crossref 回读标题: Inference for Regression with Variables Generated from Unstructured Data〕
  - 〔已接线家族 (5): F531, F539, F540, F544, F545〕
- 【2024–2026】Zrnic, T., & Candès, E. J. (2024). Cross-prediction-powered inference. Proceedings of the National Academy of Sciences, 121(15), e2322083121. https://doi.org/10.1073/pnas.2322083121
  - *锚定* — Zrnic & Candès 提出 cross-prediction-powered inference: 当结果变量大部分由机器学习模型预测、仅少量有金标签时, 如何构造有效的置信区间。这与本项目 prob 分组 (llm_prob_score 非缺失掩码) 的构念同族 —— 概率映射的模型输出被当作测度并按权重聚合。原文真实做的是统计方法学 (估计量 + 覆盖率证明 + 模拟/实证演示), 属该测度族的前沿存在性与方法学参照。
  - *迁移边界* — 原文核心前提是存在一个金标准标注子样本用于去偏, 本项目 sum_wd_*_prob 分母无人工金标注子样本、亦不做去偏, 只做有效性掩码求和; 原文任务是推断置信区间, 本项目是构造面板分母列; 原文语料非中文新闻、非银行域。
  - 〔Crossref 回读标题: Cross-prediction-powered inference〕
  - 〔已接线家族 (1): F540〕


### 十补-12. 文本冗余 / 复用 / lazy prices / 年际连贯 (lazy_* / redund_* / coh_* / centroid_diff)

> 净增 12 条(其中 2024–2026 者 11 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (14): F065, F066, F072, F148, F149, F156, F157, F158, F361, F362, F363, F495, F501, F507

- 【2024–2026】Choi, I., Pinsonneault, A., & Han, K. (2026). IT investment differentiation, strategic distinctiveness, and firm performance. The Journal of Strategic Information Systems, 35(1), 101925. https://doi.org/10.1016/j.jsis.2025.101925
  - *锚定* — 原文 (JSIS 2026) 检验 IT 投资差异化、战略独特性与企业绩效的关系, 表明「相对同业的投资/战略偏离程度」在当代信息系统与战略文献中仍被作为有绩效含义的构念主动构造与使用。**仅作构念层面的前沿存在性佐证** (差异化得分是一个被持续使用、有经济含义的量), 不锚定任何算子。边界: 该文 Crossref/OpenAlex 均无公开摘要, 其差异化的具体操作化形式 (是否为距离均值) 未经回读证实, 定稿引用前须据正文核实; 原文差异化为单维连续财务/投资强度变量相对行业分布的偏离, **无 kNN 邻域限定 (与全行业比而非与最近 N 家比), 故不支撑本项目 N∈{10,20,40,50} 邻域梯子**, 亦无多维主题分布上的 Jensen-Shannon 距离; 国别/样本非中国银行, DV=企业绩效, 与本项目 outcome 不同。
  - 〔Crossref 回读标题: IT investment differentiation, strategic distinctiveness, and firm performance〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Dai, L., Gong, P., Jackson, A. B., & Peng, Z. (2026). Controlling the narrative: managers’ topic-shifting behavior in conference calls. Review of Accounting Studies, 31(2), 1165-1206. https://doi.org/10.1007/s11142-026-09952-5
  - *锚定* — 原文 (Review of Accounting Studies 2026, 电话会议样本 2002-2017) 以主题分析度量管理层回答偏离分析师提问主题的程度 (managerial topic-shifting), 发现业绩较好、CEO 权力较强、信息环境较弱的公司管理层转移更多, 且该转移行为向资本市场传递增量信息、促进盈余信息融入股价。对本项目 F156 (coh_lda = 1 − JSD(theta_{i,t}, theta_{i,t-1})) 是【表征空间层面】的前沿佐证: 顶刊层面确立『两个 LDA 主题分布之间的距离本身即为有实质经济含义的沟通行为测度, 而非噪声』, 支持本项目把主题分布距离作为标量测度落盘的做法。迁移边界: 原文的位移是同一场电话会议内问答之间的主题转移 (话轮层面、以提问主题为参照系), 本项目 F156 是同一银行相邻两年自身主题分布的距离 (年度层面、以自身上期为参照系), 时间尺度与参照系均不同; 原文未使用 Jensen-Shannon 距离; 语料为英文管理层发言, 本项目为中文第三方报道。原文无任何同业/行业质心参照物, 其构念是管理层回避而非战略差异化, 故【不】锚定 F148 (1−cos(theta_i, theta_bar_{-i}) 的 leave-one-out 同业质心差异化构念)。
  - 〔Crossref 回读标题: Controlling the narrative: managers’ topic-shifting behavior in conference calls〕
  - 〔已接线家族 (1): F156〕
- 【2024–2026】Li, F., Zhao, Z., & Cheng, H. (2026). Disclosure similarity and bond comovement. Pacific-Basin Finance Journal, 98, 103191. https://doi.org/10.1016/j.pacfin.2026.103191
  - *锚定* — 原文以中国上市公司 MD&A 的跨主体披露文本相似度为核心解释变量, 检验其对债券信用利差共动的预测力, 并发现相似披露预测未来违约距离 (DD) 的收敛, 契合『相似披露使投资者的违约风险评估趋同』; 效应在低评级债、承销商声誉较低、久期较长、分析师分歧大或负面媒体报道多的样本更强。是 2026 年「文本相似度作为主体间距离测度」的前沿存在性证明, 对 F148/F149 的构念 (以文本向量间距离刻画主体相对位置) 属同族, 且同为中国语境。迁移边界: 原文做的是两两 (pairwise) 相似度以解释共动, 本项目 F148/F149 是单个银行对 leave-one-out 同业质心 c_{-i}=(n·c̄−v_i)/(n−1) 的距离 (one-vs-centroid, 非 pairwise); 原文语料为公司自撰 MD&A 披露, 本项目为银行-年第三方新闻报道聚合文本; 原文 DV 为债券共动, 本项目不承接。原文无任何年际 (t, t-1) 自比构造, 故不锚定 F157/F158。
  - 〔Crossref 回读标题: Disclosure similarity and bond comovement〕
  - 〔已接线家族 (2): F148, F149〕
- 【2024–2026】Xiao, B., & Ma, H. (2026). How market openness, narrative distinctiveness, and innovation capability impact firm performance: A comparative study of Chinese and foreign platform enterprises in China. Journal of International Management, 32(3), 101354. https://doi.org/10.1016/j.intman.2026.101354
  - *锚定* — 原文在中国情境下把「叙事独特性」(narrative distinctiveness) 作为文本派生的构念纳入实证模型, 是本项目 centroid_diff 族「以文本刻画主体差异化」在中国语境的 2026 年同域应用。
  - *迁移边界* — 原文对象为平台企业, 不是银行; 其叙事独特性的具体算子与本项目的 1−cos(v_i, c_{-i}) leave-one-out 质心构造不同, 故只锚定构念不锚定公式; 原文 DV 为企业绩效, 本项目不承接; 语料为企业自述叙事而非第三方新闻报道。
  - 〔Crossref 回读标题: How market openness, narrative distinctiveness, and innovation capability impact firm performance: A comparative study of Chinese and foreign platform enterprises in China〕
  - 〔已接线家族 (2): F148, F149〕
- 【2024–2026】Kang, J., & Kang, Y. (2025). Capital Market Scrutiny and Strategic Distinctiveness of the Firm: Evidence from a Natural Experiment. British Journal of Management, 36(1), 461-476. https://doi.org/10.1111/1467-8551.12857
  - *锚定* — 原文以自然实验识别外部审视压力对企业战略独特性 (strategic distinctiveness) 的因果影响, 提供「企业相对同业的战略偏离度是一个可被外生冲击移动的、有内容的构念」的当代实证证据。可作为本桶 strat_diff / strat_sim_max 家族的构念存在性与经济含义锚点。
  - *迁移边界* — 原文的战略独特性=基于财务比率向量 (资本密度/广告研发强度等) 相对行业均值的马氏/标准化距离, **非文本相似度**, 更非 LDA 主题分布或嵌入空间距离; 单位=公司-年 (美国样本); 与本项目「媒体报道文本空间中的位置」在数据生成机制上完全不同 — 本条只锚构念, 不锚算子。
  - 〔Crossref 回读标题: Capital Market Scrutiny and Strategic Distinctiveness of the Firm: Evidence from a Natural Experiment〕
  - 〔已接线家族 (5): F148, F149, F495, F501, F507〕
- 【2024–2026】Lui, D., Moraru‐Arfire, A., & Tao, C. (2025). The Nexus of Corporate Disclosure and Investors’ Information Needs: An Analysis Using Topic Modeling. Journal of Business Finance & Accounting, 52(5), 2145-2174. https://doi.org/10.1111/jbfa.12857
  - *锚定* — 原文以 LDA 识别个人与机构投资者讨论的公司相关主题, 并与公司后续 MD&A 披露的主题内容比对, 发现投资者讨论某主题的文本占比与公司后续披露同一主题的文本占比正相关, 且公司显著更多地回应机构投资者 (而非个人投资者) 的信息需求。对本项目仅提供【弱构念层】佐证: 支持把 LDA 主题占比向量 (theta) 当作可在不同主体/来源之间比对的对象这一做法, 与 F148 (theta_i 对某参照 theta 的相对位置) 处于同一表征空间。⚠ 不得表述为距离测度先例 —— 原文实为逐主题的占比对占比关联回归, 从未把 theta 当向量计算余弦或 JSD 距离, 亦未产出任何标量距离落盘列; 亦不锚定 F156, 因原文无同一主体相邻年份自比构造。迁移边界: 原文比较的是『披露 vs 投资者信息需求』两类不同来源文本, 不是本项目的银行 vs 同业 leave-one-out 质心 (c_{-i}=(n·c̄−theta_i)/(n−1)); 语料语言与主体均不同 (英文披露/投资者讨论 vs 中文银行新闻)。
  - 〔Crossref 回读标题: The Nexus of Corporate Disclosure and Investors’ Information Needs: An Analysis Using Topic Modeling〕
  - 〔已接线家族 (1): F148〕
- 【2024–2026】Qi, D., & Chen, W. (2025). R&D narrative disclosure and semantic similarity: evidence from China. Economic Change and Restructuring, 58(5), 77. https://doi.org/10.1007/s10644-025-09915-x
  - *锚定* — 原文在中国语境对叙事性披露构造语义相似度测度, 是 2025 年中文文本相似度族的应用实例。对 F157/F158/F361 属同构念 (文本重合度) 的近期存在性佐证。
  - *迁移边界* — 原文用语义 (embedding) 相似度而非本项目的 TF-IDF 余弦或词集 Jaccard; 期刊层级低于顶刊; 原文对象为 R&D 叙事披露 (公司自撰), 本项目为银行新闻报道聚合文本; 原文未涉及本项目三轨 (full/ctx/ss) 口径。
  - 〔Crossref 回读标题: R&amp;D narrative disclosure and semantic similarity: evidence from China〕
  - 〔已接线家族 (1): F363〕
- 【2024–2026】Bestgen, Y. (2024). Measuring Lexical Diversity in Texts: The Twofold Length Problem. Language Learning, 74(3), 638-671. https://doi.org/10.1111/lang.12630
  - *锚定* — 原文是关于文本长度如何干扰词汇多样性测度的权威方法论综述 (基于三个英语学习者文本数据集), 系统批判常用指数并指出『双重长度问题』: 第一重是各类 type-token 比率类指数本身对文本长度的依赖; 第二重是——即便采用概率或算法方法把所有文本削减至等长从而解决了第一重——这些指数仍对『决定该等长长度的参数取值』高度敏感, 无一幸免。F072 的 1−(唯一汉字3-gram/全部汉字3-gram) 在数学上正是一个 (1 减) type-token 比率, 因此该文是 F072 已知长度偏倚的直接测度学依据, 同时说明为何须与 F065/F066 的长度列并置解读 (长度作为须显式呈现的混淆因子)。迁移边界: 原文在英文等字母语言的学习者语料上做词级 type-token 分析, 本项目 F072 是中文汉字 3-gram 级 (剔数字/标点/拉丁), 语言与 n-gram 阶数均不同; 原文未研究金融/新闻文本, 也未提出本项目采用的 mean-of-ln 长度聚合; 原文给出的等长削减类校正方法本项目并未实施——引用它是为诚实披露长度依赖 (并提示本项目未做校正), 不是主张本项目已解决该问题。
  - 〔Crossref 回读标题: Measuring Lexical Diversity in Texts: The Twofold Length Problem〕
  - 〔已接线家族 (3): F065, F066, F072〕
- 【2024–2026】Xu, D., Huang, J., Ren, X., & Ye, M. (2024). ESG report textual similarity and stock price synchronicity: Evidence from China. Pacific-Basin Finance Journal, 85, 102343. https://doi.org/10.1016/j.pacfin.2024.102343
  - *锚定* — 原文 (中国 A 股 2019-2021, 2,419 个公司-年 ESG 报告) 以两种算子度量 ESG 报告文本相似度 —— TF-IDF 余弦相似度与基于 LDA 主题模型的 JS 散度 —— 并发现相似度越高、股价同步性越高 (高相似文本不传递独特信息)。对本项目是「中文语料上以 TF-IDF 余弦 / LDA 主题分布散度度量文本区分度」这一测度族的 2024 年应用佐证, 锚定 F148/F149 (文本向量距离刻画主体区分度) 与 F156 (LDA 主题分布 JSD, 与原文同算子)。⚠ 须核: 原文相似度的比较基准 (跨公司 vs 公司自身上年) 未能从公开摘要/关键词证实, 正文核实前不得据以主张任何具体口径同族; 若确为跨公司, 则不支撑 F157/F158 的年际 (t, t-1) 口径。迁移边界: 原文未做 c_{-i}=(n·c̄−v_i)/(n−1) 的 leave-one-out 质心构造; 原文单位为上市公司-年的自撰 ESG 报告, 本项目为银行-年第三方新闻报道; 原文 DV 为股价同步性, 本项目不承接。
  - 〔Crossref 回读标题: ESG report textual similarity and stock price synchronicity: Evidence from China〕
  - 〔已接线家族 (2): F148, F149〕
- 【2024–2026】Xue, X., Wang, L., & Hu, N. (2024). Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China. The British Accounting Review, 56(5), 101305. https://doi.org/10.1016/j.bar.2023.101305
  - *锚定* — 原文 (中国上市公司 2009-2021) 基于制度理论检验经济政策不确定性对【公司自身跨期】CSR 披露相似度 (CSR time-series disclosure similarity, 即当年报告与自身以往报告的相似程度) 的影响, 发现 EPU 越高、企业越倾向发布与自身过往高度相似的 CSR 报告 (象征性行为); 该效应在国有企业减弱、在财务约束或亏损企业增强。对 F157/F158 (cos(v_{bank,t}, v_{bank,t-1}), 年际相邻期自比) 是构念完全对应的中文语境同域先例 —— 原文正是把『与自身上期文本高度重合』记录为一种可被外部环境驱动的实质性披露行为。迁移边界: 原文单位为上市公司-年的自撰 CSR 报告, 本项目为银行-年第三方新闻报道 (银行非文本作者, 象征性披露的主动选择机制不可直接搬用); 原文把相似度当被解释变量、由 EPU 驱动, 本项目 F157/F158 为面板自变量; 原文为纯时间序列自比, 无同业质心成分, 故不锚定 F148/F149。
  - 〔Crossref 回读标题: Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China〕
  - 〔已接线家族 (4): F157, F158, F362, F363〕
- 【2024–2026】Zhou, Y., Fan, J., & Xue, L. (2024). How Much Can Machines Learn Finance from Chinese Text Data? Management Science, 70(12), 8962-8987. https://doi.org/10.1287/mnsc.2022.01468
  - *锚定* — 原文提出 FarmPredict (因子增广 + 稀疏正则框架), 让模型直接从中文财经新闻中学习并预测股票收益, 结论是中文财经文本在词级/文本因子表示下确实携带可观的可学习信号 (正面情感日均 +83bp、负面 −26bp 超额收益, 简单策略年化最高 54%), 且优于其他统计与机器学习基准。对本项目仅提供【构念层】依据: 顶刊层面证实中文财经新闻文本经词级切分后的词袋类表示含有真实经济信息, 从而支持 F158 (jieba 词级 TF-IDF 向量) 这一表示路线在中文语境下并非无信息噪声。⚠ 不得据以主张原文为 TF-IDF 加权或 jieba 分词提供了效度校验 —— 恰相反, 原文的方法论卖点是【不依赖】预定义词典或预训练模型, 由模型自行抽取信息, 全文未评估 TF-IDF 权重方案, 亦未对本项目任何具体列做过校验。迁移边界: 原文目标为日频收益预测的机器学习管线, 不构造年际连贯 (F157/F158 的 t vs t-1)、不构造 leave-one-out 同业质心 (F149)、不涉及 char-ngram TF-IDF, 亦与文本长度列 (F065/F066) 无关; 原文单位为公司层面的中文财经新闻, 本项目为银行-年聚合报道。
  - 〔Crossref 回读标题: How Much Can Machines Learn Finance from Chinese Text Data?〕
  - 〔已接线家族 (1): F158〕
- Wang, Y., Ye, Q., Wang, J. J., & Wang, Y. (2023). Earnings manipulation and similarity of annual report disclosure: Evidence from China. Accounting & Finance, 63(S1), 1137-1156. https://doi.org/10.1111/acfi.13076
  - *锚定* — 原文在 2008-2020 年中国 A 股 13,679 家样本上, 以 MD&A 与上一年文本的相似度作为核心测度, 记录了「高相似度 = 低增量信息」的经验规律。是本项目年际连贯/lazy 族在中文语料上的同域先例 (中文分词后词袋相似度)。
  - *迁移边界* — 2023 年发表, 非 2024+; 原文是公司自撰年报 MD&A、单位公司-年, 本项目是银行-年新闻报道; 原文用相似度且解释为「操纵动机」, 本项目 F157/F158 为中性连贯性测度、F361 为距离 (补数), 不承接其操纵解释。
  - 〔Crossref 回读标题: Earnings manipulation and similarity of annual report disclosure: Evidence from China〕
  - 〔已接线家族 (5): F157, F158, F361, F362, F363〕


### 十补-13. 可读性 / 文本复杂度 / 具体性 / 硬信息 (hard_char / ttr / specificity / modal_weak / uncert)

> 净增 17 条(其中 2024–2026 者 17 条)。**已接线家族** (13): F045, F067, F068, F070, F073, F163, F365, F407, F409, F411, F436, F442, F600

- 【2024–2026】Kanner, A., & Mäkelä, E. (2026). The digital shift and syntactic complexity: Mean sentence length in Finnish news journalism. European Journal of Applied Linguistics. https://doi.org/10.1515/eujal-2025-0047
  - *锚定* — 该文在芬兰语新闻语料上以平均句长追踪句法复杂度的历时变化, 发现十年间句法复杂度上升约 20% 并降低了文本可及性; 与本项目在新闻文本上计算 avg_sentence_len 的语料类型同域, 是新闻文体句长测度的前沿存在性证明 (并佐证句长对文体/生产流程变迁敏感)。⚠ 原文语言=芬兰语, 句长以词计, 本项目以字符计且切句依赖句末标点规则; 分析单位=报刊/年代而非银行-年, 为描述性历时研究, 无经济学 DV; 原文不涉及文档长度/篇均词数, 不锚定 F073。
  - 〔Crossref 回读标题: The digital shift and syntactic complexity: Mean sentence length in Finnish news journalism〕
  - 〔已接线家族 (1): F067〕
- 【2024–2026】Sui, L., Woumans, E., Duyck, W., Boeve, S., & Dirix, N. (2026). The word and character frequency effect in Chinese natural reading. Reading and Writing, 39(5), 1877-1900. https://doi.org/10.1007/s11145-025-10681-5
  - *锚定* — 该文用自然阅读眼动实证检验中文『字频』与『词频』对阅读加工的独立效应, 直接支撑本项目 F045 的核心前提: 汉字层面的频次/常用性是中文文本阅读难度的可测量来源 (即『非常用字 = 难字』这一判定的认知基础)。
  - *迁移边界* — 原文是心理语言学眼动实验 (个体阅读加工时间为 DV), 非金融/媒体计量; 其字频来自中文阅读语料频次表, 而本项目难字判定基于 jieba 0.42.1 冻结词典的常用字集 _common_char_set (阈值口径不同, 且为二元集合判定而非连续频次)。原文不涉及 bank-year 聚合。
  - 〔Crossref 回读标题: The word and character frequency effect in Chinese natural reading〕
  - 〔已接线家族 (1): F045〕
- 【2024–2026】Yuan, D., Shen, J., & Li, Y. (2026). Annual report textual complexity and ESG rating disagreement. International Review of Economics & Finance, 110, 105609. https://doi.org/10.1016/j.iref.2026.105609
  - *锚定* — 该文把年报「文本复杂度」作为核心自变量解释 ESG 评级分歧, 说明文本复杂度族 (难度/长度/句法) 在 2026 年仍是活跃前沿构念, 且被作为年度面板级连续变量使用。
  - *迁移边界* — 原文为公司年报英文/中文披露文本的复杂度综合指标, 未逐项分解为难字占比、平均句长、ln 词数三个正交列; 本项目将其拆成 F045/F067/F409 三个独立家族并分 full/ctx/ss 三轨。国别与 DV 不同, 仅锚定构念族存在性。
  - 〔Crossref 回读标题: Annual report textual complexity and ESG rating disagreement〕
  - 〔已接线家族 (2): F045, F409〕
- 【2024–2026】Banerjee, P. (2025). Text-based multidimensional financial constraints and earnings management behaviour. Australian Journal of Management, 50(4), 1215-1266. https://doi.org/10.1177/03128962241270751
  - *锚定* — 该文用一个多维文本型融资约束测度 (区分股权市场约束与债务市场约束) 检验其与盈余管理的关系 (46,149 firm-year, 美国上市公司, 1997–2015); 本项目仅据此锚定『从披露文本中提取约束性语言以刻画融资约束』这一测度路线在当代仍活跃的**存在性参照**。⚠ 本文**不是** F163 的 method-origin: 本项目 constr_frac 计数的 LM 2011 constraining 子词典 (174 词) 源自 Bodnaruk, Loughran & McDonald (2015), 与本文的多维文本测度无谱系关系, 后者复杂度亦远高于单维词频型比率。层级为 firm-year vs 本项目 bank-year, 语料为公司自我披露 vs 第三方新闻报道, 国别与 DV 均不同。
  - 〔Crossref 回读标题: Text-based multidimensional financial constraints and earnings management behaviour〕
  - 〔已接线家族 (1): F163〕
- 【2024–2026】Cho, M., & Choi, A. (2025). Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone? Abacus, abac.70024. https://doi.org/10.1111/abac.70024
  - *锚定* — 该文同时把『媒体报道量 (coverage)』与『报道语调 (tone)』作为两个并列的公司-年媒体变量来解释审计投入, 与本项目把报道篇数 (ln_ft_articles/ln_nf_articles) 与语调 (log_sent) 分列为两族指标的做法同构, 属该建模范式的近期存在性证明。
  - *迁移边界* — 原文媒体覆盖计数基于英文商业新闻数据库的公司-年匹配, 语调为正负词占比类; 本项目计数基于中文媒体语料经 (target_bank, 标题, 日期) 去重, 且区分金科/非金科两类分子, 语调用 log1p(pos)-log1p(neg) 对数差分并有覆盖门控 NaN 规则。层级=firm-year vs bank-year, DV 不同。
  - 〔Crossref 回读标题: Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone?〕
  - 〔已接线家族 (2): F407, F411〕
- 【2024–2026】Fang, Y., Wang, F., & Dai, Z. (2025). A Zipfian Approach to Exploring Lexical Complexity Changes in Mandarin Chinese: A Corpus-Based Analysis of Word N-Grams. Journal of Quantitative Linguistics, 32(3), 251-278. https://doi.org/10.1080/09296174.2025.2483080
  - *锚定* — 该文在《人民日报》1946–2020 新闻语料上, 用 Zipf 律指数刻画现代汉语**词汇复杂度 (lexical complexity)** 的历时变化, 并证明该指数与其三个下位构念——词汇多样性 (lexical diversity)、词汇密度 (lexical density)、词汇成熟度 (lexical sophistication)——系统相关 (与前二者负相关、与后者正相关); 本项目据此锚定 F070 — 『词汇多样性可用频次-类型统计量刻画』这一测度路线的当代定量语言学依据, 且原文语料同为新闻文体 (与本项目新闻域同域, 优于跨域外推)。⚠ 原文分析单位为 word unigram/bigram, 无字级频次分析, 不得据本文支撑 F045 的字频稀有性判定; 其 Zipf 指数与本项目未做长度校正的原始 TTR 数学形式不同, 仅共享『频次-类型分布刻画复杂度』的方法论前提, 亦无 bank-year 面板层级。
  - 〔Crossref 回读标题: A Zipfian Approach to Exploring Lexical Complexity Changes in Mandarin Chinese: A Corpus-Based Analysis of Word
            <i>N</i>
            -Grams〕
  - 〔已接线家族 (1): F070〕
- 【2024–2026】Fu, Y., Liversedge, S. P., Bai, X., Moosa, M., & Zang, C. (2025). Word length and frequency effects in natural Chinese reading: Evidence for character representations in lexical identification. Quarterly Journal of Experimental Psychology, 78(7), 1438-1449. https://doi.org/10.1177/17470218241281798
  - *锚定* — 该文用控制笔画复杂度的眼动实验证明, 中文阅读中词长与词频独立影响词汇识别, 并提供了『字』作为词汇识别表征单位的证据; 本项目仅据此锚定 F045 的认知前提 — 汉字层面的频次/常用性是中文阅读加工难度的真实来源, 故『非常用字 = 难字』的字级判定有认知依据。⚠ 原文的『词长』指词内汉字数 (1 字词 vs 2 字词), 与本项目 F073 的篇均分词数 (文档长度) 是两个构念, 不得据本文为 F073 张目; 原文亦系实验室眼动研究 (DV=注视时间), 不涉及篇级统计量或机构-年聚合。
  - 〔Crossref 回读标题: Word length and frequency effects in natural Chinese reading: Evidence for character representations in lexical identification〕
  - 〔已接线家族 (1): F045〕
- 【2024–2026】Gounopoulos, D., Huang, W., & Yang, M. (2025). Innovation and annual report readability. Research Policy, 54(8), 105301. https://doi.org/10.1016/j.respol.2025.105301
  - *锚定* — 该文 (Research Policy) 检验企业创新与年报可读性之间的关联, 发现低可读性与创新绩效呈倒 U 型关系, 并以『维护竞争优势』与『隐藏风险』两条机制解释企业对披露文本复杂度的策略性调整; 本项目仅据此锚定『披露文本复杂度可测量且具经济含义』这一构念族在顶刊层面的存在性, 及其可读性构造同属难词/长度一类词汇-句法复杂度族。⚠ 原文中可读性主要处于解释变量位置、创新绩效为结果变量 (与本项目把文本复杂度列作银行-年自变量的用法方向一致), 不得据本文声称『可读性作为被解释变量』的设计先例。
  - 〔Crossref 回读标题: Innovation and annual report readability〕
  - 〔已接线家族 (4): F045, F073, F409, F436〕
- 【2024–2026】Lammers, F., & Pape, U. (2025). CEO Narcissism and Linguistic Complexity in Earnings Conference Calls. Accounting & Finance, 65(3), 3081-3106. https://doi.org/10.1111/acfi.70031
  - *锚定* — 该文检验 CEO 自恋对业绩说明会 Q&A 环节语言复杂度的影响, 把语言复杂度作为核心被解释变量, 发现自恋型 CEO 在印象管理动机下策略性降低语言复杂度; 本项目据此锚定『语言复杂度是金融沟通文本上可测量、可作为公司-年因变量、且被策略性操纵的构念』这一近期存在性证明。⚠ 原文摘要未披露其复杂度的具体算子, 故本项目**不据本文**主张『难度/句长/词汇多样性三类指标并列作为同一构念多个可观测面』的用法先例 (该并列做法的依据另见本桶 F067/F070 各自的定量语言学锚点); 原文语料=英文业绩说明会口语转写文本, 单位=call-level/firm-year, 本项目为中文书面新闻并把难字占比、平均句长、TTR 拆为三个独立且互不合并的家族 (禁混同一 Hansen J), 无 bank-year 三轨结构。
  - 〔Crossref 回读标题: CEO Narcissism and Linguistic Complexity in Earnings Conference Calls〕
  - 〔已接线家族 (1): F067〕
- 【2024–2026】Thäsler-Kordonouri, S., Thurman, N., Schwertberger, U., & Stalph, F. (2025). Too many numbers and worse word choice: Why readers find data-driven news articles produced with automation harder to understand. Journalism, 26(9), 1878-1898. https://doi.org/10.1177/14648849241262204
  - *锚定* — 该文用 3135 名读者的在线问卷实验检验自动化生产的数据新闻为何更难理解, 因子分析出五类影响读者评价的文章构成维度, 其中『数字特征 (numeric features)』『用词选择』『句子与段落长度』三类与本项目 F068/F045/F067 的构念指向一致, 且原文明确建议后编辑时『减少数字数量、解释读者不易理解的词』; 本项目据此锚定『新闻文本中的数字密度、用词难度与句长是与可理解性相关的构成性属性』这一同域 (新闻) 动机来源。⚠ 原文测量的是读者对上述维度的**主观感知评分** (survey experiment + 因子分析), **并未计算数词占比等文本统计量**, 故不得据本文声称数词密度测度的实现先例; 原文语料为英语/德语自动化新闻, DV 为读者理解度, 无机构-年聚合; 本项目 specificity_index 分子还含具名实体 (nr/ns/nt/nz) token 且分母为实词数, 与原文的数字感知口径不同; 原文结论方向 (数字多→更难懂) 与本项目把具体性视作硬信息的解读不等同。
  - 〔Crossref 回读标题: Too many numbers and worse word choice: Why readers find data-driven news articles produced with automation harder to understand〕
  - 〔已接线家族 (3): F045, F067, F068〕
- 【2024–2026】Zheng, W. (2025). Text length requirements for stable and genre-sensitive lexical diversity measurement. Cogent Arts & Humanities, 12(1), 2584418. https://doi.org/10.1080/23311983.2025.2584418
  - *锚定* — 该文用日语四文体语料 (政治演讲/自然会话/新闻/小说) 实证给出词汇多样性测量所需的最低文本长度门槛 (500 词以下高度不稳、1000–2000 词方趋稳定), 直接刻画本项目 F070 所用原始 TTR 对文本长度敏感这一已知测量学问题; 本项目据此**诚实披露 TTR 口径的局限**, 而非据其背书 TTR 的正确性。⚠ 原文语料为日语且以词计长度, 未涉及中文 jieba 分词与金融新闻; 其补救方案为设定最低文本长度门槛与采用长度校正型多样性指标 (如 Corrected/Root TTR、MTLD), 与本项目实际使用的未校正 TTR 不同; 原文**未**主张把文本长度作为同期控制变量与多样性指标并列入回归, 故不锚定 F073/F409。
  - 〔Crossref 回读标题: Text length requirements for stable and genre-sensitive lexical diversity measurement〕
  - 〔已接线家族 (1): F070〕
- 【2024–2026】Zhou, W., Xiong, Y., & Wang, S. (2025). Dialect diversity, corporate annual report text readability and stock price crash risks. Finance Research Letters, 86, 108622. https://doi.org/10.1016/j.frl.2025.108622
  - *锚定* — 该文在中国上市公司语境下构造中文年报文本可读性指标并检验其与股价崩盘风险的关系, 是「中文文本可读性可作为银行/企业层面年度面板变量」的同语境前沿存在性证明。
  - *迁移边界* — 原文测度对象=中文年报 (公司自我披露, 语体正式), 本项目=第三方媒体新闻报道; 原文可读性构造未必等同本项目的难字占比 (常用字集外汉字比) 与 ln(1+词数); 层级 firm-year vs bank-year, DV=崩盘风险而非本项目 DV。
  - 〔Crossref 回读标题: Dialect diversity, corporate annual report text readability and stock price crash risks〕
  - 〔已接线家族 (3): F045, F409, F436〕
- 【2024–2026】Zhou, Y., Jiang, J., & Liu, H. (2025). Language Universals in Sentence Length: Comparing Sentence Length Distributions of 10 Languages. Cognitive Science, 49(9), e70115. https://doi.org/10.1111/cogs.70115
  - *锚定* — 该文系统比较 10 种语言的句长分布, 论证句长作为跨语言可比语言统计量的分布规律, 直接支撑本项目把『篇均句长』当作稳定文本复杂度测度的前提 (含句长分布的重尾/量纲特征)。
  - *迁移边界* — 原文以词为句长单位并覆盖多语种通用语料; 本项目 avg_sentence_len 以『字符数/句数』计量中文新闻单篇, 单位不同 (字符 vs 词), 且再作 bank-year 篇间均值。原文无金融/银行层面应用。
  - 〔Crossref 回读标题: Language Universals in Sentence Length: Comparing Sentence Length Distributions of 10 Languages〕
  - 〔已接线家族 (1): F067〕
- 【2024–2026】Chen, X., & Kubát, M. (2024). Quantifying Syntactic Complexity in Czech Texts: An Analysis of Mean Dependency Distance and Average Sentence Length Across Genres. Journal of Quantitative Linguistics, 31(3), 260-273. https://doi.org/10.1080/09296174.2024.2370459
  - *锚定* — 该文显式把『平均句长』与依存距离并列作为句法复杂度的量化指标, 并检验其跨文体差异, 是 avg_sentence_len 作为句法复杂度代理这一 method 用法的当代定量语言学依据 (含其对文体的敏感性)。
  - *迁移边界* — 原文语言=捷克语, 句长以词计; 本项目=中文, 句长以字符计且切句依赖句末标点规则。原文分析单位是文体语料而非机构-年面板, 亦无三轨 (full/ctx/ss) 文本切分。
  - 〔Crossref 回读标题: Quantifying Syntactic Complexity in Czech Texts: An Analysis of Mean Dependency Distance and Average Sentence Length Across Genres〕
  - 〔已接线家族 (1): F067〕
- 【2024–2026】Elshandidy, T., & Elsayed, M. (2024). The UK financial firms’ textual risk disclosure and market liquidity. Finance Research Letters, 63, 105305. https://doi.org/10.1016/j.frl.2024.105305
  - *锚定* — 该文以英国 FTSE 全股金融业公司为样本, 首次检验基于文本的风险披露 (TRD) 与市场流动性的关系, 发现 TRD 降低金融公司市场流动性 (大型公司则相反), 表明金融机构的文本型风险披露对市场参与者具有信息含量; 本项目据此锚定 F600 — 金融机构文本中风险/不确定性类词频占比是可测量且具市场含义的属性。⚠ 原文语料=英国金融公司英文年报的风险披露段落, 词表为英文风险关键词表; 本项目在中文银行新闻上用中文迁移 LM 词表算比率并分 full/ctx/ss 三轨。原文 DV=市场流动性, 层级=firm-year, 与本项目不同。原文**不涉及**诉讼/法律语言子词表, 不锚定 F365。
  - 〔Crossref 回读标题: The UK financial firms’ textual risk disclosure and market liquidity〕
  - 〔已接线家族 (2): F442, F600〕
- 【2024–2026】Tucker, A. M., Xia, Y., & Smelcer, S. N. (2024). Text, tone, and legal language: Analyzing mutual fund disclosure sentiment. American Business Law Journal, 61(1), 57-86. https://doi.org/10.1111/ablj.12239
  - *锚定* — 该文显式分析共同基金披露文本中的『法律语言 (legal language)』及其在设定整体披露语调中的作用, 并自建定制词典对 164,602 份基金简明招募说明书 (2010–2020) 生成句级/文档级语调分数; 本项目据此锚定 F365 (litigious 类法律语言词表计数近年被独立作为文本属性研究的存在性证明) 与 F411 (语调构造属正负词计数族, 与 log_sent 的正负计数底盘同源)。⚠ 原文为英文共同基金披露文件, 法律语言识别依赖英文 LM litigious 表及法律语料; 本项目 litig_frac 用中文迁移词表在新闻文本上计数, 分母为剔除纯数字与标点后的真词数。原文语调未采用 log1p(pos)−log1p(neg) 的对数差分形式, 亦无三轨与银行-年聚合。原文**不涉及**弱势模态词分析, 不锚定 F442。
  - 〔Crossref 回读标题: Text, tone, and legal language: Analyzing mutual fund disclosure sentiment〕
  - 〔已接线家族 (2): F365, F411〕
- 【2024–2026】Wang, Z., Xu, H., & Liu, K. (2024). Lexical Complexity in Corporate Communication: A Corpus-Based Study of Translated and Non-Translated Chairman’s Statements. Corpus-based Studies across Humanities, 2(2), 265-284. https://doi.org/10.1515/csh-2024-0026
  - *锚定* — 该文用语料库方法对比翻译与非翻译董事长致辞的词汇复杂度, 显式采用 TTR 及其变体 (Corrected/Root/Bi-logarithmic TTR)、NDW、词汇密度与动词复杂度等指标族; 本项目仅据此锚定 F070 — 『把词汇多样性 (型例比) 类指标施加于企业沟通/年报类金融文本』的方法先例存在性。⚠ 重要更正: 原文语料为**英文**董事长致辞 (中译英译文 + 美国/香港原生英文), **非中文文本**, 不得据本文声称中文金融文本上的同语境先例, 亦不得支撑依赖汉字常用字集的 F045; 其 NDW 为词型数 (多样性) 而非文档长度, 不支撑 F073。原文系描述性对比研究 (翻译 vs 非翻译), 无因果计量与面板结构, 文本类型为公司自述致辞而非第三方新闻报道。
  - 〔Crossref 回读标题: Lexical Complexity in Corporate Communication: A Corpus-Based Study of Translated and Non-Translated Chairman’s Statements〕
  - 〔已接线家族 (1): F070〕


### 十补-14. 战略差异化 top-k 最近邻 (strat_diff_n{10..50}_{emb,lda} / strat_fluidity / strat_sim_max)

> 净增 10 条(其中 2024–2026 者 10 条; **4 条未接入任何家族**, 见各条标注)。**已接线家族** (9): F495, F497, F500, F501, F502, F503, F506, F507, F509

- 【2024–2026】Cuypers, I. R., Ertug, G., Noorderhaven, N. G., & Kavusan, K. (2026). The distinctiveness effect: How cross-country dissimilarities influence governance decisions. Strategic Organization, 24(1), 170-205. https://doi.org/10.1177/14761270241254756
  - *锚定* — 原文以 21,951 起跨境非股权联盟与股权合资为样本, 将「相异度 (dissimilarity)」显式操作化为治理结构选择的驱动变量, 并发现语言、宗教、文化等不同维度的相异度并非独立作用、而是彼此负向调节。据此**仅**锚定一个泛构念前提: 主体相对参照物的相异/相似程度是有经济含义、可驱动决策的量, 且相异度的维度界定会影响其效应 —— 支撑本项目输出 strat_sim_max 一类相似度极值测度的构念合法性。边界: **原文的「多维相异度」指语言/宗教/文化等实质不同的构念之间的交互, 并非同一构念在不同向量空间中的测度稳健性 —— 不构成 TF-IDF 轨与 LDA 主题轨并排互稳做法的依据**; 原文相异度=Hofstede 式预定义跨国维度距离, 非从文本估计的主题分布或 TF-IDF 向量, 无 Jensen-Shannon 距离; 单位=跨国治理决策, 非银行-年; 原文取成对距离, 不取同业集合内的 max。
  - 〔Crossref 回读标题: The distinctiveness effect: How cross-country dissimilarities influence governance decisions〕
  - 〔已接线家族 (1): F507〕
- 【2024–2026】Fang, B., Saiy, S., & Vyas, D. (2025). Industry Peer Information and the Equity Valuation Accuracy of Firms Emerging from Chapter 11. Management Science, 71(2), 1692-1715. https://doi.org/10.1287/mnsc.2022.01233
  - *锚定* — 原文以 Chapter 11 重整企业为样本, 发现可得的行业同业信息越充分、质量越高, 权益估值误差越小, 且显著减少索赔人之间的非预期财富转移。据此可锚定一个较弱但真实的前提: **同业信息本身对下游经济量有实质影响, 故「以谁作为同业」不是无关紧要的技术细节**。边界: **原文的处理变量是同业信息的可得性与质量, 而非同业集合的构成方式或规模 —— 原文既未变动同业集合的界定规则, 也未做任何邻域基数的敏感性检验, 因此不构成本项目 N∈{40,50} 邻域宽度并排稳健性臂的必要性论证**; 原文同业按行业代码/可比公司规则界定, 非嵌入余弦相似度 top-k 检索; 场景=美国破产重整企业权益估值, 与银行-年度媒体文本空间无关; 原文不构造任何差异化得分。
  - 〔Crossref 回读标题: Industry Peer Information and the Equity Valuation Accuracy of Firms Emerging from Chapter 11〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Li, N. (2025). Labor market peer firms: understanding firms’ labor market linkages through employees’ internet “also viewed” firms. Review of Accounting Studies, 30(1), 384-435. https://doi.org/10.1007/s11142-024-09821-z
  - *锚定* — 原文构造了一套不依赖 SIC/GICS 的同业集合 (由员工在 LinkedIn/Glassdoor 上「也浏览了」的共现关系导出), 并实证证明该数据驱动 peer 集合与传统行业分组仅部分重叠、且在解释股票收益与会计业绩共动上具有增量解释力, 捕捉了行业代码遗漏的企业间联结。据此锚定本项目 strat_diff_n{40,50}_emb 的核心设计前提: 同业集合由文本/嵌入相似度检索给定, 而非由行业代码外生指定, 是有前沿依据的做法。边界: 原文 peer 集合来源=浏览行为网络共现, 非文本嵌入余弦相似度; 国别=美国上市公司; 单位=公司-年; 分析目标=劳动力市场联结与会计信息迁移, **不构造任何差异化得分 (无 mean_{j∈kNN}(1−cos) 一类算子), 亦不取 peer 集合内的极值**。
  - 〔Crossref 回读标题: Labor market peer firms: understanding firms’ labor market linkages through employees’ internet “also viewed” firms〕
  - 〔已接线家族 (2): F500, F502〕
- 【2024–2026】Phillips, D., Edwards, B. D., & Rutherford, M. W. (2025). Conformity or Differentiation: Optimal distinctiveness through mediating channels. Journal of Business Research, 189, 115154. https://doi.org/10.1016/j.jbusres.2024.115154
  - *锚定* — 原文在新创企业命名情境下检验「趋同 vs 差异化」的张力, 并提出二者可经由认知中介机制**同时**带来合法性 (而非单纯此消彼长), 表明主体相对同业的定位选择本身是有辨识度的分析对象。据此**仅**锚定 strat_sim_max / strat_sim_max_lda 所刻画的「与最相似同业的接近程度」这一构念的理论张力 (趋同带来合法性 vs 差异化带来区隔)。边界: **原文的处理对象是新创企业名称的静态命名选择, DV 为合法性知觉 —— 全文无跨期成分、无「同行位置随时间移动」的度量, 因此不支撑 strat_fluidity 的动态侵蚀构念**; 未构造 Hoberg-Phillips-Prabhala (2014) Eq.2 式的市场变化向量 cos(N_it, Σ|N_jt−N_j,t−1|), 亦未使用任何文本向量; 单位与语境非银行、非中文新闻。fluidity 算子出处仍是既在池的 HPP (2014)。
  - 〔Crossref 回读标题: Conformity or Differentiation: Optimal distinctiveness through mediating channels〕
  - 〔已接线家族 (2): F507, F509〕
- 【2024–2026】Shen, R., Zhang, H., Zhong, W., & Lu, J. (2025). Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms. Strategic Entrepreneurship Journal, 19(1), 171-195. https://doi.org/10.1002/sej.1521
  - *锚定* — 原文在中国某天使投资平台 3266 份商业计划书上, 把同一创业企业相对两个不同参照物 (在位企业 / 同台同类创业企业) 分别计算独特性, 发现二者对投资人评价的作用方向不同且互相调节, 从而证明「独特性相对于谁而言」的参照物界定会实质改变独特性的经济含义。据此可锚定本项目 LDA kNN 差异化得分族「参照集 (邻域) 的界定不是中性技术选择、须被显式披露与检验」这一设计前提。**原文未变动参照集的规模/宽窄, 不构成 N∈{10,20,40,50} 邻域宽度梯子的直接依据**; 亦未提出 kNN 算子、未用 LDA 主题分布或 JSD 距离。原文层级=创业企业, 非银行-年度; 语料=中文商业计划书 (非本项目的第三方中文新闻报道), 参照集由平台类别/投资人视角离散界定, 非连续文本向量空间检索。
  - 〔Crossref 回读标题: Distinctiveness from whom? Evaluation of startups' distinctiveness from multiple referents in angel investment platforms〕
  - 〔已接线家族 (4): F495, F497, F501, F503〕
- 【2024–2026】Sun, Z., Zhang, R., & Li, Y. (2025). Corporate strategy uniqueness and cash holdings. Financial Review, 60(4), 1129-1160. https://doi.org/10.1111/fire.12442
  - *锚定* — 该文 (已正式发表于 Financial Review) 以「公司战略独特性」为核心解释变量, 检验其与现金持有的关系, 锚定的是**战略独特性作为一个可测度、且对公司财务政策有解释力的构念**这一前提, 与本项目 strat_diff 族「用文本/嵌入距离刻画银行策略与同业的偏离度」共享同一构念家族。⚠ 严格边界与举证缺口: 该文摘要在 Crossref/OpenAlex 均不可得, 其独特性的**操作化形式**与样本国别**未经回读证实**, 故本条仅在构念层成立, **不得**据以主张其独特性测度与本项目的kNN 邻域/余弦距离/JSD 同构 (原文未见任何文本或嵌入距离构造); 其 DV 为现金持有, 非本项目任何 outcome。
  - 〔Crossref 回读标题: Corporate strategy uniqueness and cash holdings〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Wang, Q., Xiang, C., Xin, Z., & Li, C. (2025). The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China. Emerging Markets Finance and Trade, 61(11), 3595-3611. https://doi.org/10.1080/1540496x.2025.2479064
  - *锚定* — 原文在中国上市公司样本上, 以产品文本相似度 (Hoberg-Phillips 式) 定义同业集合, 并据此识别同业间影响。可锚定「文本相似度定义的同业集合在中国语境下可用且有解释力」这一应用同域证据 — 本项目的 strat_diff_n{40,50}_emb 与 strat_sim_max 同样在中国语境下以文本相似度定义同业。
  - *迁移边界* — 原文语料=上市公司年报产品描述文本 (公司自述), 本项目语料=第三方媒体新闻报道 (他述), 文本生成过程与选择性偏误不同; 原文向量化=TF-IDF 词频空间, 非本项目的 Qwen3/text-embedding-3 神经嵌入; 原文样本=全行业上市公司, 本项目=银行; 且原文取同业集合做 peer effect 回归, 不取 mean 余弦距离作差异化得分。
  - 〔Crossref 回读标题: The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China〕
  - 〔已接线家族 (4): F500, F502, F506, F507〕
- 【2024–2026】Jin, Z., & Li, F. W. (2024). Scope Similarity and Cross-Firm Return Predictability. SSRN Electronic Journal No. 5016418 [Working Paper]. https://doi.org/10.2139/ssrn.5016418
  - *锚定* — 该 SSRN 工作论文 (2024, **未经同行评议**) 以 Hoberg & Phillips (2024) 的企业业务范围 (scope) 度量构造基于范围相似度的跨企业连结, 发现 scope peers 间基本面与股票收益强共动且超越传统行业边界, 并因投资者注意力不足产生可预测收益。据此锚定本项目「以文本相似度检索出的同业集合能捕捉行业代码之外的真实企业连结」这一设计前提 (F500/F502)。边界: 工作论文, 结论可能变动; 原文文本=公司自述业务范围披露 (10-K), 非第三方新闻报道; 相似度用于构造 peer 收益预测信号, **既不取 (1−cos) 均值作差异化得分, 也不取相似度矩阵行最大值 —— 不构成 strat_sim_max 的先例**; 国别=美国; 未涉及 LDA/JSD 轨。
  - 〔Crossref 回读标题: Scope Similarity and Cross-Firm Return Predictability〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Mochkabadi, K., Kleinert, S., Urbig, D., & Volkmann, C. (2024). From distinctiveness to optimal distinctiveness: External endorsements, innovativeness and new venture funding. Journal of Business Venturing, 39(1), 106340. https://doi.org/10.1016/j.jbusvent.2023.106340
  - *锚定* — 原文以股权型与回报型众筹的四项研究 (观察数据 + 实验) 检验独特性/创新性与资源获取的非单调关系, 发现无创新与激进创新的新创企业均被视为合法性较低、渐进创新最具吸引力, 且外部背书会随受众类型 (求回报 vs 求新奇) 移动最优独特性水平。据此锚定本项目的测度层设计立场: **独特性得分本身不预设线性的好/坏方向, 应原样输出、把方向与非线性留给下游回归识别** (F495 及差异化得分族)。边界: 原文层级=新创企业融资, 与银行-年度媒体报道无对应; 其独特性/创新性的具体编码方式未经回读证实 (摘要仅显示核心自变量为 innovativeness); **原文机制为外部背书与受众类型, 全文无同业动态、无 kNN 邻域、无 JSD、无 fluidity 变化向量 —— 不支撑 strat_fluidity 家族**。
  - 〔Crossref 回读标题: From distinctiveness to optimal distinctiveness: External endorsements, innovativeness and new venture funding〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Vamvourellis, D., Tóth, M., Bhagat, S., Desai, D., Mehta, D., & Pasquali, S. (2024). Company Similarity Using Large Language Models. 2024 IEEE Symposium on Computational Intelligence for Financial Engineering and Economics (CIFEr), 1-9. https://doi.org/10.1109/cifer62890.2024.10772990
  - *锚定* — 原文用 LLM 从企业业务描述学习公司嵌入, 并以嵌入余弦相似度重建 GICS 行业分类作为效度检验, 证明「神经嵌入空间中的公司余弦相似度确实承载行业/业务可比性信息」。这是本项目 _emb 轨 (strat_diff_n{40,50}_emb 用 1−cos(v_i,v_j)) 所依赖的核心前提的方法学效度证据 — 严格说是嵌入相似度的构念效度证明, 而非本项目算子的出处。
  - *迁移边界* — 原文语料=SEC 备案的英文业务描述, 本项目=中文新闻报道且按银行-年度聚合成超级文档; 原文嵌入模型为其自训/微调 LLM, 非本项目的 Qwen3-Embedding-8B / text-embedding-3-large; 原文效度标尺=GICS 复现, 本项目无行业分类标尺可比; 且原文止于相似度检索, 未取 top-N 距离均值作差异化得分。, 收入理由是它是嵌入-公司相似度效度的可引前沿基准, 本桶该环节在池内无对应条目。
  - 〔Crossref 回读标题: Company Similarity Using Large Language Models〕
  - 〔已接线家族 (2): F500, F502〕


### 十补-15. 采纳强度分位阈值梯子 (hidden / subst / token _adopt_{int,kw}_p{25,50,75})

> 净增 13 条(其中 2024–2026 者 13 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (27): F195, F327, F328, F331, F332, F333, F334, F335, F336, F337, F338, F512, F513, F515, F516, F517, F521, F552, F553, F555, F556, F557, F558, F559, F560, F561, F562

- 【2024–2026】Chen, F., Wang, W., & Xu, M. (2026). Symbolic versus substantive compliance from a dual legitimacy perspective: evidence from Chinese firms’ overseas violations. Chinese Management Studies, 1-29. https://doi.org/10.1108/cms-01-2025-0009
  - *锚定* — 原文在中国企业语境下以双重合法性视角区分「象征性合规」与「实质性合规」并做实证检验 (2009-2022 中国上市公司海外违规样本, 分层回归 + bootstrap), 为本桶 **token 象限 (象征式回应政策)** 在中国制度环境中的构念适用性提供 2026 年锚点。⚠ 仅锚定 token(及与之对举的实质格)构念, **不锚定 hidden 象限**: 原文未刻画「实质落实但低声量」的静默型态, 该格无原文对应物。
  - 〔Crossref 回读标题: Symbolic versus substantive compliance from a dual legitimacy perspective: evidence from Chinese firms’ overseas violations〕
  - 〔已接线家族 (1): F558〕
- 【2024–2026】Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F. (2026). Measuring policy diffusion intensity: A text-driven analysis of government documents. Information Processing & Management, 63(2), 104383. https://doi.org/10.1016/j.ipm.2025.104383
  - *锚定* — 原文以政府文件文本为基础构造政策扩散强度的文本驱动测度, 属「用政策文本相似度/强度刻画政策对齐程度」这一方法族的近期前沿。本桶所有象限的 sim 维 (policy_cosine_sim / policy_cosine_sim_allv) 正是同族测度, 该文为其提供 2026 年方法学存在性锚点。
  - *迁移边界* — 原文测的是政策文件之间的扩散强度 (政府—政府层级), 而本项目是新闻报道文本对政策锚点的余弦相似度 (媒体—政策层级); 原文不做二值象限分类, 不设年度分位阈值, 也没有 _allv 全年份静态锚点 vs 逐年滚动锚点的对照设计。
  - 〔Crossref 回读标题: Measuring policy diffusion intensity: A text-driven analysis of government documents〕
  - 〔已接线家族 (6): F328, F332, F334, F336, F552, F556〕
- 【2024–2026】Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
  - *锚定* — 原文专门刻画中国企业「多行动少言说 (more action-less talk)」的创新披露沉默型态, 即实质投入高但文本声量低的一格。这恰是本桶 hidden 象限 (词频/强度低于年度分位、政策相似度不低于年度分位) 的构念对应物, 为「低声量高实质」作为独立可测型态提供 2026 年中国语境的前沿存在性证据。
  - *迁移边界* — 原文测的是企业年报创新披露与商业信用融资的关系, 层级为上市公司-年, 沉默的定义来自披露文本与专利/研发的落差, 而非本项目的「新闻金科词频 < 年度分位 AND 政策余弦 >= 年度分位」双分位判据; 原文亦无三轨文本与 P25/P50/P75 阈值梯子。
  - 〔Crossref 回读标题: Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China〕
  - 〔已接线家族 (6): F327, F331, F333, F335, F336, F337〕
- 【2024–2026】Ge, X., & Luo, Q. (2026). Greenwashing in green mutual funds: Symbolic ESG vs. substantive carbon emissions. Global Finance Journal, 72, 101305. https://doi.org/10.1016/j.gfj.2026.101305
  - *锚定* — 原文把「象征性 ESG (声明/评级层面)」与「实质性碳排放 (真实结果层面)」并列对照以识别绿色基金的洗绿, 即把象征维与实质维分别测量后交叉比对。这与本桶 token 象限 (声量高但政策对齐低) 的识别逻辑同构, 属该测度族 2026 年前沿。
  - *迁移边界* — 原文对象是绿色共同基金, 层级为基金-期; 象征维用 ESG 声明/评级、实质维用组合碳排放, 均非文本测度, 且不使用年度分位阈值把两维二值化成 2×2 象限; 本项目为中国银行-年的新闻文本双维分位象限。
  - 〔Crossref 回读标题: Greenwashing in green mutual funds: Symbolic ESG vs. substantive carbon emissions〕
  - 〔已接线家族 (4): F516, F517, F556, F562〕
- 【2024–2026】Hellsmark, H., Andersson, J., & Hedeler, B. (2026). Beyond leaders and laggards: How incumbents navigate transformative policy missions. Energy Policy, 212, 115147. https://doi.org/10.1016/j.enpol.2026.115147
  - *锚定* — 原文明确质疑把在位者简单归为「领先者/落后者」二分的做法, 论证该二分会掩盖在位者应对转型政策的异质路径。F195 digital_frontier 正是按基年组内中位数把银行切成前沿/非前沿两组的二值分组哑变量, 该文为这一分组的边界与局限提供 2026 年的直接批评性锚点。
  - *迁移边界* — 原文是能源转型政策语境下对在位企业的定性/概念研究, 非银行业、非新闻文本, 也没有构造中位数切分的量化哑变量或跨年固定 broadcast 的组员资格; 它只支持「领先/落后二分需谨慎」这一判断, 不能作为 F195 具体阈值 (基年组内中位数、零覆盖记 0) 的方法出处。
  - 〔Crossref 回读标题: Beyond leaders and laggards: How incumbents navigate transformative policy missions〕
  - 〔已接线家族 (1): F195〕
- 【2024–2026】Pan, Y., Xue, F., & Liu, L. (2026). Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing. Information Technology and Management. https://doi.org/10.1007/s10799-026-00501-9
  - *锚定* — 原文把技术采纳明确二分为「符号性采纳 (symbolic adoption)」与「实质性行动 (substantive action)」, 并把两者的背离操作化为 AI washing 加以实证测量。这是本桶 token(高声量·低对齐) 与 subst(双高) 两象限所依赖的「同一构念拆成两维并置」做法在 2026 年的前沿存在性证明。
  - *迁移边界* — 原文对象是企业 AI 叙事与实际行动, 主体为一般企业而非银行; 其符号/实质二分基于组织冗余与披露数据, 不使用政策文本余弦相似度, 也不做年度分位阈值切分; 层级为企业, 本项目为银行-年且分母为已测量报道篇数。
  - 〔Crossref 回读标题: Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing〕
  - 〔已接线家族 (5): F512, F516, F552, F553, F555〕
- 【2024–2026】Portugal, M. A. (2026). Integrity for English Eyes Only? Evidence of Means‐Ends Decoupling in Brazilian Corporate Compliance. Regulation & Governance, rego.70164. https://doi.org/10.1111/rego.70164
  - *锚定* — 原文以巴西 2013 年反腐败法 (Law No. 12.846/2013) 后的合规整固为对象, 用行政投诉登记数据 (National Registry of Substantiated Complaints, 2009-2024) 与准实验设计 (间断时间序列 + 聚类稳健 logistic 回归 + 固定效应, 辅以事件研究与平衡的重复出现企业面板稳健性检验), 发现法后无结构性断裂且冲突解决概率显著下降 (OR=0.941, 95% CI 0.909-0.974), 即合规在形式上铺开却未转化为治理效果 —— 为 means-ends decoupling 提供监管治理领域的定量经验证据。就本桶而言, 仅锚定 **token 象限**「形式/声量到位但实质对齐不足」这一格的存在性。迁移边界: 语境为巴西企业合规而非中国银行业金融科技报道; 其脱耦由行政投诉结果指标识别, **不使用任何文本测度**, 不构造分位阈值二值指标, 层级与 DV 均与本项目不同; 亦不锚定 hidden 象限 (原文无「低声量高实质」型态)。
  - 〔Crossref 回读标题: Integrity for English Eyes Only? Evidence of Means‐Ends Decoupling in
                    <scp>B</scp>
                    razilian Corporate Compliance〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Xu, F. (2026). Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks. SSRN No. 6922688 [Working Paper]. https://doi.org/10.2139/ssrn.6922688
  - *锚定* — 该工作论文用文本方法构造银行层面的 FinTech intensity 指标并检验其与经营绩效的关系, 与本桶各 int-轨象限所用的 fintech_intensity_score (银行-报道层面的金科强度) 属同一测度族, 是「银行层面文本金科强度」在 2026 年的同域应用存在性证据。
  - *迁移边界* — 原文样本为欧洲银行, 文本来源为银行自身披露/年报而非第三方中文新闻; 其 intensity 为连续指标直接进回归, 不做年度分位二值化, 更无与政策文本相似度交叉形成 2×2 象限; 属未经同行评审的 SSRN 工作论文, 结论稳健性未定。
  - 〔Crossref 回读标题: Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks〕
  - 〔已接线家族 (5): F512, F515, F516, F553, F555〕
- 【2024–2026】Athanasopoulou, A., Marti, E., Risi, D., & Schlindwein, E. (2025). How Companies Restrain Means–Ends Decoupling: A Comparative Case Study of CSR Implementation. Journal of Management Studies, 62(1), 214-245. https://doi.org/10.1111/joms.13043
  - *锚定* — 原文比较案例研究企业如何抑制 means-ends decoupling, 即在何种条件下形式采纳能真正转化为实质结果。这为本桶 subst 象限 (政策对齐与金科强度双双高于年度分位, 即「形式与实质同时到位」) 的构念合法性提供 2025 年顶刊管理学锚点。
  - *迁移边界* — 原文为比较案例定性研究, 无量化指标、无阈值切分、无面板; 场域为 CSR 实施而非银行金融科技; 只能锚定「双高格=抑制脱耦」这一构念解释, 不能作为本项目分位判据或聚合口径的方法学来源。
  - 〔Crossref 回读标题: How Companies Restrain Means–Ends Decoupling: A Comparative Case Study of CSR Implementation〕
  - 〔已接线家族 (3): F513, F517, F521〕
- 【2024–2026】Bauer, R., Broeders, D., & van Ool, A. (2025). Walk the green talk? A textual analysis of pension funds' disclosures of sustainable investing. Journal of Pension Economics and Finance, 24(2), 297-325. https://doi.org/10.1017/s147474722400009x
  - *锚定* — 原文用 NLP 文本分析对荷兰养老金年报披露同时构造「意识 (awareness, 声量维)」与「落实 (implementation, 具体性/实质维)」两个**均取自同一披露文本**的测度, 并检验基金规模与签署可持续投资倡议对二者的差异化影响 (发现签署提升表述具体性、但对 implementation 无效)。它为本桶「在同一文本内并置声量维与实质/对齐维、再交叉构造 token/hidden 象限」的做法提供文本计量层面的前沿实践 —— 与本项目同属「两维皆在文本内、无外部行为验证」的设计, 而非言—行外部对照。迁移边界: 原文分析机构自述文本 (年报披露), 本项目分析第三方新闻报道; 原文实质维为披露具体性 (NLP 抽取), 本项目实质维为政策锚点余弦相似度; 原文不做分位阈值二值化、无 2×2 象限、无面板聚合与已测量分母口径。
  - 〔Crossref 回读标题: Walk the green talk? A textual analysis of pension funds' disclosures of sustainable investing〕
  - 〔已接线家族 (4): F337, F338, F560, F562〕
- 【2024–2026】Hemelstrand, S., & Inoue, T. (2025). Stop splitting hairs: The problems with dichotomizing continuous data in language research. Research Methods in Applied Linguistics, 4(3), 100272. https://doi.org/10.1016/j.rmal.2025.100272
  - *锚定* — 原文用三组模拟系统论证把连续变量二分的方法学代价: 二分几乎普遍抬高标准误, 进而导致显著性检验失准, 且因信息量削减而使 R² 等效应量被压低; 其立场是**建议不要二分**连续数据 (题即 'Stop splitting hairs')。本桶把连续的 policy_cosine_sim 与 fintech_intensity_score 按年度 P25/P50/P75 二值化、以及 F195 按基年组内中位数切分, 正是该文所告诫的做法, 故引作**必须直面的反向方法学告诫锚点** (披露代价、并说明为何仍采用象限设计)。⚠ 该文**不**为 P25/P50/P75 三级阈值梯子背书: 原文未提出「若必须二分则做多切点敏感性检验」的补救建议, 阈值梯子属本项目自设的稳健性措施, 不得援引该文作为其正当性依据。迁移边界: 领域为应用语言学研究方法, 非金融/经济学; 论证针对单变量二分对回归推断的影响, 未涉及双变量交叉的 2×2 象限、逐年滚动分位阈值、面板聚合与已测量分母口径。
  - 〔Crossref 回读标题: Stop splitting hairs: The problems with dichotomizing continuous data in language research〕
  - 〔已接线家族 (6): F195, F327, F331, F336, F512, F516〕
- 【2024–2026】Kaufmann, L., Krlev, G., & Brown, M. (. (2025). In Plain Sight: Mechanisms of means–ends decoupling in impact investing. Organization Studies, 46(5), 667-692. https://doi.org/10.1177/01708406241295505
  - *锚定* — 原文以影响力投资为田野, 系统刻画 means-ends decoupling (政策/实践在形式上落地但与目标脱节) 的具体机制, 是本桶「形式对齐 vs 实质产出」二维象限背后的制度理论近期前沿; 为 subst 与 token 两格的理论区分提供 2025 年顶刊组织学依据。
  - *迁移边界* — 原文为定性/机制研究, 不构造任何数值指标, 更无分位阈值二值化或 bank-year 聚合; 场域是影响力投资机构而非中国银行业; 其 means-ends 概念与本项目「政策余弦 × 金科强度」的操作化只是理论对应, 非同一测量。
  - 〔Crossref 回读标题: In Plain Sight: Mechanisms of means–ends decoupling in impact investing〕
  - 〔已接线家族 (4): F512, F515, F553, F556〕
- 【2024–2026】Liu, Y., Wang, J., Wen, F., & Wu, C. (2024). Corporate responses to systemic risk: Talk and action. Pacific-Basin Finance Journal, 87, 102493. https://doi.org/10.1016/j.pacfin.2024.102493
  - *锚定* — 原文将企业对系统性风险的回应拆为 talk (文本表述强度) 与 action (实际举措) 两条可分别测量的维度并检验二者关系, 与本桶用「词频高低」×「政策对齐高低」构造 token / hidden 象限属同一「言—行两维并置」测度族。
  - *迁移边界* — 原文是企业层面对系统性风险的回应, 非银行金融科技采纳; talk 用披露文本、action 用财务/公司行为代理, 而本项目两维均来自新闻文本 (词频 vs 政策余弦), 且不含年度分位阈值梯子与 bank-year 篇均占比聚合。
  - 〔Crossref 回读标题: Corporate responses to systemic risk: Talk and action〕
  - 〔已接线家族 (4): F333, F557, F559, F561〕


### 十补-16. 媒体来源类型分层语调 (tone_*_media / tone_gap_* / media_breadth / wire_frac / indep_frac)

> 净增 9 条(其中 2024–2026 者 8 条)。**已接线家族** (16): F339, F340, F439, F447, F467, F468, F492, F566, F568, F569, F570, F573, F579, F589, F591, F619

- 【2024–2026】Dong, Y., Liu, Y., Wang, M., & Zou, G. (2026). The Role of Media in Regulatory Oversight: Evidence From Comment Letters. Financial Review, 61(3), 1011-1035. https://doi.org/10.1111/fire.70051
  - *锚定* — 该文在中国交易所问询函情境下,发现媒体关注度更高(尤其负面报道更多)的中国上市公司更可能收到问询函,媒体监督既补充正式监管治理、也替代审计师与机构投资者等非政府治理机制。仅锚「以中文媒体报道量作为主体级构念纳入监管/治理实证」这一环,对应 nf_n_articles 的计数构造法与同数据生态参照。⚠ 原文以报道篇数计,不做去重来源媒体家数计数、无对数与逐年度截面 z 标准化,故不锚 media_breadth/media_breadth_z;识别单元为问询函事件非银行-年,未按媒体来源类型分层,不涉及 Fintech/Non-Fintech 补集划分。
  - 〔Crossref 回读标题: The Role of Media in Regulatory Oversight: Evidence From Comment Letters〕
  - 〔已接线家族 (1): F467〕
- 【2024–2026】Lu, S. (2026). Green Bonds: Reputational Bonding via Media Coverage. Management Science, 72(6), 5171-5192. https://doi.org/10.1287/mnsc.2024.05701
  - *锚定* — 该文以绿色债券发行人为主体,发现发行后企业环境表现相关的媒体报道量显著上升且持续,并将这一「声誉绑定」机制与后续环境表现改善相联系,即把发行人所获媒体报道覆盖作为核心机制变量。仅锚「报道覆盖广度/曝光量作为主体级构念来使用」这一generic理据。⚠ 原文以新闻数据库报道条数度量覆盖,**不做去重来源媒体家数(nunique)计数**,故不锚 n_outlets,亦不得视为 media_breadth 的 distinct-outlet 口径出处;无对数变换与年度截面标准化,国别为国际发行人,无 fintech 共现硬过滤前置口径。
  - 〔Crossref 回读标题: Green Bonds: Reputational Bonding via Media Coverage〕
  - 〔已接线家族 (1): F439〕
- 【2024–2026】Sun, J., Liu, M., & Huang, X. (2026). Technology adoption or independent innovation? Bank competition and SMEs’ incremental innovation strategies. Applied Economics, 1-16. https://doi.org/10.1080/00036846.2026.2651341
  - *锚定* — 该文把企业创新策略明确二分为「技术引进/采纳」与「自主创新 (independent innovation)」两种互斥模式, 并检验银行竞争如何在二者间推动切换。这为本项目 indep_frac 家族把创新来源模式判为「自主研发」与否的二分类构念本身提供了直接的构念出处与银行情境关联。
  - *迁移边界* — 关键差异在测量层: 原文的自主创新 vs 技术引进由企业专利/研发投入等结构化指标判定, 而本项目 indep_frac 是由 full/ctx/ss 三轨文本经 LLM 判定文章的创新来源模式后, 除以同轨 LLM 有效投票篇数得到的报道占比 — 是媒体叙事层的份额而非企业实际创新行为; 原文主体为中小企业 (SME) 且银行处于解释变量侧, 本项目主体是银行本身; 原文无 ctx/ss 对角线双轨 (F340) 的分轨独立分母设计。
  - 〔Crossref 回读标题: Technology adoption or independent innovation? Bank competition and SMEs’ incremental innovation strategies〕
  - 〔已接线家族 (2): F339, F340〕
- 【2024–2026】Hua, X., Dong, D., Xu, Z., & Huang, W. (2025). Official media sentiments toward energy and equity returns: Evidence from China. Energy, 340, 139126. https://doi.org/10.1016/j.energy.2025.139126
  - *锚定* — 该文以BERT对中国官方/政府控制媒体的新能源报道文本构建官方媒体语调指数,检验其与权益回报及企业融资投资行为的关系。锚 tone_official_media{track}「按媒体官方属性切出子样本、在子样本内对文章级语调取均值」这一构念的前沿存在性;对 tone_gap_official_nonoff{track} 仅提供官方侧的同构念先例,不锚两侧作差这一统计量。不锚任何中央/地方行政层级切分。
  - 〔Crossref 回读标题: Official media sentiments toward energy and equity returns: Evidence from China〕
  - 〔已接线家族 (7): F566, F569, F570, F573, F579, F589, F591〕
- 【2024–2026】Ananyev, M., & Volkova, E. (2024). Media ownership and ideological slant: Evidence from Australian newspaper mergers. PLOS ONE, 19(12), e0315137. https://doi.org/10.1371/journal.pone.0315137
  - *锚定* — 该文利用2016-2019年三起澳大利亚报业并购,以逾3000万篇报道的语言构建slant测度、以合成双重差分识别媒体所有权变更对报纸政治slant的因果影响。锚本项目按媒体归属/控制权(主管主办单位、行政层级)分层、并预期分层间语调存在系统性缺口这一前提的准实验证据。国别与制度情境、slant的政治意识形态量表口径均与本项目LLM投票的银行-金科报道语调不同,层级为报纸-时期无主体-年面板;不锚媒体内容类型(财经/综合/其他)这一正交切分维度。
  - 〔Crossref 回读标题: Media ownership and ideological slant: Evidence from Australian newspaper mergers〕
  - 〔已接线家族 (4): F447, F568, F579, F589〕
- 【2024–2026】Bushman, R., & Pinto, J. (2024). The Influence of Short Selling on Negative Press Coverage of Firms. Management Science, 70(3), 1924-1942. https://doi.org/10.1287/mnsc.2023.4783
  - *锚定* — 该文以卖空约束的外生放松(Reg SHO pilot)为识别来源,发现卖空活动上升后公司媒体报道的整体情感显著更负、负面新闻流显著增加,即把公司层面的负面新闻报道量本身建模为被解释变量。锚「某主体在某期获得多少篇报道是可独立测量、且会被外部力量系统性推动的量」这一构念,对应 nf_n_articles 作为独立聚合列用于证伪/控制的用法。⚠ 原文报道量为全部报道(数据库标注)而非 stage12 全量银行新闻 MINUS 已进面板 fintech 文章的 anti-join 补集;**原文无 nunique 去重来源家数计数**,故不锚 nf_media_breadth;主体为美国上市公司非银行。
  - 〔Crossref 回读标题: The Influence of Short Selling on Negative Press Coverage of Firms〕
  - 〔已接线家族 (1): F467〕
- 【2024–2026】Yu, M., Kyung, H., & Tsang, A. (2024). Media coverage and price reactions to earnings news. China Journal of Accounting Research, 17(3), 100379. https://doi.org/10.1016/j.cjar.2024.100379
  - *锚定* — 该文在中国情境下以公司层面的媒体报道量作为条件变量,检验其对盈余信息市场反应的调节作用。仅锚「以中文媒体报道计数构造主体-年度曝光度变量」在同语种同数据生态(中文财经新闻库)下的前沿参照,对应 nf_n_articles 的计数构造法。⚠ 原文以报道篇数计,不做去重来源媒体家数计数、无 ln(1+·) 对数变换与逐年度截面 z 标准化,故不锚 media_breadth/media_breadth_z;主体为A股上市公司、频率为盈余公告事件窗,非银行-年,亦未设 Non-Fintech 安慰剂子集。
  - 〔Crossref 回读标题: Media coverage and price reactions to earnings news〕
  - 〔已接线家族 (1): F467〕
- 【2024–2026】Zhang, Z., & Shen, D. (2024). Not all the news fitting to reprint: Evidence from price-volume relationship. Finance Research Letters, 62, 105128. https://doi.org/10.1016/j.frl.2024.105128
  - *锚定* — 该文明确把新闻区分为「转载/再刊」与非转载两类, 并证明二者的市场含义不同 — 即同一条报道是原创产制还是二次分发, 本身是有信息含量的文章级属性。这是本项目 is_wire (电头/通讯社来源判定) 与 has_byline (署名原创) 二分, 及其 bank-year 均值 wire_frac / staff_written_frac 的最贴近前沿参照。
  - *迁移边界* — 原文的转载判定依赖新闻数据库自带的转载标记, 而本项目 is_wire 由 parse_byline() 扫描「作者」字段与正文前 60 字电头关键词规则判定 (且作者字段空且电头未命中时记 NaN 不入分母), 判据完全不同; 原文停在文章级并以价量关系为 DV, 未做主体-年度的均值聚合, 也不涉及署名 (byline) 这一独立维度。
  - 〔Crossref 回读标题: Not all the news fitting to reprint: Evidence from price-volume relationship〕
  - 〔已接线家族 (5): F447, F468, F492, F566, F619〕
- Isakin, M., & Pu, X. (2023). Dispersion in news sentiment and corporate bond returns. International Review of Financial Analysis, 89, 102761. https://doi.org/10.1016/j.irfa.2023.102761
  - *锚定* — 该文把同一发行主体在同期多篇新闻之间的情感离散度作为独立可定价构念来度量并检验(美国公司债、债券-月层级、英文新闻数据库情感)。仅作 tone_gap_* 族generic前提「同一主体报道内部的语调不一致本身携带信息、而非只有语调水平有信息」的方法学近亲参照,不锚任何具体切分维度:原文的离散度是跨文章统计离散,与本项目先按来源属性划互补两组再取组均值之差(between-group contrast)非同一统计量,原文亦不做任何媒体来源属性分层。发表年2023,非2024+前沿。
  - 〔Crossref 回读标题: Dispersion in news sentiment and corporate bond returns〕
  - 〔已接线家族 (5): F568, F569, F570, F573, F579〕


### 十补-17. 地理邻近与本地偏好 (prox_* / neg_frac_home* / leave1out_{city,prov,zone})

> 净增 14 条(其中 2024–2026 者 14 条; **4 条未接入任何家族**, 见各条标注)。**已接线家族** (17): F152, F153, F450, F452, F453, F480, F481, F484, F485, F486, F487, F488, F574, F575, F581, F585, F655

- 【2024–2026】Kong, I., & Purves, R. S. (2026). Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters. Annals of the American Association of Geographers, 116(2), 270-288. https://doi.org/10.1080/24694452.2025.2564220
  - *锚定* — 对报纸文章检测地名并赋予地理坐标后, 量化报道在空间上的不均衡覆盖 (地理偏倚), 并考察地名粒度与要素类型对分析的影响。作为'先给新闻报道打地理坐标、再在坐标空间上做覆盖度统计, 并披露地名可解析性问题'这一分析范式的前沿存在性证明, 支撑本项目对可地理编码报道作距离缓冲计数 (F484/F485) 与地理编码回退占比披露 (F488)。原文语料固定为五家英国报纸, 不做圈内去重媒体来源计数, 故不锚定 F486; 主题为全球气候灾害而非银行金融科技, 分析单位是「报道-事件发生地」的国别覆盖偏倚而非「媒体所在地-银行总部」双坐标距离, 亦无 bank-year 面板聚合与 n_geocoded=0 置 NaN 的哨兵口径。
  - 〔Crossref 回读标题: Analyzing Geographic Bias of Newspaper Articles Reporting Global Climate Disasters〕
  - 〔已接线家族 (3): F484, F485, F488〕
- 【2024–2026】Lee, D. K. C., Xu, W., Shi, J., Wang, Y., & Ding, D. (2026). Shock Next Door: Geographic Spillovers in FinTech Lending After Natural Disasters. Econometrics, 14(1), 5. https://doi.org/10.3390/econometrics14010005
  - *锚定* — 用印尼最大金融科技放贷平台的贷款级数据 (2021-2023), 以空间滞后灾害暴露 (SLX 型) 估计灾害对相邻未受损省份借贷行为的溢出, 并发现溢出随地理连通性 (陆连 vs 海隔) 大幅变化。仅作为金融科技语境下'以空间邻近单元的聚合暴露刻画溢出'这一逻辑的前沿存在性证明, 与本项目经济圈内他行留一均值的空间同侪逻辑同族 (F655)。发表于 MDPI Econometrics, 非本项目优先的顶刊层级, 影响力有限。原文的空间邻近以行政邻接界定而非 Haversine 公里缓冲, 溢出对象是金融科技信贷量而非媒体报道篇数, 故**不锚定**距离缓冲族 (F484/F485); 原文有灾害外生冲击设计, 本项目无; 亦不涉及本项目的经济圈映射规则与 min_group_size 守卫。
  - 〔Crossref 回读标题: Shock Next Door: Geographic Spillovers in FinTech Lending After Natural Disasters〕
  - 〔已接线家族 (1): F655〕
- 【2024–2026】Bobrov, A., Kamdar, R., & Ulate, M. (2025). Regional Dissent: Do Local Economic Conditions Influence FOMC Votes? American Economic Review: Insights, 7(2), 268-284. https://doi.org/10.1257/aeri.20240184
  - *锚定* — 检验区域经济状况是否影响按地区指派的决策者投票行为, 即「主体所属地理区域的状况会系统性影响其可观测行为」。为本桶按省份/经济圈分组构造同侪暴露 (留一均值) 的前提 — 地理分组承载真实的共同冲击 — 提供顶刊层面的近期证据。
  - *迁移边界* — 主体为美联储 FOMC 地区联储主席, 行为为货币政策投票, 与中国银行的媒体报道语调无任何直接对应; 原文的地理分组是既定的联储辖区, 本项目是 (省份,年) / 经济圈映射且需自建; 该文不做留一均值构造, 也未把同组他成员的行为作为解释变量 — 因此仅锚定「地理分组有实质经济含义」这一前提, 不锚定 leave-one-out 算子本身。
  - 〔Crossref 回读标题: Regional Dissent: Do Local Economic Conditions Influence FOMC Votes?〕
  - 〔已接线家族 (2): F480, F655〕
- 【2024–2026】Broekel, T. (2025). Feeling the heartbeat of regions: local news and economic sentiments. Journal of Economic Geography, 25(6), 937-976. https://doi.org/10.1093/jeg/lbaf031
  - *锚定* — 从 300+ 德语地方媒体的地理编码新闻标题构建区域经济新闻情绪指数 (REGENS), 并检验其与区域失业率等地区经济指标的领先关系。作为'地方新闻文本→情感打分→地区-时间面板聚合'这一构造链路的前沿存在性证明, 支撑本项目将新闻语调按地理分组聚合成面板 (F153/F481) 及地方媒体语调水平测度 (F581)。原文聚合单位是地区本身而非「地区内某个被报道主体」, 不存在同城/异城切分与负面篇占比测度, 故不锚定 F450/F451/F585; 亦不做留一同侪均值 (F153/F481 仅锚定其区域聚合的语调面板一半, 不锚定自身排除算子)。语料为德语地方新闻, 无 LLM 投票共识语调与 full/ctx/ss 三轨; DV 为区域经济指标而非银行层面结果。
  - 〔Crossref 回读标题: Feeling the heartbeat of regions: local news and economic sentiments〕
  - 〔已接线家族 (3): F153, F481, F581〕
- 【2024–2026】Cerchiello, P., Filomeni, S., Tanda, A., & Toma, A. M. (2025). Can Soft Information Survive Organizational Distance? Evidence from SMB Lending. European Accounting Review, 34(5), 2033-2054. https://doi.org/10.1080/09638180.2024.2447356
  - *锚定* — 用某大型欧洲银行的专有数据检验企业贷款申请中的软信息对信贷决策的影响, 并证明该影响随贷款员与总部之间的组织距离拉长而衰减 (沟通摩擦阻碍软信息的'硬化')。作为'距离 → 信息质量衰减'这一核心机制的近期直接证据, 仅锚定本桶距离缓冲族 (F484/F485) 的构念前提。原文距离为银行组织内部的层级/地理距离对信贷软信息传递的影响, 与本项目的媒体报道地理距离是不同的信息通道; 语境为欧洲银行内部信贷数据与中小企业贷款, 非中文媒体语料; 原文未做任何文本情感度量, 故不锚定圈内语调族 (F487), 亦不涉及 bank-year 面板聚合与 NaN 哨兵口径。
  - 〔Crossref 回读标题: Can Soft Information Survive Organizational Distance? Evidence from SMB Lending〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Chen, H., Chen, Y., & Li, D. (2025). Local bias under natural disasters. International Review of Finance, 25(1), e70009. https://doi.org/10.1111/irfi.70009
  - *锚定* — 利用逾 24,000 名散户的账户级日度持仓记录, 证明自然灾害下本地投资者比非本地投资者更多增持本地股票, 且效应由本地投资者的信息优势驱动。仅作为'本地/异地地理二分承载真实信息差异'这一前提的近期文献锚点, 支撑本项目 is_local 二值指示 (F484) 与同城/异城组间差分 (F574) 的构念基础。原文的'本地'关系是投资者持仓行为与标的之间的关系, 本项目是媒体来源地与银行总部之间的关系, 主体与关系类型均不同; 原文无任何媒体、文本或语调测度, 故不锚定 tone_homecity_media / tone_noncity_media (F581/F585); 原文以灾害为外生冲击做异质性检验, 本项目无冲击设计, 且其 local 定义为同城/同区二分, 未使用 50/100/150/200km 四梯度 Haversine 缓冲。
  - 〔Crossref 回读标题: Local bias under natural disasters〕
  - 〔已接线家族 (3): F484, F574, F575〕
- 【2024–2026】Dong, D., Jiang, D., Peng, Y., Shen, L., & Zhu, H. (2025). Intercity mentioning: Stock posts, city network, and firms. Journal of Corporate Finance, 93, 102803. https://doi.org/10.1016/j.jcorpfin.2025.102803
  - *锚定* — 从中国股吧子论坛发帖中'提及非本公司总部城市'的行为抽取城市配对, 推断潜在城市网络, 并检验城市连通度与公司估值/换手/流动性/崩盘风险及城际收益共动的关联。仅作为'可从中文金融文本中抽取城市间地理配对、并据此做城市级聚合'这一分析范式的前沿存在性证明, 支撑本桶同城/异城二分与圈内计数 (F484/F485) 的可行性; 其配对端为「公司总部城市×帖中被提及城市」而非发帖者所在地, 与本项目「媒体所在城市×银行总部城市」的双地理键不同; 原文不做留一同侪均值、亦无任何语调测度, 故不锚定 F152/F153/F487。
  - 〔Crossref 回读标题: Intercity mentioning: Stock posts, city network, and firms〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Feng, J., Jiao, W., & Wang, Y. (2025). Bank fintech and lending distance: The role of information asymmetry and risk management channels. Economic Modelling, 151, 107154. https://doi.org/10.1016/j.econmod.2025.107154
  - *锚定* — 检验银行金融科技水平如何改变其放贷的地理距离, 并识别信息不对称与风险管理两条机制。作为'银行 × 金融科技 × 地理距离'三者同现的近期实证语境依据, 仅支撑本项目以公里距离缓冲界定暴露圈并作圈内计数 (F484/F485) 这一做法的前提 (距离在银行金融科技语境下承载信息含义)。该文的距离是银行与借款企业的放贷距离, 本项目的距离是报道媒体与银行总部的媒体地理距离, 同为公里距离但配对双方完全不同, 不可直接类比; 原文以银行金融科技指数为解释变量、距离为被解释变量, 且无任何媒体文本与语调维度, 故不锚定圈内语调族 (F487)。
  - 〔Crossref 回读标题: Bank fintech and lending distance: The role of information asymmetry and risk management channels〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Frandsen, B., Leslie, E., & McIntyre, S. (2025). Cluster Jackknife Instrumental Variables Estimation. Review of Economics and Statistics, 1-19. https://doi.org/10.1162/rest.a.263
  - *锚定* — 提出并推导 cluster jackknife (按簇留出) IV 估计量, 证明在簇内多工具/多固定效应设定下可消除标准 2SLS 的偏误。本桶留一均值按 (城市/省份/经济圈, 年) 分组构造, 与该文的按簇留出思路同族; 原文是纯计量方法论文, 做的是估计量推导 + 蒙特卡洛 + 一个司法数据应用。
  - *迁移边界* — REStat 计量方法文, 应用示例为美国司法/法官指派数据, 与中文银行媒体语调面板无关。该文留出单位是 cluster (法官), 本项目留出单位是同组的单个银行且分组键为地理×年份; 原文关注估计量渐近性质, 本项目仅借其对留一构造的偏误校正逻辑作方法参照, 并未实施 cluster jackknife 估计。
  - 〔Crossref 回读标题: Cluster Jackknife Instrumental Variables Estimation〕
  - 〔已接线家族 (5): F152, F153, F480, F481, F655〕
- 【2024–2026】Zhang, Z., & Bethard, S. (2025). A survey on geocoding: algorithms and datasets for toponym resolution. Language Resources and Evaluation, 59(2), 1775-1796. https://doi.org/10.1007/s10579-024-09730-2
  - *锚定* — 系统综述 geocoding / toponym resolution 的算法族与评测数据集 (将非结构化文本匹配到地理坐标或本体)。仅作为本项目媒体来源地三级查找这一 geocoding 步骤所处方法学领域的综述性参照, 支撑对地理编码质量与回退命中占比作显式披露的必要性 (F488) 及其上游坐标输入 (F484/F485/F486); **不主张**该综述是省会质心回退启发式的方法学出处 (综述为二手梳理, 非方法来源), 亦未经核实其是否讨论行政中心回退这一具体启发式——本项目的省会回退属研究者实现选择。原文面向英文 NLP 语料的通用 geoparsing, 本项目仅对结构化的媒体来源城市/省份元数据字段做词典查找, 消歧难度更低; 原文无任何语调测度, 不锚定 F487。
  - 〔Crossref 回读标题: A survey on geocoding: algorithms and datasets for toponym resolution〕
  - 〔已接线家族 (2): F486, F488〕
- 【2024–2026】Ellis, C., & Jaspersen, J. G. (2024). Fixed Effects and the "Leave-Out'' Instrument. SSRN Electronic Journal No. 4787799 [Working Paper]. https://doi.org/10.2139/ssrn.4787799
  - *锚定* — 该文分析 leave-out (留一同侪均值) 工具变量在含固定效应模型中的行为, 指出组内留一均值与固定效应同时使用时估计量会出现机械性偏误。属本桶五个 leave1out 家族 (city/prov/zone) 所用构造法的方法学警示文献 — 原文做的是估计量性质推导与模拟, 不涉及媒体或银行数据。
  - *迁移边界* — SSRN 工作论文 (未见期刊终刊记录), 非同行评审终稿; 讨论对象是一般线性面板留一 IV 估计量, 未涉及本项目的 bank-year 层级、中文媒体语调原子值 (dict_avg_tone / bert_pos_share / llm_vote_score), 亦未讨论本项目 (省份,年份) / (城市,年份) / 经济圈 三种分组键与 min_group_size 守卫。原文关注 IV 用途, 本项目 leave1out 列部分仅作同侪暴露控制变量而非 IV。
  - 〔Crossref 回读标题: Fixed Effects and the "Leave-Out'' Instrument〕
  - 〔已接线家族 (5): F152, F153, F480, F481, F655〕
- 【2024–2026】Huang, W., Liu, J., & Zhang, R.-Z. (. (2024). Local newspaper closures and non-GAAP reporting quality. Finance Research Letters, 62, 105024. https://doi.org/10.1016/j.frl.2024.105024
  - *锚定* — 以本地报纸停刊作为本地媒体监督减弱的冲击, 检验公司信息披露质量变化。原文的核心前提正是「总部同城的本地媒体与异地媒体在监督功能上不可替代」, 这是本桶 homecity vs noncity 媒体子样本二分及其语调/负面占比对比的构念依据。
  - *迁移边界* — 识别策略是停刊事件的 DiD, 本项目不做停刊冲击而是横截面上的同城/异城子样本对比; 语境为美国本地报纸与美国上市公司; DV 为非 GAAP 披露质量, 非媒体语调本身 — 该文只把本地媒体当作监督强度的处理变量, 并未度量本地媒体的报道语调, 因此对 F581/F585 只锚定「本地媒体独立构念」这一半, 不锚定其语调算法。FRL 为快报刊, 篇幅有限。
  - 〔Crossref 回读标题: Local newspaper closures and non-GAAP reporting quality〕
  - 〔已接线家族 (6): F450, F452, F453, F575, F581, F585〕
- 【2024–2026】Huang, Y., Li, F., Li, T., & Lin, T. (2024). Local information advantage and stock returns: Evidence from social media. Contemporary Accounting Research, 41(2), 1089-1119. https://doi.org/10.1111/1911-3846.12935
  - *锚定* — 用社交媒体用户地理位置识别「本地」信息发布者, 检验本地信息优势对股票收益的预测力。原文做的是: 按发帖者与公司总部的地理关系切分样本、比较本地组与非本地组的信息含量差异 — 与本桶 tone_homecity_media / tone_gap_homecity_noncity 的同城 vs 异城子样本对比设计同族。
  - *迁移边界* — 数据为社交媒体发帖 (中国雪球/股吧类平台) 而非报纸/通讯社媒体来源; 地理归属基于用户 IP/自报位置, 本项目基于媒体来源城市字段经地名后缀清洗比对; 该文以股票收益为 DV 并按同城二分, 未使用连续距离缓冲 (50/100/150/200km) 或 Haversine 球面距离; 研究对象为一般上市公司非银行。
  - 〔Crossref 回读标题: Local information advantage and stock returns: Evidence from social media〕
  - 〔已接线家族 (6): F453, F484, F487, F574, F575, F581〕
- 【2024–2026】Tian, Y., & Su, Q. (2024). Digital transformation, information and lending distance -Evidence from Chinese bank branch data. Economic Analysis and Policy, 84, 545-560. https://doi.org/10.1016/j.eap.2024.09.015
  - *锚定* — 用中国银行分支机构数据检验数字化转型对放贷距离的影响, 是中国银行业语境下距离-信息关系的近期实证。仅作为'在中国银行业语境中地理距离承载实质信息含义'这一前提的同国别语境依据, 支撑本项目以距离缓冲界定暴露圈并作圈内计数 (F484/F485)。该文距离对象是银行分支与借款人的信贷距离, 非本项目的媒体-总部距离; 分析层级是银行分支机构, 本项目是银行法人 (总部坐标) × 年; 原文无媒体文本分析与语调测度, 故不锚定圈内语调族 (F487)。**本项目 50/100/150/200km 四梯度阈值不引用该文作依据, 属研究者选择**, 并已作敏感性梯度并排披露。
  - 〔Crossref 回读标题: Digital transformation, information and lending distance -Evidence from Chinese bank branch data〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕


### 十补-18. 网络与同行溢出 / Bartik-IV / page_rank

> 净增 13 条(其中 2024–2026 者 13 条; **2 条未接入任何家族**, 见各条标注)。**已接线家族** (7): F028, F062, F103, F343, F433, F444, F471

- 【2024–2026】Avramov, D., Ge, S., Li, S., & Linton, O. (2026). Dual peer effects and cross-stock predictability. Journal of Financial Economics, 180, 104274. https://doi.org/10.1016/j.jfineco.2026.104274
  - *锚定* — Avramov 等在 JFE 构造股票间的同侪连接矩阵并度量同侪特征向自身的溢出, 属典型的「以加权同侪均值作为暴露变量」设定, 与 F471 的 Σ_j W[i,j,t-1]×x[j,t-1] 行随机加权、F433 的同组同业均值构造同一测度族。是该族在顶级金融期刊的最新应用存在性证明。
  - *迁移边界* — 原文的同侪连接基于股票收益/特征的经济联系, 被加权的量是收益或特征、DV 是横截面收益可预测性; 本项目 W 来自银行新闻共现网络, 被加权的量是 ln_news_coverage (媒体报道量对数), 单位与层级 (银行-年) 均不同, 且本项目不做收益预测。
  - 〔Crossref 回读标题: Dual peer effects and cross-stock predictability〕
  - 〔已接线家族 (2): F433, F471〕
- 【2024–2026】Huynh, T. H. H., & Nguyen, T. M. H. (2026). Signals in the news: How media reputation improves stock liquidity around the world. Asia and the Global Economy, 6(1), 100139. https://doi.org/10.1016/j.aglobe.2026.100139
  - *锚定* — 该文以企业媒体声誉为核心解释变量, 用 2000–2020 年 40 国企业数据发现媒体声誉与股票流动性正相关, 且在信息透明度低、企业可见度低的公司中更强, 在集体主义/不确定性规避与社会信任高的文化中更明显, 并最终降低融资成本。其价值在于: 把「企业相关新闻的褒贬倾向聚合为单一企业层声誉指标」这一构念作为前沿实证的主变量, 证明 F343 所属的媒体极性/声誉测度族在 2024 年后仍是活跃的研究对象, 并佐证该构念承载可观测的经济后果 (流动性、融资成本)。⚠ 可得摘要未披露其声誉指标的具体公式, 无法证实其采用 Janis-Fadner 失衡系数, 故本文只锚定构念族的使用前沿, 不得作为「jf_coefficient 公式本身在 2024 年后仍被采用」的证据 (该项举证请改用 Applied Sciences 2026 那条: 其明文以 media favorableness / media endorsement 系数为对比基准)。原文实体为多国上市公司、DV 为股票流动性; 本项目 F343 为银行-年, 已按 metric-audit 2026-06-10 把分母由旧 (P+N)^2 改为 T^2 (T=n_articles_llm_valid), 并逐 full/ctx/ss 三轨分别计算, T=0 时置 NaN, 该文对这两项调整无任何对应。期刊层级非顶刊。
  - 〔Crossref 回读标题: Signals in the news: How media reputation improves stock liquidity around the world〕
  - 〔已接线家族 (1): F343〕
- 【2024–2026】Ouyang, H., Liu, X., Yin, J., & Huang, C. (2026). Firm Network Complexity and Stock Returns: Case of Shared Analyst Coverage in China. Emerging Markets Finance and Trade, 62(11), 4113-4136. https://doi.org/10.1080/1540496x.2025.2605157
  - *锚定* — 该文以「共享分析师覆盖」这一信息中介的共现关系构造中国企业间网络并研究网络上的传导, 与本项目用新闻共现 (同一篇报道同时提及两家银行) 定义 W 的思路同族 — 均是以第三方信息生产者的共同覆盖来推断实体间连接。
  - *迁移边界* — 原文连接来自分析师覆盖重叠、DV 为股票收益; 本项目连接来自新闻文本共现、被加权量为媒体报道量对数, 层级为银行-年面板。原文亦未涉及本项目对缺失同行重归一的具体处理。
  - 〔Crossref 回读标题: Firm Network Complexity and Stock Returns: Case of Shared Analyst Coverage in China〕
  - 〔已接线家族 (1): F471〕
- 【2024–2026】Venčkauskas, A., Jusas, V., & Barisas, D. (2026). Evaluation of a Company’s Media Reputation Based on the Articles Published on News Portals. Applied Sciences, 16(4), 1987. https://doi.org/10.3390/app16041987
  - *锚定* — 该文构建了一条从新闻门户文章自动抽取、分类并聚合为企业媒体声誉分值的计算流水线, 与本项目「逐篇判正负 → 银行-年聚合为单一极性指标」的产线形态同族, 是该测度族在 2026 年的工程化前沿实例。
  - *迁移边界* — 原文是计算/工程导向论文 (Applied Sciences), 聚合函数为其自定义评分而非 Janis-Fadner 二次式, 语料为立陶宛语新闻门户, 无经济学识别设计, 亦无银行样本。仅作同族流水线的存在性锚, 不构成 F343 公式的方法出处。
  - 〔Crossref 回读标题: Evaluation of a Company’s Media Reputation Based on the Articles Published on News Portals〕
  - 〔已接线家族 (1): F343〕
- 【2024–2026】Borusyak, K., & Hull, P. (2025). Optimal Formula Instruments. SSRN Electronic Journal No. 5198954 [Working Paper]. https://doi.org/10.2139/ssrn.5198954
  - *锚定* — Borusyak 与 Hull 推导 formula instrument (由已知公式把外生冲击映射为个体暴露值) 的最优构造与 recentering, 给出实践中的构造算法, 并证明当公式对冲击线性 (如 shift-share 构造) 时 recentering 只需对冲击期望建模这一更弱假设; 实证以 2014 年 ACA Medicaid 部分扩张展示相对 simulated IV 的显著功效增益。F103 的份额×冲击 Bartik 工具落在该文界定的 formula instrument 家族内, 该文是这一家族当前的前沿方法工作。本项目并未采用其最优加权/recentering 方案, 仍用基期份额行归一的等权构造, 故该文只作方法族的前沿存在性锚, 不是本项目实现的依据; 其推导停在一般 formula instrument 抽象层, 未对媒体文本份额做实证。原文未论及 leave-one-out 同侪均值工具 (该构造无外生冲击输入、不经公式映射), 故不锚定 F433。注: 该文流通版本为 NBER w33594 / CeMMAP CWP09-25 且已被 Econometrica 接收, 引用时应以已接收版本为准, 不宜按未评审工作论文对待。
  - 〔Crossref 回读标题: Optimal Formula Instruments〕
  - 〔已接线家族 (1): F103〕
- 【2024–2026】Boucher, V., & Houndetoungan, A. (2025). Estimating Peer Effects Using Partial Network Data. Review of Economics and Statistics, 1-48. https://doi.org/10.1162/rest.a.1630
  - *锚定* — Boucher 与 Houndetoungan 提出在网络结构仅被部分观测 (抽样网络/删失网络/误分类链接) 时估计同侪效应的方法, 证明只要能一致估计网络分布即可用 linear-in-means 模型识别同侪效应, 并以 Add Health 数据显示网络数据误差会造成同侪效应的大幅向下偏误。该模型的规范对象正是行归一化邻接矩阵 W 与空间滞后项 W·y, F471 的 peer_fintech_exposure_lag1 = Σ_j W[i,j,t-1]×ln_news_coverage[j,t-1] 即此类 row-stochastic 空间滞后, 故本文锚定该测度形式的计量地位, 并提示网络测量误差会衰减此类估计。原文的 W 来自社会/同侪链接的部分观测样本并对缺失做模型化推断; 本项目 W 由银行共现网络直接构造并行归一, 对缺失采取「仅对 ln_news_coverage 非缺失的在网同行重归一、其余置零」的确定性口径, 二者处理缺失的机制完全不同, 原文亦不涉及银行、媒体报道量或中国语境。原文不讨论同组 LOO 均值作为工具变量的合法性, 且本项目 bank_type 分组完全可观测、不存在该文针对的部分观测问题, 故不锚定 F433。
  - 〔Crossref 回读标题: Estimating Peer Effects Using Partial Network Data〕
  - 〔已接线家族 (1): F471〕
- 【2024–2026】Ding, J., Huang, J., & Ding, A. (2025). The peer effects of corporate social responsibility in China: A pre-registered study. Pacific-Basin Finance Journal, 94, 102878. https://doi.org/10.1016/j.pacfin.2025.102878
  - *锚定* — 该文是中国语境下企业社会责任同侪效应的预注册研究 (pre-registered study, 另有同题 2024 年注册报告篇), 考察企业如何对同侪的 CSR 实践做出反应, 以 OLS 验证假设并用工具变量法缓解内生性威胁, 并提出市场竞争与制度压力两条机制。其价值在于: 同侪效应的识别在中国语境下以预注册设计执行, 对「同侪暴露变量 + IV 缓解反射性/内生性」这一识别范式提供了近期的可信性参考, 与 F433 把同型同业的 tech_frac 均值作为工具的思路同属同侪效应识别族。⚠ 该文的同侪暴露变量的具体构造 (分组维度、是否为 leave-one-out 组内均值) 与其工具变量的具体形式均未在可得摘要中披露, 故本文只锚定同侪效应识别范式的存在与可信性, 不得据以主张与 F433 的 mean_{j∈g(i), j≠i} 构造同形。原文被平均/被考察的是 CSR 表现; 本项目分组为 bank_type, 被平均的是 tech_frac_{lc,ls} (LLM 分类得到的技术类报道占比, [0,1]), 且本项目另做 lag1 一阶滞后臂, 原文亦未对该同组均值作为工具的合法性做与本项目相同的论证。
  - 〔Crossref 回读标题: The peer effects of corporate social responsibility in China: A pre-registered study〕
  - 〔已接线家族 (1): F433〕
- 【2024–2026】Estrada, P., Estrada, J., Huynh, K. P., Jacho-Chávez, D., & Sánchez-Aragón, L. (2025). netivreg: Estimation of peer effects in endogenous social networks. The Stata Journal: Promoting communications on statistics and Stata, 25(2), 344-373. https://doi.org/10.1177/1536867x251341145
  - *锚定* — 该文提供 netivreg 的 Stata 实现, 针对内生社会网络下的 linear-in-means 同侪效应模型, 实现 Estrada (2022) 的广义三阶段最小二乘与 Chan et al. (2024) 的 GMM 估计量, 其识别利用 two-layered multiplex network 数据结构 (以第二层网络提供外生变异), 估计对象即行归一化 W 与空间滞后 W·y。与 F471 的行随机空间滞后暴露同属该估计对象族, 是该族在 Stata 生态的当前实现前沿 (本项目分析端亦落在 Stata), 并提示 W 内生时需专门校正。原文是软件实现与方法说明 (Stata Journal), 非实证发现, 其应用为模拟数据与经济学期刊论文数据; 本项目未使用 netivreg, 亦不做内生网络校正而将 W 视为前定 (取 t-1 期), 该文仅锚定同族方法的存在与可行性, 不背书本项目的前定假设。原文工具来自 multiplex 第二层网络, 与 F433 的同 bank_type 组内 leave-one-out 均值无构造同源性, 故不锚定 F433。
  - 〔Crossref 回读标题: netivreg: Estimation of peer effects in endogenous social networks〕
  - 〔已接线家族 (1): F471〕
- 【2024–2026】Huang, Y., Li, Y., Li, P., Zhang, Q., & Zhang, Y. (2025). The unseen guardian: News co-mention and stock market manipulation. Finance Research Letters, 86, 108648. https://doi.org/10.1016/j.frl.2025.108648
  - *锚定* — 该文用分布式爬虫构造 news co-mention 指数 (同一篇报道同时点名多家公司), 刻画媒体报道中的企业间共同点名网络, 检验其对中国 A 股市场操纵的抑制作用。属 F444 multi_bank_frac 的 is_multi_bank 旗标与 F028 bank_count 同构念的**前沿存在性与同域应用**参照 (非构念出处 —— 同篇共同点名构念的提出远早于本文)。
  - 〔Crossref 回读标题: The unseen guardian: News co-mention and stock market manipulation〕
  - 〔已接线家族 (2): F028, F444〕
- 【2024–2026】Lamot, K., & Paulussen, S. (2025). News content promotion pressure: A content analysis of the cross-media visibility of and engagement with news stories. Journalism, 26(12), 2563-2580. https://doi.org/10.1177/14648849241279012
  - *锚定* — Lamot 与 Paulussen 做内容分析, 考察平台经济下新闻机构如何对抗算法造成的不可见性: 识别并度量若干刻意的推广策略以提升单篇文章可见度 (跨平台策略性发帖、主页位置摆放 homepage placement、延长内容生命周期), 并把这些策略聚合为一个「推广压力 (promotion pressure)」分数, 进而分析其与受众参与的循环关系; 推广压力最高的文章多与重大事件相关, 依赖冲突性与人格化新闻价值, 且常用标题党。其对本项目的价值在于: 「把稿件摆在多显著的位置」被作为可编码、可量化的变量纳入分析 (homepage placement 是该推广压力分数的构成项之一), 佐证 F062 的 page_rank 所依赖的前提 — 稿件的位置摆放是可测量的编辑/机构决策痕迹。⚠ 原文的构念内核是新闻机构在平台算法下的主动推广努力, 而非编辑赋予的显著性信号, 位置只是聚合分数的一个分项而非独立的 story prominence 维度, 二者方向不同 (主动争取可见度 vs 被动的显著性痕迹); 其测度对象是数字新闻网站的主页位置, 而非报纸「字母序版叠 + 页码」的序数编码, 且不聚合到实体-年层级、无金融结果变量。本项目 F062 是银行-年均值且值域含 NaN。故该文仅作位置可编码性的存在性锚, 不是 F062 的方法出处。
  - 〔Crossref 回读标题: News content promotion pressure: A content analysis of the cross-media visibility of and engagement with news stories〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Wang, H. (2025). Decoding Momentum Spillover Effects. Journal of Financial and Quantitative Analysis, 1-36. https://doi.org/10.1017/s002210902510238x
  - *锚定* — 该文系统拆解跨企业连接网络上的动量溢出, 其估计量即「按连接矩阵加权的同行变量」这一空间滞后形式, 与 F471 的行归一化 W 加权同行暴露构造同族。可作为网络溢出测度在 JFQA 层级的最新前沿存在性证据。
  - *迁移边界* — 原文加权对象为同行的历史收益 (动量), 网络来自经济联系并服务于资产定价预测; 本项目 F471 加权对象为同行的 ln_news_coverage, W 来自新闻共现且严格取 t-1 期滞后, 分母只对非缺失在网同行重归一 (不做 fillna(0) 伪零)。原文未处理这一缺失重归一问题。
  - 〔Crossref 回读标题: Decoding Momentum Spillover Effects〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Borusyak, K., & Hull, P. (2024). Negative Weights Are No Concern in Design-Based Specifications. AEA Papers and Proceedings, 114, 597-600. https://doi.org/10.1257/pandp.20241046
  - *锚定* — Borusyak 与 Hull 在 design-based 框架下证明: 当识别力来自冲击的准随机分配、且低维控制张成处理的条件期望时, 回归隐含的负权重不构成识别威胁 — 该结论经一阶单调性条件延伸至 design-based IV 估计量, 并明确适用于 formula treatments 与 shift-share 型工具。F103 的基期份额加权 Bartik 构造正落在该文点名的 shift-share/formula 工具族内, 故本文锚定的是 F103 这一识别设计在负权重质疑下的稳健性依据。原文为纯计量方法论短文, 示例场景为地区×产业就业份额的经典 Bartik 设定; 本项目 F103 份额是银行 i 基期文章在 innovation_locus_full ∈ {tech,app} 上的篇数占比 (媒体文本层, 非就业层), 且原文未涉及银行、金融科技或中文新闻文本, 亦未讨论剔除 other 后按行归一这一步。原文未论及同侪暴露型 (leave-one-out 组内均值) 工具, 故不锚定 F433。
  - 〔Crossref 回读标题: Negative Weights Are No Concern in Design-Based Specifications〕
  - 〔已接线家族 (1): F103〕
- 【2024–2026】Huang, C., Huang, H.-Y., & Ho, K.-C. (2024). Media coverage and stock liquidity: Evidence from China. International Review of Economics & Finance, 89, 665-682. https://doi.org/10.1016/j.iref.2023.07.085
  - *锚定* — 该文在中国股票市场检验媒体报道量对股票流动性的影响, 发现报道量通过改善信息环境、降低逆向选择而提升流动性, 且该效应在信息环境更透明的公司中减弱、在 First News (首要/首发报道) 更多的公司中更明显, 并在投资者情绪高涨或专业投资者更多时减弱。其价值在于: 证明中国新闻语料上「报道的显著性/首要性」是可测量且具经济后果的维度 — 与 F062 的 avg_page_rank 所编码的构念方向一致 (编辑赋予报道的显著程度承载信息), 提供中国语境的近期存在性锚。⚠ 原文的显著性代理是报道数量与 First News 标识, 而非「叠字母序×100+页码」这类报纸版面位置序数编码, 故非 F062 的方法出处; 实体为 A 股上市公司、DV 为股票流动性, 与本项目银行-年面板不同。⚠ 原文不含任何报道极性/褒贬倾向的聚合测度 (摘要中的 investor sentiment 是投资者情绪调节变量, 非报道倾向), 故不锚定 F343。
  - 〔Crossref 回读标题: Media coverage and stock liquidity: Evidence from China〕
  - 〔已接线家族 (1): F062〕


### 十补-19. 关注度 / 报道量 / 覆盖广度基础量

> 净增 11 条(其中 2024–2026 者 11 条; **2 条未接入任何家族**, 见各条标注)。**已接线家族** (9): F028, F162, F229, F314, F316, F319, F320, F525, F526

- 【2024–2026】Bie, S., Feng, G., Guo, N., & He, J. (2026). Can news predict firm bankruptcy? Journal of Financial Markets, 79, 101002. https://doi.org/10.1016/j.finmar.2025.101002
  - *锚定* — 该文用 Dow Jones Newswires 全文新闻以 LLM (ChatGPT) 生成公司层情感预测变量, 对标 FinBERT 与词典模型, 证明新闻情感在财务变量之外对企业破产有增量预测力。可作为「媒体负面情感的聚合测度携带企业困境信号」这一构念的前沿存在性参照, 支持 F162 concern_score 把负面强度作为关切/困境指数分量的立意。⚠ 原文无报道量分量、无 (neg−pos)/(neg+pos) 归一化比, 且本项目样本内无破产银行, 原文的预测性结论不可迁移为 F162 的效度证据。
  - 〔Crossref 回读标题: Can news predict firm bankruptcy?〕
  - 〔已接线家族 (1): F162〕
- 【2024–2026】Meng, L., Wang, P. P., Lu, H., Yang, W. Y., & Vijayakumar, S. (2026). Entity-specific text classification with large language models: two applications on financial and brand news. China Accounting and Finance Review, 1-11. https://doi.org/10.1108/cafr-12-2025-0269
  - *锚定* — 该文以 LLM 做实体特定 (entity-specific) 的新闻文本分类基准评测, 明确指出同一篇报道内多实体并存会使文档级分析失效, 需在实体粒度上抽取信息, 并在英文金融新闻与中文危机新闻两语料上以 F1 对人工标注做效度评估。可作为 F028 bank_count (单篇被识别出的不同目标银行数) 所依赖的「单篇多实体并存」构念前提之前沿参照。本项目 F028 的实体识别走词典/AC 自动机 + jieba token 匹配 (非 LLM), 故原文不构成本项目实体抽取精度的背书。
  - 〔Crossref 回读标题: Entity-specific text classification with large language models: two applications on financial and brand news〕
  - 〔已接线家族 (2): F028, F314〕
- 【2024–2026】Chen, C., Yuen, C., Zhang, H., & Yan, J. (2025). The impact of major customers’ qualitative forward-looking information on suppliers’ future operating performance. Accounting Forum, 49(5), 1068-1095. https://doi.org/10.1080/01559982.2024.2440688
  - *锚定* — 该文以客户方前瞻性业绩预告报告 (MEFR) 中定性信息的可读性/不确定性与语调变动为自变量, 检验其对供应商未来经营绩效的预测力。至多可作为「前瞻性披露文本的定性成分具有跨主体信息含量」的广义参照; 原文并未构造前瞻句占比类测度, 亦无句级门控设计, 与 F316 frac_fls_fonly 的构造无操作化关联 —— 若无法补充原文确用 FLS 句级识别的正文证据, 建议整条剔除。
  - 〔Crossref 回读标题: The impact of major customers’ qualitative forward-looking information on suppliers’ future operating performance〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Chen, D., & Zhang, Q. (2025). Media attention and corporate digital transformation. International Review of Economics & Finance, 102, 104288. https://doi.org/10.1016/j.iref.2025.104288
  - *锚定* — 该文以媒体关注度 (media attention, 由报道数量类指标构造) 为核心解释变量, 检验其对企业数字化转型的影响, 是中国语境下「媒体关注度量 → 技术/数字化结果」的同域应用。这锚定 F320 ft_vol_yr = ln(1+当年金融科技唯一篇数) 作为金融科技媒体关注度代理的构造与应用定位。
  - *迁移边界* — 原文对象为 A 股一般上市公司的数字化转型, 本项目对象为商业银行的金融科技报道, 实体宇宙与主题词表均不同 (本项目金科侧为裸 AC 词典 (撰稿时 1506 词, 2026-07-21 换血后现行 607 词), 经 stage 13 银行∧金科邻近共现硬过滤); 原文媒体关注度多为公司层面的全主题报道计数, 本项目 ft_vol_yr 只计金融科技唯一篇数; 原文无 ft_vol_prov/ft_vol_city 的 (省/市, 年) 曝露加权 leave-one-out 设计; 原文 DV 为数字化转型指数, 本项目 F320 为右手侧列。
  - 〔Crossref 回读标题: Media attention and corporate digital transformation〕
  - 〔已接线家族 (1): F320〕
- 【2024–2026】Huang, Y.-T., Chiu, I.-C., & Hung, M.-W. (2025). Firm-specific news sentiment and stock returns: the impact of relevance and time frames. Applied Economics Letters, 1-10. https://doi.org/10.1080/13504851.2025.2522167
  - *锚定* — 该文明确检验「新闻与特定公司的相关度 (relevance)」这一维度对公司特定新闻情感效力的调节作用, 即一篇报道在多大程度上是关于该公司的, 会改变该报道所携信号的强度。这锚定 F525 sum_mention_density (目标银行提及次数 / 文本字符数, 即单篇报道中目标实体的相对篇幅占比) 与 F526 sum_target_mentions (提及次数加总) 的构念动机: 二者正是以提及强度/密度操作化「该篇报道与目标实体的相关度」。原文使用的是商业数据供应商给定的 relevance 分数, 并非本项目的密度公式。
  - *迁移边界* — 原文的 relevance 来自第三方新闻情感数据库的既有打分 (黑箱、供应商定义), 本项目 F525 是自建的透明比值 target_bank_mention_count / max(len(内容), 1), 二者数值不可比且原文不构成对本项目密度公式的效度检验; 原文层级为公司-新闻条目并对接股票收益 (高频), 本项目 F525/F526 在 bank-year 上取 sum (非 mean, 故与年内篇数量级共线, 需另行注意); 语种上中文字符数与英文 token 数的分母含义不同, 密度值域不可跨语种迁移; 原文为一般上市公司, 本项目为目标银行。
  - 〔Crossref 回读标题: Firm-specific news sentiment and stock returns: the impact of relevance and time frames〕
  - 〔已接线家族 (2): F525, F526〕
- 【2024–2026】deHaan, E., Lawrence, A., & Litjens, R. (2025). Measuring Investor Attention Using Google Search. Management Science, 71(7), 6275-6297. https://doi.org/10.1287/mnsc.2022.02174
  - *锚定* — 该文以 27 亿次网站访问数据系统评估 Google ticker 搜索量指数 (SVI) 作为投资者关注度代理的测量误差, 发现 69% 的搜索与投资无关、误差与公司特征系统相关并可导致假阳/假阴, 并提出 ticker-stock SVI 作为改进。属 F320 ft_vol 所在「关注度代理量」族的方法学参照 —— 关注度代理的构造选择本身会驱动结论, 须交代口径。⚠ 原文代理为读者侧搜索量, 本项目 ft_vol 为媒体侧报道篇数对数, 二者是关注度的不同侧面, 原文的测量批评既不能背书亦不能否证 ft_vol。
  - 〔Crossref 回读标题: Measuring Investor Attention Using Google Search〕
  - 〔已接线家族 (1): F320〕
- 【2024–2026】Chen, J. J., Song, P., & Loi, F. L. (2024). Strategic forward-looking nonearnings disclosure and overinvestment. The British Accounting Review, 56(6), 101431. https://doi.org/10.1016/j.bar.2024.101431
  - *锚定* — 该文以美国上市公司 2003-2019 的前瞻性语句 (FLS) 为文本对象, 度量非盈利类定性 FLS 的异常语调并检验其与过度投资的关系。可作为 F316 所在「前瞻性语句文本测度」族的应用存在性参照 (FLS 作为可机器识别的句类在顶刊被常规使用), 但原文的落地测度是异常语调而非前瞻句占比, 故不构成 F316 的 D_future 词门或句级占比构造的操作化参照。
  - 〔Crossref 回读标题: Strategic forward-looking nonearnings disclosure and overinvestment〕
  - 〔已接线家族 (1): F316〕
- 【2024–2026】Kim, J.-B., Tseng, K., Wang, J. (., & Xi, Y. (2024). Policy uncertainty, bad news disclosure, and stock price crash risk. Journal of Empirical Finance, 78, 101512. https://doi.org/10.1016/j.jempfin.2024.101512
  - *锚定* — 该文在经济政策不确定性背景下检验管理层坏消息披露/囤积与股价崩盘风险的关系。可作为 F229 dummy_no_positive_news 的**背景性构念动机**参照 —— 即负面信息在时间上的分布 (是否被扣留/是否主导信息环境) 本身具有信息含量。⚠ 原文的坏消息来自公司自主披露的时点选择 (发送方内生行为), 本项目 F229 来自第三方媒体报道的 LLM 情感判定计数角点, 二者层级与生成机制均不同, 原文不构成 F229 的测度来源或阈值依据。
  - 〔Crossref 回读标题: Policy uncertainty, bad news disclosure, and stock price crash risk〕
  - 〔已接线家族 (1): F229〕
- 【2024–2026】Kitchens, B., Parham, R., & Yung, C. (2024). Is news really news? The effects of selective disclosure regulations. Review of Finance, 28(6), 1991-2015. https://doi.org/10.1093/rof/rfae030
  - *锚定* — 该文利用美/欧禁止选择性披露的监管出台 (澳/日为无监管对照), 证明监管前新闻日的信息已通过泄露提前进入市场、监管后新闻日才真正传递新信息。可作为「被计为一条新闻的内容未必是新信息」这一问题意识的前沿参照, 用以说明 F319 ft_n_articles_dedup 为何不能把原始篇数直接当作独立信息条数。⚠ 须诚实区分: 原文的信息非新颖性来自监管前的提前泄露, 本项目 F319 的去重是 (target_bank, 标题, 日期) 复合键的机械去重, 只能剔除标题-日期完全一致的重复, 无法识别改写型转载, 亦与原文机制无关。
  - 〔Crossref 回读标题: Is news really news? The effects of selective disclosure regulations〕
  - 〔已接线家族 (1): F319〕
- 【2024–2026】Semenova, M., Sokolov, V., & Benov, A. (2024). Bank runs and media freedom: What you don’t know won’t hurt you? Journal of Financial Stability, 74, 101323. https://doi.org/10.1016/j.jfs.2024.101323
  - *锚定* — 该文检验媒体自由度 (信息可得性的制度维度) 与危机期间零售存款流出的关系, 结果**未支持**媒体自由度直接影响储户行为策略的假设, 仅提示信息限制可能与市场纪律及金融素养效应交互。可作为「储户/公众能否获得银行负面信息构成一种信息环境」这一构念动机的同域 (银行 × 媒体) 文献参照, 用于说明 F162 concern_score 把负面强度与报道量结合刻画信息环境的立意。⚠ 原文为制度层面变量与近乎零结果, 不构成本项目任何列的构造来源或效度证据。
  - 〔Crossref 回读标题: Bank runs and media freedom: What you don’t know won’t hurt you?〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Thomas, W. B., Wang, Y., & Zhang, L. (2024). Algorithmic Trading and Forward‐Looking MD&A Disclosures. Journal of Accounting Research, 62(4), 1533-1569. https://doi.org/10.1111/1475-679x.12540
  - *锚定* — 该文的自变量为算法交易 (AT), 因变量为 MD&A 前瞻性披露的逐年修订程度, 稳健性中另用 '前瞻句数' 与语调修订作替代测度。可作为 F316 所在「前瞻性语句 (FLS) 文本测度」族的顶刊前沿存在性参照 —— 证明前瞻句的识别与计数在顶刊层面是被接受的构念操作化。但原文并未构造「前瞻句数 / 全部句数」的占比测度, 亦未拆分未来动作词门与未来时间标记门, 故不构成 F316 分母口径或单/双门二臂设计的 method-origin。
  - 〔Crossref 回读标题: Algorithmic Trading and Forward‐Looking MD&amp;A Disclosures〕
  - 〔已接线家族 (1): F316〕


### 十补-20. 银行结构控制与交互项 (bank_scale / is_soe / stress_period / tone_x_*)

> 净增 12 条(其中 2024–2026 者 12 条; **1 条未接入任何家族**, 见各条标注)。**已接线家族** (10): F082, F342, F449, F474, F489, F510, F595, F597, F598, F599

- 【2024–2026】Chen, Q., & Zhan, X. (2026). Deposit insurance, bank competition, and corporate lending in China: A loan-level analysis. Research in International Business and Finance, 89, 103456. https://doi.org/10.1016/j.ribaf.2026.103456
  - *锚定* — 原文用贷款层级 (loan-level) 数据研究中国存款保险制度与银行竞争对企业信贷的影响, 为 F595 的 depins_post = 1[year >= 2015] 断点提供 2015 年存保制度冲击在中国银行业的前沿实证锚点。⚠ 原文为贷款层级分析、DV=企业信贷, 本项目为银行×年聚合面板且无贷款层数据; F595 处该断点仅作交互项的调节变量, 原文不涉媒体语调。⚠ 原文摘要不可得 (Crossref/OpenAlex/S2 三源均无), 除标题外的内容主张均未经证实, 不得据以声称其含国有产权分组分析。
  - 〔Crossref 回读标题: Deposit insurance, bank competition, and corporate lending in China: A loan-level analysis〕
  - 〔已接线家族 (1): F595〕
- 【2024–2026】Stromer-Galley, J., McKernan, B., Zaman, S., Maganur, C., & Regmi, S. (2026). The Efficacy of Large Language Models and Crowd Annotation for Accurate Content Analysis of Political Social Media Messages. Social Science Computer Review, 44(3), 466-487. https://doi.org/10.1177/08944393251334977
  - *锚定* — 原文实证评估 LLM 与众包标注在文本内容分析中的准确性表现。F449/F474 的 neg_frac/pos_frac 分子来自三家 LLM 对篇章情感作三分类后的多数投票共识 (llm_vote_score ∈ {-1,0,+1}), 该文为「以 LLM 替代/辅助人工标注做类别判定」这一测度路径提供效度评估锚点。
  - *迁移边界* — 原文语料为英文政治社交媒体消息, 标注任务为政治内容类别; 本项目为中文银行金融科技新闻的情感三分类, 语言/领域/标注体系均不同。原文评估的是单模型与众包的对比, 未评估本项目所用的三家模型多数投票聚合规则, 亦未涉及 gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash 这一具体组合。
  - 〔Crossref 回读标题: The Efficacy of Large Language Models and Crowd Annotation for Accurate Content Analysis of Political Social Media Messages〕
  - 〔已接线家族 (2): F449, F474〕
- 【2024–2026】Zheng, Y., Li, R., Ren, S., & He, F. (2026). The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience. Emerging Markets Finance and Trade, 1-17. https://doi.org/10.1080/1540496x.2026.2698629
  - *锚定* — 原文以中国金融科技创新监管试点 (即监管沙盒) 为准自然实验, 研究其对银行金融科技发展与风险韧性的影响。这与 F489 的 sandbox_treat_year (按城市/省份首次纳入沙盒试点年份分组匹配) 是同一政策冲击、同一处理分配逻辑, 且落在银行层面 — 是本桶最贴近的前沿实证存在性证明。原文的银行异质性讨论与 F097 的规模分组亦相关。
  - *迁移边界* — 原文 DV 为银行金融科技发展指数与风险韧性指标; 本项目 sandbox 哑变量族服务于媒体语调/关注度类 DV。原文的试点分期与本项目 config/policy_shocks.json::fintech_sandbox 三阶段分组是否逐城逐年一致未经核对, 引用时不得声称口径等同。原文对 F097 的关联属附带的规模异质性, 非其主测度。
  - 〔Crossref 回读标题: The Catalytic Sandbox: How the FinTech Innovation Regulatory Pilot Fuels Bank FinTech Development and Risk Resilience〕
  - 〔已接线家族 (2): F489, F597〕
- 【2024–2026】Aguilar-Loyo, J. (2025). A comparative analysis of two-way fixed effects estimators in staggered treatment designs. Journal of Econometrics, 251, 106059. https://doi.org/10.1016/j.jeconom.2025.106059
  - *锚定* — 原文系统比较交错处理设计下各类 TWFE 估计量 (重点为 extended TWFE), 推导其与 DiD 估计量的等价分解, 并证明估计量选择取决于目标参数与应用特征、无单一最优。F489 的 sandbox 处理分配正是交错采纳设计, 该文可作为该设计下估计量选择的方法学参考。⚠ 原文为纯计量方法学 (含理论推导与示例), 不针对任何具体经验场景, 不背书本项目的处理分配规则; 亦不构成对面板主键结构列 (F549) 的任何依据。
  - 〔Crossref 回读标题: A comparative analysis of two-way fixed effects estimators in staggered treatment designs〕
  - 〔已接线家族 (1): F489〕
- 【2024–2026】Betts, C. M., & Cao, Y. (2025). How Does State Ownership Affect Firm Innovation? Evidence from Chinese Manufacturing Firms. The World Bank Economic Review, lhaf024. https://doi.org/10.1093/wber/lhaf024
  - *锚定* — 原文识别中国语境下国有产权对创新行为的影响, 其核心自变量即国有/非国有的产权二分。F342 的 is_soe = 1{bank_type == "soe"} 是同款产权哑变量, F598 = llm_vote_tone × is_soe 是其交互 — 该文为「中国国有产权是实质性的异质性调节维度」提供近期实证依据。
  - *迁移边界* — 原文样本为中国制造业企业 (非银行), DV=企业创新; 本项目 F342 施加于商业银行, 且国有界定来自面板 bank_type 列 (缺失时恒置 0 并记 WARNING), 与原文的国有企业界定标准不同。原文完全未涉及媒体语调, 对 F598 的交互项仅提供「产权分组有意义」的一般性依据, 不涉及语调×产权的具体机制。
  - 〔Crossref 回读标题: How Does State Ownership Affect Firm Innovation? Evidence from Chinese Manufacturing Firms〕
  - 〔已接线家族 (2): F342, F598〕
- 【2024–2026】Ding, N., Xu, L., Wu, X., & Dai, Z. (2025). Explicit deposit insurance, active risk taking, and bank efficiency in China. International Review of Financial Analysis, 102, 104139. https://doi.org/10.1016/j.irfa.2025.104139
  - *锚定* — 原文研究中国显性存款保险制度对银行主动风险承担与效率的影响。F595 的 depins_post = 1[year >= 2015] 断点正是以《存款保险条例》2015-05-01 施行为界, 该文是该制度冲击在中国银行业的前沿实证锚点。
  - *迁移边界* — 原文 DV 为银行风险承担与效率测度; 本项目 F595 是 llm_vote_tone{track} × depins_post 的交互项, DV 与构念均不同。原文研究存保制度的实体经济后果, 未涉及媒体语调, 亦不对语调×存保交互的理论机制作任何主张。
  - 〔Crossref 回读标题: Explicit deposit insurance, active risk taking, and bank efficiency in China〕
  - 〔已接线家族 (1): F595〕
- 【2024–2026】Lin, Y., Li, L., Yang, X., & Yan, X. (2025). Geographic expansion of banks and enterprise investment efficiency: Structural evidence from China. International Review of Financial Analysis, 100, 103967. https://doi.org/10.1016/j.irfa.2025.103967
  - *锚定* — 原文研究中国银行的地理扩张 (跨区域布局) 及其经济后果, 其识别依赖将银行与具体省/市地理位置相匹配。F082 的 bank_province/bank_city 正是由 config/bank_addresses.json 把银行名映射到省与市 — 该文为「中国银行的省市地理归属是有经济含义的结构性变量」提供同域实证锚点。
  - *迁移边界* — 原文的地理变量刻画的是银行分支机构的跨区域扩张 (随时间变化的网点布局), 本项目 F082 仅是银行总部地址的静态省/市标识字符串 (未匹配→''), 不含分支网点信息、不随年份变化。原文 DV=企业投资效率, 与本项目无重叠。
  - 〔Crossref 回读标题: Geographic expansion of banks and enterprise investment efficiency: Structural evidence from China〕
  - 〔已接线家族 (1): F082〕
- 【2024–2026】Nagengast, A. J., & Yotov, Y. V. (2025). Staggered Difference-in-Differences in Gravity Settings: Revisiting the Effects of Trade Agreements. American Economic Journal: Applied Economics, 17(1), 271-296. https://doi.org/10.1257/app.20230089
  - *锚定* — 原文将扩展双向固定效应 (ETWFE) 交错 DiD 估计量嵌入结构引力模型重估贸易协定效应, 表明传统设定下的估计可能被显著低估。与 F489 的 sandbox_treat_year / sandbox_treated / sandbox_post 交错处理分配同属 staggered adoption DiD 设计谱系, 可作为该设计在前沿实证中被采用的存在性证明。⚠ 原文未展示事件研究 lead/lag 相对期系数图, 不构成对 F489 的 sandbox_lag{0..3}/lead{2,3} 相对期哑变量构造的直接依据; 且原文为国家对层级引力模型 (DV=双边贸易流), 与本项目银行×年媒体语调面板在层级、DV、处理分配规则上均无重叠。
  - 〔Crossref 回读标题: Staggered Difference-in-Differences in Gravity Settings: Revisiting the Effects of Trade Agreements〕
  - 〔⚠ **本条未接入任何指标家族** — 接线层逐族相关性复核判定它与各候选家族的公式无实质关联 (即本项目自己判它为 citation padding)。保留于本补编仅作**文献综述参考**, **不支撑任何指标**; 其 DOI 虽入白名单池, 但零家族引用。〕
- 【2024–2026】Dette, H., & Schumann, M. (2024). Testing for Equivalence of Pre-Trends in Difference-in-Differences Estimation. Journal of Business & Economic Statistics, 42(4), 1289-1301. https://doi.org/10.1080/07350015.2024.2308121
  - *锚定* — 原文提出 DiD 平行趋势前期检验的等价性检验方法 (equivalence testing), 直接针对事件研究中 lead 系数的检验解释问题。F489 构造 sandbox_lead{2,3} 且以 k=-1 为省略基期, 其识别有效性依赖前期系数的检验, 该文为此提供检验方法学锚点。
  - *迁移边界* — 原文提供的是检验程序本身, 不涉及金融科技监管沙盒或银行业数据; 本项目 F489 的 lead 系数是否已按该文的等价性检验实施, 属本项目自身的实施选择, 原文不构成对本项目已有做法的背书。
  - 〔Crossref 回读标题: Testing for Equivalence of Pre-Trends in Difference-in-Differences Estimation〕
  - 〔已接线家族 (1): F489〕
- 【2024–2026】Ji, Z., Ye, N., & Kong, D. (2024). The contraction of Chinese shadow banking and corporate investment behavior: Evidence from the background of the “New Rules on asset management”. China Economic Quarterly International, 4(2), 119-132. https://doi.org/10.1016/j.ceqi.2024.06.003
  - *锚定* — 原文以中国资管新规导致的影子银行收缩为背景识别其经济后果。F510 的 stress_period = 1{year ∈ {2015, 2018, 2020}} 中的 2018 年正是以资管新规去杠杆为设定依据, F599 是该哑变量与语调的交互 — 该文为 2018 作为中国金融体系压力年份提供实证依据。
  - *迁移边界* — 原文 DV 为企业投资行为, 分析单位是企业; 本项目 F510 是银行×年层面的 0/1 年份哑变量。原文只覆盖 2018 资管新规这一个事件, 对 F510 另两个年份 (2015 股灾去杠杆前夜、2020 新冠冲击) 不提供任何依据 — 该三年并置为单一 stress_period 属本项目的研究者设定, 原文不背书。
  - 〔Crossref 回读标题: The contraction of Chinese shadow banking and corporate investment behavior: Evidence from the background of the “New Rules on asset management”〕
  - 〔已接线家族 (2): F510, F599〕
- 【2024–2026】Ni, T., Ren, Y., & Choi, J. (2024). Deposit insurance system and commercial bank profitability: A quasi-natural experiment based on the deposit insurance regulations. Finance Research Letters, 67, 105763. https://doi.org/10.1016/j.frl.2024.105763
  - *锚定* — 原文明确将《存款保险条例》的施行作为准自然实验来识别其对商业银行盈利能力的影响。这与 F595 把 depins_post 设为 1[year>=2015] 单一时点断点哑变量的做法, 是对同一制度事件的同款识别策略, 可作为该断点设定的实证先例。
  - *迁移边界* — 原文为单一时点冲击的盈利能力 DiD; 本项目 F595 将该断点仅用作交互项的调节变量 (与三轨 LLM 语调相乘), 并非独立估计存保的处理效应。原文 DV=盈利能力, 与本项目媒体语调类构念无重叠。
  - 〔Crossref 回读标题: Deposit insurance system and commercial bank profitability: A quasi-natural experiment based on the deposit insurance regulations〕
  - 〔已接线家族 (1): F595〕
- 【2024–2026】Nogueira, G., Farinha, L., & Blattner, L. (2024). Not All Shocks Are Created Equal: Assessing Heterogeneity in the Bank Lending Channel. Management Science, 70(10), 6942-6965. https://doi.org/10.1287/mnsc.2023.00104
  - *锚定* — 原文以葡萄牙信贷登记与证券层银行资产负债表数据, 横向比较欧债危机中三个正面冲击 (PSI 债务重组 / OMT / QE) 的传导, 证明收益率影响并非衡量银行信贷渠道强度的充分统计量: 唯有 QE 显著改变银行主权债持有与对企业和家庭的信贷, 机制为资本充足率与抵押品激励削弱再资本化渠道、以及 QE 独有的组合再平衡渠道。该文为「不同冲击期的效应不可等同、冲击期身份本身是实质性的调节维度」提供顶刊层面依据, 与 F599 = llm_vote_tone × stress_period 的冲击期交互设定对口。⚠ 原文 DV 为银行信贷供给, 冲击为非常规货币政策事件, 样本为葡萄牙/欧洲银行体系, 不涉及媒体文本。⚠ 原文的银行异质性维度是**资本充足率 (capitalization)**, **非银行规模** — 不构成对 F097 规模四分序数或 F597 语调×规模交互的任何依据。⚠ stress_period = 1{year ∈ {2015,2018,2020}} 是本项目自定义的中国特定压力年份哑变量, 原文无此设定。
  - 〔Crossref 回读标题: Not All Shocks Are Created Equal: Assessing Heterogeneity in the Bank Lending Channel〕
  - 〔已接线家族 (1): F599〕


---

## 二、核验台账

- **发现层自弃**: 189 条(查不实 / 题名不符 / 撤稿 / 已在池)。
- **对抗层判杀**: 5 条。逐桶对抗判定分布: `{"keep": 130, "overclaim": 161, "wrong_paper": 5, "metadata_error": 2}`。
- **主控权威回填丢弃**: 1 条。清单:
  - `10.47004/wp.cem.2024.1024` — incomplete_authoritative_metadata
- **overclaim 条目的边界字段处置 (刻意设计)**: 对抗层判「夸大」的条目, 其发现层自写的`migration_boundary` 与被判杀的原始 rationale **出自同一前提**, 已随之失效, 故本补编**一律不印**该字段, 只印对抗层撰写的降级版 *锚定* (其中 82% 已自带边界/限定语)。实证依据: `10.1017/s175577392610054x` (Beltran et al., 2026) 的降级版定谳其样本为**墨西哥单一国家**, 而发现层旧边界仍写作『跨国/欧洲语境』—— 二者直接冲突。keep / metadata_error 条目的边界未被判杀, 照印。
- **agent 自报 vs 权威回读 drift**: 1 处(一律以权威回读覆盖, agent 值全弃):
  - `10.1109/cifer62890.2024.10772990` year: agent=2023 → 权威=2024

> 全语料决定性闸 = `python news_process/scripts/audit/audit_dois.py`(直连 Crossref/DataCite, 不耗模型 token, 100% 覆盖非抽样)。
> 引文白名单差集闸 = `python -m news_process.scripts.audit.check_longdesc_whitelist`。


---

## 三、结构性代价的诚实披露 (本补编的负面结果, 不予粉饰)

### 3.1 顶刊占比下降: 49.7% → 44.9%

本轮接线后, 全卷 `top_journal_mix` 由 top **49.7%** 降至 **44.9%**, `unlisted` 由 26.3% 升至 **29.6%**,
「(top+field 内) 非 top 占比 >30%」软 WARN 由 471 增至 544 (+73)。**这是本补编的真实代价, 如实记录。**

成因经实测拆解 (245 条新锚点按 `classify_citation_detailed` 五分类):

| 分类 | 唯一锚点 | 占比 |
|---|---|---|
| unlisted (未列名刊) | 131 | 53.5% |
| field (清单列名领域刊) | 56 | 22.9% |
| wp-preprint | 30 | 12.2% |
| top (清单顶刊) | 28 | 11.4% |

**但 `unlisted` ≠ 低质刊。** `config/top_journal_list.yaml` 的清单域, 按其文件头自述, 是依据
「仓库 manuscripts/paper_spec **实际引用域**」建成 (top 40 刊 + field 37 刊)。本补编首次成规模引入
该历史引用域之外的venue (计算语言学会议 EMNLP、地理学、语言资源、会计学区域刊等), 故大量落入未列名。
**实证反例**: `Review of Economics and Statistics` (REStat) 在 top 与 field **两张清单中均不存在**,
因而本补编的 Frandsen、Leslie 与 McIntyre (2025, cluster jackknife IV) 与 Boucher 与 Houndetoungan
(2025, 部分网络数据下的同侪效应估计) 两条 REStat 锚点被判 `unlisted` —— 而 REStat 的学术地位显然
高于现清单中已列为 top 的若干综述刊。其余未列名刊亦多为 *Accounting & Finance* / *The British
Accounting Review* / *China Journal of Accounting Research* / *Strategic Entrepreneurship Journal* /
EMNLP Proceedings 等正当学术出处, 未见掠夺性刊。

**本补编刻意不动 `top_journal_list.yaml`**: 在本轮审计中把清单改宽以抬高自身占比数字, 等同于
「审计中途移动标尺」, 属自我授权。清单是否补入 REStat 等遗漏刊, 应作为**独立议题**由用户裁定,
不与本补编捆绑。家族级**硬闸**(每 final 家族 ≥1 条 top 锚)本轮 **0 致命项**, 即每个家族仍保有
顶刊支撑底线; 上述占比变化只触发刻意降级的软 WARN (v2.11 起该项即为 WARN, 非硬闸)。

### 3.2 novelty 口径说明 (分母排除豁免家族)

`novelty_2023plus` = **50.02% → 55.3%** (3156/5703, 硬闸 ≥50%; 本节数字由脚本**实读家族库**算出, 非硬编码)。须说清两点:
① 分母**排除 61 个 `novelty_exempt` 家族**(构念定义型, 引文池以奠基经典为主, 其 frontmatter 声明
   `novelty_exempt_rationale` 即整族出统计池) —— 该豁免机制**非本轮引入**, 系既有设计;
② 本轮**未新增任何豁免家族**, 亦未改动任何家族的豁免声明 —— 55.4% 全部来自**真实新增的 2024-2026 引文**,
   不存在「靠扩大豁免做数」。起跑前 50.02% 距硬闸仅 0.02 个百分点 (再多 1 条 2023 前引文即判死),
   本轮把余量做厚至 5.4 个百分点。

### 3.3 锚点级落地率: 212/245 条接线, 33 条未接入任何家族

**〔已接线家族〕行的口径 (终审整改后)**: §一 各条的〔已接线家族〕**由 `patches.json` (接线层实际
落地结果) 机械派生**, 即「按构造为真」—— 不再沿用发现层的**提名意向**。
⚠ **本项整改源于终审 P1**: 初版沿用提名意向, 致 757 条 (doi, fid) 断言中 **168 条 (22.2%) 与家族 md
实况不符** (最严重一条声称锚定 20 族、实际 6 族)。根因是接线层的相关性把关弃用了 **840 条**配对,
而补编未回写。现已按实际接线重生, 该类断言归零。

**33 条未接入任何家族的锚点**: 逐条在 §一 内显式标注 (不隐藏、不从计数中抹去)。它们经权威回读、
撤稿筛查与对抗复核, 文献本身**真实无误**, 但**本项目自己的接线层**判定它们与各候选家族的公式无实质
关联 (即判为 citation padding)。处置: **保留于本补编作文献综述参考, 但不支撑任何指标**; 其 DOI 虽随
补编并入白名单池 (故 `audit_dois.py` 池计 245 条), 家族引用数为零。
读者若只关心「支撑指标的锚点」, 应以 **212 条 / 328 个家族**为准。

**接线落差的两个方向** (均为设计内行为):
① 「补编某条列出的家族 ⊉ 发现层提名」—— 相关性把关弃用所致 (弃用理由逐条记录在 `patches.json::rejected`);
② 「某家族收录了补编未提名它的条目」—— 第一轮未获分配的 60 个家族走了**同桶姐妹族锚点池**扩展所致。

---

## 四、顶刊标准对抗终审的整改台账 (18 confirmed / 6 refuted)

本补编交付前经 **8 维度 × (1 审 + 1 独立复核) = 16 agents** 的顶刊标准对抗终审。终审明确**证伪**了
「万无一失、完美无缺」这一主张 —— 以下为**被抓出并已整改**的实质缺陷, 如实登记:

| # | 严重度 | 缺陷 | 整改 |
|---|---|---|---|
| 1 | P1 | **3 条预印本实已正式发表**, 却以 `[Working Paper]`/`[Preprint]` 印出, 且「未经同行评审」被当作**承重降格理由**写进 8 份家族 md —— 该状态陈述为假。最讽刺者: 对抗层据「未经同行评议」把某条降级, 即**诚实降级建立在错误前提上**。根因 = 主控回填只回读**被提名 DOI 自身**, 从不反查同题正式版。 | 全部改引 version-of-record: `ssrn.5362858`→**JIBS 56(7) 921-936**; `ssrn.5644710`→**Financial Review 60(4) 1129-1160**; `arXiv:2308.08031`→**IEEE CIFEr 2024**。8 处家族 citations 已换、发表状态措辞已删。 |
| 2 | P1 | **Pinto & Siano 构念张冠李戴**: 补编称其考察「**跨语言**迁移困难 / 英语词表在**他语语境**适用性存疑」, 并在 F412 抬为「直接动因」。实则原文语料为 **85 国 200,960 份英文财报电话会**, 定谳主因是**文化距离**而非语言, 全文**无词表翻译、无非英语语料**。该错前提已扩散进 6 份家族 md。 | 按原文实际口径重写 (美国基准词表**移出美国语境即使文本仍是英文**信号亦衰减约 30% → 移入中国语境**既跨文化又加翻译**风险更大), 该口径仍足以支撑本族设计; F412「直接动因」降级为「动机之一」。 |
| 3 | P1 | **12 条悬空叙述** (F481/F484/F485): 悬空收尾层剔除了这些 DOI, 但**第一轮的叙述未同步删除** → 正文谈了却不引。机械闸因 `_PROSE_CITE_RE` 只认 `(年份)` 紧闭形态、看不见 `(年份, 刊名)` 写法而**完全漏检**。 | 16 个收尾族**整体回退到接线前状态并按终态 DOI 重写**融入段 (根治悬空 + 同时消除下条的重复段)。 |
| 4 | P1 | **F602 张冠李戴** (既有缺陷, 本轮**未修反而新增第 3 处**): 「**Weick** & Zajac (1998, **Academy of Management Journal**)」—— 实为 **Westphal** & Zajac (1998, **Administrative Science Quarterly**, 43(1), 127)。 | 全部 `Weick`→`Westphal`、`AMJ`→`ASQ`, 并补入 `10.2307/2393593` 至 citations。 |
| 5 | P1/P2 | **〔锚定家族〕22.2% 反事实** (168/757 条 (doi,fid) 断言与家族 md 实况不符)。 | 改由 `patches.json` **机械派生**, 按构造为真 (见 §3.3)。 |
| 6 | P2 | **APA 题名断词**: `Word N -Grams`(应 `Word N-Grams`) / `B razilian`(应 `Brazilian`) —— `clean_text` 把 Crossref **XML pretty-print 换行**一律折叠成空格所致, 其中一条已出厂进 F070。 | 改为**有原则的还原规则**: 开标签前换行→空格, 闭标签后换行→无; 两例同时成立。 |
| 7 | P2 | **Crossref 全大写作者名原样透传** (`LOUGHRAN, T.` / `HIRSHLEIFER, D.`), 不符 APA 且与全库风格断裂。 | 新增 `fix_caps`: 仅整串全大写时还原, 混合大小写 (`van Lent`/`McDonald`) 一律不动; Mc/Mac/O' 前缀显式补正。 |
| 8 | P2 | 交付方自称「告警 +75 **全为**顶刊软 WARN」不实。此前的「0 新增」结论源于**集合差分**掩盖了**计数增长**。 | 更正为**按类别计数**口径。终态实测: 顶刊软 WARN **471→544 (+73)**; 正文引注弱断言 **224→221 (−3, 净减少)** —— 本轮反而修掉了既有的 F602/F506 悬空引注。 |

**被独立复核推翻的 6 条** (记录在案, 供后续勿再立案): 「Devlin 红旗系 ACL deposit 空标题」的定性之争
(复核证 Crossref 未 404, referee 误把兜底源状态码当主源成因)、`_new_dois_ledger.json` 的 F463
`apa_line` 冻结值「自相矛盾」(实为对字段语义的误读: apa_line 是准入当时的快照, 非当前渲染值) 等。

### 4-bis. 终局签核 (10 维度 × 审+独立复核 = 20 agents) —— 又抓出 12 类, 全已整改

⚠ **上一轮 §四 的 18 条整改, 其本身从未被任何评审看过** —— 终局签核的首要职责即复验整改。
结果: **整改本身又被抓出 12 类缺陷** (含整改**引入**的新缺陷)。全部已修, 如实登记:

| # | 严重度 | 缺陷 (终局签核抓出) | 整改 |
|---|---|---|---|
| T1 | P1 | **整改只落到家族库、未落到补编本体**: §一 Pinto 条的 *锚定* / *迁移边界* 仍印「该工作论文 + **跨语言**」—— 而 §四 却自称「发表状态措辞已删 / 按原文实际口径重写」。**交付物自己打自己的脸**。 | §一 该条 *锚定* 与 *迁移边界* 均按原文实际口径 (跨**文化**; 85 国**英文**语料; 主因文化距离) 重写, 并标明已刊 JIBS。 |
| T2 | P1 | **整改 #1 引入新缺陷**: VOR 换 DOI 后未重跑机械派生 → Pinto (JIBS) 与 Vamvourellis (CIFEr) 两条**实际接线 6 族与 2 族**的锚点被反向误标为「**零家族引用 / 本项目自己判它为 citation padding / 不支撑任何指标**」。 | 〔已接线家族〕改为**直接实读盘上家族 md frontmatter** (见 §3.3 演进史 ③), 对任何中间产物的陈旧免疫。 |
| T3 | P1 | **零接线计数三重自相矛盾**: 同一文件内 §0 印「35 条」、§3.3 标题印「**1 条 / 244**」、实测 33 条。根因 = 桶循环内的局部变量 `n_orph` **遮蔽**全局同名变量, 循环后残留为「最后一个桶」的值。 | 循环变量改名 `bucket_orph`; 三处口径与盘上真值统一为 **212/245 接线、33 条零接线、328 族**。 |
| T4 | P1 | **「改全了吗」失败**: F602 的 Weick→Westphal 修好了, 但**同款张冠李戴的未清同伴** F049「Weick 与 Zbaracki」漏网 (且零引文背书)。 | F049 改 Westphal 与 Zajac + 补入 `10.2307/2393593`。呼应本仓既有教训: **改一处必 grep 全文同构念的所有表述**。 |
| T5 | P1 | **整改 #7 只修生成器、未回灌出厂物**: `clean_text` 已修好, 但 **F070 仍出厂 `Word N -Grams`** (正是「整改」commit 亲手写入)。 | 以修正后的权威 backfill **回灌**家族 md citation 字段 (F070 题名), 并重渲染。 |
| T6 | P1 | **整改 #8 同款**: `fix_caps` 只修了被点名的 LOUGHRAN, 但 **4 族仍出厂全大写作者** (`HIRSHLEIFER, D.` 等), 其中 **3 处已渗入手写正文** —— 生成器修法永远够不到正文。 | frontmatter 回灌 4 族 + 正文 3 处全大写姓氏还原 (`HIRSHLEIFER`→`Hirshleifer` 等)。 |
| T7 | P2 | **内部字段名泄漏进交付正文**: 对抗层用 `migration_boundary:` 当小标题写降级版 → 机器字段名随交付物出厂 (**15 条**)。 | 统一改为中文标签「迁移边界」(内容保留)。 |
| T8 | P2 | **内部评审私话泄漏**: `**建议: 若正文引文预算紧张, 本条应优先删除。**` 这类**给编者的私话**印进了交付物。 | 净化剔除。 |
| T9 | P2 | **孤儿标点**: VOR 替换用正则剥「未经同行评审」小句后, 留下句首孤儿标点 (`。边界: ...`), 且 fire.12442 的 *锚定* 整段被剥空只剩一个句号。 | 净化 + 该条 *锚定* 按已刊 Financial Review 口径重写。 |
| T10 | P2 | **§3.1/§3.2 数字与 gate 实跑不符** (unlisted 29.5% vs **29.6%**; novelty 分母 5698 vs **5699**; 软 WARN +72 vs **+73**)。 | 全部对齐 gate 实跑回读值。 |
| T11 | P2 | **§policy 自我证伪**: 声明「overclaim 条目一律不印 migration_boundary」, 但 15 条 *锚定* 正文里就含该字段名。 | 与 T7 同批净化后, 该声明与实况一致。 |
| T12 | — | **系统性反查** (referee 点名要求): 除已修的 3 条外, 其余 **27 条 wp/arxiv 是否也有未收录的正式版**? | 逐条 Crossref 同题反查 (阈值 85% token 重叠) → **0 条**真命中 (唯一疑似为哲学书章 *Steadfast Views of Disagreement* vs NBER *Disagreement of Disagreement*, 经回读证伪)。**该缺陷类已收口**。 |

### 4-ter. 终局签核**第二轮复核**又抓出 2 项 (原判「独立议题」者, 本轮升格整改)

上一版 §4-bis 曾把两项判为「非本轮引入 / 独立议题」暂不处理。第二轮复核 (10 维 × 审+复核) 认定
其中两项**本轮确有贡献且可低成本根治**, 遂升格整改:

| # | 严重度 | 缺陷 | 整改 |
|---|---|---|---|
| U1 | P2 | **APA 7 §9.19 违反**: 题名以 `?`/`!` 收尾时该终止标点应**取代**句点, 而生产渲染器 `render_citation_apa` 恒加 `.` → 全库 **305 处 `Title?.`** (本轮新增约 15 处)。 | **改生产渲染器** (题名末为 `?`/`!` 时不再补句点), **重渲染全部 655 族** → 258 族渲染尾节更新 (diff 逐字节验证为**纯标点**: 310 删 / 310 增, 0 实质变化); 补编 APA 同步。全库 + 补编 `?.` 残留 **= 0**。此为改进整个 codebook 的 APA 合规性, 非仅本补编。 |
| U2 | NIT | **Zipf 条目误译**: 补编把原文三下位构念之一 lexical **sophistication** 误译为「词汇复杂度」, 与其**上位**构念 lexical complexity 自我重叠 (OpenAlex 摘要证实原文三构念 = lexical diversity / density / **sophistication**, 上位 = lexical complexity)。 | 改为「词汇成熟度 (lexical sophistication)」, 并补上相关性方向 (指数与前二者负相关、与成熟度正相关)。 |

**仍判为「非本轮引入」而留作独立议题的** (如实记录):
- `</content>` / `</invoke>` 工具调用 XML 标记残留 **30 个家族 md** —— 逐一对比 `1b9704d0` 证实本轮前即存在;
- `F387` 行首 `+ ` 列表符、5 处 `[0, 2](…)` 数学区间被 markdown 读成链接 —— 既有, 且生产 lint
  模式表只有 heading/bold/table/fence, 不覆盖 list/link;
- `Luo & Li (2025, FRL)` 被 `pipeline/panel/geography.py:907` 与 F481 既有正文引用, 但**全池无该 DOI**
  —— 既有锚点缺口, 本轮未新增该引用的实质内容;
- **顶刊清单 (`top_journal_list.yaml`) 补入 REStat 等遗漏刊** —— 审计中途改宽清单属自我授权, 挂用户裁定;
- **姐妹消融臂的锚点把关一致性** (如 Iqbal & Pfarrer 2025 在 bian 母族 F120 收、在 advonly 臂 F232 弃)
  —— 各家族的实际 citations 逐条可辩护 (母族承载构念、消融臂不必重引每一锚), 无删改必要; 唯 patches.json
  内部弃用注记的「真正归属」措辞偶有不精确 (F485 注记称仅属 F488, 实则 F486 亦用), 属内部台账瑕疵、
  不影响任何交付产物, 留待下一份补编统一收口。
