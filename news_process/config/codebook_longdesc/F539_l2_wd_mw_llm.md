---
family_id: F539
columns:
- sum_wd_mw_llm_ctx
- sum_wd_mw_llm_full
- sum_wd_mw_llm_ss
unit: 无量纲权重之和 (银行-年层面, media_authority_weight 在"三家 LLM 共识打分有效"子集上逐篇求和)
formula: 'sum_wd_mw_llm{track} = sum(_wd_mw_llm{track}), 其中 _wd_mw_llm{track} 是文章级 valid-mask 权重列, 仅当 llm_vote_score{track} 非缺失 (三家 LLM 多数投票共识成功打分) 时取值 media_authority_weight, 否则置为 NaN (pandas .where 无 other 参数时的默认填充, 非 0), sum 聚合时自动跳过 NaN 行, 效果上等价于该行不参与分母求和; 源自 pipeline/panel/runner.py::_build_llm_valid_masked_weights(df, mw, "mw") 对 grp="llm" 的产出, 聚合见 pipeline/panel/encode.py: for track in [_full,_ctx,_ss]: for wtag in (vw,mw,hw): for grp in [llm, *LLM_MODELS, prob]: agg[f"sum_wd_{wtag}_{grp}{track}"]=(f"_wd_{wtag}_{grp}{track}","sum")'
producer: pipeline\panel\runner.py::_build_llm_valid_masked_weights ; pipeline\panel\encode.py ; pipeline\audit\stata_audit.py
upstream:
- "21_tone_llms.parquet (llm_vote_score{track}: 三家 LLM 多数投票共识得分, gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash; 其缺失/有效状态决定本列掩码)"
- media_authority_weight (文章级媒体权威权重, 来源报社/来源等级映射, Holzman et al. 2023 TAR 加权设计)
- 14_materialize_ctx.parquet (content_ctx/content_ss 三轨文本物化)
citations:
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, Fabrizio; Alizadeh, Meysam; Kubli, Maël"
  year: 2023
  title: "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
- doi: "10.17016/FEDS.2026.020"
  type: wp
  authors: "Hansen, A. L."
  year: 2026
  title: "Validating Large Language Model Annotations"
  venue: "FEDS Working Paper, Federal Reserve Board"
  vol: "2026-020"
- doi: "10.1007/s00521-024-10603-6"
  type: journal
  authors: "Lan, Y.; Wu, Y.; Xu, W.; Feng, W.; Zhang, Y."
  year: 2025
  title: "Chinese Fine-Grained Financial Sentiment Analysis with Large Language Models"
  venue: "Neural Computing and Applications"
  vol: "37"
  issue: "30"
  pages_or_artno: "24883-24892"
- doi: "10.3982/te6424"
  type: "journal"
  authors: "Eliaz, K., & Spiegler, R."
  year: 2026
  title: "News media as suppliers of narratives (and information)"
  venue: "Theoretical Economics"
  vol: "21"
  issue: "3"
  pages_or_artno: "928-972"
- doi: "10.1371/journal.pone.0323064"
  type: "journal"
  authors: "Wright, D., & Augenstein, I."
  year: 2025
  title: "Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift"
  venue: "PLOS One"
  vol: "20"
  issue: "6"
  pages_or_artno: "e0323064"
- doi: "10.2139/ssrn.5395056"
  type: "wp"
  authors: "Liu, Y., Liu, J., & Wang, T."
  year: 2025
  title: "Large Language Model Disagreement"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "5395056"
- doi: "10.48550/arxiv.2510.01499"
  type: "arxiv"
  authors: "Ai, R., Pan, Y., Simchi-Levi, D., Tambe, M., & Xu, H."
  year: 2025
  title: "Beyond Majority Voting: LLM Aggregation by Leveraging Higher-Order Information"
  venue: "arXiv"
