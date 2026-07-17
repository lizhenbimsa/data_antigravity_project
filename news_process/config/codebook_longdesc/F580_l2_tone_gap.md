---
family_id: F580
columns:
- tone_gap_sub_symb
- tone_gap_sub_symb_sc_ctx
- tone_gap_sub_symb_ss_ss
- tone_gap_symb_sub_ctx
- tone_gap_symb_sub_full
- tone_gap_symb_sub_ss
- tone_gap_tech_app
- tone_gap_tech_app_lc_ctx
- tone_gap_tech_app_ls_ss
unit: 语调差值 (连续, 两个 bank-year 语调均值之差, 理论域约 [-2,2], 实务上多落在 [-1,1] 附近)
formula: 'sub/symb 族: tone_gap_sub_symb{诊断后缀} = mean(llm_vote_score, 实质性子样本) − mean(llm_vote_score, 象征性子样本), 需两侧 n≥5 才出值 (encode.py); tone_gap_symb_sub{track} = mean(llm_vote_score, 象征性子样本) − mean(llm_vote_score, 实质性子样本), 无 n≥5 门槛 (runner.py 洗稿率方法 C)。tech/app 族: tone_gap_tech_app{诊断后缀} = mean(llm_vote_score, 底层技术子样本) − mean(llm_vote_score, 应用场景子样本), 需两侧 n≥5 才出值。'
producer: pipeline\panel\encode.py::aggregate_panel (sub/symb 与 tech/app 的 gated 版本) ; pipeline\panel\runner.py (步骤 7h 洗稿率方法 C, tone_gap_symb_sub{track})
upstream: []
citations:
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: The Symbolic Management of Stockholders. Corporate Governance Reforms and Shareholder Reactions
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
- doi: 10.1287/orsc.2014.0949
  type: journal
  authors: Kim, E.-H., & Lyon, T. P.
  year: 2015
  title: 'Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure'
  venue: Organization Science
  vol: '26'
  issue: '3'
  pages_or_artno: 705-723
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing enthusiasm. Media sentiment and the disciplining role of quarterly earnings announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure Sentiment: Machine Learning vs. Dictionary Methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: 'Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures'
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: 'On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services'
  venue: Journal of Management Information Systems
  vol: '35'
  issue: '1'
  pages_or_artno: 220-265
- doi: 10.1002/csr.3172
  type: journal
  authors: Velte, P.
  year: 2025
  title: 'Corporate Social Responsibility (CSR) Decoupling and Tax Avoidance: Symbolic Use of Sustainable Boards in the European Union?'
  venue: Corporate Social Responsibility and Environmental Management
  vol: '32'
  issue: '3'
  pages_or_artno: 4179-4193
- doi: "10.1016/j.jbusres.2025.115188"
  title: "Talk, but don't talk too much: How corporate sustainability communication evokes stepwise organizational change"
  authors: "Reppmann, M., Maibaum, F., Edinger-Schons, L. M., & Foege, J. N."
  year: 2025
  venue: "Journal of Business Research"
  type: "journal"
  one_sentence_zh: "该文提出企业可持续性言辞(talk)与实际行动(walk)之间存在倒U型关系、言辞过量反而抑制言行一致的实证发现,为本家族实质性vs象征性报道语调缺口测度提供了2025年的最新方法论呼应。"
new_dois:
  - "10.1016/j.jbusres.2025.115188"
---

## CORE

