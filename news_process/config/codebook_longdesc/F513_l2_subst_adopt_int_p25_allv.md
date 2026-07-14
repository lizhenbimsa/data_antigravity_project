---
family_id: F513
columns:
- subst_adopt_int_p25_allv
- subst_adopt_int_p25_allv_ctx
- subst_adopt_int_p25_allv_ss
unit: 银行-年占比 (0-1 区间的篇均份额, 分母=该银行-年内已测量政策相似度与金科强度的报道篇数)
formula: 'bank-year 内 mean(_is_subst_{track}_p25{ctx/ss})，其中 _is_subst 由 _classify_policy_quadrants(df, sim_col=policy_cosine_sim(_track), freq_col=fintech_intensity_score(_track), pct=25) 逐篇二值判定: sim>=P25(sim) 且 freq>=P25(freq) 记为 1，否则为 0；P25 阈值按 groupby(year) 逐年分别在 sim 分布与 freq 分布各自的年内第 25 百分位数上计算 (非联合分布分位, 亦非跨全部年份合并的单一全局分位), 与调用方是否切片无关。'
producer: pipeline\panel\runner.py (_classify_policy_quadrants 逐篇分类 + bank-year 聚合逻辑) ; pipeline\panel\export.py (STATA_LABELS 标签映射)
upstream:
- pipeline/filtering/policy_alignment.py (policy_cosine_sim_{track} 逐篇三轨政策余弦相似度, stage 16, 聚合为 article_sim_mean/article_sim_std 供本族消费)
- pipeline/filtering/fintech_intensity.py (fintech_intensity_score_{track} 逐篇三轨金科强度得分, stage 15, 聚合为 fintech_intensity_mean 供本族消费)
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
- doi: 10.5465/amj.2006.23478255
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: The Symbolic Management of Strategic Change; Sensegiving via Framing and Decoupling
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是「实质性金科政策采纳」(substantive fintech-policy adoption) 在银行-年层面的占比强度, 构念根植于组织理论的实质-象征二分传统 (substance vs. symbolism)。Westphal & Zajac (1994, ASQ) 最早在 CEO 长期激励计划的研究中区分了「采纳一项政策」与「真正实施一项政策」两个独立维度; Westphal & Zajac (1998, 2001) 与 Fiss & Zajac (2006, AMJ) 进一步把这一区分系统化为组织脱耦 (decoupling) 框架: 组织可以在话语/披露层面高度趋同于制度期待, 却在实际行为层面并未随之调整, 二者的组合关系而非任一维度单独决定了「真采纳」还是「表面采纳」。本项目把这一构念平移到中国银行业媒体报道语料: 每篇报道同时携带两条独立信号 —— (a) 逐篇政策相似度 `policy_cosine_sim_{track}` (stage 16 `pipeline/filtering/policy_alignment.py` 产出, 报道文本与权威政策锚点文档段嵌入后取余弦相似度, 聚合为本族消费的 `article_sim_mean`/`article_sim_std`), (b) 逐篇金科强度 `fintech_intensity_score_{track}` (stage 15 `pipeline/filtering/fintech_intensity.py` 产出, 基于连续型强度打分而非关键词命中计数, 聚合为本族消费的 `fintech_intensity_mean`)。当一篇报道在这两条信号上同时"高"时, 判定其体现的是「话语与强度同步」的实质性采纳; 当仅政策相似度高而强度低, 或仅强度高而相似度低时, 则分别落入象征性 (token) 或隐性 (hidden) 采纳象限, 与本族并列同源但非本族列。

