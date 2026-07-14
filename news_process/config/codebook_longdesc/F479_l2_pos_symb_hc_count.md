---
family_id: F479
columns:
- pos_symb_hc_count_ctx
- pos_symb_hc_count_full
- pos_symb_hc_count_ss
unit: 篇数/计数 (count)
formula: 'pos_symb_hc_count{track} = sum(_is_pos_symb_hc{track}), 逐篇布尔指示量在 bank-year 层聚合求和; {track} ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\encode.py (聚合注册, L1097-L1127) ; pipeline\panel\runner.py (下游洗稿率变体 F 消费, L2286-L2294)
upstream: []
citations:
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: Cheap talk and cherry-picking; What ClimateBert has to say on corporate climate risk disclosures
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
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
`pos_symb_hc_count` 属于本仓「洗稿率 (washing ratio)」测度体系中的方法 F 分支——"高置信度子样本 (high-confidence subsample)" 通道的分子计数列。它统计的不是某篇报道是否正面, 而是在已被判定为高置信度正面的报道子集中, 有多少篇同时携带了"象征性 (symbolic)"正面语言标记, 即措辞正面但缺乏可验证的实质性信息支撑。该构念直接承袭企业传播文献中"实质性 vs 象征性"沟通二分框架的核心洞见: 组织行为与战略文献早已指出, 企业对外沟通存在言辞层面的"廉价谈话 (cheap talk)"与行动/事实层面的实质性披露之间的系统性缺口 (Bingler, Kraus, Leippold & Webersinke, 2022, *Finance Research Letters*)。该文献将这一现象概括为"cheap talk and cherry-picking"——企业倾向于用高频出现的正面措辞来装点门面, 而非用可核查的量化指标或具体行动来支撑其披露主张。本家族的洗稿率测度体系正是把这一诊断逻辑从企业气候披露语境迁移到中国银行业金融科技新闻报道语境: 一篇报道若被标记为"正面且象征性 (pos_symb)", 意味着其情感取向的载体主要是形容词、评价性短语等无法被事实核查的修辞成分, 而非包含具体数字、项目名称、监管批文等可验证细节的实质性正面内容。

洗稿率测度体系共设六套并行方法 (A 至 F, 详见 `pipeline/panel/runner.py` 的 `wr_variants` 台账): A 是 LLM 投票整体判定, A2 是三家 LLM 单模型判定, D/D2 是词典整体/单词典判定, E/E2 是 BERT 均值/单模型判定, F 即本家族所属的"高置信度子样本"通道。方法 F 的设计动机是控制测量误差: 当某篇报道的正面/象征性判定在多种方法或多个评分维度上高度一致时 (即"高置信度"), 才将其计入 `pos_hc_count`/`pos_symb_hc_count` 分子分母, 从而得到一个对单一分类器噪声更稳健的洗稿率子样本估计, 与方法 A/A2/D/D2/E/E2 构成互为稳健性的并列梯子, 而非相互替代或加总的关系。`pos_symb_hc_count` 是这套方法 F 洗稿率公式 `washing_ratio_hc = pos_symb_hc_count / pos_hc_substvalid_count` (经安全分母函数 `_svd_denom` 处理零值/极小分母) 的分子; 分母优先取 `pos_hc_substvalid_count` (即高置信度子样本内、且实质性判定已成功测量的正面报道子集, 阳性∧实质性已测量的双重条件计数), 仅当该同域分母列因旧 schema 缺失时才回退到 `pos_hc_count` (高置信度正面报道物理总数, 不筛实质性是否已测量) 并发出告警, 二者口径并不等价——`pos_hc_count` 是本家族之外的另一列, 计的是全部高置信度正面篇数, 而 `pos_hc_substvalid_count` 排除了实质性判定缺失 (NaN) 的部分篇目, 使分子分母在"是否已测量实质性"这一维度上同域。比值衡量的是: 在高置信度正面且实质性判定有效的报道中, "只谈修辞不谈实质"的报道占多大比例。

