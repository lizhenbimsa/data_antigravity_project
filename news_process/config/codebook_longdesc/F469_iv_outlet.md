---
family_id: F469
columns:
- outlet_disp_exposure_iv_ctx
- outlet_disp_exposure_iv_full
- outlet_disp_exposure_iv_ss
- outlet_style_clarity_iv_ctx
- outlet_style_clarity_iv_full
- outlet_style_clarity_iv_ss
unit: 工具变量 (无独立量纲; 与被工具化的内生媒体测度同量纲 — disp 系情感离散度、clarity 系笔法清晰度分)
formula: "IV_{i,t} = Σ_o share_{i,o,T0} × style_{o,t}^{LOO(排除银行 i 的文章)}; share_{i,o,T0} = 基期银行 i 报道中来自媒体 o 的占比; disp 的 style = |llm_vote_score − 年均|, clarity 的 style = clarity_clarity_score"
producer: news_process/pipeline/panel/iv_extensions.py::compute_outlet_composition_iv (编排 compute_iv_extensions, runner 步骤 8z); 标签见 news_process/pipeline/panel/export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss — disp style 原料)
- 16_article_policy_alignment.parquet
- 40_article_bank_level (df_exploded; clarity_clarity_score_full/_ctx/_ss — clarity style 原料)
citations:
- doi: 10.1080/07350015.2026.2618311
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2026
  title: "Gradient wild bootstrap for instrumental variable quantile regressions with weak and few clusters"
  venue: Journal of Business & Economic Statistics
  vol: "44"
  pages_or_artno: 1-12
- doi: 10.48550/arXiv.2509.12538
  type: arxiv
  authors: Nibbering, D., & Oosterveen, M.
  year: 2025
  title: "Policy-relevant causal effect estimation using instrumental variables with interference"
  venue: arXiv
- doi: 10.48550/arXiv.2504.05658
  type: arxiv
  authors: Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y.
  year: 2025
  title: "Identification and estimation of causal peer effects using instrumental variables"
  venue: arXiv
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: "39"
  issue: "1"
  pages_or_artno: 181-204
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: "65"
  issue: "4"
  pages_or_artno: 1373-1403
- doi: 10.1086/728743
  type: journal
  authors: Gabaix, X., & Koijen, R. S. J.
  year: 2024
  title: "Granular instrumental variables"
  venue: Journal of Political Economy
  vol: "132"
  issue: "7"
  pages_or_artno: 2274-2303
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: Journal of the Royal Statistical Society Series A
  vol: "187"
  issue: "3"
  pages_or_artno: 748-771
- doi: 10.1016/j.jeconom.2024.105727
  type: journal
  authors: Wang, W., & Zhang, Y.
  year: 2024
  title: "Wild bootstrap inference for instrumental variables regressions with weak and few clusters"
  venue: Journal of Econometrics
  vol: "241"
  issue: "1"
  pages_or_artno: "105727"
- doi: 10.48550/arXiv.2308.03531
  type: arxiv
  authors: Färber, M., Schwade, J., & Jatowt, A.
  year: 2023
  title: "Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election"
  venue: arXiv
- doi: 10.1177/1536867X20953572
  type: journal
  authors: Dippel, C., Ferrara, A., & Heblich, S.
  year: 2020
  title: "Causal mediation analysis in instrumental-variables regressions"
  venue: The Stata Journal
  vol: "20"
  issue: "3"
  pages_or_artno: 613-626
- doi: 10.1146/annurev-economics-080218-025643
  type: journal
  authors: Andrews, I., Stock, J. H., & Sun, L.
  year: 2019
  title: "Weak instruments in instrumental variables regression: Theory and practice"
  venue: Annual Review of Economics
  vol: "11"
  pages_or_artno: 727-753
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: "Annual report readability, tone ambiguity, and the cost of borrowing"
  venue: Journal of Financial and Quantitative Analysis
  vol: "52"
  issue: "2"
  pages_or_artno: 811-836
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: "63"
  issue: "2-3"
  pages_or_artno: 329-357
- doi: 10.1111/j.1911-3846.2011.01125.x
  type: journal
  authors: Davis, A. K., & Tama-Sweet, I.
  year: 2012
  title: "Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A"
  venue: Contemporary Accounting Research
  vol: "29"
  issue: "3"
  pages_or_artno: 804-837
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: "78"
  issue: "1"
  pages_or_artno: 35-71
new_dois: []
---

## CORE

【构念与来源】
本家族是两条媒体来源构成型 (outlet-composition) 工具变量, 服务两篇 provisional 论文的因果识别: outlet_disp_exposure_iv 服务 bank_media_disagreement (跨媒体情感分歧), outlet_style_clarity_iv 服务 bank_news_clarity (银行新闻笔法清晰度)。两者共用同一台 shift-share 引擎, 只是灌进引擎的文章级 shift 取值 (house-style) 不同: 前者的笔法信号是"立场极端度", 即某篇报道的情感偏离当年全样本均值的绝对幅度; 后者的笔法信号是"清晰度分", 即报道文本的可读性/明晰程度。二者共同的识别直觉源自媒体经济学的一条稳健事实: 每一家媒体来源都有相对持久的编辑风格 (house style), 一家倾向于用强烈、极化的措辞报道, 另一家倾向于平实、清楚的叙述, 而这套风格在短期内相对外生于任一家被报道银行当年的真实基本面。于是, 一家银行"接触到什么样风格的媒体报道", 很大程度由它历史上被哪些媒体覆盖 (基期媒体构成) 决定, 而各家媒体在当年对其他银行所展现的风格水平, 又是相对外生的冲击。把"基期媒体份额"当作 share、把"媒体当年对他行展现的风格"当作 shift, 二者相乘求和, 就得到一个既与银行实际接触到的媒体分歧/清晰度高度相关、又不由该银行自身当年新闻内生驱动的暴露量。这正是被工具化的内生测度 (cross_outlet_tone_variance 与 mean_clarity_score) 的合格工具。数据来源为文章级 df_exploded (来自 40_article_bank_level): disp 的 style 原料是 stage 21 LLM 共识情感分 llm_vote_score{track}, clarity 的 style 原料是 clarity 打分列 clarity_clarity_score{track}; 媒体来源列由 OUTLET_COL 指定, 基期年集合 base_years 用于冻结份额并施加前视掩码。

