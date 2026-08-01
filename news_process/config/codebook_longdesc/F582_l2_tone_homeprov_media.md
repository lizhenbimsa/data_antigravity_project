---
family_id: F582
columns:
- tone_homeprov_media_ctx
- tone_homeprov_media_full
- tone_homeprov_media_ss
unit: 语调得分 (连续, 落在约 [-1,1] 区间; bank-year 面板层面为该银行当年"同省媒体"子样本文章的三家 LLM 共识情感均值)
formula: '子样本先筛后均: 先以 _is_homeprov==1 (银行注册省份与报道来源省份经地名后缀清洗后严格相等, 城市匹配蕴含省匹配) 圈定"同省媒体"文章子集, 再对该子集在 target_bank×year 上取 llm_vote_score{full,ctx,ss} 的算术平均; 地理不可判 (银行注册地或新闻省份缺失) 记 NaN 且不计入子集, 该银行当年若无任何同省报道则整格 NaN。'
producer: pipeline\panel\attention_media.py (维度⑨ 地理邻近性; export.py 仅承载 Stata 变量标签映射, 非计算发生地)
upstream:
- pipeline\panel\tone_llms.py (llm_vote_score_full/_ctx/_ss 三家 LLM 多数投票共识情感分)
- config\bank_addresses.json (银行注册地省份/城市字典)
- 原始新闻元数据列 国家地区/省份、城市 (报道来源地)
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What drives media slant? Evidence from U.S. daily newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"同省媒体对目标银行报道的语调倾向"——把一家银行当年被本省 (与银行注册地同省份) 媒体报道的所有文章挑出来, 对这些文章的情感打分取平均, 得到一个反映"本地媒体如何说自家银行"的语调水平。构念直接源自 Gurun & Butler (2012, *The Journal of Finance*) 的本地媒体偏袒 (local media slant) 命题: 本地媒体因广告收入依赖本地企业、与地方政府存在关系性绑定等结构性原因, 对辖区内企业存在系统性正面倾斜的动机, 因此单纯观察"全部媒体的平均语调"会掩盖这种地理异质性, 必须先按报道来源地理位置切分子样本再比较。本族是该地理邻近性维度 (代码内部标注为"维度⑨") 下三项核心指标之一 (另两项为 `homeprov_media_frac` 封闭度、`neg_frac_homeprov_*` 负面过滤率), 三者协同刻画同一现象的不同侧面: 语调水平、报道占比、负面消息尾部抑制程度。语调本身继承自 P1 主线三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票共识分 `llm_vote_score` (`bank_fintech_tone` 论文 treatment 的同一原语), 本族不引入新的情感测度引擎, 只是在既有情感列之上做地理条件化子样本聚合, 与情感三法 (LLM/词典/BERT) 互为稳健性的梯子完全正交——本族只用 LLM 一支, 不产词典/BERT 平行版本。

【方法学与计算】
计算发生在 `pipeline/panel/attention_media.py` 维度⑨代码块 (`export.py` 命中的两处仅是该列在 `.dta` 导出时的英文变量标签映射表, 并非计算逻辑所在地, frontmatter `producer` 已注明这一点以防误判)。地理归属判定分三步: 第一步加载 `config/bank_addresses.json` 取每家银行注册地的省份/城市, 映射到文章级数据的 `_bank_prov`/`_bank_city` 两列; 第二步对银行注册省份与新闻元数据列"国家地区/省份"做地名后缀清洗 (去除"省/市/自治区/特别行政区"等后缀, 解决"杭州市"≠"杭州"的字符串假阴性) 后逐行比较, 相等记 `_is_homeprov=1.0`, 不等记 `0.0`; 第三步对缺失做显式 NaN 守卫——若银行注册省份或新闻省份任一为空/缺失, 直接记 NaN 而非强行归为"非本地"的 `0`, 这是 2026-06-11 的一次修复 (`omni-g-attention-07`): 旧编码把"来源不可判定"错误并入异地组, 会同时低估本地占比分子、稀释 away 组纯度、拖累 `tone_gap` 缺口估计。此外还有一条拓扑不变量: 若城市层面确认同城 (`_is_homecity==1`), 则省级归属强制提升为同省 (`_is_homeprov=1.0`), 因为同城蕴含同省, 反向则不成立 (非同城不代表非同省), 故不可用 `np.maximum`/`np.fmax` 处理 (会让 NaN 传播或被错误吃掉)。判定完成后, 对每条轨道 (`_full`/`_ctx`/`_ss`) 各自筛出 `_is_homeprov==1` 的文章子集, 在 `target_bank`×`year` 上对该轨道对应的 `llm_vote_score{track}` 取算术平均, 得到本族三列。若某银行当年境内无任何可判定同省报道 (子集为空), 该格记 NaN; 若地理元数据整体缺失 (银行注册地或来源省份列缺失), 上游 `_is_homeprov` 全 NaN, 本族随之整体 NaN 优雅降级, 不会抛异常也不会静默清零。

