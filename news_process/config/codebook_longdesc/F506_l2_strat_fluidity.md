---
family_id: F506
columns:
- strat_fluidity
- strat_fluidity_ctx
- strat_fluidity_ss
- strat_fluidity_w
- strat_fluidity_w_ctx
- strat_fluidity_w_ss
unit: 无量纲余弦相似度 (理论值域 ∈[0,1]; 计算单元=银行-年聚合文档, 非文章级取均值), 衡量该银行当期"文本位置"与"同行整体变化方向"的一致程度——越高表示同行正在向该银行所在的文本空间集中/侵蚀
formula: 'strat_fluidity_{i,t} = cos(N_{i,t}, Σ_{j≠i}|N_{j,t}-N_{j,t-1}|), 复刻 Hoberg, Phillips & Prabhala (2014) Eq.2: 先由 _aggregate_bank_year_texts 把每家目标银行同年全部报道聚合成单一银行-年文档 N_{i,t} (非文章级 sim(i) 取均值); 用 t 期∪t-1 期两期语料联合拟合 TF-IDF 向量化器 (char 轨=char_wb n-gram(2,4); _w 轨=jieba 分词并注入 607 个金科领域词) 得 L2 归一化向量; 市场变化向量 change_{i,t}=对除自身外全部同期出现于 t 与 t-1 两期的银行, 逐元素求 |N_{j,t}-N_{j,t-1}| 之和; 该银行当期得分=N_{i,t} 与 change_{i,t} 的余弦相似度; 首年无 t-1 数据则全部返回 NaN。不涉及 Top-N 最近邻检索, 不与家族内 strat_diff_n5 共享计算基础设施 (后者走独立的 _compute_nn_scores 最近邻函数); _ctx/_ss 后缀=聚合前的文章文本来源改用 stage 14 物化的实体窗口/同句共现轨, 聚合与向量化步骤本身不变'
producer: pipeline\features\strategic_diff.py (面板列 strat_fluidity{,_w,_ctx,_ss,_w_ctx,_w_ss} 由本模块 _compute_fluidity 计算, 经 panel.apply 直接赋值到面板, 不经 stage 40 pipeline\panel\export.py 二次汇总)
upstream: []
citations:
- {doi: "10.1111/jofi.12050", type: journal, authors: "Hoberg, G., Phillips, G., & Prabhala, N.", year: 2014, title: "Product market threats, payouts, and financial flexibility", venue: "The Journal of Finance", vol: "69", issue: "1", pages_or_artno: "293-324"}
- {doi: "10.1287/mnsc.2022.4369", type: journal, authors: "Guzman, J., & Li, A.", year: 2023, title: "Measuring founding strategy", venue: "Management Science", vol: "69", issue: "1", pages_or_artno: "101-118"}
- {doi: "10.1086/688176", type: journal, authors: "Hoberg, G., & Phillips, G.", year: 2016, title: "Text-based network industries and endogenous product differentiation", venue: "Journal of Political Economy", vol: "124", issue: "5", pages_or_artno: "1423-1465"}
- {doi: "10.1002/smj.2978", type: journal, authors: "Haans, R. F. J.", year: 2019, title: "What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories", venue: "Strategic Management Journal", vol: "40", issue: "1", pages_or_artno: "3-27"}
- {doi: "10.1257/jel.20181020", type: journal, authors: "Gentzkow, M., Kelly, B., & Taddy, M.", year: 2019, title: "Text as data", venue: "Journal of Economic Literature", vol: "57", issue: "3", pages_or_artno: "535-574"}
- doi: "10.1287/mnsc.2023.00282"
  title: "Position and Differentiation of Firms in Technology Space"
  authors: "Arts, S., Cassiman, B., & Hou, J."
  year: 2023
  venue: "Management Science"
  type: "journal"
- doi: "10.1016/j.econlet.2024.111823"
  title: "Textual similarity between firm and government: Measurement and pricing"
  authors: "Liu, Y., Cao, Z., & Wen, F."
  year: 2024
  venue: "Economics Letters"
  type: "journal"
