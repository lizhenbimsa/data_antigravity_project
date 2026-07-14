---
family_id: F005
columns:
- all_n_articles
unit: 篇数 (整数计数, 存为 double; 银行-年粒度)
formula: "all_n_articles = ft_dedup_agg + nf_n_articles (同去重稿件基; ft_dedup_agg 缺失时回退 物理 n_articles + nf_n_articles 混合基)"
producer: news_process/pipeline/falsification/controls.py::merge_to_panel
upstream:
- 12_fintech_news_full.parquet
- 40_article_bank_level.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.1093/restud/rdad018
  type: journal
  authors: Rambachan, A., & Roth, J.
  year: 2023
  title: "A more credible approach to parallel trends"
  venue: The Review of Economic Studies
  vol: 90
  issue: 5
  pages_or_artno: 2555-2591
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
  venue: Journal of Accounting and Economics
  vol: 73
  issue: 2-3
  pages_or_artno: 101455
- doi: 10.1016/j.jeconom.2020.12.001
  type: journal
  authors: Callaway, B., & Sant'Anna, P. H. C.
  year: 2021
  title: "Difference-in-differences with multiple time periods"
  venue: Journal of Econometrics
  vol: 225
  issue: 2
  pages_or_artno: 200-230
- doi: 10.1016/j.jacceco.2017.07.002
  type: journal
  authors: Dyer, T., Lang, M., & Stice-Lawrence, L.
  year: 2017
  title: "The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation"
  venue: Journal of Accounting and Economics
  vol: 64
  issue: 2-3
  pages_or_artno: 221-245
- doi: 10.1093/pan/mps028
  type: journal
  authors: Grimmer, J., & Stewart, B. M.
  year: 2013
  title: "Text as data: The promise and pitfalls of automatic content analysis methods for political texts"
  venue: Political Analysis
  vol: 21
  issue: 3
  pages_or_artno: 267-297
- doi: "10.1111/1911-3846.12982"
  title: "The impact of news media coverage on voluntary disclosure"
  authors: "Lock, B."
  year: 2024
  venue: "Contemporary Accounting Research"
  type: "journal"
  one_sentence_zh: "该文用媒体报道量度量投资者注意力并检验其对企业信息披露行为的因果影响, 为本列把总报道篇数作为一般媒体关注度混淆控制的构念定位提供了2024年顶刊佐证。"
- doi: "10.1002/smj.3600"
  title: "Competing for attention on digital platforms: The case of news outlets"
  authors: "Meyer, T., Kerkhof, A., Cennamo, C., & Kretschmer, T."
  year: 2024
  venue: "Strategic Management Journal"
  type: "journal"
  one_sentence_zh: "该文研究新闻媒体在数字平台上争夺注意力的机制, 揭示报道量/曝光度本身是一种独立于内容质量的注意力资源, 为本列把总报道篇数作为一般媒体关注度基线的构念定位提供2024年顶刊佐证。"
- doi: "10.1111/ajps.12752"
  title: "Banklash: How Media Coverage of Bank Scandals Moves Mass Preferences on Financial Regulation"
  authors: "Culpepper, P. D., Jung, J.-H., & Lee, T."
  year: 2023
  venue: "American Journal of Political Science"
  type: "journal"
  one_sentence_zh: "该文用银行相关新闻报道的曝光量衡量公众对银行议题的媒体关注强度并检验其对监管偏好的因果影响, 为本列以银行-年报道篇数作为媒体关注度计数测度提供2023年针对银行主体的实证佐证。"
new_dois:
  - "10.1111/1911-3846.12982"
  - "10.1002/smj.3600"
  - "10.1111/ajps.12752"
---

## CORE

