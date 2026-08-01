---
family_id: F180
columns:
- deepseekv4_sub_frac_ctx
- deepseekv4_sub_frac_full
- deepseekv4_sub_frac_ss
- gemini31_sub_frac_ctx
- gemini31_sub_frac_full
- gemini31_sub_frac_ss
- gpt54nano_sub_frac_ctx
- gpt54nano_sub_frac_full
- gpt54nano_sub_frac_ss
unit: 比率/占比 (proportion, 取值域 [0,1]; 分子分母同为银行-年文章计数)
formula: "{short}_sub_frac{track} = mean({short}_sub_frac_src{track}); 门控指示列 {short}_sub_frac_src ≡ (该模型 verified ∧ innovation_substantiveness 判为『实质性』) / 该模型同轨 verified 篇数; short ∈ {gpt54nano, gemini31, deepseekv4}, track ∈ {_full, _ctx, _ss}; 分母 0 时置 NaN"
producer: news_process/pipeline/panel/encode.py::encode_sentiment (门控指示列 _src) + build_aggregation_dict (mean 聚合) ; news_process/pipeline/sentiment/tone_llms.py (per-model 文章级判类)
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 21_tone_llms.parquet (per-model 文章级 {short}_subst{track} 存档列)
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
- doi: 10.1287/mnsc.2024.07420
  type: journal
  authors: Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C.
  year: 2026
  title: "\"Glossy green\" banks: The disconnect between environmental disclosures and lending activities"
  venue: Management Science
  pages_or_artno: Advance online publication
- doi: 10.1177/00491241251325243
  type: journal
  authors: Chae, Y., & Davidson, T.
  year: 2026
  title: "Large language models for text classification: From zero-shot learning to instruction-tuning"
  venue: Sociological Methods & Research
  vol: 55
  issue: 2
  pages_or_artno: 501-567
- doi: 10.1111/jofi.13412
  type: journal
  authors: Duchin, R., Gao, J., & Xu, Q.
  year: 2025
  title: "Sustainability or greenwashing: Evidence from the asset market for industrial pollution"
  venue: The Journal of Finance
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: "ChatGPT for textual analysis? How to use generative LLMs in accounting research"
  venue: Management Science
  vol: 71
  issue: 9
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2412.07031
  type: arxiv
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: "Large language models: An applied econometric framework (NBER Working Paper No. 33344)"
  venue: arXiv
- doi: 10.1016/j.jbankfin.2024.107191
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2024
  title: "How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk"
  venue: Journal of Banking & Finance
  vol: 164
  pages_or_artno: 107191
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
本家族刻画银行金融科技创新叙事的『实质性』维度在单一大语言模型判读下的银行-年占比, 即在一家银行某一年度被媒体报道并经该模型确认 (verified) 为有效的金融科技报道中, 有多大比例被该模型判定为『实质性』创新投入而非『象征性』表态。这是 P3 (bank_fintech_substance) 论文线处理构念的跨厂商稳健性载体。理论根基是 Westphal 与 Zajac (1994) 在高管长期激励计划情境中确立的实质—象征二分 (substance versus symbolism): 组织的许多治理与战略动作既可能是真实改变资源配置的实质行动, 也可能只是迎合外部合法性预期的象征姿态, 二者在对外披露文本中往往难分, 却对后续绩效有截然不同的含义。落到银行与金融科技这一具体关系上, 『实质性』对应真实的科技投入、系统上线、业务重构、专利与研发落地; 『象征性』对应仅停留在口号、战略表态、概念响应层面的言说。用大白话讲, 这九列想量化的是『这家银行今年被新闻讲成是真金白银在搞金融科技, 还是更像喊口号做样子』, 数值越高代表该模型读到的实质成色越足。这种言行脱耦 (decoupling) 现象在近期银行与企业实证中被反复确认: Giannetti, Jasova, Loumioti 与 Mendicino (2026) 记录了银行环境披露与实际放贷行为之间的系统性断裂, Duchin, Gao 与 Xu (2025) 从工业污染资产市场识别出可持续叙事与真实减排的背离, Bingler, Kraus, Leippold 与 Webersinke (2024) 则以气候披露中的『廉价言辞』(cheap talk) 与真实减排行动的关联刻画同一构念。这些证据共同为『实质 vs 象征』作为可测银行行为维度提供了构念效度支撑。数据链条为: 原始中文银行/金融科技新闻经预处理、银行与金融科技实体识别、共现硬过滤 (stage 13) 后, 在 stage 21 由三家 LLM (gpt54nano、gemini31 两家走 yunwu, deepseekv4 直连 api.deepseek.com) 分别对每篇文章的 innovation_substantiveness 维度独立判类, 面板导出阶段 (stage 40, encode.py) 再按模型逐一聚合为银行-年占比。

