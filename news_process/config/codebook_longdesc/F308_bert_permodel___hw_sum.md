---
family_id: F308
columns:
- fin_sent_zh_负面_hw_sum_ctx
- fin_sent_zh_负面_hw_sum_full
- fin_sent_zh_负面_hw_sum_ss
- finbert2_负面_hw_sum_ctx
- finbert2_负面_hw_sum_full
- finbert2_负面_hw_sum_ss
- finbert_cn_负面_hw_sum_ctx
- finbert_cn_负面_hw_sum_full
- finbert_cn_负面_hw_sum_ss
unit: 无量纲加权概率和 (跟风衰减权重 × BERT 负面概率的 bank-year 求和, 未除以权重和分母, 非区间有界得分)
formula: bank-year 内 Σ_articles [herd_weight_{track}(article) × {model}_负面_{track}(article)], 三模型 (finbert_cn/fin_sent_zh/finbert2) × 三轨 (full/ctx/ss) 各自独立求和; 是 {model}_neg_hw{track} = 本列 / sum_herd_weight_{track} 的分子中间列, 本身不除分母
producer: pipeline\panel\encode.py (build_aggregation_dict 聚合注册 L1070-1072; aggregate_panel 除法消费 L2307-2311) ; pipeline\sentiment\tone_berts.py (文章级 {model}_负面_{track} 概率来源) ; pipeline\sentiment\herd_decay.py (herd_weight_{track} 计算逻辑, stage 24 的实现模块; 24_herd_decay_processor.py 仅为仓库根目录 thin shim)
upstream:
- 23_bert_tone.parquet
- 24_herd_decay.parquet
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
  vol: "40"
  issue: "2"
  pages_or_artno: 806-841
- doi: 10.18653/v1/N19-1423
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019)
  pages_or_artno: 4171-4186
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: "62"
  issue: "3"
  pages_or_artno: 1139-1168
- doi: 10.1007/978-3-030-32381-3_16
  type: journal
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: "Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science"
  vol: "11856"
  pages_or_artno: 194-206
- doi: "10.1111/jofi.13482"
  type: "journal"
  authors: "Hirshleifer, D., Mai, D., & Pukthuanthong, K."
  year: 2025
  title: "War Discourse and the Cross Section of Expected Stock Returns"
  venue: "The Journal of Finance"
  vol: "80"
  issue: "6"
  pages_or_artno: "3589-3637"
- doi: "10.1287/mnsc.2022.00261"
  type: "journal"
  authors: "Chen, L., & Mankad, S."
  year: 2025
  title: "A Structural Topic and Sentiment-Discourse Model for Text Analysis"
  venue: "Management Science"
  vol: "71"
  issue: "7"
  pages_or_artno: "5767-5787"
new_dois: []
---

## CORE

【构念与来源】
本家族 (F308) 是 bank-year 面板中 BERT 逐模型情感 (per-model robustness) 测度族里的一个纯中间/审计层: 跟风衰减加权 (herd-decay-weighted, 简称 HW) 负面概率的 bank-year 求和分子。它不是终态可解释测度, 而是 `{model}_neg_hw{track}` (加权负面概率均值) 分数的未除权分子, 保留在面板中供审计、复算与自定义分母替换用。产出模型有三个中文金融 BERT: finbert_cn (yiyanghkust/finbert-tone-chinese, 3 分类 中性/正面/负面)、fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3 分类模型)、finbert2 (项目自训练私有模型, 2 分类 负面/正面, 经 `.env` 的 `FINBERT2_MODEL_DIR` 解析; 该路径未配置或不存在时优雅跳过, 另外两个公开 HF 模型照常运行, 不影响本家族其余两模型的列)。这三个模型与情感测度体系里的另外两条独立路线——大模型三家投票 (LLM_MODELS: gpt54nano/gemini31/deepseekv4) 与词典法 (DICT_NAMES 六词典)——共同构成"三方法互证"的语调测量体系; BERT 一支不依赖关键词硬计数或提示工程, 而是端到端学习文本的整体语气分布, 对短文本、反讽、复杂句式的鲁棒性与前两支方法结构性不同, 因此三法并列互为稳健性, 用来证明结论不被任一测量范式的特有偏误驱动。
本家族名中的"负面_hw_sum"精确对应 stage 24 (herd_decay_processor) 产出的跟风衰减权重 (`herd_weight_{track}`, 其构念锚点是媒体新闻信息冗余/重复效应的度量思想——高度雷同的跟风报道彼此边际新增信息含量递减, 因此对雷同报道施加衰减权重、放大独立首发报道的权重) 与 stage 23 (tone_berts) 产出的文章级 `{model}_负面_{track}` 概率列 (softmax 输出的负面类概率, 0-1 区间) 逐篇相乘后, 在 bank-year 分组内求和。这一求和运算发生在 `pipeline/panel/encode.py::build_aggregation_dict` 的聚合字典注册阶段 (对每个 BERT_MODELS 成员与三轨分别注册 `agg[f'{b}_负面_hw_sum{track}'] = (f'{b}_负面_hw{track}', 'sum')`), 属 pandas groupby-agg 的标准 sum 聚合, 无额外裁剪或缩尾。

