---
family_id: F157
columns:
- coh_tfidf_c_ctx
- coh_tfidf_c_full
- coh_tfidf_c_ss
unit: 无量纲余弦相似度 (取值区间 [0,1]; 首年及年份间隙返回 NaN)
formula: "coh_tfidf_c_track_t = cos( v_{bank,t}, v_{bank,t-1} ); v = 银行-年度聚合文本的 TF-IDF char-ngram 向量 (L2 归一化); 仅当 year_t 与 year_{t-1} 为连续年度时定义, 否则 NaN"
producer: news_process/pipeline/features/strategic_diff.py ; news_process/pipeline/panel/export.py
upstream:
- 14_materialize_ctx.parquet (content_full, content_ctx, content_ss)
- 40_panel_yearly.parquet
citations:
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: The Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.48550/arXiv.2004.05150
  type: arxiv
  authors: Beltagy, I., Peters, M. E., & Cohan, A.
  year: 2020
  title: "Longformer: The long-document transformer"
  venue: arXiv
- doi: "10.1016/j.bar.2023.101305"
  type: "journal"
  authors: "Xue, X., Wang, L., & Hu, N."
  year: 2024
  title: "Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China"
  venue: "The British Accounting Review"
  vol: "56"
  issue: "5"
  pages_or_artno: "101305"
- doi: "10.1111/acfi.13076"
  type: "journal"
  authors: "Wang, Y., Ye, Q., Wang, J. J., & Wang, Y."
  year: 2023
  title: "Earnings manipulation and similarity of annual report disclosure: Evidence from China"
  venue: "Accounting & Finance"
  vol: "63"
  issue: "S1"
  pages_or_artno: "1137-1156"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画相邻期文本连贯性 (temporal text coherence), 即同一家银行在连续两个年度里被媒体报道所呈现的语义画像是否稳定。构念取自欧阳志刚与胡雯华 (2024) 对文本连贯性的界定: 把某一主体在年度 t 的全部相关文本聚合成一个词频向量, 与其在年度 t-1 的同类向量做余弦比对, 相似度越高说明该主体的叙事在时间维度上越平稳、越缺乏变动, 相似度越低则说明报道口径、主题焦点或措辞在两年之间发生了明显位移。这一"逐年比对同一主体文本"的思路与 Cohen、Malloy 与 Nguyen (2020) 在顶刊 The Journal of Finance 上提出的 Lazy Prices 度量同源: 该文以连续两期公司披露文件之间的文本相似度作为"信息更新程度"的代理, 发现披露文本相较上一期变动越小 (相似度越高) 的公司未来股价表现越可预测。本家族把同一余弦相似度机理从企业自撰披露迁移到第三方新闻语料上, 因此测量的是"媒体感知的年度间叙事连贯性", 而非企业自我披露的连贯性, 这一口径差异在文献定位与局限一节反复申明。

【方法学与计算】
计算链路分三步。第一步在 stage 14 (ctx_materializer) 物化三条文本轨 content_full / content_ctx / content_ss (均已 prepend_title 把标题拼入正文首句), 再在银行-年度层面把该银行当年命中的全部文章按内容去重后拼接为一份聚合文档 (见 strategic_diff.py 的 _aggregate_bank_year_texts, 同行年内逐字重复默认去重, 以抑制共提及文章带来的机械相似)。第二步对聚合文档做 TF-IDF 字符 n-gram 向量化 (char analyzer, 故家族短名后缀为 _c, 以区别于 jieba 分词的 _w 词级孪生家族), 并对向量做 L2 归一化。第三步取该银行年度 t 与年度 t-1 两份归一化向量的余弦内积作为连贯性得分, 取值落在 [0,1] 区间; 得分对首年 (无 t-1) 及年份间隙 (t 与 t-1 非连续年度) 一律返回 NaN, 该缺失规则与同源的 strat_fluidity 一致, 严格把"相邻期"限定为连续年度而非任意历史年度。字符 n-gram 相比词级切分对未登录词、机构简称与新造金融科技术语更稳健, 无需依赖分词词典, 因而被选为本家族 canonical 轨; jieba 词级 (coh_tfidf_w)、LDA+JSD 主题距离 (coh_lda)、稠密嵌入余弦 (coh_emb 及其 co-primary _lg 孪生) 三条同构念的替代实现构成稳健性梯子。

