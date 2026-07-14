---
family_id: F396
columns:
- llm_vote_score_mw_sum_ctx
- llm_vote_score_mw_sum_full
- llm_vote_score_mw_sum_ss
unit: 无量纲得分之媒体权威加权和 (银行-年层面, 文章级 llm_vote_score{track} × media_authority_weight 逐篇求和)
formula: 'llm_vote_score_mw_sum{track} = sum(llm_vote_score_mw{track}), 其中 llm_vote_score_mw{track} = llm_vote_score{track} * media_authority_weight (文章级); 分子来自 pipeline/panel/encode.py 聚合块 for track in [_full,_ctx,_ss]: agg[f"llm_vote_score_mw_sum{track}"] = (f"llm_vote_score_mw{track}", "sum")'
producer: pipeline\panel\encode.py ; pipeline\audit\stata_audit.py
upstream:
- 21_tone_llms.parquet (llm_vote_score{track}: 三家 LLM 多数投票共识得分, gpt-5.4-nano/gemini-3.1-flash-lite/deepseek-v4-flash)
- media_authority_weight (文章级媒体权威权重, 来源报社/来源等级映射)
- 14_materialize_ctx.parquet (content_ctx/content_ss 三轨文本物化)
citations:
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Zhi; Huang, Allen G.; Wermers, Russ; Wu, Wenfeng"
  year: 2022
  title: "Language and Domain Specificity: A Chinese Financial Sentiment Dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1287/mnsc.2023.03253"
  type: journal
  authors: "de Kok, T."
  year: 2025
  title: "ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research"
  venue: "Management Science"
  vol: "71"
  issue: "9"
  pages_or_artno: "7888-7906"
- doi: "10.48550/arXiv.2511.15714"
  type: arxiv
  authors: "Kamen, A.; Kamen, Y."
  year: 2025
  title: "Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization"
  venue: "arXiv"
- doi: "10.1111/j.1540-6261.2009.01493.x"
  type: journal
  authors: "Fang, Lily; Peress, Joel"
  year: 2009
  title: "Media Coverage and the Cross-Section of Stock Returns"
  venue: "The Journal of Finance"
  vol: "64"
  issue: "5"
  pages_or_artno: "2023-2052"
- doi: "10.1073/pnas.2305016120"
  type: journal
  authors: "Gilardi, Fabrizio; Alizadeh, Meysam; Kubli, Maël"
  year: 2023
  title: "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks"
  venue: "Proceedings of the National Academy of Sciences"
  vol: "120"
  issue: "30"
  pages_or_artno: "e2305016120"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是「银行-年」层面、以媒体权威度加权的三家大语言模型多数投票语调得分之总量, 是 stage 21 情感 LLM 产出经 pipeline/panel/encode.py 面板聚合而来的三轨 (full/ctx/ss) 分子和列族。其上游构念链条是: stage 21 三家 LLM (OpenAI 系 gpt-5.4-nano、Google 系 gemini-3.1-flash-lite、DeepSeek 系 deepseek-v4-flash) 各自独立对每篇留篇文章的银行-金科语调打分并多数投票, 产出文章级共识变量 llm_vote_score{track} (正/负/中性三分类转标量, 与投票口径一致); 随后 pipeline/panel/encode.py 在聚合到银行-年面板前, 用该文章的媒体权威权重 media_authority_weight (反映发文来源的行业地位/影响力, 来自来源等级映射, 与来源报社层级、转载广度相关的先验刻画) 逐篇相乘, 得到文章级中间列 llm_vote_score_mw{track}, 再按银行-年分组求和, 即本家族三列。mw 即 media-weighted 的缩写, 与家族名邻近的 vw (mention-density 加权)、hw (羊群/抄稿权重加权) 是并列的三套加权口径, 三者共用同一文章级共识得分 llm_vote_score{track} 作分子基座, 仅加权因子不同。该分子和列本身不是最终可直接解读的语调水平测度, 而是构造加权平均语调 llm_vote_tone_mw{track} = llm_vote_score_mw_sum{track} / 分母 (sum_media_authority_weight{track} 物理分母, 或优先取 valid-mask 分母 sum_wd_mw_llm{track}) 的分子部件; 因此本家族三列的经济含义更接近「该银行-年被媒体权威加权后的净正面/净负面报道强度之和」, 量纲随媒体权威权重的取值范围而定, 数值本身不做跨银行-年直接横比 (须先除以对应分母得到加权均值语调后再比较)。

