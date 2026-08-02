---
family_id: F199
columns:
- disag_deepseekv4_ctx
- disag_deepseekv4_full
- disag_deepseekv4_ss
unit: 无量纲分歧指数, 取值区间 [0, 1] (0 = 报道语调完全一边倒, 1 = 正负报道势均力敌)
formula: "disag_deepseekv4 = sqrt(1 - ((P - N) / (P + N))^2); P = deepseek-v4-flash 逐模型判正的 verified 篇数, N = 判负篇数 (同一银行-年-轨道内聚合)"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag); 逐模型 P/N 计数来自 news_process/pipeline/sentiment/tone_llms.py 与 encode 层
upstream:
- 21_tone_llms.parquet (deepseek-v4-flash 逐模型篇章级情感标签)
- 24_herd_decay.parquet (df_exploded, verified article×bank 集)
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
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: "Learning from disagreement: A survey"
  venue: Journal of Artificial Intelligence Research
  vol: 72
  issue: ""
  pages_or_artno: 1385-1470
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
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
- doi: "10.1093/rcfs/cfag023"
  title: "Conversational Disagreement: Evidence from Reddit Threads"
  authors: "Balasubramaniam, S., & Sabat, J."
  year: 2026
  venue: "Review of Corporate Finance Studies"
  type: "journal"
  one_sentence_zh: "该文利用社交讨论串文本构造投资者对话层面的分歧测度,与本家族从媒体报道语调正负计数构造银行-年分歧指数的思路同构,均把文本端的意见对立转化为可比较的分歧标量。"
new_dois:
  - "10.1093/rcfs/cfag023"
---

## CORE

【构念与来源】
本家族度量的是"媒体对某家银行金融科技活动的语调分歧程度", 即在给定银行-年度里, 正面报道与负面报道两股力量相互抵消的程度。构念上它不是语调水平 (谁多谁少), 而是语调的内部离散度: 当同一银行同一年既有大量看好又有大量看衰的报道时, 分歧指数取高值; 当报道口径高度一致地倒向一侧时, 分歧指数趋近于零。这一测度直接对应金融学里"信念异质性 (belief heterogeneity)"或"意见分歧 (disagreement)"这一被广泛研究的信息环境特征——它刻画的是市场对一家银行前景没有形成共识的状态, 而这种未达共识本身被大量文献视为交易量、波动率与资产定价的重要驱动。数据来源是流水线 stage 21 的 deepseek-v4-flash 逐模型情感判定: 每一篇经 full-only 门控留下的银行金融科技报道, 由 deepseek-v4-flash 单独给出正/负/中性三分类标签, 再在银行-年-轨道单元内把判正篇数聚合为 P、判负篇数聚合为 N。留篇门控遵循 2026-06-29 的 full-only 口径, 即一篇报道是否算作"一篇银行金融科技报道"仅由 full 轨的验证结果决定, ctx 与 ss 轨在此前提下作为 conditional-on-full 的稳健性测度并排存在。

【方法学与计算】
分歧指数在 runner 步骤 8b 内以闭式公式计算: disag = 根号下 (1 − ((P − N) / (P + N))²)。括号内的 (P − N)/(P + N) 恰是该模型逐轨的净语调 (net tone), 取值在 [−1, 1]; 分歧指数把这个净语调平方后从 1 中减去再开方, 因此它是净语调绝对值的单调递减变换: 净语调为 0 (正负各半) 时分歧达到最大值 1, 净语调为 ±1 (报道完全一边倒) 时分歧降到 0。这一构造等价于把语调看作一个 [0,1] 上的正面比例 p = P/(P+N), 则 disag = 2·根号下 p(1−p), 即伯努利方差的标准化形式, 因而它天然是一个有界、无量纲、跨银行可比的离散度量。分母 P+N 仅计入判正与判负两类, 中性票不进入分子分母; 需要辨明的是, 本家族与 canonical 的 Janis-Fadner 系数、concern_score 虽同样以 deepseek-v4-flash 的逐篇正/负标签为原始输入, 但归一化分母口径并不相同: 分歧指数以 P+N 为分母 (中性票被排除在外), 而 Janis-Fadner 系数的归一化项是把含中性票在内的报道总数平方后所得的 t² = n_articles_llm_valid², concern_score 亦按其自身定义取分母, 因此三者共享的是同一批逐篇正/负计数输入, 而非同一个分母, 不宜笼统称为"同一分母口径"。三条文本轨 full/ctx/ss 各自独立地数各自轨道的 P 与 N: full = 标题 prepend + 全文正文; ctx = 标题 + 实体窗口; ss = 标题 + 银行与金融科技同句共现窗口, 无同句共现时 ss 优雅回退镜像 ctx 的全文 body 语义。三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 检验。同理, deepseek-v4-flash 只是三家投票 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 之一, 本家族是该模型的逐模型 (per-model) 分歧轨, 与 gpt54nano、gemini31 各自的同名分歧轨 co-equal, 三家逐模型度量互为跨厂商稳健性、各自 just-identified 并排, 同样禁混同一 over-identified Hansen J; deepseek-v4-flash 单模型缺席时仅其自身族降级, 不连坐其余两家, 亦非 co-primary 嵌入那种 both-or-neither 的双列同置。

