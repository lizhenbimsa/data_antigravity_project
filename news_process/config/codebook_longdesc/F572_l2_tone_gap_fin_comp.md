---
family_id: F572
columns:
- tone_gap_fin_comp_ctx
- tone_gap_fin_comp_full
- tone_gap_fin_comp_ss
unit: 语调缺口 (连续, 两组 bank-year 情感均值之差, 理论区间约 [-2,2], 实际集中于 [-1,1])
formula: 'tone_gap_fin_comp{track} = mean(llm_vote_score{track} | 财经类媒体) - mean(llm_vote_score{track} | 综合类媒体), 分组均值均在 (target_bank, year) 面板格内计算; track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\attention_media.py (缺口计算主体) ; pipeline\panel\export.py (面板列标签/装配)
upstream:
- llm_vote_score_full
- llm_vote_score_ctx
- llm_vote_score_ss
- fin_media_frac
- comp_media_frac
- tone_fin_media_full/_ctx/_ss
- tone_comp_media_full/_ctx/_ss
citations:
- doi: "10.1111/j.1540-6261.2007.01232.x"
  type: journal
  authors: "Tetlock, P. C."
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: "Journal of Finance"
  vol: "62"
  issue: "3"
  pages_or_artno: "1139-1168"
- doi: "10.1093/rfs/hhx055"
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who Captures the Power of the Pen?"
  venue: "Review of Financial Studies"
  vol: "31"
  issue: "1"
  pages_or_artno: "43-96"
- doi: "10.1257/aer.20170947"
  type: journal
  authors: "Qin, B., Strömberg, D., & Wu, Y."
  year: 2018
  title: "Media Bias in China"
  venue: "American Economic Review"
  vol: "108"
  issue: "9"
  pages_or_artno: "2442-2476"
- doi: "10.1016/j.iref.2024.01.067"
  type: journal
  authors: "Fang, Y., Wang, Q., Wang, Y., & Yuan, Y."
  year: 2024
  title: "Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China"
  venue: "International Review of Economics & Finance"
  vol: "91"
  pages_or_artno: "1150-1172"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514-5532"
- doi: "10.1007/s00521-024-10603-6"
  type: journal
  authors: "Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y."
  year: 2025
  title: "Chinese Fine-Grained Financial Sentiment Analysis with Large Language Models"
  venue: "Neural Computing and Applications"
  vol: "37"
  issue: "30"
  pages_or_artno: "24883-24892"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 tone_gap_fin_comp_full / tone_gap_fin_comp_ctx / tone_gap_fin_comp_ss 度量的是同一 bank-year 观测格内, 财经类专业媒体 (fin) 与综合类大众媒体 (comp) 对同一目标银行的报道语调之差, 是"媒体异质性"梯队 (与 tone_gap_fin_other / tone_gap_comp_other / tone_gap_central_local 并列) 中的一支。构念动机来自媒体经济学的一个基本判断: 不同类型媒体面向不同受众、承担不同的信息生产职能, 其报道语调不应被当作单一同质的"市场情绪"简单平均, 而应视为多个存在系统性差异的信息来源。财经类媒体 (证券时报、上海证券报、中国证券报、财新等专业财经报刊) 的编辑议程更贴近机构投资者与专业读者, 报道内容偏重业绩、监管、风险等硬信息且措辞相对克制审慎; 综合类媒体 (人民日报、新华社地方版、都市报等) 面向大众读者, 议程设置更容易受宣传/公关驱动、也更容易出现渲染式或叙事化的措辞。tone_gap_fin_comp 把这两类受众/职能差异转译为一个可直接检验的语调落差: 数值为正表示财经媒体对该银行的报道相对综合媒体更正面, 为负则反之。这一构念直接呼应 You, Zhang & Zhang (2018, Review of Financial Studies) 关于"谁在掌握媒体之笔" (Who Captures the Power of the Pen) 的分类框架, 以及 Qin, Strömberg & Wu (2018, American Economic Review) 关于中国媒体系统性偏向的证据; 二者共同提示媒体类型是理解中国语境下媒体情感生成机制不可忽视的调节变量, 而非可以忽略的噪声。
