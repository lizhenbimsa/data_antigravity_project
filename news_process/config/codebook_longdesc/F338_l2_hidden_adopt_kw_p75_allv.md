---
family_id: F338
columns:
- hidden_adopt_kw_p75_allv
- hidden_adopt_kw_p75_allv_ctx
- hidden_adopt_kw_p75_allv_ss
unit: 银行-年占比 (0-1 区间比例, 分母=当年已测量篇数)
formula: 'bank-year 内满足 [fintech_distinct_keywords < P75_year(freq)] AND [policy_cosine_sim_allv >= P75_year(sim)] 的文章占比 (sim/freq 双双 notna 的已测量文章为分母, mean over _is_hidden_kw_p75_allv{track} indicator)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (逐篇分类) + runner.py 四象限外层三重循环 (anchor × sim_track × pct) 聚合
upstream:
- 15_fintech_intensity.parquet::fintech_distinct_keywords (AC 原始去重关键词数, kw 词频轨, track-agnostic 元数据)
- 16_article_alignment.parquet::policy_cosine_sim_allv{,_ctx,_ss} (Stage 16 article_policy_alignment 产出, 全年份静态锚点政策对齐余弦相似度)
- 24_herd_decay.parquet (df_exploded, verified 域 semi-join 对齐分母)
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
- doi: 10.1073/pnas.2203150119
  type: journal
  authors: Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al.
  year: 2022
  title: Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty
  venue: Proceedings of the National Academy of Sciences
  vol: '119'
  issue: '44'
  pages_or_artno: e2203150119
