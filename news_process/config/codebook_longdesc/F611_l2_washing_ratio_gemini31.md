---
family_id: F611
columns:
- washing_ratio_gemini31
- washing_ratio_gemini31_ctx
- washing_ratio_gemini31_ss
unit: 比率 (proportion, [0,1]; 分子分母均为文章计数, 无量纲)
formula: 'washing_ratio_gemini31{track} = count(gemini31_score{track}>0 且 innovation_substantiveness_full=="象征性") / count(gemini31_score{track}>0 且 innovation_substantiveness_full ∈ {"象征性","实质性"} 即已测出的样本), 按 track ∈ {full, ctx, ss} 分别计算, 银行-年聚合层面的比率; 面板列名对应 `washing_ratio_{llm}{_sfx}`, llm=gemini31'
producer: pipeline\panel\runner.py 方法 A2 单模型 (篇章级标记 L1001-1015, `_is_{llm}_positive{track}`=`{llm}_score{track}>0`、`_is_{llm}_pos_symb{track}`、`_svd_{llm}_pos{track}`; 面板聚合 L2209-2218, `vn=f'washing_ratio_{llm}{_sfx}'`) ; pipeline\panel\export.py (变量标签)
upstream:
- "21_tone_llms (gemini31_score{track}: LLM 单一厂商模型 gemini31(gemini-3.1-flash-lite, 走 OpenLux) 在该 track 上的情感分数, `>0` 判正; 与三家多数投票共识 is_positive{track} 是不同列, 后者对应无后缀 washing_ratio 家族而非本家族)"
- "21_tone_llms (innovation_substantiveness_full: LLM 判定报道内容是'实质性'创新举措还是'象征性'宣传姿态; pipeline/sentiment/tone_llms.py 同时写出 innovation_substantiveness_full/_ctx/_ss 三轨完整孪生列, 本家族公式仅取其中 _full 版本作实质性判定的锚定轨道, 这是家族公式的选择而非该列本身'无 ctx/ss 孪生')"
citations:
- doi: '10.1111/jofi.13412'
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
  vol: '80'
  issue: '2'
  pages_or_artno: 699-754
- doi: '10.1111/eufm.12509'
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: '10.1016/j.pacfin.2024.102600'
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: 'Ownership concentration and corporate greenwashing in China''s capital markets: Based on a multi-actors perspective'
  venue: Pacific-Basin Finance Journal
  vol: '89'
  issue: ''
  pages_or_artno: Article 102600
- doi: '10.1016/j.frl.2026.109684'
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  issue: ''
  pages_or_artno: '109684'
- doi: "10.1016/j.eap.2025.07.036"
  type: "journal"
  authors: "Zhou, H."
  year: 2025
  title: "Major shareholders' equity pledge and the “All talk and no action” strategy in digital transformation"
  venue: "Economic Analysis and Policy"
  vol: "87"
  pages_or_artno: "1630-1652"
