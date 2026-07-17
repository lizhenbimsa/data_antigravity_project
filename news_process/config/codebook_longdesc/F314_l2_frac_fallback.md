---
family_id: F314
columns:
- frac_ctx_fallback
- frac_ss_fallback
unit: 比率 (proportion, [0,1]; bank-year 层面对文章级布尔回退旗标取算术均值)
formula: 'frac_ctx_fallback = mean(ctx_is_fallback); frac_ss_fallback = mean(ss_is_fallback); 两旗标均在 stage 14 (ctx_materializer) 物化于文章级, stage 40 (encode.py) 用 groupby(bank, year).agg 聚合为 bank-year 均值; 源列缺失时 encode.py 按条件式 (if 源列 in df.columns) 跳过该聚合项, 该列不进入聚合产物, 终态经下游对 (bank, year) 全笛卡尔积 reindex 补齐为 NaN (非静默填 0)'
producer: 'pipeline/panel/encode.py (聚合, groupby agg 分别注入 frac_ctx_fallback / frac_ss_fallback); 上游物化在 pipeline/text/ctx_materializer.py (stage 14, 产 ctx_is_fallback / ss_is_fallback 两文章级布尔列)'
upstream:
- ctx_is_fallback
- ss_is_fallback
citations:
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: 'Analysis of linked files: A missing data perspective'
  venue: Statistical Science
  vol: '41'
  issue: '1'
  pages_or_artno: ''
- doi: 10.1257/aer.20200292
  type: journal
  authors: Ward, Z.
  year: 2023
  title: 'Intergenerational mobility in American history: Accounting for race and measurement error'
  venue: American Economic Review
  vol: '113'
  issue: '12'
  pages_or_artno: 3213-3248
- doi: 10.1126/sciadv.abi8021
  type: journal
  authors: Binette, O., & Steorts, R. C.
  year: 2022
  title: (Almost) all of entity resolution
  venue: Science Advances
  vol: '8'
  issue: '12'
  pages_or_artno: eabi8021
- doi: 10.1080/01621459.1969.10501049
  type: journal
  authors: Fellegi, I. P., & Sunter, A. B.
  year: 1969
  title: A theory for record linkage
  venue: Journal of the American Statistical Association
  vol: '64'
  issue: '328'
  pages_or_artno: 1183-1210
- doi: "10.1108/cafr-12-2025-0269"
  type: "journal"
  authors: "Meng, L., Wang, P. P., Lu, H., Yang, W. Y., & Vijayakumar, S."
  year: 2026
  title: "Entity-specific text classification with large language models: two applications on financial and brand news"
  venue: "China Accounting and Finance Review"
  pages_or_artno: "1-11"
- doi: "10.1177/10944281251334777"
  type: "journal"
  authors: "Iqbal, F., & Pfarrer, M. D."
  year: 2025
  title: "Using Coreference Resolution to Mitigate Measurement Error in Text Analysis"
  venue: "Organizational Research Methods"
  pages_or_artno: "10944281251334777"
new_dois: []
---

## CORE

【构念与来源】
frac_ctx_fallback 与 frac_ss_fallback 是一对 bank-year 层面的"回退占比"诊断指标, 度量三轨文本架构 (full/ctx/ss, 详见 CLAUDE.md「三轨」铁律段) 中 ctx 轨与 ss 轨相对于 full 轨的"实际独立信息含量"。两者的原语都是文章级布尔旗标: ctx_is_fallback 标记该篇文章的实体窗文本 content_ctx 是否与整篇正文 content_full 完全等价 (即目标银行∧金科关键词的实体窗口未命中, 系统按回退公理退化为全文); ss_is_fallback 标记同句文本 content_ss 是否退化为全文 (即该篇文章内不存在"目标银行与金科关键词同句共现", 按同一回退公理退回全文 body)。两旗标均在 stage 14 ctx_materializer 中与 content_full/content_ctx/content_ss 三轨文本同批物化, 三轨文本均已经过 prepend_title 注入标题 (标题前缀对三轨相同, 不影响回退判定的 entity-miss 语义)。stage 40 面板导出阶段 (pipeline/panel/encode.py) 对同一 (bank, year) 分组内的全部文章取两旗标的算术均值, 得到本家族的两个比率列; 若源列因历史 schema 版本缺失, encode.py 的条件式聚合会直接跳过该聚合键 (该列不会被写入聚合产物, 而非"先产出后置 NaN"), 该 (bank, year) 格子的最终列值经下游对全部银行-年份的笛卡尔积 reindex 间接补齐为 NaN; 聚合逻辑不会主动静默填零, 终态呈现的是 NaN 而非 0, 以防止把"未采集回退信号"误读为"零回退"。

