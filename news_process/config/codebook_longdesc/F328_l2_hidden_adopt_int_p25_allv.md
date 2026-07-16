---
family_id: F328
columns:
- hidden_adopt_int_p25_allv
- hidden_adopt_int_p25_allv_ctx
- hidden_adopt_int_p25_allv_ss
unit: bank-year 占比 (0–1 区间的比例; 分母=该银行该年"政策相似度×金科强度双双可测"的文章篇数, 分子=落入"隐性采纳"格的篇数)
formula: 逐篇先经 stage 15 得 (policy_cosine_sim_allv{_ctx,_ss}, fintech_intensity_score{_ctx,_ss}) 二元组; 年度组内以第 25 百分位数为界把 policy_cosine_sim_allv 二值化 high_sim=(sim>=P25) 与 fintech_intensity_score 二值化 high_freq=(freq>=P25); hidden_adopt = 1{~high_freq & high_sim}, 逐篇取 .astype(float).where(measured) 后按 (target_bank, year) groupby mean 得占比; sim/freq 任一 NaN 的行不计入分子分母 (measured=sim.notna() & freq.notna())
producer: pipeline\panel\runner.py::_classify_policy_quadrants (核心分类原语) + pipeline\panel\runner.py 步骤7h 四象限循环 (L2037-2090, anchor_variants='_allv' 分支) ; 面板列标签见 pipeline\panel\export.py (Track B int × P25 象限族注释段 L1404-1413); 上游相似度来源 pipeline\filtering\policy_alignment.py (`_allv` 全年份静态锚点分支)
upstream:
- 15_article_policy_alignment (policy_cosine_sim_allv / policy_cosine_sim_allv_ctx / policy_cosine_sim_allv_ss; Qwen 主嵌入轨, 全语料静态锚点)
- 15_fintech_intensity (fintech_intensity_score / _ctx / _ss; Track B "int" 连续词频强度)
- 24_herd_decay_processor (LLM-verified 留篇域, 经 runner._filter_to_verified_universe semi-join 收敛聚合域)
citations:
- doi: "10.1002/smj.821"
  type: journal
  authors: "Adner, R., & Kapoor, R."
  year: 2010
  title: "Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations"
  venue: "Strategic Management Journal"
  vol: "31"
  issue: "3"
  pages_or_artno: "306-333"
- doi: "10.1073/pnas.2203150119"
  type: journal
  authors: "Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al."
  year: 2022
  title: "Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "119"
  issue: "44"
  pages_or_artno: "e2203150119"
- doi: "10.1007/s11573-017-0852-x"
  type: journal
  authors: "Gomber, P., Koch, J.-A., & Siering, M."
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: "Journal of Business Economics"
  vol: "87"
  issue: "5"
  pages_or_artno: "537-580"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行—金科关系的"隐性采纳" (hidden adoption) 强度: 一篇报道若在语义上与官方金科政策文本高度贴合 (policy_cosine_sim 高), 却在表层词频上并不密集提及金科关键词 (fintech_intensity_score 低), 即被判为该银行"做得多、说得少"的信号——采纳行为已发生但未被表层关键词密度充分表征。这是 export.py 注释所称"象限离散分类 (机制检验/稳健性用)"四宫格之一, 另三格为 token_adopt (词频高但语义对齐低, 表层蹭热词)、subst_adopt (词频语义双高, 实质性采纳) 与隐含的第四格 (双低, 未纳入面板, 视为对照组基线)。该四象限设计承袭 Hassan et al. (2019) 在企业电话会议文本中用"锚点相似度"识别政策关注度的思路, 并把它与词频密度交叉, 以区分"真做" (substantive) 与"表演式" (token) 或"低调" (hidden) 两种非对称的采纳姿态——这一构念区分呼应创新生态系统文献中互补性资产与技术依赖对企业绩效路径的非对称影响 (Adner & Kapoor, 2010, *Strategic Management Journal*): 采纳的"深度"信号 (语义对齐) 与"广度"信号 (词频强度) 在测量上并不同构, 二者解耦恰是本族存在的理由。
