---
family_id: F519
columns:
- subst_adopt_kw_p25_allv
- subst_adopt_kw_p25_allv_ctx
- subst_adopt_kw_p25_allv_ss
unit: 银行-年内文章占比 (0-1 区间无量纲比率)
formula: 'subst_adopt_kw_p25_allv{trk} = mean_i[ (freq_i >= Q_year(freq, 0.25)) AND
  (sim_i >= Q_year(sim_allv, 0.25)) | freq_i, sim_i notna ], 其中 freq = fintech_distinct_keywords
  (Track A 关键词轨, kw 轨为 track-agnostic 元数据, _ctx/_ss 词频列无同轨变体则回退 full 列),
  sim = policy_cosine_sim_allv{_ctx,_ss} (Stage 16 文章-政策余弦相似度, _allv = 全年份静态锚点变体,
  与 vintage 主轨 policy_cosine_sim 并排互为稳健性), 分位阈值 Q 为年度内样本分位数 (groupby year transform
  quantile), 分母 = 该银行-年内 freq 与 sim_allv 双双非缺测的文章数'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (L312-335) + 四象限×锚点变体面板聚合循环
  (L2024-2090)
upstream:
- 15_fintech_intensity (fintech_distinct_keywords)
- 16_article_policy_alignment (policy_cosine_sim_allv / _allv_ctx / _allv_ss)
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: The Symbolic Management of Strategic Change; Sensegiving via Framing and
    Decoupling
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate
    Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial
    Pollution'
  venue: The Journal of Finance
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: 'Stress Testing Banks'' Digital Capabilities: Evidence from the COVID-19
    Pandemic'
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2618-2646
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability
    Disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
new_dois: []
---

## CORE

【构念与来源】
本家族与 F518 (subst_adopt_kw_p25, vintage 主轨) 共享完全相同的四象限分类逻辑与词频轨选择 (Track A, kw, 基于金融科技关键词 AC 自动机的去重命中计数), 二者的唯一差别在于政策相似度信号所依赖的锚点向量口径: F518 用的是随时间动态更新的 vintage 锚点 (`policy_cosine_sim`), 而本家族 (F519, `_allv` 后缀) 用的是全年份汇总的静态锚点 (`policy_cosine_sim_allv`)。这一 `_allv`/vintage 锚点二分是 2026-06-21 引入的稳健性并排设计: vintage 锚点让每年的政策相似度参照当年 (或该年及之前) 的政策文本集合动态计算, 能捕捉政策话语本身随时间演变的事实, 但也意味着同一篇文章在不同年份被评估时理论上可能因锚点漂移而得到不同的相似度分数; `_allv` (all-vintage, 全年份静态锚点) 则把全部年份的政策文本一次性合并为单一固定锚点集合, 用同一把尺子测量所有年份的文章, 换来跨年可比性但代价是丧失了对政策话语本身演化的敏感度。两个锚点变体在项目里被明确定位为"互为稳健性、不分主次"的并排测度, 而非相互替代或存在优先级——vintage 主轨更贴近"文章是否跟上了当期政策话语", `_allv` 更贴近"文章相对于金融科技政策议题整体基调的稳定对齐程度"。本家族测度的仍是组织理论"实质与象征管理"(substance vs. symbolism) 传统下的 Substantive (实质采纳) 象限: 词频信号 (说得多不多) 与政策语义对齐信号 (说得像不像政策) 同时"高"的文章, 被判定为言行一致的实质性金科投入报道, 理论根基见 Westphal & Zajac (1994, 1998, ASQ) 对公司治理措施"采纳"与"落实"脱耦的经典区分, 以及 Fiss & Zajac (2006, AMJ) 把该区分系统化为"象征管理"框架的后续工作。与本家族并列同源但落在其他家族文件的还有 Token (词频高、对齐低)、Hidden (词频低、对齐高) 两个象限, 以及使用 Track B (int, 连续型强度轨) 词频信号的姊妹家族矩阵——三档分位阈值 (P25/P50/P75)、两个词频轨 (kw/int)、两个锚点变体 (vintage/_allv)、三个文本轨 (full/ctx/ss) 共同构成本项目机制检验体系里最完整的一张稳健性梯子矩阵, 本家族只占据其中 kw 轨 × P25 阈值 × _allv 锚点这一个格子。

