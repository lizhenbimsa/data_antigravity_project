---
family_id: F326
columns:
- headline_frac
unit: 比率 (proportion, 无量纲, 取值域 [0,1]; 零新闻 bank-year 为 NaN 而非 0)
formula: "headline_frac = mean(in_title) by (target_bank, year); in_title = int(target_bank_in_title) (stage 11 判定目标银行别名出现在标题, runner 步骤3 转 int); 零新闻 bank-year 比率未定义保 NaN (balance_panel 比例类契约)"
producer: news_process/pipeline/panel/encode.py::build_aggregation_dict (agg['headline_frac'] = ('in_title','mean')) → aggregate_panel 按 (target_bank, year) 聚合; in_title 由 pipeline/panel/runner.py 步骤3 自 target_bank_in_title 派生 (源头 = pipeline/filtering/news_bank.py::analyze_bank_matches)
upstream:
- 11_bank_news.parquet (target_bank_in_title, firm-document 展开行)
- 40_article_bank_level.parquet (in_title 派生, full-only 留篇门控后文章宇宙)
- 40_panel_yearly.parquet (bank-year 聚合落列)
citations:
- doi: 10.1016/j.jempfin.2025.101670
  type: journal
  authors: Chen, Z., Li, Z., Liu, J., & Liu, X.
  year: 2026
  title: "Information salience, investor attention, and stock price crash risk"
  venue: Journal of Empirical Finance
  vol: 85
  pages_or_artno: "Article 101670"
- doi: 10.1002/mde.70100
  type: journal
  authors: Li, Y.
  year: 2026
  title: "The textual tone of annual reports and market attention: Evidence from Chinese listed companies"
  venue: Managerial and Decision Economics
  vol: 46
  pages_or_artno: "e70100"
- doi: 10.1016/j.gfj.2025.101126
  type: journal
  authors: Garcia, J.
  year: 2025
  title: "Beyond the headlines: Sentiment divergence and financial distress"
  venue: Global Finance Journal
  vol: 66
  pages_or_artno: "Article 101126"
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: "1373-1403"
- doi: 10.1111/jofi.13287
  type: journal
  authors: Fedyk, A.
  year: 2024
  title: "Front-page news: The effect of news positioning on financial markets"
  venue: The Journal of Finance
  vol: 79
  issue: 1
  pages_or_artno: "5-33"
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B. T., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: "3105-3147"
- doi: 10.1111/acfi.13328
  type: journal
  authors: Ni, Y.
  year: 2024
  title: "Media coverage and disclosure of short-termism tone: Evidence from China"
  venue: Accounting & Finance
  vol: 64
  issue: S1
  pages_or_artno: "5107-5131"
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-level political risk: Measurement and effects"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: "2135-2202"
- doi: 10.1093/rfs/hhr133
  type: journal
  authors: Dougal, C., Engelberg, J., García, D., & Parsons, C. A.
  year: 2012
  title: "Journalists and the stock market"
  venue: The Review of Financial Studies
  vol: 25
  issue: 3
  pages_or_artno: "639-679"
- doi: 10.1111/j.1540-6261.2011.01679.x
  type: journal
  authors: Da, Z., Engelberg, J., & Gao, P.
  year: 2011
  title: "In search of attention"
  venue: The Journal of Finance
  vol: 66
  issue: 5
  pages_or_artno: "1461-1499"
- doi: 10.1111/j.1540-6261.2010.01626.x
  type: journal
  authors: Engelberg, J. E., & Parsons, C. A.
  year: 2011
  title: "The causal impact of media in financial markets"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: "67-97"
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: "2023-2052"
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: "1139-1168"
new_dois: []
---

## CORE

