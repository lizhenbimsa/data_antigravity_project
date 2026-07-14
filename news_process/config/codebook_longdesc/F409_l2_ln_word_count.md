---
family_id: F409
columns:
  - ln_word_count_ctx
  - ln_word_count_full
  - ln_word_count_ss
unit: 对数变换后的篇均分词计数 (无量纲, ln(1+词数))
formula: "ln_word_count{track} = ln(1 + avg_word_count{track}); avg_word_count{track} = bank-year 内 n_words_real{track} 的均值 (跳过 NaN); n_words_real{track} 为 jieba 分词后的有效词数 (剔除纯标点/空白 token)"
producer: news_process/pipeline/panel/geography.py (ln 变换) ; news_process/pipeline/panel/encode.py (avg_word_count{track} bank-year 聚合)
upstream:
  - 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
  - encode.py 文章级 n_words_real{track} → bank-year avg_word_count{track}
citations:
  - doi: 10.1016/j.jacceco.2015.09.002
    type: journal
    authors: Lang, M., & Stice-Lawrence, L.
    year: 2015
    title: "Textual analysis and international financial reporting: Large sample evidence"
    venue: Journal of Accounting and Economics
    vol: 60
    issue: 2-3
    pages_or_artno: 110-135
  - doi: 10.1007/s11142-008-9083-2
    type: journal
    authors: You, H., & Zhang, X.-J.
    year: 2009
    title: "Financial reporting complexity and investor underreaction to 10-K information"
    venue: Review of Accounting Studies
    vol: 14
    issue: 4
    pages_or_artno: 559-586
  - doi: 10.1016/j.jacceco.2008.02.003
    type: journal
    authors: Li, F.
    year: 2008
    title: "Annual report readability, current earnings, and earnings persistence"
    venue: Journal of Accounting and Economics
    vol: 45
    issue: 2-3
    pages_or_artno: 221-247
  - doi: 10.1016/j.jfineco.2022.08.004
    type: journal
    authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
    year: 2022
    title: "Count (and count-like) data in finance"
    venue: Journal of Financial Economics
    vol: 146
    issue: 2
    pages_or_artno: 529-551
new_dois: []
---

## CORE

【构念与来源】
ln_word_count 家族测度的是一篇银行金科报道在文本量维度上的信息投入规模, 口径为 bank-year 层面的对数变换篇均分词数, 即 ln(1 + bank-year 内该轨道有效 jieba 词数的均值)。构念动机来自文本分析文献中长期使用的报告长度代理变量: 文本篇幅越长, 通常意味着披露者或撰稿人投入了更多信息生产成本, 读者需要投入更多处理成本才能消化, 也因此常被作为信息处理成本 (disclosure processing cost) 或可读性的反向代理 (Li 2008; Lang & Stice-Lawrence 2015)。ln_word_count 属于本项目"文章长度三口径并存"体系中的词口径: 与字符口径 avg_article_length (ln(1+平均字符数), 未剔除数字/标点/拉丁字符) 和汉字口径 ln_han_count (ln(1+平均 CJK 汉字数), 剔除非汉字符号且不依赖分词) 互为长度稳健性度量, 三者刻意并存、互不替代, 共同覆盖分词切分误差、符号噪声、字符-词汉字换算比例不稳定等不同来源的测量偏误。

【方法学与计算】
计算链路分两层。文章级 (encode.py 上游更早阶段) 先对 content_full / content_ctx / content_ss 三种文本轨道各自跑 jieba 分词, 得到有效词数列 n_words_real{track} (剔除纯标点、空白等非语义 token, 与 hard_char_ratio/rare_word_ratio 等复杂度族测度共享同一分词切分口径, 减少跨测度分词不一致造成的伪差异)。encode.py 的 bank-year 聚合段 (H2 段, 词汇/句法复杂度测度族的一部分) 对 n_words_real{track} 取 mean (自动跳过 NaN, 短文本或空文本不污染均值), 得到中间列 avg_word_count{track}。geography.py 再对 avg_word_count{track} 做 log1p 变换, 即 ln(1 + avg_word_count{track}), 产出本家族三列 ln_word_count_full / ln_word_count_ctx / ln_word_count_ss。log1p 而非裸 ln 的选择是标准的计数变量零值稳健处理 (Cohn, Liu & Wardlaw 2022 系统讨论了金融实证中计数及类计数变量的建模陷阱, 包括零膨胀、偏态尾部与对数变换选择), 避免罕见的零词数样本导致 ln(0) 未定义或极端离群值主导回归。需要特别澄清的是"mean-of-ln vs ln-of-mean"两种非等价聚合顺序: ln_word_count 采用的是 ln-of-mean (先算 bank-year 篇均词数, 再取对数), 这与家族 F 中另一支 avg_redund_log_length{track} (mean-of-ln, 先对文章级词数取对数、再在 bank-year 内取均值, 服务于 redundancy 回归的配对长度控制) 是两个刻意并存、不互相替代的口径, 二者数值上不等价 (Jensen 不等式意义上 ln-of-mean ≥ mean-of-ln), 不应混用或误当作同一变量的重复列。

