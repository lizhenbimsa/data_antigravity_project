---
family_id: F574
columns:
- tone_gap_homecity_noncity_ctx
- tone_gap_homecity_noncity_full
- tone_gap_homecity_noncity_ss
unit: 语调差值 (连续, 理论域约 [-2,2]; 实际集中于 [-1,1] 附近, bank-year 层面两组均值之差)
formula: 'tone_gap_homecity_noncity{track} = mean(llm_vote_score{track} | _is_homecity==1, groupby target_bank,year) − mean(llm_vote_score{track} | _is_homecity==0, groupby target_bank,year); _is_homecity 由银行注册地城市 (config/bank_addresses.json) 与报道来源城市 (原始列「城市」) 清洗地名后缀比对得到, 1=同城/0=异城/NaN=地理不可判(两侧文章均被剔除, 不计入任一组均值)'
producer: pipeline\panel\attention_media.py (维度⑨ 地理邻近性, (9f) 指标1 偏袒度)
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss)
- config/bank_addresses.json (银行注册地省/市)
- 原始新闻元数据列「国家地区/省份」「城市」
citations:
- doi: 10.1257/aer.20170947
  type: journal
  authors: Qin, B., Strömberg, D., & Wu, Y.
  year: 2018
  title: Media bias in China
  venue: American Economic Review
  vol: '108'
  issue: '9'
  pages_or_artno: 2442-2476
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: "10.1111/1911-3846.12935"
  type: "journal"
  authors: "Huang, Y., Li, F., Li, T., & Lin, T."
  year: 2024
  title: "Local information advantage and stock returns: Evidence from social media"
  venue: "Contemporary Accounting Research"
  vol: "41"
  issue: "2"
  pages_or_artno: "1089-1119"
- doi: "10.1111/irfi.70009"
  type: "journal"
  authors: "Chen, H., Chen, Y., & Li, D."
  year: 2025
  title: "Local bias under natural disasters"
  venue: "International Review of Finance"
  vol: "25"
  issue: "1"
  pages_or_artno: "e70009"
new_dois: []
---

## CORE

【构念与来源】
tone_gap_homecity_noncity 度量的是同一家银行在"同城媒体"与"异城媒体"两类报道来源上语调水平的系统性差异, 即媒体地理接近性造成的语调偏袒 (local media slant)。构念直接对标 Qin, Strömberg & Wu (2018, American Economic Review) 关于中国媒体因所有权结构、地方政商关系嵌入与审查约束等渠道对辖区内报道对象存在系统性倾向性偏差的经典发现; 在中国语境下亦与 Fang, Wang, Wang & Yuan (2024, IREF) 关于媒体情感、存款稳定性与银行系统性风险的研究、以及 You, Zhang & Zhang (2018, Review of Financial Studies) 关于谁俘获了"笔杆子"、媒体报道对象如何通过资源与关系渠道系统性影响报道倾向的框架相呼应: 三者共享同一个基本前提, 即媒体既非纯粹信息中介也非随机噪声源, 报道地理来源本身携带系统性偏差信号。本列把这一构念操作化为 bank-year 层面两组 (同城 vs 异城) 报道语调均值之差, gap>0 表示同城媒体较异城媒体对该行的报道更偏正面, |gap| 越大代表媒体地理分歧越显著, 是 bank_media_disagreement (方法学衍生篇) 与地理邻近性稳健性分析共同消费的核心 treatment/covariate 候选。

【方法学与计算】
producer 为 pipeline\panel\attention_media.py 内维度⑨ "地理邻近性" 模块 ((9a)-(9g))。计算分两层: 省级 (homeprov/nonprov) 与市级 (homecity/noncity), 本家族聚焦市级。先在文章级构造 _is_homecity 布尔编码: 以 config/bank_addresses.json 中银行注册地城市字段与原始新闻元数据「城市」列, 经统一地名后缀清洗 (剔除"省/市/自治区/特别行政区"等行政区划后缀, 解决"杭州市"≠"杭州"字面不等问题) 后逐字符串比对, 相等记 1.0 (同城)、不等记 0.0 (异城)。关键的口径纪律是缺失值处理: 若银行注册地城市缺失、或报道来源城市缺失/为空串、或整个数据源缺「城市」列, 一律显式置 NaN (地理不可判), 而非旧口径下强制归零 (归零会把"来源不可知"错误算作"异地", 一是压低 home_media_frac 分子而不压低分母造成低估, 二是把不可判文章混入异地组稀释 tone_gap)。此外存在一条拓扑不变量约束: 确认同城 (city==1) 蕴含同省 (若同省字段此前未判为1, 强制提升为1), 反向不成立 (非同城不蕴含非同省), producer 内以断言方式在盘上校验 homeprov_media_frac ≥ homecity_media_frac。
在 bank-year 层面, 对每条轨道 track ∈ {full, ctx, ss} 分别取该轨道情感原语 llm_vote_score{track} (stage 21 三家 LLM 多数投票的连续打分), 按 _is_homecity 分组求组内均值 tone_homecity_media{track} / tone_noncity_media{track} (分组过滤 ==1/==0 天然排除 NaN 行, 因 NaN==x 恒为 False), 再取两者之差得到 tone_gap_homecity_noncity{track} = tone_homecity_media{track} − tone_noncity_media{track}。若某 bank-year 内某一组 (同城或异城) 报道为空, 该组均值为 NaN, gap 相应传播为 NaN, 不做 0 填补 (保守稀疏, 避免虚假精确)。
三轨口径必须与项目铁律对齐: full/ctx/ss 三条轨道各自独立计算, 各自 just-identified 并排、互为稳健性、不分主次, 严禁在同一 over-identified Hansen J 检验中混用三轨的 tone_gap 列。full 轨为标题+全文语调; ctx 轨为标题+实体窗口语调; ss 轨镜像 ctx 的回退语义, 即银行∧金科词无同句共现时 content_ss 退化为全文 body (ss_is_fallback=True, 与 ctx 共享 n_articles 分母口径)。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入"银行金科报道"全集只看 llm_vote_score_full 所在文章的 full 轨验证结果, ctx/ss 是该留篇集合之上的条件测度/稳健性轨道, 不独立扩大或收缩行宇宙。

