---
family_id: F517
columns:
- subst_adopt_int_p75_allv
- subst_adopt_int_p75_allv_ctx
- subst_adopt_int_p75_allv_ss
unit: 银行-年内已测量文章占比 (0-1 无量纲比率)
formula: 'subst_adopt_int_p75_allv{_ctx,_ss} = mean_over_articles( 1{fintech_intensity_score{trk} >= Q75_year(fintech_intensity_score{trk})} AND 1{policy_cosine_sim_allv{trk} >= Q75_year(policy_cosine_sim_allv{trk})} ), 分母=该银行-年内 sim 与 freq 双双非缺失的文章数; sim/freq 任一缺失的文章 NaN 掩码剔除 (不计入分子亦不计入分母), 全年不可测则该银行-年输出 NaN'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (逐篇分类) + 同文件 7h 四象限聚合区块 (L1997-L2089, groupby(target_bank, year).mean)
upstream: pipeline\filtering\fintech_intensity.py (stage 15, 产 fintech_intensity_score{,_ctx,_ss}); pipeline\filtering\policy_alignment.py (stage 16, 产 policy_cosine_sim_allv{,_ctx,_ss}); pipeline\text\ctx_materializer.py (stage 14, 产 content_ctx/content_ss)
citations:
- doi: '10.2307/2393295'
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: Substance and Symbolism in CEOs' Long-Term Incentive Plans
  venue: Administrative Science Quarterly
  vol: '39'
  issue: '3'
  pages_or_artno: 367-390
- doi: '10.5465/amj.2006.23478255'
  type: journal
  authors: Fiss, P. C., & Zajac, E. J.
  year: 2006
  title: The Symbolic Management of Strategic Change Sensegiving via Framing and Decoupling
  venue: Academy of Management Journal
  vol: '49'
  issue: '6'
  pages_or_artno: 1173-1193
- doi: '10.1111/jofi.13412'
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution'
  venue: The Journal of Finance
- doi: '10.1016/j.jbankfin.2024.107191'
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk
  venue: Journal of Banking & Finance
  vol: '164'
  pages_or_artno: '107191'
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (`subst_adopt_int_p75_allv`/`_ctx`/`_ss`) 度量的是「实质性金融科技采纳」(substantive fintech adoption) 在银行-年层面的占比, 其构念根柢是组织行为与战略管理文献中的 substance-symbolic (实质-象征) 区分传统: Westphal & Zajac (1994, ASQ) 首先指出企业对外披露的行动纲领存在「宣示」与「践行」的分野, 组织可能只在文本/沟通层面表态 (symbolic decoupling) 而不伴随实际资源投入, 也可能表里如一地把纲领落到具体行为上 (substantive adoption); Fiss & Zajac (2006, AMJ) 进一步把这种象征性管理的框架 (framing) 与解耦 (decoupling) 机制模型化, 为文本测度提供了「口径-行为」二维分类学。本项目把这套分类学移植到中国银行业金融科技报道语料上: 每篇报道被放进一张二维象限图里, 纵轴是「该报道谈金融科技谈得有多深/多密」(词频/强度侧), 横轴是「该报道的具体行动描述与官方政策文本有多像」(政策对齐侧); 落入「双高」象限 (词频高 且 政策相似度高) 的报道被判定为 subst(实质采纳)信号, 只有词频高但相似度低的是 token(象征性/口号式), 只有相似度高但词频低的是 hidden(低调务实), 两者皆低是 irrelevant。`subst_adopt_int_p75_allv` 系列即是「双高」象限里, 频率侧取 Track B — 连续型 `fintech_intensity_score` (而非离散关键词计数 Track A `fintech_distinct_keywords`), 相似度侧取 P75 (银行-年内最严苛的四分位阈值), 且相似度锚点取 `_allv` (全年份/全语料静态锚点) 变体, 在该银行-年全部已测量文章中所占的比例。

