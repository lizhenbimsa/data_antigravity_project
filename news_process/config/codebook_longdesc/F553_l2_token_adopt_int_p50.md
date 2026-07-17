---
family_id: F553
columns:
- token_adopt_int_p50
- token_adopt_int_p50_ctx
- token_adopt_int_p50_ss
unit: 占比 (0–1 区间, 银行-年内"落入 Token 象限"的文章篇数占已测量篇数的比例)
formula: 'token_adopt_int_p{50} = mean_i(1[fintech_intensity_score_i >= 年度P50分位阈值 AND policy_cosine_sim_i < 年度P50分位阈值]), 仅对 sim 与 freq 双双非缺失(measured)的文章 i 计入分子分母; 年度分位阈值按年份分组 quantile(0.50) 计算 (core.panel.runner::_classify_policy_quadrants)'
producer: pipeline\panel\runner.py
upstream:
- pipeline\panel\fintech_intensity.py
- pipeline\panel\policy_alignment.py
citations:
- doi: 10.1007/s11573-017-0852-x
  type: journal
  authors: Gomber, P., Koch, J.-A., & Siering, M.
  year: 2017
  title: 'Digital finance and FinTech: Current research and future research directions'
  venue: Journal of Business Economics
  vol: '87'
  issue: '5'
  pages_or_artno: 537-580
- doi: 10.1002/smj.821
  type: journal
  authors: Adner, R., & Kapoor, R.
  year: 2010
  title: 'Value creation in innovation ecosystems: How the structure of technological
    interdependence affects firm performance in new technology generations'
  venue: Strategic Management Journal
  vol: '31'
  issue: '3'
  pages_or_artno: 306-333
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: 'Text-based sentiment analysis in finance: Synthesising the existing literature
    and exploring future directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
- doi: "10.1007/s10799-026-00501-9"
  type: "journal"
  authors: "Pan, Y., Xue, F., & Liu, L."
  year: 2026
  title: "Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing"
  venue: "Information Technology and Management"
- doi: "10.1177/01708406241295505"
  type: "journal"
  authors: "Kaufmann, L., Krlev, G., & Brown, M. (."
  year: 2025
  title: "In Plain Sight: Mechanisms of means–ends decoupling in impact investing"
  venue: "Organization Studies"
  vol: "46"
  issue: "5"
  pages_or_artno: "667-692"
- doi: "10.2139/ssrn.6922688"
  type: "wp"
  authors: "Xu, F."
  year: 2026
  title: "Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks"
  venue: "SSRN"
  pages_or_artno: "6922688"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"银行对金融科技话语的采纳方式"——不是有没有报道金融科技,而是报道金融科技的方式落在四种模式里的哪一种。构念直接来自 Gomber, Koch & Siering (2017) 对数字金融/金融科技创新的分类学传统: 企业对新技术话语的吸纳存在"标签化蹭热点"与"实质性融入自身叙事"两种截然不同的路径, 二者对企业真实的技术采纳行为有不同的信号含量, 不能用同一个连续分数笼统衡量。本族属于 P4(Gomber locus 维)论文序列产出的机制检验/稳健性四象限分类之一, 与家族核心变量 innovation_locus_full/ctx(LLM 判定的创新定位)构成同一构念空间下"关键词-嵌入双引擎互证"的一支。

具体构造逻辑: 对每一篇通过留篇门控的文章, 同时观测两个维度——(1) 该文章讨论金融科技的"强度"(词频侧, 本家族用 INT 轨即 fintech_intensity_score, 是逐篇金融科技强度连续分数, 区别于另一并行家族用的 KW 轨即 AC 自动机去重关键词计数 fintech_distinct_keywords); (2) 该文章与银行官方政策文本的"语义对齐度"(policy_cosine_sim, 逐篇余弦相似度)。以银行-年为单位、按年份分别取两个维度的样本内分位数作阈值, 把每篇文章分入四个格子: 高强度&高对齐=Substantive(实质性采纳, 家族 subst_adopt_*); 高强度&低对齐=Token(符号化/蹭热点采纳, 本家族 token_adopt_*); 低强度&高对齐=Hidden(低调对齐, 家族 hidden_adopt_*); 低强度&低对齐=Irrelevant(不相关, 不单独出面板列)。三个 adopt 系族(token/hidden/subst)在银行-年层面被聚合为"该格子文章数占已测量文章数的比例"——即 groupby(['target_bank','year'])[指示列].mean(), pandas mean 对 NaN 自动跳过, 因而分母天然等于该银行-年内 sim 与 freq 双双非缺失(已测量)的文章数, 而非全部报道篇数。

