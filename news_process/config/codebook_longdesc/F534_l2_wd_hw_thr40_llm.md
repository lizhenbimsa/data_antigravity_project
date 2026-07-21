---
family_id: F534
columns:
- sum_wd_hw_thr40_llm_ctx
- sum_wd_hw_thr40_llm_full
- sum_wd_hw_thr40_llm_ss
unit: 无量纲权重和 (跟风衰减权重 herd_weight 在给定敏感性阈值下按银行-年求和, 非情感分数本身)
formula: 'sum_wd_hw_thr40_llm_{track} = Σ_i herd_weight_{track}_thr40(i), 对属于该银行-年 (bank×year) 且 llm_vote_score_{track}(i) 非缺失的全部文章 i 求和; herd_weight_{track}_thr40 由 stage 24 (herd_decay_processor) 在敏感性阈值 τ=0.40 下逐篇算出, 经 runner.py 步骤 3d-2 生成中间列 _wd_hw_thr40_llm{track} = herd_weight_{track}_thr40.where(llm_vote_score_{track}.notna()) 做同域截断 (分子分母同域), 再由 encode.py 聚合 agg[f"sum_wd_hw_{tag}_llm{track}"] = (f"_wd_hw_{tag}_llm{track}", "sum") 按银行-年求和产出本列'
producer: pipeline\panel\encode.py ; pipeline\panel\runner.py
upstream:
- pipeline\sentiment\herd_decay.py (stage 24, 由根级 thin shim 24_herd_decay_processor.py 调用, herd_weight_{track}_thrNN 敏感性网格来源)
- pipeline\sentiment\tone_llms.py (llm_vote_score_{track} 三家 LLM 多数投票分数, 定义"同域"掩码)
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: 'When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks'
  venue: Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating Large Language Model Annotations
  venue: 'FEDS Working Paper No. 2026-020, Federal Reserve Board'
new_dois: []
---

## CORE

【构念与来源】
本家族 F534 的三个列 (`sum_wd_hw_thr40_llm_ctx`/`_full`/`_ss`) 不是情感测度本身, 而是"跟风衰减 (herding decay) 加权 LLM 语调"这条测度链上的权重分母(weight-denominator, 命名前缀 `wd`)三轨求和, 在阈值敏感性网格 (sensitivity grid) 的 τ=0.40 一格上取值。它服务于 Stata 面板阶段 (根级 `.do` 模板 "HW Tone" 区块) 把 `llm_vote_score_hw_thr40_sum{track}` (加权分子和) 除以本列 (加权分母和), 还原出银行-年层面"跟风衰减加权平均 LLM 语调"这一稳健性测度。构念背景是: 银行相关报道在真实新闻生态中并非彼此独立——若某家银行某一年被多篇高度相似 (可能互相转载、跟风改写) 的报道反复覆盖, 简单等权平均会让"多篇雷同稿件"获得与"多篇独立观点"同等的权重, 从而人为放大或稀释语调均值。跟风衰减处理 (stage 24 `herd_decay_processor`) 借鉴社会传染/信息瀑布文献对"重复暴露信号"的折价思路, 对每篇文章按其与同银行-年内其他报道的文本相似度衰减打一个 ∈(0,1] 的权重 `herd_weight`——越像"抄稿/跟风稿"权重越低、独立稿件权重越接近 1。

