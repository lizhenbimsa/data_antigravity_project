---
family_id: F542
columns:
- sum_wd_vw_gemini31_ctx
- sum_wd_vw_gemini31_full
- sum_wd_vw_gemini31_ss
unit: 无量纲权重之和 (关注度加权 vw 在有效样本上的分母加总, 非情感分)
formula: 'sum_wd_vw_gemini31_{track} = Σ_i mention_density_i · 1[gemini31_score{track}_i 非缺失], 其中 mention_density 为面板聚合前置构造的银行提及密度/关注度权重 (value-weight, 简称 vw), 三轨共用同一篇章级权重取值 (非逐 track 独立计算); 求和范围限定在 gemini31 该轨情感分有效 (非 NaN) 的文章 i 上, 三轨分母差异完全来自该 valid-mask 覆盖范围不同, 银行-年层面聚合。'
producer: pipeline\panel\runner.py::_build_llm_valid_masked_weights (核心权重构造, 步骤3b 内以单一 mention_density 权重 Series 对 VW 调用, 与 sum_mention_density 配对) ; pipeline\panel\encode.py (聚合 agg 字典 sum_wd_{wtag}_{grp}{track}, wtag='vw') ; pipeline\panel\encode.py (下游 _llm_denom 消费, 构造 gemini31_tone_vw_{track})
upstream:
- 21_tone_llms.parquet (gemini31_score_full/ctx/ss)
- 24_herd_decay_processor.parquet 或前置 mention_density 构造 (sum_mention_density 系列)
citations:
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: 'Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy'
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: Article eadp1528
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: "10.1287/mnsc.2021.03722"
  type: "journal"
  authors: "Cuñat, V., & Groen-Xu, M."
  year: 2025
  title: "Timing Complex News to Target Attention"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7774-7799"
- doi: "10.17016/feds.2025.022"
  type: "wp"
  authors: "Kroner, N."
  year: 2025
  title: "How Markets Process Macro News: The Importance of Investor Attention"
  venue: "Finance and Economics Discussion Series"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
new_dois: []
---

## CORE

