---
family_id: F112
columns:
- bert_avg_neg_sum_ctx
- bert_avg_neg_sum_full
- bert_avg_neg_sum_ss
unit: 概率质量之和 (无量纲, 随篇数放缩的非归一化聚合)
formula: "bert_avg_neg_sum{track} = mean_{b ∈ BERT3}( {b}_neg_sum{track} ); {b}_neg_sum{track} = Σ_articles P_b(negative | article), 逐轨对该银行-年内全部命中报道求和; BERT3 = [b for b in BERT_MODELS if b in THREE_CLASS_MODELS] = {finbert_cn, fin_sent_zh} (刻意排除二分类 finbert2, 见 geography.py::_BERT3 / omni-g-geography-06)"
producer: news_process/pipeline/panel/geography.py
upstream:
- 23_tone_berts.parquet
- 40_panel_yearly.parquet
citations:
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: 53
  issue: 2
  pages_or_artno: 405-459
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2018
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是一家银行在一个年度内, 全部命中报道所承载的「负面情绪概率质量之总量」, 并且这一总量取自两家三分类中文金融 BERT 情感分类模型 (finbert_cn 与 fin_sent_zh) 的横向平均。这里必须先厘清一个关键的口径事实: 源码中横向平均的模型集合并非全部 BERT 模型, 而是 _BERT3 = [b for b in BERT_MODELS if b in THREE_CLASS_MODELS], 即在三家已配置模型中筛出「带中性类」的两家三分类模型, 二分类的 finbert2 被刻意排除在本聚合之外 (排除动机见方法学节)。这一「BERT3 实为两家」的命名是历史产物, 变量族名中的 avg 指的是这两家可比模型间的等权平均, 而非三家。与家族 bert_avg_neg (逐篇负面概率的银行-年均值) 不同, 本家族保留的是求和口径 (_sum 后缀): 它不对篇数做归一, 因此是一个随报道数量放缩的「外延/体量」型度量, 语义上更接近「该行该年被媒体投射的负面情绪的累计规模」, 而非「平均每篇有多负」。构念动机来自金融文本研究的一个长期共识: 媒体所释放的负面语调不仅在强度上影响资产定价与融资条件, 其累计的暴露量 (报道体量 × 负面倾向) 同样承载信息, 尤其在银行这类对存款人信心与舆情高度敏感的主体上, 负面报道的总量是刻画声誉压力与潜在挤兑外部性的天然载体。Tetlock (2007) 在顶级金融期刊上系统论证了媒体负面语调对市场的可预测作用, 为「负面情绪应作为独立于正面情绪的一维信号来度量」提供了经典依据; 本家族正是把这一思想落到「跨模型平均的负面概率总量」这一具体度量上。

【方法学与计算】
计算分两层。第一层在文章级由 stage 23 (23_tone_berts) 完成: 三家中文/金融 BERT 分类器 finbert_cn、fin_sent_zh、finbert2 各自对每篇报道输出三分类 (正/中/负) 的 softmax 概率, 其中负面类概率记为 P_b(negative | article)。第二层在面板聚合阶段完成: 对每家 BERT 模型 b, 先在银行-年内对全部命中报道的负面概率求和得到 {b}_neg_sum{track} (体量口径, 不除以篇数), 再由 producer news_process/pipeline/panel/geography.py 用 _safe_mean 对 _BERT3 集合内两家三分类模型的求和值取横向平均, 生成 bert_avg_neg_sum{track}。这里的 track ∈ {full, ctx, ss} 是三条文本轨道, 决定「喂给 BERT 的是哪一段文本」而非改变聚合公式。为何刻意把 finbert2 排除在本平均之外, 有一条明确的源码级理由 (fix omni-g-geography-06, 2026-06-11): finbert2 是二分类 (仅正/负, 无中性类) 模型, 若把它并入 pos/neg 的横向平均, 会发生「类空间混合」——finbert2 把本应属于中性的概率质量强制重归一进正负两极 (盘上实测其正类均值约 0.912, 远高于三分类的 0.690/0.817), 致使 pos/neg 系统性上偏, 且 pos+neu+neg 不再构成合法的概率单纯形 (实测三类和最高达 1.33)。修复后 pos/neg/neu 统一只在 THREE_CLASS_MODELS 域上平均, 概率单纯形恒等式在三分类族重新成立; finbert2 的逐模型列 (finbert2_neg_* 及其 _vw/_mw/_hw 变体) 完整保留, 作为二分类稳健轨单独使用, 而非并入本综合列。_safe_mean 在某一模型列缺失 (如某家三分类模型未落盘时) 时按可得子集取均值, 属 per-model 独立降级, 不牵连其余模型, 也不同于 co-primary 嵌入双轨那种「both-or-neither」的同生共死约束。就稳健性口径而言, 参与本平均的两家三分类 BERT 与单列使用的 finbert2 均是 co-equal 的互为稳健性轨: 它们各自 just-identified 并排、不分主次, 严禁把不同模型的负面总量混进同一个 over-identified 的 Hansen J 过度识别检验里; 本家族提供的两家横向平均是一个便于展示的综合视图, 真正的跨模型一致性/FWER 校正由根级 rwolf 模板承担, 而非在此列上做联合工具变量。也正因 finbert2 的二分类概率与三分类的负面概率在水平上不严格可比, 才把它排除出本水平型平均而只作单列结构解读。

