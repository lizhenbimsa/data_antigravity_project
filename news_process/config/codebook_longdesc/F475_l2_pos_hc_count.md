---
family_id: F475
columns:
- pos_hc_count_ctx
- pos_hc_count_full
- pos_hc_count_ss
unit: 篇数/计数 (count)
formula: 'pos_hc_count{track} = sum(_is_pos_hc{track}), 逐 track (full/ctx/ss) 在 bank-year 分组内对文章级高置信度正面标记求和; _is_pos_hc{track} 是"高置信度正面"文章级布尔标记, 定义为该篇同时满足 (a) LLM 共识判正 (pos_col=is_positive{track}==1, 即三家 LLM 投票多数一致为正) 且 (b) 该判正在三家 LLM 内部的一致率不低于阈值 (agr_col=llm_agreement_rate{track} >= HC_AGREEMENT_THRESHOLD, 阈值取 2/3 - 1e-9 以把恰好 2/3 一致档纳入) 的双条件交集标记 (runner.py 方法 F 段), 全程只消费三家 LLM 内部投票分布, 不涉及词典 (_is_dict_positive) 或 BERT (_is_bert_positive) 口径, 与单一方法裸 pos_count 的差异在于额外叠加了"LLM 内部一致率"这一置信度门槛, 而非跨方法(词典/BERT)交叉验证'
producer: "pipeline/panel/runner.py (标记构造, L1088-1104, 方法 F: 高置信度子样本) ; pipeline/panel/runner.py (下游 washing_ratio_hc 消费, L2286-2294, 方法 F 块)"
upstream:
- 21_tone_llms (三家 LLM 投票共识 is_positive{track} 与内部一致率 llm_agreement_rate{track})
- 40_panel_export_main (bank-year 聚合)
citations:
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: Count (and count-like) data in finance
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 529-551
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: Bank transparency and deposit flows
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 475-501
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: Annual report readability, current earnings, and earnings persistence
  venue: Journal of Accounting and Economics
  vol: '45'
  issue: 2-3
  pages_or_artno: 221-247
new_dois: []
---

## CORE

【构念与来源】
本家族 l2_pos_hc_count 度量的是"高置信度正面报道计数"——在 bank-year 分组内, 对文章级高置信度正面标记 `_is_pos_hc{track}` 求和得到的篇数计数, 三个变体 `pos_hc_count_full` / `pos_hc_count_ctx` / `pos_hc_count_ss` 分别对应全文、实体窗口、银行∧金科同句三条文本轨道的独立计数。与家族内相邻的 `pos_count{track}` (裸单方法正面计数, 见 F461 等家族) 不同, `pos_hc_count{track}` 不是三家 LLM 多数投票共识判正的直接原样计数, 而是 producer `runner.py` 聚合区块「洗稿率聚合: 多方法 × 三轨 full/ctx/ss」中标注为「方法 F: 高置信度子样本」的双条件加严派生量: 一篇报道要计入高置信度正面子样本, 必须同时满足 (a) `is_positive{track}` 为 1, 即三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 多数投票共识判正; 且 (b) `llm_agreement_rate{track}` 不低于阈值 `HC_AGREEMENT_THRESHOLD` (取 2/3 − 1e-9, 使恰好 2/3 一致档按声明构念纳入而非被浮点比较误排除)。"高置信度"这一构念名的真实含义是"三家 LLM 内部投票的一致程度", 即多数判正是否伴随着高度一致 (而非勉强的 2 票对 1 票擦边通过); 满足双条件时文章级布尔标记记为 1, 否则记为 0; bank-year 层面再对该标记求和即得本家族三列。这一设计不涉及词典 (stage 22) 或 BERT (stage 23) 口径的任何交叉比对——`_is_pos_hc{track}` 的全部输入信号都来自 stage 21 三家 LLM 投票内部的分布特征, 不是词典/LLM/BERT 三种测度法之间的跨方法交集验证。该设计的动机来自套话/洗稿(boilerplate/text-recycling)诊断的现实需要: 一篇报道即便被三家 LLM 多数判正, 若三家内部意见分歧较大 (例如恰好 2 票对 1 票), 该正面判定的可靠性相对较低, 用于分母基数时更容易引入噪声; 提高对内部一致率的门槛能压低这类边缘擦边样本混入高置信度子样本的概率, 为下游「washing_ratio_hc」(洗稿率-高置信度口径, 定义为高置信度正面符号化子集占高置信度正面基数的比例, 见 runner.py 方法 F 段) 提供更干净的分子/分母基数。

