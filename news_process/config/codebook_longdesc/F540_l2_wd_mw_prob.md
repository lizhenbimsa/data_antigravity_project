---
family_id: F540
columns:
- sum_wd_mw_prob_ctx
- sum_wd_mw_prob_full
- sum_wd_mw_prob_ss
unit: 无量纲权重和 (媒体权威度权重之和, 非情感分数本身)
formula: 'sum_wd_mw_prob{track} = Σ_i media_authority_weight_i · 1{llm_prob_score{track}_i 非缺失}, i 遍历该银行-年全部留篇文章 (留篇门控见下)'
producer: pipeline/panel/runner.py::_build_llm_valid_masked_weights (生成逐篇有效性掩码权重 `_wd_mw_prob{track}`); pipeline/panel/encode.py (groupby.sum 聚合为面板列 `sum_wd_mw_prob{track}`)
upstream:
- 21_tone_llms (提供 llm_prob_score{track} 与其缺失标记)
- 步骤3c media_authority 加权列 (媒体权威度权重 mw, Holzman 2023 口径)
citations:
- doi: 10.1145/1102351.1102430
  type: wp
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: Predicting good probabilities with supervised learning
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.2307/1914121
  type: journal
  authors: Manski, C. F., & Lerman, S. R.
  year: 1977
  title: The estimation of choice probabilities from choice based samples
  venue: Econometrica
  vol: '45'
  issue: '8'
  pages_or_artno: 1977-1988
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: The Validity of Sentiment Analysis - Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: Text-based sentiment analysis in finance - Synthesising the existing literature and exploring future directions
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
new_dois: []
---

## CORE

【构念与来源】
本家族 F540 的三个列 sum_wd_mw_prob_ctx / sum_wd_mw_prob_full / sum_wd_mw_prob_ss, 度量的不是情感、不是态度、也不是任何语义构念本身, 而是一个纯粹的核算辅助量: 某银行在某年份的全部留篇报道中, "LLM 概率化语调分数 (llm_prob_score) 有效可用" 的那些文章, 其媒体权威度权重 (media weight, 简称 mw) 之和。它是 F379 家族 (llm_prob_score_mw_sum, 即媒体权威度加权的 LLM 概率语调分子) 的配对分母, 二者相除才构成一个完整的加权平均语调指标: MW-weighted llm_prob_score = llm_prob_score_mw_sum{track} / sum_wd_mw_prob{track}。脱离分子单独看，本列不能被解读为"某种语调水平"，它只回答一个核算问题: 在加权平均的分母里，究竟应该数哪些文章的权重。

本列的存在源于一个具体的、已被项目记录在 encode.py 注释中的度量偏误修正 (encode-01, 2026-06-10 metric-audit)。LLM 概率化语调分数 llm_prob_score{track} 并非对每一篇留篇文章都有值: 当 stage 21 的 logit-to-score 概率转换模块因判定门控 (LOGIT_SCORE_ENABLED) 或模型侧解析失败而未产出有效分数时, 该文章在 llm_prob_score{track} 上取值缺失 (nullable NA)。如果在做媒体权威度加权平均时, 分子只累加"确有 llm_prob_score 有效值"的文章 (Σ weight_i · score_i, 缺失行天然被 pandas sum 跳过), 但分母却仍然使用该银行-年"全部文章"的权重和 (物理域 Σ weight_i, 不管 score 是否缺失), 就会出现分子分母定义域不一致的系统性偏误: 缺失值被隐性当作 "语调 = 0" 计入了分母, 导致加权平均语调被系统性地向零压低, 且压低幅度随该银行-年缺失率的升高而增大 — 这是一种隐蔽的、不易在描述统计中被察觉的度量偏误, 而非随机噪声。

