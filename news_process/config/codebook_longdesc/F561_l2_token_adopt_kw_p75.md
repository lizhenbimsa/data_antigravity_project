---
family_id: F561
columns:
- token_adopt_kw_p75
- token_adopt_kw_p75_ctx
- token_adopt_kw_p75_ss
unit: 比例 (银行-年内落入"Token"象限的文章占比, ∈[0,1], 未测量记 NaN)
formula: 'token_adopt_kw_p75 = mean_i( 1{freq_i(kw) >= Q75_year(freq(kw))} AND 1{sim_i < Q75_year(sim)} ), 仅对 sim 与 freq 双双非缺失的文章 i 计分; 逐年 (year) 分组求 P75 分位阈值, 与文章级布尔指示 (源列 pipeline/panel/runner.py::_classify_policy_quadrants 产出的 _is_token_kw_p75* 指示列) 按 (target_bank, year) groupby mean 聚合'
producer: pipeline\panel\runner.py
upstream:
- 15_fintech_intensity (fintech_distinct_keywords, AC 去重关键词数, Track A/kw 轨词频)
- 16_article_policy_alignment (policy_cosine_sim, Hassan, Hollander, van Lent & Tahoun 2019 QJE 风格政策余弦相似度)
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
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.1086/226550
  type: journal
  authors: Meyer, J. W., & Rowan, B.
  year: 1977
  title: "Institutionalized Organizations: Formal Structure as Myth and Ceremony"
  venue: American Journal of Sociology
  vol: '83'
  issue: '2'
  pages_or_artno: 340-363
- doi: "10.1016/j.pacfin.2024.102493"
  type: "journal"
  authors: "Liu, Y., Wang, J., Wen, F., & Wu, C."
  year: 2024
  title: "Corporate responses to systemic risk: Talk and action"
  venue: "Pacific-Basin Finance Journal"
  vol: "87"
  pages_or_artno: "102493"
new_dois:
- 10.1086/226550
---

## CORE

