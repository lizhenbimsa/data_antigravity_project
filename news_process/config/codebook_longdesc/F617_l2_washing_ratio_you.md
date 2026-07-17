---
family_id: F617
columns:
- washing_ratio_you_2018
- washing_ratio_you_2018_ctx
- washing_ratio_you_2018_ss
unit: 比率/占比 (proportion, [0,1]; 银行-年面板层级)
formula: washing_ratio_you_2018{track} = count(you_2018_score{track} > 0 且当期 innovation_substantiveness_full=='象征性') / count(you_2018_score{track} > 0 且 innovation_substantiveness_full 已测量, 即 ∈ {'象征性','实质性'})
producer: pipeline\panel\runner.py (方法 D2 篇章级标记构造与步骤 7h 聚合) ; pipeline\panel\export.py (Stata 变量标签映射)
upstream:
- 21_tone_llms (innovation_substantiveness_full, P3/W&Z 象征性-实质性分类)
- 22_tone_words (you_2018_score_full/_ctx/_ss, You/Zhang/Zhang 2018 词典逐篇打分)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: "AI washing: Strategic disclosure and backlash"
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: Ownership concentration and corporate greenwashing in China's capital markets- Based on a multi-actors perspective
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: '102600'
- doi: "10.1016/j.iref.2026.104974"
  type: "journal"
  authors: "Li, Y., & Zhu, C."
  year: 2026
  title: "Govern digitalization with digitalization: government digital governance and corporate false digital disclosure"
  venue: "International Review of Economics & Finance"
  vol: "106"
  pages_or_artno: "104974"
- doi: "10.1016/j.frl.2024.105401"
  type: "journal"
  authors: "Zhang, Z., Hou, Y., Li, Z., & Li, M."
  year: 2024
  title: "From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105401"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量银行在给定年度媒体报道中"洗稿"倾向的一个单词典变体: 用 You, Zhang & Zhang (2018, Review of Financial Studies)"谁掌握了笔杆子的力量"一文所建的媒体基调词典 (以下简写 you_2018) 单独打分, 与本仓库对每篇报道的实质性/象征性判定 (创新实质性三分类, W&Z 传统, 由 stage 21 LLM 三家投票产出) 交叉, 得到一个以"正面且象征性"文章占"正面且已测量实质性"文章之比"作为核心洗稿信号。直觉是: 一家银行如果在媒体上频繁被以正面基调报道、但那些正面报道的内容多为空洞宣传性质的"象征性"创新叙事 (口号式的战略愿景、跟风概念、无具体产品/流程落地细节), 而非"实质性"创新叙事 (有具体产品发布、技术投入、合作细节的报道), 则该银行存在较高的"漂绿式"/"洗稿式"媒体形象管理动机。这一构念直接承接 Westphal & Zajac (1998) 关于企业采纳表面姿态而非实质变革的组织理论传统, 并借用 You et al. (2018) 的词典化文本测度工具将其操作化为可计算的面板变量。本家族名 `l2_washing_ratio_you` 中的 `you` 明确标记该变体锁定于 you_2018 单一词典, 区别于面板中另有的 LLM 投票法 (`washing_ratio`)、6 词典均值法 (`washing_ratio_dict`)、BERT 3 模型均值法 (`washing_ratio_bert`) 与高置信度子样本法 (`washing_ratio_hc`) 等并行变体; 各变体互为稳健性、不分主次, 详见【方法学与计算】。

