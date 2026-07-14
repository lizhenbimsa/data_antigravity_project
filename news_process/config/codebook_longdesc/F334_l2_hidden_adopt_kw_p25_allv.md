---
family_id: F334
columns:
  - hidden_adopt_kw_p25_allv
  - hidden_adopt_kw_p25_allv_ctx
  - hidden_adopt_kw_p25_allv_ss
unit: bank-year 占比 (0-1 区间, 已测量文章中被判为"隐性采纳"象限的篇占比; 无量纲)
formula: "对每篇 (docid, target_bank) 文章: high_freq = fintech_distinct_keywords >= 年度25分位阈值; high_sim = policy_cosine_sim_allv >= 年度25分位阈值; hidden = (~high_freq) & high_sim (仅对 freq/sim 双双非缺测行赋值, 否则该行分类为 NaN); hidden_adopt_kw_p25_allv = groupby(target_bank, year) 对 hidden 指示取 mean (跳过 NaN, 分母=已测量篇数)"
producer: news_process/pipeline/panel/runner.py::_classify_policy_quadrants + news_process/pipeline/panel/runner.py (7h-token 四象限聚合循环, L1997-2104)
upstream:
  - 15_fintech_intensity.parquet (fintech_distinct_keywords, policy_cosine_sim_allv[_ctx/_ss])
  - 24_herd_decay.parquet (verified 语义精筛集, 用于 _filter_to_verified_universe 半连接对齐)
citations:
  - doi: 10.1017/S0022109023000662
    type: journal
    authors: Kwan, A., Lin, C., Pursiainen, V., & Tai, M.
    year: 2024
    title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
    venue: Journal of Financial and Quantitative Analysis
    vol: 59
    issue: 6
    pages_or_artno: 2618-2646
  - doi: 10.1073/pnas.2203150119
    type: journal
    authors: Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al.
    year: 2022
    title: "Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty"
    venue: Proceedings of the National Academy of Sciences
    vol: 119
    issue: 44
    pages_or_artno: "e2203150119"
  - doi: 10.1111/ecin.12992
    type: journal
    authors: Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y.
    year: 2021
    title: "The influence of hidden researcher decisions in applied microeconomics"
    venue: Economic Inquiry
    vol: 59
    issue: 3
    pages_or_artno: 944-960
  - doi: 10.1086/730053
    type: journal
    authors: Fan, H., Liu, Y., Qian, N., & Wen, J.
    year: 2024
    title: "Technological adoption and taxation: The case of China's Golden Tax reform"
    venue: Tax Policy and the Economy
    vol: 38
    pages_or_artno: 101-122
new_dois: []
---

## CORE

【构念与来源】

hidden_adopt_kw_p25_allv 家族刻画银行在年度媒体报道中"隐性金融科技采纳"象限的占比: 一篇报道被计入该象限, 要求它在关键词层面对金融科技词汇的显性提及量偏低 (低于当年该轨道关键词计数分布的 25 分位), 但在语义层面与政策/战略基准锚点的余弦相似度偏高 (不低于当年该锚点分布的 25 分位)。直觉是, 银行有两种披露金融科技动作的方式: 一种是大量堆叠"金融科技""开放银行""区块链"一类关键词的显性宣传式报道 (对应家族 token_adopt_* 象限), 另一种是措辞含蓄、关键词密度不高、却在语义结构上高度贴合监管政策话语的报道 — 后者更接近银行在真正落地业务转型但对外披露克制、或媒体转述时经过筛选加工的情形, 是构念上更接近"实质性但低调"的采纳信号, 因此命名为 hidden (隐性) 而非字面意义的隐瞒。四象限体系源自 pipeline/panel/runner.py::_classify_policy_quadrants, 与 token_adopt (高频低相似, 表面提及但语义偏离政策焦点)、subst_adopt (高频高相似, 实质性采纳) 共同构成三分类矩阵的补集之一 (第四格 "低频低相似" 未单独命名列, 隐含为"未测量到显著关联")。