本家族三列固定为 INT 轨(词频维用 fintech_intensity_score 连续强度分数而非关键词计数) × P50 分位阈值(年度中位数切分, 是 {25,50,75} 三档分位梯子中的居中档) × vintage 锚点(sim 用当期滚动 policy_cosine_sim, 区别于另有 _allv 后缀的全语料静态锚点稳健孪生, 该锚点变体不在本家族范围)× full/ctx/ss 三文本轨的 Token 格子占比。

【方法学与计算】
分类函数 `_classify_policy_quadrants`(pipeline/panel/runner.py) 对每一 (词频轨, 分位数 pct, 相似度轨) 组合逐篇产出三个浮点指示列 `_is_token_*`/`_is_hidden_*`/`_is_subst_*`。年度阈值用 `groupby('year')[col].transform(lambda x: x.quantile(p/100.0))` 计算, 即阈值按年重新估计(而非跨年混合样本一次性估计), 与 stage 21 情感/stage 15 强度的"年度对齐"惯例一致, 避免早期样本量小年份的分位数被后期年份稀释。分类判据: high_freq = freq >= 年度阈值; high_sim = sim >= 年度阈值; token = high_freq & ~high_sim; hidden = ~high_freq & high_sim; subst = high_freq & high_sim。measured 掩码 = sim 与 freq 同时非缺失; 未测量的文章三个指示列全部输出 NaN 而非误判为 False(2026-06-11 修复 omni-g-runner-03/g-runner-11: 旧实现把测量失败的文章静默计入低对齐/低词频格子, 导致 stage 15 优雅早退产生的全 NaN policy_cosine_sim 会让全部高词频文章误判为 Token, 且逐篇 NaN 会滞留进物理域分母污染占比)。聚合层沿用同一"无数据=未测量"契约: 全年无可测量报道的银行-年输出面板 NaN, 不会被 fillna(0) 掩盖为"零采纳"(v6/F3 修复删除了原先的 fillna(0.0), 因为 0 与"未测量"在计量含义上截然不同, 强填零会污染 TWFE 系数, 参考 Allison(2001) 关于缺失数据处理的一般性告诫)。

三轨(full/ctx/ss)口径: full 轨的相似度/词频列为无后缀基名(policy_cosine_sim / fintech_intensity_score); ctx 轨优先使用同轨变体列(policy_cosine_sim_ctx / fintech_intensity_score_ctx, 若词频列无同轨变体则该维度退化为 track-agnostic 复用 full 列, 并在日志中披露); ss 轨镜像 ctx 的逻辑, 使用 policy_cosine_sim_ss / 对应 _ss 词频列, 缺列时优雅跳过整轨孪生(旧 schema 兼容)。三轨严格并排——full/ctx/ss 各自独立完成"分位阈值估计→四象限分类→银行-年聚合"的全流程, 不共享阈值也不共享分类结果, 是互为稳健性、不分主次的规格并排关系, 禁止把三轨的四象限占比同时塞进同一个 over-identified 的 Hansen J 检验框架(与项目其余三轨测度——情感/政策对齐/staleness 等——遵循同一铁律)。留篇门控口径与全项目一致, 采用 2026-06-29 起的 full-only 门控: 一篇文章是否被计入"银行-金科报道"universe 只看 llm_verified_full, ctx/ss 是 conditional-on-full 的测度轨(行宇宙是 full 留篇集的子集), 本家族的 ctx/ss 分类同样建立在这一行宇宙之上。ss 轨的回退语义镜像 ctx: 若某文章没有银行与金科词的同句共现, content_ss 回退为全文正文(ss_is_fallback=True), fintech_intensity_score_ss 等下游测度在此回退语义上照常计算, 不会因回退而被排除出四象限分类。