【方法学与计算】
分子分母的构造分两步。第一步在文章级 (article-level) 依据 pipeline\panel\attention_media.py 内的 _media_type 分类逻辑, 把该银行-金科共现文章按报道该文章的媒体名称归入 fin / comp / other 三类之一 (三分类互斥穷尽, 分类字典与判据见同模块内的媒体名单常量, 本家族不复述判据细节, 只承接其输出)。第二步在 (target_bank, year) 面板格内, 分别对归入 fin 类和归入 comp 类的文章计算 llm_vote_score{track} 的组内均值, 得到 tone_fin_media{track} 与 tone_comp_media{track} 两个中间面板列, 再相减得到 tone_gap_fin_comp{track} = tone_fin_media{track} − tone_comp_media{track}。这里的 llm_vote_score{track} 是三家 LLM (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 多数投票情感的数值编码, 与家族命名前缀 "l2" 对应的二级 (面板级) 派生列一致, 不是文章级原始概率。三个轨道 (full/ctx/ss) 各自独立走完上述两步, 互不借用彼此的中间列; 任一轨道的源列 llm_vote_score{track} 若在上游面板缺失 (attention_media.py 内 `if src not in df.columns: continue` 的优雅跳过判据), 该轨道对应的 tone_gap_fin_comp{track} 及其两个中间均值列整体缺失, 不会用其他轨道回填。分组均值的样本量取决于 fin_media_frac 与 comp_media_frac 所反映的该 bank-year 格内两类媒体覆盖的文章数, 当某一类媒体在该格内零覆盖时, 对应的组内均值为缺失, 缺口列随之缺失 (而非置零), 这一点在解读面板稀疏格 (尤其 T=2 开发库中的小样本格) 时需要特别注意, 缺失不代表语调持平。
【文献定位】
将媒体报道按类型分组后比较组间语调差异, 方法论上承袭 Tetlock (2007, Journal of Finance) 开创的"媒体情感作为可度量、可用于预测市场行为的信号"范式, 但本家族更进一步吸收了 You, Zhang & Zhang (2018) 与 Qin, Strömberg & Wu (2018) 关于媒体异质性 (media heterogeneity) 的核心洞见: 把媒体简单聚合为单一情感均值会掩盖不同媒体类型在报道立场上的系统性分歧, 而这种分歧本身就承载了识别信息 (例如财经媒体相对综合媒体更负面, 可能反映专业读者更早捕捉到风险信号; 反之则可能反映宣传性报道对负面消息的稀释)。中国银行业媒体情感与银行系统性风险的关联在 Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 中已有直接的中国场景证据, 为本家族在中国银行样本上的构念效度提供了同域支撑。三个语调子测度 (fin/comp 组均值本身) 采用的是三家 LLM 多数投票口径, 这一测度选择处在一条更宽的方法学谱系延长线上: Frankel, Jennings & Lee (2022, Management Science) 系统比较了传统机器学习分类器与词典法在披露情感测度上的表现差异, 其核心结论是基于统计学习的分类方法相较固定词典更能捕捉语境依赖的措辞含义, 这一"学习型方法优于规则型词典"的判断为本家族选择模型化 (而非纯词典) 情感测度路径提供了方法学上的先导依据, 但需明确该文比较的是传统机器学习分类器与词典法, 并非专门针对大语言模型, 本家族实际采用的三家 LLM 多数投票口径是在这一"学习型优于规则型"谱系上的进一步延伸, 而非该文直接验证的对象; 与 Lan, Wu, Xu, Feng & Zhang (2025, Neural Computing and Applications) 关于中文金融细粒度情感分析的近期证据结合来看, 才更直接支撑基于大模型的情感判定在中文金融文本上相较传统词典法具备更细粒度的语境识别能力这一具体论断。

## VAR: tone_gap_fin_comp_ctx

【变体差分】
本列是 tone_gap_fin_comp 家族的 ctx (context) 轨道实现, 差分锚点是分组均值所用的源情感列 llm_vote_score_ctx, 而非家族 canonical 讨论中笼统提到的"三轨"抽象。ctx 轨道的文本口径继承自 stage 14 ctx_materializer 物化的 content_ctx (标题 + 实体窗口截取正文), 情感判定同样经过 stage 21 三家 LLM 多数投票, 但判定所依据的正文范围比 full 轨道更窄, 只保留围绕目标银行/金科实体的上下文片段。因此 tone_fin_media_ctx 与 tone_comp_media_ctx 两个中间组均值、进而本列 tone_gap_fin_comp_ctx, 度量的是"聚焦实体上下文语境"下财经媒体与综合媒体的语调落差, 与 full 轨道基于全文语境的落差在数值上通常不相等, 也不应被当作同一测度的重复观测简单平均或相互替代。按照本仓库对多轨情感测度的口径铁律, full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 在实证设计中应分别作为独立的右手边解释变量或分别作稳健性检验, 禁止混入同一个 over-identified 的 Hansen J 过度识别检验框架。留篇门控 (即一篇文章是否被计入"银行金科报道") 采用 full-only 口径 (2026-06-29 起生效): 只要该文章在 full 轨道被 LLM 判定为有效报道 (llm_verified_full == True), 该文章就同时纳入 full/ctx/ss 三轨各自的分组均值计算行宇宙; ctx 轨道本身不重复做留篇判定, 是条件于 full 轨道留篇集合之上的测度轨。fin_media_frac/comp_media_frac 分组占比列本身是 track-agnostic 的 (不分轨道, 只与媒体类型分类相关), 但两组各自的语调均值与由此得到的缺口值是 ctx 轨道专属的。ctx 轨道缺列的优雅跳过判据同样适用于本列: 若上游面板不含 llm_vote_score_ctx, 本列及其两个中间列整体缺失。

## VAR: tone_gap_fin_comp_full

【变体差分】
本列是 tone_gap_fin_comp 家族的 full 轨道实现, 也是三轨中的口径锚 (canonical anchor): 分组均值所用的源情感列是 llm_vote_score_full, 对应 stage 14 物化的 content_full (标题 + 全文正文) 文本口径, 情感判定覆盖该文章的完整正文而非截取窗口。full 轨道之所以在本家族的三轨并排结构中承担"锚"的角色, 并非因为它在统计意义上优于 ctx/ss, 而是因为按照本仓库 2026-06-29 起确立的留篇门控口径, 一篇文章是否被认定为"一篇有效的银行金科报道"这一行宇宙判定本身就锚定在 full 轨道的 llm_verified_full 标志上 (即 `tone_llms.py::df_filtered` 与 `run_pipeline_function.py::_stage21_skip_is_compatible` 两处门控副本必须同步的判据)。因此 tone_fin_media_full 与 tone_comp_media_full 两个中间组均值所覆盖的样本行集合, 就是本家族 ctx/ss 两轨行宇宙的母集 (ctx/ss 是条件于 full 留篇集合之上的子集测度轨, 而非独立采样)。tone_gap_fin_comp_full 度量的是"完整正文语境"下财经类专业媒体与综合类大众媒体对同一目标银行报道语调的落差, 数值为正说明该银行-年份格内财经媒体的整体语调相对综合媒体更正面, 数值为负则相反; 当该格内 fin 或 comp 任一类媒体零覆盖 (fin_media_frac 或 comp_media_frac 为 0) 时, 对应组均值为缺失, 本列随之缺失而非置零, 不能把缺失误读为"语调持平/无差异"。full 轨道与 ctx/ss 两轨之间遵循互为稳健性、不分主次、各自 just-identified 并排、禁止混入同一 over-identified Hansen J 的口径铁律, 三者的差异不应被解读为孰优孰劣, 而应被解读为"全文语境" vs "实体聚焦语境" vs "银行金科同句语境" 三种不同构念窗口下语调落差的独立度量。

## VAR: tone_gap_fin_comp_ss

【变体差分】
本列是 tone_gap_fin_comp 家族的 ss (same-sentence) 轨道实现, 分组均值所用的源情感列是 llm_vote_score_ss, 对应 stage 14 物化的 content_ss 文本口径, 即目标银行实体与金科词在同一句子内共现的句子集合 (窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1, 与 stage 13 cooccurrence_filter 用于硬过滤的 sentence_radius 是两个独立配置键, 不可混用)。ss 轨道的回退语义镜像 ctx 轨道: 当某篇被 full 轨道判定为有效报道的文章在正文中不存在银行∧金科同句共现时, content_ss 退化为全文 body (等价于该篇退回 full 口径的文本), 并同时置位 ss_is_fallback=True; 这一回退共享同一分母 n_articles, 因此本列在计算 tone_fin_media_ss / tone_comp_media_ss 两个中间组均值时, 混入了一部分"实质上按 full 口径打分"的回退样本, 在解读该轨语调落差时应结合回退比例综合判断, 回退比例越高, ss 轨与 full 轨在数值上越趋同, 这是设计内的预期行为而非缺陷。ss 轨道同样只在 full 轨道留篇集合的子集上计算, 缺列时优雅跳过、整族置缺失。作为三轨中语境窗口最窄 (严格同句) 的一支, tone_gap_fin_comp_ss 理论上比 full/ctx 更能捕捉"银行与金科紧密同时出现的那句话"层面的语调分歧, 适合用作稳健性检验中排除"泛泛提及银行、金科话题较远"噪声样本后的敏感性分析; 但由于严格同句判据往往显著缩小样本量 (尤其在开发库 T=2 小样本格中), 该轨的组内均值方差可能明显偏大, 解读时须结合样本量与回退比例, 不应脱离 full/ctx 孤立解读。ss 轨与 full/ctx 两轨遵循同样的互为稳健性、各自 just-identified 并排、禁止混入同一 over-identified Hansen J 口径铁律。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Qin, B., Strömberg, D., & Wu, Y. (2018). Media Bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media Sentiment, Deposit Stability and Bank Systemic Risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese Fine-Grained Financial Sentiment Analysis with Large Language Models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
<!-- rendered-citations:end -->