【文献定位】
把"意见分歧"当作可观测的信息环境变量并研究其定价后果, 是金融学的一条主干线。Hong 与 Stein (2007) 在《Journal of Economic Perspectives》中系统梳理了分歧模型 (disagreement models) 如何统一解释交易量、泡沫与崩盘, 为把分歧作为一阶状态变量提供了理论纲领。Carlin、Longstaff 与 Matoba (2014) 在《Journal of Financial Economics》上用抵押支持证券市场的分析师预测离散度实证了分歧升高伴随更高的预期收益、波动率与交易量, 印证了分歧的资产定价含义。Cen、Wei 与 Yang (2017) 在《Management Science》进一步刻画了分歧与反应不足如何共同塑造横截面收益。Cookson 与 Niessner (2020) 在《The Journal of Finance》中借助投资者社交网络把总分歧分解为"跨投资类型"与"同类型内部"两部分, 为本家族"把语调分歧拆到银行-年层面"的分解思路提供了直接的方法学先例。晚近的 Li 与 Luan (2025) 在《Review of Accounting Studies》用基于新闻文本构造的投资者分歧预测股票收益, 与本家族"从媒体报道语调离散度反推信息环境"的路径高度同构。此外, 因为本家族的分歧信号来自 LLM 逐篇标注, 标注端的分歧本身也是一门方法学: Uma 等 (2021) 在《Journal of Artificial Intelligence Research》综述了"从标注分歧中学习"的范式, 提醒我们模型间与轨道间的判定差异既是噪声也是可利用的信号——这正是本项目把三家 LLM、三条轨道并排为互为稳健性梯子而非强行合并的深层依据。Balasubramaniam 与 Sabat (2026, Review of Corporate Finance Studies) 利用社交讨论串文本构造投资者对话层面的分歧测度, 与本家族从媒体报道语调正负计数构造银行-年分歧指数的思路同构, 均把文本端的意见对立转化为可比较的分歧标量。

## VAR: disag_deepseekv4_full

【变体差分】
本列是 deepseek-v4-flash 分歧家族的 full 轨实例, 也是 full-only 留篇门控的 canonical 文本轨。它在 full 文本轨上聚合 deepseek-v4-flash 的逐模型判定: full 轨 = 标题 prepend + 全文正文, 因此 P (判正篇数) 与 N (判负篇数) 数的是"标题加整篇正文"喂给 deepseek-v4-flash 后得到的正负标签。该轨的行宇宙 = full-only 门控下留下的银行金融科技报道全集, 是三轨中信息量最大、样本最全的一轨, 其余两轨 (ctx/ss) 的行宇宙均是本轨留篇集的子集。与家族内 gpt54nano_full、gemini31_full 两个同轨兄弟列相比, 本列唯一的差分维度是打分模型 = deepseek-v4-flash (直连 api.deepseek.com, 与走 OpenLux 的另两家不同源); 三家逐模型 full 轨分歧各自 just-identified 并排, 互为跨厂商稳健性、不分主次, 严禁三家混进同一 over-identified 的 Hansen J。计算口径与家族公式完全一致: disag = 根号下 (1 − ((P − N)/(P + N))²), 分母只计判正判负、中性不入分母。当某银行-年在 full 轨仅有单侧报道或仅有中性票时, 净语调为 ±1 或分母为零, 分歧相应取 0 或 NaN, 属预期退化而非缺陷。需要强调的是, 本列作为 canonical 门控轨, 其 P、N 计数与家族其余测度 (Janis-Fadner 系数、concern_score、逐模型净语调) 共享同一批以 deepseek-v4-flash 逐篇正/负标签为原始输入的计数, 但各测度的归一化分母口径并不一致, 不可混同: 本列分歧指数的分母是 P+N, 中性票被排除在外; 而 Janis-Fadner 系数以含中性票在内的报道总数平方 t² = n_articles_llm_valid² 为归一化项, concern_score 则另按其自身定义取分母。因此三者在 full 轨上共享的是一致的正/负计数样本基础, 可在回归里彼此印证, 但这并不意味着它们使用同一个分母——分母口径的差异恰恰是三测度构念侧重不同 (是否把中性票计入"总关注量") 的体现, 使用时应据此区分而非视作可互换。本列刻画的是媒体对该银行金融科技前景在整篇报道层面尚未形成共识的程度, 高值意味着看好与看衰两股叙事在同一年度里并存且势均力敌, 这一状态本身即被分歧定价文献视为信息环境的重要维度, 与语调水平列共同进入信息环境刻画时二者正交互补: 前者答"倾向哪边", 本列答"分歧多大"。

