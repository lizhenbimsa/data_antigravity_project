---
family_id: F337
columns:
- hidden_adopt_kw_p75
- hidden_adopt_kw_p75_ctx
- hidden_adopt_kw_p75_ss
unit: 银行-年占比 (measured 分母上的比例, 值域 [0,1], 无量纲)
formula: 'hidden_adopt_kw_p{track} = mean_over_articles( 1{fintech_distinct_keywords{trk} < P75_year(fintech_distinct_keywords{trk})} AND 1{policy_cosine_sim{trk} >= P75_year(policy_cosine_sim{trk})} ), 逐篇指示先按 sim/freq 双双 notna 掩码为 measured, 未测量记 NaN 不进分母, 再按 (target_bank, year) groupby mean 聚合'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (被 runner.py 步骤7h 四象限循环调用; 面板列名/label 在 pipeline\panel\export.py 声明)
upstream:
- 15_fintech_intensity.parquet (fintech_distinct_keywords 词频 Track A / AC 去重关键词数)
- 16_article_policy_alignment.parquet (policy_cosine_sim 政策文本余弦相似度, vintage 主锚)
- 24_herd_decay.parquet (verified 域 semi-join, 仅 llm_verified_full 留篇集内文章参与聚合)
citations:
- doi: 10.1017/S0022109023000662
  type: journal
  authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: Journal of Financial and Quantitative Analysis
  vol: '59'
  issue: '6'
  pages_or_artno: 2618-2646
- doi: 10.1086/730053
  type: journal
  authors: Fan, H., Liu, Y., Qian, N., & Wen, J.
  year: 2024
  title: "Technological adoption and taxation: The case of China's Golden Tax reform"
  venue: Tax Policy and the Economy
  vol: '38'
  pages_or_artno: 101-122
- doi: 10.1111/ecin.12992
  type: journal
  authors: Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y.
  year: 2021
  title: The influence of hidden researcher decisions in applied microeconomics
  venue: Economic Inquiry
  vol: '59'
  issue: '3'
  pages_or_artno: 944-960
- doi: 10.1073/pnas.2203150119
  type: journal
  authors: Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al.
  year: 2022
  title: Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty
  venue: Proceedings of the National Academy of Sciences
  vol: '119'
  issue: '44'
  pages_or_artno: e2203150119
- doi: "10.1016/j.frl.2026.109668"
  type: "journal"
  authors: "Chen, M., Zhang, Z., & Liu, Y."
  year: 2026
  title: "Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China"
  venue: "Finance Research Letters"
  vol: "95"
  pages_or_artno: "109668"
- doi: "10.1017/s147474722400009x"
  type: "journal"
  authors: "Bauer, R., Broeders, D., & van Ool, A."
  year: 2025
  title: "Walk the green talk? A textual analysis of pension funds' disclosures of sustainable investing"
  venue: "Journal of Pension Economics and Finance"
  vol: "24"
  issue: "2"
  pages_or_artno: "297-325"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行金融科技报道的"言行错配"结构, 属于 stage 15/16 文章级政策对齐四象限体系的一支。runner.py 在每年度内, 对每篇通过留篇门控的文章同时观测两个维度: 一是该文章的金融科技关键词密度 (Track A, `fintech_distinct_keywords`, 即 Aho-Corasick 词典在文中命中的去重关键词数, 是词面层面"提没提金融科技"的计数指标), 二是该文章正文与政策语料的语义余弦相似度 (`policy_cosine_sim`, 由 stage 16 `article_policy_alignment` 产出, 刻画报道内容与官方政策话语在语义空间中的贴近程度)。runner 内部函数 `_classify_policy_quadrants` 按年度分别对两个维度做分位数变换 (`groupby('year').transform(quantile)`), 用同一年内的经验分布切出高/低两档, 再把每篇文章逐一放进"高词频×高相似""高词频×低相似""低词频×高相似""低词频×低相似"四个格子。本家族对应其中的"低词频 (< 年度 P75 分位) 且高相似度 (>= 年度 P75 分位)"格子, 命名为 hidden (闷声干大事): 这类文章不靠堆砌"金融科技""数字化转型"等关键词来制造声量, 但其论述内容在语义上与监管政策文本高度贴合 — 经验上更接近"业务已经在按政策方向做, 但报道不刻意贴标签"的隐性采纳, 与之相对的 token (高词频低相似, "洗科技") 和 subst (高词频高相似, "言行一致") 共同构成识别银行金融科技采纳"言"与"行"是否一致的三分类工具。P75 是该分位阈值梯子里最严格的一档: 只有词频排在本年度后 75% (即最不高频的四分之三) 且相似度排在本年度前 25% (即最贴合政策的四分之一) 的文章才计入分子, 因此 P75 版本比 P25/P50 版本对"低调但高度贴合"更挑剔, 识别出的是言行错配现象中最极端的一端。

