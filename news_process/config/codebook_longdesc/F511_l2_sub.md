---
family_id: F511
columns:
- sub_frac
- sub_frac_sc
- sub_frac_ss
unit: 占比 (proportion, 无量纲, 取值域 [0,1])
formula: "sub_frac = n_articles_sub / n_articles_llm_valid; sub_frac_sc = n_articles_sub_sc_ctx / n_articles_llm_valid_ctx; sub_frac_ss = n_articles_sub_ss_ss / n_articles_llm_valid_ss"
producer: news_process/pipeline/sentiment/tone_llms.py (文章级三维分类投票) ; news_process/pipeline/panel/encode.py (bank-year 面板占比聚合)
upstream:
  - 15_fintech_intensity.parquet (三轨文本 content_full/content_ctx/content_ss + 金科强度列)
  - 21_tone_llms.parquet (innovation_substantiveness_{full,ctx,ss} 三家投票分类)
citations:
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: "AI washing: Strategic disclosure and backlash"
  venue: Finance Research Letters
  vol: 95
  pages_or_artno: 109684
- doi: 10.1287/mnsc.2024.07420
  type: journal
  authors: Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C.
  year: 2026
  title: "\"Glossy green\" banks: The disconnect between environmental disclosures and lending activities"
  venue: Management Science
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking & Finance
  vol: 164
  pages_or_artno: 107191
- doi: 10.1287/stsc.2023.0188
  type: journal
  authors: Westphal, J. D.
  year: 2023
  title: "Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale"
  venue: Strategy Science
  vol: 8
  issue: 2
  pages_or_artno: 221-232
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
- doi: 10.1177/1536867X19830877
  type: journal
  authors: Roodman, D., Nielsen, M. Ø., MacKinnon, J. G., & Webb, M. D.
  year: 2019
  title: "Fast and wild: Bootstrap inference in Stata using boottest"
  venue: The Stata Journal
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: The Journal of Finance
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: "Identification of endogenous social effects: The reflection problem"
  venue: The Review of Economic Studies
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: "Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure"
  venue: Organization Science
  vol: 26
  issue: 3
  pages_or_artno: 705-723
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: "The symbolic management of strategic change: Sensegiving via framing and decoupling"
  venue: Academy of Management Journal
  vol: 49
  issue: 6
  pages_or_artno: 1173-1193
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: Administrative Science Quarterly
  vol: 39
  issue: 3
  pages_or_artno: 367-390
- doi: "10.1016/j.techsoc.2025.103145"
  title: "Fake it till you make it: Digital washing and corporate innovation"
  authors: "Zhou, H., Liu, Z., & Huang, C."
  year: 2026
  venue: "Technology in Society"
  type: "journal"
- doi: "10.3390/systems12060197"
  title: "Symbolic or Substantive? The Effects of the Digital Transformation Process on Environmental Disclosure"
  authors: "Ji, H., Sheng, S., & Wan, J."
  year: 2024
  venue: "Systems"
  type: "journal"
- doi: "10.1007/s10490-025-10098-2"
  title: "Substantive investment or symbolic disclosure toward digital transformation? The impact of entrepreneurial orientation and political connections"
  authors: "Liu, L., Li, Z., & Zhu, Q."
  year: 2026
  venue: "Asia Pacific Journal of Management"
  type: "journal"
new_dois:
  - "10.1016/j.techsoc.2025.103145"
  - "10.3390/systems12060197"
  - "10.1007/s10490-025-10098-2"
---

## CORE

【构念与来源】
本家族刻画每家银行每年被媒体报道的金融科技创新中, 被判定为"实质性"(substantive) 的报道所占的比重, 是 P3 论文 (bank_fintech_substance) 的正文级主处理变量。构念的思想母体是 Westphal 与 Zajac (1994, 1998) 在管理学顶刊提出的"实质—象征"二分: 一项组织行动既可能是真正改变资源配置、业务流程与技术底盘的实质性变革, 也可能只是面向外部受众的象征性姿态 (symbolic gesture), 用以获取合法性而不改动内部运作。Fiss 与 Zajac (2006) 进一步把这一二分与"脱耦"(decoupling) 机制联系起来: 组织在对外沟通 (framing) 与实际实践之间可以系统性地脱钩。落到本项目情境, 一篇讲"某银行搞金融科技"的新闻, 究竟是在报道一次真实落地的技术投入与产品重构 (实质性), 还是在转述一句战略口号、一次发布会造势或一纸合作备忘录 (象征性), 正是本家族要区分的核心。把这一逐篇判断在 bank-year 层面聚合成占比, 就得到"这家银行这一年被外界看到的金科叙事里, 有多大份额是有真材实料的", 它是度量银行金科转型"言行是否脱耦"的媒体侧代理变量。

