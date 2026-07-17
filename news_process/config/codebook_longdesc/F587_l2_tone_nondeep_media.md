---
family_id: F587
columns:
- tone_nondeep_media_ctx
- tone_nondeep_media_full
- tone_nondeep_media_ss
unit: 语调得分 (连续, 约 [-1,1]; LLM 三家投票逐篇打分 llm_vote_score{track} 在 bank-year 单元内对非深度期刊子样本取算术均值)
formula: 'tone_nondeep_media{track} = mean(llm_vote_score{track} | target_bank, year, _is_deepdive==0), 其中 _is_deepdive = 1{媒体(中文) ∈ DEEPDIVE 深度期刊名单} (attention_media.py); {track} ∈ {_full, _ctx, _ss}, 三轨各自独立求均值; 与 tone_deepdive_media{track} 互补构成 tone_gap_deepdive_nondeep{track} = tone_deepdive_media{track} - tone_nondeep_media{track}'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms
- 14_materialize_ctx
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., Shapiro, J. M.
  year: 2010
  title: What Drives Media Slant? Evidence from U.S. Daily Newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., Yuan, Y.
  year: 2024
  title: 'Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., Branzoli, N.
  year: 2025
  title: 'Measuring Tone Shifts in Media Coverage: An Empirical Application to Bank Financing Conditions in Italy'
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
tone_nondeep_media 家族刻画"非深度期刊"渠道对目标银行报道的平均语调, 是媒体异质性 (media heterogeneity) 拆解体系中"出版频率/深度"维度的补集测度, 与其互补量 tone_deepdive_media 共同构成 tone_gap_deepdive_nondeep 缺口指标。构念动机源自媒体信息中介功能的分层假说: 低频、深度分析型出版物 (如行业周刊、专题期刊) 因编辑资源投入更高, 倾向于产出原创性分析而非简单转载, 其语调更可能反映记者独立判断; 高频、日报/快讯型渠道 (即本家族覆盖的"非深度"集合) 更依赖官方通稿转载与即时报道, 语调更贴近事件本身的即时基调, 波动性与事件驱动性更强。You, Zhang & Zhang (2018, RFS) 在"谁掌握了笔杆子"研究中区分了媒体在信息生产链条中的不同角色 (记者原创 vs. 编辑转载 vs. 官方通稿), 为按出版类型拆分语调测度提供了理论依据; Gentzkow & Shapiro (2010, Econometrica) 进一步证明媒体机构存在稳定的报道倾向性 (outlet-level slant), 支持将出版物按可观察属性 (如出版频率) 分组后分别聚合语调的做法, 而非笼统合并全部渠道。
本家族在系统内属于 attention_media.py 媒体异质性拆解模块的第⑦维度产出。该模块沿多个正交维度 (官方/市场化、财经/综合、集中/离散、深度/非深度、日报/非日报) 对同一批银行相关报道做子样本切分, 每个维度各自独立计算语调均值与缺口, 彼此不构成嵌套或互斥的单一分类体系, 而是多把互补的"透镜", 供研究者按不同理论视角检验媒体属性对语调水平及其与企业结果关联性的调节作用。tone_nondeep_media 对应"深度分析强度"这把透镜的补集端。

【方法学与计算】
计算入口是 attention_media.py 中标注为"维度⑦: 深度期刊 vs 非深度"的代码块。首先基于媒体名录 DEEPDIVE (来源 NPPA 出版周期分类, 出版周期为周报及以上的非日刊出版物归入深度期刊集合) 对每篇报道的"媒体(中文)"字段做成员关系判定, 生成二元指示列 _is_deepdive; 未落入该名录的报道即视为非深度媒体来源, 构成本家族的样本子集。随后按 (target_bank, year) 分组, 在 _is_deepdive==0 的子样本内对逐篇文章的 LLM 三家投票语调分 (llm_vote_score{track}, 三家 gpt54nano/gemini31/deepseekv4 多数共识经 tone_llms.py 产出的 headline 语调) 取算术均值, 得到 tone_nondeep_media{track}。三轨 (full/ctx/ss) 分别独立执行同一聚合逻辑, 源列 llm_vote_score{track} 若在上游 df 中缺失 (如某轨未跑或列被裁剪) 则整轨优雅跳过, 不产生该轨列, 亦不借用其他轨道数据填补。
与 tone_deepdive_media{track} (_is_deepdive==1 子样本均值) 相减构成 tone_gap_deepdive_nondeep{track}, 该缺口列不在本家族内 (属独立家族), 但其计算依赖本家族列作为减数, 理解本家族数值时应注意其"被减项"身份。留篇门控口径与主线一致: 分子分母均限定在 llm_verified_full==True 的留篇集合上 (2026-06-29 起 full-only 门控), ctx/ss 轨的样本行集合是 full 留篇集合的子集经该轨自身条件 (如 ss 轨要求银行∧金科同句共现或回退全文) 过滤后的结果, 而非独立留篇标准; ss 轨若某篇文章无银行∧金科同句共现, content_ss 回退为全文 body 且 ss_is_fallback 置 True, 语调仍照常计入 (镜像 ctx 回退语义, 与三轨文本物化的通用回退规则一致)。三轨在本家族内各自 just-identified 并排, 互为稳健性、不分主次, 不应混入同一 over-identified Hansen J 设定中联合使用。
数值上, tone_nondeep_media{track} 与其对应轨道的整体银行-年语调均值 (未做媒体类型拆分的 llm_vote_tone{track}) 高度相关但不恒等, 因为非深度媒体样本通常在报道条数上占绝大多数 (日报/快讯类渠道产量远高于深度期刊), 故该指标常与未拆分整体语调数值接近; 差异主要体现在深度期刊报道条数较多、且其语调与非深度报道系统性偏离的银行-年单元。某 (bank, year) 单元若全部报道均来自非深度媒体, 则 tone_deepdive_media{track} 为 NaN 而 tone_nondeep_media{track} 等于该单元整体语调均值; 反之若全部报道均来自深度期刊, 则本列为 NaN。