- doi: "10.1016/j.finmar.2024.100896"
  type: "journal"
  authors: "Ashwin, J."
  year: 2024
  title: "Financial news media and volatility: Is there more to newspapers than news?"
  venue: "Journal of Financial Markets"
  vol: "69"
  pages_or_artno: "100896"
- doi: "10.2139/ssrn.4842086"
  type: "wp"
  authors: "Battaglia, L., Christensen, T., Hansen, S., & Sacher, S."
  year: 2024
  title: "Inference for Regression with Variables Generated from Unstructured Data"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "4842086"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (sum_wd_mw_llm_full/_ctx/_ss) 是「银行-年」层面上、供三家大语言模型多数投票语调共识测度构造媒体权威加权 (media-authority-weighted, MW) 平均值所需的 valid-mask 分母部件, 三轨 (full/ctx/ss) 各自并排、互为稳健性。它本身不是可直接解读的语调水平, 而是一个纯计数/权重和性质的辅助列, 精确含义是: 在某银行某年被留篇为"一篇有效银行金科报道"的全部文章中, 只统计三家 LLM (OpenAI 系 gpt-5.4-nano、Google 系 gemini-3.1-flash-lite、DeepSeek 系 deepseek-v4-flash) 多数投票共识得分 llm_vote_score{track} 成功打分 (非缺失) 的那些文章, 把它们各自的媒体权威权重 media_authority_weight 逐篇加总。这与"物理域"分母 sum_media_authority_weight{track} (对该银行-年全部相关文章不分是否成功打分一律求和媒体权重) 是两个不同的量: 前者的求和范围严格限定在"LLM 打分有效"这一子集, 后者不做此限定。

该列的存在源自一次生产端的度量修正 (encode-01, metric-audit 2026-06-10): 加权平均语调的标准构造是 W_tone = Σ(weight_j × tone_j) / Σ(weight_j), 但 LLM 族的 tone_j (即 llm_vote_score{track}) 是 nullable 类型, 对打分失败/未留篇的文章记为缺失, 因此分子 Σ(weight_j × tone_j) 在求和时天然跳过缺失行 (pandas sum 对 NaN/NA 的默认行为), 等价于只在"打分有效"子集上求和; 但若分母仍沿用物理域 Σ(weight_j) (对全部文章不加区分地求权重和), 就会出现分子分母定义域不一致——物理分母系统性偏大 (含了打分失败文章的权重), 使最终算出的加权平均语调随"LLM 打分失败占比"的增大而系统性向 0 收缩, 这是一个测度层面的偏误而非真实的语调衰减。修正办法是为 LLM 族单独建一套 valid-mask 权重列, 只在"该篇 llm_vote_score{track} 非缺失"的行上取实值权重、其余行置为 NaN (pandas .where 缺省填充, sum 时自动跳过), 再对这套 valid-mask 权重逐银行-年求和 (NaN 行不参与求和, 效果上等价于 0 贡献但字面赋值并非 0), 得到与分子同域的匹配分母——这正是本家族三列的构造逻辑。用大白话说: 假设某银行某年有 10 篇报道, 但其中 2 篇因文本过短/接口异常等原因未能被三家 LLM 联合判出共识分数, 那么算"媒体权威加权平均语调"时, 分子只对剩下 8 篇算加权和, 分母也必须只数这 8 篇的媒体权重加总, 而不能把那 2 篇打分失败文章的媒体权重也算进分母——否则相当于把"没打出分"的文章当成"打出 0 分"来稀释平均值, 是系统性向零压低。