【方法学与计算】
计算分两层。第一层 (文章级, stage 23/24 产出, 不落入本家族): 对每篇文章 i, `{model}_负面_{track}(i)` 是该 BERT 模型对文章三轨拼接文本 (full=标题+正文; ctx=标题+实体窗口截取; ss=标题+银行∧金科同句±N 窗口, 无同句共现时回退为全文 body 并置 `ss_is_fallback=True`) 推理得到的负面类 softmax 概率 (超长文本经滑动窗口切片、按窗口置信度加权池化聚合各窗 logits 后再 softmax); `herd_weight_{track}(i)` 是该文章在其所属"报道簇"(同一事件/主题的高度相似报道群) 中的跟风衰减权重, 独立报道或首发报道权重更高, 后续高度雷同的跟风跟帖权重被衰减降低, 三轨各自独立计算 (full/ctx/ss 三套跟风权重互不共享, 因为不同轨道下的文本相似度判定基础不同)。第二层 (bank-year 级, 即本家族): 对同一 bank-year 单元内的全部文章 i, 计算 `Σ_i herd_weight_{track}(i) × {model}_负面_{track}(i)`, 得到本列的原始值。
本家族的九列穷尽了"三模型 × 三轨"的全部组合 (finbert_cn/fin_sent_zh/finbert2 各三列, 后缀 _full/_ctx/_ss)。它们在 `aggregate_panel` 的下游消费步骤 (`encode.py` L2307-2311) 中被同一 bank-year 单元的 `sum_herd_weight_{track}` (跟风权重和, 分母, 0 值经 `.replace(0, np.nan)` 防除零) 相除, 产出真正可解释、区间大致落在 [0,1] 的加权测度 `{model}_neg_hw{track}` = 本列 ÷ `sum_herd_weight_{track}`。因此本家族九列在计量意义上是"分子未归一化的原始加权和", 单位是"权重 × 概率"的量纲乘积, 并非概率本身, 也不是标准化得分; 其绝对水平会随 bank-year 单元内文章篇数、跟风权重尺度共同波动, 不建议直接作为回归自变量——正确用法是取其与配套 `sum_herd_weight_{track}` 的比值 (即 `_hw` 后缀的下游列), 或在需要复算/换分母/审计口径时使用本列作为可追溯的原始分子。保留本家族列在面板中的意义在于: 使加权语调测度的构造过程完全可逆、可审计, 任何研究者可用不同的权重和分母重新推导, 而不必回溯到文章级明细。
与 F308 平行的还有正面 (正面_hw_sum) 姊妹家族与 mw (媒体加权)、vw (市值加权) 变体家族, 均遵循同一"分子求和列 ÷ 权重和分母"构造范式, 只是权重来源不同 (媒体级出现频次 vs 银行市值 vs 跟风衰减)。

