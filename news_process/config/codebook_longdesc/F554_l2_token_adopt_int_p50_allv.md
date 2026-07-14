---
family_id: F554
columns:
- token_adopt_int_p50_allv
- token_adopt_int_p50_allv_ctx
- token_adopt_int_p50_allv_ss
unit: 占比 (bank-year 内 measured 文章中落入该象限的篇数占比, ∈[0,1], 无量纲)
formula: '逐篇二值指示 1{fintech_intensity_score(INT轨,同轨变体) >= 年度P50分位阈值 AND policy_cosine_sim_allv(同轨变体) < 年度P50分位阈值}, 按 (target_bank, year) groupby mean 聚合; sim/freq 任一 NaN 的文章不计入分子分母 (measured 掩码), 全未测量 bank-year 输出 NaN (不填 0)。'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (调用点 runner.py L2069-L2090); 上游依赖 pipeline\panel\export.py 面板标签映射 (L1404-L1413)
upstream:
- 15_article_policy_alignment.parquet (policy_cosine_sim_allv 及其 _ctx/_ss 变体; fintech_intensity_score 及其 _ctx/_ss 变体)
citations:
- doi: "10.1016/j.irfa.2014.02.006"
  type: journal
  authors: "Kearney, C., & Liu, S."
  year: 2014
  title: "Textual sentiment in finance: A survey of methods and models"
  venue: "International Review of Financial Analysis"
  vol: "33"
  pages_or_artno: "171-185"
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
  vol: "31"
  issue: "1"
  pages_or_artno: "e1549"
- doi: "10.1007/s11573-017-0852-x"
  type: journal
  authors: "Gomber, P., Koch, J.-A., & Siering, M."
  year: 2017
  title: "Digital finance and FinTech: Current research and future research directions"
  venue: "Journal of Business Economics"
  vol: "87"
  issue: "5"
  pages_or_artno: "537-580"
- doi: "10.1006/jfin.2000.0282"
  type: journal
  authors: "Boot, A. W. A."
  year: 2000
  title: "Relationship banking: What do we know?"
  venue: "Journal of Financial Intermediation"
  vol: "9"
  issue: "1"
  pages_or_artno: "7-25"
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure Sentiment: Machine Learning vs. Dictionary Methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
F554 家族刻画银行—年度层面「Token Adoption」(象征性/表面化金科采纳) 的文章占比, 是 stage 15 政策对齐四象限分类体系 (`_classify_policy_quadrants`, `pipeline/panel/runner.py`) 在 INT 词频轨、P50 分位、`_allv` 全语料静态锚点下的产出。四象限体系把每篇经共现过滤并留篇的报道, 按「与权威政策文本的余弦相似度 (`policy_cosine_sim`)」和「金科词频/强度 (`fintech_distinct_keywords` KW 轨或 `fintech_intensity_score` INT 轨)」两个连续测度, 各自在年度截面内取 P25/P50/P75 分位阈值做高/低二分, 组合出三个非互斥但两两互斥于同一象限的命名指示: Token (高词频、低政策相似度)、Hidden (低词频、高政策相似度)、Substantive (高词频、高政策相似度)。第四象限 (低词频、低政策相似度, 即"未采纳/无关") 是刻意省略的基准象限 — 不单独产列, 因为它是研究者关心的三类"采纳姿态"之外的剩余类别, 其占比可由 `1 - token - hidden - subst` 在下游分析中隐式还原, 无需重复占用面板列空间。

