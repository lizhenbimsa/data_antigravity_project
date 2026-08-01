---
family_id: F004
columns:
- all_ln_coverage
- coverage_active_days
- coverage_continuity
- has_coverage
- high_coverage
- ln_news_coverage
- ln_news_coverage_z
- nf_ln_coverage
- zero_coverage
unit: 混合量纲 — 对数覆盖量 (无量纲, ln(1+篇数)) / 天数 (coverage_active_days, 单位=日) / 比率 [0,1] (coverage_continuity) / 0-1 指示 (has_coverage, high_coverage, zero_coverage) / 年内截面标准分 (ln_news_coverage_z, 无量纲)
formula: "ln_news_coverage = ln(1 + n_articles); all_ln_coverage = ln(1 + all_n_articles), all_n_articles = ft_n_articles_dedup + nf_n_articles; nf_ln_coverage = ln(1 + nf_n_articles); has_coverage = 1{n_articles > 0}; zero_coverage = 1{all_n_articles == 0}; high_coverage = 1{n_articles > 基年中位数}; coverage_active_days = nunique(报道日期); coverage_continuity = coverage_active_days / 当年自然天数(365/366); ln_news_coverage_z = 年内截面 z-score(ln_news_coverage), 仅 n_articles>0"
producer: pipeline/panel/encode.py ; pipeline/panel/runner.py ; pipeline/panel/geography.py ; pipeline/falsification/controls.py
upstream:
- 24_herd_decay.parquet (df_exploded, target_bank/年/日期)
- 12_fintech_news_full.parquet (全量银行新闻, all/nf 分母)
- 40_panel_yearly.parquet (n_articles 聚合口径)
citations:
- doi: 10.1007/s11156-024-01383-0
  type: journal
  authors: Gutknecht, D.
  year: 2025
  title: "Media coverage of corporate social irresponsibility and firm equity risk"
  venue: Review of Quantitative Finance and Accounting
  vol: 65
  issue: 4
  pages_or_artno: 1373-1403
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1002/jae.3095
  type: journal
  authors: Bodilsen, S. T., & Lunde, A.
  year: 2025
  title: "Exploiting news analytics for volatility forecasting"
  venue: Journal of Applied Econometrics
  vol: 40
  issue: 1
  pages_or_artno: 18-36
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
  venue: Journal of Accounting and Economics
  vol: 73
  issue: 2-3
  pages_or_artno: 101455
- doi: 10.1093/rfs/hhq141
  type: journal
  authors: Tetlock, P. C.
  year: 2011
  title: "All the news that's fit to reprint: Do investors react to stale information?"
  venue: Review of Financial Studies
  vol: 24
  issue: 5
  pages_or_artno: 1481-1512
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
new_dois: []
---

## CORE

【构念与来源】
本家族刻画每一家目标银行在每一个年度里"被媒体报道的量、广度与时间形态", 即银行层面的媒体关注度 (media coverage / media attention) 及其分布节奏。它不度量报道的语调好坏, 也不度量报道是否谈及金融科技, 而只回答三个更基础的问题: 这家银行今年到底被写了多少篇、这些报道来自广还是窄的时间跨度、以及有没有被报道。构念根植于金融媒体经济学的一条主线——媒体既是信息中介也是关注度的分配者, 报道量本身承载着信息扩散、投资者关注与价格发现的含义。Call, Emett, Maksymov 与 Sharp (2022) 以问卷证据刻画财经记者作为信息中介的角色, 说明"被报道"这一事件绝非中性噪声, 而是有筛选、有议程的信息生产结果; Gutknecht (2025) 与 Li 与 Luan (2025) 则分别在企业股权风险与投资者分歧的语境下, 直接把媒体报道数量作为核心解释或调节变量, 为本家族"覆盖量→经济后果"的因果叙事提供当代锚点。数据源自本流水线上游的 article 级新闻集: 主口径 n_articles 来自 24_herd_decay.parquet 的 df_exploded (经 stage 21 语义精筛后的 article×bank verified 集), 全量与非金融科技口径则在证伪阶段 (pipeline/falsification/controls.py) 由 12_fintech_news_full.parquet 全量银行新闻经 anti-join 互补划分得到。