数据来源是媒体报道全文语料经流水线逐级加工后的产物。上游 stage 21 (tone_llms) 让三个相互独立的大语言模型 (gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash, 相当于三位独立的金融文本标注员) 对每篇通过金科精筛的报道给出 innovation_substantiveness 分类标签 (取值"实质性"或"象征性"); 三家投票, 严格多数决产出该篇的共识标签, 平票时按保守先验降级为"象征性"(tie_default, uniform-prior MAP, 宁可低估实质性也不虚高)。随后 stage 40 (encode) 把逐篇标签在 bank-year 网格上聚合: 分子是被判"实质性"的报道篇数, 分母是该 bank-year 通过 full-only 留篇门控的有效报道篇数, 相除得占比。

为什么要在"实质—象征"这一维度上区分金科报道? 银行业的金融科技转型天然充满合法性压力: 监管、市场与同侪都在推动"数字化"叙事, 于是任何一家银行都有强烈动机对外宣称自己在拥抱金科, 无论内部是否真正投入。这正是象征性管理理论所刻画的典型场景——组织通过对外话语获取合法性, 而话语可以与实践脱钩。若研究者只统计"银行被报道搞金科的次数"(纯注意力/曝光度), 就无法把"真做"与"只说"分开, 会把象征性造势误当成实质性转型, 从而高估媒体叙事与真实绩效之间的关联。本家族的价值恰在于把这层"叙事含金量"拆出来: 它不问银行有没有被报道搞金科 (那是注意力族 attention 的事), 而问被报道的这些金科故事里, 有多大比例是有真材实料的实质性变革。这使 P3 能够检验一个更精细的命题——是"实质性"的金科叙事, 而非单纯的曝光, 才驱动后续的成本效率改善与财务后果。

从数据加工链看, 一篇报道要进入本家族的分子, 需先后通过三道关: 其一是 stage 13 的银行—金科共现硬过滤 (只保留目标银行与至少一个金科词邻近共现的报道); 其二是 stage 21 的 verified 三角验证 (三家 LLM 确认该篇确实在讲"银行—金科关系"而非泛泛提及); 其三才是 substantiveness 三家投票判"实质性"。三道关层层收紧, 保证分子里的每一篇都既真讲银行金科、又被判为实质性, 大幅压制了误报。分母 n_articles_llm_valid 则是通过前两关 (共现 + verified) 的全部有效报道, 因此占比读作"在确实讲银行金科的报道中, 实质性报道的份额"。

【方法学与计算】
canonical 列 sub_frac 的公式为 sub_frac = n_articles_sub / n_articles_llm_valid: 分子 n_articles_sub 是该 bank-year 中 innovation_substantiveness 共识标签为"实质性"的报道数, 分母 n_articles_llm_valid 是同一 bank-year 通过留篇门控、可用于 LLM 聚合的有效报道总数。分母口径遵循 full-only 留篇门控 (2026-06-29 用户决策): 一篇报道是否算作"一篇银行金科报道"只看全文轨 (full) 的 llm_verified_full 判定, ctx/ss 截断视窗可能漏掉信息, 不参与留篇决定。与之配对但不属本家族的 symb_frac (象征性占比) 由相同分母、以"象征性"篇数为分子构成, 两者与 avg_category_confidence 一道满足分区恒等式 (n_articles_sub + n_articles_symb 在 min-n 守卫下与 n_articles_llm_valid 对齐, encode.py 的 _check_partition_identity 校验)。分母为零 (该 bank-year 无有效报道) 时占比置 NaN 而非 0, 避免把"没有报道"误编码成"零实质性"。

