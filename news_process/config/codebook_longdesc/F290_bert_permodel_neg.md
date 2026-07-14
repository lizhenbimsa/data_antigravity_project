---
family_id: F290
columns:
- fin_sent_zh_neg_app_ctx
- fin_sent_zh_neg_app_full
- fin_sent_zh_neg_app_ss
- fin_sent_zh_neg_ctx
- fin_sent_zh_neg_full
- fin_sent_zh_neg_hw_ctx
- fin_sent_zh_neg_hw_full
- fin_sent_zh_neg_hw_ss
- fin_sent_zh_neg_mw_ctx
- fin_sent_zh_neg_mw_full
- fin_sent_zh_neg_mw_ss
- fin_sent_zh_neg_ss
- fin_sent_zh_neg_tech_ctx
- fin_sent_zh_neg_tech_full
- fin_sent_zh_neg_tech_ss
- fin_sent_zh_neg_vw_ctx
- fin_sent_zh_neg_vw_full
- fin_sent_zh_neg_vw_ss
- finbert2_neg_app_ctx
- finbert2_neg_app_full
- finbert2_neg_app_ss
- finbert2_neg_ctx
- finbert2_neg_full
- finbert2_neg_hw_ctx
- finbert2_neg_hw_full
- finbert2_neg_hw_ss
- finbert2_neg_mw_ctx
- finbert2_neg_mw_full
- finbert2_neg_mw_ss
- finbert2_neg_ss
- finbert2_neg_tech_ctx
- finbert2_neg_tech_full
- finbert2_neg_tech_ss
- finbert2_neg_vw_ctx
- finbert2_neg_vw_full
- finbert2_neg_vw_ss
- finbert_cn_neg_app_ctx
- finbert_cn_neg_app_full
- finbert_cn_neg_app_ss
- finbert_cn_neg_ctx
- finbert_cn_neg_full
- finbert_cn_neg_hw_ctx
- finbert_cn_neg_hw_full
- finbert_cn_neg_hw_ss
- finbert_cn_neg_mw_ctx
- finbert_cn_neg_mw_full
- finbert_cn_neg_mw_ss
- finbert_cn_neg_ss
- finbert_cn_neg_tech_ctx
- finbert_cn_neg_tech_full
- finbert_cn_neg_tech_ss
- finbert_cn_neg_vw_ctx
- finbert_cn_neg_vw_full
- finbert_cn_neg_vw_ss
unit: 无量纲概率 (BERT 分类器 softmax 输出的负面类概率, 单模型独立值, [0,1] 区间; 加权变体为同区间加权平均; 分类维度变体为该子集内条件均值)
formula: "{model}_neg{sfx}{track} = 该 BERT 模型对银行-年留篇文章负面类 softmax 概率的 (条件/加权) 均值; model in {finbert_cn, fin_sent_zh, finbert2}; sfx in {'', _hw, _mw, _vw, _app, _tech}; track in {_full, _ctx, _ss}"
producer: pipeline/sentiment/tone_berts.py (逐模型逐轨 softmax 概率, stage 23) ; pipeline/panel/encode.py (银行-年聚合 agg 字典 D/F3-F5/K/L 块与 VW/MW/HW 除法) ; pipeline/panel/geography.py (compute_composite_indicators 内 _app/_tech 条件均值分支)
upstream:
- 23_tone_berts.parquet (逐模型三轨 {sn}_负面 概率列 + bert_num_windows_{track} 哨兵)
- 14_materialize_ctx.parquet (三轨文本 content_full/ctx/ss)
- 21_tone_llms.parquet (llm_verified_full 留篇门控 + tech/app 分类标签来源)
- 40_panel_yearly.parquet (银行-年聚合与 VW/MW/HW 加权源列)
citations:
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1145/3711896.3737219
  type: journal
  authors: Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z.
  year: 2025
  title: "FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models"
  venue: "Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25)"
  pages_or_artno: 5117-5128
