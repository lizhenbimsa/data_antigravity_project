---
family_id: F642
columns:
- you_2018_idf_score_w_sum_ctx
- you_2018_idf_score_w_sum_full
- you_2018_idf_score_w_sum_ss
unit: 无量纲 (IDF 加权情感分之提及密度加权和; bank-year 层面的分子级中间量, 供 VW 语调分母相除后方为无量纲比率)
formula: 'you_2018_idf_score_w_sum{track} = Σ_articles( you_2018_idf_score{track} × mention_density{track} ), 逐 bank-year 求和; 其中 you_2018_idf_score{track} 是文章级 you_2018 词典 IDF 加权情感分 (winsorized normalized-IDF 加权正负词计数后归一化), mention_density{track} 是同篇文章内目标银行提及密度权重 (Hassan et al. 2019 QJE value-weighted exposure 权重)。track ∈ {full, ctx, ss} 三轨独立计算, 权重 w=mention_density 与轨道无关但相乘对象 you_2018_idf_score 按轨取值。'
producer: pipeline\sentiment\tone_words.py (文章级 you_2018_idf_score{track} 计算, build_idf_weights/_build_idf_weighted_dict) ; pipeline\panel\runner.py (加权列预计算 you_2018_idf_score_w{track} = score × mention_density) ; pipeline\panel\encode.py (bank-year 聚合 sum 与下游 VW 语调比率 you_2018_idf_tone_vw{track})
upstream:
- you_2018_idf_score_full
- you_2018_idf_score_ctx
- you_2018_idf_score_ss
- mention_density
- sum_mention_density
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43–96
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: 'Word power: A new approach for content analysis'
  venue: Journal of Financial Economics
  vol: '110'
  issue: '3'
  pages_or_artno: 712–729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: A statistical interpretation of term specificity and its application in retrieval
  venue: Journal of Documentation
  vol: '28'
  issue: '1'
  pages_or_artno: 11–21
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673–719
- doi: 10.1080/00031305.2025.2539241
  type: journal
  authors: Sheridan, P., Ahmed, Z., & Farooque, A. A.
  year: 2026
  title: A Fisher's exact test justification of the TF–IDF term-weighting scheme
  venue: The American Statistician
  vol: '80'
  issue: '1'
  pages_or_artno: 146–156
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514–5532
- doi: "10.1093/rfs/hhad044"
  title: "Firm-Level Exposure to Epidemic Diseases: COVID-19, SARS, and H1N1"
  authors: "Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A."
  year: 2023
  venue: "The Review of Financial Studies"
  type: "journal"
- doi: "10.1016/j.finmar.2024.100896"
  type: "journal"
  authors: "Ashwin, J."
  year: 2024
  title: "Financial news media and volatility: Is there more to newspapers than news?"
  venue: "Journal of Financial Markets"
  vol: "69"
  pages_or_artno: "100896"
new_dois:
  - "10.1093/rfs/hhad044"
---

## CORE

【构念与来源】
F642 家族刻画的是「you_2018 中文金融情感词典在 IDF (逆文档频率) 加权口径下, 经提及密度再加权 (value-weighted) 后, 在 bank-year 层面累加得到的分子级中间量」。它处在两层加权的交叉点: 第一层加权发生在词层面 —— you_2018 词典 (You, Zhang & Zhang, 2018, 《Review of Financial Studies》「Who captures the power of the pen?」提出的官媒/市场化媒体口径下中文金融情感词表, 含 positive 1,425 词 / negative 1,583 词) 中每个情感词的贡献不再是等权计数, 而是按其在语料中的稀有程度赋权: 越是几乎每篇报道都出现的高频词 (如"发展""提高"), 携带的情感识别信息量越低, 权重被压低; 越是罕见但一旦出现就高度指向性的词 (如"违约""挤兑"), 权重被抬高。第二层加权发生在文章层面 —— 同一篇报道对不同银行的"提及密度" (mention_density, 即该银行相关词汇在文章中的出现强度) 不同, 文章对 bank-year 语调的贡献按提及密度再加权一次, 这是 Hassan et al. (2019, *QJE*) value-weighted (VW) 政策不确定性暴露测度范式在情感领域的移植: 一篇仅捎带提及某银行的报道, 不应与一篇通篇围绕该银行展开的深度报道等权计入该行的语调水平。`_w_sum` 是这条两层加权链路上承前启后的分子级中间量: 它把已经完成词级 IDF 加权的文章级得分 `you_2018_idf_score{track}`, 乘以文章级提及密度权重 `mention_density{track}`, 再在 bank-year 分组内求和, 尚未除以任何分母, 因此本身不是可直接解读语调水平的比率, 而是供下游 `you_2018_idf_tone_vw{track} = you_2018_idf_score_w_sum{track} / sum_mention_density{track}` 相除后才形成的、以提及密度加权的 IDF 语调均值的分子部件。