【方法学与计算】
分类函数对 sim 列与 freq 列先各自在年度内取分位数作为该年阈值 (`ysim`/`yfreq`), 再定义 `measured = sim.notna() & freq.notna()`, `high_freq = freq >= yfreq`, `high_sim = sim >= ysim`, `hidden = (~high_freq & high_sim).astype(float).where(measured)`。这一 measured 掩码是 2026-06-11 的 fix(omni-g-runner-03/g-runner-11) 修复点: 早期实现对 NaN 与阈值比较会返回 False, 使 stage 15 三条优雅早退路径写出的全 NaN `policy_cosine_sim` 静默地把全部高词频文章误判为"低相似"从而灌入 token 格, 且未测量文章的 NaN 会残留在分母里制造伪零。修复后未测量的文章 (sim 或 freq 任一缺失) 指示值直接为 NaN, 不进入下游 `groupby(['target_bank','year']).agg(..., 'mean')` 的分母, 使占比的分母严格等于该银行该年已测量篇数, 全年无测量文章的银行-年输出 NaN 而非 0, 与项目"无数据=未测量"的缺失值语义铁律 (Allison 2001 §3 的完整个案分析告诫; F3 红线) 对齐, 避免虚假零值污染面板回归。文章级聚合前, 参与计算的样本域已经过 `_filter_to_verified_universe` 相对 24_herd_decay 的 semi-join, 即只有 `llm_verified_full == True` 的留篇集文章参与统计, 这与全库 full-only 留篇门控口径 (2026-06-29) 一致: full 轨的门控结果决定"这是不是一篇银行金融科技报道", ctx/ss 轨的四象限测度是在同一行宇宙 (full 留篇集子集) 上按各自轨道重算相似度与词频得到的稳健性变体, 不重新做门控判定。分位阈值网格由 `config/features.yaml::article_alignment.quadrant_percentiles` 配置 (默认 [25, 50, 75]), P50 是机制检验基准分割点, P25/P75 互为稳健性检验; 三档分位各自独立地做 just-identified 分类, 不应混入同一 over-identified 设定联合检验。
本家族的三个列对应词频与相似度所使用的文本轨道: full (标题+正文全文)、ctx (标题+实体窗口)、ss (标题+银行∧金科同句±N窗)。三轨严格并排, 各自独立完成分位数计算与四象限分类, 互为稳健性、不分主次, 禁止把三轨结果混入同一 over-identified Hansen J 设定联合估计。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行与金科词的同句共现时, `content_ss` 退化为全文正文 (`ss_is_fallback=True`), 该篇的 ss 轨词频/相似度仍照常计算, 只是文本来源退化为等同 full 的全文, 分母仍计入该银行该年已测量篇数 (`n_articles` 共享分母口径)。kw 轨 (Track A) 使用的 `fintech_distinct_keywords` 是 Aho-Corasick 词典命中去重计数, 与 int 轨 (Track B, `fintech_intensity_score`, TF-IDF × SIF 加权强度) 是两条平行的词频测度分支, F337 专属 kw 轨, 与同 P75 分位下的 int 轨家族 (F331 `hidden_adopt_int_p75`) 互为稳健性并排, 不应合并解读。sim 列本身也有 vintage 主锚 (`policy_cosine_sim`, 逐年滚动政策语料) 与 `_allv` 全语料静态锚点两个变体, F337 对应 vintage 主轨 (无 `_allv` 后缀), 与 F338 (`_allv` 孪生家族) 同样构成并排稳健性关系。