值得强调的是, 这一 valid-mask 修正只施于 LLM 族 (grp ∈ {llm, gpt54nano, gemini31, deepseekv4, prob}), 不施于词典族 (dict) 与 BERT 族。原因 (reaudit-2026-07-12 WP-A5 前提更正) 是: 词典族的分数在结构上不存在缺失——stage 13 共现硬过滤 + stage 14 prepend_title 拼接保证每一篇存活到面板聚合阶段的文章都必然含有可计词的真实文本 token, "空文本"分支在生产管线中不可达, 因此词典族的分子分母天然同域, 无需建 valid-mask; BERT 族则自 omni-g-berts-02 (2026-06-11) 起存在推理失败哨兵 (概率记为 NaN), 理论上也存在与 LLM 族同构的分子分母失配问题, 但其掩码根治被判定为"改测度"性质的变更, 需延后到 M0/golden 重生窗口统一处理 (FATAL_REAUDIT_CLOSEOUT 执行计划 §3 WP-B1), 现行防线是 runner.py 输入处的 infer_failed 观测闸——一旦生产语料上出现失败率大于 0 的推理批次, 会 fail-loud 记 ERROR 日志而非静默放行, 提醒核查 stage 23 日志定位失败篇, 但不会自动修正该批次的加权分母。

【方法学与计算】
计算分两段。第一段 (runner.py::_build_llm_valid_masked_weights): 输入是该篇的 media_authority_weight (来自 compute_media_authority_weights 依据发文媒体来源等级映射产出的文章级权重) 与该轨道的 llm_vote_score{track} 是否非缺失; 函数按行判定"该篇在该轨道上 LLM 打分是否有效" (源码为 wt.where(frame[f'llm_vote_score{track}'].notna())), 有效则赋值为该篇的媒体权威权重, 无效则置为 NaN (pandas .where 无 other 参数的默认填充, 而非字面赋 0; 后续 groupby.sum 对 NaN 默认跳过, 效果上等价于该行不参与分母求和); 输出列名为 _wd_mw_llm{track} (前缀 "_wd_" = weighted-denominator 的内部命名约定, "mw" = media-authority-weighted 权重口径, "llm" = 三家共识投票族)。该函数在 mw、vw (mention-density 加权)、hw (跟风衰减加权) 三套权重口径下均被复用 (仅传入的 weight 与 wtag 不同), 三套权重口径与三轨文本各自独立构造出各自的一套 valid-mask 分母列。

第二段 (encode.py 面板聚合级): 按银行-年分组, 对 _wd_mw_llm{track} 求 sum, 即为本家族三列 sum_wd_mw_llm{track}, track ∈ {_full, _ctx, _ss}, 与同一循环内针对 gpt54nano/gemini31/deepseekv4 各自的 sum_wd_mw_{短名}{track} (对应家族 F536/F537/F538)、以及针对 Logit-to-Score 概率映射情感的 sum_wd_mw_prob{track} (对应家族 F540) 一并批量产出, 均在 "for track in [_full,_ctx,_ss]: for wtag in (vw,mw,hw): for grp in [llm, *LLM_MODELS, prob]: agg[f'sum_wd_{wtag}_{grp}{track}']=(f'_wd_{wtag}_{grp}{track}','sum')" 这一逻辑块内一次性对齐产出, grp="llm" 即三家投票共识族、区别于逐模型的 per-model 族 (grp ∈ LLM_MODELS)。

本家族三列在下游消费于 encode.py 的 _llm_denom 辅助函数: 对 track 逐一构造 llm_vote_tone_mw{track} = llm_vote_score_mw_sum{track} / _llm_denom("mw","llm",track,mw_denom), 其中 _llm_denom 的取列逻辑是"若 sum_wd_mw_llm{track} 存在于面板列中, 优先取用该列 (并将其中的 0 值替换为 NaN 以避免除零); 若该列不存在 (如面板重生时未跑对应聚合块), 才回退到物理分母 sum_media_authority_weight{track}"。这一"优先取 valid-mask、缺则回退物理域"的防御式设计, 保证即使某次面板重生偶然跳过了该聚合块, 加权语调的计算也不会因 KeyError 崩溃, 而是自动退化为向后兼容的物理域口径 (代价是重新引入前述向零衰减偏误, 因此该防御分支只是兜底而非推荐路径)。stata_audit.py 对 llm_vote_tone_mw{track} 的加权恒等式做三轨全覆盖的 PASS/WARN 稽核记录, 分母缺失时记 WARN 而非静默跳过, 防止面板重生悄悄丢失这一稽核项。

