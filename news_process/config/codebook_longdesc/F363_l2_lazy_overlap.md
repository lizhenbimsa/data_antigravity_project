---
family_id: F363
columns:
  - lazy_overlap_ctx
  - lazy_overlap_full
  - lazy_overlap_ss
unit: 无量纲距离得分 (1 减 Szymkiewicz–Simpson overlap coefficient, 取值 [0,1], 1=完全改动/两期词集合完全不重合, 0=完全未改动/两期词集合完全重合)
formula: "lazy_overlap_track(t) = 1 - |W_track(bank,t) ∩ W_track(bank,t-1)| / min(|W_track(bank,t)|, |W_track(bank,t-1)|); W_track(bank,t) 为该银行-年度 track 轨聚合文本的分词后词集合; track ∈ {full, ctx, ss}; 分母取两期词集合中较小者的势 (overlap coefficient), 并非并集势 (并集势对应家族外的 lazy_jaccard 列)"
producer: news_process/pipeline/features/strategic_diff.py::_compute_lazy_distances (经 pipeline/panel/export.py 挂载入面板导出标签表)
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - strategic_diff 内部 _aggregate_bank_year_texts 产出的 bank-year 聚合文本
citations:
- doi: 10.1111/jofi.12885
  type: journal
  authors: Cohen, L., Malloy, C., & Nguyen, Q.
  year: 2020
  title: "Lazy prices"
  venue: The Journal of Finance
  vol: 75
  issue: 3
  pages_or_artno: 1371-1415
- doi: 10.1016/j.jcorpfin.2021.102097
  type: journal
  authors: Haw, I.-M., Song, B. Y., Tan, W., & Wang, W.
  year: 2021
  title: "Bankruptcy, overlapping directors, and bank loan pricing"
  venue: Journal of Corporate Finance
  vol: 71
  pages_or_artno: "Article 102097"
- doi: 10.1016/j.gfj.2021.100672
  type: journal
  authors: Togan Egrican, A.
  year: 2021
  title: "Overlapping board connections with banker directors and corporate loan terms: Evidence from syndicated loans"
  venue: Global Finance Journal
  vol: 50
  pages_or_artno: "Article 100672"
- doi: "10.1111/acfi.13076"
  type: "journal"
  authors: "Wang, Y., Ye, Q., Wang, J. J., & Wang, Y."
  year: 2023
  title: "Earnings manipulation and similarity of annual report disclosure: Evidence from China"
  venue: "Accounting & Finance"
  vol: "63"
  issue: "S1"
  pages_or_artno: "1137-1156"
- doi: "10.1016/j.bar.2023.101305"
  type: "journal"
  authors: "Xue, X., Wang, L., & Hu, N."
  year: 2024
  title: "Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China"
  venue: "The British Accounting Review"
  vol: "56"
  issue: "5"
  pages_or_artno: "101305"
- doi: "10.1007/s10644-025-09915-x"
  type: "journal"
  authors: "Qi, D., & Chen, W."
  year: 2025
  title: "R&D narrative disclosure and semantic similarity: evidence from China"
  venue: "Economic Change and Restructuring"
  vol: "58"
  issue: "5"
  pages_or_artno: "77"
new_dois: []
---

## CORE

【构念与来源】

