---
family_id: F256
columns:
- exc_gpt54nano_score_ctx
- exc_gpt54nano_score_full
- exc_gpt54nano_score_hw_ctx
- exc_gpt54nano_score_hw_full
- exc_gpt54nano_score_hw_ss
- exc_gpt54nano_score_ss
- exc_gpt54nano_score_w_ctx
- exc_gpt54nano_score_w_full
- exc_gpt54nano_score_w_ss
unit: 无量纲情感得分均值 (排除疑似退出覆盖媒体后的 bank-year 语调均值; hw/w 变体为加权后再取均值, 保留权重量纲)
formula: "exc_gpt54nano_score{track} = mean_{a ∈ bank-year ∧ media(a) ∉ ceased_set} gpt54nano_score{track}_a; exc_gpt54nano_score_hw{track} = mean_{a ∈ alive} (gpt54nano_score{track}_a × herd_weight{track}_a); exc_gpt54nano_score_w{track} = mean_{a ∈ alive} (gpt54nano_score{track}_a × mention_density_a); gpt54nano_score ∈ {+1, 0, -1} 为 gpt-5.4-nano 单模型签名语调票; ceased_set = confirmed ∪ suspected 覆盖退出媒体; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (C.3/C.4 停刊排除均值, 调用 detect_defacto_cessation) ; news_process/pipeline/panel/runner.py (步骤 3b/3d 逐文章 gpt54nano_score_w / gpt54nano_score_hw 加权列)
upstream:
- 21_tone_llms.parquet (gpt-5.4-nano 逐文章签名语调票 gpt54nano_score{track})
- 24_herd_decay_processor.parquet (三轨 herd_weight{track}; 供 _hw 变体)
- 40_panel_yearly.parquet (bank-year 聚合 + 媒体来源退出检测)
citations:
- doi: 10.48550/arXiv.2603.20237
  type: arxiv
  authors: Muhammad, T.
  year: 2026
  title: "Temporal coverage bias in financial panel data: A coverage-aware structuring framework with evidence from the Dhaka Stock Exchange"
  venue: arXiv
- doi: 10.1016/j.jcorpfin.2025.102772
  type: journal
  authors: Schwenkler, G., & Zheng, H.
  year: 2025
  title: "News-driven peer co-movement in crypto markets"
  venue: Journal of Corporate Finance
  vol: 93
  pages_or_artno: Article 102772
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.48550/arXiv.2308.03531
  type: arxiv
  authors: Färber, M., Schwade, J., & Jatowt, A.
  year: 2023
  title: "Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election"
  venue: arXiv
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: Review of Financial Studies
  vol: 36
  issue: 12
  pages_or_artno: 4919-4964
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
- doi: 10.1257/aer.98.4.1413
  type: journal
  authors: Khwaja, A. I., & Mian, A.
  year: 2008
  title: "Tracing the impact of bank liquidity shocks: Evidence from an emerging market"
  venue: American Economic Review
  vol: 98
  issue: 4
  pages_or_artno: 1413-1442
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"在剔除疑似退出话题覆盖的媒体来源之后, 单一大语言模型 GPT-5.4-nano (gpt54nano) 对某银行-年内每篇银行金融科技报道所给语调票的重算均值"。它不是一个新的情感测度, 而是主情感测度的样本选择稳健性 (sample-selection robustness) 变体: 把可能因媒体停刊或停止覆盖而系统性消失的报道从聚合分母中剔除, 再在存活媒体子样本上重算 gpt54nano 单模型语调, 用以检验主结论是否被幸存者偏差 (survivorship bias) 驱动。九个列由三条文本轨道 (full、ctx、ss) 与三种加权口径 (等权、跟风加权 hw、提及密度加权 w) 交叉而成, 每列都是一个 bank-year 级的均值量。exc_ 前缀专指"排除覆盖退出媒体"这一子样本口径, 与全样本口径的 gpt54nano 语调家族逐列对偶: 前者剔除疑似退出者、后者保留全部媒体, 二者并置即可读出媒体来源消失对语调水平的贡献。之所以要为 gpt54nano 这一单一厂商模型单独物化排除口径, 是因为跨厂商三角验证要求每家模型都能在同一稳健性维度上被独立复核, 而非只对三家投票共识做一次排除。gpt54nano 是 stage 21 情感三家投票中经 yunwu 网关路由的一家 (与 gemini31 同经 yunwu, 与直连 api.deepseek.com 的 deepseekv4 异源), 其单模型语调票与共识票 llm_vote_score 相互独立, 供跨厂商稳健性对照。

