---
family_id: F470
columns:
- peer_compete_idx
- peer_compete_idx_70
- peer_compete_idx_75
- peer_compete_idx_80
- peer_compete_idx_85
- peer_compete_idx_90
unit: 比例, 取值 ∈ [0, 1] (银行-年层面文章占比)
formula: 'peer_compete_idx_{c} = (bank, year) 单元内「同一篇报道正文 co_mentioned_banks
  字段中出现 ≥1 家 LLM 识别并经 cutoff=c 归一化管道解析出的该银行同行」的文章占该单元全部展开文章的比例; cutoff
  历史上控制的是把 LLM 输出的银行名字符串归一化为规范名时 difflib 模糊串匹配的严格度, 而非 LLM 对"是否为同行"这一判断本身的置信度。
  该 difflib 兜底策略已被移除, 现行归一化仅剩策略 1 (精确匹配)/策略 2 (变体映射)/策略 3 (唯一子串包含) 三档, 三者均与
  cutoff 参数无关, 因此五档 cutoff 后缀列在归一化结果上结构性相同 (盘上实证 nonnull 数与均值五档全同), 五档列的存在仅为与本仓库
  derivative_replication.py 消费的 CUTOFF_VARS 列表及 Stata schema 保持命名齐整。cutoff=0.80 (对应中缀 80)
  的变体额外写入无后缀别名 peer_compete_idx。当 (bank, year) 已被查证 (key ∈ queried_keys) 但同行集合为空时,
  记 0.0 (真实零同行, 区别于未查证的 NaN 缺失)。'
producer: pipeline\panel\llm_peer_iv.py (L563-580 _normalize_peer_names 归一化管道; L973-980
  disclosure omni-g-llm-peer-05; L1072-1109 之后同区块「同业竞争压力指标」; L1186-1187 cutoff
  勘误注释) ; pipeline\panel\export.py (dta 标签映射)
upstream:
- llm_peer_iv.py 内 peer_maps (LLM 同行识别结果, 按 cutoff 分层归一化, 但归一化本身与 cutoff 无关)
- df_exploded (文章级展开面板, 含 co_mentioned_banks 列)
- queried_keys (已完成 LLM 同行查证的 bank_year 集合)
citations:
- doi: 10.1016/j.jbankfin.2024.107356
  type: journal
  authors: Ge, S., Li, S., & Zheng, H.
  year: 2025
  title: Diamond cuts diamond — News co-mention momentum spillover prevails in China
  venue: Journal of Banking & Finance
  vol: '171'
  pages_or_artno: '107356'
- doi: 10.1016/j.jcorpfin.2025.102772
  type: journal
  authors: Schwenkler, G., & Zheng, H.
  year: 2025
  title: News-driven peer co-movement in crypto markets
  venue: Journal of Corporate Finance
  vol: '93'
  pages_or_artno: '102772'
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: Network effects in corporate financial policies
  venue: Journal of Financial Economics
  vol: '144'
  issue: '1'
  pages_or_artno: 247-272
- doi: 10.1016/j.jfineco.2015.02.003
  type: journal
  authors: Lee, C. M. C., Ma, P., & Wang, C. C. Y.
  year: 2015
  title: Search-based peer firms — Aggregating investor perceptions through internet
    co-searches
  venue: Journal of Financial Economics
  vol: '116'
  issue: '2'
  pages_or_artno: 410-431
- doi: 10.1111/jofi.12094
  type: journal
  authors: Leary, M. T., & Roberts, M. R.
  year: 2014
  title: Do peer firms affect corporate financial policy?
  venue: The Journal of Finance
  vol: '69'
  issue: '1'
  pages_or_artno: 139-178
- doi: 10.1146/annurev-economics-020320-033926
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2020
  title: Peer effects in networks — A survey
  venue: Annual Review of Economics
  vol: '12'
  pages_or_artno: 603-629
- doi: "10.1108/jfrc-11-2024-0218"
  title: "Fintech-driven resilience amid pandemic: a text mining analysis of the banking industry with ESG dynamics"
  authors: "Kakinuma, Y., & Likitratcharoen, D."
  year: 2025
  venue: "Journal of Financial Regulation and Compliance"
  type: "journal"
- doi: "10.1111/1475-679x.12560"
  title: "News Bias in Financial Journalists' Social Networks"
  authors: "Xu, G."
  year: 2024
  venue: "Journal of Accounting Research"
  type: "journal"
