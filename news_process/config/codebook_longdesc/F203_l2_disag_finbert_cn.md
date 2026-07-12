---
family_id: F203
columns:
- disag_finbert_cn_ctx
- disag_finbert_cn_full
- disag_finbert_cn_ss
unit: 无量纲离散度指标, 取值区间 [0, 1]
formula: "disag = sqrt(1 - ((P - N) / (P + N))^2); P = FinBERT-CN 正面类概率在该 (银行, 年份, 轨道) 单元的均值 (bank-year-track mean of per-article positive-class probability, 即 finbert_cn_pos), N = 负面类概率均值 (finbert_cn_neg); 为 [0,1] 概率均值而非篇数计数"
producer: news_process/pipeline/panel/runner.py::main (步骤 8b disag, 输入 finbert_cn_pos/finbert_cn_neg) ; news_process/pipeline/panel/encode.py (BERT 逐模型正/负类概率的 bank-year mean 聚合, 非 argmax 篇数计数)
upstream:
- 23_tone_berts.parquet
- 24_herd_decay.parquet
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: "Learning from disagreement: A survey"
  venue: Journal of Artificial Intelligence Research
  vol: 72
  pages_or_artno: 1385-1470
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
new_dois: []
---

## CORE

【构念与来源】
本家族三列度量的是同一构念: 在给定银行-年度单元内, FinBERT-CN 情感分类器对该行相关新闻所打情感在正负两极之间的分散程度, 即"媒体口径的观点分歧度"(disagreement)。构念动机来自资产定价与信息经济学的分歧文献: Hong & Stein (2007) 将投资者观点分歧视作影响价格与交易的独立状态变量, Carlin, Longstaff, & Matoba (2014) 进一步给出分歧与资产价格、波动、成交量的联合刻画, Cen, Wei, & Yang (2017) 则记录分歧与反应不足、后续收益之间的系统关系。在银行舆论场景里, 一年中媒体对同一家银行既有大量正面报道又有大量负面报道, 与舆论一边倒地看多或看空, 传递的信息内容截然不同; 前者意味着市场对该行金融科技转型的评价存在实质撕裂, 后者意味着共识。用一个标量把这种"撕裂程度"压缩出来, 便于纳入银行-年度面板做回归。数据来源是 stage 23 (23_tone_berts) 产出的 FinBERT-CN 篇章级情感概率——每篇报道 FinBERT-CN 都给出正面、中性、负面三类的 softmax 概率。在 stage 40 装配阶段, encode 层先逐篇取该报道的正面类概率与负面类概率, 再逐 (银行, 年份, 轨道) 求算术平均, 得到该单元的正面概率均值 P (finbert_cn_pos) 与负面概率均值 N (finbert_cn_neg); runner.py 步骤 8b 再把 P、N 代入下述闭式。需强调 P、N 是落在 [0,1] 区间的概率均值, 而非把每篇 argmax 归到 {正面, 中性, 负面} 三类后再数出的整数篇数——argmax 篇数计数 (finbert_cn_pos_count 一类) 是另一套本家族并不消费的量, 只出现在别的列族里。这与本流水线 LLM 分歧列 (disag_llm、各家单 LLM disag) 走离散篇数计数 (pos_count/neg_count) 是刻意分开的两套基座: BERT 侧承接的是分类器的连续置信度信息, LLM 侧承接的是逐篇多数票, 二者对"表态强度"的编码粒度不同, 不可互相替换分子分母。