- doi: 10.1007/s13278-025-01416-z
  type: journal
  authors: Punetha, N., & Jain, G.
  year: 2025
  title: "Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach"
  venue: Social Network Analysis and Mining
  vol: 15
  issue: 1
  pages_or_artno: Article 20
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: Journal of Finance
  vol: 67
  issue: 2
  pages_or_artno: 561-598
new_dois: []
---

## CORE

【构念与来源】
本家族 (F290, bert_permodel_neg) 度量的是"银行-年"层面每个 BERT 情感分类器各自独立输出的负面类概率强度, 是本项目情感测量三角中 BERT 一支的逐模型 (per-model) 稳健轨, 与 F111 (bert_avg_neg, 三分类模型跨模型集成) 互为稳健性、不分主次并排 — F111 回答"多个 BERT 模型综合起来看报道有多负面", F290 回答"单独看某一个 BERT 模型自己判读报道有多负面"。数据源自 stage 23 (23_tone_berts.parquet), 由三个独立训练的中文金融文本分类器 finbert_cn (yiyanghkust/finbert-tone-chinese)、fin_sent_zh (bardsai/finance-sentiment-zh-base) 与 finbert2 (本项目私有微调模型) 各自对每篇文章输出 softmax 概率, 本家族取每个模型自身负面类概率列在银行-年层面的 (条件/加权) 均值。三个模型互不共享参数、互不共享分词批次 (fix g-berts-01 后按各自 tokenizer 独立切窗), 因此三条逐模型负面轨可视为三个相互独立的"评审员"意见, 其两两一致性可用 Cohen's kappa / Krippendorff's alpha 度量 (tone_validation.py), 而非视为同一构念的三次重复测量。finbert2 是三者中唯一的二分类模型 (无中性类, 负面+正面概率恒等于 1), 类空间与另两个三分类模型不可比, 因此不参与 F111 的跨模型集成, 只以本家族的独立逐模型稳健轨形式存在——这正是 F290 存在的核心理由: 若无逐模型轨, finbert2 的判读信息将在集成阶段被结构性丢弃。

【方法学与计算】
每篇文章的原始负面概率由 stage 23 (tone_berts.py) 产出: 三个模型预加载至 GPU、混合精度批量推理, 超长文本按 WINDOW_STRIDE_RATIO=0.5 (50% 重叠) 滑动窗口切片, 各窗 logits 按置信度加权池化聚合 (logits ∝ Σ(conf_k·logits_k)/Σconf_k), 得到篇章级 softmax 概率; 批级异常逐篇重试一次, 仍失败则写失败哨兵 (概率 NaN, 与空文本 num_windows=0 严格区分)。银行-年聚合阶段 (encode.py) 对每个模型独立取组内均值 (mean), 自动跳过 NaN, 不与其他模型的概率混算。基列 (无后缀) 即该模型在 full/ctx/ss 三轨上的等权银行-年均值; 三类加权变体各刻画报道重要性的一个正交维度——_vw 按提及密度加权 (曝光量视角)、_mw 按来源媒体权威性加权 (媒体信誉视角, Tetlock 2007 JF)、_hw 按跟风衰减权加权 (Tetlock 2011 RFS 抄袭/羊群侦测视角, 下调雷同跟风报道贡献); 三者权重分别在 runner 步骤 3b/3c/3d 于文章级预计算, 聚合时进入各自的加权分子 (sum) 与对应分母的除法。_app/_tech 两个分类维度变体则是条件均值: 只在被 LLM 三家投票判定为"应用落地导向"或"底层技术导向"的金融科技报道子集上计算该模型的负面概率均值 (分母为该子集内该模型自身留篇文章数), 用以检验负面情绪是否集中于某一叙事焦点。三轨 (full/ctx/ss) 遵循 full-only 留篇门控口径 (2026-06-29): 一篇报道是否计入银行-年样本只由 llm_verified_full 判定, ctx/ss 轨是该留篇集之上的 conditional-on-full 测度/稳健性轨, 其行宇宙是 full 留篇集的子集; ss 轨回退语义镜像 ctx——无银行∧金科同句共现时 content_ss 回退为全文正文且 ss_is_fallback 置 True。

