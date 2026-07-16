---
family_id: F175
columns:
- deepseekv4_pos_substvalid_count_ctx
- deepseekv4_pos_substvalid_count_full
- deepseekv4_pos_substvalid_count_ss
- gemini31_pos_substvalid_count_ctx
- gemini31_pos_substvalid_count_full
- gemini31_pos_substvalid_count_ss
- gpt54nano_pos_substvalid_count_ctx
- gpt54nano_pos_substvalid_count_full
- gpt54nano_pos_substvalid_count_ss
unit: 篇数 (bank-year 整数计数, count)
formula: "{llm}_pos_substvalid_count{track} = Σ_{文章∈bank-year} 1[ {llm}_score{track} > 0 ∧ innovation_substantiveness ∈ SUBST_VALID_LABELS ]"
producer: news_process/pipeline/panel/runner.py::_build_washing_indicators (篇章级 _svd_{llm}_pos) + _pool_svd_substvalid_counts (bank-year 聚合); 上游 news_process/pipeline/sentiment/tone_llms.py (per-model score 与实质性标签)
upstream:
- 21_tone_llms.parquet (per-model {llm}_score{track} 与 innovation_substantiveness 实质性标签)
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
citations:
- doi: 10.1002/smj.70023
  type: journal
  authors: Carlson, N. A., & Burbano, V.
  year: 2026
  title: "The use of LLMs to annotate data in management research: Foundational guidelines and warnings"
  venue: Strategic Management Journal
  vol: 47
  issue: 3
  pages_or_artno: 699-725
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework"
  venue: arXiv
- doi: 10.48550/arXiv.2509.08825
  type: arxiv
  authors: Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D.
  year: 2025
  title: "Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation"
  venue: arXiv
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
- doi: 10.2307/2393295
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1994
  title: "Substance and symbolism in CEOs' long-term incentive plans"
  venue: Administrative Science Quarterly
  vol: 39
  issue: 3
  pages_or_artno: 367-390
new_dois: []
---

## CORE

【构念与来源】
本家族记录的是"单一大语言模型判定为正面、且实质性维度已被有效测量"的银行年度报道篇数, 是一个 per-model (逐模型) 的计数测度, 覆盖三家模型 (deepseekv4 即 DeepSeek-V4 Flash、gemini31 即 Gemini-3.1-Flash-Lite、gpt54nano 即 GPT-5.4-nano) 与三条文本轨道 (full 全文、ctx 实体窗口、ss 银行金科同句窗) 的九个交叉单元。它并非一个独立回归的处理变量或结果变量, 而是"洗稿率"(washing ratio) 这一构念的同域分母 (same-domain denominator): 分子是"正面且象征性"的报道数, 分母是"正面且实质性已测量"的报道数, 二者共享同一个正面性门槛与同一批被有效解析的样本, 从而使比率的分子分母落在同一个可观测域内, 避免分类失败被误读为洗稿程度下降的假象。这一构念根植于 Westphal & Zajac (1994) 提出的实质性 (substance) 与象征性 (symbolism) 二分: 企业的战略宣示可以是真正落地的实质动作, 也可以是仅供外部合法性消费的象征姿态; 把银行金融科技报道按这一维度切分, 正是本项目 P3 (substance, Westphal & Zajac 谱系) 论文的测量核心。

【方法学与计算】
计算分两步。第一步在篇章级 (runner 的 washing 指示构造段) 生成布尔指示列 `_svd_{llm}_pos{track}`: 对每篇报道, 当该模型在该轨道上的 per-model 情感码 `{llm}_score{track}` 严格大于零 (即该模型独立判为正面, 缺席或解析失败经 fillna(0) 后不计入), 且该篇报道的实质性标签 innovation_substantiveness 落在有效标签集 SUBST_VALID_LABELS (即模型确实判出了"实质型"或"象征型"而非解析失败、NaN 转字符串后的 'nan' 恒为 False) 时, 指示取 1, 否则取 0。第二步在 bank-year 聚合 (`_pool_svd_substvalid_counts`): 按 target_bank×year 对篇章级指示求和, 更名为 `{llm}_pos_substvalid_count{track}`, 并命中 balance_panel 的计数零填规则 (零报道的银行年度补 0, 下游 `_safe_ratio` 遇零分母返回 NaN 而非除零)。需要强调的是: 逐模型差异只体现在"正面"这一侧 (由各家自己的 `{llm}_score` 门槛决定), 而"实质性已测量"这一侧用的是三家共识的 innovation_substantiveness 标签, 三个模型的计数因此共享同一个实质性掩码、仅在正面判定上分流。此设计使三家计数之间的差异纯粹归因于各家对正面语义的判别口径, 便于把跨模型分歧解释为测量者效应而非样本框差异。