【文献定位】
本列所属"地理媒体异质性"九维度中的第⑨维, 与同批的 tone_gap_homeprov_nonprov (省级同构变体, 见姊妹家族)、homecity_media_frac (封闭度, 同城报道占比)、neg_frac_homecity/noncity (负面过滤, 同城媒体是否系统性压低负面报道比例) 共同构成 Qin, Strömberg & Wu (2018) 中国媒体系统性倾向性偏差发现在市级地理邻近性维度上的操作化切片。Fang et al. (2024) 在中国银行业情境下证实媒体情感对存款稳定性与系统性风险有因果传导, 为本列的经济后果假设提供直接同域参照; Tetlock (2007) 则是媒体语调作为投资者情绪代理变量这一测量传统的奠基文献, 说明 tone_gap 类构念背后"语调差异蕴含信息或偏差"的一般性理论预期。命名前缀 home/non 与项目内另一条正交轴 central/local (媒体行政层级: 央级 vs 地方级) 刻意区分, 二者捕捉不同机制 (地理邻近性 vs 行政级别), 不应混淆或替代使用。 近期文献从两个方向为本列的同城/异城二分补充了更新的证据基础。Huang、Li、Li 与 Lin (2024) 以社交媒体发帖者的地理位置识别「本地」信息发布者, 按发帖者与公司总部的地理关系切分样本、比较本地组与非本地组的信息含量对股票收益的预测力, 其「按地理关系切分子样本再作组间对比」的设计与本列同城/异城两组语调均值作差同族; 迁移边界在于该文文本源为散户社交媒体发帖而非正式媒体报道, 地理归属基于用户 IP/自报位置而非本项目的媒体来源城市字段经地名后缀清洗比对, 研究对象为一般上市公司而非银行, 且其被解释变量是股票收益而非语调本身。Chen、Chen 与 Li (2025) 利用逾 24,000 名散户的账户级日度持仓记录, 证明自然灾害下本地投资者比非本地投资者更多增持本地股票, 且效应由本地投资者的信息优势驱动, 为「本地/异地地理二分确实承载真实信息差异」这一前提提供了近期锚点, 支撑本列组间差分的构念基础; 但须诚实指出, 该文的「本地」是投资者持仓行为与标的之间的关系, 与本列「媒体来源地—银行总部」的主体与关系类型均不同, 原文以灾害为外生冲击做异质性检验而本项目无冲击设计, 且原文不含任何媒体、文本或语调测度, 故仅锚定二分的构念前提, 不锚定本列的语调聚合与作差算法。
## VAR: tone_gap_homecity_noncity_ctx

【变体差分】
本列为 ctx 轨道版本, 分组求均值时消费的情感原语是 llm_vote_score_ctx 而非 llm_vote_score_full, 对应 stage 14 物化的 content_ctx (标题 + 实体窗口文本) 三家 LLM 多数投票打分。文章分组集合 (同城/异城判定 _is_homecity) 与 full 轨完全共享同一套地理元数据编码, 唯一差异是参与均值计算的语调分数来自不同文本窗口。ctx 轨的行宇宙是 full-only 留篇门控之上的条件子集 (即只统计 llm_vote_score_full 所在文章通过留篇验证的那批报道, 在其中再取 ctx 轨分数求组内均值), 而非独立的留篇判定; 若某篇文章的 content_ctx 缺失或该实体窗口过短导致 ctx 轨分数缺失, 该篇在 ctx 轨的两组均值计算中被跳过 (producer 逻辑为 `if src_tone not in df.columns: continue` 优雅降级, 整条轨道缺列则该轨全部相关列不生成), 不借用 full 轨分数顶替, 也不借用其他轨道的分母。
与 tone_gap_homecity_noncity_full 的经济含义差异在于: full 轨捕捉的是媒体对银行整体报道 (含大量背景性、非实体聚焦段落) 的语调偏袒, 而 ctx 轨聚焦实体窗口附近的语调, 更贴近"针对该银行本身的措辞"而非全文氛围, 因此对无关段落 (如同一篇报道里提及多家机构的比较性叙述) 的稀释更不敏感。二者数值上通常相关但不恒等, 按项目铁律二者互为稳健性并排, 不设主轨, 在识别策略层面绝不可与 full/ss 轨的 tone_gap 混入同一过度识别方程。样本层面 ctx 轨报道覆盖度天然弱于/等于 full 轨 (因需同时满足实体窗口可提取), 故 ctx 轨 tone_gap 在 bank-year 上的缺失率通常不低于 full 轨, 尤其在同城报道稀疏的银行-年份上更容易出现两组之一为空导致 gap 为 NaN 的情形。