【文献定位】
BERT 法作为独立的第三条情感测量路线, 其方法学原点是 Huang, Wang & Yang (2023, *Contemporary Accounting Research*) 提出的 FinBERT 金融文本信息抽取模型, 本家族三个逐模型负面轨的设计沿此路线, 但刻意不做跨模型集成而是各自独立留存, 以保留每个模型的判读特异性 (finbert2 二分类判读尤为如此)。finbert2 本身的模型架构与训练细节见 Xu et al. (2025, KDD '25) 关于 FinBERT2 双向编码器如何弥合金融领域大模型部署缺口的说明, 该文是本地私有模型的直接方法学锚点。Punetha & Jain (2025, *Social Network Analysis and Mining*) 聚焦否定处理这一情感分析的长期技术难题, 说明不同分类器对负面极性的判读天然存在方法学分歧, 支持本家族保留独立逐模型负面轨 (而非仅报告集成均值) 的设计取向, 因为集成会掩盖模型间的系统性判读差异。Du et al. (2022, *Review of Finance*) 针对中文金融文本构建了领域专用情感词典, 界定了中文语料下情感判读的语言与领域特异性, 为本项目在中文银行/金科新闻语料上部署多个中文金融 BERT 模型提供了领域背景。Frankel, Jennings & Lee (2022, *Management Science*) 系统比较了机器学习与词典法的披露情感测量, 支持让 BERT 逐模型轨与词典法、LLM 投票法三角互证的整体设计。Tetlock (2007, *Journal of Finance*) 关于媒体报道语调对股票市场作用的经典研究界定了媒体作为情感信号载体的基准范式, 是本家族整体依托媒体报道文本测度情感的方法学背景; _mw 媒体权威加权这一具体构念的文献锚点则是 Gurun & Butler (2012, *Journal of Finance*) 关于地方媒体渲染 (slant) 与广告关系如何系统性调节报道可信度与市场相关性的发现——不同来源媒体在报道同一实体时存在系统性的可信度/权威性差异, 这一发现为按来源媒体权威性对逐模型负面概率加权 (media_authority) 提供了直接的构念依据: 权威性更高的来源, 其报道语调对银行声誉与市场认知的边际影响更大, 故 _mw 变体在加权聚合时赋予更高权重, 界定了"谁在报道"对情感信号市场相关性的调节作用。

凡涉三轨 (full/ctx/ss)、per-model 三家判读、三类加权 (VW/MW/HW) 与技术/应用两个分类维度, 各口径均为规格稳健性并排, 各自 just-identified、互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; per-model 之间遵循独立降级原则——finbert2 缺席 (FINBERT2_MODEL_DIR 未配置) 仅令 finbert2 自身各列缺席, 不连坐另两个 HuggingFace 模型的负面轨。

## VAR: fin_sent_zh_neg_app_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_app_full

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_app_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_full

本列即本家族在 fin_sent_zh 模型上的 canonical 基列: 无加权、不限分类子集、取 full 全文轨。它是 bardsai/finance-sentiment-zh-base (三分类 (正面/中性/负面), HuggingFace 公开模型, 基于 Financial PhraseBank 式中文金融语料微调) 对该银行该年度留篇金融科技报道独立输出的负面类 softmax 概率, 在 full 轨 (标题 prepend 加全文正文) 上取银行-年等权均值。留篇门控为 full-only 口径: 一篇报道是否计入样本, 由 llm_verified_full 判定。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。本列不进入任何加权或分类子集运算, 是该模型全部加权/分类变体在解读时的参照基准, 也是本家族 (逐模型) 与 F111 (跨模型集成) 之间可直接对照的锚点列——比较 fin_sent_zh_neg_full 与 F111 的 bert_avg_neg_full, 可判断该模型的判读是否与集成结果系统性偏离。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_hw_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_hw_full

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权)。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_hw_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_mw_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_mw_full

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权)。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_mw_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_tech_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_tech_full

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_tech_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_vw_ctx

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_vw_full

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路)。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: fin_sent_zh_neg_vw_ss

