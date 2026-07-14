---
family_id: F653
columns:
- you_2018_tone_sum_ctx
- you_2018_tone_sum_full
- you_2018_tone_sum_ss
unit: 语调得分之和 (article-level 归一化语调 ∈ [-1,1] 逐篇求和; bank-year 维度上无上下界, 量级随该行业-年报道量线性增长)
formula: 'you_2018_tone_sum{track} = Σ_{a∈bank-year} you_2018_score{a,track}; 其中单篇 you_2018_score = total_score / total_abs_score (total_abs_score>0 时), 否则记 0.0; total_score = Σ_token(base_score×degree_multiplier×negation×adversative_boost), base_score 取自 you_2018 词典 (positive 1,425 / negative 1,583 词, ±1 起分), degree_multiplier 由程度副词表决定 (最高 ×3.0), 遇 NEGATION_WINDOW 内否定词翻号, 遇 ADVERSATIVE_WORDS 后续 token 再 ×ADVERSATIVE_BOOST(=1.5); track ∈ {full,ctx,ss} 各自独立计算再各自求和'
producer: pipeline\sentiment\tone_words.py (article-level you_2018_score 计算, config/tone_dicts.json::you_2018 词典源) ; pipeline\panel\encode.py::_build_llm_bank_year_agg 附近 C 段 (agg[f'{d}_tone_sum{track}'] = (f'{d}_score{track}', 'sum'), d 迭代 DICT_NAMES 含 you_2018)
upstream:
- 21_tone_llms (留篇门控 llm_verified_full, 决定该篇是否计入 bank-year 分组)
- 14_materialize_ctx (content_ctx/content_ss 三轨文本物化)
- 22_tone_words (article-level you_2018_score_full/_ctx/_ss 逐篇产出)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J.; Zhang, B.; Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z.; Huang, A. G.; Wermers, R.; Wu, W.
  year: 2022
  title: 'Language and Domain Specificity: A Chinese Financial Sentiment Dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R.; Jennings, J.; Lee, J.
  year: 2022
  title: 'Disclosure Sentiment: Machine Learning vs. Dictionary Methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M.; Brooke, J.; Tofiloski, M.; Voll, K.; Stede, M.
  year: 2011
  title: Lexicon-based methods for sentiment analysis
  venue: Computational Linguistics
  vol: '37'
  issue: '2'
  pages_or_artno: 267-307
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, Paul C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"银行-金科报道的词典法语调总量" (dictionary-based tone volume), 使用 You, Zhang & Zhang (2018, RFS)《Who Captures the Power of the Pen?》构造的中文金融情感词典 (you_2018) 对每篇报道逐词打分、逐篇归一化后, 在 bank-year 层面对同一银行、同一年度所有留篇报道的归一化语调求和。you_2018 词典收录 positive 1,425 词、negative 1,583 词 (SSOT = `config/tone_dicts.json::you_2018`, 词典加载逻辑见 `pipeline/sentiment/tone_words.py`), 并额外收录 definite(388)/ambiguous(178) 两类非极性词表, 后者供 clarity 族测度使用、与本家族语调无关。you_2018 词典与本仓另五部词典 (jiang_2021、yao_2021、bian_2021、du_2022、loughran_mcdonald_zh_2026) 并列为「词典消融梯度」下的六部并行词典之一, 六部词典互为稳健性、不设优先级, 详见家族区分段落。you_2018 语调家族在本仓的角色是 Frankel, Jennings & Lee (2022, *Management Science*) 所强调的「机器学习 vs. 词典法互为稳健性」三角中词典臂的其中一支具体实现, 与本仓 LLM 三家投票 (stage 21) 及 BERT 三模型 (stage 23) 情感测度并列、互不替代。

`_tone_sum` 是该家族 sum 聚合口径的落地列, 与同族 `_tone` (mean) 和 `_tone_std` (std) 三者共用同一个 article-level 源列 `you_2018_score{track}`、仅聚合函数不同。`_tone_sum` 本身不是归一化比率, 而是把 bank-year 内每篇报道 [-1,1] 区间的归一化语调值直接相加, 因此其数值量级正比于该银行-年度落入 you_2018 留篇集合的报道篇数 (`n_articles_llm_valid{track}`), 篇数越多、`_tone_sum` 的绝对值上限越高; 与之相对, `_tone` (mean) 才是去除篇数规模效应后可跨银行-年份直接比较语调水平的口径。`_tone_sum` 的经济含义更接近"该银行-年度在媒体上被赋予的正面语调净存量"(一种类似媒体关注度加权的净情感暴露), 适合作为 herd 加权/媒体权威加权等下游构造的分子, 或用于检验篇数规模是否驱动结果 (与 `_tone` mean 版本对照可分离出规模效应 vs. 强度效应)。

