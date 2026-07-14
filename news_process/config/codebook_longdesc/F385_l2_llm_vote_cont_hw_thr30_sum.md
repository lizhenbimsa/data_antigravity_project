---
family_id: F385
columns:
- llm_vote_cont_hw_thr30_sum_ctx
- llm_vote_cont_hw_thr30_sum_full
- llm_vote_cont_hw_thr30_sum_ss
unit: 无量纲加权和 (银行-年层面, 由篇级"离散投票×一致率"连续语调乘以跟风衰减权重后加总而得, 非比率)
formula: 'llm_vote_cont_hw_thr30_sum{track} = Σ_i [ llm_vote_cont{track}_i × herd_weight{track}_thr30_i ], 求和遍历该银行-年内 llm_vote_score{track} 非缺失(即三家 LLM 投票有效)的篇级文章 i; llm_vote_cont{track}_i = llm_vote_score{track}_i × llm_agreement_rate{track}_i (离散共识票 {-1,0,1} 乘以三家一致率, 自然传播 NaN); herd_weight{track}_thr30_i 是 stage 24 在相似度阈值 τ=0.30 (敏感性网格备选值, 区别于生产基线 τ=0.35) 下重估的跟风衰减权重 (Tetlock 2011 RFS 思路: 与同银行同轨窗口内高相似文章越"扎堆", 权重越向 0 衰减)。'
producer: pipeline\panel\encode.py (build_aggregation_dict 聚合注册 + herd_sensitivity_grid 阈值网格; runner.py 步骤 3d 预生成 llm_vote_cont_hw_thr30{track} 篇级列); core\config.py::herd_sensitivity_grid (τ→tag 唯一编码 SSOT); pipeline\sentiment\herd_decay.py (stage 24, 产 herd_weight{track}_thr30 篇级列)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track} / llm_agreement_rate{track} / llm_vote_cont{track})
- 24_herd_decay.parquet (herd_weight{track}_thr30, 阈值敏感性网格篇级权重)
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.48550/arXiv.2511.15714"
  type: arxiv
  authors: "Kamen, A., & Kamen, Y."
  year: 2025
  title: "Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization"
  venue: "arXiv"
  vol: ""
  issue: ""
  pages_or_artno: "2511.15714"
new_dois: []
---

## CORE

【构念与来源】
本家族三列是银行-年面板上的一个中间加总(intermediate sum)测度族, 度量"在跟风衰减阈值 τ 取一个比生产基线更松的备选值 (0.30, 对应基线 0.35) 时, 该银行-年全部有效 LLM 投票文章的连续语调 × 跟风权重"的加权和。它不是最终的银行-年平均语调 (那是同名去掉 `_sum` 后缀、再除以对应权重和的比率列 llm_vote_tone_hw_thr30{track}), 而是这个比率的分子 — 加总后未除以分母的中间产物, 供审计/复算/稳健性重构使用, 也直接体现"抄稿/跟风程度"敏感性分析所依赖的构造链条。

母体构念链条分三层。第一层是 stage 21 三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 对每篇文章的情感多数投票 `llm_vote_score{track}` (离散 {-1, 0, 1}), 以及三家投票的一致率 `llm_agreement_rate{track}` (0~1, 三家全一致取 1, 分歧越大越低)。二者相乘得到 `llm_vote_cont{track}` — 一个"连续化"的语调测度: 方向仍由多数票决定, 但幅度按三家共识强度收缩, 一致率越低越向 0 靠拢, 这是把离散分类结果转成可直接加权平均的连续变量的标准做法(镜像 encode.py 中 vote_cont 的构造逻辑, 自然传播 <NA>/NaN, 而非把无效行坍塌为中性 0)。第二层是 stage 24 的跟风衰减 (herd decay): 对每篇文章, 在其所在银行-轨-窗口内计算与其余文章的文本相似度, 若相似度 ≥ 阈值 τ 视为"跟风/抄稿", 该文章的权重随相似文章数量增多而递减 (Tetlock 2011, *Journal of Finance* 的"重复报道稀释信息含量"直觉在中文财经新闻场景下的实现)。生产口径的相似度阈值基线为 τ=0.35 (对应无后缀的 `herd_weight{track}` 与 `llm_vote_cont_hw_sum{track}`), 但这一阈值本质是研究者自由选择的超参数, 没有理论上唯一正确的取值。第三层是本家族所在的阈值敏感性网格 (`herd_sensitivity_grid`, 2026-06-13 引入): 除基线 τ=0.35 外, 额外在 {0.25, 0.30, 0.40, 0.45} 上各重算一遍 herd_weight 与对应的加权和, `thr30` 即其中 τ=0.30 (相似度门槛比基线更松, 也就是更容易被判定为"跟风", 权重整体比基线更保守地向下压)。

