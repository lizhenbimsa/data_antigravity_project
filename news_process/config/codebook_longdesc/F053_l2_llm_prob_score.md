---
family_id: F053
columns:
- avg_llm_prob_score_ctx
- avg_llm_prob_score_full
- avg_llm_prob_score_ss
- avg_llm_prob_score_std_ctx
- avg_llm_prob_score_std_full
- avg_llm_prob_score_std_ss
- llm_prob_score_app_ctx
- llm_prob_score_app_full
- llm_prob_score_app_lc_ctx
- llm_prob_score_app_ls_ss
- llm_prob_score_app_ss
- llm_prob_score_sub_ctx
- llm_prob_score_sub_full
- llm_prob_score_sub_sc_ctx
- llm_prob_score_sub_ss
- llm_prob_score_sub_ss_ss
- llm_prob_score_symb_ctx
- llm_prob_score_symb_full
- llm_prob_score_symb_sc_ctx
- llm_prob_score_symb_ss
- llm_prob_score_symb_ss_ss
- llm_prob_score_tech_ctx
- llm_prob_score_tech_full
- llm_prob_score_tech_lc_ctx
- llm_prob_score_tech_ls_ss
- llm_prob_score_tech_ss
unit: 无量纲连续情感分 (逐篇 ∈ [-1, +1]; 银行-年聚合与其同尺度, std 变体为其组内离散度)
formula: "compute_prob_score(label, c): 中性→0; 正面→(3c-1)/2; 负面→(1-3c)/2 (P2 路径, c∈(0,1]); c=0/缺失→one-hot ±1/0 (P3); c∈NaN 或越界→NaN 拒绝 (P3_INV)。avg_llm_prob_score{track}=银行-年内逐篇 prob_score 均值; _std 变体=同组样本标准差; 子样本变体=在 {底层技术/应用场景/实质/象征} 分类子集上重算的同一均值"
producer: news_process/pipeline/sentiment/tone_llms.py::compute_prob_score ; news_process/pipeline/panel/encode.py
upstream:
- 15_fintech_intensity.parquet (content_full/content_ctx/content_ss + target_bank)
- 21_tone_llms.parquet (逐篇 llm_prob_score{track} 及创新维度分类标签)
citations:
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: FEDS Working Paper, Federal Reserve Board
  pages_or_artno: No. 2026-020
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
  pages_or_artno: 2412.07031
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
  pages_or_artno: 2502.18036
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: 105227
- doi: 10.18653/v1/2024.findings-emnlp.432
  type: journal
  authors: Renze, M.
  year: 2024
  title: "The effect of sampling temperature on problem solving in large language models"
  venue: "Findings of the Association for Computational Linguistics: EMNLP 2024"
  pages_or_artno: 7346-7356
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.2139/ssrn.4412788
  type: wp
  authors: Lopez-Lira, A., & Tang, Y.
  year: 2023
  title: "Can ChatGPT forecast stock price movements? Return predictability and large language models"
  venue: SSRN Working Paper
  pages_or_artno: No. 4412788
- doi: 10.1016/j.mlwa.2023.100508
  type: journal
  authors: Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D.
  year: 2023
  title: "Transforming sentiment analysis in the financial domain with ChatGPT"
  venue: Machine Learning with Applications
  vol: 14
  pages_or_artno: 100508
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是大语言模型情感判定的概率映射连续分 (logit-to-score), 即把 stage 21 三家 LLM 对每篇银行-金科报道给出的三分类情感标签 (正面 / 中性 / 负面) 连同其自报置信度, 折算成一个落在负一到正一之间的连续得分。构念上它填补了离散标签与连续计量之间的裂缝: 单纯的多数投票标签只有三个取值, 丢失了同为正面报道之间强弱的差异, 而媒体语调对银行负债端与融资成本的作用本质上是连续的边际效应, 需要一个方向乘强度的度量。得分越接近正一表示模型越确信该篇为正面, 越接近负一表示越确信为负面, 零附近对应中性或模型自身高度不确定。数据来源是 stage 21 的逐篇输出 21_tone_llms.parquet, 其上游是 stage 15 的 fintech_intensity 输出以及 stage 13 物化的三轨文本 (全文 content_full / 实体窗 content_ctx / 银行与金科同句窗 content_ss)。逐篇分在 encode 与面板聚合阶段按银行-年取组内均值 (avg 前缀列) 与组内标准差 (std 后缀列), 形成进入面板的银行-年测度。

【方法学与计算】
核心函数 compute_prob_score 把标签与置信度 c 映射为得分: 在 c 落于零到一开区间的常规路径 (P2) 下, 主类概率取 c, 其余两类各取剩余概率均分 (一减 c) 除以二, 得分等于正面概率减负面概率, 因此中性恒为零, 正面得 (三 c 减一) 除以二, 负面得 (一减三 c) 除以二; 当 c 大于三分之一时得分与标签方向一致, 而口头化置信度在实践中通常远高于该阈值, 得分方向稳定 (确切经验分布随语料而定, 本家族不手填盘上统计, 由引擎注入的统计段刻画)。剩余概率均分服从最大熵原理: 在已知主类概率的约束下 Shannon 熵最大的唯一解即其余类均匀分布。置信度为零或缺失走 one-hot 路径 (P3) 产正一 / 零 / 负一; 置信度为 NaN 或越出零到一区间则显式拒绝 (P3_INV) 返回 NaN 并在聚合层按 isnan 剔除, 以避免 CPython 的 min 语义把 NaN 静默编码为满置信信号。须强调置信度是模型生成的口头化 (verbalized) 数值, 并非内部 softmax 概率, 只作分类确信度的序数代理: 已知 LLM 口头置信系统性过度自信, 但保序性基本成立, 故在排序层面可靠而不可直接解释为校准概率。三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 在温度零下确定性推理, prompt v8 字节级冻结, 结果落 _llm_cache.db 缓存以保证逐字节可复现。

