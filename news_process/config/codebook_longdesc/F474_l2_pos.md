---
family_id: F474
columns:
- pos_frac_ctx
- pos_frac_full
- pos_frac_ss
unit: 占比 (proportion), 值域 [0, 1]
formula: 'pos_frac{track} = mean(is_positive{track}), 其中 is_positive{track} = 1{llm_vote_score{track} == 1}; llm_vote_score 是三家大语言模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 对同一篇文章-银行样本作情感三分类 (正面=1/中性=0/负面=-1) 后取多数投票 (majority vote) 共识; bank-year 聚合在 stage 40 (encode.build_aggregation_dict) 以 groupby(target_bank, year).mean() 完成'
producer: pipeline\panel\encode.py (build_aggregation_dict L755, encode_sentiment 门控 L289) ; pipeline\panel\runner.py (步骤2 encode_sentiment 调用点) ; pipeline\panel\codebook.py (_SENT_DIAG_SPECS 元数据)
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss, 三家 LLM 逐篇投票共识)
- 24_herd_decay.parquet (df_exploded, stage 21 语义精筛后 article×bank 级 verified 集; 是 40_panel_export_main 的主读入口)
citations:
- doi: 10.1111/jofi.13287
  type: journal
  authors: Fedyk, A.
  year: 2024
  title: 'Front-page news: The effect of news positioning on financial markets'
  venue: The Journal of Finance
  vol: '79'
  issue: '1'
  pages_or_artno: 5-33
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: Measuring corporate culture using machine learning
  venue: The Review of Financial Studies
  vol: '34'
  issue: '7'
  pages_or_artno: 3265-3315
- doi: 10.48550/arxiv.2406.07791
  type: arxiv
  authors: Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S.
  year: 2024
  title: 'Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge'
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
pos_frac 家族刻画的是"一家银行在某一年度里, 被大语言模型判定为正面情感的报道占其全部有效报道的比例"这一类别先验型 (class-prior) 诊断量, 属于本项目情感测度体系 (P1 `bank_fintech_tone`) 的分类分布诊断分支, 而非核心处理变量 (treatment) 本身。核心处理变量是连续的 `llm_vote_tone{track}` (三家 LLM 逐篇三分类标签取多数投票后, 在 bank-year 层取均值), pos_frac 与其姊妹列 neg_frac 共同回答一个更基础的问题: 在这批以银行与金融科技共现为筛选前提的报道语料里, 正面/负面/中性三档标签各占多大比例, 从而支撑测量学 (measurement) 稳健性叙事里的"类别先验"诊断——即判断连续均值指标背后的样本分类结构是否偏斜、是否存在某一档极度稀薄导致统计功效退化的问题。源码模块 `pipeline/panel/codebook.py` 中的 `_SENT_DIAG_SPECS` 明确将其定位为"支撑 SENT CV-1 measurement 节的类别先验诊断", 并记录了一个重要的经验事实: 负面类占比 neg_frac 在验证语料上实测约 0.24%, 呈现出近乎退化 (near-degenerate) 的分布, 这使得任何依赖负面子样本方差的稳健性检验都需要格外小心样本量与零方差风险; pos_frac 作为负面类占比的镜像互补量, 其分布形态同样是判断整体标签分布是否失衡的关键参考。这种诊断设计延续了文本分类研究中对标签基率 (base rate) 保持透明披露的一贯要求, 与 Li, Mai, Shen & Yan (2021) 在测量企业文化时同步报告标签分布基本统计以证明测度未被某一极端类别主导的做法呼应——当研究者用连续情感均值做回归时, 读者有权知道这一均值背后的原始分类构成是"多数正面/少数负面"还是"接近对称", 因为极端不对称的基率会影响标准误估计与显著性推断的可信度。

【方法学与计算】
计算链路起于 stage 21 (`21_tone_llms.py`): 每篇文章-银行样本经三家独立厂商大语言模型 (gpt-5.4-nano、gemini-3.1-flash-lite 两家走 yunwu 中转、deepseek-v4-flash 直连 api.deepseek.com) 各自独立打出情感三分类标签 (正面/中性/负面), 三票取多数一致的共识记为 `llm_vote_score{track}` ∈ {-1, 0, 1}。该共识判定与嵌入模型无关, 是一套完全独立的 LLM 语义判断链路 (CLAUDE.md 铁律: 嵌入 ≠ LLM)。到了 stage 40 面板导出阶段, `pipeline/panel/encode.py` 的 `encode_sentiment` 函数把 `llm_vote_score{track} == 1` 的布尔判定物化为文章级 nullable Int8 指示列 `is_positive{track}` (同时产出 `is_negative{track}`/`is_neutral{track}` 三分类完整指示列族)。随后在 `build_aggregation_dict` 的 GroupBy 聚合字典里, `pos_frac{track}` 被定义为对 `is_positive{track}` 取 `mean` 聚合、`pos_count{track}` 取 `sum` 聚合, 两者在同一 bank-year 分组内共享同一个分母——该 bank-year 单元内三轨各自的有效 (verified) 文章篇数。需要强调的是, `mean(is_positive)` 与后文的 `sum(is_positive)` 是同一构念下"比例"与"计数"两种呈现: pos_frac 关心相对占比, pos_count (属另一家族) 关心绝对篇数, 二者配合可以同时判断"某银行年度报道情感是否偏正面"与"该结论是否建立在足够大的样本上"。留篇门控口径遵循 full-only 铁律 (2026-06-29 起): 一篇报道是否算作"银行-金融科技相关的一篇有效报道"只以 `llm_verified_full == True` 为准, ctx/ss 轨的分类计算是在这一 full 轨确定的行宇宙子集上做的条件测度 (conditional-on-full), 三轨各自独立计算 `is_positive{track}` 与其对应的 pos_frac{track}, 互不借用彼此的分母。