- doi: 10.1111/ecin.12992
  type: journal
  authors: Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y.
  year: 2021
  title: The influence of hidden researcher decisions in applied microeconomics
  venue: Economic Inquiry
  vol: '59'
  issue: '3'
  pages_or_artno: 944-960
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
本家族衡量银行金融科技报道的"隐性采纳" (hidden adoption) 现象: 一篇文章若与监管政策/战略语汇高度贴合 (policy_cosine_sim 高) 却几乎不提金融科技关键词 (fintech_distinct_keywords 低), 说明该报道所指涉的实践更接近"闷声干大事"而非公开宣传式的科技营销。这是 runner.py 中"四象限"分类法 (token adoption / hidden adoption / substantive adoption / irrelevant) 的一个格子, 与家族兄弟测度 token_adopt_kw_p75_allv (高词频·低相似度, "洗科技"/象征性采纳)、subst_adopt_kw_p75_allv (高词频·高相似度, 言行一致的实质性采纳) 共同构成一个 2×2 判别矩阵, 分类边界均取自当年 (year 内) 分位数, 而非跨年固定阈值, 以吸收行业整体报道热度的年度漂移。构念上呼应组织理论中"decoupling" (政策承诺与实际行为脱耦) 与技术采纳文献中"象征性 vs 实质性合规"的区分传统: 一家银行可能在公开文本 (新闻通稿、年报措辞) 中大量堆砌"金融科技""数字化转型"等热词却缺乏与监管/战略议程的深度绑定 (token), 也可能反过来在极少提及关键词的低调报道中呈现出与政策语汇高度一致的深层布局 (hidden)。分母口径遵循项目 F3 红线: 只在 policy_cosine_sim_allv 与 fintech_distinct_keywords 双双非缺失 ("已测量") 的文章上参与分类与聚合, 未测量文章既不计入分子也不计入分母 (而非静默填零), 银行-年若全年无一篇已测量文章则输出 NaN, 与 Allison (2001) 及 Heckman (1979) 关于测量缺失不应等同于"零效应"的方法论告诫一致。
【方法学与计算】
计算分两层: 逐篇分类层与银行-年聚合层。逐篇分类层由 `_classify_policy_quadrants` 完成: 对齐样本 (df_align, 已经过 `_filter_to_verified_universe` 与 24_herd_decay 的 (docid, target_bank) semi-join, 收敛到 stage 21 语义精筛后的 LLM-verified 篇集, 避免约 26.8% 假阳性文章污染年度分位数阈值与四象限分母) 内, 按 year 分组对相似度列与词频列各自计算 P75 分位数作为该年动态阈值 (ysim/yfreq), 再对相似度、词频均非缺失的文章逐篇判定: 词频 < 阈值 且 相似度 >= 阈值 → hidden 指示为 1, 其余测量到位但不满足该组合的文章指示为 0, 未测量文章指示为 NaN (通过 `.where(measured)` 显式设空, 不落入 0/1 二元)。聚合层按 (target_bank, year) 分组对该 0/1/NaN 指示序列取 `mean`, pandas 的 groupby mean 默认跳过 NaN, 因此聚合结果的隐含分母是该银行-年内相似度与词频双双可测的文章篇数, 而非全部报道篇数; 若某银行-年一篇可测文章都没有, 聚合表中该格不出现或为 NaN, 面板导出阶段刻意不做 `fillna(0.0)` (v6/F3 修复移除了旧版本的兜底填零, 因为"未观测"与"观测到零采纳"是两种不同的数据生成过程, 前者填零会把测量缺失误判为强证据的负面信号, 系统性压低 TWFE 回归中受 stage 15 早退路径影响样本的系数估计)。本家族三列共享 kw 词频轨 (fintech_distinct_keywords, AC 自动机原始去重关键词计数, 未做 TF-IDF/SIF 加权, 与家族外的 int 轨 fintech_intensity_score 并列不混用) 与 P75 分位阈值 (与 P25/P50 分位阈值家族互为稳健性并排, P50 是项目机制检验基准、P25/P75 是稳健性检验), 并共享 `_allv` "全年份锚点"变体: 与默认的 vintage 主轨 (逐年滚动更新的政策语汇锚点) 相对, `_allv` 使用 stage 15/16 companion 产出的全语料静态锚点计算 policy_cosine_sim_allv, 即锚点向量取自整个语料期而非按年重估, 用于检验四象限分类结论是否对锚点估计窗口敏感 (稳健性轨, 非主次关系)。
【文献定位】
金融科技新闻文本与银行战略/监管政策语汇的对齐测度直接承袭 Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 关于银行数字能力压力测试的证据框架, 该文强调银行数字化能力存在难以从公开披露话语中直接观测的隐性维度, 需要借助文本-政策对齐等间接测度加以刻画, 这正是本家族"hidden adoption" 象限存在的经验基础: 部分银行的金融科技实践并不体现在高频关键词堆砌的公开叙事中, 而是体现在与监管政策议程高度贴合但关键词稀疏的报道里。四象限判别法的可复现性顾虑 (同一构念在不同分析流程/参数选择下得出不同结论) 呼应 Breznau et al. (2022, *Proceedings of the National Academy of Sciences*) 关于"许多研究者用同一数据同一假设仍产生隐藏的不确定性宇宙"的多分析师范式发现, 以及 Huntington-Klein et al. (2021, *Economic Inquiry*) 对应用微观经济学中"隐藏的研究者决策"如何系统影响结果的度量, 二者共同支持本家族在阈值 (P25/P50/P75)、锚点 (vintage/`_allv`)、词频轨 (kw/int)、文本轨 (full/ctx/ss) 四个维度上同时铺设稳健性梯子、而非只报告单一参数组合下的点估计的设计取向。三轨 (full/ctx/ss) 铁律适用于本家族: full/ctx/ss 各自独立 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 检验; ss 轨遵循项目统一的回退语义 (镜像 ctx: 无银行∧金科同句共现时词频列缺同轨变体, 优雅回退复用 full 轨的 track-agnostic 关键词计数列, 并在日志中披露)。留篇门控口径与项目 2026-06-29 起统一的 full-only 规则一致: 是否判定"一篇银行金科报道"只看 `llm_verified_full`, ctx/ss 轨是 conditional-on-full 的测度子集, 行宇宙由 24_herd_decay 的 verified 域界定, 不因 ctx/ss 自身文本降级而扩张或收缩样本宇宙。 在测度构造层面, Bauer 与 Broeders (2025) 提供了同源的前沿实践参照: 该文用 NLP 文本分析对荷兰养老金年报披露同时构造「意识 (awareness, 声量维)」与「落实 (implementation, 具体性维)」两个均取自同一披露文本的测度, 并检验基金规模与签署可持续投资倡议对二者的差异化影响, 发现签署只提升了表述具体性、对 implementation 并无实质推进。这与本家族在同一篇报道内并置关键词声量维与政策对齐维、再交叉切出 hidden/token 象限的设计同属「两维皆取自文本内部、不引入外部行为验证」的一类做法, 因而其结论边界亦为本家族所共享: 象限判别刻画的是文本内部两维的相对位置, 而非已证实的真实采纳行为。迁移边界须一并写明: 该文分析的是机构自述的年报披露文本, 本家族分析的是第三方新闻报道; 其实质维是 NLP 抽取的披露具体性, 本家族的对齐维是全年份静态锚 `policy_cosine_sim_allv` 上的余弦相似度; 且该文不做分位阈值二值化、无 2×2 象限, 亦无面板聚合与已测量分母口径, 故不能援引其为本家族阈值/锚点/词频轨/文本轨四维梯子的正当性依据。
## VAR: hidden_adopt_kw_p75_allv

