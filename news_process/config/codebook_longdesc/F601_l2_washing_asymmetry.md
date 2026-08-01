---
family_id: F601
columns:
- washing_asymmetry_ctx
- washing_asymmetry_full
- washing_asymmetry_ss
unit: 无量纲得分, 取值范围理论上界为 (-1, 1) 区间内的实数差分
formula: washing_asymmetry{track} = neg_sub_ratio{track} - (1 - washing_ratio{track}); 其中 washing_ratio{track} = pos_symb_count{track} / pos_substvalid_count{track} (方法 A, LLM 投票口径), neg_sub_ratio{track} = neg_sub_count{track} / neg_substvalid_count{track} (方法 B, 反向验证口径), substvalid 分母为 _svd_denom 的稳健兜底分母
producer: pipeline\panel\runner.py (核心计算, 方法 B 区块「非对称性」) ; pipeline\panel\export.py (变量标签注册与 Stata 导出)
upstream:
- washing_ratio
- neg_sub_ratio
citations:
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: Ownership concentration and corporate greenwashing in China's capital markets - Based on a multi-actors perspective
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: '102600'
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: 'Sustainability or greenwashing: Evidence from the asset market for industrial pollution'
  venue: The Journal of Finance
  vol: '80'
  issue: '2'
  pages_or_artno: 699-754
- doi: 10.48550/arXiv.2502.07541
  type: arxiv
  authors: Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M.
  year: 2025
  title: 'Detecting greenwashing: A natural language processing literature survey'
  venue: arXiv
- doi: "10.1016/j.iref.2026.105256"
  type: "journal"
  authors: "Huang, Y., Zhang, Y., Li, Y., Ma, S., & Hao, C."
  year: 2026
  title: "Different effect of positivity and negativity: ESG media sentiment and corporate energy consumption intensity"
  venue: "International Review of Economics & Finance"
  vol: "108"
  pages_or_artno: "105256"
- doi: "10.24136/oc.4220"
  type: "journal"
  authors: "Long, H., & Hao, Y."
  year: 2026
  title: "AI talk–action gaps and ESG rating sensitivity: Evidence from Chinese A-share firms"
  venue: "Oeconomia Copernicana"
  vol: "17"
  issue: "2"
  pages_or_artno: "457-513"
new_dois: []
---

## CORE

【构念与来源】
washing_asymmetry 家族衡量的是银行金融科技相关报道中"洗白"(washing) 行为在正面与负面报道两端表现出的不对称性。其构念根基来自组织理论对"象征性行动"(symbolic action) 与"实质性行动"(substantive action) 的经典区分 (Weaver, Trevino & Cochran 1999 的企业社会责任象征-实质二分, W&Z 1998 的符号管理理论), 并在本仓库的洗稿/洗绿测度传统中具体化为对新闻报道内容与银行金融科技实际行动之间落差的量化。管道对每篇文章的情感极性 (正面/负面) 与内容属性 (实质性/象征性) 做联合分类, 由此可以计算"正面报道中有多大比例只是象征性的空话"(washing_ratio, 见方法 A) 以及"负面报道中有多大比例是实质性批评"(neg_sub_ratio, 见方法 B)。washing_asymmetry 正是把这两个互补但方向相反的比率合并成单一非对称性指标: 若正面报道被大量象征性内容主导 (washing_ratio 高, 即 1-washing_ratio 低) 而负面报道却以扎实的实质性批评为主 (neg_sub_ratio 高), 则该指标取正且数值增大, 反映银行在对外传播上呈现"报喜的空、报忧的实"的系统性偏斜——这正是洗白/漂绿实证文献里反复强调的"选择性披露"(selective disclosure) 或"印象管理"(impression management) 不对称模式的量化落地。反之若两端趋同, 指标趋近零, 说明正负面报道在实质性程度上大体对称, 不存在系统性的洗白倾向。
构念定位上, washing_asymmetry 不是对洗白程度的绝对水平测度 (那是 washing_ratio 的职责), 而是一个二阶差分测度: 它把"正面端的虚化程度"与"负面端的实化程度"放在同一把尺子上相减, 捕捉的是两端偏离对称基线的联合效应, 因而比单看 washing_ratio 或单看 neg_sub_ratio 任何一个更能反映媒体呈现结构性偏斜的整体形态。这一设计呼应了银行漂绿/漂科技(fintech-washing) 文献中对"言行不一"的操作化诉求: 银行既可能夸大金融科技投入的正面叙事 (象征性居多), 也可能在负面报道被曝光时被迫承认具体问题 (实质性居多), 二者叠加即构成传播策略上的选择性不对称。

