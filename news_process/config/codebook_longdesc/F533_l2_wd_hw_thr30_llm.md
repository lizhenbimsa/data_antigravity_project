---
family_id: F533
columns:
- sum_wd_hw_thr30_llm_ctx
- sum_wd_hw_thr30_llm_full
- sum_wd_hw_thr30_llm_ss
unit: 无量纲权重之和 (跟风衰减权重的银行-年加总, 用作分母)
formula: 'sum_wd_hw_thr30_llm{track} = Σ_i∈bank-year herd_weight{track}_thr30_i, 其中 herd_weight{track}_thr30_i 仅对 llm_vote_score{track}_i 非缺失的篇章 i 取值 (否则该篇不计入求和); track ∈ {_full, _ctx, _ss}'
producer: pipeline\panel\encode.py ; pipeline\panel\runner.py
upstream: []
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
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: 'Giving content to investor sentiment: The role of media in the stock market'
  venue: Journal of Finance
  vol: '62'
  issue: '3'
  pages_or_artno: 1139-1168
- doi: 10.1073/pnas.2305016120
  type: journal
  authors: Gilardi, F., Alizadeh, M., & Kubli, M.
  year: 2023
  title: ChatGPT outperforms crowd workers for text-annotation tasks
  venue: Proceedings of the National Academy of Sciences
  vol: '120'
  issue: '30'
  pages_or_artno: e2305016120
- doi: 10.17016/FEDS.2026.020
  type: wp
  authors: Hansen, A. L.
  year: 2026
  title: Validating large language model annotations
  venue: FEDS Working Paper No. 2026-020, Federal Reserve Board
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: Wisdom of the silicon crowd LLM ensemble prediction capabilities rival human crowd accuracy
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: "10.1093/restud/rdaf037"
  type: "journal"
  authors: "Kwon, S. Y., & Tang, J."
  year: 2026
  title: "Extreme Categories and Overreaction to News"
  venue: "Review of Economic Studies"
  vol: "93"
  issue: "2"
  pages_or_artno: "1137-1166"
new_dois: []
---

## CORE

【构念与来源】
本家族的三个列 (sum_wd_hw_thr30_llm_full / _ctx / _ss) 是"跟风衰减权重" (herd decay weight, HW) 阈值敏感性网格里, LLM 投票语调测度 (llm_vote_score) 在阈值 τ=0.30 处的银行-年加权分母和, 三轨 full/ctx/ss 各一份。列名前缀 "wd" 取"weight denominator"之意: 它不是情感得分本身, 而是把逐篇跟风衰减权重 (herd_weight{track}_thr30) 加总起来, 供下游把 llm_vote_score_hw_thr30_sum{track} 除以本列, 还原成"阈值取 0.30 时的加权平均语调"。构念根子在 Tetlock (2011, 及其 2007 J. Finance 前作确立的"媒体语调作投资者情绪代理"框架) 的洞察: 当多家媒体在同一时间窗内报道口径高度雷同 ("扎堆"/herd) 时, 简单等权平均会让重复报道的语调被过度放大, 需要按"该篇与同期同银行报道的相似度"打折权重, 越像扎堆稿的篇章权重越低。跟风衰减权重的构造与判定发生在 stage 24 (herd_decay_processor), 阈值敏感性网格 (herd_sensitivity_grid, 由 config/panel.yaml::herd_detection.sensitivity_thresholds 驱动) 在此基础上额外产出一组备选阈值下的权重列 herd_weight{track}_{tag}, tag=thr30 即备选阈值 τ=0.30 (与生产口径 canonical τ=0.35 相对)。

【方法学与计算】
计算发生在两处: (1) pipeline/panel/runner.py 步骤 3d-2 里, 对每个 (tag, track) 组合, 若 herd_weight{track}_{tag} 与 llm_vote_score{track} 两列同时存在, 则令 hw_t = herd_weight{track}_{tag} 的缺失值填 1.0 (不打折), 再生成 _wd_hw_{tag}_llm{track} = hw_t.where(llm_vote_score{track}.notna()) — 即只在 LLM 投票分数本身非缺失的行才保留该权重, 否则置缺失, 这样分子 (llm_vote_score_hw_{tag}_sum{track}) 与分母 (本列) 的非缺失行集合严格对齐, 避免分子分母"域不一致"导致加权平均系统性偏误。(2) pipeline/panel/encode.py 的聚合阶段, 把篇章级 _wd_hw_{tag}_llm{track} 按银行-年做 sum 聚合, 得到本家族的三个面板列。needs_review 均为 false, 三列均为 standard tier, 无 core 差分理由字段填写 — 因为三列彼此的唯一差异就是三轨文本口径, 属于本仓文档规范里"轨道并排、非嵌套"的标准差分模式, 不构成需要单列 core 长文的额外识别策略。