【方法学与计算】
计算链路分三步, 由三个不同 producer 接续完成。第一步 (`tone_words.py::build_idf_weights` / `_build_idf_weighted_dict`) 在全语料 (以去重后的 `content_full` 文本, 缺则回退裸「内容」列) 上, 对 you_2018 词典内每个情感词 w 计算 smooth IDF: raw_idf(w) = log₁₀(N / (1 + df(w))), 其中 N 是唯一文档数、df(w) 是包含该词的文档数 (fix omni-g-tonewords-04, 2026-06-11 起严格按去重后的唯一文档统计, 杜绝同一文章因"提及 8 家银行展开成 8 行"而虚增 N 与 df(w) 的同向膨胀); 再做均值归一化 normalized_idf(w) = raw_idf(w) / mean(raw_idf), 使加权后得分量级与不加权版本大致可比、可共用同一套语调阈值; 最后做 P1/P99 分位 Winsorization 削平极端权重, 防止个别超稀有词单独左右整篇文章的判分。三轨 (full/ctx/ss) 共享同一份基于 `content_full` 语料算出的 IDF 权重表, 绝不按轨分别估计语料 —— 这是刻意的方法学选择: 若按轨各自估计, ss 轨样本量小、极端稀有词的 df(w) 估计噪声大, 会让本应互为稳健性的三轨在权重层面就先行失真; 因此差异只体现在轨道各自的文本 (含哪些情感词、词频多少) 上, 而不体现在权重表本身。第二步在文章级用该 IDF 权重表对每篇文章 (每轨分别) 重新加权计分, 产出 `you_2018_idf_score{track}` (归一化后取值范围与未加权的 `you_2018_score{track}` 量级可比)。第三步是本家族三列所在的 panel 聚合层: `runner.py` 先用 `mention_density{track}` (银行在该文章中的提及强度) 对 `you_2018_idf_score{track}` 做逐文章相乘, 得到文章级加权列 `you_2018_idf_score_w{track}`; `encode.py` 再按 bank-year 分组对该列取 `sum` 聚合, 落地为本家族三列 `you_2018_idf_score_w_sum{full,ctx,ss}`。这三列本身不是最终语调测度, 而是与 `sum_mention_density{track}` 分母配对使用的分子: 下游 `you_2018_idf_tone_vw{track}` 语调变量正是用本家族列除以该分母得到。三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 禁止在同一个 over-identified 的 Hansen J 检验中混用; ss 轨若某篇文章没有银行与金科词汇的同句共现, 依 CLAUDE.md 回退语义镜像 ctx —— `content_ss` 回退为全文正文 (`ss_is_fallback=True`), 与 `n_articles` 分母共享同一套口径, 不产生单边孤儿列。留篇门控口径 (2026-06-29 起) 是 full-only: 一篇报道是否算作"一篇银行金科报道"只看 `llm_verified_full`, ctx/ss 是 conditional-on-full 的测度轨, 行宇宙是 full 留篇集合的子集, 但本族三轨各自的分子/分母仍按各自轨道逐项计算, 不借用 full 轨的分母去凑 ctx/ss 的比率。

