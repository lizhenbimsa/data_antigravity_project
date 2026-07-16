---
family_id: F382
columns:
- llm_vote_cont_app_ctx
- llm_vote_cont_app_full
- llm_vote_cont_app_ss
- llm_vote_cont_ctx
- llm_vote_cont_ctx_z
- llm_vote_cont_full
- llm_vote_cont_full_z
- llm_vote_cont_hw_ctx
- llm_vote_cont_hw_full
- llm_vote_cont_hw_ss
- llm_vote_cont_hw_thr25_ctx
- llm_vote_cont_hw_thr25_full
- llm_vote_cont_hw_thr25_ss
- llm_vote_cont_hw_thr30_ctx
- llm_vote_cont_hw_thr30_full
- llm_vote_cont_hw_thr30_ss
- llm_vote_cont_hw_thr40_ctx
- llm_vote_cont_hw_thr40_full
- llm_vote_cont_hw_thr40_ss
- llm_vote_cont_hw_thr45_ctx
- llm_vote_cont_hw_thr45_full
- llm_vote_cont_hw_thr45_ss
- llm_vote_cont_mw_ctx
- llm_vote_cont_mw_full
- llm_vote_cont_mw_ss
- llm_vote_cont_ss
- llm_vote_cont_ss_z
- llm_vote_cont_tech_ctx
- llm_vote_cont_tech_full
- llm_vote_cont_tech_ss
- llm_vote_cont_vw_ctx
- llm_vote_cont_vw_full
- llm_vote_cont_vw_ss
unit: 无量纲连续情感得分 (∈ [-1, 1]; bank-year 加权/等权均值后仍落在同一有界区间内)
formula: "篇级 llm_vote_cont{track} = llm_vote_score{track} × llm_agreement_rate{track}; llm_vote_score ∈ {-1,0,+1} 为三家 LLM 多数投票共识码, llm_agreement_rate ∈ [0,1] 为投票一致率; bank-year 面板列 = 篇级值的等权/加权 (vw/mw/hw) 均值, 加权时分母 = Σweight over LLM-valid 篇 (匹配分母, 修 encode-01 向零衰减)"
producer: news_process/pipeline/panel/encode.py (encode_sentiment / build_aggregation_dict / aggregate_panel) ; news_process/pipeline/panel/runner.py (步骤 3b/3c/3d 加权列 + _build_llm_valid_masked_weights)
upstream:
- 21_tone_llms.parquet (llm_sentiment{track} / 三家逐模型标签 / llm_agreement_rate{track} / llm_verified{track})
- 24_herd_decay.parquet (herd_weight{track} 及阈值敏感性网格 herd_weight{track}_thrNN)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 40_panel_yearly.parquet (bank-year 聚合出口)
citations:
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
- doi: 10.48550/arXiv.2602.19467
  type: arxiv
  authors: Haman, M.
  year: 2026
  title: "Can large language models replace human coders? Introducing ContentBench"
  venue: arXiv
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: "Validating large language model annotations"
  venue: Finance and Economics Discussion Series (Federal Reserve Board)
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: "Majority rules: LLM ensemble is a winning approach for content categorization"
  venue: arXiv
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., ... & Yu, P. S.
  year: 2025
  title: "Harnessing multiple large language models: A survey on LLM ensemble"
  venue: arXiv
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1287/mnsc.2024.05417
  type: journal
  authors: Siano, F.
  year: 2025
  title: "The news in earnings announcement disclosures: Capturing word context using LLM methods"
  venue: Management Science
  vol: 71
  issue: 11
  pages_or_artno: 9831-9855
- doi: 10.48550/arXiv.2509.08825
  type: arxiv
  authors: Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D.
  year: 2025
  title: "Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation"
  venue: arXiv
- doi: 10.48550/arXiv.2306.04746
  type: arxiv
  authors: Egami, N., Hinck, M., Stewart, B. M., & Wei, H.
  year: 2023
  title: "Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models"
  venue: arXiv
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: The Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: "10.3390/electronics14173404"
  title: "Integrated Survey Classification and Trend Analysis via LLMs: An Ensemble Approach for Robust Literature Synthesis"
  authors: "Bernasconi, E., Redavid, D., & Ferilli, S."
  year: 2025
  venue: "Electronics"
  type: "journal"
- doi: "10.3389/frai.2025.1609097"
  title: "An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability"
  authors: "Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R."
  year: 2025
  venue: "Frontiers in Artificial Intelligence"
  type: "journal"
new_dois:
  - "10.3390/electronics14173404"
  - "10.3389/frai.2025.1609097"
---

## CORE

【构念与来源】
本家族度量"银行—金融科技"报道的连续情感极性 (continuous sentiment polarity), 是离散共识语调 llm_vote_tone 的连续孪生 (continuous twin)。构念内核有两层, 缺一不可。第一层是极性方向, 即一篇报道对目标银行的金融科技相关叙事整体偏正面、中性还是负面; 这一层是所有金融文本情感测量的公共内核, 从早期的词计数法到近期的机器学习法都在刻画它 (Tetlock, 2007; Loughran & McDonald 一脉)。第二层是极性强度, 即这一方向判断本身有多可靠、多确定。传统词典法与单一三分类模型只交付离散的 {-1,0,+1} 标签, 把"三家评审一致认定为正面"与"两家正面、一家负面勉强多数"这两种信息含量迥异的情形压成同一个 +1, 从而丢弃了标注不确定性这一重要维度。本家族的核心设计正是把这两层耦合进单一有界标量: 篇级 llm_vote_cont = llm_vote_score × llm_agreement_rate。其中 llm_vote_score ∈ {-1,0,+1} 是三家大语言模型 (gpt54nano 走 yunwu、gemini31 走 yunwu、deepseekv4 直连 api.deepseek.com) 对该篇报道情感的多数投票共识码, llm_agreement_rate ∈ [0,1] 是这三票落在共识标签上的一致率。当三家全票一致时一致率为 1, 连续值等于离散码 (±1); 当出现分裂时一致率下降, 连续值按比例向 0 收缩。由此, 一篇"全票正面"报道的连续码为 +1, 一篇"勉强多数正面"报道的连续码可能只有 +0.67, 强度差异被显式编码进变量本身。这一构念既承接金融文本情感测量传统, 又用 LLM 集成投票的一致率把标注不确定性显式量化, 呼应近年把大语言模型标注视为带噪代理、需刻画其可靠性与效度的方法学取向 (Egami et al., 2023; Hansen, 2026; Ludwig et al., 2026)。用大白话说: 它不只告诉你"这篇报道对这家银行搞金融科技是夸还是贬", 还告诉你"这个夸/贬的判断有多靠谱"——三个 AI 裁判越一致, 分值越接近满格; 越吵, 分值越往中间缩。

数据来源链条为: 原始中文银行/金科报道 (全量 约 1,819 万条量级、2007–2025、T=19; 盘上开发样本为 T=2 试跑) 经 stage 00–14 预处理、银行与金科实体识别、共现硬过滤、三轨文本物化后, 在 stage 21 (21_tone_llms) 交由三家 LLM 在冻结 Prompt (v8-2026-05-17, temperature=0.0) 下逐篇逐轨打标, 产出每篇的三家标签、共识情感 llm_sentiment{track}、一致率 llm_agreement_rate{track} 与验证位 llm_verified{track}; 面板层 (pipeline/panel/encode.py) 再据此在 encode_sentiment 内合成篇级连续码, 并在 build_aggregation_dict / aggregate_panel 内聚合到 bank-year。缓存命中键为 prompt_version='v8-2026-05-17'、temperature=0.0, 保证三轨全命中时可 NEWS_PROCESS_LLM_OFFLINE=1 离线零成本字节级复现——这正是 de Kok (2025) 所倡导的 temperature=0 / prompt 冻结 / 缓存范式在本项目的落地, 也是把 LLM 标注纳入可复现实证流程的前提。

【方法学与计算】
计算分三步, 每步都有防御性设计。第一步是篇级有效性门控与离散共识码合成 (encode.py encode_sentiment)。先构造 invalid_mask, 把矛盾旗标 (conflict / undetermined)、情感缺失 (sentiment 为 None/NaN)、以及 verified=False 的行统统标为无效; 共识 llm_vote_score 由 llm_sentiment 经 SENTIMENT_MAP 映射为 nullable Int8, 无效行落 <NA> 而非坍塌为"中性"(v6/F2 口径)。这一点关键: 若把不可信判断伪装成 0 (中性), 会系统性稀释银行-年语调并扭曲方差; 落 <NA> 则让它们干净地退出后续一切均值。第二步是连续码合成: 取一致率列 llm_agreement_rate{track} (若上游缺该列则优雅退化为常数 1.0, 此时连续码退化为纯离散码), 令 llm_vote_cont{track} = llm_vote_score{track}.astype(Float32) × 一致率, NaN 自然传播——无效行因 score 为 <NA> 而在连续码上落 NaN, 不参与任何后续聚合。第三步是 bank-year 聚合。等权变体 (无权重后缀) 取篇级连续码的 groupby mean (自动跳过 NaN); 加权变体 (vw/mw/hw) 走"分子加权和 ÷ 匹配分母"的两段式: 分子在 runner 步骤 3b/3c/3d 预乘权重后按 sum 聚合, 分母则由 _build_llm_valid_masked_weights 生成的、只覆盖"LLM 真给出判断"那批篇的权重和 (masked = weight.where(score.notna()))。这个匹配分母是一处承重修正 (encode-01): 若分子只加有效篇、分母却把全部篇的权重都算入, 加权语调会随 LLM-invalid 占比升高而系统性向 0 衰减, 等于把未判断的篇当成语调 0; 匹配分母保证分子与分母数的是同一批篇, 从根上消除该衰减偏差。逐模型/词典/BERT 族因 score=0 非 <NA>、分子分母同为全物理域, 刻意不建此 mask (加了反而失配), 只有 LLM 共识族需要。

