---
family_id: F468
columns:
- nf_media_breadth
unit: 家 (distinct-outlet 计数, 整数值域 [0, +∞))
formula: 'nf_media_breadth(bank, year) = nunique(媒体(中文)) over 该 bank-year 的
  Non-Fintech 物理 (去重前) 行集; Non-Fintech = 12_fintech_news_full.parquet (stage
  12 过滤前全量银行新闻) MINUS 40_article_bank_level.parquet (已进面板的 fintech 文章), 复合键
  (target_bank, 标题, _date_str) anti-join'
producer: pipeline\falsification\controls.py::build_non_fintech / aggregate_non_fintech
upstream:
- 12_fintech_news_full.parquet
- 40_article_bank_level.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What Drives Media Slant? Evidence from U.S. Daily Newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: 'When the Local Newspaper Leaves Town: The Effects of Local Newspaper
    Closures on Corporate Misconduct'
  venue: Journal of Financial Economics
  vol: '145'
  issue: '2'
  pages_or_artno: 445-463
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The Information Role of the Media in Earnings News
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: 'The Media and the Diffusion of Information in Financial Markets: Evidence
    from Newspaper Strikes'
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: 'Meet the Press: Survey Evidence on Financial Journalists as Information
    Intermediaries'
  venue: Journal of Accounting and Economics
  vol: '73'
  issue: 2-3
  pages_or_artno: '101455'
- doi: "10.1287/mnsc.2023.02247"
  type: journal
  authors: "Dyer, T., Lang, M. H., & Oh, J."
  year: 2025
  title: "Media Conglomeration, Local News, and Capital Market Consequences"
  venue: "Management Science"
new_dois:
  - "10.1287/mnsc.2023.02247"
---

## CORE

【构念与来源】
nf_media_breadth 隶属伪造检验 (falsification test) 模块下的非金融科技 (Non-Fintech) 对照变量族, 度量的构念是「信息中介多样性」——某银行在给定年份被多少家不同媒体来源报道过, 而非报道了多少次。该家族与家族内的姊妹列 nf_n_articles (报道篇数)、nf_ln_coverage (对数化报道量) 共同构成本项目伪造检验框架中 Fintech/Non-Fintech 互补划分范式下的对照组特征, 用于回答一个识别层面的问题: 本项目核心处理变量 (fintech tone / attention) 观测到的解释力, 是否仅仅来自「银行一般性获得了更多媒体关注」这一混杂渠道, 而非金融科技维度的特异性信息。构念上, nf_media_breadth 承接 Gentzkow & Shapiro (2010, Econometrica) 对报纸媒体来源异质性的经典论证: 不同的新闻机构各自拥有独立的采编立场、受众群体与信息核验流程, 因此报道来源的广度 (breadth, 有多少家不同媒体参与报道) 与报道的数量 (volume, 报道了多少条) 在概念上是两个可分离的维度——前者反映信息在媒体生态中的扩散广度与到达面, 后者反映单一事件被反复叙述的强度。这一区分呼应 Heese, Pérez-Cavazos & Peter (2022, JFE) 关于地方报纸退出 (newspaper closures) 削弱信息中介多样性、进而弱化公司治理监督的因果证据——媒体来源数量本身是一个具有独立经济后果的维度, 而非报道量的简单衍生品; 两者共同构成本项目伪造检验框架中"一般媒体关注度"控制变量组的方法论谱系。

数据来源上, nf_media_breadth 的样本基是 build_non_fintech 函数通过 anti-join 构造的互补划分: 以 12_fintech_news_full.parquet (stage 12 分类阶段过滤之前落盘的全量银行新闻, 与更上游的 11_bank_news.parquet 逐行一致、仅多出 is_fintech_news 等 7 列标注; 命名带 "fintech" 字样但实为全量底库, 勿因字面误判) 为全集, 减去 40_article_bank_level.parquet (最终进入生产面板、被判定为金融科技相关的文章) 得到 Non-Fintech 对照组——即被判定为"与该银行相关但不构成金融科技报道"的全部新闻。两侧 anti-join 的复合键为 (target_bank, 标题, _date_str), 双侧各自先按此键 drop_duplicates(keep='first') 消除"同一稿件被系统重复摄入"的技术性重复, 这与 nf_media_breadth 自身的口径处理是两回事 (详见【方法学与计算】)。

【方法学与计算】
计算链条分三步。第一步 build_non_fintech 在完成复合键去重之前, 先对 12_fintech_news_full 侧的原始 (物理) 行集取一份仅含 (target_bank, 标题, _date_str, 日期, 媒体(中文)) 五列的快照, 记为 _df_full_physical; 随后才对 df_full 执行复合键去重、再与面板文章集合做差集运算得到去重后的 Non-Fintech 行集 df_nf。物理快照与去重后集合分别经 anti-join (基于同一复合键 是否落入面板 key 集合) 得到物理口径 Non-Fintech 行集 _nf_phys, 按 (target_bank, _year) 分组对媒体(中文)列取 nunique(), 结果通过 pandas DataFrame.attrs 机制以键 nf_media_breadth_physical 挂载在返回的 df_nf 对象上, 供下游聚合函数按需读取——这是一种刻意的"物理口径"与"去重口径"并行保留设计: build_non_fintech 主流程输出的 df_nf 仍是复合键去重后的集合 (供 nf_n_articles 等篇数类变量使用"同稿件"集合语义), 但 nf_media_breadth 单独走未去重的物理行集。

