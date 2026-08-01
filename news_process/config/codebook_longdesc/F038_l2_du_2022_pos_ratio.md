---
family_id: F038
columns:
- avg_du_2022_pos_ratio_ctx
- avg_du_2022_pos_ratio_full
- avg_du_2022_pos_ratio_ss
unit: 比率 (正面词次占 word-token 数之比, 无量纲; 文章级 ∈ [0,1], 面板级为银行-年内文章均值)
formula: "avg_du_2022_pos_ratio{trk} = mean_over_articles(du_2022_pos_ratio{trk}), trk ∈ {full, ctx, ss}; 文章级 du_2022_pos_ratio = pos_count / n_word_tokens, pos_count = 经否定/程度/转折状态机处理后最终极性为正的 du_2022 词典命中词次数 (计数口径, 与幅度无关), n_word_tokens = 剔除纯标点/纯数字 token 后的词元数; n_word_tokens = 0 或空文本或词典缺失 → NaN"
producer: news_process/pipeline/sentiment/tone_words.py::_analyze_single_article (打分内核 _compute_sentiment_with_rules); 面板聚合 news_process/pipeline/panel/encode.py (avg_{d}_pos_ratio{track} = ({d}_pos_ratio{track}, 'mean')); Stata 标签 news_process/pipeline/panel/export.py + stata_export.py
upstream:
- "config/tone_dicts.json (du_2022 词典: positive 2,235 / political_positive 1,434 [打分权重 0.5] / negative 2,986)"
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 22_words_tone.parquet (文章级 du_2022_pos_ratio_{full,ctx,ss})
- 21_tone_llms.parquet (llm_verified_full 留篇门控, full-only 口径 2026-06-29)
citations:
- doi: 10.1007/s10479-025-06567-y
  type: journal
  authors: Anastasiou, D., Katsafados, A., & Tzomakas, C.
  year: 2026
  title: "Banks' stock price crash risk prediction with textual analysis: A machine learning approach"
  venue: Annals of Operations Research
  vol: 357
  issue: 1
  pages_or_artno: 89-111
- doi: 10.1007/s10479-026-07305-8
  type: journal
  authors: Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y.
  year: 2026
  title: "Uncovering financial network structures and connectedness from textual risk disclosures"
  venue: Annals of Operations Research
  pages_or_artno: Advance online publication
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: "125739"
- doi: 10.1177/10591478241245144
  type: journal
  authors: Banker, R. D., Huang, R., Li, X., & Yan, Y.
  year: 2024
  title: "Strategy typology and cost structure: A textual analysis approach"
  venue: Production and Operations Management
  vol: 33
  issue: 6
  pages_or_artno: 1285-1305
- doi: 10.1287/mnsc.2023.03556
  type: journal
  authors: Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration
  year: 2024
  title: "Reproducibility in Management Science"
  venue: Management Science
  vol: 70
  issue: 3
  pages_or_artno: 1343-1356
- doi: 10.1016/j.enpol.2023.113917
  type: journal
  authors: Xu, Z., Li, J., Hua, X., & Ren, P.
  year: 2024
  title: "Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry"
  venue: Energy Policy
  vol: 184
  pages_or_artno: "113917"
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1007/s10994-021-05946-3
  type: journal
  authors: Hüllermeier, E., & Waegeman, W.
  year: 2021
  title: "Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods"
  venue: Machine Learning
  vol: 110
  issue: 3
  pages_or_artno: 457-506
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: "Does fintech innovation improve bank efficiency? Evidence from China's banking industry"
  venue: International Review of Economics & Finance
  vol: 74
  pages_or_artno: 468-483
- doi: 10.18653/v1/d16-1057
  type: journal
  authors: Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D.
  year: 2016
  title: "Inducing domain-specific sentiment lexicons from unlabeled corpora"
  venue: Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing
  pages_or_artno: 595-605
- doi: 10.1016/j.jeconom.2005.02.011
  type: journal
  authors: Kleibergen, F., & Paap, R.
  year: 2006
  title: "Generalized reduced rank tests using the singular value decomposition"
  venue: Journal of Econometrics
  vol: 133
  issue: 1
  pages_or_artno: 97-126
new_dois: []
---

## CORE