INT 轨与并行的 KW 轨(token_adopt_kw_p50 等)是词频测度维度上的两种独立算子——INT 用连续强度打分, KW 用关键词计数——二者同样是并排的、互为稳健性的规格, 不构成主次关系, 也不应混入同一识别方程。P25/P50/P75 三档分位阈值构成另一条正交的稳健性梯子(阈值敏感性), 本家族固定在 P50(年度中位数切分, 是三档中样本最均衡的居中档), P25/P75 是另外两个独立家族, 与本家族并排、不构成层级关系。

【文献定位】
四象限"标签-实质"分类的构念根基是 Gomber, Koch & Siering(2017)对数字金融/金融科技创新研究方向的系统梳理, 该文强调金融科技话语存在从边缘符号性提及到核心业务整合的连续谱系, 是 P4 论文序列(Gomber locus 维)的直接理论出处。测度层面, 高强度-低对齐的"Token"格子刻画的是一种典型的企业传播现象——组织在缺乏实质技术投入的情况下通过密集使用热点词汇维持外部合法性观感, 这与创新生态系统研究中企业间技术互依结构影响绩效表现的框架(Adner & Kapoor, 2010, Strategic Management Journal)有相通的分析逻辑: 二者都关注"话语声量"与"结构性投入/互依"之间可能存在的脱节。分类使用的相似度维度(policy_cosine_sim, 逐篇文本与政策文本的余弦相似度)属于文本挖掘中广泛使用的语义对齐测度传统。Todd, Bowden & Moshfeghi(2024, Intelligent Systems in Accounting, Finance and Management)系统梳理了金融文本情感分析领域方法学的演进脉络——从早期词典法到近年基于向量空间表示的分类路径, 其中特别指出连续型文本测度在应用研究中普遍需要经过离散化(如阈值切分、分位数分箱)才能落地为可解释的类别变量, 这与本族"用年度分位数把连续的强度分数与相似度分数切成高/低两档、再组合成四象限"的做法属于同一类方法学操作; 需要说明的是, 该文献本身聚焦情感分析而非政策语义对齐或四象限分类这一具体应用, 此处仅借其对"连续测度离散化"这一通用方法学环节的梳理作为旁证, 不代表该文献直接讨论过 Token/Hidden/Substantive 象限分类本身。 近年文献进一步为本族赖以成立的象限二分提供了更直接的前沿存在性证据。Pan、Xue 与 Liu (2026) 把技术采纳明确拆为「符号性采纳 (symbolic adoption)」与「实质性行动 (substantive action)」两维, 并把二者的背离操作化为 AI washing 加以实证测量, 与本族「把同一构念拆成强度维与对齐维并置、再由二者的错位识别 Token」的做法同构; 其迁移边界在于对象是一般企业的 AI 叙事而非银行, 符号/实质二分基于组织冗余与披露数据, 既不使用政策文本余弦相似度, 也不做年度分位阈值切分, 层级为企业而非银行-年、分母亦非已测量报道篇数。Kaufmann、Krlev 与 Brown (2025) 以影响力投资为田野, 系统刻画了 means-ends decoupling (形式上落地但与目标脱节) 的具体机制, 为 Token 格与 Substantive 格的理论区分提供了近期组织学依据; 但该文为定性机制研究, 不构造任何数值指标, 更无分位阈值二值化或银行-年聚合, 场域是影响力投资机构而非中国银行业, 其 means-ends 概念与本族「政策余弦 × 金科强度」的操作化只是理论对应而非同一测量。词频维方面, Xu (2026) 以文本方法构造银行层面的 FinTech intensity 指标并检验其与经营绩效的关系, 与本族 INT 轨所用的 fintech_intensity_score 属同一测度族, 是「银行层面文本金科强度」的同域应用先例; 需注意其样本为欧洲银行、文本取自银行自身披露/年报而非第三方中文新闻, intensity 作为连续指标直接进入回归而不做年度分位二值化, 更无与政策文本相似度交叉形成 2×2 象限, 且属未经同行评审的 SSRN 工作论文, 结论稳健性未定。
## VAR: token_adopt_int_p50

