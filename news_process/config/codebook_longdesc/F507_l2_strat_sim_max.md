---
family_id: F507
columns:
- strat_sim_max
- strat_sim_max_ctx
- strat_sim_max_ss
- strat_sim_max_w
- strat_sim_max_w_ctx
- strat_sim_max_w_ss
unit: 相似度 [-1,1] (TF-IDF 轨理论上非负向量点积 ∈ [0,1]; 实测极少数余弦截断误差可致极小负值)
formula: 'strat_sim_max = max_{j≠i} cos(v_i, v_j), 其中 v_i 为银行 i 当年报道文本经 TF-IDF 向量化后的稀疏向量; j 遍历同年度全部同业银行(不含 i 自身); 逐年独立拟合词表/IDF 权重, 不跨年汇聚'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\export.py
upstream: []
citations:
- doi: 10.1002/smj.3549
  type: journal
  authors: Su, J., Gao, X., & Tan, J.
  year: 2024
  title: 'Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment'
  venue: Strategic Management Journal
  vol: '45'
  issue: '2'
  pages_or_artno: 333-361
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: Measuring Founding Strategy
  venue: Management Science
  vol: '69'
  issue: '1'
  pages_or_artno: 101-118
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories"
  venue: Strategic Management Journal
  vol: '40'
  issue: '1'
  pages_or_artno: 3-27
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: Text-based network industries and endogenous product differentiation
  venue: Journal of Political Economy
  vol: '124'
  issue: '5'
  pages_or_artno: 1423-1465
- doi: 10.1111/jofi.12050
  type: journal
  authors: Hoberg, G., Phillips, G., & Prabhala, N.
  year: 2014
  title: Product market threats, payouts, and financial flexibility
  venue: The Journal of Finance
  vol: '69'
  issue: '1'
  pages_or_artno: 293-324
new_dois: []
---

## CORE

【构念与来源】
strat_sim_max 家族刻画银行 i 在特定年度与"最相似的那一家同业"之间的文本战略同质度, 是战略差异度 (strategic distinctiveness) 测度体系的镜像互补量: strat_diff_n5 等 N-最近邻列回答"银行 i 的报道文本与其近邻均值/分布相差多远", 而 strat_sim_max 回答一个更尖锐的问题——"银行 i 在同业集合里能找到的、语言最接近自己的那个对手, 相似到什么程度"。两者共享同一底层向量化引擎与同一逐年拟合的 TF-IDF 空间, 互为镜像但非线性可加分解 (max 算子对异常近邻高度敏感, 而 N=5 近邻均值对异常值稳健, 二者数值不可相互折算)。构念渊源直接继承文本战略距离测度传统: Hoberg & Phillips (2016) 用 10-K 产品描述文本的成对余弦相似度构造文本网络产业分类 (TNIC), 定义"竞争对手集合"为余弦相似度超过阈值的公司对; strat_sim_max 把这一逻辑收窄到"逐年最大成对相似度"这一个统计量, 直接对应 TNIC 构造过程中每家公司找到的"头号文本近邻"。方法论上还借鉴 Guzman & Li (2023) 对"创业战略"的文本测量框架——用高维稀疏文本向量表示企业战略定位, 以向量间距离/相似度代理战略趋同或分化程度。本项目的应用场景是中国银行业媒体报道文本 (而非公司自身披露的 10-K), 银行 i 当年的"文本战略画像"由该行当年全部报道文章聚合而成 (拼接后统一分词/向量化), 相似度矩阵逐年重新拟合, 不跨年汇聚, 因此严格意义上是"同业银行在媒体呈现层面的战略趋同度", 而非银行自身主动披露的战略定位——这一区分对解释系数符号至关重要: strat_sim_max 高既可能反映银行 i 与近邻确实业务趋同 (真实战略趋同), 也可能反映两行被媒体以雷同话术报道 (报道套路趋同, 即媒体侧的"套话"效应), 二者在本测度里不可分离, 需与 boilerplate 套话比率家族联合解读。