【构念与来源】
本家族测度银行-年面板层面的词典法正面情感词密度: 对每一篇经留篇门控保留的目标银行金融科技相关报道, 以 Du、Huang、Wermers 与 Wu 构建的中文金融情感词典 (管道内代号 du_2022, 见 Du et al. (2022)) 为量尺, 统计经语言学规则处理后最终极性为正面的词典命中词次数, 除以该篇文章剔除纯标点与纯数字后的词元总数, 得到文章级正面词占比 du_2022_pos_ratio; 再在每个银行-年单元内对全部留存文章取无加权算术均值, 得到面板列 avg_du_2022_pos_ratio。三条轨道 full、ctx、ss 分别在三种文本视窗上重复同一计算, 构成同一构念在不同文本口径下的三个并排测量。这里的核心构念不是情感的方向, 而是正面表述在一篇报道篇幅中的浓度: 它回答的问题是, 在关于某家银行金融科技动向的媒体叙事里, 有多大比例的词是被明确渲染为正面的, 而非这些正面词与负面词相抵之后偏向哪一侧。

构念设计上, 本族刻意与净语调分离。净语调类测度把正负两侧信息压缩为单一带号分值, 当一篇报道同时含有强烈正面与强烈负面表述时, 两侧在分子中相互抵消, 净值趋近零, 与一篇通篇平淡、几乎不含情感词的报道在净语调上不可分辨, 这就是词典法文献所称的极性对冲掩蔽问题。把正面侧单独析出为独立协变量后, 回归设计可以让正负两侧各自进入模型、比较两侧系数的相对大小, 也可以用两侧占比构造情感分歧类的二阶指标, 从而保留净语调压缩过程中丢失的单侧强度信息。管道内, 本族与镜像列 avg_du_2022_neg_ratio 构成正负分离对, 并作为下游词级情感分歧指标族的直接输入; 六部词典的同名正负占比对共同支撑跨词典分歧的计算。换言之, 本族既是一个可以独立进入回归右端的浓度型协变量, 又是一个专供二阶分歧构念取用的原材料, 双重身份决定了它的定义必须是分侧的、可加的、不做净额抵消的。

词典来源上, du_2022 是针对中文金融语料专门构建的领域情感词典, 收录常规正面词 2,235 条、负面词 2,986 条, 并额外单列政治正面词 1,434 条。领域与语言的双重特异性是该词典的立身之本: Du et al. (2022) 系统论证了把英文通用词典或英文金融词典直接翻译移植到中文金融语境会产生大量极性误判, 词汇的情感负载必须在目标领域语料上重新标定; 这一立场与计算语言学侧的证据一致, Hamilton et al. (2016) 表明情感词典具有强烈的领域特异性, 同一词在不同领域语料中的极性可以相反, 在领域语料上诱导的专用词典显著优于通用词典的直接套用。中文金融情感词典的构建此后仍在活跃迭代, Ma et al. (2025) 面向中国个人投资者语料构建了细粒度中文金融情感词典, 说明该文献分支持续演进; 本管道同时并行维护六部中文金融与通用情感词典 (jiang_2021、yao_2021、bian_2021、du_2022、you_2018 与 loughran 中文主译本), du_2022 只是其中之一, 六部词典的同名占比列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。

应用语境上, 本面板的观测单元是中国商业银行乘年份, 语料是银行与金融科技共现的媒体报道。银行层面的媒体情感测度已有直接同域先例: Fang et al. (2024) 用中国银行业的媒体情感解释存款稳定性与系统性风险, 证明报道情感在银行样本上具有经济后果层面的信息含量; Lee et al. (2021) 确立了金融科技创新与中国银行效率之间的实证联系, 为本面板银行乘金科报道的语料切片提供了研究问题层面的依据。政治正面词的单独收录与差异化处理则呼应中国媒体环境的制度特征: 政治性褒扬词的情感信号强度系统性弱于普通正面词, 是 Du et al. (2022) 在构建该词典时的发现, 也是词典把政治正面词单列一类并在打分层降权的直接经验依据; Xu et al. (2024) 则从旁佐证了这一制度背景 — 政府控制媒体的语调对资本市场有信息含量, 但其语言习惯高度程式化。需要注意的是, 本族是计数口径, 政治词降权只作用于打分层, 对本族的影响机制在方法学一节单独写明。

