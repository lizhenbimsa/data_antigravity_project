---
family_id: F300
columns:
- fin_sent_zh_pos_substvalid_count_ctx
- fin_sent_zh_pos_substvalid_count_full
- fin_sent_zh_pos_substvalid_count_ss
- finbert2_pos_substvalid_count_ctx
- finbert2_pos_substvalid_count_full
- finbert2_pos_substvalid_count_ss
- finbert_cn_pos_substvalid_count_ctx
- finbert_cn_pos_substvalid_count_full
- finbert_cn_pos_substvalid_count_ss
unit: 篇数/计数 (count)
formula: bank-year 内满足「该 BERT 模型判正面 且 innovation_substantiveness (LLM 实质性判定) 非缺失」的文章篇数; groupby(target_bank, year) 对篇章级指示列 _svd_{model}_pos{track} 求和
producer: pipeline\panel\runner.py::_pool_svd_substvalid_counts (聚合) ; pipeline\sentiment\tone_berts.py (上游 BERT 概率/标签来源) ; pipeline\panel\runner.py::_svd_denom (消费, 洗稿率分母)
upstream: [21_tone_llms.parquet, 22_words_tone.parquet, 23_bert_tone.parquet, 24_herd_decay.parquet]
citations:
- doi: "10.1111/1911-3846.12832"
  type: journal
  authors: "Huang, A. H., Wang, H., & Yang, Y."
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "806-841"
- doi: "10.1145/3711896.3737219"
  type: wp
  authors: "Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z."
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: "5117-5128"
- doi: "10.1111/1911-3846.12825"
  type: journal
  authors: "Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W."
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: "Contemporary Accounting Research"
  vol: "40"
  issue: "2"
  pages_or_artno: "765-805"
- doi: "10.1016/j.jfineco.2022.08.004"
  type: journal
  authors: "Cohn, J. B., Liu, Z., & Wardlaw, M. I."
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: "Journal of Financial Economics"
  vol: "146"
  issue: "2"
  pages_or_artno: "529-551"
- doi: "10.1287/mnsc.2024.05821"
  type: "journal"
  authors: "Bennett, B., Ham, C., Milbourn, T., & Wang, Z."
  year: 2026
  title: "Firm-Level Litigation Risk: Measurement and Effects"
  venue: "Management Science"
  pages_or_artno: "mnsc.2024.05821"
new_dois: []
---

## CORE

