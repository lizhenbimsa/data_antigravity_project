---
family_id: F069
columns:
- avg_subst_prob_score_ctx
- avg_subst_prob_score_full
- avg_subst_prob_score_ss
- avg_subst_prob_score_std_ctx
- avg_subst_prob_score_std_full
- avg_subst_prob_score_std_ss
unit: 无量纲概率分值 ∈ [0, 1] (均值轨); 同尺度的组内离散度 (标准差轨)
formula: "article: avg_subst_prob_score = mean_over_verifying_models(binary prob_score, positive_class=象征性) ∈ [0,1]; panel mean 轨: avg_subst_prob_score_{track} = mean over articles per (target_bank, year); panel std 轨: avg_subst_prob_score_std_{track} = std over articles per (target_bank, year)"
producer: news_process/pipeline/panel/encode.py (mean/std aggregation) ← news_process/pipeline/sentiment/tone_llms.py::_aggregate_track (article-level avg_subst_prob_score)
upstream:
  - 21_tone_llms.parquet (article-level avg_subst_prob_score_{full,ctx,ss})
  - 14_materialize_ctx.parquet (content_ctx / content_ss)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
- doi: 10.18653/v1/2024.findings-emnlp.432
  type: journal
  authors: Renze, M.
  year: 2024
  title: "The effect of sampling temperature on problem solving in large language models"
  venue: "Findings of the Association for Computational Linguistics: EMNLP 2024"
  pages_or_artno: 7346-7356
- doi: 10.1177/20531680241236239
  type: journal
  authors: Heseltine, M., & Clemm von Hohenberg, B.
  year: 2024
  title: "Large language models as a substitute for human experts in annotating political text"
  venue: Research & Politics
  vol: 11
  issue: 1
  pages_or_artno: 20531680241236239
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
- doi: 10.1145/1102351.1102430
  type: journal
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: "Predicting good probabilities with supervised learning"
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: Administrative Science Quarterly
  vol: 39
  issue: 3
  pages_or_artno: 367-390
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"银行金融科技新闻在多大程度上被大模型判为象征性 (symbolic) 而非实质性 (substantive)"这一构念在银行-年度层面的聚合。构念根源是 Westphal & Zajac (1994, 1998) 提出的实质-象征 (substance-symbolic) 管理框架: 组织既可以通过真实改变运营与资源配置来回应制度压力 (实质性), 也可以通过发布姿态性、修辞性、脱耦 (decoupling) 的声明来营造合规印象而不改变实际行为 (象征性)。落到本项目, 每一篇被判定为"银行金融科技报道"的文章, 由 stage 21 情感 LLM 三家模型 (gpt54nano / gemini31 / deepseekv4) 各自独立就"该报道所述创新是实质性还是象征性"作二元投票, 每家模型输出一个经 logit-to-score 校准的概率分 prob_score, positive_class 锚定为"象征性"。文章级 avg_subst_prob_score = 对通过金科验证 (verified) 的模型的 prob_score 取均值, 取值域 [0, 1], 值越高代表越倾向被判为象征性/姿态性、越低代表越倾向被判为有实质技术或业务改变。该文章级列在 stage 21 `tone_llms.py::_aggregate_track` 产出, 是 18 元组返回值中的 `avg_subst_prob_score` 分量, 与情感 `avg_prob_score`、创新位点 `avg_locus_prob_score`、协作模式 `avg_collab_prob_score` 并列构成 LLM 分类维度的概率化测度。