三轨语义遵循项目统一口径: `_full`=标题+正文全文, `_ctx`=标题+银行/金科实体窗口, `_ss`=标题+银行∧金科同句±1句窗口 (无同句共现回退为全文并置位 `ss_is_fallback=True`, 镜像 `_ctx` 缺同一实体窗口时的退化语义)。三轨情感原语 `llm_vote_score{track}` 各自独立计算, 本族对每条轨道分别做同省子样本聚合, 因而三条产出列各自 just-identified 并排, 是互为稳健性、不分主次的关系, 绝不可混入同一个 over-identified 的 Hansen J 过度识别检验; 留篇门控口径同样遵循 full-only 铁律 (2026-06-29 起), 即"是否算一篇有效银行金科报道"只看 `llm_verified_full`, ctx/ss 轨的 `n_articles`/聚合行宇宙是 full 留篇集的条件子集而非独立样本框, 因此 `_ctx`/`_ss` 两列的同省子样本规模天然小于等于 `_full` 对应子样本、且并非平行抽样, 解读稳健性对比时须留意这一点而非把三者当独立重复实验。

【文献定位】
本族方法学谱系可归纳为两条主干的交汇: 一是本地媒体偏袒/媒体地理邻近性文献, 以 Gurun & Butler (2012, JF) 为奠基之作, 该文首次证明企业总部所在地的本地报纸报道对该企业存在系统性更正面的语调, 并将其归因于广告收入依赖与信息获取便利性两条渠道; Gentzkow & Shapiro (2010, *Econometrica*) 进一步从需求侧证明媒体语调受众口味 (而非仅供给方所有权) 驱动, 为"本地=更正面"提供了另一种解释机制的对照。二是文本情感测度在金融/银行场域的应用主干, 以 Tetlock (2007, JF) 的"给投资者情绪赋予内容"为方法学源头, Holzman, Miller & Twedt (2023, *The Accounting Review*) 展示媒体语调对盈余公告信息环境的纪律约束作用, 为本族"语调是一种可与其它治理/纪律机制并列的信息变量"提供了直接的构念锚点。中国银行业场景下, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 已将媒体情感与银行系统性风险/存款稳定性直接勾连, 是与本项目同域最近的中国银行媒体情感实证; Marchetti, Tarducci & Branzoli (2025, SSRN) 提供了银行×年语调聚合口径的平行做法参照。本族的独特之处在于把"本地偏袒"命题从企业层面搬到银行层面, 并进一步用银行注册地 (而非仅新闻数据集内某种默认地理归属) 精确匹配报道来源省份, 是对 Gurun & Butler 范式在中国银行金科语境下的直接复刻与延伸。

## VAR: tone_homeprov_media_full

【变体差分】
`_full` 轨是本家族的 canonical / 主口径: 语调来源文本为标题+正文全文对应的 `llm_vote_score_full`, 子样本圈定条件同家族公用逻辑——`_is_homeprov==1` 且该篇文章在 full 轨下语调可判定 (三家 LLM 投票产生有效 `llm_vote_score_full`)。由于留篇门控严格执行 full-only 口径, `llm_verified_full==True` 是判定"这篇文章算不算一篇有效银行金科报道"的唯一依据, 因此 `_full` 轨对应的同省子样本是三轨中样本量最大、行宇宙定义最完整的一支, 也是家族内唯一不依赖任何实体窗口/同句判据缩窄文本范围的版本。在稳健性梯子的解读顺序上, `_full` 通常作为报告首选或与 `_ctx`/`_ss` 并列展示的基准, 但按项目铁律三轨互为稳健性、不分主次, 不应将 `_full` 简单等同于"真值"而把另两轨仅视为附属检验——三者应各自独立估计再比较系数符号与显著性是否一致, 且严禁三轨情感变量同时进入同一个过度识别方程。该列与家族内 `homeprov_media_frac`(封闭度)、`neg_frac_homeprov_full`(负面过滤率, 若产出) 共享同一 `_is_homeprov` 地理判定与同一 full 轨情感原语, 三者是对"同一同省子样本"的不同统计矩 (均值语调/占比/负面比例), 适合联合解读但不构成同一构念的重复测量。

