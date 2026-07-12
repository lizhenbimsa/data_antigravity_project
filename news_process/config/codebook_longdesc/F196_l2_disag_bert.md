---
family_id: F196
columns:
- disag_bert_ctx
- disag_bert_full
- disag_bert_ss
unit: 有界情感分歧指数, 取值域 [0, 1] (0 = 银行-年内报道情感完全一致即全正或全负, 1 = 正负情感力量相等即最大分歧); 无量纲
formula: "disag_bert{track} = sqrt(1 - ((bert_avg_pos{track} - bert_avg_neg{track}) / (bert_avg_pos{track} + bert_avg_neg{track}))^2), 分母 (pos+neg) 为 0 时取 NaN; bert_avg_pos / bert_avg_neg = 银行-年内三个金融 BERT 模型 (finbert_cn, fin_sent_zh, finbert2) 正类 / 负类概率的等权均值聚合; track ∈ {full, ctx, ss}"
producer: news_process/pipeline/panel/runner.py (step 8b _compute_disag, 由 bert_avg_pos/neg 计算并写入 disag_bert{track}) ; news_process/pipeline/panel/geography.py (合成 bert_avg_pos/bert_avg_neg 三模型概率均值) ; news_process/pipeline/panel/export.py (.dta 标签映射) ; news_process/pipeline/panel/codebook.py (元数据发射)
upstream:
- 23_tone_berts.parquet (finbert_cn / fin_sent_zh / finbert2 逐篇正/负/中类概率)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss 三轨文本)
- 40_panel_yearly.parquet (银行-年聚合)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1145/3711896.3737219
  type: wp
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2
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
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2018
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是一个银行在一个年度里, 关于它的新闻报道在情感倾向上究竟有多"众说纷纭"。用大白话讲: 如果这一年里所有涉及该银行金融科技的报道都异口同声地正面, 或者一致地负面, 那么分歧度就低; 相反, 如果有的报道热情吹捧、有的报道冷嘲热讽, 正面与负面的情感力量势均力敌, 那么分歧度就高。这个"打架程度"就是情感分歧 (disagreement) 构念, 它捕捉的不是情感的平均高低 (那是 tone 家族的事), 而是正、负两个方向情感在同一银行-年内的相对失衡程度。disag_bert 这一支, 专门用三个金融领域 BERT 模型集成后的正类、负类概率来度量这种分歧, 是整个 disag_* 分歧族里以深度学习语义编码器为测量前端的一轨。

必须先厘清一个易被误读的口径要点: 本家族并非"银行-年内各文章逐篇有符号情感值的横截面标准差", 也不存在名为 bert_avg_tone 的逐篇有符号集成情感列。真正的度量是一个有界分歧指数, 由银行-年层面聚合后的 BERT 正类概率均值与负类概率均值构造, 落在闭区间 [0, 1] 内: 当报道情感全部偏正或全部偏负 (正负两侧的概率质量高度失衡) 时指数取 0, 表示完全一致; 当正、负两侧的概率质量恰好相等时指数取 1, 表示最大分歧。这一构造遵循意见分歧文献里常用的"看多比例失衡"型分歧指数思路, 与逐篇打分再求标准差是两条不同的技术路线, 数值含义与取值域皆不相同。

本构念的经济学根据来自资产定价与信息经济学中源远流长的"意见分歧"文献。Hong 与 Stein (2007) 系统梳理了分歧如何通过卖空约束与异质信念影响价格形成; Carlin、Longstaff 与 Matoba (2014) 直接把分歧度量与资产价格波动、预期收益联系起来; Cen、Wei 与 Yang (2017) 证明分歧会带来反应不足与可预测的横截面收益。到了以文本为信息载体的时代, Cookson 与 Niessner (2020) 用投资者社交网络的帖子刻画分歧的来源与传导, Li 与 Luan (2025) 更进一步以新闻文本构造投资者分歧并检验其对股票收益的预测力——这正是本家族"以新闻情感失衡度作为分歧代理"这一测量选择的直接前沿依据。对银行而言, 关于其经营与金融科技布局的媒体叙事若正负拉锯、莫衷一是, 往往预示着市场对该银行前景判断的不确定, 进而影响其融资成本与存款稳定性, 因此分歧度是一个有独立经济含义的信息环境变量, 而非单纯的噪声。