【方法学与计算】
分子/分母的构造发生在 `pipeline/panel/runner.py` 中的篇章级标记阶段 (方法 D2: 单词典), 随后在面板聚合步骤 (代码注释所称"步骤 7h") 汇总到银行-年层级, 再由 `pipeline/panel/export.py` 补上 Stata 变量标签并落盘。具体口径: 先取该银行-年内所有 you_2018_score{track} > 0 (即该词典在对应文本轨道上判定为正面基调) 的文章, 在这批文章中, 分子计数其 `innovation_substantiveness_full` 字段被 stage 21 三家 LLM 投票判定为"象征性"的篇数, 分母计数该字段已被成功测量 (即落在 {'象征性','实质性'} 两个有效标签之一, 而非因 LLM 判定失败/平局/拒绝而缺失) 的篇数。该比值就是 washing_ratio_you_2018{track}。这一"分母仅数已测量" 的设计 (代码注释称之为 `_svd_*`, subst-valid denominator) 是 2026-06-11 的一次修复 (fix omni-g-runner-10/14): 此前分母误取全部正面文章 (含实质性分类失败的文章), 若 LLM 分类失败率系统性上升, 会把失败文章错误地当作分母膨胀项, 从而人为压低洗稿率, 造出"分类越差、洗稿率越低"的假象。修复后分母与分子严格同域 (只在已成功测量实质性/象征性的子样本内计算比例), 避免了这一衰减偏误。注意实质性/象征性标签固定取自 `_full` 轨 (`innovation_substantiveness_full`), 不随 track 后缀切换 — 三轨差异只体现在词典打分 `you_2018_score{track}` 上, 象征性判定这一"标尺"始终统一, 使跨轨结果具可比性。
本家族与情感三轨、跨模型稳健性铁律直接相关: `washing_ratio_you_2018` 是该家族在全文轨 (full-only, 与 stage 21 留篇门控 2026-06-29 后的口径一致, 即该银行-年洗稿率计算所纳入的文章集合以 `llm_verified_full == True` 的留篇集为行宇宙基准) 上的口径, `_ctx` 使用标题+实体窗口文本轨的 you_2018 词典打分, `_ss` 使用标题+银行∧金科同句共现窗文本轨的打分 (无该窗口共现时按 `content_ss` 回退语义镜像 `_ctx`: 回退为全文正文, `ss_is_fallback` 标记为 True, 分母 n_articles 与全文轨共享)。三轨在方法论上各自 just-identified 并排, 互为稳健性、不分主次, 绝不应混入同一个 over-identified Hansen J 检验中联合识别。
需特别提醒的构念边界: `you_2018` 词典本身是一个基调 (语气正负) 词典, 并非"象征性/实质性"分类器 — 后者来自完全独立的 stage 21 LLM 三家投票管线 (P3/W&Z 创新实质性维度, `LLM_CLASS_SPEC` 的一支)。washing_ratio_you_2018 是二者的交叉乘积式指标, 词典给出"该文章语气是否正面"的信号, LLM 给出"该文章内容是否空洞"的信号, 二者同时成立才计入分子。因此该指标的有效性同时依赖词典打分与 LLM 分类两条链路的质量, 是一个复合测度而非单一信号的直接读出。