【方法学与计算】
计算链路分两层。第一层在文章级 (article-level) 完成于 `runner.py`: 上游 stage 21 (`21_tone_llms`) 产出三家 LLM 投票共识列 `is_positive{track}` (取值来自 `llm_vote_tone{track}` 多数一致判正的布尔化) 以及内部一致率列 `llm_agreement_rate{track}`; `runner.py` 方法 F 代码块以 `agr_col = f'llm_agreement_rate{track}'; _hc = df[agr_col].fillna(0) >= HC_AGREEMENT_THRESHOLD` 求出高一致率掩码, 再与 `pos_col`(即 `is_positive{track}`, nullable Int8 先 `fillna(0)` 防空值误判) 的判正掩码取逻辑与 (`&`), 合成 `_is_pos_hc{track}` 这一双条件交集标记; 同一代码块内还并列产出 `_is_pos_symb_hc{track}` (叠加符号化过滤) 与 `_svd_pos_hc{track}` (叠加实质有效性口径子集测量), 三者共享同一高置信度基础掩码但用于不同下游分子。第二层是本家族真正的聚合动作: `agg[f'pos_hc_count{track}'] = (f'_is_pos_hc{track}', 'sum')`, 即在 `groupby(bank, year)` 语境下对 0/1 标记求和, 得到该行 bank-year 单元内的高置信度正面报道篇数, 数据类型为 double (整数计数在含 NaN 场景下以浮点承载)。三轨 (`_full`/`_ctx`/`_ss`) 严格并列独立计算, 互不借用彼此的分子分母: `_full` 轨扫描全文 (标题+正文) 文本; `_ctx` 轨扫描标题+实体窗口文本; `_ss` 轨扫描银行∧金科同句±N窗口文本 (窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认1)。`_ss` 轨的回退语义镜像 `_ctx` 轨: 若某篇文章不存在银行∧金科的同句共现, 则 `content_ss` 退化为全文 body, 对应 `ss_is_fallback` 标记为 True, 该情形下的高置信度判定仍照常参与计数, 不因回退而被剔除或单独处理。本家族的计数本身不涉及留篇门控之外的额外过滤, 但其分母意义上的可比性仍需注意: stage 21 的"是否判为一篇银行金科报道"这一留篇门控口径为 full-only (2026-06-29 起生效), 即 `llm_verified_full == True` 是行宇宙的唯一裁决依据, ctx/ss 两轨的高置信度计数是在同一行宇宙 (full 留篇集合的子集) 内、各自轨道文本上重新计算的测度/稳健性轨, 而非独立留篇。

【文献定位】
高置信度子样本设计与洗稿率诊断的一般计量传统直接呼应 Cohn, Liu & Wardlaw (2022, JFE) 关于金融研究中计数类与类计数(count-like)数据的方法论讨论——该文强调计数变量在截断、稀疏、异方差等场景下若不做稳健化处理, 容易在后续回归中放大测量误差; 本家族用"LLM 内部一致率门槛"而非裸单方法计数作为高置信度计数轨的设计选择, 与该文提倡的计数数据稳健化取向相呼应, 但需明确的是该文并非本设计的直接方法论出处, 而是同一研究关切下的一般性文献支持 (producer 源码内联注释标注的直接参照是 Shapiro et al. 2022, Journal of Economics, 该文未收录于本项目引文白名单池, 故本处不直接引注, 仅据代码注释如实说明); 本家族条目采纳 Cohn et al. (2022) 作为计数数据稳健性处理的独立佐证, 不构成对代码注释所引文献的替代或等价声称。多方法/多信号一致性确认正面情感信号可靠性的思路亦可参照银行业文本情感测度的中国语境应用, 例如 Fang, Wang, Wang & Yuan (2024, IREF) 在研究媒体情感与银行系统性风险关系时同样强调情感信号的稳健提取对下游存款稳定性推断的重要性, 与本项目 `pos_hc_count` 服务于 washing_ratio_hc 这一下游稳健性诊断量的设计初衷一致。银行文本披露信号可靠性的更广义文献脉络还包括 Chen, Goldstein, Huang & Vashishtha (2022, JFE) 对银行透明度与存款流动关系的实证, 该文提示文本类披露信号在银行业场景下的信息含量高度依赖测度构造的稳健性, 支持本家族在裸判正之外叠加一致率门槛的设计选择; 而计数类文本测度的可靠性度量传统亦可回溯至 Li (2008, JAE) 关于年报可读性与盈余持续性关系研究中对文本正面/负面词计数构造的早期规范化讨论。三轨并列、互为稳健性、禁止混入同一 over-identified Hansen J 的设计铁律与本项目情感测度全线的三轨口径 (full/ctx/ss) 完全一致, 三个轨道各自 just-identified, 不应在同一工具变量识别框架下混合使用。

