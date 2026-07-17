---
family_id: F537
columns:
- sum_wd_mw_gemini31_ctx
- sum_wd_mw_gemini31_full
- sum_wd_mw_gemini31_ss
unit: 无量纲权重和 (媒体权威性权重 media_authority_weight 的银行-年度加总, 分母口径)
formula: 'sum_wd_mw_gemini31{track} = Σ_i∈bank-year media_authority_weight_i · 1{gemini31_score{track}_i not null}
  ; 即仅对该银行-年度内 gemini31 三分类打分非缺失 (有效) 的文章 i, 累加其媒体权威性权重, 由
  runner._build_llm_valid_masked_weights(df, mw, ''mw'') 在篇章级生成掩码列 _wd_mw_gemini31{track}
  = media_authority_weight.where(gemini31_score{track}.notna()), encode.aggregate_panel 逐银行-年度
  sum 聚合得到本列。'
producer: pipeline/panel/runner.py::_build_llm_valid_masked_weights (篇章级掩码列 _wd_mw_gemini31{track}
  生成, 步骤 3c 媒体权威性加权预计算区块) + pipeline/panel/encode.py::_agg_dict / aggregate_panel
  (agg[f'sum_wd_{wtag}_{grp}{track}'] = (f'_wd_{wtag}_{grp}{track}', 'sum') 逐银行-年度聚合, encode.py
  约 1200-1203 行)
upstream:
- "21_tone_llms (gemini31_score{track} 三分类判定)"
- "runner.compute_media_authority_weights (media_authority_weight)"
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
- doi: 10.1017/pan.2021.33
  type: journal
  authors: Ying, L., Montgomery, J. M., & Stewart, B. M.
  year: 2022
  title: 'Topics, Concepts, and Measurement: A Crowdsourced Procedure for Validating
    Topics as Measures'
  venue: Political Analysis
  vol: '30'
  issue: '4'
  pages_or_artno: 570-589
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding,
    Dictionary Approaches, and Machine Learning Algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
- doi: "10.3982/te6424"
  type: "journal"
  authors: "Eliaz, K., & Spiegler, R."
  year: 2026
  title: "News media as suppliers of narratives (and information)"
  venue: "Theoretical Economics"
  vol: "21"
  issue: "3"
  pages_or_artno: "928-972"
- doi: "10.1080/19312458.2024.2378690"
  type: "journal"
  authors: "Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K."
  year: 2025
  title: "On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions"
  venue: "Communication Methods and Measures"
  vol: "19"
  issue: "1"
  pages_or_artno: "46-62"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 sum_wd_mw_gemini31_full / _ctx / _ss 不是一个独立的"语调"或"态度"测度, 而是配套 Media-Authority-Weighted (MW) 三分类语调指标 gemini31_tone_mw{track} 的有效分母 (valid-mask denominator)。它衡量的是: 在给定银行-年度单元内, 三家投票 LLM 之一 gemini-3.1-flash-lite (家族命名短名 gemini31) 对某一报道文本轨道成功给出可用三分类判定 (正面/中性/负面, 对应 gemini31_score{track} 非缺失) 的那些文章, 其"媒体权威性权重" (media_authority_weight) 之和。列名前缀 wd 取自 "weight-denominator" (权重分母) 的缩写, mw 对应 media authority weight (媒体权威性加权), gemini31 标注权重所服务的具体 LLM 模型分支, track 后缀 (full/ctx/ss) 标注文本轨道。三列共同构成 encode.py 中计算 gemini31_tone_mw{track} = gemini31_score_mw_sum{track} / sum_wd_mw_gemini31{track} 时严格匹配分子分母口径的分母侧。

