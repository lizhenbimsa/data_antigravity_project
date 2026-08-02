---
family_id: F178
columns:
- deepseekv4_score_mw_sum_ctx
- deepseekv4_score_mw_sum_full
- deepseekv4_score_mw_sum_ss
- gemini31_score_mw_sum_ctx
- gemini31_score_mw_sum_full
- gemini31_score_mw_sum_ss
- gpt54nano_score_mw_sum_ctx
- gpt54nano_score_mw_sum_full
- gpt54nano_score_mw_sum_ss
unit: 无量纲 (媒体权威性加权情感得分的银行-年求和; 情感基分离散 ∈ {-1,0,+1}, 权重均值归一化)
formula: "{model}_score_mw{track} = {model}_score{track} * media_authority_weight; {model}_score_mw_sum{track} = Σ_articles {model}_score_mw{track} (over 该银行-年留篇集)"
producer: news_process/pipeline/panel/runner.py (步骤 3c 媒体权威性加权列预计算) ; news_process/pipeline/panel/encode.py (build_aggregation_dict MW 分子和 sum + compute_media_authority_weights)
upstream:
- 21_tone_llms.parquet ({model}_score{track} 逐模型逐轨文章级情感)
- 40_panel_export_main (media_authority_weight; sum_media_authority_weight 分母)
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
- doi: 10.1146/annurev-economics-120925-105620
  type: journal
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2026
  title: "Large language models: An applied econometric framework"
  venue: Annual Review of Economics
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
- doi: 10.1038/s41586-024-07421-0
  type: journal
  authors: Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y.
  year: 2024
  title: "Detecting hallucinations in large language models using semantic entropy"
  venue: Nature
  vol: 630
  issue: 8017
  pages_or_artno: 625-630
- doi: 10.1073/pnas.2308950121
  type: journal
  authors: Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J.
  year: 2024
  title: "GPT is an effective tool for multilingual psychological text analysis"
  venue: Proceedings of the National Academy of Sciences
  vol: 121
  issue: 34
  pages_or_artno: e2308950121
- doi: 10.1016/j.frl.2024.105227
  type: journal
  authors: Kirtac, K., & Germano, G.
  year: 2024
  title: "Sentiment trading with large language models"
  venue: Finance Research Letters
  vol: 62
  pages_or_artno: 105227
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: "ChatGPT outperforms crowd workers for text-annotation tasks"
  venue: Proceedings of the National Academy of Sciences
  vol: 120
  issue: 30
  pages_or_artno: e2305016120
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
new_dois: []
---

## CORE

【构念与来源】
本家族是「单模型大语言模型情感得分, 经媒体权威性加权后, 在银行-年层聚合出的分子求和」这一中间构念的九个实例。命名骨架为 {模型}_score_mw_sum_{轨}, 其中 mw 是 media-authority weighted 的缩写 (媒体权威性加权, 并非"中等权重"), sum 表明它是聚合到银行-年的求和量而非已归一化的比率。三家大模型分别是 deepseekv4 (DeepSeek V4 Flash, 直连 api.deepseek.com)、gemini31 (gemini-3.1-flash-lite, 经 OpenLux 路由)、gpt54nano (gpt-5.4-nano, 经 OpenLux 路由); 三条文本轨道分别是 full (标题 prepend 后拼接全文正文)、ctx (标题加含目标银行句的上下文窗口)、ss (标题加银行与金融科技词同句共现的片段窗)。三模型三轨交叉即得九列, 全部为 standard 层级的中间分子列。它的直接下游是媒体权威性加权语调 {模型}_tone_mw_{轨}, 后者以本列为分子、以该银行-年有效篇数对应的媒体权威权重和为分母相除得到; 因此本家族本身不是可直接进回归右手边的强度测度, 而是把"单篇情感极性"沿"媒体影响力"维度重新称重后累加的原材料, 服务于稳健性检验中的加权口径对照。

