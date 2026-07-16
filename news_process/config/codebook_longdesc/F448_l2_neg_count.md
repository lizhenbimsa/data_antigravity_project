---
family_id: F448
columns:
- neg_count_ctx
- neg_count_full
- neg_count_ss
- neg_count_vw_ctx
- neg_count_vw_full
- neg_count_vw_ss
unit: 篇数/加权篇数 (count; _vw 变体为 mention_density 加权计数, 量纲不再是整数篇数)
formula: 'neg_count{track} = Σ_{i∈bank-year} 1(llm_vote_score_i{track} == -1); neg_count_vw{track} = Σ_{i∈bank-year} 1(llm_vote_score_i{track} == -1) × mention_density_i{track}, mention_density_i = 该银行在文章 i 中被提及次数 / 文章总字数'
producer: pipeline\panel\encode.py (build_aggregation_dict, agg[f''neg_count{track}''] / agg[f''neg_count_vw{track}'']) ; pipeline\panel\runner.py (步骤 3b 提及密度加权列预计算, weighted_cols[f''is_negative_w{track}'']) ; pipeline\filtering\news_bank.py (mention_density 物化)
upstream: [21_tone_llms.parquet, 14_news_with_ctx.parquet, 11_news_bank.parquet]
citations:
- doi: 10.1016/j.jfineco.2022.08.004
  type: journal
  authors: Cohn, J. B., Liu, Z., & Wardlaw, M. I.
  year: 2022
  title: Count (and count-like) data in finance
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 529-551
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: 'Political incentives to suppress negative information: Evidence from Chinese listed firms'
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: 'Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions'
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: '31'
  issue: '1'
  pages_or_artno: e1549
new_dois: []
---

## CORE

【构念与来源】
本家族衡量 bank-year 面板中"三家 LLM 多数投票判定为负面语调"的文章篇数, 是 F1 主线 (`bank_fintech_tone`) 情感构念在计数尺度上的伴生测度, 与均值尺度的 `llm_vote_tone{track}` 互补: 均值刻画整体语调水平, 计数刻画负面报道的绝对暴露量。构念谱系上溯 Tetlock (2007, *Journal of Finance*) 与 Tetlock, Saar-Tsechansky & Macskassy (2008, *Journal of Finance*) 建立的"文本负面词/负面文章计数作为投资者关注与市场反应的代理变量"范式——原始 Tetlock 范式基于词典法逐词计数, 本项目在保留该"计数即暴露量"直觉的同时, 把负面判定的原语从词典命中改为三家 LLM (`gpt-5.4-nano`/`gemini-3.1-flash-lite`/`deepseek-v4-flash`) 多数投票的离散标签, 因此本家族的负面判定与词典法词频计数族 (如 `l2_bian_2021_neg_count` 等) 是两条独立的方法学谱系, 共享"计数"这一聚合形式但不共享判定原语, 不可互相替代或混用作同一构念的两种测量。

篇章级源头是 `llm_vote_score{track} ∈ {-1, 0, 1}` (stage 21 三家多数投票共识分数, `tone_llms.py`), 本家族仅取该分数等于 -1 的行数指示 `is_negative{track} = 1(llm_vote_score{track} == -1)` (`encode.py::encode_sentiment`, L289-290), 在 bank-year 层用 `groupby(...).sum()` 对该 0/1 指示求和 (`build_aggregation_dict`, L758)。因此 `neg_count{track}` 与同族 `pos_count{track}`/`pos_frac{track}`/`neg_frac{track}` 共享同一篇章级源列 `llm_vote_score{track}`, 仅聚合算子 (sum vs mean) 与目标标签 (+1 vs -1) 不同——四者构成一组完全对偶的计数/占比矩阵, 不应把 `neg_count` 与 `neg_frac` 当作独立构念解读回归系数, 二者只是同一底层判定的不同标准化 (绝对数 vs 相对占比, 后者以留篇门控后的 `n_articles` 为隐式分母)。

