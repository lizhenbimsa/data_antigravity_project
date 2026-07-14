---
family_id: F247
columns:
- exc_du_2022_score_negonly_ctx
- exc_du_2022_score_negonly_full
- exc_du_2022_score_negonly_ss
unit: 情感倾向得分 (无量纲; 值域约 [-1, 1], 正为褒、负为贬)
formula: "exc_du_2022_score_negonly{track} = mean_{article ∈ 非停刊媒体} du_2022_score_negonly{track}; 文章级 du_2022_score_negonly = Σ(final_score) / Σ|final_score| ∈ [-1, +1] (逐词最终有向幅度之和除以幅度绝对值之和; 否定作用域内的词经极性翻转后其 final_score 已改号, 故被计入相反侧), 仅启用否定翻转规则 (negation), 程度副词加权与转折放大规则关闭"
producer: news_process/pipeline/panel/attention_media.py (exc_ 停刊稳健性聚合); 文章级底料 news_process/pipeline/sentiment/tone_words.py::compute_dict_scores (rule-ablation negonly 变体)
upstream:
- 22_words_tone.parquet (du_2022_score_negonly_full / _ctx / _ss)
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
- doi: 10.1016/j.dss.2016.05.009
  type: journal
  authors: Pröllochs, N., Feuerriegel, S., & Neumann, D.
  year: 2016
  title: "Negation scope detection in sentiment analysis: Decision support for news-driven trading"
  venue: Decision Support Systems
  vol: 88
  pages_or_artno: 67-75
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「剔除隐性停刊媒体之后、以 du_2022 中文金融情感词典在仅否定翻转语言学规则下重算」的银行–年度情感倾向。列名前缀 exc_ 是 excluding-ceased-media 的缩写, 语义与词典本身无关, 而是一道幸存者偏差 (survivorship bias) 稳健性处理: 面板构建阶段先由 detect_defacto_cessation 判定哪些媒体来源在样本期内事实上停止发稿 (de-facto cessation, 隐性停刊而非正式注销), 再仅对来自「仍存活媒体」的文章聚合情感, 以检验主情感测度是否被存活媒体的选择性构成所污染。底层词典采用 Du 等 (2022) 在 Review of Finance 发表的中文金融情感词典, 该词典针对中文语料与金融领域特异性重建了褒贬词表, 并识别出政治类正面词的市场信号弱于普通正面词这一发现; 生产口径中政治正面词以 0.5 的降低权重计入正侧 (polw05, canonical)。本家族在此词典之上叠加 negonly 规则消融: 在否定翻转、程度副词加权、转折放大三条语言学规则的幂集消融梯度里, negonly 单独保留否定翻转规则、关闭程度副词与转折两条。它是消融梯度中与经典 Loughran-McDonald 式「仅处理否定、不做强度调制」计数法最接近的一档, 因而承担一种向经典基线回归的稳健性对照角色。

【方法学与计算】
文章级底料由 tone_words.py 的 compute_dict_scores 产出。分词冻结在 jieba 0.42.1, 纯 CPU、无 LLM、无网络、零成本, 确定性完全来自 jieba 版本与词典文件。得分口径是自归一化的有向幅度比: 逐词计算最终有向情感幅度 final_score (正词取正、负词取负, 叠加规则后的调制值), 文章级得分 = Σ(final_score) / Σ|final_score|, 即所有词最终有向幅度之和除以其绝对值之和, 值域约束在 [−1, +1]。这里的分子分母都是「幅度」而非朴素计数: 之所以在 du_2022 上数值近似「(加权正 − 负) / (加权正 + 负)」, 是因为 du_2022 负面词权重恒为 1.0、故负侧幅度和与负面词计数一致, 但正确表述仍应以 Σ|final_score| 为分母。关键处在否定处理——负面情感词并非独立计数: negonly 变体在扫描时把 apply_negation 置 True、apply_degree 与 apply_adversative 置 False, 遇否定词时识别否定作用域并按窗口翻转其内情感词的极性 (褒贬互换, 该词 final_score 随之改号并计入相反侧), 遇程度副词时把强化倍率锁定为 1.0 (不放大也不衰减), 遇转折词时不对从句区域施加 ×ADVERSATIVE_BOOST 放大。关键铁律是这三条规则的从句级 scoping (作用域按句末标点重置) 在所有消融变体间共享: negonly 只关闭程度与转折的「数值效应」, 不改动作用域切分逻辑, 从而与全规则档及其余五档逐字节可比、抵消 scoping 差异带来的伪变异。这一「只锁数值、不动 scoping」的处理保证否定翻转的纯净语义在 negonly 里被单独隔离。银行–年度聚合在 attention_media.py 完成: 先剔除 _is_ceased_media 为真的隐性停刊媒体文章得到存活子集 df_alive, 再按 target_bank×year 对文章级 du_2022_score_negonly{track} 取算术均值, 落列 exc_du_2022_score_negonly{track}。停刊过滤只作用于分子聚合口径, 不改变词典与规则本身; 情感类 exc_ 列在零文章的 bank-year 按契约保持 NaN, 不做计数零填。需强调, 规则消融梯度各变体自归一化 (每篇文章各自以 Σ|final| 为分母), (full − negonly) 反映程度加转折对最终归一化语调的联合净效应, 属非可加分解: full 与 negonly 各自 self-normalize, 实测二者高度共线 (corr 约 0.998–0.999), 因此只报相关而非并入同一加性分解式。