【文献定位】
核心方法学锚点是 You, Zhang & Zhang (2018, Review of Financial Studies) 关于媒体基调词典构造与"谁掌握了笔杆子的力量"的研究, 本家族即以其词典分支命名并直接复用其正负面词表逻辑对中文财经报道打分。"洗稿/漂绿"构念的操作化借鉴 Gorovaia & Makrominas (2024, European Financial Management) 使用自然语言处理方法从企业社会责任报告中识别漂绿文本的思路 — 该文将"言辞正面但实质缺位"的文本模式系统化为可计算指标, 与本家族"正面基调 ∧ 象征性内容"的交叉构造在方法论精神上一致。近期文献进一步确认此类"策略性信息披露与后续舆论反噬"的现象仍是活跃研究前沿, 如 Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 讨论的"AI 洗白" (AI washing) 中策略性披露与市场反弹机制, 以及 Fan, Tang, Huang & Yang (2025, Pacific-Basin Finance Journal) 基于多主体视角考察中国资本市场股权集中度与企业漂绿行为的关系, 均为本家族测度所试图捕捉的"言辞与实质脱节"现象提供了跨市场、跨主题的持续实证支持。 该构念在中文语境下的最新前沿测度可参照 Li 与 Zhu (2026): 该文构造中国企业"虚假数字化披露"(false digital disclosure)测度并检验政府数字治理对其的抑制作用, 其"数字化叙事强度与实质数字化不匹配"的识别逻辑与本家族分子(正面基调 ∧ 实质性缺席)同义。迁移边界在于: 该文测量对象为企业年报自述文本, 参照系为企业内部数字资产与投入, 单位为公司-年; 本家族测量第三方媒体报道, 实质性由 LLM 逐篇判定而非与财务投入比对, 单位为银行-年, 且该文未使用中文情感词典分层, 因此不锚定 you_2018 词典判定器口径本身。分母的结构性占比设计则可与 Zhang、Hou、Li 与 Li (2024) 相参照: 该文考察 ESG 评级如何推动企业创新结构由象征性向实质性迁移, 把象征性占比作为可随外部监督变化的构成比而非绝对水平来处理, 与本列取"象征性 / 正面且实质性已测"比率的同域设计逻辑一致; 但其比例基于专利结构数据, 主体为 A 股非金融企业, 驱动因素为 ESG 评级, 且全文未使用任何文本判定器, 故仅锚定象征占比这一构念, 不涉及本家族词典与 LLM 交叉的复合判据。
## VAR: washing_ratio_you_2018

【变体差分】
本列是家族的 full 轨 canonical 版本: 分子/分母中的词典打分均取 `you_2018_score_full` (即基于标题+全文正文文本计算的 you_2018 词典基调分), 象征性/实质性标签固定取 `innovation_substantiveness_full`。该轨与 stage 21 留篇门控 (2026-06-29) 的行宇宙口径完全一致 — 门控判定"是否为一篇有效银行-金科报道"本身就是基于 `llm_verified_full == True`, 因此本列天然对齐主留篇集, 是三轨中承担样本量最大、覆盖面最广的一支, 常被视为多数下游稳健性表格的默认参照轨, 但按本仓库口径铁律, 它与 `_ctx`/`_ss` 两支仍是并排的互为稳健性关系, 不因样本量优势而享有"主指标"地位; 三者应在实证表格中平行报告, 而非彼此嵌套进同一联立方程组识别。
从计算路径看, 该轨的分子分母窗口最宽: `you_2018_score_full` 是把整篇文章 (含标题) 通读一遍后给出的基调分, 不做任何截断或聚焦, 因此该列既包含直接讨论银行与金科合作/创新的核心段落, 也包含文章其他部分 (如公司整体经营情况、行业背景铺垫) 的语气信息。这意味着该列对"文章整体基调"最敏感, 但也最容易被与银行-金科主题无关的段落稀释或反向拉扯, 这正是 `_ctx`/`_ss` 两轨希望通过收窄窗口予以缓解的问题。研究者若观察到 `_full` 与 `_ctx`/`_ss` 结果方向一致但幅度不同, 应理解为窗口宽窄导致的信噪比差异, 而非任一轨"更正确"; 若三轨方向出现分歧, 则提示该银行-年的洗稿信号对文本窗口选择较为敏感, 需结合具体报道内容进一步核查, 而不应简单取平均或挑选对结果更有利的一轨。

## VAR: washing_ratio_you_2018_ctx