修正方案是给每一种加权口径 (vw/mw/hw) 各配一个"仅计入有效文章"的分母列, 让分子分母共享同一个定义域 (validity domain)。本家族 sum_wd_mw_prob{track} 正是 mw 权重族在 prob 分组下的有效性掩码分母: producer 函数 `_build_llm_valid_masked_weights` 对每一篇文章生成 `_wd_mw_prob{track} = media_authority_weight · 1{llm_prob_score{track} 非缺失}` (即把媒体权威度权重在 llm_prob_score 缺失处置为 NaN, 有效处保留原权重), encode.py 随后用标准 pandas groupby.sum 在银行-年层面累加这一逐篇列, 得到面板列 sum_wd_mw_prob{track}。因 NaN 在 groupby('sum') 中被自动跳过, 该和天然只覆盖 llm_prob_score{track} 有效的文章子集, 与分子 llm_prob_score_mw_sum{track} 的定义域完全一致。

【方法学与计算】
计算分三层。第一层 (stage 21): 每篇留篇文章的三家 LLM (gpt54nano/gemini31/deepseekv4) 投票产生分类语调, 若 logit-to-score 转换开启且解析成功, 额外产出连续概率化分数 llm_prob_score{track} ∈ [-1, +1] (P(正面) − P(负面) 的差, 与三家多数投票的离散 llm_vote_score 是并行但独立的两条测度)。第二层 (步骤3c, runner.py): 为每篇文章计算媒体权威度权重 media_authority_weight (mw, Holzman 2023 口径, 反映报道所属媒体来源的行业权威性/影响力差异), 并调用 `_build_llm_valid_masked_weights(frame, weight=media_authority_weight, wtag='mw')`, 对三轨分别生成 `_wd_mw_llm{track}` (对应 llm_vote 族)、逐模型的 `_wd_mw_{short}{track}`、以及本家族对应的 `_wd_mw_prob{track}` (对应 llm_prob_score 族) 三类掩码权重列, 命名统一遵循 `_wd_{wtag}_{group}{track}` 模板 (wd 取"weight-denominator"之意)。第三层 (encode.py 聚合): 对上述逐篇掩码列在银行-年层面求和, 落盘为面板列 sum_wd_mw_prob{track} = Σ_i media_authority_weight_i, 求和范围严格限定在该银行-年内 llm_prob_score{track} 非缺失的文章。

零填契约: 若某银行-年不存在任何留篇报道 (Σ over 空集), 该列在 balance_panel 阶段按"计数/和"类列的统一契约填 0 (与 sum_mention_density / sum_herd_weight_* 等兄弟列同规则), 而非留空; 后续在计算加权平均语调时, 分母 0 会先经 `.replace(0, np.nan)` 处理避免除零, 这是消费端 (encode.py `_llm_denom` 辅助函数) 的职责, 与本列自身的零填契约互不冲突。

三轨口径 full/ctx/ss 各自独立计算、并排存在, 互为稳健性、不分主次, 严禁在同一 over-identified 的 Hansen J 检验中同时纳入三轨对应的加权语调及其分母 (会人为夸大工具数、破坏刚好识别结构)。留篇门控口径与全项目一致: 是否构成"一篇有效的银行-金科报道"由 full 轨 `llm_verified_full == True` 唯一判定 (2026-06-29 起的 full-only 门控), ctx/ss 轨是在同一留篇行宇宙 (full 的子集) 上的 conditional-on-full 测度/稳健性轨, 而非独立样本; ss 轨的回退语义镜像 ctx 轨: 若某文章不存在银行与金科词汇的同句共现, `content_ss` 回退为全文正文, 对应 `ss_is_fallback=True`, 与 ctx 轨共享同一 n_articles 分母口径, 而非另起炉灶。当 llm_prob_score{track} 因某轨整体不可用 (如该轨概率转换模块关闭) 而全体缺失时, sum_wd_mw_prob{track} 会退化为 0 或全 NaN (视上游是否产出该轨源列而定), 属优雅降级而非报错。

