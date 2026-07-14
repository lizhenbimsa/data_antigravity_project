---
family_id: F444
columns:
- multi_bank_frac
unit: 比率/占比 (proportion, [0,1])
formula: 'agg[''multi_bank_frac''] = (''is_multi_bank'', ''mean'') — bank-year 面板列, 由文章级布尔旗标 is_multi_bank 在 groupby([bank, year]) 内取算术平均得到; is_multi_bank 标记该篇报道的 co_mentioned_banks 集合(经银行名 variant→canonical 归一后)基数是否 ≥2, 即同一篇报道是否同时点名了聚焦银行之外的至少一家其他银行。'
producer: pipeline\panel\encode.py (聚合列定义, encode_coverage_and_robustness 段) ; pipeline\filtering\news_bank.py (stage 11, co_mentioned_banks 与 _BANK_VARIANTS 银行名归一字典的产出方) ; pipeline\panel\runner.py (步骤3, 由 co_mentioned_banks 计算 bank_count 与 is_multi_bank 布尔旗标)
upstream: []
citations:
- {doi: "10.1016/j.jeconom.2020.12.001", type: journal, authors: "Callaway, B., & Sant'Anna, P. H. C.", year: 2021, title: "Difference-in-differences with multiple time periods", venue: "Journal of Econometrics", vol: "225", issue: "2", pages_or_artno: "200-230"}
- {doi: "10.1073/pnas.2308950121", type: journal, authors: "Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J.", year: 2024, title: "GPT is an effective tool for multilingual psychological text analysis", venue: "Proceedings of the National Academy of Sciences", vol: "121", issue: "34", pages_or_artno: "e2308950121"}
- {doi: "10.1177/1536867X20976314", type: journal, authors: "Clarke, D., Romano, J. P., & Wolf, M.", year: 2020, title: "The Romano-Wolf multiple-hypothesis correction in Stata", venue: "The Stata Journal", vol: "20", issue: "4", pages_or_artno: "812-843"}
- {doi: "10.1177/109442810142004", type: journal, authors: "Edwards, J. R.", year: 2001, title: "Multidimensional constructs in organizational behavior research: An integrative analytical framework", venue: "Organizational Research Methods", vol: "4", issue: "2", pages_or_artno: "144-192"}
new_dois: []
---

## CORE

【构念与来源】
multi_bank_frac 度量一家银行在某一年份的全部报道中, "同一篇报道同时点名了该银行之外至少一家其他银行"这一现象所占的比例, 是银行-年面板上关于媒体报道结构 (structure of media coverage) 而非报道内容情感或实质的一个覆盖量辅助指标。它回答的问题不是"这家银行被如何评价", 而是"这家银行有多大比例的曝光是发生在与同业比较、并列或竞争语境中的"。该列在 pipeline 中位于 encode.py 的"E. 新闻覆盖量 & 稳健性辅助"代码段, 与 n_articles / avg_bank_count / max_bank_count / headline_frac 等 track-agnostic (轨道无关) 列并排产出, 共享同一篇数分母 n_articles (物理新闻篇数, 计入全部行含 LLM 情感缺失的 NA), 而非情感/态度类列所用的 n_articles_llm_valid 定义域分母。这一点是理解本列构念边界的关键: multi_bank_frac 统计的是"文章是否提及多家银行"这一纯粹的文本共现事实, 不依赖任何 LLM 情感/立场判定是否成功, 因此其分母采用最宽的物理篇数口径, 与三轨 (full/ctx/ss) 情感测度所用的、按轨道各自独立有效投票篇数 n_articles_llm_valid_{track} 分母有本质不同。
本列的直接来源是文章级布尔旗标 is_multi_bank, 该旗标由银行实体识别与归一化管线产出: 报道文本中出现的银行名先经 variant → canonical 映射 (银行名字典含标准名与变体, 如"工商银行"与"中国工商银行"统一归一到同一 canonical 名), 再统计该篇报道中出现的 distinct 规范银行数; 当且仅当归一后的银行集合基数 ≥2 (即除聚焦银行本身外还至少命中一家其他银行) 时, is_multi_bank 记为 True。multi_bank_frac 便是这一文章级旗标在 bank-year 分组内的算术平均, 因此其值域天然落在 [0,1] 区间: 0 代表该银行-年内全部报道都只提及该银行自身 (单一银行叙事), 1 代表全部报道都是多银行并提的比较/竞争语境。
本列与同批产出的 avg_bank_count (银行-年内每篇报道命中的规范银行数均值) 及 max_bank_count (同一分组内单篇报道命中银行数的最大值) 构成一组互补的"报道共现广度"辅助指标族: avg_bank_count 度量强度 (一篇报道平均卷入几家银行), max_bank_count 度量极值 (是否存在高度密集的多行并提报道, 如行业综述或监管政策解读类文章常同时点名十余家银行), 而 multi_bank_frac 度量发生率 (有多大比例的报道触及了"多行并提"这一现象, 不关心卷入几家)。三者共同为后续的媒体覆盖结构分析、以及区分"该行是被单独报道"还是"该行总是搭同业便车出现"这一构念差异, 提供了互相印证但非彼此冗余的截面刻画。