- doi: "10.1016/j.frl.2025.108096"
  type: "journal"
  authors: "Li, Y."
  year: 2025
  title: "Can large language models (LLMs) replace human reading? Empirical evidence from sustainability reports"
  venue: "Finance Research Letters"
  vol: "85"
  pages_or_artno: "108096"
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_gemini31 系列刻画银行-年层面"洗稿式"金融科技报道在全部正面报道中的占比, 是本项目对企业"漂绿"(greenwashing)文献中"言行不一"测度思路向"金融科技叙事"场域的移植: 用文本挖掘识别哪些正面报道只是空洞姿态性宣传(象征性), 哪些对应真实的产品/流程/组织层面创新(实质性), 再以"象征性正面报道占已判定正面报道的比例"来量化一家银行在媒体上"说得多、做得少"的程度。构念方法学上呼应文本挖掘文献中"言行分野"(将叙事口吻正面与否, 和内容是否对应可验证具体行动分开识别)的一般思路, 并与本项目最邻近的 F 系家族(实质性/象征性二分类 innovation_substantiveness、per-model 情感分数)共享底层篇章级标注, 但 washing_ratio_gemini31 本身是这些底层列的派生比率, 不在文章级 parquet 落盘, 只在面板导出(runner.py)阶段由方法 A2(单模型)篇章级标记聚合而来。本家族命名中的 "gemini31" 后缀并非历史遗留、而是实际口径: 与本项目 LLM 三家(gpt54nano/gemini31/deepseekv4)互为稳健性框架下的方法 A2(单模型分支)一一对应, 情感极性判定只取 gemini31(gemini-3.1-flash-lite, 走 OpenLux)单一模型的分数 `gemini31_score{track}`(`>0` 判正), 而不是三家多数投票共识 `is_positive{track}`——后者对应另一个不含模型后缀的家族(无后缀 washing_ratio, 方法 A), 与本家族并列而非同一构念的重复。分子分母的构造顺序值得强调: 先筛出"该轨道下 gemini31 单模型判定为正面"的文章集合, 再在其中区分"象征性"与"实质性", 分子取象征性子集计数, 分母则不是全部 gemini31-正面文章数, 而是"gemini31-正面且实质性判定已成功测出"的文章数(即 `_svd_gemini31_pos`, subst-valid denominator)。这一分母口径是 2026-06-11 的 omni-g-runner-14 修正引入的(方法 A2 分母同域计数, 对齐方法 A 的 omni-g-runner-10 修正): 若某篇 gemini31-正面报道的 LLM 实质性/象征性分类失败(NaN, 既非"实质性"也非"象征性"标签), 该文章既进不了分子, 也不该被算进分母——旧实现里失败样本仍被计入全部正面文章的分母, 导致 LLM 分类失败率越高、washing_ratio_gemini31 越被系统性稀释走低, 制造分类噪声混同为"洗稿率真的低"的假象。同域分母修正后, washing_ratio_gemini31 只在"测量成功"的样本空间内计算比率, 是内部一致(measurement-consistent)的估计量, 而不受上游 LLM 分类失败率波动的机械牵连。
【方法学与计算】
分子: 该 track 下 `gemini31_score{track}>0`(gemini31 单模型判定为正面情感的报道, 由篇章级标记 `_is_gemini31_positive{track}` 记录) 且 innovation_substantiveness_full=="象征性"(该报道内容被 LLM 判为姿态性/宣传性叙事而非具体创新举措)的文章计数(篇章级 `_is_gemini31_pos_symb{track}`, 面板聚合列 `gemini31_pos_symb_count{track}`)。分母: 同一 track 下 `gemini31_score{track}>0` 且 innovation_substantiveness_full ∈ {"象征性","实质性"}(即该报道的实质性/象征性判定已经成功测出, 不含分类失败/缺测)的文章计数(篇章级 `_svd_gemini31_pos{track}`, 面板聚合列 `gemini31_pos_substvalid_count{track}`)。两者相除得到一个 [0,1] 区间内的比率, 银行-年层面通过对篇章级标记做加总再相除(而非对篇章级比率取均值)聚合, 与本项目通行的"分子分母各自求和再相除"聚合范式一致(避免除以零/小样本篇章级比率被简单平均放大方差)。需要特别注意: innovation_substantiveness_full 由 21_tone_llms(pipeline/sentiment/tone_llms.py)在情感三轨管线内一并产出, 本身实际存在完整的 _full/_ctx/_ss 三轨孪生列(与三轨铁律一致, 并非独立于三轨架构之外的单轨判定); 但 washing_ratio_gemini31 家族的分子分母公式刻意只取其中的 _full 版本作实质性判定的锚定轨道, 不随本家族自身的 full/ctx/ss track 切换——这是家族公式层面的设计选择(避免实质性判定本身也随窗口漂移、削弱分子分母的可比性), 而非该列本身缺失 ctx/ss 孪生。据此, washing_ratio_gemini31 的三个变体并非对同一构造做"三次重复", 而是分子分母中"情感极性判定"这一半随本家族 track 切换 gemini31_score{track}, "实质性判定"这一半在家族公式层面固定取 innovation_substantiveness_full, 是一种半-track-agnostic 的混合口径, 写手须避免误读为三轨各自完全独立测度同一构念, 也不应误读为 innovation_substantiveness 列本身不支持三轨。
【文献定位】
washing_ratio 家族方法学上呼应公司金融漂绿测度文献中"言行分野"(将叙事宣称与实际行动分开识别再构造错配比率)的一般范式: Duchin, Gao & Xu(2025, Journal of Finance)构造资产市场层面的漂绿指标区分"可持续性宣称"与工业污染资产实际处置行为的错配, 是本家族在顶刊层面最直接的方法论同源; Gorovaia & Makrominas(2024, European Financial Management)用自然语言处理从企业社会责任报告中识别漂绿, 方法路径(先分类叙事类型再构造比率)与本家族高度一致; Fan, Tang, Huang & Yang(2025, Pacific-Basin Finance Journal)从股权集中度视角研究中国资本市场企业漂绿行为, 为本家族在中国制度背景下的可比研究提供参照; Song, Hou, Ouyang & Hao(2026, Finance Research Letters)提出"AI washing"概念, 研究企业在人工智能相关信息披露上的策略性夸大与市场反噬, 与本家族"金融科技叙事洗稿"的构念高度平行, 均属"技术叙事真实性"这一新兴文本计量子领域。washing_ratio 越高, 意味着该银行的正面金融科技报道中越大比例只是姿态性宣传而非可验证的实质创新, 可用作银行"叙事管理"(narrative management)强度或媒体沟通策略的代理变量。 就该构念在中国科技叙事场景中的可识别性, Zhou (2025) 直接构造并检验中国上市公司数字化转型中的"只说不做"(all talk and no action)策略, 并以股权质押为驱动因素, 证明"宣称强度远超实质投入"是可测量、可识别的企业策略, 与本家族 washing_ratio 的构念定义一致; 惟其测度基于企业自身年报数字化词频与实际数字投入之比, 主体为非金融上市公司, 本家族仅取其构念定义与存在性, 不迁移其股权质押识别设计。就本家族分子与分母共同依赖的 innovation_substantiveness 判定环节, Li (2025) 以可持续报告为语料, 实证比较 LLM 抽取与人工阅读的结果一致性, 评估 LLM 能否替代人工完成文本内容判定, 为本家族以 LLM 逐篇判定实质性提供了 LLM-as-annotator 的效度前提; 但该文语料为英文可持续报告, 判定任务为可持续内容抽取, 未涉及象征-实质二分, 亦未做多模型投票, 其效度结论不能直接外推至本家族的中文银行新闻任务与 gemini31 这一具体模型版本。本 F611 作为 per-model 分支, 与 gpt54nano、deepseekv4 两支互为稳健性、不分主次, 各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 设定。
【与相邻测度的构念区分】
washing_ratio_gemini31 与无后缀的 washing_ratio(方法 A, 情感极性取三家 LLM 多数投票共识 is_positive{track})是最邻近但不同构念的一对: 前者是"方法 A2 单模型"分支, 后者是"方法 A 多数投票"分支, 二者共享同一套 innovation_substantiveness_full 实质性/象征性判定, 但情感极性半边的来源不同——命名后缀 gemini31 是该差异的忠实标记而非历史噪声, 不应被误读为"名不副实的历史遗留"。washing_ratio_gemini31 与其余两个 A2 单模型姊妹列 washing_ratio_gpt54nano{track}/washing_ratio_deepseekv4{track}(分别取 gpt54nano_score{track}>0、deepseekv4_score{track}>0 判正)构成 per-model 稳健性梯子, 三者各自 just-identified 并排、互为稳健性、不分主次, 不应混入同一 over-identified Hansen J 设定, 也不应把三者的差异解读为"洗稿程度真的不同"而应首先排查各模型情感判定分歧的机械性影响(参见 llm_bert 互稳健铁律的三家/三模型并排原则)。washing_ratio_gemini31 与 sub_frac/symb_frac(全样本口径的实质性/象征性文章占比, 不限定正面情感)、washing_asymmetry(washing_ratio 与其负面镜像 neg_sub_ratio 之差)、washing_tone_shift(象征性 vs 实质性报道之间的情感强度落差)则是同一方法族(runner.py 方法 A/A2/B/D/D2/E/E2/F 家族)下并排的多种"言行错配"测度构造, 同样各自 just-identified 并排、互为稳健性、不分主次。

