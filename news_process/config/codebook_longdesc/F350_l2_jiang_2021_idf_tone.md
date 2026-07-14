---
family_id: F350
columns:
- jiang_2021_idf_tone_app_ctx
- jiang_2021_idf_tone_app_full
- jiang_2021_idf_tone_app_ss
- jiang_2021_idf_tone_ctx
- jiang_2021_idf_tone_full
- jiang_2021_idf_tone_hw_ctx
- jiang_2021_idf_tone_hw_full
- jiang_2021_idf_tone_hw_ss
- jiang_2021_idf_tone_mw_ctx
- jiang_2021_idf_tone_mw_full
- jiang_2021_idf_tone_mw_ss
- jiang_2021_idf_tone_ss
- jiang_2021_idf_tone_std_ctx
- jiang_2021_idf_tone_std_full
- jiang_2021_idf_tone_std_ss
- jiang_2021_idf_tone_tech_ctx
- jiang_2021_idf_tone_tech_full
- jiang_2021_idf_tone_tech_ss
- jiang_2021_idf_tone_vw_ctx
- jiang_2021_idf_tone_vw_full
- jiang_2021_idf_tone_vw_ss
unit: "语调得分 (连续, 词典正负词 tf-idf 加权后逐篇归一化幅度, 理论域约 [-1,1]; bank-year 聚合口径按变体而定: 简单均值/加权均值/组内标准差)"
formula: 'jiang_2021_idf_score = Σ_w∈W(article) idf(w)·sign(w) / Σ_w∈W(article) idf(w) (词级 tf-idf 权重替代等权计数; sign(w) 取自 jiang_2021 词典正负极性; idf(w) 非单一 log(N/df(w)) 型权重, 而是三步管线: ① smooth idf, raw_idf(w)=log₁₀(N/(1+df(w))) 分母 1+df(w) 平滑防零除; ② 均值归一化, normalized_idf(w)=raw_idf(w)/mean(raw_idf); ③ Winsorize(P1, P99) 缩尾极端词权重)。bank-year 聚合: 无后缀/`_ctx`/`_ss` = mean(jiang_2021_idf_score, by bank-year, per track); `_std` = std(同上); `_vw` = Σ(jiang_2021_idf_score_w_sum)/Σ(mention_density) 关注度加权; `_mw` = Σ(jiang_2021_idf_score_mw_sum)/Σ(media_authority_weight) 媒体权威加权; `_hw` = Σ(jiang_2021_idf_score_hw_sum)/Σ(herd_weight) 从众/时间衰减加权; `_app`/`_tech` = mean(jiang_2021_idf_score), 限定子样本 (LLM locus 分类=应用场景/底层技术)。'
producer: pipeline\panel\encode.py (build_aggregation_dict / tf-idf 词权重聚合区块 C2, 约 L152-L172, L762-L772; VW/MW/HW 归一化区块 L2195-L2320; app/tech 类别切分聚合 L1560-L1600)
upstream: [pipeline\sentiment\tone_words.py (jiang_2021 词典与逐词 idf 计分), pipeline\panel\encode.py::DICT_NAMES, 14_materialize_ctx (content_ctx/content_ss 物化), stage 21 llm locus 分类 (app/tech 子样本切分来源)]
citations:
- {doi: 10.13821/j.cnki.ceq.2021.04.10, type: journal, authors: "姜富伟, 孟令超, 唐国豪", year: 2021, title: "媒体文本情绪与股票回报预测", venue: "经济学(季刊)", vol: "21", issue: "4", pages_or_artno: "1323–1344"}
- {doi: 10.1093/rof/rfab036, type: journal, authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W.", year: 2022, title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary", venue: "Review of Finance", vol: "26", issue: "3", pages_or_artno: "673–719"}
- {doi: 10.1016/j.jfineco.2013.08.018, type: journal, authors: "Jegadeesh, N., & Wu, D.", year: 2013, title: "Word Power: A New Approach for Content Analysis", venue: "Journal of Financial Economics", vol: "110", issue: "3", pages_or_artno: "712–729"}
- {doi: 10.2308/TAR-2020-0104, type: journal, authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J.", year: 2023, title: "Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements", venue: "The Accounting Review", vol: "98", issue: "7", pages_or_artno: "315–345"}
- {doi: 10.1108/eb026526, type: journal, authors: "Spärck Jones, K.", year: 1972, title: "A Statistical Interpretation of Term Specificity and Its Application in Retrieval", venue: "Journal of Documentation", vol: "28", issue: "1", pages_or_artno: "11–21"}
new_dois: []
---

## CORE

【构念与来源】
jiang_2021_idf_tone 家族测度的是姜富伟、孟令超、唐国豪 (2021, 《经济学(季刊)》) 构建的中文财经媒体情绪词典在单篇文章内经 tf-idf 词权重重加权后的语调得分, 再按银行-年份聚合为面板变量。姜富伟等 (2021) 的原始词典方法是对每篇报道内命中的正/负面词做等权计数, 得到 pos_ratio/neg_ratio 式的语调指标 (对应本仓库 `jiang_2021_tone{track}` 姊妹家族, 简单等权口径)。本家族是其 tf-idf 词级加权稳健性检验: 对每个命中词赋予该词在全语料的逆文档频率 (inverse document frequency, IDF) 作为权重, 再取正负号求加权和并归一化, 得到逐篇 `jiang_2021_idf_score{track}`。方法学动机直接锚定 Gentzkow, Kelly & Taddy (2019, JEL)《Text as Data》对 text-as-data 领域词权重方案的系统梳理: 等权计数隐含假设每个词的信息量相同, 而高频常见词 (如"银行""业务"等财经报道中泛滥出现的功能词) 即便被词典收录为正/负面词, 其区分力也天然弱于低频罕见词; tf-idf 加权用词的全库稀有度作为信息量代理, 对高频词降权、对低频词升权, 是文本分析中最经典的词级重要性重加权方案之一, 其数学根源可追溯到 Spärck Jones (1972,《Journal of Documentation》) 对 term specificity 的统计诠释, 即 IDF 权重的原始出处。该加权与本仓库同源的 `{dict}_idf_score` 逐词加权计分器共享同一套 IDF 表, 词典本身 (jiang_2021 词库) 与等权姊妹家族完全一致, 唯一差异在词级权重方案。

【方法学与计算】
逐篇计分发生在情感词典引擎 (`pipeline\sentiment\tone_words.py`) 与其上游 idf 权重计算 (`build_idf_weights`)。idf 权重并非单一步骤的 log(N/df(w)), 而是三步管线: 第一步 smooth idf, raw_idf(w) = log₁₀(N / (1+df(w))), 分母加 1 平滑防止 df(w)=0 时除零; 第二步均值归一化, normalized_idf(w) = raw_idf(w) / mean(raw_idf), 把全部词的权重规模统一到以 1 为均值的相对尺度, 避免语料规模 (N) 或 log 底数选择本身影响词间相对权重的可比性; 第三步 Winsorize(normalized_idf, P1, P99) 缩尾, 把落在第 1/第 99 百分位之外的极端权重值截断到分位数边界, 抑制个别超罕见词 (df(w) 极小导致 raw_idf 爆炸) 对篇章加权和的过度杠杆效应。逐篇扫描命中 jiang_2021 词典的正/负面词, 每个命中词按其 final_idf(w) 加权、按词典极性取正负号, 累加得到该篇的加权净情绪分, 再除以命中词 idf 权重总和做归一化, 得到 `jiang_2021_idf_score{track}` ∈ 理论域约 [-1,1] (与等权姊妹 `jiang_2021_score{track}` 同域但数值一般不同, 因为高频功能词被系统性降权)。词典规则本身 (否定翻转/程度副词/转折句式三条状态机规则) 与等权姊妹家族共用同一套语言学规则引擎, 本家族只替换词级权重方案, 不改变规则消融维度 (规则消融梯度是另一条正交轨, 见 CLAUDE.md「词典消融梯度」, 与本 idf 加权轨不交叉)。
面板聚合环节由 `pipeline\panel\encode.py::build_aggregation_dict` 的 C2 区块 (约 L762-L772) 与 VW/MW/HW 归一化区块 (L2195-L2320) 完成, 分两族:
第一族是「聚合权重」的三个变体 — `_vw` (value-weighted, 以 `mention_density` 即银行提及密度作为篇章权重的分母来源)、`_mw` (media-authority-weighted, 以媒体声誉三级 tier 权重 `media_authority_weight` 加权, 方法学锚定 Holzman, Miller & Twedt 2023,《The Accounting Review》对媒体权威加权 tone 的直接先例)、`_hw` (herd-weighted, 以从众/时间衰减权重 `herd_weight` 加权, 反映报道在信息传播中的"扎堆"衰减)。三者均先在文章级算出 `jiang_2021_idf_score{track} × weight` 的 bank-year 求和 (`_sum` 后缀中间列), 再除以对应权重的 bank-year 求和, 得到加权均值; 这与 `jiang_2021_idf_tone{track}` (无权重后缀, 篇章简单算术平均) 及 `_std{track}` (篇章层面组内标准差, 衡量银行-年份内报道语气的离散度) 共同构成"聚合方式"维度上的稳健性梯子, 彼此各自 just-identified, 互为稳健性、不分主次。
第二族是「子样本切分」的两个变体 — `_app` (限定 LLM locus 分类判定为"应用场景"的报道子集) 与 `_tech` (限定判定为"底层技术"的报道子集), 二者在 `build_aggregation_dict` 的类别聚合分支 (约 L1560-L1600) 内对同一 `jiang_2021_idf_score{track}` 源列做条件均值, 分类依据来自 stage 21 LLM locus 判定 (P4 Gomber 范式下的技术定位维度), 与 IDF 词权重方案本身正交 — app/tech 差分的是"算哪些篇章", vw/mw/hw/std 差分的是"怎么加权/怎么汇总", 无后缀/canonical 差分的是"聚合层面的简单均值"。

【文献定位】
本家族在方法学谱系上处于三条已核验先例的交汇点: ① 词典构造本体沿用姜富伟等 (2021) 的中文财经情绪词典, 是本仓库对中国语境金融文本情绪测度的本土化锚点之一, 与仓库内 bian_2021/du_2022/yao_2021/you_2018/loughran 等其余五部词典构成"多词典互为稳健性"矩阵 (`DICT_NAMES` 遍历, 各词典各自 just-identified 并排); ② tf-idf 词权重方案直接对应 Gentzkow, Kelly & Taddy (2019) 对 text-as-data 领域词权重技术的系统性综述, 是本仓库处理"高频泛义词稀释情绪信号"问题的标准应对; ③ IDF 权重的数学根源溯自 Spärck Jones (1972) 对 term specificity 的经典统计诠释。此外, `_mw` 变体直接呼应 Holzman, Miller & Twedt (2023) 对媒体权威加权语气的方法论先例, `_vw`/`_hw` 变体与仓库同名的其余词典/LLM 加权族共享同一套加权基础设施 (`sum_mention_density`/`sum_media_authority_weight`/`sum_herd_weight` 三个分母源), 三者均是跨情感测度方法 (词典法/LLM 三家投票/BERT 三模型) 通用的"聚合权重"稳健性维度, 而非 jiang_2021 词典独有。与仓库内 Du et al. (2022,《Review of Finance》) 中文金融情绪词典、Jegadeesh & Wu (2013,《Journal of Financial Economics》) 提出的 word power 内容分析法互为方法学参照, 三者均属"词典法 vs 加权改进版词典法"这一测度谱系, 共同支撑 P1 银行-金科语调 (`bank_fintech_tone`) 主线论文将 jiang_2021 词典法作为 LLM 三家投票之外的独立测度路径纳入跨方法一致性检验 (Krippendorff's alpha / Cohen kappa)。

三轨口径 (full/ctx/ss) 铁律: `jiang_2021_idf_tone_full` 以全文 (`content_full`=标题+正文) 为扫描域, `jiang_2021_idf_tone_ctx` 以实体窗口 (`content_ctx`=标题+银行/金科实体窗口) 为扫描域, `jiang_2021_idf_tone_ss` 以银行∧金科同句共现窗口 (`content_ss`, 默认 ±1 句半径) 为扫描域; `_ss` 的回退语义镜像 `_ctx`: 当某篇文章无银行∧金科同句共现时, `content_ss` 退化为全文 body 且共享分母的 `ss_is_fallback` 标记为 True, 优雅降级而非产出缺失值。三轨各自 just-identified 并排、互为稳健性、不分主次, 铁律要求禁止将三轨测度混入同一个 over-identified 的 Hansen J 检验; 留篇门控 (是否判定某篇报道为"一篇有效的银行-金科报道") 一律以 full 轨 LLM 验证结果 (`llm_verified_full`) 为准 (2026-06-29 full-only 门控切换), ctx/ss 轨的 `jiang_2021_idf_tone` 系列是"以 full 留篇集为行宇宙"的条件测度/稳健性轨, 而非独立样本。同理, `_vw`/`_mw`/`_hw`/`_std`/`_app`/`_tech` 六个衍生维度彼此正交、各自 just-identified 并排 (聚合权重维度与子样本切分维度互不重叠, 均与三轨维度正交), 不得将任意两个衍生维度混入同一个过度识别的 Hansen J/GMM 检验设定; 在跨方法稳健性叙事中, 应将其视为一组"互相印证、彼此独立"的测度矩阵单元, 而非单一测度的多个候选替代。

## VAR: jiang_2021_idf_tone_app_ctx

【变体差分】
本列在「子样本切分=应用场景 (app)」×「三轨=实体窗口 (ctx)」两个维度上定位: 分子源列限定于 stage 21 LLM locus 分类判定为"应用场景" (金科在报道中体现为具体业务应用而非底层技术研发/基础设施) 的报道子集, 扫描文本域为 `content_ctx` (标题+银行/金科实体窗口), 聚合方式为该子集内 `jiang_2021_idf_score_ctx` 的简单算术均值, 不做 vw/mw/hw 加权、不做标准差统计。与 `jiang_2021_idf_tone_tech_ctx` (底层技术子集, 同轨) 构成 P4 Gomber locus 范式下"应用 vs 技术"语调差异的直接对照; 需特别说明, 仓库内 `tone_gap_tech_app_lc_ctx` 诊断量 (encode.py ctx 轨对角线聚合区块) 并非由本列 (`jiang_2021_idf_score_ctx`) 相减构成, 而是硬编码取 `llm_vote_tone_tech_lc_ctx` 与 `llm_vote_tone_app_lc_ctx` 两个 LLM 三家投票语调列相减 — 即该差距量走的是 stage 21 LLM 情感路径而非本词典 idf 加权路径; 与 `jiang_2021_idf_tone_app_full`/`jiang_2021_idf_tone_app_ss` 构成三轨稳健性并排, 与全样本 canonical `jiang_2021_idf_tone_ctx` 相比是行宇宙更窄的条件子集测度 (n 更小, 银行-年份内 app 类报道不足最小篇数阈值时该列取 NaN, 是预期的稀疏退化而非缺陷)。
使用该列时应注意两点解读边界: 第一, "应用场景"这一子样本标签本身来自 stage 21 LLM 三家投票对报道 locus 维度的分类判定, 而非本家族词典法自身产出, 因此该列的样本构成质量 (是否真正区分出应用型报道) 依赖上游分类器的准确度, 与词典语调计分本身无直接关联, 二者是两条独立的方法学环节串联而非同一测度重复; 第二, 由于分子分母都限定在实体窗口 (ctx) 扫描域内, 该列同时叠加了"文本范围收窄"与"样本子集收窄"两重效应, 数值上不宜直接与 `jiang_2021_idf_tone_app_full` 做水平比较, 而应各自作为独立的稳健性单元解读方向一致性。在跨模型/跨方法的一致性检验中 (例如与 LLM locus 分类下的 `llm_vote_tone_app_ctx` 对照), 本列提供了词典法路径下的平行印证, 二者若方向一致可增强"应用场景报道语调普遍偏正/偏负"这一结论的稳健性, 若方向不一致则提示测度方法间存在系统性分歧, 需结合样本量与词典覆盖率进一步诊断, 而非简单取其一为准。

## VAR: jiang_2021_idf_tone_app_full

【变体差分】
本列在「子样本切分=应用场景 (app)」×「三轨=全文 (full)」两个维度上定位: 扫描文本域为 `content_full` (标题+全文正文), 分子源列限定于 LLM locus 判定为"应用场景"的报道子集, 聚合方式为该子集内 `jiang_2021_idf_score_full` 的简单算术均值。作为 full 轨的 app 子样本测度, 它与留篇门控 (`llm_verified_full`) 共享同一行宇宙锚点 — 全部三轨 app 变体的分母都以 full 轨判定的"有效银行-金科报道"集合为基准再做 locus 二次切分, 而非各轨独立招募样本。与 `jiang_2021_idf_tone_tech_full` 构成同轨技术-应用对照, 与 `jiang_2021_idf_tone_app_ctx`/`jiang_2021_idf_tone_app_ss` 构成三轨并排稳健性, 三者禁止混入同一 Hansen J。
本列是三个 app 子样本变体中样本量最大、覆盖面最宽的一支, 因为 full 轨扫描全文而非仅实体窗口或严格同句窗口, 命中词典正/负面词的机会更多, 词级 idf 权重的稀释效应也更充分体现 — 高频功能词在全文中出现次数最多, 被系统性降权的幅度也最大, 因此本列相对等权姊妹列 `jiang_2021_tone_app_full` 的数值偏离通常比 ctx/ss 两轨更明显。在 P4 Gomber locus 范式的应用场景论证中, 本列常作为最主要的证据来源 (行宇宙最完整), ctx/ss 两轨则提供"收窄扫描域后结论是否依然成立"的补充稳健性检验; 三者应联合报告而非只报告 full 轨, 以避免因单一扫描域的偶然噪声驱动结论。此外, 该列继承了 full 轨留篇门控的全部性质: 只要该篇报道被 `llm_verified_full` 判定为有效银行-金科报道且 locus 分类为应用场景, 无论其在 ctx/ss 轨是否满足更严格的窗口判据, 都会计入本列的分子分母, 这是本列区别于 app_ctx/app_ss 两列在"行宇宙宽窄"上的核心差异。

## VAR: jiang_2021_idf_tone_app_ss

【变体差分】
本列在「子样本切分=应用场景 (app)」×「三轨=同句共现 (ss)」两个维度上定位: 扫描文本域为 `content_ss` (标题+银行∧金科同句共现窗口, 默认 ±1 句半径), 分子源列限定于 LLM locus 判定为"应用场景"的报道子集。当某篇文章不存在银行∧金科同句共现时, `content_ss` 回退为全文 body 且 `ss_is_fallback` 置 True, 镜像 `_ctx` 轨的回退语义, 而非产生系统性缺失; 在 T=2 开发集小样本下, app×ss 双重切窄 (子样本 + 严格同句窗口) 极易导致银行-年份内合格篇数不足, 该列大量取 NaN 属预期稀疏退化, 生产语料 (T=18, 1700 万篇级) 下样本量回升后应显著缓解。与 `jiang_2021_idf_tone_tech_ss` 构成同轨技术-应用对照, 与另两轨 app 变体互为稳健性并排。
本列的构念意义在于: 同句共现判据 (银行与金科词必须出现在同一句内) 本身是对"该篇报道是否真的在讨论银行与金科的直接关系"最严格的过滤器, 而应用场景子集又进一步要求该关系被 LLM 判定为业务应用层面 (而非底层技术研发), 两层过滤叠加后剩余样本代表的是"银行与金科应用场景在同一句紧密关联"的高置信度报道, 信噪比理论上最高但样本规模最小。研究者在解读本列时应重点关注其"高精度、低召回"的特性: 若本列与 app_full/app_ctx 两列在方向上高度一致, 则说明应用场景语调结论对扫描域收窄具有强稳健性, 是最有力的证据; 若因样本过小导致该银行-年份大量取 NaN, 不应将其解读为"该银行-年份无应用场景报道", 而应结合另两轨的非缺失结果综合判断。三轨 app 变体在回归设定中应各自作为独立稳健性列并排报告, 不应因 ss 轨样本量小而弃用, 也不应将三轨结果强行合并为单一指标。

## VAR: jiang_2021_idf_tone_ctx

【变体差分】
本列是家族在「实体窗口轨 (ctx)」上的 canonical 简单均值口径: 不做子样本切分 (app/tech)、不做加权聚合 (vw/mw/hw)、不做离散度统计 (std), 仅对全部纳入 ctx 轨留篇集的报道 `jiang_2021_idf_score_ctx` 取银行-年份简单算术均值。扫描文本域 `content_ctx` = 标题 + 银行/金科实体窗口 (由 stage 14 `ctx_materializer` 物化), 与 `content_full` (全文) 相比聚焦于实体附近语境, 降低无关段落对情绪测度的稀释。作为 full-only 门控下的条件稳健性轨, 其行宇宙锚定于 full 轨 `llm_verified_full` 留篇集合, 与 `jiang_2021_idf_tone_full`/`jiang_2021_idf_tone_ss` 构成三轨并排 (禁混同一 Hansen J), 与等权姊妹家族 `jiang_2021_tone_ctx` 构成"是否 tf-idf 词权重"维度上的稳健性对照。
本列在实践中的核心价值是提供"聚焦于实体附近语境后, 语调测度是否依然稳健"的检验: 全文轨可能因报道中夹杂大量与银行/金科无直接关系的背景段落 (如宏观经济评论、行业综述) 而稀释真正针对该银行的情绪信号, 实体窗口轨通过截取标题与银行/金科实体前后一定窗口的文本, 更聚焦地捕捉"该篇报道对该银行本身的评价语气"。与全文轨 canonical `jiang_2021_idf_tone_full` 相比, 本列在样本量上完全一致 (行宇宙同为 full 轨留篇门控确定), 唯一差异是文本扫描范围; 二者若数值高度相关, 说明全文中的背景段落对语调测度影响有限, 反之则提示全文轨可能混入了非目标语境的情绪噪声, 应优先采信 ctx 轨结果或在稳健性附录中同时披露两轨差异。本列同时是 `_vw_ctx`/`_mw_ctx`/`_hw_ctx`/`_std_ctx`/`_app_ctx`/`_tech_ctx` 六个 ctx 轨衍生列的简单均值基准, 理解这些衍生列前应先锚定本列的口径。

## VAR: jiang_2021_idf_tone_full

【变体差分】
本列是家族的 canonical 主口径 (全文轨简单均值): 扫描文本域为 `content_full` (标题+全部正文), 不做子样本切分、不做加权聚合、不做离散度统计, 对全部 full 轨留篇集报道的 `jiang_2021_idf_score_full` 取银行-年份简单算术均值。它是本家族在三轨中的首要参照口径 (full-only 留篇门控直接建立在此轨之上), 也是其余 20 个衍生列 (三轨×子样本、三轨×加权、三轨×std) 的锚点基准: 任何变体的差异都应相对于本列的 full-canonical 值理解为"聚合方式变了"或"扫描域变了"或"样本子集变了", 而非彼此互为上位替代。与等权姊妹家族 canonical 列 `jiang_2021_tone_full` 相比, 差异纯粹来自词级 tf-idf 加权 vs 等权计数, 二者互为稳健性、不分主次。
在 P1 银行-金科语调主线论文中, 本列作为词典法路径的首要报告口径, 与 LLM 三家投票共识 `llm_vote_tone_full` (P1 treatment.primary) 及 BERT 三模型路径构成"三方法互为稳健性"矩阵中的一个方法学分支; 三种测度方法 (词典法/LLM/BERT) 各自捕捉情绪信号的机制不同 (词典法依赖预先构造的正负词表与语言学规则, LLM 依赖上下文语义理解, BERT 依赖预训练语言模型的微调判别), 若三者在同一批银行-年份上方向一致, 可显著增强研究结论对测度方法选择的稳健性; 若不一致, 词典法作为最透明、最可复现、无模型漂移风险的基准方法, 常被用作解释三方法分歧来源的诊断锚点。本列相对等权计数版本额外具备"高频泛义词降权"的优势, 在中文财经报道普遍存在大量套话/模板化措辞的语境下 (参见仓库 boilerplate 套话比率测度), 这一降权机制有助于进一步提纯真正承载情绪信息的词汇贡献。

## VAR: jiang_2021_idf_tone_hw_ctx

【变体差分】
本列在「聚合权重=从众/时间衰减加权 (herd-weighted, hw)」×「三轨=实体窗口 (ctx)」两个维度上定位: 分子为 `jiang_2021_idf_score_hw_sum_ctx` (逐篇 idf 语调分乘以该篇 `herd_weight_ctx` 后按银行-年份求和), 分母为 `sum_herd_weight_ctx` (对应权重的银行-年份求和), 二者相除得到 herd-weight 加权均值。herd_weight 捕捉报道在时间/来源上"扎堆"程度的衰减权重 — 短期内大量雷同报道会被系统性降权, 抑制"媒体一窝蜂跟风报道"对语调测度的机械性放大, 与等权简单均值 canonical `jiang_2021_idf_tone_ctx` 构成聚合方式维度上的稳健性对照。若某银行-年份缺失 `sum_herd_weight_ss` 上游源列 (ss 轨 herd_weight 未计算), 依 encode.py 的守卫逻辑该列 (以及 ss 轨同族列) 优雅退化为 NaN, ctx 轨本身不受影响。
herd_weight 权重的构造逻辑源自对媒体报道"羊群效应"的经济学直觉: 当某一负面/正面事件发生后, 短时间窗口内大量媒体会跟风转载或改写同一条新闻线索, 若不加区分地等权纳入聚合, 会让"报道条数"而非"独立信息含量"主导银行-年份语调水平, 制造虚假的情绪强度信号。本列通过对时间上扎堆出现的雷同报道做衰减降权, 试图逼近"独立信息增量"意义上的语调测度, 与仓库内 herd_decay_processor (stage 24) 产出的从众衰减权重体系一脉相承。使用本列时应注意其与 `_vw_ctx` (关注度加权) 的区别: vw 权重反映的是单篇报道内部对该银行的提及密度, herd 权重反映的是该篇报道相对于同期其他报道的独立性, 二者关注的"扎堆"维度不同 (一为篇内提及密度, 一为篇际时间聚集度), 不可互相替代, 应联合报告以覆盖不同的稳健性关切。

## VAR: jiang_2021_idf_tone_hw_full

【变体差分】
本列在「聚合权重=从众/时间衰减加权 (hw)」×「三轨=全文 (full)」两个维度上定位: 分子为 `jiang_2021_idf_score_hw_sum_full`, 分母为 `sum_herd_weight_full`, 相除得到全文轨 herd-weight 加权均值。与 canonical `jiang_2021_idf_tone_full` (简单均值) 相比, 本列对短期内扎堆报道的贡献做时间衰减降权, 更贴近"独立信息增量"而非"报道次数"驱动的语调测度; 与 `jiang_2021_idf_tone_hw_ctx`/`jiang_2021_idf_tone_hw_ss` 构成三轨并排稳健性, 三者禁止混入同一 over-identified 检验设定。
本列作为 full 轨的 herd-weight 加权口径, 在覆盖面上与 canonical `jiang_2021_idf_tone_full` 一致 (行宇宙同为 full 轨留篇门控), 唯一差异在聚合权重方案, 因此本列可视为对 canonical 均值口径最直接的一个稳健性替代: 若二者数值高度相关且方向一致, 说明该银行-年份的语调水平不受"是否存在短期扎堆报道"影响, 结论稳健; 若二者出现明显背离, 通常提示该银行-年份内存在若干条被大量转载的头条事件报道, 拉动等权均值偏离独立信息含量意义上的真实语调水平, 此时应优先参考本列或在文中披露差异来源, 并结合原始报道时间分布做进一步核查。本列与 mw_full/vw_full 两个加权变体共同构成 full 轨的完整聚合权重梯子, 三者应联合作为稳健性附录表格的相邻列呈现。

## VAR: jiang_2021_idf_tone_hw_ss

【变体差分】
本列在「聚合权重=从众/时间衰减加权 (hw)」×「三轨=同句共现 (ss)」两个维度上定位: 分子为 `jiang_2021_idf_score_hw_sum_ss`, 分母为 `sum_herd_weight_ss`。encode.py 明确将 ss 轨 herd_weight 分母处理为条件加入 (`hw_denom_by_track` 仅在 `sum_herd_weight_ss` 存在时才注册该轨), 缺失时该列及其分子分母同族列一并优雅退化为 NaN, 而非借用 full 轨分母 (三轨分母严格逐轨对齐, 不跨轨借用, 镜像仓库内网络三轨列的分母口径铁律)。`content_ss` 的回退语义与其余 ss 轨列一致: 无同句共现时退化为全文 body 且 `ss_is_fallback` 置 True。
本列是三轨 herd-weight 加权变体中样本量最小、判据最严的一支, 同时叠加了"同句共现"文本域收窄与"从众衰减"权重下调两重效应。在实证使用中应将本列视为对 hw_full/hw_ctx 两列结论的"强判据检验": 如果一个语调结论在扫描域最宽 (full)、权重最松的口径下成立, 但在样本最少、判据最严、又叠加从众衰减的本列下依然方向一致 (即便统计显著性因样本量下降而减弱), 说明该结论具有相当强的稳健性; 反之若本列因样本过小而大量取 NaN 或方向逆转, 不应单独据此否定 full/ctx 两轨的结论, 而应在稳健性附录中如实披露样本规模差异, 避免读者误将样本量效应误读为经济效应的消失。

## VAR: jiang_2021_idf_tone_mw_ctx

【变体差分】
本列在「聚合权重=媒体权威加权 (media-authority-weighted, mw)」×「三轨=实体窗口 (ctx)」两个维度上定位: 分子为 `jiang_2021_idf_score_mw_sum_ctx` (逐篇 idf 语调分乘以该篇来源媒体的三级权威度 tier 权重 `media_authority_weight_ctx` 后求和), 分母为 `sum_media_authority_weight_ctx`。媒体权威加权的方法学动机直接对应 Holzman, Miller & Twedt (2023,《The Accounting Review》) 对"高权威媒体的语气应获得更大市场解读权重"的实证先例, 抑制低权威/边缘媒体噪声对银行-年份语调测度的稀释。与等权 canonical `jiang_2021_idf_tone_ctx` 构成聚合权重维度上的对照, 与 `jiang_2021_idf_tone_mw_full`/`jiang_2021_idf_tone_mw_ss` 构成三轨并排。
媒体权威三级 tier 权重的构造依据是仓库内媒体来源库对全部纳入语料的 3,740 家媒体 (原始普查口径) 按声誉/公信力/发行覆盖面分级, 权威度越高的媒体在聚合中获得越大的权重份额, 方法学动机与 Holzman, Miller & Twedt (2023) 在盈余公告披露纪律研究中对媒体权威加权语气的直接实证先例相符。本列聚焦实体窗口扫描域, 相比全文轨 mw 变体, 在权威加权基础上叠加了"仅看银行/金科实体附近文本"的语境收窄, 二者若结论一致可增强"权威媒体对该银行金科相关业务的评价"这一构念的稳健性。媒体权威度作为媒体来源层面的静态属性, 不随扫描域宽窄 (full/ctx/ss) 或情感测度方法 (词典法/LLM/BERT) 变化, 因此本列与全文轨/同句轨 mw 变体的权重定义完全一致, 差异纯粹来自纳入聚合的文本范围与样本构成; 研究者若在 ctx 轨发现 mw 加权均值与等权均值 (`jiang_2021_idf_tone_ctx`) 出现明显背离, 通常提示该银行-年份内权威媒体与边缘媒体在"银行/金科实体附近语境"上的用词倾向存在系统性分化, 值得结合原始报道来源结构进一步核查, 而非简单归因于权重方案本身的不稳定。

## VAR: jiang_2021_idf_tone_mw_full

【变体差分】
本列在「聚合权重=媒体权威加权 (mw)」×「三轨=全文 (full)」两个维度上定位: 分子为 `jiang_2021_idf_score_mw_sum_full`, 分母为 `sum_media_authority_weight_full`。作为家族在 full 轨上的媒体权威加权口径, 它与 `jiang_2021_idf_tone_hw_full` (从众衰减加权) 在动机上互补而非重叠 — mw 权重针对"信源可信度"这一横截面维度, hw 权重针对"报道扎堆程度"这一时间维度, 二者均为聚合权重梯子的正交单元, 互为稳健性、不分主次。
本列在样本覆盖上与 canonical `jiang_2021_idf_tone_full` 一致, 是三个 mw 变体中样本量最大的一支, 适合作为主要报告口径。研究者在解读本列时应留意媒体权威权重是媒体来源层面的固定属性 (与具体报道内容无关), 因此该权重不随情绪测度方法 (词典法/LLM/BERT) 变化而变化, 是跨方法共享的聚合基础设施; 若 `jiang_2021_idf_tone_mw_full` 与同一权重方案下的 LLM 版本 `llm_vote_tone_mw_full` 或 BERT 版本呈现一致的媒体权威加权模式 (例如权威媒体语调普遍更审慎/更负面), 可为"高权威媒体对银行报道更谨慎"这一制度性假说提供跨方法印证, 该印证独立于任一具体情绪测度方法的模型假设。
本列与 vw_full/hw_full 两个 full 轨聚合权重变体应联合构成一张稳健性附录表格的相邻三列, 分别检验"篇内提及密度""信源权威度""篇际时间扎堆度"三个独立维度对语调水平结论的敏感性。若三列结果方向高度一致, 是对 canonical `jiang_2021_idf_tone_full` 均值口径最强的联合稳健性证据; 若某一列出现明显偏离, 应结合该权重的经济含义具体诊断偏离来源, 而非笼统归因于"加权方法不同", 例如 mw_full 偏离而 vw_full/hw_full 不偏离, 通常提示该银行-年份的报道来源结构存在权威媒体与非权威媒体语调系统性分化的现象, 值得单独展开描述性分析。

## VAR: jiang_2021_idf_tone_mw_ss

【变体差分】
本列在「聚合权重=媒体权威加权 (mw)」×「三轨=同句共现 (ss)」两个维度上定位: 分子为 `jiang_2021_idf_score_mw_sum_ss`, 分母为 `sum_media_authority_weight_ss`。当 ss 轨对应的媒体权威权重上游列缺失或该银行-年份 ss 轨留篇数为零时, 分母/分子同步退化为 NaN, 不借用 full 或 ctx 轨的权重数据。`content_ss` 回退语义同其余 ss 轨列: 无银行∧金科同句共现的报道计入回退全文口径, `ss_is_fallback` 置 True, 分母 (`n_articles`) 与其余 ss 轨列共享。
本列与 hw_ss 变体共同构成 ss 轨聚合权重梯子中样本量最受限的两支, 二者的差异在于权重来源 (媒体权威 vs 时间从众衰减) 而非文本域, 二者若能在同一批银行-年份上给出一致方向, 是对"银行-金科同句紧密关联报道的语调水平"这一构念最强的稳健性证据组合。由于媒体权威权重是媒体来源层面的静态属性, 其在 ss 轨与 full/ctx 轨的取值口径完全一致 (同一篇文章无论落入哪个文本扫描轨, 其来源媒体的权威度不变), 因此 mw_ss 相对 mw_full/mw_ctx 的差异纯粹来自样本构成 (哪些文章满足同句共现判据), 而非权重定义本身的变化, 这是理解三轨 mw 变体差异来源的关键。本列在实证报告中通常与 hw_ss/vw_ss 同框呈现, 三者共同构成 ss 轨聚合权重梯子的完整集合; 由于 ss 轨样本量普遍偏小, 三者若能相互印证方向一致, 是"银行-金科同句紧密关联报道语调"这一细粒度构念在聚合权重选择上稳健的强证据, 应优先在正文而非仅稳健性附录中呈现, 以体现该构念不依赖任一特定权重方案的选择。

## VAR: jiang_2021_idf_tone_ss

【变体差分】
本列是家族在「同句共现轨 (ss)」上的 canonical 简单均值口径: 扫描文本域为 `content_ss` (标题+银行∧金科同句共现窗口, 默认 ±1 句半径, `config/filtering.yaml::context_window.ss_sentence_radius`), 不做子样本切分、不做加权聚合、不做离散度统计, 对 ss 轨留篇集报道的 `jiang_2021_idf_score_ss` 取银行-年份简单算术均值。ss 轨是三轨中判据最严格的一支 (要求银行与金科词在同一句内共现, 而非仅在实体窗口或全文内出现), 因而样本量通常小于 ctx/full 两轨; 缺共现时回退为全文 body 且 `ss_is_fallback` 置 True, 与 `_ctx` 轨回退语义完全镜像。作为三轨并排之一, 本列不得与 `_full`/`_ctx` 两列混入同一过度识别的 Hansen J 检验。
本列在三轨中样本量最受限但精度最高, 是研究"银行与金科在直接文本关联下的媒体口径"最保守也最不容易受无关背景段落污染的口径。由于同句共现判据要求银行名与金科相关词在同一自然语句内出现, 本列受益于最低的"话题漂移"风险 — 报道全文可能同时涉及多个话题 (如宏观政策、行业动态、公司治理), 而同句窗口几乎必然是围绕"该银行的金科相关事项"展开的核心叙事句, 因此 `jiang_2021_idf_tone_ss` 的信噪比理论上高于 ctx 与 full 两轨, 代价是样本量随判据收紧而系统性下降。在稳健性附录中, 研究者常将本列作为"高精度低召回"极端, 将 `jiang_2021_idf_tone_full` 作为"低精度高召回"极端, ctx 轨居中, 三者共同勾勒出扫描域收紧对结论稳健性的影响曲线。

## VAR: jiang_2021_idf_tone_std_ctx

【变体差分】
本列在「聚合方式=组内标准差 (std)」×「三轨=实体窗口 (ctx)」两个维度上定位: 对银行-年份内全部 ctx 轨留篇报道的 `jiang_2021_idf_score_ctx` 取样本标准差 (而非均值), 度量的是该银行-年份内媒体语调的离散程度/分歧度, 而非语调水平本身。与 canonical `jiang_2021_idf_tone_ctx` (均值, 衡量"语调多正/多负") 是互补而非替代关系, 常用于刻画"媒体报道口径是否一致"这一独立构念 (与仓库内 bank_media_disagreement 衍生 paper 的分歧度测度精神一致但不同源); 银行-年份内合格篇数 < 2 时标准差无法定义, 该列取 NaN 属预期。
研究者应避免将本列与均值列 `jiang_2021_idf_tone_ctx` 视为同一构念的两个候选替代, 二者衡量的是完全不同的统计矩: 均值刻画"中心趋势" (语调整体偏正或偏负), 标准差刻画"离散程度" (报道口径是否统一)。一个银行-年份可能同时呈现"均值接近中性"与"标准差很高"的组合, 这通常意味着该期间该银行同时受到正面 (如业务创新报道) 与负面 (如合规处罚报道) 事件的媒体关注, 若只看均值容易误判为"媒体态度中立", 实际上是"媒体态度两极分化"; 本列正是为捕捉这类情形而设计, 在解释银行声誉波动/媒体关注度不稳定等构念时应优先纳入而非省略。

## VAR: jiang_2021_idf_tone_std_full

【变体差分】
本列在「聚合方式=组内标准差 (std)」×「三轨=全文 (full)」两个维度上定位: 对 full 轨留篇集报道的 `jiang_2021_idf_score_full` 取银行-年份组内标准差。作为三个 std 变体中样本量通常最大的一支 (full 轨留篇门控是全部三轨的行宇宙锚点), 它是衡量银行-年份内报道语调分歧度最主要的口径; 与 `jiang_2021_idf_tone_std_ctx`/`jiang_2021_idf_tone_std_ss` 构成三轨并排稳健性。
本列在实证中常与均值列 `jiang_2021_idf_tone_full` 联合构成"均值-离散度"二维刻画: 若两个银行-年份的均值接近但标准差差异悬殊, 说明它们虽然"整体语调水平相近", 但媒体报道的一致性/分歧程度截然不同, 后者往往与更深层的构念 (如该银行是否处于舆论风口浪尖、是否存在监管调查等重大不确定性事件) 相关。由于本列基于全文轨 (样本量最大), 相对 ctx/ss 两个 std 变体, 其标准差估计的统计效率最高、受随机噪声干扰最小, 应作为分歧度维度的首选报告口径, ctx/ss 两轨作为收窄扫描域后离散度结论是否稳健的补充检验。
本列在跨方法一致性检验中同样具有价值: 若词典法路径 (本列) 与 LLM 三家投票路径的对应标准差列在同一批银行-年份上呈现相似的高/低分歧模式, 说明"该银行-年份报道口径分歧"这一现象并非某一测度方法的模型伪影, 而是媒体报道客观存在的语调异质性; 反之若仅词典法呈现高分歧而 LLM/BERT 路径未呈现, 需考虑是否是词典覆盖率不足或规则消融 (否定/程度/转折三条规则的组合) 导致的测度噪声放大, 而非真实的报道口径分歧, 此时应交叉核对该家族的规则消融梯度变体 (`_raw`/`_negonly` 等) 加以甄别。

## VAR: jiang_2021_idf_tone_std_ss

【变体差分】
本列在「聚合方式=组内标准差 (std)」×「三轨=同句共现 (ss)」两个维度上定位: 对 ss 轨留篇报道的 `jiang_2021_idf_score_ss` 取银行-年份组内标准差。ss 轨样本量最小 (判据最严), 银行-年份内合格篇数不足 2 篇的情形比 full/ctx 两轨更常见, 该列取 NaN 的比例预期高于另两个 std 变体, 在 T=2 开发集小样本下尤其明显, 属预期的稀疏退化而非产出缺陷。
尽管样本受限, 本列在生产语料规模 (T=18, 1700 万篇级) 下仍具有独立价值: 银行∧金科同句紧密关联的报道数量本身通常远小于泛泛提及银行的全部报道, 但这部分报道往往是媒体对该银行金科业务发展的核心叙事, 其语调离散度反映的是"媒体在评价该银行金科战略/产品时是否存在分歧"这一更聚焦的构念, 与全文轨标准差 (可能被大量与金科无关的银行报道稀释) 相比更贴近研究者关心的问题本身。在报告规范上, 本列应与 `jiang_2021_idf_tone_ss` (均值) 成对出现, 而不宜脱离均值单独解读标准差的经济含义。
本列与 std_full/std_ctx 两个变体的差异纯粹来自文本扫描域的宽窄, 三者共同构成"离散度对判据严格程度是否敏感"这一稳健性维度: 若三轨标准差呈现相似的相对排序 (例如同一批银行-年份在三轨下都显示较高分歧), 说明分歧结论不依赖具体的共现判据选择; 若排序发生明显变化, 通常提示同句共现窗口内命中的少数几篇报道恰好语调极端 (正或负), 对小样本标准差的杠杆效应较大, 此时应结合具体篇章逐条核查, 避免将个别极端报道误读为系统性的媒体分歧模式。

## VAR: jiang_2021_idf_tone_tech_ctx

【变体差分】
本列在「子样本切分=底层技术 (tech)」×「三轨=实体窗口 (ctx)」两个维度上定位: 分子源列限定于 stage 21 LLM locus 分类判定为"底层技术" (金科在报道中体现为核心技术研发/基础设施建设而非终端业务应用) 的报道子集, 扫描文本域为 `content_ctx`, 聚合方式为该子集内 `jiang_2021_idf_score_ctx` 的简单算术均值。与 `jiang_2021_idf_tone_app_ctx` 构成同轨技术-应用对照, 是 P4 (Gomber locus 范式) 主线论文识别策略的支撑测度之一; 与另两轨 tech 变体互为稳健性并排。
"底层技术"这一分类标签在 Gomber, Kauffman, Parker & Weber (2018) 的金融科技解构框架中对应技术基础设施/核心系统研发层面 (例如区块链底层协议、风控模型算法、云计算基础设施建设), 区别于终端用户可见的业务应用层面 (例如手机银行 App 功能、消费信贷产品)。本列度量的是媒体对银行在技术底层投入的评价语气, 相对应用场景报道, 底层技术类报道在中文财经媒体中通常篇幅更专业、受众更窄, 词典法命中率与 LLM 分类置信度均可能低于应用场景报道, 因此本列在小样本 (T=2 开发集) 下比 app_ctx 更容易呈现稀疏取值, 属数据特征而非产出缺陷。仓库内 ctx 轨确有落盘的 `tone_gap_tech_app_lc_ctx` 诊断量, 但该量并非以本列 (`jiang_2021_idf_score_ctx`) 为输入构造, 而是硬编码取 `llm_vote_tone_tech_lc_ctx` 减 `llm_vote_tone_app_lc_ctx` (LLM 三家投票语调, 同一最小篇数≥5 混杂防御), 与本词典 idf 加权路径无关; 研究者若需在 ctx 轨考察本列自身的技术-应用 idf 语调差距, 应自行以 `jiang_2021_idf_tone_tech_ctx − jiang_2021_idf_tone_app_ctx` 构造, 并在方法论附注中注明该临时构造量与仓库官方落盘的 `tone_gap_tech_app_lc_ctx` (LLM 路径) 是两套不同来源、不应混用或直接对比数值水平。

## VAR: jiang_2021_idf_tone_tech_full

【变体差分】
本列在「子样本切分=底层技术 (tech)」×「三轨=全文 (full)」两个维度上定位: 分子源列限定于 LLM locus 判定为"底层技术"的报道子集, 扫描文本域为 `content_full`, 聚合方式为该子集内 `jiang_2021_idf_score_full` 的简单算术均值。作为 full 轨的 tech 子样本测度, 其行宇宙锚定于 full 轨留篇门控之下再做 locus 二次切分。需特别澄清: 仓库内落盘的 `tone_gap_tech_app` (full 轨) 诊断量并非以本列 (`jiang_2021_idf_score_full`) 为输入, 而是硬编码取 `llm_vote_tone_tech_full` 减 `llm_vote_tone_app_full` (LLM 三家投票语调, 附带最小篇数≥5 的混杂防御守门, 见 `encode.py::_compute_tone_gap_tech_app`), 走的是 stage 21 LLM 情感路径而非本词典 idf 加权路径; 本列自身若要构造对应的 idf 版本差距量, 需研究者自行以本列减 `jiang_2021_idf_tone_app_full` 计算, 且不应与官方落盘的 `tone_gap_tech_app` (LLM 路径) 混为同一测度。
本列是三个 tech 变体中样本量最大的一支, 适合作为技术-应用语调差异比较的主口径。研究者应留意本列与其等权计数姊妹 (若存在同名 `jiang_2021_tone_tech_full`) 之间的差异纯粹来自 IDF 词权重方案, 而与子样本切分本身无关 — 换言之, app/tech 切分维度与 idf 加权维度是两条完全正交的变化轴, 组合出的 21 列矩阵中任意一列都可以拆解为"在哪个文本域扫描 (full/ctx/ss)"×"聚合层面做什么处理 (均值/std/vw/mw/hw/app/tech)"两个独立选择, 理解这一正交结构是准确解读整个家族、避免误把某一维度的差异归因于另一维度的关键。
在 P4 主线论文的识别策略中, 落盘诊断量 `tone_gap_tech_app` (= `llm_vote_tone_tech_full − llm_vote_tone_app_full`, LLM 三家投票路径, 非本列) 常被用作检验"金科底层技术投入 vs 应用场景推广"两条战略路径在媒体评价上是否存在系统性差异的核心解释变量之一, 该差距量已内置最小篇数≥5 的双侧混杂防御, 避免样本量过小导致的虚假差距估计; 本列 (`jiang_2021_idf_score_full` 的 tech 子样本均值) 与该 LLM 差距量共享同一套 locus 分类样本子集切分 (`n_articles_tech`≥5 的最小篇数守门语义相同), 但二者是词典法与 LLM 法两条独立测度路径, 应作为互相印证的稳健性证据联合披露, 不应把词典法本列的数值当作 LLM 差距量的分解项或直接替代。

## VAR: jiang_2021_idf_tone_tech_ss

【变体差分】
本列在「子样本切分=底层技术 (tech)」×「三轨=同句共现 (ss)」两个维度上定位: 分子源列限定于 LLM locus 判定为"底层技术"的报道子集, 扫描文本域为 `content_ss`。tech×ss 双重切窄 (子样本切分 + 严格同句共现判据) 使该列在小样本下极易出现合格篇数不足, T=2 开发集上大量取 NaN 属预期稀疏退化; 生产语料规模下样本量回升后应能更稳定地支撑 tech-app 语调差距的 ss 轨稳健性检验。
仓库内落盘的 `tone_gap_tech_app_ls_ss` 诊断量 (命名后缀 `_ls_ss` 表示 locus-split 同句轨) 并非以本列为输入, 而是硬编码取 `llm_vote_tone_tech_ls_ss` 减 `llm_vote_tone_app_ls_ss` (LLM 三家投票语调同句轨), 同样附带最小篇数≥5 的双侧混杂防御守门, 即只有当该银行-年份的 tech 与 app 两个子集都满足最小篇数阈值时, 差距量才会被计算, 否则置 NaN, 避免因单侧子集样本过少而产生虚假的技术-应用语调差距估计。三轨 tech 变体 (full/ctx/ss) 与三轨 app 变体两两配对, 仓库内 full/ctx/ss 三轨的 `tone_gap_tech_app`/`tone_gap_tech_app_lc_ctx`/`tone_gap_tech_app_ls_ss` 均已落盘, 但全部三个差距量都基于 LLM 三家投票语调 (`llm_vote_tone_{tech,app}{track}`) 而非本词典 idf 加权路径; 本列作为 ss 轨底层技术子样本的词典法原始测度, 与对应的 LLM 差距量共享同一套 locus 样本子集切分与最小篇数守门语义, 但二者是相互独立、互为稳健性的两条测度路径, 不构成该 LLM 差距量的输入项。作为家族内样本最受限的子样本×严格判据组合列之一, 本列在跨年份比较时应格外谨慎: 若某银行在某一年份该列有值而下一年份取 NaN, 未必意味着该银行的底层技术相关报道消失, 更可能是同句共现判据在样本量本就稀少的情况下产生的技术性缺失, 建议结合 `n_articles_tech_ls_ss` 等分母配套列 (若已落盘) 联合判读缺失是"真零"还是"判据过严导致的技术性缺失"。

## VAR: jiang_2021_idf_tone_vw_ctx

【变体差分】
本列在「聚合权重=关注度加权 (value-weighted, vw)」×「三轨=实体窗口 (ctx)」两个维度上定位: 分子为 `jiang_2021_idf_score_w_sum_ctx` (逐篇 idf 语调分乘以该篇 `mention_density_ctx` 即银行提及密度后求和), 分母为 `sum_mention_density_ctx`。vw 加权的方法学直觉是: 一篇文章中银行被反复密集提及, 意味着该篇报道以该银行为核心叙事对象, 其语调对该银行更具代表性, 理应获得更大权重, 而非与仅顺带一提的报道同等对待; 与等权 canonical `jiang_2021_idf_tone_ctx` 构成聚合权重维度上的对照。
本列的分母 `sum_mention_density_ctx` 与 mw/hw 两个变体使用的分母来源完全不同 (mention_density 是篇内密度而非篇际权威度或时间衰减), 三者共享统一的加权聚合数学形式 (Σ(score×weight)/Σ(weight)) 但权重语义各异, 这是理解 vw/mw/hw 三个聚合权重变体差异的关键。研究者若发现 vw_ctx 与 mw_ctx 数值高度一致而与 hw_ctx 明显不同, 通常提示"高密度提及的报道"与"高权威媒体的报道"在样本中高度重合 (例如权威媒体倾向于对重点银行做深度、高密度报道), 而与"是否属于短期扎堆报道"关系较弱, 这类交叉模式本身也是值得在稳健性附录中披露的描述性发现。本列聚焦实体窗口扫描域, 相对全文轨 vw 变体在文本域上做了收窄, 但权重计算所依据的提及密度本身已经是"密度"而非绝对计数, 因此文本域收窄对提及密度权重的影响机制与其对简单均值 canonical 列的影响机制不完全相同, 解读时不应简单类比。

## VAR: jiang_2021_idf_tone_vw_full

【变体差分】
本列在「聚合权重=关注度加权 (vw)」×「三轨=全文 (full)」两个维度上定位: 分子为 `jiang_2021_idf_score_w_sum_full`, 分母为 `sum_mention_density_full`。作为家族在 full 轨上的关注度加权口径, 它与 mw (媒体权威)、hw (从众衰减) 两条聚合权重维度并列而不重叠 — vw 权重的信息来源是"单篇报道内部对该银行的提及密度", 与 mw/hw 权重的信息来源 (信源可信度/时间扎堆度) 完全不同, 三者共同构成聚合权重梯子的三个正交单元。
作为 full 轨的关注度加权口径, 本列覆盖 full 轨全部留篇集样本, 在实证中常作为 vw 系列的主要报告口径, ctx/ss 两轨提供收窄扫描域后的补充稳健性。需要提醒的是, `mention_density_full` 本身的计算逻辑是在全文范围内统计银行名称出现的相对频率, 因此本列的加权效应与"报道篇幅长短"存在一定关联 (篇幅越长, 提及密度的绝对计数可能越高但相对密度未必更高, 具体取决于分母归一化方式), 在跨银行比较时应留意提及密度本身是否受报道篇幅系统性影响, 避免将"报道篇幅效应"误读为"语调水平效应"。本列与 mw_full/hw_full 三者应作为一组联合报告的稳健性附录列, 分别检验篇内提及密度、信源权威度、篇际时间扎堆度三种不同的加权机制是否驱动同一个语调水平结论, 三者一致是最强证据, 任一不一致均值得展开描述性诊断而非简单舍弃。

## VAR: jiang_2021_idf_tone_vw_ss

【变体差分】
本列在「聚合权重=关注度加权 (vw)」×「三轨=同句共现 (ss)」两个维度上定位: 分子为 `jiang_2021_idf_score_w_sum_ss`, 分母为 `sum_mention_density_ss`。ss 轨的 `mention_density_ss` 本身基于同句共现窗口内的提及计数, 与 ctx/full 两轨的关注度权重来源于不同宽窄的扫描域, 因此三轨 vw 变体的数值不应被直接跨轨比较水平高低, 而应各自作为 just-identified 的稳健性单元并排解读, 一致性检验以方向/显著性而非绝对数值对齐为准。
本列是三个 vw 变体中样本量最受限的一支, 同句共现判据本身已大幅收窄行宇宙, 提及密度权重又进一步在此基础上对篇内提及次数做二次加权, 双重收窄的结果是本列在小样本 (T=2 开发集) 下极易呈现稀疏取值。研究者应把本列理解为"银行与金科同句紧密关联、且该关联在文中被反复密集提及"的报道子集语调水平, 这是整个家族中构念最聚焦、精度最高但样本最少的一个单元, 适合作为主结论的极端稳健性检验而非首要报告口径; 主要报告口径应优先选用样本量更充裕的 `jiang_2021_idf_tone_vw_full` 或 canonical 均值列, 本列结果若与之方向一致, 是对结论稳健性的锦上添花证据。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323–1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673–719. https://doi.org/10.1093/rof/rfab036
Jegadeesh, N., & Wu, D. (2013). Word Power: A New Approach for Content Analysis. Journal of Financial Economics, 110(3), 712–729. https://doi.org/10.1016/j.jfineco.2013.08.018
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315–345. https://doi.org/10.2308/TAR-2020-0104
Spärck Jones, K. (1972). A Statistical Interpretation of Term Specificity and Its Application in Retrieval. Journal of Documentation, 28(1), 11–21. https://doi.org/10.1108/eb026526
<!-- rendered-citations:end -->
