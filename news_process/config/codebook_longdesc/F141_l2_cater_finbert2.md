---
family_id: F141
novelty_exempt_rationale: "该家族是算法迎合度 (algo_cater) 母族在单一 finbert2 模型上的 per-model 变体分支 (与 cater_finbert_cn/cater_fin_sent_zh 并排), 其测度定义 (词典均值净语调减机器净语调) 依据的是母族 canonical algo_cater_b 及正文已引 Frankel/Jennings/Lee (2022) 等词典-机器分歧文献, 非独立新构念, 不需单独追新 2023+ 引文。"
columns:
- cater_finbert2_ctx
- cater_finbert2_full
- cater_finbert2_ss
unit: 无量纲情感差值 (dict 与 finbert2 净语调之差, 归一化后作差)
formula: "cater_finbert2{track} = dict_avg_tone{track} - tone_finbert2{track}; 即词典均值净语调减去 finbert2 机器净语调, 在同一留篇 article 集上按 bank-year 聚合后的有向差 (正值→词典比机器更正面, 潜在迎合), 逐轨独立"
producer: news_process/pipeline/panel/export.py (标签与列装配) ; news_process/pipeline/panel/runner.py (步骤 8d algo_cater 计算)
upstream:
- 23_tone_berts.parquet (finbert2 篇章级概率/净语调)
- 22_tone_words.parquet (六词典篇章级净语调, dict_avg 分量)
- 24_herd_decay.parquet (df_exploded, 留篇 article×bank 集)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
citations:
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1145/3711896.3737219
  type: book
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: 5117-5128
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"算法迎合度" (algorithmic catering) 在单一 BERT 模型 finbert2 上的实现: 同一批银行金融科技报道, 用传统金融情感词典去读得到一套净语调, 再用现代深度学习模型 finbert2 去读得到另一套净语调, 以词典净语调减去 finbert2 净语调即为 cater_finbert2 (正值表示词典读法比机器读法更正面)。这一差值捕捉的是文本在"词典读者"眼中相对"机器读者"眼中的情感落差。其学理动机源自媒体文本被越来越多的算法而非人眼消费这一事实: 当披露方与媒体意识到打分权已从人类分析师转移到机器时, 会调整措辞以在算法阅读下获得更高的正面评价, 而这种调整未必被以固定词表逐词计分的词典所识别。因此词典读法可视为贴近传统人类阅读的基准, finbert2 读法可视为贴近当代机器阅读的口径, 二者的系统性楔子 (wedge) 就是"迎合算法"的可观测代理。Frankel、Jennings 与 Lee (2022) 正是在披露情感的语境下系统比较了机器学习读法与词典读法的分歧, 指出两种范式在同一文本上给出的情感并不等价、其差异本身携带信息; cater_finbert2 把这一"词典减机器"的分歧从公司披露迁移到中文银行金融科技新闻, 并锚定到单一可复现的 finbert2 模型上。

在本项目的度量谱系里, cater_finbert2 属于算法迎合度族的一个 per-model 分支。族内 canonical 聚合是 algo_cater_b (Dict 减 BERT 三模型均值), 而把均值替换为单一具名 BERT 模型即得到 cater_finbert_cn / cater_fin_sent_zh / cater_finbert2 三个并排的 per-model 变体。三者互为稳健性、不分主次, 各自 just-identified 并排, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验 (这与三轨、co-primary 双轨嵌入所遵循的铁律同源)。finbert2 是本项目 BERT 三模型中唯一的二分类 (Bernoulli, 仅正/负) 模型, 另两个 finbert_cn 与 fin_sent_zh 为三分类 (含中性); 因此 finbert2 的净语调在构造上是正负概率之差的单一化产物, 其绝对水平与三分类模型的净语调不严格可比, 差值型指标 cater_finbert2 也应只在标准化系数层面跨模型比较, 不比未标准化的水平。finbert2 系可选的本地私有微调模型, 当 FINBERT2_MODEL_DIR 未配置或无效时该模型整体优雅跳过, 此时 cater_finbert2 族随之缺席——这是 per-model 各自独立降级, 不牵连 finbert_cn 与 fin_sent_zh 的对应列, 也不同于 co-primary 嵌入的 both-or-neither 连坐语义。

