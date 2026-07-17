---
family_id: F411
columns:
  - log_sent_ctx
  - log_sent_full
  - log_sent_ss
unit: 对数差分得分 (无量纲, 可正可负, 覆盖门控下可为 NaN)
formula: "log_sent{track} = log1p(pos_count{track}) - log1p(neg_count{track}); full 轨 n_articles==0 → NaN; ctx/ss 轨 n_articles_llm_valid_{track}==0 → NaN (_gated_log_sent 覆盖门控, F5 2026-07-16 per-track 有效票分母; 不与'1正1负均衡'的真实测量0混淆)"
producer: news_process/pipeline/panel/runner.py::_gated_log_sent (调用点 runner.py 步骤8c, 面板导出阶段)
upstream:
  - 21_tone_llms.parquet (llm_sentiment_* 逐篇情感判定 → 面板层聚合 pos_count/neg_count)
  - 40_panel_export_main (balance_panel 零填契约; full 轨 n_articles / ctx·ss 轨 n_articles_llm_valid_{track} 覆盖门控依据)
citations:
- doi: 10.1093/qje/qjad054
  type: journal
  authors: Chen, J., & Roth, J.
  year: 2024
  title: "Logs with zeros? Some problems and solutions"
  venue: Quarterly Journal of Economics
  vol: 139
  issue: 2
  pages_or_artno: 891-936
- doi: 10.1016/j.jfineco.2024.103957
  type: journal
  authors: Vives, X., & Ye, Z.
  year: 2025
  title: "Information technology and lender competition"
  venue: Journal of Financial Economics
  vol: 163
  pages_or_artno: Article 103957
- doi: 10.1016/j.jmoneco.2022.04.001
  type: journal
  authors: Pierri, N., & Timmer, Y.
  year: 2022
  title: "The importance of technology in banking during a crisis"
  venue: Journal of Monetary Economics
  vol: 128
  pages_or_artno: 88-104
- doi: "10.1111/abac.70024"
  type: "journal"
  authors: "Cho, M., & Choi, A."
  year: 2025
  title: "Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone?"
  venue: "Abacus"
  pages_or_artno: "abac.70024"
- doi: "10.1111/ablj.12239"
  type: "journal"
  authors: "Tucker, A. M., Xia, Y., & Smelcer, S. N."
  year: 2024
  title: "Text, tone, and legal language: Analyzing mutual fund disclosure sentiment"
  venue: "American Business Law Journal"
  vol: "61"
  issue: "1"
  pages_or_artno: "57-86"
new_dois: []
---

## CORE

【构念与来源】

log_sent 家族刻画银行-年层面新闻情感的"对数降噪定向净情感"强度, 是面板导出阶段 (`pipeline/panel/runner.py` 步骤 8c) 在情感计数列基础上派生的二次指标, 而非某个情感引擎的直接输出。其构念定位是: 用计数(count)而非比率(ratio)或均值(mean)来刻画媒体情感强度, 同时用对数变换压缩计数分布的右偏尾部, 使得极端高报道量的银行-年不会以线性尺度主导跨行比较。计算链路上, 家族的直接上游是 `pos_count{track}` 与 `neg_count{track}` 两个面板计数列 —— 二者本身是 stage 21 `tone_llms.py` 三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 多数投票情感共识 (`llm_sentiment_*`) 在面板导出层按 bank-year-track 分组统计出的正面/负面篇数, 属于面板导出层 (`40_panel_export_main` 前置的聚合步骤) 而非某一情感引擎自身的列。log_sent 处于计数聚合之后、比率化之前的中间地带: 它既不是像 `frac_pos`/`frac_neg` 那样的占比指标, 也不是像 `llm_vote_tone` 那样的逐篇均值指标, 而是把正负计数分别做 log(1+x) 变换后相减, 兼具"计数强度"与"方向"两种信息。

【方法学与计算】

