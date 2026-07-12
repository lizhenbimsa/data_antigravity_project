---
family_id: F073
columns:
- avg_word_count_ctx
- avg_word_count_full
- avg_word_count_ss
unit: 词数 (jieba 分词计数, 无量纲整数经 bank-year 均值化为 double)
formula: "avg_word_count{track} = mean_over_articles( n_words_real{track} ); n_words_real = 单篇 jieba 实词分词数 (track ∈ {_full, _ctx, _ss}); 下游 geography.py 再取 ln(1+·) → ln_word_count{track}"
producer: news_process/pipeline/panel/encode.py (H2 词汇/句法复杂度聚合段, agg 字典) ; news_process/pipeline/panel/geography.py (下游 ln 变换消费者)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本 + *_is_fallback)
- 22_tone_words.parquet (article-level n_words_real{track} 词数中间列)
citations:
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.1016/j.jacceco.2020.101344
  type: journal
  authors: Blankespoor, E., deHaan, E., & Marinovic, I.
  year: 2020
  title: "Disclosure processing costs, investors' information choice, and equity market outcomes: A review"
  venue: Journal of Accounting and Economics
  vol: 70
  issue: 2-3
  pages_or_artno: 101344
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1016/j.jacceco.2015.09.002
  type: journal
  authors: Lang, M., & Stice-Lawrence, L.
  year: 2015
  title: "Textual analysis and international financial reporting: Large sample evidence"
  venue: Journal of Accounting and Economics
  vol: 60
  issue: 2-3
  pages_or_artno: 110-135
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: "Financial reporting complexity and investor underreaction to 10-K information"
  venue: Review of Accounting Studies
  vol: 14
  issue: 4
  pages_or_artno: 559-586
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"银行相关金融科技报道的篇均词级长度"这一文本体量构念。对某一银行在某一年度内被判为相关的每一篇报道, 先用 jieba 分词器 (冻结版本 0.42.1) 切出实词序列并计其词数 n_words_real, 再在 bank-year 单元内对这些逐篇词数取算术平均, 得到 avg_word_count。构念定位是"平均一篇报道有多长", 而非"一年有多少篇报道"——后者是篇数计数 (n_articles) 的领域, 与本家族正交。因此单位是词数 (一个非负整数经均值化后落为 double), 不是篇数。原始 frontmatter 曾初判单位为"篇数/计数", 经对 encode.py 源码逐条校对后修正为词级长度, 这一点必须清晰: 分母是"篇", 被平均的量是"每篇的词数"。文本长度之所以进入面板, 是因为在会计与金融的文本分析传统里, 篇幅是信息含量、信息处理成本与可读性的一阶代理: 更长的披露往往携带更多硬信息, 但也抬高读者的处理成本并可能稀释信号。Li (2008) 以年报的词级篇幅 (MLENGTH) 作为可读性与信息复杂度的基准代理, 确立了"长度即处理负担"的经验范式; Blankespoor, deHaan 与 Marinovic (2020) 系统综述了披露处理成本如何经由篇幅、复杂度进入投资者的信息选择与市场结果, 为本长度族提供了机制层面的理论锚。

【方法学与计算】
计算链路分两层。第一层在文章级 (上游 22_tone_words 阶段附近物化): 对三轨文本 content_full / content_ctx / content_ss 各自跑 jieba 分词, 数出实词数得到 n_words_real_full / _ctx / _ss。第二层在面板聚合 (encode.py 的 H2 词汇/句法复杂度批段): agg[f'avg_word_count{track}'] = (f'n_words_real{track}', 'mean'), 即对每个 bank-year 单元内所有留篇报道的逐篇词数取 pandas mean。mean 聚合会自动跳过 NaN, 使得短文或空文本不污染均值。此长度是"词口径"长度, 与并存的另两种口径刻意区分: 字符口径 avg_article_length = ln(1+平均字符数) (底层 doc_length = len(str(内容)) 是 Unicode 字符数, 非词数, 2026-06-05 已勘误其单位标注); 汉字口径 avg_han_count / ln_han_count = 剔除数字标点拉丁后的 CJK 汉字计数均值。三口径 (字符 / 词 / 汉字) 兑现"既要汉字也要字符"的诉求, 互为长度稳健性、不分主次, 各自 just-identified 并排进入自回归, 禁混进同一 over-identified Hansen J。下游 geography.py 对本家族三列做 ln(1+·) 变换生成 ln_word_count{track}, 即真正的词口径 MLENGTH (Li 2008), 与字符口径的 avg_article_length 互为长度稳健轨; 缺列 (ss 未落盘) 时以 if 守卫优雅跳过, 不硬崩。就其计数本性而言, Cohn, Liu 与 Wardlaw (2022) 提醒: 金融中的计数与类计数变量 (词数、篇数皆属此列) 具有右偏、非负、方差随均值增长的特征, 直接线性回归易偏, 故下游一律以 ln(1+·) 稳定其分布——这正是 geography.py 对本家族施加对数变换而非直接使用原始词数的方法学依据。