【文献定位】
概率映射连续化情感的方法学承接 Ludwig, Mullainathan 与 Rambachan (2025) 关于把 LLM 输出纳入计量测量误差框架的讨论, 以及 Gilardi, Alizadeh 与 Kubli (2023) 证明 LLM 文本标注可媲美甚至超过众包标注的基准。金融文本层面, Lopez-Lira 与 Tang (2023)、Kirtac 与 Germano (2024)、Fatouros 等 (2023) 展示了 LLM 情感对收益的预测力, Lan 等 (2025) 则聚焦中文细粒度金融情感; de Kok (2025) 与 Hansen (2026) 分别就温度零 / prompt 冻结 / 缓存的可复现范式与无金标准时的标注验证给出方法学准绳, Renze (2024) 量化了采样温度对稳定性的影响, 印证本家族温度零的确定性选择。构念上, 连续语调延续 Tetlock (2007) 媒体情感传导的经典脉络; 而按创新维度切分的子样本变体 (底层技术 / 应用场景来自 Gomber 等 2018 的技术-应用两分, 实质 / 象征来自 Westphal 与 Zajac 1994、1998 的实质-象征二分) 使连续语调可在异质报道结构上分层核验。中文情感词典基线参照 Du 等 (2022)。铁律: 三轨 (full/ctx/ss) 与各子样本切分互为稳健性、不分主次, 各自 just-identified 并排进各自回归, 禁混进同一 over-identified Hansen J; 留篇门控为 full-only (2026-06-29), 即是否判为一篇银行-金科报道只看全文轨的 verified, ctx/ss 降为 conditional-on-full 的测度与稳健性轨, ss 无同句共现时优雅回退——content_ss 取全文 body (与 content_full 同源, 非取 ctx 的实体窗内容) 并标 fallback、共享 n_articles 分母; 此处所谓「镜像 ctx」仅指两轨共享『无命中即回退到全文』这一公理, 非指内容相等。

## VAR: avg_llm_prob_score_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上的银行-年组内均值。ctx 轨的取材范围是标题 prepend 后的实体上下文窗口 (银行实体附近 ±N 句), 相较全文轨过滤掉了与目标银行无关的段落, 因此在报道冗长、银行仅被顺带提及时能压制无关噪声。它与 full、ss 两轨的同名均值互为稳健性、不分主次, 三轨各自 just-identified 并排进各自回归, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 产出 (方向乘置信度, 常规路径下正面 (三 c 减一) 除以二、负面对称、中性零), 只是喂入的文本是 content_ctx 而非全文; 聚合分母是该银行-年内 ctx 轨有效投票的篇数, ctx 轨缺列或该篇无实体窗时按 conditional-on-full 口径处理而不借全文轨分母。因留篇门控为 full-only, 本列刻画的是在全文轨已判定保留的报道集合上, 改用实体窗取材重算的语调水平, 用以检验主结论是否被全文中银行无关内容的语调所污染。当窗内语调与全文轨系统性背离时, 该列提供测量稳健性的诊断信号。
在面板使用上, 本列多作为主语调变量 avg_llm_prob_score_full 的稳健性替代进入平行回归: 若实体窗轨与全文轨的系数同号同量级, 则说明语调效应不由全文中银行无关段落驱动, 识别更可信。聚合口径遵循 conditional-on-full, 即行集恒为全文轨留篇集的子集, 分母按该银行-年 ctx 轨有效投票篇数逐轨自算, 绝不借全文轨分母凑数, 以免夸大 ctx 轨的语调稳定性。相较词典法, 本列保留了模型置信度信息, 对语调强弱的刻画更细腻。


## VAR: avg_llm_prob_score_full

【变体差分】
本列是本家族的 canonical 聚合测度: 概率映射情感分在全文 (full) 轨上的银行-年组内均值。full 轨取材为标题 prepend 后的整篇正文, 是留篇门控 (full-only, 2026-06-29) 所依据的唯一轨道, 因此其行宇宙即面板的银行-年全集, 其余两轨均为其上的 conditional-on-full 子测度。逐篇分由 compute_prob_score 按方向乘置信度产出 (正面 (三 c 减一) 除以二、负面 (一减三 c) 除以二、中性恒零, NaN/越界置信度按 P3_INV 剔除), 银行-年内对全文轨有效投票篇数取算术均值即得本列。它是把三分类标签连续化后进入面板的主语调变量之一, 相较仅计正负比例的离散测度保留了置信强度信息, 对边际语调效应的识别更灵敏。与 ctx、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。作为家族基准, 其余带子样本或跨轨后缀的列都可视为在本列基础上叠加分类门控或换轨取材的派生, 差分语义均相对本列陈述。
在下游计量中, 本列是媒体语调传导链条 (语调影响银行负债端与融资成本) 的核心处理变量之一, 也是三轨稳健性比较的基准锚: ctx 与 ss 轨的同名均值均相对本列陈述其偏离。聚合口径下, 银行-年内全文轨每篇有效投票各计一次, NaN 与越界置信度已在逐篇层按 P3_INV 剔除, 故均值不受无效标注污染。与仅计正负比例或净语调的离散测度相比, 本列因内嵌 verbalized confidence 的序数强度信息, 在边际语调效应上更灵敏, 但也须注意置信度过度自信带来的水平偏移只影响截距而非排序。


## VAR: avg_llm_prob_score_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上的银行-年组内均值。ss 轨取材最窄: 只保留目标银行与金科词在同一句子 (±N 句同句窗) 共现的片段, 因此语调最贴近银行-金科关系本身, 排除了同篇中银行其它业务的语调干扰。逐篇分同样由 compute_prob_score 产出, 喂入文本为 content_ss; 关键回退语义是当某篇无银行与金科同句共现时, content_ss 回退取全文 body (与 content_full 同源, 而非取 ctx 的实体窗内容) 并标记 fallback, 分母共享 n_articles 口径; 所谓「镜像 ctx」只指两轨同享『无命中即回退全文』这一回退公理, 不代表内容与 ctx 相等。该列与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因留篇门控为 full-only, 本列度量的是在全文轨已保留的报道集合上, 用最严格同句取材重算的语调, 是三轨中信噪比取向最极端的一端: 当同句语调与全文轨一致时增强主结论可信度, 背离时提示报道语调更多由银行非金科语境驱动。dev T=2 上 ss 轨可能出现零方差退化属预期, 生产 T=19 恢复正常。
在面板使用上, 本列是三轨中信噪比取向最激进的稳健性轨: 它剔除银行其它业务语境, 只留银行-金科同句语调, 因此当它与全文轨系数背离时, 强烈提示总语调更多由银行非金科报道驱动, 是识别银行-金科关系净语调效应的关键旁证。聚合口径为 conditional-on-full, 分母取该银行-年 ss 轨有效篇数, fallback 篇按共享 n_articles 口径纳入, 不单边孤立。因取材最窄, 本列在稀薄语料下方差不稳, 使用时宜配合有效篇数阈值过滤。