【方法学与计算】
文章级计算位于管道 stage 22 (producer 为 pipeline/sentiment/tone_words.py), 入口函数 _analyze_single_article, 打分内核 _compute_sentiment_with_rules。分词使用 stage 22 词典匹配专用的独立 jieba Tokenizer 实例 (注入隔离, 见 _get_tone_tokenizer): 领域复合词只注入此实例, 全局 jieba 分词器保持纯净, 以免污染其它依赖词性标注的度量; jieba 版本冻结在 0.42.1。每篇文章仅切分一次, 六部词典共享同一份词元序列, 调用方预切的 raw token 复用回内核以保证逐字节等价。计数遵循一个逐词元的状态机: 遍历词元序列时维护否定窗口、程度副词倍率与转折激活三个句法状态; 遇句末标点全部重置, 实现从句级作用域; 遇转折连词激活转折并重置否定与程度; 遇否定词开启定长否定窗口 (窗口长度 2 个分词单元); 遇程度副词记录倍率。当词元命中 du_2022 词典时, 取词典基础分, 常规正面词与负面词为满幅, 政治正面词以 0.5 权重的基础分进入; 若处于否定窗口内则翻转符号, 再乘以程度倍率 (最高约 3.0) 与转折增强 (约 1.5), 得到该词次的最终带号分值。这套从句级作用域的规则设计遵循转折效应限定为从句级的语言学惯例, 使否定与转折不会跨句串味。

本族分子 pos_count 是计数口径: 统计最终带号分值为正的命中词次数, 每个词次记一次, 与其幅度无关。由此有三个必须写明的推论。其一, 否定翻转改变计数归属, 不乐观里的乐观最终计入负面词次而非正面词次, 因此本族并非裸词表匹配频次, 而是语言学规则处理后的极性计数, 这一点区别于纯词频法。其二, 政治正面词的 0.5 权重只作用于分值幅度, 不作用于计数: 一个未被否定的政治正面词, 其基础分 0.5 为正、翻转与缩放后仍为正, 在 pos_count 中与一个普通正面词同样记一次。因此本族对政治词权重梯子中 0.5 与 1.0 两臂的取值天然不变, 该梯子 (polw00、polw05、polw10 三权重, 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J) 只物化 score 类列, pos_ratio 族不设 polw 变体。其三, du_2022 词典没有正负跨类重叠词, 管道登记的两侧计数词表只涉及 jiang_2021、you_2018 与 loughran 三部, 故 2026-06-24 重叠词两侧保留的决策对本族数值没有任何影响。

分母 n_word_tokens 为 word-token 口径: 剔除纯标点与纯数字词元后的词元数, 复用 lm_non_sentiment 模块的非词正则 _LMFLS_NONWORD_RE, 与该模块占比类分母的修复同口径。分母收紧的动机是标点与数字词元的占比逐篇差异大且非常数, 若以物理词元总数作分母, 会引入与内容无关的稀释噪声, 使占比在标点密集的短讯与正文连贯的长稿之间不可比; 而词典命中词本为真词, 分子不受此剔除影响。文章级值保留六位小数。缺失语义为: 空文本、纯符号文本、分母为零, 或 du_2022 词典整体缺失时, 文章级值置 NaN, 与有词但零命中的真零严格区分; 该缺失契约与同模块其它比率列一致, 保证真零 (有实词却无正面命中) 与不可测 (无实词可供计数) 在下游聚合时不被混为一谈。

三轨文本在 stage 14 物化: content_full 为标题 prepend 后的全文正文, 原始内容列不动, 标题作为第 0 句参与扫描; content_ctx 为标题加目标银行实体提及句的邻域窗口文本; content_ss 为标题加银行与金融科技词同句共现句的正负 1 句窗口文本, 半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1, 该键与 stage 13 共现硬过滤的 cooccurrence_filter.sentence_radius 是两个不同的键。stage 22 对三轨文本各自独立运行同一状态机, 产出文章级三列写入 22_words_tone.parquet。

面板聚合位于 pipeline/panel/encode.py: 对每个银行-年单元, avg_du_2022_pos_ratio 等于该单元内留存文章对应轨道文章级值的无加权算术均值, NaN 值自动剔除不入分母, 因此银行-年均值的有效篇数是该单元内该轨道非缺失文章数。行宇宙遵循 2026-06-29 起的 full-only 留篇门控: 一篇文章是否计入面板只看 stage 21 的 llm_verified_full 是否为真; ctx 与 ss 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 逐轨照算各自的文章级值, 不另设留篇判据。Stata 导出层为本族生成正面占比均值系列的变量标签, 家族内三列在最宽 dta 中随其它词典占比列一并落盘。

