---
family_id: F591
columns:
- tone_official_media_ctx
- tone_official_media_full
- tone_official_media_ss
unit: 语调得分 (连续, 三家 LLM 多数投票语调 llm_vote_score 的 bank-year 组内均值; 单篇取值域约 [-1,1] 三分类映射, 聚合后仍落在同一区间)
formula: 'tone_official_media{track} = mean(llm_vote_score{track} | _is_official==1), 分组键 (target_bank, year); _is_official = 媒体(中文) ∈ (OFFICIAL − MARKET), OFFICIAL/MARKET 为 NPPA 数据库主管/主办单位判据下的媒体名单; track ∈ {full, ctx, ss}'
producer: pipeline\panel\attention_media.py (official/market 互斥构造与三轨 groupby-mean 主计算); pipeline\panel\export.py (列标签登记, 不改写数值)
upstream:
- 21_tone_llms (llm_vote_score_full/_ctx/_ss 三家 LLM 多数投票语调, 供本族按官方媒体子样本重聚合)
- 11_news_bank (target_bank 银行实体标注)
- 14_materialize_ctx (content_ctx/content_ss 三轨文本物化, 供 stage 21 产出对应轨道的 llm_vote_score)
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
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: Political incentives to suppress negative information - Evidence from Chinese listed firms
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing enthusiasm - Media sentiment and the disciplining role of quarterly earnings announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: Media sentiment, deposit stability and bank systemic risk - Evidence from China
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: "10.1016/j.energy.2025.139126"
  type: "journal"
  authors: "Hua, X., Dong, D., Xu, Z., & Huang, W."
  year: 2025
  title: "Official media sentiments toward energy and equity returns: Evidence from China"
  venue: "Energy"
  vol: "340"
  pages_or_artno: "139126"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量"官方媒体"子样本对目标银行报道的平均语调, 是媒体异质性 (media heterogeneity) 测度组中沿"政治取向" (political orientation) 维度切分的一支。官方媒体 (official media) 的操作化取自 You, Zhang & Zhang (2018, RFS) 关于中国媒体"谁掌握了笔杆子"的经典二分: 官方媒体依附于党政机关, 报道更受宣传纪律与行政问责约束; 与之相对的市场化媒体依赖发行与广告收入, 治理动机更接近独立第三方监督者。You et al. (2018) 的核心发现是市场化媒体的负面报道能显著促进公司治理事件 (如高管更替), 而官方媒体的这一效应弱得多——这为"媒体语调的可信度因媒体属性而系统性不同"提供了理论与实证基础。本家族沿此文献脉络, 把每篇报道先按名单硬编码归类为官方/非官方, 再在官方子样本内取语调均值, 得到 bank-year 面板列 `tone_official_media{track}`。

具体名单来源于 NPPA (国家新闻出版署) 媒体数据库的两个独立字段: 主管单位 (是否为党政机关, 记作 OFFICIAL 集合) 与主办单位 (是否为企业/商业集团, 记作 MARKET 集合)。producer 源码 (`attention_media.py`) 中记录了一次关键的构造口径修正 (fix omni-g-attention-02, 2026-06-11): 旧版直接用 `isin(OFFICIAL)` 作为官方哑变量, 但 NPPA 的 OFF 判据覆盖了 2208 家媒体 (接近全体样本), 与 MKT 判据 (471 家) 重叠达 386 家, 导致 `official_media_frac` 均值高达 0.873——这实质上是"近乎退化"的处理组定义, 且非官方对照组反而被系统性剔除了大量市场化媒体。修正后的口径改为互斥构造: `official := OFF − MKT` (剔除同时具有主办企业属性的媒体, 只留"纯官方"), `market := MKT − OFF` (对称地留"纯市场化"), 二者结构性互斥 (`official_media_frac + market_media_frac ≤ 1`, producer 代码文末有校验)。双判据媒体 (OFF∩MKT, 即主管为党政机关但主办为企业的混合属性媒体, 例如部分行业协会主办的商业化党报) 不计入 official 或 market 任一处理组, 而是落入两者各自的对照组 (`nonoff`/`nonmkt`)——这意味着 `tone_nonoff_media{track}` (非官方组) 实际上"含全部市场化媒体加上部分双判据媒体", 论文层引用该操作化时应重述"主管 vs 主办双判据非互斥"这一披露, 不能简单等同于纯二分类。

数值来源是 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票产出的逐篇语调分 `llm_vote_score{track}` (与嵌入模型无关, 详见项目铁律"嵌入 ≠ LLM"), 而非词典或 BERT 情感; 因此本族列反映的是"LLM 语调测度在官方媒体子样本上的条件均值", 与该家族之外的市场化 (`market`)、深度报道 (`deepdive`)、高频日报 (`daily`) 等其余媒体异质性维度共用同一底层语调原语, 只是切分子样本的判据不同。