- doi: "10.1080/1540496x.2025.2479064"
  type: "journal"
  authors: "Wang, Q., Xiang, C., Xin, Z., & Li, C."
  year: 2025
  title: "The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China"
  venue: "Emerging Markets Finance and Trade"
  vol: "61"
  issue: "11"
  pages_or_artno: "3595-3611"
new_dois:
  - "10.1287/mnsc.2023.00282"
  - "10.1016/j.econlet.2024.111823"
---

## CORE

【构念与来源】
本家族 6 列共同度量"银行 i 在报道语料中的战略/产品市场流动性 (product market fluidity)"——即该银行当期的文本"位置"与同行整体的文本"变化方向"越一致, 说明同行正在向该行所在的竞争空间集中或侵蚀, 该行面临的产品市场威胁越大。构念与计算公式直接迁移自 Hoberg, Phillips & Prabhala (2014, 简称 HPP) 在《Journal of Finance》提出的产品市场流动性指数 Eq.2: Fluidity_{i,t} = cos(N_{i,t}, Σ_{j≠i}|N_{j,t}−N_{j,t-1}|), 其中 N_{i,t} 是焦点企业当期的文本向量, Σ_{j≠i}|N_{j,t}−N_{j,t-1}| 是除自身外全部同行企业从 t-1 期到 t 期的"文本变化"逐元素绝对值加总 (即"市场整体正在往哪个方向移动"的合成向量), 二者的余弦相似度越高, 意味着同行的变化方向越指向焦点企业当前所在的文本位置, 即该企业的产品市场边界越容易被同行的产品线趋同侵蚀。原始设计用于解释企业支付政策与财务灵活性受产品市场威胁驱动的机制; 本模块把分析单元从上市公司 10-K 换成银行金科新闻报道, 以银行为分析单元、以年度为切片, 先将该行当年全部报道聚合成单一银行-年文档, 再按 HPP Eq.2 原式计算该行当期得分, 是构念与计算公式的直接迁移而非重新设计的替代算法, 契合 CLAUDE.md「战略差异度」family (F506 所属的 strategic_diff 模块) 的一贯做法——把文本相似度/变化向量视为竞争定位的代理变量而非情感/态度测度。

【方法学与计算】
计算管线四步, 与家族内 `strat_diff_n{N}`/`centroid_diff_*` 等最近邻/质心类姊妹列的实现路径完全不同 (不共享检索基础设施)。第一步, 银行-年文档聚合。`_aggregate_bank_year_texts` 把每家目标银行同一年份内全部报道的文本拼接聚合为单一文档 N_{i,t}, 计算单元自此就是"银行-年"而非"文章", 全流程不存在文章级 sim(i) 再取均值的步骤。第二步, 两期联合向量化。对每个 t 期, 同时取 t-1 期的银行-年文档集合, 用二者的并集联合拟合一个 TF-IDF 向量化器: 默认字符级轨 (无 `_w` 后缀) 用 char_wb n-gram(2,4) 编码; `_w` 后缀轨改用注入 607 个金科领域词的独立 jieba 分词器做词级 (word) TF-IDF 向量化, 使"金融科技""区块链"等领域复合词整词保留而不被字符切碎, 该口径自 2026-06-21 起对全部 `*_w`/`*_lda` 列统一生效 (fix inject-fintech-word-lda); 拟合完成后对 t 期与 t-1 期文档向量分别做 L2 归一化。第三步, 构造市场变化向量。对 t 期内每家银行 i, 遍历除自身外同时出现在 t 期与 t-1 期的全部其余银行 j, 逐元素计算 |N_{j,t}−N_{j,t-1}| 并累加, 得到该行当期专属的市场变化向量 change_{i,t} (注意: change 向量本身不含银行 i 的信息, 是"其余全部同行"的变化合成)。第四步, 求余弦相似度。fluidity_{i,t} = dot(N_{i,t}, change_{i,t}) / (‖N_{i,t}‖·‖change_{i,t}‖); 分母为零 (change 向量全零, 即无任何同行在两期间发生文本变化) 时取 NaN; 首年 (无 t-1 期数据可比) 该年全部银行同样返回 NaN。三轨 full/ctx/ss 的差别只在第一步聚合前喂给聚合函数的原始文章文本来源不同 (详见各 VAR 节), 第二至四步的两期联合向量化/市场变化向量构造/余弦求值逻辑对三轨完全一致, 因此三轨可直接横向比较、互为稳健性检验而非彼此替代。值域方面, TF-IDF 向量与由其逐元素绝对差累加而成的 change 向量均为非负, 二者余弦相似度理论落在 [0,1], 不涉及 embedding 轨 [-1,1] 的负值问题, 但这一非负结论建立在"两个参与内积的向量均非负"这一 TF-IDF 输入前提上, 而非"相似度均值天然落域"式的经验凑数论证。

