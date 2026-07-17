---
family_id: F392
columns:
- llm_vote_score_hw_thr25_sum_ctx
- llm_vote_score_hw_thr25_sum_full
- llm_vote_score_hw_thr25_sum_ss
unit: 银行-年内加权语调打分之和 (三分类符号打分 {-1,0,+1} × 抄稿衰减权重后逐篇求和, 无量纲)
formula: 'sum_over_articles( llm_vote_score{track} × herd_weight{track}_thr25 ), 仅对 llm_vote_score{track} 非缺失 (即三家 LLM 投票有效) 的文章求和; herd_weight{track}_thr25 由 stage 24 herd_decay 在替代相似度阈值 τ=0.25 (而非生产基线 τ=0.35) 下重算的抄稿衰减权重; 分母侧配套列 sum_wd_hw_thr25_llm{track} 单独存在, 比值列 llm_vote_tone_hw_thr25{track} = 本列 / 配套分母列 (Σ herd_weight_thr25 over 有效文章), 属另一家族, 不在本列内)'
producer: pipeline\panel\encode.py (聚合 agg[f'llm_vote_score_hw_{{_tag}}_sum{{track}}']) ; pipeline\sentiment\herd_decay.py (stage 24, 产 herd_weight{track}_thr25 源列) ; pipeline\panel\runner.py (步骤 3d, 产 llm_vote_score_hw_thr25{track} 加权中间列) ; core\config.py::herd_sensitivity_grid (τ 网格与 tag 单一事实源)
upstream:
- 21_tone_llms.parquet (llm_vote_score{track}, 三家 LLM 多数投票共识语调)
- 24_herd_decay.parquet (herd_weight{track}_thr25, τ=0.25 下的抄稿衰减权重)
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
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: Media Coverage and the Cross-Section of Stock Returns
  venue: The Journal of Finance
  vol: '64'
  issue: '5'
  pages_or_artno: 2023-2052
- doi: 10.1287/mnsc.2023.03253
  type: journal
  authors: de Kok, T.
  year: 2025
  title: 'ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research'
  venue: Management Science
  vol: '71'
  issue: '9'
  pages_or_artno: 7888-7906
- doi: 10.48550/arXiv.2511.15714
  type: arxiv
  authors: Kamen, A., & Kamen, Y.
  year: 2025
  title: 'Majority Rules: LLM Ensemble is a Winning Approach for Content Categorization'
  venue: arXiv
- doi: "10.18653/v1/2025.findings-acl.744"
  type: "journal"
  authors: "Wang, W., Wang, Y., & Huang, H."
  year: 2025
  title: "Ranked Voting based Self-Consistency of Large Language Models"
  venue: "Findings of the Association for Computational Linguistics: ACL 2025"
  pages_or_artno: "14410-14426"
- doi: "10.18653/v1/2024.law-1.13"
  type: "journal"
  authors: "Rønningstad, E., Velldal, E., & Øvrelid, L."
  year: 2024
  title: "A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation"
  venue: "Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII)"
  pages_or_artno: "133-139"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的是"银行-年内、经抄稿衰减调整后的 LLM 共识语调加总"这一中间量, 是构造加权情感均值 (herd-weight, HW) 稳健性梯子上的一个分子诊断列, 本身不是最终回归用的语调水平变量。其构念根基是"媒体扎堆报道会人为放大某一篇通稿的样本权重, 从而扭曲银行-年语调均值"这一经典媒体经济学关切 (You, Zhang & Zhang, 2018 RFS 的"谁执掌笔杆子"研究即刻画了中国语境下媒体对企业负面信息的选择性报道与转载扩散; Fang & Peress, 2009 JF 亦证明媒体覆盖广度本身对定价有独立信息含量, 而非仅是情感符号)。管道对此的应对是: 先在 stage 24 (`herd_decay.py`) 按文本相似度聚类识别"抄稿群"并给每篇文章赋予一个衰减权重 (相似度越高、群规模越大, 权重越低, 单篇通稿被多家媒体转载不再等价于多条独立信息), 再用该权重去加权 stage 21 (`tone_llms.py`) 产出的三家 LLM 多数投票共识语调打分 `llm_vote_score{track}` (取值 {-1, 0, +1}, 三家模型多数一致才判定非零, 否则记为无效/缺失), 得到本家族的分子求和列。