【文献定位】
本家族三个 BERT 底座模型的方法学谱系: finbert2 直接采用 Xu et al. (2025, KDD '25) 提出的面向金融部署场景的双向编码器 FinBERT2, 针对中文金融文本的领域适配做了专门优化; finbert_cn/fin_sent_zh 属于同一脉络下的中文金融情感微调模型, 与 Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 提出的英文 FinBERT (基于金融文本语料继续预训练再微调的路线) 方法学同源; 三者的底层 Transformer 编码器架构均可追溯至 Devlin et al. (2019) 的 BERT 原始论文, 双向自注意力机制使其相较传统词袋/词典方法能捕捉长距离语境依赖与否定/转折等语言学结构。微调策略 (学习率、层冻结、序列截断) 遵循 Sun et al. (2019) 对中文文本分类场景下 BERT 微调超参数的系统性实证建议。加权聚合层面的"跟风衰减"思想服务于另一条独立的构念: 同题材/高度雷同的跟风报道彼此重复、边际新增信息含量递减, 因此本项目对雷同报道施加衰减权重、以加权求和 (而非简单等权平均) 方式聚合到 bank-year 层级, 高权重赋予首发/独立报道, 使 bank-year 层面的加权语调更贴近"新增信息含量"而非"报道数量"。这一权重构造的构念锚点是媒体新闻信息冗余/重复效应的度量思想 (完整理论依据见 stage 24 herd_decay 模块注释), 与本家族三个 BERT 底座模型的方法学谱系相互独立、不可混为一谈; 该锚点论文的正式 DOI 未收录于本家族白名单引文池, 故本节仅以思想脉络叙述, 不在 citations 中列出对应条目, 避免张冠李戴地借用另一篇不相关论文的 DOI 冒充其出处。Tetlock (2007, *Journal of Finance*) 在本家族中的定位仅限于其对"媒体语调信息内容会被市场价格吸收"这一更上位的媒体-市场定价关系的开创性论证, 为本项目将 BERT 逐模型负面概率作为语调测度、进而与银行融资成本等结果变量建立关联的整体研究设计提供背景依据, 与跟风衰减权重 (`herd_weight_{track}`) 的构造本身是两条完全独立的构念脉络, 不构成后者的理论来源, 引用时须避免把两者混同。 就「篇级信号按逐篇权重加总为单元暴露量」这一构造范式而言, Hirshleifer、Mai 与 Pukthuanthong (2025) 提供了前沿先例: 该文用半监督主题模型对跨 160 年、约 700 万篇《纽约时报》报道抽取话语主题, 逐篇得到战争话语强度后按强度 (而非等权计数) 汇总为文本暴露量, 据以构造战争因子解释预期收益截面; 本族以 herd_weight 逐篇加权再求和、而非等权计篇数的做法与之共享同一汇总逻辑。⚠ 该锚点仅止于加权汇总这一步: 原文的逐篇权重来自话语主题强度, 与本族按报道雷同度折扣冗余的衰减权重来源不同, 且原文无情感极性与分类概率输出、聚合层级为市场/组合而非银行-年、语料为美国英文新闻, 故不为本族的负面概率口径提供任何依据。Chen 与 Mankad (2025) 提出 STS 主题模型, 引入文档级的连续情感-话语潜变量并允许其被文档级协变量解释, 使文本情感得以进入正式统计推断而非仅作描述性摘要; 本族以篇级连续负面概率 (而非 argmax 硬标签) 作为被加权量, 与该文以篇级连续情感量为测度基本单位的立场一致。⚠ 边界须写实: 原文的情感量是贝叶斯生成模型的连续后验潜变量, 与 BERT softmax 的类别概率语义不同, 语料为评论/话语文本而非中文银行新闻, 亦无中性档、无篇级量在单元内求和的聚合步骤, 更无跟风衰减权重与银行-年面板。
## VAR: fin_sent_zh_负面_hw_sum_ctx

【变体差分】
模型 = fin_sent_zh (bardsai/finance-sentiment-zh-base, 基于 Financial PhraseBank 微调的 3 分类中文金融情感模型, 与 finbert_cn 同为公开 HuggingFace 权重, 二者共享同一"预期加载失败即 fail-loud"的严格降级语义, 与 finbert2 的预期性优雅跳过明确不同); 轨道 = ctx (标题 + 实体窗口截取正文, 而非全文正文, 也不是同句窄窗)。本列是该模型在 ctx 轨对每篇留篇文章的负面概率 × 该文章 ctx 轨跟风衰减权重, 在 bank-year 内求和后得到的分子; 除以同一 bank-year 单元的 `sum_herd_weight_ctx` 后得到最终可解释的加权测度 `fin_sent_zh_neg_hw_ctx`, 本列自身仍是未归一化的原始求和, 量纲为"权重×概率"乘积。ctx 轨与 full/ss 轨各自独立计算跟风衰减权重与文章留篇子集 (口径细节见家族 CORE 节), 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。留篇门控本身以 full-only 口径为准 (2026-06-29 起生效): 是否判定某篇文章为"一篇银行×金科报道"只看 full 轨的 LLM 验证结果, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集, 而非独立采样。若某篇文章缺少 `content_ctx` 有效窗口 (即正文中无法锚定目标银行实体上下文), 该篇 ctx 轨的负面概率与跟风权重均按上游 stage 14/23/24 既定的优雅降级规则处理, 不会静默产生偏差或错配到其他银行; finbert2 若因 `.env` 的 `FINBERT2_MODEL_DIR` 未配置或路径无效而被 stage 23 跳过, 不影响本列的计算 (fin_sent_zh 三轨独立降级, 不与 finbert2 或 finbert_cn 的任何一族联动或连坐)。作为审计用中间分子, 本列的绝对水平同时受该 bank-year 单元留篇文章数量与各篇跟风权重尺度共同驱动, 不宜脱离配套分母单独解读为"负面程度"。

## VAR: fin_sent_zh_负面_hw_sum_full

【变体差分】
模型 = fin_sent_zh (公开 HF 3 分类中文金融情感模型); 轨道 = full (标题 + 全文正文, 三轨中信息量最完整、也是家族默认的最宽文本口径, 与仅截取实体窗口的 ctx、仅截取银行∧金科同句窗口的 ss 形成互补)。本列是 fin_sent_zh 在 full 轨对每篇文章的负面概率与该文章 full 轨跟风衰减权重逐篇相乘后, 在 bank-year 分组内求和得到的分子; 除以同一单元的 `sum_herd_weight_full` 后得到最终测度 `fin_sent_zh_neg_hw_full`。full 轨的留篇门控是本项目当前主口径 (2026-06-29 起, stage 21 判定"是否为一篇银行×金科报道"只依据 full 轨的 LLM 验证结果, 即 `llm_verified_full == True`), 因此本列所覆盖的文章集合即为该 bank-year 单元的完整留篇集合, 不像 ctx/ss 轨那样会因为无法锚定实体窗口或无同句共现而进一步收缩或回退。full 轨的跟风衰减权重同样独立于 ctx/ss 计算 (三轨各自基于自身文本相似度判定报道簇), 因此 `sum_herd_weight_full` 与 `sum_herd_weight_ctx`/`sum_herd_weight_ss` 在数值上并不对应同一权重体系。与同家族 ctx/ss 两轨互为稳健性并排, 不分主次, 禁止三轨混入同一 over-identified Hansen J; finbert2 若因 `FINBERT2_MODEL_DIR` 未配置而整体跳过, 完全不影响本列 (per-model 独立降级)。作为分子中间列, 本列的水平会随该 bank-year 单元的报道体量 (n_articles) 与跟风权重尺度共同波动, 直接用作回归自变量前应先除以配套分母。

## VAR: fin_sent_zh_负面_hw_sum_ss

【变体差分】
模型 = fin_sent_zh; 轨道 = ss (标题 + 银行∧金科同句 ±N 窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认为 1; 这是三轨中最窄、最贴近"银行与金科同一句话被提及"这一严格判据的文本口径)。当某篇文章不存在银行与金科词汇的同句共现时, 该篇 `content_ss` 回退为全文 body, 语义上镜像 ctx 轨的回退规则, 并置 `ss_is_fallback=True`, 与 ctx 共享同一 `n_articles` 分母口径; 此时该篇在 ss 轨的负面概率实质上等同于对全文推理的结果, 但其跟风衰减权重 (`herd_weight_ss`) 仍按 ss 轨自身的文本相似度独立计算, 不与 ctx/full 轨共享权重体系。若上游 stage 24 未产出同句共现口径下的跟风权重 (即 `herd_weight_ss` 整列缺失), 本列在聚合阶段会因配套的 `sum_herd_weight_ss` 缺失而被 `aggregate_panel` 自动跳过分母除法, 对应的 bank-year 单元该列 (以及下游的 `fin_sent_zh_neg_hw_ss`) 取 NaN 而非 0, 属既定的优雅降级路径, 不会静默产生数值污染。ss 轨的判定原语 (`extract_bank_fintech_cooccurrence`) 与 stage 13 共现硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` 是不同口径的两个独立函数, 前者严格要求同一句, 后者允许 ±1 句窗口, 二者不可互相复用或混淆。作为最窄文本口径下的加权分子, ss 轨样本量天然小于 full/ctx (仅覆盖存在严格同句共现或触发回退的文章), 在文章数较少的 bank-year 单元中本列更容易出现零值或与 full 轨高度雷同的退化取值, 这是构造使然而非缺陷。本列与同家族 full/ctx 两轨互为稳健性、不分主次, 三轨/三模型各自 just-identified 并排, 禁止混入同一 over-identified Hansen J。

## VAR: finbert2_负面_hw_sum_ctx

【变体差分】
模型 = finbert2 (项目自训练私有金融 BERT, 2 分类 负面/正面, 无中性类; 经 `.env` 的 `FINBERT2_MODEL_DIR` 解析本地权重路径, 与另外两个直接从 HuggingFace Hub 拉取的公开模型来源不同); 轨道 = ctx (标题 + 实体窗口截取正文)。本列是 finbert2 在 ctx 轨对每篇留篇文章的负面概率与该文章 ctx 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以 `sum_herd_weight_ctx` 后得到 `finbert2_neg_hw_ctx`。finbert2 是三个 BERT 模型中唯一可能整族缺席的模型: 当 `FINBERT2_MODEL_DIR` 未配置或路径不存在时, stage 23 会优雅跳过该模型的推理 (finbert_cn/fin_sent_zh 两个公开 HF 模型照常运行、不受影响), 此时本列及其姊妹的 full/ss 两轨列在面板中整体缺失或全为 NaN, 这属于 per-model 独立降级机制——与 co-primary 嵌入族 (Qwen3/text-embedding-3-large) 的 both-or-neither 语义刻意不同, finbert2 缺席只影响其自身族, 不连坐 finbert_cn/fin_sent_zh 的任何一列。ctx 轨的具体口径 (实体窗口截取正文、行宇宙是 full 留篇集的子集、跟风权重按 ctx 轨自身文本相似度独立计算, 不与 full/ss 共享) 与家族 CORE 节所述一致, 与 full/ss 两轨互为稳健性并排、不分主次, 三模型三轨的组合均各自 just-identified, 禁止混入同一 over-identified Hansen J。finbert2 因是 2 分类模型, 其负面概率的分布形态 (无中性类争夺概率质量) 与另两个 3 分类模型存在结构性差异, 跨模型比较时应留意。

## VAR: finbert2_负面_hw_sum_full

【变体差分】
模型 = finbert2 (私有 2 分类模型); 轨道 = full (标题+全文正文, 当前留篇门控主口径覆盖的完整文本范围)。本列是 finbert2 在 full 轨对每篇留篇文章的负面概率与该文章 full 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以 `sum_herd_weight_full` 得到最终测度 `finbert2_neg_hw_full`。由于 finbert2 是 2 分类模型 (仅负面/正面, 无中性类), 其"负面概率"本质是二分类 softmax 输出, 与 finbert_cn/fin_sent_zh 的 3 分类负面概率在数值尺度上不完全可比——3 分类模型的负面概率还需与中性类争夺概率质量, 而 finbert2 的负面/正面概率之和恒为 1——因此三模型间的横向比较应以标准化后的效应量 (β 系数或 z-score) 为准, 而非直接比较概率水平或本列的原始加权和水平。full 轨是当前留篇门控主口径 (stage 21 判定"是否为一篇银行×金科报道"只看 full 轨), 覆盖该 bank-year 单元的完整留篇文章集合。finbert2 若因 `FINBERT2_MODEL_DIR` 未配置而被 stage 23 跳过, 本列 (连同其 ctx/ss 姊妹列) 整体缺失, 但不影响同一 bank-year 单元下 finbert_cn/fin_sent_zh 两模型任何轨道的列, 属 per-model 独立降级设计。与同家族 ctx/ss 两轨互为稳健性并排、不分主次, 三模型三轨均各自 just-identified, 禁止混入同一 over-identified Hansen J。full 轨的跟风衰减权重按该轨自身的报道文本相似度计算报道簇归属, 与 ctx/ss 轨的权重体系互不共享, 因此三轨下同一篇文章的跟风权重数值一般并不相等, 求和后的分子也各自独立可比对不同轨道的稳健性表现, 而非同一数字的简单重复。

## VAR: finbert2_负面_hw_sum_ss

【变体差分】
模型 = finbert2; 轨道 = ss (银行∧金科同句 ±N 窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制默认 1; 无同句共现时该篇 `content_ss` 回退为全文 body 并置 `ss_is_fallback=True`, 镜像 ctx 回退语义, 与 ctx 共享同一 `n_articles` 分母口径)。本列是 finbert2 在 ss 轨对每篇文章的负面概率与该文章 ss 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以 `sum_herd_weight_ss` 得到 `finbert2_neg_hw_ss`。finbert2 因 `FINBERT2_MODEL_DIR` 未配置而缺席时, 本列随其 full/ctx 两个姊妹轨一并缺失或全为 NaN (per-model 降级在同一模型的三轨内部是联动的, 但绝不牵连 finbert_cn/fin_sent_zh 这两个独立模型的任何一列)。若 `herd_weight_ss`(stage 24 同句轨跟风权重) 因该阶段未运行同句轨而缺列, 本列的聚合结果因配套分母 `sum_herd_weight_ss` 缺失而在下游除法中被跳过, 取 NaN 而非误当 0 处理。作为 2 分类模型在最窄文本口径下的加权分子, 本列相较 3 分类模型的同名列在小样本 bank-year 单元 (文章数少) 下更容易出现零方差或退化取值, 属预期现象, 在 T=2 开发数据上尤为常见, 生产语料 T=19 规模下预期缓解。finbert2 缺席与 ss 轨 `herd_weight_ss` 缺列是两条相互独立的降级路径, 前者是模型层面整体缺失, 后者是权重来源层面局部缺失, 二者可能同时发生也可能只发生其一, 均不会互相掩盖或误报。与同家族 full/ctx 两轨互为稳健性并排, 不分主次, 三模型三轨均各自 just-identified, 禁止混入同一 over-identified Hansen J。

## VAR: finbert_cn_负面_hw_sum_ctx

【变体差分】
模型 = finbert_cn (yiyanghkust/finbert-tone-chinese, 公开 HuggingFace 3 分类中文金融情感模型, 中性/正面/负面, 由第三方在通用中文金融文本上预训练并做语调分类微调); 轨道 = ctx (标题 + 实体窗口截取正文)。本列是 finbert_cn 在 ctx 轨对每篇留篇文章的负面概率与该文章 ctx 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以 `sum_herd_weight_ctx` 后得到 `finbert_cn_neg_hw_ctx`。finbert_cn 与 fin_sent_zh 同属公开 HuggingFace 模型, 在默认 `strict_models=true` 配置下, 若这两个预期应当加载成功的模型实际加载失败, stage 23 会 fail-loud 直接抛错终止, 而非像 finbert2 那样静默优雅跳过——finbert2 因 `.env` 的 `FINBERT2_MODEL_DIR` 未配置或路径不存在属于预期内降级路径, 二者在失败语义上被明确区分开来。因此本列在正常生产运行中通常保持完整, 若出现大面积缺失更可能意味着环境配置异常 (如网络无法访问 hf.co 且本地无缓存, 未设置 `HF_HUB_OFFLINE=1`) 而非设计内的优雅降级。ctx 轨的实体窗口截取、留篇子集口径 (行宇宙是 full 留篇集的子集)、跟风权重独立计算等细节与家族 CORE 节所述一致, 与 full/ss 两轨互为稳健性并排、不分主次, 三模型三轨均各自 just-identified, 禁止混入同一 over-identified Hansen J。finbert_cn 与 finbert2 的 ctx 轨列在同一 bank-year 单元中互不依赖, 即使 finbert2 因路径未配而缺席, finbert_cn 的 ctx 轨列仍会正常产出, 二者的缺失/完整状态各自独立记录。

## VAR: finbert_cn_负面_hw_sum_full

【变体差分】
模型 = finbert_cn (公开 HF 3 分类中文金融情感模型); 轨道 = full (标题+全文正文, 当前留篇门控主口径覆盖的完整文本范围)。本列是 finbert_cn 在 full 轨对每篇留篇文章的负面概率与该文章 full 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以同一单元的 `sum_herd_weight_full` 后得到最终测度 `finbert_cn_neg_hw_full`。finbert_cn 是三分类模型 (中性/正面/负面), 负面概率与正面、中性概率共同构成一个 softmax 概率分布 (三者之和恒为 1), 这一点与 finbert2 的二分类输出结构 (仅负面/正面, 二者之和恒为 1, 无中性类争夺概率质量) 存在结构性差异, 跨模型比较负面概率的绝对水平时应留意这一分类基数差异, 更严谨的做法是比较标准化后的 net_tone (正−负, 定义域 [-1,1]) 或进一步 z-score 标准化后的效应量, 而非直接比较概率水平或本列这样的原始加权和。full 轨是当前留篇门控主口径, 本列覆盖该 bank-year 单元的完整留篇文章集合, 不像 ctx/ss 轨那样可能因实体窗口缺失或无同句共现而依赖回退逻辑。finbert_cn 与 fin_sent_zh 在 full 轨上同属 fail-loud 严格加载语义 (与 finbert2 的预期性优雅跳过区分), 二者的 full 轨列在正常生产环境下都应完整存在, 若同时缺失往往指向环境层面的模型下载/缓存问题而非设计使然。与同家族 ctx/ss 两轨互为稳健性、不分主次, 三模型三轨均各自 just-identified 并排, 禁止混入同一 over-identified Hansen J。

## VAR: finbert_cn_负面_hw_sum_ss

【变体差分】
模型 = finbert_cn; 轨道 = ss (标题 + 银行∧金科同句 ±N 窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制默认 1; 无同句共现时该篇 `content_ss` 回退为全文 body 并置 `ss_is_fallback=True`, 语义上镜像 ctx 轨的回退规则, 与 ctx 共享同一 `n_articles` 分母口径)。本列是 finbert_cn 在 ss 轨对每篇文章的负面概率与该文章 ss 轨跟风衰减权重相乘后, 在 bank-year 单元内求和得到的分子, 除以 `sum_herd_weight_ss` 得到 `finbert_cn_neg_hw_ss`。`herd_weight_ss` (stage 24 同句轨跟风权重) 若因该阶段未运行同句轨而缺列, 本列的聚合结果因配套分母 `sum_herd_weight_ss` 缺失而在下游除法阶段被跳过, 该 bank-year 单元取 NaN, 不影响 full/ctx 两轨的正常计算, 也不静默产生 0 值污染。finbert_cn 与 fin_sent_zh 同属 fail-loud 严格加载语义的公开 HF 模型, 因此 ss 轨的缺失通常只源于上游同句共现权重未产出, 而非模型自身推理失败。作为三分类模型在最窄文本口径下的加权分子, 本列的负面概率仍需与正面、中性概率共同构成 softmax 分布之和恒为 1, 这一约束在 ss 轨回退为全文推理的样本上同样成立, 不因窗口收窄而改变分类模型的输出结构。ss 轨样本天然是该 bank-year 单元留篇集合中存在严格同句共现或触发回退的子集, 样本量通常小于或等于 full/ctx 轨, 小样本单元下更易出现退化取值, 这是构造使然。本列与同家族 full/ctx 两轨互为稳健性并排, 不分主次, 三轨/三模型均各自 just-identified 并排, 禁止混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT 2019), 4171-4186. https://doi.org/10.18653/v1/N19-1423
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science, 11856, 194-206. https://doi.org/10.1007/978-3-030-32381-3_16
Hirshleifer, D., Mai, D., & Pukthuanthong, K. (2025). War Discourse and the Cross Section of Expected Stock Returns. The Journal of Finance, 80(6), 3589-3637. https://doi.org/10.1111/jofi.13482
Chen, L., & Mankad, S. (2025). A Structural Topic and Sentiment-Discourse Model for Text Analysis. Management Science, 71(7), 5767-5787. https://doi.org/10.1287/mnsc.2022.00261
<!-- rendered-citations:end -->
</content>