三家 LLM 的聚合不是简单多数, 而是逐篇的 verified 三角验证与分类多数决叠加: 只有先被判定确实在讲"银行—金科关系"的报道才进入分类; substantiveness 三家标签用 majority_vote_categorical 取严格多数, 平票降级"象征性"。Prompt v8 字节级冻结、temperature=0.0 确定性推理, 结果落 _llm_cache.db 缓存账本, 命中即零成本、逐字节可复现 (论文复现的命脉锚点)。这一"多模型投票 + 保守降级 + 缓存确定性"的标注范式, 与近期方法学文献对 LLM 作为标注员的评估一脉相承: Gilardi 等 (2023) 证明大模型在文本标注任务上可超过众包工人, Carlson 与 Burbano (2026) 则为管理学研究使用 LLM 标注给出基础准则与警示 (强调多模型一致性、温度控制与可复现)。Gentzkow 等 (2019) 的"文本即数据"框架为把非结构化报道转成结构化计量变量提供了总纲。

平票降级为"象征性"的选择本身是一个可审计的保守设计决策, 而非随意默认。其逻辑是: 当三家模型对一篇报道究竟实质还是象征意见分裂时, 最谨慎的做法是不把它计入"实质性"分子, 从而避免对银行金科转型的实质含量给出过于乐观的估计。这一 uniform-prior MAP 的保守降级与情感轨的 tie_default 处理同源 (情感平票在金科轨降级"中性"以防中性污染), 都体现项目"宁可低估、不可虚高"的一致口径。与之配套的是: 逐模型的原始标签并未被丢弃, 而是以 per-model 存档列 ({short}_ 前缀) 保留下来, 供跨模型一致性 (Krippendorff α / Cohen κ) 审计与 per-model 稳健性臂使用——substantiveness 维经 LLM_CLASS_SPEC 三元映射 (subst → sub_frac, 目标类"实质性", 解析键 innovation_substantiveness) 与面板列互锁, 这是文章级基名与面板 metric 基名之间唯一的字符串不可达互锁点 (subst 无法由字符串变换到 sub_frac), 由该映射单点维护。三家 per-model 子测度各自 just-identified 并排, 互为稳健性、不分主次, 同样禁混进同一 over-identified Hansen J。

在面板聚合层, encode.py 对 substantiveness 的三轨采取分层实现: full 轨直接以 n_articles_sub / n_articles_llm_valid 产 sub_frac 与对偶 symb_frac; ctx 轨与 ss 轨则走"对角线追加"逻辑 (_aggregate_ctx_diagonal), 分别对 innovation_substantiveness_ctx / innovation_substantiveness_ss 逐轨聚合出各自的分子, 并严格配对同轨分母 (n_articles_llm_valid_ctx / n_articles_llm_valid_ss)。这一"分子分母同轨配对"是 metric-audit 定稿的核心修正: 早期曾用 full 轨分母去除 ctx/ss 分子, 导致轨道不对称、占比越界至大于 1, 现已统一为逐轨自洽。计数列在填充时先 fillna(0) 再转 int, 占比计算对分母为零的 bank-year 严格置 NaN。这一实现细节保证了三轨占比在语义上可比又在口径上各自自洽: 三轨用同一套投票逻辑与同一套保守降级规则, 差异只在取材视窗与对应的分子分母轨, 从而使三轨真正构成一组"同法异窗"的稳健性梯子, 而非口径混杂的异质度量。

【文献定位】
本家族把组织理论的"实质—象征"话语搬到银行金科的媒体计量语境, 与金融学近年蓬勃的"言行脱耦/漂绿"实证直接对话。Kim 与 Lyon (2015) 在披露维度刻画了夸大与过度谦虚两类脱耦; Bingler 等 (2022, 2024) 用 ClimateBert 识别气候披露中的"廉价空谈"(cheap talk) 与择优披露, 并把文本信号关联到真实的减排行动与声誉风险; Duchin 等 (2025) 在资产市场层面区分了真实的可持续行为与漂绿; Giannetti 等 (2026) 直击"光鲜绿色银行"——环境披露与实际放贷活动的脱节; Song 等 (2026) 命名了"AI 洗白"(AI washing) 现象——用战略性披露包装 AI 能力并招致市场反噬。本家族正是把这一族"叙事—实质是否脱耦"的测度精神, 落到"银行金科报道中实质性份额"这一具体占比上, 使 P3 得以检验媒体叙事的实质含量是否驱动后续的成本效率与财务结果。

