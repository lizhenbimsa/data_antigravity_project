---
family_id: F124
columns:
- bian_2021_idf_score_mw_sum_ctx
- bian_2021_idf_score_mw_sum_full
- bian_2021_idf_score_mw_sum_ss
unit: 无量纲情感得分的银行-年合计 (媒体权威度加权 × IDF 词项加权的篇级情感得分逐篇求和; 归一化 IDF 使量级与等权版可比)
formula: "bian_2021_idf_score_mw_sum{track} = Σ_i ( bian_2021_idf_score_i{track} × mw_i ); mw_i = media_authority_weight (raw_weight / mean(raw_weight)); bian_2021_idf_score = 归一化( Σ_w idf(w)·polarity_bian(w) ), idf(w) = Winsorize( log10(N/(1+df(w))) / mean(log10(N/(1+df(w)))), P1, P99 )"
producer: news_process/pipeline/sentiment/tone_words.py (篇级 bian_2021_idf_score 计算 + build_idf_weights) ; news_process/pipeline/panel/runner.py (步骤 3c/3d 媒体权威度加权 _mw 篇级列) ; news_process/pipeline/panel/encode.py (Bank-Year 求和 _mw_sum 聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_idf_score{track})
- config/media_weights.json (媒体权威度评分)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"以 Bian 等 (2021) 中文金融情感词典为极性来源、经 IDF 词项加权后、再按媒体权威度加权的银行-年情感得分合计"。构念上它属于词典法情感测度族中的一个稳健性变体, 而非主测度。基础极性来自 Bian 等 (2021) 构建的中文财经文本情感词典 (SSRN 3446388): 该词典面向会计与金融领域的中文语料, 区分正面与负面情感词, 是本项目并行装载的六部情感词典之一 (jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 / loughran)。选用多部词典而非单一词典, 目的正是让不同来源、不同构建方法的词典各自算出一套语调, 彼此互为稳健性、不分主次, 以证明主结论不依赖某一部词典的词表选择。列名中的 bian_2021 标识词典来源, idf_score 标识这是 IDF 加权轨的篇级得分而非普通计数轨, mw 标识媒体权威度加权 (media-authority weighted), sum 标识 Bank-Year 层的合计聚合。需说明词典年份口径: 该词典以 SSRN 工作论文形式流通, 项目内统一以 2021 作为引用年份锚, 与词典文件的实际定稿年份口径一致, 引用时不再另行标注版本差异。

【方法学与计算】
计算分三层。第一层是篇级 IDF 加权得分 bian_2021_idf_score, 在 stage 22 (tone_words) 内计算。IDF 权重由 build_idf_weights 在全语料上统一估计一次, 采用 smooth IDF 公式 raw_idf(w) = log10(N/(1+df(w))), 再做均值归一化 normalized_idf = raw_idf / mean(raw_idf), 最后对 P1/P99 做 Winsorization 削平极端权重。文档频次 df(w) 与文档总数 N 均按唯一文档去重后统计, 以免"一篇新闻提到多家银行被展开成多行"虚增计数, 从而严格贴合 Gentzkow、Kelly 与 Taddy (2019) 以及 Spärck Jones (1972) 对文档级词项特异性的定义。IDF 词典构建后经 _compute_sentiment_with_rules 对每篇文本切词并按极性累加, 得到归一化的篇级 IDF 情感得分, 均值归一化保证其量级与等权版可比、可共享阈值。第二层是媒体权威度加权, 在 panel/runner 步骤 3c/3d 完成: media_authority_weight 由 media_weights.json 的静态权威性评分经均值归一化得到 (raw_weight / mean(raw_weight), 均值约为 1), 匹配策略为精确匹配 → 去括号归一化匹配 → 默认权重回退; 篇级列 bian_2021_idf_score_mw = bian_2021_idf_score × media_authority_weight。第三层是 Bank-Year 聚合, 在 encode 内以 sum 聚合把同一银行同一年内所有报道的加权得分逐篇相加, 得到本家族列。该合计是加权语调的分子, 与并行聚合的 sum_media_authority_weight 分母配对即可还原为加权均值。媒体权威度加权 (mw) 与市场提及密度加权 (vw)、跟风衰减加权 (hw)、等权版并列, 各自 just-identified 单独并排进入回归, 互为稳健性、不分主次, 严禁把不同加权方案或不同词典混入同一 over-identified 的 Hansen J 过度识别检验。

【文献定位】
IDF 词项加权的思想承接 Spärck Jones (1972) 的词项特异性统计诠释, 并在金融文本分析中由 Jegadeesh 与 Wu (2013) 的 "Word power" 方法发扬: 他们指出不同词对情感的边际信息量不等, 用样本回归赋予词以数据驱动的权重, 本项目以文档级 IDF 作为其无监督、语料内可复算的近似, 突出稀有词 (如违约、挤兑) 的信号、抑制高频泛用词 (如发展、提高) 的噪声。词典来源上, Bian 等 (2021) 与 Du 等 (2022) 均是面向中文财经语料的领域专用情感词典构建工作, Du 等 (2022) 尤其强调语言与领域特异性对中文金融情感测度的重要性, 说明为何不能直接照搬英文 Loughran-McDonald 词表; 本家族并列装载多部中文词典正是对这一关切的直接回应。方法互证层面, Frankel、Jennings 与 Lee (2022) 系统比较了词典法与机器学习法在披露情感测度上的表现, 为本项目将词典、LLM 投票、BERT 三法并置为互为稳健性轨提供了先例; van Atteveldt、van der Velden 与 Boukes (2021) 则以人工标注为基准评估了词典法与机器学习法情感测度的效度, 提示词典法在特定语料上的系统偏差需要多测度交叉验证来约束。综合而言, 本家族的方法学定位是"领域词典 × IDF 词项加权 × 媒体权威度加权"三重稳健性叠加下的一条并行测度轨。

