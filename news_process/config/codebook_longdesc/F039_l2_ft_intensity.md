---
family_id: F039
columns:
- avg_ft_intensity
- avg_ft_intensity_ctx
- avg_ft_intensity_ctx_std
- avg_ft_intensity_full
- avg_ft_intensity_full_std
- avg_ft_intensity_lg
- avg_ft_intensity_lg_ctx
- avg_ft_intensity_lg_ctx_std
- avg_ft_intensity_lg_full
- avg_ft_intensity_lg_full_std
- avg_ft_intensity_lg_ss
- avg_ft_intensity_lg_ss_std
- avg_ft_intensity_lg_std
- avg_ft_intensity_ss
- avg_ft_intensity_ss_std
- avg_ft_intensity_std
unit: 连续技术强度得分 (无量纲; 文章级 IDF×语义纯度加权对数词频得分的银行-年均值 / 组内样本标准差)
formula: "文章级 Score_d = Σ_i [(1 + ln TF_di) / (1 + ln L_d)] × W_i (仅对 TF_di > 0 的关键词 i 求和), 其中 W_i = IDF_i × CosSim_scaled_i, raw IDF = log10(N_total/(1+df_i)); 面板级 avg_ft_intensity[_lg][_full/_ctx/_ss] = mean(fintech_intensity_score[_lg][_full/_ctx/_ss]), 对应 *_std = std(ddof=1), 按 groupby(target_bank, year) 聚合; 无后缀列 ≡ _full 别名, avg_ft_intensity_lg ≡ avg_ft_intensity_lg_full 别名"
producer: news_process/pipeline/panel/encode.py::build_aggregation_dict + aggregate_panel (bank-year 聚合入口); news_process/pipeline/filtering/fintech_intensity.py (文章级得分, thin shim 15_fintech_intensity.py)
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score_full/ctx/ss 及 _lg 孪生族 + intensity_verified_*)
- 14_news_with_ctx.parquet (content_full/content_ctx/content_ss 三轨打分语料, stage 14 物化)
- 12_fintech_news_full.parquet (全量含非金科参考语料, 仅供全局 IDF)
citations:
- doi: 10.1111/jbfa.70056
  type: journal
  authors: Taraj, I., & Wahlström, R. R.
  year: 2026
  title: "Narratives contextualizing numeric disclosures: Insights from earnings calls"
  venue: "Journal of Business Finance & Accounting"
  vol: 53
  issue: 3
  pages_or_artno: 1263-1286
- doi: 10.1111/1467-8551.12853
  type: journal
  authors: Cai, W., Shi, W., & Jiang, F.
  year: 2025
  title: "Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance"
  venue: "British Journal of Management"
  vol: 36
  issue: 1
  pages_or_artno: 361-382
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: "SSRN Working Paper"
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: "Journal of Economic Perspectives"
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1016/j.jcorpfin.2024.102593
  type: journal
  authors: Wang, Y., & Wu, S.
  year: 2024
  title: "Impact of mobile banking on small business lending after bank branch closures"
  venue: "Journal of Corporate Finance"
  vol: 87
  pages_or_artno: "102593"
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: "The Review of Economic Studies"
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aeri.20210236
  type: journal
  authors: Roth, J.
  year: 2022
  title: "Pretest with caution: Event-study estimates after testing for parallel trends"
  venue: "American Economic Review: Insights"
  vol: 4
  issue: 3
  pages_or_artno: 305-322
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: "The Review of Financial Studies"
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: "American Economic Review"
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: "The Quarterly Journal of Economics"
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: "W.E. Upjohn Institute for Employment Research"
new_dois:
- 10.1093/rfs/hhaa079
---

## CORE

【构念与来源】
本家族度量的构念是银行-年层面的金融科技技术强度 (fintech technical intensity): 对一家银行当年被媒体报道且通过金科相关判定的文章集合, 每篇文章先得到一个连续的技术含金量得分, 再在银行-年格内取均值 (avg_ 前缀各列) 与样本标准差 (_std 后缀各列), 分别刻画该银行当年金科报道的平均硬核程度与篇际离散程度。它与上游 stage 12 的词典二元判定在构念上分居两端: 二元判定回答的是有没有 (extensive margin, 一篇文章是否属于金融科技报道), 本家族回答的是有多实 (intensive margin, 这篇报道谈金融科技谈得有多深、用词有多硬核)。用大白话说, 光数关键词很容易被注水稿件骗到, 一篇通稿把支付、线上这类泛化词堆十遍, 和一篇认真讨论联邦学习、隐私计算落地细节的深度稿, 在二元开关下毫无区别; 本家族的连续得分就是为了把真干事和喊口号区分开。设计上明确对准三类系统性偏差: 其一是复读机刷分, 同一关键词在一篇稿件里反复出现不应线性抬分; 其二是长文体量偏差, 长文不应仅凭字数多而自动得高分; 其三是术语区分度缺失, 篇篇都出现的泛化词与高稀缺高区分度的专业术语不应等权。方法学上, 这一从种子词典出发、用嵌入空间几何结构把词条语义纯度折进权重、再对文档打连续分的路线, 锚定 Li, Mai, Shen 与 Yan (2021) 用机器学习从文本测度公司文化的范式: 潜在构念的强度不由研究者逐篇主观打分, 而由种子词与词向量共同定义, 从而兼得词典法的可解释性与嵌入法的语义分辨率。在披露文献一侧, Cai, Shi 与 Jiang (2025) 表明战略披露强度这一连续测度承载了超出披露与否的增量信息, 且与公司风险承担和绩效系统相关, 其对空谈与实质披露的区分正是本家族在银行金科语境下要解决的测量问题; Wang 与 Wu (2024) 关于移动银行在网点收缩后重塑小微信贷可得性的证据, 则说明银行金融科技活动的强弱具有可识别的真实经济后果, 为把媒体报道中的技术强度作为银行金科动态的文本代理提供外部效度动机; Taraj 与 Wahlström (2026) 强调数字信息的解读依赖其叙事语境, 这一洞见同样适用于关键词信号 — 同一个金科术语出现在针对目标银行的段落与出现在行业泛谈中含义不同, 这正是本家族三轨文本口径 (full/ctx/ss) 存在的构念理由。

数据来源与链路: 原始媒体语料经 00 预处理、11 银行实体识别、12 金科词典二元分类 (1506 词 Aho-Corasick 词典)、13 银行×金科邻近共现硬过滤、14 三轨文本物化 (content_full/content_ctx/content_ss, 标题 prepend 进正文首句) 之后, 在 15_fintech_intensity 阶段对每篇金科文章逐轨打分, 产出文章级 fintech_intensity_score_full/ctx/ss 及其 _lg 嵌入孪生族与 intensity_verified_* 验证指示; 面板层由 pipeline/panel/encode.py 的 build_aggregation_dict 注册聚合入口、aggregate_panel 按 groupby(target_bank, year) 收敛为本家族 16 列。这一文章级得分先行、银行×年均值收敛的聚合口径, 与 Marchetti, Tarducci 与 Branzoli (2025) 在意大利银行融资条件研究中对媒体覆盖测度采用的银行×时间聚合口径同构。

