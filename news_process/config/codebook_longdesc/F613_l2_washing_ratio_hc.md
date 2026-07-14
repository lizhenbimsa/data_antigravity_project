---
family_id: F613
columns:
- washing_ratio_hc
- washing_ratio_hc_ctx
- washing_ratio_hc_ss
unit: 比率/占比 (proportion, [0,1]; 分母为 0 时输出 NaN, 非 0)
formula: 'washing_ratio_hc{track} = pos_symb_hc_count{track} / pos_hc_substvalid_count{track} (同域分母缺失时回退 pos_hc_count{track}); 分子/分母均限定于三家 LLM 情感投票一致性 agreement_rate ≥ 2/3-1e-9 的高置信度子样本'
producer: pipeline\panel\runner.py::步骤7h(方法F, HC_AGREEMENT_THRESHOLD 判据+_svd_denom 同域分母) ; pipeline\panel\encode.py(pos_hc_count/pos_symb_hc_count 聚合) ; pipeline\panel\export.py(变量标签)
upstream: [pos_count, innovation_substantiveness, llm_agreement_rate, pos_hc_count, pos_symb_hc_count, pos_hc_substvalid_count]
citations:
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
  vol: '80'
  issue: '2'
  pages_or_artno: 699-754
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: 'Ownership concentration and corporate greenwashing in China''s capital markets: Based on a multi-actors perspective'
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: Article 102600
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: Article 109684
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_hc 族衡量的是"洗稿"(cheap talk / symbolic disclosure)现象在高置信度子样本上的强度: 在一篇文章被三家 LLM 一致判为正面情感 (`is_positive{track}==1`) 且三家投票一致性 (`llm_agreement_rate{track}`) 达到高置信门槛的前提下, 该文章是否同时被判定为"象征性"(符号性、无实质业务内容, W&Z 1998 分类下 `innovation_substantiveness{track}=='象征性'`) 而非"实质性"报道。分子是同时满足"正面+象征性+高置信"三条件的文章数 `pos_symb_hc_count{track}`, 分母是"正面+高置信+实质性已测量"的同域计数 `pos_hc_substvalid_count{track}` (缺该同域列时按旧 schema 回退到物理计数 `pos_hc_count{track}`, 由 `_svd_denom` 函数统一实现并告警)。比值越高, 表明该银行-年的正面报道中, 越大比例的"好新闻"其实是缺乏实质内容的符号性宣传("媒体自我美化"/自我塑造式公关), 而非有具体业务信息支撑的正面报道 — 这正是 washing (洗稿/漂绿式话术) 构念在文本层面的操作化度量。该族是 F613 家族三个列的共同构念载体 (washing_ratio_hc / _ctx / _ss), 三者共享同一分子分母公式, 仅在文本轨道 (full/ctx/ss) 上不同, 详见各 VAR 节。

家族命名中的 "hc" 特指 "high confidence"(高置信度)子样本限定, 对应 runner.py 步骤 7h 中标注的"方法 F"。这是 washing_ratio 多方法矩阵 (方法 A: LLM 投票极化条件法; A2: 单模型; D/D2: 词典均值/单词典; E/E2: BERT 均值/单模型; F: 高置信度子样本; G: 情感偏移) 里专门用来做测量误差稳健性检验的一支: 它不改变"正面且象征性"的分子构念本身, 而是把样本限定在 LLM 三家投票高度一致 (agreement_rate ≥ 2/3, 阈值取 `(2.0/3.0) - 1e-9` 以数值上稳妥地把恰好 2/3 一致的边界档位纳入高置信集合, 避免浮点比较的假阴性排除) 的那部分文章上, 从而剥离掉因三家 LLM 判断分歧导致的标签噪声, 检验洗稿率的核心结论是否仅由低置信度、易错判的边缘样本驱动。