【文献定位】
本家族的方法学谱系有三条主线交汇。其一是词典本身的出处: You, Zhang & Zhang (2018, *Review of Financial Studies*) 在「Who captures the power of the pen?」一文中构建并验证了官媒/市场化媒体双锚定的中文金融情感词典 (定义为 you_2018 词典的 positive/negative 及后续 v3.5.1 引入的 definite/ambiguous 子集), 是本项目情感词典族六部词典之一, 也是本家族测度赖以计分的底层情感极性来源。其二是 IDF 加权本身的谱系: Spärck Jones (1972, *Journal of Documentation*) 最早提出词项特异性的统计诠释, 是 IDF 权重的原始出处; Jegadeesh & Wu (2013, *Journal of Financial Economics*) 的 "Word Power" 把类似的逆文档频率式加权思想系统地引入金融文本内容分析, 论证词的稀有度信息应纳入情感/语调打分而非简单等权计数, 是本家族"词级 IDF 加权而非裸词典等权计数"这一设计选择的直接方法学先例; Sheridan, Ahmed & Farooque (2025/2026, *The American Statistician*) 近期从 Fisher 精确检验角度为 TF-IDF 权重方案提供了统计推断层面的正当性论证, 补强了本家族 smooth-IDF 加权公式并非纯粹工程经验规则、而是有统计检验基础支撑的判断。其三是本项目自身的方法学一致性来源: Du et al. (2022, *Review of Finance*) 的中文金融情感词典构建论文与 Bian et al. (2021, SSRN) 的中文情感词典本土化扩充工作, 与 you_2018 同属项目六词典族的姊妹词典, 共享同一套 IDF 加权/提及密度加权/三轨并排的处理管线, 论证本族的加权设计不是 you_2018 独有的特例而是跨词典一致落地的通用规则。此外 Frankel, Jennings & Lee (2022, *Management Science*) 关于机器学习与词典法测度语调互为稳健性的论证, 为本项目"词典法 (含 IDF 加权变体) / LLM 三家投票 / BERT 三模型" 三条测度路径各自 just-identified、互为稳健性而非相互嵌套检验的整体设计哲学提供了外部方法学支撑。此外, Hassan, Hollander, van Lent, Schwedeler & Tahoun (2023, The Review of Financial Studies) 将 Hassan et al. (2019, QJE) 提及密度加权 (value-weighted) 文本暴露测度范式延展应用于疫情语境, 为本家族 mention_density 提及密度再加权分子求和的方法学谱系提供了最新的顶刊延续性佐证。 在「报道量维度与报道所含信息内容须分作两列、由下游相除而非混同为单一测度」这一架构选择上, Ashwin (2024) 提供了近期的直接实证支撑: 该文把报纸报道的数量/篇幅维度与报道所含的新信息内容明确分离, 检验前者是否对波动率具有独立于后者的解释力, 论证了二者不可合并为同一个量。本家族恰处在这一分离的分子侧 —— `you_2018_idf_score_w_sum{track}` 只承载经词级 IDF 加权与文章级提及密度加权后的语调内容, 与之配对的 `sum_mention_density{track}` 才对应原文所指的「报道量」维度, 两者相除后方成为可解读的 vw 语调水平。迁移边界须诚实写出: 原文语料为英文报纸、结果变量是股票波动率, 其「报道量」是等权计数或版面维度, 既未使用提及密度权重亦未使用媒体权威度权重, 更不涉及中文六词典的 smooth-IDF 加权公式与三轨 (full/ctx/ss) 文本范围; 故该文只锚「量与内容须分离」这一架构必要性, 不构成对本家族任一加权层函数形式的证据。
## VAR: you_2018_idf_score_w_sum_ctx

【变体差分】
本列是 ctx 轨的加权和分子, 区别于家族内其余两列的精确差分点在于文本窗口: ctx 轨的文章级底层文本是 `content_ctx` (标题 + 目标银行实体窗口, 由 stage 14 `ctx_materializer` 在情感计分之前物化, 而非在情感阶段临时截取), 因此参与相乘求和的 `you_2018_idf_score_ctx` 是仅基于该实体窗口文本 (而非全文正文) 打出的 IDF 加权情感分。IDF 权重表本身与轨道无关 —— 三轨共享同一份基于 `content_full` 语料估计出的词级权重, 差异只体现在"哪些情感词、以多高词频出现在窗口内的文本里", 而不体现在权重取值本身; 这一设计避免了 ctx 轨样本文本量偏小导致的权重估计噪声反过来污染打分公式。乘数 `mention_density_ctx` 同样是 ctx 轨专属的提及密度权重 (基于同一实体窗口内的提及强度计算), 与 full 轨的 `mention_density_full` 数值上一般不相等。若某篇文章缺失 ctx 轨的实体窗口锚点 (`ctx_is_fallback=True`), 依三轨回退语义, `content_ctx` 退化为等同全文正文, 此时该篇对 ctx 轨 `you_2018_idf_score_w_sum_ctx` 的贡献在数值上趋同于该篇对 full 轨的贡献, 但仍作为独立观测计入 ctx 轨的分组求和, 不与 full 轨发生数据层面的合并或借用。作为「留篇门控 = full-only」体系下的 conditional-on-full 测度轨, 本列所覆盖的 bank-year 行宇宙是 full 轨留篇集合的子集: 一篇文章是否被判定为"一篇银行金科报道"只依据 `llm_verified_full`, ctx 轨不独立决定文章的取舍, 只在该篇已通过 full 轨门控的前提下, 按 ctx 轨自身的文本与权重重新计分求和。本列与 `_full`/`_ss` 两列互为稳健性并排, 不构成对 canonical 全文轨的替代或校正, 三者绝不可混入同一个 over-identified 的 Hansen J 过度识别检验框架中联合使用, 也不应在同一回归右侧同时纳入多轨造成人为共线膨胀。

## VAR: you_2018_idf_score_w_sum_full

