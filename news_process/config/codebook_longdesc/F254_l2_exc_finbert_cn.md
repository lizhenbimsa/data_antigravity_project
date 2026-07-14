---
family_id: F254
novelty_exempt_rationale: "exc_ 前缀的停刊媒体剔除稳健性变体家族, 是 finbert_cn 主情感测度在剔除疑似退出覆盖媒体子样本上的技术性排除变体 (镜像全样本口径), 其测度定义 (FinBERT 情感概率、价值/跟风加权) 的学术依据已在母族 finbert_cn 及其锚定文献 (Huang et al. 2023; Tetlock 2007; Hassan et al. 2019) 中给出, 非独立新构念, 无需单独追新文献。"
columns:
- exc_finbert_cn_正面_ctx
- exc_finbert_cn_正面_full
- exc_finbert_cn_正面_hw_ctx
- exc_finbert_cn_正面_hw_full
- exc_finbert_cn_正面_hw_ss
- exc_finbert_cn_正面_ss
- exc_finbert_cn_正面_w_ctx
- exc_finbert_cn_正面_w_full
- exc_finbert_cn_正面_w_ss
unit: 概率均值 (无量纲, ∈[0,1]; 加权变体为未归一化的概率×权重之样本均值)
formula: "exc_finbert_cn_正面_X = mean_{i ∈ alive-media(b,y)} ( finbert_cn_正面_X_i ); alive = 非停刊代理媒体 (_is_ceased_media==0); base X = P(正面) softmax 概率, _w = P(正面)×value-weight, _hw = P(正面)×herd-decay-weight; 逐轨 track ∈ {_full,_ctx,_ss}"
producer: news_process/pipeline/panel/attention_media.py (exc_* 动态发现块; base 源概率 pipeline/sentiment/tone_berts.py stage 23; _w/_hw 加权变体现算于 pipeline/panel/runner.py 步骤 3b/3d)
upstream:
- 23_tone_berts.parquet (finbert_cn_正面{_full,_ctx,_ss} softmax 概率, base 未加权)
- pipeline/panel/runner.py 步骤 3b (value-weighted, 以 mention_density 为权重现算 finbert_cn_正面_w{track}, 未持久化进 23_tone_berts.parquet)
- pipeline/panel/runner.py 步骤 3d (herd-weighted, 以 herd_weight 三轨现算 finbert_cn_正面_hw{track}, 未持久化进 23_tone_berts.parquet)
- 40_panel_export_main (attention_media.detect_defacto_cessation → _is_ceased_media)
citations:
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.24963/ijcai.2020/622
  type: wp
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of IJCAI-20
  pages_or_artno: 4513-4519
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 2135-2202
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"剔除疑似退出覆盖媒体之后"银行年度层面的 FinBERT 正面情感强度。前缀 exc 取自 exclude ceased media (排除停刊媒体), 是一条停刊稳健性 (cessation robustness) 轨道; 中段 finbert_cn 指第一家 BERT 情感模型, 即以中文 bert-base-chinese 为骨干、在中文金融语料上微调的三分类情感器 (finbert_cn / fin_sent_zh / finbert2 三模型互为稳健性中的头一家); 尾段"正面"指该模型 softmax 输出中"正面"这一类的概率 P(正面)。因此家族的核心构念可一句话概括为: 只统计那些在样本期内始终保持对目标银行覆盖的"存活媒体"所发报道, 计算这些报道被 finbert_cn 判为正面的平均概率, 从而在样本框发生媒体退出时检验主情感测度的系数是否稳定。构念服务的经济学问题是媒体注意力与情感的信息效应, 而剔除停刊媒体则针对一个具体的样本选择威胁: 若某些媒体在样本期内停止对某银行的报道, 其早期正面或负面报道会被保留进面板, 造成幸存者偏差与覆盖强度的时变失真。