【构念与来源】
all_n_articles 是一个银行-年粒度的总媒体报道量计数, 度量某家目标银行在某一年被媒体报道的总篇数, 涵盖金融科技类与非金融科技类两个互补子集。它诞生于打假对照 (falsification) 阶段, 目的不是直接进入主回归作解释变量, 而是充当赛马 (horse-race) 对照里的一般媒体关注度基线: 论文主张金融科技新闻的语调对银行有超出普通报道量的特异性增量信息, 而检验这一主张的前提是先把纯粹的报道多寡这一混淆通道量化出来, 才能在控制它之后观察金融科技语调是否仍然显著。该构念承接媒体金融学关于报道量与市场关注度的经典范式: 媒体覆盖既是信息中介活动的产物, 也是投资者注意力的代理, 报道越多未必意味着信息越丰富, 但报道量本身会系统性地与银行的可见度、流动性与估值相关。Call, Emett, Maksymov 与 Sharp (2022) 通过对财经记者的调查证据说明媒体作为信息中介的角色, 记者的选题与转载行为决定了某一主体被报道的密度, 这正是本列所刻画的对象。因此把总报道量与金融科技语调并置于同一回归, 是分离数量效应与语调 (内容) 效应的必要一步。

【方法学与计算】
本列在 stage 51 (falsification) 的 merge_to_panel 环节构造。上游三方 fan-in: 12_fintech_news_full.parquet 是 stage 12 过滤之前的全量银行新闻底库 (与 11_bank_news 逐行 1:1, 仅多出 is_fintech_news 等标注列, 命名带 fintech 但实为全量), 40_article_bank_level.parquet 是已进入面板的金融科技文章, 40_panel_yearly.parquet 是待挂控制变量的银行-年面板。构造分两支: 一支经 build_non_fintech 用反连接 (anti-join) 把全量银行新闻减去已进面板的金融科技文章, 得到非金融科技对照组, 复合键为 (目标银行, 标题, 日期串) 双侧去重后取集合差集, 再按 (银行, 年) 聚合得 nf_n_articles; 另一支取金融科技去重稿件计数 ft_dedup_agg。二者相加即 all_n_articles。这里最承重的一条纪律是同一把尺子: 分子分母必须共用同一去重口径, 若 ft 端用去重稿件数而 nf 端用物理篇数 (或反之), 得到的份额会系统性偏大, 赛马就失真; 因此 all_n_articles 优先以去重稿件为同基, 仅当 ft_dedup_agg 缺失时才回退为物理 n_articles 与 nf 的混合基, 并配有去重计数不超过物理计数的逐行一致性校验。派生同族的 fintech_share = ft_dedup / all_n_articles, 当 all_n_articles 为 0 时置为未定义 (NaN) 而非零份额, 以免把全年零报道的银行-年当成金融科技占比为零污染回归。整个阶段无 LLM、无嵌入、无网络调用, 纯 pandas/numpy, 确定性强。留篇口径与全线一致: 是否算作一篇银行金融科技报道以 full 轨的 LLM 门控为准 (full-only, 2026-06-29), 非金融科技对照组则是全量底库减去这些留篇文章的补集, 二者构成 Hassan 式的互补划分。

【文献定位】
该列的方法论谱系横跨三条脉络。其一是媒体与信息中介文献: Call 等 (2022) 的记者调查、以及更广义的文本即数据传统 (Grimmer & Stewart, 2013) 提示, 从非结构化新闻抽取的任何计数都带有内容分析方法的固有偏误 (选题、转载、去重口径), 必须显式声明测量协议才能复现, 这正是本列坚持同基去重与物理/去重双口径披露的原因。其二是文本披露演化文献: Dyer, Lang 与 Stice-Lawrence (2017) 对 10-K 文本篇幅与主题演化的度量表明, 简单的量 (篇数、字数) 与质 (语调、主题) 需分别建模, 二者高度相关却不可互相替代, 这为把报道量单列为赛马对照、而非并入语调变量提供了度量学依据。其三是打假/安慰剂识别文献: 本阶段的假设框架为 H0 (金融科技语调解释力全部来自一般媒体关注度) 对 H1 (含金融科技特异性增量), all_n_articles 是检验 H0 的核心对照; 与之配套的安慰剂时点 DID 借鉴 Callaway 与 Sant'Anna (2021) 的多期差分框架, 而对平行趋势可信性的敏感性叙事则可锚定 Rambachan 与 Roth (2023) 的更可信平行趋势方法。需要说明的是, all_n_articles 与金融科技份额、语调等测度是构念上正交的两类对象: 前者是数量维度的混淆控制, 后者是内容维度的处理变量, 二者不得互相代换, 这一区分是整条打假防线成立的前提。Lock (2024, Contemporary Accounting Research) 用媒体报道量度量投资者注意力并检验其对企业信息披露行为的因果影响, 为本列把总报道篇数作为一般媒体关注度混淆控制的构念定位提供了2024年顶刊佐证。Meyer, Kerkhof, Cennamo 与 Kretschmer (2024, Strategic Management Journal) 研究新闻媒体在数字平台上争夺注意力的机制, 揭示报道量/曝光度本身是一种独立于内容质量的注意力资源, 为本列把总报道篇数作为一般媒体关注度基线的构念定位提供2024年顶刊佐证。Culpepper, Jung 与 Lee (2023, American Journal of Political Science) 用银行相关新闻报道的曝光量衡量公众对银行议题的媒体关注强度并检验其对监管偏好的因果影响, 为本列以银行-年报道篇数作为媒体关注度计数测度提供2023年针对银行主体的实证佐证。

