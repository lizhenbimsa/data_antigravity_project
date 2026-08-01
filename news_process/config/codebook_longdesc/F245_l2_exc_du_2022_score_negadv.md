---
family_id: F245
columns:
- exc_du_2022_score_negadv_ctx
- exc_du_2022_score_negadv_full
- exc_du_2022_score_negadv_ss
unit: 情感倾向分值 (无量纲, Σ|base| 幅度归一化, 值域约束于 [-1, 1])
formula: "exc_du_2022_score_negadv_{track} = mean_{i ∈ (bank,year), _is_ceased_media_i = 0} du_2022_score_negadv_{track},i; 其中文章级 du_2022_score_negadv = Σ signed_final / Σ|base|, 以 du_2022 词典逐 token 计分, 规则组合 = 否定翻转 ON + 程度副词 OFF + 转折增益 ON"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (文章级源列 news_process/pipeline/sentiment/tone_words.py::_analyze_single_article, 经 _RULE_ABLATION_VARIANTS 消融循环调用 _compute_sentiment_with_rules)
upstream:
- 22_tone_words.parquet (du_2022_score_negadv_full / _ctx / _ss)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 40_panel_yearly.parquet (target_bank × year 骨架 + _is_ceased_media 标记)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1016/j.jbef.2023.100809
  type: journal
  authors: Nițoi, M., Pochea, M.-M., & Radu, Ș.-C.
  year: 2023
  title: "Unveiling the sentiment behind central bank narratives: A novel deep learning index"
  venue: Journal of Behavioral and Experimental Finance
  vol: 38
  pages_or_artno: 100809
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: "10.3390/computers12010018"
  type: "journal"
  authors: "Naldi, M., & Petroni, S."
  year: 2023
  title: "A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools"
  venue: "Computers"
  vol: "12"
  issue: "1"
  pages_or_artno: "18"
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
本家族度量的是"剔除疑似退出覆盖媒体后、以 Du 词典否定加转折规则计得的银行年度报道语调"。它由两条独立构念叠合而成: 其一是情感词典测度本身 —— 以 Du et al. (2022) 构建的中文金融情感词典 (代号 du_2022) 对每篇银行金融科技报道逐 token 计分, 得到文章级极性分值; 其二是样本稳健性口径 —— 在把该文章级分值聚合到银行年度面板时, 只纳入"存活媒体"发布的报道, 把疑似退出本地话题覆盖的媒体来源保守剔出, 前缀 exc_ 即 exclude ceased media 之意。两者相乘, 使本列既保留 du_2022 词典法的语言学口径, 又对媒体退出所引入的幸存者偏差 (survivorship bias) 做敏感性检验。词典来源 Du et al. (2022) 把中文金融文本的情感词划分为普通正面、政治正面与负面三类; 本项目采用其词表, 政治正面词以 0.5 权重计入正侧 (生产口径), 该权重另有独立的政治词权重梯度处理, 与本家族的规则消融轴正交, 互不交叉。

【方法学与计算】
文章级源列 du_2022_score_negadv 由 tone_words.py 的 _analyze_single_article 产出: 该函数对每篇报道分词后, 在 _RULE_ABLATION_VARIANTS 消融变体谱上逐一调用计分内核 _compute_sentiment_with_rules, 以后缀 negadv 对应的规则开关组合物化本列。计分内核 _compute_sentiment_with_rules 对分词后的 token 序列扫描 du_2022 词表, 命中词取其基础极性 base, 再按三条可开关的语言学规则修饰: 否定翻转 (否定词在窗口内出现则翻转其后情感词极性)、程度副词 (程度词按级别缩放情感强度)、转折增益 (转折连词后的分句情感权重上调)。本家族对应的规则组合后缀为 negadv, 即否定翻转 ON、程度副词 OFF、转折增益 ON —— 等价于在全规则基线上关掉程度副词一维 (full 减 degree)。最终分值以幅度口径归一化, 即 signed_final 之和除以 base 绝对值之和, 得到约束于 [-1, 1] 的无量纲极性。聚合环节在 attention_media.py 的 compute_media_heterogeneity 中: 先由 detect_defacto_cessation 依据媒体在语料中的覆盖跨度识别疑似退出媒体集 (confirmed 与 NPPA 交叉验证、suspected 仅数据判据), 逐篇打上 _is_ceased_media 标记; 随后对 _is_ceased_media 等于 0 的存活报道, 按 target_bank 与 year 分组取文章级分值的算术平均, 落成本列。分组为空 (该银行年度无存活媒体报道) 时本列按情感类契约保持 NaN, 绝不零填 —— 零填只施加于 n_articles_exc 一类计数列。留篇门控沿用 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技样本仅由 full 轨 LLM 判定, ctx 与 ss 轨为 conditional-on-full 的测度轨与稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 分值照各轨文本独立计算。

