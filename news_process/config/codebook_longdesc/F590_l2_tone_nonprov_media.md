---
family_id: F590
columns:
- tone_nonprov_media_ctx
- tone_nonprov_media_full
- tone_nonprov_media_ss
unit: 语调得分 (连续, 理论域 [-1,1]; bank-year 面板层聚合均值)
formula: tone_nonprov_media{track} = mean(llm_vote_score{track} | _is_homeprov==0), groupby [target_bank, year]; _is_homeprov 由银行注册地省份 (config/bank_addresses.json) 与报道来源省份 (国家地区/省份 列, 经 _clean_geo 去行政区划后缀) 逐篇比对得到, 地理元数据任一侧缺失记 NaN (出域, 不计入本地/异地任一侧); 同城 (_is_homecity==1) 拓扑蕴含同省, 经 np.where 上调
producer: pipeline\panel\attention_media.py
upstream:
- pipeline\panel\attention_media.py::_is_homeprov (维度⑨ 地理邻近性)
- config\bank_addresses.json
- pipeline\sentiment\tone_llms.py (llm_vote_score{track} 来源)
citations:
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What drives media slant? Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: Media bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: '145'
  issue: '2'
  pages_or_artno: 445-463
- doi: "10.1111/1475-679x.12560"
  type: journal
  authors: "Xu, G."
  year: 2024
  title: "News Bias in Financial Journalists' Social Networks"
  venue: "Journal of Accounting Research"
- doi: "10.1287/mnsc.2023.02247"
  type: journal
  authors: "Dyer, T., Lang, M. H., & Oh, J."
  year: 2025
  title: "Media Conglomeration, Local News, and Capital Market Consequences"
  venue: "Management Science"
new_dois:
- "10.1111/1475-679x.12560"
- "10.1287/mnsc.2023.02247"
---

## CORE

【构念与来源】
本家族 (F590) 测度"异地媒体语调" (`tone_nonprov_media`): 对一家银行、一个年份, 汇总所有注册地省份与该银行总部所在省份不相同的媒体来源所发布报道的情感均值。它是 Gentzkow & Shapiro (2010, Econometrica) "媒体偏向由何驱动" (what drives media slant) 理论在中文银行-金科新闻语料上的操作化对照组: Gentzkow & Shapiro 用美国日报数据证明媒体偏向 (slant) 系统性地向本地读者的既有立场/需求倾斜, 广告收入依赖、所有权结构与地方受众偏好共同塑造了这种"贴近本地"的报道取向; 本项目将这一"本地贴近性驱动偏向"的逻辑拆成"同省" (homeprov) 与"异地" (nonprov) 两个互斥子样本各自聚合语调, 再作差得到 `tone_gap_homeprov_nonprov{track}` (偏袒度缺口, 另一独立家族)。F590 本身对应异地一侧, 即偏袒度缺口的"基线"/对照测度: 若同省语调显著高于异地语调, 说明存在本地正面倾斜; F590 单独看则反映"外部视角"下银行的媒体形象, 不受本地关系网络污染, 在跨市场比较、监管声誉外部性等研究场景中可独立作为控制变量或结果变量使用。

You & Zhang & Zhang (2018, RFS) 与 Qin, Strömberg & Wu (2018, AER) 的中国媒体制度研究进一步支持这一拆分的必要性: 中国媒体系统存在显著的地方保护主义与"你办事我宣传"式合谋 (You et al. 2018), 且官方媒体存在系统性正面偏向 (Qin et al. 2018), 两者叠加意味着同一篇报道的语调强烈依赖发布媒体与被报道银行的地理关系, 若不拆分同省/异地子样本, 银行层面的聚合语调会把"银行基本面" (fundamentals) 与"本地媒体关系" (relationship-driven slant) 两种截然不同的信号混为一谈。F590 通过剔除本地关系可能污染的同省样本, 提供了一个相对"干净"的语调测度, 更接近 Tetlock (2007, JF) 原始框架中"媒体作为独立信息中介"的构念假设 (媒体反映而非扭曲基本面信息)。