【方法学与计算】
计算式为 disag = √(1 − ((P − N) / (P + N))²)。令一致率 tone = (P − N) / (P + N) ∈ [−1, 1] 表示正负净倾向, 则 disag = √(1 − tone²)。极端情形: 当该单元所有报道的概率一致偏向单极 (正面概率均值 P 远大于负面概率均值 N, 或反之, 极限下另一极均值趋 0) 时 tone→±1, disag→0, 表示零分歧; 当正、负两类概率均值恰好相等 (P = N > 0, 意味着媒体样本整体上对该行既有等量的看多置信也有等量的看空置信) 时 tone=0, disag=1, 表示最大分歧。需要澄清基座差异: 本 FinBERT-CN 分歧列的 P、N 是 BERT 正/负类概率的 bank-year-track 均值, 与流水线中 Janis-Fadner 系数 (7i) 及 concern_score 走的基座并不相同——Janis-Fadner 用的是 LLM 有效投票篇数 (n_articles_llm_valid 与正、负篇数计数), concern_score 用的是词典效价比率 (neg−pos)/(neg+pos); 而 disag 家族内部又分三支: 词典综合/单词典支走词级正负比率 (avg_pos_ratio 等), LLM 综合/单 LLM 支走 LLM 篇数计数 (pos_count/neg_count), 唯独 BERT 综合/单 BERT 支 (含本 finbert_cn 列) 走概率均值。三支只是 disag 这一函数壳的三种不同输入基座, 函数形态相同而基座各异, 因此本列与 Janis-Fadner、concern 之间既非"共用同一 P/N 计数基座", 也不能把它们的 P、N 混用。中性类概率不进入分子分母 (只由 P、N 定义), 因此 disag 反映的是"正负两极置信之间"的对立, 而非"表态与中性"的对比。分母 P+N 为 0 (该单元该轨无任何 FinBERT-CN 有效概率) 时结果按缺失处理, 不强行置零, 以免把"无信息"误当成"零分歧"。FinBERT-CN 是 stage 23 三个并列 BERT 模型 (finbert_cn / fin_sent_zh / finbert2) 之一, 三模型 co-equal、互为稳健性、不分主次; 本家族只取 FinBERT-CN 一家的概率均值, 其同构兄弟家族对 fin_sent_zh、finbert2 各自另算。按项目铁律, 三个 BERT 模型的同名分歧列各自 just-identified 并排、互为稳健性, 禁混进同一 over-identified Hansen J; 且 per-model 独立降级——某模型缺席只掉其自身族列, 不连坐其余。FinBERT 类模型对金融文本的判别效度见 Huang, Wang, & Yang (2023) 的系统评估。

【文献定位】
把分歧作为一个可测度的舆论状态量, 直接承接 Cookson & Niessner (2020) 在《Journal of Finance》提出的分歧分解框架: 他们区分同一信息集下不同解读带来的分歧, 与不同信息集带来的分歧, 并展示前者对定价的独立作用; 本家族的 disag 属"给定媒体样本内情感对立"的可观测代理, 落在其框架的"信息处理异质"一侧。Li & Luan (2025) 更直接地以新闻文本构造投资者分歧并检验其对股票收益的预测力, 与本项目用媒体报道情感极性离散刻画银行层面分歧的做法同源。方法层面, 用机器标注情感的"不一致"本身承载信号而非纯噪声, 这一视角由 Uma et al. (2021) 的"从分歧中学习"综述系统化; 值得注意的是本列以概率均值而非离散标签为基座, 恰与该综述强调的"保留标注端连续不确定度信息"的主张相合。分歧亦具网络维度: Grieser, Hadlock, LeSage, & Zekhnini (2022) 记录企业财务政策的同行网络效应, 提示银行层面的舆论分歧可能沿同业网络扩散, 为下游 disag 与网络溢出族的交叉分析提供理论接口。综合看, disag 是把资产定价分歧文献的核心状态变量, 移植到中文银行-金融科技媒体语料、并以 FinBERT-CN 分类器的连续概率为基座的一个操作化实现。

## VAR: disag_finbert_cn_full

【变体差分】
本列为 full 轨实现: 情感判定的输入文本 = 标题 prepend 后的全文正文 (content_full), 覆盖整篇报道的语义。full 轨是本家族的 canonical 主轨——按 2026-06-29 确立的 full-only 留篇门控, 一篇报道是否计入"银行金融科技报道"宇宙只看其 full 轨的 LLM 判定, ctx/ss 轨的行宇宙是 full 留篇集的子集。因此 disag_finbert_cn_full 的正、负概率均值 (P、N) 覆盖面最广, 对该行该年全部留篇逐篇取 FinBERT-CN 概率后求均, 是三轨中信息量最完整、最稳定的分歧刻画, 也是把本构念接入主回归时的首选处理/控制变量。与同轨的 fin_sent_zh、finbert2 分歧列各自 just-identified 并排、互为稳健性、不分主次, 三模型 full 轨列禁混进同一 over-identified Hansen J。相对 ctx/ss 两轨, 本列不做任何实体窗口或同句共现的文本裁剪, 分歧信号来自整篇语义, 因而更不易因窗口过窄而退化为零方差。该列无 _lg 孪生: FinBERT 是本地分类器而非嵌入 API, 不落 co-primary 双轨嵌入的 both-or-neither 约束; 其缺失遵循 per-model 独立降级——FinBERT-CN 缺席仅使本列 (及其 ctx/ss 兄弟) 置缺, 不影响 fin_sent_zh、finbert2 的同名列。使用建议: 由于 full 轨对整篇语义计算概率均值, 参与平均的报道数最充分, disag_finbert_cn_full 是解释"某行某年媒体口径是否撕裂"最稳健的主口径, 优先作为进入基准回归的分歧代理; ctx、ss 两轨则退居 conditional-on-full 的稳健性对照, 用于验证结论不依赖于文本取窗口径。需要强调的是 disag 与同基座的一致率 tone 是严格函数关系 (disag=√(1−tone²)), 二者高度非线性相关, 因此在同一 over-identified 设定内并列 tone 与 disag 会引入构造共线, 应分开进入各自 just-identified 规格; 这与政治词权重梯子、消融梯度的处理口径一致。同时须记得本列 P、N 是 [0,1] 概率均值而非篇数, 解读系数量纲时不可套用"每多一篇正面报道"的篇数直觉。