【文献定位】
把同一批文本同时交给多家大模型逐条判定、再以各家结果并排比对, 是近年 LLM 文本测度可复现性文献的核心建议。de Kok (2025) 在 Management Science 系统论证了在会计与金融文本分析中使用生成式大模型的规范流程, 强调温度归零、提示词冻结与缓存复算以锁定确定性, 本项目 stage 21 的 temperature=0.0 与 prompt v8 字节冻结缓存正是这一范式的落地。Carlson & Burbano (2026, Strategic Management Journal) 为管理学研究中用 LLM 做数据标注给出基础准则与警示, 指出单一模型标注存在系统性偏差, 须以多模型交叉与人工校验作为效度背书, 直接支撑本家族逐模型并排存档的设计动机。Gilardi et al. (2023) 在 PNAS 上证明 ChatGPT 在文本标注任务上可超越众包工人, 但也提示不同模型、不同批次间存在不可忽视的标注方差; Ludwig, Mullainathan & Rambachan (2025) 与 Baumann et al. (2025) 进一步把这种"模型选择即研究者自由度"形式化为测量误差与"LLM hacking"风险, 论证跨模型稳健性检验的必要性。金融文本测度的经典锚点 Loughran & McDonald (2011, Journal of Finance) 与深度学习时代的 FinBERT (Huang, Wang & Yang, 2023) 则共同界定了从词典法到大模型法的测量谱系, 本家族的逐模型计数即处于该谱系的大模型端。方法学铁律上, 三家模型的逐模型计数各自 just-identified 并排, 互为稳健性、不分主次, 严禁把它们混进同一个 over-identified 的 Hansen J 检验; 同理三条轨道 (full/ctx/ss) 亦各自 just-identified, 互为稳健性, 禁混同一 over-identified Hansen J。

## VAR: deepseekv4_pos_substvalid_count_ctx

【变体差分】
本列固定模型为 deepseekv4 (DeepSeek-V4 Flash, 直连 api.deepseek.com, 与走 yunwu 的另两家不同源), 固定轨道为 ctx (上下文窗口)。ctx 轨的输入文本 content_ctx = 标题 prepend + 含目标银行句的 ±窗口片段 (proximity 口径, 只截取实体邻近上下文而非全文), 因此本列统计的是: 在仅给模型看"银行邻近上下文"时, DeepSeek-V4 独立判为正面、且该篇实质性维度被有效解析的银行年度报道数。相对家族口径, 本列的差分维度是"模型=deepseekv4"与"轨道=ctx"两者的交叉: 正面判定完全由 `deepseekv4_score_ctx > 0` 决定 (不参与三家投票, 缺席经 fillna(0) 视为非正面), 实质性侧沿用三家共识标签。与同模型的 full 列相比, ctx 只喂邻近上下文, 通常报道计数更少或语义更聚焦; 与 gemini31_ctx、gpt54nano_ctx 相比, 差异纯粹来自各家对正面语义的口径。ctx 轨为条件于 full 留篇集的稳健性轨道, 行宇宙是 full 留篇集的子集 (留篇门控 full-only, 2026-06-29 口径)。作为构念角色, 本列进入步骤 7h 洗稿率除法时充当同域分母, 其对应分子为 DeepSeek-V4 同轨的"正面且象征性"报道计数 (per-model pos_symb); 零报道的银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN 而非除零。per-model 降级独立: DeepSeek-V4 整体缺席只使本家族 deepseekv4 三轨计数缺失, 不连坐 gemini31 与 gpt54nano (非 co-primary 嵌入的 both-or-neither)。本列与家族内其余八列各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。

## VAR: deepseekv4_pos_substvalid_count_full

