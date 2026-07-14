---
family_id: F391
columns:
- llm_vote_score_hw_sum_ctx
- llm_vote_score_hw_sum_full
- llm_vote_score_hw_sum_ss
unit: 无量纲加权得分之和 (herd-decay 权重 × 三家 LLM 多数投票情感分, 银行-年层面求和)
formula: 'sum(llm_vote_score_hw{track}) — 逐文章 llm_vote_score_hw{track} = llm_vote_score{track} × herd_weight{track}, 其中 llm_vote_score{track} ∈ {-1,0,1} 为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票的情感分, herd_weight{track} 为 stage 24 (herd_decay_processor) 产出的跟风衰减权重, 再按 (bank, year) 分组对逐文章乘积求 sum; 该和是构造 llm_vote_tone_hw{track} = llm_vote_score_hw_sum{track} / sum_herd_weight{track} 的分子'
producer: pipeline\panel\encode.py (build_aggregation_dict, 三轨 for-loop 注册 agg[f''llm_vote_score_hw_sum{track}''] = (f''llm_vote_score_hw{track}'', ''sum'')) ; pipeline\audit\stata_audit.py (3e 加权均值恒等式校验, HW 分子=llm_vote_score_hw_sum{track})
upstream:
- 21_tone_llms (三家 LLM 多数投票 llm_vote_score{track})
- 24_herd_decay_processor (herd_weight{track})
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
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
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: 'Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy'
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
new_dois: []
---

## CORE

【构念与来源】
llm_vote_score_hw_sum 家族是银行-年面板层面的一个中间加权求和量, 它本身不是终端可解释测度, 而是构造跟风衰减加权 (herd-decay weighted, HW) LLM 语调 llm_vote_tone_hw{track} 的分子。上游链路分两段: 第一段是 stage 21 三家大语言模型 (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 两家走云雾中转, deepseek-v4-flash/deepseekv4 直连 api.deepseek.com) 逐篇文章多数投票, 产出 llm_vote_score{track} ∈ {-1, 0, 1} 的文章级情感极性分 (投票共识, 与均值-ensemble llm_models_avg_tone 是并排概念); 第二段是 stage 24 (herd_decay_processor) 承袭 Tetlock (2007, Journal of Finance) 开创的媒体语调测度传统中"重复报道会机械放大语调信号"的洞见, 对同一银行在时间窗内密集重复出现的雷同报道给予递减权重, 抑制"同一波媒体跟风炒作"对语调均值的机械放大效应, 产出文章级 herd_weight{track}; 三轨 (full/ctx/ss) 各自在其窗口文本上独立计算跟风衰减权重, 窗口宽窄不同直接决定"重复报道"判定所依赖的文本相似度口径不同, 这也是本族坚持三轨分别物化、而非单轨复用的构造动因之一——衡量对象 (银行实体在特定窗口内被报道的相似度) 必须与处理变量 (该窗口文本上的情感投票) 在同一文本粒度上匹配, 全文相似度并不能替代实体窗口内的相似度。llm_vote_score_hw_sum 家族即在 pipeline/panel/encode.py 的 build_aggregation_dict 里, 对每篇文章的 llm_vote_score{track} × herd_weight{track} 乘积, 按 (bank, year) 分组求和, 是一个纯粹的中间累加器, 单独看无经济含义, 必须结合同名分母列 sum_herd_weight{track} 才能还原出 HW 加权平均语调 llm_vote_tone_hw{track} = llm_vote_score_hw_sum{track} / sum_herd_weight{track}。

【方法学与计算】
计算发生在面板聚合阶段 (encode.py), 是逐年份文章级到银行-年面板的 groupby-sum 操作, 不涉及任何模型推断或重新调用 LLM API, 因此本族列是 $0 边际成本的纯后处理产物。源码里有一个需要写明的历史兼容分支: 若磁盘上仍是 v3.5.x 之前遗留的单列 herd_weight (未按三轨拆分), build_aggregation_dict 会退化为"三轨共用同一权重源"并打印 WARNING (此时 sum_herd_weight_full == sum_herd_weight_ctx == sum_herd_weight_ss, 是一种 fake 多轨), 生产口径 (stage 24 v3.6.0+) 已产出真正三轨独立的 herd_weight_full/herd_weight_ctx/herd_weight_ss, 本族三列在生产语料上应为真三轨、非退化。下游一致性由 pipeline/audit/stata_audit.py 的加权均值恒等式校验段 (3e) 兜底: 对每一轨分别验证 llm_vote_tone_hw{track} × 分母 ≈ llm_vote_score_hw_sum{track}, 分母优先取 valid-mask 列 sum_wd_hw_llm{track} (只统计 LLM 判定有效的文章), 缺失时回退物理分母 sum_herd_weight{track}, 恒等式不成立会记 FAIL 并使审计阶段退出码非零, 因此本族列在盘上若存在必然满足该会计恒等式, 可作为下游复算 llm_vote_tone_hw{track} 的可靠依据。三轨 full/ctx/ss 各自独立聚合、独立求和, 互不借用彼此分子分母, 是并排而非嵌套关系。

