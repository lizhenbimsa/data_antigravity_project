---
family_id: F273
columns:
- exc_tone_ctx
- exc_tone_full
- exc_tone_ss
unit: 语调得分 (连续, 约 [-1,1]; bank-year 级, 剔除疑似退出银行-fintech 话题覆盖媒体后 llm_vote_score 的算术均值; 非严格停刊口径, 见下)
formula: "exc_tone{track} = mean_over_articles( llm_vote_score{track} | _is_ceased_media == 0 ), 按 (target_bank, year) 分组; track ∈ {_full, _ctx, _ss}; _is_ceased_media 由 detect_defacto_cessation 的 ceased_all = confirmed ∪ suspected 判定"
producer: news_process/pipeline/panel/attention_media.py (detect_defacto_cessation, 话题覆盖退出稳健性块 C.3) ; news_process/pipeline/panel/export.py (Stata 标签)
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss)
- 40_panel_yearly (target_bank, year, _is_ceased_media)
citations:
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: "Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements"
  venue: The Accounting Review
  vol: 98
  issue: 7
  pages_or_artno: 315-345
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: "Who captures the power of the pen?"
  venue: Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1017/s0022109025101749"
  title: "When Spotlights Fade: Local Newspaper Closures and Financial Advisor Misconduct"
  authors: "Li, Z., Peng, Q., & Zhang, R.-Z."
  year: 2025
  venue: "Journal of Financial and Quantitative Analysis"
  type: "journal"
- doi: "10.1111/1911-3846.13046"
  title: "Local newspaper closures and bank loan contracts"
  authors: "Ma, Z., Stice, D., Stice, H., & Zhang, Y."
  year: 2025
  venue: "Contemporary Accounting Research"
  type: "journal"
new_dois:
  - "10.1017/s0022109025101749"
  - "10.1111/1911-3846.13046"
---

## CORE

【构念与来源】
本家族三列 exc_tone_full / exc_tone_ctx / exc_tone_ss 是「疑似退出银行-fintech 话题覆盖媒体稳健性」情感测度: 在 bank-year 级把语料按篇聚合为语调均值时, 剔除掉被判定为 _is_ceased_media == 1 的媒体来源所发的报道, 只对未被判定退出的媒体 (_is_ceased_media == 0) 计算目标银行当年被报道的整体语调。这里必须先做一处关键的构念澄清, 直接来自产出该列的源码 detect_defacto_cessation 函数体的显式措辞修正: 传入的数据本就是银行-fintech 文章子集, first_year/last_year 度量的是某媒体来源在这一话题上的最后一次出现年份, 由此推断的是该媒体退出银行-fintech 话题覆盖 (topic coverage exit) 这一代理事件, 而不是经证实的报纸停刊 (publication cessation) —— 一家媒体完全可能仍在正常出版, 只是不再报道银行与金融科技相关的话题, 这种情况下同样会被本判据标记为 _is_ceased_media == 1。因此 exc_tone 家族的构念动机应表述为: 一部分媒体来源在样本期内退出了「对目标行业话题的持续覆盖」(可能因停刊, 也可能只是编辑方向转移、栏目撤并、记者流失等与停刊无关的原因), 若这些来源在退出覆盖前系统性地偏向某种语调, 则包含它们的整体语调均值可能被「话题覆盖构成随时间变化」这一非构念因素污染, 从而使语调与银行结果之间的关系产生虚假的时间趋势。剔除疑似退出覆盖媒体后重算的语调, 与保留全部媒体的主测度并排比较, 用来检验主结论是否被这一话题覆盖构成变动所驱动 —— 这是一条保守的、以话题覆盖退出为停刊的代理 (proxy) 稳健性臂, 不应被解读为「已确证停刊媒体剔除」。这一思路仍延续媒体作为信息中介的经典识别关切: Fang 与 Peress (2009) 证明媒体报道覆盖度本身进入股票横截面定价, You 等 (2018) 揭示中国制度环境下「谁掌握笔杆」会系统性塑造报道语调, 二者都提示报道来源的构成 (而非仅报道内容) 是一个需要单独处理的混淆维度, 本家族把这一维度显式操纵为剔除臂。

