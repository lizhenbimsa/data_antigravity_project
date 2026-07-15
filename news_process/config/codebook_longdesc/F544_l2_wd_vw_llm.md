---
family_id: F544
columns:
- sum_wd_vw_llm_ctx
- sum_wd_vw_llm_full
- sum_wd_vw_llm_ss
unit: 无量纲权重和 (提及密度 mention_density 的银行-年加总, 分母角色, 非语调本身)
formula: 'sum_wd_vw_llm{track} = Σ_i mention_density_i · 1[llm_vote_score{track}_i is not NA], 加总遍历该银行-年全部留存文章 i; 即"valid-mask 提及密度权重和" = 仅对三家 LLM 多数投票共识分数该轨非缺失的文章求提及密度之和'
producer: pipeline/panel/runner.py::_build_llm_valid_masked_weights (文章级 _wd_vw_llm{track} 掩码列, 步骤 3b 调用, weight=mention_density, wtag='vw', grp='llm', 判据列 llm_vote_score{track}) → pipeline/panel/encode.py::build_aggregation_dict (bank-year groupby sum, 列名 sum_wd_vw_{grp}{track}, encode-01 fix 段三轨×wtag×grp 循环注册)
upstream:
- "11_news_bank.py (mention_density 文章级来源: 目标银行提及次数密度)"
- "21_tone_llms.py (llm_vote_score{track} 三轨文章级共识评分: gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash 三家多数投票, prompt v8, temperature=0.0)"
- 14_materialize_ctx.py (content_ctx/content_ss 三轨文本物化, ctx/ss 轨 llm_vote_score 依赖此产物)
citations:
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: Wisdom of the silicon crowd; LLM ensemble prediction capabilities rival human crowd accuracy
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: 10.48550/arXiv.2502.18036
  type: arxiv
  authors: Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S.
  year: 2025
  title: 'Harnessing multiple large language models: A survey on LLM ensemble'
  venue: arXiv
- doi: 10.48550/arXiv.2307.12973
  type: arxiv
  authors: Plaza-del-Arco, F. M., Nozza, D., & Hovy, D.
  year: 2023
  title: 'Wisdom of instruction-tuned language model crowds: Exploring model label variation'
  venue: arXiv
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: 'The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms'
  venue: Communication Methods and Measures
  vol: '15'
  issue: '2'
  pages_or_artno: 121-140
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (sum_wd_vw_llm_full / _ctx / _ss) 与 sum_wd_vw_deepseekv4 (F541)、sum_wd_vw_gemini31 (F542)、sum_wd_vw_gpt54nano (F543) 四个家族结构完全平行, 唯一区别是本家族承载的不是任一单厂商模型的逐模型评分, 而是三家 LLM (gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash) 多数投票后的共识判据列 llm_vote_score{track}。名字拆解: sum(求和) _ wd(weight-denominator, 掩码后的权重) _ vw(value-weighted, 三种加权体系之一) _ llm(承载对象是三家投票共识, 而非单一厂商)。它本身不是独立构念测度, 而是面板层"提及密度加权语调" (Value-Weighted Tone) 计算链路中的纯记账辅助量, 是下游 llm_vote_tone_vw{track} = llm_vote_score_w_sum{track} / sum_wd_vw_llm{track} 这一 P1 主线 treatment 候选 (headline 共识 VW 语调) 的分母。分子 llm_vote_score_w_sum{track} 是 Σ(mention_density_i × llm_vote_score{track}_i), 只对共识评分非缺失的文章求和; 本家族三列是与之精确同域的分母: Σ mention_density_i, 同样只在共识评分非缺失的文章上累加。二者的"有效文章集合"逐位重合, 这是本家族存在的唯一理由。

