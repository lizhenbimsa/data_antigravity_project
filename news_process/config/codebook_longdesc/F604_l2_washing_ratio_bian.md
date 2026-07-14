---
family_id: F604
columns:
- washing_ratio_bian_2021
- washing_ratio_bian_2021_ctx
- washing_ratio_bian_2021_ss
unit: 比率/占比 (proportion, 定义域 [0,1]; substvalid 分母为 0 时输出 NaN, 非 0)
formula: 'washing_ratio_bian_2021{track} = bian_2021_pos_symb_count{track} / bian_2021_pos_substvalid_count{track} (旧 schema 回退 bian_2021_pos_count{track}); 分子=按 Bian et al. (2021) 中文金融情感词典判正 ∧ 该篇 innovation_substantiveness_full=="象征性" 的报道数; 分母=按同词典判正 ∧ 该篇实质性维度已被 LLM 有效测量 (象征性∪实质性均计入) 的报道数'
producer: pipeline\panel\runner.py (`_compute_washing_ratio_variants` 族; `_svd_denom`/`_safe_ratio` 辅助; codebook.py 仅接元数据发射)
upstream:
- 12_news_fintech.py (bian_2021_score{track} 词典打分)
- 21_tone_llms.py (innovation_substantiveness_full 象征性/实质性分类, P3 W&Z 构念, full-only 门控)
- 14_materialize_ctx.py (content_ctx/content_ss 三轨文本物化, 供 bian_2021_score_ctx/_ss 消费)
citations:
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper No. 3446388
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: Ownership concentration and corporate greenwashing in China's capital markets, Based on a multi-actors perspective
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: Article 102600
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"洗稿率" (washing ratio) 构念: 在全部被词典判定为正面情绪的银行金科报道中, 有多大比例只是象征性 (symbolic) 表态而非实质性 (substantive) 内容支撑。这一构念对应企业传播文献中的"象征性合规 vs 实质性合规"二分, 与近年兴起的绿色/概念"洗白" (washing / greenwashing) 文献同源: 企业或媒体可能大量释放正面措辞以营造创新、合规或转型的印象, 而这些措辞并未对应可验证的实质动作。家族名以 bian 命名, 表明其分子分母的正/负极性判定来自 Bian, Jia, Li & Yan (2021, SSRN No. 3446388) 构建的中文金融情感词典 (`bian_2021` 词典), 该词典是 pipeline 六词典体系 (词典 D2 单词典族) 之一, 与 Du et al. (2022, Review of Finance) 提出的中文金融情感词典构成互补参照: 两者均针对中文财经文本的领域特异性 (domain specificity) 问题, 主张脱离英文 Loughran-McDonald 词表直接翻译, 而应基于中文财经语料重新构造正负词库。washing_ratio_bian_2021 家族是该词典驱动 pipeline 洗稿率矩阵 (方法 D2: 逐词典单独计算) 中的一个成员, 与跨词典均值版本 washing_ratio_dict (F-其他家族)、单模型 LLM 版本 washing_ratio_{gpt54nano,gemini31,deepseekv4} 以及跨 BERT 均值版本 washing_ratio_bert 并列, 是 pipeline "媒体质量/洗稿" 测度矩阵 (Bingler et al. 2022, FRL 传统) 的众多稳健性并排轨之一。

【方法学与计算】
分子分母构造遵循同一"分母同域计数"原则 (2026-06-11 修复, omni-g-runner-10/14): 分子 bian_2021_pos_symb_count{track} 统计 bian_2021 词典打分 (`bian_2021_score{track}`) 为正 且 该篇文章 innovation_substantiveness_full 维度被 LLM 三家投票判定为"象征性"的报道数; 分母 bian_2021_pos_substvalid_count{track} 统计 bian_2021 词典判正 且 该篇实质性维度已被有效测量 (象征性∪实质性两类均计入, 不含未测量/拒绝) 的报道数。二者比值即为该银行-年份样本中"词典判正报道里有多少是纯象征性表态"。若面板 schema 缺失 substvalid 分母列 (旧版本兼容路径), producer 会告警回退到物理分母 bian_2021_pos_count{track} (未按实质性维度可测性筛选), 此时口径与新版存在系统性差异, 使用者应核对面板 schema 版本。分母为 0 (该银行-年该轨无任何 bian_2021 判正报道) 时经 `_safe_ratio` 输出 NaN 而非 0, 避免把"无样本"误读为"零洗稿"。判定"象征性/实质性"的分类器本身固定取自 innovation_substantiveness_full — 即便本家族存在 ctx/ss 轨变体, 象征性/实质性标签始终由 full-only 文本 (标题+全文) 判定 (2026-06-29 留篇门控口径), 三轨之间真正变动的只是 bian_2021 词典打分所依赖的文本窗口 (full=标题+正文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗)。这一"分类器 full-only 固定、极性打分逐轨变动"的构造与 pipeline P3 治理维度稳健性设计 (LLM_CLASS_SPEC 三元映射) 一脉相承。

