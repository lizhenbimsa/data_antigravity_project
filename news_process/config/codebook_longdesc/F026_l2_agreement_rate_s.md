---
family_id: F026
columns:
- avg_agreement_rate_s_ctx
- avg_agreement_rate_s_full
- avg_agreement_rate_s_ss
unit: 比率 (proportion, 无量纲, 取值域 [0,1] ∪ NaN)
formula: "avg_agreement_rate_s{track} = bank-year mean of llm_agreement_rate_s{track}; llm_agreement_rate_s = (三家 LLM 情感票中与最终多数情感方向一致的票数) / (该篇有效情感票数), 域 = LLM verified 留篇 (逐轨收缩); 文章级 NaN=无有效情感票, 自编码域直 mean 无掩码"
producer: news_process/pipeline/sentiment/tone_llms.py ; news_process/pipeline/panel/encode.py ; news_process/pipeline/panel/codebook.py
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 21_tone_llms.parquet (llm_agreement_rate_s_full / _ctx / _ss 文章级列)
- 40_panel_yearly.parquet (Stage 40 panel/encode aggregate_panel bank-year 聚合)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1177/00131644251380540
  type: journal
  authors: Almehrizi, R. S.
  year: 2026
  title: "Coefficient Lambda for interrater agreement among multiple raters: Correction for category prevalence"
  venue: Educational and Psychological Measurement
  vol: 86
  issue: 2
  pages_or_artno: 287-319
- doi: 10.3758/s13428-025-02746-8
  type: journal
  authors: Moons, F., & Vandervieren, E.
  year: 2025
  title: "Measuring agreement among several raters classifying subjects into one or more (hierarchical) categories: A generalization of Fleiss' kappa"
  venue: Behavior Research Methods
  vol: 57
  issue: 10
  pages_or_artno: 287
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1037/met0000412
  type: journal
  authors: van Oest, R., & Girard, J. M.
  year: 2021
  title: "Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement"
  venue: Psychological Methods
  vol: 28
  issue: 6
  pages_or_artno: 1412-1432
- doi: 10.1348/000711006x126600
  type: journal
  authors: Gwet, K. L.
  year: 2008
  title: "Computing inter-rater reliability and its variance in the presence of high agreement"
  venue: British Journal of Mathematical and Statistical Psychology
  vol: 61
  issue: 1
  pages_or_artno: 29-48
- doi: 10.1016/0895-4356(90)90158-l
  type: journal
  authors: Feinstein, A. R., & Cicchetti, D. V.
  year: 1990
  title: "High agreement but low kappa: I. The problems of two paradoxes"
  venue: Journal of Clinical Epidemiology
  vol: 43
  issue: 6
  pages_or_artno: 543-549
- doi: 10.1037/h0031619
  type: journal
  authors: Fleiss, J. L.
  year: 1971
  title: "Measuring nominal scale agreement among many raters"
  venue: Psychological Bulletin
  vol: 76
  issue: 5
  pages_or_artno: 378-382
new_dois: []
---

## CORE

【构念与来源】
本家族三列 avg_agreement_rate_s_full、avg_agreement_rate_s_ctx、avg_agreement_rate_s_ss 度量的是同一构念在三条文本轨道上的银行-年 (bank-year) 展开: 三家大语言模型对同一篇银行金融科技报道所投的情感方向票, 与该篇最终共识情感方向的一致占比, 在留篇集合上取银行-年均值。名字里的后缀 s 是 sentiment (情感) 的缩记, 它把本列与同批的兄弟列 avg_agreement_rate 明确区隔开: 兄弟列度量的是验证票一致率 (三家模型是否一致判定该篇属于一篇银行金融科技报道, 即 verification decision), 而本家族度量的是情感票一致率 (三家模型对报道语气方向 —— 正面、中性、负面 —— 是否一致)。两者是同一质量诊断框架下互补的两个维度: 前者回答"这篇报道是否被一致认定为在样本内", 后者回答"被认定在样本内的报道, 其情感标注是否被一致给出"。因而本家族被定位为并排的第二质量维度, 而非情感数值本身 —— 它不进入任何情感 headline 度量的构造, 只作为银行-年层的 LLM 测量不确定性诊断量。

情感投票的三家模型阵容动态读自 config/sentiment.yaml, 生产口径为 gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash 三家 (前两家经 yunwu 路由, 第三家直连 api.deepseek.com)。三家各自独立读取同一篇报道文本给出情感方向判断, 由多数投票产生最终共识方向; 文章级的一致率原语 llm_agreement_rate_s 即在这一投票展开上计算: 分子为三票中方向与最终共识一致的票数, 分母为该篇的有效情感票数。低值意味着三家在情感方向上分歧较大, 该篇的情感标注可信度较弱; 高值意味着三家高度一致, 标注稳固。把文章级一致率在银行-年格子内按简单均值聚合, 即得本家族三列。这一多标注者一致率的构念与经典的多评分者名义尺度一致性度量同源 (Fleiss, 1971), 并与近年将大语言模型作为标注者纳入管理学与金融学研究的方法学脉络直接衔接 (Carlson & Burbano, 2026)。