三种加权各有清晰物理含义且相互正交, 论文须明写区分以防"变量农场"(variable farm) 质疑。vw (value-weighted) 以报道显著度 mention_density 加权, 让目标银行被密集提及的高强度覆盖占更大权重 (呼应 Tetlock, 2007 及 Hassan 一脉的注意力/显著度加权传统); mw (media-authority weighted) 以媒体权威性 media_authority_weight 加权, 让权威媒体的语调占更大权重 (信源可信度维度); hw (herd-decay weighted) 以跟风衰减权重 herd_weight 加权, 对疑似互相抄稿、信息含量重复的报道降权 (媒体信息去重维度), 其相似度判定门槛 similarity_threshold 生产口径为 0.35。三者分别加权"说得多响""谁在说""是不是原创", 维度互不重叠。z 标准化变体 (_z) 则是把等权 bank-year 列做逐年度截面标准化 (Fama-MacBeth 1973 锚点; 产列函数 pipeline/panel/geography.py::standardize_panel_variables 明确 groupby('year') 在每个年度截面内归至 μ=0/σ=1, 而非 pooled 全样本), 仅覆盖有新闻的行 (n_articles>0), 逐年门槛该年有效观测 ≥3、整列有效观测 ≥10, 便于跨规格、跨模型 β 的标准化对照。注意在 T>1 的多期面板上, 逐年度截面标准化与全样本 pooled 标准化数值不同, 论文披露口径须按逐年度截面 (年内单位方差) 表述。

【识别策略定位】
在 P1 (bank_fintech_tone) 主线里, llm_vote_cont_full 及其家族是情感处理变量 (treatment) 的连续版本, 与离散 headline llm_vote_tone_full 并排。它的识别增量在于: 离散码只区分方向, 连续码额外携带"共识强度"这一维度的横截面/时序变异, 允许检验"报道语调的强度 (而非仅方向) 是否驱动银行融资成本、存款流、金科投资等结果"。识别纪律严格遵循全仓铁律: 三轨 (full/ctx/ss)、三种加权 (vw/mw/hw)、四档跟风阈值 (thr25/30/40/45)、两类创新位置子样本 (tech/app) 均为"各自 just-identified 并排、互为稳健性、不分主次"的规格稳健性轴——它们是同一构念在不同测量设定下的平行估计, 不是可叠加的独立工具。因此严禁把任意两个变体混进同一个 over-identified 的 Hansen J 过度识别检验 (这会把测量口径差异误当成工具外生性检验)。真正的跨设定族错误率控制走根级 rwolf/FWER 模板 (Romano & Wolf, 2005 的逐步多重检验框架), 而非 Hansen J。留篇门控严格遵循 full-only 口径 (2026-06-29): 一篇是否计入"银行金科报道"只看 llm_verified_full == True, ctx/ss 降为 conditional-on-full 的子集测度轨, 其行宇宙是 full 留篇集的子集, per-track 连续码在该子集上照算。进一步说明识别的层次: 本家族提供的连续码把"共识强度"从离散方向码里解耦出来, 因而在实证设计上开辟了一条离散码不具备的识别通道——研究者可在同一回归框架内, 分别以离散 headline 与连续码进入 (二者不同时进右手边, 因高度共线), 对照系数量级与显著性, 判断结果究竟由"语调方向的翻转"驱动还是由"语调判断的确定性"驱动。这一区分对政策解读意义重大: 若融资成本仅对方向敏感, 则市场只在意媒体是褒是贬; 若对连续码 (方向 × 强度) 更敏感, 则市场进一步在意这一褒贬判断的媒体共识程度, 后者提示信息可信度而非单纯极性在定价中起作用。这一识别增量正是把 LLM 集成一致率作为"标注置信度"显式建模所换来的, 亦是本家族区别于任何单模型或纯词典连续情感的方法学价值所在 (Hansen, 2026; Ludwig et al., 2026)。此外, 连续码作为处理变量进入时, 其在同侪网络上的 leave-one-out 均值与按判据分轨的溢出项均可构造, 但这些扩展仍以本家族的集成层构念内核为唯一锚, 不改变"方向 × 共识强度"的语义定义。

【与相邻测度的构念区分】
本家族须与三组相邻测度严格区分, 以免在同一表内被误当独立信息叠加。其一, 与离散共识语调 llm_vote_tone: 后者是 {-1,0,+1} 方向码, 本家族是方向码 × 一致率的连续码, 二者共享同一投票机制与同一 verified 门控, 但连续码额外承载强度, 因此在同一回归里不应互为工具或并列进右手边 (高度相关)。其二, 与逐模型连续码 {gpt54nano,gemini31,deepseekv4}_cont: 后者是单家模型 score × 该家 confidence, 属跨厂商稳健性轨; 本家族是三家共识 score × 三家一致率, 属集成层——共识 ≠ 裸多数票, 而是经 verified 门控清票、final_v 校验后的一致率加权 (Kamen & Kamen, 2025; Chen et al., 2025 的集成投票文献表明多数票集成能提升标注稳定性)。其三, 与词典/BERT 连续情感 (Du et al., 2022 的中文金融词典; Huang et al., 2023 的 FinBERT): 三法互为稳健性、不分主次, 各自 just-identified 并排, 同样禁混同一 Hansen J。这三组区分共同确保本家族在情感三角 (LLM/词典/BERT) 与集成层级 (共识/逐模型) 中占据一个精确、不与他测度重复的坐标。还须补充第四组区分, 以杜绝表内维度冗余: 本家族与逐模型分类维度族 (subst/locus/collab 的 sub_frac/tech_frac/collab_frac) 在构念上正交——后者刻画的是"报道讲的是哪类创新"(实质创新 vs 位置 vs 协作), 是内容主题维度; 本家族刻画的是"报道的情感极性与共识强度", 是情感态度维度。二者可在同一篇上同时取值且互不决定 (一篇讲底层技术的报道既可能正面亦可能负面), 因此在回归里可作为独立协变量并列, 而非彼此的替代测量。相较之下, 本家族内的 tech/app 位置子样本仅是把情感码限定在某一创新位置的篇子集上重算, 属"同一情感构念的子样本切片", 与分类维度族的"不同构念"有本质区别: 前者是样本域的收窄, 后者是测量对象的更换。厘清这两类"看似相邻实则异质"的关系, 是避免在稳健性大表内把子样本切片误当独立信息、或把不同构念误当同一构念稳健轨的前提, 也直接决定了哪些列可以共处一张 FWER 校正表、哪些不可。

【已知局限与稳健性梯子】
局限有三, 均须在论文中如实披露。第一, 一致率作为强度代理并非无偏: 三家模型若共享训练语料偏误或提示敏感性, 高一致率可能反映系统性同质而非真正的判断置信 (Baumann et al., 2025 所警示的 LLM 标注隐性风险: 提示微扰下标注可被"操纵")。项目层面以跨模型 κ (Cohen)/α (Krippendorff) 一致性诊断与逐模型并排缓解, 并把三家投票的裸多数票与门控后共识分开审计。第二, 连续码把方向与强度耦合进单一标量, 在极性接近中性时数值不稳定: score=0 时连续码恒为 0, 丢失一致率信息; 这一耦合在 tech/app 位置子样本因篇数变薄时更突出。第三, LLM 标注作为下游回归的生成回归元 (generated regressor) 会引入测量误差, 系数须按 Ludwig et al. (2026)、Egami et al. (2023) 的框架审慎解读 (其偏差方向与放大机制有专门刻画)。效度阶梯由五层构成: 三家投票集成、冻结 Prompt (v8, temperature=0.0)、缓存字节级复现、人工盲标 κ/α 校验 (Gilardi et al., 2023; Haman, 2026 的 LLM-vs-人工编码对照)、以及与外部金融文本情感基准的收敛效度 (Siano, 2025; Lan et al., 2025 的中文金融 LLM 情感证据)。稳健性梯子沿三轨 × 三加权 × 四阈值 × 两位置逐轴展开, 每轴各自 just-identified、并排比较; 主结论若在全梯子上方向稳定, 即视为不被任一测量设定驱动, 而非依赖某一特定口径的偶然产物。此处须再申明梯子的正确统计使用方式, 以免稳健性设计被误用为过度识别工具: 三轨、三加权、四阈值、两位置这四条梯子彼此正交、互不叠加, 每条梯子的各档都是同一集成层构念在某一测量维度上的平行估计, 因此任何两档都不构成"同一参数的两个外生工具", 严禁被并入同一个 over-identified 的 Hansen J 过度识别检验——那会把纯粹的测量口径差异误读成工具外生性证据, 得出无意义的 J 统计量。跨这些平行估计的联合推断, 唯一正确的路径是根级 rwolf/FWER 逐步多重检验模板 (Romano & Wolf, 2005), 它对"同一构念在多口径下反复检验"带来的族错误率膨胀做出恰当校正, 而非借道矩条件过度识别。第四, 须警惕连续码在跨模型比较中的尺度不可比: 由于本家族基于三分类共识, 其原始方差与二分类模型 (如某些 BERT 变体) 不同, 任何跨模型 β 比较都须先做 z 标准化 (本家族的 _z 变体正为此而设), 直接比原始系数会因方差差异得出错误结论。第五, herd 加权族依赖上游 stage 24 的三轨独立 herd_weight; 若上游仅存 legacy 单列 (v3.5.x schema), 三轨会退化为同源假多轨并触发 warning, 此时 hw 族的三轨稳健性名存实亡, 须以重跑 v3.6.0+ stage 24 为前提方能采信。以上五条局限与纪律共同界定了本家族在何种条件下可作为可信实证变量、以何种统计形式进入联合推断。

