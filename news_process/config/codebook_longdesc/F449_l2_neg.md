---
family_id: F449
columns:
- neg_frac_ctx
- neg_frac_full
- neg_frac_ss
unit: 占比 (proportion, ∈ [0, 1])
formula: 'neg_frac{track} = mean(is_negative{track}) over bank-year 内全部有效文章; is_negative{track} = 1{llm_vote_score{track} == -1}, llm_vote_score{track} 为三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票产生的篇章级情感共识分类 (-1/0/+1)'
producer: pipeline\panel\encode.py (build_aggregation_dict, L755-756; encode_sentiment 的 is_positive/is_negative 构造 L289-293) ; pipeline\sentiment\tone_llms.py (llm_vote_score 上游生成) ; pipeline\panel\runner.py (步骤2 encode_sentiment 调用点)
upstream: []
citations:
- {doi: "10.1108/JED-06-2025-0296", type: journal, authors: "Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B.", year: 2025, title: "Investor negativity derived from news shapes firm distress dynamics under bounded rationality", venue: "Journal of Economics and Development", vol: "27", issue: "4", pages_or_artno: "309–321"}
- {doi: "10.1111/j.1540-6261.2012.01725.x", type: journal, authors: "Gurun, U. G., & Butler, A. W.", year: 2012, title: "Don't believe the hype: Local media slant, local advertising, and firm value", venue: "The Journal of Finance", vol: "67", issue: "2", pages_or_artno: "561–598"}
- {doi: "10.1111/1475-679X.12071", type: journal, authors: "Piotroski, J. D., Wong, T. J., & Zhang, T.", year: 2015, title: "Political incentives to suppress negative information: Evidence from Chinese listed firms", venue: "Journal of Accounting Research", vol: "53", issue: "2", pages_or_artno: "405–459"}
- {doi: "10.1126/sciadv.adp1528", type: journal, authors: "Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.", year: 2024, title: "Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy", venue: "Science Advances", vol: "10", issue: "45", pages_or_artno: "Article eadp1528"}
- doi: "10.1177/08944393251334977"
  type: "journal"
  authors: "Stromer-Galley, J., McKernan, B., Zaman, S., Maganur, C., & Regmi, S."
  year: 2026
  title: "The Efficacy of Large Language Models and Crowd Annotation for Accurate Content Analysis of Political Social Media Messages"
  venue: "Social Science Computer Review"
  vol: "44"
  issue: "3"
  pages_or_artno: "466-487"
- doi: "10.1016/j.iref.2025.104564"
  type: "journal"
  authors: "Branzoli, N., Marchetti, S., & Tarducci, E."
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "International Review of Economics & Finance"
  vol: "104"
  pages_or_artno: "104564"
new_dois: []
---

## CORE

【构念与来源】
本家族 (F449, l2_neg) 度量的是"银行-年"面板内一家银行当年被报道文章中, 经三家大语言模型 (LLM) 多数投票产生负面情感共识判定的文章所占比例。它属于情感分析产出链条上"分类占比"这一支, 与"平均语调分数" (tone/score) 支是同源不同表征: score 支把 -1/0/+1 三分类值直接算术平均得到一个连续尺度的年度语调; 而本家族先把每篇文章二值化为"是/不是负面共识" (`is_negative`), 再对该二值指示量按银行-年取均值, 得到一个可直接解释为"负面报道占比"的比率, 落在 [0, 1] 区间。这两支在信息含量上高度相关但不等价: score 支对"轻度负面"与"极度负面"敏感 (幅度信息), 占比支只关心"是否越过负面阈值"这个二元判据 (发生率信息), 二者互为补充而非互相替代。

源头是 stage 21 三家 LLM (`gpt-5.4-nano`/`gpt54nano`、`gemini-3.1-flash-lite`/`gemini31` 两家经由 yunwu 网关、`deepseek-v4-flash`/`deepseekv4` 直连 api.deepseek.com) 对每篇文章-银行配对独立打出的三分类情感判断, 经多数投票机制聚合为单一篇章级共识分类 `llm_vote_score` (取值 ∈ {-1, 0, +1}, 对应负面/中性/正面)。`pipeline\panel\encode.py` 的 `encode_sentiment` 步骤 (对应 runner 步骤2) 把该共识分类物化为两个 nullable Int8 指示列: `is_positive = 1{llm_vote_score == 1}`、`is_negative = 1{llm_vote_score == -1}` (中性既非二者)。随后 `build_aggregation_dict` 在 bank-year 聚合字典里登记 `neg_frac{track} = mean(is_negative{track})`, 即该银行当年全部有效 (verified) 文章里被判为负面的比例; 与其成对的 `neg_count{track} = sum(is_negative{track})` 是同一分子的计数版 (未除以有效篇数), 二者共享分子、分母不同 (占比是率, 计数是量)。

