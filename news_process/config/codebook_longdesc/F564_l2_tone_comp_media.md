---
family_id: F564
columns:
- tone_comp_media_ctx
- tone_comp_media_full
- tone_comp_media_ss
unit: 语调/正向倾向得分 (连续, 名义 [-1,1]; bank-year 面板层面为该银行当年"综合类"媒体子样本内三家 LLM 多数投票情感分的算术均值)
formula: 'tone_comp_media{track} = mean_{i∈(target_bank=b, year=y, _media_type=comp)} llm_vote_score{track}_i, track∈{_full,_ctx,_ss}; _media_type 由 attention_media.py 内媒体分类规则派生 (comp=综合类媒体, 与 fin=财经类、other=其余类型三分互斥); llm_vote_score{track} 源自 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票情感分'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss)
- 媒体来源分类元数据 (媒体(中文) → _media_type)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving content to investor sentiment - The role of media in the stock market
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: The media and the diffusion of information in financial markets - Evidence from newspaper strikes
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., Shapiro, J. M.
  year: 2010
  title: What drives media slant - Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., Yuan, Y.
  year: 2024
  title: Media sentiment, deposit stability and bank systemic risk - Evidence from China
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., Branzoli, N.
  year: 2025
  title: Measuring tone shifts in media coverage - An empirical application to bank financing conditions in Italy
  venue: SSRN Working Paper
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., Boukes, M.
  year: 2021
  title: The validity of sentiment analysis - Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: "10.1016/j.heliyon.2024.e30211"
  title: "Sentimental showdown: News media vs. social media in stock markets"
  authors: "Nyakurukwa, K., Seetharam, Y."
  year: 2024
  venue: "Heliyon"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
  - "10.1016/j.heliyon.2024.e30211"
  - "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
本家族测度媒体报道来源类型异质性对报道语调的影响, 是 P2 (`bank_fintech_attention`) 媒体属性维度中"内容/受众定位"这一分类轴的具体化。producer `pipeline/panel/attention_media.py` 在文章级把媒体来源划分为三个互斥类别: `fin` (财经专业媒体)、`comp` (综合性大众媒体)、`other` (其余/未分类媒体), 划分依据是媒体来源字段 (`媒体(中文)`) 的名录归类, 与银行报道内容本身无关, 是媒体机构的先验属性标签。`tone_comp_media` 即该三分类中"综合类"分支在 bank-year 层面的报道情感均值: 对于目标银行 `target_bank` 在年份 `year` 内、来源被判定为综合类媒体 (`_media_type == 'comp'`) 的全部文章, 取其 stage 21 三家 LLM 多数投票情感分 (`llm_vote_score{track}`) 的算术均值。这一构念直接呼应新闻传播学与金融文本分析交叉领域长期关注的"报道渠道异质性"命题: 不同定位的媒体机构因受众结构、编辑方针、商业模式不同, 对同一对象的报道基调系统性有别 (Gentzkow & Shapiro 2010 关于媒体立场稳定性的经典论证即建立在渠道固定效应之上)。财经专业媒体与综合类大众媒体的受众、专业化程度、监管敏感度都不同: 财经媒体读者群体偏专业投资者与机构, 报道用语与信息密度受行业规范约束较强; 综合类媒体面向大众读者, 更强调可读性与新闻价值 (news value), 在报道基调上可能表现出更强的情绪化倾向或更受一般社会议题 (如消费者权益、社会责任) 牵引。`tone_comp_media` 与家族同源的 `tone_fin_media`(财经类)、`tone_other_media`(其余类) 三者并列构成媒体类型异质性的完整拆分, 并在 producer 内进一步派生出两两情感缺口指标 (`tone_gap_fin_comp` 等, 非本家族列, 属邻近家族), 用于直接检验渠道差异的统计显著性。

