---
family_id: F052
columns:
- avg_llm_conf_ctx
- avg_llm_conf_ctx_z
- avg_llm_conf_full
- avg_llm_conf_full_z
- avg_llm_conf_ss
- avg_llm_conf_ss_z
- avg_llm_conf_std_ctx
- avg_llm_conf_std_full
- avg_llm_conf_std_ss
unit: 无量纲 (LLM 情感置信度宏平均, 落在 0-1 概率区间; _std 后缀列为同域内的样本标准差, 同量纲; _z 后缀列为逐年度截面 z-score 标准化, 无量纲且年内均值 0 方差 1)
formula: "article-level avg_llm_conf{track} = mean_m {model}_sentiment_confidence{track}, 掩码到 valid-vote 域 (llm_vote_score{track}.notna()); 且仅计该模型自身投出有效票 ({model}_score{track}.notna()) 的格 — 缺席 (API 失败, conf=0.0 哨兵)/判伪/缺标模型格剔出分子分母 (F3 2026-07-16, D5 口径); panel avg_llm_conf{track} = 银行-年内该文章级列的均值; avg_llm_conf_std{track} = 同域样本标准差; avg_llm_conf{track}_z = 逐年度截面标准化, 对每个 year 分组内有新闻覆盖的各银行 (n_articles>0), z = (x - mu_year) / sigma_year, 其中 mu_year/sigma_year 为该年各银行截面均值/标准差 (门槛: 年内有效观测 n>=3 且该列全表 notna>=10, sigma<1e-10 或不足则该组留 NaN)"
producer: news_process/pipeline/panel/encode.py (文章级宏平均合成 + valid-vote 域掩码 + 银行-年 mean/std 聚合) ; news_process/pipeline/panel/geography.py (步骤 7b Fama-MacBeth 1973 逐年度截面 z-score 标准化 standardize_panel_variables) ; news_process/pipeline/panel/export.py (变量标签 var_labels)
upstream:
- 21_tone_llms.parquet ({model}_sentiment_confidence{track} 三模型逐轨置信度 + llm_vote_score{track})
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 40_panel_yearly.parquet (银行-年聚合宿主)
citations:
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: Finance and Economics Discussion Series (FEDS), Federal Reserve Board
  pages_or_artno: "2026-020"
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
  pages_or_artno: arXiv:2412.07031
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., et al.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
  pages_or_artno: arXiv:2502.18036
- doi: 10.48550/arXiv.2509.08825
  type: arxiv
  authors: Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D.
  year: 2025
  title: "Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation"
  venue: arXiv
  pages_or_artno: arXiv:2509.08825
- doi: 10.18653/v1/2024.naacl-long.366
  type: journal
  authors: Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I.
  year: 2024
  title: "A survey of confidence estimation and calibration in large language models"
  venue: Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)
  pages_or_artno: 6577-6595
- doi: 10.48550/arXiv.2408.15204
  type: arxiv
  authors: Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D.
  year: 2024
  title: "Can unconfident LLM annotations be used for confident conclusions?"
  venue: arXiv
  pages_or_artno: arXiv:2408.15204
- doi: 10.1038/s41586-024-07421-0
  type: journal
  authors: Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y.
  year: 2024
  title: "Detecting hallucinations in large language models using semantic entropy"
  venue: Nature
  vol: 630
  issue: 8017
  pages_or_artno: 625-630
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是情感标注环节的信号清晰度, 而非情感倾向本身。stage 21 情感 LLM 由三家模型投票产出 (gpt-5.4-nano、gemini-3.1-flash-lite 两家走 OpenLux, deepseek-v4-flash 直连 api.deepseek.com), 每家在给出正面/负面/中性判断的同时回吐一个落在 0 到 1 概率区间的自评置信度 {model}_sentiment_confidence。本家族把同一篇文章上三家的逐轨置信度做宏平均 (macro-average, 各模型等权先各自成列再取算术平均, 而非把三家概率混池), 得到文章级的 avg_llm_conf, 再在银行-年层面聚合成面板列。它回答的问题是: 支撑本银行本年度情感均值的那批报道, LLM 读起来到底有多确定。置信度高说明文本情感信号鲜明、标注噪声小; 置信度低说明文本模棱两可、标注测量误差大。这一构念因此天然是情感测度的信噪比刻画量, 用于诊断与调节而非直接进入处理变量位置。

