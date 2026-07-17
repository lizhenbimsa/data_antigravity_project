---
family_id: F298
columns:
- fin_sent_zh_pos_app_ctx
- fin_sent_zh_pos_app_full
- fin_sent_zh_pos_app_ss
- fin_sent_zh_pos_ctx
- fin_sent_zh_pos_full
- fin_sent_zh_pos_hw_ctx
- fin_sent_zh_pos_hw_full
- fin_sent_zh_pos_hw_ss
- fin_sent_zh_pos_mw_ctx
- fin_sent_zh_pos_mw_full
- fin_sent_zh_pos_mw_ss
- fin_sent_zh_pos_ss
- fin_sent_zh_pos_std_ctx
- fin_sent_zh_pos_std_full
- fin_sent_zh_pos_std_ss
- fin_sent_zh_pos_tech_ctx
- fin_sent_zh_pos_tech_full
- fin_sent_zh_pos_tech_ss
- fin_sent_zh_pos_vw_ctx
- fin_sent_zh_pos_vw_full
- fin_sent_zh_pos_vw_ss
- finbert2_pos_app_ctx
- finbert2_pos_app_full
- finbert2_pos_app_ss
- finbert2_pos_ctx
- finbert2_pos_full
- finbert2_pos_hw_ctx
- finbert2_pos_hw_full
- finbert2_pos_hw_ss
- finbert2_pos_mw_ctx
- finbert2_pos_mw_full
- finbert2_pos_mw_ss
- finbert2_pos_ss
- finbert2_pos_std_ctx
- finbert2_pos_std_full
- finbert2_pos_std_ss
- finbert2_pos_tech_ctx
- finbert2_pos_tech_full
- finbert2_pos_tech_ss
- finbert2_pos_vw_ctx
- finbert2_pos_vw_full
- finbert2_pos_vw_ss
- finbert_cn_pos_app_ctx
- finbert_cn_pos_app_full
- finbert_cn_pos_app_ss
- finbert_cn_pos_ctx
- finbert_cn_pos_full
- finbert_cn_pos_hw_ctx
- finbert_cn_pos_hw_full
- finbert_cn_pos_hw_ss
- finbert_cn_pos_mw_ctx
- finbert_cn_pos_mw_full
- finbert_cn_pos_mw_ss
- finbert_cn_pos_ss
- finbert_cn_pos_std_ctx
- finbert_cn_pos_std_full
- finbert_cn_pos_std_ss
- finbert_cn_pos_tech_ctx
- finbert_cn_pos_tech_full
- finbert_cn_pos_tech_ss
- finbert_cn_pos_vw_ctx
- finbert_cn_pos_vw_full
- finbert_cn_pos_vw_ss
unit: 无量纲得分/指标 (BERT softmax 输出的正面类概率属于[0,1] 之 bank-year 聚合值, 部分后缀为组内标准差/加权均值, 单位仍为概率量纲)
formula: 单模型 (finbert_cn/fin_sent_zh/finbert2) 文章级正面类 softmax 概率, 按三轨 (full/ctx/ss) × 7 类聚合口径 (等权/locus 子样本 app·tech/herd-decay 加权 hw/媒体权威加权 mw/组内标准差 std/密度值权加权 vw) 汇总到 bank-year
producer: pipeline/sentiment/tone_berts.py ; pipeline/panel/encode.py
upstream:
- 22_words_tone.parquet
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
- doi: "10.1093/rfs/hhad044"
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A."
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: "The Review of Financial Studies"
  vol: "36"
  issue: "12"
  pages_or_artno: "4919-4964"
- doi: "10.1007/978-3-030-32381-3_16"
  type: wp
  authors: "Sun, C., Qiu, X., Xu, Y., & Huang, X."
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science"
  vol: "11856"
  pages_or_artno: "194-206"
- doi: "10.1080/07421222.2018.1440766"
  type: journal
  authors: "Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W."
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: "Journal of Management Information Systems"
  vol: "35"
  issue: "1"
  pages_or_artno: "220-265"
- doi: "10.1111/1475-679X.12123"
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: "Journal of Accounting Research"
  vol: "54"
  issue: "4"
  pages_or_artno: "1187-1230"
