---
family_id: F512
columns:
- subst_adopt_int_p25
- subst_adopt_int_p25_ctx
- subst_adopt_int_p25_ss
unit: bank-year 层面连续占比 [0,1] (文章级二值指示 groupby(['target_bank','year']).mean() 聚合结果, 非逐行 0/1 标量)
formula: '文章级: I(policy_cosine_sim_{trk} >= P25_year(policy_cosine_sim_{trk})) AND I(fintech_intensity_score_{trk} >= P25_year(fintech_intensity_score_{trk})), 阈值按 groupby(year) 逐年分位数估计 (非样本内整体分位); bank-year 层面: subst_adopt_int_p25{trk} = mean(该二值指示, over articles in (target_bank, year))'
producer: pipeline\panel\runner.py
upstream:
- pipeline/filtering/policy_alignment.py
- pipeline/filtering/fintech_intensity.py
- pipeline/panel/export.py
citations:
- doi: '10.1111/jofi.13412'
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
- doi: '10.5465/amj.2006.23478255'
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: 'The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling'
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: '10.2307/2393295'
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: '10.1016/j.jfi.2024.101101'
  type: journal
  authors: Kutzbach, M. J., & Pogach, J.
  year: 2024
  title: 'Financial Technology and Relationship Lending: Complements or Substitutes?'
  venue: Journal of Financial Intermediation
  vol: '59'
  pages_or_artno: '101101'
- doi: '10.1016/j.frl.2022.102776'
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: 'Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: "10.1007/s10799-026-00501-9"
  type: "journal"
  authors: "Pan, Y., Xue, F., & Liu, L."
  year: 2026
  title: "Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing"
  venue: "Information Technology and Management"
- doi: "10.1177/01708406241295505"
  type: "journal"
  authors: "Kaufmann, L., Krlev, G., & Brown, M. (."
  year: 2025
  title: "In Plain Sight: Mechanisms of means–ends decoupling in impact investing"
  venue: "Organization Studies"
  vol: "46"
  issue: "5"
  pages_or_artno: "667-692"
- doi: "10.2139/ssrn.6922688"
  type: "wp"
  authors: "Xu, F."
  year: 2026
  title: "Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks"
  venue: "SSRN"
  pages_or_artno: "6922688"
- doi: "10.1016/j.rmal.2025.100272"
  type: "journal"
  authors: "Hemelstrand, S., & Inoue, T."
  year: 2025
  title: "Stop splitting hairs: The problems with dichotomizing continuous data in language research"
  venue: "Research Methods in Applied Linguistics"
  vol: "4"
  issue: "3"
  pages_or_artno: "100272"
new_dois: []
---

## CORE