【构念与来源】
本家族 9 列是 bank-year 计数型辅助测度, 度量「三个中文金融 BERT 模型 (finbert_cn/fin_sent_zh/finbert2) 各自判为正面情感、且该篇文章的 innovation_substantiveness (由 stage 21 LLM 三家投票产出的实质性/象征性判定) 已被成功测量 (非缺失)」的文章篇数, 按 target_bank×year×轨道 (full/ctx/ss) 汇总。它不是独立的情感或态度指标, 而是下游「洗稿率」(washing_ratio) 稳健性方法 E2 (per-model BERT 变体) 的分母同域计数, 用来修正一个具体的分子-分母失配问题。该问题的根源: 洗稿率原始设计要计算「象征性正面报道」(pos_symb, 语气正面但未落到具体可验证的创新实质) 占「实质性已测正面报道」的比例, 但若分母仍用 pos_count (物理正面篇数, 不管 innovation_substantiveness 是否被测到), 则分子隐式要求已测量、分母却把未测量的正面文章也计入, 造成系统性稀释 (fix omni-g-runner-10/g-runner-14, 2026-06-11)。本家族列即为修正后的「同域」分母。
洗稿 (greenwashing / symbolic decoupling) 概念源自组织理论的象征管理文献: Westphal & Zajac (1994, 1998, 2001) 与 Fiss & Zajac (2006) 系统论证企业可以在公开传播中采纳某种「实质性行动」的话语框架, 而实际决策与该框架脱耦 (decoupling)。本项目 P3 论文 (bank_fintech_substance) 把这一逻辑用于银行金融科技报道: 一篇报道语气正面 (pos) 不等于报道内容含有可核实的技术/创新实质 (substantive), 二者的落差即为符号治理信号。BERT 三模型给出独立于大模型 (LLM) 与词典法的第三条情感判定路线, 各自的 pos_substvalid_count 支撑「洗稿率对情感测量方法稳健」这一论证链条上的 per-model 分支。
【方法学与计算】
计算分两层。第一层 (文章级, stage 21/22/23 之后): 对每篇文章、每个 BERT 模型、每条轨道, 由 `tone_berts.py` 输出该模型在该轨道上的分类标签与三类 (或二类) 概率列 (`{model}_正面`/`_负面`/`_中性` 或对应英文键), 判正/判负采用 argmax 规则 (3-class 模型比较正面概率是否同时大于负面与中性概率; 2-class 模型用 P>0.5), 这一步是逐轨独立完成的 (full/ctx/ss 各用自己轨道的推理文本、自己轨道的模型输出)。但「实质性已测」这一半判据不逐轨独立: 源码 (`pipeline/panel/runner.py` 中 `_tt = df['innovation_substantiveness_full']`) 恒取 `innovation_substantiveness_full` 单一 full 轨列作三条轨道共用的实质性掩码 (`_subst_measured = _tt.isin(_SUBST_VALID_LABELS)`), ctx/ss 两轨的本家族列同样以这一 full 轨判定为准, 并非各自使用 ctx/ss 自己轨道的实质性标注——项目 v3.2.0 起即把 bare (非 `_full` 后缀) 的 innovation_substantiveness 删除、统一以 `_full` 作 main spec (plan v14 §3.3 P3)。因此判正部分逐轨独立、实质性已测部分三轨共用同一 full 轨判据, 得到一个仅在「该轨模型判正 且 (full 轨) 实质性已测」时为真的篇章级指示列 `_svd_{model}_pos{track}` (`_svd_` = substantiveness-valid-determined 的内部工作前缀, 不落最终面板)。
第二层 (bank-year 聚合, `pipeline/panel/runner.py::_pool_svd_substvalid_counts`): 对所有以 `_svd_` 开头的篇章级指示列, 按 `target_bank`、`year` 分组求和 (`groupby(...).sum()`), 再将列名从内部前缀 `_svd_{model}_pos{track}` 重写为面板最终名 `{model}_pos_substvalid_count{track}`。求和即计数——因为被求和的列本身是 0/1 指示, sum 等价于满足条件的篇数。三条轨道 (full=标题+正文全文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句窗口) 在「BERT 判正」这一半判据上各自独立聚合、互不借用彼此的行集合 (各轨道用各轨道自己的模型推理输出); 但如上所述,「实质性已测」这一半判据三轨共用同一 full 轨 `innovation_substantiveness_full`, 因此严格说三条轨道并非在两个判据维度上都完全独立聚合——只有判正维度逐轨独立, 掩码维度是三轨共享输入。若某轨道 BERT 上游列缺失, 对应后缀被跳过而非回退借用其他轨道判正结果; 但 full 轨 `innovation_substantiveness_full` 若缺失, 三条轨道的本家族列会同时受影响 (因为它们共享同一实质性掩码来源)。产出的 bank-year 表随后并入主面板, 供 `_svd_denom` 辅助函数在洗稿率方法 E2 (`washing_ratio_{model}{track}`) 中作除数消费: `washing_ratio_{model} = pos_symb_count_{model} / pos_substvalid_count_{model}` (`_safe_ratio` 对分母为 0 的 bank-year 输出 NaN 而非除零错误或虚假 0)。
计数列本身的统计性质: 非负整数值 (dtype 存储为 double 以兼容面板缺失值 NaN), 单调随该 bank-year 新闻覆盖量 (`n_articles`) 上升, 三模型/三轨之间存在正相关但不恒等 (因各模型判正标准、各轨道文本窗口不同)。作为分母使用时, 分母过小 (如 0 或 1) 的 bank-year 单元其洗稿率对单篇报道的抽样噪声高度敏感, 下游有对应的最小篇数/缺失口径处理, 使用者若直接消费本列做描述统计, 也应留意小样本 bank-year 的分母不稳定性。
本家族三模型 (finbert_cn/fin_sent_zh/finbert2) 互为稳健性、不分主次、各自 just-identified 并排, 禁止混进同一个 over-identified 的 Hansen J 检验 (与项目内三轨/co-primary 嵌入双轨/政治词权重梯度共享同一条铁律)。finbert2 为本项目私有微调模型, 依赖本机 `.env` 的 `FINBERT2_MODEL_DIR` 解析到有效本地权重路径; 未配置时该模型族 (含本家族对应的 3 列) 优雅整体跳过, 另两个公开 HuggingFace 模型 (finbert_cn=yiyanghkust/finbert-tone-chinese, fin_sent_zh=bardsai/finance-sentiment-zh-base) 照常产出, 这是 per-model 独立降级、非 co-primary 双轨那种 both-or-neither 硬联动。
三条轨道 (full/ctx/ss) 在「BERT 判正」这一半判据上各自 just-identified 并排, 互为稳健性、不分主次, 同样禁止混入同一 over-identified Hansen J; 但须明确, 这条并排铁律适用范围是判正逻辑与推理文本窗口的差异, 不代表三轨在「实质性已测」判据上也各自独立——如上节所述, 三轨共享同一 full 轨 innovation_substantiveness_full 掩码, 这是本家族计算口径里唯一不逐轨独立的输入, 使用者不应误以为 ctx/ss 列的实质性判定用了 ctx/ss 自己轨道的 LLM 标注。ss 轨道回退语义镜像 ctx: 当某篇文章不存在银行∧金科词同句共现时, `content_ss` 回退为全文正文 (`ss_is_fallback=True`), 该篇仍参与 ss 轨道的 BERT 推理与本家族计数, 只是其"同句"窗口实质等于全文窗口; 三轨分母 (`n_articles`) 各自独立, 不共享。留篇门控口径为 full-only (2026-06-29 后): 一篇文章是否计入"银行金科报道"样本仅由 `llm_verified_full` 判定, ctx/ss 轨的本家族计数行宇宙是 full 留篇集合的子集 (conditional-on-full), 而非独立样本。
【文献定位】
BERT 系列中文金融情感分类的方法学基础见 Huang, Wang & Yang (2023, Contemporary Accounting Research) 提出的 FinBERT 框架, 及 Xu et al. (2025) 提出的 FinBERT2 (本项目 finbert2 模型的直接方法学来源, 经金融语料专门预训练以弥合通用大模型在金融场景部署的语义缺口)。Bochkay, Brown, Leone & Tucker (2023, Contemporary Accounting Research) 对会计文本分析方法论 (含情感分类、可读性、复杂度等) 的综述文章讨论了「文本测度需多方法互证」的方法论共识, 支撑本项目 LLM/词典/BERT 三条独立路线互为稳健性的设计选择。本家族计数列的功能定位——作为比率型指标的同域分母、避免分子分母失配的稀释偏误——呼应 Cohn, Liu & Wardlaw (2022, Journal of Financial Economics) 对金融研究中计数与类计数数据处理陷阱的系统讨论 (该文强调分母选取不当会系统性扭曲比率型因变量的经济含义, 与本家族 `_svd_` 修正的动机直接对应)。 Bennett、Ham、Milbourn 与 Wang (2026) 解析 SEC 10-K 年报构造企业层面诉讼风险的简单透明测度, 以其对诉讼发生的预测力 (在控制企业特征、既有诉讼与地理因素并纳入企业固定效应后仍显著) 确立效度, 并显示该简单测度的表现与资源密集的 AI 生成测度相当, 再将其连结至现金持有、资本支出、研发与并购等政策。该文锚定本家族两环: 其一, 文本派生的实体-年计数型指标可作为面板变量, 且其效度宜以对外部结果的预测力而非构造精巧度来论证, 正对应本家族门控计数列的效度论证范式; 其二, 同一构念的简单测度与模型生成测度可表现相当, 支持把测度/模型选择显式化为互为稳健性的并排规格维度 (三模型各自 just-identified, 不混入同一 over-identified Hansen J), 而非默认复杂模型更优。⚠ 迁移边界: 原文构念是诉讼风险, 语料为每公司-年一份的美国英文 10-K, 测度由单份文档解析得到, 不存在多篇文本在实体-期内的聚合步骤, 亦无情感 softmax 概率与 BERT 三模型并排, 更无本家族特有的 LLM 实质性判定 (`innovation_substantiveness_full`) 这一重门控判据。
## VAR: fin_sent_zh_pos_substvalid_count_full