- doi: "10.1093/qje/qjz021"
  type: journal
  authors: "Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A."
  year: 2019
  title: "Firm-Level Political Risk: Measurement and Effects"
  venue: "Quarterly Journal of Economics"
  vol: "134"
  issue: "4"
  pages_or_artno: "2135-2202"
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
- doi: "10.3390/bdcc9100263"
  type: journal
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  venue: "Big Data and Cognitive Computing"
new_dois:
  - "10.1002/isaf.1549"
  - "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
F298 家族收纳三家独立 BERT 情感分类器 (finbert_cn=yiyanghkust/finbert-tone-chinese 公开预训练三分类; fin_sent_zh=bardsai/finance-sentiment-zh-base 基于 Financial PhraseBank 微调三分类; finbert2=项目自研两分类私有微调, 经 .env FINBERT2_MODEL_DIR 解析, 未配置时优雅跳过) 各自输出的正面类 softmax 概率, 在 bank-year 层面按三轨文本 (full/ctx/ss) 与七类聚合口径 (等权基线、locus 分类子样本 app/tech、herd-decay 加权 hw、媒体权威加权 mw、组内标准差 std、密度值权加权 vw) 展开的全部列。三家 BERT 模型与三家大语言模型 (gpt54nano/gemini31/deepseekv4)、六部情感词典并列为项目情感三条独立测度路线之一: LLM 依赖提示词理解上下文, 词典依赖关键词硬匹配加语言学规则, BERT 依赖在金融语料上微调过的神经网络对整段文本做语义分类, 三者互不依赖、互为交叉验证, 结论若能被三条路线同时支持则更稳健、更能承受顶刊审稿人对单一测度工具的质疑。stage 23 (tone_berts.py) 是三条路线里唯一使用本地推理 (GPU + torch/transformers) 而非外部 API 的一支, 因此不产生按次计费成本, 也不受 LLM 离线缓存守卫约束, 但需要本地部署模型权重 (两个 HuggingFace 模型可离线缓存, FinBERT2 需私有权重文件)。三模型互为稳健性、不分主次 (2026-07-02 铁律): 任一模型缺席仅影响其自身列族 (per-model 独立降级), 不触发 both-or-neither 联动, 这一点与 co-primary 嵌入双轨 (缺一即全族置 NaN) 的降级语义刻意不同。

【方法学与计算】
每篇文章文本先按 prepend_title 规则拼接标题与对应轨正文 (full=标题+全文, ctx=标题+银行实体窗口正文 content_ctx, ss=标题+银行和金科同句前后各1句窗正文 content_ss; ss 若无同句共现回退为全文 body 且置 ss_is_fallback=True, 镜像 ctx 轨回退语义), 超长文本按 WINDOW_STRIDE_RATIO=0.5 (50% 重叠) 切成多个不超过 512 token (含特殊 token, 有效正文不超过510 token) 的滑动窗口, 各窗口分别推理后按置信度加权池化 (logits 乘以归一化置信度权重求和) 合并为整篇文本的分类概率, 三个模型各自使用自身 tokenizer 独立分词 (词表不同的模型不共享分词结果, 防止跨词表 token id 错配)。批级推理异常时逐篇重试一次, 仍失败才写失败哨兵 (label=None、概率列 NaN、bert_num_windows_{track}=-1), 与空文本 (num_windows=0) 严格区分, 二者均不参与本家族任何列的 bank-year 聚合分母。基线聚合 (无后缀) 在 encode.aggregate_panel 中对该 track 下留篇文章的正面概率列做 groupby(target_bank, year).mean(); std 后缀改用 .std() (ddof=1, 组内 n<2 时为 NaN); app/tech 后缀先按 innovation_locus_full (三家 LLM 多数投票产出的 locus 分类, Gomber et al. 2018 概念化的应用场景/底层技术二分) 切出子样本 df_cat, 再在该子集上对该 track 的正面概率取组内均值, 需特别注意子样本切分依据固定用 full 轨分类标签, 即便被聚合的是 ctx 或 ss 轨情感概率, 这是 M1 阶段遗留设计, 尚待后续 M2 展开为逐轨对角分类; hw/mw/vw 三支加权后缀分别以 herd_weight (跟风衰减权重, 源自 stage 24 herd_decay_processor 的三轨独立衰减权重设计)、media_authority_weight (媒体权威度打分表)、提及密度权重 w (Hassan, Hollander, van Lent & Tahoun 2019, Quarterly Journal of Economics 提出的企业层面文本提及密度加权范式, 该文原用于政治风险测度, 本项目借鉴其加权思路应用于本家族情感测度) 为权重, 面板层先算概率乘以权重的加和与权重本身的加和两个求和列, 再相除得到最终列, 权重和为 0 时结果置 NaN。