【方法学与计算】
washing_ratio_hc 的构造分两层。第一层是文章级布尔旗标, 在 `pipeline/panel/runner.py` 步骤 7h 内对每条轨道 `track ∈ {_full, _ctx, _ss}` 逐一计算: `_hc = llm_agreement_rate{track}.fillna(0) >= HC_AGREEMENT_THRESHOLD`(缺失一致性视为不满足高置信); `_is_pos_hc{track} = (pos_count{track}==1) & _hc`; `_is_pos_symb_hc{track} = (pos_count{track}==1) & is_symb & _hc`; 同时并行生成同域分母旗标 `_svd_pos_hc{track} = (pos_count{track}==1) & _hc & _subst_measured`(`_subst_measured` 指该文章 `innovation_substantiveness` 已被 LLM 实质性分类成功测量, 非 NaN)。第二层在 `pipeline/panel/encode.py` 按 (target_bank, year) 分组聚合为面板计数列 `pos_hc_count{track}`(`_is_pos_hc{track}` 求和) 与 `pos_symb_hc_count{track}`(`_is_pos_symb_hc{track}` 求和), 以及分母侧的 `pos_hc_substvalid_count{track}`(`_svd_pos_hc{track}` 求和)。第三层回到 runner.py 步骤 7h 末尾用 `_safe_ratio` 做除法: 分母 ≤ 0 时输出 NaN (而非 0 或 inf, 避免把"无高置信正面样本"误判为"零洗稿"), 分母来源经 `_svd_denom` 优先取同域分母 `pos_hc_substvalid_count{track}`, 该列缺失时 (旧 schema) 回退到物理计数 `pos_hc_count{track}` 并记录告警日志。

这一"同域分母"设计 (fix omni-g-runner-10/14, 2026-06-11) 是关键的测量误差修正: 分子 `pos_symb_hc_count` 隐式要求 `innovation_substantiveness` 已被 LLM 成功分类 (未成功分类的文章 astype(str) 后为 'nan' 字符串, 永远不等于 '象征性', 因而分子恒排除); 若分母仍沿用未按"实质性已测量"过滤的物理计数 `pos_hc_count`, 则当 LLM 实质性分类失败率系统性上升时 (例如某年该模型解析失败增多), 分子分母的有效样本域发生错配, 洗稿率会被系统性下拉, 制造与真实洗稿现象无关的虚假趋势。同域化分母修正后, 分子分母共享同一"高置信且实质性判断成功"的样本域, 比值才是对"洗稿倾向"的无偏估计。

高置信度阈值 2/3 的选取逻辑: 生产口径三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 对每篇文章的情感做独立判断并投票, `llm_agreement_rate{track}` 记录多数票占比, 取值集合近似 {1/3, 2/3, 1}(三选一分类下的可能一致度)。以 2/3 为门槛意味着至少两家模型判断一致才纳入高置信子样本, 排除三家两两分歧(1/3 一致度, 等价于无多数)的边缘文章; 减去 1e-9 的浮点容差是为了把恰好落在 2/3 = 0.6667 边界档的观测正确纳入 (若直接写 `>= 2/3` 在浮点表示下可能因舍入误差被误判为略小于阈值而漏收, 此修正对应 fix omni-g-runner-05/09)。

【文献定位】
washing/洗稿构念直接呼应企业传播/公司治理文献中"表面披露与实质行为脱钩"的一般命题: `innovation_substantiveness` 分类本身沿用象征性 (symbolic) vs. 实质性 (substantive) 的二分口径, 该口径已在同一 panel 的 `symb_frac`/`n_articles_symb` 变量标签中沿用, 本族在其基础上叠加"正面情感"条件, 把这一二分口径转译为可与洗稿/漂绿文献直接对话的比率测度。就资本市场如何识别与定价"表面正面但缺乏实质内容"的漂绿/洗稿式披露而言, Duchin, Gao & Xu (2025, *The Journal of Finance*) 用工业污染资产市场的证据表明, 市场能够部分甄别可持续性披露中的漂绿成分而非全盘照单全收, 这为本族"用高置信度子样本剥离标签噪声后再度量洗稿强度"的稳健性设计提供了直接的实证动机: 若漂绿/洗稿信号本身就容易被市场参与者与文本分类模型共同误判, 那么先控制分类置信度再估计洗稿率, 才能避免把分类噪声误认成真实的洗稿行为变化。就"表面正面但缺乏实质内容"的漂绿/洗稿式披露操作化而言, 本族与近年公司治理文献中的 greenwashing 测度一脉相承: Fan, Tang, Huang & Yang (2025, *Pacific-Basin Finance Journal*) 用股权集中度视角研究中国资本市场的企业漂绿行为, 与本族在中国银行业媒体报道语境下捕捉"象征性正面报道"占比的思路高度平行; Gorovaia & Makrominas (2024, *European Financial Management*) 提出用自然语言处理方法从企业社会责任报告中识别漂绿, 其"用文本分类信号构造漂绿/洗稿比率"的方法学与本族分子分母构造(正面情感 × 象征性分类的交叉计数比率)属同一测量传统。高置信度子样本稳健性检验的必要性, 亦呼应 Song, Hou, Ouyang & Hao (2026, *Finance Research Letters*) 对"策略性披露与市场反噬 (AI washing: strategic disclosure and backlash)"的最新讨论 — 该文献同属本族命名所在的 "washing" 测度谱系最新锚点, 强调策略性披露信号本身存在被误判的系统性风险; 本族通过限定三家 LLM 判断高度一致(agreement_rate ≥ 2/3)的子样本重新估计洗稿率, 正是对这一"测度信号可能被误判"问题的直接方法学回应, 用以检验核心结论是否仅由低置信度、易错判的边缘样本驱动。

