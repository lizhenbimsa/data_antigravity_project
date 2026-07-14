---
family_id: F565
columns:
- tone_daily_media_ctx
- tone_daily_media_full
- tone_daily_media_ss
unit: 语调得分 (连续, 三家 LLM 多数投票量表映射后取值约在 [-1,1]; 银行×年内先按报道过滤再取算术均值)
formula: 'tone_daily_media{track} = mean_{i∈{报道: target_bank=b, year=y, 媒体(中文)∈DAILY, llm_verified_full=True}} llm_vote_score{track}_i; 其中 DAILY 为 attention_media.py 内以 NPPA 出版周期字段判定的“日报”出版物集合 (_is_daily 指示列), track∈{_full,_ctx,_ss} 对应三条文本轨道各自独立聚合的 llm_vote_score{track} 源列'
producer: pipeline\panel\attention_media.py (媒体异质性维度⑧「高频日报 vs 非日报」区块) ; pipeline\panel\export.py (面板列标签映射与导出)
upstream:
- 21_tone_llms.parquet::llm_vote_score_full/_ctx/_ss
- 00_preprocessing 媒体元数据::媒体(中文)
- config 出版周期参照表 (NPPA 日报清单, attention_media.py 内 DAILY 常量)
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
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"银行—年"维度上, 报道该银行且金融科技相关的新闻文章中, 来自高频日报类出版物的子集在情感语调上的均值水平, 是 `pipeline/panel/attention_media.py` 内媒体异质性九维度分解的第⑧维「高频日报 vs 非日报」的核心量。其理论出发点是: 出版频率是媒体信息生产制度结构的一个关键维度——日报因其发行频率高、内容时效性强, 是投资者与研究者在实证文献中构建"日频情感指标"的主要素材来源, 这一构念直接承袭自 Tetlock (2007) 用《华尔街日报》专栏构建的悲观情绪指数, 以及后续 Tetlock, Saar-Tsechansky & Macskassy (2008) 关于日频新闻负面词汇比例可预测企业盈余与股票回报的发现。日报与非日报(周刊、月刊、深度期刊等)在编辑周期、审稿把关、信息新鲜度、记者对突发事件的反应速度上存在系统性差异, 这种差异会进入所报道内容的情感基调, 因此将样本按出版频率二分并分别聚合语调均值, 是检验"媒体制度特征是否驱动情感测度差异"这一更广泛媒体异质性问题的一个具体切片。本家族三列全部落在"日报"这一边(与之互补、镜像的 `tone_nondaily_media{track}` 属另一家族, 二者相减构成 `tone_gap_daily_nondaily{track}` 缺口列, 亦属另一家族), F565 三列本身聚焦"日报子样本的语调水平"这一构念。
【方法学与计算】
计算流程在 `attention_media.py` 内分两步: 第一步是标注, 对面板底层文章级数据 `df` 中的每一行, 依据其"媒体(中文)"字段是否落在预先构造的 `DAILY` 出版物名录中, 生成布尔指示列 `_is_daily`(名录构造原则为出版周期属日报; 该名录来自项目内配置化的媒体出版周期参照, 与本文档同批次 `daily_media_frac` 列共享同一 `_is_daily` 判定, 二者是同一底层标注在"占比"和"语调水平"两个统计量上的不同投影)。第二步是分轨条件聚合: 对 `_full`/`_ctx`/`_ss` 三条文本轨道分别循环, 若该轨道对应的情感源列 `llm_vote_score{track}` 不存在于 `df`(例如某次运行未产出该轨道)则整轨优雅跳过, 存在时先按 `_is_daily == 1` 过滤出日报子样本, 再按 `target_bank`、`year` 分组取 `llm_vote_score{track}` 的算术均值, 得到 `tone_daily_media{track}`, 随后与主面板 `panel` 做左连接合并。`llm_vote_score{track}` 本身是 stage 21 三家 LLM(`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`)多数投票情感的连续打分版本, 其上游行级样本已受 stage 21 留篇门控约束——门控口径为 full-only(2026-06-29 起): 一篇报道是否被判定为"一篇有效的银行金科报道"只看 `llm_verified_full == True`, `_ctx`/`_ss` 两条轨道是 conditional-on-full 的测度轨, 其行宇宙是 full 轨留篇集合的子集, 但各自的 `llm_vote_score{track}` 仍按各自轨道文本独立生成, 因此三条轨道的 `tone_daily_media{track}` 在样本口径上共享同一留篇集合、在情感取值上彼此独立。日报子样本内若某银行—年没有任何一篇日报来源的报道命中留篇门控, 则该格产出缺失值(NaN), 不做跨轨或跨类别插补, 这与 `daily_media_frac`(日报占比, 分母含全部有效报道)在缺失处理上是一致的稀疏保留策略——保证均值只在有真实观测支撑时给出, 而非用 0 冒充"无日报报道且情感中性"。
【文献定位】
三轨设计与情感测度的构念定位对齐项目主线口径: Tetlock (2007, *Journal of Finance*) 是本维度理论上的直接源头, 其核心贡献是证明日频媒体文本情感(悲观指数)对股票市场收益具有可预测性, 从而确立了"高频出版物情感"作为独立于低频/深度报道情感的一类信息载体这一构念合法性, 本家族正是把这一构念在中国银行业新闻语境下具体化为可计算列。Tetlock, Saar-Tsechansky & Macskassy (2008, *Journal of Finance*) 进一步把这一逻辑推进到公司盈余预测层面, 强化了"日频新闻情感"作为独立信息通道而非低频报道简单子集的经验基础。Holzman, Miller & Twedt (2023, *The Accounting Review*) 的媒体权威性加权框架虽然主要服务于本文件同批次的 `_mw` 加权情感列, 但其"媒体来源制度特征系统性影响情感测度"的一般性论点同样支撑了本家族按出版频率切分聚合的正当性——出版频率与媒体权威度是媒体异质性这一大类构念下彼此正交但同源的两个切面。You, Zhang & Zhang (2018, *The Review of Financial Studies*) 关于中国"官媒 vs 市场化媒体"分类的框架(见同批次 `official_media_frac`/`market_media_frac`)与本维度共享同一媒体异质性九维分解体系, 二者在方法论上互为并列而非嵌套。中国情境下媒体情感与银行系统性风险、存款稳定性的实证关联可参见 Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*), 其结论为本家族"日报语调"这一细分测度在中国银行业设定下的经济相关性提供了同域佐证。

