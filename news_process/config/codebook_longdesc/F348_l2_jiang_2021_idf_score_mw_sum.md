---
family_id: F348
columns:
- jiang_2021_idf_score_mw_sum_ctx
- jiang_2021_idf_score_mw_sum_full
- jiang_2021_idf_score_mw_sum_ss
unit: 无量纲加权得分和 (IDF 加权净极性 × 媒体权威权重, 未归一化的运行和; bank-year × 轨道)
formula: "article: jiang_2021_idf_score{track} = (Σ_pos idf(w)·|score(w)| − Σ_neg idf(w)·|score(w)|) / (Σ_pos idf(w)·|score(w)| + Σ_neg idf(w)·|score(w)|) ∈ [-1,1]; idf(w) = Winsorize_{P1,P99}( log10(N/(1+df(w))) / mean(log10(N/(1+df(·)))) ), 由 build_idf_weights 在 content_full 语料上一次性估计、三轨共享; media_authority_weight_i = raw_authority_i / mean(raw_authority) (runner 步骤3c 均值归一化媒体权威权重); panel: jiang_2021_idf_score_mw_sum{track} = Σ_{a ∈ bank-year 留篇集(轨道 track)} jiang_2021_idf_score_a{track} × media_authority_weight_a; 下游 jiang_2021_idf_tone_mw{track} = jiang_2021_idf_score_mw_sum{track} / sum_media_authority_weight{track}"
producer: news_process/pipeline/sentiment/tone_words.py::build_idf_weights + _analyze_single_article → classify_batch (article idf_score) ; news_process/pipeline/panel/runner.py (步骤3c 媒体权威加权 MW 预计算) ; news_process/pipeline/panel/encode.py::_aggregate_bank_year (bank-year 求和 → jiang_2021_idf_score_mw_sum{track})
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (jiang_2021_idf_score{track} 文章级 IDF 加权净极性)
- 22_idf_weights.json (语料级 IDF 权重快照)
- 40_panel 内 media_authority_weight (compute_media_authority_weights)
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: 10.1016/j.jfineco.2013.08.018
  type: journal
  authors: Jegadeesh, N., & Wu, D.
  year: 2013
  title: "Word power: A new approach for content analysis"
  venue: Journal of Financial Economics
  vol: 110
  issue: 3
  pages_or_artno: 712-729
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
new_dois: []
---

## CORE

【构念与来源】
本家族三列 jiang_2021_idf_score_mw_sum{full,ctx,ss} 度量的是"以姜富伟、孟令超与唐国豪 (2021) 中文媒体情绪词典为极性底本、先经语料级 IDF (逆文档频率) 重加权得到逐篇连续得分、再按报道所属媒体的权威性二次加权后, 在银行-年层面求和所得的运行和"。它是本项目情感词典轨中"IDF 加权 × 媒体权威加权"这一双重加权组合的存档分子, 与其归一化后的加权均值语调 jiang_2021_idf_tone_mw{track} 是同一条测度链的分子/比值两端: 本家族保留未除以权重和的原始求和, 使分子的方向 (净极性符号) 与体量 (被两重权重放大的报道规模) 同时可审计, 便于稳健性核对与加权口径复算时直接溯源, 也使得零留篇年份可按 Σ over ∅ = 0 落 0、不残留缺失。词典底本 jiang_2021 取自姜富伟等 (2021) 在《经济学(季刊)》构建的中文媒体文本情绪词典, 该词典专门校准了中国财经媒体报道中的褒贬用词, 用以预测股票回报, 是本项目六部并置中文金融情感词典之一, 相较通用汉语情感词表更贴合银行、信贷、监管与金融科技语域的措辞习惯。家族短名中的 idf 标识第一重加权维度 (逆文档频率对稀有高信息量词赋予更高权重), score_mw 标识在此基础上叠加第二重加权 (媒体权威), sum 标识 bank-year 聚合口径为求和而非求均值或按权重归一。三层结构因此把"词汇稀有度""媒体可信度""曝光强度"三个正交维度依次编码进单一标量, 是本项目加权口径梯子中层级最深的一支。

