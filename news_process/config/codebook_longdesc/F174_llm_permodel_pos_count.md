---
family_id: F174
columns:
- deepseekv4_pos_count_ctx
- deepseekv4_pos_count_full
- deepseekv4_pos_count_ss
- gemini31_pos_count_ctx
- gemini31_pos_count_full
- gemini31_pos_count_ss
- gpt54nano_pos_count_ctx
- gpt54nano_pos_count_full
- gpt54nano_pos_count_ss
unit: 篇数 (count, 非负整数)
formula: "{llm}_pos_count{track} = Σ_i 1[ {llm}_score{track}_i > 0 ]; 逐 bank-year 对文章级单模型正面判定加总, 分模型 llm∈{deepseekv4,gemini31,gpt54nano}, 分轨 track∈{_full,_ctx,_ss}"
producer: news_process/pipeline/panel/encode.py (聚合, 方法 A2); news_process/pipeline/panel/runner.py (文章级 _is_{llm}_positive 构造); news_process/pipeline/sentiment/tone_llms.py (stage 21 单模型逐条 LLM 判定)
upstream:
- 21_tone_llms.parquet ({llm}_score{track} 单模型有符号语调)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: "10.1017/psrm.2024.64"
  type: "journal"
  authors: "Ornstein, J. T., Blasingame, E. N., & Truscott, J. S."
  year: 2025
  title: "How to train your stochastic parrot: large language models for political texts"
  venue: "Political Science Research and Methods"
  vol: "13"
  issue: "2"
  pages_or_artno: "264-281"
- doi: "10.18653/v1/2024.law-1.13"
  type: "journal"
  authors: "Rønningstad, E., Velldal, E., & Øvrelid, L."
  year: 2024
  title: "A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation"
  venue: "Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII)"
  pages_or_artno: "133-139"
- doi: "10.48550/arxiv.2406.04692"
  type: "arxiv"
  authors: "Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J."
  year: 2024
  title: "Mixture-of-Agents Enhances Large Language Model Capabilities"
  venue: "arXiv"
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是每一家 LLM 标注器在给定文本轨道下, 逐 bank-year 判为「正面」的银行金科报道篇数。它不是共识测度, 而是把三家大模型情感投票机制拆解到单模型层面后, 每个模型各自留下的正面计数足迹。生产链路始于 stage 21 (tone_llms.py): 每条经留篇门控保留的银行金科报道, 由 gpt-5.4-nano、gemini-3.1-flash-lite、deepseek-v4-flash 三家模型分别以思维链单次请求同时给出真伪判定与情感极性, 得到文章级单模型有符号语调 {llm}_score{track} (取值 -1/0/+1, 经该模型自身 verified 门控置 NA)。在 panel 聚合前, runner.py 把每个模型的有符号分数二值化为 _is_{llm}_positive{track} = 1[{llm}_score{track} > 0] (缺席即模型未返回时 fillna 0 视为非正面), 再由 encode.py 的洗稿率聚合块 (方法 A2「单个 LLM」) 对每个 bank-year 分格加总, 落地为 {llm}_pos_count{track}。因此该列是一个非负整数计数, 分子域 = 该模型对该 bank-year 报道集判正的篇数, 与之配对的 {llm}_neg_count{track} (负面计数) 分离编码, 刻意不做极性对冲, 以便下游构造模型内与模型间的情感离散度。

【方法学与计算】
计数口径承接单模型有符号语调, 而非各家均值或多数投票共识: 共识轨 llm_vote_tone (三家多数票) 已单列, 本族是拆到厂商粒度的稳健性投影。分母语义须与留篇门控对齐——留篇判定为 full-only (2026-06-29 口径): 是否算作一篇「银行金科报道」只看 llm_verified_full 是否为真, ctx 与 ss 轨降为 conditional-on-full 的条件测度轨, 其行宇宙是 full 留篇集的子集, 但每条轨道的正面计数仍按该轨各自的文本输入与该模型该轨的 verified 状态独立计算。三家模型互为稳健性、不分主次: 每家各自 just-identified 并排进入稳健性网格, 严禁把三家的 pos_count 混进同一 over-identified Hansen J 过度识别检验——这是与三轨、co-primary 双轨嵌入、词典消融梯度、政治词权重梯度一致的铁律。per-model 独立降级: 某家模型整体缺席只会掏空该模型自身的计数族, 而不像 co-primary 嵌入那样 both-or-neither 连坐同置 NaN。三轨同样各自 just-identified 并排, ss 轨回退语义镜像 ctx: 当某报道无银行与金科词同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母。