媒体权威加权 (mw) 的设计动机, 生产源码 (pipeline/panel/encode.py) 明确标注源自会计学文献中「媒体来源可信度/权威性差异会影响其报道对市场行为的规训作用」这一支脉络: 权威度更高的媒体来源发布的报道, 对市场参与者的信息获取与预期形成的边际影响力更大, 因此对同一篇报道按其发文媒体的权威权重加权求和, 比简单等权求和更贴近该银行-年"被市场实际感知到的舆论压力"。与之相邻但构念不同的是 Fang & Peress (2009) 关于媒体覆盖广度 (是否被报道、报道数量) 与个股横截面收益关系的发现——该文献刻画的是"覆盖有无/覆盖量"这一媒体关注广度维度, 而非本家族聚焦的"同一篇报道因发文媒体权威等级不同而应获得不同权重"这一媒体权威度维度, 二者在媒体经济学脉络上相邻但不可混为一谈, 本家族仅在"媒体特征会系统性调节报道影响力"的宽泛意义上与该文献呼应, 不宜将其视为 mw 加权口径的直接方法学来源。三家 LLM 多数投票机制则呼应 Kamen & Kamen (2025) 关于 LLM ensemble 多数投票在内容分类任务上优于单模型的发现, 以及 de Kok (2025) 在会计研究中对生成式大语言模型文本分析范式 (含 temperature=0、prompt 版本冻结、结果可复现缓存) 的方法学规范; 本项目 stage 21 严格遵循该范式, prompt v8 字节级冻结、temperature=0.0、命中缓存可离线 $0 复现。

【方法学与计算】
计算链条分两段。第一段在文章级: stage 21 (tone_llms.py) 对每篇留篇文章的三轨文本 (content_full/content_ctx/content_ss, stage 14 物化) 各自跑三家 LLM 打分并多数投票, 产出 llm_vote_score{track} (标量, 三分类多数票转标量, 与三家一致性挂钩; 少数分歧票按投票规则折算); 随后在文章级中间步骤将其与该篇 media_authority_weight 相乘, 得 llm_vote_score_mw{track}。第二段在面板聚合级 (encode.py): 按银行-年分组, 对 llm_vote_score_mw{track} 求 sum, 即为本家族三列 llm_vote_score_mw_sum{track}, track ∈ {_full, _ctx, _ss}。该聚合与同一 for 循环内的 llm_vote_cont_mw_sum{track} (连续版共识得分的媒体权重和)、以及各家单 LLM 的 {short}_score_mw_sum{track} / {short}_cont_mw_sum{track} 是并列产出, 均在 encode.py 同一段 "for track in ['_full','_ctx','_ss']: agg[f'llm_vote_score_mw_sum{track}'] = (f'llm_vote_score_mw{track}', 'sum')" 逻辑块内批量生成, 三轨一次性对齐产出, 不存在跨轨顺序依赖。

分母侧的核算逻辑见 pipeline/audit/stata_audit.py 的加权恒等式审计段: llm_vote_tone_mw{track} = llm_vote_score_mw_sum{track} / 分母, 分母优先取 valid-mask 列 sum_wd_mw_llm{track} (仅统计 LLM 判定为有效/留篇的文章的媒体权重和, 与 encode.py 内 _llm_denom 口径对齐), 若该列缺失才回退物理分母 sum_media_authority_weight{track} (对该银行-年全部相关文章不分是否留篇一律求和的媒体权重总量)。stata_audit.py 对该恒等式做三轨全覆盖 PASS/WARN 记录, 缺失所需列时记 WARN 而非静默跳过, 以防重生面板悄悄丢失该项稽核。

留篇门控口径 (2026-06-29 起): 一篇报道是否计入"银行金科报道"的判定只看 llm_verified_full == True (full 轨门控), ctx/ss 轨的分子和只在 full 轨判定的留篇行子集上、按各自轨道文本重新计算对应轨道的 llm_vote_score{track}, 即 ctx/ss 是 conditional-on-full 的测度轨/稳健性轨, 行宇宙与 full 轨一致但各轨文本与打分逐轨单独产生。