【构念与来源】
本家族测量的构念是标题显著性 (headline salience): 在一家银行的年度新闻组合中, 该银行的名称直接出现在新闻标题里的文章所占的比例。标题是新闻文本中位置显著性最高、读者注意力分配最密集的部分 — 一篇报道把目标银行写进标题, 意味着编辑部把这家银行当作该篇报道的叙事主角而非顺带提及的配角, 也意味着仅浏览标题不读正文的读者同样会接收到这家银行的信号。因此标题提及率刻画的不是报道数量 (覆盖广度), 也不是报道内容的情感方向 (语调), 而是既有报道内部的显著性构成: 同样一百篇报道, 九成把银行写进标题与只有一成写进标题, 对投资者与储户注意力的动员强度截然不同。这一构念区分在近年文献中被明确形式化: Chen 等 (2026) 把信息显著性与投资者注意力当作两个可分离的可测构造分别估计其对股价崩盘风险的影响, 证明显著性维度携带独立于关注总量的增量信息; Fedyk (2024) 利用新闻在版面上的准随机摆放位置识别出纯位置效应 — 内容完全相同的新闻, 摆在头版位置能引发显著更强的交易反应, 这为把标题位置当作独立于内容的显著性处理提供了最干净的因果证据。往前追溯, Tetlock (2007) 开创的媒体文本经济学关注的是内容维度 (悲观语调预测收益), 而本列刻意剥离内容、只保留位置与显著性维度, 与之构成互补而非重复。在项目内部, headline_frac 属于被 CLAUDE.md 点名保留的非情感信号族: v3.8.0 版本删除了独立的标题情感轨 (标题文本改为 prepend 进三轨正文), 但标题命中类的非情感信号 — 文章级 target_bank_in_title、金科侧 fintech_in_title、以及本面板级聚合列 headline_frac — 被刻意保留, 因为它们承载的是显著性与叙事主角信息, 不随情感轨的架构调整而失效。白话说, 这一列回答的问题是: 这家银行这一年的新闻里, 有多大比例是把它写在大字标题上的重头报道, 而不是埋在正文里一笔带过的背景提及。

【方法学与计算】
计算链路自上而下分三层, 每层职责单一。第一层是文章级判定, 发生在 stage 11 (pipeline/filtering/news_bank.py)。该阶段用全局 Aho-Corasick 自动机在一次线性扫描中匹配全部银行别名, 并做 firm-document 展开: 一篇文章同时命中多家合格银行时, 为每家银行生成一条独立物理行, 每行有自己的 target_bank。对每一行, analyze_bank_matches 判定该目标银行的任一别名是否出现在标题字段中, 输出布尔列 target_bank_in_title (代码里 int(bank_info.get('in_title', False)))。这一判定继承银行侧不对称口径的全部假阳性排除机制: 其一是否定模式排除, 形如务农行列、交通行业这类字面命中农行、交行的伪匹配被 NEGATION_AC 自动机剔除; 其二是短名歧义消解, 两字以内的简称 (如工行、中行) 须检查前后语境窗口字符, 命中排除词则该次匹配作废。标题命中同时参与银行资格判定本身 — 分布条件 (b) 允许别名出现在标题且全文合计次数达到下限的文章直接过闸, 即标题命中在上游就是一条独立的合格通道, 与本列的测度语义自洽。第二层是列名规整, 发生在面板 runner 的步骤 3 (pipeline/panel/runner.py): 存在 target_bank_in_title 列时执行 in_title = target_bank_in_title.astype(int); 仅当该列与 in_title 双双缺失的异常 schema 下才回退置 0, 属防御性兜底而非常规路径。第三层是 bank-year 聚合, 发生在 pipeline/panel/encode.py::build_aggregation_dict — agg 字典中登记 headline_frac = ('in_title', 'mean'), 由 aggregate_panel 按 (target_bank, year) 分组求均值。由于 in_title 是 0/1 指示变量, 组内均值即比例, 数学上保证落在 [0,1] 闭区间。聚合的行宇宙与 n_articles 同基: 进入 40_article_bank_level 的文章集合, 即经过 stage 13 银行与金科词邻近共现硬过滤、再经 stage 21 full-only 留篇门控 (2026-06-29 口径, 一篇是否留在面板只看 llm_verified_full 为真) 之后的银行金融科技报道全集。分母是该 bank-year 的全部物理文章行, 不做任何有效性子集筛选, 因为标题命中是纯词典判定, 不依赖 LLM 标注成功与否。最后是面板平衡层的缺失语义: balance_panel 对计数与和类列在零新闻 bank-year 填 0, 但对比例类列保持 NaN — headline_frac 是比率, 零新闻年份上 0/0 未定义, 填 0 会被回归误读为标题提及率真为零, 因此该列在无报道的银行年份严格保持缺失。这一契约与 stage 51 对 nf_headline_frac 的修复 (伪 0 改回未定义) 是同一条红线的两处落地: 零报道不等于零比率。整条链路无 LLM、无嵌入、无网络调用, 纯词典与 pandas 聚合, 给定语料与冻结的 jieba 及别名词典逐位可复现, 不属于面板中少数受浮点运算次序影响的网络类非确定列, 也无需任何缓存或线上密钥即可在离线环境零成本重算。另有一处口径细节值得记录: stage 13 的共现硬过滤在生产口径下开启 match_in_title, 即标题文本参与银行与金科词的邻近共现判定 — 这意味着标题命中的文章在过滤层就更容易进入面板宇宙, 本列的分母因此已经隐含了对标题信号的部分选择; 解释本列水平值时应意识到它测量的是过滤后宇宙内的标题主角比例, 而非全语料无条件比例, 跨样本比较须保持过滤口径一致。