【构念与来源】
F580 家族衡量的是"同一 bank-year 内, 银行金融科技相关报道按内容属性一分为二后, 两个子样本的 LLM 投票语调均值之差"——一种言行是否一致的脱耦 (decoupling) 测度。家族内实际混装了两组构念上有联系但计算细节不同的测度: 第一组围绕 innovation_substantiveness (实质性 vs 象征性) 分类, 第二组围绕 innovation_locus (底层技术 vs 应用场景) 分类。两组分类维度均来自 stage 21 三家 LLM 多数投票的分类结果 (SSOT 详见 encode.py 模块级 `_dim_col`/分类映射), 与情感三家共识 llm_vote_score 独立计算但共享同一批已过 full-only 留篇门控的文章。实质性 vs 象征性的分类思路直接对应组织理论中"言行不一致" (decoupling) 的经典构念: Westphal & Zajac (1994, Administrative Science Quarterly) 最早在 CEO 长期激励计划研究中区分"实质性采纳"与"象征性采纳", 后续 Westphal & Zajac (1998, ASQ) 将该框架用于公司治理改革的股东反应; 本仓库将其映射为"报道的是银行金融科技业务的实质性举措 (如落地系统、上线产品) 还是象征性举措 (如战略愿景、口号性表态)"。若市场/媒体对两类报道给予系统性不同的语调偏好, 则该缺口捕捉的正是"言行脱耦是否被媒体差异化定价"这一现象, 呼应企业可持续性披露领域"言过其实的漂绿"与"言行一致性脱耦"两类实证证据的经典界定 (Kim & Lyon, 2015, Organization Science; Velte, 2025, Corporate Social Responsibility and Environmental Management)。底层技术 vs 应用场景的划分则来自 Gomber, Kauffman, Parker, & Weber (2018) 对金融科技创新层级的经典界定, 对应 P4 (Gomber, locus) 主线的处理变量分组; tone_gap_tech_app 捕捉的是"媒体对底层技术突破报道的语调"与"对应用场景落地报道的语调"之间的系统性差异, 可用来间接检验媒体是否偏好炒作底层技术叙事而对应用场景落地更为克制 (或相反)。

两组测度均建立在同一批上游列之上: llm_vote_tone_sub{track}/llm_vote_tone_symb{track} 与 llm_vote_tone_tech{track}/llm_vote_tone_app{track}, 这些列本身是文章级 llm_vote_score{track} (三家 LLM 情感多数投票共识, ∈ {−1,0,1}) 按分类标签分组取 bank-year 均值的结果, 与家族 F580 本身不直接消费文章级列, 而是消费 encode.py aggregate_panel 内已完成的分组聚合中间产物。

【方法学与计算】
家族内两组"符号相反"的测度需要格外辨明, 否则极易读反方向: encode.py 内产出的 tone_gap_sub_symb 及其 ctx/ss 对角变体, 定义为"实质性均值 − 象征性均值" (sub − symb), 且强制 min(n_sub, n_symb) ≥ 5 的最小篇数门槛 —— 若某 bank-year 的实质性或象征性子样本文章不足 5 篇, 则该格记为缺失而非用噪声均值参与差分, 这是为防止 compositional confound (某类别只有 1-2 篇驱动出极端伪差距, 混进 Table 3 机制回归会造成虚假显著)。tone_gap_tech_app 及其 ctx/ss 对角变体走同一套 min-n≥5 守门逻辑, 定义为"底层技术均值 − 应用场景均值" (tech − app)。与此相对, runner.py 步骤 7h "洗稿率 (Washing Ratio)" 模块方法 C 产出的 tone_gap_symb_sub{track} (含 full/ctx/ss 三轨), 定义方向刻意相反 —— "象征性均值 − 实质性均值" (symb − sub) —— 且不带 min-n≥5 门槛, 只要求 llm_vote_tone_sub{track} 与 llm_vote_tone_symb{track} 两列同时存在于面板即计算。这一方向反转并非笔误: 洗稿率 (washing ratio) 方法族的叙事视角是"象征性报道相对实质性报道语调虚高多少" (即 symb − sub > 0 意味着报道口径存在'洗稿'倾向, 媒体/机构对无实质内容的表态给予更正面的语调), 与 encode.py 视角"实质性报道语调是否优于象征性报道" (sub − symb > 0 意味着言行一致的报道更受正面评价) 互为镜像但用于不同下游叙事, 使用者引用时须核对符号方向与是否经过 min-n≥5 稀疏格过滤, 不可混用或直接相减对冲。