具体公式为 log_sent{track} = log1p(pos_count{track}) − log1p(neg_count{track}), 其中 log1p(x) = log(1+x) 是标准的"加一对数"变换, 用于处理计数变量里大量的零值 (若直接取 log(x), 零计数会产生 −∞ 或未定义)。该变换在计量文献中被称为对数降噪 (log-transformed count): 用计数的对数差而非原始计数差或比率, 既保留了"篇数越多、信号越强"的单调性, 又通过对数压缩使得从 1 篇增至 2 篇与从 100 篇增至 200 篇具有相近的边际权重, 避免报道量极端不均衡的银行-年主导回归结果。这一构造选择本身在计量方法论上并非没有争议: Chen & Roth (2024, *Quarterly Journal of Economics*) 系统指出, log(1+x) 类变换在存在大量零值时会引入非线性的解释力偏误, 系数不再具有"百分比变化"的直观解释, 且对加一常数的选择本身是任意的, 在样本零值占比高、跨组零值比例不同时尤为敏感。log_sent 家族在设计上意识到这一局限, 并做了一项关键的覆盖门控修正: `_gated_log_sent` 函数并非对全部 bank-year 无条件套用 log1p 差分公式, 而是先检查 `n_articles` 列 —— 若某 bank-year 在该轨道下全年零报道 (n_articles==0), 则不论 pos_count/neg_count 经零填后计算出什么数值, 一律强制置为 NaN, 而非任由计数列在 `balance_panel` 零填契约下退化为 pos_count=neg_count=0、进而 log_sent 恒等于 0。这一门控的动机是: 全年无报道的银行-年在情感测量意义上是"不可测" (missing), 而非"情感中性" (measured zero) —— 二者若都编码为 0.0, 会把相当一部分零覆盖行错误地混入"1篇正面1篇负面完全抵消"的真实中性观测, 系统性压低方差并污染下游估计 (零覆盖行占比随样本口径与年份窗口浮动, 以当次面板实测为准, 本文不手填具体数值)。该门控逻辑与同一面板导出模块内 `jf_coefficient` (Janis-Fadner 系数)、`concern_score`、`disag` (分歧度) 等同族情感强度指标共享同一条 F3 红线纪律 (依据 Allison 2001 与 Heckman 1979 关于缺失数据不应被当作观测零处理的经典论述), log_sent 是该纪律里最后一个补齐门控的指标 (2026-06-11 修复, omni-g-runner-06/-15)。2026-07-16 (F5) 进一步把 ctx/ss 轨门控从共享的 n_articles 收紧为轨道专属有效票计数 n_articles_llm_valid_{track} —— "有覆盖但该轨 LLM 全部无效"的银行-年此前仍会输出伪中性 0.0 (盘上实测 ctx 15 行/ss 11 行), 与同族 jf_coefficient 的 per-track 分母对齐后一并置 NaN; full 轨保留物理分母 (full-only 留篇口径下与有效票计数经验恒等, dev 实测 0 行不等)。

【文献定位】

log_sent 家族的方法论谱系交汇两条文献线: 一是计数类情感/关注度指标的对数变换传统, 本仓库 `pipeline/falsification/controls.py` 非金融科技对照变量 `nf_ln_coverage` 的媒体覆盖度 log(1+count) 构造亦沿用同一对数降噪思路但服务不同构念; 二是关于该类变换本身局限性的方法论批评线 (Chen & Roth 2024 *QJE* 对 log(1+x) 估计量非线性偏误的系统性揭示)。在银行科技新闻情感的具体应用场景下, log_sent 的现实合理性还须放在金融科技如何改变银行间信息与竞争环境的背景下理解: Vives & Ye (2025, *Journal of Financial Economics*) 指出信息技术采纳会重塑放贷者之间的竞争强度与信息优势分布, Pierri & Timmer (2022, *Journal of Monetary Economics*) 发现银行技术禀赋在危机期间对经营表现具有异质性影响 —— 这两支文献共同提示, 媒体情感计数的对数差分若不做覆盖门控, 可能把技术禀赋差异导致的报道量差异错误地折算进"情感水平"的跨行比较里, 这正是本家族在 2026-06-11 引入门控修正、并在三轨并行设计中刻意保留每轨各自零覆盖判定的方法论初衷。 就“报道量与语调分列建模”这一范式的近期存在性而言, Cho 与 Choi (2025) 在 *Abacus* 的研究把客户公司的媒体报道量与报道语调作为两个并列的公司-年媒体变量, 用以解释审计师的劳动投入配置, 与本项目把报道篇数 (ln_ft_articles/ln_nf_articles) 与语调 (log_sent) 分列为两族指标的分工同构; 惟原文语调为正负词占比类构造、层级为 firm-year, 未涉及本家族的对数差分形式与覆盖门控, 故仅锚定该建模范式的存在性。就正负词计数底盘而言, Tucker、Xia 与 Smelcer (2024) 在 *American Business Law Journal* 自建定制词典, 对 164,602 份基金简明招募说明书 (2010-2020) 生成句级与文档级语调分数, 并显式分析法律语言在设定整体披露语调中的作用, 说明以正负词计数为底盘的语调构造在大规模披露文本上可行且具研究价值, 与 log_sent 所消费的 pos_count/neg_count 同源; 迁移边界在于原文为英文共同基金披露文件、语调未采用 log1p(pos) - log1p(neg) 的对数差分形式, 亦无三轨设计与银行-年聚合, 更无本家族的零覆盖 NaN 门控。
【三轨口径说明】