【方法学与计算】
计算管道分两步: 第一步文本向量化, 第二步逐年成对相似度矩阵取行最大值。向量化阶段, char 轨 (无 _w 后缀的三列) 使用字符 n-gram (char_wb) TF-IDF, 不依赖分词器, 对中文文本的编码噪声与分词错误更稳健, 是家族的 canonical 口径; word 轨 (_w 后缀三列) 使用 jieba 分词后的词级 TF-IDF, 自 2026-06-21 起 (fix inject-fintech-word-lda) 改用注入 1506 个金科词的独立分词器 (`_get_diff_tokenizer`), 使"金融科技""区块链"等领域复合词整词保留、不被切碎, 与 char 轨、embedding 轨的领域感知口径对齐; char 轨本身字节不受此次改动影响。char 轨与 word 轨是互为稳健性、不分主次的并排测度——两者对分词误差的敏感性方向相反 (word 轨依赖分词质量, char 轨绕过分词), 因此在回归设计中应各自独立进入模型 (just-identified 并排), 不得混入同一个 over-identified 设定 (如同一 Hansen J 检验同时用 char 与 word 两轨的相似度做过识别工具), 这与项目对三轨文本 (full/ctx/ss)、co-primary 双轨嵌入等其他梯子测度的一贯口径完全一致。第二步, 对每一年度截面, 计算全部同业银行两两之间的余弦相似度矩阵 (方阵, 对角线为自身相似度 1, 计算时剔除), 银行 i 当年的 strat_sim_max 取该行 (排除自身列) 的最大值, 即"该行当年能找到的最相似同业"的相似度。TF-IDF 轨向量为非负 (词频与逆文档频率均非负), 理论余弦值域 ∈ [0,1]; frontmatter unit 字段沿用项目对该测度族值域披露的统一惯例, 主区间标注为 [-1,1] 并附注 "TF-IDF 轨理论上非负向量点积 ∈ [0,1]"——这一并列写法既覆盖了本项目内其他共享同一相似度计算路径的 embedding 轨真实值域 [-1,1] (fix omni-g-strategic-02/03), 也不掩盖 strat_sim_max 系列自身作为 TF-IDF 轨理论值域应为 [0,1] 这一事实; frontmatter 并未将主值域改写为 [0,1], 使用者应以括注的"[0,1]"为 strat_sim_max 系列的理论口径, 主区间 [-1,1] 仅是跨轨统一标注惯例, 并注记极少数情形下浮点余弦截断误差可能产生极小负值 (数值上贴近 0, 不改变"理论非负"的构念判断)。三个文本轨道 (full/ctx/ss) 分别在各自的文本物化列 (`content_full`/`content_ctx`/`content_ss`, stage 14 `ctx_materializer` 产出) 上重跑同一套向量化-最大相似度流程: full 轨用标题+全文正文聚合; ctx 轨用标题+银行/金科实体窗口聚合; ss 轨用标题+银行∧金科同句共现窗口聚合, 若某行某年无同句共现证据则回退为全文 body (镜像 ctx 轨回退语义, 共享 `n_articles` 分母, 由 `ss_is_fallback` 指示列标记)。三轨在同一年度截面上分别独立拟合各自的 TF-IDF 词表与相似度矩阵, 因此不是同一相似度矩阵的子集运算, 而是三套完全独立的向量空间——各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。留篇口径遵循 full-only 门控 (2026-06-29 起生效): 一篇报道是否计入某银行的"当年文本战略画像", 只看 `llm_verified_full == True` 这一判据; ctx/ss 轨的行宇宙是 full 轨留篇集合的子集, 各轨在此子集上分别聚合文本、分别向量化。

【文献定位】
strat_sim_max 家族的最直接方法学出处是 Hoberg & Phillips (2016, *Journal of Political Economy*) 提出的文本网络产业分类框架——该文用公司 10-K 产品描述的成对余弦相似度构造"竞争对手邻近度", 本测度将其收窄为逐年最大值统计量, 直接对应该框架里"每家公司的头号文本近邻"这一中间产物。姊妹测度 strat_fluidity 则来自同一研究团队的 Hoberg, Phillips & Prabhala (2014, *The Journal of Finance*) 产品市场流动性构造, 与 strat_sim_max 共享同一底层向量化引擎但衡量不同统计量 (流动性衡量竞争对手集合的整体扩张速度, 而非单一最大相似度)。在"最优区分度"(optimal distinctiveness) 理论脉络上, Haans (2019, *Strategic Management Journal*) 与 Su, Gao & Tan (2024, *Strategic Management Journal*) 均以文本/类别相似度测量企业在同类竞争者中的趋同-分化取舍, 为 strat_sim_max 的经济解释 (相似度高是否等价于战略趋同抑或媒体报道套路化) 提供理论框架。分词与向量化方法学参照 Guzman & Li (2023, *Management Science*) 对创业战略的高维文本测量范式。

## VAR: strat_sim_max

