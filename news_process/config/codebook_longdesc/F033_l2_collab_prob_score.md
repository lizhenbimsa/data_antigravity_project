---
family_id: F033
columns:
- avg_collab_prob_score_ctx
- avg_collab_prob_score_full
- avg_collab_prob_score_ss
- avg_collab_prob_score_std_ctx
- avg_collab_prob_score_std_full
- avg_collab_prob_score_std_ss
unit: 概率得分 (无量纲, 值域 [0,1]); _std 列为该概率的 bank-year 标准差
formula: "avg_collab_prob_score{track} = mean_models( compute_prob_score_binary(innovation_collab_mode{track} 标签, confidence, positive_class='外部协同') ); avg_collab_prob_score_std{track} = std_articles( avg_collab_prob_score{track} ) per (target_bank, year)"
producer: news_process/pipeline/sentiment/tone_llms.py (article-level Stage 21) ; news_process/pipeline/panel/encode.py::aggregate_panel (bank-year mean/std 数值聚合 Stage 40)
upstream:
- 15_fintech_intensity.parquet (内容/标题/content_ctx/content_ss 三轨输入)
- 21_tone_llms.parquet (article-level innovation_collab_mode 标签 + confidence + binary prob_score)
- 40_panel_yearly.parquet (bank-year mean 与 SD 聚合)
citations:
- doi: 10.1016/j.techfore.2026.124581
  type: journal
  authors: Dehghani, M. A., Brauneis, A., & Karavidas, D.
  year: 2026
  title: "Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions"
  venue: Technological Forecasting and Social Change
  vol: 226
  pages_or_artno: 124581
- doi: 10.1111/joms.13063
  type: journal
  authors: Chen, X., Yang, Y., & Wei, J.
  year: 2025
  title: "How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence"
  venue: Journal of Management Studies
  vol: 62
  issue: 2
  pages_or_artno: 565-596
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.1016/j.frl.2023.104779
  type: journal
  authors: Kueschnig, M., & Schertler, A.
  year: 2024
  title: "Fusing futures: Financial institutions' stock price response to fintech acquisitions"
  venue: Finance Research Letters
  vol: 59
  pages_or_artno: 104779
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: Strategic Management Journal
  vol: 27
  issue: 2
  pages_or_artno: 131-150
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"银行金融科技创新的协作模式" (innovation collaboration mode) 这一构念在 bank-year 面板上的连续化概率测度。构念根植于开放式创新理论: Chesbrough (2003) 把企业创新划分为"封闭式" (依赖内部研发、自给自足) 与"开放式" (跨越企业边界、引入外部知识与合作伙伴) 两种范式; Laursen 与 Salter (2006) 进一步把"开放度"操作化为企业向外部搜寻知识来源的广度与深度, 并实证其对创新绩效的贡献。落到本项目的语料, 每一篇被判定为"某目标银行 × 金融科技"的媒体报道, 都会被 Stage 21 的三个大语言模型阅读并给出一个三维创新标签之一——innovation_collab_mode——用以回答"这条创新是银行自主研发、还是与外部机构 (金融科技公司、平台、科研机构) 协同完成"。正类 (positive_class) 锁定为"外部协同", 即 1 表示开放式/对外合作, 0 表示自主研发/封闭式, 与 stata_export 中 1=对照 的编码方向保持一致。该维度与情感语调 (tone)、创新实质性 (substantiveness, W&Z)、创新落点 (locus, Gomber) 三者正交并列, 共同构成对单篇报道创新性质的多维刻画。Chen 等 (2025) 关于联盟战略 (alliance strategy) 与技术互依如何驱动新创企业成长的研究, 为"外部协同"这一构念在生态位创业情境下的战略价值提供了近期理论支撑; Dehghani 等 (2026) 则直接考察金融机构层面的开放式创新与知识产权管理实践, 是本构念在 FinTech 场景内最贴近的当代对应。