【文献定位】
把"言语声量"与"语义贴合度"分离开来识别真实政策采纳而非表面迎合, 呼应了 Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 对银行数字化能力的压力测试式识别思路: 该文强调不能仅凭银行是否宣称数字化转型来推断其真实数字能力, 必须借助外生冲击 (COVID-19) 下的行为表现来做甄别, 这与本家族用"高相似度但低词频"这一行为特征区分"闷声做实事"与"高调但空心"的银行金融科技报道在方法论精神上一致, 都是试图穿透文本表层信号去逼近真实行动。Fan, Liu, Qian & Wen (2024, *Tax Policy and the Economy*) 关于金税改革下企业技术采纳的研究提供了"采纳"这一构念在制度经济学中的对照: 该文用征管数字化冲击识别企业真实的技术采纳行为, 说明采纳强度的可信测量往往需要多个信号交叉验证, 而不能单靠自我报告或关键词堆砌, 这一逻辑支持本家族采用双维度 (词频×语义相似度) 而非单一关键词计数来定义"采纳"格子的做法。P25/P50/P75 三档分位阈值梯子本身是一种稳健性设计: Huntington-Klein 等 (2021, *Economic Inquiry*) 与 Breznau 等 (2022, *Proceedings of the National Academy of Sciences*) 均系统记录了研究者在处理同一数据集时, 因隐藏的、看似无关紧要的分析选择 (如阈值切点、样本筛选规则) 不同而导致结论出现可观差异的现象, 这构成了本项目坚持"多档分位阈值互为稳健性并排、禁止把某一档结果当唯一真值"这一设计原则的方法论依据: 与其在事后争论 P75 是否比 P50"更对", 不如把整条分位阈值梯子一并报告, 让读者自行判断结论对切点选择的敏感度。 晚近文本计量文献进一步为 hidden 这一格的构念独立性提供了直接支撑。Chen、Zhang 与 Liu (2026) 专门刻画中国企业「多行动少言说 (more action-less talk)」的创新披露沉默型态, 即实质投入高而文本声量低的一类企业, 为本家族「低词频但高政策相似度」作为可独立测量的型态提供了 2026 年中国语境的存在性证据; 其迁移边界在于该文的沉默由年报创新披露与专利/研发投入之间的落差界定, 层级为上市公司-年, 既不使用本家族「金科词频 < 年度分位 AND 政策余弦 >= 年度分位」的双分位判据, 也无三轨文本与 P25/P50/P75 阈值梯子, 故只在构念层对应而非测量层同源。Bauer 与 Broeders (2025) 用 NLP 文本分析对荷兰养老金年报披露同时构造「意识 (awareness, 声量维)」与「落实 (implementation, 具体性维)」两个均取自同一披露文本的测度, 并发现签署可持续投资倡议只提升了表述具体性、对 implementation 并无实质推进, 为本家族「在同一文本内并置声量维与对齐维、再交叉切成象限」的做法提供了文本计量层面的前沿实践参照; 须诚实写明的是, 该文与本家族同属两维皆取自文本内部、无外部行为验证的设计, 故上文借 Kwan, Lin, Pursiainen & Tai (2024) 所述「借外生冲击的行为表现甄别真实能力」的精神在本家族只是取向而非已实现的识别策略。迁移边界另有三点: 该文分析的是机构自述的年报披露而非第三方新闻报道, 其实质维为 NLP 抽取的披露具体性而非政策锚点余弦相似度, 且不做分位阈值二值化、无 2×2 象限, 亦无面板聚合与已测量分母口径。
## VAR: hidden_adopt_kw_p75