lazy_overlap 家族衡量的是同一家银行相邻两个年度媒体报道文本之间的"改动程度": 把某银行某年度全部报道文本(按 track 轨聚合为一篇年度文档)分词后取词集合, 计算与上一年度词集合的 Szymkiewicz–Simpson overlap coefficient(交集势除以两集合中较小者的势), 再用 1 减去该系数得到本列存值。数值越接近 1, 说明两期词集合重合度越低, 本年度媒体叙事用词相对上一年度发生了实质性更替, 信息环境出现新增内容或叙事切换; 数值越接近 0, 说明今年的媒体叙事用词与去年高度重合, 银行相关的公开信息环境在措辞层面几乎"原地踏步"。换言之本列存的是"改动距离"而非"重合相似度", 数值方向与直觉上的"重叠比例"相反, 下游解读回归系数符号时须以"值越大=改动越多/叙事越不稳定"为准, 不可按"值越大=越相似/越未改动"理解。这一构念直接继承 Cohen, Malloy & Nguyen (2020, Journal of Finance) 提出的"懒惰定价"(lazy prices)诊断思路: 该文发现公司年报在相邻财年之间的文本改动量与股价对基本面变化的反应速度存在系统性关联, 文本改动越少的公司, 市场对其后续负面消息的定价越滞后, 意味着文本层面的"懒惰"本身携带增量信息, 而非纯噪声。在该文原始设定下, 改动量本身用类似的"1-重合度"距离度量刻画, 数值越大代表改动越多、"懒惰"程度越低, 本家族的存值方向与之一致。本项目将这一年报-年度改动量诊断迁移到银行金融科技新闻叙事场域: 用银行-年度媒体文本替代公司年报文本, 用词集合改动距离替代年报段落改动距离, 检验"银行相关报道叙事是否稳定/滞后"这一构念是否也具有信息含量, 例如叙事长期不变(本列长期接近 0)的银行是否在金融科技转型节奏、风险披露及时性上表现出滞后特征。

【方法学与计算】

计算发生在 pipeline/features/strategic_diff.py 内的相邻期文本变化多算子模块。生产者函数 _compute_lazy_distances 对每个 track 轨的 bank-year 聚合文本, 逐银行取 (t, t-1) 相邻两期的分词词集合, 一次性产出三个算子: lazy_jaccard(标准 Jaccard 距离, 分母为并集势, 家族外列)、lazy_overlap(overlap coefficient 型距离, 分母为两集合中较小者的势, 与 lazy_jaccard 分母口径不同、实现路径独立、互为交叉校验)、lazy_minedit(归一化编辑距离, 对词序敏感, 与前两者互补)。三算子共享同一套相邻期分词与集合构造管线, 但对"改动"的刻画维度不同: Jaccard/overlap 类度量只关心词汇集合层面的增减, 完全忽略词序与重复频次, 且二者分母口径不同(并集 vs. 较小集合)会在集合大小差异悬殊时产生系统性数值差; minedit 则对词序变化和逐字/逐词插删更敏感。三算子均以 1 减相似度的形式存值, 数值越大代表改动越多。lazy_overlap 家族本身不做时间序列滞后处理之外的额外平滑或缩尾, 首年度(无 t-1 可比)按缺失处理, 不做前向填充或以 0/1 顶替, 避免制造虚假的"完全改动"或"完全未改动"信号。

三个轨道 full/ctx/ss 完全并行、各自独立计算, 不存在互相借用或回填关系:
full 轨复用 strategic_diff 顶部已生成的银行-年度聚合文本(标题 prepend 全文正文, prepend_title 语义), 是覆盖面最广的基准轨; ctx 轨基于 content_ctx(标题 prepend 实体窗口文本)重新做一次 _aggregate_bank_year_texts 聚合, 只在银行-金科相关实体邻近窗口内比较用词变化; ss 轨基于 content_ss(标题 prepend 银行∧金科同句共现文本)重新聚合, 判据最严格。ss 轨的回退语义严格镜像 ctx 轨: 当某篇文章不存在银行与金科词的同句共现时, 该篇 content_ss 退化为全文 body 兜底、ss_is_fallback 标记为 True, 与 ctx 轨"实体窗口缺失则退化"的降级逻辑保持同构, 二者共享 n_articles 分母口径, 不因回退而制造虚假的零方差或单边孤儿列。若某银行-年度在 content_ctx 或 content_ss 列本身缺失(上游列不存在, 而非该行回退), _compute_lazy_distances 的调用点会打印 WARNING 并整体跳过对应轨道, 不静默补零。