【方法学与计算】
计算分三层。第一层是文章级的情感编码: stage 23 (23_tone_berts) 对每篇报道分别用三个中文金融 BERT 模型 (finbert_cn、fin_sent_zh、finbert2) 打出正类、负类、中性类三个概率。此处选用 BERT 而非词典或 LLM, 是因为 Transformer 双向编码器 (Devlin 等, 2018) 能捕捉词典法难以覆盖的上下文与否定结构, 而金融领域微调后的编码器 (Huang、Wang 与 Yang, 2023; Xu 等, 2025 的 FinBERT2) 在金融文本上显著优于通用模型; Bochkay、Brown、Leone 与 Tucker (2023) 关于会计文本分析方法演进的综述也把这类领域专用编码器列为词典法之后的方法学前沿。第二层是三模型集成与银行-年聚合 (geography.py): 把三个模型的正类概率取等权均值得到 bert_avg_pos、负类概率取等权均值得到 bert_avg_neg, 并聚合到同一银行、同一年度、同一文本轨道。第三层是分歧指数合成 (runner.py step 8b 的 _compute_disag): 令 r 为 (bert_avg_pos − bert_avg_neg) / (bert_avg_pos + bert_avg_neg), 它是一个刻画净看多倾向、取值介于 −1 到 1 之间的比率; 分歧指数取 sqrt(1 − r²)。直观地, 当情感一边倒 (r 趋近 ±1) 时指数趋近 0, 当正负均衡 (r 趋近 0) 时指数趋近 1; 分母 (bert_avg_pos + bert_avg_neg) 为 0 时该银行-年该轨取 NaN 而非强行赋值。需要说明的是, 概率均值是 float 输入, 该函数针对计数轨设置的整数回绕防护 (先转 float64) 对本轨是 no-op, 不改变数值。

需要强调三轨与稳健性口径。本家族按 full / ctx / ss 三条文本轨道并行计算 (stage 14 物化 content_full / content_ctx / content_ss): full 轨为标题 prepend 加全文正文, 是 canonical 主轨, 其行宇宙锚定 full-only 留篇门控 (2026-06-29 口径, 即一篇报道是否算作"一篇银行金科报道"只看 full 轨判定); ctx 轨为标题加实体窗口, ss 轨为标题加银行与金科同句共现窗, 二者降格为 conditional-on-full 的稳健性轨, ss 轨在无同句共现时优雅回退、镜像 ctx 语义。三轨各自 just-identified 并排使用, 互为稳健性、不分主次, 严禁把三轨混入同一 over-identified 的 Hansen J 过度识别检验。同理, 本 disag_bert 与分歧族内的词典均值分歧 (disag_full/ctx)、LLM 投票分歧 (disag_llm)、以及三个 BERT 单模型分歧 (disag_finbert_cn / disag_fin_sent_zh / disag_finbert2) 属于对同一"分歧"构念的不同测量前端, 彼此互为稳健性并排, 各自 just-identified, 亦禁混入同一过度识别检验。per-model 的单模型缺席只拖累其自身族列, 不触发集成轨的连坐降级。

【文献定位】
在实证识别层面, 本家族服务于以媒体信息环境解释银行融资与稳定性的研究链条。分歧作为信息环境刻画, 一方面可作解释变量进入银行结果方程 (融资成本、存款流动性等), 另一方面可作稳健性检验的替代测量, 检验主结论是否被单一情感测度所驱动。Cookson 与 Niessner (2020)、Li 与 Luan (2025) 提供了"分歧分解"与"新闻分歧预测收益"的框架先例; Cen、Wei 与 Yang (2017) 及 Carlin 等 (2014) 提供了分歧与价格、收益的理论桥梁; 而 Huang、Wang 与 Yang (2023) 与 Bochkay 等 (2023) 则为"用金融 BERT 测量文本情感"这一方法选择提供了会计金融顶刊层面的方法学背书。综合而言, disag_bert 是把成熟的意见分歧构念嫁接到深度学习情感编码前端、以银行-年聚合正负概率质量失衡度构造有界指数、并按三轨稳健性纪律实现的一组测量变量。

## VAR: disag_bert_full

【变体差分】
本列是 disag_bert 家族的 full 轨实现, 也是三轨中的 canonical 主轨。它在 full 文本轨道 (标题 prepend 加完整正文, content_full) 下, 由该银行-年三个金融 BERT 模型集成后的正类概率均值 bert_avg_pos_full 与负类概率均值 bert_avg_neg_full, 按 sqrt(1 − ((pos−neg)/(pos+neg))²) 合成有界分歧指数, 取值落在 [0, 1] (0 = 情感一边倒, 1 = 正负均衡即最大分歧)。请注意本列不是逐篇有符号情感的横截面标准差, 而是聚合正负概率质量失衡度的指数, 这是与"标准差式离散度"完全不同的口径。与 ctx、ss 两轨的唯一区别在于文本范围: full 轨读取整篇正文, 因此语义信息最完整, 也最不受实体窗口截断的影响, 相应地也会纳入正文中与目标银行金融科技主题关系较远的段落。full 轨的行宇宙严格锚定 full-only 留篇门控 (2026-06-29 口径): 一篇报道是否计入"一篇银行金科报道"、进而是否进入本轨聚合概率的分母集合, 只看该报道在 full 轨上的判定结果, ctx / ss 轨不参与留篇裁决。正因如此, full 轨的分歧指数在样本上是最完整、最稳定的一支, 通常被选作主回归中的分歧测量, 而 ctx、ss 两轨则作为 conditional-on-full 的稳健性对照。本列与三个 BERT 单模型的 full 轨分歧 (disag_finbert_cn_full 等) 的区别在于: 本列以三模型等权平均后的集成正负概率为输入, 单模型列则各用一家模型的正负概率; 集成轨与单模型轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J。full、ctx、ss 三轨同样各自 just-identified 并排, 不得跨轨拼进同一过度识别检验。