【文献定位】
词级长度作为文本复杂度与可读性代理, 其学术脉络清晰。You 与 Zhang (2009) 在 Review of Accounting Studies 上证明报告复杂度 (以篇幅与词汇为核心成分) 系统性放大投资者对 10-K 信息的欠反应, 确立篇幅的经济后果; Bonsall, Leone, Miller 与 Rennekamp (2017) 进一步用 Bog Index 等 plain-English 度量把可读性从单纯长度扩展到句法层, 表明长度是复杂度的必要但不充分成分, 因而本家族的词长与家族外的句法/词汇难度族 (rare_word / hard_char / nominalization) 互补而非替代。Lang 与 Stice-Lawrence (2015) 在大样本国际财报语境中系统化了文本长度、boilerplate 与信息量的关系, 为本长度族提供跨语境外部效度。三轨 (full / ctx / ss) 是本项目对同一长度构念在三种文本切分口径下的并排测量: full 为标题 prepend + 全文正文的完整篇幅, 是留篇门控 (full-only, 2026-06-29) 与 canonical 主轨; ctx 收窄到实体上下文窗, ss 进一步收窄到银行与金科同句共现窗。三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。ss 轨的回退语义镜像 ctx: 当某篇无银行∧金科同句共现时, content_ss 退回全文 body 且 ss_is_fallback=True, 与 ctx 共享 n_articles 分母口径。

## VAR: avg_word_count_full

【变体差分】
本列是家族 canonical 主轨, 也是三轨中唯一进入留篇门控口径的长度测量。full 轨文本 = content_full = 标题 prepend 到全文正文, 覆盖一篇报道的完整篇幅, 因而 avg_word_count_full 反映的是"一篇银行金科报道从标题到正文一共有多少 jieba 实词"的完整体量。之所以 full 是 canonical, 是因为 2026-06-29 起留篇门控收敛为 full-only: 一篇是否被判为"银行金科相关报道"只看 llm_verified_full == True, 故 full 轨的 bank-year 行宇宙即完整留篇集, 其词数均值是分母口径最稳、样本最全的长度基线。计算上, encode.py 对该 bank-year 单元内所有 full-verified 报道的逐篇 n_words_real_full 取 mean (自动跳 NaN); 下游 geography.py 以 ln(1+avg_word_count_full) 产 ln_word_count_full, 即真词口径 MLENGTH (Li 2008), 与字符口径 avg_article_length、汉字口径 ln_han_count 互为长度稳健。相对 ctx / ss 两个收窄轨, 本列的差分点是文本范围最宽 (整篇)、门控最严 (full-only 决定留篇)、样本最全, 三者共同使其成为长度族回归的默认自变量。在与外部财务哨兵列 (如资金成本、金科投资、成本收入比) 做回归时, 研究者默认取本 full 列或其对数变换 ln_word_count_full 作为篇幅控制或代理; 之所以优先 full 而非 ctx / ss, 是因为完整篇幅在小样本上方差更充分、缺失更少, 收窄轨在稀疏共现下易退化。需要强调本列度量的是"长度"而非"情感"或"内容": 它与家族外的极性族 (llm_vote_tone / dict tone)、内容维度族 (substance / locus / collab) 正交, 只回答"有多长"这一体量问题, 却常作为它们的必要控制变量, 因为篇幅长短会机械地放大或稀释其它逐词密度型测度。与 ctx / ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁三轨混进同一 over-identified Hansen J。

## VAR: avg_word_count_ctx