llm_vote_score{track} 本身并非某一家模型的原始打分, 而是 stage 21 三家 LLM 各自独立评分后, 按多数投票规则汇总成的一个共识标量 (与 llm_vote_tone 系列的 headline 共识测度共享同一底层判据列)。当三家评分中出现有效多数 (至少两家给出可比判定) 时, llm_vote_score{track} 才有值; 若三家评分或投票聚合本身在该轨失败 (例如三家判断彼此矛盾且无法多数收敛, 或该轨全部三家评分均缺失), 则该行 llm_vote_score{track} 记为缺失, 本家族对应的掩码权重列在该行置 NaN 并被 groupby.sum 自动跳过。因此本家族测度的是"三家投票共识意义上的有效文章集合"的提及密度加总, 与 F541/F542/F543 分别测度的是"某一家单厂商模型意义上的有效文章集合", 二者判据列不同、有效文章集合原则上也不完全重合 (投票共识的有效性判据比单厂商更严, 依赖三家结果的可汇总性, 因此 sum_wd_vw_llm{track} 的有效文章数一般不高于任一单厂商家族的对应值)。

提及密度 (mention_density) 度量一篇报道对目标银行的关注强度 (通常正比于该银行名称/别名在文中出现次数相对文章长度的密度), 源自 Hassan et al. (2019, QJE) 政治风险文本暴露度量传统与 Sautner et al. (2023, JF) 气候风险暴露度量传统所共享的"提及密度加权"范式: 与其把每篇报道等权计入语调均值, 不如让"更聚焦讨论该银行"的报道拿到更大权重, 从而让 VW 语调比简单算术平均更贴近"该银行在媒体叙事中的实际语调暴露"。三家投票共识是 P1 主线的 headline treatment 候选 (`llm_vote_tone_full`), 与三家各自独立保留的逐模型语调轨 (F541/F542/F543 承载的三个单厂商家族) 互为跨厂商稳健性佐证——共识轨给出"多数意见", 逐模型轨给出"是否存在厂商特异性偏误", 二者定位互补而非互斥。本家族因此在整个 VW 权重族群里扮演"共识轨的分母", 与另外三个单厂商家族的分母各自独立核算, 互不依赖、互不借用。

【方法学与计算】
计算发生在两个阶段。第一阶段是文章级掩码构建 (pipeline/panel/runner.py 步骤 3b, 函数 _build_llm_valid_masked_weights): 对每条轨 track ∈ {_full, _ctx, _ss}, 先取文章的提及密度权重 w = mention_density (缺失填 0), 再取该轨的共识判据列 llm_vote_score{track}, 用 w.where(llm_vote_score{track}.notna()) 生成掩码后的权重列 _wd_vw_llm{track}: 共识评分有效的文章保留其提及密度权重, 共识评分无效 (三家投票该轨未能收敛到可用判定) 的文章权重置为 NaN。同一函数在同一次调用内还并行为三家单厂商模型 (LLM_MODELS 循环) 及概率化评分 llm_prob_score{track} 各自生成独立的掩码权重列 (_wd_vw_{short}{track} / _wd_vw_prob{track}), 但这些属于姊妹家族的产物, 与本家族 grp='llm' 分支各自独立、互不干扰。第二阶段是银行-年聚合 (pipeline/panel/encode.py::build_aggregation_dict, encode-01 fix 段三轨×wtag×grp 循环注册聚合入口): 对每个 (target_bank, year) 分组, 对 _wd_vw_llm{track} 做 groupby.sum, sum 对 NaN 自动跳过, 得到 sum_wd_vw_llm{track} = 仅在共识评分该轨有效的文章集合上求提及密度之和。

这一"掩码分母"设计源自一次针对性修复 (encode.py 内部注释标注为 encode-01, 2026-06-10 metric-audit): 若直接用物理分母 (Σ 全部文章的提及密度权重, 不管共识评分是否有效) 去除以"仅有效文章参与"的分子, 则随着三家投票判断失败/无法收敛占比升高, 加权语调会被系统性地拉向 0 —— 因为分母把"无共识判断"的文章也算作贡献了权重, 相当于隐含把这些文章的语调计为 0。掩码分母修正后, 分子分母的文章集合严格重合, VW 语调退化为"对共识有效判断文章的提及密度加权平均", 不再受判断失败率的机械污染。这一逻辑仅施于 LLM 族 (词典族逐轨评分结构性无缺失, 因 stage 13 已做共现硬过滤 + prepend_title 拼接, 存活文章必含可评分 token; BERT 族存在推理失败哨兵 NaN, 掩码化根治被列为 DEFER 到未来 M0/golden 重生窗口的既知缺口, 现行防线是 runner 输入端的 infer_failed 观测闸)。

