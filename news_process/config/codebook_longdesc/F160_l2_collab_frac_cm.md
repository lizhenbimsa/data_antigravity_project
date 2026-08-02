---
family_id: F160
columns:
- collab_frac_cm
- collab_frac_cm_ss
unit: 比率/占比 (proportion, 取值域 [0,1]; 分子分母同为银行-年文章计数)
formula: "collab_frac_cm = n_articles_collab_cm_ctx / n_articles_llm_valid_ctx (ctx 轨); collab_frac_cm_ss = n_articles_collab_cm_ss / n_articles_llm_valid_ss (ss 轨); 分子 = 该银行-年内 innovation_collab_mode 判为『外部协同』的文章数, 分母 = 同轨 LLM 有效文章数; 分母 0 时置 NaN"
producer: news_process/pipeline/panel/encode.py::_aggregate_ctx_diagonal ; news_process/pipeline/panel/iv_extensions.py::compute_iv_extensions
upstream:
- 14_materialize_ctx.parquet (content_ctx / content_ss + *_is_fallback)
- 21_tone_llms.parquet (innovation_collab_mode_ctx / innovation_collab_mode_ss)
- 40_panel_yearly.parquet (n_articles_llm_valid_ctx / n_articles_llm_valid_ss 分母)
citations:
- doi: 10.1002/smj.3729
  type: journal
  authors: Burford, N., Shipilov, A., & Furr, N.
  year: 2025
  title: "Ecosystem synergies as drivers of acquisitions"
  venue: Strategic Management Journal
  vol: 46
  issue: 13
  pages_or_artno: 3218-3251
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1111/joms.13063
  type: journal
  authors: Chen, X., Yang, Y., & Wei, J.
  year: 2025
  title: "How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence"
  venue: Journal of Management Studies
  vol: 62
  issue: 2
  pages_or_artno: 565-596
- doi: 10.1111/jofi.13384
  type: journal
  authors: Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L.
  year: 2024
  title: "FinTech credit and entrepreneurial growth"
  venue: Journal of Finance
  vol: 79
  issue: 5
  pages_or_artno: 3309-3359
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: "Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis"
  venue: Journal of Product Innovation Management
  vol: 41
  issue: 4
  pages_or_artno: 793-815
- doi: 10.3386/w33297
  type: wp
  authors: Puri, M., Qian, Y., & Zheng, X.
  year: 2024
  title: "From competitors to partners: Banks' venture investments in fintech"
  venue: NBER Working Paper No. 33297
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: "Do peer firms affect corporate financial policy?"
  venue: Journal of Finance
  vol: 69
  issue: 1
  pages_or_artno: 139-178
- doi: 10.1002/smj.507
  type: journal
  authors: Laursen, K., & Salter, A.
  year: 2006
  title: "Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms"
  venue: Strategic Management Journal
  vol: 27
  issue: 2
  pages_or_artno: 131-150
- doi: 10.1016/S0048-7333(01)00120-2
  type: journal
  authors: Hagedoorn, J.
  year: 2002
  title: "Inter-firm R&D partnerships: An overview of major trends and patterns since 1960"
  venue: Research Policy
  vol: 31
  issue: 4
  pages_or_artno: 477-492
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行金融科技创新的『协同模式』强度, 即在一家银行某一年度被媒体报道的金融科技创新叙事中, 有多大占比被判定为『外部协同』而非『自主研发』。这是 P5 (bank_fintech_collab) 论文线的处理构念, 理论根基是 Chesbrough (2003) 提出的开放式创新 (open innovation) 命题: 企业不再仅依赖内部封闭研发, 而是通过联盟、合资、股权投资、并购与外部技术伙伴的边界协同来获取与商业化技术。落到银行与金融科技公司这一具体关系上, 『外部协同』对应银行以入股、战略合作、联合实验室、收购金融科技企业等方式向外借力的开放路径; 『自主研发』对应银行依托自有科技子公司或内部团队的封闭路径。用大白话说: 这两列想量化的是『这家银行今年被新闻讲成更像是自己闷头做金融科技, 还是更像拉着外面的金融科技公司一起做』, 数值越高代表报道里外部协同的成色越足。开放式创新与自主研发的二分构念在近二十年的实证综述中被反复确认为一条稳定的战略维度 (Zhang, Ma, Liang, & Garrett, 2024); 而以联盟策略与技术互补性驱动新兴企业成长的机制 (Chen, Yang, & Wei, 2025)、以生态协同作为并购驱动力的证据 (Burford, Shipilov, & Furr, 2025)、以及跨行业早已确立的公司间研发伙伴关系长期趋势 (Hagedoorn, 2002), 共同为『银行—金融科技外部协同』这一测度提供了构念效度支撑。在开放度与创新绩效的关系上, Laursen 与 Salter (2006) 的经典研究进一步说明外部搜索广度本身即是可测的战略选择, 呼应本测度把『协同占比』作为连续处理强度的做法。银行侧的具体证据则来自金融科技信贷对创业增长的推动 (Hau, Huang, Lin, Shan, Sheng, & Wei, 2024) 与银行从竞争者转为伙伴、以风险投资方式投资金融科技的现象 (Puri, Qian, & Zheng, 2024)。数据链条为: 原始中文银行/金融科技新闻经预处理、银行与金融科技实体识别、共现硬过滤 (stage 13) 后, 在 stage 21 由 LLM 对每篇文章的 innovation_collab_mode 维度判类 (自主研发 / 外部协同 / 缺判), 再于面板导出阶段 (stage 40, encode.py) 聚合为银行-年占比。