【方法学与计算】
构造分两步。第一步是逐篇二值分类: `pipeline/panel/runner.py::_classify_policy_quadrants` 对每篇已测量的报道同时读取逐篇相似度列 `sim_col`(=`policy_cosine_sim_{track}`, 来自 stage 16 `policy_alignment.py`) 与逐篇强度列 `freq_col`(=`fintech_intensity_score_{track}`, 来自 stage 15 `fintech_intensity.py`), 函数体内部固定 `groupby('year')` 逐年分别计算相似度分布与强度分布各自的第 25 百分位数 (P25) 作为该年份/该分类口径下的阈值——这一按年重算是函数实现本身写死的行为, 与外部调用方是否已按年份切片传入子集无关(即便传入的是多年合并样本, 阈值仍在函数内部按 year 列分组分别计算, 而非对整批样本取一个单一全局分位数)。再逐篇判定: 相似度 ≥ 该篇所属年份的 P25 且强度 ≥ 该篇所属年份的 P25 者记 `_is_subst_*=1`, 否则为 0。阈值是对相似度分布和强度分布分别独立取分位数, 不是对联合分布取分位数, 且是逐年独立计算而非跨全部年份合并的单一阈值 —— 这意味着两个维度的"高"是各自年内边际分布意义上的高, 象限划分近似一个正交的 2×2 网格而非某个联合密度等高线, 这一实现细节决定了四个象限 (token/hidden/subst/以及隐含的第四象限"双低") 在样本中不必然各占 1/4, 取决于相似度与强度两个变量在该年内的相关结构; 同时逐年阈值也意味着跨年比较本族占比时, 分类基准本身是随年份浮动的相对阈值而非固定的绝对阈值, 不同年份被判定为"高"的原始分值可能不同。本家族取的是 Track B —— 即 `int` (intensity, 强度轨), 强度信号来自 stage 15 连续型金科强度打分, 与另一并行轨 Track A `kw` (keyword, 基于金科关键词 AC 自动机命中计数的离散轨) 是两套独立构造、互不替代的稳健性对照, 二者共享同一套政策相似度信号与同一 P25 阈值口径, 但强度信号的构造原语不同 (连续打分 vs. 关键词命中计数), 分类结果不必然一致。`allv` 后缀标记的是政策锚点的时间维度口径, 而非话题粒度口径: `pipeline/filtering/policy_alignment.py::all_vintage_companion_enabled` 明确, vintage-aware 主轨 (无 `allv` 后缀的另一并列族) 构造锚点时只纳入"年度 t 仅使用截至 t 已发布的政策文档"，以此消除前视偏误 (look-ahead bias)，是 identification 意义上的正确口径；`_allv` (all-vintage) 则是与之并列的全年份/全语料静态锚点孪生: 年度 t 的文章统一与所有年份 (含未来) 的政策文档拼接后的静态锚点计算余弦相似度, 下游构造方法 (同嵌入/同池化/同余弦/同四象限) 与主轨完全一致, 唯一区别是锚点本身是否受 vintage 前视裁剪。`_allv` 因此含未来政策文本, 源码明确要求"论文须明确披露 `_allv` 系 ex-post/全语料口径", 且仅作 anchor-robustness 对照, 绝不替换 vintage 主轨; 两轨各自 just-identified 并排、互为稳健性不分主次, 绝不可混入同一 over-identified Hansen J 检验 (vintage 不可用/无年份信息时二者退化为数值相同, 属诚实退化而非构造等价)。第二步是按 (银行, 年) 分组对二值列取均值: `subst_adopt_{track}_p25{anc_sfx}{sim_sfx} = groupby(['target_bank','year'])['_is_subst_*'].mean()`, 分母是该银行-年内已同时测得相似度与强度两列的报道篇数, 而非该银行-年全部报道篇数——未测量的报道 (相似度或强度任一缺失) 既不进入分子也不进入分母, 是逐篇 listwise 处理而非填零。这一处理刻意避免了早期版本 `fillna(0.0)` 造成的度量污染: `subst_adopt` 等"率/均值/相似度"类指标若把"未测量"强填为 0, 会把"没有证据支持采纳"误编码为"证据证明未采纳", 在双向固定效应回归中系统性压低系数 (Allison 2001 关于缺失数据处理对固定效应估计偏误的一般性论述适用于此); 因此该银行-年若全部报道均未测得, 面板列取 NaN 并保持缺失, 由下游回归做 listwise 处理。

【文献定位】
本族在构念定位上直接对接 Westphal & Zajac (1994, ASQ) 与 Fiss & Zajac (2006, AMJ) 的实质-象征二分及组织脱耦理论: 二者研究的是政策"采纳"(话语层面的宣称/披露) 与"实施"(行为层面的资源投入/强度) 之间的一致或背离; 本族把这套逻辑操作化为文本层面的双信号交叉分类, 政策相似度对应"话语层面是否对齐制度期待", 金科强度对应"文本所反映的实际参与深度"。在方法论上, 这一"披露/宣称"与"实际行为"脱耦、"cheap talk"式表态的识别策略, 与近年气候披露文献 (Bingler, Kraus, Leippold & Webersinke 2024, *Journal of Banking & Finance*) 用文本相似度刻画企业气候披露的"廉价谈话"程度、以及 Duchin, Gao & Xu (2025, *The Journal of Finance*) 用资产市场证据检验可持续性披露是否伴随真实行为调整的研究思路一脉相承——三者共同的方法论直觉是: 单一文本信号 (相似度或强度) 都不足以区分"真做"与"只说", 唯有把两条信号交叉才能定位出"说了也做了"(本族 subst)、"只说不做"(token, 并列列)、"做了没说"(hidden, 并列列) 三种质性不同的采纳形态。