【方法学与计算】
面板化在 stage 40 `panel/encode.py` 完成, 对同一 (target_bank, year) 单元内的全部文章级 avg_subst_prob_score 做两种聚合: 均值轨 `avg_subst_prob_score_{track}` = 组内 mean, 反映该行当年报道"象征性倾向"的集中水平; 标准差轨 `avg_subst_prob_score_std_{track}` = 组内 std, 反映该行当年不同报道之间在实质-象征判定上的离散/分歧程度。二者不是同一测度的替换标准化, 而是"水平"与"内部离散"两个正交信息面: 均值刻画中心位置, 标准差刻画组内异质性 (单观测 bank-year 的 std 为 NaN, 属数学退化而非缺陷)。概率分本身经监督式校准, Niculescu-Mizil & Caruana (2005) 论证经良好校准的概率输出比硬标签保留更多序信息, 因此以连续 prob_score 均值化优于对硬多数票计数; 大模型采样温度对二元判定稳定性有影响, 本项目 stage 21 一律钉 temperature=0.0 以贴合 Renze (2024) 关于低温提升确定性任务一致性的发现, 并使缓存键可复现。留篇口径遵循 full-only 门控 (2026-06-29): 一篇是否计入某银行-年度的报道宇宙, 仅由 full 轨的 LLM 金科验证决定, ctx/ss 轨的对应列为 conditional-on-full 的条件测度, 其行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。

【文献定位】
实质-象征二分的规范出处是 Westphal & Zajac (1994, 1998) 在 Administrative Science Quarterly 上确立的框架, 其核心洞见是"宣告"与"落实"之间可系统性脱耦, 这与本构念把新闻文本的"姿态性"从"真实改变"中分离的目标严格同构。在披露经济学一侧, Loughran & McDonald (2011) 奠定以文本量化企业真实态度的传统, Bingler et al. (2022) 与 Duchin, Gao & Xu (2025) 分别在气候披露与污染资产市场上给出"廉价空谈"与"漂绿"式象征行为的实证识别, 为把"象征性概率"作为一个可解释的公司行为信号提供外部效度参照。测量工具一侧, 本家族用大模型替代人工编码来标注实质-象征, 依据是 Gilardi, Alizadeh & Kubli (2023) 与 Heseltine & Clemm von Hohenberg (2024) 关于大模型在文本标注任务上可比甚至优于众包/专家的证据, 以及 Carlson & Burbano (2026) 为管理学研究使用大模型标注给出的操作规范与告警清单 (对齐、验证、稳健性披露), 本项目据此以三家模型独立投票 + verified 门控 + 概率校准来抑制单模型偏误。⚠ 三家模型的 per-model 子测度、三轨 (full/ctx/ss)、以及均值/标准差两轨, 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: avg_subst_prob_score_full

【变体差分】
canonical 轨, 也是本家族的头部主测度。full 的阅读文本口径 = 标题 prepend 后拼接全文正文, 即大模型看到的是"标题 + 完整正文"的一整篇报道, 未做任何实体窗口裁剪。本列在下游被赋予主轨地位: 它是 stage 39d 词典判别效度检验 lexical_discriminant_validity.py 中 T1 = LLM substance 的默认指标 (substance_col 取 avg_subst_prob_score_full), 与 A1 清晰度、A3 数字密集度共同构成 3×3 的 HTMT / AVE 判别矩阵, 用于验证"大模型判象征性"这一构念与词典化文本特征在测量上确实可分。计算上, 本列是 target_bank × year 单元内全部 full 轨留篇文章的文章级 avg_subst_prob_score 的算术均值, 取值域 [0, 1], 越接近 1 越倾向被判为象征性/姿态性叙事, 越接近 0 越倾向被判为有实质技术或业务改变。因为留篇门控采 full-only 口径 (2026-06-29), full 轨的行宇宙就是该银行-年度的完整报道集, 分母与 n_articles 口径严格一致, 不存在条件子集收缩, 这也是它区别于 ctx/ss 两条 conditional-on-full 轨的根本处。与同名标准差列 avg_subst_prob_score_std_full 的差别在于: 本列取分布的一阶矩 (中心水平), std 列取二阶矩 (组内离散), 两者是正交信息面而非标准化替换。与 ctx/ss 均值列互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。相较同源的创新位点 avg_locus_prob_score (positive_class=应用场景)、协作模式 avg_collab_prob_score (positive_class=外部协同) 两个 LLM 分类概率, 本列 positive_class 专锚"象征性"维度, 三者语义正交、各测各的构念, 不可互相替代或合并入同一识别式。

## VAR: avg_subst_prob_score_ctx