【变体差分】
本列是 ctx 轨长度测量, 相对 canonical 的 full 轨其唯一差分是底层文本口径: content_ctx = 标题 prepend + 实体上下文窗 (围绕目标银行实体命中位置的邻近窗口文本), 而非整篇正文。因此 avg_word_count_ctx 度量的是"聚焦到银行实体上下文那一段, 篇均有多少 jieba 词", 系统性地短于 full 轨——它剔除了与目标银行无关的远端段落, 只保留实体周边语境。这一收窄使 ctx 轨在构念上更贴近"针对该银行的那部分报道有多长", 是对 full 轨"整篇多长"的 conditional-on-full 稳健性补充: ctx 轨行宇宙是 full 留篇集的子集, per-track 词数照算。计算同 encode.py H2 段的 mean 聚合, 对 n_words_real_ctx 逐篇取均值; 下游 ln_word_count_ctx 由 geography.py 以 ln(1+·) 产出, 缺列时 if 守卫优雅跳过。方法学上, ctx 与 full 的长度差本身携带信息 (报道有多少篇幅真正围绕该银行), 呼应 Bonsall 等 (2017) 关于"信息定位"影响可读性感知的观点。本列与 full / ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁三轨混进同一 over-identified Hansen J; 在 dev T=2 小样本上 ctx 轨可能出现零方差退化, 属预期, 不代表列失效。使用建议: 当研究关注"针对该银行的报道体量"而非"泛泛提及该银行的整篇报道体量"时, ctx 轨更贴合识别意图; 而在稳健性检验里, full 与 ctx 词长的相对高低本身即可作为"报道聚焦度"的间接线索——若两者接近, 说明报道通篇围绕该银行, 若 ctx 远短于 full, 说明银行只是长文中的一小段。本列与 full 共享同一 jieba 冻结词典与同一 mean 聚合逻辑, 唯一分野在 content_ctx 的文本切分, 故任何 full 与 ctx 的数值差纯粹源于文本范围而非算法差异, 这一干净的差分设计使两轨之差可解释、可审计。

## VAR: avg_word_count_ss

【变体差分】
本列是 ss (same-sentence) 轨长度测量, 相对 full canonical 的差分是最激进的文本收窄: content_ss = 标题 prepend + 银行∧金科同句共现窗 (config/filtering.yaml::context_window.ss_sentence_radius, 默认 ±1 句), 只保留目标银行与金融科技词在同一句 (及邻近 ±N 句) 共现的那一小段文本。因此 avg_word_count_ss 度量的是"在银行与金科真正同句挂钩的那几句里, 篇均有多少 jieba 词", 是三轨中文本范围最窄的长度口径。其关键的回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 优雅退回全文 body 且 ss_is_fallback=True, 并与 ctx 共享 n_articles 分母口径; 若 FINTECH_AC=None (金科词表缺失) 则 ss_is_fallback 全 True 整体降级为全文长度。计算同 encode.py H2 段对 n_words_real_ss 取 bank-year mean, 下游 ln_word_count_ss 由 geography.py 产出, 缺列 if 守卫跳过。ss 轨长度捕捉"银行金科关系被明确表述的语境有多长", 是对 full / ctx 的 conditional 稳健性极端轨, 行宇宙是 full 留篇集子集。本列与 full / ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁三轨混进同一 over-identified Hansen J; dev T=2 上因大量回退与共现稀疏, ss 轨可能近零方差退化, 属预期, 生产 T=18 上正常。使用时须格外注意回退带来的口径混合: 因非共现篇退回全文, ss 词长在回退比例高的 bank-year 上会向 full 词长收敛, 故解释 ss 轨长度须联合 ss_is_fallback 的占比一并看, 单看 avg_word_count_ss 而忽略回退率可能误判"同句语境很长"。本列与 full / ctx 共用同一 jieba 冻结词典和同一 mean 聚合, 唯一分野在最窄的同句共现文本切分, 因此它承载的是三轨中信噪比最高但样本最脆的长度信号, 定位为极端稳健性轨而非主轨; 与 full / ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁三轨混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Blankespoor, E., deHaan, E., & Marinovic, I. (2020). Disclosure processing costs, investors' information choice, and equity market outcomes: A review. Journal of Accounting and Economics, 70(2-3), 101344. https://doi.org/10.1016/j.jacceco.2020.101344
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Lang, M., & Stice-Lawrence, L. (2015). Textual analysis and international financial reporting: Large sample evidence. Journal of Accounting and Economics, 60(2-3), 110-135. https://doi.org/10.1016/j.jacceco.2015.09.002
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
<!-- rendered-citations:end -->