【文献定位】
本家族方法学直接对应 Huang, Wang & Yang (2023, Contemporary Accounting Research) 提出的金融领域微调 BERT 文本信息抽取范式, 该文证明在金融语料上微调过的 BERT 相比通用情感词典与通用预训练模型更能捕捉金融文本的专业语境语义, 是三家 BERT 模型均选用金融领域微调/预训练权重而非通用情感模型的方法学依据。子样本切分所依赖的 locus 分类维度概念化自 Gomber, Kauffman, Parker & Weber (2018, Journal of Management Information Systems) 对金融科技创新的应用场景/基础设施层次划分, 本项目将其转化为 LLM 分类任务再据以切分 BERT 情感子样本, 使得 app/tech 两类后缀能够回答与整体正面语调不同的问题, 即银行在金融科技应用落地报道中的媒体形象是否系统性异于在底层技术布局报道中的形象。微调策略 (分层学习率、滑动窗口长度、序列截断) 参照 Sun, Qiu, Xu & Huang (2019) 关于中文 BERT 文本分类微调的系统性实践建议 (发表于 CCL 2019, Springer LNCS)。作为顶刊方法学锚点, Hassan, Hollander, van Lent, Schwedeler & Tahoun (2023, The Review of Financial Studies) 展示了同一套文本语料到神经网络语义打分到企业-年面板的一般化测度构造范式 (该文测度企业层面对流行病的暴露强度), 本家族的 BERT 正面概率 bank-year 聚合结构与其高度同构, 均是把篇章级模型输出通过等权/加权求和折叠为面板单元层面的连续变量。Loughran & McDonald (2016, Journal of Accounting Research) 的文本分析综述则系统比较了词典法与机器学习法在会计金融文本分析中的适用边界, 为本项目采用词典/LLM/BERT 三线并行而非依赖单一方法提供了方法学正当性依据。vw 后缀所用的提及密度加权思路参照 Hassan, Hollander, van Lent & Tahoun (2019, Quarterly Journal of Economics) 在构造企业层面政治风险暴露度时采用的按文本提及量赋权做法, 该文原始构念是政治风险而非情感, 本家族仅借鉴其"篇章提及密度即可作为该篇对企业相关性权重"的加权范式, 用以在 bank-year 聚合时让与目标银行提及更密集的文章对正面概率均值贡献更大权重, 与该文的政治风险测度构念本身不构成同一构念。Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献并指明未来研究方向, 其中对 BERT 等神经网络方法与传统词典法的对比脉络梳理, 为本家族三线并行 (词典/LLM/BERT) 的方法学选择提供了最新文献定位。Chuang, He & Hu (2025, Big Data and Cognitive Computing) 针对中文金融新闻构建情感分类与股价预测联合框架, 系统比较 BERT 等多种词嵌入及 LLM 微调模型在中文金融文本情感任务上的表现, 与本家族三家中文/金融 BERT 模型并行测度设计高度对应。

## VAR: fin_sent_zh_pos_app_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinSentZH_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_app_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinSentZH_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_app_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinSentZH_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 等权基线。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinSentZH_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 等权基线。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinSentZH_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_hw_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinSentZH_正面_hw_sum_ctx = 该模型正面概率与 herd_weight_ctx 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ctx 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_hw_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinSentZH_正面_hw_sum_full = 该模型正面概率与 herd_weight_full 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_full 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_hw_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinSentZH_正面_hw_sum_ss = 该模型正面概率与 herd_weight_ss 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ss 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_mw_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinSentZH_正面_mw_sum_ctx / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_mw_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinSentZH_正面_mw_sum_full / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_mw_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinSentZH_正面_mw_sum_ss / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 等权基线。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinSentZH_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_std_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_std_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_std_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_tech_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinSentZH_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_tech_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinSentZH_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_tech_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinSentZH_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_vw_ctx

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinSentZH_正面_w_sum_ctx / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_vw_full

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinSentZH_正面_w_sum_full / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: fin_sent_zh_pos_vw_ss