【文献定位】
以类别标签占比 (base-rate diagnostic) 的方式披露文本分类结果的分布结构, 呼应了文本情感/文本分类测量文献里对报告连续分数之前必须先说明其背后离散标签基率分布的一贯要求, 否则读者无法判断该分数的统计性质。近年基于大语言模型的文本分类研究进一步凸显了这一诊断的必要性: Li, Mai, Shen & Yan (2021, *The Review of Financial Studies*) 用机器学习方法测量企业文化时同样报告了标签分布的基本统计, 以证明测度并非被某一极端类别主导; 更贴近本项目 LLM-as-judge 判定机制的方法学关切见 Shi, Ma, Liang, Diao, Ma & Vosoughi (2024, *arXiv*) 关于 LLM 作为评判者存在位置偏差 (position bias) 的系统性研究, 这类偏差风险也是本项目坚持三家独立厂商 LLM 多数投票而非单一模型判定的方法学动机之一——单一模型的类别先验漂移会直接污染 pos_frac 这类占比诊断, 而多家独立模型投票能够部分抵消系统性偏差。三轨 (full/ctx/ss) 并排设计的思路则与 Fedyk (2024, *The Journal of Finance*) 关于新闻文本呈现位置 (front-page positioning) 对市场反应存在因果效应的发现相呼应——正如新闻的呈现方式会系统性影响读者解读, 情感判定所依赖的文本窗口 (全文 vs 实体上下文 vs 银行与金科同句共现) 同样可能系统性影响标签基率, 因此本项目要求三轨各自独立诊断、互不替代。

## VAR: pos_frac_full

【变体差分】
pos_frac_full 是全文轨 (full track) 的正面类占比, 分子 `is_positive_full` 取自 `llm_vote_score_full == 1`, 该判定基于 LLM 阅读"标题+完整正文" (`content_full`, prepend_title 拼接标题) 后给出的情感三分类, 是留篇门控的锚定轨——一篇文章是否计入"银行-金融科技相关有效报道"的行宇宙, 完全由 `llm_verified_full == True` 决定 (2026-06-29 起的 full-only 门控铁律)。因此 pos_frac_full 的分母 (bank-year 单元内 full 轨有效篇数) 同时也是 ctx 轨与 ss 轨行宇宙的上界: ctx/ss 两轨的分子分母都只能在 full 轨确定"这是一篇有效报道"之后才谈得上进一步的窗口内分类, 不存在某篇文章 full 轨未被判定为有效、却单独出现在 ctx 或 ss 轨分母里的情形。作为家族 canonical 轨道, pos_frac_full 是 P1 主处理变量 `llm_vote_tone_full` 所依赖的同一票源分类结果, 二者共享 `llm_vote_score_full` 这一底层列, 前者取三分类中"正面"这一档的占比, 后者取 {-1,0,1} 的连续均值——可以把 pos_frac_full 理解为 llm_vote_tone_full 这个连续测度背后的类别构成剖面之一, 二者互相印证但不可替代: 均值可能因为正面票数多但每票强度不同而与占比走势不完全一致, 因此实证分析中常把二者并列报告, 用占比佐证均值的稳健性。由于 full 轨同时是留篇门控锚点, pos_frac_full 的分母随时间、随银行样本量变化的稳定性直接决定了整张 bank-year 面板的覆盖质量, 该列在诊断意义上也承担着监控样本平衡度的角色——若某银行某年 full 轨有效篇数极小, 该单元的 pos_frac_full 将呈现高方差、易受个别文章标签翻转影响, 这与该家族在测量学 (measurement) 一节反复强调的"类别先验 + 极小 N 子样本"风险直接相关。

## VAR: pos_frac_ctx