【文献定位】
词典法是金融文本分析的基线方法学, 其优势是透明、可复现、零边际成本, 与机器学习法和大语言模型法互补而非替代。Anastasiou et al. (2026) 在银行股价崩盘风险预测中系统比较文本特征与机器学习方法, 显示词典类特征仍是不可或缺的可解释基准; Banker et al. (2024) 用文本分析测度企业战略类型并连接成本结构, 示范了从文本构造企业级构念测度再进入面板计量的通用范式, 与本族从报道文本构造银行级情感测度的路径同构; Li et al. (2026) 进一步从文本风险披露中恢复金融网络结构与关联性, 说明文本测度已从单变量情感扩展到结构性信息抽取, 本管道的词典情感列位于这一谱系的基础层, 为上层的分歧、网络与语义类测度提供构件。方法学口径上, 本族的正负分离加词数分母设计延续英文金融词典法的经典占词比传统, 但因中文无空格、分词依赖 jieba、词典为中文领域词典, 其可比性锚点是中文金融词典文献 (Du et al. (2022); Ma et al. (2025)) 而非任何英文原始词表; 政治正面词单列的设计在英文词典谱系中没有对应物, 是中文制度语境的特有构造 (其经验基础来自 Du et al. (2022) 政治正面词信号弱于普通正面词的发现, Xu et al. (2024) 对政府控制媒体程式化语调的证据提供制度背景佐证)。把这些先例放在一起看, 本族的定位是清晰的: 它不追求作为唯一的情感测量, 而是作为透明、可审计、可与更黑箱的模型法三角互证的基线一臂, 在方法学组合里扮演解释性锚点的角色。

【识别策略定位】
本族在整个论文组合里不承担任何一篇的 headline 处理变量身份。P1 主线以银行金融科技报道的情感为处理变量, 其 canonical 测度是 LLM 三家投票的 llm_vote_tone_full, 结果变量则是外部财务哨兵 funding_cost, 这一对处理与结果之间的因果解释才是论文的第一层叙事; 本族在这层叙事之外承担三重从属但不可替代的支撑角色。第一重是净语调效应的正负分解与机制归因。词典法净语调 du_2022_tone 若在回归中给出显著系数, 其符号只告诉我们正负两侧净额偏向何方, 却无法回答该净效应究竟由乐观表述的增加驱动, 还是由负面披露的减少驱动; 把正面侧密度 avg_du_2022_pos_ratio 与镜像的 avg_du_2022_neg_ratio 分别放入同一设定的两个系数位, 就能读出两侧各自的边际贡献。若净语调效应几乎全部由负面侧承载而正面侧系数不可区分于零, 则"媒体乐观情绪推动银行融资成本下降"的解读必须让位于"负面信息披露抬升融资成本"的解读, 两种机制在政策含义上截然不同, 而这一判别只有在正负分离的前提下才可能成立。

第二重是情感分歧类二阶构念的构件。词级与跨词典情感分歧指标度量的是一篇报道内部、或多部词典之间正负两侧的失衡与不一致, 这类指标在数学上只能从分离的两侧占比构造, 无法从已经做过净额抵消的单一净语调值反推; 因为净值把正、负二维信息坍缩成一维带号标量, 分歧所依赖的两侧联合分布在坍缩过程中不可逆地丢失。本族与 avg_du_2022_neg_ratio 成对, 是 du_2022 口径下这一分歧构造的直接原材料, 六部词典的同名正负占比对共同支撑跨词典层面的分歧计算。正因如此, 本族的定义被刻意锁定为分侧的、可加的、不做净额抵消的计数密度, 任何把它改写成净值的"简化"都会摧毁其作为分歧输入的价值。第三重是跨词典规格稳健性并排中的 du_2022 臂。六部中文金融与通用情感词典的同名占比列构成互为稳健性、不分主次的规格并排, 各自 just-identified 并排, du_2022 臂在这一并排中的独特信息在于它是唯一单列并降权处理政治正面词的词典, 因而对政治性程式化褒扬密集的报道给出与其余五部系统性不同的读数, 这一差异本身就是识别政治语言对情感测度污染程度的一把内生标尺。

计量口径必须严格执行仓库铁律: 三轨 full、ctx、ss 之间, 六部词典之间, 以及一切梯子变体之间, 各自 just-identified 并排, 互为稳健性、不分主次, 禁止把不同轨、不同词典或不同变体当作多只工具塞进同一个 over-identified 的 Hansen J 检验。把同一构念的多个测量并入一条广义矩估计, 会把测量之间的误差结构差异伪装成过度识别拒绝, 使 J 统计量丧失对排除性约束的解释力, 拒绝或不拒绝都不再对应工具外生性的真实成立与否。当本族列进入工具变量设计充当被工具的内生情感测度时, 面板 IV 扩展提供三类恰好识别的工具: 同组 leave-one-out 同伴均值、广义 Bartik 份额暴露、以及媒体来源 house-style 暴露, 每条规格保持恰好识别, 弱工具诊断依 Kleibergen 与 Paap (2006) 的广义降秩检验统计量报告, 该统计量在非独立同分布误差下仍稳健, 而在恰好识别设定下过度识别检验没有自由度、本就不可用。跨词典的多重比较则按规格稳健性并排处理而非族错误率校正: 仓库既有的 FWER 校正模板只覆盖同一构念的替代 headline 测量场景, 即跨 LLM 厂商与跨 BERT 模型两族, 六词典占比族不属于该口径 — 它不是对同一 headline 处理变量的替代测量, 而是为分解与分歧提供构件的从属测度族, 因此不设 FWER 模板, 论文表述以主结论定性不变的稳健性叙事呈现, 而非以校正后 p 值的联合显著性主张呈现。