【文献定位】
洗稿/漂绿 (washing) 概念在会计与金融文献中近年迅速扩张: Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法从企业社会责任报告中识别漂绿, 关注"言辞承诺"与"实质行动"的脱节, 与本家族"象征性正面报道占比"的构念高度一致; Fan, Tang, Huang & Yang (2025, Pacific-Basin Finance Journal) 进一步在中国资本市场情境下研究股权集中度与企业漂绿的关系, 提供了本家族在银行业情境外的平行证据; Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 将洗稿概念延伸到"AI washing" (人工智能概念的策略性披露与反噬), 与本项目银行-金科合作报道的核心研究情境直接呼应, 提示媒体报道中的"创新叙事"同样可能存在策略性夸大而非实质变革。词典层面, Bian et al. (2021) 与 Du et al. (2022, Review of Finance) 是本 pipeline 六词典体系中专门针对中文财经文本情境构建的两部代表性词典, 二者均强调英文金融情感词表 (如 Loughran & McDonald 2011) 直接翻译到中文语境存在系统性失真, 主张基于中文财经语料的领域特异性重新标注正负词汇 — 这构成了 washing_ratio 矩阵按词典逐一并排计算 (而非仅依赖单一词典) 的方法论依据: 不同词典对"正面"的判定标准存在差异, 逐词典单独产出洗稿率可以检验该构念是否对具体词典选择稳健。

## VAR: washing_ratio_bian_2021

【变体差分】
本列是家族的 full 轨 (无后缀), 是三轨中的 canonical 主测度。分子分母均取自标题+正文全文 (`content_full`) 上计算的 bian_2021_score_full 与 innovation_substantiveness_full 分类: 分子 `bian_2021_pos_symb_count_full` 为 bian_2021 词典判正 (`bian_2021_score_full > 0`) 且 LLM 判定为"象征性"的报道数, 分母 `bian_2021_pos_substvalid_count_full` 为 bian_2021 词典判正 且 实质性维度已有效测量的报道数 (若 substvalid 分母列缺失则回退物理正面计数 `bian_2021_pos_count_full`)。full 轨覆盖全篇正文, 信息量最完整, 但也可能因全文中出现的与目标银行-金科合作关系无关的正面/象征性措辞而引入噪声。按 2026-06-29 起生效的留篇门控口径, 银行-金科报道的"是否留篇"判据本身即取自 full 轨 LLM 判定, 因此 full 轨在留篇集合内是无额外条件限制的基准测度; ctx/ss 两轨在本家族中相对 full 轨是"以留篇集合为行宇宙的条件测度/稳健性轨", 三轨之间不应被混入同一个 over-identified 的 Hansen J 检验, 而应各自 just-identified 并排解读、互为稳健性、不分主次。使用者若在同一张回归表里同时报告 full/ctx/ss 三列系数, 应把三者当作彼此独立的稳健性检验并排陈列, 而不是把三者堆进一个联合矩条件下用工具变量个数超过内生变量个数的方式做单一联合估计; 三者共同支持的结论是"该银行-年份的正面报道中象征性表态占比"这一构念在不同文本窗口口径下是否保持稳定, 而不是彼此互相修正或加权平均出一个"更优"的合成估计。当 bian_2021_pos_symb_count_full 或 bian_2021_pos_substvalid_count_full 任一分子分母因该银行-年份样本量过小而出现极端值 (如全部或几乎全部正面报道均被判为象征性) 时, 应结合 n_articles_llm_valid_full 等分母基数一并解读, 避免把小样本波动误读为系统性洗稿行为。

## VAR: washing_ratio_bian_2021_ctx