【变体差分】
本列是家族的 canonical / 全文轨, 是三轨中信息覆盖面最完整、也是当前 P1 主线 (`bank_fintech_tone`) 与留篇门控体系所依赖的基准口径: 其底层文章级情感分 `you_2018_idf_score_full` 基于标题 + 完整正文 (`content_full`, prepend_title 拼接而成) 计分, 覆盖文章全部文本信息而不做任何窗口截取或同句约束。乘数 `mention_density_full` 是基于全文文本计算的银行提及密度权重, 在三轨中通常样本覆盖最广、缺失率最低, 因为它不依赖实体窗口锚点或银行-金科同句共现这类更严格的结构性判据是否成立。stage 21 情感留篇门控 (2026-06-29 起) 明确以 `llm_verified_full == True` 作为唯一的"是否算一篇银行金科报道"判据, 因此本列的分子求和口径直接决定了哪些 bank-year 观测进入留篇集合, 而 ctx/ss 两轨是在本列锚定的行宇宙子集上条件计算的稳健性/补充测度轨, 不能反过来影响 full 轨的取舍。本列与 ctx/ss 两轨在方法学地位上互为稳健性、不分主次并排陈列, 但在实际论文写作与 P1 处理变量选择上, `_full` 后缀轨(及其派生的 `you_2018_idf_tone_vw_full`)是当前主线默认引用的口径; 三轨仍须各自 just-identified、禁止混入同一 over-identified Hansen J 检验。作为 IDF 加权×提及密度加权的双层加权分子, 本列数值本身量级会随语料规模、bank-year 内文章篇数及各篇提及密度分布而变化, 不能脱离对应的 `sum_mention_density_full` 分母单独解读为语调水平, 必须结合下游派生的 VW 语调比率变量一并使用。

## VAR: you_2018_idf_score_w_sum_ss

【变体差分】
本列是三轨中判据最严格的 ss (同句共现) 轨: 底层文章级情感分 `you_2018_idf_score_ss` 依据的是 `content_ss` 文本, 即标题 + 「目标银行与金科关键词同句 (可配置 ±N 句窗口半径, 默认半径 1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 与 stage 13 硬过滤所用的 `cooccurrence_filter.sentence_radius` 是两个不同的配置键, 不可混淆)」的窗口文本, 是三轨中对"银行∧金科话题真正同句出现"这一构念要求最苛刻的一支。乘数 `mention_density_ss` 是基于该同句窗口文本计算的提及密度权重, 与 full/ctx 两轨的提及密度取值一般不相等, 且更容易因窗口文本过短而在个别文章上出现较低的密度估计。若某篇文章不存在银行与金科词汇的同句共现 (即不满足 ss 轨的结构性判据), 依 CLAUDE.md 铁律 ss 轨回退语义严格镜像 ctx 轨: `content_ss` 退化为全文正文、`ss_is_fallback=True`, 与 `n_articles` 分母共享同一套口径优雅降级, 而非静默清空或产生单边孤儿观测; 该篇仍以退化后的全文文本参与 ss 轨的 IDF 加权情感打分与提及密度加权求和。作为留篇门控体系下 full-only 之外的 conditional-on-full 稳健性轨, 本列覆盖的 bank-year 观测行宇宙同样是 full 轨留篇集合的子集, 且由于 ss 轨判据更严格, 在实证上其非退化观测占比通常低于 ctx 轨 (dev 小样本早期试跑 T=2 语料下二者甚至可能因数据规模过小而呈现零方差退化, attribut 于样本规模而非测度失效)。本列与 `_full`/`_ctx` 两列在方法学上并排互为稳健性, 三者共同验证"银行-金科语调关联是否对文本窗口宽严的具体设定敏感", 而非构成层层嵌套的主/辅关系, 使用时须与 `_full`/`_ctx` 分别独立进入回归右侧或分别汇报, 严禁混入同一个 over-identified Hansen J 框架联合估计。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43–96. https://doi.org/10.1093/rfs/hhx055
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712–729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11–21. https://doi.org/10.1108/eb026526
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673–719. https://doi.org/10.1093/rof/rfab036
Sheridan, P., Ahmed, Z., & Farooque, A. A. (2026). A Fisher's exact test justification of the TF–IDF term-weighting scheme. The American Statistician, 80(1), 146–156. https://doi.org/10.1080/00031305.2025.2539241
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514–5532. https://doi.org/10.1287/mnsc.2021.4156
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-Level Exposure to Epidemic Diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies. https://doi.org/10.1093/rfs/hhad044
Ashwin, J. (2024). Financial news media and volatility: Is there more to newspapers than news? Journal of Financial Markets, 69, 100896. https://doi.org/10.1016/j.finmar.2024.100896
<!-- rendered-citations:end -->
