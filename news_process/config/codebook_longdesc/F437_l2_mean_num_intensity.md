---
family_id: F437
columns:
- mean_num_intensity_ctx
- mean_num_intensity_full
- mean_num_intensity_ss
unit: 无量纲比率 (数字 token 数 / 句子数; bank-year 加权均值)
formula: "mean_num_intensity_{track} = Σ_i (w_i · num_intensity_i) / Σ_{i∈valid(track)} w_i;  num_intensity_i = n_numeric_tokens_i / max(n_sentences_i, 1);  w_i = media_authority_weight_i · herd_weight_{track},i"
producer: news_process/pipeline/panel/encode_collab.py::aggregate_num_intensity_panel (article 层来自 news_process/pipeline/sentiment/numerical_intensity.py::enrich_with_num_intensity_dual_track / compute_num_intensity)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (article 层 num_intensity_{full,ctx,ss})
- 40_panel_yearly.parquet (bank-year 加权聚合入面板)
citations:
- doi: 10.1111/jbfa.70056
  type: journal
  authors: Taraj, I., & Wahlström, R. R.
  year: 2026
  title: "Narratives contextualizing numeric disclosures: Insights from earnings calls"
  venue: Journal of Business Finance & Accounting
  vol: 53
  issue: 3
  pages_or_artno: 1263-1286
- doi: 10.1111/1475-679X.70058
  type: journal
  authors: Levy, B.
  year: 2026
  title: "Caution ahead: Numerical reasoning and look-ahead bias in AI models"
  venue: Journal of Accounting Research
  vol: 64
  issue: 3
  pages_or_artno: 1139-1188
- doi: 10.1016/j.jcorpfin.2025.102813
  type: journal
  authors: Campbell, J. L., Zheng, X., & Zhou, D.
  year: 2025
  title: "Number of numbers: Does a greater proportion of quantitative textual disclosure reduce information risk?"
  venue: Journal of Corporate Finance
  vol: 94
  pages_or_artno: 102813
- doi: 10.1111/1467-8551.12853
  type: journal
  authors: Cai, W., Shi, W., & Jiang, F.
  year: 2025
  title: "Cheap talk? Strategy disclosure intensity, corporate risk-taking and financial performance"
  venue: British Journal of Management
  vol: 36
  issue: 1
  pages_or_artno: 361-382
- doi: 10.48550/arXiv.2511.17866
  type: arxiv
  authors: Hartley, E.
  year: 2025
  title: "Narratives to numbers: Large language models and economic policy uncertainty"
  venue: arXiv
- doi: 10.1016/j.ecolind.2024.111971
  type: journal
  authors: Ricotta, C., & Feoli, E.
  year: 2024
  title: "Hill numbers everywhere. Does it make ecological sense?"
  venue: Ecological Indicators
  vol: 161
  pages_or_artno: 111971
- doi: 10.1111/ele.14336
  type: journal
  authors: Chao, A., Chiu, C.-H., Hu, K.-H., van der Plas, F., Cadotte, M. W., Mitesser, O., Thorn, S., Mori, A. S., Scherer-Lorenzen, M., Eisenhauer, N., Bässler, C., Delory, B. M., Feldhaar, H., Fichtner, A., Hothorn, T., Peters, M. K., Pierick, K., von Oheimb, G., & Müller, J.
  year: 2024
  title: "Hill–Chao numbers allow decomposing gamma multifunctionality into alpha and beta components"
  venue: Ecology Letters
  vol: 27
  issue: 1
  pages_or_artno: e14336
- doi: 10.1002/ecm.1588
  type: journal
  authors: Chao, A., Thorn, S., Chiu, C.-H., Moyes, F., Hu, K.-H., Chazdon, R. L., Wu, J., Magnago, L. F. S., Dornelas, M., Zelený, D., Colwell, R. K., & Magurran, A. E.
  year: 2023
  title: "Rarefaction and extrapolation with beta diversity under a framework of Hill numbers: The iNEXT.beta3D standardization"
  venue: Ecological Monographs
  vol: 93
  issue: 4
  pages_or_artno: e1588
