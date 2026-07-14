---
family_id: F536
columns:
- sum_wd_mw_deepseekv4_ctx
- sum_wd_mw_deepseekv4_full
- sum_wd_mw_deepseekv4_ss
unit: 无量纲权重和 (媒体权威权重 media_authority_weight 之和, 与银行-年内"文章数"同量纲但按媒体权威度加权)
formula: 'sum_wd_mw_deepseekv4{track} = Σ_i media_authority_weight_i, i 取遍该 银行×年 单元内 deepseekv4_score{track} 非缺失 (即 DeepSeekV4 在该轨对该篇给出有效情感判断) 的文章; media_authority_weight 由 compute_media_authority_weights 依据来源媒体在 config/media_weights.json 的权威度取值 (未登录来源退到 default 权重), fillna(1.0) 兜底后逐篇赋值; track ∈ {full, ctx, ss}'
producer: pipeline/panel/runner.py::_build_llm_valid_masked_weights (逐篇构造 _wd_mw_deepseekv4{track} 掩码列, wtag=mw) → pipeline/panel/encode.py::build_aggregation_dict (agg[f"sum_wd_mw_{grp}{track}"] = (f"_wd_mw_{grp}{track}", "sum"), grp=deepseekv4) 在 groupby(target_bank, year) 聚合层求和
upstream:
- 21_tone_llms.parquet (deepseekv4_score_full/_ctx/_ss 逐篇 DeepSeekV4 情感判分, 缺失=该模型对该篇未给出有效判断)
- runner.py 步骤3c compute_media_authority_weights 产出的 media_authority_weight (来源媒体权威度, config/media_weights.json)
- 14_materialize_ctx (content_ctx/content_ss 三轨物化, 决定 ctx/ss 轨是否存在候选行)
citations:
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
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: 'Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy'
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: 'Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
new_dois: []
---

## CORE

【构念与来源】
sum_wd_mw_deepseekv4 是三家 LLM 情感投票体系里, 单独归给 DeepSeekV4 一家模型的"媒体权威加权"有效样本量分母, 而不是一个独立的情感分数本身。它的构念角色是"配套分母", 服务于媒体权威加权语调 (media-authority weighted tone, 记号 MW) 的正确计算: 银行-年层面的 MW 加权语调 = Σ(该篇 media_authority_weight × 该篇 deepseekv4_score) / Σ(该篇 media_authority_weight, 限于 DeepSeekV4 给出有效判断的那批文章)。sum_wd_mw_deepseekv4 就是这个式子的分母。媒体权威权重来自 config/media_weights.json 里对具体媒体来源 (如权威财经媒体 vs 地方小站) 的权威度打分, 体现"同一条负面消息, 出自权威媒体的市场冲击力通常大于出自边缘媒体"这一新闻传播学常识 — 加权语调因此比简单等权均值更贴近市场实际感知到的舆论压力。DeepSeekV4 (deepseek-v4-flash, 经 api.deepseek.com 直连) 是本项目三家情感 LLM 之一 (另两家为 gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31, 均经 yunwu 中转), 三家各自独立对每篇文章判断情感极性, 经多数投票形成共识 llm_vote_tone 作为 P1 主处理变量; 与此同时, 三家各自的逐模型情感分数 (deepseekv4_score 等) 被并排保留为"互为稳健性、不分主次"的跨厂商测度轨, 用以证明主结论不是被单一模型的判断偏差驱动。
【方法学与计算】
本列的数值构造分两步。第一步在文章级由 runner.py 的 `_build_llm_valid_masked_weights` 完成: 对每一篇文章, 若 DeepSeekV4 在给定轨道 (full/ctx/ss) 上给出了非缺失的 deepseekv4_score, 该篇的 media_authority_weight 原值被保留 (掩码通过); 若 DeepSeekV4 未能给出有效判断 (如该篇内容被判定超出银行-金科议题范围、或该轨对应的银行∧金科共现条件不满足导致文本退化), 该篇在这一轨上的权重被置为缺失值而非 0。这一"掩码而非清零"的设计是本列存在的核心动因: 若直接用全体文章 (含 DeepSeekV4 未判断的) 的媒体权重之和做分母, 分子却只累加 DeepSeekV4 实际判断过的那批文章的加权得分, 会系统性把"未判断"的文章隐含记为语调 0, 使加权语调随 DeepSeekV4 无效判断占比的上升而机械地向零衰减 — 这是本项目 2026 年 6 月 encode-01 度量审计发现并修复的口径缺陷, 修复方案就是让分子分母共用同一个"有效样本"口径, sum_wd_mw_deepseekv4 即修复后配套的正确分母。第二步在面板级由 encode.py 的聚合字典完成: 按 (target_bank, year) 分组对第一步产出的掩码列求和, pandas groupby().sum() 对缺失值 (未通过掩码的文章) 自动跳过而非计为 0, 因此该列的值精确等于"该银行-年单元内 DeepSeekV4 给出有效情感判断的文章"的媒体权威权重之和, 而非该单元全部文章的权重之和。当分母为 0 (该单元内 DeepSeekV4 无一篇给出有效判断) 时, 下游 deepseekv4_tone_mw{track} = 分子/分母 会产生缺失而非除零异常, 这是聚合层刻意保留的优雅降级行为。
【文献定位】
以媒体权威度/来源可信度对新闻文本情感度量加权, 呼应了金融文本情感分析文献里"信号来源异质性影响信号强度"的一贯关切: Todd, Bowden & Moshfeghi (2024) 在对金融文本情感分析文献的系统综述中指出, 情感测度的稳健性很大程度上取决于对文本来源、方法论选择 (词典法 vs 机器学习法 vs 大模型法) 的透明披露与交叉验证, 而不能孤立地报告单一来源、单一模型的分数。van Atteveldt, van der Velden & Boukes (2021) 通过系统比较人工标注、众包标注、词典法与机器学习算法, 证明不同测量路径之间的"有效性一致性"本身需要被实证检验而非默认成立, 这正是本项目坚持三家 LLM 并排 (而非只用单一模型) 的方法论出发点。在生成式大模型作为文本标注/情感判别工具的近期文献里, Gilardi, Alizadeh & Kubli (2023, PNAS) 证明大模型在文本标注任务上可以系统性优于众包工作者的准确率与一致性, 为把 DeepSeekV4 这类大模型直接用作情感判别引擎提供了实证支撑; Schoenegger 等 (2024, Science Advances) 进一步表明多个大模型的集成判断 (wisdom of the silicon crowd) 在预测类任务上可比肩甚至超越人类群体智慧的准确度, 这与本项目"三家 LLM 多数投票为主轨、逐模型分数为稳健性轨"的整体设计思路相互印证: 单一模型 (如本列聚焦的 DeepSeekV4) 的判断质量足以支撑独立测度, 但结论的稳健性最终要靠跨模型比对来确认, 而 sum_wd_mw_deepseekv4 正是支撑这种逐模型独立测度得以正确加权计算的技术基石。