【计算链路补述】
把上述三步落到面板生成的实际数据流上: stage 21 产出的篇级 21_tone_llms.parquet 携带每篇每轨的共识情感、三家逐模型标签、一致率 llm_agreement_rate{track} 与验证位; runner 在步骤 3b/3c/3d 先把篇级连续码分别乘上 mention_density (vw)、media_authority_weight (mw)、herd_weight{track} 及其阈值网格权重 (hw / hw_thrNN), 生成一批预乘列; encode 的 build_aggregation_dict 再把这些预乘列按 sum 注册进聚合字典, 同时经 _build_llm_valid_masked_weights 注册对应的匹配分母列 (_wd_{wtag}_llm{track}, 只覆盖 llm_vote_score{track}.notna() 的篇); aggregate_panel 一次 groupby 完成全部 sum/mean 聚合后, 再以"加权和 ÷ 匹配分母"两列相除得到最终的 llm_vote_cont_{vw,mw,hw}{track} 及阈值档列。等权列则直接由篇级 llm_vote_cont{track} 的 mean 得到, 无需分母修正。整条链路对无效篇的处理是一致的: 无效篇在篇级即落 NaN/<NA>, 既不进分子也不进匹配分母, 从而在等权与加权口径下都不污染银行-年均值。所有银行-年的取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在各列的【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。

【论文组合中的用途与效度证据】
在项目的多论文组合里, 本家族主要服务 P1 (bank_fintech_tone) 作为连续处理变量, 并经 tech/app 位置子样本延伸至 P4 (Gomber 一脉创新位置区分) 的技术—应用语调差构造。相较离散 headline llm_vote_tone_full, 连续码的增量价值在于它把"报道语调的共识强度"变成可回归的变异源: 当银行融资成本、存款流或金科投资等结果对"语调有多确定"而非仅"语调是正是负"敏感时, 连续码能识别出离散码无法捕捉的边际。效度上, 本家族的构念效度由多条外部证据支撑: LLM 集成投票相较单模型能提升内容分类的稳定性与准确性 (Kamen & Kamen, 2025; Chen et al., 2025); 大语言模型在文本标注任务上可媲美甚至超过众包人工编码 (Gilardi et al., 2023), 且已有系统性基准评估其替代人工编码员的边界 (Haman, 2026); 在金融文本域, LLM 方法能捕捉词序上下文、优于纯词袋 (Siano, 2025; Frankel 一脉), 中文金融情感的细粒度 LLM 分析亦有专门证据 (Lan et al., 2025); 无金标准时的 LLM 标注效度可经 κ/α 一致性设计验证 (Hansen, 2026)。这些证据共同构成本家族从"AI 打标"到"可信实证变量"的效度桥。Bernasconi、Redavid 与 Ferilli (2025, Electronics) 该文提出面向文献综合的 LLM 集成分类与趋势分析方法, 验证多次推理集成投票相较单模型单次判断能提升分类稳定性, 支持本家族三家 LLM 多数投票共识设计的方法学基础。Herrera-Poyatos 等人 (2025, Frontiers in Artificial Intelligence) 该综述系统梳理 LLM 情感分析中的模型不确定性与结果变异性来源、缓解策略及可解释性角色, 为本家族用投票一致率显式量化标注置信度这一设计提供文献支撑。

【白话总述】
用最直白的话讲, 这一整个家族回答的是一个问题: 某家银行在某一年被媒体报道搞金融科技时, 整体口碑是好是坏、这个好坏判断三个 AI 裁判有多一致? 分值在 -1 到 +1 之间, 越接近 +1 表示又正面又一致, 越接近 -1 表示又负面又一致, 接近 0 则要么是中性、要么是三个 AI 吵得没定论。家族里三十多列不是三十多个不同的东西, 而是同一个口碑分换了三种读文本的口径 (读全文 / 只读实体附近 / 只读同句)、三种给报道分权重的办法 (报道得多的更重 / 权威媒体更重 / 抄稿的打折)、四档抄稿判定松紧、以及按"讲底层技术"还是"讲应用场景"分两拨。它们互相是稳健性检查, 谁也不比谁更权威, 主结论只有在这一整排口径上都站得住, 才算不是靠某一种算法凑出来的。


【三轨口径的精确复述与回退语义】
本家族横跨三条文本轨, 其口径须精确复述以免误用。full 轨文本 = 标题 prepend + 全文正文 (content_full), 是三轨中唯一承担留篇门控的轨: 一篇是否被判为"一篇银行金科报道"只看 llm_verified_full == True (full-only 口径, 2026-06-29), 因此 full 轨的行宇宙即银行金科报道的 canonical 全集。ctx 轨文本 = 标题 prepend + 银行/金科实体窗口 (content_ctx), 意在剔除与目标叙事无关的段落; ss 轨文本 = 标题 prepend + 银行∧金科同句 ±N 句窗 (content_ss, 窗半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1), 是最严的强共现口径。ctx 与 ss 均为 conditional-on-full 的子集测度轨: 它们不独立留篇, 行宇宙恒为 full 留篇集的子集, per-track 连续码只在该子集上逐轨计算。两轨各有优雅回退: 当实体窗未命中 (content_ctx 退化为等于 content_full) 时 ctx_is_fallback=True, 该篇 ctx 轨等价于 full 轨; 当整篇不存在银行∧金科同句共现时 content_ss 回退为全文 body、ss_is_fallback=True, 该篇 ss 轨等价于全文轨 (共享 n_articles 分母, 优雅降级而非清空)。面板层以 frac_ctx_fallback / frac_ss_fallback 及对应的独立篇绝对数记录两轨相对 full 的独立度, 供论文披露每轨提供的增量信息。三轨的核心方法论纪律是: full/ctx/ss 各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨中任二混进同一 over-identified 的 Hansen J——它们是同一构念在不同文本窗口下的三个平行测量, 而非可叠加的独立工具或过度识别的多余矩条件。

【与情感三角及集成层级的坐标定位】
把本家族放进项目的情感测量全景, 它占据两个正交坐标轴上的一个精确位置。第一轴是"测量范式": 情感三角由 LLM 投票 (本家族所属)、词典法 (Du et al., 2022 的中文金融词典、Loughran-McDonald 一脉) 与 BERT 微调模型 (Huang et al., 2023 的 FinBERT 一脉) 三法构成, 三法互为稳健性、不分主次, 各自 just-identified 并排, 同样禁混同一 Hansen J。第二轴是"集成层级": 在 LLM 范式内部, 本家族是三家 verified 门控后共识 score × 三家一致率的集成层测度, 与逐模型连续码 {gpt54nano,gemini31,deepseekv4}_cont (单家 score × 单家 confidence, 属跨厂商稳健性轨) 相区别——共识不是裸多数票, 而是经 verified 清票、final_v 校验后的门控一致率加权。这一双轴定位保证本家族在整个情感测度矩阵中不与任何他测度语义重叠: 它既不是词典/BERT 的方向码, 也不是单厂商的置信码, 而是集成层的"方向 × 共识强度"连续标量。理解这一坐标是正确解读家族内各稳健性变体的前提: 所有三轨、三加权、四阈值、两位置的变体, 都是在这个固定坐标上对同一集成层构念做测量口径的横向扰动, 结论的稳健性正体现在这一横向扰动下的方向一致性。


