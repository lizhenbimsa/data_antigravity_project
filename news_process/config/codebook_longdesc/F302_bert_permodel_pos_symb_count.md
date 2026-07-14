---
family_id: F302
columns:
- fin_sent_zh_pos_symb_count_ctx
- fin_sent_zh_pos_symb_count_full
- fin_sent_zh_pos_symb_count_ss
- finbert2_pos_symb_count_ctx
- finbert2_pos_symb_count_full
- finbert2_pos_symb_count_ss
- finbert_cn_pos_symb_count_ctx
- finbert_cn_pos_symb_count_full
- finbert_cn_pos_symb_count_ss
unit: 篇数 (bank-year 计数, 非负整数)
formula: "{b}_pos_symb_count{track} = Σ_{i∈(bank,year)} _is_{b}_pos_symb_i{track}; _is_{b}_pos_symb = 1 iff (单模型 argmax 标签 == 正面, 即 _is_{b}_positive{track} == 1) AND (该篇 innovation_substantiveness_full == '象征性'); b ∈ {finbert_cn, fin_sent_zh, finbert2}, track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (逐篇 _is_{b}_pos_symb{track} 指示构造) ; news_process/pipeline/panel/encode.py (E2 段 groupby-sum 聚合入 bank-year 面板)
upstream:
- 23_tone_berts.parquet (finbert_cn / fin_sent_zh / finbert2 三模型逐篇三轨概率与 argmax 标签)
- 21_tone_llms.parquet (innovation_substantiveness_full 实质/象征分类)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
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
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
new_dois: []
---

## CORE

【构念与来源】
本家族是「银行—年度」层面「正面且象征性 (positive-and-symbolic)」报道篇数在 BERT 单模型 (per-model) 口径下的计数, 与 F118 的 BERT 三模型集成计数 (bert_pos_symb_count) 是并排而非替代的关系: F118 用三模型 argmax 多数票集成后再判正面, 本家族则把 finbert_cn (yiyanghkust/finbert-tone-chinese, HF 三分类 中性/正面/负面)、fin_sent_zh (bardsai/finance-sentiment-zh-base, HF 基于 Financial PhraseBank 微调, 三分类)、finbert2 (项目私有微调模型, 二分类 负面/正面, 经 .env `FINBERT2_MODEL_DIR` 解析) 三个模型各自单独统计, 每模型再按 full/ctx/ss 三条文本轨各自单独统计, 共 3 模型 × 3 轨 = 9 列。所谓"象征性", 沿用 Westphal & Zajac (1998) 在公司治理研究中确立的实质—象征二元框架的迁移应用: 一篇报道若只在话语层面宣示某种金融科技姿态、却缺乏可核验的落地内容 (投入规模、系统上线、产品交付、组织变革等), 即判为象征性 (symbolic / decoupling / cheap talk); 反之若有实体证据支撑则判为实质性 (substantive)。Bingler et al. (2022) 把这一二元框架应用到 ClimateBERT 对企业气候披露的度量上, 揭示出企业气候话语中大量"廉价表态 (cheap talk)"与"挑肥拣瘦 (cherry-picking)"的模式 — 本家族把该识别策略迁移到银行金融科技媒体报道语境, 用"正面 × 象征"两条判据的逻辑合取, 刻画"银行被媒体正面报道、但报道内容偏空谈"的那一类篇章, 是下游"洗稿率/象征化占比"这一构念的分子来源之一。白话说: 这九个数是"某个 BERT 模型认为一家银行这一年被'又正面、又是空谈'地报道了几篇", 三个模型各自数一遍、三条文本范围各自数一遍, 互不替代。