## VAR: sum_wd_mw_deepseekv4_ctx

【变体差分】
本列对应 ctx (实体窗) 轨: 分子分母所计的"有效判断"以 deepseekv4_score_ctx 是否非缺失为准, 该分数来自 stage 21 对 content_ctx (标题 + 目标银行实体窗口文本, 由 stage 14 materialize_ctx 物化) 的 DeepSeekV4 判断。ctx 轨与 full 轨、ss 轨在构念上互为稳健性并排, 三者各自 just-identified, 不分主次, 严禁混入同一个 over-identified 的 Hansen J 检验框架; 三轨差异只反映"喂给模型看的文本范围"不同 (全文 vs 实体窗口 vs 银行∧金科同句窗), 不代表优先级高低。ctx 轨自身不设独立回退语义 (回退语义属于 ss 轨, 见下), 但当上游 content_ctx 因 stage 14 未跑或 DeepSeekV4 对该轨全部判断缺失时, 本列 (乃至整族 ctx 相关列) 由 encode.py 的 valid_agg 机制自动整体跳过而不报错, 是一种"缺源列优雅降级"而非"数值退化"的行为。留篇门控口径为 full-only (2026-06-29 起): 一篇文章是否计入"银行-金科报道"总体, 只看 llm_vote_score_full (即三家投票在 full 轨) 是否有效, 与本列所属的 ctx 轨、deepseekv4 单模型无关; ctx 轨的样本行宇宙是 full 留篇集合的子集, 本列的分母因此天然不会超过对应银行-年单元内 full 轨的有效文章媒体权重和。使用者若要计算 deepseekv4 单模型在 ctx 轨的媒体权威加权语调 deepseekv4_tone_mw_ctx, 分子应取 deepseekv4_score_mw_sum_ctx (逐篇 deepseekv4_score_ctx × media_authority_weight 的加权和), 分母正是本列; 二者共享同一批"DeepSeekV4 在 ctx 轨给出有效判断"的文章子集, 是修复 encode-01 分子分母口径不一致缺陷后的正确匹配对。切勿将本列与 full 轨或 ss 轨的同名分母混用, 也不可将其误当作该银行-年单元的文章总数 (n_articles) 使用 — 后者是等权计数, 本列是按媒体权威度加权后的和, 二者在媒体权重分布不均时数值差异可观。