【方法学与计算】
背景动因写在 encode.py 的 encode-01 修复注释里 (metric-audit 2026-06-10): LLM 三分类打分 gemini31_score{track} 是 nullable 值 — 当某篇文章 LLM 输出解析失败/置信不足/被门控排除时该列为 NA, 而 pandas groupby('sum') 在做分子加权和 (score×weight) 时天然跳过 NA 行, 相当于"只累加打分成功的文章"。如果分母仍用该银行-年度全部文章的物理权重总和 (Σ weight over all, 不区分 gemini31 是否成功打分), 就会出现分子是"有效子集"、分母是"全集"的口径错配, 使加权平均语调系统性向 0 收缩 — LLM 该轨道打分失败率越高, 这种向零衰减就越严重, 尤其在跨模型比较三家 LLM 稳健性时会人为压低失败率较高模型的语调强度, 制造虚假的模型间差异。修复办法是为每个需要 valid-mask 的族 (LLM 聚合投票 llm、逐模型 gpt54nano/gemini31/deepseekv4、logit-to-score 概率 prob) 各建一个"只在打分有效时取权重、否则记 NaN"的篇章级掩码列, 再对其做 sum 聚合 — pandas 的 sum 对 NaN 天然跳过, 因此聚合结果精确等于"Σ media_authority_weight over {该银行-年度内 gemini31 三分类判定有效的文章}"。这就是本列的算法定义: 掩码构造发生在 pipeline/panel/runner.py::_build_llm_valid_masked_weights(df, mw, 'mw') (调用点在步骤 3c 媒体权威性加权预计算区块, mw = df['media_authority_weight'].fillna(1.0)), 产出篇章级列 _wd_mw_gemini31{track} = media_authority_weight.where(gemini31_score{track}.notna()); 而后 pipeline/panel/encode.py 的聚合规格字典把该列注册为 agg[f'sum_wd_mw_gemini31{track}'] = ('_wd_mw_gemini31{track}', 'sum'), 由 aggregate_panel 按 (target_bank, year) 分组求和写入面板。media_authority_weight 本身由 compute_media_authority_weights (源码内部注释标注其方法学动因源自媒体经济学文献中的媒体权威性框架, 具体文献见下文【文献定位】段落引注) 依据发文媒体的传播广度/权威层级赋值, fillna(1.0) 对权重缺失的媒体记 1.0 作中性权重, 不因媒体元数据缺失而使该文章权重归零。三轨 full/ctx/ss 各自独立走一遍上述流程: 掩码有效性判据是 gemini31_score{track} 各轨道自身的非缺失状态, 不借用其他轨道的有效性, 因此三列在同一银行-年度内数值一般不相等 (某文章可能 full 轨判定成功但 ctx 轨因实体窗口截断导致 LLM 输出发生变化而失败, 反之亦然)。留篇门控铁律 (full-only, 2026-06-29) 决定了进入 stage 21 三家 LLM 判定环节的文章行宇宙以 llm_verified_full 为准, ctx/ss 是 conditional-on-full 的测度轨, 本列同样继承该行宇宙; ss 轨在无银行∧金科同句共现时回退全文正文 (镜像 ctx 的回退语义, content_ss=body 且 ss_is_fallback=True), 该回退不改变本列的掩码判据 (仍看 gemini31_score_ss 是否非缺失), 只影响 gemini31 在该轨读到的输入文本。
本列本身没有独立经济含义 (不建议单独作为回归 DV/IV), 其唯一用途是作 gemini31_tone_mw{track} 的匹配分母; 当该银行-年度单元 gemini31 在该轨道零篇有效打分时, 本列聚合结果为 0, encode.py 中 _llm_denom 辅助函数会将 0 替换为 NaN (panel[col].replace(0, np.nan)) 以避免除零, 使下游 gemini31_tone_mw{track} 该格记为缺失而非错误的无穷大或 0。 晚近文献从理论与测量两侧进一步夯实了本列的两个构造前提。Eliaz 与 Spiegler (2026) 以理论建模把新闻媒体刻画为叙事 (而不仅是信息) 的供给者, 分析不同媒体所供叙事如何塑造受众信念, 为"不同来源的报道不等价、须按来源加权"这一 media_authority_weight 的存在性前提提供了理论侧论证; 惟须注意该文是纯理论均衡分析, 其媒体差异化维度是叙事内容而非权威度, 不提供任何可迁移的权重赋值方案或经验参数, 与本项目 config 登录表加未登录来源退默认再 fillna(1.0) 的具体取值口径无对应关系。Laurer、Casas 与 Welbers (2025) 以对照实验检验语言模型作为测量工具的效度, 证明指令/提示设计会实质改变效度与偏误, 恰锚定本列掩码赖以成立的效度前提: 本列以 gemini31 在该轨是否给出有效判断界定分母求和域, 该掩码本身即模型效度的函数。迁移边界须诚实标明: 原文对象为英文传播学分类任务与开源指令微调模型, 本项目为中文新闻加三家商用 API 模型; 原文结论支持"加指令可提效度", 而本项目情感提示词 v8 已字节冻结、嵌入侧刻意零 instruct 前缀, 二者设计取向不同, 不可直接迁移; 原文亦不涉及任何权重加权分母口径。
【文献定位】
媒体权威性加权语调的构念源头是媒体经济学与文本情感测量交叉领域对"信息源可信度应折算进语调强度"的共识: 不同媒体在读者触达面、编辑权威性、市场影响力上存在系统性差异, 未加权的简单平均会让权威性弱的自媒体/小报与权威财经媒体的报道等量齐观, 掩盖真正影响市场参与者预期的信号来源。本列所服务的 valid-mask 修正逻辑, 本质上是"多标注者/多模型聚合测度"文献中对缺失值处理稳健性的一般性关切: Gilardi, Alizadeh & Kubli (2023, PNAS) 系统比较大语言模型与众包标注者在文本标注任务上的表现差异, 指出模型输出的可用性 (是否成功产出可解析标签) 本身是需要显式建模而非忽略的环节, 这与本列把"打分是否有效"作为一等公民纳入分母构造的做法在方法论关切上一致。Ying, Montgomery & Stewart (2022, Political Analysis) 提出对众包/自动化测度的"概念-测量"对应关系做形式化校验的框架, 强调聚合测度的分子分母必须共享同一有效样本域, 否则会引入系统性偏误, 这正是本家族要修正的 encode-01 向零衰减问题的一般化表述。van Atteveldt, van der Velden & Boukes (2021, Communication Methods and Measures) 对比人工标注、众包编码、词典法与机器学习算法在情感分析效度上的表现, 其核心发现之一是不同方法的"失败/缺失模式"不同 (词典法极少缺失, 机器学习/众包会因置信度不足产生系统性缺失), 呼应本项目对 LLM 族与词典/BERT 族分别处理缺失掩码的差异化设计 (词典族因 stage 13 硬过滤后结构性无 NaN 而不建掩码, LLM 族因存在解析失败必须建掩码)。三家投票 LLM (gpt54nano/gemini31/deepseekv4) 互为稳健性、不分主次是本项目情感测量体系的铁律, 本家族的 gemini31 分支是该铁律在媒体权威性加权维度上的具体落实, 与 gpt54nano、deepseekv4 对应的姊妹家族 (F536/F538 等) 结构完全对称, 保证跨模型比较时口径一致、不因某一模型解析失败率更高而在加权平均层面被系统性低估。