【方法学与计算】
文章级得分由三个模块串联, 全部实现在 pipeline/filtering/fintech_intensity.py。模块 A 计算全局文档频率: 参考语料取 12_fintech_news_full, 即包含非金科文章的全量语料 — 这是刻意为之, 若改用金科子集作参考语料, 人人都谈金科的子集内金科词不再稀缺, IDF 的区分度会整体塌缩; 语料先按标题与日期二元组去重为唯一文档, 再用 jieba 整词统计每个词典关键词的文档频率 df 与文档总数 N_total, 与打分端同一分词器同一口径, 避免 Aho-Corasick 子串计数与 jieba 整词计数之间的系统性错位; 词典中含空格或顿号、jieba 整词切分下永不可命中的极少数词条被从权重宇宙剔除并在日志显式披露。模块 B 构造关键词综合权重, 分三步: 第一步 IDF, raw IDF = log10(N_total/(1+df)), 均值归一化后按默认百分之一与百分之九十九分位 Winsorize 压尾, 防个别极端稀缺词独占权重; 第二步语义纯度, 用 co-primary 双 API 嵌入模型 (canonical 无后缀槽为 Qwen3-Embedding-8B, 4096 维, 硅基流动端点; _lg 槽为 text-embedding-3-large, 3072 维, OpenAI 系经 yunwu 端点) 各自把整个关键词表一次性编码, 以 IDF 为权取普通加权质心, 计算每个关键词对质心的余弦相似度, 再经 min-max 重标定并设下限 floor (默认 0.1) 缓解嵌入空间各向异性造成的余弦区间压缩 — 须澄清两点: 该实现名义上借鉴句向量加权质心思想, 但既无平滑逆频率权重也无首主成分去除, 实际是 IDF 加权普通质心; 各向异性处理亦属工程化经验重标定而非正式校准方法; 第三步预乘, W_i = IDF_i × CosSim_scaled_i, 即稀缺度乘语义纯粹度。模块 C 逐文档打分, 核公式为双重对数: Score_d = Σ_i [(1 + ln TF_di) / (1 + ln L_d)] × W_i, 求和只遍历该文档中词频大于零的关键词 — 分子对词频取对数抑制复读机刷分, 分母对文长取对数抑制长文体量偏差。此外设二次熔断: 一篇文档中去重后的命中关键词种数低于阈值 (默认 2) 时, 该轨得分记为 NaN 且 intensity_verified 记 False — NaN 在下游银行-年均值中被自动剔除, 这是刻意设计: 只孤立提到一两个金科词的文章很可能只是顺带一提, 把它记为零强度会系统性拉低银行年均值, 记缺失则让均值成为通过验证文章上的条件均值。

有两处工程细节直接决定得分的可复现性与轨间可比性, 须专门澄清。其一是分词器单源: 全局 df 统计与逐文档 TF 打分共用同一 jieba 注入态 (打分前把全部可命中关键词经 add_word 注入) 与同一可匹配词集, 因此同一个关键词在 df 分母与 TF 分子里的出现定义严格一致; 这是刻意纠正早期实现的一处系统性偏差: 若 df 沿用 Aho-Corasick 子串扫描 (允许子串误命中与重叠双计) 而 TF 走 jieba 整词, 子串高发词的 df 会系统性偏大、IDF 偏低, 违反同语料同口径原则。其二是文长归一化的轨道自洽: 三轨的文长一律按各自打分文本 (content_full/content_ctx/content_ss) 的实际字符长度逐篇重算 (下限截断为 1), 绝不拿全文长度去归一化窗口化短文本 — 否则短窗文本会被过长的全文分母系统性压低得分, 破坏三轨可比; 仅在 full 轨降级回退用原始内容列打分且上游预算的 doc_length 列存在时, 才沿用该预算列, 正常生产路径 (stage 14 已物化 content_full) 不触发此回退。此外, 权重的可审计性是本方法相对端到端嵌入打分的关键优势: 打分阶段会把综合权重排序后的头部硬核词与尾部泛化词连同各自的 IDF 分量与余弦纯度分量写入日志, 每篇文章的得分都能逐词拆回具体命中了哪些词、各词权重几何来源, 便于人工核对权重是否合理、稳健性检验时精确定位轨间或模型间分歧的来源。

退化与失败路径是 fail-loud 设计: 文档频率为空、IDF 均值非正、余弦全同等数据退化情形会逐一以 error 级日志披露并降级为纯词频或纯 IDF 权重, 防止同名列在无声中改变语义; 而嵌入 API 硬失败不走降级 — 失败侧嵌入 spec 的三轨得分整体置 NaN, 且 canonical Qwen 族与 _lg 族严格执行 both-or-neither parity, 任一侧失败两族同置缺失, 绝不留单边孤儿列, 防止付双倍嵌入成本却在面板层丢掉一轨。面板聚合层由 valid_agg 机制按源列存在性过滤: 旧单轨 parquet 或 _lg 未播种时, 对应面板列优雅缺席而不抛 KeyError。均值用 pandas groupby mean, NaN 自动剔除; 标准差用 groupby std, 即除以 n-1 的样本标准差, 组内有效篇数不足 2 时为 NaN。命名上有两处历史别名须知: 面板无后缀 avg_ft_intensity 与 avg_ft_intensity_std 的源列是文章级 fintech_intensity_score, 而该列本身就是 stage 15 为向后兼容保留的 _full 别名, 故无后缀面板列与 _full 面板列数值恒等; 对称地, avg_ft_intensity_lg 与 avg_ft_intensity_lg_std 的源列即 fintech_intensity_score_lg_full, 恒等于 _lg_full 面板列。行宇宙口径遵循 2026-06-29 的 full-only 留篇门控: 一篇文章是否计入银行金科报道面板宇宙只看 llm_verified_full, ctx 与 ss 是 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, 各轨列在该宇宙上照算。ss 轨回退语义镜像 ctx: 当一篇文章不存在银行与金科词的同句共现 (±1 句窗口, 由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 注意它与 stage 13 硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的配置键) 时, content_ss 回退为全文 body 且 ss_is_fallback 记 True, 与 full 共享 n_articles 分母; 金科自动机不可用时全体回退、优雅降级不崩。共现判定采用不对称口径: 银行侧经过否定与短名过滤, 金科侧为裸 Aho-Corasick 词典命中。

【文献定位】
在文本即数据的测量谱系里, 本家族处于词典计数法与纯嵌入法之间的加权词典层: 相对朴素词频占比, 它引入 IDF 稀缺度与嵌入语义纯度双重加权和双重对数归一; 相对端到端嵌入打分, 它保留了逐词可追溯的权重分解, 每篇文章的得分可以拆回到具体命中了哪些词、各词权重几何, 便于审计与稳健性检验。Li, Mai, Shen 与 Yan (2021) 是这一层的方法学源头, 其从种子词出发用词向量扩展并度量构念强度的做法为本家族的语义纯度权重提供了直接先例, 也确立了让潜在构念强度由种子词与词向量共同定义、而非研究者逐篇主观打分的可复现测量原则。Cai, Shi 与 Jiang (2025) 与 Taraj 与 Wahlström (2026) 分别从披露强度与叙事语境两个方向支持连续强度测度与语境敏感口径的信息增量: 前者证明连续强度承载超出二元披露与否的增量, 后者证明术语与数字信号的含义取决于其所处叙事语境, 二者合起来同时为本家族的连续得分设计与三轨语境口径提供文献支撑。Marchetti, Tarducci 与 Branzoli (2025) 提供了银行媒体测度按银行×时间聚合的操作先例; Wang 与 Wu (2024) 则从真实效应端说明银行金科强度差异值得被测量, 为把文本强度作为银行金科动态代理提供外部效度。均值与标准差成对报告的设计, 使本家族同时覆盖强度的位置参数与离散参数: 前者用于回答某银行金科报道平均有多硬核, 后者用于回答其报道口径是整齐划一还是深浅两极分化, 二者在下游回归中承载不同构念, 不可互相替代。