new_dois:
  - "10.1108/jfrc-11-2024-0218"
  - "10.1111/1475-679x.12560"
---

## CORE

【构念与来源】
peer_compete_idx 系列量化的是「某银行在某年被新闻媒体同篇报道中与其同行 (peer) 共同提及的强度」, 用作衡量该银行在媒体注意力空间中所处的同业竞争暴露程度的银行-年层面指数。其数据基础是 stage 11 银行实体识别的自然副产品 co_mentioned_banks: 文章级展开表 df_exploded 中记录了与目标银行同篇报道内共同出现的其他银行实体列表 (分号分隔字符串), 不依赖 LLM 二次调用。该指数把这一原始共现信号与另一条独立的 LLM 同行识别管道 (针对每个 (bank, year) 单元, 由 LLM 基于该银行当年报道语料输出一份候选同行名单) 交叉: 只有当某篇报道的 co_mentioned_banks 集合与该单元的 LLM 认定同行集合存在非空交集时, 该篇才计入分子。这一"新闻共现频率 × LLM 语义同行判定"的双源交叉设计, 方法学谱系上与 Ge, Li & Zheng (2025, Journal of Banking & Finance) 关于中国语境下新闻共同提及 (co-mention) 现象与企业间关联效应、动量外溢的发现相呼应: 该文证明新闻文本层面的共同提及本身携带经济信息, 是本仓库把 co_mentioned_banks 字段当作有效同业暴露信号的直接文献支撑。Schwenkler & Zheng (2025, Journal of Corporate Finance) 进一步在加密市场语境下验证了"新闻驱动的同行联动" (news-driven peer co-movement) 这一构念的普适性, 说明用新闻叙事 (而非仅财务基本面) 驱动的同行共振效应, 在不同资产类别、不同新闻语料上均可复现, 为本指数把"新闻共现"作为同业竞争暴露的代理变量提供了跨市场的方法学佐证。
需要特别澄清的一点是: peer_compete_idx_{c} 系列名义上按 LLM 归一化管道中的 cutoff 参数 (0.70–0.90) 分五档, 但该参数 历史上 (在已移除的 difflib 模糊串匹配兜底策略中) 才真正影响归一化结果的严格度; 现行归一化管道仅保留精确匹配、变体映射、唯一子串包含三种策略, 三者判定逻辑均与 cutoff 数值无关, 因此五档列在盘上呈现结构性相同的取值 (非缺失计数与均值逐档全同)。这是一处需要向读者如实披露的口径事实, 而非某种统计上的巧合或算法设计缺陷: 它反映的是本仓库同行归一化管道演进过程中, 曾经承担阈值敏感性的组件已被更严谨的规则化匹配取代, 而阈值参数本身作为历史遗留接口被保留, 以维持与下游 Stata 复现脚本的 schema 兼容性。

