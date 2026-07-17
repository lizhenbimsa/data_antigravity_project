---
family_id: F571
columns:
- tone_gap_deepdive_nondeep_ctx
- tone_gap_deepdive_nondeep_full
- tone_gap_deepdive_nondeep_ss
unit: 语调缺口 (连续, 两个语调均值之差, 理论域约 [-2,2]; bank-year 面板列)
formula: 'tone_gap_deepdive_nondeep{track} = tone_deepdive_media{track} - tone_nondeep_media{track};
  其中 tone_deepdive_media{track} = mean(llm_vote_score{track} | _is_deepdive==1) 按 (target_bank, year) 分组,
  tone_nondeep_media{track} = mean(llm_vote_score{track} | _is_deepdive==0) 按 (target_bank, year) 分组;
  _is_deepdive = 媒体(中文) ∈ DEEPDIVE (NPPA 出版周期≥周报的非日刊出版物名录)'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full / _ctx / _ss)
- config 媒体出版周期名录 DEEPDIVE (NPPA 分类)
citations:
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1111/1475-679X.12349
  type: journal
  authors: Guest, N. M.
  year: 2021
  title: The information role of the media in earnings news
  venue: Journal of Accounting Research
  vol: '59'
  issue: '3'
  pages_or_artno: 1021-1076
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: Sentiment trading with large language models
  venue: Finance Research Letters
  vol: '62'
  pages_or_artno: '105227'
new_dois: []
---

## CORE

【构念与来源】
本家族衡量同一银行-年度样本内, 深度期刊 (deep-dive periodicals) 与非深度期刊两类出版物在报道语调上的系统性落差, 属于媒体异质性 (media heterogeneity) 这一大类测度下按出版周期切分的第七维度, 与官方/市场媒体缺口 (official-nonoff)、日报/非日报缺口 (daily-nondaily) 并列, 共同构成 attention_media.py 中"谁在写、写得多正面/多负面"的媒体来源画像。构念动机来自媒体经济学中一条稳健发现: 出版频率与报道深度存在权衡——日报受时效压力驱动, 倾向于转载简讯、跟随共识口径; 而周报及更低频出版的深度期刊具备更长的编辑周期与更充分的调查资源, 更可能生产原创分析而非简单转述。若深度期刊的语调系统性偏离非深度期刊, 说明媒体报道的信息含量并非同质, 简单加总全部报道计算的平均语调可能掩盖了"谁在主导舆论叙事"这一结构性差异。该缺口进一步嵌入媒体作为公司治理信息中介 (information intermediary) 的理论脉络: Guest (2021, JAR) 证明深度分析型媒体的新闻原创性越高, 对公司治理的改善效果越显著, 即深度报道不只是数量多少的问题, 而是携带增量信息、能被市场和监管方用作纠偏信号; Holzman, Miller & Twedt (2023, *The Accounting Review*) 进一步证实媒体语调本身具有规训 (disciplining) 功能——报道基调会约束管理层在盈余公告等信息事件上的行为空间, 而这种规训力的强弱恰与报道来源的编辑周期、原创程度密切相关, 为本家族按出版周期切分语调缺口提供了额外的理论支撑。本家族三个列 (`_full`/`_ctx`/`_ss`) 把这一构念落到银行金融科技新闻情境下的三条文本轨道上。
【方法学与计算】
计算分两步。第一步是媒体类型标注: 在文章级 DataFrame 上依据"媒体(中文)"字段是否落入 DEEPDIVE 名录 (基于 NPPA 出版周期分类、周报及更低频的非日刊出版物) 生成二元指示列 `_is_deepdive`, 该指示与轨道无关, 是纯来源属性判据, 不依赖报道内容或情感分值本身。第二步是分组语调聚合与作差: 对每条轨道 track ∈ {`_full`, `_ctx`, `_ss`}, 若源列 `llm_vote_score{track}` 存在于文章表 (缺列即优雅跳过该轨道, 不报错、不补零), 分别在 `_is_deepdive==1` 与 `_is_deepdive==0` 两个子样本上按 (target_bank, year) 分组求 `llm_vote_score{track}` 的算术均值, 得到 `tone_deepdive_media{track}` 与 `tone_nondeep_media{track}` 两个中间面板列, 再以左连接方式并入主面板; 最终 `tone_gap_deepdive_nondeep{track} = tone_deepdive_media{track} - tone_nondeep_media{track}`。`llm_vote_score{track}` 是 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票后的共识语调打分, 与本家族无关的词典/BERT 情感测度不混用。三个轨道彼此独立计算、独立合并, 互不借用彼此的样本划分或分母, 是并排的三个 just-identified 规格, 而非同一构念下的加权组合——full/ctx/ss 各自基于自身留篇集合的文本内容计算 `_is_deepdive` 分组语调, 禁止把三轨结果混入同一个 over-identified 假设检验 (如同一 Hansen J 统计量) 中联合识别。三轨具体差异见下方各 VAR 节。当某 (target_bank, year) 组合内某一媒体类别 (深度或非深度) 没有任何报道时, 对应的 `tone_*_media{track}` 为缺失, 差值列相应传播为 NaN, 这是分组均值语义下的自然结果, 并非计算错误, 反映该银行-年度样本在特定媒体类别上的报道空白。
【文献定位】
本家族的理论根基直接对应 Guest (2021, *Journal of Accounting Research*) 关于媒体信息中介功能的经典发现——深度分析型媒体的新闻原创性越高, 对公司治理的改善效果越显著, 而出版周期 (是否为周报及更低频的深度期刊) 正是原创性的一个可观测代理变量, 为把"深度期刊 vs. 非深度期刊"的语调落差当作有信息含量的异质性来源提供了直接支持; Holzman, Miller & Twedt (2023, *The Accounting Review*) 同样在盈余公告情境下证实媒体语调对管理层行为具有规训作用, 且这种规训力度依赖于报道来源的编辑深度而非单纯的报道数量, 进一步佐证按出版周期切分语调是识别媒体异质性影响力的有效维度。这一媒体异质性建模思路与本项目并列的官方/市场媒体缺口维度共享同一方法学传统——You, Zhang & Zhang (2018, *Review of Financial Studies*) 关于"谁掌握了笔杆子的权力"的分析同样强调媒体来源属性 (而非仅报道数量) 是理解媒体影响力异质性的关键。在中国银行业情境下, Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 的研究表明媒体情感对银行存款稳定性与系统性风险的影响本身就依媒体来源特征而异, 这与本家族"媒体异质性驱动语调缺口"的构念高度一致, 支持把出版周期这一来源属性单独拆分为独立的稳健性/机制维度, 而非简单假设所有媒体报道对样本银行的语调贡献同质。就语调测度本身而言, `llm_vote_score{track}` 承袭自 Tetlock (2007, *Journal of Finance*) 开创、并经大规模语言模型时代重新校准的文本情感测度传统 (如 Kirtac & Germano 2024, *Finance Research Letters* 在 LLM 情感交易上的应用), 差异在于本家族关注的不是语调水平本身, 而是语调在媒体来源结构上的分布形态。