【构念与来源】
本家族 (token_adopt_kw_p75 三列) 度量银行-年层面"象征性金科采纳" (token/symbolic adoption) 在词频轨 (Track A, kw) 下、以年度 P75 分位数为分割阈值的文章占比。构念根植于组织理论对"象征性合规/采纳"与"实质性采纳"的经典区分 (Meyer & Rowan 1977, *American Journal of Sociology*, 提出"制度化组织"框架, 论证正式结构可作为仪式性神话而与实际运作脱钩, 是本家族"言而不行"构念的理论源头; Westphal & Zajac 1998 治理层面的象征性 vs 实质性执行进一步细化了这一区分) 在金融科技话语情境下的操作化: 一篇报道若在词面上大量堆砌金科关键词、却与官方政策文本在语义上相似度不高, 即被判为"言而不行"的洗科技 (token adoption) 信号; 反之词频不高但政策语义相似度高则记为"闷声干大事"的隐性采纳 (hidden adoption, 另一家族); 二者皆高记为言行一致的实质性采纳 (substantive adoption)。该四象限设计直接呼应 pipeline/panel/runner.py 内注释所述"象限离散分类 (机制检验/稳健性)"用途, 与连续型政策对齐测度 (article_sim_mean 等) 互补, 后者供主回归的线性识别, 本家族三列供机制检验与稳健性分组用的离散化替代设定。
【方法学与计算】
计算分两层。文章层: Track A 词频侧取 stage 15 (fintech_intensity) 产出的 fintech_distinct_keywords (Aho-Corasick 原始去重关键词命中数, 与政治词权重、TF-IDF/SIF 加权的 fintech_intensity_score 即 Track B/int 轨严格区分, 二者互为并排稳健性梯子, 详见 F5xx 系列 int 轨家族); 语义侧取 stage 16 (article_policy_alignment) 产出的 policy_cosine_sim (银行报道文本嵌入与官方金融科技政策文本嵌入之间的余弦相似度, 方法学上移植自 Hassan, Hollander, van Lent & Tahoun (2019, *Quarterly Journal of Economics*) 以文本-语料余弦相似度测度企业层面政治风险暴露的构造思路)。两列先按 year 分组各自求 P75 分位阈值 (`groupby('year').transform(quantile)`), 分位阈值逐年独立估计而非全样本混合, 目的是吸收年度语料规模/写作风格的时变漂移; 随后逐篇比较词频/相似度是否达到当年阈值, 得到布尔象限指示。仅 sim 与 freq 同时非缺失的文章参与分类 (`_classify_policy_quadrants` 的 measured 掩码), 任一测度缺失 (如 stage 15/16 优雅早退产生的全 NaN 中间产物) 的文章指示置 NaN 而非静默计零, 避免在测量失败的年份把高词频文章错误分入 Token 象限、污染分母。银行-年层: 对文章级布尔指示按 (target_bank, year) 分组取均值, pandas `.mean()` 对 NaN 逐元素跳过, 故聚合结果的分母是"该银行该年已成功测量 sim 与 freq 两个量的文章数", 而非该银行该年全部报道数; 若某银行某年全部文章均未测量, 聚合输出为 NaN (不回填 0), 遵循项目 v6/F3 修复确立的"无测量数据 ≠ 零事件"契约 (强行 fillna(0.0) 会把结构性缺失伪装成"零采纳", 系统性压低固定效应回归中的处理组均值, 参见 Allison 2001 关于面板缺失值处理的告诫)。
【文献定位】
方法学谱系上, 本家族同时借用三条文献线: 一是文本-政策语义对齐的余弦相似度构造, 直接沿用 Hassan, Hollander, van Lent & Tahoun (2019, *Quarterly Journal of Economics*) 以词嵌入余弦相似度测度企业文本与外部风险语料贴合程度的方法脉络, 及后续金融文本分析对"言语-行动"分离度量的操作化传统; 二是关键词词频侧的稀疏/加权双轨设计参考了公司文本披露研究中对"提及次数"与"语义强度"分离建模的做法, 与银行数字化转型实证研究 (如 Kwan, Lin, Pursiainen & Tai 2024, *Journal of Financial and Quantitative Analysis*, 关于银行数字能力压力测试的证据) 所强调的"披露话语 vs 实际能力"缺口构念高度一致 —— 该文发现银行在压力情境下的数字化陈述与其真实数字韧性存在可观测缺口, 为本家族"象征性/实质性"二分提供了外部效度参照; 三是组织理论对正式结构与实际运作脱钩的经典论证 (Meyer & Rowan 1977, *American Journal of Sociology*), 为"词频高但语义贴合低"这一操作化判据提供理论层面的合法性基础, 而非仅是数据驱动的临时分割。P75 分位阈值本身是稳健性检验设计: 项目主线以 P50 作机制检验基准 (中位数分割与项目内多处既有惯例一致), P25/P75 为对称的稳健性梯子, 三者按 pipeline/panel/runner.py 内 `_percentiles = [25, 50, 75]` 循环并排生成, 互不嵌套、互为并排稳健性 (镜像项目内政治词权重、词典消融等梯子设计惯例)。 在同代实证测度上, Liu、Wang、Wen 与 Wu (2024) 把企业对系统性风险的回应拆为 talk (文本表述强度) 与 action (实际举措) 两条可分别测量的维度并检验二者关系, 与本家族用「词频高低 × 政策对齐高低」切分 token 象限属同一「言—行两维并置」的测度族, 为该二分的可操作性提供了近期参照。迁移边界须诚实标明: 原文对象是企业层面对系统性风险的回应而非银行金融科技采纳; 更关键的是, 其 talk 取自披露文本、action 取自财务/公司行为代理, 即「行」一侧有文本之外的独立验证, 而本家族两维均来自新闻文本 (词频 vs 政策余弦), 并无外部行为对照。故该文只锚定「两维并置」这一构造思路, 不得被援引为「本家族低政策相似度即等同于实际行动缺位」的证据; 原文亦不含年度分位阈值梯子与 bank-year 篇均占比聚合。
【识别策略定位】
该四象限离散化不进入主识别方程本身 (主回归使用连续型 article_sim_mean / fintech_intensity_mean), 而是作为异质性/机制检验的分组变量或稳健性替代 DV 使用: 例如检验"高词频低相似度"银行-年子样本内处理效应是否显著弱于"高词频高相似度"子样本, 从而排除"报道声量驱动结果而非真实政策响应"的替代解释。
【与相邻测度的构念区分】
本家族与同源的 hidden_adopt_kw_p75 (隐性采纳, F337 家族)、subst_adopt_kw_p75 (实质性采纳, F522 家族) 共享同一文章级布尔分类矩阵, 三者互斥且穷尽 (加上未计入任何列的 Irrelevant 象限, 四象限之和逐篇恰为 1); 与 Track B (int 轨, F561 姊妹家族 token_adopt_int_p75 系列) 的区别仅在词频侧输入列 (fintech_distinct_keywords 原始计数 vs fintech_intensity_score TF-IDF×SIF 加权分数), 语义侧 policy_cosine_sim 及分类逻辑完全一致, 两条词频轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。

## VAR: token_adopt_kw_p75

【变体差分】
本列是家族 canonical (无三轨后缀) 列, 对应全文轨 (full-text): 语义侧使用 stage 16 全文情境下的 policy_cosine_sim (标题+正文全文本嵌入与政策文本的余弦相似度), 词频侧使用 track-agnostic 的 fintech_distinct_keywords (该列在 AC 关键词计数层面本身即为跨轨元数据, 无 ctx/ss 独立变体, 三轨版本共同复用同一份 full 轨词频输入, 这一点在 pipeline/panel/runner.py 注释中被显式标注为"track-agnostic")。分位阈值 P75 (year 内) 与四象限判据 (词频高 AND 相似度低 → Token) 均按家族 canonical 定义, 是三条轨道中样本覆盖最完整的一支 —— 依据本项目 2026-06-29 确立的留篇门控铁律, 全文轨 (full) 是唯一驱动"是否判定为一篇银行金科报道"的门控轨, ctx/ss 两轨的行宇宙是 full 留篇集合的条件子集 (conditional-on-full), 因此本列在三者中拥有最大的非缺失银行-年格数, 是后续机制检验/稳健性分析的默认基准列。计算链路上游依赖两个独立阶段: stage 15 (fintech_intensity) 提供词频侧输入, stage 16 (article_policy_alignment) 提供语义侧输入; 二者任一在某篇文章上产出缺失 (含优雅早退产生的结构性全 NaN), 该篇即被排除出分类分母, 不会被误计入象限占比的计算基础。在使用场景上, 研究者若要对比"高声量低政策贴合"银行与"高声量高政策贴合"银行的实体后果差异 (如融资成本、监管评级变化), 本列即是划分前一子样本的默认起点; 由于其分母口径最宽, 也最适合作跨年度、跨银行池化统计描述 (如年度趋势图) 的基准序列, 而 ctx/ss 两列则用于在更窄的文本邻近性假设下复核该趋势是否稳健。