【方法学与计算】
每列的计算入口是 encode.py: 先在 encode_sentiment 层为每个模型、每条轨道生成门控指示列 {short}_sub_frac_src{track}, 其取值为 Int8 指示 (该模型 verified 且 innovation_substantiveness 判为『实质性』记 1, verified 但判象征或缺判记 0, 未 verified 置缺失), 再由 build_aggregation_dict 对该指示列取 mean, 得到 {short}_sub_frac{track} = (该模型 verified ∧ 判实质) / 该模型同轨 verified 篇数。分母是各模型自身的 verified 篇数而非全体篇数, 故每列是模型内自洽的条件占比; 分母为 0 时该银行-年置 NaN 并优雅缺席, 绝不静默清零。文章级与面板级的命名域刻意不可字符串互达: 文章级基名为 subst, 面板 metric 基名为 sub_frac, 二者由 encode.LLM_CLASS_SPEC 三元映射唯一互锁 (subst → sub_frac / 实质性 / innovation_substantiveness), 该映射是发列、聚合、正则推断三处的唯一权威锚点。共识非裸多数票: 三家 per-model 判读经各自 verified 门控清票后进入聚合, 分母恒为该模型自身的 verified 篇数。留篇门控自 2026-06-29 起为 full-only: 一篇是否算『银行金科报道』只由 full 轨的 llm_verified_full 决定, ctx/ss 因而降为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集, 但 per-track、per-model 的分子分母一律逐轨逐模型独立计算, 绝不跨轨或跨模型借分母。ss 轨的文本回退语义镜像 ctx: 当某文无银行与金融科技同句共现时, content_ss 回退为全文正文并置 ss_is_fallback=True, 判类在该回退文本上进行, 分母与 ctx/ss 共享 n_articles 口径。三家 LLM 各自、三轨 (full/ctx/ss) 各自均属互为稳健性、不分主次的并排臂: 每个『模型 × 轨道』单元各自 just-identified 并排, 严禁把任意两个 per-model 或两轨的 sub_frac 拼进同一 over-identified Hansen J —— 三家模型读的是同一批文章、三轨源自同一篇文章的三个剪裁窗口, bank_type×year 的共同冲击逐字同污染各单元, 过度识别检验对真实威胁功效近零且近共线会拖垮弱工具 F 统计量; 真正的跨模型多重检验校正在根级 rwolf 模板 27_tableA12 Panel C 的 CLS 族内完成。per-model 独立降级: 某模型缺席仅掉其自身三列, 不连坐其余两家 (区别于 co-primary 嵌入的 both-or-neither)。

