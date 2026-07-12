---
family_id: F118
columns:
- bert_pos_symb_count_ctx
- bert_pos_symb_count_full
- bert_pos_symb_count_ss
unit: 篇数 (非负整数计数, count)
formula: "bert_pos_symb_count{track} = Σ_{i ∈ (bank b, year t)} _is_bert_pos_symb_i{track}; _is_bert_pos_symb = 1 iff (BERT 三模型 argmax 多数票集成判为正面 _is_bert_positive == 1, 即逐模型 argmax 投正面的模型占比 > 0.5) AND (该篇被判为象征性 symbolic 披露); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/encode.py::(K 段洗稿率聚合 groupby-sum) ; news_process/pipeline/panel/runner.py::(消费为 washing_ratio_bert 分子)
upstream:
- 23_tone_berts.parquet (per-article BERT 三分类概率 → 逐模型 argmax 标签 → 模型间 argmax 多数票正面判定 _is_bert_positive)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 文章级中间指示列 _is_bert_pos_symb{track} (聚合前构造, 不落文章级 parquet)
citations:
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: 47
  pages_or_artno: 102776
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: Administrative Science Quarterly
  vol: 39
  issue: 3
  pages_or_artno: 367-390
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是「银行—年度」层面被机器判定为「正面且象征性 (positive-and-symbolic)」的报道篇数, 是洗稿率 (washing ratio, 亦称"言而无实/挑肥拣瘦"率) 家族在 BERT 集成方法下的正面象征分子。所谓象征性披露, 指语气正面、姿态积极, 却缺乏可核验的实质信息含量的报道 — 与之相对的是实质性 (substantive) 披露, 即带有具体项目、金额、时间表、可追踪承诺的报道。该二分构念的思想源头是 Westphal & Zajac (1994) 对高管长期激励计划中"实质与象征"的经典区分: 企业常以象征性动作 (宣布计划、发布姿态) 迎合外部预期, 而不必然兑现实质变化。把这一区分迁移到金融文本机器度量的, 是 Bingler et al. (2022) 关于 ClimateBERT 的研究 — 他们发现企业气候风险披露中存在大量"廉价表态 (cheap talk)"与"挑肥拣瘦 (cherry-picking)", 即选择性地只讲好听的、正面的、却无实质承诺的内容。本家族正是把"正面 × 象征"两个判据在报道层做逻辑合取, 再按银行—年度求和, 得到象征性正面报道的绝对篇数。

【方法学与计算】
计算分两层。第一层在报道层 (article level) 构造二值指示列 _is_bert_pos_symb: 一篇报道当且仅当同时满足两个条件才置 1 — 其一, 被 BERT 三模型 (finbert_cn / fin_sent_zh / finbert2) 以 argmax 多数票集成判为正面 (对应中间列 _is_bert_positive == 1); 其二, 该篇被内容属性判据判为象征性而非实质性。这里必须精确区分集成口径: BERT 概率来自 stage 23 (tone_berts) 的逐篇三分类打分, 但集成并非对情感概率取平均 — 因三模型概率尺度不可比 (finbert2 为二分类 Bernoulli, 其余为三分类), 直接平均概率会被尺度差污染。故实现改为先对每个模型在该篇上取 argmax 得到二值正面标签, 再计算"投正面 (argmax) 的模型占比"(尺度不变), 以该占比 > 0.5 作多数票判定正面。因此 _is_bert_positive 是逐模型 argmax 二值标签的多数票结果, 不是概率均值过阈值 (per-model 独立降级: 若 finbert2 因本地模型缺失而缺席, 仅掉自身一票, 不触发 co-primary 嵌入式的 both-or-neither 连坐)。第二层在 encode.py 的 K 段聚合把报道层指示列按银行—年度做 groupby 求和 (pandas agg 'sum'), 得到 bert_pos_symb_count{track}, 因此本列量纲是非负整数篇数计数, 不是比率、不是归一化分值。该计数随后在 runner.py 被 washing_ratio_bert 消费为分子, 分母是经实质验证的正面篇数 bert_pos_substvalid_count (在其缺失时安全回退到 bert_pos_count), 通过 _safe_ratio 得到 BERT 洗稿率。因此理解本列的正确姿势是: 它是一个中间计数积木, 既可单独作为象征性叙事强度的规模度量, 又是下游洗稿率的分子输入。由于 BERT 集成方法 (E) 与单模型 (E2)、词典均值 (D)、单词典 (D2)、LLM 投票 (A)、高置信子样本 (F) 等并行的多方法象征计数互为稳健性、不分主次, 各方法自成一条 just-identified 的并排证据, 严禁把不同方法的象征计数混入同一条 over-identified 的 Hansen J 过度识别检验 — 这一铁律与本仓三轨、co-primary 双轨嵌入、per-model 稳健性梯子的处置口径完全一致。

【文献定位】
本家族坐落在金融文本机器度量与"实质—象征"披露质量两条文献的交汇处。在文本度量一侧, Loughran & McDonald (2016) 对会计金融领域文本分析做了权威综述, 确立了词典法与机器学习法各有偏误、需交叉验证的方法论基线; Huang et al. (2023) 提出的 FinBERT 证明了预训练 Transformer 在金融文本情感抽取上相对词典法的增益, 是本家族 BERT 集成分量的直接方法学依托; Bochkay et al. (2023) 进一步梳理了会计文本分析"下一步"的方向, 强调从单纯的极性打分转向对披露内容质量 (如实质性、可核验性) 的刻画 — 这正是本家族在正面极性之上再叠加象征性判据的动机。Devlin et al. (2019) 的 BERT 原始工作提供了底层双向 Transformer 架构。在中文金融文本一侧, Du et al. (2022) 构建的中文金融情感词典与领域特异性发现, 支撑了本仓多方法三角化 (词典 / BERT / LLM) 的整体设计。而象征性构念的组织理论根基则回到 Westphal & Zajac (1994) 与 Bingler et al. (2022) 揭示的"廉价表态、挑肥拣瘦"机制。三轨 (full / ctx / ss) 各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J。