【方法学与计算】
计算分三步, 文章级宏平均与银行-年 mean/std 聚合的承重细节在 pipeline/panel/encode.py (F3 2026-07-16: 宏平均仅计该模型自身投出有效票的格 — 缺席 [conf=0.0 结构性哨兵] 与在场判伪/缺标格不入分子亦不入分母, 与 _conf_valid_* 逐模型掩码列同口径), 标准化在 pipeline/panel/geography.py 的 standardize_panel_variables (步骤 7b), export.py 仅提供变量标签。第一步文章级合成: 对每条轨道 (full/ctx/ss) 取该轨三模型置信度列的按行均值。关键的域对齐修正 (fix omni-g-encode-02, 2026-06-11) 在于, 这个宏平均必须掩码到 valid-vote 域, 即只保留 llm_vote_score{track} 非缺失 (等价于该文章在该轨拿到了一张有效情感票) 的行; 因为它要调节的 llm_vote_tone 本身只用有效票算, 而验证失败/未定义/调用失败的无效票文章其自评置信度系统性偏低 (盘上实测无效文章置信度约 0.66, 有效约 0.88), 若把它们混进来会让验证失败率高的银行的 avg_llm_conf 被无效票机械拉低, 造成域错位。修正后 raw 列保持原值不动, 另产 underscore 掩码列供聚合字典优先取用, 其余消费者 (llm_vote_cont 等) 不受影响。第二步银行-年聚合: 面板层对文章级列求组内均值得到 avg_llm_conf{track} (一阶矩), 求组内样本标准差得到 avg_llm_conf_std{track} (二阶矩, 刻画年内报道置信度的离散程度)。第三步逐年度截面标准化: 对聚合后的均值列做年度截面 z-score 标准化, 即在每个 year 分组内、仅对有新闻覆盖的各银行 (n_articles 大于 0), 减去该年各银行的截面均值再除以该年截面标准差 (参照样本是同一年度内的各银行, 而非整个银行-年集合), 得到 avg_llm_conf{track}_z, 使系数可直接读为 1 个年内截面标准差的置信度变化对应 β 个单位的因变量变动, 便于跨模型、跨规格系数比较时消除量纲差异。门槛为年内有效观测不少于 3 且该列全表非缺失不少于 10, 截面标准差近零或观测不足的年组该列留缺失, 零新闻行保持缺失。整个家族是 stage 21 概率列的纯后处理, 不额外调用任何付费接口, 在 LLM 缓存 0 miss 时可离线字节级复现。

【三轨口径与铁律】
三轨文本在 stage 14 ctx_materializer 物化: full 轨为标题 prepend 后的标题加全文正文; ctx 轨为标题加实体窗口; ss 轨为标题加银行与金科同句正负 N 窗。ss 的回退语义镜像 ctx: 当某文无银行与金科同句共现时, content_ss 退化为全文正文且 ss_is_fallback 置真, 共享同一 n_articles 分母, 属优雅降级而非丢样本。留篇门控是 full-only 口径 (2026-06-29): 一篇报道是否算作银行金科报道只看 full 轨的有效判定, ctx 与 ss 因此是 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集的子集, 但每轨的置信度列各自逐轨计算。方法论上必须复述的铁律是: full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨的置信度或其调节的情感测度混进同一个 over-identified 的 Hansen J 过度识别检验; 这与项目对 co-primary 双轨嵌入、政治词权重梯度、LLM 三家投票的处理口径一致。同理, 均值、标准差、z-score 三种矩/变换是同一构念的不同呈现, 也不并入同一过度识别式。

