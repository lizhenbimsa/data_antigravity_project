---
family_id: F162
columns:
- concern_score_ctx
- concern_score_full
- concern_score_ss
unit: 无量纲关切指数 (非负标度; 报道量对数与归一化负面强度之积)
formula: "concern_score = ln_news_coverage × (senti_ratio + 1) / 2; senti_ratio = (neg − pos) / (neg + pos); ln_news_coverage = ln(1 + n_articles) (log1p, 三轨共用的单一 track-agnostic 报道量列, n_articles = full-only 门控下的留篇篇数); 逐轨 {full, ctx, ss} 仅 senti_ratio 的 pos/neg 计数独立, 报道量对数分量三轨恒等"
producer: news_process/pipeline/panel/runner.py (main() 步骤7 综合指标段, 非 aggregate_panel 函数内) ; news_process/pipeline/panel/export.py (标签)
upstream:
- 24_herd_decay.parquet (df_exploded, stage 21 语义精筛后 article×bank 级 verified 集)
- 21_tone_llms.parquet (逐篇 LLM 情感标签 → 逐轨 pos/neg 计数)
citations:
- doi: 10.1016/j.jfineco.2016.01.032
  type: journal
  authors: Manela, A., & Moreira, A.
  year: 2017
  title: "News implied volatility and disaster concerns"
  venue: Journal of Financial Economics
  vol: 123
  issue: 1
  pages_or_artno: 137-162
- doi: 10.1093/qje/qjw024
  type: journal
  authors: Baker, S. R., Bloom, N., & Davis, S. J.
  year: 2016
  title: "Measuring economic policy uncertainty"
  venue: Quarterly Journal of Economics
  vol: 131
  issue: 4
  pages_or_artno: 1593-1636
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1016/j.finmar.2025.101002"
  type: "journal"
  authors: "Bie, S., Feng, G., Guo, N., & He, J."
  year: 2026
  title: "Can news predict firm bankruptcy?"
  venue: "Journal of Financial Markets"
  vol: "79"
  pages_or_artno: "101002"
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
本家族刻画的构念是"某家银行在某一年被新闻话语所笼罩的关切强度"(news-implied concern), 即把两条各自单薄、合在一起才有意义的信号乘在一起: 一条是该银行当年被媒体报道的密集程度 (报道量, 反映话题的显著性与被关注程度), 另一条是这些报道整体上偏负面还是偏正面 (情感极性, 反映舆论对该主体的忧虑或安心)。单看报道量无法区分"被夸"与"被批", 单看情感极性又无法区分"零星几篇的负面"与"铺天盖地的负面"; 关切指数把二者相乘, 只有当"报道又多、口径又负"两个条件同时满足时才取到高值, 从而把"银行被舆论集中盯上并且盯得不友好"这一状态从噪声里析出。它对应金融文本计量里一个成熟的思路: 媒体话语的显著性 (salience) 与效价 (valence) 是两个正交维度, 唯有交乘才能度量"被关切"这一二阶事件。构念上它更接近一个 concern / worry 指标而非纯情感分, 因此本家族独立于 F1 系列的纯 tone 家族存在, 不能被后者线性替代。

数据来源上, 关切指数是纯下游派生量, 不额外调用任何 LLM 或嵌入 API: 它在 stage 40 面板总装 (runner.py 的 main() 步骤7 综合指标段, 而非 encode 侧的 aggregate_panel 函数内) 计算, 消费上游 stage 21 语义精筛后的 verified article×bank 集 (经 24_herd_decay.parquet 汇入), 对每家银行每一年、逐轨统计正面篇数 pos 与负面篇数 neg; 而报道量分量并非逐轨各算, 而是取该银行-年的单一留篇篇数 n_articles 作对数。留篇口径遵循全仓 full-only 门控 (2026-06-29): 一篇报道是否算作"该银行的一篇金融科技相关报道"只由 full 轨的 LLM 判定决定, 由此确定的留篇篇数 n_articles 是一个 track-agnostic 的量, 三轨共用同一个 ln_news_coverage = ln(1 + n_articles) 作报道量分量。ctx 与 ss 轨的 pos/neg 计数才是在 full 留篇集之上逐轨各自累加的条件子集, 因此三列 concern_score 的轨间差异完全来自情感比 senti_ratio 的 pos/neg, 报道量对数分量在三轨间恒等、并不逐轨变化。