【方法学与计算】
计算链路分三层。第一层是篇章级情感: stage 22 用六部金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 对每篇报道逐轨计净语调, 六者取均值构成 dict_avg 分量; stage 23 用 finbert2 对每篇报道输出正负概率并折算为净语调。第二层是 bank-year 聚合: 沿 24_herd_decay 给出的 df_exploded 留篇 article×bank 集, 把篇章级净语调按银行-年度分组求均值, 分别得到词典均值净语调面板列与 finbert2 净语调面板列。第三层是作差: 在 runner 步骤 8d 由词典均值面板净语调减去 finbert2 面板净语调, 得到有向的迎合度差值 (正值表示词典比 finbert2 更正面, 对应潜在的算法迎合), 再由 export 装配为带轨道后缀的三条面板列。留篇口径遵循 full-only 门控 (2026-06-29): 一篇报道是否计入银行金融科技样本只看 full 轨的 LLM 判定, ctx 与 ss 轨降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但每轨的分子分母仍逐轨独立核算, 不互借。分母口径与 n_articles 的 full-only 语义一致。

三条轨道对应三种文本视野: full = 标题 prepend 后的全文正文; ctx = 标题加实体上下文窗口; ss = 标题加"银行与金融科技同句 ±N 窗"的窄语境。ss 轨的回退语义镜像 ctx: 当某篇不存在银行与金融科技的同句共现时, content_ss 退化为全文正文且 ss_is_fallback 置 True, 与 ctx 共享 n_articles 分母。三轨各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一个 over-identified Hansen J。由于差值是两个相关测度之差, 其符号与量纲取决于两侧净语调的归一化口径; 解读时应关注差值的系统性偏离方向与其跨模型标准化后的稳健性, 而非把未标准化的绝对水平当作可跨模型或跨轨直接比较的量。

【文献定位】
本族坐落在金融文本情感测度"词典—机器学习"三角的分歧一端。Tetlock (2007) 奠定了媒体语调影响资产定价的实证范式, 确立了"以文本情感作为可回归变量"的方法论起点; Loughran 与 McDonald (2011) 指出通用词表移植到金融语境会系统误分类, 催生了领域专用词典这一支; Du 等 (2022) 进一步为中文金融文本构建了领域与语言双重适配的情感词典, 是本项目六词典中 du_2022 分支的直接来源, 也提示词典读法本身受语言与领域特异性约束。机器学习一侧, Huang、Wang 与 Yang (2023) 的 FinBERT 展示了预训练语言模型在金融文本情感抽取上相对词典的增量, 而本项目采用的 finbert2 (Xu 等, 2025) 是面向金融部署进一步专门化的双向编码器。真正把两侧对立成"可测量的分歧"的是 Frankel、Jennings 与 Lee (2022): 他们在披露情感上正式比较机器学习与词典方法, 证明二者不可互相替代、其差异携带独立信息——这正是 cater_finbert2 作为"词典减机器"差值的构念合法性所在。算法迎合的行为学动机在于: 当披露方与媒体意识到打分权已从人类分析师转移到机器之后, 披露与报道语言会向算法读者的评分函数系统漂移, 以在机器阅读下获取更高的正面评价, 而这种漂移未必被以固定词表逐词计分的词典所识别, 于是在词典读法与机器读法之间留下可测量的楔子。综合而言, cater_finbert2 把上述文献的两条测量支路 (领域词典 vs 金融 BERT) 显式作差, 提供一个可复现、可跨轨与跨模型做稳健性梯子的迎合度代理。

## VAR: cater_finbert2_full

【变体差分】
本列是 full 轨实现, 也是本族在留篇门控意义上的 headline 轨道。full 轨的文本视野 = 标题 prepend 到全文正文后的完整篇章, 既是 stage 22 词典读法与 stage 23 finbert2 读法各自计净语调的输入, 也是 full-only 留篇门控 (2026-06-29) 唯一的判定依据: 一篇报道是否被计为"一篇银行金融科技报道"只看 full 轨的 LLM 判定为真, 因此本列的行宇宙即为 full 留篇集本身, 而 ctx 与 ss 两轨则是其子集上的 conditional-on-full 测度。相对家族 canonical 聚合 algo_cater_b (词典均值减 BERT 三模型均值), 本列把减数从 BERT 三模型均值收窄为单一 finbert2 模型 (被减数恒为词典均值净语调), 从而成为 per-model 稳健性梯子的一根; 相对同族另两轨 (_ctx、_ss), 本列的唯一差分维度是文本视野为全文而非实体窗或同句窗。full 轨语义最完整、样本覆盖最广, 通常作为主分析轨进入回归, ctx 与 ss 作为首要与次要稳健性轨并排。铁律: full 与 ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 严禁把三轨或三个 per-model BERT 变体混进同一个 over-identified 的 Hansen J; finbert2 缺席时本列随该模型族整体降级, 不牵连 finbert_cn 与 fin_sent_zh 的对应列。作为二分类 finbert2 的差值产物, 本列水平只宜在标准化系数层面与其他模型或轨道比较, 不比未标准化的绝对水平。需强调本列并非独立测量, 而是词典均值净语调与 finbert2 净语调两个高度相关测度之差, 因此其信息量集中在两种读法的系统性分歧上; 当迎合行为存在时, 词典读法相对机器读法的正面偏移 (即词典比 finbert2 更正面) 会在本列上留下非零的正向印记, 这也是把本列作为 headline 轨进入主回归的构念依据。

