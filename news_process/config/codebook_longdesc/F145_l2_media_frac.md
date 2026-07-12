---
family_id: F145
columns:
- ceased_media_frac
- comp_media_frac
- daily_media_frac
- deepdive_media_frac
- fin_media_frac
- homecity_media_frac
- homeprov_media_frac
- market_media_frac
- official_media_frac
unit: 占比 (proportion, 无量纲, 取值域 [0,1])
formula: "<sfx>_media_frac = mean_over_articles( 1[媒体 ∈ 该类别集合] ) within (target_bank, year); 分子分母均以银行×fintech 文章行 (article×bank, 非 docid 去重) 计"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity ; news_process/pipeline/panel/export.py (标签注入)
upstream:
- 13_cooccurrence_filter.parquet (银行-fintech 共现子集)
- 21_tone_llms.parquet (留篇门控 llm_verified_full)
- config 媒体分类名单 (financial_media / comprehensive_media / official_media / market_media / deep_dive_periodicals / high_frequency_dailies / NPPA 交叉验证)
citations:
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
  venue: Journal of Accounting and Economics
  vol: 73
  issue: 2-3
  pages_or_artno: 101455
- doi: 10.1016/j.jfineco.2019.06.003
  type: journal
  authors: Gao, P., Lee, C., & Murphy, D.
  year: 2020
  title: "Financing dies in darkness? The impact of newspaper closures on public finance"
  venue: Journal of Financial Economics
  vol: 135
  issue: 2
  pages_or_artno: 445-467
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: "The media and the diffusion of information in financial markets: Evidence from newspaper strikes"
  venue: The Journal of Finance
  vol: 69
  issue: 5
  pages_or_artno: 2007-2043
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: 67
  issue: 2
  pages_or_artno: 561-598
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是每家银行在给定年度所收到的银行-fintech 报道, 按其发布媒体的属性划分后, 各属性类别所占的报道篇数份额。九个列全部是同一构造范式下沿不同分类维度的占比 (share) 变量: 给定一个媒体类别集合 (如财经类、综合类、纯官方、纯市场化、高频日报、深度期刊、同省、同城, 以及疑似退出覆盖的停刊代理集合), 对落入该 (target_bank, year) 单元的每一篇文章打一个 0/1 指示 (发布媒体是否属于该集合), 再在单元内对全部文章取均值, 即得该类别在该银行-年报道结构中的相对权重。构念动机来自媒体金融学的一条核心洞见: 报道的信息含量、倾向性与治理效力并非同质, 而系统性地依赖于报道来源的组织属性——财经专业媒体与综合门户在原创分析深度上不同, 党政主管的官方媒体与企业主办的市场化媒体在政治激励与批判性上不同, 日报与低频深度期刊在时效与分析性上不同, 本地媒体与异地媒体在广告依赖驱动的地方偏袒上不同。把这些结构维度显式量化, 使得后续可以检验"银行-fintech 叙事的乐观度是否被特定媒体结构放大或压制", 并为媒体来源构成本身作为控制变量或工具变量暴露提供面板列。

【方法学与计算】
所有分子分母均在 stage 13 共现硬过滤后的银行-fintech 文章子集上计算, 行的口径是 article×bank (一篇涉及多家银行的文章在各银行下分别计入一行, 非 docid 去重), 与家族 n_articles 口径一致; 留篇是否算作"一篇银行-fintech 报道"遵循 2026-06-29 起的 full-only 门控 (只看 llm_verified_full == True), ctx/ss 派生量为 conditional-on-full 的子集轨。分类名单来自项目媒体分类配置, 其中官方/市场化两维源自 NPPA (国家新闻出版) 数据库并按主管/主办单位双判据构造: 官方以主管单位为党政机关为判据, 市场化以主办单位为企业/商业集团为判据。这两条判据在实证上并不互斥 (实测重叠 386 家, 约 82% 市场化媒体同时被官方名单覆盖), 因此代码采取结构性互斥的净化构造——official 取 OFFICIAL 减 MARKET (纯官方), market 取 MARKET 减 OFFICIAL (纯市场化), 双判据媒体不计入任一处理组而落入各自对照, 保证 official_media_frac 与 market_media_frac 之和不超过 1。深度期刊与高频日报按 NPPA 出版周期判据划分 (日刊 vs 周报及以下的低频出版物), 二者互斥且和不超过 1。地理邻近性以银行注册地的省/市与媒体来源省/市匹配得到, 来源地不可知的报道被置为 NaN 而非强制归入异地, 并保证同省包含同城 (homeprov ≥ homecity 的单调约束在文末校验)。停刊代理集合由数据驱动的隐性覆盖退出检测得到 (媒体在样本中的 last_year 早于样本末年减去缺口阈值即标疑似退出), 经 NPPA 交叉验证仅改报告标签、不收窄排除集。各占比一律 groupby(target_bank, year).mean() 直接得到, 缺失单元按左连接保留 NaN、按契约不做零填充。