三轨之间遵循本项目的一贯口径: full/ctx/ss 互为稳健性度量、不分主次, 各自 just-identified 并排使用, 严禁在同一 over-identified 的 Hansen J 设定中把三轨同时作为多余工具变量混入(会人为制造过度识别检验的虚假拒绝或虚假通过)。三算子(jaccard/overlap/minedit)之间同样是互相印证而非互相替代的关系: 三者高度相关但刻画维度不同, 论文写作中应报告三者一致性而非把三者线性合并为单一复合指标。lazy_overlap 与家族内 coh_emb/coh_tfidf 等"同期内部连贯性"度量在构念上明确区分: coh_* 系列衡量的是同一年度内部多篇报道彼此之间的语义一致性(横截面连贯), lazy_overlap 系列衡量的是相邻两个年度之间的纵向改动量(时间序列稳定性), 两者互补而非重复, 不应在同一回归设定中作为共线的替代解释变量处理。

【文献定位】

Cohen, Malloy & Nguyen (2020, Journal of Finance)的"懒惰定价"发现是本家族最直接的方法论来源: 文本改动量本身(而非改动的具体内容)携带可定价的信息, 这一发现为把媒体叙事的年度间重叠度作为银行信息环境稳定性代理变量提供了理论依据。与此同时, "重叠"(overlap)作为一种诊断金融机构间关联与信息传导的度量思路, 在公司金融文献中也有独立的谱系: Haw, Song, Tan & Wang (2021, Journal of Corporate Finance)研究了破产事件、董事重叠与银行贷款定价之间的关系, 发现董事网络重叠会通过信息渠道影响贷款条款; Togan Egrican (2021, Global Finance Journal)进一步考察了含银行家董事的董事会重叠连接如何影响银团贷款条款。这两篇文献中的"重叠"指的是治理网络层面的节点重叠(董事身份重合), 与本家族衡量的文本词汇集合重叠属于不同的构念层次, 但二者共享同一方法论直觉: 重叠/不变本身可以是信息渠道的代理变量, 而不只是噪声。引用这两篇文献意在提示后续使用者, "重叠"类指标在银行相关实证文献中已具备一定的方法论正当性基础, 但须清楚区分网络结构重叠与文本内容重叠这两类完全不同的度量对象, 不可混用或彼此替代解释。 在词集合层面的年际改动量上, 近期中文语料证据可进一步充实本家族的文献坐标。Wang、Ye、Wang 与 Wang (2023) 以 2008-2020 年中国 A 股 13,679 家样本, 用 MD&A 与上一年文本的相似度作为核心测度, 记录了「高相似度=低增量信息」的经验规律, 且其算子同为中文分词后的词袋相似度, 与本家族的分词词集合口径最为贴近, 是 lazy 族在中文语料上的同域先例; 迁移边界在于原文单位为公司-年的自撰年报 MD&A、把低改动解读为盈余操纵动机, 而本家族度量的是第三方媒体叙事的中性改动距离, 不承接该操纵解释, 原文亦未采用本列以两集合中较小者的势为分母的 Szymkiewicz-Simpson 口径。Xue、Wang 与 Hu (2024) 以中国上市公司 2009-2021 样本检验经济政策不确定性对公司自身跨期 CSR 披露相似度的影响, 发现 EPU 越高、企业越倾向发布与自身过往高度重合的报告 (象征性披露), 直接印证「与自身上期文本重合本身可被外部环境驱动、并非纯噪声」这一本家族赖以成立的前提; 但原文把相似度置于被解释变量位置、由 EPU 驱动, 本家族三列为面板自变量, 且其象征性披露机制以披露方即文本作者为前提, 银行在本项目中并非报道撰写者, 该机制不可直接搬用。Qi 与 Chen (2025) 在中国语境对 R&D 叙事性披露构造语义相似度测度, 为「文本重合度」这一测度族提供了 2025 年的近期应用实例; 惟原文使用 embedding 语义相似度, 与本家族的分词词集合重叠系数在算子层面不同 (前者度量语义邻近, 后者只关心词汇集合的增减、完全忽略词序与频次), 期刊层级亦低于顶刊, 且原文不涉及本项目 full/ctx/ss 三轨口径, 故仅作构念族的近期存在性佐证, 不锚定本列的具体分母口径。
## VAR: lazy_overlap_ctx