三轨 full/ctx/ss 各自独立掩码、独立聚合: full 轨用标题+正文, ctx 轨用标题+实体窗口, ss 轨用标题+银行∧金科同句±N窗口 (窗口半径见 config/filtering.yaml::context_window.ss_sentence_radius)。三轨之间没有借用关系——某篇文章在 full 轨共识评分有效, 不代表它在 ctx 或 ss 轨也有效, 因为三家 LLM 在 ctx/ss 轨的评分建立在各自物化的 content_ctx / content_ss 文本之上, 每条轨独立跑 stage 21 推理、独立汇总投票。ss 轨遵循与 ctx 轨镜像的回退语义: 若某篇文章不存在"银行与金科词同句共现", content_ss 退化为全文正文 (ss_is_fallback=True), 但这不改变本家族的计算逻辑——回退只影响喂给三家 LLM 的文本内容, 不改变"共识评分是否非缺失"这一掩码判据本身。留篇门控口径 (2026-06-29 起) 为 full-only: 一篇报道是否计入"银行金科报道"行宇宙, 只看 llm_verified_full==True; ctx/ss 轨的评分与聚合是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集合的子集, 但 per-track 列仍照常各自计算, 与本家族的掩码/聚合逻辑不冲突。

【文献定位】
本家族本身不是一个"测度构念", 而是三条正交稳健性梯子 (三轨 / VW-MW-HW 三套加权 / 共识-单厂商互证) 交汇处的记账基础设施, 其学术定位落在两条文献脉络上。第一条是提及密度/暴露度加权范式, 与 Hassan et al. (2019, QJE) 及 Sautner et al. (2023, JF) 一脉相承——核心思想是"报道对目标实体的聚焦程度应作为语调贡献的权重", 而非对所有报道一视同仁, 本项目将该范式套用于三家 LLM 投票共识轨与三条逐模型轨, 结构完全平行。第二条是"多 LLM 互证/wisdom of crowd"文献脉络, 直接支撑本家族所承载的"三家投票共识"这一设计。Gilardi, Alizadeh & Kubli (2023, *Proceedings of the National Academy of Sciences*) 证明 LLM 在文本标注任务上可比肩甚至超越众包人工标注员, 为"用 LLM 替代/补充人工标注做大规模情感分类"这一路线提供了效度依据。Schoenegger, Tuminauskaite, Park, Bastos & Tetlock (2024, *Science Advances*) 进一步论证多个 LLM 集成 (ensemble) 的预测准确度可媲美人类群体智慧 (wisdom of crowd), 直接呼应本家族"三家 LLM 各自独立打分、再以多数投票汇总为共识"的架构选择——共识轨的价值恰恰来自 ensemble 效应, 而非任一单一模型的优越性。Chen et al. (2025, arXiv) 对"利用多个大语言模型"这一 LLM ensemble 方法论做了系统综述, 梳理了投票聚合、加权集成、级联等多种跨模型汇总策略在准确度与鲁棒性上的权衡, 为本项目采用多数投票 (而非其他集成规则) 汇总三家评分提供了方法论谱系定位。Plaza-del-Arco, Nozza & Hovy (2023, arXiv) 揭示不同指令微调 LLM 之间在标签判断上存在系统性变异, 这正是本项目坚持"共识轨与逐模型轨并排、禁止把二者混入同一 over-identified 检验"这一铁律的方法学动因——模型间分歧本身是需要被观测和披露的信息, 共识只是对分歧的一种(而非唯一)汇总方式, 逐模型轨仍需独立保留以便审视共识背后的分歧结构。van Atteveldt, van der Velden & Boukes (2021, *Communication Methods and Measures*) 系统比较了人工标注、众包、词典法与机器学习(含早期 LLM 前身)在情感分析效度上的差异, 为本项目同时并行词典法 (dict 族)、LLM 法 (三家投票+逐模型)、BERT 法 (三模型) 三重互证架构提供了跨方法论证依据。