## VAR: disag_finbert_cn_ctx

【变体差分】
本列为 ctx 轨实现: 情感判定输入文本 = 标题 prepend + 实体上下文窗口 (content_ctx), 即只保留目标银行实体附近的若干句而非整篇。相对 full 轨, ctx 轨聚焦"围绕该银行说了什么", 剔除与银行无关的段落噪声, 因而分歧信号更贴近针对该行本身的观点对立, 但代价是参与概率平均的报道通常少于 full 轨, 在样本稀薄的银行-年度单元上更易出现零方差退化 (dev T=2 上尤为明显, 属预期)。ctx 轨定位为 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 留篇集的子集, per-track 概率均值照算, 但不承担留篇门控职责。本列与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混进同一 over-identified Hansen J; 同时与 fin_sent_zh、finbert2 的 ctx 轨分歧列构成 per-model 并列稳健性。当 FINTECH_AC=None 或实体窗口物化失败时, content_ctx 触发 fallback 语义, 相应 disag 依据可用报道的 FinBERT-CN 概率均值计算或按缺失优雅降级, 不静默置零。该列无 _lg 孪生, 理由同 full 轨: FinBERT 为本地分类器, 不在 co-primary 嵌入族之列。解读要点: 若某行某年 disag_finbert_cn_ctx 与 disag_finbert_cn_full 出现明显背离, 通常指向"整篇层面的分歧主要来自与银行本体无关的段落"——full 轨把这些外围报道的概率也计入平均, ctx 轨则将其滤除, 二者之差本身即一条可供机制分析的信号。正因如此, ctx 轨不是 full 轨的冗余复制, 而是对文本聚焦程度这一维度的稳健性检验, 用来确认分歧构念不是被无关背景报道人为放大或稀释。轨间比较时须记得三轨行宇宙不同 (ctx ⊆ full 留篇集), 逐轨 P、N 各自计算, 不跨轨借用概率均值。

## VAR: disag_finbert_cn_ss

【变体差分】
本列为 ss 轨实现: 情感判定输入文本 = 标题 prepend + 银行与金融科技词同句共现窗口 (content_ss), 判定口径最严——只有目标银行与金融科技词在同一句 (±N 句半径, 由 config filtering.yaml 的 ss_sentence_radius 控, 默认 1) 内共现的片段才进入文本。因此 ss 轨捕捉的是"银行的金融科技相关表态"最聚焦的一层, 分歧信号最贴近本项目核心构念, 但参与概率平均的报道在三轨中最少, 零方差退化风险最高 (dev T=2 上 ctx/ss 常均值零方差, 属预期退化, 生产 T=18 正常)。ss 轨的回退语义镜像 ctx: 当某篇无银行与金融科技的同句共现时, content_ss 回退为全文 body、ss_is_fallback=True, 与共享 n_articles 分母保持一致; FINTECH_AC=None 时全篇 fallback 优雅降级。本列定位为 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集。与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 与 fin_sent_zh、finbert2 的 ss 轨分歧列构成 per-model 并列稳健性, per-model 独立降级。该列同样无 _lg 孪生 (FinBERT 本地分类器, 非嵌入族)。定位小结: ss 轨在三轨中语义最窄、最贴近"银行与金融科技同框时的舆论对立", 因而当研究关注的正是该行金融科技动作引发的评价分歧时, ss 轨的 disag 提供了口径最纯净的度量; 但其参与平均的报道最少, 统计噪声与零方差退化风险相应最高, 单独使用时须结合有效报道数一并披露, 避免把少数几篇报道的偶然概率对立误读为系统分歧。实践上三轨应成组呈现: full 给出面最广的主口径, ctx 检验窗口聚焦的稳健性, ss 检验极端聚焦下结论是否仍成立, 三者互为稳健性、不分主次, 任一轨都不得与其余两轨混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
<!-- rendered-citations:end -->