【变体差分】
本列取模型 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的中文金融情感 3-class 模型) 在 full 轨道 (标题+正文全文, `prepend_title` 拼接) 上的判正+实质性已测同域计数。full 轨道文本窗口最宽, 覆盖整篇文章可能提及的所有信息, 也因此最容易夹带与目标银行无直接关系的背景段落, 是本家族三轨中的基准/canonical 轨道, 亦是 2026-06-29 起留篇门控 (`llm_verified_full`) 的锚定轨道——本列对应的行宇宙就是决定"这是否算一篇银行金科报道"的那条判据本身所在轨道, 因此 ctx/ss 两轨的行集合都是本列行集合的子集 (conditional-on-full), 而非独立抽样。fin_sent_zh 三分类判正沿用 argmax 规则 (正面概率同时高于负面与中性概率才判正), 超长文本经滑动窗口 (`WINDOW_STRIDE_RATIO=0.5`, 50% 重叠) 切片、按置信度加权池化各窗 logits 后再统一判类, 因此长文章不因截断而系统性偏向某一情感极。fin_sent_zh 与另两模型 (finbert_cn/finbert2) 互为稳健性、不分主次、各自 just-identified 并排, 使用时不应与其他模型的同轨列混入同一 over-identified 设定, 亦不应把三模型计数直接相加当作"总正面篇数"使用 (三者判正标准与训练语料不同, 相加没有可解释的经济含义)。该列在洗稿率方法 E2 中作为分母 `_svd_denom('fin_sent_zh_pos_substvalid_count_full', pos_col)` 消费, 若分母为 0 或缺失, `_safe_ratio` 会输出 NaN 而非误导性的 0 或除零崩溃, 避免把"该银行年份完全没有可比样本"错误呈现为"洗稿率为零"。