【方法学与计算】
washing_asymmetry{track} 的计算严格遵循 pipeline\panel\runner.py 中标注为"方法 B: 反向验证"的代码区块, 是在方法 A (washing_ratio, LLM 投票口径) 与方法 B (neg_sub_ratio, 负面实质性口径) 均已成功计算的前提下派生的三阶指标: washing_asymmetry{track} = neg_sub_ratio{track} - (1 - washing_ratio{track})。展开来看, washing_ratio{track} = pos_symb_count{track} / pos_substvalid_count{track} 度量的是"正面报道中被判定为象征性的比例"(方法 A, LLM 三家投票多数决口径, 分母经 _safe_ratio 与 _svd_denom 双重稳健化——分母为零或过小时优雅退化为缺失而非除零崩溃); (1 - washing_ratio{track}) 因而表示"正面报道中实质性内容的比例", 是正面端的实质性水平。neg_sub_ratio{track} = neg_sub_count{track} / neg_substvalid_count{track} 度量的是"负面报道中被判定为实质性的比例", 是负面端的实质性水平, 计算方式与正面端结构对称但分子分母均取自负面报道子样本。两者相减即得到"负面端实质性水平 - 正面端实质性水平"的差分: 若为正, 说明负面报道比正面报道更"实"; 若为负, 说明正面报道反而比负面报道更实 (即负面报道也偏象征化, 罕见但理论上可能, 例如负面事件被大量空洞谴责性报道覆盖而缺乏实质细节)。该指标的分子分母均建立在 stage 21 三家 LLM (gpt54nano/gemini31/deepseekv4) 多数投票产出的情感极性与文本类型联合分类之上, 属于纯粹的面板层 (panel-level) 派生列, 不额外调用 LLM 或嵌入 API, 计算成本为 $0——它是 stage 21 情感分类结果在 pipeline\panel\runner.py 聚合阶段的算术再组合。
本 F601 家族的三个成员列 washing_asymmetry_full / washing_asymmetry_ctx / washing_asymmetry_ss 对应文本三轨 (full=标题+正文全文, ctx=标题+银行∧金科实体窗口, ss=标题+银行∧金科同句±N窗口, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)。三轨遵循本仓库统一的三轨架构铁律: 各自 just-identified 并排、互为稳健性、不分主次, 严禁将三轨列混入同一 over-identified Hansen J 检验框架。ss 轨的回退语义镜像 ctx 轨: 当某篇文章内不存在银行与金融科技实体的同句共现时, content_ss 退化为全文 body (与 content_full 相同), 并置位 ss_is_fallback=True, 此时该文章在 ss 轨上的情感/类型分类实质上复用了全文口径, 三轨分母 n_articles 在此情形下共享同一集合而非各自独立采样。留篇门控口径遵循 2026-06-29 起生效的 full-only 铁律: 一篇文章是否被计入"银行金融科技报道"的分母, 只取决于 llm_verified_full == True, ctx/ss 两轨在此意义上是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 三轨各自的分子分母仍按各自轨道逐轨计算 (即 washing_asymmetry_ctx 的 neg_sub_count_ctx / neg_substvalid_count_ctx 等分子分母全部取 _ctx 后缀列, 不借用 full 轨的中间量), 因而三轨数值一般不相等, 差异本身即反映了文本窗口收窄后洗白判定的稳健性区间。

