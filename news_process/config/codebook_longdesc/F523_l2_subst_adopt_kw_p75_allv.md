---
family_id: F523
columns:
- subst_adopt_kw_p75_allv
- subst_adopt_kw_p75_allv_ctx
- subst_adopt_kw_p75_allv_ss
unit: 比例 (bank-year 内已测量文章中落入"实质采纳"象限的占比, [0,1], 无量纲)
formula: 'subst_adopt_kw_p75_allv{_ctx,_ss} = mean_i( 1{ freq_i(kw,轨) >= Q75_year(freq(kw,轨)) AND sim_i(allv,轨) >= Q75_year(sim(allv,轨)) } ), 逐篇仅在 freq/sim 双双非缺失时参与分类与分母 (未测量文章 NaN 掩码, 不计零)'
producer: pipeline\filtering\policy_alignment.py ; pipeline\panel\runner.py::_classify_policy_quadrants
upstream:
- 15_fintech_intensity (fintech_distinct_keywords 词频)
- 16_article_policy_alignment (policy_cosine_sim_allv 全年份锚点余弦)
- 21_tone_llms (llm_verified_full 留篇门控上游, 经 semi-join 限定到留篇宇宙)
citations:
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H.; Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D.; Zajac, E. J.
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C.; Zajac, E. J.
  year: 2006
  title: 'The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling'
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A.; Kraus, M.; Leippold, M.; Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A.; Kraus, M.; Leippold, M.; Webersinke, N.
  year: 2022
  title: 'Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R.; Gao, J.; Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行—金融科技新闻报道在"言"(话语层面提及金融科技关键词的强度)与"行"(话语与权威政策文本在语义上的贴合程度)两个维度上是否同步兑现, 用以区分银行对金融科技的"实质采纳"(substantive adoption)与"象征性/洗术语式采纳"(token/symbolic adoption)。该四象限构念源自组织理论中的 decoupling/symbolic management 文献: Westphal & Zajac (1994, 2006 Fiss & Zajac 扩展) 指出企业可以在正式话语/制度采纳与实际实践之间产生系统性脱耦, 话语热度并不必然对应实践投入; Kim & Lyon (2015) 在可持续披露语境下将这种脱耦形式化为"greenwash"(话语超前于实践)与"brownwash"(实践超前于话语)两种非对称错配, 本家族的四象限设计正是这一逻辑在银行金融科技新闻语境下的移植: 纵轴用"金融科技关键词词频"代理话语强度, 横轴用"文章与权威政策语料的余弦相似度"代理与官方政策实践方向的贴合度, 两轴各自按年度分位数二值化后交叉产生 Token(高词频/低相似度, 类比"洗科技术语")、Hidden(低词频/高相似度, 类比"闷声干大事")、Substantive(高词频且高相似度, 言行一致的实质采纳)与 Irrelevant(双低)四格。`subst_adopt_kw_p75_allv` 三列即 Substantive 格在 P75 阈值、关键词(kw)词频轨、全年份锚点(allv)相似度口径下、按 bank-year 聚合的占比。

方法学同时借鉴文本量化对齐的锚点注入范式: 本项目上游 stage 16 `article_policy_alignment` 采用与文本量化对齐/政策语义锚点测度文献一脉相承的做法, 用银行新闻文章嵌入与权威政策文本锚点嵌入的余弦相似度衡量话语与官方政策议程的语义贴合, 而非依赖表层关键词匹配。近年 LLM/embedding-based 话语—实践脱耦测量文献(如 Bingler et al. 2022 关于 ClimateBert 识别气候披露中"cherry-picking"式话语操纵、Bingler et al. 2024 关于"cheap talk"与真实排放/声誉风险的对齐检验; Duchin, Gao & Xu 2025 用资产市场证据区分真实可持续性投入与漂绿)进一步确认: 单纯的话语强度信号(词频/关键词密度)极易被策略性操纵而与真实行动脱钩, 必须与语义对齐/外部实践证据联合识别, 才能把"实质"从"象征"中分离出来。本家族即是这一方法论共识在中国银行业金融科技新闻场景的具体实现: 词频度量捕捉"说了多少", 政策相似度度量捕捉"说的是不是官方鼓励的那个方向", 二者交叉才判定为言行一致的实质性响应。