【方法学与计算】
计算发生在 llm_peer_iv.py 的第 7b 步 (「同业竞争压力指标」区块), 紧随第 7 步的 IV 合并逻辑之后, 共用同一批已经在前序步骤中按 cutoff 分层构建好的 peer_maps 字典与 queried_keys 集合。算法对 panel 中出现过的每一个 (bank, year) 组合逐一处理: 先取该单元在 df_exploded 中的全部文章行 (mask 过滤 target_bank 与 year 双重匹配), 若该单元无任何展开文章则直接跳过 (既不置 0 也不置 NaN, 该单元在结果字典中缺席, 后续 merge 时自然为 NaN)。若该单元有展开文章但 peer_maps[cutoff] 中查不到该 bank_year 键对应的同行列表 (peers 为空), 则进一步区分两种情形: 若该 key 已经出现在 queried_keys 中 (即 LLM 同行查询确实执行过, 只是查证结果是"零同行"), 则记 peer_compete_idx_{int(c*100)} = 0.0, 这是一个真实的、有信息量的零值, 表示该银行当年报道中不存在任何被 LLM 认定的同行; 若该 key 根本不在 queried_keys 中 (查询未执行, 例如受限于 LLM 查询预算或该单元在上游被跳过), 则该 cutoff 下该单元直接 continue, 不写入任何值, 最终体现为面板中的 NaN 缺失。这一"真零 vs 缺失"的区分 (对应源码注释 fix omni-g-llm-peer-07) 是本指数的关键设计: 避免了把"未查证"误记为"零竞争", 从而污染下游把 peer_compete_idx 当作连续暴露度量的回归。若 peers 非空, 则把同行列表转成集合 peer_set, 逐篇检查该文章的 co_mentioned_banks 字符串 (以分号切分后转集合) 与 peer_set 是否有交集, 得到布尔序列 co_with_peer; 最终该 cutoff 下的指数值即为 co_with_peer 在该单元全部文章上的均值, 自然落在 [0, 1] 区间。
关于 peer_maps 本身如何按 cutoff 分层构建: LLM 对每个 (bank, year) 单元输出的候选同行名单是自由文本 (可能含简称、全称、异体字), 需经归一化管道 (_normalize_peer_names) 映射到 bank_names.json 规范名。该归一化管道明确披露 (源码 fix omni-g-llm-peer-04): 原有的策略 4 (difflib.get_close_matches 模糊串匹配, 以 cutoff 控制匹配严格度) 已被移除并替换为策略 4' OOV 拒绝 (不在规范名册中的候选一律丢弃, 不再吸附到最相近在册银行, 因其曾把政策性银行"中国农业发展银行"误配为"中国农业银行")。现行有效策略仅剩策略 1 精确匹配、策略 2 变体映射 (处理"工行"→"中国工商银行"等简称)、策略 3 唯一子串包含 (命中 >1 家规范名视为歧义泛称直接拒绝), 三者均不消费 cutoff 参数。源码 disclosure (omni-g-llm-peer-05) 因此明确指出: cutoff 五档"原仅作用于已移除的策略 4 difflib 兜底", 现行五档后缀列"结构性逐位相同", 保留仅为 Stata schema 兼容, 且"论文表注必须披露该灵敏度维度无识别变差"。无后缀 peer_compete_idx 并非独立计算, 而是在循环内当 c == 0.80 时把该单元的值原样复制一份, 即 peer_compete_idx ≡ peer_compete_idx_80, 是本家族的 canonical (默认) 口径, 对应 export.py 面板标签 "Peer Competition Index (0.80)"。

【文献定位】
本家族"用新闻共现构造同行暴露"这一构造范式的直接文献支撑来自 Ge, Li & Zheng (2025, Journal of Banking & Finance): 该文在中国资本市场语境下证明新闻共同提及现象携带可预测的关联效应与动量外溢信息, 是 co_mentioned_banks 字段被赋予经济含义的最贴近文献锚。Schwenkler & Zheng (2025, Journal of Corporate Finance) 在加密资产语境下的"新闻驱动同行联动"发现进一步佐证了这一构念的跨市场普适性, 说明新闻叙事本身 (不依赖公司基本面相似度) 足以驱动可观测的同行联动效应。在"同行"这一构念本身应如何界定的更广泛文献中, Lee, Ma & Wang (2015, Journal of Financial Economics) 用互联网协同搜索行为构造"搜索型同行"网络, 是另一支基于非静态行业代码信息源构造同行关系的代表性工作, 佐证了实证金融中"同行"存在多种数据驱动的替代定义方式, peer_compete_idx (基于新闻共现 + LLM 语义识别的交叉) 是这一谱系中面向中文财经新闻语境的一个具体实现。Grieser, Hadlock, LeSage & Zekhnini (2022, Journal of Financial Economics) 用网络方法研究同行公司财务政策的相互影响, 提供了"同行网络对公司决策产生实质性经济后果"这一背景论证。在同行效应 (peer effects) 更广泛的计量识别文献中, Leary & Roberts (2014, The Journal of Finance) 证明同行公司的资本结构决策会显著影响焦点公司自身的资本结构选择, 是最早系统检验同行效应存在性的代表性研究之一, 但需要特别说明: 该文的"同行效应"是分析端的因果识别设计 (用同行冲击作为工具变量估计政策外溢), 而 peer_compete_idx 只是一个描述性的暴露强度测度, 二者构念层级不同, Leary & Roberts (2014) 在本家族中的定位是方法论对照锚, 提醒读者 peer_compete_idx 本身不构成同行效应的因果证据。Bramoullé, Djebbari & Fortin (2020, Annual Review of Economics) 对同行效应网络识别的系统性综述进一步说明, 若要把"同行竞争暴露"提升为因果识别设计, 须借助独立的识别策略 (如本仓库另一族 LOO 同行工具变量 leave_one_out_peer_*_iv), 而非直接把 peer_compete_idx 代入因果推断框架。Kakinuma & Likitratcharoen (2025, Journal of Financial Regulation and Compliance) 用文本挖掘方法从新闻语料构造银行业指数, 与本族用新闻共现构造银行同业暴露测度的文本挖掘方法学谱系相呼应。Xu (2024, Journal of Accounting Research) 研究财经记者社交网络对新闻报道偏向的影响, 为本族以新闻共同提及构造银行同业竞争暴露指数提供了新闻网络结构如何塑造企业间报道关联的文献背景。

