---
family_id: F036
columns:
- avg_doc_length
- sum_doc_length
unit: 字符数 (Unicode 汉字/字符计, 无量纲计数; avg=每篇均值, sum=年内合计)
formula: "doc_length = len(str(内容)) (逐篇 Unicode 字符数); avg_doc_length = mean_{d∈(bank,year)} doc_length; sum_doc_length = Σ_{d∈(bank,year)} doc_length"
producer: pipeline\filtering\news_bank.py (逐篇 doc_length) ; pipeline\panel\encode.py (bank-year 聚合)
upstream:
- 11_news_bank.parquet (doc_length)
- 40_panel_yearly.parquet
citations:
- doi: 10.1002/widm.70019
  type: journal
  authors: Alva Principe, R., Chiarini, N., & Viviani, M.
  year: 2025
  title: "Long document classification in the transformer era: A survey on challenges, advances, and open issues"
  venue: WIREs Data Mining and Knowledge Discovery
  vol: 15
  issue: 2
  pages_or_artno: e70019
- doi: 10.1145/3657299
  type: journal
  authors: Xia, B., Rawte, V., Gupta, A., & Zaki, M. J.
  year: 2024
  title: "FETILDA: Evaluation framework for effective representations of long financial documents"
  venue: ACM Transactions on Knowledge Discovery from Data
  vol: 18
  issue: 7
  pages_or_artno: 1-27
- doi: 10.18653/v1/2024.starsem-1.22
  type: journal
  authors: Han, G., Tsao, J., & Huang, X.
  year: 2024
  title: "Length-aware multi-kernel transformer for long document classification"
  venue: Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024)
  pages_or_artno: 278-290
- doi: 10.1093/restud/rdz061
  type: journal
  authors: Cagé, J., Hervé, N., & Viaud, M.-L.
  year: 2020
  title: "The production of information in an online world"
  venue: The Review of Economic Studies
  vol: 87
  issue: 5
  pages_or_artno: 2126-2164
- doi: 10.1145/243199.243206
  type: journal
  authors: Singhal, A., Buckley, C., & Mitra, M.
  year: 1996
  title: "Pivoted document length normalization"
  venue: Proceedings of the 19th Annual International ACM SIGIR Conference
  pages_or_artno: 21-29
- doi: 10.1108/eb026526
  type: journal
  authors: Spärck Jones, K.
  year: 1972
  title: "A statistical interpretation of term specificity and its application in retrieval"
  venue: Journal of Documentation
  vol: 28
  issue: 1
  pages_or_artno: 11-21
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行-年面板单元内所载新闻报道的文本篇幅规模, 由两列构成: 逐篇文档字符长度在单元内的均值 avg_doc_length 与合计 sum_doc_length。两列的共同底层原语是文章级列 doc_length, 在 stage 11 (news_bank.py) 的银行新闻判定与 firm-document 展开过程中逐行落列, 其定义为 doc_length = len(str(内容)) —— 即报道正文'内容'字段的 Unicode 字符数 (汉字、标点、数字、空白一并计入, 非分词后的词数、非字节数)。需强调该口径与词数口径的区别: 项目另有词口径的 ln_word_count (export.py, 对标词汇计数文献), 与本家族的字符口径互不等同; geography.py 中原名 avg_words 曾被勘误为字符口径的误标, 底层始终是 doc_length 字符数。文本篇幅是 text-as-data 语料的标准描述统计, 常被审稿人索取, 也常作为回归的报道级/单元级控制变量, 用以吸收"长文自带更多情感词、更多实体共现、更高技术强度绝对量"这一机械混淆。

