---
family_id: F354
columns:
- jiang_2021_pos_substvalid_count_ctx
- jiang_2021_pos_substvalid_count_full
- jiang_2021_pos_substvalid_count_ss
unit: 篇数/计数 (count)
formula: 'bank-year 计数 = Σ over 该银行-年留篇集文章的篇章级指示 `_svd_jiang_2021_pos{track}` = (jiang_2021_score{track} > 0) & (innovation_substantiveness_full ∈ {"实质性","象征性"}); 即"jiang_2021 词典打分为正 ∧ LLM 已成功判出该文章 W&Z(1994/1998) 实质性/象征性创新话语分类"这一同域指示的按银行-年求和, 是 washing_ratio_jiang_2021{track} 洗稿率的同域分母输入, 与"实词有效性/分词边界校验"无关'
producer: pipeline\panel\runner.py (`_svd_jiang_2021_pos{track}` 篇章级指示构造, 步骤 7h 前置; `_pool_svd_substvalid_counts` 步骤5 按银行-年 groupby.sum 聚合为本列)
upstream:
- 14_materialize_ctx (content_full/content_ctx/content_ss 三轨文本物化)
- 21_tone_llms (llm_verified_full 留篇门控, full-only; innovation_substantiveness_full 亦源自 stage 21 LLM 分类维度)
- 22_tone_words (jiang_2021_score{track} 词典打分主计算, 本列的阳性判据来源)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., McDonald, B.
  year: 2011
  title: When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., Yan, Z.
  year: 2021
  title: A New Chinese Financial Sentiment Dictionary for Textual Analysis in Accounting and Finance
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列 (`jiang_2021_pos_substvalid_count_{full,ctx,ss}`) 度量的不是词典命中的实词校验计数, 而是"洗稿率" (washing ratio) 计算所需的同域分母指示计数: 某银行-年内, 有多少篇文章同时满足①姜富伟、孟令超、唐国豪 (2021,《经济学(季刊)》) 构建的中文金融情感词典 jiang_2021 对该篇文章打出正面分 (`jiang_2021_score{track} > 0`), ②stage 21 LLM 已成功把该篇文章的创新话语判定为 W&Z (1994/1998) 意义上的"实质性" (substantive) 或"象征性" (symbolic) 之一 (`innovation_substantiveness_full ∈ {"实质性","象征性"}`, 判定失败/缺标则被排除)。这一"正面 ∧ 已测量" (positive-and-measured) 交集的按银行-年求和即为本列取值, 计算发生在 `pipeline/panel/runner.py` 面板构建阶段而非词典打分阶段。

本列的直接下游用途是 `washing_ratio_jiang_2021{track}` (洗稿率) 的分母。洗稿率的构念是: 在词典判为正面报道的文章中, 有多大比例其创新话语实为"象征性" (即企业以金科合作/创新为名做符号化公关宣传, 而非真实推进实质业务) —— 这是本项目呼应 Westphal & Zajac (1994, 1998) "象征性管理" (symbolic management) 理论, 检验金融机构与金融科技合作报道中"言行是否一致"的核心诊断指标之一。若洗稿率分母简单取"词典判正面"的全部文章数 (物理计数), 则当 LLM 对部分文章的实质性/象征性判定失败时, 这些文章既进不了分子 (无法归入象征性) 也不该计入分母——否则 LLM 分类失败率越高, 洗稿率会被系统性稀释, 制造"洗稿现象被低估"的假象。`_svd_jiang_2021_pos{track}` 正是为修正这一偏差而设计的"同域" (same-domain) 分母指示: 只数 LLM 确已给出实质性/象征性判定的那批正面文章。

【方法学与计算】
面板构建阶段 (`pipeline/panel/runner.py`) 先构造 `_subst_measured` 布尔掩码: 取 `innovation_substantiveness_full` (stage 21 LLM 对该篇文章创新话语实质性/象征性的分类结果, 固定读 full 轨, 不逐轨重复判定) 字符串化后是否落入 `_SUBST_VALID_LABELS = ('实质性', '象征性')` 二值集合内; 未成功分类 (缺标/其他类别) 的文章该掩码为 False。随后对三轨 (full/ctx/ss) 各自的 jiang_2021 词典打分列 `jiang_2021_score{track}` (stage 22 `tone_words.py` 产出) 取阳性 (`> 0`), 与 `_subst_measured` 做逻辑与, 得到篇章级指示 `_svd_jiang_2021_pos{track}`。注意: 三轨之间变化的只是词典打分的阳性判据 (`jiang_2021_score{track}`), 而 `_subst_measured` 本身恒取 full 轨的实质性/象征性判定, 不随 track 变化——这是留篇门控 full-only 铁律 (2026-06-29 起) 在洗稿率分母构造上的自然延伸: 是否一篇文章"可被判定实质性/象征性"是 full-only 的分类结果, ctx/ss 轨只贡献词典打分方向, 不重新判定实质性归类。

