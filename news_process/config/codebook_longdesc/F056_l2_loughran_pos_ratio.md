---
family_id: F056
columns:
- avg_loughran_pos_ratio_ctx
- avg_loughran_pos_ratio_full
- avg_loughran_pos_ratio_ss
unit: 比率/占比 (正面词命中数占 word-token 数之比, 无量纲, 值域 [0,1])
formula: "文章级 loughran_pos_ratio{trk} = pos_count{trk} / n_word_tokens{trk} (分母 = word-token 数, 剔除纯标点/纯数字词元; 分子 = loughran 词典命中且经否定规则翻号后带符号分值 > 0 的词元数, 两侧保留词双计); 面板级 avg_loughran_pos_ratio{trk} = 银行-年内留篇文章该比率的简单算术均值 (NaN 篇自动跳过), trk ∈ {_full, _ctx, _ss}"
producer: pipeline/panel/encode.py::build_aggregation_dict (M 段单词典比率聚合, aggregate_panel 消费); 文章级由 pipeline/sentiment/tone_words.py::_analyze_single_article 产出 (逐词典分值经 _compute_sentiment_with_rules)
upstream:
- 21_tone_llms.parquet (content_full/content_ctx/content_ss 三轨文本, stage 14 ctx_materializer 物化)
- 22_words_tone.parquet (文章级 loughran_pos_ratio_{full,ctx,ss})
- config/tone_dicts.json (loughran_mcdonald_zh_2026 词表 SSOT, 列前缀别名 loughran)
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
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1017/S0022109023000716
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2024
  title: "Measuring firm complexity"
  venue: Journal of Financial and Quantitative Analysis
  vol: 59
  issue: 6
  pages_or_artno: 2487-2514
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 475-501
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1093/rfs/hhaa079
  type: journal
  authors: Li, K., Mai, F., Shen, R., & Yan, X.
  year: 2021
  title: "Measuring corporate culture using machine learning"
  venue: The Review of Financial Studies
  vol: 34
  issue: 7
  pages_or_artno: 3265-3315
- doi: 10.1093/qje/qjx045
  type: journal
  authors: Hansen, S., McMahon, M., & Prat, A.
  year: 2018
  title: "Transparency and deliberation within the FOMC: A computational linguistics approach"
  venue: The Quarterly Journal of Economics
  vol: 133
  issue: 2
  pages_or_artno: 801-870
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: "Political bias in corporate news: The role of conglomeration reform in China"
  venue: The Journal of Law and Economics
  vol: 60
  issue: 1
  pages_or_artno: 173-207
- doi: 10.1111/jofi.12027
  type: journal
  authors: Garcia, D.
  year: 2013
  title: "Sentiment during recessions"
  venue: The Journal of Finance
  vol: 68
  issue: 3
  pages_or_artno: 1267-1300
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/j.1540-6261.2004.00662.x
  type: journal
  authors: Antweiler, W., & Frank, M. Z.
  year: 2004
  title: "Is all that talk just noise? The information content of internet stock message boards"
  venue: The Journal of Finance
  vol: 59
  issue: 3
  pages_or_artno: 1259-1294
- doi: "10.1111/ecin.13264"
  type: journal
  authors: "Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E."
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: "Economic Inquiry"
- doi: "10.1016/j.procs.2025.04.477"
  title: "Enhancing Financial Sentiment Analysis: Integrating the Loughran-McDonald Dictionary with BERT for Advanced Market Predictive Insights"
  authors: "Sheetal, R., & Aithal, P. K."
  year: 2025
  venue: "Procedia Computer Science"
  type: "journal"
- doi: "10.3390/bdcc9100263"
  title: "Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models"
  authors: "Chuang, H.-M., He, H.-C., & Hu, M.-C."
  year: 2025
  venue: "Big Data and Cognitive Computing"
  type: "journal"
new_dois:
- 10.1111/jofi.12027
- 10.1111/j.1540-6261.2004.00662.x
- "10.1111/ecin.13264"
- "10.1016/j.procs.2025.04.477"
- "10.3390/bdcc9100263"
---

## CORE

