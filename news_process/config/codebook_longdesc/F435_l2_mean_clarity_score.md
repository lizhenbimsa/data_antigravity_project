---
family_id: F435
columns:
- mean_clarity_score_ctx
- mean_clarity_score_full
- mean_clarity_score_ss
unit: 无量纲清晰度得分 (∈ [-1, +1], 银行-年加权聚合)
formula: "clarity_score_i = frac_definite_i - frac_ambiguous_i ∈ [-1,+1]; frac_definite = n_definite / n_tokens_word, frac_ambiguous = n_ambiguous / n_tokens_word; mean_clarity_score_track[b,t] = Σ_valid w_i × clarity_score_track_i / Σ_valid w_i, w_i = media_authority_weight × herd_weight_track"
producer: news_process/pipeline/sentiment/tone_words.py::_compute_clarity_for_text ; news_process/pipeline/panel/encode_collab.py::aggregate_clarity_panel ; news_process/pipeline/audit/lexical_discriminant_validity.py (Stage 39d 效度审计)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (clarity_clarity_score_{full,ctx,ss} 等文章级列)
- 40_panel_yearly.parquet
citations:
- doi: 10.1057/s41310-024-00240-9
  type: journal
  authors: Du, Y.-G., Li, S., Kuo, N.-T., & Li, D.
  year: 2025
  title: "Does the annual report readability improve corporate R&D investment? Evidence from China"
  venue: International Journal of Disclosure and Governance
  vol: 22
  issue: 2
  pages_or_artno: 440-460
- doi: 10.1016/j.ribaf.2024.102220
  type: journal
  authors: Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y.
  year: 2024
  title: "Annual report readability and trade credit financing: Evidence from China"
  venue: Research in International Business and Finance
  vol: 69
  pages_or_artno: 102220
- doi: 10.1057/s41599-024-03162-7
  type: journal
  authors: Jiang, Z., Hu, L., & Wang, Z.
  year: 2024
  title: "Better or worse? Revealing the impact of common institutional ownership on annual report readability"
  venue: Humanities and Social Sciences Communications
  vol: 11
  issue: 1
  pages_or_artno: 688
- doi: 10.1016/j.pacfin.2023.102074
  type: journal
  authors: Li, F., Yang, M., & Zhang, T.
  year: 2023
  title: "Does prospectus readability matter for bond issuance pricing? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 80
  pages_or_artno: 102074
- doi: 10.1080/21697213.2019.1701259
  type: journal
  authors: Xu, W., Yao, Z., & Chen, D.
  year: 2019
  title: "Chinese annual report readability: Measurement and test"
  venue: China Journal of Accounting Studies
  vol: 7
  issue: 3
  pages_or_artno: 407-437
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1017/S0022109017000187
  type: journal
  authors: Ertugrul, M., Lei, J., Qiu, J., & Wan, C.
  year: 2017
  title: "Annual report readability, tone ambiguity, and the cost of borrowing"
  venue: Journal of Financial and Quantitative Analysis
  vol: 52
  issue: 2
  pages_or_artno: 811-836
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: The Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
- doi: 10.1007/BF02310555
  type: journal
  authors: Cronbach, L. J.
  year: 1951
  title: "Coefficient alpha and the internal structure of tests"
  venue: Psychometrika
  vol: 16
  issue: 3
  pages_or_artno: 297-334
new_dois:
- 10.1007/BF02310555
---

## CORE