【方法学与计算】
计算链路分两段: 第一段在文章级完成实体识别与归一化, 依赖银行名主字典 (含标准名 bank_name 与其 variants 变体列表, 变体长度 ≥2 字符方纳入, 防止过短的字符串子串误命中), 将原始文本中出现的全部银行提及映射到唯一的 canonical 名集合 co_mentioned_banks, 再据其基数是否 ≥2 判定 is_multi_bank。第二段在银行-年聚合时用 pandas groupby(['bank','year']).agg 对该布尔列取 mean, 得到 multi_bank_frac。
需要特别说明的是与 llm_peer_iv.py 中"多银行同句抽取"逻辑的关系与区别: llm_peer_iv.py 内的 `_extract_multi_bank_sentences` 函数虽然名称中也含"multi_bank", 但它作用于句子级而非文章级, 且附加了第二重过滤条件 (句中须同时命中 ≥1 个金融科技关键词), 目的是为下游"同业竞对语境下的金融科技定位"LLM 判别任务筛选高信号句子池, 其产出并不直接进入 multi_bank_frac 这一列的计算; 该模块历史上曾修复过两个已知缺陷 (变体子串双计导致单银行句被误判为多银行比较句; PEER_PROMPT 断言与实际抽取句子不一致导致约 46% 的过筛句根本不含焦点银行本身), 修复后采用"规范银行集合须同时包含焦点银行且 distinct 计数 ≥2"的双重判据, 这一更严格的判据逻辑与 multi_bank_frac 所依赖的、更宽松的文章级 is_multi_bank (不要求集合中一定含"焦点银行"以外的判据强绑定, 仅要求归一化后 distinct 银行数 ≥2 即可) 分属管线中的两个独立消费场景, 阅读代码时不应将二者的判据细节相互混淆或彼此替代。
multi_bank_frac 是 track-agnostic (轨道无关) 列: 它不区分 full/ctx/ss 三种文本窗口口径, 也不像情感三轨或 co-primary 双轨嵌入那样构成"各自 just-identified 并排、互为稳健性、不分主次、禁混进同一 over-identified Hansen J"的梯子测度; 它是基于全文 (相当于 full 轨的原始"内容"字段拼接标题后逐句/逐篇扫描) 一次性算出的单一覆盖量辅助列, 不存在与之对应的 _ctx / _ss 变体, 也不参与本项目"稳健性梯子"体系下的模型间/轨道间/判据间 FWER 校正框架。这一点在解读该列时须与情感测度族严格区分, 以免误将其纳入不适用的多重假设检验校正范畴。

【文献定位】
从方法论谱系看, multi_bank_frac 所属的"媒体共同提及/共现结构"这一构念传统上服务于两类研究目的: 其一是作为同业可比性/竞争暴露的文本代理变量, 与业已成熟的"媒体关注度是信息扩散渠道"这一文献脉络 (如 Fang & Peress 2009 关于媒体报道广度影响资产定价的经典发现, 该文献线索已被本项目 n_articles 覆盖量族列吸收) 相呼应, 但 multi_bank_frac 进一步聚焦于报道内部的实体并置结构, 而非报道数量本身; 其二是作为多维构念分解的辅助校验信号, 呼应 Edwards (2001) 关于多维构念 (multidimensional constructs) 测度体系设计的整合分析框架 —— multi_bank_frac、avg_bank_count、max_bank_count 三者正是对"报道共现广度"这一潜在构念从不同角度 (发生率/强度/极值) 进行的多指标刻画, 而非单一指标的重复测量, 这与 Edwards 强调的"多维构念须用形式不同但逻辑互补的观测指标共同界定"的方法论主张一致。
在文本挖掘与 LLM 辅助编码的应用侧, Rathje et al. (2024, *PNAS*) 证明大语言模型在多语言心理与社会科学文本分析任务上能达到与人工编码相当乃至更优的信度水平, 这为本项目银行名实体归一化与句级/篇级多银行共现判据之后接续的 LLM 判别任务 (如 llm_peer_iv.py 中依托同句共现筛选出的高信号句子池所进行的同业竞对定位分类) 提供了方法学正当性支撑。在计量方法侧, multi_bank_frac 作为面板辅助控制变量或异质性分组变量使用时, 若涉及跨银行-年多重假设检验的显著性校正, 应遵循 Clarke, Romano & Wolf (2020) 在 Stata 环境下实现的 Romano-Wolf 逐步下降法框架, 而 Callaway & Sant'Anna (2021) 关于多期双重差分的估计框架, 则为以 multi_bank_frac 或其分组作为处理时点异质性协变量的事件研究设计提供了可直接借鉴的估计范式, 尤其适用于银行陆续接入金融科技合作/竞争叙事的渐进式处理场景。