用一句大白话概括构造逻辑: 我们想知道"一家银行的新闻分歧 (或清晰度) 会不会真的影响它的融资成本/风险等结果", 但直接回归会有内生性——银行自身的经营状况既可能影响新闻怎么写, 又直接影响结果, 两头纠缠。于是我们换一个角度: 一家银行历史上主要被哪几家媒体报道, 是相对固定的; 而这几家媒体今年在报道别的银行时表现出多大的分歧 (或多清楚的笔法), 与这家银行今年自己的真实经营基本无关。把"历史上主要被谁报道"当权重, 把"这些媒体今年对别人展现的风格"当信号, 加权平均, 就得到一个只反映"这家银行大概率会接触到多分歧/多清楚的媒体环境", 却不掺入它自身当年内生信息的干净变量, 用它去替内生的分歧/清晰度做两阶段最小二乘 (2SLS)。这套"基期结构份额 × 外生冲击"的做法, 在计量里叫 shift-share 或 Bartik 工具, 是媒体经济学与劳动经济学里被反复检验的成熟识别范式。之所以选媒体来源构成而非其他维度作份额, 是因为媒体的编辑风格 (house style) 在文献里被证明有很强的时间持续性与来源间异质性, 这正是 shift-share 识别所需要的"份额稳定、冲击外生"两个前提能落地的现实基础。

【方法学与计算】
引擎实现于 compute_outlet_composition_iv, 由 compute_iv_extensions (runner 步骤 8z) 逐轨编排。构造式为 IV_{i,t} = Σ_o share_{i,o,T0} × style_{o,t}^{LOO}。第一步冻结基期份额: 在基期年集合内, 对每家银行 i 统计其被各媒体 o 报道的篇数占比 share_{i,o,T0}=n_{i,o}/n_i, 分母是该银行基期全部可识别媒体来源的文章数; 基期无文章的银行其 IV 置 NaN。第二步计算逐媒体逐年的 house-style 水平 style_{o,t}: 对媒体 o 在年 t 的全部文章取 shift 变量均值, 但严格做 leave-one-out — 剔除报道焦点银行 i 自己的那些文章, 只用该媒体当年报道"其他银行"的部分, 从而阻断"银行 i 当年新闻内容"经由 style 回流进自己的工具; 剩余文章数低于 min_outlet_loo (默认 1) 时该 outlet-year 的 style 置 NaN。第三步做严格缺失传播: 把 share 与逐 (bank, outlet, year) LOO 后的 style 相乘得逐项贡献 _term, 在 bank-year 上求和; 只要任一 share>0 的媒体当年 style 不可计算, 该 bank-year 的 IV 即置 NaN (strict), 刻意不做 available-renormalize 重归一 — 因为"哪些媒体还在报道这家银行"本身是内生选择, 若按可得媒体重新归一化会让这一选择回流进工具, 污染外生性 (与 iv_did 同口径)。第四步施加 share 前视掩码: 面板年份早于基期末年 (year < max(base_years)) 的行, IV 一律置 NaN, 防止用未来才冻结的份额去解释更早的观测。disp 的 style 在灌入前额外做年内去均值 (|tone − 该年全样本均值|), 以剥离"年份级共同情绪水平"、只保留媒体个体的极端度; clarity 的 style 直接取 clarity 打分 (清晰度是文本的绝对属性, 无需剥离年份基调, 故不做年内去均值)。全过程纯 CPU、确定性 groupby 算术、无 LLM/embedding 调用, golden-safe——即在冻结缓存下逐位可复现, 不受浮点非确定性影响。整台引擎由 compute_iv_extensions 在 runner 步骤 8z 就地 merge 进 panel, 不单独写盘, 由后续 export/stata_export 统一落 parquet 与 dta; 列标签在 export.py 的标签字典里登记 (Outlet Dispersion Exposure IV / Outlet Style Clarity IV 各三轨)。因新增或改动本族列涉及面板 schema, 落盘须重跑 stage 45/46 并受控重生 golden, 本机 T=2 试跑不可安全 regen, 留待生产语料 run 执行 (CLAUDE.md 确定性约束)。日志层面, 引擎逐 IV 列打印 n_valid/len(panel) 的有效率, 供审计核对退化是否落在 T=2 预期范围内; 步骤 8z banner 另把 10 条核心方法论引文从 docstring 提升进 .log, 达顶刊审计留痕标准。

关于四步之间的耦合关系再补三点工程细节。其一, 基期份额与逐年 style 在时间上刻意错位: 份额只用基期 (T0 及之前) 冻结, 一次算定不随年变; style 逐年重算, 反映当年媒体环境。这种"冻结份额 × 逐年冲击"的错位正是 shift-share 识别的核心——份额提供横截面上的暴露差异 (哪家银行更暴露于哪类媒体), shift 提供时间上的外生变动 (媒体环境逐年怎么波动), 二者相乘才既有截面识别力又有时序外生性。其二, leave-one-out 是双重剔除的: 计算某家银行 i 在媒体 o 年 t 的 style 贡献时, 从 o 当年的文章池里减掉所有报道 i 的文章, 只留 o 报道其他银行的部分, 从根上切断"i 自己今年的报道内容"经 style 渠道回流; 若剔除后 o 当年剩余文章不足 min_outlet_loo, 该 outlet-year 的 style 视为不可计, 触发 strict 传播。其三, strict NaN 传播与 available-renormalize 的取舍是刻意的方法论选择: 若某家银行基期的某个媒体今年恰好没报道其他银行 (style 不可计), 我们宁可让整个 bank-year 工具置 NaN, 也不按"还能算的那几家媒体"重新归一化份额, 因为"今年哪几家媒体还在报道"本身是内生的媒体选择行为, 重归一化会把这一选择偷偷装回工具, 破坏外生性 (与 iv_did 严格同口径)。这一保守取舍在浅面板上代价明显 (大量 NaN), 但在全量语料上换来更干净的排他性。

