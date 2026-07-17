---
family_id: F567
columns:
- tone_fin_media_ctx
- tone_fin_media_full
- tone_fin_media_ss
unit: 语调得分 (连续, 名义双极 [-1,1]; bank-year 面板层面为该银行当年"财经类媒体"子样本内三家 LLM 投票语调的算术均值)
formula: 'tone_fin_media{track} = mean_媒体类型为财经专业类 (media_type==fin) 且属于该银行该年份的文章集合 llm_vote_score{track}; media_type 由 attention_media.py::_classify_content 对 媒体(中文) 名称做规则分类 (fin/comp/other 三分类, 与①②③维度正交于④中央/地方行政层级分类); track ∈ {full, ctx, ss}; llm_vote_score{track} 缺列时该轨整族列优雅跳过 (if src not in df.columns: continue), 不产生该轨输出而非报错'
producer: pipeline\panel\attention_media.py ; pipeline\panel\export.py
upstream:
- 21_tone_llms.parquet (llm_vote_score_full/_ctx/_ss 三家 LLM 多数投票语调)
- 12_news_fintech.parquet / 11_news_bank.parquet (媒体(中文) 来源名称字段, 供 _classify_content 分类)
- 14_materialize_ctx.parquet (content_ctx / content_ss 物化, 供 ctx/ss 轨 LLM 打分上游)
citations:
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving Content to Investor Sentiment: The Role of Media in the Stock Market"
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: "The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes"
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.2139/ssrn.5220056
  type: wp
  authors: Marchetti, S., Tarducci, E., & Branzoli, N.
  year: 2025
  title: "Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy"
  venue: SSRN Working Paper
- doi: "10.1111/acfi.13230"
  type: "journal"
  authors: "Yan, L., Ma, Y., Li, C., & Tang, G."
  year: 2024
  title: "Media abnormal tone and cross section of stock returns: Evidence from China"
  venue: "Accounting & Finance"
  vol: "64"
  issue: "3"
  pages_or_artno: "2671-2698"
new_dois: []
---

## CORE

【构念与来源】
tone_fin_media 家族刻画的是"财经专业类媒体"这一媒体来源子群体对目标银行报道语调的均值水平, 属于 attention_media.py 媒体异质性模块四条正交分类轴中的第①②③维度 (内容类型异质性: fin/comp/other) 与语调测度的交叉表。母表 attention_media.py 先对每篇文章的媒体来源名称字段 (媒体(中文)) 施加规则分类函数 _classify_content, 把每篇报道的发布媒体归入 fin (财经专业媒体, 如证券时报、财新、21世纪经济报道类)、comp (综合性媒体, 如人民日报、新华社等非专业财经但覆盖财经新闻的综合类媒体) 或 other (其余, 包括地方都市报、行业垂直媒体等) 三类之一。这一分类与④中央/地方行政层级分类 (central_media_frac 系列) 是两条彼此正交的媒体异质性坐标轴: 前者刻画媒体的专业化定位, 后者刻画媒体的行政隶属层级, 二者可以同时成立 (例如某财经媒体既可能是中央级也可能是地方级)。tone_fin_media 家族只消费 fin 这一支, 对应的 comp/other 支分别落在同一批产出的 tone_comp_media/tone_other_media 姊妹家族, 三者以及由三者两两相减派生出的三条 tone_gap_* 缺口列共同构成一个完整的媒体类型异质性测度组。构造该测度组的经济学动机源自 Tetlock (2007) 开创的"媒体即信息中介"传统: 媒体不是信息的中性传声筒, 不同类型媒体在信息生产的专业深度、编辑立场、受众结构和商业模式上系统性存在差异, 因而对同一家银行的报道可能呈现系统性不同的语调分布。财经专业媒体相对于综合类和其它类媒体, 通常具备更强的行业专业知识储备、更贴近机构投资者与专业读者的编辑取向, 也更可能在竞争性财经报道市场中形成有别于党政机关报的独立评价基调 (You, Zhang, & Zhang, 2018 关于中国"谁掌握了笔杆子的力量"的研究即刻画了不同媒体所有权/定位结构下语调生产的系统性差异)。因此 tone_fin_media 一方面服务于描述性刻画 (专业财经媒体眼中的银行形象是否系统性不同于大众媒体), 另一方面也是构造 tone_gap_fin_other / tone_gap_fin_comp 等媒体来源异质性检验列的分子来源, 用于检验主回归结论是否被某一类媒体的报道口径单方面驱动。

