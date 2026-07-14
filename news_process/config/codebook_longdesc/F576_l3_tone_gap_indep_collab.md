---
family_id: F576
columns:
- tone_gap_indep_collab
unit: 语调差分得分 (连续, 理论范围约 [-2,2], 实践中集中于 [-1,1]; bank-year 面板层级)
formula: 'tone_gap_indep_collab = llm_vote_tone_indep_full − llm_vote_tone_collab_full, 仅当 n_articles_indep≥5 且 n_articles_collab≥5 时取值, 否则记为缺失'
producer: pipeline\panel\encode.py
upstream:
- llm_vote_tone_indep_full
- llm_vote_tone_collab_full
- n_articles_indep
- n_articles_collab
- n_articles_llm_valid
citations:
- doi: "10.1111/jpim.12710"
  type: journal
  authors: "Zhang, H., Ma, Z., Liang, X., & Garrett, T. C."
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: "Journal of Product Innovation Management"
  vol: "41"
  issue: "4"
  pages_or_artno: "793-815"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J."
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: "The Accounting Review"
  vol: "98"
  issue: "7"
  pages_or_artno: "315-345"
- doi: "10.1016/j.techfore.2026.124581"
  type: journal
  authors: "Dehghani, M. A., Brauneis, A., & Karavidas, D."
  year: 2026
  title: "Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions"
  venue: "Technological Forecasting and Social Change"
  vol: "226"
  pages_or_artno: "124581"
- doi: "10.1002/smj.507"
  type: journal
  authors: "Laursen, K., & Salter, A."
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: "Strategic Management Journal"
  vol: "27"
  issue: "2"
  pages_or_artno: "131-150"
new_dois: []
---

## CORE

【构念与来源】
tone_gap_indep_collab 度量的是同一家银行、同一年度内, 媒体报道呈现出的"自主研发"叙事口吻与"外部协同"叙事口吻之间的情感落差, 属 P5 (bank_fintech_collab, Chesbrough 开放式创新框架) provisional 论文条线下的派生诊断指标, 而非该论文的主处理变量本身。P5 主线区分银行金融科技相关报道的两种创新模式: 一种是银行完全依靠内部力量自主研发金融科技能力 (indep, 对应开放式创新文献中的"封闭式创新"一端), 另一种是银行通过与外部金融科技公司结盟、并购、参股、联合实验室等方式实现协同创新 (collab, 对应"开放式创新"一端)。这一二分类判据来自 stage 21 三家 LLM (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 经 yunwu、deepseek-v4-flash 直连 api.deepseek.com) 对每篇留篇报道的 innovation_collab_mode 维度多数投票分类, 与情感判定共用同一套 verified 门控与缓存键 (prompt_version='v8-2026-05-17', temperature=0.0)。tone_gap_indep_collab 本身并不重新判定情感, 而是在 encode.py 面板聚合阶段, 对已经按 collab_mode 分组聚合出的两条语调子测度做算术相减: 自主研发子样本的 headline 语调均值减去外部协同子样本的 headline 语调均值。正值意味着该银行在样本期内, 媒体谈及其自主研发布局时口吻更为乐观, 而谈及外部协同合作时口吻相对谨慎或偏负面; 负值则相反, 意味着协同叙事比自主叙事获得了更正面的媒体评价。这一构念定位与家族命名中的 gap 后缀一致——它衡量的是"落差", 而非任一单一模式下的绝对语调水平, 因此不能脱离 indep_frac / collab_frac (两个模式各自占该银行当年金融科技报道的比例) 单独解读: 落差数值的经济含义依赖于两个子样本各自的报道基数与代表性。

【方法学与计算】
计算链条起自 stage 21 tone_llms 的三家 LLM 情感投票与 innovation_collab_mode 分类, 经 encode.py 的 cm_agg 聚合块按 (target_bank, year) 分组、按 collab_mode ∈ {indep, collab} 拆分后, 分别算出 llm_vote_tone_indep_full 与 llm_vote_tone_collab_full 两条 headline 情感子测度 (headline 口径固定为 full 轨, 与 2026-06-29 起全线切换的 full-only 留篇门控保持一致: 是否判定为"一篇银行金融科技报道"只看 llm_verified_full==True, ctx/ss 是 conditional-on-full 的稳健性轨道而非独立留篇集合)。在此基础上, encode.py 引入了 fix(encode-02) 补丁引入的最小样本量守门: 只有当该银行-年度内 n_articles_indep≥5 且 n_articles_collab≥5 同时成立时, tone_gap_indep_collab 才被赋予实际数值 (panel[...].where(_indep_collab_qual, np.nan)), 否则整个 bank-year 观测被记为缺失。这一守门逻辑与家族 F575 (tone_gap_sub_symb) 完全镜像, 都是为了防止极小样本 (例如某银行某年仅有 1-2 篇协同类报道) 导致的均值估计噪声被误读为系统性语调落差。门控之后, encode.py 还会执行一段纯日志、golden-safe 的分布统计 (n_qual、占全体 bank-year 比例、均值、标准差、中位数), 该统计仅供运行时监控与审计留痕, 不参与任何下游列计算, 也不会写回面板本身。此外, 与 n_articles_indep / n_articles_collab 相关的恒等式校验遵循 R6 规范: 由于上游 collab_mode 判定本身可能因 LLM 分类失败而产生 NaN, 面板层面只保证 n_articles ≥ n_articles_indep + n_articles_collab 的逻辑必然性, 差额由 n_articles_cell_NA_full 兜底追踪, 不强制严格等式。