【文献定位】
文本长度作为信息处理成本或披露复杂度代理, 在会计与金融文本分析文献中有深厚谱系。Li (2008) 首次系统论证年报可读性 (以 Fog Index 和篇幅为核心成分) 与盈余持续性负相关, 是本家族最直接的方法学母锚; Lang & Stice-Lawrence (2015) 在跨国大样本年报文本分析中同样把文本量度量 (含词数) 作为披露详尽度与可比性研究的基础控制变量, 印证了篇幅代理在跨制度环境下依然稳健适用; You & Zhang (2009) 从财务报告复杂度导致投资者反应不足的角度, 为"文本量-信息处理成本-市场反应滞后"这一因果链条提供了理论支撑, 呼应本项目 rare_word_ratio 等复杂度族测度共享的母锚文献; Cohn, Liu & Wardlaw (2022) 则从计量方法论角度提醒研究者计数及类计数变量 (词数即是典型的类计数变量) 在对数变换、零值处理和函数形式选择上的常见陷阱, 为本家族选择 log1p 而非裸对数或线性词数提供了直接的方法学依据。三轨并列的设计延续本项目"三轨禁混同一 over-identified Hansen J、各自 just-identified 并排、互为稳健性不分主次"的一贯纪律 (CLAUDE.md 铁律), full/ctx/ss 三条 ln_word_count 序列在下游回归中应分别作为独立右手边控制变量或稳健性检验轨道使用, 不得同时纳入同一识别方程充当过度识别工具。

## VAR: ln_word_count_full

【变体差分】
ln_word_count_full 是本家族的 canonical 主轨, 底层文本为 content_full, 即标题 prepend 全文正文 (14_materialize_ctx 阶段物化, prepend_title 拼接方式, 原始"内容"列本身不做改动)。该轨覆盖一篇报道的完整正文信息量, 不做任何实体窗口或共现句裁剪, 因此在三轨中通常取值最大、方差也最大, 是文本长度测度里信息覆盖面最完整的版本。按本项目 2026-06-29 起生效的"留篇门控 = full-only"铁律, 一篇报道是否被判定为"一篇银行金科报道"只看 llm_verified_full == True, 这意味着 full 轨对应的行宇宙是三轨中唯一承担留篇判定职能的口径, ctx/ss 两轨的行宇宙是 full 留篇集合的子集 (conditional-on-full 测度/稳健性轨), 但三条 ln_word_count 序列各自在自己的样本内独立计算均值再对数化, 并不互相借用彼此的分母或缺失填补。ln_word_count_full 因此既是本家族的默认/首选长度控制变量 (在多数下游 paper 模板中作为篇幅控制项优先纳入), 也是与字符口径 avg_article_length 和汉字口径 ln_han_count 做交叉验证时的锚点轨道 — 三者理论上应高度相关 (同一篇文章不同粒度的长度量度), 若相关性显著偏离预期, 通常提示分词异常或标题重复拼接等数据管线问题。使用该列时应注意: 它反映的是一段 bank-year 内该银行相关报道的平均篇幅, 而非总篇幅或总信息量, 篇均口径隐含着对报道频次 (n_articles) 的归一化, 因此不能替代衡量媒体关注度的 attention/frac 类测度, 两者在回归设计上是互补而非替代关系, 应根据研究问题分别选用篇幅密度还是覆盖广度作为解释变量。

## VAR: ln_word_count_ctx