【变体差分】

本列是 lazy_overlap 家族在 ctx 轨(标题 prepend 实体窗口文本)上的实现。计算时先用 content_ctx 列重新执行一次 _aggregate_bank_year_texts, 得到银行-年度层面的 ctx 轨聚合文本, 再对相邻两期(t, t-1)的分词词集合计算 overlap coefficient 并以 1 减该系数存值, 与 full 轨、ss 轨完全独立、互不借用中间结果。数值越接近 1 表示两期用词改动越大, 越接近 0 表示两期用词高度重合、几乎未改动。ctx 轨的文本范围被限定在银行与金融科技相关实体的邻近窗口内, 因此该列反映的是"银行-金科实体密切相关叙事片段"的年度间用词改动量, 而不是全文层面的改动量: 若某银行整体报道内容变化不大(lazy_overlap_full 偏低), 但金科相关片段的措辞出现明显更替(例如从笼统提及转为具体产品名称、监管口径, lazy_overlap_ctx 偏高), 则 lazy_overlap_ctx 会比 lazy_overlap_full 更早、更敏感地捕捉到这一变化, 二者出现分歧本身即具有诊断价值。ctx 轨依赖 content_ctx 列存在, 若该列在上游缺失, _compute_lazy_distances 会打印 WARNING 并跳过整个 ctx 轨(不产出该列, 而非补零或借用 full 轨), 与 CLAUDE.md 三轨口径要求的各自独立降级保持一致。该列不做首年度前向填充, 首年度对应银行的 lazy_overlap_ctx 恒为缺失, 需要在面板回归中按缺失值处理而非按 0 处理; 也不做跨年份平滑或缩尾, 保留原始波动以便与 lazy_jaccard_ctx/lazy_minedit_ctx 做算子间交叉校验。作为 ctx 轨稳健性臂, 该列须与 lazy_overlap_full、lazy_overlap_ss 并排报告, 而非在同一识别设定中相互替代或线性合并使用。

## VAR: lazy_overlap_full

【变体差分】

本列是 lazy_overlap 家族的基准(canonical)实现, 使用 full 轨聚合文本, 即标题 prepend 全文正文构成的银行-年度年度文档。计算上直接复用 strategic_diff 模块顶部已经为其他统计量(如 coh_* 系列)生成好的 agg_df 聚合结果, 避免对同一份 full 轨文本重复聚合, 是三轨中计算路径最短、覆盖样本最广的一支: 只要该银行该年度存在任意留篇通过(llm_verified_full == True, 全文口径留篇门控 2026-06-29)后的报道, 就能纳入聚合, 不受实体窗口或同句共现这类更严格判据的样本损耗影响。该列的取值区间与含义与家族 canonical 公式完全一致: 相邻两年度 full 轨词集合的 overlap coefficient 以 1 减值形式存储, 越接近 0 表示该银行整体媒体叙事年度间用词越稳定(重合度越高), 越接近 1 表示改动越大, 对应 Cohen, Malloy & Nguyen (2020)"懒惰定价"框架中"低改动量"取值接近 0 的诊断方向。该列同样不对首年度做前向填充, 该银行样本期首年的 lazy_overlap_full 恒为缺失; 不做跨期平滑或截尾处理, 原始波动保留以支持与同轨 lazy_jaccard_full、lazy_minedit_full 做一致性交叉检验。作为三轨并排稳健性设计的一支, full 轨在样本覆盖上最完整, 通常作为论文正文首选测度, 但按本项目口径三轨互为稳健性、不分主次, 不应仅因样本量优势而在识别策略中赋予 full 轨优先解释权, 更不得与 ctx/ss 轨同时塞入同一 over-identified Hansen J 设定。