【识别策略定位】
本家族在论文组合中的识别角色须分三层澄清。第一层, 与 P2 注意力论文的同源关系: P2 的处理变量 attention_index_full 是对同一底层文章级金科强度信号取 ln(1+总和) 的总量式变换, 本家族是对同一信号取均值的强度式变换, 两者派生自同一媒体语料; 均值式变换对报道篇数免疫, 恰好把内容强度从覆盖体量中剥离出来, 这既是本家族相对总量测度的识别优势, 也正是它不能充当同源处理变量之结局变量的深层原因 — 若把与隔壁论文 treatment 派生自同一语料的文本量设为 Y, 估计到的很可能是共同媒体覆盖因子而非真实公司行为, 因为分子分母同随覆盖量涨落, 系数吸收的是覆盖强度而非因果传导。P2 图表层在 attention_index 列缺席的防御路径下会以本家族列作代理并在图题显式注明。第二层, llm_peer 方法学论文中的角色变迁: avg_ft_intensity_full 曾短暂被设为该篇主 outcome, 但顶刊口径重审 (PORT SAL-3, 2026-06-14) 依上述共同覆盖因子的识别隐患确认它与 P2 的处理变量同源, 故主 outcome 改回真实经济结局 roa, 本家族降级为 first-stage 机制佐证 (mechanism_evidence), 用于展示同业语调工具经由本行金科报道强度传导的中间通道, 但明确不作 co-equal headline, 论文正文须披露该同源性。第三层, 工具变量扩展: 面板 IV 三引擎各自隔离一类外生变异 — 同组 leave-one-out 均值 (剔除本行、只留同业变异, 阻断本行金科强度对同业均值的反向污染) 、广义 Bartik (份额 share × 冲击 shift 的加权暴露, share 为共现或暴露权重、shift 为银行测度) 、媒体来源 house-style 暴露 (捕捉特定媒体行文风格的外生冲击) — 对面板测度族提供工具列。其中 Bartik 型工具的效度论证遵循 shift-share 文献的双路径框架: 份额外生路径与 Rotemberg 权重诊断见 Goldsmith-Pinkham, Sorkin 与 Swift (2020) — 该框架下识别力集中于少数高 Rotemberg 权重的份额, 一旦某份额出现负 Rotemberg 权重即提示设定误置、须逐份额审查其外生性而非仅看总体 F 统计量; 冲击外生 (即冲击近似随机、可等价推断) 路径见 Borusyak, Hull 与 Jaravel (2022); 推断与标准误的组内相关修正见 Adão, Kolesár 与 Morales (2019); 排除约束的放松条件见 Apfel (2024); 含 incomplete-shares 重归一选择的操作检查表见 Borusyak, Hull 与 Jaravel (2025); 范式源头为 Bartik (1991)。P2 事件研究图涉及本家族代理路径时, 平行趋势预检验后估计量的条件偏差问题应记 Roth (2022) 的警告。口径铁律必须复述: 三轨 full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; canonical Qwen 轨与 _lg 轨是 co-primary 双轨, 同为主测度、互为稳健性, 同样各自 just-identified 并排、禁混同一 over-identified Hansen J。Hahn, Kuersteiner, Santos 与 Willigrod (2024) 对 shift-share 设计中过度识别检验失效机理的分析为该铁律提供计量支撑: 把构念高度相关、测量误差结构同源的多个变体塞进同一过度识别系统, 检验的拒绝无法区分工具无效与测度间机械相关, just-identified 并排才是变体族的正确用法。

【与相邻测度的构念区分】
与 n_articles、fintech_share、attention_pct 的区分: 后三者是数量与占比测度, 只问报道了多少, 本家族问报道得多实, 分居数量与质量两个维度。与 avg_ft_word_ratio (相对披露密度) 的区分: 该列是金科词的原始词频占比, 无 IDF 加权、无语义纯度加权、无对数抑制, 可视作本家族的未加权朴素对照臂 — 两者一起报告时, 差异恰好度量加权方案本身的贡献。与 attention_index_full 的区分: 总量对报道篇数敏感, 均值对篇数不敏感, 一家被十篇浅稿覆盖的银行总量可以很高而均值很低, 两者回答注意力体量与内容强度两个不同问题, 前文所述同源披露正因此而必要。与情感三法 (stage 21 LLM / 22 词典 / 23 BERT) 的区分是构念上最易混淆的一处: 情感测度的是报道对银行的态度极性 (正面/中性/负面), 本家族测度的是报道谈金科谈得多硬核, 两者正交 — 一篇技术含金量极高的深度稿, 其语调既可能是褒扬也可能是质疑, 强度得分不随语调翻转而变, 故本家族绝不可当作情感代理, 反之亦然; 二者如需同入回归应各占一列、不构成同一构念的冗余测量。与 policy_alignment (stage 16, 同为嵌入类测度) 的区分在于语义锚不同: policy_alignment 计算文章向量对政策文本向量的余弦贴合度, 度量报道与政策话语的对齐; 本家族的余弦只用于给关键词赋语义纯度权重、锚点是金科关键词表质心而非政策文本, 度量的是技术密度, 两者共用同一嵌入引擎却指向完全不同的构念, 不可因同源于嵌入而误判为相关测度。与 P3 实质性分类 (substance) 的区分: 那是 LLM 对文章的离散类别判定, 本家族是词典加嵌入的连续得分, 测量仪器与标度均不同。与 fintech_in_title、target_bank_in_title 等表层信号的区分: 标题信号只看位置显著性, 不看内容密度。与 semantic_staleness 族的区分: 陈旧度度量的是文本相对历史语料的新颖性, 与技术强度正交。最后, intensity_verified_* 指示列族记录每篇文章是否通过熔断验证, 是理解本家族 NaN 语义的伴生列: 均值的分母不是全部金科文章, 而是通过验证的文章, 因此本家族衡量的始终是有实质金科内容那部分报道的条件强度, 而非全部报道的无条件强度。