## VAR: sum_wd_mw_gemini31_ctx

【变体差分】
本列取 track=_ctx, 即以"标题 + 实体窗口"截取的上下文文本 (content_ctx, 由 stage 14 ctx_materializer 物化, prepend_title 前置标题) 作为送入 gemini-3.1-flash-lite 判定的输入。判据仍是 gemini31_score_ctx 是否非缺失: 若某篇文章的 ctx 窗口截断后送入 LLM 未能得到可解析的三分类输出 (无论 full 轨是否成功), 该文章在 _wd_mw_gemini31_ctx 篇章级掩码列中记为 NaN, 不计入本列的银行-年度加总。ctx 轨的留篇行宇宙继承 full-only 门控 (2026-06-29 铁律): 是否算作"一篇银行金科报道"只看 llm_verified_full, ctx 轨是 conditional-on-full 的稳健性/测度轨而非独立门控标准, 因此本列的分母行集合是 full 轨留篇集的子集, per-track 有效性照算不借用。ctx/full/ss 三轨在本家族内各自 just-identified 并排, 互为稳健性、不分主次, 严禁把三轨的 sum_wd_mw_gemini31 混进同一 over-identified Hansen J 检验或同一 IV 方程作联合矩条件。实践含义: 由于 ctx 窗口比 full 全文短、上下文信息更聚焦但也更易因实体窗口截断丢失判定所需线索, ctx 轨 gemini31 打分失败率与 full 轨通常不同, 因此 sum_wd_mw_gemini31_ctx 与 sum_wd_mw_gemini31_full 在同一银行-年度内数值一般不相等 — 差异本身即反映了两条文本构造管线对 LLM 可判定性的不同影响, 是 ctx 轨作为 full 轨稳健性检验的价值所在, 而非误差或需要调和的不一致。当某银行-年度在 ctx 轨零篇有效判定 (本列聚合为 0) 时, 下游 gemini31_tone_mw_ctx 该格经 encode.py 的 replace(0, np.nan) 处理记为缺失, 不产生除零污染。

## VAR: sum_wd_mw_gemini31_full