【文献定位】
本家族的思想根源是文本情感测度中的经典衰减偏误: 当情感度量含测量噪声时, 用它做右手侧变量的回归系数会向零收缩, 而 LLM 自评置信度恰是这种噪声的可观测代理, 置信度越低意味着测量误差越大、效应越可能被低估, 因此 avg_llm_conf 可作为信噪比调节量或样本切分依据。这一测量误差与识别的关系在 Ludwig, Mullainathan 和 Rambachan (2025) 提出的 LLM 应用计量框架中被系统化, 他们强调把 LLM 输出视为带误差的测量并据此约束推断。置信度本身作为标注质量信号的效度问题, 有专门的校准文献: Geng 等 (2024) 综述了大语言模型置信度估计与校准的方法, 指出自评概率并不天然良置准, 需谨慎解读其绝对水平; Farquhar 等 (2024) 从语义熵角度检测幻觉, 说明模型不确定性与输出可靠性之间存在可度量的联系; Gligorić 等 (2024) 则直接讨论了低置信 LLM 标注在何种设计下仍可支撑可信结论, 为把置信度用作加权/切分依据提供了间接支撑 (须注意其为一般性方法学论证, 非对本家族双域口径的直接背书)。在把 LLM 用作标注器的效度谱系上, Gilardi 等 (2023) 证明 ChatGPT 在文本标注任务上可超越众包工人, Hansen (2026) 与 Carlson 和 Burbano (2026) 分别给出无金标准时的 LLM 标注验证与管理学研究中的使用准则和警示, Baumann 等 (2025) 量化了标注设计选择带来的隐藏风险 (LLM hacking)。多模型宏平均而非单模型的做法呼应 Chen 等 (2025) 对 LLM 集成的综述: 跨厂商聚合可平滑单一模型的特质性偏差。此外本家族的确定性依赖 temperature=0、prompt 冻结与缓存复现, 这一范式的方法学讨论见 de Kok (2025)。需要强调的是, 项目对情感测度换厂商 (从 Google 转阿里 Qwen 用于嵌入; 情感 LLM 三家) 的口径变更须在手稿中披露, 而本家族作为诊断层不进入主结果的因果解释。

## VAR: avg_llm_conf_full

【变体差分】
本列是家族的 canonical 一阶矩测度, 轨道为 full。full 轨文本等于标题 prepend 后的标题加全文正文, 是留篇门控 (full-only, 2026-06-29) 的判定轨, 因此其行宇宙即银行金科报道的全体留篇集, 而非任何子集。计算上, 对该银行该年度所有 full 轨有效票文章 (llm_vote_score_full 非缺失) 取文章级 avg_llm_conf_full 的组内均值; 文章级值本身是三家模型 full 轨自评置信度的宏平均。与同家族其他列的差分在于: 相对 ctx/ss 两轨, 本列文本涵盖面最宽 (全文而非实体窗或同句窗), 通常置信度水平最稳、样本最全, 是审稿人判断该银行情感均值信噪比时的首选参照。相对 avg_llm_conf_std_full, 本列刻画的是置信度的中心水平 (一阶矩) 而非年内离散 (二阶矩); 相对 avg_llm_conf_full_z, 本列保留原始 0-1 概率量纲而非逐年度截面标准化。作为诊断/调节量, 本列低值提示该银行-年情感测度测量误差偏大, 据 Ludwig 等 (2025) 的框架其相关系数更可能受衰减偏误影响。文章级宏平均是三家模型 (gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash) 等权先各自成列再取算术平均, 而非把三家概率混池, 这一跨厂商聚合可平滑单一模型的特质性偏差, 呼应 Chen 等 (2025) 对 LLM 集成的讨论; 单家置信度的绝对水平并不天然良置准 (Geng 等 2024), 宏平均后作水平参照亦须谨慎。方法论铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 均值、标准差、z-score 三种呈现属互补, 不并入同一过度识别式。

## VAR: avg_llm_conf_ctx

【变体差分】
本列与 canonical 的唯一差分在轨道: ctx 轨文本为标题 prepend 后的标题加实体窗口 (银行与金科实体附近的上下文窗), 而非 full 轨的全文正文。因此本列度量的是, 在只看实体邻近语境时三家 LLM 对情感判断的平均确定程度。由于留篇门控是 full-only 口径, ctx 轨为 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集, 有效票掩码走 llm_vote_score_ctx 非缺失这一逐轨口径, 分母不借用 full 轨的口径。相对 full 轨, 窄化到实体窗后文本更聚焦于银行金科主题、无关背景更少, 但可用信息量也更小, 因而置信度水平与样本量可能与 full 轨系统性不同; 二者并排正是为检验主结论不被文本窗口选择所驱动。相对 avg_llm_conf_std_ctx 与 avg_llm_conf_ctx_z, 本列分别是同轨的一阶矩、原始量纲版本, 前者取组内标准差刻画年内离散, 后者做逐年度截面标准化消除量纲。作为诊断量, 本列低值同样提示在实体邻近语境下情感信号偏弱、测量误差偏大, 据 Ludwig 等 (2025) 框架可能引致系数衰减; 但因窗口窄化会剔除背景干扰, ctx 轨置信度与 full 轨可能系统性不同, 不可用一轨水平简单外推另一轨。铁律照旧: 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把 ctx 轨与 full/ss 轨的置信度或其调节的情感测度混进同一个过度识别的 Hansen J 检验; ctx 轨相对 full 轨属规格稳健性并排, 不设跨轨 FWER 模板。

