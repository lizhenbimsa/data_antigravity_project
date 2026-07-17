---
family_id: F555
columns:
- token_adopt_int_p75
- token_adopt_int_p75_ctx
- token_adopt_int_p75_ss
unit: 银行-年内"象征性采纳"文章占比 (0-1 之间的比率, 分母=当年可测量[sim/freq 双双非缺失]篇数)
formula: 逐篇二值指示 token_i = 1{fintech_intensity_score_i >= Q75_year(fintech_intensity_score)} AND 1{policy_cosine_sim_i < Q75_year(policy_cosine_sim)}, 银行-年 token_adopt_int_p75 = mean(token_i | measured_i), measured_i = sim_i notna & freq_i notna
producer: pipeline\panel\runner.py (_classify_policy_quadrants + 四象限占比聚合循环, L312-L2090; STATA_LABELS 标签见 pipeline\panel\export.py L1407)
upstream:
- pipeline\filtering\policy_alignment.py (stage 16 article_sim/policy_cosine_sim 逐篇产出)
- pipeline\filtering\fintech_intensity.py (stage 15 fintech_intensity_score TF-IDF x SIF 加权强度)
- pipeline\panel\runner.py::_classify_policy_quadrants
citations:
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: 'Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations'
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306-333
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital finance and FinTech: Current research and future research directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: 10.1006/jfin.2000.0282
  type: journal
  authors: Boot, A. W. A.
  year: 2000
  title: 'Relationship banking: What do we know?'
  venue: Journal of Financial Intermediation
  vol: '9'
  issue: '1'
  pages_or_artno: 7-25
- doi: "10.1007/s10799-026-00501-9"
  type: "journal"
  authors: "Pan, Y., Xue, F., & Liu, L."
  year: 2026
  title: "Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing"
  venue: "Information Technology and Management"
- doi: "10.2139/ssrn.6922688"
  type: "wp"
  authors: "Xu, F."
  year: 2026
  title: "Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks"
  venue: "SSRN"
  pages_or_artno: "6922688"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画"银行金融科技报道的言行一致性"这一构念在文章层面的一种离散化机制检验测度: 把每篇被判定为"目标银行与金融科技相关"的报道, 按其"词频强度"(该文章金融科技术语的密集程度)与"政策相似度"(该文章内容与官方金融科技政策文本在语义空间中的接近程度)两个维度, 联合切分成一个 2x2 四象限, 再在银行-年层面把落入"高词频/低相似度"象限的文章占比汇总为 token_adopt_int_p75。四象限的另外三格分别对应 subst_adopt(高词频且高相似度, 言行一致/实质性采纳)、hidden_adopt(低词频且高相似度, 低调布局/隐性采纳)与被舍弃未单列的 irrelevant(低词频且低相似度)。token 象限的经济学含义是"说得多、做得像"的偏离: 报道文本大量堆砌金融科技术语, 但报道内容与官方政策文本的语义相似度却处于当年样本的中下段, 直觉对应管理学与公司披露文献里反复讨论的"象征性采纳"(symbolic adoption)或俗称"洗科技"(fintech-washing)现象 — 企业/银行在传播层面大量使用热词以迎合市场叙事, 但披露内容与真实政策/战略方向的耦合度不足。该构念承接 Adner & Kapoor (2010) 关于创新生态系统中"技术互依性"如何影响企业价值创造路径的理论框架, 并与 Gomber, Koch & Siering (2017) 对金融科技研究中"数字化转型话语与实质业务重构"二分的综述性观察相呼应: 二者都强调"提及新技术的频率"本身并不等价于"技术采纳的深度", 必须辅以内容层面的语义对齐来判别真伪采纳。