【方法学与计算】
计算分两层, 均在 pipeline/panel/runner.py 与 encode.py 中完成。第一层在报道层构造二值指示列 _is_{b}_pos_symb{track}: 对每个 BERT 模型 b、每条轨 track, 一篇报道当且仅当同时满足两个条件才置 1 — 其一, 该模型该轨的 argmax 标签为正面 (对应中间列 _is_{b}_positive{track} == 1, 由 stage 23 tone_berts 产出的逐模型逐轨概率取 argmax 得到, 而非概率阈值软判; finbert2 为二分类, 其余两模型为三分类, 三者各自独立按自身标签空间取 argmax, 不做跨模型概率平均以规避尺度不可比问题); 其二, 该篇 innovation_substantiveness_full 判为"象征性"。这里有一处承重且贯穿全九列的口径: 象征-实质判定固定取 full 轨的 innovation_substantiveness_full (由 stage 21 LLM 输出), 不随 BERT 的 track 切换, 因此 ctx/ss 轨列的语义是"用该 BERT 模型 ctx/ss 轨的正面判定 × full 轨的象征判定"的乘积, 而非在 ctx/ss 文本上重判象征性。第二层在 encode.py 的 K 段洗稿率聚合块 (E2: 单个 BERT, 与家族注释 `# E2: 单个 BERT (Huang et al. 2023, CAR)` 对应) 中, 对每个模型 b 与每条轨 track 分别执行 groupby(bank, year).sum(), 把逐篇 0/1 指示折算为 bank-year 计数, 因此本列量纲是非负整数计数, 不是比率也不是归一化分值。计数落在留篇门控 (full-only, 2026-06-29) 界定的宇宙内: 一篇报道是否算作"一篇银行金融科技报道"只看 llm_verified_full, ctx/ss 是 conditional-on-full 的子集轨, per-track 分子各自独立累计, 不跨轨借值。BERT 单模型独立降级: finbert2 若因 `FINBERT2_MODEL_DIR` 未配置而缺席, 仅令 finbert2_pos_symb_count{track} 三列全为 NaN 后续零填, 不触发 co-primary 嵌入式的 both-or-neither 连坐, 另两模型 (finbert_cn/fin_sent_zh) 照常出值。三模型推理确定性来自模型权重固定与 argmax 判定 (AMP 混合精度对分类结果无影响), 与 stage 21 三家大模型 LLM 完全独立 (换嵌入模型不影响本家族; BERT 亦与嵌入模型无关)。⚠ 铁律: 三模型各自 just-identified 并排、三轨各自 just-identified 并排, 彼此互为稳健性、不分主次, 严禁把不同模型或不同轨的计数混进同一 over-identified 的 Hansen J 检验。

【文献定位】
本家族坐落在"用预训练金融领域 Transformer 对中文新闻做情感极性标注、并与实质—象征二元判据交叉相乘构造计数测度"的方法学传统上。Huang et al. (2023) 在 Contemporary Accounting Research 上提出的 FinBERT 证明了预训练金融领域 Transformer 相对词典法在情感抽取上的增益, 是本家族三个 BERT 模型 (finbert_cn/fin_sent_zh/finbert2) 方法学依托的直接来源; Bochkay et al. (2023) 同刊进一步综述了会计文本分析"下一步"的方向, 主张从单纯极性打分转向对披露内容质量 (实质性、可核验性) 的刻画, 这正是本家族在正面极性之上叠加象征性判据的动机。Loughran & McDonald (2016) 在 Journal of Accounting Research 对会计金融文本分析方法做了权威综述, 确立了计数型测度需多方法交叉验证的规范, 支撑本仓词典法 (D/D2)、LLM 投票法 (A/A2)、BERT 集成法 (E) 与本家族 BERT per-model 法 (E2) 并列互证的整体设计。象征性构念本身的组织理论根基是 Westphal & Zajac (1998) 关于公司治理改革中"股东象征性管理"的经典论述, 并经 Bingler et al. (2022) 在气候披露语境下复活为 cheap talk 的机器可测度量。Du et al. (2022) 在 Review of Finance 构建的中文金融情感词典及其领域特异性发现, 支撑了本仓多方法三角化 (词典/BERT/LLM) 的整体设计思路与中文语境适配的必要性。三模型、三轨两个维度均各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J。

## VAR: fin_sent_zh_pos_symb_count_ctx