【变体差分】
ctx 轨稳健性变体, 非留篇门控轨。ctx 的阅读文本口径 = 标题 prepend + 实体上下文窗口, 即在标题之外只保留围绕目标银行/金科实体邻近的段落, 相对 full 主动剔除与目标实体无关的正文篇幅。设立本轨的目的是稳健性检验: 若一篇长报道大段落谈论与本行金科无关的内容, full 轨的象征性判定可能被这些无关篇幅稀释或污染, ctx 轨则把大模型的注意力约束在实体语境上, 用以验证"象征性水平是否对阅读窗口口径稳健"。计算上, 本列是 target_bank × year 单元内 ctx 轨文章级 avg_subst_prob_score 的算术均值, 取值域 [0, 1], 语义方向与 full 一致 (越高越象征)。因为留篇门控采 full-only 口径 (2026-06-29), 本列是 conditional-on-full 条件测度: 一篇是否进入该银行-年度的报道宇宙仍只由 full 轨的金科验证决定, 故本列的行宇宙是 full 留篇集的子集, per-track 列在该子集上照算, 不另立留篇标准。在早期试跑 T=2 面板上, ctx 轨常因样本稀薄而出现零方差或整体退化, 这是数据深度不足的预期表现, 生产 T=19 语料下正常。与 full/ss 均值列、以及同轨标准差列 avg_subst_prob_score_std_ctx 互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。ctx 与 ss 两条聚焦轨的根本差别在窗口判据: ctx 用实体上下文窗口 (实体邻近), ss 用银行∧金科同句共现 ±N 窗 (严格同句), 两者判据原语不同、不可互相复用, 因而是两条独立的稳健性证据而非冗余复制。

## VAR: avg_subst_prob_score_ss

【变体差分】
ss 轨稳健性变体, 非留篇门控轨, 是三轨中语义聚焦最严的一条。ss 的阅读文本口径 = 标题 prepend + 银行∧金科同句共现 ±N 窗 (窗半径由 config context_window.ss_sentence_radius 控制, 默认 1 句), 只保留银行与金融科技在同一句子层面强共现的上下文, 相比 ctx 的实体邻近窗更为苛刻。设立本轨意在最保守地界定"这句话确实在谈本行的金融科技"的语境, 从而检验象征性判定在最紧语义边界下是否依然成立。计算上, 本列是 target_bank × year 单元内 ss 轨文章级 avg_subst_prob_score 的算术均值, 取值域 [0, 1], 语义方向与 full/ctx 一致 (越高越象征)。回退语义严格镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 优雅降级为全文 body、ss_is_fallback=True, 并与 ctx 共享 n_articles 分母, 保证降级不清空、不产生单边孤儿。因为留篇门控采 full-only 口径 (2026-06-29), 本列同为 conditional-on-full 条件测度: 留篇与否只由 full 轨的金科验证裁定, 本列行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。在早期试跑 T=2 面板上本列常出现 zero-variance 退化, 属数据深度不足的预期表现, 生产 T=19 语料下恢复正常。与 full/ctx 均值列及同轨标准差列 avg_subst_prob_score_std_ss 互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。ss 与 ctx 的判据原语不同 (严格同句共现 vs 实体邻近窗), 二者是彼此独立的稳健性证据。

## VAR: avg_subst_prob_score_std_full

【变体差分】
full 轨的组内离散轨。区别于同轨均值列 avg_subst_prob_score_full 取一阶矩, 本列取二阶矩: 它是 target_bank × year 单元内全部 full 轨留篇文章的文章级 avg_subst_prob_score 的组内标准差 (std over articles per 单元), 而不是均值。⚠ 特别注意本列的 std 后缀不是"跨截面 z-标准化", 而是同一银行-年度内文章之间的样本标准差 (聚合口径见 encode.py 的 std aggregation), 这一点与其它家族里表示归一化的 std 后缀语义不同, 不可混淆。它衡量该银行当年不同报道之间在"实质 vs 象征"判定上的分歧/离散程度: 值越大代表当年舆论对该行金融科技叙事究竟是真改变还是姿态存在越大内部异质或争议, 值越小代表各报道口径越趋一致 (无论一致地判实质还是一致地判象征)。因此本列与均值列刻画的是同一分布的展布与中心两个正交信息面, 二者不是同一测度的两种归一, 联合使用可同时表征"象征性水平"与"象征性共识度"。单观测 bank-year (组内仅一篇报道) 的样本标准差为 NaN, 属数学退化而非缺失值注入, 下游需以缺失掩码处理。full 为留篇门控轨 (full-only, 2026-06-29), 分母与 n_articles 严格一致, 无条件子集收缩。与 std_ctx / std_ss 三轨、以及本轨均值列互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