【文献定位】
washing_asymmetry 家族在测度设计上直接承袭了近年漂绿/洗白 (greenwashing/washing) 实证文献对"言行不一致"的量化范式。Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 提出的 "AI washing" 概念——企业在人工智能相关信息披露上进行策略性夸大并招致市场反噬——为本家族"报道内容虚实不对称"的构念提供了直接的当代锚点: 银行在金融科技领域的媒体呈现同样存在"技术标签滥用"与"实质投入不足"之间的落差, washing_asymmetry 正是把这种落差从定性观察转为可面板回归的连续变量。Fan, Tang, Huang & Yang (2025, Pacific-Basin Finance Journal) 基于多主体视角研究中国资本市场的企业漂绿行为与股权集中度的关系, 其研究设计中对"漂绿严重程度"的操作化同样依赖披露文本与实际行动的对比, 与本家族方法 A (washing_ratio) 和方法 B (neg_sub_ratio) 联合构造非对称性指标的思路高度一致, 也印证了在中国制度背景下用文本挖掘识别策略性披露具有可行性。Gorovaia & Makrominas (2024, European Financial Management) 使用自然语言处理方法从企业社会责任报告中识别漂绿信号, 其方法学路径 (对报告文本做情感与实质性的联合标注, 再构造比率型指标) 与本仓库 washing_ratio 及其非对称性衍生指标的构造逻辑同源, 是本家族方法学定位的重要参照。Duchin, Gao & Xu (2025, *The Journal of Finance*) 通过工业污染资产市场的交易数据识别可持续性叙事与漂绿行为的真伪, 提供了顶刊层级对"企业对外叙事与实质行为存在系统性落差"这一现象的实证确认, 为本家族的核心构念假设 (媒体报道的正负面呈现存在结构性不对称) 提供了跨行业、跨市场的外部效度支撑。此外, Calamai, Balalau, Le Guenedal & Suchanek (2025, arXiv 综述) 系统梳理了漂绿检测的自然语言处理文献, 指出情感极性与内容实质性的联合建模是当前主流路径之一, 与本仓库 stage 21 三家 LLM 联合分类情感与文本类型 (实质性 vs 象征性) 的设计思路相符, 佐证了本家族方法学选择处于该领域的技术前沿而非孤立设计。washing_asymmetry 家族的三轨扩展 (full/ctx/ss) 亦呼应了上述文献共同关切的"叙述窗口大小影响信号提取"这一一般性问题: Duchin, Gao & Xu (2025) 与 Calamai et al. (2025) 的方法学讨论均隐含了信息颗粒度的选择会系统性影响不对称性测度稳健性这一判断, 本仓库将这一关切具体化为三个并排的文本窗口轨道 (full/ctx/ss), 而非单一窗口下的单点估计, 三轨互为稳健性并排、禁止混入同一 over-identified Hansen J 检验框架。 两条更晚近的实证分别从极性侧与构造侧加固了本家族的设计。Huang、Zhang、Li、Ma 与 Hao (2026) 实证表明媒体 ESG 情感的正面侧与负面侧对企业实质行为的影响在方向与幅度上并不对称, 为本家族把「正面—象征」通道 (方法 A, washing_ratio) 与「负面—实质」通道 (方法 B, neg_sub_ratio) 分开构造再作差提供了媒体情感极性不对称的当代实证依据; 迁移边界须诚实写明: 该文的不对称体现在正/负媒体情感对 DV (能耗强度) 回归系数的差异, 属效应侧不对称, 而 washing_asymmetry 是在测量侧把两个比率直接相减构成单一指标, 二者不是同一数学对象, 且原文主体为非金融企业、议题为 ESG/能耗, 未涉及象征—实质判定。Long 与 Hao (2026) 对中国 A 股企业构造 AI 的 talk–action gap (言论强度与实际行动之差) 并检验其与 ESG 评级敏感性的关系, 其 gap 的差分式构造与本家族的减法式属同一类「叙事—行动背离」量化, 是该测度族在中国技术话语情境下的前沿存在性证明; 但原文 talk 侧来自年报文本 AI 词频、action 侧来自企业实际投入与专利, 观测单位为公司-年且技术域为 AI、DV 为 ESG 评级敏感性, 本家族 talk/action 两侧则同源于新闻报道内部的 LLM 象征—实质判定 (无外部行动侧数据), 单位为银行-年、技术域为金融科技, 故本轮仅取其构造范式的存在性而不迁移其识别设计。
## VAR: washing_asymmetry_ctx