【构念与来源】
subst_adopt_int_p25 家族属于文章级政策对齐 (Article-level Policy Alignment, stage 15/16) 派生的象限离散分类体系, 用于捕捉银行金科报道究竟是「实质采纳」(substantive adoption) 还是「符号采纳」(symbolic adoption / cheap talk)。该体系的理论根基是组织理论中的实质-符号管理区分传统: Westphal & Zajac (1994) 首次系统区分企业采纳某项治理实践时「言」与「行」的分离, 即企业可能只是象征性地宣告采纳某实践 (symbolic adoption) 而并未在实质运营中落实; Fiss & Zajac (2006) 进一步把这一区分扩展到战略变革的框架化 (framing) 与解耦 (decoupling) 情境, 指出组织可通过对外话语的策略性建构来管理利益相关者对变革实质性的感知。本家族把该逻辑映射到银行金科报道语境: 一篇报道若同时表现出「高政策对齐」(该行的金科话语与监管/政策导向高度贴合) 与「高金科强度」(该行的金科具体举措/技术细节丰富), 才被判定为「实质采纳」; 若只在话语层面对齐政策但缺乏实质强度支撑, 则更接近「符号采纳」或「隐性采纳」范畴 (对应同一象限体系内的 token_adopt/hidden_adopt 系列, 与本家族并列但非本家族成员)。这一分类逻辑也呼应了金融文本分析中「廉价谈话」(cheap talk) 的识别传统: Bingler et al. (2022) 在气候信息披露语境下发现企业climate-related话语常与实际风险敞口和排放行为脱钩, 提出需要用文本细粒度指标区分「谈了什么」与「做了什么」; 本家族借鉴同一方法论精神, 把「对齐度」与「强度」两个正交维度交叉分类, 而非简单以单一情感或关键词计数刻画金科采纳。
【方法学与计算】
subst_adopt_int_p25 在盘上真实的构造分两层: 第一层是文章级二值化——由两个连续型上游测度在每篇文章 (而非 bank-year 聚合均值) 上同时二值化后取逻辑「与」得到, 其一是 policy_cosine_sim (及其 _ctx/_ss 同名轨道变体), 即文章文本与政策/监管语料的余弦相似度, 产出于 stage 16 article_policy_alignment (co-primary Qwen 嵌入主轨, 无后缀); 其二是 fintech_intensity_score, 即该篇文章中金科相关词汇/语义的强度得分, 产出于 stage 15 fintech_intensity。二值化阈值按年份分组 (`groupby('year')`) 分别对当年样本内的 policy_cosine_sim 与 fintech_intensity_score 逐年估计第 25 百分位切点 (而非对聚合后的 article_sim_mean/fintech_intensity_mean 计算样本内整体分位数), 高于当年切点记 1、否则记 0, 两个二值指示变量取逻辑与, 得到文章级指示: 该篇文章同时落在「当年政策对齐度前 75%」与「当年金科强度前 75%」区间时记 1, 否则记 0; sim 或 freq 任一测量缺失 (NaN) 的文章不参与分类, 指示值记 NaN (分母因此是"已测量篇数"而非全部篇数)。第二层是 bank-year 聚合——盘上真正落入面板的 subst_adopt_int_p25{_ctx,_ss} 列, 是把上述文章级 0/1/NaN 指示按 (target_bank, year) 做 `.mean()` 聚合 (pandas groupby mean 自动跳过 NaN) 得到的连续占比, 语义是「该行该年被测量文章中, 落入实质采纳象限的文章占比」, 取值范围 [0,1] 而非离散 {0,1}; 当该行该年全部文章均未测量时, 该占比列本身也是 NaN (未测量, 与 CLAUDE.md 「NaN 保持、listwise 处理」的项目通用口径一致, 不做 fillna(0) 处理)。命名中的 "int" 标识该列属于「Track B (intensity 连续测度)」象限体系, 与并列的 "kw" (Track A, 基于关键词计数的离散测度) 形成方法学对照的两条独立象限化路径, 二者各自 just-identified, 互为稳健性、不分主次, 不可混入同一 over-identified 设定 (如同一 Hansen J 检验)。"p25" 标识文章级二值化所用的年度分位阈值为第 25 百分位。P25 是该象限体系三档阈值梯度 {P25, P50, P75} 中最宽松的一档 (纳入样本比例最高); 项目口径上 P50 (中位数切分) 是与项目 10+ 处中位数分割惯例一致的机制检验基准档, P25/P75 是围绕该基准展开的阈值敏感性稳健性检验档——三档在计量设定上各自 just-identified 并排, 互为稳健性检验、禁止混入同一 over-identified 设定 (如同一 Hansen J 检验), 但在"何档作为正文机制检验的默认呈现"这一叙事选择上, 项目约定以 P50 为基准、P25/P75 供稳健性附表引用, 并非三档在计量地位上完全等权、无任何取舍。
【文献定位】
本族测度的构念定位可归入组织与战略文献中「实质 vs. 符号」采纳区分的量化操作化尝试。Westphal & Zajac (1994, Administrative Science Quarterly) 建立了这一区分的经典范式, 指出治理实践的正式采纳 (formal adoption) 未必伴随实质执行, 二者需要用独立的观测量分别度量而非假定同构; Fiss & Zajac (2006, Academy of Management Journal) 则从话语框架化角度补充了「言」如何被策略性建构以管理外部感知的机制。将该框架迁移到文本挖掘语境时, 需要引入可从大规模非结构化文本中稳定提取的代理变量: 本族选用「政策对齐度」代理「言」(话语层面与监管导向的贴合程度) 、「金科强度」代理「行」(具体技术/业务细节的丰富程度), 这一设计也与 Duchin, Gao & Xu (2025, The Journal of Finance) 在可持续性披露语境下对「披露-实际脱钩」现象的实证识别策略相呼应, 后者同样强调需要用双维度交叉而非单一披露文本指标来甄别名实是否相符。Kutzbach & Pogach (2024, Journal of Financial Intermediation) 的实证发现构成本族「强度」维度经济含义的旁证而非方法论溯源: 该文考察金融科技与银行关系型信贷是互补还是替代, 发现二者关系依赖于金融科技渗透的具体强度而非仅其有无, 提示「金科举措介入信贷关系的程度」本身是一个独立于「话语是否政策对齐」的经济学上有意义的维度——若把强度与对齐度合并为单一综合指数, 会掩盖这种强度依赖性异质性。这一发现支持本族将 fintech_intensity_score 保留为区别于 policy_cosine_sim 的独立测度轴, 而非将其合并为单一综合指数; 但该文本身并非文本化测量方法论文献, 不构成「文本化测量传统」的溯源出处, 本族的文本化操作化方法论根基仍在 Westphal & Zajac (1994) / Fiss & Zajac (2006) 的实质-符号区分传统与 Bingler et al. (2022) 的文本细粒度识别传统。 晚近文献在三个层面为本族补充了锚点。其一是符号-实质二分在数字技术议题下的当代重述: Pan、Xue 与 Liu (2026) 把技术采纳明确二分为「符号性采纳 (symbolic adoption)」与「实质性行动 (substantive action)」, 并将二者的背离操作化为 AI washing 加以实证测量, 为本族 subst (双高) 与 token (高声量、低对齐) 两格所依赖的「同一构念拆成两维并置」提供了 2026 年的存在性证明; 惟其对象是一般企业的 AI 叙事与实际行动, 符号/实质的划分基于组织冗余与披露数据, 既不使用政策文本余弦相似度, 也不做年度分位阈值切分, 层级为企业而非银行-年, 更无以已测量报道篇数为分母的聚合口径。Kaufmann、Krlev 与 Brown (2025) 以影响力投资为田野, 系统刻画 means-ends decoupling (实践在形式上落地却与目标脱节) 的具体机制, 为 subst 与 token 两格的理论区分提供了近期组织学依据; 但该文为定性机制研究, 不构造任何数值指标, 亦无分位阈值二值化与 bank-year 聚合, 其 means-ends 概念与本族「政策余弦 × 金科强度」的操作化仅属理论对应而非同一测量。其二是强度维度的同域应用: Xu (2026) 用文本方法构造银行层面的 FinTech intensity 指标并检验其与经营绩效的关系, 与本族所用 fintech_intensity_score 属同一测度族; 惟其样本为欧洲银行, 文本取自银行自身披露而非第三方中文新闻, intensity 作为连续指标直接进入回归而不做年度分位二值化, 更未与政策相似度交叉形成 2×2 象限, 且属未经同行评审的 SSRN 工作论文, 结论稳健性未定, 故仅作同域存在性旁证。其三是对本族二值化做法本身的反向方法学告诫, 须直面而非回避: Hemelstrand 与 Inoue (2025) 用三组模拟系统论证连续变量二分的方法学代价 —— 二分几乎普遍抬高标准误、进而使显著性检验失准, 并因信息量削减而压低 R² 等效应量, 其明确立场是建议不要二分连续数据。本族把连续的 policy_cosine_sim 与 fintech_intensity_score 按年度 P25 切成指示变量再聚合, 正落在该文告诫的范围内, 使用者应据此理解本族占比列相对于直接使用两个连续测度所付出的效率代价, 并在需要精确推断时优先回到连续测度。须强调的是, 该文并未为 P25/P50/P75 三级阈值梯子背书, 亦未提出「若必须二分则做多切点敏感性检验」的补救建议 —— 阈值梯子是本项目自设的稳健性措施, 其正当性不得援引该文; 该文领域为应用语言学研究方法而非金融/经济学, 论证针对单变量二分对回归推断的影响, 未涉及双变量交叉的 2×2 象限、逐年滚动分位阈值、面板聚合与已测量分母口径。本族之所以仍保留象限设计, 理由在于「实质 vs. 符号」的构念本身即为离散型态学 (typology) 而非连续强度, 且 P25/P50/P75 三档各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 检验 —— 这是对切点任意性的披露式应对, 而非对上述告诫的反驳。
## VAR: subst_adopt_int_p25

