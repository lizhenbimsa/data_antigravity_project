---
family_id: F430
columns:
- lpeer_attention_iv_ctx
- lpeer_attention_iv_ctx_lag1
- lpeer_attention_iv_ss
- lpeer_attention_iv_ss_lag1
unit: 工具变量 (与被工具化内生变量 attention_index_ctx / attention_index_ss 同量纲, 0–1 区间连续值)
formula: '同类型 (same bank_type) 同业留一法 (leave-one-out, LOO) 均值: 对银行 i 在年份 t, 取同 bank_type 分组内除 i 自身外全部银行同轨注意力指数的算术平均, ctx 轨以 attention_index_ctx 为输入、ss 轨以 attention_index_ss 为输入; _lag1 后缀 = 该 LOO 序列按银行 id 整体滞后一期 (t-1), 用于面板年度 FE 下弱化同期反向因果'
producer: pipeline\panel\iv_extensions.py::compute_iv_extensions ; pipeline\panel\stata_export.py::HEURISTIC_LABELS
upstream:
- attention_index_ctx
- attention_index_ss
- bank_type
citations:
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-Level Political Risk: Measurement and Effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.2307/2298123
  type: journal
  authors: Manski, C. F.
  year: 1993
  title: 'Identification of Endogenous Social Effects: The Reflection Problem'
  venue: The Review of Economic Studies
  vol: '60'
  issue: '3'
  pages_or_artno: 531-542
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: 'Bartik Instruments: What, When, Why, and How'
  venue: American Economic Review
  vol: '110'
  issue: '8'
  pages_or_artno: 2586-2624
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as Data
  venue: Journal of Economic Literature
  vol: '57'
  issue: '3'
  pages_or_artno: 535-574
- doi: 10.1017/CBO9780511614491.006
  type: book
  authors: Stock, J. H., & Yogo, M.
  year: 2005
  title: Testing for Weak Instruments in Linear IV Regression
  venue: 'Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (Cambridge University Press)'
  pages_or_artno: 80-108
- doi: 10.1016/j.jeconom.2008.12.021
  type: journal
  authors: Bramoullé, Y., Djebbari, H., & Fortin, B.
  year: 2009
  title: Identification of Peer Effects through Social Networks
  venue: Journal of Econometrics
  vol: '150'
  issue: '1'
  pages_or_artno: 41-55
- doi: "10.3390/systems13100918"
  type: journal
  authors: "He, L., Zhu, S., Zhang, M., & Dong, X."
  year: 2025
  title: "Peer Effects of Bank Digital Transformation Through Shareholder Networks"
  venue: "Systems"
- doi: "10.1080/00036846.2025.2515298"
  type: journal
  authors: "Ren, Q., Chen, Z., Tourani-Rad, A., Xiong, H., & Xu, Y."
  year: 2025
  title: "Peer effects in cross-regional investment: evidence from China"
  venue: "Applied Economics"
new_dois:
  - "10.3390/systems13100918"
  - "10.1080/00036846.2025.2515298"
---

## CORE