- doi: 10.1177/001041407901200101
  type: journal
  authors: Laakso, M., & Taagepera, R.
  year: 1979
  title: "\"Effective\" number of parties: A measure with application to West Europe"
  venue: Comparative Political Studies
  vol: 12
  issue: 1
  pages_or_artno: 3-27
- doi: 10.1890/13-0133.1
  type: journal
  authors: Chao, A., Gotelli, N. J., Hsieh, T. C., Sander, E. L., Ma, K. H., Colwell, R. K., & Ellison, A. M.
  year: 2014
  title: "Rarefaction and extrapolation with Hill numbers: A framework for sampling and estimation in species diversity studies"
  venue: Ecological Monographs
  vol: 84
  issue: 1
  pages_or_artno: 45-67
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是银行相关新闻叙事的数值披露密集度 (numerical disclosure intensity), 即一篇报道在其文本中使用了多少个可被明确解析的定量表达。构念直觉很朴素: 一篇充斥着具体金额、增长率、百分比、时间跨度与规模数字的报道, 相较于只有形容词与立场表态的报道, 携带了更多可被市场核验、可被后续追责的硬信息 (hard information); 反之, 数字稀疏、通篇软性叙事的文本更接近立场性的软信息 (soft information)。把这一直觉操作化为可入面板的连续测度, 就得到文章级的 num_intensity, 再经 bank-year 加权聚合得到本家族三列 mean_num_intensity_full / mean_num_intensity_ctx / mean_num_intensity_ss。这一测度族在披露文本分析文献里有清晰的谱系: 数值披露强度作为独立于情感极性的叙事维度, 其构念锚可追溯到管理层跨披露渠道语言使用差异的研究 (盈余新闻稿相对 MD&A 更倾向使用数字), 而近年的顶刊工作进一步把"数字占文本的比例"直接当作信息量与信息风险的因果变量来检验。Campbell, Zheng 与 Zhou (2025) 的 number of numbers 研究表明, 定量文本披露比例越高, 信息风险越低, 正是本家族测度逻辑的近期母本; Taraj 与 Wahlström (2026) 则强调数字披露必须放进叙事语境里解读, 为本家族区分全文轨与实体邻近轨提供了理论支撑。

数据来源上, 本家族是纯文本派生测度, 全链条 $0 调用外部 API, 不依赖任何 LLM 或嵌入模型。文章级原始信号在 stage 22 批处理之后, 由 numerical_intensity 模块的 enrich_with_num_intensity_dual_track 后处理器对每一篇报道的三条物理文本列各独立计算一次而得; 三条文本列 content_full / content_ctx / content_ss 由 stage 14 ctx_materializer 物化, 全部为 prepend_title 后的含标题文本 (标题作为第 0 句参与句子切分与数字计数)。经 bank-year 加权聚合后, 三列作为数字密度 headline 测度进入 40_panel_yearly 面板, 并在 stage 46 导出 Stata dta。除面板消费外, 本家族的 full 轨 (mean_num_intensity_full) 还被验证阶段 39d 词汇判别效度检验 (lexical_discriminant_validity) 取用为三指标判别矩阵中的 T3 = A3 num_intensity, 与 T1 = LLM substance vote、T2 = A1 clarity 一同做 HTMT / AVE 判别效度诊断, 确认数字密度与实质性投票、清晰度是三个可区分的构念而非同一潜变量的三次测量。

