---
family_id: F514
columns:
- subst_adopt_int_p50
- subst_adopt_int_p50_ctx
- subst_adopt_int_p50_ss
unit: 银行-年占比 (measured 篇数为分母的比例, 值域 [0,1], 无量纲)
formula: 'subst_adopt_{trk}_p50 = mean_i[ 1{freq_i>=Q50(freq|year)} & 1{sim_i>=Q50(sim|year)} | measured_i ], 其中 measured_i = notna(sim_i) & notna(freq_i); freq 取 Track B (int) = fintech_intensity_score, sim 取 policy_cosine_sim{_ctx/_ss}; 年度分位阈值经 groupby(year).transform(quantile) 逐年重估'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (聚合入 pipeline\panel\export.py 标签层)
upstream:
- 15_fintech_intensity (fintech_intensity_score, Track B/int 词频强度)
- 16_article_policy_alignment (policy_cosine_sim{_ctx,_ss}, 政策余弦相似度)
- 21_tone_llms (llm_verified_full 留篇门控, 经 semi-join 传导至对齐样本域)
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: 'Substance and Symbolism in CEOs'' Long-Term Incentive Plans'
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: 'The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling'
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: 'Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital finance and FinTech: Current research and future research directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: "10.1111/1467-8551.12879"
  title: "FinTech Adoption and Corporate Greenwashing: A Technology Affordance Perspective"
  authors: "Sun, Z., Liu, L., Johan, S., & Zhao, L."
  year: 2024
  venue: "British Journal of Management"
  type: "journal"
- doi: "10.1002/csr.70722"
  title: "Symbolic Versus Substantive ESG Practices: A Systematic Review and Integrative Framework"
  authors: "Ștefănescu, C. A., & Suciu, A. L."
  year: 2026
  venue: "Corporate Social Responsibility and Environmental Management"
  type: "journal"
new_dois:
  - "10.1111/1467-8551.12879"
  - "10.1002/csr.70722"
---

## CORE

【构念与来源】
subst_adopt_int_p50 家族刻画银行-年层面「实质性金融科技政策采纳」在全体报道中所占的比例, 其理论谱系直接源自组织制度理论中"实质与象征"(substance vs. symbolism) 的经典区分: Westphal & Zajac (1994, ASQ) 最早证明企业可以在采纳某项治理实践时仅完成表面宣示(象征性采纳)而不落实真正的行为改变(实质性采纳), 两者在文本/公告层面高度相似但经济后果迥异; Fiss & Zajac (2006, AMJ) 进一步把这一区分理论化为"框架化-解耦"(framing-decoupling)机制, 强调组织话语(讨论强度)与组织行为对齐度(与既定标准/政策的契合程度)是两条可分离的维度, 唯有二者同时"高"才构成真正的实质性采纳, 仅话语高而对齐低则是"廉价谈话"(cheap talk)式的象征性采纳。本项目把这一构念移植到银行-金融科技语境: 一篇报道若同时表现出(a)对金融科技的高强度关注(词频/强度维度)与(b)与官方金融科技政策文本的高语义对齐(政策余弦相似度维度), 才被记为"实质采纳"(subst_adopt); 若只有词频高而对齐低, 记为"象征采纳"(token_adopt, 對齊 Bingler et al. 2024, JBF 对"漂绿式"廉价气候披露的刻画逻辑——高声量、低落地一致性); 若只有对齐高而词频低, 记为"隐性采纳"(hidden_adopt, 低声量但语义高度贴合政策, 可能是低调但真实的采纳)。三分类构成一个完整的 2×2 象限(第四象限为"双低"未记为任一类, 指示列全部为 0), subst_adopt_int_p50 即该象限矩阵中"双高"格的银行-年占比。
【方法学与计算】
上游两条测度链路各自独立产出原始变量: 词频/强度维度取 stage 15 (`fintech_intensity`) 产出的 Track B/int 连续强度分 `fintech_intensity_score`(与 Track A/kw 的裸关键词计数并列、互为稳健性, 详见姊妹家族 F518-F523 subst_adopt_kw_* 系列); 对齐维度取 stage 16 (`article_policy_alignment`) 产出的 `policy_cosine_sim{_ctx,_ss}`(文章嵌入向量与政策锚点文本嵌入向量的余弦相似度)。判据函数 `_classify_policy_quadrants` (runner.py) 对每篇文章分别在 freq 维和 sim 维上, 按年度(而非全样本)分位数阈值(P50=年内中位数)做高/低二分, 再取逻辑与得到"双高"指示 `_is_subst_{track}_p50`; 年度而非全样本分位是为了吸收金融科技话语整体随时间增长的长期趋势, 避免早期年份文章被系统性判为"低词频", 与本项目其它梯子(如政治词权重、词典消融)一样属于按年重估的相对判据而非绝对阈值。分类前置一道 measured 掩码: 仅当 sim 与 freq 同时非缺失(notna)的文章才参与二分类, 否则该文章的三个指示列(token/hidden/subst)全部记为 NaN 而非静默计为 0——这是 2026-06-11 的一处修复(commit note "omni-g-runner-03/g-runner-11"): 旧实现对 `NaN >= threshold` 求值时 pandas 返回 False, 会把 stage 15 三条优雅早退路径写出的全 NaN `policy_cosine_sim` 静默误判为"低对齐", 从而让全部高词频文章系统性地误落入 token_adopt 象限, 制造由零测量伪造出的非缺失面板值。修复后, 逐篇指示列在 groupby(bank, year).mean() 聚合为占比时, pandas 的 mean 会自动跳过 NaN, 使占比分母严格等于"已测量篇数"而非"全部篇数", 与 CLAUDE.md 铁律"无数据=未测量(NaN)非零"的口径(Allison 2001 §3 缺失值处理原则)保持一致——若一年内一家银行的对齐分与强度分全部未测量, 面板输出为 NaN 而非 0, 避免虚假拉低固定效应回归系数。三个占比列(token_adopt/hidden_adopt/subst_adopt)加总恰等于"已测量篇数中双高或单高的篇数占比", 不含双低象限, 因此三者之和一般 <1 (双低象限文章计入分母但不计入任一分子)。
【文献定位】
本家族与 P3 (bank_fintech_substance, 参照 W&Z/Fiss-Zajac 政策解耦框架) 论文主线直接对应, 是该论文实质-象征区分的核心文本测度层。象征性高声量、低实质对齐的现象在企业可持续披露文献中有大量平行证据: Bingler et al. (2022, Finance Research Letters; 2024, Journal of Banking & Finance) 用 ClimateBERT 证明企业气候披露文本存在系统性"廉价谈话"(cherry-picking)成分, 即披露声量与真实排放/举措改善脱钩; 本家族的 token_adopt(F551 起的 int 轨系列)即是该逻辑在银行金融科技语境下的对应测度。Gomber, Koch & Siering (2017, Journal of Business Economics) 对数字金融/金融科技研究的主题图谱与研究方向做了系统梳理, 是本项目金融科技话语域(bank-fintech discourse)整体研究定位的背景文献之一, 为"金融科技"这一话语场的边界与子主题构成提供了外部学术参照; 需要说明的是, 该文在本项目其它家族(如 locus 维度测度)中被用作更直接的构念出处, 本家族对它的引用范围仅限于金融科技话语域的一般性背景定位, 并非声称本列词频词典本身直接取自该文的主题分类。Sun, Liu, Johan & Zhao (2024, British Journal of Management) 该文从技术可供性视角研究金融科技采纳如何压缩企业漂绿(象征性合规)的操作空间, 为本家族"实质采纳 vs 象征采纳"的二分测度提供了金融科技语境下的最新实证平行证据。Ștefănescu & Suciu (2026, Corporate Social Responsibility and Environmental Management) 该文系统综述并提出整合框架, 梳理"象征性 vs 实质性"ESG实践区分的理论谱系与测度方法, 直接呼应本家族源自 Westphal & Zajac (1994)/Fiss & Zajac (2006) 的实质-象征二分构念在近期文献中的延续与再理论化。年度相对分位阈值设计参照本项目一贯的"梯子/轨"方法论惯例——凡涉及阈值切分, 各分位点 (P25/P50/P75, 对应家族 F512/F514/F516) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。