【构念与来源】
本家族度量单条新闻报道在语言表达上的"清晰度"(clarity), 并把文章级清晰度加权聚合到银行-年面板。核心构念不是银行自身的透明度, 也不是报道的情绪好坏, 而是第三方媒体在书写某家银行时用词的确定性程度: 一篇报道里"明确、肯定"类措辞越多、"模糊、含糊、不确定"类措辞越少, 该报道被判定为越清晰。换成大白话就是, 如果记者写这家银行时满篇都是"或将、可能、据称、有待观察"这类留有余地的词, 这篇报道对读者而言就更含糊; 反过来, 如果记者敢用"确定、明确、必然、已经"这类把话说死的词, 报道就更清晰。本测度把这种"敢不敢把话说清楚"量化成一个介于负一到正一之间的分数。这一构念定位经所属论文 bank_news_clarity 的 V4 audit reframe 刻意收窄——放弃"clarity 等于银行自身信息透明度"的旧主张(新闻文体与年报文体错配, 该主张在方法学上致命: 银行年报是银行自己写的、可以代理银行透明度, 但新闻是记者写的、只能代理记者/媒体对该银行的感知), 改为"clarity 等于外部观察者(媒体)感知并转述该银行时的表达确定性"。因此本测度捕捉的是媒体报道环境这一外生于单家被报道银行当期经营的文本特征, 而非银行披露质量的直接代理, 这一点也正是论文识别策略(媒体笔法工具变量)成立的构念前提。数据来源上, 文章级原始文本来自 stage 14 物化的三轨文本 content_full / content_ctx / content_ss(标题 prepend, 原始正文列不动), 文章级清晰度列 clarity_clarity_score_{full,ctx,ss} 在 stage 22 tone_words 内由 _compute_clarity_for_text 逐文本独立扫描产出, 银行-年聚合列 mean_clarity_score_{full,ctx,ss} 在 encode_collab.py 的 aggregate_clarity_panel 内完成, 效度审计另由 stage 39d 的 lexical_discriminant_validity.py 独立承担(该 stage 属 validation-only, EXPECTED_NO_OUTPUT, 不进论文主分析)。整条链路的上游是 stage 13 银行金科共现硬过滤后的报道集, 中游是 stage 14 三轨文本物化与 stage 22 词典扫描, 下游是 stage 40 面板导出, 因此本家族的每一列都对应"某家银行在某一年被媒体报道时的平均表达清晰度", 是一个纯文本派生、不依赖任何银行财务数据的度量。所属论文对该测度的定位补充说明还强调: 它与 P5(bank_fintech_collab)已把 mean_clarity_score 用作 Table A7 稳健性对照一事互不冲突, 因为两处引用的是同一文本特征但服务于不同论文的不同角色。需要进一步澄清本测度与几类相近对象的边界: 与信用评级机构或分析师报告的"明确性"不同, 本测度的观察者是新闻媒体而非专业金融中介, 度量的是大众/财经媒体笔下的表达确定性; 与银行自身信息披露(年报 MD&A)的可读性不同, 本测度不经过银行之手、不受银行披露策略直接操纵, 这正是它可作为外生报道环境代理的前提; 与情绪极性(正面/负面)不同, 清晰度是"确定性维度"而非"方向维度", 一篇明确的负面报道与一篇明确的正面报道在本测度上同为高清晰度。由此可见, 本家族三列共同刻画的是一个纯语言学、纯第三方、纯文本派生的报道环境特征, 它既不代理银行透明度、也不代理媒体情绪, 而是独立的"媒体书写确定性"维度, 这一构念纯度是论文识别策略与判别效度审计得以成立的基础。