这一文献谱系的组织理论根脉可追溯到 Westphal 与 Zajac 的系列工作。Westphal 与 Zajac (1994) 首次在 CEO 长期激励计划中区分了"实质"与"象征": 一项治理安排可以真正改变高管的激励结构 (实质), 也可以只是向股东发出信号而不改动实际支付 (象征)。Westphal 与 Zajac (1998) 进一步展示了公司治理改革中面向股东的象征性管理如何引发市场反应, 揭示了"对外话语"与"内部实践"可以系统脱钩且这种脱钩本身被市场感知。Fiss 与 Zajac (2006) 把这一逻辑扩展到战略变革的"意义给予"(sensegiving), 阐明框架化 (framing) 与脱耦 (decoupling) 如何共同服务于象征性目的。Westphal (2023) 最新的反思则警示了系统性象征管理在 CSR 与公司宗旨语境下的风险。本项目继承这一谱系, 但把研究对象从治理/CSR 转到银行的金融科技转型, 并把测量从档案编码升级为多模型 LLM 标注——这既延续了构念的理论内核, 又借助 Gentzkow 等 (2019) 的"文本即数据"范式和 Gilardi 等 (2023)、Carlson 与 Burbano (2026) 对 LLM 标注的方法学背书, 使"实质—象征"这一原本需要大量人工编码的构念可以在千万级报道语料上规模化、可复现地度量。正是这一测量升级, 让本家族既扎根经典理论、又具备大样本计量的操作性。近期 Zhou, Liu 与 Huang (2026, Technology in Society) 用中国A股上市公司披露文本区分数字化转型披露中的实质性投入与象征性(洗牌式)宣称, 为本家族区分实质性创新报道与形式性/空洞报道占比(sub_frac)的构念提供了同构的经验参照。基于中国制造业上市公司文本挖掘证据, 区分数字化转型过程驱动的象征性与实质性环境披露两类反应, 为 sub_frac 的实质—象征二分构念提供同期经验参照, 引用格式为 Ji, Sheng 与 Wan (2024, Systems)。考察企业家导向与政治关联如何驱动企业在数字化转型上选择实质性投入还是象征性披露, 呼应本家族用实质性报道占比刻画银行金科转型言行是否脱耦的构念, 引用格式为 Liu, Li 与 Zhu (2026, Asia Pacific Journal of Management)。

【识别策略定位】
sub_frac 作为 P3 主处理变量, 其识别挑战在于"实质性报道份额"可能与银行的可观测特征、地区金融环境乃至媒体覆盖强度内生共变。项目为此配套了 IV 扩展 (iv_extensions.py): 对 sub_frac 计算同组留一 (leave-one-out) 同侪均值工具 (leave_one_out_peer_subst_iv), 借同类银行的实质性报道份额作为外生变动来源, 呼应同侪效应识别的经典框架; ctx/ss 轨内生变量 (sub_frac_sc / sub_frac_ss) 各自配套对应轨的 LOO 工具, 严格轨内配对。需要强调的是: full/ctx/ss 三轨以及各自的 just-identified IV 设定是并排的稳健性臂, 互为稳健性、不分主次, 严禁把不同轨或不同工具混进同一个 over-identified 的 Hansen J 过度识别检验 (这是本项目贯穿三轨、co-primary 双轨嵌入、per-model、各类梯子的统一铁律)。分类维度的跨厂商稳健则由 per-model 存档列 (subst 维经 LLM_CLASS_SPEC 映射到 sub_frac) 承担, 三家 per-model 子测度同样各自 just-identified 并排。