【文献定位】
把 LLM 用作可复现的文本标注器而非黑箱, 是近年会计金融计量的方法学主线。de Kok (2025) 系统论证了在会计研究中使用生成式大模型做文本分析时, 必须冻结 prompt、把温度设为 0 并缓存返回, 才能获得跨运行可复现的标注——本项目 stage 21 正是以 temperature=0、prompt v8 字节冻结、缓存命中键锁定的方式落地这一规范, 使单模型正面计数成为确定性锚点。Gilardi et al. (2023) 以实证证明 ChatGPT 在文本标注任务上超越众包工人, 为把单一 LLM 判定作为独立效度轨提供了外部依据; 但正因单模型判定存在厂商特异的系统偏差, 本项目坚持保留三家分厂商计数并排而非只取共识。Loughran & McDonald (2016) 对会计金融文本分析的综述奠定了以词频/极性计数刻画语调的传统, 单模型正面计数即这一传统在 LLM 时代的延伸——把「正面词篇」替换为「模型判正篇」。Huang et al. (2023) 的 FinBERT 代表判别式金融文本模型路线, 与本族的生成式 LLM 路线互为方法三角。Lan et al. (2025) 针对中文细粒度金融情感的大模型应用, 与本项目中文银行金科语料的判定场景直接同域, 支撑单模型中文正面判定的构念效度。 在社会科学测量的同族脉络上, Ornstein、Blasingame 与 Truscott (2025) 以 few-shot prompt 在情感分析、文档标度与主题建模等政治学「文本即数据」任务上做预注册评估, 结论是该做法优于传统有监督学习基线, 并以极低成本达到与专家及众包编码员相当 (comparable, 而非超过) 的水平, 同时给出社科测量任务的 prompt 适配最佳实践与开源软件包; 这正是本族「由 LLM 直接产出文本级标签、再逐单元二值化加总」这一链路的方法学先例。惟其语料为英文政治文本 (立法、演讲等), 采用单一模型而非三家投票, 未构造置信度, 亦无 bank-year 面板聚合、留篇门控与三轨切分, 迁移至中文银行金科语料时上述差异须如实计入; 该文亦不构成对本项目任何置信度列的依据。构念侧, Rønningstad 与 Velldal (2024) 评估 LLM 对「针对特定目标实体」的情感 (entity-level / targeted sentiment) 的标注质量并与人工标注对照, 与本族情感构念恰为同构 — 本项目判定的是「针对目标银行」的实体级语调而非篇章整体语调, 该文因而是这一构念下 LLM 标注可行性的直接同族实证; 但其语料为挪威语与英语的通用新闻及评论、目标实体非银行, 采用单一 GPT 模型且无三家投票与置信度概率化, 只报告标注一致性, 不做面板聚合与三轨切分。至于为何保留三家厂商计数并排而非只留共识轨, Wang、Wang、Athiwaratkun、Zhang 与 Zou (2024) 实证聚合多个异构 LLM 的输出优于任何单一模型并刻画了模型间协作性, 为本项目采用三家异构厂商模型的架构提供了前沿存在性依据; 但其聚合是分层生成式的 (后层模型读取前层模型的完整回答再合成), 与本项目对离散标签取多数票、对连续分取算术均值的机械聚合是不同机制, 评测亦在英文指令跟随基准而非中文银行金科新闻, 且未讨论 per-model 独立降级与缺列 NaN 语义, 故该文仅支撑「异构多模型并用有价值」这一取向, 不构成对本族 per-model 计数口径的直接背书 — 三家仍各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。
## VAR: deepseekv4_pos_count_ctx