【方法学与计算】
计算分三步。第一步在 stage 21 的统一语义精筛与情感分析中, 每篇报道被三家模型各自独立地以思维链方式判定真伪与情感, 产出逐模型逐轨的离散情感基分 {模型}_score_{轨} (取值约束在负面、中性、正面三档, 映射为 -1、0、+1)。第二步在面板 runner 的步骤 3c, 由 compute_media_authority_weights 依据 media_weights.json 中各媒体来源的静态权威性评分, 经"精确匹配→去括号归一化匹配→默认权重"三层匹配赋权, 并做均值归一化 (原始权重除以其均值), 使加权量级与等权版本可比; 随后把该权重逐篇乘到情感基分上, 得到文章级 {模型}_score_mw_{轨}。第三步在 encode 的聚合字典里对每个银行-年做 sum, 得到本家族列。分子与分母严格同域: 下游语调用 valid-mask 分母 (仅对该模型判定有效的篇数累计权重), 保证每家模型各用自己的有效篇集作分母, 避免跨模型缺标污染。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否算作"银行金融科技报道"仅由 full 轨的验证结果决定, ctx 与 ss 轨降为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但每条轨的加权求和仍逐轨独立计算, 不互相借分子。媒体权威加权的方法学依据是媒体影响力在横截面上并不均等: 权威财经媒体与地方小报的一篇同样极性的报道, 对市场认知与银行融资条件的边际影响不同, 因此按媒体权威度重新称重可抑制低影响来源的等权稀释。

【文献定位】
媒体权威性加权的经济学根据源自媒体作为信息中介的横截面差异文献: Fang and Peress (2009) 证明媒体覆盖度在股票横截面定价中系统性有价, Tetlock (2007) 则给出媒体语调传导投资者情绪进而影响市场的经典证据, 二者共同支撑"按来源影响力对情感称重优于等权平均"的取向。逐模型情感基分的可信度与方法规范来自新一代大模型标注文献: Gilardi et al. (2023) 与 Rathje et al. (2024) 表明生成式模型在文本标注 (含多语心理文本) 上可媲美甚至超过人工众包, de Kok (2025) 系统梳理了在会计研究中使用生成式模型做文本分析的温度归零、提示冻结与缓存复现范式 (与本项目 prompt v8 字节冻结、temperature=0、离线缓存复现完全一致), Lan et al. (2025) 直接针对中文细粒度金融情感展示大模型的实体级判定能力。把多家模型并排而非取单一模型, 是三角验证与集成推断的方法要求; Carlson and Burbano (2026) 与 Ludwig et al. (2026) 分别从管理学标注规范与应用计量框架角度警示单一专有模型的隐性偏差, Farquhar et al. (2024) 提供了逐模型幻觉可检测性的证据, 共同论证保留三家 per-model 分子而非过早合并的必要。本家族坚持铁律: 三家模型的九列各自 just-identified 并排, 互为稳健性、不分主次, 严禁把不同模型或不同轨的加权分子混进同一 over-identified 的 Hansen J 统计量; 跨模型的族级错误率控制由根级 rwolf 模板单独承担。

## VAR: deepseekv4_score_mw_sum_ctx

【变体差分】
本列是 DeepSeek V4 Flash 模型在 ctx 轨上的媒体权威性加权情感基分的银行-年求和。模型维度上, deepseekv4 是三家中唯一直连 api.deepseek.com 的一家 (另两家经 OpenLux 路由), 其情感基分 deepseekv4_score_ctx 由该模型独立的思维链判定产生, 与 gemini31、gpt54nano 两家 co-equal 并排, 互为跨厂商稳健性、不分主次; per-model 采用独立降级语义, 即某一家缺席只掉自己这一族列, 不触发家族性的 both-or-neither 连坐。轨道维度上, ctx 轨的文本是标题 prepend 之后加上含目标银行句的上下文窗口 (银行邻近证据窗), 而非全文; 在 full-only 留篇门控下, ctx 是 conditional-on-full 的测度轨, 其银行-年行宇宙是 full 留篇集的子集, 但加权与求和逐轨独立, 分子分母不与 full 或 ss 互借。加权因子为 media_authority_weight (均值归一化后的媒体权威度), 逐篇乘到 deepseekv4_score_ctx 再对该银行-年求和。本列作为分子, 下游与 ctx 轨的有效篇数权重和相除得到 deepseekv4_tone_mw_ctx。用大白话说, 它回答的是"如果只读靠近银行的那几句上下文, 并且给权威媒体的报道更大话语权, DeepSeek 这一家在这一银行这一年读出来的正负情感累加是多少"。它与等权版本 (直接对情感基分求和、不乘媒体权重) 以及跟风衰减加权版本 (hw 家族, 按抄稿检测门槛打折) 属于同构念的不同称重口径, 三种加权互为稳健性、并排使用, 用来证明主结论不依赖某一种称重方案。之所以保留逐模型分子而不直接提供合并后的加权语调, 是因为跨厂商差异本身是一个待检验的稳健性维度: 保留 deepseekv4 一家的加权分子, 才能在下游让它与 gemini31、gpt54nano 的同轨列做并排对照。铁律: 本列与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混入同一 over-identified Hansen J。

