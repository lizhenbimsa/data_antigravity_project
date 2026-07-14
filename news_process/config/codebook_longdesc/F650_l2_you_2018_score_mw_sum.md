---
family_id: F650
columns:
- you_2018_score_mw_sum_ctx
- you_2018_score_mw_sum_full
- you_2018_score_mw_sum_ss
unit: 无量纲加权分值 (银行-年内篇章级 you_2018 词典净情感分之媒体权威性加权和)
formula: 'you_2018_score_mw_sum{track} = Σ_i∈(bank,year) [you_2018_score{track}_i × media_authority_weight_i]; media_authority_weight_i = raw_weight_i / mean(raw_weight), raw_weight 由 config/media_weights.json 按「媒体(中文)」精确匹配→去括号归一化匹配→default 三级查表得到 (10–100 量表); you_2018_score{track}_i 为该篇章在 you_2018 词典 (positive 1,425 / negative 1,583 词) 上按语言学规则 (否定翻转/程度副词/转折) 计算的净情感分'
producer: pipeline\panel\encode.py::compute_media_authority_weights (步骤3c 加权) + pipeline\panel\runner.py (步骤3c 调用 + 逐篇 you_2018_score_mw{track} 生成) + pipeline\panel\encode.py::聚合块 L1092 (sum 聚合) + pipeline\sentiment\tone_words.py (you_2018 词典逐篇打分, 上游)
upstream:
- you_2018_score_full
- you_2018_score_ctx
- you_2018_score_ss
- media_authority_weight
- sum_media_authority_weight
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: Curbing enthusiasm - Media sentiment and the disciplining role of quarterly earnings announcements
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: Language and domain specificity - A Chinese financial sentiment dictionary
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: Disclosure sentiment - Machine learning vs. dictionary methods
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
new_dois: []
---

## CORE

【构念与来源】
you_2018_score_mw_sum{track} 度量的是「银行-年」窗口内、以媒体权威性为权重加总后的 you_2018 词典净情感强度, 是本项目情感三法 (词典法/LLM 法/BERT 法) 中词典法一支下、六本词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran_mcdonald_zh_2026) 之一的加权测度族。词典本体 you_2018 取自 You, Zhang & Zhang (2018, Review of Financial Studies)「Who captures the power of the pen?」, 该文构造了区分官方媒体 (党报口径) 与市场化媒体 (都市报/财经媒体口径) 两类语调锚的框架, 用以检验媒体报道基调对公司融资成本、投资者行为的因果影响; 本项目沿用其中文金融情感词典本体 (positive 1,425 词 / negative 1,583 词, 另含 definite 388 词 / ambiguous 178 词供 clarity 族复用), 作为词典法六本词典之一喂入统一的语言学规则打分引擎。词典逐篇净分先由 `tone_words.py` 按否定翻转/程度副词加权/转折降权三条规则计算出 `you_2018_score{track}` (每篇一个浮点净分, 不做归一化), 再在面板聚合阶段乘以该篇报道所属媒体的权威性权重 `media_authority_weight`, 求和得到本列。这不是词典法的 canonical 输出 (canonical 是同名不带后缀的 `you_2018_score{track}` 篇章级均值/求和聚合), 而是与「等权求和」`you_2018_score_sum{track}`、以「关注度加权」(VW, mention_density) 与「羊群衰减加权」(HW, herd_weight) 并列的第三类加权稳健性测度: MW 用媒体权威性对冲小报与权威财经媒体等权混同的问题, 三种加权方式互为稳健性、不分主次。

