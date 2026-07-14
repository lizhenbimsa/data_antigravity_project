---
family_id: F563
columns:
- tone_central_media_ctx
- tone_central_media_full
- tone_central_media_ss
unit: 语调得分 (连续, 约 [-1,1] 名义双极区间; LLM 三家投票均分, 银行×年内按中央级媒体子样本聚合均值)
formula: 'tone_central_media{track} = mean_{i∈{银行b报道: 媒体(中文)∈CENTRAL, year=y, track}}(llm_vote_score{track}_i); track ∈ {_full, _ctx, _ss}; CENTRAL 为中央级媒体名单 (中文媒体名匹配), _is_central 派生自 df["媒体(中文)"].isin(CENTRAL)'
producer: pipeline\panel\attention_media.py (中央/地方媒体情感均值主计算; export.py 仅承担 dta 标签映射)
upstream:
- 21_tone_llms (llm_vote_score_full / llm_vote_score_ctx / llm_vote_score_ss, 三家 LLM 多数投票共识分)
- 13_cooccurrence_filter (留篇集; full-only 门控)
- 14_materialize_ctx (content_ctx / content_ss 物化)
- 媒体行政层级名单 CENTRAL (中央级媒体清单, 与 OFFICIAL/MARKET/DEEPDIVE/DAILY 等维度正交)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who Captures the Power of the Pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: The Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: 'Media sentiment, deposit stability and bank systemic risk: Evidence from China'
  venue: International Review of Economics & Finance
  vol: '91'
  pages_or_artno: 1150-1172
new_dois: []
---

## CORE

【构念与来源】
本家族测度中央级媒体对目标银行报道的情感倾向均值, 属 stage 40 面板导出中「媒体异质性」板块下的第④维度: 行政层级分类 (中央级 vs 地方级), 与该板块另外三个正交维度——财经/综合/其他媒体类型 (维度①)、官方/市场化媒体政治取向 (维度⑤⑥)、深度/高频媒体报道节奏 (维度②③)——彼此独立、不互斥, 均建立在同一份银行×金科共现留篇文章的媒体元数据之上。行政层级判据来自数据源自带的「媒体(中文)」名称字段, 与预先维护的中央级媒体名单 CENTRAL 做集合归属匹配 (`df['_is_central'] = df['媒体(中文)'].isin(CENTRAL).astype(int)`), 是逐篇文章级的二值旗标, 与银行/金科共现判据(stage 13)、情感判定(stage 21)分属两条独立信息通道, 互不影响。构念动机源自媒体政治经济学文献对"谁的笔杆子更有力"这一问题的长期关注: 媒体的行政隶属关系与所有制结构会系统性影响其报道立场与治理效应传导路径, You, Zhang & Zhang (2018, *Review of Financial Studies*) 在研究中国资本市场媒体角色时明确区分了党委机关报等中央/官方口径媒体与市场化媒体在信息生产激励上的差异, 发现两类媒体的负面报道对公司治理结果(如高管更替)的作用强度并不相同——这构成本维度"中央级 vs 地方级"划分的直接理论依据: 中央级媒体往往承担更强的政策宣传与舆论引导职能, 其报道基调可能更受政治周期与监管口径影响, 而地方级媒体更贴近区域性银行经营实况与本地舆情, 二者对银行声誉与融资成本的传导机制存在结构性差异, 故有必要在面板中将两类媒体的情感均值分离度量, 而非笼统合并为单一媒体情感指标。

