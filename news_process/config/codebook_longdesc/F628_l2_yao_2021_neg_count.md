---
family_id: F628
columns:
- yao_2021_neg_count_ctx
- yao_2021_neg_count_full
- yao_2021_neg_count_ss
unit: 篇数/计数 (count, 银行-年内负面判定文章数)
formula: 'yao_2021_neg_count{track} = Σ_{i∈bank-year} 1{yao_2021_score{track}_i < 0}; 逐篇二值负面判定门槛来自 Gentzkow, Kelly & Taddy (2019, JEL) D2 单词典法, 与词典法 tone 均值 (yao_2021_tone{track}) 共享同一逐篇 score 但改用符号计数而非取均值'
producer: pipeline\panel\runner.py (_is_{d}_negative{track} 逐篇符号判定); pipeline\panel\encode.py (DICT_NAMES 循环聚合 sum); pipeline\sentiment\tone_words.py (yao_2021_score{track} 逐篇词典打分上游)
upstream: [yao_2021_score_full, yao_2021_score_ctx, yao_2021_score_ss]
citations:
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
  vol: ''
  issue: ''
  pages_or_artno: '3446388'
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application
  venue: Expert Systems with Applications
  vol: '264'
  issue: ''
  pages_or_artno: '125739'
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: 'Negation scope detection in sentiment analysis: Decision support for news-driven trading'
  venue: Decision Support Systems
  vol: '88'
  issue: ''
  pages_or_artno: 67-75
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: 'Chinese annual report readability: Measurement and test'
  venue: China Journal of Accounting Studies
  vol: '7'
  issue: '3'
  pages_or_artno: 407-437
- doi: "10.1016/j.jaccpubpol.2024.107181"
  type: "journal"
  authors: "Cheng, C. A., Jiang, L., & Song, W.-L."
  year: 2024
  title: "Media coverage and debt financing choice"
  venue: "Journal of Accounting and Public Policy"
  vol: "44"
  pages_or_artno: "107181"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
- doi: "10.1111/acfi.13353"
  type: "journal"
  authors: "Kanagaretnam, K., Li, W., Shi, G., & Zhou, Z."
  year: 2025
  title: "Ambiguity of tone in annual reports and bank risk taking"
  venue: "Accounting & Finance"
  vol: "65"
  issue: "1"
  pages_or_artno: "935-970"
new_dois: []
---

## CORE

【构念与来源】
本家族 3 列 (`yao_2021_neg_count_full`/`_ctx`/`_ss`) 度量的是"某银行在某年度被认定为负面语调的报道篇数", 属于 Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 归纳的文本情感测度谱系中最朴素的一支——将词典打分连续量二值化后取计数, 而非取均值 (后者即同家族姊妹列 `yao_2021_tone{track}`)。上游情感打分词典为 Yao 等 (2021) 面向中文金融文本构建的情感词典 (`yao_2021`, 六部中文词典之一, 与 `jiang_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran` 并列, 详见 `config/tone_dicts.json::SSOT`), 该词典延续 Loughran & McDonald (2011, *Journal of Finance*) 开创的、面向特定领域(而非通用汉语)词汇表构建情感字典的方法论传统, 并针对中文金融新闻语境做了本地化扩充与校准。词典法逐篇打分产出连续变量 `yao_2021_score{track}` (正负号与幅度均携带信息), 本家族在其基础上做符号截断: 打分 < 0 记为 1 ("负面文章"), 否则记为 0, 再按银行-年分组求和, 得到该银行-年内负面文章的绝对篇数。三个后缀 `_full`/`_ctx`/`_ss` 对应本项目的三轨文本口径 (详见【方法学与计算】), 是同一构念在三种不同文本窗口上的并排复算, 三者互为稳健性、不分主次, 严禁在同一过度识别 (over-identified) 的 Hansen J 检验中混用。

本家族属于"计数"而非"比率"或"均值"测度, 与同家族体系内 `yao_2021_tone{track}` (词典法语调均值, 连续量, 范围通常在 [-1, 1] 附近)、`yao_2021_neg_frac{track}` 一类的比率型指标 (若存在) 有本质区别: 计数型指标随银行-年内文章总数 (`n_articles{track}`) 机械增长, 不做样本量归一, 因而在跨银行、跨年横截面比较时天然带有"曝光量效应"——报道量越大的银行, 计数型指标的绝对水平也倾向越高, 即便负面报道占比 (即语调) 并未更差。这一点在使用本家族列作解释变量或结果变量时须在回归设定中显式控制 `n_articles{track}` 或改用比率型/均值型姊妹列, 否则计数效应与语调效应会相互混淆, 削弱识别力。

