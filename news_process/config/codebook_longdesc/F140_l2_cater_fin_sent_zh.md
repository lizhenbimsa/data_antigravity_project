---
family_id: F140
columns:
- cater_fin_sent_zh_ctx
- cater_fin_sent_zh_full
- cater_fin_sent_zh_ss
unit: 情感迎合度差值 (无量纲, 词典综合语调与 BERT 净语调之差)
formula: "cater_fin_sent_zh{track} = dict_avg_tone{track} - (fin_sent_zh_pos{track} - fin_sent_zh_neg{track}); track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/runner.py (步骤 8d algo_cater 段) ; news_process/pipeline/panel/export.py (标签映射)
upstream:
- 22_tone_words.parquet (dict_avg_tone 综合词典语调)
- 23_tone_berts.parquet (fin_sent_zh_pos / fin_sent_zh_neg 概率)
- 24_herd_decay.parquet (df_exploded, verified 篇章集)
- 40_panel_yearly.parquet (bank-year 聚合宿主)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: Review of Financial Studies
  vol: 36
  issue: 9
  pages_or_artno: 3603-3642
- doi: 10.1007/978-3-030-32381-3_16
  type: book
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science
  vol: 11856
  pages_or_artno: 194-206
- doi: "10.1145/3677052.3698675"
  type: "journal"
  authors: "Kim, W., Spörer, J., Lee, C. L., & Handschuh, S."
  year: 2024
  title: "Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER"
  venue: "Proceedings of the 5th ACM International Conference on AI in Finance"
  pages_or_artno: "626-633"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"算法迎合度"(algorithmic catering) 这一构念在单一深层语言模型 fin_sent_zh 上的实现: 它度量的是同一篇 (或同一银行-年聚合下的) 银行金融科技报道, 在综合金融情感词典下算出的语调, 与中文金融领域微调 BERT 模型 fin_sent_zh 算出的净语调之间的系统性落差。落差取正值时, 表示词典读法比深层模型更为正面; 取负值时表示深层模型比词典更为正面。这一差值之所以被命名为"迎合", 是因为在媒体经济学与文本披露文献里, 当写作者知道下游有算法在读取文本并据以形成判断时, 会倾向于调整措辞以迎合算法的读法, 从而在浅层词面 (词典可捕获的显性褒贬词) 与深层语义 (上下文 BERT 可捕获的隐性语气) 之间制造可观测的裂缝。本家族正是把这条裂缝在 fin_sent_zh 这一具体模型上量化出来, 作为跨模型迎合度稳健性梯子中的一根。

数据来源上, 词典侧综合语调 dict_avg_tone 来自 stage 22 的 tone_words 阶段, 是六部金融情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018、loughran) 在完整语言学规则 (否定翻转、程度副词、转折) 下各自归一化语调的综合平均; 模型侧的 fin_sent_zh_pos 与 fin_sent_zh_neg 来自 stage 23 的 tone_berts 阶段, 是中文金融 BERT 模型 fin_sent_zh 对每篇报道输出的正面、负面类概率。深层净语调定义为正面概率减负面概率, 落在闭区间的负一到正一之间。两侧信号在 stage 24 语义精筛后的 verified 篇章集 (df_exploded) 上按银行-年聚合, 最终在 stage 40 的面板总装车间 (runner.py 步骤 8d) 逐轨相减物化为本家族三列。

【方法学与计算】
计算链路是纯后处理的逐元素相减, 不重新调用任何情感模型或语言模型: 对每一轨 track, 若面板同时含 dict_avg_tone 与 fin_sent_zh 的正负概率列, 则令本列等于词典综合语调减去 fin_sent_zh 净语调; 三条轨道 full、ctx、ss 各自独立走这条链路, 缺任一上游列则该轨优雅跳过而不借用其它轨的分子分母。因为迎合度是两个已归一化测度之差, 它本身无量纲, 也不再二次归一化, 其符号与量纲的经济含义完全继承自两个被减量的口径。需要强调, 本家族与 algo_cater_b (综合词典对综合 BERT 平均) 以及 cater_finbert_cn、cater_finbert2 (换用另两个 BERT 模型) 是构念平行的族: 三个 BERT 模型各自的迎合度是互为稳健性、不分主次的并排测度, 各自 just-identified, 严禁把它们混进同一个 over-identified 的 Hansen J 过度识别检验; 同理三条文本轨道 (full/ctx/ss) 与词典侧的政治词权重梯度、规则消融梯度之间也保持正交, 不交叉相乘以免列数爆炸。per-model 独立降级: 若 fin_sent_zh 模型在某次运行缺席, 只掉本族三列, 不连坐其它模型族, 这与 co-primary 双轨嵌入 both-or-neither 的强绑定语义不同。留篇门控遵循 full-only 口径 (2026-06-29): 一篇报道是否计入银行金融科技样本只看 full 轨的 verified 判定, ctx 与 ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集。