【方法学与计算】
article-level `you_2018_score{track}` 的计算发生在 stage 22 (`pipeline/sentiment/tone_words.py`), 对每篇文章的分词结果逐 token 扫描: 命中 you_2018 正/负词表则取 base_score (±1); 若该 token 落在此前否定词 (`NEGATION_WORDS`) 触发的 `NEGATION_WINDOW` (默认 2 个 token) 窗口内则翻号; 若 token 前是程度副词则乘以 degree_multiplier (最高 ×3.0); 若处于转折词 (`ADVERSATIVE_WORDS`) 之后的从句作用域内 (以句末标点重置) 则再乘以 `ADVERSATIVE_BOOST`(默认 1.5)。逐 token 的 final_score 累加得 total_score, 其绝对值之和为 total_abs_score, 该篇归一化分数 `normalized_score = total_score / total_abs_score` (若 total_abs_score=0 则记 0.0), 恒落在 [-1, +1] 区间 —— 分子分母同含 degree×adversative 权重, 与旧版"裸匹配词数做分母"的口径不同 (源码注释明确标注此为当前生产口径, 旧分母已弃用)。这一逐篇归一化分数即为面板聚合时的 `you_2018_score{track}` 源列。

在 stage 40/`pipeline/panel/encode.py` 的 bank-year 聚合中, `_tone_sum{track}` 由 pandas groupby-agg 对该 bank-year 分组内所有留篇报道的 `you_2018_score{track}` 取 `sum`, 与 `_tone{track}`(mean)、`_tone_std{track}`(std) 共用同一分组和同一源列, 三者是同一底层分布的三个描述统计量、不构成独立测度。留篇门控 (2026-06-29 起) 遵循 full-only 铁律: 一篇报道是否计入某银行-年度的 you_2018 语调分组, 仅由 `llm_verified_full == True` 判定; `_ctx`/`_ss` 两条轨的行宇宙是 full 留篇集合的子集, 在该子集上各轨独立按 ctx/ss 文本重新跑一遍 you_2018 词典打分再求和, 不与 full 轨共享篇数以外的任何计算结果。

【文献定位】
you_2018 词典源自 You, Zhang & Zhang (2018, *The Review of Financial Studies*)「Who Captures the Power of the Pen?」, 该文构造中文金融情感词典并用于识别媒体报道对企业信息环境的塑造作用, 是本仓引用最广的中文金融情感词典锚点之一 (家族命名直接沿用其作者-年份)。词典法与机器学习法 (LLM/BERT) 的互补关系呼应 Frankel, Jennings & Lee (2022, *Management Science*)「Disclosure Sentiment: Machine Learning vs. Dictionary Methods」的核心论点: 词典法透明、可复现、无需训练数据, 但对语境/反讽/长距离否定不敏感; 机器学习法则相反。词典法内部的否定翻转、程度副词加权、转折降权三条语言学规则的设计脉络参见 Taboada et al. (2011, *Computational Linguistics*)「Lexicon-based methods for sentiment analysis」对 lexicon-based 情感分析中"取反+强化词+转折词"标准处理框架的系统梳理; 本仓 you_2018 计算引擎的 negation/degree/adversative 三段式流水线正是该框架在中文金融文本上的具体落地。you_2018 词典与本仓另一常用中文金融情感词典 du_2022 (Du, Huang, Wermers & Wu, 2022, *Review of Finance*)「Language and Domain Specificity: A Chinese Financial Sentiment Dictionary」并列构成六部词典消融梯度的两个代表性节点, 二者构词范围、正负词数比例不同 (you_2018 正 1,425/负 1,583 略偏负; du_2022 另含政治正面词敏感性三权重梯度, you_2018 无此维度), 详细差异属家族间对比不在本家族内部展开。

## VAR: you_2018_tone_sum_full

【变体差分】
`_full` 是全文轨: article-level `you_2018_score_full` 的输入文本是 stage 14 物化的 `content_full` (标题+全文正文 prepend_title 拼接), 覆盖该篇报道在银行-金科语境判定之外的全部正文信息。留篇门控本身即以 `llm_verified_full` 为唯一判据 (2026-06-29 起 full-only 铁律), 因此 `_full` 轨天然对齐门控口径、行宇宙 = 该银行-年度全部留篇报道 (无子集缩窄)、`n_articles_llm_valid_full` 即该 bank-year 分母。`_full` 与 `_ctx`/`_ss` 三轨在本仓设计上各自独立打分与求和、互为稳健性并排, 不分主次, 严禁把三轨语调列混入同一个 over-identified Hansen J 检验 (会破坏 just-identified 结构)。相对 `_ctx`/`_ss`, `_full` 轨捕捉的是整篇报道 (含与银行/金科无关段落) 的语调总氛围, 更贴近传统媒体语调文献 (如 Tetlock, 2007, *Journal of Finance*《Giving Content to Investor Sentiment: The Role of Media in the Stock Market》以整篇新闻报道为分析单位的语调度量传统) 的"整篇文章语调"构念, 但也因此更容易被报道中与目标银行无关的段落稀释或污染。