本列 = fin_sent_zh 模型 (bardsai/finance-sentiment-zh-base, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 fin_sent_zh_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 bardsai/finance-sentiment-zh-base 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 finbert_cn 同为三分类 HF 模型, 二者互为跨厂商稳健对照; tokenizer 与 finbert_cn 不同源, fix g-berts-01 后两模型各自独立分词, 不共享分词批次。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_app_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_app_full

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_app_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_full

本列即本家族在 finbert2 模型上的 canonical 基列: 无加权、不限分类子集、取 full 全文轨。它是 FinBERT2 (本项目私有微调模型) (二分类 (负面/正面, 无中性类), 本地私有权重, 经 .env FINBERT2_MODEL_DIR 解析; 路径未配置或不存在时优雅跳过该模型, 另两个 HuggingFace 模型照常运行) 对该银行该年度留篇金融科技报道独立输出的负面类 softmax 概率, 在 full 轨 (标题 prepend 加全文正文) 上取银行-年等权均值。留篇门控为 full-only 口径: 一篇报道是否计入样本, 由 llm_verified_full 判定。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。本列不进入任何加权或分类子集运算, 是该模型全部加权/分类变体在解读时的参照基准, 也是本家族 (逐模型) 与 F111 (跨模型集成) 之间可直接对照的锚点列——比较 finbert2_neg_full 与 F111 的 bert_avg_neg_full, 可判断该模型的判读是否与集成结果系统性偏离。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_hw_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_hw_full

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权)。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_hw_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_mw_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_mw_full

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权)。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_mw_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_tech_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_tech_full

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_tech_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_vw_ctx

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_vw_full

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路)。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert2_neg_vw_ss

本列 = finbert2 模型 (FinBERT2 (本项目私有微调模型), 二分类 (负面/正面, 无中性类)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert2_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 FinBERT2 (本项目私有微调模型) 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (二分类 (负面/正面, 无中性类)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。二分类类空间与另两个三分类模型不可比 (pos+neg 恒等于 1, 中性质量已重归一进正负两类), 因此不参与 F111 bert_avg 集成, 只以独立逐模型稳健轨形式存在。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_app_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_app_full

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_app_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 应用分类维度条件均值 (仅在被判为"应用落地导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为应用落地导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为底层技术导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_full

本列即本家族在 finbert_cn 模型上的 canonical 基列: 无加权、不限分类子集、取 full 全文轨。它是 yiyanghkust/finbert-tone-chinese (三分类 (正面/中性/负面), HuggingFace 公开模型) 对该银行该年度留篇金融科技报道独立输出的负面类 softmax 概率, 在 full 轨 (标题 prepend 加全文正文) 上取银行-年等权均值。留篇门控为 full-only 口径: 一篇报道是否计入样本, 由 llm_verified_full 判定。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。本列不进入任何加权或分类子集运算, 是该模型全部加权/分类变体在解读时的参照基准, 也是本家族 (逐模型) 与 F111 (跨模型集成) 之间可直接对照的锚点列——比较 finbert_cn_neg_full 与 F111 的 bert_avg_neg_full, 可判断该模型的判读是否与集成结果系统性偏离。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_hw_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_hw_full

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权)。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_hw_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 羊群衰减加权 (herd_weight, Tetlock 2011 RFS 跟风衰减权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 跟风衰减权 herd_weight (Tetlock 2011 RFS), 在 runner 步骤 3d 于文章级预计算, 三轨独立; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_mw_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_mw_full

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权)。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_mw_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 媒体权威加权 (media_authority, Gurun & Butler 2012 JF 媒体权威性权); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 媒体权威权 media_authority (Gurun & Butler 2012 JF), 在 runner 步骤 3c 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 无加权、无分类, 家族 (该模型) canonical 基列, 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_tech_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_tech_full

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算)。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_tech_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 技术分类维度条件均值 (仅在被判为"底层技术导向"金融科技报道子集上计算); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。分类维度来自 LLM 三家投票的 innovation_locus 判定 (LLM_CLASS_SPEC), 本列只在被判为底层技术导向的报道子集上取该模型的负面概率条件均值, 分母为该子集内该模型自身留篇文章数; 它与判为应用落地导向子集的对应列互为镜像, 二者之差是检验该模型负面情绪是否集中于特定叙事焦点的天然对照量, 但差值本身在样本篇数不足 (少数银行-年子集样本极小) 时噪声较大, 解读须结合子集篇数。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_vw_ctx

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ctx 实体上下文轨 (标题 prepend 加实体邻近窗口文本), conditional-on-full 稳健轨。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_vw_full

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 full 全文轨 (标题 prepend 加全文正文), 留篇门控主轨。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路)。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