【方法学与计算】
计算分四步, 须逐步厘清各阶段归属, 不可把两重加权混记到同一函数。第一步在文章层求逐篇 IDF 加权语调得分 jiang_2021_idf_score{track} (stage 22 tone_words): 用注入态 tone tokenizer 切词, 命中 jiang_2021 词典的褒贬词按极性归入正、负两侧, 每个命中词的幅值先乘以其语料级 IDF 权重, 正负两侧分别求加权和后作归一化, 得到落在闭区间 [-1,1] 的连续得分。IDF 权重由 build_idf_weights 在全语料上一次性估计: 以平滑逆文档频率 log10(N/(1+df(w))) 为原始权重, 除以全体情感词原始权重均值做归一化 (使加权版得分量级与等权版可比), 再做 P1/P99 Winsorization 抑制极端稀有词或极高频词的杠杆; 文档频率与文档总数均在按文本内容去重后的唯一文档集上统计, 避免同一篇报道展开成多家银行多行时虚增计数。三轨 (full/ctx/ss) 共享同一份基于 content_full 语料估计的 IDF 权重, 不按轨分别估权, 保证跨轨权重口径一致。第二步在面板装配阶段 (panel runner 步骤3c, 媒体权威加权 MW; 与步骤3b 的提及密度加权 VW 是两个互不相关的加权分支) 计算 media_authority_weight = raw_authority / mean(raw_authority): 报道所属媒体名先做精确匹配、再做去括号后缀的模糊匹配, 未评级媒体赋默认权重, 全样本均值归一化使权重中心恒为 1, 从而加权和在总体量纲上与等权和可比。第三步逐篇相乘, 得文章级双重加权得分 jiang_2021_idf_score{track} × media_authority_weight (该乘积是 runner 步骤3c 现算的中间量, 并非 stage 22 落盘列)。第四步在 encode.py 的 bank-year 聚合中对该双重加权得分求和, 即得本列 jiang_2021_idf_score_mw_sum{track}; 随后同段以 sum_media_authority_weight{track} 为分母作除法, 派生出归一化的 jiang_2021_idf_tone_mw{track}, 故本家族三列在数学上是该加权均值语调的分子。三轨文本域各自独立走完这条链路: full 轨 = 标题 prepend + 全文正文, ctx 轨 = 标题 + 银行/金融科技实体上下文窗 (stage 14 ctx_materializer 物化), ss 轨 = 标题 + 银行与金科同句共现窗 (半径由 config filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句)。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入某银行-年的"银行金科报道"总体只看 full 轨的 llm_verified_full 判定, ctx/ss 是 conditional-on-full 的子集测度, 行宇宙为 full 留篇集的子集, 但 per-track 分子仍逐轨照算, 不借用彼此分母。

【文献定位】
词典来源姜富伟、孟令超与唐国豪 (2021) 在《经济学(季刊)》构建了面向中国媒体文本的情绪词典并验证其对股票回报的预测力, 是本家族极性判据的原始出处, 也是本项目六部并置中文情感词典之一。IDF 重加权这一构造维度的方法学根据可追溯至两处经典文献: Spärck Jones (1972) 首次提出以逆文档频率刻画词条特异性、抑制高频套话词权重, 是全部 IDF 加权测度的共同源头; Jegadeesh 与 Wu (2013) 在 Journal of Financial Economics 将词权重内容分析范式引入金融文本, 是本家族"以 IDF 为稀有高信息量词赋权"这一设计的直接金融学先例, 也是本家族的顶刊锚点之一。就中文金融词典本身的构造效度, Du、Huang、Wermers 与 Wu (2022) 在 Review of Finance 系统论证了语言与领域专用性对中文金融情感测度的必要性, 与本项目并置多部中文词典 (含 jiang_2021) 互为稳健性的整体设计同源。Barbaglia、Consoli、Manzan、Tiozzo Pezzoli 与 Tosetti (2025) 在 Economic Inquiry 给出经济文本词典法情感分析的系统流程与验证证据, 印证了"逐词命中 → 篇章净极性 → 单元加权求和"这一构造链路在当代文献中的规范性。方法论三角的另两支由 Cao、Jiang、Yang 与 Zhang (2023) 在 The Review of Financial Studies 关于机器 (LLM) 阅读企业披露的研究间接界定, 提示词典法、LLM 法与 BERT 法各有其效度边界, 应互为稳健性对照而非相互替代。须强调铁律: 本家族所属的 IDF 加权与媒体权威加权 (MW) 是加权口径梯子中的两层维度, 与等权聚合、提及密度加权 (VW)、羊群衰减加权 (HW) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同加权口径的分子混进同一 over-identified Hansen J 过度识别检验; 三轨 full/ctx/ss 同样各自 just-identified 并排, 禁混同一 over-identified Hansen J; 六部并置词典 (jiang_2021 与 bian_2021/yao_2021/du_2022/you_2018/loughran) 之间亦互为稳健性、不分主次。

## VAR: jiang_2021_idf_score_mw_sum_ctx