⚠ 口径铁律: sum_wd_vw_llm_{full,ctx,ss} 三轨、以及三家投票共识 (本家族) 与三条对应单厂商家族 (F541 deepseekv4 / F542 gemini31 / F543 gpt54nano) 均各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 检验; VW/MW/HW 三套加权体系(提及密度/媒体权威/跟风衰减)同样各自独立、不可交叉混用同一工具变量检验。三轨口径与留篇门控口径 (full-only, 2026-06-29) 独立正交, ss 轨回退语义严格镜像 ctx 轨。

## VAR: sum_wd_vw_llm_full

【变体差分】
本列是 full 轨 (标题+全文正文) 上的掩码提及密度权重和: 对每个银行-年, 遍历该银行-年全部留存文章, 仅累加那些 llm_vote_score_full 非缺失的文章的 mention_density, 缺失 (该文章在 full 轨上三家 LLM 投票未能收敛为可用共识, 例如接口失败、内容不满足评分前提、或三家判断彼此矛盾无法多数聚合) 的文章权重记为 NaN 并被 groupby.sum 自动跳过。full 轨是留篇门控的门控轨——一篇报道是否被判定为"一篇银行金科报道"、从而进入 24_herd_decay_processor 之后的 df_exploded 主行宇宙, 完全取决于 llm_verified_full == True; 因此 full 轨上的掩码有效文章集合规模通常最大、也最贴近该银行-年"新闻覆盖总量"的真实提及密度分布, 三轨之中 full 轨的掩码有效率 (有效文章数 / 留存文章数) 一般也最高, 因为它面对的原始文本信息量最完整, 不存在实体窗口截取或同句共现收窄导致的信息缺失风险。本列是 llm_vote_tone_vw_full = llm_vote_score_w_sum_full / sum_wd_vw_llm_full 这一 P1 主线候选测度 (三家投票共识提及密度加权语调) 的分母, 与该银行-年简单算术平均语调 (等权不掩码不加权)、媒体权威加权 llm_vote_tone_mw_full、跟风衰减加权 llm_vote_tone_hw_full 三套加权互为并列稳健性轨, 各自的掩码分母独立核算(权重不同, 掩码判据均依据 llm_vote_score_full 有效性但作用于不同权重序列), 互不借用彼此的分母。本列亦与三条单厂商对应量 sum_wd_vw_deepseekv4_full (F541)、sum_wd_vw_gemini31_full (F542)、sum_wd_vw_gpt54nano_full (F543) 并列, 四者各自独立核算掩码有效集合(共识判据比单厂商判据更严, 有效文章集合原则上更小或相等), 互为跨厂商/跨聚合口径的稳健性佐证, 不应被合并进同一识别方程。

## VAR: sum_wd_vw_llm_ctx

