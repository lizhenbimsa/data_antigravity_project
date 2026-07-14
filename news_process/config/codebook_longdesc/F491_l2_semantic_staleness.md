---
family_id: F491
columns:
- semantic_staleness_ctx
- semantic_staleness_ctx_lg
- semantic_staleness_full
- semantic_staleness_full_lg
- semantic_staleness_ss
- semantic_staleness_ss_lg
unit: 语义陈旧度 (归一化余弦相似度, 无量纲, 取值域 [0,1])
formula: "semantic_staleness_i = max_{j in W(i)} cosine(emb_i, emb_j); W(i) = {同库文章 j : d_i-7d <= date_j < d_i, date_j != date_i}; emb 为 stage 25 单位归一文章嵌入 (MAIN=Qwen 4096 维 / _lg=text-embedding-3-large 3072 维, 各算一遍, 余弦维度无关绝不混算); 面板列 = bank-year 内对 verified full-only 留篇集求均值"
producer: news_process/pipeline/text/article_staleness.py::compute_semantic_staleness ; news_process/pipeline/text/article_sbert.py::encode_articles
upstream:
- 14_news_with_ctx.parquet (content_full / content_ctx / content_ss)
- 25_article_embeddings.parquet (emb_{full,ctx,ss} + emb_{full,ctx,ss}_lg)
- 24_herd_decay.parquet (聚合域门控内连键)
- 21_tone_llms.parquet (聚合域门控回退键 + full-only 留篇集)
citations:
- doi: 10.48550/arXiv.2511.01211
  type: arxiv
  authors: Wu, C.
  year: 2025
  title: "Novelty and impact of economics papers"
  venue: arXiv
- doi: 10.48550/arXiv.2504.16318
  type: arxiv
  authors: You, K.
  year: 2025
  title: "Semantics at an angle: When cosine similarity works until it doesn't"
  venue: arXiv
- doi: 10.1038/s41586-024-07421-0
  type: journal
  authors: Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y.
  year: 2024
  title: "Detecting hallucinations in large language models using semantic entropy"
  venue: Nature
  vol: 630
  issue: 8017
  pages_or_artno: 625-630
- doi: 10.18653/v1/2024.starsem-1.22
  type: journal
  authors: Han, G., Tsao, J., & Huang, X.
  year: 2024
  title: "Length-aware multi-kernel transformer for long document classification"
  venue: Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024)
  pages_or_artno: 278-290
- doi: 10.1111/jofi.13377
  type: journal
  authors: Bybee, L., Kelly, B. T., Manela, A., & Xiu, D.
  year: 2024
  title: "Business news and business cycles"
  venue: The Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3105-3147
- doi: 10.3233/sw-222986
  type: journal
  authors: Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C.
  year: 2022
  title: "Neural entity linking: A survey of models based on deep learning"
  venue: Semantic Web
  vol: 13
  issue: 3
  pages_or_artno: 527-570
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: Tetlock, P. C.
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.18653/v1/D19-1410
  type: journal
  authors: Reimers, N., & Gurevych, I.
  year: 2019
  title: "Sentence-BERT: Sentence embeddings using Siamese BERT-networks"
  venue: Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP)
  pages_or_artno: 3982-3992
- doi: 10.1145/3677136
  type: journal
  authors: Peng, Z., Zhang, Y., & Deng, D.
  year: 2024
  title: "Near-duplicate text alignment with one permutation hashing"
  venue: Proceedings of the ACM on Management of Data
  vol: 2
  issue: 4
  pages_or_artno: Article 222
- doi: "10.1016/j.ememar.2025.101309"
  type: "journal"
  authors: "Huang, R., Chen, X., & Wu, C."
  year: 2025
  title: "The textual similarity of news content and stock return synchronicity"
  venue: "Emerging Markets Review"
- doi: "10.1145/3701716.3715303"
  type: "journal"
  authors: "Kumar, A., Tumre, S., & Patil, S."
  year: 2025
  title: "Benchmarking Near-Duplicate Detection in the era of Pay-walled News"
  venue: "Companion Proceedings of the ACM on Web Conference 2025 (WWW '25)"
new_dois:
- 10.1111/jofi.13377
- 10.1257/jel.20181020
- "10.1016/j.ememar.2025.101309"
- "10.1145/3701716.3715303"
---

## CORE