【方法学与计算】
清晰度词典采用 You (2018) 的两个词表: definite(Panel C, 388 词, 明确/肯定类)与 ambiguous(Panel D, 178 词, 模糊/不确定类)。这两个词表在 v3.5.1 之前仅作存档(此前 you_2018 的 definite/ambiguous 只保存在词典 JSON 里不参与任何计算), 自 v3.5.1 A1 起正式启用于 clarity 计算。用户 2026-06-24 决策明确逆转了早期的跨类去重方案: definite 与 ambiguous 的交集词(实测仅"不可"1 词)不再从任一侧剔除, 而是同时保留在两侧、两侧各计一次, 在 clarity_score 相减时自然抵消, 以保持词表的原始外部可复现性——这一决策的意义在于, 剔除交集词会使复现者用同一份 You (2018)词表却得到不同分数, 而两侧保留则保证任何人拿原始词表都能逐字节重算。分词使用独立的 tone tokenizer(独立 jieba.Tokenizer 实例, 与主分词器隔离以防状态污染), 并在 fix(clarity_cn-01)后对多字 definite/ambiguous 词全部 add_word, 修复此前约 12.4%(实测 67/541)多字词被 jieba 切碎导致的系统性低估——多字模糊词如"有待观察"若被切成"有待""观察"两个 token 就永远命中不了词表, 使模糊度被系统性低估、清晰度被系统性高估。文章级公式为 clarity_score_i = frac_definite_i − frac_ambiguous_i, 其中 frac_definite = n_definite / n_tokens_word、frac_ambiguous = n_ambiguous / n_tokens_word, 取值落在 [−1, +1]: 正值表示明确措辞占优、报道清晰, 负值表示模糊措辞占优、报道含糊, 零表示两类措辞势均力敌。两个分数的分母 n_tokens_word 是 word-token 数, 即在原始 token 上排除纯标点与纯数字 token(复用 lm_non_sentiment 的非词正则 _LMFLS_NONWORD_RE, 与 2026-06-11 lmfls 分母修复同口径); 旧分母含约 19% 标点/数字 token, 会对逐篇比率造成 14.5%–25% 的非常数稀释(不同报道标点/数字占比不同, 若都进分母则等于对每篇施加不同的缩放, 破坏可比性), 故此项分母收紧是对已知偏差的修正而非口径漂移。定义域上仍是"未去停用词"版本(论文 §3.4 disclosure 明确保留停用词, 以免去停用词引入额外的词表依赖)。空文本、非字符串或零 word-token 文章一律返回 NaN 而非假零, 避免把"没有文本"误当"完全模糊/完全清晰"。银行-年聚合采用加权均值 mean_clarity_score_track[b,t] = Σ_valid w_i × clarity_score_track_i / Σ_valid w_i, 权重 w_i = media_authority_weight × herd_weight_track(媒体权威度 × 羊群衰减), 其含义是: 权威媒体、以及在羊群式跟风扩散中处于早期而非尾部的报道, 对该银行当年的平均清晰度贡献更大。三轨各配自己的 herd 权重以实现 measurement-treatment 匹配(Edwards 2001 口径, fix herd-ghost-01), 不再让 ctx/ss 轨借用 full 轨的 herd_weight; herd_weight_ctx / herd_weight_ss 缺失时才优雅回退 full 轨权重。加权分母经 fix(clarity-weighted-denom, metric-audit 2026-06-10)mask 到该指标 valid 的文章集(即 clarity_score 非缺失的文章), 否则缺失文章的权重仍进物理分母会造成 Σ_valid(w·x)/Σ_all(w) 的系统性下偏(分子只累加有效文章、分母却把无效文章的权重也算进去, 结果被人为拉低)。配套还产出 frac_definite 的银行-年加权均值与 frac_amb_articles 的二值化占比(以各轨自身分布的 D0 冻结中位数 median_amb_d0_track 为阈值、n_clarity_valid ≥ 2 为门槛), 与本家族三列同源同分母。二值化占比列 frac_amb_articles_track 的口径值得单独说明: 它数的是"本银行-年内 frac_ambiguous 高于该轨全样本中位数的文章数 / 该轨 clarity 非缺失文章数(n_clarity_valid)", 分子分母同域(空文/零 token 文章不进物理分母), 且 n_clarity_valid < 2 或阈值为 NaN(全 NaN 轨)时返回 NaN 而非假零, 这是 fix H2 + R8-H2 + R9-M3 + omni-2026-06-11 分母口径修订的联合结果, 目的是杜绝"用一个含无效文章的膨胀分母造成系统性下偏"。整个聚合流在 encode_collab.py 内以单次 assign 写临时加权列的方式完成(避免逐列 insert 触发 pandas PerformanceWarning), 各指标(clarity / frac_definite × full/ctx/ss)各用自己的 valid 分母 mask, 互不借用。就确定性而言, clarity 全链是纯词典 + 纯 jieba(0.42.1 冻结)计算、不调任何 LLM 或嵌入 API, 因此本家族三列在离线 NEWS_PROCESS_LLM_OFFLINE=1 下可零成本逐字节复现, 属 golden 可复现锚的组成部分。

