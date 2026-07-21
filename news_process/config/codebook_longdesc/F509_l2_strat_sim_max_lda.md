---
family_id: F509
columns:
- strat_sim_max_lda
- strat_sim_max_lda_ctx
- strat_sim_max_lda_ss
unit: 相似度 (Jensen-Shannon 相似度, 值域 [0,1])
formula: 'strat_sim_max_lda_i,t = max_{j∈peers(t), j≠i} [1 − sqrt(JSD(θ_i,t ‖ θ_j,t))]; θ 为 LDA 主题分布, scipy.spatial.distance.jensenshannon(base=2) 返回的是 Jensen-Shannon 距离 √JSD (∈[0,1]), 而非散度 JSD 本身 (JSD = 距离的平方); 相似度按惯例定义为 1 − √JSD'
producer: pipeline\features\strategic_diff.py ; pipeline\panel\export.py
upstream:
- 14_materialize_ctx
- 21_tone_llms (留篇门控, full-only)
citations:
- doi: 10.1287/mnsc.2022.4369
  type: journal
  authors: Guzman, J., & Li, A.
  year: 2023
  title: Measuring Founding Strategy
  venue: Management Science
  vol: '69'
  issue: '1'
  pages_or_artno: 101-118
- doi: 10.1086/688176
  type: journal
  authors: Hoberg, G., & Phillips, G.
  year: 2016
  title: Text-Based Network Industries and Endogenous Product Differentiation
  venue: Journal of Political Economy
  vol: '124'
  issue: '5'
  pages_or_artno: 1423-1465
- doi: 10.1002/smj.2978
  type: journal
  authors: Haans, R. F. J.
  year: 2019
  title: 'What''s the value of being different when everyone is? The effects of
    distinctiveness on performance in homogeneous versus heterogeneous categories'
  venue: Strategic Management Journal
  vol: '40'
  issue: '1'
  pages_or_artno: 3-27
- doi: 10.1002/smj.3549
  type: journal
  authors: Su, J., Gao, X., & Tan, J.
  year: 2024
  title: 'Positioning for optimal distinctiveness: How firms manage competitive
    and institutional pressures under dynamic and complex environment'
  venue: Strategic Management Journal
  vol: '45'
  issue: '2'
  pages_or_artno: 333-361
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
- doi: "10.1016/j.jbusres.2024.115154"
  type: "journal"
  authors: "Phillips, D., Edwards, B. D., & Rutherford, M. W."
  year: 2025
  title: "Conformity or Differentiation: Optimal distinctiveness through mediating channels"
  venue: "Journal of Business Research"
  vol: "189"
  pages_or_artno: "115154"
new_dois: []
---

## CORE

【构念与来源】
本家族测量的构念是"报道文本所隐含的银行战略主题定位, 与同期同行银行相比有多相似"——即用 LDA (Latent Dirichlet Allocation) 主题模型把每篇/每家银行-年的报道文本表征为一个主题概率分布 θ, 再用该分布与同期所有同行银行主题分布的相似度取最大值, 得到"该银行在文本战略空间中最贴近哪一个同行"的指标。这是 Hoberg & Phillips (2016) 文本网络行业分类思路在中国银行-金科新闻语料上的本地化实现: 原始 TNIC (Text-based Network Industry Classification) 用 10-K 产品描述的词向量夹角度量企业间产品市场重叠, 本仓库把标的替换成银行相关新闻报道的主题分布, 用 Jensen-Shannon 散度取代余弦距离作为分布间的度量原语, 从而更契合 LDA 输出的是概率单纯形上的点而非稠密欧氏向量这一事实。strat_sim_max_lda 与家族同级的 strat_sim_max (TF-IDF char 轨) / strat_sim_max_w (TF-IDF jieba 词轨) / strat_sim_max_emb (Embedding 轨) 共同构成"最大同行相似度"这一构念的四种方法学实现, 彼此互为稳健性检验, 不设定何者为主 (parity 并排口径, 详见【方法学与计算】)。同族还有孪生的"战略差异度" strat_diff_n5_lda (N=5 最近邻 JSD 距离, 与本列同源但取最不相似的邻域均值而非最相似的单点) 与 centroid_diff_lda (银行主题分布到全行业质心的 JSD 距离, 谢佳松等 2025 全行业向量法的本地实现)。三者度量的是同一潜在语义空间下三个不同的几何量: 到最近邻的距离 (sim_max, 相似性极值)、到 N 个近邻的平均距离 (diff_n5, 局部密度)、到质心的距离 (centroid_diff, 全局定位), 互不替代、互不冗余。

