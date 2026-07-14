---
family_id: F639
columns:
- you_2018_cater_ctx
- you_2018_cater_full
- you_2018_cater_ss
unit: 无量纲差值 (词典净语调 − LLM 三家投票净语调, 区间约 [-2, 2], 由两个各自归一到约 [-1, 1] 的净语调指数相减得到)
formula: 'you_2018_cater{trk} = you_2018_tone{trk} - llm_vote_tone{trk}; 前者 = you_2018 词典 (positive 1,425 词 / negative 1,583 词) 经 tone_words.py 语言学规则增强(否定翻转/程度副词/转折连词)逐篇计数后归一得到的净语调, 后者 = gpt54nano/gemini31/deepseekv4 三家 LLM 多数投票语调; 两者在 pipeline/panel/runner.py 步骤 8d "Algorithmic Catering" 中相减, 正值表示词典打分比 LLM 深层模型判断更正面(潜在算法迎合), trk ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\runner.py (步骤 8d, 消费 you_2018_tone{trk} 与 llm_vote_tone{trk} 两个已聚合面板列做差) ; pipeline\sentiment\tone_words.py (上游, 产出 you_2018_tone{trk} 的词典计数) ; pipeline\panel\export.py (仅贡献 .dta 变量标签渲染, 不参与数值计算)
upstream: []
citations:
- doi: "10.1093/rfs/hhad021"
  type: journal
  authors: "Cao, S., Jiang, W., Yang, B., & Zhang, A. L."
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: "The Review of Financial Studies"
  vol: "36"
  issue: "9"
  pages_or_artno: "3603-3642"
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who captures the power of the pen?"
  venue: "The Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1111/ecin.13264"
  type: journal
  authors: "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E."
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: "Economic Inquiry"
  vol: "63"
  issue: "1"
  pages_or_artno: "125-143"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514-5532"
new_dois: []
---

## CORE

