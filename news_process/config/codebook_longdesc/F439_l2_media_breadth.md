---
family_id: F439
columns:
- media_breadth
- media_breadth_z
unit: 无量纲得分 (对数变换后的媒体来源计数; z 版为年度截面标准化分数, 年内均值0标准差1)
formula: 'media_breadth = ln(1 + distinct_outlet_count); distinct_outlet_count 为该 bank-year 单元内涉及目标银行的报道去重来源媒体数 (以来源媒体名称字段计数, 非篇数); media_breadth_z 为 media_breadth 按 year 分组、逐年度截面做标准化 z = (x - mean_year(x)) / sd_year(x) 后的分数 (Fama-MacBeth 1973 年度截面标准化范式, 每年内部单独求 mu/sigma, 非跨全部年份一次性汇总), 要求 n_articles>0 且年内有效观测 >=3, 否则该格 NaN'
producer: pipeline\panel\encode.py::aggregate_panel (步骤5 Bank-Year 聚合, 产出 media_breadth 原始列); pipeline\panel\geography.py::standardize_panel_variables (步骤 7b "年度截面标准化", 产出 media_breadth_z, 对 _STANDARDIZE_SCALAR 白名单列逐年度 groupby('year') 分别求 mu/sigma 标准化); pipeline\falsification\controls.py (伪造检验对照变量族与 media_breadth 共享方法论出处, 非本列直接产出方)
upstream:
- 11_news_bank.parquet
- 12_fintech_news_full.parquet
- 40_article_bank_level.parquet
citations:
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media coverage and the cross-section of stock returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving content to investor sentiment; The role of media in the stock market
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The information role of the media in earnings news
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What drives media slant? Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: "10.1016/j.irfa.2024.103140"
  title: "Media opinion divergence and stock returns: Evidence from China"
  authors: "Zhang, Z., Goodell, J. W., Shen, D., & Lahmar, O."
  year: 2024
  venue: "International Review of Financial Analysis"
  type: "journal"
- doi: "10.1111/ajps.12752"
  title: "Banklash: How Media Coverage of Bank Scandals Moves Mass Preferences on Financial Regulation"
  authors: "Culpepper, P. D., Jung, J.-H., & Lee, T."
  year: 2023
  venue: "American Journal of Political Science"
  type: "journal"
- doi: "10.1287/mnsc.2024.05701"
  type: "journal"
  authors: "Lu, S."
  year: 2026
  title: "Green Bonds: Reputational Bonding via Media Coverage"
  venue: "Management Science"
  vol: "72"
  issue: "6"
  pages_or_artno: "5171-5192"
- doi: "10.1287/mnsc.2021.02218"
  type: "journal"
  authors: "Dechow, P., Lawrence, A., Luo, M., & Stamenov, V."
  year: 2024
  title: "Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics"
  venue: "Management Science"
  vol: "70"
  issue: "8"
  pages_or_artno: "5157-5186"
new_dois:
  - "10.1016/j.irfa.2024.103140"
  - "10.1111/ajps.12752"
---

## CORE

【构念与来源】
media_breadth 度量的是一个 bank-year 单元在其新闻报道所处的"信息环境宽度", 落地口径为该单元内涉及目标银行的全部报道所来自的不同媒体来源家数, 取对数变换 ln(1 + distinct_outlet_count) 后作为面板列。这是一个 volume/breadth 维度的度量, 与 tone (语调) 或 substance (实质内容) 维度是正交概念: 同样一篇正面或负面的报道, 若来自五家不同媒体各报道一次, 与来自同一家媒体连续报道五次, 在 tone 均值上可能完全相同, 但在信息扩散广度上截然不同。media_breadth 正是为了捕捉这一"来源多样性"而非"数量"或"语调"的独立信号。构念渊源可追溯到财经媒体作为信息中介 (information intermediary) 这一研究脉络: 不同媒体机构各有独立的采编渠道、审稿标准与受众群体, 报道来源越分散, 意味着某一事件或某银行的信息越可能突破单一媒体的把关 (gatekeeping) 与潜在偏见 (slant), 抵达更广泛的投资者与公众认知。Gentzkow & Shapiro (2010, Econometrica) 关于媒体倾向性 (media slant) 的经典发现进一步说明, 单一媒体来源的报道天然带有该媒体的风格与立场固定性 (house style), 因此以"来源数"而非"篇数"作为独立的信息环境刻画维度, 能够部分剥离单一媒体固定效应对面板结果的污染, 是对纯粹计数类指标 (如 n_articles) 的必要补充。