【构念与来源】
本家族度量的是"语义陈旧度"(semantic staleness): 一篇银行相关报道在其发表前 7 天的信息环境里, 与最相似的一篇旧报道之间的语义相似程度。构念的经济学锚点是 Tetlock (2011) 关于陈旧信息的经典发现——投资者对"新瓶装旧酒"式的报道 (同一事件换个说法再发一遍, 或通稿被多家媒体转载) 反应较弱, 甚至出现随后的收益反转。据此, 一篇报道若与近期旧闻高度雷同, 其边际信息含量就低, "陈旧度"就高。语义陈旧度捕捉的正是这一"词面可能不同、但含义近似"的重复维度: 它不问两篇文章用词是否一样, 而问它们说的是不是同一回事。这与本管道并存的表层陈旧度 (surface_staleness, 基于 MinHash 字符级 3-gram jaccard 的词面重叠) 构成刻意互补的一对度量——表层轨抓"字面像不像", 语义轨抓"意思像不像", 一篇真正的旧闻重印通常两把尺子都高, 而仅改写措辞的洗稿则往往语义高而表层低。数据来源上, 家族六列全部由 stage 26 (article_staleness) 从 stage 25 (article_sbert) 持久化的文章级嵌入派生; 嵌入本身来自 stage 14 物化的三轨文本 (content_full / content_ctx / content_ss), 每轨文本已由上游 prepend 标题恰好一次。构念来源与文本证据链因此是: 原始报道文本经三轨切分与标题前置, 经 co-primary 双 API 嵌入编码, 再经滚动窗口余弦最近邻检索折算为逐篇陈旧度, 最后聚合为 bank-year 面板列。构念的时间维度值得单独强调: 陈旧度是一个前视 (backward-looking) 的相对量, 一篇报道是否陈旧不取决于它自身的绝对信息量, 而取决于它相对于此前 7 天信息流的边际增量。同一篇报道若发布在信息稀疏的窗口 (前 7 天无相似旧闻) 会得到低陈旧度甚至 NaN, 而发布在一波密集同题报道之后则会得到高陈旧度——这正是"信息环境"层面的度量而非"文本质量"层面的度量。这一相对性也决定了本家族天然带有窗口边界效应: 语料最早 7 天的文章因无可比旧闻而系统性缺失陈旧度, 聚合到 bank-year 时须容忍首期的稀疏。构念上还须区分"陈旧"与"低质": 一篇高陈旧的报道未必写得差, 它可能只是把一件已被充分报道的事再讲一遍; 反之一篇原创独家 (低陈旧) 也未必信息含量高。因此本家族只作"信息重复度"的代理, 不作"报道质量"的代理, 下游解读须守住这一构念边界。

【方法学与计算】
逐篇语义陈旧度的计算由 compute_semantic_staleness 完成: 对每篇文章 i, 取其发表日 d_i 之前 7 天、且严格排除同日行的窗口 W(i), 在该窗口内用 Faiss IndexFlatIP (对单位归一向量做内积即等价于余弦相似度) 检索与 emb_i 最相似的旧文, 返回窗内 top-1 相似度作为该篇的 semantic_staleness。之所以严格排除同日行, 是为了修掉同一 docid 跨 bank 复制行 (同一篇报道匹配到多家目标银行) 之间 cosine=1.0 的伪陈旧 artifact。窗口按日粒度滚动, 第一周或空窗口 (无更早文章可比) 记 NaN, 有窗口但无有效邻居时的边界处理与表层轨对称。为保证可复现, 检索前后用稳定 argsort 的逆置换还原原始行序, 避免整列错位。算法复杂度上, 朴素 pairwise 相似度在数十万文章 × 7 天窗口下是约 2×10^9 量级的 pair 不可行, 因此语义轨用 Faiss 的滚动窗口索引 (大样本升级路径为 IVFFlat / HNSW) 把成本降到近线性; 表层兄弟轨则用 MinHash LSHForest 达到同样目的。嵌入对齐是承重环节: _load_aligned_embeddings 按 article_id 显式 join (而非裸位置对齐), 一旦行数不等、键缺失、键重复或辅键 (target_bank / 日期) 逐行不一致就 fail-loud 退出并提示重跑 stage 25, 以防陈旧的嵌入 parquet 静默错位。嵌入维度无关性是 v3.14.0 co-primary 双轨得以并存的技术前提: IndexFlatIP(dim) 对 4096 维 (Qwen MAIN) 与 3072 维 (text-embedding-3-large, _lg) 一视同仁, 各自建各自的索引、算各自的余弦, 两套维度的向量绝不混进同一次内积。聚合层由 aggregate_to_bank_year 把逐篇 score 折成 bank-year 均值 (以及配套的 highstale 占比列); 聚合前 _restrict_to_panel_domain 把"平均域"收缩到 verified 面板语料——按 (docid, target_bank) 内连 24_herd_decay (缺则回退 21_tone_llms), 与面板兄弟列 (tone / herd / intensity) 同口径, 后者均聚合自 2026-06-29 起的 verified full-only 留篇集。关键的口径分层是: "参照窗口" (过去 7 天的信息环境基准) 刻意保留 stage 13 预筛全集, 而"平均域"才收缩到留篇集——前者是为了让陈旧度基准反映真实的银行业信息环境, 后者是为了让 bank-year 均值不被约四分之一并非真正讲这家银行的文章带偏。本阶段自身不调 API、零成本 (纯 CPU 的 Faiss / MinHash), 但其消费的 stage 25 嵌入是 co-primary 双 API 付费产出, 经 _llm_cache.db 穿透缓存, 在三轨双轨全命中时可离线零成本复现。数值确定性上, 语义轨的 Faiss 内积在不同 BLAS 线程配置下可能有末位浮点漂移, 因此逐位可复现须钉死 PYTHONHASHSEED 与全部 BLAS 线程为 1; 稳定 argsort 的逆置换只保证行序确定, 不消除浮点非确定源, 这一点与本项目其它 BLAS-FP 敏感列的处理一致。聚合层的 highstale 占比列 (陈旧度超过 0.9 阈值的文章占比) 与均值列并行产出, 二者一同刻画 bank-year 的陈旧度水平与尾部形状——均值抓中心趋势, highstale 抓"高度重复报道"的密度; 两列共享同一 verified full-only 平均域, 口径与面板兄弟列严格对齐。窗口实现细节上, 滚动窗口按 unique-day 分组、每个"天"重建一次索引、窗口取 [d-7d, d) 半开区间并严格排除同日行, 把原始 O(N^2) 的 pairwise 成本降到约 7N 量级; 这一近线性化对生产规模 (约 1700 万条报道、2007–2024、T=18) 是可行性前提, 而非可选优化。嵌入缺失的降级路径亦是方法学的一部分: stage 25 的某轨 embed_texts 因 API 重试耗尽返回 None 时, 该轨两列 (MAIN 与 _lg) 依 both-or-neither 同置缺失, stage 26 据此优雅缺席对应 semantic_staleness 列, 全链不崩且不留单边孤儿列。

