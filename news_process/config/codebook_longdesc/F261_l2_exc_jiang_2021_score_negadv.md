---
family_id: F261
novelty_exempt_rationale: "exc_前缀=排除疑似停刊媒体的样本层稳健性变体, negadv=词典规则消融梯度变体(否定翻转+转折, 关闭程度副词), 二者均为姜富伟(2021)词典母族测度的技术性组合变体, 非独立新构念, 其测度定义学术依据已在母族词典文献与规则消融方法学(Taboada 2011)中给出。"
columns:
- exc_jiang_2021_score_negadv_ctx
- exc_jiang_2021_score_negadv_full
- exc_jiang_2021_score_negadv_ss
unit: 无量纲情感得分 (自归一化 tone, 排除疑似退出覆盖媒体后的 bank-year 均值)
formula: "exc_jiang_2021_score_negadv_{track} = mean_{i ∈ 该 bank-year 且 _is_ceased_media_i==0} jiang_2021_score_negadv_{track}(i); 其中 jiang_2021_score_negadv = 以姜富伟等 (2021) 中文媒体情绪词典打分, 仅启用『否定翻转 + 转折』两条语言学规则、关闭『程度副词』规则, 逐篇自归一化"
producer: news_process/pipeline/panel/attention_media.py (C.4 段动态发现; 文章级得分产于 news_process/pipeline/sentiment/tone_words.py)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_tone_words.parquet (jiang_2021_score_negadv_{full,ctx,ss})
- 40_panel_export_main 内 detect_defacto_cessation (_is_ceased_media 停刊代理旗标)
citations:
- doi: 10.1016/j.jfineco.2024.103910
  type: journal
  authors: Cao, S., Jiang, W., Wang, J., & Yang, B.
  year: 2024
  title: "From man vs. machine to man + machine: The art and AI of stock analyses"
  venue: Journal of Financial Economics
  vol: 160
  pages_or_artno: 103910
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, & 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是一条组合稳健性测度: 在剔除疑似退出覆盖 (停刊代理) 的媒体来源之后, 再以姜富伟等 (2021) 提出的中文媒体情绪词典对目标银行相关报道逐篇打分, 并把打分限定在『否定翻转 + 转折』两条语言学规则之下、关闭『程度副词』规则, 最后按 bank-year 聚合成年度均值。列名由三段语义拼装而成: 前缀 exc_ 标记这是排除停刊媒体后的稳健性口径 (cessation-robustness), 中段 jiang_2021_score_negadv 标记底层文章级得分所用的词典与规则消融变体, 末段轨道后缀 (_full / _ctx / _ss) 标记文本口径。因此本家族既承载"词典消融梯度"这一测量层面的稳健性维度, 又叠加"排除幸存者偏差媒体"这一样本层面的稳健性维度, 二者正交叠放, 服务于 Stata 端对主线情感系数的稳定性检验。

词典来源方面, 姜富伟等 (2021) 在《经济学(季刊)》上构建了面向中国资本市场的媒体文本情绪词表, 并证明媒体文本情绪对股票回报具有预测力; 该词典是本项目六部中文金融情绪词典之一, 词表事实源固定在 tone_dicts.json (不回读 dicts_excel 原始料)。规则消融方面, 本项目对三条语言学规则 (否定翻转 neg、程度副词 deg、转折 adv) 取全部非空子集物化为消融变体 {dict}_score_{raw, negonly, degonly, advonly, negdeg, negadv, degadv}, 共 7 个非全规则变体; 全三规则同开的那一档即无后缀 canonical 得分。negadv 变体因此精确等于"开否定翻转、开转折、关程度副词"的那一格。样本层面的排除口径来自 detect_defacto_cessation: 该函数以"话题覆盖退出"作为报纸停刊的保守代理 (proxy), 把在样本期内疑似不再覆盖该银行话题的媒体来源打上 _is_ceased_media 旗标, 下游一律以"疑似退出覆盖媒体"的保守剔除口径解读, 不可在论文中表述为严格的出版停刊 (publication cessation) 口径。

【方法学与计算】
计算分两层。第一层在文章级 (stage 22 tone_words): 对每篇报道的相应轨道文本, 用 jiang_2021 词表匹配情绪词, 在词到句的合成中启用否定翻转与转折两条规则、关闭程度副词加权, 得到逐篇自归一化的 jiang_2021_score_negadv_{track}。由于各消融变体各自归一化, 它们之间是非可加分解 (audit MATH-1: 高度共线, 逐篇相关系数约 0.99), 因此报告时只报相关而不并入同一线性分式。第二层在面板级 (attention_media.py C.4 段, 步骤 6c, 纯 CPU、零 API、零 LLM): 先由 detect_defacto_cessation 标注 _is_ceased_media, 再取 df_alive = 未停刊子集, 按 (target_bank, year) 分组对文章级得分求算术均值, 通过左连接并入年度面板。C.4 段以 _SCORE_PATTERNS 前缀动态发现所有情感列 (含 LLM 投票、各厂 LLM、六部词典、BERT), jiang_2021_score_ 是其中之一; 已加权变体 (_w / _mw_ / _idf_) 与已在 C.3 单列处理的 llm_vote_score_ 被显式跳过, 避免重复。空媒体子集下该 bank-year 留 NaN (情感类按契约保持缺失, 不连带零填, 以区别于 n_articles_exc 这类计数列的 Σ over ∅ = 0 零填契约)。