【方法学与计算】
计算链路完全承接主语调轨: 上游 stage 21 (tone_llms) 已对每篇报道产出三家大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 多数投票共识得到的篇级语调 llm_vote_score{track}, 数值域约 [-1, 1], 负面为负、正面为正。_is_ceased_media 的判定发生在 attention_media.py::detect_defacto_cessation: 先在银行-fintech 文章子集上按媒体来源计算 first_year/last_year/n_articles, 把 last_year 早于「样本最大年份 − threshold_gap (默认 2)」且历史报道量 ≥10 篇的来源标记为 data_ceased (数据驱动的话题覆盖退出候选); 再用 NPPA (国家新闻出版署) 报刊名录做交叉验证, 得到 confirmed = data_ceased ∩ nppa_ceased (数据信号与 NPPA 登记的注销/停办/休刊状态双重吻合) 与 suspected = data_ceased − nppa_ceased (只有数据信号、未在 NPPA 名录里找到对应停办登记)。最终进入排除集的 ceased_all = confirmed ∪ suspected —— 必须明确披露的一点是, NPPA 交叉验证只改变报告 (cessation_report) 里的分类标签, 并不收窄排除集本身: 未经 NPPA 证实的 suspected 部分照样全量计入 ceased_all, 也就照样把对应媒体的报道剔出 exc_tone 的分子分母。因此 _is_ceased_media == 1 里既包含「NPPA 登记证实确已停办」的来源, 也包含「仅因话题覆盖退出信号被保守判定、未经外部登记证实」的来源, 后者可能只是不再报道银行金科话题而并未停刊。本家族在 attention_media.py 的话题覆盖退出稳健性块 (C.3) 中, 先用 df_alive = df[df['_is_ceased_media'] == 0] 过滤掉被判定退出的媒体的行, 再对每条轨道 (_full / _ctx / _ss) 按 (target_bank, year) 分组取 llm_vote_score{track} 的算术均值, 落为 exc_tone{track} 列, 左连接回主面板。三轨的源列若在存续子集里缺失 (例如某轨未产出), 有 if src in df_alive.columns 守卫优雅跳过, 不会连坐其余两轨。需要强调聚合口径与零填契约的边界: 兄弟列 n_articles_exc (排除疑似退出覆盖媒体后的文章计数) 属计数类, 遵循「Σ over ∅ = 0」契约, 零文章的 bank-year 补 0 并恢复整型; 而 exc_tone{track} 属情感均值类, 空集上的均值无定义, 按契约保持 NaN 而不零填 —— 二者填充语义刻意不同, 混淆会使「无报道」与「中性报道」不可区分。留篇门控与主口径一致 (2026-06-29 full-only): 一篇报道是否计入「银行金科报道」宇宙只看 full 轨的 llm_verified_full, ctx/ss 是 conditional-on-full 的子集轨, 因此三条 exc_tone 轨的行宇宙同源, 差异只在文本窗口。

【文献定位】
本测度落在「媒体语调 → 银行 (存款人/资本市场) 反应」这条实证链上, 但其独特贡献是把「媒体来源构成」作为一个可操纵的稳健性维度显式暴露出来。Tetlock (2007) 奠定了媒体语调进入投资者情绪并预测市场走势的范式, Shapiro 等 (2022) 从计量角度系统化了新闻情感指数的构造与验证, Holzman 等 (2023) 进一步指出媒体情感的定价作用会被硬信息 (季度盈余公告) 的到来所约束 —— 这些工作共同说明语调测度对「哪些媒体、在什么约束下发声」高度敏感。在中国银行业情境下, Fang 等 (2024) 直接把媒体情感与存款稳定性、银行系统性风险相连, 与本项目的银行-年面板对象同域, 为「剔除疑似退出话题覆盖媒体后语调是否仍稳健地关联银行结果」提供了直接的构念对照。综合看, exc_tone 家族不是一个新构念, 而是主语调 (llm_vote_tone) 的一条媒体样本稳健性臂: 它与主测度互为稳健性、不分主次, 各自 just-identified 并排使用, 严禁把「含全部媒体」与「排除疑似退出话题覆盖媒体」两个版本混进同一个 over-identified Hansen J 过度识别式 —— 二者高度共线, 混入只会人为制造识别假象, 正确用法是并排报告系数稳定性。Li, Peng, & Zhang (2025, Journal of Financial and Quantitative Analysis) 利用约95万名理财顾问的个体记录发现, 当地报纸停刊后所在县域理财顾问违规概率与严重程度显著上升, 证实媒体监督退出会削弱金融不当行为的外部约束, 为本家族「疑似退出话题覆盖媒体」稳健性剔除臂提供了媒体退出即监督缺位的直接实证支持。Ma, Stice, Stice, & Zhang (2025, Contemporary Accounting Research) 研究发现当地报纸停刊后借款人贷款利差上升、契约条款收紧, 银行作为报道读者失去低成本信息中介后被迫加强其他监督渠道, 揭示媒体来源退出对银行-借款人信息环境的系统性冲击, 呼应本家族把媒体覆盖构成变动显式作为稳健性操纵维度的构念动机。再次强调: exc_* 系列的排除口径是「疑似退出银行-fintech 话题覆盖媒体」的保守代理, 而非经证实的报纸停刊 (publication cessation), 论文行文中应避免使用「停刊媒体」这一确证性措辞, 应表述为「疑似退出话题覆盖的媒体」或「话题覆盖退出代理」。