【变体差分】
本列是家族的 full 轨、无 _allv 锚点后缀的基准列, 词频维取 fintech_intensity_score(全文本扫描的金融科技强度连续分数), 相似度维取 policy_cosine_sim(全文本与政策文本的当期滚动余弦相似度), 二者均按年度 P50(中位数)分位阈值切分。该列刻画的是"高强度、低政策语义对齐"的 Token(符号化采纳)象限占比, 分子为该银行-年内落入此象限的 full 轨已测量文章数, 分母为该银行-年内 sim 与 freq 双双非缺失的 full 轨已测量文章数(而非全部报道篇数)。与 P25/P75 两档并排为分位阈值敏感性梯子(P50 是居中档, 三档地位对等、互为稳健性), 与 KW 轨的同名列(token_adopt_kw_p50)并排为词频测度敏感性梯子, 与 ctx/ss 两个孪生列并排为三轨稳健性梯子。作为 full 轨基准, 该列对应的行宇宙即 stage 21 全文本留篇门控(llm_verified_full=True)确定的样本, 是 ctx/ss 两轨在"行宇宙"意义上的锚定参照。

用大白话讲: 想象把一家银行某一年被报道的所有金融科技相关新闻摊开来看, 每篇新闻问两个问题——"这篇报道里金融科技话题讲得浓不浓"(强度)和"这篇报道的说法跟银行自己发的政策文件像不像"(对齐度)。把全行业该年所有报道按这两个指标各自排队, 排在前一半算"浓/像", 排在后一半算"淡/不像"。本列统计的是"浓但不像"这一类报道占该银行-年全部可判定报道的比例——也就是媒体上大量提金融科技、但说法和银行官方政策口径对不上号的那类新闻, 常被理解为蹭热点式的符号化宣传, 而非真正落地到银行政策叙事里的实质动作。该占比越高, 说明这家银行当年围绕金融科技的媒体形象越偏"声量大、落地浅"。full 轨用的是完整正文, 是三条平行文本口径里覆盖信息最全的一条, 常作为其余两条口径(实体窗口/同句共现)结果是否稳健的参照锚点, 但三者在统计设计上地位相同, 谁也不是"更权威"的那一个。

## VAR: token_adopt_int_p50_ctx

【变体差分】
本列是家族的 ctx 轨变体, 相似度维取 policy_cosine_sim_ctx(标题+实体窗口文本与政策文本的余弦相似度), 词频维优先取 fintech_intensity_score_ctx(实体窗口文本的强度分数, INT 轨在 ctx 下确有同轨变体列, 不同于 KW 轨"track-agnostic 复用 full 列"的降级路径)。年度 P50 分位阈值在 ctx 轨自身样本内独立估计, 不借用 full 轨阈值。行宇宙仍是 full-only 门控确定的留篇文章集合(conditional-on-full), 但四象限分类所依据的文本内容、强度分数、相似度分数均切换为 ctx 轨专属测度。与 full/ss 两轨互为稳健性并排, 禁止混入同一 Hansen J; 是构念上"实体聚焦窗口视角下 Token 采纳模式是否依然成立"的稳健性检验轨, 而非另一种主测度。