【方法学与计算】
计算发生在篇级 (article-level) 到面板级 (bank-year-level) 的两阶段流水: 先在 stage 21/24 产出篇级列 `llm_vote_cont{track}` 与 `herd_weight{track}_thr30` (后者由 stage 24 `herd_decay.py` 在敏感性网格的每个 τ 上独立跑一遍相似度判定与权重衰减公式), 再由 `runner.py` 步骤 3d 把两者逐篇相乘得到篇级乘积列 `llm_vote_cont_hw_thr30{track}`, 最后 `encode.py::build_aggregation_dict` 在 groupby(target_bank, year) 聚合时对该乘积列取 `sum`, 得到本家族三列。留篇门控口径与全库一致: 一篇文章是否计入某银行-年的"有效报道"由 `llm_verified_full` 决定 (2026-06-29 起的 full-only 门控), ctx/ss 轨的行宇宙是 full 留篇集的条件子集, 各轨分子分母严格逐轨自洽, 不借用彼此的分母。求和过程中 NaN 语义是自然传播: 若某篇文章的 `llm_vote_score{track}` 因三家判定失败/未通过 verification 而缺失, 则该篇的 `llm_vote_cont{track}` 及乘积项亦为 NaN, `sum` 聚合按 pandas 语义自动跳过缺失值 (而非计为 0), 因此这一列本质是"有效篇章上的加权和", 分母口径的严谨匹配交由下游比率列 `llm_vote_tone_hw_thr30{track}` (= 本列 / `sum_wd_hw_thr30_llm{track}` valid-mask 分母) 负责, 本列自身不做除法。

【文献定位】
本家族方法学谱系融合了两条独立文献线索。其一是"抄稿/重复报道对信息含量的稀释"传统, 源自 Tetlock (2007, *Journal of Finance*) 对媒体情绪度量投资者信念的开创性框架, 并在 Tetlock (2011) 及后续跟风/羊群效应文献中发展出"高度相似的重复报道应降权而非等权计入"的处理思路 — 本家族的核心构造(herd_weight 随相似度阈值衰减)即是这一思路在中文银行金融科技新闻语料上的落地。其二是"用大语言模型多数投票替代单一模型标注、并以模型间一致率量化标注置信度"的 LLM-as-coder 方法学, 参考 de Kok (2025, *Management Science*) 对生成式 LLM 在会计与文本分析研究中温度参数冻结、提示词版本化等确定性重现规范的系统梳理, 以及 Kamen & Kamen (2025) 关于 LLM 集成多数投票作为内容分类稳健方案的论证。阈值 τ=0.30 属于本项目阈值敏感性网格 (基线 0.35, 备选 {0.25, 0.30, 0.40, 0.45}) 的一个格点, 设计动机与 Du et al. (2022, *Review of Finance*) 对政治词权重取值做 {0.0, 0.5, 1.0} 敏感性检验、以及本项目其余"梯子式"稳健性构造(规则消融、罕见词 cutoff、BERT 极端负面分位)同构: 证明主结论不依赖某一具体超参数选择。

## VAR: llm_vote_cont_hw_thr30_sum_full

【变体差分】
`_full` 轨: 篇级源文本为标题+全文正文 (prepend_title 拼接后的完整报道), 是本项目 P1 (`bank_fintech_tone`) 主处理变量 `llm_vote_tone_full` 所在轨道, 也是留篇门控 (`llm_verified_full`) 的口径基准 — 该银行-年内是否算作"一篇有效银行-金科报道"完全由 full 轨的 LLM 验证结果决定, ctx/ss 轨的行宇宙是这一集合的条件子集。因此 `llm_vote_cont_hw_thr30_sum_full` 的求和范围最宽(理论上是三轨中样本量的上界), 权重 `herd_weight_full_thr30` 的相似度比较窗口也是在全文层面进行(而非局限于实体窗口或同句窗口), 更容易捕捉到整篇文章层面的高度雷同(如通稿转发、多家媒体逐字转载同一篇通讯稿)。作为阈值敏感性网格的一格, 本列与基线 `llm_vote_cont_hw_sum_full` (τ=0.35) 及网格内其余三个阈值列 (thr25/thr40/thr45) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一个 over-identified 的 Hansen J 检验; 与 ctx/ss 两轨的对应列同样遵循三轨"禁混同一 Hansen J"的项目铁律, 三者是并列的稳健性口径而非可加合的分解。本列本身是求和后的分子中间量, 不能脱离匹配分母直接解读为"平均语调"。读者若要在稳健性表中呈现 full 轨阈值敏感性结果, 应把本列换算成比率(除以对应 τ 下的匹配权重和)后再与基线比率并列展示, 且应在表注中明确标出所用相似度阈值取值, 避免被误读为主回归的点估计本身。

