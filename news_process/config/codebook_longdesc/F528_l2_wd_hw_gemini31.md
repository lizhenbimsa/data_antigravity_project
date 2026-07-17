---
family_id: F528
columns:
- sum_wd_hw_gemini31_ctx
- sum_wd_hw_gemini31_full
- sum_wd_hw_gemini31_ss
unit: 无量纲权重之和 (跟风衰减权重 hw 在有效样本上的分母加总, 非情感分)
formula: 'sum_wd_hw_gemini31_{track} = Σ_i hw_i{track} · 1[gemini31_score{track}_i 非缺失], 其中 hw = herd_weight (stage 24 跟风衰减权重, 逐 track 独立计算); 求和范围限定在 gemini31 该轨情感分有效 (非 NaN) 的文章 i 上, 银行-年层面聚合。'
producer: pipeline\panel\runner.py::_build_llm_valid_masked_weights (核心权重构造) ; pipeline\panel\runner.py (阈值敏感性/HW前置列生成) ; pipeline\panel\encode.py (聚合 agg 字典 sum_*_hw_sum / sum_wd_hw_*)
upstream:
- 24_herd_decay_processor.parquet (herd_weight_full/ctx/ss)
- 21_tone_llms.parquet (gemini31_score_full/ctx/ss)
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
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: It pays to write well
  venue: Journal of Financial Economics
  vol: '124'
  issue: '2'
  pages_or_artno: 373-394
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: "10.1080/19312458.2024.2378690"
  type: "journal"
  authors: "Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K."
  year: 2025
  title: "On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions"
  venue: "Communication Methods and Measures"
  vol: "19"
  issue: "1"
  pages_or_artno: "46-62"
- doi: "10.2139/ssrn.5395056"
  type: "wp"
  authors: "Liu, Y., Liu, J., & Wang, T."
  year: 2025
  title: "Large Language Model Disagreement"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "5395056"
new_dois: []
---

## CORE