【构念与来源】
本家族测量的构念是: 一家银行在一个年度内, 其全部留存新闻报道中, 按 Loughran-McDonald 金融情感词典中文主译本判定为正面语调的词汇命中数, 占该篇全部有效词元数的平均比例。它是词典法语调测度经极性分解后的正面成分: 与把正负两侧轧差再归一化的净语调分值不同, 本族只保留正面一侧的词频密度, 与镜像的负面成分列 avg_loughran_neg_ratio 构成一对可分离的协变量。这一分解的方法学依据来自 Garcia (2013): 同一篇文本里正面词与负面词携带的信息并不对称, 若只用单一净情感指标, 两侧信号会相互对冲掩蔽, 研究者无法区分"正面信息增加"与"负面信息减少"这两种在经济含义上完全不同的变动; 把两侧分开作为独立变量, 才能让回归系数各自可解释。用大白话说, 净语调像温度计只报一个净读数, 而正负占比这对列相当于分别报告加热与制冷的功率, 两者对银行经营与风险的含义可以截然不同。词典来源方面, Loughran & McDonald (2011) 以"何时负债不是负债"的著名发问证明: 通用英语情感词典在金融语域会系统性误判, 其负面词表中约四分之三的词在财务披露语境中并不表达负面含义, 因此金融文本分析必须使用领域专用词表, 这一原则也构成本仓六部中文金融词典体系的共同方法论前提。本项目于 v3.10.0 把 Loughran-McDonald 词表的中文主译全本接入为第六部主情感词典, JSON 键为 loughran_mcdonald_zh_2026, 单一事实源为 config/tone_dicts.json; 由于该 JSON 键作列前缀会产生超长且不可读的列名, 加载时经唯一桥接常量把列前缀别名统一映射为 loughran, 面板聚合循环与 Stata 导出侧也硬编码同一别名, 两处必须逐字节一致, 否则聚合循环按别名找不到源列会静默全部置空, 这一别名一致性是本族与其余五部词典共用的接线命门。词表规模上, 极性消歧后含正面 1295 词、负面 3729 词; 原始 61 个正负跨类重叠词经 2026-06-24 逐词两侧保留判断, 其中 38 词已归入单侧, 其余 23 词不可约简, 按用户决策保留并登记到跨类重叠词表, 在打分时两侧同时计数, 而非武断剔除或静默判为单极。数据来源为本仓中文银行与金融科技新闻语料, 上游流经 stage 00 预处理、stage 11 银行实体识别、stage 12 金融科技识别、stage 13 共现硬过滤 (只保留目标银行与至少一个金科词邻近共现的报道) 与 stage 14 三轨文本物化, 再在 stage 22 词典情感阶段逐篇计算, 最终于面板阶段聚合到银行-年层。需要特别说明谱系身份: 本族三列是 v3.10.0 词典扩容时的新增扩展列而非回溯变值列 —— codebook 发射层的六词典扩容披露正则刻意把 avg_loughran_pos_ratio 前缀排除在"union 计数基由五部扩为六部而回溯微变"的受影响名单之外, 因为受该扩容影响的是固定并集口径的跨词典聚合列, 而本列自诞生起就是单词典口径; 同时发射层按列名命中 L&M 来源规则, 为本族自动补注 Loughran-McDonald 词表来源引文与 provenance 备注, 使 .dta 标签与 codebook 元数据同源一致, 不再落入自动推断的空引文占位。