【构念与来源】
本家族 F430 (lpeer_attention_iv, l2 层级) 收录 P2 (bank_fintech_attention 论文) 注意力指数在 ctx/ss 两条稳健轨上的同业留一法 (leave-one-out, LOO) 工具变量及其滞后派生, 共 4 列、全部 standard tier。产出编排入口为 `pipeline/panel/iv_extensions.py::compute_iv_extensions` (runner 步骤 8z, 由 `config/panel.yaml::compute_iv_extensions` 开关控制), 面板标签写入由 `pipeline/panel/stata_export.py::HEURISTIC_LABELS` 承担。命名前缀 `lpeer_` (leave-one-out peer 的紧凑写法) 是 2026-06-13 起对 P2 full 轨既有 `leave_one_out_peer_attention_iv(_lag1)` 的 ctx/ss 轨镜像补全: ctx 轨于 2026-06-13 四 agent 对抗评审后落地, ss 轨于 2026-06-14 随三轨平价补全跟进, 二者与 full 轨 IV 三足并列, 是同一识别策略在三种文本剪裁窗口上的复刻, 而非三种不同的构念。前缀刻意压缩为 `lpeer_` 而非 `leave_one_out_peer_`, 是为了让 `_ss_lag1` (26 字符) 与 `_ctx_lag1` (27 字符) 都不超过 Stata 变量名 32 字符上限, 绕开 `stata_export` 32-char 截断导致的列名歧义, 也让各 2SLS 模板可以直接引用而不必再做名义映射。
本家族的经济学动机是社会互动/同侪效应识别里的经典"反射问题" (reflection problem, Manski 1993): 银行 i 自身受媒体关注的程度 (attention_index) 很可能是内生的——它既反映银行自身的金融科技活动强度 (真实需求), 也反映媒体资源分配、银行公关策略等未观测的混杂因素, 直接把 attention_index 放进结果方程的右侧会产生联立性偏误。lpeer_attention_iv 系列采用"同类型同侪均值"作为工具: 对银行 i 在年份 t, 在同一 `bank_type` 分组 (如国有大行/股份制/城商行/农商行等监管口径分类) 内, 计算除 i 本身之外全部同组银行同一轨道注意力指数的算术平均。直觉是——同类型银行面临相似的行业性媒体环境冲击、监管周期与舆论热度 (行业层面的共同驱动力), 但同侪银行的个体特质性冲击 (idiosyncratic shock) 与银行 i 自身的特质性冲击相互独立, 因此同侪均值捕捉了行业层面的共同变异、又不直接包含银行 i 自身可能导致联立性偏误的私有信息, 满足排他性约束的合理性论证与 Bartik/shift-share 文献中"其他单位的结果均值作工具"的谱系一致 (亦与网络文献中同侪效应工具的构造思路同源, Manski 1993; Bramoullé, Djebbari & Fortin 2009 一脉相承的留一法逻辑)。
在被工具化的内生变量选择上, ctx 轨工具化 `attention_index_ctx` (标题+实体窗口口径下的注意力指数), ss 轨工具化 `attention_index_ss` (标题+银行∧金科同句窗口口径下的注意力指数), 与 P2 论文 full 轨既有的 `leave_one_out_peer_attention_iv` 工具化 `attention_index`(full) 三者一一对应、并列存在, 而非互相替代。

【方法学与计算】
计算流程严格分两步: 第一步在原始面板 (未展开的银行-年份行) 上按 `bank_type × year` 分组, 对组内全部银行的同轨 attention_index 求和与计数; 第二步对每个银行 i, 用"组总和减去 i 自身值"再除以"组计数减一"得到留一法均值, 这样每家银行看到的工具值都天然排除了自身贡献, 避免了工具变量构造中常见的"自身混入自身工具"的机械性内生偏误。`_lag1` 变体在此基础上再做一次按银行 id 分组的整体滞后一期操作, 把 t 期算出的 LOO 均值搬到 t+1 期使用, 目的是在年度固定效应吸收同期共同冲击之后, 进一步用上一期的同侪状态弱化"当期反向因果"的担忧 (被工具化的内生变量若与工具同期测量, 无法排除结果方程误差项与工具在当期存在共同驱动的可能, 用滞后期切断这条同期反馈路径)。分母口径注意: 源码 `compute_peer_loo_iv` (`min_peers=2` 守卫) 实际生效的置缺失判据比"组内计数为 1 时除零"更严格——只要银行 i 所属 `bank_type` 分组在该年除 i 自身外的有效剩余同业数 (remain_cnt) 小于 2 (即含"组内仅 i 一家自身、剩余为 0"与"组内共 2 家含 i 自身、剩余仅 1 家同业"两种情形), 该行工具值即按设计置为缺失 (NaN), 而非仅在严格除零 (剩余为 0) 时才置缺失; 之所以把下限定在 2 而非 1, 是因为仅 1 个同业构成的"均值"退化为该单一同业的个体观测值, 无法体现"行业层面共同变异"的工具构造初衷、且极易被该唯一同业的特质性冲击污染, 故一并置缺失。这一 NaN 既非除零报错也非人为填补, 下游 2SLS 回归会自然按列表式删除 (listwise deletion) 处理这类观测, 不做隐性外推。
本家族与家族级铁律的关系 (对照 CLAUDE.md「三轨」条款): ctx 轨与 ss 轨的工具变量各自 just-identified、与其对应的同轨内生变量各自并排配对 (ctx 工具配 ctx 内生, ss 工具配 ss 内生), 三轨 (连同 full 轨既有工具) 互为稳健性、不分主次, 严禁把 full/ctx/ss 三轨任意两轨的 LOO 工具混进同一个 over-identified 的 Hansen J 统计量联合检验。原因是三轨源自对同一篇文章的三种不同文本剪裁窗口 (full=标题+全文正文; ctx=标题+围绕目标实体的窗口; ss=标题+银行∧金科同句窗口, 无同句共现时回退全文、镜像 ctx 的回退语义), 同一 `bank_type × year` 的行业性共同冲击会以几乎相同的方式逐字污染三条轨道, 使得三轨工具彼此高度共线, 此时把它们当作独立的额外工具塞进 over-id 检验既无法为真实的排他性威胁提供有效功效, 又会拖累第一阶段 Kleibergen-Paap rk Wald F 统计量、诱发弱工具误判——这一"高度共线工具不应混入同一过度识别检验"的逻辑, 与 Bramoullé, Djebbari & Fortin (2009) 对社会网络同侪效应工具排他性条件的刻画一脉相承 (该文指出, 若候选工具彼此共享相同的网络结构性来源, 联合使用并不能提供额外的识别信息、反而会放大弱工具问题)。若要做真正的过度识别检验, 应使用跨"识别策略族"的工具组合 (如同一轨内 LOO 工具与 Bartik 型工具的组合, 或 LOO 工具与 zone-LOO 工具的组合), 这类组合已经内建在各论文既有的 2SLS 模板 overid 列中, 本家族列不再重复该功能。
留篇门控口径: attention_index 系列 (及本家族工具化的 ctx/ss 变体) 的样本行是否计入"一篇银行金科报道", 遵循 2026-06-29 起确立的 full-only 留篇门控——即行宇宙由 `llm_verified_full == True` 决定, ctx/ss 轨的样本集合是 full 留篇集的子集, 各轨在此子集之上分别计算自身的 per-track 测度 (含本家族的 LOO 均值), 不存在 ctx/ss 各自独立扩样的情况。ss 轨回退语义严格镜像 ctx: 若某银行-文章对不存在"目标银行与金科词同句 (±N 句窗) 共现", `content_ss` 回退为全文 body、`ss_is_fallback` 置 True, 该行 attention_index_ss 仍按全文口径参与计算并共享 `n_articles` 分母, 因此本家族 ss 轨工具值的样本基础与 ctx 轨在存在同句共现的子样本上重合, 在无共现样本上退化为 full 口径, 这是设计使然而非缺陷。