## VAR: subst_adopt_int_p50

【变体差分】
本列是 subst_adopt_int_p50 家族的 full 轨主变量(canonical), 词频维度取 Track B/int 强度分 `fintech_intensity_score`(计算自全文 `content_full`), 对齐维度取无后缀的主轨 `policy_cosine_sim`(同样计算自全文语料, MAIN 嵌入引擎 Qwen/Qwen3-Embedding-8B); 阈值分位点为 P50(年度中位数), 与家族名 `_p50` 对应, 姊妹家族 F512(`_p25`)/F516(`_p75`)使用相同判据函数但取不同分位阈值——P50 在三个分位点中处于中间, 划分出的"高/低"两组样本规模最均衡, 是本梯子中判别力与样本平衡性折中的默认锚点, 常被用作论文正文报告的基线口径, P25/P75 作为更严格/更宽松的稳健性检验并排使用。本列继承 stage 21 情感 LLM 的 full-only 留篇门控口径(2026-06-29 起): 该门控只筛"是否计为一篇有效银行-金科报道", 与本列自身的 measured 掩码(sim/freq 是否双双非缺失)是两道独立的过滤, 后者进一步在门控通过的样本内部区分"是否成功测量出对齐分与强度分"。作为家族 canonical, 本列在全部下游模板(P3 主线 27_substance_anchor_robustness 等)中被优先引用为主回归自变量, ctx/ss 两个同族列作为稳健性并排存在, 不构成"次要"或"备用"关系。本列与姊妹词频轨家族(F518-F523, Track A/kw 裸关键词计数)在同一 P50 分位点上互为方法学稳健性: kw 轨用裸词频计数衡量话语强度, int 轨(本列)用连续强度分衡量话语强度, 二者对"高话语量"的算子定义不同但构念目标一致, 是词频测度层面的并排稳健性检验, 同样禁止混入同一 over-identified 检验。此外, 本列的分子(双高篇数)与同批次产出的 token_adopt(自 F551 `token_adopt_int_p25` 起的 int 轨系列)、hidden_adopt(自 F327 `hidden_adopt_int_p25` 起的 int 轨系列, 两个姊妹家族族群编号并不相邻, 系历史批次编号所致)两个姊妹列共享同一批 measured 篇数分母与同一年度分位阈值, 三列在读表时应联立解读为一个完整的采纳象限矩阵, 而非孤立看待单一比例。