【文献定位】
方法学谱系上, 本家族坐落在"文本作为数据"的计量传统里。Gentzkow, Kelly, & Taddy (2019) 系统梳理了把非结构化文本折算为经济计量变量的范式, 本家族正是其中"文档相似度 / 重复度"一支的具体实现; 计量文本方法学的一条通行规范提醒任何文本派生度量都须显式披露其构念效度与已知偏差, 尤其自动化内容分析既有兑现承诺的一面也有内含陷阱的一面, 本 codebook 对 corpus-level 混池、输入截断、窗口固定性等局限的前置登记正是对这一规范的响应。构念内核直接继承 Tetlock (2011): 陈旧信息的可度量性及其与投资者反应弱化的因果联系, 是本家族全部下游稳健性叙事的出发点。嵌入编码策略上, stage 25 的"标题 + 首段约 300 字"输入构造依据 Bybee, Kelly, Manela, & Xiu (2024) 关于商业新闻信息含量的做法, 意在规避长文档编码时尾段被截断丢失信息的问题; 这一策略也与长文档表示学习的近期进展 (Han, Tsao, & Huang, 2024, 关于长文档分类的长度感知多核 transformer) 同源关切。语义相似度度量本身近年受到方法论审视: You (2025) 指出余弦相似度并非在所有几何情形下都稳健可解释, 提示"余弦高"未必等价于"语义等价", 这为本家族"语义轨仅作稳健性、不单独承载主结论"的定位提供了外部依据; 文本嵌入余弦相似度的度量口径与其可解释性边界近年已有系统梳理, 进一步佐证"嵌入余弦=语义对齐"这一等式须谨慎使用、不宜单独承载因果解读, 与本家族把语义轨定位为稳健性臂的选择高度一致。Farquhar, Kossen, Kuhn, & Gal (2024) 在大模型幻觉检测中用语义等价聚类 (semantic entropy) 度量输出的语义一致性, 与本家族"用嵌入相似度捕捉含义层面重复"的思路一脉相承。嵌入模型的适用性与效度亦受近期审视: 应用研究中如何判别一套词嵌入"是否可用、何时失效"已有成熟诊断范式, 提示同一构念在不同嵌入下的一致性本身即是效度证据——这正是本家族 co-primary 双厂商 (Qwen 与 text-embedding-3-large) 互证设计的方法学依据; 通用嵌入在金融领域语义文本相似度任务上可能退化的风险进一步警示, 在中文银行报道这一垂直语域里, 单一嵌入的余弦不足为凭, 须以跨厂商双轨并排互证, 让两家训练语料与目标全然不同的嵌入模型对"是否语义近似"给出交叉裁决。实体消歧维度上, Sevgili, Shelmanov, Arkhipov, Panchenko, & Biemann (2022) 的神经实体链接综述界定了"同一实体的不同表述"这一近似问题的技术边界, 提醒本家族的 corpus-level 匹配并非严格的同实体消歧。novelty 的对偶构念 (陈旧度的反面即新颖度) 亦有近期计量刻画, Wu (2025) 用嵌入距离度量经济学论文的新颖性与影响, 与本家族在方法上互为镜像——同一套嵌入相似度既可读作"越像越陈旧", 也可读作"越不像越新颖"。综合来看, 本家族在文献坐标上处于三条脉络的交汇: 金融经济学的陈旧信息与投资者反应 (Tetlock, 2011; Bybee et al., 2024)、计量文本方法的文档相似度范式 (Gentzkow et al., 2019)、以及自然语言处理的语义表示与相似度可解释性 (Farquhar et al., 2024; You, 2025; Han et al., 2024; Sevgili et al., 2022)。这一交汇决定了本家族的方法论谨慎: 既借用了 NLP 的嵌入相似度工具, 又受制于金融计量对可解释性与稳健性的要求, 故始终以稳健性轨而非主测度的身份出现。近期文献进一步充实了这一交汇的两端: 该文用新闻文本相似度(嵌入/文本挖掘)度量报道间的语义重复程度并检验其与股票收益同步性的关系,方法论上直接呼应本家族'语义相似度=陈旧度代理'的构念设计, 作者为 Huang, Chen, & Wu (2025, Emerging Markets Review); 该文系统对比 MinHash-LSH、SimHash 与句嵌入三类近重复新闻检测方法在付费墙新闻语料上的表现,为本家族'表层 MinHash 轨 vs 语义嵌入轨互补设计'提供最新方法学参照, 作者为 Kumar, Tumre, & Patil (2025, Companion Proceedings of the ACM on Web Conference 2025)。