这一构念的理论根基是组织制度主义中「象征性采纳 (symbolic/ceremonial adoption) vs 实质性采纳 (substantive adoption)」的经典区分: 组织可以在话语/文本层面高度贴合权威规范框架 (政策相似度高), 却未必伴随相应强度的实际业务语言/操作细节披露 (词频/强度低), 反之亦然。Token adoption 具体对应"高强度谈金科, 但话语框架未贴合官方政策语言"的一类报道姿态 — 即银行侧的金科相关表述活跃, 却不与监管/政策口径同频, 可理解为"自说自话式"的金科叙事密集但未与权威框架耦合; 这与 Hidden adoption ("政策语言贴合但金科词频本身不高", 更像是低调合规式的框架跟随而非高调宣传) 和 Substantive adoption (二者皆高, 话语框架与实际叙事密度同步) 构成互补的三分类光谱。该判据以 (target_bank, year) 为聚合单元, 每年独立计算分位阈值 (`groupby('year')[col].transform(quantile)`), 故阈值本身随年度分布浮动, `token_adopt_*` 系列度量的是"相对本年度截面而言"的高低组合, 而非跨年固定阈值下的绝对水平 — 这一年度内截面分位设计与家族相邻的 KW 轨、P25/P75 分位、以及非 `_allv` 的 vintage 锚点变体共享同一分类原语 `_classify_policy_quadrants`, 仅词频列/相似度列/百分位参数不同, 属于同一测度族的参数化梯子而非独立构念。

【方法学与计算】
INT 轨: 词频维使用 `fintech_intensity_score` (stage 15 产出的连续型金科强度得分, 与 KW 轨的离散去重关键词计数 `fintech_distinct_keywords` 是并排的两条词频侧稳健性分支, 二者各自产生独立的 token/hidden/subst 三元组, 互为稳健性不分主次, 不应混入同一过度识别设定)。相似度维使用 `_allv` 后缀锚点 `policy_cosine_sim_allv`, 即政策文本参照系取「全语料静态锚点」(all-vintage, 与年度滚动的 vintage 主轨 `policy_cosine_sim` 相对) — 两个锚点变体 (无后缀 vintage / `_allv` 全年份静态) 共用完全一致的 track(full/ctx/ss) × 词频(kw/int) × 分位(P25/P50/P75) 四象限构造循环, 仅相似度阈值列的锚点来源不同, 二者是同一构念在"政策文本参照系随时间演化"与"政策文本参照系固定不变"两种假设下的并排稳健性检验, 互为稳健性、不分主次, 禁止混入同一过度识别 Hansen J 设定。P50 是分位参数梯子 {25,50,75} 中的中位数切分, 相对 P25/P75 两端更保守地把样本对半分为高/低两组, 是三档分位中样本量最均衡、对极端年度分布形状最不敏感的一档, 常作为该分位梯子的默认/主要报告口径, 但 P25/P75 两档同样各自 just-identified 并排产出, 不因 P50 居中而具有事前优先性。

聚合层面, `_classify_policy_quadrants` 先对 sim 列与 freq 列分别在年度内做分位阈值变换 (`transform(lambda x: x.quantile(pct/100))`), 随后用 `high_freq = freq >= yfreq`、`high_sim = sim >= ysim` 两个布尔掩码组合出 `token = high_freq & ~high_sim`。关键的缺失值处理修复 (2026-06-11, fix(omni-g-runner-03/g-runner-11)) 是仅对 sim 与 freq 双双非缺失 (`measured = sim.notna() & freq.notna()`) 的文章行给出 0/1 指示, 其余文章的指示值显式置 NaN 而非旧实现中把测量失败误判为"低对齐/低词频"进而静默计入 Token 象限分子的错误做法 — 这一修复避免了 stage 15 优雅早退产生的全 NaN `policy_cosine_sim` 年份把全部高词频文章误伪造成 Token 采纳的系统性偏误。逐篇指示随后按 `(target_bank, year)` groupby `mean` 聚合为占比: `mean` 对 NaN 天然跳过, 故分母是该银行—年度内"sim 与 freq 均被成功测量"的文章篇数, 而非该银行—年度全部留篇篇数; 若某银行—年度全部文章均未测量 (例如政策对齐相似度整年计算失败), 面板输出 NaN 而非被 0 填充的伪零, 这与本项目 F3 缺失值红线 (Allison 2001; Heckman 1979 处理效应文献对"未测量"与"测量为零"须严格区分的一贯要求) 保持一致, 后续在面板导出阶段亦刻意删除了早期版本对该列族的 `fillna(0.0)` 逻辑, 以防止把结构性缺失误注入双向固定效应回归系数。

