---
family_id: F028
columns:
- avg_bank_count
- max_bank_count
unit: 银行家数/篇 (count, 无量纲整数计数的年度聚合)
formula: "bank_count(article) = 单篇报道中被识别出的不同目标银行数; avg_bank_count(bank-year) = mean(bank_count); max_bank_count(bank-year) = max(bank_count)"
producer: news_process/pipeline/panel/encode.py::aggregate_panel (article 级 bank_count 于 runner 步骤3 构造)
upstream:
- 24_herd_decay.parquet (df_exploded; article×bank 级 verified 集, 含 bank_count/is_multi_bank)
- 40_panel_yearly.parquet (bank-year 聚合输出)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: Journal of Financial Economics
  vol: 146
  issue: 2
  pages_or_artno: 529-551
- doi: 10.1016/j.jacceco.2021.101455
  type: journal
  authors: Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y.
  year: 2022
  title: "Meet the press: Survey evidence on financial journalists as information intermediaries"
  venue: Journal of Accounting and Economics
  vol: 73
  issue: 2-3
  pages_or_artno: 101455
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的构念是"同篇共提银行家数"(bank co-mention breadth), 即一篇媒体报道在文本中同时点名了多少家不同的目标银行, 再把这一篇章级计数按银行-年度聚合成两个统计量。文章级原始量 bank_count 在 runner 步骤3 的多银行特征块中构造 (与 is_multi_bank、ln_bank_count 并列产出), 但其实体识别并不在步骤3 重新扫描: 逐篇的银行识别早在上游 stage 11 的 news_bank.py 完成, 管道以银行侧判定 (否定过滤加短名过滤) 识别出目标银行之外同篇共提的其他银行, 去重后以分号分隔写入 co_mentioned_banks 列。步骤3 据此纯派生 bank_count——即取该篇 co_mentioned_banks 中分号分隔的共提银行个数再加 1 (加 1 是计入 target_bank 自身; 若 co_mentioned_banks 为空串则 bank_count 记为 1)。故 bank_count 是对 stage 11 已固化的实体识别产物 (co_mentioned_banks token) 的计基数派生, 而非在聚合阶段重跑一次银行侧扫描; 构念上仍严格等价于"同篇被识别出的不同目标银行家数", 只是落地机制是 token 计数而非二次识别。当且仅当 bank_count 大于 1 时 is_multi_bank 置真、multi_bank_frac 在年度层作均值。可将本家族理解为把"这家银行的报道里, 平均每篇还捎带提了几家同业、以及最拥挤的一篇提了几家"这一信息浓缩进面板。它衡量的不是语调、不是金融科技强度, 而是报道的"银行密度"——一家银行是被单独聚焦报道, 还是总被裹进多主体的行业综述、榜单、监管通报之中。

【方法学与计算】
两列都是 encode.py::aggregate_panel 中对同一 article 级源列 bank_count 的分组聚合: avg_bank_count 取组内均值 ('bank_count','mean'), max_bank_count 取组内极大值 ('bank_count','max')。分组键为银行-年度 (target_bank × year), 行宇宙严格等于 full-only 留篇集: 一篇报道是否计入某银行某年, 由 stage 21 的 llm_verified_full 为真决定 (2026-06-29 留篇门控定为 full-only, ctx/ss 降为 conditional-on-full 的测度轨), 因此这两列的聚合样本与 n_articles 物理篇数分母同源、同一批 verified article×bank 行。需强调 bank_count 是 track-agnostic 的元数据计数: 它源于实体识别而非三轨情感文本, 全文/实体窗/同句三轨共享同一篇计数, 不存在 avg_bank_count_ctx / _ss 之类的轨道孪生列——这与 CLAUDE.md 中"唯一不能双轨的是 track-agnostic 元数据度量"的口径一致, 也因此本家族不涉及三轨、co-primary 双轨嵌入或任何梯子的"各自 just-identified 并排"叙事。均值与极大值二者互补而非替代: 均值刻画集中趋势 (典型报道的共提规模), 极大值刻画尾部极端 (最拥挤的一篇), 极大值对单篇大榜单/行业普查式报道高度敏感, 均值则被大量单主体报道拉低。作为整数计数的年度聚合, 本量属于典型的 count / count-like 数据, 其分布右偏、方差随均值上升, 下游若直接入回归须留意这一异方差与非负特性。

