---
family_id: F292
columns:
- fin_sent_zh_neg_sum_ctx
- fin_sent_zh_neg_sum_full
- fin_sent_zh_neg_sum_ss
- finbert2_neg_sum_ctx
- finbert2_neg_sum_full
- finbert2_neg_sum_ss
- finbert_cn_neg_sum_ctx
- finbert_cn_neg_sum_full
- finbert_cn_neg_sum_ss
unit: 无量纲概率和 (银行-年内文章级负面概率求和; 非比率, 未除以篇数)
formula: bank-year 内, 该 BERT 模型对每篇文章输出的负面标签 softmax 概率 P(neg) 在指定文本轨 (full/ctx/ss) 上逐篇求和, Σ_i P(neg)_i, i 遍历该 bank-year 下留篇 (llm_verified_full=True) 的文章
producer: pipeline\sentiment\tone_berts.py (stage 23, 文章级 {model}_负面 概率列生成); pipeline\panel\codebook.py (`_BERT_MODEL_RE` 归类 + `_BERT_MODEL_NOTE` 文案) 与 pipeline\panel\encode.py (panel 层 per-model 聚合 `agg[f'{short}_neg_sum{track}'] = (f'{short}_负面{track}', 'sum')`, 第800-804行一带); 注意 pipeline\panel\bert_distribution.py 是独立叶模块, 只产 entropy/xneg_frac/skew/xmodel/iyvol 五族分布形状列, 不参与本家族 neg_sum 聚合
upstream:
- 22_words_tone.parquet (标题 / 内容 / content_ctx / content_ss 文本来源)
- 23_bert_tone.parquet ({model}_负面 概率列, 三轨)
- 21_tone_llms.parquet (llm_verified_full 留篇门控)
- 40_panel_yearly.parquet (bank-year 聚合层)
citations:
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)
  pages_or_artno: 5117-5128
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.18653/v1/N19-1423
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019)
  pages_or_artno: 4171-4186
- doi: 10.24963/ijcai.2020/622
  type: journal
  authors: Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J.
  year: 2020
  title: "FinBERT: A pre-trained financial language representation model for financial text mining"
  venue: Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20)
  pages_or_artno: 4513-4519
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: "10.1287/mnsc.2022.00261"
  type: "journal"
  authors: "Chen, L., & Mankad, S."
  year: 2025
  title: "A Structural Topic and Sentiment-Discourse Model for Text Analysis"
  venue: "Management Science"
  vol: "71"
  issue: "7"
  pages_or_artno: "5767-5787"
- doi: "10.1007/s42521-024-00107-2"
  type: "journal"
  authors: "Groß-Klußmann, A."
  year: 2024
  title: "Learning deep news sentiment representations for macro-finance"
  venue: "Digital Finance"
  vol: "6"
  issue: "3"
  pages_or_artno: "341-377"
- doi: "10.3982/qe1825"
  type: "journal"
  authors: "Ke, S., Montiel Olea, J. L., & Nesbit, J."
  year: 2024
  title: "Robust machine learning algorithms for text analysis"
  venue: "Quantitative Economics"
  vol: "15"
  issue: "4"
  pages_or_artno: "939-970"
- doi: "10.1016/j.pacfin.2025.102721"
  type: "journal"
  authors: "Wang, Y., Xiao, J., Wang, L., & Wang, D."
  year: 2025
  title: "News sentiment and the cost of debt"
  venue: "Pacific-Basin Finance Journal"
  vol: "91"
  pages_or_artno: "102721"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画三个中文金融领域 BERT 分类器 (finbert_cn / fin_sent_zh / finbert2) 各自在 bank-year 层面产出的"负面概率总量"——即该模型判给每篇文章的负面 softmax 概率, 在同一 bank-year、同一文本轨内逐篇累加所得的和 (sum, 非均值)。这是 stage 23 (`tone_berts.py`) 神经网络情感路线在面板层的三个 per-model 强度型 (level, extensive-margin 敏感) 汇总量之一。与常见的 `neg` (负面概率均值) 或 `net_tone` (正负概率差) 不同, `neg_sum` 携带的是"总暴露量"信息: 同样的均值水平下, 报道篇数越多、负面概率越极端的银行-年份, `neg_sum` 越大; 因此它天然把"报道强度 (attention)"与"负面程度 (tone)"两个维度耦合在一个数字里, 使用时须留意与单纯语调测度 (均值型) 的构念差异——`neg_sum` 更接近"负面信息流总量"而非"负面情绪浓度"。