【开发样本退化与生产规模的解读纪律】
盘上开发样本为 T=2 的极小试跑 (仅约两百个银行-年、占真实语料约万分之几), 家族内不少细分格子在该样本上会出现方差偏低甚至近零方差的退化, 尤以最严文本轨 (ss) 叠加位置子样本 (tech/app) 的格子最为突出——同句共现且属某一创新位置的篇在两年窗口内可能寥寥无几, 均值因此高度不稳。这类退化是小样本的必然产物而非代码缺陷, 生产 T=19 全量语料 (2007–2025、约 1,819 万条报道量级) 下相应格子会恢复正常方差与可解释性。因此本家族任何列的数值解读都须以生产规模为准: 不得据 T=2 开发样本的具体数值下实质性结论, 只应据其验证列的存在性、schema 一致性与零漂移复现性判断管道正确与否。与之配套, golden 快照的确定性复现要求 PYTHONHASHSEED=0 且全 BLAS 线程钉 1, 情感三轨在缓存全命中时可离线零成本字节级复现, 保证本家族取值跨 run 稳定、可审计、可追溯。

## VAR: llm_vote_cont_full

【变体差分】
本列是家族 canonical 核心列, 也是 P1 (bank_fintech_tone) 连续处理变量的锚点。轨道为 full: 篇级文本 = 标题 prepend + 全文正文 (content_full), 是三轨中唯一承担留篇门控的轨——一篇是否计入银行金科报道只看 llm_verified_full == True (full-only 口径, 2026-06-29), 因此 full 轨的行宇宙即银行金科报道的 canonical 全集, ctx 与 ss 轨都是它的子集。加权设定为等权 (无 vw/mw/hw 后缀): bank-year 值 = 该行该年全部 LLM-valid 篇的篇级 llm_vote_cont_full (= 共识 score × 一致率) 的简单算术均值 (groupby mean, 自动跳过无效行的 NaN)。数值区间 ∈ [-1, 1]: 正值代表该行该年金科报道整体偏正面且三家 AI 共识强, 接近 0 既可能是语调中性、也可能是极性方向存在分歧 (低一致率把有向码拉向 0)——解读时须结合方向占比列, 不可把 0 简单读成"中性"。负值代表整体偏负且共识强。它区别于离散孪生 llm_vote_tone_full 之处在于额外携带投票一致率这一强度维度, 使"报道语调强度"成为可回归的连续变异源; 区别于逐模型 {short}_cont_full 之处在于它是三家 verified 门控后共识 score × 三家一致率, 属集成层而非单厂商轨, 承接多数票集成提升标注稳定性的证据 (Kamen & Kamen, 2025)。作为 canonical 列, 其余 32 列 (三轨等权、vw/mw/hw 加权、thr25/30/40/45 阈值、tech/app 位置、z 标准化) 都是围绕它展开的规格稳健性变体, 与它各自 just-identified 并排、互为稳健性、不分主次, 严禁与它中任一混进同一 over-identified Hansen J; 跨设定族错误率控制走根级 rwolf/FWER 模板 (Romano & Wolf, 2005) 而非过度识别检验。作为下游回归的生成回归元, 其系数解读须计入 LLM 标注测量误差 (Ludwig et al., 2026; Egami et al., 2023), 由三家投票、冻结 Prompt (v8, temperature=0.0)、缓存字节级复现与人工盲标 κ/α 校验 (Gilardi et al., 2023; Haman, 2026) 共同支撑效度; 与外部中文金融 LLM 情感基准的收敛证据 (Lan et al., 2025; Siano, 2025) 进一步佐证其构念效度。大白话: 这一列就是"这家银行这一年被媒体报道搞金融科技, 整体口碑是好是坏、这个口碑判断三个 AI 有多一致", 是全家族的定盘星, 别的列都是换个统计口径给它做体检。


作为下游回归的连续处理变量, 本列的取值可直接进入以银行融资成本、存款流或金科投资为结果的面板回归, 也可经其 z 标准化孪生 llm_vote_cont_full_z 参与跨变量、跨模型的标准化系数对照。解读时须牢记两条: 其一, 接近 0 的取值不等于"中性报道", 可能是三家 AI 对方向存在分歧被一致率拉低, 因此须结合方向占比列与一致率列联合判读, 不可单看数值符号下结论; 其二, 本列作为生成回归元携带 LLM 标注测量误差, 系数须按应用计量框架审慎解释 (Ludwig et al., 2026), 必要时以逐模型并排、人工盲标 κ/α 与外部基准收敛效度三重证据佐证。本列的银行-年取值范围、均值、标准差与缺失率等实测统计由 codebook 生成期在【动态统计】段自动注入, 本长文不手填任何数字。

进一步地, 本列在实证中既可作为主回归的核心解释变量单独进入, 也常与其滞后项、行业同侪均值 (leave-one-out peer) 或按判据分轨的网络溢出项并列, 以刻画媒体语调强度沿时间与同侪网络的传导。无论以何种设定进入, 其构念内核始终是"该行该年金科报道的方向 × 三家 AI 共识强度"这一集成层连续标量, 不因下游用途改变。

再补三点使用纪律, 供实证与审稿共同参照。其一, 本列作为 canonical 定盘星, 是全家族三十余列稳健性变体的比较基准: 任何一档变体 (换轨、换加权、换阈值、换位置子样本) 的估计都须以本列为参照系解读其偏移方向与量级, 单看某一变体的孤立系数无从判断稳健与否。其二, 本列的等权聚合刻意不引入任何报道级权重, 因而是"每篇 LLM-valid 报道一票"的中性基准; 它与 vw/mw/hw 三加权变体各自 just-identified 并排、互为稳健性、不分主次, 严禁其中任二混进同一 over-identified Hansen J——等权与加权的差异是权重设定的差异, 不是工具外生性的证据。其三, 本列的缓存确定性使其可作为 golden 快照的稳定锚: 三轨在 _llm_cache.db 全命中且 prompt_version='v8-2026-05-17'、temperature=0.0 时, 可在 NEWS_PROCESS_LLM_OFFLINE=1 下离线零成本字节级复现 (须 PYTHONHASHSEED=0 且全 BLAS 线程钉 1), 保证本列取值跨 run 可审计、可追溯、不漂移。开发 T=2 样本上本列虽因样本极小而方差偏低, 但其存在性、schema 一致性与零漂移复现性仍可用于验证管道正确, 数值级实质结论须以生产 T=19 全量语料为准。
## VAR: llm_vote_cont_ctx

【变体差分】
本列与 canonical llm_vote_cont_full 仅在文本轨道上不同: 轨道为 ctx, 篇级文本 = 标题 prepend + 实体窗口 (content_ctx), 即只保留银行/金科实体附近的上下文窗口而非全文正文, 由 stage 14 ctx_materializer 物化。构念内核 (共识 score × 一致率)、投票机制、有效性门控、等权 bank-year mean 聚合与 full 完全一致, 唯一差别是情感判断所依据的文本范围被收窄到实体邻域, 意在过滤掉与目标银行金科叙事无关的段落噪声, 提供"聚焦上下文"下的语调估计。它是 conditional-on-full 的稳健性轨: 其行宇宙是 full 留篇集的子集 (留篇门控恒由 full 轨决定, ctx 不独立留篇), per-track 连续码在此子集上照算。当实体窗口未命中、content_ctx 退化为等于 content_full 时, ctx_is_fallback=True, 该轨在这些篇上等价于 full 轨; 面板层另有 frac_ctx_fallback (退化篇占比) 与 n_articles_for_ctx_independence (真 ctx-独立篇绝对数) 记录该轨与 full 的独立度, 供论文披露"ctx 到底提供了多少 full 之外的增量信息"。用途上, ctx 轨常作为 full 轨主结论的首要 robustness 轨, 检验语调效应是否稳健于文本聚焦范围的收窄——若效应在 ctx 轨消失, 提示原效应可能来自与金科无关的正文段落; 若稳健, 则强化"效应来自银行金科叙事本身"的解读。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨中任二混进同一 over-identified Hansen J (三轨是同一构念的三种文本窗口, 非独立工具)。大白话: 同样一批报道, 这一列只读"提到这家银行和金融科技那几句话附近"来打分, 把跑题的段落剔掉, 看结论还稳不稳。

## VAR: llm_vote_cont_ss

【变体差分】
本列轨道为 ss (sentence-scope 同句轨), 篇级文本 = 标题 prepend + "银行∧金科同句"±N 句窗 (content_ss, 窗半径由 config/filtering.yaml context_window.ss_sentence_radius 控制, 默认 1)。相对 canonical full 的差别只在文本范围: ss 是三轨中最严的聚焦, 只保留银行与金科词出现在同一句 (及邻窗) 的语境, 意在把语调锚定到"银行确实与金科同框讨论"的最强共现证据上, 排除"同一篇里银行与金科各说各的、并无实质关联"的弱共现噪声。构念内核、投票机制、有效性门控、等权 bank-year mean 聚合与 full 一致。回退语义严格镜像 ctx: 当整篇不存在银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback=True, 该篇 ss 轨等价于全文轨 (共享 n_articles 分母, 优雅降级而非清空); 面板层有 frac_ss_fallback 与 n_articles_for_ss_independence 记录独立度。它属 conditional-on-full 稳健轨, 行宇宙为 full 留篇集的子集。在 T=2 开发样本上, ss 轨常因同句共现篇稀少而方差偏低甚至退化 (近零方差), 属预期现象, 生产 T=19 语料正常。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。用途上, ss 轨提供最保守的"强共现"语调估计, 与 full (全篇) 和 ctx (实体窗) 形成由宽到严的三级证据梯度: 结论若在最严的 ss 轨仍稳健, 说服力最强。大白话: 这一列只看"银行和金融科技出现在同一句话里"的那些报道段落来打分, 是三种口径里最抠字眼、最保守的一种。