需要特别指出一个已知的经验特征而非缺陷: 银行金融科技新闻语料的情感极性天然右偏 (正面/中性远多于负面报道), 因此 `neg_frac` 在生产语料上实测接近退化 (验证篇负面占比约 0.24%)。这一"近退化"特征已被上游 `pipeline\panel\codebook.py` 的 `_SENT_DIAG_SPECS` 显式标注为诊断用途——`pos_frac`/`neg_frac`/`pos_count`/`neg_count` 这组变量的首要功能是支撑测量学诊断 (揭示类别先验极度不平衡、负面子样本可能出现零方差或极小 N, 提示后续回归对该子样本估计的功效局限), 而非作为高方差的核心处理变量或结果变量直接进入主回归设定。使用者在把 `neg_frac` 纳入模型前, 应先核验对应银行-年单元的有效篇数是否足以支撑该比率的统计功效。

【方法学与计算】
计算发生在 `pipeline\panel\runner.py` 编排的 bank-year 聚合阶段 (步骤2 `encode_sentiment` 产 `is_negative{track}` 指示列, 步骤5 `aggregate_panel` 消费 `build_aggregation_dict` 里登记的 `mean` 聚合规则)。具体链路: (1) stage 21 三家 LLM 各自独立对同一篇文章-银行配对给出情感判断; (2) 多数投票规则把三家判断汇总为单一共识 `llm_vote_score` (`pipeline\sentiment\tone_llms.py` 生成, 详见该模块的投票逻辑); (3) `encode_sentiment` 把共识值二值化为 `is_negative = 1{llm_vote_score == -1}` (文章级, 逐轨道各自独立二值化); (4) `aggregate_panel` 对同一银行-年内全部符合门控条件的文章取该指示列的算术均值, 得到 `neg_frac{track}`。分母是该银行-年-轨道下参与聚合的文章数 (verified 域), 分子是其中判定为负面的文章数——因此本质上是一个条件频率/比率 (rate), 而非幅度测度。

三轨道 (full/ctx/ss) 是本仓库贯穿全部情感测度族的标准正交扩展: `_full` 轨基于标题+全文正文构造的 LLM 输入 (`content_full`); `_ctx` 轨基于标题+目标银行实体窗口截取的文本 (`content_ctx`); `_ss` 轨基于标题+银行与金融科技词同句 (±N 句窗, 默认 N=1) 共现片段的文本 (`content_ss`)。三者各自独立跑一遍完整的 LLM 判定→投票→二值化→聚合链路, 产生三套互相平行、口径独立的 `neg_frac_full`/`neg_frac_ctx`/`neg_frac_ss`, 各自 just-identified 并排、互为稳健性、不分主次, 使用者禁止把三轨混入同一 over-identified Hansen J 类过度识别检验框架内联合使用——三轨是为回答"结论是否依赖于文本截取窗口选择"这一稳健性问题而设计的平行轨道, 不是可以相互替代或加总的子成分。

留篇门控口径 (2026-06-29 起) 遵循 full-only 铁律: 一篇报道是否被计入"该银行当年一篇有效的银行-金科报道"这一判定, 只看 `llm_verified_full == True` (即仅 full 轨的验证结果决定行是否留在样本宇宙内); ctx/ss 轨道退化为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 但 per-track 的分子分母 (`is_negative{track}` 及其均值) 仍按各轨自身文本重新计算, 不借用 full 轨的判定结果。`_ss` 轨还有一层镜像 `_ctx` 的回退语义: 若某篇文章在 full 轨被判定留篇, 但该文章内银行与金融科技词并未出现在同一句 (即无共现窗口可截取), 则 `content_ss` 退化为使用全文 body (`ss_is_fallback = True`), 该退化标记与 `n_articles` 共享同一分母口径, 不会造成分母/分子的不对称计数错误; 若 stage 21 未跑同句轨 (`FINTECH_AC=None` 等场景), `*_is_fallback` 全为 True, 相应 `neg_frac_ss` 优雅降级为等同于全文口径的近似值而非直接产生缺列或崩溃。

【文献定位】
把负面报道占比 (而非仅平均语调分数) 作为独立测度纳入分析, 与新闻情绪对企业困境动态影响的实证传统一脉相承: Pham et al. (2025, *Journal of Economics and Development*) 在有限理性框架下证明投资者从新闻中提炼出的"负面性" (negativity, 与本家族的 negative-share 构念同构) 对企业困境动态具有独立于整体情绪水平的解释力, 支持把负面占比作为区别于均值语调的补充测度单独建模。Gurun & Butler (2012, *The Journal of Finance*) 与 Piotroski, Wong & Zhang (2015, *Journal of Accounting Research*) 分别在本地媒体口径偏向、以及中国上市公司政治激励压制负面信息披露的情境下, 使用负面报道占比刻画媒体覆盖的方向性偏差, 为本家族"负面占比反映的是选择性报道/披露倾向而非纯粹的信息内容"这一解读提供了方法学先例——尤其在本仓库语料呈现负面占比近退化 (右偏) 的经验背景下, 这类"压制负面信息"的文献视角提示: 观测到的低负面占比未必意味着银行金融科技相关事件本身罕见负面, 也可能部分反映了中国语境下媒体/机构对负面报道的结构性抑制, 使用者在解读该变量时应对此保持审慎。