【方法学与计算】
计算分三步。第一步在 stage 21 (tone_llms) 完成: 每篇报道以 full、ctx、ss 三种文本形态提交给 gpt-5.4-nano, 模型经同一条思维链 Prompt 同时输出真伪判定与情感判定, 情感判定被离散映射为签名语调票 gpt54nano_score{track} ∈ {+1, 0, −1}。第二步在面板构建阶段 (runner.py 步骤 3b/3d) 预计算两种加权文章列: 提及密度加权列 gpt54nano_score_w{track} = 签名票乘以文章的 mention_density (VW, 提及越密权重越高), 跟风加权列 gpt54nano_score_hw{track} = 签名票乘以同轨的跟风衰减权重 herd_weight{track} (HW, 对扎堆转载降权)。第三步在媒体异质性函数 compute_media_heterogeneity 内完成排除与聚合: 先由 detect_defacto_cessation 识别覆盖退出媒体——凡某媒体在银行金科子样本上的末次报道年份早于样本末年减 threshold_gap (默认 2)、且累计报道数不少于 10 篇者标记为疑似退出, 并与国家新闻出版署 (NPPA) 的注销/停办/休刊名录交叉验证, 得到 ceased_set = confirmed ∪ suspected (未经证实的疑似者亦保守全量纳入排除集); 随后取 df_alive = 媒体来源不在 ceased_set 内的报道子集, 在其上按 (target_bank, year) 对等权票、hw 加权票、w 加权票分别取均值, 落为本家族九列。三条轨道的权重严格逐轨构造、互不借用。计数类兄弟列 n_articles_exc 走"计数 Σ over ∅ = 0"的零填契约, 而本家族的比例/情感类 exc_ 列按契约保持 NaN、勿连带零填。

【文献定位】
本家族的方法学根基是"媒体来源消失会污染基于媒体文本的面板测度"这一识别关切。Muhammad (2026) 直接提出面板数据中的时间覆盖偏误 (temporal coverage bias) 与覆盖感知的样本结构化框架, 是本排除口径最贴切的构念锚: 若不识别覆盖退出, 语调水平会向存活媒体的口径系统性偏移。Färber et al. (2023) 从媒体覆盖的多样性、平衡性与差异度三维度刻画覆盖结构, 呼应了"媒体来源构成变化本身即测量误差来源"的诚实披露。在以媒体语调作为核心变量的更长脉络上, Hwang & Kim (2017) 在 Journal of Financial Economics 上证明文本可读性等书面表达特征对市场后果有独立解释力, 支撑了以中文银行报道文本 (而非仅数值) 提取语调的可行性; Hassan et al. (2023) 在 Review of Financial Studies 上以文本命中计数构造企业层面暴露度, 其提及密度加权思路正是本家族 w 变体 (mention_density 加权) 的方法学同源。样本选择偏误对识别的威胁则可追溯至 Khwaja & Mian (2008) 的银行冲击识别范式——当情感测度进一步用于 Bartik 式暴露加权工具变量时, 媒体来源退出会经由分母污染工具变量, Apfel (2024) 关于放松 shift-share 工具变量排除限制的处理为此提供了稳健性对照。Schwenkler & Zheng (2025) 关于新闻驱动同侪共动的证据则从另一侧说明媒体网络结构 (含跟风转载) 何以需要 hw 加权降权。⚠ 铁律: 三条文本轨道 (full / ctx / ss) 以及三种加权口径 (等权 / hw / w) 各自 just-identified 并排, 互为稳健性、不分主次, 严禁把跨轨或跨加权口径的排除均值混进同一条 over-identified 的 Hansen J 检验; 每条轨道、每种口径各自单独进入自回归或 2SLS 作稳健性并排。本家族为 gpt54nano 单模型口径, 采用 per-model 独立降级: 若 gpt54nano 端点缺席, 仅其自身族列置空, 不牵连 gemini31 / deepseekv4, 亦非 co-primary 嵌入那种 both-or-neither 连坐。

