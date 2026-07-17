---
family_id: F453
columns:
- neg_frac_nonprov_ctx
- neg_frac_nonprov_full
- neg_frac_nonprov_ss
unit: 比率/占比 (proportion, [0,1]; 银行-年层面的负面报道占比)
formula: 'neg_frac_nonprov_{trk} = (该银行-年由非属地省份媒体产出、且情感判为负面的报道篇数) / (该银行-年由非属地省份媒体产出的报道总篇数); 分子分母口径逐轨 (full/ctx/ss) 各自独立统计, 分母为 0 (该银行-年无非属地省媒体报道) 时置 NaN'
producer: pipeline\panel\attention_media.py::compute_media_heterogeneity
upstream:
- 11_news_bank
- 21_tone_llms
- config/bank_addresses.json (银行属地省/市映射, 经 _bank_prov_map/_bank_city_map 构造 _bank_prov/_bank_city 列)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: 'Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy'
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: "10.1016/j.frl.2024.105024"
  type: "journal"
  authors: "Huang, W., Liu, J., & Zhang, R.-Z. (."
  year: 2024
  title: "Local newspaper closures and non-GAAP reporting quality"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105024"
- doi: "10.1111/1911-3846.12935"
  type: "journal"
  authors: "Huang, Y., Li, F., Li, T., & Lin, T."
  year: 2024
  title: "Local information advantage and stock returns: Evidence from social media"
  venue: "Contemporary Accounting Research"
  vol: "41"
  issue: "2"
  pages_or_artno: "1089-1119"
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是地理邻近性视角下的媒体负面报道倾向: 对每家银行-年样本, 先按报道媒体的注册属地是否等于该银行总部所在省份, 把全部报道划分为"属地省媒体 (homeprov)"与"非属地省媒体 (nonprov)"两个互斥子集, 再在"非属地省媒体"子集内统计负面篇数占比, 即为本家族三个变体的共同基座。这一构念直接呼应地理邻近性文献里关于本地媒体与非本地媒体报道基调系统性差异的经典发现: 本地媒体因广告收入依赖、区域声誉维护等激励更倾向于压制负面报道 (即"护犊子"效应), 而非属地媒体因缺乏这类经济捆绑, 更可能如实呈现或放大负面信息。因此 `neg_frac_nonprov_*` 与其孪生家族 `neg_frac_homeprov_*` 构成一组对照测度: 二者之差 (或比值) 即是"属地媒体是否系统性地更少负面报道"这一假说的直接经验证据, 呼应 CLAUDE.md 记录的地理邻近性维度⑨ (与 `tone_homeprov_media_full`/`tone_nonprov_media_full`/`tone_gap_homeprov_nonprov_full` 等同批产出的地理-媒体情感/负面占比矩阵) 共享同一属地判定逻辑与分组口径, 只是本家族聚焦"负面篇数占比"而非"平均情感分"这一连续测度, 二者互补而非替代: 情感均值对极端值与中性文章的稀释更敏感, 而负面占比是对"有多大比例的报道明确唱衰"这一离散事件比例的直接刻画, 在稳健性叙事中常配对出现以交叉验证结论方向的一致性。

【方法学与计算】
构造分两步, 由 `pipeline/panel/attention_media.py::compute_media_heterogeneity` 计算。第一步是媒体属地判定: 依据 `config/bank_addresses.json` 中银行总部/主要经营省份的映射 (经 `_bank_prov_map`/`_bank_city_map` 构造 `_bank_prov`/`_bank_city` 列), 结合报道来源媒体的注册属地元数据 (媒体名录中的省份字段), 对样本期内每一篇报道打上"属地"或"非属地"二元标签; 这一判定与孪生家族 `neg_frac_homeprov_*`、`tone_homeprov_media_*`/`tone_nonprov_media_*` 共用同一套省份匹配规则, 保证两个方向 (属地 vs 非属地) 的分组互斥且穷尽 (即每篇报道恰好落入其中一组, 不存在既非属地也非非属地的第三态)。第二步是负面篇数占比统计: 对每家银行-年的"非属地省媒体"子集, 以 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票产出的情感判定 (`llm_vote_tone`) 是否落在负面类别为准, 统计该子集内负面篇数占子集总篇数的比例。三个变体分别对应三条文本轨道: `_full` 用标题+正文全文情感判定, `_ctx` 用标题+银行实体窗口文本情感判定, `_ss` 用标题+银行∧金科同句(±N 窗口, 默认1)文本情感判定; 三轨在情感投票阶段各自独立跑一遍, 互不借用彼此的判定结果。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 是否计入"该篇报道"这一分母/分子基本单位, 只看 `llm_verified_full == True` 这一全文轨的验证结果, ctx/ss 轨的负面占比统计是在 full 轨留篇集合的子集之上、按各自轨道重新跑情感判定后计算, 而非独立留篇。`_ss` 轨的回退语义镜像 `_ctx`: 当某篇报道内银行实体与金科词并无同句共现时, `content_ss` 退化为全文正文 (`ss_is_fallback=True`), 此时该篇在 `_ss` 轨的情感判定退化为等价于全文判定, 分母仍计入该银行-年 `_ss` 轨的 `n_articles` 统计。分母为 0 (该银行-年样本期内不存在任何非属地省媒体报道) 时该银行-年该轨观测置为 NaN, 而非 0, 以避免把"无非属地报道"这一缺失状态误读为"非属地报道零负面"。