【方法学与计算】
计算分两截。第一截是情感比 senti_ratio = (neg − pos) / (neg + pos): 分子是负面减正面, 分母是正负总数 (中性不进此式), 取值落在闭区间 [−1, 1], 全正面时取 −1、正负相抵时取 0、全负面时取 +1。第二截把它平移压缩成一个 [0, 1] 的负面权重 (senti_ratio + 1) / 2: 0 代表口径彻底正面、0.5 代表中性平衡、1 代表口径彻底负面。第三步用该负面权重去缩放报道量的对数 ln_news_coverage = ln(1 + n_articles): 此处取的是 log1p 即自然对数作用在"篇数加一"上 (而非直接 ln(篇数)), 这样篇数为零时对数分量仍良定义为零、且在篇数很小时相比裸 ln 有一个不可忽略的 +1 平移; 报道量本身是该银行-年 full-only 门控下的单一留篇篇数 n_articles, 三轨共用同一列, 不随文本轨变化。取对数是标准的显著性衰减处理, 让"从 10 篇涨到 100 篇"与"从 100 篇涨到 1000 篇"带来同量级的边际关切, 避免极少数报道量巨大的头部银行-年支配整张面板。三步合成 concern_score = ln_news_coverage × (senti_ratio + 1) / 2, 其量纲是无量纲的非负标度: 报道越多且越负则越高, 报道虽多但口径正面则被负面权重压近零, 报道极少则被对数分量压近零。需要说明的是, 当某轨正负篇数皆为零时分母为零, senti_ratio 无定义, 该轨关切指数落为缺失而非零, 以免把"无报道"误当"无关切"混入回归。

关键的口径区分是三轨 full / ctx / ss: full = 标题 prepend 全文正文; ctx = 标题加实体上下文窗口; ss = 标题加"银行与金科同句 ±N 窗"。三条文本轨各自跑出各自的 pos/neg 情感计数 (报道量对数分量则三轨共用同一个 track-agnostic 的 ln_news_coverage), 因而三列 concern_score 是同一构念在三种文本作用域下的三次并排测量, 其轨间差异只来自情感比这一分量。按全仓铁律, 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨关切指数混进同一个 over-identified 的 Hansen J 过度识别检验 (混入会把"文本作用域选择"这一规格自由度伪装成额外的识别约束)。ss 轨的回退语义镜像 ctx: 若某篇无"银行∧金科"同句共现, 则 content_ss 退化为全文 body、ss_is_fallback=True 并共享 n_articles 分母, 因此在同句共现稀薄的样本上 concern_score_ss 会向 concern_score_full 收敛, 属预期退化而非缺陷。

【文献定位】
关切指数的构念直系于新闻文本计量中"以媒体话语度量市场关切"的传统。Manela 与 Moreira (2017) 从新闻文本构造新闻隐含波动率并将其与灾难关切 (disaster concerns) 直接挂钩, 证明媒体话语中的关切信号能预测风险溢价, 为"新闻可读出关切"提供了顶刊层面的构念背书; 本家族与之同宗, 区别在于本家族把关切拆成显著性 (报道量) 与效价 (负面比) 两个可分离分量再相乘, 而非端到端训练。Baker、Bloom 与 Davis (2016) 的经济政策不确定性指数同样是"以报道频次为骨架、以主题过滤为效价约束"的新闻计数式关切测度, 其方法论要旨——用报道量的对数化频次承载显著性、用文本条件承载效价——正是本关切指数把 ln 报道量与负面权重相乘的直接理论依据。Tetlock (2007) 则从另一侧提供效价分量的经典证据: 媒体负面语调本身携带对股价与基本面的预测信息, 说明"负面口径"不是噪声而是可度量的关切载体。三者共同界定了本家族的位置: 它是一个把 salience×valence 显式相乘、逐轨可复算的银行-年关切代理, 既非纯情感分 (缺显著性维度), 亦非纯报道量 (缺效价维度)。 晚近的同域研究进一步印证了本家族两个分量的立意, 但均须按降级口径引用。Bie、Feng、Guo 与 He (2026) 以 Dow Jones Newswires 全文新闻用大语言模型生成公司层情感预测变量, 对标 FinBERT 与词典模型, 证明新闻情感在财务变量之外对企业破产仍有增量预测力, 可作为「媒体负面情感的聚合测度携带主体困境信号」这一构念的前沿存在性参照, 支持本家族把负面强度作为关切/困境分量的立意; 但原文既无报道量分量、也无 (neg − pos)/(neg + pos) 式的归一化比, 其结果变量为二值、低频且有明确法律界定的破产事件, 而本项目样本内无破产银行 (中国商业银行破产极罕见), 故原文的预测性结论不可迁移为本家族任何一轨的效度证据; 其正负面判定亦与本项目的情感判定口径无关。Branzoli、Marchetti 与 Tarducci (2025) 构造媒体报道的语调测度, 并将其应用于银行融资条件这一银行层级的实证问题, 是「新闻语调到银行层级结果」这一链条的近期同域实践, 与本家族把逐轨 pos/neg 聚合到银行-年再与报道量对数相乘的应用域一致; 迁移边界在于原文国别为意大利、语料非中文新闻, 其语调测度不使用本项目的中文词典与投票口径, 无 full/ctx/ss 三轨文本切分, 结果变量为该国口径的银行融资条件, 与本项目在数据源与测度构造上均不对齐, 故只锚定应用链条的同域存在性, 不构成本家族任何一轨取值的效度背书。
## VAR: concern_score_ctx