## VAR: tone_daily_media_ctx

【变体差分】
本列取自三轨中的 `_ctx` 轨道: 源情感列为 `llm_vote_score_ctx`, 文本输入是"标题+目标银行实体窗口"而非全文正文, 聚合过滤条件(`_is_daily==1`、按 `target_bank`/`year` 分组取均值)与家族其余两列完全一致, 唯一差异落在情感打分所依赖的文本材料范围上。`_ctx` 轨道的行宇宙是 stage 21 full-only 留篇门控下的子集(即只有 `llm_verified_full==True` 的文章才进入分母), 但 `llm_vote_score_ctx` 的取值本身由该轨道自身文本独立生成, 不与 `_full`/`_ss` 共享情感打分结果。与 `tone_daily_media_full` 相比, `_ctx` 版本剔除了正文中与目标银行实体距离较远的段落, 更聚焦于报道对该银行本身的直接措辞, 因此在存在"同篇报道混谈多家机构"或"正文夹带大段背景铺垫"的样本上, `_ctx` 与 `_full` 的语调读数可能产生系统性偏离。按项目铁律, `_ctx` 与 `_full`、`_ss` 三轨各自 just-identified 并排, 互为稳健性检验、不分主次, 严禁将三轨情感列混入同一个 over-identified 的 Hansen J 检验框架中联合识别。在解读上, `_ctx` 版本对理解"高频出版物"这一构念本身具有额外价值: 全文正文中, 日报记者往往需要为读者补充较多背景介绍(如该银行近期业绩、行业地位、监管环境), 这部分背景性文字未必带有明确情感取向, 会在 `_full` 轨道内对真实语调形成稀释效应; `_ctx` 轨道通过收窄到实体窗口, 有助于剥离此类背景稀释, 从而更逼近记者对目标银行本身的直接评价基调。但这种收窄同时带来样本利用效率的取舍——当实体窗口内文本过短或语义不完整时, 情感打分的噪声也可能相应上升, 因此 `_ctx` 与 `_full` 的差异既是构念精度与文本充分性之间的权衡, 也是本家族三轨并排设计所要覆盖的稳健性来源之一, 不应被简化为"哪一轨更准确"的单一排序判断。