【文献定位】
Token adoption 所刻画的"言语框架贴合度"与"叙事密度"两维分离, 呼应了文本情感/文本分析方法论文献中对文本测度多维度、不可简单加总为单一分数的一般性提醒: Kearney and Liu (2014, *International Review of Financial Analysis*) 系统综述了金融文本情感测度方法, 强调不同文本构念 (情感极性、话题相似度、词频强度) 各自捕捉文本的不同侧面, 不应在缺乏理论支撑时随意合并; Todd, Bowden 和 Moshfeghi (2024, *Intelligent Systems in Accounting, Finance and Management*) 进一步综合了金融文本情感分析的方法演进, 指出基于余弦相似度的语义对齐测度与基于词频/关键词密度的强度测度是两类互补而非替代的文本信号来源, 这与本家族刻意把 `policy_cosine_sim` (语义对齐) 与 `fintech_intensity_score` (词频强度) 作为两条正交轴构造象限分类的设计思路一致。金科话语与权威政策语言的对齐关系本身是金融科技研究的核心问题域: Gomber, Koch 和 Siering (2017, *Journal of Business Economics*) 界定了数字金融/金融科技的研究范畴, 指出银行披露话语与技术采纳实践之间可能存在的错位, 为区分"话语层面的采纳"与"实践层面的采纳"提供了构念基础。此外, Boot (2000, *Journal of Financial Intermediation*) 对关系型银行业的经典综述强调银行对外沟通/信息披露既服务于监管合规信号传递, 又服务于业务实质的信息生产, 这一"信号传递 vs 信息生产"二分为 Token/Hidden/Substantive 三分类象限提供了银行业情境下的理论对照: Token 象限 (高词频、低政策相似度) 更贴近"业务实质叙事活跃但信号传递框架未贴合"的组合, 而 Hidden 象限则更贴近"信号传递框架贴合但业务实质叙事强度不高"的组合。词频强度类信号相较传统词典法的方法学优势另有 Frankel, Jennings & Lee (2022, Management Science) 的顶刊证据支撑: 该文系统比较机器学习分类器与词典法在披露文本情感抽取上的表现, 证明经监督学习/微调的分类模型能更准确捕捉披露文本的语义强度信号, 为本家族以 TF-IDF×SIF 加权词频 (而非简单词典命中计数) 构造词频侧信号提供了顶刊层级的方法学正当性。

【三轨/梯子铁律复述】
本家族的 full/ctx/ss 三个成员列各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一过度识别 Hansen J 设定; full 轨与 stage 21 情感留篇门控保持一致的 full-only 语义 (2026-06-29 起, 是否计入"一篇银行金科报道"的口径判定仅看 `llm_verified_full`), ctx/ss 是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集, 但每轨分子分母仍严格按各自轨道的 sim/freq 列独立计算 (不借用 full 轨分母)。ss 轨的回退语义镜像 ctx 轨: 当某篇文章在 stage 14 未探测到目标银行与金科词的同句共现窗口时, `content_ss` 回退为全文 body 且 `ss_is_fallback=True`, 该回退文章仍参与 ss 轨 sim/freq 的计算 (只要对应列非 NaN), 但其语义已退化为等价于 full 轨的窗口范围, 是"同句证据缺失时退而求其次用全文兜底"而非该文章被排除出 ss 轨分母。`_allv` 全年份静态锚点与非 `_allv` 的年度 vintage 主轨锚点同样各自 just-identified 并排、互为稳健性, 不构成主次关系。

## VAR: token_adopt_int_p50_allv