【文献定位】
本家族的方法学谱系有三条主线交汇。其一是媒体作为信息中介的定价效应文献, 由 Tetlock (2007, JF) 开创: 基于道琼斯专栏文本构建悲观情绪指数, 证明媒体语调可预测短期市场回报及后续均值回复, 确立了"报道文本语调是可计量且具有经济意义的状态变量"这一基础命题; 本指标沿用其"文本语调→资本市场后果"的核心逻辑, 但将测度主体从单一渠道扩展为按出版属性分组的银行-年面板。其二是媒体机构异质性文献, Gentzkow & Shapiro (2010, Econometrica) 证明媒体报道倾向存在稳定的机构/风格固定效应而非随机噪声, 为按出版物属性 (而非逐篇随机抽样) 分组聚合语调提供了识别上的正当性 — 若各渠道语调纯属随机噪声, 按出版频率拆分将不具有额外信息; You, Zhang & Zhang (2018, RFS) 在中国资本市场情境下进一步验证了媒体角色分层 (记者/编辑/官方) 对语调信息含量的调节作用, 是本模块"官方/市场化"及"深度/非深度"两条拆解维度共同的直接理论来源。其三是中国银行业媒体情感的应用文献, Fang, Wang, Wang & Yuan (2024, IREF) 在中国银行系统性风险背景下构建媒体情感指标并检验其对存款稳定性的影响, 是与本项目同一研究对象 (中国银行业) 及同一测度类型 (银行-年媒体语调) 最直接的比较基准; Marchetti, Tarducci & Branzoli (2025, SSRN) 提出银行融资条件语境下的语调聚合口径, 为按出版属性拆分后再聚合到银行-年单元的操作化路径提供了方法参照。Holzman, Miller & Twedt (2023, TAR) 的媒体权威加权语调框架进一步说明: 不同渠道的语调不应无差别等权合并, 渠道属性 (权威性、深度、出版频率) 本身携带对语调信息含量的调节信息, 这正是本家族及整个媒体异质性拆解模块存在的方法论正当性。需说明的是, 源码 attention_media.py 中标注该维度⑦代码块的注释另行援引了 Bushee, Core, Guay & Hamm (2010, JAR) 及 Guest (2021, JAR) 关于媒体原创信息生产与转载差异对治理效力调节作用的发现, 作为深度期刊 vs. 非深度划分的直接理论出处; 二者不在本家族当前引文池白名单内, 故本段未展开引注, 仅在此注明源码另有该独立理论依据, 待后续补编纳入引文池后再行合并引注。

## VAR: tone_nondeep_media_full

【变体差分】
full 轨: 语调源列为 llm_vote_score_full, 该分是 LLM 三家投票对"标题+全文正文"文本 (content_full, 无实体窗口截断) 的多数共识语调分。full 轨是留篇门控的唯一判定轨 (llm_verified_full==True 决定一篇文章是否计入"银行金科报道"样本), 因此本列的 (target_bank, year) 行覆盖范围即为该单元下 full 轨留篇集合中非深度媒体报道的子集, 是三轨中样本行数最多、覆盖最完整的一支, 也是各 paper 主轨 treatment (如 P1 llm_vote_tone_full) 采用的口径基准。作为家族 canonical 轨道, 本列反映"不做任何实体窗口截断"情形下非深度媒体子样本的平均语调水平, 波动性主要来自日报/快讯类渠道对突发事件的即时反应, 相对深度期刊子样本 (tone_deepdive_media_full) 更贴近舆情脉冲而非深度评论基调。
由于 full 轨承担着上游留篇门控的判定职能, 本列在实证使用上具有一层额外含义: 它不仅是"该分组下语调均值"的测量结果, 同时其所依赖的样本行集合本身即是研究设计中"哪些报道被认定为与目标银行金科议题相关"的判定结果。这意味着 tone_nondeep_media_full 与 n_articles、fintech_share 等留篇口径敏感的分母类变量共享同一批底层留篇标记, 在做面板回归时应注意分母行集合口径的一致性, 避免将 full 轨语调均值与 ctx/ss 轨的分母混用导致口径不一致的伪回归结果。与整体 (未拆分媒体类型) 的语调均值相比, 本列的样本方差通常更小, 因为非深度媒体子样本报道条数占比高, 极端值被更大样本量平滑; 但在报道条数本就稀少的银行-年单元 (如新设银行或报道覆盖不足的小型城商行), 该均值仍可能因样本量小而对个别篇目语调敏感, 使用时应结合对应的报道条数辅助列判断统计意义。