## VAR: token_adopt_kw_p75_ctx

【变体差分】
本列是 ctx (实体窗口) 轨的 P75 孪生: 语义侧改用 policy_cosine_sim_ctx (标题+目标银行/金科实体窗口文本的政策余弦相似度, 而非全文), 词频侧优先取同轨变体 fintech_distinct_keywords_ctx (若该同轨列存在于 stage 15 输出中); 若同轨词频列不存在 (即该指标在 ctx 语境下未产出独立版本), 则退回复用 full 轨 fintech_distinct_keywords, 并在计算日志中披露这一复用决定, 这与 kw 轨词频本属 track-agnostic 元数据的既有事实一致 —— 无论词频侧是否有真正独立的 ctx 版本, 语义侧的 policy_cosine_sim_ctx 始终是独立测量, 因此本列与 canonical 列的差异主体落在"用什么文本窗口算相似度"而非词频统计口径。按项目三轨铁律, ctx 与 full/ss 各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J; 又因留篇门控为 full-only, 本列所依赖的行宇宙是 full 轨留篇集合的条件子集, 用于验证"象征性采纳"结论是否对文本窗口选择 (全文 vs 实体局部窗口) 稳健, 而非提供额外识别力。分位阈值同样按 year 分组、以 ctx 轨语义相似度序列独立求 P75, 不与 full 轨阈值混用。使用建议上, 本列适合在关注"报道中围绕目标银行/金科实体的紧邻语境"是否言过其实时作为替代口径: 若某银行-年在 canonical (full) 列上呈现高 Token 占比, 但在 ctx 列上占比明显收敛, 提示该银行相关报道的整体篇幅中存在大量与政策语义无关的背景段落拉低了全文相似度, 而实体附近语境本身其实与政策贴合度更高, 二者对照有助于定位"象征性采纳"信号究竟来自全文写作风格还是实体叙事本身。

## VAR: token_adopt_kw_p75_ss

【变体差分】
本列是 ss (银行∧金科同句) 轨的 P75 孪生: 语义侧改用 policy_cosine_sim_ss (银行与金科关键词落在同一句±N窗口内时构造的文本嵌入与政策文本的余弦相似度), 词频侧同样优先取同轨变体 fintech_distinct_keywords_ss, 缺失时退回复用 full 轨。ss 轨回退语义严格镜像 ctx 轨: 当某篇文章不存在银行与金科词的同句共现时, 该文章的 content_ss 在上游 stage 14 物化阶段即已回退为全文 body (`ss_is_fallback=True`), 但这一回退发生在文本物化层, 不改变本家族在 policy_cosine_sim_ss 列缺失时的处理方式 —— 该篇文章的 ss 轨相似度若不可测 (为 NaN), 依旧被 `_classify_policy_quadrants` 的 measured 掩码排除出分类分母, 不因回退到全文而被强行视为"已测量"。按项目铁律, ss 与 full/ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 留篇门控仍为 full-only, 本列的银行-年格数样本量在三轨中通常最小 (同句共现是比实体窗口更严格的邻近性判据), 用于在最严格的文本邻近性设定下复核"象征性金科采纳"结论是否依旧成立, 是三轨稳健性梯子中判据最紧的一支。使用建议上, 若某银行-年的象征性采纳信号在 canonical (full) 与 ctx 两列均显著、但在本列上因样本量过小而无法稳定估计 (呈 NaN 或高方差), 不应将其解读为"结论不成立", 而应结合 ss 轨天然的稀疏性 (要求银行与金科关键词严格同句共现, 是三轨中最保守的邻近性判据) 一并披露样本覆盖情况; 反之若本列在有效样本内依然复现 full 轨的方向性结论, 则构成对"象征性采纳并非源自宽松语境窗口下的语义稀释"这一潜在质疑的有力反驳。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Meyer, J. W., & Rowan, B. (1977). Institutionalized Organizations: Formal Structure as Myth and Ceremony. American Journal of Sociology, 83(2), 340-363. https://doi.org/10.1086/226550
Liu, Y., Wang, J., Wen, F., & Wu, C. (2024). Corporate responses to systemic risk: Talk and action. Pacific-Basin Finance Journal, 87, 102493. https://doi.org/10.1016/j.pacfin.2024.102493
<!-- rendered-citations:end -->