三轨 (full/ctx/ss) 铁律适用于全部含轨道后缀的列: full=标题+正文全文, ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗口 (缺同句共现回退全文并标记 fallback, 语义镜像 ctx 回退)。三轨口径各自独立成立、互为稳健性而不分主次, 在识别策略上各自 just-identified 并排, 严禁混入同一 over-identified 的 Hansen J 检验框架。留篇门控为 full-only (2026-06-29 起生效): 一篇文章是否计入"银行金科报道"的样本论域, 只看 llm_verified_full 是否为真; ctx/ss 轨道的分组均值是在该 full-only 留篇集合的子集上, 按各自轨道的分类标签与情感列重新计算, 属于 conditional-on-full 的测度/稳健性轨, 而非独立样本论域。ss 轨若某文章不满足银行与金科同句共现, 则 content_ss 回退为全文正文且 ss_is_fallback 记为真, 该文章仍参与 ss 轨的实质性/象征性或底层技术/应用场景分类与均值计算, 只是所用文本退化为全文, 与 ctx 轨的回退处理逻辑完全对称。

【文献定位】
本家族的方法学谱系可分三条线: 其一是言行脱耦/象征管理 (symbolic management) 传统, 源自 Westphal & Zajac (1994, 1998, Administrative Science Quarterly) 对"采纳了制度但未真正执行"现象的开创性刻画, 在企业可持续性/ESG 披露文献中进一步细化为"漂绿 (greenwash) 与漂棕 (brownwash) 两类脱耦方向"的经典区分 (Kim & Lyon, 2015, Organization Science) 以及"象征性治理工具是否被用来掩护实质性回避行为"的检验设计 (Velte, 2025, Corporate Social Responsibility and Environmental Management)。其二是媒体语调分组比较的方法学基础, 承袭 Holzman, Miller, & Twedt (2023, The Accounting Review) 用媒体情感约束盈余公告披露纪律的分组均值设计思路, 以及 Frankel, Jennings, & Lee (2022, Management Science) 对机器学习与词典法情感测度互为稳健性的方法论立场 (本仓库三家 LLM 多数投票即践行该立场的中文金融语境延伸)。其三是洗稿率 (washing ratio) 方法族本身的漂绿/漂科技类比, 借鉴 climate-washing 文献对"廉价言辞 (cheap talk)"与实际行动脱节的量化范式 (Bingler, Kraus, Leippold, & Webersinke, 2022, Finance Research Letters; 2024, Journal of Banking & Finance), 将其原本用于气候披露的"言辞 vs 实质"对比结构移植到银行金融科技报道语境, 用媒体语调而非披露文本内容作为言辞代理变量。三条线交汇于同一个基本诊断问题: 当报道内容可分为"做了什么"(实质性/底层技术) 与"说了什么"(象征性/应用场景) 两类时, 语调本身是否也系统性地偏向某一类, 若是, 则该偏向本身构成一种可测度的"叙事脱耦"信号, 可作为 P1 tone 主线与 P4 locus 主线的机制/稳健性补充证据, 而非独立主假设检验对象。Reppmann, Maibaum, Edinger-Schons, & Foege (2025, Journal of Business Research) 提出企业可持续性言辞(talk)与实际行动(walk)之间存在倒U型关系、言辞过量反而抑制言行一致的实证发现,为本家族实质性vs象征性报道语调缺口测度提供了2025年的最新方法论呼应。

## VAR: tone_gap_sub_symb

