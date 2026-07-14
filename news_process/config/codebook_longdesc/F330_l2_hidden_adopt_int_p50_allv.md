---
family_id: F330
columns:
- hidden_adopt_int_p50_allv
- hidden_adopt_int_p50_allv_ctx
- hidden_adopt_int_p50_allv_ss
unit: 占比 (bank-year 内"隐性采纳"分类文章数 / 已测量文章数, ∈[0,1], 无覆盖→NaN)
formula: 'per-article 双轴分类: freq=fintech_intensity_score(int 轨), sim=policy_cosine_sim_allv(全语料静态锚点); 年内阈值=freq/sim 各自的 P50 分位数; Hidden ⟺ (freq < P50_freq) AND (sim >= P50_sim) AND freq,sim 双双非缺失; 未测量(freq 或 sim 缺失)→ NaN, 不计入分子分母。bank-year 聚合 = groupby(target_bank, year) 对逐篇 Hidden 指示做 mean (NaN 自动跳过, 分母=已测量篇数)。'
producer: pipeline\panel\runner.py::_classify_policy_quadrants (核心分类原语) + 外层 anchor/track/percentile 三重循环 (L1997-2104)
upstream:
- 15_fintech_intensity.parquet (fintech_intensity_score, 词频侧 Track-int 输入)
- 16_article_policy_alignment.parquet (policy_cosine_sim_allv*, 相似度侧全语料静态锚点输入)
- 24_herd_decay_processor.parquet (LLM-verified 语义精筛集, 经 _filter_to_verified_universe semi-join 收敛聚合域)
citations:
- doi: 10.1016/j.intfin.2026.102306
  type: journal
  authors: Alfhaili, F. A., Bakoush, M., & Wolfe, S.
  year: 2026
  title: Investing in fintech equity and bank innovation
  venue: Journal of International Financial Markets, Institutions and Money
  vol: '108'
  pages_or_artno: '102306'
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
- doi: 10.1016/j.econmod.2023.106445
  type: journal
  authors: Fang, Y., Wang, Q., Wang, F., & Zhao, Y.
  year: 2023
  title: 'Bank fintech, liquidity creation, and risk-taking: Evidence from China'
  venue: Economic Modelling
  vol: '127'
  pages_or_artno: '106445'
- doi: 10.1016/j.iref.2021.03.009
  type: journal
  authors: Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J.
  year: 2021
  title: Does fintech innovation improve bank efficiency? Evidence from China's banking industry
  venue: International Review of Economics & Finance
  vol: '74'
  pages_or_artno: 468-483
- doi: 10.1006/jfin.2000.0282
  type: journal
  authors: Boot, A. W. A.
  year: 2000
  title: 'Relationship banking: What do we know?'
  venue: Journal of Financial Intermediation
  vol: '9'
  issue: '1'
  pages_or_artno: 7-25
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: "The symbolic management of stockholders: Corporate governance reforms and shareholder reactions"
  venue: Administrative Science Quarterly
  vol: 43
  issue: 1
  pages_or_artno: 127-153
new_dois: []
---

## CORE