【文献定位】
本家族的构念根基是媒体金融学关于"来源属性调节信息含量"的实证传统。Gentzkow 与 Shapiro (2010) 证明媒体倾向 (slant) 具有由需求侧驱动的稳定组织特征, 为按来源属性分层、并把媒体结构视为可暴露的固定风格提供了方法论依据; Gurun 与 Butler (2012) 直接刻画本地媒体因本地广告收入而对本地企业系统性正面倾斜, 是同省/同城两列的母锚。财经专业媒体与信息中介功能的作用, 呼应 Call 等 (2022) 对财经记者作为信息中介的调查证据, 以及 Peress (2014) 借报纸罢工这一自然实验识别媒体对金融市场信息扩散的因果作用。停刊/覆盖退出维度直接承接报纸关停的因果文献: Heese 等 (2022) 记录本地报纸关停后地方公司违规上升, Gao 等 (2020) 记录关停抬高地方公共财政成本, 二者共同论证"覆盖退出"作为监督真空代理的合理性, 也正是把疑似退出媒体保守剔除以做样本选择稳健性的因果依据。就中国银行业情境, Fang 等 (2024) 提供了银行级媒体情感影响存款稳定与系统性风险的同域证据, Gutknecht (2025) 则示范了媒体报道构成与企业风险的近期关联。需强调, 本家族九维属规格稳健性并排关系: 各维度分类彼此正交或互斥、各自 just-identified 并排, 互为稳健性、不分主次, 禁止把不同维度的份额混进同一 over-identified 的 Hansen J 检验; 三轨 (full/ctx/ss) 的情感均值副产品同理各自并排、禁混同一过度识别检验。

## VAR: ceased_media_frac

【变体差分】
本列是本家族中唯一的样本选择稳健性维度, 与其余八列的"媒体属性构成"性质不同。其分类集合不是媒体的静态组织属性, 而是数据驱动的隐性覆盖退出 (de-facto coverage cessation) 检测结果: 对每家媒体在银行-fintech 子集上算 first_year/last_year/n_articles, 若某媒体的 last_year 早于样本末年减去缺口阈值 (threshold_gap, 默认 2 年), 即标为疑似退出覆盖并纳入停刊代理集合。构念上须诚实披露三点: 一是该度量刻画的是"媒体退出银行-fintech 话题覆盖" (topic exit) 而非经证实的报纸停刊, 媒体可能仍在正常出版只是不再覆盖该话题; 二是排除集为 confirmed ∪ suspected, NPPA 交叉验证只改报告标签、未经证实的 suspected 也全量进入排除集; 三是分母仍按 article×bank 行计数、非 docid 去重。因此本列应解读为"疑似退出覆盖媒体"的保守剔除稳健性口径, 在论文中不可表述为严格出版停刊 (publication cessation) 口径。其学术依据是报纸关停引致地方监督真空的因果文献 (Heese 等 2022; Gao 等 2020): 报纸一旦退出本地覆盖, 公司违规与公共财政成本上升, 故把疑似退出媒体识别出来并保守剔出主样本, 是控制因媒体来源消失而引入的样本选择偏误的手段。与其余占比列关系为规格稳健性并排、各自 just-identified, 不得混入同一过度识别检验。

## VAR: comp_media_frac

