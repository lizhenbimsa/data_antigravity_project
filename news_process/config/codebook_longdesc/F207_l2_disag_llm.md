---
family_id: F207
columns:
- disag_llm_ctx
- disag_llm_full
- disag_llm_ss
unit: 无量纲分歧指数 (∈ [0, 1], 0=完全一致, 1=最大分歧)
formula: "disag_llm{track} = sqrt(1 - ((pos_count{track} - neg_count{track}) / (pos_count{track} + neg_count{track}))^2); 分母为 0 时置 NaN"
producer: news_process/pipeline/panel/runner.py (8b 情感意见分歧块, _compute_disag); 标签映射见 pipeline/panel/export.py
upstream:
- "21_tone_llms.parquet (pos_count/neg_count 三轨: LLM 三家投票共识篇章计数)"
- 40_panel_yearly.parquet (bank-year 聚合)
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
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
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"围绕某家银行金融科技报道, 媒体情感基调在同一 bank-year 内部的意见分歧程度", 即同一年内针对同一家银行的多篇报道究竟是口径高度一致 (要么普遍正面、要么普遍负面), 还是正负交织、莫衷一是。用大白话说: 如果这一年关于某银行金科动向的所有报道全都在唱多或者全都在唱空, 分歧就接近 0; 如果一半说好一半说坏, 分歧就冲到最高。这个"内部不一致"本身是一条独立于平均基调 (tone) 的信息维度——两家银行可以有一模一样的平均情感, 却一家报道口径整齐划一、另一家舆论撕裂, 分歧指数正是用来把后一种情形单独拎出来度量的。该构念在资产定价与信息经济学文献中有稳固地位: Cookson 和 Niessner (2020) 系统论证了投资者之间的意见分歧可被分解、度量并解释横截面收益, Carlin、Longstaff 和 Matoba (2014) 进一步给出分歧与资产价格、成交量及风险溢价的直接联系。本家族把这一构念落到"媒体报道情感"层面, 与情感均值轨、情感强度轨互补, 构成对银行金科舆论环境的多维刻画。

【方法学与计算】
本家族三列均由 pipeline/panel/runner.py 的 8b 情感意见分歧块统一生成, 核心是通用函数 _compute_disag(p_col, n_col)。落到 LLM 投票综合口径, 其分子分母取自 stage 21 情感 LLM 三家投票共识 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash 多数投票) 在 bank-year 上聚合出的正面篇数 pos_count 与负面篇数 neg_count。分歧指数的闭式定义为 disag = sqrt(1 - ((pos - neg) / (pos + neg))^2), 取值严格落在 [0, 1] 区间: 当所有报道同向 (pos 或 neg 之一为 0) 时, 括号内比值绝对值为 1, 根号内为 0, 分歧=0, 表示完全一致; 当正负篇数恰好相等时, 比值为 0, 根号内为 1, 分歧=1, 表示最大分歧。计算前对计数列做 float64 强制转换以防御 Int8 计数在 pos+neg ≥ 128 时的静默整数回绕 (对已是浮点的比率/概率输入是 no-op); 分母 pos+neg 为 0 (该 bank-year 无 LLM 判定的正负篇章) 时经 replace(0, NaN) 优雅置为 NaN, 与同族 jf/concern/log_sent 对无文章行输出 NaN 的缺失语义一致 (Allison 2001; Heckman 1979 精神), 绝不用伪中性 0 冒充真测量。这一构造与 Cookson 和 Niessner (2020) 的分歧分解框架同源, 只是把投资者层面的意见离散度替换为媒体报道层面的情感投票离散度。

上游的 LLM 情感投票本身经过严格工程冻结以保证跨-run 可复现: prompt 版本字节级冻结于 v8-2026-05-17、temperature=0.0、命中同一 LLM 缓存键。de Kok (2025) 论证了在会计与金融文本研究中以生成式大模型做标注时, temperature=0 加 prompt 冻结加结果缓存正是保证测量可复现的规范范式; Gilardi、Alizadeh 和 Kubli (2023) 则给出 ChatGPT 类模型在文本标注任务上系统优于众包工人的证据, 支撑以 LLM 投票作为情感基调的可信来源; Huang、Wang 和 Yang (2023) 的 FinBERT 工作说明金融领域文本的情感抽取需要领域适配, 本项目因此让 LLM 三家与三个 BERT 模型互为稳健性、并存不废。分歧指数不改变上游任何情感判定, 纯粹是 bank-year 聚合后的一步无参数后处理。

【文献定位】
把媒体报道的情感分歧作为一条独立面板测度, 直接对接"基于新闻的投资者分歧"这一新兴实证方向: Li 和 Luan (2025) 用新闻文本构造投资者分歧并证明其对股票收益有预测力, 与本家族"以报道情感投票离散度度量舆论分歧"的思路高度一致, 是最贴近的当代锚点。相对情感均值轨, 分歧轨捕捉的是二阶矩性质的信息——不是"舆论多正面", 而是"舆论多不齐"; 相对情感强度轨, 分歧轨对同向的强弱不敏感, 只对正负两侧的相对篇数敏感。本家族三列分属 full/ctx/ss 三轨, 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨混进同一 over-identified Hansen J 过度识别检验; 留篇门控采用 full-only 口径 (2026-06-29), 即一篇报道是否算作"银行金科报道"只看 llm_verified_full, ctx/ss 降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但每轨的 pos_count/neg_count 与由此派生的分歧指数按各轨自身口径独立计算。