【方法学与计算】
计算链条分三步, 分别落在三个不同的 producer 模块中:
第一步 (`pipeline/sentiment/tone_words.py`, stage 22 词典法情感打分): 对每篇文章的三轨文本 (`content_full`/`content_ctx`/`content_ss`, 由 stage 14 `ctx_materializer` 预先物化) 分别用 `yao_2021` 词典做逐词匹配打分, 打分规则遵循本项目统一的词典法框架——命中正面词/负面词计数、否定规则翻转极性、程度副词加权、转折规则调整, 产出逐篇连续打分 `yao_2021_score{track}`。
第二步 (`pipeline/panel/runner.py`, 文章级→面板级中间层): 对逐篇连续打分做符号二值化, `_is_yao_2021_negative{track} = 1{yao_2021_score{track} < 0}`, 这是一个 0/1 中间掩码列 (整数, 非 nullable), 命名前缀 `_is_` 表示其为面板导出前的临时工作列, 不落盘到文章级 parquet, 仅供聚合环节消费。该二值化判据方法学上呼应 Garcia (2013, *Journal of Finance*) 对新闻情感符号化处理的实践先例。
第三步 (`pipeline/panel/encode.py`, 面板聚合): 沿 `DICT_NAMES` (六部词典的 SSOT 列表) 循环, 对每部词典 `d` 执行 `agg[f'{d}_neg_count{track}'] = (f'_is_{d}_negative{track}', 'sum')`, 即按 (银行, 年) 分组对该二值掩码求和, 得到本家族三列。由于 `_is_yao_2021_negative{track}` 只在 `yao_2021_score{track}` 非缺失时才有确定取值, 若某银行-年内全部文章该词典打分均缺失 (理论上极罕见, 词典法不依赖 LLM API 因而通常不缺失), 该银行-年格点的 `sum` 会退化为 0 而非 NaN——这与 LLM 法/BERT 法计数列 (依赖模型可用性, 缺失会传导为 NaN) 的缺失语义不同, 使用时须注意区分"真实零篇负面"与"数据缺失"。

三轨文本口径 (镜像项目铁律, CLAUDE.md「当前状态铁律」): `_full` = 标题+正文全文; `_ctx` = 标题+目标银行实体窗口 (窗口大小见 `config/filtering.yaml::context_window`); `_ss` = 标题+银行∧金科科技词同句 (或 ±N 句窗) 共现片段, 无同句共现命中时回退为全文 (`ss_is_fallback=True`, 与 `_ctx` 的回退语义镜像一致, 共享 `n_articles` 分母)。三轨在 stage 14 `ctx_materializer` 统一物化, stage 21/22/23/24 情感测度 (含本家族所属的 stage 22 词典法) 均无条件对三轝并行打分。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 检验设定。留篇门控口径 (2026-06-29 起) 为 full-only: 某篇报道是否计入"银行-金科相关报道"样本, 仅由 `llm_verified_full` 决定, `_ctx`/`_ss` 轨的行宇宙是 full 轨留篇集合的子集, 在此子集上分轨独立复算, 而非各轨自行决定留篇边界。