【方法学与计算】
计算发生在 `pipeline/panel/runner.py::_classify_policy_quadrants` 及其调用方——四象限×锚点变体的双层外循环 (L2024-2090)。外层第一维 `_anchor_variants` 依次遍历 `('', 'policy_cosine_sim')` (vintage 主轨) 与 `('_allv', 'policy_cosine_sim_allv')` (本家族所属分支, 仅当 `policy_cosine_sim_allv` 列存在时才追加, 否则跳过并记录 INFO 日志——这是 companion 关闭或旧 schema 下的优雅降级, 不产生本家族三列); 外层第二维遍历文本轨 (full/ctx/ss), 内层遍历词频轨 (kw/int) 与分位阈值 (P25/P50/P75)。对本家族而言, 锚点后缀固定取 `_allv`、词频轨固定取 kw、分位固定取 25: 逐篇分类先在年度内对词频列 (`fintech_distinct_keywords`, kw 轨) 与相似度列 (`policy_cosine_sim_allv`, 及其 `_ctx`/`_ss` 变体) 各自算出该年样本的 25 分位阈值 (`groupby('year').transform(lambda x: x.quantile(0.25))`), 再逐篇比较 freq ≥ 该年 P25 阈值 且 sim ≥ 该年 P25 阈值, 双高交叉记 Substantive 指示为 1, 否则为 0。分类前先做"未测量"掩码: 只有 freq 与 sim 同时非缺测的文章参与 0/1 判定, 任一缺测则指示值保持 NaN——这是 2026-06-11 (omni-g-runner-03/g-runner-11) 修复的历史缺陷收尾, 旧实现把 `NaN >= threshold` 隐式当 False, 会把 Stage 15/16 优雅早退产生的全 NaN 相似度列静默计成"低对齐", 系统性把高词频文章错分进 Token 格。之后按 `(target_bank, year)` 分组对逐篇 0/1/NaN 指示取 `mean`, pandas 的 `mean` 天然跳过 NaN, 隐含分母是"该银行-年内 freq 与 sim_allv 均已测量的文章数", 而非该银行-年全部文章数; 若某银行-年全部文章都未测量, 面板结果为 NaN 而非人为填零, 呼应 v6/F3 修复移除 `fillna(0.0)` 后确立的"无数据=未测量"契约 (Allison 2001 §3 关于强填零污染 TWFE 系数的论述)。⚠ 需要特别说明词频轨内部的一处非对称: kw 轨的 `fintech_distinct_keywords` 在本项目里是 track-agnostic 元数据 (该词典命中计数本身不区分 full/ctx/ss 三个文本窗口, 只有 int 轨 `fintech_intensity_score` 才产出真正的 `_ctx`/`_ss` 独立词频变体), 因此本家族 `_ctx`/`_ss` 两列在词频侧实际复用的是 full 轨 kw 词频列, 只有相似度信号真正切换到对应文本轨的 `policy_cosine_sim_allv_ctx`/`policy_cosine_sim_allv_ss`; 该"部分轨道化"处理在源码注释中逐条记录并伴随日志披露, 不构成静默口径漂移。