## VAR: avg_llm_conf_ss

【变体差分】
本列的差分同样在轨道: ss 轨文本为标题 prepend 后的标题加银行与金科同句正负 N 窗 (窗半径由 config filtering 的 ss_sentence_radius 控制, 默认 1)。它度量的是, 在把语境收窄到银行与金科真正同句共现的最严口径下, LLM 情感判断的平均置信度。ss 的回退语义镜像 ctx 且必须写准 (写错为 P0): 当某篇文章不存在银行与金科同句共现时, content_ss 退化为全文正文, ss_is_fallback 置真, 且与其他轨共享同一 n_articles 分母, 属优雅降级而非样本剔除; 当 FINTECH_AC 为空时全部 is_fallback 置真的全局降级也是同一逻辑。因此 ss 轨在早期试跑 T=2 小样本上可能因回退比例高而与 ctx 轨高度接近, 生产期 T=19 全量语料上才充分分化。与 canonical (full) 的差分在于文本口径最严、信息量最小、对同句共现的依赖最强, 因此在三轨梯度中处于最保守的一端: 它只保留银行与金科真正同句出现处的语境, 最大限度排除跨句、跨段的关联噪声, 代价是可用文本最少、置信度估计对回退最敏感。相对同轨的 avg_llm_conf_std_ss 与 avg_llm_conf_ss_z, 本列是一阶矩、原始量纲版本; 前者取组内标准差, 后者做逐年度截面标准化。掩码走 llm_vote_score_ss 非缺失的逐轨有效票域, 行宇宙为 full 留篇集子集。铁律: full/ctx/ss 各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; ss 相对 full/ctx 属规格稳健性并排, 不设跨轨 FWER 模板。

## VAR: avg_llm_conf_std_full

【变体差分】
本列是 full 轨的二阶矩测度, 与一阶矩的 avg_llm_conf_full 是对同一批文章级置信度的两种统计: 后者取组内均值刻画中心水平, 本列取组内样本标准差刻画年内报道置信度的离散程度。它回答的是, 该银行该年度各篇报道被 LLM 读得有多参差: 标准差大说明既有信号鲜明的报道也有模棱两可的报道, 情感测度的信噪比在年内不均匀; 标准差小说明报道置信度整齐。轨道为 full, 因此掩码与行宇宙口径与 avg_llm_conf_full 完全一致 (llm_vote_score_full 非缺失的有效票域, full-only 留篇集)。与同轨一阶矩列的差分是矩的阶数, 与另两轨的 _std 列的差分是文本轨道。在稳健性叙事里, 均值与标准差是同一置信度构念的互补呈现, 属规格稳健性并排, 二者不并入同一过度识别式; 三轨的 _std 列亦各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。作为诊断量, 高离散度提示该银行-年报道质量不齐, 情感均值背后既有强信号也有弱信号, 审稿人可据此判断是否需要对该银行-年的情感效应做加权或稳健性切分。与 avg_llm_conf_full_z 的差分在于本列是原始量纲的二阶矩而非标准化的一阶矩, 语义完全正交。早期试跑 T=2 上组内文章数少时标准差估计不稳属预期退化, 生产期 T=19 全量语料上组内篇数充足时估计正常。

## VAR: avg_llm_conf_std_ctx

【变体差分】
本列是 ctx 轨的年内置信度离散度 (组内样本标准差), 与 avg_llm_conf_ctx 一阶矩配对呈现同一构念的二阶矩。轨道差分同 ctx 一阶矩列: 文本为标题加实体窗口, 掩码走 llm_vote_score_ctx 非缺失的逐轨有效票域, 行宇宙为 full 留篇集的子集 (conditional-on-full 稳健性轨)。它度量的是, 在只看实体邻近语境时, 该银行-年各篇报道的 LLM 置信度有多参差。与 avg_llm_conf_std_full 的差分在文本窗口: 窄化到实体窗后, 无关背景被剔除, 置信度的年内离散结构可能与全文轨不同, 二者并排用于检验离散度构念不被文本口径驱动。与 avg_llm_conf_ctx_z 的差分在于本列是原始量纲的二阶矩而非标准化的一阶矩。方法论铁律照旧: 三轨的标准差列各自 just-identified 并排、互为稳健性不分主次, 严禁与 full/ss 轨的对应列或均值列混进同一 over-identified Hansen J; 一阶矩与二阶矩属互补呈现, 不并入同一过度识别式。作为诊断量, 本列刻画实体窗口语境下年内报道置信度的参差程度, 与 avg_llm_conf_std_full 并排可揭示离散结构是否随文本窗口稳健: 若两轨离散度高度一致, 说明置信度的年内参差不由文本口径驱动, 反之则提示实体窗化改变了报道被读取的确定性结构。与 avg_llm_conf_ctx 均值列是同一批置信度的一二阶矩配对, 与 avg_llm_conf_ss 的对应列构成由宽到严文本梯度上的离散度稳健性检验。早期试跑 T=2 上组内篇数少时估计不稳属预期退化, 生产期 T=19 全量语料上组内篇数充足时估计正常。