【方法学与计算】
测度分两级构造。第一级 (article-level, Stage 21, 由 tone_llms.py 产出): 三个 LLM 家族 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 各自对同一篇文章的 collab_mode 标签及其置信度 (confidence) 给出判断; 函数 compute_prob_score_binary(label, confidence, positive_class="外部协同") 把每个模型的离散标签与置信度联合映射为一个 [0,1] 区间的二分类概率分——标签为"外部协同"时分数随置信度上升趋近 1, 标签为"自主研发"时随置信度上升趋近 0, confidence 为 NaN 或越界则被拒绝 (对应 P2_BIN/P3_BIN 守卫)。三模型分数取均值即得文章级 avg_collab_prob_score{track}。这一 logit-to-score 的连续化思路与概率校准文献一脉相承: Niculescu-Mizil 与 Caruana (2005) 指出把分类器输出转成可信概率需要审慎处理, 本项目用置信度加权而非直接采纳硬标签, 正是为了保留判定的不确定性信息, 避免把边界个案强行二值化。第二级 (bank-year, Stage 40, 由 encode.py 的 aggregate_panel 完成数值聚合): 对同一 (target_bank, year) 下的所有文章级分数取均值得到面板主列 avg_collab_prob_score{track}, 取标准差得到离散度列 avg_collab_prob_score_std{track}——后者刻画的是"该行该年不同报道在协作模式上的分歧程度", 高值意味着媒体对该行创新是自主还是合作莫衷一是。需辨明分工: 真正把文章级分数聚成 bank-year mean/std 的算子是 encode.py::aggregate_panel 中登记的 (源列, 'mean') 与 (源列, 'std') 聚合项 (走 pandas 默认 ddof=1, NaN 安全), collab 维的 mean+std 于 2026-06-14 补齐以与 subst/locus 两维在三轨上对称; codebook.py 在本环节仅生成 VariableMetadata 文本描述、并不计算任何数值, 故聚合 producer 归 encode.py 而非 codebook.py。

【三轨与识别口径】
本家族的六列覆盖 full / ctx / ss 三条文本轨。full = 标题 prepend + 全文正文; ctx = 标题 + 实体上下文窗口; ss = 标题 + 银行与金科同句共现片段 (±N 句窗)。ss 的回退语义镜像 ctx: 当某篇不存在银行∧金科同句共现时, content_ss 降级为全文正文且 ss_is_fallback=True。三轨遵循 full-only 留篇门控 (2026-06-29): 一篇报道是否被判为"银行金科报道"、是否留在样本内, 只看 verified_full; ctx 与 ss 被降为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 各轨列在其上照常计算但不参与留篇决定。三轨互为稳健性、不分主次: 每条轨道各自 just-identified 并排进入分析, 严禁把 full/ctx/ss 三列混进同一个 over-identified 的 Hansen J 过度识别检验——这是项目的口径铁律, 因为三轨是同一构念在不同取材范围下的替代测量, 而非可叠加的独立工具变量。同理, mean 主列与 _std 离散度列刻画的是分布的一阶矩与二阶矩, 属互补而非替代信息, 也不应被塞进同一过度识别集。整个 Stage 21 是全流水线唯一核心付费阶段, 其确定性由 _llm_cache.db 缓存账本锚定 (Prompt v8 字节级冻结、temperature=0.0), 命中即可离线零成本逐字节复现——de Kok (2025) 关于生成式大模型用于文本分析研究的方法学讨论, 恰强调了此类 LLM 打分必须可复现、可审计, 本项目的缓存化设计正是对该要求的直接回应。

【文献定位与构念区分】
在文献坐标上, 本家族处于"开放式创新度量"与"金融科技银行合作"两条脉络的交叉点。Zhang 等 (2024) 对过去二十年开放式创新研究的框架与元分析, 为把 collab_mode 二分为开放/封闭提供了成熟的构念边界; Kueschnig 与 Schertler (2024) 对金融机构收购金融科技公司股价反应的研究, 则提示"外部协同"在实践中常以并购、股权投资、战略合作等具体形态出现, 是本测度所要捕捉的现实对象。需与相邻测度审慎区分: 本家族测的是创新的"协作模式" (谁来做), 与创新的"实质性" (是真投入还是象征性表态) 及"落点" (底层技术还是应用场景) 是不同的分类维度, 三者由同一批 LLM 在同一次调用中并行判定但语义正交, 不可互相替代或合并入同一识别式。已知局限有三: 其一, 媒体报道对"合作"的描述可能系统性多于对"自研"的描述 (合作事件更具新闻价值), 使概率分存在向上偏; 其二, ctx/ss 轨在样本较薄的 bank-year 上可能出现方差退化甚至常数化, _std 列在此类格点会失真, 应结合有效篇数解读; 其三, LLM 判定虽经三家投票但仍可能对中文语境下的"参股""共建""接入"等模糊表述归类不稳, 故本测度以三轨并排、mean 与 std 并列的方式提供互为稳健性的多重视角, 而非单点结论。