【文献定位】
在测量方法上, 以生成式 LLM 对中文长文本做维度判类而非传统词典或人工编码, 其在管理与会计研究中的操作规范与风险由 Carlson 与 Burbano (2026) 系统化为可复现指南与警示, 本家族的三家投票、verified 门控与温度零冻结缓存正遵循这一取向; de Kok (2025) 进一步给出会计文本分析中生成式 LLM 的适用边界与提示冻结、缓存复现范式; Chae 与 Davidson (2026) 则从零样本到指令微调梳理了 LLM 文本分类的方法谱系, 为本项目把不同厂商模型并排作稳健性臂提供了方法学依据。在中文金融文本的直接实证上, Lan, Wu, Xu, Feng 与 Zhang (2025) 展示了大模型对中文金融细粒度情感与实体级判读的可行性, 支撑本测度在中文银行语料上的适用性。在识别的方法论警觉上, Ludwig, Mullainathan 与 Rambachan (2025) 的应用计量框架提醒 LLM 生成的度量本身带有测量误差与内生构造风险, 本家族因此不把 per-model 占比当作无误差真值, 而是三家并排互证并保留跨模型 κ/α 一致性诊断。与相邻测度的区分: 本家族 (实质性 sub_frac) 与 locus (创新落点 tech_frac)、collab (外部协同 collab_frac) 是三条正交的 LLM 分类维度, 三者命名域间无字符串变换可达, 由 LLM_CLASS_SPEC 三元映射唯一互锁, 不可混淆; 且本家族是 per-model 存档稳健臂, 其上位 canonical headline 是三家共识的 sub_frac (verified 门控清票后的共识占比), per-model 九列 co-equal 佐证共识的跨厂商稳健性。

## VAR: deepseekv4_sub_frac_full

【变体差分】
本列是 DeepSeek-V4 Flash 单一模型在 full 轨 (标题 prepend 加全文正文) 上的实质性占比。差分三维: 模型 = deepseekv4 (config/sentiment.yaml::models 单一事实源, 直连 api.deepseek.com, 与走 yunwu 的另两家不同源, 曾被误标 Grok-4.1 已勘误); 轨道 = full; 维度固定为 innovation_substantiveness。计算为该模型 verified 且判『实质性』的银行-年文章数除以该模型同轨 verified 篇数 (门控指示列 deepseekv4_sub_frac_src_full 取 mean), 分母为 0 置 NaN。full 轨承载全项目唯一的留篇门控 (full-only, 2026-06-29): 一篇是否算银行金科报道只看 full 轨 verified, 故本列的分母口径最直接对应主留篇集, 是三轨中粒度最全、有效篇数通常最大的一轨。作为 P3 substance 线共识 sub_frac 的跨厂商稳健臂之一, 本列与 gpt54nano、gemini31 两家的 full 轨对应列 co-equal, 三家各自 just-identified 并排、互为稳健性不分主次, 严禁把任意两家的 sub_frac 拼进同一 over-identified Hansen J; 跨模型多重检验校正走根级 27_tableA12 Panel C 的 CLS 族。deepseekv4 若在生产中缺席, 仅掉其自身三列, 不连坐另两家 (per-model 独立降级)。文章级 deepseekv4_subst_full 存档列不门控 (保留原始输出供审计), 门控在 encode 层一次完成。三家 full 轨列并排的实证意义在于: 若共识 sub_frac 揭示的银行实质投入模式仅在某一家模型下成立、切换厂商即翻转, 则该结论不可靠; 反之三家读数方向一致才构成跨厂商稳健的证据。deepseekv4 直连自有端点、与另两家不共享代理与厂商训练分布, 因而是三家中信息最独立的一臂, 其 full 轨读数对检验判读偏好是否由某一代理链路特有的系统偏差驱动尤为关键; 跨模型一致性由 tone_validation 复用 Krippendorff α 与 Cohen κ (κ 须先重映射非负码, 使 -1 缺标哨兵不与负面标签冲突) 量化, 而非以两两相关系数简单替代。本列的温度零冻结缓存 (prompt v8 字节冻结) 保证该模型判读在离线复现下逐字节可重放。

## VAR: deepseekv4_sub_frac_ctx