frac_ctx_fallback / frac_ss_fallback 的实质是"轨道退化率": 值越接近 1, 说明该银行-年份的报道样本中, 对应轨道 (ctx 或 ss) 绝大多数文章都退化成了与 full 轨完全相同的文本, 该轨携带的增量识别信息趋近于零; 值越接近 0, 说明该轨道文本相对 full 轨拥有真实的、独立的窗口化裁剪信息, 是"局部聚焦"测度构念真正生效的证据。两列因此既是三轨稳健性设计的质量诊断工具, 也是论文层面样本筛选/异质性分组的候选协变量 (例如按 frac_ctx_fallback 高低分组, 检验 full↔ctx 两轨情感/属性测度在"退化样本"与"非退化样本"中的一致性)。

【方法学与计算】
ctx 轨的实体窗口裁剪逻辑与 stage 13 共现硬过滤 (cooccurrence_filter.py) 是两套不同判据: stage 13 用「银行∧金科邻近共现」(config/filtering.yaml::cooccurrence_filter, 生产口径 sentence_radius=1 + match_in_title=true) 决定文章是否保留进样本; ctx_is_fallback 度量的是保留下来的文章中, 实体窗口裁剪算法本身是否命中了可裁剪的实体锚点。二者判据原语不同, 不可混用 (镜像 CLAUDE.md「stage 13 共现硬过滤」段对 has_bank_fintech_cooccurrence_within_radius 与 extract_bank_fintech_cooccurrence 严禁互相复用的铁律)。ss 轨的判据更严格: 要求目标银行词与金科关键词落在同一句 (核心原语 core/text/entity_context.py 的同句共现抽取, 与 stage 13 windowed 判据是另一个不同口径), 因此在几乎所有生产语料上 frac_ss_fallback 的期望值系统性高于 frac_ctx_fallback (同句是比窗口更严的必要条件, ss 轨退化的概率天然更大)。config/filtering.yaml 中亦记录了一段针对 _ss 轨交互的三态演进注记: 若上游共现判据改为严格同句 (即 stage 13 keep 集合本身就等价于同句集合), 则 frac_ss_fallback 会坍缩至零方差附近 (因为保留下来的文章几乎全部满足同句条件, 回退比率恒趋近于 0); 而在当前生产口径 (radius=1 的窗口共现) 下, keep 集合严格宽于同句集合, frac_ss_fallback 才呈现出有意义的 (0,1) 区间分布, 是独立于 full/ctx 文本信号的诊断量。

【文献定位】
本家族在方法论谱系上更贴近"链接/裁剪失败即测量退化"这一支文献, 而非情感测度本身。ctx_is_fallback / ss_is_fallback 的生成机制是: 实体窗口裁剪算法尝试把目标银行与金科关键词的邻近窗 (或同句) 从全文中"链接"出来, 一旦这次链接失败 (锚点未命中), 系统才退回全文——这与经典记录链接 (record linkage) 问题中"链接失败退回默认/缺失处理"的结构是同一类操作化风险。Fellegi & Sunter (1969, Journal of the American Statistical Association) 奠定了记录链接的概率判定框架, 明确区分"确定链接""确定非链接""待定"三态, 其"链接判定本身可能失败, 失败态必须被显式标记而非静默吞并"的原则, 正是 frac_ctx_fallback / frac_ss_fallback 把"实体窗口锚定失败"独立物化为可观测布尔旗标 (而非让裁剪失败悄悄退化为看似正常的全文文本) 这一设计选择的方法论源头。Binette & Steorts (2022, Science Advances) 系统梳理了实体消歧/记录链接管道中错误如何在下游传播, 强调链接质量的事后可诊断性是管道可信度的前提条件, 对应本家族"回退比率作为链接质量事后诊断指标"的定位。Kamat & Gutman (2026, Statistical Science) 从缺失数据视角分析"链接文件" (linked files) 中链接失败导致的系统性偏误, 其核心论点——链接失败不应被当作随机缺失处理, 而应作为一种独立的、可能与结果相关的选择机制单独建模——直接对应本家族坚持"聚合缺列时跳过而非静默填零"「NaN 而非填零」的设计取舍。Ward (2023, American Economic Review) 在跨代际流动性研究中处理历史记录匹配误差时, 进一步证明链接/匹配失败率本身往往与研究关心的经济变量相关 (而非纯噪声), 若不显式度量并纳入稳健性检验, 会系统性偏误结论——这正是 frac_ctx_fallback / frac_ss_fallback 被设计为可用于样本筛选与异质性分组协变量的实证依据: 若回退率与银行特征系统性相关, 简单忽略回退样本或不对回退率加以控制, 会重蹈该文献揭示的匹配误差内生性问题。四篇文献共同的方法论启示可归纳为一点: 任何以"实体/窗口/记录链接"为前提的测度设计, 都必须把链接失败本身操作化为可观测、可审计的独立信号, 而非任其退化为看似完好的默认值; frac_ctx_fallback / frac_ss_fallback 正是把这一原则应用到银行金科新闻文本裁剪场景下的具体实现。