【构念与来源】
sum_wd_hw_gemini31_{full,ctx,ss} 三列不是情感分本身, 而是三家投票 LLM 之一 gemini31 (gemini-3.1-flash-lite, 经 yunwu 中转) 在跟风衰减加权 (herd-weight, 简称 hw) 体系下, 逐轨道有效样本上的权重分母之和。它服务于一个明确的下游用途: 与同族分子列 gemini31_score_hw_sum_{track} (= Σ hw_i · gemini31_score_{track}_i) 相除, 得到银行-年层面"跟风衰减加权后的 gemini31 情感均值" = gemini31_score_hw_sum_{track} / sum_wd_hw_gemini31_{track}。若直接用简单平均 (mean) 聚合逐篇情感, 会把"扎堆跟风、内容高度雷同"的报道与"独立信息含量高"的报道同等对待; herd-weight 机制 (源码注释标注 Tetlock (2011, Review of Financial Studies) 的跟风/媒体聚集思想) 对每篇文章按其与同期同银行报道的相似度施加衰减权重, 相似度越高 (越像"抄稿"或跟风重复) 权重越低。sum_wd_hw_gemini31_{track} 正是这套衰减权重在"gemini31 该轨情感分非缺失"这一有效样本上的加总, 充当加权平均的分母, 因此单位不是情感强度而是"有效权重质量" (无量纲, 理论上界为该银行-年 gemini31 该轨有效篇数, 下界随衰减程度趋近于 0)。
命名解析: 前缀 wd 是 weighted-denominator 的缩写, 与源码内部临时列 `_wd_hw_{short}{track}`(经 `_build_llm_valid_masked_weights(df, hw_by_track, 'hw')` 构造) 对应; 中段 hw 标记权重体系为跟风衰减权重 (与另一体系 mw = media-weight 媒体权重并列, 后者产生同构的 `sum_wd_mw_gemini31_{track}` 系列, 属另一家族, 不与本族混用); 末段 gemini31 标记该分母专属于三家 LLM 投票模型之一 gemini31, 与另两家 gpt54nano、deepseekv4 的同构分母 (`sum_wd_hw_gpt54nano_{track}`、`sum_wd_hw_deepseekv4_{track}`) 各自独立计算、互不借用, 因为三家模型各自的有效判定 (LLM 是否成功输出情感分、是否命中留篇门控) 可能不同步缺失, valid-mask 分母必须逐模型精确对齐分子。
【方法学与计算】
计算发生在 stage 21 (三家 LLM 情感投票) 与 stage 24 (herd_decay_processor 产出 herd_weight_full/ctx/ss) 之后、面板聚合 encode 阶段之内。具体地, `_build_llm_valid_masked_weights` 先构造逐模型 valid-mask (gemini31_score_{track} 非缺失的布尔向量), 与该轨 herd_weight_{track} (缺失时 fillna 为 1.0, 即不衰减) 逐元素相乘并按 mask 置 NaN 屏蔽无效行, 再由 encode.py 的 groupby-agg 字典对该临时列取 'sum' 得到银行-年层面的 sum_wd_hw_gemini31_{track}。三轨 full/ctx/ss 的 herd_weight 各自独立计算 (即"三轨独立权重", 与历史遗留的单轨 legacy 权重路径二选一, 由 `has_dual_hw` 判定源 parquet 是否具备三轨列), 因此三条分母列彼此不可加总、不可跨轨比较, 只能各自与同轨分子相除。
【文献定位】
跟风衰减权重的经济学动机是媒体报道的相互抄袭与羊群式跟风会稀释单篇报道的信息增量, 这一构念可追溯到 Tetlock (2011) 对媒体聚集 (media herding) 的讨论。三家 LLM (gpt54nano/gemini31/deepseekv4) 各自独立打分再各自加权聚合、互不预先融合, 这一"多裁判各自独立、事后横向比较而非事前平均"的设计呼应 Schoenegger, Tuminauskaite, Park, Bastos & Tetlock (2024, Science Advances) 关于 LLM 集成 (ensemble) 预测能力可比拟人群智慧 (wisdom of crowd) 的证据——多个独立评判者的分歧本身就是可用信息, 过早平均会抹去这一信息, 这正是本项目坚持"各模型 just-identified 并排、不预先融合"的方法论依据。LLM 作为文本标注工具的有效性另见 Gilardi, Alizadeh & Kubli (2023, PNAS) 关于 ChatGPT 类模型在文本标注任务上可比甚至超越众包人工标注员的证据, 以及 van Atteveldt, van der Velden & Boukes (2021, Communication Methods and Measures) 对人工标注、众包、词典法与机器学习情感分析方法有效性的系统比较, 二者共同支撑本项目采用 LLM 投票而非纯词典法作为情感测度主轨的选择。加权平均而非简单平均对文本测度稳健性的价值, 也与 Hwang & Kim (2017, Journal of Financial Economics) 关于文本写作质量 (可读性/清晰度) 对信息含量与市场反应存在系统性影响的发现相呼应——文本本身的可读性与重复度差异并非噪声, 而是应被显式建模而非平均掉的结构性特征, 这也是本项目引入 herd-weight 而非直接对逐篇情感取算术平均的核心理由。
口径铁律复述: sum_wd_hw_gemini31 三轨 (full/ctx/ss) 各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验; ss 轨的回退语义镜像 ctx——当某篇文章不满足银行∧金科同句共现条件时, content_ss 回退为全文 body 且 ss_is_fallback=True, 该篇若 gemini31_score_ss 仍有效, 依然计入 sum_wd_hw_gemini31_ss 的分母 (回退不等于剔除, 只是文本窗口收窄失败后的优雅降级)。三家 LLM 的留篇门控口径统一为 full-only (2026-06-29 起): 是否判定"一篇银行金科报道"只看 llm_verified_full, ctx/ss 轨的 sum_wd_hw_gemini31_{ctx,ss} 因此是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 而非独立样本框; 三本列均属 per-model 独立降级机制的一部分——gemini31 若某轨缺失分数, 只影响 gemini31 自身该轨分母, 不连坐 gpt54nano/deepseekv4 的同轨分母, 也不同于 co-primary 嵌入双轨的 both-or-neither 规则。 就本家族分母所依赖的有效性掩码前提, Laurer、Casas 与 Welbers (2025) 以对照实验证明指令/提示设计会实质改变语言模型作为测量工具的效度与偏误, 提示「gemini31 在该轨给出有效判断」这一掩码本身即模型效度的函数, 从而使分母的样本覆盖面成为一个需被显式披露的效度变量; 但该文对象是传播学英文文本分类任务与开源指令微调模型, 其「加指令可提效度」的结论与本项目嵌入侧刻意零 instruct 前缀、情感提示词 v8 已字节冻结的设计取向不同, 且原文不含权重加权分母口径, 故只作效度前提的方法学锚定。Liu、Liu 与 Wang (2025) 以金融文本为对象度量并实证刻画了不同大语言模型判断的分歧程度, 恰可解释为何 gemini31 与 gpt54nano/deepseekv4 的同名 hw 分母彼此不同——差异完全源于各家有效打分覆盖面的不重合, 这与上述 per-model 独立降级机制互为表里; 但该文系 SSRN 工作论文尚未经同行评审, 且其把分歧本身当作信号/噪声变量加以研究, 本项目不将分歧入模, 仅以各家有效性掩码构造各自独立的分母, 模型集合与语料亦与本项目不同。
## VAR: sum_wd_hw_gemini31_full

