---
family_id: F531
columns:
- sum_wd_hw_prob_ctx
- sum_wd_hw_prob_full
- sum_wd_hw_prob_ss
unit: 无量纲权重和 (herd-decay 权重之和, 银行-年层面; 分子分母皆无量纲, 比值构成一个概率映射语调指标的加权均值)
formula: 'sum_wd_hw_prob{track} = Σ_i [ herd_weight{track}_i · 1{llm_prob_score{track}_i is not NA} ]，其中 i 遍历该银行-年全部文章、track ∈ {_full, _ctx, _ss}；即 runner._build_llm_valid_masked_weights(df, hw_by_track, "hw") 产出的文章级中间列 _wd_hw_prob{track} = herd_weight{track}.where(llm_prob_score{track}.notna()) 在 encode.py groupby(["target_bank","year"]) 后按 "sum" 聚合得到 (encode.py agg[f"sum_wd_{{wtag}}_{{grp}}{{track}}"] 循环, grp="prob", wtag="hw")。下游消费: llm_vote_tone_hw_prob{track} = llm_prob_score_hw_sum{track} / sum_wd_hw_prob{track} (0 分母置 NaN)。'
producer: pipeline\panel\runner.py (_build_llm_valid_masked_weights, L436-478 生成文章级 _wd_hw_prob{track}) ; pipeline\panel\encode.py (L1197-1203 groupby-sum 聚合出 panel 级 sum_wd_hw_prob{track}; L2193-2195 _llm_denom 消费为分母; L2312-2315 计算 llm_vote_tone_hw_prob{track})
upstream:
- herd_weight_full
- herd_weight_ctx
- herd_weight_ss
- llm_prob_score_full
- llm_prob_score_ctx
- llm_prob_score_ss
citations:
- doi: 10.1145/1102351.1102430
  type: wp
  authors: Niculescu-Mizil, A., & Caruana, R.
  year: 2005
  title: Predicting good probabilities with supervised learning
  venue: Proceedings of the 22nd International Conference on Machine Learning (ICML)
  pages_or_artno: 625-632
- doi: 10.2307/1914121
  type: journal
  authors: Manski, C. F., & Lerman, S. R.
  year: 1977
  title: The estimation of choice probabilities from choice based samples
  venue: Econometrica
  vol: '45'
  issue: '8'
  pages_or_artno: 1977-1988
- doi: 10.1126/sciadv.adp1528
  type: journal
  authors: Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E.
  year: 2024
  title: Wisdom of the silicon crowd- LLM ensemble prediction capabilities rival human crowd accuracy
  venue: Science Advances
  vol: '10'
  issue: '45'
  pages_or_artno: eadp1528
- doi: "10.1371/journal.pone.0323064"
  type: "journal"
  authors: "Wright, D., & Augenstein, I."
  year: 2025
  title: "Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift"
  venue: "PLOS One"
  vol: "20"
  issue: "6"
  pages_or_artno: "e0323064"
- doi: "10.2139/ssrn.4842086"
  type: "wp"
  authors: "Battaglia, L., Christensen, T., Hansen, S., & Sacher, S."
  year: 2024
  title: "Inference for Regression with Variables Generated from Unstructured Data"
  venue: "SSRN Electronic Journal"
  pages_or_artno: "4842086"
new_dois: []
---

## CORE

【构念与来源】
本家族三列 (sum_wd_hw_prob_full / sum_wd_hw_prob_ctx / sum_wd_hw_prob_ss) 属"跟风衰减加权 (herd-decay weighting, HW) × logit-to-score 概率映射语调 (llm_prob_score)" 组合测度体系里的匹配分母, 与"当前状态铁律"下的 herd_weight 三轨族、LLM 三家投票族、以及 logit-to-score 概率映射语调族三者共同构成一个自洽的加权均值系统。其自身不是直接可解释的语调分数, 而是银行-年层面上"参与 HW 加权平均的有效权重之和"——一个纯技术性的分母中间量, 供计算 llm_vote_tone_hw_prob{track} (= llm_prob_score_hw_sum{track} / sum_wd_hw_prob{track}) 时使用。理解这个家族, 必须先理解它试图修补的一个测度学问题: encode-01 分子分母失配 bug (2026-06-10 修复, 见 runner.py L436-478 docstring)。