【文献定位】
把加权平均的分子分母限定在同一有效性域内, 是概率化度量与文本情感测度交叉领域的常见方法学要求。Niculescu-Mizil & Caruana (2005) 系统讨论了监督学习模型输出"良好校准概率"的必要性与常见陷阱, 其核心洞见——概率分数若在聚合前未与其有效性掩码对齐, 汇总统计量会系统性偏离真实水平——为本列的构造逻辑提供了方法论支撑。Manski & Lerman (1977, *Econometrica*) 关于从基于选择的样本 (choice-based sample) 估计选择概率的经典工作, 确立了概率型测度在非随机缺失/筛选样本下必须显式建模纳入域, 否则估计量有偏, 这一原则同构地适用于本列所修正的"缺失即视为零"偏误。van Atteveldt et al. (2021) 比较人工编码、众包、词典与机器学习方法在情感分析效度上的差异, 指出机器学习/LLM 类方法产出的连续概率化分数在跨方法比较与加权聚合时需要格外注意样本对齐问题, 为本项目将 LLM 概率化语调 (llm_prob_score) 与其掩码分母同域配对提供了外部佐证。Gilardi, Alizadeh & Kubli (2023, *Proceedings of the National Academy of Sciences*) 展示了 LLM 在文本标注任务上可产出优于众包工的分类结果, 印证了将 LLM 输出的概率化分数纳入银行-年面板加权测度体系的合理性, 同时也提示此类分数的可用率并非恒定 100%——校准掩码分母正是应对这一现实的工程手段。Todd, Bowden & Moshfeghi (2024) 对金融文本情感分析文献的系统综述, 明确将"基于概率的情感分数聚合"列为该领域方法学演进的方向之一, 为本家族在项目情感测度矩阵中的定位 (LLM 概率轨 × 媒体权威度加权 × 三轨) 提供了文献坐标。

## VAR: sum_wd_mw_prob_ctx

【变体差分】
本列是家族 canonical 三轨之一, 对应 ctx (实体窗口) 轨: 上游 llm_prob_score_ctx 的有效性判定基于 content_ctx (标题 + 目标银行实体窗口文本) 上 stage 21 的概率化语调转换结果, media_authority_weight 权重本身不分轨 (媒体权威度是报道来源属性, 与文本裁剪方式无关), 但掩码依据——即"哪些文章计入求和"——严格由 ctx 轨自身的 llm_prob_score_ctx 缺失模式决定, 与 full 轨、ss 轨的缺失模式可能不同 (例如某文章 ctx 轨因实体窗口过短导致概率转换解析失败, 但 full 轨解析成功, 此时该文章只计入 sum_wd_mw_prob_full 而不计入 sum_wd_mw_prob_ctx)。因此三列虽共享同一权重来源 media_authority_weight, 其和的数值一般并不相等，差异直接反映三轨各自的 llm_prob_score 有效覆盖率差异。

留篇行宇宙: ctx 轨的求和范围仍是 full-only 门控下的留篇集合 (`llm_verified_full == True` 的文章), ctx 只是在这一行宇宙内, 用 content_ctx 文本重新跑一遍概率化语调转换与掩码, 属于 conditional-on-full 的稳健性测度, 不是独立抽样。当某银行-年该轨源列 llm_prob_score_ctx 整体缺失 (如概率转换模块未对 ctx 轨启用) 时, 本列按空求和 (0) 或全 NaN 优雅降级, 不会导致下游加权语调计算崩溃, 消费端 encode.py 的 `_llm_denom` 会以 `col in panel.columns` 守卫 + `.replace(0, np.nan)` 兜底除零。本列与 sum_wd_mw_prob_full / sum_wd_mw_prob_ss 之间严格互为稳健性、不分主次, 三者构成的三个 MW-weighted llm_prob_score 加权语调各自 just-identified, 分析中应并排报告而非相互替代或混入同一过度识别的工具变量检验。ctx 轨相对 full 轨的方法学价值在于剥离掉正文中与目标银行无直接实体关联的段落噪声, 更贴近"围绕该银行本身的论述口吻"这一构念, 但代价是窗口截断可能造成的信息损失与概率转换失败率上升, 这正是本列 (而非 full 轨同名列) 数值系统性偏低或偏高的常见原因之一。

## VAR: sum_wd_mw_prob_full