本列名中的 `hw` 是 herd-weight 加权族的标签 (与 `vw`/`mw` 并列, 分别对应 mention-density 加权与 media-authority 加权), `thr25` 是抄稿相似度判定阈值敏感性网格中的一个具体取值标签, 对应 τ=0.25 (而非生产基线 τ=0.35)。该阈值敏感性网格由 `core/config.py::herd_sensitivity_grid` 统一解析 `sentiment.yaml::herd_detection.sensitivity_thresholds` (默认候选集 {0.25, 0.30, 0.40, 0.45}), 已自动剔除与基线重合的取值, 并将每个合法 τ 编码为 `thr{round(τ*100):02d}` 形式的列名后缀 —— 0.25 → `thr25`。`_sum` 后缀标记这是逐篇求和后的"分子"中间量, 尚未除以对应的有效权重和分母 (分母列名形如 `sum_wd_hw_thr25_llm{track}`, 属于配套的另一家族), 面板上真正可直接解释为"加权平均语调"的是比值列 `llm_vote_tone_hw_thr25{track}` (= 本列 / 分母列), 而非本家族本身。之所以要把分子中间量也落到面板上, 是为了让下游 (审计脚本 / Stata `.do` 模板中手动构造替代比值) 能够复核加权均值的构造过程, 而不必信任一步到位的封装比值。

【方法学与计算】
计算发生在两阶段流水线内。第一阶段 stage 24 `herd_decay.py` 在文章级对每个相似度阈值 τ (含基线 0.35 与敏感性网格中的 0.25/0.30/0.40/0.45) 各自独立地做一次相似文章聚类与衰减权重计算, 产出 `herd_weight{track}_thr25` 一列 (逐轨道 full/ctx/ss 各一份, 因为聚类是在轨道对应的文本 `content_{track}` 上进行的, 不同轨道文本不同, 抄稿判定结果也随之不同)。第二阶段 `pipeline/panel/runner.py` 步骤 3d 用该权重列去加权 stage 21 的 `llm_vote_score{track}`, 得到文章级中间列 `llm_vote_score_hw_thr25{track}` (= `llm_vote_score{track} × herd_weight{track}_thr25`, 逐篇乘积)。第三阶段 `encode.py` 在按 `(target_bank, year)` 分组聚合时, 对该文章级乘积列取 `sum`, 写入本家族列 `llm_vote_score_hw_thr25_sum{track}`; 聚合遵循 `LLM 族 numerator NA-skip` 规则 —— `llm_vote_score{track}` 为 `<NA>` 的文章 (三家 LLM 未达多数一致, 或该文章未通过 stage 21 留篇门控) 不参与求和, 而非被当作 0 计入, 从而避免"未判定"与"判定为中性 0"混淆。与之配套, `encode.py::_build_llm_valid_masked_weights` 会构造一个"仅对有效行取值、无效行置 NaN"的分母权重列 `_wd_hw_thr25_llm{track}`, 聚合后成为 `sum_wd_hw_thr25_llm{track}`, 使分子分母统计的是同一批"LLM 真正给出判断"的文章, 避免把未判定文章的权重计入分母而系统性把加权语调拉向 0 (encode-01 号已知修正)。
留篇门控口径遵循 2026-06-29 起的 full-only 铁律: 一篇报道是否计入"银行-金科报道"样本只由 `llm_verified_full == True` 决定, ctx/ss 轨道的行宇宙是 full 轨留篇集合的子集 (conditional-on-full), 三轨各自独立计算加权和, 不互相借用彼此的分母或样本范围。三轨 (full/ctx/ss) 之间是"各自 just-identified 并排、互为稳健性、不分主次"的关系: full 用标题+正文全文, ctx 用标题+实体窗口, ss 用标题+银行∧金科同句 ±N 窗口 (无同句共现时回退为全文 body, 并置 `ss_is_fallback=True`, 语义上镜像 ctx 轨的回退规则); 三条轨道的加权和序列不应被合并进同一个 over-identified 的 Hansen J 检验框架, 而应各自作为独立的稳健性观察。τ=0.25 阈值本身同样是一个梯子刻度: 它与基线 τ=0.35 及另外三个候选阈值 (0.30/0.40/0.45) 一起构成抄稿判定敏感性梯子, 各阈值对应的加权和/加权均值列也是各自并排的稳健性观察, 用以证明主回归结论不依赖 0.35 这一具体门槛值的人为选择, 同样不应混入同一个 over-identified 设定。

