---
family_id: F643
columns:
- you_2018_idf_tone_app_ctx
- you_2018_idf_tone_app_full
- you_2018_idf_tone_app_ss
- you_2018_idf_tone_ctx
- you_2018_idf_tone_full
- you_2018_idf_tone_hw_ctx
- you_2018_idf_tone_hw_full
- you_2018_idf_tone_hw_ss
- you_2018_idf_tone_mw_ctx
- you_2018_idf_tone_mw_full
- you_2018_idf_tone_mw_ss
- you_2018_idf_tone_ss
- you_2018_idf_tone_std_ctx
- you_2018_idf_tone_std_full
- you_2018_idf_tone_std_ss
- you_2018_idf_tone_tech_ctx
- you_2018_idf_tone_tech_full
- you_2018_idf_tone_tech_ss
- you_2018_idf_tone_vw_ctx
- you_2018_idf_tone_vw_full
- you_2018_idf_tone_vw_ss
unit: 无量纲语调得分 (idf 词权聚合, 理论范围约 [-1,1]; bank-year × 轨道)
formula: 'you_2018_idf_tone{track} = mean_{a∈bank-year}(you_2018_idf_score{track}(a)), 其中逐篇 you_2018_idf_score{track}(a) 由 stage 22 tone_words 用 you_2018 词典命中词按 corpus 级 idf 权重(而非等权计数)加总正负极性得到; _std{track} = std_{a}(you_2018_idf_score{track}(a)); _vw{track} = sum(you_2018_idf_score_w{track}) / sum_mention_density (news_salience 提及密度加权); _mw{track} = sum(you_2018_idf_score_mw{track}) / sum_media_authority_weight (Holzman et al. 2023 媒体权威加权); _hw{track} = sum(you_2018_idf_score_hw{track}) / sum_herd_weight{track} (stage 24 herd_decay 时间衰减加权); _app{track}/_tech{track} = mean(you_2018_idf_score{track}(a)) 限定在 innovation_locus_full(a)==应用场景/底层技术 的子样本(分类判据固定用 full 轨, 与 you_2018_idf_tone{track} 本身的文本轨互相独立)'
producer: "news_process/pipeline/sentiment/tone_words.py (逐篇 you_2018_idf_score{track} 计算) ; news_process/pipeline/panel/encode.py (聚合: 基础/std 见 build_aggregation_dict 第 C2 段; vw/mw/hw 见 Value/Media-Authority/Herd-Decay-weighted Tone 后处理段; app/tech 见 innovation_locus 分类聚合段)"
upstream:
- 22_tone_words.parquet (逐篇 you_2018_idf_score_full / _ctx / _ss 及其 _w / _mw / _hw 加权分子)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 11_news_bank news_salience (mention_density, 供 _vw 分母)
- pipeline media authority tier (Holzman et al. 2023 三级媒体权威权重, 供 _mw 分母)
- 24_herd_decay_processor.parquet (herd_weight{track}, 供 _hw 分母)
- 16_article_policy_alignment / innovation_locus 分类模块 (innovation_locus_full, 供 _app/_tech 子样本切分)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
本家族测度报道语调(media tone)对目标银行的整体倾向, 底层词典来自 You, Zhang & Zhang (2018, RFS)《Who Captures the Power of the Pen?》构建的中文金融情感词典(正面词 1,425 个、负面词 1,583 个)。该词典与 jiang_2021/yao_2021/bian_2021/du_2022/loughran 五部词典并列构成 config/tone_dicts.json 的多词典矩阵, 六部词典互为稳健性、不分主次, 任一词典的结论皆不应单独作为主分析依赖。you_2018 词典在原论文中的应用场景是识别官方媒体与市场化媒体在企业负面消息报道上的系统性差异("谁在为谁的笔杆子服务"), 本项目移植其正负词表, 服务于识别银行—金融科技共现报道的语调方向。与其余五部等权词典族(如 bian_2021_score_w_sum、du_2022_score 等)不同, you_2018_idf_tone 家族在词典命中的基础上引入 corpus 级 idf(逆文档频率)词权, 即每个命中词的贡献不再是等权 ±1 计数, 而是按该词在整个语料中的稀有度(信息量)加权, 高频泛用的情感词(如"发展""风险")权重被压低, 低频但更具信息含量的情感用语权重被放大。

【方法学与计算】
逐篇 idf 加权得分 you_2018_idf_score{track}(a) 在 stage 22 tone_words.py 中计算: 先用 you_2018 正负词表在文章分词结果上做词典匹配(同时应用否定翻转/程度副词/转折等语言学规则, 与等权口径一致), 再将每个命中词的 ±1 极性乘以该词在全语料上的 idf 权重后求和/归一, 得到单篇 idf 加权语调分。bank-year 面板聚合层(pipeline/panel/encode.py)在此之上派生出本家族 21 列: (1) 无后缀基线列 you_2018_idf_tone{track} 是该 bank-year 内全部留篇文章 idf 语调分的等权算术平均, 是本家族的 canonical 测度; (2) _std 后缀是同一集合的标准差, 度量语调的篇间离散度而非水平; (3) _vw/_mw/_hw 三个加权变体分别用文章的媒体提及密度(mention_density, 出自 stage 11 news_salience)、媒体权威分层权重(Holzman et al. 2023 的三级媒体声誉权重)、以及 herd-decay 时间衰减权重(stage 24, 越晚近报道权重越高的衰减核)对逐篇 idf 语调分加权求和后除以对应权重和, 三者是彼此正交、互为稳健性的聚合方式选择, 不构成同一构念的层级关系; (4) _app/_tech 是按 innovation_locus_full(P4 Gomber(2018)框架下的"底层技术"vs"应用场景"金融科技创新定位分类, 判据固定用 full 轨文本分类结果)切分子样本后重新计算的等权均值, 与切分该 idf 语调分本身所用的轨道(full/ctx/ss)是两个独立维度, 不可混淆——例如 you_2018_idf_tone_app_ctx 是"ctx 轨文本算出的 idf 语调分, 限定在 full 轨判定为应用场景类的文章子集"。