## VAR: deepseekv4_score_mw_sum_full

【变体差分】
本列是 DeepSeek V4 Flash 模型在 full 轨上的媒体权威性加权情感基分的银行-年求和, 是本家族中最接近"主口径"的一列, 因为 full 轨是留篇门控的唯一判定轨 (2026-06-29 full-only): 一篇报道是否算作银行金融科技报道, 只看 full 轨的验证结果。full 轨文本为标题 prepend 后拼接完整正文, 信息量最全, 也最贴近下游主回归对"篇"的定义。模型维度上, deepseekv4 直连 api.deepseek.com, 与经 OpenLux 路由的 gemini31、gpt54nano 两家 co-equal, 互为跨厂商稳健性、不分主次, per-model 独立降级。计算上, media_authority_weight 逐篇乘到 deepseekv4_score_full 上再对银行-年求和; 下游 deepseekv4_tone_mw_full 以本列为分子、以该模型 full 轨有效篇数的权重和为分母 (valid-mask 分母, 保证分子分母同域)。因 full 轨行宇宙即完整留篇集 (而非子集), 本列在三轨中样本最完整、方差最稳。用大白话说, 它回答的是"读完整篇报道、并且让权威财经媒体的声音占更大分量之后, DeepSeek 一家在这一银行这一年读出来的正负情感累加是多少"。它与同名的等权求和以及跟风衰减加权 (hw) 版本属于同一构念下的三种称重口径, 三者互为稳健性、并排使用, 并非主次关系; 无后缀或某一称重版本被当作"主口径"只是历史命名与门控便利, 不代表它在计量上优先。本列作为分子在下游被 valid-mask 分母相除, 分母只累计 DeepSeek 判定为有效的那些篇的媒体权重, 从而保证分子分母同域、不因该模型缺标而虚高或虚低。铁律仍然适用: 三家模型三轨九列各自 just-identified 并排, 严禁把 full 与 ctx/ss 的加权分子混进同一 over-identified Hansen J; 跨模型比较交由根级 rwolf FWER 模板处理, 本列不承担合并推断。

## VAR: deepseekv4_score_mw_sum_ss

【变体差分】
本列是 DeepSeek V4 Flash 模型在 ss 轨上的媒体权威性加权情感基分的银行-年求和。ss 轨是三轨中最严格的文本口径: 文本为标题 prepend 后加上"目标银行与金融科技词在同一句共现"的句子及其上下窗, 聚焦银行与金科真正同句关联的语义证据。ss 轨采用镜像 ctx 的回退语义: 当某篇报道不存在银行与金科同句共现时, content_ss 回退为全文正文, 并置 ss_is_fallback=True (与该轨共享有效篇数分母)。在 full-only 门控下 ss 亦为 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, 但加权求和逐轨独立、不与 full/ctx 互借分子。模型维度上 deepseekv4 直连 api.deepseek.com, 与另两家 co-equal 并排、互为稳健性、per-model 独立降级。早期试跑 T=2 语料上, ss 轨因同句共现稀疏可能出现较多回退与近零方差, 属预期退化, 生产期 T=19 恢复正常。本列作为分子, 下游相除得 deepseekv4_tone_mw_ss。用大白话说, 它回答的是"只挑出银行和金融科技真正被写在同一句里的那些片段, 再让权威媒体的报道占更大分量, DeepSeek 一家在这一银行这一年读出来的加权情感累加是多少"。相比 ctx 轨只要求银行邻近, ss 轨额外要求金融科技词也同句出现, 因此它测的是更紧的银行-金科语义关联, 与 full、ctx 两轨互为稳健性、并排使用, 用来检验主结论是否随语义定位窗口的松紧而改变。它同样与等权求和及跟风衰减加权 (hw) 版本构成同构念的多种称重口径。铁律: 与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混入同一 over-identified Hansen J。