【变体差分】
本列固定模型为 deepseekv4 (DeepSeek-V4 Flash), 固定轨道为 full (全文)。full 轨输入 content_full = 标题 prepend + 全文正文, 是留篇门控的判定轨 (2026-06-29 full-only 口径: 一篇报道是否算入某银行金科宇宙, 只看 llm_verified_full == True), 因而在三轨中行宇宙最完整、计数通常最大。本列统计: 在给模型看完整标题加正文时, DeepSeek-V4 独立判为正面 (`deepseekv4_score_full > 0`)、且该篇 innovation_substantiveness 落在有效标签集的银行年度报道数。差分维度为"模型=deepseekv4"与"轨道=full"的交叉: 正面侧完全由该模型自身的 full 轨情感码决定, 不经三家多数投票; 实质性侧用三家共识的实质性标签作掩码, 与同族其余各列共享。作为该模型三轨中的基准轨 (full), 它是 ctx/ss 两条条件轨的上界宇宙来源。跨模型看, 本列与 gemini31_full、gpt54nano_full 构成同轨的逐模型稳健性三元组, 差异只反映各家正面判别口径。作为构念角色, 本列在步骤 7h 充当 DeepSeek-V4 full 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN。per-model 降级独立: DeepSeek-V4 缺席只使自身族计数缺失, 不连坐其余两家。三家逐模型计数、三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验。

## VAR: deepseekv4_pos_substvalid_count_ss

【变体差分】
本列固定模型为 deepseekv4 (DeepSeek-V4 Flash), 固定轨道为 ss (银行金科同句窗)。ss 轨输入 content_ss = 标题 prepend + 同一句内同时含目标银行与金融科技词的句子 ±窗口片段, 是三轨中语义最严格、要求银行与金科在同句共现的轨道。回退语义镜像 ctx: 当某篇报道无银行金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True (与 ctx 共享 n_articles 分母口径)。本列统计: 在仅给模型看银行金科同句片段 (或回退全文) 时, DeepSeek-V4 独立判为正面 (`deepseekv4_score_ss > 0`)、且实质性维度被有效测量的银行年度报道数。差分维度为"模型=deepseekv4"与"轨道=ss"的交叉: 正面侧由该模型 ss 轨情感码决定, 实质性侧沿用三家共识标签。相对同模型 full/ctx 列, ss 因同句约束通常样本更聚焦 (T=2 开发数据上 ss 轨可能出现零方差退化属预期, 生产 T=19 正常)。ss 为条件于 full 留篇集的稳健性轨道。作为构念角色, 本列在步骤 7h 充当 DeepSeek-V4 ss 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN 而非除零。per-model 降级独立: DeepSeek-V4 缺席只使自身族三轨计数缺失, 不连坐 gemini31 与 gpt54nano。本列与同族其余八列各自 just-identified 并排、互为稳健性, 禁混同一 over-identified Hansen J。

## VAR: gemini31_pos_substvalid_count_ctx

【变体差分】
本列固定模型为 gemini31 (Gemini-3.1-Flash-Lite, 经 yunwu 路由), 固定轨道为 ctx (上下文窗口)。本列统计: 在仅喂银行邻近上下文片段 content_ctx (标题 prepend + 含目标银行句 ±窗口) 时, Gemini-3.1 独立判为正面 (`gemini31_score_ctx > 0`)、且该篇 innovation_substantiveness 落在有效标签集的银行年度报道数。差分维度为"模型=gemini31"与"轨道=ctx"的交叉: 正面判定完全由 Gemini-3.1 自家的 ctx 轨情感码决定, 不进三家投票 (缺席或解析失败经 fillna(0) 视为非正面); 实质性侧沿用三家共识的实质性掩码, 与同族各列共享。与 deepseekv4_ctx、gpt54nano_ctx 并排, 本列的独有信息是 Gemini-3.1 对正面语义的判别口径在 ctx 轨上的落点 — 三家在同一批实质性样本上因正面阈值不同而产生的计数差异, 正是跨模型稳健性检验要利用的测量者效应。ctx 为条件于 full 留篇集 (full-only 门控) 的稳健性轨道。作为构念角色, Gemini-3.1 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 Gemini-3.1 ctx 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN。per-model 降级独立: Gemini-3.1 缺席只使自身族计数缺失, 不连坐 deepseekv4 与 gpt54nano (非 co-primary 嵌入的 both-or-neither)。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: gemini31_pos_substvalid_count_full