【变体差分】
本列取 fin_sent_zh (bardsai/finance-sentiment-zh-base, HF 三分类, 基于 Financial PhraseBank 微调) 在 ctx 轨的 argmax 正面判定与 full 轨的象征判定 (innovation_substantiveness_full == '象征性') 相乘后的 bank-year 计数。ctx 轨文本 content_ctx = 标题 prepend + 目标银行实体邻近窗口, 相较 full 轨剔除了与目标银行无关的段落, 因此正面判定 _is_fin_sent_zh_positive_ctx 是在"聚焦银行的窄语境"上判定的; 象征这一半仍固定取 full 轨分类, 不随本列所在的 ctx 轨切换, 即本列并非在 ctx 文本上重判象征性。与同族 fin_sent_zh_pos_symb_count_full 的差异纯在正面判定所用的文本轨: ctx 语料更窄, 计数一般不超过 full 列; 与 finbert_cn / finbert2 的同轨 ctx 列并排构成跨模型稳健性, 三模型各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列落在 full-only 留篇门控宇宙内, ctx 为 conditional-on-full 子集轨, fin_sent_zh 在该篇 ctx 轨推理失败或空文本时对应 argmax 判定不成立、该篇不入分子, 不借 full/ss 轨分值填补。下游用法上本列充当"正面且象征"的分子, 与同域分母 (该模型 ctx 轨已实质验证的正面篇数) 相除即得 fin_sent_zh 一支 ctx 轨的象征化占比 (洗稿率的一支)。作为三分类模型, fin_sent_zh 的中性/正面/负面判别边界与 finbert_cn 训练语料不同、与 finbert2 的二分类边界更不可比, 三者的绝对计数不宜直接比较水平, 应各自作为独立稳健性证据看待。

## VAR: fin_sent_zh_pos_symb_count_full

【变体差分】
本列取 fin_sent_zh 在 full 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是 fin_sent_zh 一支的基准轨。full 轨文本 content_full = 标题 prepend + 完整正文, 与留篇门控同轨 (full-only, 2026-06-29), 本列行宇宙即该银行—年度的 full 留篇集本身, 而非其子集。正面判定 _is_fin_sent_zh_positive_full 在完整正文上取 argmax, 象征判定同取 full 轨, 两半同轨、语义最自洽, 三轨中信息最全, 计数通常最大。与 finbert_cn_pos_symb_count_full、finbert2_pos_symb_count_full 并排即跨模型 per-model 稳健性梯子的基准轨对照, 三模型各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。fin_sent_zh 基于 Financial PhraseBank (英文金融语料) 微调迁移到中文场景, 其正面判别边界可能系统性不同于专为中文金融语料训练的 finbert_cn, 这一差异正是跨模型并排要暴露而非抹平的稳健性维度。fin_sent_zh 该篇推理失败 (批级异常重试仍失败、写失败哨兵 label=None) 时不计入分子, 与空文本 (num_windows=0) 严格区分处理但结果同样不入分子。下游以同域分母 (fin_sent_zh full 轨实质验证正面篇数) 相除得该模型 full 轨洗稿率。本列作为绝对整数计数, 既可单独衡量该模型认定的象征性叙事规模, 亦是三模型 (finbert_cn/fin_sent_zh/finbert2) 与 F118 集成口径 (三模型 argmax 多数票) 相区分的独立一支证据。超长文本经滑动窗口切片 (WINDOW_STRIDE_RATIO=0.5, 单窗≤512 token 含特殊符, 有效正文≤510 token) 分段推理, 各窗按置信度加权池化 logits 后再取 argmax, 因此本列的正面判定并非简单截断首尾, 而是覆盖全文所有窗口的置信度加权综合结果, 长报道不因超长而系统性漏判。

## VAR: fin_sent_zh_pos_symb_count_ss