【文献定位】
本家族的方法学定位处在两条文献脉络的交叉点。其一是媒体情感测量文献: 从 Tetlock (2007 JF) 用 Harvard IV 词典构造媒体悲观度指数, 到 Loughran & McDonald (2011 JF) 提出金融领域专用词典纠正通用词典的语境失配, 再到近年 LLM-based 情感抽取 (de Kok, 2025 Management Science, 系统论证了 temperature=0 与 prompt 冻结在会计/金融文本标注中的可复现性要求, 本项目 stage 21 的三家 LLM 多数投票范式与之呼应)。其二是媒体覆盖度量与信息含量文献: Fang & Peress (2009 JF) 证明媒体覆盖广度 (而非仅情感符号) 对股票定价具有独立解释力, 这正是抄稿衰减权重设计的理论出发点 —— 同一篇通稿被多家媒体机械转载不应被计为多条独立的市场关注信号, 需要用衰减权重去折算"有效报道篇数"。You, Zhang & Zhang (2018 RFS) 在中国媒体语境下的发现进一步支持了这一必要性: 中国媒体对企业 (含银行) 的报道存在系统性的选择性放大与压制模式, 若不对转载/雷同报道做权重折算, 银行-年语调均值会被少数被广泛转载的通稿主导。LLM 多数投票共识本身的稳健性则参照 Kamen & Kamen (2025) 关于集成式 LLM 多数表决在内容分类任务上优于单模型的发现, 支撑本项目采用三家异构 LLM 投票而非单一模型判定的设计选择。 沿着同一条线索, Wang、Wang 与 Huang (2025) 以排序投票 (ranked voting) 取代朴素多数票来聚合 LLM 的多个候选输出并实证聚合质量提升, 提示投票规则本身即是一处研究者自由度——本族分子沿用的仍是三家朴素多数票 llm_vote_score{track} ∈ {-1, 0, +1}, 该文在此仅用于交代该自由度的存在, 而非为现口径背书; 其迁移边界亦须如实标注: 原文的投票单元是同一模型多次采样得到的候选答案 (self-consistency) 而非跨厂商模型的标签投票, 任务为推理/生成而非三分类情感标注, 且只到样本级聚合为止, 不涉及本族的抄稿衰减加权与银行-年求和。分子所度量的构念是"针对目标银行"的实体级语调而非篇章整体基调, 这一点上 Rønningstad 与 Velldal (2024) 提供了同族实证: 该文评估 LLM 对特定目标实体的情感 (entity-level / targeted sentiment) 标注质量并与人工标注对比, 支持实体级 LLM 情感标注在本构念下的可行性。边界在于原文语料为挪威语/英语通用新闻与评论、目标实体非银行, 采用单一 GPT 模型而无三家投票与置信度概率化, 且只报告标注一致性, 不做银行-年面板聚合、抄稿衰减加权分子构造或三轨 (full/ctx/ss) 文本切分, 更未涉及本族的 τ 阈值敏感性梯子。
## VAR: llm_vote_score_hw_thr25_sum_ctx

【变体差分】
本列是 ctx 轨道 (标题 + 实体窗口文本) 上的 τ=0.25 抄稿衰减加权语调和。与 full 轨的区别在两处: 其一, 抄稿相似度聚类 (stage 24) 是在 `content_ctx` 文本上进行的, 而不是全文, 因此同一对文章在 ctx 轨与 full 轨下被判定为"相似抄稿"的结果可能不同 (窗口截断后两篇原本用词不同但围绕同一实体的报道, 相似度可能被拉高或拉低); 其二, 样本行宇宙是 full 轨留篇集合的子集 (conditional-on-full, 2026-06-29 起口径), 即某篇文章只有在 `llm_verified_full == True` 时才可能出现在 ctx 轨的求和范围内, ctx 轨自身不独立扩展留篇边界。ctx 轨的 `llm_vote_score_ctx` 与其对应的 `herd_weight_ctx_thr25` 均取自各自轨道专属的文章级列, 逐篇相乘后按 `(target_bank, year)` 分组求和, 缺失 (LLM 未定/未留篇) 的文章不计入分子, 分母对应的独立求和列位于配套家族。本列与 full/ss 两个同族变体是并排的稳健性观察, 不构成对彼此的替代或加总关系, 三者各自 just-identified, 不应混入同一个 over-identified 设定用于联合矩条件检验; 解读时应把 ctx 轨结果与 full 轨结果并列报告, 用以说明"聚焦实体窗口文本"是否改变基于抄稿衰减权重的语调结论。此外, 本列同时处在阈值敏感性梯子上: 与基线 τ=0.35 及其余候选阈值 (0.30/0.40/0.45) 下的 ctx 轨同名分子列并排, 二者的差异只反映抄稿相似度判定门槛的松紧, 与轨道选择正交, 不应交叉解读为轨道效应。

## VAR: llm_vote_score_hw_thr25_sum_full

