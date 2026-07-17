---
family_id: F646
columns:
- you_2018_pos_count_ctx
- you_2018_pos_count_full
- you_2018_pos_count_ss
unit: 篇数/计数 (count, 非负整数值域, 存储为 double)
formula: count_you2018_pos(track) = 该篇报道 track 文本 (content_full / content_ctx / content_ss) 中命中 you_2018 词典 positive 词表 (You, Zhang & Zhang, 2018, 1,425 词) 的原始命中次数, 经语言学规则 (否定翻转/程度副词/转折连词) 调整后按 track 独立统计; 不做长度归一, 不做跨词典聚合
producer: pipeline\sentiment\tone_words.py (词典打分主逻辑, stage 22) ; pipeline\panel\export.py (bank-year 面板聚合)
upstream:
- 14_materialize_ctx (content_ctx/content_ss 物化)
- config/tone_dicts.json (you_2018 词典源, positive 1,425 词 / negative 1,583 词 / definite 388 词 / ambiguous 178 词)
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
- doi: 10.1007/s11142-008-9083-2
  type: journal
  authors: You, H., & Zhang, X.-J.
  year: 2009
  title: Financial reporting complexity and investor underreaction to 10-K information
  venue: Review of Accounting Studies
  vol: '14'
  issue: '4'
  pages_or_artno: 559-586
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: A new Chinese financial sentiment dictionary for textual analysis in accounting and finance
  venue: SSRN Working Paper
  pages_or_artno: '3446388'
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: Text-based sentiment analysis in finance ; Synthesising the existing literature and exploring future directions
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: "10.1016/j.jcorpfin.2026.103033"
  type: "journal"
  authors: "Battalio, R., Loughran, T., & McDonald, B."
  year: 2026
  title: "How managers frame capital budgeting in investor communications"
  venue: "Journal of Corporate Finance"
  vol: "100"
  pages_or_artno: "103033"
- doi: "10.1016/j.cjar.2025.100406"
  type: "journal"
  authors: "Zhao, J., & Ren, M."
  year: 2025
  title: "Innovative or conservative? How clan culture shapes bank digital transformation in China"
  venue: "China Journal of Accounting Research"
  vol: "18"
  issue: "2"
  pages_or_artno: "100406"
new_dois: []
---

## CORE

【构念与来源】
you_2018_pos_count 家族衡量单篇银行×金科报道文本中命中 You, Zhang & Zhang (2018, Review of Financial Studies)「谁把持了笔杆子」(Who Captures the Power of the Pen) 一文所建构的中文金融正面情感词表的原始命中次数。该词典是本项目 stage 22 词典法情感打分六词典矩阵之一 (另五为 jiang_2021、yao_2021、bian_2021、du_2022、loughran_mcdonald_zh_2026), 收录正面词 1,425 个、负面词 1,583 个 (另含 definite 388 词 / ambiguous 178 词, 后者自 v3.5.1 起专供 clarity 测度使用、不参与本情感计数)。You et al. (2018) 原文的核心贡献是把中国官方媒体与市场化媒体在企业新闻报道上的系统性语调差异映射为「谁在为企业代言」的治理与信息中介问题, 其词典是配合该实证设计构建的中文语境金融情感词表, 与美式 Loughran-McDonald (2011) 词典面向英文 10-K 文本的构建路径不同, 更贴合中国新闻报道的表达习惯与措辞密度。本项目将该词典移植进多词典并行打分体系, pos_count 是六族计数变量之一 (对应词典法打分流程中 「先分词命中→再规则调整→再计数/加权/评分」三层输出中的第一层「计数」层), 与同族的 neg_count (负面命中数)、score (规则调整后综合语调分) 等变量互为不同抽取层级、共享同一词典源但语义不可相互替代。

需要特别强调的是, pos_count 是「命中次数计数」而非「语调得分」——它不做正负相抵、不做词典规模归一化, 仅回答「该篇报道 track 文本中出现了多少次 you_2018 正面词」这一计数问题。这一属性使其在稳健性检验中扮演「原始信号强度」的角色: 当研究者担心 score 类变量的规则调整 (否定翻转/程度副词/转折连词) 引入过多结构性假设时, pos_count 提供了未经复杂变换的底层计数作为交叉验证锚点。同时, pos_count 也是词典消融梯度 (`_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}` 等变体) 的上游输入之一——尽管 pos_count 本身不直接参与该消融矩阵 (消融变体作用于 score 层), 但理解 pos_count 的"零规则"性质有助于把握消融梯度中 raw 变体与本变量在方法论上的呼应关系: raw 变体近似于剥离全部语言学规则后的裸计数, pos_count 正是这条链路最底层、未经规则处理前的候选命中层 (词典命中在规则调整前后计数会有差异, pos_count 记录的是规则调整后的净命中, 详见【方法学与计算】)。