【变体差分】
本列是 full 轨 (标题+全文正文, 未做实体窗口或同句截断) 上 gemini31 模型跟风衰减权重的有效样本分母之和, 是三轨中样本覆盖最完整、权重稳定性最高的一支。full 轨承担留篇门控主责: 一篇文章是否被算作"银行-金科相关报道"完全由 llm_verified_full 决定, 因此 sum_wd_hw_gemini31_full 的分母集合 (gemini31_score_full 非缺失的文章集合) 与该银行-年最终留篇集合高度重合, 是 P1 主回归 treatment (llm_vote_tone_full 及其配套 per-model 稳健性测度) 计算加权均值时最常用的分母。由于 full 轨文本量最大, herd_weight_full 的相似度判据在更长文本上计算, 对"整段照抄"式跟风的识别力通常强于短窗口轨道, 但也更容易被无关背景段落稀释相似度信号, 因此其衰减幅度与 ctx/ss 轨系统性不同, 三轨分母不可互相替代或跨轨相加。该列在与 gemini31_score_hw_sum_full 配对构造加权均值时, 若某银行-年 full 轨全部文章的 gemini31 判分皆缺失 (例如 API 调用失败且缓存未命中), 分母将退化为 0, 下游相除须显式处理除零 (通常在聚合脚本以 NaN 兜底, 而非 0/0 静默产出 inf)。使用者若拿本列与另两家 LLM 的同轨分母 (sum_wd_hw_gpt54nano_full、sum_wd_hw_deepseekv4_full) 直接比较绝对量级, 需先意识到三者虽同属 full 轨、共享同一 herd_weight_full 权重来源列, 但各自的 valid-mask (即哪些文章该模型成功输出了情感分) 并不完全重合——某篇文章可能 gpt54nano 判分成功而 gemini31 因 API 超时判分缺失, 此时该篇计入前者分母却不计入本列分母, 三个分母因此在同一银行-年内可以有细微差异, 这一差异本身不构成误差, 而是 per-model 独立降级设计的自然结果, 不应被误读为数据质量问题。分析者若要严格核对 full 轨的加权均值是否可靠, 建议同时报告本列取值 (即有效权重质量) 而非只报告加权均值本身, 因为分母过小的银行-年 (例如仅 1-2 篇有效报道) 其加权均值稳健性天然弱于分母充足的银行-年, 这一点在样本量小的早期年份 (如 T=2 开发子集) 尤须留意。

## VAR: sum_wd_hw_gemini31_ctx