【文献定位】
可读性/清晰度作为文本财务学的经典构念, 源流可上溯 Li (2008)以年报"雾度指数"与词数度量披露可读性并联系盈余持续性的开创性工作, 以及 Loughran & McDonald (2014)对 Fog 指数在财务披露中失效的批评与替代度量(文件大小)的提出。本项目 clarity 走的是词典法(明确词减模糊词)而非音节/句长的可读性公式, 更接近 Ertugrul et al. (2017)将"语气模糊度"(tone ambiguity)与可读性并列纳入借款成本方程的路径, 以及 Bonsall et al. (2017)的 plain-English 度量思路。在中文语境下, 词典法尤为必要: Xu, Yao & Chen (2019)系统论证了英文音节可读性公式无法平移到中文、并给出中文年报可读性的测量与检验框架, 为本项目采用中文词表(You 2018)而非 Fog 类公式提供了直接方法学依据。近年一批基于中国样本的经验证据进一步支撑了可读性作为经济后果驱动变量的外部效度: Li, Yang & Zhang (2023)发现招股说明书可读性影响债券发行定价, Li et al. (2024)将年报可读性与商业信用融资联系起来, Du et al. (2025)记录可读性对企业研发投入的促进, Jiang, Hu & Wang (2024)则从共同机构持股角度检视可读性的决定因素。这些文献共同确立了"清晰的文本表达降低信息处理成本、改善融资与投资结果"这一机制预期, 也提示本测度虽落于新闻文体、但与主流年报可读性文献属同一构念家族、可相互印证。需要强调的是, 本项目对可读性文献的借鉴是"构念与机制"层面而非"公式"层面: Li (2008)与 Loughran & McDonald (2014)的度量对象是文本本身的阅读难度(Fog、词数、文件大小), 而本测度度量的是措辞的确定性(明确减模糊), 二者虽同属"文本清晰度"大家族但操作化路径不同; Ertugrul et al. (2017)把 readability 与 tone ambiguity 并列, 恰说明"可读性"与"语气模糊度"是两个可分的维度, 而本测度更贴近后者。中文语境的适配是本测度的关键取舍: 英文 Fog 指数依赖音节与句长, 在中文里没有对应的可复现操作化, Xu, Yao & Chen (2019)正是为此提出中文年报可读性的独立测量框架, 本项目选择词典法(而非移植英文公式)与其方法学立场一致。最后, 效度层面本家族接入了心理测量学的经典工具: Cronbach (1951)的系数 α 被 stage 39d 用于跨 clarity / num_intensity / LLM substance 三指标(而非轨内单指标, 后者数学退化)的信度评估, 这把文本财务学的清晰度构念与更普适的构念效度框架接通。

【识别策略定位】
所属论文 bank_news_clarity 以 mean_clarity_score_full 为主处理变量(treatment.primary), 基线设定为银行内、年份内的长面板双向固定效应 long_panel_within_bank_within_year。由于媒体报道清晰度可能与银行当期经营状况反向内生(经营出问题的银行可能被写得更含糊, 或反之), 论文进一步落地了媒体笔法工具变量 outlet_style_clarity_iv_full: 以基期(冻结)outlet 报道份额为 Bartik/GPSS 式外生 share, 乘以各 outlet 当年文章级 clarity_score 的 leave-one-out 均值(剔除焦点银行自身报道)。识别逻辑为——报道你的媒体爱不爱用模糊词是媒体自身持久的 house-style(Gentzkow & Shapiro 2010; Dougal et al. 2012), 由基期媒体组合决定, 外生于你这家银行当年的经营好坏, 却通过"你被写得清不清楚"进入结果方程。IV 主轨为 full, fallback 为 _ctx, ss 轨配同句 outlet 笔法工具 outlet_style_clarity_iv_ss 作第三主轨镜像。会计准则切换事件(IFRS 9、资管新规、监管检查标准变化)构造的 intensity DiD(注意是 intensity DiD 而非 staggered DiD, V4 技术更正)保留为候选工具, 待 M5 first-stage 后赛马。识别层面还有两点须写清: 其一, 本测度作为处理变量, 主轨 mean_clarity_score_full 与两条稳健性轨在 IV 设定中各自配备同轨工具(full 配 outlet_style_clarity_iv_full、ctx 配 _iv_ctx、ss 配 _iv_ss), 三轨各自 just-identified 并排, 严禁把三轨内生变量与多工具凑成 over-identified 的 Hansen J 联合检验, 因为三轨度量的是同一构念在不同文本窗口的重复测量、并非三个独立的过度识别矩; 其二, 结果变量(DV)在本论文中另行定义(provisional 阶段以 z_score 等占位变量名承载, 财务面板接入后替换为真实风险/融资结果列), 本家族只承担 treatment 一侧, 不应被误读为结果。

