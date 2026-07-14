---
family_id: F492
columns:
- staff_written_frac
unit: 比率/占比 (proportion, [0,1] ∪ NaN)
formula: 'bank-year mean of has_byline (作者具名且非通讯社); Stage 11 (news_salience) 物化 has_byline → Stage 40 (encode.py) agg[''staff_written_frac''] = (''has_byline'', ''mean'')'
producer: pipeline\filtering\news_salience.py (has_byline 物化) ; pipeline\panel\encode.py (bank-year 聚合) ; pipeline\panel\codebook.py (元数据条目)
upstream:
- has_byline
citations:
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The Information Role of the Media in Earnings News
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: Disagreement and Asset Prices
  venue: Journal of Financial Economics
  vol: '114'
  issue: '2'
  pages_or_artno: 226-238
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving Content to Investor Sentiment — The Role of Media in the Stock Market
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
staff_written_frac 度量一家银行在某年度全部报道中, 由"具名记者本人撰写"而非新闻通讯社通稿构成的比例。它源自 stage 11 (news_salience) 在文章级物化的布尔指示列 has_byline: 该列判定一篇报道是否携带具体记者署名 (作者行), 且该署名不落在通讯社/电头 (如新华社、中新社、路透) 的识别名单内。stage 40 (encode.py) 对这一文章级布尔量在 bank-year 维度取算术平均, 即得到本列 — 一个位于 [0,1] 区间(允许 NaN)的连续比率, 表示该银行当年报道中"记者原创撰写"占比的高低。设计上, has_byline 与其镜像列 is_wire (通讯社/电头识别) 并非严格互补: 既存在既非具名记者、也未命中通讯社识别名单的边界情形(如仅署"本报讯"、集体署名或匿名通稿), 也因此 staff_written_frac 与家族内的 wire_frac 通常不满足 staff_written_frac + wire_frac ≡ 1, 二者是两个独立测度而非同一构念的正反面。

