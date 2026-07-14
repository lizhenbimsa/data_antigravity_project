---
family_id: F584
columns:
- tone_market_media_ctx
- tone_market_media_full
- tone_market_media_ss
unit: 语调得分 (连续, 理论范围约 [-1,1]; bank-year 层面对文章级 LLM 投票分做算术均值聚合)
formula: 'tone_market_media{track} = mean(llm_vote_score{track} | 银行b, 年份y, _is_market==1); _is_market = 媒体(中文) ∈ (MARKET \ OFFICIAL), 即市场化媒体名单剔除与官方媒体名单重叠部分后的纯市场化子集; track ∈ {full, ctx, ss} 三轨独立聚合'
producer: pipeline\panel\attention_media.py (媒体政治取向维度⑤, market_media_frac / tone_market_media 族生成) ; pipeline\panel\export.py (面板列标签映射, L614/L623 等)
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss)
- config/bank_list.yaml 或媒体名单配置 (MARKET、OFFICIAL 媒体主办单位判据来源 NPPA 数据库)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: Giving Content to Investor Sentiment; The Role of Media in the Stock Market
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
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What Drives Media Slant? Evidence from U.S. Daily Newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
new_dois: []
---

## CORE

【构念与来源】
本家族衡量"市场化媒体"这一媒体政治取向子群体对目标银行的报道语调, 是媒体异质性 (media heterogeneity) 维度⑤"官方 vs 市场化"的正样本臂。中国新闻出版业存在鲜明的双元治理结构: 党报党刊等官方媒体承担宣传与舆论导向职能, 而都市报、财经类市场化媒体依赖广告与发行收入生存, 报道立场更贴近读者与投资者需求、批判性与独立性更强。You, Zhang & Zhang (2018, RFS) 在"Who Captures the Power of the Pen?"一文中系统论证了这一区分的经济后果: 市场化媒体的负面报道显著促进中国上市公司高管更替, 体现出媒体作为公司治理外部机制的"笔杆子的权力"; 而官方媒体的负面报道未见同等治理效力, 说明媒体的所有制/激励结构而非单纯报道数量决定其信息含量与市场反应。本家族的 `tone_market_media{track}` 正是在银行-年panel 层面复刻这一区分, 用以检验市场化媒体的语调是否比官方媒体或全样本更能预测、解释银行的金融科技化行为与市场后果。

产出该家族的核心操作化逻辑记录在 `pipeline\panel\attention_media.py` 维度⑤代码块: 媒体名单 MARKET (市场化媒体主办单位来自 NPPA — 国家新闻出版署主办单位备案数据库, 以"企业/商业集团"为主办性质判据) 与 OFFICIAL (官方媒体名单, 党政机关主办) 是两个独立构建的媒体来源集合。早期版本曾直接用 `isin(MARKET)` 作为哑变量, 但审计 (fix(omni-g-attention-02, 2026-06-11)) 发现两名单存在 82% 的 MARKET 媒体同时落入 OFFICIAL 集合 (重叠 386 家), 这会让 You, Zhang & Zhang (2018) 原本对立的构念被系统性重叠所稀释、掩盖真实的官方-市场对比。修复后的判据改为结构性互斥: `_is_market = 媒体(中文) ∈ (MARKET − OFFICIAL)`, 即只把"纯市场化" (既在市场化名单内、又不在官方名单内) 的媒体计入处理组; 对称地, `_is_official`(F145/F146 等姊妹家族) 也改为 `OFFICIAL − MARKET`。双判据媒体 (同时出现在两份名单里, OFF∩MKT) 既不计入 market 处理组、也不计入 official 处理组, 而是落入各自的对照组 (`nonoff`/`nonmkt`) 内。这一结构性互斥设计是理解本家族数值口径的前提: `tone_market_media{track}` 的样本不是"广义市场化倾向媒体"的报道, 而是"排他性市场化、无官方背景"的严格子样本, 与 `tone_official_media{track}` (F145 姊妹家族) 天然互不重叠, 二者之差 `tone_gap_market_nonmkt{track}` 是家族外的衍生对比列, 不在本家族内。

【方法学与计算】
计算管线分两步。第一步在文章级 dataframe 上标注 `_is_market` 哑变量 (0/1), 判据是文章的媒体来源字段 `媒体(中文)` 是否落入 `MARKET − OFFICIAL` 集合; 该哑变量与年份/银行无关, 是纯媒体来源属性, 与文章内容或情感无关。第二步按银行-年分组、按 `_is_market == 1` 过滤后, 对情感分数取组内算术均值: `tone_market_media{track} = df[df['_is_market']==1].groupby(['target_bank','year'])[f'llm_vote_score{track}'].mean()`。情感分数的上游是 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票共识 `llm_vote_score{track}`, 三分类 (负面/中性/正面) 映射为数值分数后取均值, 理论落域约 [-1, 1] (取决于三分类到数值的映射方式与实际样本分布, 实测均值通常更收敛)。若某银行-年组合内没有任何市场化媒体报道 (即 `_is_market==1` 的子样本为空), 该单元合并 (merge how='left') 后取值缺失 (NaN), 不做任何插补或借用其他轨道/其他媒体类别的数值, 这是稀疏媒体来源下的自然缺失, 并非数据管道错误。

