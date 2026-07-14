---
family_id: F583
columns:
- tone_local_media_ctx
- tone_local_media_full
- tone_local_media_ss
unit: 语调得分 (连续, 约 [-1,1]; 三家 LLM 多数投票 llm_vote_score 逐篇均值聚合至 bank-year)
formula: "tone_local_media{track} = mean(llm_vote_score{track}) over 目标银行为 b、年份为 y 且 _is_central 取 0 (即非中央媒体) 的文章集合; _is_central 判据 = 媒体(中文) ∈ CENTRAL 名单 (行政层级分类, 与财经/综合、官方/市场化、深度/高频三条媒体异质性维度正交)"
producer: pipeline/panel/attention_media.py::compute_media_heterogeneity (中央/地方情感均值+缺口块) ; 列标签渲染于 pipeline/panel/export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss)
- 14_materialize_ctx.parquet (content_full/content_ctx/content_ss)
- config/bank_list.yaml (target_bank 实体匹配)
citations:
  - doi: 10.1111/1911-3846.13049
    type: journal
    authors: Kang, B. U., & Nam, J. S.
    year: 2025
    title: "Do local newspapers matter to institutional investors?"
    venue: Contemporary Accounting Research
    vol: 42
    issue: 3
    pages_or_artno: 1713-1743
  - doi: 10.1016/j.jfineco.2021.08.015
    type: journal
    authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
    year: 2022
    title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
    venue: Journal of Financial Economics
    vol: 145
    issue: 2
    pages_or_artno: 445-463
  - doi: 10.1093/rfs/hhx055
    type: journal
    authors: You, J., Zhang, B., & Zhang, L.
    year: 2018
    title: "Who captures the power of the pen?"
    venue: Review of Financial Studies
    vol: 31
    issue: 1
    pages_or_artno: 43-96
  - doi: 10.1111/j.1540-6261.2012.01725.x
    type: journal
    authors: Gurun, U. G., & Butler, A. W.
    year: 2012
    title: "Don't believe the hype: Local media slant, local advertising, and firm value"
    venue: Journal of Finance
    vol: 67
    issue: 2
    pages_or_artno: 561-598
  - doi: 10.1111/j.1540-6261.2007.01232.x
    type: journal
    authors: Tetlock, P. C.
    year: 2007
    title: "Giving content to investor sentiment: The role of media in the stock market"
    venue: Journal of Finance
    vol: 62
    issue: 3
    pages_or_artno: 1139-1168
  - doi: 10.1016/j.iref.2024.01.067
    type: journal
    authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
    year: 2024
    title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
    venue: International Review of Economics & Finance
    vol: 91
    pages_or_artno: 1150-1172
new_dois: []
---

## CORE

【构念与来源】
本家族刻画"地方级媒体"在报道目标银行金融科技相关新闻时的平均语气 (tone), 是媒体异质性四条正交维度之一 (财经/综合类型、中央/地方行政层级、官方/市场化取向、深度/高频发刊频率) 中"中央 vs 地方"这一维度的地方端产出。构念动机来自媒体政治经济学文献: 中国新闻出版行业存在明确的行政层级体系, 中央级媒体 (如人民日报、新华社、中央电视台系媒体) 在采编上受更强的宣传纪律约束, 而地方级媒体 (省市党报、都市报、地方财经媒体等) 虽同受主管单位制度约束, 但在报道口径、时效性、对本地企业 (含地方法人银行、城商行、农商行) 的关注密度与语气取向上, 与中央级媒体存在系统性差异。You, Zhang & Zhang (2018, *Review of Financial Studies*) 的"谁执笔杆子"研究表明, 媒体的所有制与层级结构显著影响其报道对公司治理事件的敏感度和语气倾向, 为本维度的构念效度提供了直接的实证支撑——地方语气与中央语气分离计量, 使研究者可以检验行政层级是否是驱动报道语气差异的独立渠道, 而非仅仅是财经属性或市场化程度的代理。