本列所属的"新闻体裁显著性"批次(#8–#10, 2026-06-05 引入)与 frac_front_page / frac_front_section / avg_page_rank / wire_frac / frac_target_in_lead / coverage_active_days / coverage_continuity 同源, 均由 stage 11 直接解析原始报道的版面元数据(版面名称、页码、作者署名字段)得到, 不依赖情感 LLM/词典/BERT 三法中的任何一支, 也不依赖 fintech 词库或共现过滤判据。这批指标刻意与家族外两组既有测度做构念切割: 一是 media_authority(媒体级权威性加权, 度量"谁在报道"这一信源层面的可信度), 二是 herd/staleness 一族(度量"报道内容彼此雷同/滚动复制"这一产出端重复性)。staff_written_frac 度量的是投入端的原创性——记者是否亲自采写成稿——与信源权威、内容重复度是三个正交维度, 一篇高权威媒体转载的通讯社通稿(低 staff_written_frac、高 media_authority)与一篇小报记者独家原创(高 staff_written_frac、低 media_authority)是两种截然不同的组合, 论文行文中须避免把三者混为一谈。

【方法学与计算】
计算分两步。第一步(stage 11, news_salience.py)在文章级解析原始 Excel 元数据的作者/来源字段, 输出布尔列 has_byline: 若能提取出具体自然人姓名式署名, 且该署名/电头不匹配通讯社名单(与家族内 is_wire 共用同一解析入口但判据方向相反), 则记 True, 否则 False。该步骤与 stage 11 内的 is_front_page / is_front_section / page_rank / target_in_lead 共享同一版面解析基础设施, 是纯文本/元数据规则解析, 不涉及任何 API 调用或模型推理, 因而是确定性、$0 成本的信号。第二步(stage 40, encode.py agg 字典条目 `agg['staff_written_frac'] = ('has_byline', 'mean')`)把文章级布尔列在 bank-year 分组内取均值; pandas 的 groupby mean 对布尔列自动等价于 True 占比计算, 且对缺失值(某些历史归档报道无法解析出作者字段)按语义跳过而非计入分母, 故本列在极端情形(该银行当年全部报道均缺失作者字段)可能为 NaN。

本列是 track-agnostic(单轨)指标, 不参与家族内 full/ctx/ss 三轨或 co-primary 双轨嵌入体系, 也不落入任何消融梯度或 per-model 稳健性并排结构 —— 它衡量的是文章的物理/编辑属性(是否具名撰写), 与情感测度的文本窗口选取(全文/实体窗口/同句窗口)、嵌入模型选择、词典规则消融等维度无关, 因此在 codebook.py 的 `_SINGLE_TEXT_SPECS` 表中以 track='' 空值注册, 与三轨/双轨族群的注册方式(`_DUAL_TEXT_SPECS` 循环生成 `_full`/`_ctx`/`_ss` 三个变体)明确区分。读者若在检索面板列时看到本列没有 `_full`/`_ctx`/`_ss` 后缀, 这是设计使然而非遗漏。

【文献定位】
署名/来源原创性作为新闻信息质量的代理变量, 在会计与金融的媒体研究文献中有明确谱系。Guest (2021, *Journal of Accounting Research*)系统考察了媒体在盈余新闻传播过程中的信息角色, 强调媒体报道对信息传播效率的边际贡献取决于其生产方式与信息含量, 是本列"投入端原创性"构念的相关文献锚点——若照此逻辑推演, 记者独立采写的报道相较机械转发的通讯社通稿, 理论上更可能包含增量分析与背景信息, 但二者对投资者信息环境边际贡献的具体差异性大小, 需留待本项目实证部分检验而非文献先验断言。这一"报道形式特征而非情感极性"的代理变量思路, 与 Tetlock (2007, *Journal of Finance*)率先把媒体文本的可计量属性(而非事后归因的定性判断)引入资产定价研究的方法论取向一脉相承——staff_written_frac 与家族内 frac_front_page/avg_page_rank/frac_target_in_lead 共同构成一组不依赖情感极性、仅依赖报道"形式特征"的注意力与信息质量代理变量集。此外, Carlin, Longstaff & Matoba (2014, *Journal of Financial Economics*)关于信息来源异质性与资产价格分歧的研究, 为"报道来源(记者原创 vs. 通稿转载)可能系统性影响信息在市场参与者间的分散程度"这一机制提供了间接的理论支撑, 可作为本列在稳健性讨论中论证"来源原创性并非中性噪声"的辅助引注。

在本项目的面板体系中, staff_written_frac 通常作为控制变量或异质性分组变量出现, 用以排除"报道数量效应实为通稿灌水效应"的替代解释: 若某银行当年报道量激增主要由 wire_frac 上升驱动而非 staff_written_frac, 则该银行真实获得的媒体关注(记者主动采写、深度报道)可能被简单计数指标(n_articles)高估。

## VAR: staff_written_frac

【变体差分】
本列是其所属家族(新闻体裁显著性批次, l3_staff_written_frac)在 bank-year panel 中唯一落盘的成员列, tier=standard, 不存在同家族内需要相互区分的兄弟变体——因此本节说明的重点不是"与同家族他列的差异", 而是澄清它与相邻但不同家族的形似列之间的边界, 防止在检索/建模时误用。

首先, 与家族内并列注册但属于不同家族条目的 wire_frac(bank-year mean of is_wire)相比: 两者共享 stage 11 的同一段作者/来源字段解析代码路径, 但判据方向相反且不构成严格互补关系——一篇报道可能既未命中具名记者署名规则, 也未命中通讯社/电头识别名单(如仅署"本报讯"或完全匿名), 此时该篇在 has_byline 与 is_wire 上都记 False, 二者之和不必等于 1。分析时若需要"记者原创 vs. 非记者原创"的完全二分, 不能简单用 `1 - wire_frac` 替代 staff_written_frac, 必须分别取用两列各自的经验分布。

其次, 与家族外的 media_authority(媒体级权威性加权聚合)相比: media_authority 回答的是"发布该报道的媒体机构本身声誉/权威程度如何", 是媒体主体层面的加权; staff_written_frac 回答的是"这篇报道是否由该媒体的记者亲自采写", 是单篇报道生产方式层面的判据。一家高权威媒体既可能刊登记者原创深度报道, 也可能原样转发通讯社通稿, 二者在 staff_written_frac 上的取值可以截然不同, 因此不应把 media_authority 高低作为 staff_written_frac 的代理或替代。

再次, 与家族外的 herd_weight / staleness 一族(跟风衰减权重; article_staleness 语义重复度)相比: 后者度量的是内容在时间/文章间的雷同程度(产出端的重复性), 与本列度量的"生产方式是否为记者原创采写"(投入端的原创性)是两个不同的分析维度——一篇记者原创撰写的报道仍可能与既有报道在语义上高度雷同(记者跟风报道同一事件), 反之一篇通讯社通稿也可能因内容首发而语义新颖。二者在回归设定中应作为独立的控制变量分别纳入, 不可相互替代或合并为单一"原创性"指数。

最后需说明的是本列的取值退化情形: 若某银行-年份组合下全部报道均因元数据字段缺失(如早期归档报道无法解析出作者信息)而无法判定 has_byline, 则该 bank-year 观测在本列上记为 NaN(pandas groupby mean 对全 NaN 组的默认行为), 而非误记为 0——0 意味着"确认全部为非原创", NaN 意味着"该年度信息不可判定", 二者在解释上不可混淆, 使用者在做缺失值填补前应先核实是数据缺失还是真实全零。

<!-- rendered-citations:begin -->
Guest, N. M. (2021). The Information Role of the Media in Earnings News. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and Asset Prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Tetlock, P. C. (2007). Giving Content to Investor Sentiment — The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
