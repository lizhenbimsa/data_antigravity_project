---
family_id: F387
columns:
- llm_vote_cont_hw_thr45_sum_ctx
- llm_vote_cont_hw_thr45_sum_full
- llm_vote_cont_hw_thr45_sum_ss
unit: 无量纲加权和 (跟风衰减权重 × 连续语调分, 银行-年层面对文章求和)
formula: 'sum_{i in bank-year} herd_weight_{track}_thr45(i) * llm_vote_cont_{track}(i);
  其中 llm_vote_cont_{track}(i) = llm_vote_score_{track}(i) * ar_v(i) 是三家 LLM 多数投票方向
  乘以连续强度权重的篇级连续语调分, herd_weight_{track}_thr45(i) 是相似度阈值取
  0.45 (而非生产基线 0.35) 时该篇文章的跟风衰减权重 (与其它高相似文章的重复扎堆
  程度成反比); 本列是该加权乘积在 (target_bank, year) 分组内的原始求和, 是下游
  llm_vote_cont_hw_thr45_{track} = 本列 / sum_wd_hw_thr45_llm_{track} (有效篇数匹配分母)
  这一银行-年加权平均连续语调的分子中间量, 本身不直接进回归。'
producer: pipeline\panel\encode.py (build_aggregation_dict 聚合字典注册, aggregate_panel
  执行 groupby sum) ; pipeline\panel\runner.py (步骤 3d 预算 llm_vote_cont_hw_thr45_{track}
  篇级加权列) ; pipeline\sentiment\herd_decay.py (stage 24 产 herd_weight_{track}_thr45
  篇级权重源) ; core\config.py::herd_sensitivity_grid (阈值网格 SSOT)
upstream:
- 21_tone_llms.parquet
- 24_herd_decay.parquet
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, Paul C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, Lily, & Peress, Joel
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting
    research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: "10.1609/aaai.v39i18.34120"
  type: "journal"
  authors: "Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C."
  year: 2025
  title: "Calibrating Large Language Models with Sample Consistency"
  venue: "Proceedings of the AAAI Conference on Artificial Intelligence"
  vol: "39"
  issue: "18"
  pages_or_artno: "19260-19268"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"剔除媒体跟风扎堆效应后的银行-年加权 LLM 语调强度", 在阈值敏感性
稳健性梯子上取相似度门槛 0.45 (thr45) 这一档。构念根基有两层: 第一层是三家
LLM (gpt54nano/gemini31/deepseekv4) 多数投票共识形成的 llm_vote_score (方向:
正/负/中性) 与连续强度 ar_v 的乘积 llm_vote_cont, 即篇级连续语调分, 度量口径
沿用 Tetlock (2007, JF) 以来"从大规模文本抽取投资者情绪/媒体语调"的经典范式,
但用三家大语言模型多数投票替代传统词典打分, 呼应 Kamen & Kamen (2025) 关于
LLM 集成投票在内容分类上优于单一模型的发现, 也符合 de Kok (2025, Management
Science) 对生成式 LLM 用于会计/金融文本分析的温度=0、prompt 冻结范式建议
(本仓库 stage 21 缓存键正是 prompt_version + temperature=0.0)。第二层是"跟风
衰减权重" herd_weight: 同一时间窗口内, 若多篇报道内容高度相似 (被判定为
互相抄稿/转载), 则被判定为"扎堆"的每篇文章权重按衰减函数下调, 避免单一事件
被多家媒体反复转载后在语调聚合中被过度加权, 这一思路呼应 Fang & Peress
(2009, JF) 关于媒体报道覆盖强度本身即是驱动股票收益横截面差异的独立信息
渠道 (而非中性的信息传递管道) 的发现 —— 若不同报道对同一事件的重复曝光被
简单等权计入语调聚合, 会把"媒体覆盖强度差异"错误地混进"媒体语调水平"的
测度中, 故须对扎堆文章降权以分离二者。跟风判定的核心参数是"相似度阈值": 两篇文章相似度达到该阈值
即被计入彼此的扎堆计数, 阈值越低越容易被判定为扎堆 (权重衰减更普遍), 阈值
越高则越少文章被判定为扎堆 (权重更接近未衰减的原始 1)。生产口径基线阈值取
0.35 (`herd_detection.similarity_threshold`, sentiment.yaml), thr45 家族取
0.45 —— 即比基线更宽松的相似度门槛, 只有相似度极高的文章才被判定为扎堆,
故 thr45 口径下同一批文章的平均权重通常不低于基线 thr35 口径 (被扎堆惩罚的
文章更少)。