【文献定位】
本家族的方法论谱系首先落在 Hassan, Hollander, van Lent & Tahoun (2019, QJE)"公司层面政治风险测度"一文开创的文本暴露度量与工具化框架: 该文示范了如何用同侪公司 (peer firm) 的暴露度均值作为焦点公司自身暴露度的工具, 以缓解文本测度中公司自身特质性因素导致的联立性偏误, 本家族的 bank_type 同侪留一法与该文的识别逻辑直接呼应。识别策略的理论基础追溯到 Manski (1993, Review of Economic Studies)"反射问题"经典文献, 该文首次系统刻画了同侪效应估计中内生同侪选择与共同环境冲击难以区分的识别困境, 是本家族"为何要工具化注意力指数"这一动机的理论出处。留一法工具的构造与近年 Bartik/shift-share 工具变量方法论文献一脉相承, Goldsmith-Pinkham, Sorkin & Swift (2020, American Economic Review)"Bartik 工具: 是什么、何时用、为何用、如何用"一文系统阐述了此类"用其余单位的结果或特征构造工具"的识别条件与诊断做法, 为本家族工具的排他性论证提供方法论支撑; Stock & Yogo (2005) 关于线性 IV 回归弱工具检验的经典判据是下游 2SLS 模板评估本家族工具强度 (第一阶段 F 统计量) 时的标准参照。构念侧的"注意力"测度本身则承接媒体覆盖度与市场关注度的经典文献谱系 (如 Fang & Peress 2009 关于媒体覆盖度与股票截面收益关系的研究, 以及更广义的"文本作为数据"方法论综述 Gentzkow, Kelly & Taddy 2019), 本家族只负责该测度的工具化环节, 不重复定义注意力本身的构念 (注意力指数构念定位见 attention_index / attention_index_ctx / attention_index_ss 所在家族)。近期银行业同侪效应 IV 文献亦为本家族识别策略提供了同期方法学同伴: He, Zhu, Zhang & Dong (2025, Systems) 用股东网络同侪构造工具变量识别银行数字化转型的同侪效应, 与本家族用 bank_type 同业留一法工具化注意力指数的识别思路同属银行业同侪效应 IV 谱系; Ren, Chen, Tourani-Rad, Xiong & Xu (2025, Applied Economics) 在中国上市公司样本中用同侪留一法均值构造工具变量识别跨区域投资中的同侪效应, 为本家族 bank_type 分组留一法 IV 的排他性论证提供了近期中国情境下的方法学同侪。

