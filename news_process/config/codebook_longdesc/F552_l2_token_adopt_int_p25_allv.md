---
family_id: F552
columns:
- token_adopt_int_p25_allv
- token_adopt_int_p25_allv_ctx
- token_adopt_int_p25_allv_ss
unit: 篇均占比 (0-1 之间的年度-银行截面比率, 分子为落入"象限"的已测量文章数, 分母为该银行-年内 sim 与 freq 双双非缺失的报道篇数)
formula: 'token_adopt_int_p25_allv = mean_over_articles( 1{ policy_cosine_sim_allv <= P25(policy_cosine_sim_allv) } AND 1{ fintech_intensity_score > P25(fintech_intensity_score) } ), 仅对 sim 与 freq 同时非缺失的文章计入分子分母; 三轨变体将 policy_cosine_sim_allv / fintech_intensity_score 换成同轨 (_ctx/_ss) 列, 无同轨变体的元数据列退回 full'
producer: pipeline\panel\runner.py (四象限分类循环, 约 L1978-L2040+) ; pipeline\panel\export.py (面板列标签映射, L1404-L1413)
upstream:
- 15_fintech_intensity (fintech_intensity_score, article_sim_mean/std, policy_cosine_sim*)
- article_policy_alignment (policy_cosine_sim_allv 全语料静态锚点)
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
- doi: "10.1006/jfin.2000.0282"
  type: journal
  authors: "Boot, A. W. A."
  year: 2000
  title: "Relationship banking: What do we know?"
  venue: "Journal of Financial Intermediation"
  vol: "9"
  issue: "1"
  pages_or_artno: "7-25"
- doi: "10.1007/s11573-017-0852-x"
  type: journal
  authors: "Gomber, P., Koch, J.-A., & Siering, M."
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: "Journal of Business Economics"
  vol: "87"
  issue: "5"
  pages_or_artno: "537-580"
- doi: "10.1016/j.econmod.2023.106445"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, F., & Zhao, Y."
  year: 2023
  title: "Bank fintech, liquidity creation, and risk-taking: Evidence from China"
  venue: "Economic Modelling"
  vol: "127"
  pages_or_artno: "106445"
- doi: "10.1007/s10799-026-00501-9"
  type: "journal"
  authors: "Pan, Y., Xue, F., & Liu, L."
  year: 2026
  title: "Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing"
  venue: "Information Technology and Management"
- doi: "10.1016/j.ipm.2025.104383"
  type: "journal"
  authors: "Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F."
  year: 2026
  title: "Measuring policy diffusion intensity: A text-driven analysis of government documents"
  venue: "Information Processing & Management"
  vol: "63"
  issue: "2"
  pages_or_artno: "104383"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行-年报道样本中, 文章语言对监管/政策话语的"象限式"响应类型占比, 属 stage 15 (fintech_intensity / article_policy_alignment) 与面板聚合层 (pipeline/panel/runner.py 四象限分类循环) 联合产出的机制检验/稳健性测度, 而非主回归的连续型情感或对齐指标。构念动机来自组织理论中"言行解耦" (talk-action decoupling) 与创新生态位互补性文献: 一篇报道可以在语言上高度贴近官方政策话语 (用词/语义与监管文本高度相似), 却几乎不涉及具体金科技术细节 (低词频强度); 也可以反过来, 大量堆砌金科技术词汇却与政策语言疏离。家族把这两个维度 (政策语义相似度 sim、金科词频强度 freq) 各自按截面 25 百分位 (P25) 二分, 组成 2×2 象限, 并分别输出三类占比列: token_adopt (象征性采纳/"套话式响应": sim 低于阈值但 freq 高于阈值, 即语言并不贴近政策官方话语、却大量堆砌金科技术词汇——高词频强度但低政策语义对齐, 刻画的是"蹭热词而非真对齐监管口径"这一套话现象)、hidden_adopt (隐性采纳/"低调对齐": sim 高于阈值但 freq 低于阈值, 即语言高度贴近政策话语框架、却较少涉及具体金科技术细节的堆砌)、subst_adopt (实质性采纳: sim 与 freq 同时高于/低于阈值的"言行一致"组合, 与 token/hidden 互补覆盖象限空间)。本家族 F552 对应的是 token_adopt 分支, 即"低语义对齐、高词频强度"这一象限在银行-年内的占比, 刻画的是报道样本中"高频堆砌金科词汇但未真正贴合政策/监管话语"的比重, 可用作政策响应真实性/表面化程度的辅助诊断变量, 与家族核心测度 (article_sim_mean、fintech_intensity_mean 等连续型对齐/强度均值) 互为补充而非替代。

