---
family_id: F345
columns:
- jiang_2021_cater_b_ctx
- jiang_2021_cater_b_full
- jiang_2021_cater_b_ss
unit: 无量纲得分差 (词典语调分 减 BERT 净语调分, 值域理论上约 [-2, 2])
formula: 'jiang_2021_cater_b_{track} = jiang_2021_tone_{track} - (bert_avg_pos_{track} - bert_avg_neg_{track})'
producer: pipeline\panel\runner.py (8d 算法迎合度 Algorithmic Catering 区块, 单词典 vs 综合深层模型分支)
upstream:
- jiang_2021_tone_full
- jiang_2021_tone_ctx
- jiang_2021_tone_ss
- bert_avg_pos_full
- bert_avg_pos_ctx
- bert_avg_pos_ss
- bert_avg_neg_full
- bert_avg_neg_ctx
- bert_avg_neg_ss
citations:
- doi: 10.1093/rfs/hhad021
  type: journal
  authors: Cao, S., Jiang, W., Yang, B., & Zhang, A. L.
  year: 2023
  title: "How to talk when a machine is listening: Corporate disclosure in the age of AI"
  venue: The Review of Financial Studies
  vol: '36'
  issue: '9'
  pages_or_artno: 3603-3642
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: '21'
  issue: '4'
  pages_or_artno: 1323-1344
- doi: "10.1080/21697213.2024.2337262"
  type: "journal"
  authors: "Meng, Q., Du, X., & Gong, X."
  year: 2024
  title: "Does operational disclosure curb textual tone manipulation by corporate management?"
  venue: "China Journal of Accounting Studies"
  vol: "12"
  issue: "2"
  pages_or_artno: "247-275"
- doi: "10.1515/econ-2022-0129"
  type: "journal"
  authors: "Wang, H."
  year: 2024
  title: "Media Tone and Earnings Management before the Earnings Announcement: Evidence from China"
  venue: "Economics"
  vol: "18"
  issue: "1"
  pages_or_artno: "20220129"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"词典语调"与"深度学习语调"之间的系统性偏离, 学术上称为"算法迎合度"(algorithmic catering)。其识别依据是 Cao, Jiang, Yang & Zhang (2023, Review of Financial Studies) 提出的洞见: 企业和媒体的文本撰写者若知道市场存在依赖简单规则词典的自动化文本分析工具, 会策略性地在措辞上"迎合"这些工具(例如堆砌词典正面词但整体语义并不真正正面), 从而人为拉高词典打分而不改变文本的真实经济含义。词典法(逐词匹配、加总计分)与深度学习法(整句语境编码、端到端判别)对这种策略性措辞的敏感度不同——词典法更容易被"迎合", 深度学习法(尤其是在大规模语料上微调过的领域专用 BERT)相对更难被简单的关键词堆砌操纵。二者打分之差因此构成一个可观测的"迎合度"代理变量: 差值越大, 说明该篇报道的词典打分相对于模型打分"虚高"得越多, 潜在迎合(或至少是词典法系统性偏误)的可能性越大。