【变体差分】
本列是 sub/symb 族的 full 轨 canonical 版本, 由 encode.py aggregate_panel 在按 innovation_substantiveness_full 分组聚合之后直接计算, 定义为 llm_vote_tone_sub_full − llm_vote_tone_symb_full, 即"实质性子样本 LLM 语调均值"减去"象征性子样本 LLM 语调均值"。计算前置条件是 min(n_articles_sub, n_articles_symb) ≥ 5, 两个计数均取自该 bank-year 下按 innovation_substantiveness_full 标签过滤后、llm_vote_score_full 非缺失的文章计数; 若任一子样本篇数不足 5 篇, 本列记为 NaN 而非输出基于极小样本的噪声差值, 这一守门逻辑 (fix encode-02, 对齐 _compute_tone_gap_tech_app 的 R8 防混杂设计) 专门用于防止某个分类格只有一两篇文章便驱动出极端伪差距、进而污染 Table 3 一类的机制回归。正值表示该 bank-year 内, 关于银行金融科技的实质性报道语调显著优于象征性报道语调, 可解读为"媒体对真正落地的举措给予更正面评价, 对停留在口号/愿景层面的表态相对克制"; 负值则相反, 象征性报道反而获得更正面语调, 可能提示存在漂绿式的叙事包装。本列的样本论域已受 full-only 留篇门控约束 (只统计 llm_verified_full 为真的文章), 与家族内其余 ctx/ss 对角变体、以及符号相反的 tone_gap_symb_sub_full 严格区分: 后者虽然同样以 full 轨为计算基础, 但符号方向相反且不带 min-n≥5 门槛, 两者不可互相替代或相加抵消, 引用时必须明确指出所引的是哪一个产出者、哪一种符号约定。日志层面本列附带 bank-year 满足门槛的格数占比、均值、标准差、中位数等诊断统计, 便于核实"是否存在足够多满足最小篇数的观测格"这一小样本担忧 (T=2 开发集下常见"无满足格"的预期退化, 不代表代码缺陷)。

## VAR: tone_gap_sub_symb_sc_ctx

【变体差分】
本列是 sub/symb 族在 ctx 轨的对角线版本, 由 encode.py 内 `_aggregate_ctx_diagonal` 辅助函数按 innovation_substantiveness_ctx (而非 full 轨分类标签) 分组、聚合 llm_vote_score_ctx (而非 full 轨情感列) 后得到, 定义为 llm_vote_tone_sub_sc_ctx − llm_vote_tone_symb_sc_ctx。"对角线"含义是: 分类标签与情感均值均取自 ctx 轨, 二者轨道严格一致 (不像家族外某些"legacy"跨轨列那样分类用一轨、情感用另一轨), 这也是列名中 `_sc` (substantiveness-ctx 简写) 与 `_ctx` 双重后缀共存的原因。分母同域化: sub_frac_sc/symb_frac_sc 的分母统一使用 n_articles_llm_valid_ctx (ctx 轨下 LLM 分类与情感均有效的文章计数), 而非误用 full 轨分母, 避免出现 frac > 1 的轨道不对称错误 (2026-06 修复记录 fix omni-g-encode-05)。min-n≥5 守门逻辑与 canonical 版本完全一致: 需 n_articles_sub_sc_ctx 与 n_articles_symb_sc_ctx 均 ≥5 才出值, 否则记 NaN。ctx 轨的文本论域是"标题+实体窗口"而非全文, 因此本列捕捉的是"聚焦银行主体邻近语境时, 实质性与象征性报道的语调缺口"是否与全文视角下的 tone_gap_sub_symb 一致, 二者互为稳健性并排比较, 不设主次、禁止混入同一 over-identified 检验设计。样本论域仍受 full-only 留篇门控约束 (行宇宙是 llm_verified_full 为真的文章子集), ctx 轨分类与情感值只是在该子集上按 ctx 轨文本重新计算的条件测度, 不构成独立样本扩张。本列与另一个符号相反、无守门条件的 tone_gap_symb_sub_ctx 属于家族内的镜像对子, 二者虽同为 ctx 轨、同源于 llm_vote_tone_sub_ctx/llm_vote_tone_symb_ctx 两列, 但一个用于 Table 3 一类的严谨机制回归 (本列), 另一个用于洗稿率方法 C 的三轨并排诊断, 使用前须先核对符号方向再决定采用哪一版本, 不应在同一张回归表内混用而不加注明。