【变体差分】
本列固定模型 = deepseek-v4-flash (供应商 DeepSeek, 直连 api.deepseek.com, 与走 OpenLux 路由的 gpt/gemini 两家不同源; 短名 deepseekv4 以 config/sentiment.yaml 为单一事实源), 固定轨道 = ctx。ctx 轨输入 = content_ctx = 标题 prepend + 含目标银行句 ±窗口的上下文片段 (Hassan et al. 2019 的实体邻近口径), 相对 full 轨剔除了与目标银行无关的远端段落, 使模型的正面判定聚焦于银行相关语境。计数值 = 该 bank-year 中 deepseek 模型在 ctx 文本上判为正面 (deepseekv4_score_ctx > 0) 的篇数。它与同族 deepseekv4_pos_count_full、deepseekv4_pos_count_ss 三轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。ctx 是 conditional-on-full 条件轨: 行宇宙为 full 留篇集子集, 但正面篇数按 ctx 文本与该模型 ctx 轨 verified 状态独立计算, 不借 full 分子。在早期试跑 T=2 极小样本上 ctx 计数可能高度退化甚至零方差, 属预期, 生产 T=19 恢复正常判别力。二值化口径须留意: _is_deepseekv4_positive_ctx = (deepseekv4_score_ctx.fillna(0) > 0), 即该模型 verified=False 或整体缺席时分数为 NA、被填 0 视作非正面, 故本计数只累计该模型在 ctx 轨明确判正且通过其自身 verified 门控的篇数, 是一个保守下界。它是原始篇数计数而非占比 (不除 n_articles 分母), 相对 pos_frac 类占比列保留了稀疏格与高覆盖格的规模信息, 便于加权聚合与厂商间水平对照; 但正因未标准化, 跨模型比较其原始计数水平无意义, 进入 Table A5 类跨模型对照须先按 z-score 标准化后比标准化系数。模型间一致性由 Krippendorff α 与 Cohen κ 刻画 (tone_validation 复用), 真 FWER 校正在根级 27_tableA12 跨模型模板统一处理, 本列不单独做过度识别检验。gate = tests/test_llm_model_robustness.py。

## VAR: deepseekv4_pos_count_full

【变体差分】
本列固定模型 = deepseek-v4-flash (DeepSeek 直连 api.deepseek.com), 固定轨道 = full。full 轨输入 = content_full = 标题 prepend + 全文正文, 是留篇门控的判定轨 (full-only 口径: 一篇报道是否入样只看 llm_verified_full)。计数值 = 该 bank-year 中 deepseek 模型在全文上判正 (deepseekv4_score_full > 0) 的篇数, 是本模型三轨里信息量最全、也是留篇分母所锚定的主轨。相对 ctx/ss 的窄窗输入, full 轨纳入远端段落, 正面判定可能被非银行语境的正面表述抬高, 因此三轨并排恰好构成「文本范围」维度的稳健性梯子。它与 gpt54nano_pos_count_full、gemini31_pos_count_full 三家同轨并排, 构成 per-model 跨厂商稳健性: 三家各自 just-identified、不分主次、禁混同一 over-identified Hansen J。deepseek 家若整体缺席仅掏空自身计数族 (per-model 独立降级), 不连坐另两家。与 deepseekv4_neg_count_full 分离编码, 刻意不对冲极性, 供下游模型内离散度与跨模型分歧构造使用。文章级来源 deepseekv4_score_full 由 stage 21 单次思维链请求同时产出真伪与情感, 温度锁 0、prompt v8 字节冻结、缓存命中键固定, 使本计数在缓存全命中时可离线零字节复现, 是 golden 确定性锚点之一 (de Kok 2025 所倡的 prompt 冻结加温度 0 加缓存范式)。二值化保守口径同族一致: 分数 NA (verified=False 或模型缺席) 填 0 视作非正面, 故 full 轨正面计数是该模型明确判正且通过 full 轨 verified 门控的篇数下界。作为原始篇数而非占比, 本列保留规模信息但跨模型水平不可直接比较, 须 z-score 标准化后进跨模型对照; 模型间一致性由 Krippendorff α 与 Cohen κ 度量, 真 FWER 归根级 27_tableA12 模板。gate = tests/test_llm_model_robustness.py。

## VAR: deepseekv4_pos_count_ss

【变体差分】
本列固定模型 = deepseek-v4-flash, 固定轨道 = ss (银行金科同句共现轨)。ss 轨输入 = content_ss = 标题 prepend + 同句内同时含目标银行∧金科词的句 ±窗口片段, 是三轨里语境最严的一轨, 只保留银行与金融科技直接共现的表述。计数值 = 该 bank-year 中 deepseek 模型在 ss 文本上判正 (deepseekv4_score_ss > 0) 的篇数。ss 回退语义镜像 ctx: 当某报道无银行金科同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 故 ss 计数在无共现语料上会退化为 full 语境下的判定。它与本模型 full/ctx 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J; ss 亦为 conditional-on-full 条件轨。早期试跑 T=2 上 ss 因共现稀疏可能大面积回退或零方差, 属预期退化; 生产 T=19 上 ss 提供最聚焦银行金科关系的正面判定信号, 与另两轨的差异恰是共现严格度对情感测量的敏感性证据。二值化保守口径同族: deepseekv4_score_ss 为 NA (verified=False 或模型缺席) 时填 0 视作非正面, 故本计数只累计该模型在 ss 文本明确判正的篇数。须强调 ss 与三轨文本后缀是同一维度而与网络判据后缀 (_win1/_sent) 分属不同空间, 不可混淆。作为原始篇数计数, 本列不除分母, 跨模型比较其水平无意义, 须 z-score 标准化后进 Table A5 类跨模型对照; 模型间一致性由 Krippendorff α (容 2-vs-3 分类、缺标感知) 与 Cohen κ (须先重映射非负码) 度量, 真 FWER 归根级 27_tableA12 跨模型模板。三家 per-model 计数与三轨计数各自 just-identified 并排, 是与 co-primary 双轨嵌入、词典消融、政治词权重梯度同构的稳健性纪律。gate = tests/test_llm_model_robustness.py。