【变体差分】
本列是内容属性维度 (维度①②③: 财经/综合/其他三方分类) 中的综合类份额。分类判据为媒体名称落入 comprehensive_media 名单; 三方分类由 _classify_content 实现——先判是否属财经类, 否则判是否属综合类, 再余下归其他类, 因此财经优先、财经与综合在构造上互斥 (若名单出现重叠, 重叠媒体归为财经并记 warning)。分子是该 (target_bank, year) 内被判为综合类的文章行数, 分母是该单元全部文章行数, 取均值即综合媒体份额。构念上综合类指综合性门户/都市类等非财经专业媒体, 与财经专业媒体在原创金融分析深度上形成对照: 综合媒体覆盖面广但对 fintech 议题的专业加工通常弱于财经媒体, 因而其份额高低反映银行-fintech 叙事在多大程度上由非专业信息源承载。本列与 fin_media_frac 构成同一三方分类的两条互补份额 (其余落入 other), 二者之和不超过 1 (文末 (6) 校验), 与 official/market、deepdive/daily、homeprov/homecity 等其他维度正交, 属规格稳健性并排、各自 just-identified, 禁混同一 over-identified Hansen J。该列不涉及情感轨道, 是纯来源构成比率; 家族内相关的情感均值 (tone_comp_media_full/ctx/ss) 与缺口 (tone_gap_comp_other) 是另立的三轨副产品, 不属本列。就解读而言, 综合类份额上升往往对应叙事扩散度提高、专业深度稀释, 可与财经份额联合刻画信息源的专业化程度; 该份额对缺失单元按左连接保留 NaN, 不做零填充, 生产 T=18 全量语料下方能反映真实的媒体结构分布, 本机 T=2 试跑口径下部分单元退化属预期。

## VAR: daily_media_frac

【变体差分】
本列是出版频率维度 (维度⑧) 中的高频日报份额, 分类判据为媒体落入 high_frequency_dailies 名单, 该名单基于 NPPA 出版周期为日报的出版物界定。分子为单元内被判为日报的文章行数, 分母为单元全部文章行数, 取均值。构念动机来自日频媒体情感研究传统: 日报出版频率高、时效性强, 是日频情感指标的主要驱动来源, 高日报份额意味着银行-fintech 叙事更多由高频、即时性报道构成, 相较低频深度期刊更贴近事件时点、信息刷新更快但单篇分析深度通常更浅。本列与 deepdive_media_frac 构成出版频率维度的一对互斥份额 (二者判据基于同一 NPPA 出版周期字段的不同取值), 文末 (7) 校验二者之和不超过 1、并检验其与其他维度正交。该维度与内容属性 (财经/综合)、政治取向 (官方/市场化)、地理邻近 (同省/同城) 均正交, 属规格稳健性并排关系、各自 just-identified, 不得混进同一 over-identified 的 Hansen J 检验。本列为纯来源构成比率、不涉三轨情感; 对应的日报/非日报情感均值与缺口 (tone_daily_media、tone_gap_daily_nondaily) 是另立三轨副产品, 不属本列语义。解读上, 高日报份额意味着单元内报道更贴近事件时点、信息刷新更频繁, 可用于检验银行-fintech 叙事乐观度是否被高频即时报道放大; 该份额缺失单元按左连接保留 NaN、不做零填充, 生产 T=18 全量语料下方能稳定估计, 本机 T=2 试跑下部分单元零方差退化属预期现象。

## VAR: deepdive_media_frac

【变体差分】
本列是出版频率维度 (维度⑦) 中的深度期刊份额, 与 daily_media_frac 互为对照。分类判据为媒体落入 deep_dive_periodicals 名单, 该名单基于 NPPA 出版周期为周报及以下 (即非日刊) 的低频出版物界定。分子为单元内被判为深度期刊的文章行数, 分母为单元全部文章行数, 取均值。构念动机是: 低频出版的深度期刊具有更强的信息分析与原创内容创造能力, 相较日报的即时转载/简讯更倾向原创深度报道, 而原创信息创造被认为比简单转载传播更具治理效力。因此高深度期刊份额意味着银行-fintech 叙事更多由分析型、原创性内容承载, 是信息质量维度上与日频规模相对立的一极。本列与 daily_media_frac 基于同一 NPPA 出版周期字段的互斥取值构造, 二者之和不超过 1 (文末 (7) 校验), 且与内容属性、政治取向、地理邻近三维度正交。九维之间为规格稳健性并排、各自 just-identified, 禁混同一 over-identified Hansen J。本列为纯来源构成比率; 对应的深度/非深度情感均值 (tone_deepdive_media) 与缺口 (tone_gap_deepdive_nondeep) 是另立的三轨副产品, 不属本列。解读上, 高深度期刊份额可视为信息质量维度的一个正向指标, 用于检验原创分析型报道占比是否与银行-fintech 叙事的治理效力关联; 该份额缺失单元按左连接保留 NaN、不做零填充, 生产 T=18 全量语料下方能稳定估计, 本机 T=2 试跑口径下部分单元退化属预期。

