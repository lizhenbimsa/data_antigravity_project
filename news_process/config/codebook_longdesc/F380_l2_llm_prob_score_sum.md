---
family_id: F380
columns:
- llm_prob_score_sum_ctx
- llm_prob_score_sum_full
- llm_prob_score_sum_ss
unit: 无量纲得分之和 (逐篇 Logit-to-Score 概率差 P(正面)-P(负面) ∈ [-1,+1] 的 bank-year 求和, 值域随留篇篇数扩张, 无固定上下界)
formula: 'llm_prob_score_sum{track} = Σ_{article ∈ bank-year} llm_prob_score{track}; 其中 llm_prob_score{track} = P(正面|article,track) - P(负面|article,track) ∈ [-1,+1], 三家 LLM (gpt54nano/gemini31/deepseekv4) 各自出票后按家族既定聚合规则折算为单一逐篇概率差 (镜像 avg_llm_prob_score{track} 的分子来源, 聚合算子由 mean 换为 sum); track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\encode.py (agg[f''llm_prob_score_sum{track}''] = (f''llm_prob_score{track}'', ''sum''), 三轨循环 L1189-L1195); 上游逐篇概率打分产自 stage 21 (tone_llms.py) 情感 LLM 输出; pipeline\panel\export.py (Sum Prob Score 面板列标签映射, L1359-L1360, 仅登记 full/ctx 两轨字符串标签, ss 轨由第三轨机械派生循环补全)
upstream: []
citations:
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: 'Large Language Models: An Applied Econometric Framework'
  venue: arXiv preprint (NBER Working Paper No. 33344)
- doi: 10.1073/pnas.2308950121
  type: journal
  authors: Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J.
  year: 2024
  title: 'GPT is an Effective Tool for Multilingual Psychological Text Analysis'
  venue: Proceedings of the National Academy of Sciences
  vol: '121'
  issue: '34'
  pages_or_artno: e2308950121
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: 'When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks'
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: 'FinBERT: A Large Language Model for Extracting Information from Financial Text'
  venue: Contemporary Accounting Research
  vol: '40'
  issue: '2'
  pages_or_artno: 806-841
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
new_dois: []
---

## CORE

【构念与来源】
llm_prob_score_sum 家族刻画的是银行-年度层面「LLM 情感强度总量」的一种非均值化聚合方式: 对某银行在某年内被留篇 (full-only 门控, 见下) 的全部报道逐篇计算 llm_prob_score = P(正面) - P(负面) ∈ [-1, +1], 再在 bank-year 单元内求和, 而非取均值。这一构念的方法学立场与 Ludwig, Mullainathan & Rambachan (2025, NBER Working Paper) 提出的「LLM 应用计量框架」相呼应: 与传统词典法或离散三分类投票不同, LLM 被要求(或经由概率化 prompt 设计)对每篇文章的语气给出可解释为伪概率的连续打分, 从而把情感强度从粗粒度的 {正/负/中} 三值判别升级为区间连续量, 兼容更细的语气强弱梯度。producer 侧的实现位于 pipeline/panel/encode.py 的面板聚合循环 (三轨 for 循环 L1189-L1195), 逐篇概率分值 llm_prob_score{track} 在 stage 21 (tone_llms.py) 情感 LLM 阶段产出后随文章级 parquet 落盘, 面板层仅做 groupby(bank, year) 后的 sum 聚合, 不引入新的判定逻辑。
本家族与家族 avg_llm_prob_score (逐篇概率分的 bank-year 均值) 及 avg_llm_prob_score_std (标准差) 是同源姊妹测度: 三者共享同一份逐篇概率分子 llm_prob_score{track}, 区别仅在聚合算子 (sum vs mean vs std)。llm_prob_score_sum 的独特价值在于, 它同时携带了「语气强度」与「报道数量」两个维度的联合信息——一个银行即便平均语气温和 (mean 较小), 若该年被大量报道 (n_articles 大), sum 也会显著偏离 0; 反之报道稀少但语气极端的银行, sum 的绝对值反而可能较小。这种「强度 × 数量」耦合特性使 sum 版本天然适合作为「媒体关注度加权情感暴露」的代理变量, 在计量设定中与 n_articles 同时纳入可分离出「语气强度」的边际效应, 或者反过来把 sum 直接理解为规模不敏感的原始暴露量, 供后续按篇数标准化前的诊断/分解使用。这一「sum 版本承载规模信息、mean 版本承载纯语气信息」的区分, 也正是本项目在 encode.py 中为同一逐篇概率分子同时物化 mean/std/sum 三种聚合算子的设计初衷: 三者互为诊断组合而非相互替代, 研究者应按具体设定 (是否已单独控制 n_articles) 选择合适的聚合口径, 避免把「强度效应」误读为「数量效应」或反之。