【变体差分】
本列固定模型为 gemini31 (Gemini-3.1-Flash-Lite), 固定轨道为 full (全文)。full 轨是留篇门控判定轨 (full-only, 2026-06-29), 行宇宙在三轨中最完整。本列统计: 在喂完整标题加正文 content_full 时, Gemini-3.1 独立判为正面 (`gemini31_score_full > 0`)、且该篇实质性维度被有效测量的银行年度报道数。差分维度为"模型=gemini31"与"轨道=full"的交叉: 正面侧完全由 Gemini-3.1 自身 full 轨情感码决定, 不经三家多数投票; 实质性侧用三家共识的 innovation_substantiveness 标签作掩码。作为 Gemini-3.1 三轨中的基准轨, 本列是该模型 ctx/ss 两条条件轨的上界宇宙来源。跨模型看, 本列与 deepseekv4_full、gpt54nano_full 构成同轨逐模型稳健性三元组: 三列共享同一实质性掩码, 差异只反映各家在完整文本下对正面语义的判别口径, 从而可诊断厂商级测量分歧。作为构念角色, Gemini-3.1 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 Gemini-3.1 full 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN 而非除零。per-model 降级独立: Gemini-3.1 缺席只使自身族三轨计数缺失, 不连坐其余两家。三家逐模型计数、三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验。

## VAR: gemini31_pos_substvalid_count_ss

【变体差分】
本列固定模型为 gemini31 (Gemini-3.1-Flash-Lite), 固定轨道为 ss (银行金科同句窗)。ss 轨输入 content_ss = 标题 prepend + 银行与金科同句共现片段 ±窗口; 无同句共现时回退全文 body 且 ss_is_fallback=True (回退语义镜像 ctx, 共享 n_articles 分母)。本列统计: 在仅喂银行金科同句片段 (或回退全文) 时, Gemini-3.1 独立判为正面 (`gemini31_score_ss > 0`)、且实质性维度被有效测量的银行年度报道数。差分维度为"模型=gemini31"与"轨道=ss"的交叉: 正面侧由 Gemini-3.1 的 ss 轨情感码决定, 实质性侧沿用三家共识标签。相对同模型 full/ctx 列, ss 因同句共现约束语义最严、样本最聚焦 (T=2 开发数据上 ss 轨可能零方差退化属预期, 生产 T=19 正常)。与 deepseekv4_ss、gpt54nano_ss 并排, 本列独有信息是 Gemini-3.1 在最严格同句语境下的正面判别口径。ss 为条件于 full 留篇集的稳健性轨道。作为构念角色, Gemini-3.1 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 Gemini-3.1 ss 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN。per-model 降级独立: Gemini-3.1 缺席只使自身族计数缺失, 不连坐 deepseekv4 与 gpt54nano。本列与同族其余八列各自 just-identified 并排、互为稳健性, 严禁混同一 over-identified Hansen J。

## VAR: gpt54nano_pos_substvalid_count_ctx

【变体差分】
本列固定模型为 gpt54nano (GPT-5.4-nano, 经 yunwu 路由), 固定轨道为 ctx (上下文窗口)。本列统计: 在仅喂银行邻近上下文片段 content_ctx (标题 prepend + 含目标银行句 ±窗口) 时, GPT-5.4-nano 独立判为正面 (`gpt54nano_score_ctx > 0`)、且该篇 innovation_substantiveness 落在有效标签集的银行年度报道数。差分维度为"模型=gpt54nano"与"轨道=ctx"的交叉: 正面判定完全由 GPT-5.4-nano 自家 ctx 轨情感码决定, 不进三家投票 (缺席或解析失败经 fillna(0) 视为非正面); 实质性侧沿用三家共识的实质性掩码。与 deepseekv4_ctx、gemini31_ctx 并排, 本列独有信息是 GPT-5.4-nano 对正面语义在 ctx 轨的判别口径 — 三家在同一批实质性样本上因正面阈值不同而生的计数差异, 即跨模型稳健性检验所利用的测量者效应。ctx 为条件于 full 留篇集 (full-only 门控) 的稳健性轨道, 行宇宙是 full 留篇集子集。作为构念角色, GPT-5.4-nano 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 GPT-5.4-nano ctx 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN。per-model 降级独立: GPT-5.4-nano 缺席只使自身族计数缺失, 不连坐 deepseekv4 与 gemini31 (非 co-primary 嵌入的 both-or-neither)。本列与家族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。