【变体差分】
本列是 washing_asymmetry 家族在 ctx 轨 (标题 + 银行∧金科实体窗口文本) 上的实现, 后缀 `_ctx` 对应 pipeline\panel\runner.py 循环变量 `track='_ctx'` 分支。计算公式与家族 canonical 完全一致 (washing_asymmetry_ctx = neg_sub_ratio_ctx - (1 - washing_ratio_ctx)), 差异仅在于所有中间分子分母列 (neg_sub_count_ctx, neg_substvalid_count_ctx, pos_symb_count_ctx, pos_substvalid_count_ctx) 均来自 ctx 轨的 LLM 分类结果, 而 ctx 轨的输入文本是 stage 14 `ctx_materializer` 物化的 content_ctx (标题前置 + 实体窗口截取), 相较 full 轨大幅收窄了上下文范围, 只保留银行与金融科技实体附近的局部语境。这意味着 washing_asymmetry_ctx 反映的是"聚焦实体局部语境时"观测到的报道虚实不对称, 更贴近具体事件层面的措辞倾向, 但也因窗口收窄而对情感分类的边界样本更敏感 (窗口越小, 上下文线索越少, LLM 分类噪声占比可能相对上升)。留篇门控仍为 full-only: 本列的样本宇宙是 llm_verified_full==True 的文章子集在 ctx 轨上的再分类结果, 而非 ctx 轨独立留篇。ctx 轨与 full/ss 两轨互为稳健性并排比较, 不设置优先级, 三者在回归设计中不得同时作为同一 over-identified 工具变量集合的正交工具使用。从解释角度看, ctx 轨适合用来剥离与银行金融科技主题无关的段落噪声: 一篇长文如果只有个别句子涉及金融科技, 全文轨 (full) 会把大量无关内容也纳入情感与实质性判断, 而 ctx 轨通过实体窗口截取, 让分类器更聚焦于真正相关的措辞, 因而 washing_asymmetry_ctx 通常被视为对"报道虚实不对称"更精细但样本方差可能更大的估计。使用者在解读该列时应留意: 当某家银行在某年度报道量较小时, ctx 轨的窗口截取可能进一步压缩有效文本长度, 使得该年度该银行的分类结果对个别关键词更敏感, 建议结合 full 轨与 ss 轨联合展示以判断结论的稳健性, 而非仅凭 ctx 轨单独下结论。

## VAR: washing_asymmetry_full

【变体差分】
本列是 washing_asymmetry 家族的 full 轨实现, 对应 pipeline\panel\runner.py 循环 `for track in ['_full', '_ctx', '_ss']` 中 track=='_full' 的分支。需注意本家族列名构造与同一循环内的 washing_ratio 不同: washing_ratio 用派生变量 `_sfx = '' if track == '_full' else track` 命名 (故 full 轨的 washing_ratio 列名不带后缀, 直接写作 washing_ratio), 而 washing_asymmetry 的变量名固定用 `f'washing_asymmetry{track}'` (即始终直接拼接 track 本身, 不经 `_sfx` 折叠), 因此三轨的 washing_asymmetry 列名均带后缀, full 轨即为 washing_asymmetry_full, 与 ctx/ss 两轨在命名规则上完全对称、无特殊简写。full 轨消费 stage 00 原始"内容"列拼接标题后的全文文本 (content_full = prepend_title 全文), 不做任何实体窗口截取或同句限定, 因而覆盖的上下文信息量在三轨中最完整, 是三轨中样本覆盖率最高、对局部措辞噪声最不敏感的一支, 也是留篇门控 (llm_verified_full) 直接锚定的轨道——即 full 轨本身就是决定一篇文章是否进入"银行金融科技报道"分母的判据来源, 其余两轨是在 full 轨留篇集合基础上的条件测度。washing_asymmetry_full 因此在三个并排轨道中承担事实上的默认参照角色 (但不构成构念上的"主轨"优先级, 三轨仍是互为稳健性、禁止混入同一 Hansen J 的并排关系), 其分子分母 (neg_sub_count_full 等) 与 ctx/ss 两轨对应列在计算公式结构上完全对称, 唯一差异是输入文本窗口大小。由于 full 轨覆盖全文, 它天然包含了更多与银行金融科技主题弱相关甚至无关的段落, 这些段落同样会被 stage 21 三家 LLM 联合判断情感极性与文本类型 (实质性/象征性), 因而 washing_asymmetry_full 的分类结果可以理解为"整篇报道的总体虚实基调", 而非局限于具体涉及银行与金融科技的语句本身。这一特点使得 full 轨在跨年度、跨银行比较时具有更好的样本覆盖率与更低的窗口截取噪声, 但也可能因引入无关段落而稀释局部信号强度。使用者在实证分析中若关心整体媒体传播基调的虚实不对称, 应优先参考 full 轨; 若关心具体事件语境下的措辞倾向, 则应结合 ctx 或 ss 轨联合解读, 三轨并排展示是本仓库推荐的稳健性呈现方式。