【文献定位】
词典来源锚定 Du 等 (2022): 该文论证通用英文情感词典迁移到中文金融文本会系统性失真, 领域与语言特异性词表能显著提升情感抽取效度, 是本家族褒贬词表与政治词降权的直接依据, 也是本项目全部 du_2022 系列测度的顶刊锚。否定处理的方法学基础可锚定 Pröllochs 等 (2016): 该文系统研究了新闻驱动交易情境下否定作用域 (negation scope) 的自动识别, 论证正确界定否定的辖域对情感极性抽取至关重要——这正是 negonly 变体唯一保留的语言学通道, 也解释了为何在消融梯度中把否定单列一档具有独立的构念意义。Ma 等 (2025) 构建面向中国境内投资者的细粒度中文情感词典, 印证了在中文金融语境下持续精化领域词典与规则的必要性, 为本项目多词典并置提供同期对照。exc_ 前缀的幸存者稳健动机则由 Heese 等 (2022) 提供: 地方报纸关停会实质改变媒体监督的横截面构成, 若不剔除停刊来源, 情感聚合会向存活媒体倾斜并污染以媒体为基的暴露度量。需强调, 规则消融梯度 (raw/negonly/degonly/advonly/negdeg/negadv/degadv) 各变体自归一化、高度共线且非可加分解, 它们各自 just-identified 并排、互为稳健性、不分主次, 禁混进同一 over-identified 的 Hansen J 检验; 同理三轨 full/ctx/ss 亦禁混同一 Hansen J。留篇门控口径与全项目一致, 采用 full-only (2026-06-29): 是否判为一篇银行金科报道只看 full 轨留篇集, ctx/ss 为 conditional-on-full 的稳健性轨。

## VAR: exc_du_2022_score_negonly_ctx

【变体差分】
本列为 ctx 轨: 文章文本取标题 prepend 后的「实体窗口」上下文 content_ctx, 即在标题加银行实体命中位置附近窗口内截取的语段, 而非整篇正文。相对家族 canonical (此处以 full 轨为参照口径), 差分维度是文本轨道而非规则或词典: 词典仍是 du_2022、政治词权重仍是 canonical 0.5、规则仍是 negonly (仅否定翻转, 程度与转折关闭)。ctx 轨用以检验情感信号是否稳健于「只看银行邻近语境」的收窄视野, 缓解整篇正文里与目标银行无关段落带来的稀释。在 negonly 规则下, ctx 轨的收窄尤其影响否定辖域的判定: 由于否定作用域按句末标点重置, 实体窗口截断可能把某些否定词或其辖内情感词切在窗口之外, 因此 ctx 轨的 negonly 得分与 full 轨并非同一文本上的简单子集重算, 而是各自在本轨文本上独立扫描、独立归一化的结果, 这也是把它列为独立稳健性轨而非派生量的原因。聚合层面同样先剔除隐性停刊媒体再取 bank-year 均值, 故本列是 ctx 轨与停刊稳健叠加后的 negonly 情感, 同时承载文本轨道与幸存者偏差两道正交的稳健性检验。按 full-only 门控, ctx 轨为 conditional-on-full 测度: 行宇宙是 full 轨留篇集的子集, per-track 列照常在该子集上计算, 分母口径与 full 轨的留篇判定严格对齐, 不另立独立留篇门控。本列与 exc_du_2022_score_negonly_full、exc_du_2022_score_negonly_ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁三轨混入同一 over-identified Hansen J; 与规则消融梯度其余六臂亦为并排稳健关系。dev T=2 语料上 ctx 轨可能出现零方差退化属预期, 生产 T=18 正常。