【方法学与计算】
产出发生在 `pipeline/panel/attention_media.py` 维度⑨ ("地理邻近性: 本地 vs 异地媒体, 同省/同城双层")。构造分三步。第一步是地理判定: 从 `config/bank_addresses.json` 取银行注册地省份, 与文章级"国家地区/省份"列比对, 两侧均先经 `_clean_geo` 去除"省/市/自治区/特别行政区"等行政区划后缀标准化 (解决"杭州市"≠"杭州"字面不匹配问题); 逐篇编码 `_is_homeprov` ∈ {1.0=同省, 0.0=异地, NaN=不可判}。第二步是显式 NaN 出域守卫: 若银行注册地省份缺失或报道来源省份缺失/为空串, 记为 NaN 而非强制归为 0 (异地) ——这是 2026-06-11 (omni-g-attention-07) 的口径修正, 修正前的旧编码会把"来源不可知"错误并入异地组, 导致 F590 (异地) 分母虚增、分子混入不可判文章, 系统性拉低语调均值并压缩 `tone_gap_homeprov_nonprov` 缺口。修正后, `groupby.mean()` 天然跳过 NaN, 使 F590 的分母严格等于"确认为异地"的篇数。第三步是拓扑一致性提升: 若同城 (`_is_homecity==1`) 则同省必然为 1 (`np.where` 覆写, 而非可能抹掉已判定值的 `np.maximum`/`np.fmax`), 保证"同城⇒同省"这一行政层级蕴含关系恒成立 (Stage 内断言: `homeprov_media_frac >= homecity_media_frac`, 违反时写 ERROR 日志)。

三列本身的计算是: 取 `_is_homeprov==0` 的子样本 (异地报道), 按 `[target_bank, year]` 分组, 对该轨道情感原始得分列 `llm_vote_score{track}` 取算术均值, 得到 `tone_nonprov_media{track}`。这里的 `llm_vote_score` 是三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票的连续情感得分 (非离散标签), 与家族名前缀 `tone_` 一致的其余地理测度 (`tone_homeprov_media`/`tone_homecity_media`/`tone_noncity_media`) 共享同一 `_is_homeprov`/`_is_homecity` 判定逻辑与同一情感来源列, 仅子样本过滤条件与分组标签不同。三轨 (`_full`/`_ctx`/`_ss`) 的差异纯粹来自源列切换 (`llm_vote_score_full`/`_ctx`/`_ss`), 三者在同一子样本掩码下各自独立聚合, 不存在轨间加权或合并; 若某轨源列在文章级表中缺失, 该轨整体优雅跳过 (`if src_tone not in df.columns: continue`), 不产生该轨列而非填 NaN 占位。

【文献定位】
本家族的理论根基是 Gentzkow & Shapiro (2010, Econometrica) 的媒体偏向驱动因素研究 ——他们用美国日报数据证明媒体报道立场系统性向本地读者需求/既有偏好倾斜, 并将其归因于广告收入依赖、所有权结构与受众地缘特征三条制度性传导渠道。本项目将这一"地理邻近性驱动报道立场"的美国场景发现, 移植到中国银行业媒体报道语境, 并叠加中国特有的媒体制度背景: You, Zhang & Zhang (2018, RFS) 证明中国财经媒体存在"以负面报道换取广告/公关费"的寻租行为 (media capture), Qin, Strömberg & Wu (2018, AER) 证明官方媒体在政治敏感议题上系统性压低负面报道比例, 二者均暗示地理邻近性 (尤其省级行政关系) 是中国语境下媒体独立性受损的重要传导渠道之一。Fang, Wang, Wang & Yuan (2024, IREF) 是在同一"中国银行业+媒体情感"经验设定下的直接同域文献, 其发现媒体情感通过存款稳定性传导至银行系统性风险, 为本项目将地理拆分后的媒体语调纳入银行层面面板回归 (作为治理/声誉溢价的控制或识别工具) 提供了实证先例。Tetlock (2007, JF) 是"媒体语调作为独立信息载体"这条经典文献线索的方法学锚点; Heese, Pérez-Cavazos & Peter (2022, JFE) 用美国地方报纸倒闭作为准自然实验, 证明本地新闻监督缺位后企业不当行为上升, 揭示"本地媒体存在" (local media presence) 本身构成公司治理外部约束的一环, 与本家族"异地媒体是否仍能提供独立于本地关系网络的语调信号"这一构念形成互补参照: 前者关注本地媒体"退出"对治理的负外部性, 后者关注本地媒体"在场但可能被俘获"对语调水平的正向扭曲, 二者共同支撑"地理邻近性系统性影响媒体报道质量与立场"这一跨制度背景的一般性发现, 尤其对应本维度⑨同一代码块内伴生的 `neg_frac_{home,non}prov{track}` (负面比例) 指标族, 互补构成"语调水平"与"负面尾部过滤"两个正交的地方偏袒检验角度。Xu (2024, Journal of Accounting Research) 证明财经记者的社交网络关系会系统性引入报道偏向, 为F590所依赖的地理邻近性驱动媒体语调偏袒机制提供了记者层面关系俘获渠道的最新实证补充。Dyer, Lang & Oh (2025, Management Science) 考察媒体集团化对本地新闻覆盖与资本市场后果的影响, 为F590区分本地/异地媒体语调的构念划分提供了本地新闻供给变化如何影响公司信息环境的最新证据支持。

