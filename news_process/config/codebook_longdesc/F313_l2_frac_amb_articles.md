---
family_id: F313
columns:
- frac_amb_articles_ctx
- frac_amb_articles_full
- frac_amb_articles_ss
unit: 银行-年内文章占比 (article fraction, [0,1] ∪ NaN)
formula: 'count(i ∣ frac_ambiguous_{trk}_i ≥ median_amb_d0_{trk}) / n_clarity_valid_{trk} (trk ∈ {full, ctx, ss}; 分子分母同域, 均取该轨 clarity 非缺失文章 i; 门槛 = n_clarity_valid_{trk} ≥ 2, 否则整格 NaN; 该轨 median_amb_d0_{trk} 为 NaN 时同样整格 NaN; 此处 n_clarity_valid_{trk} ≠ 物理 n_articles)'
producer: pipeline\panel\encode_collab.py::aggregate_clarity_panel ; pipeline\panel\codebook.py
upstream:
- 22_tone_words (clarity_score_{trk} / frac_ambiguous_{trk} / frac_definite_{trk} 三轨词典扫描)
- 40_panel_export_main (aggregate_clarity_panel 聚合入口; D0 冻结中位数 sidecar 传入)
citations:
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: Annual report readability, tone ambiguity, and the cost of borrowing
  venue: Journal of Financial and Quantitative Analysis
  vol: '52'
  issue: '2'
  pages_or_artno: 811-836
- doi: 10.1111/j.1540-6261.2008.01314.x
  type: journal
  authors: Epstein, L. G., & Schneider, M.
  year: 2008
  title: Ambiguity, information quality, and asset pricing
  venue: The Journal of Finance
  vol: '63'
  issue: '1'
  pages_or_artno: 197-228
- doi: 10.1257/aer.104.8.2368
  type: journal
  authors: Ilut, C. L., & Schneider, M.
  year: 2014
  title: Ambiguous business cycles
  venue: American Economic Review
  vol: '104'
  issue: '8'
  pages_or_artno: 2368-2399
- doi: 10.2307/1884324
  type: journal
  authors: Ellsberg, D.
  year: 1961
  title: Risk, ambiguity, and the Savage axioms
  venue: The Quarterly Journal of Economics
  vol: '75'
  issue: '4'
  pages_or_artno: 643-669
- doi: 10.2139/ssrn.5337268
  type: wp
  authors: Wei, X., & Zhang, Q.
  year: 2025
  title: Narrative ambiguity matters
  venue: SSRN Working Paper No. 5337268
- doi: 10.1093/rfs/hhac058
  type: journal
  authors: Cookson, J. A., Engelberg, J. E., & Mullins, W.
  year: 2023
  title: Echo chambers
  venue: The Review of Financial Studies
  vol: '36'
  issue: '2'
  pages_or_artno: 450-500
new_dois: []
---

## CORE

【构念与来源】
F313 家族刻画银行-年层面「报道语气/措辞含糊」这一构念在文章占比意义上的强度: frac_amb_articles_{full,ctx,ss} 度量的是某银行在某年份被点名报道的全部文章中, 有多大比例落在"高含糊度"一侧, 而非含糊程度本身的连续均值。该构念的经济学根基来自 Ellsberg (1961) 对模糊性 (ambiguity) 与风险 (risk) 的经典区分——前者指概率本身不确定, 后者指结果概率已知但结果不确定——以及 Epstein & Schneider (2008) 将信息质量的模糊性引入资产定价的理论框架: 当披露文本本身语义含糊, 理性投资者会对其内含信息的可靠性打折扣, 进而要求更高的风险补偿。落到文本层面, Ertugrul et al. (2017, JFQA) 首次系统证明年报语气模糊度 (tone ambiguity) 会独立于可读性显著推高银行借款成本, 这构成了本家族在"新闻报道→融资成本"这一识别链条中的直接文献锚点——若媒体对银行的报道本身措辞含糊, 市场同样可能因信息噪声升高而要求更高定价, 逻辑与年报语气模糊度对借贷成本的作用机制平行, 只是信息来源从企业自我披露换成了第三方媒体转译。宏观层面, Ilut & Schneider (2014, AER) 进一步说明模糊性冲击 (ambiguity shocks) 可作为独立于传统 TFP 冲击的商业周期驱动力, 为本家族的银行-年时间序列波动提供了更宏大的理论参照。frac_amb_articles 与本家族的姊妹连续测度 mean_clarity_score / mean_frac_definite (归属另一家族) 互补: 后者报告的是加权平均连续分数, 本家族报告的是二值化之后的"越过中位数门槛的文章占比", 二者共同构成一套"连续尺度均值 + 离散化覆盖率"并置的稳健性组合——既看连续尺度均值, 也看离散化的"高模糊文章"覆盖率, 防止极端值单方向拉高均值而掩盖分布形状。