【变体差分】
本列是 FinSentZH 模型 (bardsai/finance-sentiment-zh-base（基于 Financial PhraseBank 微调的中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinSentZH_正面_w_sum_ss / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinBERT2, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_app_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT2_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_app_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT2_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_app_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT2_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 等权基线。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT2_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 等权基线。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT2_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_hw_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT2_正面_hw_sum_ctx = 该模型正面概率与 herd_weight_ctx 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ctx 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_hw_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT2_正面_hw_sum_full = 该模型正面概率与 herd_weight_full 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_full 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_hw_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT2_正面_hw_sum_ss = 该模型正面概率与 herd_weight_ss 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ss 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_mw_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT2_正面_mw_sum_ctx / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_mw_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT2_正面_mw_sum_full / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_mw_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT2_正面_mw_sum_ss / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 等权基线。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT2_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_std_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_std_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_std_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_tech_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT2_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_tech_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT2_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_tech_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT2_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_vw_ctx

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT2_正面_w_sum_ctx / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_vw_full

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在全文轨 (full)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT2_正面_w_sum_full / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert2_pos_vw_ss

【变体差分】
本列是 FinBERT2 模型 (项目自研两分类（负面/正面, 无中性档）私有微调 BERT, 模型权重路径经 .env 变量 FINBERT2_MODEL_DIR 解析; 未配置或路径不存在时 stage 23 优雅跳过该模型, 仅遗留 NaN, 不影响另两个 HuggingFace 模型照常产出) 在同句轨 (ss)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT2_正面_w_sum_ss / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT-CN) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_app_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_app_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_app_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 应用场景子样本 (locus=应用场景)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。由三家 LLM 多数投票产出的 innovation_locus 分类维度 (Gomber et al. 2018 locus-of-innovation 构念, 值域={底层技术, 应用场景}) 筛出的子样本均值 , 面板构建 (encode.aggregate_panel) 用 innovation_locus_full=='应用场景' 对文章级 DataFrame 做 df_cat 过滤 (M1 阶段设计: 子样本切分统一用 full 轨分类标签, 即便本列自身取的是 ctx/ss 轨情感概率, 分组依据仍是 full 轨的 LLM 共识分类, 不随本列轨道切换), 再在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 应用场景子样本 (locus=应用场景) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 等权基线。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT-CN_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 等权基线。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT-CN_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_hw_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT-CN_正面_hw_sum_ctx = 该模型正面概率与 herd_weight_ctx 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ctx 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_hw_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT-CN_正面_hw_sum_full = 该模型正面概率与 herd_weight_full 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_full 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_hw_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 跟风衰减加权 (herd-decay weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。分子分母均为该 track 下 herd_weight 的加权和结构: 面板层先聚合 FinBERT-CN_正面_hw_sum_ss = 该模型正面概率与 herd_weight_ss 逐篇相乘后求和, 再除以该 bank-year 的 sum_herd_weight_ss 得到最终 hw 列, herd_weight 依跟风/羊群衰减权重构造 (对与同期媒体论调高度雷同、疑似跟风转载的文章打折), 权重来自 stage 24 herd_decay_processor 三轨独立产出, 与 mw/vw 权重来源互不相关、并排为互为稳健性的加权臂. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 跟风衰减加权 (herd-decay weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_mw_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT-CN_正面_mw_sum_ctx / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_mw_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT-CN_正面_mw_sum_full / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_mw_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 媒体权威性加权 (media-authority weighted)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以 media_authority_weight (媒体权威度加权构造, 权重取自项目媒体来源库匹配的权威度打分表) 为权重的加权均值: FinBERT-CN_正面_mw_sum_ss / sum_media_authority_weight , 媒体权威权重取自项目媒体来源库匹配的权威度打分表 (media_weights.json), 未匹配到权威度的媒体落默认权重 (等权兜底); 与 hw/vw 加权臂并排, 各自 just-identified, 不进同一 over-identified 设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 媒体权威性加权 (media-authority weighted) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 等权基线。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。该模型该轨的 bank-year 等权算术平均 , groupby(target_bank, year) 对该 track 下留篇文章的 FinBERT-CN_正面 概率列取 mean, 未做任何再加权或子样本切分, 是本家族内该模型该轨的 canonical 起点, 其余 6 类后缀 (app/hw/mw/std/tech/vw) 均以其为参照系. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 等权基线本身 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_std_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_std_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_std_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 组内标准差 (dispersion, ddof=1)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。同一 bank-year、同一 track 下该模型正面概率的组内标准差 (pandas groupby .agg('std'), 默认 ddof=1), 是离散度/分歧度诊断量而非均值型语调测度 , 反映同一银行同一年内不同报道被该 BERT 模型判正的概率有多分散: 值越小说明该行当年媒体语调判断趋同, 值越大说明报道间语调分歧明显, 常与共识/分歧类稳健性检验 (如与 dict/LLM 分歧指标对照) 搭配使用, 单篇文章的 bank-year 天然为 NaN (std 定义域要求 n不小于2). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 组内标准差 (dispersion, ddof=1) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_tech_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_tech_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_tech_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 底层技术子样本 (locus=底层技术)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。与 _app 同一 innovation_locus 分类维度的另一极 (值='底层技术', 指报道聚焦金融科技的基础设施/技术层面而非面向客户的应用场景) , 同样以 innovation_locus_full 做子样本过滤, 在该子集上对该 track 下 FinBERT-CN_正面 取组内 mean; _tech 与 _app 互斥且并不穷尽全部留篇样本 (LLM 标签缺失的文章计入分母 n_articles_llm_valid 但不落入任一子类, R6 口径为 >= 而非严格 ==). 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 底层技术子样本 (locus=底层技术) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_vw_ctx

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在实体窗轨 (ctx)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。实体窗轨 (ctx)文本构造: 标题 + 银行实体窗口正文 (content_ctx, 经 prepend_title 拼接)。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT-CN_正面_w_sum_ctx / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_vw_full

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在全文轨 (full)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。全文轨 (full)文本构造: 标题 + 全文正文 (content, 经 prepend_title 拼接); 全文轨是留篇门控轨 , 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT-CN_正面_w_sum_full / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 full 轨是留篇门控轨: 2026-06-29 起 stage 21 是否判定为一篇有效银行金科报道只看 llm_verified_full, ctx/ss 两轨行宇宙均是 full 轨留篇集合的子集, 属 conditional-on-full 的测度/稳健性轨。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

## VAR: finbert_cn_pos_vw_ss

【变体差分】
本列是 FinBERT-CN 模型 (yiyanghkust/finbert-tone-chinese（公开预训练中文金融三分类 BERT, 标签空间=正面/中性/负面）) 在同句轨 (ss)上的正面类概率, 聚合口径 = 密度值权加权 (value/mention-density weighted, VW)。同句轨 (ss)文本构造: 标题 + 银行和金科同句 前后各1 句窗正文 (content_ss); 若该篇文章不存在银行与金科词的同句共现, content_ss 回退为全文 body 且 ss_is_fallback=True, 镜像 ctx 轨回退语义。以文章级提及密度权重 w (词数/密度导出, Hassan et al. 2019, QJE 提及密度加权范式的中文语料实现) 为权重的加权均值: FinBERT-CN_正面_w_sum_ss / 该 track 下有效样本的密度权重和 , 密度权重刻画单篇报道中目标银行被提及的强度而非仅计篇数, 与等权基线互为稳健性 (等权把每篇文章记 1 票, VW 按提及密度赋权), 二者并排不构成同一过度识别设定. 本列与家族内同模型同轨的其余 6 类后缀 (等权/app/hw/mw/std/tech/vw 互斥集合) 互为稳健性并排比较, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 设定; 与另两家 BERT 模型 (FinSentZH, FinBERT2) 同口径同轨列亦是 per-model co-equal 稳健性关系, 任一模型缺席仅致其自身列族置 NaN (per-model 独立降级), 不触发家族内其余模型列联动清空。 本列所在的非 full 轨行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 该轨自身的分母/取值域按该轨源列的存在性独立计算, 缺该轨源列时由 valid_agg 自动过滤优雅跳过, 不借用 full 轨数值顶替。 数值解读上, 本列与家族其余 62 列共同构成 finbert_cn/fin_sent_zh/finbert2 三模型 × full/ctx/ss 三轨 × 等权/app/hw/mw/std/tech/vw 七类聚合口径的完整交叉表, 使用者在做正文主回归或稳健性表时应优先锚定等权基线 (无后缀) 作为该模型该轨的主测度, 再把 密度值权加权 (value/mention-density weighted, VW) 作为交叉验证或异质性分解的旁证列纳入附表, 而非把七类口径混进同一条回归方程当作互不相关的独立控制变量, 以免制造伪多重共线或伪过度识别问题。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. The Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification? Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science No. 194-206 [Working Paper]. https://doi.org/10.1007/978-3-030-32381-3_16
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