## VAR: tone_gap_deepdive_nondeep_full

【变体差分】
`_full` 轨道使用标题+全文正文 (`content_full`) 作为文本输入源, 是留篇门控的主口径——2026-06-29 起, stage 21 是否判定某篇报道为"一篇银行金科报道"仅依据 `llm_vote_verified_full`, 即行宇宙 (哪些文章被纳入计算) 由 full 轨单独决定。本列的 `llm_vote_score_full` 来自这一 full-only 门控下的留篇集合, 因此是三轨中样本覆盖最完整、也是唯一独立决定纳入哪些文章-年度观测的轨道; ctx/ss 是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集合的子集。`_is_deepdive` 分组判据本身与轨道无关 (纯来源属性), 但由于 full 轨的文本输入是完整正文, `llm_vote_score_full` 捕捉的是记者对整篇报道 (标题+全部正文语境) 的语调判断, 因此 `tone_gap_deepdive_nondeep_full` 度量的是"深度期刊与非深度期刊在报道全文语调上的系统性落差", 不受实体窗口截断或同句共现约束影响, 是本家族三轨中信息最完整、也是默认呈报的规格。作为 P1 主线论文 `bank_fintech_tone` 的处理变量 `llm_vote_tone_full` 的媒体异质性延伸测度之一, 该列常与官方/市场/日报缺口列一同用于检验主结论是否被特定媒体来源结构驱动。经济含义上, 若 `tone_gap_deepdive_nondeep_full` 在样本内显著为正, 说明深度期刊对样本银行的报道语调整体更正面, 与"深度期刊更多依赖调查性、分析性报道而非简讯转载"的先验一致; 若显著为负, 则提示深度期刊在该银行金科议题上承担了更多批判性、监督性叙事功能, 这与 Guest (2021) 强调的媒体信息中介治理效力相呼应。由于分组均值分别在深度与非深度两个子样本上独立计算, 任一子样本在某银行-年度内报道量为零都会使对应缺口列缺失, 这一缺失是样本覆盖不足的直接反映, 不应与"语调本身为零"混淆。