## VAR: pos_hc_count_ctx

【变体差分】
`pos_hc_count_ctx` 是本家族在 ctx (实体窗口) 轨道上的高置信度正面报道计数。区别于 `_full` 轨扫描标题+全文正文, ctx 轨扫描的是标题+目标银行实体所在窗口内的文本片段 (由 stage 14 `ctx_materializer` 物化为 `content_ctx` 列, 采用 `prepend_title` 方式将标题拼接在窗口文本之前), 意在剔除同一篇报道中与目标银行无关的段落对情感/高置信度判定的稀释或污染。计算上, `_is_pos_hc_ctx` 标记的产生逻辑与 full 轨完全对称——同样要求 (a) 三家 LLM 投票在 ctx 轨文本上多数一致判正 (`is_positive_ctx==1`) 且 (b) 三家 LLM 在 ctx 轨文本上的内部一致率 `llm_agreement_rate_ctx` 不低于 `HC_AGREEMENT_THRESHOLD`, 全程不涉及词典/BERT 口径, 唯一差异是输入文本换成了 `content_ctx`。聚合公式为 `agg['pos_hc_count_ctx'] = ('_is_pos_hc_ctx', 'sum')`, 在 bank-year 分组内对该标记求和。行宇宙层面, ctx 轨的留篇门控继承 full-only 铁律: 是否将某篇文章计入某 bank-year 的行宇宙, 完全由 `llm_verified_full == True` 决定, ctx 轨本身不产生独立的留篇判定, 因此 `pos_hc_count_ctx` 应理解为"在 full 轨已确认相关的报道子集上, 用 ctx 窗口文本重新测算高置信度正面计数"的稳健性/测度轨, 而非另一套独立样本。与 `pos_hc_count_full` 相比, ctx 轨在实体边界清晰、多主体共现频繁的长文中通常给出更聚焦的高置信度计数 (窗口内噪声更少), 但也可能因窗口截断丢失原本支撑判正的语境线索而低估计数; 与 `pos_hc_count_ss` 相比, ctx 轨的窗口范围更宽 (实体窗口 vs. 严格同句), 因此 ctx 轨计数在多数情形下不小于 ss 轨计数。三轨 (full/ctx/ss) 应作为互为稳健性、不分主次的并列测度对待, 在识别策略上各自 just-identified, 禁止混入同一 over-identified Hansen J 框架联合使用。

## VAR: pos_hc_count_full

