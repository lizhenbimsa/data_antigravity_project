---
family_id: F397
columns:
- llm_vote_score_w_sum_ctx
- llm_vote_score_w_sum_full
- llm_vote_score_w_sum_ss
unit: 无量纲加权得分之和 (bank-year 层, 由篇章级投票得分乘以提及密度权重后求和)
formula: 'bank-year 层 llm_vote_score_w_sum{track} = Σ_i (llm_vote_score_i{track} × mention_density_i)，对该 bank-year 单元内全部留篇文章 i 求和；mention_density 是 track-agnostic 的单一权重 (无 _full/_ctx/_ss 后缀分身), 三轨共用同一权重列, 差异仅来自 llm_vote_score{track} 本身；对应 VW 均值 llm_vote_tone_vw{track} 的分子，配对分母为 sum_wd_vw_llm{track} (valid-mask 优先) 或回退 sum_mention_density{track} (物理分母)'
producer: pipeline\panel\encode.py (聚合 agg[f''llm_vote_score_w_sum{track}''] = (f''llm_vote_score_w{track}'', ''sum'')；篇章级 weighted_cols[f''llm_vote_score_w{track}''] = df[f''llm_vote_score{track}''] * w 在 pipeline\panel\runner.py 内以单一 track-agnostic 权重 w = df['mention_density'].fillna(0) 逐轨相乘；审计对齐 pipeline\audit\stata_audit.py)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track}, 三家 LLM 多数投票篇章级得分)
- 11_news_bank.parquet (mention_density, 在 pipeline\filtering\news_bank.py 内以 bank_info['total_count'] / doc_len 直接计算, track-agnostic 单一列, 供三轨权重共用)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-level political risk: Measurement and effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: "10.1287/mnsc.2024.08999"
  type: "journal"
  authors: "Burtch, G., McFowland, E., Yang, M., & Adomavicius, G."
  year: 2026
  title: "EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables"
  venue: "Management Science"
  pages_or_artno: "mnsc.2024.08999"
new_dois: []
---

## CORE

【构念与来源】
llm_vote_score_w_sum 家族刻画的是「银行—年度」单元内, 由三家大语言模型 (gpt54nano / gemini31 / deepseekv4) 多数投票得到的篇章级情感得分, 按提及密度 (mention_density) 加权后求和的价值加权 (value-weighted, VW) 汇总量。它本身是一个中间聚合分子, 不是最终归一化的语气均值: 真正对外报告、进入 Table 1/主回归的是分母归一后的 llm_vote_tone_vw{track} (= llm_vote_score_w_sum{track} / 对应分母), 而 llm_vote_score_w_sum{track} 的作用是把这一均值恒等式的分子单独物化出来, 供 stata_audit.py 的加权均值恒等式校验 (VW/MW/HW 三套权重) 复核、也供研究者在需要自定义分母 (例如按不同 valid-mask 口径重算) 时直接取用。source_excerpt 中 encode.py 的聚合语句 `agg[f'llm_vote_score_w_sum{track}'] = (f'llm_vote_score_w{track}', 'sum')` 表明该列是纯粹的组内求和 (groupby bank-year 后对篇章级 `llm_vote_score_w{track}` 做 sum), 而篇章级 `llm_vote_score_w{track}` 又是 `llm_vote_score{track}`（三家 LLM 多数票判定的正负标签映射的数值得分, 通常 {-1,0,1} 或经度数强度扩展的连续得分）乘以该篇文章的 `mention_density` 权重所得。需特别澄清的一点口径: mention_density 并非分轨物化的量, 它在 stage 11 `news_bank.py` 内以 `total_count / doc_len` 一次性算出、且全仓不存在 `mention_density_full`/`_ctx`/`_ss` 任何分身列——full/ctx/ss 三条轨道的 llm_vote_score_w_sum 在权重侧共用这同一个 track-agnostic 的 mention_density, 三轨之间的差异完全来自分子侧的 `llm_vote_score{track}`（三家 LLM 在不同文本窗口上的多数投票判定不同）, 而非来自权重侧的密度计算。mention_density 度量的是目标银行在该篇报道全文中被提及的相对密度/显著性 (提及次数相对于文档长度的归一量, 在 ctx/ss 窗口物化之前即已算好), 借鉴 Hassan et al. (2019, QJE) 在企业层面政治风险测度中"以提及密度而非简单计数加权文本信号"的做法——密集、反复提及目标银行的报道被认为承载更强的情感信息含量, 因此在加总时赋予更高权重; 这与等权 (unweighted) 篇章计数式测度形成对照, 后者对"一句带过"和"通篇聚焦"一视同仁。