【文献定位】
迎合度构念的直接理论出处是机器阅读时代的公司披露文献: Cao 等 (2023) 系统刻画了当披露的接收方由人类分析师转向算法读取时, 公司文本生产者如何有意调整措辞与语调以适配"正在聆听的机器", 为"词面语调与算法语调之差可作为迎合信号"提供了机制基础。模型侧, fin_sent_zh 属于中文金融领域微调的 BERT 家族, 其方法学根基见 Sun 等 (2019) 关于如何为文本分类微调 BERT 的系统研究; 词典侧综合语调则接续中文金融细粒度情感词典的构建传统, Ma 等 (2025) 构建的面向中国国内投资者的细粒度情感词典 CN-FSD 说明了中文金融词面情感为何需要专门词表而非直接移植英文 Loughran-McDonald。就"词典与深层模型对同一文本给出系统性不同读法"这一现象, Todd 等 (2024) 对金融文本情感分析文献的综述指出, 词典法与深度学习法的分歧本身是一类值得刻画的信号而非纯噪声; Lan 等 (2025) 进一步表明大语言模型在中文金融细粒度情感上的判读与词典存在可量化差异, 为本家族把差值当作构念而非误差提供了外部佐证。 在跨范式并排评测这一维度上, Kim、Spörer、Lee 与 Handschuh (2024) 于同一批央行沟通语料上把词典法 (VADER)、BERT 族 (FinBERT 与 FinBERT-FOMC) 与大语言模型 (GPT-4、Llama-3-70B) 并排评测, 给出三类方法语调判读彼此分歧、且模型规模更大并不必然与词典或小模型趋同的基准证据, 从测度学上支持本家族把「词典减 BERT」单列为与「词典减 LLM」正交的一根迎合度切面, 而非以任一侧为真值去校正另一侧。迁移边界须诚实标明: 该文语料为美联储 FOMC 英文沟通文本, 词典臂是通用情感词典 VADER 而非本项目六部中文金融词典, BERT 臂为 FinBERT 与 FinBERT-FOMC 而非 fin_sent_zh, 其评价目标是对齐人工标签的分类准确率, 并未构造本家族这样的有向差值面板列, 故只能用作模型端选择的定位依据, 不提供任何数值口径。
## VAR: cater_fin_sent_zh_full

【变体差分】
本列是 full 文本轨上的 fin_sent_zh 迎合度, 也是本家族的 canonical 门控轨。full 轨的文本口径为标题 prepend 之后拼接全文正文 (content_full), 即在 stage 14 的 ctx_materializer 中把标题前置到正文之首形成的完整篇章文本。按 full-only 留篇门控 (2026-06-29), 一篇银行金融科技报道是否计入样本, 唯一由 full 轨的 verified 判定决定, 因此本列的行宇宙即为面板的 verified 留篇全集, 是三轨中唯一不作条件化的基准轨。具体计算为: 该银行-年内 full 轨综合词典语调 dict_avg_tone_full, 减去 fin_sent_zh 模型 full 轨净语调 (fin_sent_zh_pos_full 减 fin_sent_zh_neg_full)。取正值时表示在完整篇章语境下词典读法比 fin_sent_zh 深层模型更正面, 是最贴近"整篇报道给读者的显性褒贬"与"整篇报道深层语气"落差的口径。本列与同轨的 cater_finbert_cn_full、cater_finbert2_full 构成跨 BERT 模型的迎合度稳健性并排, 三者各自 just-identified、互为稳健性不分主次, 严禁混入同一 over-identified 的 Hansen J; 与 ctx、ss 两轨亦为规格稳健性并排, 不得跨轨混同一过度识别检验。之所以选定 full 轨为 canonical, 是因为整篇文本承载了最完整的显性褒贬词与深层语气信息, 两侧读法的落差在整篇尺度上最稳定、最不受窗口切分噪声干扰; ctx 与 ss 两轨则通过收窄语境提供稳健性检验, 用以验证迎合度是否被无关段落稀释或放大。需要提醒, 本列的分子 dict_avg_tone_full 已在词典侧综合了六部词典并施加了完整语言学规则, 分母 fin_sent_zh 净语调则是深层上下文读法, 二者相减得到的正负号与量级须结合两个被减量的口径解读, 不宜脱离词典综合口径单独解读本列绝对水平。

