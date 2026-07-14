---
family_id: F467
columns:
  - nf_headline_frac
  - nf_n_articles
unit: nf_n_articles=计数(篇, 非负整数); nf_headline_frac=比率(proportion, [0,1], 全年无报道则未定义为 NaN)
formula: "nf_n_articles = count(Non-Fintech 银行报道去重后行数 | target_bank, year); nf_headline_frac = mean(target_bank_in_title) over 该 (target_bank, year) 内全部 Non-Fintech 行"
producer: news_process/pipeline/falsification/controls.py::aggregate_non_fintech
upstream:
  - 12_fintech_news_full.parquet (stage 12 过滤前全量银行新闻, 与 11_bank_news 逐行 1:1)
  - 40_article_bank_level.parquet (已进面板的金融科技文章)
  - 40_panel_yearly.parquet
citations:
  - doi: 10.1016/j.jacceco.2021.101455
    type: journal
    authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
    year: 2022
    title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
    venue: Journal of Accounting and Economics
    vol: 73
    issue: 2-3
    pages_or_artno: 101455
  - doi: 10.1016/j.jfineco.2024.103957
    type: journal
    authors: Vives, X., & Ye, Z.
    year: 2025
    title: "Information technology and lender competition"
    venue: Journal of Financial Economics
    vol: 163
    pages_or_artno: 103957
  - doi: 10.1016/j.jempfin.2025.101670
    type: journal
    authors: Chen, Z., Li, Z., Liu, J., & Liu, X.
    year: 2026
    title: "Information salience, investor attention, and stock price crash risk"
    venue: Journal of Empirical Finance
    vol: 85
    pages_or_artno: "101670"
  - doi: 10.1016/j.jimonfin.2024.103076
    type: journal
    authors: Zheng, H., & Mao, M. Q.
    year: 2024
    title: "Fintech mergers and acquisitions"
    venue: Journal of International Money and Finance
    vol: 143
    pages_or_artno: 103076
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是 falsification (安慰剂/打假) 对照组的媒体覆盖强度: "Non-Fintech" 银行新闻, 即某银行在某年被报道过、但报道内容不涉及金融科技的普通新闻。这是 bank_fintech_tone 主线论文用来做赛马检验 (horse race) 的关键控制变量族, 直接回应审稿人最常见的质疑: 金融科技新闻的语调之所以能解释银行结果变量, 会不会仅仅是因为该银行"新闻多"这个一般性媒体关注度效应, 而与内容是否涉及金融科技无关? 若把 Non-Fintech 覆盖强度一并放进回归、金融科技语调依然显著, 就能排除"纯关注度"这一竞争性解释, 支持金融科技语调携带内容特异性的增量信息 (H1), 而非仅是关注度的副产品 (H0)。这一构念直接对应 Hassan et al. (2019, QJE) 政治风险文献中 PRisk/NPRisk 范式下"话题特异性 vs 一般关注度"的区分逻辑, 也呼应 Call, Emett, Maksymov & Sharp (2022) 关于财经记者作为信息中介、其报道选择本身携带信息含量的证据——记者决定报什么、放不放标题, 并非随机噪声, 因此普通新闻的覆盖广度和标题显著度本身就构成一个有意义的对照基准, 而不能被当作纯粹的噪声项丢弃。

数据来源上, 本家族由三方 fan-in 构造。第一路是 `12_fintech_news_full.parquet`, 这是 stage 12 在过滤之前落盘的全量银行新闻分类结果, 与上游 `11_bank_news.parquet` 逐行 1:1 对应 (零删行), 只是多出 `is_fintech_news` 等 7 列金融科技标注; 之所以取名带 "fintech" 却是全量底库, 是命名历史遗留, 使用时务必按此口径理解, 不可误判为"仅金融科技新闻"。第二路是 `40_article_bank_level.parquet`, 即已经进入面板的金融科技文章集合。第三路是 `40_panel_yearly.parquet`, 待挂载控制变量的 bank-year 骨架面板。核心构造逻辑是反连接 (anti-join): Non-Fintech = 全量银行新闻 减去 已进面板的金融科技文章, 复合键取 (target_bank, 标题, 日期字符串) 双侧先各自 `drop_duplicates` 再取集合差集, 这一"互补划分"做法直接对应 Hassan et al. (2019, QJE) Table 7 的构造思路——把关注的话题类新闻与其补集分开衡量, 而不是简单地拿总新闻量做对照。这一反连接过程还会通过 pandas `attrs` 机制向下游暴露两个辅助口径: `nf_media_breadth_physical` (去重前的物理媒体广度——同一稿件被多家媒体转载时按转载次数计入广度) 与 `ft_dedup_agg` (去重后的金融科技计数, 与 fintech_share 分子共用同一基准), 用来保证下游聚合口径的一致性。