## VAR: avg_llm_conf_std_ss

【变体差分】
本列是 ss 轨的年内置信度离散度 (组内样本标准差)。轨道为最严的银行与金科同句正负 N 窗, 因此除度量矩的阶数不同于 avg_llm_conf_ss 之外, 还完整继承 ss 轨的回退语义: 无同句共现时 content_ss 退化为全文正文并置 ss_is_fallback, 与其他轨共享 n_articles 分母, 属优雅降级; FINTECH_AC 为空时全局回退。这意味着在回退比例高的银行-年, 本列的离散度更多反映的是回退文本 (全文) 而非严格同句文本的置信度参差, 解读时须结合 ss_is_fallback 比例。与 avg_llm_conf_std_full、avg_llm_conf_std_ctx 的差分在文本轨道由宽到严的梯度; 与 avg_llm_conf_ss 的差分在一阶矩与二阶矩。早期试跑 T=2 上因回退高、组内篇数少, 本列可能与 ctx 轨对应列接近或估计不稳, 属预期退化, 生产期 T=19 才充分分化。与 avg_llm_conf_std_full、avg_llm_conf_std_ctx 并排, 三者构成由宽到严的文本口径梯度上的离散度稳健性检验; 与 avg_llm_conf_ss 的差分在矩的阶数, 与 avg_llm_conf_ss_z 的差分在于本列为原始量纲的二阶矩而非标准化一阶矩, 三者语义两两正交。作为诊断量, 在同句最严口径下的高离散度尤须结合 ss_is_fallback 比例解读, 因为回退文本 (全文) 与严格同句文本的置信度参差来源不同, 混合样本上的标准差可能同时反映两种结构。铁律: full/ctx/ss 三轨的标准差列各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

## VAR: avg_llm_conf_full_z

【变体差分】
本列是 avg_llm_conf_full 的逐年度截面 z-score 标准化版本: 对聚合后的 full 轨置信度均值列, 在每个年度分组内、仅对有新闻覆盖的各银行, 减去同年各银行的截面均值再除以同年截面标准差 (参照样本是同一年度内的各银行, 而非整个银行-年集合), 得到年内均值 0、方差 1 的无量纲列。差分因此不在测度构念也不在轨道 (仍是 full 轨的置信度中心水平), 而在量纲: 原始列保留 0-1 概率量纲, 本列消除量纲以便跨模型、跨规格、跨测度做系数量级比较。在项目口径下, 跨模型/跨规格的 β 比较必须先标准化 (镜像 Table A5 跨模型系数须 z-score 的做法), 因为不同置信度分布的原始方差不同, 直接比水平会误导。本列的用途正是让 full 轨置信度作为调节量或协变量进入需要标准化系数的规格。与 avg_llm_conf_ctx_z、avg_llm_conf_ss_z 的差分在文本轨道, 与 avg_llm_conf_full 的差分在标准化变换, 与 avg_llm_conf_std_full 的差分在于本列是标准化的一阶矩而非原始量纲的二阶矩。铁律: 三轨的标准化列各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 标准化与原始量纲是同一构念的两种呈现, 不并入同一过度识别式。需要提醒的是, z-score 是逐年度截面标准化, 其数值随所在年度截面 (同年各银行) 的构成变化而漂移, 不宜跨不同年度或样本子集直接比较绝对值; 它服务的是同一次回归内的系数量级可比性, 而非绝对置信度水平的解读, 后者应回看原始量纲的 avg_llm_conf_full。

## VAR: avg_llm_conf_ctx_z