## VAR: multi_bank_frac

【变体差分】
multi_bank_frac 在家族内是唯一一列, 无同构念的姊妹变体 (无 _ctx/_ss 轨道版本, 无阈值/判据梯子, 无跨模型对应列), 因此本节说明的重点不是"与家族 canonical 的差分", 而是该列自身在管线中与相邻覆盖量列的精确边界, 避免误用。
第一, 分母口径: multi_bank_frac 的分母是该银行-年内全部物理报道篇数 (即隐含在 mean 聚合中的分组行数, 与 n_articles 的口径完全一致, 覆盖含 NA 情感标签的全部行), 而非 n_articles_llm_valid 或任何轨道特定的 n_articles_llm_valid_{track}; 这意味着即便某篇报道未获得任何一家 LLM 的有效情感判定 (例如触发缓存缺失或模型拒答), 只要其命中了 ≥2 家规范银行名, 依然计入分子, 且始终计入分母。这与"某类情感/分类占比"型列 (如 tech_frac/sub_frac/collab_frac 等, 铁律要求其分子分母须同轨道严格自洽) 的分母选取原则不同, 读者在做跨列除法一致性核对时不应误以为 multi_bank_frac 应当采用与情感占比列相同的有效票分母。
第二, 与 max_bank_count/avg_bank_count 的差分: 三者共享同一上游 is_multi_bank/bank_count 判据体系, 但聚合函数不同 (mean vs mean vs max), 统计意涵也不同——multi_bank_frac 是"发生了多行并提"的比例 (二值旗标均值, 本身即是一个占比/频率), avg_bank_count 是"平均并提几家"的连续量均值, max_bank_count 是"该年内是否出现过极端并提"的极值; 三者在实证中应作为并列辅助控制变量或稳健性交叉核验对象使用, 而非相互替代或加总, 也不构成需做多重假设检验校正的同一构念梯子, 仅在需要同时报告多个协变量的稳健性表中依循 Romano-Wolf 逐步下降法 (Clarke, Romano & Wolf, 2020) 或同类校正框架处理家族层面的多重比较问题。
第三, 与 llm_peer_iv.py 内部句级 `_extract_multi_bank_sentences` 抽取逻辑的边界: 后者服务于同业竞对定位 LLM 分类任务的输入句子池构造, 其"多银行"判据附加了金融科技关键词过滤且要求归一化银行集合必须含焦点银行本身, 产出物是句子文本, 并不直接贡献 multi_bank_frac 列的取值, 二者在管线中是并行而非上下游依赖关系, 阅读或调试代码时应据此区分各自的输入输出边界, 避免把句级同业竞对抽取的判据细节误套用到本列的文章级多银行判据描述中。

<!-- rendered-citations:begin -->
Callaway, B., & Sant'Anna, P. H. C. (2021). Difference-in-differences with multiple time periods. Journal of Econometrics, 225(2), 200-230. https://doi.org/10.1016/j.jeconom.2020.12.001
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121
Clarke, D., Romano, J. P., & Wolf, M. (2020). The Romano-Wolf multiple-hypothesis correction in Stata. The Stata Journal, 20(4), 812-843. https://doi.org/10.1177/1536867X20976314
Edwards, J. R. (2001). Multidimensional constructs in organizational behavior research: An integrative analytical framework. Organizational Research Methods, 4(2), 144-192. https://doi.org/10.1177/109442810142004
<!-- rendered-citations:end -->