【文献定位】
在计数型金融变量的处理上, Cohn, Liu, and Wardlaw (2022) 系统梳理了 count 与 count-like 数据在公司金融中的建模陷阱, 指出对右偏非负计数直接跑 OLS 或对数变换均可能产生偏误, 为本家族两列作为潜在协变量/被解释变量时的函数形式选择提供了方法学基准。就"媒体共提"这一信息结构而言, Li and Luan (2025) 以新闻文本构造投资者分歧, 说明同一新闻流中被并置的多主体信息会通过关注与解读的异质性影响市场, 呼应本家族把"一篇里同时提了几家银行"视作行业关注结构的代理。Call, Emett, Maksymov, and Sharp (2022) 通过对财经记者的调查证据揭示新闻中介如何选择报道对象与并置主体, 为 bank_count 的生成机制 (为何某些银行更常被裹进多主体报道) 提供了信息中介视角的制度解释。Loughran and McDonald (2016) 对会计与金融文本分析方法的综述则界定了实体识别与计数类文本测度的一般效度边界, 提示短名匹配/否定过滤等判定选择会实质影响计数结果, 与本管道银行侧判定的否定加短名过滤设计相互印证。综上, 本家族两列在文献坐标中处于"媒体报道的行业共提结构"这一交叉带, 既是文本计数测度、也是关注网络的边密度信号。

## VAR: avg_bank_count

【变体差分】
avg_bank_count 是家族的中心趋势臂: 对某银行某年全部 full-only 留篇报道的 article 级 bank_count 取算术均值 ('bank_count','mean')。语义上它回答"这家银行这一年被报道时, 平均每篇同时还提到了几家银行"。取值下界为 1 (该年所有报道都只单独提到本行时), 越大表示报道越倾向于把本行与同业并置——常见于行业排行榜、监管批量通报、板块行情综述等多主体文本。它区别于同族 max_bank_count 之处在于对分布的刻画位置: 均值受大量单主体报道 (bank_count=1) 稀释, 因此稳健地反映"典型报道拥挤度", 而非尾部极端; 若一家银行绝大多数报道是单独聚焦、仅偶有一篇大榜单, 则 avg_bank_count 仍接近 1、而 max_bank_count 会被那一篇顶高, 二者之差恰是分布右偏程度的粗略读数。它也区别于相邻的 multi_bank_frac (is_multi_bank 的年度均值): 后者是"多提报道占比"的 0/1 二值频率, 只分单主体与多主体两档、丢失了"多提到底多几家"的强度信息; avg_bank_count 保留计数强度, 二者可并用作行业共提的频率-强度分解。作为 track-agnostic 元数据计数, 本列无三轨或嵌入双轨孪生, 也不进任何梯子。使用时须记住其分母口径与 n_articles 同为 full-only 留篇集, 且作为右偏计数的均值, 入回归前宜考虑对数或计数模型而非默认线性设定 (呼应 Cohn 等 2022 的计数数据建模告诫)。

## VAR: max_bank_count

【变体差分】
max_bank_count 是家族的尾部/极值臂: 对同一银行-年度分组内全部 full-only 留篇报道的 article 级 bank_count 取极大值 ('bank_count','max'), 即"这家银行这一年里, 单篇提到最多银行的那一篇提了几家"。它专门捕捉分布右尾, 对行业普查式、榜单式或系统性监管通报这类一次性并置大量主体的极端报道极其敏感——哪怕全年仅出现一篇 20 家银行同列的排行榜, max_bank_count 也会被顶到 20, 而 avg_bank_count 几乎不动。因此本列与家族均值臂 avg_bank_count 构成"极值 vs 中心趋势"的互补对: 单独看 max 会高估一家银行的常态共提强度 (被稀有大榜单主导), 单独看 avg 则会漏掉这类稀有但信息量大的系统性并置事件; 二者之差可作分布偏态与"最大共提事件规模"的诊断量。相较 multi_bank_frac 只给频率、avg_bank_count 给中心强度, max 给的是该年共提结构的上确界, 三者层层刻画同一构念的不同矩。作为整数计数的极大值统计, 它同样是 track-agnostic 元数据, 无三轨/嵌入双轨变体、不参与消融或权重梯子。分析上须格外注意其对单篇异常报道的高杠杆与右偏厚尾特性: max 型计数不宜直接线性入 RHS, 稳健用法是作离散阈值指示 (如是否曾出现大规模并置) 或与 avg 并列作稳健性对照, 这与 Cohn, Liu, and Wardlaw (2022) 关于 count-like 变量须审慎设定函数形式的建议一致。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Call, A. C., Emett, S. A., Maksymov, E., & Sharp, N. Y. (2022). Meet the press: Survey evidence on financial journalists as information intermediaries. Journal of Accounting and Economics, 73(2-3), 101455. https://doi.org/10.1016/j.jacceco.2021.101455
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
<!-- rendered-citations:end -->