【变体差分】
本列是 full 轨道 (标题 + 完整正文) 上的 τ=0.25 抄稿衰减加权语调和, 是本家族三个变体中口径最宽、留篇门控的锚定轨道: 一篇报道是否被判定为"一篇有效的银行-金科报道"完全由 full 轨的 `llm_verified_full == True` 决定 (2026-06-29 起的 full-only 门控铁律), ctx 与 ss 两个轨道的样本范围都是 full 轨留篇集合的真子集, 而非各自独立扩样。相应地, `llm_vote_score_full` 与 `herd_weight_full_thr25` 均基于完整正文文本计算 —— 抄稿相似度聚类在全文层面进行, 能够捕捉到仅在正文细节 (而非标题或局部窗口) 才显现的高度雷同段落, 因此 full 轨识别出的"抄稿群"规模与结构通常与 ctx/ss 轨不同。本列作为面板上多个 paper 主处理变量 (treatment) 的口径基础之一 (P1 `llm_vote_tone_full` 等主轨已切换为 full-only 锚点), 在需要引用"生产口径下的加权语调分子"时应以本列 (而非 ctx/ss 变体) 为准; 但作为 τ=0.25 敏感性网格中的一个刻度, 它仍与基线 τ=0.35 及其余候选阈值下的同名列并排, 用于阈值敏感性检验, 而不应替代基线口径直接用于主回归。full 轨与 ctx/ss 轨之间同样是并排稳健性关系而非层级关系: 三轨各自独立完成抄稿聚类与加权求和, 不共享聚类结果, 也不存在"full 是主、ctx/ss 是补充计算"的从属计算依赖, 仅在留篇门控这一件事上 ctx/ss 依赖 full 轨的判定结果。

## VAR: llm_vote_score_hw_thr25_sum_ss

【变体差分】
本列是 ss 轨道 (标题 + 银行∧金科同句 ±N 窗口文本) 上的 τ=0.25 抄稿衰减加权语调和。其文本构造判据与 ctx 轨不同: ss 要求银行实体与金科关键词在同一句 (或配置的 ±N 句窗口, 默认半径 1) 内共现才纳入窗口文本, 若某篇留篇文章不存在这种同句共现, `content_ss` 回退为全文 body 且置 `ss_is_fallback=True`, 该回退语义与 ctx 轨镜像一致 (回退时的分母与 full 轨共享 `n_articles` 口径)。抄稿相似度聚类 (stage 24) 与 LLM 语调判定均在这一 ss 专属文本上进行, 因此即便某文章在 full/ctx/ss 三轨下都被判定为留篇, 三轨各自的 `herd_weight_thr25` 取值及所属抄稿群划分也可能互不相同, 导致本列的求和结果与 full/ctx 两个变体在数值上不必然一致, 也不构成对彼此的加总或替代。ss 轨样本行宇宙同样是 full 轨留篇集合的子集 (conditional-on-full), 不独立扩展。本列与 ctx/full 两变体、以及同一 ss 轨下基线阈值 τ=0.35 与其余敏感性阈值的同名列, 均各自 just-identified 并排, 互为稳健性观察, 禁止混入同一个 over-identified Hansen J 或联合矩条件检验框架中联合估计。由于 ss 判据 (同句共现) 比 ctx 判据 (实体窗口) 更严格, 当研究者观察到 ss 轨回退比例 (`ss_is_fallback` 占比) 偏高时, 应结合 full 轨结果交叉核对, 避免把"回退样本占主导"误读为"同句共现结构本身的语调效应"。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who Captures the Power of the Pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Fang, L., & Peress, J. (2009). Media Coverage and the Cross-Section of Stock Returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
de Kok, T. (2025). ChatGPT for Textual Analysis? How to Use Generative LLMs in Accounting Research. Management Science, 71(9), 7888-7906. https://doi.org/10.1287/mnsc.2023.03253
Kamen, A., & Kamen, Y. (2025). Majority Rules: LLM Ensemble is a Winning Approach for Content Categorization. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2511.15714
Wang, W., Wang, Y., & Huang, H. (2025). Ranked Voting based Self-Consistency of Large Language Models. Findings of the Association for Computational Linguistics: ACL 2025, 14410-14426. https://doi.org/10.18653/v1/2025.findings-acl.744
Rønningstad, E., Velldal, E., & Øvrelid, L. (2024). A GPT among Annotators: LLM-based Entity-Level Sentiment Annotation. Proceedings of the 18th Linguistic Annotation Workshop (LAW-XVIII), 133-139. https://doi.org/10.18653/v1/2024.law-1.13
<!-- rendered-citations:end -->