【文献定位】
本指标的构念根基是开放式创新理论对"自建能力"与"外部协同"两种创新模式的经典二分, 其奠基性框架见 Chesbrough (2003) 与 Laursen & Salter (2006) 关于企业开放边界选择如何影响创新绩效的论证; Zhang, Ma, Liang & Garrett (2024) 在 Journal of Product Innovation Management 发表的近 20 年开放式创新元分析进一步系统化了"开放度—绩效"关系的调节因素框架, 为本指标将开放度维度 (indep vs collab) 与外部媒体情感表征相勾连提供了理论支点。将媒体语调差异用作银行创新模式选择之市场认知代理的做法, 呼应了金融文本情感分析中"事件驱动情感测度"的传统, 例如 Holzman, Miller & Twedt (2023) 在 The Accounting Review 关于媒体情感与季度盈余披露间约束关系的研究表明, 媒体语调本身携带独立于基本面之外的市场解读信号。在金融科技情境下, Dehghani, Brauneis & Karavidas (2026) 对金融机构专利策略与开放式创新实践的最新实证进一步确认, 银行在自主研发与外部合作之间的策略选择存在系统性异质性, 这一异质性正是 tone_gap_indep_collab 试图从媒体叙事侧捕捉的现象。需要强调的是, 本指标是 P5 论文的辅助诊断/描述性测度, 用以刻画媒体如何差异化评价两种创新模式, 而非该论文因果识别策略中的处理变量或工具变量; P5 主线处理变量另有专门定义 (详见 papers/bank_fintech_collab 模块), 使用者不应将 tone_gap_indep_collab 直接代入回归右侧作为核心自变量, 更适合的用途是作为稳健性描述、异质性分组依据或论文正文中"叙事差距"现象的可视化材料。

## VAR: tone_gap_indep_collab

【变体差分】
tone_gap_indep_collab 是本家族在 standard tier 下唯一的列, 其精确语义由三个维度的选择共同锁定, 使用者在引用该列前应逐一核对。第一, 轨道选择: 该列固定取 headline full 轨 (llm_vote_tone_indep_full 与 llm_vote_tone_collab_full), 而非 ctx 或 ss 轨。按 CLAUDE.md 三轨铁律, full/ctx/ss 三轨互为稳健性、各自 just-identified 并排、禁止混入同一 over-identified Hansen J 估计; encode.py 在 ctx 对角线追加块与 ss 对角线追加块中确实各自派生出了对应的差分列 tone_gap_indep_collab_cm_ctx 与 tone_gap_indep_collab_cm_ss (命名带 _cm 中缀以区分于本列所在的 full 轨命名空间), 二者分别以 llm_vote_tone_indep_cm_ctx/_cm_ss 与 llm_vote_tone_collab_cm_ctx/_cm_ss 相减构造, 并各自独立配上与本列同构的 min-n≥5 双门槛守卫 (n_articles_indep_cm_{ctx,ss}≥5 且 n_articles_collab_cm_{ctx,ss}≥5 同时成立才取值, fix(completeness-05) 补齐该守门, 否则单篇 cell 的伪差距会混入 ctx/ss 轨机制回归), 因此本家族测度在三轨上确有并排的稳健性版本, 并非需要研究者自行从零构造; 三者互为稳健性、不分主次, 各自 just-identified, 不应混入同一 over-identified Hansen J。使用者若要引用 ctx/ss 版本, 应取用 tone_gap_indep_collab_cm_ctx / tone_gap_indep_collab_cm_ss 两列 (不在本家族列清单内, 由各自所属家族的 codebook 条目单独描述), 而不是误以为该差分只存在于 full 轨。第二, LLM 情感来源选择: llm_vote_tone_{indep,collab}_full 使用的是三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票后的共识语调 llm_vote_tone, 而非任一单一厂商的 per-model 语调 (如 gpt54nano_tone_full 或 deepseekv4_tone_full)。三家 per-model 语调彼此互为稳健性、不分主次, 但本列不提供 per-model 版本的语调落差, 若要做跨模型稳健性检验须自行以 per-model 列重新构造对应差分, 并遵守"各模型各自 just-identified 并排、禁混同一 Hansen J"的铁律。第三, 最小样本量守门与缺失语义: 该列并非对全体 bank-year 观测都有定义, 只有当 n_articles_indep≥5 且 n_articles_collab≥5 同时满足时才取实际数值, 否则记为 NaN; 这一 NaN 不是"数据缺失", 而是"该银行-年度内至少一种创新模式的报道量不足以支撑稳健的语调均值估计", 使用者在面板回归中若不加区分地对该列做插补或整体样本量核算, 极易低估真实样本损耗。在盘上 T=2 (2017-2018, 110 家银行) 开发规模数据上, 由于金融科技报道本身即属稀疏事件、按 collab_mode 二次拆分后单元更稀疏, 满足 min-n≥5 双门槛的 bank-year 数量通常极为有限 (encode.py 日志明确记录该情形为"T=2 小样常态"), 该列的经验有效值密度须以生产语料 T=18 (2007-2024, 约 1700 万条原始报道过滤后的口径) 重新评估, 不应以本机开发库上的稀疏性外推为最终结论。

<!-- rendered-citations:begin -->
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
<!-- rendered-citations:end -->
