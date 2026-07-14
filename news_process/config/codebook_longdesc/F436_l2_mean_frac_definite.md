---
family_id: F436
columns:
- mean_frac_definite_ctx
- mean_frac_definite_full
- mean_frac_definite_ss
unit: 词元占比 (token fraction, [0,1] 区间; 分子=文章内确定性词元命中数, 分母=该文章清晰度词典基准词元数)
formula: "mean_frac_definite_{track}[b,t] = Σ_valid w_i × frac_definite_{track}_i / Σ_valid w_i, 其中 frac_definite_{track}_i = n_definite_{track}_i / n_tokens_clarity_base_{track}_i, w_i 为篇章权重 (默认等权 1); frac_definite_{track}_i 在阶段 22 落盘时以 clarity_frac_definite_{track} 为实际列名 (clarity_ 命名空间前缀, 见 pipeline/sentiment/tone_words.py 第1732行重命名环节 merged[clarity_{k}_{track}] = v), 阶段 40 消费方 encode_collab.py::aggregate_clarity_panel 按 clarity_frac_definite_{track} 读取该列后聚合为无前缀的面板列 mean_frac_definite_{track}"
producer: pipeline\panel\encode_collab.py::aggregate_clarity_panel ; pipeline\panel\codebook.py
upstream:
- 22_tone_words (clarity_frac_definite_{track} 文章级词典扫描列, tone_words.py 内部以 frac_definite 键计算后按 clarity_{k}_{track} 命名空间前缀落盘)
- 14_materialize_ctx (content_ctx / content_ss 三轨文本物化)
citations:
- doi: 10.1093/rfs/hhx055
  type: journal
  authors: "You, J., Zhang, B., & Zhang, L."
  year: 2018
  title: "Who captures the power of the pen?"
  venue: The Review of Financial Studies
  vol: 31
  issue: 1
  pages_or_artno: 43-96
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: "Loughran, T., & McDonald, B."
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: "Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K."
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
new_dois: []
---

## CORE

【构念与来源】
本家族刻画的核心构念是"银行金融科技报道文本中确定性语言的相对占比", 大白话说, 就是记者在描述一家银行的金融科技动态时, 用词是斩钉截铁、明确表态型的 (比如"将""必然""确定""已经"), 还是含糊其辞、留有余地型的 (比如"可能""或许""预计")。一篇新闻里确定性词元用得越多, frac_definite 越高, 意味着这篇报道传递的信息在措辞层面越"实锤"; 反之则说明报道更偏推测、试探、留白。这个构念承接的是清晰度 (clarity) 与文本可读性两条并行的学术脉络。You, Zhang & Zhang (2018) 在中国上市公司新闻语境下构造了一套区分"确定性词汇"与"模糊性词汇"的中文词典 (Panel C/D), 用以刻画媒体报道措辞的果断程度, 是本家族词典与判据的直接学术锚点。Loughran & McDonald (2011) 则为金融领域词典化文本测量确立了方法学基石——他们证明通用情感/语气词典搬到财务文本上会系统性失真, 必须针对金融语域专门构造词表, 这一原则同样适用于确定性/模糊性词汇的甄别 (通用汉语里的"可能"未必在金融报道语境下承载同等程度的模糊语义)。Bonsall, Leone, Miller & Rennekamp (2017) 从可读性角度提出"平实英语"综合测度, 把句式负担、词汇难度等维度并入单一清晰度评分, 启发了本项目把"确定性占比"作为清晰度家族里独立于可读性、但同属"文本表达明晰程度"范畴的互补分量。frac_definite 与家族姊妹指标 mean_clarity_score (clarity_score = frac_definite − frac_ambiguous) 及二值化指标 frac_amb_articles 共同构成 v3.5.1 A1 清晰度补强族, 是备份连续指标而非替代关系: clarity_score 做净额差分, frac_definite 单独保留确定性一侧的绝对水平信息, 避免净额相减掩盖"两类词都用得多"或"两类词都用得少"的不同文本风格。