【方法学与计算】
计算流程分两步。第一步, 分词与词典匹配: 对 track 文本 (full/ctx/ss 三选一) 用项目冻结版本 jieba==0.42.1 分词, 逐词/逐 n-gram 匹配 you_2018 positive 词表 (1,425 词, 载入自 config/tone_dicts.json, 与项目内其余五部词典同源加载、同一套加载器 tone_words.py 处理, 不单独硬编码路径)。第二步, 语言学规则调整: 对每个命中词, 检查其局部窗口内是否存在否定词 (触发极性翻转, 命中词从「正面」计入变为「负面」或抵消)、程度副词 (强化/弱化权重, 但不改变计入方向)、转折连词 (依据规则可能降权后半分句命中)。规则调整完毕后, 归入正面桶的命中次数汇总即为 you_2018_pos_count。词典消歧口径遵循项目统一约定: you_2018 词典 positive∩negative 跨类重叠词 (5 词) 采用「两侧计数」而非单侧剔除或 last-writer-wins 覆盖——重叠词在 pos_count 与 neg_count 中各计一次, 不做武断选边。

三个变量 (_ctx/_full/_ss) 对应项目统一的三轨文本架构: full=标题+正文全量; ctx=标题+银行/金科实体窗口截取文本; ss=标题+银行∧金科实体同句 (±N 句窗, 默认 N=1) 共现文本, 无该共现窗口时回退为全文 body 并置位 ss_is_fallback=True (回退语义严格镜像 ctx 轨: 无 fintech/entity 窗口命中时同样回退全文并置位对应 is_fallback 标记, 两轨共享同一套 n_articles 分母口径)。三轨在 stage 14 (`14_materialize_ctx`) 物化为 content_full / content_ctx / content_ss 三个独立文本列 (prepend_title 前置标题), stage 22 词典打分对三列各自独立运行整套「分词-匹配-规则-计数」流程, 互不借用彼此的命中结果——即 you_2018_pos_count_full 与 you_2018_pos_count_ctx 不是对同一次匹配结果的裁剪或子集关系, 而是对不同输入文本的独立重新计算, 三者数值上通常存在差异 (ctx/ss 因文本窗口更窄, 命中总数一般 ≤ full 轨对应值, 但因窗口截取可能改变局部否定/转折的规则触发结果, 不保证严格单调)。三轨在计量经济学定位上各自 just-identified 并排, 互为稳健性、不分主次, 严禁将三轨命中数混入同一 over-identified Hansen J 设定 (会构造出伪造的过度识别约束, 因三轨并非独立工具而是同一构念的三种测量口径)。留篇门控口径遵循项目 2026-06-29 起的 full-only 铁律: 一篇报道是否被认定为「有效银行×金科报道」只看 full 轨 LLM 验证结果 (llm_verified_full==True), ctx/ss 轨的 pos_count 是「conditional-on-full」的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 三轨各自在该子集内独立计算 pos_count (而非各轨各自定义留篇标准)。

面板层聚合 (pipeline\panel\export.py) 将文章级 you_2018_pos_count_{track} 按 bank-year 单元汇总, 与家族内 neg_count 等姊妹计数变量共用同一聚合框架, 但作为计数类变量不做该框架内的语调正负相抵处理, 面板层保留的是 bank-year 单元下三轨命中总量 (或均值, 视聚合规格而定, 由下游 panel schema 决定, 本 md 覆盖文章级 producer 与三轨差分口径为主)。

