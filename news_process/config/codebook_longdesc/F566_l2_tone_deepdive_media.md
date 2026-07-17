---
family_id: F566
columns:
- tone_deepdive_media_ctx
- tone_deepdive_media_full
- tone_deepdive_media_ss
unit: 语调得分 (连续, 落在约 [-1,1] 区间; 由文章级 LLM 三家投票语调分 llm_vote_score{track} 在 银行×年×深度期刊子样本内取算术均值聚合而成)
formula: 'tone_deepdive_media{track} = mean( llm_vote_score{track} | target_bank, year, _is_deepdive==1 ); _is_deepdive = 媒体(中文) ∈ DEEPDIVE 清单 (基于 NPPA 出版周期 ≥ 周报的非日刊出版物白名单)'
producer: pipeline\panel\attention_media.py (维度⑦深度期刊 vs 非深度分支; 列标签由 pipeline\panel\export.py 写入 dta 变量标签)
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss)
- 11_news_bank.parquet (target_bank)
- 00_preprocessing 媒体(中文) 出版物名称字段
citations:
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The information role of the media in earnings news
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving content to investor sentiment; The role of media in the stock market
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: Media sentiment, deposit stability and bank systemic risk; Evidence from China
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing enthusiasm; Media sentiment and the disciplining role of quarterly earnings announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: "10.1016/j.frl.2024.105128"
  type: "journal"
  authors: "Zhang, Z., & Shen, D."
  year: 2024
  title: "Not all the news fitting to reprint: Evidence from price-volume relationship"
  venue: "Finance Research Letters"
  vol: "62"
  pages_or_artno: "105128"
- doi: "10.1016/j.energy.2025.139126"
  type: "journal"
  authors: "Hua, X., Dong, D., Xu, Z., & Huang, W."
  year: 2025
  title: "Official media sentiments toward energy and equity returns: Evidence from China"
  venue: "Energy"
  vol: "340"
  pages_or_artno: "139126"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"深度期刊型媒体"对目标银行报道时所呈现的平均语调, 是媒体异质性谱系中按出版频率/深度划分的一个维度。构念动机来自媒体信息中介理论的一个基本区分: 不同出版周期的媒体在信息生产方式上存在系统性差异。日报/通讯社式媒体追求时效性, 多为事件驱动的即时转述, 信息密度低、原创分析少; 而周报/月刊/季刊等低频出版的深度期刊, 受版面周期约束无法追逐即时热点, 反而倾向于投入更多采编资源做行业研究、深度调查与专题分析, 原创信息创造的比例更高。Guest (2021, Journal of Accounting Research) 在盈余新闻语境下系统检验了媒体新闻原创性对信息含量的影响, 发现原创性越高的报道对公司治理与市场反应的边际信息贡献越大, 而深度期刊正是原创性生产的典型载体; 这为把出版周期 (深度期刊 vs 高频快讯) 当作媒体异质性的独立解释维度而非简单控制变量提供了直接依据。You, Zhang & Zhang (2018, The Review of Financial Studies) 关于"谁掌握了笔杆子的权力"的研究进一步表明, 媒体机构层面的固定属性 (包括出版形态与所有制) 会系统性地影响其报道对企业行为的实际约束力, 支持了本家族把出版周期视为媒体机构层面外生标签、而非报道内容内生产物的建模前提。本家族即把这一"深度期刊 vs 高频快讯"的区分移植到银行金融科技报道语境: 若深度期刊在报道银行时呈现出与日报/通讯社系统性不同的语调水平或语调分布, 就说明媒体出版频率本身携带了独立于议题内容之外的信息生产模式信号, 值得在 panel 回归中作为异质性维度单独处理, 而不能简单把全部媒体报道汇总成单一均值语调。