本指标的直接方法论定位借鉴自 Fang & Peress (2009, JF) 关于媒体覆盖 (media coverage) 与股票截面收益关系的研究框架——该文将"媒体覆盖广度"作为一种信息可得性 (information availability) 的代理变量, 论证了媒体覆盖的广度差异本身即可解释横截面上收益率的系统性差异, 与报道本身的情感倾向无关。落到本项目语境, media_breadth 与核心的 fintech tone 测度 (llm_vote_tone_full 等) 服务于完全不同的识别目的: tone 测度捕捉"银行金融科技相关报道说了什么" (语义/情感内容), media_breadth 捕捉"这件事被多少家独立信息渠道关注" (关注度的结构广度)。二者在伪造检验 (falsification test, 见 `pipeline/falsification/controls.py`) 框架中扮演互补角色——该脚本依据 Hassan et al. (2019, QJE) 的伪造检验范式, 构造一组 non-fintech (对照组) 变量来检验核心 fintech tone 指标是否具有超越"一般媒体关注度"的增量解释力; media_breadth 正是这一对照逻辑所依赖的"一般媒体关注度"维度的具体化之一 (源码注释中标注为 nf_media_breadth 一族的方法论出处), 用以排除"结果仅仅反映了银行整体曝光度上升"这一竞争性解释, 而非金融科技报道本身的语调/实质内容驱动了下游经济后果。

【方法学与计算】
计算路径起点是文章级去重来源标注: 每篇报道在预处理阶段带有来源媒体标识字段, 在 stage 40 面板聚合阶段 (`pipeline/panel/encode.py::aggregate_panel`, 步骤5 "Bank-Year 聚合", 遵循 Tetlock et al. 先分组后合并的范式) 按 (target_bank, year) 分组后, 对组内全部报道的来源媒体做去重计数, 得到 distinct_outlet_count。为压缩长尾分布并稳定回归中的异方差性 (来源数分布通常右偏, 少数银行-年份单元来源极多), 对计数做对数平滑变换 ln(1 + distinct_outlet_count) (加一是标准的处理零值/极小值惯例, 使 0 家来源映射为 0 而非未定义), 得到 media_breadth。media_breadth_z 并非在 media_breadth 之上对全样本 (跨全部年份汇总的) bank-year 单元池做一次性标准化, 而是在下游 `pipeline/panel/geography.py::standardize_panel_variables` (步骤 7b "年度截面标准化", Fama & MacBeth 1973 年度截面范式) 中, 按 year 分组、逐年度截面分别计算 mu/sigma 后标准化, z = (x − mean_year(x)) / sd_year(x); 计算前提是 n_articles>0 且该年度截面内有效观测数 ≥3 (否则整格 NaN), 换言之每一年份内部单独归一至 μ=0/σ=1, 而非跨全部年份混合求一个整体均值/标准差。标准化的目的是使核心回归变量的系数可直接解读为"1σ 年度截面变化对应 β 个单位的因变量变动" (Fama-MacBeth 两阶段回归对截面可比性的要求), 尤其在需要将 media_breadth 作为协变量并入包含其他年度截面 z-score 化控制变量的回归设定中时, 该做法使跨变量系数量纲对齐; 而 media_breadth 本身 (对数原始尺度) 保留了更直接可解释的"报道来源数量级"含义, 二者互补而非互斥, 应用场景不同: 描述性统计/直接解读用 media_breadth, 跨变量系数比较/联合回归用 media_breadth_z。

需要明确的边界: media_breadth 是 track-agnostic (轨道无关) 的元数据类度量——它统计的是"多少家媒体报道过", 与该报道被归入 full/ctx/ss 哪条文本轨道、或该篇文章的情感/语调判定无关, 因此不适用于三轨 (full/ctx/ss) 并排稳健性框架, 也不产生 co-primary 嵌入双轨 (canonical Qwen / `_lg` OpenAI) 变体。这与项目中"三轨/双轨嵌入/梯子测度各自 just-identified 并排、互为稳健性不分主次、禁止混入同一 over-identified Hansen J"的铁律并不冲突——该铁律约束的是同一构念的多种可替代测量方式 (如同一篇文章在不同文本窗口下的情感判定), 而 media_breadth 是唯一确定的来源计数聚合, 不存在平行轨道版本, 因此本家族不涉及三轨/双轨/梯子选择问题, 亦不受 stage 21 留篇门控 full-only 口径的直接约束 (来源计数在 stage 40 聚合阶段基于全部已进入面板的报道行, 而非情感判定专属的 llm_verified_full 子集)。