【方法学与计算】
两列均产于 encode.py 的对角线聚合块 (_aggregate_ctx_diagonal), 与 substantiveness (_sc)、locus (_lc) 两维度共用同一聚合模式。collab_frac_cm 走 ctx 轨: 分子 n_articles_collab_cm_ctx = 银行-年内 innovation_collab_mode_ctx 判为『外部协同』的文章数, 分母 n_articles_llm_valid_ctx = 同一银行-年、同一 ctx 轨的 LLM 有效文章数, 分母大于 0 时相除、否则整列置 NaN 并告警。collab_frac_cm_ss 是其 ss 轨镜像, 分子分母严格逐轨改用 _ss 后缀量。这里有一条命门口径: 分子必须配同轨分母 (metric-audit 2026-06-02 终裁), 早期 ctx 分子错配 full 分母会产生占比大于 1 的轨道不对称伪值, 已修。分区恒等采用逻辑必然的弱式 n_articles >= n_articles_indep + n_articles_collab (R6 修): 当 LLM 对 collab_mode 维度部分失败时, 该文章既不入自主研发也不入外部协同却仍计入总篇数, 差额即 collab_mode 缺判文章, 由 v3.5.0 的 cell_NA 兜底列独立跟踪, 而非强行塞进任一类。三家 LLM (gpt54nano / gemini31 两家走 OpenLux、deepseekv4 直连) 对分类维度的判定经 verified 门控清票后进入聚合, 分母为该测度自身的 verified 篇数, 共识非裸多数票。留篇门控自 2026-06-29 起为 full-only: 一篇是否算『银行金科报道』只看 full 轨的 llm_verified_full, ctx/ss 因而降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track 分子分母仍照各自轨道独立计算。ss 轨的文本回退语义镜像 ctx: 当某文无银行与金融科技同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 分类在该回退文本上进行。三轨 (full / ctx / ss) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把任意两轨拼进同一 over-identified Hansen J —— 三者源自同一篇文章的三个剪裁窗口 (full=标题加全文 / ctx=标题加实体窗口 / ss=标题加银行金科同句窗), bank_type×year 的共同冲击逐字同污染各轨, 过度识别检验对真实威胁功效近零且近共线会拖垮弱工具 F 统计量。

【文献定位】
在测量方法上, 以生成式 LLM 对长文本做维度判类而非传统词典或人工编码, 其在会计与金融研究中的适用边界与操作规范由 de Kok (2025) 系统化, 本测度的三家投票、verified 门控与温度零冻结缓存即遵循这一可复现取向。在识别策略上, 协同占比作为处理变量存在同业反射与共同冲击的内生性隐忧, 本项目为 ctx/ss 两轨各配同轨的同业留一 (leave-one-out) 工具变量 (lpeer_collab_iv_ctx ← collab_frac_cm; lpeer_collab_iv_ss ← collab_frac_cm_ss), 其识别逻辑承接同业效应可由社会网络结构识别的经典结果, 并与 Leary 与 Roberts (2014) 用同业冲击识别公司财务政策的做法一脉相承; 若需过度识别, 只能跨族配对 (LOO × Bartik 或 LOO × zone-LOO), 而 shift-share 类工具的构造与推断规范见 Borusyak, Hull 与 Jaravel (2025)。与相邻测度的区分是: 本家族测的是『协同 vs 自主』的模式维度, 与 substantiveness (实质性)、locus (创新落点) 是三条正交的 LLM 分类维度, 三者在命名域间无字符串变换可达、由 encode.LLM_CLASS_SPEC 三元映射唯一互锁, 不可混淆。

## VAR: collab_frac_cm