【方法学与计算】
计算链路分三步。第一步在 stage 23 (tone_berts) 对每篇报道跑 finbert_cn, 经窗口切分与置信度加权 softmax 得到三类概率, 物化文章级列 finbert_cn_正面_full / _ctx / _ss (三轨文本), 以及其价值加权变体 finbert_cn_正面_w{track} = P(正面)×value-weight (以文档长度/提及密度为权重, 锚 Hassan 等 2019) 与跟风衰减加权变体 finbert_cn_正面_hw{track} = P(正面)×herd-decay-weight (锚 Tetlock (2007))。第二步在 stage 40 的 attention_media 里以覆盖退出为停刊代理: detect_defacto_cessation 比对每家媒体对目标话题的首末出现年份, 把在样本末期不再出现的媒体标记为"疑似退出覆盖", 并可与 NPPA 停刊名录交叉验证 (交叉仅改报告标签, 不改排除集), 得到文章级哨兵 _is_ceased_media。第三步在动态发现块里, 对所有匹配情感前缀且未被显式排除的文章级得分列, 仅在存活媒体子集 (_is_ceased_media==0) 上按 target_bank×year 求均值, 生成 exc_ 前缀列。由此 exc_finbert_cn_正面{track} 是存活媒体报道正面概率的算术均值; 而 exc_finbert_cn_正面_w{track} 与 _hw{track} 是对应加权文章列的均值 (即概率×权重之均值, 属未归一化的辅助聚合, 定位为稳健性/审计存档而非首要归一化情感强度)。缺列时 (如 T=2 盘面 ss 轨或某加权列缺失) 由存在性守卫优雅跳过, 比例/情感类列按契约保持 NaN 不零填。

【文献定位】
测度骨架承接金融文本情感三角。词典法一支以 Loughran 和 McDonald (2011) 为代表, 指出通用情感词典在金融语境的误分类, 催生领域专用词典; 机器学习一支中 Frankel、Jennings 和 Lee (2022) 系统比较了机器学习与词典法在披露情感上的表现, 说明二者各有偏误、宜互为稳健。BERT 类金融情感器由 Huang、Wang 和 Yang (2023) 与 Liu 等 (2020) 奠定, 本家族所用 finbert_cn 即属此谱系。媒体情感的经济后果自 Tetlock (2007) 起被系统检验, 他以媒体悲观语气预测收益与成交, 确立"媒体情感承载增量信息"这一命题。在中国制度背景下, You、Zhang 和 Zhang (2018) 刻画了媒体报道权力的分配, Fang 等 (2024) 进一步给出媒体情感影响存款稳定与银行系统性风险的证据, 二者共同支撑"银行相关媒体情感有真实经济后果、故其测量的样本稳健性值得单列检验"的论证。停刊剔除的因果依据在于报纸退出会造成地方监督真空, 本家族以话题覆盖退出为其保守代理。需强调本家族与主情感轨、与 fin_sent_zh / finbert2 两模型的对应家族各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三模型或停刊/全样本口径混入同一 over-identified Hansen J; 三轨 full/ctx/ss 同理, 各自并排、不得混入同一过度识别检验; ss 轨回退语义镜像 ctx (无银行与金科同句共现时退回全文 body), 留篇门控口径与 full-only 一致。

## VAR: exc_finbert_cn_正面_ctx

【变体差分】
本列是 ctx 轨、无加权 (base) 的停刊剔除正面概率均值。相对家族 canonical, 其两处差分为: 其一, 文本轨道取 ctx 而非 full。ctx 轨的文章级源概率来自 finbert_cn 在"标题 prepend + 实体上下文窗口"文本上的推断, 即只保留目标银行实体附近的语句窗口, 剔除与银行无关的段落, 使情感信号更贴近银行主体, 但代价是可能截断跨段的情感线索; full 轨则吃标题加全文正文。其二, 加权维度取 base, 即对存活媒体报道的 P(正面) 直接求算术均值, 每篇报道等权, 不引入文档长度或跟风衰减权重, 因而语义最干净、可直接解读为"存活媒体正面报道的平均概率"。本列与 exc_finbert_cn_正面_full 构成同为 base 的跨轨对照, 与 exc_finbert_cn_正面_w_ctx / _hw_ctx 构成同轨的跨权重对照。在识别上, ctx 轨与 full 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混入同一 over-identified Hansen J; 停刊剔除口径亦与全样本口径并排, 用于检验主系数在媒体退出下的稳定性而非替代主测度。盘面 T=2 上 ctx 轨若样本稀薄可能出现零方差或缺格, 属预期退化, 生产 T=18 正常。就下游用法而言, 本列与全样本 ctx 正面概率并列进入稳健性表, 用以佐证主系数不由媒体退出的样本框收缩驱动; 与词典法、LLM 投票的对应停刊剔除列同属方法互证, 而非同一构念的重复度量, 不得并入同一回归右端造成人为共线。

## VAR: exc_finbert_cn_正面_full