【方法学与计算】
构造分两层。第一层是逐篇文章级二值分类 `_classify_policy_quadrants`(`pipeline\panel\runner.py`): 对给定轨道(full/ctx/ss)与锚点口径(vintage 主轨/allv 全年份锚点), 分别取该篇文章的关键词词频列 `fintech_distinct_keywords{轨}` 与政策相似度列 `policy_cosine_sim_allv{轨}`, 按年度(而非全样本)计算两列的 P75 分位数作为当年阈值(`groupby('year').transform(quantile)`), 逐篇比较词频/相似度是否达到当年阈值, 得到 Token/Hidden/Substantive 三个互斥示性变量(第四格 Irrelevant 未单独物化为面板列, 可由 1 减前三者的 bank-year 均值反推)。测量缺失显式掩码: 只有词频与相似度同时非缺失的文章才参与分类, 任一缺失(如该年政策语料未覆盖、或该篇未通过留篇门控)的文章在示性变量上记为 NaN 而非误判为"低"(2026-06-11 fix, 避免 stage 15/16 优雅早退产生的全 NaN parquet 把未测量文章系统性错分进 Token 格)。第二层是 bank-year 聚合: 按 `(target_bank, year)` 分组对示性变量取 `mean`, pandas 的 `mean` 默认跳过 NaN, 因此分母是该 bank-year 内已测量的文章数而非全部报道数; 若某 bank-year 全部文章都未测量, 输出面板值为 NaN(而非误导性的 0), 与项目 F3 铁律("无数据=未测量=NaN, 不可与真实零混淆", 参照 Allison 2001 §3 对不平衡面板缺失机制的讨论)一致——该聚合逻辑对本家族与整个 token/hidden/subst_adopt 列族(`export.py`/`runner.py` 中以 `token_adopt_/hidden_adopt_/subst_adopt_` 为前缀的全部列)统一适用, 且面板聚合阶段刻意删除了旧版本的 `fillna(0.0)` 兜底(2026 v6/F3 修复), 因为对"率/相似度类"指标强行填零会把未测量语义污染为虚假的低采纳信号, 扭曲 TWFE 回归系数。

列名中的 `kw` 标识词频轨采用 `fintech_distinct_keywords`(去重后命中的金融科技关键词种类数, 来自 stage 15 fintech_intensity 的 Aho-Corasick 扫描), 与之并列的另一词频轨 `int`(`fintech_intensity_score`, 连续强度分)属另一家族, 二者是互为稳健性、不分主次的并排测度, 不应混入同一 over-identified 设定。`p75` 标识分类阈值取年度第 75 百分位(该项目同时物化 P25/P50/P75 三档分位阈值梯子, 各阈值同样各自独立、互为稳健性, P75 相对 P50/P25 门槛更严格, 划入"高词频"/"高相似度"的文章更少, 因而 Substantive 格的占比通常随阈值上移而下降)。`allv`(all-vintage)标识相似度锚点口径: 项目 stage 16 的主轨相似度 `policy_cosine_sim`(vintage-aware)对年度 t 的文章只用发布年份 ≤ t 的政策文档拼接构造语义锚点, 目的是消除"用尚未发布的政策文件去解释更早年份新闻"的前视(look-ahead)构造性偏误; 而 `_allv` 锚点则退回旧口径, 用全部年份(含未来)的政策文档拼成一个静态全语料锚点计算余弦相似度, 除锚点文本集合不同外, 嵌入模型、池化方式、余弦计算、四象限分类逻辑与主轨完全一致(`policy_alignment.py::all_vintage_companion_enabled` 文档字符串明确"完全一致的下游构造方法")。`_allv` 存在的唯一目的是回答审稿人常见追问——"vintage 前视守卫本身是否驱动了结论?"——作为纯粹的稳健性对照轨, 绝不能替换 vintage 主轨作为主回归设定, 也绝不能与 vintage 主轨混入同一个 over-identified 检验(如 Hansen J 过度识别检验), 二者各自 just-identified 并排使用。三轨文本(full 全文/ctx 实体窗口/ss 银行∧金科同句窗)与 allv/vintage 锚点口径、以及 kw/int 词频轨、P25/P50/P75 分位阈值合计构成一个多维度的稳健性网格, 任意两个维度的组合都只应作为彼此独立的稳健性证据并排报告, 不应合并进同一工具变量识别方程。

行宇宙口径: 与项目 2026-06-29 起的留篇门控(full-only gate)一致, "一篇文章是否算作银行—金融科技报道"由 `llm_verified_full` 决定; ctx/ss 轨的分类与聚合是在这一 full 留篇集合的子集上分别计算各自轨道的词频与相似度, 而非独立扩展行宇宙。分母(已测量篇数)因此随轨道 (full/ctx/ss) 与锚点 (vintage/allv) 组合各自结算, 不跨轨借用。

