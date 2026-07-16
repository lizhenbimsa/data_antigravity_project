---
family_id: F473
columns:
- pos_count_ctx
- pos_count_full
- pos_count_ss
- pos_count_vw_ctx
- pos_count_vw_full
- pos_count_vw_ss
unit: 篇数/计数 (count, 加权变体为提及密度加权和, 无量纲但与"篇数"同量级)
formula: 'pos_count{track} = Σ_i is_positive_i{track} (bank-year 内 LLM 投票判正的文章篇数, is_positive 来自 llm_vote_score{track}>0 的离散指示, 详见文献定位段); pos_count_vw{track} = Σ_i is_positive_i{track} × mention_density_i (mention_density_i = 该银行在文章 i 中被提及次数 / 文章长度, 文本经济学文献中常见的提及密度暴露权重思路, 源列在 pipeline/filtering/news_bank.py 逐篇预计算; 加权聚合在 pipeline/panel/runner.py 步骤 3b 预乘, pipeline/panel/encode.py 求 bank-year 和)'
producer: pipeline\panel\runner.py (步骤3b 提及密度加权列预计算) ; pipeline\panel\encode.py (build_bank_year_panel 聚合字典)
upstream:
- pipeline\filtering\news_bank.py (mention_density 逐篇预计算)
- pipeline\sentiment\encode.py 或对应 encode_sentiment (is_positive{track} 逐篇离散指示, 由三家 LLM 多数投票 llm_vote_score{track} 派生)
- 14_materialize_ctx (content_ctx/content_ss 物化, 供 ctx/ss 轨情感重跑)
citations:
- doi: "10.1002/isaf.1549"
  type: journal
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: "Intelligent Systems in Accounting, Finance and Management"
  vol: "31"
  issue: "1"
  pages_or_artno: "e1549"
- doi: "10.1016/j.jfineco.2022.08.004"
  type: journal
  authors: "Cohn, J. B., Liu, Z., & Wardlaw, M. I."
  year: 2022
  title: "Count (and count-like) data in finance"
  venue: "Journal of Financial Economics"
  vol: "146"
  issue: "2"
  pages_or_artno: "529-551"