【文献定位】
本家族方法学谱系有三层, 且 fluidity 一列与家族内最近邻/质心类姊妹列在方法学出处上分属不同层次, 不应混同。底层且唯一直接支撑本列公式的文献是 Hoberg, Phillips & Prabhala (2014) 的产品市场流动性构念与 Eq.2 计算式本身, 其原始设计用于解释企业支付政策与财务灵活性受产品市场威胁驱动的机制, 本列是该 Eq.2 公式从企业 10-K 语料到银行金科新闻语料的直接迁移复刻, 而非另起炉灶的近似替代算法。第二层是本家族内其余最近邻类列 (`strat_diff_n{N}` 系列) 所依据的方法学出处 Guzman & Li (2023, Management Science)——其"Measuring Founding Strategy"一文用 TF-IDF 最近邻相似度衡量创业策略的独特性/趋同性, 为家族内 Top-N 检索类列 (含 2026-07-02 起的大邻域 N∈{10,20,30,40,50} 孪生) 提供方法学模板, 但该文献与本 fluidity 一列的市场变化向量算法无直接方法学传承关系, 二者仅同属 strategic_diff 模块下"以文本相似度代理竞争定位"的共同技术家族, 不共享计算步骤。第三层是文本相似度用作产业/竞争测度的更早经典出处 Hoberg & Phillips (2016, Journal of Political Economy), 该文提出文本网络行业分类 (TNIC) 与内生产品差异化的框架, 是 Hoberg、Phillips 与 Prabhala (2014) 之前的方法学奠基, 也是家族内 `strat_diff_n{N}`/`centroid_diff_*` 等姊妹列共同追溯的源头之一。此外, Haans (2019, Strategic Management Journal) 关于"差异化价值取决于同质/异质情境"的发现提醒使用者: 流动性得分的经济含义随竞争环境结构而变, 不能脱离行业背景做跨期简单比较; Gentzkow, Kelly & Taddy (2019, Journal of Economic Literature) 的文本即数据方法论综述则为本家族的 TF-IDF 整体技术路线提供了计量经济学框架层面的正当性论证。Arts, Cassiman, & Hou (2023, Management Science) 该文用文本方法度量企业在技术空间中的相对位置与差异化程度, 为本家族以文本相似度/变化向量代理战略定位的方法论提供 2023 年后的最新同类实证支持。Liu, Cao, & Wen (2024, Economics Letters) 该文用 BERT 文本相似度量化企业文本与政府文本的对齐程度并检验其市场定价效应, 佐证文本相似度/变化度量作为经济主体战略/行为代理变量在 2024 年后仍是活跃的方法论路线。全部三轨/两分词轨口径均遵循 CLAUDE.md「当前状态铁律」: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 设定; char 与 word (`_w`) 两条分词轨同理互为稳健性检验, 二者共同构成本家族对"分词粒度是否驱动结论"的敏感性证据链, 而非哪一条更优先的取舍。 同域应用层面, Wang、Xiang、Xin 与 Li (2025) 在中国上市公司样本上以 Hoberg-Phillips 式产品文本相似度界定同业集合, 并据此识别同业间的相互影响, 佐证了本列赖以成立的核心前提——文本空间中的同业邻近关系在中国语境下确实承载真实的竞争关联, 因而以同业文本位置的整体移动方向去度量对焦点银行的侵蚀是有依据的。边界须写明: 该文语料为公司自述的年报产品描述, 而非本项目的第三方媒体报道, 文本生成过程与选择性偏误不同; 其同业集合用于 peer effect 回归, 全文既未构造 Hoberg、Phillips 与 Prabhala (2014) Eq.2 式的市场变化向量 cos(N_it, Σ|N_jt−N_j,t−1|), 也不含任何跨期成分, 故本条只作同域可用性旁证, fluidity 算子本身的出处仍是 Hoberg、Phillips 与 Prabhala (2014)。
## VAR: strat_fluidity