## VAR: washing_asymmetry_ss

【变体差分】
本列是 washing_asymmetry 家族在 ss 轨 (标题 + 银行∧金科同句共现窗口, ±N 句, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认为 1) 上的实现, 是三轨中文本窗口最窄、判定条件最严格的一支: 只有当银行实体与金融科技词汇在同一句 (或半径 N 内的邻近句) 共同出现时, 才纳入该句局部文本参与情感与文本类型分类。当某篇文章不满足银行∧金科同句共现条件时, ss 轨遵循镜像 ctx 轨的回退语义: content_ss 退化为等同于 content_full 的全文 body, 并置位 ss_is_fallback=True, 该文章在此情形下的 neg_sub_count_ss / pos_symb_count_ss 等中间量实质上复用了全文口径下的分类结果, 三轨共享同一 n_articles 分母而非独立采样计数。washing_asymmetry_ss 因而在语义上是"最贴近具体共现语句"的洗白非对称性测度, 相比 ctx 轨窗口更窄、判据更严, 对同句共现稀疏的样本 (如 dev 环境早期试跑 T=2 小样本) 可能出现较高比例的回退, 此时其数值会趋近于 washing_asymmetry_full 而非独立信号。ss 轨与 full/ctx 两轨同样互为稳健性并排, 三者禁止混入同一 over-identified Hansen J 检验; 生产语料 (T=19, 全量 约 1,819 万条报道) 下同句共现样本量显著大于本机 dev 环境, ss 轨的独立信号强度预期在生产规模下更充分显现。使用者在解读 washing_asymmetry_ss 时应特别留意回退比例这一元信息: 若某银行-年度单元的 ss_is_fallback 比例过高, 意味着该单元的 washing_asymmetry_ss 数值实质上是 full 轨的复制, 不应被误读为"同句层面独立验证了非对称性结论"。建议在稳健性表格中同时报告各单元的回退占比, 以便读者判断 ss 轨结果的信息增量。相较 ctx 轨的实体窗口截取 (允许实体与相关词汇跨句邻近), ss 轨的同句判据更为苛刻, 因而在概念上更贴近"逐句核查报道措辞是否与银行金融科技话题直接相关"的严格标准, 是三轨中对文本噪声最不敏感、但对样本稀疏性最敏感的一支, 与 full/ctx 两轨共同构成从宽松到严格的窗口谱系, 供研究者按不同稳健性需求择用而非相互替代。

<!-- rendered-citations:begin -->
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets - Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance, 80(2), 699-754. https://doi.org/10.1111/jofi.13412
Calamai, T., Balalau, O., Le Guenedal, T., & Suchanek, F. M. (2025). Detecting greenwashing: A natural language processing literature survey. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.07541
Huang, Y., Zhang, Y., Li, Y., Ma, S., & Hao, C. (2026). Different effect of positivity and negativity: ESG media sentiment and corporate energy consumption intensity. International Review of Economics & Finance, 108, 105256. https://doi.org/10.1016/j.iref.2026.105256
Long, H., & Hao, Y. (2026). AI talk–action gaps and ESG rating sensitivity: Evidence from Chinese A-share firms. Oeconomia Copernicana, 17(2), 457-513. https://doi.org/10.24136/oc.4220
<!-- rendered-citations:end -->