【与相邻测度的构念区分】
与 du_2022_tone 及其面板聚合的区分: tone 是幅度口径的净语调, 分子为全部命中词次最终带号分值之和, 分母为这些分值的绝对值之和, 自归一化到正负 1 区间, 度量的是情感的净方向与相对强度; 本族是计数口径的单侧密度, 分子是最终极性为正的命中词次数、每次记一、与幅度无关, 分母是全文剔除标点数字后的词元总数, 度量的是正面表述在篇幅中的浓度。两者分母性质根本不同, 一个是命中词内部的相对幅度量, 一个是占全篇幅的绝对篇幅量, 二者不可互相换算, 也不可互相替代 — 一篇净语调极高但正负命中都稀少的短讯, 其 pos_ratio 可以很低; 一篇正负势均力敌因而净语调趋零的长稿, 其 pos_ratio 却可以不低。

与 avg_du_2022_neg_ratio 的区分: 严格镜像, 分子换为最终极性为负的词次数, 两列共享同一分母与全部规则口径, 设计上成对使用、共同喂入分歧构造; 单独看任一列都只是分歧信息的一半, 只有两列联读才能还原一篇报道正负两侧的联合分布。与无词典前缀 avg_pos_ratio 的区分: 关键在量尺。无前缀列的计数基是六部词典固定 union 词典 — 全样本统一词表, 跨词典极性平票的歧义词以正一负一双票平衡喂入、极性 margin 守恒后被中性化, 回答的是综合词表下的正面密度; 本族以 du_2022 单部词典为量尺, 回答的是 du_2022 口径下的正面密度。两者在词表覆盖与政治词处理上均不同, 是家族层面的不同构念而非同列的轨道变体。

与其余五部词典同名 pos_ratio 的区分: jiang_2021、yao_2021、bian_2021、you_2018 与 loughran 各有同名正面占比列, 与本族在计算内核、分母口径、聚合方式上完全一致, 唯一差分在量尺词典。du_2022 臂的签名有二: 其一是六部词典中唯一单列并在打分层以 0.5 权重降权政治正面词的词典 (但降权只作用于 score 类列的分值幅度、不作用于本族的计数, 详见方法学一节); 其二是其领域与语言双重特异性的标定方式。六部词典的同名占比列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。与 du_2022_score 的规则消融与政治权重变体的区分: score 类列把否定、程度、转折三条规则的全组合物化为消融变体, 又把政治词权重的 0.0、0.5、1.0 三取值物化为 polw 变体; pos_ratio 族两类变体都不设 — 本族数值恒为全语言学规则、政治词满权计数口径下的唯一取值, 因为计数对政治词权重天然不变, 消融只改分值幅度不改极性归属的边际效应很小却会引发列数爆炸, 故家族刻意不铺开这两条梯子。规则消融梯子与政治权重梯子在 score 侧各自 just-identified 并排、互为稳健性、不分主次、正交不交叉, 禁混进同一 over-identified Hansen J。

与 msent 类计数净值指标的区分: msent 用固定 union 词典的原始极性计数、不经语言学规则, 其分值定义为负面计数减正面计数之差、再除以正负命中词计数之和 — 分母是命中词计数而非本族的全篇 word-token 篇幅量, 方向约定也与常见净语调相反 (负减正, 取值越大越偏负); 本族用规则处理后的最终极性、基于 du_2022 单部词典、输出以篇幅为分母的单侧占比, 在词典范围、规则处理、正负是否抵消、分母口径与符号方向诸维度上全部不同, 两者数值不可互相换算。与主题密度类 avg_ft_word_ratio 及套话、罕见词等风格类占比的区分: 那些列度量的是金融科技主题词密度或文本风格特征, 与词的情感极性无关; 本族的分子严格限定为情感词典命中且最终极性为正的词次, 是情感测度而非主题或风格测度, 两者即便数值上偶然相关也不可互换解释。与 LLM 与 BERT 情感轨的区分: 方法学家族不同, 词典法、生成式大模型法与判别式 BERT 法互为稳健性、不分主次, 各自 just-identified 并排, 同样禁混进同一 over-identified Hansen J; 三法的价值在于三角互证, 而非以其一取代其余。