【文献定位】
idf 词权思路的方法学锚点是 Gentzkow, Kelly & Taddy (2019, JEL)《Text as data》对 text-as-data 文献中 tf-idf 类词加权技术的系统综述, 以及 Spärck Jones (1972) 提出的逆文档频率(idf)统计解释这一信息检索经典定义本身。you_2018_idf_tone 与家族外的等权 you_2018_tone(若存在)/等权其余五词典构成"等权计数 vs idf 加权"的方法学梯子, 二者互为稳健性稳健性检验、不设主次: 等权口径假设每个命中词信息量相同, idf 口径假设高频泛用词信息量更低, 两种假设在文献中均有支持, 因此并排报告。_mw 变体的方法学依据是 Holzman, Miller & Twedt (2023, The Accounting Review) 对媒体声誉分级加权在语调可信度上的作用的实证发现; _app/_tech 分类判据的方法学依据是 Gomber, Kauffman, Parker & Weber (2018, JMIS) 对金融科技创新"底层技术 vs 应用场景"二分框架的界定, 该框架是本项目 P4(bank_fintech_locus)论文主轨的构念基础。

三轨/加权梯子铁律: full/ctx/ss 三个文本轨道, vw/mw/hw 三种加权口径, 与 app/tech 二分类判据均是各自独立、just-identified 并排的稳健性维度, 不得混入同一个 over-identified 的 Hansen J 检验框架中联合识别; 三轨之间互为稳健性、不分主次, 各自独立进入回归而非合并为单一右手边变量。留篇门控口径遵循 2026-06-29 起生效的 full-only 规则: 一篇报道是否计入"银行—金融科技共现报道"样本仅由 llm_verified_full 判定, ctx/ss 轨的语调数值是在 full 轨留篇集合的子集上计算的条件测度/稳健性轨, 而非独立样本; you_2018_idf_tone_ctx/_ss 的行宇宙始终是 you_2018_idf_tone_full 留篇集合的子集。ss 轨遵循镜像 ctx 的回退语义: 若某篇文章在标题窗口内不存在银行∧金融科技同句共现, 则 content_ss 回退为全文正文(与 content_full 相同文本), ss_is_fallback 置为 True, 此时该篇的 you_2018_idf_score_ss 数值上等于按同一词典对全文计算的结果, 不代表真实的"同句窗口"语调; bank-year 聚合分母(n_articles)在 full/ctx/ss 之间共享同一计数口径。

## VAR: you_2018_idf_tone_app_ctx

【变体差分】
本列在 ctx 轨文本(标题+实体窗口)上计算 you_2018 idf 加权语调分的逐篇均值, 但限定样本仅含 innovation_locus_full 分类结果为"应用场景"(_app)的文章子集。判据来源须特别注意: 用于切分子样本的 innovation_locus 分类判定固定使用 full 轨(标题+全文正文)文本作为分类依据, 与本列语调计算所用的 ctx 轨文本是两个独立通道——这意味着即便某篇文章在 ctx 窗口内出现的语调倾向不同于 full 轨, 它是否被划入"应用场景"桶不受 ctx 轨影响, 只看该文章在 full 轨上的 P4(Gomber 2018)分类归属。该设计避免了"用哪个轨道的文本做分类判据"与"用哪个轨道的文本做语调测度"两个维度相互纠缠导致的组合爆炸, 分类判据统一锚定在留篇门控轨(full)上, 测度轨则独立地在 full/ctx/ss 三者间轮换, 构成本家族 21 列中 app/tech 两个后缀各自的三轨并排。应用场景类通常指银行将金融科技技术应用于获客、风控、支付等具体业务场景的报道(相对于底层技术研发本身), 该子样本上的语调均值可用来检验"媒体对银行金融科技应用层面的评价"是否系统性不同于对底层技术投入的评价, 是 P4 论文识别策略的辅助测度之一。ctx 轨作为条件稳健性轨, 行宇宙是 you_2018_idf_tone_app_full 留篇集合(且落在应用场景类)的子集, 与 _tech_ctx、以及无分类切分的 you_2018_idf_tone_ctx 互为稳健性并排, 不应混入同一 over-identified 设定联合识别。

## VAR: you_2018_idf_tone_app_full

【变体差分】
本列是 full 轨(标题+全文正文)文本上计算的 you_2018 idf 加权语调分, 限定在 innovation_locus_full 分类为"应用场景"的文章子集上取逐篇均值。由于分类判据本身也锚定在 full 轨, 本列是 app/tech 两个分类子样本变体中判据轨与测度轨完全重合的唯一一列(ctx/ss 版本的判据轨固定为 full、测度轨切换为 ctx/ss, 存在轨间错位), 因此本列在方法学上最贴近"应用场景类报道整体语调水平"这一构念本身, 是 P4 论文识别策略中该类别语调的 headline 版本。计算上, 先由 innovation_locus 分类模块(P4/Gomber 2018 底层技术—应用场景二分框架)在留篇集合内对每篇文章标注 innovation_locus_full∈{底层技术, 应用场景}, 再取该子集内逐篇 you_2018_idf_score_full 的算术平均。样本量上, 该列的有效观测数 n_articles_app 与 n_articles_tech 之和须满足对 n_articles_llm_valid 的恒等式校验(R6 口径 >=, 而非严格 ==, 与 collab 维度的分类校验逻辑一致), 以防止分类逻辑静默漏记文章。该列与家族基线 you_2018_idf_tone_full(未做类别切分的全样本均值)互补: 二者之差(gap)可用于检验银行金融科技报道的语调是否因创新定位不同而系统性分化, 是稳健性检验维度而非替代关系。使用者在解读该列时应留意, "应用场景"与"底层技术"的分类边界并非机械的关键词匹配, 而是由 P4 innovation_locus 分类模块基于全文语义判定得出, 因此该列的样本构成本身携带了分类模型的判定不确定性, 建议与分类置信度诊断(如面板层面的低置信度标记 low_conf_flag, 见 G-20 诊断段)交叉核对后再解读语调水平的经济含义, 避免把分类噪声误读为真实的类别间语调差异。