【变体差分】
本列是 full 轨、无加权 (base) 的停刊剔除正面概率均值, 是本家族语义最完整、最接近 canonical 的一列。差分点在于文本轨取 full: 文章级源概率 finbert_cn_正面_full 由模型在"标题 prepend + 全文正文"上推断得到, 覆盖整篇报道的情感信号, 信息量最大, 但也最易混入与目标银行不直接相关的段落情感。加权维度取 base, 即对存活媒体 (非停刊代理) 报道的 P(正面) 逐篇等权求均值, 无价值加权、无跟风衰减加权, 故可直接解读为"剔除疑似退出媒体后, 银行年度正面报道概率"。留篇门控采 full-only 口径 (2026-06-29): 是否算作一篇银行金科报道只看 full 轨判定, 因此 full 轨的存活媒体样本即行宇宙的基准子集。本列相对全样本主情感测度的唯一处理是把 _is_ceased_media==1 的报道从分子分母中剔除, 用于回答"若媒体退出造成样本框收缩, 正面情感强度是否被系统性高估或低估"。在识别纪律上, full 与 ctx/ss 三轨各自 just-identified 并排、互为稳健性, 停刊与全样本两口径亦并排, 皆禁混入同一 over-identified Hansen J。本列与三家 BERT 模型的对应列 (fin_sent_zh / finbert2) 各自并排, 不分主次。作为 base full 轨, 本列在稳健性表中通常与全样本 finbert_cn 正面主测度直接对照, 二者系数的接近程度即媒体退出偏误大小的直接读数; 与 exc_ 词典法及 LLM 停刊剔除列的三角一致亦是常用的方法收敛证据。

## VAR: exc_finbert_cn_正面_hw_ctx

【变体差分】
本列是 ctx 轨、跟风衰减加权 (hw) 的停刊剔除正面聚合。相对家族 base 列, 差分在加权维度: 源文章列为 finbert_cn_正面_hw_ctx = P(正面)×herd-decay-weight, 其中跟风衰减权重锚 Tetlock (2007), 对同一事件的重复跟风报道按时间衰减降权, 以抑制"同一信息被多家媒体转载放大"造成的情感计数膨胀。因此本列衡量的是在剔除疑似退出媒体后、并对跟风转载降权后的正面情感聚合。需强调两点口径: 其一, 该列是概率与衰减权重之乘积在存活媒体上的算术均值, 属未归一化的加权聚合 (未除以权重之和), 定位为稳健性与审计存档, 不应与主情感强度直接比水平, 只宜比标准化系数的方向与显著性; 其二, 文本轨取 ctx (标题 prepend + 实体上下文窗口), 与 full/ss 各自 just-identified 并排、互为稳健性。跟风衰减加权、价值加权与 base 三种加权同为稳健性梯子的并排臂, 不分主次, 三者禁混入同一 over-identified Hansen J。ctx 轨在 T=2 盘面可能零方差退化, 生产 T=18 恢复正常, 此为预期。与 base 的 ctx 列相比, 本列剥离了转载放大成分, 因此在跟风密集的年份两列会显著背离, 这一背离本身即跟风结构对情感聚合影响的诊断信号, 而非误差; 本列不与 base 列同入右端。

## VAR: exc_finbert_cn_正面_hw_full

【变体差分】
本列是 full 轨、跟风衰减加权 (hw) 的停刊剔除正面聚合。文本轨取 full (标题 prepend + 全文正文), 加权取跟风衰减: 源文章列 finbert_cn_正面_hw_full = P(正面)×herd-decay-weight, 衰减权重锚 Tetlock (2007), 用于对同一事件被多家媒体重复跟风报道的情形按时间衰减降权, 从而使正面情感聚合不被转载放大所主导。相对 base 的 full 列, 本列在等权均值之上引入了跟风结构信息; 相对 hw_ctx, 本列吃全文而非实体窗口, 覆盖情感信号更全。该列同样是概率×权重在存活媒体子集上的算术均值, 未按权重和归一化, 因此属未归一化加权聚合, 定位稳健性/审计, 只比标准化系数不比水平。停刊剔除的作用是检验在媒体退出下、经跟风降权后的正面情感是否稳定。识别纪律: full/ctx/ss 三轨与 base/w/hw 三加权臂各自 just-identified 并排、互为稳健性、不分主次, 一律禁混入同一 over-identified Hansen J; 与 fin_sent_zh / finbert2 两模型对应列亦各自并排。留篇门控 full-only, 存活媒体样本以 full 轨判定为基准子集。本列在稳健性梯子中与 base full、value 加权 full 三臂并排, 用以证明正面情感的经济含义既不由跟风转载放大所主导, 也不由停刊媒体样本框所驱动; 三臂各自单独进模型, 互为佐证而不叠加。