【变体差分】
本列对应 full 轨 (标题 + 完整正文), 是三轨中的口径基准与留篇门控本身所在的轨: 是否将某篇文章计入该银行-年的"有效报道"集合, 唯一由 full 轨的 `llm_verified_full == True` 判定 (2026-06-29 起生效的 full-only 门控), 因此本列的求和范围本质上就是该银行-年 llm_prob_score_full 在留篇集合内的有效覆盖情况, 不存在 ctx/ss 轨那样的"行宇宙子集嵌套"关系——它就是行宇宙本身在 prob 测度上的有效性掩码。

尽管 full 轨承担留篇门控职责, 本列在 MW 加权体系内仍与 ctx、ss 两个同族列并排, 而非享有"主测度"地位: 项目铁律明确三轨口径各自 just-identified, 互为稳健性, 不设主次之分, 主回归表通常以 full 轨作报告起点, 但这是叙事习惯而非统计意义上的优先级。full 轨相对 ctx/ss 轨的方法学特征是纳入全文语境, 概率化转换在完整信息下进行, 一般覆盖率 (llm_prob_score_full 非缺失比例) 较高, 因此 sum_wd_mw_prob_full 通常在同一银行-年内不小于 sum_wd_mw_prob_ctx 与 sum_wd_mw_prob_ss (但因三者掩码来源独立, 这不是数学保证, 只是经验规律)。零文章银行-年在 balance_panel 阶段填 0, 与 n_articles / sum_mention_density 等计数类列同契约; 与 F379 家族的 llm_prob_score_mw_sum_full 配对构成完整的 MW-weighted 概率语调平均, 二者必须成对使用, 单独使用分母列本身不具备情感解读意义。

## VAR: sum_wd_mw_prob_ss

【变体差分】
本列对应 ss 轨 (银行∧金科同句共现窗口): 掩码依据是 llm_prob_score_ss 在该轨文本 content_ss 上的概率化语调转换结果是否有效。ss 轨的判定原语与 ctx 轨不同——ctx 用实体窗口, ss 要求银行与金科词汇在同一句内共现——因此 ss 轨的 llm_prob_score_ss 缺失模式往往比 ctx 轨更稀疏 (回退发生率更高)。当某篇留篇文章不存在银行∧金科同句共现时, content_ss 按项目铁律回退为全文正文 (镜像 ctx 轨的回退语义), 对应标记列 ss_is_fallback=True, 此时该文章是否仍计入 sum_wd_mw_prob_ss 取决于回退后的 content_ss (即等同全文) 上概率化转换是否成功解析, 与是否发生回退是两件独立的事: 回退只决定"喂给概率转换模块的文本是什么", 不直接决定"转换是否成功"。ss 轨与 ctx 轨共享同一个 n_articles 分母口径 (both 依赖 fallback 标记维护行宇宙一致性), 但 sum_wd_mw_prob_ss 本身作为 MW 权重的有效性掩码和, 是 prob 测度族在 ss 轨上的独立产物, 不与 ctx 轨的对应列相加或替代。

三轨互为稳健性的铁律在此同样适用: sum_wd_mw_prob_ss 与 sum_wd_mw_prob_full、sum_wd_mw_prob_ctx 各自 just-identified 并排, 严禁混入同一过度识别的 Hansen J 检验框架。ss 轨的方法学价值在于最严格地锁定"银行与金融科技话题被同一句话直接关联提及"的语境, 排除了 ctx 轨可能纳入的"同段落但不同句"式松散关联, 因而当报道中银行与金科话题被并列讨论但语调判断本身较为特定于该并列语境时, ss 轨的概率化分数与其对应的 MW 权重掩码和最能反映"紧密语境下的媒体权威度加权语调水平"这一构念; 但由于同句共现门槛更高, 该列在样本覆盖率与统计功效上通常弱于 full/ctx 两轨, 稳健性分析应以三轨并列呈现而非以 ss 轨单独替代 full 轨结论。

<!-- rendered-citations:begin -->
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML) No. 625-632 [Working Paper]. https://doi.org/10.1145/1102351.1102430
Manski, C. F., & Lerman, S. R. (1977). The estimation of choice probabilities from choice based samples. Econometrica, 45(8), 1977-1988. https://doi.org/10.2307/1914121
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis - Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance - Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