## VAR: avg_subst_prob_score_std_ctx

【变体差分】
ctx 轨的组内离散轨, 非留篇门控轨。本列 = target_bank × year 单元内 ctx 轨文章级 avg_subst_prob_score 的组内样本标准差 (std over articles, 非跨截面 z-标准化), 度量在实体上下文窗口阅读口径下, 该行当年报道象征性判定的内部离散/分歧。它是 std_full 的稳健性变体: 相对 std_full, 本列在剔除文章中与目标实体无关的篇幅后再重算分歧, 用以检验"报道间的象征性判定离散是否由无关篇幅噪声人为放大"——若 std_ctx 与 std_full 走势一致, 说明离散是真实的舆论异质而非文本噪声伪影。语义方向与其它离散轨一致: 值越大内部争议越大, 值越小共识越强。因为留篇门控采 full-only 口径 (2026-06-29), 本列为 conditional-on-full 条件测度, 留篇裁定只由 full 轨金科验证决定, 行宇宙是 full 留篇集的子集, per-track 列在该子集上照算。单观测单元 (组内仅一篇) 的样本标准差为 NaN, 且早期试跑 T=2 面板上 ctx 轨可能因样本稀薄整体退化 (zero-variance), 均属预期表现, 生产 T=19 语料下恢复。与 std_full / std_ss 三轨、以及同轨均值列 avg_subst_prob_score_ctx 互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。ctx 与 ss 离散轨的差别沿袭均值轨: 判据分别为实体上下文窗口与银行∧金科同句共现窗, 判据原语不可互相复用。

## VAR: avg_subst_prob_score_std_ss

【变体差分】
ss 轨的组内离散轨, 非留篇门控轨, 是三轨离散测度中语义聚焦最严的一条。本列 = target_bank × year 单元内 ss 轨文章级 avg_subst_prob_score 的组内样本标准差 (std over articles, 非跨截面 z-标准化), 仅在银行∧金科同句共现 (窗半径默认 1 句) 语境下度量该行当年报道象征性判定的内部分歧。它衡量的是最紧语义边界下报道间的离散: 值越大代表即便只看强共现语句, 舆论对该行金科叙事是实质还是象征仍存显著争议; 值越小代表共识度高。回退语义严格镜像 ctx: 对无银行∧金科同句共现的文章, content_ss 优雅降级为全文 body、ss_is_fallback=True, 并共享 n_articles 分母, 故本列的离散实际在该降级集合上计算, 保证不产生单边孤儿。因为留篇门控采 full-only 口径 (2026-06-29), 本列为 conditional-on-full 条件测度, 留篇裁定只由 full 轨金科验证决定, 行宇宙为 full 留篇集的子集, per-track 列在该子集上照算。单观测单元 (组内仅一篇) 的样本标准差为 NaN, 且早期试跑 T=2 面板上本列常整体 zero-variance 退化, 均属预期, 生产 T=19 语料下恢复正常。与 std_full / std_ctx 三轨、以及同轨均值列 avg_subst_prob_score_ss 互为稳健性、不分主次、各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。本列刻画分布展布而非中心, 与 ss 均值列正交, 不得作同一测度的归一替换。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal. https://doi.org/10.1002/smj.70023
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Renze, M. (2024). The effect of sampling temperature on problem solving in large language models. Findings of the Association for Computational Linguistics: EMNLP 2024, 7346-7356. https://doi.org/10.18653/v1/2024.findings-emnlp.432
Heseltine, M., & Clemm von Hohenberg, B. (2024). Large language models as a substitute for human experts in annotating political text. Research & Politics, 11(1), 20531680241236239. https://doi.org/10.1177/20531680241236239
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML), 625-632. https://doi.org/10.1145/1102351.1102430
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
<!-- rendered-citations:end -->