留篇门控口径 (2026-06-29 起生效): 一篇报道是否计入"银行金科报道"的判定只看 llm_verified_full == True (full-only 门控), 本家族三列的求和范围首先受此约束——只有落在 full 轨留篇集合内的文章才有资格参与任一轨道的 valid-mask 分母求和; 在此基础上, ctx/ss 轨的 _wd_mw_llm{track} 掩码进一步取决于该篇在 ctx/ss 轨各自的 llm_vote_score{track} 是否非缺失 (即该轨道文本上三家 LLM 是否成功打出共识分数), 因此三轨分母列的加总值一般不完全相等, 差异来自各轨道各自的打分有效率。

【文献定位】
本家族的方法学定位交汇于三条脉络。其一是生成式大语言模型在会计与金融文本分析中的规范化应用: de Kok (2025, Management Science) 系统论述了在会计研究中使用生成式 LLM 做文本分析时应遵循的工程规范 (含 prompt 版本控制、temperature 设定为 0 以保证确定性、结果缓存以支持可复现), 本项目 stage 21 的确定性锚点设计 (prompt v8 字节级冻结、temperature=0.0、缓存命中可离线 $0 复现) 正是对该规范的直接工程落地, 而本家族的 valid-mask 机制进一步保证了"部分文章打分失败"这一现实情形不会破坏下游加权测度的统计性质。其二是 LLM 标注质量与人工标注的比较研究: Gilardi et al. (2023, Proceedings of the National Academy of Sciences) 的发现——ChatGPT 类模型在文本标注任务上的准确率可超越众包人工标注者——为以三家 LLM 多数投票替代传统人工/词典标注提供了方法学正当性基础; 本项目采取跨厂商 (OpenAI/Google/DeepSeek) 三家独立模型多数投票而非单模型标注, 呼应该文献所倡导的"LLM 标注可靠但仍需质量保障机制"的核心关切。其三是无金标准场景下 LLM 标注的验证方法学: Hansen (2026, FEDS Working Paper) 专门探讨了在缺乏人工金标准的情形下如何验证大语言模型标注结果的一致性与有效性, 与本项目在 tone_validation.py 中复用 Krippendorff's alpha 与 Cohen's kappa 度量三家模型间一致性的做法在方法论关切上高度契合——本家族的 valid-mask 机制正是这条"标注质量可能存在缺口, 须显式处理而非掩盖"思路在面板聚合层面的落地。此外, Lan et al. (2025, Neural Computing and Applications) 关于中文细粒度金融情感分析的大语言模型应用研究, 为本项目在中文财经新闻语料上使用 LLM 判定银行-金科语调这一具体应用场景提供了同语种、同领域的方法学参照。