三轨口径铁律 (与 CLAUDE.md「三轨 full/ctx/ss」条款一致): `tone_nonprov_media_full`/`_ctx`/`_ss` 三者各自基于独立的情感源轨道 (标题+正文全文 / 标题+实体窗口 / 标题+银行∧金科同句±N窗) just-identified 并排计算, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 或同一 RHS 回归设定。`_ss` 轨的回退语义镜像 `_ctx`: 当某篇报道不存在银行∧金科同句共现时, 其 `content_ss` 退化为全文 body (`ss_is_fallback=True`), 情感源列 `llm_vote_score_ss` 的取值口径随之继承该退化, 但地理判定 `_is_homeprov` 本身与轨道无关 (基于报道来源省份, 不依赖情感文本窗口), 故三轨仅在"取哪一列语调均值"上分叉, 分组子样本 (哪些篇属于异地) 三轨完全一致。留篇门控 (2026-06-29 起 full-only) 意味着"是否算作一篇有效银行-金科报道"仅由 `llm_verified_full` 判定, ctx/ss 两轨的 `tone_nonprov_media_ctx`/`_ss` 行宇宙是 full 留篇集合的条件子集 (conditional-on-full), 而非独立样本框架下的平行測度。

## VAR: tone_nonprov_media_ctx

【变体差分】
本列是 `_ctx` 轨: 分组求均值的源列为 `llm_vote_score_ctx`, 该情感得分产生于"标题+实体窗口"文本 (仅围绕目标银行/金科实体截取的局部上下文, 而非全文), 由 stage 21 三家 LLM 投票产出、stage 14 `ctx_materializer` 物化的 `content_ctx` 驱动。与 `_full` 轨相比, `_ctx` 剔除了正文中与银行-金科议题无直接实体关联的背景段落, 因而更贴近"报道中直接谈及该银行/金科业务的那部分语气", 对长篇综述型报道 (银行仅作为背景提及) 的语调噪声更不敏感。地理子样本划分 (哪些文章计入异地组) 与 `_full`/`_ss` 完全一致, 差分仅体现在情感测量窗口。按留篇门控口径, `_ctx` 轨的有效样本是 `llm_verified_full==True` 的条件子集, 属于测度/稳健性轨而非独立留篇判据; 该列与 `tone_nonprov_media_full`/`tone_nonprov_media_ss` 互为稳健性并排, 不应混入同一 over-identified 设定。

在异地媒体这一特定子样本上, `_ctx` 轨的相对价值体现在: 当异地媒体转载或转述本地新闻时, 报道全文常夹杂大段与该银行本身经营无关的行业综述、政策解读或其他银行的对比信息 (异地媒体缺乏本地采编资源, 更依赖通稿/综合改写), 此时 `_full` 轨的语调均值容易被这些背景段落稀释或污染, 而 `_ctx` 轨聚焦于实体窗口, 能更精确地捕捉异地媒体"谈到这家银行时"的真实语气, 是检验 Gentzkow & Shapiro (2010) 媒体立场地缘驱动假说时排除"背景噪声混淆"解释的重要稳健性佐证。若 `tone_gap_homeprov_nonprov_ctx` (同省减异地的语调缺口, 另一独立家族) 在 `_ctx` 轨上依然显著为正, 则可以排除"缺口只是背景段落长度差异造成的测量伪影"这一竞争性解释。

## VAR: tone_nonprov_media_full