## VAR: you_2018_idf_tone_app_ss

【变体差分】
本列在 ss 轨(标题+银行∧金融科技同句±N窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 设定, 默认 1)文本上计算 you_2018 idf 加权语调分, 限定在 innovation_locus_full 分类为"应用场景"的子样本上取均值。与 app_ctx 列相同, 分类判据固定锚定在 full 轨, 与本列所用的 ss 测度轨相互独立。ss 轨相比 ctx 轨窗口更窄, 只截取银行与金融科技词汇同句出现(或按句子半径扩展)的局部文本, 更贴近"语境紧邻"的语调信号, 是比 ctx 更严格的局部化稳健性轨。需特别注意 ss 轨的回退语义: 若一篇被 full 轨判定为应用场景类的文章, 在标题窗口内不存在银行∧金融科技同句共现, 则其 content_ss 按镜像 ctx 的规则回退为全文正文, ss_is_fallback 标记为 True, 此时该篇对本列的贡献数值上等价于把该篇计入 full 轨语调分, 而非真实的同句局部语调, 这是一种优雅降级而非缺失值, 分母 n_articles 与 full/ctx 共享同一计数口径不因回退而改变。本列与 you_2018_idf_tone_app_ctx、you_2018_idf_tone_app_full 构成三轨并排, 互为稳健性, 三者禁止混入同一 over-identified Hansen J 联合识别, 应在回归设计中分别单独进入模型或作为独立稳健性表格并排报告。由于 ss 轨窗口本身已比 ctx 更窄, 叠加应用场景子样本切分后, 部分 bank-year 的有效观测篇数可能进一步收缩至个位数, 使用该列做统计推断时应结合 n_articles_app 观测该子样本容量, 容量过小的年份估计值的抽样不确定性较大, 不宜单独据此下强结论。

## VAR: you_2018_idf_tone_ctx

【变体差分】
本列是家族 canonical 基线在 ctx 轨(标题+实体窗口文本)上的对应版本: 对留篇集合中每篇文章的 content_ctx 文本用 you_2018 词典按 idf 词权计算逐篇语调分 you_2018_idf_score_ctx, 再在 bank-year 内取算术平均, 不做任何加权或类别切分, 是本家族 21 列中最基础的三轨基线之一。ctx 轨的实体窗口构造是围绕目标银行与金融科技相关实体截取的局部上下文, 相对 full 轨排除了文章中与银行—金融科技话题无关的段落噪声, 因此常被用作比全文更聚焦的稳健性测度。留篇门控铁律要求: 该列的行宇宙是 you_2018_idf_tone_full 对应留篇集合的子集(即是否计入样本仍由 llm_verified_full 判定), ctx 轨仅决定"在留篇集合内, 用哪段文本算语调", 不改变样本边界本身。该列与 you_2018_idf_tone_full、you_2018_idf_tone_ss 构成三轨并排关系, 互为稳健性、不分主次, 三者应分别单独进入回归右手边或作为并排稳健性表格呈现, 禁止在同一 over-identified 设定中联合识别; 三者与本家族的 std/vw/mw/hw/app/tech 等其余维度是正交的独立稳健性轴, 互不覆盖对方的稳健性含义。实践上建议将 ctx 轨结果与 full 轨结果并列汇报: 若二者在符号和显著性上高度一致, 说明结论不依赖于是否纳入报道全文中与银行—金融科技话题无关的背景段落, 从而增强对基线测度稳健性的信心; 若二者出现分歧, 则提示全文中存在的额外语境信息(如同一篇报道中提及的其他业务)可能在系统性地拉动或压低整体语调水平, 值得进一步定性核查典型样本。

## VAR: you_2018_idf_tone_full

【变体差分】
本列是家族 canonical 主测度: 在 full 轨(标题+全文正文)文本上, 对 bank-year 内全部留篇文章计算 you_2018 idf 加权语调分的算术平均, 未做任何加权调整或类别切分。作为 full-only 留篇门控口径下的基线轨, 本列的样本边界(是否计入该 bank-year 的分子分母)直接由 llm_verified_full 判定决定, 是本家族全部其余 20 列共享的行宇宙锚点: ctx/ss 轨、std/vw/mw/hw 加权变体、app/tech 类别切分, 均是在该留篇集合(或其子集)上做的条件测度或加权重述, 不构成独立样本。计算链路上, 本列源自 stage 22 tone_words.py 逐篇计算的 you_2018_idf_score_full(idf 加权版本, 区别于同名等权词典族的 you_2018_score_full), 经 pipeline/panel/encode.py 的 build_aggregation_dict 在 C2 段(词典法 IDF)以 'mean' 方式聚合到 bank-year。该列是 P1(bank_fintech_tone)论文情感稳健性检验的多词典矩阵成员之一, 与 jiang_2021/yao_2021/bian_2021/du_2022/loughran 五部词典各自的 idf_tone_full(若存在对应家族)以及 you_2018 自身的等权版本共同构成词典层面的稳健性梯子, 均不作为主分析的唯一依据, 主分析依赖 P1 主轨的三家 LLM 投票语调 llm_vote_tone_full。词典法与 LLM 法在方法学上互为稳健性、并非层级关系: 词典法透明可复现、无温度随机性, 但对语境依赖(反讽、否定嵌套、行业术语的多义性)不敏感; LLM 法能捕捉更细粒度的语境线索, 但存在模型间分歧与提示词版本依赖。两者数值方向一致时, 结论的稳健性证据更强; 出现系统性分歧时应披露并讨论可能原因, 而非选择性报告支持结论的一方。