【方法学与计算】
`neg_count{track}` 是留篇门控下的条件计数: 分子只对 `llm_vote_score{track}` 非缺失 (即该篇文章在该轨道下被三家 LLM 有效评分) 的行计数, 未通过留篇门控 (`llm_verified_full != True`, 2026-06-29 起 full-only 门控) 的文章不贡献分子。本项目 2026-06-29 起把"是否判为一篇银行金科报道"的留篇门控收紧为 full-only——门控只看 `llm_verified_full`, ctx/ss 两轨降级为 full 留篇集合之上的 conditional-on-full 测度/稳健性轨, 即 `neg_count_ctx`/`neg_count_ss` 的行宇宙是 `neg_count_full` 留篇集的子集, 逐轨各自独立计数 (非借用 full 轨分母)。这一口径变更是刻意设计而非缺陷: full 轨承担唯一的"是否算作一篇有效报道"判定权, ctx/ss 轨只在 full 轨已确认的样本上补充测量精细度, 避免三轨各自定义留篇标准导致的样本口径漂移。

`neg_count_vw{track}` 是 value-weighted 稳健性变体 (Hassan et al., 2019, *Quarterly Journal of Economics* 风格的提及密度加权暴露量), 计算路径是: 先在篇章级把 0/1 负面指示乘以该银行在该文章中的 mention_density 权重 (`runner.py` 步骤 3b, L761: `weighted_cols[f'is_negative_w{track}'] = df[f'is_negative{track}'] * w`, 其中 `w = df['mention_density'].fillna(0)`), 再在 bank-year 层求和 (`encode.py` L996: `agg[f'neg_count_vw{track}'] = (f'is_negative_w{track}', 'sum')`)。mention_density 本身在 stage 11 (`news_bank.py`) 物化, 定义为"该银行在文章中被提及次数 / 文章总字数" (L283, L289), 刻画银行在该篇报道中的"文本份额"或曝光强度——同一篇报道里若目标银行被反复提及、篇幅占比更高, 则该篇对 `neg_count_vw` 的贡献大于仅被提及一两次的边缘报道。因此 `neg_count_vw{track}` 已不再是整数意义上的"篇数", 而是一个连续的加权暴露量, dtype 为 double (相对 `neg_count{track}` 的 int64), 单位退化为"加权篇数当量", 不可直接与 `neg_count{track}` 做算术比较或相除得到有意义的比率——二者是并排的稳健性轨而非同一量纲的原始值与加权值配对使用。

三轨 (full/ctx/ss) 与 vw/非-vw 两个加权维度正交组合, 构成本家族全部 6 列: `{neg_count, neg_count_vw} × {full, ctx, ss}`。full=标题+正文全文; ctx=标题+目标银行实体上下文窗口; ss=标题+银行∧金科词同句 (±N 句窗, 默认 N=1) 共现文本, 无共现时回退为全文 body 且 `ss_is_fallback=True` (镜像 ctx 回退语义, 共享 `n_articles` 分母口径)。铁律: 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁止把 full/ctx/ss 三轨的 `neg_count` 混进同一 over-identified Hansen J 设定; vw 与非-vw 两个加权维度同理并排, 不构成一个可加分解的"总量-权重"层级关系。