【方法学与计算】
媒体权威性权重的构造依据 Holzman, Miller & Twedt (2023, The Accounting Review)「Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements」Appendix A 的 Outlet Impact Media Sent 加权方法: 该文通过滚动回归估计每家媒体报道对股票周转率的边际贡献, 再按估计出的贡献度排名百分位赋权, 用以说明不同媒体对市场的实际影响力存在系统性差异, 不应等权处理。本项目未逐媒体重新估计边际贡献回归 (数据与算力约束下的简化替代), 而是采用 `config/media_weights.json` 中预先设定的静态权威性评分 (10–100 量表, 财经权威媒体评分显著高于地方都市报/晚报) 作为该边际贡献排名的代理。匹配策略分三级: ① 媒体名精确匹配 `media_weights.json` 键; ② 去括号归一化匹配 (如「扬子晚报(数字报)」归一化为「扬子晚报」再匹配, 处理同一媒体不同版式署名); ③ 两级均未命中则退回 `media_weights.json::default` 键 (默认权重 10, 与 `68_media_diversity.py` 的默认口径严格一致, 避免同一份媒体权重表在不同 producer 里出现两套默认值)。三级匹配后得到原始权重 `raw_weight`, 再做均值归一化 `media_authority_weight = raw_weight / mean(raw_weight)`, 使加权版本量级 ≈ 等权版本 (均值恒为 1), 保证 MW 求和列与不加权求和列在数量级上直接可比、差异纯粹来自媒体权威性分布形态而非量纲平移。逐篇 `you_2018_score_mw{track} = you_2018_score{track} × media_authority_weight` 在 `runner.py` 步骤 3c 生成, 与 VW (`mention_density` 加权) / HW (三轨独立的 `herd_weight{track}` 加权, 缺失时退化单轨) 共用同一「先逐篇加权、再按银行-年求和」的两步流水线, 三者互不覆盖、并行存档。面板聚合阶段 (`encode.py`) 按银行-年分组对 `you_2018_score_mw{track}` 求和, 得到本列; 同批产出的 `sum_media_authority_weight` (权重本身按银行-年求和) 充当分母, 用于下游派生 `you_2018_tone_mw{track} = you_2018_score_mw_sum{track} / sum_media_authority_weight` (加权均值语调, 与本列的加权求和「总量」在语义上互补但非同一测度: 求和反映银行-年总加权情感强度且随报道量单调放大, 加权均值反映去规模效应后的语调水平)。三轨 full/ctx/ss 各自独立走完整套「篇章级词典打分 → 逐篇媒体权威加权 → 银行-年求和」流水线, 互不借用彼此的中间结果。

【文献定位】
本列的构念定位横跨两支独立文献: 一支是中文金融文本情感词典构造, 另一支是媒体权威性/媒体影响力加权。词典本体锚定 You, Zhang & Zhang (2018, RFS), 该文本身即是媒体语调影响公司融资行为的经典因果识别范式 (「谁捕获了笔的力量」), 与本项目「媒体报道语调 → 银行融资成本/声誉」的核心研究问题高度对齐, 是词典法六本词典中唯一原生服务于金融机构语境 (而非泛用金融文本或年报文本) 的中文词典。加权机制锚定 Holzman, Miller & Twedt (2023, The Accounting Review) 的 Outlet Impact 加权框架, 其核心洞见 (不同媒体对市场的边际影响力存在系统性差异, 等权处理会低估权威媒体、高估长尾小报的实际信息含量) 是本列区别于同族「等权求和」变体的方法学依据。词典法本身的效度与机器学习/LLM 方法的比较参照 Frankel, Jennings & Lee (2022, Management Science)「Disclosure Sentiment: Machine Learning vs. Dictionary Methods」, 该文系统比较了词典法与机器学习情感分类法在披露文本上的表现差异, 是本项目「词典法/LLM 法/BERT 法三法并列、互为稳健性」总体设计的方法学先例之一; du_2022 (Review of Finance) 则是六本词典中另一本聚焦中文金融语境政治词汇特殊性的姊妹词典, 与 you_2018 共同构成词典法多词典梯度的两个代表性节点。

## VAR: you_2018_score_mw_sum_full

【变体差分】
本列取 full 轨: 篇章级打分文本 = 标题 + 全文正文 (prepend_title 拼接), 是三轨中信息覆盖最完整的一支, 也是留篇门控 (2026-06-29 起 full-only) 唯一直接决定「一篇报道是否计入银行-金科报道行宇宙」这一判定所依赖的轨道 —— stage 21 是否判为一篇有效的银行-金科报道只看 `llm_verified_full == True`, ctx/ss 两轨的留篇集合是 full 轨留篇集的子集, 本列本身不参与该门控判定, 但共享由 full 轨确定的行宇宙。you_2018_score_mw_sum_full 的上游篇章级分值 `you_2018_score_full` 在完整正文上运行否定翻转/程度副词加权/转折降权三条语言学规则, 覆盖面最广、样本量最大, 但也最容易被与银行-金科关系无直接关联的正文段落 (如公司治理、常规业务公告等无关语调的段落) 稀释真实的语调信号, 是「信息量最大但噪声也可能最大」的一端。加权链条上, 该篇章级分值先乘以按 `config/media_weights.json` 三级匹配得到的均值归一化媒体权威性权重 `media_authority_weight`, 再按银行-年分组求和, 与 VW (`mention_density` 关注度加权) / HW (`herd_weight_full` 羊群衰减加权) 的 full 轨版本共用同一逐篇加权、按组求和的两步流水线, 三种加权口径互不覆盖、并行存档于面板。full 轨与 ctx/ss 两轨在本族内是并排的「互为稳健性、不分主次」测度, 三者各自独立走完整的打分-加权-求和链路, 不共享任何中间结果; 铁律上禁止将三轨测度混入同一个 over-identified 的 Hansen J 检验设计中同时作为工具变量或内生解释变量的多个替代测度使用, 每一轨都应各自 just-identified 并排使用。