## VAR: gpt54nano_pos_substvalid_count_full

【变体差分】
本列固定模型为 gpt54nano (GPT-5.4-nano), 固定轨道为 full (全文)。full 轨是留篇门控判定轨 (full-only, 2026-06-29), 三轨中行宇宙最完整、计数通常最大。本列统计: 在喂完整标题加正文 content_full 时, GPT-5.4-nano 独立判为正面 (`gpt54nano_score_full > 0`)、且该篇实质性维度被有效测量的银行年度报道数。差分维度为"模型=gpt54nano"与"轨道=full"的交叉: 正面侧完全由 GPT-5.4-nano 自身 full 轨情感码决定, 不经三家多数投票; 实质性侧用三家共识的 innovation_substantiveness 标签作掩码。作为 GPT-5.4-nano 三轨基准轨, 本列是该模型 ctx/ss 两条条件轨的上界宇宙来源。跨模型看, 本列与 deepseekv4_full、gemini31_full 构成同轨逐模型稳健性三元组: 三列共享同一实质性掩码, 差异只反映各家在完整文本下对正面语义的判别口径, 可诊断厂商级测量分歧。作为构念角色, GPT-5.4-nano 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 GPT-5.4-nano full 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN 而非除零。per-model 降级独立: GPT-5.4-nano 缺席只使自身族三轨计数缺失, 不连坐其余两家。三家逐模型计数、三条轨道各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J 检验。

## VAR: gpt54nano_pos_substvalid_count_ss

【变体差分】
本列固定模型为 gpt54nano (GPT-5.4-nano), 固定轨道为 ss (银行金科同句窗)。ss 轨输入 content_ss = 标题 prepend + 银行与金科同句共现片段 ±窗口; 无同句共现时回退全文 body 且 ss_is_fallback=True (回退语义镜像 ctx, 共享 n_articles 分母)。本列统计: 在仅喂银行金科同句片段 (或回退全文) 时, GPT-5.4-nano 独立判为正面 (`gpt54nano_score_ss > 0`)、且实质性维度被有效测量的银行年度报道数。差分维度为"模型=gpt54nano"与"轨道=ss"的交叉: 正面侧由 GPT-5.4-nano 的 ss 轨情感码决定, 实质性侧沿用三家共识标签。相对同模型 full/ctx 列, ss 因同句共现约束语义最严、样本最聚焦 (T=2 开发数据上 ss 轨可能零方差退化属预期, 生产 T=19 正常)。与 deepseekv4_ss、gemini31_ss 并排, 本列独有信息是 GPT-5.4-nano 在最严格同句语境下的正面判别口径。ss 为条件于 full 留篇集的稳健性轨道。作为构念角色, GPT-5.4-nano 经 yunwu 路由、逐条独立请求经并发信号量控制, 缓存命中键为 prompt_version='v8-2026-05-17' 与 temperature=0.0, 离线三轨全命中即可字节级复现。本列在步骤 7h 充当 GPT-5.4-nano ss 轨洗稿率的同域分母, 对应分子为该模型同轨"正面且象征性"报道计数; 零报道银行年度经 balance_panel 补 0, `_safe_ratio` 遇零分母返回 NaN。per-model 降级独立: GPT-5.4-nano 缺席只使自身族计数缺失, 不连坐 deepseekv4 与 gemini31。本列与同族其余八列各自 just-identified 并排、互为稳健性、不分主次, 严禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Baumann, J., Röttger, P., Urman, A., Wendsjö, A., Plaza-del-Arco, F. M., Gruber, J. B., & Hovy, D. (2025). Large language model hacking: Quantifying the hidden risks of using LLMs for text annotation. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2509.08825
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences. https://doi.org/10.1073/pnas.2305016120
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
<!-- rendered-citations:end -->
