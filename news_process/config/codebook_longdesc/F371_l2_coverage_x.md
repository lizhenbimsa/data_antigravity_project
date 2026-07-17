---
family_id: F371
columns:
- llm_peer_coverage_iv
- llm_peer_coverage_iv_70
- llm_peer_coverage_iv_75
- llm_peer_coverage_iv_80
- llm_peer_coverage_iv_85
- llm_peer_coverage_iv_90
unit: 对数变换量 (panel 级同行声量均值, log1p 后无上界的连续量, 非归一化比率/占比, 详见 CORE)
formula: "llm_peer_coverage_iv(bank,t) = mean_over_peers( coverage(peer, t) ), peer 集合来自 llm_peer_iv.py 用 LLM 识别的产品市场竞争同行 (TNIC 式上限 10 家), coverage(peer, t) = ln_news_coverage(peer, t) = log1p(n_articles(peer, t)) 即该同行当年在语料中报道文章数的 log1p 对数变换 (encode.py 内 ln_news_coverage 字段 = np.log1p(panel[n_articles])), 是无上界的对数尺度量而非 [0,1] 归一化比率; 未做文章级 leave-out; _70/_75/_80/_85/_90 后缀 = 识别同行时使用的 LLM 相似度/置信度 cutoff c ∈ {0.70,...,0.90} 的敏感性梯子, 其余公式结构不变"
producer: pipeline\panel\llm_peer_iv.py ; pipeline\panel\export.py
upstream: []
citations:
- {doi: "10.1007/s11142-025-09892-6", type: journal, authors: "Cao, Y., Chen, L., Tucker, J. W., & Wan, C.", year: 2025, title: "Can generative AI help identify peer firms?", venue: "Review of Accounting Studies", vol: "30", issue: "4", pages_or_artno: "3344-3386"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-based network industries and endogenous product differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.1111/jofi.12094", type: journal, authors: "Leary, M. T., & Roberts, M. R.", year: 2014, title: "Do peer firms affect corporate financial policy?", venue: "The Journal of Finance", vol: "69", issue: "1", pages_or_artno: "139-178"}
- {doi: "10.2307/2298123", type: journal, authors: "Manski, C. F.", year: 1993, title: "Identification of endogenous social effects: The reflection problem", venue: "The Review of Economic Studies", vol: "60", issue: "3", pages_or_artno: "531-542"}
- {doi: "10.1017/CBO9780511614491.006", type: book, authors: "Stock, J. H., & Yogo, M.", year: 2005, title: "Testing for weak instruments in linear IV regression", venue: "Identification and Inference for Econometric Models (Cambridge University Press)", pages_or_artno: "80-108"}
- {doi: "10.1146/annurev-economics-080218-025643", type: journal, authors: "Andrews, I., Stock, J. H., & Sun, L.", year: 2019, title: "Weak instruments in instrumental variables regression: Theory and practice", venue: "Annual Review of Economics", vol: "11", pages_or_artno: "727-753"}
- {doi: "10.48550/arXiv.2504.05658", type: arxiv, authors: "Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y.", year: 2025, title: "Identification and estimation of causal peer effects using instrumental variables", venue: "arXiv"}
- doi: "10.1111/jofi.13377"
  title: "Business News and Business Cycles"
  authors: "Bybee, L., Kelly, B., Manela, A., & Xiu, D."
  year: 2024
  venue: "The Journal of Finance"
  type: "journal"
- doi: "10.2139/ssrn.5668511"
  title: "Mining Causality: AI-Assisted Search for Instrumental Variables"
  authors: "Han, S."
  year: 2025
  venue: "SSRN Working Paper"
  type: "wp"
new_dois:
  - "10.1111/jofi.13377"
  - "10.2139/ssrn.5668511"
---

## CORE

【构念与来源】
本家族 (F371) 的 6 列全部隶属 llm_peer 方法学论文的辅助工具变量族, 由 `pipeline/panel/llm_peer_iv.py` 生产、经 `pipeline/panel/export.py` 挂标签写入面板。核心构念是"同行声量" (peer coverage): 先用 LLM (Cao, Chen, Tucker & Wan, 2025, Review of Accounting Studies) 在产品市场竞争意义上为每家焦点银行识别一组文本相似的同行企业, 同行集合规模上限沿用 Hoberg & Phillips (2016, Journal of Political Economy) 提出的 TNIC ("text-based network industry classification") 标准做法, 即取"最接近的 10 家"作为同行上限; 再对每个同行在该年度语料中的报道声量取 `ln_news_coverage = log1p(n_articles)` 这一对数变换量, 取跨同行等权均值, 得到 `llm_peer_coverage_iv`。需特别澄清: 该量并非归一化到 [0,1] 的比率/占比, 而是对当年报道条数做 log1p 变换后的无上界连续量, 数值随同行当年报道条数增长而单调增大且增速递减 (log1p 平滑零值), 取值范围理论上可远超 1, 不应按"占比/概率"解读。这是一个 panel 级的、面向"该银行的同行圈子在媒体上有多热"的暴露度量, 与三家 LLM 情感投票 (`llm_vote_tone`) 或三家 BERT 情感模型完全是两回事——本族不衡量情感方向, 只衡量声量/曝光。产出的六列同属 standard tier, 互为敏感性并排, 不设主辅之分（各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 检验）。
需要特别澄清的是"IV"这个后缀的含义: 本模块同时生产 `llm_peer_tone_iv_{full,ctx,ss}` (核心工具变量, 文章级 leave-out, 三轨各自 just-identified) 与 `llm_peer_coverage_iv` (辅助工具变量, 未做文章级 leave-out, panel 级均值)。二者共享"同行圈"这一构念底座, 但用途不同: `llm_peer_tone_iv` 是拿去做第一阶段回归的工具变量本体, 而 `llm_peer_coverage_iv` 是配套的"共享报道声量"披露项——用来说明焦点银行与其同行是否经常出现在同一批报道里、从而佐证或质疑工具变量满足排除约束的合理性。换言之, coverage 族不是用来单独识别因果效应的核心 IV, 而是识别策略的辅助诊断/披露变量, 帮助读者判断 tone IV 背后"同行声量共享"渠道有多强。

【方法学与计算】
生成流程分两步。第一步是同行识别: `llm_peer_iv.py` 对每家焦点银行调用 LLM, 要求其基于产品市场竞争关系输出一份候选同行名单, 并给出置信度/相似度打分; 只保留打分超过 cutoff c 的候选, 且候选数量不超过 TNIC 惯例的 10 家上限。生产口径的默认 cutoff 未附后缀 (即 `llm_peer_coverage_iv`), 其余五列 `_70/_75/_80/_85/_90` 是同一识别流程在 c = 0.70, 0.75, 0.80, 0.85, 0.90 五个阈值下的重复运行, 构成一条阈值敏感性梯子 (与家族的 tone IV、count、peer_compete_idx 等平行变体共享同一套阈值集合, 见 `export.py` 中 `for c in [70, 75, 80, 85, 90]` 的批量列名生成)。第二步是声量聚合: 对每个进入同行集合的银行, 取其 `ln_news_coverage(peer, t) = log1p(n_articles(peer, t))` 即当年在语料中报道条数的 log1p 对数变换, 再对同行集合做等权算术平均, 得到 panel 级的 `llm_peer_coverage_iv(bank, t)`。log1p 变换的作用是压缩报道条数的右偏分布并平滑零报道情形 (log1p(0)=0), 但变换后的量仍是无上界的对数尺度声量, 不是归一化到 [0,1] 的占比/概率。
与核心 tone IV 族的关键计算差异有两点。其一, coverage 族未做文章级 leave-out: tone IV 为规避"焦点银行与同行共同出现在同一篇报道里"造成的机械相关, 会先剔除与焦点银行共同提及的文章再算同行情感均值; coverage 族则保留全部同行报道声量, 因为它本身就是用来刻画"共享报道声量有多大"这件事的诊断量, 不需要、也不应该做 leave-out (leave-out 反而会把待测的共享效应本身剔除掉)。其二, coverage 族是 panel 级 (bank × year) 的均值统计量, 不像 tone IV 的三轨 full/ctx/ss 那样区分文本窗口, 因为声量统计的对象是文章计数而非文本内容, 没有全文/实体窗口/同句窗口之分。
识别策略上, 本族的因果论证依据 Manski (1993, The Review of Economic Studies) 提出的"反射问题" (reflection problem): 同期同行结果与焦点银行结果同时决定, 简单相关无法区分同行影响焦点银行还是反之。llm_peer_iv.py 的应对策略是使用滞后一期同行特质冲击 (体现在 tone IV 的 lag 处理与 leave-out 设计上), 而 coverage 族作为该策略的伴随诊断项, 其数值大小直接反映了"同行圈子被媒体同时提及的密集程度"——数值越高, 意味着焦点银行与其同行越容易共享同一批报道来源, tone IV 排除约束 (同行报道冲击只通过同行渠道而非直接机制影响焦点银行结果) 的可信度就越需要审慎讨论, 这也是 Leary & Roberts (2014, The Journal of Finance) 指出的同行均值 IV 的经典局限——同行结果均值本身很难完全满足排除约束, 需要额外的机制说明或稳健性检验来支撑。

【文献定位】
本族方法论直接继承三条文献脉络。识别同行主体用 LLM 而非传统的行业代码或专利文本相似度, 依据 Cao, Chen, Tucker & Wan (2025, Review of Accounting Studies) 关于生成式 AI 识别产品市场同行的研究, 该文发现 LLM 输出的同行集合在预测未来业绩共动性上优于传统 SIC/NAICS 分类; 同行集合规模的 TNIC 上限设定则参照 Hoberg & Phillips (2016, Journal of Political Economy) 的文本网络行业分类方法论。工具变量设计的反射问题规避思路来自 Manski (1993, The Review of Economic Studies) 的经典论证, 而对同行均值型 IV 排除约束局限性的自觉披露则遵循 Leary & Roberts (2014, The Journal of Finance) 在公司金融同行效应文献中的做法。弱工具诊断与推断层面, Stock & Yogo (2005) 与 Andrews, Stock & Sun (2019, Annual Review of Economics) 提供了本族及其姊妹 tone IV 族在下游 2SLS 应用时应参照的弱工具判定标准; Luo, Shuai, Zhang, Li & He (2025, arXiv) 关于工具变量估计因果同行效应的最新方法论进展, 为本族"LLM 识别同行 + 声量/情感双轨 IV"这一组合设计提供了当代文献坐标。整体上, 本族六列服务于同一个方法学定位: 它们不是任何一篇主线论文 (P1-P5) 的处理变量或结果变量, 而是 `llm_peer` 方法学 paper 模块用来支撑 tone IV 有效性论证的辅助测度族。此外, Bybee, Kelly, Manela & Xiu (2024, The Journal of Finance) 用大规模文本分析度量媒体新闻报道声量并验证其宏观与公司层面信息含量, 为本族以 log1p(报道条数) 刻画同行媒体声量的做法提供了新闻覆盖度量效度的当代文献支撑; Han (2025, SSRN Working Paper) 提出用大语言模型辅助搜寻满足排除约束的工具变量, 与本族用 LLM 识别产品市场同行圈子并构造声量/情感辅助工具变量的设计思路属同一方法学前沿脉络。

## VAR: llm_peer_coverage_iv

【变体差分】
本列是家族的生产 canonical 变体, 对应 LLM 同行识别阈值的默认 cutoff (与 `llm_peer_tone_iv_full/ctx/ss` 等核心 IV 使用相同的默认识别口径, 未附数字后缀)。计算上不做文章级 leave-out, 直接对识别出的全部同行 (至多 10 家, 满足相似度打分门槛的银行) 的当年报道声量取等权算术平均。定位是"LLM-Peer 等权声量均值 IV", 属辅助 IV/披露项而非核心识别工具变量, 用于向读者展示焦点银行与其同行圈子共享媒体报道声量的基线程度, 是判断 tone IV 排除约束合理性时的首要参照点; 该列不区分 full/ctx/ss 文本轨道, 因为其输入是文章计数级别的声量统计而非情感或语义内容, 与三轨情感/属性测度分属两套完全不同的量纲体系, 不应误当作又一条文本窗口轨道去解读。
在下游使用上, 该列常与 `llm_peer_n_effective` (实际进入 tone IV 均值的面板内同行数) 与 `llm_peer_queried` (该 bank-year 是否成功完成 LLM 查证) 联合解读: 若某一 bank-year 的 `llm_peer_coverage_iv` 数值偏高但 `llm_peer_n_effective` 很小, 说明声量集中在少数几个高曝光同行身上, 排除约束的机制解释需要更谨慎; 若 `llm_peer_queried` 为 0 或对应同行集合为空, 该列取值应结合缺失/退化情形审慎解读, 不宜直接与其余 bank-year 做横向数值比较。作为生产口径, 本列在论文正文与稳健性附录中同时承担"基线披露"与"阈值敏感性梯子锚点"两重角色, 是 `_70` 至 `_90` 五档敏感性变体共同比对的参照原点。

## VAR: llm_peer_coverage_iv_70

【变体差分】
与 canonical 列的唯一区别在于同行识别阶段使用的 LLM 相似度/置信度 cutoff c = 0.70——五个阈值敏感性变体中门槛最低、因而纳入同行集合的候选企业最多、平均意义上同行圈子最"宽"的一档。该列与 `_75/_80/_85/_90` 及无后缀 canonical 列共同构成一条阈值梯子, 五档 (加 canonical 共六档) 各自独立计算、各自 just-identified, 互为稳健性并排、不分主次, 不得混入同一 over-identified Hansen J 检验; 用途是检验"同行声量共享"这一诊断结论是否对 LLM 识别阈值的具体取值敏感——若 c=0.70 与 c=0.90 两档给出的声量共享强度方向一致, 则增强 tone IV 排除约束讨论的稳健性, 反之则提示结论对阈值选择敏感需在稳健性部分披露。
c=0.70 是梯子里唯一的"宽松端"锚点: 由于相似度门槛低, LLM 更容易把边缘相关、甚至只是同处金融/银行大类但产品市场竞争关系较弱的企业也纳入同行集合, 因而同行数量普遍逼近 TNIC 上限 10 家。这一档的诊断价值在于压力测试——若把同行圈子人为放宽后, 声量共享强度仍与更严格阈值下的结论方向一致, 说明该结论不依赖于对"同行"的从严定义; 若放宽后声量共享明显被稀释或反转, 则提示焦点银行的报道声量共享主要来自少数高相似度核心竞争对手, 而非整个宽泛意义上的同业圈子, 此时应以更高 cutoff 档 (如 `_85`/`_90`) 的结果作为主要讨论依据, 本列则作为下界稳健性佐证保留在附录中。

## VAR: llm_peer_coverage_iv_75

【变体差分】
同上阈值梯子的第二档, cutoff c = 0.75, 计算逻辑与 canonical 列完全一致 (等权声量均值、无文章级 leave-out), 仅同行识别阶段的相似度门槛不同, 纳入同行圈子的候选企业数量介于 c=0.70 与 c=0.80 之间。该列与家族内其余五个阈值变体互为稳健性并排, 不设主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J 检验; 其存在价值在于提供比 c=0.70 更保守、比 c=0.80 更宽松的中间锚点, 支撑阈值敏感性曲线的平滑性检查。
在稳健性叙事里, c=0.75 一般不单独作为讨论焦点, 而是与相邻档位 (c=0.70、c=0.80) 一起构成阈值敏感性曲线在"较宽松"区间的三点插值。若三档 (0.70/0.75/0.80) 之间声量共享强度呈现单调、平滑的变化趋势 (而非剧烈跳变), 可视为同行识别流程对阈值扰动不敏感的证据, 支持 tone IV 排除约束讨论不依赖于 cutoff 的精确取值; 若在 0.70 到 0.80 之间出现明显非单调或跳变, 则提示 LLM 同行识别结果本身存在阈值附近的不稳定区域, 需要在方法学附录中单列讨论, 并建议下游引用者优先参照更远离该不稳定区间的档位 (如 c=0.85 或 c=0.90)。该列与其姊妹梯子 `llm_peer_tone_iv_full_75`/`llm_peer_tone_iv_ctx_75`/`llm_peer_count_75`/`peer_compete_idx_75` 共享同一 c=0.75 识别批次的同行集合, 因此在方法学上是同一次 LLM 调用产物在不同下游聚合口径上的投影, 但作为面板列各自独立估计、互不构成对方的先验或约束。

## VAR: llm_peer_coverage_iv_80

【变体差分】
阈值梯子的第三档, cutoff c = 0.80, 与家族内其余变体共享同一计算流程 (LLM 同行识别 → log1p 报道条数对数变换 → 等权均值, 无 leave-out)。此档在 `export.py` 中同时也是 `peer_compete_idx` (Peer Competition Index) 无后缀 canonical 版本所采用的默认阈值 (0.80), 意味着该 cutoff 是整个 llm_peer 方法学族里被当作事实上"中位/推荐"取值使用最广的一档; 因此本列在阈值梯子内部具有一定的参照锚点意义, 但在统计推断层面仍与其余四档及 canonical 列同为 just-identified 并排关系, 不构成对其余变体的统计优先级, 禁止混入同一 over-identified Hansen J 检验。
之所以 0.80 在方法学族内被反复复用 (既出现在 coverage 梯子, 也出现在 tone IV、count、peer_compete_idx 三条并行梯子里), 是因为生产流程在批量运行 LLM 同行识别时选择了一个跨多个下游用途都表现稳定的相似度门槛, 便于横向比较不同测度族在同一阈值下的行为。但这只是工程实现上的复用便利, 不改变本列在统计意义上与 `_70/_75/_85/_90` 及无后缀 canonical 列完全平行、各自独立估计的地位——读者不应因为 0.80 在其他测度族中也是 canonical 默认值, 就误以为它在 coverage 梯子内部具有额外的统计权重或应被优先采信。若需要选取单一档位做正文主表展示 (而非把六档全部列入附录), 撰稿人可参考 0.80 在 `peer_compete_idx` 中的默认地位作为工程上的一致性理由, 但须在文中明确声明这只是展示便利, 统计推断结论应以全部六档 (canonical 与 `_70/_75/_85/_90`) 的方向一致性为准, 而非仅凭 0.80 单档下结论。

## VAR: llm_peer_coverage_iv_85

【变体差分】
阈值梯子的第四档, cutoff c = 0.85, 计算口径与 canonical 列一致, 仅同行识别相似度门槛更严格, 纳入同行圈子的候选企业数量比 c=0.80 更少、"同行"定义更收窄向高相似度核心竞争对手集中。该列与家族内其余变体各自独立估计、互为稳健性并排、不分主次, 禁止混入同一 over-identified Hansen J; 用于检验"收窄同行定义至更强竞争关系"是否改变声量共享强度的结论方向, 是阈值敏感性曲线在高端一侧的关键锚点。
c=0.85 与紧邻的 c=0.90 共同构成梯子的"严格端"配对, 二者的对比价值在于检验结论是否对"极端从严"的同行定义敏感: 若焦点银行在 c=0.85 下的同行圈子已经收窄到仅剩少数几家高度相似的核心竞争对手, 但声量共享强度依然与更宽松阈值下的结论方向一致, 则说明这一诊断结论具有相当的构念稳定性, 不是宽泛同行定义下的统计假象; 反之, 若严格端阈值下同行数量过少导致均值估计噪声明显放大 (可结合 `llm_peer_n_effective` 判断), 则应在稳健性附录中提示读者该档结果的样本支持有限, 并以中间档位 (0.75-0.80) 的结果作为主要参照。

## VAR: llm_peer_coverage_iv_90

【变体差分】
阈值梯子的最高端一档, cutoff c = 0.90, 计算逻辑同 canonical 列, 但同行识别门槛最严, 平均意义上纳入的同行数量最少、同行圈子最"窄"、要求 LLM 给出的产品市场竞争相似度打分最高。该列是阈值敏感性梯子的上界锚点, 与 `_70/_75/_80/_85` 及 canonical 六档共同构成完整的敏感性谱系, 各档各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 检验; 若声量共享结论在 c=0.90 (最严格同行定义) 下依然与 c=0.70 (最宽松同行定义) 方向一致, 则是对 tone IV 排除约束讨论稳健性的最强支撑之一。
由于门槛最高, 部分焦点银行在 c=0.90 下可能只剩个位数甚至零同行通过筛选, 此时应结合 `llm_peer_n_effective`(实际进入均值的面板内同行数) 与 `llm_peer_queried`(该 bank-year 是否成功完成 LLM 查证并可返回空集合) 两个诊断列联合判读: 若某 bank-year 在本列取值缺失或为退化边界值, 大概率是因为严格阈值下同行集合为空而非数据本身缺失, 不应与其他 bank-year 的正常观测值混为一谈直接纳入回归。作为敏感性梯子六档中样本支持最薄弱的一档, `llm_peer_coverage_iv_90` 在正文中通常只作为"极端严格定义下结论仍然成立"的补充证据出现, 不建议单独作为主要稳健性检验依据, 而应与 `_85` 一并解读、互相印证严格端的结论稳定性。

<!-- rendered-citations:begin -->
Cao, Y., Chen, L., Tucker, J. W., & Wan, C. (2025). Can generative AI help identify peer firms? Review of Accounting Studies, 30(4), 3344-3386. https://doi.org/10.1007/s11142-025-09892-6
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Manski, C. F. (1993). Identification of endogenous social effects: The reflection problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Stock, J. H., & Yogo, M. (2005). Testing for weak instruments in linear IV regression. Identification and Inference for Econometric Models (Cambridge University Press). https://doi.org/10.1017/CBO9780511614491.006
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.05658
Bybee, L., Kelly, B., Manela, A., & Xiu, D. (2024). Business News and Business Cycles. The Journal of Finance. https://doi.org/10.1111/jofi.13377
Han, S. (2025). Mining Causality: AI-Assisted Search for Instrumental Variables. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5668511
<!-- rendered-citations:end -->