【构念与来源】
sum_wd_vw_gemini31_{full,ctx,ss} 三列不是情感分本身, 而是三家投票 LLM 之一 gemini31 (gemini-3.1-flash-lite, 经 yunwu 中转) 在关注度加权 (value-weight, 简称 vw, 权重来源为 mention_density 银行提及密度) 体系下, 逐轨道有效样本上的权重分母之和。它服务于一个明确的下游用途: 与同族分子列 gemini31_score_w_sum_{track} (= Σ mention_density_i · gemini31_score_{track}_i, 权重 mention_density 三轨共用同一份取值) 相除, 得到银行-年层面"关注度加权后的 gemini31 情感均值" gemini31_tone_vw_{track} = gemini31_score_w_sum_{track} / sum_wd_vw_gemini31_{track}。vw 体系的经济学动机与 hw (跟风衰减权重)、mw (媒体权威权重) 并列但机制不同: vw 按银行在单篇报道中被提及的密度 (mention_density, 衡量该银行是该篇报道的核心主角还是仅被顺带提及的配角) 赋权, 让"整篇聚焦于该银行"的报道比"仅一笔带过"的报道在加权均值里贡献更大权重——文本对某一主体的关注强度本身携带信息, 不应与"仅提及一次"的边缘案例同等对待, 这一"按显著度加权而非简单算术平均"的构念取向与文本分析测度文献中普遍强调的"关注强度即信息"共识一致。
命名解析: 前缀 wd 是 weighted-denominator 的缩写, 与源码内部临时列 `_wd_vw_{short}{track}` (经 `_build_llm_valid_masked_weights(df, w, 'vw')` 构造, w 为三轨共用的篇章级 mention_density 权重 Series) 对应; 中段 vw 标记权重体系为关注度加权 (与另两体系 hw = herd-weight 跟风衰减权重、mw = media-weight 媒体权威权重并列, 三者产生同构但数值不同的 sum_wd_{hw,mw}_gemini31_{track} 系列, 分属另两个家族, 不与本族混用、不可加总); 末段 gemini31 标记该分母专属于三家 LLM 投票模型之一 gemini31, 与另两家 gpt54nano、deepseekv4 的同构分母 (sum_wd_vw_gpt54nano_{track}、sum_wd_vw_deepseekv4_{track}) 各自独立计算、互不借用, 因为三家模型各自的有效判定 (LLM 是否成功输出情感分、是否命中留篇门控) 可能不同步缺失, valid-mask 分母必须逐模型精确对齐分子, 才能保证"该模型该轨的加权均值只用该模型该轨真实有效的观测"这一基本聚合正确性。
【方法学与计算】
计算发生在 stage 21 (三家 LLM 情感投票产出 gemini31_score_{track}) 与 mention_density 前置构造之后、面板聚合 encode 阶段之内。具体地, `pipeline\panel\runner.py` 步骤3b 先取篇章级单一权重列 `df['mention_density']` (对 full/ctx/ss 三轨共用同一份权重取值, 而非逐轨独立计算; VW 场景权重是"三轨同权重", 与 hw 跟风衰减权重 "三轨独立权重" 的构造方式不同), 再对每一轨调用 `_build_llm_valid_masked_weights(df, w, 'vw')`: 该函数构造该轨专属的 valid-mask (gemini31_score_{track} 非缺失的布尔向量), 与共用权重 mention_density 逐元素相乘并按 mask 置 NaN 屏蔽无效行, 得到临时列 `_wd_vw_gemini31{track}`, 再由 encode.py 的 groupby-agg 字典对该临时列取 'sum' 得到银行-年层面的 sum_wd_vw_gemini31_{track}。此设计承接 encode-01 (metric-audit 2026-06-10) 对 LLM 族的一项关键修正: LLM 打分存在结构性缺失 (API 失败/缓存未命中/留篇门控未过), 若分子 Σ(w·score) 只在有效行求和而分母沿用物理全域 Σw, 则 Σ_valid(w·score)/Σ_all(w) 会随缺失率系统性向 0 收缩, 掩盖真实的加权语调水平; 改用 valid-mask 分母 sum_wd_vw_gemini31_{track} (即分母也只在同一有效行集合上求和) 后, 分子分母同域, 加权均值不再受缺失率干扰而失真。三轨 sum_wd_vw_gemini31_{full,ctx,ss} 彼此的差异因此并非来自 mention_density 本身逐轨不同 (VW 权重是同一份篇章级取值), 而完全来自各轨 gemini31_score_{track} 的 valid-mask 覆盖范围不同 (三家 LLM 各轨的 API 成功率/缓存命中/留篇门控通过情况互相独立、可能不同步缺失); 三条分母列因这一 valid-mask 差异而彼此不可加总、不可跨轨比较, 只能各自与同轨分子相除; 若某银行-年该轨全部文章的 gemini31 判分皆缺失, 分母将退化为 0, 下游相除以 NaN 兜底而非 0/0 静默产出 inf。
【文献定位】
关注度加权 (按文本对目标主体的着墨密度赋权, 而非简单算术平均) 的构念取向, 与 Gilardi, Alizadeh & Kubli (2023, Proceedings of the National Academy of Sciences) 关于 ChatGPT 类模型在文本标注任务上可比甚至超越众包人工标注员的证据所处的同一方法论脉络相通——该文强调标注任务中"文本-标签"对应关系的密度与质量本身携带可用信息, 一篇报道对目标银行着墨越多、该银行在文中被反复提及, 该篇报道传递的关于该银行的信息增量通常也越大, 简单算术平均会把"深度聚焦"与"顺带一提"的报道混为一谈, 系统性稀释真正相关报道的信号。三家 LLM (gpt54nano/gemini31/deepseekv4) 各自独立打分再各自加权聚合、互不预先融合, 这一设计呼应 Schoenegger, Tuminauskaite, Park, Bastos & Tetlock (2024, Science Advances) 关于 LLM 集成预测能力可比拟人群智慧 (wisdom of crowd) 的证据——多个独立评判者的分歧本身就是可用信息, 过早平均会抹去这一信息, 支撑本项目坚持"各模型 just-identified 并排、不预先融合"的方法论选择。LLM 作为文本标注工具的有效性亦见前述 Gilardi, Alizadeh & Kubli (2023, PNAS) 关于 ChatGPT 类模型在文本标注任务上可比甚至超越众包人工标注员的证据, 以及 van Atteveldt, van der Velden & Boukes (2021, Communication Methods and Measures) 对人工标注、众包、词典法与机器学习情感分析方法有效性的系统比较, 二者共同支撑本项目采用 LLM 投票而非纯词典法作为情感测度主轨、并对每种方法学选择 (含加权方案) 保留系统性稳健性检验的整体设计取向。
口径铁律复述: sum_wd_vw_gemini31 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验; ss 轨的回退语义镜像 ctx——当某篇文章不满足银行∧金科同句共现条件时, content_ss 回退为全文 body 且 ss_is_fallback=True, 该篇若 gemini31_score_ss 仍有效, 依然计入 sum_wd_vw_gemini31_ss 的分母 (回退不等于剔除, 只是文本窗口收窄失败后的优雅降级)。三家 LLM 的留篇门控口径统一为 full-only (2026-06-29 起): 是否判定"一篇银行金科报道"只看 llm_verified_full, ctx/ss 轨的 sum_wd_vw_gemini31_{ctx,ss} 因此是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 而非独立样本框; 三本列均属 per-model 独立降级机制的一部分——gemini31 若某轨缺失分数, 只影响 gemini31 自身该轨分母, 不连坐 gpt54nano/deepseekv4 的同轨分母, 也不同于 co-primary 嵌入双轨的 both-or-neither 规则。此外, vw 权重体系与 hw (跟风衰减)、mw (媒体权威) 三套权重各自独立构造、各自 just-identified, 三者不应在同一识别方程中混用或加总, 使用者须依据研究问题 (强调"聚焦度"用 vw、强调"去重复度"用 hw、强调"渠道权威性"用 mw) 择一为主, 其余互为稳健性检验。 在上述脉络之外, 近年前沿从两个方向补充了本族权重维度的文献坐标。其一是「报道非等权」的存在性证据: Cuñat 与 Groen-Xu (2025) 借助美国公司备案系统 5:30 p.m. 的制度断点 (截止前提交立即可见、截止后次晨才可见且吸引更少关注), 证明投资者注意力有限且时变, 发行方会据此策略性择时——把更长、更难处理的复杂新闻安排在注意力更高的时段发布, 且此类新闻随后价格收敛更快、流动性更好; Kroner (2025, 美联储 Finance and Economics Discussion Series 工作论文, 未经期刊同行评审) 则以宏观公告 × 投资者注意力代理估计高频市场反应, 表明同一条宏观新闻在注意力高低不同的时点被吸收的程度显著不同。两文所能支撑的仅是一条一般性命题——新闻条目在受众端的有效影响力随其被接收的显著性条件而变, 故「每篇报道等权计 1」并非无争议的默认口径, 这为 vw 族在分母中引入篇章级显著性权重留出了构念上的合理性空间; 必须明确的是, 二者均未构造、亦未检验任何文本端显著性权重, 更未比较加权与等权分母的优劣: Cuñat 与 Groen-Xu (2025) 的显著性维度是发布时点与日历制度断点, Kroner (2025) 的注意力代理是外生于文本的市场端交易/搜索类状态变量, 与本族 mention_density 这一篇内银行实体提及密度是完全不同的算子, 故不得引申为原文对 mention_density 取值口径的经验背书; 二文的层级分别为公司公告事件与美国宏观高频价格, 均不涉及 LLM 有效性掩码与 full/ctx/ss 三轨。其二是实体归属侧的测量误差证据: Iqbal 与 Pfarrer (2025) 指出情感分析在多主体文本中的情感归属上存在系统性测量误差 (传统方法易将文本误归于错误公司), 提出以共指消解作为解决方案, 并经两项研究证明该处理可降低测量误差、提升文本分析的真实性; 该文对本族的锚定仅止于「一项具体的语言学处理选择会系统性改变文本测度的取值、并构成实质性的测量误差来源」这一一般命题, 即着墨密度如何被计量本身就是需要被显式对待的方法学选择, 而非中性记账。严格边界须一并载明: 原文的处理是共指消解 (实体指代还原), 本项目在实体归属上的对应设计是 ctx/ss 实体窗口轨与 mention_density 的裸实体计数, 二者非同一手段, 本项目并未实施共指消解, 因而 mention_density 对代词回指的漏计仍是本列已知的测量局限, 而不是该文已为本列解决的问题; 原文立场是规范性的 (主张采纳该规则以减少误差), 而本项目令三轨、三家 LLM 与 vw/mw/hw 三套权重互为稳健性并排、各自 just-identified、不分主次, 二者方法学取向不同, 不得据以推定某一轨或某一权重方案为主; 原文语料为英文组织管理文本, 单位为文档/组织, 无银行-年面板层。
## VAR: sum_wd_vw_gemini31_full