## VAR: lazy_overlap_ss

【变体差分】

本列是 lazy_overlap 家族在 ss 轨(标题 prepend 银行∧金科同句共现文本)上的实现, 判据口径在三轨中最严格: content_ss 只保留银行主体词与金融科技相关词在同一句子内共同出现的文本片段(±1 句窗口的更宽松判据由 stage 13 共现硬过滤承担, ss 轨本身是同句严格判据, 二者是不同的判定层级)。计算流程与 ctx 轨对称: 先用 content_ss 列重新执行一次 _aggregate_bank_year_texts 得到银行-年度聚合文本, 再对相邻两期分词词集合计算 overlap coefficient 并以 1 减该系数存值, 数值越大表示银行-金科强相关叙事片段的年度间改动越大, 越接近 0 表示该片段用词高度稳定。该列的回退语义严格镜像 ctx 轨: 若某篇文章不存在银行-金科同句共现, 其 content_ss 会退化为全文 body 兜底、对应 ss_is_fallback 标记为 True, 与 ctx 轨"实体窗口缺失即退化"同构, 二者共享 n_articles 分母口径, 不产生单边孤儿或虚假零方差; 若 content_ss 列本身在上游整体缺失(而非逐行回退), _compute_lazy_distances 会打印 WARNING 并跳过整个 ss 轨, 不补零、不借用 ctx 或 full 轨的结果。由于同句共现判据最为苛刻, ss 轨样本量在三轨中通常最小, 在样本量有限的开发期数据(如早期试跑 T=2)上该列取值可能出现较多缺失甚至零方差退化, 这属于样本规模不足下的预期表现, 不代表计算逻辑存在缺陷; 在生产规模全量语料(T=19)上样本量损耗会显著缓解。与 ctx、full 两轨相同, 该列不做首年度前向填充、不做跨期平滑或缩尾处理, 保留原始波动供与同轨 lazy_jaccard_ss、lazy_minedit_ss 做算子间交叉校验。三轨并排使用时, ss 轨给出的是"银行与金融科技话题严格绑定叙事"的年度间稳定性, 当其与 full/ctx 轨结果出现分歧, 往往意味着银行整体叙事稳定但金科强相关叙事发生了实质更替, 或反之, 这类分歧本身是稳健性检验中值得单独讨论的现象, 不应通过合并三轨消除。

<!-- rendered-citations:begin -->
Cohen, L., Malloy, C., & Nguyen, Q. (2020). Lazy prices. The Journal of Finance, 75(3), 1371-1415. https://doi.org/10.1111/jofi.12885
Haw, I.-M., Song, B. Y., Tan, W., & Wang, W. (2021). Bankruptcy, overlapping directors, and bank loan pricing. Journal of Corporate Finance, 71, Article 102097. https://doi.org/10.1016/j.jcorpfin.2021.102097
Togan Egrican, A. (2021). Overlapping board connections with banker directors and corporate loan terms: Evidence from syndicated loans. Global Finance Journal, 50, Article 100672. https://doi.org/10.1016/j.gfj.2021.100672
Wang, Y., Ye, Q., Wang, J. J., & Wang, Y. (2023). Earnings manipulation and similarity of annual report disclosure: Evidence from China. Accounting & Finance, 63(S1), 1137-1156. https://doi.org/10.1111/acfi.13076
Xue, X., Wang, L., & Hu, N. (2024). Economic policy uncertainty and corporate social responsibility disclosure similarity: Evidence from China. The British Accounting Review, 56(5), 101305. https://doi.org/10.1016/j.bar.2023.101305
Qi, D., & Chen, W. (2025). R&D narrative disclosure and semantic similarity: evidence from China. Economic Change and Restructuring, 58(5), 77. https://doi.org/10.1007/s10644-025-09915-x
<!-- rendered-citations:end -->