【文献定位】
方法学骨架是 shift-share / Bartik 型工具变量, 其可信度取决于基期份额的外生性而非 shift 的外生性, Borusyak, Hull & Jaravel (2025) 的操作清单系统区分了 share-外生与 shock-外生两条识别路径, 本引擎走的是基期 share 外生路径; Apfel (2024) 进一步给出在部分 share 内生时如何放松排他性约束的诊断, 为本族 IV 的稳健性讨论提供参照; Gabaix & Koijen (2024) 的 granular IV 则从"大单位特异冲击加权和"角度为把媒体级异质冲击聚合成银行级工具提供了同源理论。媒体 house-style 的持久性——即本族识别赖以成立的前提——由 Gentzkow & Shapiro (2010) 关于报纸媒体立场固定性的经典证据支撑。就两条测度的构念内涵而言, clarity 侧接续会计与金融的可读性文献: Bonsall, Leone, Miller & Rennekamp (2017) 的 plain-English 可读性测度、Ertugrul, Lei, Qiu & Wan (2017) 关于年报可读性与语调模糊如何抬高借贷成本的证据、以及 Davis & Tama-Sweet (2012) 关于管理层在不同披露渠道间调节语言的发现; disp 侧接续媒体覆盖的多样性/离散度文献, Färber, Schwade & Jatowt (2023) 给出了衡量媒体报道 variety/balance/disparity 的框架, Gutknecht (2025) 则记录媒体覆盖如何经由风险渠道影响企业。弱工具与少簇推断维度, Andrews, Stock & Sun (2019) 的弱工具实践综述、Wang & Zhang (2024, 2026) 的弱簇/少簇 wild bootstrap 推断, 为下游 2SLS 在 bank×year 面板上的有效推断提供程序性依据。因果链条若涉及中介, Dippel, Ferrara & Heblich (2020) 给出 IV 框架下的中介分析工具; 同伴/干扰型识别的前沿, Luo et al. (2025) 与 Nibbering & Oosterveen (2025) 讨论了存在同伴效应/干扰时 IV 的识别与政策相关效应估计, 与本族"以他行媒体风格作工具"的设定精神一致。就 disp 侧的分歧构念而言, 媒体覆盖的多样性与离散度并非新概念: Färber, Schwade & Jatowt (2023) 提出以 variety (类别数)、balance (分布均匀度)、disparity (类别间差异) 三维刻画媒体报道的多元程度, 为"跨媒体分歧"提供了可操作的测度语言; Gutknecht (2025) 则记录企业社会不当行为的媒体覆盖如何经由风险渠道抬高股权风险, 佐证媒体报道结构 (而非仅仅报道量) 具有独立的经济后果, 这正是把媒体分歧作为一条待识别渠道的现实依据。综合看, 本族在方法学上站在 shift-share IV 的成熟传统里, 在构念上分别接续媒体分歧文献 (disp) 与财务文本可读性文献 (clarity), 在诊断上遵循弱工具与少簇稳健推断的当代规范, 三条脉络在两篇论文的 identification.iv 里汇合为一台共用引擎的两条正交工具。

【识别策略定位】
在两篇论文的 paper_spec 中, 本族列被 identification.iv 显式登记为主工具: bank_media_disagreement 的 primary=outlet_disp_exposure_iv_full、fallback=outlet_disp_exposure_iv_ctx、ss_mirror=outlet_disp_exposure_iv_ss; bank_news_clarity 的 primary=outlet_style_clarity_iv_full、fallback=outlet_style_clarity_iv_ctx、ss_mirror=outlet_style_clarity_iv_ss。被工具化的内生变量分别是 cross_outlet_tone_variance{track} (媒体间情感方差) 与 mean_clarity_score{track} (银行年度平均清晰度)。主轨为 _full, 与全仓 full-only 留篇门控 (2026-06-29) 及 governance 同步口径一致——是否算作一篇银行金科报道只看 full 轨 LLM 判定, ctx/ss 是 conditional-on-full 的子集测度轨; _ctx 作首要 robustness (fallback), _ss 作同句共现窗口的第三稳健轨镜像。三轨 (full/ctx/ss) 是同一篇文章的三个剪裁窗口 (full=标题+全文 / ctx=标题+实体窗口 / ss=标题+银行金科同句窗), 因此在 2SLS 中三轨各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 严禁把 full/ctx/ss 任意两轨的 outlet 工具拼进同一 over-identified Hansen J——三窗源自同一文章、被 bank_type×year 共同冲击逐字同污染, J 检验对真实排他性威胁的功效趋近于零, 近共线还会拖垮 KP rk F 一阶段诊断 (Parente & Santos Silva 2012 一类论证)。要做过度识别检验须改用跨族工具组合 (LOO × Bartik / LOO × zone-LOO, 见各 2SLS 模板既有 overid 列), 而非同族跨轨拼接。这条铁律不是保守习惯而是有代价的方法论纪律: 一旦误把同源两轨拼成 over-identified, Hansen J 会因两个工具高度共线而给出一个看似漂亮的高 p 值 (无法拒绝排他性), 但这只是共线的假象, 对真正的排他性违背毫无侦测力, 反而误导读者相信识别更稳; 同时近共线会稀释一阶段的 KP rk F, 让本可强识别的工具显得弱。正确的做法是三轨各自 just-identified 并排报告, 用系数在三个文本窗口下是否方向一致、显著性相近来支持稳健性主张, 把过度识别检验留给真正跨族、跨识别源的工具组合 (outlet × 同业 LOO × 广义 Bartik)。这也是全仓所有涉三轨/双轨/梯子的测度共享的统一纪律, 本族两条 outlet 工具在 disp 与 clarity 两篇论文里各自恪守, 不因它们共用同一台引擎而破例。