【方法学与计算】
计算链路分文章级与面板级两层, 全程零 LLM 调用、零 API 成本, 确定性来自冻结版 jieba 分词器与词典文件本身, 因而在缓存离线守卫下可字节级复现。文章级在 stage 22 完成, 核心函数是 _analyze_single_article 调用 _compute_sentiment_with_rules: 输入读 stage 21 输出 parquet, 其中三条文本轨 content_full、content_ctx、content_ss 已在 stage 14 物化, 标题以 prepend 方式并入各轨正文, 原始内容列保持不动。对每条轨道文本, 先用独立的 tone tokenizer 单次分词, 该分词器与全局 jieba 隔离, 领域词注入不会污染其他阶段; 六部词典共享同一份分词结果, 保证跨词典可比。随后进入语言学规则状态机: 顺序遍历词元序列, 同时维护否定窗口剩余长度、程度副词倍率、转折激活标志三个状态变量, 句末标点会重置全部句法级状态, 修饰效果不跨句串味。当词元命中 loughran 词表时, 其基础极性分值先按否定窗口翻号 —— 处于否定窗口内的正面词被翻转为负向 —— 再乘以程度副词倍率与转折加权; 后两类规则只缩放幅度、不改变符号, 因而对计数归侧唯一有影响的语言学规则是否定翻号。最终带符号分值严格大于零的命中计入 pos_count, 严格小于零的计入 neg_count; 23 个两侧保留词每次命中同时向两侧各计一次, 对净语调贡献为零但对两侧占比对称贡献。文章级比率即 pos_count 除以 n_word_tokens, 四舍五入至小数点后六位。这里须与无前缀的 pos_ratio 计数基区分: 无前缀列走六词典固定并集扫描, 本列走单一 loughran 词典扫描, 两者共用同一分母但分子来自不同词表口径。分母 n_word_tokens 采用 word-token 口径: 剔除纯标点与纯数字词元后计数, 该类被剔词元在中文财经报道里占全部物理词元的比例非可忽略且逐篇不恒定 (报道内数字与标点的使用密度因文而异), 若不剔除会因标点数字比例差异造成逐篇非均匀稀释; 该口径与 Loughran & McDonald (2011) 及 Garcia (2013) 定义的"词数占比"原始构念对齐, 也与本仓 L&M 非情感子集 frac 族的分母修复同口径, 保证同词表家族内分母可比。边界契约体现"缺失不可测"与"真实为零"的严格区分: 空文本、全空白分词结果、分母为零的纯标点或纯数字文本、以及词典文件缺失时, 本列输出 NaN 而非零 —— 零只保留给"有有效词元但无正面命中"的真实观测。面板级在 stage 40 聚合: 聚合注册表 M 段把文章级三轨比率按银行-年做简单算术均值 (聚合入口 build_aggregation_dict 生成三轨 avg_loughran_pos_ratio 各列到对应文章级源列的 mean 映射, aggregate_panel 消费), 得到 avg_loughran_pos_ratio_full、_ctx、_ss 三列, pandas 均值自动跳过 NaN 篇; 源列缺席时聚合入口自动过滤该列而不抛错。留篇门控执行 full-only 口径 (2026-06-29 变更): 一篇报道是否进入聚合宇宙只看 full 轨 LLM 验证结果 llm_verified_full 是否为真, ctx 与 ss 两轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 各轨列在该子集上照常计算。另需说明的是, 本列的单词典扫描与用于 sentiment_details 展示的固定并集 Top-20 匹配词是两条独立的扫描路径: 单词典比率只统计命中 loughran 词表的词元, 而 sentiment_details 只保留并集口径下绝对影响力最大的前二十个匹配词供人工审计, 两者互不干扰, 本列的分子不受 Top-20 截断影响。确定性来源可逐层追溯: 分词器版本冻结在 jieba 0.42.1, 词表冻结在 config/tone_dicts.json, 语言学规则为纯函数状态机无随机成分, 因而同一输入文本在任意机器上给出逐字节一致的比率, 面板重生时该列不进入需要排除的 BLAS 浮点非确定列名单。下游消费上, 本族与镜像负面族共同构成词级意见分歧指标 disag_loughran 三轨的直接输入, 该指标按 Antweiler & Frank (2004) 的经典分歧公式构造 —— 分歧等于一减去正负占比之差与正负占比之和的比值的平方、再开平方 —— 取值零表示银行-年内媒体语调完全一致, 取值一表示正负势均力敌的最大分歧; 因此本列不仅本身是一条正面密度测度, 还是媒体分歧这一独立构念的必备半成品, 缺了正面侧分歧公式无从成立。

【文献定位】
本族在三条文献脉络的交汇处。第一条是金融文本词典法的经典谱系: Loughran & McDonald (2011) 确立了领域专用词表原则并成为财务文本分析被引最多的测量工具, 其研究纲领延续至今, Loughran & McDonald (2024) 仍在用文本测度刻画企业复杂性, 说明词典与词频类简单透明测度在机器学习时代依然有独立的方法论地位; Garcia (2013) 则确立了正负极性分离进入回归的规范, 本列正是该规范在中文银行新闻语料上的逐词典实现。第二条是测量效度与方法比较脉络: van Atteveldt et al. (2021) 系统比较人工标注、众包、词典法与机器学习算法的情感测量效度, 发现词典法效度通常最低但透明性与可复现性最高, 这一结论直接支撑本仓"词典法不单用、与 LLM 三家投票和 BERT 三模型并行三角验证"的总体设计 —— 本列的价值不在单独作为最优测度, 而在提供一条完全透明、零成本、可逐词审计的基准轨; Ma, Zhang & Zhang (2025) 为中国投资者构建本土细粒度情感词典, 提示译本词典与本土构建词典可能存在覆盖差异, 是本列翻译效度局限的直接对照文献; Sun, Yuan & Xu (2025) 把词典知识注入预训练语言模型做金融情感分析, 表明词典作为先验知识与深度模型融合是当前前沿方向, 词典成分测度因而具有面向未来方法的可衔接性。第三条是银行与媒体文本的应用脉络: Hansen, McMahon & Prat (2018) 示范了计算语言学方法在央行沟通研究中的因果识别应用, 为文本测度进入严肃识别设计立标; Li, Mai, Shen & Yan (2021) 用词嵌入从文本中测量企业文化, 代表与词典法互补的机器学习测量路线, 亦是本仓 co-primary 嵌入轨的方法源头之一; Fang, Wang, Wang & Yuan (2024) 用中国媒体情感解释存款稳定性与银行系统性风险, 与本面板的银行-年媒体语调设定同域同构; Anastasiou, Katsafados & Tzomakas (2026) 用文本分析预测银行股价崩盘风险, 说明银行文本测度对尾部风险结果有预测力; Chen, Goldstein, Huang & Vashishtha (2022) 证明银行信息环境的透明度直接影响存款人行为, 为"媒体正面语调密度影响银行负债端"的经济机制提供理论支点; Piotroski, Wong & Zhang (2017) 则揭示中国企业新闻存在系统性政治偏倚, 提示中文语料中正面词汇的基线密度受媒体制度环境影响, 是解读本列水平值时必须纳入的制度背景。Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, Economic Inquiry) 构建面向经济文本的词典法情感测度并验证其效度, 与本族基于词表匹配计算正面词密度的方法学路径直接呼应, 佐证词典法在金融与经济文本情感测量中依然具有独立方法论地位。Sheetal & Aithal (2025, Procedia Computer Science) 该文把 Loughran-McDonald 词典法与 BERT 微调结合做金融新闻情感分析, 印证词典法与深度模型融合是当前前沿方向, 呼应本族作为透明词典基准轨与 LLM/BERT 三角互证的方法学定位。Chuang, He & Hu (2025, Big Data and Cognitive Computing) 该文系统比较多种词嵌入与语言模型在中文财经新闻情感分类与股价预测中的表现, 为本族词典法正面占比在中文金融新闻语域的方法学定位提供同域对照。