【方法学与计算】
本测度的计算分两层。第一层是逐篇文章层面的连续测度产出: 词频强度侧走 Track B("int"轨, 与并列的 Track A "kw"轨——AC 自动机去重关键词计数——互为稳健性并排, 非本家族覆盖范围), 取自 stage 15 产出的 fintech_intensity_score, 该分数是金融科技词典命中词的 TF-IDF 权重与 SIF (Smooth Inverse Frequency) 平滑逆频率加权的组合强度, 用以压低高频泛用词、放大低频专指词的贡献; 相似度侧取自 stage 16 产出的 policy_cosine_sim, 是文章嵌入向量与官方金融科技政策文本嵌入向量之间的余弦相似度。第二层是年度分位数阈值切分与银行-年聚合: 对每一年样本内的 fintech_intensity_score 与 policy_cosine_sim 分别独立计算 P75 分位数 (year-specific quantile, 而非全样本统一阈值, 用以吸收跨年整体热度/相似度水平漂移), 逐篇比较得到 high_freq/high_sim 两个布尔指示, token 象限定义为 high_freq & ~high_sim, 再按 (target_bank, year) 分组取均值汇总为占比。P75 是 P25/P50/P75 三档分位数梯子 (config `article_alignment.quadrant_percentiles`) 中最严格的一档: 只有词频排进当年前 25% 高位、同时相似度排在后 75% (即未进入前 25% 高相似度) 的文章才计入 token, 因此相对 P50 (机制检验基准, 中位数分割) 与 P25 (最宽松档) 而言, P75 档给出的是"高热度阈值下的象征性采纳"这一更严苛定义, 三档之间是同一构念在不同切分严格度下的稳健性并排, 互不隶属, 禁止把三档混入同一 over-identified 的 Hansen J 检验。该测度对缺失值采取"未测量即不计入分母"的显式掩码: 仅当 sim 与 freq 双双非缺失时才参与逐篇分类, 全年无可测量文章的银行-年输出面板 NaN 而非伪零 (避免虚假零值污染双向固定效应估计的系数)。这一 NaN 掩码修复 (omni-g-runner-03/g-runner-11) 专门纠正了旧实现把 stage 15 优雅早退产生的全 NaN policy_cosine_sim parquet 误判为"低相似度"从而把全部高词频文章错误归入 token 象限的系统性偏误。
【文献定位】
四象限框架的经济学根基来自创新采纳与技术互依性文献: Adner & Kapoor (2010, *Strategic Management Journal*) 论证了创新生态系统内部技术互依结构如何决定企业价值创造的实际路径, 本测度借用其"结构性互依 vs. 表面提及"的区分逻辑, 把"词频"对应表层信号, 把"政策语义相似度"对应结构性/实质性信号。Gomber, Koch & Siering (2017, *Journal of Business Economics*) 对金融科技研究脉络的系统综述指出, 银行披露与媒体报道中大量出现的"数字化""金融科技"等热词往往先于真实业务转型出现, 这正是 token 象限试图捕捉的"言行时滞/脱耦"现象, 也是本项目 P4 (Gomber 式) locus 维度论文族的方法学邻居。银行与金融科技关系的关系型银行业文献 (Boot 2000, *Journal of Financial Intermediation*) 进一步提示, 银行对外沟通中的战略叙事与其真实关系资本投入之间存在结构性张力, 为把"话语热度"与"政策内容对齐度"分离测量提供了理论正当性: 若银行仅在传播层面追逐金融科技叙事而未在业务政策方向上真正对齐监管导向, 其沟通策略更接近关系维系/合规姿态展示而非实质战略转型, 与本测度定义的 token 象限所刻画的机制一致。 这一「言/行二分」的操作化在近期文献中已有直接的前沿对应。Pan、Xue 与 Liu (2026) 把技术采纳明确二分为「符号性采纳 (symbolic adoption)」与「实质性行动 (substantive action)」, 并把两者的背离操作化为 AI washing 加以实证测量, 印证了本族把同一构念拆成词频强度维与政策对齐维、再以二者错位界定 token 象限的做法在当前文献中确有同构先例; 其迁移边界是对象为一般企业的 AI 叙事而非银行, 符号/实质二分依托组织冗余与披露数据, 不使用政策文本余弦相似度, 亦不做年度分位阈值切分, 层级为企业而非银行-年。词频侧 Track B 的连续强度打分亦有同域应用先例: Xu (2026) 以文本方法构造银行层面的 FinTech intensity 指标并检验其与经营绩效的关系, 与本族所用的 fintech_intensity_score 属同一测度族; 但其样本为欧洲银行、文本取自银行自身披露/年报而非第三方中文新闻, intensity 作为连续指标直接进入回归, 既不做年度分位二值化, 也未与政策相似度交叉形成 2×2 象限, 且系未经同行评审的 SSRN 工作论文, 结论稳健性尚待检验, 此处仅作测度族的存在性旁证。
## VAR: token_adopt_int_p75

【变体差分】
本列是家族 canonical (无轨道后缀) 版本, 词频与相似度双侧均取自"full"轨: 词频用 stage 15 fintech_intensity_score 的 full 轨 (标题+正文全文扫描), 相似度用 stage 16 policy_cosine_sim 的 full 轨 (同样标题+正文全文嵌入)。full/ctx/ss 三轨在本项目是"各自 just-identified 并排、互为稳健性、不分主次"的口径 (CLAUDE.md 当前状态铁律), 本列构成三轨梯子的基准锚, 覆盖域是 stage 21 情感 LLM full-only 门控 (2026-06-29) 之后仍保留的 llm_verified_full == True 留篇集合 (四象限聚合发生在 stage 15/16 产出上, 并经 _filter_to_verified_universe semi-join 与 stage 24 herd_decay 验证域对齐, 旧 schema 下若键不齐则退化为 pre-verification 全集并有日志告警)。三轨 P75 阈值均按各自轨道文本重新计算年度分位数 (非跨轨共用阈值), 因此本列与下方两个轨道变体在数值上不可直接相减做差分解读, 只能作为独立稳健性证据并列报告; 禁止把三轨混入同一 over-identified Hansen J 检验。当银行-年内 full 轨可测量篇数为零时输出 NaN, 不填零, 该 NaN 与"该银行该年确实无金融科技相关报道"这一真实缺失语义对齐, 不因分母为零而人为置零污染面板均值 (呼应 F3 红线关于率类指标缺失处理的项目惯例)。full 轨作为三轨中信息最完整、覆盖篇数最多的一支, 通常在生产 T=19 全量语料上具有最少的 NaN 银行-年, 是论文正文首选报告轨; ctx/ss 两轨则作为对文本抽取范围的稳健性检验并列呈现, 三者不构成主次关系, 也不应被简单平均或加总为单一综合测度。