## VAR: avg_collab_prob_score_full

【变体差分】
本列是 full 轨的协作模式概率主列, 取材范围为"标题 prepend + 全文正文", 是三轨中信息最完整、也是留篇门控唯一依据的轨道。其值 = 三个 LLM 对该篇 innovation_collab_mode_full 标签按 compute_prob_score_binary(positive_class="外部协同") 各产一个 [0,1] 分后取均值, 再在 (target_bank, year) 上对所有留篇文章取均值。相较 ctx/ss 轨, full 轨读的是完整文章, 不做实体窗口或同句窗口截断, 因而对"合作"信号的召回最高、漏判最少, 但也最容易把与目标银行关系较弱的背景性合作叙述纳入。作为 full-only 门控 (2026-06-29) 的承载轨, 只有 verified_full 判定为真的文章才进入本列的 bank-year 分母, ctx/ss 轨的对应列则是在此留篇集之上的条件测度。本列与 ctx/ss 两列互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified Hansen J。值域 [0,1], 越接近 1 表示该行该年的报道整体越倾向于把创新描述为对外开放协同, 越接近 0 越倾向自主研发。生产口径下本列由 Stage 21 缓存命中确定性复现, 无需重复付费调用。在文献坐标上, 本列所测的"外部协同"倾向正是 Chesbrough (2003) 意义上的开放式创新在媒体叙事层面的映射; Dehghani 等 (2026) 关于金融机构开放式创新实践的研究提示, 银行的对外合作常伴随知识产权与平台接入安排, 本列对完整正文的高召回口径最能捕捉这类跨边界协同的多样表述。相较三维中的实质性与落点两列, 本列语义正交、由同一次 LLM 调用并行判定, 不可互相替代或合并入同一识别式; 作为 full 轨主列, 它是 P5 (collab, provisional) 主线处理变量族在协作概率维度上的完整信息锚点。

## VAR: avg_collab_prob_score_ctx

【变体差分】
本列是 ctx 轨 (实体上下文轨) 的协作模式概率, 取材范围为"标题 + 目标银行实体上下文窗口", 只把围绕目标银行实体出现位置的邻近文本喂给 LLM, 剔除与该行无关的段落。相较 full 轨, ctx 轨牺牲了部分召回以换取"判定聚焦于目标银行自身的合作行为"这一更严格的相关性——当一篇长文同时提及多家机构的合作时, ctx 轨更可能只捕捉与目标银行直接相关的协同信号。计算式与 full 轨同构: 三模型 binary prob_score (positive_class="外部协同") 取均值得文章级分, 再在 bank-year 上取均值。关键差异在门控地位: ctx 轨不参与留篇决定, 是 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集的子集; 当某篇的实体窗口未能覆盖协作描述时, 该篇 ctx 判定可能与 full 判定分歧, 这正是三轨互为稳健性的价值所在。本列与 full/ss 两列各自 just-identified 并排, 禁混同一 over-identified Hansen J。值域 [0,1], 语义方向同 full 轨: 高值指向外部开放协同。ctx 轨在样本较薄的 bank-year 上可能因窗口内有效文本不足而出现方差收缩, 解读时应参照该格点的有效篇数。ctx 轨的存在价值在于提供一个"相关性更严格"的替代测量: Laursen 与 Salter (2006) 强调开放度须落到企业自身向外部搜寻知识的具体行为上, ctx 轨的实体聚焦恰是把这一"落到目标银行自身"的口径工程化; 当 full 轨因长文背景合作叙述而高估外部协同倾向时, ctx 轨可作为纠偏的稳健性对照。本列与 full/ss 三轨并排各自进入分析而非合并, 正是为了让读者比较"完整取材"与"实体聚焦"两种口径下协作概率的一致性, 从而判断结论是否被取材范围驱动。