三个模型彼此独立训练、独立推理, 项目文档 (`codebook.py::_BERT_MODEL_NOTE`) 明确将其定位为"co-equal 互为稳健性、不分主次"的三条并行测度轨, 而非一个 canonical 加两个补充: finbert_cn (yiyanghkust/finbert-tone-chinese, 基于中文语料微调的 3-class 中性/正面/负面模型) 与 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 中文迁移微调的 3-class 模型) 是公开 HuggingFace 模型, 而 finbert2 是项目私有微调、经 `.env::FINBERT2_MODEL_DIR` 解析的 2-class (负面/正面, 无中性类) 模型——当该环境变量未配置或路径不存在时, finbert2 一族列会优雅整体缺席 (per-model 独立降级), 但两个 HF 公开模型照常产出, 不因此拖累整个家族。这种"三选一失败不传染"的设计是本家族与 co-primary 嵌入双轨 (both-or-neither) 铁律的关键区别: BERT 三模型是"各自可独立退化"的稳健性并排, 不是"任一缺席则全族置 NaN"的联动关系。

BERT 路线与 stage 21 的大模型 (LLM) 投票路线、stage 22 的词典法路线, 三者共同构成项目"情感三角验证"体系的第三条独立轨——LLM 靠上下文推理判断语调, 词典法靠关键词计数, BERT 靠端到端神经网络对整段文本的语义表征分类, 三条路线互不依赖、互相印证, 只有当三条路线结论一致时结果才被认为足够稳健可以支撑顶刊投稿的稳健性叙事。BERT 相对词典法的优势在于能捕捉否定、转折等语言学结构而不依赖硬编码规则; 相对 LLM 路线的优势在于零边际推理成本 (本地 GPU 批量推理, 无 API 调用) 且确定性更强 (argmax 分类 + 固定权重, 不受采样温度影响)。

【方法学与计算】
文章级来源: stage 23 (`23_tone_berts.py` 调用 `pipeline/sentiment/tone_berts.py`) 读取 stage 22 输出, 用 `prepend_title` 把标题与三种正文范围拼接成 full (标题+全文正文) / ctx (标题+银行实体窗口正文) / ss (标题+银行∧金科同句±N窗正文) 三份文本, 对每个模型各自独立分词 (fix g-berts-01 后不同词表模型不共享同一次批量分词, 避免 token id 跨词表错配) 并批量推理。超过模型单窗上限 (512 token 含特殊符, 有效正文 ≤510) 的文本用 50% 重叠滑动窗口切片, 各窗输出按 softmax 前 logits 的置信度加权池化 (`logits *= Σ(conf_k · logits_k) / Σconf_k`) 合并为该篇文章、该轨、该模型的一组分类概率, 其中负面标签对应的概率即本家族逐篇求和的基础量; 批级异常先降级为逐篇重试一次, 仍失败才写失败哨兵 (概率 NaN, 与空文本 0 窗口严格区分, 不会被误当作 0 概率计入求和)。

面板层聚合: `pipeline/panel/codebook.py` 用 `_BERT_MODEL_RE` 正则识别形如 `{model}_neg_sum(_full|_ctx|_ss)?` 的列名, 归入 `_BERT_MODEL_NOTE` 描述的 per-model 稳健性族; 实际数值聚合发生在面板构建阶段, 对每个 bank-year 内、按 `llm_verified_full == True` (即 stage 21 large-model 三家投票认定"确系一篇银行金科报道") 留篇的文章集合, 在指定轨上把该模型输出的负面概率逐篇相加得到 `neg_sum`。这一"留篇口径 = full-only"是 2026-06-29 起全项目情感测度的统一门控: 是否把一篇文章计入某个 bank-year 分析样本, 只由该文章在 full 轨的 LLM 判定决定, ctx/ss 轨的行宇宙是 full 留篇集的子集, 各轨照旧独立算自己的分子分母, 不因为某轨判定不同而单独增删行。