【变体差分】
本列是家族的 full 轨、无 `_ctx`/`_ss` 后缀的基准列, 词频维度取 `fintech_distinct_keywords` (对全文标题+正文文本做 Aho-Corasick 命中计数), 相似度维度取 vintage 主锚 `policy_cosine_sim` (亦基于全文/标题拼接文本计算的政策语义相似度)。年度分位阈值分别在 `fintech_distinct_keywords` 与 `policy_cosine_sim` 各自的当年经验分布上取 75 分位, 因此本列衡量的是"当年词频排在后 75% 且政策相似度排在前 25%"的文章占该银行当年全部已测量文章的比例。作为 P75 版本, 相较同名 P25/P50 家族, 本列对"低调"的门槛更松 (只需不落在词频前 25%) 而对"高相似"的门槛更严 (需落在相似度前 25%), 因此识别出的"隐性采纳"样本比 P50 更集中在语义高度贴合政策但确实极少提及关键词的极端子样本, 样本量通常小于 P25/P50 版本, 但错配信号更纯粹。该列参与 stage 15/16 依赖链, 分母域已被限定在 `llm_verified_full` 留篇集内, 与 P1 主轨情感处理变量共享同一行宇宙, 但本身不是任何 paper 的 canonical treatment, 而是机制检验/异质性分析的辅助测度。全年无已测量文章的银行-年输出 NaN, 不可与 0 混同; 使用该列做回归前应确认样本量随分位数收紧而收缩的样本选择性质, 并在结果解读中与同族 P25/P50/P75 三档并排报告而非单独援引。

## VAR: hidden_adopt_kw_p75_ctx

【变体差分】
本列在词频与相似度两个维度上均切换为 ctx 轨: 词频维度优先使用 `fintech_distinct_keywords_ctx` (若该列存在, 即基于"标题+实体窗口"文本重新做 Aho-Corasick 计数; kw 轨关键词计数属于 track-agnostic 元数据时才会退化复用 full 列, 并在 runner 日志中披露), 相似度维度使用 `policy_cosine_sim_ctx` (stage 16 对 ctx 轨文本单独计算的政策语义相似度)。年度分位阈值在 ctx 轨各自的经验分布上独立取 75 分位, 不与 full 轨共享阈值或样本排序, 因此即使某篇文章在 full 轨落入 hidden 格, 在 ctx 轨也可能因窗口截断改变了词频或相似度排名而落入其他格子。ctx 轨与 full 轨、ss 轨严格并排, 互为稳健性、不分主次, 三者不得混入同一 over-identified Hansen J 联合估计。行宇宙仍是 full-only 留篇门控确定的子集 (2026-06-29 口径): 是否计入某篇文章由 full 轨的 `llm_verified_full` 判定, ctx 轨只负责在该固定样本上重算词频与相似度分类, 不重新做门控判定。本列的意义在于检验"隐性采纳"这一言行错配现象是否对文本窗口的选取敏感: 若某银行在 full 与 ctx 两轨上的 hidden 占比方向一致, 说明该现象不是全文噪声词稀释造成的假象; 若两轨系统性偏离, 应结合 `_ctx` 列缺失时的优雅跳过日志核实是否属于旧 schema 未产出该轨。

## VAR: hidden_adopt_kw_p75_ss

【变体差分】
本列在词频与相似度两个维度上均切换为 ss 轨: 词频维度优先使用 `fintech_distinct_keywords_ss` (若存在), 相似度维度使用 `policy_cosine_sim_ss` (stage 16 基于"标题+银行∧金科同句±N窗"文本计算的政策语义相似度, 窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1)。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行实体与金融科技词在同一句 (或窗口半径内) 共现时, 该篇的 `content_ss` 退化为全文正文, `ss_is_fallback=True`, 但该篇仍照常参与本列的词频/相似度计算与四象限分类, 只是此时其词频与相似度的取值实质上等同于 full 轨的度量, 分母仍计入 `n_articles` 共享口径, 不会因回退而被剔除或单独计数。年度 75 分位阈值在 ss 轨自身的经验分布上独立计算, 与 full/ctx 两轨互不借用阈值或排序。ss 轨相比 ctx 轨的窗口更紧 (仅同句±N而非整个实体窗口), 因此在真正发生同句共现的文章上, ss 轨的词频统计更贴近"银行与金科词紧邻出现的那一句话说了什么", 是三轨中对上下文噪声最敏感、也最精细的一档; 与 full、ctx 两轨一样, 本列是并排的稳健性变体而非替代关系, 三者应联合报告而非互相取代, 且禁止混入同一 over-identified 设定的联合检验。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
Bauer, R., Broeders, D., & van Ool, A. (2025). Walk the green talk? A textual analysis of pension funds' disclosures of sustainable investing. Journal of Pension Economics and Finance, 24(2), 297-325. https://doi.org/10.1017/s147474722400009x
<!-- rendered-citations:end -->