## VAR: subst_adopt_int_p50_ctx

【变体差分】
本列与 canonical 列共享完全相同的判据函数 `_classify_policy_quadrants` 与 P50 分位阈值, 主差分维度是对齐相似度的文本来源轨道: sim 输入换为 `policy_cosine_sim_ctx`——由 stage 14 物化的 `content_ctx`(标题+目标银行实体窗口文本, 而非全文)计算出的政策对齐分。词频维度同样随 track 切换而非固定不变: `runner.py::_classify_policy_quadrants` 的装配逻辑对 ctx/ss 轨优先探测同轨变体列 `{freq_col}_ctx`/`{freq_col}_ss`, 命中即改用同轨词频列(本列实取 `fintech_intensity_score_ctx`, 由 stage 15 `fintech_intensity` 对 `content_ctx` 独立重算产出), 只有当某词频基名不存在同轨变体(即 track-agnostic 元数据列, 如 kw 轨的 AC 去重关键词数)时才回退复用 full 列——本列所属的 int 轨词频存在真实的 `_ctx` 同轨变体, 因此本列的 sim 与 freq 两个维度均切到了 ctx 轨, 并非仅 sim 一维差分。ctx 轨的设计意图是把"政策对齐"这一语义相似度测度收窄到与目标银行直接相关的实体窗口文本上, 排除全文中与该银行无关但恰好提到金融科技/政策的段落所引入的噪声, 是对 canonical 全文轨的构念收窄型稳健性检验而非替代: 若一篇长报道仅在与银行无关的段落大谈政策术语, canonical(full)轨会把该篇的对齐分记高, 而 ctx 轨会因实体窗口未覆盖该段落而记低, 二者的分歧本身即是诊断信息。按 CLAUDE.md 三轨铁律, full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁在同一个 over-identified Hansen J 检验中混用本列与 canonical/ss 列。ss 回退语义在本列不适用(本列不是 ss 轨), 但下游三轨门控口径(留篇=full-only)对本列同样生效: 只有 `llm_verified_full==True` 的文章才进入本列的 measured 判定候选集。

## VAR: subst_adopt_int_p50_ss

【变体差分】
本列的 sim 输入换为 `policy_cosine_sim_ss`——由 stage 14 物化的 `content_ss`(标题+目标银行∧金融科技同句共现窗口文本, 默认 ±1 句半径, 见 `config/filtering.yaml::context_window.ss_sentence_radius`)计算出的政策对齐分; 判据函数与 P50 分位阈值与 canonical/ctx 两列保持一致, 但词频维度输入不固定为 `fintech_intensity_score`——与 ctx 轨同理, `_classify_policy_quadrants` 装配阶段命中同轨变体列 `fintech_intensity_score_ss`(stage 15 对 `content_ss` 独立重算的强度分)即优先改用之, 故本列的 sim 与 freq 两个维度均切至 ss 轨, 与 canonical(full)/ctx 两列在词频口径上也存在真实差分, 而非仅对齐维度单一差分。ss 轨是三轨中最严格的实体窗口收窄: 只有银行实体与金融科技词汇在同一句(或邻近句窗口)共现时才纳入对齐计算的文本片段, 因此比 ctx 轨(实体窗口)对"政策话语是否真正落在银行与金融科技的交汇处"要求更高。回退语义镜像 ctx 轨: 当一篇文章不存在银行∧金融科技同句共现时, `content_ss` 按约定回退为全文 body(等同 full 轨文本), 并置位 `ss_is_fallback=True`, 该回退共享 `n_articles` 分母, 使得回退发生率可被审计而不会静默扭曲占比列的分母口径。与前两列相同, 本列的三个内部指示列(token/hidden/subst_adopt_int_p50_ss)加总 <1(双低象限不计入任一分子), measured 掩码(sim_ss 与 freq 同时非缺失)独立于 full-only 留篇门控, 二者共同决定本列的有效样本域。三轨(full/ctx/ss)在本列语境下的铁律同样适用: 各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 检验; 与姊妹家族 F512/F516 (P25/P75) 及 kw 词频轨 F518-F523 一起, 构成本项目"实质-象征采纳"测度谱系里判据/词频来源/文本轨道三条正交梯子的完整矩阵。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Sun, Z., Liu, L., Johan, S., & Zhao, L. (2024). FinTech Adoption and Corporate Greenwashing: A Technology Affordance Perspective. British Journal of Management. https://doi.org/10.1111/1467-8551.12879
Ștefănescu, C. A., & Suciu, A. L. (2026). Symbolic Versus Substantive ESG Practices: A Systematic Review and Integrative Framework. Corporate Social Responsibility and Environmental Management. https://doi.org/10.1002/csr.70722
<!-- rendered-citations:end -->