## VAR: tone_daily_media_full

【变体差分】
本列取自三轨中的 `_full` 轨道(全文正文+标题), 是家族内唯一直接承接 stage 21 留篇门控主体口径的一列——`llm_verified_full` 判定本身就是在 `_full` 轨道文本上做出的, 因此 `tone_daily_media_full` 的行宇宙定义与门控口径完全同源, 不存在"条件于 full"的从属关系, 而是门控的第一现场。计算上, `llm_vote_score_full` 对每篇通过留篇门控且来源属日报的文章取值, 按银行—年分组求均值。在项目多轨/多模型互为稳健性的通用设计原则下, `_full` 轨道在多数下游 paper(如 P1 `bank_fintech_tone` 的 headline treatment `llm_vote_tone_full`)中被采用为主口径测度对象的输入文本范围, 但这并不意味着 `_full` 在情感测度自身的统计地位上高于 `_ctx`/`_ss`——三轨依旧是并排的稳健性设计, `tone_daily_media_full` 与另两列的关系不构成主检验/稳健性检验的从属结构, 而是三个各自独立可识别的估计。由于 `_full` 轨道的行宇宙与留篇门控本身完全同源, `tone_daily_media_full` 是三列中最贴近"原始报道全文情感"这一朴素直觉的一列, 也是绝大多数下游 paper 在报告 headline 结果时默认引用的文本范围对象。但需要强调, 这种"被更多下游 paper 采用"的应用惯例是历史命名与既有 paper spec 选择的结果, 不构成该列在情感测度自身统计地位上高于 `_ctx`/`_ss` 的理由; 三轨在本家族内部仍是并排的、互不隶属的估计量, 任何跨轨比较都应作为稳健性叙事而非主检验/附属检验的层级关系呈现, 报告结果时应同时列出三轨读数并说明其各自基于的文本范围差异, 以避免读者误以为 `_full` 是"更正确"的语调水平。

## VAR: tone_daily_media_ss

【变体差分】
本列取自三轨中的 `_ss` 轨道: 源情感列为 `llm_vote_score_ss`, 文本输入是"标题+目标银行与金融科技词汇同句(±N 句窗口, 默认 N=1)共现"的片段。`_ss` 轨道的回退语义镜像 `_ctx`: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文正文(与 `_ctx` 找不到实体窗口时的回退行为对称), 并置位 `ss_is_fallback=True`, 分母 `n_articles` 与 `_ctx` 共享同一套稀疏性会计处理, 不因回退触发而产生虚假的完整覆盖率假象。`tone_daily_media_ss` 因此度量的是"日报来源中, 银行与金科议题在同一句话内被并列提及(或退化为全文兜底)时"的情感语调均值, 相比 `_ctx` 的实体窗口范围更窄、判据更严格(裸 AC 自动机命中金科词, 银行侧叠加否定词与短名过滤), 是三轨中对"银行—金科关联情感"这一构念界定最紧的一支。与 `_full`/`_ctx` 一样, `_ss` 的样本行宇宙仍受 full-only 留篇门控约束(`llm_verified_full==True` 是进入 `_is_daily` 分组求均值前的先决条件), 但情感打分结果由 `_ss` 轨道文本独立产生, 与另两轨并排、互为稳健性, 不共享同一识别方程。`_ss` 的判据不对称口径值得单独说明: 银行侧命中采用否定词过滤加短名过滤的双重把关(避免"某某银行"这类通用短称在无关语境下误触发), 而金科侧命中采用裸 AC 自动机对 1506 词金科词表的直接匹配, 不做否定或短名过滤; 这一不对称设计是全项目三轨架构下 `_ctx`/`_ss` 共用的判据约定, 并非本家族独有。当 `FINTECH_AC` 词典对象在某次运行中为 None 时, `*_is_fallback` 会整体退化为 True, `tone_daily_media_ss` 在该次运行下实质上退化为"日报子样本内 `_full` 口径的语调均值", 这一优雅降级行为应视为数据可用性约束下的预期结果, 而非计算逻辑缺陷。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->