【方法学与计算】
家族内 9 列可归为四条计算链路。其一是对数覆盖量: 直接对当年物理报道篇数取 ln(1+x) 缓解右偏, ln_news_coverage 是无后缀 canonical 列, 全量口径 all_ln_coverage 与非金融科技口径 nf_ln_coverage 是同一对数变换施于不同计数底的平行列——三者互为口径参照而非互相替代, 分母边界不同 (面板金融科技篇数 vs 全部银行新闻 vs 剔除金融科技后的新闻), 因此绝不可当作同一测度的冗余复本合并入同一识别式。ln(1+count) 的对数变换沿用媒体金融学的通行做法 (Fang 与 Peress 2009 首创该口径, Hassan 等 2019 在企业层面沿用), 本家族如实继承。其二是标准化: ln_news_coverage_z 是 ln_news_coverage 的年内截面 z-score, 按 Fama 与 MacBeth (1973) 的两阶段思想在每一年度截面内归至 μ=0、σ=1, 使回归系数可直接读为"1σ 关注度变化对应的因变量变动"; 该步只处理 n_articles>0 的行, 零报道行保持 NaN。其三是指示变量: has_coverage、high_coverage、zero_coverage 三个 0-1 哑变量分别刻画"是否有报道""是否高关注度""是否零新闻", 承载不同的门限语义。其四是时间形态: coverage_active_days 数当年有报道的不同自然日, coverage_continuity 以之除以当年自然天数 (闰年 366、平年 365) 得到年内覆盖密度, 度量报道是全年铺开还是爆发式集中 (Hillert 等 2014 的报道节奏思路), 与内容重复的 staleness、产出端重复的 herd 构念正交。

【文献定位】
本家族在测量层与情感、语调、金融科技属性等家族严格分工: 它是"曝露量/关注度"的容器, 是许多比率型指标的分母与许多回归的控制变量, 而非处理变量本身。与语调型测度相比, 覆盖量回答"写了多少"而非"写得好坏"; 与新鲜度 (staleness) 相比, 覆盖量的时间形态列 coverage_continuity 度量报道在时间轴上的分布形状, 与 Tetlock (2011) 所刻画的"陈旧信息重印"是两个正交维度——前者问节奏疏密, 后者问内容是否冷饭重炒。测量噪声对系数的衰减偏误是覆盖量作控制变量时的已知隐忧: Shapiro, Sudhof 与 Wilson (2022) 指出新闻文本测度的测量误差会把系数向零拉, 这为标准化列 ln_news_coverage_z 的存在提供方法学理由——年内标准化让不同年度的关注度可比, 缓解跨期尺度漂移。Bodilsen 与 Lunde (2025) 进一步展示新闻分析量 (news analytics volume) 对波动率的预测力, 佐证报道量本身是有信息含量的一阶信号而非可弃噪声。需要强调的口径铁律: 主口径 n_articles 是"物理覆盖篇数"(含 LLM 投票失败/NA 行), 其行宇宙服从 full-only 留篇门控 (2026-06-29, 一篇报道是否算入只看 full 轨 llm_verified_full); 它区别于 n_articles_llm_valid (分类 frac 的分母, 跳过 NA 行), 二者不可混用。零报道 bank-year 在笛卡尔积补全后语义为"未测量"(NaN) 而非"零", 这一"零报道 ≠ 零比率"的处理是覆盖量家族在回归中不产生伪信号的关键。

## VAR: all_ln_coverage