【文献定位】
本家族测度"负面报道计数"这一构念的经济学动机, 直接呼应 Piotroski, Wong & Zhang (2015, *Journal of Accounting Research*, 53(2), 405-459) 关于中国上市公司存在压制负面信息的政治激励这一发现——该文揭示了负面信息在中国制度语境下具有区别于西方样本的传播摩擦与披露激励, 说明在中国银行-金科新闻语境中, 单独刻画"负面报道篇数"(而非仅看语调均值) 具有独立的经济学信息含量: 负面报道计数偏低既可能反映真实经营稳健, 也可能反映信息压制/媒体选择性报道, 二者的区分需要结合计数与均值/占比型姊妹指标联合解读。词典本身的构建方法论参照两支中文金融情感词典文献: 一是 Bian, Jia, Li & Yan (2021, SSRN Working Paper No. 3446388) 面向中文会计与金融文本分析构建的情感词典, 与本家族所属 `yao_2021` 词典同属六部中文词典稳健性梯子中的姊妹词典; 二是 Ma, Zhang & Zhang (2025, *Expert Systems with Applications*, 264, 125739) 面向中国境内投资者构建的细粒度中文情感词典 (CN-FSD), 二者共同印证了"面向中文金融文本定制情感词表, 而非直接套用英文或通用汉语词典"这一方法论路径在近年文献中持续得到验证与迭代。逐篇打分二值化 (score<0 → 负面标记) 所隐含的否定规则处理, 方法学上呼应 Pröllochs, Feuerriegel & Neumann (2016, *Decision Support Systems*, 88, 67-75) 对新闻情感分析中否定辖域检测 (negation scope detection) 的系统性论证——该文指出否定词的辖域判定误差会直接扭曲逐篇情感符号判定的准确性, 这正是本项目词典法打分内置否定翻转规则、并将 `yao_2021_score{track}` 而非裸词频计数作为二值化输入的方法学依据。中文文本量化分析在会计与金融研究中的更广泛应用参照 Xu, Yao & Chen (2019, *China Journal of Accounting Studies*, 7(3), 407-437) 对中文年报可读性的测量与检验, 与本家族同属"中文金融文本挖掘用于治理/披露研究"的方法论谱系。 在测度形态与应用场域两侧, 近期文献亦为本家族「逐篇极性判定后按主体-年求和」这一构造提供了同域参照。Cheng、Jiang 与 Song (2024) 把美国上市公司 2001–2014 年的新闻按公司-年归集为报道量与新闻情感, 作为解释变量进入债务融资方式选择回归, 发现负面盈余新闻显著降低银行贷款与公募债概率、提高私募债概率, 是「文章级极性判定 → 按主体-年对极性指示求和」这一聚合范式的前沿实证用例, 亦印证负面报道计数本身携带独立于语调均值的信息含量; 惟原文极性来自专有事件情感分析服务, 既非公开情感词典亦非人工编码, 故此处只锚定其聚合形态而不锚定极性来源, 且原文主体为美国上市公司而非中国商业银行, 亦无本项目的三轨文本与六词典并排设计。Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 表明把新闻情感按银行主体归集并进入银行层面实证, 是当前金融稳定领域被接受的做法, 为本家族以银行-年为聚合单元提供场域层面的支撑; 但原文为美国银行监管语境且以监管评级/监管行动为被解释变量, 其情感测度的构造细节与本项目逐篇词典打分后按符号截断计数的口径不同, 亦不涉及三轨文本。Kanagaretnam、Li、Shi 与 Zhou (2025) 以银行年报文本的语调模糊度进入银行风险承担面板回归, 提供了「银行文本的词表型语调测度可作为银行层面实证解释变量」这一效度证据; 仅此为限 —— 原文的具体构造是残差化的模糊度指标, 未见极性比率式口径, 更未按极性符号对多篇文本计数 (年报每银行-年仅一份文档, 与本家族逐篇判定后再求和的分母结构根本不同), 且原文为英文词表体系, 无中文分词与否定翻转/程度副词/转折三规则层。
## VAR: yao_2021_neg_count_ctx

【变体差分】
本列是家族在实体窗轨 (`_ctx`) 上的负面文章计数。扫描文本为 stage 14 物化的 `content_ctx`——标题 + 目标银行实体出现位置周边的窗口文本片段, 而非全文, 因而文本长度通常显著短于 `_full` 轨, 逐篇命中的情感词数量随之减少, 词典打分 `yao_2021_score_ctx` 的方差与均值水平都可能与全文轨系统性不同 (窗口更聚焦于银行相关表述, 可能过滤掉与银行无关的正负面陈述, 使打分更贴近"银行本体语调"而非"全文语调")。`_ctx` 轨的行宇宙 (即参与计数的文章集合) 遵循 full-only 留篇门控: 只有 `llm_verified_full == True` 的文章才进入该银行-年的分母/分子统计, `_ctx` 轨本身不独立判定留篇资格。若某篇文章不存在目标银行实体窗口 (理论上应罕见, 因该文章已通过银行实体识别阶段), 上游 `ctx_materializer` 的回退语义会将 `content_ctx` 退化为全文, 并标记 `ctx_is_fallback=True`；本列作为下游聚合不区分是否 fallback, 与 `n_articles_ctx` 共享同一分母口径。本列与家族 canonical (`_full`) 轨互为稳健性并排, 不构成对 `_full` 轨结果的替代或修正, 不应在同一过度识别设定中同时作为工具或内生解释变量混用。在实际使用中, `_ctx` 轨的价值在于剥离"报道全文中与目标银行无关段落"对情感打分的稀释或污染——例如一篇报道整体基调正面, 但涉及目标银行的具体段落语气负面(或反之), `_full` 轨打分会被无关段落的语调拉平, 而 `_ctx` 轨聚焦于实体窗口, 更贴近"该银行本身在报道中被如何评价"这一构念。但窗口截断也带来局部化代价: 若目标银行实体窗口恰好落在陈述性、无情感色彩的语句附近 (如仅提及银行名称作背景信息), `_ctx` 轨的逐篇打分噪声会相应升高, 计数列的银行-年格点方差可能因此比 `_full` 轨更大, 在小样本 (低 `n_articles_ctx`) 银行-年格点上尤需谨慎解读。