【方法学与计算】
_p25 表示阈值取自年度组内 (`groupby('year')`) sim 与 freq 各自的第 25 百分位数 `quantile(0.25)`; 与家族同源的 _p50/_p75 变体 (F328 外的相邻家族) 构成阈值梯子, 三者各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。阈值越低 (P25), "高" (high_sim/high_freq) 的门槛越低, 落入 hidden/subst/token 格的篇数越多, 面板占比整体上移; 这是分类边界的敏感性维度, 而非测量误差。分类采用 NaN 掩码而非零填充: `measured = sim.notna() & freq.notna()`, 只有 sim 与 freq 同时可测的行才参与 `high_freq`/`high_sim` 布尔比较与后续 `.where(measured)`, 未测量行 (如 stage 15 优雅早退产出的全 NaN 相似度) 保持 NaN 并被 `groupby.mean()` 自动跳过——分母是"已测量篇数"而非"全部候选篇数", 避免测量失败被误判为"低对齐/低词频"从而制造伪造的高 token_adopt/hidden_adopt 占比 (对应源码 fix(omni-g-runner-03/g-runner-11, 2026-06-11) 的显式修复)。聚合发生在 `_filter_to_verified_universe` semi-join 之后的 verified 域上 (与 stage 24 LLM 语义精筛后的留篇集对齐, 而非 stage 15 规则预筛的候选集), 消除约 26.8% 假阳性文章对 bank-year 均值/分位阈值/象限分母的污染。
`_allv` 后缀标记本族所用的 policy_cosine_sim 并非 stage 15 主轨的"vintage"锚点 (逐年动态更新、只用截至当年已发布的政策文本构造锚点), 而是"全年份静态锚点" (all-vintage): 用所有年份(含未来年份) 的政策文本一次性拼成锚点池, 计算余弦相似度。`_allv` 完全复用与 vintage 主轨相同的下游构造方法 (同嵌入模型、同池化、同余弦度量、同四象限分类函数), 唯一差异是锚点的时间覆盖范围。这一设计的用意是: 若某银行的报道语义与"金科政策的历史+未来全貌"高度吻合, 但与"截至当年已知"的政策文本吻合度较低, 说明该银行的战略布局具有前瞻性 (提前对齐尚未发布的政策方向), 或者 vintage 主轨的锚点因政策文本累积不足而存在噪声。`_allv` 因此是 vintage 主轨的稳健性对照, 而非替代测度; vintage 关闭或政策文本样本过少时, `_allv` 数值上会退化为等同主轨 (诚实退化, 而非静默零), 调用方可据此识别。口径铁律: `_allv` 含未来政策文本, 属于 ex-post/全语料稳健性对照, 论文中绝不可替换 vintage 主轨作为主回归设定, 必须在数据口径说明中明确披露其 ex-post 性质。
三轨 (full/无后缀=full 全文本, `_ctx`=银行实体窗口, `_ss`=银行∧金科同句±N窗) 由 runner.py 步骤7h 循环中的 `_sim_tracks`/`_freq_eff` 分支机械派生: sim 优先取该轨对应的 `policy_cosine_sim_allv{_ctx,_ss}` 列, 词频侧优先取 `fintech_intensity_score{_ctx,_ss}` 同轨变体, 轨道缺列 (旧 schema / `_ss` 未上线) 时优雅跳过, 绝不借用其他轨道数据补位。三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定; `_ss` 缺失银行∧金科同句共现时, 上游 stage 14 已把 `content_ss` 回退为全文 body 并置 `ss_is_fallback=True`, 本族聚合时该行仍照常参与四象限分类 (回退语义镜像 `_ctx`, 与 CLAUDE.md「三轨文本架构」口径一致)。留篇门控口径遵循 2026-06-29 起的 full-only 铁律: 一篇文章是否被计为"该银行—金科报道"仅由 `llm_verified_full==True` 决定, ctx/ss 轨的行宇宙是 full 轨留篇集的条件子集, 各轨占比据此各自计算, 不改变谁进入 verified 域。
【文献定位】
四象限构造直接承袭 Hassan et al. (2019) 用文本相似度锚点度量企业对政策关注/暴露的范式思路 (export.py 注释明确标注), 本族把它推广为"语义对齐×表层词频"二维交叉, 用以刻画企业创新/技术采纳中"言行是否一致"的非对称模式, 呼应 Adner & Kapoor (2010, *Strategic Management Journal*) 关于技术互补性与依赖关系如何在多维度上非线性影响企业绩效的论证——采纳的语义深度与词频广度并非同一构念的两种测量, 而是两个可以独立变动的维度, 交叉分类正是为了识别这种解耦而非简单加总。测度所依赖的金科采纳"实质 vs. 表演" (substantive vs. token) 区分与 Gomber, Koch & Siering (2017, *Journal of Business Economics*) 对金融科技研究方向的分类框架 (locus 维度) 同源, 二者共同支撑了银行—金科关系强度不能仅凭关键词密度单一维度判断的方法论主张。阈值梯子 (P25/P50/P75) 与锚点变体 (vintage/`_allv`) 并列构成规格空间, 这一"多路径并排呈现而非单选最优"的稳健性叙事逻辑与 Breznau et al. (2022, *Proceedings of the National Academy of Sciences*) 关于同一数据、同一假设下不同分析者会得出高度分散结果的多分析者研究 (many-analysts) 发现一致: 分类阈值与锚点口径的选择空间客观存在不确定性, 本族选择以并排稳健性梯子呈现而非隐藏单一"最优"切点, 正是对这种方法论不确定性的显式回应。