【方法学与计算】
frac_definite 的计算发生在两个流水线阶段。阶段 22 (tone_words) 在文章层面对 content_full / content_ctx / content_ss 三轨文本各自独立做确定性词典扫描, 命中确定性词元数记为 n_definite_{track}, 除以该轨清晰度词典的基准词元总数 n_tokens_clarity_base_{track} (即该文章参与清晰度判定的有效词元数, 而非全文分词数), 得到文章级连续比例 frac_definite_{track}_i ∈ [0,1]。该比例在落盘时被套上 clarity_ 命名空间前缀, 实际物理列名为 clarity_frac_definite_{track}, 与同批次落盘的 clarity_frac_ambiguous_{track}/clarity_clarity_score_{track} 共享同一前缀约定, 用以和词典族其余非清晰度列 (情感极性/否定翻转等) 在同一张文章级宽表里区分命名空间; 阶段 40 聚合函数按这一带前缀的真实列名读取上游数据, 产出时再落回不带前缀的面板列名 mean_frac_definite_{track}, 这一"文章层带前缀、面板层去前缀"的转换发生在 encode_collab.py 内部而非独立的重命名脚本。阶段 40 (encode_collab.py::aggregate_clarity_panel) 再把文章级列聚合到银行—年度面板层: 对同一银行同一年度下的全部有效文章 (即该轨清晰度扫描非缺失的文章), 以权重 w_i (默认等权, 与 llm_vote_tone 等家族一致, 未启用提及密度/媒体权威/羊群衰减等专属加权口径) 做加权平均, 得到 mean_frac_definite_{track}[b,t] = Σ w_i × frac_definite_{track}_i / Σ w_i。分母口径遵循 2026-06-11 修订: n_clarity_valid_{track} < 2 (该银行年度下清晰度非缺失文章不足 2 篇) 时整格记为 NaN 而非假零, 避免样本量过小导致的伪精度; 空文或零 token 文章在 tone_words 阶段已显式记 NaN, 不会被错误计入物理分母造成系统性下偏。三轨口径 (full/ctx/ss) 各自独立扫描、独立聚合、各自 just-identified 并排, 互为稳健性、不分主次, 严禁混进同一 over-identified 的 Hansen J 检验——full 轨是标题+正文全文扫描, ctx 轨是标题+银行实体窗口扫描, ss 轨是标题+银行与金科同句 (±1 句默认半径) 扫描; 三轨分母口径不直接可比 (ctx/ss 文本长度显著短于 full, 论文披露口径见家族姊妹变量 notes), 因此跨轨比较应看方向一致性而非绝对水平差。ss 轨遵循镜像 ctx 的回退语义: 若某文章无银行∧金科同句共现, 则该文章 content_ss 回退为全文 body 且 ss_is_fallback 记 True, 与 n_articles 共享分母; 若清晰度词典整体缺席 (旧版 parquet 未产出 clarity_*_ss 列), 该轨在聚合环节被优雅跳过, 不影响 full/ctx 两轨照常产出。留篇门控口径 (2026-06-29 起) 采用 full-only 判定: 一篇报道是否被计为"一篇银行金科报道"只看 llm_verified_full, ctx/ss 两轨的清晰度聚合行宇宙是 full 留篇集的子集, 各轨列值仍按各自文本独立计算, 不借用彼此的判定结果。

【文献定位】
本家族在文本测度谱系中处于"叙事语气确定性"这一相对小众但方法学脉络清晰的子领域。You, Zhang & Zhang (2018) 在《金融研究评论》上系统论证了中国媒体报道措辞的确定/模糊程度与后续股价反应、机构关注度存在稳健关联, 提出媒体在"能确定的事说死、不能确定的事留白"这一叙事策略本身携带增量信息, 是本家族最直接的构念与词典来源, 其 Panel C 词表在本项目里被逐字复用为确定性词元判据的基础。Loughran & McDonald (2011) 虽然聚焦的是正负情感与不确定性 (uncertainty) 词典而非确定性词典本身, 但他们提出的"金融语域词典须专门构造、不可套用通用语言学词典"这一方法学原则, 是本项目在中文语境下沿用 You et al. 词表而非直接套用通用汉语"确定性副词表"的理据; 同时 Loughran & McDonald 的 uncertain 词类别与本家族的 definite 词类别在语义上互为镜像 (不确定性上升往往伴随确定性下降), 因此常被同一批论文并列引用作方法学对照。Bonsall, Leone, Miller & Rennekamp (2017) 的平实英语测度提醒研究者: 清晰度是多维构念, 句法复杂度 (可读性维度) 与措辞确定性 (本家族维度) 是两条彼此正交但都指向"文本传达信息难易程度"的分量, 不应用单一综合评分掩盖两者各自的方向性。本项目把 frac_definite 作为清晰度综合指标 clarity_score 的连续备份分量单独物化保留 (而非仅保留净额差), 呼应了 Bonsall et al. 倡导的"多维并行、不强行合一"的测度设计取向, 也是家族 notes 中所述"与 LLM substance 做 HTMT discriminant validity" (阶段 39d) 稳健性检验的基础——只有分量粒度足够细, 判别效度检验才能定位清晰度构念与实质性报道构念之间的真实重叠边界, 而非被合成指标掩盖。

## VAR: mean_frac_definite_full

