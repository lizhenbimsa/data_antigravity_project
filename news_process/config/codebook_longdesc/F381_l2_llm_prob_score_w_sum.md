---
family_id: F381
columns:
- llm_prob_score_w_sum_ctx
- llm_prob_score_w_sum_full
- llm_prob_score_w_sum_ss
unit: 无量纲加权得分之和 (bank-year 层面, 提及密度 mention_density 加权)
formula: 'llm_prob_score_w_sum{track} = Σ_i (llm_prob_score{track}_i × mention_density_i), 逐篇文章 i 求和聚合到 bank-year; 权重来源列由 runner._build_llm_valid_masked_weights 同步产出 valid-mask 权重和 (_wd_vw_prob{track}) 作匹配分母'
producer: pipeline\panel\runner.py (加权列预计算, 步骤 3b) + pipeline\panel\encode.py (bank-year sum 聚合, L1193)
upstream:
- 21_tone_llms.parquet (llm_prob_score{track} 文章级列, 三家 LLM 共识/概率映射)
- mention_density (银行提及密度, Hassan et al. 2019 QJE Value-weighted Exposure 构念)
citations:
- doi: 10.1093/qje/qjz021
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A.
  year: 2019
  title: 'Firm-Level Political Risk: Measurement and Effects'
  venue: Quarterly Journal of Economics
  vol: '134'
  issue: '4'
  pages_or_artno: 2135-2202
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for textual analysis? How to use generative LLMs in accounting research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: Chinese fine-grained financial sentiment analysis with large language models
  venue: Neural Computing and Applications
  vol: '37'
  issue: '30'
  pages_or_artno: 24883-24892
- doi: 10.48550/arXiv.2412.07031
  type: wp
  authors: Ludwig, J., Mullainathan, S., & Rambachan, A.
  year: 2025
  title: 'Large language models: An applied econometric framework'
  venue: NBER Working Paper No. 33344
- doi: 10.18653/v1/2024.findings-emnlp.432
  type: journal
  authors: Renze, M.
  year: 2024
  title: The Effect of Sampling Temperature on Problem Solving in Large Language Models
  venue: 'Findings of the Association for Computational Linguistics: EMNLP 2024'
  pages_or_artno: 7346-7356
new_dois: []
---

## CORE

【构念与来源】
llm_prob_score_w_sum 是「Logit-to-Score 概率映射情感」测度族在 bank-year 层面的提及密度加权求和分支, 与家族内 avg_llm_prob_score(等权均值)、llm_prob_score_sum(等权求和)、llm_prob_score_mw_sum(媒体权威加权)、llm_prob_score_hw_sum(跟风衰减加权)并列, 共同构成同一底层文章级信号 llm_prob_score 的加权稳健性梯子。底层构念是把三家 LLM (gpt54nano/gemini31/deepseekv4) 对每篇报道的三分类判定 (正面/中性/负面) 折算为连续概率对比得分 Score = P(正面) − P(负面) ∈ [−1, +1], 用以在离散投票 llm_vote_tone 之外提供一条不损失概率信息的连续测度稳健性轨。llm_prob_score_w_sum 在此基础上乘以文章级权重 mention_density 再对 bank-year 求和; mention_density 的构念直接借鉴 Hassan et al. (2019, QJE) 提出的 Value-weighted Exposure 思路 —— 同一篇报道内某银行被提及的相对密度越高, 该篇报道对该银行情感刻画的信息含量与代表性就越强, 因此在加总为面板测度时应赋予更高权重, 而非把"提到一次"与"通篇围绕该行"的报道等量齐观。w_sum 与家族内另两支加权 sum (mw_sum 用媒体权威性权重, hw_sum 用跟风衰减权重) 在方法论上完全平行, 均是"同一文章级概率得分 × 不同经济学意义上的文章权重 → 求和"的结构, 互为稳健性并排, 不分主次, 也不应混入同一 over-identified 设定联合估计。