【文献定位】
计数型文本情感测度的方法学基础是 Tetlock, Saar-Tsechansky & Macskassy (2008, *Journal of Finance*) 与 Loughran & McDonald (2011, *Journal of Finance*) 建立的词典/文章计数范式, 本家族继承其"负面文章绝对数量作为舆论压力代理变量"的构念定位, 但把判定原语替换为 LLM 多数投票。计数数据在计量上的特殊性质 (非负整数、右偏、易零膨胀) 及其对回归设定的要求, 参照 Cohn, Liu & Wardlaw (2022, *Journal of Financial Economics*) 对 count-like 金融数据的系统性讨论——该文提醒研究者在 `neg_count{track}` 这类右偏计数变量上直接用 OLS 可能产生偏误, 建议配合对数变换 (参见家族外的 `_gated_log_sent` 衍生指标) 或计数模型 (Poisson/负二项) 作稳健性检验。中国情境下负面信息本身的可观测性存在系统性抑制, Piotroski, Wong & Zhang (2015, *Journal of Accounting Research*) 发现地方国企出于政治激励会压制负面信息的对外披露与传播——这提示本家族的负面文章计数在跨所有制、跨地区比较时须警惕"负面报道计数偏低"未必等于"真实经营负面事件更少", 而可能部分反映了信息渠道的政治性抑制, 是解读 `neg_count{track}` 系数时应披露的构念局限。提及密度加权 (`_vw` 变体) 的一般性方法学定位可参照 Todd, Bowden & Moshfeghi (2024, *Intelligent Systems in Accounting, Finance and Management*) 对金融文本情感分析文献的系统性综述, 该文梳理了从简单计数到强度/份额加权的测量演进脉络, 本项目的 mention_density 加权 (银行在文章中的文本份额) 属于这一"从二元命中到连续暴露强度"演进路径在中文银行新闻场景的具体实现, 用以区分银行作为报道主角与作为边缘提及对象时的不同舆论暴露程度。

## VAR: neg_count_ctx

【变体差分】
本列取 ctx 轨 (标题+目标银行实体上下文窗口文本) 的 `llm_vote_score_ctx == -1` 指示在 bank-year 层求和, 非加权 (无 mention_density 权重), dtype int64。行宇宙是 full 轨留篇门控 (`llm_verified_full == True`) 之上的条件子集: 只有通过 full 轨留篇判定的文章, 其 ctx 轨的负面计数才计入本列; ctx 轨自身的评分有效性 (`llm_vote_score_ctx` 非缺失) 是在此子集内再判定的, 不构成独立的留篇标准。相对 canonical `neg_count_full`, 本列是"聚焦实体上下文窗口而非全文"的稳健性并排轨, 用于检验负面语调计数是否对全文中与目标银行无关的段落 (可能引入的噪声) 敏感; 二者互为稳健性, 不设主次, 禁止混入同一 over-identified 设定。

ctx 轨的实体上下文窗口在 stage 14 (`ctx_materializer`) 物化为 `content_ctx`, 抓取标题及目标银行实体周边的局部文本, 相比全文更贴近"银行本身在被如何评价"这一狭义构念, 但也因窗口截断而可能丢失全文层面才能判断出的转折句、总括句语境, 因此负面判定在 ctx 轨上偶尔会与 full 轨方向不一致——这类不一致本身是可解读的信号 (窗口内局部负面而全篇整体基调正面, 反之亦然), 而非测量误差, 论文引用时应把 `neg_count_ctx` 与 `neg_count_full` 的差异作为局部关注度与整体基调分离度的一种诊断, 不宜简单认为二者应当高度一致。本列与同轨 `neg_count_vw_ctx` 构成加权/非加权配对, 与 `neg_count_ss` 构成窗口宽严配对, 三者共同覆盖从全文到实体窗口再到句级共现的语境收紧梯度。

## VAR: neg_count_full

【变体差分】
本列是本家族的 canonical/主轨: 取 full 轨 (标题+正文全文) 的 `llm_vote_score_full == -1` 指示在 bank-year 层求和, 非加权, dtype int64。留篇门控直接作用于本轨 (`llm_verified_full == True` 即为分子/分母的行宇宙判定标准, 2026-06-29 起 full-only 铁律), 是 ctx/ss 两轨的行宇宙上界——ctx/ss 轨的样本量恒 ≤ 本列。P1 主线 `bank_fintech_tone` 的处理变量 `llm_vote_tone_full` 与本列共享同一篇章级源列 `llm_vote_score_full`, 但聚合算子不同 (mean vs sum); 本列在实证中通常作为负面舆论绝对暴露量的描述性/稳健性变量, 而非直接处理变量。