## VAR: tone_gap_deepdive_nondeep_ctx

【变体差分】
`_ctx` 轨道使用标题+目标银行实体窗口文本 (`content_ctx`) 作为语调打分输入, 与 `_full` 的差异仅在于送入 LLM 打分的文本范围——`_ctx` 只截取银行实体周边的语境窗口而非全文, 意在剥离与银行本身无关的正文段落对语调判断的干扰。行宇宙上, `_ctx` 是 full-only 留篇集合的条件子集 (conditional-on-full), 即先由 `_full` 轨决定"这是不是一篇有效的银行金科报道", 再在该留篇集合内用 `_ctx` 文本重新计算语调, 而非独立门控。分组判据 `_is_deepdive` (深度/非深度期刊) 与轨道无关, 但 `tone_deepdive_media_ctx` / `tone_nondeep_media_ctx` 的分组均值是在 `_ctx` 自身的样本 (缺列即整轨跳过, 不借用 `_full` 的均值填补) 上计算, 与 `_full` 轨相互独立、并排存在, 属于互为稳健性、不分主次的规格——若 `tone_gap_deepdive_nondeep_full` 与 `tone_gap_deepdive_nondeep_ctx` 方向一致, 增强"深度期刊语调系统性不同于非深度期刊"这一结论对文本窗口选择的稳健性; 若不一致, 提示该缺口可能部分由全文中与银行无直接关系的段落驱动。禁止把 `_full` 与 `_ctx` 两列同时作为解释变量放入同一个 over-identified 工具变量设定中联合识别。实务上, `_ctx` 常用于排除"全文谈及深度期刊与非深度期刊语调差异, 但差异实际来自与目标银行无关段落 (如宏观经济评论、行业综述)"这一混淆解释——若把语调打分收窄到银行实体窗口后, `tone_gap_deepdive_nondeep_ctx` 与 `_full` 版本符号一致且量级相近, 则增强该缺口确系"深度期刊如何评价目标银行本身"而非"深度期刊行文整体基调不同"的解释力。

## VAR: tone_gap_deepdive_nondeep_ss

【变体差分】
`_ss` 轨道使用标题+银行与金融科技词汇同句 (±N 句窗口, 默认 N=1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制) 共现文本 (`content_ss`) 作为语调打分输入, 是三轨中文本范围最窄、最贴近"银行与金融科技二者被同时提及的具体语境"的规格。其回退语义镜像 `_ctx`: 当某篇文章不存在银行∧金科同句共现时, `content_ss` 退化为全文 body, 对应的 `ss_is_fallback` 标记为 True, 此时该篇文章在 `_ss` 轨下实际消费的是与 `_full` 相同的全文文本, 但仍计入 `_ss` 轨自身的分母 (`n_articles`), 是优雅降级而非静默丢弃。行宇宙同样是 full-only 留篇集合的条件子集。`_is_deepdive` 判据是来源属性、与轨道无关, 但 `tone_deepdive_media_ss` / `tone_nondeep_media_ss` 的分组均值完全基于 `_ss` 轨自身的 `llm_vote_score_ss` 计算, 若该列在文章表中不存在则整个 `_ss` 分支跳过 (对应面板列全为 NaN), 不会借用 `_full`/`_ctx` 的数值填补。`tone_gap_deepdive_nondeep_ss` 与 `_full`/`_ctx` 两列同为并排的 just-identified 稳健性规格, 三者互不隶属、不设主次, 共同构成媒体出版周期异质性缺口的三轨稳健性证据链, 但同样禁止混入同一个 over-identified Hansen J 检验中联合估计。相较 `_full`/`_ctx`, `_ss` 轨的样本量通常更小 (更多篇章因不满足同句共现而触发回退), 因此其 `tone_deepdive_media_ss`/`tone_nondeep_media_ss` 分组均值对个别极端语调打分的样本量敏感度更高, 解读该缺口时须结合各银行-年度 `_ss` 轨实际留篇数, 避免把小样本噪声误判为出版周期驱动的系统性语调落差。
<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm: Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Guest, N. M. (2021). The information role of the media in earnings news. Journal of Accounting Research, 59(3), 1021-1076. https://doi.org/10.1111/1475-679X.12349
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
<!-- rendered-citations:end -->