【变体差分】
本列是 DeepSeek-V4 Flash 在 ctx 轨 (标题 prepend 加含目标银行句的实体上下文窗口, 即以目标银行所在句为中心的邻近上下文剪裁) 上的实质性占比。相对同模型 full 轨列, 唯一差分是判类文本窗口收窄为实体上下文而非全文: 分子取 deepseekv4 判『实质性』的 ctx 轨银行-年文章数, 分母取该模型同轨 verified 篇数 n, 严格逐 ctx 轨、逐模型配对, 绝不向 full 或另两家借分母。作为 conditional-on-full 的测度/稳健性轨, 本列行宇宙是 full 留篇集的子集, 但占比在 ctx 窗口上独立计算, 因窗口较 full 窄、较 ss 宽, 通常提供介于二者之间的中间粒度读数与较平滑的有效分母。本列与同模型 full/ss 两轨列、以及另两家的 ctx 轨列均 co-equal 互为稳健性、不分主次, 各自 just-identified 并排, 严禁两轨或两家拼入同一 over-identified Hansen J —— 三轨同源一篇文章的三个剪裁窗口, 共同冲击逐字同污染, 过度识别既无功效又近共线。早期试跑 T=2 浅面板上 ctx 轨可能出现零方差退化, 属预期而非缺陷, 生产 T=19 语料恢复正常变异。缺同轨分母时整列置 NaN 并告警, 属优雅降级。ctx 轨的价值在于隔离判读对文本剪裁窗口的敏感性: 若某银行-年在 full 全文下被判高实质、而在 ctx 实体窗口下占比骤降, 提示其实质信号更多来自与目标银行句相距较远的段落, 需谨慎解读; 三轨读数一致才构成对判读稳健于剪裁选择的证据。本列由 deepseekv4 单模型在实体上下文窗口内读判, 与同模型的 full/ss 两轨、及 gemini31、gpt54nano 两家的 ctx 轨列共同构成『模型 × 轨道』的稳健性矩阵, 任一单元的偏离都可被其余单元对照定位, 而非并入同一识别式相互抵消。

## VAR: deepseekv4_sub_frac_ss

【变体差分】
本列是 DeepSeek-V4 Flash 在 ss 轨 (标题 prepend 加『银行与金融科技词同句正负 N 窗』的最窄剪裁) 上的实质性占比, 差分纯在文本判据窗口: 判类基于该模型对 content_ss 的读判, 分子为 deepseekv4 判『实质性』的 ss 轨银行-年文章数, 分母为该模型同轨 verified 篇数, 严格逐 ss 轨、逐模型配对, 绝不借用 ctx/full 或另两家的分母。回退语义镜像 ctx: 当某篇文章无银行与金融科技同句共现时, content_ss 优雅回退为全文正文并置 ss_is_fallback=True, 判类在该回退文本上进行, 分母与 ctx/ss 共享 n_articles 口径。因窗口最窄, 本列在浅面板上最易出现有效篇数偏少、方差塌缩甚至逐格 NaN 的退化, 早期试跑 T=2 数据上属预期, 生产 T=19 恢复。作为 conditional-on-full 的最窄稳健性轨, 本列与同模型 full/ctx 两轨、及另两家 ss 轨列 co-equal 互为稳健性不分主次, 各自 just-identified 并排, 严禁把 full/ctx/ss 任意两轨或任意两家的 sub_frac 拼成一对工具跑同一 over-identified Hansen J。本列提供的是『银行与金融科技在最贴近语境下确被同句提及』严格共现前提下、由 deepseekv4 单模型读出的实质叙事强度稳健读数, 与该模型的 full/ctx 两轨读数三点对照, 检验实质判定是否稳健于从全文到同句的窗口逐级收窄。ss 轨剔除了银行与金融科技仅在文中相隔较远处各自出现的偶合语境, 保留最强共现信号, 因而在有效篇数充足时给出最保守也最贴题的实质占比读数; 当回退频繁 (ss_is_fallback 大面积为真) 时本列近似退化为 full 轨, 解读须结合 ss_is_fallback 占比一并判断。

## VAR: gemini31_sub_frac_full