【方法学与计算】
文章级公式为 num_intensity_i = n_numeric_tokens_i / max(n_sentences_i, 1), 即一篇报道中数字 token 的个数除以句子数, 得到"平均每句携带多少个数字"。分子 n_numeric_tokens 的计数经过一套保守的中文数字规范化前处理: 先由自实现的约五十行 cn2arab 转换器把中文数字串统一转成阿拉伯数字 (锁定五个标准样例, 如两千万转 20000000、三亿五千万转 350000000、百分之三十转 30%、三十万亿元的量级换算), 再用阿拉伯数字 token 正则计数。这套转换器不引入 PyPI 的 cn2an 依赖, 且内嵌了多重守卫以避免功能词与专名污染: 不定数 (几千 / 数十亿 / 上百万 / 三十多万 / 二十余家) 一律不计为数字; 序数词第 N (第三季度 / 第十八届) 不转; 党代会与规划序数专名 (十九大 / 十三五) 单列守卫; 单字中文数字块 (一 / 三 / 五) 仅在数量语境计入 — 必须后接量词单位白名单 (家 / 笔 / 元 / 户 / 年) 或前置数量修饰 (约 / 近 / 达 / 共), 且前字命中功能词黑名单 (之 / 统 / 进 / 这 / 同 / 唯) 时强制否决, 从而剔除"进一步 / 之一 / 统一 / 一系列 / 一带一路"这类根本不是数字的高频误计。这些守卫来自 2026-06-11 的一次审计: 盘上样本实测显示旧实现约四成分子 token 来自 cn2arab 误转 (单字"一"一项即占分子约四分之一), 修复后单字数字仅在真实"数东西"语境计入。分母 n_sentences 用句末标点 (句号 / 问号 / 感叹号) 计数, 并以前后向断言排除小数点位置的半角句点 (避免把 1.5 拆成两句), 分号不计。空文本或单字符文本返回 NaN 而非 0, 这一显式 NaN 语义在下游聚合层被严格尊重。

bank-year 聚合公式为各轨的媒体权威×羊群加权均值: mean_num_intensity_{track} = Σ_i (w_i · num_intensity_i) / Σ_{i∈valid(track)} w_i, 其中权重 w_i = media_authority_weight_i · herd_weight_{track},i, 分母只对该轨 num_intensity 非 NaN 的报道求权重和 (valid-mask 分母)。这一分母口径至关重要: 若把空文本报道的权重也计入物理分母, 加权均值会被系统性稀释, 抵消文章级显式 NaN 保护的语义, 因此各指标使用自身的有效掩码分母, 使分子与分母的求和域严格一致。三条轨各自配备与自身同轨的羊群权重 herd_weight_{track} (缺该轨列时回退 full 轨权重), 与情感族 clarity 聚合口径完全对齐。加权而非简单平均的动机是: 权威度高的媒体来源与羊群效应校正后的报道, 更能代表市场实际接收到的信息, 用媒体权威×羊群权重加权可让 bank-year 数字密度更贴近"投资者真正读到的硬信息强度", 而非把边缘小媒体的重复转载与权威主流报道等量齐观。聚合实现上还做了幂等处理: 合并前先 drop 面板中已存在的同名输出列, 避免 merge 时产生 _x / _y 后缀冲突, 保证多次运行结果一致 (golden-safe)。所有中间加权临时列 (以下划线前缀命名) 在聚合完成后立即从 df 删除, 绝不落文章级 parquet。

值得强调的是文章级分子计数的保守取向所隐含的一条方法论立场: 本测度宁可漏计 (false negative), 也要避免把功能词与专名误计为数字 (false positive)。这一取向背后有实证依据 — 2026-06-11 审计在盘上样本发现旧实现约四成分子来自 cn2arab 误转, 其中压倒性为进一步 / 之一 / 统一 / 一系列 / 一带一路 / 一方面这类固定搭配, 以及十九大转 19 大、十三五被错算成 15、万一被误算成 10001 这类专名与 malformed 数词。若不加守卫, 数字密度会被系统性灌水, 且灌水量与文本长度正相关, 使分子与分母产生虚假的正相关而抬高整体密度。因此单字中文数字块采用双向门控 (后接量词单位白名单 或 前置数量修饰守卫, 且功能词黑名单一票否决), 序数第 N 与党代会 / 规划序数专名单列守卫, 后缀不定字符 (多 / 余 / 来 / 几) 与块内不定数一并剔除。这些守卫共同确保 num_intensity 计入的是真正的定量披露, 而非中文里高频但非定量的数字字。