peer_compete_idx 家族与本仓库其他"同行" (peer) 相关的族群构念边界分明、不可混同: leave_one_out_peer_*_iv 系列是留一法同行均值工具变量, 用于工具变量识别策略的排他性约束构造 (第一阶段回归的外生工具), 属于识别设计工具; llm_peer_coverage_iv / llm_peer_count 度量的是 LLM 同行查询本身的覆盖率与同行数目, 是工具有效性的辅助诊断; 而 peer_compete_idx 是一个纯描述性的、银行自身报道中同行共现频率的暴露测度, 不承担工具变量的排他性角色, 不应被单独用作因果识别的排他性约束来源。五个 cutoff 后缀列名义上各自独立、并排存在, 遵循本仓库梯子类测度的一般铁律: 各档口径互为稳健性、不分主次, 严禁把多个 cutoff 变体同时纳入同一个过度识别的 Hansen J 检验框架 (镜像本仓库三轨文本、co-primary 双轨嵌入、政治词权重梯度等既有梯子铁律)。但对本家族而言必须额外如实披露: 五档口径当前在归一化管道层面结构性相同 (无 difflib 兜底后, cutoff 不再影响归一化结果), 即该阈值维度暂不提供真实的识别变差, 使用者若要展示阈值敏感性稳健性, 应改为在最大同行数上限、单模型 vs 多模型合意、句子级 vs 全文级判据等其余维度上另行扫描, 而非依赖本家族五档列本身。

## VAR: peer_compete_idx

【变体差分】
本列是家族的无后缀 canonical 口径, 数值上恒等于 peer_compete_idx_80, 即循环内 cutoff == 0.80 分支下计算的媒体同业竞争暴露指数原样复制。之所以选定 0.80 作为默认别名而非其余四档, 是源码在合并 IV 结果时的既定命名约定 (与本仓库其余 LLM-Peer 族群, 如 llm_peer_tone_iv_full/ctx 的默认 cutoff=0.80 口径保持一致, 便于跨族群在同一命名习惯上做联合稳健性叙事), 而非某种统计最优性证明; 尤须注意, 由于现行归一化管道 (精确匹配/变体映射/唯一子串包含) 均不消费 cutoff 参数, 0.80 并不比其余四档在"判别更准确"意义上更优, 它只是历史上曾承担 difflib 严格度控制的一个数值锚点。export.py 中该列被赋予面板标签 "Peer Competition Index (0.80)", 提醒使用者该默认值本质上是 0.70–0.90 五档命名梯子中的一个特定取值。在解释上, 该列衡量的是: 一家银行当年的新闻报道有多大比例与被 LLM 认定、并经归一化管道解析出的同行银行共同出现。若某单元 LLM 未能识别出任何同行但该单元已完成同行查证, 则记 0.0 (真零, 非缺失); 若该单元从未被查证, 则为 NaN。
在主回归表 (正文表格) 与叙事性描述中, 使用者应默认引用本无后缀列, 因为它是本仓库跨模块 (IV 合并、面板导出、下游 paper 模块) 约定俗成的默认引用口径, 与 llm_peer_tone_iv 系列的默认阈值命名形成一致的横向可比性。由于本列与 peer_compete_idx_80, 以及在归一化结果层面的其余四档变体在数值上完全或高度等价 (源码层面归一化不消费 cutoff), 使用者不应误将无后缀列与任一带后缀列视为两个独立信息源纳入同一回归右端项, 否则将引入完全共线性; 若正文表注涉及该指数的阈值敏感性维度, 须如实注明五档结构性相同、不构成独立识别变差这一源码披露事实。

## VAR: peer_compete_idx_70