【文献定位】
本家族的构念根基与 F518 一致, 直接对接 Westphal & Zajac (1994, ASQ) 关于公司治理措施"采纳但不落实"的经典脱耦发现, 及其后续 (1998, ASQ) 与 Fiss & Zajac (2006, AMJ) 把该区分系统化为"象征管理"一般理论的工作: 三者共同的洞见是, 单纯观测组织是否"宣称采纳"某项制度期待, 会系统性高估实际行为变革, 唯有把"话语层面的采纳信号"与"行为/语义层面的落实信号"交叉, 才能识别出真正的实质性变革。在金融文献里, 与之平行的经验设计是气候与可持续性披露领域的 cheap talk 甄别: Bingler, Kraus, Leippold & Webersinke (2024, *Journal of Banking & Finance*) 用文本相似度刻画企业气候披露相对气候倡议、碳排放与声誉风险的"廉价谈话"程度; Duchin, Gao & Xu (2025, *The Journal of Finance*) 用资产市场证据检验企业可持续性投入的真实性与漂绿边界; Kim & Lyon (2015, *Organization Science*) 区分了企业可持续性披露中的"过度渲染"(greenwash) 与"过度谦逊"(brownwash) 两种脱耦方向——三者与本家族"词频高但语义对齐低=Token/洗科技话术"的构造思路同构, 均是用双信号交叉而非单一信号来甄别"言行是否一致"。银行数字化转型的实证背景参照 Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 关于银行数字能力压力测试的证据, 该研究说明银行在报道/宣称层面的数字化投入未必与实际韧性能力对齐, 与本家族甄别"报道是否言行一致"的核心问题意识一致。本家族相较 F518 的增量文献意义在于锚点稳健性设计本身: `_allv` 全年份静态锚点变体验证的是, 上述实质-象征甄别结论是否敏感于"政策话语参照系是否随时间动态调整"这一测度选择, 若 vintage 与 `_allv` 两个锚点口径下的结论方向一致, 说明分类结果并非由锚点漂移的人为产物驱动。上游信号 (词频=Stage 15 fintech_intensity 关键词计数; 相似度=Stage 16 article_policy_alignment 余弦相似度) 各自在其所属家族文件里另有独立方法学与文献定位, 本节聚焦四象限分类本身及 `_allv` 锚点稳健性设计的构念来源, 不重复展开上游信号的构造细节。

## VAR: subst_adopt_kw_p25_allv

【变体差分】
本列是家族的 full-track 主轨, 也是三个 `_allv` 锚点、kw 词频轨、P25 阈值版本中信号来源全部取 full 文本 (标题+正文全文) 的一列: 词频信号 = full 轨 `fintech_distinct_keywords` (Stage 15 AC 自动机在全文范围内扫描去重后的金融科技关键词数), 相似度信号 = `policy_cosine_sim_allv` (Stage 16 用 full 文本与全年份静态政策锚点算余弦相似度, 区别于 F518 无 `_allv` 后缀列所用的 vintage 动态锚点 `policy_cosine_sim`)。分类判据是"freq ≥ 该年 P25 分位数 AND sim_allv ≥ 该年 P25 分位数"双高交叉, 两个阈值都取偏低的第 25 百分位, 相对 P50/P75 姊妹家族门槛更宽松。本列与 F518 无后缀主轨的对照关系是本家族三列共同的核心稳健性看点: 二者共享同一套词频信号与同一 P25 阈值口径, 差异完全集中在相似度锚点是动态 (vintage) 还是静态汇总 (`_allv`), 若两者的银行-年占比走势高度一致, 说明"实质采纳"占比的时序模式不是锚点动态漂移的产物; 若出现分歧, 则提示政策话语本身的年度演变对分类结果有实质影响, 需要在稳健性附录中并排陈列而非只报告其中一个。行级分母是该银行-年内 freq 与 sim_allv 同时非缺测的 full 轨文章数, 全体缺测的银行-年在本列输出面板级 NaN。本列与家族内 `_ctx`/`_ss` 姊妹列、以及与另一并列的 P50/P75 阈值梯子、int 词频轨姊妹家族均是互为稳健性、不分主次的并排测度, 严禁将其中任意组合混入同一个 over-identified 工具变量估计。

## VAR: subst_adopt_kw_p25_allv_ctx