## VAR: llm_vote_cont_full_z

【变体差分】
本列是 llm_vote_cont_full 的 z 标准化变体。数值 = 把等权 full 轨 bank-year 连续码在每个年度截面内减去该年均值再除以该年标准差, 得到年内均值 0、标准差 1 的无量纲标准分——即逐年度截面标准化 (Fama-MacBeth 1973 口径), 由产列函数 pipeline/panel/geography.py::standardize_panel_variables 经 groupby('year') 实现, 仅覆盖有新闻的行 (n_articles>0)、该年有效观测 ≥3 且整列有效观测 ≥10 方标准化, 而非 pooled 全样本均值/标准差。须强调这不是全样本标准化: 在 T>1 多期面板上二者数值不同, 逐年度口径消除了年度水平漂移, 使每年的横截面可比。轨道 (full)、加权 (等权)、投票机制、有效性门控与 canonical 完全相同, 唯一差别是在面板层做了逐年度截面线性标准化。目的有二: 一是让该情感处理变量的系数在与其他量纲/尺度不同的变量并列的回归表里可直接比较大小 (标准差单位效应), 二是便于跨规格 (不同轨/加权) 与跨模型 (LLM/词典/BERT) 的标准化 β 对照——尤其在 Table A5 一类跨模型系数比较里, 因 2 分类与 3 分类测度的原始方差不同, 须先 z 标准化再比 β。它不改变任何构念内涵、样本排序或统计显著性, 只是把原始有界连续码重标度到标准正态尺度。作为 full 轨的派生标准分, 它与原始 llm_vote_cont_full 承载完全相同的信息 (二者线性完全共线), 因此绝不应同时进入同一回归的右手边; z 变体的定位是导出到 Stata 做标准化系数比较的便利列, 而非独立处理变量。与 ctx_z / ss_z 三轨标准分各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。大白话: 内容和 full 那列一模一样, 只是把分数换算成"比平均高/低几个标准差"的通用刻度, 方便和别的变量比谁的影响更大。

## VAR: llm_vote_cont_ctx_z

【变体差分】
本列是 llm_vote_cont_ctx 的 z 标准化变体: 对等权 ctx 轨 (标题 prepend + 实体窗口文本) 的 bank-year 连续码做逐年度截面均值/标准差标准化 (Fama-MacBeth 1973 口径, pipeline/panel/geography.py::standardize_panel_variables 经 groupby('year') 在每个年度截面内归一, 仅覆盖 n_articles>0 且逐年有效观测 ≥3、整列 ≥10 的行, 而非 pooled 全样本), 得年内均值 0、标准差 1 的标准分。在 T>1 多期面板上逐年度截面标准化与全样本标准化数值不同, 此处为逐年度口径。轨道为 ctx、加权为等权。相对 full_z 的唯一差别是文本范围收窄到实体邻域 (conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集); 相对原始 llm_vote_cont_ctx 的唯一差别是做了线性重标度以支持标准化系数比较。它与 llm_vote_cont_ctx 承载同一信息、完全共线, 不应同时进入同一回归右手边, 定位是便利导出列而非独立处理变量。与 full_z / ss_z 三轨标准分各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。用途是让 ctx 轨稳健性检验的标准化系数与 full 轨主结论在标准差单位上直接对照, 判断"文本聚焦范围收窄"是否改变效应量级 (而非仅方向)——若标准化 β 在 full_z 与 ctx_z 间量级相近, 说明效应稳健于文本窗口; 若量级大幅缩水, 提示原效应部分来自实体窗之外的段落。ctx 轨在实体窗未命中时退化为 full (ctx_is_fallback=True), 标准化不改变这一退化关系。大白话: 就是 ctx 那列换成通用标准差刻度, 好和 full 的标准化分数比一比"聚焦读文本"后影响力有没有缩水。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_ss_z

【变体差分】
本列是 llm_vote_cont_ss 的 z 标准化变体: 对等权 ss 同句轨 (标题 prepend + 银行∧金科同句 ±N 窗) 的 bank-year 连续码做逐年度截面标准化 (Fama-MacBeth 1973 口径, pipeline/panel/geography.py::standardize_panel_variables 经 groupby('year') 在每个年度截面内归至 μ=0/σ=1, 仅覆盖 n_articles>0 且逐年有效观测 ≥3、整列 ≥10 的行, 而非 pooled 全样本均值/标准差), 得年内均值 0、标准差 1 的标准分。在 T>1 多期面板上逐年度截面标准化与全样本标准化数值不同, 此处为逐年度口径。轨道为 ss、加权为等权。回退语义镜像 ctx: 无同句共现则底层 ss 连续码退化为全文 body 打分、ss_is_fallback=True, 标准化在此退化结果之上进行、不改变退化关系。相对 full_z/ctx_z 的差别是文本聚焦最严 (只读银行∧金科同句证据)。它与原始 llm_vote_cont_ss 完全共线, 只做线性重标度以便标准化系数比较, 绝不应与之同时进入同一回归右手边。在开发 T=2 样本上, 因同句共现篇稀少、底层 ss 连续码近零方差, 标准化后仍可能出现数值退化或极端标准分, 属预期, 生产 T=19 正常。与 full_z / ctx_z 三轨标准分各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。用途是把最保守的强共现语调估计放到标准差刻度上, 与 full/ctx 标准化系数并排, 完成"由宽到严三级证据梯度"的量级对照。大白话: 最抠字眼那一版 (ss) 换成标准差刻度, 好跟另外两版比影响力大小。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_vw_full

【变体差分】
本列是 full 轨的价值加权 (value-weighted, vw) 变体。bank-year 值 = Σ(篇级 llm_vote_cont_full × mention_density) over LLM-valid 篇 ÷ Σ(mention_density) over LLM-valid 篇。相对 canonical 等权列的唯一差别是聚合权重从等权改为报道显著度 mention_density 加权, 让高强度覆盖 (目标银行被密集提及) 的报道在银行-年语调中占更大权重, 承接 Tetlock (2007) 及注意力/显著度加权传统的思想: 一篇通篇密集讨论该行金科的深度报道, 其语调对市场认知的影响理应大于一篇一笔带过的简讯。关键实现细节是匹配分母 (encode-01 修正): 分母只累加"LLM 真给出判断"那批篇的 mention_density 权重 (masked = weight.where(score.notna())), 避免加权语调随 LLM-invalid 占比升高而系统性向 0 衰减——若不做匹配, 未判断篇的显著度会虚增分母、把加权均值往 0 拉。vw 与 mw、hw 三种加权各自 just-identified 并排、互为稳健性、不分主次, 铁律: 严禁任意两种加权混进同一 over-identified Hansen J (三加权是同一构念的三种权重设定, 非独立工具)。它检验的核心问题是"语调效应是否稳健于按报道显著度重加权", 即主结论是否被大量低显著度简讯稀释或被少数高显著度深度报道驱动; 与等权 full 并排解读即可读出显著度加权对结论的影响方向。大白话: 给"提到这家银行提得多、写得深"的报道更高话语权算出的口碑分, 看结论会不会变。

## VAR: llm_vote_cont_vw_ctx

【变体差分】
本列是 ctx 轨的价值加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × mention_density) over LLM-valid 篇 ÷ Σ(mention_density) over LLM-valid 篇, 分母为匹配分母 (只累加有判断篇的显著度权重, 修 encode-01 向零衰减)。它同时叠加两个偏离 canonical 的维度: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 加权为 mention_density 价值加权。相对 vw_full 的差别是文本聚焦到实体邻域 (剔除跑题段落); 相对等权 ctx 的差别是按报道显著度重加权 (高强度覆盖占更大权重)。用途是 ctx 轨在价值加权设定下的稳健性交叉检验: 同时收窄文本范围并按显著度加权, 若结论仍稳健, 说服力强于单一维度稳健。ctx 在实体窗未命中时退化为 full (ctx_is_fallback=True), vw 加权在退化篇上按其显著度照算。vw/mw/hw 三加权与 full/ctx/ss 三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 既聚焦读实体附近的文字、又给报道得多的稿子更高权重, 双重换口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_vw_ss

【变体差分】
本列是 ss 同句轨的价值加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ss × mention_density) over LLM-valid 篇 ÷ 匹配分母 Σ(mention_density) over LLM-valid 篇。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 加权为 mention_density 价值加权。相对 vw_full/vw_ctx 的差别是文本聚焦最严 (只读银行∧金科同句证据), 相对等权 ss 的差别是按显著度重加权。它是三轨 × 三加权网格里"最严文本 × 显著度加权"的一格, 提供最保守文本口径下的价值加权语调。开发 T=2 样本上因同句篇稀少, vw 加权后仍易方差退化, 属预期, 生产 T=19 正常。vw/mw/hw 三加权与三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。用途是把"最强共现证据 + 显著度加权"两重保守设定叠加, 作为主结论最苛刻的稳健性检查之一。大白话: 只看银行和金科同句的段落、还给报道多的稿子更高权重, 是最较真的一版加权口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_mw_full