从内生性的具体来源看, sub_frac 面临三类挑战。其一是反向因果: 财务表现更好的银行可能更有能力做实质性金科投入, 也可能更受媒体青睐而获得更"实质"的报道, 使实质性份额与结果变量互为因果。其二是遗漏变量: 银行所在地区的金融科技生态、监管试点、数字基础设施等既影响实质性金科落地、又影响财务结果, 若不控制会混淆估计。其三是测量端的媒体覆盖异质性: 报道多的银行其占比更稳定、报道少的银行占比噪声更大, 这是一种由样本量驱动的非经典测量误差。项目的 IV 扩展针对第一、二类挑战: 留一同侪均值工具借"同类银行的实质性报道份额"作为外生变动源, 其识别假设是同侪的实质性叙事通过行业共同冲击影响本银行的实质性份额, 却不直接影响本银行的结果变量 (排除性)。这一同侪工具的理论依据可追溯到 Manski (1993) 对内生社会效应的"反射问题"辨识与 Leary 与 Roberts (2014) 对同侪如何影响公司财务政策的实证识别: 借同组留一均值剥离本银行自身对同侪均值的机械贡献, 是缓解反射问题的标准做法。跨模型与三轨稳健性则针对测量端: 若主结论在三家模型、三条取材轨下都成立, 就大幅削弱了"结果被某一模型判读癖好或某一视窗截断驱动"的担忧。所有这些稳健性臂都是并排的 just-identified 设定, 严禁拼进同一过度识别检验。需再次强调: full/ctx/ss 三轨、三家 per-model 子测度、以及各自配套的轨内 LOO 工具, 全部互为稳健性、不分主次, 各自 just-identified 并排, 严禁把任意两条混进同一个 over-identified 的 Hansen J 过度识别统计量——这与项目在 co-primary 双轨嵌入、政治词权重梯度、词典消融梯度、判据敏感性上贯彻的铁律完全一致, 是保证稳健性论证不被"人为拼工具制造过度识别自由度"污染的根本约束。真正的跨模型族错误率控制 (FWER) 由根级 rwolf 模板 (27_tableA12 Panel C 的 CLS 族) 统一承担, 而非在单个回归里堆叠工具。

【与相邻测度的构念区分】
sub_frac 须与同为 stage 21 三维创新分类的另外两族严格区分: locus 族 (tech_frac/app_frac, 底层技术 vs 应用场景, 母锚 Gomber 等 2018) 问的是"创新落在技术栈的哪一层"; collab_mode 族 (indep_frac/collab_frac, 自主研发 vs 外部协同, 母锚 Chesbrough 开放式创新) 问的是"创新靠自研还是合作"。substantiveness 族问的则是"这项创新是真做了还是只是说说", 三者维度正交, 分别对应 P4/P5/P3。此外 sub_frac 也不同于情感语调族 (tone): 一篇实质性报道未必语调正面, 项目另设 tone_gap_sub_symb (实质—象征语调差距) 作为脱耦的补充测度, 但那是纯日志/衍生量, 不属本家族。本家族只承载"实质性份额"这一占比构念本身。再从测量方法的谱系看, 本族与用词典或监督式分类器识别"廉价空谈"的路线 (如 Bingler 等 2022, 2024 的 ClimateBert 择优披露识别) 属同一构念家族但不同实现: 前者在披露文本内部用固定词表或微调模型打分, 本族则用三家通用大模型对整篇媒体报道做零样本语义判定并投票取共识。二者互为方法学佐证而非替代——本族的优势在于不依赖预先冻结的领域词表、可迁移到金融科技这一新兴且措辞快速演化的语域; 代价是判读边界更依赖 prompt 设计与模型先验, 故须以三家投票、保守平票降级与 per-model 存档三重防线控制单模型癖好。

还需与两个易混的注意力/规模量划清界限。其一是 attention 族 (P2, 如 fintech_share/attention_pct): 那度量的是"银行被报道搞金科的曝光强度或份额", 分子是金科报道数、不区分实质与象征; 而 sub_frac 是在"确实讲金科"的报道内部再切一刀, 问其中实质性的比例。二者可以同高同低、也可以背离——一家银行可能曝光度极高 (attention 大) 却满是象征性造势 (sub_frac 低), 这种"高曝光低实质"的组合恰是漂绿/AI 洗白文献最关心的脱耦形态。其二是报道基数 n_articles_llm_valid: 它是本家族的分母而非度量本身, 使用时须与占比联读, 避免把小样本高占比误读为强实质性。此外, sub_frac 与情感语调 (tone) 正交: 实质性说的是"做没做", 语调说的是"评价好不好", 一篇实质性报道可以语调中性甚至负面 (如客观报道一次失败的技术投入)。项目为捕捉二者交互另设 tone_gap_sub_symb (实质—象征报道的语调差距) 作为脱耦的补充信号, 但该衍生量不属本家族。厘清这些边界, 才能保证 sub_frac 在 P3 中承载的正是"叙事实质含量"这一唯一构念。