## VAR: tone_gap_sub_symb_ss_ss

【变体差分】
本列是 sub/symb 族在 ss 轨 (银行∧金科同句共现窗口) 的对角线版本, 镜像 tone_gap_sub_symb_sc_ctx 的构造逻辑, 由 `_aggregate_ctx_diagonal` 按 innovation_substantiveness_ss 分组、聚合 llm_vote_score_ss 后得到, 定义为 llm_vote_tone_sub_ss_ss − llm_vote_tone_symb_ss_ss, 同样要求两侧计数 ≥5 方出值, 否则记 NaN。列名中 `_ss_ss` 双重后缀分别对应"substantiveness-ss 分类标签轨道简写"与"ss 情感轨道", 与 ctx 版本的 `_sc_ctx` 命名规则一一对应, 而非重复书写的笔误。分母同域化同理: sub_frac_ss/symb_frac_ss 分母使用 n_articles_llm_valid_ss。ss 轨的文本论域是"标题+银行与金科关键词同句±N窗" (config/filtering.yaml::context_window.ss_sentence_radius, 默认 1 句), 若某文章不存在此类同句共现, content_ss 按约定回退为全文正文并置 ss_is_fallback=True, 该文章仍正常参与本列的分类分组与均值计算, 只是所用文本材料退化为全文, 这一回退语义与 ctx 轨完全对称、共享同一份 n_articles 分母口径。本列与 tone_gap_sub_symb (full)、tone_gap_sub_symb_sc_ctx (ctx) 三者共同构成 sub/symb 族的三轨并排稳健性梯子, 三者各自 just-identified、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 检验; T=2 开发集样本量下三轨可能同时出现"无满足 min-n≥5 格"的退化结果, 属预期现象, 生产 T=19 语料下应能观察到更多合格格。本列同样存在符号相反、无守门条件的镜像列 tone_gap_symb_sub_ss (洗稿率方法 C 的 ss 轨产出), 二者共享同一批上游 llm_vote_tone_sub_ss/llm_vote_tone_symb_ss 列, 但本列面向"实质性报道语调是否优于象征性报道"的严谨判定, 后者面向"象征性报道是否存在洗稿式语调虚高"的宽松诊断, 两条并行叙事不可相加或相消, 引用前须核对是哪一产出者、是否经过篇数守门。

## VAR: tone_gap_symb_sub_ctx

【变体差分】
本列属于洗稿率 (washing ratio) 方法族的方法 C ("情感纯度缺口")在 ctx 轨的产出, 由 runner.py 步骤 7h 的三轨循环 (`for track in ['_full', '_ctx', '_ss']`) 在 track='_ctx' 时计算得到, 定义为 llm_vote_tone_symb_ctx − llm_vote_tone_sub_ctx, 即"象征性子样本语调均值"减去"实质性子样本语调均值" —— 符号方向与家族内 tone_gap_sub_symb_sc_ctx 严格相反 (后者是 sub − symb 且带 min-n≥5 守门, 本列是 symb − sub 且不带该守门)。计算条件仅要求 llm_vote_tone_sub_ctx 与 llm_vote_tone_symb_ctx 两列同时存在于面板 (存在性守卫 `if ... in panel.columns`), 不额外要求任一子样本满足最小篇数, 因此在稀疏格上比 encode.py 侧的 gated 版本更容易出值, 但也更容易被极小样本的噪声均值驱动, 使用者在解读显著性时需格外留意样本量。本列服务于"洗稿率"叙事: 正值 (symb − sub > 0) 表示象征性/口号性报道反而获得更正面的语调, 可类比气候披露文献中的 cheap-talk/漂绿现象 (Bingler et al., 2022, Finance Research Letters; 2024, Journal of Banking & Finance) 在银行金融科技报道语境下的映射, 用作 washing_ratio 系列指标 (方法 A/A2/B/D) 的并排补充诊断, 而非独立处理变量。ctx 轨文本论域为标题+实体窗口, 与 full/ss 轨互为稳健性并排, 样本论域同样受 full-only 留篇门控约束。本列在 wr_variants 诊断字典中标注为方法 C 的 ctx 轨条目, 与 washing_ratio_ctx (方法 A)、neg_sub_ratio_ctx (方法 B)、washing_ratio_dict_ctx (方法 D) 等同轨其余洗稿率指标并列出现在同一份 bank-year 面板行内, 共同构成"洗稿率"多方法交叉验证矩阵的一部分, 而非单独回归的处理变量; 与家族内 encode.py 侧的 tone_gap_sub_symb_sc_ctx (符号相反、带 min-n≥5 守门) 是同一构念的两种不同稳健性取舍, 不应混淆使用场景。