【变体差分】
本列是家族的 canonical 口径: full 轨 (标题+全文正文聚合, 留篇门控 `llm_verified_full == True`) × char 级 TF-IDF (char_wb n-gram, 不依赖 jieba 分词, 对编码噪声与分词错误稳健)。计算上, 逐年在该年度全部银行的 full 轨聚合文本上拟合 TF-IDF 向量空间 (词表与 IDF 权重逐年独立重新估计, 不跨年汇聚, 避免早年词表污染晚年估计), 计算银行两两余弦相似度方阵, 取每行 (排除对角线自身) 的最大值。经济解释上, strat_sim_max 值高意味着该行当年存在一家"文本画像几乎重叠"的同业对手, 可能反映业务定位真实趋同 (如同为大力发展供应链金融的城商行), 也可能反映媒体报道的模板化雷同 (与 boilerplate 套话比率家族联合解读可分离两种机制)。作为家族基准列, 本列在回归设计中通常与 strat_sim_max_w (word 轨) 并排作互为稳健性检验, 与 strat_sim_max_ctx / strat_sim_max_ss 并排作三轨稳健性检验, 三者及 char/word 两轨的组合共四种口径互不嵌套, 各自独立进入模型设定, 不得混入同一个过识别工具变量集合。使用者若要检验"银行是否倾向于回避与最强对手在文本战略上过度趋同", 本列是首选起点, 因为它同时满足样本覆盖最全 (full 轨行宇宙最大)、方法最稳健 (char 级不受分词误差干扰) 两个条件; 其余五列均应视为对本列结论的交叉验证而非替代测度。

## VAR: strat_sim_max_ctx

【变体差分】
本列与 canonical 列的唯一差分维度是文本轨道: 使用 ctx 轨聚合文本 (标题+银行/金科实体窗口, 而非全文正文) 拟合逐年 TF-IDF 空间并取最大相似度, 向量化方法 (char 级 TF-IDF) 与 canonical 列完全一致。ctx 轨的经济含义是"聚焦于实体提及邻近上下文的战略相似度"——文本范围收窄到实体窗口后, 相似度矩阵对报道篇幅/无关段落的敏感性降低, 更贴近"报道在谈论银行做什么业务"这一核心语义, 而非全文中夹杂的行情综述、监管背景等泛化段落。行宇宙上, ctx 轨的留篇集合是 full 轨留篇集合 (`llm_verified_full == True`) 的子集, 在此子集上独立完成聚合、独立拟合词表、独立计算相似度矩阵, 不复用 full 轨的相似度矩阵做子集截取。ctx 轨与 full 轨、ss 轨三者各自 just-identified 并排, 互为稳健性、不分主次, 三轨系数应分别报告, 不得混入同一个过识别 Hansen J 设定。相较 canonical 列, 本列剔除了报道正文中与银行/金科实体无关的段落 (如宏观行情综述、监管政策背景铺垫等), 因此对"报道确实在描述该行金融科技相关业务"这一构念的测量误差理论上更小, 但代价是可用文本量缩水、逐年词表估计的样本方差相应上升, 在样本量偏小的年度 (如 dev 环境 T=2) 应格外留意估计不稳定性。

## VAR: strat_sim_max_ss

【变体差分】
本列与 canonical 列的差分维度同样是文本轨道, 采用 ss 轨聚合文本: 标题+银行∧金科词同句共现窗口 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认半径 1 句), 是三轨中对"银行与金科在同一句话里被提及"这一最严格共现判据的实现, 向量化方法仍为 char 级 TF-IDF, 与 canonical 列保持一致以保证可比性。ss 轨的回退语义镜像 ctx 轨: 若某行某年的报道中不存在银行与金科同句共现的句子, 则该篇文章的 `content_ss` 回退为全文 body (与 ctx 轨共享 `n_articles` 分母), 并由 `ss_is_fallback` 指示列标记这类回退观测, 使用者可据此判断该行当年的 ss 轨相似度是否建立在"真实同句共现文本"之上还是退化为全文近似。ss 轨的相似度矩阵同样逐年独立拟合, 行宇宙是 full 轨留篇集合的子集。ss 轨与 full 轨、ctx 轨三者互为稳健性并排关系不变, 禁止混入同一过识别设定; 在 dev 环境 T=2 小样本上, ss 轨因同句共现证据本就稀疏, 相似度矩阵易呈现更多回退观测, 生产语料 T=18 上退化程度应显著降低。本列在三轨中构念纯度最高 (要求银行与金科词严格同句共现, 判据强于 ctx 轨的实体窗口), 因此在解读"银行媒体形象与最强对手在金融科技话语上的趋同度"时最贴近字面含义, 但也正因判据严格, 使用者在联合六列比较时应优先关注 `ss_is_fallback` 比例, 比例过高的年度/银行应弱化对本列点估计的信任、转而参考 ctx 或 full 轨。

## VAR: strat_sim_max_w