【与相邻测度的构念区分】
本族两条工具刻意构念正交, 却共用引擎, 故须严格互斥论证 (paper_spec 的 distinct_iv / sibling_iv 字段, F12.2): 对 bank_media_disagreement, distinct_iv=outlet_disp_exposure_iv (媒体立场极端度暴露) 是主, sibling_iv=outlet_style_clarity_iv (媒体清晰度暴露) 须论证与被解释渠道互斥; 对 bank_news_clarity 则相反。二者的判别在于灌入引擎的 shift 语义不同: 一条度量"报道有多极端/离散"(情感对年均的偏离幅度), 一条度量"报道有多清楚"(文本可读性), 前者刻画分歧、后者刻画明晰, 经验上二者可以同高 (措辞既极端又清楚) 或反向, 因此不是同一构念的两种称呼。与本族相邻的其他 IV 引擎——同组 leave-one-out 同业均值工具 (leave_one_out_peer_*_iv) 与广义 Bartik 工具 (bartik_*_iv)——虽同属 iv_extensions 的三引擎, 但识别源不同: LOO 走同业社会网络均值 (Manski 反射问题下的同伴识别), Bartik 走 bank_type×year 组份额 × 组内 LOO shift; 本族独有的识别源是"媒体来源构成"这一维度, 把外生性寄托在基期被谁报道的历史构成上, 与前两者可组成跨族 overid 而不同源自污染。须强调本族不是嵌入类测度, 无 co-primary 双轨 _lg 孪生, 换嵌入模型时零涉及。还须把本族与被它工具化的内生测度本身区分开: cross_outlet_tone_variance 与 mean_clarity_score 是银行年度的实际观测量 (真实分歧、真实清晰度), 属内生 RHS 变量; 本族 outlet_*_iv 是它们的外生替身工具, 二者在 2SLS 里分居内生与工具两侧, 数值上不相等也不应相等——工具只需与内生量相关且满足排他性, 不需要与之同量级。误把工具当内生量、或反过来用内生量做工具, 都是识别错误。最后, 本族与广义 Bartik 族 (bartik_*_iv) 虽同为 shift-share, 但份额维度不同: Bartik 用 bank_type×year 的类型份额, 本族用 bank×outlet 的媒体来源份额, 前者的外生性寄托在行业类型结构上、后者寄托在历史媒体构成上, 两者可作为不同识别源组成跨族 overid, 恰因份额维度正交而不同源自污染, 这也是唯一被允许的过度识别做法。

【已知局限与稳健性梯子】
第一, 排他性依赖"基期媒体构成外生"这一不可完全检验的假设: 若一家银行在基期就系统性地只被某类风格媒体覆盖 (例如强监管背景银行更多被官方媒体报道), 且该风格媒体又系统性关联该行未来结果, 则份额并非纯外生, Apfel (2024) 的放松排他性诊断与 Borusyak, Hull & Jaravel (2025) 的 share-外生检查表是应对路径。第二, strict NaN 传播在样本浅 (T 小、媒体稀疏) 时会大面积吞掉 IV——在 T=2 试跑面板上尤甚, 属预期退化, 全量 T=18 语料下自然恢复, 不得据 T=2 的稀疏推断引擎有缺陷。第三, LOO 与前视掩码共同保证工具不含焦点银行当年信息与未来份额, 但代价是牺牲基期与早年观测的有效性。第四, 弱工具风险须在下游用 KP rk F + AR 稳健置信区间 + tF 程序统一诊断, 少簇/两维聚类推断辅以 Wang & Zhang (2024, 2026) 的 wild bootstrap。稳健性梯子由三轨 (full/ctx/ss) 并排构成——各自 just-identified、互为稳健性、不分主次、禁混同一 over-identified Hansen J; ss 轨采同句共现窗口, 语义镜像 ctx (无同句共现时优雅置 NaN 而非借 full 分母), 是判据最严的第三主轨。第五, 媒体 house-style 的持续性假设本身有边界: 若某家媒体在样本期内发生编辑方针剧变 (改版、并购、监管介入), 则其风格不再时间稳定, shift 的外生性会被削弱; 这类结构断裂在中文媒体样本里可经媒体层面稳健性检验与剔除高换手媒体来识别。第六, 同伴/干扰型识别的一般性风险——即"以他行媒体风格作工具"隐含各银行媒体暴露之间存在溢出——由 Luo et al. (2025) 与 Nibbering & Oosterveen (2025) 系统讨论, 提示在存在干扰时应关注政策相关效应的界定而非机械套用无干扰 IV 渐近理论; 本引擎的 LOO 剔除已切断最直接的自我回流, 但跨行溢出的残余须在解释系数时保守披露。第七, 因果链条若经由中介变量传导 (如分歧先影响投资者关注再影响成本), 应配合 Dippel, Ferrara & Heblich (2020) 的 IV 中介分析框架分解直接与间接效应, 而非把总效应误读为单一渠道。综上, 本族两条工具是识别策略的核心, 但其可信度须靠"基期份额外生 + house-style 持续 + LOO 切断回流 + strict 传播 + 前视掩码 + 弱工具诊断 + 三轨并排"这一整套约束共同支撑, 任一环节的披露不足都会让识别主张打折。