【文献定位】
本家族在方法学上与三支文献对话。其一是文本相似度作为信息动态代理的金融学脉络, 以 Cohen、Malloy 与 Nguyen (2020) 的 Lazy Prices 为顶刊锚: 二者共享"连续两期同主体文本余弦相似度"这一核心算子, 区别仅在语料是企业自撰披露还是第三方新闻。其二是文本派生变量在建模时须审慎对待其非标准分布这一测度构造规范, Cohn、Liu 与 Wardlaw (2022) 在 Journal of Financial Economics 上系统讨论了由文本机械生成的计数型与类计数型 (count and count-like) 变量的建模陷阱, 其核心告诫是此类变量的数据生成过程内蕴于测量方式本身, 直接套用为其设计外的模型会产生识别偏误。此处须明确构念边界: 本家族的连贯性得分是一个取值有界于 [0,1] 的连续余弦相似度, 并非计数或类计数变量, 故 Cohn、Liu 与 Wardlaw (2022) 针对计数数据提出的具体处方 (如泊松/负二项族、零膨胀模型) 对本家族并不适用, 本家族亦不存在计数意义上的零膨胀。本家族向该文借鉴的仅是其上位的方法学教训, 即凡是由文本机械派生、其取值形态由测量算子而非潜在经济过程直接决定的变量, 在纳入回归时都应正视其分布特征而非默认线性同方差; 落到本家族即须正视余弦相似度的取值有界性 ([0,1] 端点堆积) 及其在相邻期语料量极不均衡时的机械偏斜, 而非照搬计数模型。这一"借上位原则、不借具体处方"的引用口径在此明确申明, 以免读者将本连续相似度误认为计数构念。其三是长文本表征技术, Beltagy、Peters 与 Cohan (2020) 的 Longformer 对超长文档的分段处理思想, 与本家族嵌入替代轨对长文采用 token 分段加均值池化以避免尾部语义被截断的工程选择相呼应。需要强调的是, 本家族三条轨道 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 同理, TF-IDF char 与 jieba 词级、LDA、嵌入四种连贯性实现之间也属规格稳健性并排, 不得跨方法拼入同一过度识别检验。三轨的行宇宙统一遵循 2026-06-29 确立的 full-only 留篇门控: 一篇报道是否计入某银行年度的分母由 full 轨的 llm_verified_full 判定, ctx 与 ss 轨降为 conditional-on-full 的条件测度, ss 轨在无银行与金融科技同句共现时其文本回退镜像 ctx 语义、退化为全文正文并置 ss_is_fallback 为真。 在中文语境的同域先例上, 本家族另可锚定两支证据。Xue、Wang 与 Hu (2024) 以 2009-2021 年中国上市公司为样本, 把当年 CSR 报告与该公司自身以往报告的相似度 (CSR time-series disclosure similarity) 设为被解释变量, 发现经济政策不确定性越高、企业越倾向发布与自身过往高度重合的报告 (象征性行为), 且该效应在国有企业减弱、在财务约束或亏损企业增强; 该文与本家族"同一主体相邻期自比"这一核心算子构念完全对应, 正是把"与自身上期文本高度重合"记录为一种可被外部环境驱动的行为。迁移边界须明写: 原文单位为上市公司-年的自撰 CSR 报告, 本家族为银行-年第三方新闻报道, 银行并非文本作者, 故原文的象征性披露主动选择机制不可直接搬用; 且原文把相似度置于方程左侧、由 EPU 驱动, 本家族三列均作为面板自变量进入右侧, 原文亦为纯时间序列自比、未构造 leave-one-out 同业质心。Wang、Ye、Wang 与 Wang (2023) 在 2008-2020 年中国 A 股 13,679 家样本上以 MD&A 与上一年文本的相似度为核心测度, 记录了"高相似度即低增量信息"的经验规律, 为相邻期词袋相似度在中文语料上的可操作性提供同域佐证; 其边界在于该文发表于 2023 年、语料为公司自撰年报且单位为公司-年, 并把相似度解释为盈余操纵动机, 本家族仅取其测度层含义 (文本重合度可测且承载信息量), 不承接该操纵解释, 亦不因之赋予本连贯性得分任何行为动机含义。
## VAR: coh_tfidf_c_full

【变体差分】
本列是相邻期文本连贯性 TF-IDF 字符 n-gram 实现的 full 轨, 是家族三轨中语料最完整的一条, 也是 full-only 留篇门控的定义轨。其聚合文本 content_full 由标题 prepend 后的全文正文构成, 即把该银行当年每篇经 full 轨核定报道的完整标题与正文并入年度聚合文档, 再做 TF-IDF char 向量化与年度间余弦比对。相较 ctx 轨仅取银行实体窗口、ss 轨仅取银行与金融科技同句窗口, full 轨纳入最多背景文本, 因而其连贯性得分反映的是媒体对该银行整体叙事 (含宏观、监管、经营各类语境) 的年度稳定性, 灵敏度更钝但覆盖更全。作为门控轨, full 轨的留篇判定 (llm_verified_full) 决定了三轨共享的银行-年度行宇宙, ctx 与 ss 轨只能在 full 留篇集的子集上取值。本列与 ctx / ss 两轨各自 just-identified 并排、互为稳健性且不分主次, 三者禁混进同一 over-identified Hansen J; 与其字符对应的 jieba 词级列 coh_tfidf_w_full、主题距离列 coh_lda_full 及嵌入列 coh_emb_full (含 _lg 孪生) 同属跨方法稳健性梯子, 亦不得跨方法并入同一过度识别检验。字符 n-gram 相较词级切分不依赖分词词典, 对银行机构简称、监管术语与新造金融科技词汇的拼写变体更稳健, 这正是 full 轨采用字符实现作为 canonical 的理由; 词级实现 coh_tfidf_w_full 作为分词口径的平行稳健性臂保留。该列对银行首个观测年度及非连续年度间隙返回 NaN, 与 strat_fluidity 的缺失规则严格一致, 不以任意历史年度回填。