【已知局限与稳健性梯子】
第一, 词典依赖: 种子词典固定 1506 词, 对新兴术语存在收录滞后, 词典更新即换测度, 须受控重生; jieba 锁定 0.42.1 保证跨 run 分词确定性, 但整词统计对未登录的新组合词不敏感; 不可命中词条的剔除虽有日志披露, 仍意味着权重宇宙略小于词典全集。第二, 嵌入依赖: 语义纯度权重来自外部嵌入 API, 复现性由 LLMCache 缓存锚定, 离线守卫开启时缓存未命中即抛错而非静默调用, 保证零成本字节级复现; 换嵌入模型等价于换测度, 属于受控全量重生事项并须在论文中披露。须进一步披露语义纯度权重本身的构造性质: 该权重名义上借鉴句向量加权质心思想, 但实现上既无平滑逆频率权重也无首主成分去除, 实为 IDF 加权普通质心; 各向异性的 min-max 加下限重标定亦属工程化经验处理而非正式校准方法 — 因此语义纯度维度是一套可解释但非理论最优的启发式权重, 其对具体构造 (质心口径、下限取值、嵌入空间) 的敏感性, 正是 co-primary 双嵌入并排要暴露的自由度: 若某结论只在一个嵌入空间下成立, 即提示它受该启发式构造驱动而非真正稳健。第三, 研究者自由度: Winsorize 分位、各向异性下限、熔断阈值均为默认参数, 其取值未做全格点敏感性物化; 熔断把低命中文章记缺失而非零是刻意的选择性设计, 解释均值时必须记住这是条件均值, 该条件在轨道间不同 (窗口化轨道文本短, 更易触发熔断)。第四, 标准差列在组内有效篇数不足 2 时缺失, 报道稀少的小银行与早年份系统性缺失, 缺失机制与报道量相关而非随机, 回归中使用离散度臂须正视样本选择。第五, 开发盘为两年短窗试跑, 组内篇数少时均值与标准差的抽样噪声大, 生产十九年窗下方可谈稳定推断。第六, 参考语料依赖: 全局 IDF 建立在 stage 12 全量语料之上, 这是刻意选择以保区分度, 但也意味着 IDF 权重对参考语料构成敏感, 语料年份覆盖或媒体来源结构变化会平移权重, 换语料同样等价于换测度; 全量语料按标题与日期去重为唯一文档后统计 df, 与面板端 fintech_share 的去重计数基对齐, 避免同一物理文档因跨媒体转载或银行爆炸行被重复计入 df 分子与文档总数分母。稳健性梯子结构: 三轨 (full/ctx/ss) 乘 co-primary 双嵌入 (Qwen 与 _lg) 共六个测度单元, 每格配均值与标准差两臂, 单元之间互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; avg_ft_word_ratio 作为无加权对照臂在梯子之外提供加权方案的增量证据。嵌入双轨在同一 run 的值层执行 both-or-neither parity, 嵌入失败导致的缺失总是成对出现, 不留单边孤儿值 (legacy 缺列路径另论: 旧单轨 parquet 或 _lg 未播种时由 valid_agg 缺源跳过, _lg 面板列整列缺席而 Qwen 列照在, 属预期而非 parity 违约) — 须注意 parity 是一柄双刃: parity 杜绝了付双倍嵌入成本却在面板层丢一轨的风险, 但代价是任一侧嵌入 API 硬失败会连坐置另一侧为 NaN, 属刻意的 fail-loud 设计, 因此某格缺失时应先排查两族是否成对缺席、检查嵌入播种状态, 而非误判为某一嵌入测度本身失效。

## VAR: avg_ft_intensity

【变体差分】
无后缀 legacy 别名列, 均值臂。聚合入口注册为文章级 fintech_intensity_score 的银行-年均值, 而该源列本身就是 stage 15 为向后兼容保留的 _full 轨别名 — 因此本列与 avg_ft_intensity_full 数值恒等, 是同一底层信号的两个聚合入口, 差异仅在列名。保留动机: 三轨化 (v3.6.0) 之前的历史模板、golden 快照与旧下游脚本按无后缀名引用, 直接删除会断链; 该别名设计与 _lg 侧的 avg_ft_intensity_lg 恒等 avg_ft_intensity_lg_full 完全对称, 两侧对称是刻意的工程约定。使用规范: 新增下游代码应显式引用 avg_ft_intensity_full, 把本列视为兼容通道而非独立测度; 尤其禁止把本列与 _full 列当作两个不同测度同时放进同一回归或同一稳健性表 — 它们不是梯子的两臂, 而是同一列的两个名字, 同时纳入会造成完全共线且虚增测度数。无后缀不代表主列: canonical headline 语义由 _full 显式后缀列承载, 本列是历史命名产物, 这一点与政治词权重族中无后缀列的定位口径一致。轨道语义、full-only 留篇门控、熔断 NaN 剔除、Qwen canonical 嵌入权重、valid_agg 缺源跳过等全部口径与 avg_ft_intensity_full 节所述相同, 均值分母同为通过验证文章、故本列亦为条件均值, 不再重复。须补充一点辨识: 本列与 _lg 侧的无后缀别名 avg_ft_intensity_lg 都属无后缀命名空间, 却分属 canonical 与 _lg 两个平权嵌入轨、数值不同, 各自恒等于己方的 _full 面板列, 两条恒等链彼此独立, 不可混为一谈; 本列与其伴生离散别名 avg_ft_intensity_std 成对保留, 使无后缀命名空间内位置与离散两参数俱全, 便于按旧列名书写的模板一次取齐。

## VAR: avg_ft_intensity_ctx

【变体差分】
ctx 轨均值臂, canonical Qwen 嵌入权重。打分文本为 content_ctx, 即 prepend 标题加目标银行实体上下文窗口 — 只保留银行实体出现位置附近的句子片段。相对 full 轨的全文打分, 它剔除了同一篇文章里与目标银行无关的段落, 例如多银行盘点稿中他行的部分、行业综述里的泛谈段落, 使技术强度信号更贴近该银行自身被谈及时的技术密度; 这正是叙事语境影响数字与术语信息含义这一洞见在轨道设计上的落地。行宇宙为 conditional-on-full: 面板留篇由 llm_verified_full 决定, ctx 轨只是在同一文章集合上换文本口径重算, 不改变哪些文章入面板。关键词权重 W_i 与 full 轨完全共享 (同一全局 IDF、同一 Qwen 语义纯度质心), 轨间差异全部来自窗口化后的词频 TF 与文长 L_d; 文长按 content_ctx 的实际长度重算而非借用全文长度。与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。解释注意: 窗口化使文本变短, 双重对数归一虽已抑制文长效应, 但短文本中去重命中词种数更容易低于熔断阈值, 导致 ctx 轨的未验证 (NaN) 比例结构性高于 full 轨, 组内条件均值的选择面不同; 因此跨轨比较应侧重方向与显著性而非水平值差异。

## VAR: avg_ft_intensity_ctx_std

【变体差分】
ctx 轨离散度臂。对同一银行-年内全部通过熔断验证的 ctx 轨文章级得分取样本标准差 (groupby std, 除以 n-1), 度量该银行当年金科报道在银行实体上下文口径下的篇际强度离散: 数值大意味着该行的金科报道在硬核深度稿与浅提及稿之间两极分化, 数值小则报道口径整齐。与均值臂 avg_ft_intensity_ctx 同源同轨, 构念上一个是位置参数一个是离散参数, 两者可同入一表但回答不同问题, 不构成重复测度。组内有效篇数不足 2 时为 NaN — 报道稀少的小银行与早年份会系统性缺失, 该缺失机制与报道量相关而非随机, 使用时须正视样本选择而不能当作完全随机缺失处理。此外 ctx 轨的窗口化熔断选择性 (短文本更易记 NaN, 见均值臂一节) 会同步收窄进入标准差计算的样本, 令本列的有效篇数进一步小于 full 轨对应格, 离散度估计的抽样噪声相应更大, 短面板窗下尤须谨慎。三轨的离散度臂之间同样互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。本列与其 _lg 对偶 avg_ft_intensity_lg_ctx_std 逐格文章集合一致、仅嵌入模型不同, 并读可判断 ctx 轨离散度是否稳健于嵌入空间选择; 报告离散臂时须与均值臂 avg_ft_intensity_ctx 成对呈现, 位置与离散两个参数缺一不可完整刻画该行报道结构。

## VAR: avg_ft_intensity_full