【方法学与计算】
三家 LLM 多数投票的方法学基础见 stage 21 tone_llms 的三家并列设计: gpt-5.4-nano、gemini-3.1-flash-lite (经 yunwu 中转) 与 deepseek-v4-flash (直连 api.deepseek.com), 对同一篇章-轨道文本独立打分, 再以多数表决 (2/3 及以上一致) 汇总为 llm_vote 系列的共识判断; 这一「多模型集成投票降低单模型幻觉/系统性偏误」的设计取向与 Kamen & Kamen (2025) 提出的 LLM ensemble majority-rule 内容分类范式一致, 也呼应 Gilardi, Alizadeh & Kubli (2023, PNAS) 关于 LLM 标注在文本标注任务上可比甚至超越众包人工标注者的发现——多数投票在此进一步降低了对单一模型输出的依赖。prompt 构造采用 v8-2026-05-17 冻结版本、temperature=0.0, 确定性缓存命中键与 de Kok (2025, Management Science) 倡导的"生成式 LLM 用于会计/金融文本分析须走可复现、temperature=0、prompt 版本冻结"范式对齐, 这也是本仓库能够以 `NEWS_PROCESS_LLM_OFFLINE=1` 实现三轨零字节漂移离线复现的方法学基础。加权求和本身是简单算术: 对 bank-year 单元内每篇留篇文章的 `llm_vote_score{track} × mention_density{track}` 逐篇相乘后组内求和, 不涉及归一化、不做符号截断, 因此该列的绝对量级会随 bank-year 单元内文章数量、密度权重尺度而变, 不能脱离配对分母单独解读为"平均语气"; 它与配对的 VW 均值列构成经典的"分子/分母恒等式"对偶结构, 这也是 stata_audit.py 专门设一节校验加权均值恒等式 (VW/MW/HW 三套权重是否可由各自分子除以各自分母精确复现) 的原因——一旦分子分母口径 (valid-mask vs 物理分母) 不匹配, 恒等式校验会给出 WARN 并提示口径不一致的诊断细节。

【文献定位】
本家族在文献坐标系中横跨两条脉络: 一是媒体情感测度的价值加权传统, 源自 Tetlock (2007, Journal of Finance) 首次系统论证媒体语气可作为投资者情绪的可观测代理, 后续研究普遍采用以提及强度/显著性加权的做法避免"稀释"高信息密度报道的情感信号, Hassan et al. (2019, QJE) 在政治风险测度上进一步规范化了这一"提及密度加权求和"的操作化路径, 本家族的 mention_density 加权设计直接承袭这一传统; 二是大语言模型作为文本标注引擎的新兴方法学脉络, Gilardi et al. (2023, PNAS) 与 de Kok (2025, Management Science) 分别从标注质量和会计/金融应用规范两个角度为"用 LLM 替代/补充人工标注"提供了方法学正当性, Kamen & Kamen (2025) 则专门论证了多模型集成投票相较单模型的稳健性优势——本家族的三家 LLM 多数投票设计正是这一集成范式在中文银行金科新闻语境下的落地。三轨 (full/ctx/ss) 并行是仓库全局铁律: full/ctx/ss 三条文本窗口 (全文、实体上下文窗、银行∧金科同句窗) 各自独立聚合出 llm_vote_score_w_sum, 三者是「互为稳健性、不分主次」的并列测度, 各自 just-identified, 严禁混入同一 over-identified 的 Hansen J 检验; 留篇门控口径统一为 full-only (2026-06-29 起), 即 stage 21 是否判定"一篇银行—金科报道"仅看 `llm_verified_full == True`, ctx/ss 轨道的样本行宇宙是 full 留篇集的子集, 三轨互不借用彼此的行集合。需要强调的是, 这一"各轨并列"仅体现在分子侧的 `llm_vote_score{track}`——权重侧的 mention_density 是唯一一个 track-agnostic 元数据度量, 三轨在求和时共用同一份权重列, 并不存在"各轨各自计算自身密度权重"的口径; 这与记忆库中"唯一不能双轨的是 track-agnostic 元数据度量"的先例完全一致, 权重的不可分轨恰恰是为了保证三轨之间的差异纯粹来自情感判定本身, 而非权重口径漂移带来的混淆。 沿分子侧这条线再向下游看一步, Burtch、McFowland、Yang 与 Adomavicius (2026) 利用集成学习器内部各成员预测之间的差异构造工具变量, 以缓解 ML 生成变量作为回归元时的测量误差偏误; 本族的 llm_vote_score_w_sum{track} 恰是由三家异构模型逐篇打分、投票后再按 mention_density 加权求和而成的 ML 生成变量, 该文因此为下游把此类聚合量当作回归元的做法提供了一条已发表的处理路径参照。其迁移边界须如实标明: 原文的集成成员是同一训练流程下的 ML 预测器 (树/神经网络等), 成员间差异有明确的重采样来源; 本项目的成员是三家不同厂商的闭源 LLM, 差异来源不可控亦不可重采样, 原文构造 IV 的前提未必成立。本项目并未实施 EnsembleIV, 该文仅作方法学存在性参照收录; 尤须强调, 不得据此把三家 per-model 子测度或 full/ctx/ss 三轨并列列混入同一 over-identified 的 Hansen J——这与上文已述的各自 just-identified 并排、互为稳健性不分主次的口径直接冲突。
## VAR: llm_vote_score_w_sum_full

