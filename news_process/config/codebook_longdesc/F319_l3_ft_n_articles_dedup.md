---
family_id: F319
columns:
- ft_n_articles_dedup
unit: 篇 (bank-year 层面去重后的报道计数)
formula: 'ft_n_articles_dedup(target_bank, year) = df_art.groupby([target_bank, year]).size(), 其中 df_art 已在 build_non_fintech 内按复合键 (target_bank, 标题, 日期字符串) 双侧 drop_duplicates(keep=first)。fintech_share = ft_n_articles_dedup / (ft_n_articles_dedup + nf_n_articles); all_n_articles = ft_n_articles_dedup + nf_n_articles; all_ln_coverage = ln(1 + all_n_articles)。'
producer: pipeline\falsification\controls.py
upstream: []
citations:
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: 'Shift-share designs: Theory and inference'
  venue: The Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 1949-2010
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: Quasi-experimental shift-share research designs
  venue: The Review of Economic Studies
  vol: '89'
  issue: '1'
  pages_or_artno: 181-213
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: Overidentification in shift-share designs
  venue: arXiv
new_dois: []
---

## CORE

【构念与来源】
`ft_n_articles_dedup` 是 stage 51 伪造检验 (falsification test) 对照变量构建模块 `pipeline/falsification/controls.py` 内计算的一个中间/辅助计数变量, 语义为「某银行在某年度、经复合键去重后的金融科技相关新闻篇数」, 用作 fintech_share 及 all_n_articles/all_ln_coverage 等一系列衍生曝光度/覆盖度变量的分子/分母同基输入。该变量本身不是任何一篇论文的核心处理变量或结果变量, 而是伪造检验 (falsification/placebo) 环节里用来诊断"新闻计数是否反映金融科技特异性信息、还是仅反映一般媒体关注度" (H0 vs H1 假设框架) 的构造性对照量。其直接动机是修复此前版本中 fintech 计数分子与 non-fintech 计数分母"计数基不一致"的问题: 早期实现里, 面板 fintech 篇数 (`n_articles`) 是未经复合键去重的物理计数 (转载/同稿多次收录也各计一次), 而 `nf_n_articles` (non-fintech 篇数) 天然经过 `build_non_fintech` 的复合键 `(target_bank, 标题, 日期)` 双侧 `drop_duplicates` 之后计得, 二者混用会系统性夸大 fintech 一侧的相对份额。`ft_n_articles_dedup` 正是为消除这一分子/分母计数基分叉而引入的"去重同基"分子: 它取自去重后的 `df_art` (面板最终纳入的 fintech 文章集合) 按 `(target_bank, year)` 分组计数, 与 `nf_n_articles` 共享完全相同的去重口径, 从而使 `fintech_share = ft_n_articles_dedup / (ft_n_articles_dedup + nf_n_articles)` 的分子分母口径对称, 不再冒充"物理篇数 / 去重篇数"的伪比率。

【方法学与计算】
计算发生在 `build_non_fintech` 函数内: 该函数先对全量银行新闻表与面板 fintech 文章表分别按复合键 `(target_bank, 标题, _date_str)` 做双侧 `drop_duplicates(subset=_key_cols, keep='first')`, 保证"同一篇稿件在同一银行、同一标题、同一日期"只计一次, 这是 anti-join 互补划分 (non-fintech = 全量银行新闻 减去 面板 fintech 文章) 得以成立的前提。去重后的 `df_art` 再按 `groupby(['target_bank', 'year']).size()` 聚合, 结果命名为 `ft_n_articles_dedup`, 并通过 pandas `DataFrame.attrs['ft_dedup_agg']` 这一非列式通道从 `build_non_fintech` 传递给下游 `merge_to_panel`。在 `merge_to_panel` 里, 若 `ft_dedup_agg` 可用 (`_has_dedup=True`), 面板原有的 `ft_n_articles_dedup` 列 (若存在) 先被丢弃, 再以 `(target_bank, year)` 左连接方式合并进面板, 缺失值填 0; 该列随即被用作 `_ft_count`, 驱动 `all_n_articles = _ft_count + nf_n_articles`、`all_ln_coverage = ln(1 + all_n_articles)`、`fintech_share = _ft_count / all_n_articles` (分母为 0 时置 NaN, 由 `zero_coverage` 标记, 不冒充 0 份额) 等一整族衍生变量。模块内还嵌有一条构造性不变量的运行时断言: 去重后的 `ft_n_articles_dedup` 逐行不应超过面板物理计数 `n_articles` (后者来自 stage 45 聚合、未经复合键去重), 若违反则判定为 merge 键错位或上游计数源分叉并终止流程, 这一硬契约保证了 `ft_n_articles_dedup` 与物理计数之间的可审计一致性。若 `ft_dedup_agg` 缺失 (例如上游 `build_non_fintech` 未被调用或 attrs 丢失), 代码会优雅降级、回退到用面板物理 `n_articles` 充当分子, 并记录警告日志说明本次运行处于回退口径, 而非静默产出错误结果。