【变体差分】
本列是关切指数在 ctx (上下文窗口) 文本轨上的测量。ctx 轨的作用域 = 标题 prepend 加实体上下文窗口 (content_ctx), 即只截取围绕目标银行实体附近的文本片段而非整篇正文, 因而对"该银行"这一主体更聚焦、能抵抗整篇正文里与该银行无关段落对情感与计数的稀释, 但代价是覆盖语义比 full 轨窄、可能漏掉正文远处才出现的关切线索。本列的 pos/neg 情感计数基于 ctx 轨自身的逐篇判定, 与 full 轨口径严格分离; 但报道量分量 ln_news_coverage 并非 ctx 轨自算, 而是三轨共用的单一 track-agnostic 列 ln(1 + n_articles), 其中 n_articles 是 full-only 门控下的留篇篇数, 故本列相对 full/ss 的差异只来自 senti_ratio 的 pos/neg, 报道量对数分量与另两轨恒等。其行宇宙受 full-only 门控约束——只有 full 轨已判为该银行金科报道的样本才可能进入 ctx 轨的条件测量, 故 concern_score_ctx 是 conditional-on-full 的稳健性轨而非独立留篇轨。因此当 full 轨判定为非金科报道时, 即便 ctx 窗内本身出现负面共现, 该样本也不进入 ctx 轨关切测量, 这一条件依赖须在解读斜率时明确。与 concern_score_full、concern_score_ss 的关系是三轨互为稳健性、不分主次: 三者度量的是同一关切构念在"整篇 / 实体窗 / 同句窗"三种文本作用域下的三次并排测量, 各自 just-identified, 严禁把三列混进同一个 over-identified 的 Hansen J 过度识别检验, 以免把文本作用域这一规格自由度伪装成额外的识别约束。须澄清的是, ctx 轨在实体窗内无银行实体命中时同样会触发整篇回退——ctx_materializer 的回退公理规定 content_ctx 在 extract_entity_context 无命中时退化为全文 body 并置 ctx_is_fallback=True, ss 轨的回退语义 (无"银行∧金科"同句共现时退化全文 body) 正是镜像 ctx 轨这一回退。因此 ctx 与 ss 的真正语义分野不在"是否回退整篇", 而在命中判据本身: ctx 轨以目标银行别名在实体窗内命中为判据, ss 轨以"银行∧金科同句共现"为更严的判据, 后者更挑剔故回退更频繁; 两轨都在各自判据落空时优雅退化为全文 body 而非落缺失。

## VAR: concern_score_full