【变体差分】
本列是全量口径的对数覆盖量, 与 canonical 列 ln_news_coverage 的唯一区别在计数底: 分母由"面板内金融科技相关篇数"扩展为"该银行当年全部银行新闻篇数"。具体在证伪阶段 (pipeline/falsification/controls.py::merge_to_panel) 计算, all_n_articles = ft_n_articles_dedup (去重后的金融科技篇数) + nf_n_articles (非金融科技篇数), 再取 ln(1+all_n_articles)。它对标 Hassan 等 (2019) 的"总体风险暴露 Risk_it"概念: all_ln_coverage 代表一家银行在媒体上的总体曝露量, 用作份额型变量 fintech_share = ft_dedup / all_n_articles 的对数版曝露控制, 也用于挤出弹性叙事中"总盘子"的度量。相较 ln_news_coverage 的金融科技子集口径, 本列把非金融科技报道也纳入分子, 因此在数值上恒不小于同基下的金融科技覆盖量, 语义上回答"这家银行今年被媒体写了多少总量的新闻"。计数底采用去重同基口径 (ft 与 nf 均去重, 复合键 target_bank×标题×日期双侧 drop_duplicates), 与 fintech_share 的分子分母同尺度, 避免转载重复膨胀总量。当去重金融科技聚合 ft_dedup_agg 缺失时, 会回退为物理 n_articles 加去重 nf 的混合基, 仅向后兼容旧调用与测试, 生产口径恒走去重同基。它与 ln_news_coverage、nf_ln_coverage 是三条平行口径, 分母边界互不相同 (金融科技子集、全量、非金融科技), 三者是媒体总关注度的口径分解而非冗余复本, 只作互为参照的稳健性口径而不并入同一识别式, 以免把不同分母的同源变量混进同一过度识别的检验中造成机械共线。作为对数曝露量, 本列在证伪叙事里代表"总盘子", 与其上的份额型变量 fintech_share 配对, 支撑挤出弹性与信息密集度的分析。

## VAR: coverage_active_days

【变体差分】
本列是时间形态链路的计数基元, 度量该 bank-year 有报道的不同自然日数目 (distinct active days), 单位为日, 取值为非负整数 (以 float 存储)。计算在 pipeline/panel/encode.py 完成: 取该银行当年全部报道的日期列, 用 pd.to_datetime 解析并 dropna, 归一化到自然日 (dt.normalize) 后按 target_bank×year 做 nunique 聚合。它区别于家族内所有对数覆盖量列——后者数的是"篇数"(同一天可有多篇), 本列数的是"天数"(同一天多篇只计一天), 因此刻画的是报道在时间轴上触及了多少个不同的日子, 而非总产出量。它是 coverage_continuity 的分子, 也是理解报道节奏的原始材料: 若一年报道 100 篇但只集中在 3 天, active_days=3 会揭示这种爆发式集中, 而篇数口径的 ln_news_coverage 无法区分。缺失语义: 当上游缺 '日期' 列时本列整体置 NaN 并发 warning, 绝不静默填 0, 以免把"日期不可得"误当作"无报道日"。它与内容重复的 staleness、产出端重复的 herd 构念正交——active_days 只问"哪些天有报道", 不问报道内容是否雷同、也不问报道产出是否扎堆。作为绝对天数, 本列未按年度长度归一, 因而在闰年与平年、以及样本首末不完整年份之间不可直接横向比较, 需归一化版本才能跨年可比, 该归一化版本即 coverage_continuity。本列是理解报道节奏的原始材料: 同样 100 篇报道, active_days=100 与 active_days=3 描绘的是全然不同的媒体关注形态——前者是持续跟踪、后者是事件驱动的爆发式集中, 而任何仅数篇数的对数覆盖量列都无法区分这两种形态, 这正是时间形态链路存在的价值。

## VAR: coverage_continuity

【变体差分】
本列是年内覆盖密度 (within-year coverage density), 取值区间 [0,1], 定义为 coverage_active_days 除以当年自然天数 (闰年 366、平年 365)。它与 coverage_active_days 的关键差分是分母: 本列用"当年自然天数"这一外生于报道行为的分母做归一化, 使不同年度、闰年与平年之间可比, 1.0 仅当全年天天有报道、低值对应稀疏或爆发式覆盖。此处有一条承重的口径修正 (fix omni-g-encode-04, 2026-06-11): 旧实现曾以"自身报道首末跨度"为分母, 属端点内生 (endpoint endogeneity)——单日单篇报道会得到 1/1=1.0 的理论最大值, 使最极端的爆发式覆盖反而获最高"连续性", 与构念方向 (低=爆发式) 完全相反; 盘上实证显示旧口径下约 47% 行 =1.0 且多为单篇, 且 corr(continuity, active_days)<0, 明确是坏信号。改用外生自然天数分母后 1.0 仅当全年天天有报道, 构念方向恢复为"年覆盖密度"。论文须明写它与 staleness 的判别区分: coverage_continuity 度量报道在时间轴的分布形态 (节奏疏密), staleness 度量报道内容是否重复 (冷饭重炒), 两者正交——一家银行可以每天被报道却篇篇雷同 (高连续、高陈旧), 也可以偶尔被报道却篇篇新料 (低连续、低陈旧)。它与 Tetlock (2011) 所刻画的"陈旧信息重印"是两个不同问题: 前者问报道的时间铺展, 后者问信息的新旧。作为 [0,1] 归一化密度, 本列消除了年度长度差异 (闰年/平年) 与绝对篇数量级的干扰, 使不同银行、不同年度的报道节奏可横向比较, 是覆盖量家族里唯一以外生年历天数为分母、因而不受报道行为内生影响的比率列。缺 '日期' 列时置 NaN, 与 coverage_active_days 同步降级。