数据来源上, 分类判据 `_is_central` 由 `attention_media.py` 依据媒体名称字段"媒体(中文)"是否命中预先构造的 CENTRAL 名单集合决定 (二值哑变量, 1=中央级、0=地方级), 与本家族对应的 `tone_local_media{track}` 恰是 `_is_central==0` 子样本上的语气均值。该分类与财经/综合 (fin_media_frac 等)、官方/市场化 (official_media_frac/market_media_frac, 基于 NPPA 主管单位/主办单位双判据, 2026-06-11 修正为互斥构造 official := OFF − MKT)、深度/高频 (deepdive_media_frac/daily_media_frac) 三条维度分别独立构造, 彼此正交、互不嵌套——一篇地方级报道可以同时是财经类、市场化的, 也可以同时是官方的、综合类的, 四条维度分别从各自子样本聚合语气均值, 不做交叉分层。

【方法学与计算】
语气原始信号来自 stage 21 三家大语言模型 (`gpt-5.4-nano`/gpt54nano、`gemini-3.1-flash-lite`/gemini31 经 yunwu 中转、`deepseek-v4-flash`/deepseekv4 直连 api.deepseek.com) 对每篇文章的多数投票语气得分 `llm_vote_score{track}` (逐轨道产出, track ∈ {_full, _ctx, _ss})——三家模型互为跨厂商稳健性, 不设加权主次。计算逻辑在 `attention_media.py` 中对 `_is_central==0` 的子样本按 `(target_bank, year)` 分组取 `llm_vote_score{track}` 均值, 三轨道各自独立跑一遍循环 (`for track in ['_full', '_ctx', '_ss']`), 若某轨道的语气源列在当期数据框中不存在则优雅跳过该轨道 (不报错、不补空列), 这是全仓一致的三轨"缺列跳轨"防御性写法。与之配对的 `tone_central_media{track}` (中央级语气均值) 以及派生的 `tone_gap_central_local{track}` (中央减地方之差) 属邻近但不同的家族/列, 本家族只覆盖地方一侧的水平值。

需要特别澄清的是留篇门控口径 (2026-06-29 生效): stage 21 判定"某篇报道是否被计入一篇有效的银行×金科报道"只看 full 轨道的 `llm_verified_full==True`, 这是唯一的门控开关。ctx 与 ss 两轨道的行宇宙是 full 轨道留篇集合的子集 (conditional-on-full), 各轨道语气值在该子集内各自独立计算, 不存在"ctx 单独放宽门槛多留几篇"的情况。三轨道之间各自 just-identified 并排、互为稳健性、不分主次, 是同一构念 (地方媒体报道语气) 在不同文本窗口下的三种测量口径, 禁止把三轨的地方语气变量混入同一个 over-identified 的 Hansen J 检验方程——每个轨道应各自作为独立的处理变量或工具变量进入回归, 而不是三者叠加过度识别同一内生变量。

语气得分本身的构念含义也需要澄清: PROJECT_REAUDIT_TOPTIER_T18 (2026-06-14) 复核发现验证篇的分布高度偏向正面 (正 798 / 中 33 / 负 2, 负面占比仅约 0.24%), 名义上的双极量表 [-1,1] 在实证分布上更接近单极的"正向强度/乐观度"(favorability/optimism) 而非真正的双极情感, 这一点在 `llm_vote_tone_full` 等主轨列的 dta 标签中已显式披露 ("neg degenerate")。`tone_local_media{track}` 由同一 `llm_vote_score` 聚合而来, 继承相同的分布特征——研究者在解读地方媒体语气高低时, 应理解其经验含义更接近"地方媒体对该银行金科业务的正面/乐观报道密度", 而非严格意义上的正负对称情感强度。

【文献定位】
本家族的构念传承自媒体经济学两条互补脉络。第一条脉络关注"地方性"作为媒体报道行为的独立解释变量: Gurun & Butler (2012, *Journal of Finance*) 发现本地媒体的报道倾向 (slant) 与本地广告收入存在系统性关联, 影响本地企业的融资成本与估值, 说明地方媒体并非中央媒体的缩小版复制, 而具有自身独立的经济激励结构; Heese, Pérez-Cavazos & Peter (2022, *Journal of Financial Economics*) 利用美国地方报纸停刊这一准自然实验, 证明地方新闻业的存在本身对企业不当行为具有威慑效应, 佐证了地方媒体监督职能与中央媒体不可替代。第二条脉络聚焦中国情境下媒体的科层结构与政治经济学: You, Zhang & Zhang (2018, *Review of Financial Studies*) 系统刻画了媒体所有制/层级对报道语气与治理效应的调节作用, 是本维度"中央/地方"二分类构造的直接理论来源; Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 将媒体情感度量应用于中国银行体系, 检验其对存款稳定性与系统性风险的影响, 与本项目"银行×媒体语气"面板设定高度同域, 提供了方法论上的对照基准。语气测量本身的技术谱系上溯至 Tetlock (2007, *Journal of Finance*) 关于媒体内容如何赋予投资者情绪以可度量含义的开创性框架——本项目以三家 LLM 多数投票取代其词典打分法, 但"从文本抽取语气信号并聚合到实体-期间面板"的基本方法论骨架一脉相承。