## VAR: gemini31_score_mw_sum_ctx

【变体差分】
本列是 gemini-3.1-flash-lite 模型 (经 OpenLux 路由) 在 ctx 轨上的媒体权威性加权情感基分的银行-年求和。模型维度上, gemini31 与 gpt54nano 同经 OpenLux 端点、与直连 api.deepseek.com 的 deepseekv4 分属不同来源, 三家 co-equal 并排, 互为跨厂商稳健性、不分主次, per-model 独立降级。其情感基分 gemini31_score_ctx 来自该模型独立的思维链真伪与情感判定, 不做跨模型平滑。轨道维度上, ctx 轨文本是标题 prepend 后加含目标银行句的上下文窗口, 在 full-only 留篇门控下为 conditional-on-full 测度轨, 行宇宙是 full 留篇集的子集, 加权与求和逐轨独立。计算上, media_authority_weight 逐篇乘到 gemini31_score_ctx 上再对该银行-年求和; 下游 gemini31_tone_mw_ctx 以本列为分子、以 ctx 轨该模型有效篇数权重和为分母。本列反映"若只看银行邻近上下文, 且按媒体权威度称重, Gemini 一家读出的加权情感总量"。与直连 api.deepseek.com 的 deepseekv4 相比, gemini31 与 gpt54nano 共用 OpenLux 端点, 这一路由差异本身不进入情感判定逻辑, 但保留逐厂商分子有助于识别可能的模型系统性偏差。它同样与等权求和及跟风衰减加权 (hw) 版本构成同一构念下的多种称重口径, 三种加权互为稳健性、并排使用, 用来证明结论不依赖任一称重方案; 也与词典、BERT 家族的同名 mw 列构成三法互证, 即字典法、编码器法与生成式模型法各自读出的加权情感并排对照, 而非相互替代。铁律: 与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混进同一 over-identified Hansen J。

## VAR: gemini31_score_mw_sum_full

【变体差分】
本列是 gemini-3.1-flash-lite 模型 (经 OpenLux 路由) 在 full 轨上的媒体权威性加权情感基分的银行-年求和。full 轨是留篇门控的唯一判定轨 (full-only, 2026-06-29), 文本为标题 prepend 后拼接完整正文, 行宇宙即完整留篇集而非子集, 因此在三轨中本列样本最完整、方差最稳。模型维度上, gemini31 与同经 OpenLux 的 gpt54nano、直连 api.deepseek.com 的 deepseekv4 三家 co-equal 并排, 互为跨厂商稳健性、不分主次, per-model 独立降级 (Gemini 一家缺席仅掉自身族列)。计算上, media_authority_weight 逐篇乘到 gemini31_score_full 上再对银行-年求和; 下游 gemini31_tone_mw_full 以本列为分子、以该模型 full 轨有效篇数的权重和为 valid-mask 分母, 分子分母严格同域。相较词典与 BERT 家族的同名 mw 加权列, 本列的情感基分来自生成式模型的整体语义判定而非词频或编码器概率, 三法之间互为稳健性、并排使用。用大白话说, 它回答的是"读完整篇报道、并让权威媒体占更大分量之后, Gemini 一家在这一银行这一年读出来的正负情感累加是多少"。保留 Gemini 一家的加权分子而不并入合并语调, 是为了让它与 DeepSeek、GPT 的同轨列做跨厂商稳健性对照; 三家中任何一家出现系统性偏差都可通过并排比较暴露, 这正是采用多模型投票与三角验证而非单一模型的方法学初衷。铁律: 三家模型三轨九列各自 just-identified 并排, 严禁把 full 与 ctx/ss 的加权分子混进同一 over-identified Hansen J; 跨模型合并推断交由根级 rwolf FWER 模板。

## VAR: gemini31_score_mw_sum_ss