【与相邻测度的构念区分】
washing_ratio_hc (方法 F) 与家族内并列的其余洗稿率方法互为稳健性、不分主次, 各自 just-identified 并排, 禁止混入同一个 over-identified 的 Hansen J 检验: 方法 A `washing_ratio{track}` 是全样本口径 (不做置信度过滤), 是 canonical 主指标; 方法 A2 `washing_ratio_{llm}{track}` 是单个 LLM 口径 (三家模型各自独立, per-model 并排, 见 CLAUDE.md「LLM 三家互为稳健性」铁律); 方法 D/D2 `washing_ratio_dict{,_模型}{track}` 是六部词典均值/单词典口径; 方法 E/E2 `washing_ratio_bert{,_模型}{track}` 是三家 BERT 均值/单模型口径; 方法 G `washing_tone_shift{track}` 不是比率而是象征性文章与全部文章的情感均值之差, 度量情感偏移幅度而非频率占比。本族 (方法 F) 的差异化贡献在于用一致性门槛剥离标签噪声, 是"测量置信度"维度的稳健性检验, 与"测量方法/模型选择"维度 (A2/D2/E2) 及"度量口径"维度 (比率 vs. 偏移量, F vs. G) 正交, 不应相互替代或混入同一识别方程。

本族亦须与非洗稿类"实质性/象征性"分类变量族 (`sub_frac`/`symb_frac`/`n_articles_sub`/`n_articles_symb`) 区分: 后者是分类计数的原始占比 (不涉及情感极性交叉), 前者是"正面情感 × 象征性分类"的条件比率, 构念层级更高、更贴近"洗稿"这一综合行为构念, 而非单纯的文本类型分布。

## VAR: washing_ratio_hc

【变体差分】
washing_ratio_hc 是家族的 full 轨 canonical 列, 对应 runner.py 步骤 7h 中 `track='_full'`(变量名后缀为空, `_sfx=''`)的分支。计算所用文本是三轨架构中的 full 轨 `content_full`(标题+全文正文, 由 stage 14 物化), 分子分母涉及的情感极性 (`pos_count_full`)、象征性分类 (`innovation_substantiveness_full`)、LLM 一致性 (`llm_agreement_rate_full`) 全部取自基于全文的 LLM 判断结果。按 2026-06-29 生效的留篇门控口径, 一篇文章是否被计入面板 (是否构成"一篇银行金科报道")只看 `llm_verified_full == True`, 即行宇宙由 full 轨判定; ctx/ss 轨是在同一留篇集合子集上的稳健性测度, 分子分母仍按各自轨道独立计算 (per-track 列照算, 不借用 full 轨分母, 详见家族 CORE 中 `_svd_denom` 的轨道内闭合逻辑)。该列是 F613 家族三列中唯一的主口径(canonical)列, ctx/ss 两列是与其并排、互为稳健性的轨道稳健性检验, 不构成主次关系, 亦不应混入同一 over-identified 识别方程。在解读上, washing_ratio_hc 因基于全文正文, 覆盖信息量最完整, 通常作为论文正文主回归的默认口径; 但正因全文覆盖面广, 一篇文章中与目标银行无关的段落(例如同一篇报道同时涉及多家银行或宏观政策背景)也会进入象征性/实质性分类的判断输入, 理论上存在把"银行以外内容驱动的象征性标签"错误地记入该银行洗稿率的风险, 这也是引入 ctx/ss 两条并排轨道做稳健性检验的动机所在。与家族内其余洗稿率方法(A 全样本、A2 单模型、D/D2 词典、E/E2 BERT、G 情感偏移)相比, 本列固定在方法 F(高置信度子样本)之下, 仅在文本窗口维度上取 full, 置信度维度与方法维度均与家族其余成员共享同一套构造逻辑, 不重复定义。

## VAR: washing_ratio_hc_ctx