在跟风衰减加权体系下, 每篇文章 i 被赋予一个"跟风衰减权重" herd_weight{track}_i (衡量该文章在同题材报道浪潮中的边际信息增量, 抄稿/跟风程度越高权重越低; 该权重本身的构造细节见 herd_weight 家族长文, 本家族只消费其结果作分母权重, 不重复论证其构造)。三家 LLM (gpt54nano/gemini31/deepseekv4) 投票共识之外, 本项目额外产出一个基于 logit 变换的连续概率映射语调分数 llm_prob_score{track} (取值范围为概率区间, 详见分类维度 logit-to-score 校准法, 锚点 Niculescu-Mizil & Caruana 2005 关于监督学习预测概率校准的经典方法论)。若直接用 Σ(herd_weight_i × llm_prob_score_i) / Σ(herd_weight_i, over all i) 计算加权均值, 分子只累加了 llm_prob_score 非缺失 (LLM 判断有效) 的文章, 但分母却把该银行-年全部文章 (含 LLM 未给出有效判断的文章) 的权重都计入——这相当于把"LLM 未判断"的文章隐式当成语调贡献为 0 参与平均, 导致加权均值系统性地向 0 方向衰减, 且衰减幅度随 LLM-invalid 占比增大而增大 (fix(encode-01, metric-audit 2026-06-10) 明确记录的度量偏误)。

本家族三列正是这一修复的产物: 它把分母也限定在"llm_prob_score{track} 非缺失"的那批文章上, 使分子 (llm_prob_score_hw_sum{track}) 与分母 (sum_wd_hw_prob{track}) 数的是同一批文章, 让二者相除得到的加权均值口径自洽、无隐式的"缺失当零"偏误。这一设计模式 (valid-mask 分母) 并非本家族独有——同一 runner._build_llm_valid_masked_weights 函数为 vw (mention_density 加权)/mw (媒体权威性加权)/hw (跟风衰减加权) 三套权重体系, 分别对 llm (共识投票)、LLM_MODELS 逐模型、以及 prob (概率映射语调) 三组测度各自生成一套 valid-mask 分母列, 本家族即是 hw × prob 这一格。

【方法学与计算】
计算发生在两个阶段。第一阶段 (runner.py, _build_llm_valid_masked_weights): 对每个轨道 track ∈ {_full, _ctx, _ss}, 取该轨道的跟风衰减权重 (hw_by_track[track], 即 herd_weight{track}, 三轨各自独立估计, 详见 herd_weight 家族), 用 pandas .where() 方法把 llm_prob_score{track} 为缺失的行的权重置为 NaN、非缺失行保留原权重值, 得到文章级中间列 _wd_hw_prob{track} (下划线前缀标记为内部临时列, 不落盘文章级 parquet)。第二阶段 (encode.py, 聚合循环 L1197-1203): 对 (target_bank, year) 分组, 把 _wd_hw_prob{track} 按 sum 聚合 (pandas groupby.agg 对 NaN 自动跳过, 等价于"只累加有效行的权重"), 得到本家族的三个面板列 sum_wd_hw_prob{track}。随后在同一 encode.py 模块内, 该列被 _llm_denom("hw", "prob", track, hw_denom) 辅助函数消费 (L2193-2195): 若 sum_wd_hw_prob{track} 存在于面板中, 优先用它作分母 (且对 0 值 replace 为 NaN, 防止除零); 否则退化为该轨道的物理跟风权重和 (sum_herd_weight{track}) 作分母兜底。最终产出 llm_vote_tone_hw_prob{track} = llm_prob_score_hw_sum{track} / sum_wd_hw_prob{track} (L2312-2315), 即"跟风衰减加权、以有效判断篇数为权重口径的银行-年概率映射语调均值"。

三轨语义遵循项目统一口径: _full = 标题+正文全文轨、_ctx = 标题+银行实体窗口轨、_ss = 标题+银行∧金科词同句±N窗轨 (ss 若无银行∧金科同句共现, 回退为全文 body, 镜像 ctx 的回退公理, 该篇的 ss_is_fallback 置 True, 但 llm_prob_score_ss 是否有效仍取决于 LLM 判断本身、不因 fallback 而系统性缺失)。三轨 herd_weight 各自独立估计 (v3.6.0 起, 移除单轨 legacy 权重后三轨权重互不共享), 因此本家族三列彼此不是同一权重口径的重复, 而是各轨独立的分母。铁律: full/ctx/ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止把三轨分母/由其派生的加权均值混入同一 over-identified Hansen J 检验; 留篇门控 (2026-06-29 起) 采用 full-only 口径 (即"是否算作一篇银行-金科报道" 只看 llm_verified_full), ctx/ss 是 conditional-on-full 的稳健性/测度轨, 行宇宙为 full 留篇集的子集, 但本家族的 sum 聚合本身按 per-track 独立计算、不借用 full 轨的分母。