【变体差分】
本列是 gemini-3.1-flash-lite 模型 (经 OpenLux 路由) 在 ss 轨上的媒体权威性加权情感基分的银行-年求和。ss 轨文本为标题 prepend 后加"目标银行与金融科技词同句共现"的片段窗, 是三轨中语义定位最严格的口径, 采用镜像 ctx 的回退: 无同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True。在 full-only 门控下 ss 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集的子集, 加权求和逐轨独立、不与 full/ctx 互借分子。模型维度上, gemini31 与 gpt54nano 同经 OpenLux、与直连 api.deepseek.com 的 deepseekv4 分属不同来源, 三家 co-equal 并排、互为稳健性、per-model 独立降级。计算上, media_authority_weight 逐篇乘到 gemini31_score_ss 再对银行-年求和; 下游相除得 gemini31_tone_mw_ss。早期试跑 T=2 上 ss 轨因同句共现稀疏可能大量回退、方差趋零, 属预期退化, 生产 T=19 恢复。用大白话说, 它回答的是"只挑出银行和金融科技被写在同一句里的片段, 再让权威媒体占更大分量, Gemini 一家在这一银行这一年读出来的加权情感累加是多少"。它与 full、ctx 两轨互为稳健性、并排使用, 用来检验主结论是否随语义定位窗口的松紧改变; 也与等权求和及跟风衰减加权 (hw) 版本构成同一构念下的多种称重口径。ss 轨的回退设计保证了即便没有严格同句共现的报道也不被丢弃, 而是优雅降级为全文口径并以哨兵列标记, 从而维持分母的可解释性。铁律: 与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混入同一 over-identified Hansen J。

## VAR: gpt54nano_score_mw_sum_ctx

【变体差分】
本列是 gpt-5.4-nano 模型 (经 OpenLux 路由) 在 ctx 轨上的媒体权威性加权情感基分的银行-年求和。模型维度上, gpt54nano 与同经 OpenLux 的 gemini31、直连 api.deepseek.com 的 deepseekv4 三家 co-equal 并排, 互为跨厂商稳健性、不分主次, per-model 独立降级; 其情感基分 gpt54nano_score_ctx 由该模型独立思维链判定产出, 不做跨模型平滑。轨道维度上, ctx 轨文本是标题 prepend 后加含目标银行句的上下文窗口, 在 full-only 留篇门控下为 conditional-on-full 测度轨, 行宇宙是 full 留篇集的子集, 加权与求和逐轨独立、分子分母不与 full/ss 互借。计算上, media_authority_weight 逐篇乘到 gpt54nano_score_ctx 再对该银行-年求和; 下游 gpt54nano_tone_mw_ctx 以本列为分子、以 ctx 轨该模型有效篇数权重和为分母。本列刻画"仅看银行邻近上下文且按媒体权威度称重时, GPT 一家读出的加权情感总量", 与另两家的同轨列并排构成跨厂商稳健性对照。它与等权求和及跟风衰减加权 (hw) 版本属于同一构念下的多种称重口径, 三种加权互为稳健性、并排使用; 也与词典、BERT 家族的同名 mw 列构成字典法、编码器法与生成式模型法的三法互证。保留 GPT 一家的加权分子而不并入合并语调, 是为了在下游让它与 DeepSeek、Gemini 的同轨列做并排对照, 从而把跨厂商差异当作待检验的稳健性维度而非提前平滑掉。用大白话说, 它回答的是"只读靠近银行的那几句、并让权威媒体占更大分量, GPT 这一家在这一银行这一年读出来的正负情感累加是多少"。铁律: 与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混进同一 over-identified Hansen J。

## VAR: gpt54nano_score_mw_sum_full