## VAR: gemini31_pos_count_ctx

【变体差分】
本列固定模型 = gemini-3.1-flash-lite (Google 模型, 经 OpenLux 路由), 固定轨道 = ctx。ctx 轨输入 = 标题 prepend + 目标银行句 ±窗口上下文片段。计数值 = 该 bank-year 中 gemini 模型在 ctx 文本上判正 (gemini31_score_ctx > 0) 的篇数。换厂商而不换轨道: 本列与 deepseekv4_pos_count_ctx、gpt54nano_pos_count_ctx 同为 ctx 轨的三家并排, 用于识别正面判定中的厂商特异偏差——若三家在同一 ctx 文本上的正面计数系统性发散, 提示单模型判定不可作为唯一测量。三家各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。它与本模型 full/ss 两轨又构成文本范围稳健性梯子, 同样各轨 just-identified 并排。ctx 为 conditional-on-full 条件轨, 行宇宙是 full 留篇集子集, 正面篇数按 ctx 文本与 gemini 该轨 verified 状态独立计算。gemini 家整体缺席仅掏空自身计数族 (per-model 独立降级), 不连坐 deepseek/gpt 两家。早期试跑 T=2 上可能零方差退化, 属预期。二值化保守口径: _is_gemini31_positive_ctx = (gemini31_score_ctx.fillna(0) > 0), 分数 NA (verified=False 或缺席) 填 0 视作非正面, 故只累计 gemini 在 ctx 轨明确判正且过其自身 verified 门控的篇数。gemini 经 OpenLux 与 gpt 同源路由但为不同厂商模型, 三家投票机制的价值恰在于跨厂商三角验证: 若 gemini 的 ctx 正面计数与另两家系统性发散, 提示单一 LLM 判定存在厂商特异偏差, 不可作唯一测量 (Gilardi et al. 2023 虽证单模型可超众包, 本项目仍坚持三家并排)。作为原始篇数计数, 跨模型水平不可直接比较, 须 z-score 标准化后进跨模型对照; 一致性由 Krippendorff α 与 Cohen κ 度量, 真 FWER 归 27_tableA12。gate = tests/test_llm_model_robustness.py。

## VAR: gemini31_pos_count_full

【变体差分】
本列固定模型 = gemini-3.1-flash-lite (Google, OpenLux 路由), 固定轨道 = full。full 轨输入 = 标题 prepend + 全文正文, 系留篇门控判定轨。计数值 = 该 bank-year 中 gemini 模型在全文上判正 (gemini31_score_full > 0) 的篇数。作为 gemini 三轨里信息量最全的一轨, 它锚定 full-only 留篇分母。与 deepseekv4_pos_count_full、gpt54nano_pos_count_full 三家同轨并排, 是跨厂商 per-model 稳健性的核心对照: gemini 与另两家在同一全文语料上的正面判定差异, 直接刻画大模型情感标注的厂商依赖度。三家各自 just-identified、不分主次、禁混同一 over-identified Hansen J。它与本模型 ctx/ss 两轨构成文本范围梯子, 各轨 just-identified 并排。gemini 家整体缺席时按 per-model 独立降级仅掏空自身族, 不像 co-primary 嵌入 both-or-neither 连坐。与 gemini31_neg_count_full 分离编码, 不对冲极性, 供下游跨模型分歧与模型内离散度构造使用。文章级来源 gemini31_score_full 由 stage 21 单次思维链请求与真伪判定一体产出, 温度锁 0、prompt v8 字节冻结、缓存键固定, 缓存全命中时可离线零字节复现。二值化保守口径同族: 分数 NA (verified=False 或缺席) 填 0 视作非正面, 故 full 轨正面计数是 gemini 明确判正且过 full 轨 verified 门控的篇数下界。作为原始篇数而非占比, 本列保留规模信息但跨模型水平不可直接比较, 进入 Table A5 类跨模型对照须先 z-score 标准化后比标准化系数 (2 分类与 3 分类原始方差不同); 模型间一致性由 Krippendorff α 与 Cohen κ 度量, 真 FWER 归根级 27_tableA12 跨模型模板。三家 per-model、三轨各自 just-identified 并排。gate = tests/test_llm_model_robustness.py。

