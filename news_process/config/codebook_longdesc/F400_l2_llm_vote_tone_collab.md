---
family_id: F400
columns:
- llm_vote_tone_collab_ctx
- llm_vote_tone_collab_full
- llm_vote_tone_collab_ss
unit: 语调得分 (连续, 约 [-1,1]; 三家 LLM 多数投票后按 bank-year 取均值)
formula: 'llm_vote_tone_collab{track} = mean_{i∈collab子样本}(llm_vote_tone{track}_i); 子样本判据 innovation_collab_mode_i = "_collab" (外部协同, 与 "_indep" 自主研发二分); 聚合发生在 pipeline\panel\encode.py 的 cm_agg groupby([target_bank, year])'
producer: pipeline\panel\encode.py
upstream:
- 21_tone_llms.py (三家 LLM 逐篇投票, gpt54nano/gemini31/deepseekv4)
- news_collab_mode 分类器 (innovation_collab_mode 二分类打标, indep vs collab)
- 40_panel_export_main.py (bank-year 聚合入口)
citations:
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: ChatGPT for textual analysis? How to use generative LLMs in accounting research
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority rules: LLM ensemble is a winning approach for content categorization'
  venue: arXiv
- doi: 10.1111/jpim.12710
  type: journal
  authors: Zhang, H., Ma, Z., Liang, X., & Garrett, T. C.
  year: 2024
  title: 'Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis'
  venue: Journal of Product Innovation Management
  vol: '41'
  issue: '4'
  pages_or_artno: 793-815
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: FEDS Working Paper No. 2026-020, Federal Reserve Board
new_dois: []
---

## CORE

【构念与来源】
本家族 llm_vote_tone_collab 是三家大语言模型多数投票语调分 (llm_vote_tone, P1 主处理变量 llm_vote_tone_full 的同一构念底座) 按报道所属"银行—金科互动模式"(innovation_collab_mode) 二分之一子样本重算的 bank-year 均值, 归属 P5 (bank_fintech_collab, Chesbrough 开放式创新框架) 论文族。上游 innovation_collab_mode 是逐篇二分类判据, 把每篇通过 stage 13 共现硬过滤且被 stage 21 情感 LLM 判定"确系一篇银行—金科报道"(留篇门控, 见下)的文章标为 "_indep"(银行自主研发金融科技, 如自建实验室、内部立项)或 "_collab"(银行与外部金科公司缔结合作关系, 如战略合作协议、股权投资、联合共建), 本列即取 collab 一侧子样本内 llm_vote_tone 的算术均值。三家 LLM (gpt-5.4-nano/gpt54nano、gemini-3.1-flash-lite/gemini31 两家走 yunwu、deepseek-v4-flash/deepseekv4 直连 api.deepseek.com) 各自对每篇报道独立打出语调判断, llm_vote_tone 是三家多数投票后的共识分, 即 P1 headline 处理变量的同一底座, 与三家 per-model 子测度 ({gpt54nano,gemini31,deepseekv4}_tone{track}) 互为跨厂商稳健性并排、不分主次。本列族只是把这一共识分限定在 collab 子样本内重新聚合, 不改变三家投票机制本身。llm_vote_tone_collab 与其镜像列 llm_vote_tone_indep (另一家族, 同一 encode.py 代码块内并列生成) 共同构成 P5 论文用于构造 tone_gap_indep_collab 派生 DV 的两个输入分量: tone_gap_indep_collab = llm_vote_tone_indep_full − llm_vote_tone_collab_full, 正值代表银行关于自主研发的报道语调比关于外部协同的报道更乐观, 是检验"开放式创新是否伴随媒体叙事上的情感折价"(open-innovation sentiment discount) 这一假说的核心构念。