【识别策略定位】
在识别策略里, 本家族全部六列均定位为稳健性度量而非主处理变量或结果变量。它们的用途是支撑一条辩护性论证: 银行相关报道的情感 / 关注 / 强度等主测度所驱动的结论, 不是被"重复报道的噪音"人为放大的。具体地, 陈旧度可作为控制变量进入自回归, 用以剥离信息环境层面的重复度; 也可用于样本切分 (高陈旧 vs 低陈旧子样本) 检验主效应的稳健性。此处必须严格复述本项目的口径铁律: 三轨 (full / ctx / ss) 各自 just-identified 并排、互为稳健性、不分主次; co-primary 双轨嵌入 (MAIN 无后缀 vs _lg) 亦各自 just-identified 并排、互为稳健性、不分主次; 六列中任意两列 (无论是跨轨还是跨嵌入 spec) 绝不混进同一 over-identified Hansen J——因为它们度量的是高度相关的同一构念的不同实现, 混入同一过度识别集会制造虚假的工具变量冗余。full 轨与 _lg 无后缀轨是家族的两个 canonical (semantic_staleness_full 与 semantic_staleness_full_lg 同列为 core), 其余四列是围绕这一对 canonical 的轨道 / 厂商稳健性臂。

【与相邻测度的构念区分】
本家族须与三个相邻测度严格区分。其一, 与 surface_staleness_{full,ctx,ss} 的区分: 后者是 MinHash 字符级 3-gram jaccard 的词面重叠, 属于非嵌入派生, 是明确的 carve-out——它没有 _lg 孪生列 (因为它根本不经过嵌入 API), 也不参与 co-primary 的 both-or-neither parity。语义轨与表层轨互补而非冗余, D-0 诊断期望二者相关性落在 [0.3, 0.7]: 太低说明某一轨失效, 太高说明二者退化为同一度量。表层轨的 MinHash / LSH near-duplicate 原语坐落在近重复文本对齐 (one-permutation hashing) 的方法谱系里, 度量的是 Jaccard 意义上的词面 shingle 重叠; 本家族语义轨则以嵌入余弦扩展到含义层面, 二者分属"词面相似"与"语义相似"两条正交的近重复检测范式, 组合使用才能同时识别原样重印与深度改写洗稿。其二, 与 stage 6.x dedup.py 的 jaccard 布尔去重决策的区分: 后者是"是否近重复"的二元判定 (阈值 0.80), 本家族是连续 score, 保留了重复程度的全部梯度信息, 不做硬切分。其三, 与新颖度 / novelty 类度量的区分: 本家族取的是窗内 top-1 相似度的 max (越大越陈旧), 语义上是"最像的旧闻有多像", 而非"平均有多新"; 方向与聚合算子都与 novelty 度量不同, 不可直接互换解读。其四, 与 stage 21 情感 LLM 及 stage 23 BERT 等情感 / 分类度量的区分: 那些度量刻画的是报道的语气或内容维度, 与本家族的"信息重复度"正交; 本家族既不问报道是正面还是负面, 也不问报道谈的是何种金科主题, 只问它相对近期旧闻带来多少语义增量。因此在下游模型里, 陈旧度与情感变量可以并列进入而不构成同族共线, 但同一家族内的六列 (三轨 × 双嵌入) 彼此高度相关, 须遵守 just-identified 并排、禁混同一 over-identified Hansen J 的铁律。其五, 与嵌入本身产出的其它派生列 (如 stage 25 直接持久化的文章嵌入向量、或其它基于同一嵌入的相似度度量) 的区分: 本家族是"对旧闻窗口取最近邻余弦的 max"这一特定算子的产物, 换算子 (如取均值、取 top-k 均值) 即成不同构念, 不可与本家族混为一谈。