【方法学与计算】
producer 侧的分类原语是 `pipeline/panel/runner.py::_classify_policy_quadrants`: 对每个 (sim_col, freq_col, pct) 三元组, 先按年份分组计算 `freq_col`/`sim_col` 的 P75 分位阈值 (`groupby('year').transform(quantile)`), 再逐篇比较, 输出 token/hidden/subst 三个 0/1 浮点指示列; 该函数的关键设计是「NaN 掩码而非 NaN 归零」: sim 或 freq 任一缺失的文章不参与分类比较 (`.where(measured)` 把未测量行显式置 NaN), 这是 2026-06-11 修复 (omni-g-runner-03/g-runner-11) 后的契约 — 旧实现会把 stage 15 三条优雅早退路径写出的全 NaN `policy_cosine_sim` 误判成「相似度低」从而把所有高词频文章错误批量归入 token 象限, 制造虚假的象征性采纳信号。修复后, 分类指示列经 `groupby(['target_bank','year']).mean()` 聚合为占比: `mean` 天然跳过 NaN, 分母是该银行-年「sim 与 freq 双双非缺失」的已测量文章数, 而非该银行-年全部报道数; 若某银行-年一篇可测量文章都没有, 输出为 NaN (面板契约: 未测量 ≠ 零, 详见 Allison 2001 §3 关于强填零污染 TWFE 系数的论证, runner.py 注释亦明确引用)。频率侧 `fintech_intensity_score` 与相似度侧 `policy_cosine_sim_allv` 均来自上游 stage 15/16 (`article_policy_alignment.py`), 前者 (`fintech_intensity_score`) 是逐篇金融科技语义强度连续打分, 其计算是确定性的 TF-IDF/IDF 加权关键词向量质心口径, 与 stage 21 情感三家 LLM 投票是两套完全不相关的机制 (CLAUDE.md「嵌入≠LLM」铁律): 打分公式对文章内出现的每个金融科技关键词取双重对数词频权重 (1+lnTF)/(1+lnL), 再乘以该词的 IDF 权重与该词嵌入向量同「金融科技语义质心」的缩放余弦相似度 W_i=IDF×CosSim_scaled 加总而成, 全程不调用任何大语言模型接口, 仅借用词向量嵌入空间来度量关键词与金融科技语义质心的贴近程度、以此充当权重, 学术上借鉴的是 Arora, Liang & Ma (2017) 对句向量做加权词向量平均的思路与 Ethayarajh (2019) 对上下文嵌入各向异性的讨论, 底层加权词频框架则可追溯到 Singhal, Buckley & Mitra (1996) 经典的 TF-IDF 加权检索模型, 以及 Manning, Raghavan & Schütze (2008) 对 IDF 权重的标准形式化; Li, Mai, Shen & Yan (2021, *Review of Financial Studies*) 是本项目在金融文本领域采用嵌入构造语义强度测度的直接方法学参照。后者 (`policy_cosine_sim_allv`) 是该篇文章嵌入向量与「政策锚点」文本嵌入的余弦相似度, 同样是嵌入空间内的确定性几何计算, 不涉及 LLM 打分或标注。`_allv` 后缀标记锚点变体: 主轨 (无 `_allv`) 用「vintage 锚点」——按报道所在年份匹配同期政策文本构建的锚点, 随时间演化; `_allv` 是其稳健性孪生, 用「全年份静态锚点」——把全部年份的政策语料汇总构建一个不随年份变化的固定锚点, 消除锚点本身跨年漂移对相似度比较基准的干扰。两个锚点变体在完全相同的 track(full/ctx/ss) × 频率轨(kw/int) × 分位(P25/P50/P75) 网格上并行产出, 互为稳健性检验, 不设主次, 禁止把 vintage 与 allv 两套锚点产出的 subst_adopt 列混入同一 over-identified 的 Hansen J 检验 (二者共享同一组银行-年观测单位, 混用会人为夸大过识别约束数目而破坏检验的渐近性质)。三列后缀对应 CLAUDE.md「三轨文本架构」铁律: 无后缀=full(标题+全文), `_ctx`=标题+实体窗口, `_ss`=标题+银行∧金科同句±N窗; 三轨的 sim/freq 输入列均取各自轨道的同名变体 (如 `policy_cosine_sim_allv_ctx`/`fintech_intensity_score_ctx`), 缺列则优雅跳过 (旧 schema 兼容), 三轨彼此 just-identified 并排、互为稳健性, 同样禁止混入同一 Hansen J。留篇口径遵循 2026-06-29 全量切换的 full-only 门控: 是否算作「一篇可纳入分析的银行金科报道」只看 `llm_verified_full`, ctx/ss 是在该留篇集合子集上的条件测度, 而非独立的留篇判定。