【文献定位】
本家族方法学定位处于三条文献脉络的交汇点。其一是 LLM 文本标注/情感分析在金融文本挖掘中的应用范式: de Kok (2025, Management Science) 系统论述了如何在会计与金融研究中规范使用生成式大语言模型做文本分析 (含 prompt 版本控制、temperature 设定、可复现缓存), 本项目 stage 21 的确定性锚点设计 (prompt v8 冻结 + temperature=0.0 + LLM 缓存离线可复现) 正是对该规范的工程落地; Gilardi et al. (2023, PNAS) 的发现 (ChatGPT 类模型在文本标注任务上可超越众包标注质量) 为以 LLM 多数投票替代传统人工/词典标注提供了方法学正当性基础。其二是 LLM 集成/多数投票机制: Kamen & Kamen (2025) 证明 LLM ensemble 的多数投票策略在内容分类上系统性优于单模型判断, 本项目采用跨厂商 (OpenAI/Google/DeepSeek) 三家独立模型多数投票, 既降低单一厂商模型偏差, 也与该文献的 ensemble 优越性发现相呼应。其三是媒体特征与市场信息环境的更宽泛脉络: Fang & Peress (2009, Journal of Finance) 揭示媒体覆盖广度 (报道有无/报道量) 与个股横截面收益的因果关联, 说明媒体特征会系统性调节报道对定价与信息环境的影响力, 本家族 mw 权威度加权与其在"媒体特征异质性重要"这一宽泛判断上呼应, 但 mw 权重的直接构造依据 (生产源码 encode.py 注释所标注) 是媒体来源权威等级本身, 与 Fang & Peress 所刻画的"覆盖广度"是媒体经济学脉络下两个不同的构念维度, 不应互相替代解读; Du et al. (2022, Review of Finance) 构建中文金融情感词典时同样强调中文金融文本情感测度须针对领域特异性做校准, 本项目虽以 LLM 而非词典为主测度, 但词典法 (dict_*) 是本项目情感测度三角 (LLM/词典/BERT) 中互为稳健性的并列一支, mw 加权口径在三法之间统一适用, 保证跨方法可比。

三轨口径铁律: full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁止混进同一 over-identified Hansen J 检验。ss 轨回退语义镜像 ctx 轨——当某篇文章不存在银行∧金科词同句共现时, content_ss 回退为全文 body (与 content_ctx 的实体窗口回退逻辑对称), 对应 ss_is_fallback 标记为 True, 且此类回退行仍计入分母 (n_articles 口径共享)。n_articles 与留篇门控严格遵循 full-only 口径 (2026-06-29 起生效): 一篇文章是否被计为"该银行-年的一篇有效银行金科报道", 只由 llm_verified_full 决定, ctx/ss 轨的加权和列是在该 full-only 留篇行集合的子集上、按各自轨道文本条件计算的稳健性测度, 不构成独立的行宇宙判定。

## VAR: llm_vote_score_mw_sum_ctx

【变体差分】
本列是 ctx 轨 (实体窗口文本, 标题+目标银行实体窗口) 的媒体权威加权分子和, 计算基座 llm_vote_score_ctx 来自 stage 21 对 content_ctx (stage 14 物化, prepend_title 拼接标题与银行实体窗口正文片段) 跑三家 LLM 多数投票产出的共识得分, 再乘以该篇 media_authority_weight 后按银行-年求和。与 full 轨的核心差异在于文本输入范围更窄——ctx 轨只截取围绕目标银行实体的窗口正文而非全文, 意在剥离与银行本体不直接相关的段落对语调判定的干扰, 是"聚焦目标实体"视角下的稳健性测度。ctx 轨的行宇宙 (哪些银行-年、哪些文章参与求和) 由 full 轨的留篇门控 (llm_verified_full == True) 决定, 本列只是在该行集合上重新用 ctx 轨文本与打分口径计算加权和, 并非独立扩展或收缩样本。当某篇文章缺乏可识别的银行实体窗口 (罕见退化情形) 时, content_ctx 按既定回退规则处理, 相应 ctx_is_fallback 标记为 True, 但仍计入本列求和 (回退不等于剔除)。ctx 轨与 full 轨、ss 轨互为稳健性并排关系, 不因文本范围收窄而被视为"更精确"或"次要", 三者共同构成本项目三轨稳健性设计的一部分, 严禁将 ctx/full/ss 三条加权和列同时作为工具变量塞入同一 over-identified 的 Hansen J 检验方程。

