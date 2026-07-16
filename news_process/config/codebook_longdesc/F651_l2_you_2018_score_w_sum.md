---
family_id: F651
columns:
- you_2018_score_w_sum_ctx
- you_2018_score_w_sum_full
- you_2018_score_w_sum_ss
unit: 无量纲得分 (提及密度加权和, 银行-年层面)
formula: 'you_2018_score_w_sum{track} = Σ_{article∈bank-year} (you_2018_score{track} × mention_density_article); 其中 you_2018_score{track} = Σ(final_score) / Σ|final_score| ∈ [-1,+1] (含否定翻转/程度副词/转折三条语言学规则)'
producer: pipeline\sentiment\tone_words.py ; pipeline\panel\runner.py ; pipeline\panel\encode.py
upstream:
- you_2018_score_full
- you_2018_score_ctx
- you_2018_score_ss
- mention_density
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: You, J., Zhang, B., & Zhang, L.
  year: 2018
  title: Who captures the power of the pen?
  venue: The Review of Financial Studies
  vol: '31'
  issue: '1'
  pages_or_artno: 43-96
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: 'Sentiment analysis of economic text: A lexicon-based approach'
  venue: Economic Inquiry
  vol: '63'
  issue: '1'
  pages_or_artno: 125-143
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: Lexicon-based methods for sentiment analysis
  venue: Computational Linguistics
  vol: '37'
  issue: '2'
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族三列是词典法情感测度 you_2018 词典在银行-年面板层面的「提及密度加权 (Value-Weighted, VW) 得分和」, 即银行-年内该银行所有相关报道的 you_2018 情感得分, 按各篇报道内目标银行提及密度加权后求和的分子项, 是构造 VW 语调指标 `you_2018_tone_vw{track}`(= 本列 / `sum_mention_density{track}`) 的中间分子, 也可独立作为「该银行-年被媒体以 you_2018 词典口径赋予的加权情感总量」使用。词典来源为 You, Zhang & Zhang (2018, *Review of Financial Studies*) 构建的中文金融情感词典, 含正面词 1,425 个 / 负面词 1,583 个 (config/tone_dicts.json::you_2018), 是本项目 6 部情感词典之一 (另 5 部为 jiang_2021 / yao_2021 / bian_2021 / du_2022 / loughran_mcdonald_zh_2026), 彼此互为稳健性并排, 不设主次。you_2018 词典同时含 definite(388)/ambiguous(178) 两个子集用于 clarity 测度族 (与本家族的情感极性用法是不同下游消费者, 本家族只用 positive/negative 极性子集)。
提及密度加权 (VW) 的经济学依据是 Hassan et al. (2019, *QJE*, political risk 文本暴露度加权先例) 的构念延伸: 一篇报道对目标银行的「情感信号强度」不应与其他篇文章等权计入, 而应按该银行在该篇文章中的相对提及密度 (mention_density, 银行提及次数占该篇实体提及总量的比重) 加权 — 提及密度越高, 说明该篇报道越以该银行为核心叙事对象, 其情感判断对该银行的代表性越强、应赋予更大权重; 反之若银行只是该篇报道中被顺带提及的多个实体之一, 其情感信号对该银行的归因强度理应打折。

【方法学与计算】
计算分两层。第一层 (文章级, `you_2018_score{track}`): 对每篇文章的文本 (依轨道取 `content_full`/`content_ctx`/`content_ss`, 均已 prepend 标题) 做分词与词典匹配, 命中 you_2018 词典词条时依次应用三条语言学规则 — ①否定翻转 (词前出现否定词, 极性反号); ②程度副词乘子 (词前出现程度副词, 幅度放大/缩小); ③转折让步规则 (转折连词后语义主导权重上调)。逐词计算 `final_score = base_score × degree_multiplier × negation`, 再对全文加总: `normalized_score = Σ(final_score) / Σ|final_score|`, 该值即为 `you_2018_score{track}` ∈ [-1, +1] (自归一化, 分母为零时该篇文章记 NaN/0 按 producer 口径处理)。该篇级得分是含全部三条语言学规则的完整口径 (canonical, 与「词典消融梯度」的 7 个非-full 变体 `you_2018_score_{raw,negonly,degonly,advonly,negdeg,negadv,degadv}{track}` 并排, 本家族对应其中的 full 口径, 消融变体不在本家族范围)。
第二层 (加权与聚合, 本家族三列所在层): 文章级得分先按提及密度加权 `you_2018_score_w{track} = you_2018_score{track} × mention_density`(`pipeline/panel/runner.py` 步骤 3b), 再在银行-年内对该银行全部相关文章求和 `you_2018_score_w_sum{track} = Σ you_2018_score_w{track}`(`pipeline/panel/encode.py` groupby-agg 的 sum 聚合)。该和值本身是构造 VW 语调率的分子, 下游在 `encode.py` 中除以对应轨道的提及密度分母和 `sum_mention_density{track}` 得到 `you_2018_tone_vw{track}` (标准化到 [-1,+1] 附近的加权平均语调); 本列作为未除以分母的原始加权和, 其量纲随该银行-年报道数量与总提及强度增长, 更适合作「该银行-年被媒体关注并赋予情感倾向的总规模」而非纯粹的语调水平度量, 分析时须留意与 `you_2018_tone_vw{track}` 的量纲区分 — 前者是流量 (总量), 后者是密度 (率)。
本家族严格覆盖三轨 full/ctx/ss: full=标题+全文正文; ctx=标题+目标银行实体窗口; ss=标题+银行∧金科词同句 (±可配置句半径) 共现窗口, 若某篇文章无银行∧金科同句共现则 `content_ss` 回退为全文 body 且该篇 `ss_is_fallback=True`(镜像 ctx 的回退语义, 共享 `n_articles` 分母口径)。三轨在留篇门控上均以 `llm_verified_full == True` 的 full 轨留篇集为行宇宙 (2026-06-29 起 full-only 门控), ctx/ss 是 conditional-on-full 的测度轨/稳健性轨, 三轨得分各自独立计算、各自 just-identified 并排, 互为稳健性、不分主次, 禁止将三轨得分混入同一 over-identified Hansen J 设定。