## VAR: tone_gap_symb_sub_full

【变体差分】
本列是洗稿率方法 C 在 full 轨 (track='_full', 变量名后缀为空字符串规则不适用于 tone_gap_symb_sub —— 该列固定拼接 track 原始值, 因此 full 轨列名是 tone_gap_symb_sub_full 而非无后缀裸名) 的产出, 定义为 llm_vote_tone_symb_full − llm_vote_tone_sub_full, 计算仅要求两列存在于面板即执行, 无 min-n≥5 守门。本列与 encode.py 侧 canonical 版本 tone_gap_sub_symb (同样基于 full 轨的 llm_vote_tone_sub_full/llm_vote_tone_symb_full) 计算量互为负数的近似关系 (数值上 tone_gap_symb_sub_full ≈ −tone_gap_sub_symb, 但因守门条件不同, 二者在 NaN 分布上并不完全对称 —— tone_gap_sub_symb 在稀疏格记 NaN 的位置, tone_gap_symb_sub_full 仍可能有值), 这是家族内最容易被误用的一对列: 若研究者需要"言行一致性溢价"的严谨版本 (防小样本噪声), 应使用 tone_gap_sub_symb; 若需要与洗稿率方法 A/A2/B/D 并排的"洗稿倾向"诊断族, 应使用本列, 两者不应在同一张回归表内不加说明地互换或相加。full 轨样本论域即为 full-only 留篇门控本身定义的行宇宙, 不存在条件缩窄问题。本列在 wr_variants 诊断字典中标注为方法 C 的 full 轨条目 (无后缀规则在此不适用, 变量名固定携带 `_full`), 与洗稿率其余方法在同一 bank-year 面板行内并列输出, 是"言辞是否虚高"这一叙事下最基础、样本量最大的一轨版本, 也是研究者最先应查看的一轨, 其余 ctx/ss 版本用于检验该洗稿倾向是否在聚焦银行主体语境或严格同句共现语境下依然成立。



## VAR: tone_gap_symb_sub_ss

【变体差分】
本列是洗稿率方法 C 在 ss 轨 (银行∧金科同句共现窗口, track='_ss') 的产出, 定义为 llm_vote_tone_symb_ss − llm_vote_tone_sub_ss, 计算条件与 ctx/full 姊妹列一致, 仅要求两个源列存在、不设 min-n≥5 守门。ss 轨文本论域为标题+银行与金科关键词同句±N窗, 缺同句共现时 content_ss 回退为全文并置 ss_is_fallback=True, 该回退语义与 ctx 轨镜像对称, 回退文章仍正常参与本列所依赖的 llm_vote_tone_sub_ss/llm_vote_tone_symb_ss 分组均值计算。本列与家族内 encode.py 侧的 gated 对角列 tone_gap_sub_symb_ss_ss 构成同一逻辑对子中的 ss 轨版本: 前者 (本列) 无篇数守门、符号为 symb − sub, 用于洗稿率方法 C 的三轨并排诊断; 后者带 min-n≥5 守门、符号为 sub − symb, 用于 Table 3 一类机制回归的严谨版本。full/ctx/ss 三轨在洗稿率方法 C 内部各自 just-identified 并排、互为稳健性不分主次, 禁止混入同一 over-identified Hansen J 检验; 样本论域受 full-only 留篇门控约束, ss 轨只是在该子集上按 ss 轨材料重新计算的条件测度。本列是三轨梯子中样本量通常最小的一轨 (ss 轨的行宇宙受同句共现回退比例影响), 若某 bank-year 的银行∧金科同句共现文章本就稀少, 则本列虽无 min-n≥5 硬性门槛, 实践上仍可能因为 llm_vote_tone_sub_ss/llm_vote_tone_symb_ss 本身基于极少数文章而带有较大噪声, 解读时建议同时参考对应的 n_articles_sub_ss_ss/n_articles_symb_ss_ss 计数列。