三轨 (full/ctx/ss) 是本项目情感测量的正交稳健性设计, 而非从属或替代关系: full 轨以标题+正文全文作为 LLM 输入; ctx 轨以标题+围绕目标实体的窗口文本作为输入; ss 轨以标题+银行与金科词同句 (±N 句窗口, 默认基数 N=1) 共现文本作为输入, 若某篇文章不存在银行∧金科同句共现, 则 ss 轨回退为全文 body (镜像 ctx 轨回退语义), 并以 `ss_is_fallback` 标记该行是否处于回退状态, 分母 `n_articles` 与回退状态共享口径。三轨各自独立计算、并排呈现, 依项目铁律各自 just-identified、互为稳健性、不分主次, 严禁在同一个 over-identified 的 Hansen J 检验中把三轨混入同一组过度识别工具变量。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇文章是否被判定为"一篇有效的银行-金科报道"只看 `llm_verified_full == True`, ctx/ss 轨的行宇宙是 full 轨留篇集合的子集, 在此子集之上再各自独立计算 per-track 的市场化媒体语调均值, 因此 ctx/ss 轨样本量恒不大于 full 轨。

【文献定位】
本家族的理论基础直接来自 You, Zhang & Zhang (2018, The Review of Financial Studies) 关于中国媒体政治属性与公司治理效力的经典发现——市场化媒体因摆脱了官方宣传导向的激励约束, 其负面报道更能反映企业真实经营状况并触发实质性治理反应, 这一构念被本项目移植到银行-金融科技情境, 用以检验"谁在报道银行金融科技化"这一媒体所有制维度是否系统性调节语调-结果关系。在方法论谱系上, 本家族与 Fang & Peress (2009, JF) "媒体覆盖度降低信息不对称"、Tetlock (2007, JF) "媒体语调蕴含投资者情绪信息"共享同一文本情感测度框架 (`llm_vote_score`), 但本家族关注的不是覆盖度或整体语调水平, 而是媒体来源异质性对语调的调节效应, 概念上更接近 Gentzkow & Shapiro (2010, Econometrica) 关于媒体立场系统性受供给侧激励结构塑造 ("媒体倾向由什么驱动") 的论证逻辑——市场化媒体与官方媒体面对同一新闻事件产生系统性不同的语调, 根源在于二者不同的收入结构与问责机制, 而非随机噪音。此外, Holzman, Miller & Twedt (2023, The Accounting Review) 关于媒体权威性加权语调对盈余公告纪律效应的研究, 为本项目"媒体异质性应纳入语调测度"的整体设计提供了直接的方法学锚点 (本项目另设 `llm_vote_tone_mw{track}` 媒体权威加权语调族, 与本家族的媒体来源子群体切分是并列而非包含关系)。

## VAR: tone_market_media_ctx

【变体差分】
本列为 ctx (context) 轨: LLM 情感分数上游取自 `llm_vote_score_ctx`, 该分数由 stage 21 三家 LLM 对"标题 + 目标实体 (银行∧金科) 窗口文本"投票产生的多数共识分数, 而非全文。ctx 轨行宇宙受 full-only 留篇门控约束——只在 `llm_verified_full == True` 的文章子集上计算, 因此 `tone_market_media_ctx` 的样本量恒不超过 `tone_market_media_full`, 二者差异反映的是"聚焦实体窗口文本" vs "全文" 两种文本输入对市场化媒体语调测度的影响, 而非样本口径本身的差异。ctx 轨与 full 轨、ss 轨互为稳健性、并排 just-identified, 不构成主/次关系, 三者严禁混入同一 over-identified Hansen J 检验。若某银行-年组合下市场化媒体子样本在 ctx 轨判定为空 (可能因 `llm_vote_score_ctx` 缺失或该窗口 LLM 未通过 full-only 门控), 该单元取值缺失, 与 full 轨的缺失模式可能不完全重合。

ctx 轨的构造动机在于压缩噪音: 一篇长报道往往夹杂银行整体经营、宏观政策评论、无关业务板块等段落, 若直接用全文情感均值代表"该篇报道对银行金融科技化的语调", 可能被与金融科技完全无关的段落稀释或反向拉动。ctx 轨通过截取目标实体 (银行名+金科相关实体/词汇) 出现位置附近的窗口文本喂给 LLM, 试图让语调判断更贴近报道主题本身。市场化媒体的判定哑变量 `_is_market` 与轨道无关, 仍是纯粹的媒体来源属性 (媒体(中文) 字段是否落入 MARKET−OFFICIAL 集合), 三轨共享同一份媒体来源标注, 差异只体现在情感分数的文本来源上。使用者若同时报告 full 轨与 ctx 轨的市场化媒体语调, 应将二者解读为对同一构念的两种独立测量方式, 而非稳健性检验意义上"哪个更对", 二者高度一致时增强结论可信度, 不一致时应转向探讨窗口裁剪本身对该子样本的影响机制, 而非简单取舍。