## VAR: yao_2021_neg_count_full

【变体差分】
本列是家族的全文轨 (`_full`), 是三轨中口径最宽的一支, 扫描文本为 stage 14 物化的 `content_full` (标题 + 完整正文), 也是本项目多数下游 paper 模块 (P1 `bank_fintech_tone` 等) 选定的主口径 (canonical treatment 轨, 2026-06-29 全量切换 full-only 门控后确立)。留篇判定 (`llm_verified_full`) 直接锚定在本轨——某篇报道是否被计入"银行-金科相关报道"样本, 唯一由全文轨的 LLM 验证结果决定, `_ctx`/`_ss` 两轨的行宇宙是本轨留篇集合的子集。由于扫描文本涵盖全文, 本列在三轨中通常具有最大的逐篇情感词命中概率, 计数绝对水平在三轨中也倾向最高 (但这并不意味着本轨"更准确", 三轨是互补的稳健性设计而非主次关系)。使用本列时应注意其构念含义: 全文可能包含与目标银行无关的段落 (例如同一篇报道兼谈多家银行、宏观政策、行业整体动态), 因此逐篇打分是对"整篇报道语调"而非"银行专属语调"的度量, 与 `_ctx`/`_ss` 两轨"聚焦银行相关文本片段"的构念定位形成互补而非替代关系。作为 P1 (`bank_fintech_tone`) 等下游 paper 模块的 canonical treatment 轨来源之一, 本列在与 `yao_2021_tone_full` (均值型姊妹列) 联合使用时, 应始终以 `n_articles_full` 做归一化基准, 避免计数绝对水平的曝光量效应被误读为语调本身的变化。



## VAR: yao_2021_neg_count_ss

【变体差分】
本列是家族在同句轨 (`_ss`) 上的负面文章计数。扫描文本为 stage 14 物化的 `content_ss`——标题 + 目标银行与金科科技词汇同句共现 (或按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的 ±N 句窗口, 默认半径为 1) 的片段, 是三轨中文本窗口最窄、语义最聚焦于"银行-金科关联陈述"的一支。`_ss` 轨的回退语义镜像 `_ctx` 轨: 若某篇文章内不存在银行∧金科词的同句 (或窗口内) 共现, `content_ss` 回退为全文 body, 并标记 `ss_is_fallback=True`, 与 `n_articles` 共享同一分母口径, 而非静默丢弃该文章或产出缺失值; 若上游 `FINTECH_AC` (金科词自动机) 为 None (极端配置缺失场景), 则 `*_is_fallback` 全部退化为 True, 整个 `_ss` 轨优雅降级为等价于全文轨的宽口径。需要注意的是, `_ss` 轨"同句共现"判据 (用于决定文本窗口内容) 与 stage 13 `cooccurrence_filter` 硬过滤所用的"±1 句窗口"判据 (`config/filtering.yaml::cooccurrence_filter.sentence_radius`, 用于决定文章是否进入样本) 是两个不同配置键、不同代码路径, 前者用 `entity_context.py` 中与 `_ctx` 判据不同的严格同句原语实现, 二者刻意不复用, 不可混淆。本列在三轨中样本更聚焦但对个别词的敏感度更高 (窗口越窄, 单个负面词命中对逐篇打分符号的影响越大), 作为稳健性并排轨解读时应留意这一噪声特性。

<!-- rendered-citations:begin -->
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
Xu, W., Yao, Z., & Chen, D. (2019). Chinese annual report readability: Measurement and test. China Journal of Accounting Studies, 7(3), 407-437. https://doi.org/10.1080/21697213.2019.1701259
Cheng, C. A., Jiang, L., & Song, W.-L. (2024). Media coverage and debt financing choice. Journal of Accounting and Public Policy, 44, 107181. https://doi.org/10.1016/j.jaccpubpol.2024.107181
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision?. Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
Kanagaretnam, K., Li, W., Shi, G., & Zhou, Z. (2025). Ambiguity of tone in annual reports and bank risk taking. Accounting & Finance, 65(1), 935-970. https://doi.org/10.1111/acfi.13353
<!-- rendered-citations:end -->