【识别策略定位】
本族在识别体系中的角色是机制分解测度与词典法稳健性臂, 而非任何一篇论文的主处理变量。厘清这一从属定位是正确使用本列的前提。P1 主线的 treatment primary 是 LLM 三家投票共识 llm_vote_tone_full (gpt54nano、gemini31、deepseekv4 三家多数投票产出), 词典法整体作为与 LLM、BERT 并列的第三类测量方法进入稳健性矩阵; 三类方法互为三角验证而非替代 —— LLM 是大模型判别、BERT 是微调判别、词典是词表匹配, 三者对同一情感构念给出方法学互相独立的读数, 只有当主效应在三类方法下定性一致时, 才可判定结论不被任一测量范式的特异误差 (LLM 的提示敏感、BERT 的训练域偏、词典的覆盖漏项) 单独驱动。在词典法内部, loughran 与 jiang_2021、yao_2021、bian_2021、du_2022、you_2018 共六部词典互为稳健性、不分主次, 各词典的成分测度各自 just-identified 并排进入各自的回归设定; 铁律是禁止把多部词典的同构念测度混进同一个 over-identified Hansen J 检验 —— 六词典高度相关 (固定并集口径下第六部接入前后实测 Pearson r=0.985), 混入同一工具集只会制造虚假的过度识别检验通过, 用同源工具的表面正交掩盖其实质共线。三轨维度同理: full、ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。本列在门控结构中的位置也印证其从属地位: 2026-06-29 起留篇门控为 full-only 口径, 一篇报道是否进入面板宇宙只看 full 轨 LLM 验证 llm_verified_full 是否为真, 词典法比率是在这一门控划定的留篇集上事后计算的属性测度, 不参与留篇决策本身, 因而天然落在机制/稳健性侧而非处理侧。本列的识别价值有三层: 其一, 作为极性分解成分, 它允许把任何用净语调发现的主效应拆解为正面侧与负面侧的各自贡献, 回答机制层面"效应由哪一侧驱动"的问题, 这正是 Garcia (2013) 主张正负极性分离进回归的识别理由 —— 单一净指标会让"正面信息增多"与"负面信息减少"两种经济含义相反的变动在系数上无法辨识; 其二, 与镜像负面列合成的 disag_loughran 分歧指标, 为媒体意见分散度这一独立构念提供词典法测量, 使本列同时是一条正面密度属性测度和一个独立构念的必备半成品, 缺了正面侧分歧公式无从成立; 其三, 跨词典比较时须报告标准化系数 —— 六部词典的正面词表规模差异悬殊, loughran 正面侧 1295 词的命中基率与其他词典不同, 原始系数的水平不可直接跨词典比较, 只有 z 标准化后的 β 才有跨词典可比性, 这与本仓跨 BERT 模型比较须先标准化的口径完全一致。此外, 本列不设跨词典 FWER 校正模板: 根级 rwolf 多重检验模板 (根级 27_tableA12 跨模型 FWER) 只覆盖同一构念的替代 headline 测量, 而按词典的成分测度属于规格稳健性并排, 按既定先例 (镜像政治词权重梯度、词典消融梯度、三轨/co-primary 嵌入并排) 不适用该模板; 换言之, 六词典之间报告的是稳健性一致性而非需要多重检验校正的独立假设检验族, 误套 FWER 反会把稳健性并排错当成需要控制的独立发现集。