【变体差分】
本列是家族的 full 轨主变体: 相似度取自全年份静态锚点列 `policy_cosine_sim_allv` (锚点后缀 `_allv`, 未附加 `_ctx`/`_ss`), 词频取自 track-agnostic 的 `fintech_distinct_keywords` (kw 轨, 不随文本轨切换), 两者均在文章的完整正文+标题拼接文本 (`content_full`, prepend_title) 上计算, 年度分位阈值取 P75。数值上代表"高对齐、低词频"文章在该银行-年已测量样本中的占比, 使用全语料期固定政策锚点而非逐年滚动锚点, 因此对政策语汇本身随时间漂移不敏感, 更适合捕捉银行在长时间窗口内相对于稳定政策基准的持续性隐性布局, 而非某一年政策热点骤变带来的短期对齐波动。P75 意味着门槛较宽松 (词频落在年度后 75% 分位即算"低词频", 相似度落在年度前 25% 即算"高相似度"), 相比 P50 基准更容易被划入 hidden 象限, 因而本列在稳健性梯子上偏向"宽口径"一端, 与 P25 (最严口径) 互为对照, 三者共享同一分类算法与同一 full 轨输入列, 差别只在年度分位阈值百分位, 彼此并列、不设主次。本列与同家族 `_ctx`/`_ss` 两列构成三轨并排关系, 互为稳健性检验, 本列不因另两列缺失或降级而调整口径, 也不与它们共享分位阈值或分母; 若需要联合估计, 应各轨分别 just-identified 检验, 不得混入同一 over-identified 设定。该列继承 runner.py 四象限循环中 anchor 变体外层、sim_track 中层、pct 内层的三重嵌套命名规则, full 轨对应 `_sim_sfx=''` 分支, 即列名中不出现 `_ctx`/`_ss` 后缀。

## VAR: hidden_adopt_kw_p75_allv_ctx

【变体差分】
本列相似度改取 ctx 轨政策对齐列 `policy_cosine_sim_allv_ctx` (标题+银行/金科实体窗口文本上计算的全年份静态锚点相似度), 词频列优先取同轨变体 `fintech_distinct_keywords_ctx` (若该同轨变体不存在, 因 kw 轨关键词计数在当前生产 schema 下是 track-agnostic 元数据, 优雅回退复用 full 轨 `fintech_distinct_keywords` 并在日志中记录 "词频列无同轨变体, 复用 full"), P75 年度分位阈值分别对 ctx 轨相似度、词频重新计算 (与 full 轨阈值不共享, 即便词频列因回退而与 full 轨数值相同, 分位阈值仍按 ctx 轨相似度列的年度分布单独估计)。该列考察"实体窗口视角"下的隐性采纳强度: 只聚焦标题与目标银行/金科实体附近文本时, 政策语汇对齐度是否依然高、关键词密度是否依然低, 用于排除文章其余无关段落 (如无关业务板块、行业综述性文字、非银行金科主线的插叙) 对判别结果的稀释或污染。ctx 轨的分类行宇宙仍受项目 full-only 留篇门控约束: 是否算作"一篇银行金科报道"由 `llm_verified_full` 决定, ctx 轨只是在该行宇宙子集上换用更聚焦的窗口文本重新计算相似度与 (若可得) 词频, 不会因 ctx 文本本身质量差异而扩张或收缩参与分类的篇数。若 stage 15/16 companion 关闭导致 `policy_cosine_sim_allv_ctx` 缺列, 则 runner.py 在构建 `_sim_tracks` 时直接跳过该轨的分类与聚合循环, 对应面板列在导出前不会被生成, 而非以 NaN 占位写出全空列; 已生成的场景下, 该列与 full/ss 轨并排、互为稳健性, 各自独立 just-identified, 禁止混入同一 over-identified Hansen J 设定联合检验。

## VAR: hidden_adopt_kw_p75_allv_ss

【变体差分】
本列相似度改取 ss 轨政策对齐列 `policy_cosine_sim_allv_ss` (银行与金科关键词同句共现窗口文本上计算的全年份静态锚点相似度), 词频列同理优先取同轨变体 `fintech_distinct_keywords_ss`, 缺失则回退复用 full 轨列并披露。ss 轨是三轨中判定口径最严格的一支: 要求银行实体与金科关键词出现在同一句 (`config/filtering.yaml::context_window.ss_sentence_radius` 默认窗口半径 1), 若某篇文章不存在这样的同句共现, 则该篇的 `content_ss` 回退为全文正文 (`ss_is_fallback=True`, 与 ctx 轨回退语义镜像对称, 共享 n_articles 分母), 对应地本列在该篇上的相似度/词频取值退化为等同全文轨的近似口径, 而非缺失, 使得回退发生率高的银行-年不会被系统性地从 ss 轨分母中剔除。本列衡量的是"银行与金科话题在同一句紧密绑定"的高精度语境下, 隐性采纳象限的占比是否稳健: 相比 ctx 轨更宽的实体窗口, ss 轨进一步收窄到句子级共现, 因此对"报道正文虽长但银行与金科话题实际上并未紧密关联"的稀释噪音有更强的抵抗力, 代价是当同句共现本身较稀疏时更依赖回退机制, 数值上会更接近 full 轨。与 full/ctx 轨并排互为稳健性, 三者均各自 just-identified, 使用各自独立的年度分位阈值与 (在可得同轨列时) 独立的词频分母, 不得混入同一 over-identified Hansen J 联合估计。ss 轨同样受 stage 21 full-only 留篇门控约束, 参与分类的行宇宙与 full/ctx 轨一致, 差异仅体现在相似度与词频取值的文本口径上, 而非样本篇数本身。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Bauer, R., Broeders, D., & van Ool, A. (2025). Walk the green talk? A textual analysis of pension funds' disclosures of sustainable investing. Journal of Pension Economics and Finance, 24(2), 297-325. https://doi.org/10.1017/s147474722400009x
<!-- rendered-citations:end -->