【方法学与计算】
strat_sim_max_lda 的计算分三步。第一步, 对每期(年)语料池内全部银行的文本 (full/ctx/ss 三轨分别取各自物化文本) 拟合 LDA 主题模型, 得到每家银行-年的主题概率分布向量 θ_i,t (维度 = 主题数 K, 各分量非负且和为 1)。第二步, 对同期所有银行两两计算 Jensen-Shannon 散度的平方根 √JSD(θ_i,t ‖ θ_j,t), 该值由 scipy.spatial.distance.jensenshannon(θ_i, θ_j, base=2) 直接返回——须明确区分: Jensen-Shannon 散度 (JSD) 本身是 KL 散度的对称化、平滑版本, 而 scipy 该函数按其官方语义返回的是 Jensen-Shannon 距离, 即 JSD 的平方根 √JSD, 二者数值不等 (JSD = (√JSD)²)。以 2 为底时 √JSD 严格落入 [0,1] 区间 (√JSD=0 表示两分布完全一致, √JSD=1 表示两分布支撑完全不相交), 相似度按惯例定义为 1 − √JSD (而非 1 − JSD), 因而 strat_sim_max_lda 本身值域是 [0,1], 与文档口径披露 (fix omni-g-strategic-02/03, 2026-06-11) 中"TF-IDF/LDA 轨 (非负向量/分布) ∈ [0,1]"的表述一致——这一点与 Embedding 轨的姊妹列 strat_sim_max_emb 形成鲜明对照: 余弦相似度理论真值域是 [-1,1], 该轨此前曾被误 clip 到 [0,1] (值域删失, 负余弦被地板到 0), 已于该次修复中改正为按真值域处理。第三步, 对每家银行-年, 在同期全部其余银行中取相似度最大的一个作为 strat_sim_max_lda_i,t = max_{j≠i} [1 − √JSD(θ_i,t, θ_j,t)]。分词器口径披露 (fix inject-fintech-word-lda, 2026-06-21): 全部 LDA 列 (含本列) 与全部 word 级 TF-IDF 列自该次修复起统一改用注入 607 个金科关键词的独立分词器 (_get_diff_tokenizer), 使"金融科技""区块链"等领域复合词在分词阶段整词保留而不被拆散为单字或误切分, 与 char 轨、Embedding 轨对领域词汇的感知口径保持一致; 该口径变更只影响 word/LDA 两个轨道的分词输入, char 轨与 Embedding 轨字节不受影响。