第二步 aggregate_non_fintech 优先读取 attrs 中的 nf_media_breadth_physical 并 left join 挂到主聚合表, 缺失值填 0 并转 int; 仅当 attrs 缺失时 (即函数被脱离标准调用链单独直调) 才退化为对已去重的 df_nf 直接做 nunique() 的 legacy fallback, 并输出 WARNING 明确告知该口径会因复合键去重折叠掉跨媒体转载而低估广度。生产管线 (run_diagnostics → export_results 全流程) 恒定走物理口径分支, fallback 分支仅为兼容遗留直调路径保留, 不构成生产口径的一部分。

第三步是这一物理口径设计的构念依据, 由代码内 fix(omni-g-controls-02, 2026-06-11) 变更说明明确记录: 复合键 (target_bank, 标题, 日期) 不含媒体列, 若在去重之后的集合上取媒体 nunique, "同一稿件被 N 家不同媒体转载"这一现象会被 keep='first' 逻辑折叠为仅保留其一家, 系统性低估广度; 而 nf_media_breadth 的构念恰恰是"多少家不同信息中介覆盖了该银行", 转载本身就是构念的一部分而非需要剔除的噪声。这一设计选择与本项目 attention_media.py 中 attention_index/attention_pct 等核心处理变量族的口径形成鲜明的对照互补 (而非矛盾): attention 族衡量的是"信息到达"构念, 通稿/转载不携带增量信息, 理应在去重语料基上计算; nf_media_breadth 衡量的是"传播广度/可见度"构念, 转载本身就是可见度的体现, 理应在去重前的物理行集上计算 (Guest 2021, JAR, 关于媒体在盈余新闻中信息中介角色的实证传统同样将报道来源的覆盖广度而非单次事件计数作为信息环境丰富度的代理)。白话理解: 一条新闻被 50 家网站转载, 若问"发生了多少件事", 答案是 1 件 (attention 族口径, 不去重会虚增); 若问"传播得有多广", 答案恰恰要数满 50 次 (nf_media_breadth 口径)。两套口径分工明确、各司其职, 是同一份原始语料上两个不同构念各自采用的正确统计口径, 而非同一构念内部的不一致。

需要特别澄清的边界: nf_media_breadth 度量的是非金融科技报道 (Non-Fintech) 的媒体来源广度, 服务的是伪造检验的对照组特征构造, 而非核心处理变量本身; 它在 51_falsification_test.py 主流程中随 merge_to_panel 一并左连接进 bank-year 面板 (51_panel_with_controls.parquet/.dta), 与情感三轨 (llm_vote_tone_full/_ctx/_ss) 一起送入 run_diagnostics 计算 Pearson/Spearman 相关矩阵, 作为 H0 (核心处理变量的解释力完全来自一般媒体关注度) vs H1 (核心处理变量含金融科技特异性增量信息) 假设检验的诊断依据之一: 若情感测度与 nf_media_breadth 等一般媒体关注度控制变量的相关系数 |r| < 0.3, 则被视为对 H1 的支持性证据。作为控制变量, nf_media_breadth 本身并不进入本项目任何三轨/co-primary 嵌入/梯子体系——它是伪造检验的辅助诊断列, 与核心处理变量的三轨并排稳健性设计 (full/ctx/ss 各自 just-identified 并排、互为稳健性、禁混进同一 over-identified Hansen J) 是两个独立的方法论层面, 互不交叉, 亦不受 stage 21 全量口径 (2026-06-29 起留篇门控 full-only) 约束——该门控针对的是"一篇报道是否算作金融科技相关文章"这一判定, 而 nf_media_breadth 恰恰统计的是被排除在该判定之外的 Non-Fintech 报道集合, 两者在样本层面互斥而非重叠。