【方法学与计算】
计算链条起点是 stage 21 (tone_llms.py) 的三家 LLM 情感投票: gpt-5.4-nano (gpt54nano)、gemini-3.1-flash-lite (gemini31, 经由 yunwu 中转)、deepseek-v4-flash (deepseekv4, 直连 api.deepseek.com)。三家除产出离散三分类多数票 (llm_vote_tone 系列) 外, 还各自贡献可折算为 P(正面)/P(负面) 的置信度/概率信号, 经家族既定的折算规则 (与 avg_llm_prob_score 家族共享同一折算函数, 非本家族独有创新) 汇总为逐篇标量 llm_prob_score{track} = P(正面) - P(负面), 天然落在 [-1, +1] 闭区间, 0 代表中性或正负抵消, 正值代表净正面语气强度, 负值代表净负面语气强度。encode.py 面板聚合阶段对该逐篇列在三轨 (full/ctx/ss) 下分别执行 groupby(bank, year)['llm_prob_score{track}'].sum(), 即 agg[f'llm_prob_score_sum{track}'] = (f'llm_prob_score{track}', 'sum')。sum 聚合本身对 NaN 采用 pandas 默认跳过语义 (缺失篇章不计入和, 不会因单篇缺失将整个 bank-year 置为 NaN), 但分母口径 (即该 bank-year 实际参与求和的有效篇数) 由并排存在的 n_articles / n_articles_llm_valid 系列列另行记录, sum 本身不显式携带分母信息, 需要研究者按需联表使用。
三轨 full/ctx/ss 分别对应三种不同的文章文本窗口: full = 标题+全文正文, ctx = 标题+银行/金科实体窗口截取, ss = 标题+银行∧金科同句 (±N 句半径, 默认 N=1) 窗口截取, 三者在 stage 14 (ctx_materializer) 统一物化, 情感相关阶段 (21/22/23/24) 均逐轨复算。本项目的留篇门控 (决定某篇文章是否计入某银行某年的「一篇银行金科报道」) 自 2026-06-29 起收紧为 full-only 口径: 仅以 llm_verified_full == True 作为唯一判据, ctx/ss 两轨降格为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集合的子集, 各轨列值仍按该子集独立计算 (即 llm_prob_score_sum_ctx / llm_prob_score_sum_ss 的求和范围与 llm_prob_score_sum_full 共享同一批文章, 但每篇文章各轨自身的概率打分因文本窗口不同而可能不同)。三轨之间是「各自 just-identified 并排、互为稳健性、不分主次」的关系: 三者应分别作为独立右手边/被解释变量代入回归, 严禁把 full/ctx/ss 三个 sum 混进同一个 over-identified 的 Hansen J 检验框架 (会导致工具变量过度识别检验的构念污染)。ss 轨的回退语义镜像 ctx: 当某篇文章不存在银行∧金科同句共现窗口时, content_ss 回退为全文 body (与 content_full 一致), 对应 ss_is_fallback=True, 该篇文章仍计入 n_articles 分母, 其 ss 轨的逐篇概率打分退化为等同于 full 轨的打分结果。
llm_prob_score_sum 家族与词典法/离散投票法的核心差异在于测度粒度与来源: 词典法 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran 等六词典) 依赖预先编制的正负词表与规则化打分, 是规则驱动、可完全复现、但对上下文语义与讽刺/否定结构不敏感的测度; 三家投票法 (llm_vote_tone) 是离散三分类多数决, 丢失了语气强弱的连续信息; 而 llm_prob_score 系列则试图在 LLM 语义理解能力与连续可加聚合之间取得平衡, 兼具语义敏感性与可加性 (sum/mean 在数学上有明确含义, 不像离散投票的众数难以跨篇累加)。