【变体差分】
本列是 ctx (实体窗) 轨的 jiang_2021 双重加权 (IDF × 媒体权威) 得分和。相对于家族的 full 轨, 唯一差分在底层文本域: ctx 轨的逐篇文本 content_ctx 由 stage 14 ctx_materializer 物化, 取标题 prepend 后加上以银行/金融科技实体为中心的上下文窗口, 而非全文正文, 因此 jiang_2021 词典的逐词命中只在实体邻近语境内统计, 得到的 jiang_2021_idf_score_ctx 反映"围绕目标银行与金融科技实体的局部语调"经 IDF 重加权后的结果, 对远离实体的题外极性词不敏感。IDF 权重本身仍复用三轨共享的同一份基于 content_full 语料估计的权重 (不按 ctx 轨重估), 媒体权威权重同样与轨无关、恒取自报道所属媒体, 二者只在乘数意义上参与, 差分不发生在权重估计环节而只发生在极性得分的文本扫描环节。留篇宇宙受 full-only 门控约束: 求和域是 full 轨留篇集的子集, 且须该报道存在可物化的实体上下文窗; 当上游实体窗缺失或轨源列缺失时, 逐项守卫使聚合优雅跳过、按空集求和落 0, 不借用 full 轨分母。本列与 full、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; 与家族内其他加权口径分子 (等权 sum、VW 分子、HW 分子) 相比, 本列专属 IDF × 媒体权威双重加权组合, 亦互为稳健性并排, 不合并识别。作为求和轨, 本列的绝对量级同时受该银行-年 ctx 轨留篇报道数与命中词稀有度分布、媒体权威分布共同驱动, 跨银行比较时应与归一化的 jiang_2021_idf_tone_mw_ctx 及留篇报道数联合判读, 避免把曝光强度或权威分布偏斜误读为语调方向本身的变化。开发期 T=2 小样本上 ctx 轨可能因实体窗命中稀疏而呈现较大波动或退化格, 属预期, 生产期 T=18 语料下回归正常。

## VAR: jiang_2021_idf_score_mw_sum_full

【变体差分】
本列是 full (全文) 轨, 是家族内口径最完备的一列, 也是留篇门控的定义轨。其逐篇得分 jiang_2021_idf_score_full 算在 content_full 上 (标题 prepend + 完整正文), 覆盖报道全部可用文字, 不做实体窗或同句收窄; IDF 权重估计语料恒为 content_full, 因此 full 轨是三轨中文本底料与 IDF 估权语料严格同源、口径最"原生"的一轨。留篇门控为 full-only (2026-06-29): 一篇报道是否计入某银行-年的"银行金科报道"总体只由 full 轨的 llm_verified_full 判定, 因而 full 轨的求和域即银行-年行宇宙本身, 是 ctx/ss 两轨求和域的母集。第二重媒体权威加权与文本域无关, 恒按报道所属媒体经均值归一化后相乘, 与 ctx/ss 轨共享同一权重估计逻辑。作为双重加权求和的分子, 本列须与同轨的媒体权威权重和 sum_media_authority_weight_full 配对使用方得加权均值语调 jiang_2021_idf_tone_mw_full; 单独看本列是"IDF 加权净极性 × 媒体权威"的运行和, 量纲随该单元报道条数、词汇稀有度分布与权威分布浮动, 不可直接跨单元比水平。与等权求和分子、VW/HW 加权分子相比, 本列在权重维度上专属 IDF × 媒体权威组合, 各口径互为稳健性、不分主次, 各自 just-identified 并排, 严禁混同一 over-identified Hansen J; 与 ctx、ss 两轨相比, 差分仅在文本扫描范围, 三轨同样互为稳健性并排。由于 full 轨文本域最宽, 命中褒贬词与高 IDF 稀有词的机会最多, 其加权求和总量在三轨中通常绝对量级最大, 跨银行解读时须与均值轨及留篇报道数联合判读, 以分离语调方向、词汇稀有度信号与媒体曝光强度三重耦合。

## VAR: jiang_2021_idf_score_mw_sum_ss

【变体差分】
本列是 ss (同句) 轨, 三轨中文本域最窄、极性判据最严的一轨。其逐篇得分 jiang_2021_idf_score_ss 算在 content_ss 上, 即标题 prepend 后保留银行与金融科技词在同一句 (±N 句半径, 由 config filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 内共现的语段, 把 jiang_2021 词典命中进一步收紧到银行与金科真正同句共现的最小语境。回退语义须与 CLAUDE.md 口径一致、镜像 ctx 轨: 当某报道不存在银行∧金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True (与 ctx 共享 n_articles 分母口径); 若上游金融科技 AC 自动机为 None 则 *_is_fallback 全体置真, 优雅降级, 而非静默丢行。IDF 权重同样复用三轨共享的 content_full 语料估计结果, 不按 ss 轨重估; 媒体权威权重与轨无关。留篇仍遵 full-only 门控, ss 轨为 conditional-on-full 的稳健性轨, 在 full 留篇集子集上逐轨自算双重加权求和, 缺源列或空集时按 Σ over ∅ = 0 落 0。本列与 full、ctx 各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; 与家族内其他加权口径分子相比亦互为稳健性并排, 不合并识别。因同句共现语段常短于全文与实体窗, 单篇命中词数往往更少、IDF 高权重稀有词命中概率也随之下降, 故 ss 轨双重加权求和总量在三轨中通常绝对量级最小, 跨银行比较时须与留篇报道数及回退占比联合判读, 避免把语境收窄或大面积回退导致的量级下降误读为语调转弱。在开发期 T=2 上 ss 轨常因同句共现稀疏而大面积回退甚至零方差, 属预期退化, 生产期 T=18 语料下恢复正常, 不影响本列作为双重加权分子的口径定义。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Jegadeesh, N., & Wu, D. (2013). Word power: A new approach for content analysis. Journal of Financial Economics, 110(3), 712-729. https://doi.org/10.1016/j.jfineco.2013.08.018
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
<!-- rendered-citations:end -->