篇章级指示随后在步骤5 `aggregate_panel` 内由 `_pool_svd_substvalid_counts` 按 (target_bank, year) 分组求和聚合, 输出即为本家族三列 (列名由 `_svd_jiang_2021_pos{track}` 重命名映射为 `jiang_2021_pos_substvalid_count{track}`)。聚合结果在步骤 7h 被 `_svd_denom` 读取, 作为 `washing_ratio_jiang_2021{track}` 的分母 (分子为词典判正面且 LLM 判为"象征性"的篇数, `_is_dict_pos_symb`/`_is_jiang_2021_pos_symb` 一族); 若该同域分母缺失 (旧 schema 未生成), 洗稿率计算才回退到物理分母 (词典判正面的全部篇数) 并发出警告。因此本列并非方法论透明度的旁路诊断列, 而是洗稿率这一活跃回归可用衍生指标计算链条上的必经中间产物。三轨 (full/ctx/ss) 各自的本列各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J; ss 轨在无银行∧金科同句共现时 `content_ss` 回退为全文 body (镜像 ctx 回退语义), 对应 `ss_is_fallback` 标记, 与 `n_articles` 分母口径共享。留篇门控严格 full-only: 是否判定为"一篇有效银行金科报道"只看 `llm_verified_full == True`, ctx/ss 轨的本列取值在 full 留篇集这一行宇宙子集之上按轨计算 (conditional-on-full), 而非独立样本。

本家族与同族姊妹诊断列 `jiang_2021_pos_count`/`jiang_2021_neg_count` (全部正/负词典命中篇数, 不做实质性同域限定) 在构念上互不重叠: 后者是词典打分器的原始正负计数, 前者是洗稿率计算专用的分母子集计数, 二者不构成可加分解关系。

【文献定位】
词典构建方法学依据姜富伟等 (2021) 对中文财经文本情绪测度的原始构建, 该文献是本项目中文金融文本情感词典消融组六部词典之一的锚点。象征性管理理论构念 (本列作分母服务的洗稿率所度量的"言行不一致") 溯源自组织理论文献对企业象征性行为 (symbolic action) 与实质性行为 (substantive action) 的经典区分——该区分在金融文本情绪测度语境下的应用需要文本情感词典与内容分类结果的交叉验证, 这正是本列存在的方法论必要性。分母同域校正的统计逻辑呼应 Loughran & McDonald (2011, *The Journal of Finance*) 关于财务文本情感度量须警惕"表面测量与真实构念错配"导致系统性偏误的原则——该文强调英文 10-K 情感词典须结合语境层面校验以避免伪信号, 本列在中文语境下的对应做法是: 分母只纳入 LLM 分类确已成功的那批文章, 以避免分类失败率差异污染洗稿率的跨银行-年可比性。词典消融族的整体设计 (多词典并排互稳健) 亦参照 Bian, Jia, Li & Yan (2021) 关于中文金融情感词典跨来源构建差异对下游测度稳健性影响的讨论, jiang_2021 与家族内其余词典各自产生独立的同域分母计数, 供各自的洗稿率测度并排比较。

## VAR: jiang_2021_pos_substvalid_count_ctx

【变体差分】
本列为 ctx 轨 (实体窗口轨) 的洗稿率同域分母指示计数: 阳性判据取 `jiang_2021_score_ctx > 0` (词典对 `content_ctx`——标题 + 目标银行实体窗口内正文片段, stage 14 物化、`prepend_title` 拼接——的打分), 与 `_subst_measured` (恒取 full 轨的 `innovation_substantiveness_full` 实质性/象征性判定, 不逐轨重复判定) 逻辑与后按银行-年求和。本列与 full/ss 轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J。行宇宙口径遵循 2026-06-29 起的 full-only 留篇门控: 是否计入面板的"一篇文章"判定完全依赖 `llm_verified_full`, ctx 轨仅在该留篇子集内取值, 属 conditional-on-full 的稳健性测度轨, 不单独扩展样本行宇宙。若目标银行在该篇文章中缺乏可界定的实体窗口, `content_ctx` 依 stage 14 物化规则退化处理, 词典打分及本列阳性判据相应可能取 0, 不代表数据缺失。

本列与 full 轨的构念差异仅体现在阳性判据的文本输入域上 (词典打分作用于 ctx 窗口 vs 全文), `_subst_measured` 这一"实质性/象征性已判定"掩码在 ctx/full/ss 三轨间完全相同 (均读 `innovation_substantiveness_full`)。因此本列度量的是"银行实体窗口内 jiang_2021 词典判正面, 且该篇文章已被 LLM 成功分类实质性/象征性"的篇数——用作 `washing_ratio_jiang_2021_ctx` 的分母, 检验"洗稿率"这一构念在收紧到银行实体语境窗口后是否与 full 轨定性一致。审计时若发现 ctx 轨本列远小于 full 轨, 通常提示该篇文章正面表述集中在与目标银行实体距离较远的段落, 值得结合 `target_bank_in_title` 等标题层信号交叉核验, 而非提示实质性判定本身有差异 (后者三轨恒同)。