【方法学与计算】
计算分两步串联, 均在面板构建 (panel) 阶段完成, 不改动 stage 21 情感 LLM 的文章级原始输出。第一步 (`pipeline/panel/runner.py` 步骤 3b) 在文章级 DataFrame 上, 对每条轨道 track ∈ {_full, _ctx, _ss} 取该轨的 mention_density (缺失填 0), 与该轨的 llm_prob_score{track} 逐行相乘, 生成文章级加权列 llm_prob_score_w{track}; 该步骤与情感离散/连续投票、逐模型 LLM 得分、词典得分、词典 IDF 得分、BERT 概率列共用同一套 mention_density 权重预计算逻辑, 是面板加权体系的统一入口, 而非 llm_prob 族专属旁路。第二步 (`pipeline/panel/encode.py`, 约 L1193) 在 bank-year 聚合阶段对文章级加权列取 sum, 得到 llm_prob_score_w_sum{track} 三轨列。与之配套的分母侧修正是 valid-mask 权重和 (`_wd_vw_{grp}{track}`, 由 `_build_llm_valid_masked_weights` 产出, grp 含 'prob'): 2026-06-10 的一处审计 fix 指出, 若分子只在"有效篇" (verified 门控通过) 上累加, 分母却沿用全样本权重和, 会人为把加权均值压向零, 因此专门为 LLM 族 (含 prob 概率子族) 建一份仅在有效样本上累加的权重和分母, 与 w_sum 类分子在统计口径上严格匹配。llm_prob_score_w_sum 本身是求和量, 不是均值, 使用时若需构造加权均值须自行除以对应分母列, 不能直接把 sum 当作代表性水平指标解读, 求和量对银行-年内文章篇数天然敏感, 篇数越多绝对值越大, 这是该支路与 avg_llm_prob_score 均值支路在解释上的根本区别。三轨 full/ctx/ss 的权重来源 mention_density 与情感得分 llm_prob_score 均按各自轨道独立计算, 不存在跨轨借用: 若某轨 mention_density 或 llm_prob_score 缺失, 该轨的 w_sum 列在聚合时通过 valid_agg 优雅跳过, 不会用其它轨的值填补, 也不会导致整族聚合失败。

【文献定位】
概率对比得分的方法学定位承接文本情感度量从离散标签向连续打分演进的一般脉络: de Kok (2025, Management Science) 系统讨论了在会计与金融研究中使用生成式大语言模型做文本分析时的 prompt/temperature 冻结与结果稳定性问题, 是本项目 stage 21 采用 temperature=0.0 与缓存化 prompt 的方法论依据, 也是 llm_prob_score 这类连续概率输出相较纯离散多数投票更适合做统计推断的背景论证之一; Ludwig, Mullainathan & Rambachan (2025, NBER WP) 提出的 LLM 应用计量框架进一步论证了将 LLM 输出视为对不可观测潜变量的带噪测量, 为多支加权/多模型并排的稳健性设计提供了识别层面的正当性; Renze (2024, EMNLP Findings) 关于采样温度对大语言模型输出稳定性的实证发现, 支撑本项目将 temperature 锁定为 0.0 以最大化概率映射得分的可复现性; Lan et al. (2025, Neural Computing and Applications) 针对中文金融文本的细粒度情感分析研究, 与本项目中文财经报道场景直接可比, 印证了在中文语境下用大语言模型输出概率而非仅硬标签的可行性。而 mention_density 加权本身的构念源头 Hassan et al. (2019, QJE) 的 Value-weighted Exposure 方法, 已是政治风险/公司层面文本暴露测度文献中的标准做法, 本处将其平移到银行金融科技情感文本的加权求和构造上, 逻辑一致: 报道正文中对目标银行着墨越多, 该篇文章对银行情感面板值的贡献权重就应越大。

## VAR: llm_prob_score_w_sum_full

【变体差分】
_full 轨使用 stage 14 物化的 content_full (标题+全文正文) 作为文章级情感与权重的计算文本域, 是家族内文本覆盖面最宽的轨道。按 2026-06-29 的留篇门控口径, 是否将一篇报道计入"该银行的一篇金融科技相关报道"这一行宇宙判定, 唯一依据是 llm_verified_full == True, 即 full 轨是留篇门控的判定轨; ctx/ss 两轨在此基础上退化为 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 轨留篇集合的子集, 但各轨内部的 llm_prob_score/mention_density 仍按各轨自身文本独立计算与求和, 不借用 full 轨的数值。因此 llm_prob_score_w_sum_full 既是 P1 情感主线 llm_vote_tone_full 所在的同一 full 轨路径, 也是本 w_sum 支路里样本量最完整、缺失最少的一支, 常被视为该加权求和梯子的默认参照点, 但在识别策略层面仍与 ctx/ss 两轨并排、互为稳健性, 三轨在同一 over-identified 设定内不可混用同一工具集。
从计算细节看, full 轨的 mention_density 权重同样以全文正文为口径统计目标银行提及次数与位置分布, 因此该轨的加权求和天然把"通篇聚焦目标银行"的深度报道与"仅在段落末尾附带一句"的浅提及报道拉开权重差距, 是三轨中权重区分度最大的一支; 又因样本覆盖最全, 该轨的 llm_prob_score_w_sum_full 波动主要来自银行-年内报道篇数与题材构成的变化, 而非文本窗口构造本身引入的噪声, 这是它与 ctx/ss 两轨在方差来源上的关键差异, 使用时应结合 full 轨的等权求和 llm_prob_score_sum_full 与均值 avg_llm_prob_score_full 对照, 避免把加权总量的变动误判为情感水平本身的变动。

## VAR: llm_prob_score_w_sum_ctx