【变体差分】
本列是 full 轨的媒体权威性加权 (media-authority weighted, mw) 变体。bank-year 值 = Σ(篇级 llm_vote_cont_full × media_authority_weight) over LLM-valid 篇 ÷ 匹配分母 Σ(media_authority_weight) over LLM-valid 篇。相对 canonical 等权列的差别是权重改为媒体权威性 (media_authority_weight, 由媒体来源的权威度经 raw_series / raw_mean 归一化而来), 让权威媒体 (如央媒、主流财经媒体) 的语调在银行-年聚合中占更大权重, 检验"报道语调效应是否被高权威媒体的声音主导"。它与 vw (显著度加权) 严格正交: mw 加权的是"谁在说"(信源权威、可信度维度), vw 加权的是"说得多响"(报道显著度维度), 二者刻画媒体影响力的不同面向, 论文须并排披露以证明加权设计非事后挑选。匹配分母同样只覆盖有判断篇 (修 encode-01, 防向零衰减)。另有并行的分层权重列 media_authority_weight_tier 作 Table A8 敏感性, 不覆盖本列的连续权重。mw 与 vw、hw 三加权各自 just-identified 并排、互为稳健性、不分主次, 铁律: 严禁任意两种加权混进同一 over-identified Hansen J。用途上, 若语调效应在 mw 加权下增强, 提示权威媒体语调更具信息含量; 若减弱, 提示效应部分来自低权威媒体的噪声。大白话: 给权威大媒体的报道更高话语权算口碑分, 看结论是不是主要由"大台大报"的口风撑起来的。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_mw_ctx

【变体差分】
本列是 ctx 轨的媒体权威性加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × media_authority_weight) over LLM-valid 篇 ÷ 匹配分母。叠加两维: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 加权为媒体权威性 media_authority_weight。相对 mw_full 的差别是文本聚焦实体邻域 (剔跑题段落); 相对等权 ctx 的差别是按信源权威重加权; 相对 vw_ctx 的差别是权重维度从"报道显著度"换成"媒体权威度"。用途是 ctx 轨在媒体权威加权下的稳健性交叉检验, 把文本聚焦与信源权威两重口径叠加。ctx 在实体窗未命中时退化为 full (ctx_is_fallback=True), mw 加权在退化篇上按其媒体权威度照算。mw/vw/hw 三加权与 full/ctx/ss 三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 既聚焦读实体附近文字、又给权威媒体更高权重, 双重换口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_mw_ss

【变体差分】
本列是 ss 同句轨的媒体权威性加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ss × media_authority_weight) over LLM-valid 篇 ÷ 匹配分母。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 加权为媒体权威性。相对 mw_full/mw_ctx 的差别是文本聚焦最严 (只读同句证据); 相对 vw_ss 的差别是权重维度换成媒体权威度。它是三轨 × 三加权网格里"最严文本 × 权威加权"的一格, 提供最保守文本口径下的媒体权威加权语调。开发 T=2 样本上同句篇稀少, 加权后仍易方差退化, 属预期, 生产 T=19 正常。mw/vw/hw 三加权与三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。用途是把"最强共现证据 + 权威信源加权"叠加, 作为主结论的苛刻稳健性检查。大白话: 只看银行金科同句段落、还给权威媒体更高权重, 是最较真的一版权威加权口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_full

【变体差分】
本列是 full 轨的跟风衰减加权 (herd-decay weighted, hw) 变体。bank-year 值 = Σ(篇级 llm_vote_cont_full × herd_weight_full) over LLM-valid 篇 ÷ 匹配分母 Σ(herd_weight_full) over LLM-valid 篇。相对 canonical 等权列的差别是权重改为跟风衰减权重 herd_weight (由 stage 24 herd_decay 计算, 对疑似互相抄稿、内容高度相似的报道降权, 从而抑制信息含量重复的报道被重复计入), 生产口径的相似度判定门槛 similarity_threshold = 0.35。它检验"语调效应是否稳健于对同质抄稿报道去重", 即主结论是否被大量互相转载/洗稿的重复报道虚增了语调信号——若一条正面通稿被上百家媒体原样转发, 等权聚合会把它算成上百篇独立正面报道, hw 加权则对这批高相似报道整体降权, 还原其真实信息含量。这一设计承接媒体信息去重与"报道量 ≠ 独立信息量"的思想 (Tetlock, 2007 一脉)。herd_weight 三轨独立 (full/ctx/ss 各自一列, v3.6.0+); ⚠ 若上游仅存 legacy 单列 herd_weight (v3.5.x schema), 三轨会退化为同源 (fake 多轨) 并触发 warning。hw 与 vw、mw 三加权各自 just-identified 并排、互为稳健性、不分主次, 铁律严禁任意两种加权混进同一 over-identified Hansen J。本列的门槛敏感性由 hw_thr25/30/40/45 系列进一步展开, 证明结论不靠 0.35 这一个抄稿门槛。大白话: 把互相抄来抄去、内容雷同的报道打个折再算口碑, 免得一条通稿被转一百遍就当成一百条独立好评。

## VAR: llm_vote_cont_hw_ctx

【变体差分】
本列是 ctx 轨的跟风衰减加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × herd_weight_ctx) over LLM-valid 篇 ÷ 匹配分母。叠加两维: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 加权为三轨独立的跟风衰减权重 herd_weight_ctx (相似度门槛 0.35)。相对 hw_full 的差别是文本聚焦实体邻域 (剔跑题段落); 相对等权 ctx 的差别是对疑似抄稿报道降权; 相对 vw_ctx/mw_ctx 的差别是权重维度换成"报道原创性/去重"。用途是 ctx 轨在跟风去重设定下的稳健性交叉检验, 把文本聚焦与抄稿去重两重口径叠加。ctx 在实体窗未命中时退化为 full (ctx_is_fallback=True), hw 加权按 herd_weight_ctx 照算。门槛敏感性由 hw_thr25/30/40/45_ctx 展开。hw/vw/mw 三加权与 full/ctx/ss 三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 既聚焦读实体附近文字、又给抄来抄去的稿子打折, 双重换口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_ss

【变体差分】
本列是 ss 同句轨的跟风衰减加权变体。bank-year 值 = Σ(篇级 llm_vote_cont_ss × herd_weight_ss) over LLM-valid 篇 ÷ 匹配分母。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 加权为三轨独立的跟风衰减权重 herd_weight_ss (相似度门槛 0.35)。相对 hw_full/hw_ctx 的差别是文本聚焦最严 (只读同句证据); 相对 vw_ss/mw_ss 的差别是权重维度换成抄稿去重。⚠ 若上游仅存 legacy 单列 herd_weight (v3.5.x schema), 三轨会退化为同源 (fake 多轨) 并触发 warning, 真三轨需重跑 v3.6.0+ 的 stage 24 (含同句 ss 轨 herd_decay)。开发 T=2 样本上同句篇稀少, 加权后仍易方差退化, 属预期。门槛敏感性由 hw_thr25/30/40/45_ss 展开。hw/vw/mw 三加权与三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 只看银行金科同句段落、还给抄稿打折, 是"最较真文本 + 去重加权"的一版口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr25_full

【变体差分】
本列是 full 轨跟风衰减加权的阈值敏感性变体, 抄稿相似度门槛 τ=0.25 (thr25)。相对 canonical hw_full (τ=0.35 生产口径) 的唯一差别是相似度判定门槛降到 0.25: 门槛越低, 越多报道被判为"相似抄稿"而降权, 去重更激进 (即便相似度只有 0.25 也算作跟风)。它属于 herd_sensitivity_grid (τ∈{0.25,0.30,0.40,0.45}, 由 core.config.herd_sensitivity_grid 单一事实源生成) 的一档, 仅施于 LLM 投票主测度族 (llm_vote_score/llm_vote_cont), 因为网格 × 全 11 测度族会导致列爆炸, 而稳健性表只需主回归 DV 的逐 τ 变体。bank-year 值 = Σ(篇级 llm_vote_cont_full × herd_weight_full_thr25) over LLM-valid 篇 ÷ 匹配分母。用途是证明主结论不依赖 0.35 这一个特定抄稿门槛: 逐 τ 各聚合出一套加权语调, 各自导进 Stata 重跑主回归, 观察系数是否稳定。thr25 是网格中去重最激进的一档 (与 thr45 最保守相对)。四档阈值 (thr25/30/40/45) 与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 铁律严禁任意两档混进同一 over-identified Hansen J (它们是同一去重机制的不同门槛, 非独立工具)。大白话: 把"算不算抄稿"的门槛调到最松 (0.25, 稍微像就算抄), 更狠地给雷同报道打折, 看结论还稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr25_ctx