【与相邻测度的构念区分】
本列坐落在一个测度密集的邻域, 精确区分是防止误用的关键, 逐条厘清如下。与 avg_pos_ratio 的区分是计数基: 无词典前缀的 avg_pos_ratio 用六词典固定并集词表扫描, 是跨词典综合口径, 其数值曾因第六部 L&M 词典接入而由五部基扩为六部基回溯微变 (实测 Pearson r=0.985 / 符号翻转 0.13%); 本列锁定单一 loughran 词表, 是并集口径的成分分解, 两者一综合一成分, 不可互相替代 —— codebook 发射层的六词典扩容披露正则刻意把本列前缀排除在受影响名单外, 正因为本列自诞生即单词典口径, 从未经历那次并集扩容的回溯微变, 而是 provenance 另标的新增列。与 loughran_tone 及其面板聚合的区分是归一化方式与值域: tone 分值是带语言学规则加权后的净分值除以加权幅度绝对值之和, 自归一化到正负一区间, 度量语调的方向与强度; 本列分母是全文词元数, 度量正面词汇在文本中的密度, 两者一个回答"报道口径偏正还是偏负", 一个回答"正面词占了全文多大篇幅", 构念维度正交, 可同时进入同一回归而不构成冗余共线。与 loughran_score 及 loughran_score_negonly 等 score 族的区分是量纲与消融谱系: score 族是带符号的加权净分, negonly 是只保留否定规则、近似 L&M 原版纯计数 baseline 的消融臂, 规则消融梯子 (raw/negonly/degonly/advonly/negdeg/negadv/degadv 七变体) 只对 score 族物化, 比率族刻意不设消融孪生以防列数爆炸; 使用者若需纯计数基准应参照 negonly 谱系的 score 列而非本列。与 avg_loughran_neg_ratio 是严格镜像关系, 分母相同、分子分别取两侧计数, 23 个跨类保留词对两侧对称各计一次、对本列与镜像列同时贡献而对净语调贡献为零, 规范用法是成对进入同一回归实现极性分离。与 uncert_frac、litig_frac、constr_frac、modal_strong_frac、modal_weak_frac、complexity_frac 六个 L&M 非情感子集占比的区分是词表类别: 它们取自同一部 L&M 词表的不确定性、诉讼、约束、情态、复杂性等非极性类别 (源词典八类中六类为非极性主题类), 与正负情感类互斥, 分母同口径但构念完全不同, 绝不可当作情感强弱测度使用。与 msent 计数型净情感的区分是谱系与口径: msent 走固定并集词表的净负占比计数谱系, 本列是单词典单侧占比。与 washing_ratio_loughran、disag_loughran、loughran_idf 等 loughran 派生族的区分是构念: 它们分别度量套稿相似度、正负意见分歧、逆文档频率加权语调, 与本列的正面密度构念各异, 只是共享同一 loughran 词表来源。与 LLM 及 BERT 语调族的区分是测量方法类别: 后两者是模型判别, 本列是词表匹配, 三类方法互为三角验证而非替代。最后须澄清两处易混的梯子归属: du_2022 词典独有的政治词权重梯子 (polw00/05/10) 与本列无关, loughran 词表不含政治正面词类别, 不存在 polw 变体, 引用时勿混淆; 同理 co-primary 双轨嵌入 (canonical Qwen3-Embedding-8B 4096 维 / text-embedding-3-large 3072 维) 是语义嵌入测度, 与本列的词表匹配测度无任何接线关系, 换嵌入模型时本列零误改。规则消融梯子只对 score 族物化变体、不落到比率族, 本列不带任何消融后缀。