【变体差分】
本列是家族 canonical 轨道, 基于 content_full (标题 + 正文全文) 做确定性词元扫描后聚合。分子 n_definite_full_i 统计一篇报道全文范围内命中 You et al. (2018) Panel C 确定性词表的词元数, 分母 n_tokens_clarity_base_full_i 是该文章参与清晰度判定的全部有效词元数, 两者之比在文章层得到 frac_definite_full_i, 再按银行—年度分组做等权 (或既定加权口径) 汇总。作为三轨中文本覆盖面最完整的一轨, full 轨样本量最大、单篇内命中的确定性词元绝对数也最多, 因此该列的分母口径 (即"参与判定的词元基数") 明显宽于 ctx/ss 两轨, 三轨数值不可直接混同比较水平, 只能比较符号方向或做标准化后比较。作为 P1 (bank_fintech_tone) 等主线论文里稳健性检验轨的一部分, 该列与其余情感/清晰度测度共享 full-only 留篇门控——只有 llm_verified_full == True 的文章才进入该银行年度的清晰度聚合样本, 与其余全文轨测度使用同一行宇宙, 便于跨测度做同期可比的敏感性分析。由于 full 轨扫描的是标题加正文全文, 它天然涵盖了记者在导语、正文主体、结尾展望等各个段落里所有明确表态或留有余地的措辞, 因此该列最适合回答"一篇报道整体上给读者留下的确定感有多强"这类粗粒度问题, 而不追问确定性语言具体出现在文章的哪个位置。与 ctx/ss 两轨相比, full 轨样本量最大、缺失率最低——只要文章本身非空且未被 stage 22 判定为零 token, 就几乎必然能计算出有效的 frac_definite_full_i, 不受银行实体窗口或银行∧金科同句这类更苛刻空间判据的约束, 这也是它被选作 canonical 轨、供其余轨对照的现实原因。在稳健性解读上, 若某银行年度的 mean_frac_definite_full 明显高于同期 mean_frac_definite_ctx/ss, 说明该银行相关报道里的确定性措辞更多分布在与银行金科话题不直接相关的段落 (例如企业背景介绍、行业综述), 而非聚焦于银行本身的具体金科动态描述, 这一方向性差异本身是三轨并排设计要捕捉的信息增量之一。

## VAR: mean_frac_definite_ctx

【变体差分】
本列基于 content_ctx (标题 + 银行实体窗口文本) 做确定性词元扫描后聚合, 与 full 轨在词典判据、聚合公式、权重口径上完全一致, 唯一差异是输入文本的截取范围更窄——只保留银行实体出现位置附近的窗口文本, 剔除与目标银行无直接关联的段落。这意味着 ctx 轨的分母 n_tokens_clarity_base_ctx_i 系统性小于 full 轨对应值 (窗口文本通常比全文短 50%–80%, 论文披露口径详见家族姊妹变量 mean_clarity_score_ctx 的 notes), 因此同一篇文章的 frac_definite_ctx 与 frac_definite_full 数值不可直接相减或相除做"窗口化损失了多少确定性语言"的解读, 只能在各自轨内部做银行间/年度间的横向比较。ctx 轨与 full 轨互为稳健性并排关系, 用于验证"确定性语言是否集中出现在紧邻银行提及处"——若两轨方向高度一致, 说明报道的整体措辞风格与聚焦银行段落的措辞风格趋同; 若出现系统性偏离, 则提示记者可能在描述银行主体时刻意采用与全文基调不同的措辞策略, 这本身构成一个值得单独探讨的现象, 但已超出本列 codebook 范畴。ctx 轨清晰度扫描留篇行宇宙同样锚定 full-only 门控 (只取 llm_verified_full 为真的文章子集), 不单独放宽或收紧样本口径。

## VAR: mean_frac_definite_ss

【变体差分】
本列基于 content_ss (标题 + 银行与金科词同句±1句窗口, 半径见 config/filtering.yaml::context_window.ss_sentence_radius) 做确定性词元扫描后聚合, 是三轨中文本覆盖面最窄、聚焦度最高的一轨, 判据原语与 stage 13 共现硬过滤同源但严格程度不同 (ss 要求银行与金科词严格同句, 而 stage 13 硬过滤口径是 ±1 句窗口)。当某文章内不存在银行∧金科同句共现时, 该文章的 content_ss 回退为全文 body 且对应 ss_is_fallback 标记为 True, 此时该文章在 ss 轨的 frac_definite_ss_i 实质上等同于该文章的 full 轨取值, 与 n_articles 共享同一套回退分母口径 (镜像 ctx 轨的回退语义, 而非独立设计)。ss 轨衡量的是"银行与金融科技被同时明确提及的那个具体语句附近, 记者的措辞有多确定", 相比 ctx 轨进一步剔除了泛泛提及银行但未直接关联金科话题的段落, 因而更贴近本项目核心构念 (银行金融科技活动的媒体语调) 的最窄聚焦口径。若某批次 parquet 缺失 clarity_*_ss 上游列 (旧版流水线产出), 该列在阶段 40 聚合时被优雅跳过, mean_frac_definite_ss 整列记为缺失而不会引发下游报错; ss 轨与 full/ctx 两轨同样各自 just-identified 并排, 三者互为稳健性、不分主次, 不得混入同一 over-identified 的 Hansen J 识别检验, 也不与词典消融梯度或政治词权重梯度交叉使用。

<!-- rendered-citations:begin -->
You, J., Zhang, B., & Zhang, L. (2018). Who captures the power of the pen?. The Review of Financial Studies, 31(1), 43-96. https://doi.org/10.1093/rfs/hhx055
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
<!-- rendered-citations:end -->