【文献定位】
本家族测度直接服务于 P3 (`bank_fintech_substance`) 论文, 该论文的核心研究设计正是借用 Westphal & Zajac (1994) 与 Fiss & Zajac (2006) 建立的实质-象征二分法, 检验中国银行业媒体报道中「谈金融科技」与「真做金融科技」的分离程度及其经济后果。方法学脉络上, 用文本相似度锚点度量「言行对齐」的做法呼应了近年气候/ESG 披露文献中「cheap talk」测度传统: Bingler, Kraus, Leippold & Webersinke (2024, *Journal of Banking & Finance*) 用文本模型检验企业气候披露与实际排放/倡议之间的脱耦程度, 与本处「报道语言强度 vs. 政策文本相似度」四象限逻辑同构; Duchin, Gao & Xu (2025, *The Journal of Finance*) 则在可持续性/漂绿情境下提供了「披露-行动」错配的资产定价证据, 是本家族分类学在金融顶刊语境下的方法学参照。频率侧 Track B 取连续型嵌入加权强度打分而非离散关键词计数, 其合理性建立在文本即数据 (text-as-data) 与嵌入空间连续测度文献之上: TF-IDF/IDF 加权关键词质心打分是一套确定性算法, 不依赖任何大语言模型调用 (与 stage 21 情感三家 LLM 投票是两套不相关机制), 其连续打分相较离散 0/1 关键词计数的优势在于能区分「浅提一句」与「通篇高强度讨论」两类文章之间的强度梯度, 这一思路与 Li, Mai, Shen & Yan (2021, *Review of Financial Studies*) 用词嵌入构造金融文本连续测度的方法学取向一致, 后者同样是本项目以嵌入衍生的强度分数替代二元关键词表的正当性来源。

## VAR: subst_adopt_int_p75_allv

【变体差分】
本列是家族的 full 轨: 频率侧 `fintech_intensity_score` (无后缀, 标题+全文范围逐篇强度打分)、相似度侧 `policy_cosine_sim_allv` (无后缀, 同样在标题+全文文本上计算, 政策锚点取全年份静态锚点) 均取 full 文本轨道, P75 意味着只有当一篇报道在该银行-年内金融科技强度打分排进后 25% (即 ≥ 年度 P75 分位) 且政策相似度也排进后 25% 时才被计入 subst(实质采纳)分子; 阈值 P75 相较家族梯子中的 P25/P50 是最严格的门槛, 刻画的是「高强度且高政策对齐」的重叠尾部, 因此该列的样本占比在实证上通常显著低于 P25/P50 版本, 更适合用作稳健性梯子中的「严格识别」端点, 而非首要 headline 测度 (P25/P50/P75 三档同样各自 just-identified、互为稳健性、不设主次, 禁止混入同一 Hansen J)。作为 full 轨, 其留篇口径与 P1 主线的 `llm_verified_full` 门控完全一致, 是该家族三轨中样本量最大、分母最稳定的一支, 也是三轨横向比较时的基准锚点。全年份静态锚点 (`_allv`) 相较主轨 vintage 锚点的差异在于: 全年份锚点把不同年份的政策文本汇总构建一次性锚点, 相似度比较不受政策文本本身跨年演变的影响, 因而更适合捕捉「银行报道内容与长期一贯政策导向的稳定对齐度」, 而非某一年份特定政策热点带来的短期相似度波动; 两个锚点版本的差异本身即是稳健性证据的一部分, 而非孰优孰劣的取舍。

## VAR: subst_adopt_int_p75_allv_ctx