【已知局限与稳健性梯子】
第一, 翻译效度局限。本词典是英文 10-K 词表的中文主译本 (取自 Loughran-McDonald Master Dictionary 带情感标签的载荷词, 经财经译者金融义优先逐词中译并做本土近义词扩展、多轮对抗审计定稿), 从美国财务披露语域迁移到中文新闻语域存在双重构念漂移风险: 一是词义在翻译中的偏移, 二是语域从年报披露到新闻报道的偏移。Ma, Zhang & Zhang (2025) 为中国投资者构建的本土细粒度情感词典表明译本与本土构建词表覆盖面可能系统性不同, 是本列翻译效度局限的直接对照文献。本仓的对冲设计是六词典互稳梯子: loughran 与五部本土中文金融词典并排, 主结论若在六部词典下定性一致, 则不由任何单一词表的构造选择驱动; 词典间一致性可用 Krippendorff α 与 Cohen κ 度量, 但报告前须先把标签重映射为非负码以避免缺标哨兵与负面标签冲突。第二, 框架级词类局限。源词典系 L&M 框架派生并沿用其八类情感体系, 因而继承若干框架级特性 (多为 L&M 原典或中译固有、非扩展引入): 会计中性程序词 (减值、拨备、计提、核销、敞口) 被计入消极类, 强情态类含极性优越性形容词, 约束性类混入条件依存副词, 复杂性类含交易/组织结构名词; 这些特性对负面侧影响更大, 但也提示正面侧的"改善/增长"类词与中性业绩陈述边界可能模糊。词典采二元收录、未分级情感强度, 因此本列度量的是正面词出现的频密, 不区分"略有改善"与"大幅飙升"的强度差异; 源词典披露建议做"剔除会计程序词"重算的稳健性检验, 但该检验落在 score 族而非比率族。第三, 规则耦合局限。分子 pos_count 在全语言学规则下计数, 否定翻号会改变命中的归侧 (处于否定窗口内的正面词被翻转记入负侧), 因此本列是语境校正后的正面密度, 不等于原版 L&M 的纯词频计数; 程度副词与转折规则只缩放幅度不改符号, 对归侧无影响。使用者若需纯计数基准应参照 negonly 谱系的 score 列而非本列。第四, 分词匹配局限。源词典建议用 Aho-Corasick 整词匹配以规避 jieba 裸切切碎 ≥4 字复合词造成的漏匹配, 而本列文章级走的是冻结版 tone tokenizer 单次分词后逐词元匹配, 复合金融词在分词粒度下的整词命中率是已知的系统性衰减源, 可能对长词密度低估。第五, 制度环境局限。Piotroski, Wong & Zhang (2017) 证明的中文企业新闻政治偏倚意味着正面词基线密度含制度成分, 银行与年份固定效应可吸收跨行、跨年的水平差异, 但解释仍应聚焦组内变异而非跨行水平横比。第六, 测量效度局限。van Atteveldt et al. (2021) 系统比较人工标注、众包、词典、机器学习四类方法, 发现词典法效度通常最低但透明性与可复现性最高, 因此本列的定位不是最优测度, 而是完全透明、零 API 成本、可逐词审计的基准轨, 与 LLM 三家、BERT 三模型三角互证。第七, 稀疏性。loughran 正面侧仅 1295 词而负面侧 3729 词, 正面命中相对稀疏, 报道数少的银行-年格上均值波动大; 开发环境两年窗口 (早期试跑 T=2) 下的退化属预期, 生产环境十九年全量语料 (T=19) 下缓解。第八, 门控口径。full-only 留篇门控使各轨聚合宇宙统一锚定 full 轨验证结果, 这是 2026-06-29 已披露的口径变更, 造成的 ctx/ss 样本收缩非缺陷。稳健性梯子全景: 三轨梯子、六词典梯子相互正交、不做交叉展开 (避免列数组合爆炸); 每一梯子内部各臂各自 just-identified 并排、互为稳健性不分主次, 任何情况下禁止把梯子各臂混进同一 over-identified Hansen J。

## VAR: avg_loughran_pos_ratio_full