本家族三列均取自 F345 canonical 词典 jiang_2021(姜富伟、孟令超、唐国豪 2021, 载《经济学(季刊)》, 基于中国财经媒体语料构建的中文金融情感词典, 是本项目六部情感词典之一)与 BERT 两个三分类模型(finbert_cn、fin_sent_zh; 二分类 finbert2 因概率单纯形不兼容被结构性排除, 详见【方法学与计算】)综合净语调的逐篇差值, 归属"B 组"(_cater_b 后缀), 与不带 _b 后缀的 _cater 组(词典 vs LLM 三家投票)在同一 8d 区块内并列产出, 二者互为稳健性、不分主次, 分别捕捉"词典 vs 深度学习(BERT)"与"词典 vs 大语言模型(LLM)"两条独立的迎合度测量路径。
【方法学与计算】
公式为 jiang_2021_cater_b_{track} = jiang_2021_tone_{track} - (bert_avg_pos_{track} - bert_avg_neg_{track})。被减数 jiang_2021_tone_{track} 是 jiang_2021 词典在该轨道上对逐篇文章计算的语调分(词典正面词计数减负面词计数并按语言学规则调整后归一化得到的连续分); 减数 (bert_avg_pos_{track} - bert_avg_neg_{track}) 是 BERT 三模型中 finbert_cn 与 fin_sent_zh 两个三分类模型(THREE_CLASS_MODELS)在该轨道上输出的正类概率均值减负类概率均值, 构成一个"BERT 综合净语调"参照基准, 数值落在约 [-1, 1] 区间(两个三分类模型 signed net_tone 的均值)。finbert2 是二分类模型, 其 pos/neg/neu 概率不构成合法的三分类概率单纯形, 结构性地不参与 bert_avg_pos/bert_avg_neg 的聚合域(pipeline\panel\geography.py 8d 前置聚合逻辑), 这与"本地部署缺失"无关, 是设计上的永久排除、与 finbert2 是否具备本地权重文件无关。因此本家族差值的真实构念是"词典 vs 两个三分类 BERT 模型综合"而非"词典 vs 三个 BERT 模型综合", finbert2 自身的 signed net_tone 应参照 F345 之外的 per-model BERT 分布形状指标单独查看, 不进入本家族的减数。两个分量在计算前均已各自完成归一化, 相减得到的差值本身即为迎阶度代理, 数值符号具有直接经济含义: 正值表示词典打分高于 BERT 判断(词典"过于乐观", 潜在迎合词典侧); 负值表示词典打分低于 BERT 判断(词典"过于悲观"或 BERT 判断更乐观); 绝对值越大表示两法分歧越大。该指标在 pipeline\panel\runner.py 的 8d "算法迎合度(Algorithmic Catering)"区块中于面板导出阶段(而非文章级阶段)逐轨道计算, 属于面板层的派生指标(non-additive, 二阶差分构念), 不落文章级 parquet, 只在导出面板时现算现出。
计算严格遵循三轨并列铁律: full(标题+正文全文)、ctx(标题+实体窗口)、ss(标题+银行∧金科同句±N窗)三条轨道各自独立地计算 jiang_2021_tone 与 BERT 净语调再相减, 三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定。ss 轨道回退语义镜像 ctx: 当某篇文章不存在银行∧金科词同句共现窗口时, content_ss 回退为全文正文(与 content_full 相同文本), ss_is_fallback 标记为真, 该情形下 jiang_2021_cater_b_ss 实质上退化为在全文文本上计算的差值, 与 jiang_2021_cater_b_full 高度重合, 分析时应结合 ss_is_fallback 覆盖率解读。留篇门控口径为 full-only(2026-06-29 起): 一篇报道是否计入"银行金科报道"样本只看 llm_verified_full, ctx/ss 轨道的本指标是在 full 留篇集合的子集行上计算的条件测度/稳健性轨, 不单独扩展行宇宙。
【文献定位】
Cao, Jiang, Yang & Zhang (2023, RFS) 首次系统化提出并检验了"算法读者(algorithmic readers)"对企业信息披露文本策略的影响, 发现随着自动化文本分析工具的普及, 企业倾向于在措辞上迎合这些工具的打分机制, 该研究是本家族"词典 vs 深度模型差值即迎合度代理"这一构念设计的直接理论依据。Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习方法与词典方法在披露语调测度上的系统性差异, 为"词典法与深度学习法存在结构性偏离而非纯噪声"这一前提提供了跨方法比较的实证支撑, 是本项目"多方法互为稳健性"设计哲学的方法论先例。Du, Huang, Wermers & Wu (2022, Review of Finance) 构建了另一部具有语言与领域专属性的中文金融情感词典, 强调通用词典移植到中文金融语境时的系统性偏误问题, 从"词典本身可能存在系统性偏差"的角度佐证了本家族用深度模型作为参照基准来量化偏离的合理性。姜富伟等(2021, 《经济学(季刊)》)是本家族被减数词典 jiang_2021 的原始构建文献, 基于中国财经媒体文本样本, 采用有监督机器学习方法结合人工标注扩展出面向中国资本市场语境的情感词表, 是本项目六部中文金融情感词典中唯一原生针对中国媒体语料构建的一部, 在方法学上与本项目"多词典并排、互为稳健性"的设计一脉相承。 近期两项中国情境的实证研究可进一步补强本家族在被减数一侧与构念前提上的外部效度。Meng、Du 与 Gong (2024) 以中国上市公司年报文本测量管理层的文本语调操纵(textual tone manipulation), 即语调正面程度超出基本面可解释的部分, 并检验经营性披露对该操纵行为的约束作用; 其"语调减基准语调"的差分/残差思路与本家族"词典语调减 BERT 综合净语调"在测度形态上同属"以语调相对某一参照基准的偏离量化策略性书写"一类, 且语调来源同为中文金融文本的词典化打分, 从而为 Cao, Jiang, Yang & Zhang (2023) 源自美国披露场景的迎合机制补上了一项中国语境下的同域行为学前提。迁移边界须如实标明: 该文的参照基准是基本面回归的拟合值(残差法)而非第二套测度引擎, 文本为企业自述年报、观测单位为公司-年, 原文既未使用深层模型对照, 亦未涉及象征-实质二分, 因此它只锚定本家族被减数与"语调偏离可作为策略性书写信号"这一构念前提, 不能被援引为本家族以 BERT 三分类模型综合净语调作减数的方法学依据。Wang (2024) 用中文媒体报道语调测度检验其与盈余管理的关系, 提供了"中文媒体报道语调经词典类方法可测且具经济含义"的同域应用证据, 与 jiang_2021 面向媒体语料的词表构建定位相互呼应, 支撑本家族被减数所依托的中文媒体语调测度传统; 但该文仅使用单臂词典语调, 无 BERT/LLM 任何对照臂, 故只能锚定本家族差值的词典端而不能锚定模型端, 其报道对象为中国上市公司一般财经报道(非银行×金融科技共现报道)、分析层级为公司-事件窗而非 bank-year, 载文期刊层级一般, 引用时应按此降级口径理解, 不宜据以推断本家族差值模型端的构念效度。
## VAR: jiang_2021_cater_b_full