【变体差分】
本列与 canonical 主轨 (subst_adopt_kw_p25_allv) 的差异集中在相似度信号的文本窗口: 本列的 sim 取 `policy_cosine_sim_allv_ctx` (标题+实体窗口文本, stage 14 `ctx_materializer` 物化的 content_ctx, 与全年份静态锚点向量的余弦相似度), 而非 full 轨的全文相似度; 阈值同样按年度内 ctx 轨样本重新计算 P25 分位数, 与 full 轨阈值相互独立、不共用同一分位切点。词频信号侧保持项目既定的"kw 轨 track-agnostic"处理: `fintech_distinct_keywords` 本身不产出独立的 `_ctx` 变体, 本列词频仍复用 full 轨词频列, 只有相似度一侧真正切到 ctx 文本窗口——这一点在 `pipeline/panel/runner.py` 装配 `_freq_eff` 的分支逻辑与源码注释中逐条记录、非静默复用。ctx 轨与 full 轨、ss 轨三者互为稳健性并排比较: ctx 把关注范围收窄到银行与金融科技实体附近的局部语境, 若某篇报道全文夹杂大量与金融科技无关的内容 (如银行常规业务报道里偶然提及金融科技), ctx 轨的相似度信号会比 full 轨更贴近"报道主体是否真谈金融科技政策", 但也可能因窗口过窄丢失全文语境里分散表述的政策关联信息; 三轨各自 just-identified、禁止混入同一 over-identified Hansen J 估计, 留篇门控仍以 full 轨 `llm_verified_full` 为唯一判据, 本列的分子分母均限定在该子集内计算, ctx/ss 属条件测度而非独立样本口径。分母是该银行-年内 ctx 轨 sim_allv 与 (复用的) full 轨 freq 双双非缺测的文章数, 与 full 轨主列的分母未必相等 (ctx 相似度可能因实体窗口抽取失败而缺测, 即便 full 轨相似度已测量)。本列与 F518 系列的对应 ctx 列 (subst_adopt_kw_p25_ctx, vintage 锚点) 构成锚点维度的另一组稳健性对照, 二者差异同样只在相似度锚点是否随时间动态更新。

## VAR: subst_adopt_kw_p25_allv_ss

【变体差分】
本列与 canonical 主轨的差异同样局限于相似度信号的文本窗口, 但收窄程度比 ctx 更严格: 本列的 sim 取 `policy_cosine_sim_allv_ss` (标题+银行∧金科同句±N窗文本, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认±1句, 与全年份静态锚点向量的余弦相似度), 阈值同样按年度内 ss 轨样本独立计算 P25 分位数。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行与金融科技词的同句共现, 则该文章的 `content_ss` 在 Stage 14 物化阶段已回退为全文 body、`ss_is_fallback` 标记为 True, 其相似度计算实质上退化为接近 full 轨的信号 (共享 `n_articles` 分母口径); 若上游 `FINTECH_AC` 词典本身为 None, 则全体文章的 `*_is_fallback` 标记为 True, 整族信号优雅降级但不产生虚假的高置信度分类。词频信号侧同样复用 full 轨 `fintech_distinct_keywords` (kw 轨 track-agnostic, 无独立 ss 变体)。ss 轨相对 ctx 轨的甄别逻辑更严苛: 只有银行与金融科技词在同一句子里紧邻出现的报道, 才被认为是"真正在谈银行的金融科技动作"的强信号语境, 因此 ss 轨的相似度信号理论上比 ctx/full 更少受无关上下文稀释, 但代价是更容易触发回退 (样本覆盖面更窄)。full/ctx/ss 三轨在本列上同样是互为稳健性、各自 just-identified 并排的测度选择, 不设主次, 更不得混入同一个 over-identified 工具变量估计式; 三轨聚焦的是文本窗口口径差异, 与家族内部的 P25/P50/P75 阈值梯子、kw/int 词频轨选择、以及 vintage/`_allv` 锚点选择彼此正交、不交叉组合报告。分母是该银行-年内 ss 轨 sim_allv (含回退样本) 与复用的 full 轨 freq 双双非缺测的文章数。留篇门控同样以 full 轨 `llm_verified_full` 为准, 本列是该子集上的条件测度。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change; Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress Testing Banks' Digital Capabilities: Evidence from the COVID-19 Pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
<!-- rendered-citations:end -->