【文献定位】
情感词典法一脉在金融文本分析中源远流长, 中文场景尤须领域专用词表。Du et al. (2022) 在 Review of Finance 上系统论证了语言与领域专用性对中文金融情感测度的重要性, 并交付了本项目采用的 du_2022 词典, 是本家族情感构念的直接来源与顶刊锚。晚近方法学延展方面, Ma, Zhang & Zhang (2025) 构建面向中国境内投资者的细粒度中文情感词典 CN-FSD, 印证领域细分词表对本土金融文本的增益; Sun, Yuan & Xu (2025) 进一步把词典知识与中性特征注入预训练语言模型, 呼应本项目以词典法与 BERT、LLM 三法互为稳健性的多测度设计; Nițoi, Pochea & Radu (2023) 以深度学习指数解读央行叙事情感, 为词典法之外的对照口径提供参照。样本稳健性一侧, Heese, Pérez-Cavazos & Peter (2022) 在 Journal of Financial Economics 上实证地方报纸关停会造成企业监督真空进而抬升违规, 正是本家族剔除疑似退出媒体、检验语调测度是否受媒体退出污染的因果依据。本家族三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨或多套规则消融变体混进同一 over-identified 的 Hansen J 检验; 规则消融梯度各变体高度共线 (与全规则版相关系数近 0.99), 仅作定性不变的稳健性对照, 不主张某一规则组合更优。 就本口径所启用的两条规则而言, 尚可各补一条方法学锚点。否定翻转一侧, Naldi 与 Petroni (2023) 提出一套测试集方法专门评估词典法情感工具对否定的检测与处理能力, 实证各工具在否定处理上的表现差异显著, 表明否定是词典法内部可被单独测量、亦可单独失效的模块, 这正是本项目把否定翻转设为可独立开关的规则维、并令 negadv 这类开启否定的组合与关闭否定的组合并排互证的方法学依据; 迁移边界在于原文为英文通用领域的工具准确率评测, 而本项目不作否定检测准确率评估, 只把规则开关作为中文金融新闻银行年度测度的一条稳健性臂。转折增益一侧, Venglařová 与 Matlach (2024) 实证功能词 (含连词一类的非内容词) 在文本类型判别上具有独立于内容词极性的信息量, 佐证转折连词值得在计分内核中单独建模而非当作可忽略的虚词; 惟原文任务为文本类型分类、并不区分转折连词与其他功能词类, 语料亦非中文金融新闻, 其支撑仅止于「转折类功能词自带独立信息」这一构念层面。样本一侧, Cziraki 与 Gider (2024) 以美国本地报纸停刊为冲击, 发现报道供给退出会改变本地股票的交易行为, 说明媒体退出是携带经济后果的真实样本组成变化, 与 Heese, Pérez-Cavazos & Peter (2022) 一道构成剔停轨的现实动机; 但该文停刊判定取自外部事件数据、被解释变量为交易活动, 而本项目的排除集是 detect_defacto_cessation 自语料内部推断的疑似覆盖退出保守代理, 并非严格停刊事实, 用途限于稳健性子样本而非识别冲击, 且该文为未经同行评审的工作论文, 只作动机性参照。
## VAR: exc_du_2022_score_negadv_ctx

【变体差分】
本列取实体上下文轨 (ctx)。文本口径为标题 prepend 后的银行实体窗文本 (content_ctx) —— 即在物化阶段 14 由 ctx_materializer 抽取焦点银行提及周边窗口、并前置标题所得的截断文本, 而非整篇正文。相较 full 轨, ctx 轨把计分素材收缩到与目标银行直接邻近的语句, 意在剥离与该银行无关的段落噪声, 检验语调测度对"实体近场文本"是否稳健。规则组合与家族一致 (否定翻转 ON、程度副词 OFF、转折增益 ON), 词典为 du_2022, 归一化为 Σ signed_final / Σ|base|; 聚合仍只纳入 _is_ceased_media 等于 0 的存活媒体报道, 按 target_bank 与 year 取均值, 空组保持 NaN。轨道定位上, ctx 为 conditional-on-full 轨: 其行宇宙是 full 轨留篇集的子集, 是否计入银行金融科技样本由 full 轨门控裁定, ctx 只在被留篇的报道上按 content_ctx 独立计分。本 ctx 轨与同家族的 full、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 检验。它与政治词权重梯度、规则消融其余六变体彼此正交, 不得交叉组合以免列数爆炸。实证解读上, ctx 轨相对 full 轨的系统性差异, 反映"实体近场语调"与"全篇语调"的口径落差: 若一篇报道整体基调偏正但银行邻近语句偏负, ctx 轨会更贴近后者。因此本列在稳健性叙事中承担"测度是否受实体外无关文本驱动"的检验角色, 与 full 轨互为参照。同样, 剔除疑似退出媒体这一样本口径亦逐轨独立施加, ctx 轨的存活媒体子集与 full 轨同源于 _is_ceased_media 标记, 但各轨在被留篇报道上按各自文本独立计分, 互不借用分母。