## VAR: tone_homeprov_media_ctx

【变体差分】
`_ctx` 轨在语调来源上换成"标题+银行/金科实体窗口"截取的正文片段所对应的 `llm_vote_score_ctx`, 其余的同省判定逻辑 (`_is_homeprov==1`、银行注册地-新闻来源省份匹配、地名后缀清洗、拓扑不变量) 与 `_full` 完全一致, 差异只在情感打分所依据的文本范围更窄、聚焦于银行实体附近语境, 意在过滤掉与目标银行本身无直接关联的段落式噪声语调。留篇门控是 full-only 的, `_ctx` 轨的样本行宇宙是 full 留篇集的条件子集 (conditional-on-full), 而非独立于 `_full` 的另一批文章, 因此该列与 `_full` 版本之间的差异既包含"实体窗口截取带来的语调测量口径变化", 也包含"因该篇 ctx 轨情感解析失败而进一步收窄的子样本组成变化"两层来源, 解读时不能把系数差异全部归因于测度口径。作为家族内互为稳健性的一支, `_ctx` 与 `_full`/`_ss` 应各自独立进入回归、各自 just-identified, 绝不可三者同时塞进一个 over-identified 的 Hansen J 检验; 若 `_ctx` 与 `_full` 在同省语调水平上的系数方向一致, 可视为对"本地媒体偏袒"结论不依赖于全文噪声的一项支持性证据; 反之若两轨方向或显著性出现分歧, 也不宜简单判为测度失败, 而应结合子样本规模变化 (ctx 轨解析失败率、实体窗口是否恰当捕捉到本地媒体的褒扬性措辞) 一并诊断, 因为窄窗口截取本身就可能改变文本中可被 LLM 捕捉到的语气线索密度。

## VAR: tone_homeprov_media_ss

【变体差分】
`_ss` 轨语调来源是"标题+银行∧金科同句 (±1句窗口) 共现"截取文本对应的 `llm_vote_score_ss`, 是三轨中文本范围最窄、判据最严格的一支, 判据镜像 `_ctx` 的回退语义: 若某篇文章不存在银行与金科词汇同句共现, 则 `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 与 `_ctx` 缺实体窗口时的降级方式完全对称, 共享同一 `n_articles` 分母口径。地理判定部分 (`_is_homeprov`、省份匹配、拓扑不变量) 与另两轨完全共用同一套逻辑, 差异只体现在语调原语的文本截取粒度上。由于留篇门控是 full-only, `_ss` 轨的行宇宙同样是 full 留篇集的条件子集, 并进一步受同句共现判据约束而可能比 `_ctx` 更窄; 在早期试跑 T=2 数据规模下该轨情感解析样本量偏小是预期中的退化表现, 不代表口径错误。`_ss` 与 `_full`、`_ctx` 三者各自 just-identified 并排、互为稳健性、不分主次, 是判断"同省媒体正面倾斜"结论是否对文本截取粒度的选择敏感的第三重独立检验支路, 三条轨道情感变量绝不可混入同一个过度识别的 Hansen J 方程中联合估计。由于同句共现判据比实体窗口更严苛, `_ss` 轨解析出的同省样本量在多数情形下应弱于或等于 `_ctx`, 若观察到 `_ss` 轨系数方向与另两轨相反, 优先排查是否落入小样本/高回退率区间, 而非直接据此否定本地媒体偏袒的整体结论; 生产全量语料 (T=19) 下同句共现命中率显著高于早期试跑 T=2 数据, 该退化表现预期随语料规模扩大而缓解。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
<!-- rendered-citations:end -->