## VAR: you_2018_idf_tone_hw_ctx

【变体差分】
本列在 ctx 轨文本上, 用 herd-decay 时间衰减权重(hw, herd weight, 出自 stage 24 herd_decay_processor)对逐篇 you_2018 idf 加权语调分做加权聚合: 分子是逐篇 idf 语调分乘以该篇的 herd_weight_ctx 后求和(you_2018_idf_score_hw_ctx 的 sum), 分母是该 bank-year 内全部文章 herd_weight_ctx 之和(sum_herd_weight_ctx), 二者相除得到本列数值。herd-decay 权重的构念含义是"报道时点距离该 bank-year 观测窗口越晚近, 权重越高", 反映信息衰减/羊群效应随时间递减的假设, 与 vw(提及密度加权)、mw(媒体权威加权)是三种彼此独立的加权哲学, 分别捕捉"提及强度"、"信源可信度"、"时间新近性"三个不同维度, 互为稳健性并排而非层级关系。hw 加权分母按轨道独立计算(_hw_denom_by_track 在 full/ctx/ss 三轨分别取各自的 sum_herd_weight{track}), 这意味着 you_2018_idf_tone_hw_ctx 与 you_2018_idf_tone_hw_full 不仅语调分子来自不同文本轨, 衰减权重本身也是按 ctx 轨单独估计的, 二者是完全独立的稳健性测度, 不共享分母。herd-decay 权重核的设计初衷是刻画舆论"羊群效应"随时间自然衰减的经验规律: 一条负面报道在发布当下对市场情绪的边际影响通常大于事后被重新提及, 若不做时间加权, 等权聚合会把年初已被市场充分消化的旧闻与年末最新报道同等对待, hw 加权正是为纠正这一偏差而设。该列因此尤其适合与等权基线 you_2018_idf_tone_ctx 联合解读舆论新近性对结论的影响。

## VAR: you_2018_idf_tone_hw_full

【变体差分】
本列在 full 轨文本上, 用 herd-decay 时间衰减权重对逐篇 you_2018 idf 加权语调分做加权聚合, 是 hw 加权口径在留篇门控主轨(full)上的版本。计算公式为 sum(you_2018_idf_score_hw_full) / sum_herd_weight_full, 分子分母均在 full 轨内部自洽计算。该加权设计的动机是: 等权聚合(you_2018_idf_tone_full)对 bank-year 内的所有留篇文章一视同仁, 但若某银行在年末密集出现相关报道而年初报道寥寥, 等权均值会低估近期舆论态势的权重; herd-decay 核对越晚近的报道赋予越高权重, 从而更贴近"当前舆论氛围"这一构念。该权重核的具体衰减函数(如半衰期设定)由 stage 24 herd_decay_processor 统一估计并写入 herd_weight{track} 列, 本列仅是该权重在 you_2018 词典 idf 语调分上的应用实例之一, 与 llm_vote_tone_hw_full、其余五词典各自的 dict_idf_tone_hw_full(若存在)共享同一套 herd_weight_full 权重序列, 构成跨测度方法(LLM/词典)、跨词典共用同一时间衰减核的横向可比设计, 便于在稳健性表格中并排比较不同情感测度方法在同一加权哲学下的结果。该列与等权基线 you_2018_idf_tone_full、提及密度加权 you_2018_idf_tone_vw_full、媒体权威加权 you_2018_idf_tone_mw_full 共同构成 full 轨上四种聚合哲学(等权/提及强度/信源权威/时间新近)的完整对照组, 是评估该银行—年度语调结论对聚合方式选择稳健性的核心参照集之一, 建议在正文结果表之外的附录中完整呈现该四列并排结果。

## VAR: you_2018_idf_tone_hw_ss

【变体差分】
本列在 ss 轨(标题+银行∧金融科技同句窗口)文本上, 用按 ss 轨单独估计的 herd-decay 权重(sum_herd_weight_ss)对逐篇 you_2018 idf 加权语调分做加权平均: sum(you_2018_idf_score_hw_ss) / sum_herd_weight_ss。ss 轨的窗口比 ctx 更局部, 只截取银行与金融科技实体同句共现(或按句子半径参数扩展)的紧邻文本, 该列因此是"局部语境语调 × 时间新近性加权"的双重稳健性组合。需注意 ss 轨遵循镜像 ctx 的回退语义: 若某篇文章无同句共现, content_ss 回退为全文正文且 ss_is_fallback=True, 此时该篇对分子分母的贡献等价于把该篇当作 full 轨处理, 而 herd_weight_ss 本身的估计是否也对回退文章做相应处理由 stage 24 内部实现决定, 但分母口径(sum_herd_weight_ss)与分子口径(sum(you_2018_idf_score_hw_ss))在同一轨内保持自洽。本列与 you_2018_idf_tone_hw_ctx、you_2018_idf_tone_hw_full 构成 hw 加权口径下的三轨并排, 三者禁止混入同一 over-identified Hansen J, 应各自独立进入稳健性检验矩阵。由于 ss 轨窗口本身较窄且部分文章可能触发同句回退, hw 权重与语调分子在回退文章上实质上退化为 full 轨口径的重述, 该列因此在高回退比例的 bank-year 上信息增量有限, 建议使用者结合 ss_is_fallback 占比诊断该列在不同银行—年度上的解释力边界, 对回退比例极高的观测谨慎解读为"局部语境的时间加权语调"。