【已知局限与稳健性梯子】
第一, 计数口径丢失幅度信息。pos_count 把强烈褒扬与轻微肯定同记一次, 程度副词的最高约三倍放大与转折的约一倍半增强只影响极性判定后的分值幅度、不改变计数, 因此本族对情感强度不敏感, 只对正面表述的条数密度敏感。这既是设计取舍也是局限: 与幅度口径的净语调列并读可以互补, 两者在解读中分别承担浓度维度与强度维度, 单看本族会低估"少而极强"的正面叙事、单看净语调会漏掉"多而温和"的正面铺陈, 稳健的机制解读应把两个维度并列而非二选一。

第二, 政治正面词在计数上满权计入。打分层针对政治正面词的 0.5 降权在本族中不存在 — 一个未被否定的政治正面词其基础分为正、经翻转与缩放后仍为正, 在 pos_count 中与一个普通正面词同样记一次。若政治性程式化用语的正面信号确实系统性弱于普通正面词 (Du et al. (2022) 构建词典时的发现; Xu et al. (2024) 对政府控制媒体程式化语调的证据是其制度背景佐证), 本族会对政治词密集的报道高估正面密度。缓解手段有二: 其一与政治词权重梯子的 score 列并读, 观察在 0.0、0.5、1.0 三权重下 score 结论是否稳定 (该梯子三权重各自 just-identified 并排、互为稳健性、不分主次、禁混进同一 over-identified Hansen J); 其二与其余五部不单列政治词的词典的同名占比列对照, 系数方向与显著性在对照中一致方可下结论。

第三, 词典时效与覆盖漂移。du_2022 词表冻结于其构建语料期, 而生产全量面板语料横跨 2007 至 2025 共 19 年, 词典构建之后才涌现的金融科技新词与新造褒义表达不在词表内, 命中覆盖率可能随时间单调漂移并与年份固定效应发生混同。六部词典并排以及与 LLM、BERT 轨的跨方法学对照提供对这一漂移的诊断; 年份固定效应可吸收各词典共同的时间趋势, 但无法吸收 du_2022 相对其余词典的差异化漂移, 后者只能靠跨词典对照识别。第四, 分词依赖与领域词注入。词典命中以 jieba 切分的词元为准, 分词错误直接改变命中集合与分母词元数。stage 22 使用注入隔离的独立 jieba 实例, 领域复合词只注入此实例、不污染全局分词器, jieba 版本冻结在 0.42.1 以保证跨次运行确定性; 但版本冻结只消除运行间的随机性, 不消除分词器本身对金融复合词可能过度切分或欠切分带来的系统误差, 这类误差在所有依赖 jieba 的词典列上共通, 属方法学基线的固有约束。

第五, 分母口径的取舍。分母为剔除纯标点与纯数字后的词元数, 复用 lm_non_sentiment 模块的非词正则, 目的是消除标点与数字词元逐篇占比差异带来的与内容无关的稀释噪声, 使占比在标点密集的短讯与正文连贯的长稿之间可比。代价是该分母定义与物理词元总数不同, 在与采用不同分母口径的外部研究做数值对照时须先对齐分母定义, 否则水平不可比; 但同一管道内六部词典共享同一分母口径, 内部横向可比性不受影响。第六, 三轨分母不等长导致的跨轨水平不可比。full、ctx、ss 三轨的窗口文本长度依次递减, 分母 n_word_tokens 依次减小, 占比的抽样方差依次增大; 三轨的占比水平不宜直接横向比大小, 而应作为同一构念在三种文本视窗下的并排测量, 各自 just-identified 并排、互为稳健性、不分主次, 用于检验 canonical full 结论对文本口径的敏感性。ss 轨还叠加回退混合: 无银行金科同句共现的文章其 content_ss 回退为全文正文、ss_is_fallback 置真、仍留在行宇宙内共享 n_articles 分母, 该回退语义镜像 ctx 轨的降级机制, 使 ss 轨在解读上是"能定位则聚焦、不能定位则退回全文"的混合口径。任何情况下三轨禁混进同一 over-identified Hansen J。

