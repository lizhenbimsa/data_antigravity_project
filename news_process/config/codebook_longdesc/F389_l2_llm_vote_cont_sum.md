---
family_id: F389
columns:
- llm_vote_cont_sum_ctx
- llm_vote_cont_sum_full
- llm_vote_cont_sum_ss
unit: 无量纲连续情感得分之和 (bank-year 内逐篇 llm_vote_cont 求和, 值域随留篇篇数扩张, 非归一化占比)
formula: 'llm_vote_cont_sum{track} = groupby(bank, year)[llm_vote_cont{track}].sum(), 源列 llm_vote_cont{track} = llm_vote_score{track} (三家 LLM 多数投票离散码 {-1,0,+1}) × llm_agreement_rate{track} (三票一致率), 在 encode_sentiment 内合成'
producer: pipeline\panel\encode.py (build_aggregation_dict, L760 sum 聚合语句; 源列 llm_vote_cont{track} 由同文件 encode_sentiment 函数 L301 合成)
upstream:
- pipeline/sentiment/tone_llms.py
- pipeline/panel/encode.py
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: Federal Reserve Board FEDS Working Paper
  pages_or_artno: '2026-020'
new_dois: []
---

## CORE

【构念与来源】
llm_vote_cont_sum{track} 度量的是一家银行在给定年份内, 全部留篇报道所获三家大语言模型 (LLM) 投票共识连续情感分的加总。它的直接上游是文章级列 llm_vote_cont{track}, 后者是 encode_sentiment (encode.py) 在 tone_llms.py 产出的三家模型 (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 两家走 yunwu 网关, deepseek-v4-flash/deepseekv4 直连 api.deepseek.com) 逐篇多数投票结果之上合成的连续化版本: llm_vote_cont{track} = llm_vote_score{track} (三家多数投票得到的离散码, 取值 {-1, 0, +1}) × llm_agreement_rate{track} (三家打分中与多数票一致的票数占比, 即一致率), 而非三家各自输出连续分再取共识; encode.py 的 build_aggregation_dict (agg 段 B: "LLM 投票结果") 对同一 bank-year 组内的 llm_vote_cont{track} 直接调用 pandas groupby.sum, 与均值口径的 llm_vote_cont{track}/mean 及离散码求和口径的 llm_vote_tone_sum{track} 构成同一源列家族的不同聚合视角, 互为补充而非替代。sum 视角刻意保留了报道量的量纲信息: 同样的均值情感水平, 报道篇数多的银行 sum 值更大, 因而 llm_vote_cont_sum{track} 天然把"银行被多热烈地报道"与"报道情感有多正/负、多一致"两个维度耦合在一起, 更适合作为总暴露强度或总情感冲击量的代理变量, 而非纯情感水平的代理 (纯水平应看 llm_vote_tone{track}/mean(llm_vote_score{track}))。
本列所属的 LLM 投票机制是三家独立厂商模型对同一篇报道分别打分后取多数决共识 (离散码), 再用一致率对共识码做强度加权连续化, 而非单一模型的输出, 呼应 Kamen & Kamen (2025) 关于 LLM 集成在内容分类任务上系统性优于单模型的发现, 也符合 de Kok (2025) 在 Management Science 提出的会计/金融文本分析中生成式 LLM 使用规范 (temperature=0、prompt 版本冻结、结果可复现的缓存范式) —— 本仓库 stage 21 的 prompt v8 字节级冻结与 `_llm_cache.db` 缓存锚正是这一规范的工程化落地, 使 llm_vote_cont{track} 在同一缓存命中条件下具备逐位可复现性, 因而其求和聚合 llm_vote_cont_sum{track} 亦是确定性的, 不受重跑时随机种子或采样温度扰动。
【方法学与计算】
llm_vote_cont{track} 的取值域是 llm_vote_score{track} × llm_agreement_rate{track} 的乘积, 一致率 ∈ [0, 1], 离散码 ∈ {-1, 0, +1}, 故取值范围为 [-1, 1] 的连续区间, 但零值处兼容离散码为 0 (中性多数票) 与一致率恰为 0 两种来源; 它与纯离散的 llm_vote_score{track} (供 pos_frac/neg_frac/pos_count/neg_count 使用) 是派生而非并列关系 —— llm_vote_cont{track} 在离散共识码之上叠加了"三家模型意见有多一致"这一置信度维度, 一致率越高, 该篇连续分的绝对值越接近其离散码的极值, 反之三家分歧越大, 连续分越向 0 收缩。sum 聚合本身不做任何归一化或去噪处理: 它是逐篇 llm_vote_cont{track} 的算术和, 因此对留篇篇数 n_articles{track} 高度敏感, 分析时通常需要与该轨的篇数控制变量联合使用, 或改用 mean 口径 (llm_vote_cont{track}/mean) 剥离规模效应。三家模型各自的独立打分 ({short}_cont_sum{track}, short ∈ {gpt54nano, gemini31, deepseekv4}) 与共识列 llm_vote_cont_sum{track} 是 co-equal 互为稳健性的并列关系, 而非共识列由三家简单平均反推 —— 三家 per-model 子测度旨在验证共识结论不依赖单一厂商模型的系统性偏差, 呼应 Hansen (2026) 在无金标准场景下对 LLM 标注做一致性验证的设计思路 (κ/α 一致性度量)。
本家族三个成员列的唯一差分维度是文本轨道 (full/ctx/ss), 而非模型、阈值或权重梯度。三轨文本在 stage 14 (`ctx_materializer`) 物化: full = 标题+正文全文, ctx = 标题+银行/金科实体窗口, ss = 标题+银行与金科同句共现窗口 (窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句); 情感四阶段 (21 LLM/22 词典/23 BERT/24 herd_decay) 均无条件对三轨分别计算。三轨之间遵循「各自 just-identified 并排、互为稳健性、不分主次」的仓库铁律, 分析中禁止把三轨的 llm_vote_cont_sum 同时纳入同一 over-identified Hansen J 检验 —— 每一轨都是对同一构念的独立测量视角, 混用会人为制造工具变量个数虚增的伪超识别。留篇门控口径遵循 2026-06-29 起的 full-only 铁律: 一篇报道是否被计入"银行金科报道"样本, 唯一判据是 llm_vote_tone/llm_verified_full == True 的 full 轨结果; ctx 与 ss 轨的行宇宙是 full 留篇集的子集 (conditional-on-full), 各轨在此子集上分别计算自己的 llm_vote_cont{track} 并求和, 而非独立的门控标准。ss 轨的回退语义镜像 ctx 轨: 若某篇报道中银行与金科词未出现同句共现, 则 content_ss 回退为全文正文 (`ss_is_fallback=True`), llm_vote_cont_ss 仍照常计算并计入求和, 不会因未命中同句窗口而被剔除或置空; 这保证了三轨分母 (n_articles) 在缺失共现时仍可共享同一优雅降级路径, 不产生单边孤儿列。
【文献定位】
将 LLM 输出的连续情感分聚合为银行年度总量, 承接了 Tetlock (2007) 在 Journal of Finance 开创的"媒体情感度量投资者情绪"范式 —— 该文首次证明报纸语调可系统性预测股票收益, 建立了"文本→情感分数→加总为期间/主体级测度"的分析链条, 本列是该链条在 LLM 打分而非词典打分下的现代复现。采用三家 LLM 投票而非单一模型的设计, 直接呼应 Gilardi, Alizadeh & Kubli (2023) 在 PNAS 证明的 LLM 文本标注在多项任务上优于众包工作者的发现, 以及该文隐含的"多模型/多次运行取共识以降低单次采样噪声"的稳健性思路。本家族与词典法情感测度 (如 du_2022 系) 构成互补三角: LLM 投票捕捉语境化的语用情感, 词典法捕捉词汇层面的规则化情感, 二者并非相互替代而是各自独立锚定同一构念的不同侧面, 呼应 Du, Huang, Wermers & Wu (2022) 在 Review of Finance 中文金融情感词典构建工作里对中文财经文本情感度量特殊性 (双重否定、程度副词、政治词特殊语义) 的系统讨论。