【已知局限与稳健性梯子】
第一, 实质—象征的判定终究是语义标注, 存在模型主观性与语料偏差; 项目以三家跨厂商模型投票 + 保守平票降级压制单模型偏误, 并保留 per-model 存档列供跨模型 kappa 一致性审计。第二, 占比对小样本敏感: bank-year 报道数少时占比方差大, 分母为零置 NaN、机制型差距量另设 min-n≥5 守卫。第三, 媒体报道本身是"被外界看到的"实质性, 与银行内部真实投入之间仍有测量误差, 这与 Westphal 系列强调的"象征性管理面向外部受众"恰好同源——媒体正是外部受众的镜像, 故该代理在构念上是自洽的, 但解释因果时需配合 IV 与财务侧结果变量。第四, 三轨 (full/ctx/ss) 视窗宽窄不同带来的差异被刻意保留为稳健性梯子而非取平均: 三轨各自 just-identified 并排、禁混同一 Hansen J。生产语料 (T=18) 下三轨占比均有意义; 开发样本 (T=2) 上 ctx/ss 轨可能因视窗截断而退化, 属预期而非缺陷。第五, LLM 标注虽经三家投票加固, 仍可能对特定表达习惯 (如中文财经稿的套话、模板化措辞) 存在系统性判读偏好; 项目对此的防线是保留 per-model 存档列供事后审计、并把三轨与三家模型都设为可替换的稳健性臂, 使主结论不被任何单一模型或单一取材视窗驱动。第六, 需明确本占比是"相对份额"而非"绝对数量": 一家报道极少的银行即便只有一两篇实质性报道也可能得到高占比, 故在解释时须与 n_articles_llm_valid (报道基数) 联读, 机制型衍生量 (如 tone_gap_sub_symb 实质—象征语调差距) 另设 min-n≥5 守卫正是为此。综上, 本家族在构念保真、测量可复现与识别稳健三个层面都配置了对应的防护与稳健性梯子, 是 P3 因果叙事的可审计基石。

## VAR: sub_frac

【变体差分】
本列是家族 canonical, tier=core, 即 P3 (bank_fintech_substance) 正文回归的主处理变量。轨道 = full (全文轨): 上游 stage 21 对 content_full (标题 prepend + 全文正文) 做 innovation_substantiveness 三家投票分类, 面板层以 sub_frac = n_articles_sub / n_articles_llm_valid 聚合。分子 n_articles_sub 是全文轨判"实质性"的报道数, 分母 n_articles_llm_valid 是该 bank-year 通过 full-only 留篇门控的有效报道总数——这正是留篇门控本身所依据的全文轨口径, 故 canonical 列的分子分母同处 full 轨、口径完全自洽, 无跨轨错配。相对本家族另两列, 本列的区别纯在轨道: 它用的是最宽的取材视窗 (整篇报道), 因而信息最全、也最可能把边缘提及也纳入判断, 是三轨中信息量最大、被论文选作 headline 的一轨。

作为主处理变量, 本列在 P3 的基准回归中进入 RHS, 并配套留一同侪均值工具 (leave_one_out_peer_subst_iv) 处理内生性; 象征性对偶列 symb_frac 与之共享分母、由"象征性"篇数构成, 两者在 min-n 守卫下满足分区恒等式。本列与 ctx 轨 sub_frac_sc、ss 轨 sub_frac_ss 构成三轨稳健性梯子: 三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁把三轨的实质性占比混进同一个 over-identified Hansen J 过度识别检验 (三轨铁律)。本列的确定性来自 Prompt v8 字节冻结 + temperature=0.0 + _llm_cache.db 缓存命中, 逐字节可复现。构念上, 本列直接承载 Westphal 与 Zajac (1994, 1998) 的"实质—象征"母命题, 并与 Bingler 等 (2022, 2024)、Duchin 等 (2025)、Giannetti 等 (2026)、Song 等 (2026) 的"言行脱耦/漂绿/AI 洗白"实证形成对话: 当一家银行的金科叙事里实质性份额越高, 越可能对应真实的转型投入而非象征性造势。使用者须记住本列是 full 轨口径, 论文正文引用即以本列为准, ctx/ss 两列仅作稳健性佐证, 不可与本列合并进单一过度识别设定。