【变体差分】
本列是家族的 full 轨成员, 即三轨循环中 `_sim_sfx=''` 分支: 相似度列取 `policy_cosine_sim_allv` (全语料静态锚点, 无轨道后缀 = 基于全文标题+正文文本计算的政策对齐相似度), 词频列取 `fintech_intensity_score` 的 full 轨版本 (INT 轨基名本身即代表 full 轨, 无需额外后缀)。列名不带 `_ctx`/`_ss` 后缀是本项目"无后缀槽 = full 轨/canonical 主槽"的通用命名约定 (与三轨嵌入、三轨情感等其余家族一致), 与 P1 治理框架下 `llm_vote_tone_full` 等 full-only 主轨口径同源, 但本列本身不属于任何单一 paper 的 treatment 主轨, 而是四象限体系的 full 轨基准成员, 与 `_ctx`/`_ss` 两个孪生列并排、互为稳健性, 不因无后缀而具有事前优先地位。年度 P50 分位阈值分别对全文 `policy_cosine_sim_allv` 和全文 `fintech_intensity_score` 独立计算, 两阈值均基于该银行—年度内的全体已测量留篇文章分布, 不掺入 ctx/ss 轨的分位信息。

由于本列的文本扫描范围是留篇文章的标题+正文全文 (`content_full`, 未经实体窗口或同句窗口裁剪), 词频维 `fintech_intensity_score` 与相似度维 `policy_cosine_sim_allv` 均在最大可用文本量上计算, 相对 ctx/ss 两轨捕捉的信息更完整, 但也更可能被文章中与目标银行—金科关系无关的段落稀释信号 (例如同一篇报道中夹杂的其他银行或非金科业务叙述)。这一"信息完整但可能被稀释"与 ctx/ss 轨"信息聚焦但可能因窗口过窄而丢失语境"的权衡, 正是三轨设计"互为稳健性、不分主次"的实质动因: 若某银行—年度的 Token adoption 占比在 full/ctx/ss 三轨上方向一致 (同高或同低), 说明该结论对文本裁剪范围不敏感; 若三轨分化, 则提示分类结果对窗口选择敏感, 需要在下游分析中审慎解释, 不能仅凭 full 轨单一结果下结论。本列同时是 stage 21 情感留篇门控 full-only 口径下的行宇宙基准: 凡是被 `llm_verified_full` 判定为"确系一篇银行—金科报道"的留篇文章, 才会进入本列及其年度分位阈值计算的候选池, ctx/ss 两轨的候选池是该基准池的子集而非独立扩展。

## VAR: token_adopt_int_p50_allv_ctx

【变体差分】
本列是 ctx (实体窗口) 轨成员: 相似度列取 `policy_cosine_sim_allv_ctx`, 词频列在 `fintech_intensity_score_ctx` 存在于面板对齐表时优先使用该 ctx 轨专属词频列 (标题+实体窗口文本重新独立扫描算得), 而非借用 full 轨词频列做简单复制 — 这是 runner.py 四象限循环中 `_freq_eff` 选取逻辑 (`if f'{freq_col}{_sim_sfx}' in df_align.columns: _freq_eff = f'{freq_col}{_sim_sfx}'`) 对 int 轨 (与 kw 轨的去重关键词计数不同, 后者属 track-agnostic 元数据、无 ctx/ss 独立变体、会退回复用 full 轨列并在日志中披露) 的处理结果: fintech_intensity_score 本身具备真正独立的 ctx/ss 轨扫描 (stage 15 三轨输出), 故本列的高/低词频判据并非 full 轨的简单继承, 而是 ctx 文本 (标题+目标银行实体窗口, 由 stage 14 `content_ctx` 物化) 独立计算强度得分后再取该子样本年度分位阈值。年度分位阈值 (P50) 在 ctx 轨内部独立计算, 与 full 轨阈值数值一般不同; 分母同样仅限该银行—年度内 ctx 轨 sim 与 freq 均非缺失的文章篇数。ctx 轨是 full 轨的 conditional-on-full 稳健性轨, 行宇宙以 full 轨留篇集合为准的子集, 但象限判据本身按 ctx 轨自身连续测度独立计算, 不借用 full 轨的高/低标签。