## VAR: exc_gpt54nano_score_ctx

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ctx 轨上等权签名语调票的 bank-year 均值。模型维度: gpt54nano 特指 gpt-5.4-nano, 由 config/sentiment.yaml::models 单一事实源定义, 经 yunwu 网关路由 (与 gemini31 同源, 与直连 api.deepseek.com 的 deepseekv4 异源), 是三家投票中的一家。轨道维度: ctx 轨输入 content_ctx = 标题 prepend + 含目标银行句的 ±窗口上下文片段, 相较 full 轨聚焦银行实体周边语境、削弱全文无关段落干扰。口径维度: 本列为等权口径 (无 hw / w 加权后缀), 逐篇取 gpt54nano_score_ctx ∈ {+1, 0, −1} 后仅在存活媒体子集 df_alive 上取算术均值。排除维度: df_alive 剔除的是 detect_defacto_cessation 判定的 ceased_set = confirmed ∪ suspected 覆盖退出媒体 (末次报道年份早于样本末年减 2、累计报道 ≥10 篇, 并与 NPPA 停办名录交叉验证; 未证实的疑似者亦保守全量剔除)。与全样本对偶列 gpt54nano 语调相比, 本列的唯一差别就是分母剔除了疑似退出媒体, 二者并置读出幸存者偏差对 ctx 轨语调水平的贡献。本列与同轨的跟风加权 hw_ctx、提及密度加权 w_ctx 两个非等权变体互为稳健性、不分主次, 三者仅在是否施加权重及权重方向上不同, 分母同为存活媒体子集。本列须解读为"疑似退出覆盖媒体"保守剔除口径的稳健性变体, 不可在论文中表述为严格停刊 (publication cessation) 口径。⚠ 铁律: 本列作为 ctx 单轨 × 等权口径的稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; gpt54nano 缺席仅掉自身族列。

## VAR: exc_gpt54nano_score_full

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 full 轨上等权签名语调票的 bank-year 均值, 是本家族在留篇门控口径下最贴近"主"测量的轨道。模型维度同 gpt54nano 家族: gpt-5.4-nano 经 yunwu 网关路由, 与 gemini31 同源、与直连的 deepseekv4 异源。轨道维度: full 轨输入 content_full = 标题 prepend + 全文正文, 是留篇门控 (2026-06-29 full-only 口径) 的判定基准轨——一篇报道是否被计为银行金科报道只看 full 轨的 llm_verified_full, 故 full 轨行宇宙即银行-年留篇集本身, ctx / ss 轨为其 conditional-on-full 的子集测度。口径维度: 等权口径, 逐篇 gpt54nano_score_full ∈ {+1, 0, −1} 在存活媒体子集上取算术均值。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (阈值 threshold_gap=2、累计报道 ≥10 篇, 交叉 NPPA 名录, 疑似者保守全剔)。本列与全样本对偶 full 轨语调仅在分母是否剔除退出媒体上不同, 系媒体来源消失稳健性的核心并排项; 对以 full 轨语调为处理变量的主回归 (如 P1 tone) 尤具证伪价值——若剔除退出媒体后系数方向与显著性稳定, 则可排除幸存者偏差驱动主结论的疑虑。本列亦须表述为疑似退出覆盖媒体的保守剔除口径, 不等同严格停刊口径。⚠ 铁律: 本列作为 full 单轨 × 等权口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; per-model 独立降级, gpt54nano 缺席不牵连另两家。