## VAR: exc_finbert_cn_正面_hw_ss

【变体差分】
本列是 ss 轨、跟风衰减加权 (hw) 的停刊剔除正面聚合。ss 轨指"标题 prepend + 银行与金科同句共现窗口"文本: 只保留目标银行与金融科技词在同一句 (±N 句半径, 默认 1) 共现的语句, 是三轨中对"银行谈金科"这一构念最严的判定; 当某报道无银行与金科同句共现时, ss 轨回退语义镜像 ctx, 即 content_ss 退回全文 body、ss_is_fallback 置 True, 并与 n_articles 共享分母。加权维度取跟风衰减: 源列 finbert_cn_正面_hw_ss = P(正面)×herd-decay-weight, 锚 Tetlock (2007), 对跟风转载降权。因此本列是在最严同句共现子集上、剔除疑似退出媒体、并对跟风降权后的正面概率×权重之均值, 属未归一化加权聚合, 定位稳健性/审计存档, 只比标准化系数不比水平。本列与 hw_full / hw_ctx 构成同加权的跨轨对照, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混入同一 over-identified Hansen J。因 ss 判定最严, 盘面 T=2 上有效格更稀、易零方差或大面积回退, 属预期退化; 生产 T=18 上同句共现样本充足时恢复常态。本列把最严的同句共现语境、跟风降权与停刊剔除三重收窄叠加于一身, 因此是家族中信号最贴构念但样本最薄的一列, 定位为极端稳健性检验: 若主结论在此列仍方向一致, 则对语境、跟风与样本框三类扰动同时稳健。

## VAR: exc_finbert_cn_正面_ss

【变体差分】
本列是 ss 轨、无加权 (base) 的停刊剔除正面概率均值。文本轨取 ss (标题 prepend + 银行与金科同句共现窗口), 是三轨中最严的"银行谈金科"判定: 仅保留目标银行与金融科技词同句共现 (默认 ±1 句半径) 的语句喂入 finbert_cn; 若某报道无同句共现, ss 轨回退语义镜像 ctx, content_ss 退回全文 body 且 ss_is_fallback 置 True, 与 n_articles 共享分母。加权维度取 base, 即对存活媒体报道的 P(正面) 逐篇等权求均值, 语义为"剔除疑似退出媒体后, 银行与金科同句语境下正面报道的平均概率"。相对 exc_finbert_cn_正面_full / _ctx, 本列以最严语境换取最贴近构念的信号, 代价是有效样本更薄、回退比例更高。在识别纪律上, ss 与 full/ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 停刊与全样本口径亦并排, 皆禁混入同一 over-identified Hansen J。盘面 T=2 上 ss 轨常大面积缺格或零方差, 属预期退化, 生产 T=18 正常。本列亦与三家 BERT 模型对应列各自并排, 不分主次。作为 base ss 轨, 本列与 hw_ss、w_ss 构成同轨的跨加权对照, 用以在最严语境下分离等权、跟风降权与信息含量加权三种聚合口径对正面情感的影响; 三者各自 just-identified, 不叠加进同一右端。作为最严语境下的等权聚合, 本列在稳健性表中常与 full/ctx 的 base 列并排, 用以证明正面情感即便只取银行与金科同句共现的严判子集、并剔除疑似退出媒体, 其经济含义仍方向一致。

## VAR: exc_finbert_cn_正面_w_ctx