【文献定位】
you_2018 词典的构念根源是 You, Zhang & Zhang (2018, Review of Financial Studies)「Who Captures the Power of the Pen?」, 该文以官方媒体与市场化媒体对同一企业事件报道语调的系统性差异为切入点, 揭示媒体所有权结构如何塑造企业新闻的信息含量与市场反应, 是中国语境下媒体语调—资本市场关系研究的重要方法学锚点, 也是本项目将「媒体语调」作为银行×金科关系核心解释变量之一的直接方法学来源之一。词典法情感测度作为本项目三大情感测度路径之一 (词典法/BERT 分类/LLM 三家投票), 与文本复杂度、可读性研究 (You & Zhang, 2009, *Review of Accounting Studies*, 关于财务报告复杂度与投资者反应不足) 同源同组 (均出自 You 及合作者的文本分析方法学脉络), 后者是本项目 rare_word_ratio 等文本复杂度测度族的方法学母锚, 二者共同构成「文本可读性/情感」两条平行分析主线在方法论谱系上的呼应。词典法情感打分本身作为一种成熟的文本分析范式, 也与近期综述文献 (如 Todd, Bowden & Moshfeghi, 2024, *Intelligent Systems in Accounting, Finance and Management*, 对金融文本情感分析方法的系统梳理) 所刻画的「基于预定义词表的规则式打分」谱系相衔接——本项目在此谱系基础上叠加了否定/程度/转折三类语言学规则调整, 属于该谱系内的增强规则式实现, 而非纯粹词袋计数。 在这一谱系的当代延续上, Battalio、Loughran 与 McDonald (2026) 自建 45 个资本预算术语的词表, 对 2010–2020 年业绩说明会文本做逐词命中统计以刻画管理者的措辞框架, 直接证明「固定词表逐词命中的原始词次计数, 不做长度归一、不跨词表聚合」这一构造在金融顶刊仍属活跃做法, 且由金融词典法的原始提出者参与, 恰可锚定 you_2018_pos_count 不做归一、不跨词典聚合的形态取舍。惟其测度对象为术语使用频次而非情感极性, 原文不作正/负面判定, 更不涉及按极性符号对篇数分拆, 其词表为英文术语表且无否定翻转/程度副词/转折规则层, 分析单元为公司-披露文档, 故它只锚定原始命中词次这一形态, 不涉及本家族正面极性的判定口径。同国别同行业的近期参照是 Zhao 与 Ren (2025): 该文以中国商业银行为对象, 发现宗族文化经「短半径信任推高物理网点与人员依赖」与「风险规避降低风险承担意愿」两条供给侧机制、以及宗族内资源共济削弱信贷需求的需求侧机制抑制银行数字化转型, 与本项目同国别、同行业且同为银行-年层的文本型变量。仅此: 原文该测度的构造口径 (是否为分词后固定词表逐词命中计数) 在可得材料中未见披露、未经核实, 因而只能作为「中国银行业以文本型变量构造银行-年测度」的同域存在性参照, 不可据以宣称词表命中频次的技术路线获得背书; 其词表 (若有) 为数字化/科技关键词而非情感词表, 亦无情感极性与正/负面判定, 文本源为银行年报 (每银行-年单文档) 而非第三方新闻逐篇后聚合, 且无三规则层与 full/ctx/ss 三轨。
## VAR: you_2018_pos_count_ctx

【变体差分】
本列取 content_ctx (标题+实体窗口截取文本) 作为词典匹配的输入文本, 是 you_2018 正面词命中计数在 ctx 轨下的独立测度。ctx 文本以银行/金科相关实体所在段落或窗口为核心, 相比 full 轨舍弃了与目标实体无关的报道正文, 因而通常样本内文本长度显著短于 full 轨, 命中的正面词绝对数一般随之下降, 但信噪比 (命中词与目标实体的语义相关性) 更高, 适合作为「聚焦于目标实体本身语调」的稳健性对照。当 ctx 窗口截取导致实体相关文本缺失 (即无法定位有效实体窗口) 时, content_ctx 按项目统一回退规则退化为全文 body, 并由 ctx_is_fallback 标记该行, 此时 you_2018_pos_count_ctx 在数值上会趋同于（但不严格等于, 因仍是独立分词匹配的结果）full 轨对应值。留篇门控仍以 full 轨 llm_verified_full 为准, ctx 轨样本宇宙是该留篇集合的子集, 与 full 轨互为稳健性并排, 不构成对 full 轨的替代或加总关系。本列与同家族 you_2018_pos_count_full、you_2018_pos_count_ss 严禁混入同一 over-identified 设定。

实践中使用 ctx 轨的典型场景是: 当研究者担心 full 轨命中数被报道正文中与银行×金科关系无关的段落 (例如企业其他业务线的正面报道、无关的行业综述性铺垫段落) 污染, 希望获得更贴近「该银行与该金科实体本身在报道中被如何评价」这一构念的测度时, 应参照 ctx 轨结果而非仅看 full 轨。ctx 轨与 full 轨的差值 (或比值) 本身也可作为「报道语调是否集中于目标实体」的辅助诊断信号, 但该差值不构成本项目正式产出列, 仅供研究者在稳健性附录中自行构造。词典匹配与语言学规则调整流程 (否定翻转/程度副词/转折连词) 在 ctx 轨与 full/ss 轨完全一致, 唯一差异是输入文本来源, 因此三轨命中数差异可完全归因于文本窗口宽窄, 不掺杂规则口径不一致的干扰。