【方法学与计算】
计算发生在 pipeline\panel\encode.py 的 groupby-agg 代码块 (源码摘录 L1968-L2028): 对 innovation_collab_mode 每个取值 (indep/collab) 各建一个聚合字典 cm_agg, 若三轨 (_full/_ctx/_ss) 下三家 LLM 的逐篇 score 列 {short}_score{track} 存在于该 collab_mode 子集 df_cm 中, 则以 (target_bank, year) 分组取均值写入 cm_panel, 随后左连接进主面板 panel。llm_vote_tone_collab{track} 属于这批被聚合的列之一 (虽摘录段落显式展示的是 per-model {short}_tone{track} 与 llm_prob_score{track} 两族, llm_vote_tone_collab{track} 与之同一代码路径、同一 cm_agg 循环产出, 是三家投票共识分而非 per-model 分)。聚合前有一道显式质量守门: n_articles_indep ≥ 5 且 n_articles_collab ≥ 5 时下游派生列 tone_gap_indep_collab 才计算 (源码注 fix(encode-02) 对齐 tech_app/sub_symb 同类最小样本门槛), 该守门作用于派生差值列而非本列自身, 但本列在小样本 bank-year (T=2 开发集常见) 上同样会因某一模式内文章数过少而呈现噪声更大的均值, 使用者应结合 n_articles_collab 分母判断可信度。分母恒等式遵循逻辑必然性口径 (v3.5.0 R6 修复): n_articles ≥ n_articles_indep + n_articles_collab, 差额是 collab_mode 判定本身为 NaN 的文章 (由 n_articles_cell_NA_full 兜底追踪), 而非严格拆分等式, 因为 LLM 对 collab_mode 维度的判定可能独立于 llm_verified_full 门控失败。留篇门控铁律 (2026-06-29 起, full-only): 一篇报道是否计入"一篇银行金科报道"只看 llm_verified_full == True, ctx/ss 是 conditional-on-full 的测度/稳健性轨, 行宇宙 = full 留篇集的子集; innovation_collab_mode 的判定同样建立在通过该门控的文章之上, 因此 llm_vote_tone_collab_ctx/_ss 与 _full 共享同一批"是否算作报道"的判定, 三轨仅在语调打分所读文本窗口 (全文/实体上下文窗/银行∧金科同句窗) 上分岔。

【文献定位】
本测度方法学谱系直接对应 LLM-as-annotator 文献: de Kok (2025, Management Science) 系统论证了 temperature=0、prompt 版本冻结、结果可缓存复现是会计/金融文本分析中使用生成式 LLM 的方法学范式, 本项目 stage 21 的 prompt v8 字节级冻结与 `_llm_cache.db` 确定性锚正是该范式的工程落地; Kamen & Kamen (2025) 论证多数投票集成 (majority-vote ensemble) 在内容分类任务上系统优于单模型, 为本项目采用三家 LLM 多数投票而非单一模型输出 llm_vote_tone 提供直接方法学支撑; Hansen (2026, FEDS WP) 讨论无金标准场景下 LLM 标注的验证策略 (κ/α 一致性设计), 呼应本项目 tone_validation.py 复用 Krippendorff's α 与重映射后 Cohen's κ 度量三家 LLM 间一致性的做法。构念层面, Zhang, Ma, Liang & Garrett (2024, JPIM) 对开放式创新前因后果做了近 20 年文献元分析, 是本列 indep/collab 二分类判据 (自主研发 vs 外部协同) 在 Chesbrough 开放式创新框架下的当代文献坐标; 该二分类本身的理论根基仍是 Chesbrough (2003) 提出的开放式创新概念——企业既可依赖内部知识独立创新, 亦可通过与外部行为体 (此处为金科公司) 的合作关系获取、整合外部知识, 本列即是媒体语调这一"软信号"维度上对该理论二分的经验度量。

## VAR: llm_vote_tone_collab_ctx

【变体差分】
本列是三轨 (full/ctx/ss) 之一的实体上下文窗轨: 语调打分所读文本为 content_ctx (标题 + 目标银行实体窗口), 由 stage 14 ctx_materializer 物化, 与 content_full (标题+全文正文) 及 content_ss (标题+银行∧金科同句±N窗) 并列。三轨在本列族内共享同一批"是否属于 collab 子样本"的判定 (innovation_collab_mode 二分类判据不随打分轨道切换), 差异只体现在三家 LLM 各自读到的文本窗口不同、因而三家投票共识分 llm_vote_tone_ctx 本身在 collab 子集上取均值的结果不同于 _full/_ss。三轨口径互为稳健性、各自 just-identified 并排、不分主次, 禁止把三轨列混进同一 over-identified Hansen J 设定。留篇门控为 full-only: 本列的行宇宙 (哪些 bank-year 有值) 由 llm_verified_full 决定, _ctx 打分本身不参与"是否留篇"的判定, 是 conditional-on-full 的测度/稳健性轨, 行宇宙严格是 full 留篇集的子集。使用场景上, ctx 轨相较 full 轨剔除了全文正文中与目标银行实体不直接相关的段落 (如同篇报道内提及的其他金融机构、宏观背景铺陈), 理论上能降低语调打分被无关段落稀释的风险; 但对 collab 子样本而言, 由于"外部协同"类报道往往整篇围绕合作双方展开 (合作公告、联合发布会通稿等文体特征), ctx 轨与 full 轨在此类报道上的文本重叠度通常高于一般报道, 因此本列与 llm_vote_tone_collab_full 在 collab 子样本内的相关性预期强于二者在全样本上的相关性, 但仍应作为独立稳健性轨对待、不应事先假定二者数值高度一致。