需特别说明的一点度量学含义: 本家族列的数值大小本身不是"语调强度"，而是"该银行-年内 LLM 对该文章给出有效概率判断、且被跟风衰减权重加权后的样本权重总量"，可粗略理解为"经权重折算后的有效样本规模"。当一个银行-年内报道量大但 LLM 判断有效率低 (如因 prompt 触发拒答、格式解析失败等), 该列数值会明显小于同期 sum_herd_weight{track} (物理权重总和); 二者之比 sum_wd_hw_prob{track} / sum_herd_weight{track} 可作为该银行-年 llm_prob_score 判断覆盖率的诊断量, 但该比值本身不是既定面板列, 需下游自行构造。

【文献定位】
跟风衰减加权的经济学动机 (抄稿/重复报道稀释边际信息含量, 因而应对高度雷同的跟风报道降权) 的详细文献谱系见 herd_weight 家族长文, 本家族不重复展开该动机论证。以概率化连续分数替代离散三分类语调标签的做法 (llm_prob_score), 呼应 Niculescu-Mizil & Caruana (2005) 关于监督学习模型输出概率校准 (probability calibration) 的方法论——本项目的 logit-to-score 映射同样追求把 LLM 的离散判断转换为可信的连续概率量表, 而非直接把 softmax/离散标签当作基数意义上可加总的分数使用。valid-mask 分母的设计 (只对有效观测计入分母权重) 呼应计量经济学里"选择性缺失下加权均值的分子分母同域"这一基本原则, 与 Manski & Lerman (1977, Econometrica) 关于基于选择的样本估计选择概率时须保证样本口径一致性的经典论证同构——若分子分母口径不一致 (如本家族修复前的 encode-01 bug), 估计量会产生系统性偏误方向 (向 0 或向某个基准值收缩), 而非仅仅是方差增大。此外, 概率化多分类器集成投票的可靠性也有近期 LLM 文献支持: Schoenegger et al. (2024, Science Advances) 展示 LLM 集成 (ensemble) 预测能力可比拟人类群体智慧, 为本项目采用三家 LLM 投票 + 概率映射双轨并行的设计提供跨领域佐证——但需注意, 本项目的三家 LLM 投票共识 (llm_vote_tone) 与三家各自的 per-model 子测度、以及 llm_prob_score 概率映射轨, 是并列的互为稳健性测度, 并非以概率映射轨替代投票共识轨。 在上述锚点之外, 另有两条近期文献分别贴合本家族的两个构造环节。Wright 与 Augenstein (2025) 在 NLP 标注基准上系统比较了把多标注者软标签 (概率) 聚合为训练/评估目标的若干方案, 发现软标签聚合在分布偏移下比硬标签多数投票给出更好的不确定性估计; 这正对应本项目两条并排轨的存在理由: prob 分组 (软概率映射) 与 llm 分组 (三家硬多数投票共识), 本家族即前者的 hw 分母。迁移边界须写明: 原文的标注者是人类众包工人而非商用 LLM, 其目标是分类器不确定性校准而非面板分母求和, 语料为英文基准集, 原文既无银行-年聚合层, 亦无跟风/媒体权威/提及密度三套权重维度; 尤须避免据该文把 prob 轨读作优于投票轨的主测度——本仓库两轨仍是互为稳健性、不分主次、各自 just-identified 并排的设定, 禁止混入同一 over-identified Hansen J。Battaglia、Christensen、Hansen 与 Sacher (2024) 建立了"先由文本等非结构化数据生成变量, 再把该变量放进回归"这一两步流程的推断理论, 证明朴素代入会产生偏误, 并给出偏误修正与有效标准误。本家族恰处该流程的分母侧: llm_prob_score 由 LLM 从新闻文本生成, 其有效性掩码决定哪些篇章的权重进入加权求和。该文亦为工作论文; 其处理对象是回归中的生成型回归元/被解释变量本身, 与本处"有效性掩码构成的权重分母"层级不同, 原文未涉及中文新闻、银行-年面板、三轨设定与多模型投票共识, 本仓库也并未实施其修正估计量, 故引用限于"文本生成变量的误差非随机、朴素代入有偏"这一前提层, 不主张本家族已按其方案去偏。
## VAR: sum_wd_hw_prob_ctx