【方法学与计算】
计算分两步。第一步是文章级归类: 对每篇留篇 (full-only 门控下 `llm_verified_full==True` 判定为"一篇银行金科报道", 详见项目铁律) 的报道, 依据其"媒体(中文)"字段是否落在 `OFFICIAL − MARKET` 集合内赋 `_is_official ∈ {0,1}`。第二步是条件聚合: 按 `(target_bank, year)` 分组, 在 `_is_official==1` 的子样本内对 `llm_vote_score{track}` 取算术均值, 得到 `tone_official_media{track}`; 该聚合对每个 track 独立执行 (三轨互不借用彼此的官方子样本或语调分)。若某银行-年份组合内官方媒体报道篇数为零, 该格聚合结果为缺失 (NaN), 不做插补——这是子样本条件均值类测度的常见退化, 在小样本 (如本机 T=2 dev 语料) 或官方媒体覆盖稀疏的银行-年上尤为常见。

与之配对的还有非官方语调 `tone_nonoff_media{track}` 与语调缺口 `tone_gap_official_nonoff{track} = tone_official_media{track} − tone_nonoff_media{track}` (本家族之外的姊妹列), 三者共同构成"官方 vs 非官方"这一媒体异质性子分析的完整测度组; 本家族仅覆盖其中的官方语调本体三列。

【文献定位】
官方媒体作为独立报道来源的可信度差异, 其理论根基来自媒体经济学与公司治理交叉文献。You, Zhang & Zhang (2018, *The Review of Financial Studies*) 首次在中国情境下系统区分党委机关报与市场化报纸, 发现市场化媒体的负面报道显著促进高管更替, 而官方媒体的治理纪律功能相对弱, 为本家族"按媒体属性切分语调子样本"的操作化提供了直接的构念来源与判据设计依据。Tetlock (2007, *The Journal of Finance*) 的经典研究则确立了"新闻语调是投资者情绪的可观测代理"这一测量范式的方法论基础, 是本家族底层 `llm_vote_score` 语调原语所承继的量化传统的原点文献。二者共同锚定了本家族"媒体属性异质性 × 文本语调测量"这一交叉设计的两条理论支柱。 在前沿的构念存在性层面, Hua、Dong、Xu 与 Huang (2025) 以 BERT 对中国官方/政府控制媒体的新能源报道文本构建官方媒体语调指数, 并检验其与权益回报及企业融资投资行为的关系, 表明「按媒体的官方属性切出子样本、在子样本内对文章级语调取均值」这一操作化在当下仍是活跃的测度路径, 为本家族提供了同构念的近期先例。迁移边界须如实标注: 该文的指数是能源行业与股票市场层面的日度序列, 情感由文本指数法而非本项目的三家 LLM 多数投票得到, 官方媒体名单依中国国家控股报纸清单而非本项目 NPPA 主管/主办单位判据下的 OFFICIAL−MARKET 差集, 且原文未构造 bank-year 面板层级、亦未报告官方与非官方两侧的均值之差。因此它只锚官方语调这一侧的构念存在性, 既不构成姊妹列 tone_gap_official_nonoff{track} 两侧作差这一统计量的依据, 也不涉及任何中央/地方行政层级的切分。
## VAR: tone_official_media_ctx

【变体差分】
`_ctx` 轨聚合的是实体窗口轨语调 `llm_vote_score_ctx` (标题 + 银行/金科实体附近窗口文本), 而非全文。分组、官方判据 (`_is_official`) 与聚合方式与家族 canonical 完全一致, 唯一差别在于底层逐篇语调分的文本输入范围更窄——只覆盖实体上下文附近的语言线索, 剔除了全文中与银行/金科主题无关的段落对语调分的稀释或污染。留篇门控口径 (是否计入"一篇银行金科报道") 仍由 full-only 判定 (`llm_verified_full==True`), `_ctx` 轨行宇宙是 full 留篇集的子集, 不独立扩大或收窄样本。项目铁律要求: full/ctx/ss 三轨语调各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一个 over-identified Hansen J 检验框架。当本列与 `_full`/`_ss` 两列数值出现分歧时, 应理解为"实体窗口叙事语气"与"全文整体语气"之间的构念侧重差异, 而非测量误差; 若某银行-年官方媒体报道中存在大段与该银行无关的背景介绍或行业综述, `_ctx` 与 `_full` 之间的差值会相对更明显。

在官方媒体这一子样本上, `_ctx` 轨还有一层特别值得关注的解释力: 官方媒体的行文习惯往往包含大量政策背景铺陈、领导讲话引述、行业宏观数据罗列等与目标银行本身弱相关的段落, 这类段落若整体计入 `_full` 轨的语调判断, 可能稀释或掩盖报道对该银行本身的真实态度; `_ctx` 轨聚焦于银行/金科实体紧邻窗口, 理论上更能剥离这类"泛政策叙事噪声", 更贴近"官方媒体究竟如何评价这家银行"这一狭义构念。但这也意味着 `_ctx` 轨对窗口切分参数 (实体识别准确率、窗口宽度) 更敏感, 一旦实体识别在官方媒体特有的行文风格 (如较少直呼银行简称、多用全称或职务称谓) 下出现漏检, 窗口文本可能系统性偏窄甚至为空, 从而放大与 `_full` 轨的偏离。使用者在解读本列与 `_full` 轨的差值时, 应同时检查该银行-年格内官方媒体报道的篇数是否过少, 避免把小样本噪声误读为实体窗口构念差异。