【变体差分】
本列为家族 canonical 列, tier=core, 签核依据为类别六扩围第一批: 词典法 loughran 正面成分占比的 canonical full 轨, 是 L&M 语调分解成分在面板上的旗舰载体。full 轨文本 = 标题 prepend 加全文正文, 即对报道全文逐词元扫描后的正面密度, 不做任何实体邻近截断, 覆盖信息量最大、对报道整体叙事基调的代表性最强, 是三轨中唯一以完整报道体作为测量文本的一条。本列与留篇门控天然同轨自洽: 2026-06-29 起留篇门控为 full-only 口径, 一篇报道进入面板聚合宇宙的唯一判据是 full 轨 LLM 验证 llm_verified_full 通过, 因此本列的测量文本与门控判据作用于同一条轨道, 不存在 ctx、ss 两轨那种"门控看 full、测量看别轨"的条件截断结构, 解释上最干净, 也是把本列而非 ctx/ss 列列为 canonical 与 core 的直接理由。计算口径承家族公式: 分子为全文 word-token 中命中 loughran 词表且经否定翻号后仍为正向的词元数, 23 个两侧保留词双侧同计, 分子严格用带符号分值大于零的判据而非裸匹配数, 因而已内含否定语境校正; 分母为剔除纯标点与纯数字后的 word-token 数; 文章级四舍五入至六位小数, 银行-年内对留篇文章取简单算术均值, NaN 篇自动跳过。作为 core 列, 其规范用法有三: 一是与镜像列 avg_loughran_neg_ratio_full 成对进入回归, 实现 Garcia (2013) 意义上的极性分离设定, 单独放正面侧而遗漏负面侧会重新引入对冲掩蔽, 使系数难以解释; 二是作为 LLM 主测度 llm_vote_tone_full 的词典法机制佐证 —— 当 LLM 净语调效应显著时, 用本列检验效应是否由正面信息密度侧驱动, 提供一条完全透明、可逐词审计、零 API 成本的独立证据链; 三是作为 disag_loughran_full 的正面侧输入, 与负面侧共同支撑媒体意见分歧构念。与家族内其他两列的关系遵守铁律: full、ctx、ss 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 同理与其余五部词典的同名成分列并排时亦禁混同一 Hansen J。跨词典使用时须报告标准化系数, 因 loughran 正面词表 1295 词的规模与其他五部词典差异悬殊, 原始系数水平不可比, 只有 z 标准化后的 β 才有跨词典解释力。在解读水平值时须结合固定效应设定: 中文新闻的正面词基线密度含制度成分 (Piotroski, Wong & Zhang, 2017 揭示的政治偏倚), 加入银行与年份固定效应后, 本列吸收掉跨行、跨年的水平差异, 有意义的变异是同一家银行在时间维度上的正面密度波动, 因而本列适合进入以组内变异为识别来源的面板设定, 而不宜用于跨行水平横比。与三轨中 ctx、ss 两条聚焦轨相比, 本列覆盖全文、词元基数最大, 抽样方差最小, 是三轨里最稳的一条, 这也是把它而非窗口截断轨设为旗舰的又一原因; 反过来说, 若研究关切的是"正面措辞是否精准指向目标银行"这类归因问题, 则应改用 ctx 轨并把本列作为覆盖面参照。确定性上, 本列的整条计算链零 LLM 调用、零 API 成本, 分词器冻结在 jieba 0.42.1、词表冻结在 config/tone_dicts.json、语言学规则为纯函数状态机无随机成分, 因而同一 full 轨文本在任意机器上给出逐字节一致的比率, 面板重生时本列不进入需要排除的 BLAS 浮点非确定列名单, 是列哈希可对 golden 的一条确定性锚。下游上, 本列是 disag_loughran_full 的正面侧直接输入 (分歧公式 disag = 根号下 (一减去正负占比之差与正负占比之和之比的平方)), 与镜像负面列 avg_loughran_neg_ratio_full 共同支撑 full 轨媒体意见分歧构念, 缺本列该指标无从成立。须再次强调 23 个跨类保留词在本轨的行为: 它们命中时向正负两侧各计一次, 对本列与镜像列同时贡献正的密度、对 loughran_tone 的净分贡献为零, 因而本列的水平不应被误读为纯单极信号, 而是含这批双义词对称贡献的正面词元密度。Stata 导出标签为 loughran 正面占比 full 轨, codebook 发射层按列名命中 L&M 来源规则, 自动附 Loughran-McDonald 词表 provenance 引文与来源备注, 与 .dta 标签同源一致, 不落自动推断空引文占位。

## VAR: avg_loughran_pos_ratio_ctx

【变体差分】
本列为 ctx 轨变体, tier=standard, 与 canonical full 列的唯一差分维度是测量文本轨道: ctx 轨文本 = 标题 prepend 加目标银行实体上下文窗口, 即只保留报道中围绕目标银行实体出现位置的邻近文本片段, 剔除与该银行无直接关联的段落。构念含义随之收窄: full 列度量整篇报道的正面词密度, 本列度量与目标银行直接相邻语境中的正面词密度, 对"一篇报道提及多家银行、正面措辞却只针对其中一家"的归因噪声有天然免疫力, 是降噪聚焦轨。代价是文本变短后 word-token 基数下降, 比率的抽样方差增大, 且实体窗口截断可能切断否定词与情感词的跨段依赖, 使语言学规则的作用范围与 full 轨不完全一致。行宇宙口径须注意: 留篇门控为 full-only, 本列的行宇宙是 full 留篇集的子集, 属 conditional-on-full 测度轨, 文章级 ctx 比率在该子集上照常计算, 银行-年均值自动跳过 NaN 篇。规范用法是作为 full 列的稳健性臂: 两轨各自 just-identified 并排进各自回归、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 两轨系数的方向一致性是结论不被无关段落语调污染的证据, 系数差异本身则可解读为报道内语境异质性的描述性信号, 不作因果解释。计算口径与 full 列完全一致 (分子为经否定翻号后仍为正向的 loughran 命中词元数, 分母为剔纯标点纯数字后的 word-token 数, 23 个跨类保留词双侧同计, 文章级六位小数、银行-年简单均值跳 NaN 篇), 差异仅在测量文本轨道。与其余五部词典的同名 ctx 成分列并排时同样禁混同一 over-identified Hansen J, 跨词典比较须报告 z 标准化系数。