## VAR: tone_local_media_ctx

【变体差分】
本列是家族 canonical 语气度量在 ctx (entity-context) 文本窗口下的地方级媒体语气均值。ctx 轨道的底层文本 `content_ctx` 在 stage 14 `materialize_ctx` 阶段物化, 定义为"标题 + 目标银行实体窗口"截取的正文片段 (`prepend_title` 拼接约定, 与 full 轨道的"标题 + 全文正文"不同, 也与 ss 轨道的"标题 + 银行∧金科同句±N 窗"不同)。三轨文本互不覆盖, 是对同一篇文章语气构念的三种不同文本粒度测量。

ctx 轨道语气值的计算路径与 canonical full 轨道完全平行: 取 stage 21 三家 LLM 多数投票在 ctx 窗口下产出的 `llm_vote_score_ctx`, 在 `_is_central==0` 的地方级媒体子样本上按 (target_bank, year) 分组求均值。行宇宙受 2026-06-29 生效的 full-only 留篇门控约束——是否计入某篇报道, 仍只看该篇 `llm_verified_full` 是否为真; ctx 轨道不单独放宽或收紧这一门槛, 因此 ctx 语气均值的样本篇数与 full 轨道逐篇一一对应 (同一分母下的不同文本窗口测量), 不会出现 ctx 纳入了 full 未纳入的边际篇目的情况。

ctx 与 full、ss 三轨道之间是互为稳健性、不分主次的并排关系, 不存在"ctx 是主指标 full 是稳健性检验"或反之的先验排序——三者对应实体窗口聚焦程度递增/递减的三种文本截取策略, 各自反映"地方媒体语气"构念的不同侧面 (ctx 更聚焦于银行实体紧邻上下文的措辞, 排除掉全文中与该银行关系较远段落的语气干扰; full 保留全文语境包括可能稀释或放大语气的周边段落)。在回归设计中应将三者分别作为独立的解释变量或稳健性检验, 绝不可将 full/ctx/ss 三条地方媒体语气序列同时塞入同一个 over-identified 的 Hansen J 过度识别检验方程, 这会人为制造工具冗余并破坏识别假设的可解释性。此外 ctx 轨道本身没有独立的回退语义 (回退语义是 ss 轨道相对 ctx 的镜像设计, 详见 tone_local_media_ss 一节), ctx 若源列 `llm_vote_score_ctx` 在当期数据中缺失, `attention_media.py` 的构造循环会优雅跳过该轨道, 使 `tone_local_media_ctx` 及其对应的 `tone_gap_central_local_ctx` 整体不产出而非填充误导性的默认值。

## VAR: tone_local_media_full

【变体差分】
本列是家族的 canonical/主口径地方级媒体语气度量, 使用 full 轨道文本 (`content_full` = 标题 prepend + 全文正文, stage 14 `materialize_ctx` 物化) 对应的 `llm_vote_score_full` 作为语气源信号。这是三轨中留篇门控的锚定轨道: 2026-06-29 生效的 full-only 口径规定, 一篇报道是否被认定为"一篇有效的银行×金科报道"完全由 `llm_verified_full==True` 决定, 与 ctx/ss 轨道的验证结果无关。因此 `tone_local_media_full` 所依赖的样本行宇宙就是该门控本身筛选出的行集合, 是三条轨道中样本口径最"原生"的一条, 也是 P1 主论文 (`bank_fintech_tone`) treatment 主轨 (`llm_vote_tone_full`) 所在的同一文本窗口族。

