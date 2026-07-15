---
family_id: TB002
columns:
- company
- bank
- year
- track
- n_docs
- n_docs_v
- n_docs_strict
- n_docs_frac
- n_docs_frac_v
- n_docs_longhit
unit: pair 长表逐行计数, 无量纲 (篇数/分数计数)
formula: "pair 长表以 (company, bank, year, track) 为粒度键, 对满足银企共现条件的报道去重计数; n_docs 为canonical不门控篇数, n_docs_v 为经LLM verified门控篇数, n_docs_frac 为按同篇多银行1/k分摊的分数计数, n_docs_longhit 为限定≥4字variant命中的精度稳健臂"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py (pair 长表生成分支)
upstream:
- 21_tone_llms_full.parquet (报道乘目标银行乘轨全宇宙, LLM验证门控来源)
- config/company_tax_names.yaml (税调企业名单AC匹配SSOT, 44,771家/124,366个variants)
citations:
- doi: 10.1145/360825.360855
  type: journal
  authors: Aho, A. V., & Corasick, M. J.
  year: 1975
  title: "Efficient string matching: An aid to bibliographic search"
  venue: Communications of the ACM
  vol: 18
  issue: 6
  pages_or_artno: 333-340
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
---

## CORE

pair 长表是税调企业银企共现面板体系中承载最细粒度信息的中间产物, 其行键是企业、银行、年份与文本轨四元组, 每一行记录该四元组下满足共现条件的去重报道篇数。这张表存在的根本理由是, 企业年面板上呈现的全部加权测度列在理论上都可以由这张长表结合银行年层面的源列值重新构造出来, 因此当研究者出于篇幅或规范考虑删减面板上的某些细分权重列时, 只要长表本身完好保存, 被删列并未真正丢失, 只是暂时不落盘, 需要时可以按公开的加权公式一行代码精确复原。这一"可重构性"设计直接呼应文本挖掘领域关于高效字符串匹配算法的经典工作, 该算法族正是本项目用于在海量报道全文中定位企业与银行名称及其变体的底层技术, 匹配效率与匹配精度共同决定了长表计数列的可信度上限。

十个列中最容易被误解的是四组计数口径的差异。canonical 口径 n_docs 完全不做验证门控, 只要触发共现判据即计入, 这一口径保证了权重侧的宇宙与银行年主面板的共现口径完全一致; verified 口径 n_docs_v 则叠加了大语言模型对报道是否真实涉及该银行该企业实质性关联的验证判定, 用于分子端而非权重端的测度构造。分数计数 n_docs_frac 处理的是同一篇报道同时提及多家银行的常见情形, 若不做分摊, 一篇报道会对每家被提及银行都贡献一整篇的计数, 造成系统性重复计数偏差, 这与媒体覆盖度测度文献中反复强调的度量层面加总方式对结果敏感高度呼应, 早期关于媒体报道与股票横截面收益关系的研究即指出, 媒体计数指标的构造方式本身会实质影响后续估计的方向与显著性。n_docs_longhit 是精度稳健臂, 只统计触发四字及以上较长企业名变体命中的篇数, 用以对冲短简称带来的假阳性风险, 这一设计思路与媒体倾向性测度研究中强调应对文本匹配噪声保持警觉的方法论立场一致。

从行数规模上看, pair 长表的体量远超企业年主面板, 因为它把每一个 (企业, 银行, 年份, 文本轨) 组合都单独列为一行, 即便该组合下的共现篇数恰为零也不例外, 这一"满骨架不裁行"的存储策略与主面板保持满骨架不裁行是同一套设计哲学的延伸, 目的是让使用者在任何时刻都能从长表出发, 通过标准的分组聚合操作精确复原出主面板上的任意一个加权测度列, 而不必担心因长表本身裁去了零值行而丢失了应有的加总基数。四个计数口径彼此之间并非相互替代关系, 而是分别服务于不同的分析目的: canonical 口径用于与银行年主面板共现口径对齐的权重构造场景, verified 口径服务于需要排除大语言模型判定为不实质相关报道的分子端测度, 分数计数服务于需要严格避免同篇报道被多家银行重复计入的场景, 精度稳健臂则服务于对短变体假阳性风险格外敏感的稳健性检验场景, 论文写作端应当在方法部分明确声明本文采用的是哪一种或哪几种口径的组合, 而不能笼统地只提及一个覆盖不清的"共现篇数"概念, 媒体报道文本挖掘领域的匹配算法效率与语义精度权衡, 以及媒体覆盖度测度构造对结果方向性的实质影响, 共同提示研究者在选择计数口径时应保持与研究问题本身的经济含义相匹配, 而非仅凭默认设置草率决定。

<!-- rendered-citations:begin -->
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
<!-- rendered-citations:end -->