三个文本轨 (full/ctx/ss) 的语义差异: full = 标题 + 文章全文正文, 信息量最全但可能引入与目标银行无关的段落噪声; ctx = 标题 + 围绕目标银行实体的上下文窗口正文, 聚焦银行相关段落; ss = 标题 + 目标银行与金科关键词同句 (或 config 设定的 ±N 句半径) 共现窗口正文, 判据最严格。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 退化为全文正文 (等同 full), 并置位 `ss_is_fallback=True`, 该"回退作为分母一部分"的处理与 ctx 轨完全对称, 保证三轨分母口径一致可比。三个轨道各自 just-identified 并排, 互为稳健性、不分主次, 严禁将三轨列混入同一个 over-identified Hansen J 检验方程——这是本项目所有三轨测度 (含情感/嵌入/结构指标) 共享的铁律, 目的是防止研究者把本应独立的稳健性检验人为拼装成单一过度识别方程从而制造虚假的过度识别检验通过率。

三模型间的差异同理: finbert_cn/fin_sent_zh/finbert2 各自独立训练、各自的负面概率量纲和分类边界不必然可比 (finbert2 是 2-class 无中性类, 另两个是 3-class), 因此跨模型比较应优先用标准化后的统计量 (如 z-score), 而非直接比较原始 `neg_sum` 水平; 三模型同样各自 just-identified 并排、禁止混入同一 over-identified Hansen J, 只用于证明"负面语调结论不被任一单一模型的训练数据/架构选择所驱动"这一稳健性主张。

