---
family_id: F242
columns:
- exc_du_2022_score_ctx
- exc_du_2022_score_full
- exc_du_2022_score_hw_ctx
- exc_du_2022_score_hw_full
- exc_du_2022_score_hw_ss
- exc_du_2022_score_ss
- exc_du_2022_score_w_ctx
- exc_du_2022_score_w_full
- exc_du_2022_score_w_ss
unit: 无量纲情感得分 (银行-年均值; 基线归一化轨 ∈ [-1, +1], 加权轨为幅度可放大的实数)
formula: "exc_du_2022_score{sfx}{track} = mean_{i ∈ 非停刊媒体报道} du_2022_score{sfx}{track}_i; sfx ∈ {空, _hw (跟风衰减权), _w (价值权/提及密度)}; track ∈ {_full, _ctx, _ss}; 分母 = 该银行-年 _is_ceased_media==0 的报道数"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity
upstream:
- 22_tone_words.parquet (article: du_2022_score{track} 原始未加权情感得分; _hw/_w 两加权变体不落盘该 parquet, 由 runner.py 步骤 3b/3d 在 panel 构建阶段现算, 见下两条)
- 24_herd_decay_processor.parquet (herd_weight{track}, 供 pipeline/panel/runner.py 步骤 3d 现算 du_2022_score_hw{track} = du_2022_score{track} × herd_weight{track})
- 11_news_bank.py (mention_density 提及密度, 供 runner.py 步骤 3b 现算 du_2022_score_w{track} = du_2022_score{track} × mention_density)
- attention_media.py::detect_defacto_cessation (_is_ceased_media 停刊代理标记, 由本 producer 自身在运行期对传入 df 现场计算赋值, 非从 40_article_bank_level.parquet 读入的既有列)
citations:
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.1016/j.jfineco.2017.01.006
  type: journal
  authors: Hwang, B.-H., & Kim, H. H.
  year: 2017
  title: "It pays to write well"
  venue: Journal of Financial Economics
  vol: 124
  issue: 2
  pages_or_artno: 373-394
new_dois: []
---

## CORE

【构念与来源】
本家族度量的是"剔除疑似停刊媒体后重算的 Du 词典情感均值", 是主线银行-年情感测度的一条幸存者偏差 (survivorship bias) 稳健性轨。构念底座是 Du et al. (2022) 在 Review of Finance 发表的中文金融情感词典: 该词典针对中文财经语料的语言与领域特异性专门构建, 相较于英文词典直译更贴合中国市场用语, 是本项目六部情感词典之一 (列前缀 du_2022)。词典法在每篇报道上产出归一化情感得分 du_2022_score, 落在 [-1, +1] 区间, 正值偏正面、负值偏负面、零附近中性。近年中文投资者情感词典研究 (如 Ma et al. (2025) 构建的 CN-FSD 细粒度词典) 进一步印证了领域专用词典对中文金融文本效度的重要性, 为本项目坚持词典法作为 LLM/BERT 之外的独立稳健性支柱提供了外部方法学支撑。
本家族在 du_2022_score 的基础上叠加两层结构: 其一是"停刊剔除"这一样本层过滤, 其二是三种加权方案与三条文本轨的正交组合。停刊剔除的动机在于, 媒体来源在样本期内退出本地覆盖会引入幸存者偏差 — 情感指标会向存活媒体倾斜, 进而污染以媒体暴露为工具变量的 Bartik 类识别。项目用 detect_defacto_cessation 侦测"隐性覆盖退出"(报道时间序列出现异常长的覆盖断裂), 把疑似退出的媒体保守地标为 _is_ceased_media, 再在银行-年层只对存活媒体报道求情感均值, 得到 exc_ 前缀列。这一保守剔除的因果依据来自报纸关停实证谱系: Heese et al. (2022) 发现地方报纸关停会导致本地监督真空、公司违规上升, 说明"覆盖退出"本身携带系统性信息, 不能当作随机缺失处理。
构念上必须诚实披露源码本身要求的两点保留: 其一, detect_defacto_cessation 的排除集 = 数据驱动侦测的 confirmed ∪ suspected, NPPA (国家新闻出版署) 交叉验证只改报告标签、不收窄排除集 — 也就是说 suspected (未经 NPPA 证实的疑似退出媒体) 仍全量进入排除集, 这是一个偏保守 (宁可多剔) 的设计选择。其二, 源码明确要求下游文档不得把这一稳健性口径表述为严格意义上的"报纸关停" (publication cessation): 本家族捕捉的是"话题覆盖退出" (topic exit, 即该媒体不再报道目标银行相关话题) 这一代理现象, 与经证实的、编辑部整体停刊的 publication cessation 是两个不同构念, 二者可能重叠但不等同 — 例如媒体仍在运营但转向其他报道方向, 也会被本侦测算法标为覆盖退出。因此 exc_ 前缀列应严格解读为"剔除疑似退出本地银行报道覆盖的媒体后的稳健性对照轨", 不可在论文正文中写成"剔除已停刊报纸后的情感"这类过度确定的表述。