【变体差分】
本列是家族的 ctx 轨: 频率侧改用 `fintech_intensity_score_ctx` (标题+实体窗口范围内计算的强度打分), 相似度侧改用 `policy_cosine_sim_allv_ctx` (同一实体窗口文本与全年份静态政策锚点的余弦相似度); ctx 轨把扫描范围从全文收窄到目标实体 (银行/金融科技词) 周边的局部窗口, 目的是降低无关段落 (如版面其他新闻要素、无关背景介绍) 对强度打分和相似度计算的稀释效应, 使测度更贴近「文章真正在谈论目标银行的金融科技行动」这一段落, 而非整篇文章的平均水平。与 full 轨相同, 分类逻辑、P75 阈值口径、`_allv` 锚点定义完全一致, 唯一差分是频率与相似度两个输入源的文本范围; 若某篇文章缺少 ctx 轨的同名变体列 (旧 schema 或该文章无法界定实体窗口), producer 侧优雅跳过该文章的 ctx 分类 (不借用 full 轨顶替, 保持轨道纯净)。留篇口径上, ctx 轨的行宇宙是 full 留篇集合 (`llm_verified_full == True`) 的子集, 即先用 full 轨判定「这是不是一篇该纳入分析的银行金科报道」, 再在该子集内条件性地计算 ctx 轨测度, ctx 轨本身不参与是否留篇的判定; 与 full 轨、ss 轨互为稳健性并排, 禁止混入同一 Hansen J。经济含义上, 若某银行-年在 ctx 轨上的实质采纳占比明显低于 full 轨, 提示该银行的高强度金融科技措辞更多散落在文章的背景铺陈段落而非围绕该银行本身的核心叙述里, 是一种「话题相关但非本行主体行动」的信号分离; 反之若 ctx 与 full 高度一致, 则说明强度与政策相似度信号在实体窗口内外都稳定, 对采纳判定的稳健性提供额外支撑。

## VAR: subst_adopt_int_p75_allv_ss

【变体差分】
本列是家族的 ss 轨: 频率侧改用 `fintech_intensity_score_ss`, 相似度侧改用 `policy_cosine_sim_allv_ss`, 两者均取「标题+银行∧金科同句 (±N 句窗, 默认 N=1)」的最窄文本范围; 这是三轨中判据最严格的一支, 只有在同一句 (或紧邻句窗) 里银行实体与金融科技词同时出现的片段才纳入强度与相似度计算, 用来检验「实质采纳」信号是否在最贴近的共现证据上依然成立, 而非被全文或实体窗口层面的宽松匹配稀释。ss 轨的回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现 (`ss_is_fallback=True`), 则该文章的 `content_ss` 退化为全文 body, 此时其 ss 轨的强度/相似度计算实际上落回全文口径, 与 full 轨共享同一 `n_articles` 分母, 但列名与判定逻辑仍标记为 ss 轨 (由上游 `fintech_intensity_score_ss`/`policy_cosine_sim_allv_ss` 列自身携带该回退信息, 本家族聚合层不做二次特判); 若上游 `FINTECH_AC=None` (金融科技词典未加载), 则 `*_is_fallback` 全 True, 全部退化为全文口径的优雅降级。行宇宙同样是 full 留篇集合的子集, P75 阈值与 `_allv` 锚点定义与另外两轨严格一致, 三轨在此家族内属规格稳健性并排关系, 互不作为彼此的替代或主测度, 亦不混入同一 Hansen J 过识别检验。经济解读上, ss 轨的高实质采纳占比是三轨中证据强度最高的信号: 银行与金融科技词同句共现且强度/相似度双双过 P75 分位, 意味着该句本身就在描述一项具体、可辨识的金融科技行动而非泛泛提及, 是判定「实质而非象征」最不容置疑的一档; 但受限于同句共现本身样本量偏小 (尤其在 T=2 开发数据上), 该轨占比的估计精度通常弱于 full/ctx 两轨, 解读时须结合已测量篇数分母一并考量。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Fiss, P. C., & Zajac, E. J. (2006). The Symbolic Management of Strategic Change Sensegiving via Framing and Decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or Greenwashing: Evidence from the Asset Market for Industrial Pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How Cheap Talk in Climate Disclosures Relates to Climate Initiatives, Corporate Emissions, and Reputation Risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
<!-- rendered-citations:end -->