【方法学与计算】
上游 stage 22 (tone_words) 对每篇文章的三轨文本 (content_full/content_ctx/content_ss) 各自独立跑一次词典扫描, 产出 article 层 frac_definite_{trk} 与 frac_ambiguous_{trk} 两个连续比例——前者由 definite_set (388 词) 命中数除以该轨有效 word-token 数得到, 后者由 ambiguous_set (178 词) 命中数除以同一分母得到; 两个词表直接取自域外中文金融情感词典 You et al. (2018, hhx055) 的 Panel C (确定类, definite) 与 Panel D (模糊类, ambiguous) 两个互补类别, 源码逐词表注明出处, 各自独立计数、互不共用命中集合, frac_ambiguous_{trk} 本身即为本家族聚合门槛所依赖的连续基础量。该词典来源目前未收入本家族结构化 citations 白名单池 (DOI 需另经白名单核验后补录), 此处以作者年份形式据实标注方法学溯源, 不代表已完成正式引文条目登记。stage 40 的 aggregate_clarity_panel (encode_collab.py) 在聚合到 bank-year panel 时, 先用 D0 冻结全样本中位数 median_amb_d0_{trk} 作为二值化门槛——冻结中位数经 sidecar 在生产首跑时算定并持久化, 而非每次聚合临时计算, 保证跨批次跑同一门槛值不漂移; 随后对每个 bank-year 单元计数 frac_ambiguous_{trk}_i ≥ median_amb_d0_{trk} 的文章数, 除以该单元下该轨 clarity 非缺失的文章数 n_clarity_valid_{trk} (而非全部 n_articles)。这一分母口径是 2026-06-11 的一次修订结果: 空文本或零 token 文章在 tone_words 阶段会被显式标记 NaN, 早期版本若仍把这些文章计入物理分母会造成系统性下偏 (分子不变而分母偏大), 修订后分子分母同域, 消除了这一偏误来源。同时设有 n_clarity_valid_{trk} ≥ 2 的门槛: 样本量过小 (0 或 1 篇有效文章) 的 bank-year 输出 NaN 而非假零, 防止把"没有可靠估计"误标为"零模糊", 这是本项目一贯坚持的"宁缺勿伪零"底线; 若该轨 D0 中位数本身为 NaN (整轨全样本无效), 同样传导为 NaN。full 与 ctx 是硬必需轨——任一缺失, 整个聚合函数优雅返回空结果并跳过; ss 轨作为加性可选轨, 缺失时仅退化为双轨 (full+ctx) 聚合, 不阻塞主流程, 这一降级逻辑与项目内其他情感族 ss 轨的处理方式完全一致。

【文献定位】
本家族的三轨设计并非 lexical clarity 的孤立创新, 而是承接项目内"情感/文本测度族统一走三轨"的既定架构决策——full=标题+正文全文、ctx=标题+实体邻近窗口、ss=标题+银行∧金科词同句共现窗口 (含句子半径参数)——将其套用到 clarity 构念上。三轨并排各自独立测算、跨窗口比对以排除单一文本截取方式驱动结果的一般性做法, 是本项目文本测度族的既定架构选择, 与信息环境文献中"信息来源结构会系统性影响信号解读"这一更宽泛的问题意识相呼应——Cookson, Engelberg & Mullins (2023, Review of Financial Studies) 研究的是投资者社交网络中因关注对象同质化而形成的"回声室"效应, 其实证对象是 StockTwits 论坛的社交关注结构而非文本窗口稳健性方法本身; 该文与本家族的关联仅在于二者共同提示"文本/信息呈现方式的差异可能改变市场参与者对同一底层信号的解读", 而非该文提供了三轨窗口设计的方法论模板, 本家族三轨稳健性检验的直接方法论依据仍是项目内部既有的三轨架构决策。就近年模糊度测量文献而言, Wei & Zhang (2025, SSRN) 的"叙事模糊性" (narrative ambiguity) 工作稿延续了 Ertugrul et al. (2017) 一脉对文本模糊性经济后果的兴趣, 关注点从年报扩展到更广义的企业叙事文本, 这与本家族把模糊度测量对象从企业年报进一步外推到第三方媒体报道的思路方向一致, 均是在拓展"文本模糊性"这一构念的应用场域, 而非改变其定义内核。

