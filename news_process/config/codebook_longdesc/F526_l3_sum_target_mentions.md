---
family_id: F526
columns:
- sum_target_mentions
unit: 次数加总 (银行-年内逐篇目标银行实体提及次数之和, 无量纲计数)
formula: 'bank-year 层 sum_target_mentions = Σ_{article ∈ bank-year} target_bank_mention_count_article, 其中 target_bank_mention_count 为文章级目标银行实体提及计数(entity_context 抽取), 聚合口径为 groupby(bank, year) 上的 sum'
producer: pipeline\panel\encode.py
upstream:
- news_bank.py (article 级 target_bank_mention_count 抽取)
- panel/encode.py (bank-year 聚合)
citations:
- doi: 10.1093/rfs/hhy083
  type: journal
  authors: Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M.
  year: 2019
  title: 'Information, trading, and volatility: Evidence from firm-specific news'
  venue: The Review of Financial Studies
  vol: '32'
  issue: '3'
  pages_or_artno: 992-1033
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: "Diamond cuts diamond: News co-mention momentum spillover prevails in China"
  venue: Journal of Banking and Finance
  vol: '171'
  pages_or_artno: 107356
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: "10.1080/13504851.2025.2522167"
  type: "journal"
  authors: "Huang, Y.-T., Chiu, I.-C., & Hung, M.-W."
  year: 2025
  title: "Firm-specific news sentiment and stock returns: the impact of relevance and time frames"
  venue: "Applied Economics Letters"
  pages_or_artno: "1-10"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
new_dois: []
---

## CORE

【构念与来源】
sum_target_mentions 是银行-年面板上的一个 value-weighted 辅助聚合列, 度量某银行在某年内全部留篇报道中目标银行实体被提及的总次数。其上游是文章级 target_bank_mention_count(由银行实体识别模块 news_bank.py 在文本中定位目标银行的各种名称变体、简称、曾用名并逐篇计数得到), 在 panel/encode.py 的 bank-year 聚合阶段以 groupby(bank, year).agg(sum) 求和产出。与家族内 sum_mention_density(提及密度之和)、sum_doc_length/avg_doc_length(文档长度之和/均值)并列, 同属源码注释标注的"F. Value-weighted 辅助列"区块, 该区块整体锚定文本曝光/注意力度量文献中"以提及次数/密度作分子、加总到公司-期间层"的通用方法论谱系(与本列 citations 所列 Boudoukh et al. (2019, RFS) 一脉相承)——其方法论内核是: 简单的"是否提及"二元指示符会抹平提及强度差异, 而以提及次数/密度作为分子对篇幅或文章数加权求和, 能保留强度信息, 为后续构造 value-weighted(而非等权 equal-weighted)版本的注意力或情感测度提供分子端原料。sum_target_mentions 本身不是最终的经济学解释变量, 而是一个中间加总列: 它把"该银行在本年度被提及了多少次"这一原始计数信息从文章级搬运并累积到 bank-year 级, 供下游派生指标(如平均提及密度、提及次数占篇幅比等)复用分子, 也为审计"某银行-年样本量是否稀薄"提供一个比 n_articles 更细粒度的强度侧写。

