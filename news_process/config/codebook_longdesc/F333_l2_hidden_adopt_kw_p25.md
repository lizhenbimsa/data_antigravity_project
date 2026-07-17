---
family_id: F333
columns:
- hidden_adopt_kw_p25
- hidden_adopt_kw_p25_ctx
- hidden_adopt_kw_p25_ss
unit: 银行-年占比 (0-1 区间比例, 分母=该银行该年已双测量[词频+相似度均非缺失]的报道篇数)
formula: 'per-article 逐年 (year 内) 分位阈值分类: high_freq = fintech_distinct_keywords >= 该年该轨词频 P25 分位; high_sim = policy_cosine_sim >= 该年该轨相似度 P25 分位; hidden = (~high_freq) & high_sim (词频低于阈值 且 相似度不低于阈值), 仅对 sim/freq 双双非缺失的行分类, 其余记 NaN; 按 (target_bank, year) groupby mean 聚合为占比 (分母自动跳过 NaN)'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (per-article 分类); pipeline\panel\export.py (标签注册)
upstream: 15_fintech_intensity.parquet (fintech_distinct_keywords 词频元数据); 16_article_policy_alignment.parquet 或等价上游 (policy_cosine_sim 政策文本余弦相似度); 24_herd_decay.parquet (verified 域 semi-join 分母对齐)
citations:
- doi: "10.1017/S0022109023000662"
  type: journal
  authors: "Kwan, A., Lin, C., Pursiainen, V., & Tai, M."
  year: 2024
  title: "Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic"
  venue: "Journal of Financial and Quantitative Analysis"
  vol: "59"
  issue: "6"
  pages_or_artno: "2618-2646"
- doi: "10.1073/pnas.2203150119"
  type: journal
  authors: "Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al."
  year: 2022
  title: "Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "119"
  issue: "44"
  pages_or_artno: "e2203150119"
- doi: "10.1111/ecin.12992"
  type: journal
  authors: "Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al."
  year: 2021
  title: "The influence of hidden researcher decisions in applied microeconomics"
  venue: "Economic Inquiry"
  vol: "59"
  issue: "3"
  pages_or_artno: "944-960"
- doi: "10.1016/j.frl.2026.109668"
  type: "journal"
  authors: "Chen, M., Zhang, Z., & Liu, Y."
  year: 2026
  title: "Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China"
  venue: "Finance Research Letters"
  vol: "95"
  pages_or_artno: "109668"
- doi: "10.1016/j.pacfin.2024.102493"
  type: "journal"
  authors: "Liu, Y., Wang, J., Wen, F., & Wu, C."
  year: 2024
  title: "Corporate responses to systemic risk: Talk and action"
  venue: "Pacific-Basin Finance Journal"
  vol: "87"
  pages_or_artno: "102493"
new_dois: []
---

## CORE