## VAR: llm_vote_cont_sum_ctx

【变体差分】
本列取文本轨道 = ctx (标题+银行/金科实体窗口), 是家族内三轨并排测度之一, 而非 canonical 主轨。ctx 轨的文本物化发生在 stage 14, 取标题前置后围绕目标实体截取的局部窗口, 目的是让 LLM 打分聚焦于报道中直接涉及目标银行与金科议题的语句, 剔除同一篇报道中与银行-金科关系无关的段落对情感判断的稀释或污染。llm_vote_cont_ctx 的行宇宙是 full 轨留篇门控 (llm_verified_full==True) 之后的子集, 即先由 full 轨判定"这是一篇合格的银行金科报道", 再在该子集上用 ctx 文本重新跑三家 LLM 投票取得连续分, 因此 ctx 轨样本量恒不超过 full 轨。llm_vote_cont_sum_ctx 对 bank-year 内 ctx 轨逐篇连续分求和, 若某篇文章缺失有效 ctx 源列 (例如实体窗口无法可靠截取), 该篇由 encode.py 的 valid_agg 机制自动从求和中过滤跳过, 不会以 0 值污染加总。与 full 轨相比, ctx 轨情感往往因文本更聚焦而信噪比更高, 但样本损耗 (部分文章无法可靠定位实体窗口) 也可能使 ctx 轨求和值系统性小于同期 full 轨值, 这种差异本身即是构念稳健性检验的一部分, 而非测量误差。实证使用上, 若研究问题关心的是"报道对目标银行的直接叙事情感总量", ctx 轨往往比 full 轨更贴切; 但因其对实体窗口截取算法的依赖, 跨年度/跨报道风格比较时需留意窗口截取的稳定性, 建议与 full 轨结果并列报告而非单独依赖 ctx 轨下结论。