## VAR: token_adopt_int_p75_ctx

【变体差分】
本列是三轨梯子中的"ctx"(实体窗口) 变体: 相似度取 policy_cosine_sim_ctx (标题+实体窗口文本嵌入与政策文本的余弦相似度), 词频侧优先取同轨变体 fintech_intensity_score_ctx (若该列存在于 stage 15 产出中); 若 int 轨词频本身不产生 ctx 独立变体 (旧 schema 下可能退化为 track-agnostic 元数据), 则按代码逻辑回退复用 full 轨词频列并在日志中披露该复用, 此时相似度侧仍严格使用 ctx 轨。ctx 轨与 ss 轨镜像同一构造范式: 均是"实体窗口/同句共现"式的局部文本, 相对 full 轨的整篇扫描而言, ctx 轨把文章-政策语义相似度的计算聚焦在银行与金融科技实体附近的上下文窗口, 用以检验"言行一致性"这一构念是否对文本抽取范围敏感 — 如果一篇报道只在文章开头顺带提一句"金融科技", 而实体附近的上下文却与官方政策文本语义脱耦, full 轨的整篇相似度可能被文章其余部分的无关内容拉高或拉低, ctx 轨则更聚焦地反映"银行与金融科技实体真正共同出现的那一小段文本"是否贴合政策方向。P75 分位阈值同样按 ctx 轨自身年度分布独立计算, 不借用 full 轨阈值, 也不与 full 轨的词频/相似度做联合排序。ctx 轨与 full/ss 轨互为稳健性并排, 覆盖域同样限定在 stage 21 full-only 留篇门控确定的行宇宙子集上 (ctx/ss 降级为 conditional-on-full 的测度轨, 而非独立的留篇判定标准, 即 ctx 轨不会引入 full 轨未覆盖的额外文章)。若 stage 16 policy_cosine_sim_ctx 全列缺失 (旧 schema), 该列在四象限聚合循环中被跳过, 面板对应列整体为 NaN, 而非以 full 轨结果顶替。

## VAR: token_adopt_int_p75_ss

【变体差分】
本列是三轨梯子中的"ss"(银行与金融科技同句共现) 变体: 相似度取 policy_cosine_sim_ss, 词频侧同样优先取同轨变体 fintech_intensity_score_ss, 缺失时回退复用 full 轨词频并披露。ss 轨的文本构造语义镜像 ctx 轨 (CLAUDE.md 三轨口径): 要求目标银行与金融科技词汇出现在同一句子窗口 (config/filtering.yaml::context_window.ss_sentence_radius, 默认正负1句) 内才计入该轨的"真实同句"文本; 若某篇文章不存在银行与金融科技同句共现, 则该篇的 ss 轨内容回退为全文 body (与 ctx 轨同源的 is_fallback 标记指示), 属于优雅降级而非缺失, 此时该篇在 ss 轨上的词频/相似度数值实质上退化为与 full 轨等价的全文测度, 只是仍标注在 ss 轨列下供审计追溯。ss 轨相对 ctx 轨的判定口径更严格: ctx 只要求实体落入一个较宽的窗口即可, ss 则要求银行实体与金融科技词汇严格同句共现才算"真实"命中, 因此 ss 轨的回退比例通常高于 ctx 轨, 是三轨中样本覆盖最窄、判据最苛刻的一支, 用以检验"言行一致性"结论是否只在最严格的共现口径下依然稳健。ss 轨在词频与相似度两侧均要求先经过 stage 14 ctx_materializer 的 content_ss 物化, 再喂给 stage 15/16 产出各自的 ss 轨列; 与 full/ctx 轨完全独立地计算年度 P75 阈值并聚合占比, 不共享阈值也不共享分母。ss 轨与 full/ctx 轨三者共同构成"各自 just-identified 并排、互为稳健性"的梯子, 分析时应作为并列稳健性证据分别报告系数, 禁止在同一 over-identified Hansen J 检验框架下把三轨方程混合识别。若某银行-年在 ss 轨上可测量篇数为零 (无同句共现且无回退全文可用的极端情形, 或 stage 16 未产出 ss 轨列), 该银行-年该列输出面板 NaN, 与 full/ctx 轨的对应 NaN 并非同一缺失原因, 解读时须区分"该银行该年无报道"与"该银行该年有报道但无同句共现"两种不同的测量不可得情形。

<!-- rendered-citations:begin -->
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Boot, A. W. A. (2000). Relationship banking: What do we know?. Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Pan, Y., Xue, F., & Liu, L. (2026). Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing. Information Technology and Management. https://doi.org/10.1007/s10799-026-00501-9
Xu, F. (2026). Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks. SSRN No. 6922688 [Working Paper]. https://doi.org/10.2139/ssrn.6922688
<!-- rendered-citations:end -->