【方法学与计算】
计算管线分两步: 第一步在 `pipeline\panel\attention_media.py` 内, 对已按 `target_bank` × `year` × `track` 三键分组的留篇文章子集, 先以 `_is_central` 旗标切出中央级子样本 (`is_c=1`) 与地方级子样本 (`is_c=0`), 再分别对 `llm_vote_score{track}` 逐组取算术均值, 得到 `tone_central_media{track}` 与 `tone_local_media{track}` 两列, 随后左连接回主面板 (`how='left'`, 缺组则该 bank-year-track 单元格为 NaN, 而非误填 0)。第二步同一函数内紧接着计算 `tone_gap_central_local{track} = tone_central_media{track} - tone_local_media{track}`, 落在姊妹家族中, 提供中央/地方媒体基调差的直接对比列(本家族本身不含该差值列, 仅覆盖三轨均值本身)。`llm_vote_score{track}` 的来源是 stage 21 三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票共识打分, 与嵌入模型无关, 与词典法(`tone_words`)/BERT 三模型法(`tone_berts`)是三条并列的独立情感测度通道, 本家族只消费 LLM 投票通道。分母口径继承留篇门控: 2026-06-29 起「是否算一篇银行金科报道」的判定唯一锚定 `llm_verified_full == True` (full-only 门控), `_ctx`/`_ss` 两轨的行宇宙是 full 留篇集的子集, 属 conditional-on-full 的稳健性/补充测度轨, 而非独立样本口径——这意味着三轨分子样本量不同, `_ctx`/`_ss` 天然弱于或等于 `_full`, 差异本身即含信息(反映情感判定对文本窗口的敏感度), 不代表数据缺陷。若某 bank-year 单元格内不存在任何中央级媒体报道(该银行当年报道全部来自地方媒体), 则该单元格 `tone_central_media{track}` 为 NaN, 而非 0, 使用者应区分"无中央级报道"与"中央级报道情感中性(0分)"两种不同状态, 避免误读缺失为零。

【文献定位】
本家族属于媒体情感异质性(media sentiment heterogeneity)测度谱系, 其行政层级切分设计直接呼应 You, Zhang & Zhang (2018, *Review of Financial Studies*) 关于中国媒体"谁执笔谁有权"的核心洞察——该文发现官方主管媒体(党委机关报)的负面报道并不能引发预期的公司治理响应(如高管更替), 而市场化媒体的负面报道则具有显著的治理约束效应, 揭示了媒体所有制/隶属关系是调节媒体信息传导有效性的关键变量, 而非单纯的报道数量或情感极性问题。这一发现为本家族"分轨报告中央级与地方级媒体基调"而非笼统合并提供了直接的构念校验依据: 若中央级与地方级媒体的报道基调系统性有别, 混同计算的整体媒体情感均值将掩盖这一异质性、导致对媒体影响力传导机制的误判。在情感测度层面, 本家族延续 Tetlock (2007, *Journal of Finance*) 开创的"以媒体文本内容度量投资者情绪"传统, 并采纳 Fang, Wang, Wang & Yuan (2024, *International Review of Economics & Finance*) 面向中国银行业媒体情感-系统性风险关联研究的银行×年聚合口径, 将情感测度落到银行×年×媒体子类别的细粒度单元, 便于后续检验中央级媒体基调对银行融资成本、存款稳定性等结果变量的差异化传导路径。

## VAR: tone_central_media_full

【变体差分】
本列取 `track=_full` 轨, 情感源列为 `llm_vote_score_full`, 计算范围是标题+全文正文的完整文本经三家 LLM 多数投票产生的共识情感分, 在中央级媒体子样本内按银行×年取均值。`_full` 轨是留篇门控的唯一锚定轨(2026-06-29 起 `llm_verified_full == True` 是"是否算一篇银行金科报道"的唯一判据), 因此本列的分子样本量在三轨中最大、最接近该 bank-year 单元格内全部中央级媒体报道的真实覆盖, `_ctx`/`_ss` 两轨则是以 `_full` 留篇集为行宇宙的条件子测度。作为家族 canonical 轨, `_full` 与 `_ctx`、`_ss` 三者在计量意义上各自 just-identified 并排、互为稳健性、不分主次——即三轨情感均值均可独立作为处理变量或控制变量放入回归, 但绝不应混入同一个 over-identified 的 Hansen J 过度识别检验中联合使用, 因为三者共享同一底层情感投票机制、仅文本窗口不同, 联合使用会人为夸大过度识别自由度并违反工具外生性假设的独立性前提。使用者在做全文本 vs 局部文本窗口的稳健性检验时, 应以 `_full` 为主报告口径, `_ctx`/`_ss` 作平行展示而非替代。由于 `_full` 轨的分母覆盖了该银行当年全部中央级媒体留篇报道(不受实体窗口或同句共现二次筛选影响), 它也是判断"中央级媒体报道基调是否随全文语境展开而系统性偏移"的基准参照点: 若某银行的 `_full` 均值与其对应 `_ctx`/`_ss` 均值出现明显缺口, 应结合 `tone_gap_central_local_full` 与该银行的报道结构一并解读, 而不宜孤立看待单一轨的数值。