## VAR: hidden_adopt_int_p25_allv

【变体差分】
本列是家族的 full 轨 canonical 列: sim 取 `policy_cosine_sim_allv` (全文本 full 轨、`_allv` 全年份静态锚点), freq 取 `fintech_intensity_score` (Track B "int"=连续词频强度测度, 区别于同族相邻家族 Track A "kw"=AC 自动机去重关键词计数), 阈值取年度组内第 25 百分位数。列名结构为 `{track_name}_adopt_{freq_track}_p{pct}{anchor_sfx}{track_sfx}` 的具体实例 `hidden_adopt_int_p25_allv` (full 轨在 track_sfx 位置为空字符串, `_allv` 紧跟在百分位后)。数值上, 该列表示某银行某年"语义高度贴近全年份政策语料、但词频强度低于年度中位数以下第 25 百分位"的报道占该银行当年全部可测(sim 与 freq 双双非 NaN)报道篇数的比例。由于所用锚点是 `_allv` 全年份静态口径 (含未来政策文本), 本列在解释上须谨慎: 高占比可能反映银行前瞻性布局, 也可能仅是锚点包含更丰富未来政策文本后语义空间更稠密所致的机械效应, 论文引用时须与 vintage 主轨 (无 `_allv` 后缀的同名家族) 并列报告, 明确本列为 ex-post 稳健性对照而非主设定; 二者互为稳健性并排, 禁止混入同一 over-identified Hansen J。分母口径上, 本列与同族 `token_adopt_int_p25_allv`/`subst_adopt_int_p25_allv` 共享同一 (银行, 年) 分组下已测量篇数, 三者之和 (加上未纳入面板的"双低"隐含格) 不必然等于 1, 因为三者各自独立按 `.where(measured)` 掩码求均值, 分母口径一致但分子互斥, 读者可用三者之和检验测量完整性 (若三者之和显著小于 1, 说明存在双低格未计入面板的篇数)。P25 阈值意味着分类边界相对宽松 (只要求 sim/freq 超过组内后 25%), 因而 hidden_adopt 占比在 P25 口径下通常高于 P50/P75 口径, 三档阈值差异反映的是分类严格度的规格选择而非测量误差, 解读回归系数时应始终注明所用百分位。

## VAR: hidden_adopt_int_p25_allv_ctx