作为唯一直接承担留篇门控判定权的轨道, 本列的分母 (即该 bank-year 内被判定为有效银行金科报道的篇数 `n_articles`) 与 `neg_frac_full`/`pos_count_full` 等同族列共享同一行宇宙, 三者构成内部一致的核算体系: `neg_count_full + pos_count_full` 加上中性篇数应等于该 bank-year 已验证篇数总和 (留篇门控通过且 `llm_vote_score_full` 非缺失)。研究者在描述性统计表中报告 `neg_count_full` 时, 建议同时报告 `n_articles` 以避免读者把绝对计数误读为占比; 银行规模 (报道总量) 差异会直接放大或缩小本列数值, 跨行比较绝对计数前应先用 `neg_frac_full` 或对数变换控制报道总量差异。

本列亦是 ctx/ss 两轨、以及全部 3 个 vw 加权变体的行宇宙锚点: 任何下游轨道若要在 full-only 留篇门控之外扩展样本, 都必须先经本列判定的留篇集合过滤, 这一"唯 full 轨定夺留篇"的架构设计是 2026-06-29 起的现行铁律, 取代了此前三轨各自独立判定留篇的旧口径; 复现或审计本家族任何一列的样本量时, 均应以本列的非缺失行数作为交叉核验的基准。

## VAR: neg_count_ss

【变体差分】
本列取 ss 轨 (标题+银行∧金科词同句共现窗口文本, 默认 ±1 句半径) 的 `llm_vote_score_ss == -1` 指示在 bank-year 层求和, 非加权, dtype int64。行宇宙同样是 full 轨留篇门控之上的条件子集。ss 回退语义镜像 ctx: 若某篇文章不存在银行∧金科词同句共现, `content_ss` 回退为全文 body, 对应篇章级 `ss_is_fallback=True`, 该情形下 ss 轨的负面判定实质上退化为 full 轨判定的重复 (而非独立测量), 解读本列的 bank-year 均值时应结合 `frac_ss_fallback` 判断该行是否以退化观测为主。本列是三轨中最"聚焦"的一支, 用于检验负面语调计数是否需要银行与金科议题在句子层面严格共现才成立, 与 ctx/full 两轨互为稳健性并排, 不分主次。

ss 轨的共现判据来自 `entity_context.extract_bank_fintech_cooccurrence` (与 stage 13 硬过滤所用的 `has_bank_fintech_cooccurrence_within_radius` 是不同判据原语, 禁止互相复用), 要求银行词与金科词在同一句内出现方视为真共现; 该判据比 ctx 轨的实体窗口更严格, 因此本列的真实 (非回退) 观测数通常显著少于 `neg_count_ctx` 的有效样本。当一个 bank-year 内 `frac_ss_fallback` 接近 1 (几乎所有文章都不存在同句共现) 时, `neg_count_ss` 应与 `neg_count_full` 在数值上高度接近甚至相等, 此时本列不再提供额外的识别信息, 是数据稀疏导致的预期退化而非缺陷; 在 T=2 的本机开发样本上这一退化尤为常见, 生产 T=19 全量语料上真实同句共现观测量预期显著提升。

## VAR: neg_count_vw_ctx

【变体差分】
本列是 `neg_count_ctx` 的提及密度加权 (value-weighted) 版本: 篇章级先算 `is_negative_ctx × mention_density`, 再在 bank-year 层求和, dtype double (非整数篇数)。行宇宙与 `neg_count_ctx` 相同 (full 轨留篇门控之上的条件子集), 加权维度与轨道维度正交——本列同时承载"实体上下文窗口"与"提及密度加权"两重差分, 用于检验 ctx 轨负面语调暴露量的结论是否对报道中银行提及的文本份额敏感 (即区分银行作为报道主角与边缘提及对象)。与非加权的 `neg_count_ctx`、以及其余两轨的 vw 变体互为稳健性并排, 不设主次, 不可相除构造出有意义的"加权率"。