【文献定位】
本家族方法学谱系的直接源头是 Hoberg & Phillips (2016, Journal of Political Economy) 的文本网络行业 (TNIC) 分类框架, 该文首次证明可以脱离静态 SIC/NAICS 行业代码, 用企业自我描述文本的向量相似度动态刻画产品市场重叠, 本仓库把这一思路迁移到银行-金科报道语料, 用 LDA 主题分布替代产品描述词袋, 用 Jensen-Shannon 散度替代余弦距离, 因而是同一构念族在不同文本表征与不同相似度度量下的方法学延伸。战略定位相似度/差异度的绩效含义参照 Haans (2019, Strategic Management Journal) 关于"在同质与异质品类下差异化对绩效影响"的理论讨论, 以及 Su, Gao & Tan (2024, Strategic Management Journal) 关于企业在竞争与制度双重压力下追求"最优区分度"(optimal distinctiveness) 的最新证据——这两篇论文共同的理论直觉是, 战略相似度既非越高越好也非越低越好, 与同行的定位重叠或定位区分度都会因语境不同而产生不同的绩效含义, 因此本测度体系提供 strat_sim_max (最相似) / strat_diff_n5 (局部平均差异) / centroid_diff (全局定位偏离) 三种几何刻面供后续实证按理论假设灵活选用, 而非预设单一方向的"越大越好"或"越小越好"。方法学基座上, Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 对"文本作为数据"的系统性方法论综述为本仓库采用 LDA/TF-IDF/Embedding 三种并行文本表征提供了一般性方法论依据, 明确指出不同文本表征方法在捕捉语义相似度时各有侧重、理应互相印证而非相互替代, 这也是本仓库将 char/word/LDA/Embedding 四条相似度测度并列而非坍缩为单一"最优"方法的方法学出发点; 主题模型本身的技术源头是 Blei, Ng & Jordan (2003) 的经典 LDA 论文 (未纳入本文件白名单引文池, 仅作背景技术脚注)。用文本刻画企业战略定位这一路径, 也呼应 Guzman & Li (2023, Management Science) 对"创业战略测量"提出的方法论框架——该文主张从企业早期文本描述中提炼可比的战略定位向量, 以替代人工编码或粗粒度行业代码, 与本仓库把银行-金科报道文本转成 LDA 主题分布、再用分布间相似度刻画战略定位重叠的做法, 在"用规模化文本提取替代主观编码的战略定位量表"这一方法论取向上是一致的, 二者的差别只在于 Guzman & Li 处理的是企业自我描述而本仓库处理的是第三方新闻报道文本。 沿着同一不预设方向的立场, Phillips、Edwards 与 Rutherford (2025) 在新创企业命名情境下检验趋同与差异化的张力, 并提出二者可经由认知中介机制同时带来合法性, 而非单纯的此消彼长, 这与上文「战略相似度既非越高越好也非越低越好」的判断互为呼应, 为本列以 1 − √JSD 刻画的「与最相似同业的主题分布重叠」提供了理论张力上的当代支撑: 主题重叠既可读作合法性来源, 也可读作定位区隔的缺失, 方向留待下游回归识别。边界上, 该文处理的是新创企业名称的静态命名选择、DV 为合法性知觉, 全文未使用任何文本向量, 更未涉及 LDA 主题分布或 Jensen-Shannon 距离, 单位与语境非银行、非中文新闻, 故本处只锚构念张力、不锚测度算子。
## VAR: strat_sim_max_lda

【变体差分】
本列是家族的 canonical (full) 轨实现: 输入文本取自 stage 14 物化的 content_full (标题 + 完整正文), 不做实体窗口截断或同句共现过滤, 参与 LDA 拟合与相似度计算的语料池是同期全部通过 stage 21 留篇门控 (llm_verified_full == True, 2026-06-29 起门控口径为 full-only) 的银行-年文本, 即行宇宙以 full 轨的留篇集为准, ctx/ss 两轨是该行宇宙子集上的 conditional-on-full 测度/稳健性轨。作为 full 轨, 本列与同族 _ctx / _ss 两个变体各自独立拟合各自轨道的 LDA 模型、各自计算轨道内的相似度最大值, 三者是并排的、互为稳健性检验的测度而非层级关系或替代关系——不存在"以 full 为主、ctx/ss 为补充"的先后次序, 铁律要求三者各自 just-identified 并排使用, 禁止混入同一个 over-identified 的 Hansen J 过度识别检验框架。值域仍是 [0,1], 数值上限受同期银行样本量约束 (银行数越多, 出现高相似度近邻的概率越高); 当某年参与拟合的银行数过少 (如仅 1 家), max 运算无有效对手方, 该银行-年该列会退化为缺失。分词器采用注入 607 金科关键词的独立分词器 (与家族 word/LDA 轨口径一致), 领域复合词整词保留, 不受 char 轨影响。作为三轨中语料覆盖面最宽的一支, full 轨相似度对全文中与银行战略定位弱相关的段落 (如免责声明、行业通稿套话) 更敏感, 这正是需要 ctx/ss 两条更聚焦轨道并排稳健性检验的动机所在。

## VAR: strat_sim_max_lda_ctx