## VAR: bert_pos_symb_count_ctx

【变体差分】
本列是 BERT 集成象征性正面篇数的 ctx (上下文窗口) 轨变体。ctx 轨的文本载体是 content_ctx, 即"标题 prepend + 实体窗口"— 仅保留围绕目标银行与金融科技实体邻近上下文的片段, 而非整篇正文。因此本列统计的是: 在实体邻近上下文这一较窄语义视野下, 被 BERT 三模型 argmax 多数票 (逐模型 argmax 二值标签中投正面者占比 > 0.5, 非概率平均) 集成判为正面且被判为象征性的报道篇数 (按银行—年度求和)。与 full 轨相比, ctx 轨刻意剥离了远离银行—金科共现点的背景段落, 更贴近"关于该银行金融科技的这段话本身是不是廉价表态"的判断, 从而对全文级噪声更不敏感, 但也可能因窗口截断而漏掉分散在正文他处的实质信息。ctx 轨在留篇门控口径下是 conditional-on-full 的测度/稳健性轨: 行宇宙是 full 留篇集的子集, 是否算作一篇银行金融科技报道由 full 轨门控 (full-only, 2026-06-29) 决定, ctx 列在门控通过的报道上 per-track 照算。本列与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨象征计数混入同一 over-identified Hansen J 过度识别检验。作为非归一化的绝对计数, 本列既承担规模含义, 又是 ctx 轨 washing_ratio_bert 的分子输入 (分母为 ctx 轨的实质验证正面篇数)。BERT 单模型独立降级: 若某模型缺席仅影响其自身分量对集成均值的贡献, 不使本 ctx 计数连坐置空。

## VAR: bert_pos_symb_count_full

【变体差分】
本列是 BERT 集成象征性正面篇数的 full (全文) 轨变体, 也是本家族在留篇门控意义下的基准轨。full 轨的文本载体是 content_full, 即"标题 prepend + 完整正文", 是最完整的语义视野。本列统计的是: 在全文视野下被 BERT 三模型 argmax 多数票 (逐模型 argmax 二值标签中投正面者占比 > 0.5, 非情感概率平均) 集成判为正面且被判为象征性的报道篇数, 按银行—年度求和。full 轨的特殊地位在于, 全仓的留篇门控是 full-only (2026-06-29): 一篇报道是否被计为"一篇银行金融科技报道", 只看 full 轨的判定; 因此 full 轨计数的行宇宙即为该银行—年度的留篇全集, 而 ctx / ss 两轨是在此全集的子集上 conditional-on-full 地照算。相对 ctx / ss 的窗口截断视野, full 轨纳入全文所有段落, 对分散在正文各处的实质承诺信息最敏感, 是象征性判据在最丰富上下文下的判断, 但同时也更易受与银行金融科技主题弱相关的正面套话干扰。本列作为绝对计数是 full 轨 washing_ratio_bert 的分子, 分母为 full 轨的实质验证正面篇数 (缺失时安全回退 bert_pos_count)。本列与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨象征计数混入同一 over-identified Hansen J。BERT 三模型 (finbert_cn / fin_sent_zh / finbert2) 各自的 per-model 分量互为稳健性且独立降级, argmax 多数票集成非 both-or-neither 连坐, 缺一模型仅令其自身一票退出多数票。

## VAR: bert_pos_symb_count_ss

【变体差分】
本列是 BERT 集成象征性正面篇数的 ss (同句共现) 轨变体。ss 轨的文本载体是 content_ss, 即"标题 prepend + 银行与金融科技同句共现的 ±N 句窗"(窗半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语义视野最窄、聚焦度最高的一轨 — 只保留银行与金科在同一句 (及邻近极小窗) 内真正共现的文本。因此本列统计的是: 在最严格的同句共现视野下被 BERT 三模型 argmax 多数票 (逐模型 argmax 二值标签中投正面者占比 > 0.5, 非概率平均) 集成判为正面且被判为象征性的报道篇数 (按银行—年度求和)。ss 轨的关键语义是回退口径镜像 ctx: 当某篇报道不存在银行与金科的同句共现时, content_ss 优雅回退为全文正文, 且 ss_is_fallback 置 True (与 ctx 的回退语义对齐, 共享 n_articles 分母); 若上游金科词典 FINTECH_AC 为 None, 则 *_is_fallback 全 True 整体优雅降级。与 full / ctx 相比, ss 轨最直接地回答"银行金融科技这件事本身在同一句里是不是被正面而空洞地表述", 对全文与实体窗口层面的背景噪声都最不敏感, 但也最易因窗口极窄或回退而信息稀疏, 在 T=2 开发切片上可能出现零方差退化 (生产 T=18 正常)。本列在留篇门控下同为 conditional-on-full 轨, 行宇宙是 full 留篇集子集。本列与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨象征计数混入同一 over-identified Hansen J。作为绝对计数, 本列是 ss 轨 washing_ratio_bert 的分子; BERT 单模型独立降级不连坐。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
<!-- rendered-citations:end -->