【文献定位】
本指标的多源信息环境构念呼应 Tetlock (2007, JF) 关于媒体在投资者情绪形成中角色的开创性论证——该文明确区分了新闻"量" (volume) 与新闻"内容" (content) 两个独立维度, 是 media_breadth (量/广度维度) 与 tone 类指标 (内容维度) 分工的思想源头。Guest (2021, JAR) 关于媒体在盈余新闻中信息角色的研究进一步细化了媒体来源结构 (如 deepdive/staff-written/wire 等不同来源类型) 对信息传递效力的差异化影响, 为本指标"来源多样性即信息环境质量代理"这一构念提供了当代实证支撑。Gentzkow & Shapiro (2010, Econometrica) 作为顶刊经典文献, 从媒体倾向性固定效应的角度论证了单一媒体来源报道的系统性偏误风险, 为 media_breadth 作为"抵消单一媒体固定效应污染"的补充测度提供了理论依据。总体而言, media_breadth 家族在本项目测度体系中定位为 falsification/robustness 层的关注度对照维度, 与核心情感/实质性测度族 (P1–P5 各 paper 的 treatment 变量) 相互独立、互为鉴别效度检验的组成部分。Zhang, Goodell, Shen, & Lahmar (2024, International Review of Financial Analysis) 构造媒体意见分歧度量并证明其对中国股票收益具有短期正向、长期负向的可预测性, 呼应了媒体来源多样性作为独立信息广度维度而非语调维度的构念。Culpepper, Jung, & Lee (2023, American Journal of Political Science) 考察银行丑闻的媒体覆盖广度如何塑造公众对金融监管的态度, 支持将媒体覆盖广度视为区别于报道语调的独立关注度结构维度。 两项新近顶刊证据可进一步充实本族计数基座的参照, 但均须按降级口径引用。Lu (2026) 以绿色债券发行人为主体, 发现发行后与其环境表现相关的媒体报道量显著上升且持续, 并将这一「声誉绑定」机制与后续环境表现的改善相联系, 从而把主体所获媒体报道覆盖确立为可独立使用的主体级构念; 但该文以新闻数据库的报道条数度量覆盖, 并不做去重来源媒体家数 (nunique) 的 extensive-margin 计数, 故仅锚「覆盖作为主体级构念」这一般性理据, 不得视为 media_breadth 的 distinct-outlet 口径出处, 该文亦无对数变换与年度截面标准化, 且样本以国际发行人为主而非中国银行。Dechow、Lawrence、Luo 与 Stamenov (2024) 检视五届夏季奥运会中被媒体炒作为奥运受益的概念股, 发现其在奥运周期内收益更高、彼此共动更强, 并在媒体有报道关联该公司的交易日出现成交量与波动率上升, 为「涉及某主体的媒体报道量是可独立测量的注意力构念且会驱动市场后果」在中国情境下提供了前沿存在性证据; 其边界同样在于以报道篇数与炒作强度刻画关注, 未见去重来源媒体家数计数, 亦无 ln(1+·) 变换与逐年度截面 z 标准化 (含年内有效观测不少于 3 的门槛), 且以概念股与特定事件窗口而非银行-年全样本为对象, 不涉及 Fintech 与 Non-Fintech 补集的分层。
## VAR: media_breadth

【变体差分】
media_breadth 是本家族的对数原始尺度版本, 计算公式为 ln(1 + distinct_outlet_count), 其中 distinct_outlet_count 为该 bank-year 单元内全部相关报道去重后的来源媒体家数。该列未经过跨样本标准化, 数值单位为"对数化的媒体来源家数", 可直接解读: 数值越高代表该银行在该年度被越多不同来源的媒体独立报道过, 即其新闻曝光的信息渠道广度越大。作为 canonical 计算路径的直接产出, 该列既可用于描述性统计报告 (报告实际的对数尺度覆盖广度), 也可作为回归中控制银行关注度/曝光结构的协变量, 尤其适合与其他保留原始量纲的计数类控制变量 (如 n_articles 的对数版本) 并列比较, 因二者共享相同的对数平滑处理惯例, 系数含义具有可比性 (弹性解释: media_breadth 每变化 1 单位近似对应来源数的百分比变化)。该列不涉及三轨/双轨/梯子选择, 是唯一确定的聚合结果, 不存在平行版本需要"互为稳健性"地并排陈述。在伪造检验框架 (`pipeline/falsification/controls.py`) 语境下, 该列的对照组镜像版本以 non-fintech 全量银行报道 (12_fintech_news_full.parquet 减去 40_article_bank_level.parquet 差集) 为基集重新计算来源计数, 用以检验核心结论是否仅由银行整体媒体曝光结构驱动、而非金融科技相关报道特有的语调或实质内容驱动; 但该对照组变量与本列属不同 parquet/不同聚合基集下的平行产出, 命名与口径均独立于本列, 不应与本列在同一回归设定中直接相加或替换。二者的口径差异不仅止于基集范围, 还有一层更具体的去重前/去重后差异: 对照组变量 nf_media_breadth 是在【去重前】的物理行集口径上计数, 含跨媒体转载 (同一篇稿件被多家媒体转发即计为多条不同来源记录); 而本列 media_breadth 是在 stage 40 面板聚合前已完成文章级去重的面板上做 groupby nunique(媒体(中文)) 计数, 即在【去重后】的报道集合上统计来源家数。这意味着若某银行的报道存在大量跨媒体转载现象, nf_media_breadth 与 media_breadth 在同一时期呈现的"来源广度"绝对水平并不直接可比——前者的计数基数天然更大, 使用者在联合解读或做差分对照时应留意这一去重口径的边界, 而非仅将差异归因于 fintech-report 子集与全量报道基集的范围差异。使用该列时应留意其对数底为自然对数 (ln), 加一平滑对 distinct_outlet_count=0 的单元 (完全无报道或报道均来自唯一来源判定为0家的极端情形) 给出确定值 0, 不产生缺失。