【变体差分】
本列取 fin_sent_zh 在 ss 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨文本 content_ss = 标题 prepend + 银行∧金融科技词同句共现片段及其 ±窗口 (窗半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1), 是三轨中语境最严的一轨; 当某篇不存在银行∧金科同句共现时, ss 镜像 ctx 的回退语义, content_ss 优雅退回全文正文并置 ss_is_fallback=True (与 ctx 回退口径对齐, 共享 n_articles 分母)。因此本列正面判定 _is_fin_sent_zh_positive_ss 是在"银行与金科真正同句"的最窄语料上取 argmax (回退篇则等价 full 口径), 象征判定仍固定取 full 轨。与同族 full/ctx 列的差异纯在正面判定所用文本轨: ss 语料最窄, 计数一般最小, 但回退篇会拉高该列使其不必然严格小于 ctx。与 finbert_cn/finbert2 的同轨 ss 列并排为跨模型稳健性; 三轨与三模型两个维度均各自 just-identified 并排、互为稳健性不分主次, 严禁混同一 over-identified Hansen J。本列亦落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨。ss 轨的构造意图是把语境收到"银行与金融科技真正同句"的最严口径, 检验象征化叙事计数是否对语境窗口的选择稳健, 若三轨结论一致则不由某种特定语境切法驱动。若上游金融科技词典 FINTECH_AC 为 None (整体禁用金科识别), *_is_fallback 全体置 True, 本列在此极端情形下优雅退化为等价 full 轨口径, 而非报错或产生垃圾计数, 与本仓"绝不静默清空"的安全设计一致。下游以同域分母 (fin_sent_zh ss 轨实质验证正面篇数) 相除得该模型 ss 轨洗稿率, 与 full/ctx 两轨并列构成 fin_sent_zh 一支内部的语境敏感性完整证据链。

## VAR: finbert2_pos_symb_count_ctx

【变体差分】
本列取 finbert2 (项目私有微调模型, 二分类 负面/正面, 经 .env `FINBERT2_MODEL_DIR` 解析) 在 ctx 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ctx 轨文本 content_ctx 聚焦目标银行实体邻近窗口, 正面判定 _is_finbert2_positive_ctx 是在窄语境上取 argmax, 象征判定固定取 full 轨。finbert2 是二分类模型 (无中性类), 其正面/负面二元判别与另两个三分类模型 (finbert_cn/fin_sent_zh) 的判别空间结构不同 — 三分类模型的"正面"是在正面/中性/负面三者中获胜, 而 finbert2 的"正面"只需在正面/负面二者中获胜, 因此 finbert2 的正面计数在同等语料下可能系统性高于三分类模型 (因无中性选项分流), 三模型计数不宜直接比较绝对水平, 只作跨模型稳健性并排。与同族 finbert2_pos_symb_count_full 的差异纯在正面判定文本轨 (ctx 语料更窄, 计数一般不超过 full)。⚠ 外部依赖: FINBERT2_MODEL_DIR 未配置或路径不存在时 finbert2 整体优雅跳过, 本列 (及 finbert2 家族全部列) 呈 NaN、encode 后按计数列契约零填, 不影响 finbert_cn/fin_sent_zh 两模型照常出值 (per-model 独立降级, 非 co-primary 嵌入式 both-or-neither 连坐)。本列落在 full-only 留篇宇宙内, ctx 为 conditional-on-full 子集轨; 与 finbert_cn/fin_sent_zh 同轨列并排构成跨模型稳健性, 三模型各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。finbert2 作为项目自训练的私有模型, 不依赖外网 Hugging Face Hub 拉取, 部署时无需设置 `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE`, 与另两个 HF 公开模型的离线重跑约束互不相关; 其权重固定、推理仅取 argmax, 确定性不受 AMP 混合精度影响, 生产语料重跑时结果字节级可复现。

## VAR: finbert2_pos_symb_count_full