## VAR: disag_llm_full

【变体差分】
本列是 LLM 投票分歧指数的 full 轨实例, 也是三轨中与留篇门控口径最贴合的一支。full 轨文本 = 标题 prepend 到全文正文 (content_full), 即把整篇报道的标题与全部正文合并后交给 stage 21 的三家 LLM 投票判定正负, 再在 bank-year 上聚合出 pos_count_full 与 neg_count_full, 代入 disag = sqrt(1 - ((pos - neg) / (pos + neg))^2) 得本列。由于全仓留篇门控采用 full-only 口径 (2026-06-29)——一篇报道是否被计为"一篇银行金科报道"只由 llm_verified_full == True 决定——full 轨的分母 pos+neg 覆盖的正是该 bank-year 的完整留篇集, 因而本列在三轨中样本覆盖最广、缺失最少, 是最稳健的分歧主测度轨。与同家族 ctx/ss 两列相比, 本列不做任何实体窗口或同句共现的文本裁剪, 度量的是整篇报道级别的情感投票离散度。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J; 本列与 ctx/ss 之间是规格稳健性并排关系, 不因相关性高低决定取舍, 各自进入自回归而非同一 RHS。分母为 0 (无 LLM 判定正负篇章) 时本列置 NaN, 不以 0 冒充"1 正 1 负均衡"的真分歧。计数列在进入分歧公式前先 float64 强制转换以防御 Int8 计数在 pos+neg ≥ 128 时的静默整数回绕。本列的上游 LLM 投票经 prompt v8 字节级冻结与 temperature=0 锁定, 保证跨-run 逐位可复现, 是本家族三轨中缺失最少、覆盖最完整、可直接进入基线自回归的分歧主测度; ctx/ss 两轨则作为文本聚焦口径的稳健性对照与本列并排, 三者不因相关性高低取舍。

## VAR: disag_llm_ctx

【变体差分】
本列是 LLM 投票分歧指数的 ctx 轨实例。ctx 轨文本 = 标题 prepend 到实体窗口 (content_ctx), 即只截取目标银行实体附近的上下文窗口 (而非整篇正文) 交给 stage 21 三家 LLM 投票, 再在 bank-year 上聚合出 pos_count_ctx 与 neg_count_ctx, 代入同一分歧闭式得本列。与 full 轨相比, ctx 轨刻意剔除了与目标银行实体距离较远的正文段落, 度量的是"聚焦到银行实体周边语境时"报道情感投票的离散程度——这在报道涉及多主体、正文大段与目标银行无关时, 能过滤掉噪声、更精准地刻画针对该银行的舆论分歧。在 full-only 留篇门控下, ctx 轨是 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 留篇集的子集, 分母 pos_count_ctx+neg_count_ctx 按 ctx 轨自身口径独立统计, 分母为 0 时置 NaN。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。本列与 full 轨的差异纯由文本切分口径 (整篇 vs 实体窗口) 驱动, 模型、投票机制、阈值、分歧公式完全一致, 因而两列的对照恰好隔离出"上下文聚焦"这一单一维度对分歧测量的影响, 构成规格稳健性检验的一条正交轨。计数列在代入分歧公式前同样先做 float64 强制转换以防御 Int8 整数回绕。需强调 ctx 轨的实体窗口裁剪由 stage 14 ctx_materializer 在 stage 21 之前物化, 与 ss 轨的同句共现口径是两个独立的文本切分键, 不可互相复用; 在 T=2 开发切片上 ctx 轨的分歧样本方差可能因篇数稀少而退化, 属预期现象, 生产 T=18 语料下方能充分识别。

## VAR: disag_llm_ss

【变体差分】
本列是 LLM 投票分歧指数的 ss 轨 (same-sentence) 实例。ss 轨文本 = 标题 prepend 到"银行与金融科技词在同一句子且窗口半径内共现"的最严口径片段 (content_ss, 半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 交给 stage 21 三家 LLM 投票, 聚合出 pos_count_ss 与 neg_count_ss 后代入同一分歧闭式得本列。ss 轨是三轨中文本裁剪最严格的一支, 只保留银行与金科概念真正同句共现的语境, 度量的是"报道明确把该银行与金融科技绑定讨论时"情感投票的离散程度, 对纯背景性、泛泛提及的段落最不敏感。ss 轨的回退语义镜像 ctx 轨: 当某篇报道不存在银行与金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 并与其它轨共享 n_articles 分母; 当 FINTECH_AC 为 None 时全部 fallback 优雅降级。在 full-only 留篇门控下, ss 轨同为 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集子集, 分母按 ss 轨自身口径独立统计, 为 0 时置 NaN。full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified Hansen J。需注意在 T=2 开发切片上 ss 轨常出现零方差退化 (共现篇数稀少), 属预期现象, 生产 T=18 语料下方能充分识别。ss 轨的同句共现判据 (银行与金科词同句且窗口半径内) 与 stage 13 上游共现硬过滤所用的 sentence_radius 是不同的配置键, 前者是文本物化口径、后者是留篇过滤口径, 二者不可混淆。与 ctx 轨相比, ss 轨牺牲了更多样本换取语境的精准, 度量的是最严格意义上"银行金科绑定讨论"时的舆论离散度, 因而在三轨梯子中处于文本裁剪最严的一端, 与 full 轨形成最大对比, 是稳健性叙事中不可或缺的一条并排臂。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
<!-- rendered-citations:end -->