具体计算上, `attention_media.py` 在地方级 (`_is_central==0`) 子样本上按 (target_bank, year) 分组对 `llm_vote_score_full` 取均值, 得到该银行-年度地方媒体报道的平均语气水平。与之配对产出的还有 `tone_central_media_full` (中央级语气均值) 与 `tone_gap_central_local_full` (中央减地方之差, 用以刻画行政层级语气落差的方向与幅度), 三者共同构成中央/地方这一媒体异质性维度在 full 轨道下的完整刻画; 本列只覆盖其中地方一侧的水平值本身。

即便是 canonical 轨道, `tone_local_media_full` 与 ctx、ss 两个姊妹列之间仍然是并排的互为稳健性关系, 不构成主从——"canonical" 仅指该列对应 P1 主论文 treatment 所在的文本窗口惯例, 并不意味着 full 轨道在方法论上优于 ctx/ss。三轨语气序列应各自独立地进入识别策略 (作为处理变量或工具变量), 禁止将三者同时纳入同一个过度识别的 Hansen J 检验, 以避免虚假的 over-identification 与工具冗余问题混淆推断。此外需重申语气得分的分布特征: 验证篇分布高度偏向正面 (负面占比约 0.24%), `tone_local_media_full` 的经验含义更接近"地方媒体对该银行金科业务的正面强度均值", 在跨银行、跨年度比较时应关注均值的相对高低而非将其视为严格双极对称的情感量表读数。

## VAR: tone_local_media_ss

【变体差分】
本列是家族在 ss (same-sentence) 文本窗口下的地方级媒体语气均值, 底层文本 `content_ss` 由 stage 14 `materialize_ctx` 物化, 判据为"标题 + 目标银行与金融科技词同句共现 (±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1)"截取的片段——这是三轨中文本粒度最窄、聚焦度最高的一条, 严格要求银行实体与金科词汇在同一句 (或紧邻句窗) 内共同出现, 判定不对称口径为银行侧套用否定词过滤+短名过滤、金科侧套用裸 AC 自动机 1506 词表匹配。

ss 轨道的回退语义镜像 ctx 轨道的设计原则: 当某篇报道中不存在银行∧金科同句共现时 (即找不到满足 ss 判据的句子窗口), `content_ss` 退化为全文 body (与 full 轨道文本一致), 对应的 `ss_is_fallback` 标记列置为 True; 若上游 `FINTECH_AC` 词表自动机为 None (罕见的配置缺失场景), 则该批次全部 `*_is_fallback` 优雅降级为 True。回退发生的篇目共享同一个 `n_articles` 分母, 不会因回退而在计数口径上产生偏差——`tone_local_media_ss` 的聚合分母与 ctx/full 两轨在样本篇数层面保持一致 (均受 full-only 留篇门控约束), 只是部分篇目在回退情形下实际消费的是与 full 相同的全文文本而非严格同句片段。

`attention_media.py` 中该列的构造循环对 `llm_vote_score_ss` 源列做存在性检查 (`if src not in df.columns: continue`), 若上游 stage 21 未产出 ss 轨道语气列 (例如某次运行 `FINTECH_AC` 缺失导致 ss 轨道整体退化为 full 的镜像), 则 `tone_local_media_ss` 及其配对的 `tone_gap_central_local_ss` 整体不产出, 而非填充零值或 NaN 占位——这是与 ctx 轨道完全一致的"缺列跳轨"防御写法, 避免下游面板出现语义模糊的伪空列。

在识别策略与稳健性叙事上, ss 轨道与 full、ctx 三者各自 just-identified 并排、互为稳健性、不分主次——ss 提供的是"语境最贴近的严格共现"证据, 用以排除同一篇报道中银行与金科话题被文章其他部分的无关段落稀释语气信号的可能性; 当研究结论在 full/ctx/ss 三条轨道下方向一致、显著性稳健时, 才能对"地方媒体语气"这一构念的经验发现建立更高的信心。同样禁止将 full/ctx/ss 三条地方语气序列混入同一个 over-identified 的 Hansen J 检验——三轨应始终作为并列的稳健性检验组, 而非叠加的工具变量集合去过度识别单一内生解释变量。

<!-- rendered-citations:begin -->
Kang, B. U., & Nam, J. S. (2025). Do local newspapers matter to institutional investors?. Contemporary Accounting Research, 42(3), 1713-1743. https://doi.org/10.1111/1911-3846.13049
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