## VAR: llm_vote_tone_collab_full

【变体差分】
本列是三轨中的全文轨, 语调打分所读文本为 content_full (标题 + 全文正文), 是家族 canonical 轨、P5 论文主处理变量 llm_vote_tone_full 的同一底座在 collab 子样本上的重聚合, 也是留篇门控 (llm_verified_full) 的判定基准轨本身——即"一篇文章是否算作一篇银行金科报道"这一判定, 与本列打分所读的文本窗口是同一份 content_full。tone_gap_indep_collab (P5 派生 DV) 的两个输入分量 llm_vote_tone_indep_full 与 llm_vote_tone_collab_full 均取本轨, 而非 ctx/ss, 是因为主设定采用 full-only headline 处理变量口径 (2026-06-29 起); ctx/ss 两轨的同名差值仅作为 conditional-on-full 稳健性参照, 不构成 P5 主设定的一部分。本轨相较 ctx/ss 覆盖信息量最完整 (不裁剪、不受同句共现回退影响), 代价是可能混入与银行—金科互动本身无关的段落语调 (如报道正文顺带提及的宏观政策评论、行业整体走势), 使 collab 子样本上的均值相对 ctx/ss 更平滑但也更易受长文中不相关段落拖拽; 三轨互为稳健性并排, 使用者若观察到 _full 与 _ctx/_ss 在 collab 子样本上方向一致但幅度不同, 应理解为文本窗口宽窄差异的自然结果, 而非测度失效的信号。本轨在三轨中样本覆盖最完整、不受回退语义影响 (content_full 不存在"回退"这一概念, ss/ctx 的回退恰是退化为本轨), 因此在 P5 主设定中被选为构造 tone_gap_indep_collab 的输入分量, 兼顾了统计功效与解释一致性——回归系数可直接对应"整篇报道语调"而非某一裁剪窗口内的语调。



## VAR: llm_vote_tone_collab_ss

【变体差分】
本列是三轨中的同句窗轨: 语调打分所读文本为 content_ss (标题 + 银行实体∧金科关键词同句±N窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1)。回退语义镜像 ctx 轨: 若某篇报道中银行与金科词未曾在同一句中共现, content_ss 退化为全文 body (与 content_full 相同文本), 对应 ss_is_fallback=True, 与 content_ctx 的回退语义完全对称、共享 n_articles 分母口径。本列与 _full/_ctx 同样互为稳健性并排, 打分文本窗口最窄 (理论上信噪比最高但覆盖率随回退率上升而下降), 是否属于 collab 子样本仍沿用 innovation_collab_mode 判据, 不随打分轨道改变; 留篇门控同样为 full-only, 本列行宇宙仍以 llm_verified_full 为准。由于同句共现判据 (银行实体与金科词严格出现在同一句内, 判据原语与 stage 13 的邻近共现口径不同, 二者禁互相复用) 比 ctx 轨的实体窗口更严格, ss 轨在 collab 子样本上的有效样本 (非回退) 覆盖率预期低于 ctx 轨, 尤其当合作类报道的银行与金科词分处标题与正文不同句时更易触发回退; 使用者应结合 ss_is_fallback 占比判断本列在特定 bank-year 上是否已退化为等同 _full 轨的度量, 而非误判为独立的严格窗口信号。当回退比例较高时, llm_vote_tone_collab_ss 与 llm_vote_tone_collab_full 数值上会高度接近甚至一致 (因分子共享大量已回退全文文本), 此时不应将二者的高相关性解读为"严格同句窗轨获得独立验证", 而应先核查该 bank-year 内 collab 子样本的回退计数与共享 n_articles 分母。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority rules: LLM ensemble is a winning approach for content categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Zhang, H., Ma, Z., Liang, X., & Garrett, T. C. (2024). Antecedents and outcomes of open innovation over the past 20 years: A framework and meta-analysis. Journal of Product Innovation Management, 41(4), 793-815. https://doi.org/10.1111/jpim.12710
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
<!-- rendered-citations:end -->