【方法学与计算】
计算链路跨两个阶段, 须分清各自的落盘边界。第一步在文章层 stage 22 tone_words 只产出无加权的原始 du_2022_score{track} (三条文本轨各一份), 这是唯一落盘进 22_tone_words.parquet 的 du_2022 情感列; tone_words.py 源码中不存在任何 _hw/_w 后缀列的生成逻辑。第二步在 pipeline/panel/runner.py 面板构建阶段现算两个加权中间列: 步骤 3b 用 stage 11 news_bank.py 产出的 mention_density (提及密度) 与 du_2022_score{track} 相乘, 现算 du_2022_score_w{track} (价值权); 步骤 3d 用 stage 24 herd_decay_processor 产出的 herd_weight{track} 与 du_2022_score{track} 相乘, 现算 du_2022_score_hw{track} (跟风衰减权)。这两个加权列是 runner.py 内存中的中间量, 不对应任何独立落盘的 parquet 文件, 仅供后续聚合环节消费。第三步在 compute_media_heterogeneity 中, 由 detect_defacto_cessation 在运行期对传入 df 现场计算并赋值 _is_ceased_media 标记 (该标记不是从任何上游 parquet 读入的既有列, 而是本 producer 自身的计算逻辑), 随后筛掉 _is_ceased_media==1 的报道, 对剩余存活媒体报道 (无权及两个已加权变体) 按银行-年分组取简单均值, 即 exc_du_2022_score{sfx}{track}。分母是该银行-年存活媒体报道数 (对应 n_articles_exc), 与全样本 n_articles 不同。加权轨 _w/_hw 的取值已含权重放大, 故其银行-年均值不再严格落在 [-1,+1], 应解读为幅度可比的相对情感强度而非概率。停刊比例本身单列为 ceased_media_frac; 缺存活报道的银行-年按契约保留 NaN, 不做零填 (情感类不可加, 与计数类填零口径不同)。
三条文本轨的口径遵循项目统一定义: full=标题 prepend 全文正文; ctx=标题+实体窗口; ss=标题+银行与金科同句共现窗 (无共现则回退为全文正文, 镜像 ctx 回退语义)。三种加权 (无权/跟风衰减 _hw/价值权 _w) 与三条轨互为稳健性、不分主次, 各自 just-identified 并排进入模型, 严禁把不同权重或不同轨混进同一 over-identified 的 Hansen J 过度识别检验。停刊剔除轨与全样本轨同理: 它是主测度的稳健性对照臂, 用于验证主结论不被媒体退出驱动, 而非替代主测度。

【文献定位】
本家族在文献上处于三条线的交叉: 词典情感测量 (Du et al. (2022); Ma et al. (2025))、文本信息的市场含义 (Hwang & Kim (2017) 论文本可读性/写作质量与资产定价关联, 支撑"文本特征携带可定价信息"这一前提)、以及媒体覆盖退出的幸存者偏差治理 (Heese et al. (2022))。词典法的价值在于其完全透明、可复现、零 API 成本, 与 LLM 三家投票、BERT 三模型构成互为稳健性的多方法三角; 停刊剔除轨则把稳健性从"测量方法"维度延伸到"样本构成"维度, 回应审稿人可能提出的"媒体样本非随机流失是否污染情感面板"这一质疑。

## VAR: exc_du_2022_score_full

【变体差分】
本列为家族在 full 轨、无加权 (基线) 组合下的停刊剔除情感均值。full 轨 = 标题 prepend 后拼接全文正文, 是信息最全的文本轨, 也是项目留篇门控 (full-only, 2026-06-29) 的判定轨。取值为 du_2022_score_full 在该银行-年全部存活媒体 (_is_ceased_media==0) 报道上的简单算术均值, 落在 [-1, +1], 正负号与全样本 du_2022 情感一致。与家族 canonical 的差分维度只有一个: 文本轨=full 且加权=无。它与 _ctx/_ss 两轨、与 _hw/_w 两加权变体互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。本列的独特用途是"最全文本 × 最简聚合 × 停刊剔除"的三重基准: 若主回归在全样本 full 轨成立而本列不成立, 提示结论可能由退出媒体驱动, 应作为幸存者偏差的直接诊断。
需要强调的是, 本列的分母是存活媒体报道数 n_articles_exc 而非全样本 n_articles, 因此即便情感均值本身与主测度接近, 其背后的有效样本也已收窄; 在解读时应同时对照 ceased_media_frac 停刊比例, 该比例越高说明剔除越激进、本列与全样本列的偏离越具诊断意义。词典法在此扮演的是零成本、完全可复现的独立锚: 相较 LLM 三家投票与 BERT 三模型, du_2022 词典不依赖任何 API 调用, 便于在生产 T=18 全量语料上无成本地跑通停刊剔除稳健性, 是审稿复现包里最易被独立第三方重算的一条轨。