【文献定位】
概率化文本情感测度用连续量取代传统离散词典打分的方法学立场, 与 Ludwig, Mullainathan & Rambachan (2025, NBER Working Paper)「大语言模型应用计量框架」的系统性论述一致, 本家族的 llm_prob_score = P(正面) - P(负面) 构造正是这一「LLM 输出视为可加总连续测度」立场的具体实现, 仅将底层判分器由传统机器学习模型替换为大语言模型。用 LLM 而非传统监督模型执行文本标注/情感打分的合理性, 由 Rathje et al. (2024, PNAS)「GPT is an Effective Tool for Multilingual Psychological Text Analysis」关于 GPT 在多语言文本分析任务中匹配甚至超越人工标注基准的实证发现提供支持, 以及 Gilardi, Alizadeh & Kubli (2023, PNAS)「ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks」的跨任务系统性验证; de Kok (2025, Management Science) 进一步为会计/金融研究场景下使用生成式 LLM 做文本分析提供了方法学规范 (包括 temperature=0、prompt 冻结、缓存复现等实践, 与本项目 stage 21 的确定性锚点设计一致)。文本情感与信息内容之间的经典对照参照 Loughran & McDonald (2011, Journal of Finance) 关于金融文本词典法局限性的开创性发现, 该文指出通用情感词典在金融语境下存在系统性误判 (例如"liability"等中性词被通用词典误判为负面), 是本项目同时保留词典法与 LLM 法作为互补测度、而非用后者完全取代前者的方法学依据。基于 Transformer 架构的金融专用语言模型 (如 Huang, Wang & Yang 2023, Contemporary Accounting Research 提出的 FinBERT) 代表了介于传统词典法与通用 LLM 之间的第三条技术路线, 本项目 stage 23 (tone_berts) 的三家 BERT 模型族与 stage 21 的三家 LLM 族构成情感测度的双重技术路线互证, 与本家族的 LLM 概率打分共同服务于「情感测度三角」(dictionary / BERT / LLM) 的稳健性设计。

## VAR: llm_prob_score_sum_ctx

【变体差分】
本列是 llm_prob_score_sum 家族在 ctx 轨 (标题 + 银行/金科实体窗口截取正文) 下的求和值, agg 键为 llm_prob_score_sum_ctx = groupby(bank, year)['llm_prob_score_ctx'].sum()。行宇宙由 full-only 留篇门控决定 (llm_verified_full == True 的文章子集), 与 llm_prob_score_sum_full / llm_prob_score_sum_ss 共享相同的分母文章集合, 区别只在于逐篇打分所依据的文本窗口: ctx 轨仅截取标题加围绕目标银行/金科实体的局部窗口喂给三家 LLM 打分, 而非全文, 因此每篇文章在 ctx 轨下的 llm_prob_score 值可能与 full 轨不同 (局部窗口可能放大或削弱与实体直接相关句子的语气权重, 剔除了全文中与银行金科话题无关的段落对情感打分的稀释/干扰)。本列在计量设定中是 llm_prob_score_sum_full 的「互为稳健性」并排轨, 而非替代轨或次要轨: 若某一发现只在 full 轨显著而在 ctx 轨消失 (或反之), 应理解为测度对文本窗口选择的敏感性证据, 而非直接判定哪一轨"更对"。ctx 轨自身也有回退语义: 若某篇文章不存在可提取的银行/金科实体窗口, content_ctx 回退为全文 body, 该篇文章的 ctx 轨打分退化为等同 full 轨结果, 对应标记列 ctx_is_fallback=True, 该退化篇章仍正常计入 sum。使用本列须遵循三轨并排铁律: 不得将 ctx/full/ss 三个 sum 列同时作为工具变量塞入同一个 over-identified Hansen J 检验; 若需要联合两轨或以上信息, 应分别单独估计再做跨轨系数比较, 而非直接构造混合右手边。