【文献定位】
BERT 类金融文本情感分类器的方法学谱系可追溯至 Devlin et al. (2019) 提出的双向 Transformer 预训练框架, 该框架奠定了通过掩码语言建模预训练再针对下游任务微调的范式, 是本家族三模型架构的共同技术祖先。在金融领域的专门化方面, Huang, Wang & Yang (2023, Contemporary Accounting Research) 的 FinBERT 证明了针对金融文本语料微调的 BERT 变体在抽取财务文本信息任务上显著优于通用领域模型, 为本项目采用领域专门化 BERT (finbert_cn/fin_sent_zh) 而非通用中文 BERT 提供了直接的方法学依据; finbert2 (Xu et al. 2025, KDD '25) 进一步针对金融部署场景做双向编码器的专门化改进, 是本项目本地私有微调模型选型的技术参照。多模型三角验证的必要性在方法学上呼应 Denzin (2017) 的方法论三角验证 (methodological triangulation) 传统——单一模型的分类误差或系统性偏差不应被误认为是构念本身的属性, 只有当独立训练的多个模型对同一构念给出方向一致的结论时, 该结论才具有超越单一模型工件的稳健性; 这一逻辑也是本项目将 LLM 三家投票路线与 BERT 三模型路线并列为"情感测量三角"的理论支点。BERT 分类模型相较词典法在情感判定质量上的优势, 另有 Frankel, Jennings & Lee (2022, Management Science) 的直接顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型在识别语义层面的情感信号上显著优于关键词计数式词典法, 为本项目以 BERT 深层模型 (而非词典) 承担情感分类主力提供了顶刊层级的方法学背书。 就本家族取概率和而非硬标签计数这一口径, 近期前沿提供了两条互补的弱支撑。Chen 与 Mankad (2025) 提出 STS 主题模型, 引入可被文档级协变量解释的连续情感-话语潜变量, 使文本情感得以进入正式的统计推断而非仅作描述性摘要; 本家族据此仅取一点: 以篇级连续情感量而非 argmax 硬标签作为文本测度的基本单位, 在前沿是被接受的做法, 支撑本族保留篇级概率再入面板。迁移边界在于原文的情感量是贝叶斯生成模型的连续后验潜变量, 与 BERT softmax 类别概率的校准含义不同, 语料为评论/话语文本而非中文银行新闻, 且原文的用法是潜变量对协变量回归, 并无篇级量在单元内求和的聚合步骤。Groß-Klußmann (2024) 以监督式自编码器对跨主题的新闻情感时间序列抽取低维潜在经济因子, 并在 GDP nowcasting、资产类别收益面板解释与时序动量三个应用上证明其优于 PCA/PLS 等线性降维, 同样表明以连续取值的情感信号进入宏观金融实证是常规做法; 但原文的神经模型作用于已聚合的情感时间序列做降维, 并不产出篇级情感, 亦不存在篇级信号在单元内求和的步骤, 其"表征"是压缩后的潜因子而非三分类 softmax 概率, 层级为英文新闻的宏观时序而非中文银行-年面板, 无 per-model 独立分母与三轨切分。Ke 与 Nesbit (2024) 证明 LDA 参数不可识别、文本派生量的下游结论会随先验设定改变, 并给出刻画该结论取值区间的算法; 本家族仅取其一般性方法论立场 —— 建模者未被数据识别的选择应被显式化并报告结论在其上的取值范围, 对应三个 BERT 的 neg_sum 各自 just-identified 并排、互为稳健性不分主次、严禁混入同一 over-identified Hansen J 的设计; 原文针对的是单一 LDA 内的先验敏感性而非不同分类器之间的模型选择, 未评估任何 BERT 或神经情感分类器, 亦不涉及概率和口径与中文语料。在应用语境一侧, Wang、Xiao、Wang 与 Wang (2025) 在中国语境下从新闻报道抽取情感并聚合到企业层面用于债务成本实证, 是"中文新闻情感 → 实体-年测度"应用同域的近期实例, 用以锚定本家族概率和列族的应用语境而非其具体算法; 其实体为一般上市公司、DV 为债务成本, 未区分 count 与 probability-sum 两种口径, 无三模型 per-model 子测度, 亦无三轨文本范围。
## VAR: fin_sent_zh_neg_sum_ctx

【变体差分】
本列取模型 fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 中文迁移微调的 3-class 公开 HuggingFace 模型), 文本轨为 ctx (标题 + 银行实体上下文窗口正文, 由 stage 14 `content_ctx` 物化)。分子为该 bank-year 内、`llm_verified_full == True` 留篇集合中每篇文章在 ctx 轨上 fin_sent_zh 输出的负面 softmax 概率之和; 若某篇文章 ctx 轨判定失败 (哨兵), 该篇不计入求和而非计为 0。ctx 轨相较 full 轨聚焦银行相关段落, 剔除全文中与目标银行无关的噪声内容, 与 full/ss 两轨互为稳健性并排, 不分主次, 禁止与其它轨混入同一 over-identified Hansen J 方程; 与同模型 full/ss 轨的差异纯粹在于喂入模型的正文范围不同, 模型权重、分词方式、窗口池化算法完全一致。

使用建议: 若研究问题关心"报道聚焦到银行本身时的负面强度", ctx 轨比 full 轨更贴近构念, 因为它剔除了同一篇报道里可能涉及的其它银行、宏观政策等无关段落; 但 ctx 窗口裁剪本身依赖实体识别的准确率, 窗口边界误差会给该列引入额外测量噪声, 这是使用 ctx 轨须承担的代价。与 fin_sent_zh_neg_sum_full/ss 联合使用时, 三者数值一般正相关但不完全一致, 差异幅度本身即可作为"文本范围选择是否影响结论"的诊断信号: 若三轨系数方向和显著性高度一致, 则该银行-年份的负面语调结论对文本范围选择稳健; 若出现明显分歧, 应在稳健性附录中如实报告并讨论可能原因 (如报道正文大段涉及行业整体而非目标银行本身)。

## VAR: fin_sent_zh_neg_sum_full

【变体差分】
本列取模型 fin_sent_zh, 文本轨为 full (标题 + 文章全文正文, 未做实体窗口裁剪)。这是三轨中信息量最完整、也是留篇门控 (2026-06-29 起 full-only) 直接依据的轨道: 一篇文章是否被认定为"该银行-年份的一篇有效银行金科报道"只看其 full 轨的 LLM 判定, ctx/ss 两轨的行宇宙都是该 full 留篇集的子集。因此 `fin_sent_zh_neg_sum_full` 在三轨中覆盖的潜在信息范围最广, 但也可能因全文包含与银行无直接关系的段落而引入语调噪声; 与 ctx/ss 轨互为稳健性并排, 用于交叉验证负面语调结论是否对"要不要限定到银行相关段落"这一构造选择敏感。