## VAR: tone_gap_homecity_noncity_full

【变体差分】
本列是家族 canonical 轨道, 消费 llm_vote_score_full (标题 + 全文正文三家 LLM 多数投票语调分数)。它同时是 producer 内唯一被单独挑出打印分布诊断日志的轨道 (attention_media.py 步骤 6c "媒体分歧缺口" 日志块, 2026-06-29 起新增, 保守只覆盖 full 轨以避免 ×3 轨冗余输出), 也是留篇门控判定的直接来源: 一篇文章是否进入"银行×金科报道"全集, 完全由该篇 llm_vote_score_full 对应的 full-only 验证结果决定, ctx/ss 两条轨道的分组集合都以 full 轨的留篇结果为行宇宙上界。
full 轨语调覆盖全文语境, 相较 ctx/ss 更少受实体窗口截断或同句共现筛选影响, 报道量/覆盖率通常最高, 因此 bank-year 上两组 (同城/异城) 同时非空、gap 可计算的比例也通常最高, 缺失模式相对稀疏。full 轨与 ctx/ss 轨严格并列、互为稳健性、不分主次, 三者共同验证媒体地理偏袒结论对文本窗口选择是否稳健; 若三轨方向一致 (同符号) 且量级相近, 增强对本地媒体倾斜真实存在而非文本切分伪影的信心; 若仅 full 轨显著而 ctx/ss 均不显著, 提示效应可能来自报道整体氛围 (如版面基调、记者立场) 而非针对该银行本身措辞的差异化处理, 是解读上需要特别标注的分歧模式。

## VAR: tone_gap_homecity_noncity_ss

【变体差分】
本列为 ss (同句共现) 轨道, 消费 llm_vote_score_ss, 对应 stage 14 物化的 content_ss (标题 + 银行∧金科词同句 ±N 窗口文本, 窗口半径见 config/filtering.yaml::context_window.ss_sentence_radius, 与 stage 13 硬过滤所用的 cooccurrence_filter.sentence_radius 是两个不同配置键, 不可混用)。ss 轨的回退语义严格镜像 ctx: 当某篇文章中银行与金科关键词不存在同句共现时, content_ss 退化为全文 body, 对应 ss_is_fallback=True, 并与 ctx 轨共享同一 n_articles 分母口径; 若上游 FINTECH_AC (金科词自动机) 为 None, 则 *_is_fallback 全体置 True, 整条 ss 轨优雅降级为近似全文口径而非报错。
在本家族的具体计算上, ss 轨与 ctx 轨结构完全平行: 均在 full-only 留篇集合的条件子集上, 用各自轨道的 llm_vote_score_ss 按 _is_homecity 分组求均值再作差, 该篇若无 llm_vote_score_ss (轨道整体缺列或该行分数缺失) 则从两组统计中跳过, 不做跨轨补值。ss 轨捕捉的是"银行与金科词紧邻共现处"的语调, 相较 ctx 的实体窗口窗口更窄、判据更严格 (裸 AC 自动机命中金科侧词表、银行侧另叠加否定词+短名过滤的不对称口径), 因此天然覆盖的报道子集最小、gap 计算所需的非空双组条件也最难满足, 在早期试跑 T=2 开发规模数据上尤其容易出现同城/异城任一组为空导致大量 bank-year 观测为 NaN 的情形; 生产 T=19 全量语料下该轨的有效样本量预期显著回升。与 full/ctx 两轨同为并排稳健性检验, 若三轨结论方向一致, 说明媒体地理偏袒效应即便收窄到银行与金科紧邻共现的窄口径下依然存在, 是对效应稳健性最严格的一道检验。

<!-- rendered-citations:begin -->
Qin, B., Strömberg, D., & Wu, Y. (2018). Media bias in China. American Economic Review, 108(9), 2442-2476. https://doi.org/10.1257/aer.20170947
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Huang, Y., Li, F., Li, T., & Lin, T. (2024). Local information advantage and stock returns: Evidence from social media. Contemporary Accounting Research, 41(2), 1089-1119. https://doi.org/10.1111/1911-3846.12935
Chen, H., Chen, Y., & Li, D. (2025). Local bias under natural disasters. International Review of Finance, 25(1), e70009. https://doi.org/10.1111/irfi.70009
<!-- rendered-citations:end -->