ctx 文本窗口 (`content_ctx`, stage 14 `ctx_materializer` 物化, `prepend_title` 拼接标题) 以目标银行实体为中心截取邻近段落, 相对 full 轨裁去了与该银行不直接相关的段落, 理论上应能提高相似度与强度两个测度的信噪比: 若某篇报道同时报道多家银行或多项业务, ctx 轨的强度得分更能反映"该银行相关叙事"本身的金科词密度, 而不被无关段落稀释; 但代价是当实体窗口过窄时可能截断本应纳入的政策语言线索, 使 `policy_cosine_sim_allv_ctx` 相对 full 轨系统性偏低或偏高, 具体方向取决于该银行相关段落与政策语言的实际共现模式, 不预设先验方向。因此本列与 full/ss 两轨的差异应被解读为"文本裁剪范围假设不同下的并排稳健性检验", 而非"更准确"或"更不准确"的优劣关系; 三者在 (target_bank, year) 层面的相关系数是判断结论对窗口选择敏感度的诊断信息, 但不构成任一轨优先于另一轨的依据。

## VAR: token_adopt_int_p50_allv_ss

【变体差分】
本列是 ss (银行∧金科同句窗口) 轨成员: 相似度列取 `policy_cosine_sim_allv_ss`, 词频列同理优先取真实存在的 `fintech_intensity_score_ss` (若该列在面板对齐表缺失才按代码逻辑退回 full 轨并记录日志, 但按当前生产 schema 三轨均已上线, 实际取到的是 ss 轨专属强度得分)。ss 轨的行宇宙以银行名与金科词在同一句 (`config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1 即同句±1 句窗口) 共现为判据窗口, 由 stage 14 物化 `content_ss`; 当某篇留篇文章不满足该同句共现条件时, 依 CLAUDE.md 铁律回退为全文 body 且 `ss_is_fallback=True` (镜像 ctx 轨回退语义), 该文章仍以回退后的 sim/ss 强度值参与本列的年度分位分类与占比聚合, 并非从分母中剔除。ss 轨年度分位阈值 (P50) 在 ss 子样本内部独立计算, 与 full/ctx 两轨阈值一般不同数值; 三轨 (full/ctx/ss) 各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一过度识别 Hansen J 设定。

ss 轨是三轨中窗口范围最窄的一支: 只有当目标银行与金科词真正落在同一句 (含配置窗口半径) 时, 才用该同句片段计算相似度与强度; 一旦发生回退, ss 轨的取值在数值上与 full 轨完全一致 (因为回退后的扫描文本本身就是全文), 但其"回退"身份仍被 `ss_is_fallback` 标记保留, 供下游分析按需剔除或加权处理。这意味着本列在高共现密度的银行—年度 (同句证据丰富) 上最能体现"金科话语与政策语言是否在同一叙事单元内真正耦合"这一更严格的构念, 而在低共现密度的银行—年度上则退化为与 full 轨高度相关的冗余测度。与 KW 轨 (词频维用离散去重关键词计数、无法产出真正独立的 ctx/ss 强度变体、须复用 full 轨列) 不同, 本列所属的 INT 轨在三个文本轨道上均有独立扫描产出, 是该四象限体系中三轨差异化程度最高的一条词频分支, 这也是本 F554 家族选择以 INT 轨而非 KW 轨承载三轨敏感性分析的设计考量所在。

<!-- rendered-citations:begin -->
Kearney, C., & Liu, S. (2014). Textual sentiment in finance: A survey of methods and models. International Review of Financial Analysis, 33, 171-185. https://doi.org/10.1016/j.irfa.2014.02.006
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Boot, A. W. A. (2000). Relationship banking: What do we know?. Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure Sentiment: Machine Learning vs. Dictionary Methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