## VAR: llm_vote_score_mw_sum_full

【变体差分】
本列是 full 轨 (标题+全文正文) 的媒体权威加权分子和, 是本家族的门控主轨: 一篇文章是否被认定为"一篇有效的银行金科报道"并计入银行-年面板, 唯一由该篇在 full 轨上的 LLM 验证结果 llm_verified_full 决定 (2026-06-29 起 full-only 留篇门控铁律), ctx/ss 两轨的对应列均是在 full 轨判定出的留篇行子集上派生的稳健性测度。计算上, 本列的分子基座 llm_vote_score_full 来自 stage 21 对 content_full (标题+完整正文, stage 14 prepend_title 拼接) 跑三家 LLM 多数投票的共识得分, 乘以该篇 media_authority_weight 后按银行-年分组求和。在下游 P1 主线论文 (bank_fintech_tone) 的处理变量设计中, 由该列参与构造的加权平均语调 llm_vote_tone_mw_full 是 full 轨口径下媒体权威加权语调测度的分子部件, 与其姊妹加权口径 vw (提及密度加权, 分子列名含 _w_ 而非 _vw_) 、hw (羊群/抄稿权重加权) 并列, 三套权重各自反映不同的"报道重要性"构念——mw 强调发文媒体权威性、vw 强调该银行在文中被提及的密集程度、hw 强调该报道相对同期同题材报道群的雷同/抄稿程度调整。三套加权口径互为稳健性并排, 不设主次, 分别通过各自的 sum 列服务各自的加权均值分母恒等式, stata_audit.py 对三者逐一做恒等式 PASS/WARN 稽核。

## VAR: llm_vote_score_mw_sum_ss

【变体差分】
本列是 ss 轨 (标题+银行∧金科同句共现窗口, 句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 ±1 句) 的媒体权威加权分子和, 计算基座 llm_vote_score_ss 来自 stage 21 对 content_ss 跑三家 LLM 多数投票产出的共识得分, 乘以该篇 media_authority_weight 后按银行-年求和。ss 轨是三轨中文本范围最窄的一支, 只截取银行实体与金科词汇同句 (或窗口内邻近句) 共现的片段, 意在最大限度剥离与"银行-金科关系"本体无关的段落干扰, 判定不对称口径为银行侧走否定+短名过滤、金科侧走裸 AC 自动机匹配 (1506 词表)。ss 轨回退语义严格镜像 ctx 轨: 当某篇文章不存在银行∧金科词同句共现时, content_ss 回退为全文 body, ss_is_fallback 标记为 True, 该回退行仍计入本列求和的分母口径 (n_articles 与 ctx 轨共享同一分母定义)。ss 轨的行宇宙同样由 full 轨留篇门控决定, 本列是该行集合上的条件测度, 不独立扩大或缩小样本。ss 轨与 full、ctx 两轨构成互为稳健性、各自 just-identified 并排的三支, 三者严禁混入同一 over-identified 的 Hansen J 过度识别检验; 在实证解读时, ss 轨因文本窗口最窄, 通常表现出比 full/ctx 更保守 (样本内变异更集中于强共现片段) 的加权和规模, 但这是文本范围差异的自然结果, 不代表测度质量优劣之分。
<!-- rendered-citations:begin -->
Du, Zhi; Huang, Allen G.; Wermers, Russ; Wu, Wenfeng. (2022). Language and Domain Specificity: A Chinese Financial Sentiment Dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A.; Kamen, Y. (2025). Majority Rules: LLM Ensemble Is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Fang, Lily; Peress, Joel. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Gilardi, Fabrizio; Alizadeh, Meysam; Kubli, Maël. (2023). ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
<!-- rendered-citations:end -->
