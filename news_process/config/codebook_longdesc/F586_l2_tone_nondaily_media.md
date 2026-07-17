---
family_id: F586
columns:
- tone_nondaily_media_ctx
- tone_nondaily_media_full
- tone_nondaily_media_ss
unit: 语调得分 (连续, 理论区间约 [-1,1]; 银行-年 bank-year 均值聚合)
formula: tone_nondaily_media{track} = mean(llm_vote_score{track}) over rows where target_bank×year 且 媒体(中文) ∉ DAILY (高频日报出版物清单); track ∈ {_full, _ctx, _ss}
producer: pipeline\panel\attention_media.py (维度⑧ 出版频率异质性构造块; 常量名列于 pipeline\panel\export.py 的列标签映射表)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track} 三家 LLM 多数投票语调分)
- 原始文章元数据列 媒体(中文) (出版物中文名)
- config/media_classification.json::high_frequency_dailies (高频日报出版物白名单, 运行时由 attention_media.py 加载为集合变量 DAILY, 并非硬编码在 .py 文件内的常量)
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: "98"
  issue: "7"
  pages_or_artno: "315-345"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: "91"
  pages_or_artno: "1150-1172"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行-年报道语调在"出版频率"这一媒体属性维度上的异质性: 把落在目标银行×年单元内的全部涉该行报道, 按报道来源出版物是否属于高频日报 (daily newspaper) 一分为二, 本家族三列取的是"非日报" (nondaily) 子集上的语调均值。构念动机直接承袭 Tetlock (2007) 的经典设定——该文即以《华尔街日报》"Abreast of the Market" 专栏这一高频日报专栏为标的构造悲观指数, 证明日频媒体因发稿密度高、追踪即时事件能力强, 其语调对市场回报的短期预测力与低频出版物存在系统性差异, 这一"高频出版物语调具有独特定价信息含量"的先验是本家族构造 daily/nondaily 二分的直接理论出发点。本项目把这一"出版频率梯度"思想搬到中国银行-金科报道场景: 高频日报因追热点、抢时效, 在语调生成机制上更贴近"新闻噪声"或"注意力驱动"叙事, 而周刊、月刊等非日报出版物(含深度财经期刊、行业专刊)在同一构念光谱的另一端, 通常发稿周期更长、编辑把关更审慎, 语调更可能反映积累性、深加工的判断而非即时情绪波动。日报白名单是一份出版物中文名单, 记录在 config 目录下 media_classification.json 配置文件的高频日报键位下(依据 NPPA 出版周期登记为"日报"的媒体), attention_media.py 在运行时读取该 JSON 文件并把该名单实例化为集合变量, 供逐篇报道按出版物中文名字段与该清单做集合成员判定, 打出是否日报的 0/1 标记; 本家族三列即取非日报子样本、按目标银行与年份分组对对应文本轨道的三家 LLM 多数投票语调分取均值。该指标与"日报语调"家族互为镜像分区(日报/非日报二分穷尽全部报道), 二者之差是配套的语调缺口列(不在本家族), 用于直接检验"高频出版是否系统性拉高/拉低银行报道语调"这一假设。