【方法学与计算】
计算链路分文章级与面板级两段。文章级 (Stage 21, tone_llms) 对每篇报道、每条轨道分别汇总三家 JSON 响应并执行多数投票三角验证, 产出 llm_agreement_rate_s_full、llm_agreement_rate_s_ctx、llm_agreement_rate_s_ss 三个文章级列; 当某篇某轨无有效情感票时, 文章级取 NaN。面板级 (Stage 40, panel/encode aggregate_panel) 对每个银行-年格子内的文章级一致率取均值。此处采用的是自编码域 (self-coding domain) 直接均值, 不施加额外掩码: 文章级 NaN 篇自然被均值排除, 银行-年若全无有效情感票则该格取 NaN。取值域为 [0,1] ∪ NaN, 单位为无量纲比率。

本家族严格遵守项目的三轨与留篇口径铁律。三条轨道文本在 Stage 14 (ctx_materializer) 物化: full 轨 = 标题 prepend 后拼全文正文; ctx 轨 = 标题 + 实体上下文窗口; ss 轨 = 标题 + 银行与金融科技同句共现的 ±N 句窗 (窗半径读 config/filtering.yaml 的 ss_sentence_radius, 默认 1)。ss 轨采用镜像 ctx 的回退语义: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文正文, ss_is_fallback=True。留篇门控为 full-only (2026-06-29 口径): 一篇报道是否被判为"银行金融科技报道"只看 llm_verified_full 是否为真; ctx 与 ss 轨降为 conditional-on-full 的测度与稳健性轨, 其行宇宙是 full 留篇集的子集, 各轨的一致率在各自轨的 verified 留篇篇数上收缩计算。三条轨道互为稳健性、不分主次, 各自 just-identified 并排; 铁律: 三轨禁混进同一 over-identified Hansen J 检验。

【文献定位】
本家族的方法学根系在多评分者名义尺度一致性文献。原始一致率 (raw / observed agreement) 是最直接的一致性刻画, 由 Fleiss (1971) 系统化为多评分者情形。但原始一致率不做机会一致 (chance agreement) 校正, 因而存在著名的"高一致率、低 kappa"悖论: 当类别边际分布高度不均衡时, 观测一致率可以很高而机会校正系数却塌向零 (Feinstein & Cicchetti, 1990)。本家族刻意保留原始一致率口径而非机会校正系数, 原因有三: 其一, 本列的用途是银行-年层的相对诊断而非跨研究的绝对信度报告, 原始比率的可解释性 (三家中有几家同向) 对面板诊断更透明; 其二, 机会校正系数 (如 Gwet 的 AC 系列、加权与不完整数据下的贝叶斯校正) 各有其边际假设与方差估计的复杂性 (Gwet, 2008; van Oest & Girard, 2021), 在银行-年格子内篇数很小时估计极不稳定; 其三, 面向类别流行度校正的新一代系数 (Almehrizi, 2026) 与对多类别、层级分类的 Fleiss kappa 推广 (Moons & Vandervieren, 2025) 表明机会校正本身是一个开放的方法学谱系, 把其中任一具体系数固化进面板反而牺牲透明度。作为稳健性梯子, 项目在别处以 Krippendorff α 与 Cohen κ 承接机会校正维度的模型间一致性诊断, 本家族与之正交互补。将模型间分歧本身作为可用信号 (而非纯噪声) 的做法, 亦与近年新闻驱动投资者分歧文献一脉相承 (Li & Luan, 2025): 银行-年层的情感标注分歧, 可解读为该行当年媒体叙事内在模糊度的代理。

## VAR: avg_agreement_rate_s_full

【变体差分】
本列是家族在 full 轨上的展开, 也是留篇门控所依据的规范轨道。full 轨文本 = 标题 prepend 后拼接全文正文 (content_full), 覆盖报道全篇信息, 因而三家 LLM 在最丰富的上下文下给出情感方向判断。由于留篇门控为 full-only (2026-06-29 口径), 本列的行宇宙即银行-年内所有 llm_verified_full 为真的留篇报道 —— 它是三轨中唯一直接定义留篇集的轨道, ctx 与 ss 轨的行宇宙都是本轨留篇集的子集。分母为 full 轨该篇的有效情感票数, 分子为其中方向与最终共识一致的票数; 银行-年均值在 full 留篇集上直接计算, NaN 篇 (无有效情感票) 自然排除。相较 ctx 与 ss 轨, 本列因文本最长、信息最全, 三家在情感方向上通常更易收敛, 一致率水平往往最高且方差最稳; 但也正因覆盖全篇, 当报道同时含正负面段落时, 三家对整体基调的取舍可能出现方向分歧, 使本列成为捕捉全篇层面叙事模糊度最灵敏的诊断轨。在解释上, 本列低值应读作"该行当年被认定在样本内的报道, 三家 LLM 对其全篇基调方向的判断分歧较大", 可作为对该行当年情感度量测量误差的银行-年层预警; 高值则支持情感 headline 度量在该格上的稳定性。作为原始一致率而非机会校正系数, 本列在类别边际高度不均衡 (如某行某年报道几乎全为中性) 时需谨慎解读, 以免落入高一致率悖论 (Feinstein & Cicchetti, 1990)。本列与 ctx、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排; 铁律: 三轨禁混进同一 over-identified Hansen J 检验。