## VAR: avg_collab_prob_score_ss

【变体差分】
本列是 ss 轨 (同句共现轨) 的协作模式概率, 取材范围最窄: "标题 + 银行与金融科技词同句共现的句子片段 (±N 句窗)"。ss 轨的设计意图是把 LLM 的注意力压缩到"银行与金科在同一句话里被同时提及"的最强共现证据上, 从而对协作模式给出最保守、最不受无关上下文干扰的判定。其回退语义严格镜像 ctx: 当某篇不存在银行∧金科同句共现时, content_ss 优雅降级为全文正文且 ss_is_fallback=True, 与 ctx 共享 n_articles 分母口径, 避免因回退产生单边孤儿。计算式与 full/ctx 同构: 三模型 binary prob_score (positive_class="外部协同") 取均值, 再 bank-year 取均值。作为 conditional-on-full 稳健性轨, ss 轨不参与留篇门控, 行宇宙是 full 留篇集的子集。在开发期 T=2 的薄样本上, ss 轨因回退与窗口稀疏可能出现较高比例的 fallback, 其 mean 与 full 轨趋同、方差退化属预期现象, 生产期 T=19 语料下方能充分展开三轨差异。本列与 full/ctx 各自 just-identified 并排, 禁混同一 over-identified Hansen J。值域 [0,1], 高值指向外部开放协同。ss 轨是三轨中最保守的证据口径: 只有当银行与金融科技词落在同一句话时才被视作最强共现证据喂给 LLM, 因而对"这条协作是否真与目标银行直接相关"施加了最严的门槛。Kueschnig 与 Schertler (2024) 对金融机构收购金融科技公司的研究提示, 现实中的外部协同 (并购、股权、战略合作) 往往在报道里被浓缩在少数关键句中, ss 轨的同句取材恰能抓住这类高密度共现表述, 是 full 与 ctx 之外第三种互补视角, 三者并排比较可检验协作结论的取材稳健性。

## VAR: avg_collab_prob_score_std_full

【变体差分】
本列是 full 轨协作模式概率的 bank-year 标准差, 即对同一 (target_bank, year) 下所有留篇文章的 avg_collab_prob_score_full 取 std, 刻画的是"该行该年不同报道在协作模式判定上的离散/分歧程度"而非中心水平。与主列 avg_collab_prob_score_full 是同一分布的二阶矩与一阶矩关系: 主列答"平均而言偏开放还是偏自研", 本列答"各篇报道是否众口一词"。高 std 意味着媒体对该行创新是自主还是合作存在实质分歧 (例如同年既有报道称其自建技术团队、又有报道称其与金科公司战略合作), 低 std 意味着报道口径一致。单位为概率的标准差 (无量纲), 值域受 _PROB_STD_RANGE 约束。本列与 mean 主列刻画互补信息, 不可替代——mean 与 std 严禁塞进同一 over-identified Hansen J; 本列与 ctx/ss 两条 std 轨亦各自 just-identified 并排、互为稳健性、不分主次。重要局限: 当某 bank-year 仅有一篇留篇文章时 std 无定义 (或为 0), 薄样本格点的 std 高度依赖有效篇数, 解读须结合分母; 在开发期 T=2 上本列大量格点退化属预期, 生产期 T=19 方有稳定离散度。从研究用途看, 本列可作为"媒体对该行创新协作模式认知不确定性"的代理: 当一家银行同年既被描述为自建能力、又被描述为对外合作时, 本列取值升高, 这种分歧本身可能与该行处于自研向开放转型的过渡期相关, 呼应 Chen 等 (2025) 关于联盟战略与技术互依动态演化的观察。使用时须谨记本列刻画的是二阶矩离散度而非水平, 与主列联合解读方能完整——切勿单独把 std 当作"合作强度"读。