【变体差分】
本列是关切指数在 full 文本轨上的测量, 也是三轨中承担留篇门控职能的那一轨。full 轨的作用域 = 标题 prepend 后的全文正文 (content_full), 因此 pos/neg 计数与报道量都基于整篇文章的完整语义, 覆盖面最宽、信息量最足, 但也最易被正文里与目标银行无关的段落带入噪声。按 full-only 门控 (2026-06-29), 一篇报道是否计入某银行-年的关切测量, 其"是否为一篇银行金科报道"的判定只看 full 轨的 LLM 判定 (llm_verified_full == True); 也就是说 full 轨单独定义了整张面板的行宇宙, 而 concern_score_ctx 与 concern_score_ss 都是在这一行宇宙内的条件测量, 二者不能反过来把 full 未留的样本纳入。正因如此, full 轨定义的留篇篇数 n_articles 即整张面板三轨共用的那个 track-agnostic 报道量, ln_news_coverage = ln(1 + n_articles) 三列取值恒等; full 列 concern_score 相对 ctx/ss 的唯一差异来自其情感比 senti_ratio 使用的是 full 轨逐篇 pos/neg。在解读上, concern_score_full 通常作为该构念信息量最完整的读数, 但它并非"主轨"而 ctx/ss 为"辅轨": 三列互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J 过度识别检验, 以免把文本作用域的选择伪装成识别约束。数值上须注意, 由于报道量对数分量三轨共用同一 ln(1 + n_articles), concern_score_full 相对 ctx/ss 的水平差异并非来自报道量 (三轨该分量恒等), 而完全由 full 轨的负面权重 (senti_ratio + 1)/2 相对另两轨的差异决定; 因此绝对水平的高低不意味着它更"准", 跨轨比较应以标准化后的系数而非原始关切水平为准。

## VAR: concern_score_ss

【变体差分】
本列是关切指数在 ss (同句窗) 文本轨上的测量, 口径最严。ss 轨的作用域 = 标题 prepend 加"银行与金融科技同句 ±N 窗"(content_ss, N 由 config/filtering.yaml 的 ss_sentence_radius 控制, 默认 1), 即只保留银行与金科词落在同一或相邻句子内的最小文本片段, 对"银行确实在谈金融科技"这一共现最挑剔, 因而在三轨中语义信噪比最高、但保留文本量最少。本列 pos/neg 情感计数基于 ss 轨自身逐篇判定, 口径严格同轨; 但报道量分量 ln_news_coverage 并非 ss 轨自算, 而是三轨共用的单一 track-agnostic 列 ln(1 + n_articles) (n_articles = full-only 门控留篇篇数), 故本列相对 full/ctx 的差异只来自 senti_ratio 的 pos/neg。其行宇宙同样受 full-only 门控约束, 是 conditional-on-full 的稳健性轨而非独立留篇轨。ss 轨独有的是回退语义, 镜像 ctx: 当某篇不存在"银行∧金科"同句共现时, content_ss 优雅退化为全文 body、ss_is_fallback 置 True 并共享 n_articles 分母; 因此在同句共现普遍稀薄的样本上, concern_score_ss 会向 concern_score_full 收敛, 这是设计内的优雅降级而非缺陷, 解读时须结合 ss_is_fallback 比例判断该轨的独立信息含量。与 concern_score_full、concern_score_ctx 的关系是三轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三列混进同一 over-identified 的 Hansen J 过度识别检验。由于同句窗保留文本最短、共现最挑剔, ss 轨的情感比 senti_ratio 最容易受小样本波动影响 (报道量对数分量因三轨共用 track-agnostic 的 n_articles 而不随轨变化, 不构成 ss 轨的额外波动来源), 在报道稀疏的银行-年上其 pos/neg 更易因正负皆零而落为缺失、或因无同句共现而触发整篇回退, 因此该列在稳健性梯子中承担的是"最严共现口径下结论是否依然成立"的角色, 与 full 的最宽口径、ctx 的中间口径共同界定关切构念对文本作用域选择的敏感区间。

<!-- rendered-citations:begin -->
Manela, A., & Moreira, A. (2017). News implied volatility and disaster concerns. Journal of Financial Economics, 123(1), 137-162. https://doi.org/10.1016/j.jfineco.2016.01.032
Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. Quarterly Journal of Economics, 131(4), 1593-1636. https://doi.org/10.1093/qje/qjw024
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Bie, S., Feng, G., Guo, N., & He, J. (2026). Can news predict firm bankruptcy?. Journal of Financial Markets, 79, 101002. https://doi.org/10.1016/j.finmar.2025.101002
Branzoli, N., Marchetti, S., & Tarducci, E. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. International Review of Economics & Finance, 104, 104564. https://doi.org/10.1016/j.iref.2025.104564
<!-- rendered-citations:end -->