【变体差分】
本列是 ctx 轨 (标题+目标银行实体窗口, 围绕银行名称截取的局部上下文而非全文) 上 gemini31 模型跟风衰减权重的有效样本分母之和。与 full 轨相比, ctx 轨文本窗口更窄、更聚焦于银行实体周边表述, 因此 herd_weight_ctx 的相似度判据是在更短、更同质化的文本片段上计算的——多篇报道即便全文差异很大, 若都摘引同一段监管公告或财报数据作为银行实体窗口, ctx 轨的相似度反而可能偏高, 导致衰减更重, 这是 ctx 轨分母与 full 轨分母系统性偏离的机制来源之一。ctx 轨的留篇口径是 conditional-on-full: 只有 llm_verified_full 判定为真的文章才进入 ctx 轨的候选行宇宙, 但该文章在 ctx 轨自身是否被 gemini31 成功打分 (从而计入本列分母) 仍是独立事件, 属 per-model 独立降级——不会因为 full 轨命中就自动补全 ctx 轨分数。作为稳健性测度, sum_wd_hw_gemini31_ctx 与 sum_wd_hw_gemini31_full 配对构造的加权均值互为稳健性检验对象, 用于验证 P1 主结论是否对"情感测度到底基于全文还是基于银行实体局部窗口"这一构念选择敏感, 二者应各自 just-identified 单独进入回归, 不得混合进同一识别方程。由于 ctx 轨文本天然短于 full 轨, herd_weight_ctx 的相似度计算所依赖的词汇/句法特征空间更稀疏, 在样本量不大的银行-年内容易出现"多篇报道 ctx 窗口几乎逐字重合"的极端情形 (例如都只截取了同一句监管处罚通报), 使得 sum_wd_hw_gemini31_ctx 相对 sum_wd_hw_gemini31_full 呈现更陡峭的衰减, 分母绝对值系统性偏小; 这并非测量误差, 而是 ctx 轨构念本身 (聚焦实体局部语境而非全篇论述) 决定的正常特征。使用者在跨轨比较分母量级时, 应始终把它理解为"该轨道下的有效权重质量", 而非可直接跨轨相加或替代的样本量代理; 若需要评估 ctx 轨相对 full 轨的信息稀释程度, 更稳妥的做法是比较两轨加权均值的差异及其标准误, 而非直接比较两个分母列本身的数值大小。

## VAR: sum_wd_hw_gemini31_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句共现窗口, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制的句子半径, 默认±1句) 上 gemini31 模型跟风衰减权重的有效样本分母之和, 是三轨中文本窗口最严格、最贴近"银行与金融科技同句提及"这一狭义构念的一支。当某篇文章不存在满足半径条件的银行∧金科同句共现时, content_ss 依 ss 轨回退语义整体退化为全文 body 且 ss_is_fallback=True (与 ctx 轨回退语义镜像对称), 此时该篇若 gemini31 仍成功输出 ss 轨情感分, 依然正常计入本列分母, 即"回退"改变的是文本窗口构造方式而非样本资格; 换言之 sum_wd_hw_gemini31_ss 的分母集合并不因回退而系统性缩小, 但回退样本的 herd_weight_ss 相似度判据实际上是在 full-body 文本上计算的 (retreated 到与 full 轨同样的输入), 只是仍归入 ss 轨列名下, 使用者若要做纯"严格同句"子样本分析, 需额外结合 ss_is_fallback 标记做二次筛选。ss 轨同样遵循 full-only 留篇门控 (行宇宙为 full 留篇集合子集) 与 per-model 独立降级规则, sum_wd_hw_gemini31_ss 与另两轨分母各自 just-identified、互为稳健性、禁止混入同一 over-identified 识别方程。就构念严格度而言, ss 轨是三轨中对"银行与金融科技话题在同一叙述单元内被共同讨论"这一狭义假设要求最高的一支, 未回退样本的 herd_weight_ss 相似度判据仅在极窄的同句片段上计算, 极易因句式高度模板化 (如新闻通稿常见的"XX银行与YY金科达成战略合作"句式) 而出现多篇报道同句雷同, 从而触发较重的跟风衰减; 回退样本则如前述退化为 full-body 计算, 衰减特征更接近 full 轨。这意味着 sum_wd_hw_gemini31_ss 内部实际上混合了两种不同生成机制的观测 (严格同句 vs. 回退全文), 若研究设计需要排除回退样本的干扰, 应结合 ss_is_fallback 标记做子样本重新聚合, 而不能假定本列在所有银行-年上都反映同一严格构念下的权重质量; 这一点是 ss 轨区别于 full/ctx 两轨 (二者均无镜像回退机制) 的关键差分, 使用前须予以说明。
<!-- rendered-citations:begin -->
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), Article eadp1528. https://doi.org/10.1126/sciadv.adp1528
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
Liu, Y., Liu, J., & Wang, T. (2025). Large Language Model Disagreement. SSRN Electronic Journal No. 5395056 [Working Paper]. https://doi.org/10.2139/ssrn.5395056
<!-- rendered-citations:end -->