【方法学与计算】
计算链条起点是 21_tone_llms 阶段产出的 llm_vote_score{track} —— 三家大模型 (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash) 对每篇文章语调的多数投票共识分数, 名义双极域 [-1, 1] (需注意生产语料下该分数实证呈近退化的单极正向强度分布, 负面类占比极低, 后续面板导出层已将标签口径由"双极情感"收敛为 favorability/optimism 框架披露, 但本列内部计算逻辑不受影响, 仍是对该共识分数的算术均值)。attention_media.py 在文章级 DataFrame 上先打 _media_type 标签, 再按 (target_bank, year, _media_type=='fin') 三键分组对 llm_vote_score{track} 取组内均值, 得到 bank-year 层面的 tone_fin_media{track}。这一均值计算在三条轨道 full/ctx/ss 上各自独立重复: full 轨消费标题+全文语调分数, ctx 轨消费标题+实体窗口语调分数, ss 轨消费标题+银行∧金科同句±N 窗口语调分数 (ss 回退语义镜像 ctx: 当某篇文章不存在银行与金科词的同句共现时, content_ss 退回全文 body, 对应 ss_is_fallback 标记为真, 该文章仍以其退化后的全文语调分数计入分母, 而非被剔除)。三轨各自基于 llm_vote_score{track} 是否存在于上游 DataFrame 中做优雅跳过判断 (if src not in df.columns: continue), 即某一轨若因上游产出缺失而整体不可用, 则该轨对应的 tone_fin_media{track} 列及其下游缺口列均不产出, 而不是以 NaN 填充误导性地保留列名。三轨聚合逻辑完全平行独立, 属于"各自 just-identified 并排、互为稳健性、不分主次"的口径 —— full/ctx/ss 三条轨道在本家族内绝不应被混入同一个 over-identified 的 Hansen J 检验框架, 各轨各自作为独立的识别策略稳健性对照, 使用者若需要联合利用三轨信息应分别单独纳入回归而非构造联合矩条件。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否被判定为"一篇有效的银行金科报道"只取决于该篇 full 轨的 LLM 判定结果 llm_verified_full, ctx/ss 轨的分组均值计算限定在 full 轨已确立的留篇集合子集上进行, 因而 ctx/ss 轨的 tone_fin_media 行数 (bank-year 观测数) 天然是 full 轨观测数的子集或相等, 不会出现 ctx/ss 轨观测数反超 full 轨的情形。分母是同一 bank-year 单元内落入 fin 分类且属于留篇集合的文章篇数, 若某银行某年不存在任何财经专业媒体报道则该 bank-year 观测的 tone_fin_media{track} 为缺失 (NaN, 通过 pandas merge how='left' 自然产生), 这与 fin_media_frac (财经媒体占比) 分母覆盖全部留篇报道不同、口径上更窄。