由于 `_full` 轨的行宇宙即留篇门控本身的判定集合, 不存在任何回退子集或缩窄逻辑, `_full_tone_sum` 是三轨中唯一"篇数分母天然与门控分母一致、无 fallback 标记"的一支, 因而也是三轨中数值最稳定、最少受下游窗口/共现判据影响的版本。作为规模型 (sum) 统计量, `_full_tone_sum` 的绝对水平会随该银行-年度报道覆盖量增长而线性放大, 使用者若要比较不同银行-年度间语调"强度"而非"存量", 应改用同源 `_tone_full` (mean) 而非本列; 若要构造媒体关注度加权的净情感暴露指标 (如作为 herd 加权或媒体权威加权分子), 则 `_full_tone_sum` 是三轨中口径最贴合门控定义、最适合直接使用的一支。

## VAR: you_2018_tone_sum_ctx

【变体差分】
`_ctx` 是实体窗轨: article-level `you_2018_score_ctx` 的输入文本是 stage 14 物化的 `content_ctx` (标题+目标银行实体名周边窗口文本), 意在把打分范围收窄到与目标银行直接相关的语句邻域, 降低无关段落对语调的稀释。行宇宙与 `_full` 相同 (留篇门控仍由 `llm_verified_full` 判定, `_ctx` 不单独决定是否留篇), 但打分输入文本不同, 故 `you_2018_score_ctx` 与 `you_2018_score_full` 是两套独立计算结果, 不存在算术恒等关系。若某篇报道未产出有效实体窗口 (无法定位银行实体上下文), `content_ctx` 按约定回退为全文 body、并以 `ctx_is_fallback` 标记, 该回退语义与 `_ss` 轨的回退机制对称。`_ctx_tone_sum` 与 `_full_tone_sum`、`_ss_tone_sum` 三者互为稳健性并排, 禁止混入同一 over-identified Hansen J。

`_ctx` 的设计动机是缓解全文轨可能出现的"稀释"问题: 一篇报道即使被判定为银行-金科相关报道 (通过留篇门控), 其正文中仍可能包含大段与该银行无直接关系的背景介绍、行业综述或其他企业信息, 若逐词打分覆盖全文, you_2018 词表命中的情感词有相当比例来自这些无关段落, 使 `_full_tone_sum` 偏离"该银行本身的媒体语调"这一构念。`_ctx` 通过把打分输入收窄到实体名周边窗口, 试图更精确地捕捉与目标银行直接相关语句的情感极性, 代价是当窗口过窄或实体识别失败时依赖回退机制、可能引入与 `_full` 趋同的观测。在本机 dev 样本 (T=2, 银行覆盖有限) 上 `_ctx` 相对 `_full` 的边际信息量可能不明显, 生产全量语料下二者的差异化预期更充分显现, 应对照 `_full_tone_sum` 一并解读、不单独作为主结论依据。

## VAR: you_2018_tone_sum_ss

【变体差分】
`_ss` 是同句轨: article-level `you_2018_score_ss` 的输入文本是 stage 14 物化的 `content_ss` (标题+银行∧金科关键词同句共现窗口, 窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句), 是三轨中打分范围最窄、最严格聚焦"银行与金科同时出现"语境的一支。`_ss` 的回退语义镜像 `_ctx`: 若某篇报道不存在银行∧金科同句共现, `content_ss` 回退为全文 body、`ss_is_fallback` 标记为 True, 与 `_ctx_is_fallback` 共享同一套"优雅降级、不静默清空"的设计约定, 二者共享同一 `n_articles` 分母口径。行宇宙同样是 full 留篇门控下的子集 (不独立扩大或缩小留篇集合)。`_ss_tone_sum` 与 `_full_tone_sum`、`_ctx_tone_sum` 三者各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 检验。由于同句窗口极窄, 该轨在样本量较小 (如本机 dev T=2 试跑) 时容易出现大量回退到全文口径的情形, 此为按设计的预期退化而非缺陷; 生产全量语料 (T=18) 上同句共现覆盖率预期显著提升。

`_ss` 的判据原语 (`extract_bank_fintech_cooccurrence`) 与 stage 13 硬过滤所用的邻近窗口判据 (`has_bank_fintech_cooccurrence_within_radius`) 是两套不同口径, 前者要求严格同句、后者允许 ±1 句半径, 二者刻意不互相复用, 使用者不应把 `_ss` 的窗口半径参数与 stage 13 `cooccurrence_filter.sentence_radius` 混为一谈 (两个不同 config 键)。相对 `_full`/`_ctx` 两轨, `_ss` 是三轨中构念最"苛刻"的一支: 只有当银行实体名与金科关键词在同一句 (或 ±1 句默认半径) 内共同出现时, 该句 (及标题) 才进入打分输入, 因此 `_ss_tone_sum` 更贴近"银行与金融科技被同时、直接提及时的语调", 而非该银行整体媒体形象的语调。这一窄口径的代价是对样本规模的敏感性更高, 在小样本或金科话题稀疏的银行-年度上, `_ss_tone_sum` 的方差和均值都更容易受个别报道或回退机制主导, 解读时应结合 `n_articles_llm_valid_ss` 与回退占比一并考察, 不宜孤立看待单一数值。

<!-- rendered-citations:begin -->
You, J.; Zhang, B.; Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Du, Z.; Huang, A. G.; Wermers, R.; Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R.; Jennings, J.; Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M.; Brooke, J.; Tofiloski, M.; Voll, K.; Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Tetlock, Paul C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