## VAR: exc_tone_full

【变体差分】
本列是 full 轨的疑似退出话题覆盖媒体稳健性语调: 文本窗口取「标题 prepend + 全文正文」的完整报道 (content_full), 篇级来源为 llm_vote_score_full, 在未被判定退出银行-fintech 话题覆盖的媒体子集 (_is_ceased_media == 0) 上按 (target_bank, year) 求均值。相对家族内另两轨, full 轨是留篇门控的 canonical 判定轨 (full-only, 2026-06-29): 一篇报道是否属于「银行金科报道」宇宙只由 llm_verified_full 决定, 因此 exc_tone_full 的行宇宙即 full 留篇集 (再叠加存续媒体过滤), ctx/ss 两轨则是它的 conditional-on-full 子集测度。相对家族外的主语调 exc 之外版本, 本列的差分维度只有一个: 分子分母都只纳入未被判定退出话题覆盖的媒体的报道, 用来对冲媒体话题覆盖退出造成的样本构成漂移。它与保留全部媒体的主 full 语调互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。空集 (该 bank-year 无未退出媒体报道) 上均值无定义, 按情感类契约保持 NaN, 不与计数类 n_articles_exc 的零填连坐 —— 这是区别于兄弟计数列的关键口径。export.py 给它的 Stata 标签为 "Tone Excl Ceased (LLM Vote, Full)", 明确标注其来源为三家 LLM 多数投票而非词典或 BERT 法 (标签沿用 "Ceased" 字面, 但底层判据是话题覆盖退出代理, 详见家族 CORE 构念澄清)。使用建议: 主回归用全媒体主语调, 把 exc_tone_full 放进稳健性列, 观察点估计与显著性是否随媒体话题覆盖构成变化而系统性移动; 若两版系数在符号与量级上一致, 即可排除「媒体幸存者偏差驱动结论」这一替代解释。_is_ceased_media 是媒体来源层面的静态属性 (某来源在银行-fintech 话题子集上是否被判定退出覆盖, 判据 = 数据驱动 confirmed ∪ suspected, 其中 suspected 未经 NPPA 证实仍全量进入排除集), 而非报道层面, 因此同一未被判定退出的来源在任意年份的报道均被保留, 剔除的是整个来源在该判据下的时间序列, 该来源本身未必已真正停刊。

## VAR: exc_tone_ctx