## VAR: outlet_disp_exposure_iv_full

【变体差分】
本列是跨媒体情感分歧工具在 full 轨 (标题 prepend + 全文正文) 的实现, 服务 bank_media_disagreement, 且是该论文 identification.iv 的 primary 主工具 (main_track=_full, 与 governance 同步、与 11_table2 OLS 主轨一致、与全仓 full-only 留篇门控 2026-06-29 对齐)。它被工具化的内生变量是 cross_outlet_tone_variance_full——银行年度内跨媒体的情感方差。灌入 shift-share 引擎的文章级 style 是"立场极端度": 取 full 轨 LLM 共识情感分 llm_vote_score_full, 先按年做年内去均值 (|llm_vote_score_full − 该年全样本均值|), 剥离年份级共同情绪水平后只留媒体个体对当年基调的偏离幅度; 再按媒体×年做 leave-one-out 均值 (剔除焦点银行自身文章), 得逐 outlet-year 的 house-style 极端度水平, 最后与基期媒体份额相乘求和。与本族 _ctx/_ss 的唯一差别是文本窗口取全文 (full=标题+全文), 因而 style 原料 llm_vote_score_full 覆盖最完整的文本证据、样本损失最小、在浅面板上有效行最多。作为主工具, 本列在 2SLS 中与 _ctx (fallback)、_ss (ss_mirror) 各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 禁与 _ctx/_ss 任意拼进同一 over-identified Hansen J——三窗同源同污染, J 功效≈0 且拖垮一阶段 KP rk F。作为分歧工具, 本列须与同引擎产出的清晰度工具 outlet_style_clarity_iv 做 distinct/sibling 互斥论证 (F12.2): 二者 shift 语义不同 (极端度 vs 清晰度), 构念正交, 不得互相替代解释同一渠道。本列非嵌入测度, 无 co-primary 双轨 _lg 孪生。

用大白话说清本列在做什么: 一家银行今年新闻里的"众说纷纭程度"(有的媒体大唱赞歌、有的猛烈唱衰) 很难直接用来做因果, 因为经营好坏本身会引来分歧。本列换个替身——先看这家银行历史上主要被哪几家媒体报道 (基期份额固定住), 再看这几家媒体今年在报道别的银行时, 用词有多极端 (对当年平均基调偏离多大, 且只统计它们报道别人的部分, 把这家银行自己的报道剔干净), 把两者加权平均。得到的数值高, 说明这家银行大概率浸泡在一个"爱用极端措辞"的媒体环境里, 从而更容易出现跨媒体分歧, 但这个数值本身不受它今年真实经营的直接污染, 可以拿来当分歧的干净替身做 2SLS。之所以取 full 轨, 是因为全文窗口保留最完整的语义证据, LLM 情感判定 llm_vote_score_full 的信噪比最高、样本流失最小, 因此被定为主工具, 承担 12_table3_iv_2sls 模板里的 IV1 角色; 而 _ctx 作 IV2 (fallback)、_ss 作 IVSS (ss_mirror) 是它的两条稳健替身。识别的可信度上, 本列继承整套 shift-share 约束: 基期份额外生 (由历史媒体构成决定, 非当年选择)、house-style 时间持续 (Gentzkow & Shapiro 2010 的媒体立场固定性)、LOO 切断自我回流、strict NaN 传播不重归一化、year<T0 前视掩码。作为主工具, 下游须报 KP rk F 一阶段强度与 AR 稳健置信区间, 弱工具时改用 tF 程序或 Wang & Zhang (2024, 2026) 的少簇 wild bootstrap 推断。本列的一个实现要点是 disp 特有的年内去均值: llm_vote_score_full 在灌入前先减去当年全样本情感均值再取绝对值, 目的是把"某一年整个市场情绪偏乐观/偏悲观"这种年份级共同成分剥掉, 只留下媒体个体相对当年基调的偏离幅度——否则一个情绪普遍高涨的年份会让所有媒体的原始情感分都偏高, 被误当成"极端度上升"。经此处理后, style 度量的才是纯粹的媒体 house-style 极端倾向, 与 clarity 侧不做去均值形成刻意对照。就有效性而言, full 轨因样本流失最小, 在浅面板上通常是三轨中有效观测最多、一阶段最强的一轨, 这也是把它选作 primary 的实务理由之一。

## VAR: outlet_disp_exposure_iv_ctx

【变体差分】
本列是跨媒体情感分歧工具在 ctx 轨 (标题 prepend + 实体上下文窗口) 的实现, 服务 bank_media_disagreement, 在 identification.iv 中登记为 fallback (首要 robustness 轨), 与主轨 _full 配对——因两轨在 paper_spec 中被 primary/fallback 全收, 故 tier 同判 core。它被工具化的内生变量是 cross_outlet_tone_variance_ctx。与 _full 的唯一实质差别在文本窗口: style 原料改取 llm_vote_score_ctx, 即 LLM 情感判定只在标题加实体上下文窗口 (银行/金科实体附近的截取文本) 上运行, 而非全文; 其余构造完全一致——年内去均值得立场极端度、媒体×年 LOO 剔除焦点银行、基期份额加权求和、strict NaN 传播、year<T0 前视掩码。相较 full 轨, ctx 轨聚焦实体邻近语境, 剔除与银行金科无关的段落噪声, 但样本与文本证据相应收窄, 在浅面板上有效行可能更少。作为首要稳健性轨, 本列与 _full (主)、_ss (ss_mirror) 三轨各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 三轨严禁拼进同一 over-identified Hansen J (同源三窗被 bank_type×year 共同冲击同污染, Hansen J 零功效)。若要做过度识别须改用跨族工具 (本族 outlet IV × LOO / Bartik)。本列同样须与 outlet_style_clarity_iv_ctx 做 distinct/sibling 互斥论证。本列非嵌入测度, 无 _lg 孪生。