【变体差分】
本列是 Gemini-3.1-Flash-Lite 单一模型在 full 轨 (标题 prepend 加全文正文) 上的实质性占比。差分三维: 模型 = gemini31 (走 yunwu 代理端点, 与直连的 deepseekv4 及同走 yunwu 的 gpt54nano 是三家不同厂商模型); 轨道 = full; 维度固定为 innovation_substantiveness。计算为该模型 verified 且判『实质性』的银行-年文章数除以该模型同轨 verified 篇数 (门控指示列 gemini31_sub_frac_src_full 取 mean), 分母 0 置 NaN。full 轨承载 full-only 留篇门控, 分母口径最直接对应主留篇集, 是三轨中粒度最全的一轨。作为 P3 substance 共识 sub_frac 的跨厂商稳健臂之一, 本列与 deepseekv4、gpt54nano 两家 full 轨对应列 co-equal, 三家各自 just-identified 并排、互为稳健性不分主次, 严禁两家 sub_frac 拼入同一 over-identified Hansen J; 跨模型 FWER 校正走 27_tableA12 Panel C 的 CLS 族, 跨模型一致性由 tone_validation 复用 Krippendorff α 与 Cohen κ (κ 须先重映射非负码) 诊断。gemini31 若缺席仅掉自身三列, 不连坐另两家。文章级 gemini31_subst_full 存档列不门控, 门控在 encode 层一次完成。gemini31 与 gpt54nano 虽同走 yunwu 代理端点, 但底层是 Google 与 OpenAI 两家不同厂商、不同训练分布的模型, 故仍构成有效的跨厂商互证臂; 三家 full 轨读数并排意在检验共识实质占比是否稳健于厂商切换, 而非由某一模型对『实质 vs 象征』边界的系统性判读偏好驱动。本列的实质判定同样承接 Westphal 与 Zajac (1994) 的实质—象征二分, 只是把人工编码替换为该模型在温度零、prompt v8 冻结下的可复现读判, 判读结果经该模型自身 verified 门控清票后聚合, 分母恒为其自身 verified 篇数。

## VAR: gemini31_sub_frac_ctx

【变体差分】
本列是 Gemini-3.1-Flash-Lite 在 ctx 轨 (标题 prepend 加目标银行句实体上下文窗口) 上的实质性占比, 相对同模型 full 轨列唯一差分是判类窗口收窄为实体上下文而非全文。分子取 gemini31 判『实质性』的 ctx 轨银行-年文章数, 分母取该模型同轨 verified 篇数, 严格逐 ctx 轨、逐模型配对, 绝不向 full 或另两家借分母。作为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 占比在 ctx 窗口上独立计, 粒度介于 full 与 ss 之间, 通常给出较平滑的中间读数。本列与同模型 full/ss 两轨、及另两家 ctx 轨列 co-equal 互为稳健性不分主次, 各自 just-identified 并排, 严禁两轨或两家拼入同一 over-identified Hansen J —— 三轨同源一篇文章的三窗剪裁, 共同冲击逐字同污染, 过度识别既无功效又近共线。gemini31 与另两家的 ctx 轨读数并排, 检验共识 sub_frac 的判读是否稳健于厂商切换而非由单一模型的系统偏好驱动。早期试跑 T=2 浅面板 ctx 轨可能零方差退化属预期, 生产 T=19 恢复; 缺同轨分母整列置 NaN 并告警, 属优雅降级。作为中间粒度轨, 本列既避免了 full 轨可能纳入远距离偶合语境的噪声, 又不像 ss 轨那样因窗口过窄而频繁回退, 因而在多数银行-年上给出兼具信息量与稳定性的实质占比读数; 其与同模型 full/ss 两轨的三点对照, 用于定位 gemini31 的实质判定对剪裁窗口的敏感区间, 而三家 ctx 轨的横向对照则用于定位判定对厂商的敏感区间, 两个方向的稳健性由『模型 × 轨道』九列矩阵联合覆盖。

## VAR: gemini31_sub_frac_ss