## VAR: exc_du_2022_score_ctx

【变体差分】
本列为 ctx 轨、无加权组合的停刊剔除情感均值。ctx 轨 = 标题+目标银行实体上下文窗口 (由 stage 14 ctx_materializer 物化 content_ctx), 相较 full 轨聚焦到银行被提及的邻近语句, 剔除远离主体的噪声段落。取值为 du_2022_score_ctx 在该银行-年存活媒体报道上的简单均值 ∈ [-1, +1]。与 canonical 的差分: 文本轨=ctx 且加权=无。ctx 轨相对 full 轨是"信息更聚焦但覆盖更窄"的权衡臂: 当报道大篇幅涉及银行以外主体时, ctx 能避免无关情感稀释银行本身的语调。本列同样是稳健性轨, 与 full/ss 两轨、_hw/_w 两加权互为稳健性、不分主次, 各自 just-identified 并排, 禁混同一 over-identified Hansen J。在 T=2 开发盘上 ctx/ss 轨可能因样本稀薄退化, 属预期现象, 生产 T=18 语料下方可正常出值。
ctx 轨与 full 轨的差异本质是"分母口径"之别: full 轨把整篇报道的情感都算入银行, ctx 轨只算银行实体邻近窗口内的情感。当一篇报道同时涉及多家主体、或银行只是配角时, 二者会显著分叉; 本列在停刊剔除基础上进一步用 ctx 收窄语境, 提供"存活媒体 × 聚焦语境"的双净化视角。若主结论在 full 停刊轨与 ctx 停刊轨上同号同显著, 说明结论既不被退出媒体驱动, 也不被无关语境情感稀释所掩盖, 是较强的联合稳健性证据。

## VAR: exc_du_2022_score_ss

【变体差分】
本列为 ss 轨、无加权组合的停刊剔除情感均值。ss 轨 = 标题+"银行与金融科技同句共现"窗口 (content_ss): 只保留目标银行与金科词在同一句 (可含 ±N 句半径, 默认 1) 共现的语境; 若该报道无银行∧金科同句共现, ss 轨优雅回退为全文正文并置 ss_is_fallback=True, 回退语义严格镜像 ctx 轨。取值为 du_2022_score_ss 在存活媒体报道上的银行-年均值。与 canonical 的差分: 文本轨=ss 且加权=无。ss 轨是三轨中最严的语境约束, 专门捕捉"银行涉金科语境"下的情感, 是 P1 等主线论文界定"银行金科报道"的最窄口径。它与 full/ctx、_hw/_w 互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。停刊剔除叠加同句约束后, 存活报道数进一步收缩, 缺样本银行-年按契约保留 NaN。
ss 轨的回退机制值得单独说明: 当一篇报道虽提及银行但银行与金科词从未落在同一句时, content_ss 会回退为整篇正文并置 ss_is_fallback=True, 此时该篇的 ss 情感实际等同于 full 情感。因此本列在共现稀疏的银行-年会向 full 停刊轨收敛, 而在共现密集的银行-年才真正体现"银行涉金科语境"的独立信号; 解读时应结合 frac_ss_fallback 回退比例判断本列的语境纯度。作为家族中语境最严的无权轨, 本列与 full/ctx 无权轨构成语境宽窄的三点稳健性谱, 三者各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: exc_du_2022_score_hw_full

