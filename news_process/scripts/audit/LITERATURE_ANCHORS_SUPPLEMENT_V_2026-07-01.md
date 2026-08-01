# 文献理论锚点扩充报告 · 第五补编(2024–2026 最新文献为主 · 26 主题桶全覆盖 · 含 v3.15.0 双轨嵌入/词典消融等新指标 · APA 第 7 版 · Crossref/DataCite DOI→标题回比全核验)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


- **日期**: 2026-07-01
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 12 族/143 条)、`LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 10 族/102 条)、`LITERATURE_ANCHORS_EXPANSION_2026-06-22.md`(第二补编, 10 子族/63 条)、`LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md`(第三补编, 24 桶/108 条)、`LITERATURE_ANCHORS_SUPPLEMENT_IV_2026-06-26.md`(第四补编, 2 条)之后的 **第五补编**, 六者**合为一套**。前五份已建成 **416 条已核验锚点 / 396 个唯一 doi.org DOI**; 本第五补编按用户要求**再次大量补充 2024–2026 最新顶刊与工作论文**, 并补齐 v3.15.0 后新增/演进指标的学术出处——**Qwen3-Embedding-8B(硅基流动 4096 维) + text-embedding-3-large(`_lg`)co-primary 双轨嵌入**、**词典语言学规则消融梯度**(否定/程度/转折 powerset)、**generalized Bartik / leave-one-out 同伴 IV 扩展**等。
- **规模**: 工作流对抗层 confirm 148 → 经全语料 DOI+标题去重(剔除与前五份重叠 37 + DOI 自重 1)+ 主控直接 Crossref/DataCite 核验补入嵌入轨奠基锚 2 条(OpenAI 对比预训练嵌入 Neelakantan 2022 / MTEB EACL 2023)= 112 → **三审追剔 1 条同篇 preprint/published 重复**(arXiv 2412.19245 与已收正式发表版 FRL 10.1016/j.frl.2024.105227 同篇, 保留期刊版)后, **净增唯一锚点 111 条**, 其中 **97 条为 2024–2026**(占 **87%**), 工作论文(arXiv/NBER/SSRN)**60 条**; 覆盖 **26 主题桶**(对应 32 方法学族 + v3.15.0 后新增指标)。对抗层 reject 4 条均为 **claim-fit 不符**(DOI 真实可解析但论文与所锚指标不贴合), 连同上述 1 条同篇重复, 均已剔除。
- **生产方式**: 动态多智能体工作流 `litanchor-supplement-v-2024-2026`(26 主题桶并行, 共 **178 智能体**)。流水线 = 每桶 FIND 智能体(WebSearch 发现 + **提名前 `GET api.crossref.org/works/{DOI}`(arXiv 走 DataCite)DOI→标题自核验**) → 每候选独立对抗审计员(**二次独立解析 + 逐字标题回比 + claim-fit 诚实性检验, 默认 REJECT 直到证实**)。
- **核验铁律**: "查不实=不存在", **严禁自我生成参考文献**。本补编全部 111 条经 **第三道独立全语料本地核验**(`scripts/audit/audit_dois.py` 直连 Crossref/DataCite, 逐条 DOI→标题逐字回比 + 年份核验): **111/111 resolved, 0 UNRESOLVED / 0 TITLE_MISMATCH / 0 YEAR_DIFF**。下方每条后的 "Crossref/DataCite 回读标题" 为接口实际回读值。
- **合计**: 416(前五份)+ **111(本补编净增)** = **527 条**唯一文献锚点 / **507 个唯一 doi.org DOI**(全语料 `audit_dois.py` 实测 507 个)。

---

## 〇、白话导读

**这份补的是什么**: 前五份已把项目用到的方法和经典文献配齐(416 条)。用户再次要"尽可能多、且大量 2024–2026 最新"。这份就专门补**最近两三年**的顶刊论文与工作论文, 并补齐项目最近一次大改(v3.15.0)引入的**新指标**的出处——尤其是**换用 Qwen3-Embedding-8B + text-embedding-3-large 两个嵌入模型作 co-primary 双轨**这件事, 需要这两个模型本身的技术报告与"多嵌入模型互为稳健性"的方法学锚点。

**和"严禁自我生成"的关系**: 这些**不是编的**。每一条都被**两个互相独立的智能体**拿到 Crossref/DataCite 官方接口查 DOI、把官方回读标题与要引论文**逐字比对**, 对不上就丢; 之后又被本地脚本(直连 Crossref/DataCite)**第三次全量复核**(112/112 全部解析、0 错配)。每条后面的"回读标题"就是接口实际回读值。

**怎么用**: 写论文时按 §一各主题桶直接引用; 参考文献表抄各条 APA(已是第 7 版成品、DOI 全可点开)。**勿沿用代码注释里的旧版引用**。

---

## 一、26 主题桶 × 新增已核验锚点(2024–2026 优先)

### 五补-1. LLM 文本情感测度与多模型集成投票 (stage 21)

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Vamvourellis, D., & Mehta, D. (2025). Reasoning or overthinking: Evaluating large language models on financial sentiment analysis. arXiv. https://doi.org/10.48550/arXiv.2506.04574
  - *锚定* — stage 21 的零样本/低温情感判定提示设计：该文在专家标注的 Financial PhraseBank 上系统对比 GPT-4o/GPT-4.1/o3-mini 在直觉式与思维链提示下的表现，发现无 CoT 的直觉式提示最贴合人工判断，为本项目 temperature=0.0、非推理式 prompt v8 的取舍提供前沿 2025 经验依据。
  - 〔DataCite 回读标题: Reasoning or Overthinking: Evaluating Large Language Models on Financial Sentiment Analysis〕
- 【2024–2026】Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv. https://doi.org/10.48550/arXiv.2511.15714
  - *锚定* — stage 21 的多模型投票集成 (gpt54nano/gemini31/deepseekv4 三家)：该文在人工标注语料上比较 2/3/5/7/10 模型委员会的多数表决，证明 LLM 集成显著提升分类质量并抑制幻觉，为本项目三家投票而非单模型的设计提供方法学正当性。
  - 〔DataCite 回读标题: Majority Rules: LLM Ensemble is a Winning Approach for Content Categorization〕
- 【2024–2026】Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv. https://doi.org/10.48550/arXiv.2502.18036
  - *锚定* — `21_tone_llms` (construct-anchor)：为 stage 21 三家 LLM 事后多数投票 (gpt54nano / gemini31 / deepseekv4) 提供集成范式的分类学参照。该综述系统梳理 LLM 集成的推理前/中/后聚合谱系，可在方法节将本项目的事后多数投票定位到"输出级集成 (post-hoc / output ensemble)"一类并对照其权衡，属方法论类比与分类定位，而非对集成性能的实证背书。
  - 〔DataCite 回读标题: Harnessing Multiple Large Language Models: A Survey on LLM Ensemble〕
- 【2024–2026】Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
  - *锚定* — stage 21 用 LLM 对金融新闻做篇级情感标注这一核心方法：该文在 96 万余条美国财经新闻上用 LLM 直接产出情感分并驱动收益预测，为本项目以大模型替代词典/人工对银行金科报道判定语调 (llm_vote_tone) 提供频率最高的金融期刊级方法学背书。
  - 〔Crossref 回读标题: Sentiment trading with large language models〕

### 五补-2. 词典法情感 + 中文金融词典 + valence-shifter 规则消融 (stage 22)

> 净增 3 条(其中 3 条 2024–2026)。

> 注: 本节新增条目锚定**否定**(negation)valence-shifter 分量; 词典消融梯度的**程度副词**(Kennedy & Inkpen, 2006)与**转折/对比**(Taboada et al., 2011; Li et al., 2010)分量已在 `LITERATURE_ANCHORS_EXPANSION_2026-06-22.md` 子族 27 锚定, 三者共同覆盖 `_RULE_ABLATION_VARIANTS` 的 否定/程度/转折 powerset。

- 【2024–2026】Kirtac, K., & Germano, G. (2025). Large language models in finance: What is financial sentiment? arXiv. https://doi.org/10.48550/arXiv.2503.03612
  - *锚定* — 本项目 stage 21(LLM)/22(词典)/23(BERT)三测度三角的方法学定位。该文系统梳理从市场基、词典基到 NLP/LLM 的金融情感测度谱系, 支撑多测度互为稳健性、词典法与上下文模型并存而非替代的设计取向。
  - 〔DataCite 回读标题: Large language models in finance : what is financial sentiment?〕
- 【2024–2026】Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
  - *锚定* — `stage 22` 词典消融梯度中的否定翻转规则(negation valence shifter) / `_RULE_ABLATION_VARIANTS` 的 neg 分量(recent-application)。该文用无监督数学方法处理情感分析中的否定,实证显示否定处理对极性判定准确度的影响,与本项目把 neg 规则作为单列消融变体并报告其边际贡献的做法是平行的近期同法参照(其方法路径不同,非直接采用),呼应"否定值得独立消融"这一判断。
  - 〔Crossref 回读标题: Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach〕
- 【2024–2026】Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
  - *锚定* — 词典先验与预训练模型的融合, 即 stage 22(词典)与 stage 23(BERT)混合路径。该文把金融情感词典知识作为特征注入 PLM 提升中性识别, 支撑本项目词典轨与上下文模型并非互斥、可作为互补特征的设计理据。
  - 〔Crossref 回读标题: Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features〕

### 五补-3. BERT/FinBERT 文章级情感与长文档表示 (stage 23)

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Hicham, N., & Habbat, N. (2026). LLMs and generative AI for financial sentiment classification: An explainable domain-adaptive framework. Digital, 6(2), Article 48. https://doi.org/10.3390/digital6020048
  - *锚定* — `stage 23` (域适配 BERT 编码器轨) — recent-application。该 2026 MDPI Digital 框架在金融情感分类上系统对比域适配 transformer 编码器与生成式 LLM, 为本项目并置 BERT 编码器轨 (stage 23) 与三家 LLM 投票轨 (stage 21, gpt54nano/gemini31/deepseekv4) 的多方法三角验证设计提供近期同法参照。
  - 〔Crossref 回读标题: LLMs and Generative AI for Financial Sentiment Classification: An Explainable Domain-Adaptive Framework〕
- 【2024–2026】Nasiopoulos, D. K., Roumeliotis, K. I., Sakas, D. P., Toudas, K., & Reklitis, P. (2025). Financial sentiment analysis and classification: A comparative study of fine-tuned deep learning models. International Journal of Financial Studies, 13(2), Article 75. https://doi.org/10.3390/ijfs13020075
  - *锚定* — `stage 23 tone_berts`(recent-application): 该文在金融情感分类基准上系统比较微调后的 BERT、FinBERT 与 GPT-4o(-mini) 等模型, 量化微调对分类准确率的提升。为本项目在 stage 21 LLM 三模型投票(gpt54nano/gemini31/deepseekv4)之外, 保留 FinBERT 作为独立编码器情感轨的设计提供近期同法参照。
  - 〔Crossref 回读标题: Financial Sentiment Analysis and Classification: A Comparative Study of Fine-Tuned Deep Learning Models〕
- 【2024–2026】Zafar, M. B. (2025). FinAI-BERT: A transformer-based model for sentence-level detection of AI disclosures in financial reports. arXiv. https://doi.org/10.48550/arXiv.2507.01991
  - *锚定* — `stage 23 (tone_berts)` recent-application / 方法论类比 — 该文以微调 BERT 在英文金融报告中做句级 AI 披露检测, 为本项目编码器型 (BERT/FinBERT) 句级金融文本分类提供近期同法参照。仅为平行的句级 BERT 分类先例, 并不直接支撑 _ss 轨的中文金科 (fintech/AI) 共现判定、共现窗口设定或情感极性编码 — 这些子任务属本项目独立实现, 非该文方法可外推。
  - 〔DataCite 回读标题: FinAI-BERT: A Transformer-Based Model for Sentence-Level Detection of AI Disclosures in Financial Reports〕
- 【2024–2026】Delgadillo, J., Kinyua, J., & Mutigwe, C. (2024). FinSoSent: Advancing financial market sentiment analysis through pretrained large language models. Big Data and Cognitive Computing, 8(8), 87. https://doi.org/10.3390/bdcc8080087
  - *锚定* — stage 23 金融市场文本预训练编码器情感分析。FinSoSent 通过金融领域预训练提升市场情感分析, 是本项目 FinBERT 类编码器情感轨(对短金融文本做情感极性打分)的近期同类方法佐证。
  - 〔Crossref 回读标题: FinSoSent: Advancing Financial Market Sentiment Analysis through Pretrained Large Language Models〕

### 五补-4. 媒体报道语调/显著性 → 银行风险/存款流 (核心研究问题)

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Jacobs, H., & Lauber, A. (2025). Media sentiment and price run-ups. European Financial Management, 32(2), 677–700. https://doi.org/10.1111/eufm.70025
  - *锚定* — `llm_vote_tone_full` (P1 语气主轨) / P2 关注度轨 — recent-application (construct-anchor): 该文将企业级媒体情绪作为已测构造, 检验其与个股价格预涨 (price run-ups) 的横截面关联; 为本项目"媒体语气作为公司层横截面信号"的设定提供平行的近期同法参照 (呼应而非直接因果背书), 增强情感主轨外部效度的可比性。
  - 〔Crossref 回读标题: Media Sentiment and Price Run‐Ups〕
- 【2024–2026】Chen, Z., Li, Z., Liu, J., & Liu, X. (2026). Information salience, investor attention, and stock price crash risk. Journal of Empirical Finance, 85, Article 101670. https://doi.org/10.1016/j.jempfin.2025.101670
  - *锚定* — `stage 26 news_salience` / `attention_pct` 关注度-显著性测度 (P2 attention 轨, recent-application): 该文将"信息显著性"与"投资者关注"作为两个可分离的可测构造、并分别估计其对崩盘风险的影响, 为本项目把新闻显著性/关注度建模为独立于情感的测度提供了近期同法参照, 呼应而非直接证明本项目在 stage 26 上的显著性/关注度构造设定。
  - 〔Crossref 回读标题: Information salience, investor attention, and stock price crash risk〕
- 【2024–2026】Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN. https://doi.org/10.2139/ssrn.5220056
  - *锚定* — stage 21/40 的银行级新闻语气构造与面板聚合 (bank_fintech_tone、funding_cost 结果列): 该文用 NLP 在单个银行层面测量报纸语气随时间的迁移, 并验证语气指标对银行融资条件 (股价/成交量/存款) 的预测力, 是本项目'按银行-年聚合媒体语气测度银行风险'方法的最贴近前沿正当性来源。
  - 〔Crossref 回读标题: Measuring Tone Shifts in Media Coverage: An Empirical Application to Bank Financing Conditions in Italy〕
- 【2024–2026】Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373–1403. https://doi.org/10.1007/s11156-024-01383-0
  - *锚定* — '媒体负面语气/覆盖度 → 公司层风险结果'的面板因果链 (本项目以银行-年负面语气测度风险, benefit/brokerage 的 roa 等结果列): 该文以 6928 家跨国上市公司面板证明负面媒体覆盖推高总风险/特质风险/崩盘风险, 是面板回归口径的近因前沿对照。
  - 〔Crossref 回读标题: Media coverage of corporate social irresponsibility and firm equity risk〕

### 五补-5. 公司层面文本暴露度/注意力 (Hassan 2019 范式, stage 15)

> 净增 4 条(其中 3 条 2024–2026)。

- 【2024–2026】Tan, L., Wang, C., Sun, J., & Qian, Y. (2026). Measuring corporate risk using large language model embeddings: Evidence on corporate climate risk and supply chain restructuring. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.6507162
  - *锚定* — `stage 25 article_sbert` / `stage 26 semantic_staleness`（method-origin）：该 2026 工作用 LLM sentence embeddings 构造企业层面风险暴露度（气候风险与供应链重构），为本项目以嵌入度量金科语义暴露与陈旧度提供"用 LLM 嵌入构造企业层面暴露"的方法先例。仅作方法论类比——该文走单一嵌入 + 监督分类路径、核心贡献是分类精度改进，与 stage 25/26 基于余弦相似度的语义暴露/陈旧度度量并非完全同构，亦不为本项目 Qwen3-Embedding-8B ⟂ text-embedding-3-large 的 co-primary 双轨互稳健设计提供专项背书。
  - 〔Crossref 回读标题: <p>Measuring Corporate Risk Using Large Language Model Embeddings:</p>
<p>Evidence on Corporate Climate Risk and Supply Chain Restructuring</p>〕
- 【2024–2026】Fan, S., Wu, Y., & Yang, R. (2025). Measuring firm-level supply chain risk using a generative large language model. Finance Research Letters, 77, Article 107111. https://doi.org/10.1016/j.frl.2025.107111
  - *锚定* — `21_tone_llms` (method-origin)：该文用生成式 LLM 对中文调研纪要生成摘要、以"摘要相对长度/信息压缩率"作为公司层供应链风险暴露的代理，与本项目同属"在中文语料上以生成式 LLM 构造 firm-level 暴露/属性指标"的方法论谱系，为 stage 21 中文 LLM 测度提供跨领域的方法论类比参照。需说明二者 LLM 利用方式不同：该文走摘要长度代理，本项目 stage 21 走三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票的情感分类，测度原理、噪声结构与验证路径均不同，且领域分属供应链风险 vs. 金融科技情感暴露，故为平行的方法论呼应而非同构。
  - 〔Crossref 回读标题: Measuring firm-level supply chain risk using a generative large language model〕
- 【2024–2026】Huynh, N., & Le, Q. N. (2025). Firm-level supply chain risk exposure and stock price crash risk: Evidence from textual analysis. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.5188882
  - *锚定* — `stage 40` bank-year 面板 / 文本派生暴露列 → 财务结果识别设计（recent-application 近期同法应用）：该文将 firm-level 文本暴露测度作为解释变量进入面板回归、预测企业层面财务结果（股价崩盘风险),为项目 stage 40 把金科暴露/注意力列接入下游财务结果的识别设计提供平行的近期同法参照。属设计层方法论类比(该文主题为供应链风险,非金科主题),呼应而非主题同构。
  - 〔Crossref 回读标题: Firm-Level Supply Chain Risk Exposure and Stock Price Crash Risk: Evidence from Textual Analysis〕
- Kim, A. G., Muhn, M., & Nikolaev, V. V. (2023). From transcripts to insights: Uncovering corporate risks using generative AI. SSRN Electronic Journal. https://doi.org/10.2139/ssrn.4593660
  - *锚定* — stage 21 tone_llms 的 LLM 三家投票暴露/风险判定:该文证明用生成式 LLM 从文本抽取的 firm-level 政治/气候/AI 暴露度在预测波动率与投资创新上优于词典/bigram 测度,直接为项目以 LLM 抽取银行对金科主题暴露(而非纯词典)提供前沿方法背书。
  - 〔Crossref 回读标题: From Transcripts to Insights: Uncovering Corporate Risks Using Generative AI〕

### 五补-6. 实质 vs 象征 / decoupling (P3 substance)

> 净增 5 条(其中 5 条 2024–2026)。

- 【2024–2026】Cai, W., Shi, W., & Jiang, F. (2025). Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance. British Journal of Management, 36(1), 361–382. https://doi.org/10.1111/1467-8551.12853
  - *锚定* — 锚'披露文本强度是否预示真实行动'的实证识别框架: 把战略披露强度作为潜在 cheap talk, 检验其与真实风险承担/绩效的关系。为本项目 stage 21 情感/强度文本测度通往真实结果 (P3 cost_income_ratio_change_3yr) 的 symbolic-vs-substantive 推断提供方法对标。
  - 〔Crossref 回读标题: Cheap Talk? Strategy Disclosure Intensity, Corporate Risk‐Taking and Financial Performance〕
- 【2024–2026】Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427–462. https://doi.org/10.1111/eufm.12509
  - *锚定* — 锚文本侧 decoupling 量化的方法学: 以 NLP 从 CSR 报告抽取象征性陈述并量化与实质行动的背离 (greenwashing)。映射到本项目把'金科washing'操作化为文本测度的做法, 支撑 P3 substance 文本特征工程与象征性陈述识别。
  - 〔Crossref 回读标题: Identifying greenwashing in corporate‐social responsibility reports using natural‐language processing〕
- 【2024–2026】Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M. (2025). Detecting greenwashing: A natural language processing literature survey. arXiv. https://doi.org/10.48550/arXiv.2502.07541
  - *锚定* — 锚方法学全景的稳健性引用: 系统梳理 61 篇用 NLP 识别象征性/欺骗性企业沟通的工作, 覆盖特异性、立场、论证结构与欺骗性语言线索等维度。为本项目 P3 substance 的文本测度选型 (specificity/stance/cheap-talk cues) 提供 frontier 综述支撑, 界定本方法在文献谱系中的位置。
  - 〔DataCite 回读标题: Detecting Greenwashing: A Natural Language Processing Literature Survey〕
- 【2024–2026】Hassani, B. K., Bahini, Y., & Mushtaq, R. (2025). Discourse vs emissions: Analysis of corporate narratives, symbolic practices, and mimicry through LLMs. arXiv. https://doi.org/10.48550/arXiv.2510.01222
  - *锚定* — 锚 LLM 驱动的'话语 vs 真实行为'背离测度: 用 LLM 量化企业叙事中的象征性实践与同群模仿 (mimicry), 与真实排放对照。直接对应本项目 stage 21 三家 LLM 投票文本测度与真实金科结果的 decoupling 设计, 并为 P5 collab/同群模仿机制提供方法接口。
  - 〔DataCite 回读标题: Discourse vs emissions: Analysis of corporate narratives, symbolic practices, and mimicry through LLMs〕
- 【2024–2026】Chen, X., Wan, P., Ma, Z., & Yang, Y. (2024). Does corporate digital transformation restrain ESG decoupling? Evidence from China. Humanities and Social Sciences Communications, 11(1), Article 407. https://doi.org/10.1057/s41599-024-02921-w
  - *锚定* — `substance-decoupling` 缺口变量构造 (construct-anchor): 该文为中国上市公司显式构造象征(披露)与实质(行动)之间的 ESG decoupling 缺口变量, 并以数字化/科技转型作调节项。为本项目把"金科采用象征 vs 实质"操作化为 bank-year 缺口变量、并在中国银行制度语境下解释, 提供平行的同法参照(方法论类比, 非直接实证支持: 其结果落在 ESG 而非银行金科语境)。
  - 〔Crossref 回读标题: Does corporate digital transformation restrain ESG decoupling? Evidence from China〕

### 五补-7. FinTech 基础设施 vs 应用层 locus (P4) + 银行-金科协同 (P5)

> 净增 5 条(其中 5 条 2024–2026)。

- 【2024–2026】Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
  - *锚定* — P4 locus 的创新产出 outcome citation_weighted_patent。该文实证银行金科股权投资→银行自身商标/专利申请显著上升 (1 SD 投资对应专利 +13-14%), 把'金科作为创新基础设施/locus 外移'与银行专利度量直接连接, 为 locus-of-innovation 设定提供最新 (2026) 量化锚。
  - 〔Crossref 回读标题: Investing in fintech equity and bank innovation〕
- 【2024–2026】Dehghani, M. A., Brauneis, A., & Karavidas, D. (2026). Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions. Technological Forecasting and Social Change, 226, 124581. https://doi.org/10.1016/j.techfore.2026.124581
  - *锚定* — P4 locus / P5 collab 的 open innovation (Chesbrough 谱系) 构念与'基础设施层 vs 应用层'的理论区分。该文对比传统银行与金科公司的 IP 管理与开放式创新实践, 为 stage 16 policy_alignment / fintech_intensity 中区分自研 vs 外部协作创新提供前沿框架。
  - 〔Crossref 回读标题: Patent strategies in the age of FinTech: Understanding IP management practices and open innovation across financial institutions〕
- 【2024–2026】Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2025). The role of banks' business models in their FinTech acquisitions. Journal of Financial Services Research. https://doi.org/10.1007/s10693-024-00442-w
  - *锚定* — P5 collab 金科并购 treatment 的异质性来源。该文证多元化业务模式的银行更倾向金科并购, 为面板中按银行商业模式切分 m_and_a_fintech / 伙伴关系倾向 (异质性/IV 暴露列) 提供识别逻辑与前沿 (2025) 引用支撑。
  - 〔Crossref 回读标题: The Role of Banks’ Business Models in their FinTech Acquisitions〕
- 【2024–2026】Puri, M., Qian, Y., & Zheng, X. (2024). From competitors to partners: Banks' venture investments in fintech (NBER Working Paper No. 33297). National Bureau of Economic Research. https://doi.org/10.3386/w33297
  - *锚定* — `m_and_a_fintech` (P5 collab outcome) — recent-application。该文实证银行对金科创业公司的风险投资 (VC/少数股权, 非完全或控股并购), 记录由竞争转向合作 (运营协作+知识转移) 的伙伴关系演化。**口径校准**: 本文证据落在「股权投资/VC」这一协作模态, 与 `m_and_a_fintech` 所指的并购 (完全/多数收购) 是相邻但不同范畴, 故仅为 P5「银行—金科由竞争走向伙伴」这一更宽协作构念提供前沿 (2024) 平行参照与概念背景, 不直接支持 M&A 维度的因果识别。
  - 〔Crossref 回读标题: From Competitors to Partners: Banks’ Venture Investments in Fintech〕
- 【2024–2026】Zheng, H., & Mao, M. Q. (2024). Fintech mergers and acquisitions. Journal of International Money and Finance, 143, Article 103076. https://doi.org/10.1016/j.jimonfin.2024.103076
  - *锚定* — `m_and_a_fintech` (P5 collab outcome, construct-anchor): 该文以"金科并购"为题, 系统刻画银行/机构对金融科技标的的并购行为, 为面板中 P5 协作结果变量 `m_and_a_fintech` (银行—金科并购/合作) 的构造与界定提供直接的构念参照。其关于并购后创新产出的讨论可为本变量与创新指标的关联分析提供平行的同法参照 (具体专利数量/质量结论以原文为准, 此处不作强断言)。
  - 〔Crossref 回读标题: Fintech mergers and acquisitions〕

### 五补-8. 羊群行为 / 信息陈旧度 / 注意力衰减 (stage 24 herd_decay, stage 26 semantic_staleness)

> 净增 4 条(其中 3 条 2024–2026)。

- 【2024–2026】Hirshleifer, D., Peng, L., & Wang, Q. (2025). News diffusion in social networks and stock market reactions. The Review of Financial Studies, 38(3), 883–937. https://doi.org/10.1093/rfs/hhae025
  - *锚定* — `stage 24 herd_decay` (注意力/反应时间衰减) — recent-application。该文研究新闻经社会网络扩散后股市反应的时变结构 (即时价格反应、随后漂移、波动率与成交量动态)。其总体发现——网络中心度更高的节点引发更强即时反应、随后漂移与波动率衰减更快、而成交量更持久——与本项目「新闻经网络扩散后注意力按衰减核衰退」的羊群衰减建模相呼应, 为该建模提供平行的近期外部参照 (具体方向性结论若需在正文引用须回溯原文表/图逐条 pin 页码)。
  - 〔Crossref 回读标题: News Diffusion in Social Networks and Stock Market Reactions〕
- 【2024–2026】Zhang, S., Miao, W., & Zhang, Y. (2025). Institutional investor diversity, herding behavior, and systemic financial risk: Evidence from China. Risks, 13(12), 243. https://doi.org/10.3390/risks13120243
  - *锚定* — stage 24 羊群行为测度本身, 并贴合本项目中国银行/金融机构语境。该文用 84 家中国金融机构构造机构投资者多样性的新测度并以极值理论估计系统性风险, 发现多样性显著抑制羊群、间接降低系统性风险, 为'羊群度量 → 银行层系统性后果'的链路提供 2025 年中国市场前沿锚。
  - 〔Crossref 回读标题: Institutional Investor Diversity, Herding Behavior, and Systemic Financial Risk: Evidence from China〕
- 【2024–2026】Wu, C. (2025). Novelty and impact of economics papers. arXiv. https://doi.org/10.48550/arXiv.2511.01211
  - *锚定* — `stage 26 semantic_staleness_*`（method-origin）。该文用大语言模型把论文新颖度分解为"空间维度"(智识独特性) 与"时间维度"(对研究前沿的参与) 两个语义维度，为本项目以嵌入语义相似度判定一篇报道是新内容还是旧素材再拼接的 staleness 度量提供 2025 年 LLM 语义新颖度框架的方法论参照。注意是平行的同法近期参照而非直接支持：Wu (2025) 走的是 LLM 语义分解，并不依赖非常规引用/知识网络重组 (citation recombination) 那一支操作化，本项目亦不照搬其空间/时间二分。
  - 〔DataCite 回读标题: Novelty and Impact of Economics Papers〕
- Glasserman, P., Mamaysky, H., & Qin, J. (2023). New news is bad news. arXiv. https://doi.org/10.48550/arXiv.2309.05560
  - *锚定* — `semantic_staleness_*` (stage 26 article_staleness, 上游 stage 25 article_sbert 嵌入) · method-origin · 用语言模型在大规模新闻语料上以条件熵构造"新闻文本分布变化"的新颖度测度, 证明新颖度上升预测未来负的市场与宏观结果并携带负风险溢价。与本项目以 MinHash/嵌入式刻画的语义陈旧度构成方法论类比的对立面参照(熵式新颖度 vs. 陈旧/再循环度量), 为"高新颖度=真新信息、低新颖度=再循环陈旧内容"的刻画提供近期方法学前沿对照。
  - 〔DataCite 回读标题: New News is Bad News〕

### 五补-9. 句/文档嵌入 · LLM 指令微调嵌入 · 语义相似度 (Qwen3-Embedding-8B / text-embedding-3-large co-primary 双轨, stage 15/25/26)

> 净增 8 条(其中 6 条 2024–2026)。

- 【2024–2026】Zhang, Y., Li, M., Long, D., Zhang, X., Lin, H., Yang, B., Xie, P., Yang, A., Liu, D., Lin, J., Huang, F., & Zhou, J. (2025). Qwen3 Embedding: Advancing text embedding and reranking through foundation models. arXiv. https://doi.org/10.48550/arXiv.2506.05176
  - *锚定* — stage 25 `article_sbert` 的 canonical 无后缀槽 `Qwen/Qwen3-Embedding-8B` (硅基流动, 4096 维) — construct-anchor / 模型出处: 本项目主测度嵌入引擎的官方技术报告, 交代 0.6B/4B/8B 三档骨干、MRL 可变维度与多语训练配方, 为"用 instruction-tuned LLM 嵌入做中文银行金科文本表征"提供模型出处与维度合法性依据; 与 co-primary `_lg` 轨 (text-embedding-3-large) 互为稳健性。
  - 〔DataCite 回读标题: Qwen3 Embedding: Advancing Text Embedding and Reranking Through Foundation Models〕
- 【2024–2026】Tang, Y., & Yang, Y. (2025). FinMTEB: Finance massive text embedding benchmark. arXiv. https://doi.org/10.48550/arXiv.2502.10990
  - *锚定* — stage 15/25/26 在金融领域专门评估嵌入质量的合法性 — FinMTEB 含中英财经新闻/年报/财报电话会等 64 个金融嵌入数据集, 证实领域适配嵌入在金融 STS 任务上的增益, 为本项目'用嵌入做金科语义强度/语义陈旧度'与 co-primary 稳健性比较提供领域基准依据。
  - 〔DataCite 回读标题: FinMTEB: Finance Massive Text Embedding Benchmark〕
- 【2024–2026】Gabaix, X., Koijen, R. S. J., Richmond, R. J., & Yogo, M. (2025). Asset embeddings (NBER Working Paper No. 33651). National Bureau of Economic Research. https://doi.org/10.3386/w33651
  - *锚定* — '把文本/资产嵌入向量直接用作金融经济计量变量'这一前沿应用范式 — 该文以 10-K、财报电话会与新闻的 LLM 嵌入 (Cohere/OpenAI) 表征企业业务活动, 为 stage 25/26 把嵌入派生量 (语义强度、staleness) 接入 bank-year 面板作经济计量度量提供顶刊级 (NBER, 2025) 的方法学正当性。
  - 〔Crossref 回读标题: Asset Embeddings〕
- 【2024–2026】Lee, C., Roy, R., Xu, M., Raiman, J., Shoeybi, M., Catanzaro, B., & Ping, W. (2024). NV-Embed: Improved techniques for training LLMs as generalist embedding models. arXiv. https://doi.org/10.48550/arXiv.2405.17428
  - *锚定* — `stage 25 (article_sbert) / stage 26 (semantic_staleness)` method-origin — latent attention 池化、去因果掩码对比训练、两阶段 instruction-tuning 这一类把解码器 LLM 改造为通用句/篇嵌入器的架构创新, 为本项目用 instruction-tuned LLM 嵌入 (canonical 槽 Qwen3-Embedding-8B) 替代 mean-pooling BERT 的选型论断提供平行的同法佐证。NV-Embed 系 NVIDIA 体系成果, 与阿里 GTE-Qwen 一脉的 Qwen3-Embedding 是相似架构思路的平行发展, 二者无前身—后继的谱系关系, 此处仅作方法论类比, 不主张其为 Qwen3-Embedding 的技术前身。
  - 〔DataCite 回读标题: NV-Embed: Improved Techniques for Training LLMs as Generalist Embedding Models〕
- 【2024–2026】Wang, L., Yang, N., Huang, X., Yang, L., Majumder, R., & Wei, F. (2024). Improving text embeddings with large language models. arXiv. https://doi.org/10.48550/arXiv.2401.00368
  - *锚定* — `stage 25/26 嵌入 (Qwen3-Embedding-8B 轨)` — method-origin (方法论谱系)。本文是 instruction-tuned、decoder-only LLM 文本嵌入路线 (指令 + 合成数据微调) 的代表性奠基文献, 为 canonical 嵌入槽 Qwen/Qwen3-Embedding-8B 所遵循的范式提供方法谱系参照; 其在 MTEB/BEIR 上刷新 SOTA, 亦为以该类基准衡量嵌入质量提供依据。注: 此范式仅覆盖 co-primary 的 Qwen3 轨, _lg 轨 (text-embedding-3-large, OpenAI) 不属此谱系; 项目已于 v3.14.0 移除全部本地嵌入模型 (含 E5-mistral), 故仅作通用方法谱系引用而非项目实现。
  - 〔DataCite 回读标题: Improving Text Embeddings with Large Language Models〕
- 【2024–2026】Chen, J., Xiao, S., Zhang, P., Luo, K., Lian, D., & Liu, Z. (2024). M3-Embedding: Multi-linguality, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. arXiv. https://doi.org/10.48550/arXiv.2402.03216
  - *锚定* — stage 25 三轨 (full/ctx/ss) 与 stage 26 staleness 对'中文长文档 + 8192 token 多粒度嵌入'的需求 — M3 的多语/多粒度/自知识蒸馏正面支撑对中文银行新闻这类长文本做语义嵌入的可行性, 也是项目曾用 BGE-M3 作第四轨 (`_bge`) 的出处。
  - 〔DataCite 回读标题: M3-Embedding: Multi-Linguality, Multi-Functionality, Multi-Granularity Text Embeddings Through Self-Knowledge Distillation〕
- Muennighoff, N., Tazi, N., Magne, L., & Reimers, N. (2023). MTEB: Massive text embedding benchmark. In Proceedings of the 17th Conference of the European Chapter of the Association for Computational Linguistics (pp. 2014–2037). Association for Computational Linguistics. https://doi.org/10.18653/v1/2023.eacl-main.148
  - *锚定* — co-primary 双轨\"多嵌入模型选型 + 跨模型 parity\"设计的方法学参照出处。construct-anchor。MTEB 在 8 类任务、58 数据集、112 语言上统一评测文本嵌入模型, 实证\"没有单一嵌入模型在所有任务上称霸\"; 该\"无普适最优\"结论为本项目并用 canonical `Qwen/Qwen3-Embedding-8B` 与 co-primary `_lg` (`text-embedding-3-large`) 两轨互为稳健性、而非独选其一提供方法学依据。需注意 MTEB 评测的是模型本身, 并未直接规定面板层 dual-track 设计, 故此处为方法论类比式的呼应而非直接同构。
  - 〔Crossref 回读标题: MTEB: Massive Text Embedding Benchmark〕
- Neelakantan, A., Xu, T., Puri, R., Radford, A., Han, J. M., Tworek, J., Yuan, Q., Tezak, N., Kim, J. W., Hallacy, C., Heidecke, J., Shyam, P., Power, B., Nekoul, T. E., Sastry, G., Krueger, G., Schnurr, D., Such, F. P., Hsu, K., ... Weng, L. (2022). Text and code embeddings by contrastive pre-training. arXiv. https://doi.org/10.48550/arXiv.2201.10005
  - *锚定* — `_lg` 轨 = text-embedding-3-large(OpenAI, 3072 维)的方法谱系直接出处 — 该文提出以对比预训练在大规模(文本,文本)/(代码,代码)正负对上训练通用稠密嵌入(cpt-text/cpt-code, 即 text-embedding 系列同源技术路线), 为本项目 co-primary 双轨中 OpenAI `_lg` 槽提供模型层方法学锚, 与 canonical Qwen3-Embedding 轨(硅基流动 4096 维)互为稳健性、严格 parity。method-origin。
  - 〔DataCite 回读标题: Text and Code Embeddings by Contrastive Pre-Training〕

### 五补-10. 可读性 / 词法复杂度 / 数值强度 (clarity, num_intensity)

> 净增 3 条(其中 3 条 2024–2026)。

- 【2024–2026】Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y. (2024). Annual report readability and trade credit financing: Evidence from China. Research in International Business and Finance, 69, Article 102220. https://doi.org/10.1016/j.ribaf.2024.102220
  - *锚定* — `bank_news_clarity` (provisional 论文, clarity/readability 主轨) — construct-anchor。该文研究中国上市公司年报可读性及其对商业信用融资的经济后果，为中文语境下文本可读性度量提供本土化方法参照。⚠ 体裁差异需注意：研究对象是年报，与本管线的银行/金科新闻在文风、长度、读者对象上不同，故仅作可读性构念的平行方法参照、而非直接背书新闻主轨；其具体度量工具（如中文 Fog 指数等）须以论文方法节原文为准，本锚不就此作实质断言。
  - 〔Crossref 回读标题: Annual report readability and trade credit financing: Evidence from China〕
- 【2024–2026】Jiang, Z., Hu, L., & Wang, Z. (2024). Better or worse? Revealing the impact of common institutional ownership on annual report readability. Humanities and Social Sciences Communications, 11(1), Article 688. https://doi.org/10.1057/s41599-024-03162-7
  - *锚定* — `bank_news_clarity` (provisional 轨) construct-anchor — 该文是中国上市公司治理因果研究 (共同机构持股 → 年报可读性作被解释变量), 为"文本可读性"作为中国语境下合法的实证被解释/结果变量提供近期同法参照; 它使用而非验证可读性测度, 故仅作平行应用佐证, 不主张其支撑构念测量方法。
  - 〔Crossref 回读标题: Better or worse? Revealing the impact of common institutional ownership on annual report readability〕
- 【2024–2026】Abedin, M. Z., Goldstein, M. A., Huang, Q., & Zeng, H. (2024). Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis. International Review of Financial Analysis, 95, 103484. https://doi.org/10.1016/j.irfa.2024.103484
  - *锚定* — 中文 MD&A 文本特征的多维 NLP 度量 (readability + tone + forward-looking) 与其市场后果。关键点：文中明确『可读性与语气改善会强化前瞻披露对流动性的效应』，为本管线把 readability/complexity 轨与 tone (stage 21) 轨联用、并主张可读性放大语气信息含量提供 2024 中国实证依据。
  - 〔Crossref 回读标题: Forward-looking disclosure effects on stock liquidity in China: Evidence from MD&A text analysis〕

### 五补-11. LLM 前视偏误 / 数据污染 / 时间泄漏 (DC4)

> 净增 3 条(其中 3 条 2024–2026)。

- 【2024–2026】Gao, Z., Jiang, W., & Yan, Y. (2025). Detecting lookahead bias in LLM forecasts. arXiv. https://doi.org/10.48550/arXiv.2512.23847
  - *锚定* — `stage 21`(三家投票情感 LLM:gpt54nano/gemini31/deepseekv4)— recent-application(方法论类比)。该文针对 LLM 金融预测任务(股票收益、资本支出预测)提出 Lookahead Propensity (LAP) 统计量,训练截止前显著为正、截止后骤降为零,其实证案例之一为"新闻标题预测股票收益"。本项目 stage 21 是对历史新闻做情感极性分类、并非令 LLM 直接预测未来市场结果,污染路径(训练语料是否含该批新闻的后续解读/标签)与预测任务并不相同,故二者属同类威胁的近似案例而非同构:该文为本项目披露 LLM 测量工具的训练数据泄漏威胁、并提供可操作检测思路提供平行参照。
  - 〔DataCite 回读标题: Detecting Lookahead Bias in LLM Forecasts〕
- 【2024–2026】He, S., Lv, L., Manela, A., & Wu, J. (2025). Instruction tuning chronologically consistent language models. arXiv. https://doi.org/10.48550/arXiv.2510.11677
  - *锚定* — stage 21 所用 instruction-tuned LLM(gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash 均为指令微调模型)的链时一致性问题。该文把链时约束从预训练延伸到指令微调阶段,正对本项目'指令微调模型在 prompt v8 下打情感分'这一环节,说明仅靠预训练截止不足以消除泄漏。
  - 〔DataCite 回读标题: Instruction Tuning Chronologically Consistent Language Models〕
- 【2024–2026】Wongchamcharoen, P. K., & Glasserman, P. (2025). Do large language models (LLMs) understand chronology? arXiv. https://doi.org/10.48550/arXiv.2511.14214
  - *锚定* — `21_tone_llms`(冻结 prompt v8 + 离线缓存复现)recent-application — 该文实证检验 LLM 的时序排序与时间一致性能力(chronological ordering / conditional sorting / anachronism detection),为本项目"某时点 LLM 判定是否真受时间约束"这一有效性假设提供近期平行参照:即便冻结 prompt 与缓存可字节级复现,模型内化的时间认知本身仍可能对 2007–2025 时序语料泄漏前瞻信息(lookahead contamination)。据此在 manuscript 中将其作为需讨论的风险而非断言其不存在。
  - 〔DataCite 回读标题: Do Large Language Models (LLMs) Understand Chronology?〕

### 五补-12. 同业/同伴效应识别 · leave-one-out IV · 网络溢出 (llm_peer)

> 净增 6 条(其中 5 条 2024–2026)。

- 【2024–2026】Tchuente, G. (2026). Who matters to whom? Identifying peer effects with propagation geometry. arXiv. https://doi.org/10.48550/arXiv.2602.23594
  - *锚定* — `leave_one_out_peer_*_iv` / `bartik_*_iv`（method-origin / 方法论类比）：本文以"传播几何"（propagation geometry）框架用网络拓扑结构（边际影响异质性与非冗余传播路径）推导几何导出工具变量来识别同伴效应，为以网络结构作为外生变异来源识别同伴溢出提供概念性理论基础。注：本文并不涉及广义 Bartik / shift-share 或同组 LOO 均值 IV——后两者是本管线自有的 IV 引擎，此处仅作"用网络拓扑识别谁影响谁"的方法论类比参照，非对具体引擎的直接支撑。
  - 〔DataCite 回读标题: Who Matters to Whom? Identifying Peer Effects with Propagation Geometry〕
- 【2024–2026】Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv. https://doi.org/10.48550/arXiv.2504.05658
  - *锚定* — llm_peer 项目与 leave_one_out_peer_*_iv 排除自身工具的因果识别正当性：在未观测混淆下用双工具变量非参数识别因果同伴效应估计量，为本管线把同伴均值用 LOO 工具变量化、绕开 Manski 反射问题提供 2025 前沿方法学依据。
  - 〔DataCite 回读标题: Identification and estimation of causal peer effects using instrumental variables〕
- 【2024–2026】Houndetoungan, A. (2025). Quantile peer effect models. arXiv. https://doi.org/10.48550/arXiv.2506.12920
  - *锚定* — `leave_one_out_peer_*_iv`（recent-application）：本管线以同组 leave-one-out 均值构造排除自身的同伴工具，识别均值层面的同伴效应；该文将同伴效应推广到 peer outcome 分布的各分位数（quantile peer effects），与本管线属平行的同法近期应用，为在均值同伴效应之外报告分布异质的同伴影响提供 2025 年方法学参照，而非直接采用其分位数设定。
  - 〔DataCite 回读标题: Quantile Peer Effect Models〕
- 【2024–2026】Nibbering, D., & Oosterveen, M. (2025). Policy-relevant causal effect estimation using instrumental variables with interference. arXiv. https://doi.org/10.48550/arXiv.2509.12538
  - *锚定* — 存在干扰/溢出（interference）时 IV 估计的政策相关解读：用同伴工具部分识别溢出效应、同时固定个体自身工具以区分直接与溢出效应，正面支撑本管线 leave_one_out_peer / bartik IV 在 SUTVA 失效（同伴互相影响）情形下的识别论证。
  - 〔DataCite 回读标题: Policy-relevant causal effect estimation using instrumental variables with interference〕
- 【2024–2026】Herstad, E. I., & Shin, M. (2024). Identification of a rank-dependent peer effect model. arXiv. https://doi.org/10.48550/arXiv.2410.14317
  - *锚定* — `leave_one_out_peer_*_iv`（method-origin，方法论类比/平行参照）：本管线第一个 IV 引擎为"同组 LOO 均值"，属标准 linear-in-means 排除自身均值的工具变量（识别依赖 Bramoullé / Angrist 型排除约束），并非秩依赖设定。Herstad & Shin (2024) 给出秩依赖 rank-dependent 同伴效应模型的识别条件，为同伴效应识别这一问题域提供平行的近期方法论参照，提醒同伴权重设定的识别敏感性；但本管线并未采用其秩依赖权重，故仅作类比呼应而非直接理论支撑。
  - 〔DataCite 回读标题: Identification of a Rank-dependent Peer Effect Model〕
- Hoshino, T. (2023). Causal interpretation of linear social interaction models with endogenous networks. arXiv. https://doi.org/10.48550/arXiv.2308.04276
  - *锚定* — 网络内生性下线性社会互动模型的因果解读（leave_one_out_peer / llm_peer IV 排除限制的合法性前提）：当同伴网络本身内生时给出系数的因果可解释条件，支撑本管线用 exclude-own LOO 与媒体来源外生暴露处理网络内生、捍卫排除限制。
  - 〔DataCite 回读标题: Causal Interpretation of Linear Social Interaction Models with Endogenous Networks〕

### 五补-13. 面板 / 高维固定效应 / 聚类稳健推断 (reghdfe)

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】MacKinnon, J. G. (2026). When can we trust cluster-robust inference? arXiv. https://doi.org/10.48550/arXiv.2604.02000
  - *锚定* — `cluster(bank)` 聚类稳健标准误 (method-origin / recent-application): 本项目在 86 家银行 (簇数有限) 且簇规模与杠杆高度异质的面板上做 bank 维度聚类推断。该文系统刻画 CRVE 失效条件与诊断量, 并讨论 wild bootstrap 作为补救, 为本项目判定聚类标准误何时可信、是否改用 wild bootstrap (rwolf 稳健性 battery 旁) 提供近期同法的方法学参照。
  - 〔DataCite 回读标题: When Can We Trust Cluster-Robust Inference?〕
- 【2024–2026】Chen, K. (2025). Inference in high-dimensional panel models: Two-way dependence and unobserved heterogeneity. arXiv. https://doi.org/10.48550/arXiv.2504.18772
  - *锚定* — 本项目最宽达约 2782 列的高维面板 (大量文本派生控制 + 嵌入特征) 在双向依赖与不可观测异质性下的推断。该文给出高维面板下兼顾 two-way dependence 与个体固定效应的有效推断, 为高维控制集进入 TWFE 时的标准误有效性提供前沿支撑。
  - 〔DataCite 回读标题: Inference in High-Dimensional Panel Models: Two-Way Dependence and Unobserved Heterogeneity〕
- 【2024–2026】Hahn, J., Hughes, D. W., Kuersteiner, G., & Newey, W. K. (2024). Efficient bias correction for cross-section and panel data. Quantitative Economics, 15(3), 783–816. https://doi.org/10.3982/QE2350
  - *锚定* — 本项目短面板 (盘上 T=2, 生产 T=19) 银行+年份双向固定效应下的 incidental-parameter (附带参数) 偏差问题。该文给出 leave-one-out / split-sample jackknife 的高阶方差与高效偏差修正, 为 bank-year 面板系数在固定效应估计下的偏差校正提供前沿方法依据。
  - 〔Crossref 回读标题: Efficient bias correction for cross‐section and panel data〕
- 【2024–2026】MacKinnon, J. G., Nielsen, M. Ø., & Webb, M. D. (2024). Jackknife inference with two-way clustering. arXiv. https://doi.org/10.48550/arXiv.2406.08880
  - *锚定* — bank-year 面板可能存在的双向聚类 (银行 × 年份) 推断。该文将 jackknife CRVE 推广到 two-way clustering, 解决双向聚类方差估计常见的不可信/负方差问题, 为本项目在年份共同冲击与银行个体相关并存时的标准误选择提供前沿依据。
  - 〔DataCite 回读标题: Jackknife inference with two-way clustering〕

### 五补-14. shift-share / Bartik 工具变量 (iv_extensions: generalized Bartik)

> 净增 3 条(其中 3 条 2024–2026)。

- 【2024–2026】Borusyak, K., & Hull, P. (2025). Optimal formula instruments (NBER Working Paper No. 33594). National Bureau of Economic Research. https://doi.org/10.3386/w33594
  - *锚定* — 广义 Bartik / 公式型工具变量的 recentering 去偏与高效工具构造。本项目三引擎 (广义 Bartik / 媒体来源 house-style 暴露 / 同组 LOO) 本质都是'按暴露公式合成的工具变量', 该文的再中心化 (recentering) 程序与渐近高效工具刻画, 直接为 outlet_*_iv 与 bartik_*_iv 的偏误控制和功效提升提供前沿 (2025, 拟刊 Econometrica) 方法学依据。
  - 〔Crossref 回读标题: Optimal Formula Instruments〕
- 【2024–2026】Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748–771. https://doi.org/10.1093/jrsssa/qnad148
  - *锚定* — `bartik_*_iv` (stage 8z 广义 Bartik / shift-share IV 引擎), method-origin: Goldsmith-Pinkham 框架下各 share 须各自满足排他性约束这一过严假设的放松 — 允许部分 share 违反排他仍可识别。为 stage 8z 广义 Bartik 引擎在「份额内生」疑虑下的敏感性/falsification 论证提供方法论参照。注: 不涉及 `leave_one_out_peer_*_iv` (同组 LOO 均值的同伴效应工具, 无 Bartik/GP 意义上的份额矩阵结构, 故本锚定仅限 Bartik/份额支路)。
  - 〔Crossref 回读标题: Relaxing the exclusion restriction in shift-share instrumental variable estimation〕
- 【2024–2026】Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv. https://doi.org/10.48550/arXiv.2404.17049
  - *锚定* — 本项目 over-identified Hansen J 的铁律 (co-primary 双轨 / full-ctx-ss 三轨严禁混进同一过度识别检验)。该文系统刻画 shift-share 设计中不同识别假设隐含的过度识别约束及其检验, 正是 7 篇 paper_spec 的 2SLS 模板做 Hansen J 过度识别检验、以及'各 just-identified 轨并排而非合并'设计选择的直接理论支撑。
  - 〔DataCite 回读标题: Overidentification in Shift-Share Designs〕

### 五补-15. 错时 / 异质稳健 DiD 与事件研究

> 净增 1 条(其中 1 条 2024–2026)。

- 【2024–2026】Roth, J. (2026). Interpreting event-studies from recent difference-in-differences methods. The Japanese Economic Review, 77(2), 275–288. https://doi.org/10.1007/s42973-026-00235-x
  - *锚定* — 事件研究图的解读规范: 各前沿 DiD 估计量 (CS/SA/BJS/dCdH) 产出的 event-study 系数估计的是何种加权 ATT。为我们 .do 模板 coefplot/event-study 图的解释与脚注提供前沿方法依据, 防止动态系数被误读为简单处理效应。
  - 〔Crossref 回读标题: Interpreting event-studies from recent difference-in-differences methods〕

### 五补-16. 稳健性 battery (Oster δ / Romano-Wolf FWER / wild bootstrap / PPML / qreg / winsorize)

> 净增 7 条(其中 5 条 2024–2026)。

- 【2024–2026】Kwon, O., Yoon, J., & Yotov, Y. V. (2025). A generalized Poisson-pseudo maximum likelihood estimator. Journal of Business & Economic Statistics, 44(2), 560–573. https://doi.org/10.1080/07350015.2025.2544190
  - *锚定* — PPML 估计环节(Stata `ppmlhdfe`),用于专利计数 / 投资额 / 并购计数等非负偏态、含零的 outcome(P2 `ln_fintech_investment`、P4 `citation_weighted_patent`、P5 `m_and_a_fintech`)。该文检验 PPML 高效性赖以成立的等方差比假设(CVMR),并给出更高效的 G-PPML 与 CVMR 设定检验,为本管线选用 PPML 的稳健性辩护提供 2025 前沿依据。
  - 〔Crossref 回读标题: A Generalized Poisson-Pseudo Maximum Likelihood Estimator〕
- 【2024–2026】Rambachan, A., & Roth, J. (2025). Design-based uncertainty for quasi-experiments. Journal of the American Statistical Association, 121(553), 477–491. https://doi.org/10.1080/01621459.2025.2526700
  - *锚定* — randomization inference / 设计型推断环节(Stata `ritest`)及面板不确定性来源的界定。该文为准实验(条件随机分配处理)给出设计型不确定性框架,正对应本管线把银行-金科曝光当作准随机处理时的有限总体推断口径,支撑 ritest 随机化检验相对抽样型标准误的合理性。
  - 〔Crossref 回读标题: Design-Based Uncertainty for Quasi-Experiments〕
- 【2024–2026】Diegert, P., Masten, M. A., & Poirier, A. (2025). An axiomatic approach to comparing sensitivity parameters. arXiv. https://doi.org/10.48550/arXiv.2504.21106
  - *锚定* — 稳健性 battery 中 Stata `oster` 系数稳定性界 (recent-application)。该文以公理化框架比较 residualization 型敏感性参数, 指出 Oster(2019) δ/β 类参数在控制变量内生时可能给出误导性的稳健性结论, 并刻画一致、单调的替代参数。为本管线报告 Oster δ 界时提供一个近期同法的批判性方法学参照, 提示该指标的解释边界 (而非直接背书其数值)。
  - 〔DataCite 回读标题: An Axiomatic Approach to Comparing Sensitivity Parameters〕
- 【2024–2026】Alvarez, L., Ferman, B., & Wüthrich, K. (2025). Inference with few treated units. arXiv. https://doi.org/10.48550/arXiv.2504.19841
  - *锚定* — 少处理单元 / 少处理簇下的 randomization inference 与 wild bootstrap 选择(Stata `ritest` + `wildbootstrap`)。本机银行-年面板(86 家、T=2)及子样本异质性分析常落入少处理单元情形,该 2025 综述系统梳理此设定下各类推断方法(含 wild-cluster bootstrap 的有效性边界),为本管线稳健性 battery 的方法选型提供前沿统一参考。
  - 〔DataCite 回读标题: Inference with few treated units〕
- 【2024–2026】Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
  - *锚定* — IV 扩展(`iv_extensions.py`:LOO 同组均值 / 广义 Bartik / outlet house-style 三引擎 + 7 个 2SLS 模板)在弱识别 + 少簇下的稳健推断。该文给出在仅个别簇强识别、甚至全簇弱识别时仍控制 size 的 wild bootstrap Wald / Anderson-Rubin 检验,直接支撑面板 IV 列族的聚类稳健 2SLS 推断。
  - 〔Crossref 回读标题: Wild bootstrap inference for instrumental variables regressions with weak and few clusters〕
- List, J. A., Shaikh, A. M., & Vayalinkal, A. (2023). Multiple testing with covariate adjustment in experimental economics. Journal of Applied Econometrics, 38(6), 920–939. https://doi.org/10.1002/jae.2985
  - *锚定* — `rwolf` / FWER 多重检验环节(Stata `rwolf`,recent-application)。本管线跨 11 篇 paper、多轨(full/ctx/ss)× 多词典消融变体产生大量并行假设,FWER 失控风险高;Stata `rwolf` 实现的是 Romano & Wolf(2005/2016)stepdown 程序,其直接方法学引文应为 Romano-Wolf 原文或 Clarke, Romano & Wolf(2020)。本文是 List-Shaikh-Xu(LSX)resampling 框架向协变量调整版的近期扩展,与 Romano-Wolf 属两条平行的 FWER 控制文献脉络,并非 `rwolf` 的上游——此处仅作为协变量调整版多重检验的补充方法学参照,不与 Romano-Wolf 并列提名为同一直接锚。
  - 〔Crossref 回读标题: Multiple testing with covariate adjustment in experimental economics〕
- Diegert, P., Masten, M. A., & Poirier, A. (2022). Assessing omitted variable bias when the controls are endogenous. arXiv. https://doi.org/10.48550/arXiv.2206.02303
  - *锚定* — Oster 型遗漏变量偏误稳健性界(Stata `oster`)的现代化替代。文本即数据管线大量使用 LLM/词典情感、嵌入相似度等可能与遗漏混杂相关的控制变量,该文给出控制变量内生时的 OVB 界与一致敏感性参数,为本项目 Oster-bounds 稳健性论证提供更稳妥的近期理论基础。
  - 〔DataCite 回读标题: Assessing Omitted Variable Bias when the Controls are Endogenous〕

### 五补-17. 信度与构念效度统计 (kappa, alpha, HTMT, P/R/F1)

> 净增 3 条(其中 2 条 2024–2026)。

- 【2024–2026】James, J. (2026). Counting on consensus: Selecting the right inter-annotator agreement metric for NLP annotation and evaluation. arXiv. https://doi.org/10.48550/arXiv.2603.06865
  - *锚定* — stage 21 三轨 (full/ctx/ss) × 三家 LLM 标注评估中 IAA 指标 (Cohen/Fleiss κ、Krippendorff α、AC1) 的选型——按任务类型、标签不平衡、缺失数据组织指标选择,并要求报告置信区间与分歧模式,直接支撑验证阶段一致性度量的方法论透明性。
  - 〔DataCite 回读标题: Counting on Consensus: Selecting the Right Inter-annotator Agreement Metric for NLP Annotation and Evaluation〕
- 【2024–2026】Camuffo, A., Gambardella, A., Kazemi, S., Malachowski, J., & Pandey, A. (2026). Variance-aware LLM annotation for strategy research: Sources, diagnostics, and a protocol for reliable measurement. arXiv. https://doi.org/10.48550/arXiv.2601.02370
  - *锚定* — stage 21 LLM 情感标注的可靠性协议——多次运行方差来源诊断、temperature=0 确定性、缓存可复现测量,直接对应本项目三家投票 + Prompt v8 字节冻结 + _llm_cache.db 确定性锚点的方法学正当性 (frontier 商管/策略研究语境)。
  - 〔DataCite 回读标题: Variance-Aware LLM Annotation for Strategy Research: Sources, Diagnostics, and a Protocol for Reliable Measurement〕
- Vach, W., & Gerke, O. (2023). Gwet's AC1 is not a substitute for Cohen's kappa – A comparison of basic properties. MethodsX, 10, Article 102212. https://doi.org/10.1016/j.mex.2023.102212
  - *锚定* — `stage 66/70 一致性指标` (construct-anchor)：银行金科判定（银行侧否定+短名过滤、金科侧裸 AC）类别极不平衡场景下的信度报告——当标签分布高度偏斜引发 kappa paradox 时,本文逐项比较 Gwet AC1 与 Cohen kappa 的基本性质,界定 AC1 何时可作 kappa 的旁证、何时会高估一致性,为 stage 66/70 评分者间一致性指标的选择与解读提供方法论参照。
  - 〔Crossref 回读标题: Gwet's AC1 is not a substitute for Cohen's kappa – A comparison of basic properties〕

### 五补-18. 多样性 / 集中度 / 均匀度指数 (Shannon, HHI, Gini, Pielou)

> 净增 6 条(其中 5 条 2024–2026)。

- 【2024–2026】Estève, L., de Marneffe, M.-C., Melnik, N., Savary, A., & Kanishcheva, O. (2025). A survey of diversity quantification in natural language processing: The why, what, where and how. arXiv. https://doi.org/10.48550/arXiv.2507.20858
  - *锚定* — NLP 文本多样性量化的指标选型正当性(Shannon entropy、Simpson/Gini-Simpson、Hill numbers/有效类别数在文本场景的取舍)。为我们在新闻语料构造议题/词汇多样性列时引用前沿综述,说明为何采用某一族 evenness/集中度指标。
  - 〔DataCite 回读标题: A survey of diversity quantification in natural language processing: The why, what, where and how〕
- 【2024–2026】Nguyen, D., & Ploeger, E. (2025). We need to measure data diversity in NLP — Better and broader. arXiv. https://doi.org/10.48550/arXiv.2505.20264
  - *锚定* — 语料层面的多样性度量必要性与方法批评——支撑我们对银行/金科新闻样本框(实体、来源、议题分布)做多样性/集中度刻画时,论证度量口径选择与潜在偏差,呼应 fintech 词频集中度与样本均衡性诊断。
  - 〔DataCite 回读标题: We Need to Measure Data Diversity in NLP -- Better and Broader〕
- 【2024–2026】Kaneko, K., & Kajikawa, Y. (2025). Relative technological diversification measure using patent data: Analysis of firms' strategies in the Fast Moving Consumer Goods (FMCG) sector. World Patent Information, 80, 102333. https://doi.org/10.1016/j.wpi.2024.102333
  - *锚定* — 对传统 Herfindahl/entropy 多样化指数仅刻画单主体绝对组合之局限的最新批评,并提出相对化改进。支撑本项目在构造银行层面金科多样化/集中度指标时,讨论绝对 vs 相对(对标基准)度量口径的稳健性。
  - 〔Crossref 回读标题: Relative technological diversification measure using patent data: Analysis of firms’ strategies in the Fast Moving Consumer Goods (FMCG) sector〕
- 【2024–2026】Shaib, C., Govindarajan, V. S., Barrow, J., Sun, J., Siu, A. F., Wallace, B. C., & Nenkova, A. (2024). Standardizing the measurement of text diversity: A tool and a comparative analysis of scores. arXiv. https://doi.org/10.48550/arXiv.2403.00553
  - *锚定* — 文本多样性度量的方法学规范——对压缩比、n-gram 自重复、Self-BLEU、BERTScore 等多样性分数做收敛效度比较。支撑我们在新闻文本(三轨 full/ctx/ss)上选择并交叉验证多样性/集中度指标,论证不同 evenness 类度量之间的相关性与可替代性。
  - 〔DataCite 回读标题: Standardizing the Measurement of Text Diversity: A Tool and a Comparative Analysis of Scores〕
- 【2024–2026】Hur, W. (2024). Entropy, heterogeneity, and their impact on technology progress. Journal of Informetrics, 18(2), Article 101506. https://doi.org/10.1016/j.joi.2024.101506
  - *锚定* — `HHI/Shannon 集中度测度` (recent-application): 熵与异质性测度应用于大规模专利数据的近期实证研究。为本项目把 HHI/Shannon 作为银行-金科议题集中度或金科强度分散度的应用度量提供平行同法参照,而非断言其具体的多测度并列结构、语料规模或相关性报告(此类细节无法仅凭题录核实)。
  - 〔Crossref 回读标题: Entropy, heterogeneity, and their impact on technology progress〕
- Färber, M., Schwade, J., & Jatowt, A. (2023). Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election. arXiv. https://doi.org/10.48550/arXiv.2308.03531
  - *锚定* — 本项目对银行/金科新闻媒体覆盖多样性与集中度的度量——把 Stirling 的 variety/balance/disparity 三分解(对应有效类别数、Shannon/Pielou evenness、disparity)直接落地到新闻语料,为我们在 outlet/topic 维度上构造多样性指标(如媒体来源 house-style 暴露、议题分散度)提供最新的文本侧应用范式。
  - 〔DataCite 回读标题: Measuring Variety, Balance, and Disparity: An Analysis of Media Coverage of the 2021 German Federal Election〕

### 五补-19. 文本算法原语 (Aho-Corasick, MinHash-LSH, SimHash, TF-IDF)

> 净增 4 条(其中 2 条 2024–2026)。

- 【2024–2026】Khan, A., Underwood, R., Siebenschuh, C., Babuji, Y., Ajith, A., Hippe, K., Gokdemir, O., Brace, A., Chard, K., & Foster, I. (2024). LSHBloom: Memory-efficient, extreme-scale document deduplication. arXiv. https://doi.org/10.48550/arXiv.2411.04257
  - *锚定* — 2024 前沿,把 MinHash+LSH 用 Bloom filter 替代签名存储以做亿级文档去重,直接论证本项目在真实全量 18,198,978 条新闻语料上跑 MinHash 近重复(surface_staleness)的可扩展性与内存可行性,是 MinHash-LSH 主测度的规模化方法学锚。
  - 〔DataCite 回读标题: LSHBloom: Memory-efficient, Extreme-scale Document Deduplication〕
- 【2024–2026】Penedo, G., Kydlíček, H., Ben Allal, L., Lozhkov, A., Mitchell, M., Raffel, C., Von Werra, L., & Wolf, T. (2024). The FineWeb datasets: Decanting the web for the finest text data at scale. arXiv. https://doi.org/10.48550/arXiv.2406.17557
  - *锚定* — 2024 前沿语料工程,公开给出 MinHash-LSH 去重的具体超参配方(5-gram、112 哈希分 14 桶、相似度阈值),是本项目 surface_staleness 的 MinHash shingle/hash 参数选型与近重复阈值设定的工程依据。
  - 〔DataCite 回读标题: The FineWeb Datasets: Decanting the Web for the Finest Text Data at Scale〕
- Zhang, M., Vallis, O., Bumin, A., Vakharia, T., & Bursztein, E. (2023). RETSim: Resilient and efficient text similarity. arXiv. https://doi.org/10.48550/arXiv.2311.17264
  - *锚定* — `surface_staleness`(MinHash 近重复去重, recent-application):RETSim 是噪声/对抗扰动下近重复检索的近期神经基线,为本项目 `surface_staleness`/`surface_highstale` 的 MinHash+LSH 表层陈旧度路线提供平行的方法学参照与取舍边界。在 18,198,978 级语料上任何神经推理管线都重于纯哈希 MinHash,呼应本项目选用轻量哈希近重复的工程取舍;此处仅作平行同法对照(RETSim 本身以高效为设计目标),不宜据此把神经法一概称为"重型"。
  - 〔DataCite 回读标题: RETSim: Resilient and Efficient Text Similarity〕
- Silcock, E., D'Amico-Wong, L., Yang, J., & Dell, M. (2022). Noise-robust de-duplication at scale (NBER Working Paper No. 30726). National Bureau of Economic Research. https://doi.org/10.3386/w30726
  - *锚定* — 经济学家(Dell 组)对历史新闻 wire 的近重复检测系统比较 LSH/n-gram 哈希与神经方法,是本项目 stage 26 surface_staleness/surface_highstale MinHash 近重复测度最贴合的经济学来源锚:它直接论证在大规模噪声新闻语料上用哈希(LSH)做近重复识别的合理性与边界。
  - 〔Crossref 回读标题: Noise-Robust De-Duplication at Scale〕

### 五补-20. 网络中心度 / 经纪角色 / 二分图投影 / 模块度

> 净增 7 条(其中 6 条 2024–2026)。

- 【2024–2026】Neal, Z. P. (2026). Backbone 3.0: An R package for extracting network backbones. PLOS ONE, 21(5), e0349258. https://doi.org/10.1371/journal.pone.0349258
  - *锚定* — bipartite/two-mode 投影后的 backbone 提取步骤。本项目把银行-金科词、银行-媒体来源等二模网络投影成银行-银行一模网络再算中心度; 该投影会产生大量噪声边, Neal 的 SDSM 统计显著性 backbone 提取是把投影网络稀疏化为可信边集的前沿工具 (2026, 最新版包)。
  - 〔Crossref 回读标题: Backbone 3.0: An R package for extracting network backbones〕
- 【2024–2026】Neal, Z. P., & Neal, J. W. (2024). Illustrating the importance of edge constraints in backbones of bipartite projections. PLOS ONE, 19(5), e0302973. https://doi.org/10.1371/journal.pone.0302973
  - *锚定* — 二模投影 backbone 的边约束 (SDSM-EC) 细节。当银行-金科共现矩阵存在结构性约束 (如某些银行从不与某类金科词共现) 时, 朴素 SDSM 会误判边显著性; 本文证明须用带边约束的随机度序列模型, 直接关系本项目 bipartite 投影中心度列的稳健构造。
  - 〔Crossref 回读标题: Illustrating the importance of edge constraints in backbones of bipartite projections〕
- 【2024–2026】Nezami, M., Chisam, N., & Palmatier, R. W. (2025). Network centrality and firm performance: A meta-analysis. Journal of the Academy of Marketing Science, 53(1), 79–104. https://doi.org/10.1007/s11747-024-01043-8
  - *锚定* — `bank_cfbetween_cent` (betweenness) / `bank_harmonic_cent` (closeness 变体) [construct-anchor / recent-application]: 一项覆盖 degree/closeness/betweenness/eigenvector 四类中心度与企业绩效关联的元分析, 为本项目把银行中介中心度 (betweenness) 与调和中心度 (closeness 变体) 作为面板自变量预测银行结果提供同法的近期经验参照, 并提示 eigenvector 中心度近年解释力相对增强。注: `bank_clustering` 是聚类系数 (局部网络传递性/凝聚度), 不属于该元分析考察的四类中心度构念, 故不纳入此条背书。
  - 〔Crossref 回读标题: Network centrality and firm performance: A meta-analysis〕
- 【2024–2026】Sadeghi, A., & Feinstein, Z. (2024). Statistical validation of contagion centrality in financial networks. arXiv. https://doi.org/10.48550/arXiv.2404.14337
  - *锚定* — `bank_cfbetween_cent` / `bank_harmonic_cent` (network-centrality, method-origin / 方法论类比)。本文为加权有向金融网络提出一种可统计验证的传染/影响中心度 (Katz-Bonacich 类), 并给出其显著性检验框架。该度量与本项目采用的 current-flow betweenness、harmonic 等经典图论中心度在构造上不同, 故仅作平行的方法论参照——为"金融网络中心度本身值得严格统计处理"提供一般性动因, 而非直接支持对 cfbetween/harmonic 的显著性判定。
  - 〔DataCite 回读标题: Statistical Validation of Contagion Centrality in Financial Networks〕
- 【2024–2026】Xu, Y., & Zhao, X. (2024). How does node centrality in a financial network affect asset price prediction? The North American Journal of Economics and Finance, 73, Article 102163. https://doi.org/10.1016/j.najef.2024.102163
  - *锚定* — `bank_clustering` / `bank_harmonic_cent` / `bank_cfbetween_cent` (construct-anchor / 方法论类比): 该文在金融网络的资产价格预测场景中考察节点中心度 (eigenvector/closeness 等) 作为预测因子的价值, 为"中心度并非天然越高越有信息量"提供一个平行的警示性参照。其具体方向性结论 (不同中心度因子的预测力对比) 限于股价/资产收益预测语境, 与本项目把中心度列用作银行-年面板回归解释变量并非同一识别设定; 故仅作中心度特征工程须谨慎甄别的方法论类比, 不直接外推为面板的因果指引。
  - 〔Crossref 回读标题: How does node centrality in a financial network affect asset price prediction?〕
- 【2024–2026】Yu, M., Hu, X., & Zhong, A. (2024). Network centrality, information diffusion and asset pricing. International Review of Financial Analysis, 93, 103223. https://doi.org/10.1016/j.irfa.2024.103223
  - *锚定* — 中心度-信息扩散-资产定价的传导机制。本项目核心是银行金科新闻情感经由网络扩散影响银行结果; 本文 (2024) 把网络中心度与信息扩散显式连到资产定价, 为本项目以银行中心度列调节新闻情感扩散强度的设定提供前沿实证机制锚点。
  - 〔Crossref 回读标题: Network centrality, information diffusion and asset pricing〕
- Zádor, Z., Zhu, Z., Smith, M., & Gorgoni, S. (2022). A weighted and normalized Gould–Fernandez brokerage measure. PLOS ONE, 17(9), e0274475. https://doi.org/10.1371/journal.pone.0274475
  - *锚定* — brokerage_network 论文的 Gould-Fernandez 经纪角色 (coordinator/gatekeeper/representative/consultant/liaison) 测度。本文把经典 GF 经纪指标扩展到加权、有向、完全图而不丢信息, 正是本项目银行-金科共现网络 (带权多模) 计算经纪位置所需的方法学正当性来源。
  - 〔Crossref 回读标题: A Weighted and Normalized Gould–Fernandez brokerage measure〕

### 五补-21. generated-regressor / 两步测度误差下的推断 (W&Z)

> 净增 3 条(其中 1 条 2024–2026)。

- 【2024–2026】Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for regression with variables generated by AI or machine learning. arXiv. https://doi.org/10.48550/arXiv.2402.15585
  - *锚定* — 最核心锚点: 直接论证当文本/ML 生成的变量(本项目 stage 21 三家 LLM 情感票、stage 23 BERT 情感、stage 25/26 嵌入测度)被当作下游面板/paper 回归的右手边解释变量时, 朴素两步法既有衡量误差偏误又有 generated-regressor 推断失效, 并给出偏误修正与联合 MLE 两套修法 — 正是 P1 用 llm_vote_tone_full 作 treatment 的二阶段推断合法性依据。
  - 〔DataCite 回读标题: Inference for Regression with Variables Generated by AI or Machine Learning〕
- Egami, N., Hinck, M., Stewart, B. M., & Wei, H. (2023). Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of large language models. arXiv. https://doi.org/10.48550/arXiv.2306.04746
  - *锚定* — seminal-recent: 证明即便 LLM 代理标注准确率高达 80–90%, 直接拿来做下游统计分析仍导致实质偏误与失效置信区间, 并给出 DSL 双稳健估计量(少量 gold-standard 标注 + 受控抽样)。直接锚定本项目用 stage 21 LLM 情感作为代理标注、再以 validation 阶段少量人工金标做合法下游推断的设计正当性。
  - 〔DataCite 回读标题: Using Imperfect Surrogates for Downstream Inference: Design-based Supervised Learning for Social Science Applications of Large Language Models〕
- Escanciano, J. C., & Pérez-Izquierdo, T. (2023). Automatic locally robust GMM with machine-learning-generated regressors. arXiv. https://doi.org/10.48550/arXiv.2301.10643
  - *锚定* — 本项目 IV/GMM 路线(pipeline/panel/iv_extensions.py 的 2SLS 列族与 Hansen J over-identified 检验): 当 ML 生成的回归元进入 GMM/IV 矩条件时, 标准 plug-in 与 Double ML 忽略生成回归元的条件效应导致严重偏误; 该文用正交化矩 + 交叉拟合 Riesz 表示器自动消除 generated-regressor 的间接效应, 为嵌入/BERT 测度进 2SLS 提供局部稳健推断依据。
  - 〔DataCite 回读标题: Automatic Locally Robust GMM with Machine-Learning-Generated Regressors〕

### 五补-22. 空间滞后 / 认知-地理邻近 (spatial econometrics)

> 净增 5 条(其中 5 条 2024–2026)。

- 【2024–2026】de Paula, A., Rasul, I., & Souza, P. C. L. (2024). Identifying network ties from panel data: Theory and an application to tax competition. The Review of Economic Studies, 92(4), 2691–2729. https://doi.org/10.1093/restud/rdae088
  - *锚定* — `stage 25/26 _full/_ctx/_ss 嵌入邻近矩阵` (method-origin)：顶刊计量方法论先例——证明同业/网络连边可从面板数据内生识别,而非外生假设地理邻接。注:de Paula 等以面板*结果变量*(辖区间税率财政溢出)的变异为识别杠杆,不涉及文本、NLP 嵌入或余弦相似度。本项目用嵌入语义相似度内生构造同业邻近矩阵是该「数据驱动识别权重矩阵」原则的平行同法应用,故本文为「W 矩阵可由数据内生设定而非先验地理给定」提供顶刊方法论先例,而非直接验证嵌入相似度构造法本身。
  - 〔Crossref 回读标题: Identifying Network Ties from Panel Data: Theory and an Application to Tax Competition〕
- 【2024–2026】Ahmad, M., Hall, S. G., Law, S. H., & Nayan, S. (2024). Spillover effects in the nexus of finance-institutions-growth: New insights from spatial Durbin analysis on emerging economies. International Journal of Finance & Economics, 30(3), 2470–2491. https://doi.org/10.1002/ijfe.3025
  - *锚定* — `leave_one_out_peer_*_iv` / SDM 稳健性轨 (recent-application)：该文用空间杜宾模型 (SDM) 把直接效应与溢出效应分解开来，是金融类空间计量的近年范例，为本项目"将同业溢出与本地效应相分离"的稳健性思路提供平行的同法近期参照。注：本项目面板 IV 扩展中的 leave_one_out_peer 同组均值是排除本行观测的外生工具变量构造，与 SDM 空间回归框架本质不同，故该文仅作间接方法论参照，并非对 LOO-IV 列设定的直接支撑；其具体空间权重矩阵 (邻接/距离倒数/k-NN) 设定需以原文正文为准，此处不作断言。
  - 〔Crossref 回读标题: Spillover effects in the nexus of finance‐institutions‐growth: New insights from spatial Durbin analysis on emerging economies〕
- 【2024–2026】Ahmad, M., & Law, S. H. (2024). Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities. International Journal of Finance & Economics, 29(3), 2699–2721. https://doi.org/10.1002/ijfe.2791
  - *锚定* — 为面板里地理邻近与制度/认知邻近两类空间权重并置提供金融领域的当代范例,直接支撑 IV 扩展 (leave_one_out_peer / Bartik) 与同业溢出测度对非地理邻近权重矩阵的使用,论证空间杜宾框架可同时容纳多维 proximity 通道。
  - 〔Crossref 回读标题: Financial development, institutions, and economic growth nexus: A spatial econometrics analysis using geographical and institutional proximities〕
- 【2024–2026】Koranteng, B., & You, K. (2024). Fintech and financial stability: Evidence from spatial analysis for 25 countries. Journal of International Financial Markets, Institutions and Money, 93, 102002. https://doi.org/10.1016/j.intfin.2024.102002
  - *锚定* — 银行/金科主题与空间溢出最直接对口的前沿文献:用空间模型证实金融稳定存在正向跨境空间依赖、fintech 融资有本地+邻近溢出。可锚定本项目 fintech_share / herd_decay 同业传染列与面板溢出口径,论证 fintech 信号存在空间外溢需用空间滞后/SDM 处理。
  - 〔Crossref 回读标题: Fintech and financial stability: Evidence from spatial analysis for 25 countries〕
- 【2024–2026】Giroud, X., Liu, E., & Mueller, H. M. (2024). Innovation spillovers across U.S. tech clusters (NBER Working Paper No. 32677). National Bureau of Economic Research. https://doi.org/10.3386/w32677
  - *锚定* — `strategic_diff` 嵌入距离 / 同业网络邻近 (recent-application)。前沿工作论文,研究美国科技集群之间的创新溢出格局,为"以网络/空间邻近性而非单一物理距离刻画溢出"这一框架提供近期同法参照。本项目以语义/同业网络邻近 (strategic_diff 嵌入距离、outlet house-style 暴露 IV) 补充地理邻近的做法与之呼应、互为方法论类比;论文标题未明确分离企业网络与物理距离孰主孰次,亦未直接给出"远距离簇专利引用更多"的具体实证发现,故此处仅作平行先例而非对该机制命题的直接支撑。
  - 〔Crossref 回读标题: Innovation Spillovers across U.S. Tech Clusters〕

### 五补-23. 主题模型 / niche distance / 战略差异 / 文本 fluidity

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Hoberg, G., & Phillips, G. M. (2025). Scope, scale, and concentration: The 21st-century firm. The Journal of Finance, 80(1), 415–466. https://doi.org/10.1111/jofi.13400
  - *锚定* — `strategic_diff` (construct-anchor): Hoberg-Phillips 谱系最新一篇 JoF 论文, 基于 10-K 文本的产品/经营范围与差异化测度, 为本项目嵌入式 firm-level 差异化与 niche distance 构造提供方法论先例。注: 该文分析的是 10-K 申报文本 (非新闻/媒体文本), 故对 stage 25/26 用报道文本嵌入构造差异化测度仅为平行的同法参照 (方法论类比), 而非直接背书; Hoberg-Phillips 经典口径用 10-K 产品描述的词重叠余弦相似, 本锚定不主张其使用 doc2vec 或 ETNIC。
  - 〔Crossref 回读标题: Scope, Scale, and Concentration: The 21<sup>st</sup>‐Century Firm〕
- 【2024–2026】Banker, R. D., Huang, R., Li, X., & Yan, Y. (2024). Strategy typology and cost structure: A textual analysis approach. Production and Operations Management, 33(6), 1285–1305. https://doi.org/10.1177/10591478241245144
  - *锚定* — strategic_diff 的 treatment 构造: 用 10-K 文本沿产品领导/客户亲密/运营卓越三维刻画企业战略定位差异化。为本项目从中文银行/金科报道文本提取企业战略差异化信号 (stage 16 policy_alignment / strategic_diff 维度投影) 提供方法学正当性。
  - 〔Crossref 回读标题: Strategy Typology and Cost Structure: A Textual Analysis Approach〕
- 【2024–2026】Cong, L. W., Liang, T., Zhang, X., & Zhu, W. (2024). Textual factors: A scalable, interpretable, and data-driven approach to analyzing unstructured information (NBER Working Paper No. 33168). National Bureau of Economic Research. https://doi.org/10.3386/w33168
  - *锚定* — 本项目从非结构化文本提取可解释 textual factors / 语义维度 (stage 15 fintech_intensity、维度分析) 的方法路线, 是 LDA 之后 scalable+interpretable 主题/因子方法的前沿替代, 支撑用嵌入而非词袋构造金科语义强度因子。
  - 〔Crossref 回读标题: Textual Factors: A Scalable, Interpretable, and Data-driven Approach to Analyzing Unstructured Information〕
- 【2024–2026】Ganguli, I., Lin, J., Meursault, V., & Reynolds, N. (2024). Patent text and long-run innovation dynamics: The critical role of model selection (NBER Working Paper No. 32934). National Bureau of Economic Research. https://doi.org/10.3386/w32934
  - *锚定* — 本项目的嵌入模型选择敏感性 (Qwen3-Embedding-8B 与 text-embedding-3-large co-primary 双轨、互为稳健性): 该文系统论证 text-based 创新/相似度测度结论强烈依赖嵌入模型选择, 为双轨 parity 设计与 manuscript 披露厂商维度副作用提供前沿方法学依据。
  - 〔Crossref 回读标题: Patent Text and Long-Run Innovation Dynamics: The Critical Role of Model Selection〕

### 五补-24. LLM 标注效度 / 校准 / 与人工一致性 / 测量可复现

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Haman, M. (2026). Can large language models replace human coders? Introducing ContentBench. arXiv. https://doi.org/10.48550/arXiv.2602.19467
  - *锚定* — 2026 最新基准 ContentBench，系统评测 LLM 能否在内容分析中替代人工编码员。锚定本项目用 LLM 替代人工编码做新闻情感/属性标注的整体合法性，可作为 stage 21 LLM-vs-human 效度对标的外部基准参照。
  - 〔DataCite 回读标题: Can Large Language Models Replace Human Coders? Introducing ContentBench〕
- 【2024–2026】Hartley, E. (2025). Narratives to numbers: Large language models and economic policy uncertainty. arXiv. https://doi.org/10.48550/arXiv.2511.17866
  - *锚定* — 最新 frontier：用 LLM 把新闻叙事转化为经济政策不确定性数值测度并与既有指数对照校准。与本项目“中文新闻文本→bank-year 面板数值列”的核心 text-as-data 转换高度同构，锚定 LLM 测度对外部基准的收敛效度验证。
  - 〔DataCite 回读标题: Narratives to Numbers: Large Language Models and Economic Policy Uncertainty〕
- 【2024–2026】Törnberg, P. (2024). Large language models outperform expert coders and supervised classifiers at annotating political social media messages. Social Science Computer Review, 43(6), 1181–1195. https://doi.org/10.1177/08944393241286471
  - *锚定* — `stage 21 tone_llms`（LLM 情感标注）·recent-application：实证发现 LLM 在标注短文本社媒消息上可超过专家编码员与监督式分类器。该证据以方法论类比/跨域参照方式呼应本项目用 LLM 三模型多数投票（gpt54nano/gemini31/deepseekv4）替代/增强人工编码、并相对词典法（stage 22）与 BERT（stage 23）的设计取向；但原文为英语政治社媒短文本，与本项目中文银行金科新闻在语言、领域、文本类型上均有实质差距，故仅作跨域佐证而非对中文金融新闻标注的直接实证。
  - 〔Crossref 回读标题: Large Language Models Outperform Expert Coders and Supervised Classifiers at Annotating Political Social Media Messages〕
- 【2024–2026】Gligorić, K., Zrnic, T., Lee, C., Candès, E. J., & Jurafsky, D. (2024). Can unconfident LLM annotations be used for confident conclusions? arXiv. https://doi.org/10.48550/arXiv.2408.15204
  - *锚定* — 用置信度驱动推断（prediction-powered inference 思路）把不确定的 LLM 标注与少量人工标注结合得到有效统计结论。锚定本项目把 LLM 情感列接入面板后做有效推断的方法论，与 Ludwig 等的验证样本框架互补，支撑 stage 40 面板估计的统计有效性。
  - 〔DataCite 回读标题: Can Unconfident LLM Annotations Be Used for Confident Conclusions?〕

### 五补-25. 中文金融/金科/银行文本测度 (Crossref/DataCite 可解析)

> 净增 3 条(其中 3 条 2024–2026)。

- 【2024–2026】Li, Y. (2026). The textual tone of annual reports and market attention: Evidence from Chinese listed companies. Managerial and Decision Economics, 46, e70100. https://doi.org/10.1002/mde.70100
  - *锚定* — P2 (attention) 关注度论文与 stage 21/22/23 文本语调→注意力面板列 (`attention_pct` / `news_salience`) 的链接 [recent-application]：该文以中文上市公司年报语调度量市场注意力，为本项目把文本语调映射到关注度提供近年同语种实证参照。注意其文本源为年报 (年报) 而非新闻报道，故属平行同法参照而非直接对应。
  - 〔Crossref 回读标题: The Textual Tone of Annual Reports and Market Attention: Evidence From Chinese Listed Companies〕
- 【2024–2026】Li, S., Wang, D., & Jiang, L. (2025). Can the MD&A tone of listed firms' annual reports predict their future performance? Empirical evidence based on machine learning text analysis. Asia-Pacific Journal of Financial Studies, 54(1), 54–81. https://doi.org/10.1111/ajfs.12500
  - *锚定* — `stage 21`/`stage 22` 情感语调测度 (recent-application)：该文以机器学习对 15,743 份中国 A 股年报 MD&A 语调建模，并检验其对未来财务绩效的预测能力。其同语种 tone→performance 设计与本项目 P1 (tone→funding_cost/绩效) 平行同法参照，为中文语调测度的预测效度提供前沿佐证（属预测关系，非因果识别）。
  - 〔Crossref 回读标题: Can the MD&A Tone of Listed Firms’ Annual Reports Predict Their Future Performance? Empirical Evidence Based on Machine Learning Text Analysis*〕
- 【2024–2026】Zhu, S., He, C., Liu, H., Dong, P., Zhao, H., Yan, Y., Jia, Y., Zan, H., & Peng, M. (2024). SILC-EFSA: Self-aware in-context learning correction for entity-level financial sentiment analysis. arXiv. https://doi.org/10.48550/arXiv.2412.19140
  - *锚定* — stage 13/14 实体共现硬过滤与实体上下文窗 (_ctx/_ss 三轨、银行∧金科同句共现) 的实体级情感判定：该文针对中英文金融文本提出实体级 (entity-level) 情感分析与 in-context 纠错，正面支撑本项目把情感判定锚定到目标银行实体窗口而非整篇 (full) 的方法设计。
  - 〔DataCite 回读标题: SILC-EFSA: Self-aware In-context Learning Correction for Entity-level Financial Sentiment Analysis〕

### 五补-26. 可复现计算研究 / 数据版本血缘 / provenance

> 净增 4 条(其中 4 条 2024–2026)。

- 【2024–2026】Brodeur, A., Mikola, D., Cook, N., Fiala, L., Brailey, T., Briggs, R., de Gendre, A., Dupraz, Y., Gabani, J., Gauriot, R., Haddad, J., Lima, G., Ankel-Peters, J., Dreber, A., Campbell, D., Kattan, L., Marino Fages, D., Mierisch, F., Sun, P., … Zhong, Y. (2026). Reproducibility and robustness of economics and political science research. Nature, 652(8108), 151–156. https://doi.org/10.1038/s41586-026-10251-x
  - *锚定* — `tests/integration/test_panel_reproducibility.py` 复现门 (列哈希对 golden_panel) + 「确定性/golden」铁律 [construct-anchor]。这篇 Nature 2026 大规模(110+ 篇)经济学/政治学计算可复现性与稳健性协作研究是一项诊断性实证研究,测量既有论文的可复现率,确立了「计算可复现」作为一线期刊质量标准的实证必要性,从而为本管线整体走确定性复现取向(stage 21 三轨 LLM 情感用 _llm_cache.db 做字节级可复现锚、PYTHONHASHSEED=0 + BLAS 线程钉 1)提供动机性与背景性依据。该文不处方具体的 LLM 缓存机制、哈希种子或 BLAS 线程固定等实现选择,这些技术取舍须另引技术文献支撑,故此处为必要性/背景的呼应而非对具体设计的直接正当化。
  - 〔Crossref 回读标题: Reproducibility and robustness of economics and political science research〕
- 【2024–2026】Brodeur, A., Sung, S. Y., Miguel, E., Vilhuber, L., & Hoces de la Guardia, F. (2025). Assessing reproducibility in economics using standardized crowd-sourced analysis (NBER Working Paper No. 33753). National Bureau of Economic Research. https://doi.org/10.3386/w33753
  - *锚定* — 本项目「研究者自由度/多设定稳健性」工程化——三轨 full/ctx/ss、co-primary 双轨嵌入(Qwen3 ⟂ text-embedding-3-large)、词典消融梯度(6 变体 × 6 词典 × 3 轨)本质上是把同一识别问题的多种合理分析路径并排物化。该 NBER 标准化众包分析正是量化「分析设定差异如何驱动结论漂移」的前沿证据,为本管线把稳健性内建进 DAG 而非事后补做提供依据。
  - 〔Crossref 回读标题: Assessing Reproducibility in Economics Using Standardized Crowd-sourced Analysis〕
- 【2024–2026】Fink, L., & Marcus, J. (2024). Replication code availability over time and across fields: Evidence from the German Socio-Economic Panel. Economic Inquiry, 63(2), 357–386. https://doi.org/10.1111/ecin.13267
  - *锚定* — `OUTPUT_REGISTRY` / `core/dag.py` / `data_versioning` (recent-application)：本项目的数据/版本溯源与依赖钉死实践——OUTPUT_REGISTRY(stage→parquet 单源血缘)、core/dag.py 声明式阶段注册、内容寻址血缘(data_versioning),以及冻结锚点 jieba==0.42.1 + Prompt v8 字节级冻结 + requirements.lock + PYTHONHASHSEED=0/BLAS 线程钉 1。Fink-Marcus 实证显示发表论文的复现代码"可得性"随时间与领域差异显著且普遍不足(即便提供代码亦未必完整可用),从侧面呼应本管线把可复现依赖(嵌入/LLM 模型 ID、prompt 版本、随机种子、BLAS 线程)显式版本化为一等公民。该文仅度量代码是否可得,未直接检验可得代码能否成功重跑结果,故此处仅作动机性平行参照。
  - 〔Crossref 回读标题: Replication code availability over time and across fields: Evidence from the German Socio‐Economic Panel〕
- 【2024–2026】Dreber, A., & Johannesson, M. (2024). A framework for evaluating reproducibility and replicability in economics. Economic Inquiry, 63(2), 338–356. https://doi.org/10.1111/ecin.13244
  - *锚定* — 本项目对「可复现 vs 稳健性 vs 可复制」三类概念的口径区分:test_panel_reproducibility 是 computational reproducibility(逐位字节),而稳健性 battery(bootstrap/rwolf/ritest/csdid wild bootstrap)与三轨/双轨并排属 robustness reproducibility。Dreber-Johannesson 的五类型框架为本管线在文档与审计中精确标注每个 gate 属于哪一类、避免概念混用提供权威分类依据。
  - 〔Crossref 回读标题: A framework for evaluating reproducibility and replicability in economics〕

---

## 二、核验记录(三道独立核验)

1. **FIND 自核验**: 每桶 FIND 智能体提名每条前, 实时 `GET api.crossref.org/works/{DOI}`(arXiv 走 `api.datacite.org`)读回标题自比对; 解析失败/标题不符当场弃。
2. **对抗审计**: 每候选交由独立审计员二次独立解析 + 逐字标题回比 + claim-fit 诚实性检验, 默认 REJECT。本批 confirm 148 / reject 4(4 条均 DOI 真实但 claim-fit 不符, 已剔除, 不入正文)。
3. **全语料本地核验**(决定性闸): `scripts/audit/audit_dois.py` 直连 Crossref/DataCite, 对全套 **507 个唯一 doi.org DOI**(前五份 396 + 本补编 111)逐条 DOI→标题逐字回比 + 年份核验。结果: **504 OK + 3 条 pre-existing benign**(① CNKI DOI 不进 Crossref; ② 老 ACL Anthology deposit `10.18653/v1/N19-1423` 的 Crossref 标题字段空缺但 DOI 真实可解析、doi.org 链接可达; ③ SSRN 工作论文张贴年差 1 年, 标题逐字相符) —— 三者均为前五份既有条目且 2026-06-24 审计已逐条裁决为 benign; **本补编新增 111 条 0 flag**(111/111 全部 resolved, 0 UNRESOLVED / 0 TITLE_MISMATCH / 0 YEAR_DIFF)。任何不能解析或解析到另一篇的 DOI 一律不入本文件。

> **新指标专项锚点**(v3.15.0 后): 嵌入轨 §五补-9 收录 Qwen3-Embedding(arXiv 2506.05176)、OpenAI 对比预训练嵌入(Neelakantan et al., arXiv 2201.10005, 锚 `_lg`=text-embedding-3-large 轨方法谱系)、MTEB(EACL 2023, 锚"多嵌入模型对比/选型")、NV-Embed/E5-mistral/BGE-M3/FinMTEB 等, 直接为 co-primary 双轨嵌入(canonical Qwen3 ⟂ `_lg` OpenAI)与"两轨互为稳健性"提供模型层与基准层出处。词典消融梯度见 §五补-2(否定/valence-shifter 规则分量), generalized Bartik/leave-one-out IV 见 §五补-12/14。