【方法学与计算】
计算分两层。第一层在文章级产生两个原始信号: policy_cosine_sim (或其 _allv 变体) 度量单篇报道与政策/监管文本库的余弦相似度, 由 stage 15 article_policy_alignment 环节产出; fintech_intensity_score 度量单篇报道内金科关键词的出现强度 (int 轨, 与另一"kw 轨"——去重关键词计数——并列的两套词频口径之一)。第二层在 pipeline/panel/runner.py 的象限分类循环中, 对每个银行-年子样本分别计算 sim 与 freq 各自的截面 25 百分位阈值 P25, 仅对 sim 与 freq 同时非缺失 (notna) 的文章参与分类与分母计数——这一 NaN 处理约定是 2026-06-11 (omni-g-runner-03/11) 的修复要点: 旧实现把测量失败 (stage 15 早退导致 policy_cosine_sim 全 NaN) 的文章误判为"低对齐"计入分子, 会把零测量误记为伪信号; 现改为未测量行的分类指示本身也是 NaN, 分组聚合 (groupby mean) 自动跳过, 分母收缩为"已测量篇数"而非全部报道篇数, 与"无数据=未测量"而非"无数据=零"的口径契约保持一致。家族名中的 "_allv" 后缀表示 sim 侧使用的是 "all-vintage" 全语料静态锚点 policy_cosine_sim_allv (而非随年份滚动更新的主轨 policy_cosine_sim), 即政策参照文本库固定不随文章所在年份变化, 用于剥离"锚点本身随时间漂移"对象限归类的干扰, 是与不带 _allv 后缀的同名家族 (若存在) 互为稳健性的锚点变体, 二者共用完全一致的 track (full/ctx/ss) × 词频口径 (kw/int) × 分位 (P25/P50/P75) 四象限构造逻辑, 唯 sim 阈值列的基名不同。"_int" 表示词频侧采用的是 fintech_intensity_score (强度型连续计数), 与采用 fintech_distinct_keywords (去重关键词个数) 的 "_kw" 轨并列, 二者互为稳健性口径, 不分主次, 禁止把 kw 轨与 int 轨的象限占比混入同一过度识别的 Hansen J 检验。"_p25" 表示分位阈值取 25 百分位, 与 p50/p75 构成阈值梯子, 同样各自 just-identified 并排, 互为稳健性而非嵌套子集。

