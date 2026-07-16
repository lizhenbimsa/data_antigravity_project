---
family_id: F201
columns:
- disag_fin_sent_zh_ctx
- disag_fin_sent_zh_full
- disag_fin_sent_zh_ss
unit: 无量纲分歧指数, 取值区间 [0, 1]
formula: "disag = sqrt(1 - ((P - N) / (P + N))^2); P = fin_sent_zh BERT 逐篇正类概率在 (bank, year, track) 内的均值, N = 逐篇负类概率均值"
producer: news_process/pipeline/panel/runner.py::main (步骤 8b disag, 单 BERT 概率均值) ; 上游情感码 news_process/pipeline/panel/encode.py (BERT 三分类概率均值聚合 {short}_pos/{short}_neg)
upstream:
- 23_tone_berts.parquet (fin_sent_zh 三分类概率/argmax)
- 24_herd_decay.parquet (df_exploded, verified article×bank 级)
citations:
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1007/978-3-030-32381-3_16
  type: book
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science, Vol. 11856"
  pages_or_artno: 194-206
  no_doi_ack: whitelist-pool-F201
  alt_link: "https://link.springer.com/chapter/10.1007/978-3-030-32381-3_16"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"某家银行某一年内、围绕其金融科技活动的新闻报道在情感极性上有多分裂", 即分歧 (disagreement) 或极化 (polarization) 强度, 而非情感的平均高低。构念的落点是: 当一家银行的相关报道既有明显看多的正面篇章、又有明显看空的负面篇章并存时, 舆论对该银行数字化前景的判断是撕裂的; 反之若报道口径高度一致 (清一色正面或清一色负面), 则舆论是同向的。分歧本身携带独立于均值语调的信息——两家银行可以拥有完全相同的净语调均值, 却对应截然不同的意见结构。金融学文献早已把意见分歧确立为一个与资产定价、成交量、风险溢价系统相关的一阶状态变量: Cookson 与 Niessner (2020) 从投资者社交网络直接测度分歧并刻画其来源分解, Carlin、Longstaff 与 Matoba (2014) 证明分歧对资产价格与预期收益具有可观测的解释力, Li 与 Luan (2025) 则进一步把基于新闻文本的投资者分歧与股票收益联系起来。本家族把这一构念从投资者层面平移到"银行×年"的媒体报道层面, 作为舆论环境的极化刻画。

【方法学与计算】
指标以三家 BERT 情感模型之一的 fin_sent_zh 为分类引擎。上游 stage 23 (23_tone_berts) 对每篇纳入篇章给出三分类 (正/中性/负) softmax 概率; encode 层把每篇的正类概率、负类概率作为篇章级信号, runner 在 8b 步聚合时对给定 (bank, year, track) 三元组取均值——P 为该格内所有篇章正类概率的均值 (即 fin_sent_zh_pos 列), N 为负类概率的均值 (即 fin_sent_zh_neg 列)——再按闭式公式 disag = √(1 − ((P − N) / (P + N))²) 计算。须强调 P、N 是逐篇概率的均值, 而非对 argmax 硬标签的篇数计数: 单 BERT 分歧轨消费的是概率均值列 (fin_sent_zh_pos / fin_sent_zh_neg), 并不消费同样存在的 argmax 计数列 (fin_sent_zh_pos_count / fin_sent_zh_neg_count)——这一点与同族的 LLM 投票分歧轨 (走 pos_count 篇数计数) 存在实现口径差异, 使用时不可混淆。该式等价于把净极性比例 r = (P − N)/(P + N) ∈ [−1, 1] 映射到 √(1 − r²): 当正、负类平均概率相等 (意见最撕裂) 时 r = 0, disag 取最大值 1; 当报道情感一边倒 (N ≈ 0 或 P ≈ 0) 时 |r| → 1, disag 趋近最小值 0。因此该指标是一个纯粹的"极性平衡度", 与总报道量、与净语调方向都正交, 只对"多空并存的程度"敏感。因每篇三类概率满足 正 + 中性 + 负 = 1, 中性类的概率质量会同时直接压低 P 与 N 两个均值 (它进入 P、N 的构成结构而非仅间接作用), 从而在多空并存程度既定时把 disag 的两个输入按比例缩小; 分母 P + N 为 0 (该格内正负类平均概率均为 0, 极端情形) 时取 NaN 而非 0, 与全流水线"无报道标缺失、不标零"的口径一致。fin_sent_zh 作为 BERT 三模型 (finbert_cn / fin_sent_zh / finbert2) 之一, 其概率化情感判定的中文金融情感效度可追溯到 Sun 等 (2019) 的 BERT 微调范式与 Todd 等 (2024)、Ma 等 (2025) 对中文金融文本情感测度的方法学综述。