【变体差分】
本列是三轨中的 ctx (实体上下文窗) 轨。与 full 轨的唯一构造差异在于: bian_2021 词典打分所依赖的输入文本换成 `content_ctx` (标题 + 目标银行/金科实体附近的上下文窗口, 而非全文), 即 `bian_2021_score_ctx` 与其对应的 bian_2021_pos_symb_count_ctx / bian_2021_pos_substvalid_count_ctx 分子分母, 均限定在实体窗口内重新计算词典极性与"是否判正"; 而是否"象征性"这一分类标签仍固定沿用 innovation_substantiveness_full (full-only 分类不随轨切换, 见家族 CORE 说明)。ctx 轨的构念含义是: 把词典打分的关注范围收窄到与目标银行-金科关系直接相关的文本片段, 从而降低全文中无关段落 (如企业整体财报、其他业务条线新闻) 带来的极性判定噪声, 是 full 轨的稳健性并排测度而非替代。若该银行-年份样本没有形成有效的实体窗口共现 (即无银行∧金科在窗口内共现), 相应的 `content_ctx` 会退化为全文 body 且 `ctx_is_fallback` 标记为 True, 此时 ctx 轨在数值上会趋近但不严格等于 full 轨 (因回退发生在文本物化层, 计数分母 n_articles 与 full 轨共享)。按家族口径铁律, ctx 轨与 full/ss 轨各自 just-identified 并排, 禁止混入同一个 over-identified Hansen J。ctx 轨对研究设计的价值在于: 当某银行同时经营多条业务线 (如零售、对公、理财、金融科技子公司) 且新闻稿件常常在同一篇报道中混谈多项业务进展时, 单纯依赖全文词典打分容易把与银行-金科合作无关的正面措辞 (例如对公业务扩张、股价表现等) 也计入分子分母, 从而稀释或放大洗稿率的真实信号; ctx 轨通过把词典打分文本收窄到目标实体附近, 更精确地锚定"针对银行-金科关系本身"的情绪极性, 是 full 轨在测度精度维度上的互补稳健性检验, 而非替代或修正。研究者在解释 ctx 轨与 full 轨系数差异时, 应优先归因于文本窗口收窄带来的信号纯化效应, 而非简单假定某一轨"更正确"。"象征性/实质性" 分类标签本身不随 ctx/full 切换而改变, 意味着 full 轨与 ctx 轨的差异完全来自词典打分文本窗口的变化, 而不是分类器口径的变化, 这也是三轨之间可以被视为严格并排稳健性检验 (而非互相嵌套或互相修正) 的关键前提。

## VAR: washing_ratio_bian_2021_ss

【变体差分】
本列是三轨中的 ss (银行∧金科同句) 轨, 是三轨中文本窗口最窄、判定条件最严格的一支。bian_2021 词典打分依赖的输入文本换成 `content_ss` — 仅取标题与目标银行、金科实体在同一句子内 (句半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句) 共现的片段拼接, 由此计算 `bian_2021_score_ss` 及对应的 bian_2021_pos_symb_count_ss / bian_2021_pos_substvalid_count_ss。ss 轨的回退语义严格镜像 ctx 轨: 若该篇报道不存在银行∧金科同句共现, `content_ss` 退化为全文 body、`ss_is_fallback` 标记为 True, 并与 ctx 轨共享同一个 `n_articles` 分母口径, 而非另起单独的样本框架。是否"象征性"的分类标签同样固定取自 innovation_substantiveness_full, 不随 ss 轨的文本收窄而改变。ss 轨的构念意义在于: 用最严格的"同句强共现"证据来判断该篇报道的正面措辞是否确实是针对银行-金科合作这一具体关系的表态, 从而在最保守的样本口径下检验洗稿率结论是否依然成立。三轨 (full/ctx/ss) 之间刻意设计为互为稳健性、不分主次的并排测度, 任何回归设定都不应把三轨系数同时塞进单一的 over-identified Hansen J 检验框架中联合识别。相较 ctx 轨的实体窗口 (以目标实体为中心的段落级邻近), ss 轨要求银行与金科关键词严格出现在同一自然句内 (句半径参数决定是否放宽到相邻 ±N 句), 因此在文本证据强度上比 ctx 轨更保守: 一篇报道即便在实体窗口内出现正面措辞, 也可能因银行与金科分处不同句子而在 ss 轨上被判定为无有效共现进而回退全文。这意味着 ss 轨样本中真正参与词典打分的报道子集通常比 ctx 轨更小、证据更集中, 洗稿率数值在 ss 轨上的波动性 (尤其在银行-年份报道量本就稀少的样本中) 可能因分母基数更小而偏大, 解读时应结合 ss 轨自身的 n_articles 分母与 ss_is_fallback 占比一并核查, 不能脱离样本规模孤立比较三轨数值大小。ss 轨与 stage 13 共现硬过滤 (`sentence_radius=1` + `match_in_title=true`) 所用的同句共现原语在判据参数上同源但服务于不同环节 — stage 13 的共现判据用于文章级留篇/剔除, 本家族 ss 轨的同句共现判据则只影响 `content_ss` 文本物化与其上的词典打分文本范围, 二者不可混同。

<!-- rendered-citations:begin -->
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets, Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
<!-- rendered-citations:end -->
