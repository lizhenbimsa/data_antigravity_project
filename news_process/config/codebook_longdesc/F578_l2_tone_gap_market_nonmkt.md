---
family_id: F578
columns:
- tone_gap_market_nonmkt_ctx
- tone_gap_market_nonmkt_full
- tone_gap_market_nonmkt_ss
unit: 语调缺口 (连续, 理论范围约 [-2,2]; 两个子均值之差, bank-year 面板)
formula: 'tone_gap_market_nonmkt{track} = tone_market_media{track} - tone_nonmkt_media{track};
  其中 tone_market_media{track} = mean(llm_vote_score{track} | _is_market==1) 按
  (target_bank, year) 分组, tone_nonmkt_media{track} = mean(llm_vote_score{track}
  | _is_market==0) 同口径分组; _is_market = 媒体(中文) ∈ (MARKET − OFFICIAL) 名单'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss)
- 11_news_bank.parquet (target_bank)
- config 媒体名单 (NPPA 主办单位口径, MARKET / OFFICIAL 集合)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving Content to Investor Sentiment - The Role of Media in the Stock Market
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing Enthusiasm - Media Sentiment and the Disciplining Role of Quarterly
    Earnings Announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: Media Sentiment, Deposit Stability and Bank Systemic Risk - Evidence from
    China
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.ememar.2024.101234
  type: journal
  authors: Xu, Z., Hua, X., & Zhang, T.
  year: 2025
  title: Does Official Media Sentiment Matter for the Stock Market? Evidence from
    China
  venue: Emerging Markets Review
  vol: '64'
  pages_or_artno: Article 101234
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列 (`tone_gap_market_nonmkt_full`/`_ctx`/`_ss`) 度量同一 bank-year 报道池内「市场化媒体」与「非市场化媒体」对目标银行报道语调的均值缺口, 出自 `pipeline/panel/attention_media.py` 维度⑥ (「政治取向 - 市场化 vs 非市场化」区块)。构念来源直接对标 You, Zhang & Zhang (2018, RFS)「谁执笔杆子」的核心发现: 市场化媒体因收入结构 (依赖广告与发行, 而非财政拨款) 独立于行政科层, 报道更具批判性与信息价值, 其负面报道对公司治理 (高管更替) 有显著的纪律约束效应, 而官办媒体因承担宣传/维稳职能, 报道基调系统性偏正面且较少反映真实经营信息。本家族把这一「媒体所有制/资金来源→报道立场」的因果机制操作化为一个可直接进面板回归的缺口变量: 缺口越正, 说明该行在市场化媒体眼中比在非市场化媒体眼中更正面 (或反之为负), 缺口本身即是一种「媒体异质性引起的语调分歧」度量, 可用于检验治理假说 (市场化媒体是否更早/更强地捕捉银行的负面信息)、媒体俘获假说、以及作为工具变量构造的媒体暴露基础。
与家族 F 同批的另一相邻家族维度⑤「官方 vs 非官方」(official/nonoff) 在构念上是政治-科层维度, 维度⑥「市场化 vs 非市场化」是资金/激励维度, 两者并非同一分类的互补事件, 而是两套独立、可能重叠的媒体属性标签体系。