## VAR: avg_loughran_pos_ratio_ss

【变体差分】
本列为 ss 轨变体, tier=standard, 差分维度同为文本轨道, 且是三轨中口径最窄的一条: ss 轨文本 = 标题 prepend 加"目标银行与金融科技词在同一句内共现"的句子及其前后各一句的窗口, 窗口半径由 config/filtering.yaml 的 ss_sentence_radius 键控制, 默认为一, 注意该键与 stage 13 共现硬过滤的 sentence_radius 是两个不同配置键。共现判定采用不对称口径: 银行侧经否定与短名过滤, 金融科技侧为裸 AC 自动机 607 词匹配。因此本列度量的是报道中银行与金科议题绑定最紧的句群里的正面词密度, 构念上最贴近"银行金科叙事本身的正面基调"。回退语义是本列解释的关键: 当一篇留篇文章内不存在银行与金科的同句共现时, content_ss 镜像 ctx 的回退逻辑而回退为全文 body 且 ss_is_fallback 置真, 该篇仍进入均值且与其他轨共享 n_articles 分母 —— 高回退率的银行-年格上, 本列实际混合了严格同句口径与全文口径; 极端情形下若金科词表整体缺失, 全部行回退, 本列优雅降级为近似全文口径而非报错。行宇宙同为 conditional-on-full 子集。规范用法与 ctx 列对称: 作为 full 列的最窄稳健性臂, 三轨各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J; 解读时宜同时报告回退率背景, 避免把回退混合口径误读为纯同句测度。计算口径承家族公式、仅测量文本轨道最窄 (分子经否定翻号后为正向的 loughran 命中数, 分母为剔纯标点纯数字后的 word-token 数, 23 个跨类保留词双侧同计, 六位小数、银行-年简单均值跳 NaN 篇)。开发环境两年窗口下, 因共现同句样本更稀, 本列的抽样方差在三轨中最大, 高回退率格上尤须谨慎; 与其余五部词典同名 ss 列并排时同样禁混同一 over-identified Hansen J, 跨词典比较须报告 z 标准化系数。

<!-- rendered-citations:begin -->
Anastasiou, D., Katsafados, A., & Tzomakas, C. (2026). Banks' stock price crash risk prediction with textual analysis: A machine learning approach. Annals of Operations Research, 357(1), 89-111. https://doi.org/10.1007/s10479-025-06567-y
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Loughran, T., & McDonald, B. (2024). Measuring firm complexity. Journal of Financial and Quantitative Analysis, 59(6), 2487-2514. https://doi.org/10.1017/S0022109023000716
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Li, K., Mai, F., Shen, R., & Yan, X. (2021). Measuring corporate culture using machine learning. The Review of Financial Studies, 34(7), 3265-3315. https://doi.org/10.1093/rfs/hhaa079
Hansen, S., McMahon, M., & Prat, A. (2018). Transparency and deliberation within the FOMC: A computational linguistics approach. The Quarterly Journal of Economics, 133(2), 801-870. https://doi.org/10.1093/qje/qjx045
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news: The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Garcia, D. (2013). Sentiment during recessions. The Journal of Finance, 68(3), 1267-1300. https://doi.org/10.1111/jofi.12027
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? The information content of internet stock message boards. The Journal of Finance, 59(3), 1259-1294. https://doi.org/10.1111/j.1540-6261.2004.00662.x
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry. https://doi.org/10.1111/ecin.13264
Sheetal, R., & Aithal, P. K. (2025). Enhancing Financial Sentiment Analysis: Integrating the Loughran-McDonald Dictionary with BERT for Advanced Market Predictive Insights. Procedia Computer Science. https://doi.org/10.1016/j.procs.2025.04.477
Chuang, H.-M., He, H.-C., & Hu, M.-C. (2025). Chinese Financial News Analysis for Sentiment and Stock Prediction: A Comparative Framework with Language Models. Big Data and Cognitive Computing. https://doi.org/10.3390/bdcc9100263
<!-- rendered-citations:end -->