【文献定位】
本家族方法学谱系上溯至 Tetlock (2007) 在 The Journal of Finance 上确立的"媒体语调是投资者情绪的可观测代理"这一基本范式, 并进一步吸收了 Peress (2014) 关于媒体信息扩散机制的识别思路 (媒体报道对市场的因果作用需要区分信息内容本身与传播渠道差异)。将媒体按类型/定位切分再分别测算语调均值的做法, 直接呼应 You, Zhang, & Zhang (2018) 在 Review of Financial Studies 上对中国媒体"笔杆子权力"结构性差异的实证发现——不同媒体主体在信息生产的独立性与专业性上存在系统差异, 因而不能把所有媒体来源汇总为单一无差别的语调测度。就中国银行业情境而言, Fang, Wang, Wang, & Yuan (2024) 在 International Review of Economics & Finance 上研究了中国语境下媒体情感与银行系统性风险及存款稳定性之间的关系, 为本家族"财经媒体语调作为银行层面结果变量的解释力来源"提供了直接的同类应用先例; Marchetti, Tarducci, & Branzoli (2025) 的工作银行工作论文进一步示范了银行×年层面语调聚合的方法论操作细节, 与本家族按 (target_bank, year, media_type) 分组取均值的聚合逻辑相印证。 在同语种、同媒体生态的语调计量实践上, Yan、Ma、Li 与 Tang (2024) 以中国中文媒体报道构造语调测度并检验其对股票横截面收益的解释力, 是与本家族同语言、同媒体类型的近期前沿参照, 佐证了「在中文财经新闻文本上可抽取具有独立解释力的语调信号」这一测量前提在本项目所处数据生态中的可行性。其迁移边界须诚实标明: 该文层级为上市公司-股票横截面而非 bank-year 面板, 被解释变量为股票收益, 与本项目 funding_cost 等银行侧结果变量不同; 其语调为「异常语调」(相对预期的残差) 口径且由文本词典法得到, 与本家族直接对三家 LLM 投票共识分 llm_vote_score{track} 在 fin 子样本内取算术均值不是同一公式; 原文亦未按财经/综合/其他这一媒体内容类型维度切分子样本。故该文只锚定中文媒体语调计量的同域可行性, 不锚定本家族赖以成立的 media_type 分层设计与三轨并排口径。
## VAR: tone_fin_media_ctx

【变体差分】
本列是家族内的 ctx 轨变体: 语调分数来源为 llm_vote_score_ctx, 该分数由 21_tone_llms 阶段对 content_ctx (标题+实体窗口文本, 在 14_materialize_ctx 阶段物化) 打分产生, 而非 full 轨的标题+全文。分组条件与 full 轨完全一致 (target_bank, year, _media_type=='fin'), 唯一差异在于参与均值计算的语调分数来自实体窗口窄化后的文本。ctx 轨的经济学解读是"聚焦于银行实体被直接提及的局部语境下财经媒体的语调水平", 相较 full 轨剔除了文章中与该银行无直接关联段落的语调噪声, 但也因此对文本窗口截取规则更敏感。行数覆盖受 full-only 留篇门控约束, 即该列观测集合是 full 轨留篇集合的子集 (仅限落在 ctx 轨语调分数非缺失范围内的记录), 与 full/ss 两轨互为稳健性并排、不构成同一 over-identified 矩条件的一部分。若上游 llm_vote_score_ctx 列因某次运行未产出 ctx 轨结果而整体缺失, 则本列 (以及同批的 tone_gap_fin_other_ctx 等下游列) 亦一并优雅跳过不产出, 而非以全 NaN 列占位。使用场景上, ctx 轨适合用作"排除文章内无关段落语调污染"的稳健性对照: 一篇长篇综合性财经报道可能在提及目标银行的段落之外, 还夹杂对宏观经济、其它银行或行业整体的评述, 这些评述如果整体基调与该银行局部段落相反, 会拉动 full 轨均值偏离银行实体本身受到的评价水平; ctx 轨通过窗口截取尽量把这类"搭车"文本排除在打分输入之外。但这也意味着 ctx 轨对实体窗口抽取规则 (如括号内窗口大小、句子边界识别) 更敏感, 窗口过窄可能丢失必要的语境线索导致 LLM 打分噪声增大。在与 tone_fin_media_full、tone_fin_media_ss 联合解读时, 三者数值方向一致而幅度存在系统性差异, 可视为财经媒体语调测度对文本窗口宽度选择的敏感性佐证, 而非相互矛盾的信号来源。

## VAR: tone_fin_media_full