【方法学与计算】
计算分两步。第一步是媒体二分类判据: `_is_market = 媒体(中文).isin(MARKET − OFFICIAL)`, 即先构造两个媒体名单集合 MARKET (来自 NPPA 全国报刊索引数据库, 以主办单位性质为企业/商业集团为判据) 与 OFFICIAL (以主办单位为党政机关/事业单位为判据), 再取差集 MARKET − OFFICIAL 作为「纯市场化」媒体名单。这一差集处理是 2026-06-11 (`fix omni-g-attention-02`) 的一次结构性修正: 早期版本直接用 `isin(MARKET)` 判定市场化虚拟变量, 审计发现 82% 的 MARKET 名单媒体同时也在 OFFICIAL 名单里 (重叠 386 家), 导致 You, Zhang & Zhang (2018) 原本设计为对立构念的「市场化 vs 官方」被这批双重认定媒体的重叠所掩盖、估计有偏。修正后, 双判据媒体 (同时 ∈ OFFICIAL ∩ MARKET) 既不计入 `_is_market==1` 也不计入官方维度的处理组, 而是同时落入两个维度各自的对照组 (`nonmkt` 与 `nonoff`)——即本维度的 `nonmkt` 组实际上是「非纯市场化」的并集 (含官方媒体、双判据媒体、以及既非官方也非市场化的普通商业性/都市类媒体), 并非「纯官方」的镜像。这一披露在维度⑤ (`tone_gap_official_nonoff`) 注释中给出, 本家族继承同一处理。
第二步是三轨条件均值缺口: 对 `['_full','_ctx','_ss']` 依次取源列 `llm_vote_score{track}` (若该轨道列在当期 DataFrame 不存在, 优雅跳过, 不报错、不产出该轨道列——这是三轨设计的通用容错约定, 与 `_ss` 缺列跳轨、`_lg` both-or-neither 等既有先例一致), 按 (target_bank, year) 分组、分别在 `_is_market==1` 子样本与 `_is_market==0` 子样本上取 `llm_vote_score{track}` 均值, 得到 `tone_market_media{track}` 与 `tone_nonmkt_media{track}` 两个中间面板列 (均已在 `export.py` 的列标签映射中登记, 中文含义分别为「市场化媒体平均语调」与「非市场化媒体平均语调」), 再逐轨相减: `tone_gap_market_nonmkt{track} = tone_market_media{track} - tone_nonmkt_media{track}`。若某轨道某 bank-year 单元格任一子均值因样本量为零而缺失 (`panel.get(..., np.nan)` 兜底), 则该轨道该单元格缺口列直接置 NaN, 不做零填充或跨轨插补。
`llm_vote_score{track}` 源自 stage 21 情感 LLM 三家投票共识分 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash` 多数投票), 与嵌入模型无关; full/ctx/ss 三轨的文本口径分别是「标题+全文」/「标题+实体窗口」/「标题+银行∧金科同句±N 窗」, `_ss` 在无银行∧金科同句共现时回退为全文 body (镜像 `_ctx` 语义, `ss_is_fallback=True` 且共享 `n_articles` 分母)。留篇门控口径是 full-only (2026-06-29 起): 一篇报道是否计入「该行的一篇银行-金科报道」只看 `llm_verified_full==True`, ctx/ss 是在该行宇宙 (full 留篇集的子集) 上按各自轨道文本重算的 conditional-on-full 稳健测度, 而非独立样本。三轨各自 just-identified 并排、互为稳健性、不分主次, 三者的估计禁止混进同一 over-identified Hansen J 检验。

【文献定位】
本家族的双差-缺口设计糅合了两支文献。第一支是媒体所有制/独立性文献: You, Zhang & Zhang (2018, RFS) 是本家族最直接的理论锚点, 其核心发现 (市场化媒体的负面报道显著提升高管更替概率, 体现媒体治理功能) 为「市场化 vs 非市场化语调缺口是否显著非零、是否与治理结果相关」提供了可检验的先验假设; Fang & Peress (2009, JF) 建立了媒体覆盖广度与信息不对称、股票回报之间的一般联系, 为「媒体异质性影响资本市场结果」这一更宽泛的机制提供理论背书。第二支是媒体语调测度文献: Tetlock (2007, JF) 是文本语调进入金融实证的奠基性工作 (Harvard-IV 词典法), 本家族虽然测度引擎是 LLM 投票而非词典法, 但「语调均值差异刻画信息环境异质性」这一分析范式与 Tetlock 一脉相承; Holzman, Miller & Twedt (2023, TAR) 进一步区分媒体权威性对语调-市场反应关系的调节作用, 为本项目另设的媒体权威加权轨 (`_mw` 后缀, 与本家族的媒体所有制维度正交、不混用) 提供依据。中国语境下的对应实证见 Fang, Wang, Wang & Yuan (2024, IREF) 与 Xu, Hua & Zhang (2025, EMR): 前者验证媒体语调对中国银行系统性风险与存款稳定性的影响, 后者验证官方媒体语调对中国股市的定价含量, 二者共同支持「媒体所有制/资金来源是中国新闻语境下语调分歧的一阶来源」这一构念假设, 是本家族在中国银行-金科新闻语料上的直接经验依据。

## VAR: tone_gap_market_nonmkt_full

【变体差分】
本列是三轨中的 full 轨, 分子分母口径均取标题+全文 (`content_full`, 即原始「内容」列 prepend 标题) 作为文本输入, 对应 `llm_vote_score_full` 源列, 语调差异不受实体窗口截断或同句共现约束的影响, 覆盖信息量最完整。full 轨同时是 stage 21 情感体系的留篇门控轨: 一篇报道是否计入「该行-该年的一篇银行-金科报道」的判定 (`llm_verified_full==True`) 只看 full 轨, 因此 `tone_market_media_full`/`tone_nonmkt_media_full` 两个子均值所依赖的分母 (市场化/非市场化子样本内 `llm_verified_full==True` 的报道数) 是本家族三轨中唯一直接等于门控留篇集合的口径; ctx/ss 轨道计算的是该留篇集合子集上的条件测度, 因此本列在三轨中承担"主轨/规格锚点"的角色 (但三轨仍是并排、互为稳健性关系, 非层级主次)。当某 bank-year 单元格在市场化或非市场化子样本中任一侧零篇留篇报道时, 对应 `tone_market_media_full` 或 `tone_nonmkt_media_full` 为 NaN, 缺口列相应置 NaN。
实证解读上, full 轨缺口是三条轨道里样本量最大、最不受文本截断影响的一支, 适合作为基线设定汇报; 但这不意味着它在识别策略上优先于 ctx/ss——三轨仍是并排、互为稳健性的关系, 不构成层级主次, 论文行文与回归表汇报须同时呈现三轨或至少声明三轨互证, 不得只保留 full 轨而略去 ctx/ss 作为稳健性附表。full 轨对应的 `_is_market` 判据本身不随轨道变化 (媒体名单是文章元数据层面的属性, 与语调测度所用文本窗口无关), 因此三轨缺口列之间的差异纯粹来自 `llm_vote_score{track}` 语调值本身随文本窗口变化, 而非样本构成 (市场化/非市场化二分类) 的变化——这一点是理解三轨缺口比较意义的关键: 若三轨缺口方向一致, 说明市场化媒体语调更正面/更负面这一结论不依赖于是否纳入报道全文背景; 若方向不一致或幅度显著收窄, 应在稳健性讨论中如实披露。

## VAR: tone_gap_market_nonmkt_ctx

【变体差分】
本列是三轨中的 ctx 轨, 分子分母改取标题+实体窗口 (`content_ctx`, stage 14 `ctx_materializer` 物化) 作为文本输入, 对应 `llm_vote_score_ctx` 源列。行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 即本列的市场化/非市场化子均值只在 `llm_verified_full==True` 的报道范围内、按各自实体窗口文本重新推断语调后聚合, 而非独立留篇。相对 full 轨, ctx 轨剔除了报道中与目标银行、金融科技实体无关的段落, 语调判断更聚焦实体本身周边语境, 因而对「文章通篇基调 vs 实体局部基调不一致」的报道更敏感, 是 full 轨的稳健性对照而非替代——两轨语调缺口若方向一致、幅度接近, 支持媒体所有制效应稳健于文本窗口选择; 若出现系统性偏离, 则提示语调分歧集中在实体窗口之外的篇幅 (如背景铺垫、行业综述段落), 而非目标实体本身的报道立场。与 full 轨同理, 本列的两个子均值分母是各自子样本内非缺失 `llm_vote_score_ctx` 的报道数, 与 full 轨的门控分母不同 (ctx 轨自身若因窗口过窄导致某些报道无法构造出有效 `content_ctx`, 该报道在 ctx 轨天然缺失, 不借用 full 轨分母)。
本列与家族内另一列 `tone_gap_market_nonmkt_ss` 的差异在于窗口构造原语不同: ctx 轨的实体窗口以 `core/text/entity_context.py` 中面向实体本身 (而非句子边界) 的截取逻辑为准, 覆盖范围通常宽于严格的同句共现窗口, 可以跨句、只要求落在实体上下文半径内; ss 轨则要求银行与金融科技词严格同句 (或 ±N 句窗) 共现, 是比 ctx 更窄的子集口径。二者均是「实体聚焦」的稳健化尝试, 但收紧程度不同, 分析时应视作两个独立的稳健性检查点, 而非同一构念的重复计算。与政治词权重梯度、词典消融梯度等既有敏感性设计一致, 三轨 (含本列) 的估计各自 just-identified 并排、互为稳健性, 不应混入同一 over-identified 的 Hansen J 过度识别检验, 也不应在同一回归 RHS 中同时纳入两条以上轨道的缺口列造成共线性膨胀。

## VAR: tone_gap_market_nonmkt_ss

【变体差分】
本列是三轨中的 ss 轨, 分子分母改取标题+银行∧金科同句窗口 (`content_ss`, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句) 作为文本输入, 对应 `llm_vote_score_ss` 源列。ss 轨口径比 ctx 轨更严格: 只保留银行实体与金融科技词汇在同一句 (或邻近 ±N 句窗) 共同出现的语境, 用于捕捉「银行与金融科技被直接并列讨论」时的语调, 剔除报道中泛泛提及银行但与金科话题无关的段落。若某篇报道不存在银行∧金科同句共现, `content_ss` 回退为全文 body (镜像 ctx 轨回退语义), 对应 `ss_is_fallback=True`, 此时该篇报道在 ss 轨的贡献退化为 full 轨口径下的语调, 但仍计入 ss 轨自身的分母 (与 full/ctx 共享 `n_articles` 分母口径); 若目标银行的金融科技识别体系 (`FINTECH_AC`) 整体不可用 (为 None), 则全体报道 `_is_fallback` 置 True, ss 轨优雅降级为等价于 full 轨的宽口径, 而非报错或产出全空列。与 ctx 轨一样, ss 轨的市场化/非市场化子均值行宇宙是 full 轨留篇集合的子集, 且分母不借用其他轨道; ss 轨与 full、ctx 轨三者共同构成互为稳健性、各自 just-identified 的并排测度组, 三者估计禁止混入同一 over-identified Hansen J 设定。
需特别注意 `_is_market` 判据 (媒体是否属于市场化名单) 与三轨文本窗口是两套独立机制: 前者是文章元数据层面的固定属性, 不随 full/ctx/ss 而变化; 后者是语调测度时使用的文本范围。因此本列与 full/ctx 两列的分组结构 (市场化 vs 非市场化子样本的成员构成) 完全一致, 差异只体现在每篇报道贡献的 `llm_vote_score_ss` 数值本身, 以及因回退语义导致的子均值分母是否覆盖到无同句共现的报道。由于回退触发条件 (无银行∧金科同句共现) 与市场化/非市场化身份无关, 回退比例在两个子样本间原则上不应有系统性差异; 若观测到市场化媒体与非市场化媒体的 `ss_is_fallback` 比例显著不同, 应在稳健性讨论中单独说明, 因为这会使 ss 轨缺口混入「回退到全文口径的报道占比不同」这一额外差异来源, 削弱其作为严格同句稳健性检验的解释力。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving Content to Investor Sentiment - The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm - Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk - Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Xu, Z., Hua, X., & Zhang, T. (2025). Does Official Media Sentiment Matter for the Stock Market? Evidence from China. Emerging Markets Review, 64, Article 101234. https://doi.org/10.1016/j.ememar.2024.101234
<!-- rendered-citations:end -->