【变体差分】
本列取 track=_full, 即以完整正文 (标题 + 全文内容, content_full) 作为送入 gemini-3.1-flash-lite 判定的输入, 是三轨中信息量最完整、也是留篇门控 (full-only, 2026-06-29) 直接锚定的轨道: 一篇报道是否被计入"银行-金科"留篇集, 判据即 llm_verified_full == True, 该判据与本列所依赖的 gemini31_score_full 有效性判据 (三分类是否非缺失) 是两个相关但不同层级的概念——前者是文章能否进入分析样本的门槛, 后者是进入样本后该模型该轨道是否成功给出可解析输出。full 轨因输入信息最完整, 通常 LLM 解析失败率相对 ctx/ss 更低, 但仍可能因文本超长截断、格式异常等原因出现个别缺失, 本列忠实反映这一真实缺失模式而不做插补。作为 P1 主线论文 (bank_fintech_tone) 的 headline treatment 轨道 (llm_vote_tone_full 系), full 轨对应的 gemini31_tone_mw_full 及其分母 sum_wd_mw_gemini31_full 在跨模型稳健性表 (镜像 27_tableA12 cross-model FWER 模板的构念) 中承担锚定角色, 与 sum_wd_mw_gemini31_ctx / sum_wd_mw_gemini31_ss 互为稳健性并排, 三者共享同一 gemini31 模型但不分主次, 不得混入同一 over-identified 矩条件检验。
从数据链路上看, full 轨的行宇宙 (即哪些文章参与本列的银行-年度加总) 是三轨中最宽的一个: 因为 ctx/ss 是 conditional-on-full 的子集测度, 它们各自的有效判定文章数天然不超过 full 轨潜在覆盖的文章数; 而 full 轨内部仍会因个别 LLM 解析失败产生真实缺失, 本列的媒体权威性权重加总据此如实反映 gemini31 在完整正文输入下的可判定覆盖面。该覆盖面与三家投票 LLM 中另外两家 (gpt54nano/deepseekv4) 各自的 sum_wd_mw_{model}_full 姊妹列并非强制相等——三家模型的解析失败模式彼此独立, 这正是跨模型稳健性检验 (镜像 27_tableA12 cross-model FWER 模板) 需要分别核算各模型专属分母、而不能共用同一分母的原因; 若三家模型强行共享分母, 会把某一家模型的解析失败误算进另外两家的加权平均语调, 制造虚假的模型间一致性或差异性。此外, media_authority_weight 对权重缺失媒体记 1.0 中性值的处理 (fillna(1.0)) 在 full 轨同样生效, 保证媒体元数据缺失不会通过分母端制造额外的向零偏误, 与 gemini31 打分本身的有效性判据相互独立、互不污染。

## VAR: sum_wd_mw_gemini31_ss

【变体差分】
本列取 track=_ss, 即以"标题 + 银行∧金科同句共现窗口" (content_ss, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句) 作为送入 gemini-3.1-flash-lite 判定的输入, 是三轨中文本跨度最窄、语境最聚焦于银行与金融科技词汇同句共现的判定轨道。当某篇文章不存在银行与金科词汇的同句共现时, ss 轨回退语义镜像 ctx: content_ss 退化为全文正文 (与 content_full 相同), 且 ss_is_fallback 标记为 True, 该回退不影响 gemini31_score_ss 是否有效这一判据本身 (回退后的全文照样送入模型判定, 判定成功与否仍由模型输出解析结果决定), 但意味着回退发生的文章其 ss 轨判定环境实质上退化为 full 轨环境。本列的掩码构造与 ctx/full 完全同构: _wd_mw_gemini31_ss = media_authority_weight.where(gemini31_score_ss.notna()), 银行-年度聚合求和。由于 ss 轨判据比 ctx 更严格 (要求同句而非窗口邻近), 在生产语料上其非回退比例通常低于 ctx, 因此该轨的有效打分文章集合、进而本列的权重加总, 与 full/ctx 两轨的差异可能更明显, 这一差异是三轨互为稳健性设计的预期表现而非缺陷。三轨 (full/ctx/ss) 及其对应的 sum_wd_mw_gemini31 家族三列各自 just-identified 并排, 在任何联合识别方程或跨模型 FWER 校正表中都必须分别单独进入、不得混入同一 over-identified Hansen J 检验; dev T=2 小样本上 ss 轨因样本量极小可能出现零方差退化, 属预期现象, 生产 T=19 全量语料上不受此限。

<!-- rendered-citations:begin -->
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Ying, L., Montgomery, J. M., & Stewart, B. M. (2022). Topics, Concepts, and Measurement: A Crowdsourced Procedure for Validating Topics as Measures. Political Analysis, 30(4), 570-589. https://doi.org/10.1017/pan.2021.33
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The Validity of Sentiment Analysis: Comparing Manual Annotation, Crowd-Coding, Dictionary Approaches, and Machine Learning Algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Eliaz, K., & Spiegler, R. (2026). News media as suppliers of narratives (and information). Theoretical Economics, 21(3), 928-972. https://doi.org/10.3982/te6424
Laurer, M., van Atteveldt, W., Casas, A., & Welbers, K. (2025). On Measurement Validity and Language Models: Increasing Validity and Decreasing Bias with Instructions. Communication Methods and Measures, 19(1), 46-62. https://doi.org/10.1080/19312458.2024.2378690
<!-- rendered-citations:end -->