【构念与来源】
hidden_adopt_kw_p25 家族衡量银行在某一年度里, 有多大比例的金融科技相关报道属于「隐性采纳」(hidden adoption) 象限: 报道中金融科技关键词出现频次偏低, 但报道文本与监管政策文本的语义相似度却不低。这个构念的直觉来自 Hassan et al. (2019) 开创的电话会议文本-政策文本余弦相似度识别策略, 以及企业创新经济学里对「策略性沉默」(strategic reticence) 的一般观察: 企业不总是用大量密集关键词高调宣传自己在做什么, 有些采纳行为是在悄悄发生, 文本表层信号 (词频) 弱, 但深层语义信号 (与政策话语的贴合度) 强。生产代码内部注释把这个格子直白地称为「闷声干大事」——银行没有大讲特讲金融科技, 但其报道语言已经悄悄向监管政策的表述方式靠拢, 暗示实质性的技术响应正在发生但未被高调传播。这与「token adoption」(token_adopt_* 家族: 词频高但相似度低, 蹭热词但缺乏政策实质呼应) 和「substantive adoption」(subst_adopt_* 家族: 词频与相似度双高, 既高调又贴合政策) 三分构念在同一象限矩阵体系内互补, 三者共同穷尽已测量报道的分类空间 (还有第四格 irrelevant: 词频低且相似度低, 未被物化为面板列)。
【方法学与计算】
分类算法逐篇进行、按年重估阈值: 对每一年度、每一相似度轨道, 分别取该年该轨全部已测量文章的词频 (fintech_distinct_keywords, 即该篇报道中出现的金融科技词典去重关键词个数) 与相似度 (policy_cosine_sim, 该篇报道文本嵌入与年度政策文本嵌入之间的余弦相似度) 的第 25 百分位数 (P25, 家族名 kw_p25 里的 p25 即此分位阈值; 家族之外还有 P50/P75 平行梯子, 互为稳健性、不分主次, 详见【文献定位】段), 记作 ysim/yfreq。随后对每篇报道判定: high_freq = 词频 >= yfreq, high_sim = 相似度 >= ysim; hidden = (非 high_freq) 且 high_sim。⚠ 关键的缺失值处理铁律: 只有词频与相似度双双非缺失的文章才参与分类, 任一测量失败 (例如 stage 15 词频计算优雅早退, 或 stage 16 政策相似度计算未覆盖) 的文章记为 NaN, 绝不静默按 False 处理——旧实现曾把 NaN 误判为「未达阈值」从而把测量失败的文章错误地并入 irrelevant/token 格子, 人为制造虚假的高词频文章占比; 现行版本经 fix(omni-g-runner-03/g-runner-11) 修正为掩码机制, 未测量文章不进入分子也不进入分母。聚合层面, 按 (target_bank, year) 分组取 hidden 指示列的均值——由于 pandas groupby mean 默认跳过 NaN, 该均值的隐含分母是「该银行该年已双测量的报道篇数」而非全部报道篇数, 因此 hidden_adopt_kw_p25 的取值范围是 [0, 1] 的占比而非计数; 若某银行某年全部报道均未双测量, 面板输出为 NaN (v6/F3 缺失值红线: 无法测量的银行-年绝不用 0 填充, 因为 0 与「真实测得的零隐性采纳」在计量上不可区分, Allison 2001 §3)。kw 轨的词频度量 (fintech_distinct_keywords) 是 track-agnostic 元数据 (逐篇去重关键词计数, 与文本三轨切分无关), 与之相对的 int 轨采用连续型 fintech_intensity_score 作词频侧度量 (对应家族 hidden_adopt_int_p25 等, 不在本家族内)。 就 hidden 象限所对应的现实型态而言, 近期两项中国/亚太语境的实证提供了构念层面的旁证。Chen、Zhang 与 Liu (2026) 刻画了中国企业「多行动少言说 (more action-less talk)」的创新披露沉默型态——实质投入不低而文本声量偏低——正是本家族「词频低于年度 P25 而政策语义相似度不低于年度 P25」这一格的构念对应物, 支持把「低声量、高实质」当作可独立测量的型态而非残差噪音; 迁移边界: 该文层级为上市公司-年, 以年报披露文本与专利/研发投入的落差界定沉默, 落点是商业信用融资, 与本家族基于新闻报道的双分位判据并非同一操作化, 亦无三轨文本与 P25/P50/P75 阈值梯子。Liu、Wang、Wen 与 Wu (2024) 则把企业对系统性风险的回应拆为 talk (文本表述强度) 与 action (实际举措) 两条可分别测量的维度并检验二者关系, 与本家族用「词频高低 × 政策对齐高低」并置言—行两维、由此分出 token 与 hidden 象限属同一测度族; 迁移边界: 该文针对企业层面的系统性风险回应而非银行金融科技采纳, 其 talk 取自披露文本、action 取自财务与公司行为代理, 而本项目两维均来自新闻文本 (去重关键词计数 vs. 政策余弦), 且不含年度分位阈值梯子与 bank-year 已测量篇均占比的聚合口径。
【文献定位】
四象限文本分类范式承袭 Hassan, Hollander, van Lent & Tahoun (2019, *Quarterly Journal of Economics*) 建立的政策不确定性/政策响应文本测度学派——用余弦相似度捕捉企业文本与外部政策话语的贴合程度, 是该学派向「关键词强度 × 语义相似度」二维矩阵的自然扩展。这类基于 LLM/嵌入辅助文本分类的经验策略近年在金融科技采纳测量文献中日益普遍, Kwan, Lin, Pursiainen & Tai (2024, *Journal of Financial and Quantitative Analysis*) 以 COVID-19 冲击为背景对银行数字化能力做压力测试式度量, 独立印证了「银行数字响应强度需要在危机情境下被单独测量、不能仅凭静态披露判断」这一构念动机, 为本家族把隐性/显性/实质三象限采纳测度锚定在危机/政策冲击驱动的响应强度上提供了跨方法论 (非同源文本信号) 的旁证。P25/P50/P75 三档分位阈值构成一条构造判据敏感性梯子, 三档各自 just-identified 并排、互为稳健性、不分主次, 绝不应混入同一 over-identified Hansen J 设定——这一原则与项目内政治词权重梯度 (Du et al. 2022 权重 0/0.5/1)、词典消融梯度、罕见词频次 cutoff 梯子共享同一稳健性哲学: 用固定研究者判断对结果稳健性做多档验证, 而非用某一档去过度识别同一构念。此外, 本类基于研究者自定阈值/分位切分的文本分类流程天然存在「隐藏的研究者决策」问题——Huntington-Klein et al. (2021, *Economic Inquiry*) 与 Breznau et al. (2022, *Proceedings of the National Academy of Sciences*) 均系统记录了看似中性的分析选择 (如本处的分位阈值取值) 如何在多研究者复现中产生结果的隐藏不确定性, 这正是本家族坚持公开三档分位阈值敏感性梯子、而非只报告单一档次结果的方法论动因。