【变体差分】
本列是家族的 ctx (entity-context window) 轨变体: 输入文本取自 stage 14 物化的 content_ctx, 即标题 + 目标实体 (银行) 周边窗口文本, 而非全文, 目的是把 LDA 主题拟合的输入聚焦在与目标银行直接相关的语境片段, 抑制长篇报道中与银行战略定位无关的段落对主题分布的稀释。ctx 轨自身有回退语义: 当某篇报道不存在可界定的实体窗口 (即无法从原文中框出围绕目标银行的局部上下文) 时, content_ctx 退化为全文 body, 并置位 ctx_is_fallback=True, 该行在分母 n_articles 的计算口径上与非回退行共享统计口径, 不做特殊剔除。本列与 canonical (full) 轨及 _ss 轨是三者并排、互为稳健性的关系, 各轨各自独立拟合 LDA 模型、各自在轨内计算相似度最大值, 三者不得混入同一个 over-identified Hansen J 框架联合估计。ctx 轨的行宇宙是 stage 21 full-only 留篇门控下的子集 (conditional-on-full), 而非独立的留篇判定; 换言之, 是否算作"一篇有效银行-金科报道"仍只看 full 轨的 LLM 验证结果, ctx 只是在该行宇宙上换一种文本截取口径重算 LDA 相似度, 用以检验 full 轨结论是否对"是否纳入无关段落"这一测量选择敏感。分词器同样采用注入 607 金科关键词的独立分词器, 与 full/ss 两轨口径一致, 保证三轨之间的差异只来自文本截取窗口而非分词规则。

## VAR: strat_sim_max_lda_ss

【变体差分】
本列是家族的 ss (same-sentence) 轨变体: 输入文本取自 stage 14 物化的 content_ss, 即标题 + 银行与金科关键词同句 (±N 句窗口, 默认 N=1, 见 config/filtering.yaml::context_window.ss_sentence_radius) 共现的句子集合, 是三轨中语境窗口最窄、聚焦度最高的一支, 用于刻画报道中银行与金融科技话题直接绑定出现的局部语义定位相似度。ss 轨的回退语义镜像 ctx 轨: 当某篇报道不存在银行∧金科同句共现时, content_ss 退化为全文 body, 并置位 ss_is_fallback=True, 与 ctx_is_fallback 共享同一套"回退不剔除、分母 n_articles 口径一致"的处理原则; 若上游 FINTECH_AC (金科关键词自动机) 为 None, 则 *_is_fallback 全体置 True, 以优雅降级方式退化为等同于 full 轨的行为而不报错中断。本列与 canonical (full) 轨及 _ctx 轨三者并排、互为稳健性检验, 各自独立拟合各自轨内的 LDA 模型与相似度极值, 不得三轨混用进同一个 over-identified 的 Hansen J 联合识别框架; ss 轨判定不对称口径继承自 stage 13/14 的整体设计——银行侧采用否定词过滤+短名过滤, 金科侧采用裸 Aho-Corasick 607 词匹配, 该不对称性是共现抽取阶段的既有设计, 不改变本列作为相似度测度本身的计算逻辑。由于 ss 轨窗口最窄, 参与拟合的字符/词量最小, 主题分布估计的方差通常大于 ctx/ss 相对 full 更粗颗粒度的截取, 解读时应结合样本量与回退占比一并评估, 不宜孤立地把 ss 轨数值差异直接归因于"战略定位"本身的变化。

<!-- rendered-citations:begin -->
Guzman, J., & Li, A. (2023). Measuring Founding Strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-Based Network Industries and Endogenous Product Differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Su, J., Gao, X., & Tan, J. (2024). Positioning for optimal distinctiveness: How firms manage competitive and institutional pressures under dynamic and complex environment. Strategic Management Journal, 45(2), 333-361. https://doi.org/10.1002/smj.3549
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Phillips, D., Edwards, B. D., & Rutherford, M. W. (2025). Conformity or Differentiation: Optimal distinctiveness through mediating channels. Journal of Business Research, 189, 115154. https://doi.org/10.1016/j.jbusres.2024.115154
<!-- rendered-citations:end -->