【已知局限与稳健性梯子】
须如实披露与 Tetlock (2011) 原度量的两点刻意偏离。其一是匹配域: Tetlock 原文按同一公司过去 72 小时内最近 10 篇旧故事匹配, 本实现的表层与语义两轨相似度均为 corpus-level (全银行混池) 的 7 天日粒度窗口, 度量的是"银行业信息环境"层面的陈旧度, 而非严格的同公司旧闻重印率——银行 A 的一篇文章与上周关于银行 B 的行业通稿高度相似, 也会被计为陈旧。其二是相似度函数: Tetlock 原文用词重叠比率 (与本模块 surface jaccard 轨同族), 而 semantic 轨的嵌入 cosine 是对该范式的扩展而非复刻 (2011 年尚不存在此类嵌入)。方法学梯子上, 家族通过两条正交的稳健性轴展开: 一条是三轨文本轴 (full / ctx / ss, 分别对应全文 / 实体窗口 / 银行与金科同句窗口的参照范围), 另一条是 co-primary 嵌入厂商轴 (Qwen 阿里系 vs text-embedding-3-large OpenAI 系, 跨厂商独立性互证)。任何一轨或任一 spec 缺失时优雅降级: ss 轨依赖 stage 25 为 content_ss 产出的 emb_ss, 旧 schema 无该列时 main() 不产 semantic_staleness_ss, 下游按"缺列即跳过"处理不崩; both-or-neither parity 保证同一轨的 MAIN 与 _lg 两列要么同在、要么同缺, 绝不留单边孤儿。ss 回退语义须与 CLAUDE.md 一致: content_ss 在无银行与金科同句共现时回退为全文 body, 但即便嵌入层 emb_ss 等于 emb_full, 陈旧度层因 ss 的参照窗口邻居不同于 full, semantic_staleness_ss 仍不等于 semantic_staleness_full——它带独立信号而非纯冗余。此外, 语义相似度本身的可解释性有边界 (You, 2025), 因此本家族的定位始终是稳健性轨, 不单独承载任何主结论。还有若干具体局限须登记在案。其一是窗口固定性: 7 天回溯窗口是一个研究者选择的固定参数, 它假定媒体报道的"炒冷饭"周期在一周量级——对突发事件的即日多家转载捕捉良好, 但对以月为周期反复出现的季节性主题 (如季度财报季的例行报道) 则可能低估陈旧度, 因为相隔一月的相似旧闻落在窗口之外。其二是 corpus-level 混池带来的跨行污染: 由于参照窗口是全银行混池而非同公司, 一家小行的报道若与同期大行的行业通稿语义相近, 会被判为陈旧, 这在"银行业信息环境"的构念下是设计意图, 但若下游研究者误把本家族当作"同公司旧闻重印率"来解读则会产生偏差, 故 codebook 必须把这一偏离前置披露。其三是嵌入编码的输入截断: stage 25 采用"标题 + 首段约 300 字" (Bybee et al., 2024) 的输入构造, 尾段信息不进入嵌入, 因此本家族对"仅在正文后段重复旧闻"的报道敏感度较低——这是为规避长文档编码截断而做的工程折中, Han et al. (2024) 的长文档表示进展提示未来可用长度感知模型缓解, 但当前实现刻意选择短输入以控成本与稳定性。其四是回退行的语义耦合: ss 轨在无同句共现时回退全文, 嵌入层与 full 轨趋同, 虽陈旧度层因参照窗口不同仍带独立信号, 但下游若在高回退率子样本上比较 ss 与 full 轨须留意二者的部分耦合。稳健性梯子的整体设计意图是: 三轨 (参照范围维度) 与双嵌入 (厂商维度) 构成一个 3×2 的稳健性网格, 网格上任意一格失效都能定位到具体的脆弱来源 (参照范围过宽 / 单一厂商偏置 / 二者兼有), 而任意一格成立都为主结论排除一条 artifact 通道; 六列各自 just-identified 并排, 从不因彼此高度相关而被合并进同一 over-identified 工具集, 这是本家族嵌入本项目全局口径铁律的具体落地。最后就下游使用给出一条实操提示: 由于本家族全部六列共享同一套滚动窗口与聚合语义, 且 highstale 占比列与均值列并行产出, 研究者在稳健性表里应成对报告"均值 + highstale", 前者刻画信息重复度的中心趋势、后者刻画高度重复报道的尾部密度; 二者共用 verified full-only 平均域, 与面板兄弟列 (tone / herd / intensity) 口径严格一致, 因此可安全地与这些兄弟列同表并列。凡涉本家族的论文披露, 须同时载明两点刻意偏离 (corpus-level 混池 7 天窗、嵌入 cosine 为扩展而非 Tetlock 原范式) 与厂商维度变更 (Google 系历史轨已退役, 现为阿里 Qwen 与 OpenAI large 双厂商), 以满足可复现与构念保真的双重要求。

## VAR: semantic_staleness_full

【变体差分】
本列是家族两个 canonical 之一 (tier=core), 对应 full 轨 × MAIN (Qwen) 嵌入 spec。full 轨的参照文本是 content_full, 即"标题 prepend + 全文正文"——参照范围覆盖整篇报道的语义, 是三轨中信息范围最宽的一轨。MAIN spec 指 config/features.yaml::embedding_api 配置的 Qwen/Qwen3-Embedding-8B (阿里 / 硅基流动端点, 4096 维), canonical 无后缀命名仅是历史命名机制, 不代表它相对 _lg 孪生有任何层级优先——两者在 co-primary 架构下地位完全对等。计算上, 本列对每篇 full 轨文章在其发表前 7 天 (严格排除同日行) 的全库窗口内, 用 Faiss IndexFlatIP 对 4096 维单位归一向量检索 top-1 余弦, 折算为逐篇 semantic_staleness, 再在 bank-year 内对 verified full-only 留篇集求均值。由于留篇门控本身即 full-only (2026-06-29), full 轨的留篇集与平均域天然对齐, 是三轨中口径最直接的一轨。本列与家族其余五列的精确差分在于两个正交维度的组合: 轨道维度上它是 full (相对 ctx 的实体窗口、ss 的同句窗口, 参照文本范围不同), 嵌入厂商维度上它是 MAIN/Qwen (相对 _lg 的 text-embedding-3-large, 厂商与维度不同)。作为 canonical, 它与 semantic_staleness_full_lg 构成一对 co-primary: 两者各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 与 ctx / ss 两轨的关系同样是各自 just-identified 的规格稳健性并排, 绝不因相关性高就并入同一过度识别集。本列是家族在下游稳健性表中最常作为主陈旧度控制项引用的一列, 其 4096 维 Qwen 嵌入的跨厂商互证对偶恰是 _lg 列。补充几点本列特有的语义细节: full 轨读全文, 意味着它对"整篇报道层面的语义重复"最敏感——一篇把某项政策从头到尾复述一遍的报道, 即便实体窗口 (ctx) 或同句窗口 (ss) 里只有零散的银行与金科共现, 在 full 轨下仍会因全文语义与旧闻高度重合而得到高陈旧度。这使 full 轨在三轨中最不容易漏判"整体洗稿", 但也最容易把"长篇背景铺陈相似、核心增量不同"的报道误判为陈旧, 后一情形正是 ctx / ss 两条收窄参照范围的轨道作为稳健性臂存在的理由。full/MAIN 列的参照窗口用 stage 13 预筛全集 (信息环境基准不收缩), 平均域收缩到 verified full-only 留篇集; 因留篇门控本身即 full-only, 本列的逐篇宇宙与平均域在三轨中对齐得最干净, 无需 conditional-on-full 的子集截断。数值上本列受 BLAS-FP 浮点漂移影响, 逐位复现须钉死线程数。作为 core, 本列在 codebook 中承担家族 canonical 的解释重量, 其余五列的差分说明均以本列为参照系。从下游消费角度看, 本列是稳健性表里默认引用的"语义陈旧度"主变量: 当研究者在回归中控制陈旧度、或按陈旧度切分样本时, 若无特别说明, 通常指本列 (full × Qwen)。这一默认地位来自两点: full 轨的留篇集与平均域天然对齐无需子集截断, 且 Qwen 是 config 里 embedding_api 的默认 MAIN spec。但须重申"默认"不等于"主次"——本列相对 semantic_staleness_full_lg 没有任何统计上的优先权, 二者是 co-primary 对偶, 谁作报告的首列纯是命名与呈现惯例。本列与表层兄弟 surface_staleness_full 的配对使用是家族的标准实践: 二者相关性期望落在 [0.3, 0.7], 一篇真正的旧闻重印两轨俱高, 仅改写措辞的洗稿则本列 (语义) 高而 surface (词面) 低, 这一分歧本身是识别"深度洗稿"的信号, 也是本列相对表层轨不可替代的构念价值所在。