【文献定位】
nf_media_breadth 的核心构念依据是 Gentzkow & Shapiro (2010, Econometrica) 对美国日报媒体立场异质性的经典论证, 该文强调不同新闻机构在采编选择上存在系统性差异, 单一信源不能代表信息环境的全貌, 唯有跨多家独立信源的覆盖才能降低单一信源偏误或选择性披露对信息环境的支配力——这是本列以 distinct-outlet 计数而非单一"是否被报道"二元指示衡量信息环境丰富程度的直接理论依据。计算口径 (去重前物理行集取 nunique) 的选择进一步呼应 Heese, Pérez-Cavazos & Peter (2022, JFE) 关于地方报纸退出削弱媒体来源多样性、进而弱化公司治理监督效力的因果证据: 该文以报纸停刊这一外生冲击证明媒体来源的"数量"本身 (而非报道总量) 具有独立的信息中介价值; nf_media_breadth 的构念设计与其一致, 计的是覆盖来源数而非覆盖次数。伪造检验的整体识别框架承接本项目 Fintech/Non-Fintech 互补划分范式, nf_media_breadth 作为对照组侧的媒体环境控制变量之一嵌入该框架, 用以排除"银行整体媒体关注度上升"这一混杂渠道对核心处理变量解释力的污染。此外, Peress (2014, JF) 利用报业罢工的自然实验证明媒体存在与否会因果性地影响金融市场信息扩散速度与深度, 从识别策略角度进一步支持"媒体来源多样性是一个应当被控制、而非被忽略的混杂渠道"这一建模选择; Guest (2021, JAR) 关于媒体在盈余新闻信息生产链条中信息中介角色的实证研究、以及 Call, Emett, Maksymov & Sharp (2022, JAE) 基于财经记者的调查证据, 共同确认了新闻媒体作为独立信息中介在资本市场信息生产链条中的作用, 为多信源广度构念的现实基础提供了当代实证背书。Dyer, Lang & Oh (2025, Management Science) 以 Sinclair 电视台并购为外生冲击, 证明地方媒体来源整合会因果性地压缩本地公司报道覆盖并削弱投资者信息获取, 印证媒体来源数量 (而非报道总量) 本身具有独立信息中介价值, 与 nf_media_breadth 以 distinct-outlet 计数而非报道量衡量传播广度的构念设计相呼应。

## VAR: nf_media_breadth

【变体差分】
本家族仅含单一列 nf_media_breadth, 无并列变体, 该节说明其在自身产出链条内部的口径确定性, 以避免与相邻姊妹列混淆。nf_media_breadth 与同一 aggregate_non_fintech 函数产出的 nf_n_articles (Non-Fintech 报道篇数)、nf_ln_coverage (对数化报道量) 共享同一个 Non-Fintech 行集来源, 但三者的去重基不同: nf_n_articles 与 nf_ln_coverage 建立在复合键 (target_bank, 标题, _date_str) 去重后的"同稿件"集合语义之上 (与 40_panel_yearly 面板侧的口径口径对齐, 一条稿件不论被多少家媒体转载都只计一次); 而 nf_media_breadth 特意选用去重之前的物理行集做 distinct-outlet nunique, 因为其构念 (信息中介多样性) 要求转载被计入而非折叠。这一去重基的不对称并非实现疏忽, 而是 fix(omni-g-controls-02, 2026-06-11) 记录在案的显式设计决策, 在代码中以 df_nf.attrs['nf_media_breadth_physical'] 这一独立通道传递物理口径聚合结果, 与主聚合流程 (走去重基) 并行不悖。

取值上, nf_media_breadth 是非负整数 (家为单位, 即"该 bank-year 内出现过的不同媒体名称数"), 理论下界 0 (对应该银行年内无 Non-Fintech 报道或媒体列全部缺失, 后者会触发 WARNING 而非静默填 0); 当媒体列 '媒体(中文)' 在源数据中不存在时, aggregate_non_fintech 会记 WARNING 并将该列整体置 0 (而非 NaN), 这与同一函数内 nf_headline_frac 在类似缺失情形下改填 NaN (因其是比率量, 0 具有"提及率确为零"的误导性语义) 的处理有意不同——nf_media_breadth 的 0 值在"无媒体列可用"与"确实只有 0 家媒体报道"两种情形下语义上是一致的 (均表示"无法/未观测到多信源覆盖"), 故填 0 不构成语义混淆。该列不区分 full/ctx/ss 三轨 (伪造检验对照变量族不涉及正文文本窗口切分, 三轨切分是情感/嵌入类核心处理变量的专属设计), 不涉及 co-primary 嵌入双轨, 也不落在本项目任何消融梯度 (词典规则消融、政治词权重、罕见词频次 cutoff 等) 或 per-model 稳健性矩阵内, 属于纯计数类结构性控制变量, 在面板中以单一列形态存在、无需梯子/轨道语义警示。

<!-- rendered-citations:begin -->
Gentzkow, M., & Shapiro, J. M. (2010). What Drives Media Slant? Evidence from U.S. Daily Newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the Local Newspaper Leaves Town: The Effects of Local Newspaper Closures on Corporate Misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Guest, N. M. (2021). The Information Role of the Media in Earnings News. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the Press: Survey Evidence on Financial Journalists as Information Intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Dyer, T., Lang, M. H., & Oh, J. (2025). Media Conglomeration, Local News, and Capital Market Consequences. Management Science. https://doi.org/10.1287/mnsc.2023.02247
<!-- rendered-citations:end -->