三轨口径铁律: full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验方程。ss 轨回退语义镜像 ctx 轨——当某篇文章不存在银行∧金科词同句共现时, content_ss 回退为全文 body, ss_is_fallback 标记为 True, 此类回退行若其 llm_vote_score_ss 仍成功打分, 依旧计入本列求和 (回退不等于剔除, 亦不等于自动失效)。n_articles 与留篇门控严格遵循 full-only 口径 (2026-06-29 起生效): 一篇文章是否被计为该银行-年的一篇有效银行金科报道, 只由 llm_verified_full 决定, ctx/ss 轨的 valid-mask 分母列是在该 full-only 留篇行集合的子集上、按各自轨道打分有效性条件求和的稳健性测度, 不构成独立的行宇宙判定。此外须与 MW/VW/HW 三套加权口径的并排关系区分开: mw (媒体权威加权)、vw (提及密度加权)、hw (跟风衰减加权) 各自服务不同的"报道重要性"构念, 各自建有独立的 valid-mask 分母列族 (sum_wd_vw_llm{track}/sum_wd_mw_llm{track}/sum_wd_hw_llm{track}), 三套权重口径同样各自 just-identified 并排、不设主次, 不应混同或相互替代。 在上述三条脉络之外, 晚近文献从媒体加权、聚合口径与生成变量推断三个方向补充了本族的前沿定位。Eliaz 与 Spiegler (2026) 以理论建模把新闻媒体刻画为叙事而不仅是信息的供给者, 分析不同媒体供给的叙事如何影响受众信念, 为 mw 轨"不同来源媒体的报道不等价、须按来源加权"提供理论侧的存在性论证; 该文是纯理论均衡分析, 其媒体差异化维度是叙事内容而非权威度, 不提供可迁移的权重赋值方案, 与 media_authority_weight 的具体取值口径无对应。Wright 与 Augenstein (2025) 基准比较了把多标注者软标签 (概率) 聚合为目标的若干方案, 发现软标签聚合在分布偏移下比硬标签多数投票给出更好的不确定性估计, 恰对应 prob 分组 (软概率映射) 与本族 llm 分组 (三家硬多数投票共识) 这两条并排轨; 迁移边界是原文标注者为人类众包工人、目标为分类器不确定性校准, 语料为英文 NLP 基准集, 既无银行-年聚合层, 亦无媒体权威/提及密度/跟风衰减的权重维度。Liu、Liu 与 Wang (2025) 以金融文本为对象度量不同大语言模型判断的分歧程度, 印证各家 per-model 的 mw 分母姊妹族之所以彼此不同, 完全来自各家有效打分覆盖面与判断差异, 而本族的共识掩码正是该分歧的折叠结果; 该文为 SSRN 工作论文, 尚未经期刊同行评审, 且原文把分歧本身当作信号/噪声变量, 本项目不作此用, 仅以有效性掩码界定分母。Ai、Pan、Simchi-Levi、Tambe 与 Xu (2025) 在 arXiv 预印本 (未经同行评审) 中指出朴素多数投票忽略了各模型的期望准确率与模型间答案相关性, 并设计利用此类高阶信息的聚合规则, 其对本族的意义仅在于锚定"多模型投票共识作为一种聚合口径"的前沿存在性, 并提示朴素多数票并非唯一选择; 须明确该文不构成对本项目投票口径的背书——本族生产口径刻意保留朴素多数投票, 未采用原文的高阶聚合器, 且原文任务为英文 QA/推理基准, 无权重加权分母与面板聚合。Ashwin (2024) 把报纸报道的数量/篇幅维度与报道所含的新信息内容分离, 检验前者对波动率是否具有独立于后者的解释力, 这正锚定本族把"按来源权威度加权的报道量分母"与语调分子相分离之必要性; 迁移边界是原文语境为英文报纸与股票波动率, 其报道量为等权计数或版面维度而非媒体权威度加权, 且波动率是结果变量, 本列则是分母。Battaglia、Christensen、Hansen 与 Sacher (2024) 建立了先用非结构化文本生成变量、再把该变量代入回归这一两步流程的推断理论, 证明朴素代入会产生偏误并给出偏误修正与有效标准误, 提示本族分母所服务的 llm_vote_tone_mw 一类生成型测度在进入回归时须正视这层推断代价; 惟须诚实指出层级差异: 原文处理的是回归中的生成型变量本身, 本列则是界定该变量求和域的有效性掩码分母, 原文未处理多模型投票共识, 亦无中文语料、银行-年面板与三轨设定。
## VAR: sum_wd_mw_llm_ctx