## VAR: you_2018_idf_tone_mw_ctx

【变体差分】
本列在 ctx 轨文本上, 用媒体权威分层权重(mw, media authority weight, 依据 Holzman, Miller & Twedt 2023《Curbing enthusiasm》对媒体声誉三级分层的实证设计)对逐篇 you_2018 idf 加权语调分做加权聚合: sum(you_2018_idf_score_mw_ctx) / sum_media_authority_weight。媒体权威权重的构念含义是"权威媒体(如党报、财经专业媒体)对市场的语调影响力大于地方小报或自媒体", 因此在加权聚合时给权威媒体来源的报道更高权重, 这与家族内 vw(提及密度加权, 捕捉报道数量强度)、hw(herd-decay 时间衰减加权, 捕捉时间新近性)是三个彼此独立、构念上不重叠的加权维度。媒体权威权重本身与文本轨(full/ctx/ss)无关, 是基于文章元数据(发布媒体来源)而非正文内容确定的固定权重, 因此 sum_media_authority_weight 分母在理论上不因 ctx/full/ss 轨切换而改变构造逻辑, 差异仅来自哪些文章落入留篇集合、以及 ctx 轨截取的文本片段用于计算分子中的 idf 语调分。该列是 P1 论文"媒体权威加权稳健性"检验的多词典矩阵成员之一。需要强调的是, 媒体权威分层权重本身是外生元数据(取决于媒体来源标签), 不随本列所处的文本轨(ctx)切换而改变分层判定逻辑, 唯一随轨道变化的是分子中逐篇 idf 语调分所依据的文本片段; 因此 mw_ctx 与 mw_full、mw_ss 三列的差异纯粹来自"文本抽取范围不同导致的逐篇语调分不同", 而非权重方案本身的差异, 这一点是解读 mw 三轨并排结果时需要牢记的识别要点。

## VAR: you_2018_idf_tone_mw_full

【变体差分】
本列在 full 轨文本上用媒体权威分层权重对逐篇 you_2018 idf 加权语调分做加权聚合, 是 mw 加权口径在留篇主轨上的版本: sum(you_2018_idf_score_mw_full) / sum_media_authority_weight。Holzman et al. (2023, The Accounting Review) 的原始设计是用媒体声誉分层来解释语调对市场反应的解释力差异, 本项目将该思路移植为面板加权方案: 每篇报道按其所属媒体的权威分层(通常为高/中/低三级)获得固定权重, 权威媒体的语调在 bank-year 聚合中被赋予更大话语权。该列与 you_2018_idf_tone_full(等权基线)构成同一 idf 词典、同一文本轨、不同加权哲学的差分对: 若二者数值高度一致, 说明该银行的媒体报道语调对媒体权威分层不敏感; 若二者出现系统性分歧, 则提示权威媒体与非权威媒体对该银行的报道倾向存在差异, 需结合具体案例解读。该列与本家族其余五部词典各自的 mw 加权版本、以及 P1 主轨 llm_vote_tone_mw_full 共享同一套 media_authority_weight 权重序列, 是跨测度方法可比的横向稳健性设计。由于权重序列跨测度方法共享, 研究者可以在同一张稳健性表格中并排列出词典法(如本列)与 LLM 法在相同媒体权威加权方案下的估计系数, 若二者方向一致则说明"媒体权威加权"这一稳健性维度的结论不依赖于具体采用哪种情感测度技术, 是跨方法一致性检验的一个标准配置。

## VAR: you_2018_idf_tone_mw_ss

【变体差分】
本列在 ss 轨(银行∧金融科技同句窗口)文本上, 用媒体权威分层权重对逐篇 you_2018 idf 加权语调分做加权聚合: sum(you_2018_idf_score_mw_ss) / sum_media_authority_weight。该列组合了两层稳健性: 文本层面聚焦到银行与金融科技实体同句紧邻出现的局部语境(比 ctx 更严格的局部化), 加权层面按报道来源的媒体权威性调整话语权。ss 轨的回退语义与其余 ss 列一致(镜像 ctx): 若某篇文章不存在同句共现, content_ss 回退为全文正文, ss_is_fallback=True, 该篇按全文文本参与 idf 语调分计算, 但其媒体权威权重不受回退影响(权重取决于发布媒体本身, 与文本截取方式无关)。本列与 you_2018_idf_tone_mw_ctx、you_2018_idf_tone_mw_full 构成 mw 加权口径下的三轨并排家族, 三者及其与 hw/vw 加权口径、与 app/tech 类别切分维度均彼此正交, 是各自独立的稳健性检验轴, 不应在同一实证设计中混合叠加成单一构造以避免维度爆炸和识别混淆, 应作为并排稳健性表格分别报告。ss 轨窗口最窄、且叠加媒体权威加权后, 若某银行—年度内触发同句共现的报道恰好集中于同一家权威媒体或同一家非权威媒体, 该列数值会对该单一媒体来源的语调判断高度敏感, 使用者应结合媒体来源分布的描述统计一并核查, 避免把单一信源的偶然语调误读为系统性舆论态势。

## VAR: you_2018_idf_tone_ss