第七, 认识论与偶然不确定性的分野。以测量不确定性框架看, 词典覆盖不足属于可通过更换或增补量尺缓解的认识论不确定性, 而自然语言本身的歧义、反讽与语境依赖属于任何固定量尺都无法消除的偶然不确定性 (Hüllermeier 与 Waegeman (2021) 对二者的区分)。六部词典并排是对前者的操作化处理, 对后者只能靠词典法、LLM 法、BERT 法的多方法三角验证逼近, 而非靠任一单一量尺的精细化解决。第八, 可复现性与开发态退化。本族全链条无随机源: 词典冻结在 config/tone_dicts.json, 分词器版本冻结, 状态机为纯确定性函数, 词典法列不涉 LLM 缓存与嵌入接口, 可在离线模式下零成本逐字节重放, 符合当代对计算可复现性的规范要求 (Fišar et al. (2024)); 这是词典轨相对模型轨在审计层面的独特价值。早期试跑盘曾为两年开发面板 (本机现为 T=19 全量), 银行-年内文章数偏少使均值的抽样方差偏大, 生产全量语料下缓解; 本族无 _lg 孪生列, co-primary 双轨口径仅适用于嵌入族, 词典法属于非嵌入 carve-out, 这是设计使然而非缺漏。最后重申轨道铁律: full、ctx、ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 任何情况下禁混进同一 over-identified Hansen J。

## VAR: avg_du_2022_pos_ratio_ctx

【变体差分】
本列为实体窗口轨。计算内核、词典、分子分母口径与家族 canonical 的 full 轨完全一致, 唯一差分在输入文本: 文章级值在 content_ctx 上计算, 即标题 prepend 加目标银行实体提及句的邻域窗口文本, 由 stage 14 物化。银行实体的判定采用管道的不对称口径, 银行侧施加否定与短名过滤以防常见短名误匹配, 与金融科技侧的裸词表匹配判据不同。构念含义上, 本列把测量视窗收窄到目标银行被直接谈及的语句邻域, 剔除同一篇文章中与目标银行无关的段落, 例如同篇报道其它银行或铺陈宏观背景的部分所携带的情感噪声, 换取的解释是针对该银行的正面表述密度, 情感归属更干净。代价有二: 其一, 窗口文本显著短于全文, 分母 n_word_tokens 变小, 比率的抽样方差变大, 单篇取值更不稳定; 其二, 窗口截断可能切断跨句的情感修饰结构, 否定窗口与转折作用域在截断边界处失效, 个别词次的极性判定可能与全文口径不同, 从而使同一命中词在 ctx 与 full 两轨落入不同的 pos_count 归属。行宇宙与家族一致, 是 full-only 留篇门控下的 conditional-on-full 测度轨, 不另设留篇判据。本列与 full、ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 论文中作为 canonical full 结论的文本口径稳健性对照臂使用。

## VAR: avg_du_2022_pos_ratio_full

【变体差分】
本列为家族 canonical 列, tier 为 core, 2026-07-10 签核扩围的类别六即词典分解成分类核心列, 签核理由是其作为 du_2022 词典正面成分占比的全文轨规范口径。文章级值在 content_full 上计算, 即标题 prepend 后的全文正文, 原始内容列不动, 标题作为第 0 句参与状态机扫描, 因此标题中的正面词与正文同权计数, 标题词元也一并进入分母 n_word_tokens。full 轨被选为家族 canonical 有四点依据。第一, 口径与留篇门控同轨: 2026-06-29 起管道的留篇判据只看 llm_verified_full, full 轨的文本视窗与定义面板行宇宙的门控视窗完全重合, canonical 测度与样本构成之间没有口径错位; ctx 与 ss 是该行宇宙上的 conditional-on-full 附加测量, 它们的行宇宙是 full 留篇集的子集, 文本视窗也更窄。第二, 统计性质最稳: 全文是三轨中最长的文本, 分母词元数最大, 占比的抽样方差最小, 作为进入回归的基准测度信噪比最优, 银行-年均值对个别文章的敏感度也最低。第三, 跨文献可比: 词典法金融文本文献的标准做法是在整篇文档上计算占词比, 全文轨与该口径直接可比, 而窗口轨是本管道特有的构造, 缺少外部基准, 因此以全文轨承担对外报告与跨文献对照的角色最稳妥。第四, 语言学规则的作用域完整: 否定窗口、程度副词与转折的从句级作用域在连续全文上不受截断干扰, 极性判定最接近状态机的设计语义, 不会因窗口边界把一个本应被否定翻转的正面词误计入 pos_count。本列在论文组合中的典型用法有三: 作为 du_2022 净语调全文轨的正面侧分解臂, 检验净效应由哪一侧驱动; 作为词级与跨词典分歧指标的输入构件, 与 avg_du_2022_neg_ratio 成对喂入分歧构造; 作为六词典正面占比并排中的 du_2022 臂参与跨词典稳健性叙事。解读本列时须记住两点计数口径的特性: 政治正面词满权计一次, 打分层的 0.5 降权不影响本列, 政治词密集报道的取值需与权重梯子 score 列对照解读, 判断正面密度的抬升是否由程式化政治褒扬贡献; 否定翻转改变计数归属, 本列不是裸词频, 一处被否定的正面词会转记入负面而非正面, 因此本列度量的是净规则处理后的正面浓度, 而非表层正面词的出现频率。还须区分本列的分子分母语义与净语调列的根本不同: 本列的分母是全文剔除标点数字后的词元总数, 是一个篇幅量, 与命中词多寡无直接联系, 所以当一篇报道整体信息密度上升、正面词绝对数增加而篇幅同比膨胀时, 本列可以保持平稳, 它捕捉的是正面表述占用篇幅的比例而非绝对条数。缺失契约在本列上同样严格: 空文本、纯符号文本或分母为零时本列置 NaN, 与有实词却零正面命中的真零区分, 面板均值自动剔除 NaN 而不把不可测样本当作零值稀释银行-年浓度。与 ctx、ss 的关系是并排而非嵌套修正: 全文口径包含与目标银行无直接关联的段落, 存在情感归属误差, 该误差由两条窗口轨对照评估, 而非由窗口轨去修正全文轨; 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J。本列作为 core 列在最宽 dta 中落盘并被赋予正面占比均值全文轨的规范变量标签, 是家族对外呈现的默认口径。