【变体差分】
本列为 full 轨、跟风衰减加权 (_hw) 的停刊剔除情感均值。_hw 权重来自 stage 24 herd_decay_processor 产出的 herd_weight_full: 依据"旧信息经重复报道后边际信息含量随时间衰减"这一项目内建模思想, 对抄稿/转载/跟风报道下压权重, 让首发、原创报道在情感聚合中占更大份额。文章层先算 du_2022_score_hw_full = du_2022_score_full × herd_weight, 本列再在银行-年存活媒体报道上取均值。与 canonical 的差分: 文本轨=full 且加权=跟风衰减 _hw。因含权重放大, 取值不再严格落 [-1,+1], 应解读为去重复化后的相对情感强度。本列与无权/价值权两变体、与 ctx/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。用途是回应"情感面板是否被大量同质转载稿放大"的稳健性质疑, 同时叠加停刊剔除双重净化。
需要区分本列与全样本 hw 轨的关系: 跟风衰减权处理的是"同一条信息被多家媒体重复转载导致的情感放大", 停刊剔除处理的是"媒体退出导致的样本非随机流失", 二者是正交的两种偏差来源。本列同时施加两种校正, 因此它检验的是主结论对"重复报道放大 × 媒体退出流失"联合扰动的稳健性。herd_weight 由 stage 24 herd_decay_processor 三轨独立产出, 缺列时由 valid_agg 优雅跳过; 权重值域使本列失去 [-1,+1] 的概率解读, 只能作幅度相对比较, 跨列比较时须先标准化以免不同权重尺度混淆系数。

## VAR: exc_du_2022_score_hw_ctx

【变体差分】
本列为 ctx 轨、跟风衰减加权 (_hw) 的停刊剔除情感均值。文本轨口径同 exc_du_2022_score_ctx (标题+银行实体窗口), 加权口径同 _hw (herd_weight_ctx 下压抄稿/跟风报道, 按报道信息新鲜度衰减建模)。文章层取值 du_2022_score_hw_ctx = du_2022_score_ctx × herd_weight_ctx, 本列在银行-年存活媒体报道上取均值。与 canonical 的差分: 文本轨=ctx 且加权=跟风衰减 _hw, 两个差分维度同时偏离基线。它把"聚焦银行邻近语境"与"抑制重复报道"两种净化叠加在停刊剔除之上, 是三重稳健化的组合臂。与家族内其余八列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。因含权重放大与语境收窄双重作用, 取值幅度与覆盖度均可能偏离 full 无权基线, 缺样本银行-年保留 NaN, 不做零填。
本列在诊断上的价值在于把两个正交维度 (语境聚焦 ctx、重复抑制 hw) 叠加于停刊剔除之上, 提供介于 full-hw 与 ss-hw 之间的中间约束强度。当 full-hw 停刊轨显著而本列不显著时, 提示信号可能来自银行邻近语境之外的段落; 当本列显著而 ss-hw 不显著时, 提示信号更多来自宽于同句金科窗的银行语境。这种逐轨、逐权的分层对照, 正是词典法作为透明可复现测度的优势所在: 每一层过滤的边际影响都可被独立第三方重算核验, 无需依赖任何付费模型的黑箱输出。

## VAR: exc_du_2022_score_hw_ss

【变体差分】
本列为 ss 轨、跟风衰减加权 (_hw) 的停刊剔除情感均值。文本轨口径同 exc_du_2022_score_ss (银行与金科同句共现窗, 无共现回退全文, 镜像 ctx), 加权口径同 _hw (herd_weight_ss 下压重复/跟风报道)。文章层取值 du_2022_score_hw_ss = du_2022_score_ss × herd_weight_ss, 本列在存活媒体报道上取银行-年均值。与 canonical 的差分: 文本轨=ss 且加权=跟风衰减 _hw。本列是家族中约束最强的组合之一: 同句金科语境 + 去重复化 + 停刊剔除三层过滤同时生效, 存活样本最稀薄, 在 T=2 开发盘常见退化或 NaN, 生产 T=18 下正常出值。它与其余八列互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。用途是在最窄语境下验证情感结论对重复报道与媒体退出的双重不敏感性。
由于同句金科语境、跟风衰减权、停刊剔除三层过滤同时作用, 本列的有效样本在三条无权轨与三条 hw 轨中最稀薄, 应对其 T=2 开发盘上的 NaN 或零方差保持宽容, 不得据此判定实现缺陷。生产 T=18 语料下, 本列才具备足够的跨银行-年变异供识别使用。它在稳健性叙事中扮演"最保守情形"的角色: 若主结论连在这条最严组合轨上都稳健, 则对任何单层过滤的稳健性均可由此推得, 是稳健性梯子的下界锚。与家族其余八列各自 just-identified 并排, 禁混同一 over-identified Hansen J。

## VAR: exc_du_2022_score_w_full