为何 ctx 轨值得单列为 core 而非仅作附属: ctx 窗口把文本限定在银行与金科实体附近的上下文, 剥掉了与该行金科话题无关的段落 (如同一版面里其他公司的消息、宏观综述), 因此 llm_vote_score_ctx 度量的是"专门针对这家银行金科的那段话有多极端", 而非整篇报道的笼统基调。这在概念上更贴近论文关心的"关于该银行的媒体分歧", 是对 full 轨"全文归因可能掺入无关噪声"的一种针对性稳健检验; 反过来, ctx 也可能因窗口过窄而丢失篇章级语境, 故两轨互为补充、谁也不能单独称最优, 这正是三轨"互为稳健性、不分主次"设计的本意。在 12_table3_iv_2sls 模板中, 本列以 IV2 (fallback) 身份与主轨 IV1 并排跑独立的 just-identified 2SLS, 报告各自的一阶段 F 与系数, 供读者判断结论是否随文本窗口选择而漂移。铁律须再申一遍: full 与 ctx 虽同源同引擎, 但绝不能把 outlet_disp_exposure_iv_full 与 outlet_disp_exposure_iv_ctx 一起塞进同一个 over-identified 方程做 Hansen J——它们是同一批文章的两个剪裁窗口, 被 bank_type×year 的共同冲击逐字同污染, J 检验对真实排他性违背几乎没有功效, 反而因近共线拉低 KP rk F、给出误导性的"通过"信号。补充本列与 disp 主轨的量纲一致性: ctx 与 full 都被工具化到情感离散度量纲上 (cross_outlet_tone_variance_ctx 与 _full 分别是 ctx/full 窗口的媒体间情感方差), 因此两轨工具虽文本窗口不同, 却服务同一构念的两个测量版本, 是名副其实的"互为稳健性"而非两个不同构念。实务上, 若主轨 full 与稳健轨 ctx 给出方向一致、显著性相近的 2SLS 系数, 即可主张分歧效应不被文本窗口选择驱动; 若两轨明显背离, 则须回到 llm_vote_score 三轨的测量差异去追因, 而非简单取其一。ctx 轨 style 同样先做年内去均值再取绝对值, 与 full 轨口径一致, 只是情感判定基于实体上下文窗口而非全文, 故对"整篇报道里与该行金科无关的段落是否稀释了极端度信号"这一疑问给出针对性回答。也正因如此, 本列在 paper_spec 中与 full 一同被 primary/fallback 全收、同判 core, 是识别策略的承重列而非附属。

## VAR: outlet_disp_exposure_iv_ss

【变体差分】
本列是跨媒体情感分歧工具在 ss 轨 (标题 prepend + 银行金科同句共现窗口 ±N) 的实现, 服务 bank_media_disagreement, 在 identification.iv 中登记为 ss_mirror (同句共现窗口的第三稳健主轨), tier=standard。它被工具化的内生变量是 cross_outlet_tone_variance_ss。与 _full/_ctx 的差别在文本窗口取最严的同句判据: style 原料取 llm_vote_score_ss, 即只在"银行与金科词同句共现"的句子窗口上做 LLM 情感判定; 若某篇文章无银行金科同句共现, 则 ss 轨回退语义镜像 ctx——该文的 style 值缺失, 相应地当 shift_values_by_track 的 _ss 键为 None 或该轨 shift 不可计算时, 引擎内置守卫将 outlet_disp_exposure_iv_ss 优雅置 NaN (绝不借 full 分母或 full style 顶替)。其余构造 (年内去均值得极端度、媒体×年 LOO、基期份额加权、strict NaN 传播、前视掩码) 与前两轨完全一致。ss 是判据最严窗口, 在浅面板/稀疏语料上退化最重 (T=2 试跑常大面积 NaN, 属预期), 全量 T=18 恢复。作为第三稳健主轨, 本列与 _full/_ctx 各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 三轨禁混同一 over-identified Hansen J。须与 outlet_style_clarity_iv_ss 做 distinct/sibling 互斥论证。本列非嵌入测度, 无 _lg 孪生。ss 轨的价值在于它施加了最严的共现判据: 只有银行与金科词真正出现在同一句里, 那句话的情感才被计入, 因此它排除了"文章前半段夸银行、后半段单说金科政策"这类跨句拼接可能带来的伪关联, 是对 full/ctx 的最保守稳健性检验。代价是同句共现在语料里相对稀疏, ss 轨的有效观测最少、在 T=2 试跑面板上退化最重, 解释系数时须与 full/ctx 对照、不宜孤立解读。

## VAR: outlet_style_clarity_iv_full

【变体差分】
本列是媒体笔法清晰度工具在 full 轨 (标题 prepend + 全文正文) 的实现, 服务 bank_news_clarity, 且是该论文 identification.iv 的 primary 主工具 (main_track=_full, governance 同步、full-only 门控 2026-06-29 对齐)。它被工具化的内生变量是 mean_clarity_score_full——银行年度平均新闻清晰度。灌入 shift-share 引擎的文章级 style 是"清晰度分": 直接取 full 轨清晰度打分列 clarity_clarity_score_full (不做 disp 那样的年内去均值——清晰度是绝对笔法属性, 无需剥离年份基调), 再按媒体×年做 leave-one-out 均值 (剔除焦点银行自身文章) 得逐 outlet-year 的 house-style 清晰度水平, 最后与基期媒体份额相乘求和。与本族 _ctx/_ss 的唯一差别是文本窗口取全文, style 原料 clarity_clarity_score_full 覆盖最完整文本、样本损失最小。识别直觉承接可读性文献 (Bonsall et al. 2017; Ertugrul et al. 2017; Davis & Tama-Sweet 2012): 一家媒体写得清楚与否是相对持久的编辑风格, 银行"接触到多清楚的报道"由其历史媒体构成决定, 而各媒体当年对他行展现的清晰度是外生冲击。作为主工具, 本列与 _ctx (fallback)、_ss (ss_mirror) 三轨各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 禁与 _ctx/_ss 拼进同一 over-identified Hansen J (三窗同源同污染, J 功效≈0 且拖垮 KP rk F)。作为清晰度工具, 本列须与同引擎的分歧工具 outlet_disp_exposure_iv 做 distinct/sibling 互斥论证 (F12.2): 清晰度 ≠ 立场极端度, 二者构念正交不得互替。本列非嵌入测度, 无 co-primary 双轨 _lg 孪生。