## VAR: has_coverage

【变体差分】
本列是最基础的覆盖指示哑变量, 定义为 1{n_articles > 0}, 在 pipeline/panel/runner.py 的步骤 6a 生成, 紧接笛卡尔积补全 (balance_panel) 之后。它区别于家族内其它指示列的门限对象与计数底: has_coverage 以主口径物理篇数 n_articles 为判据, 回答"这家银行今年到底有没有被报道", 是识别"零报道 bank-year"的第一道闸。它承载的核心语义是"零报道 ≠ 零信号": 笛卡尔积补全会把从未被报道的 bank-year 也补进面板, 这些行的情感、语调等测度按契约置 NaN (未测量) 而非 0, has_coverage=0 正是这些行的标记位, 使下游能条件化剔除或单独诊断。它与 zero_coverage 的差分在计数底——has_coverage 用面板金融科技口径 n_articles, zero_coverage 用全量口径 all_n_articles, 因此二者在"有金融科技报道但可能无其它新闻"或反向情形下并不互为反码, 不可混用。它也是真实信号密度诊断的分子 (有报道 bank-year 占完整笛卡尔积之比), 该密度越高说明面板中承载真实媒体信号的行越密、越少被补全的空行稀释。其判据 n_articles 服从 full-only 留篇门控 (2026-06-29): 一篇报道是否算入只看 full 轨是否 verified, 因此 has_coverage 度量的是"这家银行今年有没有一篇通过语义精筛的金融科技相关报道"。作为 0-1 指示, 无量纲, 是覆盖量家族最粗粒度的门限压缩——它丢弃了篇数的量级信息, 只保留有无, 服务于样本框识别与零报道行的条件化。

## VAR: high_coverage

【变体差分】
本列是高关注度哑变量, 与 has_coverage 的差分在门限: has_coverage 的门限是"是否 >0", 本列的门限是"是否高于基准年中位数"。它在 pipeline/panel/runner.py 由 _base_year_median_split 生成, 判据为 n_articles 相对面板最早年 (基年) 的中位数切分, 高于中位数记 1、否则 0。此处的承重设计是使用 pre-period 固定切分而非同期切分: 若用当期中位数, 调节变量会与 outcome 完全同期内生; 改用基年 (面板最早年份) 固定中位数, 对齐 predetermined (预定) 口径, 避免异质性交互中的内生污染。本列的主要用途是异质性分析——步骤 7g-het 用它构造 Tone×HighCov 交互项 (tone_x_highcov{track}), 检验情感效应在高关注度银行与低关注度银行间是否异质。它区别于 ln_news_coverage_z 的连续标准化: high_coverage 是二元门限切分 (信息压缩为 0/1), 服务于分组比较与三重差分; ln_news_coverage_z 保留连续尺度, 服务于系数的 1σ 解读。作为 0-1 指示, 无量纲, 且因基年固定切分, 同一银行跨年可保持同一档位 (预定性), 这一时间不变的档位设计使它在固定效应与三重差分框架下作为组别标识不被自身后续报道量反向决定。需要与 has_coverage 明确区分: has_coverage 的门限是绝对零点 (>0), 划分"有无报道"; high_coverage 的门限是相对基准年中位数, 划分"关注度高低", 二者回答两个层级的问题, 一个是存在性、一个是强度分档。它也区别于全量口径的 all_ln_coverage——high_coverage 的切分底始终是面板主口径 n_articles, 而非全量或非金融科技口径。

## VAR: ln_news_coverage