在实操层面, 本列的取值区间为 [0,1], 分母为零 (该 bank-year 无通过留篇门控的有效报道) 时为 NaN。读数上, sub_frac=0 表示该 bank-year 的金科报道全部被判象征性 (只见叙事造势、不见实质变革), sub_frac=1 表示全部被判实质性 (报道所述皆有真材实料), 中间值给出实质叙事的相对浓度。因本列是 full 轨 (最宽视窗), 相对 ctx/ss 两列, 它把整篇报道中任何提及银行金科实质动作的信号都纳入判断, 因而在同一 bank-year 上通常给出信息量最全的实质性份额估计; 但也正因视窗最宽, 它对"报道主体并非该银行、只是顺带提及"的边缘情形相对更宽容, 这正是设置 ctx/ss 两条更聚焦轨作为稳健性对偶的动机所在。本列与对偶列 symb_frac 并非机械互补 (二者之和未必恒为 1): 因为分母是全部有效报道, 而分子只数被判"实质性"或"象征性"的报道, 在分区恒等式的 min-n 守卫与个别未定情形下二者之和可略偏离 1, 使用时应把 sub_frac 视为独立的实质性份额度量, 而非简单地由 1 减 symb_frac 推得。最后, 本列进入 P3 回归时通常配合银行与年份固定效应及基准控制, 并以留一同侪工具 (leave_one_out_peer_subst_iv) 做 2SLS 稳健性; 其滞后项与差分项按面板惯例 (L./D.) 在 Stata 侧构造, 本列本身是当期水平值。在推断层面, 本列进入 P3 时须搭配稳健性电池: 跨模型族错误率由根级 rwolf 模板 (Romano 与 Wolf 2005 的逐步多重检验) 统一控制, wild bootstrap 推断遵循 Roodman 等 (2019) 的实现, 生产语料本机按 license 自动拉满处理器; 这些电池只在 headline 的 full 轨上运行, ctx/ss 两列作为独立稳健性臂各自并排复现, 而非拼入同一过度识别设定。总之, 本列是家族内唯一被论文选作正文 headline 的实质性占比度量, 其 full 轨口径、留篇门控自洽的分子分母、以及配套的同侪工具 (full 轨全名 leave_one_out_peer_subst_iv) 与三轨稳健性梯子共同构成 P3 主处理变量的完整规格, 使用者引用时应始终以本列而非其 ctx/ss 对偶作为主结果的锚。

## VAR: sub_frac_sc

【变体差分】
本列 tier=standard, 是 canonical sub_frac 的 ctx 轨 (context-conditional 上下文轨) 稳健性对偶。后缀 "_sc" 是本项目对 substantiveness 维度 ctx 对角轨的历史沿用编码 (subst 维 + ctx = sc), 与 locus 维的 "_lc"、collab 维的 "_cm" 同构, 并非新语义, 只是轨道字母标识。轨道差异: 本列的分类基于 content_ctx (标题 prepend + 银行实体邻近窗口文本, 而非整篇正文), 因而只在"与目标银行上下文相关"的片段上判断实质—象征, 视窗比 full 窄。计算上 sub_frac_sc = n_articles_sub_sc_ctx / n_articles_llm_valid_ctx: 分子是 ctx 轨对角聚合的"实质性"篇数 (_sub_sc_ctx), 分母是 ctx 轨独立的有效报道数 n_articles_llm_valid_ctx——ctx 分子严格配 ctx 分母, 修正了早期"轨道不对称除法致 frac>1"的口径缺陷 (metric-audit 定稿)。分母列缺失时本列置 NaN 并告警, 优雅降级。