【变体差分】
与 canonical 列的唯一差异在扫描文本轨: sim 取 `policy_cosine_sim_allv_ctx` (银行实体窗口 ctx 轨嵌入的政策余弦相似度, 同样使用 `_allv` 全年份静态锚点), freq 优先取同轨变体 `fintech_intensity_score_ctx` (若该列存在; 若金科词频测度在 ctx 轨无独立变体则退化为复用 full 轨列并在日志中披露, 但当前 stage 15 已产出 ctx 轨强度列, 通常不触发退化)。阈值仍为年度组内第 25 百分位数, 分类分母仍是该轨 sim 与 freq 双双可测的篇数, 与 full 轨分母彼此独立、不共享。ctx 轨捕捉"围绕目标银行实体附近窗口"的局部语境, 相较 full 轨(含全文无关段落) 更聚焦于银行主体本身的政策话语, 但也因窗口截断可能丢失全文层面的政策语义线索。本列与 canonical (无轨道后缀) 及 `_ss` 变体三者各自 just-identified 并排、互为稳健性、不分主次, 留篇门控口径仍以 full 轨 `llm_verified_full==True` 为准, 本列行宇宙是该留篇集的条件子集。ctx 轨在实体窗口截断的代价是可能丢失文章开头/结尾处与银行主体无直接文本邻接、但语义上仍与政策相关的段落 (如宏观背景铺垫、行业展望结语), 因而 ctx 轨 sim 值相对 full 轨可能整体上移或下移, 具体方向取决于个案窗口截取质量, 不构成系统性偏误结论, 须以 full 轨 canonical 结果为主、以 ctx 轨结果作交叉验证。若某银行某年 ctx 轨可测篇数明显少于 full 轨 (因窗口截取失败或实体识别缺失导致 ctx 文本退化), 该银行—年份的 ctx 轨占比样本量应在稳健性表脚注中披露, 避免小样本波动被误读为经济显著的采纳模式变化。

## VAR: hidden_adopt_int_p25_allv_ss

【变体差分】
与 canonical 列的唯一差异在扫描文本轨: sim 取 `policy_cosine_sim_allv_ss` (银行∧金科关键词同句±N窗 ss 轨嵌入的政策余弦相似度, `_allv` 全年份静态锚点), freq 优先取同轨变体 `fintech_intensity_score_ss`。ss 轨在缺乏银行与金科关键词同句共现的文章上, 上游 stage 14 物化阶段已将 `content_ss` 回退为全文 body 并置 `ss_is_fallback=True` (回退语义镜像 `_ctx`, 而非镜像 full——两者独立回退互不借用), 该行仍会参与本族 sim/freq 双测原语判定, 不因回退而被排除出分母, 但读者在解释该轨占比时应了解部分观测的"ss"实际是全文本口径。ss 轨相较 ctx 轨窗口更窄 (仅同句±N句), 理论上信噪比更高但样本覆盖率更低 (更多文章因无同句共现触发回退)。本列在盘上 T=2 开发数据上因样本量有限, ss 轨可能出现零方差或大比例缺测的退化表现, 属于开发期预期现象, 生产 T=19 全量语料上预期覆盖改善。三轨 (full/ctx/ss) 与阈值梯子 (P25/P50/P75)、锚点变体 (vintage/`_allv`) 共同构成本家族的规格稳健性空间, 各维度正交、互不交叉, 禁止在同一 over-identified 设定中混用。ss 轨的经济学意图是最大限度剔除与银行—金科关系无关的"噪声段落" (例如同一篇报道中与其他银行、其他业务无关的段落), 仅保留银行实体与金科关键词紧邻出现的句子窗口, 理论上能提供信噪比最高的语义相似度信号, 但代价是覆盖面最窄、对个别文章的句子切分与实体识别误差最敏感。三轨并列呈现的目的正是让读者能够在"覆盖面广但可能夹杂噪声" (full) 与"覆盖面窄但信号纯净" (ss) 之间权衡, 而非要求研究者在三者中裁定唯一"正确"轨道。

<!-- rendered-citations:begin -->
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
<!-- rendered-citations:end -->