【方法学与计算】
计算链条起点在文章级篇章表 (`21_tone_llms.parquet` 等上游情感产出经合并后的宽表): 每篇文章、每条轨道下均有一个布尔指示列 `_is_pos_symb_hc{track}`, 由上游情感模块综合多源判定 (LLM 投票 + 高置信度筛选逻辑) 后打上标记, 值为 1 表示"该篇文章在此轨道下被判定为高置信度正面且带有象征性语言特征", 否则为 0/NaN。`encode.py` 在 bank-year 聚合阶段 (第 K 组 "洗稿率聚合: 多方法 × 三轨") 对该指示列执行 `groupby(...).sum()`, 得到三条轨道各自的 `pos_symb_hc_count{track}` 列, 单位是纯计数 (count), 取值为非负整数或（因上游可能含 NaN 经 pandas nullable dtype 处理而呈现为）浮点计数。该列本身不做任何归一化或除法, 是后续 `washing_ratio_hc{track}` 比率型指标的原始分子输入; 除以对应的高置信度正面篇数分母后才具备可比的"比例"含义, 单独看该计数列则直接反映样本银行-年度观测窗口内高置信度象征性正面报道的绝对频次, 会随该行 `n_articles` 报道基数规模变化而变化, 使用者若要做跨行比较应优先使用其派生比率 `washing_ratio_hc{track}` 而非原始计数本身。

三条轨道 `_full`/`_ctx`/`_ss` 对应本仓统一的三轨文本架构: `_full` 轨用标题+全文正文作为情感判定与后续象征性标记的文本输入; `_ctx` 轨用标题+目标实体窗口截取文本; `_ss` 轨用标题+银行∧金科同句 (±N 句窗口, 默认 N=1) 截取文本, 若某篇文章不存在银行与金科词的同句共现, 则该篇的 `_ss` 轨回退为镜像 `_ctx` 的全文语义 (即 `content_ss` 取全文 body, 并标记 `ss_is_fallback=True`, 与 `_ctx` 共享分母口径)。三条轨道下的 `pos_symb_hc_count` 各自独立计算、各自 just-identified, 互为稳健性并列关系, 不分主次, 严禁在同一处 over-identified 工具变量检验 (如 Hansen J 过度识别检验) 中把三轨的同名派生列混合作为多个工具同时纳入——这是本仓贯穿所有多轨/多梯子测度族的铁律。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否被判定为"一篇有效的银行-金科报道"只看 `llm_verified_full` 是否为真, `_ctx`/`_ss` 轨道的计数与比率是在该 full-only 留篇集合子集内的条件测度/稳健性轨, 而非独立扩样的平行样本。

【文献定位】
本家族的方法学脉络有两条互补来源。其一是 Bingler et al. (2022, *Finance Research Letters*; 2024, *Journal of Banking & Finance*) 关于企业气候披露中"cheap talk"与"cherry-picking"的系列研究, 二者共同构成了"言辞正面 vs 实质支撑"二分识别框架的直接理论来源, `pos_symb` 这一命名与判定逻辑正是对该框架的操作化迁移: 从企业自我气候披露的实质性核查, 迁移到新闻报道中金融科技相关正面措辞的实质性核查; 该系列研究同时强调对文本样本按信息可信度分层处理的必要性, 为方法 F "高置信度子样本" 这一分层过滤设计思路提供了直接的方法学依据——低置信度、易受分类器噪声干扰的样本应被识别并单独处理, 而非与高置信度样本混为一谈。其二是 Li (2008, *Journal of Accounting and Economics*) 关于年报可读性与当期盈余、盈余持续性关系的研究, 该文示范了如何用篇章级文本特征构造计数型指标并通过恰当归一化 (而非直接比较绝对计数) 获得跨观测单元可比的测度, 为洗稿率测度体系里以计数配合安全分母 (`_svd_denom`) 构造比率型指标的设计提供了方法论上的参照——即"绝对计数需要通过合适的分母归一化才能获得跨观测单元可比性"这一原则同样适用于本列, 也呼应了本家族分子 `pos_symb_hc_count` 必须与同域分母 `pos_hc_substvalid_count` 配对使用, 而非孤立解读绝对频次的设计取向。

## VAR: pos_symb_hc_count_full

【变体差分】
本列是三轨中的 `_full` 轨版本, 判定所用文本输入为该篇报道的标题+全文正文 (未做实体窗口截取或同句共现过滤), 对应上游 `_is_pos_symb_hc_full` 指示列在 bank-year 层的求和。`_full` 轨是本仓留篇门控 (2026-06-29 起) 的唯一判据来源: 一篇报道是否计入某银行-年度的有效样本, 完全由该篇在 `_full` 轨的 `llm_verified_full` 判定决定, 因此 `pos_symb_hc_count_full` 天然覆盖该银行-年度全部留篇集合, 不存在因窗口截取或同句限定而产生的样本收缩。作为三条并列轨道之一, 它与 `_ctx`/`_ss` 轨互为稳健性检验, 不构成"更优先"的默认选择——但在留篇门控意义上, `_full` 轨是唯一决定"这篇文章算不算数"的轨道, 其它两轨的计数只在 `_full` 判定为有效留篇的子集内条件成立。