【文献定位】
you_2018 词典法源自 You, Zhang & Zhang (2018, *The Review of Financial Studies*)「Who captures the power of the pen?」一文, 该文构建并验证了针对中国资本市场语境的情感词典, 用以刻画媒体报道文本的情感倾向对市场反应的解释力, 是本项目词典法情感测度族的直接理论与词表来源之一。词典法情感测度整体的方法学定位参照 Du, Huang, Wermers & Wu (2022, *Review of Finance*)对中文金融领域专属情感词典构建必要性的系统论证 (语言与领域特异性使英文通用词典或简单翻译版本失效, 需领域内构建), 以及 Taboada, Brooke, Tofiloski, Voll & Stede (2011, *Computational Linguistics*) 对词典法情感分析中否定/程度副词/转折等语言学规则增强的方法学综述, 本项目的三条规则增强 (负向翻转、程度副词、转折让步) 即沿此传统。提及密度加权聚合的经济学思路呼应 Barbaglia, Consoli, Manzan, Tiozzo Pezzoli & Tosetti (2025, *Economic Inquiry*) 对基于词典的经济文本情感分析中「文本-实体关联强度」应纳入聚合权重的讨论, 强调聚合层面的加权设计对最终测度经济学解释力的影响不亚于底层词典本身的选取。词典法 (you_2018 等 6 部词典) 与本项目另两条情感测度技术路线——LLM 三家投票 (`llm_vote_tone*`) 与 BERT 三模型 (`finbert_cn`/`fin_sent_zh`/`finbert2`)——互为稳健性并排, 三条技术路线各自独立测度同一构念、不设主次, 三者间跨方法一致性由 `tone_validation.py` 的 Krippendorff's α 与重映射后 Cohen's κ 度量, 真实跨模型/跨方法族维度 FWER 控制见根级模板 `27_tableA12_cross_model_fwer`。

## VAR: you_2018_score_w_sum_ctx

【变体差分】
本列为 ctx 轨: 文章级 you_2018 情感得分基于 `content_ctx`(标题 + 目标银行实体窗口文本) 计算, 再按 `mention_density` 加权、在银行-年内求和。ctx 轨聚焦目标银行周边的局部语境窗口而非全文, 目的是降低文章中无关段落 (如同篇报道内提及的其他银行、其他议题) 对该银行情感归因的稀释/污染, 使情感信号更贴近「与目标银行直接相关」的叙事片段。ctx 轨行宇宙是 full 轨留篇集的子集 (conditional-on-full, 2026-06-29 起口径), 与 full/ss 两轨各自独立计算、just-identified 并排, 互为稳健性不分主次, 禁止三轨混入同一 over-identified 设定。当某篇文章未能提取出有效实体窗口 (回退触发) 时该篇 `ctx_is_fallback=True`, `content_ctx` 退化为全文 body, 此时该篇对本列的贡献与 full 轨该篇的贡献在文本层面趋同但仍作为独立轨道分别加总, 不与 full 轨列相互替代或合并。
在解读上, ctx 轨的核心价值是对「同篇报道内提及多家银行或多个议题」情形的稀释校正: 若一篇报道同时报道甲银行的业务扩张与乙银行的合规处罚, full 轨会把两段情感混合计入同一篇得分, 而 ctx 轨理论上应能分别聚焦到各自实体窗口、减少交叉污染 (实际校正力度取决于实体窗口提取算法的召回率与精度)。由于 ctx 轨依赖实体窗口的准确切分, 其样本量与 full 轨理论上一致 (行宇宙相同), 但窗口内可匹配到 you_2018 词典词条的文本量通常小于全文, 故单篇 `you_2018_score_ctx` 的方差可能高于 `_full`(样本词量更小、易受个别强极性词主导), 这一特征会传导到本列 (加权求和后在银行-年层面被部分平滑, 但银行-年报道数极少时仍可能放大)。分析时若 full 与 ctx 两轨结果方向一致, 可视为该银行-年情感信号对文本窗口选择不敏感的证据; 若出现方向性分歧, 应结合该银行-年报道的多实体共现结构具体核查, 而非机械取其一为准。