【变体差分】
本列是 F160 家族的 ctx 轨对角线聚合列, 也是族内 canonical 命名列 (无 _ss 后缀), 但须强调其语义并非 full 轨: 名字里不带 _ctx 后缀是历史命名产物, 计算实体是 ctx 轨 (ctx = 标题 prepend 加实体窗口文本)。精确差分为: 分子取 innovation_collab_mode_ctx 判为『外部协同』的银行-年文章数 (n_articles_collab_cm_ctx), 分母取同轨 LLM 有效篇数 n_articles_llm_valid_ctx, 严格同轨配对以避免占比大于 1 的轨道不对称。相对 ss 孪生列, 本列的判类文本窗口更宽 (实体上下文窗口而非严格同句), 因而在同一银行-年通常有更大的有效分母与更平滑的占比, 是三轨中居于 full 与 ss 之间的中间粒度轨。作为 conditional-on-full 轨, 其行宇宙受 full-only 留篇门控约束, 是 full 留篇集的子集, 但分子分母一律逐 ctx 轨独立计, 不向 full 借分母。本列同时是 P5 collab 线 ctx 轨同业留一工具变量 lpeer_collab_iv_ctx 的内生源变量, 与 full/ss 两轨对应列各自 just-identified 并排、互为稳健性不分主次, 严禁与其他轨的 collab 占比拼入同一 over-identified Hansen J。在早期试跑 T=2 的浅面板上, ctx 轨可能出现零方差退化, 属预期而非缺陷, 生产期 T=19 语料上恢复正常变异。缺 n_articles_llm_valid_ctx 分母时本列整列置 NaN 并记录告警, 属优雅降级而非静默清零。需强调本列与 ctx 轨对角情感列 (llm_vote_tone_collab_cm_ctx) 共用同一对角聚合入口, 二者语义正交: 前者量协同叙事的相对篇幅占比, 后者量协同类文章内部的情感基调, 不可互相替代或并入同一识别式。

## VAR: collab_frac_cm_ss

【变体差分】
本列是 collab_frac_cm 的 ss 轨 (同句共现窗) 镜像, 差分维度纯粹在文本判据窗口: ss = 标题 prepend 加『银行与金融科技词同句正负 N 窗』的最窄剪裁, 判类基于 innovation_collab_mode_ss, 分子 n_articles_collab_cm_ss、分母 n_articles_llm_valid_ss 严格逐 ss 轨配对, 绝不借用 ctx 或 full 的分母。回退语义镜像 ctx: 当某篇文章无银行与金融科技的同句共现时, content_ss 优雅回退为全文正文、置 ss_is_fallback=True, 分类在该回退文本上进行, 分母与 ctx/ss 共享 n_articles 口径。因窗口最窄, 本列在浅面板上最易出现有效篇数偏少、方差塌缩甚至逐格为 NaN 的退化, 在早期试跑 T=2 数据上属预期, 生产 T=19 语料上恢复。本列是 ss 轨同业留一工具变量 lpeer_collab_iv_ss 的内生源变量, 紧凑前缀 lpeer_ 使 _ss_lag1 全名不超过 32 字符、绕开 Stata 变量名截断歧义。作为 conditional-on-full 的最窄稳健性轨, 它与 full/ctx 两轨对应列各自 just-identified 并排、互为稳健性不分主次, 严禁把 full/ctx/ss 任意两轨的 collab 占比拼成一对工具跑同一 over-identified Hansen J —— 三轨同源一篇文章、共同冲击逐字同污染, 过度识别既无功效又近共线。ss 轨提供的是对『银行与金融科技在最贴近语境下确被同句提及』这一严格共现前提下协同叙事强度的稳健性读数, 与 ctx 轨的中间粒度、full 轨的全文粒度构成规格稳健性并排。

<!-- rendered-citations:begin -->
Burford, N., Shipilov, A., & Furr, N. (2025). Ecosystem synergies as drivers of acquisitions. Strategic Management Journal, 46(13), 3218-3251. https://doi.org/10.1002/smj.3729
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Chen, X., Yang, Y., & Wei, J. (2025). How do new ventures thrive in ecosystem venturing: The impacts of alliance strategy and technology interdependence. Journal of Management Studies, 62(2), 565-596. https://doi.org/10.1111/joms.13063
Hau, H., Huang, Y., Lin, C., Shan, H., Sheng, Z., & Wei, L. (2024). FinTech credit and entrepreneurial growth. Journal of Finance, 79(5), 3309-3359. https://doi.org/10.1111/jofi.13384
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Puri, M., Qian, Y., & Zheng, X. (2024). From competitors to partners: Banks' venture investments in fintech. NBER Working Paper No. 33297 [Working Paper]. https://doi.org/10.3386/w33297
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Laursen, K., & Salter, A. (2006). Open for innovation: The role of openness in explaining innovation performance among U.K. manufacturing firms. Strategic Management Journal, 27(2), 131-150. https://doi.org/10.1002/smj.507
Hagedoorn, J. (2002). Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. Research Policy, 31(4), 477-492. https://doi.org/10.1016/S0048-7333(01)00120-2
<!-- rendered-citations:end -->