用大白话说清本列: 一家银行的新闻写得清不清楚, 直接拿来解释它的融资成本会有内生性——经营透明规范的银行本就更容易被写清楚, 而透明本身又降成本, 两头纠缠。本列的替身思路是: 看这家银行历史上主要被哪几家媒体报道, 再看这几家媒体今年在写别的银行时笔法有多清楚 (只算它们报道别人的部分, 把这家银行自己的报道剔掉), 加权平均。数值高说明这家银行大概率处在一个"惯用清楚笔法"的媒体环境, 从而它的新闻更可能清晰, 但这个替身不受它自身当年经营的直接污染。之所以定为主工具并取 full 轨, 是因为清晰度是整篇文本的属性, 全文窗口 clarity_clarity_score_full 能最完整地刻画一篇报道的可读性, 样本流失最小, 故在 12_table3_iv_2sls 模板里承担 IV1 角色, _ctx 作 IV2、_ss 作 IV3。与 disp 侧的一个关键实现差别再强调一次: clarity 的 style 不做年内去均值——因为"清楚"是绝对笔法属性, 不像情感极端度那样需要先扣掉年份共同基调; 分歧关心的是"偏离年均多远", 清晰关心的是"绝对有多清楚", 两者度量哲学不同。识别上本列继承全套 shift-share 约束 (基期份额外生、house-style 持续、LOO 切断回流、strict 传播、前视掩码), 下游报 KP rk F 与 AR 稳健 CI; 构念渊源接续会计金融的可读性文献 (Bonsall et al. 2017 的 plain-English 测度、Ertugrul et al. 2017 关于可读性与语调模糊抬高借贷成本、Davis & Tama-Sweet 2012 关于跨渠道语言调节)。其中 Ertugrul et al. (2017) 的证据尤为切题: 年报可读性差、语调模糊会实打实抬高企业借贷成本, 说明"文本清不清楚"本身有独立的定价后果, 这正是 bank_news_clarity 把清晰度当作一条待识别渠道、并为之构造外生工具的现实动机。本列作为该论文 identification.iv 的 primary, 承担把内生的 mean_clarity_score_full 换成外生替身的核心角色: 银行年度平均清晰度既可能由其自身信息披露质量内生驱动 (透明银行更易被写清楚), 又直接关联结果变量, 故不能直接回归; 用"历史媒体构成 × 他行清晰度冲击"这一 shift-share 替身, 才能把媒体环境的外生部分从银行自身透明度里剥离出来。下游若主轨 full 与稳健轨 ctx/ss 系数方向一致, 即可主张清晰度效应稳健于文本窗口选择。

## VAR: outlet_style_clarity_iv_ctx

【变体差分】
本列是媒体笔法清晰度工具在 ctx 轨 (标题 prepend + 实体上下文窗口) 的实现, 服务 bank_news_clarity, 在 identification.iv 中登记为 fallback (首要 robustness 轨), 与主轨 _full 因 primary/fallback 全收而 tier 同判 core。它被工具化的内生变量是 mean_clarity_score_ctx。与 _full 的唯一实质差别在文本窗口: style 原料改取 clarity_clarity_score_ctx, 即清晰度打分只在标题加实体上下文窗口上计算, 聚焦银行/金科实体邻近语境; 其余构造完全一致——媒体×年 LOO 剔除焦点银行、基期份额加权求和、strict NaN 传播、year<T0 前视掩码 (清晰度 style 不做年内去均值)。相较 full 轨, ctx 轨剔除与实体无关的段落, 更贴近"关于该银行金科的那段文字有多清楚", 但文本证据与样本相应收窄, 浅面板有效行可能更少。作为首要稳健性轨, 本列与 _full (主)、_ss (ss_mirror) 三轨各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 三轨严禁拼进同一 over-identified Hansen J (同源三窗被 bank_type×year 共同冲击同污染, Hansen J 零功效)。过度识别须改用跨族工具组合。本列须与 outlet_disp_exposure_iv_ctx 做 distinct/sibling 互斥论证。本列非嵌入测度, 无 _lg 孪生。