【变体差分】
本列是 full 轨 (标题+全文正文, 未做实体窗口或同句截断) 上 gemini31 模型关注度加权权重的有效样本分母之和, 是三轨中样本覆盖最完整、mention_density 计算基础文本量最大的一支。full 轨承担留篇门控主责: 一篇文章是否被算作"银行-金科相关报道"完全由 llm_verified_full 决定, 因此 sum_wd_vw_gemini31_full 的分母集合 (gemini31_score_full 非缺失的文章集合) 与该银行-年最终留篇集合高度重合, 是 P1 主回归 treatment (llm_vote_tone_full 及其配套 per-model 稳健性测度) 计算加权均值时最常用的分母之一。mention_density (vw 权重来源) 本身是篇章级单一取值, 对 full/ctx/ss 三轨共用同一份权重 (VW 场景权重不逐轨独立计算, 区别于 hw 跟风衰减权重的三轨独立构造), 因此 full 轨与 ctx/ss 轨分母之间的差异并非来自权重本身不同, 而是来自各轨 gemini31_score_{track} 的 valid-mask 覆盖范围不同——full 轨凭借留篇门控主责地位, 通常拥有最宽的有效样本集合, 三轨分母仍不可互相替代或跨轨相加。若某银行-年 full 轨全部文章的 gemini31 判分皆缺失 (例如 API 调用失败且缓存未命中), 分母将退化为 0, 下游相除须显式处理除零 (工程实现以 NaN 兜底, 而非 0/0 静默产出 inf, 避免下游回归把该银行-年误当作真实零值样本纳入)。作为三轨中的锚定轨, full 轨分母还承担另一层功能性意义: 它是判断"某银行-年是否存在可用的 gemini31 vw 加权测度"这一可得性前提的主要依据——若 sum_wd_vw_gemini31_full 恰为 0 或缺失, 通常意味着该银行-年在留篇门控下根本没有 gemini31 有效打分的报道, 此时不仅 full 轨加权语调不可算, ctx/ss 轨 (作为 conditional-on-full 的子集测度) 大概率也同步不可算, 这与 co-primary 嵌入双轨的 both-or-neither 机制在效果上相似但成因不同 (前者是行宇宙嵌套导致的自然结果, 后者是显式的成对置空守卫)。使用者在做描述性统计或缺失值诊断时, 应优先核对本列而非直接核对分子列, 因为分母缺失必然导致比值不可算, 而分子偶发的零值 (Σ 加权分数恰好为 0, 例如该银行-年报道情感高度对称) 并不代表分母也缺失。