【文献定位】
地理邻近性对媒体报道基调系统性影响的识别策略, 经典范式见 Gurun and Butler (2012, The Journal of Finance), 该文利用本地/非本地媒体广告收入与企业价值的关联, 论证本地媒体存在系统性正面偏向; 本家族的属地/非属地二分与负面占比构造直接承袭这一识别框架, 把银行总部所在省份作为"本地"锚点, 区分省内(属地)与省外(非属地)媒体子样本。负面倾向抑制的另一支文献强调信息压制的政治经济学动机: Piotroski, Wong, and Zhang (2015, Journal of Accounting Research) 发现存在压制负面信息的政治激励, 与本家族"属地媒体或系统性少报负面"这一假说方向一致, 为 `neg_frac_homeprov_*` 显著低于 `neg_frac_nonprov_*` 这一预期模式提供理论支撑。情感极性判定本身 (何为"负面")继承自 stage 21 三家 LLM 投票的情感分类框架; Schoenegger, Tuminauskaite, Park, Bastos, and Tetlock (2024, Science Advances) 在预测市场/预测问题场域证实, 多个 LLM 的集成判断在准确度上可比拟乃至超过人类群体智慧, 其研究场景虽是预测准确度而非情感极性分类, 但"多模型集成优于单模型判定"这一一般性原理与本家族依赖 stage 21 三家 LLM 多数投票(而非单模型判定)产出负面标签的设计选择相呼应, 为该设计提供了较弱但方向一致的方法学佐证, 使用时应注意其证据来自不同任务域, 不构成对情感分类效度本身的直接检验。就"占比"这一统计量在分母较小(非属地报道篇数很少)时点估计噪声偏大这一统计学性质而言, 本家族与孪生家族 `neg_frac_homeprov_*` 采取相同应对: 分母为 0 时置 NaN 而非 0, 提醒使用者在样本量过小的银行-年观测上谨慎解读点估计。 近期文献从三个方向补强了上述属地/非属地二分的构念与设计前提。Huang、Liu 与 Zhang (2024) 以本地报纸停刊作为本地媒体监督减弱的冲击, 检验公司非 GAAP 披露质量的变化, 其识别前提即总部所在地的本地媒体与异地媒体在监督功能上不可相互替代, 直接支撑本家族按媒体来源省份切分属地/非属地子样本、并在其上作负面占比对比的构念依据; 但该文走停刊事件的 DiD 识别、语境为美国报纸与美国上市公司, 且被解释变量是披露质量而非媒体语调, 该文并未度量本地媒体的报道倾向, 故此处仅锚定“本地媒体构成独立信息渠道”这一半, 不锚定其语调或负面判定算法。Huang、Li、Li 与 Lin (2024) 依据社交媒体用户的地理位置识别本地信息发布者, 按发布者与公司总部的地理关系切分样本并比较本地组与非本地组的信息含量差异, 与本家族属地/非属地子样本对比的设计同族; 其文本源为社交媒体发帖 (UGC) 而非本项目的正式媒体报道, 地理归属基于用户 IP/自报位置而非媒体来源省份字段的词典比对, 且研究对象为一般上市公司、被解释变量为股票收益, 地理粒度亦为同城二分而非省级, 因此只锚定地理二分子样本对比这一设计逻辑, 不锚定测度构造。Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度并将其应用于意大利银行的融资条件, 为“新闻语调 → 银行层级结果”这一链条提供近期同域实践参照; 该文语料为意大利媒体, 无中文情感词典与三家 LLM 投票口径, 亦无 full/ctx/ss 三轨切分与属地/非属地划分, 故仅作同域存在性参照, 不支持本家族的具体分母口径与 NaN 哨兵设计。
## VAR: neg_frac_nonprov_ctx