本列相对 canonical 的唯一实质区别就是取材视窗更聚焦 (只看银行相关上下文), 因而对"提及银行但金科内容边缘"的报道更严格。它是 P3 的稳健性轨: 与 full 轨 sub_frac、ss 轨 sub_frac_ss 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J (三轨铁律)。IV 侧本列配套 lpeer_subst_iv_ctx 轨内工具, 不与 full 轨工具跨轨混用。构念内核不变——仍是 Westphal 与 Zajac (1998) 的实质—象征二分与 Fiss 与 Zajac (2006) 的脱耦逻辑, 只是把判断锚定到与银行实体邻近的上下文, 呼应实体邻近 (entity-proximity) 的文本计量思想: 越贴近银行本体的叙事, 越能剔除泛化背景噪声, 给出更"就事论事"的实质性判断。

## VAR: sub_frac_ss

【变体差分】
本列 tier=standard, 是 canonical sub_frac 的 ss 轨 (银行与金科同句共现窗口) 稳健性对偶, 也是本家族三轨梯子中视窗最窄的一轨。轨道差异: 本列的分类基于 content_ss (标题 prepend + 银行与金融科技词在同一句 / ±N 句窗内共现的片段), 只在"银行和金科被同句捆绑提及"的最贴身语境上判断实质—象征。ss 轨的回退语义镜像 ctx: 当某篇无银行∧金科同句共现时, content_ss 优雅回退到全文 body 并置 ss_is_fallback=True (与 ctx 回退同款优雅降级), 保证不因视窗为空而丢篇。计算上 sub_frac_ss = n_articles_sub_ss_ss / n_articles_llm_valid_ss: 分子是 ss 轨对角聚合的"实质性"篇数 (_sub_ss_ss), 分母是 ss 轨独立的有效报道数 n_articles_llm_valid_ss——各轨 LLM 成功率不同, ss 严格用自己的分母, 与 ctx 用 n_articles_llm_valid_ctx 同口径; 分母缺失置 NaN 并告警。

本列相对 canonical 的区别是最严格的取材口径 (同句共现), 因而给出"银行与金科最直接绑定"语境下的实质性份额, 对纯背景式、拼盘式提及最不敏感。它是 P3 稳健性梯子的第三臂: 与 full 轨 sub_frac、ctx 轨 sub_frac_sc 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J (三轨铁律)。IV 侧配套 lpeer_subst_iv_ss 轨内工具, 且 sub_frac_ss 缺列时相关 IV 优雅置 NaN。需特别提示: 由于 ss 视窗最窄, 在开发样本 (T=2) 上本列常因共现片段稀少而方差退化甚至近零, 属预期的小样本退化而非缺陷; 生产语料 (T=18) 下本列恢复应有区分度。构念上本列仍承载 Westphal 与 Zajac (1998) 的实质—象征母命题, 并借共现窗口把叙事与银行本体最紧密地对齐, 是三轨中"最就事论事"的实质性度量。

<!-- rendered-citations:begin -->
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy green" banks: The disconnect between environmental disclosures and lending activities. Management Science. https://doi.org/10.1287/mnsc.2024.07420
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal. https://doi.org/10.1002/smj.70023
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Westphal, J. D. (2023). Systemic symbolic management, corporate social responsibility, and corporate purpose: A cautionary tale. Strategy Science, 8(2), 221-232. https://doi.org/10.1287/stsc.2023.0188
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature. https://doi.org/10.1257/jel.20181020
Roodman, D., Nielsen, M. Ø., MacKinnon, J. G., & Webb, M. D. (2019). Fast and wild: Bootstrap inference in Stata using boottest. The Stata Journal. https://doi.org/10.1177/1536867X19830877
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy?. The Journal of Finance. https://doi.org/10.1111/jofi.12094
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies. https://doi.org/10.2307/2298123
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. brownwash: Exaggeration and undue modesty in corporate sustainability disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Zhou, H., Liu, Z., & Huang, C. (2026). Fake it till you make it: Digital washing and corporate innovation. Technology in Society. https://doi.org/10.1016/j.techsoc.2025.103145
Ji, H., Sheng, S., & Wan, J. (2024). Symbolic or Substantive? The Effects of the Digital Transformation Process on Environmental Disclosure. Systems. https://doi.org/10.3390/systems12060197
Liu, L., Li, Z., & Zhu, Q. (2026). Substantive investment or symbolic disclosure toward digital transformation? The impact of entrepreneurial orientation and political connections. Asia Pacific Journal of Management. https://doi.org/10.1007/s10490-025-10098-2
<!-- rendered-citations:end -->
