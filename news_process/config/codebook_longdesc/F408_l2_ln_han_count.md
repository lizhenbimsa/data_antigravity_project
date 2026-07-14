---
family_id: F408
columns:
- ln_han_count_ctx
- ln_han_count_full
- ln_han_count_ss
unit: 对数计数 (ln(1+平均汉字数), 无量纲)
formula: 'panel[f"ln_han_count{track}"] = np.log1p(panel[f"avg_han_count{track}"]); avg_han_count{track} 是 bank-year 单元内、该轨道下全部文章 n_han_real (CJK 汉字计数) 的算术均值; n_han_real 由 is_cjk 字符过滤在文章级计得 (与 hard_char_ratio 分子 n_han 同源同值)'
producer: pipeline\panel\geography.py (ln 变换与三轨物化落点); pipeline\sentiment\lexical_complexity.py (HAN_COUNT_KEY='n_han_real' 文章级原始计数定义)
upstream:
- 14_materialize_ctx (content_full/content_ctx/content_ss 三轨文本物化)
- 22_tone_words (lexical_complexity 在文章级算 n_han_real, 随词典法阶段跑三轨)
- encode (H2 段将 n_han_real mean 聚合为 avg_han_count_{full,ctx,ss})
citations:
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: Financial reporting complexity and investor underreaction to 10-K information
  venue: Review of Accounting Studies
  vol: '14'
  issue: '4'
  pages_or_artno: 559–586
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405–459
- doi: 10.2308/accr-50725
  type: journal
  authors: Lundholm, R. J., Rogo, R., & Zhang, J. L.
  year: 2014
  title: 'Restoring the Tower of Babel: How foreign firms communicate with U.S. investors'
  venue: The Accounting Review
  vol: '89'
  issue: '4'
  pages_or_artno: 1453–1485
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: Hope, O.-K., Hu, D., & Lu, H.
  year: 2016
  title: The benefits of specific risk-factor disclosures
  venue: Review of Accounting Studies
  vol: '21'
  issue: '4'
  pages_or_artno: 1005–1045
- doi: "10.1111/ijau.12366"
  title: "Financial report readability and audit fees: Evidence from China"
  authors: "Yuan, D., Yang, X., Qin, R., & Yu, J."
  year: 2024
  venue: "International Journal of Auditing"
  type: "journal"
- doi: "10.1016/j.ribaf.2024.102220"
  title: "Annual report readability and trade credit financing: Evidence from China"
  authors: "Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y."
  year: 2024
  venue: "Research in International Business and Finance"
  type: "journal"
new_dois:
  - "10.1111/ijau.12366"
  - "10.1016/j.ribaf.2024.102220"
---

## CORE

【构念与来源】
ln_han_count 族刻画的是"一家银行在某年份、被报道文章的平均篇幅有多长"这个朴素但在文本计量文献中屡被证明有系统性含义的构念——篇幅本身既是信息量的粗代理, 也是记者/编辑投入、事件重要性、乃至刻意"以量掩质"套话行为的伴生信号。本族是本仓文章长度测度体系的第三条并行口径: geography.py 源码注释明确记录了三口径并存的设计意图——(a) 字符口径 avg_article_length = ln(1+平均字符数), 字符含数字、标点、拉丁字母, 是最粗粒度但计算最简单的长度代理; (b) 词口径 ln_word_count = ln(1+平均 jieba 分词词数), 对应 Li (2008 JAE) 与 He et al. (2024 IRFA) 文献中"MLENGTH"变量的本源定义, 但其绝对值受分词器切分粒度影响; (c) 本族汉字口径 ln_han_count = ln(1+平均 CJK 汉字数), 剔除数字/标点/拉丁字符干扰、也不依赖分词切分正确性, 是三者中"最纯"的中文正文长度代理。三口径互为长度稳健性并排, 不分主次, 分别捕捉篇幅构念的不同侧面——字符口径覆盖面最广但混入符号噪音, 词口径贴合海外经典文献定义但受分词误差影响, 汉字口径居间, 在中文语境下对"实际书写了多少内容"给出一个稳健读数。三支列均由同一原始计数逻辑 n_han_real (定义于 lexical_complexity.py 的 HAN_COUNT_KEY 常量) 驱动: 该计数在文章级用 is_cjk 字符类判据逐字符扫描, 只统计落在 CJK 统一表意文字区段的字符, 与 hard_char_ratio 测度分子 n_han 同源同值 (即两处消费的是同一次扫描结果, 非独立重算), 这保证了长度口径与"生僻字比例"等复杂度测度在底层字符分类上完全一致, 不会因为两套判据版本漂移而产生数值上互不兼容的伪差异。