full 轨还承担一个特殊角色: 它是 stage 21 LLM 三家投票据以判定"是否为一篇银行金科报道" (`llm_verified_full`) 的同一份文本, 因此 `fin_sent_zh_neg_sum_full` 的样本行宇宙与该 bank-year 的 `n_articles` 分母定义天然对齐, 不存在"分子分母来自不同文本口径"的错配风险。相较之下 ctx/ss 轨虽共享同一留篇集合, 但各自在该子集内独立推理, 若某篇文章在 ctx 或 ss 轨恰好触发窗口切分异常导致哨兵, 会造成该篇在不同轨的有效计入状态不完全相同——这也是三轨须各自独立报告分母而不能互相借用的原因之一。使用时若只能展示一条 headline 结果, 项目惯例是优先展示 full 轨 (与留篇门控一致), 再把 ctx/ss 作为附录稳健性; 但这属于呈现顺序上的惯例, 不构成 full 轨在统计意义上优于另外两轨的主张。

## VAR: fin_sent_zh_neg_sum_ss

【变体差分】
本列取模型 fin_sent_zh, 文本轨为 ss (标题 + 目标银行与金科关键词同句、或按 `config/filtering.yaml::context_window.ss_sentence_radius` 设定的 ±N 句半径窗口正文, 由 stage 14 物化 `content_ss`)。ss 判据是三轨中最严格的, 只保留银行与金科话题真正同句共现的段落; 当某篇文章不存在这种同句共现时, `content_ss` 按 ctx 镜像的回退语义退化为全文正文, 并置位 `ss_is_fallback=True` 共享 `n_articles` 分母, 保证退化篇不会被静默剔出样本、也不会人为压低分母。ss 轨与 full/ctx 轨互为稳健性并排, 不分主次, 禁止混入同一 over-identified Hansen J; 三轨差异仅在喂入文本范围, 模型与算法链路与另两轨完全一致。

ss 轨的特殊之处在于其判据 (银行与金科关键词是否同句共现) 与 stage 13 共现硬过滤所用的判据原语不同: stage 13 用 `has_bank_fintech_cooccurrence_within_radius` 做±1句窗口的行级硬过滤 (决定文章是否进入下游 pipeline), 而 stage 14 物化 `content_ss` 用的是更严格的严格同句判据 (`extract_bank_fintech_cooccurrence`), 两者刻意不复用同一函数、口径不完全等价。这意味着 `fin_sent_zh_neg_sum_ss` 的分母 (该轨判定为非回退的篇数) 可能显著小于 full/ctx 轨, 是三轨中样本最"精炼"但也最容易受稀疏样本影响的一支; 在 T=2 的开发环境下 ss 轨甚至可能对若干 bank-year 出现零方差或全 NaN 的退化, 这属于开发环境样本量不足的预期现象, 生产语料 (T=19) 上应恢复正常变异。研究者若发现 `fin_sent_zh_neg_sum_ss` 与同模型 full/ctx 轨的差距在 T=2 上异常大, 应先确认是否属于上述样本量不足的退化, 而非直接推断为"同句共现口径下负面语调显著不同"这类实质性结论, 生产语料重新播种后应重新核验该判读是否依然成立。

## VAR: finbert2_neg_sum_ctx

【变体差分】
本列取模型 finbert2 (项目私有微调、经 `.env::FINBERT2_MODEL_DIR` 本地解析的 2-class 负面/正面模型, 无中性类), 文本轨为 ctx。finbert2 与另两个公开 HF 模型的关键差异是: 其权重非公开可复现下载, 而是项目自有训练产物, 且分类边界只有正负二元、不含中性, 因此 `finbert2_neg_sum_ctx` 与 `finbert_cn`/`fin_sent_zh` 的 `neg_sum` 原始水平不必然可比 (二分类模型天然把中性文本的概率质量摊到正负两端, 可能系统性推高负面概率), 跨模型比较应优先用标准化统计量。当 `FINBERT2_MODEL_DIR` 未配置或路径失效时, 本列及同模型全部列整族优雅缺席 (per-model 独立降级), 不影响 finbert_cn/fin_sent_zh 两族照常产出; ctx 轨与该模型 full/ss 轨互为稳健性并排。