【变体差分】
本列取 full 轨道(标题+正文全文)上的 jiang_2021 词典语调与 BERT 两个三分类模型综合净语调之差, 即 jiang_2021_tone_full - (bert_avg_pos_full - bert_avg_neg_full)。full 轨道以整篇报道全文(含标题前置拼接)为扫描范围, 不做实体窗口截断或同句限定, 是本项目三轨中信息覆盖面最宽、噪声也相对更高的一支——词典逐词扫描全文时更容易被文中与目标银行、金科关系无关的段落(如行业背景介绍、宏观数据引用、其他公司案例)带入额外的正负面词汇计数, 而 BERT 模型基于全文语境编码同样会吸收这些无关段落信息, 因此该列捕捉的是"整篇报道尺度上"词典法与深度模型法对语调判断的系统性分歧, 更适合作为文章整体基调层面的迎合度代理。
按项目留篇门控口径(2026-06-29 起 full-only), full 轨道是决定一篇报道是否计入"银行金科报道"样本宇宙的门控轨道(llm_verified_full == True 才留篇), 因此本列在三轨中拥有最完整、无条件约束的行覆盖, 不存在因实体窗口缺失或同句共现缺失导致的回退问题, 是三轨中样本量最大、缺失率最低的一支, 也是研究者在报告主结果时最常引用的参照轨道。与 jiang_2021_cater_full(词典 vs LLM 三家投票版本, 不带 _b 后缀)相比, 本列换用的参照基准是 BERT 两个三分类模型的综合净语调而非 LLM 投票, 二者对"深度模型"的操作化定义不同(BERT 编码器判别式打分 vs LLM 生成式多数投票), 在同一 full 轨道内互为稳健性、不分主次, 不应混入同一过度识别设定进行联合估计。使用时应注意, bert_avg_pos_full/bert_avg_neg_full 的聚合域恒为 finbert_cn 与 fin_sent_zh 两个三分类模型, finbert2(二分类, 需本地私有微调模型, 由 FINBERT2_MODEL_DIR 环境变量控制)因其 pos/neg/neu 概率不构成合法单纯形而被结构性排除于该聚合之外, 这是设计常态而非"本地部署缺失时才降级"的临时兜底——即便 finbert2 本地权重齐备、正常产出, 本列减数依然只取另两个三分类模型的均值, finbert2 本身概率是否可用不改变本列的聚合域。建议结合 BERT 分布形状五族(finbert2 per-model 列)单独核查 finbert2 的语调判断, 不应默认其已计入本列差值。

## VAR: jiang_2021_cater_b_ctx