【构念与来源】
you_2018_cater 家族衡量的不是 you_2018 词典本身的净语调水位, 而是"词典打分与深层模型(LLM)打分之间的分歧程度", 即算法迎合度(algorithmic catering)。家族内三列(_full/_ctx/_ss)是同一构念在三条文本窗口上的并排实现。命名沿用 pipeline/panel/runner.py 步骤 8d 的历史变量族命名 `{dict}_cater{track}`, `{dict}` 取 config/tone_dicts.json 登记的 6 部词典之一(本家族取 you_2018), 但列名中的 "cater" 二字对应的是 Cao, Jiang, Yang & Zhang (2023, RFS)「How to talk when a machine is listening」提出的算法迎合(algorithmic catering)概念——该文发现随着自动化文本分析(算法/AI)被投资者与监管者用于审查企业信息披露, 部分披露主体会针对性调整措辞, 使得基于简单规则(如词典)的语调打分呈现出比深层语义模型更正面的系统性偏离, 这种偏离本身携带"是否在迎合浅层算法审查"的信息, 而不只是噪声。you_2018_cater{trk} 把这一诊断测度下沉到本项目的银行-金科新闻文本层面: 以 you_2018 词典的逐篇净语调(you_2018_tone{trk})为词典侧输入, 以三家 LLM(gpt54nano/gemini31/deepseekv4)多数投票得到的 llm_vote_tone{trk} 为深层模型侧输入, 两者相减。正值意味着 you_2018 词典判断该篇报道比 LLM 深层理解更正面, 可能反映报道措辞在词面层刻意堆砌正面词汇但深层语义未必同样正面(潜在迎合浅层词频审查); 负值则相反, 词典判断更负面而 LLM 判断更中性或正面, 可能反映词典误伤(如反讽、专业术语误判)或深层模型捕捉到了词面之外的正面语境。you_2018 词典本身(positive 1,425 词/negative 1,583 词)只是这个"分歧测度"公式左手边的一个输入选择, 词典的出处论文 You, Zhang & Zhang (2018, RFS)「Who captures the power of the pen?」解释的是词典本身刻画的媒体用词倾向构念(供 you_2018_tone{trk} 等纯词典打分列消费), 与本家族 "_cater_" 后缀所代表的"词典-LLM 分歧"这一二阶测度是两个不同层次的构念, 不能混同。
【方法学与计算】
计算发生在 pipeline/panel/runner.py 步骤 8d "Algorithmic Catering — 全展开", 该步骤在 bank-year 面板已聚合出各词典净语调列 `{d}_tone{track}`(d 遍历 DICT_NAMES, 含 you_2018)与三家 LLM 投票语调列 `llm_vote_tone{track}` 之后, 逐轨做减法: `panel[f'{d}_cater{track}'] = panel[d_col] - panel[lc]`, 其中 `d_col = f'{d}_tone{track}'`, `lc = f'llm_vote_tone{track}'`。you_2018_tone{trk} 自身的计算链条在更上游: pipeline/sentiment/tone_words.py(阶段 22)对 config/tone_dicts.json 中的 you_2018 词典逐篇计数, positive/negative 两极性集合存在 5 个跨类重叠词, 按项目 2026-06-24 决策以 (+1, −1) 对称计入两侧(不做单侧武断判负), 原始计数之上叠加否定翻转/程度副词/转折连词三条语言学规则增强, 归一为 (pos_count−neg_count)/(pos_count+neg_count) 得到 you_2018_tone{trk}; 分母为 0 的文章输出缺失, 不做人为填零。llm_vote_tone{trk} 则来自 stage 21 三家 LLM(gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash)对同一文本轨的独立打分后取多数投票共识, 门控遵循 full-only 铁律(2026-06-29 起): 一篇报道是否计入"银行×金科"文章总体, 只看 llm_verified_full; ctx/ss 两轨在此基础上是以 full 留篇集为行宇宙的条件测度(conditional-on-full)。you_2018_cater{trk} 是两个已经在面板层聚合完毕的净语调列之间的逐格相减, 本身不再回到文章级重新计数, 因此该列的数值缺失模式继承自 you_2018_tone{trk} 与 llm_vote_tone{trk} 两者任一缺失即缺失。pipeline/panel/export.py 在此过程中不参与任何数值计算, 只在渲染 .dta 时为 `{d}_cater{track}` 列生成形如 "Catering: {d}-LLM ({t})" 的变量标签文本, 属纯标签映射而非产出逻辑。三轨口径与本项目其余测度一致: full=标题+全文正文, ctx=标题+目标银行实体窗口, ss=标题+银行∧金科词同句±N 句半径窗口(默认 N=1), 三条文本在 stage 14 统一物化, 三轨各自独立走 8d 减法, 互不借用彼此中间结果, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified 的 Hansen J 检验。
【文献定位】
本家族真实的构念权威文献是 Cao, Jiang, Yang & Zhang (2023, RFS)提出的算法迎合(algorithmic catering)框架, 该文是本文本测度设计中"词典 vs 深层模型分歧"这一整条 8d 变量族(含综合词典 vs 综合 LLM 的 algo_cater、综合词典 vs 综合 BERT 的 algo_cater_b、以及本家族这种单词典 vs 综合 LLM 的 `{d}_cater`)的唯一直接出处, 8d 代码块的注释直接标注该文 DOI 与页码。Huang, Wang & Yang (2023, Contemporary Accounting Research)提出的 FinBERT 是同一段代码里"深层模型"一侧的另一个代表性实现(BERT 系), 与本家族并行的 `you_2018_cater_b{trk}` 变体(词典 vs 综合 BERT, 未在本家族收录但共享同一分歧测度设计思路)直接对应该文方法。You, Zhang & Zhang (2018, RFS)「Who captures the power of the pen?」仍然是必要引用, 但其角色被重新定位为"词典侧输入 you_2018_tone{trk} 的出处"而非"本家族核心构念的出处"——该文解释的是媒体用词的正负倾向如何反映信息生产链条中的立场分歧, 本家族借用其词典作为算法迎合测度公式里的一个输入项, 而不是直接复刻其构念。方法学脉络上, 本家族仍与 Du et al.(2022, Review of Finance)的中文词典构建路径同源(词典法本身的构建逻辑一致), 也仍适用 Barbaglia et al.(2025, Economic Inquiry)对词典法情感分析优劣势的系统论述——可解释、可审计、计算成本低, 但对语境/反讽/领域外用词不敏感, 这恰恰是"词典分数为何可能系统性偏离深层模型分数"的方法学解释。Frankel, Jennings & Lee (2022, Management Science)"机器学习 vs 词典法互为稳健性"的先例进一步支撑本家族"不把词典-LLM 分歧简单等同于测量误差, 而是把分歧本身当作携带信息的诊断量"这一处理思路。
【与相邻测度的构念区分】
you_2018_cater{trk} 与本项目其余"词典法净语调"列(you_2018_tone{trk}/jiang_2021_tone{trk}/yao_2021_tone{trk}/bian_2021_tone{trk}/du_2022_tone{trk} 等)是两个不同层级的测度: 后者是一阶的"词典打分本身", 前者是二阶的"词典打分减去 LLM 打分的差值", 二者数值范围与解读方式均不同(一阶量刻画"这篇报道措辞褒贬", 二阶量刻画"词典判断与深层模型判断分歧多大")。you_2018_cater{trk} 与同一 8d 步骤产出的相邻变量族(`algo_cater{trk}`=综合词典 vs 综合 LLM、`algo_cater_b{trk}`=综合词典 vs 综合 BERT、`{d}_cater_b{trk}`=单词典 vs 综合 BERT、`cater_{llm}{trk}`/`cater_{b}{trk}`=综合词典 vs 单个深层模型)同属"迎合度诊断"这一大类下的不同并排切片(词典粒度 × 深层模型粒度的组合), 彼此互为稳健性、不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J。you_2018_cater{trk} 与 LLM 三家投票语调 llm_vote_tone{trk}、BERT 三模型语调也不是同一构念下的方法学并排轨(那是一阶净语调层面的词典/LLM/BERT 三方法并排), 而是把 LLM 一侧直接作为分歧计算的减数使用, 不应把 you_2018_cater{trk} 误当作"又一个语调测度"塞进同一识别方程与 you_2018_tone{trk}、llm_vote_tone{trk} 三者同时作自变量, 那样会人为制造共线性(cater 本身就是另两者的线性组合)。