【变体差分】
本列是 ctx 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.25。叠加两维: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨), 抄稿门槛 τ=0.25 (较生产口径 0.35 更激进去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × herd_weight_ctx_thr25) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr25_full 的差别是文本聚焦实体邻域; 相对 hw_ctx (τ=0.35) 的差别是门槛更低、去重更激进; 相对 hw_thr30/40/45_ctx 的差别是同一网格内门槛最低的一档。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族 (score/cont)。用途是 ctx 轨在最激进去重门槛下的稳健性交叉检验, 把文本聚焦与激进去重两重设定叠加。ctx 在实体窗未命中时退化为 full。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 聚焦读实体附近文字、再把抄稿门槛调到最松狠打折, 双重口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr25_ss

【变体差分】
本列是 ss 同句轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.25。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx), 抄稿门槛 τ=0.25 (较 0.35 更激进去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ss × herd_weight_ss_thr25) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr25_full/hw_thr25_ctx 的差别是文本聚焦最严 (只读同句证据); 相对 hw_ss (τ=0.35) 的差别是门槛更低。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。开发 T=2 样本上同句篇稀少, 激进去重后更易方差退化, 属预期, 生产 T=19 正常。它是"最严文本 × 最激进去重"的一格, 提供主结论的苛刻稳健性检查之一。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 只看同句段落、还把抄稿门槛调最松狠打折, 是很较真的一版去重口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr30_full

【变体差分】
本列是 full 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.30 (thr30)。相对 canonical hw_full (τ=0.35) 的唯一差别是抄稿相似度门槛降到 0.30, 去重较生产口径略激进但弱于 thr25 (0.25)。bank-year 值 = Σ(篇级 llm_vote_cont_full × herd_weight_full_thr30) over LLM-valid 篇 ÷ 匹配分母。它属 herd_sensitivity_grid (由 core.config.herd_sensitivity_grid 生成) 一档, 仅施于 LLM 投票主测度族 (llm_vote_score/llm_vote_cont), 避免与全测度族相乘列爆炸。用途同其他阈值档: 逐 τ 重估主回归, 证明结论不靠单一抄稿门槛; thr30 提供介于 canonical 0.35 与激进 0.25 之间的中间去重强度, 让敏感性曲线更平滑、更能看出结论对门槛的连续依赖。四档阈值 (thr25/30/40/45) 与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 铁律严禁任意两档混进同一 over-identified Hansen J。大白话: 抄稿门槛调到 0.30 (比默认稍松一点), 给雷同报道打折稍狠些, 看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr30_ctx

【变体差分】
本列是 ctx 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.30。文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 抄稿门槛 τ=0.30 (较 0.35 略激进去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × herd_weight_ctx_thr30) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr30_full 的差别是文本聚焦实体邻域; 相对 hw_ctx (τ=0.35) 的差别是门槛更低; 相对 hw_thr25/40/45_ctx 的差别是网格内的中间去重档。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。用途是 ctx 轨在中间去重门槛下的稳健性交叉检验, 让 ctx 轨的敏感性曲线与 full 轨对照。ctx 在实体窗未命中时退化为 full。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 聚焦读实体附近文字、抄稿门槛调 0.30, 双重口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr30_ss

【变体差分】
本列是 ss 同句轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.30。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 抄稿门槛 τ=0.30 (较 0.35 略激进去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ss × herd_weight_ss_thr30) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr30_full/ctx 的差别是文本聚焦最严 (只读同句证据); 相对 hw_ss (τ=0.35) 的差别是门槛更低; 相对同轨其他阈值档的差别是中间去重强度。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。开发 T=2 样本上同句篇稀少, 加权后仍易方差退化, 属预期。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 只看同句段落、抄稿门槛调 0.30, 是中等去重强度下最较真文本口径的口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr40_full

【变体差分】
本列是 full 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.40 (thr40)。相对 canonical hw_full (τ=0.35) 的唯一差别是抄稿相似度门槛升到 0.40: 门槛越高, 越少报道被判为相似抄稿、去重越保守, 更多报道保留接近等权的权重 (只有相似度达 0.40 以上才算跟风)。bank-year 值 = Σ(篇级 llm_vote_cont_full × herd_weight_full_thr40) over LLM-valid 篇 ÷ 匹配分母。它属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族 (score/cont)。用途是证明主结论在"更宽松去重"设定下同样稳健——若结论只在激进去重 (低门槛) 下成立、在保守去重 (高门槛) 下消失, 提示效应可能依赖去重强度, 反之则稳健。thr40 与 thr45 构成网格中偏保守的两档, 与 thr25/thr30 的激进两档对称, 使敏感性曲线覆盖 canonical 0.35 两侧。四档阈值 (thr25/30/40/45) 与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 铁律严禁任意两档混进同一 over-identified Hansen J。大白话: 抄稿门槛调到 0.40 (比默认更严, 不太容易算抄), 给雷同报道打折更温和, 看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr40_ctx

【变体差分】
本列是 ctx 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.40。文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 抄稿门槛 τ=0.40 (较 0.35 更保守去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × herd_weight_ctx_thr40) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr40_full 的差别是文本聚焦实体邻域; 相对 hw_ctx (τ=0.35) 的差别是门槛更高、去重更保守; 相对同轨激进档 (thr25/30) 的差别是保留更多报道接近等权。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。用途是 ctx 轨在保守去重门槛下的稳健性交叉检验, 与 ctx 轨激进档对照, 判断 ctx 轨结论对去重强度的依赖。ctx 在实体窗未命中时退化为 full。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 聚焦读实体附近文字、抄稿门槛调 0.40, 双重口径看结论稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr40_ss

【变体差分】
本列是 ss 同句轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.40。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx), 抄稿门槛 τ=0.40 (较 0.35 更保守去重)。bank-year 值 = Σ(篇级 llm_vote_cont_ss × herd_weight_ss_thr40) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr40_full/ctx 的差别是文本聚焦最严 (只读同句证据); 相对 hw_ss (τ=0.35) 的差别是门槛更高; 相对同轨激进档的差别是保留更多报道接近等权。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。开发 T=2 样本上同句篇稀少, 保守去重下更接近等权 ss, 仍易方差退化, 属预期。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 只看同句段落、抄稿门槛调 0.40 温和去重, 是保守去重下最较真文本口径的口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr45_full

【变体差分】
本列是 full 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.45 (thr45), 是敏感性网格中去重最保守的一档。相对 canonical hw_full (τ=0.35) 的唯一差别是抄稿相似度门槛升到 0.45: 只有相似度极高 (达 0.45 以上) 的报道才被判为抄稿降权, 绝大多数报道保留接近等权的权重, 因此本列的加权语调最接近等权 full 列。bank-year 值 = Σ(篇级 llm_vote_cont_full × herd_weight_full_thr45) over LLM-valid 篇 ÷ 匹配分母。它属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族 (score/cont)。用途是敏感性曲线的保守端点: 与最激进的 thr25 (0.25) 端点、canonical 0.35 中点共同勾勒结论对抄稿门槛的完整依赖轮廓; thr45 若与等权 full 结论几乎一致, 说明在极保守去重下语调信号未被去重扭曲。四档阈值 (thr25/30/40/45) 与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 铁律严禁任意两档混进同一 over-identified Hansen J。大白话: 抄稿门槛调到最严 (0.45, 几乎一模一样才算抄), 只给极度雷同的报道打折, 结果最接近不去重的原始口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr45_ctx

【变体差分】
本列是 ctx 轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.45 (网格内最保守去重档)。文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 抄稿门槛 τ=0.45。bank-year 值 = Σ(篇级 llm_vote_cont_ctx × herd_weight_ctx_thr45) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr45_full 的差别是文本聚焦实体邻域; 相对 hw_ctx (τ=0.35) 的差别是门槛更高、去重最保守 (最接近等权 ctx); 相对同轨激进档 (thr25) 的差别是敏感性曲线的另一端点。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。用途是 ctx 轨敏感性曲线的保守端点, 与 ctx 激进档对照给出 ctx 轨结论对门槛依赖的完整轮廓。ctx 在实体窗未命中时退化为 full。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 聚焦读实体附近文字、抄稿门槛调最严, 结果最接近不去重的聚焦口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_hw_thr45_ss

【变体差分】
本列是 ss 同句轨跟风衰减加权的阈值敏感性变体, 门槛 τ=0.45 (网格内最保守去重档)。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 抄稿门槛 τ=0.45。bank-year 值 = Σ(篇级 llm_vote_cont_ss × herd_weight_ss_thr45) over LLM-valid 篇 ÷ 匹配分母。相对 hw_thr45_full/ctx 的差别是文本聚焦最严 (只读同句证据); 相对 hw_ss (τ=0.35) 的差别是门槛更高、去重最保守 (最接近等权 ss); 相对同轨激进档的差别是敏感性曲线另一端点。属 herd_sensitivity_grid 一档, 仅施于 LLM 投票主测度族。开发 T=2 样本上同句篇稀少, 最保守去重下几乎等价于等权 ss, 仍易方差退化, 属预期。四档阈值与 canonical 0.35 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两档混进同一 over-identified Hansen J。大白话: 只看同句段落、抄稿门槛调最严, 是"最较真文本 + 几乎不去重"的一版口碑分。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_tech_full