## VAR: lpeer_attention_iv_ctx

【变体差分】
本列是 lpeer_attention_iv 家族的 ctx 轨、无滞后原始版本, 工具化的内生变量是 `attention_index_ctx` (标题+实体窗口口径的注意力指数, ctx = 标题 prepend 后围绕目标银行/金科实体截取的窗口文本, 实体窗口谱系承接 Hassan 2019 QJE 的 firm-level exposure 计量思路), 分组变量是 `bank_type`, 时间维度是年份 t 与被工具化变量同期 (未滞后)。数值等于银行 i 所属 bank_type 分组内 (排除 i 自身) 该年份全部银行 attention_index_ctx 的算术平均; 分组内仅 i 一家时置缺失、不做人为填补或跨组借用。该列与 full 轨既有的 `leave_one_out_peer_attention_iv` 在计算逻辑上完全平行, 唯一差异是被工具化的内生变量文本口径不同 (ctx 窗口而非标题+全文正文), 二者应各自 just-identified 使用、不得混入同一 Hansen J 联合过度识别检验。该列与本家族 `lpeer_attention_iv_ss` 的差异同样只在文本口径 (ctx 实体窗口 vs ss 银行∧金科同句窗口), 二者互为稳健性并排, 不存在孰优孰劣的先验排序——ctx 轨的实体窗口通常覆盖更宽的上下文, 对"话题相关但未必银行金科同句提及"的报道更宽容, 因而样本量与信息量相对 ss 轨更充分, 但排他性论证相对 ss 轨稍弱; 与 `lpeer_attention_iv_ctx_lag1` 的差异仅在时间对齐——本列同期、后者滞后一期。留篇门控上, 本列所在样本行宇宙由 full 轨 `llm_verified_full == True` 决定, 本列作为 ctx 轨条件测度只在该留篇集合的子集上计算, 不单独扩样。

## VAR: lpeer_attention_iv_ctx_lag1

【变体差分】
本列是 `lpeer_attention_iv_ctx` 按银行 id 整体滞后一期 (t-1 期取值填入 t 期行) 的派生序列, 其余计算口径 (ctx 轨 attention_index_ctx 输入、bank_type 分组、留一法均值排他) 与同期版本完全一致, 唯一差异是时间对齐方式。滞后处理的动机是: 在面板固定效应模型中年度虚拟变量已经吸收了行业层面的同期共同冲击, 但若被工具化的内生变量与工具变量在同一期测量, 仍无法完全排除结果方程误差项与工具存在同期共同驱动的可能 (例如某一年全行业性的舆情事件同时影响银行 i 与其同侪银行, 且该事件本身也与结果变量相关), 用上一期的同侪状态作为工具可以进一步切断这条同期反馈路径, 是弱化"反向因果/同期性"担忧的常规稳健性做法而非替代同期版本的更优选择——两者应作为同一识别策略下的滞后结构敏感性并排报告, 而非二选一取代。首年样本 (面板起始年份, 无 t-1 观测) 该列按设计置为缺失, 下游 2SLS 回归对该行做列表式删除。与 `lpeer_attention_iv_ss_lag1` 相比, 本列同为滞后一期, 差异仅在文本裁剪口径 (ctx 实体窗口 vs ss 银行金科同句窗口), 二者应各自 just-identified 并排使用, 不可混入同一过度识别检验; 与本家族两个同期版本相比, 滞后版本对"反向因果"更稳健, 但代价是丢失面板首年观测, 属于典型的样本量-识别稳健性权衡, 建议同期与滞后两个版本都作为敏感性报告而非只取其一。

## VAR: lpeer_attention_iv_ss