## VAR: avg_llm_prob_score_std_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上的银行-年组内标准差, 而非均值。它刻画的是同一银行同一年内, 各篇报道 ctx 轨语调的离散程度: 标准差越大说明该行该年媒体语调越分裂 (有强正也有强负), 越小说明语调越一致。构念上这是语调的二阶矩, 与均值 (一阶矩) 正交, 可作为测量误差 / 信噪比的代理——组内分散度高时该轨情感测度的信噪比更低, 对下游衰减偏误有诊断意义。计算上先由 compute_prob_score 得逐篇 ctx 轨分, 再在银行-年组内取样本标准差 (仅对有效投票篇数, NaN 已剔除)。它与 full、ss 轨的同名标准差互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。相较均值列, 本列不进入语调水平的主回归, 而多用于异质性与稳健性: 例如把它作为交互项检验语调分歧是否放大或削弱语调水平对银行融资成本的作用。ctx 轨取材去除银行无关段落后, 其分散度通常低于全文轨。
在计量应用上, 本列常作为语调不确定性 / 分歧度的调节变量进入交互项, 检验语调分散是否放大或削弱 ctx 轨语调水平对银行融资成本的边际作用; 它也可作测量误差代理, 提示该银行-年 ctx 轨情感信号的信噪比。聚合口径为 conditional-on-full 且逐轨自算样本标准差, 单篇或零有效篇时未定义返回 NaN。因 ctx 轨已滤除银行无关段落, 其组内分散度通常低于全文轨, 故本列水平不宜与全文轨标准差直接比大小, 而应在各自轨内解读。


## VAR: avg_llm_prob_score_std_full

【变体差分】
本列是概率映射情感分在全文 (full) 轨上的银行-年组内标准差, 是家族标准差三兄弟中对应 canonical 轨的一支。它度量全文轨逐篇语调在银行-年内的离散度, 反映该行该年媒体报道语调的一致性 (分歧度)。计算链路是先由 compute_prob_score 得每篇全文轨的连续分, 再在银行-年组内取样本标准差。因 full 轨即留篇门控轨, 本列的样本域与面板行宇宙完全对齐, 无 conditional-on-full 的子集缩减, 故是三条标准差轨中样本最全、最可作水平比较的一支。构念上它是语调二阶矩, 与 avg_llm_prob_score_full 的一阶矩正交: 两行该年语调均值可能相同, 但一行语调整齐、另一行两极分化, 本列即捕捉此差异。它与 ctx、ss 轨标准差互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。典型用法是把语调分歧引入异质性检验, 或作为媒体不确定性代理, 而非直接作语调水平的处理变量。
在计量应用上, 本列是媒体语调分歧的基准二阶矩测度: 常作调节变量检验语调分散对语调水平效应的放大 / 抵消, 或作媒体关注不确定性的代理进入稳健性表。因全文轨即留篇门控轨, 本列样本域与面板行宇宙对齐, 是三条标准差轨中唯一可作跨行水平比较的一支 (无子集缩减导致的不可比)。逐篇分先经 P3_INV 剔除无效标注再取样本标准差, 故分散度反映的是有效语调判定之间的真实分歧, 而非无效值噪声。它与均值列正交, 两者可同时进入模型而不构成机械共线。


## VAR: avg_llm_prob_score_std_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上的银行-年组内标准差。它度量最严格取材下, 银行-年内逐篇语调的离散程度: 因 ss 轨只看银行与金科同句共现片段, 本列反映的是纯银行-金科关系语调在同年不同报道间的分歧。计算上先由 compute_prob_score 得逐篇 ss 轨分 (无同句共现的篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)), 再在银行-年组内取样本标准差。它与 full、ctx 轨标准差互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。由于 ss 轨样本最窄、每银行-年有效篇数最少, 本列在 dev T=2 上极易出现 NaN 或零方差退化 (单篇或零篇时标准差未定义), 属预期行为, 生产 T=19 语料密度足够时恢复。相较均值列, 本列同样定位为二阶矩的稳健性 / 异质性诊断轨, 不进语调水平主回归; 其与 full、ctx 标准差的比较可揭示语调分歧是集中于银行-金科同句语境还是弥散于全文。
在计量应用上, 本列度量银行-金科同句语境内的语调分歧, 是三条标准差轨中最贴近银行-金科关系本身、也最易稀疏的一支; 它可作最严取材下语调不确定性的代理, 与 full、ctx 标准差比较可判断分歧集中于同句语境还是弥散全文。聚合为 conditional-on-full 逐轨自算, 单篇 / 零篇未定义返回 NaN, fallback 篇按共享分母纳入。因样本双重受限 (留篇门控加同句取材), 使用本列须严格配合有效篇数门槛, 避免以极少样本的标准差作强推断。


## VAR: llm_prob_score_app_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上, 限定于创新位点被判为应用场景 (application locus) 子样本后的聚合语调。位点二分来自 Gomber 等 (2018) 的技术-应用框架, 由 stage 21 的 innovation_locus 分类给出 (应用场景对二元 positive_class); 本列只纳入 ctx 轨上被判为应用场景的报道, 在该子集上取概率映射情感分, 从而回答同为银行-金科报道, 聚焦落地应用的那部分语调是正是负。它与 tech (底层技术) 子样本形成位点两分的对照, 与 full、ss 轨的同类子样本互为稳健性、不分主次, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 按方向乘置信度产出, 只是样本被位点门控筛过。分类门控与情感取材同为 ctx 轨 (同轨条件), 区别于后面 lc/ls 后缀的跨轨门控变体。因留篇门控 full-only, 本列是在全文轨已保留报道内、按应用场景位点分层的 conditional 测度, 用于检验语调是否随创新位点异质。
在异质性分析中, 本列与 tech 子样本并列构成位点两臂, 用于检验媒体对聚焦金科落地应用的报道语调是否系统区别于聚焦底层技术的报道; 若应用臂语调系统性偏高, 或印证应用型创新更易被媒体正面叙事。聚合遵循 conditional-on-full 且位点门控与情感取材同为 ctx 轨, 分母为该银行-年 ctx 轨被判应用场景的有效篇数, 逐轨自算。位点分类平局时按保守 tie_default 归应用场景 (uniform-prior MAP 保守降级), 故本臂在证据薄弱时略偏充盈, 解读需留意此基率倾向。