## VAR: tone_central_media_ctx

【变体差分】
本列取 `track=_ctx` 轨, 情感源列为 `llm_vote_score_ctx`, 计算范围是标题+目标实体(银行/金科)窗口文本(由 stage 14 `ctx_materializer` 物化 `content_ctx`, `prepend_title` 拼接标题)经三家 LLM 投票产生的共识分, 在中央级媒体子样本内按银行×年取均值。`_ctx` 轨行宇宙是 `_full` 留篇集的子集(conditional-on-full), 即仅对已被 `llm_verified_full` 判定为有效银行金科报道的文章, 再用实体窗口文本重新跑一次情感投票, 目的是检验情感基调是否对"读全文"与"只读实体附近段落"两种文本呈现方式敏感——若二者高度一致, 说明中央级媒体的情感倾向不依赖于冗余上下文；若出现系统性偏离, 则提示全文语境(如报道中夹杂的其他银行/行业信息)对情感判定有实质影响。本列与 `_full`、`_ss` 同为 just-identified 并排的互为稳健性测度, 三者绝不可混入同一 over-identified Hansen J 检验联合使用。若某中央级媒体报道未通过 `_ctx` 轨自身的有效性判定或缺少 `content_ctx` 物化文本, 对应的 `llm_vote_score_ctx` 为缺失值, 不参与该 bank-year 单元格的均值计算, 分母随之收缩(而非借用 `_full` 分母平摊)。此外, `_ctx` 轨在中央级媒体子样本上格外值得关注的一点是: 中央级媒体的报道篇幅通常较长、常涉及宏观政策背景与多家机构并提, 实体窗口裁剪对情感判定的影响幅度可能大于地方级媒体的短平快报道, 因此比较 `tone_central_media_ctx` 与 `tone_local_media_ctx` 之间的差距时, 应意识到二者对窗口裁剪的敏感度本身可能不对称, 这是解读 `_ctx` 轨中央/地方对比结果时需要额外留意的方法学细节。

## VAR: tone_central_media_ss

【变体差分】
本列取 `track=_ss` 轨, 情感源列为 `llm_vote_score_ss`, 计算范围是标题+银行与金科词汇同句(或按 `config/filtering.yaml::context_window.ss_sentence_radius` 定义的句子半径窗口, 默认±1句)共现文本经三家 LLM 投票产生的共识分, 在中央级媒体子样本内按银行×年取均值。`_ss` 轨的回退语义镜像 `_ctx`: 当一篇留篇文章内不存在银行∧金科词汇的同句共现时, `content_ss` 回退为全文 body(`ss_is_fallback=True`), 情感投票退化为近似全文口径, 该回退共享与 `_ctx` 相同的 `n_articles` 分母约定, 不会因回退而人为缩小样本。`_ss` 轨判定口径比 `_ctx` 更严格(要求实体真正同句邻近, 而非仅在实体窗口内), 因此在存在真实同句共现的报道子集上, `_ss` 轨的情感分更聚焦于银行与金科业务直接关联的表述, 是三轨中文本窗口最窄、噪声最低但覆盖率也最低的一支。本列与 `_full`、`_ctx` 三者互为稳健性、各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 检验联合估计; 三者对比使用时应各自单独进入回归模型, 观察系数符号与显著性在窄窄窗口下是否依然稳健, 而非把三者堆叠为单一工具变量组。需要额外提醒的是, `_ss` 轨的回退比例(有多少中央级媒体报道触发 `ss_is_fallback=True`)本身随媒体类型而异: 中央级媒体的宏观叙事型报道更可能不出现银行与金科词汇的同句直接并提(二者常分处不同段落), 因而回退发生率可能系统性高于地方级媒体的产品/事件型报道, 使用者在解读 `tone_central_media_ss` 与 `tone_local_media_ss` 的差异时, 应同时核对各自的回退占比, 避免把"文本窗口效应"误读为"媒体基调本身的差异"。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. The Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics & Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
<!-- rendered-citations:end -->