从测度可靠性看, 本家族还有两条工程化保护值得记入 codebook。其一是字符串化 NaN 哨兵拦截: 下游三轨富集用 df[col].astype(str).apply 调用时, pandas 会把 NaN / None / NA 转成字符串 'nan' / 'None' / '<NA>' (长度均 ≥ 3, 能通过 isinstance(str) 与 strip 检查), 若不显式拦截会被当正常文本算出 0.0, 让面板均值系统性偏低; 本实现在 isinstance 检查后显式拦截这些字符串化哨兵值, 保证 NaN 正确 propagate 到聚合层。其二是句级与词级共享单次 cn2arab pass 的性能优化 (accel-numint-01): 原本对每轨分别 apply 句级与词级两函数会各算一遍 cn2arab (同文本重复转换), 现由 _num_intensity_both 单 pass 返回句级与词级二元组, 与分别调用逐位等价, 面向 1700 万条全量语料消去重复转换开销。

【文献定位】
本家族在文献版图上位于"文本硬信息量测度"这一支。数值披露密度作为独立于情感极性、语气、可读性的叙事特征, 近年被反复证明与信息环境质量、投资者注意力与风险承担相关。Campbell, Zheng 与 Zhou (2025) 直接把定量文本披露比例作为降低信息风险的因果自变量; Taraj 与 Wahlström (2026) 从盈余电话会议出发, 论证数字披露的信息含量高度依赖其叙事语境, 支撑了把数字密度按全文 / 实体邻近 / 同句共现三种语境粒度分别度量的设计; Cai, Shi 与 Jiang (2025) 研究战略披露强度与企业风险承担及财务绩效的关系, 提示披露强度类文本测度并非中性的描述统计, 而可能与真实公司行为存在系统关联; Hartley (2025) 与 Levy (2026) 则从大语言模型的数值推理角度提醒, 把叙事转为数字、以及模型处理数字时的偏差, 都是当代文本量化研究必须正视的方法论前沿。这些文献共同确立了数字密度作为一个可解释、可核验、与情感极性正交的独立叙事维度进入公司金融面板的正当性。

需要说明本家族测度出处的一段勘误史, 以维护引文的诚实性。numerical_intensity 模块早期注释曾把数值披露强度构念 Eq.(1) 归给 Hales, Kuang 与 Venkataraman (2011), 但经 web 核验该文实为投资者判断中 vivid / pallid 语言影响的研究, 并未定义 numerical intensity, 故该归属被撤销; 现构念锚定于管理层跨披露渠道语言使用差异的会计学研究, 而本实现的具体公式 (数字 token 除以句子数 / 除以词数) 明确记录为项目自定义操作化, 精确公式锚仍待最终确认。这一诚实披露对使用者的含义是: mean_num_intensity 应被理解为一个操作化良好、构念清晰但公式非规范文献直引的自建测度, 其价值在于内部一致的可复现计数与三轨 / 句词双分母的稳健性设计, 而非某篇经典论文公式的机械复刻。