## VAR: tone_official_media_full

【变体差分】
`_full` 轨是本家族的 canonical 轨道, 聚合的是全文语调 `llm_vote_score_full` (标题 + 正文全部内容)。本列同时也是留篇门控的判定基准轨: 一篇报道是否被计入分母 (即是否为"一篇银行金科报道"), 完全由该篇的 `llm_verified_full` 布尔标志决定, `_ctx`/`_ss` 两个姊妹轨的行宇宙都是本轨留篇集合的子集。因此 `_full` 轨在样本覆盖面上通常是三轨中最完整的一支, 反映的是"整篇报道通读后的官方媒体平均语气", 适合作为跨轨比较时的默认参照, 但项目口径明确三轨互为稳健性并排, 不存在孰为"主"孰为"次"的先验排序——`_full` 只是门控基准与历史命名产物意义上的默认轨, 并非统计意义上更优的测度。

对官方媒体这一子样本而言, `_full` 轨的构念含义是"报道通篇整体基调", 这与官方媒体常见的行文结构 (标题定调、开篇引述权威表态、正文铺陈政策背景、结尾归纳意义) 相对契合——官方媒体的语调往往并非集中在提及银行名称的局部句子, 而是弥散于全篇的措辞选择与叙事框架之中, 因此 `_full` 轨在捕捉这类"整体基调"上具有天然优势, 不会像 `_ctx`/`_ss` 那样因窗口过窄而遗漏分散在全文各处的定调性表述。与此同时, `_full` 轨也更容易受到与目标银行本身弱相关的大段政策背景、行业综述内容的稀释, 这一权衡在【方法学与计算】节已作说明。使用者若关注"官方媒体是否整体上偏正面报道该银行"这一宽泛构念, 应以本列为主要参照; 若关注"官方媒体针对该银行具体行为的褒贬", 则应结合 `_ctx`/`_ss` 两列交叉验证, 三者并列而非替代。

## VAR: tone_official_media_ss

【变体差分】
`_ss` 轨聚合的是银行与金科词严格同句共现窗口内的语调 `llm_vote_score_ss` (标题 + 目标银行与金科词同句 ±N 句半径, 默认半径由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1)。`_ss` 的回退语义镜像 `_ctx`: 若某篇报道内不存在银行∧金科词同句共现, 则该篇的 `content_ss` 退化为全文 body, 对应 `ss_is_fallback` 标记为 True, 此时该篇对 `_ss` 轨语调的贡献实质上与 `_full` 轨趋同 (但仍走独立的 LLM 调用与独立的语调分列, 不是直接复制 `_full` 数值); 若金科实体识别的 Aho-Corasick 自动机 (`FINTECH_AC`) 为 None (罕见的上游依赖缺失场景), 则全部行的 `*_is_fallback` 优雅降级为 True, 三轨口径退化为一致但仍分列存储。`_ss` 相对 `_ctx` 的判定更严格 (要求同句而非窗口邻近), 因此在官方媒体报道篇数本就有限的银行-年格内, `_ss` 轨更容易因回退触发或样本过窄而与另外两轨出现较大数值分歧, 这是构念设计的预期表现而非缺陷。三轨 (`_full`/`_ctx`/`_ss`) 及本家族与"市场化""深度报道""高频日报"等其余媒体异质性维度之间, 均遵循互为稳健性并排、禁止混入同一 over-identified Hansen J 的项目铁律。

`_ss` 轨在官方媒体子样本上的实践意义在于: 它是三轨中判据最严格、噪声潜在最小的一支——只要银行名与金科词同句出现, 该句大概率是全篇最直接评价"该银行的金科相关行为"的位置, 语调判断的构念效度最高; 但代价是样本损耗也最大, 官方媒体报道原本篇数就可能少于市场化媒体 (官方媒体报道倾向于综述性、政策解读性内容, 银行与金科词严格同句共现的概率相对更低), 叠加严格判据后, `_ss` 轨在很多银行-年格上会大量触发回退 (`ss_is_fallback=True`), 使得该格实际聚合的是与 `_full` 轨趋同但独立计算的语调分, 而非真正意义上的"同句聚焦"测度。使用者在解读跨银行或跨年份的 `_ss` 轨差异时, 应先检查回退比例, 避免把"回退触发率不同"误读为"官方媒体语调本身的差异"。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving content to investor sentiment - The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information - Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm - Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk - Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Hua, X., Dong, D., Xu, Z., & Huang, W. (2025). Official media sentiments toward energy and equity returns: Evidence from China. Energy, 340, 139126. https://doi.org/10.1016/j.energy.2025.139126
<!-- rendered-citations:end -->
