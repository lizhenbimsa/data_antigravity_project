---
family_id: F129
columns:
- bian_2021_pos_count_ctx
- bian_2021_pos_count_full
- bian_2021_pos_count_ss
unit: 篇数/计数 (count, 非负整数存为 double)
formula: "bian_2021_pos_count{track} = Σ_{i∈bank-year} 1[bian_2021_score_i{track} > 0]; 其中 track ∈ {_full, _ctx, _ss}, 逐篇指示列 _is_bian_2021_positive{track} = (bian_2021_score{track} > 0)"
producer: news_process/pipeline/panel/runner.py (逐篇极性指示 _is_bian_2021_positive{track}, 洗稿方法 D2) ; news_process/pipeline/panel/encode.py (bank-year 求和聚合)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (bian_2021_score_full / bian_2021_score_ctx / bian_2021_score_ss)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2024
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper No. 3446388
new_dois: []
---

## CORE

【构念与来源】
本家族度量一个银行-年度单元内, 被 Bian et al. (2021) 中文金融情感词典判为正面基调的报道篇数。它不是语调分值 (tone), 也不是词频, 而是一个整数计数: 把落在该银行该年度的每一篇金融科技相关报道逐篇过一遍 Bian 词典打分, 分值严格大于零者记为一篇"正面报道", 然后在银行-年度层面对这些正面报道求和。因此该列回答的是"这家银行今年有多少篇被此词典判正的报道", 与均值型语调列 (bian_2021_tone) 回答的"平均基调多正"是两个不同构念: 前者随报道体量放大, 后者对体量归一。计数口径的价值在于它保留了绝对信息量维度 — 一家高曝光银行即便平均语调平平, 其正面报道的绝对篇数仍可能远高于低曝光银行, 这一"极性事件的绝对多寡"正是计数列独有的、被均值列抹去的信号。

【方法学与计算】
计算分两级。第一级在报道层 (runner.py 的洗稿/极性指示模块, 对应方法 D2 "单个词典"分支): 对每篇报道读取上游 stage 22 产出的逐篇词典分 bian_2021_score{track}, 构造二值指示 _is_bian_2021_positive{track} = 1[bian_2021_score{track} > 0]。阈值取严格大于零, 即净极性偏正即计入, 零分与负分均不计入正面篇 (负面篇由对称的 _is_bian_2021_negative 另行编码, 供下游分歧度指标使用)。第二级在银行-年度层 (encode.py 的聚合字典): 对该指示列按银行-年度做 sum 求和, 得到 bian_2021_pos_count{track}。求和而非取均值是该列与 bian_2021_pos_frac (占比) 的分野。底层的 Bian 词典分本身由词典法状态机对分词后的文本逐 token 匹配情感词、叠加否定翻转/程度副词/转折三条语言学规则后归一化得到; 但对本计数列而言, 起决定作用的只是该篇净分的符号 (是否为正), 规则细节仅通过影响符号间接作用。存储类型为非负整数, 面板落盘为 double 以统一 schema。

【文献定位】
计数型文本度量在金融实证中有独立的方法学传统。Cohn, Liu 与 Wardlaw (2022) 在 Journal of Financial Economics 上系统论证了金融研究中计数 (及类计数) 数据的建模要点 — 计数变量的分布形态、零膨胀与体量共变问题不同于连续型均值变量, 应对应地选择估计量与稳健性处理; 本家族作为篇数计数列, 其下游进入回归时正应遵循该文的计数数据规范, 而非套用连续语调列的处理。词典本体方面, Bian, Jia, Li 与 Yan (2021) 构建了面向会计与金融文本分析的中文金融情感词典, 弥补了英文 Loughran-McDonald 词典在中文语料上的水土不服; Ma, Zhang 与 Zhang (2024) 进一步构建面向中国国内投资者的细粒度中文情感词典 (CN-FSD), 与 Todd, Bowden 与 Moshfeghi (2024) 对金融文本情感分析文献的综述共同勾勒出中文金融情感词典这一活跃分支。在银行媒体情感的应用侧, Fang, Wang, Wang 与 Yuan (2024) 以中国银行为样本证据媒体情感影响存款稳定与银行系统性风险, Chen, Goldstein, Huang 与 Vashishtha (2022) 论证银行透明度与存款流动的关联, Li 与 Luan (2025) 则从新闻分歧度角度刻画情感信号的横截面含义 — 这些工作共同支撑了"以词典法对银行相关报道逐篇定性、并在银行-年度聚合"这一测度路径的构念效度。

## VAR: bian_2021_pos_count_ctx