【变体差分】
本列是 lpeer_attention_iv 家族的 ss 轨、无滞后原始版本, 工具化的内生变量是 `attention_index_ss` (标题+银行∧金科同句窗口口径的注意力指数)。计算逻辑 (bank_type 分组留一法均值、同期对齐、组内单银行置缺失) 与 `lpeer_attention_iv_ctx` 完全平行, 唯一差异是被工具化变量的文本裁剪判据更严格——ss 轨要求目标银行与金科词在同一句 (±N 句窗, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1) 内共现才计入紧邻窗口文本, 判据原语与 stage 13 硬过滤共现判据不同 (ss 严格同句 vs stage 13 ±1 句窗共现), 二者禁止互相复用。若某文章不存在这种同句共现则 `content_ss` 回退为全文、`ss_is_fallback` 置 True (镜像 ctx 轨的回退语义), 该行仍参与 attention_index_ss 及本列的计算并共享 `n_articles` 分母, 因此在无同句共现的样本子集上, 本列与 ctx 轨、乃至 full 轨工具的取值来源趋同 (均退化为全文口径), 只在存在同句共现的样本子集上才体现出 ss 轨"更紧邻文本窗口"的信息增量。本列与 `lpeer_attention_iv_ctx` 互为稳健性并排、禁止混入同一 Hansen J; 与 `lpeer_attention_iv_ss_lag1` 的差异仅在滞后结构 (本列同期、后者滞后一期)。与 full 轨既有 `leave_one_out_peer_attention_iv` 相比, 本列在识别策略上完全平行 (同一 bank_type 留一法均值), 差异仅在被工具化内生变量的文本裁剪窗口, 三轨应作为同一识别策略的并列稳健性报告, 不应彼此替代或合并检验。

## VAR: lpeer_attention_iv_ss_lag1

【变体差分】
本列是 `lpeer_attention_iv_ss` 按银行 id 整体滞后一期的派生序列, 输入的同侪均值序列基于 ss 轨 `attention_index_ss` (银行∧金科同句共现窗口, 无共现回退全文镜像 ctx), 滞后动机与 `lpeer_attention_iv_ctx_lag1` 相同——用上一期同侪状态弱化年度固定效应之外残余的同期反馈担忧, 而非替代同期版本的更优选择, 两者应作为同一识别策略下的滞后结构敏感性并排报告。该列变量名 `lpeer_attention_iv_ss_lag1` 长度 26 字符, 严格短于 ctx 轨对应列 `lpeer_attention_iv_ctx_lag1` 的 27 字符, 这一命名长度差是 `lpeer_` 紧凑前缀设计时的刻意结果, 用以确保全部 4 列变量名 (含最长的 ctx_lag1) 都不超过 Stata 32 字符变量名上限, 避免 `stata_export` 字节截断在 ctx/ss 两条孪生列之间产生歧义命名冲突。首年样本 (面板起始年份, 无 t-1 观测) 该列同样按设计置为缺失, 下游 2SLS 回归对该行做列表式删除; 计算口径其余部分 (bank_type 分组、留一法分母排他、组内单银行置缺失) 与家族内其余三列完全一致。与 `lpeer_attention_iv_ctx_lag1` 相比, 本列同为滞后一期, 差异仅在文本裁剪口径, 二者应各自 just-identified 并排使用、禁止混入同一 Hansen J 过度识别检验; 与本家族两个同期版本相比, 本列在弱化反向因果担忧的同时以样本量为代价, 建议同期与滞后版本互为稳健性敏感性报告而非二选一。

<!-- rendered-citations:begin -->
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
Manski, C. F. (1993). Identification of Endogenous Social Effects: The Reflection Problem. The Review of Economic Studies, 60(3), 531-542. https://doi.org/10.2307/2298123
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik Instruments: What, When, Why, and How. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as Data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Stock, J. H., & Yogo, M. (2005). Testing for Weak Instruments in Linear IV Regression. Identification and Inference for Econometric Models: Essays in Honor of Thomas Rothenberg (Cambridge University Press). https://doi.org/10.1017/CBO9780511614491.006
Bramoullé, Y., Djebbari, H., & Fortin, B. (2009). Identification of Peer Effects through Social Networks. Journal of Econometrics, 150(1), 41-55. https://doi.org/10.1016/j.jeconom.2008.12.021
He, L., Zhu, S., Zhang, M., & Dong, X. (2025). Peer Effects of Bank Digital Transformation Through Shareholder Networks. Systems. https://doi.org/10.3390/systems13100918
Ren, Q., Chen, Z., Tourani-Rad, A., Xiong, H., & Xu, Y. (2025). Peer effects in cross-regional investment: evidence from China. Applied Economics. https://doi.org/10.1080/00036846.2025.2515298
<!-- rendered-citations:end -->
</content>