【变体差分】
本列是覆盖量家族的 canonical (无后缀) 列, 也是全家族的主参照, 定义为 ln(1 + n_articles), 在 pipeline/panel/encode.py 由主口径物理篇数直接对数变换得到。相对家族内其它对数覆盖量, 它的差分在计数底: 使用 n_articles——即经 stage 21 语义精筛、服从 full-only 留篇门控 (2026-06-29) 的面板金融科技相关物理篇数 (含 LLM 投票失败/NA 行)。它区别于 all_ln_coverage (全量银行新闻底) 与 nf_ln_coverage (非金融科技底), 三者是分母边界不同的平行口径, 互为参照而不合并。ln(1+count) 的对数变换是媒体金融学度量媒体关注度的通行做法, 缓解报道篇数的右偏分布 (Fang 与 Peress 2009 首倡, Hassan 等 2019 沿用)。本列在流水线中身兼多职: 既是 concern_score = ln_news_coverage×(senti_ratio+1)/2 的曝露量因子, 又是地理金融科技暴露 fintech_exposure 的连续基, 还是标准化列 ln_news_coverage_z 的原始输入。口径上须谨记 n_articles 是"物理覆盖篇数"而非"LLM 有效投票篇数 n_articles_llm_valid", 后者才是分类 frac 的分母, 二者差额即投票失败/NA 篇数, 不可互换。零报道行 (n_articles=0) 取 ln(1)=0, 但下游多按 has_coverage 条件化处理其未测量语义, 不把补全空行的 0 当作真实的低关注度信号。作为无后缀 canonical 列, 它是本家族一切口径变体与标准化列的共同起点: all_ln_coverage 换分母、nf_ln_coverage 换分母、ln_news_coverage_z 加标准化、high_coverage 做门限切分, 差分维度各异, 但都以本列所锚定的"面板金融科技物理篇数的对数关注度"为参照原点。它是无量纲对数值, 值域 [0,+∞)。

## VAR: ln_news_coverage_z

【变体差分】
本列是 ln_news_coverage 的年内截面标准化版, 与 canonical 列的唯一差分是一次 Fama-MacBeth 型标准化变换。它在 pipeline/panel/geography.py::standardize_panel_variables (步骤 7b) 生成: 按 Fama 与 MacBeth (1973) 的两阶段思想, 在每一个年度截面内把 ln_news_coverage 归至 μ=0、σ=1, 生成 _z 后缀列而保留原始列不变。关键操作细节有三: 其一, 只处理有新闻覆盖的行 (n_articles > 0), 零报道行保持 NaN, 不让零报道伪值污染截面矩; 其二, 每个年度截面内有效观测须 ≥3 才做标准化, 否则该年该列留 NaN (小样本早期试跑 T=2 下常触发); 其三, 上游 nullable ExtensionArray dtype 先经 to_numeric 归至 float64 再算术, 使 z-score 对 dtype 不敏感且不触发 LossySetitem。它的存在理由是使系数可直接读为"1σ 关注度变化→β 单位因变量", 并缓解跨年度尺度漂移与测量噪声致的衰减偏误 (Shapiro 等 2022)。相较 high_coverage 的二元门限, 本列保留连续信息, 是关注度进入回归的连续标准化通道; 相较原始 ln_news_coverage, 它牺牲了绝对量级的可解释性、换来跨年度截面的尺度可比性, 二者互为参照, 视回归设计选用。需要强调本列只做年内截面标准化而非全样本标准化, 因此它移除的是"哪一年整体报道更多"这一年度均值漂移, 保留的是"同一年里哪家银行相对更受关注"这一截面变异, 这与 Fama-MacBeth 两阶段回归对截面可比性的要求一致。无量纲 (标准分), 零报道行与年内有效观测不足 (<3) 的年份留 NaN。

## VAR: nf_ln_coverage