## VAR: llm_vote_cont_hw_thr30_sum_ctx

【变体差分】
`_ctx` 轨: 篇级源文本为标题+目标银行/金科实体窗口截取的上下文片段, 而非全文。该轨的行宇宙是 full 轨留篇集的条件子集 (conditional-on-full 测度/稳健性轨, 2026-06-29 全文轨门控切换后的口径), 相似度比较也只在这段更短的实体窗口文本上进行, 因此 `herd_weight_ctx_thr30` 捕捉的是"围绕同一实体的表述雷同度", 与 `_full` 轨捕捉"整篇通稿雷同度"在构念上并不等价 — 两者是互为稳健性的并排口径, 不能因为数值上相关就相互替代或合并进同一回归右端。当某篇文章不存在可提取的实体窗口(即无有效 ctx 截取)时, 依上游 stage 14 的回退语义, 该篇的 `content_ctx` 退化为全文 body 且 `ctx_is_fallback=True`, 相应地其 `llm_vote_cont_ctx` 与 `herd_weight_ctx_thr30` 仍参与计算, 不额外剔除, 与 full 轨共享同一 `n_articles` 分母口径。本列与 `_full`/`_ss` 两轨、以及同轨内其余阈值网格列 (thr25/thr40/thr45/基线 thr35) 均为并排稳健性变体, 禁止混入同一个 over-identified Hansen J 检验; 阈值网格与三轨两个维度相互正交, 不做交叉笛卡尔积以外的额外合并解释。ctx 轨相似度比较窗口更短, 意味着相同的相似度阈值 τ=0.30 在 ctx 轨与在 full 轨下捕捉到的"雷同"实际上是不同尺度的现象, 二者数值不宜直接相减或比较绝对大小, 只能各自换算成比率后比较标准化系数的方向与显著性。

## VAR: llm_vote_cont_hw_thr30_sum_ss

【变体差分】
`_ss` 轨: 篇级源文本为标题+目标银行与金科词严格同句(±N 句窗口, 默认 N=1)共现的片段, 是三轨中判据最严格的一支, 镜像 `_ctx` 轨的回退语义 — 当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 与 ctx 共享同一 `n_articles` 分母, 该行仍计入求和(不因回退而剔除)。该轨的相似度判定 `herd_weight_ss_thr30` 仅在这段更短、更聚焦的同句窗口文本上比较, 理论上比 ctx/full 轨更容易因文本片段过短而出现"表面相似"(用词重合但语境不同)的假阳性跟风判定, 是三轨中最应谨慎解读的稳健性口径。`_ss` 轨的样本行宇宙同样是 full 轨留篇集的条件子集, 与 `_full`/`_ctx` 两轨、及同轨内阈值敏感性网格其余格点 (thr25/thr40/thr45/基线) 各自 just-identified 并排、互为稳健性不分主次, 禁止混进同一个 over-identified Hansen J 检验。作为求和而非比率, 本列在跨轨/跨阈值比较时应始终配合各自匹配的权重和分母 (`sum_wd_hw_thr30_llm_ss` 等) 换算成比率后再比较水平, 不宜直接比较原始加总值的大小(样本量、权重和量纲均随轨/阈值变化)。由于同句窗口通常比实体窗口更短、更易触发"用词重合但主题无关"的表面相似, `_ss` 轨在 τ=0.30 这一更松阈值下被判定为跟风的比例, 理论上会系统性高于 `_full`/`_ctx` 两轨, 解读结果时应把这一构造性差异与真实的抄稿/雷同程度区分开来, 不宜简单地把三轨数值差异等同于内容雷同程度的差异。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Kamen, A., & Kamen, Y. (2025). Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
<!-- rendered-citations:end -->