## VAR: hidden_adopt_kw_p25

【变体差分】
这是家族的 canonical (无轨道后缀) 列, 相似度侧使用 policy_cosine_sim (全文轨 full 政策余弦相似度), 词频侧使用 track-agnostic 的 fintech_distinct_keywords (逐篇去重金融科技关键词计数, 不区分 full/ctx/ss 三轨, 因为该计数本质是元数据统计量, 项目里也未对其做三轨版本切分)。分位阈值取年度 P25 (家族名 kw_p25 中的 p25)。分类掩码仅对 policy_cosine_sim 与 fintech_distinct_keywords 双双非缺失的文章生效; 按 (target_bank, year) 聚合为占比, 分母为该银行该年已双测量的报道数。这一列是本家族在三轨梯子里的锚点参照——full 轨相似度基于报道全文本 (标题+正文) 与政策文本的语义比对, 覆盖面最广, 也是留篇门控 (full-only, 2026-06-29) 下唯一直接对应「一篇银行金科报道」判定口径的相似度来源。与同名 P50/P75 变体相比, P25 阈值对 high_sim 判定确实是三档里门槛最低的一档 (相似度只需达到年度后 75% 分位以上即算 high_sim, 比 P50/P75 更容易满足)。但 hidden 定义同时要求 ~high_freq, 而 high_freq 用的是同一 pct 参数——P25 阈值下 high_freq 判定同样门槛更低 (词频只需高于年度后 75% 分位即算 high_freq), 也就更容易被满足, 于是 ~high_freq (词频低于阈值) 在 P25 下反而是三档里最难满足的一侧。两侧一松一紧相互对冲, P25 相对 P50/P75 对 hidden 象限整体占比是扩大还是收窄取决于词频与相似度两个分布的联合结构, 不能单凭「相似度门槛更松」就推断 P25 必然让 hidden 格子纳入更多文章; 三档阈值仍互为稳健性、不分主次, 差异方向留给面板实测数字披露, 不应在文本层面预设结论去挑选其中一档作为主设定过度识别构念。同一象限矩阵体系内还存在全语料静态锚点孪生 (`_allv` 后缀, 相似度改用 policy_cosine_sim_allv 而非随年度滚动的 vintage 锚点), 与本列共享完全一致的词频/相似度双轨判据构造, 唯锚点来源不同, 二者同样互为稳健性并排、不分主次。读者若需比较 full 轨与其它两轨的差异, 应把三轨占比并列陈列而非相减做差分推断, 因为三轨背后的可测量文章子集本身就不完全重合。

## VAR: hidden_adopt_kw_p25_ctx