【方法学与计算】
计算分两步。第一步是媒体分类: producer 在文章级构造 `_media_type` 列, 依据媒体来源名称在预设名录中的归属, 把每篇报道标记为 `fin`/`comp`/`other` 三者之一, 这一分类与文章内容、情感分无关, 纯粹基于媒体机构属性; 随后按 `(target_bank, year)` 分组统计 `_is_comp` 哑元的组内均值得到 `comp_media_frac` (综合类媒体占比, 邻近家族列, 非本家族)。第二步是分类内情感聚合: 对每个三轨情感分来源列 `llm_vote_score{track}` (`track` ∈ `{_full, _ctx, _ss}`), producer 先筛出 `_media_type == 'comp'` 的子样本, 再按 `(target_bank, year)` 分组取该轨情感分的均值, 得到 `tone_comp_media{track}`。三轨分别对应 stage 21 情感 LLM 在全文、实体上下文窗口、银行∧金科同句共现窗口三种文本切分口径下产出的情感分, 三者是各自独立、just-identified 并排的稳健性口径, 互为稳健性、不分主次, 分析中禁止把三轨情感分混入同一个 over-identified 模型 (如同一 Hansen J 过识别检验) 中联合使用。若某轨的源列 `llm_vote_score{track}` 在上游 stage 21 输出中缺席 (例如离线复现未覆盖某轨), producer 用 `if src not in df.columns: continue` 优雅跳过整轨, 该轨对应的三个媒体类型情感列 (`tone_fin/comp/other_media{track}`) 及其缺口列同步不产出, 不会静默填充误导性的零或全体均值。留篇口径遵循全仓 full-only 门控铁律 (2026-06-29 生效): 一篇报道是否计入"银行-金科相关报道"的样本全集, 仅由 `llm_vote_score_full` 所在轨 (即 `llm_verified_full`) 判定, ctx/ss 轨的 `tone_comp_media` 是在 full-only 判定后的行宇宙子集上、按各自轨道文本重新计算情感分, 而非独立扩样。`_ss` 轨的回退语义镜像 `_ctx`: 当某篇报道内银行实体与金科词未出现在同一句 (窗口半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 时, `content_ss` 退化为全文正文 (`ss_is_fallback=True`), 该篇的 `llm_vote_score_ss` 仍基于此退化文本计算, 不会因缺乏严格同句共现而被排除出 `tone_comp_media_ss` 的均值分母。若某 bank-year 组合内 `_media_type=='comp'` 的文章数为零 (即该银行当年没有被综合类媒体报道), 对应三个轨道的 `tone_comp_media{track}` 在 `merge(..., how='left')` 之后均为缺失值 (NaN), 这是分组均值在空组上的自然结果, 不代表零情感或中性情感, 使用时须与 `comp_media_frac==0` 联合判读避免误读为"情感中性"。

【文献定位】
媒体渠道异质性影响文本语调与市场反应的命题在实证金融与传播学交叉文献中有稳固根基。Tetlock (2007, *Journal of Finance*) 首次系统证明报纸文本语调蕴含独立于基本面的可预测信息, 为"媒体语调是一种可计量的经济信号"确立了方法论基准, 本家族对综合类媒体情感的单独提取正是延续这一传统, 把渠道异质性作为语调信号的一个调节维度。Peress (2014, *Journal of Finance*) 利用报纸罢工的准自然实验证明媒体在信息扩散中扮演因果角色而非被动传声筒, 意味着不同类型媒体的语调差异本身具有经济后果而非纯噪声。Gentzkow & Shapiro (2010, *Econometrica*) 的媒体立场模型表明媒体机构的编辑倾向具有跨时间的稳定性, 为把媒体类型 (而非单篇文章特征) 作为语调差异的组织维度提供了理论支撑——即综合类与财经类媒体的语调差异预期是系统性、持续性的机构特征, 而非随机噪声。就中国情境与银行业设定而言, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 直接在中国银行样本上考察媒体情感对存款稳定性与系统性风险的影响, 是本家族最直接的同域实证参照; Marchetti, Tarducci & Branzoli (2025, SSRN) 提出的银行×年语气聚合方法与本家族"按银行-年分组取媒体子样本情感均值"的聚合逻辑高度一致。三家 LLM 多数投票情感分本身的方法学基础见 van Atteveldt, van der Velden & Boukes (2021, *Communication Methods and Measures*) 对情感分析多方法效度比较的系统评估, 该文强调不同标注/分类方法 (人工标注、众包、词典法、机器学习) 在效度上的差异性, 支持本项目采用多家 LLM 投票而非单一方法降低测量误差的设计选择。Nyakurukwa 和 Seetharam (2024, Heliyon) 对比新闻媒体与社交媒体情感对四国股市回报的差异化影响, 佐证不同媒体渠道情感信号系统性有别的构念。Chuang, He 和 Hu (2025, Big Data and Cognitive Computing) 以中文财经新闻为语料, 系统比较多种词嵌入与大语言模型在情感分类与股价预测任务上的表现, 支持本项目多模型情感聚合的方法学选择。

## VAR: tone_comp_media_ctx

【变体差分】
本列是 `tone_comp_media` 家族在 ctx (实体上下文窗口) 轨道上的实现, 源列为 `llm_vote_score_ctx`。ctx 轨的文本切分口径是"标题 + 银行/金科实体所在窗口" (由 stage 14 `ctx_materializer` 物化的 `content_ctx`, `prepend_title` 拼接), 相较 full 轨截断了与银行/金科实体无直接邻近关系的段落, 目的是聚焦报道中与目标实体最相关的语义片段, 降低无关叙事 (如同一篇综合性报道中穿插的宏观新闻、其他机构消息) 对情感分的稀释效应。留篇门控依旧是 full-only: 是否计入某银行当年的报道全集只看 `llm_verified_full`, ctx 轨仅在此行宇宙子集上重新取该轨文本的情感分并按 `_media_type=='comp'` 筛选聚合, 因此 `tone_comp_media_ctx` 与 `tone_comp_media_full` 共享完全相同的 (target_bank, year) 分组行集合与相同的综合类媒体归属判定, 差异仅来自送入 LLM 的文本切片不同导致的情感分数值差异。与 `_full` 轨相比, ctx 轨对于综合类媒体报道尤其重要: 综合类媒体文章往往篇幅长、话题跨度大 (例如一篇年终经济综述里仅一段提及某银行的金科合作), full 轨情感分可能被主体无关内容拉向中性或被其他话题的语调污染, ctx 轨通过聚焦实体邻近窗口更贴近"报道对该银行到底是什么态度"的构念意图。ctx 轨与 full 轨、ss 轨三者是各自独立、just-identified 并排的稳健性口径, 互为稳健性、不分主次, 严禁把三轨情感分同时纳入同一个 over-identified 的 Hansen J 过识别检验框架; 实证分析中应将三轨结果并列汇报作为文本切分口径的稳健性证据链, 而非挑选单一轨道作为"更优"版本。若某银行某年综合类媒体报道虽存在但相关文章的 `llm_vote_score_ctx` 均缺失 (理论上罕见, 因 ctx 轨与 full 轨共享同一批留篇文章), 该 bank-year 的 `tone_comp_media_ctx` 相应缺失, 使用者应结合 `comp_media_frac` 判断是分类样本本身为空还是仅 ctx 轨情感分缺失。

## VAR: tone_comp_media_full

【变体差分】
本列是 `tone_comp_media` 家族的 full (全文) 轨道实现, 也是三轨中口径最宽的一支: 源列 `llm_vote_score_full` 由三家 LLM (gpt54nano/gemini31/deepseekv4) 对文章标题+完整正文文本 (`content_full`) 独立打分后多数投票得到, 未做任何实体窗口截断。留篇门控本身即以本轨 (`llm_verified_full`) 为唯一判据: 一篇报道是否被计入某银行当年"综合类媒体报道"的样本全集, 完全由 full 轨的 LLM 验证结果决定, ctx/ss 两轨只是在此确定的行宇宙子集内换用不同文本切片重新计算情感分, 因此 `tone_comp_media_full` 在概念上处于"锚定轨"地位——它既是最完整文本信息量的情感测度, 也是决定其余两轨样本范围的门控轨。在 P1 (`bank_fintech_tone`) 论文的主处理变量口径中, `llm_vote_tone_full` 是 headline treatment (自 2026-06-29 起从 `_ctx` 切换为 `_full` 主轨), 本列作为其在综合类媒体子样本上的细分版本, 天然继承 full 轨作为论文主口径的方法学地位; 但这不改变家族内部三轨"各自 just-identified 并排、互为稳健性不分主次"的分析铁律——`tone_comp_media_full` 不因是门控轨而在统计推断上优先于 ctx/ss 两轨, 三者依旧应作为独立稳健性口径分别汇报, 禁止混入同一 over-identified Hansen J 框架。full 轨相对 ctx/ss 轨的方法学取舍是: 保留完整叙事上下文 (包括可能与目标银行无直接关联的段落), 换来更贴近人类读者整体阅读体验的情感测度, 但也更易受综合类媒体常见的长篇、多话题、软新闻 (soft news) 写作风格稀释; 这一权衡在综合类媒体子样本上尤为突出, 因综合类媒体的报道篇幅与话题跨度通常大于财经专业媒体。

## VAR: tone_comp_media_ss

【变体差分】
本列是 `tone_comp_media` 家族在 ss (银行∧金科同句共现) 轨道上的实现, 源列 `llm_vote_score_ss`。ss 轨的文本切分口径最严格: 仅纳入目标银行实体与金科相关词汇同句共现 (句窗半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 ±1 句) 的片段构成 `content_ss` (同样经 `prepend_title` 拼接标题), 目的是把情感测度锁定到银行与金科议题真正同时出现、语义上直接相关的最小语境, 排除报道中银行与金科议题分别独立出现但彼此无关联的段落。ss 轨的回退语义严格镜像 ctx 轨: 当某篇报道内不存在银行∧金科同句共现时, `content_ss` 退化为全文正文, 并置 `ss_is_fallback=True`; 此时该篇文章仍正常参与 `n_articles` 分母与情感分计算, 不会因未命中严格同句条件而被剔除样本, 这是为了避免"同句共现"这一严格判据把大量"确实相关但表述分散"的报道系统性排除、从而在综合类媒体子样本 (往往话题分布更松散) 上产生更强的样本选择偏误。留篇门控同样是 full-only: `tone_comp_media_ss` 的 (target_bank, year) 行集合与综合类媒体归属判定与 full/ctx 两轨完全一致, 差异仅在于送入 LLM 打分的文本片段不同。ss 轨与 full/ctx 两轨、以及与网络三轨判据体系中"严格同句"判据 (`_sent` 后缀, 用于结构指标而非情感测度) 概念上呼应但不是同一构造原语: ss 轨的同句共现原语是 `extract_bank_fintech_cooccurrence` (银行×金科), 与结构指标判据后缀所用的 `map_bank_sentence_positions` (银行×银行) 属不同判据体系, 二者不可混淆或互相复用。三轨 (full/ctx/ss) 依旧遵循家族铁律: 各自独立 just-identified 并排, 互为稳健性、不分主次, 分析时不得混入同一个 over-identified Hansen J 过识别检验; ss 轨作为判据最严格的一支, 通常用于检验语调结论对"文本相关性"这一构念效度维度的敏感程度, 是三轨稳健性梯子中语境纯度最高但样本噪声 (因回退机制) 也需要单独审视的一支。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving content to investor sentiment - The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Peress, J. (2014). The media and the diffusion of information in financial markets - Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Gentzkow, M., Shapiro, J. M. (2010). What drives media slant - Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Fang, Y., Wang, Q., Wang, Y., Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk - Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., Branzoli, N. (2025). Measuring tone shifts in media coverage - An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
van Atteveldt, W., van der Velden, M. A. C. G., Boukes, M. (2021). The validity of sentiment analysis - Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Nyakurukwa, K., Seetharam, Y. (2024). Sentimental showdown: News media vs. social media in stock markets. Heliyon. https://doi.org/10.1016/j.heliyon.2024.e30211
Chuang, H.-M., He, H.-C., Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