【文献定位】
本家族坐落在「金融文本情感度量」三角 (词典法/BERT 机器学习法/大模型法) 的 BERT 一支。Huang, Wang & Yang (2023) 提出的 FinBERT 证明了在金融语料上微调的双向编码器在情感抽取上系统优于通用词典, 是本家族选用 BERT 概率而非词频计数的直接方法学依据; Devlin 等 (2018) 的 BERT 原始工作则奠定了这些分类器的架构基础。Bochkay 等 (2023) 在会计文本分析综述中特别指出, 机器学习情感度量的下一步是把「概率而非硬标签」和「体量而非仅均值」纳入面板设计——本家族的求和口径正回应了这一方向。Frankel、Jennings & Lee (2022) 在顶刊上比较了机器学习与词典法情感, 提示两类度量各有偏误, 支撑本项目「BERT 与词典、大模型互为稳健性并排」的整体设计。最后, Piotroski、Wong & Zhang (2015) 关于中国上市公司负面信息被政治性压制的证据, 提醒本家族在中国媒体制度下解读「负面总量」时须警惕系统性的下偏与截断, 这也是把三家模型、三条轨道并排作为稳健性梯子的现实理由。

## VAR: bert_avg_neg_sum_full

【变体差分】
本列是三条轨道中的 full 轨, 即喂给三家 BERT 的文本 = 标题 prepend 到全文正文 (content_full)。在本项目 2026-06-29 起确立的 full-only 留篇门控口径下, full 轨具有特殊地位: 一篇报道是否被判为「一篇银行金科报道」只看 llm_verified_full == True, 因此 full 轨对应的银行-年报道全集就是面板行宇宙的基准留篇集, ctx/ss 轨的行宇宙是它的子集 (conditional-on-full)。落到本家族, bert_avg_neg_sum_full 的求和分母 (报道数) 与 n_articles 的 full-only 口径一致, 是三轨中唯一「在完整留篇集上」累计负面概率质量的版本, 因而作为本家族体量口径的 canonical 轨呈现。它与 ctx/ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁把三轨的负面总量混进同一个 over-identified 的 Hansen J。相对家族层的均值口径 bert_avg_neg, 本列以求和保留了报道体量维度: 一家该年被大量负面报道覆盖的银行, 即便逐篇负面强度不高, 其 full 轨总量也会显著抬升, 这正是本列想捕捉的「累计负面暴露规模」。作为求和口径, 本列在数值上随该行该年报道篇数放缩, 属其非归一定义的固有性质, 与家族层的均值口径 bert_avg_neg 恰构成「体量 vs 强度」的一对互补视角。就模型构成而言, full 轨的横向平均是两家三分类模型 finbert_cn、fin_sent_zh 求和值的等权综合, 并不包含二分类的 finbert2 (其类空间与三分类不可比, 详见 CORE 方法学节的排除理由): 两家各自 just-identified 并排、互为稳健性不分主次, 而 finbert2 作为独立的二分类稳健轨单列使用, 三者严禁把 full 轨负面总量混进同一个 over-identified 的 Hansen J。作为体量口径的基准轨, 本列在同家族内是解读其余两轨 (ctx/ss) 收敛与否的参照系: 若 ctx/ss 的聚焦负面总量与 full 同向, 则支持负面暴露信号对语境窗口选择稳健。