## VAR: exc_gpt54nano_score_hw_ctx

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ctx 轨上跟风加权 (HW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由。轨道维度: ctx 轨聚焦含目标银行句的 ±窗口上下文。加权维度: hw 后缀表示逐篇先以 gpt54nano_score_ctx × herd_weight_ctx 得到跟风加权文章列 (runner.py 步骤 3d), 再在存活媒体子集上取均值; herd_weight 来自 stage 24 herd_decay 处理器, 对同一事件被多家媒体扎堆转载的羊群式报道降权, 抑制信息重复计数, 权重严格取 ctx 轨自身构造值、不借 full 轨权。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (阈值 2 年、≥10 篇、交叉 NPPA、疑似保守全剔)。本列相较等权的 exc_gpt54nano_score_ctx, 差别在于每篇票已乘跟风权重, 因此它既剔除了覆盖退出媒体、又对转载扎堆降权, 是"样本选择稳健 × 转载去重"两重稳健性的叠加口径。相较全样本 hw 对偶列, 差别仍只在分母剔除退出媒体。跟风加权尤其呼应 Schwenkler & Zheng (2025) 新闻驱动同侪共动的证据: 媒体网络的转载结构若不降权, 会放大扎堆报道的语调。本列须解读为疑似退出覆盖媒体保守剔除口径下的跟风加权稳健性变体。⚠ 铁律: 本列作为 ctx 单轨 × hw 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; gpt54nano 缺席仅掉自身族列。

## VAR: exc_gpt54nano_score_hw_full

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 full 轨上跟风加权 (HW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由。轨道维度: full 轨 content_full = 标题 prepend + 全文正文, 是 full-only 留篇门控 (2026-06-29) 判定基准轨, 行宇宙即银行-年留篇集本身。加权维度: hw 表示逐篇 gpt54nano_score_full × herd_weight_full 得跟风加权文章列, 再在存活媒体子集取均值; herd_weight 来自 stage 24, full 轨权重独立构造。排除维度: 分母剔除 ceased_set (末次覆盖年份早于样本末年减 2、累计 ≥10 篇, 交叉 NPPA 停办名录, 疑似者保守全剔)。本列是 full 轨上"覆盖退出媒体剔除 × 跟风降权"的双重稳健口径: 既回应媒体来源消失引入的幸存者偏差 (Muhammad 2026 时间覆盖偏误), 又回应扎堆转载放大语调的问题。相较等权的 exc_gpt54nano_score_full, 本列每篇票已乘跟风权重; 相较全样本 hw 对偶列, 仅分母剔除退出媒体不同。对以 full 轨语调为主处理变量的回归而言, 本列可作为"同时控制样本选择与转载重复"的最保守语调稳健口径。仍须表述为疑似退出覆盖媒体保守剔除口径, 非严格停刊口径。⚠ 铁律: 本列作为 full 单轨 × hw 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; per-model 独立降级。

## VAR: exc_gpt54nano_score_hw_ss

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ss 轨上跟风加权 (HW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由。轨道维度: ss (same-sentence) 轨输入 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子 ±窗口片段, 是三轨中银行金科共现语义最严格者, 由 stage 14 ctx_materializer 物化 (stage 13 仅上游共现硬过滤、不物化文本列); 无同句共现时镜像 ctx 回退语义、退回全文 body 并置 ss_is_fallback=True。加权维度: hw 表示逐篇 gpt54nano_score_ss × herd_weight_ss 得跟风加权文章列, 再在存活媒体子集取均值, 正常情形下权重取 ss 轨自身跟风衰减值; 若 herd_weight_ss 因旧 schema 或 ss 轨未上线而缺列, runner 会退回借用 herd_weight_full 作降级权重, 此为 schema 缺失时的优雅降级分支, 非常规行为, 不影响生产期 herd_weight_ss 正常产出时"权重严格取 ss 轨自身构造值"的口径。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (阈值 2 年、≥10 篇、交叉 NPPA、疑似保守全剔)。本列在开发期 T=2 语料上因 ss 共现稀疏、大面积回退, 叠加覆盖退出剔除后有效样本可进一步收窄、数值可显著退化甚至近零方差, 属预期的语料退化而非缺陷; 生产期 T=19 全量语料上共现覆盖与媒体年份跨度均显著改善。相较等权 exc_gpt54nano_score_ss, 本列每篇票已乘跟风权重; 相较全样本 hw 对偶列, 仅分母剔除退出媒体。本列须解读为疑似退出覆盖媒体保守剔除口径下 ss 轨的跟风加权稳健性变体。⚠ 铁律: 本列作为 ss 单轨 × hw 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; gpt54nano 缺席仅掉自身族列。

## VAR: exc_gpt54nano_score_ss

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ss 轨上等权签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由 (与 gemini31 同源、与直连 api.deepseek.com 的 deepseekv4 异源)。轨道维度: ss 轨 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子 ±窗口片段, 是语义最严格的银行金科共现轨, 由 stage 14 ctx_materializer 物化; 无同句共现时镜像 ctx 回退语义、退回全文 body 并置 ss_is_fallback=True (与 full / ctx 共享 n_articles 分母)。口径维度: 等权口径 (无 hw / w 后缀), 逐篇 gpt54nano_score_ss ∈ {+1, 0, −1} 在存活媒体子集上取算术均值。排除维度: 分母剔除 detect_defacto_cessation 判定的 ceased_set 覆盖退出媒体 (末次年份早于样本末年减 2、累计 ≥10 篇, 交叉 NPPA 停办名录, 疑似者保守全剔)。本列与全样本对偶 ss 轨语调仅在分母是否剔除退出媒体上不同。因 ss 轨共现稀疏、叠加覆盖退出剔除后有效样本收窄, 开发期数值可退化甚至近零方差, 生产全量语料上共现覆盖与媒体年份跨度均显著改善。本列与同轨的跟风加权 hw_ss、提及密度加权 w_ss 两个非等权变体互为稳健性、不分主次: 三者仅在是否施加权重及权重方向 (等权 / 转载降权 / 提及密度升权) 上不同, 分母同为剔除覆盖退出媒体后的存活子集。本列须表述为疑似退出覆盖媒体保守剔除口径的 ss 轨等权稳健性变体, 不可作严格停刊口径解读, 亦不可与全样本 ss 轨语调混为同一测度。⚠ 铁律: 本列作为 ss 单轨 × 等权口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; per-model 独立降级, gpt54nano 缺席不牵连另两家。

## VAR: exc_gpt54nano_score_w_ctx

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ctx 轨上提及密度加权 (VW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由。轨道维度: ctx 轨聚焦含目标银行句的 ±窗口上下文。加权维度: w 后缀表示逐篇先以 gpt54nano_score_ctx × mention_density 得到提及密度加权文章列 (runner.py 步骤 3b), 再在存活媒体子集上取均值; mention_density 越高 (目标银行在文中被提及越密) 权重越大, 方法学同源于 Hassan et al. (2023) 以文本命中计数构造企业层面暴露度的提及加权思路。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (阈值 2 年、≥10 篇、交叉 NPPA、疑似保守全剔)。本列相较等权的 exc_gpt54nano_score_ctx, 差别在于每篇票已乘提及密度权重, 因此它既剔除覆盖退出媒体、又让高密度提及的报道对语调贡献更大, 是"样本选择稳健 × 提及密度加权"的叠加口径。与跟风加权 hw 变体正交: hw 对转载扎堆降权, w 按提及密度升权, 二者各自 just-identified 并排、互为稳健性。相较全样本 w 对偶列, 仅分母剔除退出媒体。本列须解读为疑似退出覆盖媒体保守剔除口径下的提及密度加权稳健性变体。⚠ 铁律: 本列作为 ctx 单轨 × w 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; gpt54nano 缺席仅掉自身族列。

## VAR: exc_gpt54nano_score_w_full

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 full 轨上提及密度加权 (VW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由。轨道维度: full 轨 content_full = 标题 prepend + 全文正文, 是 full-only 留篇门控 (2026-06-29) 判定基准轨, 行宇宙即银行-年留篇集本身。加权维度: w 表示逐篇 gpt54nano_score_full × mention_density 得提及密度加权文章列, 再在存活媒体子集取均值; mention_density 加权的经济学依据是提及越密的报道对该银行信息含量越高, 方法学同源于 Hassan et al. (2023) 的文本命中暴露度构造。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (末次年份早于样本末年减 2、累计 ≥10 篇, 交叉 NPPA 停办名录, 疑似者保守全剔)。本列是 full 轨上"覆盖退出媒体剔除 × 提及密度升权"的双重口径: 既回应媒体来源消失的幸存者偏差, 又让高信息含量报道主导语调。相较等权 exc_gpt54nano_score_full, 本列每篇票已乘提及密度权重; 相较跟风加权 hw_full 变体, 加权方向相反 (密度升权 vs 转载降权), 二者互为稳健性并排; 相较全样本 w 对偶列, 仅分母剔除退出媒体。本列须表述为疑似退出覆盖媒体保守剔除口径的提及密度加权稳健性变体, 非严格停刊口径。⚠ 铁律: 本列作为 full 单轨 × w 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; per-model 独立降级。

## VAR: exc_gpt54nano_score_w_ss

【变体差分】
本列 = 剔除疑似覆盖退出媒体后, GPT-5.4-nano 在 ss 轨上提及密度加权 (VW) 签名语调票的 bank-year 均值。模型维度: gpt-5.4-nano 经 yunwu 网关路由 (与 gemini31 同源、与直连 api.deepseek.com 的 deepseekv4 异源)。轨道维度: ss 轨 content_ss = 标题 prepend + 同句内同时含"目标银行 ∧ 金科词"的句子 ±窗口片段, 是语义最严格的银行金科共现轨, 由 stage 14 ctx_materializer 物化; 无同句共现时镜像 ctx 回退语义、退回全文 body 并置 ss_is_fallback=True。加权维度: w 表示逐篇 gpt54nano_score_ss × mention_density 得提及密度加权文章列, 再在存活媒体子集取均值; 提及密度加权方法学同源于 Hassan et al. (2023) 的文本命中暴露度构造。排除维度: 分母剔除 ceased_set 覆盖退出媒体 (阈值 2 年、≥10 篇、交叉 NPPA、疑似保守全剔)。本列在开发期 T=2 语料上因 ss 共现稀疏叠加覆盖退出剔除, 有效样本可进一步收窄、数值可退化, 属预期; 生产 T=19 全量语料上改善。相较等权 exc_gpt54nano_score_ss, 每篇票已乘提及密度权重; 相较跟风加权 hw_ss 变体加权方向相反, 二者互为稳健性并排; 相较全样本 w 对偶列, 仅分母剔除退出媒体。本列须解读为疑似退出覆盖媒体保守剔除口径下 ss 轨的提及密度加权稳健性变体。⚠ 铁律: 本列作为 ss 单轨 × w 口径稳健性并排项, 与另两轨、另两加权口径各自 just-identified 并排, 严禁混入同一 over-identified Hansen J; gpt54nano 缺席仅掉自身族列。

<!-- rendered-citations:begin -->
Muhammad, T. (2026). Temporal coverage bias in financial panel data: A coverage-aware structuring framework with evidence from the Dhaka Stock Exchange. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2603.20237
Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. Journal of Corporate Finance, 93, Article 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Färber, M., Schwade, J., & Jatowt, A. (2023). Measuring variety, balance, and disparity: An analysis of media coverage of the 2021 German federal election. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2308.03531
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
Khwaja, A. I., & Mian, A. (2008). Tracing the impact of bank liquidity shocks: Evidence from an emerging market. American Economic Review, 98(4), 1413-1442. https://doi.org/10.1257/aer.98.4.1413
<!-- rendered-citations:end -->