【方法学与计算】
本家族对应的敏感性网格键为 `thr40`, 即把"判定两篇报道构成跟风关系"的相似度门槛设为 0.40 (40%), 这是 `config` 里 `herd_detection.sensitivity_thresholds` 网格中的一格 (相邻还有更严/更松的门槛档位, 各自产出同构的 `sum_wd_hw_thr{NN}_llm{track}` 列族, F534 只覆盖 thr40 这一格)。计算链路: stage 24 先按 τ=0.40 逐篇算出 `herd_weight_{track}_thr40`; runner.py 步骤 3d-2 只对"LLM 投票主测度族 (score/cont)"生成敏感性加权列 (词典/BERT 等其余测度族不进入该网格, 避免网格 × 全测度族组合导致列数爆炸), 用 `.where(llm_vote_score_{track}.notna())` 把权重截断到与分子 `llm_vote_score_{track}` 完全同域的样本上, 得到文章级中间列 `_wd_hw_thr40_llm{track}`; encode.py 再按银行-年分组对该中间列取 `sum`, 产出面板级 `sum_wd_hw_thr40_llm{track}` (即本家族三列)。这个"分子分母同域"的设计 (源码注释标注为 encode-01 fix, 2026-06-10) 是关键正确性约束: 只要分子 `llm_vote_score_hw_thr40_sum{track}` 与分母 `sum_wd_hw_thr40_llm{track}` 在同一批文章上求和, 相除得到的加权均值就是良定义的; 若分母纳入了分子缺失的文章 (例如 LLM 三家投票未能达成共识、`llm_vote_score` 为 NaN 的稿件), 加权均值会系统性被稀释。三轨 (full/ctx/ss) 各自独立走一遍该链路——full=标题+正文全文, ctx=标题+银行/金科实体窗口, ss=标题+银行∧金科词同句(±N 句)窗口, 无银行∧金科同句共现时回退为全文 body 且 `ss_is_fallback=True` (回退语义镜像 ctx)——三轨口径完全对称, 三个 `herd_weight_{track}_thr40` 各自独立计算、各自独立求和, 彼此不共享同一个权重值。