finbert2 是本项目自行在中文金融新闻语料上微调的模型, 相比 finbert_cn/fin_sent_zh 两个通用金融 BERT, 其训练语料与本项目下游任务 (银行金科新闻) 的领域匹配度理论上更高, 但也因此不具备外部同行独立复现的公开权重可比性——这是把它与另两个公开模型并列为"互为稳健性、不分主次"而非"以其为 canonical" 的关键原因: 领域匹配度高不等于测量偏差更低, 反而可能因训练集选择带入项目特有的标注偏好。使用本列时若发现其与 finbert_cn/fin_sent_zh 的 ctx 轨结果系统性偏离, 不应默认以 finbert2 为准, 而应把偏离本身作为需要在稳健性讨论中说明的现象。finbert2_neg_sum_full 的分类边界只有正/负二元, 若用于跟 finbert_cn/fin_sent_zh 的 3-class 结果做定量对齐, 建议先把三者分别标准化 (z-score) 再比较系数方向与显著性, 而不是直接比较原始 `neg_sum` 数值水平, 这一处理惯例适用于本家族全部跨模型比较场景。

## VAR: finbert2_neg_sum_full

【变体差分】
本列取模型 finbert2, 文本轨为 full。作为三个 BERT 模型中唯一的本地私有 2-class 模型, finbert2 的负面概率是"1 − 正面概率" (二分类互补, 无独立中性通道), 这与 finbert_cn/fin_sent_zh 的 3-class softmax 输出在数学结构上不同, 用户如需跨模型比较负面强度应留意这一构念差异。full 轨覆盖信息最全, 是留篇门控依据轨; finbert2 一旦因本地模型目录缺失而整族缺席, 该缺席与 full/ctx/ss 三轨联动 (同模型三轨同缺同有), 而非与另外两个 HF 模型的存在与否挂钩。