产生 `llm_vote_score` 的多数投票机制本身建立在"LLM 集成判断可逼近甚至媲美人类群体智慧"这一新近方法学证据之上: Schoenegger, Tuminauskaite, Park, Bastos & Tetlock (2024, *Science Advances*) 系统评估了 LLM 集成 (ensemble) 在预测任务上的准确度, 发现多模型投票聚合能够对齐乃至逼近人类群体判断的精度, 为本仓库三家异构 LLM (gpt54nano/gemini31/deepseekv4) 多数投票取代单一模型判断、进而支撑 `is_negative` 二值化的方法学设计提供了外部效度支持。 在"以 LLM 替代或辅助人工标注完成类别判定"这一测度路径的效度层面, Stromer-Galley、McKernan、Zaman、Maganur 与 Regmi (2026) 实证评估了 LLM 与众包标注在文本内容分析中的准确性表现, 为本家族分子端(即把篇章级情感共识二值化为负面指示量)依赖机器标注而非人工编码提供了外部效度参照。迁移边界须诚实写明: 该文语料为英文政治社交媒体消息、标注任务为政治内容类别, 与本仓库中文银行金融科技新闻的情感三分类在语言、领域与标注体系上均不同; 且该文评估的是单模型与众包标注的对比, 既未检验本家族所用的三家模型多数投票聚合规则, 也未涉及 gpt54nano/gemini31/deepseekv4 这一具体组合, 因此它支持的是"LLM 可胜任类别判定"这一前提, 而非本仓库投票口径本身。就"媒体语调测度 → 银行层级结果"这条应用链条而言, Branzoli、Marchetti 与 Tarducci (2025) 构造了媒体报道的语调测度并将其应用于意大利银行融资条件这一银行层级实证问题, 与本家族"文章级情感判定 → bank-year 聚合 → 银行层级结果变量"的应用域同构, 是该链条的近期同域存在性证明; 但其国别为意大利、语料非中文新闻, 其语调测度既非本仓库的 LLM 共识投票口径, 亦无 full/ctx/ss 三轨文本切分, 故仅可作为应用域层面的平行参照, 不构成对负面占比(区别于语调均值)这一具体构造的直接背书。
## VAR: neg_frac_full

【变体差分】
本列是 l2_neg 家族在 full 轨道 (标题+全文正文) 上的负面占比测度, 是留篇门控的主口径轨——`llm_verified_full == True` 直接决定该银行-年-文章是否进入分母宇宙, 因此 `neg_frac_full` 的分母 (verified 篇数) 是三轨中唯一独立确定行宇宙、不依赖其他轨道判定结果的一支。其分子 `is_negative_full = 1{llm_vote_score_full == -1}` 由三家 LLM (gpt54nano/gemini31/deepseekv4) 各自读取标题+全文正文构造的输入、独立打分、再多数投票得到共识分类 `llm_vote_score_full`。作为三轨之一, `neg_frac_full` 与 `neg_frac_ctx`/`neg_frac_ss` 各自 just-identified 并排、互为稳健性、不分主次, 但由于其留篇门控地位, 在多数下游 paper 模块 (如 P1 `bank_fintech_tone` 主处理变量 `llm_vote_tone_full`) 的主设定中, full 轨常作为默认起点, ctx/ss 轨则作为"结论是否随文本窗口选择而改变"的稳健性检验轨。

该轨文本量最大 (包含全文正文全部段落), 优点是信息最完整、不受实体窗口截取或同句共现判据的窗口效应影响; 局限是若一篇文章内除银行金融科技相关段落外还夹杂其他主题的负面内容 (例如同一篇报道里既提到该银行的金融科技合作、又提到宏观经济下行), LLM 在全文语境下的负面判定可能被无关段落的负面语气"稀释"或"污染", 这正是 ctx/ss 两轨存在的方法学动机——用更窄的窗口剥离无关文本, 检验 full 轨的判定是否稳健于这种潜在污染。使用者若观察到 full 轨负面占比与 ctx/ss 轨系统性偏离, 应优先怀疑全文冗余段落对 LLM 判读的干扰, 而非直接判定某一轨"更准确"。