【变体差分】
本列是家族的 canonical (无后缀) 版本: 文本来源=全文轨 (full, 标题+正文全文, 由 stage 14 `ctx_materializer` 的 `prepend_title` 规则拼接后经 `_aggregate_bank_year_texts` 聚合为银行-年单一文档); 分词/向量化=字符级 (char_wb n-gram(2,4)) TF-IDF, 未启用金科词注入分词器; 计算方法=Hoberg, Phillips & Prabhala (2014) Eq.2 的市场变化向量余弦相似度——用 t 期与 t-1 期联合语料拟合向量化器后, 对当期每家银行计算其自身文本向量与"除自身外全部同行两期间文本变化量之和"的余弦相似度, 不涉及 Top-N 最近邻检索, 与家族内 `strat_diff_n5` 是两套不同的计算基础设施 (后者走 `_compute_nn_scores` 最近邻函数), 二者仅同属 strategic_diff 模块下"以文本相似度代理竞争定位"的技术家族、不共享中间结果。该列是 Hoberg、Phillips 与 Prabhala (2014) 流动性构念在本项目里最贴近原始设计的实现: 因为 full 轨保留了报道全部原始信息 (标题+正文) 且未做实体窗口截断或同句共现过滤, 最大程度还原了 HPP 原文"用企业全篇文本做相似度"的精神, 是本家族默认作图/默认回归推荐使用的口径。需要强调的是, 该列的计算单元是银行-年聚合文档而非文章, 首年 (无前一年数据可比) 该年全部银行取值为 NaN, 银行-年样本内报道篇数偏少时聚合文档信息量不足、市场变化向量的估计方差也会相应升高, 使用者在解释估计系数时应结合 `n_articles`(留篇门控=full-only 口径下的分母) 一并报告, 以免把稀疏样本的噪声误读为真实的产品市场流动性变化。

## VAR: strat_fluidity_ctx

【变体差分】
本列与 canonical 列的唯一差分维度是输入文本的轨道: 分词/向量化仍为字符级 TF-IDF, HPP Eq.2 的两期联合向量化/市场变化向量/余弦求值方法学步骤完全不变, 但聚合前喂给 `_aggregate_bank_year_texts` 的原始文章文本换成 stage 14 物化的 `content_ctx` (标题+目标银行实体窗口), 而非全文正文。这一替换的动机是: 全文轨可能包含与银行战略定位无关的大段背景叙述 (如宏观经济评论、其他机构介绍), 稀释了银行-年聚合文档中的信号密度; 实体窗口轨聚焦在银行实体附近的局部文本, 理论上能提高聚合文档对"该银行到底在做什么"这一构念的信噪比。按 CLAUDE.md 三轨铁律, `_ctx` 与 canonical (`_full`, 此处即无后缀列) 是并排的互为稳健性关系, 不存在孰优孰劣的先验排序, 二者应在同一稳健性表格中并列报告而不是相互替代; 若某篇报道不存在实体窗口共现 (即 `ctx_is_fallback=True`), 该篇的 `content_ctx` 回退为全文正文, 汇入聚合文档后 `_ctx` 列在回退占比高的银行-年会趋同于 `strat_fluidity`, 使用者在做跨行比较时应留意回退比例是否在样本内失衡。本列因此在实证设计中通常被用作 canonical 列的敏感性检验轨, 与 `_ss` 轨、`_w_ctx` 轨共同构成对"文本窗口口径是否驱动流动性结论"的多维交叉验证。