本家族与同批产出的 deepdive_media_frac (深度期刊报道占比)、tone_nondeep_media{track} (非深度期刊语调)、tone_gap_deepdive_nondeep{track} (深度-非深度语调缺口) 共同构成"出版频率维度⑦"的完整四件套; 姊妹维度⑧ (daily_media 高频日报) 采用完全平行的构造逻辑, 唯一区别是媒体分类标准从"周期≥周报的深度期刊清单 DEEPDIVE"换成"日报清单 DAILY"。两个维度理论上应大致互补但不严格互斥 (存在既非深度期刊也非日报的中间周期媒体), 故不可简单相加复原全样本均值。

【方法学与计算】
计算分两步。第一步在文章级判定媒体类型: 依据媒体(中文) 字段所记录的出版物名称, 对照 NPPA (国家新闻出版署) 登记的出版周期信息构造的 DEEPDIVE 静态清单 (周期 ≥ 周报的非日刊出版物), 生成二值指示列 _is_deepdive。这一分类是基于媒体机构属性的静态外生标签, 不依赖报道内容本身, 因而不会与报道语调产生同源内生性。第二步做分组聚合: 在已通过留篇门控 (llm_verified_full == True, full-only 口径, 2026-06-29 起生效) 的样本内, 按 target_bank × year 分组, 仅取 _is_deepdive == 1 的子样本, 对 llm_vote_score{track} (LLM 三家投票共识语调分, 三家为 gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 求算术均值, 得到 tone_deepdive_media{track}。若某银行-年内深度期刊报道篇数为 0, 该格自然产生 NaN (不做人为插补或借用全样本均值填充), 这是分组聚合的正常缺失, 反映样本在该维度上的稀疏性而非数据错误。

本家族存在三轨版本 tone_deepdive_media_full / _ctx / _ss, 对应文章文本三种不同的物化窗口: full 轨使用标题+全文正文, ctx 轨使用标题+目标实体窗口截取正文, ss 轨使用标题+银行∧金科同句 (或±N句窗口) 截取正文, 三轨物化于 stage 14 ctx_materializer。三轨语调分 llm_vote_score{track} 均来自 stage 21 三家 LLM 投票, 三轨在方法论上各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨语调分混入同一 over-identified Hansen J 检验框架。留篇门控是 full-only 口径: 一篇报道是否计入"银行金科报道"样本只看 llm_verified_full 一个判据, ctx/ss 轨道语调分是在 full 留篇集合的行宇宙子集上按各自轨道文本重新计算的测度/稳健性轨, 而非独立扩样。ss 轨若某篇报道内不存在银行∧金科同句共现, 则回退为使用全文 body 且标记 ss_is_fallback=True (镜像 ctx 轨的回退语义), 该回退样本仍计入 n_articles 分母参与本家族的分组均值计算, 不做剔除。

【文献定位】
出版周期作为媒体异质性代理变量在会计与金融文献中有明确渊源。Guest (2021, JAR) 系统区分了媒体报道在信息生产过程中"原创分析"与"转载聚合"两种不同的信息贡献方式, 在盈余公告场景下证明新闻原创性 (与出版深度高度相关) 是媒体信息含量的关键调节变量, 是本家族"深度期刊具有更强信息生产能力、故值得在报道语调上单独区分"这一理论假设与建模选择的直接文献来源, 支持了把出版周期作为独立异质性维度 (而非仅仅是控制变量) 纳入面板。在中国银行业媒体情感的具体应用场景, Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 直接以中国银行为研究对象构建媒体情感指标并考察其对存款稳定性与系统性风险的影响, 是本家族在研究对象 (中国银行) 与测度构念 (媒体语调) 两个维度上最贴近的同域文献。语调分本身的构造方法学 (LLM 三家投票语调) 则承袭 Tetlock (2007, The Journal of Finance) 开创的"文本语调可预测市场行为"这一实证传统 — Tetlock 首次证明基于报纸专栏构造的悲观语调指数具有独立于基本面的市场预测力, 为本家族"媒体语调是有信息含量的独立解释变量"这一前提提供了奠基性证据; Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体情感与盈余公告纪律效应的研究则是本 panel 内媒体权威性加权语调族 (llm_vote_tone_mw{track}) 的直接方法学锚点, 与本家族出版频率维度共同构成媒体异质性的多角度刻画。 近期文献进一步在两个方向上收紧了本家族的构造依据。Zhang 与 Shen (2024) 明确把新闻区分为转载/再刊与非转载两类, 并证明二者的价量含义不同, 表明一条报道究竟是原创产制还是二次分发本身即是携带信息的文章级属性, 直接支持本家族把出版周期 (深度原创 vs 高频转述) 视作独立信号维度而非冗余控制项的前提; 但其转载判定依赖新闻数据库自带的转载标记, 与本家族基于 NPPA 出版周期构造的 DEEPDIVE 静态名单判据完全不同, 且原文停在文章级并以价量关系为被解释变量, 未做主体-年度的语调均值聚合。Hua、Dong、Xu 与 Huang (2025) 以 BERT 对中国官方媒体的新能源报道文本构建官方媒体语调指数, 并检验其与权益回报及企业融资投资行为的关系, 为「按媒体机构属性切出子样本、在子样本内对文章级语调取均值」这一操作化范式提供了同域 (中文媒体) 的前沿存在性证据; 但其切分维度是媒体的官方属性而非出版周期, 情感由文本指数法而非三家 LLM 投票共识得到, 层级为行业与股票市场层面的日度指数而非 bank-year 面板, 故该文只锚定分层-组内聚合这一构造范式的可行性, 不构成深度期刊维度本身的文献出处。
## VAR: tone_deepdive_media_ctx

【变体差分】
本列取 llm_vote_score_ctx 作为聚合源, 即语调分来自 ctx 轨文本 (标题 + 目标实体窗口截取正文) 而非全文。ctx 轨是围绕目标银行实体做局部窗口截取, 意在剔除文章中与银行报道主题无关的段落干扰, 使语调分更聚焦于银行相关表述本身; 但其行宇宙仍是 full-only 留篇门控确定的同一批文章 (conditional-on-full), 分组聚合逻辑 (按 target_bank × year × _is_deepdive==1 取均值) 与 full 轨完全一致, 唯一差异在于输入的语调分测量口径。本列与 tone_deepdive_media_full、tone_deepdive_media_ss 三者互为稳健性并排比较, 不存在何者更优先的先验排序, 禁止在同一识别方程中把三轨语调分同时作为过度识别的工具或回归量混用。

从测量误差的角度理解, ctx 轨相较 full 轨的取舍是一种"精确度换覆盖面"的权衡: 截取实体窗口能够降低文章中与银行报道主题无关段落 (例如行业综述、宏观背景铺垫、其他企业案例) 对语调分的稀释效应, 使 llm_vote_score_ctx 更贴近"作者对该银行本身的评价倾向", 但代价是丢失了部分上下文信息, 在实体窗口划定不够精确的边界情形下可能引入截断误差。对深度期刊子样本而言, 由于此类报道篇幅往往更长、结构更复杂 (常见行业专题夹叙多家银行的写法), ctx 轨窗口截取的实际影响可能比日报快讯更明显, 这正是把 ctx 与 full、ss 并列作为独立稳健性轨而非相互替代关系的原因: 三者数值若在方向上一致, 增强了深度期刊语调测度对文本窗口选择的稳健性结论; 若出现系统性分歧, 则本身构成一个值得在异质性分析中报告的发现, 而非应当被"择优"掩盖的噪声。

## VAR: tone_deepdive_media_full

【变体差分】
本列取 llm_vote_score_full 作为聚合源, 即语调分来自 full 轨文本 (标题 + 完整正文), 是三轨中信息覆盖面最广的一轨, 也是留篇门控 (llm_verified_full) 直接依据的轨道 — 换言之, 本列聚合所用的分母 (深度期刊子样本内的篇数) 与门控判据同源, 是三轨中口径最内部一致的版本, 常被各 paper 主线用作 canonical/primary 测度 (镜像 P1 bank_fintech_tone 的 treatment.primary 切 full 轨的先例)。但按本项目「互为稳健性不分主次」的一般原则, 这里的"常用作 primary"是各 paper 层面的建模选择, 不代表本列在测度构念上优于 ctx/ss 两轨, 三者仍应并排报告。

full 轨对深度期刊子样本尤其重要的一点在于: 深度期刊报道往往篇幅更长、信息密度分布不均 (开篇铺垫背景、中段展开分析、结尾给出结论倾向), 全文语调分能够完整覆盖这种"渐进式表达"的语调轨迹, 不会因窗口截取而遗漏结论段落中最终成型的评价倾向; 相应地, full 轨也更容易被无关段落 (行业背景介绍、监管政策转述、其他机构对比) 稀释, 这是它与 ctx/ss 两轨形成稳健性对照的价值所在。留篇门控只在 full 轨上判定 llm_verified_full, 使得 tone_deepdive_media_full 在三轨中与"该篇文章是否算作一篇合格的银行金科报道"这一底层样本口径判据完全同源, 因此在解读三轨差异时, full 轨的分组分母 (深度期刊篇数) 与 ctx/ss 两轨完全一致 (行宇宙相同), 差异只来自输入语调分本身, 而非样本选择效应。

## VAR: tone_deepdive_media_ss

【变体差分】
本列取 llm_vote_score_ss 作为聚合源, 即语调分来自 ss 轨文本 (标题 + 银行∧金科同句共现窗口, 默认 ±1 句半径, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制)。ss 轨是三轨中文本窗口最窄、判定最严格的一轨, 只保留银行实体与金融科技词汇在同一句 (或邻近句窗口) 出现的局部文本, 用以逼近"报道确实在讨论银行与金融科技交集"这一更强的语境要求。若某篇文章在 full-only 门控下已计入样本, 但其内部并不存在银行∧金科同句共现, 则该篇的 content_ss 回退为使用全文 body (与 ctx 轨回退语义镜像一致), 并置 ss_is_fallback=True; 这类回退篇目仍正常计入本列所在银行-年-深度期刊子样本的均值分母, 不做单独剔除, 因为剔除会人为改变样本口径并可能引入选择性偏误。同样地, 本列与 full/ctx 两轨互为稳健性并排, 三者语调分严禁混入同一 over-identified Hansen J 识别框架。

ss 轨的构造原语 (extract_bank_fintech_cooccurrence, 严格同句判据) 与 stage 13 共现硬过滤所用的原语 (has_bank_fintech_cooccurrence_within_radius, ±1 句窗口判据) 是两个不同口径, 不可混用互证: stage 13 决定"这篇文章是否留在语料里", 而 ss 轨的同句判据决定"这篇文章内哪一段句子被用来算语调"。对深度期刊子样本来说, 由于篇幅长、话题夹杂多, 银行与金融科技词汇同句共现的比例通常低于日报快讯类简短报道, 因而 ss_is_fallback=True 的回退比例在深度期刊子样本中可能更高, 这是解读 tone_deepdive_media_ss 时需要留意的样本构成特征: 回退发生率本身不是缺陷, 而是该轨"窄化到严格共现语境"这一设计选择在长文本上的自然后果, 且回退篇目仍完整计入分组均值分母, 不改变分组样本量口径。

<!-- rendered-citations:begin -->
Guest, N. M. (2021). The information role of the media in earnings news. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Tetlock, P. C. (2007). Giving content to investor sentiment; The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk; Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm; Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Zhang, Z., & Shen, D. (2024). Not all the news fitting to reprint: Evidence from price-volume relationship. Finance Research Letters, 62, 105128. https://doi.org/10.1016/j.frl.2024.105128
Hua, X., Dong, D., Xu, Z., & Huang, W. (2025). Official media sentiments toward energy and equity returns: Evidence from China. Energy, 340, 139126. https://doi.org/10.1016/j.energy.2025.139126
<!-- rendered-citations:end -->