## VAR: bian_2021_idf_score_mw_sum_full

【变体差分】
本列是 full 全文轨。三轨口径中, full 轨的篇级文本 = 标题 prepend 到全文正文 (content_full, 在 stage 14 由 ctx_materializer 物化, 原始"内容"列不动)。full 轨承担留篇门控的权威角色: 一篇报道是否被判为"银行金科报道"、是否进入银行-年样本宇宙, 仅由 full 轨的 LLM 判定决定 (full-only 门控口径, 2026-06-29); ctx 与 ss 两轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 的加权得分照常逐轨独立计算。因此本 full 列在三条轨中量级最完整, 覆盖同一银行-年内全部留篇报道的加权 IDF 情感合计, 通常是三轨里绝对值最大的一条。它区别于 ctx/ss 之处仅在文本范围 (整篇正文 vs 实体窗 vs 同句窗), IDF 权重本身三轨共享同一份 content_full 语料估计的权重表 (绝不按轨分语料重估), 媒体权威度权重亦逐篇同值。需强调本列是合计口径而非均值口径: 它把银行-年内每篇报道的加权 IDF 得分逐篇相加, 因此天然随报道数量放大, 使用时通常需与并行聚合的媒体权威度权重合计分母配对还原为加权均值, 或在回归中显式控制报道量, 以免把"覆盖多"误读为"情感强"。与之相对, 本列刻意保留合计形态是为了作为加权语调的分子直接进入下游加权均值构造, 避免在篇级先做除法引入零覆盖格的除零问题。作为规格稳健性并排轨, full 与 ctx、ss 各自 just-identified 单独进入回归, 互为稳健性、不分主次, 禁止三轨混入同一 over-identified 的 Hansen J; 同理本 mw 加权轨也不与等权版、市场提及密度加权版 (vw)、跟风衰减加权版 (hw) 混入同一过度识别检验。

## VAR: bian_2021_idf_score_mw_sum_ctx

【变体差分】
本列是 ctx 实体窗轨。ctx 轨的篇级文本 = 标题 prepend 到实体上下文窗口 (content_ctx, 在 stage 14 物化), 即只截取目标银行实体附近的若干句子而非整篇正文, 目的是把情感信号收敛到与银行实体真正相关的语境, 削弱整篇报道中与该银行无关段落带来的稀释。相较 full 轨覆盖全文, ctx 轨的加权 IDF 情感合计只累加实体窗内命中词的贡献, 因此在同一银行-年内其绝对量级通常小于 full 轨。ctx 轨是 conditional-on-full 的稳健性轨: 其行宇宙为 full 留篇集的子集 (留篇判定只看 full), 但窗内的 IDF 篇级得分、媒体权威度加权与 Bank-Year 求和均按 ctx 轨自身文本逐轨独立计算, 不借用 full 轨的中间量。IDF 权重表仍与 full/ss 共享同一份 content_full 语料估计的权重 (三轨绝不分语料重估), 差异纯粹来自打分文本范围。实体窗轨的价值在于它把"这家银行在这篇报道里到底被怎样评价"与"这篇报道整体基调"两件事分开: 一篇整体乐观的行业综述里, 单独提及某家银行的那几句可能是负面的, ctx 轨能捕捉到这一局部信号而 full 轨会被整篇稀释。也正因为窗口收窄, ctx 轨在语料稀疏或实体提及零散时更易出现零覆盖或方差退化, 使用时需留意其样本依赖性。作为规格稳健性并排轨, ctx 与 full、ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 过度识别检验; 本 mw 加权轨亦不与等权、vw、hw 加权版混入同一过度识别检验。

## VAR: bian_2021_idf_score_mw_sum_ss

【变体差分】
本列是 ss 银行金科同句轨。ss 轨的篇级文本 = 标题 prepend 到"银行与金融科技词同句共现 ± N 窗"内的句子 (content_ss, 在 stage 14 物化, 窗半径由 filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语境最收窄的一条, 只保留银行与金科主题真正同句耦合处的情感信号。其回退语义严格镜像 ctx: 当某篇报道不存在银行与金科的同句共现时, content_ss 退化为全文正文、ss_is_fallback 置为 True, 并与其余轨共享同一 n_articles 分母; 当金科词表 FINTECH_AC 为空时全篇优雅降级。这一回退口径决定了 ss 轨在语料稀疏时会向 full 轨靠拢而非留空。ss 轨同样是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集, 但同句窗内的 IDF 篇级得分、媒体权威度加权与 Bank-Year 求和均按 ss 轨文本逐轨独立计算; IDF 权重仍与 full/ctx 共享同一份 content_full 语料权重表。同句轨是三轨中构念最锐、也最易退化的一条: 在开发期的浅面板 (T 很小) 上, 同句共现命中稀少会使该轨大面积走回退、逼近零方差, 属预期的样本退化而非缺陷; 在生产规模语料上它才能稳定给出银行与金科主题真正耦合处的情感读数, 这也是把它单列一轨而非并入 ctx 的原因。使用时应结合 ss_is_fallback 指示列判断某格究竟来自真实同句窗还是全文回退, 避免把回退格当作真同句信号解读。作为规格稳健性并排轨, ss 与 full、ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁止三轨混入同一 over-identified 的 Hansen J; 本 mw 加权轨同样不与等权、vw、hw 加权版混入同一过度识别检验。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
<!-- rendered-citations:end -->