【变体差分】
本列切换词典打分至 `_ctx` 轨: `you_2018_score_ctx` 基于"标题 + 实体窗口" (目标银行/金科相关实体附近的截取文本) 计算, 而非全文正文。这一切换的动机是控制全文正文中大量与银行-金科关系无关的段落 (如公司其他业务板块新闻、行业综述性内容) 对词典打分的稀释或污染, 使基调判定更聚焦于与目标实体直接相关的语境。象征性/实质性标签仍固定取 `innovation_substantiveness_full` (不随 track 切换, 详见 CORE), 因此本列与 canonical 列的唯一差异是分子/分母判据中"是否正面"这一条件所依赖的文本窗口, 象征性判定标尺保持统一以确保跨轨结果的可比性。行宇宙: 与 `_full`/`_ss` 共享同一留篇集 (full-only 门控), `_ctx` 本身不产生独立的样本纳入/剔除逻辑, 是 conditional-on-full 的测度轨。
实体窗口的物化发生在 stage 14 `ctx_materializer` (`prepend_title`, 见 CLAUDE.md 三轨架构说明), 与 stage 21 情感三轨、stage 22 词典三轨、stage 15 fintech 强度、stage 16 政策对齐等下游模块共用同一份 `content_ctx` 列, 因此本列与仓库内其他 `_ctx` 后缀测度在窗口定义上保持严格一致, 便于跨家族横向比较。由于窗口更窄, 该列相对 `_full` 轨样本内变异往往更集中在与银行-金科关系直接相关的语句上, 在存在大量"标题党"或行业综述式报道的语料中, `_ctx` 轨的洗稿信号通常比 `_full` 轨更能剥离无关段落的噪声, 但代价是当实体窗口截取过窄时可能丢失必要的上下文语气线索 (如反讽、让步转折等需要跨句理解的语言现象), 这也是为何该轨与 `_full`/`_ss` 应作为并排稳健性检验而非互相替代。

## VAR: washing_ratio_you_2018_ss

【变体差分】
本列切换词典打分至 `_ss` 轨: `you_2018_score_ss` 基于"标题 + 银行∧金科同句共现窗" (仅取目标银行与金科关键词同句出现的句子, 半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 计算基调分, 是三轨中窗口最窄、语境约束最严格的一支。当某篇文章不存在银行∧金科同句共现时, 按镜像 `_ctx` 的回退语义处理: `content_ss` 整体回退为全文正文 body, 对应的 `ss_is_fallback` 标记置 True, 该情形下本列在分母/分子上与 `_full` 轨共享同一批文章 (n_articles 分母口径不变)。象征性/实质性标签同样固定取 `innovation_substantiveness_full`, 差异仅体现在词典正负判定所依赖的文本窗口宽窄上。本列与 `_full`/`_ctx` 一样是留篇门控 (full-only) 下的 conditional-on-full 稳健性轨, 三者各自 just-identified 并排, 不应混入同一个 over-identified Hansen J 联立识别方程。
由于同句共现的判据比实体窗口更严格 (要求银行名与金科关键词落在同一句而非邻近句段), 该轨天然更容易触发回退, 在覆盖率较低的银行-年组合上 `ss_is_fallback` 比例可能偏高, 此时本列在数值上退化为 `_full` 轨的一个子集口径, 与 `_full` 高度重合是回退机制的预期结果而非计算错误。当同句共现确实存在时, `_ss` 轨给出的是三轨中语境最纯粹、噪声最小的基调信号, 因为它排除了同一段落内与银行-金科关系无关的其他句子, 仅保留银行与金科概念直接并置出现的语句。这使得 `_ss` 轨在检验"洗稿"这一构念时具有独特价值: 若一篇报道中银行与金科同句出现处语气正面, 但该正面语气对应的创新叙事被 LLM 判为象征性而非实质性, 则该证据链条比全文轨或实体窗口轨更直接地指向"标题/邻近文本层面的正面包装与内容实质脱节"这一洗稿核心特征。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets- Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Li, Y., & Zhu, C. (2026). Govern digitalization with digitalization: government digital governance and corporate false digital disclosure. International Review of Economics & Finance, 106, 104974. https://doi.org/10.1016/j.iref.2026.104974
Zhang, Z., Hou, Y., Li, Z., & Li, M. (2024). From symbolic to substantive green innovation: How does ESG ratings optimize corporate green innovation structure. Finance Research Letters, 63, 105401. https://doi.org/10.1016/j.frl.2024.105401
<!-- rendered-citations:end -->