【文献定位】
本家族在稳健性谱系中的定位是"以 BERT 正负类概率均值构造的意见分歧轨", 与以 LLM 投票、以词典打分构造的同名分歧指标互为稳健性、不分主次。三条 BERT 模型各自派生的分歧列并排, 各自 just-identified, 严禁混进同一 over-identified Hansen J——这是全项目对 per-model / 三轨 / 双轨嵌入一以贯之的识别铁律。就构念区分而言, 本家族与 Janis-Fadner 系数 (同在 runner 7i 步) 、与 concern_score 属于不同维度: J-F 在正负之外再引入报道总量 t 做归一, concern_score 是覆盖度与净情感比的乘积, 而本 disag 家族刻意剥离总量、只留极性平衡; Cookson 与 Niessner (2020) 意义上"分歧的来源"在此被压缩为一个可回归的标量。fin_sent_zh 轨与 finbert_cn / finbert2 轨的差别仅在分类器权重, 三者共享同一 disag 闭式与同一聚合口径, 因而其系数差异可被解读为"测量方法敏感性"而非构念漂移。

## VAR: disag_fin_sent_zh_full

【变体差分】
本列是 full 轨变体, 也是本家族的 canonical 轨。full 轨的篇章文本 = 标题 prepend + 全文正文 (content_full), 是全项目留篇门控的唯一裁决轨: 一篇报道是否被判为"一篇银行金融科技报道"只看 full 轨的 verified 结果 (full-only 门控, 2026-06-29 定稿); ctx/ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。因此 disag_fin_sent_zh_full 的 P、N (正、负类概率均值) 建立在最完整的篇章集合之上, 统计功效最高, 是论文主表引用该家族时的默认口径。数值上, 它对 fin_sent_zh BERT 在 full 文本上给出的逐篇正类概率、负类概率分别取该 (bank, year) 格内的均值得到 P、N, 代入 √(1 − ((P − N)/(P + N))²)。与 ctx/ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混同一 over-identified Hansen J。与 finbert_cn_full / finbert2_full 同名列的差别仅在 BERT 分类器: 本列锁定 fin_sent_zh 模型, 三 per-model 分歧列 co-equal, 任一模型缺席只掉自身族而不连坐 (per-model 独立降级, 非 co-primary 嵌入的 both-or-neither)。dev 语料 T=2、篇数极少时该列可能在多数格上退化为 0 或 NaN, 属预期的小样本表现, 生产 T=19 语料下方能反映真实极化结构。需要强调的是, 本列衡量的是极性平衡度而非情感均值, 因此即便某银行年度的 fin_sent_zh 净语调 (mean over articles) 与相邻年份持平, 只要多空篇章的构成比例发生变化, 本列即会给出不同读数——这正是它作为独立解释变量、而非语调均值线性变换的价值所在。在回归设计中, 本列与同轨的 fin_sent_zh 均值语调列共同进入模型时不构成完全共线, 因为 √(1 − r²) 对 r 是非单调的对称映射, 同一分歧值对应正负两个净极性方向。fin_sent_zh 是三分类模型, 每篇正/中性/负三类概率和为 1, 中性类概率质量会直接压低 P、N 两个均值 (而非仅间接影响), 这一处理使本列的极化读数与 finbert2 这类二分类模型在同一构念上的读数存在结构性差异, 故跨模型仅比标准化 β、不比水平。

## VAR: disag_fin_sent_zh_ctx