【变体差分】
本列与 canonical 列的差分维度是向量化方法: 使用 jieba 分词后的词级 (word-level) TF-IDF, 而非 char 级 n-gram, 文本轨道仍为 full 轨, 与 canonical 列保持一致。自 2026-06-21 (fix inject-fintech-word-lda) 起, 全部 `_w` 后缀列 (含本列) 与全部 LDA 列改用注入 1506 个金科专有词的独立分词器 (`_get_diff_tokenizer`), 使"金融科技""区块链"等领域复合词在分词阶段被整词保留、不被拆散为单字或错误切分, 与 char 轨、embedding 轨对领域术语的处理口径趋于一致; 该次改动不影响 char 轨字节。word 轨与 char 轨是互为稳健性、不分主次的并排口径: word 轨依赖分词质量, 对新词/领域词的分词准确率敏感, 但捕捉的是"词汇层面"的战略相似度, 语义颗粒度比字符 n-gram 更接近人类阅读理解的"关键词重合"; char 轨绕过分词、对分词错误免疫, 但可能把无实际语义关联的字符片段计入相似度。回归设计中两轨应分别报告, 不作为彼此的替代品混入同一设定。从测量哲学上看, word 轨更接近人类读者对"两篇报道用词相似"的直觉判断——如果两行报道都反复出现"供应链金融""开放银行""金融科技子公司"等相同关键词, word 轨相似度会显著抬升; 而 char 轨即便用词不同、只要字符片段偶合也可能给出相近的相似度读数, 因此两轨的分歧本身也是一个值得报告的诊断信号。

## VAR: strat_sim_max_w_ctx

【变体差分】
本列同时叠加两个差分维度: 向量化方法为 word 级 TF-IDF (含 1506 金科词注入分词器) 而非 char 级, 文本轨道为 ctx 轨 (标题+实体窗口) 而非 full 轨。因此本列是"word×ctx"这一具体组合格点, 在家族六列构成的 2×3 网格 (向量化方法 {char, word} × 文本轨道 {full, ctx, ss}) 中占据独立一格。经济解释上兼具 strat_sim_max_ctx (聚焦实体邻近语境) 与 strat_sim_max_w (词汇层面相似度、领域词整词保留) 两者的性质: 既排除了全文中的无关段落, 又以分词后的词汇单元而非字符片段衡量相似度, 更贴近"两行报道用的关键词是否高度重合"这一直觉。留篇行宇宙同样是 full 轨留篇集合的子集, 逐年独立拟合 ctx 轨专属的 word 级 TF-IDF 空间。六列网格中的任意两列均可视为互为稳健性的并排口径, 不存在主次关系, 亦不得混入同一过识别设定联合估计。本列适合作为"实体聚焦+词汇颗粒度"双重收窄条件下的稳健性检验: 若某项发现在 canonical (full×char) 列上成立, 在本列上依然以相近符号和显著性重现, 说明结论不依赖于全文冗余段落或字符级噪声, 增强了对该发现属于真实语义信号而非文本预处理副产物的信心。

## VAR: strat_sim_max_w_ss

【变体差分】
本列是家族六列网格中"word×ss"这一格点: 向量化方法为 word 级 TF-IDF (1506 金科词注入分词器), 文本轨道为 ss 轨 (标题+银行∧金科同句共现窗口, 默认半径 1 句)。是六列中判据最严格 (要求银行与金科词同句出现) 且颗粒度最细 (词汇级而非字符级) 的组合, 理论上应最贴近"报道原文明确讨论该行金融科技相关业务、且用词与某同业高度重合"这一具体经济含义, 但也因此在样本稀疏时最容易触发 `ss_is_fallback` 回退 (无同句共现证据时退化为全文 word 级 TF-IDF 相似度)。分母 `n_articles` 与 ctx 轨、full 轨共享同一套留篇口径 (`llm_verified_full == True` 门控), 相似度矩阵逐年独立拟合。作为六列网格最末一格, 本列与其余五列 (char/word × full/ctx/ss 的其余五种组合) 一律互为稳健性并排关系, 使用者在解读时应联合六列比较其符号与显著性的一致性, 但不应将六列同时纳入同一回归的右端做联合识别工具。作为六个格点中判据最严、颗粒度最细的组合, 本列的点估计方差通常最大、`ss_is_fallback` 触发比例通常也最高, 建议在展示结果时随本列同时报告回退比例, 使读者能够判断本列的估计精度是否足以支撑独立结论, 抑或只宜作为其余五列结论方向一致性的补充旁证。

<!-- rendered-citations:begin -->
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance, 69(1), 293-324. https://doi.org/10.1111/jofi.12050
<!-- rendered-citations:end -->