【变体差分】
本列是 ctx 轨 (标题+目标银行实体窗口正文, stage 14 prepend_title 拼接 content_ctx) 的 valid-mask 媒体权威权重和: 只对该银行-年全部落在 full 轨留篇集合内、且在 ctx 轨文本上三家 LLM 多数投票共识得分 llm_vote_score_ctx 成功打出 (非缺失) 的文章, 把它们的 media_authority_weight 逐篇求和。区别于 full 轨的关键在于"打分有效"这一判定条件本身是逐轨独立评估的——即便某篇文章在 full 轨上打分成功 (从而被纳入留篇集合), 在 ctx 轨窄化文本 (只保留银行实体窗口而非全文) 后仍有可能因信息量不足、实体窗口提取失败等原因导致 llm_vote_score_ctx 本身缺失, 此时该篇不计入本列求和, 即便它计入了 full 轨对应列 sum_wd_mw_llm_full 的求和。因此三轨该家族列的加总值一般不完全相等, 差值反映各轨道各自的 LLM 打分有效率差异, 而非样本范围差异 (行宇宙仍严格共享 full 轨留篇门控)。本列作为 llm_vote_tone_mw_ctx 的匹配分母部件, 与 ctx 轨的其余稳健性测度 (subst/locus/collab 各 per-model 族的 ctx 轨版本) 处于同一"文本范围收窄以聚焦目标实体"的设计脉络下, 与 full、ss 两轨互为稳健性并排, 不视为更精确或更保守的替代版本。

用大白话理解本列的作用: 它是一个"记账簿"式的辅助列, 不直接进回归方程, 而是给 ctx 轨的媒体权威加权平均语调打分做分母校准——如果某银行某年有若干篇文章在 ctx 轨窗口下未能提取出稳定的银行实体上下文 (例如银行名多次出现但均在无实质关联的段落中), 这些文章的 llm_vote_score_ctx 会缺失, 本列会自动把它们的媒体权重从分母中剔除, 避免用"分母包含无效打分权重、分子却跳过这些行"这种失配算式压低最终的加权平均语调数值。ctx 轨的这一有效率通常与该轨道文本裁剪的严格程度正相关: 裁剪越窄, 信息缺失导致打分失败的概率相应上升, 但这属于三轨设计的内生特征而非缺陷, 稳健性检验的意义正在于观察结论是否在信息量不同的三种文本裁剪口径下保持一致方向。

## VAR: sum_wd_mw_llm_full

【变体差分】
本列是 full 轨 (标题+完整正文, stage 14 prepend_title 拼接 content_full) 的 valid-mask 媒体权威权重和, 是本家族的门控主轨: 一篇文章是否被认定为"一篇有效的银行金科报道"并纳入面板求和的候选范围, 唯一由该篇在 full 轨上的 LLM 验证结果 llm_verified_full 决定 (2026-06-29 起 full-only 留篇门控铁律)。在此候选范围内, 本列进一步只统计 llm_vote_score_full 非缺失的文章的媒体权威权重, 与同一 for 循环内的 llm_vote_score_w_sum_full (mention-density 加权分子和, 家族另计)、llm_vote_score_mw_sum_full (媒体权威加权分子和, 家族 F396) 共同服务于 encode.py 的加权平均语调恒等式构造。在下游 P1 主线论文 (bank_fintech_tone) 的处理变量设计中, full 轨语调 llm_vote_tone_full 是 P1 主处理变量 (treatment.primary), 而 llm_vote_tone_mw_full 作为其媒体权威加权稳健性版本, 依赖本列作分母, 使该加权平均语调不因文章间"LLM 打分有效率差异"而系统性失真。ctx/ss 两轨的对应分母列均以本列所刻画的 full 轨留篇集合为行宇宙上界, 是在该集合子集上的派生条件测度。

由于 full 轨是留篇门控的唯一判据, 理论上本列的求和范围应最接近该银行-年全部候选文章的媒体权重总量——只有极少数文章会出现"通过 full 轨留篇验证 (llm_verified_full == True) 但 llm_vote_score_full 本身仍缺失"的边界情形 (例如三家 LLM 返回结果解析异常导致投票折算失败), 因此 sum_wd_mw_llm_full 与物理分母 sum_media_authority_weight_full 的数值差距通常是三轨中最小的一个, 相应地本列作分母时引入的"向零衰减"修正幅度也最小, 但修正逻辑与 ctx/ss 两轨完全一致, 并非可省略的边际调整——生产端设计上不因某一轨道的失配幅度小而弱化该轨道的口径一致性要求。