【变体差分】
本列是 track=_ctx (标题+银行实体窗口轨) 下的跟风衰减权重-概率映射语调匹配分母。源头 herd_weight_ctx 是 stage 24 (herd_decay_processor) 在 ctx 轨文本 (content_ctx, 即标题+实体窗口, stage 14 materialize_ctx 物化) 上独立估计的跟风衰减权重, 与 _full 轨权重完全独立计算 (不共享权重口径, v3.6.0 起三轨权重互相独立施加)。分子来源 llm_prob_score_ctx 同样是 LLM 在 ctx 轨文本上给出的 logit-to-score 概率映射判断, 与 llm_prob_score_full 是不同文本输入下的独立判断结果 (可能因窗口截断丢失部分上下文而与 full 轨判断不完全一致)。本列的作用是: 当计算 llm_vote_tone_hw_prob_ctx (ctx 轨的跟风衰减加权概率语调均值) 时, 作为分母保证分子 llm_prob_score_hw_sum_ctx 与本列数的是同一批"ctx 轨 LLM 给出有效概率判断"的文章, 避免 ctx 轨未判断文章被隐式计为 0 语调贡献。ctx 轨是留篇门控 full-only 口径下的 conditional-on-full 稳健性测度轨, 其行宇宙为 full 轨留篇集合的子集, 但本列的加总本身在 ctx 轨内部独立进行, 不借用 full 轨的分母或篇数。与 sum_wd_hw_prob_full、sum_wd_hw_prob_ss 三者互为稳健性并排, 禁止混入同一 over-identified 检验。数值层面, sum_wd_hw_prob_ctx 通常不等于 sum_wd_hw_prob_full: 一方面 ctx 轨的 herd_weight_ctx 权重估计基于更窄的实体窗口文本, 抄稿判定的边际信息量计算口径与 full 轨不同; 另一方面 llm_prob_score_ctx 的有效判断集合 (非缺失行) 与 llm_prob_score_full 的有效判断集合未必完全重合——即便留篇门控已锁定 full-only 的行宇宙, LLM 在窗口截断后的 ctx 文本上仍可能因信息不足而给出与 full 轨不同的解析结果 (含解析失败置缺失)。因此该列不能被视为 full 轨分母的简单缩放, 须作为独立的加总量看待, 在做跨轨比较时应关注派生比值 (如 llm_vote_tone_hw_prob_ctx 与 llm_vote_tone_hw_prob_full 的相关系数), 而非直接比较本列的绝对数值大小。

## VAR: sum_wd_hw_prob_full

【变体差分】
本列是 track=_full (标题+正文全文轨) 下的跟风衰减权重-概率映射语调匹配分母, 是本家族的主轨/canonical 参照——三轨中信息覆盖面最完整 (未做实体窗口截断或同句限定), 也是留篇门控 (2026-06-29 起) 的判定基准轨: 一篇文章"是否算作一篇经 LLM 验证的银行-金科报道"只看 llm_verified_full, 因此本列所加总的 herd_weight_full 权重与 llm_prob_score_full 有效判断, 天然覆盖该银行-年被纳入分析的完整文章集合 (ctx/ss 轨则是该集合的子集测度)。源头 herd_weight_full 由 stage 24 在全文文本上估计, llm_prob_score_full 由 LLM 在全文文本 (标题+正文) 上给出。本列消费方 llm_vote_tone_hw_prob_full (= llm_prob_score_hw_sum_full / sum_wd_hw_prob_full) 是 P1 (bank_fintech_tone) 等 paper 主轨情感测度体系里概率映射一支的核心分母, 与三家 LLM 逐模型 HW 加权语调、词典 HW 加权语调、BERT HW 加权语调等并列构成 HW 加权测度家族的一格。全文轨作为主轨并不意味其构念优于 ctx/ss——三轨依然互为稳健性、不分主次, full 轨的特殊之处仅在于承担留篇门控基准的角色。就数值规模而言, sum_wd_hw_prob_full 在同一银行-年内一般是三轨分母中样本覆盖最完整的一个, 因为 full 轨文本未经窗口截断, LLM 更少因上下文不足而给出缺失判断; 但这不代表其数值必然大于 sum_wd_hw_prob_ctx/_ss, 因为跟风衰减权重本身 (herd_weight_full) 与实体窗口/同句窗轨的权重估计口径不同, 抄稿判定结果也可能因文本长度差异而系统性不同。使用者若需诊断某银行-年 LLM 概率判断的整体覆盖率, 可将本列除以对应的 sum_herd_weight_full (物理权重和, 无 valid-mask), 比值越接近 1 说明该银行-年内 LLM 对几乎全部文章都给出了有效的概率映射判断。