【文献定位】
"象限式"言行区分测度的理论根基是组织行为对监管/制度环境采纳异质性的经典关切: Boot (2000, Journal of Financial Intermediation) 指出银企关系中信息不对称使得外部观察者难以仅凭披露语言判断银行实质经营取向, 这正是本家族用 sim×freq 双维度而非单一情感分数刻画"言"与"行"错位的动机所在。Adner and Kapoor (2010, Strategic Management Journal) 关于创新生态位技术互补结构如何影响企业绩效的框架, 支撑了将金科采纳拆分为"话语层面的政策对齐"与"内容层面的技术实质"两条独立轴线的建模选择——二者在生态位互补意义上并非同一构念的两种测量, 而是刻画采纳过程中不同环节 (话语合法性获取 vs. 技术能力积累) 的正交信号。Gomber, Koch and Siering (2017, Journal of Business Economics) 对数字金融/FinTech 研究方向的系统梳理, 界定了银行层面金科响应的多重维度 (产品、渠道、话语), 为本家族在 locus (响应位置) 维度上区分"说了什么"与"做了什么"提供了直接的构念依据。Fang, Wang, Wang and Zhao (2023, Economic Modelling) 关于中国银行金科、流动性创造与风险承担的实证研究, 印证了银行金科响应的异质性 (象征性响应 vs. 实质性投入) 在中国银行业样本中具有可观测的经济后果差异, 支持本家族作为机制检验/异质性分组变量的适用场景。三轨 (full/ctx/ss) 均遵循 CLAUDE.md 铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一过度识别的 Hansen J 检验; ss 轨在无银行-金科同句共现时的回退语义镜像 ctx 轨 (回退为全文 body, 并以 *_is_fallback 标记), n_articles 分母口径与 2026-06-29 起生效的 full-only 留篇门控一致, 即"是否算作一篇银行金科报道"仅由 llm_verified_full 决定, ctx/ss 轨的象限占比是该留篇集合内的条件测度而非独立样本。 就本族 token 象限所刻画的"高声量而低对齐"这一背离本身, Pan、Xue 与 Liu (2026) 把技术采纳明确二分为符号性采纳 (symbolic adoption) 与实质性行动 (substantive action), 并将两者的背离操作化为 AI washing 加以实证测量, 为本族"同一构念拆成两维并置、以背离格 (freq 高于年度 P25 而 sim 不高于年度 P25) 识别说多做少"的做法提供了近期存在性证明; 惟其对象为一般企业的 AI 叙事与实际行动, 符号/实质二分基于组织冗余与披露数据, 既不使用政策文本余弦相似度, 也不做年度分位阈值切分, 层级为企业而非银行-年且分母非已测量报道篇数, 故不可据以外推本族的阈值与分母口径。sim 维的方法学一侧, Chen、Wen、Deng、Chen 与 Ma (2026) 以政府文件文本构造政策扩散强度的文本驱动测度, 表明"用政策文本相似度/强度刻画政策对齐程度"这一测度族仍处近期前沿, 与本族 policy_cosine_sim_allv 同属一脉; 但该文所测为政策文件之间的扩散强度 (政府—政府层级), 本族则是新闻报道文本对政策锚点的余弦相似度 (媒体—政策层级), 且该文不做二值象限分类、不设年度分位阈值, 亦无全年份静态锚点与逐年滚动锚点的对照设计, 故仅提供方法族的存在性锚点, 不锚定本族的象限判据。
## VAR: token_adopt_int_p25_allv

【变体差分】
本列是家族的 full 轨 canonical 版本, 即分类所用的 sim (policy_cosine_sim_allv) 与 freq (fintech_intensity_score) 均取自"标题+正文"全文轨。含义为: 在某银行-年内, 全文轨已测量 (sim 与 freq 同时非缺失) 的报道中, 落入"sim 低于等于该银行-年截面 P25 阈值、且 freq 高于该银行-年截面 P25 阈值"这一象限的篇数占比——即政策语义对齐薄弱但金科技术词频堆砌密集的"套话式"报道占比。行样本口径遵循 full-only 留篇门控: 参与统计的文章集合以 llm_verified_full == True 为准, 与情感/对齐等其它 full 轨指标共享同一行宇宙, 便于跨测度族在同一样本上做交叉验证。作为家族三轨中的锚定轨, 本列同时也是 ctx/ss 两条条件稳健轨的对照基准, 三者在方法学上完全对等、互不隶属, 差异只体现在文本窗口与由此改变的 sim/freq 原始信号来源, 不改变象限划分算法本身 (仍是同一 P25 双维度分类循环、同一 NaN 掩码规则、同一 _allv 全语料静态政策锚点)。使用者若关心"银行报道是否存在系统性金科词汇堆砌而缺乏真实政策话语对齐"的现象, 应优先参照本 full 轨数值, 并将 ctx/ss 轨作为文本窗口收窄后的稳健性佐证, 三者数值方向一致则增强结论可信度, 不一致则需结合 *_is_fallback 标记与分母篇数排查是窗口效应还是测量噪声所致, 而非直接判定某一轨"更对"。

## VAR: token_adopt_int_p25_allv_ctx