【方法学与计算】
计算链条分两层: 文章级层在 pipeline/sentiment/lexical_complexity.py 中完成, 对每篇文章的正文字符串做逐字符 CJK 判定并求和, 得到该文章的 n_han_real 计数; 该原始计数随词典法阶段 (22_tone_words) 一并产出, 并经由 LEXICAL_COMPLEXITY_KEYS 机制自动物化为 *_full/*_ctx/*_ss 三个轨道版本 (镜像 tone_words 三轨物化框架, 与 within_doc_redundancy_han 等汉字口径姊妹列走同一物化管线)。面板级层在 encode 阶段的 H2 段, 对同一 bank-year 单元内全部文章的 n_han_real 取算术均值, 得到 avg_han_count_{full,ctx,ss}; 最后由 pipeline/panel/geography.py 对该均值做 np.log1p (即 ln(1+x)) 变换, 产出本族三列 ln_han_count_{full,ctx,ss}。取对数而非直接使用原始均值, 一方面是长度类变量右偏分布的标准处理 (压缩极端长文对回归的杠杆效应), 另一方面便于与同一 geography.py 段落内并排产出的 avg_article_length (字符口径) 与 ln_word_count (词口径) 在同一量纲尺度上做系数比较。三个轨道分别对应: full=标题+全文正文, 该轨的 n_han_real 是三轨中口径最宽的一支, 天然长度也最大; ctx=标题+实体窗口截取文本, 只统计围绕目标银行实体的局部窗口内汉字数, 数值上系统性小于 full 轨; ss=标题+银行∧金科同句共现窗口 (句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认±1句), 是三轨中窗口最窄的一支。三轨物化逻辑在 geography.py 中用 `for _track in ('_full', '_ctx', '_ss')` 循环、逐一检查 avg_han_count{track} 是否存在于面板列中再做变换, 若某轨对应的源列因上游未落盘而缺失, 该轨列优雅跳过、不产出 (不会写 NaN 占位, 而是整列不存在), 这是与"值为 NaN"的降级语义不同的"列缺席"降级语义, 二者须在下游消费代码中分别处理。ss 轨在文章级 content_ss 物化时遵循与 content_ctx 一致的镜像回退语义: 当某篇文章内不存在银行与金科词的同句共现时, content_ss 退化为全文 body (即与 full 轨文本内容趋同), 并置位 ss_is_fallback=True 标记该行处于回退状态, 分母仍计入 n_articles 而不剔除, 该回退语义直接决定了当某 bank-year 单元内多数文章处于 ss 回退态时, ln_han_count_ss 会在数值上向 ln_han_count_full 靠拢, 这是理解 ctx/ss 两轨相对 full 轨系统性差异时必须纳入的机制性背景, 而非测度本身的缺陷。

【文献定位】
篇幅/复杂度作为文本计量的基础控制变量或独立解释变量, 在会计与金融文本分析文献中有扎实的方法学脉络。You and Zhang (2009, Review of Accounting Studies) 是文本复杂度—投资者反应不足这一研究线索的经典锚点, 其核心发现是财报文本复杂度 (含长度维度) 与信息在市场中被充分消化的速度呈负相关, 为"篇幅并非中性变量、须作为控制项或独立构念纳入模型"提供了理论依据, 本族三口径长度测度即服务于这一控制变量角色。Lundholm, Rogo, and Zhang (2014, The Accounting Review) 在跨语言/跨文化披露沟通研究中同样将文本篇幅与可读性并列作为影响信息传递效率的关键维度, 佐证了在非英语 (本仓为中文) 语境下坚持长度测度多口径并行的必要性——不同语言的"词"与"字"边界界定方式不同, 单一口径可能在跨语言比较中引入系统性偏误。Hope, Hu, and Lu (2016, Review of Accounting Studies) 关于具体风险因子披露收益的研究, 其方法学框架同样以文本长度/具体性作为基础解释变量之一, 与本仓 lexical_complexity.py 中 specificity_index/named_entity_ratio 等测度共享同一文献脉络, 本族汉字长度口径是这一测度簇的长度维度补丁。Piotroski, Wong, and Zhang (2015, Journal of Accounting Research) 研究中国上市公司政治激励下压制负面信息的行为, 是本仓聚焦中国语境新闻文本分析的方法学近邻, 其研究设计中同样需要控制报道篇幅这一混淆变量, 为本族测度在中国银行新闻场景下的适用性提供了直接的文献佐证——中文财经报道的篇幅分布特征 (含官方通稿式的固定套话结构) 与英文语境存在系统性差异, 这正是本仓坚持"字符/词/汉字"三口径并行而非照搬单一英文文献口径的方法学动机。Yuan, Yang, Qin, & Yu (2024, International Journal of Auditing) 研究中国财报可读性(含篇幅维度)对审计收费的影响,为文本篇幅作为信息复杂度代理变量提供中国语境下的方法学佐证。Li, Yang, Xue, & Liu (2024, Research in International Business and Finance) 用机器学习方法测度中国上市公司年报可读性与篇幅,考察其对贸易信用融资获取的影响,呼应本族三口径长度测度的中国语境适用性。三轨 (full/ctx/ss) 铁律在此适用: 三轨各自 just-identified 并排、互为稳健性、不分主次, 在同一回归设计中绝不可将三轨长度列混入同一 over-identified Hansen J 检验; 三口径 (字符/词/汉字) 与三轨 (full/ctx/ss) 是两条正交的变异轴, 合计构成一个 3×3 的长度测度矩阵, 使用时应明确声明所选口径与轨道的组合依据, 而非隐含假设三者可互相替代。留篇门控口径 (2026-06-29 起) 对本族同样适用: 决定"某篇文章是否计入某银行—金科报道"的判据始终是 llm_verified_full==True (即 full-only 门控), ctx/ss 两轨的 n_articles 分母是 full 留篇集的子集条件测度, 而非独立样本, 这意味着 ln_han_count_ctx/ss 中隐含的 avg_han_count 均值分母 (bank-year 单元内文章数) 与 full 轨共享同一留篇集合, 三轨差异纯粹来自窗口截取宽度而非样本构成差异。

## VAR: ln_han_count_ctx

【变体差分】
ln_han_count_ctx 是本族 ctx (实体窗口) 轨道版本, 底层源列 avg_han_count_ctx 的分子逐篇取值来自 content_ctx——即"标题+围绕目标银行实体的窗口文本"经 prepend_title 拼接后的正文, 而非全文。窗口宽度由实体上下文抽取逻辑控制 (与 stage 14 materialize_ctx 的实体窗口定义一致), 因此单篇文章的 n_han_real 计数天然小于等于同一篇文章 full 轨的对应计数——ctx 轨截取的是 full 轨文本的一个子窗口, 汉字数不会因窗口截取而增加。该列与 ln_han_count_full/ln_han_count_ss 在同一 bank-year 单元上共享 n_articles 分母 (均受 full-only 留篇门控约束), 但分子 avg_han_count 逐篇取自不同文本窗口, 三者数值层面不构成同一变量的重复测量, 而是分别捕捉"全篇篇幅""实体局部窗口篇幅""银行金科共现句窗口篇幅"三个有区别的构念侧面。在缺列降级上, 若上游 avg_han_count_ctx 因 stage 14/22 未产出 content_ctx 相关列而缺失, geography.py 的 if 守卫会使该列整体不生成 (非置 NaN), 使用者在读取面板时应先检查该列是否存在而非假设其恒在。作为方法学锚点使用时, ctx 轨与 Lundholm et al. (2014) 强调的"聚焦相关信息片段"研究设计思路更契合——ctx 窗口天然过滤掉与目标银行实体无关的正文段落, 使得该轨的长度读数更贴近"围绕该银行本身实际写了多少字", 而非整篇报道 (可能覆盖多家机构或多个事件) 的总篇幅。使用该列时须遵守三轨并排铁律: 不可将 ctx 轨与 full/ss 轨长度列同时作为同一构念的多重工具变量放入单一 over-identified 检验, 三者应作为互为稳健性的并列设定分别汇报。

## VAR: ln_han_count_full

【变体差分】
ln_han_count_full 是本族的全文轨道版本, 也是三轨中文本覆盖范围最宽、口径含义最直接的一支——底层源列 avg_han_count_full 的分子逐篇取值来自 content_full, 即"标题+完整正文"经 prepend_title 拼接后的全部文本, 涵盖该篇文章报道的全部内容而非任何局部窗口截取。在 P1 主线 (bank_fintech_tone) 等已切换为 full-only 主轨的论文模块语境下, ln_han_count_full 是与主处理变量 llm_vote_tone_full 同轨对齐的长度控制变量首选——回归设计中若要控制"报道篇幅"这一混淆因素, 使用与处理变量同轨的长度测度可以避免因轨道不匹配引入额外的测量误差协变。该列同时是留篇门控 (llm_verified_full==True) 直接定义的行子集上计算的, 即该列所依赖的 n_articles 分母就是门控本身的定义集合, 不存在条件化于其他轨道子集的问题, 这与 ctx/ss 两轨"分母继承自 full 留篇集"的从属关系形成对照——full 轨是分母的定义者, ctx/ss 轨是分母的继承者。数值上, ln_han_count_full 相对 ln_han_count_ctx/ln_han_count_ss 通常取值更大 (对数变换前的原始均值更大), 因为全文口径不做任何窗口截取, 天然容纳标题以外的完整报道正文, 含背景介绍、多方评论、数据引用等 ctx/ss 窗口可能截断掉的段落。方法学定位上, 该列与字符口径 avg_article_length、词口径 ln_word_count 的 full 轨对应列共同构成"三口径同轨"组合, 在报告篇幅控制变量的稳健性时, 建议优先汇报该三者的 full 轨组合作为主设定, ctx/ss 轨的对应组合作为并列稳健性检验, 严格遵守三轨/三口径互为并排、禁止混入同一 over-identified Hansen J 的铁律。

## VAR: ln_han_count_ss

【变体差分】
ln_han_count_ss 是本族的句子共现窗口轨道版本, 底层源列 avg_han_count_ss 的分子逐篇取值来自 content_ss——即"标题+银行与金科词同句共现窗口"文本 (句子半径见 config/filtering.yaml::context_window.ss_sentence_radius, 默认±1句), 是三轨中文本窗口最窄、判据最严格的一支。当某篇文章内不存在银行实体与金科词汇的同句共现时, content_ss 依 ctx 轨镜像回退语义退化为全文 body, 并置位 ss_is_fallback=True, 该篇文章仍计入 n_articles 分母 (与 full/ctx 共享)、但其 n_han_real 取值等同于该篇 full 轨的取值, 而非因窗口截取失败而记为缺失或零。这一回退语义的直接后果是: 当某 bank-year 单元内 ss 轨回退比例较高时, ln_han_count_ss 会向 ln_han_count_full 数值上趋同, 而非系统性地小于 full 轨——这与 ctx 轨"窗口恒截取、恒小于等于 full"的行为模式不同, 使用者在解读 ss 轨与 full 轨长度差异时应先核对该 bank-year 单元的 ss_is_fallback 比例, 避免将"回退导致的趋同"误读为"共现窗口本身很长"。当非回退 (即真实存在同句共现) 的文章占多数时, ln_han_count_ss 捕捉的是"银行与金科词紧邻共同出现的那句话及其邻近句子有多长", 这是三轨中对"银行—金科关联叙事密度"最直接的篇幅代理——一句话内同时提及银行与金科概念、且该句本身冗长, 可能反映记者对二者关系做了更详尽的铺陈, 而非仅一笔带过的并列提及。方法学上, 该列与 P5 (bank_fintech_collab, Chesbrough 框架) 等聚焦银行—金科协作叙事的论文模块在构念上关联最紧密, 因为 ss 轨窗口的定义判据本身就是"银行∧金科同句", 与该类论文的核心处理变量共享同一底层共现抽取逻辑。使用该列时同样须遵守三轨并排铁律 (禁止与 full/ctx 轨长度列混入同一 over-identified Hansen J), 并额外注意 ss 轨镜像回退语义带来的"高回退率单元趋同于 full 轨"这一测度特有性质, 在稳健性附注中应披露样本内 ss_is_fallback 的整体占比, 以便读者判断该轨结果的可信区间。
<!-- rendered-citations:begin -->
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559–586. https://doi.org/10.1007/s11142-008-9083-2
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405–459. https://doi.org/10.1111/1475-679X.12071
Lundholm, R. J., Rogo, R., & Zhang, J. L. (2014). Restoring the Tower of Babel: How foreign firms communicate with U.S. investors. The Accounting Review, 89(4), 1453–1485. https://doi.org/10.2308/accr-50725
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005–1045. https://doi.org/10.1007/s11142-016-9371-1
Yuan, D., Yang, X., Qin, R., & Yu, J. (2024). Financial report readability and audit fees: Evidence from China. International Journal of Auditing. https://doi.org/10.1111/ijau.12366
Li, H.-Q., Yang, Y., Xue, F.-W., & Liu, Z.-Y. (2024). Annual report readability and trade credit financing: Evidence from China. Research in International Business and Finance. https://doi.org/10.1016/j.ribaf.2024.102220
<!-- rendered-citations:end -->