数据来源两支: 关键词计数轨 fintech_distinct_keywords 来自 stage 15 (fintech_intensity) 对文章正文的 Aho-Corasick 金融科技词典去重命中数 (kw 轨, 与 int 轨的强度加权分数 fintech_intensity_score 并列, 但本家族固定取 kw 轨, 家族基名含 "_kw_" 段); 语义相似度轨 policy_cosine_sim_allv 同样产自 stage 15, 是文章嵌入与政策/战略锚点文本嵌入的余弦相似度, 但取"全语料静态锚点" (all-vintage anchor, 后缀 _allv) 版本 — 即锚点向量由全样本期固定构造, 不随年度重新估计, 与不带 _allv 后缀的"vintage 主轨"锚点 (逐年或滚动重估的锚点) 构成一组稳健性孪生。两支输入在合并入四象限分类前, 先经 _filter_to_verified_universe 与 stage 24 (herd_decay) 输出的 LLM 语义精筛集做 (docid, target_bank) 半连接对齐, 把 stage 15 规则预筛阶段混入的约 26.8% 假阳性文章剔出分母, 确保四象限占比与面板其余情感/文本测度共享同一 verified 聚合域, 不会因分母口径不一致而制造 phantom bank-year。

【方法学与计算】

分类判据在年度截面内动态生成: 对每个日历年, 分别对 fintech_distinct_keywords 与 policy_cosine_sim_allv 取该年样本的 25 分位数作为该年阈值 (df.groupby('year')[col].transform quantile), 而非全样本期固定阈值, 用意是控制媒体报道整体语调/关键词密度随年份漂移 (例如金融科技相关报道量逐年上升) 对跨年可比性的污染 — 每年都用当年自己的分布定义"相对高/低"。分类本身只对 fintech_distinct_keywords 与 policy_cosine_sim_allv 同时非缺测的文章生效 (measured 掩码), 任一侧缺测的文章分类结果记为 NaN 而非静默归零或归入某一象限; 这是 2026-06-11 的一次修复 (fix omni-g-runner-03/g-runner-11) 针对的问题: 旧实现把 `NaN >= threshold` 当作 False 处理, 会让 stage 15 早退路径 (例如某年因异常导致 policy_cosine_sim 整列 NaN) 输出的"零测量"文章被系统性误判为低相似度, 从而人为抬高 token_adopt 类象限、压低 hidden/subst 类象限的占比。bank-year 层面聚合时, groupby(target_bank, year).mean() 对 NaN 自动跳过, 分母是该 bank-year 内"关键词与相似度均可测"的文章数, 而非该 bank-year 全部报道数; 若整个 bank-year 均无可测文章, 面板输出为 NaN (而非填 0), 与本仓库 F3 红线 (无测量样本 → NaN, 不得注入伪零污染 TWFE 回归) 保持一致。

家族基名中的 "p25" 指分类阈值取 25 分位而非 50 分位 (中位数) 或 75 分位 — 这是 quadrant_percentiles 配置梯子 {25, 50, 75} 中的一档, p25 使"高相似度"这一侧的判定门槛相对宽松 (top 75% 都算 high_sim), 而"低词频"一侧的判定门槛相对严格 (仅 bottom 25% 算非 high_freq), 因此 p25 档的 hidden 象限相对 p50/p75 档更容易被纳入, 三档互为稳健性梯子而非互相替代, 各自 just-identified 并排, 不应混入同一 over-identified Hansen J 设定作联合矩条件。"kw" 段标示词频侧固定使用关键词计数轨 (与强度分数轨 int 并列的另一档梯子, 二者亦互为稳健性)。"allv" 段标示相似度侧固定使用全语料静态锚点轨 (与逐年 vintage 主轨并列的稳健性孪生), 二者共用完全相同的 track(full/ctx/ss) × 词频(kw/int) × 分位(p25/p50/p75) 构造循环, 仅相似度阈值列的基名不同, 因此 vintage 主轨与 allv 全年份锚点轨之间也应作为互为稳健性、不分主次的一组并排结果解读, 不应把二者的矩条件混入同一联合估计。