【变体差分】
本列是 ctx 轨变体。ctx 轨的篇章文本 = 标题 prepend + 目标实体上下文窗口 (content_ctx), 即只保留银行/金融科技实体附近的文字, 剔除与主题无关的段落, 以此逼近"围绕该银行金融科技的聚焦叙事"而非整篇泛泛报道。相对 canonical 的 full 轨, ctx 轨在留篇门控上是 conditional-on-full: 其行宇宙是 full 留篇集的子集, 只在被 full 判定为有效银行金融科技报道的篇章内, 再按 ctx 文本重新跑 fin_sent_zh BERT, 对逐篇正类、负类概率取均值得到 P、N, 代入同一 disag 闭式。因此本列度量的是"在聚焦到实体窗口的语义空间里, 舆论极化是否仍然成立", 是对 full 轨结论的稳健性检验。两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。与 ss 轨的差别在文本切分口径: ctx 取实体窗口, ss 取银行与金融科技同句共现窗。与 finbert_cn_ctx / finbert2_ctx 的差别仍仅在分类器权重, 本列锁定 fin_sent_zh。因 ctx 文本更短、篇章更少且中性概率质量更高, 在 dev 小样本下本列的 P、N 更易同趋于 0、分母 P + N 为 0 而取 NaN, 属预期退化。方法学上, ctx 轨的价值在于把 full 轨可能夹带的无关段落噪声剔除后, 检验极化结论是否仍稳健: 若 disag_fin_sent_zh_full 与 disag_fin_sent_zh_ctx 在生产语料上给出高度一致的符号与显著性, 则可判定意见分歧不是由报道中与银行金融科技无关的旁支话题人为堆砌出来的, 而是聚焦叙事本身的属性。反之两轨背离则提示极化读数对文本切分口径敏感, 需在稳健性叙事中如实披露。fin_sent_zh 在 ctx 更短文本上的正/负类概率输出受制于分类器对短文本的置信分布, 这是本列与 full 轨读数差异的技术来源之一; 与其它两家 BERT 模型的 ctx 分歧列并排时, 三者 co-equal, 任一模型缺席仅掉自身族而不连坐 (per-model 独立降级)。

## VAR: disag_fin_sent_zh_ss

【变体差分】
本列是 ss 轨变体, 口径最严。ss 轨的篇章文本 = 标题 prepend + 银行与金融科技在同一句 (±N 句窗, 默认半径 1) 共现的片段 (content_ss), 只保留"银行"与"金融科技"两类实体真正同句捆绑出现的语境, 是三轨中语义信噪比最高、文本最短的一轨。其回退语义镜像 ctx: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True (共享 n_articles 分母); 当金融科技 AC 自动机为 None 时整轨优雅降级、is_fallback 全 True。与 canonical 的 full 轨同为留篇门控下的 conditional-on-full 轨: 行宇宙是 full 留篇集子集, 在其上按 ss 文本重跑 fin_sent_zh BERT、对逐篇正类负类概率取均值得到 P、N, 代入同一 disag 闭式。本列度量"在最严格的同句共现语境内, 银行金融科技舆论的极化程度", 与 full/ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。与 finbert_cn_ss / finbert2_ss 的差别仅在 BERT 分类器, 本列锁定 fin_sent_zh, per-model 独立降级。因 ss 文本最短且大量篇章走回退, 正负类概率在 dev T=2 语料上极其稀疏、格内均值 P、N 极小, 本列大概率整列近 0 或 NaN, 属预期的小样本退化, 需生产规模语料方有判别力。ss 轨是三轨中语义纯度最高的一轨, 其分歧读数可解读为"当只看银行与金融科技被同句捆绑陈述的最核心语境时, 舆论对该银行数字化前景是否仍然撕裂"——这是对 full 轨结论最保守的一次压力测试。由于回退机制的存在 (无同句共现即回退全文正文并标记 ss_is_fallback), 生产语料上本列实际是"真同句片段"与"回退全文"两类篇章的混合读数, 使用时应结合 ss_is_fallback 比例判断本列在多大程度上反映了真正的严格共现语境。与 full/ctx 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一 over-identified Hansen J; 与 finbert_cn_ss / finbert2_ss 的跨模型比较只比标准化系数、不比分歧水平, 因各模型的分类边界与中性判定倾向不同, 极化水平不可直接跨模型对齐。

<!-- rendered-citations:begin -->
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science, Vol. 11856. https://doi.org/10.1007/978-3-030-32381-3_16
<!-- rendered-citations:end -->