## VAR: tone_market_media_full

【变体差分】
本列为 full 轨, 是本家族的 canonical/主轨: LLM 情感分数上游取自 `llm_vote_score_full`, 由三家 LLM 对"标题 + 全文正文"投票产生的多数共识分数; 该轨同时也是留篇门控的定义轨——`llm_verified_full == True` 直接决定一篇文章是否进入任一轨道的分母。在与 ctx/ss 两个轨道并排比较时, full 轨提供的是不做任何实体窗口裁剪或同句共现约束的最完整文本信息量, 覆盖面最广、样本量在同一银行-年内通常也最大 (ctx/ss 是其留篇子集)。项目铁律下 full/ctx/ss 三者各自独立计算、互为稳健性、不分主次呈现, 但在具体论文的 treatment 设计中 (如 P1 `bank_fintech_tone`), full 轨常被选为主设定用于基准回归, ctx/ss 作为稳健性检验轨, 这一"主设定选择"是论文层面的建模决策而非本家族测度本身赋予的等级差异。

full 轨对市场化媒体子群体的语调水平最贴近传统文献 (如 Tetlock 2007, JF) 处理整篇新闻文本的常规做法, 也是最不容易受到实体抽取或分句算法误差影响的轨道——只要一篇文章被判定为有效银行-金科报道 (`llm_verified_full==True`), 其全文语调分数就直接进入分母, 不存在因窗口裁剪或同句匹配失败而额外丢失样本的情形。这使得 `tone_market_media_full` 在稀疏媒体来源 (某些银行-年组合下市场化媒体报道本就不多) 情境下, 相对 ctx/ss 两轨更不容易出现因窗口/共现判据过严导致的额外缺失, 是三轨中样本覆盖最稳健的一支。使用者在解读跨银行、跨年份的市场化媒体语调差异时, 若发现某单元 full 轨有值而 ctx/ss 轨缺失, 应理解为窗口裁剪或同句共现判据未能命中, 而非该银行-年确无市场化媒体报道。

## VAR: tone_market_media_ss

【变体差分】
本列为 ss (same-sentence) 轨: LLM 情感分数上游取自 `llm_vote_score_ss`, 该分数由三家 LLM 对"标题 + 银行与金科词同句 (±N 句窗口, 生产口径 N=1, 见 `config/filtering.yaml::context_window.ss_sentence_radius`) 共现文本"投票产生。ss 轨回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则该文章的 `content_ss` 回退为全文 body, 并以 `ss_is_fallback=True` 标记, 与 ctx 轨共享 `n_articles` 分母口径; 若上游 `FINTECH_AC` 词典为 None, 则全部文章的 `*_is_fallback` 优雅降级为 True。ss 轨同样受 full-only 留篇门控约束, 行宇宙是 full 轨留篇集合的子集。ss 轨是三轨中文本粒度最细 (严格限定同句共现窗口) 的一轨, 理论上最能剥离与银行-金科议题无关的段落语调噪音, 但也因窗口更窄而更易产生回退或稀疏样本; 与 full、ctx 两轨严格并排、互为稳健性, 不分主次, 三者禁止混入同一 over-identified Hansen J 检验。

需特别注意 ss 轨与 ctx 轨的判据口径并不相同, 二者虽然都属于"实体聚焦"类文本裁剪, 但 ctx 轨用的是宽松的实体窗口 (`extract` 银行∧金科实体附近 N 词/句范围), 而 ss 轨用的是严格的同句共现判据 (`entity_context.py` 中判定银行名与金科词是否出现在同一自然句内), 两者的判据原语在代码库中是刻意区分、禁止互相复用的两套函数。当一篇市场化媒体报道虽然提及银行与金科词, 但二者分处不同句子 (例如首段提银行, 末段单独讨论金科政策) 时, 该篇文章会在 ss 轨触发回退 (使用全文 body 代替严格同句片段), 而在 ctx 轨仍可能命中窗口内共现, 二者对同一篇文章的处理结果可能不同。使用者若观察到 `tone_market_media_ss` 相对 `tone_market_media_ctx`、`tone_market_media_full` 呈现更大波动或更多缺失, 应首先核查该银行-年组合下市场化媒体报道的同句共现命中率, 而非直接归因于市场化媒体本身语调不稳定。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving Content to Investor Sentiment; The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Gentzkow, M., & Shapiro, J. M. (2010). What Drives Media Slant? Evidence from U.S. Daily Newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
<!-- rendered-citations:end -->