本家族的三个成员列 (无后缀、_ctx、_ss) 对应文本三轨口径: full 轨扫描标题+全文正文, ctx 轨扫描标题+实体窗口截取文本, ss 轨扫描标题+银行与金融科技同句共现窗口文本; 三轨在 stage 14 (materialize_ctx) 各自物化独立文本列, 相似度与词频两支输入均按轨分别计算, 三轨结果各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。留篇门控 (是否计入"一篇银行金科报道") 采用 full-only 口径 (2026-06-29 起): 一篇文章能否进入本家族的分母, 取决于其 full 轨 LLM 语义验证结果 llm_verified_full, ctx/ss 轨降级为 full 留篇集合之上的条件测度/稳健性轨, 不独立扩张或收缩样本行宇宙。ctx/ss 轨的词频侧优先复用同轨变体列 (如 fintech_distinct_keywords_ctx), 若该变体不存在 (词频为 track-agnostic 元数据) 则回退复用 full 轨词频列并在日志中披露, 此回退不改变相似度侧仍按各自轨道独立计算的事实。

【文献定位】

四象限"词频-语义相似度"交叉设计的方法学动机可追溯到银行数字化/金融科技采纳的实证测量文献: Kwan, Lin, Pursiainen & Tai (2024, JFQA) 在压力测试银行数字能力时同样面对"披露文本量"与"实质能力"可能脱钩的识别难题, 提示单纯依赖关键词出现频率会系统性混淆宣传式披露与真实转型进度, 这正是本家族区分 token(高频低相似)与 hidden(低频高相似)两象限的经验依据。Fan, Liu, Qian & Wen (2024, Tax Policy and the Economy) 在研究技术采纳与税收征管数字化改革时, 同样强调采纳行为存在"显性合规披露"与"隐性技术使用"两条不完全重合的观测路径, 支持把"低显性提及但高语义关联"单列为独立构念而非简单归入采纳缺失。percentile 梯子 (p25/p50/p75) 与 kw/int、vintage/allv 两组稳健性孪生的并排设计, 呼应了多重研究者自由度对结论稳健性的一般性关切: Huntington-Klein 等 (2021, Economic Inquiry) 与 Breznau 等 (2022, PNAS) 均以多分析者复现实验证明, 看似次要的建模选择 (如阈值分位点、锚点估计窗口) 可系统性改变实证结论的方向与显著性, 因此本仓库对每一类此类选择均物化为并排的稳健性变体而非仅报告单一口径, 供下游回归在附录稳健性表中逐档核验方向与量级的一致性, 而非把某一档默认为"正确"设定。

## VAR: hidden_adopt_kw_p25_allv

【变体差分】

本列是家族在 full 文本轨上的成员, 词频侧使用关键词计数轨 (fintech_distinct_keywords, 无轨道后缀, 即在标题+全文正文范围内统计的金融科技词典去重命中数), 相似度侧使用全语料静态锚点轨 (policy_cosine_sim_allv, 无轨道后缀), 分类阈值取年度 25 分位。full 轨文本 = 标题 prepend 到全文正文 (14_materialize_ctx 物化的 content_full), 不做实体窗口截取或同句共现过滤, 是三轨中信息覆盖面最宽、上下文最完整的一支, 也是留篇门控 (llm_verified_full) 直接作用的轨道 — 本列所在的 bank-year 分母天然对齐 full 轨语义精筛后的 verified 文章集, 无需经由 ctx/ss 的条件测度回退逻辑。