【方法学与计算】
计算链路分两段。第一段在文章级: news_bank.py 对每篇原始"内容"列正文(stage 11 阶段, 早于 stage 14 三轨物化, 不含标题)扫描目标银行的规范名称、简称及历史曾用名, 逐次匹配累加, 得到 target_bank_mention_count(article, int)。这一步与 stage 13 共现硬过滤所用的银行实体识别共享同一套实体规范化字典, 但共现过滤只关心"是否存在"而不关心"提及几次", 因此二者判据口径不同——target_bank_mention_count 是计数而非布尔。第二段在 panel/encode.py 的 bank-year 聚合函数中: agg['sum_target_mentions'] = ('target_bank_mention_count', 'sum'), 即对同一 bank-year 分组内所有留篇文章的该计数值直接求和, pandas groupby.agg 会自动跳过缺失值(不参与求和分母膨胀)。需要注意, sum_target_mentions 使用的文章全集口径与家族内多数三轨(full/ctx/ss)测度不同——它没有 _full/_ctx/_ss 后缀分裂, 是 track-agnostic 的单一列, 因为 target_bank_mention_count 产自 stage 11 news_bank.py 的原始"内容"列正文匹配计数(上下半区拼接扫描, 不含标题命中; 标题命中另计入独立字段 total_with_title, 仅供该阶段前置阈值判定使用, 从不写入 target_bank_mention_count), 在流水线时序上先于 stage 14 materialize_ctx 物化 content_full/content_ctx/content_ss 与 prepend_title 逻辑——此时 content_full 这一列尚不存在, 该计数不可能基于 prepend_title 后的 content_full 抽取。它不随情感测度的三轨切分而重复计算, 三轨物化是下游 stage 14 才引入的正交处理。这一点与家族同区块内 llm_vote_score_w_sum{track}/pos_count_vw{track} 等显式三轨列形成对比: 后者服务于情感强度的三轨稳健性梯子(full/ctx/ss 各自 just-identified 并排, 互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 设定), 而 sum_target_mentions 服务于更基础的"关注度/曝光强度"侧写, 天然只有一个全文轨口径, 不需要也不应该拆分三轨。留篇门控口径与全仓一致: 2026-06-29 起门控已收敛为 full-only(llm_verified_full == True 决定"是否算一篇银行金科报道"), sum_target_mentions 参与聚合的文章全集与其余 bank-year 列共享同一行宇宙, 不存在门控口径漂移。

【文献定位】
本列的方法论谱系直接来自新闻文本注意力/曝光度量文献。Boudoukh, Feldman, Kogan & Richardson (2019, The Review of Financial Studies) 系统检验了公司特定新闻信息含量与交易量、波动率的关系, 强调新闻提及的频次与显著性(而非单纯的有无)是刻画信息流强度的关键维度, 为本列"以提及次数加总作为强度代理"的设计提供了实证支撑——该文的核心方法论贡献之一正是区分"新闻数量"与"新闻显著性"两个维度, 这与本仓库中 sum_target_mentions(数量侧)和 frac_front_page/avg_page_rank 等显著性侧列(同属"F3. 新闻体裁显著性"区块)的正交设计思路一致。更广的谱系上, 文本曝光/主题暴露度量文献(如电话会议文本主题曝光度量、气候风险文本暴露度量等分支)共同确立了"以文本提及次数/密度作分子、以某种权重加总到公司-期间层"的 value-weighted 曝光度量范式, sum_target_mentions 是该范式在本仓库银行-金科新闻语境下的分子端具体实现, 其正式文献锚点仍以 citations 所列 Boudoukh et al. (2019, RFS) 为准。以逐条命中计数构造实体层面文本强度代理的思路另有 Hassan, Hollander, van Lent & Tahoun (2019, Quarterly Journal of Economics) 的顶刊支撑: 该文以电话会议文本中风险相关词组的命中次数构造企业层面政治风险暴露测度, 论证提及计数本身即可承载有效的经济信息含量, 为本列以银行实体提及次数作分子的构造提供了顶刊层级的方法学正当性。中国市场语境下的新闻共同提及信号价值另见 Ge, Li & Zheng (2025, Journal of Banking and Finance) 对新闻共同提及动量溢出效应的实证, 印证提及频次类文本信号在中国金融市场中的信息含量。 沿此谱系再向前, Huang、Chiu 与 Hung (2025) 直接检验了「新闻与特定公司的相关度 (relevance)」对公司特定新闻情感效力的调节作用, 表明一篇报道在多大程度上「关于」该公司会改变其所携信号的强度, 为本列以目标银行提及次数加总操作化「报道与目标实体的相关度/强度」提供了动机层锚点。迁移边界: 该文的 relevance 取自第三方新闻情感数据库的既有打分 (供应商定义、黑箱), 并非本列这类透明的命中计数, 故不构成对本列计数口径的效度检验; 其层级为公司-新闻条目并对接股票收益 (高频), 本列在 bank-year 上取 sum 而非 mean, 与年内篇数量级共线, 使用时须与篇数分母一并读取; 原文对象为一般上市公司, 本列为目标银行。计数口径本身的测量误差另见 Iqbal 与 Pfarrer (2025): 该文指出多主体文本中的实体归属存在系统性测量误差, 提出以共指消解 (coreference resolution) 应对, 并以两项研究证明其可降低误差、提升文本分析的真实性。对本列的锚定仅限于「实体归属是实质性测量误差来源」这一一般命题——target_bank_mention_count 由 entity_context 的表层实体匹配得到, 不作代词与简称的指代还原, 因而 sum_target_mentions 应视为真实提及强度的保守下界而非无偏计数。边界须诚实标明: 原文语料为英文组织管理文本、单位为文档/组织, 且其立场为规范性的 (主张采纳该规则以逼近唯一正确做法), 与本仓库令各并排臂互为稳健性、不分主次的方法学取向不同; 原文所处理的归属问题在本 pipeline 中对应的是 ctx/ss 实体窗口轨, 不得据以论证本列计数公式或规则消融族的同构性。
## VAR: sum_target_mentions