【变体差分】
本列是 llm_vote_score_w_sum 家族在 full 轨道 (标题 + 全文正文) 上的实现, 是三轨中的基准/主口径轨道: full 轨道同时也是留篇门控的唯一判据来源——一篇报道是否被计入 bank-year 分析样本, 完全由 `llm_verified_full == True` 决定, ctx 与 ss 轨道的样本行集合是 full 留篇集的子集而非独立门控。因此 llm_vote_score_w_sum_full 的求和范围 (bank-year 单元内哪些篇章参与加总) 直接对应该银行—年度被判定为"银行∧金科"相关报道的全部留篇文章。需要澄清的是, 该列的权重侧 mention_density 并非 full 轨道独有的量: 它是 stage 11 `news_bank.py` 在全文上一次性计算出的 track-agnostic 单一列 (`total_count / doc_len`), 不存在 `mention_density_full` 这一分轨列名, ctx/ss 两轨在求和时同样复用这份基于全文计算出的权重——一篇报道即便标题只提一次银行名, 只要正文反复讨论, 该权重仍会体现整体篇幅内的相对显著性, 且这一显著性判定对三轨一视同仁, 三轨之间只有分子 `llm_vote_score{track}` 会随轨道变化。full 轨道的 VW 均值分母优先取 valid-mask 列 `sum_wd_vw_llm_full` (仅统计 LLM 判定有效的篇章), 缺失时回退物理分母 `sum_mention_density_full`; 该列作为分子在两种分母口径下数值不变, 变的只是归一化后的均值。作为三轨并列测度之一, full 轨道与 ctx/ss 轨道互为稳健性、不分主次, 但由于其同时承担留篇门控职能, 在解读跨轨道差异时 (例如 stata_audit.py 中 Full-Ctx / Full-SS / Ctx-SS 三对相关性诊断) 应注意 full 是唯一"完整样本"轨道, ctx/ss 若出现回退 (fallback) 情形 (无实体窗口匹配或无银行∧金科同句共现), 会分别退化为镜像口径 (ctx 缺窗口回退全文、ss 缺同句共现回退全文并标记 `ss_is_fallback=True`), 这一降级机制使得 ctx/ss 轨道在退化样本上与 full 数值趋同, 属预期设计而非异常。

## VAR: llm_vote_score_w_sum_ctx