## VAR: media_breadth_z

【变体差分】
media_breadth_z 是 media_breadth 经年度截面标准化后的分数, 产出于 `pipeline/panel/geography.py::standardize_panel_variables` 步骤 7b (Fama-MacBeth 1973 年度截面标准化范式), 计算口径为按 year 分组、逐年度截面分别求 z = (media_breadth − mean_year(media_breadth)) / sd_year(media_breadth); 前提是当年 n_articles>0 且该年度截面内有效观测数 ≥3, 标准差过小 (<1e-10) 的退化年份亦整格 NaN。因此每一年份内部单独归一至 μ=0/σ=1, 而非跨全部年份一次性汇总求一个整体均值/标准差——这与该指标名称容易引起的"跨全样本排名"联想不同, 务必以年度截面为解读单位。与 media_breadth 的核心差分在于计算发生的"层级": media_breadth 是 bank-year 单元内部报道来源计数的对数聚合 (单元内运算), 而 media_breadth_z 在此基础上叠加了一层同年度内跨单元 (across bank, within year) 的相对位置标准化, 因此该列的取值不再具有独立可解释的"来源家数"含义, 而是表达"该银行在该年度截面内的媒体覆盖广度相对同年其他银行高/低多少个标准差"这一相对排名信息, 不同年份之间的 z 值不共享同一把标尺、不可直接相减或跨年比较绝对大小。该列的典型使用场景是需要将媒体覆盖广度与其他年度截面标准化协变量并入同一回归方程比较相对影响力大小的场合——此时统一量纲 (年内标准差单位) 是使跨变量系数直接可比的前提, 若混用原始尺度与标准化尺度的协变量, 系数大小将无法反映相对经济显著性。同样, 该列不涉及三轨/双轨/梯子选择, 是 media_breadth 唯一确定的年度截面标准化衍生版本。需要提醒的是, 由于标准化统计量 (mu/sigma) 逐年独立计算、与其它年份完全无关, 样本构成从早期试跑 T=2 的开发期样本扩展到 T=19 的生产全量样本时, 只要某一年度截面内部的银行集合与其原始 distinct_outlet_count 不变, 该年度的 z 分数理论上不会因为新增了其它年份的观测而漂移 (漂移风险仅来自同一年度截面内部银行集合/来源计数本身的变化, 例如新增银行进入某年样本改变了该年 mu/sigma), 这与"标准化基集是全样本汇总、任何年份变化都会牵动全部 z 值"的理解有本质区别。若需要跨样本、跨年份可比的绝对量尺, 应改用未标准化的 media_breadth 而非本列。此外, 与该家族并列存在于 falsification 对照体系中的其他标准化控制变量共享同一年度截面标准化惯例 (均按 year 分组独立求 z-score), 但各年度、各变量的 mu/sigma 彼此独立, 不可跨列或跨年混用同一标准化假设。
<!-- rendered-citations:begin -->
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment; The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Guest, N. M. (2021). The information role of the media in earnings news. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Zhang, Z., Goodell, J. W., Shen, D., & Lahmar, O. (2024). Media opinion divergence and stock returns: Evidence from China. International Review of Financial Analysis. https://doi.org/10.1016/j.irfa.2024.103140
Culpepper, P. D., Jung, J.-H., & Lee, T. (2023). Banklash: How Media Coverage of Bank Scandals Moves Mass Preferences on Financial Regulation. American Journal of Political Science. https://doi.org/10.1111/ajps.12752
Lu, S. (2026). Green Bonds: Reputational Bonding via Media Coverage. Management Science, 72(6), 5171-5192. https://doi.org/10.1287/mnsc.2024.05701
Dechow, P., Lawrence, A., Luo, M., & Stamenov, V. (2024). Media Attention and Event-Based Grouping of Stocks: An Examination of Stocks Hyped by Media Outlets as Benefiting from the Olympics. Management Science, 70(8), 5157-5186. https://doi.org/10.1287/mnsc.2021.02218
<!-- rendered-citations:end -->