ctx 轨对 clarity 的意义与对 disp 平行却各有侧重: 它把清晰度打分限定在银行与金科实体附近的上下文, 度量的是"关于这家银行金科的那段话写得多清楚", 而非整篇报道 (可能夹带与该行无关段落) 的笼统可读性。这对"全文清晰度是否被无关段落稀释或抬高"提供了针对性稳健检验; 但窗口过窄也可能丢掉篇章级的连贯性线索, 故 full 与 ctx 互为补充、不分主次, 在 12_table3_iv_2sls 中以 IV1/IV2 并排各跑独立 just-identified 2SLS, 供读者判断清晰度效应是否随文本窗口选择而稳健。因两轨在 bank_news_clarity 的 paper_spec 中被 primary/fallback 全收, 故 ctx 与 full 同判 core、同为识别策略的承重列, 而非可有可无的附属。铁律重申: outlet_style_clarity_iv_full 与 outlet_style_clarity_iv_ctx 绝不可拼进同一 over-identified 方程做 Hansen J——同源三窗被 bank_type×year 共同冲击同污染, J 零功效且近共线拖垮一阶段 KP rk F; 要做过度识别检验, 应把本族 outlet 工具与跨族的同业 LOO 或广义 Bartik 工具组合, 因后两者识别源不同 (社会网络均值 / 组份额冲击), 不与 outlet 构成同源自污染。本列被工具化的内生量是 mean_clarity_score_ctx, 与 full 轨的 mean_clarity_score_full 是同一"银行年度平均清晰度"构念的两个测量窗口版本, 故本列与主轨互为稳健性、量纲一致, 而非度量另一个东西。与 disp 侧一致的口径差别再申一次: clarity 的 style 不做年内去均值, 因为清晰度是文本绝对属性, 不需要扣除年份共同基调; 这一点在 ctx 轨同样成立, ctx 只改文本窗口 (实体上下文) 而不改"取绝对清晰度分、不去均值"的度量哲学。实务上, 若窗口收窄后清晰度工具的一阶段强度显著下降, 往往提示"关于该行金科的那段话"本身信息量有限, 此时 full 轨的篇章级证据更可靠, 二者对照即可判断结论的窗口敏感性。作为 fallback, 本列在 12_table3_iv_2sls 模板里以 IV2 身份与主轨 IV1、同句轨 IV3 并排, 各跑独立 just-identified 的 2SLS, 报告各自的一阶段 F 与二阶段系数; 三条估计方向一致即支持"清晰度的因果效应稳健于文本剪裁窗口"的主张, 这是三轨互为稳健性设计要交付的核心证据形态, 而非用来堆一个 over-identified 的 Hansen J。

## VAR: outlet_style_clarity_iv_ss

【变体差分】
本列是媒体笔法清晰度工具在 ss 轨 (标题 prepend + 银行金科同句共现窗口 ±N) 的实现, 服务 bank_news_clarity, 在 identification.iv 中登记为 ss_mirror (v3.9.0 三轨第三主轨, 同句共现窗口), tier=standard。它被工具化的内生变量是 mean_clarity_score_ss。与 _full/_ctx 的差别在文本窗口取最严同句判据: style 原料取 clarity_clarity_score_ss, 即清晰度打分只在银行与金科词同句共现的句子窗口上计算; 若某篇文章无同句共现, ss 轨回退语义镜像 ctx——该文 style 缺失, 相应地当该轨 clarity_clarity_score_ss 缺列或 shift 不可计算时, 引擎内置守卫将 outlet_style_clarity_iv_ss 优雅置 NaN (绝不借 full 顶替)。其余构造 (媒体×年 LOO 剔除焦点银行、基期份额加权、strict NaN 传播、前视掩码) 与前两轨一致。ss 是判据最严窗口, 浅面板/稀疏语料退化最重 (T=2 试跑常大面积 NaN, 属预期), 全量 T=18 恢复。作为第三稳健主轨, 本列与 _full/_ctx 各自 just-identified、并排成列、互为稳健性、不分主次; 铁律: 三轨禁混同一 over-identified Hansen J。须与 outlet_disp_exposure_iv_ss 做 distinct/sibling 互斥论证。本列非嵌入测度, 无 _lg 孪生。ss 轨对清晰度的价值在于最严的同句共现判据: 只有银行与金科词同句出现, 那句话的清晰度才被计入, 因此它排除了整篇报道里与该行金科无关句子对可读性均值的干扰, 是对 full/ctx 最保守的稳健检验。代价同样是同句共现稀疏、有效观测最少、浅面板退化最重 (T=2 常大面积 NaN 属预期, 全量 T=18 恢复), 系数须与 full/ctx 对照解读而非孤立采信。

<!-- rendered-citations:begin -->
Wang, W., & Zhang, Y. (2026). Gradient wild bootstrap for instrumental variable quantile regressions with weak and few clusters. Journal of Business & Economic Statistics, 44, 1-12. https://doi.org/10.1080/07350015.2026.2618311
Nibbering, D., & Oosterveen, M. (2025). Policy-relevant causal effect estimation using instrumental variables with interference. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.12538
Luo, S., Shuai, K., Zhang, Y., Li, W., & He, Y. (2025). Identification and estimation of causal peer effects using instrumental variables. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2504.05658
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Gabaix, X., & Koijen, R. S. J. (2024). Granular instrumental variables. Journal of Political Economy, 132(7), 2274-2303. https://doi.org/10.1086/728743
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Wang, W., & Zhang, Y. (2024). Wild bootstrap inference for instrumental variables regressions with weak and few clusters. Journal of Econometrics, 241(1), 105727. https://doi.org/10.1016/j.jeconom.2024.105727
Färber, M., Schwade, J., & Jatowt, A. (2023). Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2308.03531
Dippel, C., Ferrara, A., & Heblich, S. (2020). Causal mediation analysis in instrumental-variables regressions. The Stata Journal, 20(3), 613-626. https://doi.org/10.1177/1536867X20953572
Andrews, I., Stock, J. H., & Sun, L. (2019). Weak instruments in instrumental variables regression: Theory and practice. Annual Review of Economics, 11, 727-753. https://doi.org/10.1146/annurev-economics-080218-025643
Ertugrul, M., Lei, J., Qiu, J., & Wan, C. (2017). Annual report readability, tone ambiguity, and the cost of borrowing. Journal of Financial and Quantitative Analysis, 52(2), 811-836. https://doi.org/10.1017/S0022109017000187
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across alternative disclosure outlets: Earnings press releases versus MD&A. Contemporary Accounting Research, 29(3), 804-837. https://doi.org/10.1111/j.1911-3846.2011.01125.x
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
<!-- rendered-citations:end -->