【变体差分】
本列是 avg_llm_conf_ctx 的逐年度截面 z-score 标准化版本, 差分维度与 avg_llm_conf_full_z 平行但轨道换为 ctx (标题加实体窗口)。对聚合后的 ctx 轨置信度均值列, 在每个年度分组内、仅对有新闻覆盖的各银行, 做减同年各银行截面均值除同年截面标准差的标准化 (参照样本是同一年度内的各银行, 而非整个银行-年集合), 得到无量纲、年内均值 0 方差 1 的列。它的存在理由与 full_z 相同: 当 ctx 轨置信度需要作为调节量或协变量进入跨模型/跨规格系数比较时, 须先消除量纲, 因为不同轨、不同分布的原始方差不可直接比。行宇宙与掩码口径继承 ctx 轨 (conditional-on-full 稳健性轨, llm_vote_score_ctx 非缺失域)。与 avg_llm_conf_ctx 的差分在标准化变换, 与 avg_llm_conf_full_z、avg_llm_conf_ss_z 的差分在文本轨道由宽到严的梯度, 与 avg_llm_conf_std_ctx 的差分在于标准化一阶矩而非原始二阶矩。方法论铁律: 三轨标准化列各自 just-identified 并排、互为稳健性不分主次, 严禁把 ctx_z 与 full_z/ss_z 或其调节的情感测度混进同一个 over-identified Hansen J 检验; ctx_z 相对 full_z 属规格稳健性并排, 不设跨轨 FWER 模板。同 full_z, 本列的 z-score 随年度截面 (同年各银行) 构成漂移, 服务同一次回归内的系数量级可比而非绝对水平解读, 后者应回看原始量纲的 avg_llm_conf_ctx。与 avg_llm_conf_std_ctx 的差分在于本列是标准化的一阶矩而非原始量纲的二阶矩, 二者语义正交。早期试跑 T=2 上因年度截面内银行数少 (未过 n>=3 门槛的年组留缺失), 标准化估计可能不稳属预期退化, 生产期 T=19 全量语料上正常。

## VAR: avg_llm_conf_ss_z

【变体差分】
本列是 avg_llm_conf_ss 的逐年度截面 z-score 标准化版本, 轨道为最严的银行与金科同句正负 N 窗。标准化变换与 full_z、ctx_z 一致 (在每个年度分组内、仅对有新闻覆盖的各银行, 减同年各银行截面均值除同年截面标准差, 参照样本是同一年度内的各银行而非整个银行-年集合, 得无量纲、年内均值 0 方差 1 的列), 用途也一致: 让 ss 轨置信度以可比量纲进入跨模型/跨规格的系数比较。差分在于本列继承 ss 轨最严文本口径及其回退语义 (无同句共现时退化为全文正文并置 ss_is_fallback, 共享 n_articles 分母, 优雅降级; FINTECH_AC 为空时全局回退), 因此在回退比例高的样本上其标准化前的水平更多反映回退文本。与 avg_llm_conf_ss 的差分在标准化变换, 与 full_z/ctx_z 的差分在文本轨道, 与 avg_llm_conf_std_ss 的差分在于标准化一阶矩而非原始二阶矩。早期试跑 T=2 上因回退高、年度截面内银行数少, 标准化估计可能不稳属预期退化, 生产期 T=19 正常。同 full_z、ctx_z, 本列 z-score 随年度截面 (同年各银行) 构成漂移, 服务同一次回归内的系数量级可比而非绝对水平解读, 后者应回看原始量纲的 avg_llm_conf_ss; 三个标准化列构成文本口径由宽到严梯度上的量纲可比稳健性检验。与 avg_llm_conf_std_ss 的差分在于本列是标准化的一阶矩而非原始量纲的二阶矩, 与 avg_llm_conf_ss 的差分在标准化变换; 三者语义两两正交, 分别刻画中心水平、离散程度与量纲可比水平。铁律: full/ctx/ss 三轨的标准化列各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Hansen, A. L. (2026). Validating large language model annotations. Finance and Economics Discussion Series (FEDS), Federal Reserve Board No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., et al. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.08825
Geng, J., Cai, F., Wang, Y., Koeppl, H., Nakov, P., & Gurevych, I. (2024). A survey of confidence estimation and calibration in large language models. Proceedings of the 2024 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT), 6577-6595. https://doi.org/10.18653/v1/2024.naacl-long.366
Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv [Preprint]. https://doi.org/10.48550/arXiv.2408.15204
Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature, 630(8017), 625-630. https://doi.org/10.1038/s41586-024-07421-0
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