【变体差分】
本列是 canonical 列在 ctx (实体上下文窗口) 轨的孪生: 相似度侧改用 policy_cosine_sim_ctx (标题+目标银行实体窗口文本与政策文本的余弦相似度), 词频侧优先取同轨变体 fintech_distinct_keywords_ctx (若该同轨列存在于面板上游, 缺失时优雅回退复用 full 轨的 track-agnostic 词频列并在生产日志中披露)。分位阈值仍按年度、按本轨独立重估 P25, 不与 full 轨共享阈值——这保证了 ctx 轨的「高词频」「高相似度」判定是在 ctx 轨自身的经验分布内定义的, 而不是被 full 轨的分布锚定。ctx 轨与 full/ss 轨在铁律层面互为稳健性、各自 just-identified 并排, 绝不应混入同一 over-identified Hansen J 设定共同识别同一系数; 三轨分列并存的目的是让读者能观察「隐性采纳」判定在不同文本窗口 (全文 vs 实体窗口 vs 同句窗口) 下是否稳健, 而非制造可挑选的多重检验空间。ctx 轨相似度反映的是报道中直接围绕目标银行实体的局部语境与政策文本的贴合度, 比 full 轨更聚焦于「这段话是不是在说这家银行」, 理论上能过滤掉全文本中与银行本身无关但也涉及政策话语的段落 (例如行业综述性段落), 因而 ctx 轨的隐性采纳占比可能与 full 轨存在系统性差异, 差异本身即是稳健性检验的信息量所在。

## VAR: hidden_adopt_kw_p25_ss

【变体差分】
本列是 canonical 列在 ss (银行∧金科同句) 轨的孪生: 相似度侧改用 policy_cosine_sim_ss, 词频侧优先取同轨变体 fintech_distinct_keywords_ss (缺失时同样优雅回退复用 full 轨词频列)。ss 轨的判据比 ctx 更严格——只取标题与「目标银行、金融科技词同句出现」(默认 ±1 句半径) 的文本窗口构造相似度, 若某篇报道内银行与金科词从未同句共现, 该篇 ss 轨文本回退为全文 body (镜像 ctx 轨回退语义, `ss_is_fallback` 标记该行使用了回退文本, 与 ctx 轨共享同一 `n_articles` 分母口径)。分位阈值同样按年度、按 ss 轨自身分布独立重估, 与 full/ctx 轨互为稳健性并排、不共享阈值也不混入同一识别方程。ss 轨相似度捕捉的是「银行与金融科技被直接放在同一句话里讨论」这一最严格意义上的关联文本, 相比 full/ctx 两轨更不容易被无关段落的政策式措辞干扰, 因而是本家族三轨梯子中判据最严、噪声最小但覆盖面 (可测量文章数) 可能最窄的一支; 若某银行某年绝大多数报道都未出现银行-金科同句共现, 该银行-年的 ss 轨隐性采纳占比分母会明显小于 full/ctx 轨对应值, 这属于 ss 轨设计的预期行为而非数据缺陷。

<!-- rendered-citations:begin -->
Kwan, A., Lin, C., Pursiainen, V., & Tai, M. (2024). Stress testing banks' digital capabilities: Evidence from the COVID-19 pandemic. Journal of Financial and Quantitative Analysis, 59(6), 2618-2646. https://doi.org/10.1017/S0022109023000662
Breznau, N., Rinke, E. M., Wuttke, A., Nguyen, H. H. V., Adem, M., Adriaans, J., et al. (2022). Observing many researchers using the same data and hypothesis reveals a hidden universe of uncertainty. Proceedings of the National Academy of Sciences, 119(44), e2203150119. https://doi.org/10.1073/pnas.2203150119
Huntington-Klein, N., Arenas, A., Beam, E., Bertoni, M., Bloem, J. R., Burli, P., et al. (2021). The influence of hidden researcher decisions in applied microeconomics. Economic Inquiry, 59(3), 944-960. https://doi.org/10.1111/ecin.12992
Chen, M., Zhang, Z., & Liu, Y. (2026). Silence in innovation disclosure: More action-less talk innovation and trade credit financing in China. Finance Research Letters, 95, 109668. https://doi.org/10.1016/j.frl.2026.109668
Liu, Y., Wang, J., Wen, F., & Wu, C. (2024). Corporate responses to systemic risk: Talk and action. Pacific-Basin Finance Journal, 87, 102493. https://doi.org/10.1016/j.pacfin.2024.102493
<!-- rendered-citations:end -->