## VAR: you_2018_cater_ctx

【变体差分】
本列取 you_2018_tone_ctx 与 llm_vote_tone_ctx 相减, 是 you_2018_cater 家族三轨中的"实体窗口轨"。content_ctx 在 stage 14 物化阶段以目标银行实体在正文中的出现位置为锚点截取周围窗口文本, 减数与被减数(词典侧、LLM 侧)均在同一 ctx 窗口内独立计算, 不存在词典侧用 ctx 而 LLM 侧用 full 之类的跨轨错配。若某篇文章未能定位到有效实体窗口, content_ctx 退化为 fallback 语义, 由上游 ctx_is_fallback 指示列记录, you_2018_cater_ctx 此时的分歧值反映的是 fallback 文本上词典与 LLM 的分歧, 不单独在本列内标注。ctx 轨与 full/ss 轨互为稳健性并排, 不以相关系数高低判定谁"更对"三者应分别进入下游回归做稳健性对照, 不共享同一识别方程。留篇门控仍以 full 轨 llm_verified_full 为准, ctx 轨样本是该留篇集的条件子集。测度含义上, ctx 轨试图回答"记者在直接谈论这家银行的段落里, 词典判断与 LLM 判断的分歧有多大", 当一篇报道同时涉及多家银行或穿插大段无关行业背景时, full 轨的分歧值可能被无关段落的词面堆砌或深层语义污染, ctx 轨通过锚定实体窗口收窄这一噪声来源。需要披露的局限是: ctx 窗口宽度是固定配置参数而非逐篇自适应, 窗口过窄可能截断跨句否定/转折结构, 使词典侧 tone_words.py 语言学规则增强在窗口边界失效, 从而放大词典侧与 LLM 侧本就存在的分歧, 这一放大效应不应被误读为"迎合行为更强", 而应结合 ctx_is_fallback 发生率与窗口内词数分布一并解读。