【变体差分】
_ctx 轨使用 stage 14 物化的 content_ctx (标题+目标银行实体窗口文本) 作为计算文本域, 相对 full 轨聚焦在银行实体周边局部语境, 剔除了与该银行提及无关的正文段落干扰, 是"信噪比更高但样本可能因窗口构造而略有收缩"的稳健性轨。ctx 轨的 mention_density 与 llm_prob_score 均按 content_ctx 独立重新计算, 不是 full 轨数值的子集裁剪; 当银行-年内某些文章缺失 ctx 轨对应源列时 (例如实体窗口构造失败或该轨文本本身缺失), 该文章在 ctx 轨的加权求和中被 valid_agg 自然跳过, 不影响 full/ss 两轨各自的求和结果, 三轨之间是并排独立聚合而非彼此兜底。按当前主线口径, ctx 轨的行宇宙已收窄为 full 轨留篇集合的子集 (conditional-on-full), 即某篇文章要出现在 ctx 轨的求和分子里, 首先须满足该篇在 full 轨被判定为有效留篇, 这一点与 llm_prob_score_w_sum_full 的门控判定共享同一批文章, 但情感得分与权重数值本身仍是 ctx 轨自有的独立计算结果。
由于 content_ctx 只保留银行实体窗口附近的文本片段, 该轨的 mention_density 分布相对 full 轨更集中、极端值更少, 因此 llm_prob_score_w_sum_ctx 通常表现出比 full 轨更小的银行-年间离散度, 这一性质本身即是稳健性检验的价值所在: 若某项回归结论在 full 轨成立、在权重更集中的 ctx 轨下依旧成立且符号方向一致, 可在一定程度上排除"结论完全由少数极端加权观测驱动"的担忧。使用者不应因 ctx 轨样本量或权重量级小于 full 轨而将其视为"次要"或"有缺陷"的版本, 二者是同一构念在不同文本窗口下的并列估计, 论文行文与结果解读中须避免默认以 full 轨压倒 ctx 轨的表述。

## VAR: llm_prob_score_w_sum_ss

【变体差分】
_ss 轨使用 stage 14 物化的 content_ss (标题+银行与金融科技词同句共现窗口, 默认 ±1 句半径) 作为计算文本域, 是三轨中文本覆盖面最窄、语境最贴近"银行与金融科技话题直接同现"的一支。回退语义镜像 ctx 轨: 若某篇报道中不存在银行与金融科技词的同句共现, content_ss 退化为回退到全文正文 body, 并将 ss_is_fallback 标记为 True, 与 ctx 轨共享同一套 n_articles 分母口径, 即回退发生时该篇文章仍计入样本, 只是其 ss 轨文本内容退化为与 full 轨相近的全文, 而非被剔除。ss 轨的 llm_prob_score 与 mention_density 同样按 content_ss 独立计算后再乘积求和, 缺列时由 valid_agg 优雅跳过, 不借用 full/ctx 两轨数值。ss 轨的行宇宙同样已收窄为 full 轨留篇集合的子集 (conditional-on-full), 门控判定仍以 llm_verified_full 为准; 若 FINTECH_AC 词典本身为 None (罕见的降级场景), 三轨的 *_is_fallback 会全部置 True, 此时 ss 轨的文本域实质上与 full 轨趋同, 但求和列本身仍作为独立轨道产出, 与 full/ctx 两轨并排互为稳健性, 不设优先级。
就权重构造而言, ss 轨的 mention_density 只在"银行与金融科技词同句共现"这一最严格的窗口内统计, 当同句共现命中时, 该篇报道在语义上几乎必然是"就该银行的金融科技相关事项展开论述", 其对应的加权得分因此最贴近"该银行金融科技议题情感"这一狭义构念本身; 而一旦触发回退, ss 轨退化为与 full 轨近似的宽口径, 该篇文章的权重与得分便不再具备 ss 轨本应有的语境纯度。使用 llm_prob_score_w_sum_ss 做稳健性检验时, 应留意样本中 ss_is_fallback 的占比: 回退占比越高, ss 轨与 full 轨的经验差异就越可能被稀释, 这是解读三轨稳健性结果一致或不一致时需要交叉核对的背景信息, 而非该列本身的缺陷。

<!-- rendered-citations:begin -->
Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-Level Political Risk: Measurement and Effects. Quarterly Journal of Economics, 134(4), 2135-2202. https://doi.org/10.1093/qje/qjz021
de Kok, T. (2025). ChatGPT for textual analysis? How to use generative LLMs in accounting research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ludwig, J., Mullainathan, S., & Rambachan, A. (2025). Large language models: An applied econometric framework. NBER Working Paper No. 33344 [Working Paper]. https://doi.org/10.48550/arXiv.2412.07031
Renze, M. (2024). The Effect of Sampling Temperature on Problem Solving in Large Language Models. Findings of the Association for Computational Linguistics: EMNLP 2024, 7346-7356. https://doi.org/10.18653/v1/2024.findings-emnlp.432
<!-- rendered-citations:end -->