## VAR: you_2018_pos_count_full

【变体差分】
本列取 content_full (标题+正文全量) 作为词典匹配的输入文本, 是本家族的 canonical 主轨、也是本项目留篇门控 (2026-06-29 起 full-only 铁律) 唯一依据的文本轨——一篇报道是否被计入「有效银行×金科报道」样本, 仅取决于该篇 full 轨的 LLM 验证结果 (llm_verified_full==True), 与 ctx/ss 轨的验证或命中情况无关。you_2018_pos_count_full 因覆盖全文, 通常在三轨中命中绝对数最高、文本噪声也相应最大 (可能包含与目标银行×金科关系无直接关联的段落所贡献的正面词命中)。作为三轨之一, full 轨与 ctx/ss 轨各自 just-identified 并排、互为稳健性不分主次——尽管 full 轨承担留篇门控职责, 但在情感测度构念本身的解释力上, full 并不天然优于 ctx/ss, 三者代表对「报道语调」这一构念的三种互补测量视角 (全文语境 vs 实体聚焦语境 vs 严格同句共现语境)。

full 轨没有回退语义 (它本身即是「未截取」的原始文本, 不存在窗口缺失导致的降级情形), 因此 full_is_fallback 这一标记不适用于本列, 与 ctx/ss 两轨须结合各自 is_fallback 标记解读形成对比。由于 full 轨承担留篇门控职责, 其样本宇宙即为项目下游全部情感/属性测度共享的行宇宙基准, 换言之 you_2018_pos_count_full 覆盖的样本行数在三轨中最完整、不存在因回退导致的分母歧义, 是三轨横向比较时的天然锚点。研究者若只能选用单一轨作为主回归口径, 建议以 full 轨为 headline 测量、以 ctx/ss 轨结果在稳健性附录中并列报告, 但不得据此认为 full 轨在构念效度上优于另两轨, 三者仅在样本完整性与门控职责上存在差异。

## VAR: you_2018_pos_count_ss

【变体差分】
本列取 content_ss (标题+银行∧金科实体严格同句共现窗口文本, 窗口半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 N=1) 作为词典匹配的输入文本, 是三轨中文本粒度最细、对「银行与金科科技词汇同句出现」这一共现条件要求最严格的一轨。当某篇报道虽通过 full 轨留篇门控但正文内不存在银行∧金科同句共现 (即找不到满足严格同句条件的窗口) 时, content_ss 按项目统一回退语义 (镜像 ctx 轨回退规则) 退化为全文 body, 并置位 ss_is_fallback=True, 与 ctx 轨共享同一套 n_articles 回退分母口径。此时 you_2018_pos_count_ss 的命中计数来自全文而非严格同句片段, 解读时须结合 ss_is_fallback 标记区分「真同句命中」与「回退全文命中」两种情形, 不应无差别汇总。ss 轨与 ctx/full 轨严格并排、互为稳健性, 三者共享同一 you_2018 词典源与同一套语言学规则引擎, 差异仅来自输入文本窗口宽窄, 不构成层级或替代关系, 亦不得混入同一 over-identified Hansen J 设定中作为多重工具变量使用。

ss 轨的判定不对称口径需特别留意: 银行侧命中在共现判定时经过否定与短名过滤 (避免因银行简称歧义误判共现), 而金科侧命中则采用裸 AC 自动机 (Aho-Corasick, 1,506 词) 直接匹配, 二者判定逻辑不对称, 这一不对称性是共现窗口构造阶段 (stage 13/14) 的既定口径, 与 you_2018_pos_count_ss 本身的词典打分逻辑 (打分阶段 stage 22) 相互独立、不产生叠加偏差——即共现窗口一旦确定, ss 轨内部的词典命中计数仍按标准流程独立执行, 不再区分银行侧/金科侧计数。由于 ss 轨窗口通常显著窄于 ctx 轨 (同句 vs 实体窗口), 在未回退情形下 you_2018_pos_count_ss 的命中绝对数一般是三轨中最低者, 适合作为「最严格共现证据下语调仍然为正」这一强假设的证据下限, 常用于稳健性检验中的保守估计场景。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance ; Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Battalio, R., Loughran, T., & McDonald, B. (2026). How managers frame capital budgeting in investor communications. Journal of Corporate Finance, 100, 103033. https://doi.org/10.1016/j.jcorpfin.2026.103033
Zhao, J., & Ren, M. (2025). Innovative or conservative? How clan culture shapes bank digital transformation in China. China Journal of Accounting Research, 18(2), 100406. https://doi.org/10.1016/j.cjar.2025.100406
<!-- rendered-citations:end -->