【三轨口径提示】本家族三列对应 full/ctx/ss 三条文本轨道, 三轨在构造上使用彼此独立的相似度与强度输入 (`_classify_policy_quadrants` 逐篇消费的是原始未聚合列 `policy_cosine_sim_{trk}` / `fintech_intensity_score_{trk}`, 各自基于同轨文本重新计算; 与 runner.py 另一处对同一原始列按 (bank,year) 分组取 mean/std 聚合产出的面板级列 `article_sim_mean_{trk}`/`fintech_intensity_mean_{trk}` 是同名概念下的不同聚合层级, 后者是文档层面的汇总统计, 不直接进入本族的逐篇分类函数), 各自 just-identified 并排、互为稳健性、不分主次, 绝不可混入同一 over-identified Hansen J 检验。三轨共享的留篇门控口径是 full-only (2026-06-29 起): 一篇报道是否被计入"银行金科报道"由 `llm_verified_full` 单一判据决定, ctx/ss 轨的分类与聚合是在 full 留篇集合子集上的条件测度/稳健性口径, 而非独立的样本口径。

## VAR: subst_adopt_int_p25_allv

【变体差分】
本列是家族在 full 文本轨道上的 `_allv` (all-vintage) 变体, 与另一并列存在但不属本家族的 vintage-aware 主轨 (锚点仅纳入截至年度 t 已发布的政策文档, 用以消除前视偏误) 互为稳健性对照——`_allv` 锚点改用所有年份 (含未来) 政策文档拼接的静态锚点, 下游分类构造与 vintage 主轨完全一致, 仅锚点的时间裁剪不同; 论文引用本列须披露其为 ex-post/全语料口径, 不可替代 vintage 主轨用于因果识别。对应 full 文本轨道: 逐篇相似度信号取 `policy_cosine_sim_allv_full` (全文标题+正文与政策锚点向量的余弦相似度), 逐篇强度信号取 `fintech_intensity_score_full` (全文轨的连续型金科强度打分), 二者各自的 P25 阈值由 `_classify_policy_quadrants` 内部固定按 `groupby('year')` 逐年在 full 轨全体已测量报道上计算得到 (与调用方是否切片无关); 本列聚合时消费的面板级汇总统计 `article_sim_mean`/`fintech_intensity_mean` 是这批逐篇原始列按 (银行,年) 分组取 mean 后的下游产物, 与 `_classify_policy_quadrants` 分类环节直接读取的逐篇列不是同一聚合层级, 不应混为一谈。作为家族主口径, 本列的样本覆盖面最完整——因为 full 轨即为留篇门控本身依据的文本轨, 不存在 ctx/ss 轨可能出现的"因实体窗口/同句共现回退导致的文本内容退化"问题, 相似度与强度两列的缺失率理论上最低。在回归设定中, 本列通常作为机制检验/稳健性表的基准列, 用于验证"银行-年层面话语与强度同步的金科报道占比"这一构念与主回归结果 (基于 token_adopt/连续型 fintech_intensity_mean 等) 是否方向一致; 三轨互为稳健性并排陈列, 不应把本列径直等同于唯一"正确"口径。本列与家族内并列的 `token_adopt_int_p25_allv`/`hidden_adopt_int_p25_allv` 共享同一批已测量报道作为分母口径, 三者之和不必然等于 1 (因为四象限中还存在"双低"的隐含第四类未单独出列), 使用者若要核对占比闭合关系, 需连同"双低"类一并考虑而非仅凭本族三列相加验证完备性。本列同样继承家族层面的通用注意事项: P25 阈值是 `_classify_policy_quadrants` 函数体内部固定按年份分组独立计算的年内分位数, 该按年重算的行为写死在函数实现里, 不随调用方传入的报道子集范围而改变 (即便调用方一次性传入多年合并样本, 函数仍在内部按 year 分组分别取阈值), 因此跨年比较本列数值时应理解为"逐年相对阈值"而非"固定绝对阈值"下的分类结果, 不应误读为跨年阈值口径可能不一致所致的测量漂移。

## VAR: subst_adopt_int_p25_allv_ctx