## VAR: fin_sent_zh_pos_substvalid_count_ctx

【变体差分】
本列取模型 fin_sent_zh 在 ctx 轨道 (标题+目标银行实体窗口, `content_ctx`, 由 stage 14 `ctx_materializer` 物化) 上的判正+实质性已测同域计数。相对 full 轨道, ctx 轨道把推理文本收窄到银行实体附近的语境窗口, 剔除文章中与目标银行无直接关系的背景段落, 用于检验洗稿率方法 E2 是否对全文噪声敏感——若"正面且实质性已测"的结论仅在 full 轨道成立、在 ctx 轨道明显收缩或消失, 提示全文中与银行无关的段落可能驱动了表面的洗稿信号, 而非银行自身报道的语气与实质性落差。ctx 轨道的判正判据 (fin_sent_zh 三分类 argmax) 与 full 轨道完全一致, 唯一差异是喂给模型的输入文本窗口; 超长 ctx 窗口同样走滑动窗口+置信度池化。须注意本列的"实质性已测"半判据并非取自 ctx 轨自己的实质性标注, 而是与 full/ss 两轨共用同一 `innovation_substantiveness_full` 掩码 (详见 CORE 节), 本列真正逐轨独立的只有"判正"这一半。ctx 与 full、ss 三轨互为稳健性并排、不分主次、各自 just-identified, 禁止混入同一 over-identified Hansen J; 行宇宙始终是 full 留篇集合的子集。研究者若观察到某银行年份 full 轨道洗稿率显著、ctx 轨道明显衰减, 应把该发现解读为"银行报道整体语境中存在正面-实质性落差, 但落差主要来自银行相关段落之外", 而非否定洗稿现象本身。fin_sent_zh 的 ctx 判正与其 full 轨道使用同一套模型权重与分类头, 差异完全来自输入文本的选段方式, 因此 full/ctx 两列之间的差值可被清洁地归因于"哪些段落被纳入推理", 而非模型本身的不确定性。

## VAR: fin_sent_zh_pos_substvalid_count_ss