【变体差分】
本列是 gpt-5.4-nano 模型 (经 OpenLux 路由) 在 full 轨上的媒体权威性加权情感基分的银行-年求和。full 轨是留篇门控的唯一判定轨 (full-only, 2026-06-29), 文本为标题 prepend 后拼接完整正文, 行宇宙即完整留篇集, 本列在三轨中样本最完整、最贴近下游主回归对"篇"的定义。模型维度上, gpt54nano 与同经 OpenLux 的 gemini31、直连 api.deepseek.com 的 deepseekv4 三家 co-equal 并排, 互为跨厂商稳健性、不分主次, per-model 独立降级 (GPT 一家缺席仅掉自身族列)。计算上, media_authority_weight 逐篇乘到 gpt54nano_score_full 上再对银行-年求和; 下游 gpt54nano_tone_mw_full 以本列为分子、以该模型 full 轨有效篇数的权重和为 valid-mask 分母, 分子分母严格同域。相较等权版本, 本列抑制了低权威来源的稀释, 使权威财经媒体的极性判定在加权总量中占更大份额。用大白话说, 它回答的是"读完整篇报道、并让权威媒体占更大分量之后, GPT 一家在这一银行这一年读出来的正负情感累加是多少"。它与同名的等权求和以及跟风衰减加权 (hw) 版本属于同一构念下的三种称重口径, 三者互为稳健性、并排使用, 不分主次; 无后缀或某一版本被视作"主口径"只是历史命名与门控便利, 不代表计量上的优先。因 full 轨是留篇门控的唯一判定轨, 本列在三轨中样本最完整、方差最稳, 常被论文选作展示口径, 但其稳健性正由 ctx、ss 两轨及另两家模型的同名列共同背书。铁律: 三家模型三轨九列各自 just-identified 并排, 严禁把 full 与 ctx/ss 的加权分子混进同一 over-identified Hansen J; 跨模型族级错误率控制交由根级 rwolf FWER 模板, 本列不承担合并推断。

## VAR: gpt54nano_score_mw_sum_ss

【变体差分】
本列是 gpt-5.4-nano 模型 (经 OpenLux 路由) 在 ss 轨上的媒体权威性加权情感基分的银行-年求和。ss 轨文本为标题 prepend 后加"目标银行与金融科技词同句共现"的片段窗, 是三轨中最严格的语义定位口径, 采用镜像 ctx 的回退语义: 无同句共现时 content_ss 回退全文正文并置 ss_is_fallback=True (与该轨共享有效篇数分母)。在 full-only 门控下 ss 为 conditional-on-full 测度轨, 行宇宙是 full 留篇集的子集, 加权求和逐轨独立、不与 full/ctx 互借分子。模型维度上, gpt54nano 与 gemini31 同经 OpenLux、与直连 api.deepseek.com 的 deepseekv4 分属不同来源, 三家 co-equal 并排、互为稳健性、per-model 独立降级。计算上, media_authority_weight 逐篇乘到 gpt54nano_score_ss 再对银行-年求和; 下游相除得 gpt54nano_tone_mw_ss。早期试跑 T=2 上 ss 轨因同句共现稀疏可能大量回退、方差趋零, 属预期退化, 生产 T=19 恢复正常。用大白话说, 它回答的是"只挑出银行和金融科技被写在同一句里的片段, 再让权威媒体占更大分量, GPT 一家在这一银行这一年读出来的加权情感累加是多少"。它与 full、ctx 两轨互为稳健性、并排使用, 用来检验主结论是否随语义定位窗口的松紧改变; 也与等权求和及跟风衰减加权 (hw) 版本构成同一构念下的多种称重口径。ss 轨的镜像回退设计保证没有严格同句共现的报道不被丢弃, 而是优雅降级为全文口径并以哨兵列标记, 维持分母的可解释性与逐轨独立。铁律: 与其余八列各自 just-identified 并排, 严禁把不同模型或不同轨的加权分子混入同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Carlson, N. A., & Burbano, V. (2026). The use of LLMs to annotate data in management research: Foundational guidelines and warnings. Strategic Management Journal, 47(3), 699-725. https://doi.org/10.1002/smj.70023
Ludwig, J., Mullainathan, S., & Rambachan, A. (2026). Large language models: An applied econometric framework. Annual Review of Economics. https://doi.org/10.1146/annurev-economics-120925-105620
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Farquhar, S., Kossen, J., Kuhn, L., & Gal, Y. (2024). Detecting hallucinations in large language models using semantic entropy. Nature, 630(8017), 625-630. https://doi.org/10.1038/s41586-024-07421-0
Rathje, S., Mirea, D.-M., Sucholutsky, I., Marjieh, R., Robertson, C. E., & Van Bavel, J. J. (2024). GPT is an effective tool for multilingual psychological text analysis. Proceedings of the National Academy of Sciences, 121(34), e2308950121. https://doi.org/10.1073/pnas.2308950121
Kirtac, K., & Germano, G. (2024). Sentiment trading with large language models. Finance Research Letters, 62, 105227. https://doi.org/10.1016/j.frl.2024.105227
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
<!-- rendered-citations:end -->