【变体差分】
本列在命名上对应 LLM 同行归一化管道中 cutoff=0.70 这一档位。需要明确披露: 该参数历史上 (在已移除的 difflib 模糊串匹配兜底策略中) 用于控制字符串归一化的宽松程度, 但现行归一化管道 (策略 1 精确匹配、策略 2 变体映射、策略 3 唯一子串包含) 均不再消费 cutoff 数值, 因此本列在归一化结果上与其余四档 (75/80/85/90) 结构性相同 (盘上实证非缺失计数与均值逐档全同), 并不实际对应"更宽松的同行判定标准"。保留该后缀列纯粹是为了与本仓库 derivative_replication.py 消费的 CUTOFF_VARS 命名清单以及 Stata schema 命名体系保持齐整、便于程序化按阈值遍历, 而非提供真实的规格曲线采样点。缺失/真零的记录规则与家族 canonical 完全一致 (对照 queried_keys 判定): 若该 (bank, year) 已被查证但同行集合为空则记 0.0, 未被查证则记 NaN。
使用者在撰写正文或稳健性叙事时, 应避免沿用"cutoff 越低同行判定越宽松、指数越容易偏高"这一直觉性但与当前源码实现不符的表述; 若确需展示对 LLM 同行识别本身 (而非归一化字符串匹配严格度) 的敏感性, 应参考源码 disclosure 中指出的其余维度 (最大同行数上限、单模型 vs 多模型合意、句子级 vs 全文级共现判据), 这些才是当前管道中真正携带识别变差的稳健性来源。本列不应被单独解读为比 canonical 更"宽泛因而更优"的替代测度, 二者在归一化结果层面高度等价。

## VAR: peer_compete_idx_75

【变体差分】
本列在命名上对应 LLM 同行归一化管道中 cutoff=0.75 这一档位, 位于 0.70 与默认档 0.80 之间。与 peer_compete_idx_70 同理, 该 cutoff 参数当前仅在已移除的 difflib 模糊串匹配兜底策略中才发挥实际作用, 现行三条有效归一化策略 (精确匹配/变体映射/唯一子串包含) 均不受 cutoff 数值影响, 因此本列与其余四档在归一化结果上呈结构性相同的取值分布, 而非某种介于宽松与严格之间的过渡口径。列名保留 0.75 后缀是命名体系齐整性的产物 (与 llm_peer_iv.py 内固定的 cutoffs = [0.70, 0.75, 0.80, 0.85, 0.90] 五档常量列表一一对应), 便于下游脚本按统一命名规则批量消费, 不代表该档在识别力度上独立于其余四档存在实质差异。
本列在缺失/真零记录规则上与家族其余四档完全一致: 依旧以 queried_keys 是否包含该 (bank, year) 键来区分"已查证但零同行"(记 0.0) 与"未查证"(记 NaN)。使用者若在稳健性表格中同时报告五档结果, 应在表注中如实说明五档口径的归一化结果结构性相同这一源码披露事实, 而非把五档取值差异 (若观察到) 归因于阈值本身的判别力度变化 — 任何微小差异更可能来自面板合并过程中的浮点或行级差异, 而非阈值参数造成的判别集合收缩。

## VAR: peer_compete_idx_80

【变体差分】
本列与无后缀 canonical 列 peer_compete_idx 数值完全一致 (源码在 cutoff == 0.80 分支内把计算结果同时写入两个键), 保留带后缀命名是为了与其余四档阈值变体 (70/75/80/85/90) 在列命名体系上保持齐整、便于程序化按阈值遍历 (如 export.py 中批量标签生成循环)。使用者在做梯子敏感性分析 (即固定同一份代码逐档扫描) 时应优先引用本列而非无后缀列, 以保持代码风格统一; 在做主回归/正文表格时则习惯性引用无后缀列。两者在数据层面永远相等, 不存在任何口径差异。
从设计动机上说, cutoff=0.80 之所以成为整个家族乃至本仓库 LLM-Peer 族群 (llm_peer_tone_iv_full/ctx 等) 共享的默认命名锚, 更多是历史沿革而非当前算法意义上的统计最优点 — 现行归一化管道的三条有效策略均不消费 cutoff 数值, 0.80 与 0.70/0.75/0.85/0.90 在归一化结果上结构性相同。本列与无后缀列的完全等价关系在数据管道意义上是良性冗余 (redundant by design), 便于程序按统一命名规则批量处理五档变体而不必对 canonical 列做特判。使用者在编写循环遍历代码时可以放心地把 80 视为普通一档, 在编写正文叙事代码时则引用无后缀列以获得更简洁的变量名; 但在撰写方法学脚注时, 应如实说明该"默认阈值"标签本质上是命名约定而非经过校准的判别力度选择。

## VAR: peer_compete_idx_85