## VAR: washing_ratio_gemini31

【变体差分】
本列是 washing_ratio_gemini31 家族在 full 轨道(标题+正文全文)上的 canonical 版本, 对应 runner.py 方法 A2 中 llm=gemini31、track=_full 的面板列 washing_ratio_gemini31(export.py 变量标签)。其分子分母均取 gemini31_score_full>0(gemini31 单模型在全文文本上的正面情感判定, 即三家互稳健框架中 gemini31 这一支)与 innovation_substantiveness_full(全文轨道的实质性/象征性判定; 该列本身在 21_tone_llms 环节同时产出 _full/_ctx/_ss 三轨完整孪生, 但本家族公式统一固定取其 _full 版本作实质性判定锚点, 不随本列自身的 track 联动切换)。作为三轨中信息量最完整的一支, full 轨道纳入文章全文语境, 不受实体窗口截断或同句共现约束, 因此该列样本覆盖面最广、分母(gemini31-正面且已测出实质性的文章数)最大, 统计效率最高, 是本家族在论文正文中默认呈现的主设定(canonical spec)。与 _ctx/_ss 两个变体相比, full 轨道不存在"回退"(fallback)语义问题——它本身就是无条件可计算的基准轨道, 后两者的可计算性反而依赖能否找到实体窗口或同句共现片段。在稳健性梯子上, 三轨互为稳健性、不分主次, 各自 just-identified 并排; 但由于 innovation_substantiveness 判定天然只在全文上产生, 使用本列做主设定在语义上最为自洽(分子分母的"文本窗口"完全对齐), 而 _ctx/_ss 版本则存在情感窗口与实质性判定窗口不对齐的固有张力, 读者在解释系数差异时应优先考虑这一结构性因素而非简单归因于测量误差。本列与无后缀的 washing_ratio_full(方法 A, 三家多数投票共识)是并排稳健性关系而非同一构念, 二者不应在同一模型设定中同时作为解释变量混合识别。