【变体差分】
本列是家族基线在 ss 轨(标题+银行∧金融科技同句±N窗口, N 见 config/filtering.yaml::context_window.ss_sentence_radius)文本上的版本: 对留篇集合中每篇文章的 content_ss 计算 you_2018 idf 加权语调分 you_2018_idf_score_ss, 再在 bank-year 内取算术平均, 不做加权或类别切分。ss 轨是本家族三个文本轨中窗口最窄的一个, 判定原语为 core/text/entity_context.py 中与 stage 13 共现硬过滤不同口径的严格同句抽取函数, 只保留银行与金融科技词汇同一句子内(或按句子半径扩展)共现的文本片段拼接为超级文档, 该拼接过程剔除 *_is_fallback 标记的行、且禁止重复拼接标题通道以避免双标题污染。该列遵循镜像 ctx 的回退语义: 无同句共现时 content_ss 整体回退为全文正文, ss_is_fallback=True, 此时该篇对本列的贡献数值上等同于该篇的 full 轨语调分, 是优雅降级而非缺失。本列与 you_2018_idf_tone_ctx、you_2018_idf_tone_full 三轨并排、互为稳健性, 行宇宙均为留篇门控(full-only)集合的子集, 不改变样本边界只改变测度所用文本片段。作为家族基线三轨中窗口最窄的一支, 本列适合用来检验语调结论是否只在"银行与金融科技被直接同句提及"的最强证据文本上成立: 若基线均值(you_2018_idf_tone_full)与本列在方向上一致, 说明结论不依赖于纳入宽泛背景文本; 若本列因回退比例过高而在数值上趋近于 full 轨, 则该稳健性检验的信息增量有限, 应结合 ss_is_fallback 占比谨慎解读。

## VAR: you_2018_idf_tone_std_ctx

【变体差分】
本列是 you_2018_idf_tone_ctx 对应 bank-year 内逐篇语调分的标准差, 而非均值: std_{a}(you_2018_idf_score_ctx(a)), 度量的是"该银行在该年度、ctx 轨文本上的报道语调离散程度"而非语调的方向或水平。高标准差意味着该银行在同一年度内既有强烈正面报道也有强烈负面报道, 舆论评价分歧较大; 低标准差意味着报道语调相对一致(无论整体正面还是负面)。该列与家族基线 you_2018_idf_tone_ctx 构成"一阶矩(均值, 水平)vs 二阶矩(标准差, 离散度)"的互补关系而非替代关系, 二者应联合解读——例如均值接近 0 但标准差很高, 与均值接近 0 且标准差很低, 在舆论环境解读上含义截然不同(前者是"毁誉参半", 后者是"平淡中性")。样本量过小(如某 bank-year 仅 1 篇留篇文章)时标准差退化为 0 或未定义(单点样本无离散度), 使用该列做横截面或面板回归时需留意小样本年份的数值可靠性, 与 BERT 分布形状五族测度中偏度需 n≥10 掩码的设计精神一致但本列本身未设最小样本量门槛。研究者在使用该列作为舆论分歧的代理变量时, 建议同时报告对应 bank-year 的 n_articles 观测数作为诊断信息, 避免把小样本抽样噪声误读为真实的舆论撕裂现象; 跨银行、跨年份比较该列数值时也应留意样本容量本身可能与银行规模、媒体曝光度相关, 存在潜在的异方差性。

## VAR: you_2018_idf_tone_std_full

【变体差分】
本列是 you_2018_idf_tone_full 对应 bank-year 内逐篇语调分的标准差, 计算公式 std_{a∈bank-year}(you_2018_idf_score_full(a)), 是家族主轨(full)上的离散度测度。作为留篇门控主轨对应的标准差版本, 该列与 you_2018_idf_tone_full 均值构成的一阶/二阶矩对是本家族在 full 轨上最完整的分布刻画: 均值捕捉方向与水平, 标准差捕捉分歧程度。方法学上该设计与本项目 BERT 概率分布形状五族测度(2026-07-04 落地的 tone_entropy/xneg_frac/net_tone_skew 等)在构念上呼应, 都是从"逐篇打分"到"逐篇打分的分布特征"这一测度升级路径, 但计算工具不同——BERT 五族基于三分类概率的信息熵/极端占比/偏度, 本列则是最简单直接的逐篇标量得分的标准差, 二者互不替代、可并列作为舆论分歧的不同侧面证据。该列在 pipeline/panel/encode.py 的 build_aggregation_dict 中以 ('you_2018_idf_score_full', 'std') 聚合函数产出, 与其余五部词典各自的 idf_tone_std_full 共同构成词典层面的离散度稳健性矩阵。若六部词典各自的 std_full 在同一 bank-year 上呈现高度一致的相对排序(即哪些银行—年度舆论分歧更大, 各词典判断趋同), 则说明"舆论分歧"这一构念的测度对具体采用哪部词典不敏感, 是词典选择稳健性的一个附加检验维度, 可与本家族均值层面的稳健性梯子并列报告。

## VAR: you_2018_idf_tone_std_ss

【变体差分】
本列是 you_2018_idf_tone_ss 对应 bank-year 内逐篇语调分的标准差, 计算公式 std_{a∈bank-year}(you_2018_idf_score_ss(a)), 是家族在 ss 轨(银行∧金融科技同句窗口)上的离散度测度。由于 ss 轨窗口更窄, 部分文章可能触发 ss_is_fallback 回退为全文语调分, 这意味着该列所反映的"离散度"实际上是"真同句语调分"与"回退全文语调分"混合样本的标准差, 解读时应意识到回退比例较高的 bank-year 中, ss 轨标准差可能更接近 full 轨标准差而非真正的局部语境离散度。本列与 you_2018_idf_tone_std_ctx、you_2018_idf_tone_std_full 构成三轨并排的标准差稳健性组, 三者与均值三轨组(you_2018_idf_tone_{ctx,full,ss})、加权三组(vw/mw/hw)、类别切分组(app/tech)在维度上完全正交, 是各自独立的稳健性检验轴; 铁律要求三轨/加权口径/类别判据均应 just-identified 并排使用, 不得混入同一个过度识别的 Hansen J 检验设定中联合估计。ss 轨标准差还受回退机制的额外扰动: 若某 bank-year 内只有部分文章触发同句回退而另一部分保留真实同句语境, 该列实际上是两种不同信息粒度语调分的混合分布标准差, 数值上可能同时偏离"纯局部语境离散度"与"纯全文离散度"两端, 解读时应结合 ss_is_fallback 占比判断该列数值的解释力边界, 避免过度精细化归因。