## VAR: strat_fluidity_ss

【变体差分】
本列与 `_ctx` 同属"局部窗口"分支, 但窗口定义更严格: 聚合前喂给向量化流程的原始文章文本是 stage 14 物化的 `content_ss`, 即标题+"银行实体与金科关键词同句共现 (±N 句半径, 默认 N=1)"窗口, 而非仅围绕银行实体的宽窗口。分词/向量化仍为字符级 TF-IDF, HPP Eq.2 的两期联合向量化与市场变化向量余弦求值方法学步骤与 canonical 列一致, 差分仅在聚合前的文本来源。`_ss` 轨的语义设计镜像 `_ctx` 轨的回退语义: 若一篇报道内不存在银行与金科词的同句共现, `content_ss` 回退为全文正文, 对应的 `ss_is_fallback` 置为 True, 分母仍与 `_ctx`/full 共享同一 `n_articles` 口径, 不产生单边孤儿列。相较 `_ctx`, `_ss` 轨的文本粒度更细, 理论上更贴近"该银行与金融科技具体如何互动"这一叙事局部, 因此其流动性得分对金科相关竞争定位的刻画应更精准, 但同时也更容易因窗口过窄导致某些银行-年聚合文档信息量骤减、市场变化向量估计方差增大。按铁律, `_ss` 与 `_full`/`_ctx` 三者各自 just-identified 并排、互为稳健性、不分主次, 三者禁止混入同一 over-identified Hansen J 识别设定, 应作为并列的稳健性证据链呈现而非合并进单一工具变量方程。在样本较薄的年份 (如本项目早期试跑 T=2 样本), `_ss` 轨因窗口最窄, 出现 NaN 或大量回退为全文的概率也最高, 使用者报告该列结果时应同时披露回退比例, 避免把"实质是全文轨结果"误标注为"同句共现轨的独立发现", 这一披露义务与家族内其余判据敏感性列 (如网络三轨) 的既有做法保持一致。

## VAR: strat_fluidity_w

【变体差分】
本列与 canonical 列的差分维度是分词粒度而非文本轨道: 文本来源仍为全文 (full) 轨, HPP Eq.2 的银行-年聚合/两期联合向量化/市场变化向量/余弦求值步骤不变, 但向量化器由默认字符级 (char_wb) TF-IDF 换成 jieba 词级 (word) TF-IDF, 且自 2026-06-21 起该词级分词器额外注入了 607 个金融科技领域词表 (`_get_diff_tokenizer` 逻辑), 使"金融科技""区块链""供应链金融"等领域复合词在切词阶段被整体保留为单一 token, 而不会被字符级 n-gram 拆散成碎片。这一设计的动机是: 字符级向量化对中文文本天然稳健 (不依赖分词正确性), 但会丢失词汇边界带来的语义颗粒度; 词级向量化更贴近人类阅读理解的语义单元, 尤其对金科领域专有名词的识别更精确, 代价是引入了分词器本身的误差与领域词表覆盖不全的风险。`_w` 与 canonical (char) 轨在方法学地位上完全对等, 是本家族对"分词方案是否驱动流动性结论"的稳健性检验轨, 二者应在同一稳健性附表中并列呈现; 由于金科词表的引入, `_w` 轨理论上对涉及金融科技业务表述密集的报道更敏感, 与 canonical 轨的相关系数越高, 说明流动性构念对分词方案的选择越不敏感, 结论越稳健。

## VAR: strat_fluidity_w_ctx