## VAR: tone_gap_tech_app

【变体差分】
本列是 tech/app 族的 full 轨 canonical 版本, 定义为 llm_vote_tone_tech_full − llm_vote_tone_app_full, 即"底层技术子样本语调均值"减去"应用场景子样本语调均值", 由 encode.py 内 `_compute_tone_gap_tech_app` 辅助函数实现, 显式文档标注其设计"反向借鉴 tone_gap_sub_symb 块"并复用同一套 min(n_tech, n_app) ≥ 5 最小篇数防御逻辑 (R8 audit 混杂防御): 若某 bank-year 下底层技术或应用场景任一子样本文章不足 5 篇, 本列记为 NaN。分类标签来自 innovation_locus_full (P4 主线 Gomber locus 维度的 LLM 三家投票共识分类), 与 sub/symb 族使用的 innovation_substantiveness_full 是两个独立、正交的分类维度, 二者不可混淆或加总。正值表示媒体对底层技术突破类报道 (如核心系统研发、算法能力) 给予比应用场景落地类报道 (如具体产品上线、渠道拓展) 更正面的语调, 可用于间接检验媒体是否存在"技术叙事偏好"或反之偏好务实落地叙事; 该缺口是 P4 locus 主线的机制/稳健性补充证据而非该论文的核心处理变量本身 (P4 核心处理变量另有 citation_weighted_patent 等结果侧变量与 locus 维度自身的 tech_frac/app_frac 处理变量)。样本论域受 full-only 留篇门控约束。本列与 sub/symb 族的 tone_gap_sub_symb 在计算范式上完全对称 (同一 min-n≥5 守门函数族、同一 encode.py 归属), 但分类维度正交、不共享分子分母, 二者不应相加或直接对比数值大小, 只能各自作为其所属主线 (P1 tone/P4 locus) 的机制补充证据独立解读; 日志同样输出满足门槛的格数占比、均值、标准差、中位数, 便于核实门槛条件是否被满足。

## VAR: tone_gap_tech_app_lc_ctx

【变体差分】
本列是 tech/app 族在 ctx 轨的对角线版本, 由 `_aggregate_ctx_diagonal` 按 innovation_locus_ctx 分组、聚合 llm_vote_score_ctx 后得到, 定义为 llm_vote_tone_tech_lc_ctx − llm_vote_tone_app_lc_ctx, 计算前提同样是 min(n_articles_tech_lc_ctx, n_articles_app_lc_ctx) ≥ 5, 否则记 NaN (`_both` 掩码, 代码位置紧邻 tech_frac_lc/app_frac_lc 的 ctx 分母同域化计算之后)。列名中 `_lc` 是"locus-ctx 分类标签轨道简写", 与 `_ctx` 情感轨道后缀共同构成"对角线"命名规则 (分类与情感取自同一轨), 与 sub/symb 族 `_sc_ctx` 的命名逻辑完全平行。tech_frac_lc/app_frac_lc 分母同域化使用 n_articles_llm_valid_ctx, 避免轨道不对称导致 frac > 1。本列捕捉的是"聚焦银行主体邻近语境时, 底层技术与应用场景报道的语调缺口"是否与全文视角下的 tone_gap_tech_app 一致, 二者互为稳健性并排、不分主次, 禁止混入同一 over-identified Hansen J 检验。样本论域受 full-only 留篇门控约束, ctx 轨为该子集上的条件测度而非独立样本扩张。与 sub/symb 族的 ctx 对角列不同, tech/app 族目前未在 runner.py 洗稿率模块内设有符号相反的镜像版本 (locus 维度不参与洗稿率方法 C), 因此本列没有需要甄别符号方向的姊妹列, 使用者只需关注其与 full/ss 轨版本之间的稳健性一致性即可, 无需担心与洗稿率族混淆。本列同样附带日志诊断, 报告满足 min-n≥5 门槛的 bank-year 格数占比、均值与标准差, 便于在小样本开发环境下快速判断本列是否已具备可解释的取值分布, 而非盲目信任面板列存在即代表有意义的观测。