【文献定位】
分母口径本身依托三条互补文献线索定位: 一是 LLM 文本标注的方法学纪律 (de Kok 2025, Management Science) 强调 temperature=0、prompt 冻结、结果可复现是把生成式 LLM 用于会计/金融文本分析的前提, 本仓 stage 21 三家 LLM 投票 (gpt54nano/gemini31/deepseekv4) 与本处 herd 权重敏感性网格共享同一套"冻结口径 + 参数化阈值梯子"的设计哲学; 二是 Gilardi, Alizadeh & Kubli (2023, PNAS) 与 Hansen (2026, FEDS WP) 提供 LLM 标注质量与一致性验证的经验基准, 支撑"LLM 投票语调"作为可信测度输入到 herd 权重加权体系中的正当性; 三是 Tetlock (2007, Journal of Finance) 确立媒体语调是投资者情绪的可观测代理这一构念根基, 是 herd 衰减权重存在的动机——防止扎堆报道人为放大媒体语调信号; Schoenegger 等 (2024, Science Advances) 在预测市场任务上考察多家 LLM 集成 (ensemble) 后发现其准确率可媲美人类群体智慧, 该发现本身并非直接针对媒体语调或跟风权重构念, 而是作为一条跨学科佐证, 类比性地说明"多主体独立判断加总优于单一主体"这一统计逻辑在 LLM 场景下同样成立, 从而间接支持本仓"多家 LLM (gpt54nano/gemini31/deepseekv4) 投票 + 权重加总"的复合测度设计思路, 不作为该设计的直接实证依据。三轨/阈值梯子均遵循本仓一贯口径: full/ctx/ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验; τ=0.30 与 canonical τ=0.35 (及网格中其余阈值) 同理各自并排, 用于证明主回归结论不依赖单一门槛取值的武断选择, 而非彼此嵌套或可加分解。 就「阈值取值须并排检验而非默认某一档」这一取向, Kwon 与 Tang (2026) 可作一条构念侧的旁证: 该文在诊断性预期框架下检验涵盖 24 类企业新闻的语料, 发现基本面分布越极端的新闻类别, 公告后的收益反转与成交量放大越明显, 提示新闻的类别归属并非无信息含量的标签、类别边界本身即携带经济含义, 因而把连续量映射为类别或子集时的边界取值不宜被视为中性的技术细节。迁移边界须严格限定: 原文的类别是语料中外生既有的新闻题材, 其离散化发生在投资者信念形成的行为偏误层面; 原文既未做连续信号的离散化, 也未提出「研究者须显式检验阈值」这一方法学规范, 更未涉及文本相似度、跟风衰减权重、LLM 或加权分母, 其类别边界与本列研究者在跟风相似度检测网格上选定的 τ=0.30 无对应物、数值不可比。
## VAR: sum_wd_hw_thr30_llm_ctx

【变体差分】
本列是 track=_ctx 轨的跟风衰减权重阈值敏感性分母和, 文本来源为 content_ctx (标题+目标银行实体窗口物化文本, stage 14 materialize_ctx 产出)。分子分母同域对齐规则与 full/ss 轨完全一致: hw_t = herd_weight_ctx_thr30 (缺失填 1.0), 再用 llm_vote_score_ctx 的非缺失掩码筛出有效行求和。ctx 轨的特殊之处在于其"扎堆"判定与权重打折发生在实体窗口文本层面——若某银行在同一时间窗内多篇报道的 ctx 窗口文本高度相似 (即便全文措辞有差异), 该篇 ctx 权重也会被压低。当某篇文章不存在银行∧金科的实体窗口可物化时, content_ctx 按既定回退语义退化为其它可用文本 (ctx_is_fallback=True), 对应的 herd_weight_ctx 及 llm_vote_score_ctx 仍按该回退文本计算, 不会因回退而被排除出本列求和, 只要 llm_vote_score_ctx 本身非缺失。作为 full-only 留篇门控 (2026-06-29 生产口径) 下的 conditional-on-full 测度/稳健性轨, ctx 轨的行宇宙是 full 轨留篇集的子集, 但本列的逐轨分子/分母仍按 ctx 轨自身独立计算, 不借用 full 轨的权重或分母, 与家族其余两轨 (full/ss) 之间保持 just-identified 并排、互为稳健性、禁止混入同一 over-identified Hansen J 的铁律。使用场景是把 llm_vote_score_hw_thr30_sum_ctx 除以本列, 得到"阈值 0.30 时 ctx 轨加权平均 LLM 投票语调"的稳健性变体, 与 canonical τ=0.35 的 ctx 轨版本并列比较, 检验主回归系数是否随阈值取值而系统性漂移。