## VAR: washing_ratio_gemini31_ctx

【变体差分】
本列取 ctx 轨道(标题+目标实体前后局部窗口, 而非全文)上 gemini31 单模型的正面情感判定 gemini31_score_ctx>0 作分子分母的情感极性半边, 分母/分子中的实质性判定仍固定取 innovation_substantiveness_full(见家族 CORE 说明: 该列本身在 21_tone_llms 环节确有 _ctx/_ss 孪生, 但本家族公式刻意统一取 _full 版本, 不随本列的 ctx track 联动)。这意味着 washing_ratio_gemini31_ctx 度量的是"若只看银行/金科实体周边的局部语境、且仅依 gemini31 单一模型来判断情感基调, 该基调呈正面且被(基于全文的)象征性判定命中"的比例——本质上检验的是"局部叙事口吻"与"全篇内容实质"之间的错配, 而非纯粹重复 full 轨道的构念。当某篇报道标题/摘要式的局部语境读起来正面积极("XX银行携手某金科公司打造智慧金融新生态"), 但全文内容判定为象征性宣传而非具体创新举措时, 该文章更可能计入 ctx 轨道分子——这正是"标题党/局部造势"式洗稿的典型指纹, 与 full 轨道(要求整篇文本综合判定情感)相比更敏感地捕捉局部措辞层面的姿态性夸张。三轨(full/ctx/ss)按 CLAUDE.md 铁律各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 设定; ctx 轨道本身遵循 stage 14 ctx_materializer 的标准物化口径(实体窗口 prepend_title, 原文本列不动), 不存在 ss 式的"同句回退"语义, 因为 ctx 窗口构造机制本身不依赖银行∧金科的严格同句共现。本列与同轨道无后缀的 washing_ratio_ctx(三家多数投票共识)以及同轨道另两个 A2 单模型姊妹列 washing_ratio_gpt54nano_ctx/washing_ratio_deepseekv4_ctx 是并排的多模型稳健性梯子, 各自独立、互不替代。

## VAR: washing_ratio_gemini31_ss

【变体差分】
本列取 ss(same-sentence)轨道上 gemini31 单模型的正面情感判定 gemini31_score_ss>0 作分子分母的情感极性半边, 实质性判定仍锚定全文轨道 innovation_substantiveness_full。ss 轨道要求银行与金科关键词出现在同一句(±N 窗口, 默认半径 1, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制)才纳入该轨道的"严格共现文本", 是三轨中语境范围最窄、判定标准最严的一支; 按 CLAUDE.md 铁律, 当一篇文章不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True(与 ctx 轨道回退语义镜像对齐, 共享 n_articles 分母口径), 该情形下 gemini31_score_ss 实质上退化为基于全文文本判定的 gemini31 情感极性, 使得部分 ss 轨道观测在统计意义上趋近于 full 轨道而非真正的"同句局部"信号——解读该列系数时须留意样本中回退占比。在未回退(真同句共现)的子样本中, washing_ratio_gemini31_ss 度量的是"银行与金科科技词汇同句出现且 gemini31 判该同句语境为正面, 但全文被判定为象征性宣传"的比例, 是三轨中对"言之凿凿却无具体举措"式洗稿判据要求最严格的一支——理论上该轨道信噪比最高但样本量因严格共现约束而最小。三轨(full/ctx/ss)各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 设定, 也不应把三者的洗稿率差异简单解释为"洗稿程度不同", 而应首先排查样本构成(回退比例、共现密度)差异带来的机械性影响。本列与同轨道无后缀 washing_ratio_ss 及另两个 A2 单模型姊妹列同为并排的 per-model 稳健性梯子成员。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Zhou, H. (2025). Major shareholders' equity pledge and the “All talk and no action” strategy in digital transformation. Economic Analysis and Policy, 87, 1630-1652. https://doi.org/10.1016/j.eap.2025.07.036
Li, Y. (2025). Can large language models (LLMs) replace human reading? Empirical evidence from sustainability reports. Finance Research Letters, 85, 108096. https://doi.org/10.1016/j.frl.2025.108096
<!-- rendered-citations:end -->