【方法学与计算】
文章级 doc_length 在 stage 11 逐篇计算: 每篇报道经 Aho-Corasick 自动机一次线性扫描完成银行别名匹配与判定 (前置 total_with_title ≥ MIN_NAME_OCCURRENCES, 叠加上下半分布条件或标题命中条件), 判为银行新闻者按命中的每家合格银行展开为独立物理行, 每行携带同一原始'内容'派生的 doc_length。面板聚合在 stage 40 的 encode.py 完成, 按 (bank, year) 分组: sum_doc_length = ('doc_length', 'sum'), avg_doc_length = ('doc_length', 'mean')。故 sum 是单元内报道篇幅的总规模 (与报道条数 n_articles 正相关, 属计数型合计, encode.py 中与 sum_mention_density、sum_target_mentions 同列入 count_cols 语义类), avg 是单元内每篇报道的平均篇幅 (对报道条数不敏感, 表征"典型报道有多长")。下游 geography.py 进一步对 avg_doc_length 取 ln(1+x) 生成 avg_article_length, 以压缩长尾并作为报道文体控制。留篇门控与本家族无直接耦合: doc_length 是 track-agnostic 的物理篇幅元数据 (依原始'内容'而非三轨物化文本), 因此本家族不设 full/ctx/ss 三轨孪生、无 co-primary 双轨嵌入 _lg 孪生、亦不涉词典消融或政治词权重梯子 —— 它是单条 track-agnostic 度量, 不进入任何三轨/双轨/梯子的 just-identified 并排结构, 自然也不存在"禁混同一 over-identified Hansen J"的适用场景 (该铁律仅约束互为稳健性的并排轨/模型/权重, 本家族无并排臂)。

【文献定位】
文档长度既是信息检索与文本分类的核心归一化对象, 也是媒体经济学的观测量。在检索侧, Singhal、Buckley 与 Mitra (1996) 提出 pivoted document length normalization, 系统论证长文档在词频加权下的系统性偏倚需要按长度校正 —— 这正是本项目 fintech_intensity 核函数中 (1+ln(TF))/(1+ln(L_d)) 分母采用文档长度对数归一的方法论来源; Spärck Jones (1972) 的词特异性 (IDF) 思想与之互补, 共同构成"频次须同时按稀有度与篇幅调节"的加权范式。在长文档表示与分类的当代进展上, Alva Principe、Chiarini 与 Viviani (2025) 的综述梳理了 Transformer 时代长文档分类的挑战与进路, Han、Tsao 与 Huang (2024) 提出长度感知的多核 Transformer, Xia 等 (2024) 的 FETILDA 专门评估长金融文档的有效表示 —— 三者共同说明"篇幅"在金融文本建模中既是负担也是可利用的结构信号, 支持将篇幅规模显式建模而非忽略。在媒体经济学侧, Cagé、Hervé 与 Viaud (2020) 对在线新闻信息生产的量化 (含内容长度、复制与原创度) 说明报道篇幅是媒体产出的经济学变量, 为把 avg/sum 篇幅当作报道供给强度的代理提供外部效度。综合而言, 本家族两列既服务于计量上的文体控制, 又与文本表示学习的长度归一化传统一脉相承。

## VAR: avg_doc_length

【变体差分】
本列为单元内逐篇 doc_length 的算术均值 avg_doc_length = mean_{d∈(bank,year)} len(str(内容)), 量纲为每篇平均 Unicode 字符数。它与同族 sum_doc_length 的精确区别在聚合算子: avg 用 mean、对单元内报道条数 n_articles 不敏感, 刻画的是"该银行该年被报道时, 典型一篇报道有多长", 因而是文体/信息密度型指标而非规模型指标 —— 当一家银行某年仅有少数几篇长篇深度报道时, avg 会偏高即便 sum 不高。该列是本家族唯一被下游二次加工的成员: geography.py 对其取 ln(1+avg_doc_length) 生成 avg_article_length 作为报道文体控制, 目的是压缩右偏长尾、稳定回归尺度。方法学上, avg 之所以有意义, 正是因为长文档在词频加权测度 (情感词计数、技术强度绝对量、实体提及数) 上存在系统性放大, Singhal、Buckley 与 Mitra (1996) 的 pivoted length normalization 与本项目 fintech_intensity 的 (1+ln(TF))/(1+ln(L_d)) 分母都在处理这一偏倚; 把 avg_doc_length 作为控制变量, 等价于在单元层面吸收残余的篇幅混淆。作为 track-agnostic 的物理篇幅元数据 (依原始'内容'而非三轨物化文本), 本列不设 full/ctx/ss 孪生, 无 _lg 嵌入孪生, 不进入任何梯子并排, 故无 Hansen J 混轨风险。其局限在于对极端长文与版面异常敏感, 稳健性上宜与词口径 ln_word_count、对数变体 avg_article_length 交叉印证。此外, 由于底层 doc_length 落列于 stage 11 的 firm-document 展开之后, 同一篇多银行报道会为每家命中银行各贡献一条等长的 doc_length, 故 avg 的分母是"银行-年展开行数"而非"去重原始报道数"; 在解读跨银行的 avg 差异时须记住此展开口径, 它对本列无偏但会与共现结构相关。