【变体差分】
本列是 Gemini-3.1-Flash-Lite 在 ss 轨 (标题 prepend 加银行与金融科技词同句正负 N 窗最窄剪裁) 上的实质性占比, 差分纯在文本判据窗口。判类基于 gemini31 对 content_ss 的读判, 分子为该模型判『实质性』的 ss 轨银行-年文章数, 分母为该模型同轨 verified 篇数, 严格逐 ss 轨、逐模型配对, 绝不借用 ctx/full 或另两家分母。回退语义镜像 ctx: 无银行与金融科技同句共现时 content_ss 优雅回退全文正文并置 ss_is_fallback=True, 判类在回退文本上进行, 分母与 ctx/ss 共享 n_articles 口径。因窗口最窄, 本列在浅面板上最易有效篇数偏少、方差塌缩甚至逐格 NaN, 早期试跑 T=2 属预期、生产 T=19 恢复。作为 conditional-on-full 最窄稳健性轨, 本列与同模型 full/ctx 两轨、及另两家 ss 轨列 co-equal 互为稳健性不分主次, 各自 just-identified 并排, 严禁 full/ctx/ss 任意两轨或任意两家 sub_frac 拼成一对工具跑同一 over-identified Hansen J。本列给出『严格同句共现前提下、由 gemini31 单模型读出』的实质叙事强度稳健读数, 与 deepseekv4、gpt54nano 的 ss 轨读数三家互证。ss 轨在三轨中判据最严, 只承认银行与金融科技词真正落在同一句 (或其正负 N 窗) 内的共现语境, 因而对『象征性表态被误读为实质投入』这一测量威胁最不敏感; 当本列在有效篇数充足的银行-年上仍与 full/ctx 两轨读数一致时, 提供了实质判定稳健于最保守共现前提的证据。若 ss_is_fallback 在某银行-年大面积为真, 本列近似退化为 full 轨全文读判, 此时其独立信息量下降, 解读须结合回退占比谨慎对待。

## VAR: gpt54nano_sub_frac_full

【变体差分】
本列是 GPT-5.4-nano 单一模型在 full 轨 (标题 prepend 加全文正文) 上的实质性占比。差分三维: 模型 = gpt54nano (走 yunwu 代理端点); 轨道 = full; 维度固定为 innovation_substantiveness。计算为该模型 verified 且判『实质性』的银行-年文章数除以该模型同轨 verified 篇数 (门控指示列 gpt54nano_sub_frac_src_full 取 mean), 分母 0 置 NaN。full 轨承载 full-only 留篇门控 (2026-06-29), 分母口径最直接对应主留篇集, 是三轨中粒度最全、有效篇数通常最大的一轨。作为 P3 substance 共识 sub_frac 的跨厂商稳健臂之一, 本列与 deepseekv4、gemini31 两家 full 轨对应列 co-equal, 三家各自 just-identified 并排、互为稳健性不分主次, 严禁两家 sub_frac 拼入同一 over-identified Hansen J; 跨模型 FWER 校正走根级 27_tableA12 Panel C 的 CLS 族。gpt54nano 若缺席仅掉自身三列, 不连坐另两家 (per-model 独立降级)。文章级 gpt54nano_subst_full 存档列不门控 (保留原始输出供审计), 门控在 encode 层一次完成。三家 full 轨列并排的意义是检验共识实质占比是否稳健于厂商切换, 而非由某单一模型的系统性判读偏好驱动。gpt54nano 作为轻量级模型, 其判读速度与成本优势使其适合作为主投票成员之一, 但也正因参数规模较小, 其对『实质 vs 象征』细微边界的判定可能与更大模型系统性偏移, 故其 full 轨读数与 deepseekv4、gemini31 的对照尤具诊断价值: 若三家方向一致, 说明实质结论不依赖模型容量; 若 gpt54nano 系统偏离, 则提示该维度判定对模型能力敏感, 需在稳健性叙事中披露。本列判读同样在温度零、prompt v8 字节冻结下产出, 保证离线缓存命中时逐字节可复现。

## VAR: gpt54nano_sub_frac_ctx