【方法学与计算】
上游语调来源是 stage 21 三家大模型(gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash)多数投票产生的语调分, 三家均对同一篇报道文本独立打分, 投票整合后得到该篇报道在给定文本轨道下的语调分(约落在负一到正一区间, 负面-正面连续刻度)。本家族的构造步骤是: 先在文章级数据表上依据出版物中文名字段是否命中日报白名单打上是否日报的0/1标签(与文本轨道无关, 是媒体元数据属性, 全轨道共享同一份划分); 随后对每个文本轨道分别取非日报的子集, 按目标银行与年份分组、对该轨道的语调分求算术均值, 得到本家族对应列; 最后以目标银行与年份左连接合并回主面板, 单元内若该轨道该分类下无一篇有效报道则该格为缺失, 不做零填充或跨轨道借补。三轨口径完全独立并排构造(各自的分组求均值管线互不借用彼此的行), 不存在"以全文轨补实体窗口轨/同句轨缺失"的隐式回退——这是本项目全局铁律的一处具体落地: 全文/实体窗口/同句三条文本轨道各自 just-identified, 互为稳健性、不分主次, 严禁在同一 over-identified 设定(如同一个 Hansen J 检验)里把三轨语调混进同一组矩条件。需注意"非日报"划分本身是与轨道无关的媒体元数据判定(只依赖出版物名称, 与文本抽取轨道无关), 但三个本家族列各自使用对应轨道的语调分打分, 因此三列的差异只来自情感打分所依据的文本片段不同, 而不是样本划分逻辑不同。样本口径与 stage 21 留篇门控保持一致: 面板中出现的行已限定在全文轨验证通过的留篇集合(2026-06-29 起的 full-only 门控), 实体窗口轨与同句轨的语调计算是在这一全文轨留篇行宇宙的子集上进行的条件测度, 而非独立样本; 报道篇数口径分母亦随之收缩, 三轨语调均值的样本量含义因此有别于换轨前的历史口径。
【文献定位】
频率异质性这条线在文本情感金融文献里有两条并行脉络: 一是 Tetlock (2007, *Journal of Finance*) 开创的日频媒体语调—回报可预测性范式, 以高频日报专栏语调证明其对市场回报具有独特的短期定价信息含量, 本家族的 daily/nondaily 二分正是对该先验的直接操作化。二是媒体权威性/风格异质性文献: You, Zhang & Zhang (2018, *Review of Financial Studies*) 在中国资本市场语境下区分了不同媒体来源"谁真正掌握了笔杆子的权力", 揭示媒体属性(包括发稿频率、官方/市场化背景)系统性影响报道语调的信息含量与市场反应; Holzman, Miller & Twedt (2023, *The Accounting Review*) 提出以媒体权威性对语调加权可以更精细地捕捉盈余公告场景下媒体情感的纪律约束作用, 为本项目同一家族体系内的媒体权威性加权语调列族提供了方法学锚点, 也从侧面印证发稿频率、来源属性等媒体元数据在语调测度中不能被当作噪声一概而论、而应显式分层建模。就中国银行业设定而言, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 在银行系统性风险与存款稳定性研究中同样采用媒体情感作为解释变量, 为本家族在银行-年面板上的应用场景提供了直接的同域参照。本家族三列构成一组互为稳健性并排指标, 供研究者在"高频出版物语调是否更贴近短期市场噪声、非日报语调是否更贴近深加工判断"的机制检验中, 与家族 daily_media 及 gap 列联合使用, 但三条文本轨道之间以及日报/非日报两个媒体子样本之间均不应被合并进同一识别方程的单一矩条件。

## VAR: tone_nondaily_media_ctx

【变体差分】
本列取文本轨道 ctx (标题+银行/金科实体窗口)作为语调打分依据的文本片段: 上游语调分是三家 LLM 在"标题 + 目标实体上下文窗口"文本(由 stage 14 实体窗口物化步骤生成, 采用标题前置拼接方式)上独立打分、多数投票整合后的语调分。本列与 canonical 家族口径的区别只在于打分所依据的文本片段范围更窄、更聚焦于银行/金科实体周边语境, 相对全文轨剔除了与目标实体距离较远的正文段落, 因而对"文章整体基调被无关段落稀释"的问题更不敏感, 但也更依赖实体窗口抽取的准确性。样本行宇宙上, ctx 轨道语调是在全文轨留篇门控确定的行子集上计算的条件测度, 分组求均值管线(按目标银行与年份分组、且限定非日报子样本)与全文轨、同句轨两轨完全并排独立执行, 互不借补缺失; 三轨在下游回归/检验中须各自 just-identified 使用, 不得混入同一 over-identified Hansen J 设定。若某银行-年单元下 ctx 轨道缺少可用的实体窗口抽取(如整批回退到全文)、或该单元下非日报报道为零篇, 则本列在该格取缺失值, 与全文轨、同句轨两列相互独立地各自缺失, 不做跨轨补值。使用场景上, ctx 轨道适合作为全文轨估计的一条并排稳健性检验: 当研究者担心全文正文中大量与目标银行无直接关联的段落(例如宏观经济评述、行业整体走势介绍)会把语调均值向中性拉平、从而低估银行特定语调信号时, ctx 轨道通过收窄到实体窗口来提纯这一信号; 但同时也应留意, 实体窗口抽取本身依赖上游命名实体识别与窗口半径参数, 窗口过窄可能反而丢失必要的语境线索(如否定词、转折句跨窗口分布), 因而 ctx 与全文两条轨道的估计差异既可能来自"提纯效应"也可能来自"窗口截断噪声", 需结合全文轨、同句轨两轨的估计方向和显著性联合判读, 不宜单独依赖 ctx 轨道下结论。