三条轨道口径遵循项目统一定义: full = 标题 prepend 后的标题+正文全文; ctx = 标题+实体上下文窗口; ss = 标题+银行与金融科技同句共现窗。留篇门控自 2026-06-29 起为 full-only: 是否算作"一篇银行金科报道"只看 llm_verified_full, ctx/ss 降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。ss 轨采用镜像 ctx 的回退语义: 当某篇无银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 与 ctx 共享同一 n_articles 分母。三轨得分各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨 (或 negadv 与其余六个消融变体) 混进同一 over-identified Hansen J; 消融梯度与轨道口径正交, 不交叉。

【文献定位】
词典与规则的方法学定位有清晰的谱系。姜富伟等 (2021) 是本家族底层词表的直接来源, 其贡献在于把媒体文本情绪构造成对中国股票回报有预测力的信号; 同一作者群的 Jiang, Lee, Martin, & Zhou (2019, 顶刊 Journal of Financial Economics) 在管理者情绪与股票回报的框架下, 从更一般的层面论证了文本情绪测度的资产定价含义, 为本项目采用文本情绪作为核心构念提供了顶刊级支撑。就"词典法 vs 机器学习"的方法论选择而言, Frankel, Jennings, & Lee (2022, Management Science) 系统比较了披露情绪的词典法与机器学习法, 说明二者各有偏误、宜互为稳健; 这与本项目让词典、LLM 三家、BERT 三模型各自 just-identified 并排、互为稳健性的设计一脉相承。Du, Huang, Wermers, & Wu (2022, Review of Finance) 构建的中文金融情绪词典进一步论证了语言与领域特异性对情绪测度的重要性, 支持本项目并置多部中文词典而非仅套用英文 L&M 词表。Cao, Jiang, Yang, & Zhang (2023, Review of Financial Studies) 与 Cao, Jiang, Wang, & Yang (2024, Journal of Financial Economics) 则从"机器在听/人机协作"的角度提示了文本测度在 AI 时代的新内生性来源, 为把情绪测度当稳健性梯子而非单一 headline 提供了动机。语言学规则层面, Taboada 等 (2011) 系统阐述了否定、程度与转折 (adversative) 等上下文修饰对词典法极性合成的影响, 正是本项目把这三条规则做全子集消融的方法学依据; negadv 变体所关闭的程度副词规则与所保留的转折规则, 其取舍效果即可在本梯子内直接观测。 就其中否定一条的可测性而言, Naldi 与 Petroni (2023) 以人工构造测试集提出了专门评估词典法情感工具否定检测与处理能力的方法, 并实证发现各工具表现差异显著, 说明否定处理是词典法内部可被单独测量、单独失效的模块; negadv 臂保留否定翻转而关闭程度副词, 正是把这一模块的贡献单列出来的操作, 边界在于原文为英文通用领域的否定检测准确率评测, 本族并不评测准确率, 而是把规则开/关作为中文金融新闻语料上的一条并排稳健性臂。exc_ 前缀所做的「剔除疑似退出覆盖媒体后再行银行-年度聚合」亦有其现实动机: Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 表明媒体退出是真实且有经济后果的样本组成变化; 边界在于该工作论文尚未经同行评审, 其停刊判定取自外部事件数据并用于识别冲击, 而本族 ceased_set 是由 detect_defacto_cessation 自语料内部推断的保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 用途仅限稳健性子样本。
## VAR: exc_jiang_2021_score_negadv_full