## VAR: tone_gap_tech_app_ls_ss

【变体差分】
本列是 tech/app 族在 ss 轨的对角线版本, 镜像 tone_gap_tech_app_lc_ctx 的构造逻辑 (代码注释明确标注"镜像 _lc × _ctx 块"), 由 `_aggregate_ctx_diagonal` 按 innovation_locus_ss 分组、聚合 llm_vote_score_ss 后得到, 定义为 llm_vote_tone_tech_ls_ss − llm_vote_tone_app_ls_ss, 同样要求 min(n_articles_tech_ls_ss, n_articles_app_ls_ss) ≥ 5 方出值。列名中 `_ls` 对应"locus-ss 分类标签轨道简写", 与 `_ss` 情感轨道后缀共同构成对角线命名, 与 ctx 版本的 `_lc_ctx` 一一对应。tech_frac_ls/app_frac_ls 分母使用 n_articles_llm_valid_ss 同域化。ss 轨文本论域为标题+银行∧金科同句窗口, 缺同句共现回退全文并置 ss_is_fallback=True, 回退文章仍参与本列分组计算, 语义与 ctx 轨对称。本列与 tone_gap_tech_app (full)、tone_gap_tech_app_lc_ctx (ctx) 共同构成 tech/app 族的三轨并排稳健性梯子, 三者各自 just-identified、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 检验; 与 tech/app 分类维度正交的 sub/symb 族三轨梯子 (F580 家族另外六列) 及洗稿率方法 C 的符号相反版本均不可与本列直接比较或相加。ss 轨的行宇宙同样受同句共现回退比例影响, 若某 bank-year 银行∧金科同句共现文章稀少, 底层技术/应用场景分类计数亦随之稀疏, min-n≥5 守门在此更容易触发 NaN, T=2 开发集下本列大概率呈现全空或近全空的预期退化, 不构成代码缺陷, 生产 T=19 语料应能观察到更充分的合格格比例。列名中的 `_ls_ss` 双后缀刻意保留两段简写以便与 `_lc_ctx` 版本形成机械对照, 阅读时应将其拆解为"locus 分类标签轨道"与"情感/文本轨道"两段, 而非误读为某种更长的独立缩写词。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders. Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Kim, E.-H., & Lyon, T. P. (2015). Greenwash vs. Brownwash: Exaggeration and Undue Modesty in Corporate Sustainability Disclosure. Organization Science, 26(3), 705-723. https://doi.org/10.1287/orsc.2014.0949
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm. Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the Fintech Revolution: Interpreting the Forces of Innovation, Disruption, and Transformation in Financial Services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Velte, P. (2025). Corporate Social Responsibility (CSR) Decoupling and Tax Avoidance: Symbolic Use of Sustainable Boards in the European Union? Corporate Social Responsibility and Environmental Management, 32(3), 4179-4193. https://doi.org/10.1002/csr.3172
Reppmann, M., Maibaum, F., Edinger-Schons, L. M., & Foege, J. N. (2025). Talk, but don't talk too much: How corporate sustainability communication evokes stepwise organizational change. Journal of Business Research. https://doi.org/10.1016/j.jbusres.2025.115188
<!-- rendered-citations:end -->