## VAR: neg_frac_ctx

【变体差分】
本列是 l2_neg 家族在 ctx 轨道 (标题+目标银行实体窗口截取文本, `content_ctx`) 上的负面占比测度。其分子 `is_negative_ctx` 由三家 LLM 读取实体窗口文本 (而非全文) 独立打分并投票得到; 分母行宇宙沿用 full 轨的留篇判定 (`llm_verified_full == True` 决定的子集), 但分子分母的具体数值仍完全基于 ctx 轨自身文本重新计算, 不与 full 轨共享判定结果。该轨的设计动机是检验负面占比结论是否对"LLM 只看银行周边窗口文字, 而非全文语境"这一测量选择敏感——若结论在 full 与 ctx 两轨间高度一致, 说明负面判定主要由银行实体附近的文字驱动, 全文冗余信息影响有限; 若两轨出现系统性偏离, 则提示全文语境 (如文章其他段落讨论的无关负面事件) 可能污染了 full 轨的判定。与 `neg_frac_full`/`neg_frac_ss` 互为稳健性并排, 禁止混入同一过度识别检验。

ctx 轨的窗口截取发生在 stage 14 `ctx_materializer` (物化 `content_ctx` 列, `prepend_title` 拼接标题, 不改动上游原始"内容"列), 早于 stage 21 情感判定, 因此该轨的负面占比不是对 full 轨判定结果的事后再加工, 而是从头独立走完"截取窗口→LLM 独立打分→三家投票→二值化→bank-year 均值"完整链路的平行测度。相较 full 轨, ctx 轨天然剔除了文章内与目标银行不直接相关的段落, 因此更贴近"银行本身在报道中被赋予的语气"这一构念, 但代价是窗口截取本身依赖实体识别的准确性, 若命名实体识别 (NER) 漏检或误判银行别名/简称, 窗口可能截取不完整, 引入额外的测量误差来源, 这是 full 轨不存在的额外风险维度。

## VAR: neg_frac_ss

【变体差分】
本列是 l2_neg 家族在 ss 轨道 (标题+银行与金融科技词同句 ±1 句窗共现片段, `content_ss`) 上的负面占比测度, 是三轨中文本窗口最窄、判据最严格的一支——要求银行实体与金融科技词汇在同一句 (或默认 ±1 句半径窗口) 内共同出现才截取该片段供 LLM 判读。其分子分母的行宇宙同样沿用 full 轨的留篇判定子集, 但当某篇留篇文章内银行与金科词并未同句共现时, `content_ss` 依 `_ss` 镜像 `_ctx` 的回退语义退化为使用全文 body (`ss_is_fallback = True`, 与 `n_articles` 共享同一分母口径, 不产生分子分母不对称); 若 stage 21 未产出同句轨 (`FINTECH_AC=None`), `*_is_fallback` 全部为 True, `neg_frac_ss` 因而退化为等同全文口径的近似值。该轨用于检验"负面判定是否由银行与金融科技概念紧邻共现的最狭义证据支撑"这一最严格的稳健性问题, 与 `neg_frac_full`/`neg_frac_ctx` 互为稳健性并排, 不分主次, 禁止混入同一过度识别检验框架。

判定"是否同句共现"的原语函数与 stage 13 硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` 是不同口径 (禁止互相复用): `_ss` 轨依据的是严格同句 (或 ±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1) 抽取的共现原语, 与 stage 13 用于决定文章是否整体保留的硬过滤半径参数是两个独立的配置键, 不应混淆。由于 ss 轨窗口最窄, 其文本量在三轨中最小、对无关段落的抗污染能力最强, 但也最容易触发上文所述的回退到全文 body 的退化情形——尤其在 dev 早期试跑语料 (T=2) 上, ss 轨常表现出与 full 轨高度重合甚至零方差的退化特征, 这属于样本量不足导致的预期现象, 生产全量语料 (T=19) 上 ss 轨的窄窗口优势才能充分体现。

<!-- rendered-citations:begin -->
Pham, X. T. T., Huynh, D. T., Nguyen, N. T. K., & Luu, T. B. (2025). Investor negativity derived from news shapes firm distress dynamics under bounded rationality. Journal of Economics and Development, 27(4), 309–321. https://doi.org/10.1108/JED-06-2025-0296
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561–598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405–459. https://doi.org/10.1111/1475-679X.12071
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), Article eadp1528. https://doi.org/10.1126/sciadv.adp1528
Stromer-Galley, J., McKernan, B., Zaman, S., Maganur, C., & Regmi, S. (2026). The Efficacy of Large Language Models and Crowd Annotation for Accurate Content Analysis of Political Social Media Messages. Social Science Computer Review, 44(3), 466-487. https://doi.org/10.1177/08944393251334977
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