【变体差分】
subst_adopt_int_p25 是家族的 canonical (full 轨) 版本, 上游 article_sim_mean 与 fintech_intensity_mean 均取自全文文本 (标题+正文原始内容) 扫描结果, 未做实体窗口或同句共现限定。该列是三轨体系 (full/ctx/ss) 中信息覆盖面最广、噪声也最高的一档: 全文扫描会把与目标银行、金科话语不直接相关的段落一并纳入相似度与强度计算, 因此其数值更接近「整篇报道的总体基调」而非「围绕目标银行-金科交集的精确刻画」。在留篇门控 (full-only, 2026-06-29 起生效) 体系下, 一篇文章是否被判定为「银行金科报道」的门控判据只看 llm_verified_full, 因此本 full 轨列所依赖的 n_articles 分母与留篇集合口径完全对齐主门控, 是该象限体系中样本覆盖最完整的一条轨道。full/ctx/ss 三轨在本族中各自独立计算象限阈值 (P25 分位数逐轨重新估计, 不共享切点), 三者互为稳健性并排, 不设主轨优先级, 严禁在同一 over-identified 设定 (如同一 Hansen J 检验) 中混用来自不同轨道的该家族列作为过度识别工具变量。就经济含义而言, 盘上的 subst_adopt_int_p25 是 bank-year 层面的连续占比而非逐行 0/1 标量: 其数值 = 该行该年被测量文章中「同时落入当年政策对齐度前 75% 与当年金科强度前 75% 区间」的文章占比, 取值范围 [0,1]。P25 是象限体系中文章级二值化门槛最宽松的一档 (纳入被划为「高对齐/高强度」的文章比例最高), 因此该占比列在给定文章库时通常取值也相对更高, 更适合作为「粗筛」层面的实质采纳强度信号; 与之相对, P50/P75 两档阈值更严格 (P50 是与项目 10+ 处中位数分割惯例一致的机制检验基准档), 用于稳健性检验中逐步收紧「实质」的判定标准。使用者在解读该列时应注意, 底层二值化切点是逐年估计的相对阈值 (`groupby('year')` 分位数), 而非固定绝对水平或跨全样本估计的分位数, 因此不同年份的切点数值不同、该占比列的跨年比较隐含"各年内部相对位置"而非"绝对强度水平"的语义, 也不宜跨样本版本 (如加入新年份数据后重估分位数) 直接比较。