## VAR: tone_nondaily_media_full

【变体差分】
本列取文本轨道 full (标题+完整正文)作为语调打分依据: 上游语调分是三家 LLM 在标题加全文文本上独立打分、多数投票整合后的语调分, 是本家族体系里样本量最大、覆盖文本信息最完整的轨道, 也是 stage 21 留篇门控所依据的主轨道——即"一篇报道是否被判定为一篇有效的银行金科报道"这一留篇决策本身就锚定在 full 轨道上, ctx、ss 两轨的语调计算行宇宙都是 full 轨留篇集合的子集。本列与 ctx、ss 两列的区别在于: 语调打分基于全文而非实体窗口或同句片段, 因而对文章通篇的整体论调更敏感, 但也更容易被与目标银行关系松散的段落(如行业综述性内容)稀释影响。分组求均值管线独立执行, 按目标银行与年份分组、对非日报子集的语调分取均值, 与 ctx、ss 两轨互不借补; 三轨并排、互为稳健性, 不得混入同一 over-identified Hansen J。若某银行-年单元下非日报子样本为零篇, 该格取缺失值。作为三轨中样本覆盖最完整、也是留篇门控本身依据的轨道, 本列在实践中通常是研究者报告的首选口径(与本项目其余各轨、各梯子命名惯例一致, 无后缀等价物承担事实上的默认参照角色), 但这并不意味着 full 轨道在识别策略上优先于 ctx、ss——三者在方法论上仍是并排的、互为稳健性的独立测度, 选择哪一轨作为正文报告口径是研究设计层面的取舍, 而非统计效力层面的高低之分。

## VAR: tone_nondaily_media_ss

【变体差分】
本列取文本轨道 ss (标题+银行∧金科同句±N窗, 窗口半径参数配置于筛选配置文件的上下文窗口小节, 默认半径为1句)作为语调打分依据: 上游语调分是三家 LLM 在"标题 + 银行与金科关键词同句共现窗口"文本上独立打分、多数投票整合后的语调分, 是三轨中文本片段最窄、判定最严格的一支, 要求银行实体与金科词汇在同一句(或正负一句半径内)出现才纳入抽取窗口。回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, 该轨文本回退为全文正文、回退标记置为真, 与 ctx 轨道共享同一套报道篇数分母口径, 保证优雅降级而非静默丢行; 若上游金科词典自动机为空, 则各轨回退标记全部置真, 三轨同步优雅降级。本列与 full、ctx 两列的区别在于文本抽取判据更严格——ss 轨道要求"同句"而非"实体窗口", 理论上对"银行与金科议题真正共同出现在同一叙述单元"的语调有更纯粹的刻画, 但样本覆盖度通常低于 ctx。分组求均值管线独立执行, 按目标银行与年份分组、对非日报子集的语调分取均值, 与 full、ctx 两轨互不借补、各自 just-identified; 三轨互为稳健性并排使用, 严禁混入同一 over-identified Hansen J。若某银行-年单元下非日报子样本为零篇, 该格取缺失值。由于 ss 轨道判据最严格, 其非回退样本量往往显著小于 ctx、full, 在银行-年单元层面容易出现小样本波动甚至因回退比例过高而导致该单元统计功效不足; 因此 ss 轨道更适合定位为"高置信度子样本上的精细化稳健性检验", 用于验证 full、ctx 两轨发现的语调模式在最严格的共现判据下是否依然成立, 而非作为独立的主报告口径。研究者在解读三轨差异时应同时核对各自的回退比例与有效样本量, 避免把回退样本占比过高导致的估计不稳定误读为构念本身的差异。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