【变体差分】
本家族 canonical headline 列, core 列。full 轨均值臂: 打分文本 content_full 为 prepend 标题加全文正文, 源列 fintech_intensity_score_full, 关键词语义纯度权重来自 canonical 无后缀嵌入槽 Qwen3-Embedding-8B (4096 维, 硅基流动 API), 面板值为银行-年内通过熔断验证文章的得分均值。选它作 canonical 的理由有三层。第一, 口径一致性: 2026-06-29 起面板的留篇门控是 full-only — 一篇文章是否计入银行金科报道宇宙只看 llm_verified_full, full 轨的文本口径与定义行宇宙的门控口径完全同轨, 测度与宇宙自洽; ctx 与 ss 是 conditional-on-full 的稳健性轨, 其行宇宙是 full 留篇集的子集。第二, 信息完整性: 全文口径保留文章的全部技术内容信号, 窗口化轨道以降噪为目的牺牲了部分召回, 全文口径的熔断触发率最低、条件均值的选择面最宽, 因此在六个测度单元里本列的有效样本面最接近全信息口径。第三, 历史连续性: 无后缀 legacy 列 avg_ft_intensity 即本列的别名, 数值恒等, 旧模板与新代码经由本列对齐。识别角色上本列是家族中承担论文级职能最多的一列: 在 llm_peer 方法学论文中作 first-stage 机制佐证 (mechanism_evidence), 展示同业语调工具经由本行金科报道强度传导的中间通道 — 但因与 P2 注意力论文的处理变量 attention_index_full 派生自同一媒体语料 (均值式与总量式两种变换), 经 PORT SAL-3 顶刊口径重审后明确不作 headline outcome, 该同源性须在论文正文披露; 在 P2 图表层, 本列是 attention_index 缺席时的防御性代理, 命中代理路径时图题会显式注明。与 avg_ft_intensity_lg_full 构成 co-primary 双轨对偶: 两列同为主测度、互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 嵌入层执行 both-or-neither parity, 任一侧嵌入失败则两族同置 NaN, 不存在本列有值而 _lg 对偶缺失的单边状态。数值语义提醒: 本列均值的分母是通过验证 (去重命中词种数达到阈值) 的文章而非全部金科文章, 熔断把顺带一提的浅稿记缺失而非零分, 因此本列衡量的是有实质金科内容的报道的平均强度, 与全部报道的平均强度构念不同; 由于该验证条件在各轨阈值触发率不同, 跨轨比较本列与 ctx、ss 对应列时应侧重方向与显著性而非绝对水平。与其伴生的 avg_ft_intensity_full_std 提供同格离散参数, 与总量式的 attention_index_full 相比则对报道篇数不敏感 — 一家银行被十篇浅稿覆盖时, 本列的均值不会因篇数多而抬高, 这一对篇数的免疫性正是把它与注意力体量测度区分开的关键性质。就打分内部而言, 本列的文长分母按 content_full 的实际字符长度逐篇计算, 与 TF 统计严格同一文本口径 (标题经 prepend 计入首句, 分子分母同源), 仅在缺 content_full 而回退原始内容列打分时才沿用上游预算的 doc_length 列, 正常生产路径不触发该回退; 关键词权重经默认百分之一与百分之九十九分位 Winsorize 压尾、各向异性下限默认 0.1 重标定, 这些参数与 ctx、ss 轨完全共享, 保证六个测度单元只在文本口径与嵌入模型两个维度上变化、而权重构造的其余自由度被钉死, 故轨间与模型间的任何分歧都能干净归因。在稳健性梯子里本列是 canonical 锚点: 三轨乘双嵌入的六格全部围绕本列展开, 任何一格与本列的方向背离都提示对应维度 (语境窗口或嵌入空间) 的敏感性; 与无加权对照臂 avg_ft_word_ratio 并读时, 本列与该列的差异恰好度量 IDF 加嵌入语义纯度这套加权方案相对朴素词频占比的净贡献, 从而把加权方案本身的信息增量单独识别出来。最后须重申数值判读的边界: 本列是位置参数, 不含离散信息, 报告时应与 avg_ft_intensity_full_std 成对呈现, 二者分别回答该银行金科报道平均有多硬核与深浅是否两极, 承载不同构念, 任何一个都不可单独代表该银行的金科报道结构。

## VAR: avg_ft_intensity_full_std

【变体差分】
full 轨离散度臂, canonical 均值列 avg_ft_intensity_full 的伴生标准差。对银行-年内全部通过熔断验证的 full 轨文章级得分取样本标准差 (除以 n-1), 刻画该银行当年金科报道技术强度的篇际分化程度: 高值对应深度稿与浅稿并存的两极格局, 低值对应口径整齐的报道结构。构念上它与均值臂正交互补 — 两家银行可以均值相同而离散迥异, 一家靠少量硬核稿拉高均值、其余皆浅提及, 另一家篇篇中等强度, 两者的金科叙事结构完全不同, 只看均值无法区分。因源列即 _full 别名的底层列, 本列与无后缀 avg_ft_intensity_std 数值恒等, 二者是同一列的两个名字, 禁止同时入回归。组内有效篇数不足 2 时为 NaN, 缺失集中于报道稀少的银行-年格, 缺失机制与报道量相关; 短面板窗下组内篇数有限, 标准差估计噪声较大, 解释时应结合报道篇数看。full 轨因熔断触发率最低, 本列的有效样本面在三轨离散度臂中最宽, 是离散度构念下最接近全信息口径的一臂; 与 ctx、ss 两轨的 _std 臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。本列与其 _lg 版 avg_ft_intensity_lg_full_std 组内文章集合逐格一致、仅语义权重模型不同, 二者并读可检验报道结构分化对嵌入空间选择的稳健性; 无后缀 avg_ft_intensity_std 是本列的恒等别名, 二者是同一列的两个名字, 禁止同入任何回归或稳健性表。

## VAR: avg_ft_intensity_lg

【变体差分】
_lg 侧无后缀 legacy 别名列, 均值臂。聚合入口直接注册为文章级 fintech_intensity_score_lg_full 的银行-年均值, 因此与 avg_ft_intensity_lg_full 数值恒等 — 与 MAIN 侧无后缀列 avg_ft_intensity 恒等于 _full 列的别名设计完全对称, 两侧对称是刻意的工程约定, 避免使用者在两个嵌入轨间切换时遭遇不一致的命名语义。语义纯度权重来自 _lg co-primary 槽 text-embedding-3-large (3072 维, OpenAI 系, 经 yunwu 端点), 除嵌入模型外, 词典、全局 IDF、双重对数打分、熔断阈值、聚合口径与 MAIN 侧全部相同, 均值同为通过验证文章上的条件均值。使用规范与 MAIN 侧别名一致: 新代码应显式引用 avg_ft_intensity_lg_full, 本列仅作兼容通道; 禁止把本列与 _lg_full 列同时纳入任何模型 — 它们完全共线, 是同一列的两个名字而非梯子两臂, 同入会虚增测度数。作为 _lg 族成员, 本列的缺失语义须分两条路径讲清: 其一, 同一 run 内嵌入 API 硬失败走 both-or-neither parity 铁律, 本列与对应 Qwen 族同置 NaN、不留单边孤儿值; 其二, 旧单轨 parquet 或 _lg 未播种的 legacy 路径不在 parity 约束范围内 — 此时上游根本没有 _lg 源列, 面板聚合层的 valid_agg 机制按源列存在性逐列跳过, 本列与整个 _lg 族整列优雅缺席, 而 Qwen 侧各列照常存在, 属预期的单侧缺列而非 parity 违约。因此见到 Qwen 有列而 _lg 无列, 应先查 _lg 播种状态与 parquet 世代, 不必怀疑 parity 失守; parity 只保证同一 run 内两族值层的成对 NaN。铁律口径随家族: 与 canonical Qwen 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。须澄清: 本列虽与 MAIN 侧 avg_ft_intensity 都是无后缀别名, 但二者分属 _lg 与 canonical 两个平权嵌入轨、数值不同, 本列恒等于 avg_ft_intensity_lg_full, MAIN 侧无后缀列恒等于 avg_ft_intensity_full, 两条恒等链彼此独立; 本列与伴生别名 avg_ft_intensity_lg_std 成对保留, 使 _lg 无后缀命名空间内位置与离散两参数俱全。