【变体差分】
本列是 ctx (实体窗口) 轨变体: sim 若存在同轨列 policy_cosine_sim_allv_ctx 则优先使用该列 (对齐信号取自标题+目标银行/金科实体窗口文本而非全文), freq 侧同理优先取 fintech_intensity_score_ctx (若该同轨列存在于面板输入); 依据 runner.py 中"ctx/ss 轨词频优先取同轨变体, 缺失则视具体元数据性质决定是否退回 full"的规则, kw 轨的 AC 去重关键词计数因是 track-agnostic 元数据 (无 ctx 特有变体) 而复用 full 列, 但 int 轨的 fintech_intensity_score 本身是随文本窗口变化的强度型信号, 存在真实的 ctx 变体, 因此本列的词频输入不发生 track-agnostic 复用。行样本口径与 full 轨一致地继承 full-only 留篇门控 (llm_verified_full 决定的行宇宙), 即本列是"该银行-金科留篇报道集合"内, 用实体窗口文本重新计算 sim/freq 后的条件测度, 而非独立抽样。语义上, ctx 窗口聚焦于目标银行与金科实体附近的局部语境, 剥离了全文中与银行金科关系无关的背景段落干扰, 因此本列相对 full 轨对"该段落是否套话"给出更聚焦但样本量 (双双非缺失篇数) 可能更小的估计; 与 full 轨、ss 轨三者严格并排, 互为稳健性佐证, 不构成对 full 轨的替代或嵌套子集, 亦不得三者混入同一过度识别 Hansen J 检验框架。

## VAR: token_adopt_int_p25_allv_ss

【变体差分】
本列是 ss (银行∧金科同句) 轨变体: sim 若存在同轨列 policy_cosine_sim_allv_ss 则优先使用, freq 侧同理优先取 fintech_intensity_score_ss; 判定原语为"银行实体与金科关键词是否在同一句 (±N 窗口, 默认 N=1) 内共现", 与 ctx 轨的实体窗口口径是两个不同粒度的文本裁剪规则, 不可混淆。回退语义镜像 ctx 轨: 当某篇报道不存在银行∧金科同句共现时, 该篇的 content_ss 退回为全文 body, 对应 ss_is_fallback 标记为 True, 此时该篇纳入本列分母/分子的方式与其在 full 轨中的角色一致 (共享 n_articles 分母口径), 而非被剔除或另记; 若上游 fintech_intensity_score_ss 列本身缺失 (旧 schema 或 stage 14/15 未产出), 则本轨词频退回 full 列并在源码中以日志披露, 使用者若观察到本列数值与 full 轨高度雷同, 应先排查是否触发了该项优雅退回而非同句共现天然稀疏所致。同 ctx 轨一样, 本列的行样本口径继承 full-only 留篇门控, 且与 full、ctx 两轨在方法学上完全对等、各自 just-identified、互为稳健性、不分主次, 三轨数值一致方向增强"套话式响应"这一现象的可信度, 禁止三者合并进同一过度识别 Hansen J 检验。由于同句共现是三轨中裁剪最严格的窗口 (窄于 ctx 的实体窗口), 本列在真实同句参与分类的篇数往往少于 ctx 与 full 两轨, 分母 (sim 与 freq 双双非缺失且非 fallback 意义上真实测量) 更容易受样本量不足影响而波动, 使用者在解读本列象限占比时应结合 ss_is_fallback 比例与该银行-年报道总量, 避免把"共现太稀疏导致的估计噪声"误读为"套话现象本身发生了变化"; 这一注意事项与 ctx 轨的窗口收窄效应同源, 但因裁剪粒度更细而更为显著, 是三轨互为稳健性设计中预期存在、而非需要修正的差异来源。

<!-- rendered-citations:begin -->
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Boot, A. W. A. (2000). Relationship banking: What do we know? Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Pan, Y., Xue, F., & Liu, L. (2026). Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing. Information Technology and Management. https://doi.org/10.1007/s10799-026-00501-9
Chen, J., Wen, J., Deng, Y., Chen, M., & Ma, F. (2026). Measuring policy diffusion intensity: A text-driven analysis of government documents. Information Processing & Management, 63(2), 104383. https://doi.org/10.1016/j.ipm.2025.104383
<!-- rendered-citations:end -->
</content>