## VAR: sum_wd_mw_deepseekv4_full

【变体差分】
本列对应 full (全文) 轨, 是三轨中的 canonical / 门控轨: deepseekv4_score_full 由 DeepSeekV4 对 content_full (标题 + 全文正文) 做出的判断, 是否有效由 stage 21 判定, 与 llm_vote_score_full (三家投票的门控依据) 共享同一批"是否为一篇有效银行-金科报道"的裁定逻辑, 但本列本身聚合的是 DeepSeekV4 单模型的有效性掩码而非三家共识的有效性掩码 — 两者理论上高度重合但不完全相同, 因为 DeepSeekV4 单家判断失败 (如返回格式异常、超时) 而另两家判断成功的边缘情形依然可能出现, 此时该篇仍属于留篇集合 (由三家投票门控决定), 但不计入本列的求和范围。full 轨在本项目里承担"处理变量主轨"的角色 (P1 llm_vote_tone_full 是主处理变量), 因此本列作为 full 轨 MW 加权分母, 在 deepseekv4_tone_mw_full 这一逐模型稳健性测度里权重最大、样本量通常也最充分, 三轨互为稳健性并排的铁律同样适用于本列, 不因其为 canonical 轨而享有更高的统计优先级。由于留篇门控本身就以 full 轨的三家共识为准 (llm_vote_score_full 非缺失即计入留篇集合), 本列的分母在实践中最接近该银行-年单元"全部留篇文章"的媒体权威权重和, 只有当 DeepSeekV4 单家判断失败而另两家判断成功的边缘情形出现时, 本列才会略小于按留篇集合直接求和的媒体权重总量, 这一差额的规模是判断 DeepSeekV4 单模型解析成功率的一个有用旁证。分析者若需比较三家模型各自的 MW 加权分母是否系统性偏小 (提示某模型解析失败率偏高), 应把 sum_wd_mw_deepseekv4_full 与 sum_wd_mw_gpt54nano_full、sum_wd_mw_gemini31_full 并排对照, 而不是与本家族内的 ctx/ss 轨对照 — 后者比较的是文本范围差异, 前者比较的才是模型解析质量差异, 两种比较不可混为一谈。

## VAR: sum_wd_mw_deepseekv4_ss

【变体差分】
本列对应 ss (同句共现) 轨: deepseekv4_score_ss 来自 DeepSeekV4 对 content_ss (标题 + 银行∧金科同句 ±N 窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 的判断。ss 轨镜像 ctx 轨的回退语义: 当某篇文章不存在银行与金科词在同一句 (或窗口内) 共现的情形时, content_ss 退化为使用全文 body 作为替代文本, 并将 ss_is_fallback 标记为 True, 此时该篇是否被 DeepSeekV4 判定为"有效判断"仍取决于 deepseekv4_score_ss 是否非缺失, 与其是否处于回退状态无直接必然联系, 二者共享同一个 n_articles 分母口径。ss 轨的判定不对称口径与 ctx 轨一致: 银行侧采用否定词/短名过滤, 金科侧采用裸 Aho-Corasick 1506 词表匹配, 这一构造判据发生在文本物化阶段 (stage 14), 与本列所处的 panel 聚合阶段 (求媒体权威权重和) 相互独立、不受影响。同三轨铁律, ss 轨与 full、ctx 轨互为稳健性并排, 各自 just-identified, 禁止混入同一 over-identified Hansen J 框架; 在样本稀薄的开发期 (T=2) 上, ss 轨常因同句共现条件苛刻而样本量明显小于 full/ctx 轨, 属预期的窗口收窄效应, 不代表数据缺陷。使用者计算 deepseekv4_tone_mw_ss 时, 分子 deepseekv4_score_mw_sum_ss 与本列分母同样只统计 DeepSeekV4 在 ss 轨给出有效判断的那批文章, 若某银行-年单元恰好没有任何文章满足银行∧金科同句共现条件 (即该单元全部文章的 ss_is_fallback 均为 True 且未产生有效 deepseekv4_score_ss), 本列会呈现缺失而非 0, 下游加权语调计算须显式处理这一缺失而非当作零权重参与合计, 否则会人为压低该单元的 ss 轨稳健性证据强度。

<!-- rendered-citations:begin -->
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd: LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