【变体差分】
本列取 finbert2 在 full 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是 finbert2 一支的基准轨。full 轨文本 content_full 与留篇门控同轨 (full-only, 2026-06-29), 本列行宇宙即该银行—年度的 full 留篇集本身。正面判定与象征判定两半同取 full 轨, 语义最自洽, 计数通常在该模型三轨中最大。finbert2 为项目自训练的私有二分类模型, 无中性类, 与 finbert_cn/fin_sent_zh 两个三分类 HF 公开模型的判别结构不同 (三者的判别空间与训练语料均不可比), 三模型 full 轨计数并排即跨模型稳健性梯子的基准轨对照, 各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。⚠ 承重: 本机器/环境若未设置有效 `FINBERT2_MODEL_DIR`, finbert2 整体优雅跳过 (strict_models 严格模式仅约束两个 HF 模型的非预期加载失败, FINBERT2_MODEL_DIR 未配是预期 graceful skip), 本列及 finbert2 家族全部九分之三列呈缺失、encode 后按计数列零填契约填 0, 不触发其余模型的连坐降级。下游以同域分母 (finbert2 full 轨实质验证正面篇数) 相除得该模型 full 轨洗稿率。本列与 F118 集成口径 (三模型 argmax 多数票后再判正面) 相区分, 是三模型互证证据链中的独立一支。批级异常触发逐篇重试一次, 仍失败才写失败哨兵 (label=None、概率 NaN、num_windows=-1), 与空文本 (num_windows=0) 严格区分, 两者均不计入本列分子, 该套失败/空文本区分口径三模型三轨统一遵循, 保证 pos_symb 计数不因推理管道异常而被系统性污染。

## VAR: finbert2_pos_symb_count_ss

【变体差分】
本列取 finbert2 在 ss 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨文本 content_ss 收窄到银行∧金融科技同句共现片段及其 ±窗口, 是三轨中语境最严的一轨; 无同句共现时镜像 ctx 回退语义, 优雅退回全文正文并置 ss_is_fallback=True。finbert2 二分类的正面判定 _is_finbert2_positive_ss 在此最窄语料上取 argmax, 象征判定固定取 full 轨。与同族 full/ctx 列差异纯在正面判定文本轨: ss 语料最窄, 计数一般最小, 回退篇则等价 full 口径。finbert2 无中性选项的判别结构使其在极窄的 ss 语料 (可能仅一两句话) 上比三分类模型更易判出明确极性 (无中性缓冲), 这是 finbert2 相对另两模型的一处结构性差异, 在跨模型比较时应留意而非误读为"finbert2 更敏感"。⚠ 承重: FINBERT2_MODEL_DIR 未配置时本列缺失、后续零填, 不连坐其余模型。本列落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨; 与 finbert_cn/fin_sent_zh 的同轨 ss 列并排为跨模型稳健性, 三轨与三模型两维度均各自 just-identified 并排、互为稳健性不分主次, 严禁混同一 over-identified Hansen J。下游以同域分母 (finbert2 ss 轨实质验证正面篇数) 相除得该模型 ss 轨洗稿率; 与 full/ctx 两轨并列构成 finbert2 一支内部完整的语境敏感性证据链, 三条轨结论若一致即证明该模型认定的象征化叙事规模不由语境窗口的选择驱动。

## VAR: finbert_cn_pos_symb_count_ctx

【变体差分】
本列取 finbert_cn (yiyanghkust/finbert-tone-chinese, HF, 三分类 中性/正面/负面) 在 ctx 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ctx 轨文本 content_ctx 聚焦目标银行实体邻近窗口, 正面判定 _is_finbert_cn_positive_ctx 在窄语境上取 argmax, 象征判定固定取 full 轨, 不随本列所在轨切换。finbert_cn 是三个 BERT 模型中专为中文金融文本训练的公开模型 (对标 Huang et al. 2023 FinBERT 的方法学路线, 但训练语料与词表为中文金融领域), 相较基于英文 Financial PhraseBank 迁移微调的 fin_sent_zh, finbert_cn 在中文金融语境的正面判别边界理论上更贴合本仓语料。与同族 finbert_cn_pos_symb_count_full 的差异纯在正面判定文本轨 (ctx 语料更窄, 计数一般不超过 full); 与 fin_sent_zh/finbert2 的同轨 ctx 列并排构成跨模型稳健性, 三模型各自 just-identified、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列落在 full-only 留篇宇宙内, ctx 为 conditional-on-full 子集轨, finbert_cn 该篇 ctx 轨推理失败或平局时不入分子, 不借他轨或他模型分值填补。finbert_cn (yiyanghkust/finbert-tone-chinese) 与 fin_sent_zh 同属 strict_models 严格加载约束下的 HF 公开模型, 非预期加载失败会 fail-loud raise 而非静默跳过, 与 finbert2 因本地私有路径未配的预期 graceful skip 形成鲜明对照; 这一降级语义差异对理解三模型九列的缺失模式 (哪几列可能整族为零、哪几列几乎不会整族缺失) 十分关键, 生产环境校验时应优先检查 finbert2 三列而非本列。