## VAR: sum_wd_vw_gemini31_ctx

【变体差分】
本列是 ctx 轨 (标题+目标银行实体窗口, 围绕银行名称截取的局部上下文而非全文) 上 gemini31 模型关注度加权权重的有效样本分母之和。需澄清一个易混淆点: mention_density (vw 权重来源) 是篇章级单一取值, 对 full/ctx/ss 三轨共用同一份权重, 并非 ctx 轨在局部实体窗口内重新计算得到, 因此 ctx 轨与 full 轨的关注度权重本身并无系统性差异; ctx 轨与 full 轨分母的真实偏离来源是各轨 gemini31_score_{track} 的 valid-mask 覆盖范围不同——一篇文章可能 full 轨判分成功而 ctx 轨判分缺失 (或反之), 使得两轨分母纳入的有效文章集合不完全重合, 而非窗口本身改变了权重取值。ctx 轨的留篇口径是 conditional-on-full: 只有 llm_verified_full 判定为真的文章才进入 ctx 轨的候选行宇宙, 但该文章在 ctx 轨自身是否被 gemini31 成功打分 (从而计入本列分母) 仍是独立事件, 属 per-model 独立降级——不会因为 full 轨命中就自动补全 ctx 轨分数。作为稳健性测度, sum_wd_vw_gemini31_ctx 与 sum_wd_vw_gemini31_full 配对构造的加权均值互为稳健性检验对象, 用于验证 P1 主结论是否对"情感测度到底基于全文还是基于银行实体局部窗口"这一构念选择敏感, 二者应各自 just-identified 单独进入回归, 不得混合进同一识别方程。ctx 轨窗口更聚焦于银行实体本身, 对于研究者关心"报道正文中围绕该银行的具体表述" (而非整篇报道的泛泛基调, 其中可能夹杂大量与该银行无直接关系的行业背景或宏观评论) 这一构念时, ctx 轨的 sum_wd_vw_gemini31_ctx 及其配对分子提供了比 full 轨更贴近该构念的加权基础, 但代价是窗口截取本身依赖实体识别的准确性, 若银行名称识别存在漏检或误检, ctx 轨窗口的边界会相应偏移, 这是 ctx 轨相对 full 轨的额外噪声来源, 也是三轨互为稳健性检验而非互相替代的实践理由之一。