## VAR: you_2018_idf_tone_tech_ctx

【变体差分】
本列在 ctx 轨文本上计算 you_2018 idf 加权语调分的逐篇均值, 限定样本为 innovation_locus_full 分类结果为"底层技术"(_tech, 对应 Gomber 2018 框架中聚焦区块链/大数据/人工智能等底层技术研发本身的报道, 而非其具体业务应用)的文章子集。与 app_ctx 列对称, 本列的分类判据同样固定锚定在 full 轨文本, 与本列语调计算所用的 ctx 轨相互独立: 一篇文章是否属于底层技术类, 只看其在 full 轨上的 P4 分类结果, 不受 ctx 轨文本内容影响。底层技术类报道通常涉及银行对金融科技基础设施、核心算法、技术平台的投入或合作新闻, 与应用场景类报道(聚焦具体产品/渠道落地)在媒体语调基调上可能存在系统性差异——例如底层技术报道更偏技术中性描述, 应用场景报道更易带有客户体验评价色彩, 该分类切分正是为了检验此类差异是否存在。本列与 you_2018_idf_tone_app_ctx 之差(tech − app 或 app − tech, 取决于具体分析设计)是 P4 论文中语调层面的"技术—应用语调差距"(tone gap)辅助测度之一, 与 P4 主轨 llm_vote_tone_tech_full / llm_vote_tone_app_full 的差距测度(gap_raw, 见 pipeline/panel/encode.py 第 1340 行附近)构念呼应但方法学不同(词典 idf 加权 vs LLM 投票)。由于分类判据固定于 full 轨而测度改用 ctx 轨窗口, 使用者应留意本列反映的是"被 full 轨判定为底层技术类的文章, 在其实体窗口局部文本上"的语调水平, 若该子样本内 ctx 窗口与 full 全文的语义焦点出现偏离(如报道虽整体聚焦技术研发, 但实体窗口恰巧截取了与应用场景相关的段落), 本列与 tech_full 之间可能出现方向性差异, 属预期的轨间稳健性检验信息而非数据错误。

## VAR: you_2018_idf_tone_tech_full

【变体差分】
本列是 full 轨文本上、限定 innovation_locus_full 分类为"底层技术"子样本的 you_2018 idf 加权语调分均值, 是 tech 类别切分变体中判据轨与测度轨完全重合的版本(与 app_full 对称)。该列与 you_2018_idf_tone_app_full 是本家族识别策略中最直接可比的一对: 二者共享同一文本轨(full)、同一留篇门控口径、同一词典与 idf 权重方案, 唯一差异是子样本划分(底层技术 vs 应用场景), 因此二者之差最适合直接解读为"创新定位对报道语调的边际影响"而不掺杂轨道错位带来的额外噪声。计算上需通过 n_articles_tech + n_articles_app 与 n_articles_llm_valid 的恒等式校验(R6 口径, >= 而非严格相等)确保分类逻辑未静默漏记文章, 该校验位于 pipeline/panel/encode.py 的 _check_partition_identity 调用处。该列与家族基线 you_2018_idf_tone_full(未切分全样本)构成"总体 vs 类别条件"关系, 类别条件均值之和(按各自样本量加权)理论上应能还原总体均值, 可作为内部一致性检验的辅助线索, 但不构成必须满足的会计恒等式(因情感聚合是非线性的 idf 加权而非简单计数)。该列是本家族在留篇门控主轨、分类判据主轨完全重合意义下最"干净"的类别条件测度, 建议研究者在正文主表中优先使用该列而非 app_ctx/tech_ctx 或 app_ss/tech_ss 等轨间错位版本, 后者应留作附录稳健性检验, 以避免主表结果的识别逻辑因轨道错位而复杂化。

## VAR: you_2018_idf_tone_tech_ss

【变体差分】
本列在 ss 轨(银行∧金融科技同句窗口)文本上计算 you_2018 idf 加权语调分, 限定样本为 innovation_locus_full 分类为"底层技术"的文章子集, 分类判据同样固定于 full 轨、与本列测度所用的 ss 轨相互独立。ss 轨窗口最窄, 对底层技术类报道而言, 由于此类报道往往围绕技术术语本身展开而非直接讨论"银行"与具体金融科技应用场景的紧邻句子, 触发 ss_is_fallback 回退为全文语调的比例可能与应用场景类报道不同, 这是解读 tech_ss 与 app_ss 差异时需要额外留意的样本构成因素(回退比例本身不直接呈现在本列数值中, 需结合 ss_is_fallback 相关列交叉核实)。本列与 you_2018_idf_tone_tech_ctx、you_2018_idf_tone_tech_full 构成 tech 类别切分下的三轨并排组, 与 app 类别切分下的三轨并排组、以及无类别切分的基线三轨组共同构成本家族"三轨 × (无切分/app/tech)"共 9 列均值测度的完整矩阵, 该矩阵与 std/vw/mw/hw 等其余 12 列共同满足家族总列数 21 列; 类别判据(app/tech)与文本轨(full/ctx/ss)是两个不同后缀空间, 不可混淆(前者反映分类子样本, 后者反映文本抽取范围), codebook 推断函数需先剥离判据后缀再匹配轨道后缀, 避免误判。样本容量上, 该列同时受"底层技术类文章占比"与"ss 轨同句共现命中率"双重收缩影响, 是本家族 21 列中有效观测篇数最容易偏小的一列, 使用者在做面板回归或跨银行比较前, 建议先核查对应 bank-year 的 n_articles_tech 是否达到可接受的最小样本量, 对样本过少的观测应审慎处理(如设置最小篇数门槛后再纳入回归), 避免个别极端语调词命中被放大为系统性结论。