需要特别澄清与 CLAUDE.md 铁律的对齐关系: full/ctx/ss 三轨在本项目中是「各自 just-identified 并排、互为稳健性、不分主次」的设计, 三轨情感/属性测度禁止混入同一 over-identified Hansen J 检验。frac_ctx_fallback / frac_ss_fallback 并不参与该稳健性并排本身, 而是对并排设计"有效性前提"的事后审计——它们回答的是"ctx 轨/ss 轨在这个银行-年份格子里, 到底有没有真的提供不同于 full 轨的文本", 是论文披露稳健性检验适用范围时应当引用的诊断证据, 而非又一条待并排的稳健性测度轨道。 在实体粒度抽取这一更直接对口的近期文献上, Meng、Wang、Lu、Yang 与 Vijayakumar (2026) 以 LLM 做实体特定 (entity-specific) 的新闻文本分类基准评测, 明确指出同一篇报道内多实体并存会使文档级分析失效、须在实体粒度上抽取信息, 并在英文金融新闻与中文危机新闻两语料上以 F1 对人工标注做效度评估。这恰好构成本家族所诊断的那次失败的构念前提: ctx/ss 窗口正是实体粒度抽取的尝试, 而 frac_ctx_fallback / frac_ss_fallback 度量的正是这一尝试退回文档级 (全文 body) 的频率。迁移边界须写明: 原文的实体抽取由 LLM 直接完成, 本项目 ctx/ss 的实体识别走词典/AC 自动机与 jieba token 匹配 (LLM 仅用于 stage 21 情感与分类维度), 故该文不构成本项目实体抽取精度的背书; 原文实体宇宙为一般金融/品牌新闻主体, 本项目限定为目标银行且银行侧带否定+短名过滤 (金科侧为裸 AC 词表) 的不对称口径, 原文亦未产出 bank-year 面板聚合, 更无窗口回退机制。Iqbal 与 Pfarrer (2025) 则指出文本分析在多主体文本中的情感归属上存在系统性测量误差 (传统方法易将文本误归于错误主体), 并以共指消解 (coreference resolution) 处理之, 通过两项研究证明该处理可降低测量误差——这支持本家族的一般立场: 一项实体级语言学处理是否成功, 会系统性改变文本测度的取值, 因而处理失败本身必须被显式度量而非静默吞并。但边界须严格把住: 原文的规则是共指消解 (实体指代还原), 与本项目 ctx/ss 的邻近窗口裁剪并非同一操作, 亦非本家族的方法学来源; 原文语料为英文组织管理文本、单位为文档/组织; 且原文立场是规范性的 (主张采纳该规则以减少误差, 隐含存在唯一正确做法), 而本项目 full/ctx/ss 三轨互为稳健性、不分主次、各自 just-identified 并排 (禁混同一 over-identified Hansen J), 故不得据该文把本家族的回退旗标读作「ctx/ss 轨有误、须予纠正」的证据, 它只是并排设计有效性前提的事后审计量。
## VAR: frac_ctx_fallback

【变体差分】
frac_ctx_fallback 的直接来源是文章级布尔列 ctx_is_fallback: 当且仅当 content_ctx（标题+实体窗口文本）与 content_full（标题+整篇正文）在"去标题后的 body"层面完全相等时, 该旗标为 True。判定成立的机制是——实体窗口裁剪算法未能在正文中锚定到可用的目标银行/金科关键词邻近窗口 (例如实体名称出现频次过低、别名未命中词典、或正文结构导致窗口抽取失败), 系统遂按回退公理原样退回整篇正文, 使 ctx 轨在文本层面与 full 轨完全等价。frac_ctx_fallback 是该旗标在 (bank, year) 分组内的算术均值 (encode.py::agg['frac_ctx_fallback'] = ('ctx_is_fallback', 'mean')), 源列存在性由 valid_agg 自动侦测, 缺列时该聚合项被跳过而非报错。