【变体差分】
本列是 full 轨按创新位置 (innovation_locus) 分组的子样本连续语调, 位置类别为"底层技术"(_tech)。相对 canonical llm_vote_cont_full 的差别是: 分子/分母只覆盖被 stage 21 分类维度判为报道"底层技术"叙事 (而非应用场景) 的篇, bank-year 值 = 这些技术类篇的篇级 llm_vote_cont_full (= 共识 score × 一致率) 的等权均值 (源列 llm_vote_cont_full 按 innovation_locus 分组的 groupby mean)。它服务于 P4 (Gomber et al., 2018 一脉的金科创新位置区分: 底层技术 vs 应用场景), 用于构造技术—应用语调差 tone_gap_tech_app 等衍生测度——银行对"我们在搞底层技术 (如自研核心系统、区块链底层)"与"我们在搞应用场景 (如手机银行、场景金融)"两类叙事的媒体语调可能系统性不同, 该差值捕捉这一区分。为防组合性混杂 (compositional confound, R8 audit), 衍生语调差另设 min(n_tech, n_app) ≥ 5 的最小篇数门, 避免小样本格子被极端值主导。tech 与 app 两位置子样本各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J (二者是同一构念的两类语境子样本, 非独立工具)。轨道为 full (canonical 留篇门控轨), 加权为等权。开发 T=2 样本上技术类篇稀少时数值不稳, 属预期, 生产 T=19 正常。大白话: 只挑"报道讲这家银行搞底层技术"的稿子算口碑分, 好跟"搞应用场景"那批比一比媒体更捧哪一类。

## VAR: llm_vote_cont_tech_ctx

【变体差分】
本列是 ctx 轨的"底层技术"位置子样本连续语调。叠加两维: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 子样本限定为创新位置判为底层技术的篇, bank-year 值 = 这些技术类篇的 llm_vote_cont_ctx 等权均值。相对 tech_full 的差别是文本聚焦实体邻域 (剔跑题段落); 相对全样本 ctx 的差别是只保留技术类报道; 相对 app_ctx 的差别是位置类别相反。它服务于 P4 技术—应用语调差在 ctx 轨的稳健性交叉检验, 把文本聚焦与位置分组两重口径叠加, 验证技术—应用语调差是否稳健于文本窗口收窄。ctx 在实体窗未命中时退化为 full。tech/app 两位置与 full/ctx/ss 三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。开发 T=2 样本上技术类 × ctx 篇稀少易退化, 属预期, 生产 T=19 正常。大白话: 聚焦读实体附近文字、只挑讲底层技术的稿子算口碑, 双重口径看"搞技术"这类的媒体口风稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_tech_ss

【变体差分】
本列是 ss 同句轨的"底层技术"位置子样本连续语调。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 子样本限定为创新位置判为底层技术的篇, bank-year 值 = 这些技术类篇的 llm_vote_cont_ss 等权均值。相对 tech_full/tech_ctx 的差别是文本聚焦最严 (只读同句证据); 相对 app_ss 的差别是位置类别相反。它服务于 P4 技术—应用语调差在 ss 轨的稳健性检验, 是"最严文本 × 技术位置"的一格。开发 T=2 样本上, 同句 × 技术类双重限定后篇极稀少, 数值高度不稳甚至退化 (近零方差), 属预期, 生产 T=19 正常——此格是全家族最易在开发样本上退化的格子之一, 解读时须以生产规模为准, 不可据 T=2 数值下结论。tech/app 两位置与三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 只看同句段落、还只挑讲底层技术的稿子算口碑, 是很窄的一格, 小样本下数字会飘, 要看大样本。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_app_full

【变体差分】
本列是 full 轨按创新位置分组的子样本连续语调, 位置类别为"应用场景"(_app)。相对 canonical llm_vote_cont_full 的差别是只覆盖被判为报道金科"应用场景"叙事 (而非底层技术) 的篇, bank-year 值 = 这些应用类篇的篇级 llm_vote_cont_full (= 共识 score × 一致率) 的等权均值。它与 tech_full 构成 P4 (Gomber et al., 2018 一脉) 技术—应用二分的另一极: 二者相减即技术—应用语调差 tone_gap_tech_app (为防组合性混杂设 min(n_tech, n_app) ≥ 5 最小篇数门)。应用场景叙事 (如手机银行、消费金融场景、开放银行接口) 与底层技术叙事在媒体框架、受众关切与监管敏感度上不同, 媒体语调可能系统性偏离, 本列与 tech_full 的对照正是为捕捉这一异质性。app 与 tech 两位置子样本各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。轨道为 full (canonical 留篇门控轨), 加权为等权。开发 T=2 样本上应用类篇稀少时数值不稳, 属预期, 生产 T=19 正常。大白话: 只挑"报道讲这家银行搞应用场景 (手机银行那类)"的稿子算口碑分, 好跟"搞底层技术"那批比一比媒体更捧哪一类。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_app_ctx

【变体差分】
本列是 ctx 轨的"应用场景"位置子样本连续语调。叠加两维: 文本轨为 ctx (标题 prepend + 实体窗口, conditional-on-full 稳健轨, 行宇宙为 full 留篇集子集), 子样本限定为创新位置判为应用场景的篇, bank-year 值 = 这些应用类篇的 llm_vote_cont_ctx 等权均值。相对 app_full 的差别是文本聚焦实体邻域 (剔跑题段落); 相对全样本 ctx 的差别是只保留应用类报道; 相对 tech_ctx 的差别是位置类别相反 (应用 vs 技术)。它服务于 P4 技术—应用语调差在 ctx 轨的稳健性交叉检验, 把文本聚焦与位置分组两重口径叠加, 验证语调差是否稳健于文本窗口收窄。ctx 在实体窗未命中时退化为 full。app/tech 两位置与 full/ctx/ss 三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。开发 T=2 样本上应用类 × ctx 篇稀少易退化, 属预期。大白话: 聚焦读实体附近文字、只挑讲应用场景的稿子算口碑, 双重口径看"搞应用"这类的媒体口风稳不稳。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
## VAR: llm_vote_cont_app_ss

【变体差分】
本列是 ss 同句轨的"应用场景"位置子样本连续语调。文本轨为 ss (标题 prepend + 银行∧金科同句 ±N 窗, 回退镜像 ctx: 无同句共现则底层退化全文 body 打分、ss_is_fallback=True), 子样本限定为创新位置判为应用场景的篇, bank-year 值 = 这些应用类篇的 llm_vote_cont_ss 等权均值。相对 app_full/app_ctx 的差别是文本聚焦最严 (只读同句证据); 相对 tech_ss 的差别是位置类别相反。它服务于 P4 技术—应用语调差在 ss 轨的稳健性检验, 是"最严文本 × 应用位置"的一格。开发 T=2 样本上, 同句 × 应用类双重限定后篇极稀少, 数值高度不稳甚至退化 (近零方差), 属预期, 生产 T=19 正常——与 tech_ss 同属全家族最易在开发样本退化的格子, 解读须以生产规模为准。app/tech 两位置与三轨均为规格稳健性轴, 各自 just-identified 并排、互为稳健性、不分主次, 严禁任意两者混进同一 over-identified Hansen J。大白话: 只看同句段落、还只挑讲应用场景的稿子算口碑, 是很窄的一格, 小样本下数字会飘, 要看大样本。


补充说明: 该列的银行-年取值范围、均值、标准差与缺失率等实测分布统计, 一律由 codebook 生成期在【动态统计】段按面板实测自动注入, 本长文严禁手填任何具体数字。其留篇门控与家族 canonical 完全一致, 恒由 full 轨的 llm_verified_full 判定决定, 本列自身不独立留篇, 亦不改变行宇宙的界定。凡本列与其它文本轨道、加权口径或阈值档并列进稳健性表格时, 均以各自 just-identified 的平行估计形式呈现, 彼此互为稳健性、不分主次, 严禁任意两者合并进同一 over-identified 的 Hansen J 过度识别统计量; 跨这些测量设定的族错误率控制统一交由根级 rwolf 逐步多重检验模板处理 (Romano & Wolf, 2005 一脉), 而非借道过度识别检验。
<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
Haman, M. (2026). Can large language models replace human coders? Introducing ContentBench. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2602.19467
Hansen, A. L. (2026). Validating large language model annotations. Finance and Economics Discussion Series (Federal Reserve Board) [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., ... & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Siano, F. (2025). The news in earnings announcement disclosures: Capturing word context using LLM methods. Management Science, 71(11), 9831-9855. https://doi.org/10.1287/mnsc.2024.05417
Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.08825
Egami, N., Hinck, M., Stewart, B. M., & Wei, H. (2023). Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2306.04746
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Bernasconi, E., Redavid, D., & Ferilli, S. (2025). Integrated Survey Classification and Trend Analysis via LLMs: An Ensemble Approach for Robust Literature Synthesis. Electronics. https://doi.org/10.3390/electronics14173404
Herrera-Poyatos, D., Peláez-González, C., Zuheros, C., Herrera-Poyatos, A., Tejedor, V., Herrera, F., & Montes, R. (2025). An overview of model uncertainty and variability in LLM-based sentiment analysis: challenges, mitigation strategies, and the role of explainability. Frontiers in Artificial Intelligence. https://doi.org/10.3389/frai.2025.1609097
<!-- rendered-citations:end -->