## VAR: sum_wd_mw_llm_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句共现窗口, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句) 的 valid-mask 媒体权威权重和: 只对落在 full 轨留篇集合内、且在 ss 轨文本上三家 LLM 多数投票共识得分 llm_vote_score_ss 成功打出的文章, 把它们的 media_authority_weight 逐篇求和。ss 轨是三轨中文本范围最窄的一支, 只截取银行实体与金科词汇同句 (或窗口内邻近句) 共现的片段, 判定不对称口径为银行侧走否定+短名过滤、金科侧走裸 AC 自动机匹配 (1506 词表); 当某篇文章不存在银行∧金科词同句共现时, content_ss 按既定规则回退为全文 body, ss_is_fallback 标记为 True, 该回退行若其 llm_vote_score_ss 仍成功打分, 依旧计入本列求和 (与 ctx 轨回退语义严格对称)。由于 ss 轨文本窗口更窄, 部分文章可能因窗口内信息不足而导致 LLM 打分失败率高于 full/ctx 两轨, 使本列在同一银行-年上的取值通常小于或等于 full/ctx 对应列, 但这纯粹是文本范围与打分有效率差异的自然结果, 不代表 ss 轨测度质量的优劣。本列与 full、ctx 两轨的对应分母列构成互为稳健性、各自 just-identified 并排的三支, 严禁混入同一 over-identified 的 Hansen J 过度识别检验。

从数值规模上看, 三轨该家族列的相对大小关系一般遵循 sum_wd_mw_llm_full ≥ sum_wd_mw_llm_ctx ≥ sum_wd_mw_llm_ss 或与之相近的次序 (并非严格数学不等式, 因三轨打分有效率各自独立波动), 原因是文本裁剪范围逐轨收窄导致 LLM 可用信息量递减、打分失败概率递增。研究者在解读 ss 轨媒体权威加权语调 llm_vote_tone_mw_ss 时, 应意识到其分母 (本列) 天然偏小, 单独看分母绝对值无实证意义, 唯有分子分母同轨相除得到的加权平均语调才具备跨银行-年可比性; 而本列作为纯粹的权重和辅助列, 其存在价值仅在于保证该除法运算在"打分有效"这一正确定义域上进行, 不引入词典族、BERT 族所不需要的向零衰减偏误。
<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Gilardi, Fabrizio; Alizadeh, Meysam; Kubli, Maël. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Hansen, A. L. (2026). Validating Large Language Model Annotations. FEDS Working Paper, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Lan, Y.; Wu, Y.; Xu, W.; Feng, W.; Zhang, Y. (2025). Chinese Fine-Grained Financial Sentiment Analysis with Large Language Models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Eliaz, K., & Spiegler, R. (2026). News media as suppliers of narratives (and information). Theoretical Economics, 21(3), 928-972. https://doi.org/10.3982/te6424
Wright, D., & Augenstein, I. (2025). Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift. PLOS One, 20(6), e0323064. https://doi.org/10.1371/journal.pone.0323064
Liu, Y., Liu, J., & Wang, T. (2025). Large Language Model Disagreement. SSRN Electronic Journal No. 5395056 [Working Paper]. https://doi.org/10.2139/ssrn.5395056
Ai, R., Pan, Y., Simchi-Levi, D., Tambe, M., & Xu, H. (2025). Beyond Majority Voting: LLM Aggregation by Leveraging Higher-Order Information. arXiv [Preprint]. https://doi.org/10.48550/arxiv.2510.01499
Ashwin, J. (2024). Financial news media and volatility: Is there more to newspapers than news?. Journal of Financial Markets, 69, 100896. https://doi.org/10.1016/j.finmar.2024.100896
Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for Regression with Variables Generated from Unstructured Data. SSRN Electronic Journal No. 4842086 [Working Paper]. https://doi.org/10.2139/ssrn.4842086
<!-- rendered-citations:end -->