## VAR: llm_vote_cont_sum_full

【变体差分】
本列取文本轨道 = full (标题+正文全文), 是家族内三轨之一, 也是仓库 2026-06-29 起 full-only 留篇门控所锚定的轨道 —— 即"一篇报道是否被认定为合格的银行金科报道"这一判定唯一依赖 full 轨的 LLM 验证结果 (llm_verified_full==True), ctx 与 ss 轨的样本宇宙均是该判定结果的子集。llm_vote_cont_sum_full 因此是三列中样本覆盖最完整、n_articles_llm_valid_full 最大的一支, 在多数下游 paper 模块 (如 P1 bank_fintech_tone 的 treatment.primary) 中 full 轨情感测度 (llm_vote_tone_full) 被选为 canonical 主轨, 但这并不意味着 llm_vote_cont_sum_full 本身在统计推断意义上优先于 ctx/ss —— 三轨仍遵循「各自 just-identified 并排、互为稳健性、不分主次」的铁律, 只是 full 轨承担了留篇门控的技术锚定角色。全文轨的连续情感和值捕捉的是报道整体 (含标题、导语、正文全部段落) 的总体情感强度乘以篇数的联合效应, 相比 ctx/ss 更少受实体窗口截取误差影响, 但也更容易被报道中与银行-金科关系无关的段落 (如宏观经济背景介绍、其他银行的对比信息) 稀释单篇打分的针对性。由于 full 轨样本量最完整, llm_vote_cont_sum_full 在跨银行/跨年度比较中受留篇比例波动的影响相对最小, 是三轨中最适合作为总体情感暴露量代理变量的一支; 但正因其判据最宽松, 使用者仍须结合 n_articles_llm_valid_full 控制篇数规模效应, 避免将纯粹的报道量差异误读为情感水平差异。

## VAR: llm_vote_cont_sum_ss

【变体差分】
本列取文本轨道 = ss (标题+银行与金科同句共现窗口), 是三轨中判据最严格的一支: 只有银行实体名与金科相关词汇出现在同一句 (或 config/filtering.yaml::context_window.ss_sentence_radius 指定的 ±N 句窗口内, 默认 N=1) 时, 该句才被纳入 content_ss 用于 LLM 打分; 若某篇报道全文均无此类同句共现, content_ss 回退为全文正文 (镜像 ctx 轨回退语义), 并置 ss_is_fallback=True, 该篇仍照常计算 llm_vote_cont_ss 并计入求和, 不因未命中同句窗口而被剔除。ss 轨的行宇宙同样是 full 轨留篇门控之后的子集。相较 ctx 轨的"实体窗口"判据, ss 轨的"同句共现"判据更严, 理论上更能捕捉报道中银行与金科议题被直接并置讨论的语句情感, 是三轨中信噪比最高但潜在样本损耗 (依赖回退机制维持样本量) 也最显著的一支; llm_vote_cont_sum_ss 的取值因此对回退触发比例较敏感, 分析时建议同时参考 ss_is_fallback 的年度/银行分布, 以判断求和结果在多大程度上依赖回退到全文口径而非真正的同句窗口。当回退比例较高时, ss 轨在数值上会趋近于 full 轨 (因为回退即取全文正文), 此时 ss 轨作为稳健性检验的边际信息量下降; 反之当同句共现命中率高时, ss 轨最能体现"银行与金科被同时、直接谈论"这一严格构念, 是三轨中构念效度最高但样本代表性风险也最需要审视的一支。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Hansen, A. L. (2026). Validating large language model annotations. Federal Reserve Board FEDS Working Paper No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