## VAR: gemini31_pos_count_ss

【变体差分】
本列固定模型 = gemini-3.1-flash-lite (Google, OpenLux 路由), 固定轨道 = ss (银行金科同句共现轨)。ss 轨输入 = 标题 prepend + 银行∧金科同句 ±窗口片段, 语境最严。计数值 = 该 bank-year 中 gemini 模型在 ss 文本上判正 (gemini31_score_ss > 0) 的篇数。ss 回退语义镜像 ctx: 无同句共现时 content_ss 回退全文正文、置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母。本列与 deepseekv4_pos_count_ss、gpt54nano_pos_count_ss 三家同为 ss 轨并排, 检验最严语境下的厂商特异正面判定偏差; 又与本模型 full/ctx 两轨构成文本范围梯子。三家、三轨均各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 条件轨。gemini 家整体缺席仅掏空自身计数族 (per-model 独立降级)。早期试跑 T=2 上 ss 因共现稀疏大面积回退或零方差, 属预期退化; 生产 T=19 上提供聚焦银行金科关系的 gemini 正面判定信号。二值化保守口径: gemini31_score_ss 为 NA (verified=False 或缺席) 时填 0 视作非正面, 只累计 gemini 在 ss 文本明确判正的篇数。ss 文本后缀属三轨文本维度, 与网络构造判据后缀 (_win1/_sent) 分属不同命名空间, 不可混淆。作为原始篇数计数, 本列不除分母, 跨模型比较其水平无意义, 须 z-score 标准化后进跨模型对照; 模型间一致性由 Krippendorff α (容 2-vs-3 分类、缺标感知) 与 Cohen κ (须先重映射非负码) 度量, 真 FWER 归根级 27_tableA12。三家 per-model 计数与三轨计数各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。gate = tests/test_llm_model_robustness.py。

## VAR: gpt54nano_pos_count_ctx

【变体差分】
本列固定模型 = gpt-5.4-nano (OpenAI 系, 经 OpenLux 路由), 固定轨道 = ctx。ctx 轨输入 = 标题 prepend + 目标银行句 ±窗口上下文片段。计数值 = 该 bank-year 中 gpt 模型在 ctx 文本上判正 (gpt54nano_score_ctx > 0) 的篇数。与 deepseekv4_pos_count_ctx、gemini31_pos_count_ctx 三家同为 ctx 轨并排, 用于识别正面判定的厂商特异偏差; 又与本模型 full/ss 两轨构成文本范围稳健性梯子。三家、三轨均各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。ctx 为 conditional-on-full 条件轨: 行宇宙是 full 留篇集子集, 正面篇数按 ctx 文本与 gpt 该轨 verified 状态独立计算, 不借 full 分子。gpt 家整体缺席仅掏空自身计数族 (per-model 独立降级), 不连坐 deepseek/gemini 两家。早期试跑 T=2 极小样本上 ctx 计数可能高度退化甚至零方差, 属预期, 生产 T=19 恢复判别力。二值化保守口径: _is_gpt54nano_positive_ctx = (gpt54nano_score_ctx.fillna(0) > 0), 分数 NA (verified=False 或缺席) 填 0 视作非正面, 故只累计 gpt 在 ctx 轨明确判正且过其自身 verified 门控的篇数。gpt 经 OpenLux 与 gemini 同源路由但为不同厂商模型, 三家投票机制的价值在于跨厂商三角验证: 若 gpt 的 ctx 正面计数与另两家系统性发散, 提示厂商特异偏差, 三家并排恰能暴露这一偏差。作为原始篇数计数, 本列不除分母, 保留规模信息, 但跨模型水平不可直接比较, 须 z-score 标准化后进 Table A5 类跨模型对照; 模型间一致性由 Krippendorff α 与 Cohen κ 度量, 真 FWER 归根级 27_tableA12 模板。gate = tests/test_llm_model_robustness.py。