【方法学与计算】
本列是"分子中间量", 不是最终面板回归列。计算链条: ① stage 21 (`21_tone_llms.py`
经 `tone_llms.py`) 产出三家 LLM 投票共识 llm_vote_score_{track} 与连续强度
ar_v, encode.py 相乘得到篇级 llm_vote_cont_{track}; ② stage 24
(`pipeline/sentiment/herd_decay.py`) 按 `core/config.py::herd_sensitivity_grid`
读取 `herd_detection.sensitivity_thresholds` (默认 [0.25, 0.30, 0.40, 0.45],
已剔除等于基线 0.35 的项), 对每个合法阈值 τ 产出篇级列
`herd_weight_{track}_thr{round(τ*100):02d}` (0.45 → tag='thr45'); ③
`pipeline/panel/runner.py` 步骤 3d 用该篇级权重与 llm_vote_cont_{track} 逐篇
相乘, 得到篇级加权列 `llm_vote_cont_hw_thr45_{track}`; ④ `encode.py::
build_aggregation_dict` 在 (target_bank, year) 分组上对该篇级加权列取 sum,
即本列 `llm_vote_cont_hw_thr45_sum_{track}`; 该列随后被
`_llm_denom('hw_thr45', 'llm', track, ...)` 匹配的有效篇数加权分母
(`sum_wd_hw_thr45_llm_{track}`) 相除, 得到银行-年层面阈值敏感性稳健版加权
连续语调 `llm_vote_cont_hw_thr45_{track}` (面板最终列)。分母采用"仅对 LLM
判断有效的文章求权重和" (valid-mask 分母, encode.py `_build_llm_valid_masked_weights`
所修), 避免把未获 LLM 有效判断的文章权重计入分母而系统性把加权均值拉向 0。
本家族三列是该"求和分子"环节的三轨版本 (full/ctx/ss), 供审计/复算面板比值时
核对分子分母是否匹配, 一般用户应直接消费最终比值列而非本家族三列; 但因其
承载"阈值取 0.45 下的原始加权强度总量", 在稳健性附表脚注披露"总样本强度未
因换阈值而剧烈跳变"时具有独立诊断价值。

【文献定位】
本家族的双层构念 (LLM 投票语调 × 跟风衰减权重) 分别锚定两条独立文献线:
语调测度本身沿 Tetlock (2007) 开创的媒体文本情绪定量化传统, 并以三家大语言
模型多数投票取代传统词典/单模型方法, 方法学上呼应 Kamen & Kamen (2025) 的
LLM 集成投票研究与 de Kok (2025, Management Science) 关于生成式 LLM 在会计
金融文本分析中的规范化使用建议; 跟风/重复报道的权重折损设计呼应 Fang &
Peress (2009, JF) 对媒体报道强度本身构成独立信息渠道、简单等权聚合会把
覆盖强度差异误记为语调差异这一风险的关注。阈值敏感性网格本身
(0.25/0.30/0.40/0.45 与基线 0.35 并排) 是一种规格稳健性设计: 各阈值档各自
just-identified 并排, 互为稳健性、不分主次, 用于证明"相似度多高算抄稿"这一
研究者自选门槛不驱动主结论, 禁止把不同阈值档的加权语调混进同一 over-identified
Hansen J 检验。 至于篇级连续语调分中强度因子的取法, Lyu 等 (2025) 通过系统比较多种置信度来源发现, 由多次采样输出之间的一致性导出的置信度, 在校准性上优于模型自报置信度与 logit 概率, 为本族以三家投票一致率而非模型自报分数充当篇级连续权重提供了方法学依据。迁移边界须标明: 该文的一致性取自同一模型正温度下的重复采样, 而本项目 temperature=0.0 且不重复采样, 一致率来自三家异构厂商模型的跨模型投票, 该文并未检验此种跨模型一致率的校准性质, 其英文推理/问答基准任务亦不涉及 τ=0.45 档的跟风衰减加权与银行-年加总。
## VAR: llm_vote_cont_hw_thr45_sum_ctx