高 frac_ctx_fallback 值的实践含义是: 该银行-年份样本中大多数文章的 ctx 轨退化为 full 轨, 此时若下游稳健性检验发现 full 轨与 ctx 轨测度高度相关或数值趋同, 并不能被解读为"实体窗口裁剪对结果稳健", 而更可能只是"两轨文本本就相同"这一机械后果的直接体现——这正是 CLAUDE.md 提及的 R8-H1 判别效度审计关切 (pipeline/audit/lexical_discriminant_validity.py 文档锁定但未在 stage 39d 内实施的 ctx-fallback HTMT mask), 论文层若需等价处理, 可在 Stata 侧用 frac_ctx_fallback 设定阈值 (例如 <0.30) 筛除退化样本后再做 full↔ctx 判别效度比较。与其镜像列 frac_ss_fallback 相比, frac_ctx_fallback 的判据更宽松 (窗口邻近而非严格同句), 因此在同一语料上其期望取值通常更低, 意味着 ctx 轨相对 ss 轨保有更多独立于 full 轨的边际文本信息; 两列各自诊断各自轨道的退化率, 互不替代, 也不构成对彼此稳健性的检验。分母口径与 n_articles 完全一致的是分组内全部留篇文章 (full-only 留篇门控下的样本), 而非仅统计非缺失的 ctx 相关列, 这与 CLAUDE.md「留篇门控=full-only」铁律保持一致——该银行-年份是否计入分析样本, 只看 llm_verified_full, ctx 轨的回退率是该留篇集合的条件测度, 不反向影响留篇判定。

## VAR: frac_ss_fallback

【变体差分】
frac_ss_fallback 与 frac_ctx_fallback 是镜像设计: 源列 ss_is_fallback 判定 content_ss（标题+"银行∧金科同句"窗口文本）是否与 content_full 完全等价, 当且仅当该篇文章正文中不存在任何一句同时包含目标银行词与金科关键词 (核心原语 core/text/entity_context.py, 与 stage 13 共现硬过滤的窗口判据是不同判据、禁止互相复用) 时为 True, 系统按同一回退公理退回全文, ss_is_fallback=True。frac_ss_fallback 即该旗标在 (bank, year) 分组内的均值 (encode.py::agg['frac_ss_fallback'] = ('ss_is_fallback', 'mean')), 聚合机制、缺列跳过语义、NaN 而非静默填零的处理方式都与 frac_ctx_fallback 完全对称。

ss 轨判据比 ctx 轨判据更严格 (严格同句 vs. ±1 句窗口/整窗实体邻近), 这意味着在生产口径 (config/filtering.yaml::cooccurrence_filter.sentence_radius=1, 与本列所涉的同句判据是不同键, 不可混用) 下, frac_ss_fallback 通常系统性高于同一样本的 frac_ctx_fallback: 保留进样本的文章满足"窗口内共现"即可, 未必满足更严的"同句共现", 因此更多文章的 ss 轨会退化为全文。config/filtering.yaml 中明确记录了这一比率对上游共现判据选择的敏感性: 若把 stage 13 的判据改为与 ss 轨相同的严格同句 (非当前生产口径), 则保留下来的文章几乎全部满足同句条件, frac_ss_fallback 会坍缩至零方差附近, 丧失作为诊断变量的区分力; 在当前"窗口共现保留、同句共现裁剪"的错位设计下, frac_ss_fallback 才呈现出有意义的跨银行-年份变异, content_ss 文本信号本身仍然有效, 且与 full/ctx 两轨文本存在真实差异 (三态恢复的实证结论)。与 frac_ctx_fallback 相同, 该列服务于事后诊断而非稳健性并排本身: 三轨 full/ctx/ss 情感与属性测度各自 just-identified 并排、互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J; frac_ss_fallback 高企的银行-年份格子提示研究者在解读 ss 轨稳健性结论时应结合该诊断信息, 避免把"文本机械相同"误读为"稳健性通过"。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Ward, Z. (2023). Intergenerational mobility in American history: Accounting for race and measurement error. American Economic Review, 113(12), 3213-3248. https://doi.org/10.1257/aer.20200292
Binette, O., & Steorts, R. C. (2022). (Almost) all of entity resolution. Science Advances, 8(12), eabi8021. https://doi.org/10.1126/sciadv.abi8021
Fellegi, I. P., & Sunter, A. B. (1969). A theory for record linkage. Journal of the American Statistical Association, 64(328), 1183-1210. https://doi.org/10.1080/01621459.1969.10501049
Meng, L., Wang, P. P., Lu, H., Yang, W. Y., & Vijayakumar, S. (2026). Entity-specific text classification with large language models: two applications on financial and brand news. China Accounting and Finance Review, 1-11. https://doi.org/10.1108/cafr-12-2025-0269
Iqbal, F., & Pfarrer, M. D. (2025). Using Coreference Resolution to Mitigate Measurement Error in Text Analysis. Organizational Research Methods, 10944281251334777. https://doi.org/10.1177/10944281251334777
<!-- rendered-citations:end -->