用大白话讲: full 轨看的是整篇报道, 但一篇几千字的报道里可能只有几句话真正在讲"目标银行+金融科技"这件事, 其余篇幅可能在聊别的业务或大盘行情, 混进去会稀释测量精度。ctx 轨的做法是先把银行名字、金融科技相关实体周围的一小段窗口文字摘出来(标题+实体窗口), 只用这一小段去重新算强度分数和政策对齐相似度, 再重新按年度分位数排队分类。这样做出来的 Token 占比回答的是: 如果只聚焦"报道里真正谈到这家银行和金融科技的那几句话", 结论是不是还是"浓但不像"占大头?如果 full 轨和 ctx 轨算出来的占比走势一致, 说明结论不是被报道里的无关篇幅带偏的; 如果明显不一致, 则提示要谨慎解读。ctx 轨样本行数是 full 轨留篇集合的子集, 且自成一套独立的年度阈值和分类结果, 不与 full 轨共用任何中间量。

## VAR: token_adopt_int_p50_ss

【变体差分】
本列是家族的 ss 轨变体, 相似度维取 policy_cosine_sim_ss(银行∧金科同句±N窗文本与政策文本的余弦相似度), 词频维优先取对应 _ss 后缀的强度分数列; 缺列时该轨孪生整体优雅跳过(旧 schema 兼容路径)。ss 轨的文本构造回退语义镜像 ctx: 若某篇文章不存在银行与金科词的同句共现, content_ss 在 stage 14 物化阶段即回退为全文正文(ss_is_fallback=True), 该回退语义会向下游传导进本列所依赖的强度与相似度测度, 不影响四象限分类的执行(回退文章依然参与年度阈值估计与分类, 只是其底层文本退化为 full 文本)。行宇宙同样是 full-only 门控下的留篇集合的子集(conditional-on-full)。与 full/ctx 两轨互为稳健性并排, 三轨各自 just-identified, 禁止混入同一 over-identified Hansen J 识别框架; 是"银行与金科词紧邻同句共现语境下 Token 采纳模式是否依然成立"的最严格文本窗口稳健性检验轨。

用大白话讲: ss 轨比 ctx 轨的要求还要更苛刻——它只保留"银行名字"和"金融科技相关词"同时出现在同一句话(前后再各扩一点点窗口)里的那部分文字来重新计算强度和相似度, 是三条口径里对"报道确实在同时谈这家银行和金融科技"这件事要求最严格的一条。如果某篇报道压根没有这种紧挨着的同句提及(比如银行和金融科技分别出现在文章不同段落), 这一轨就不硬性剔除该篇文章, 而是退回去用整篇正文顶替, 并留一个标记表示"这篇是退回来的", 目的是避免因为窗口太窄而把样本量砍得所剩无几。分类之后按银行-年汇总出的 Token 占比, 回答的是"就算把标准收紧到只看银行与金融科技被同一句话捆在一起提及的那些内容, 蹭热点式的符号化采纳依然是主流现象吗"这一更严苛版本的问题, 与 full/ctx 两轨的结果放在一起比较, 三者一致则结论更可信, 不一致也不意味着谁对谁错, 而是提示报道的文本层次结构本身在起作用。

<!-- rendered-citations:begin -->
Gomber, P., Koch, J.-A., & Siering, M. (2017). Digital finance and FinTech: Current research and future research directions. Journal of Business Economics, 87(5), 537-580. https://doi.org/10.1007/s11573-017-0852-x
Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems: How the structure of technological interdependence affects firm performance in new technology generations. Strategic Management Journal, 31(3), 306-333. https://doi.org/10.1002/smj.821
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Pan, Y., Xue, F., & Liu, L. (2026). Divergence between symbolic adoption and substantive action: how organizational slack shapes AI washing. Information Technology and Management. https://doi.org/10.1007/s10799-026-00501-9
Kaufmann, L., Krlev, G., & Brown, M. (. (2025). In Plain Sight: Mechanisms of means–ends decoupling in impact investing. Organization Studies, 46(5), 667-692. https://doi.org/10.1177/01708406241295505
Xu, F. (2026). Bank FinTech Intensity and Financial Performance: Text-Based Evidence from European Banks. SSRN No. 6922688 [Working Paper]. https://doi.org/10.2139/ssrn.6922688
<!-- rendered-citations:end -->