## VAR: sum_wd_vw_gemini31_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句共现窗口, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制的句子半径, 默认±1句) 上 gemini31 模型关注度加权权重的有效样本分母之和, 是三轨中文本窗口最严格、最贴近"银行与金融科技同句提及"这一狭义构念的一支。当某篇文章不存在满足半径条件的银行∧金科同句共现时, content_ss 依 ss 轨回退语义整体退化为全文 body 且 ss_is_fallback=True (与 ctx 轨回退语义镜像对称), 此时该篇若 gemini31 仍成功输出 ss 轨情感分, 依然正常计入本列分母, 即"回退"改变的是文本窗口构造方式而非样本资格; 换言之 sum_wd_vw_gemini31_ss 的分母集合并不因回退而系统性缩小。须澄清: mention_density (vw 权重来源) 本身是篇章级单一取值, 对 full/ctx/ss 三轨共用同一份权重, 并不随 content_ss 是否回退而重新计算, 因此"回退"只影响该篇 ss 轨文本 (content_ss) 与情感打分输入, 不改变其 vw 权重取值, 使用者若要做纯"严格同句"子样本分析, 需额外结合 ss_is_fallback 标记做二次筛选。ss 轨同样遵循 full-only 留篇门控 (行宇宙为 full 留篇集合子集) 与 per-model 独立降级规则, sum_wd_vw_gemini31_ss 与另两轨分母各自 just-identified、互为稳健性、禁止混入同一 over-identified 识别方程。三轨分母间的真实差异全部来自各轨 gemini31_score_{track} 的 valid-mask 覆盖范围不同 (而非权重本身逐轨不同), sum_wd_vw_gemini31_ss 在银行∧金科同句共现比例较低的银行-年, 因 ss 轨文本回退为全文而与 full 轨情感打分趋于一致, 会与 sum_wd_vw_gemini31_full 高度趋同, 二者的边际差异主要来自"确有严格同句共现"的那部分文章子集; 这意味着 ss 轨作为稳健性检验的鉴别力 (discriminatory power) 随共现比例升高而增强, 使用者在解读 ss 轨与 full 轨加权均值的差异时, 宜同时报告该银行-年 ss_is_fallback 的比例作为解释上下文, 避免把"回退主导、几乎复刻 full 轨"的银行-年也当作"严格同句证据充分"的独立稳健性佐证。

<!-- rendered-citations:begin -->
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), Article eadp1528. https://doi.org/10.1126/sciadv.adp1528
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Cuñat, V., & Groen-Xu, M. (2025). Timing Complex News to Target Attention. Management Science, 71(9), 7774-7799. https://doi.org/10.1287/mnsc.2021.03722
Kroner, N. (2025). How Markets Process Macro News: The Importance of Investor Attention. Finance and Economics Discussion Series [Working Paper]. https://doi.org/10.17016/feds.2025.022
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