## VAR: jiang_2021_pos_substvalid_count_full

【变体差分】
本列为 full 轨的洗稿率同域分母指示计数: 阳性判据取 `jiang_2021_score_full > 0` (词典对标题 + 全文正文 `content_full` 的打分), 与 `_subst_measured` 逻辑与后按银行-年求和, 是 `washing_ratio_jiang_2021_full` 的分母。full 轨同时是本项目留篇门控的唯一裁决轨——`llm_verified_full == True` 是文章是否计入面板行宇宙的唯一判据 (2026-06-29 起 full-only 铁律), ctx/ss 轨均为该留篇集之上的条件测度; 且 `_subst_measured` 本身恒读 `innovation_substantiveness_full` (full 轨的 LLM 实质性/象征性分类结果), 是三轨共享的固定分类来源, 不随 track 变化。本列与 ctx/ss 轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J。

full 轨不受实体窗口/同句半径约束, 词典打分覆盖全文, 因而本列 full 轨取值通常是三轨中同域分母计数的上界参照 (但非严格数学不等式, 因各轨词典打分独立计算)。该值同时是 `_svd_denom` 在洗稿率计算 (步骤 7h) 中的默认分母来源, 若面板 schema 缺失该列, 计算逻辑回退到"词典判正面的物理计数"作分母并发出警告 (二者数值不同: 物理计数不排除实质性判定失败的文章, 会稀释洗稿率); full 轨作为唯一留篇裁决轨, 其本列同域分母计数的完整性直接决定该银行-年洗稿率测度是否可信。审计层面, 研究者可将本列 full 轨取值与同族 `jiang_2021_pos_count_full` (词典正面命中的物理计数, 不做实质性同域限定) 并列查看: 二者之差即为"词典判正面但 LLM 未能成功分类实质性/象征性"的篇数, 该差值越大, 说明该银行-年的洗稿率测度受分类失败的稀释风险越高, 应结合分类成功率一并解读, 不宜孤立看待洗稿率数值本身。

## VAR: jiang_2021_pos_substvalid_count_ss

【变体差分】
本列为 ss 轨 (同句轨) 的洗稿率同域分母指示计数: 阳性判据取 `jiang_2021_score_ss > 0` (词典对 `content_ss`——标题 + 目标银行∧金科词严格同句共现窗口, 半径参数见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1, 与 stage 13 `cooccurrence_filter.sentence_radius` 是不同配置键——的打分), 与恒取 full 轨的 `_subst_measured` 逻辑与后按银行-年求和, 是 `washing_ratio_jiang_2021_ss` 的分母。ss 轨语义镜像 ctx 轨的回退设计: 若该篇文章中不存在银行∧金科词的同句共现, `content_ss` 回退为全文 body, 并置位 `ss_is_fallback=True`, 与 `n_articles` 分母口径共享 (回退发生时 ss 轨词典打分实质上退化为 full 轨的等价扫描, 但仍受 full-only 留篇门控约束, 不改变行宇宙)。本列与 full/ctx 轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J; 三轨并排设计的目的是检验洗稿率这一构念在不同文本粒度下是否保持定性一致, 而非构造单一"更优"测度。

ss 轨是三轨中对"归因精确度"要求最严格的一支: 只有当银行实体词与金科词在同一自然句 (由标题第 0 句起算的逐句切分, 复用 `entity_context.map_bank_sentence_positions` 原语) 内共现时, 才会被纳入非回退窗口的词典打分。非回退情形下本列取值对应"银行-金科议题同句正面表述, 且该文已被判定实质性/象征性"这一最细粒度组合。回退发生的频率与 stage 13 共现硬过滤的生产口径 (`sentence_radius=1`, `match_in_title=true`) 高度相关: 已通过 stage 13 硬过滤保留的文章大概率存在某种邻近共现, 但"邻近 (±1 句)"与"严格同句 (半径 0)"是两个不同判据, 仍有相当比例文章在 ss 轨触发回退。审计本列及其下游洗稿率取值时应结合 `ss_is_fallback` 指示列, 区分"真实同句窗口内的正面命中"与"回退到全文口径的正面命中", 二者构念内涵不同, 不应不加区分地直接比较数值大小。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Loughran, T., McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Bian, S., Jia, D., Li, F., Yan, Z. (2021). A New Chinese Financial Sentiment Dictionary for Textual Analysis in Accounting and Finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