【变体差分】
本列是 ctx 轨的疑似退出话题覆盖媒体稳健性语调: 文本窗口取「标题 prepend + 银行实体上下文窗口」(content_ctx), 即以目标银行实体为中心截取邻近上下文而非整篇正文, 篇级来源为 llm_vote_score_ctx, 同样只在未被判定退出话题覆盖的媒体子集上按 (target_bank, year) 求均值。与 exc_tone_full 的唯一差分是文本窗口: full 用完整正文, ctx 收缩到实体窗口, 目的是让语调更聚焦于「关于该银行本身」的措辞、削弱同篇报道中无关段落的稀释。在留篇门控 full-only 口径下, ctx 轨是 full 留篇集的 conditional-on-full 子集测度 (行宇宙为 full 的子集, per-track 列照算), 定位为主 full 轨的稳健性并排轨而非独立主轨。exc_tone_ctx 与 exc_tone_full、exc_tone_ss 三者互为稳健性、不分主次, 各自 just-identified 并排, 三轨严禁混进同一 over-identified Hansen J (三轨高度相关, 混入即制造虚假过度识别)。空集上均值保持 NaN 不零填。export.py 标签为 "Tone Excl Ceased (LLM Vote, Ctx)" (标签沿用字面 "Ceased", 实际判据是话题覆盖退出代理, 且判定媒体是否退出的年度窗口来自银行-fintech 全篇子集, 与 ctx 轨自身的实体窗口截取无关)。ctx 与 ss 的分别在于: ctx 是实体窗口 (银行实体邻近), ss 是银行与金科同句共现窗, 二者判定不对称口径不同, 不可互相复用。使用上, exc_tone_ctx 检验的是「把语调焦点从整篇正文收缩到银行实体上下文后, 剔除疑似退出话题覆盖媒体的结论是否依旧稳健」这一双重稳健性 (窗口 × 媒体样本), 因此它既是 full 轨的窗口稳健臂, 又是全媒体主测度的媒体样本稳健臂, 两条稳健维度正交叠加。空集上均值保持 NaN 与情感类契约一致, 与兄弟计数列 n_articles_exc 的零填口径刻意区分, 避免「无未退出媒体报道」被误读为「中性语调」。

## VAR: exc_tone_ss

【变体差分】
本列是 ss 轨的疑似退出话题覆盖媒体稳健性语调: 文本窗口取「标题 prepend + 银行∧金科同句共现窗」(content_ss), 即只保留目标银行与金融科技词在同一句 (±ss_sentence_radius 句窗, 默认 1) 共现的文本片段, 篇级来源为 llm_vote_score_ss, 在未被判定退出话题覆盖的媒体子集上按 (target_bank, year) 求均值。与 full/ctx 的差分在文本窗口的最窄化: ss 轨把语调锁定在「银行与金科同句同现」的语境, 使测度最贴近「银行涉足金融科技」这一具体叙事的情感色彩。ss 轨的回退语义镜像 ctx: 当某篇报道无银行∧金科同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True (共享 n_articles 分母); 若 FINTECH_AC 为 None 则该轨 *_is_fallback 全 True 优雅降级。在 full-only 门控下, ss 同为 conditional-on-full 子集轨。exc_tone_ss 与 exc_tone_full、exc_tone_ctx 互为稳健性、不分主次, 各自 just-identified 并排, 三轨禁混进同一 over-identified Hansen J。空集上均值保持 NaN, 不与计数类零填连坐。需要注意: 源列 llm_vote_score_ss 在 df_alive 中缺失时由 if src in df_alive.columns 守卫跳过该轨, 不影响 full/ctx 的产出; 在 T=2 开发语料上 ss 轨可能因同句共现稀疏而退化, 属预期, 生产 T=18 语料下正常。使用定位上, exc_tone_ss 是三轨中语境最窄、最贴近「银行涉足金融科技」这一具体叙事的语调臂, 同时叠加了剔除疑似退出话题覆盖媒体的样本稳健性, 因此在检验主结论是否被「泛泛的银行报道语调」而非「银行金科语境语调」驱动时最具鉴别力。与 full/ctx 一样, 空集上的均值按情感类契约保持 NaN 而非零填, 不与计数类 n_articles_exc 连坐; 三轨口径的一致性保证了跨轨系数比较不受填充规则差异污染。ss 轨的判定同样继承家族级构念澄清: _is_ceased_media 标记的是媒体来源在银行-fintech 话题上的覆盖退出代理 (confirmed ∪ suspected, suspected 未经 NPPA 证实), 而非该来源已确证停刊; ss 轨自身的同句共现窗口截取与这一媒体层面判据相互独立, 不因窗口收窄而改变排除集口径。

<!-- rendered-citations:begin -->
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Li, Z., Peng, Q., & Zhang, R.-Z. (2025). When Spotlights Fade: Local Newspaper Closures and Financial Advisor Misconduct. Journal of Financial and Quantitative Analysis. https://doi.org/10.1017/s0022109025101749
Ma, Z., Stice, D., Stice, H., & Zhang, Y. (2025). Local newspaper closures and bank loan contracts. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.13046
<!-- rendered-citations:end -->