【变体差分】
本列同样是 `_allv` (all-vintage) 全年份静态锚点变体在 ctx 轨上的实现, 与 vintage-aware 主轨的 ctx 列互为稳健性对照 (差异仅在锚点是否受前视裁剪, 下游四象限分类构造一致)。本列对应 ctx (entity-context, 实体窗口) 文本轨道: 逐篇相似度与强度两个输入信号均改为在 `content_ctx` (标题+目标银行实体窗口文本, stage 14 `ctx_materializer` 物化) 上重新计算的同轨原始列 `policy_cosine_sim_allv_ctx` / `fintech_intensity_score_ctx` (若同轨强度变体列存在则优先使用; `pipeline/panel/runner.py` 在装配 `_freq_eff` 时对 ctx/ss 轨显式检测同轨变体列是否存在, 存在则切换, 不存在且为主轨才发出降级 WARNING), P25 阈值同样由 `_classify_policy_quadrants` 内部按年分组在 ctx 轨自身的分布上独立计算, 不与 full 轨阈值混用。ctx 轨反映的是"当报道聚焦在目标银行实体所在窗口时, 该窗口文本与政策锚点的相似度、金科强度是否同步走高", 是比全文轨更聚焦、噪声更少但样本覆盖率可能因实体窗口抽取失败而略窄的稳健性对照轨。按 CLAUDE.md 三轨铁律, 本列与无后缀列、`_ss` 列各自 just-identified 并排、互为稳健性不分主次, 三者绝不可混入同一 over-identified Hansen J; 留篇门控仍以 full 轨 `llm_verified_full` 为准, 本列的分子分母均限定在该子集内计算。相较于无后缀 full 轨列, 本列的实践意义在于剥离了报道中与目标银行不直接相关的段落噪声——一篇报道可能通篇涉及多家银行或宏观政策评论, 只有实体窗口附近的文本才真正承载"该银行是否同步展现政策话语与金科强度"的信息, ctx 轨因此常被用作 full 轨结果的稳健性佐证: 若两轨方向一致, 说明全文层面的信号并非被无关段落稀释所致的假象; 若两轨出现分歧, 则提示 full 轨结果可能部分由报道中与目标银行无关的政策/金科语句驱动, 需结合 `target_bank_in_title` 等辅助信号进一步排查。与 Track A (kw 轨) 并列的同名 ctx 列相比, 本族强度信号仍走连续型金科强度打分而非关键词命中计数, 这一区分在 ctx 窗口收窄后依然保持, 不因窗口缩小而退化为计数口径。

## VAR: subst_adopt_int_p25_allv_ss

【变体差分】
本列同样是 `_allv` (all-vintage) 全年份静态锚点变体在 ss 轨上的实现, 与 vintage-aware 主轨的 ss 列互为稳健性对照 (差异仅在锚点是否受前视裁剪, 下游四象限分类构造一致)。本列对应 ss (same-sentence, 银行∧金科同句共现) 文本轨道: 逐篇相似度与强度两个输入信号 `policy_cosine_sim_allv_ss` / `fintech_intensity_score_ss` 取自 `content_ss` (标题+银行与金科词同句±N 窗口文本, N 见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1) 上重新计算的同轨原始列, P25 阈值同样由 `_classify_policy_quadrants` 内部按年分组在 ss 轨自身分布上独立计算。ss 轨回退语义镜像 ctx 轨: 当一篇报道内不存在目标银行与金科词的同句共现时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 此时该篇报道在 ss 轨下的相似度与强度信号实质上退化为对全文的重新打分, 而非真正意义上的"同句局部窗口"测度, 分母上仍与 ctx 轨共享同一套 `n_articles` 计数口径 (回退篇目不被排除, 但其信号质量弱于真正命中同句共现的篇目, 使用者在解读该列时应留意这一退化情形)。本列同样以 full 轨留篇门控为行样本边界, 与无后缀列、`_ctx` 列构成三轨并排的互为稳健性关系, 绝不可混入同一 over-identified Hansen J; 三者之间的差异应被解读为"文本聚焦范围不同导致的测度稳健性对照", 而非彼此替代或存在唯一正确轨道。同句共现是三轨中判据最严格的一种: 它要求目标银行实体与金科词汇在同一句 (±N 窗) 内共同出现, 相较 ctx 轨的实体窗口口径更进一步收紧了"相关性"的判定标准——一篇报道即便在实体窗口内提及金科, 若两者未落在同一句, 也不会被 ss 轨的非回退子样本计入。这意味着 ss 轨真正命中 (非回退) 的报道子集在语义上最接近"银行与金科被作者直接并置讨论"的场景, 该子集内测得的相似度与强度信号噪声理论上最低, 但样本量也最容易受限——尤其在语料稀疏的银行-年组合上, 同句共现命中率低会推高回退比例, 使 ss 轨的有效信息量向 full 轨趋同。使用者在跨银行或跨年比较 ss 轨结果时, 应结合 `ss_is_fallback` 的比例辅助判断该银行-年的 ss 轨数值究竟主要来自真实同句命中还是全文回退, 避免把回退主导的数值误读为"强共现证据"。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change; Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
<!-- rendered-citations:end -->