## VAR: avg_du_2022_pos_ratio_ss

【变体差分】
本列为同句共现轨, 三轨中视窗最窄的一条。文章级值在 content_ss 上计算, 即标题加银行与金融科技词在同一句内共现的句子及其前后各 1 句的窗口文本, 半径由 config/filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 1。共现判定采用管道的不对称口径: 银行侧施加否定与短名过滤, 金融科技侧为裸词表匹配 (607 词的自动机词表)。回退语义与 ctx 轨机制镜像: 当一篇文章不存在银行与金科的同句共现时, content_ss 回退为全文正文, 同时 ss_is_fallback 置真, 回退篇仍留在行宇宙内共享 n_articles 分母, 其 ss 轨取值实际按全文计算; 金科词表整体缺失时全部文章置回退标志, 优雅降级不崩溃。因此本列在解读上是一个混合口径: 能定位到银行金科同句共现处的文章聚焦到共现语句邻域, 度量的是最贴近该银行金融科技业务表述的正面词密度, 定位不到的文章退回全文口径。这一构造使本列成为三轨中情感归属最强、但受回退混合与短文本方差影响也最大的一臂, 单篇分母最小, 银行-年均值对个别短窗口文章敏感。行宇宙与家族一致, 为 full-only 留篇门控下的 conditional-on-full 测度轨。本列与 full、ctx 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J; 若 canonical full 的结论在本列上定性保持, 则可排除结论由与银行金科主题无关的篇幅情感所驱动的替代解释。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Li, J., Yuan, X., Zhu, X., Emrouznejad, A., Hao, J., & Jin, Y. (2026). Uncovering financial network structures and connectedness from textual risk disclosures. Annals of Operations Research, Advance online publication. https://doi.org/10.1007/s10479-026-07305-8
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Banker, R. D., Huang, R., Li, X., & Yan, Y. (2024). Strategy typology and cost structure: A textual analysis approach. Production and Operations Management, 33(6), 1285-1305. https://doi.org/10.1177/10591478241245144
Fišar, M., Greiner, B., Huber, C., Katok, E., Ozkes, A. I., & the Management Science Reproducibility Collaboration. (2024). Reproducibility in Management Science. Management Science, 70(3), 1343-1356. https://doi.org/10.1287/mnsc.2023.03556
Xu, Z., Li, J., Hua, X., & Ren, P. (2024). Is the tone of the government-controlled media valuable for capital market? Evidence from China's new energy industry. Energy Policy, 184, 113917. https://doi.org/10.1016/j.enpol.2023.113917
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Hüllermeier, E., & Waegeman, W. (2021). Aleatoric and epistemic uncertainty in machine learning: An introduction to concepts and methods. Machine Learning, 110(3), 457-506. https://doi.org/10.1007/s10994-021-05946-3
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Hamilton, W. L., Clark, K., Leskovec, J., & Jurafsky, D. (2016). Inducing domain-specific sentiment lexicons from unlabeled corpora. Proceedings of the 2016 Conference on Empirical Methods in Natural Language Processing, 595-605. https://doi.org/10.18653/v1/d16-1057
Kleibergen, F., & Paap, R. (2006). Generalized reduced rank tests using the singular value decomposition. Journal of Econometrics, 133(1), 97-126. https://doi.org/10.1016/j.jeconom.2005.02.011
<!-- rendered-citations:end -->
