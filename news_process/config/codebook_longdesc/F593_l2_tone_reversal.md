---
family_id: F593
columns:
- tone_reversal_ctx
- tone_reversal_full
- tone_reversal_ss
unit: 语调反转差分 (连续, 理论范围约 [-2,2]; 由三分类共识语调 llm_vote_tone 逐年一阶差分得到, bank-year 面板层级, 无需再聚合)
formula: 'tone_reversal{track} = llm_vote_tone{track}_t - llm_vote_tone{track}_{t-1}, 其中 llm_vote_tone{track}_{t-1} = panel.groupby(target_bank)[llm_vote_tone{track}].shift(1) (按 target_bank 分组、按 year 排序后的一阶滞后); track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\runner.py (计算; L1695-L1711 区块 (i) 情感滞后与反转效应) ; pipeline\panel\export.py (Stata 变量标签写入; L926-927)
upstream:
- llm_vote_tone_full
- llm_vote_tone_ctx
- llm_vote_tone_ss
citations:
- doi: 10.1093/rfs/hhu072
  type: journal
  authors: Da, Z.; Engelberg, J.; Gao, P.
  year: 2015
  title: The sum of all FEARS investor sentiment and asset prices
  venue: The Review of Financial Studies
  vol: '28'
  issue: '1'
  pages_or_artno: 1-32
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, Paul C.
  year: 2007
  title: 'Giving Content to Investor Sentiment: The Role of Media in the Stock Market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H.; Sudhof, M.; Wilson, D. J.
  year: 2022
  title: Measuring news sentiment
  venue: Journal of Econometrics
  vol: '228'
  issue: '2'
  pages_or_artno: 221-243
- doi: 10.1016/j.econlet.2025.112803
  type: journal
  authors: Aksoy-Yurdagul, D.; Buchner, A.; Zareei, A.
  year: 2026
  title: 'The persistence of news sentiment: Implications for return predictability'
  venue: Economics Letters
  vol: '260'
  pages_or_artno: Article 112803
- doi: "10.1016/j.bir.2026.100863"
  type: "journal"
  authors: "Pham, H."
  year: 2026
  title: "From ESG noise to firm-specific risk: Adverse ESG sentiment trajectories and idiosyncratic volatility"
  venue: "Borsa Istanbul Review"
  pages_or_artno: "100863"
- doi: "10.1016/j.jfs.2026.101538"
  type: "journal"
  authors: "Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S."
  year: 2026
  title: "Does media sentiment influence bank supervision?"
  venue: "Journal of Financial Stability"
  vol: "84"
  pages_or_artno: "101538"
new_dois: []
---

## CORE