三轨 (full/ctx/ss) 属于项目铁律所定义的规格并排稳健性设计: 三者各自独立按自身分布计算 D0 冻结中位数并各自 just-identified 聚合, 互为稳健性检验、不分主次, 严禁在同一 over-identified Hansen J 检验中把三轨的 frac_amb_articles 同时作为工具变量或联立回归量混用。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在银行∧金科词同句共现窗口时, 该文章的 content_ss 退化为全文 body 且 ss_is_fallback 置 True (与 ctx 共享 n_articles 分母口径); 若 FINTECH_AC 词典未加载, 则 *_is_fallback 全部置 True, 整条流水线优雅降级而非报错。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇文章是否被计入"银行金科报道"样本只看 llm_verified_full 这一门控, ctx/ss 轨的 clarity 测度是在 full 轨确定的留篇行宇宙子集上按各自轨条件计算的稳健性/条件测度, 而非独立扩大或收缩样本框; 本家族三列共享同一行宇宙, 差异仅在文本窗口与各自门槛值。

## VAR: frac_amb_articles_ctx

【变体差分】
本列是三轨中的 ctx 轨: 分子文章的 frac_ambiguous_ctx_i 由 stage 22 基于 content_ctx (标题+银行/金科实体邻近窗口, 而非全文正文) 独立跑一遍 ambiguous_set (178 词) 词典扫描得到, 门槛值 median_amb_d0_ctx 是 ctx 轨自身样本分布的冻结中位数, 与 full 轨的门槛值 median_amb_d0 相互独立、不共用同一数值。这意味着即便同一篇文章在 full 轨与 ctx 轨下的原始 frac_ambiguous 数值相同, 也可能因两轨各自的中位数门槛不同而被判定为"过线"或"未过线"两种不同结果——两轨门槛不可互相替代或交叉比对绝对水平, 只能各自在自身轨内部做跨银行/跨年比较。分母为该轨自身的 n_clarity_valid_ctx (ctx 轨 clarity 非缺失文章数), 而非借用 full 轨的分母, 严格逐轨对齐分子分母的域。ctx 文本相较 full 通常明显更短 (实体邻近窗口截取而非全文), 这意味着 ctx 轨的模糊/确定词命中密度天然与 full 轨不完全可比, 二者应作为互为稳健性的并列观测使用, 不应视为彼此的替代或加权修正版本, 更不可在同一识别策略的 over-identified 设定中同时作为工具变量或控制变量简单相加。当上游 clarity_*_ctx 列因历史 parquet 版本缺失时, 本列在该次聚合中不产出 (整体聚合函数按硬必需轨处理 full/ctx, 缺失即整体跳过, 与 ss 轨的加性可选降级逻辑不同)。

## VAR: frac_amb_articles_full