【变体差分】
pos_frac_ctx 是实体上下文轨 (entity-context track) 的正面类占比, 分子 `is_positive_ctx` 取自 `llm_vote_score_ctx == 1`, 该判定基于 LLM 阅读"标题+目标银行实体窗口文本" (`content_ctx`) 后给出的情感三分类。ctx 轨聚焦于目标银行实体周边的局部语境, 与 full 轨 (通篇语境) 构成互为稳健性、不分主次的并排关系——两者各自 just-identified, 绝不可混入同一个 over-identified 的 Hansen J 检验框架。当某篇文章不存在可提取的实体窗口时 (即 `ctx_is_fallback = True`), `content_ctx` 回退为全文 body, 该行样本仍参与 ctx 轨的 pos_frac_ctx 计算, 但其信息来源实质上退化为与 full 轨相近的文本。ctx 轨的行宇宙是 full 轨留篇门控行宇宙的条件子集 (conditional-on-full): 一篇文章能否进入 pos_frac_ctx 的计算, 首先要求其在 full 轨被判定为有效报道, 其次才谈 ctx 轨自身的分类与分母统计, 因此 ctx 轨的分母不与 full 轨的分母相互独立计算, 也不借用 full 轨的分母数值。ctx 轨设计的核心动机是把 LLM 的注意力从全篇内容收窄到与目标银行直接相关的语句片段, 从而降低文章中与该银行无关的其余段落 (例如同一篇报道里其他银行、宏观背景、监管政策等段落) 对情感判定的稀释或污染效应; 这意味着 pos_frac_ctx 与 pos_frac_full 即便在同一 bank-year 单元、同一分母上计算, 也完全可能给出不同的正面占比数值——full 轨可能因通篇基调偏正面而拉高占比, ctx 轨则更精准地反映"文章具体谈到这家银行时"的语气。二者的差异本身就是一种有信息量的诊断: 若两轨占比高度一致, 说明该银行相关段落的语气与全文基调趋同; 若出现系统性偏离, 则提示该银行的报道更多是"背景提及"而非"焦点评述"。按照三轨并排铁律, pos_frac_ctx 与 pos_frac_full、pos_frac_ss 在计量设定中必须各自作为独立的 just-identified 测度使用, 例如各自单独进 OLS/固定效应回归的右手边或各自单独构造工具变量, 而不能三者同时塞进同一个 over-identified 的 Hansen J 检验框架, 这一约束在 CLAUDE.md 的三轨铁律中被反复强调, 目的是防止研究者把"互为稳健性"的并排测度误用成可以联合识别的过度识别工具集。

## VAR: pos_frac_ss

【变体差分】
pos_frac_ss 是同句共现轨 (same-sentence track) 的正面类占比, 分子 `is_positive_ss` 取自 `llm_vote_score_ss == 1`, 该判定基于 LLM 阅读"标题+目标银行与金融科技词严格同句共现窗口文本" (`content_ss`, 句子半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制、默认 1) 后给出的情感三分类, 判定口径较 ctx 轨更为严格 (逐句扫描, 要求银行实体与金融科技词汇落在同一句或相邻窗口内)。ss 轨的回退语义镜像 ctx 轨: 当一篇文章不存在银行与金融科技词的同句共现时, `content_ss` 回退为全文 body, 对应 `ss_is_fallback = True`, 该样本仍计入 pos_frac_ss 的分母, 与 ctx 轨共享"回退 = 全文降级、分母不排除"的统一处理原则; 若 `FINTECH_AC` 词典构建失败为 None, 则 `*_is_fallback` 全体置 True, 三轨优雅降级为等同全文的判定。与 pos_frac_full、pos_frac_ctx 一样, pos_frac_ss 的行宇宙同样是 full 轨留篇门控行宇宙的条件子集, 三轨各自独立聚合、互为稳健性, 分析时不应把三条 pos_frac 序列同时作为工具或内生解释变量塞进同一个过度识别 (over-identified) 的 Hansen J 检验设定。ss 轨的判定口径来自 `core/text/entity_context.py` 中与 stage 13 共现硬过滤不同的另一原语 (严格同句抽取, 而非 ±1 句窗口的共现硬过滤判据), 二者刻意不复用同一函数, 以避免"用于筛选哪些文章进入语料"的判据与"用于情感窗口取文的判据"混同。pos_frac_ss 由于其分子分母都建立在"银行与金融科技词严格同句共现"这一更苛刻的条件之上, 相较 pos_frac_ctx 通常会有更小的有效样本, 在 T=2 的开发期小样本上零方差或极小 N 的退化风险也更为突出, 这与家族整体强调的类别先验诊断意义高度一致——ss 轨恰恰是最容易在稀薄样本下暴露"正面类占比看似极端 (0 或 1) 实为样本量过小所致"这一测量学陷阱的轨道, 因此在解读 pos_frac_ss 时应同时参照其配套的篇数分母 (`n_articles_llm_valid_ss` 或等价计数列), 避免脱离样本量单独解读占比数值。

<!-- rendered-citations:begin -->
Fedyk, A. (2024). Front-page news: The effect of news positioning on financial markets. The Journal of Finance, 79(1), 5-33. https://doi.org/10.1111/jofi.13287
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Shi, L., Ma, C., Liang, W., Diao, X., Ma, W., & Vosoughi, S. (2024). Judging the Judges: A Systematic Study of Position Bias in LLM-as-a-Judge. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2406.07791
<!-- rendered-citations:end -->