【文献定位】
本列在媒体与金融文献谱系中的坐标由三条线索确定。第一条是媒体覆盖与资产定价的奠基线: Fang 与 Peress (2009) 证明是否被媒体报道及报道多寡 (extensive coverage) 与股票横截面收益系统相关, 确立了以报道存在性与篇数构造覆盖测度的范式; 本列在该范式之上向内深入一层, 在覆盖既定的条件下测量报道内部的显著性构成, 两者是广度与强度的关系而非替代关系。第二条是注意力测度线: Da、Engelberg 与 Gao (2011) 用搜索量构造直接注意力代理, 并指出媒体报道是含噪的间接注意力代理; 本列不试图直接测量投资者注意力, 而是测量媒体供给侧分配给目标银行的版面显著性 — 这是注意力的前置输入而非注意力本身, Chen 等 (2026) 的显著性与注意力可分离框架正是对这一区分的近期背书。第三条是媒体因果与供给侧线: Engelberg 与 Parsons (2011) 利用同一事件在不同地方报纸的差异化报道识别媒体报道对交易行为的因果效应, Dougal 等 (2012) 进一步证明具体撰稿记者的固定效应能解释市场反应的显著份额 — 两者共同说明报道的呈现方式 (含标题处理) 是编辑部的主动选择, 有独立于事件本身的市场后果, 这正是标题显著性值得单独测量的经济学理由。Fedyk (2024) 把这条线推进到位置效应的因果识别, 是本列构念效度最直接的现代锚点。在方法论上, 本项目的 firm-document 展开与银行级测度构造整体沿用 Hassan 等 (2019) 的公司层文本暴露范式 — 从海量文本中为每个公司-时期切出与其相关的信号切片再聚合; Bybee 等 (2024) 则代表了把新闻文本系统性结构化为经济状态测度的最新一代方法, 为新闻衍生面板变量的效度提供了总体性支持。中国语境下的近期应用包括 Ni (2024) 对中国上市公司媒体覆盖与披露语调的研究、Li (2026) 对中文年报文本语调与市场关注度关系的检验, 以及 Garcia (2025) 与 Gutknecht (2025) 分别就标题之外的情感分歧与媒体覆盖对企业风险的近期证据 — 这些工作共同表明媒体显著性类测度在中文语料与风险结果上的适用性已有平行先例。