【构念与来源】
本家族是"银行金科新闻四象限采纳分类"体系里的一格: Hidden Adoption (隐性采纳)。四象限体系把每篇通过银行∧金科共现硬过滤且经 stage 21 LLM 语义精筛验证的文章, 按两根轴各自的年内分位数切成高/低两档, 交叉出四个格子: Token (词频高、政策相似度低——"喊口号")、Hidden (词频低、政策相似度高——"闷声干大事")、Substantive (词频高、相似度都高——"言行一致的实质采纳")、Irrelevant (两者皆低)。本家族对应 Hidden 格: 一篇报道里银行提及金科词汇的强度并不突出, 但该文章的语义内容与官方金融科技政策文本的余弦相似度却排在当年前列——文章"不太谈金科", 却在"做金科该做的事", 这正是隐性/低调式技术采纳在文本上的印记, 呼应组织采纳文献里"言行分离"(decoupling) 与信息不对称下的隐性信号传递: 银行未必主动对外宣传其金融科技战略响应, 但战略文本本身与监管/产业政策议程的贴合度已经暴露了实际动作。构念上, 本家族衡量的不是"报道量"而是"报道质地与政策议程的隐性对齐强度", 分子分母定义在文章层面, 聚合到 bank-year 层面输出为占比。
【方法学与计算】
两根轴分别取自两条独立上游管线: 纵轴 (词频侧) 由 stage 15 fintech_intensity 输出的 fintech_intensity_score 承担——这是"int"轨的定义, 区别于同一家族体系内以 AC 自动机去重关键词计数 fintech_distinct_keywords 为词频侧的"kw"轨 (两轨互为稳健性并排, 不分主次, 见下)。横轴 (相似度侧) 取 stage 16 article_policy_alignment 产出的 policy_cosine_sim_allv——"allv"后缀 (all-vintage anchor, 2026-06-21 引入) 指该相似度不是用逐年滚动更新的政策文本锚点向量计算, 而是用横跨全部年份静态聚合的锚点向量计算, 是主轨 (无 allv 后缀、逐年 vintage 锚点) 的稳健性孪生: 两个锚点口径各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 或同一回归的同侧协变量。年内阈值用 pandas groupby('year') 对 freq 列与 sim 列各自做 quantile(0.5) 变换 (即 P50, 中位数分裂), 得到逐年、逐轨的动态阈值而非全样本固定阈值, 使得分类对不同年份的整体报道强度/政策贴合水平漂移具鲁棒性。分类判据要求 freq 与 sim 同时非缺失 (measured = notna & notna) 才参与判定, 任一缺失的文章在该格子指示列上记为 NaN 而非归入"低"档——这是刻意设计 (fix omni-g-runner-03/g-runner-11, 2026-06-11): 早期实现把"未测量"误判为"低于阈值", 会把 stage 15/16 未成功度量的文章系统性地错误分派进 Token 格并污染分母。聚合口径遵循 F3 红线 (Allison 2001 缺失数据处理原则; Heckman 1979 选择偏差): 一个 bank-year 若全年无可测量文章, 输出 NaN 而非填 0, 因为"0 占比"与"未测量"是不同的语义, 早期实现 fillna(0.0) 曾把约三成行注入伪零值污染双向固定效应估计。聚合口径先经 _filter_to_verified_universe 把候选集 (stage 14 规则预筛) 收敛到 stage 24 herd_decay 输出的 LLM 语义精筛验证集 (与全留篇门控 full-only 口径一致, 2026-06-29), 再按 (target_bank, year) 分组取该文章级指示列的均值——由于 pandas 的 mean 默认跳过 NaN, 分母天然等于该 bank-year 内"两轴均已测量"的文章数, 而非该行全部报道数。
【文献定位】
词频-语义双轴分类范式呼应"言"(talk) 与"行"(walk) 分离的组织采纳/合规文献传统, 也呼应银行与金融科技企业关系中的信息不对称与关系型银行业务研究——Boot (2000, Journal of Financial Intermediation) 系统阐述了银行凭借私有信息积累与关系专有资本获得信息优势的机制, 本家族用"低显性词频、高隐性政策相似度"刻画的正是这种私有/隐性信息优势在文本上的映射: 银行的金融科技战略响应未必表现为高频公开宣示, 而可能体现为内容与政策议程的深层贴合。中国情境下银行金科采纳与经营结果的关系已有直接实证支撑: Lee, Li, Yu & Zhao (2021, International Review of Economics & Finance) 发现金融科技创新显著提升中国银行业效率; Fang, Wang, Wang & Zhao (2023, Economic Modelling) 进一步证明银行金科采纳与流动性创造、风险承担存在系统性关联; Fang, Wang, Wang & Yuan (2024, International Review of Economics & Finance) 则表明媒体情感与银行系统性风险相关, 为本管线"媒体文本→银行行为代理变量"的构念路径提供直接的方法学先例; Alfhaili, Bakoush & Wolfe (2026, Journal of International Financial Markets, Institutions and Money) 研究银行金科股权投资与创新的关系, 说明银行采纳金融科技的渠道本身具异质性 (自建/投资/并购), 支持本家族"隐性采纳"作为独立于显性公告的采纳测度维度的构念效度。本家族「隐性采纳」构念的组织理论根基另有 Westphal & Zajac (1998, Administrative Science Quarterly) 的直接顶刊支撑: 该文系统论证公司治理改革中「象征性管理」(symbolic management) 与实质行动之间的脱耦 (decoupling) 现象, 揭示组织可对外释放与内部实际决策不完全一致的信号, 为本家族「报道量与政策贴合度分离」这一隐性采纳判据提供了组织社会学层面的顶刊理论依据。