【变体差分】
本列在命名上对应 LLM 同行归一化管道中 cutoff=0.85 这一档位, 处于默认档 (0.80) 与最严档 (0.90) 之间。与其余四档同理, 该参数当前仅在已移除的 difflib 模糊串匹配兜底策略中才实际影响归一化严格度, 现行三条有效策略 (精确匹配/变体映射/唯一子串包含) 均不消费 cutoff, 因此本列在归一化结果上与其余四档结构性相同, 并不实际对应"更保守的同行判定口径"。列名保留 0.85 后缀纯粹是为了与固定的 cutoffs 常量列表及下游 Stata 消费脚本的命名体系保持一致。
使用者在解释本列时应避免沿用"cutoff 越高判定越严格、同行集合越小、指数下限估计越可信"这一直觉性但与当前源码实现不符的叙事。该档在缺失/真零记录规则上与家族其余四档完全一致: 依旧以 queried_keys 是否包含该 (bank, year) 键来区分"已查证但零同行"(记 0.0) 与"未查证"(记 NaN), 不因阈值提高而改变这一判定逻辑本身, 保证五档变体在缺失机制上的可比性。若研究者确实需要一个"更保守、更不易被误报同行污染"的稳健性检验, 应转向源码 disclosure 中指出的其余具有真实识别变差的维度 (最大同行数上限 / 单模型 vs 多模型合意 / 句子级 vs 全文级共现判据), 而非依赖本列与 canonical 档之间目前并不存在的判别力度差异。

## VAR: peer_compete_idx_90

【变体差分】
本列在命名上对应 LLM 同行归一化管道中 cutoff=0.90 这一档位, 是五档命名梯子中数值最高的一档。与其余四档完全同理: 该 cutoff 参数历史上曾用于控制已移除的 difflib 模糊串匹配兜底策略的严格度, 但现行三条有效归一化策略 (精确匹配/变体映射/唯一子串包含) 均不消费 cutoff 数值, 因此本列在归一化结果上与其余四档结构性相同 (盘上实证非缺失计数与均值逐档全同), 并不实际构成"判别标准最严格、样本损耗最大"的严格端锚点。使用者不应把本列观察到的取值差异 (若有) 解读为阈值提高导致同行集合收缩的证据, 更合理的归因是面板合并过程中的行级差异, 而非算法层面真实存在的判别力度梯度。
该列在缺失/真零记录规则上与家族其余四档完全一致 (依旧以 queried_keys 判定"已查证但零同行"记 0.0、"未查证"记 NaN)。源码 disclosure (omni-g-llm-peer-05) 明确要求: 论文表注必须披露该 cutoff 灵敏度维度在当前实现下无真实识别变差, 五档列的呈现价值主要是与本仓库既有 LLM-Peer 族群命名体系保持一致, 而非提供独立的规格曲线稳健性证据。若使用者需要展示 peer_compete_idx 核心结论对判别力度选择的真实敏感性, 应参考源码所指出的其余维度 (最大同行数上限 / 单模型 vs 多模型合意 / 句子级 vs 全文级共现判据) 另行扫描, 本列 (以及 70/75/80/85 其余四档) 单独不构成该类稳健性证据的有效来源。

<!-- rendered-citations:begin -->
Ge, S., Li, S., & Zheng, H. (2025). Diamond cuts diamond — News co-mention momentum spillover prevails in China. Journal of Banking & Finance, 171, 107356. https://doi.org/10.1016/j.jbankfin.2024.107356
Schwenkler, G., & Zheng, H. (2025). News-driven peer co-movement in crypto markets. Journal of Corporate Finance, 93, 102772. https://doi.org/10.1016/j.jcorpfin.2025.102772
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Lee, C. M. C., Ma, P., & Wang, C. C. Y. (2015). Search-based peer firms — Aggregating investor perceptions through internet co-searches. Journal of Financial Economics, 116(2), 410-431. https://doi.org/10.1016/j.jfineco.2015.02.003
Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? The Journal of Finance, 69(1), 139-178. https://doi.org/10.1111/jofi.12094
Bramoullé, Y., Djebbari, H., & Fortin, B. (2020). Peer effects in networks — A survey. Annual Review of Economics, 12, 603-629. https://doi.org/10.1146/annurev-economics-020320-033926
Kakinuma, Y., & Likitratcharoen, D. (2025). Fintech-driven resilience amid pandemic: a text mining analysis of the banking industry with ESG dynamics. Journal of Financial Regulation and Compliance. https://doi.org/10.1108/jfrc-11-2024-0218
Xu, G. (2024). News Bias in Financial Journalists' Social Networks. Journal of Accounting Research. https://doi.org/10.1111/1475-679x.12560
<!-- rendered-citations:end -->
</content>