【识别策略定位】
headline_frac 在项目识别体系中的角色是控制变量与机制调节变量, 不是任何一篇论文的 treatment 主轨。它的第一重用途是吸收显著性混杂: 各 paper 的处理变量多为 full 轨情感或属性测度 (如 P1 的 llm_vote_tone_full), 若语调效应部分来自高显著性报道更能动员注意力这一通道, 在回归中并入 headline_frac 可把语调的信息含量效应与版面显著性效应分离, 这直接对应 Fedyk (2024) 位置效应与 Tetlock (2007) 内容效应的文献分工。第二重用途是机制异质性切分: 按标题提及率高低分组或交互, 检验语调效应是否集中于叙事主角型报道, 为注意力通道提供机制证据 (Chen 等 2026 的显著性-注意力分离框架)。第三重用途在证伪链: stage 51 falsification 在 Non-Fintech 对照组上构造同构的 nf_headline_frac, 与本列形成处理组对对照组的显著性赛马 — 若金科报道的语调效应在控制了一般新闻的数量与显著性后依然稳健, 则支持金融科技特异性信息含量的假设 (Hassan 等 2019 的 PRisk 对 NPRisk 范式)。需要说明本列与项目各稳健性梯子的关系: headline_frac 是 track-agnostic 的元数据类度量 — 标题命中判定发生在 stage 11 原始标题字段上, 先于 stage 14 的三轨文本物化, 与 full/ctx/ss 三轨、co-primary 双轨嵌入、词典消融与政治词权重梯度均无参数依赖, 因此本列自身无三轨后缀、无 _lg 孪生、无消融变体, 这属于项目里唯一不能双轨的元数据度量类别, 是刻意设计而非遗漏。但当它与上述任何梯子的成员同时进入识别设计时, 梯子侧的铁律照旧约束: 三轨、双轨嵌入、各权重与各模型变体之间互为稳健性、不分主次, 各自 just-identified 并排进各自的回归, 禁止把多轨或多变体混进同一个 over-identified 的 Hansen J 检验 — headline_frac 作为共同控制变量出现在并排回归的每一列中是合规的, 它不改变各轨各自恰好识别的结构。

【与相邻测度的构念区分】
本列有六个容易混淆的邻居, 逐一划界。其一是 nf_headline_frac (stage 51, pipeline/falsification/controls.py): 公式同构 (mean(target_bank_in_title)) 但行宇宙完全不同 — 它算在 Non-Fintech 对照组上, 即全量银行新闻反连接减去面板文章后的补集, 语义是该银行的非金科新闻的标题提及率, 与本列构成处理组对对照组的镜像对; WP0 机械初判曾把本家族 producer 误标到 controls.py, 即因两列名尾缀相同, 实际本列 producer 是 encode.py, 须以本文 frontmatter 为准。其二是文章级源列 target_bank_in_title (stage 11): 那是 0/1 指示列, 本列是它在 bank-year 上的均值, 层级不同; 文章级列同时被 stage 51 直接消费。其三是金科侧的 fintech_in_title (stage 12, news_fintech.py): 判定的是金融科技关键词是否出现在标题, 实体侧不同 — 本列问的是银行是不是标题主角, 那一列问的是金科话题是不是标题主角, 两者交集 (银行与金科同上标题) 未被单列。其四是 mention_density (stage 11): 目标银行提及次数除以文档总字数的强度测度, 沿 Hassan 等 (2019) 的值加权暴露思路刻画正文内的相对篇幅, 与本列的标题二元位置信号互补 — 一篇通篇讨论某银行但标题未点名的深度稿, mention_density 高而 in_title 为零。其五是媒体广度类 (media_breadth 族): 数的是不同媒体来源家数, 刻画信息环境的多样性, 与显著性正交。其六是 stage 26 的 news_salience 与 attention_pct 族: 那是基于嵌入与语料分布的连续显著性测度, 依赖付费嵌入轨且受 co-primary 双轨架构约束, 而本列是零成本、词典可解释、逐位确定的离散位置信号; 两族可互为三角验证, 但构造原理与成本结构完全不同。最后与覆盖总量族 (n_articles, ln_news_coverage; Fang 与 Peress 2009 主锚) 的关系再强调一次: 覆盖答有多少报道, 本列答报道里有多大比例把银行放在标题, 分子分母均在同一留篇宇宙内, 保证与覆盖测度可比且可同时入模。