【与相邻测度的构念区分】
clarity 与本项目多个相邻文本测度刻意区分、互补而不重叠。与 LLM substance vote(avg_subst_prob_score)相比, clarity 度量的是"表达方式"(措辞确定性)而 substance 度量的是"内容实质性", 二者属 meta-level 不同层面; stage 39d 正是以 3×3 判别效度矩阵检验 clarity(A1)、num_intensity(A3, 数值密度, Davis & Tama-Sweet 2012 CAR 口径的互补清晰度)与 LLM substance(T1)三者的判别效度, 用 HTMT(双 cutoff strict<0.85 / lenient<0.90)、Fornell-Larcker φ² 与跨全部三指标的 Cronbach α 佐证三者非同一构念。与 boilerplate(套话比率)相比, 套话越多则可证伪的具体信息越少, 与 clarity 反向互补但机制不同, 故不与 clarity 同进一式、也不并入 clarity 的 PCA 综合指标。与情绪测度(tone)完全正交: clarity 只数明确/模糊词、不问褒贬。与 avg_named_entity(命名实体密度)因与 specificity 共线而被排除出 clarity 综合指标。与语义陈旧度(staleness, 整篇相似度)、篇内冗余(within_doc_redundancy)也正交: 前两者度量的是"这篇报道是不是新东西/有没有自我重复", 与"措辞清不清楚"是不同维度, 故不并入 clarity 的 PCA 综合指标。论文侧另定义了一个 composite_clarity_index, 是对 6 个替代清晰度测度做 PCA 取第一主成分, 但刻意不含 avg_named_entity(与 specificity 共线)、也不含 boilerplate 与 staleness(构念不同), 以保证综合指标只聚合"表达确定性"这一维度。判别效度审计的量化门槛为 HTMT strict<0.85 / lenient<0.90 双 cutoff(fix R4-M2), Cohen κ 方向锁定为"象征性(1)对应 clarity_score 低于中位数(1)、预期正 κ"(fix M2'), n_articles(b,t)≥2 的样本 mask(fix R8-H2), permutation seed 固定 42(与 inter_track_kappa 一致, fix R9-H3); 这些细节保证 clarity 与相邻测度的"可分性"是可复现、可审计的结论而非口头声明。

【已知局限与稳健性梯子】
三轨 full / ctx / ss 是本家族的核心稳健性梯子: full 轨为主处理轨(full-only 留篇门控 2026-06-29 后, 一篇报道是否算"银行金科报道"只看 full 轨判定), ctx / ss 降为 conditional-on-full 的稳健性孪生。三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁把 full×ctx×ss 混进同一 over-identified Hansen J(机械 _ctx→_ss swap 即触雷)。ss 轨为银行与金科同句共现轨, 语义镜像 ctx, 缺失时(旧 parquet 无 clarity_*_ss)聚合优雅跳过 ss 部分而不阻塞主轨。已知局限包括: (一)词典法受 You (2018)词表覆盖面约束, 388/178 词表对新兴金融科技新词的召回有限; (二)ambiguous 二值化阈值 median_amb_d0 在生产由 sidecar 冻结、各轨用自身分布中位数, 换语料须重新 freeze; (三)清晰度天然与文本长度、文体相关, 新闻文体的基线清晰度不可与年报文献直接比水平, 只可比标准化系数; (四)本机 T=2 dev 语料上 ctx/ss 轨方差高度退化, 各分布统计须在生产 T=18 语料上重估。判别效度审计(stage 39d)的 permutation seed 锁定为 42、n_articles(b,t)≥2 mask、Cronbach α 跨全部三指标计算等实施细节均已在 producer 内冻结。(五)本测度是词典法, 天然假设"明确/模糊"是词汇级可判定的属性, 无法捕捉语用层面的模糊(例如用明确的词说一件本质上不确定的事), 也无法处理反讽或语境反转; 若研究者需要语义级的确定性判定, 应改用 LLM substance vote 一族而非本家族, 二者在 stage 39d 已被证明是可分构念。(六)聚合权重 w_i = media_authority × herd_weight_track 的构造隐含"权威媒体、扩散早期报道更重要"的先验, 若某些应用不认同这一加权, 可退回等权均值作稳健性对照; 但本项目默认口径是加权, 与情绪、attention 等姊妹测度的聚合权重保持一致以便横向可比。(七)clarity 的绝对水平在新闻文体与年报文体之间不可直接比较——新闻天生比年报口语化、模糊词密度分布不同——因此论文披露明确要求跨文体只比标准化系数、不比原始水平; 同理, 换嵌入模型或换语料后须重新 freeze median_amb_d0 阈值, 冻结阈值文件跨语料不可复用, 否则二值化配套列 frac_amb_articles 会失真。(八)三轨梯子是本家族最重要的稳健性设计, 但也须警惕一个常见误用: 因为 full/ctx/ss 度量同一构念的不同文本窗口、彼此高度相关, 把它们塞进同一个过度识别的 Hansen J 联合检验在统计上是错误的(会把"重复测量"误当"多个独立矩条件"), 正确做法是三轨各自单独进 just-identified 设定、横向并排比较系数稳定性。以上局限均不改变本测度作为"媒体报道清晰度"这一构念的核心效度, 而是划定其适用边界与解读纪律。

## VAR: mean_clarity_score_full

【变体差分】
本列是家族 canonical 主列, tier=core, 对应 full 轨: 文章文本 = 标题 prepend + 全文正文(content_full), 即在完整报道正文上扫描 You (2018)的 definite/ambiguous 词表并计 clarity_score_full_i = frac_definite_full − frac_ambiguous_full, 再以 w_i = media_authority_weight × herd_weight_full 加权聚合到银行-年。与另两轨的精确区别在于文本覆盖面: full 轨用整篇报道正文, 信息量最大、口径最稳, 且分母 word-token 数最多, 使逐篇比率最不受短文本抖动影响。本列在所属论文 bank_news_clarity 中被指定为 treatment.primary(主处理变量), 也是 full-only 留篇门控(2026-06-29)下的主轨: 一篇报道是否被计入银行金科报道宇宙, 只由 full 轨判定, 因此 full 轨的行宇宙是三轨中的父集, ctx/ss 轨的留篇集是其子集。其内生性处理走 outlet_style_clarity_iv_full 工具变量(基期 outlet 份额 × outlet 文章级 clarity 的 leave-one-out 均值)。作为核心稳健性梯子的一员, full 轨与 ctx、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁将三轨混进同一 over-identified Hansen J(机械轨道 swap 即为违规)。相对 ctx/ss 的 conditional-on-full 稳健性定位, full 轨承担主结论, ctx/ss 承担"结论不被文本窗口选择驱动"的稳健性佐证。本列取值落在 [−1, +1], 正值表示媒体书写该银行时明确措辞占优、报道清晰, 负值表示模糊措辞占优; 加权分母 mask 到 clarity_score_full 非缺失的文章集, 空文/零 word-token 文章不进分母、不造成系统性下偏。生产阈值(用于配套的 frac_amb 二值化)由 full 轨自身分布中位数 median_amb_d0 冻结(首跑 in-sample freeze, 生产由 apply_v3_5_1 从 sidecar JSON 读回传入), 与 ctx/ss 各用自身分布阈值相互独立。就 producer 硬约束而言, clarity_frac_ambiguous_full / clarity_frac_definite_full / clarity_clarity_score_full 三个文章级 full 列是 aggregate_clarity_panel 的硬必需列(任缺则整体聚合跳过并返回空 diagnostics), 因此 full 轨在实现上是整条 clarity 面板链的骨架轨——ctx 是加性的、ss 是加性的, 唯 full 缺失会使整族 clarity 面板列不产出。这也解释了为何 full 被选为 canonical 主列: 它既是构念上信息量最大的完整正文轨, 又是工程上不可缺的必需轨。使用建议上, 论文主回归以本列为处理变量、辅以 outlet 笔法 IV 做内生性处理, 稳健性表则并列 ctx、ss 两轨系数以证明主结论不被文本窗口选择驱动; 三轨系数应各自单独进回归、互为稳健性, 不得合成过度识别检验。补充一个工程细节: 本列的加权分母 mask 到 clarity_score_full 非缺失的文章集, 因此当某银行-年内所有 full 轨报道都因空文/零 word-token 而无效时, 本列取 NaN 而非 0, 面板上须以缺失而非零处理以免把"无有效报道"误当"清晰度为零"。再从构念区分角度重申本列相对姊妹测度的独特性: mean_clarity_score_full 度量的是 full 轨报道措辞的确定性, 与同轨的情绪测度(如 llm_vote_tone_full、各词典 tone_full)正交——一篇报道可以既清晰又负面(明确地说这家银行出了问题)、也可以既模糊又正面(含糊地夸)——因此本列绝不可与情绪列混为一谈或相互替代。它与 full 轨的 substance / attention 测度也属不同 meta-level: substance 问"讲了多少实质内容", attention 问"讲了多少", clarity 只问"讲得清不清楚"。正因如此, 本列在 P5(bank_fintech_collab)中被借作 Table A7 稳健性对照时, 承担的是"叙事清晰度"这一独立信号, 与该论文主处理变量互补而非重叠。研究者若把本列作处理变量, 应确保结果方程里同时控制情绪与实质性测度, 以隔离出"清晰度"本身的边际效应, 避免遗漏变量把情绪或实质的效应误归给清晰度。最后从聚合权重角度补充本列相对两条稳健性轨的一处关键差异: full 轨的加权权重 w_i = media_authority_weight × herd_weight_full 中, herd_weight_full 是三轨 herd 权重的父本, ctx/ss 轨缺失自身 herd 权重时才优雅回退到 full 轨权重(fix herd-ghost-01), 因此 full 轨的聚合权重口径最完整、最不依赖回退, 这从加权分母的稳定性上进一步印证了 full 作为 canonical 主列的工程合理性。综上, 本列在构念(信息量最大的完整正文轨)、识别(treatment.primary 配 outlet 笔法 IV 主轨)、工程(整族 clarity 面板链不可缺的骨架轨)与权重(herd 权重父本、不依赖回退)四个层面同时构成家族主列, 其解读纪律为: 作水平比较仅限同文体、跨文体只比标准化系数, 作 IV 处理时须以同轨 outlet_style_clarity_iv_full 为工具、并与 ctx/ss 两轨系数横向并排而非合并为过度识别检验。

## VAR: mean_clarity_score_ctx

【变体差分】
本列 tier=standard, 对应 ctx 轨: 文章文本 = 标题 prepend + 实体上下文窗口(content_ctx), 即只在目标银行等实体附近的上下文片段上扫描 definite/ambiguous 词表并计 clarity_score_ctx_i, 再以 w_i = media_authority_weight × herd_weight_ctx 加权聚合。与 canonical full 轨的精确区别是文本覆盖面从整篇正文收窄到实体上下文窗口, 因此度量的是"媒体在具体谈及该银行的那些句子里"用词的清晰度, 剔除了与银行无关的段落噪声, 但代价是 word-token 分母更小、短窗口下比率更易抖动。在 full-only 留篇门控(2026-06-29)后, 本列由早期主轨降为 conditional-on-full 的首要稳健性孪生: 行宇宙是 full 轨留篇集的子集, per-track 列照算。ctx 轨的二值化阈值 median_amb_d0_ctx 用 ctx 轨自身分布的中位数(fix encode_collab-01, 不再套用 full 轨阈值), 与 full/ss 各自独立。本列与 full、ss 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。其配套内生性工具为 outlet_style_clarity_iv_ctx(IV fallback 轨)。本机 T=2 dev 语料上 ctx 轨可能方差退化, 分布统计须在生产 T=18 语料重估。取值同为 [−1, +1], 语义与 full 轨一致, 仅文本范围不同: full 覆盖整篇正文, ctx 只覆盖实体上下文窗口。作为稳健性轨, 本列的价值在于回答"如果只看记者真正谈到该银行的那些句子、把无关段落的清晰度噪声剔掉, 主结论是否依旧", 因此它与 full 轨互为稳健性、不分主次、各自 just-identified 并排, 严禁与 full/ss 混进同一 over-identified Hansen J。其对应的内生性工具 outlet_style_clarity_iv_ctx 是 IV 的 fallback 轨。需要留意的是, ctx 轨的 word-token 分母较小, 短窗口下逐篇比率抖动更大、极端值更多, 这既是它剔噪的代价, 也提示在解读 ctx 系数时应关注其相对 full 轨的方差放大。

## VAR: mean_clarity_score_ss

【变体差分】
本列 tier=standard, 对应 ss 轨: 文章文本 = 标题 prepend + 银行与金融科技同句共现窗口(content_ss, 银行∧金科同句 ±N 句半径), 即只在"银行与金科词同现的那些句子"上扫描 definite/ambiguous 词表并计 clarity_score_ss_i, 再以 w_i = media_authority_weight × herd_weight_ss 加权聚合。与 canonical full 轨的精确区别是文本覆盖面进一步收窄到银行金科同句共现片段, 度量的是"媒体在把该银行与金融科技绑在一起谈论时"的表达清晰度, 语义上镜像 ctx 轨但共现判据更严(同句而非实体窗口)。ss 轨的回退语义镜像 ctx: 当无银行金科同句共现时, ss 文本回退为全文正文并标记 ss_is_fallback=True; 本列所需的三个 ss 文章列(clarity_frac_ambiguous_ss / clarity_frac_definite_ss / clarity_clarity_score_ss)齐备时才与 ctx 平价聚合, 旧 parquet 缺 ss 列时聚合优雅跳过而不阻塞 full/ctx 主轨。二值化阈值 median_amb_d0_ss 用 ss 轨自身分布中位数(镜像 ctx, 各轨独立)。本列在 full-only 门控后属 conditional-on-full 稳健性轨, 与 full、ctx 两轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J(机械 _ctx→_ss swap 即触雷); 其配套 IV 为 outlet_style_clarity_iv_ss(三轨第三主轨镜像)。本机 T=2 dev 语料上 ss 轨常方差退化甚至近零, 属预期, 分布统计须在生产 T=18 语料重估。取值 [−1, +1], 语义同 full 轨, 仅文本范围与共现判据不同。就使用而言, ss 轨回答的问题最聚焦——"当媒体明确把这家银行和金融科技绑在一起讲时, 讲得清不清楚", 因此它对"银行金科叙事清晰度"这一细分构念的效度最高, 但也最易受同句共现稀疏与回退污染影响, 解读时应结合 ss_is_fallback 回退率(公共信号 frac_ctx_fallback 的 ss 对应量)一并披露。ss 轨与 full、ctx 三者构成本家族完整的三轨稳健性梯子, 三轨互为稳健性、不分主次。

<!-- rendered-citations:begin -->

<!-- rendered-citations:end -->