在稳健性梯子坐标系里, 本列同时占据三个维度的一个具体格点: 文本轨=full (与 _ctx/_ss 并排)、词频轨=kw (与同家族外部的 int 轨并排, int 轨衍生的是 hidden_adopt_int_p25 系列而非本家族)、锚点轨=allv 全语料静态锚点 (与不带 _allv 的 vintage 主轨 hidden_adopt_kw_p25 并排)、分位阈值=p25 (与 p50/p75 并排)。四个维度两两正交, 互不交叉编码, 任一维度切换都会产生同家族之外或同家族内的另一并排列, 而不是本列的子集或超集。all-vintage 静态锚点相对 vintage 主轨的实质差别在于: 主轨的政策/战略锚点向量按年度 (或滚动窗口) 重新估计, 更贴合当期政策话语的措辞变化, 但也更容易受当年样本量或异常年份的估计噪声影响; allv 轨的锚点向量固定为全样本期一次性估计, 牺牲了对政策话语年度漂移的敏感性, 换取跨年更稳定、不受单年异常值扰动的锚点基准。二者互为稳健性检验对方结论是否对锚点估计窗口的选择敏感, 不存在何者"更对"的先验判断, 使用时应在附录稳健性表中并列汇报而非只取其一入正文主表。若正文主表选用 vintage 主轨 (无 _allv 后缀) 作为 canonical 口径, 本列 (_allv) 即承担对应的稳健性验证角色。

在报道量偏少或某年整体金融科技话题热度骤降的样本期 (例如本地开发环境 T=2 的极小样本窗口), 年度 25 分位阈值本身的估计方差会显著放大, 可能导致同一批文章在不同锚点轨/词频轨组合下被分类到不同象限, 这是 percentile 阈值梯子设计本身预期要暴露的现象, 而非实现缺陷; 生产语料 (T=18, 全量约 1700 万条) 下年度样本量充分, 阈值估计噪声应显著收窄。使用本列作为回归自变量或机制检验分组变量时, 应留意其分母是该 bank-year 内 fintech_distinct_keywords 与 policy_cosine_sim_allv 双侧均可测的 full 轨文章数, 若某 bank-year 无可测文章, 值为 NaN 而非 0, 不应做零填充处理。

## VAR: hidden_adopt_kw_p25_allv_ctx

【变体差分】

本列与 canonical 列 (hidden_adopt_kw_p25_allv) 共享完全相同的词频轨 (kw)、锚点轨 (allv 全语料静态锚点) 与分位阈值 (p25), 唯一差分维度是文本轨切换为 ctx: 扫描范围从标题+全文正文收窄为标题+目标银行实体窗口截取文本 (14_materialize_ctx 物化的 content_ctx), 即只保留目标银行实体前后一定窗口内的句子, 而非整篇正文。词频侧优先复用同轨变体 fintech_distinct_keywords_ctx (若该变体因词频本身是 track-agnostic 元数据而不存在, 则按约定回退复用 full 轨词频列, 由日志披露该回退发生与否); 相似度侧则严格按 ctx 轨独立计算 policy_cosine_sim_allv_ctx, 不发生回退。

ctx 轨在留篇门控上是 full 轨留篇集合之上的条件测度: 一篇文章能否进入本列所属 bank-year 的分母, 仍由其 full 轨 llm_verified_full 判定结果决定, ctx 轨本身不独立扩张或收缩行宇宙, 只在 full 轨已确认"是一篇银行金科报道"的文章子集上, 换一种更聚焦实体的文本窗口重新计算词频与相似度。这意味着本列与 canonical 列共享完全相同的样本行宇宙 (before 聚合), 差别只在于逐篇的词频计数值与相似度取值可能因窗口收窄而变化 — 关键词密度可能因窗口收窄而上升 (聚焦银行相关句子, 稀释无关正文段落), 相似度取值也会因语义窗口不同而与 full 轨存在差异, 两者的相对高低排序 (决定年度 25 分位归类) 未必与 full 轨一致, 因此本列与 canonical 列在同一 bank-year 上的取值可能出现分歧, 这是三轨设计有意保留的信息, 而非需要调和消除的噪声。