【变体差分】
sum_target_mentions 是本家族唯一列, 无家族内平行变体(不区分轨道、模型、阈值、判据或滞后)。其精确语义为: 在给定 bank-year 分组内, 对该组所有留篇(full-only 门控通过)文章的 target_bank_mention_count 逐篇求和, 得到一个纯计数型加总指标, 单位是"次", 无量纲上限(理论上随该银行-年报道篇数与单篇提及密度同时增长)。它与家族外相邻列的区分要点有三: 其一, 与 n_articles(该 bank-year 的留篇篇数)不同——n_articles 是文章数, sum_target_mentions 是提及次数, 单篇文章可能多次提及目标银行, 故 sum_target_mentions 恒 ≥ n_articles(假设每篇至少提及一次目标银行, 这是留篇的隐含前提); 其二, 与 sum_mention_density(密度加总, 提及次数经文档长度归一化后再求和)不同——sum_target_mentions 是原始计数未做长度归一化, 因此篇幅长的报道即便提及密度不高也可能贡献较大的计数; 其三, 与三轨情感强度列(如 llm_vote_score_w_sum_full/_ctx/_ss)不同——那些列的分子是情感打分与提及权重的乘积、且按 full/ctx/ss 三轨并排(各自 just-identified、互为稳健性、禁止混入同一 over-identified Hansen J), 而 sum_target_mentions 只是纯粹的实体提及计数分子, 不含情感极性信息, 也不参与三轨稳健性梯子。使用该列作为回归控制变量或构造分母(如后续派生"平均提及次数"= sum_target_mentions / n_articles)时, 应注意其量纲会随年度报道总量规模变化, 通常需要做对数变换或按篇数归一化后再用于跨银行-年比较, 以避免大银行(报道基数天然更大)在原始计数尺度上主导回归结果。

<!-- rendered-citations:begin -->
Boudoukh, J., Feldman, R., Kogan, S., & Richardson, M. (2019). Information, trading, and volatility: Evidence from firm-specific news. The Review of Financial Studies, 32(3), 992-1033. https://doi.org/10.1093/rfs/hhy083
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond: News co-mention momentum spillover prevails in China. Journal of Banking and Finance, 171, 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Huang, Y.-T., Chiu, I.-C., & Hung, M.-W. (2025). Firm-specific news sentiment and stock returns: the impact of relevance and time frames. Applied Economics Letters, 1-10. https://doi.org/10.1080/13504851.2025.2522167
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