## VAR: cater_finbert2_ctx

【变体差分】
本列是 ctx 轨实现, 差分维度为文本视野: ctx = 标题加"实体上下文窗口"内的正文片段, 即围绕目标银行与金融科技实体命中位置截取的邻近语境, 而非 full 轨的全文。词典读法与 finbert2 读法都改在这段较窄的实体语境上计净语调, 再按 bank-year 聚合、作差得到本列。在 full-only 门控下, ctx 轨是 conditional-on-full 的测度/稳健性轨: 其行宇宙是 full 留篇集的子集, 但 n_articles 分母与分子逐轨独立核算, 不向 full 借分母。相对 full 轨, ctx 把注意力聚焦到实体邻近语境, 削弱了远离主题段落对情感的稀释, 常作为主轨之外的首要稳健性轨; 相对 ss 轨, ctx 的窗口以实体上下文而非严格同句共现为界, 语境更宽。相对家族 canonical algo_cater_b, 本列同样是把 BERT 三模型均值收窄为单一 finbert2 的 per-model 变体, 只是在 ctx 文本视野上实现。铁律不变: full/ctx/ss 三轨与三个 per-model BERT 变体各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一个 over-identified Hansen J。finbert2 独立降级语义与 full 轨一致。作为二分类模型差值, 其绝对水平不跨模型直接比较, 仅比标准化后的系数。ctx 轨的价值在于: 若迎合信号主要来自实体邻近段落而非通篇, 则本列相对 full 轨会更灵敏; 反之若 full 与 ctx 两轨给出一致的迎合方向, 则说明主结论不被文本视野这一取值所驱动, 这正是三轨并排作为规格稳健性梯子的意义所在。

## VAR: cater_finbert2_ss

【变体差分】
本列是 ss 轨实现, 差分维度为最窄的文本视野: ss = 标题加"银行与金融科技同句 ±N 窗"的严格同句语境 (窗半径由 config 的 ss_sentence_radius 控制, 默认 1)。词典读法与 finbert2 读法都在这段银行与金融科技共现的同句语境上计净语调, 再聚合作差。ss 轨的关键特征是其回退语义镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 优雅退化为全文正文, 同时 ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母——这保证了没有同句共现的篇章不会被静默丢弃, 而是以全文回退方式参与, 但被标记以便下游识别。相对 full 与 ctx, ss 的语境最紧, 最直接捕捉"银行谈金融科技"这一具体命题下的情感, 因而是次要稳健性轨: 当同句共现稀疏时其有效样本收缩、方差上升属预期退化。相对家族 canonical algo_cater_b, 本列仍是把 BERT 三模型均值收窄为单一 finbert2 的 per-model 变体, 在 ss 文本视野上实现。铁律不变: 三轨与三个 per-model BERT 变体各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一个 over-identified Hansen J; finbert2 缺席时本列随族独立降级。作为二分类 finbert2 的差值, 其水平只在标准化系数层面跨模型或跨轨比较, 不比未标准化的绝对水平。ss 轨提供的是"最保守语境"下的迎合度读数: 只有在银行与金融科技被写进同一句话时的情感落差才被计入非回退部分, 因此当主轨结论在 ss 轨仍稳健时, 可最大限度排除远距离无关段落对迎合度估计的污染, 这是三轨梯子中信息最聚焦、但也最易受样本稀疏影响的一端。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25). https://doi.org/10.1145/3711896.3737219
<!-- rendered-citations:end -->