【已知局限与稳健性梯子】
第一, 词典依赖: 标题命中以别名词典与 Aho-Corasick 精确匹配为准, 别名表未覆盖的俗称、缩写或错别字会漏判, 造成向下的测量误差; 短名歧义消解取保守策略 (语境窗口命中排除词即作废), 进一步把误差方向压向漏检而非误报 — 这类经典测量误差在回归中的一般后果是系数衰减, 使基于本列的调节效应估计偏保守, 不制造虚假显著。第二, 标题字段质量: 判定用原始标题字段, 转载稿的标题改写会使同一稿件在不同媒体上取值不同; 项目在计数类列上区分物理口径与去重口径, 本列聚合在面板文章宇宙的物理行上, 转载的标题差异被如实保留, 解释时应视为媒体呈现层信号而非事件层信号。第三, firm-document 展开的不对称: 同一篇文章对写进标题的银行取 1、对仅正文提及的共现银行取 0, 这是构念本身的要求 (标题主角相对于配角), 但意味着本列在多银行文章密集的年份对大银行系统性偏高, 与规模相关 — 回归中与银行固定效应及规模控制同时使用可吸收该水平差异。第四, 防御性回退: 上游 schema 异常导致 target_bank_in_title 缺失时, runner 回退 in_title 置 0, 该路径下本列退化为全 0 而非 NaN; 正常管线不触发, 但审计面板时若见某年全体银行 headline_frac 恒为零, 应首查上游列是否缺失而非解读为真实现象。第五, 缺失语义: 零新闻 bank-year 保 NaN 是刻意契约, complete-case 使用本列的下游诊断会因此收缩有效样本, 这是选择进入报道宇宙这一更深层问题的正确显性化 — Fang 与 Peress (2009) 的无覆盖溢价文献正说明是否被报道本身携带信息, 强行填零反而掩盖它。第六, 稳健性路径: 本列是单列家族, 无自带参数梯子 (无阈值可调 — 二元命中无 cutoff, 无轨道 — 判定先于三轨物化), 其稳健性检验依赖三角验证而非变体并排: 与 nf_headline_frac 的处理-对照赛马、与 stage 26 嵌入显著性族的跨方法印证、与 mention_density 的位置-强度互证。若未来引入变体 (如限定严格标题对提前部分、或按标题内位置加权), 须遵循项目统一口径: 新变体与 canonical 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。第七, 时间维度的解释边界: 媒体行业的标题写作风格随年代漂移 — 门户与移动端兴起后标题党式点名密度普遍上升, 本列的年度水平因此含有全行业共同趋势成分, 识别设计中应由年份固定效应吸收, 只把银行间与银行内的相对变化当作信号; 这也是本列适合做控制与调节、不适合做单独 treatment 的又一结构性理由。第八, 与外部效度相关的提醒: 本列构造于报纸主导的语料 (原始普查中报纸类占绝对多数并被保留), 报纸标题的编辑规范与网络媒体不同, 将结论外推到社交媒体显著性时须谨慎, 近期文献如 Gutknecht (2025) 与 Garcia (2025) 对不同媒体层次显著性信号的差异化处理可作外推时的方法参照。综合而言, 本列的定位是一个词典可解释、零成本、逐位可复现的供给侧显著性控制与调节变量: 它以最小的构造假设捕捉编辑部把银行放上标题这一可观测的版面决策, 既不越俎代庖去直接测量投资者注意力, 也不与情感语调族争夺主轨地位, 而是为语调与属性主轨提供一层干净的显著性混杂吸收, 并在证伪与机制两条链上与同名对照列及嵌入显著性族相互印证; 上述所有局限均指向测量误差衰减或样本选择透明化, 方向上使基于本列的推断偏保守而非偏激进, 这与顶刊审稿人对控制类文本变量的稳健性预期一致。

## VAR: headline_frac