## VAR: semantic_staleness_full_lg

【变体差分】
本列是家族两个 canonical 之一 (tier=core), 与 semantic_staleness_full 共享 full 轨的参照文本 (content_full, 标题 prepend + 全文正文), 唯一差分在嵌入 spec: 本列走 _lg 孪生 spec, 即 config 的 embedding_large = text-embedding-3-large (OpenAI 系, 经 yunwu 端点, 3072 维), 而无后缀列走 MAIN/Qwen (4096 维)。_lg 后缀纯粹是命名机制以区分 co-primary 双轨中的第二个 API spec, 不含任何层级含义——它与 MAIN 列地位对等、互为稳健性, 目的是提供跨厂商 (阿里 Qwen vs OpenAI) 的独立性互证: 若同一构念在两家彼此独立的嵌入模型下都给出一致结论, 该结论就不太可能是单一嵌入模型的 artifact。计算流程与 full/MAIN 列逐字对称, 差别仅在于 Faiss IndexFlatIP 建的是 3072 维索引、检索的是 text-embedding-3-large 编码的单位归一向量; 维度无关性保证 4096 与 3072 两套向量各建各的索引、算各的余弦, 绝不混进同一次内积。both-or-neither parity 把本列与无后缀列锁死为一对: full 轨的 MAIN 与 _lg 只要任一 embed_texts 返回 None (API 重试耗尽), 该轨两列同缺, 不留单边孤儿。本列与家族其余五列的差分是: 轨道维度它是 full (相对 ctx / ss), 嵌入厂商维度它是 _lg/large (相对 MAIN/Qwen)。铁律复述: 本列与 semantic_staleness_full 各自 just-identified 并排、互为稳健性、不分主次, 严禁二者混进同一 over-identified Hansen J (co-primary 双轨的核心约束); 与 ctx_lg / ss_lg 的关系是跨轨的规格稳健性并排, 同样禁混同一过度识别集。作为 core 列, 本列承担的是"换一家嵌入厂商, 语义陈旧度结论是否依然成立"这一跨厂商稳健性检验。补充本列特有的方法学价值: Qwen 与 text-embedding-3-large 是两家训练语料、训练目标、维度 (4096 vs 3072) 全然不同的嵌入模型, 二者对"两篇中文银行报道是否语义近似"的判断若一致, 则该判断更可能反映真实的语义重复而非某一模型的表示偏置。You (2025) 恰指出余弦相似度在特定嵌入几何下可能给出误导性的"高相似", 因此单靠一家嵌入的余弦不足以支撑陈旧度结论; 本列作为无后缀 canonical 的跨厂商对偶, 正是对这一风险的直接对冲。须再次强调 _lg 与 MAIN 无主次之分——命名上的"无后缀"只是历史产物, 在 co-primary 架构里两列完全对等, 谁也不是谁的稳健性附庸。计算与聚合流程与无后缀列逐字对称 (full 轨参照文本、7 天严格排除同日行窗口、verified full-only 平均域、highstale 配套列), 唯一实质差别是 3072 维索引与 text-embedding-3-large 编码向量; 维度无关的 IndexFlatIP 保证两套维度绝不混算。本列同样受 BLAS-FP 浮点漂移影响, 逐位复现须钉死线程。作为 core, 本列与无后缀 canonical 并列构成家族的两个解释锚。在实践中, 本列常与无后缀列并排出现在同一张稳健性表的相邻两列, 用以直观展示"换厂商"前后系数的稳定性; 但二者绝不进入同一个工具变量集或同一个 over-identified Hansen J 检验——因为它们是同一构念在两家嵌入下的近乎平行的度量, 强制过度识别只会制造虚假的工具冗余并使 Hansen J 失去检验力。本列的 3072 维来自 text-embedding-3-large 的原生输出维度, 与 Qwen 的 4096 维无任何折算关系, 二者在 Faiss 中各建各的索引; 若未来更换 _lg 槽的嵌入模型, 本列的维度会随之改变而计算逻辑 (维度无关的 IndexFlatIP) 无需改动。本列的缓存命名空间由 text-embedding-3-large 的 text_pipeline_version 决定, 与 MAIN 轨的缓存键相互独立, 这保证换其中一轨的模型不会污染另一轨的缓存。

## VAR: semantic_staleness_ctx