【识别策略定位】
在识别策略上, mean_num_intensity_full 作为本家族 canonical 与 39d 判别效度矩阵中的 T3 指标, 其价值不在于单独作为处理变量, 而在于为主线情感与实质性测度提供一个构念正交的对照维度: 数字密度衡量的是"硬信息的量", 而非"信息的方向"(情感) 或"创新的实质性"(LLM substance)。判别效度检验以 Henseler 等 (HTMT) 与 Fornell-Larcker (AVE / φ²) 框架, 在 bank-year 面板横截面上作保守诊断 (对 n_articles ≥ 2 的观测设掩码, 排列种子锁 42), 确认 T1 / T2 / T3 三者两两 HTMT 低于严格与宽松双阈值, 从而排除数字密度只是情感或实质性投票的另一种测量这一竞争解释。作为面板变量本身, 本家族既可作为叙事信息环境的控制变量, 也可作为披露质量的替代刻画进入稳健性梯子。需要提醒的是, 39d 是 validation-only 阶段 (标记 EXPECTED_NO_OUTPUT, 不进 paper main analysis), 其判别效度矩阵服务于测度效度诊断而非因果识别; 计划中曾拟在 39d 内实施 ctx-fallback HTMT mask (R8-H1), 但因该阶段不进主分析、实施收益远低于面板列推广, 已推迟, 论文层若需等价 robustness 可直接在 Stata 用 frac_ctx_fallback 阈值或 ctx 独立性有效篇数门槛实现。这一安排提示使用者: 数字密度的识别价值主要通过其作为控制或替代测度进入具体论文的自回归而兑现, 三轨则提供规格稳健性的横向对照。

【与相邻测度的构念区分】
本家族须与三类相邻测度严格区分。其一是词级孪生家族 mean_num_intensity_word_{full,ctx,ss} (独立家族), 它与本家族共享同一分子 n_numeric_tokens, 仅把分母从句子数换成 jieba 词数; 二者构成"归一化分母选择"的互为稳健性替代 — 中文新闻句号使用比英文稀疏 (长句加逗号), 句级分母系统性偏低会放大数字密度, 词级分母规避了中英文句读差异。句级 (本家族) 与词级 (孪生家族) 两种口径纪律上不以相关性取舍, 各自独立进回归。这一分母归一化的取舍, 与更广的计数归一化 / 有效数量指数传统一脉相承: 把原始计数转成可比的归一化强度, 正是 Laakso 与 Taagepera (1979) 的有效政党数、以及 Chao 等 (2014) 与 Chao 等 (2024) 的 Hill 数框架所处理的同型问题, 而 Ricotta 与 Feoli (2024) 对过度依赖此类归一化指数的告诫, 与本项目坚持"分母选择须做稳健性而非单一定论"的纪律相呼应 (此处为跨学科方法论类比, 非领域直接引用)。其二是 LLM substance 投票与 clarity, 已由 39d 判别效度检验证明可区分。其三是词典情感测度, 数字密度与语气极性无关: 一篇数字极密的报道既可能是正面 (强劲增长) 也可能是负面 (巨额亏损), 二者正交。这一正交性并非事后论断而有构念层依据 — 情感词典测度的分子是极性词 (正面 / 负面情感词), 数字密度的分子是定量 token, 两套计数在词表层几乎不相交; 数字 token 携带的是信息的"量"与"具体性", 情感词携带的是信息的"方向"与"评价色彩", 二者刻画的是同一文本的两个不同侧面。因此在实证设计中, 数字密度可以与情感极性变量同时进入回归而不构成机械共线, 这也是它作为独立叙事维度的价值所在。与之相对, 与实质性 (LLM substance) 和清晰度 (clarity) 的可区分性则更微妙 — 数字更多的报道往往也更实质、更清晰, 三者存在正相关的可能, 正因如此项目专门以 39d 判别效度检验用 HTMT / AVE 框架量化确认三者的判别边界, 而非仅凭直觉断言其独立。

最后从数据可复现角度补一句聚合链路的落盘约定, 供数据附录与审计使用。本家族三列全部由 aggregate_num_intensity_panel 在 encode_collab 步骤计算并左连接进 bank-year 面板, 输入为文章级 num_intensity_{full,ctx,ss} (来自 stage 22 之后的三轨富集) 与面板骨架的 target_bank / year 键; 当面板或文章级缺失 target_bank / year 键、或文章级 num_intensity_full / num_intensity_ctx 列缺失时, 函数优雅返回空结果并记日志 (graceful skip), 绝不静默产出错误列。三列在 stage 46 随全列 dta 一并导出, 无 core / aux 切分 (该切分已整体退役), 因此下游 Stata 模板严禁按"前 N 列"截断取用本家族。数字密度分布在横截面上重度右偏 (多数报道数字稀疏、少数数字极密), 因此解读其 bank-year 分布时仅看均值与标准差会有误导, 应同时参考中位数与四分位, 这一右偏画像也已在生产日志中作为运行结果诊断被如实记录。