本列若无同句共现 (即该 bank-year 内所有文章都不存在银行实体窗口可提取的情形) 属于 ctx 轨本身的回退语义范畴 (镜像 ss 轨的回退规则), 但由于 ctx 轨定义为"实体窗口"而非"同句共现", 其回退触发条件与 ss 轨不同, 不应把二者的回退语义混淆处理。在稳健性解读上, 本列与 canonical (full) 列、_ss 列三者应作为互为稳健性、不分主次的一组并排结果共同呈现, 三者各自 just-identified, 严禁混入同一 over-identified Hansen J 设定联合估计, 也不应仅以三者数值相关系数高低来判定谁是"更好"的主轨。使用时若发现某 bank-year 在 full 轨与 ctx 轨之间的隐性采纳判定出现方向性分歧, 应结合该 bank-year 原始报道的实体窗口截取质量做定性核查, 而非默认信任其中一轨。

## VAR: hidden_adopt_kw_p25_allv_ss

【变体差分】

本列与 canonical 列共享相同的词频轨 (kw)、锚点轨 (allv) 与分位阈值 (p25), 文本轨切换为 ss (同句共现轨): 扫描范围收窄为标题+目标银行与金融科技词汇同句共现窗口内的文本 (config/filtering.yaml::context_window.ss_sentence_radius 控制窗口半径, 默认 ±1 句), 是三轨中语义聚焦程度最高、样本文本量通常最少的一支。词频侧优先复用 fintech_distinct_keywords_ss (若不存在则按约定回退复用 full 轨词频列); 相似度侧独立计算 policy_cosine_sim_allv_ss。

ss 轨回退语义镜像 ctx 轨设计原则但适用条件不同: 当某篇文章不存在银行与金融科技词汇的同句共现时 (即无法从原文中截出一个"银行与金科同时出现"的句子窗口), content_ss 回退为该文章的全文 body, 并以 ss_is_fallback=True 标记该行, 与 ctx 轨 (基于实体窗口而非同句共现) 的回退触发条件是两个不同的判据。回退发生时该文章在本列的词频/相似度计算实质上退化为 full 轨口径的语义近似 (只是仍复用 ss 轨自身若存在的独立列), 分母 (n_articles) 与非回退情形共享同一套统计口径, 不因回退而单独剔除或标记为缺测。留篇门控同样是 full-only: 本列所属 bank-year 的分母行宇宙由 full 轨 llm_verified_full 决定, ss 轨本身不独立扩张或收缩样本, 只在 full 轨已确认的报道子集上重新以更严格的同句共现窗口计算词频与相似度。

由于同句共现窗口通常比实体窗口 (ctx) 更窄, 本列在词频侧的绝对计数值通常低于 ctx 轨与 full 轨, 相似度侧的语义聚焦程度也更高, 因此本列的年度 25 分位阈值估计相对更容易受回退比例 (fallback 篇数占比) 影响 — 若某 bank-year 内绝大多数文章都触发 ss_is_fallback 回退, 该 bank-year 在本列上的取值实质上退化为对 full 轨的近似复刻, 与 ctx 轨、full 轨的区分度会明显下降, 使用时应结合 ss_is_fallback 比例辅助判断本列在特定 bank-year 是否提供了增量信息。三轨 (full/ctx/ss) 与两条锚点轨 (vintage/allv)、三档分位阈值 (p25/p50/p75)、两条词频轨 (kw/int) 共四个维度的组合构成本仓库该象限指标族的完整梯子, 本列占据 (ss, kw, allv, p25) 这一格点, 应与其余格点互为稳健性、不分主次地并排呈现, 严禁混入同一 over-identified Hansen J 联合估计。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., Chen, N., Grieco, P., Ekpe, G., Pugatch, T., Saavedra, M., & Stopnitzky, Y. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Fan, H., Liu, Y., Qian, N., & Wen, J. (2024). Technological adoption and taxation: The case of China's Golden Tax reform. Tax Policy and the Economy, 38, 101-122. https://doi.org/10.1086/730053
<!-- rendered-citations:end -->