## VAR: you_2018_idf_tone_vw_ctx

【变体差分】
本列在 ctx 轨文本上, 用媒体提及密度(mention_density, 出自 stage 11 news_bank 的 news_salience 模块)对逐篇 you_2018 idf 加权语调分做"价值加权"(value-weighted, vw)聚合: sum(you_2018_idf_score_w_ctx) / sum_mention_density(替换 0 为缺失以避免除零)。提及密度权重的构念含义是"一篇报道中目标银行被提及的强度/密集程度", 密集提及的报道被认为更能反映该报道对银行的真实关注度和态度强度, 因此在加权聚合时赋予更高权重, 相对等权聚合(you_2018_idf_tone_ctx, 每篇文章无论提及密度高低都算一票)更强调"报道内容与银行的相关强度"而非"报道数量"。vw 加权与 mw(媒体权威)、hw(时间衰减)三者在权重来源上完全独立: vw 权重取决于单篇文章内部的提及密度(文本内在特征), mw 权重取决于发布媒体的外部声誉分层(元数据特征), hw 权重取决于报道发布时点相对观测窗口的新近性(时间特征), 三者构念互不重叠, 因此三个加权口径应各自独立报告为并排稳健性检验, 不应合并为单一复合权重。ctx 轨的实体窗口本身已对文本做了一次围绕银行与金融科技相关实体的截取, 在此基础上再叠加提及密度加权, 相当于对"局部相关文本"再按"提及强度"做二次筛选式加权, 因此 vw_ctx 相比 vw_full 通常对稀疏提及、边角带过的报道更不敏感, 是家族内对噪声观测抵抗力相对较强的一列, 适合作为基线均值的稳健性上限参照。

## VAR: you_2018_idf_tone_vw_full

【变体差分】
本列在 full 轨文本上用媒体提及密度对逐篇 you_2018 idf 加权语调分做价值加权聚合: sum(you_2018_idf_score_w_full) / sum_mention_density, 是 vw 加权口径在留篇门控主轨上的版本。这是本家族继基线均值(you_2018_idf_tone_full)之后最常被用作辅助稳健性检验的加权变体之一, 因为提及密度加权直接对应"报道强度是否影响语调可信度"这一实证问题——若某银行仅因个别边角提及而被打上强烈正负标签, 等权聚合会让这类噪声观测与深度报道观测同权重进入均值, 而 vw 加权能在一定程度上压低这类低相关性观测的影响。该列与家族内 mw_full(媒体权威加权)、hw_full(时间衰减加权)在 full 轨上构成三种加权哲学的横向对照组, 三者共享同一分子(you_2018 idf 逐篇语调分)但分母权重来源完全不同, 是检验"语调结论对不同加权假设是否稳健"的标准配置, 三者数值高度一致时可增强对基线均值结论的信心, 出现分歧时需具体分析何种加权假设更贴合研究问题。实证写作中常见的呈现方式是把 you_2018_idf_tone_full 及其 vw/mw/hw 三个加权变体并列成一张稳健性附表, 逐列汇报同一自变量在不同加权假设下的回归系数与显著性, 若结果在符号和量级上基本一致, 可在正文中简要陈述"结果对加权方案选择稳健", 并将完整附表放入附录供审稿人核查, 而非仅报告其中最显著的一列。

## VAR: you_2018_idf_tone_vw_ss

【变体差分】
本列在 ss 轨(银行∧金融科技同句窗口)文本上用媒体提及密度对逐篇 you_2018 idf 加权语调分做价值加权聚合: sum(you_2018_idf_score_w_ss) / sum_mention_density。该列组合了"局部语境测度"(ss 轨聚焦银行与金融科技实体紧邻共现的文本)与"提及强度加权"(vw)两层稳健性设计, 分母 sum_mention_density 在三轨间共享同一套提及密度定义(该密度是基于文章整体提及情况估计的, 不因文本抽取轨道切换而重新计算), 因此 vw 加权的分母口径在 full/ctx/ss 三列间是一致的, 差异主要来自分子(不同轨文本上算出的逐篇 idf 语调分乘以提及密度权重后求和)。ss 轨遵循镜像 ctx 的回退语义, 无同句共现的文章其 content_ss 回退为全文, 该篇对分子的贡献等价于用 full 轨语调分乘以其提及密度权重。本列与 you_2018_idf_tone_vw_ctx、you_2018_idf_tone_vw_full 构成 vw 加权口径下的三轨并排收尾组, 完整了本家族"三轨 × (无加权/std/vw/mw/hw/app/tech)"共 21 列的矩阵结构, 各维度正交独立、互为稳健性、禁止混入同一 over-identified 联合识别设定。作为窗口最窄且叠加了提及密度加权的一列, 该列在多数生产样本中触发同句回退比例较高的 bank-year 上会与 vw_full 高度相关(因为回退文章的提及密度权重实质上是对 full 轨语调分再加权), 而在回退比例较低的 bank-year 上则更能体现真实局部语境的强度加权信号, 建议在稳健性报告中同时披露各 bank-year 的回退比例分布作为解读辅助。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