【变体差分】
本列 tier=standard, 对应 ctx 轨 × MAIN (Qwen) 嵌入 spec。与 full 轨 canonical 的唯一差分在参照文本: ctx 轨读 content_ctx, 即"标题 prepend + 实体上下文窗口"——只保留围绕目标实体 (银行) 的上下文片段, 而非整篇全文。因此本列的语义陈旧度度量的是"实体相关语境"层面的重复度, 参照范围比 full 窄、比 ss 宽。嵌入 spec 与 full 列同为 MAIN/Qwen 4096 维, 经同一 Faiss IndexFlatIP 滚动窗口检索 top-1 余弦, 差别仅在编码的输入文本范围。ctx 轨在下游是 conditional-on-full 的稳健性 / 测度轨: 其行宇宙是 full 留篇集的子集, per-track 列照算。本列与家族其余列的差分是: 轨道维度它是 ctx (相对 full 的全文、ss 的同句窗口), 嵌入厂商维度它是 MAIN/Qwen (相对 _lg 对偶 semantic_staleness_ctx_lg)。铁律复述: ctx 与 full / ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J; 本列与其 _lg 对偶 (semantic_staleness_ctx_lg) 亦是各自 just-identified 的 co-primary 并排, 同样禁混。both-or-neither parity 保证本列与 ctx_lg 同在或同缺; content_ctx 缺列 (旧 schema) 时本轨两列均不写, 下游 stage 26 优雅缺席对应 semantic_staleness_ctx, 向后兼容不崩。本列的定位是: 当参照范围收窄到实体语境时, Qwen 嵌入下的语义陈旧度结论是否与全文轨一致。实体窗口相对全文的意义在于剥离与目标银行无关的背景铺陈: 一篇报道若正文大段复述宏观政策而仅在实体窗口内谈及本行的独家动作, 则 full 轨可能因背景相似而判高陈旧、ctx 轨却因实体语境不同而判低陈旧——两轨的分歧本身即携带信息, 提示该报道的"重复"发生在背景层而非实体层。因此本列与 full canonical 的差异不是冗余噪声, 而是参照粒度不同带来的可解释信号。

## VAR: semantic_staleness_ctx_lg

【变体差分】
本列 tier=standard, 是 ctx 轨的 _lg 对偶, 与 semantic_staleness_ctx 共享 ctx 轨参照文本 (content_ctx, 标题 prepend + 实体上下文窗口), 唯一差分在嵌入 spec: 本列走 _lg = text-embedding-3-large (OpenAI 系, 3072 维), 无后缀列走 MAIN/Qwen (4096 维)。本列因此同时在两个维度上偏离 full canonical: 轨道维度是 ctx (实体窗口而非全文), 嵌入厂商维度是 _lg/large (OpenAI 而非阿里 Qwen)。计算流程与 ctx/MAIN 列逐字对称, 仅 Faiss 索引维度换为 3072、检索 text-embedding-3-large 编码向量; 维度无关性保证两套维度绝不混算。本列的用途是跨厂商 × 收窄参照范围的双重稳健性交叉验证: 既换嵌入厂商又换参照范围后, 语义陈旧度是否依然稳健。铁律复述: 本列与 semantic_staleness_ctx 各自 just-identified 并排、互为稳健性、不分主次, 严禁二者混进同一 over-identified Hansen J (co-primary 约束); ctx_lg 与 full_lg / ss_lg 的关系是跨轨的规格稳健性并排, 同样禁混同一过度识别集。both-or-neither parity 把本列与 semantic_staleness_ctx 锁为一对 (任一 embed None 则同缺, 不留单边孤儿); content_ctx 缺列时本轨两列均不写。作为 standard 列, 本列不单独承载主结论, 只在稳健性梯子上占据"ctx 轨 × OpenAI 嵌入"这一格。这一格的独特信息在于它同时关闭了两个可能的 artifact 通道: 若语义陈旧度结论在换厂商 (Qwen→large) 后消失, 说明结论依赖单一嵌入的表示偏置; 若在收窄参照范围 (full→ctx) 后消失, 说明结论依赖全文背景的重复而非实体语境的重复。只有在本列上仍成立, 才排除了这两条通道的同时作用, 故本列是家族六列中约束最强的稳健性交叉点之一。计算与聚合与 ctx/MAIN 列对称, 仅嵌入 spec 与索引维度不同。

## VAR: semantic_staleness_ss

【变体差分】
本列 tier=standard, 对应 ss 轨 × MAIN (Qwen) 嵌入 spec。ss 轨读 content_ss, 即"标题 prepend + 银行与金科同句共现窗口 (±N 句)"——是三轨中参照范围最窄的一轨, 只保留银行与金融科技在同一句 (或邻近窗口) 共现的语境。本列于 2026-06-21 全平价上线, 镜像 ctx 轨的实现, 依赖 stage 25 为 content_ss 产出的 emb_ss 嵌入。计算上与其余 MAIN 列同型: Faiss IndexFlatIP 4096 维滚动窗口 top-1 余弦。ss 回退语义须严格按 CLAUDE.md 复述: 当某篇文章无银行与金科同句共现时, content_ss 回退为全文 body, 嵌入层 emb_ss 因此等于 emb_full; 但陈旧度层因 ss 轨的参照窗口邻居不同于 full 轨, semantic_staleness_ss 仍不等于 semantic_staleness_full——它带独立信号, 是 conditional-on-full 的稳健性轨而非纯冗余。本列与家族其余列的差分是: 轨道维度它是 ss (相对 full 的全文、ctx 的实体窗口), 嵌入厂商维度它是 MAIN/Qwen (相对 _lg 对偶 semantic_staleness_ss_lg)。铁律复述: ss 与 full / ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 本列与 ss_lg 亦是各自 just-identified 的 co-primary 并排, 同样禁混。both-or-neither 保证本列与 ss_lg 同在或同缺; emb_ss 缺列 (旧 30a parquet 未重跑 ss 轨) 时 main() 不产本列, 下游"缺列即跳过"向后兼容不崩。ss 轨的构念意义在于把参照范围压到"银行与金融科技真正同句出现"的最窄语境: 相对 ctx 的实体窗口, ss 进一步要求金科词与银行词共现于同句 (或 ±N 句窗口), 因此它度量的是"银行做金融科技这件事本身"层面的报道重复, 而非泛泛的银行报道重复。这使 ss 轨在识别"金科相关旧闻重印"时最精准, 但也最容易因回退 (无同句共现→退回全文) 而在部分行上与 full 轨的嵌入趋同; 好在陈旧度层的参照窗口邻居差异仍保证其独立信号, 故本列作为稳健性轨仍有增量价值。