- doi: "10.1016/j.jfineco.2022.07.009"
  type: journal
  authors: "Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R."
  year: 2022
  title: "Bank transparency and deposit flows"
  venue: "Journal of Financial Economics"
  vol: "146"
  issue: "2"
  pages_or_artno: "475-501"
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"一个银行在某年被正面报道的绝对数量", 即 bank-year 面板层面对 LLM 情感判定为正面 (is_positive==1) 的文章篇数做加总, 以及在此基础上按提及密度加权的加总。这是本项目情感测度体系里最基础的"频次"层——不问语调有多强, 只问有多少篇文章被判为正面报道。构念上它对应文本情感文献里的"频次法" (frequency-based sentiment counts) 谱系: 与最早的词典频次计数 (Tetlock 2007 JF 首创的负面词频占比思路) 一脉相承, 只是本项目的正/负判定不是靠词典计数而是靠三家大模型 (gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 投票后的离散标签 is_positive/is_negative, 这一点在 CLAUDE.md「LLM 三家…互为稳健性」条目下有明确记载: llm_vote_tone 是三家多数投票的共识测度, pos_count/neg_count 正是从这一共识的离散化结果 (is_positive{track}) 逐篇加总而来, 与三家各自的 per-model 子测度 (gpt54nano_tone 等) 是并列而非替代关系。

大白话讲: 假设某银行在 2018 年一共被 200 篇文章报道, 经三家 AI 模型投票后有 65 篇被判定为"正面报道", 那么 pos_count_full 这一格就是 65。这个数字本身不区分"强烈正面"还是"略微正面", 也不管这 65 篇文章各自写了多长、提到银行名字多少次——它就是一个纯计数, 类似"这一年银行收到了多少条好评"。而 pos_count_vw_full 则在这个基础上做了一个修正: 如果一篇正面文章通篇反复提到这家银行 (提及密度高), 它对这个计数的贡献就比一篇只在开头提了一句就转去说别的银行的文章更大——即便两篇都被判为"正面"。这类似于在计算"好评数"时, 给那些真正聚焦谈论这家银行的好评文章更高的权重, 而不是每篇好评一视同仁地记 1 分。

【方法学与计算】
pos_count{track} 的计算路径是: 首先 stage 21 (tone_llms) 让三家 LLM 各自对每篇文章 (三轨 full/ctx/ss 各一份) 打出情感分数, 随后 encode_sentiment 用多数投票规则把三家结果压缩成一个逐篇的共识标签 llm_vote_score{track}, 并派生离散指示列 is_positive{track} (llm_vote_score{track}>0 时为 1, 否则为 0) 与 is_negative{track} (对称)。到了 pipeline/panel/encode.py 的 build_bank_year_panel 聚合阶段, agg 字典里登记 `pos_count{track} = (is_positive{track}, 'sum')`——即按 (target_bank, year) 分组对该指示列求和, 得到该银行该年被判正面的文章篇数。这是一个纯粹的计数聚合, 不涉及任何归一化或分母调整, 因此其量纲就是"篇"。

pos_count_vw{track} (vw = value-weighted, 提及密度加权) 的计算路径更长一步: 在 runner.py 步骤 3b, 系统先为每篇文章计算权重 w = mention_density (来自 news_bank.py: 该银行在文章中被提及的次数 / 文章总长度, 是文本经济学暴露度量文献中常见的"提及密度"权重思路的移植——该类方法原用于衡量公司在电话会议/新闻文本中对某风险或主题的暴露强度, 本项目移植到衡量文章对目标银行的"聚焦程度"); 随后把 is_positive{track} 逐篇乘以这个权重, 得到 is_positive_w{track} = is_positive{track} × mention_density; 最后 encode.py 在 bank-year 聚合阶段对这个加权列求和: `pos_count_vw{track} = (is_positive_w{track}, 'sum')`。因此 pos_count_vw 不再是一个整数"篇数", 而是一个连续值的加权和——每篇正面文章按其对目标银行的提及密度贡献一个 0 到 1 之间(mention_density 的典型值域)的分数, 而非固定贡献 1。两者的关系可以理解为: pos_count 是"等权计数", pos_count_vw 是"聚焦度加权计数", 二者对同一构念(正面报道数量)提供了不敏感于提及强度和敏感于提及强度两种互补视角, 遵循 CLAUDE.md 双轨"互为稳健性"的一般原则(尽管这里不是 full/ctx/ss 那种正交的三轨设计, 而是同一轨内的等权/加权两种权重方案, 二者应联合报告而非相互替代)。

三个文本轨道 full/ctx/ss 对应本项目情感测度体系的统一口径: full = 标题+全文正文; ctx = 标题+目标实体窗口文本; ss = 标题+银行与金科词同句共现窗口文本 (无同句共现时回退为全文 body, 由 ss_is_fallback 指示, 语义上镜像 ctx 轨的回退规则——ss_is_fallback=True 时 n_articles 分母口径与 ctx 保持一致处理)。三轨在下游回归中各自 just-identified 并排比较、互为稳健性、不分主次, 严禁把三轨系数塞进同一个 over-identified 的 Hansen J 过度识别检验框架。需要特别强调的是: 2026-06-29 起本项目采用 full-only 留篇门控——一篇文章是否算作"一篇被处理的银行-金科报道"只看 full 轨的 llm_verified_full 是否为真; ctx/ss 两轨降格为"以 full 留篇集为行宇宙的条件测度"(conditional-on-full), 即 pos_count_ctx/pos_count_ss 的分子虽各自逐轨判定 is_positive, 但样本行范围仍受 full 轨留篇结果约束。

【文献定位】
频次法情感计数是文本情感分析里最古老也最稳健的构念之一, 早期锚定文献是 Tetlock (2007, Journal of Finance)"Giving Content to Investor Sentiment"以及后续 Loughran & McDonald (2011, Journal of Finance) 建立的金融专用词典, 二者本质上都是在做"正/负面词或句子的计数"。本项目虽以 LLM 判定取代词典判定, 但保留了"计数"这一最朴素的测度形式, 与词典法/BERT 法的连续分数并列, 共同构成情感测度的方法学梯度(词典/LLM/BERT 三法互为稳健性)。加权计数的思路借鉴自文本经济学暴露度量文献中较为通行的"提及密度"权重构造方法——该类文献普遍强调仅仅统计"是否提及"不足以刻画暴露强度, 需按文本中该主题词/实体出现的相对密度加权; 后续气候风险暴露测度文献也进一步推广了这一提及密度加权范式, 是本家族 pos_count_vw 变体方法学谱系的旁证。需明确的是, 本条方法学脉络描述属于通行做法概述, 并非指向本家族 citations 结构化条目中的某一篇具体文献——本家族的结构化引文以下方白名单条目为准, 不额外挂靠未纳入白名单的具体作者署名。近年综述文献 Todd, Bowden & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 对金融文本情感分析的方法学谱系 (词典法/机器学习法/LLM 法) 做了系统梳理, 指出频次型指标与连续型情感分数应作为互补而非替代的测度并列报告, 与本家族在面板中同时保留 pos_count(等权)与 llm_vote_tone(连续均值)的设计逻辑一致。Cohn, Liu & Wardlaw (2022, Journal of Financial Economics)"Count (and Count-Like) Data in Finance"专门讨论了金融实证研究中计数型因变量/控制变量的计量注意事项 (过度离散、零膨胀等), 提醒本家族在下游回归中若将 pos_count 作为被解释变量, 应考虑泊松/负二项等计数模型而非简单 OLS, 这是本家族区别于连续型语调测度 (如 llm_vote_tone) 在计量策略上的关键差异点。银行层面的文本披露/媒体报道计数与银行透明度、存款流动之间的关系已有直接实证先例——Chen, Goldstein, Huang & Vashishtha (2022, Journal of Financial Economics) 发现银行透明度会显著影响存款流动的敏感性, 提示本家族 pos_count 系列作为银行媒体形象的计数化代理变量, 在用作回归解释变量时需要控制银行自身信息环境的异质性, 否则容易把"该银行本身更透明、因此更容易被正面报道"与"正面报道本身促成了更好的经营结果"这两条因果路径混淆。

## VAR: pos_count_ctx

【变体差分】
本列是 pos_count 家族在 ctx (context, 标题+目标实体窗口文本) 轨上的等权计数: bank-year 内、以 ctx 轨文本重新跑三家 LLM 情感投票后判定为正面 (is_positive_ctx==1) 的文章篇数之和, 未做提及密度加权。与 pos_count_full 的区别在于输入文本范围更窄 (只截取围绕目标实体的窗口, 而非全文), 因此其情感判定更聚焦于"该银行相关段落"本身的语调, 可能过滤掉全文中与银行无关但影响整体基调的段落——例如一篇通篇讨论宏观金融政策、仅在结尾附带一句提及某银行动态的报道, 在 full 轨上可能因通篇论调偏正面而被判为正面, 但在 ctx 轨上因为只截取了实体窗口附近的文字, 判定结果可能翻转为中性甚至负面。这种潜在的不一致正是三轨并排设计的价值所在: 它揭示了"整体基调"与"实体局部语境"两种不同构念对同一篇文章可能给出不同的情感读数。与 pos_count_ss (同句共现轨) 的区别在于窗口宽度更大——ctx 截取的是围绕目标实体的一段窗口文本, 而 ss 要求银行与金科词严格出现在同一句话内, 后者的判据更苛刻、样本更稀疏。需再次强调 CLAUDE.md 铁律: ctx 轨是 full 轨的条件测度/稳健性轨, 其样本行范围以 full 轨的留篇判定 (llm_verified_full) 为行宇宙上界, 二者应在回归中并排作为互为稳健性的规格, 不应混入同一 over-identified Hansen J 过度识别框架, 也不应视 ctx 为比 full 更"精确"的替代版本——两者是对同一构念的两种互补测量视角, 结果不一致本身即是有信息量的稳健性发现, 而非需要调和消除的"矛盾"。

## VAR: pos_count_full

【变体差分】
本列是 pos_count 家族的 canonical 主轨: bank-year 内以 full 轨文本 (标题+全文正文) 情感投票判定为正面的文章篇数之和, 未做提及密度加权。它是三轨 (full/ctx/ss) 中口径最宽的一支, 也是留篇门控 (是否算作"一篇有效的银行-金科报道") 的唯一判据来源——2026-06-29 起本项目明确 full-only 门控口径: 一篇文章能否进入 bank-year 面板的分母 (n_articles) 完全由 full 轨的 llm_verified_full 判定决定, ctx/ss 两轨的样本行范围均以此为上界, 二者只在 full 轨已确认的留篇集合内部计算各自轨道的情感判定。这意味着 pos_count_full 与 pos_count_ctx/pos_count_ss 共享同一个分母基础(样本篇数上限), 差异仅来自各轨情感判定结果本身的不同, 而非样本纳入范围的不同。在下游多数 paper 模块 (P1 bank_fintech_tone 等) 的主线设定里, full 轨对应的语调/计数测度是首选口径; pos_count_full 本身通常作为构造更精细情感强度指标 (如 log_sent = log1p(pos_count_full)−log1p(neg_count_full)) 的分子来源之一, 该衍生指标同样遵循"无文章覆盖 (n_articles==0) 时输出 NaN 而非伪零"的缺失值契约, 以避免把"该银行该年完全无报道、情感不可测"误记为"正负报道数量恰好相等的完全中性"——这是 pos_count_full 及其派生指标在面板层面的一条硬性缺失值语义, 使用前须核对是否已按 n_articles>0 做覆盖门控。

## VAR: pos_count_ss

【变体差分】
本列是 pos_count 家族在 ss (same-sentence, 同句共现) 轨上的等权计数: 以银行实体与金科词严格出现在同一句话内的窗口文本重新判定情感后, bank-year 内正面文章篇数之和。这是三轨中构造判据最窄、最贴近"银行与金融科技话题被同时、紧密提及"这一构念的一支——full 轨只要求文章整体涉及银行(全文视角), ctx 轨要求处于实体附近窗口, 而 ss 轨要求两类实体词在物理上共处一句, 判据严格程度依次递增。当某篇文章不存在银行∧金科同句共现时, 该文章的 content_ss 文本物化环节会回退为全文 body, 并由 ss_is_fallback=True 标记——这一回退语义严格镜像 ctx 轨的回退规则(二者共享"缺构造条件即退化为更宽文本"的设计哲学), 回退发生时该篇文章仍参与 pos_count_ss 的分子计数(以回退后的全文情感判定为准), 而 frac_ss_fallback 等辅助列会披露回退发生的比例, 供研究者判断该银行-年格是否因同句共现样本过少而测量噪声偏大。ss 轨与 ctx/full 轨同样是 just-identified 并排的互为稳健性规格, 三者应联合报告、禁止混入同一 over-identified Hansen J 检验; 且其行宇宙同样以 full 轨的留篇结果 (llm_verified_full) 为条件集合上界, 不构成独立于 full 轨的样本扩张。

## VAR: pos_count_vw_ctx

【变体差分】
本列是 pos_count_ctx 的提及密度加权版本: 先把 ctx 轨的逐篇正面指示 is_positive_ctx 乘以该文章的 mention_density (银行提及次数/文章长度) 权重, 得到 is_positive_w_ctx, 再在 bank-year 层面求和。与 pos_count_ctx 的差异是权重方案而非文本轨道——两者用的都是 ctx 轨文本判定出的情感标签(即"哪些文章算正面"的判定完全相同), 唯一区别是本列对"提及密度"更高(即文章更聚焦谈论目标银行)的正面文章赋予了大于典型值、更贴近该文章实际暴露强度的等效贡献, 密度更低的文章贡献相应缩小, 而 pos_count_ctx 对所有正面文章一视同仁记 1(不区分聚焦程度)。这一权重构造沿用前述提及密度暴露加权思路, 但施加对象是 ctx 轨(实体窗口文本)而非 full 轨全文, 因此其权重与情感判定在窗口口径上是内部一致的——不存在"用全文密度加权窗口情感"这类跨轨混用。二者(pos_count_ctx 与 pos_count_vw_ctx)应联合报告, 作为对"计数是否应按聚焦强度加权"这一构造判据的敏感性检验, 而非相互替代的主/辅测度; 与 pos_count_vw_full/pos_count_vw_ss 相比, 本列继承的是 ctx 轨"围绕实体窗口"这一中间口径, 在文本范围宽窄谱系中处于 full 与 ss 之间。使用者若同时报告本列与 pos_count_ctx, 相当于对"ctx 轨内是否应按提及密度加权"这一单一维度做敏感性对照, 而不涉及跨轨道的构念替换, 结果的一致性可用于检验 ctx 轨情感信号是否对个别高密度或低密度文章过度敏感。

## VAR: pos_count_vw_full

【变体差分】
本列是 pos_count_full 的提及密度加权版本: 以 full 轨文本判定的逐篇正面指示 is_positive_full 乘以 mention_density (该银行在文章中的提及次数/文章总长度) 权重后, 在 bank-year 层面求和, 加权步骤在 runner.py 步骤 3b 预计算、encode.py 聚合阶段求和。它是 vw 加权计数三轨中口径最宽的一支, 对应 canonical 主轨 pos_count_full 的加权稳健性对照——即便某篇 full 轨判定为正面的文章只是"顺带提及"目标银行(mention_density 很低, 例如一篇宏观金融综述文章里仅有一句话点名该行), 它在 pos_count_full 里仍与"通篇聚焦讨论"该银行的正面深度报道等权计 1, 而在 pos_count_vw_full 里前者的贡献会显著小于后者, 从而更贴近前述提及密度暴露加权思路强调的"暴露强度而非二元提及"这一构念。研究者在使用计数型情感测度作为回归变量时, 若担心"顺带提及"文章稀释了真正聚焦报道的信号强度、导致等权计数低估了真实的媒体聚焦效应, 应同时报告 pos_count_full 与 pos_count_vw_full 两个口径的结果作为敏感性检验; 又因 vw 版本是连续值加权和而非整数篇数, 在计量策略上更接近连续型强度测度而非严格意义上的计数变量, Cohn, Liu & Wardlaw (2022, JFE) 关于计数数据回归模型选择的建议主要适用于未加权的 pos_count_full, 而非本列。

## VAR: pos_count_vw_ss

【变体差分】
本列是 pos_count_ss 的提及密度加权版本: 以 ss (同句共现) 轨文本判定的逐篇正面指示 is_positive_ss 乘以 mention_density 权重后, 在 bank-year 层面求和; 若某篇文章因缺少银行∧金科同句共现而触发 content_ss 回退, 其情感判定与权重计算均在回退后的全文口径上进行, 与 pos_count_ss 的回退处理规则完全一致。由于 ss 轨本身已经是三轨中构造判据最严格的一支(要求银行与金科词同句共现), 再叠加提及密度加权后, 本列刻画的是"银行与金科话题紧密同现、且该文章高度聚焦谈论该银行"的正面报道强度, 是本家族六列中构念含义最集中、但样本覆盖(尤其在 dev T=2 两年小样本上)最稀疏的一列——同句共现本身是一个较严苛的筛选条件, 叠加密度加权后单篇文章的贡献进一步被拉开差距, 容易在样本量不足的 bank-year 格上出现零值或近零方差, 使用时应留意其退化风险, 并优先在生产语料 (T=19, 约 1,819 万条全量) 规模下解读, 不宜仅凭本机 dev T=2 试跑结果下结论。使用者应将本列与 pos_count_ss(等权版本)及 pos_count_vw_full/pos_count_vw_ctx(更宽轨道的加权版本)联合解读, 六者(连同其等权对应列)互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 过度识别检验框架。

<!-- rendered-citations:begin -->
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
<!-- rendered-citations:end -->
