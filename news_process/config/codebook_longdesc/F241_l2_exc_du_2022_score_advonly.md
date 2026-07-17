---
family_id: F241
columns:
- exc_du_2022_score_advonly_ctx
- exc_du_2022_score_advonly_full
- exc_du_2022_score_advonly_ss
unit: 情感倾向得分 (无量纲; 值域约 [-1, 1], 正为褒、负为贬)
formula: "exc_du_2022_score_advonly{track} = mean_{article ∈ 非停刊媒体} du_2022_score_advonly{track}; 文章级 du_2022_score_advonly = Σ(final_score) / Σ|final_score| (加权幅度归一化, fix omni-g-tonewords-09; 非计数口径), final_score = 词典基值 × 权重, 仅启用转折规则 (转折从句区域内 ×ADVERSATIVE_BOOST 放大, 正负两侧同受此放大), 否定翻转与程度副词规则关闭; 分母 Σ|final_score| 为全部匹配情感词加权幅值之和, 与分子同含 adversative 权重故值恒有界 ∈ [-1, +1]"
producer: news_process/pipeline/panel/attention_media.py (exc_ 停刊稳健性聚合); 文章级底料 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (rule-ablation advonly 变体)
upstream:
- 22_tone_words.parquet (du_2022_score_advonly_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- _is_ceased_media (attention_media 内 detect_defacto_cessation 派生的隐性停刊标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.1093/llc/fqae013"
  type: "journal"
  authors: "Venglařová, K., & Matlach, V."
  year: 2024
  title: "Beyond content: discriminatory power of function words in text type classification"
  venue: "Digital Scholarship in the Humanities"
  vol: "39"
  issue: "2"
  pages_or_artno: "765-789"
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「剔除隐性停刊媒体之后、以 du_2022 中文金融情感词典在仅转折语言学规则下重算」的银行–年度情感倾向。列名前缀 exc_ 是 excluding-ceased-media 的缩写, 语义与词典本身无关, 而是一道幸存者偏差 (survivorship bias) 稳健性处理: 面板构建阶段先由 detect_defacto_cessation 判定哪些媒体来源在样本期内事实上停止发稿 (de-facto cessation, 隐性停刊而非正式注销), 再仅对来自「仍存活媒体」的文章聚合情感, 以检验主情感测度是否被存活媒体的选择性构成所污染。底层词典采用 du 等 (2022) 在 Review of Finance 发表的中文金融情感词典, 该词典针对中文语料与金融领域特异性重建了褒贬词表, 并识别出政治类正面词的市场信号弱于普通正面词这一发现; 生产口径中政治正面词以 0.5 的降低权重计入正侧 (polw05, canonical)。本家族在此词典之上叠加 advonly 规则消融: 在否定翻转、程度副词加权、转折放大三条语言学规则的幂集消融梯度里, advonly 单独保留转折规则、关闭其余两条。

【方法学与计算】
文章级底料由 tone_words.py 的 compute_dict_scores 产出。分词冻结在 jieba 0.42.1, 纯 CPU、无 LLM、无网络、零成本, 确定性完全来自 jieba 版本与词典文件。得分是加权幅度归一化而非计数口径 (fix omni-g-tonewords-09, 2026-06-11): 逐词累加带符号的 final_score 得分子 total_score = Σ(final_score), 同时累加其绝对值得分母 total_abs_score = Σ|final_score|, 最终 normalized_score = total_score / total_abs_score (分母为零时取 0)。这里 final_score 是每个匹配情感词在启用规则调制后的带权极性值 (词典基值经政治词降权、转折放大等权重后的结果), pos_count/neg_count 仅是正负词计数副产物、并不进入本得分的分子或分母。旧口径曾以裸匹配词数 (pos_count+neg_count) 作分母, 因分子被程度 (≤3.0) 与转折 (×1.5) 放大而理论值域达 ±4.5、盘上约 13% 文章越过 1; 改用与分子同权的 Σ|final_score| 作分母后, 得分恒有界 ∈ [-1, +1]。advonly 变体在扫描时把 apply_negation 与 apply_degree 置 False、apply_adversative 置 True: 遇否定词仍识别否定 token 并维持窗口递减骨架但不翻转极性, 遇程度副词把倍率锁定为 1.0, 唯独在遇到转折词后的从句区域内对情感词施加 ×ADVERSATIVE_BOOST 放大 (转折作用域按句末标点重置, 遵循从句级 scoping); 该放大对正负两侧情感词对称作用, 故负面词的 final_score 幅值同受转折 boost 抬升, 分子分母一并变化而不破坏 [-1,1] 有界性。这条「只锁数值效应、不动 scoping」的铁律保证 advonly 与其余六个消融变体逐字节可比。银行–年度聚合在 attention_media.py 完成: 先剔除 _is_ceased_media 为真的文章得到存活子集 df_alive, 再按 target_bank×year 对文章级 du_2022_score_advonly{track} 取算术均值, 落列 exc_du_2022_score_advonly{track}。停刊过滤只作用于分子聚合口径, 不改变词典与规则本身; 比例类与情感类 exc_ 列在零文章 bank-year 按契约保持 NaN, 不做计数零填。

【文献定位】
词典来源锚定 du 等 (2022): 该文论证通用英文情感词典迁移到中文金融文本会系统性失真, 领域与语言特异性词表能显著提升情感抽取效度, 是本家族褒贬词表与政治词降权的直接依据。转折规则的语言学基础可追溯至 Taboada 等 (2011) 的词典法情感分析框架, 其中对否定、程度强化 (intensifier) 与转折 (contrastive/adversative) 结构如何调制词典极性给出了系统处理, advonly 变体正是在该框架内单独激活转折通道的一次消融。Ma 等 (2025) 构建面向中国境内投资者的细粒度中文情感词典, 印证了在中文金融语境下持续精化领域词典与规则的必要性, 为本项目多词典并置提供同期对照。exc_ 前缀的幸存者稳健动机则由 Heese 等 (2022) 提供: 地方报纸关停会实质改变媒体监督的横截面构成, 若不剔除停刊来源, 情感聚合会向存活媒体倾斜并污染以媒体为基的 Bartik 类工具变量。需强调, 规则消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 各变体自归一化、高度共线且非可加分解, 它们各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J 检验; 同理三轨 full/ctx/ss 亦禁混同一 Hansen J。留篇门控口径与全项目一致, 采用 full-only (2026-06-29): 是否判为一篇银行金科报道只看 full 轨留篇集, ctx/ss 为 conditional-on-full 的稳健性轨。 转折通道值得脱离内容词极性而单列这一构念前提, 可由 Venglařová 与 Matlach (2024) 补强: 该文实证显示连词一类功能词在文本类型判别上具有独立于内容词的信息量, 提示转折/逆接结构本身构成一个可单独计量的语言维度。迁移边界须写明: 原文任务为文本类型分类, 并不区分转折连词与其他功能词类, 语料非中文金融新闻, 亦未涉及本族在转折从句区域内对正负两侧同幅放大的效价调制与银行-年度聚合, 故只作构念层旁证, 不构成 ADVERSATIVE_BOOST 这一具体调制方式的依据。exc_ 口径方面, 除 Heese 等 (2022) 外, Cziraki 与 Gider (2024) 以报纸停刊为冲击, 实证报道供给退出会改变本地股票的交易行为, 从近期证据侧印证媒体退出是真实且具经济后果的样本组成变化。惟其停刊判定来自外部事件数据并被用于识别冲击, 而本族 ceased_set 是由语料内部推断的疑似退出覆盖保守代理 (confirmed ∪ suspected), 并非严格停刊事实, 仅用作稳健性子样本而不承担识别功能; 该文为工作论文, 未经同行评审。
## VAR: exc_du_2022_score_advonly_ctx

【变体差分】
本列为 ctx 轨: 文章文本取标题 prepend 后的「实体窗口」上下文 content_ctx, 即在标题加银行实体命中位置附近窗口内截取的语段, 而非整篇正文。相对家族 canonical (此处以 full 轨为参照口径), 差分维度是文本轨道而非规则或词典: 词典仍是 du_2022、政治词权重仍是 canonical 0.5、规则仍是 advonly (仅转折)。ctx 轨用以检验情感信号是否稳健于「只看银行邻近语境」的收窄视野, 缓解整篇正文里与目标银行无关段落带来的稀释。聚合层面同样先剔除隐性停刊媒体再取 bank-year 均值, 故本列是 ctx 轨与停刊稳健叠加后的 advonly 情感。按 full-only 门控, ctx 轨为 conditional-on-full 测度: 行宇宙是 full 轨留篇集的子集, per-track 列照常在该子集上计算。本列与 exc_du_2022_score_advonly_full、exc_du_2022_score_advonly_ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁三轨混入同一 over-identified Hansen J。dev T=2 语料上 ctx 轨可能出现零方差退化属预期, 生产 T=19 正常。需特别区分本列与两类相邻测度: 一是同为 du_2022、同为 ctx 轨但不带 exc_ 前缀的全样本聚合列, 二者仅差在是否剔除隐性停刊媒体, 本列是前者的幸存者偏差稳健对照; 二是同轨的其它规则消融列 (如 negonly、negdeg 的 exc_ 孪生), 它们与本列共用词典与文本轨、仅规则激活组合不同, 高度共线且非可加, 只能并排读作稳健性梯子而不可相加分解为各规则的边际贡献。ctx 窗口只截取银行实体邻近语段, 因此对整篇里远离目标银行的段落所携带的褒贬噪声天然不敏感, 是本轨相对 full 轨的核心识别价值。

## VAR: exc_du_2022_score_advonly_full

【变体差分】
本列为 full 轨, 是家族内文本覆盖最广的口径: 文章文本取标题 prepend 加整篇正文 content_full。它承担留篇门控的 canonical 角色 (full-only, 2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨判定, ctx 与 ss 轨的行宇宙均为本轨留篇集的子集。词典为 du_2022、政治正面词以 0.5 降权计入 (polw05), 规则为 advonly——仅激活转折 ×ADVERSATIVE_BOOST 放大、关闭否定翻转与程度副词加权, 用以隔离「转折结构单独贡献」在整篇文本上的净情感效应。与家族其余列的差分同样是停刊稳健叠加: 本列并非对全部文章聚合, 而是先剔除 _is_ceased_media 为真的隐性停刊媒体文章, 再对存活子集按 target_bank×year 取均值, 因此它是主情感测度的幸存者偏差稳健对照, 用于验证结论不被存活媒体的选择性构成驱动。本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混入同一 over-identified Hansen J; 与规则消融梯度其余六臂 (raw/negonly/degonly/negdeg/negadv/degadv) 亦为并排稳健关系而非可加分解。本列与其非-exc_ 全样本孪生列的差分是唯一实质区别: 后者对全部文章 (含隐性停刊媒体) 聚合, 本列只对存活媒体聚合, 二者系数的接近程度即是主结论不受媒体退出污染的直接证据。full 轨承载最完整的正文信息, 因而是三轨中信噪结构最丰富、也最易被无关段落稀释的一轨; advonly 在此轨上只放大转折从句后的情感、不动否定与程度, 使得转折结构对整篇净情感的单独贡献得以被隔离测量, 便于与 negadv (否定加转折) 等含转折的组合臂对照, 判断转折效应是否与否定效应存在交互。

## VAR: exc_du_2022_score_advonly_ss

【变体差分】
本列为 ss 轨 (same-sentence 同句共现轨): 文章文本取标题 prepend 后、银行与金科词在同一句子内共现的 ±N 句窗 content_ss (句半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。相对 full/ctx, 差分维度是文本轨道——ss 轨最严格, 只保留银行与金融科技真正在同句同现的语境, 用以检验情感信号是否稳健于最窄的主题相关性判据。回退语义镜像 ctx 轨: 当文章无银行∧金科同句共现时, content_ss 优雅退化为整篇正文 body、ss_is_fallback 置真并与 full 轨共享 n_articles 分母; 若金科 AC 自动机为 None 则 *_is_fallback 全真、整体优雅降级。词典、政治词 0.5 降权、advonly 仅转折规则均与家族其余列一致; 聚合仍先剔除隐性停刊媒体再取 bank-year 均值。按 full-only 门控, ss 轨为 conditional-on-full 稳健性轨, 行宇宙是 full 轨留篇集的子集。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混同一 over-identified Hansen J。dev T=2 语料上 ss 轨常呈零方差退化属预期, 生产 T=19 恢复正常。相对 ctx 轨, ss 轨的判据更严: ctx 只要求银行实体命中即取邻近窗, ss 则要求银行与金融科技词在同一句子内共现, 因此在主题相关性上比 ctx 更保守, 也更易触发回退到全文的降级路径。这一层严格判据使本列成为「即便把相关性门槛拉到最紧、且剔除停刊媒体后」情感信号是否仍然成立的极端稳健检验; 若本列与 full/ctx 轨的 advonly 系数方向一致, 则可排除信号由弱相关篇章或存活媒体选择所驱动。本列与其非-exc_ 同句孪生列仅差停刊过滤, 与同轨其余规则消融列仅差规则激活组合, 三类差分互不交叉、各自作为正交的稳健性维度并排, 不得合并进同一 over-identified 估计。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