【构念与来源】
tone_reversal 度量的是同一家银行的媒体语调在相邻两个年份之间的一阶变化, 即"今年语调减去去年语调"。它不直接测量语调水平本身, 而是测量语调的时序方向性转折——语调是从上一年的负面转向今年的正面 (差分为正), 还是从上一年的正面转向今年的负面 (差分为负), 抑或延续同一方向 (差分接近 0 或与前值同号)。构念动机来自行为金融学的情绪—反转假说: Da, Engelberg & Gao (2015) 用搜索型情绪指数 FEARS 证明投资者情绪的极端读数会在随后的短窗口内预测收益反转 (情绪推高时价格短期内回落、情绪压低时价格短期内反弹), 即情绪型信号本身携带均值回归的时序结构而非单纯的噪声游走; Tetlock (2007) 进一步确立媒体语调本身是可计量、可预测未来结果的信息载体, 而非噪声。将两者结合到银行—年份面板语境下, tone_reversal 提供了一个直接的经验度量: 若某银行经历了极端负面报道年份 (如监管处罚、挤兑传闻、高管丑闻), 随后年份语调机械性回摆 (mean-reversion) 或因基本面真实改善而回摆的幅度有多大, 是研究媒体情绪动态学、传播的信息衰减、以及叙事驱动型信贷成本冲击持续性的核心中间变量。上游直接输入是 stage 21 三家 LLM (gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 多数投票产出的三分类共识语调 `llm_vote_tone{track}` (与嵌入模型无关, 是纯粹的语调分类模型), tone_reversal 是对该列做的面板内纵向差分派生, 不涉及任何新的 LLM 调用或额外付费。

【方法学与计算】
计算发生在 `pipeline/panel/runner.py` 的区块 (i) "情感滞后与反转效应"。首先面板按 `target_bank`、`year` 排序, 保证 groupby-shift 操作在正确的时间轴上进行; 随后对三条文本轨道 (`_full`/`_ctx`/`_ss`) 循环, 对每条轨道生成滞后列 `llm_vote_tone{track}_lag1 = panel.groupby('target_bank')[tone].shift(1)`, 再取当期与滞后期之差 `tone_reversal{track} = llm_vote_tone{track} - llm_vote_tone{track}_lag1`。由于上游 `balance_panel()` 已确保面板是银行×年份的完全笛卡尔积 (无缺行的平衡面板), `shift(1)` 严格对应"上一个日历年", 不会因为面板中偶发缺行而错误地跳到更早的年份。首年 (面板样本期第一年) 没有可用的滞后值, `tone_reversal{track}` 依设计取 NaN, 这是预期的边界行为而非缺陷。三分类共识语调 `llm_vote_tone{track}` 本身取值集合近似 {-1, 0, +1} (负面/中性/正面, 由三家 LLM 多数表决产生, 详见 F1xx 段 llm_vote_tone 家族长文), 因此 tone_reversal 的理论取值范围约为 [-2, +2]: 值为 +2 表示银行语调从"最负面"完全反转到"最正面", 值为 -2 表示反向的坍塌式转折, 值为 0 表示语调水平在两年间保持不变 (但不代表期间没有波动, 期间波动由同一区块生成的姊妹变量 `tone_volatility{track}`——按银行分组的 3 年窗滚动标准差——单独刻画, 二者在构念上正交: tone_reversal 是端点差, tone_volatility 是路径方差)。列本身不做任何截尾 (winsorize) 或标准化, 是原始差分值, 供下游模板视需要自行标准化或分箱。

【文献定位】
本变量的方法学谱系横跨两条文献脉络。第一条是资产定价中的情绪—反转假说: Da, Engelberg & Gao (2015) 的经典发现是投资者情绪指数的极端读数在随后短窗口内系统性地预测收益反转, 隐含的机制是市场参与者 (含媒体叙事者) 对情绪化信息赋予过高权重而后逐步修正; 本变量将这一"修正"逻辑从投资者情绪指数迁移到媒体语调序列本身, 直接检验语调轨迹本身是否呈现均值回归模式, 而非绕道通过股价间接推断。第二条是媒体情绪度量与其经济后果的文献: Tetlock (2007) 证明报纸语调的高频波动含有可预测股票收益的信息, 后续 Shapiro, Sudhof & Wilson (2022) 用经济学专属词典构造的新闻情绪指数进一步验证了语调序列的持续性 (persistence) 与预测力可以脱离单纯的极性计数, Aksoy-Yurdagul, Buchner & Zareei (2026) 的近期研究直接聚焦"新闻情绪的持久性" (persistence of news sentiment) 对未来收益可预测性的含义, 与 tone_reversal 捕捉的"情绪不持久 (即反转)"是同一构念空间的对偶面: 若某银行—年份的 tone_reversal 幅度大, 意味着该期语调持久性低; 若 tone_reversal 长期接近 0 而语调水平本身持续偏离基准, 则指向语调具有较强的路径依赖或结构性偏移而非噪声驱动的临时性冲击。三轨 (full/ctx/ss) 并列计算是本项目情感测度体系的通用设计: full=标题+全文正文, ctx=标题+银行实体窗口, ss=标题+银行∧金科同句 (±1 句窗, 无共现则回退为镜像 ctx 语义的全文, 由 `ss_is_fallback` 标记, 与 n_articles 共享分母)。三条轨道在文献定位上互为稳健性检验、不分主次: 若同一银行—年份在 full 与 ctx/ss 轨道上算出的 tone_reversal 方向与量级高度一致, 则反转效应对文本抽取窗口的选取不敏感, 增强构念效度; 三轨的存在正是为了防止研究者选择性报告某一条最"漂亮"的轨道 (specification curve 逻辑的一个实例)。铁律: 三轨各自 just-identified 并排使用, 严禁将三轨的 tone_reversal 同时塞进同一个 over-identified 的 Hansen J 检验框架中作为多重工具或多重矩条件——这会人为夸大过度识别检验的自由度并混淆构念边界。三轨中门控口径亦须与 2026-06-29 起生效的 full-only 留篇门控保持一致: 是否判定某银行—年份构成"一篇有效的银行金科报道"完全由 `llm_verified_full == True` 决定, ctx/ss 轨道上的 tone_reversal_ctx / tone_reversal_ss 是 conditional-on-full 的测度/稳健性轨, 其行宇宙 (哪些银行—年份有值) 是 full 轨行宇宙的子集, 但每条轨道各自独立地按其自身轨道文本计算语调再差分 (即 ctx 轨的 tone_reversal_ctx 用的是 ctx 轨自身的 llm_vote_tone_ctx 序列做差分, 不借用 full 轨的语调数值)。 近期两项研究可为本变量补充同域坐标。Pham (2026) 以公司层 ESG 新闻情感的「轨迹」(随时间的路径与变化) 而非单期水平作为解释变量, 检验其对特质波动的影响, 与本变量所属的「情感时序动态测度」族同处一个构念空间, 属该方向的前沿存在性证明; 其情感序列取自 ESG 新闻、频率高于年度、DV 为特质波动, 而本变量是银行-年 LLM 共识语调的一阶差分, 差分算子与姊妹变量 tone_volatility 的窗口 (window=3, min_periods=2) 均为本项目自设, 原文并未使用同一公式, 故只锚定「把情感的时序变化而非水平作为测度对象」这一层, 不锚定具体算子。Aldama-Navarrete、Curti、Hansen 与 Kazinnik (2026) 构造针对特定银行的媒体情感测度并检验其与监管行为的关联, 表明把新闻情感按银行主体归集、再进入银行层面实证, 是当前金融稳定领域顶级期刊接受的做法, 为本变量被差分的上游对象 (银行-年媒体语调) 提供了同域应用依据; 迁移边界在于该文是美国银行监管语境 (监管评级/监管行动为 DV), 其情感测度的构造细节与本项目三轨文本、三家 LLM 多数投票的共识语调口径不同, 亦不涉及创新话语的实质性/象征性分类维度, 且未对语调作纵向差分, 因而不能据以主张反转测度本身已有直接先例。
## VAR: tone_reversal_ctx

【变体差分】
本列使用 ctx 轨 (标题+银行实体窗口文本) 的共识语调序列 `llm_vote_tone_ctx` 做逐年一阶差分, 即 `tone_reversal_ctx = llm_vote_tone_ctx_t - llm_vote_tone_ctx_lag1`, 滞后值同样按 `target_bank` 分组、按 `year` 排序后 `shift(1)` 得到。ctx 轨的语调输入本身聚焦在报道中围绕目标银行实体的局部文本窗口, 相比 full 轨排除了文章中与该银行无直接关系的段落 (例如同一篇报道中涉及的其他银行或宏观背景叙述), 因此 ctx 轨的语调序列理论上噪声更低、对目标银行本身的情绪刻画更聚焦, 但也因窗口更窄而在极端情况下样本信息量更少。ctx 轨的行宇宙受 full-only 留篇门控约束, 即只在该银行—年份被 full 轨判定为存在有效银行金科报道时才计算 (ctx 是 conditional-on-full 的稳健性轨, 不是独立的留篇判据)。tone_reversal_ctx 与 tone_reversal_full、tone_reversal_ss 三者各自 just-identified 并排, 是互为稳健性检验的关系而非相互替代或叠加使用, 三者严禁混入同一个 over-identified Hansen J 框架。ctx 轨没有独立的门控副本需要同步 (门控唯一权威副本在 full 轨), 但下游若引用 ctx 轨样本量或非缺失行数, 须知其严格是 full 轨样本的子集, 不构成独立样本框。在实证使用上, 研究者若同时报告 tone_reversal_full 与 tone_reversal_ctx 的回归系数作为跨轨稳健性证据, 应明确两者是并列稳健性检验而非层级嵌套的主副设定, 报告表述应避免出现"以 full 为主、ctx 仅作补充"的从属化措辞。

## VAR: tone_reversal_full

【变体差分】
本列使用 full 轨 (标题+全文正文, 无截取) 的共识语调序列 `llm_vote_tone_full` 做逐年一阶差分, 是家族的 canonical/主口径变体: full 轨同时也是 P1 (bank_fintech_tone 论文) 主处理变量 `llm_vote_tone_full` 的差分派生, 也是 stage 21 留篇门控 (`llm_verified_full == True`) 直接锚定的轨道, 即银行—年份是否被算作"存在一篇有效银行金科报道"完全由 full 轨判定, ctx/ss 两轨的样本行宇宙是 full 轨行宇宙的子集。因此 tone_reversal_full 的非缺失覆盖率在三轨中最高, 是三轨互为稳健性检验中承担"锚点"角色的一支, 但依本项目铁律三轨仍是并排关系而非主次关系——即便 full 轨承担留篇门控职能, 在实证设定层面 full/ctx/ss 三条 tone_reversal 轨道各自 just-identified, 不应被简化为"full 是主要设定、ctx/ss 是次要设定"的从属叙事, 而应表述为"以 full 轨门控留篇, 以 full/ctx/ss 三轨互证反转效应的稳健性"。full 轨语调因覆盖全文, 相较 ctx/ss 更容易受到文章中非目标银行段落 (背景铺垫、行业综述、其他机构对比) 的语调稀释或污染, 这是解读 tone_reversal_full 与 tone_reversal_ctx/ss 出现方向或量级分歧时应优先考虑的机制性差异, 而非直接归因于测量误差。此外, 由于 full 轨行宇宙最完整, tone_reversal_full 在覆盖广度上最适合作为跨银行、跨年度描述统计与基准分布刻画的首选轨道, 但这只是覆盖率意义上的便利性, 并不意味着其在识别策略层面优先于 ctx/ss 两轨。

## VAR: tone_reversal_ss

【变体差分】
本列使用 ss 轨 (标题+银行∧金科词同句共现窗口, ±1 句半径, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 的共识语调序列 `llm_vote_tone_ss` 做逐年一阶差分。ss 轨的判定口径最严——文章须存在银行实体与金科词在同一句 (或指定半径窗口内) 出现的证据, 才使用该同句片段的语调; 若某文章不存在这样的同句共现, ss 轨依设计回退 (fallback) 为镜像 ctx 语义的全文 body 文本, 并由 `ss_is_fallback` 标记该行处于回退状态, 与 `n_articles` 共享同一个分母, 不构成额外的样本损耗或双重计数。tone_reversal_ss 因此实际上混合了两类信号来源: 真正同句共现窗口下的紧凑语调, 与回退状态下退化为近似 ctx/full 的语调, 解读时应留意 `ss_is_fallback` 标记的分布, 尤其在金科相关报道稀疏的银行—年份, 回退比例可能偏高, 使 tone_reversal_ss 与 tone_reversal_ctx 在数值上高度接近而非独立提供额外信息。ss 轨同样是 conditional-on-full 的稳健性轨, 行宇宙是 full 轨门控留篇集合的子集, 且与 ctx、full 两轨的 tone_reversal 变量各自 just-identified 并排使用、互为稳健性、不分主次, 严禁三者混入同一个 over-identified 的 Hansen J 检验设定。研究者在使用 tone_reversal_ss 前应先核查该银行—年份子样本中 `ss_is_fallback` 的占比, 若回退比例接近 1, 则该轨在此子样本上提供的边际信息量趋近于 ctx 轨, 报告结果时宜在稳健性附注中一并披露。

<!-- rendered-citations:begin -->
Da, Z.; Engelberg, J.; Gao, P. (2015). The sum of all FEARS investor sentiment and asset prices. The Review of Financial Studies, 28(1), 1-32. https://doi.org/10.1093/rfs/hhu072
Tetlock, Paul C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Shapiro, A. H.; Sudhof, M.; Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Aksoy-Yurdagul, D.; Buchner, A.; Zareei, A. (2026). The persistence of news sentiment: Implications for return predictability. Economics Letters, 260, Article 112803. https://doi.org/10.1016/j.econlet.2025.112803
Pham, H. (2026). From ESG noise to firm-specific risk: Adverse ESG sentiment trajectories and idiosyncratic volatility. Borsa Istanbul Review, 100863. https://doi.org/10.1016/j.bir.2026.100863
Aldama-Navarrete, D., Curti, F., Hansen, A. L., & Kazinnik, S. (2026). Does media sentiment influence bank supervision? Journal of Financial Stability, 84, 101538. https://doi.org/10.1016/j.jfs.2026.101538
<!-- rendered-citations:end -->