## VAR: llm_prob_score_app_full

【变体差分】
本列是概率映射情感分在全文 (full) 轨上, 限定应用场景 (application locus) 子样本的聚合语调。它是 app 子样本族里对应 canonical 轨的一支: 位点分类由 stage 21 innovation_locus 给出 (应用场景为 positive 类), 本列只对全文轨上被判应用场景的报道取概率映射情感分。构念上它拆分了总语调, 单看聚焦金科落地应用 (支付、信贷、场景服务等) 的报道语调, 与 tech 子样本 (底层技术) 并列构成位点异质性的两臂。计算仍是 compute_prob_score 逐篇产分再按银行-年聚合, 差别仅在样本经位点门控。因 full 轨即留篇门控轨, 本列样本域与面板行宇宙对齐, 是 app 三轨中最完整的一支。它与 app_ctx、app_ss 互为稳健性、不分主次, 也与 tech_full 构成位点对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。典型用途是检验媒体对应用型金科报道的语调是否系统性区别于底层技术型报道, 从而支撑创新位点调节语调效应的假设。
在异质性分析中, 本列是位点分层的应用臂基准, 与 tech_full 对照构成媒体语调随创新位点异质的两臂检验; 它进入面板作为按位点切分的 conditional 语调测度, 而非独立处理变量。聚合遵循 full 轨留篇域, 分母为该银行-年全文轨被判应用场景的有效篇数。位点分类由三家 LLM 投票, 平局按保守 tie_default 归应用场景, 故本臂样本略含基率倾斜, 与 tech_full 比较时须以两臂一致的门控口径解读差异, 而不能把水平差直接等同于媒体偏好。它与 sub/symb 实质-象征分层正交, 两套切分互不嵌套。


## VAR: llm_prob_score_app_lc_ctx

【变体差分】
本列是 app (应用场景) 子样本概率映射情感分的跨轨门控变体: 情感取材在实体窗 (ctx) 轨, 而应用场景的位点分类门控 (lc = locus-ctx) 显式取自 ctx 轨的 innovation_locus 判定。它与不带 lc 中缀的 llm_prob_score_app_ctx 的区别在于把分类来源轨道显式钉死并标注, 用于在分类门控轨与情感取材轨的组合上做敏感性核验——当同轨门控 (app_ctx) 与显式 ctx 门控 (app_lc_ctx) 结果背离时, 说明子样本划分对轨道选择敏感。逐篇分仍由 compute_prob_score 产出, 样本经 ctx 轨位点分类为应用场景后筛出。它与 tech_lc_ctx (同为 ctx 门控的底层技术臂) 构成位点对照, 与 app 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因留篇门控 full-only, 本列是全文轨保留报道内、按 ctx 轨应用场景位点分层的 conditional 稳健性测度, 属显式跨轨归属标注体系的一员, 不进主语调回归而作分类稳健性诊断。
在稳健性表中, 本列专用于分类归属敏感性核验: 把它与同轨条件的 app_ctx 并置, 若两者系数与显著性一致, 则说明应用场景子样本的划分对位点分类取自哪条轨道不敏感, 增强位点异质性结论的稳健性; 若背离, 则提示位点标签本身随取材轨漂移, 需谨慎解读位点异质。聚合遵循 conditional-on-full, 分母为该银行-年 ctx 轨情感有效且经 ctx 轨位点判为应用场景的篇数。它属显式跨轨归属标注体系 (lc/ls/sc/ss) 的一员, 该体系与三轨主体系正交, 各自 just-identified, 从不并入同一 over-identified 检验。


## VAR: llm_prob_score_app_ls_ss

【变体差分】
本列是 app (应用场景) 子样本概率映射情感分的跨轨门控变体: 情感取材在同句窗 (ss) 轨, 而应用场景位点分类门控 (ls = locus-ss) 显式取自 ss 轨的 innovation_locus 判定。它与 llm_prob_score_app_ss 的差别在于把分类来源轨道显式标注为 ss, 便于在最窄取材下核验位点子样本划分对轨道的敏感性。逐篇分由 compute_prob_score 产出, 喂入 content_ss, 样本经 ss 轨位点判为应用场景后筛出; 无同句共现的篇按 ss 轨 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容; 「镜像 ctx」仅指共享回退全文的公理)处理。它与 tech_ls_ss (ss 门控底层技术臂) 构成位点对照, 与 app 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因 ss 轨样本最窄且经位点再切分, 本列在 dev T=2 上极易稀疏或退化, 属预期, 生产 T=19 恢复。定位为最严取材下应用场景语调的分类稳健性诊断轨, 不进主回归。
在稳健性表中, 本列用于最窄取材下的分类归属敏感性核验: 与同轨条件的 app_ss 并置, 检验应用场景划分对 ss 轨位点分类的依赖; 因取材与门控双落 ss 轨, 本列对语料密度最敏感, 是位点异质结论在极端取材端是否成立的压力测试。聚合遵循 conditional-on-full, 分母为该银行-年 ss 轨情感有效且经 ss 轨位点判应用场景的篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified 并排, 从不并入同一 over-identified 检验。dev T=2 上样本极稀属预期。


## VAR: llm_prob_score_app_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上, 限定应用场景 (application locus) 子样本的聚合语调。取材为银行与金科同句共现片段 content_ss, 位点分类同取 ss 轨 innovation_locus (同轨条件, 区别于 app_ls_ss 的显式跨轨标注), 只纳入被判应用场景的报道后取概率映射情感分。它是 app 子样本在最严格取材端的一支, 与 app_full、app_ctx 互为稳健性、不分主次, 也与 tech_ss (底层技术臂) 构成位点对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 按方向乘置信度产出, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因留篇门控 full-only, 本列是全文轨保留报道内、以同句取材加应用场景位点双重限定的 conditional 测度, 信噪比取向最严: 它回答仅看银行-金科同句语境时, 聚焦应用落地的报道语调如何。dev T=2 上样本可能稀疏退化属预期, 生产 T=19 恢复正常密度。在异质性分析中, 本列是位点分层在最严取材端的应用臂, 与 tech_ss 对照检验银行-金科同句语境下应用场景与底层技术报道的语调分化。聚合遵循 conditional-on-full, 分母为该银行-年 ss 轨情感有效且经 ss 轨位点判应用场景的有效篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因位点以应用场景为二元正类, 本臂与技术臂互为对立子集, 此消彼长。因取材与切分双重受限, 使用本列须严格配合有效篇数门槛, 避免以极少样本作强推断; 它是位点异质结论在信噪比最严端的检验旁证。