权重 mention_density 在 stage 11 (`news_bank.py`) 按"该银行在文章中被提及次数 / 文章总字数"计算, 与 ctx 轨的实体窗口截取逻辑相互独立——mention_density 度量的是全文层面的提及份额, 而 ctx 轨截取的是围绕这些提及位置的局部文本窗口, 二者共同刻画银行在报道中的可见度: 前者是量的维度 (被提及多频繁), 后者是质的维度 (提及处周边说了什么)。当一篇文章中目标银行被高频提及且该窗口内语调判定为负面时, 本列相对 `neg_count_ctx` 会赋予更大权重, 从而更贴近"银行作为报道主角承受的负面舆论压力", 而非把边缘提及的负面报道等同看待。

## VAR: neg_count_vw_full

【变体差分】
本列是 canonical `neg_count_full` 的提及密度加权版本: 篇章级 `is_negative_full × mention_density` 在 bank-year 层求和, dtype double。留篇门控直接作用于本轨 (与 `neg_count_full` 相同的行宇宙判定标准)。在 vw 维度内, 本列是三轨加权变体中的主轨/canonical 起点, 用于检验 `neg_count_full` 揭示的负面暴露量结论是否受"银行在文章中的提及份额"这一强度维度驱动——若加权后与非加权结论方向一致, 说明负面计数效应不只是由边缘提及的报道贡献, 而是与银行作为报道主角的密度相关。

本列与 `neg_count_full` 的关系刻意设计为并排的稳健性对, 而非"原始值-加权修正值"的层级关系: 二者共享同一份 0/1 负面指示与同一留篇门控行宇宙, 唯一差异是求和前是否乘以 mention_density 权重。研究者若在同一回归中同时纳入两列作为自变量, 须注意二者高度共线 (均由同一底层负面判定驱动), 应视为互相替代的稳健性设定分别汇报, 而非同一模型内的独立解释变量; 与 `neg_count_vw_ctx`/`neg_count_vw_ss` 一样, 本列同属提及密度加权稳健性梯子的一环, 三者 just-identified 并排, 不构成 over-identified 联合估计的合法输入集。

本列的 double 精度小数值域也意味着它天然不适合直接套用面向整数计数设计的 Poisson/负二项模型, 若研究设计需要计数模型稳健性检验, 应改用非加权的 `neg_count_full` 而非本列; 本列更适合与 `llm_vote_tone_full`/`neg_frac_full` 等连续型情感测度并列, 作为暴露强度加权后的负面舆论压力代理变量纳入线性设定。

## VAR: neg_count_vw_ss

【变体差分】
本列是 `neg_count_ss` 的提及密度加权版本: 篇章级 `is_negative_ss × mention_density` 在 bank-year 层求和, dtype double。行宇宙与 `neg_count_ss` 相同 (full 轨留篇门控之上的条件子集), 且继承 ss 轨的回退语义——`ss_is_fallback=True` 的文章其 `content_ss` 已退化为全文 body, mention_density 权重此时反映的是"银行在全文中的提及份额"而非"银行在同句窗口中的提及份额", 解读需结合 `frac_ss_fallback` 判断权重来源是否退化。本列是全家族加权维度最聚焦的一支, 同时叠加"同句共现"与"提及密度加权"两重严格化, 与其余五列互为稳健性并排, 不分主次, 禁止混入同一 over-identified Hansen J 设定。

需注意 mention_density 权重本身与 ss 轨的同句共现判据来自完全不同的计算路径 (前者是全文层面的字数/次数比, 后者是句子层面的实体共现判断), 权重不随 `ss_is_fallback` 状态改变——即无论该篇文章是否触发同句共现回退, mention_density 权重恒以全文为分母计算并原样乘入。因此本列的数值波动同时受三个独立来源驱动: 同句共现判定是否触发回退、语调判定是否为负面、以及银行在全文中的提及密度, 解读回归系数时应结合 `frac_ss_fallback` 与 `n_articles` 分别披露, 避免把三者混同为单一构念的单调变化。

<!-- rendered-citations:begin -->
Cohn, J. B., Liu, Z., & Wardlaw, M. I. (2022). Count (and count-like) data in finance. Journal of Financial Economics, 146(2), 529-551. https://doi.org/10.1016/j.jfineco.2022.08.004
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