## VAR: disag_bert_ctx

【变体差分】
本列是 disag_bert 家族的 ctx 轨实现, 属 conditional-on-full 的稳健性轨。它与 full 轨在合成算法上完全一致——由同银行同年度三模型集成的正类概率均值与负类概率均值按 sqrt(1 − ((pos−neg)/(pos+neg))²) 合成有界分歧指数, 取值 [0, 1]——唯一差别是文本输入换成了 ctx 轨文本 (content_ctx, 即标题 prepend 加实体上下文窗口, 而非整篇正文)。同样需澄清: 本列不是逐篇有符号情感的横截面标准差, 而是聚合正负概率质量失衡度的指数。ctx 轨的设计意图是把情感测量聚焦在与目标银行实体邻近的语句上, 剔除正文中离题较远的段落, 从而得到一个"更贴近银行本体叙事"的分歧度。因此当研究者担心 full 轨分歧指数被与银行金科主题无关的正文噪声稀释或放大时, ctx 轨提供了一个收紧文本范围的替代测量。需要强调 ctx 轨在样本口径上的从属地位: 依 full-only 留篇门控, 一篇报道是否留存由 full 轨判定, ctx 轨只在 full 轨已留篇的子集上按 ctx 文本重算聚合概率与分歧指数, 因此 ctx 轨的行宇宙是 full 轨留篇集的子集, 不会独立引入或剔除报道。ctx 与 full、ss 三轨各自 just-identified 并排使用, 互为稳健性、不分主次, 严禁把三轨混入同一 over-identified 的 Hansen J 过度识别检验; 本列以三 BERT 模型集成正负概率为输入, 与单模型 ctx 分歧列同样属互为稳健性的并排轨, 亦禁混入同一过度识别检验。在极短面板 (如 T=2 开发样本) 上, ctx 轨因窗口内文章稀疏可能出现分母失衡退化或缺失, 属预期行为, 在生产规模长面板上恢复正常。

## VAR: disag_bert_ss

【变体差分】
本列是 disag_bert 家族的 ss 轨实现, 是三轨中文本范围最窄、约束最强的稳健性轨。它的合成算法与 full、ctx 两轨一致——三模型集成正负概率均值按 sqrt(1 − ((pos−neg)/(pos+neg))²) 合成 [0, 1] 有界分歧指数, 而非逐篇有符号情感的横截面标准差——差别仅在文本输入换成 ss 轨文本 (content_ss, 即标题 prepend 加"银行与金融科技同句共现"的句子窗口)。ss 轨只保留目标银行与金科词在同一句子 (或配置的同句半径窗内) 共现的语句, 因此测量的是最直接、最贴身的"银行谈金科"叙事的情感分歧, 把仅在篇章层面松散相关的语句彻底排除。这使 ss 轨成为对抗"实体共现偶然性"最严的分歧测量。ss 轨有明确的回退语义, 镜像 ctx 轨: 当某篇报道找不到银行与金科的同句共现时, content_ss 优雅回退为全文正文、并标记 ss_is_fallback 为真, 与 ctx 共享 n_articles 分母口径; 若金科 AC 自动机整体缺席则该轨全部回退, 属优雅降级而非静默清空。样本口径同样服从 full-only 留篇门控: 一篇报道是否留篇由 full 轨判定, ss 轨仅在 full 留篇子集上按 ss 文本重算聚合概率与分歧指数, 行宇宙是 full 留篇集的子集。ss 与 full、ctx 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨混入同一 over-identified 的 Hansen J; 本列同样以三 BERT 集成正负概率为输入, 与单模型 ss 分歧列并排互为稳健性, 不得混入同一过度识别检验。在 T=2 开发样本上, ss 轨因同句共现语料极稀往往整轨缺失或分母失衡退化, 属预期行为, 生产规模长面板上恢复有效取值。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 No. 5117-5128 [Working Paper]. https://doi.org/10.1145/3711896.3737219
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
<!-- rendered-citations:end -->