## VAR: cater_fin_sent_zh_ctx

【变体差分】
本列是 ctx 实体窗口轨上的 fin_sent_zh 迎合度。ctx 轨的文本口径为标题 prepend 之后拼接实体窗口正文 (content_ctx), 即只保留目标银行等实体邻近上下文窗口内的正文, 相较 full 轨剔除了与银行金融科技主题距离较远的段落, 目的是让语调测度聚焦在与目标实体真正相关的语境上。按 full-only 门控, 本列是 conditional-on-full 的测度轨: 其行宇宙是 full 留篇集的子集, 只在被 full 轨判为留篇的银行-年上按 ctx 轨自身文本重新计算迎合度, 而非独立决定留篇。计算为该银行-年 ctx 轨综合词典语调 dict_avg_tone_ctx 减去 fin_sent_zh 模型 ctx 轨净语调 (fin_sent_zh_pos_ctx 减 fin_sent_zh_neg_ctx); 分子分母严格逐轨, 缺 ctx 列则本轨跳过, 绝不回借 full 轨的量。本列与 full、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨混进同一 over-identified 的 Hansen J; 与其它两个 BERT 模型的 ctx 迎合度亦保持同样的并排稳健性口径, 不交叉混同过度识别。ctx 轨相对 full 轨的信息价值在于: 若一篇报道大篇幅讨论其它主题而只在实体窗口内提及目标银行, full 轨会把无关段落的语调一并计入, 而 ctx 轨只保留实体邻近上下文, 从而检验迎合度是否对语境切分敏感。当本列与 full 轨的迎合度符号或量级出现系统性背离时, 提示词面语调与深层语气的裂缝主要来自实体窗口之外的段落, 这一诊断本身对判断迎合信号的稳健性有价值; 反之两轨一致则强化了迎合度不由窗口人为切分驱动的判断。

## VAR: cater_fin_sent_zh_ss

【变体差分】
本列是 ss 同句轨上的 fin_sent_zh 迎合度, 是三轨中语境最紧的口径。ss 轨的文本口径为标题 prepend 之后, 只保留目标银行与金融科技词在同一句子及其前后各 N 句窗口 (由 filtering.yaml 的 ss_sentence_radius 控制, 默认为一句) 内的共现片段所拼成的超级文档 (content_ss), 意在把语调测度收窄到银行与金融科技真正同句耦合的语义上。其回退语义镜像 ctx 轨: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 优雅回退为全文正文, 并置 ss_is_fallback 为真, 与 ctx 轨共享 n_articles 分母; 若金融科技的 AC 自动机为空则相关标记全部回退为真, 属优雅降级而非报错。按 full-only 门控, 本列同为 conditional-on-full 的测度轨, 行宇宙是 full 留篇集的子集。计算为该银行-年 ss 轨综合词典语调 dict_avg_tone_ss 减去 fin_sent_zh 模型 ss 轨净语调 (fin_sent_zh_pos_ss 减 fin_sent_zh_neg_ss), 分子分母严格逐轨不回借。本列与 full、ctx 两轨, 以及其它 BERT 模型的 ss 迎合度, 均互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified 的 Hansen J。ss 轨的独特价值在于把迎合度锁定到银行与金融科技真正同句耦合的语义上: 若词面语调与深层语气的裂缝只在这种最紧语境下仍然存在, 则更能排除迎合信号来自与主题无关的泛泛褒贬词的可能性。但须注意同句轨的样本较稀且回退比例较高, 当共现稀疏时大量篇章回退为全文正文, 使本列在极限语境与全文语境之间取值, 因此在早期试跑期短面板 (T=2) 上本列可能出现较多回退或退化, 生产期长面板上语料充足时方能稳定体现同句口径的边际信息, 解读时须结合 ss_is_fallback 回退比例一并考量。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification? Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science. https://doi.org/10.1007/978-3-030-32381-3_16
Kim, W., Spörer, J., Lee, C. L., & Handschuh, S. (2024). Is Small Really Beautiful for Central Bank Communication? Evaluating Language Models for Finance: Llama-3-70B, GPT-4, FinBERT-FOMC, FinBERT, and VADER. Proceedings of the 5th ACM International Conference on AI in Finance, 626-633. https://doi.org/10.1145/3677052.3698675
<!-- rendered-citations:end -->