## VAR: coh_tfidf_c_ctx

【变体差分】
本列是相邻期文本连贯性 TF-IDF 字符 n-gram 实现的 ctx (上下文窗口) 轨。其聚合文本 content_ctx 不取全文, 而是取以银行实体为中心的上下文窗口文本 (标题已 prepend, 银行侧判定采用否定加短名过滤口径), 再在银行-年度层面拼接、TF-IDF char 向量化并做年度间余弦比对。相较 full 轨纳入全部背景语境, ctx 轨把语料收窄到围绕目标银行实体的邻近文字, 因此其连贯性得分更专注于"针对该银行本身的叙述"是否年度稳定, 剔除了与该行无直接关涉的宏观或行业背景噪声, 对该行 bank-specific 报道口径的年度位移更敏感。ctx 轨是 conditional-on-full 的条件测度: 其行宇宙是 full 轨留篇集的子集, 门控仍由 full 轨 llm_verified_full 决定, ctx 轨本身不独立定义留篇。本列与 full / ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混进同一 over-identified Hansen J; 与 coh_tfidf_w_ctx、coh_lda_ctx、coh_emb_ctx 等跨方法实现同属稳健性梯子, 不跨方法并入同一过度识别检验。相比 full 轨纳入全部背景语境, ctx 轨对该行专属报道口径的年度位移更敏感, 因而在稳健性梯子中扮演"收窄语料后主结论是否仍成立"的检验角色; 由于 ctx 文本为 bank-specific 实体窗口, 跨银行逐字共享天然弱, 其连贯性得分较少受共提及文章机械相似的污染。该列对首年及年份间隙返回 NaN。

## VAR: coh_tfidf_c_ss

【变体差分】
本列是相邻期文本连贯性 TF-IDF 字符 n-gram 实现的 ss (同句共现窗口) 轨, 是三轨中语料判据最严的一条。其聚合文本 content_ss 取标题加"银行与金融科技同句共现正负 N 句窗"内的文字 (窗宽由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1; 银行侧走否定加短名过滤, 金融科技侧走裸 AC 词表匹配), 再拼接、TF-IDF char 向量化并做年度间余弦比对。因判据最严, ss 轨得分刻画的是"银行与金融科技直接共现语境"的年度叙事连贯性, 最贴近本项目金融科技主构念。关键回退语义: 当某篇报道无银行与金融科技的同句共现时, content_ss 回退镜像 ctx 语义, 退化为全文正文并置 ss_is_fallback 为真, 分母仍与三轨共享 n_articles, 属优雅降级而非静默丢样; 若上游 FINTECH_AC 为 None 则整批 _is_fallback 置真。ss 轨同为 conditional-on-full 的条件测度, 行宇宙受 full 轨门控约束。本列与 full / ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与 coh_tfidf_w_ss、coh_lda_ss、coh_emb_ss 跨方法实现同属稳健性梯子。该列对首年及年份间隙返回 NaN, 在 T=2 试跑盘上因样本极浅可能呈退化取值, 属预期。需特别区分本 ss 轨的同句共现判据 (银行与金融科技同句) 与家族外网络指标的银行∧银行判据: 二者原语不同、口径互斥, 不得相互复用。该列在稳健性梯子中承担"仅保留金融科技直接语境后连贯性主结论是否稳健"的最严检验角色, 与 full / ctx 两轨的对比构成语料判据由宽到严的三级谱系。

<!-- rendered-citations:begin -->
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Beltagy, I., Peters, M. E., & Cohan, A. (2020). Longformer: The long-document transformer. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2004.05150
Xue, X., Wang, L., & Hu, N. (2024). Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China. The British Accounting Review, 56(5), 101305. https://doi.org/10.1016/j.bar.2023.101305
Wang, Y., Ye, Q., Wang, J. J., & Wang, Y. (2023). Earnings manipulation and similarity of annual report disclosure: Evidence from China. Accounting & Finance, 63(S1), 1137-1156. https://doi.org/10.1111/acfi.13076
<!-- rendered-citations:end -->