【变体差分】
本列是 `_full` 轨, 即家族的 canonical/主口径: 分组求均值的源列为 `llm_vote_score_full`, 该情感得分基于"标题+正文全文" (prepend_title 拼接后的完整报道文本) 由三家 LLM 投票产出。`_full` 轨是 P1 (`bank_fintech_tone`) 主线论文 `treatment.primary` 的默认口径, 也是留篇门控 (`llm_verified_full`) 直接依赖的轨道 —— 一篇报道是否被计入"该银行的一篇有效金科报道"仅取决于 `_full` 轨的 LLM 判定, `_ctx`/`_ss` 两轨在此意义上是条件于 `_full` 留篇集合的稳健性测度。相较 `_ctx`/`_ss`, `_full` 轨保留了报道全文的所有语境信息 (包括与银行/金科议题弱相关的背景段落), 语调更接近"整篇报道给读者的总体印象", 是三轨中信息量最完整但也最可能被无关段落稀释的一档。地理子样本划分 (异地组) 与另两轨完全一致。

作为 canonical 口径, `tone_nonprov_media_full` 是 `tone_gap_homeprov_nonprov_full` (本地偏袒缺口的主测度) 的两个组成部分之一, 在多数下游面板回归/描述统计中默认以本列而非 `_ctx`/`_ss` 作为异地媒体语调的报告口径; 同一维度⑨代码块内伴生的 `neg_frac_nonprov_full` (异地负面比例) 与本列共享完全相同的子样本掩码 (`_is_homeprov==0`) 与分组键, 二者可联合解读: 若异地组的 `tone_nonprov_media_full` 偏低且 `neg_frac_nonprov_full` 偏高, 则说明异地媒体既在语调水平上更负面, 也在负面消息的报道倾向上更不加过滤, 两个信号相互印证而非冗余, 因为语调均值可能被少数极端正面/负面报道拉动, 而负面比例是更稳健的方向性指标。使用者在解释本列时应留意: 它反映的是"异地媒体报道该银行时的平均语气", 而非"该银行整体媒体形象" —— 后者须结合 `tone_homeprov_media_full` 按篇数加权合并才能还原。

## VAR: tone_nonprov_media_ss

【变体差分】
本列是 `_ss` 轨: 分组求均值的源列为 `llm_vote_score_ss`, 该情感得分基于"标题+银行∧金科同句 (±N 句窗, 默认 N=1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`) 共现窗口"文本产出, 是三轨中语境窗口最窄、判定最严格的一档 (裸 AC 自动机同句共现口径)。回退语义镜像 `_ctx`: 若一篇报道内银行与金科词汇从未出现在同一句 (含 ±N 句窗) 内, 则 `content_ss` 整体退化为全文 body (`ss_is_fallback=True`), 该篇的 `llm_vote_score_ss` 取值继承此退化路径, 使得退化篇目在 `_ss` 轨与 `_full` 轨的情感读数趋同 (但地理归属判定不受影响, 仍按报道来源省份独立判定)。地理子样本划分 (哪些文章计入异地组) 与 `_full`/`_ctx` 两轨完全一致, 仅情感测量窗口不同。`_ss` 轨与 `_ctx`/`_full` 三者 just-identified 并排、互为稳健性, 禁止混入同一 over-identified Hansen J 或合并进同一 RHS。

`_ss` 轨在异地媒体语调这一构念上的边际价值最为苛刻: 它只保留银行与金科词汇在文本中真正同句 (或紧邻句) 出现的窗口, 因此对"异地媒体是否真正在讨论银行的金科业务" (而非仅在同一篇报道中先后提及银行与金科两个独立议题) 提供最严格的过滤。判定不对称口径 (银行侧含否定+短名过滤, 金科侧为裸 AC 607 词典命中) 与 `_ctx`/`_full` 完全共享, `_ss` 轨仅是共现窗口进一步收窄到句级。在异地组样本量本就可能因地理不可判 NaN 出域而更小的前提下, `_ss` 轨的退化比例 (`ss_is_fallback` 为真的篇数占比) 往往高于本地组同类统计 (异地报道更常是通稿改写, 银行-金科议题共现密度更低), 解读该列时应结合退化比例一并考察, 避免把"退化到全文"误认为"真实同句证据"。

<!-- rendered-citations:begin -->
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Xu, G. (2024). News Bias in Financial Journalists' Social Networks. Journal of Accounting Research. https://doi.org/10.1111/1475-679x.12560
Dyer, T., Lang, M. H., & Oh, J. (2025). Media Conglomeration, Local News, and Capital Market Consequences. Management Science. https://doi.org/10.1287/mnsc.2023.02247
<!-- rendered-citations:end -->