【变体差分】
washing_ratio_hc_ctx 是三轨架构中的 ctx (context) 轨版本, 对应 runner.py 步骤 7h 中 `track='_ctx'`(变量名后缀 `_ctx`, `_sfx='_ctx'`)。所用文本是 `content_ctx`(标题+目标银行实体窗口文本, 由 stage 14 物化), 分子 `pos_symb_hc_count_ctx` 与分母 `pos_hc_substvalid_count_ctx`(或回退 `pos_hc_count_ctx`)均基于 ctx 轨自身的情感投票 (`pos_count_ctx`)、象征性分类 (`innovation_substantiveness_ctx`) 与一致性 (`llm_agreement_rate_ctx`) 独立计算, 不与 full 轨共享中间量。与家族 canonical 列 washing_ratio_hc 的精确差分在于文本窗口的选取: ctx 轨聚焦于银行实体周边语境, 剔除了与目标银行不直接相关的全文段落, 因而对"该银行相关内容是否为象征性正面报道"的判断可能比全文轨更聚焦、也可能因语境窗口截断而丢失部分实质性信息线索, 属于对 washing_ratio_hc 的一种规格稳健性检验 (与 full 轨互为稳健性、不分主次, 各自 just-identified 并排, 禁止混入同一 over-identified Hansen J)。留篇门控上, ctx 轨的行宇宙继承 full 轨的留篇集合子集 (`llm_verified_full==True` 决定的文章集合), 但 ctx 轨自身的分子分母计算完全在 ctx 轨内部闭合, 不借用 full 轨的分母。使用该列的动机是: 若研究者担心 washing_ratio_hc(full 轨) 的高置信度子样本判断被文章中与目标银行无关的段落"稀释"或"污染"(例如一篇长报道大部分篇幅在讨论宏观金融政策, 只有一句话提及目标银行), 则可改用聚焦银行实体窗口的 ctx 轨版本重新估计, 检验主结论是否对文本窗口的选取敏感。若 full 轨与 ctx 轨估计结果方向一致、幅度相近, 则可增强"洗稿现象是银行相关内容本身驱动"而非"全文噪声驱动"的解释力; 若两者出现系统性偏离, 则提示全文轨的象征性判断可能受到无关段落干扰, 需要在论文中并列报告两轨结果而非仅取其一。

## VAR: washing_ratio_hc_ss

【变体差分】
washing_ratio_hc_ss 是三轨架构中的 ss (same-sentence, 银行与金科词同句共现) 轨版本, 对应 runner.py 步骤 7h 中 `track='_ss'`(变量名后缀 `_ss`, `_sfx='_ss'`)。所用文本是 `content_ss`(标题+银行与金科词同句 ±N 窗口文本, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1; 与 stage 13 硬过滤用的 `cooccurrence_filter.sentence_radius` 是两个不同配置键), 分子分母同样基于 ss 轨自身的情感投票 (`pos_count_ss`)、象征性分类 (`innovation_substantiveness_ss`)、一致性 (`llm_agreement_rate_ss`) 独立计算。ss 轨采用镜像 ctx 轨的回退语义: 若一篇文章不存在银行与金科词的同句共现, 则 `content_ss` 退化为全文 body (与 `content_full` 相同来源), 并置位 `ss_is_fallback=True`; 若 `FINTECH_AC` 词典未加载 (None), 则该轨全部文章的 `*_is_fallback` 置 True, 优雅降级为等同 full 轨的输入。因此 washing_ratio_hc_ss 是三轨中语境窗口最窄、判定口径最严格的一支 (要求银行与金科词严格同句邻近, 而非仅实体窗口共现), 与 washing_ratio_hc / washing_ratio_hc_ctx 互为稳健性并排, 不分主次, 各自 just-identified, 禁止混入同一 over-identified Hansen J。行宇宙同样继承 full 轨留篇门控 (`llm_verified_full==True`) 决定的子集, 分子分母在 ss 轨内部独立闭合计算。由于同句共现条件比实体窗口更严苛, 在很多文章中不存在银行与金科词的严格同句邻近关系, 此时该文章的 `content_ss` 回退为全文 body、`ss_is_fallback=True`, 与 washing_ratio_hc(full 轨)在该文章上的输入趋同; 因此 washing_ratio_hc_ss 的信息增量主要来自那些确实存在银行-金科同句共现的文章子集, 在这部分文章上, 该列度量的是"银行与金科业务紧密关联语境下"的洗稿倾向, 是三轨中语境最纯净、噪声最低但样本覆盖面也最窄的一支。与 ctx 轨类似, 该列不单独作为主结论依据, 而是与 full/ctx 两轨并列报告, 用于判断洗稿现象在"银行-金科强关联语境"下是否依然成立, 从而排除"结论仅由宽泛语境下的弱关联样本驱动"的解释。

<!-- rendered-citations:begin -->
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, Article 109684. https://doi.org/10.1016/j.frl.2026.109684
<!-- rendered-citations:end -->