## VAR: semantic_staleness_ss_lg

【变体差分】
本列 tier=standard, 是 ss 轨的 _lg 对偶, 与 semantic_staleness_ss 共享 ss 轨参照文本 (content_ss, 标题 prepend + 银行与金科同句共现窗口), 唯一差分在嵌入 spec: 本列走 _lg = text-embedding-3-large (OpenAI 系, 3072 维), 无后缀列走 MAIN/Qwen (4096 维)。本列因此在两个维度上同时偏离 full canonical: 轨道维度是 ss (最窄的同句共现窗口), 嵌入厂商维度是 _lg/large。计算流程与 ss/MAIN 列逐字对称, 仅 Faiss 索引维度为 3072、检索 text-embedding-3-large 编码的 emb_ss_lg 向量。ss 回退语义同样适用: content_ss 回退为全文时嵌入层 emb_ss_lg 等于 emb_full_lg, 但陈旧度层因 ss 参照窗口邻居不同而不等于 full_lg, 仍带独立信号。本列是家族六列中稳健性坐标最"极端"的一格——最窄参照范围 × 非主厂商嵌入的交叉——用以检验语义陈旧度结论在最严苛的参照收窄与跨厂商双重扰动下是否依然成立。铁律复述: 本列与 semantic_staleness_ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁二者混进同一 over-identified Hansen J (co-primary 约束); ss_lg 与 full_lg / ctx_lg 的关系是跨轨规格稳健性并排, 同样禁混同一过度识别集。both-or-neither parity 把本列与 semantic_staleness_ss 锁为一对 (任一 embed None 则同缺, 不留单边孤儿); emb_ss 缺列时本轨两列均不写, 下游优雅缺席不崩。本列在稳健性梯子上的坐标可概括为"最窄参照 × 最独立厂商"的双重极端: 若一个语义陈旧度结论连在同句共现窗口这一最严苛参照范围下、又经 text-embedding-3-large 这一与 Qwen 完全独立的厂商嵌入后仍然成立, 则该结论几乎不可能是参照范围人为放宽或单一嵌入偏置的产物。因此本列虽为 standard, 却在家族的稳健性论证里提供了最强的一道交叉验证。计算与聚合流程与 ss/MAIN 列逐字对称, 仅嵌入 spec 与索引维度 (3072) 不同; 维度无关的 IndexFlatIP 保证与 4096 维 Qwen 向量绝不混算, 且本列受同样的 BLAS-FP 浮点漂移约束。

<!-- rendered-citations:begin -->
Wu, C. (2025). Novelty and impact of economics papers. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.01211
You, K. (2025). Semantics at an angle: When cosine similarity works until it doesn't. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.16318
Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature, 630(8017), 625-630. https://doi.org/10.1038/s41586-024-07421-0
Han, G., Tsao, J., & Huang, X. (2024). Length-aware multi-kernel transformer for long document classification. Proceedings of the 13th Joint Conference on Lexical and Computational Semantics (*SEM 2024), 278-290. https://doi.org/10.18653/v1/2024.starsem-1.22
Bybee, L., Kelly, B. T., Manela, A., & Xiu, D. (2024). Business news and business cycles. The Journal of Finance, 79(5), 3105-3147. https://doi.org/10.1111/jofi.13377
Sevgili, Ö., Shelmanov, A., Arkhipov, M., Panchenko, A., & Biemann, C. (2022). Neural entity linking: A survey of models based on deep learning. Semantic Web, 13(3), 527-570. https://doi.org/10.3233/sw-222986
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information?. Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Reimers, N., & Gurevych, I. (2019). Sentence-BERT: Sentence embeddings using Siamese BERT-networks. Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing (EMNLP-IJCNLP), 3982-3992. https://doi.org/10.18653/v1/D19-1410
Peng, Z., Zhang, Y., & Deng, D. (2024). Near-duplicate text alignment with one permutation hashing. Proceedings of the ACM on Management of Data, 2(4), Article 222. https://doi.org/10.1145/3677136
Huang, R., Chen, X., & Wu, C. (2025). The textual similarity of news content and stock return synchronicity. Emerging Markets Review. https://doi.org/10.1016/j.ememar.2025.101309
Kumar, A., Tumre, S., & Patil, S. (2025). Benchmarking Near-Duplicate Detection in the era of Pay-walled News. Companion Proceedings of the ACM on Web Conference 2025 (WWW '25). https://doi.org/10.1145/3701716.3715303
<!-- rendered-citations:end -->