【变体差分】
headline_frac 是本家族唯一列, 即家族 canonical 本身, 差分节因此写清它相对于全项目命名系统的精确坐标而非相对于家族内其他变体的差异。命名维度上, 本列无轨道后缀 — 这不是 full 轨的省略写法, 而是 track-agnostic 语义: 标题命中判定在 stage 11 的原始标题字段上完成, 时间上与逻辑上都先于 stage 14 的三轨文本物化, full/ctx/ss 三轨改变的是正文情感测度的取材窗口, 不改变标题字段本身, 故本列在三轨架构下天然只有一个取值, 与之相区别的是 pos_frac_full 这类真轨道列 (后缀指示取材文本)。注意不要与 prepend_title 机制混淆: 三轨物化把标题拼接为正文第 0 句, 使情感测度也能看到标题内容, 但那影响的是语调列, 本列的判定输入始终是独立的标题字段。模型维度上, 本列无 per-model 变体 — 判定是纯词典 Aho-Corasick 匹配, 无 LLM 参与, 不存在 gpt54nano 或 finbert_cn 后缀的孪生列, 也不受 stage 21 三家投票或 stage 23 三 BERT 独立降级机制影响。阈值与权重维度上, 本列无梯子: 命中是二元的, 无罕见词 cutoff、无政治词权重、无消融变体可言; 唯一的参数敏感面在上游银行资格判定 (最少出现次数、上下半分布条件、语境窗口宽度), 但那些参数改变的是哪些文章行进入宇宙, 属全面板共同的过滤层而非本列特有旋钮。聚合维度上, 本列的分母是该 bank-year 面板文章宇宙的全部物理行 (与 n_articles 同基), 不是 LLM 有效标注子集 (n_articles_llm_valid 族), 因为词典判定对每一行都有定义; 分子分母同基保证与覆盖族测度可直接并列入模。缺失语义上, 本列遵循比例类契约 — 零新闻 bank-year 保 NaN, 与计数类零填列 (nf_n_articles 等) 形成刻意反差; 消费本列时若做 listwise 删除, 应意识到有效样本收缩到至少有一篇留篇报道的银行年份。tier 定级上, 本列为 core (标题显著性信号 canonical, 2026-07-10 签核扩围), dtype 为 double, 数学域 [0,1], 直觉读法: 取值 0.3 表示该银行该年的金科报道中三成把该银行写进了标题。与最易混淆的同名近邻再做一次显式切割: stage 51 的 nf_headline_frac 与本列共享分子构造逻辑却工作在互斥的文章宇宙上 — 本列的宇宙是留在面板里的金科报道, 那一列的宇宙是被反连接剔出面板的非金科银行新闻, 两列在证伪回归中同时出现时分别代表处理组与对照组的显著性水平, 绝不能互相替换或简单相加; 文章级的 target_bank_in_title 则是本列与那一列共同的上游原子, 三者构成源列、处理组聚合、对照组聚合的三角关系。消费建议上, 本列进入回归的典型姿态有三种: 作为水平控制直接并入协变量组, 吸收显著性混杂; 与情感主轨交互, 检验语调效应在标题主角型报道上是否更强, 为注意力通道提供机制证据; 或按中位数二分做子样本切割, 与全样本估计并排呈现。三种姿态都不改变各情感轨各自恰好识别的回归结构, 与项目关于并排稳健性的统一铁律兼容。跨年比较时建议同时报告该银行同年的 n_articles, 因为小分母年份的比率波动包含机械噪声, 分母透明化能防止把单篇报道的标题选择误读为显著性趋势的转折。

<!-- rendered-citations:begin -->
Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, Article 101670. https://doi.org/10.1016/j.jempfin.2025.101670
Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics, 46, e70100. https://doi.org/10.1002/mde.70100
Garcia, J. (2025). Beyond the headlines: Sentiment divergence and financial distress. Global Finance Journal, 66, Article 101126. https://doi.org/10.1016/j.gfj.2025.101126
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Fedyk, A. (2024). Front-page news: The effect of news positioning on financial markets. The Journal of Finance, 79(1), 5-33. https://doi.org/10.1111/jofi.13287
Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Ni, Y. (2024). Media coverage and disclosure of short-termism tone: Evidence from China. Accounting & Finance, 64(S1), 5107-5131. https://doi.org/10.1111/acfi.13328
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. The Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Dougal, C., Engelberg, J., García, D., & Parsons, C. A. (2012). Journalists and the stock market. The Review of Financial Studies, 25(3), 639-679. https://doi.org/10.1093/rfs/hhr133
Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. The Journal of Finance, 66(5), 1461-1499. https://doi.org/10.1111/j.1540-6261.2011.01679.x
Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. The Journal of Finance, 66(1), 67-97. https://doi.org/10.1111/j.1540-6261.2010.01626.x
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