【文献定位】
本族的方法论根基有两层。分子的情感极性来自三家大语言模型的多数投票共识, 这一"多模型集成投票优于单模型"的做法呼应 Kamen & Kamen (2025) 关于 LLM ensemble 在内容分类任务上显著优于单一模型的发现, 以及 Schoenegger et al. (2024, Science Advances) 关于 LLM 集成预测能力可比拟人群智慧 (wisdom of the crowd) 的证据; 三家模型跨厂商 (OpenAI/Google/DeepSeek) 并排投票而非单家背书, 也部分回应 de Kok (2025, Management Science) 对生成式 LLM 用于会计/金融文本分析时应固定 temperature、留痕可复现的方法论建议 (本项目对应 stage 21 prompt v8 字节级冻结、temperature=0.0)。权重端的跟风衰减构造思想则直接承袭 Tetlock (2007, Journal of Finance) 开创的"媒体语调驱动投资者情绪"的测度传统——该文首次系统证明媒体文本语调可被量化为可预测股票收益的信号, 本项目在其基础上叠加 herd-decay 权重, 意在从"语调水平"测度进一步区分"独立信息增量"与"媒体跟风放大", 是对经典媒体语调测度框架的一种稳健性延伸。三轨 (full/ctx/ss) 各自独立的加权聚合口径彼此互为稳健性、不分主次, 且三轨严禁混入同一 over-identified 的 Hansen J 检验——full 轨对应 2026-06-29 起生效的 full-only 留篇门控主口径 (是否算作"一篇银行金科报道"仅看 llm_verified_full == True), ctx/ss 轨降级为 conditional-on-full 的测度稳健性轨, 行宇宙是 full 留篇集的子集; ss 轨的回退语义镜像 ctx 轨: 若某银行-金科词对在文章中不存在同句共现, ss_is_fallback 置 True 并退化为使用全文正文, 与 ctx 轨在无实体窗口时的回退处理完全对称。

## VAR: llm_vote_score_hw_sum_ctx

【变体差分】
本列是 llm_vote_score_hw_sum 家族的 ctx (context) 轨变体, 分子文本口径取 stage 14 (ctx_materializer) 物化的 content_ctx = 标题 + 银行实体上下文窗口 (而非全文正文), 情感投票 llm_vote_score_ctx 与跟风权重 herd_weight_ctx 均在此窗口文本上独立计算得出, 二者乘积再按 (bank, year) 求和构成本列。ctx 轨在 2026-06-29 起的留篇门控体制下属于 conditional-on-full 的稳健性测度轨: 行宇宙 (即哪些文章被计入求和) 由 full 轨的 llm_verified_full 门控决定, 但该子集内每篇文章各自在 ctx 窗口文本上重新做情感投票与权重计算, 并非简单复用 full 轨的数值。当某篇文章缺乏可识别的实体上下文窗口时, ctx_is_fallback 置 True, 此时 content_ctx 退化为全文正文, 该文章仍计入求和 (共享 n_articles 分母语义)。本列与 llm_vote_score_hw_sum_full、llm_vote_score_hw_sum_ss 是并排的互为稳健性关系, 三者各自 just-identified, 分析时禁止混入同一 over-identified Hansen J 设定; 如需验证 ctx 轨与 full 轨语调的跨轨道一致性, 应参照 stata_audit.py 中的 Pearson 相关性校验段, 而非直接对本列做数值比较 (本列是未除以分母的原始加权和, 量纲受分母权重规模影响, 不可跨轨直接相减或相除比较水平)。

ctx 轨的设计动机是在"全文正文可能夹杂与目标银行无关的段落"与"标题信息量有限"之间取一个折中窗口: 它比 full 轨更聚焦于银行实体真正被讨论的语境, 又比 ss 轨的严格同句窗口保留更多上下文线索, 因此在实证上常被用作 full 轨主结论的第一层稳健性检验。由于情感投票与跟风权重都是在窗口文本上独立算出而非从 full 轨截断得到, ctx 轨对权重规模 (herd_weight_ctx 的取值分布) 与 full 轨也可能存在系统性差异——例如某银行在同一波报道中反复出现于多篇文章的实体窗口附近, 跟风衰减会在 ctx 文本更短、重复模式更集中的情况下呈现出与 full 轨不完全相同的衰减轨迹。分析者若要复算 ctx 轨的加权平均语调, 必须使用同轨分母 sum_herd_weight_ctx (或 valid-mask 分母 sum_wd_hw_llm_ctx), 不能跨轨混用 full 轨的分母, 否则破坏本族三轨"各自 just-identified 并排"的识别结构。