## VAR: avg_agreement_rate_s_ctx

【变体差分】
本列是家族在 ctx 轨 (entity-context, 实体上下文轨) 上的展开。ctx 轨文本 = 标题 prepend 后拼接实体上下文窗口 (content_ctx), 即只保留目标银行实体附近的文本窗口而非全篇, 意在把三家 LLM 的情感判断聚焦到与目标银行直接相关的语境, 抑制全篇中与该行无关段落的干扰。作为 conditional-on-full 的测度与稳健性轨, 本列的行宇宙是 full 留篇集的子集, 且一致率在 ctx 轨自身的 verified 留篇篇数上收缩计算 —— ctx 轨的 LLM 有效投票率与 full 轨独立, 故分母必须用 ctx 轨自身的有效情感票数, 不借 full 轨分母 (这一逐轨分母铁律与面板 n_articles_llm_valid_ctx 的口径一致)。相较 full 轨, ctx 轨因文本被裁剪到实体窗口、上下文更短, 三家可读到的信息量减少, 情感方向判断可能因窗口边界不同而更易分歧, 也可能因去除无关噪声而更聚焦; 本列因此是检验"聚焦目标实体是否改变情感标注一致性"的稳健性轨。在跨轨对读时, 若本列与 full 轨一致率系统性偏离, 提示全篇语境与实体窗口语境给出的情感信号存在结构性差异 —— 这本身即是该行媒体叙事在整体层面与银行特定层面是否分化的诊断线索。ctx 轨窗口边界由实体上下文物化规则确定, 故本列对窗口设定较敏感, 解读时应与 full、ss 两轨联读而非孤立采信。本列与 full、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排; 铁律: 三轨禁混进同一 over-identified Hansen J 检验。

## VAR: avg_agreement_rate_s_ss

【变体差分】
本列是家族在 ss 轨 (same-sentence, 银行与金融科技同句共现轨) 上的展开, 是三轨中语境约束最严的一轨。ss 轨文本 = 标题 prepend 后拼接银行与金融科技词同句共现的 ±N 句窗 (content_ss, 窗半径读 config/filtering.yaml 的 ss_sentence_radius, 默认 1), 只在目标银行与金融科技概念于同一句 (及其近邻句窗) 内共现处取材, 把三家 LLM 的情感判断锚定到银行与金融科技的直接语义交汇点。ss 轨采用镜像 ctx 的回退语义: 当某篇不存在银行与金融科技的同句共现时, content_ss 回退为全文正文, ss_is_fallback=True, 与 ctx 回退共享 n_articles 分母口径。作为 conditional-on-full 的测度与稳健性轨, 本列行宇宙是 full 留篇集的子集, 一致率在 ss 轨自身的 verified 留篇篇数上逐轨收缩计算, 不借 full 或 ctx 轨分母。相较 full 与 ctx 轨, ss 轨文本最短、语境最窄, 在开发期 T=2 的小样本上易出现零方差退化属预期; 但在生产语料上它捕捉的是最纯粹的银行金融科技交汇语境下的情感标注一致性, 是检验"把语境收紧到同句共现是否改变标注分歧结构"的最严稳健性轨。因回退语义的存在, 解读本列时须留意 ss_is_fallback 为真的篇实际读取的是全文而非同句窗, 故在同句共现稀疏的银行-年上本列会向 full 轨口径靠拢; 只有在共现密集的格子上, 本列才真正体现同句语境约束下的标注一致性。本列与 full、ctx 两轨互为稳健性、不分主次, 各自 just-identified 并排; 铁律: 三轨禁混进同一 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Almehrizi, R. S. (2026). Coefficient Lambda for interrater agreement among multiple raters: Correction for category prevalence. Educational and Psychological Measurement, 86(2), 287-319. https://doi.org/10.1177/00131644251380540
Moons, F., & Vandervieren, E. (2025). Measuring agreement among several raters classifying subjects into one or more (hierarchical) categories: A generalization of Fleiss' kappa. Behavior Research Methods, 57(10), 287. https://doi.org/10.3758/s13428-025-02746-8
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
van Oest, R., & Girard, J. M. (2021). Weighting schemes and incomplete data: A generalized Bayesian framework for chance-corrected interrater agreement. Psychological Methods, 28(6), 1412-1432. https://doi.org/10.1037/met0000412
Gwet, K. L. (2008). Computing inter-rater reliability and its variance in the presence of high agreement. British Journal of Mathematical and Statistical Psychology, 61(1), 29-48. https://doi.org/10.1348/000711006x126600
Feinstein, A. R., & Cicchetti, D. V. (1990). High agreement but low kappa: I. The problems of two paradoxes. Journal of Clinical Epidemiology, 43(6), 543-549. https://doi.org/10.1016/0895-4356(90)90158-l
Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. Psychological Bulletin, 76(5), 378-382. https://doi.org/10.1037/h0031619
<!-- rendered-citations:end -->