【文献定位】
需要首先明确本变量的边界: `ft_n_articles_dedup` 本身不涉及 full/ctx/ss 三轨切分, 不涉及情感 LLM 三家投票或 co-primary 嵌入双轨, 也不构成任何消融/权重/阈值梯子, 它是纯计数层面 (基于标题+日期+银行复合键去重) 的辅助对照变量, 不受留篇门控 full-only 口径 (2026-06-29) 直接约束——它统计的是"文章是否存在于面板", 而非情感/属性判定是否 `llm_verified_full`。就该变量所服务的伪造检验/占位对照设计而言, 其角色贴近计量经济学中"构造对照分母以隔离处理变量特异性信息增量"的一般性思路——检验金融科技新闻计数的解释力是否仅仅来自一般媒体关注度这一混杂路径 (H0), 还是携带超出一般关注度之外的金融科技特异性增量信息 (H1)。这一"共同支撑/共同分母"式的构造要求 (`ft_n_articles_dedup` 与 `nf_n_articles` 必须共享同一复合键、同一去重口径, 否则分子分母不同基会人为夸大或压低份额), 与 shift-share/Bartik 类工具变量文献中强调份额 (share) 与位移 (shift) 需分别来自可比、同基础构造集合以避免机械关联的方法论关切, 存在有限但可辨识的类比关系, 仅作方法论参照而非直接适用: Adão, Kolesár & Morales (2019, *QJE*) 指出, 当构造性分母/权重集合口径不一致时, 由此派生的统计量可能反映的是构造性机械关系而非真实经济信号; Borusyak, Hull & Jaravel (2022, *Review of Economic Studies*) 进一步区分了"份额稳健性"与"位移外生性"两条独立可检验的识别假设, 强调二者不应被混为一谈; Hahn, Kuersteiner, Santos & Willigrod (2024) 则指出多个共享同一构造基础的派生统计量若被混入同一识别方程 (over-identified 设定) 会引入不应有的相关性, 应各自 just-identified 并排检验而非合并进单一 Hansen J 检验。本项目在跨轨道/跨梯子测度 (三轨 full/ctx/ss、co-primary 双轨嵌入、消融/权重/阈值/判据梯子、per-model 稳健性族) 上同样反复强调"各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J" 这一操作铁律, 二者关切的是同一类"避免共享构造成分导致虚假识别力度"的问题, 但适用对象不同——`ft_n_articles_dedup` 是伪造检验的辅助计数分子, 并非该铁律直接约束的梯子/轨道变量, 此处引用三篇文献仅为方法论参照, 不代表 `ft_n_articles_dedup` 本身是 shift-share 设计或 IV 权重构造。

## VAR: ft_n_articles_dedup

【变体差分】
本列是家族内唯一列, tier=standard, 不存在同家族内的轨道/模型/阈值/判据/权重/滞后差分变体——`ft_n_articles_dedup` 只有一个口径: 按 `(target_bank, 标题, _date_str)` 复合键双侧 `drop_duplicates(keep='first')` 后, 对 `(target_bank, year)` 分组计数得到的金融科技新闻篇数。它与紧邻但语义不同的两个计数变量需要严格区分, 这正是该列在面板中的"精确定位": 其一, 与面板物理列 `n_articles` (源自 stage 45 聚合、未经复合键去重, 转载/同稿多次收录会重复计入) 不同——`ft_n_articles_dedup` 恒小于或等于 `n_articles`, 二者之差 (`n_articles - ft_n_articles_dedup`) 在模块内被记录为"跨源一致性诊断"下的收缩量, 用于量化去重造成的篇数收缩幅度; 该差值不应被误读为数据丢失或缺陷, 而是复合键去重按设计剔除的转载/重复稿件。其二, 与 `nf_n_articles` (non-fintech 篇数) 共享完全相同的去重口径 (同一复合键、同一去重函数调用序列), 这是本列被专门构造出来的唯一原因——若直接用物理 `n_articles` 作分子、`nf_n_articles` 作分母, 二者计数基不一致会人为夸大或压低 `fintech_share`, `ft_n_articles_dedup` 的存在正是为堵住这一口径漏洞。下游消费该列的场景集中于三处: (1) 直接决定 `fintech_share` 的分子, 分母为 0 (即 `all_n_articles==0`) 时 `fintech_share` 置 NaN 并由 `zero_coverage` 指示列标记, 不冒充 0 份额; (2) 参与 `all_n_articles`/`all_ln_coverage`/`ln_ft_articles` 的构造, 后者是 `ln(1 + ft_n_articles_dedup)` 式对数覆盖度变量, 与 `ln_nf_articles` 构成挤出弹性诊断对 (阈值三档: r<-0.95 机械约束、[-0.95,-0.50) 中等负相关警告、≥-0.50 非机械关联); (3) 作为跨源一致性校验的左端(逐行不超过 `n_articles`), 该断言若失败会直接终止流程而非静默容忍, 是本列区别于家族内(虽为单列家族但概念上邻近的) 物理计数变量的核心质量保证边界。若上游 `build_non_fintech` 未产出 `ft_dedup_agg` (attrs 通道缺失), 本列在 `merge_to_panel` 内的取值会整体回退为面板物理 `n_articles`, 此时 `fintech_share`/`all_n_articles` 等下游变量随之切换为"回退口径", 日志会显式记录这一降级路径, 不构成静默口径漂移。

<!-- rendered-citations:begin -->
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
<!-- rendered-citations:end -->