【变体差分】
ln_word_count_ctx 使用 content_ctx 作为底层文本, 即标题 prepend 实体窗口文本 (围绕目标银行/金科实体截取的上下文窗口, 而非全文), 在 14_materialize_ctx 阶段与 content_full、content_ss 同批物化。与 canonical 的 ln_word_count_full 相比, ctx 轨的核心差分在于文本裁剪范围: 它只保留与目标实体相关的局部语境, 剔除了报道中与银行金科议题无直接关联的段落 (例如同一篇综合性财经报道中涉及其他公司或宏观背景的部分), 因此 ctx 轨的篇均词数系统性地小于或等于 full 轨的篇均词数, 度量的是"围绕实体的信息密度"而非"整篇报道的信息总量"。当上游未能定位到有效实体窗口时 (罕见的缺列/回退情形), 该文章在 ctx 轨的贡献会被优雅跳过而非以 0 填补, geography.py 中对应的 if 'avg_word_count_ctx' in panel.columns 守卫保证了缺列情形不会导致管线崩溃, 但也意味着 ctx 轨在样本覆盖上可能略窄于 full 轨。按照本项目"留篇门控 = full-only"的口径, ctx 轨的行宇宙是 full 轨留篇集合的子集, 属于 conditional-on-full 的稳健性测度, 不承担独立的样本纳入判定职能。在解释与使用上, ln_word_count_ctx 与 ln_word_count_full、ln_word_count_ss 三者各自 just-identified 并排, 互为稳健性检验、不分主次, 在同一识别方程 (尤其是 Hansen J 过度识别检验场景) 中禁止把三轨同时作为多重工具混入同一方程; 研究者若关心的是"围绕银行-金科议题本身的文本详尽程度"而非整篇报道的总篇幅, ctx 轨是比 full 轨更贴合构念的选择, 尤其适合在稳健性附录中与 canonical 结果并列报告, 以排除全文篇幅被无关段落 (如企业其他业务线新闻) 稀释或放大的担忧。

## VAR: ln_word_count_ss

【变体差分】
ln_word_count_ss 使用 content_ss 作为底层文本, 即标题 prepend 银行与金科关键词同句 (±N 窗口, 默认 N=1, 由 config/filtering.yaml::context_window.ss_sentence_radius 控制) 共现片段, 是三轨中裁剪最严格、构念聚焦最窄的一支, 判定原语与 stage 13 硬过滤所用的 has_bank_fintech_cooccurrence_within_radius 不同, ss 轨走的是严格同句共现抽取 (extract_bank_fintech_cooccurrence), 两个判据口径刻意不互相复用。ss_is_fallback 回退语义严格镜像 ctx 轨: 当一篇报道中银行实体与金科关键词不存在同句 (或半径窗口内) 共现时, content_ss 会回退为整篇正文 body 而非置空, 对应的 ss_is_fallback 标记置 True, 该回退样本与非回退样本共享同一个 n_articles 分母, 不会造成样本量的隐性缩水; 若 FINTECH_AC 词典未加载 (None), 则 *_is_fallback 全部置 True, 实现优雅降级而非硬性报错。avg_word_count_ss 在 encode.py H2 段与 full/ctx 两轨用完全相同的 mean 聚合逻辑计算, geography.py 再套用相同的 log1p 变换产出 ln_word_count_ss, 计算链路与另外两轨完全对称, 唯一差异在于底层文本裁剪半径不同。由于同句共现的裁剪范围通常比实体窗口 (ctx) 更窄, ln_word_count_ss 在多数情形下呈现三轨中最小的篇均词数与最集中的取值分布, 度量的是"银行与金科议题直接并置出现的那一小段文本"的信息量, 适合用作最保守 (最少受到无关上下文污染) 的长度控制稳健性检验。与 ctx 轨相同, ss 轨的行宇宙同样是 full 轨留篇集合的子集 (conditional-on-full), 且与 full、ctx 两轨各自 just-identified 并排、互为稳健性不分主次, 三者绝不应同时混入同一个过度识别的 Hansen J 检验方程中作为多重工具变量或多重控制同时使用, 而应作为彼此独立的稳健性附录轨分别报告回归系数, 用以证明主结论不依赖于某一种特定的文本裁剪口径。

<!-- rendered-citations:begin -->
Lang, M., & Stice-Lawrence, L. (2015). Textual analysis and international financial reporting: Large sample evidence. Journal of Accounting and Economics, 60(2-3), 110-135. https://doi.org/10.1016/j.jacceco.2015.09.002
You, H., & Zhang, X.-J. (2009). Financial reporting complexity and investor underreaction to 10-K information. Review of Accounting Studies, 14(4), 559-586. https://doi.org/10.1007/s11142-008-9083-2
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
<!-- rendered-citations:end -->