## VAR: llm_prob_score_sub_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上, 限定实质性创新 (substantive) 子样本的聚合语调。实质-象征二分承接 Westphal 与 Zajac (1994、1998) 的框架, 由 stage 21 innovation_substantiveness 分类给出 (象征性为二元 positive_class, 故实质为其对立子集); 本列只纳入 ctx 轨上被判实质性的报道, 在该子集上取概率映射情感分, 回答那些讲真金白银投入 / 落地成效的金科报道语调如何。它与 symb (象征) 子样本构成实质-象征两分对照, 与 full、ss 轨同类子样本互为稳健性、不分主次, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分由 compute_prob_score 产出, 样本经实质性门控筛过, 分类与情感取材同为 ctx 轨 (同轨条件, 区别于 sub_sc_ctx 的显式跨轨标注)。因留篇门控 full-only, 本列是全文轨保留报道内、按实质性维度分层的 conditional 测度, 用于检验语调是否随创新实质性异质。
在异质性分析中, 本列与 symb 子样本并列构成实质-象征两臂, 服务于脱耦视角: 检验媒体对有真实资源投入的金科举措与对象征性表态的语调是否分化, 若实质臂语调系统偏高则支持媒体更认可实质创新。聚合遵循 conditional-on-full 且实质性门控与情感取材同为 ctx 轨, 分母为该银行-年 ctx 轨被判实质性的有效篇数, 逐轨自算。实质-象征分类以象征性为二元 positive_class, 平局按保守 tie_default 归象征性, 故实质臂是象征臂的对立子集, 两臂样本此消彼长而非独立抽取, 比较时须留意此结构性约束。


## VAR: llm_prob_score_sub_full

【变体差分】
本列是概率映射情感分在全文 (full) 轨上, 限定实质性创新 (substantive) 子样本的聚合语调, 是 sub 子样本族对应 canonical 轨的一支。实质-象征二分来自 Westphal 与 Zajac (1994、1998), 由 innovation_substantiveness 分类给出; 本列只对全文轨上被判实质性的报道取概率映射情感分。构念上它把总语调按创新的实质程度拆分, 单看有真实资源投入 / 可验证成效的金科报道语调, 与 symb_full (象征臂) 并列构成实质-象征异质性两臂。计算是 compute_prob_score 逐篇产分再按银行-年聚合, 样本经实质性门控。因 full 轨即留篇门控轨, 本列样本域与面板行宇宙对齐, 是 sub 三轨中最完整一支。它与 sub_ctx、sub_ss 互为稳健性、不分主次, 也与 symb_full 构成对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。典型用途是检验媒体对实质性金科举措与象征性表态的语调是否系统性不同, 支撑脱耦 (decoupling) 视角下语调分化的假设。
在异质性分析中, 本列是实质-象征分层的实质臂基准, 与 symb_full 对照构成语调随创新实质程度异质的两臂检验; 它进入面板作按实质性切分的 conditional 语调测度。聚合遵循 full 轨留篇域, 分母为该银行-年全文轨被判实质性的有效篇数。因实质性以象征性为二元正类, 本臂为象征臂的对立子集, 两臂之和约等于全文轨全集, 故 sub_full 与 symb_full 的语调差直接刻画脱耦程度。它与 tech/app 位点分层正交, 两套切分互不嵌套, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。


## VAR: llm_prob_score_sub_sc_ctx

【变体差分】
本列是 sub (实质性) 子样本概率映射情感分的跨轨门控变体: 情感取材在实体窗 (ctx) 轨, 而实质性分类门控 (sc = substantiveness-ctx) 显式取自 ctx 轨的 innovation_substantiveness 判定。它与不带 sc 中缀的 llm_prob_score_sub_ctx 的区别是把分类来源轨道显式钉死并标注, 用于核验实质性子样本划分对轨道选择的敏感性——同轨门控 (sub_ctx) 与显式 ctx 门控 (sub_sc_ctx) 若背离即提示分类对取材轨敏感。逐篇分由 compute_prob_score 产出, 样本经 ctx 轨实质性判定后筛出。它与 symb_sc_ctx (同为 ctx 门控的象征臂) 构成实质-象征对照, 与 sub 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因留篇门控 full-only, 本列是全文轨保留报道内、按 ctx 轨实质性维度分层的 conditional 稳健性测度, 属显式跨轨归属标注体系一员, 定位分类稳健性诊断而非主语调回归。
在稳健性表中, 本列用于实质性分类归属敏感性核验: 与同轨条件的 sub_ctx 并置, 若两者一致则说明实质性子样本划分对分类取自哪条轨道不敏感; 若背离则提示实质-象征标签随取材轨漂移。聚合遵循 conditional-on-full, 分母为该银行-年 ctx 轨情感有效且经 ctx 轨实质性判定为实质的篇数。它与 symb_sc_ctx 互为对立子集, 两者水平差即 ctx 门控下的脱耦度。本列属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified 并排, 从不并入同一 over-identified 检验; 定位分类稳健诊断而非语调水平主回归。


## VAR: llm_prob_score_sub_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上, 限定实质性创新 (substantive) 子样本的聚合语调。取材为银行与金科同句共现片段 content_ss, 实质性分类同取 ss 轨 innovation_substantiveness (同轨条件, 区别于 sub_ss_ss 的显式跨轨标注), 只纳入被判实质性的报道后取概率映射情感分。它是 sub 子样本在最严格取材端的一支, 与 sub_full、sub_ctx 互为稳健性、不分主次, 也与 symb_ss (象征臂) 构成实质-象征对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 按方向乘置信度产出, 无同句共现篇按 ss 轨 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因留篇门控 full-only, 本列是全文轨保留报道内、以同句取材加实质性维度双重限定的 conditional 测度, 回答仅看银行-金科同句语境时实质性举措的报道语调如何。dev T=2 上因样本经双重切分极易稀疏退化, 属预期, 生产 T=19 恢复。
在异质性分析中, 本列是实质-象征分层在最严取材端的实质臂, 与 symb_ss 对照检验银行-金科同句语境下实质创新与象征表态的语调分化。聚合遵循 conditional-on-full 且实质性门控与情感取材同为 ss 轨, 分母为该银行-年 ss 轨被判实质性的有效篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因实质性以象征性为正类, 本臂为象征臂对立子集, 二者此消彼长。因取材与切分双重受限, 本列在 dev T=2 上极易稀疏退化, 使用须配合有效篇数门槛, 生产 T=19 恢复正常密度。