## VAR: exc_du_2022_score_negonly_full

【变体差分】
本列为 full 轨, 是家族内文本覆盖最广的口径: 文章文本取标题 prepend 加整篇正文 content_full。它承担留篇门控的 canonical 角色 (full-only, 2026-06-29): 一篇报道是否计入银行金科报道宇宙只由 full 轨判定, ctx 与 ss 轨的行宇宙均为本轨留篇集的子集。词典为 du_2022、政治正面词以 0.5 降权计入 (polw05), 规则为 negonly——仅激活否定翻转、关闭程度副词加权与转折放大, 用以隔离「否定结构单独贡献」在整篇文本上的净情感效应。这一档在消融梯度中最接近经典的仅否定计数法, 因而是主情感测度回归经典基线的稳健对照。与家族其余列的差分同样是停刊稳健叠加: 本列并非对全部文章聚合, 而是先剔除 _is_ceased_media 为真的隐性停刊媒体文章, 再对存活子集按 target_bank×year 取均值, 因此它是主情感测度的幸存者偏差稳健对照, 用于验证结论不被存活媒体的选择性构成驱动。在 full 文本上, negonly 与全规则档的差 (full − negonly) 恰好度量程度副词与转折两条规则在整篇报道上的联合边际贡献, 由于两档各自 self-normalize, 该差为非可加分解, 实测二者高度共线 (corr 约 0.998–0.999), 只报相关而非并入同一加性式。本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨严禁混入同一 over-identified Hansen J; 与规则消融梯度其余六臂 (raw/degonly/advonly/negdeg/negadv/degadv) 亦为并排稳健关系而非可加分解。

## VAR: exc_du_2022_score_negonly_ss

【变体差分】
本列为 ss 轨 (same-sentence 同句共现轨): 文章文本取标题 prepend 后、银行与金科词在同一句子内共现的 ±N 句窗 content_ss (句半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1)。相对 full/ctx, 差分维度是文本轨道——ss 轨最严格, 只保留银行与金融科技真正在同句同现的语境, 用以检验情感信号是否稳健于最窄的主题相关性判据。回退语义镜像 ctx 轨: 当文章无银行∧金科同句共现时, content_ss 优雅退化为整篇正文 body、ss_is_fallback 置真并与 full 轨共享 n_articles 分母; 若金科 AC 自动机为 None 则 *_is_fallback 全真、整体优雅降级。由于 ss 轨语段最短, negonly 的否定翻转在这里作用面也最小: 一个否定词只翻转其同句辖域内的褒贬词, 落在窗外的情感词不受影响, 因此 ss 轨的 negonly 得分是「最严主题相关性 × 仅否定规则」双重收窄下的情感读数, 对与银行金科强绑定的核心表述最敏感。词典、政治词 0.5 降权、negonly 仅否定翻转规则均与家族其余列一致, 差分维度纯粹是文本轨道; 聚合仍先剔除隐性停刊媒体再取 bank-year 均值, 叠加幸存者偏差稳健处理。按 full-only 门控, ss 轨为 conditional-on-full 稳健性轨, 行宇宙是 full 轨留篇集的子集, 不另立留篇判定。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁混同一 over-identified Hansen J; 与规则消融梯度其余六臂亦为并排稳健关系而非可加分解。dev T=2 语料上 ss 轨常呈零方差退化属预期, 生产 T=18 恢复正常。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Pröllochs, N., Feuerriegel, S., & Neumann, D. (2016). Negation scope detection in sentiment analysis: Decision support for news-driven trading. Decision Support Systems, 88, 67-75. https://doi.org/10.1016/j.dss.2016.05.009
<!-- rendered-citations:end -->