【已知局限与稳健性梯子】
三条轨 full / ctx / ss 属规格稳健性并排关系: 它们各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同轨混进同一 over-identified Hansen J 检验 (与项目三轨 / co-primary 双轨嵌入 / 各类梯子铁律一致)。全家族无 co-primary 嵌入 _lg 孪生 (纯规则计数测度, 非嵌入 carve-out)。已知局限有三: 一是中文句级分母与英文不直接可比, 已由词级孪生家族对冲; 二是 cn2arab 转换的守卫虽已大幅收窄误转, 但不可能穷尽所有专名与固定搭配, 序数 / 不定数 / 功能词残余误计对句级与词级两版同源同向, 不构成本家族独有缺陷; 三是词级越界 (词级版分母排除纯数字 token 而分子仍计数字 token, 数字极密文本比值理论上可大于 1) 属文档化 caveat, 仅影响词级孪生家族。此外, 本家族聚合口径与项目 full-only 留篇门控 (2026-06-29) 一致: 一篇报道是否被判为"银行金科报道"由 full 轨 llm_verified_full 决定, ss 轨在无银行∧金科同句共现时其 content_ss 镜像 ctx 回退为全文 body 并置 ss_is_fallback, 与全家族共享同一 n_articles 分母, 不产生单边孤儿。

稳健性梯子的完整叙事因此可归纳为三层正交的替代设计, 彼此不交叉。第一层是语境粒度梯子: full / ctx / ss 三轨从全文到实体邻近句再到银行∧金科同句, 逐级收窄语境, 检验数字密度信号是否稳健于"读哪一段文本"的选择。第二层是归一化分母梯子: 句级 (本家族) 与词级孪生家族在同一分子上换用句数与词数两种分母, 检验信号是否稳健于"用什么归一化篇幅"的选择, 这一层跨到独立家族 mean_num_intensity_word。第三层是聚合权重的既定口径 (媒体权威×羊群), 与情感族对齐, 不在本家族内另设权重梯子。三层设计各自解决一个不同的规格自由度, 且彼此正交、不组合成笛卡尔积以避免列爆炸。所有并排轨 / 替代分母共同遵守一条不可违反的铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁把任意两条混进同一 over-identified Hansen J 过度识别检验 — 这与项目三轨文本、co-primary 双轨嵌入、政治词权重、词典规则消融、BERT 阈值梯子等一切稳健性并排族的处理完全一致。在开发期 T=2 极小样本上, ctx / ss 轨可能出现零方差或高回退率, 属预期退化而非缺陷, 应以生产期 T=18 全量语料为准判读。

## VAR: mean_num_intensity_ctx