## VAR: llm_prob_score_sub_ss_ss

【变体差分】
本列是 sub (实质性) 子样本概率映射情感分的跨轨门控变体: 情感取材在同句窗 (ss) 轨, 且实质性分类门控 (前一个 ss = substantiveness-ss) 显式取自 ss 轨的 innovation_substantiveness 判定, 故列名出现双 ss (前者标分类来源轨、后者标情感取材轨)。它与同轨条件的 llm_prob_score_sub_ss 的区别在于把分类来源轨道显式标注为 ss, 便于在最窄取材下核验实质性子样本划分对轨道的敏感性。逐篇分由 compute_prob_score 产出, 喂入 content_ss, 样本经 ss 轨实质性判定后筛出, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它与 symb_ss_ss (ss 门控象征臂) 构成实质-象征对照, 与 sub 族其它变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因双重 ss 切分, 本列在 dev T=2 上最易稀疏或退化, 属预期, 生产 T=19 恢复。定位为最严取材下实质性语调的分类稳健性诊断轨, 不进主回归。
在稳健性表中, 本列用于最窄取材下的实质性分类归属敏感性核验: 与同轨条件的 sub_ss 并置, 检验实质性划分对 ss 轨分类的依赖; 双 ss 意味着分类与情感取材均落最窄轨, 是脱耦结论在极端取材端是否成立的压力测试。聚合遵循 conditional-on-full, 分母为该银行-年 ss 轨情感有效且经 ss 轨判实质的篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它与 symb_ss_ss 互为对立子集。本列属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified, 从不并入同一 over-identified 检验; dev T=2 上最易稀疏属预期。


## VAR: llm_prob_score_symb_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上, 限定象征性创新 (symbolic) 子样本的聚合语调。象征性是 Westphal 与 Zajac (1994、1998) 实质-象征二分中作为二元 positive_class 的一侧, 由 stage 21 innovation_substantiveness 分类给出; 本列只纳入 ctx 轨上被判象征性的报道, 在该子集取概率映射情感分, 回答那些偏表态 / 造势而缺实质投入的金科报道语调如何。它与 sub (实质) 子样本构成实质-象征对照, 与 full、ss 轨同类子样本互为稳健性、不分主次, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分由 compute_prob_score 产出, 样本经象征性门控, 分类与情感取材同为 ctx 轨 (同轨条件, 区别于 symb_sc_ctx 的显式跨轨标注)。因留篇门控 full-only, 本列是全文轨保留报道内、按象征性维度分层的 conditional 测度, 用于检验象征性表态类报道的语调是否系统区别于实质性举措。
在异质性分析中, 本列与 sub 子样本并列构成实质-象征两臂, 单看偏姿态 / 造势而缺实质投入的金科报道语调; 若象征臂语调异常偏高, 或提示媒体语调被公关性叙事驱动而非真实绩效, 是识别语调质量的重要旁证。聚合遵循 conditional-on-full 且象征性门控与情感取材同为 ctx 轨, 分母为该银行-年 ctx 轨被判象征性的有效篇数, 逐轨自算。象征性为二元 positive_class, 平局按保守 tie_default 归象征性, 故本臂在证据薄弱时略偏充盈, 与实质臂比较时须留意此基率倾向与两臂对立子集结构。


## VAR: llm_prob_score_symb_full

【变体差分】
本列是概率映射情感分在全文 (full) 轨上, 限定象征性创新 (symbolic) 子样本的聚合语调, 是 symb 子样本族对应 canonical 轨的一支。象征性由 innovation_substantiveness 分类 (positive_class=象征性) 给出; 本列只对全文轨上被判象征性的报道取概率映射情感分。构念上它单看偏姿态 / 造势而缺真实资源投入的金科报道语调, 与 sub_full (实质臂) 并列构成实质-象征异质性两臂, 直接服务于脱耦视角: 若媒体对象征性表态给出的语调系统性高于 (或低于) 实质性举措, 即揭示语调可能被公关性叙事驱动而非真实创新绩效。计算是 compute_prob_score 逐篇产分再按银行-年聚合, 样本经象征性门控。因 full 轨即留篇门控轨, 本列样本域与面板行宇宙对齐, 是 symb 三轨中最完整一支。它与 symb_ctx、symb_ss 互为稳健性、不分主次, 也与 sub_full 构成对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。
在异质性分析中, 本列是实质-象征分层的象征臂基准, 与 sub_full 对照直接刻画脱耦程度 (象征表态语调减实质举措语调); 它进入面板作按象征性切分的 conditional 语调测度。聚合遵循 full 轨留篇域, 分母为该银行-年全文轨被判象征性的有效篇数。因象征性为二元正类, 本臂与实质臂互为对立子集, 二者之和约等于全文轨全集。它服务于检验媒体是否对象征性金科表态给出与实质举措系统不同的语调, 与 tech/app 位点分层正交, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。


## VAR: llm_prob_score_symb_sc_ctx

【变体差分】
本列是 symb (象征性) 子样本概率映射情感分的跨轨门控变体: 情感取材在实体窗 (ctx) 轨, 而象征性分类门控 (sc = substantiveness-ctx) 显式取自 ctx 轨的 innovation_substantiveness 判定。它与同轨条件的 llm_prob_score_symb_ctx 的区别是把分类来源轨道显式钉死并标注, 用于核验象征性子样本划分对轨道选择的敏感性——同轨门控 (symb_ctx) 与显式 ctx 门控 (symb_sc_ctx) 若背离即提示分类对取材轨敏感。逐篇分由 compute_prob_score 产出, 样本经 ctx 轨象征性判定后筛出。它与 sub_sc_ctx (同为 ctx 门控的实质臂) 构成实质-象征对照, 与 symb 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因留篇门控 full-only, 本列是全文轨保留报道内、按 ctx 轨象征性维度分层的 conditional 稳健性测度, 属显式跨轨归属标注体系一员, 定位分类稳健性诊断而非主语调回归。
在稳健性表中, 本列用于象征性分类归属敏感性核验: 与同轨条件的 symb_ctx 并置, 若两者一致则说明象征性子样本划分对分类取自哪条轨道不敏感; 若背离则提示实质-象征标签随取材轨漂移。聚合遵循 conditional-on-full, 分母为该银行-年 ctx 轨情感有效且经 ctx 轨判象征的篇数。它与 sub_sc_ctx 互为对立子集, 两者水平差即 ctx 门控下的脱耦度。本列属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified 并排, 从不并入同一 over-identified 检验; 定位分类稳健诊断而非语调水平主回归。