【文献定位】
本家族横跨两支文献。其一是组织理论中的话语—实践脱耦/象征管理传统: Westphal & Zajac (1994) 最早在 CEO 长期激励计划采纳研究中区分"substance"(实质条款设计)与"symbolism"(仅为满足制度合法性压力的表面采纳), 发现二者驱动因素与后果显著不同; Fiss & Zajac (2006) 进一步用框架建构(sensegiving)与脱耦(decoupling)机制解释企业如何在战略变革叙事与实际执行之间制造系统性落差; Kim & Lyon (2015) 把这一逻辑正式化为可持续披露语境下的 greenwash/brownwash 双向错配框架, 是本四象限设计(词频×相似度二维交叉)最直接的概念原型。其二是文本量化对齐与"话语可信度"检验文献: Bingler et al. (2022) 用 ClimateBert 类模型识别企业气候披露中"cherry-picking"式的选择性话语操纵, Bingler et al. (2024) 进一步检验这类"cheap talk"(话语与实际排放/举措脱节的部分)是否与真实气候举措、企业排放及声誉风险对齐, 二者合力方法论上确认单一文本信号(如关键词密度)不足以区分真实承诺与策略性话术, 须结合语义对齐或外部结果证据联合判定; Duchin, Gao & Xu (2025) 则从资产市场交易行为的角度提供了可持续性投入 vs. 漂绿的外部验证证据, 呼应"话语强度需要独立信号交叉验证"这一识别逻辑。本家族的政策相似度轴(`policy_cosine_sim_allv`)在方法上承袭本项目 stage 16 `article_policy_alignment` 模块的锚点注入设计, 用政策语料嵌入构造语义锚点、以余弦相似度替代表层关键词匹配衡量话语与官方议程的贴合度, 而 `_allv` 全年份静态锚点这一稳健性口径本身则是对"锚点文本时间窗选择是否驱动结论"这一 identification 关切的显式回应, 与项目其余稳健性梯子(政治词权重/词典消融/BERT 阈值)遵循同一"多口径并排、互不替代"的方法论立场。

## VAR: subst_adopt_kw_p75_allv

【变体差分】
本列为家族 canonical 列, 对应 full 轨(标题+全文正文)。词频侧使用 `fintech_distinct_keywords`(无轨道后缀, 该列为 track-agnostic 元数据——去重关键词种类数本身不区分全文/实体窗口/同句窗口, ctx/ss 变体缺失时按设计复用 full 列, 因此三个变体在词频侧实际共享同一分母输入, 差异完全来自相似度侧的文本轨道); 相似度侧使用 `policy_cosine_sim_allv`(无轨道后缀, 即 full 轨全年份静态锚点余弦)。分类阈值为该 bank-year 所在年份内该轨该锚点口径下词频与相似度的第 75 百分位, 逐篇双高(词频≥P75 且相似度≥P75)记为 1, 双高但任一缺失记为 NaN, 按 bank-year 取均值。该列是本 P3 家族(bank_fintech_substance, W&Z 传统)在 allv 锚点稳健性口径下、P75 严格阈值、kw 词频轨、full 全文轨的实质采纳占比测度, 是三个 track 变体中样本覆盖最广(不受 ctx/ss 实体窗口/同句窗口缺失导致的额外未测量约束)、通常也是论文中作为稳健性对照表首列报告的口径。

需特别提示两条与本列同名但邻近含义的兄弟列的关系, 以防混淆解读: 一是词频轨兄弟 `subst_adopt_int_p75_allv`(用连续型 `fintech_intensity_score` 而非离散去重关键词数作词频代理), 二是锚点轨兄弟 `subst_adopt_kw_p75`(去掉 `_allv` 后缀, 即 vintage-aware 主轨口径, 相似度只用发布年份 ≤ 当年的政策文档构造锚点)。本列(kw + p75 + allv + full)与这两个兄弟在数值上通常高度相关但不代数等价——阈值分位数逐年重新计算、相似度锚点集合不同, 两个来源的差异都会传导到最终占比。研究者若观察到本列(allv 稳健口径)与主轨 `subst_adopt_kw_p75` 结论方向一致、量级接近, 即可作为"vintage 前视守卫本身未驱动结论"的证据; 若二者出现系统性偏离, 则提示应进一步排查主轨政策语料的年份覆盖是否稀疏导致早期年份锚点不稳定。

## VAR: subst_adopt_kw_p75_allv_ctx