## VAR: bert_avg_neg_sum_ctx

【变体差分】
本列是 ctx 轨, 喂给三家 BERT 的文本 = 标题 prepend 到「实体上下文窗口」(content_ctx), 即围绕目标银行实体命中位置的局部窗口文本, 而非整篇正文。相对 full 轨, ctx 轨把负面情绪的度量收窄到「与银行实体邻近的语境」, 意在削弱整篇长文中与银行无关段落对情感信号的稀释, 是一条聚焦度更高的稳健性轨。在 full-only 留篇门控下, ctx 轨为 conditional-on-full 测度: 其行宇宙是 full 留篇集的子集, per-track 求和仍逐轨独立在各自可得报道上累计, 分母不借 full 轨。ctx 轨与 full、ss 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混进同一个 over-identified 的 Hansen J。作为求和 (_sum) 口径列, 它同样承载体量语义: 当银行实体在大量报道的邻近语境中被负面提及时, ctx 轨总量升高。需注意, 由于 ctx 文本较短且可能触发回退 (无实体窗口时的降级), 在 T 较小的开发样本上 ctx 轨的方差可能显著退化甚至趋近于零, 这属预期的样本-规模退化, 在生产 T=18 语料上恢复正常; 解读时应把 ctx 视为对 full 结论的聚焦稳健性检验而非独立主结果。就横向平均的模型构成而言, ctx 轨同样是两家三分类 BERT (finbert_cn、fin_sent_zh) 求和值的等权综合, 不含二分类 finbert2 (排除理由同 CORE): 两家各自 just-identified 并排、互为稳健性不分主次, 与单列的 finbert2 一道严禁混入同一个 over-identified 的 Hansen J。与 full 轨的关键差分仅在于输入文本的语境边界: full 取整篇 (标题+正文), ctx 取标题+实体窗口, 二者聚合公式、求和口径、模型集合与降级规则完全一致, 因此 ctx 与 full 的差异可被干净地归因于「语境窗口收窄」这一单一维度, 这正是它作为稳健性轨的识别价值所在。

## VAR: bert_avg_neg_sum_ss

【变体差分】
本列是 ss 轨 (same-sentence/同句轨), 喂给三家 BERT 的文本 = 标题 prepend 到「银行与金融科技同句共现 ±N 句窗」文本 (content_ss), 是三轨中语境最严的一条: 只保留银行实体与金融科技词在同一句 (含 ss_sentence_radius 半径) 共现的片段。其构念指向「银行-金科交叉主题下的负面情绪累计量」, 比 ctx 轨的实体窗口更专门地聚焦银行与金融科技的交汇语境。ss 轨的回退语义严格镜像 ctx: 当某报道不存在银行与金科的同句共现时, content_ss 回退为全文 body 且 ss_is_fallback 置 True, 并与该轨共享 n_articles 分母; 若上游 FINTECH_AC 为 None 则整轨 *_is_fallback 全 True 优雅降级。在 full-only 门控下 ss 亦为 conditional-on-full 的稳健性轨, 行宇宙为 full 留篇集子集, 求和逐轨独立累计不借 full 分母。ss 与 full、ctx 互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混入同一个 over-identified 的 Hansen J。作为 _sum 体量口径, 本列在开发样本上因同句共现命中稀疏, 极易出现零方差或大量回退, 属预期退化; 应把它读作「银行×金科交叉语境负面暴露总量」的最严聚焦稳健性版本, 与 full canonical 轨相互印证。就模型构成而言, ss 轨仍是 finbert_cn、fin_sent_zh 两家三分类模型求和值的等权横向平均, 二分类 finbert2 因类空间不可比而被排除在本聚合之外 (排除理由同 CORE): 两家各自 just-identified 并排、互为稳健性不分主次, 与单列的 finbert2 一道严禁混进同一个 over-identified 的 Hansen J。ss 与 ctx 的差分在于判定不对称口径与窗口严格度: ctx 取银行实体的邻近窗口, ss 则额外要求金融科技词与银行同句共现, 是三轨中语境约束最强者; 三轨聚合公式、求和口径与 per-model 独立降级规则一致, 差异被干净地隔离在文本语境这一单一维度上, 使 ss 成为对 full 主结论最保守的一道稳健性防线。

<!-- rendered-citations:begin -->
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
<!-- rendered-citations:end -->