【变体差分】
本列是家族内的 ctx 轨变体: 情感判定所依据的文本是标题+银行实体窗口文本 (`content_ctx`, stage 14 物化), 而非全文正文。属地/非属地媒体分组逻辑与 `_full`/`_ss` 完全一致 (只看报道来源媒体注册省份是否等于银行总部省份), 差异仅在于"负面"这一判定标签的文本依据窗口更窄、聚焦银行实体周边语境, 剔除了正文中与该银行无直接语境关联的段落干扰。留篇门控仍遵循 full-only 铁律: 计入统计的报道范围(分母基本单位)由 `llm_verified_full` 决定, `_ctx` 轨只是在该留篇集合之上换一条文本窗口重新做情感判定, 不额外筛选或扩大样本范围。三轨 (full/ctx/ss) 之间是互为稳健性、不分主次的并排关系, 各自 just-identified, 严禁把三轨的负面占比测度混进同一个 over-identified 的 Hansen J 检验框架中联合识别 —— 三者应作为独立的稳健性检验分别报告, 而非当作同一构念的多重工具变量叠加使用。相比 `_full` 轨, `_ctx` 轨对报道正文中"标题党"式引流与银行无关的背景铺陈更不敏感, 更贴近"报道文本中直接谈及该银行的部分是否呈负面基调"这一更精细的构念; 但代价是当银行实体窗口过窄导致语境残缺时(如否定词跨窗口被截断), 情感判定可能与全文判定产生方向性分歧, 这正是设置该轨作为稳健性对照而非替代 `_full` 轨的动机所在。

## VAR: neg_frac_nonprov_full

【变体差分】
本列是家族的 full 轨变体, 也是三轨中唯一承担留篇门控职能的基准轨: 情感判定依据标题+正文全文文本 (`content_full`), 是否计入某银行-年"非属地省媒体报道总篇数"这一分母、以及该篇是否算作"负面"篇数的分子贡献, 均以全文轨的 `llm_verified_full == True` 判定与全文轨情感投票结果为准。`_full` 轨在 P1 主线 (`bank_fintech_tone`) 与 provisional `bank_news_clarity` 中均已切换为主测度轨 (2026-07-02 起), 本家族的 `_full` 列因此在三轨并排关系中承担事实上的"默认呈现口径"角色, 但这并不改变三轨互为稳健性、禁止混入同一 over-identified Hansen J 的铁律 —— `_full` 只是门控意义上的基准, 在识别策略层面仍与 `_ctx`/`_ss` 并列、各自 just-identified。分母口径为该银行-年样本期内、来源媒体注册省份不等于银行总部省份的全部留篇报道数; 分子为其中情感投票落入负面类别的篇数; 分母为 0 时置 NaN。该列与孪生列 `neg_frac_homeprov_full` 构成本轨下的属地对照组, 二者之差是检验 Gurun and Butler (2012) 式本地媒体正面偏向假说在本样本(中国银行业金融科技报道)中是否成立的核心统计量之一。在三轨并排关系中, `_full` 轨因文本窗口最宽, 覆盖了正文中与银行、金科话题相关及不直接相关的全部段落, 其负面占比测度对整体报道基调最具代表性, 但也更容易被与银行主题弱相关的负面信息(如同篇报道中提及的宏观风险事件、行业共性负面新闻)带偏, 这正是需要 `_ctx`/`_ss` 两条更窄语境窗口轨作为并排稳健性检验的原因; 三者结论方向一致时, 才能对"非属地媒体负面报道占比更高"这一假说给出更有说服力的经验支持。

## VAR: neg_frac_nonprov_ss

【变体差分】
本列是家族内的 ss 轨变体: 情感判定依据的文本是标题+银行∧金科词同句共现窗口 (`content_ss`, ±N 句半径, 默认 N=1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制), 是三轨中语境窗口最窄、判据最严格的一支, 聚焦"银行与金科话题在同一句话中被提及"这一更强的相关性判据。回退语义镜像 `_ctx`: 若某篇报道内不存在银行实体与金科词的同句共现, `content_ss` 退化为全文正文, 对应 `ss_is_fallback=True`, 该篇在本轨的负面判定实质上退化为全文判定, 但其"是否非属地媒体"这一分组标签、以及是否计入分母的留篇资格判定不受影响, 仍共享同一 `n_articles` 分母口径。留篇门控同样遵循 full-only: 样本范围由 `llm_verified_full` 决定, `_ss` 轨只负责在该集合内重新执行情感判定与分组统计。`_ss` 轨与 `_full`/`_ctx` 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 联合估计。相比 `_ctx`, `_ss` 轨的判据更贴近"该银行与金融科技话题被同句强关联提及"这一更严格的相关性设定, 因而在非属地媒体子样本本就较小的银行-年观测下, 有效样本可能进一步收缩 (更多篇章因无同句共现而回退为全文判据), 解释时应留意分母的实际有效样本规模, 避免把回退主导的观测误读为"同句判据下"的真实占比。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Huang, W., Liu, J., & Zhang, R.-Z. (. (2024). Local newspaper closures and non-GAAP reporting quality. Finance Research Letters, 62, 105024. https://doi.org/10.1016/j.frl.2024.105024
Huang, Y., Li, F., Li, T., & Lin, T. (2024). Local information advantage and stock returns: Evidence from social media. Contemporary Accounting Research, 41(2), 1089-1119. https://doi.org/10.1111/1911-3846.12935
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