## VAR: avg_collab_prob_score_std_ctx

【变体差分】
本列是 ctx 轨 (实体上下文轨) 协作模式概率的 bank-year 标准差, 即对 avg_collab_prob_score_ctx 在 (target_bank, year) 上取 std。它测的是"在实体聚焦口径下, 该行该年各篇报道对协作模式判定的分歧程度"。相较 full 轨的 std, 本列的离散度建立在更严格的相关性过滤之上——只有围绕目标银行实体窗口的判定进入方差计算, 因而更能反映"针对该行自身合作行为"的报道一致性, 而非被无关背景合作叙述稀释。作为 conditional-on-full 稳健性轨的离散度列, 其行宇宙同样是 full 留篇集的子集, 不参与留篇门控。本列与 std_full/std_ss 各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 与其对应的 mean 主列 avg_collab_prob_score_ctx 是互补的分布二阶矩, 亦不并入同一过度识别集。单位为概率标准差 (无量纲), 值域受 _PROB_STD_RANGE 约束。局限与 std_full 同源且更甚: ctx 轨窗口内有效文本较薄时, 单篇或零方差格点更常见, 在 T=2 开发样本上退化为常数或 NaN 属预期, 解读须严格结合该 bank-year 的有效篇数, 生产 T=19 语料下方能提供可靠的离散度信号。相较 std_full, 本列因建立在实体聚焦口径上, 其离散度更能剥离"无关背景合作叙述"带来的伪分歧, 从而更纯粹地反映针对目标银行自身协作模式判定的报道一致性; 但代价是窗口稀疏使有效方差样本更小, 稳定性对篇数更敏感。本列与 std_full/std_ss 并排比较, 可检验"报道分歧是否随取材口径而变", 是三轨离散度稳健性叙事的中间一环。

## VAR: avg_collab_prob_score_std_ss

【变体差分】
本列是 ss 轨 (同句共现轨) 协作模式概率的 bank-year 标准差, 即对 avg_collab_prob_score_ss 在 (target_bank, year) 上取 std, 测的是"在最严格的银行∧金科同句共现口径下, 该行该年各篇报道对协作模式判定的分歧程度"。因 ss 轨取材最窄且带全文回退 (无同句共现时 content_ss 降级为全文正文、ss_is_fallback=True), 本列的离散度在很大程度上受回退比例影响: 当某 bank-year 多数文章走 fallback 时, 其分布会向 full 轨趋同, std 也随之与 std_full 靠拢; 反之当同句共现证据充分时, 本列反映的是最保守共现片段上的判定分歧。作为 conditional-on-full 稳健性轨的离散度列, 行宇宙是 full 留篇集的子集, 不参与留篇门控。本列与 std_full/std_ctx 各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 与对应 mean 主列 avg_collab_prob_score_ss 是互补的分布矩, 亦不并入同一过度识别集。单位为概率标准差 (无量纲), 值域受 _PROB_STD_RANGE 约束。局限最为突出: 在 T=2 开发样本上, ss 轨的高 fallback 率叠加薄样本使本列大面积退化 (常数/NaN/趋同 std_full) 属预期, 须待生产 T=19 语料充分播种后方能展开三轨离散度的真实差异, 解读须结合有效篇数与 fallback 占比双重口径。正因如此, 本列在三条 std 轨中信息最不稳定、也最需审慎: 高 fallback 会使它退化为 std_full 的近似, 低 fallback 时它又反映最保守共现证据上的判定分歧, 两种情形须结合 fallback 占比区分。它与 std_full/std_ctx 三轨并排, 共同构成对"媒体协作模式认知分歧是否受取材口径驱动"这一稳健性问题的三重回答, 而非可叠加的独立信号。

<!-- rendered-citations:begin -->
Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence. Journal of Management Studies, 62(2), 565-596. https://doi.org/10.1111/joms.13063
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Kueschnig, M., & Schertler, A. (2024). Fusing futures: Financial institutions' stock price response to fintech acquisitions. Finance Research Letters, 59, 104779. https://doi.org/10.1016/j.frl.2023.104779
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
<!-- rendered-citations:end -->