## VAR: llm_prob_score_sum_full

【变体差分】
本列是 llm_prob_score_sum 家族的 full 轨版本 (标题 + 完整正文), agg 键为 llm_prob_score_sum_full = groupby(bank, year)['llm_prob_score_full'].sum(), 是本项目留篇门控唯一依据的文本窗口 (2026-06-29 起 llm_verified_full == True 为判定某篇文章是否算作"一篇银行金科报道"的唯一标准), 因此本列的求和范围即定义了整个家族三列共享的行宇宙/分母文章集合。相较 ctx/ss 两轨, full 轨不做任何窗口截取, 三家 LLM 直接对标题加全文正文打分, 优点是不丢失任何上下文信息 (包括可能影响语气判断的全篇论述逻辑、转折结构), 缺点是当文章篇幅较长且仅有小部分段落真正涉及目标银行与金科话题时, 全文语气可能被无关内容稀释或污染, 这正是 ctx/ss 两轨存在的方法学动机——作为并排稳健性轨检验结论是否对文本窗口选择敏感。作为三轨之中承担留篇门控职责的轨道, llm_prob_score_sum_full 在实证设定中通常被视为主测度 (P1 主线 treatment 变量族 llm_vote_tone_full 即以 full 轨为口径切换后的主轨), 但按项目铁律, 这不等于 full 轨在统计意义上"优先于"ctx/ss——三轨依然是各自 just-identified、互为稳健性、不分主次的并排关系, 只是 full 轨额外承担了行宇宙定义的职能性角色。使用者若在同一设定里同时纳入 full/ctx/ss 三个 sum 列做联合工具变量识别, 会违反本项目铁律 (禁止混入同一 over-identified Hansen J), 应改为三轨分别估计后比较系数符号与显著性的一致性作为稳健性证据。

## VAR: llm_prob_score_sum_ss

【变体差分】
本列是 llm_prob_score_sum 家族的 ss 轨版本 (标题 + 银行∧金科同句共现窗口, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句), agg 键为 llm_prob_score_sum_ss = groupby(bank, year)['llm_prob_score_ss'].sum()。ss 轨是三轨中文本窗口最严格的一支: 只有目标银行实体与金科关键词在同一句 (或其邻近半径句) 内共同出现的句子片段才被纳入喂给 LLM 打分的文本, 判定原语与 stage 13 硬过滤所用的邻近窗口判据 (has_bank_fintech_cooccurrence_within_radius) 属不同口径的姊妹函数 (extract_bank_fintech_cooccurrence, 严格同句), 两者刻意不互相复用以避免判据耦合。ss 轨的回退语义镜像 ctx 轨: 当某篇文章不存在满足严格同句共现条件的句子时, content_ss 整体回退为全文 body (与 full 轨内容一致), 对应标记列 ss_is_fallback=True, 该篇文章的 ss 轨逐篇概率打分因而退化为与 full 轨相同的数值, 但依然正常计入本列的 sum 聚合 (不被剔除、不单独设缺失, 与 n_articles 共享同一分母口径)。由于 ss 轨窗口比 ctx 轨更窄 (要求同句而非泛化实体窗口), 当银行与金科词汇在文章中虽有提及但分处不同句子/段落时, ss 轨相对 ctx/full 轨更容易触发回退, 在报道篇幅长、话题分散的样本中回退比例可能高于 ctx 轨, 这是解读 ss 轨与 full/ctx 轨系数差异时需要纳入考量的机制性特征, 而非测度本身的缺陷。本列同样受三轨并排铁律约束: 与 llm_prob_score_sum_full / llm_prob_score_sum_ctx 是互为稳健性、不分主次的并排关系, 严禁三者混入同一 over-identified Hansen J 识别框架。

<!-- rendered-citations:begin -->
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large Language Models: An Applied Econometric Framework. arXiv preprint (NBER Working Paper No. 33344) [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an Effective Tool for Multilingual Psychological Text Analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121
Loughran, T., & McDonald, B. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A Large Language Model for Extracting Information from Financial Text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
<!-- rendered-citations:end -->