## VAR: sum_wd_hw_thr30_llm_full

【变体差分】
本列是 track=_full 轨 (标题+全文正文, 无实体窗口裁切) 的跟风衰减权重阈值敏感性分母和, 是三轨中口径最宽的一支, 也是 P1 主线 treatment (llm_vote_tone_full 等) 所在的 full-only 留篇门控主轨——stage 21 是否判定"一篇银行金科报道"进入留篇集, 只看 llm_vote_tone_full 是否为 verified True, ctx/ss 两轨的行宇宙均是 full 轨留篇集的子集。因此本列覆盖的银行-年篇章数在三轨里通常最多 (或至少不少于 ctx/ss), 是与主回归 DV 直接配套的分母版本。计算规则同样是 herd_weight_full_thr30 缺失填 1.0 后, 用 llm_vote_score_full 非缺失掩码筛出有效行再按银行-年求和; 分子对应列为 llm_vote_score_hw_thr30_sum_full。τ=0.30 是阈值敏感性网格 (herd_sensitivity_grid, 由 config/panel.yaml::herd_detection.sensitivity_thresholds 驱动) 中的一个备选刻度, 与生产口径 canonical τ=0.35 (对应无 _thrNN 后缀的 sum_herd_weight_full 等列) 各自独立聚合、各自 just-identified, 互为稳健性并排而非替代关系; 全部阈值刻度共享同一个"仅对 LLM 投票主测度族 (score/cont) 做逐 τ 网格"的设计取舍, 是为了避免阈值梯子 × 全部 11 个情感测度族 (LLM/词典/BERT 交叉) 组合爆炸而做出的范围收窄, 详见 encode.py 注释 F5b 段。下游 Stata 复现时, 研究者会用 τ 遍历若干阈值刻度逐列重跑主回归, 用本列 (及其它 τ 刻度的同名列) 做分母, 证明"多少相似度算扎堆"这一武断的 0.35 门槛选择, 不驱动主结论方向或显著性。

## VAR: sum_wd_hw_thr30_llm_ss

【变体差分】
本列是 track=_ss 轨 (标题+银行∧金科同句±N窗, N 由 config/filtering.yaml::context_window.ss_sentence_radius 控制, 默认 1) 的跟风衰减权重阈值敏感性分母和, 是三轨中文本口径最窄、判据最严格的一支。计算规则与 full/ctx 轨同构: herd_weight_ss_thr30 缺失填 1.0, 用 llm_vote_score_ss 非缺失掩码筛出有效行按银行-年求和, 对应分子列为 llm_vote_score_hw_thr30_sum_ss。ss 轨的回退语义严格镜像 ctx 轨: 若某篇文章不存在银行与金科词在同一句 (±N 窗) 内共现, content_ss 按既定规则回退为全文 body, ss_is_fallback 置 True, 该篇的 herd_weight_ss 与 llm_vote_score_ss 仍按回退后的文本计算并计入本列求和, 不因回退而被剔除或单独标记降级——回退只影响文本来源, 不影响权重与投票分数是否有效这一判定标准。ss 轨同样是 full-only 留篇门控下 conditional-on-full 的稳健性测度, 行宇宙是 full 轨留篇集的子集, 但分子分母口径完全在 ss 轨自身内闭环计算, 不借用 full 或 ctx 轨的权重。三轨 (full/ctx/ss) 在阈值 τ=0.30 处的这一组分母列, 与 canonical τ=0.35 及网格中其它阈值刻度的同名列, 共同构成一张"文本口径 × 判定门槛"的稳健性矩阵: 任意两个格子都各自 just-identified 并排比较, 严禁把跨轨或跨阈值的分子分母混入同一个 over-identified 的 Hansen J 检验, 也不应把三轨或多阈值口径当作可加分解的成分相加, 而应各自独立汇报、共同印证结论的稳健性边界。

<!-- rendered-citations:begin -->
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Gilardi, F., Alizadeh, M., & Kubli, M. (2023). ChatGPT outperforms crowd workers for text-annotation tasks. Proceedings of the National Academy of Sciences, 120(30), e2305016120. https://doi.org/10.1073/pnas.2305016120
Hansen, A. L. (2026). Validating large language model annotations. FEDS Working Paper No. 2026-020, Federal Reserve Board [Working Paper]. https://doi.org/10.17016/FEDS.2026.020
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Kwon, S. Y., & Tang, J. (2026). Extreme Categories and Overreaction to News. Review of Economic Studies, 93(2), 1137-1166. https://doi.org/10.1093/restud/rdaf037
<!-- rendered-citations:end -->