【变体差分】
本列取三轨中的 ctx (上下文窗口) 轨: 篇级文本来源于 stage 14 物化的
`content_ctx` (标题 + 目标银行实体窗口拼接文本), 而非全文 body。留篇门控
(2026-06-29 起) 采用 full-only 口径 —— 是否判定某篇报道为"一篇有效的银行×
金科报道"只看 `llm_vote_score_full` 是否 `llm_verified_full == True`; ctx
轨的行宇宙是 full 留篇集合的子集, 在该子集内 per-track 重新解析并计算
`llm_vote_score_ctx`/`ar_v_ctx`/`llm_vote_cont_ctx`, 进而按上下文窗口内的
文本重新走一遍 LLM 投票与 herd 相似度判定, 得到独立于 full 轨的
`herd_weight_ctx_thr45` 与本列 `llm_vote_cont_hw_thr45_sum_ctx`。ctx 轨与
full 轨、ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 三轨结果不应
混入同一 over-identified Hansen J 检验; ctx 轨的价值在于验证"聚焦实体上下文
窗口而非整篇" 是否改变阈值敏感性结论, 若 ctx 与 full 在 thr45 档上方向、量级
一致, 则说明结论不依赖是否纳入全文其余段落的文本噪声。此外, 由于 herd 相似度
判定是在窗口化文本而非全文上进行, ctx 轨对"同一事件多篇报道扎堆"的判定基准
也随之收窄到实体窗口范围, 与 full 轨的扎堆判定可能出现不完全重合的分组结果:
即便两篇文章全文差异不大, 若各自实体窗口内的措辞不同, ctx 轨可能不判定为
扎堆而 full 轨判定为扎堆, 反之亦然。这一差异本身不是缺陷, 而是三轨"各自
just-identified 并排、互为稳健性"设计的自然结果 —— 每条轨道用自身文本口径
独立完成从留篇判定 (继承自 full 轨门控) 到语调计算再到扎堆权重计算的全链条,
不借用其他轨道的中间量。审计/复算本列时应核对其伴生分母列
`sum_wd_hw_thr45_llm_ctx` 是否与本列同轨同阈值, 二者相除方得到面板最终列
`llm_vote_cont_hw_thr45_ctx`, 不可与 full/ss 轨的分子分母交叉相除。

## VAR: llm_vote_cont_hw_thr45_sum_full