## VAR: finbert_cn_pos_symb_count_full

【变体差分】
本列取 finbert_cn 在 full 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数, 是 finbert_cn 一支的基准轨, 也是本家族中三模型 strict_models 严格加载约束下最稳的一支 (finbert_cn 与 fin_sent_zh 两个 HF 模型在非预期加载失败时 fail-loud raise, 不会静默跳过; 仅 finbert2 因本地私有模型路径未配是预期 graceful skip)。full 轨文本与留篇门控同轨 (full-only, 2026-06-29), 本列行宇宙即该银行—年度的 full 留篇集本身。正面判定与象征判定两半同取 full 轨, 语义最自洽, 计数通常在该模型三轨中最大。与 fin_sent_zh_pos_symb_count_full、finbert2_pos_symb_count_full 并排即跨模型 per-model 稳健性梯子的基准轨对照, 三模型各自 just-identified、互为稳健性不分主次, 严禁混进同一 over-identified Hansen J。finbert_cn 专为中文金融文本训练, 其三分类边界 (中性/正面/负面) 与本仓其余两模型不完全可比 (fin_sent_zh 亦三分类但训练语料为英文迁移微调, finbert2 为二分类), 三者绝对水平不宜直接比较, 只作跨模型稳健性证据并排。下游以同域分母 (finbert_cn full 轨实质验证正面篇数) 相除得该模型 full 轨洗稿率, 与 F118 三模型集成口径互为独立稳健性一支。finbert_cn 是三个 BERT 模型中唯一直接以"tone"(语调) 为微调目标命名的公开模型, 训练语料聚焦中文金融新闻, 理论上对本仓银行金融科技报道的正面语气识别最贴题, 这也是它常被选作三模型对照中的"锚点"参照, 但本仓设计上并不赋予其高于另两模型的权重, 三者严格 co-equal 并排。

## VAR: finbert_cn_pos_symb_count_ss

【变体差分】
本列取 finbert_cn 在 ss 轨的 argmax 正面判定与 full 轨的象征判定相乘后的 bank-year 计数。ss 轨文本收窄到银行∧金融科技同句共现片段及 ±窗口, 是三轨中语境最严的一轨; 无同句共现时镜像 ctx 回退语义, 退回全文正文并置 ss_is_fallback=True。正面判定 _is_finbert_cn_positive_ss 在此最窄语料上取 argmax, 象征判定仍固定取 full 轨。与同族 full/ctx 列差异纯在正面判定文本轨: ss 语料最窄, 计数一般最小, 回退篇等价 full 口径, 故 ss 计数不必严格小于 ctx。ss 轨的构造意图是把语境收到银行与金融科技真正同句共现的最严口径, 检验 finbert_cn 一支的象征化篇数是否对语境窗口选择稳健, 若三轨与三模型结论一致则不由某一特定模型或语境切法驱动。⚠ 三轨与三模型两维度均各自 just-identified 并排、互为稳健性不分主次, 严禁把不同轨或不同模型的计数混进同一 over-identified Hansen J; 象征这一半固定取 full 分类保证三轨判据一致, 只让正面判定这一半随轨变化, 使三轨差异可干净归因于正面判定的语境宽窄。本列落在 full-only 留篇宇宙内, 为 conditional-on-full 子集轨。下游以同域分母 (finbert_cn ss 轨实质验证正面篇数) 相除得该模型 ss 轨洗稿率, 与本家族其余八列共同构成 3 模型 × 3 轨的完整正交梯子, 任一单元缺失 (如 finbert2 整体跳过) 均不影响其余单元的可用性与解释力。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
<!-- rendered-citations:end -->