## VAR: avg_ft_intensity_lg_ctx

【变体差分】
ctx 轨均值臂的 _lg co-primary 对偶。打分文本与 MAIN 侧 avg_ft_intensity_ctx 完全相同 — content_ctx, 即 prepend 标题加目标银行实体上下文窗口 — 唯一差异在模块 B 语义纯度权重的嵌入模型: 本列用 text-embedding-3-large (3072 维) 对关键词表编码并构造 IDF 加权质心, MAIN 侧用 Qwen3-Embedding-8B (4096 维)。词频 TF、文长 L_d、全局 IDF、熔断判定全部与 MAIN ctx 轨逐篇一致, 因此本列与 avg_ft_intensity_ctx 的差异纯粹来自两个嵌入空间对关键词语义纯度的不同评估 — 哪些词被视为语义上更纯粹的金科词, 两模型的排序不完全一致, 这正是 co-primary 设计要暴露的测量不确定性: 若某结论只在其中一个嵌入空间下成立, 该结论对语义权重的构造方式敏感, 稳健性存疑。行宇宙同为 conditional-on-full, 熔断的 NaN 选择性与 MAIN ctx 轨完全同构 (熔断只看命中词种数, 不依赖嵌入)。本列同时处在两条正交梯子的交点: 轨道维度上与 lg_full、lg_ss 并排, 嵌入维度上与 avg_ft_intensity_ctx 对偶 — 两个维度都遵循互为稳健性、不分主次、各自 just-identified 并排、禁混进同一 over-identified Hansen J 的铁律, 且在同一 run 的值层受 both-or-neither parity 约束与 Qwen ctx 列成对置缺 (legacy 旧 parquet 或 _lg 未播种时本列整列由 valid_agg 优雅缺席、Qwen 列照在, 不属 parity 范畴)。须重申 co-primary 的诊断用法: 本列与 canonical ctx 列并读, 相关性高说明 ctx 轨强度对嵌入模型不敏感, 局部分歧则把测量不确定性精确定位到关键词语义纯度权重环节; 本列的缺失格与 canonical ctx 列逐一对应, 可互相校验。作为 ctx 轨成员, 本列继承窗口化短文本更易触发熔断的选择性, 未验证比例结构性高于 lg_full 对应格。

## VAR: avg_ft_intensity_lg_ctx_std

【变体差分】
ctx 轨离散度臂的 _lg 对偶。对银行-年内通过熔断验证的 _lg ctx 轨文章级得分取样本标准差 (除以 n-1), 度量在 text-embedding-3-large 语义权重与银行实体上下文窗口双重口径下, 该银行当年金科报道强度的篇际分化。因熔断判定不依赖嵌入模型, 进入本列计算的文章集合与 MAIN 侧 avg_ft_intensity_ctx_std 逐格相同, 两列差异完全来自逐篇得分中语义纯度权重的模型差 — 这使得两列的对比特别干净: 若某银行-年格在两个嵌入空间下离散度排序稳定, 说明其报道结构的两极分化是真实文本特征而非权重构造的人工产物。组内有效篇数不足 2 时为 NaN, 且 ctx 轨窗口化的高熔断率使本列有效样本面窄于 lg_full 对应格, 离散度估计噪声更大, 短窗面板下解释须谨慎。缺失机制与报道量相关, 非随机缺失。作为 _lg 族成员, 同一 run 内值层受 both-or-neither parity 约束, 嵌入失败时与 MAIN ctx std 列成对置 NaN (旧单轨 parquet 或 _lg 未播种时本列整列优雅缺席、MAIN 列照在, 属 valid_agg 缺源跳过而非 parity 违约); 在轨道与嵌入两个维度上均遵循互为稳健性、不分主次、各自 just-identified 并排、禁混进同一 over-identified Hansen J 的口径铁律。报告本列时须与其均值臂 avg_ft_intensity_lg_ctx 成对呈现: 一个是 _lg ctx 口径的位置参数, 一个是离散参数, 二者承载不同构念不可互替; 本列与 MAIN 侧 ctx 离散臂 avg_ft_intensity_ctx_std 的并读则检验离散度构念对嵌入空间的稳健性, 因两列文章集合逐格一致, 差异干净地归因于语义权重模型。

## VAR: avg_ft_intensity_lg_full

【变体差分】
_lg co-primary headline 列, core 列。full 轨均值臂的 text-embedding-3-large 对偶: 打分文本 content_full 与 canonical 列完全相同, 源列 fintech_intensity_score_lg_full, 唯一差异在模块 B 的语义纯度权重由 _lg 嵌入槽 (3072 维, OpenAI 系经 yunwu 端点) 计算。必须强调本列的地位: 它不是 canonical 列的影子或次级复制, 而是 co-primary 双轨中的另一主测度 — 项目嵌入架构的口径是两轨同为主测度、互为稳健性、严格 parity, 论文中任何以 avg_ft_intensity_full 为解释变量或机制变量的规格, 原则上都应有本列的平行规格作对照, 两轨结论一致方能声称对嵌入空间选择稳健。方法学上, 两个嵌入模型的训练语料、架构与维度不同 (4096 维对 3072 维), 对同一关键词表构造的 IDF 加权质心与余弦纯度排序存在系统差异; 统一嵌入引擎按返回矩阵的实际维度驱动计算, 维度无关, 两轨在工程上完全平权。词频、文长、全局 IDF、熔断阈值与聚合口径逐项与 canonical 列相同, 熔断不依赖嵌入, 故两列的分母文章集合逐格一致, 差异全部可归因于语义权重 — 这是 co-primary 设计的诊断价值: 两列相关性高说明测度对嵌入模型不敏感, 局部分歧则精确定位在语义权重环节, 便于在稳健性检验里判断某银行-年格的强度排序是真实文本特征还是特定嵌入空间的人工产物。parity 铁律的边界须精确: both-or-neither 约束的是同一 run 内的嵌入失败路径 — 任一嵌入侧 API 硬失败, 本列与 Qwen 族对应列在值层同置 NaN, 不留单边孤儿值; 但它不覆盖 legacy 缺列路径 — 旧单轨 parquet 或 _lg 未播种时, 上游无 _lg 源列, valid_agg 按源列存在性逐列跳过, 本列整列优雅缺席而 canonical 列照常存在, 这是预期的单侧缺列而非 parity 违约。因此本列缺失时不应径直解读为 _lg 测度失效: 值层格点缺失应查两族是否成对 NaN, 整列缺席则查 _lg 播种状态与 parquet 世代。_lg 侧无后缀列 avg_ft_intensity_lg 是本列的恒等别名, 禁止两者同入模型。识别口径: 与 canonical 列各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J — 两个 co-primary 测度误差同源 (同一语料同一词典), 塞进同一过度识别系统只会制造机械相关的假象检验, 该铁律的计量支撑见 shift-share 过度识别失效机理的相关分析; 同理, 本列在轨道维度上与 lg_ctx、lg_ss 并排, 在嵌入维度上与 canonical 列对偶, 两条正交梯子均只作 just-identified 并排。数值解释与 canonical 列同: 分母是通过熔断验证的文章, 均值是条件均值; 伴生离散臂为 avg_ft_intensity_lg_full_std。就工程实现而言, _lg 槽的关键词表编码经统一嵌入引擎在词表级一次性完成 (约 1506 词), 结果由 LLMCache 穿透缓存, 跨 run 命中即零成本、字节级可复现; 离线守卫开启时缓存未命中直接抛错而非静默付费调用, 与 canonical 槽的缓存机制完全一致, 只是 model_id 不同 — 这意味着本列与 canonical 列的复现性锚点相同, 二者的唯一实质差异被严格隔离在关键词语义向量这一环。在论文实践上, 本列的存在把嵌入空间选择从一个隐藏的研究者自由度转为可检验的显式维度: 若只报 canonical 列, 读者无从判断结论是否依赖 Qwen 特定的语义几何; 并排报本列, 两轨一致即可主张对该自由度稳健, 分歧则须在正文披露并追查到具体银行-年格。须再次强调: 在两族列均在盘的同一 run 产物内, parity 是硬约束而非惯例, 嵌入失败导致的 NaN 成对出现, 本列的缺失格与 canonical 列的缺失格逐一对应, 使用时可互相校验; 跨世代混用面板 (如接入 _lg 播种前的旧 parquet) 时该逐格对应不成立, 应先核对列存在性再谈 parity。无后缀 avg_ft_intensity_lg 是本列均值的恒等别名, 无后缀 avg_ft_intensity_lg_std 是伴生离散臂的恒等别名, 四者不可两两同入模型。