## VAR: llm_vote_score_hw_sum_full

【变体差分】
本列是 llm_vote_score_hw_sum 家族的 full 轨变体, 也是三轨中的留篇门控主轨 (2026-06-29 起生效): 情感投票 llm_vote_score_full 与跟风权重 herd_weight_full 均在 content_full = 标题 + 全文正文的完整文本上计算, 且"某篇文章是否算作一篇有效的银行-金科报道"这一判定 (llm_verified_full == True) 仅以 full 轨为准, 决定了参与本族三列求和的文章行宇宙。换言之, full 轨不仅是三个并排稳健性轨之一, 还额外承担了行集合筛选的锚点角色: ctx 轨与 ss 轨的求和范围是 full 轨留篇集的子集, 而非各自独立筛选。本列在下游用于构造 llm_vote_tone_hw_full = llm_vote_score_hw_sum_full / sum_herd_weight_full, 是 P1 (bank_fintech_tone) 论文主线处理变量 llm_vote_tone_full 一族中的跟风衰减加权版本, 与逐篇等权的 vw (mention-density weighted)、mw (media-authority weighted) 版本互为稳健性并排、不分主次——三种权重方案 (VW/MW/HW) 各自独立构造分子分母, 经 stata_audit.py 3e 段逐一验证加权均值恒等式, 但严禁将三种权重方案混入同一 over-identified 工具变量设定中联合估计。

full 轨承担行宇宙锚点角色的实际含义是: 只有当一篇文章在全文正文层面被三家 LLM 多数投票判定为"确实是一篇关于目标银行与金融科技的报道" (llm_verified_full == True) 时, 该文章的 full/ctx/ss 三条记录才会同时被纳入 stage 21 之后的下游聚合; 这一门控逻辑在代码中有两处必须严格同步的副本——tone_llms.py 里的 df_filtered 构造, 以及 run_pipeline_function.py 里判断 stage 21 是否可跳过重跑的 _stage21_skip_is_compatible——若二者不同步翻转, 会导致跳过判定与实际留篇口径脱节, 要么误跳该重跑的付费阶段, 要么每次都误判为需要重跑而白白产生 LLM 调用费用。本列作为 full 轨分子, 因此不仅是一个稳健性测度, 还隐式携带了整个三轨面板行集合的定义权重, 在解释面板 n_articles、fintech_share 等口径列时也应一并对照。

## VAR: llm_vote_score_hw_sum_ss

【变体差分】
本列是 llm_vote_score_hw_sum 家族的 ss (same-sentence) 轨变体, 分子文本口径取 stage 14 物化的 content_ss = 标题 + 银行实体与金科词严格同句 (句内窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句) 共现的最窄文本切片, 情感投票 llm_vote_score_ss 与跟风权重 herd_weight_ss 均在该切片上独立计算。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行∧金科词的同句共现时, ss_is_fallback 置 True, content_ss 退化为全文正文, 该文章仍正常计入求和而非被剔除 (与 ctx 轨共享同一套"缺窗口即退化为全文、不丢行"的降级契约, FINTECH_AC 词典缺失时 *_is_fallback 会全体置 True 优雅降级为等同 full 轨的宽松口径)。ss 轨是三轨中窗口最窄、对无关上下文噪声最不敏感的测度, 与 ctx 轨、full 轨互为稳健性并排、不分主次, 行宇宙同样是 full 轨留篇门控集合的子集。需注意 stage 13 (cooccurrence_filter) 的硬过滤判据 (sentence_radius=1 邻近共现) 与本轨 ss_sentence_radius 是两个独立配置键, 前者决定文章是否进入 pipeline (丢行), 后者只决定 stage 14 物化 content_ss 时切片窗口宽窄 (不丢行, 只是文本口径不同), 二者不可混淆或相互替代。

由于 ss 轨窗口最窄, 参与情感投票与跟风权重计算的文本量通常显著小于 ctx 轨与 full 轨, 这意味着 herd_weight_ss 的分布形状 (以及由此驱动的本列求和规模) 可能与另外两轨呈现出不同的尾部特征——窗口越窄, 单篇文章的信息熵越低, 极端情感投票的绝对占比也可能更高, 因此 ss 轨语调在实证解释上更偏向"银行与金科被同时提及那一刻的即时情感", 而非全篇报道的整体基调。分析者如果同时报告三轨结果, 应将 full 轨作为主口径叙述, ctx/ss 轨仅作为附加的稳健性证据并列展示, 而不应把三者的系数差异解读为"哪个轨道更正确"——按 CLAUDE.md 铁律, 三轨互为稳健性、不分主次, 差异本身即是测度对文本窗口选择的敏感度信息, 而非误差来源。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
<!-- rendered-citations:end -->