## VAR: finbert_cn_neg_vw_ss

本列 = finbert_cn 模型 (yiyanghkust/finbert-tone-chinese, 三分类 (正面/中性/负面)) 独立输出的负面类概率, 施加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路), 轨道为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。相对本家族在该模型上的 canonical 基列 finbert_cn_neg_full, 本列的差分点在于: 聚合口径附加 密度加权 (value-weighted, 提及密度权, 呼应 Hassan et al. 2019 QJE 政治风险暴露密度构造思路); 文本轨道由 full 全文换为 ss 同句共现轨 (标题 prepend 加银行∧金科同句 ±N 窗文本), conditional-on-full 稳健轨, 回退语义镜像 ctx。权重来源: 提及密度权, 在 runner 步骤 3b 于文章级预计算; 分子为该模型负面概率的加权和, 分母为对应权重和, 二者在 encode.py 的除法阶段配对完成, 缺源列时经 valid_agg / if-in-columns 守卫优雅缺席而非报错。 与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该轨为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集的子集, 不改变留篇门控本身。ss 轨回退语义镜像 ctx: 银行与金融科技词无同句共现时, content_ss 回退为全文正文且 ss_is_fallback 置 True, 与 ctx 缺列同口径处理; dev 小样本期该轨可能因样本不足而多数格退化为 NaN, 属预期。 本列与家族内同模型的其余轨道/加权/分类变体、以及另外两个 BERT 模型的对应逐模型轨, 各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。

从白话角度理解, 该列刻画的是这家银行这一年金融科技报道单独经 yiyanghkust/finbert-tone-chinese 这一个 BERT 模型判读后, 负面情绪的强度——它不像家族 F111 那样把三个模型的判断揉在一起取平均, 而是原原本本保留这一个模型自己的看法。这样做的价值在于: 三个 BERT 模型训练语料、模型结构、乃至类别设置 (三分类 (正面/中性/负面)) 都不同, 它们各自对"什么算负面"的理解存在系统性差异, 只看集成均值会把这些差异抹平, 而实际研究中往往需要知道"结论是不是所有模型都同意, 还是被某一个模型的判读特质带偏"。与 fin_sent_zh 同为三分类 HF 模型, 二者互为跨厂商稳健对照; 两模型词表不同, 各自独立分词 (fix g-berts-01)。该列不进入外部财务因变量的构造, 而是作为报道情感的自变量或稳健性对照列, 与词典法、大语言模型投票法以及同家族其余逐模型轨相互印证, 结论越是在多种独立测量方法下都成立, 越经得起审稿人的稳健性质疑。

<!-- rendered-citations:begin -->
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Xu, X., Wen, F., Chu, B., Fu, Z., Lin, Q., Liu, J., Fei, B., Li, Y., Zhou, L., & Yang, Z. (2025). FinBERT2: A specialized bidirectional encoder for bridging the gap in finance-specific deployment of large language models. Proceedings of the 31st ACM SIGKDD Conference on Knowledge Discovery and Data Mining V.2 (KDD '25), 5117-5128. https://doi.org/10.1145/3711896.3737219
Punetha, N., & Jain, G. (2025). Advancing sentiment analysis by addressing negation handling challenge via unsupervised mathematical approach. Social Network Analysis and Mining, 15(1), Article 20. https://doi.org/10.1007/s13278-025-01416-z
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
<!-- rendered-citations:end -->