【变体差分】
本列是 ctx 轨 (标题+目标银行实体窗口截取正文) 上的掩码提及密度权重和, 计算逻辑与 full 轨完全平行但作用于独立的文章子集与独立的判据列: 掩码判据换成 llm_vote_score_ctx 是否非缺失, 累加对象仍是 mention_density (提及密度权重本身是 track-agnostic 的文章级属性, 不随文本截取轨道改变, 改变的只是"哪些文章在该轨上有有效共识评分"这一掩码)。ctx 轨在 2026-06-29 起的留篇门控口径下被降级为 conditional-on-full 的稳健性测度轨: 行宇宙是 full 轨留篇集合的子集, 但 ctx 轨三家评分与投票聚合依旧对该子集内每篇文章独立执行——某篇文章即便通过了 full 轨门控, 若其 ctx 轨三家评分因内容截取后信息不足等原因未能汇总出有效共识, 仍会被本列的掩码逻辑排除在分母之外。本列服务 llm_vote_tone_vw_ctx, 与 full/ss 两轨的对应量互为稳健性并排, 用以检验"把评分依据从全文收窄到目标银行实体窗口附近文本"是否系统性改变三家 LLM 投票共识提及密度加权语调的结果; 三轨结果的一致性(或差异)本身构成对语调测度稳健性的证据, 不应被合并进同一识别方程。frac_ctx_fallback 是 bank-year 层面的诊断信号, 记录该银行-年"content_ctx 等价于 content_full"(实体窗口未命中回退) 的文章占比; 高值意味着 ctx 轨对该银行-年而言已退化为 full 轨的近似, 此时本列与 sum_wd_vw_llm_full 的数值也会趋同, 使用者可据此判断 ctx 轨稳健性检验的边际信息量。本列与三条单厂商对应量 sum_wd_vw_deepseekv4_ctx (F541)、sum_wd_vw_gemini31_ctx (F542)、sum_wd_vw_gpt54nano_ctx (F543) 并列, 均在 ctx 轨上各自独立核算掩码有效集合, 互为跨厂商稳健性佐证, 不应被合并进同一识别方程。

## VAR: sum_wd_vw_llm_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句±N窗口共现文本) 上的掩码提及密度权重和, 计算逻辑同样平行于 full/ctx 两轨, 掩码判据是 llm_vote_score_ss 是否非缺失。ss 轨的独有之处在于其底层文本本身带有回退语义 (镜像 ctx 轨): 若某篇留存文章不存在"目标银行与金科词在同一句 (±N 窗口) 内共现", content_ss 会退化为全文正文, 对应文章级标记 ss_is_fallback=True, 与 n_articles 分母共享同一批文章; 该回退只改变喂给三家 LLM 推理的文本内容, 不改变本列"共识评分是否非缺失"这一掩码逻辑本身——回退与非回退文章只要 llm_vote_score_ss 有效, 都会被计入本列的提及密度加总。若 FINTECH_AC (金科关键词自动机) 未构建 (None), 则 ss_is_fallback 对全体文章恒为 True, ss 轨优雅退化为与 full 轨内容趋同但仍独立评分核算的轨道。本列服务 llm_vote_tone_vw_ss, 是三轨稳健性梯子中最严格的"同句共现"判据分支, 用于检验将评分依据进一步收窄到"银行与金科词严格同句邻近"的文本片段后, 三家 LLM 投票共识的提及密度加权语调是否依然稳健; 与 full/ctx 两轨的对应分母各自独立 just-identified, 三者并排互证、不合并入同一工具变量检验。与 frac_ctx_fallback 镜像, frac_ss_fallback 记录该银行-年 content_ss 回退为全文的文章占比, 是判断 ss 轨稳健性检验边际信息量的诊断信号——高回退占比意味着该银行-年内"银行∧金科同句共现"稀少, ss 轨评分实质上多数建立在与 full 轨相同的文本上, 此时本列数值也会与 sum_wd_vw_llm_full 趋近。本列与三条单厂商对应量 sum_wd_vw_deepseekv4_ss (F541)、sum_wd_vw_gemini31_ss (F542)、sum_wd_vw_gpt54nano_ss (F543) 并列, 均独立核算 ss 轨掩码有效集合, 四者互为跨厂商稳健性佐证, 不合并进同一识别方程。

<!-- rendered-citations:begin -->
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd; LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Chen, Z., Lu, X., Li, J., Chen, P., Li, Z., Sun, K., Luo, Y., Mao, Q., Li, M., Xiao, L., Yang, D., Huang, X., Ban, Y., Sun, H., & Yu, P. S. (2025). Harnessing multiple large language models: A survey on LLM ensemble. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2502.18036
Plaza-del-Arco, F. M., Nozza, D., & Hovy, D. (2023). Wisdom of instruction-tuned language model crowds: Exploring model label variation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2307.12973
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
<!-- rendered-citations:end -->