## VAR: disag_deepseekv4_ctx

【变体差分】
本列是 deepseek-v4-flash 分歧家族的 ctx 轨实例。ctx 轨 = 标题 + 实体窗口, 即只把银行实体附近的上下文窗口 (而非整篇正文) 喂给 deepseek-v4-flash 打分, 再在银行-年单元内数该轨的判正篇数 P 与判负篇数 N。相对 full 轨, ctx 轨聚焦于银行实体周边的局部语境, 剔除了正文里与目标银行无关的段落噪声, 因此是一条"缩窄语境"的稳健性轨。在 full-only 门控口径下, 本列是 conditional-on-full 的测度: 一篇报道是否留篇仅由 full 轨判定, 本列只在留篇集内按 ctx 轨自身的正负标签重算分歧。与 gpt54nano_ctx、gemini31_ctx 相比, 本列的差分维度是打分模型 = deepseek-v4-flash; 与本家族 full/ss 两轨相比, 差分维度是文本轨道 = ctx。轨道之间、厂商之间均各自 just-identified 并排, 互为稳健性、不分主次, 禁混同一 over-identified Hansen J。计算沿用家族闭式公式, 分母只计判正判负两类。在早期试跑 T=2 的开发样本上 ctx 轨可能出现零方差或大量退化取值, 属小样本预期现象, 生产 T=19 语料上恢复正常。ctx 轨与 full 轨的分歧差异有明确的经济含义: 若某银行的整篇报道呈现高分歧、而实体窗口局部却口径一致, 说明分歧来自与该银行无直接关联的行业或宏观段落; 反之若局部窗口分歧更高, 则说明争议恰恰聚焦在该银行自身的金融科技动作上。正是这种"缩窄语境后信号是否保持"的对照, 使 ctx 轨成为 full 轨的严格稳健性检验, 而非冗余复制。本列 P/N 仅计判正判负、中性不入分母, 与家族口径完全一致; deepseek-v4-flash 直连 api.deepseek.com 打分, 与走 OpenLux 的另两家同源分离, 保证跨厂商稳健性检验的独立性。

## VAR: disag_deepseekv4_ss

【变体差分】
本列是 deepseek-v4-flash 分歧家族的 ss (same-sentence) 轨实例。ss 轨 = 标题 + 银行与金融科技同句共现窗口 (以 config 的 ss_sentence_radius 为半径, 默认 ±1 句), 即只保留"目标银行与金融科技词落在同一句或相邻句"的最窄语境喂给 deepseek-v4-flash, 再数该轨的判正 P 与判负 N。它是三轨中语境最严格的一条, 用于检验分歧信号是否稳健于"银行与金融科技强共现"这一最保守的判定口径。ss 轨的回退语义镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文 body, ss_is_fallback 置 True, 与 ctx 轨共享 n_articles 分母, 属优雅降级而非丢行。在 full-only 门控下本列同样是 conditional-on-full 测度, 只在 full 留篇集内按 ss 轨标签重算分歧。与 gpt54nano_ss、gemini31_ss 相比, 差分维度是打分模型 = deepseek-v4-flash; 与 full/ctx 两轨相比, 差分维度是文本轨道 = ss。三轨、三家各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J。计算沿用家族公式, 分母只计判正判负; 开发样本早期试跑 T=2 上 ss 轨常见零方差退化, 属预期, 不影响生产语料。ss 轨的价值在于把"银行确实在谈论金融科技"这一判定收紧到同句共现的最保守边界: 若分歧信号在如此严格的语境下依旧稳健, 则可基本排除"分歧来自银行与金融科技被松散并置的偶然共现"这一替代解释。因回退语义镜像 ctx, 无同句共现的报道并不被丢弃而是降级为全文 body 并标记 fallback, 因此本列既保住样本量又保留了最严判据下的信号强度对照。本列 P/N 同样仅计判正判负两类, 中性票不入分母, 与 full/ctx 两轨及家族其余离散度列口径一致, 从而三轨、三家在各自 just-identified 的前提下构成一张完整的规格稳健性网, 任何单元的退化都不牵连其余单元。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Balasubramaniam, S., & Sabat, J. (2026). Conversational Disagreement: Evidence from Reddit Threads. Review of Corporate Finance Studies. https://doi.org/10.1093/rcfs/cfag023
<!-- rendered-citations:end -->