值得强调的是本地模型依赖不会传染到词典法 (stage 22) 或 LLM 投票路线 (stage 21) ——`finbert2_neg_sum_full` 缺席只影响 BERT 三角验证内部的三分之一份量, 不影响项目"三条独立路线互相印证"的整体设计, 情感三角验证在 finbert2 缺席时退化为"LLM + 词典 + 两个公开 BERT"仍可正常运作、只是 BERT 内部的稳健性网格从 3×3 收窄为 2×3。审计脚本 `verify_stage21_cache_coverage` 等确定性锚点与本列无关 (finbert2 是本地纯推理, 无 LLM 缓存穿透逻辑), 但重跑 stage 23 前须设置 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1` 环境变量以让另两个 HF 模型走本地缓存, 该设置对 finbert2 无影响 (本身即本地模型)。full 轨作为留篇门控依据轨, 其在本模型内部与 ctx/ss 轨的关系跟另外两个 HF 模型的 full 轨完全对称——三个模型各自的 full 轨都共享同一份留篇集合 (由 stage 21 LLM 三家投票决定), 但各模型对同一批文章给出的负面概率是独立推理结果, 不存在模型间共享中间量的情况。

## VAR: finbert2_neg_sum_ss

【变体差分】
本列取模型 finbert2, 文本轨为 ss (银行∧金科同句共现窗口, 无共现回退为全文并标记 `ss_is_fallback=True`)。这是 finbert2 一族中判据最严格的轨道, 与该模型 full/ctx 轨互为稳健性并排、不分主次, 三者共同验证 finbert2 给出的负面语调结论是否对文本范围选择敏感; 同时与 finbert_cn/fin_sent_zh 的对应 ss 轨列构成跨模型稳健性并排, 共同证明结论不被单一模型的架构/训练语料驱动。若 `FINBERT2_MODEL_DIR` 未配置, 本列随 finbert2 全族一并优雅缺席。

由于 ss 判据本身对样本量敏感 (只保留严格同句共现的段落), finbert2_neg_sum_ss 在小样本 bank-year 上比 finbert2_neg_sum_full/ctx 更容易出现分母极小甚至为零的情形; 项目口径规定分母为零时相关派生比率置 NaN, 但 `neg_sum` 本身作为求和量, 分母为零 (即该 bank-year 该轨无留篇文章) 时也应理解为 0 或缺失而非人为填充。研究者在做跨 bank-year 面板回归时若使用 ss 轨列, 应额外检查该轨的有效样本覆盖率是否显著低于 full/ctx 轨, 避免把"样本稀疏导致的高方差"误读为"负面语调真实存在剧烈波动"。finbert2_neg_sum_ss 与 finbert_cn_neg_sum_ss / fin_sent_zh_neg_sum_ss 三者共同构成 ss 判据下的跨模型稳健性三元组, 其中只有 finbert2 一支可能因本地模型目录未配置而整体缺席, 使用者在做三模型联合展示时应显式核对该列的非缺失覆盖率, 而非默认三列样本量恒等。

## VAR: finbert_cn_neg_sum_ctx

【变体差分】
本列取模型 finbert_cn (yiyanghkust/finbert-tone-chinese, 公开 HuggingFace 3-class 中性/正面/负面模型), 文本轨为 ctx。finbert_cn 是三模型中最早、也是社区引用最广的中文金融 BERT 之一, 其分类体系与 fin_sent_zh 同为 3-class (含独立中性通道), 两者的 `neg_sum` 在量纲结构上比 finbert2 更接近可比。ctx 轨聚焦银行实体上下文, 与该模型 full/ss 轨互为稳健性并排; `strict_models=true` 默认配置下, finbert_cn 若加载失败 (非预期), 会 fail-loud 而非静默跳过, 与 finbert2 的"预期内优雅降级"在失败语义上不同——finbert_cn/fin_sent_zh 两个 HF 模型的缺失通常意味着环境/网络异常而非项目预期的可选依赖缺失。

finbert_cn (yiyanghkust/finbert-tone-chinese) 在中文金融文本情感分类任务上有相对成熟的社区验证历史, 是三模型中方法学谱系最贴近 Devlin et al. (2019) 原始 BERT 预训练-微调范式的一支, 也是 Huang, Wang & Yang (2023) FinBERT 方法论在中文语境下的延伸应用之一。使用 `finbert_cn_neg_sum_ctx` 时应注意其训练语料主要面向英文金融文本迁移而来的中文适配, 与 fin_sent_zh (专门基于中文 Financial PhraseBank 微调) 在语料底色上并不完全相同, 这也是把两者并列为独立稳健性轨而非互为同一模型不同版本的原因。ctx 轨在 finbert_cn 上的行为与在 fin_sent_zh/finbert2 上的行为一致——同一份 `content_ctx` 文本喂入三个不同模型独立推理, 窗口切分与置信度加权池化算法在三模型间共用同一套实现, 差异只体现在各自模型权重给出的负面概率数值上, 便于把 ctx 轨结果按模型分组直接比较模型间的判定分歧程度。

## VAR: finbert_cn_neg_sum_full

【变体差分】
本列取模型 finbert_cn, 文本轨为 full。作为留篇门控依据轨, `finbert_cn_neg_sum_full` 覆盖该 bank-year 留篇集在全文范围上的负面概率总量, 是三模型 full 轨 `neg_sum` 家族 (与 fin_sent_zh_neg_sum_full / finbert2_neg_sum_full 并列) 中最常被用作首要展示口径的一支, 但项目文档明确三模型 co-equal、无 ensemble headline, 不存在"以 finbert_cn 为主"的隐含排序; 与本模型 ctx/ss 轨互为稳健性并排。finbert_cn_neg_sum_full 的分母 (留篇文章数) 与 fin_sent_zh_neg_sum_full / finbert2_neg_sum_full 三者理论上应完全一致 (同一份 `llm_verified_full` 留篇集合), 若三者分母不一致 (排除 finbert2 因本地模型目录缺失整族缺席的情形), 通常提示某一模型在个别文章上触发了推理失败哨兵, 该篇会从对应模型的求和中剔除, 值得在数据质量核查时留意。作为社区历史最悠久的中文金融 BERT 之一, finbert_cn_neg_sum_full 常被研究者用作"最保守/最少争议"的对照, 但项目层面并未赋予其任何优先级, 三个模型的 full 轨列在正文引用中应平等展示, 差异化叙事只应出现在结果确实分歧时的补充讨论中, 而非默认结构。

由于 finbert_cn 加载失败时项目默认 `strict_models=true` 会 fail-loud (raise 而非静默跳过), 若 `finbert_cn_neg_sum_full` 在某次生产运行中大面积缺席, 应首先排查环境/网络问题 (如 HF Hub 连通性、`HF_HUB_OFFLINE` 配置是否与本地缓存实际存在情况冲突) 而非默认这是可选依赖的预期降级——这与 finbert2 缺席时"预期内正常"的判读逻辑相反, 混淆二者会导致把真实的环境故障误判为无害的可选依赖跳过, 从而在生产播种阶段掩盖数据缺口。

## VAR: finbert_cn_neg_sum_ss

【变体差分】
本列取模型 finbert_cn, 文本轨为 ss。判据最严格 (银行∧金科同句共现, 无共现回退全文并标记 `ss_is_fallback=True`), 与该模型 full/ctx 轨互为稳健性并排, 亦与 fin_sent_zh_neg_sum_ss / finbert2_neg_sum_ss 构成跨模型 ss 轨稳健性并排。三模型三轨共九列 (本家族全部列) 应被理解为一个 3×3 的稳健性网格, 网格内任两列都不应被拼装进同一个 over-identified 识别方程, 只用于逐格交叉验证"负面语调-总量"这一构念是否对模型选型与文本范围选择两个维度同时稳健。

finbert_cn_neg_sum_ss 与 fin_sent_zh_neg_sum_ss 同为 3-class 模型的 ss 轨列, 二者在分类边界结构上比与 finbert2_neg_sum_ss (2-class) 的比较更具可比性, 若要报告"BERT 三角验证在最严格判据下依然一致"这类稳健性主张, 建议同时展示三列而非只选其中之一, 因为三者的方差结构与样本敏感度并不完全相同——finbert_cn 与 fin_sent_zh 的中性通道会分流部分概率质量, 而 finbert2 没有中性通道, 单独展示某一列容易让读者误以为该结果代表"BERT 方法"的统一定论, 而实际上它只是九宫格中的一格。finbert_cn_neg_sum_ss 的分母覆盖率通常是全家族九列中较低的一支之一 (与另两个 ss 轨列同受严格同句判据约束), 若在生产语料 (T=19) 上仍出现分母长期偏低的情形, 应结合 stage 13/14 的共现统计核查是否属于该银行本身报道量整体稀少, 而非模型推理环节的缺陷。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019), 4171-4186. https://doi.org/10.18653/v1/N19-1423
Liu, Z., Huang, D., Huang, K., Li, Z., & Zhao, J. (2020). FinBERT: A pre-trained financial language representation model for financial text mining. Proceedings of the Twenty-Ninth International Joint Conference on Artificial Intelligence (IJCAI-20), 4513-4519. https://doi.org/10.24963/ijcai.2020/622
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Chen, L., & Mankad, S. (2025). A Structural Topic and Sentiment-Discourse Model for Text Analysis. Management Science, 71(7), 5767-5787. https://doi.org/10.1287/mnsc.2022.00261
Groß-Klußmann, A. (2024). Learning deep news sentiment representations for macro-finance. Digital Finance, 6(3), 341-377. https://doi.org/10.1007/s42521-024-00107-2
Ke, S., Montiel Olea, J. L., & Nesbit, J. (2024). Robust machine learning algorithms for text analysis. Quantitative Economics, 15(4), 939-970. https://doi.org/10.3982/qe1825
Wang, Y., Xiao, J., Wang, L., & Wang, D. (2025). News sentiment and the cost of debt. Pacific-Basin Finance Journal, 91, 102721. https://doi.org/10.1016/j.pacfin.2025.102721
<!-- rendered-citations:end -->