【变体差分】
本列是 mean_num_intensity 家族的实体邻近轨 (ctx track), 与 canonical 的 full 轨相比, 唯一差异在文章级读取的物理文本列: ctx 轨读 content_ctx (标题 prepend + 目标银行实体上下文窗口内的句子), 而非 content_full 的标题加全文正文。其余口径完全一致 — 同一文章级公式 num_intensity_i = n_numeric_tokens_i / max(n_sentences_i, 1)、同一 cn2arab 保守转换与全套守卫、同一 bank-year 媒体权威×羊群加权均值、同一 valid-mask 分母。差异的语义后果是: ctx 轨只统计银行被实体化提及的邻近句里的数字密度, 剔除了报道中与该银行无关段落的数字噪声, 因而更贴近"这家银行相关叙事本身有多少硬信息"。当 content_ctx 缺列时按守卫回退 full 列; 权重侧用与本轨同名的 herd_weight_ctx (缺则回退 full 轨权重)。该轨与 full / ss 两轨属规格稳健性并排关系: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。ctx 轨在文献上呼应 Taraj 与 Wahlström (2026) 数字披露须置于叙事语境解读的主张 — 把语境窗口从全文收窄到实体邻近句, 正是对"数字必须放进它所修饰的对象语境里看"这一理论的直接操作化。ctx 轨常作为 full 轨的首要 robustness 轨: 若主结论在全文轨与实体邻近轨下方向一致, 则可排除"数字密度只是报道整体篇幅或无关段落堆砌"的竞争解释。相较于同句共现轨, ctx 轨的语境收窄程度居中: 它既比 full 轨排除了报道中与目标银行无关的数字噪声, 又比 ss 轨保留了更充裕的句子样本, 因而在开发期 T=2 的极小样本上退化风险介于 full 与 ss 之间, 通常仍能给出有信息量的分布而不像 ss 轨那样频繁触发零方差或高回退。需强调 ctx 轨的实体窗口切分只改变"读哪些句子", 不改变文章级 num_intensity 的任何计数规则与守卫, 也不改变 bank-year 聚合的加权与 valid-mask 分母口径, 因此三轨之间的差异被严格限定为语境粒度这一个自由度, 便于把规格稳健性对照的解释归因锁定到语境选择而非计数或聚合的连带变化。本列无 co-primary 嵌入 _lg 孪生 (纯规则计数, 非嵌入 carve-out), 亦无独立 per-model 变体 (不涉 LLM), 无阈值梯子。

## VAR: mean_num_intensity_full

【变体差分】
本列是 mean_num_intensity 家族的 canonical headline 轨 (full track), 也是本家族唯一的 core 列, 是数字密度构念的规范测度与 Table A9 num_intensity 真双轨中的字符 (句级) 轨代表。相较于 ctx / ss 两轨, full 轨在文章级读取 content_full (标题 prepend + 全文正文), 即对整篇报道的全部句子统计数字 token 与句子数, 度量的是该报道整体叙事的数字密集度, 不做任何实体邻近或同句共现的语境收窄。这一全文口径使 full 轨成为覆盖面最广、样本最完整、退化风险最低的主测度: 只要报道非空, full 轨即有定义, 而 ctx / ss 轨在实体窗口或同句共现为空时会触发回退或退化。正因如此, full 轨被指定为家族 canonical, 并在验证阶段 39d 词汇判别效度检验中被取用为三指标矩阵的 T3 = A3 num_intensity, 与 T1 = LLM substance vote、T2 = A1 clarity 一同做 HTMT / AVE 判别诊断; 判别检验对 n_articles ≥ 2 的观测设掩码、排列种子锁 42、HTMT 采用严格与宽松双阈值, 目的是保守地确认数字密度是独立于实质性投票与清晰度的第三个构念, 而非同一潜变量的重复测量。

文章级公式与全家族一致: num_intensity_i = n_numeric_tokens_i / max(n_sentences_i, 1), 分子经 cn2arab 保守转换 (序数第 N、党代会 / 规划序数专名、单字数字量化语境门控、不定数与后缀不定数、malformed 数词五重守卫) 后用阿拉伯数字 token 正则计数, 分母以句末标点计数并以前后向断言排除小数点半角句点; 空 / 单字符文本返回 NaN 而非 0。bank-year 聚合为媒体权威×羊群 (herd_weight_full) 加权均值, 分母只对 num_intensity_full 非 NaN 的报道求权重和 (valid-mask), 使分子分母求和域严格一致, 尊重文章级显式 NaN 语义。full 轨聚合与 full-only 留篇门控 (2026-06-29) 天然对齐 — 留篇判定本就以 full 轨为准。