## VAR: fin_media_frac

【变体差分】
本列是内容属性维度中的财经类份额, 是三方分类 (财经/综合/其他) 中优先判定的一支。分类判据为媒体落入 financial_media 名单; _classify_content 首先判财经、命中即归财经, 故财经在构造上优先于综合、二者互斥。分子为单元内被判为财经类的文章行数, 分母为单元全部文章行数, 取均值即财经媒体份额。构念上财经专业媒体指以财经/金融报道为主业的专业媒体, 其对 fintech 议题的专业加工、术语准确性与分析深度通常高于综合门户, 因而高财经份额反映银行-fintech 叙事更多由专业信息源承载, 关联到财经记者作为信息中介的信息生产功能。本列与 comp_media_frac 是同一三方分类的两条互补份额 (余下落入 other), 二者之和不超过 1 (文末 (6) 校验), 且与政治取向、出版频率、地理邻近三维度正交。九维之间为规格稳健性并排、各自 just-identified, 禁混进同一 over-identified 的 Hansen J 检验; 三轨情感均值 (tone_fin_media_full/ctx/ss) 同理各自并排。本列为纯来源构成比率, 不涉三轨情感; 对应的财经情感均值与三条缺口 (tone_gap_fin_other、tone_gap_fin_comp) 是另立副产品, 不属本列。解读上, 高财经份额意味着叙事更多经过专业金融信息源的加工, 可与综合份额联合度量信息源专业化程度并作为报道质量的暴露变量; 该份额缺失单元按左连接保留 NaN、不做零填充, 生产 T=18 全量语料下方能稳定估计, 本机 T=2 试跑口径下部分单元退化属预期。

## VAR: homecity_media_frac

【变体差分】
本列是地理邻近性维度 (维度⑨) 中市级层面的本地媒体份额, 判据为报道来源媒体所在城市与目标银行注册地城市一致 (_is_homecity)。分子为单元内同城报道行数, 分母为该单元报道行数, 取均值。构念动机来自本地媒体偏袒文献: 本地媒体因本地广告收入依赖、地方政府关系等因素, 倾向对本地企业进行系统性正面倾斜 (media slant), 故同城报道份额高意味着银行-fintech 叙事更可能受本地正面倾斜影响, 是识别报道乐观度中"地方偏袒"成分的暴露变量。构造上须注意来源地缺失处理: 城市来源不可知的报道被置为 NaN 而非强制归入异地, 避免旧编码把"来源不可知"错误当作非本地而低估本地份额。同城是同省的子集, 代码强制 homeprov 在同城为 1 时也置 1, 并在文末校验 homeprov_media_frac ≥ homecity_media_frac (容差 1e-10) 的单调约束。本列与 homeprov_media_frac 构成省/市双层嵌套的一对地理份额, 市级是更严格 (更小半径) 的邻近口径。地理邻近维度与行政层级 (中央/地方)、内容属性、政治取向、出版频率等正交, 九维为规格稳健性并排、各自 just-identified, 禁混同一 over-identified Hansen J。本列为纯来源构成比率, 不涉三轨情感。

## VAR: homeprov_media_frac