【变体差分】
本列是 llm_vote_score_w_sum 家族在 ctx 轨道 (标题 + 目标银行实体上下文窗) 上的实现, 属于 conditional-on-full 的稳健性测度: 其求和行宇宙被限定为 full 轨道留篇集合的子集 (即已通过 `llm_verified_full == True` 门控的文章), 在该子集上取 ctx 轨道自身的 `llm_vote_score_ctx` 乘以 track-agnostic 的 `mention_density` (与 full/ss 两轨共用同一份权重列, 该权重在 stage 11 全文上算出、不随轨道分身) 并逐篇相乘求和。ctx 文本窗口通过在 stage 14 `ctx_materializer` 中截取目标银行实体附近的局部上下文窗口构造 (`content_ctx` = 标题前置 + 实体窗口文本), 相较 full 轨道剔除了与目标银行不直接相关的大段正文, 因此该列相对 full 轨道的差异完全来自 ctx 窗口文本对 LLM 判分结果 `llm_vote_score_ctx` 的影响, 而非权重侧的差异——这正是 ctx 轨道存在的构念意义: 在权重口径保持恒定的前提下, 单独检验情感判定结果是否对"文本窗口截取范围"敏感。若某篇文章找不到有效实体窗口 (无法定位目标银行的局部上下文), ctx 轨道回退为全文 body, 并标记该篇 `ctx_is_fallback=True`, 此时该篇在 ctx 轨道上的 llm_vote_score_ctx 将与 full 轨道趋同、权重侧本就恒定不变 (但两轨依然各自独立存储、独立参与各自的 bank-year 求和, 不做混轨借用)。llm_vote_score_w_sum_ctx 与 _full、_ss 是并列的互为稳健性轨道, 三者各自 just-identified, 在计量识别策略中严禁混入同一 over-identified Hansen J 检验; 在 stata_audit.py 的 Full-Ctx 跨轨道相关性诊断中, 该列 (经归一化后的 VW 均值) 与 full 轨道对应量的 Pearson r 若低于 0.5 会被记为 WARN, 提示两轨道分歧较大, 这一诊断的样本基础正是本列的加权求和结果。

## VAR: llm_vote_score_w_sum_ss

【变体差分】
本列是 llm_vote_score_w_sum 家族在 ss 轨道 (标题 + 银行∧金科同句窗口, sentence-radius 默认 ±1 句) 上的实现, 是三轨中判据最严格的轨道: 只有当目标银行与金科相关词在同一句 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的邻近句窗) 内共同出现时, 该篇文章的 ss 文本才被物化为真正的"同句窗"文本, 其求和行宇宙同样是 full 留篇集的子集, 权重侧同样取用与 full/ctx 两轨共用的 track-agnostic `mention_density` (stage 11 在全文上一次性算出, 不存在 `mention_density_ss` 分身列), 差异同样只来自分子侧的 ss 轨道判分 `llm_vote_score_ss`。ss 轨道的判定不对称口径值得特别注意: 银行侧采用否定词过滤 + 短名过滤的严格识别, 金科侧则是裸 Aho-Corasick 607 词表匹配, 这一不对称设计使得 ss 轨道相较 ctx 轨道的窗口截取更为苛刻——ctx 只需实体窗口命中即可, ss 则要求银行∧金科词在物理句子层面邻近共现。当一篇文章不存在银行∧金科同句共现时, ss 轨道镜像 ctx 轨道的回退语义: `content_ss` 整体回退为全文 body, 并标记 `ss_is_fallback=True` (与 `ctx_is_fallback` 共享 `n_articles` 分母口径), 该情形下 llm_vote_score_ss 在该篇上将与 full 轨道趋同, 从而 llm_vote_score_w_sum_ss 在该篇上的贡献值也与 full 轨道趋同 (权重侧本就始终恒定)。早期试跑 T=2 小样本环境下 ss 轨道回退比例可能偏高, 使得 ss 与 full 的相关性诊断呈现高度一致属预期退化, 并非度量失效; 在生产 T=19 全量语料上 ss 轨道预期能捕捉到更纯粹的"同句共现"情感信号, 剥离掉报道中与银行无关的金科议题段落的情感噪声。llm_vote_score_w_sum_ss 与 _full、_ctx 三者互为稳健性、不分主次, 各自 just-identified 并排, 同样禁止混入同一 over-identified Hansen J 检验; stata_audit.py 中的 Full-SS 与 Ctx-SS 两对跨轨道相关性诊断均以本列 (归一化后) 为样本对象之一, 用于监测该轨道是否与其他两轨呈现异常的系统性偏离。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk: Measurement and effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Burtch, G., McFowland, E., Yang, M., & Adomavicius, G. (2026). EnsembleIV: Creating Instrumental Variables from Ensemble Learners for Robust Statistical Inference with ML- Generated Variables. Management Science, mnsc.2024.08999. https://doi.org/10.1287/mnsc.2024.08999
<!-- rendered-citations:end -->