【变体差分】
本列是 ctx 轨、价值加权 (w) 的停刊剔除正面聚合。文本轨取 ctx (标题 prepend + 实体上下文窗口), 加权取价值加权: 源文章列 finbert_cn_正面_w_ctx = P(正面)×value-weight, 价值权重锚 Hassan 等 (2019), 以文档长度/提及密度为权重, 使篇幅更长、对目标银行提及更密集的报道在聚合中获得更大话语权, 抑制短讯与顺带提及对情感均值的稀释。因此本列衡量的是剔除疑似退出媒体后、按报道信息含量加权的 ctx 语境正面情感聚合。口径上须注意: 该列是概率×价值权重在存活媒体上的算术均值, 未按权重和归一化, 属未归一化加权聚合, 定位稳健性/审计存档, 只宜比标准化系数不比水平。相对 base 的 ctx 列, 本列引入信息含量维度; 相对 hw_ctx, 本列的权重来源是篇幅/提及密度而非跟风衰减, 二者正交。识别纪律: full/ctx/ss 三轨与 base/w/hw 三加权臂各自 just-identified 并排、互为稳健性、不分主次, 禁混入同一 over-identified Hansen J。ctx 轨在 T=2 盘面可能零方差退化, 生产 T=18 恢复正常。相对 base 的 ctx 列, 若两列显著背离, 说明短讯与顺带提及对等权均值有稀释作用, 长篇深度报道的正面倾向被价值加权凸显出来, 这一对照本身即报道信息含量异质性的诊断; 本列与 base、hw 两臂并列而不叠加。

## VAR: exc_finbert_cn_正面_w_full

【变体差分】
本列是 full 轨、价值加权 (w) 的停刊剔除正面聚合。文本轨取 full (标题 prepend + 全文正文), 加权取价值加权: 源列 finbert_cn_正面_w_full = P(正面)×value-weight, 价值权重锚 Hassan 等 (2019), 以文档长度/提及密度加权, 让信息含量更高的长篇、高提及密度报道在正面情感聚合中权重更大。相对 base 的 full 列, 本列以信息含量加权取代等权; 相对 w_ctx, 本列吃全文而非实体窗口, 覆盖情感信号最全但也最易混入无关段落; 相对 hw_full, 本列权重来源为篇幅/提及密度而非跟风衰减, 两条加权臂正交、互不替代。该列同为概率×价值权重在存活媒体子集上的算术均值, 未按权重和归一化, 属未归一化加权聚合, 定位稳健性/审计, 只比标准化系数不比水平。停刊剔除用于检验在媒体退出下、经价值加权后的正面情感是否稳定, 留篇门控采 full-only 口径。识别纪律: full/ctx/ss 三轨与 base/w/hw 三加权臂各自 just-identified 并排、互为稳健性、不分主次, 一律禁混入同一 over-identified Hansen J; 与 fin_sent_zh / finbert2 两模型对应列亦各自并排。作为 value 加权 full 轨, 本列是"信息含量加权"这一稳健性维度上覆盖最全的一列, 常与 base full、hw full 三臂并排, 共同证明正面情感的经济含义既不由篇幅结构、也不由跟风放大、更不由停刊样本框单独驱动。

## VAR: exc_finbert_cn_正面_w_ss

【变体差分】
本列是 ss 轨、价值加权 (w) 的停刊剔除正面聚合。文本轨取 ss (标题 prepend + 银行与金科同句共现窗口), 是三轨中最严的"银行谈金科"判定: 仅保留目标银行与金融科技词同句共现 (默认 ±1 句半径) 的语句; 无同句共现时回退语义镜像 ctx, content_ss 退回全文 body 且 ss_is_fallback 置 True, 与 n_articles 共享分母。加权维度取价值加权: 源列 finbert_cn_正面_w_ss = P(正面)×value-weight, 权重锚 Hassan 等 (2019), 以文档长度/提及密度加权。因此本列是在最严同句共现子集上、剔除疑似退出媒体、并按信息含量加权后的正面概率×权重之均值, 属未归一化加权聚合, 定位稳健性/审计存档, 只比标准化系数不比水平。相对 w_full / w_ctx, 本列以最严语境换取最贴近构念的信号, 代价是有效样本更薄、回退比例更高; 相对 hw_ss, 本列权重来源为篇幅/提及密度而非跟风衰减, 二者正交。识别纪律: 三轨与三加权臂各自 just-identified 并排、互为稳健性、不分主次, 禁混入同一 over-identified Hansen J。盘面 T=2 上 ss 轨常大面积缺格或零方差, 属预期退化; 生产 T=18 同句样本充足时恢复常态。本列把最严同句语境、信息含量加权与停刊剔除三重收窄叠加, 是价值加权臂中信号最贴构念但样本最薄者, 定位极端稳健性检验; 与 hw_ss、base ss 三者各自 just-identified 并排, 互为佐证而绝不并入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of IJCAI-20 No. 4513-4519 [Working Paper]. https://doi.org/10.24963/ijcai.2020/622
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