## VAR: hidden_adopt_int_p50_allv

【变体差分】
本列是家族 canonical 主轨: 词频侧取 int 轨全文本口径 fintech_intensity_score (stage 15 对文章全文 content_full 计算的金融科技语义强度连续分), 相似度侧取全语料静态锚点 policy_cosine_sim_allv (无 _ctx/_ss 后缀, 对应 content_full 全文与政策全语料静态平均锚点的余弦相似度), 阈值取该年内两列各自的 P50 中位数, 判据双轴同时非缺失。三轨 (full/ctx/ss) 铁律下, 本列是 full 轨的隐性采纳占比——即在"标题+正文全文"这一文本窗口上, 词频强度落入年度后 50% 分位而政策相似度落入年度前 50% 分位的已验证文章占比。与同家族体系内 kw 轨 (hidden_adopt_kw_p50_allv) 相比, 本列词频侧换成连续强度分而非离散关键词计数, 对文本中金科语义密度的刻画更平滑, 二者互为稳健性并排, 不分主次, 禁止混入同一 over-identified 设定; 与非 allv 主轨 (hidden_adopt_int_p50, 若存在) 相比, 本列相似度锚点固定为全语料静态口径而非逐年滚动锚点, 用以检验"政策议程本身随年份变化"是否驱动了分类结果。实践含义上, 若某银行在某年被本列判为高隐性采纳占比, 意味着该行当年被验证留篇的报道整体上"少提金科热词、但内容贴近官方产业政策议程"的比例偏高, 可作为衡量该行是否倾向低调推进金融科技战略响应的代理变量, 供机制检验或异质性分组使用; 该占比列与 token_adopt_int_p50_allv、subst_adopt_int_p50_allv 共享同一年内阈值与同一分母口径 (已测量篇数)。需注意四象限体系在概念上有四格 (Token/Hidden/Substantive/Irrelevant, 后者对应 freq、sim 均低于各自 P50 的"两者皆低"格), 但 runner.py::_classify_policy_quadrants 及其外层聚合循环只落盘并聚合 Token/Hidden/Substantive 三个指示列, 从未计算或输出 Irrelevant 列。因此 token_adopt_int_p50_allv + hidden_adopt_int_p50_allv + subst_adopt_int_p50_allv 之和等于 1 − irrelevant_frac (Irrelevant 格在已测量样本中的占比), 而非恒等于 1; 仅当某 bank-year 内已测量文章恰好不存在 Irrelevant 格观测 (即该年内该行所有已测量文章的 freq、sim 至少有一项落在各自年度 P50 及以上) 时三者之和才会数值上等于 1。由于 Irrelevant 占比未落盘, 不能把"三者之和=1"当作落盘后的自我核验恒等式使用; 若要校验落盘正确性, 应转而核对"三者互斥"(同一文章在同一 anchor/track/percentile 组合下至多命中一格) 这一较弱、但确实成立的性质, 或另行从 freq/sim 原始列重算 Irrelevant 指示后再核验四者之和恒等于 1。

## VAR: hidden_adopt_int_p50_allv_ctx