【方法学与计算】
本家族两列均在 `aggregate_non_fintech` 步骤中按 (target_bank, year) 分组聚合产出。`nf_n_articles` 是该分组内 Non-Fintech 报道去重后的计数——这里的"去重"指的是"同一稿件"基准, 即反连接阶段已按复合键去重过的行数, 而非物理转载篇数; 这与家族内另一个衍生量 `nf_ln_coverage=ln(1+nf_n_articles)` (对应 Fang & Peress 2009 的媒体覆盖对数变换惯例) 共用同一分子口径。`nf_headline_frac` 则是该分组内全部 Non-Fintech 报道行上 `target_bank_in_title` (目标银行是否出现在标题中的 0/1 指示列) 的均值, 衡量的是"普通银行新闻中有多大比例把该银行放进了标题"——这是一个标题显著度/媒体关注强度的代理变量, 呼应 Chen, Li, Liu & Liu (2026, Journal of Empirical Finance) 关于信息显著性 (salience) 与投资者关注度的构念: 报道内容是否被放在标题这一"最先被读者看到的位置", 本身就是媒体对该主体关注强度的信号, 与报道数量是两个正交但都重要的维度。

计算口径上必须强调"同一把尺子"的铁律: 全家族的分子分母 (以及与家族外 `all_n_articles`/`fintech_share` 等挂钩变量) 都刻意维持去重后的"稿件"基准一致——若一端按物理篇数、另一端按去重稿件数混算, 得到的份额或对照强度会系统性偏大或偏小, 破坏赛马检验的可比性。另外, 一个容易被忽视但对回归设定至关重要的细节是: 全年内该银行若完全没有任何 Non-Fintech 报道 (即该 (target_bank, year) 组在反连接后为空), `nf_n_articles`/`nf_headline_frac` 均不会被填成 0, 而是在合并到 `40_panel_yearly` 时以左连接方式留空为 NaN——"未定义"与"确有报道但份额为零"是两种不同的经济含义, 若强行填零会人为压低该银行年份的对照组强度, 污染赛马回归的估计。这也是为什么家族的诊断步骤 (`run_diagnostics`) 要求可用诊断列数 ≥2 才继续算 Pearson/Spearman 相关矩阵——分母过度稀疏 (大量 NaN) 时相关系数本身不可靠, 提前判空返回 None 是一种 fail-loud 的保护而非静默降级。

【文献定位】
本家族的方法论定位横跨两条文献线索。第一条是媒体覆盖与信息中介文献: Call, Emett, Maksymov & Sharp (2022, Journal of Accounting and Economics) 提供了财经记者作为信息中介、其选题与呈现方式本身携带信息含量的直接证据, 支撑本家族"普通新闻覆盖广度/标题显著度值得单独衡量"这一前提; Vives & Ye (2025, Journal of Financial Economics) 讨论信息技术与放贷人竞争的关系, 为区分"技术特异性信息"与"一般性关注度信息"这一赛马逻辑提供了理论背景锚点。第二条是显著性/关注度衡量文献: Chen, Li, Liu & Liu (2026, Journal of Empirical Finance) 的信息显著性框架为 `nf_headline_frac` 提供了直接的方法学对标; Zheng & Mao (2024, Journal of International Money and Finance) 关于金融科技并购的证据提示, 金融科技话题本身的媒体曝光度与一般银行新闻曝光度在样本期内可能存在系统性趋势差异, 这正是本家族作为安慰剂对照组所要控制的背景噪声来源。整体而言, 本家族的两列不是独立的描述性统计, 而是嵌入在"内容特异性 vs 一般关注度"这一识别策略中的对照组构造件, 其数值本身没有因果解释力, 价值在于作为赛马回归中的竞争性解释变量, 服务于金融科技语调效应的稳健性论证。

## VAR: nf_headline_frac