【变体差分】
本列取模型 fin_sent_zh 在 ss 轨道 (标题+银行∧金科同句共现窗口, `content_ss`) 上的判正+实质性已测同域计数, 判据比 ctx 更严——要求银行与金科词在同一句子内共现才纳入窗口, 而非仅实体空间邻近。当某篇文章不存在这种同句共现时, `content_ss` 回退为全文正文且 `ss_is_fallback=True`, 该篇仍照常参与 ss 轨道的 BERT 推理并计入本列 (回退语义镜像 ctx, 不因无同句共现而被剔除样本, 只是该篇的"同句窗口"实际等于全文, 与 ctx/full 分母各自独立、不互相借用)。ss 轨道用于检验洗稿信号是否即便在最严格的"银行与金科科技话题同句提及"标准下依然成立, 是三轨中判据最紧的稳健性臂; 若某银行年份的 ss 轨道计数持续偏低, 通常反映该银行的金科报道多为背景提及而非同句紧密关联, 而非模型误判。与 full/ctx 互为稳健性并排、不分主次; 同样地, 本列"实质性已测"半判据与 full/ctx 共用同一 `innovation_substantiveness_full` 掩码, 非 ss 轨自身标注。三轨联合观察时, full>ctx>ss 的递减模式属预期常态 (窗口逐步收窄), 但若某银行年份出现 ss 轨道计数反常接近甚至超过 ctx 轨道, 通常指示回退比例 (`ss_is_fallback` 占比) 偏高, 该银行金科相关报道的"同句"结构性稀少, 解读时应结合回退率一并披露而非孤立看计数绝对值。

## VAR: finbert2_pos_substvalid_count_full