作为家族 canonical, full 轨须与三类相邻测度区分。与词级孪生列 mean_num_intensity_word_full 共享同一分子, 仅分母由句数换为 jieba 词数, 二者构成归一化分母选择的互为稳健性替代 (句级易受中文句读稀疏放大, 词级规避该偏差), 纪律上不以相关性取舍、各自进回归。与 LLM substance / clarity 由 39d 判别效度证明可区分。与词典情感极性正交 (数字密度不含方向)。full / ctx / ss 三轨属规格稳健性并排关系: 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J (与项目三轨 / co-primary 双轨嵌入 / 政治词权重 / 消融梯子等铁律同款)。本列无 co-primary 嵌入 _lg 孪生 (纯规则计数, 非嵌入 carve-out), 无 per-model 变体 (不涉 LLM), 亦无阈值梯子。文献上, full 轨作为整篇报道数字密集度的规范刻画, 直接承接 Campbell, Zheng 与 Zhou (2025) 把定量文本比例作为信息风险因果变量的顶刊操作化, 并与 Cai, Shi 与 Jiang (2025) 披露强度与公司行为关联的证据、以及 Hartley (2025)、Levy (2026) 关于叙事数字化与模型数值推理的方法论前沿一同, 支撑数字密度作为独立叙事维度进入银行金科面板的正当性。作为 core 列, full 轨在实证中的典型定位是: 主回归用 full 轨给出数字密度的基准估计, 再以 ctx / ss 两轨与词级孪生列做规格稳健性对照, 三轨与两种分母各自独立进入回归, 若估计方向与显著性在各规格下一致, 则可稳妥排除"结论由某一语境粒度或某一归一化分母驱动"的竞争解释。在开发期 T=2 极小样本上, 唯有 full 轨样本最完整、退化风险最低, 因此 full 轨也是唯一可在本机验证阶段稳定给出非退化分布的轨, ctx / ss 的零方差或高回退在此规模下属预期, 须待生产期 T=18 全量语料判读。

## VAR: mean_num_intensity_ss

【变体差分】
本列是 mean_num_intensity 家族的同句共现轨 (ss track), 与 canonical full 轨的唯一差异同样在文章级读取的物理文本列: ss 轨读 content_ss (标题 prepend + 目标银行与金融科技词在同一句 ±N 窗口内共现的句子, 窗口半径由 config 的 ss_sentence_radius 控制, 默认 1)。其余全部口径 — 文章级公式、cn2arab 转换与全套守卫、bank-year 媒体权威×羊群加权均值、valid-mask 分母 — 与 full / ctx 完全平价。ss 轨的语义是把语境收窄到最严的粒度: 只统计"银行与金科被同一句话捆绑提及"的句子里的数字密度, 度量的是银行金科交汇叙事本身的硬信息含量。ss 轨遵循镜像 ctx 的回退语义 (与 CLAUDE.md 铁律一致): 当某报道无银行∧金科同句共现时, content_ss 回退为全文 body、ss_is_fallback 置 True, 并与全家族共享同一 n_articles 分母, 不产生单边孤儿列; 当整条 ss 列在旧 parquet 中缺席时, 聚合层优雅跳过 ss 部分 (仅聚 full / ctx), 镜像 ctx 守卫范式。权重侧用同名 herd_weight_ss (缺则回退 full 轨权重)。该轨与 full / ctx 两轨属规格稳健性并排关系: 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。在开发期 T=2 的极小样本上, ss 轨因同句共现句子稀少可能出现零方差或大量回退, 属预期退化, 生产期 T=18 全量语料下恢复正常; 因此实证使用中 ss 轨定位为 full 轨的收敛稳健性轨而非主测度。本列无 co-primary 嵌入 _lg 孪生 (纯规则计数, 非嵌入 carve-out), 亦无 per-model 变体。文献上 ss 轨最贴近 Taraj 与 Wahlström (2026) 数字须置于最细语境粒度解读的主张。

<!-- rendered-citations:begin -->
<!-- rendered-citations:end -->