【变体差分】
本列衡量的是 Non-Fintech (普通银行新闻, 即经反连接从全量银行新闻中排除已进面板的金融科技报道后剩余的部分) 在标题层面的显著度, 计算口径为该 (target_bank, year) 分组内全部 Non-Fintech 报道行上 `target_bank_in_title` 指示列的算术均值, 值域为 [0,1] 的比率, 无量纲。分子分母的行集合完全对齐 (同一分组、同一 Non-Fintech 集合), 不存在跨集合混算的风险。`target_bank_in_title` 本身是在 stage 11 `news_bank.py` 阶段生成的非情感信号列, 用于判定目标银行名称是否出现在文章标题中——这是保留下来的非情感度量之一 (与情感度量的三轨 full/ctx/ss 体系无关, 不参与三轨禁混 Hansen J 的铁律约束, 因为本列既不属于三轨情感测度也不是 co-primary 嵌入或任何消融梯子成员, 而是独立的标题显著度控制变量), 因此本列在识别策略里应当被理解为与情感语调、嵌入相似度等测度正交的一条单独控制线, 不与任何梯子/多轨测度混入同一 over-identified 设定。

需要特别说明的是分母覆盖问题: 若该银行在给定年份完全没有 Non-Fintech 报道, 则该分组在聚合阶段不产生任何行, 合并回 `40_panel_yearly` 后该 (target_bank, year) 观测的 `nf_headline_frac` 将是 NaN 而非 0——这是"该年无普通新闻可供衡量标题显著度"与"该年普通新闻标题显著度确实为零"两种不同经济含义的严格区分, 生产者代码不会做零填充。使用本列做回归控制时, 应当意识到 NaN 观测会被大多数估计命令自动剔除, 若该银行的普通新闻覆盖长期稀疏, 会造成样本损失; 这与 `nf_n_articles` 列的稀疏模式高度相关 (`nf_n_articles=0` 蕴含 `nf_headline_frac` 为 NaN, 二者共享同一底层分组存在性), 因此在解读赛马回归系数时应同时报告两列的缺失比例, 避免读者误以为标题显著度低是一种"数值上的零", 而实际上可能是完全没有可比样本。作为对照组变量, 本列不承担因果解释, 其唯一角色是在赛马设定中吸走"一般媒体是否重视该银行"这一竞争性解释成分, 使金融科技语调的边际贡献能够被更干净地识别出来。

## VAR: nf_n_articles

【变体差分】
本列是 Non-Fintech 报道在 (target_bank, year) 分组内去重后的计数, 单位为篇, 非负整数 (面板合并后若该年无 Non-Fintech 报道则为 NaN, 而非 0——见上文"未定义 vs 零"的区分, 本列同样遵循该口径, 不做零填充)。这里"去重"特指反连接构造阶段已按复合键 (target_bank, 标题, 日期字符串) 各自去重后再取集合差集的"稿件"基准, 而非转载篇数的物理基准; family 内还并行暴露一个物理媒体广度口径 `nf_media_breadth` (优先取反连接 attrs 暴露的物理去重口径 nunique, 缺失时才回退到稿件去重基), 二者服务于不同问题——`nf_n_articles` 回答"有多少条不同稿件", `nf_media_breadth` 回答"有多少家不同媒体报道过", 两者不应混淆或互相替代作为分母。

本列在下游面板合并时还承担着构造"总量/挤出弹性"变量族的分母/加数角色: `all_n_articles = ft_dedup_agg + nf_n_articles` (与金融科技计数同基相加, 若缺 `ft_dedup_agg` 才回退到物理口径混基, 并触发跨源一致性校验); `fintech_share = ft_dedup_agg / all_n_articles` (分母为零时置 NaN, 并配一个 zero_coverage 指示列)。此外 `nf_ln_coverage = ln(1 + nf_n_articles)` 是对本列的对数变换, 对应 Fang & Peress (2009) 处理媒体覆盖度惯用的对数化方式, 用于压缩右偏分布并使系数具备近似弹性解释; `ln_nf_articles` 与 `ln_ft_articles` 构成"挤出弹性对" (两端严格同基), 供诊断步骤检测金融科技报道与普通报道数量之间是否存在机械关联 (若相关系数绝对值过高, 说明二者可能共享同一驱动因素而非相互独立, 需要在解释赛马回归结果时格外谨慎)。作为安慰剂/对照组变量, `nf_n_articles` 本身不是任何梯子或多轨测度族成员, 不涉及三轨/co-primary 嵌入/消融梯子的并排口径, 但在与家族外挂钩的挤出弹性、总量份额等衍生变量中扮演关键的分母/加数角色, 使用时须核对上下游列 (`ft_dedup_agg`、`all_n_articles`、`fintech_share`) 是否共用同一去重基准, 避免分子分母基准不一致导致的系统性偏差。

<!-- rendered-citations:begin -->
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, 101670. https://doi.org/10.1016/j.jempfin.2025.101670
Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. Journal of International Money and Finance, 143, 103076. https://doi.org/10.1016/j.jimonfin.2024.103076
<!-- rendered-citations:end -->