## VAR: you_2018_score_mw_sum_ctx

【变体差分】
本列取 ctx 轨: 篇章级打分文本 = 标题 + 目标银行实体窗口 (围绕银行实体名截取的局部上下文片段, 在 stage 14 `ctx_materializer` 中经 `prepend_title` 物化为 `content_ctx` 列), 用以剥离与银行主体无直接关联的正文噪声段落, 是 full 轨之外的 conditional-on-full 测度/稳健性轨 —— 行宇宙仍由 full 轨的 `llm_verified_full` 留篇门控确定 (ctx 轨留篇集是 full 轨留篇集的子集), 但本列的篇章级分值 `you_2018_score_ctx` 本身在该子集上按 ctx 文本独立重新执行否定翻转/程度副词/转折三条语言学规则打分, 不复用 full 轨的打分结果。当某篇报道不存在可提取的银行实体窗口时, `content_ctx` 按镜像 `_ss` 的回退语义退回全文正文, 并置位 `ctx_is_fallback=True`, 该退化情形与 full 轨共享同一 `n_articles` 分母口径, 不产生单边孤儿列 (即不会出现 ctx 轨分值为 NaN 而 full 轨有值的不对称缺失)。ctx 轨的篇章级分值同样先乘以三级匹配 (精确/去括号归一化/default) 得到的均值归一化 `media_authority_weight`, 再按银行-年分组求和得到本列; ctx 轨与 full/ss 两轨在媒体权威性加权与银行-年求和这一构造链条上完全并行、各自独立计算中间结果, 三者互为稳健性不分主次, 铁律上禁止把 ctx 轨与 full/ss 轨混入同一个 over-identified 的 Hansen J 检验中一并作为多个替代测度使用。

## VAR: you_2018_score_mw_sum_ss

【变体差分】
本列取 ss 轨: 篇章级打分文本 = 标题 + 银行实体与金科词同句 (±N 句窗, 默认 N=1, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 与 stage 13 `cooccurrence_filter.sentence_radius` 是两个不同配置键、判据主体也不同) 共现片段, 是三轨中判定口径最严格、文本范围最窄的一支, 用以验证语调测度是否对「银行与金融科技话题真正在同一句中出现」这一最强共现假设敏感, 是 ctx 轨 (实体窗口, 较宽松) 之外更保守的一重稳健性检验。ss 轨的篇章级分值 `you_2018_score_ss` 在 `content_ss` 上独立重跑三条语言学规则, 不与 full/ctx 两轨共享中间打分结果。当某篇报道不存在银行∧金科同句共现时, `content_ss` 回退为全文正文, 并置位 `ss_is_fallback=True`, 回退语义严格镜像 ctx 轨的回退语义 (共享与 full 轨相同的 `n_articles` 分母口径, 不产生单边孤儿); 若整个语料的 `FINTECH_AC` 自动机未播种 (为 None), 则该批次全部报道的 `*_is_fallback` 一律置 True, 整体优雅降级为等同 full 轨的宽口径, 而非静默清空样本。ss 轨的篇章级分值同样先按三级匹配 (精确/去括号归一化/default) 得到均值归一化 `media_authority_weight` 加权, 再按银行-年分组求和得到本列; ss 轨与 full/ctx 两轨各自独立完成打分-加权-求和全链路, 三者并排互为稳健性、不分主次, 铁律上禁止将 ss 轨与 full/ctx 轨混入同一个 over-identified Hansen J 检验中同时作为多个替代测度使用。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm - Media sentiment and the disciplining role of quarterly earnings announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity - A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment - Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
<!-- rendered-citations:end -->