## VAR: subst_adopt_int_p25_ctx

【变体差分】
subst_adopt_int_p25_ctx 是三轨体系中的 ctx (context) 轨变体, 其文章级上游 policy_cosine_sim_ctx 与 fintech_intensity_score_ctx (存在同轨变体时优先使用, 否则回退复用 track-agnostic 的 full 列并在日志中披露) 的语义窗口收窄为「标题 + 目标银行实体窗口」文本 (content_ctx, 由 stage 14 ctx_materializer 物化, prepend_title 拼接), 而非全文。相较于 full 轨, ctx 轨的政策对齐度与金科强度测度更聚焦于目标银行被提及的局部语境, 能过滤掉报道中与该行金科业务无直接关联的背景段落, 理论上应能更精确地捕捉「该行本身」的实质采纳信号而非整篇报道混杂的话题噪声。ctx 轨的文章级二值化同样按年份分组独立重估 P25 分位阈值 (不复用 full 轨切点), 二值化后再按 (target_bank, year) 聚合为占比, 与 full/ss 轨互为稳健性并排、不分主次。需要注意的是, 留篇门控 (2026-06-29) 下 ctx 轨已降为 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 轨留篇集合的子集, 即只有已通过 full-only 门控判为「一篇银行金科报道」的文章才会在 ctx 轨上计算并参与该列的分位阈值估计与二值化, ctx 轨本身不独立扩展或收缩样本宇宙。方法学上, ctx 轨与 full 轨的差异纯粹来自输入文本窗口的收窄, 二值化逻辑本身 (逻辑与、P25 分位切点) 与 full 轨完全一致, 因此该列的价值不在于引入新的判定规则, 而在于用更聚焦的语境窗口检验 full 轨的实质采纳判定是否对「报道中与目标银行无关的背景话题噪声」敏感; 若两轨判定高度一致, 说明 full 轨结果具有语境稳健性; 若出现系统性分歧, 则提示 full 轨可能受到报道中非目标银行段落的稀释影响, 此时 ctx 轨提供了更贴近银行本身的替代读数, 供研究者在稳健性表中并列汇报, 而非取二者之一作为唯一「正确」口径。