## VAR: avg_ft_intensity_lg_full_std

【变体差分】
full 轨离散度臂的 _lg 对偶, co-primary headline 均值列 avg_ft_intensity_lg_full 的伴生标准差。对银行-年内通过熔断验证的 _lg full 轨文章级得分取样本标准差 (除以 n-1), 度量 text-embedding-3-large 语义权重口径下该银行当年金科报道强度的篇际分化。与 MAIN 侧 avg_ft_intensity_full_std 的关系: 熔断不依赖嵌入, 两列的组内文章集合逐格一致, 离散度差异全部来自逐篇得分的语义权重模型差; 两列并读可判断报道结构分化这一构念是否稳健于嵌入空间选择。与 _lg 侧无后缀别名 avg_ft_intensity_lg_std 数值恒等, 禁止同入模型。组内有效篇数不足 2 时为 NaN, 缺失集中于报道稀少格, 机制与报道量相关; full 轨熔断率最低, 本列在 _lg 三轨离散臂中样本面最宽。同一 run 内值层受 both-or-neither parity 约束, 嵌入失败时与 MAIN full std 列成对置 NaN, 值层单边缺失即异常、应查嵌入失败日志; 若本列整列缺席而 MAIN 列在, 则是旧单轨 parquet 或 _lg 未播种触发 valid_agg 缺源跳过, 属预期路径, 应查播种状态而非当作数据特征。口径铁律: 与 MAIN 对偶列及 _lg 侧 ctx、ss 离散臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 离散臂与均值臂承载不同构念参数, 二者同入一表不属重复测度。报告本列须与其均值臂 avg_ft_intensity_lg_full 成对呈现, 位置与离散两参数俱全方能刻画 _lg full 口径下的报道结构; 本列既在嵌入维度上与 MAIN full 离散臂对偶, 又在轨道维度上与 lg_ctx、lg_ss 离散臂并排, 两条正交梯子均只作 just-identified 并排, 无后缀 avg_ft_intensity_lg_std 是本列的恒等别名, 禁止同入模型。

## VAR: avg_ft_intensity_lg_ss

【变体差分】
ss 轨均值臂的 _lg 对偶。打分文本 content_ss 为 prepend 标题加银行与金科词同句共现句 (±1 句窗口, config/filtering.yaml 的 context_window.ss_sentence_radius, 与 stage 13 硬过滤的 sentence_radius 是两个不同配置键), 是三轨中最严格的语境口径 — 只保留银行与金科在同一句或紧邻句内直接绑定的文本, 最大限度剔除同篇内与目标银行无关的金科泛谈。回退语义镜像 ctx: 无同句共现时 content_ss 回退为全文 body 且 ss_is_fallback 记 True, 与 full 共享 n_articles 分母; 金科自动机不可用时全体回退、优雅降级。共现判定为不对称口径: 银行侧经否定与短名过滤, 金科侧为裸词典命中。本列的语义纯度权重用 text-embedding-3-large; 词频与文长来自 ss 窗口文本, 与 MAIN 侧 avg_ft_intensity_ss 的差异纯粹是嵌入模型差。解释注意: 回退占比高的银行-年格中 ss 得分实际按全文计算, 数值向 full 轨压缩, ss 与 full 的差异被稀释; 且 ss 文本最短、熔断 NaN 率在三轨中最高, 条件均值选择面最窄。轨道与嵌入两个维度均遵循铁律: 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 同一 run 内值层受 both-or-neither parity 约束, 嵌入失败时与 MAIN ss 列成对置 NaN (legacy 缺列路径由 valid_agg 处置, 本列可整列缺席而 MAIN 列照在)。须补充 ss 轨的诊断边界: 本列在回退占比高的格内实际按全文打分, 与 lg_full 的差异被稀释, 判读轨间差异必须结合 ss_is_fallback 占比而非只看数值; 与 canonical ss 列 avg_ft_intensity_ss 逐格文章集合一致、差异纯为嵌入模型, 二者并读检验最严格语境口径下的强度是否稳健于嵌入空间选择。

## VAR: avg_ft_intensity_lg_ss_std

【变体差分】
ss 轨离散度臂的 _lg 对偶。对银行-年内通过熔断验证的 _lg ss 轨文章级得分取样本标准差 (除以 n-1), 度量最严格同句共现口径加 text-embedding-3-large 语义权重下, 该银行当年金科报道强度的篇际分化。熔断不依赖嵌入, 组内文章集合与 MAIN 侧 avg_ft_intensity_ss_std 逐格一致, 两列差异全部来自语义权重模型。ss 轨的两重结构性特征在本列叠加放大: 其一, 同句窗口文本最短, 熔断 NaN 率三轨最高, 进入标准差计算的有效篇数最少, 组内不足 2 篇即缺失, 本列是全家族缺失面最大的列之一; 其二, 回退语义使无同句共现的文章按全文打分, 回退占比高的格内得分分布混入 full 口径成分, 离散度的构念纯度被稀释, 解读时应结合 ss_is_fallback 占比。缺失机制与报道量及共现率双重相关, 非随机缺失, 回归使用须正视选择。同一 run 内值层受 both-or-neither parity 约束, 嵌入失败时与 MAIN ss std 列成对置 NaN; legacy 旧 parquet 或 _lg 未播种时本列整列由 valid_agg 优雅缺席、MAIN 列照在, 不属 parity 违约。口径铁律随家族: 轨道维度与嵌入维度上均互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。报告本列须与其均值臂 avg_ft_intensity_lg_ss 成对呈现。本列同时是全家族缺失面最大的列之一 (ss 轨最短文本叠加最高熔断率) 与嵌入维度对偶列, 使用时既要正视样本选择, 也要记住在两族列均在盘的同一 run 产物内其缺失格与 canonical ss 离散臂 avg_ft_intensity_ss_std 逐一对应, 值层单边缺失即异常、应查嵌入播种与失败日志而非当作数据特征。

## VAR: avg_ft_intensity_lg_std