【变体差分】
本列取模型 finbert2 (项目自有私有微调 2-class 模型, 依赖 `.env::FINBERT2_MODEL_DIR` 本地权重, 未配置或路径无效时该模型整族含本列优雅跳过, 另两个公开 HuggingFace 模型照常产出) 在 full 轨道上的判正+实质性已测同域计数。finbert2 为 2-class 模型 (仅正面/负面, 无独立中性类), 判正规则为 P(正面)>0.5 而非三类 argmax 比较, 与 finbert_cn/fin_sent_zh 的三分类判正逻辑存在结构性差异——这既是三模型"各自 just-identified 并排"而非可直接数值相加的原因之一, 也意味着 finbert2 的正面判定阈值语义与另两模型不完全可比, 跨模型比较应看标准化后的效应量而非原始篇数水平。finbert2 经金融语料专门预训练 (Xu et al. 2025, KDD '25), 是本项目内唯一的私有/本地部署模型, 训练语料与另两个公开模型不同源, 与它们构成方法学谱系不同但互为稳健性的三角验证 (Denzin 2017 意义上的方法三角验证)。使用本列时须注意: finbert2 缺席是本项目内已知的、按环境配置而变的常态情形 (非生产环境常缺该私有权重), 因此涉及本列的任何跨列比较或面板回归都应显式检查该列是否全 NaN, 而非默认三模型永远齐全。full 轨道是 finbert2 三列中样本量最大、也是与另两模型 full 轨道最直接可比的一列, 常作为"私有模型是否复现公开模型全文结论"的首要检验点。

## VAR: finbert2_pos_substvalid_count_ctx

【变体差分】
本列取模型 finbert2 在 ctx 轨道 (标题+银行实体窗口) 上的判正+实质性已测同域计数, 判正沿用 finbert2 的 2-class P>0.5 规则, 文本窗口收窄到银行实体附近语境, 剔除全文中与目标银行无直接关系的段落。finbert2 的 per-model 独立降级特性 (未配置本地权重时整族跳过) 对三轨均一致生效, 即 ctx 轨道本列与 full/ss 轨道的 finbert2 列同生共死 (同一模型内部 both-or-neither: 缺席则三轨齐缺), 但与另外两模型 (finbert_cn/fin_sent_zh) 之间彼此独立降级、互不连坐——finbert2 缺席不影响 finbert_cn/fin_sent_zh 任何轨道的产出。ctx 轨道用于检验私有模型对全文噪声的敏感度是否与两个公开模型一致, 是模型选择与语境窗口选择两个稳健性维度的交叉验证点之一, 与 finbert_cn/fin_sent_zh 的 ctx 列共同构成该维度上的三模型并排矩阵, 三者行宇宙相同 (均为 full 留篇集合在 ctx 轨道上的对应计数), 差异只来自各自的分类器判正标准与训练语料; 三者的"实质性已测"掩码也相同, 均取自 `innovation_substantiveness_full`, 非各自 ctx 轨独立标注。finbert2 的 2-class 判正阈值 (P>0.5) 相对三分类 argmax 更容易在概率接近临界值时翻转判定, 使用者在跨模型比较判正比例时应留意这一结构差异, 不宜直接把 finbert2 的判正率与另两个三分类模型的判正率相减解读为"模型分歧幅度"。

## VAR: finbert2_pos_substvalid_count_ss

【变体差分】
本列取模型 finbert2 在 ss 轨道 (标题+银行∧金科同句窗口) 上的判正+实质性已测同域计数, 是 finbert2 在三轨中判据最严的一支, 回退语义与另两模型的 ss 列一致 (无同句共现则 `content_ss` 回退全文、`ss_is_fallback=True`, 该篇照常计入, 不缩减样本)。作为私有本地模型在最窄且最严格的语境窗口下的输出, 本列常用于检验"洗稿信号是否受益于私有模型特有的训练语料偏差"——若结论仅在 finbert2 的 ss 轨道成立、在两个公开模型的 ss 轨道消失, 需要谨慎排查是否为 finbert2 训练语料的特异性而非真实经济信号。与 finbert_cn/fin_sent_zh 对应轨道的列并排比较、不作为单一权威判据, 且与 finbert2 的 full/ctx 两轨同受本地权重配置的 both-or-neither 约束——本地权重一旦缺失, finbert2 相关的全部 3 列 (full/ctx/ss) 一并缺席, 不存在"只缺 ss 轨道"的中间状态。ss 轨道是三轨中样本量通常最小的一支 (受限于银行∧金科同句共现本身的发生率), 本列的分母不稳定性在三模型中于 ss 轨道最为突出, 建议结合 `ss_is_fallback` 占比与 `n_articles_ss` 一并披露, 避免把小样本单元的极端 washing_ratio 值误读为强信号。若目标是评估"洗稿信号在最严格语境判据下、跨全部三个 BERT 模型是否一致", 本列须与 fin_sent_zh_pos_substvalid_count_ss、finbert_cn_pos_substvalid_count_ss 并列查看, 三者共同构成 ss 轨道的完整模型矩阵; 三者"实质性已测"半判据同源, 均取自 `innovation_substantiveness_full`, 而非 ss 轨自身的实质性标注。

## VAR: finbert_cn_pos_substvalid_count_full

【变体差分】
本列取模型 finbert_cn (yiyanghkust/finbert-tone-chinese, 公开 HuggingFace 3-class 中文金融 BERT) 在 full 轨道上的判正+实质性已测同域计数。finbert_cn 判正采用三分类 argmax 规则 (正面概率同时大于负面与中性概率才判正, 与 fin_sent_zh 判正逻辑一致但训练语料与权重完全不同), 是本项目三个 BERT 模型中训练语料公开、发布时间较早、外部学术引用较广的一个, 常在文献中被用作中文金融文本情感分析的方法学"锚点"模型, 但在本项目设计中与另两模型严格 co-equal、无 ensemble headline (BERT 三模型不像 LLM 三家那样有多数投票共识列), 不因发布时间早或引用多而在洗稿率稳健性检验中被赋予优先权重, 三模型的证据力被平等看待。finbert_cn 属公开 HF 模型, `strict_models=true` 默认配置下若加载失败会 fail-loud 直接 raise 而非静默跳过 (与 finbert2 未配置本地路径时的优雅降级形成对照), 这保证了本列在生产环境中的存在性——finbert_cn 与 fin_sent_zh 两个公开模型要么都成功产出、要么整条 pipeline 阶段报错终止, 不会出现二者之一悄然缺失而未被察觉的情形。finbert_cn 的三分类 argmax 判正逻辑与 fin_sent_zh 一致但权重、词表、训练语料完全独立训练获得, 两者若在同一 full 轨道上对同一批文章给出高度一致的判正结果, 是"洗稿信号非单一模型架构偏差"这一稳健性论证的直接证据, 反之分歧则提示需谨慎解读、按模型分列报告而非合并。

## VAR: finbert_cn_pos_substvalid_count_ctx

【变体差分】
本列取模型 finbert_cn 在 ctx 轨道 (标题+银行实体窗口) 上的判正+实质性已测同域计数, 三分类 argmax 判正规则不变, 仅推理文本窗口收窄至实体邻近语境, 剔除全文中与目标银行无直接关系的背景段落。与 fin_sent_zh_..._ctx / finbert2_..._ctx 构成同轨三模型并排比较组, 用于把"结果是否受全文无关段落干扰"这一稳健性问题同时施加于三个独立训练、独立部署的模型, 而非仅验证单一模型的敏感度; 三模型在同一 ctx 轨道上的计数模式若高度一致, 增强"洗稿信号非模型特异性伪影"的证据力, 若分歧明显则提示需按模型分别报告结果而非合并汇总。本列所在的 ctx 轨道计数, 连同 fin_sent_zh/finbert2 同轨列, 共同支撑洗稿率方法 E2 在"语境收窄是否改变结论"这一稳健性问题上的三模型联合证据, 单一模型的偶然噪声不足以撼动跨模型一致的方向性发现。finbert_cn 在 ctx 轨道上的推理同样经过超长文本滑动窗口切片 (`WINDOW_STRIDE_RATIO=0.5`) 与置信度加权池化, 窗口重叠机制确保实体附近的关键句子不因窗口边界切分而被割裂丢失语境, 这对判正结果的稳定性尤为重要, 因为 ctx 窗口通常远短于 full 全文、边界效应对结果的相对影响更大。本列的"实质性已测"半判据同三模型全轨一致, 取自 full 轨 `innovation_substantiveness_full` 单一来源, 而非 ctx 轨自身的实质性标注。

## VAR: finbert_cn_pos_substvalid_count_ss

【变体差分】
本列取模型 finbert_cn 在 ss 轨道 (标题+银行∧金科同句窗口) 上的判正+实质性已测同域计数, 是本家族 9 列中判据最严格 (同句共现) 且模型训练语料最早公开发布的一支组合。ss 轨道回退语义与全家族一致 (无同句共现回退全文、`ss_is_fallback=True` 仍计入分母, 不缩减该银行年份的可用样本)。本列与另外 8 列共同构成完整的 3 模型 × 3 轨道并排矩阵, 供洗稿率稳健性方法 E2 (per-model BERT 变体) 在模型选择与语境窗口选择两个维度上同时接受检验, 任一单列的数值高低本身不构成结论, 须结合分子 (`pos_symb_count` 同模型同轨) 一并计算 `washing_ratio_{model}{track}` 才能解读象征性/实质性落差的经济含义, 且分母过小的 bank-year 单元需留意抽样噪声。finbert_cn 与 fin_sent_zh 同为公开 HuggingFace 模型、遵循相同的 fail-loud 加载策略, 二者在 ss 轨道上的联合表现是判断"洗稿信号是否为公开可复现模型架构的稳健结论"的关键证据; 若研究者只能访问公开模型 (无法配置 finbert2 私有权重), 本列与同轨 fin_sent_zh 列即构成可完全复现的双模型稳健性对照, 不依赖任何私有资产。本列作为整个 F300 家族中判据最严、模型最"公开锚点"的一列, 常被用作 replication 包中默认展示的稳健性单元——外部审稿人无需申请项目私有的 finbert2 权重, 仅凭公开可下载的 finbert_cn 与 fin_sent_zh 两个模型即可复现本列及其同轨对照列的全部数值, 这是本家族在跨机构复现性上的一个具体着力点。与其余 8 列一致, 本列的"实质性已测"半判据取自 full 轨 `innovation_substantiveness_full`, 与 ss 轨自身的判正判据 (finbert_cn 三分类 argmax) 分属两个不同的独立性来源, 不应混淆为"ss 轨从头到尾自成一体"的完全独立测度。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25) No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Bennett, B., Ham, C., Milbourn, T., & Wang, Z. (2026). Firm-Level Litigation Risk: Measurement and Effects. Management Science, mnsc.2024.05821. https://doi.org/10.1287/mnsc.2024.05821
<!-- rendered-citations:end -->