## VAR: sum_doc_length

【变体差分】
本列为单元内逐篇 doc_length 的合计 sum_doc_length = Σ_{d∈(bank,year)} len(str(内容)), 量纲为该银行该年全部合格报道的 Unicode 字符总数。它与同族 avg_doc_length 的精确区别在聚合算子为 sum 而非 mean: sum 随单元内报道条数 n_articles 单调累加, 因而是规模型/供给强度型指标 —— 既反映"报道有多少篇"又反映"每篇有多长"的联合规模, 在 encode.py 中与 sum_mention_density、sum_target_mentions 同归 count_cols 语义类 (计数合计而非比率/均值)。正因其与报道条数强共线, 使用时须警惕: 若模型已含 n_articles 或注意力规模类控制, sum_doc_length 会与之高度相关, 宜择一或做正交化, 避免把"被报道得多"与"被报道得长"混为一谈; 需要纯篇幅信号时应改用 avg_doc_length。sum 的价值在于为语料级信息供给总量提供直接度量, 与 Cagé、Hervé 与 Viaud (2020) 对在线新闻内容产量的量化口径一致, 可作为媒体关注度的粗粒度体量代理。同 avg_doc_length, 本列是 track-agnostic 物理篇幅元数据, 无三轨/双轨/梯子并排结构, 不涉 co-primary 嵌入 both-or-neither 守卫, 亦无 over-identified Hansen J 混轨约束的适用场景。其已知局限是对报道条数极不均衡的银行-年单元 (少数大行报道密集) 会呈现极端右偏, 稳健性上建议与均值口径及对数变体并观。同样地, sum 承 firm-document 展开口径: 一篇同时命中多家银行的报道会向每家银行的 sum 各累加一份等长字符数, 因此 sum 在跨银行汇总时存在按共现度重复计入的特性, 这在把 sum 当作全语料信息总量时须显式说明; 若研究关心的是去重后的独立报道体量, 应回到文章级 doc_length 按原始报道 id 去重后再合计, 而非直接采用面板列 sum_doc_length。

<!-- rendered-citations:begin -->
Alva Principe, R., Chiarini, N., & Viviani, M. (2025). Long document classification in the transformer era: A survey on challenges, advances, and open issues. WIREs Data Mining and Knowledge Discovery, 15(2), e70019. https://doi.org/10.1002/widm.70019
Xia, B., Rawte, V., Gupta, A., & Zaki, M. J. (2024). FETILDA: Evaluation framework for effective representations of long financial documents. ACM Transactions on Knowledge Discovery from Data, 18(7), 1-27. https://doi.org/10.1145/3657299
Han, G., Tsao, J., & Huang, X. (2024). Length-aware multi-kernel transformer for long document classification. Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024), 278-290. https://doi.org/10.18653/v1/2024.starsem-1.22
Cagé, J., Hervé, N., & Viaud, M.-L. (2020). The production of information in an online world. The Review of Economic Studies, 87(5), 2126-2164. https://doi.org/10.1093/restud/rdz061
Singhal, A., Buckley, C., & Mitra, M. (1996). Pivoted document length normalization. Proceedings of the 19th Annual International ACM SIGIR Conference, 21-29. https://doi.org/10.1145/243199.243206
Spärck Jones, K. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21. https://doi.org/10.1108/eb026526
<!-- rendered-citations:end -->