## VAR: all_n_articles

【变体差分】
本家族仅此一列, 无三轨 (full/ctx/ss)、无 co-primary 双轨嵌入、无梯子 (消融/权重/阈值/判据)、无 per-model 分裂, 因此不存在需要与家族 canonical 区分的变体后缀。其精确语义即家族核心构念本身: 银行-年粒度的总媒体报道篇数, 等于金融科技去重稿件计数 ft_dedup_agg 与非金融科技对照组计数 nf_n_articles 之和, 同去重稿件基。与同阶段相邻列的区别须逐一厘清: 它不是 nf_n_articles (仅非金融科技子集), 不是面板主链的物理 n_articles (未做本阶段的同基去重协调, 且不含 nf 补集), 也不是 fintech_share (本列是其分母而非份额本身)。数据类型为整数计数但以 double 落盘, 银行-年唯一。回退语义须重申: 仅当 ft_dedup_agg 缺失时才退化为物理 n_articles + nf 的混合基, 此时该银行-年的同基性弱化, 由跨源去重计数不超过物理计数的逐行校验兜底。它进入回归的定位始终是一般媒体关注度的赛马对照/混淆控制, 而非处理变量: 在控制 all_n_articles 后若金融科技语调仍显著, 即支持 H1 的金融科技特异性增量信息假设。全年零报道的银行-年在此列取 0, 但由其派生的 fintech_share 在 all_n_articles=0 时置 NaN 而非 0, 避免把无报道误当作零金融科技占比。本列由 merge_to_panel 单点构造, 无 LLM、无嵌入、确定性强, 不受离线缓存守卫约束。

<!-- rendered-citations:begin -->
Rambachan, A., & Roth, J. (2023). A more credible approach to parallel trends. The Review of Economic Studies, 90(5), 2555-2591. https://doi.org/10.1093/restud/rdad018
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics, 225(2), 200-230. https://doi.org/10.1016/j.jeconom.2020.12.001
Dyer, T., Lang, M., & Stice-Lawrence, L. (2017). The evolution of 10-K textual disclosure: Evidence from Latent Dirichlet Allocation. Journal of Accounting and Economics, 64(2-3), 221-245. https://doi.org/10.1016/j.jacceco.2017.07.002
Grimmer, J., & Stewart, B. M. (2013). Text as data: The promise and pitfalls of automatic content analysis methods for political texts. Political Analysis, 21(3), 267-297. https://doi.org/10.1093/pan/mps028
Lock, B. (2024). The impact of news media coverage on voluntary disclosure. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.12982
Meyer, T., Kerkhof, A., Cennamo, C., & Kretschmer, T. (2024). Competing for attention on digital platforms: The case of news outlets. Strategic Management Journal. https://doi.org/10.1002/smj.3600
Culpepper, P. D., Jung, J.-H., & Lee, T. (2023). Banklash: How Media Coverage of Bank Scandals Moves Mass Preferences on Financial Regulation. American Journal of Political Science. https://doi.org/10.1111/ajps.12752
<!-- rendered-citations:end -->