【变体差分】
本列是三轨中的 canonical 主轨: 分子文章的 frac_ambiguous_full_i 基于 content_full (标题+全文正文) 计算, 门槛值 median_amb_d0_full (即家族 frontmatter 公式中不带后缀的 median_amb_d0) 由该轨全样本冻结中位数给出, 这一冻结值同时也是本项目大多数下游论文模块 (如与 LLM substance 测度做 HTMT 判别效度检验、以及涉及 clarity 的 identification 模板) 默认引用的锚点门槛。作为留篇门控的口径来源轨, full 轨的行宇宙 (llm_verified_full == True 的文章集合) 是 ctx/ss 两轨聚合时共享的行宇宙上界——ctx/ss 轨的 clarity 测度是在 full 轨已确定"这是一篇银行金科报道"的行子集上, 按各自轨的文本与门槛条件计算, 而不会引入 full 轨判定之外的新增文章。full 轨文本长度最长, 覆盖信息量最全, 因此其 frac_ambiguous_full 的分子分母域也最宽——只要该 bank-year 存在 ≥2 篇经 clarity 有效扫描的文章即可出值, 无需额外依赖实体窗口或同句共现条件是否满足, 这是它作为三轨中默认参照系的技术基础, 但这不意味着它在构念上优先于 ctx/ss 两个稳健性轨, 三者仍是并排关系, 严禁把三轨同时塞进同一 over-identified Hansen J 检验。在跨论文模块的实际使用中, full 轨往往被优先纳入 headline 回归规格, 而 ctx/ss 则作为附表稳健性并排呈现, 这一取舍纯属工程与叙事上的便利性安排, 不代表 full 轨在识别策略或测度效度上天然优于另外两轨——三者共享同一构念定义、同一冻结中位数二值化方法论, 差异仅体现在文本截取窗口与各自门槛数值上。读者在解读 frac_amb_articles_full 时应留意其分母 n_clarity_valid_full 与整篇 n_articles 未必相等 (空文本或零 token 文章不计入), 与 ctx/ss 两轨的分母口径原则一致但各自数值独立核算, 三列不应做算术层面的直接相减或比率运算。

## VAR: frac_amb_articles_ss

【变体差分】
本列是三轨中的 ss (same-sentence) 轨: 分子文章的 frac_ambiguous_ss_i 基于 content_ss (标题+目标银行与金科词严格同句共现窗口, 半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认1) 计算, 门槛值 median_amb_d0_ss 是 ss 轨自身样本的冻结中位数, 与 full/ctx 两轨各自独立、互不通用。ss 轨在架构上属于"情感/文本测度族才配拥有的第三轨"——它并非对全部三轨家族的通用扩展, 而是本项目特意为语义/情感类测度 (clarity 归属其中) 额外增设的最严格窗口: 只有当银行实体与金科词确实出现在同一句子内, 才会截取该句子 (含标题) 作为扫描文本; 若某篇文章不存在这种严格同句共现, content_ss 回退为全文 body 且 ss_is_fallback 标记为 True, 该回退语义完全镜像 ctx 轨的回退处理, 并共享同一个 n_articles 分母口径约定。ss 轨作为聚合函数中的加性可选轨, 其存在与否不影响 full/ctx 两个硬必需轨的正常产出: 若上游 parquet 版本中不含 clarity_*_ss 相关列 (例如旧批次数据), aggregate_clarity_panel 会优雅跳过 ss 轨聚合而不报错、不阻塞整体 clarity panel 输出, 仅使本列本身在该次运行结果中缺失。由于 ss 轨窗口最窄 (通常仅一到两句话), 其 n_clarity_valid_ss ≥ 2 门槛比 full/ctx 更容易触发 NaN (小样本银行-年在严格同句共现条件下有效文章数不足), 在 T 较短的开发/试跑样本上零方差或大面积 NaN 属预期退化, 不代表测度失效, 生产全量语料上样本量更充裕后该退化会显著缓解。

<!-- rendered-citations:begin -->
Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. Journal of Financial and Quantitative Analysis, 52(2), 811-836. https://doi.org/10.1017/S0022109017000187
Epstein, L. G., & Schneider, M. (2008). Ambiguity, information quality, and asset pricing. The Journal of Finance, 63(1), 197-228. https://doi.org/10.1111/j.1540-6261.2008.01314.x
Ilut, C. L., & Schneider, M. (2014). Ambiguous business cycles. American Economic Review, 104(8), 2368-2399. https://doi.org/10.1257/aer.104.8.2368
Ellsberg, D. (1961). Risk, ambiguity, and the Savage axioms. The Quarterly Journal of Economics, 75(4), 643-669. https://doi.org/10.2307/1884324
Wei, X., & Zhang, Q. (2025). Narrative ambiguity matters. SSRN Working Paper No. 5337268 [Working Paper]. https://doi.org/10.2139/ssrn.5337268
Cookson, J. A., Engelberg, J. E., & Mullins, W. (2023). Echo chambers. The Review of Financial Studies, 36(2), 450-500. https://doi.org/10.1093/rfs/hhac058
<!-- rendered-citations:end -->