## VAR: gpt54nano_pos_count_full

【变体差分】
本列固定模型 = gpt-5.4-nano (OpenAI 系, OpenLux 路由), 固定轨道 = full。full 轨输入 = 标题 prepend + 全文正文, 系留篇门控判定轨 (full-only 口径)。计数值 = 该 bank-year 中 gpt 模型在全文上判正 (gpt54nano_score_full > 0) 的篇数, 是本模型三轨里信息量最全、锚定 full-only 留篇分母的主轨。与 deepseekv4_pos_count_full、gemini31_pos_count_full 三家同轨并排, 构成跨厂商 per-model 稳健性核心对照: 三家在同一全文语料上的正面判定差异刻画情感标注的厂商依赖度。三家各自 just-identified、不分主次、禁混同一 over-identified Hansen J。它与本模型 ctx/ss 两轨构成文本范围梯子, 各轨 just-identified 并排。gpt 家整体缺席按 per-model 独立降级仅掏空自身族, 不 both-or-neither 连坐。与 gpt54nano_neg_count_full 分离编码, 刻意不对冲极性, 供下游模型内离散度与跨模型分歧构造使用。文章级来源 gpt54nano_score_full 由 stage 21 单次思维链请求与真伪判定一体产出, 温度锁 0、prompt v8 字节冻结、缓存键固定, 缓存全命中时可离线零字节复现, 是 golden 确定性锚点之一。二值化保守口径同族: 分数 NA (verified=False 或缺席) 填 0 视作非正面, 故 full 轨正面计数是 gpt 明确判正且过 full 轨 verified 门控的篇数下界。作为原始篇数而非占比, 本列保留规模信息但跨模型水平不可直接比较, 须先 z-score 标准化后比标准化系数; 模型间一致性由 Krippendorff α 与 Cohen κ 度量, 真 FWER 归根级 27_tableA12 跨模型模板。三家 per-model、三轨各自 just-identified 并排, 互为稳健性、不分主次。gate = tests/test_llm_model_robustness.py。

## VAR: gpt54nano_pos_count_ss

【变体差分】
本列固定模型 = gpt-5.4-nano (OpenAI 系, OpenLux 路由), 固定轨道 = ss (银行金科同句共现轨)。ss 轨输入 = 标题 prepend + 银行∧金科同句 ±窗口片段, 三轨里语境最严。计数值 = 该 bank-year 中 gpt 模型在 ss 文本上判正 (gpt54nano_score_ss > 0) 的篇数。ss 回退语义镜像 ctx: 无同句共现时 content_ss 回退全文正文、置 ss_is_fallback=True, 与 ctx 共享 n_articles 分母, 故无共现语料上 ss 计数退化为全文语境判定。与 deepseekv4_pos_count_ss、gemini31_pos_count_ss 三家同为 ss 轨并排, 检验最严语境下的厂商特异正面判定偏差; 又与本模型 full/ctx 两轨构成文本范围梯子。三家、三轨均各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; ss 为 conditional-on-full 条件轨。gpt 家整体缺席仅掏空自身计数族 (per-model 独立降级)。早期试跑 T=2 上 ss 因共现稀疏大面积回退或零方差, 属预期退化; 生产 T=19 上提供聚焦银行金科关系的 gpt 正面判定信号。二值化保守口径: gpt54nano_score_ss 为 NA (verified=False 或缺席) 时填 0 视作非正面, 只累计 gpt 在 ss 文本明确判正的篇数。ss 文本后缀属三轨文本维度, 与网络构造判据后缀 (_win1/_sent) 分属不同命名空间, 不可混淆。作为原始篇数计数, 本列不除分母, 跨模型比较其水平无意义, 须 z-score 标准化后进跨模型对照; 模型间一致性由 Krippendorff α (容 2-vs-3 分类、缺标感知) 与 Cohen κ (须先重映射非负码) 度量, 真 FWER 归根级 27_tableA12。三家 per-model 计数与三轨计数各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。gate = tests/test_llm_model_robustness.py。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Ornstein, J. T., Blasingame, E. N., & Truscott, J. S. (2025). How to train your stochastic parrot: large language models for political texts. Political Science Research and Methods, 13(2), 264-281. https://doi.org/10.1017/psrm.2024.64
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
Wang, J., Wang, J., Athiwaratkun, B., Zhang, C., & Zou, J. (2024). Mixture-of-Agents Enhances Large Language Model Capabilities. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2406.04692
<!-- rendered-citations:end -->