【变体差分】
本列为 full 轨、价值加权 (_w) 的停刊剔除情感均值。_w 权重为报道的提及密度 (mention_density), 遵循项目内建的提及密度价值加权思想: 目标银行被提及越密集的报道, 越可能是关于该银行的实质性新闻, 应在情感聚合中占更高权重。文章层取值 du_2022_score_w_full = du_2022_score_full × 提及密度权, 本列在银行-年存活媒体报道上取均值。与 canonical 的差分: 文本轨=full 且加权=价值权 _w。因含权重放大, 取值不严格落 [-1,+1]。本列与无权/跟风衰减两变体、与 ctx/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。用途是检验情感结论是否稳健于"按报道相关性重加权", 即主结论不由大量低相关、擦边提及银行的报道驱动, 同时叠加停刊剔除净化。
价值权 _w 与跟风衰减权 _hw 是两种不同哲学的加权: _hw 按"信息新鲜度/是否首发"下压重复稿, _w 按"报道与银行的相关强度"上抬密集提及稿, 二者可对同一篇报道给出相反的权重调整。因此本列 (价值权) 与 hw 轨互为独立的加权稳健性臂, 不可相互替代, 更不可并入同一 over-identified Hansen J。提及密度权 mention_density 由文章层预计算, 缺列时优雅跳过; 因权重放大, 本列取值不再落 [-1,+1], 跨列比较须先标准化。它在停刊剔除之上叠加相关性重加权, 回应"情感是否被擦边提及稿稀释"的质疑。

## VAR: exc_du_2022_score_w_ctx

【变体差分】
本列为 ctx 轨、价值加权 (_w) 的停刊剔除情感均值。文本轨口径同 exc_du_2022_score_ctx (标题+银行实体窗口), 加权口径同 _w (提及密度价值权, 按目标银行提及密集度上抬实质性报道)。文章层取值 du_2022_score_w_ctx = du_2022_score_ctx × 提及密度权, 本列在银行-年存活媒体报道上取均值。与 canonical 的差分: 文本轨=ctx 且加权=价值权 _w, 两维度同时偏离基线。它把"聚焦银行邻近语境"与"按相关性重加权"两种口径叠加在停刊剔除之上。与家族内其余八列互为稳健性、不分主次, 各自 just-identified 并排, 禁混进同一 over-identified Hansen J。由于 ctx 轨覆盖较窄且价值权放大提及密集报道, 本列既检验语境聚焦稳健性又检验相关性重加权稳健性, 缺样本银行-年保留 NaN, 情感类不做零填。
本列与 exc_du_2022_score_hw_ctx 构成一个有启发性的对照对: 二者文本轨同为 ctx、同经停刊剔除, 唯一差别是加权哲学 (价值权 vs 跟风衰减权)。若两列结论一致, 说明主效应对"如何给报道加权"这一自由度不敏感, 极大压缩了变量农场 (variable farming) 质疑的空间; 若两列分叉, 则揭示情感信号更依赖某一类报道 (高相关密集稿 vs 首发原创稿), 本身即是有价值的机制线索。二者仍须各自 just-identified 并排, 严禁并入同一 over-identified Hansen J。

## VAR: exc_du_2022_score_w_ss

【变体差分】
本列为 ss 轨、价值加权 (_w) 的停刊剔除情感均值。文本轨口径同 exc_du_2022_score_ss (银行与金科同句共现窗, 无共现回退全文, 镜像 ctx 回退语义), 加权口径同 _w (提及密度价值权, 按目标银行提及密集度上抬实质性报道)。文章层取值 du_2022_score_w_ss = du_2022_score_ss × 提及密度权, 本列在存活媒体报道上取银行-年均值。与 canonical 的差分: 文本轨=ss 且加权=价值权 _w。本列在同句金科语境这一最窄口径上叠加相关性重加权与停刊剔除, 是三重净化组合臂, 存活样本最稀薄, T=2 开发盘常见退化或 NaN, 生产 T=18 正常。它与家族其余八列互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。用途是在最严语境下验证情感结论对报道相关性权重与媒体退出的双重不敏感性。
本列与 exc_du_2022_score_hw_ss 是家族中约束最强的一对: 二者同为 ss 轨、同经停刊剔除, 仅加权哲学不同 (价值权 vs 跟风衰减权)。作为价值权侧的最严组合, 本列在共现稀疏银行-年会因 ss 回退而向 full 价值权轨收敛, 在共现密集银行-年才体现"银行涉金科语境 × 高相关报道"的纯净信号, 解读时应结合 frac_ss_fallback 判断语境纯度与 mention_density 权重分布。由于同句约束、相关性重加权、停刊剔除三重收窄, 本列在 T=2 开发盘常为 NaN 属预期退化, 生产 T=18 方具识别力; 它与家族其余八列各自 just-identified 并排, 严禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
<!-- rendered-citations:end -->