log_sent 家族严格遵循本仓库三轨架构: `log_sent_full` 基于全文轨 (标题+全文正文) 的 pos_count_full/neg_count_full, `log_sent_ctx` 基于实体窗轨 (标题+目标银行句±窗口, Hassan et al. 2019 QJE proximity 范式) 的 pos_count_ctx/neg_count_ctx, `log_sent_ss` 基于银行+金科同句轨 (标题+同句同时含目标银行与金科词的片段±窗口, 无共现则镜像 ctx 回退全文 body 且 `ss_is_fallback=True`) 的 pos_count_ss/neg_count_ss。三轨的覆盖门控判据自 2026-07-16 (F5) 起分轨: full 轨用物理篇数 `n_articles` (full-only 留篇口径的直接产物), ctx/ss 轨用轨道专属有效票计数 `n_articles_llm_valid_{track}` —— 三轨虽共享同一批留篇文章 (conditional-on-full), 但各轨 LLM 判定可独立失败, "有覆盖但该轨全部无效"的银行-年在 ctx/ss 轨属不可测 (NaN) 而非中性 0。三轨各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验框架; 下游若同时纳入 full/ctx/ss 三轨 log_sent 作为同一构念的多重测量代入单一工具变量方程, 属于方法论误用。

## VAR: log_sent_ctx

【变体差分】

log_sent_ctx 是 log_sent 家族在实体窗轨 (ctx) 上的实现, 公式为 log1p(pos_count_ctx) − log1p(neg_count_ctx), 覆盖门控以轨道专属有效票计数 `n_articles_llm_valid_ctx` 判定 (F5 2026-07-16; 此前误用全文轨 n_articles, 致"有覆盖但 ctx 轨全部无效"的银行-年被注入伪中性 0.0): 该 bank-year 在 ctx 轨无任何有效票时置 NaN, 否则按零填后的 pos_count_ctx/neg_count_ctx 计算。ctx 轨的正负计数来自 stage 21 `tone_llms.py` 对 `content_ctx` (标题 + 含目标银行句 ±窗口, 窗口大小遵循 Hassan et al. 2019 QJE 提出的 proximity 范式, 即只取与目标实体在文本邻近度意义上相关的片段) 的三家 LLM 情感判定多数投票结果, 在面板层按 bank-year 分组求和。与 log_sent_full 相比, ctx 轨的输入文本更聚焦于目标银行被直接提及的语境, 理论上应过滤掉全文轨中与目标银行关系疏远的段落所贡献的情感噪声, 代价是当银行在文章中被提及次数少、窗口覆盖不全时可能损失部分真实相关的情感信息。需特别注意: ctx 轨在留篇门控 (是否判定为"一篇有效银行金科报道") 上处于 conditional-on-full 地位 (2026-06-29 全文轨门控决策) —— 即 verified_full 决定该篇文章是否进入面板宇宙, ctx 轨只负责该文章在 ctx 语境下的情感极性判定, 不参与是否留篇的决策; 因此 log_sent_ctx 的文章宇宙与 log_sent_full 一致 (conditional-on-full), 但其覆盖门控分母是 ctx 轨自身的有效票计数 (可小于 full 轨物理篇数), 有效票为零的行按不可测处理。log_sent_ctx 与 log_sent_full、log_sent_ss 互为稳健性并排测度, 不分主次, 三者各自 just-identified, 严禁混入同一 over-identified Hansen J 框架。当某银行在全年内虽有报道但目标银行从未出现在可窗口化的邻近句中 (即 ctx 轨情感计数全部退化为对应回退语义) 时, log_sent_ctx 数值上可能与 log_sent_full 高度趋同, 这是三轨设计允许的正常表现, 而非计算错误。

## VAR: log_sent_full

【变体差分】