【变体差分】
_lg 侧无后缀 legacy 别名列, 离散度臂。聚合入口直接注册为文章级 fintech_intensity_score_lg_full 的银行-年样本标准差, 与 avg_ft_intensity_lg_full_std 数值恒等 — 是 _lg full 轨离散臂的第二个名字, 与 MAIN 侧 avg_ft_intensity_std 恒等于 avg_ft_intensity_full_std 的别名设计完全对称。保留动机与家族其余别名一致: 维持与三轨化前历史命名的向后兼容, 让按旧列名书写的下游脚本与模板不断链; 均值别名与离散别名成对保留, 保证使用者在无后缀命名空间内能同时取到位置与离散两个参数。使用规范: 新代码应显式引用 avg_ft_intensity_lg_full_std; 禁止把本列与其恒等列同时纳入任何模型或稳健性表, 两者完全共线, 同入即虚增测度数。统计语义与恒等列相同: 除以 n-1 的样本标准差, 组内通过熔断验证的有效篇数不足 2 即 NaN, 缺失与报道量相关; 同一 run 内值层受 both-or-neither parity 约束, 嵌入失败时与 MAIN 侧对应列成对置 NaN, 而旧单轨 parquet 或 _lg 未播种时本列整列由 valid_agg 优雅缺席、MAIN 列照在, 属预期缺列路径。作为 _lg 族成员, 其所属嵌入轨与 canonical Qwen 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。须澄清本列与 MAIN 侧 avg_ft_intensity_std 的关系: 二者都是无后缀离散别名, 但分属 _lg 与 canonical 两个平权嵌入轨、数值不同, 本列恒等于 avg_ft_intensity_lg_full_std, MAIN 侧恒等于 avg_ft_intensity_full_std, 两条恒等链彼此独立; 作为离散别名, 本列与均值别名 avg_ft_intensity_lg 成对保留, 使 _lg 无后缀命名空间内位置与离散两参数俱全, 但报告离散信息时新代码应显式引用 avg_ft_intensity_lg_full_std 而非本别名。

## VAR: avg_ft_intensity_ss

【变体差分】
ss 轨均值臂, canonical Qwen 嵌入权重。打分文本 content_ss 为 prepend 标题加银行与金科词同句共现句 (±1 句窗口, 配置键 context_window.ss_sentence_radius; 注意与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同键, 前者管 ss 轨文本物化, 后者管文章留存), 是三轨中语境绑定最严格的一轨: 只有银行实体与金科词在同句或紧邻句内直接同现的内容才进入打分, 构念上度量的是与该银行直接挂钩的金科叙述的技术强度, 对同篇内的行业泛谈免疫最彻底。回退语义镜像 ctx: 一篇文章若无任何银行与金科同句共现, content_ss 回退为全文 body 且 ss_is_fallback 记 True, 与 full 共享 n_articles 分母; 金科自动机不可用时全体回退、优雅降级不崩。共现判定采用不对称口径: 银行侧经否定与短名过滤, 金科侧为裸 Aho-Corasick 词典命中。行宇宙为 conditional-on-full。解释注意有二: 其一, 回退占比高的格内得分实际按全文计算, ss 与 full 的差异被向零压缩, 判读轨间差异应结合回退率; 其二, ss 文本最短, 熔断 NaN 率三轨最高, 条件均值的选择面最窄, 跨轨比较宜看方向与显著性而非水平。与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 禁混进同一 over-identified Hansen J。须补充: 本列与其 _lg 对偶 avg_ft_intensity_lg_ss 逐格文章集合一致、仅嵌入模型不同, 并读检验最严格语境口径下强度的嵌入稳健性; 伴生离散臂 avg_ft_intensity_ss_std 提供同轨篇际分化, 与本列成对报告方能完整刻画该行金科叙述的位置与离散。

## VAR: avg_ft_intensity_ss_std

【变体差分】
ss 轨离散度臂, canonical Qwen 嵌入权重。对银行-年内通过熔断验证的 ss 轨文章级得分取样本标准差 (除以 n-1), 度量同句共现口径下该银行当年金科报道强度的篇际分化: 高值说明与该银行直接绑定的金科叙述深浅两极, 低值说明绑定叙述口径整齐。与均值臂 avg_ft_intensity_ss 同源同轨, 一个位置参数一个离散参数, 互补而非重复。本列继承 ss 轨的全部结构性特征: 同句窗口文本最短导致熔断 NaN 率三轨最高, 进入标准差的有效篇数最少, 组内不足 2 篇即缺失, 使本列与其 _lg 对偶同为全家族缺失面最大的列; 回退语义使无共现文章按全文打分, 回退占比高的格内离散度混入 full 口径成分, 构念纯度被稀释, 解读时应结合 ss_is_fallback 占比与报道篇数。缺失机制与报道量及同句共现率双重相关, 非随机缺失, 离散臂入回归须正视样本选择。与 full、ctx 两轨的 _std 臂互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 与 _lg 对偶列的关系遵循 co-primary 双轨口径, 同生同灭。本列与其 _lg 对偶 avg_ft_intensity_lg_ss_std 逐格文章集合一致、仅语义权重模型不同, 二者并读检验 ss 轨离散度对嵌入空间选择的稳健性; 作为全家族缺失面最大的列之一, 本列在短面板窗下抽样噪声尤大, 报告时应结合报道篇数与回退率给出判读边界。

## VAR: avg_ft_intensity_std

【变体差分】
无后缀 legacy 别名列, 离散度臂。聚合入口注册为文章级 fintech_intensity_score 的银行-年样本标准差, 而该源列即 stage 15 保留的 _full 轨别名, 故本列与 avg_ft_intensity_full_std 数值恒等 — 同一底层离散度的两个列名。它与无后缀均值别名 avg_ft_intensity 成对存在, 使旧命名空间下位置参数与离散参数俱全; 与 _lg 侧的 avg_ft_intensity_lg_std 恒等 avg_ft_intensity_lg_full_std 完全对称, 四个别名列构成一个两侧对称的兼容层。保留动机: 三轨化之前的模板、golden 快照与下游脚本按无后缀名引用, 删除即断链; 无后缀不代表主列, canonical 语义由显式 _full 后缀列承载, 本列是历史命名产物。使用规范: 新增代码应显式引用 avg_ft_intensity_full_std; 禁止把本列与恒等列同时放进任何回归、表格或稳健性梯子 — 完全共线, 同入即虚增测度数并误导读者以为存在两个独立离散测度。统计语义与恒等列相同: 除以 n-1, 组内通过熔断验证的有效篇数不足 2 即 NaN, 缺失与报道量相关而非随机; 其所属 full 轨与 ctx、ss 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。本列与其 _lg 对偶 avg_ft_intensity_lg_std 分属 canonical 与 _lg 两个平权嵌入轨, 二者并读可检验 full 轨离散度对嵌入空间选择的稳健性; 与均值别名 avg_ft_intensity 成对保留, 使无后缀命名空间内位置与离散两参数俱全, 但新代码应显式引用 avg_ft_intensity_full_std。

<!-- rendered-citations:begin -->
Taraj, I., & Wahlström, R. R. (2026). Narratives contextualizing numeric disclosures: Insights from earnings calls. Journal of Business Finance & Accounting, 53(3), 1263-1286. https://doi.org/10.1111/jbfa.70056
Cai, W., Shi, W., & Jiang, F. (2025). Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance. British Journal of Management, 36(1), 361-382. https://doi.org/10.1111/1467-8551.12853
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Wang, Y., & Wu, S. (2024). Impact of mobile banking on small business lending after bank branch closures. Journal of Corporate Finance, 87, 102593. https://doi.org/10.1016/j.jcorpfin.2024.102593
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Roth, J. (2022). Pretest with caution: Event-study estimates after testing for parallel trends. American Economic Review: Insights, 4(3), 305-322. https://doi.org/10.1257/aeri.20210236
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Bartik, T. J. (1991). Who benefits from state and local economic development policies? W.E. Upjohn Institute for Employment Research. https://doi.org/10.17848/9780585223940
<!-- rendered-citations:end -->