【变体差分】
本列是三轨中的 full 轨: 文章级 jiang_2021_score_negadv_full 在标题 prepend 后的完整标题+正文文本上计算, 再对剔除停刊媒体后的存活子集按 bank-year 求均值。full 轨在项目中具有特殊地位——自 2026-06-29 起留篇门控为 full-only, 即一篇报道是否被计入银行金科报道宇宙, 只由 llm_verified_full 判定; 因此 full 轨的行宇宙就是留篇集本身, 而非其子集。本列与家族内 canonical 全规则得分 (否定翻转+程度副词+转折三规则同开) 的差别仅在规则消融档位: 本列关闭程度副词加权, 只保留否定翻转与转折两条规则, 由此隔离"程度副词是否参与极性合成"对情绪测度的边际影响。本列与 _ctx / _ss 两轨的差别在文本口径 (全文 vs 实体窗 vs 同句共现窗); 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨或本 negadv 变体与其余六档消融变体混进同一 over-identified Hansen J。与不排除停刊媒体的普通 jiang_2021 情绪均值相比, 本列的分母是存活媒体子集, 对幸存者偏差敏感; 空存活子集时按情感列契约保持 NaN, 不零填, 以区别于 n_articles_exc 计数列 Σ over ∅ = 0 的零填契约。就构念解读而言, 本列回答的问题是: 当把疑似退出覆盖的媒体从样本中保守剔除、且只让否定翻转与转折两条规则参与极性合成 (关闭程度副词加权) 时, 目标银行在该年度所获媒体报道的整体情绪基调仍是否稳定。若本列与 canonical 全规则口径、以及与不排除停刊的普通口径的系数在 Stata 端保持同号同量级, 即构成对主线情感系数的双重稳健性证据 (测量层面消融 + 样本层面剔除)。full 轨因承担 full-only 留篇门控, 是本家族信息量最饱满、退化风险最低的一轨, 通常作为该消融变体首要报告轨。

## VAR: exc_jiang_2021_score_negadv_ctx

【变体差分】
本列是三轨中的 ctx 轨: 文章级 jiang_2021_score_negadv_ctx 在标题+实体上下文窗口文本 (content_ctx, 已 prepend 标题) 上计算, 再对剔除停刊媒体后的存活子集按 bank-year 求均值。相对 full 轨, ctx 轨把词典打分限定在目标实体附近的上下文窗内, 削弱了长文中与银行金科无关段落对情绪测度的稀释; 在留篇门控 full-only 的框架下, ctx 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 逐轨列照算但不参与是否留篇的判定。本列与家族 canonical 全规则得分的差别同样只在消融档位——关闭程度副词、保留否定翻转与转折两条规则; 与 _full / _ss 两轨的差别在文本口径。三轨与七档消融变体各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 消融梯度与轨道口径正交不交叉。样本层面仍叠加排除停刊媒体的稳健性口径, 对存活子集为空的 bank-year 保持 NaN 而非零填, 以区别于 n_articles_exc 计数列的零填契约。ctx 轨的价值在于对冲 full 轨的一个已知风险: 长篇报道里与目标银行金科议题无关的段落会稀释情绪信号, 而实体上下文窗把打分锚定在实体邻近, 使情绪测度对报道主旨更敏感。因此当 full 轨与 ctx 轨系数一致时, 可推断主线情绪效应不是由无关段落的噪声驱动; 二者背离则提示应关注上下文窗口宽度这一测量选择。与家族其余六档消融变体一样, 本列自归一化、与相邻档位高度共线 (逐篇相关约 0.99), 报告时只报相关不并入同一线性分式。

## VAR: exc_jiang_2021_score_negadv_ss

【变体差分】
本列是三轨中的 ss 轨: 文章级 jiang_2021_score_negadv_ss 在"标题+银行与金融科技同句共现窗"文本 (content_ss, 已 prepend 标题) 上计算, 再对剔除停刊媒体后的存活子集按 bank-year 求均值。ss 轨口径最严, 只截取银行与金科在同一句 (可含 ±N 句半径) 共现的片段。其回退语义镜像 ctx: 当某篇报道不存在银行与金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享同一 n_articles 分母; 若金科自动机为空则 *_is_fallback 全 True 优雅降级。在留篇门控 full-only 框架下, ss 轨同为 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集。本列与家族 canonical 全规则得分的差别只在消融档位——关闭程度副词、保留否定翻转与转折; 与 _full / _ctx 两轨的差别在文本口径。三轨与七档消融变体各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 消融梯度与轨道口径正交不交叉。dev T=2 上 ss 轨常因样本极稀而退化 (存活子集内可能无同句共现篇), 相应 bank-year 按情感列契约保持 NaN, 属预期而非缺陷; 生产 T=19 语料下正常取值。ss 轨在三轨中口径最严、对"银行与金科真正被同句讨论"这一事件的针对性最强, 因此它剔除的是那些仅在同一篇文章里松散并置、并未在句法层面建立关联的报道; 由此本列可视为对 full/ctx 的高特异性稳健性锚。当 full、ctx、ss 三轨系数一致时, 说明主线情绪效应对"共现的紧密程度"这一测量维度不敏感, 结论稳健; 若 ss 轨在有效样本上给出方向一致但幅度更大的估计, 通常提示同句共现片段承载了更纯净的银行金科情绪信号。与家族其余消融档位同理, 本列自归一化、与相邻档位高度共线, 报告只报相关不并入同一线性分式; 样本层面仍叠加排除停刊媒体口径, 空存活子集保持 NaN 不零填。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Wang, J., & Yang, B. (2024). From man vs. machine to man + machine: The art and AI of stock analyses. Journal of Financial Economics, 160, 103910. https://doi.org/10.1016/j.jfineco.2024.103910
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