【变体差分】
本列取 ctx 轨道(标题+目标银行实体窗口)上的差值, 即 jiang_2021_tone_ctx - (bert_avg_pos_ctx - bert_avg_neg_ctx)。ctx 轨道将扫描文本限定在标题与目标银行实体周边的窗口片段内(而非全文), 排除了与该银行无直接关联的段落, 因此本列捕捉的是"聚焦到目标银行本身"的词典法与深度模型法分歧, 相对 full 轨道噪声更低、构念上更贴近"报道对该特定银行的语调迎合度"而非"整篇报道的总体语调迎合度"。
在留篇门控切换为 full-only(2026-06-29)之后, ctx 轨道降级为 conditional-on-full 的测度/稳健性轨: 本列的行宇宙是 full 轨道留篇集合的子集(即仅在 llm_verified_full == True 的文章上计算), 而非独立扩展行宇宙, 与 jiang_2021_cater_b_full 共享同一批文章样本、仅测量口径(扫描窗口)不同, 二者互为稳健性并排比较, 不分主次。ctx 与 full、ss 三者禁止混入同一过度识别的 Hansen J 联合估计, 应各自 just-identified 独立估计后横向比较系数稳定性。本列与不带 _b 后缀的 jiang_2021_cater_ctx(参照 LLM 三家投票)在同一 ctx 窗口口径下并列存在, 提供"BERT 判别式模型"与"LLM 生成式投票"两种深度模型参照基准的交叉稳健性; 与家族内 jiang_2021_cater_b_full/jiang_2021_cater_b_ss 相比, 本列的差异纯粹来自扫描窗口(实体窗 vs 全文 vs 同句)而非参照模型本身, 是三轨梯子中"中间粒度"的一支。

## VAR: jiang_2021_cater_b_ss

【变体差分】
本列取 ss 轨道(标题+银行∧金科同句±N窗)上的差值, 即 jiang_2021_tone_ss - (bert_avg_pos_ss - bert_avg_neg_ss)。ss 轨道是三轨中扫描范围最窄、构念最精确的一支: 只在目标银行实体与金科相关词汇同句共现(或按 config/filtering.yaml::context_window.ss_sentence_radius 配置的 ±N 句窗口内共现, 默认半径为 1)的片段上计算词典与 BERT 打分, 直接锚定"该句话既谈银行又谈金科"这一最贴合本项目"银行-金科互动"研究主旨的语义单元, 是本家族在构念效度上最严格、但样本覆盖面也最窄的一支。
ss 轨道的回退语义严格镜像 ctx: 当某篇文章不存在银行∧金科同句(或窗口内)共现片段时, content_ss 优雅回退为全文正文(与 content_full 相同文本), ss_is_fallback 标记置真, 此时本列在数值上会与 jiang_2021_cater_b_full 高度重合甚至完全相等; 若上游 FINTECH_AC 为 None(金科词典构建失败), 则全体样本的 ss_is_fallback 一律为真, 本列整体退化为 full 口径的镜像副本。同 ctx 一样, ss 轨道在 full-only 门控切换后属于 conditional-on-full 测度, 行宇宙是 full 留篇集合的子集, 与 jiang_2021_cater_b_full、jiang_2021_cater_b_ctx 三者各自 just-identified 并排, 互为稳健性、不分主次, 严禁三轨混入同一过度识别的 Hansen J 联合估计。使用时应结合 ss_is_fallback 覆盖率解读该列的有效样本占比——若某银行年份的报道中同句共现比例很低, 本列的信息增量相对 full 轨道会非常有限, 此时更适合作为构念效度检验(而非主结果测度)使用。

<!-- rendered-citations:begin -->
Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening: Corporate disclosure in the age of AI. The Review of Financial Studies, 36(9), 3603-3642. https://doi.org/10.1093/rfs/hhad021
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Meng, Q., Du, X., & Gong, X. (2024). Does operational disclosure curb textual tone manipulation by corporate management?. China Journal of Accounting Studies, 12(2), 247-275. https://doi.org/10.1080/21697213.2024.2337262
Wang, H. (2024). Media Tone and Earnings Management before the Earnings Announcement: Evidence from China. Economics, 18(1), 20220129. https://doi.org/10.1515/econ-2022-0129
<!-- rendered-citations:end -->