【变体差分】
本列是 GPT-5.4-nano 在 ctx 轨 (标题 prepend 加目标银行句实体上下文窗口) 上的实质性占比, 相对同模型 full 轨列唯一差分是判类窗口收窄为实体上下文而非全文。分子取 gpt54nano 判『实质性』的 ctx 轨银行-年文章数, 分母取该模型同轨 verified 篇数, 严格逐 ctx 轨、逐模型配对, 绝不向 full 或另两家借分母。作为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 占比在 ctx 窗口上独立计, 粒度介于 full 与 ss 之间, 通常给出较平滑的中间读数与较大有效分母。本列与同模型 full/ss 两轨、及另两家 ctx 轨列 co-equal 互为稳健性不分主次, 各自 just-identified 并排, 严禁两轨或两家拼入同一 over-identified Hansen J —— 三轨同源一篇文章的三窗剪裁, 共同冲击逐字同污染, 过度识别既无功效又近共线。早期试跑 T=2 浅面板 ctx 轨可能零方差退化属预期, 生产 T=19 恢复正常变异; 缺同轨分母时整列置 NaN 并告警, 属优雅降级而非静默清零。本列由 gpt54nano 单模型在实体上下文窗口内读判, 与同模型 full/ss 两轨、及 deepseekv4、gemini31 两家的 ctx 轨列共同构成稳健性矩阵; 其中间粒度定位使其既滤除全文中远距离偶合语境的噪声, 又不像 ss 轨那样频繁触发回退, 通常在多数银行-年上给出信息量与稳定性兼顾的实质占比读数, 是该模型三轨中最常被主分析采用的稳健性对照轨。

## VAR: gpt54nano_sub_frac_ss

【变体差分】
本列是 GPT-5.4-nano 在 ss 轨 (标题 prepend 加银行与金融科技词同句正负 N 窗最窄剪裁) 上的实质性占比, 差分纯在文本判据窗口。判类基于 gpt54nano 对 content_ss 的读判, 分子为该模型判『实质性』的 ss 轨银行-年文章数, 分母为该模型同轨 verified 篇数, 严格逐 ss 轨、逐模型配对, 绝不借用 ctx/full 或另两家分母。回退语义镜像 ctx: 无银行与金融科技同句共现时 content_ss 优雅回退全文正文并置 ss_is_fallback=True, 判类在回退文本上进行, 分母与 ctx/ss 共享 n_articles 口径。因窗口最窄, 本列在浅面板上最易有效篇数偏少、方差塌缩甚至逐格 NaN, 早期试跑 T=2 数据上属预期, 生产 T=19 恢复。作为 conditional-on-full 最窄稳健性轨, 本列与同模型 full/ctx 两轨、及另两家 ss 轨列 co-equal 互为稳健性不分主次, 各自 just-identified 并排, 严禁把 full/ctx/ss 任意两轨或任意两家 sub_frac 拼成一对工具跑同一 over-identified Hansen J。本列给出『银行与金融科技在最贴近语境下确被同句提及』严格共现前提下、由 gpt54nano 单模型读出的实质叙事强度稳健读数, 与 deepseekv4、gemini31 的 ss 轨读数构成三家跨厂商互证。作为轻量模型在最严判据轨上的读判, 本列既受模型容量约束、又受最窄窗口约束, 是九列矩阵中信息最保守的一格; 在有效篇数充足的银行-年上, 若本列仍与同模型 full/ctx 两轨、及另两家 ss 轨读数方向一致, 则同时提供了实质判定稳健于窗口收窄与厂商切换两个方向的证据。当 ss_is_fallback 大面积为真时本列近似退化为 full 轨, 解读须结合回退占比一并判断, 避免把回退语境误当严格共现证据。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Giannetti, M., Jasova, M., Loumioti, M., & Mendicino, C. (2026). "Glossy green" banks: The disconnect between environmental disclosures and lending activities. Management Science, Advance online publication. https://doi.org/10.1287/mnsc.2024.07420
Chae, Y., & Davidson, T. (2026). Large language models for text classification: From zero-shot learning to instruction-tuning. Sociological Methods & Research, 55(2), 501-567. https://doi.org/10.1177/00491241251325243
Duchin, R., Gao, J., & Xu, Q. (2025). Sustainability or greenwashing: Evidence from the asset market for industrial pollution. The Journal of Finance. https://doi.org/10.1111/jofi.13412
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework (NBER Working Paper No. 33344). arXiv [Preprint]. https://doi.org/10.48550/arXiv.2412.07031
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2024). How cheap talk in climate disclosures relates to climate initiatives, corporate emissions, and reputation risk. Journal of Banking & Finance, 164, 107191. https://doi.org/10.1016/j.jbankfin.2024.107191
Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
<!-- rendered-citations:end -->