【变体差分】
与 canonical 列的唯一差分维度是文本轨道: 相似度侧改用 `policy_cosine_sim_allv_ctx`(标题+目标银行实体窗口文本、经 stage 14 `ctx_materializer` 物化后独立嵌入计算的全年份锚点余弦), 词频侧优先取同轨变体 `fintech_distinct_keywords_ctx`(若该列缺失, 按设计优雅回退复用 full 轨词频并在日志披露, 因关键词计数本身可以是 track-agnostic 元数据)。年度分位阈值、双高交叉分类逻辑、bank-year 聚合方式与 canonical 列完全一致, 仅输入的相似度列文本窗口更窄。ctx 轨相似度衡量的是"围绕目标银行实体的局部语境"与政策语料的贴合度, 相较 full 轨剔除了文章中与目标银行不直接相关的段落噪音, 但当某篇文章未产出有效的实体窗口(ctx 物化回退为全文, 由 `ctx_is_fallback` 标记)时, 该篇在 ctx 轨的"独立性"退化为与 full 轨趋同。本列与 canonical 列(full)、`_ss` 列(同句窗)三者是互为稳健性、不分主次的并排口径, 任何回归设定禁止把三轨结果混入同一个 over-identified 检验(如联合 Hansen J), 只应作为独立稳健性行分别报告。

从构念区分角度看, ctx 轨的取舍逻辑是: full 轨相似度容易被文章中大段与目标银行无关的背景叙述(如宏观经济评论、监管政策通稿转述)稀释或污染, 使"话语强度"与"政策贴合度"两个维度都掺入非目标银行自身的信号; ctx 轨通过限定在实体窗口内计算相似度, 试图更纯粹地捕捉"这篇报道谈到该银行时, 具体在多大程度上呼应官方政策语言"这一构念。但这一优势是有代价的: 实体窗口截取依赖于命名实体识别与窗口大小配置(`config/filtering.yaml::context_window`), 窗口过窄可能切断关键的语境信息(例如把"该行推出的XX产品"这一具体金融科技实践描述切在窗口边界外), 因此本列相对 canonical full 轨列, 既可能因为聚焦而提高信噪比, 也可能因为窗口截断而低估真实的实质采纳信号, 两种效应的净方向须由数据检验而非先验判断。

## VAR: subst_adopt_kw_p75_allv_ss

【变体差分】
与 canonical 列的差分维度同样是文本轨道, 但窗口比 ctx 更窄: 相似度侧使用 `policy_cosine_sim_allv_ss`(标题+目标银行与金融科技词汇同句共现窗口, 半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制、默认±1句, 经 stage 14 物化后独立嵌入计算的全年份锚点余弦), 词频侧优先取同轨变体 `fintech_distinct_keywords_ss`, 缺失时同样优雅回退复用 full 轨词频。分类与聚合逻辑与 canonical 列一致。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行与金融科技词汇同句共现时, `content_ss` 退化为全文 body 且 `ss_is_fallback` 置 True(与 ctx 共享 `n_articles` 分母口径), 该篇在 ss 轨的相似度衡量实质上趋同于 full 轨, 而非产生缺失。ss 轨代表本家族中语境窗口最严格、噪音剔除最彻底的版本——只保留银行与金融科技话语真正"同框"出现的句子上下文, 因此对"该文章是否真的在谈论银行自身的金融科技实践"这一构念比 ctx/full 更贴近, 但相应地更容易受窗口过窄导致的信息不足影响(尤其在同句共现本就稀疏的样本上)。本列与 full/`_ctx` 两列同属三轨并排稳健性设计, 各自 just-identified, 不设主次, 且不得混入同一 over-identified 识别方程。

三轨相对严格程度可理解为一个递进谱系: full 轨(全文)信息量最大但噪音也最多, ctx 轨(实体窗口)通过命名实体定位缩小范围, ss 轨(同句共现)则要求银行与金融科技词汇字面上同处一句(或 config 设定半径内), 是三者中判定标准最苛刻的一档。这一设计意图是: 若一篇报道真的在描述"该银行做了某项金融科技实践", 那么描述该实践的句子理应同时出现银行主体与金融科技相关词汇, ss 轨因而被设计为对"实质性描述"最敏感、对"泛泛提及"最不敏感的窗口。但当样本中银行—金科同句共现本就稀疏(尤其在中国银行业新闻语料早期年份, 金融科技术语尚未普及)时, ss 轨的回退比例会显著高于 ctx 轨, 大量文章退化为等同 full 轨计算, 此时该列在统计意义上接近 canonical 列, 稳健性检验的边际信息量随之下降, 解读时应结合 `ss_is_fallback` 回退占比一并考察, 避免把"窗口设计带来的差异"与"回退主导下的伪一致"混为一谈。

<!-- rendered-citations:begin -->
Kim, E.-H.; Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Westphal, J. D.; Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C.; Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Bingler, J. A.; Kraus, M.; Leippold, M.; Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Bingler, J. A.; Kraus, M.; Leippold, M.; Webersinke, N. (2022). Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Duchin, R.; Gao, J.; Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
<!-- rendered-citations:end -->