【变体差分】
本列是三轨中的实体窗轨 (ctx)。它与家族其它两列的唯一差异在底层文本口径: ctx 轨的报道文本取标题 prepend 后的正文中围绕目标实体 (银行/金融科技词) 命中位置的上下文窗口 (content_ctx), 而非整篇正文。因此 bian_2021_pos_count_ctx 统计的是"在实体上下文窗口内被 Bian 词典判为净正面的报道篇数": 只有当窗口内文本的词典净分大于零时该篇才计入。相对 full 轨, ctx 轨剥离了与银行/金科主体无关的段落, 计数因此更聚焦于主体邻近语境的极性, 通常篇数不高于 full 轨 (窗口是全文子集, 且窗内可能不含情感词而落为零分不计入)。在识别框架上, 三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同轨的计数混进同一 over-identified Hansen J 方程 — ctx 轨在此定位为主结果 (full) 的稳健性对照轨, 检验极性计数是否被"主体邻近 vs 全文"的文本切分口径所驱动。留篇门控采 full-only 口径 (一篇报道是否算作该银行该年度的一篇金融科技报道只看 full 轨判定), ctx 轨为 conditional-on-full 测度, 其行宇宙是 full 留篇集的子集, per-track 计数照算。需强调 ctx 与 full 的差值本身携带信息: 当某银行在 full 轨正面篇数远高于 ctx 轨时, 说明其正面基调多来自与银行/金科主体不直接相邻的段落, 提示这类正面报道的"主体相关性"较弱; 研究者可据此把 ctx 计数作为更保守的暴露度量。ctx 轨的窗口切分口径与 stage 13 共现硬过滤是两套不同判据, 不可互相复用。

## VAR: bian_2021_pos_count_full

【变体差分】
本列是三轨中的全文轨 (full), 亦是本家族概念上的 canonical 轨。其底层文本为标题 prepend 后的整篇正文 (content_full), 覆盖报道全文而非任何子窗口。bian_2021_pos_count_full 因此统计的是"整篇被 Bian 词典判为净正面 (词典净分大于零) 的报道篇数"在银行-年度上的求和。由于全文包含的候选情感词最多, 该轨的正面篇数通常是三轨中最高的, 对报道体量的敏感度也最强 — 高曝光银行在此列上的读数会显著放大。full 轨承担双重角色: 一是留篇门控的唯一裁决轨 (full-only 口径, 2026-06-29), 即一篇报道是否被认定为该银行该年度的一篇金融科技报道只依据 full 轨判定, ctx/ss 两轨的行宇宙均是 full 留篇集的子集; 二是本家族主结果轨, ctx/ss 相对它为稳健性对照。与均值型语调列 (bian_2021_tone_full) 相比, 本列不对报道篇数归一, 保留绝对极性事件的多寡信息。作为体量敏感的绝对计数, full 轨读数在跨银行比较时需与曝光量 (总报道数) 联合解读, 或按 Cohn, Liu 与 Wardlaw (2022) 对计数数据的建议在下游回归中显式处理体量共变; 单看本列的横截面高低易把"曝光多"误读为"基调好"。三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

## VAR: bian_2021_pos_count_ss

【变体差分】
本列是三轨中的同句轨 (ss)。其底层文本取标题 prepend 后正文中"银行∧金融科技词同句共现"的句子及其前后 N 句窗口 (content_ss, 窗口半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。因此 bian_2021_pos_count_ss 统计的是"在银行与金融科技主体同句共现的紧邻语境内被 Bian 词典判为净正面的报道篇数": 只有当该窄语境文本的词典净分大于零时该篇才计入。ss 轨是三轨中语境最紧、约束最强的口径, 意在捕捉恰好在银行与金科议题交汇处的极性表态, 篇数通常最低。回退语义镜像 ctx 轨: 若某篇不存在银行∧金科同句共现, 则 content_ss 优雅回退为整篇正文并置 ss_is_fallback=True (与其余轨共享 n_articles 分母); 若金融科技词表整体缺失 (FINTECH_AC=None) 则 *_is_fallback 全 True 优雅降级。识别定位与另两轨一致: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 留篇门控仍为 full-only, ss 为 conditional-on-full 的稳健性对照轨, 检验极性计数是否被"同句紧邻 vs 全文"的语境宽窄所驱动。由于回退机制的存在, ss 计数在同句共现稀疏的银行-年度会因大量回退篇而向 full 口径靠拢, 解读时应结合 ss_is_fallback 的占比判断该读数究竟反映紧邻语境极性还是回退后的全文极性; 在共现丰富的单元, ss 计数才真正体现银行与金科议题交汇处的正面表态密度。ss 与 ctx 虽同为约束轨, 但 ss 的同句判据比 ctx 的实体窗更严, 两者属规格稳健性并排关系, 不设 FWER 模板。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Ma, Y., Zhang, T., & Zhang, P. (2024). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