在洗稿率方法 F 的分子分母配对关系中, `pos_symb_hc_count_full` 需与同轨的 `pos_hc_substvalid_count_full` (高置信度∧实质性判定已测量的正面篇数, 经 `_svd_denom` 优先选取的同域分母; 该列缺失时才回退到未筛实质性测量状态的 `pos_hc_count_full`) 配对使用才具备比率含义; 单独使用该计数列时应结合同一行的 `n_articles_full` (full 轨报道基数) 一并解读, 避免把绝对频次差异误读为比例差异。由于 `_full` 轨覆盖标题+全文正文, 该列相较 `_ctx`/`_ss` 通常呈现更高或至少持平的绝对计数水平, 是三轨梯子中样本覆盖最完整的一支。

## VAR: pos_symb_hc_count_ctx

【变体差分】
本列是三轨中的 `_ctx` 轨版本, 判定所用文本输入为标题+目标银行实体窗口内截取的文本片段 (而非全文), 对应上游 `_is_pos_symb_hc_ctx` 指示列在 bank-year 层的求和。相比 `_full` 轨, `_ctx` 轨的文本输入更聚焦于目标银行实体周边的语境, 意在过滤掉一篇长文中与目标银行无关的段落对情感/象征性判定的干扰, 从而检验"高置信度象征性正面"这一构念在窗口化文本上是否依然稳健。由于留篇门控为 full-only, `_ctx` 轨的计数是在 `llm_verified_full` 为真的留篇子集内的条件测度, 其绝对水平通常会低于或等于 `_full` 轨对应值 (因窗口截取可能使部分原本判定为正面/象征性的信号在局部窗口内不再成立), 使用者不应将 `_ctx` 与 `_full` 直接相减解读为"窗口效应大小"而不控制样本口径差异。

`_ctx` 轨的实体窗口截取逻辑在 stage 14 (`ctx_materializer`) 物化为 `content_ctx` 列 (标题前置, `prepend_title`), 供下游 stage 21 情感判定与本家族的象征性标记复用, 因此 `pos_symb_hc_count_ctx` 与同轨的其它情感衍生列 (如 `llm_vote_tone_ctx`) 共享同一份物化文本, 保证测度口径的内部一致性。当某银行-年度的报道普遍篇幅较长且涉及多家实体时, `_ctx` 轨相较 `_full` 轨更能剥离无关实体的信息噪声, 是判断"高置信度象征性正面"结论是否受长文本稀释影响的重要稳健性检验轨道, 应与 `_full`/`_ss` 两轨结果并列报告而非取代。

## VAR: pos_symb_hc_count_ss

【变体差分】
本列是三轨中的 `_ss` 轨版本, 判定所用文本输入为标题+银行∧金科关键词同句共现 (±1 句窗口, `config/filtering.yaml::context_window.ss_sentence_radius`) 截取的文本片段, 对应上游 `_is_pos_symb_hc_ss` 指示列在 bank-year 层的求和。`_ss` 轨在语义上镜像 `_ctx` 轨的回退规则: 若某篇报道内不存在银行与金科词汇的同句 (或窗口内) 共现, 则该篇的 `_ss` 文本回退为全文 body 并标记为 fallback, 与 `_ctx` 共享同一 `n_articles` 分母口径, 而非因无同句共现就被排除出计数。`_ss` 轨是三条轨道中文本窗口最窄、判据最严格的一支, 用于检验"高置信度象征性正面"这一判定结果在最贴近银行-金科共现语境的文本片段上是否依然成立, 与 `_full`/`_ctx` 共同构成三轨并列稳健性梯子, 三者各自 just-identified、互不替代, 亦不得混入同一过度识别检验。

需特别注意的是, `_ss` 与 `_ctx` 所用的判据原语并不相同: `_ss` 的同句共现判据来自 `entity_context.py` 中严格意义上的同句抽取函数, 与 stage 13 硬过滤所用的 ±1 句窗口共现判据是两个不同但相互呼应的口径, 二者均以标题作为可参与判据的第 0 句。当某银行-年度报道中金科相关表述多以并列句或转折句形式出现而非同句嵌套时, `_ss` 轨的计数可能明显低于 `_ctx` 轨, 这并非测量误差而是判据严格性差异的正常体现, 解读时应结合 `ss_is_fallback` 比例一并考察, 避免把回退样本占比过高的行简单等同于"无金科关联"。
<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking; What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
<!-- rendered-citations:end -->