【变体差分】
本列是地理邻近性维度中省级层面的本地媒体份额, 判据为报道来源媒体所在省份与目标银行注册地省份一致 (_is_homeprov)。分子为单元内同省报道行数, 分母为该单元报道行数, 取均值。其构念与 homecity_media_frac 同源 (本地媒体因广告依赖与地方政府关系而系统性正面倾斜), 但采用更宽 (更大半径) 的省级邻近口径: 同省包含同城, 因此本列是同城份额的超集, 数值上恒不小于 homecity_media_frac, 代码在同城为 1 时强制同省也为 1, 并在文末以 1e-10 容差校验 homeprov ≥ homecity 的单调不违反。来源省不可知的报道同样置为 NaN、不强制归异地, 与同城口径一致。省级与市级两层平行构建, 目的在于以两种邻近半径互为稳健性: 省级口径样本更充分、噪声更低但邻近性更弱, 市级口径邻近性更强但来源可识别率更低。本列与 homecity 属同一地理维度的两层嵌套份额, 与行政层级、内容属性、政治取向、出版频率诸维度正交。九维之间为规格稳健性并排、各自 just-identified, 禁把不同层/维的份额混入同一 over-identified 的 Hansen J 检验。本列为纯来源构成比率, 不涉三轨情感; 对应的同省/非同省情感缺口是另立副产品。

## VAR: market_media_frac

【变体差分】
本列是政治取向维度 (维度⑥) 中的纯市场化媒体份额。分类以 NPPA 数据库主办单位为企业/商业集团为判据界定 MARKET 集合, 但因官方 (主管单位为党政机关) 与市场化 (主办单位为企业) 双判据在实证上非互斥 (重叠 386 家), 本列采用结构性互斥的净化构造: _is_market 判据为媒体落入 MARKET 减 OFFICIAL (纯市场化), 即企业主办且主管非党政机关者。分子为单元内纯市场化报道行数, 分母为该单元报道行数, 取均值。构念动机为: 市场化媒体依赖广告与发行收入, 报道更独立、批判性更强, 具备更强的媒体治理功能, 故纯市场化份额高意味着银行-fintech 叙事更多来自独立、批判性信息源。本列与 official_media_frac (纯官方 = OFFICIAL 减 MARKET) 结构性互斥、二者之和不超过 1 (文末 (7b) 校验); 双判据媒体 (OFFICIAL ∩ MARKET) 不计入任一处理组, 落入 nonoff/nonmkt 两对照。须披露: 该操作化以主管 vs 主办双判据近似 You/Zhang/Zhang 型官方-市场化对立构念, 论文层应重述其非互斥性来源。政治取向维度与内容属性、出版频率、地理邻近正交; 九维为规格稳健性并排、各自 just-identified, 禁混同一 over-identified Hansen J。本列为纯来源构成比率, 不涉三轨情感。

## VAR: official_media_frac

【变体差分】
本列是政治取向维度 (维度⑤) 中的纯官方媒体份额, 与 market_media_frac 结构性互斥、互为对照。分类以 NPPA 数据库主管单位为党政机关为判据界定 OFFICIAL 集合; 因双判据非互斥, 本列采用净化构造 _is_official = 媒体落入 OFFICIAL 减 MARKET (纯官方), 即主管为党政机关且主办非企业者。分子为单元内纯官方报道行数, 分母为该单元报道行数, 取均值。此净化尤为必要: 若直接用原始 OFFICIAL (约 2208 家, 近全集) 构造 dummy, official_media_frac 会近退化 (历史实测均值约 0.873)、且 nonoff 对照组反而剔除了大部分市场化媒体, 使官方-市场化对立构念被重叠掩盖。改为 OFFICIAL 减 MARKET 后, 企业主办的市场化媒体不再计入官方组、归入对照, 修正了 tone_gap_official_nonoff 的对照定义。构念上官方媒体受国有控制与政治激励影响, 报道倾向与市场化媒体系统性不同 (如官方媒体负面报道对治理的影响弱于市场化媒体), 故纯官方份额高意味着叙事更多来自受政治激励约束的信息源。本列与 market_media_frac 之和不超过 1, 双判据媒体不计入任一处理组。政治取向维度与其余维度正交, 九维为规格稳健性并排、各自 just-identified, 禁混同一 over-identified Hansen J。本列为纯来源构成比率, 不涉三轨情感。

<!-- rendered-citations:begin -->
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. Journal of Financial Economics, 135(2), 445-467. https://doi.org/10.1016/j.jfineco.2019.06.003
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
<!-- rendered-citations:end -->