【变体差分】
`pos_hc_count_full` 是本家族的 full (全文) 轨道计数, 也是三轨中文本覆盖范围最宽的一支: 扫描文本为标题+正文全文 (`content_full`, 由 stage 14 以 `prepend_title` 方式物化, 原始"内容"列本身不改动)。`_is_pos_hc_full` 标记要求 (a) 三家 LLM (gpt54nano/gemini31/deepseekv4) 在全文文本上的多数投票判正 (`is_positive_full==1`), 且 (b) 三家 LLM 在全文文本上的内部一致率 `llm_agreement_rate_full` 不低于 `HC_AGREEMENT_THRESHOLD`, 全程不涉及词典与 BERT 口径的交叉比对, 聚合公式为 `agg['pos_hc_count_full'] = ('_is_pos_hc_full', 'sum')`。full 轨在本项目情感测度体系中具有特殊地位: 它是 stage 21 留篇门控 (`llm_verified_full == True`) 的直接依据轨道, 即"一篇报道是否被认定为银行金科相关报道并计入 bank-year 行宇宙"这一判定完全基于 full 轨的 LLM 验证结果 (2026-06-29 起生效的 full-only 门控铁律), ctx/ss 两轨则是在该行宇宙确定之后, 各自在窗口/同句文本上重新计算的 conditional-on-full 测度轨。因此 `pos_hc_count_full` 在计数口径上具有"分母最完整、覆盖面最广"的特征——它不受实体窗口截断或同句共现回退的影响, 是三轨中受文本截断噪声干扰最小的一支; 但也正因扫描全文, 该轨更容易把与目标银行不直接相关的段落情感信号纳入高置信度判定, 从而在个别文章上产生比 ctx/ss 更宽松的正面判定边界。在下游 washing_ratio_hc 洗稿率诊断中, `pos_hc_count_full` 与 `pos_symb_hc_count_full`/`pos_hc_substvalid_count_full` 共同构成 full 轨口径的分子/分母基数 (见 `runner.py` 方法 F 段), 且 full 轨结果还驱动了面板层面的 `dummy_no_positive_news` 等派生哑变量的构造依据 (虽然该哑变量本身取用的是裸 `pos_count_full` 而非 hc 口径, 但两者共享同一 full 轨行宇宙前提)。作为三轨并列稳健性测度之一, `pos_hc_count_full` 与 `pos_hc_count_ctx`/`pos_hc_count_ss` 之间禁止混入同一 over-identified Hansen J 识别框架。

## VAR: pos_hc_count_ss

【变体差分】
`pos_hc_count_ss` 是本家族在 ss (银行∧金科同句) 轨道上的高置信度正面报道计数, 是三轨中文本范围最窄、判定条件最严格的一支。扫描文本为标题+目标银行与金科关键词同句共现 (±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认取值为 1) 的片段, 由 stage 14 物化为 `content_ss` 列 (同样以 `prepend_title` 方式拼接标题)。`_is_pos_hc_ss` 标记的生成逻辑与 full/ctx 两轨对称: 要求 (a) 三家 LLM 在 ss 轨文本上的多数投票判正 (`is_positive_ss==1`), 且 (b) 三家 LLM 在 ss 轨文本上的内部一致率 `llm_agreement_rate_ss` 不低于 `HC_AGREEMENT_THRESHOLD`, 同样全程不涉及词典/BERT 口径, 聚合公式为 `agg['pos_hc_count_ss'] = ('_is_pos_hc_ss', 'sum')`。ss 轨最重要的差分语义是其回退机制: 当某篇文章不存在银行与金科关键词的同句共现时 (即无法定位到严格同句窗口), `content_ss` 按 CLAUDE.md 铁律回退为全文 body 全文, 对应的 `ss_is_fallback` 标记置为 True, 但该回退不改变 `_is_pos_hc_ss` 的计算逻辑本身——回退后的高置信度判定照常基于回退文本 (即等同于 full 轨文本) 进行, 计数照常纳入求和, 与 ctx 轨"无银行∧金科共现窗口时同样回退全文"的语义完全镜像。ss 轨的判定不对称口径值得注意: 银行侧的关键词匹配采用"否定+短名过滤"规则, 金科侧则采用裸 AC 自动机 (1506 词典) 匹配, 这一不对称性继承自项目情感测度体系的统一约定, 而非本家族独有。由于 ss 轨窗口最窄, 在未回退的正常情形下 `pos_hc_count_ss` 通常不大于 `pos_hc_count_ctx`, 后者又不大于 `pos_hc_count_full`; 但回退发生时三轨在个别文章上可能重新趋同。ss 轨的行宇宙同样继承 full-only 留篇门控, 是 full 留篇集合上的条件测度轨, 与 full/ctx 两轨互为稳健性、各自 just-identified、禁止混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
<!-- rendered-citations:end -->