## VAR: exc_du_2022_score_negadv_full

【变体差分】
本列取全文轨 (full), 是三轨中的门控基准轨。文本口径为标题 prepend 后的整篇正文 (content_full), 即在原始报道正文前置标题所得的完整文本, 计分素材覆盖全篇而非实体窗或同句窗。full 轨承担留篇门控职责 (2026-06-29 full-only 口径): 一篇报道是否被判定为"银行金融科技报道"并计入样本, 仅由 full 轨的 LLM 判定决定; ctx 与 ss 两轨的行宇宙均是 full 留篇集的子集。规则组合为 negadv (否定翻转 ON、程度副词 OFF、转折增益 ON), 词典为 du_2022, 分值以 Σ signed_final / Σ|base| 归一化至 [-1, 1]; 聚合时只对 _is_ceased_media 等于 0 的存活媒体报道按 target_bank 与 year 取算术平均, 空组保持 NaN 不零填。相较 ctx 收窄到实体近场、ss 收窄到银行金科同句共现, full 轨保留最完整的语义上下文, 是语调测度的信息量上界参照。本 full 轨与 ctx、ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J; 与政治词权重三臂、规则消融其余变体正交不交叉。实证意义上, full 轨承担双重角色: 既是留篇门控的唯一裁定轨, 又是语调测度信息量的上界参照; 当 ctx、ss 因文本收窄而在早期试跑期短面板上出现零方差退化时, full 轨仍能提供稳定的基准分值。剔除疑似退出媒体的样本口径在本轨同样只作用于聚合环节, 不改变文章级计分逻辑; 因此本列与不剔除媒体的对照列 (du_2022_score_negadv 常规聚合) 之间的差异, 恰好隔离出媒体退出对银行年度语调的净影响, 是稳健性叙事中"幸存者偏差是否驱动主结论"这一诘问的直接答复列。

## VAR: exc_du_2022_score_negadv_ss

【变体差分】
本列取同句共现轨 (ss), 是三轨中口径最严的一轨。文本口径为标题 prepend 后、银行与金融科技词在同一句子 (可含前后 N 句窗, 默认半径 1) 共现的语句拼接 (content_ss)。回退语义镜像 ctx: 当某报道不存在银行与金融科技的同句共现时, content_ss 优雅回退为整篇正文, 并置 ss_is_fallback 为真, 与 ctx 轨的回退契约同构; 当金融科技 AC 自动机为空时该轨 fallback 全部为真, 整体优雅降级。规则组合与家族一致 (否定翻转 ON、程度副词 OFF、转折增益 ON), 词典 du_2022, 归一化 Σ signed_final / Σ|base|; 聚合只纳入 _is_ceased_media 等于 0 的存活媒体报道, 按 target_bank 与 year 取均值, 空组保持 NaN。轨道定位上 ss 同为 conditional-on-full 轨, 行宇宙是 full 留篇集子集, 留篇裁定权归 full 轨, ss 只在留篇报道上按 content_ss 独立计分。本 ss 轨与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 检验; 与政治词权重梯度及规则消融其余变体正交不交叉。实证解读上, ss 轨把计分素材压缩到银行与金融科技真正同句共现的语境, 因而最贴近"银行金融科技关联叙事"这一核心构念, 但也最易受回退稀释: 在同句共现稀疏的语料或短面板上, 大量报道走整篇正文回退, 使 ss 轨向 full 轨收敛。故本列在稳健性梯子中定位为口径最严的一端, 与 full 的最宽端、ctx 的中间端构成语义粒度的三点谱。剔除疑似退出媒体的样本口径逐轨独立施加, ss 轨的存活媒体子集与其余两轨同源于 _is_ceased_media 标记, 分母不跨轨借用, 空组一律保持 NaN 而非零填, 以免把"无存活报道"误读为"零语调"。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Nițoi, M., Pochea, M.-M., & Radu, Ș.-C. (2023). Unveiling the sentiment behind central bank narratives: A novel deep learning index. Journal of Behavioral and Experimental Finance, 38, 100809. https://doi.org/10.1016/j.jbef.2023.100809
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Naldi, M., & Petroni, S. (2023). A Testset-Based Method to Analyse the Negation-Detection Performance of Lexicon-Based Sentiment Analysis Tools. Computers, 12(1), 18. https://doi.org/10.3390/computers12010018
Venglařová, K., & Matlach, V. (2024). Beyond content: discriminatory power of function words in text type classification. Digital Scholarship in the Humanities, 39(2), 765-789. https://doi.org/10.1093/llc/fqae013
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