## VAR: llm_prob_score_symb_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上, 限定象征性创新 (symbolic) 子样本的聚合语调。取材为银行与金科同句共现片段 content_ss, 象征性分类同取 ss 轨 innovation_substantiveness (同轨条件, 区别于 symb_ss_ss 的显式跨轨标注), 只纳入被判象征性的报道后取概率映射情感分。它是 symb 子样本在最严格取材端的一支, 与 symb_full、symb_ctx 互为稳健性、不分主次, 也与 sub_ss (实质臂) 构成实质-象征对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 按方向乘置信度产出, 无同句共现篇按 ss 轨 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因留篇门控 full-only, 本列是全文轨保留报道内、以同句取材加象征性维度双重限定的 conditional 测度, 回答仅看银行-金科同句语境时象征性表态类报道的语调如何。dev T=2 上因样本经双重切分极易稀疏退化, 属预期, 生产 T=19 恢复。
在异质性分析中, 本列是实质-象征分层在最严取材端的象征臂, 与 sub_ss 对照检验银行-金科同句语境下象征表态与实质举措的语调分化。聚合遵循 conditional-on-full 且象征性门控与情感取材同为 ss 轨, 分母为该银行-年 ss 轨被判象征性的有效篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因象征性为二元正类, 本臂与实质臂互为对立子集, 此消彼长。因取材与切分双重受限, 本列在 dev T=2 上极易稀疏退化, 使用须配合有效篇数门槛, 生产 T=19 恢复正常密度。


## VAR: llm_prob_score_symb_ss_ss

【变体差分】
本列是 symb (象征性) 子样本概率映射情感分的跨轨门控变体: 情感取材在同句窗 (ss) 轨, 且象征性分类门控 (前一个 ss = substantiveness-ss) 显式取自 ss 轨的 innovation_substantiveness 判定, 故列名出现双 ss (前者标分类来源轨、后者标情感取材轨)。它与同轨条件的 llm_prob_score_symb_ss 的区别在于把分类来源轨道显式标注为 ss, 便于在最窄取材下核验象征性子样本划分对轨道的敏感性。逐篇分由 compute_prob_score 产出, 喂入 content_ss, 样本经 ss 轨象征性判定后筛出, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它与 sub_ss_ss (ss 门控实质臂) 构成实质-象征对照, 与 symb 族其它变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因双重 ss 切分, 本列在 dev T=2 上最易稀疏或退化, 属预期, 生产 T=19 恢复。定位为最严取材下象征性语调的分类稳健性诊断轨, 不进主回归。
在稳健性表中, 本列用于最窄取材下象征性分类归属敏感性核验: 与同轨条件的 symb_ss 并置, 检验象征性划分对 ss 轨分类的依赖; 双 ss 意味分类与情感取材均落最窄轨, 是脱耦结论在极端取材端的压力测试。聚合遵循 conditional-on-full, 分母为该银行-年 ss 轨情感有效且经 ss 轨判象征的篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它与 sub_ss_ss 互为对立子集。本列属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified, 从不并入同一 over-identified 检验; dev T=2 上最易稀疏属预期。


## VAR: llm_prob_score_tech_ctx

【变体差分】
本列是概率映射情感分在实体窗 (ctx) 轨上, 限定底层技术 (technology locus) 子样本的聚合语调。技术-应用位点二分承接 Gomber 等 (2018), 由 stage 21 innovation_locus 分类给出 (底层技术为应用场景的对立子集); 本列只纳入 ctx 轨上被判底层技术的报道, 在该子集取概率映射情感分, 回答那些讲底层技术攻坚 (区块链、AI、云原生等基础设施) 的金科报道语调如何。它与 app (应用场景) 子样本构成位点两分对照, 与 full、ss 轨同类子样本互为稳健性、不分主次, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分由 compute_prob_score 产出, 样本经底层技术位点门控, 分类与情感取材同为 ctx 轨 (同轨条件, 区别于 tech_lc_ctx 的显式跨轨标注)。因留篇门控 full-only, 本列是全文轨保留报道内、按底层技术位点分层的 conditional 测度, 用于检验技术型报道语调是否区别于应用型。
在异质性分析中, 本列与 app 子样本并列构成位点两臂, 单看聚焦底层技术攻坚的金科报道语调; 因底层技术投入见效周期长、不确定性高, 其报道语调常系统性偏谨慎, 与应用臂对照可检验此结构性差异。聚合遵循 conditional-on-full 且位点门控与情感取材同为 ctx 轨, 分母为该银行-年 ctx 轨被判底层技术的有效篇数, 逐轨自算。位点分类以应用场景为二元正类, 平局归应用场景, 故底层技术臂为其对立子集, 两臂样本此消彼长, 比较时须留意此结构性约束与保守基率倾向。


## VAR: llm_prob_score_tech_full

【变体差分】
本列是概率映射情感分在全文 (full) 轨上, 限定底层技术 (technology locus) 子样本的聚合语调, 是 tech 子样本族对应 canonical 轨的一支。位点分类由 innovation_locus 给出 (底层技术臂); 本列只对全文轨上被判底层技术的报道取概率映射情感分。构念上它单看聚焦底层技术研发的金科报道语调, 与 app_full (应用场景臂) 并列构成技术-应用位点异质性两臂, 服务于检验媒体语调是否随创新位点而系统性不同——例如底层技术投入见效周期长、不确定性高, 其报道语调可能系统性偏谨慎。计算是 compute_prob_score 逐篇产分再按银行-年聚合, 样本经底层技术位点门控。因 full 轨即留篇门控轨, 本列样本域与面板行宇宙对齐, 是 tech 三轨中最完整一支。它与 tech_ctx、tech_ss 互为稳健性、不分主次, 也与 app_full 构成位点对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。
在异质性分析中, 本列是位点分层的技术臂基准, 与 app_full 对照构成语调随创新位点异质的两臂检验; 它进入面板作按位点切分的 conditional 语调测度。聚合遵循 full 轨留篇域, 分母为该银行-年全文轨被判底层技术的有效篇数。因位点以应用场景为二元正类, 本臂为应用臂对立子集, 二者之和约等于全文轨全集, 故 tech_full 与 app_full 的语调差直接刻画媒体对两类创新位点的语调偏好。它与 sub/symb 实质-象征分层正交, 两套切分互不嵌套, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。