【变体差分】
本列是非金融科技口径的对数覆盖量, 与 canonical 列 ln_news_coverage 的差分在计数底: 分子是"非金融科技"银行新闻篇数 nf_n_articles。它在证伪阶段 (pipeline/falsification/controls.py) 由 anti-join 互补划分得到——全量银行新闻 (12_fintech_news_full) 减去面板金融科技文章 (复合键 target_bank×标题×日期双侧 drop_duplicates 后集合差集, 沿用 Hassan 等 (2019) 的互补划分思路), 再对篇数取 ln(1+nf_n_articles)。它在证伪逻辑中是关键对照量: 用于检验"金融科技语调的解释力是否仅来自一般媒体关注度"这一 H0——若情感变量与 nf_ln_coverage 弱相关 (|r|<0.3), 则金融科技信号更像独立于泛媒体关注的特异性信号 (支持 H1)。相较 all_ln_coverage (含金融科技的全量) 与 ln_news_coverage (仅金融科技), 本列刻画的是"剔除金融科技后剩下的一般媒体关注度", 三者构成 total = fintech + non-fintech 的口径分解, 但各自作为独立对数覆盖量列并排参照, 不并入同一识别式。计数采用去重"同稿件"基, 缓解转载膨胀。零 NF 行经 left join 自然保留 NaN (刻意不填 0, 避免零 NF 行的伪 0 污染诊断相关系数)——这与 nf_headline_frac 被移出 fill_cols 是同一条"零报道 ≠ 零比率"红线的落地。相较 all_ln_coverage 的全量口径, 本列剔除了金融科技报道, 因而单独刻画"泛媒体关注度"这一混淆通道; 在证伪框架里, 它作为 H0 的化身: 若银行的一般媒体关注度就能解释情感变量的全部效力, 则金融科技语调不含特异信息。本列越是与金融科技情感弱相关, 越支持"金融科技信号独立"的 H1。它与家族其它对数覆盖量各自 just-identified 地并排作口径稳健性参照, 分母边界不同, 不混入同一识别式。无量纲对数值。

## VAR: zero_coverage

【变体差分】
本列是零新闻指示哑变量, 定义为 1{all_n_articles == 0}, 在 pipeline/falsification/controls.py 生成。它与 has_coverage 的核心差分有二: 其一是计数底——本列用全量口径 all_n_articles (金融科技+非金融科技全部银行新闻), has_coverage 用面板金融科技口径 n_articles, 因此二者不互为反码; 其二是语义焦点——zero_coverage 专门标记"份额型变量 fintech_share 无定义"的行。这条设计源于一处承重修正 (fix omni-g-controls-05, 2026-06-11): 当一家银行当年全部零新闻时, fintech_share = ft_dedup / all_n_articles 分母为 0、份额无定义, 旧实现会把它填 0, 使其与"有新闻但恰好全为非金融科技"的真实 0 份额混淆; 现改为分母 0→NaN, 并以 zero_coverage=1 作配套指示列, 供使用者条件化剔除或诊断。它在诊断中承担样本稀疏度告警: 若过半 bank-year 的 zero_coverage=1, 说明面板稀疏、份额类变量样本严重缩水。作为 0-1 指示, 无量纲; 正常语料下应占少数行, 若占比超过半数即触发面板过稀的告警。它体现覆盖量家族的一贯口径铁律——零报道是"未定义/未测量"而非数值 0。与 has_coverage 再作一次并列澄清: has_coverage=0 与 zero_coverage=1 语义相近但不等价, 因计数底不同 (n_articles vs all_n_articles), 一家银行可能在金融科技口径下 n_articles=0 (has_coverage=0) 却在全量口径下仍有非金融科技新闻 (all_n_articles>0, zero_coverage=0); 故二者是互补而非冗余的两个零点指示, 分别服务面板主口径与证伪份额口径。本列专为标记 fintech_share 这一份额型变量的无定义域而设, 是分母保护 (分母 0→NaN) 的配套显式指示, 让使用者能一眼识别哪些行的份额是数学上未定义而非真实为零。

<!-- rendered-citations:begin -->
Gutknecht, D. (2025). Media coverage of corporate social irresponsibility and firm equity risk. Review of Quantitative Finance and Accounting, 65(4), 1373-1403. https://doi.org/10.1007/s11156-024-01383-0
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Bodilsen, S. T., & Lunde, A. (2025). Exploiting news analytics for volatility forecasting. Journal of Applied Econometrics, 40(1), 18-36. https://doi.org/10.1002/jae.3095
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Tetlock, P. C. (2011). All the news that's fit to reprint: Do investors react to stale information? Review of Financial Studies, 24(5), 1481-1512. https://doi.org/10.1093/rfs/hhq141
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
<!-- rendered-citations:end -->