## VAR: you_2018_cater_full

【变体差分】
本列取 you_2018_tone_full 与 llm_vote_tone_full 相减, 是三轨中窗口最宽的一支, 也是留篇门控直接锚定的轨道: 2026-06-29 起生效的 full-only 铁律规定, 一篇报道是否被判定为有效的银行×金科报道只看 llm_verified_full, ctx/ss 两轨样本行宇宙均是以本轨留篇结果为准的条件子集。you_2018_cater_full 的减数(you_2018_tone_full)与被减数(llm_vote_tone_full)均取标题+全文正文(prepend_title 拼接)为输入, 词典侧与 LLM 侧在同一份最宽文本上分别独立打分再相减, fallback 发生率最低(接近全文本身即天然覆盖目标实体与金科词的共现语境)。full 轨不因门控地位而在系数解释上天然优先于 ctx/ss, 三者应作为并列稳健性证据共同报告。full 轨下词典侧的三条语言学规则(否定翻转/程度副词/转折连词)有最充分上下文可供匹配, 跨句结构不会像 ctx/ss 那样因窗口截断失效, 这是词典侧打分在 full 轨相对更稳定的优势; 但相应代价是报道中与目标银行无关的段落(行业综述、监管背景、其他银行对比)同样计入词典侧与 LLM 侧两端的打分, 篇幅长、话题分散的文章会让分歧值同时受两端噪声牵动, 方向不确定, 这正是设置 ctx/ss 两条并排稳健性轨的动机。全文轨的算法迎合诊断意义最贴近 Cao et al.(2023)原始框架关注的"整篇披露文本层面"的迎合行为, 因为该文关注的正是企业/媒体在整篇文本层面对自动化审查的策略性调整, 而非局限于对单一实体的逐句评价。

## VAR: you_2018_cater_ss

【变体差分】
本列取 you_2018_tone_ss 与 llm_vote_tone_ss 相减, 是三轨中语境收窄程度最高的一支: content_ss 只在目标银行实体与金科关键词同时出现(或彼此相邻 N 句以内, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)的局部语境上取值, 词典侧与 LLM 侧均在该同句窗口内独立打分后相减。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句(或窗口内)共现, content_ss 退化为全文 body, 对应 ss_is_fallback=True, 且该回退与 ctx 轨共享同一个 n_articles 分母, 不因回退发生而单独降低样本量; 若上游 FINTECH_AC 语料库为空(None), 所有文章 *_is_fallback 一并置为 True, 属优雅降级而非报错。ss 轨与 full/ctx 两轨互为稳健性并排, 三者禁止混入同一 over-identified Hansen J; 留篇门控仍完全由 full 轨 llm_verified_full 决定, ss 轨样本是该留篇集的条件子集。三轨之中, ss 轨对"银行×金科"这一研究构念的语境锚定最严格, 目的是尽可能排除"文章提到银行、又在别处提到金科, 但二者并无实质关联"这类假阳性共现对词典侧与 LLM 侧两端打分的共同污染, 从而使二者的分歧更纯粹地反映"迎合"而非"话题漂移"造成的噪声。代价是样本可用文本量最小、对词典侧命中词数的稀疏性最敏感——当同句窗口内命中词数很少时, you_2018_tone_ss 的归一化分母也小, 单个词的极性误判会被放大, 进而放大 you_2018_cater_ss 的分歧值, 这一放大效应是解读该列系数时应额外披露的已知局限, 需结合 fallback 发生率与命中词数分布一并说明。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
</content>