## VAR: llm_prob_score_tech_lc_ctx

【变体差分】
本列是 tech (底层技术) 子样本概率映射情感分的跨轨门控变体: 情感取材在实体窗 (ctx) 轨, 而底层技术位点分类门控 (lc = locus-ctx) 显式取自 ctx 轨的 innovation_locus 判定。它与同轨条件的 llm_prob_score_tech_ctx 的区别是把分类来源轨道显式钉死并标注, 用于核验底层技术位点子样本划分对轨道选择的敏感性——同轨门控 (tech_ctx) 与显式 ctx 门控 (tech_lc_ctx) 若背离即提示分类对取材轨敏感。逐篇分由 compute_prob_score 产出, 样本经 ctx 轨位点判为底层技术后筛出。它与 app_lc_ctx (同为 ctx 门控的应用场景臂) 构成位点对照, 与 tech 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因留篇门控 full-only, 本列是全文轨保留报道内、按 ctx 轨底层技术位点分层的 conditional 稳健性测度, 属显式跨轨归属标注体系一员, 定位分类稳健性诊断而非主语调回归。
在稳健性表中, 本列用于底层技术分类归属敏感性核验: 与同轨条件的 tech_ctx 并置, 若两者一致则说明底层技术子样本划分对位点分类取自哪条轨道不敏感; 若背离则提示位点标签随取材轨漂移。聚合遵循 conditional-on-full, 分母为该银行-年 ctx 轨情感有效且经 ctx 轨位点判底层技术的篇数。它与 app_lc_ctx 互为对立子集, 两者水平差即 ctx 门控下的位点语调偏好。本列属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified 并排, 从不并入同一 over-identified 检验; 定位分类稳健诊断而非语调水平主回归。


## VAR: llm_prob_score_tech_ls_ss

【变体差分】
本列是 tech (底层技术) 子样本概率映射情感分的跨轨门控变体: 情感取材在同句窗 (ss) 轨, 而底层技术位点分类门控 (ls = locus-ss) 显式取自 ss 轨的 innovation_locus 判定。它与同轨条件的 llm_prob_score_tech_ss 的区别在于把分类来源轨道显式标注为 ss, 便于在最窄取材下核验底层技术位点子样本划分对轨道的敏感性。逐篇分由 compute_prob_score 产出, 喂入 content_ss, 样本经 ss 轨位点判为底层技术后筛出; 无同句共现篇按 ss 轨 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容; 「镜像 ctx」仅指共享回退全文的公理)处理。它与 app_ls_ss (ss 门控应用场景臂) 构成位点对照, 与 tech 族其它轨 / 门控变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因 ss 轨样本最窄且经位点再切分, 本列在 dev T=2 上极易稀疏或退化, 属预期, 生产 T=19 恢复。定位为最严取材下底层技术语调的分类稳健性诊断轨, 不进主回归。
在稳健性表中, 本列用于最窄取材下底层技术分类归属敏感性核验: 与同轨条件的 tech_ss 并置, 检验底层技术划分对 ss 轨位点分类的依赖; 因取材与门控双落 ss 轨, 本列对语料密度最敏感, 是位点异质结论在极端取材端是否成立的压力测试。聚合遵循 conditional-on-full, 分母为该银行-年 ss 轨情感有效且经 ss 轨位点判底层技术的篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。它与 app_ls_ss 互为对立子集, 属显式跨轨归属标注体系一员, 与三轨主体系正交, 各自 just-identified, 从不并入同一 over-identified 检验; dev T=2 上样本极稀属预期。


## VAR: llm_prob_score_tech_ss

【变体差分】
本列是概率映射情感分在同句窗 (ss) 轨上, 限定底层技术 (technology locus) 子样本的聚合语调。取材为银行与金科同句共现片段 content_ss, 位点分类同取 ss 轨 innovation_locus (同轨条件, 区别于 tech_ls_ss 的显式跨轨标注), 只纳入被判底层技术的报道后取概率映射情感分。它是 tech 子样本在最严格取材端的一支, 与 tech_full、tech_ctx 互为稳健性、不分主次, 也与 app_ss (应用场景臂) 构成位点对照, 各子样本与各轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。逐篇分仍由 compute_prob_score 按方向乘置信度产出, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因留篇门控 full-only, 本列是全文轨保留报道内、以同句取材加底层技术位点双重限定的 conditional 测度, 信噪比取向最严: 它回答仅看银行-金科同句语境时, 聚焦底层技术的报道语调如何。dev T=2 上样本可能稀疏退化属预期, 生产 T=19 恢复正常密度。
在异质性分析中, 本列是位点分层在最严取材端的技术臂, 与 app_ss 对照检验银行-金科同句语境下底层技术与应用场景报道的语调分化。聚合遵循 conditional-on-full 且位点门控与情感取材同为 ss 轨, 分母为该银行-年 ss 轨被判底层技术的有效篇数, 无同句共现篇按 fallback 回退取全文 body (与 content_full 同源, 非 ctx 实体窗内容)。因位点以应用场景为二元正类, 本臂为应用臂对立子集, 此消彼长。因取材与切分双重受限, 本列在 dev T=2 上极易稀疏退化, 使用须配合有效篇数门槛, 生产 T=19 恢复正常密度; 它是位点异质结论在信噪比最严端的检验。

<!-- rendered-citations:begin -->
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper, Federal Reserve Board No. No. 2026-020 [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Renze, M. (2024). The effect of sampling temperature on problem solving in large language models. Findings of the Association for Computational Linguistics: EMNLP 2024, 7346-7356. https://doi.org/10.18653/v1/2024.findings-emnlp.432
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Lopez-Lira, A., & Tang, Y. (2023). Can ChatGPT forecast stock price movements? Return predictability and large language models. SSRN Working Paper No. No. 4412788 [Working Paper]. https://doi.org/10.2139/ssrn.4412788
Fatouros, G., Soldatos, J., Kouroumali, K., Makridis, G., & Kyriazis, D. (2023). Transforming sentiment analysis in the financial domain with ChatGPT. Machine Learning with Applications, 14, 100508. https://doi.org/10.1016/j.mlwa.2023.100508
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