【变体差分】
本列同时叠加两个差分维度: 分词粒度换成词级 (jieba + 金科词注入分词器, 同 `_w` 列) 且聚合前文本轨道换成实体窗口轨 (`content_ctx`, 同 `_ctx` 列), HPP Eq.2 的两期联合向量化/市场变化向量/余弦求值方法学逻辑保持家族统一。本列可理解为 `_w` 列与 `_ctx` 列两个正交差分维度的交叉组合: 一个维度回答"分词粒度是否重要", 另一个维度回答"文本窗口范围是否重要", 二者在本列上同时生效但彼此独立、互不嵌套——即本列不是对 `_w` 或 `_ctx` 任一列的进一步细化或替代, 而是家族完整消融矩阵 (2 分词方案 × 3 文本轨道) 中的一个格点。使用该列做实证时应明确其定位: 它是"词级+局部窗口"组合稳健性检验, 与 canonical 全文字符轨在两个维度上同时存在差异, 若该列与 canonical 列的估计系数方向、显著性一致, 是对结论稳健性的强证据; 若不一致, 需要进一步拆解到 `_w`(仅分词差异) 与 `_ctx`(仅窗口差异) 两个单维度列上定位差异来源, 而非直接把本列的差异归因于某一单一维度。方法学上, 该列的两期联合向量化池同样限定为"同年份其余目标银行报道"聚合成的对应轨道文档, 不引入任何加权或截尾处理; 与家族内其余列一致, 本列不涉及 embedding 语义空间, 值域理论落在 [0,1] (基于 TF-IDF 与其绝对差累加而成的 change 向量均非负), 不存在余弦相似度为负导致的地板效应问题。

## VAR: strat_fluidity_w_ss

【变体差分】
本列是家族消融矩阵 (2 分词方案 × 3 文本轨道) 中的最后一个格点: 分词粒度为词级 (jieba + 金科词注入分词器, 同 `_w`/`_w_ctx`), 聚合前文本轨道为同句共现窗口 (`content_ss`, 同 `_ss` 列, 银行实体与金科关键词同句±1 句半径共现), HPP Eq.2 的两期联合向量化/市场变化向量/余弦求值步骤与家族其余五列完全一致。该列在语义上最贴近"金融科技局部叙事的词汇化流动性", 即只看银行与金科词紧邻同现的句子片段聚合成银行-年文档, 并用能识别金科领域词汇边界的分词器编码, 理论上是六列中对"银行的金科战略定位相似度"信号最集中、噪声最少但样本方差也可能最大的一支 (窗口窄+分词粒度细双重收缩效应)。`_ss` 轨的回退语义在本列同样成立: 无同句共现的报道回退为全文, 对应 `ss_is_fallback=True`, 与 `_ss`(char 分词) 列共享同一回退判据与 `n_articles` 分母, 不产生单边孤儿。六列共同构成的消融矩阵应作为一个整体在稳健性附录中呈现, 任何单列的显著性结果都应参照矩阵内其余五列的一致性方向做联合判断, 严禁挑选其中数值最"好看"的单列作为主结果单独报告。
<!-- rendered-citations:begin -->
Hoberg, G., Phillips, G., & Prabhala, N. (2014). Product market threats, payouts, and financial flexibility. The Journal of Finance, 69(1), 293-324. https://doi.org/10.1111/jofi.12050
Guzman, J., & Li, A. (2023). Measuring founding strategy. Management Science, 69(1), 101-118. https://doi.org/10.1287/mnsc.2022.4369
Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. Journal of Political Economy, 124(5), 1423-1465. https://doi.org/10.1086/688176
Haans, R. F. J. (2019). What's the value of being different when everyone is? The effects of distinctiveness on performance in homogeneous versus heterogeneous categories. Strategic Management Journal, 40(1), 3-27. https://doi.org/10.1002/smj.2978
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Arts, S., Cassiman, B., & Hou, J. (2023). Position and Differentiation of Firms in Technology Space. Management Science. https://doi.org/10.1287/mnsc.2023.00282
Liu, Y., Cao, Z., & Wen, F. (2024). Textual similarity between firm and government: Measurement and pricing. Economics Letters. https://doi.org/10.1016/j.econlet.2024.111823
Wang, Q., Xiang, C., Xin, Z., & Li, C. (2025). The Peer Influence on Green Innovation: Evidence from Product-Similarity-Based Peer Firms in China. Emerging Markets Finance and Trade, 61(11), 3595-3611. https://doi.org/10.1080/1540496x.2025.2479064
<!-- rendered-citations:end -->