## VAR: subst_adopt_int_p25_ss

【变体差分】
subst_adopt_int_p25_ss 是三轨体系中的 ss (same-sentence) 轨变体, 其文章级上游 policy_cosine_sim_ss 与 fintech_intensity_score_ss 测度基于「标题 + 目标银行与金科词同句 (±N 句窗口, 默认 N=1, 见 config/filtering.yaml::context_window.ss_sentence_radius) 共现」的最严格语境窗口 (content_ss) 计算, 是三轨中语义窗口最窄、判据最严格的一档, 理论上能最大限度剔除「同篇报道提及但与银行金科交集无关」的话语噪声, 使政策对齐度与金科强度的测度更贴近「该行金科举措被具体描述」的严格情境。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则 content_ss 退化为全文 body (与 full 轨相同文本), 并以 ss_is_fallback=True 标记该行为降级样本, 与 ctx_is_fallback 共享 n_articles 分母口径, 不因回退而制造单边孤儿行。与 ctx 轨一致, ss 轨在留篇门控下同为 conditional-on-full 的稳健性轨, 行宇宙是 full 轨留篇集合的子集; ss 轨的文章级二值化同样按年份分组独立重估 P25 分位阈值, 与 full/ctx 轨各自 just-identified 并排, 互为稳健性检验、不分主次, 严禁三轨混入同一 over-identified Hansen J 设定。由于 ss 轨判据比 ctx 轨更严格 (同句 vs. 实体窗口), 其非回退样本 (ss_is_fallback=False) 的政策对齐度与金科强度测度理论上信噪比最高, 是三轨中对「实质采纳」构念最精确但样本覆盖也最窄的一档; 当某银行金科话语在报道中零散分布、未与目标银行出现在同一句中时, ss 轨会大量触发回退, 此时其信息量退化为等同 full 轨, 研究者在解读 ss 轨结果时应结合 ss_is_fallback 占比评估该轨判定的实际精度增量, 避免在回退比例过高的子样本中过度依赖 ss 轨作为主要证据。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change: Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Kutzbach, M. J., & Pogach, J. (2024). Financial Technology and Relationship Lending: Complements or Substitutes?. Journal of Financial Intermediation, 59, 101101. https://doi.org/10.1016/j.jfi.2024.101101
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap Talk and Cherry-Picking: What ClimateBert Has to Say on Corporate Climate Risk Disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Pan, Y., Xue, F., & Liu, L. (2026). Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing. Information Technology and Management. https://doi.org/10.1007/s10799-026-00501-9
Kaufmann, L., Krlev, G., & Brown, M. (. (2025). In Plain Sight: Mechanisms of means–ends decoupling in impact investing. Organization Studies, 46(5), 667-692. https://doi.org/10.1177/01708406241295505
Xu, F. (2026). Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks. SSRN No. 6922688 [Working Paper]. https://doi.org/10.2139/ssrn.6922688
Hemelstrand, S., & Inoue, T. (2025). Stop splitting hairs: The problems with dichotomizing continuous data in language research. Research Methods in Applied Linguistics, 4(3), 100272. https://doi.org/10.1016/j.rmal.2025.100272
<!-- rendered-citations:end -->