## VAR: you_2018_score_w_sum_full

【变体差分】
本列为 full 轨 (三轨中的基准/主轨): 文章级 you_2018 情感得分基于 `content_full`(标题 + 完整正文) 计算, 再按 `mention_density` 加权、在银行-年内求和, 是本家族三列中留篇门控的锚点——`llm_verified_full == True` 定义的留篇集即以本轨的验证结果为准, ctx/ss 两轨均是以本轨留篇集为行宇宙的条件测度轨。该列反映一篇报道对目标银行的情感倾向在全文语境下的整体判断 (不做局部窗口截取), 相比 ctx/ss 两轨更少受实体窗口提取误差或句级共现判据严格性的影响, 但也因此更容易被同篇报道中与目标银行无关的段落稀释。作为三轨之一, 本列与 ctx/ss 各自独立计算并排, 互为稳健性不分主次, 不因是留篇门控锚点而在统计设定上享有优先权 (禁止把三轨混入同一 over-identified Hansen J)。
在实务应用上, full 轨通常是研究者报告主结果时的默认选取轨道 (镜像 P1 处理变量 `llm_vote_tone_full` 等主轨口径已切 full-only 的先例), 因其信息覆盖面最广、不依赖实体窗口提取或句级共现判据的额外算法假设, 出现算法误差的环节最少; 但这不意味着 full 轨在经济学含义上「更正确」——它只是信息保留最完整、算法依赖最少的一支, ctx/ss 两轨在过滤无关段落噪声方面各有其不可替代的诊断价值。使用者若只报告 full 轨结果, 应在稳健性检验中同时附上 ctx/ss 两轨的一致性证据, 而非默认 full 轨可以单独承担全部识别负担。本列作为提及密度加权和, 其数值随该银行-年报道篇数与各篇提及密度共同放大, 与经密度和归一化后的语调率 `you_2018_tone_vw_full` 存在明确的流量-密度关系, 二者不应在同一回归设定中同时作为自变量出现 (会引入机械共线性)。

## VAR: you_2018_score_w_sum_ss

【变体差分】
本列为 ss 轨 (同句共现窗口, sentence-window): 文章级 you_2018 情感得分基于 `content_ss`(标题 + 目标银行与金科关键词同句、按 `config/filtering.yaml::context_window.ss_sentence_radius` 配置的句半径共现窗口文本) 计算, 再按 `mention_density` 加权、在银行-年内求和, 是三轨中判据最严格的一支——要求目标银行与金科词汇在同一句 (或 ±N 句窗口) 内共同出现才纳入窗口文本。回退语义镜像 ctx 轨: 若某篇文章不存在银行∧金科同句共现, 则 `content_ss` 回退为全文 body, 该篇 `ss_is_fallback=True`, 与 ctx 共享 `n_articles` 分母口径 (优雅降级, 而非丢弃该篇)。ss 轨行宇宙同样是 full 轨留篇集的条件子集 (conditional-on-full)。ss 轨的经济学意图是捕捉「媒体在讨论银行与金融科技交集时的情感倾向」这一更窄但更聚焦的构念, 与 full/ctx 两轨分别独立计算、just-identified 并排, 互为稳健性不分主次, 禁止三轨混入同一 over-identified Hansen J 设定; 且判据口径 (银行∧金科同句共现) 与 stage 13 `cooccurrence_filter` 的硬过滤判据 (`sentence_radius=1` + `match_in_title=true`) 是关联但独立的两个应用层面, 不可混用配置键: 前者 (stage 14 `ctx_materializer` 物化 `content_ss` 时使用的判据) 决定「一篇文章的哪一段文本被纳入 ss 轨窗口」, 后者 (stage 13 硬过滤) 决定「一篇文章是否进入下游流水线」, 两者判据原语不同 (`extract_bank_fintech_cooccurrence` 严格同句 vs `has_bank_fintech_cooccurrence_within_radius` 半径窗口), 禁止互相复用或在文档/复现代码中混淆。
由于 ss 轨判据最严格, 触发回退的比例 (`ss_is_fallback` 占比) 通常高于 ctx 轨的实体窗口提取失败率, 这意味着本列在多数银行-年样本中相当一部分篇目实际以全文 body 计入 (回退状态), 只有真正存在银行∧金科同句共现的篇目才使用真正窄化的同句窗口文本。因此本列的经济学解读应区分两类贡献: 非回退篇目反映「银行与金融科技交集叙事」的加权情感强度, 回退篇目反映的实质上是该银行该年报道的整体情感 (与 full 轨趋同), 两类混合加总构成最终的银行-年总和。在样本量充足 (T=19 生产语料) 且金科相关报道占比不低的场景下, ss 轨的非回退占比预期显著提升, 该轨的窄化诊断价值随之增强; 在 T=2 开发样本或金科报道稀疏子样本中, ss 轨可能高比例退化为 full 轨的近似, 此为预期而非缺陷。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