【文献定位】
本家族测度所服务的"用词典/LLM 语调衡量媒体报道对银行的态度"这一构念传统上溯至 Tetlock (2007, *Journal of Finance*) 对媒体语调与股票市场关联的开创性研究, 以及 Du, Huang, Wermers & Wu (2022, *Review of Finance*) 针对中文金融文本构建的领域专属情感词典方法论——本项目多套词典测度族与本家族所属的三轨 LLM 测度族互为稳健性对照, 均遵循"用一个可复现权重方案压低雷同报道对面板均值的影响"这一处理原则。用 LLM 而非纯词典做逐篇情感判定的方法论基础参照 Gilardi, Alizadeh & Kubli (2023, *PNAS*) 对 LLM 文本标注质量优于众包标注者的系统评估, 以及 de Kok (2025, *Management Science*) 对会计/金融研究中生成式 LLM 使用规范 (含 temperature=0、prompt 版本冻结等可复现性约束) 的方法论建议——本项目 stage 21 LLM 情感三家投票管线 (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 的 prompt 冻结与缓存命中确定性设计正对齐这一规范。跟风衰减权重本身的敏感性网格设计思路呼应 Hansen (2026, FEDS Working Paper) 关于"无金标准场景下 LLM 标注结果需要多重稳健性验证 (含参数网格敏感性)"的方法论主张——本家族的 thr40 只是网格中一格, 与相邻门槛档位一起构成"结论不依赖单一相似度阈值取值"的证据链, 这一梯子设计与 Loughran & McDonald (2011, *Journal of Finance*) 提倡的"文本分析构念须交叉验证以防方法伪影"的一般性原则一致。

## VAR: sum_wd_hw_thr40_llm_ctx

【变体差分】
本列取 ctx 轨: 上游 `herd_weight_ctx_thr40` 在"标题 + 银行/金科实体窗口"文本 (`content_ctx`, stage 14 `ctx_materializer` 物化) 上计算相似度与衰减权重, 掩码来源 `llm_vote_score_ctx` (LLM 三家在 ctx 轨上的多数投票分数)。与 `_full` 轨相比, ctx 轨的跟风相似度判定只看实体窗口片段而非全文, 因此对"报道结构不同但核心表述雷同"的跟风稿更敏感 (窗口截断放大了重复表述在全文中的相对权重), 也更能过滤掉与银行/金科主题无关的正文噪声对相似度判定的干扰。ctx 与 full、ss 三轨在本项目口径下各自 just-identified 并排, 互为稳健性、不分主次, 禁止把三轨权重和混进同一个 over-identified Hansen J 检验框架——下游 Stata 回归应分别用各自轨道的分子分母配对相除, 不得跨轨相除或跨轨相加。留篇门控口径 (2026-06-29 起) 以 `llm_verified_full == True` 为准, 即"是否算作一篇有效的银行金科报道"只看 full 轨判定; ctx 轨的本列因此是 conditional-on-full 的稳健性/测度轨, 其行宇宙 (银行-年样本) 是 full 轨留篇集的子集, 但求和口径、权重计算、敏感性阈值均按 ctx 轨自身独立进行, 不借用 full 轨的权重值或分母。当某银行-年在 ctx 轨上 `llm_vote_score_ctx` 全部缺失时, 本列对应求和结果为 0 或缺失 (取决于分组聚合的空集处理), 使用时应结合同批次的 ctx 轨分子列一并判读, 避免把"分母为 0/缺失"误读为"跟风程度为 0"。

## VAR: sum_wd_hw_thr40_llm_full

【变体差分】
本列取 full 轨 (canonical 主轨): 上游 `herd_weight_full_thr40` 在"标题 + 正文全文" (`content_full`) 上计算相似度与衰减权重, 掩码来源 `llm_vote_score_full`。full 轨是本项目留篇门控 (2026-06-29 起) 的唯一判据轨——`llm_verified_full == True` 决定一篇文章是否被计入"银行×金科报道"样本全集, 因此本列所对应的分母求和是三轨中样本覆盖面最完整、也是各 paper 主线 treatment (如 P1 `llm_vote_tone_full`) 所直接依赖的权重来源。与 ctx/ss 两个"实体窗口/同句窗口"截断轨相比, full 轨的相似度判定基于全文, 更能捕捉"整体行文结构与用词高度雷同"的跟风稿 (例如通稿转载、同源改写), 但也更容易被与银行/金科主题无关的正文段落 (背景介绍、行业综述等雷同套话) 拉高相似度分数, 从而把并非真正跟风的报道也判低权重——这是 full 轨相对 ctx/ss 轨的已知取舍, 在解读跨轨差异时应纳入考量。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 本列与 ctx/ss 两个同名列禁止混入同一个 over-identified Hansen J 检验; Stata 端 HW Tone 加权均值构造须用本列与同轨分子列 (`llm_vote_score_hw_thr40_sum_full`) 配对相除, 不得跨轨配对。留篇门控直接锚定 full 轨的另一层含义是: 本列的分母求和相较 ctx/ss 两轨更少受"实体窗口截断/同句窗口回退"这类中间处理步骤引入的额外噪声影响, 是三轨里最接近"原始报道整体重复度"这一朴素直觉的权重口径, 因此在稳健性梯子的呈现顺序上通常作为基准参照, 但这并不意味着其在识别策略上优先于 ctx/ss——三者仍是并排关系。

## VAR: sum_wd_hw_thr40_llm_ss

【变体差分】
本列取 ss 轨: 上游 `herd_weight_ss_thr40` 在"标题 + 银行∧金科同句 (±N 句窗口, `config/filtering.yaml::context_window.ss_sentence_radius` 默认 1) 窗口"文本 (`content_ss`) 上计算相似度与衰减权重, 掩码来源 `llm_vote_score_ss`。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科词在同一句内共现的窗口, `content_ss` 回退为全文 body, 对应 `ss_is_fallback=True`, 此时该篇在 ss 轨上的跟风相似度判定实质上退化为对全文的判定 (与 full 轨趋同), 而非缺失或置零——这与"银行侧=否定+短名过滤、金科侧=裸 AC 607 词"的判定不对称口径共同决定了 ss 轨样本在多大程度上真正体现"同句紧邻共现"这一最严格窗口。ss 轨是三轨中文本片段最短、窗口最紧的一档, 相似度判定对局部用词的敏感度最高 (短窗口下少量重合词就可能推高相似度), 因此 thr40 (40% 相似度门槛) 在 ss 轨上被判定为"跟风"的样本占比与 ctx/full 两轨在同一阈值下的占比未必可比——三轨阈值虽数值相同但作用的文本尺度不同, 不应把三轨在同一 thr 标签下的求和结果直接横向比较绝对水平, 只应比较各自轨道内部随阈值网格 (thr 更严/更松档位) 的变化趋势是否一致, 以此作为"跟风衰减处理不依赖单一阈值取值"的稳健性证据。ss 与 ctx、full 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一个 over-identified Hansen J 检验; 行宇宙同样受 full-only 留篇门控约束, 是 full 轨留篇集的子集, 但求和与权重计算完全按 ss 轨自身独立完成。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Hansen, A. L. (2026). Validating Large Language Model Annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