## VAR: tone_nondeep_media_ctx

【变体差分】
ctx 轨: 语调源列为 llm_vote_score_ctx, 对应"标题+实体窗口"截断文本 (content_ctx, 围绕目标银行实体提取的局部上下文) 的 LLM 语调分。样本行集合是 full 留篇集合的子集 (conditional-on-full 稳健性轨), 若某篇报道在 ctx 窗口截断后不含足够上下文或该轨整体缺失, 对应 (target_bank, year, nondeep) 单元的贡献相应减少甚至该单元本列整体为 NaN。ctx 轨与 full 轨互为稳健性、不分主次, 二者并排使用可检验"聚焦银行实体局部上下文是否改变非深度媒体子样本的语调水平"这一测量维度效应, 而非替代关系; 二者禁混入同一 over-identified 识别设定。相对 full 轨, ctx 轨剔除了报道正文中与目标银行实体无关的段落, 理论上更精准地隔离"针对该银行"的语调, 但同时也放大了截断误差对非深度媒体 (通常篇幅短、信息密度高) 子样本的敏感度。
非深度媒体 (日报、快讯类) 报道往往篇幅短小、行文紧凑, 目标银行实体常在标题及导语句即已出现, 故 ctx 窗口截断相对深度期刊长文而言信息损失比例通常更低, 这使得 tone_nondeep_media_ctx 与 tone_nondeep_media_full 的数值相关性一般高于对应的 tone_deepdive_media_ctx 与其 full 轨之间的相关性。但当非深度媒体报道以联合报道形式同时提及多家银行时 (如监管政策通稿一次性点名多家机构), ctx 窗口截断会剔除针对其他银行的段落, 此时 ctx 轨语调可能与 full 轨出现有意义的偏离, 该偏离本身即是媒体报道"泛化 vs. 聚焦"程度的间接信号, 是本列相对 full 轨的独特信息增量所在。研究者在解读 ctx-full 缺口时应结合是否为联合报道类稿件 (如政策通稿、行业排名) 加以区分, 避免将截断噪声误读为语调结构性差异。

## VAR: tone_nondeep_media_ss

【变体差分】
ss 轨: 语调源列为 llm_vote_score_ss, 对应"标题+银行∧金科同句(±N 句窗口, 默认 N=1)"文本 (content_ss) 的 LLM 语调分, 判定原语与 stage 13 共现硬过滤的邻近共现口径不同 (ss 轨要求严格同句共现, 详见 entity_context.py extract_bank_fintech_cooccurrence)。若某篇报道不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback 置 True (镜像 ctx 轨回退语义), 该篇仍计入非深度媒体子样本的语调均值计算, 不因回退而被剔除, 分母 (n_articles) 与回退前口径共享。ss 轨样本行集合同样是 full 留篇集合的条件子集, 与 full、ctx 两轨各自 just-identified 并排、互为稳健性, 三轨联合使用时严禁混入同一 Hansen J 过识别设定。相对 full/ctx 两轨, ss 轨在非回退情形下将语调判定文本进一步收窄至银行与金科议题真正同句出现的语境, 是三轨中构念上最严格 (对"银行-金科议题相关性"要求最高) 但样本覆盖率通常最低的一支, 适合作为对"报道是否真正在同一句话中谈及银行与金科"这一构念敏感性最强的稳健性检验轨道。
在非深度媒体子样本内, 银行∧金科同句共现的发生率与深度期刊子样本相比通常更低: 日报、快讯类报道常以事件本身 (如监管处罚、人事变动、存款利率调整) 为主线, 金科议题多作为背景信息置于不同段落而非同句提及, 因此 tone_nondeep_media_ss 的回退比例 (ss_is_fallback==True 的篇目占比) 在非深度子样本中往往高于深度期刊子样本, 该差异本身反映了两类渠道在"银行-金科议题耦合紧密度"上的系统性区别。当回退比例较高时, tone_nondeep_media_ss 在数值上趋近于 tone_nondeep_media_full (因回退篇目直接沿用全文语调), 此时 ss 轨相对 full 轨的边际信息量主要由未回退的少数篇目贡献; 研究者在解读 ss 轨与 full 轨差异时, 建议结合该单元回退比例辅助判断差异的可信度与信息含量, 回退比例过高的单元不宜过度解读 ss-full 缺口的构念意涵。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gentzkow, M., Shapiro, J. M. (2010). What Drives Media Slant? Evidence from U.S. Daily Newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
You, J., Zhang, B., Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Holzman, E. R., Miller, B. P., Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., Branzoli, N. (2025). Measuring Tone Shifts in Media Coverage: An Empirical Application to Bank Financing Conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
<!-- rendered-citations:end -->