【变体差分】
本列是 ctx 轨孪生: 相似度侧改用 policy_cosine_sim_allv_ctx (标题+实体窗口文本与全语料静态锚点的余弦相似度); 词频侧优先取同轨变体 fintech_intensity_score_ctx (若该列存在), 仅当 ctx 轨词频列缺失时才退回全文列 fintech_intensity_score (kw 轨的去重关键词计数属 track-agnostic 元数据, 常无 ctx 独立变体而复用 full 列, int 轨通常有独立 ctx 变体)。年内 P50 阈值仍分别对 ctx 轨的 freq、sim 两列独立计算, 不与 full 轨阈值混用。本列与 canonical (`hidden_adopt_int_p50_allv`) 及 ss 轨孪生共同构成三轨并排稳健性簇: 三者在同一年内可能因文本窗口不同而给出不同的隐性采纳占比, 三轨各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 设定或同一回归模型的同侧解释变量集合。ctx 轨聚焦银行与金科实体共现附近的局部窗口文本, 相较全文轨更能剥离与银行金科议题无关的段落噪声, 但也可能因窗口过窄而丢失文章整体论述的政策贴合线索。使用建议上, 若研究者担心长篇报道中夹杂的非金科段落 (如银行综合业绩通稿里顺带一句金科表述) 会稀释全文轨的相似度信号, 应优先参考本列作为稳健性检验; 反之若担心窗口截断丢失文章对政策议程的整体论证脉络, 则应以 canonical 全文轨为参照, 二者并列报告而非相互替代。本列与 canonical 列共享同一年内阈值计算口径 (各自对本轨的 freq/sim 独立取 P50), 而非共用 full 轨阈值, 因此即便同一篇文章在 full 轨与 ctx 轨的相似度数值不同, 判定结果也严格依据各自轨道内部的相对排位, 不存在跨轨阈值污染。

## VAR: hidden_adopt_int_p50_allv_ss

【变体差分】
本列是 ss (same-sentence) 轨孪生: 相似度侧改用 policy_cosine_sim_allv_ss (标题+银行∧金科同句共现窗口±N句的文本, N 由 config/filtering.yaml::context_window.ss_sentence_radius 决定, 默认1, 与 stage 13 硬过滤的 cooccurrence_filter.sentence_radius 是两个不同配置键); 词频侧优先取同轨变体 fintech_intensity_score_ss, 缺失时退回全文列。ss 轨回退语义镜像 ctx 轨: 若文章中不存在银行与金科词汇的同句共现, content_ss 退化为全文 body 且 ss_is_fallback=True, 此时该文章在 ss 轨的相似度/词频度量实质上退化为全文口径, 但仍与共享 n_articles 分母的其余 ss 轨列口径一致地参与年内 P50 分类。本列与 canonical、ctx 轨孪生共同构成三轨并排簇, 三者各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J。ss 轨是三轨中文本窗口最窄、语义噪声最低但覆盖率也最受限的一支——当银行与金科词未同句出现时, ss 轨实质上退化为 full 轨的重复测度, 因此三轨之间的分类差异在 ss_is_fallback 比例较高的样本区间会自然收窄, 解读时须结合该退化比例。本列的分析价值在于提供三轨中最严格的共现证据基准: 只有在同一句话内银行与金融科技词汇真正相邻出现的文章, 才在非回退状态下贡献真实的 ss 轨判定, 因此本列的隐性采纳占比可视为"排除长文本远距离偶然提及"后的保守估计, 与 canonical 全文轨、ctx 局部窗口轨共同构成从宽到窄的证据强度梯度, 三者并排报告有助于判断结论对文本窗口选择的敏感程度, 但任一单独轨道都不应被视为唯一"正确"口径。

<!-- rendered-citations:begin -->
Alfhaili, F. A., Bakoush, M., & Wolfe, S. (2026). Investing in fintech equity and bank innovation. Journal of International Financial Markets, Institutions and Money, 108, 102306. https://doi.org/10.1016/j.intfin.2026.102306
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Fang, Y., Wang, Q., Wang, F., & Zhao, Y. (2023). Bank fintech, liquidity creation, and risk-taking: Evidence from China. Economic Modelling, 127, 106445. https://doi.org/10.1016/j.econmod.2023.106445
Lee, C.-C., Li, X., Yu, C.-H., & Zhao, J. (2021). Does fintech innovation improve bank efficiency? Evidence from China's banking industry. International Review of Economics & Finance, 74, 468-483. https://doi.org/10.1016/j.iref.2021.03.009
Boot, A. W. A. (2000). Relationship banking: What do we know?. Journal of Financial Intermediation, 9(1), 7-25. https://doi.org/10.1006/jfin.2000.0282
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
<!-- rendered-citations:end -->