【变体差分】
本列是家族内的 canonical 轨变体, 也是三轨中口径最宽的一支: 语调分数来源为 llm_vote_score_full, 由 21_tone_llms 阶段对标题+全文文本打分产生。留篇门控 (2026-06-29 起) 直接以本轨 llm_verified_full 判定为准绳, 即一篇报道是否计入"该银行当年的有效银行金科报道"这一行宇宙, 完全由 full 轨的 LLM 判定结果决定, ctx/ss 两轨的分组均值计算均限定在本轨已确立的留篇集合子集内进行。因此 tone_fin_media_full 的 bank-year 观测数是三轨中最完整的一支 (等于或多于 ctx/ss 两轨), 也是财经媒体子样本语调水平的默认参照口径。在多数下游 paper 模块 (如媒体异质性检验、tone_gap_fin_other_full 等缺口列) 中, full 轨常被用作首选展示口径, 但依 CLAUDE.md 三轨铁律, 这并不意味着 full 轨在识别策略上优先于 ctx/ss —— 三轨仍各自 just-identified 并排、互为稳健性, 使用者在构造工具变量或矩条件时须避免将三轨同时纳入同一个 over-identified 的 Hansen J 检验。full 轨的优势在于文本覆盖最完整、不存在窗口截取或同句共现判据带来的信息损耗, 因而统计效率通常最高、缺失值最少; 劣势在于容易把文章中与目标银行无直接关联的段落语调也计入均值, 尤其在长篇综合报道中风险更突出。财经媒体子样本 (media_type=='fin') 本身相较全样本已经过一层媒体来源专业性的筛选, 因此 tone_fin_media_full 可理解为"专业财经媒体在标题+全文口径下对该银行的整体评价基调", 是构造 tone_gap_fin_other_full (财经 vs 其它媒体语调差) 与 tone_gap_fin_comp_full (财经 vs 综合媒体语调差) 两条缺口列的直接分量来源, 这两条缺口列用于检验主效应是否被某一类媒体单方面驱动。

## VAR: tone_fin_media_ss

【变体差分】
本列是家族内的 ss 轨变体: 语调分数来源为 llm_vote_score_ss, 由 21_tone_llms 阶段对 content_ss (标题+银行∧金科词同句±N 窗口文本, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 打分产生。ss 轨的回退语义镜像 ctx 轨的一般模式但判据更严格: 当某篇报道中不存在"目标银行"与"金科词"在同一句 (±N 句窗口) 内共现的情形时, content_ss 退回为该篇的全文 body (与 full 轨文本相同), 对应的 ss_is_fallback 标记置真; 这类退化为全文的文章仍照常参与 tone_fin_media_ss 的分组均值计算 (共享 n_articles 分母, 不被剔除), 因此当银行∧金科同句共现比例较低时, ss 轨的实际信息含量会向 full 轨趋同。分组条件同样是 (target_bank, year, _media_type=='fin'), 行数覆盖同样受 full-only 留篇门控约束、是 full 轨留篇集合的子集。ss 轨与 ctx/full 两轨互为稳健性并排、经济学解读是"财经媒体在银行与金融科技词汇最紧密并置语境下所呈现的语调水平", 相较 ctx 轨窗口更窄、判据更严格, 三轨在识别策略上不设主次, 亦不得混入同一个 over-identified 的 Hansen J 检验矩条件。ss 轨的价值在于最大限度地锁定"该篇报道确实在谈论银行与金融科技交集"这一构念核心, 排除掉那些仅仅是在同一篇文章不同段落分别提及银行与金科、但二者实质不相关的报道对语调均值的稀释或污染; 代价是同句共现判据 (原语见 core/text/entity_context.py::extract_bank_fintech_cooccurrence, 与 stage 13 共现硬过滤使用的 has_bank_fintech_cooccurrence_within_radius 是不同判据、禁止互相复用) 天然会命中率偏低, 在银行∧金科同句共现较稀疏的语料区间, 大量文章依赖回退语义退化为全文口径, 此时 ss 轨实证上会与 full 轨高度相关, 这一退化属预期行为而非测度失效, 在 T=2 开发样本上表现得尤为明显, 生产 T=19 全量语料上同句共现覆盖率预期显著提升。

<!-- rendered-citations:begin -->
Tetlock, P. C. (2007). Giving Content to Investor Sentiment: The Role of Media in the Stock Market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets: Evidence from Newspaper Strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen? The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring tone shifts in media coverage: An empirical application to bank financing conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
Yan, L., Ma, Y., Li, C., & Tang, G. (2024). Media abnormal tone and cross section of stock returns: Evidence from China. Accounting & Finance, 64(3), 2671-2698. https://doi.org/10.1111/acfi.13230
<!-- rendered-citations:end -->