## VAR: sum_wd_hw_prob_ss

【变体差分】
本列是 track=_ss (标题+银行∧金科词同句±N窗轨, 窗口半径见 config/filtering.yaml::context_window.ss_sentence_radius, 默认 1) 下的跟风衰减权重-概率映射语调匹配分母。源头 herd_weight_ss 由 stage 24 镜像 ctx 轨产出 (若源列缺失, encode.py 会将该轨道的 HW 相关列整体置 NaN 优雅降级, 而非报错崩溃)。ss 轨文本回退语义: 若某篇文章内不存在"目标银行与金科词同句共现" (config 判据 sentence_radius=1 窗口), content_ss 回退为全文 body (镜像 content_ctx 的回退公理), 该行 ss_is_fallback 置 True, 与 n_articles 共享同一分母口径; 但这一回退是文本层面的替代, llm_prob_score_ss 是否有效 (是否被 LLM 判断为可解析) 仍是独立于 fallback 状态的另一件事——即便某篇文章的 ss 文本回退为全文, 只要 LLM 在该文本上给出了有效概率判断, 该篇仍计入本列的加总。ss 轨与 ctx 轨共享"回退时退化为 full 轨文本"的镜像语义, 但二者判据不同 (ctx 用实体窗口截断, ss 用同句共现窗口), 因此 herd_weight_ss 与 herd_weight_ctx、进而本列与 sum_wd_hw_prob_ctx, 是两套独立估计而非同一权重的重复标注。与 full/ctx 两轨互为稳健性并排, 不设主次, 禁止混入同一 over-identified Hansen J 检验。需提醒的是, ss 轨判据 (银行∧金科词严格同句/±1句窗共现) 比 ctx 轨判据 (实体窗口) 更严格, 因此在报道量较小的银行-年, 真正触发同句共现的文章占比可能偏低, ss_is_fallback 比例偏高, content_ss 大量退化为全文文本——这会使 herd_weight_ss 与 herd_weight_full 在这些银行-年高度趋同 (因为底层文本相同), 进而使 sum_wd_hw_prob_ss 在数值上向 sum_wd_hw_prob_full 靠拢, 但二者仍是两个独立计算、独立落盘的面板列, 不可互相替代或合并使用。

<!-- rendered-citations:begin -->
Niculescu-Mizil, A., & Caruana, R. (2005). Predicting good probabilities with supervised learning. Proceedings of the 22nd International Conference on Machine Learning (ICML) No. 625-632 [Working Paper]. https://doi.org/10.1145/1102351.1102430
Manski, C. F., & Lerman, S. R. (1977). The estimation of choice probabilities from choice based samples. Econometrica, 45(8), 1977-1988. https://doi.org/10.2307/1914121
Schoenegger, P., Tuminauskaite, I., Park, P. S., Bastos, R. V. S., & Tetlock, P. E. (2024). Wisdom of the silicon crowd- LLM ensemble prediction capabilities rival human crowd accuracy. Science Advances, 10(45), eadp1528. https://doi.org/10.1126/sciadv.adp1528
Wright, D., & Augenstein, I. (2025). Aggregating soft labels from crowd annotations improves uncertainty estimation under distribution shift. PLOS One, 20(6), e0323064. https://doi.org/10.1371/journal.pone.0323064
Battaglia, L., Christensen, T., Hansen, S., & Sacher, S. (2024). Inference for Regression with Variables Generated from Unstructured Data. SSRN Electronic Journal No. 4842086 [Working Paper]. https://doi.org/10.2139/ssrn.4842086
<!-- rendered-citations:end -->