log_sent_full 是 log_sent 家族的全文轨实现, 也是三轨中输入文本覆盖面最广的一支: 其正负计数 pos_count_full/neg_count_full 来自 stage 21 `tone_llms.py` 对 `content_full` (标题 + 全文正文, 不做任何窗口截断) 的三家 LLM (`gpt54nano`/`gemini31`/`deepseekv4`) 情感多数投票结果, 按 bank-year 分组求和后, 在面板导出层经 log_sent_full = log1p(pos_count_full) − log1p(neg_count_full) 计算, 并同样受 `n_articles==0 → NaN` 的覆盖门控约束 (F5 2026-07-16 后 full 轨保留该物理分母门控; ctx/ss 轨改用轨道专属有效票分母)。全文轨是本仓库 full-only 留篇门控 (2026-06-29 决策) 的直接锚点 —— 是否判定某篇文章为"一篇有效的银行金科报道"完全由 `llm_verified_full` 决定, 因此 log_sent_full 所依赖的 pos_count_full/neg_count_full 分母行集就是留篇门控本身的产物, 与 ctx/ss 两条 conditional-on-full 稳健轨相比, full 轨在"这篇文章算不算数"这一层面拥有最高的权威性。在多数 P1 主线分析中 (`bank_fintech_tone` 的主处理变量 `llm_vote_tone_full`), 全文轨情感被作为 canonical 口径对待, 但这不意味着 log_sent_full 本身是家族内唯一"正确"的对数降噪情感测度 —— log_sent_full 与 log_sent_ctx、log_sent_ss 依然是并排的互为稳健性测度, 三者各自 just-identified, 不应混入同一 over-identified Hansen J 估计。全文轨相对 ctx/ss 两轨的方法论权衡是: 覆盖面最广、信息损失最少, 但也最容易被文章中与目标银行/金融科技主题无关的段落 (如公司简介、免责声明、其他银行的对比性叙述) 引入情感噪声, 这正是本仓库同时维护 ctx/ss 两条聚焦轨作为稳健性检验的动机所在。

## VAR: log_sent_ss

【变体差分】

log_sent_ss 是 log_sent 家族在"银行+金科同句"轨 (ss) 上的实现, 公式结构与另两轨一致 (log1p(pos_count_ss) − log1p(neg_count_ss); 覆盖门控自 F5 2026-07-16 起用 ss 轨专属有效票计数 `n_articles_llm_valid_ss`), 但输入文本判据最为严格: `content_ss` 要求同一句内同时出现目标银行实体与金融科技词表命中 (裸 AC 自动机 1506 词, 与银行侧的否定词+短名过滤判据不对称), 即 ss 轨捕捉的是"银行与金融科技在同一句话里被共同谈论"的紧密共现情境, 而非仅仅"同一篇报道里既提到银行也提到金融科技"。当某篇文章内不存在这种严格同句共现时, ss 轨镜像 ctx 轨的回退语义: `content_ss` 回退为全文 body, 并置 `ss_is_fallback=True`, 该回退与 ctx 轨共享同一 `n_articles` 分母, 不产生额外的样本损失或口径分裂。ss 轨的正负计数同样来自 stage 21 三家 LLM 对 `content_ss` 的多数投票情感判定, 在面板层聚合后代入门控函数。由于 ss 轨判据比 ctx 轨更严苛 (同句 vs. 邻近窗口), 当一篇文章确实存在同句共现时, log_sent_ss 所反映的情感信号在构念上比 log_sent_ctx 更贴近"银行的金融科技相关活动本身被如何评价", 而不掺杂目标银行泛泛被提及但与金融科技话题无关段落的情感; 但代价是同句共现命中率通常低于窗口共现, 回退比例 (`ss_is_fallback` 为真的篇数占比) 若在某银行-年内偏高, 则该行的 log_sent_ss 实质上退化为与 log_sent_full 高度相近的度量, 使用者在解读稳健性检验结果时应结合 `ss_is_fallback` 分布加以判断。与家族内另两轨一样, log_sent_ss 是留篇门控 (full-only) 之下的 conditional-on-full 稳健性轨道, 不参与"是否留篇"的决策, 且与 log_sent_full、log_sent_ctx 各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 检验。

<!-- rendered-citations:begin -->
Chen, J., & Roth, J. (2024). Logs with zeros? Some problems and solutions. Quarterly Journal of Economics, 139(2), 891-936. https://doi.org/10.1093/qje/qjad054
Vives, X., & Ye, Z. (2025). Information technology and lender competition. Journal of Financial Economics, 163, Article 103957. https://doi.org/10.1016/j.jfineco.2024.103957
Pierri, N., & Timmer, Y. (2022). The importance of technology in banking during a crisis. Journal of Monetary Economics, 128, 88-104. https://doi.org/10.1016/j.jmoneco.2022.04.001
Cho, M., & Choi, A. (2025). Do Auditors Adjust Labour Allocation in Response to Client Media Coverage and Tone?. Abacus, abac.70024. https://doi.org/10.1111/abac.70024
Tucker, A. M., Xia, Y., & Smelcer, S. N. (2024). Text, tone, and legal language: Analyzing mutual fund disclosure sentiment. American Business Law Journal, 61(1), 57-86. https://doi.org/10.1111/ablj.12239
<!-- rendered-citations:end -->