【变体差分】
本列取三轨中的 full (全文) 轨, 是三轨中的 canonical/门控轨: 篇级文本 = 标题
+ 正文全文 (`content_full`), 留篇判定 (`llm_verified_full`) 与最终面板行
宇宙均以本轨为准 (full-only 门控, 2026-06-29 起生效, 两处门控副本
`tone_llms.py::df_filtered` 与 `run_pipeline_function.py::
_stage21_skip_is_compatible` 必须同步)。因此 `llm_vote_cont_hw_thr45_sum_full`
的分子求和覆盖的是该银行-年全部被判定为有效报道的文章, 其对应的
`herd_weight_full_thr45` 权重也在全文文本上重新计算相似度扎堆判定。作为
门控轨, 该列在阈值敏感性稳健性表中通常是主回归 DV (`llm_vote_cont_hw_full`,
基线阈值 0.35) 的对照锚点: thr45 与基线 thr35、以及 thr25/thr30/thr40 等其余
档位在 full 轨上并排比较, 用以证明主结论方向与显著性不随该门槛取值系统性
翻转; 与 ctx/ss 轨互为稳健性、不分主次, 禁止混入同一 Hansen J。full 轨的另一独特之处
在于它是唯一直接决定"这篇文章是否算作一篇有效银行×金科报道"的轨道: 无论 ctx/ss
轨自身的相似度判定或有效性判定结果如何, 只要 `llm_verified_full` 为 False, 该篇
文章即不进入任何轨道的分母/分子; 反之若 `llm_verified_full` 为 True 但该篇在
ctx/ss 轨上因文本退化 (如无银行∧金科同句触发 ss 回退) 而与其他轨道口径不同, 三轨
仍各自独立完成 herd 相似度判定与阈值敏感性加权。审计本列时, 应确认其分母伴生列
`sum_wd_hw_thr45_llm_full` 与本列同为 thr45 阈值、同为 full 轨, 相除后得到的
`llm_vote_cont_hw_thr45_full` 才是可直接进入 Stata 稳健性附表 (逐 τ 网格重跑主
回归) 的最终面板列; 本列 `_sum_full` 自身只是求和中间量, 不应被误当作已归一化
的语调水平值直接解释或作图。

## VAR: llm_vote_cont_hw_thr45_sum_ss

【变体差分】
本列取三轨中的 ss (银行∧金科同句) 轨: 篇级文本来源于 stage 14 物化的
`content_ss` (标题 + 目标银行与金科词严格同句 ±N 窗口拼接文本, N 由
`config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1)。
若某篇文章不存在银行∧金科同句共现, 则 ss 轨回退语义镜像 ctx 轨: `content_ss`
退化为全文 body, 对应的 `ss_is_fallback` 标记为 True, 且与 ctx 轨共享同一个
`n_articles` 分母口径; 在 ss 轨上重新走 LLM 投票、连续强度与 herd 相似度判定
得到 `herd_weight_ss_thr45`, 与 `llm_vote_cont_ss` 逐篇相乘并在 (target_bank,
year) 上求和, 即为本列。ss 轨是三轨中对"文本窗口最窄、语境最贴近银行-金科
直接关联句"的稳健性检验: 与 full/ctx 轨互为稳健性、不分主次, 各自
just-identified 并排, 阈值敏感性网格 (thr25/30/40/45 与基线 thr35) 在 ss 轨
上同样各自独立, 均不应混入同一 over-identified Hansen J 检验。ss 轨的回退语义
需特别注意: 当 `ss_is_fallback` 为 True 时, 该篇文章在 ss 轨上实际消费的是与
full 轨相同的全文文本 (退化行为), 但其 herd 相似度判定与阈值敏感性权重计算
仍以 ss 轨自身独立执行, 而非直接复制 full 轨的 `herd_weight_full_thr45`; 也就是
说即便个别文章文本退化为全文, ss 轨整体的扎堆分组仍是在 ss 轨的行宇宙 (即
full 留篇集合的子集) 内重新划分, 与 full 轨的分组结果不必然一致。审计本列时,
应核对伴生分母列 `sum_wd_hw_thr45_llm_ss` 是否同为 ss 轨、同为 thr45 阈值, 相除
后方得到面板最终列 `llm_vote_cont_hw_thr45_ss`; 因 ss 轨样本覆盖面通常比 full/ctx
更窄 (仅同句共现或回退全文的文章参与), 在小样本银行-年格 (T=2 开发环境下尤其
明显) 上该列及其比值列可能出现更多零方差或缺失, 属预期退化而非错误。

<!-- rendered-citations:begin -->
Tetlock, Paul C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Fang, Lily, & Peress, Joel. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lyu, Q., Shridhar, K., Malaviya, C., Zhang, L., Elazar, Y., Tandon, N., Apidianaki, M., Sachan, M., & Callison-Burch, C. (2025). Calibrating Large Language Models with Sample Consistency. Proceedings of the AAAI Conference on Artificial Intelligence, 39(18), 19260-19268. https://doi.org/10.1609/aaai.v39i18.34120
<!-- rendered-citations:end -->
