---
family_id: F024
columns:
- avg_adversative_ctx
- avg_adversative_full
- avg_adversative_ss
unit: 无量纲比率 (逆接/转折连词 token 占比的银行-年度均值, 取值域 [0, 1])
formula: "avg_adversative_track = mean_over_articles( n_adversative_tokens / n_word_tokens ), track ∈ {full, ctx, ss}; 分子 = 命中独立转折连词表 _ADVERSATIVE_WORDS 的分词单元计数, 分母 = 该轨文本经独立未注入 jieba Tokenizer 切出的有效词 token 数"
producer: news_process/pipeline/sentiment/lexical_complexity.py (逆接连词计数原语 + 独立 Tokenizer, 逐篇产 adversative_ratio{track}) ; news_process/pipeline/sentiment/tone_words.py::stage22 (三轨逐篇调度, 不做银行-年聚合) ; news_process/pipeline/panel/encode.py (stage 40 panel export, 银行-年 mean 聚合 avg_adversative{track} = mean_over_articles(adversative_ratio{track}))
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss + *_is_fallback)
- 21_tone_llms.parquet (full-only 留篇门控)
- 22_tone_words.parquet
citations:
- doi: 10.1016/j.pacfin.2023.102074
  type: journal
  authors: Li, F., Yang, M., & Zhang, T.
  year: 2023
  title: "Does prospectus readability matter for bond issuance pricing? Evidence from China"
  venue: Pacific-Basin Finance Journal
  vol: 80
  pages_or_artno: "102074"
- doi: 10.1111/1911-3846.12825
  type: journal
  authors: Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W.
  year: 2023
  title: "Textual analysis in accounting: What's next?"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 765-805
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: "Text as data"
  venue: Journal of Economic Literature
  vol: 57
  issue: 3
  pages_or_artno: 535-574
- doi: 10.1016/j.jacceco.2017.03.002
  type: journal
  authors: Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K.
  year: 2017
  title: "A plain English measure of financial reporting readability"
  venue: Journal of Accounting and Economics
  vol: 63
  issue: 2-3
  pages_or_artno: 329-357
- doi: 10.1007/s11142-016-9371-1
  type: journal
  authors: Hope, O.-K., Hu, D., & Lu, H.
  year: 2016
  title: "The benefits of specific risk-factor disclosures"
  venue: Review of Accounting Studies
  vol: 21
  issue: 4
  pages_or_artno: 1005-1045
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1111/jofi.12162
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2014
  title: "Measuring readability in financial disclosures"
  venue: The Journal of Finance
  vol: 69
  issue: 4
  pages_or_artno: 1643-1671
- doi: 10.1016/j.jacceco.2008.02.003
  type: journal
  authors: Li, F.
  year: 2008
  title: "Annual report readability, current earnings, and earnings persistence"
  venue: Journal of Accounting and Economics
  vol: 45
  issue: 2-3
  pages_or_artno: 221-247
new_dois: []
---

## CORE

【构念与来源】
本家族三列 avg_adversative_full / avg_adversative_ctx / avg_adversative_ss 测度的是一篇银行金融科技报道在语篇层面的逆接密度, 即文本中逆接连词 (转折、让步、反预期连接词) 所占的分词比例, 再在银行-年层面对留篇集合内各篇文章取均值。构念上它捕捉的是新闻叙事的两面性与修辞复杂度: 当一篇报道频繁使用但、然而、却、尽管、虽然、反而、相反、即便、纵然、哪怕等逆接标记时, 通常意味着作者在正反两种评价之间来回权衡, 或先扬后抑地引入对立立场, 从而使文本呈现出更强的对冲语气与更低的单向确定性。逆接密度高的银行报道往往并非纯粹的褒或贬, 而是把利好与风险并置, 这与金融文本分析中长期关注的模糊性、可读性、语气两面性属于同一构念族。该测度定位为一条透明、可解释、确定性可复现的语篇结构控制变量与稳健性信号, 与词典情感分、LLM 语气分互为旁证而非替代。

【方法学与计算】
计算原语落在 pipeline/sentiment/lexical_complexity.py。分子 = 逐 token 匹配一张独立的逆接连词冻结词表 _ADVERSATIVE_WORDS (含但、但是、然而、却、可是、不过、尽管、虽然、虽、反而、相反、只是、反倒、岂料、殊不知、竟然、不料、尽管如此、话虽如此、即便、即使、纵然、哪怕) 的命中计数; 分母 = 同一轨文本切出的有效词 token 数。三轨的原始文本在 stage 14 ctx_materializer 物化 (content_full = 标题 prepend + 全文正文; content_ctx = 标题 + 银行实体上下文窗口; content_ss = 标题 + 银行与金融科技同句共现窗口), stage 22 tone_words 逐篇对三轨分别调度计数原语, 产出逐篇文章级 adversative_ratio{track} 三列; tone_words 本身只做逐篇调度、不含任何 groupby 或银行-年聚合逻辑。银行-年层面的 avg 前缀均值列 avg_adversative{track} 由下游 stage 40 panel export (pipeline/panel/encode.py) 以 mean_over_articles(adversative_ratio{track}) 在留篇集合内 groupby 聚合产出, 这是文章级测度与面板列的职责分界。一个关键工程铁律是: 本模块的分词、词性、词频一律走一个从不暴露注入入口的私有未注入 jieba.Tokenizer 单例, 而不读全局 jieba.dt。原因是任何模块的 add_word 都会改写全局分词器的 FREQ 表并把领域词以 x 词性回退当标点剔出分母, 使同一文本在注入前后给出两套值、破坏确定性; 私有 Tokenizer 与 tone_words 情感轨各自持有独立分词器, 两端隔离后即便全局 jieba 被第三方污染也不影响本族取值。整条链路纯 CPU、无 LLM、无网络、零成本, 确定性仅来自 jieba==0.42.1 版本冻结与词表文件, 无缓存锚点。另一处刻意设计是: 本逆接词表独立维护, 刻意不复用 config/sentiment.yaml 中驱动情感转折 boost 的 adversative_words 表 — 复用会让本右手侧结构变量与情感轨机械同源、污染度量纯度 (缺口报告 G5 的裁决)。

【文献定位】
逆接密度承接文本可读性与文本即数据两条脉络。可读性一支上, Li (2008) 以年报文本长度与句法复杂度预测盈余持续性, 开启用语篇结构量化披露复杂度的范式; Loughran and McDonald (2014) 指出传统 Fog 指数在金融文本上失效、主张更贴合语料的可读性代理; Bonsall et al. (2017) 进一步提出 Plain English 综合度量, 把连接词与句法负担纳入复杂度评分; Li et al. (2023) 在中国债券招募说明书语境下验证中文披露可读性对发行定价的作用, 为本项目的中文语料口径提供直接同域参照。文本即数据一支上, Gentzkow, Kelly and Taddy (2019) 系统梳理了从计数特征到语义嵌入的文本量化方法学, 逆接连词占比正属其中最透明的高频结构计数特征; Loughran and McDonald (2016) 与 Bochkay et al. (2023) 两篇综述则界定了此类词典与结构计数测度在会计金融实证中的效度边界与前沿方向。就语篇具体性而言, Hope, Hu and Lu (2016) 论证了披露具体性 (specificity) 的信息价值, 与逆接密度所刻画的两面性构念相邻但正交 — 逆接标记度量的是立场对冲而非硬信息含量。逆接连词表本身的语言学锚点取自 Ding-Liu-Yu (2008) 的短语级情感分析框架与徐巍-姚振晔-陈冬华 (2021) 对副词连词占比的中文实证, 两者在正文以作者-年份形式引述, 未纳入 DOI 引文块。三条轨道 full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 检验。

## VAR: avg_adversative_full

【变体差分】
本列为家族 canonical 轨。文本口径 = content_full, 即标题 prepend 到全文正文之后的整篇报道 (原始内容列不动, 标题以第 0 句形式并入)。因此 avg_adversative_full 的分母是整篇报道的有效词 token 数, 分子是全篇命中逆接连词表的计数, 覆盖面最广、逐篇缺失最少, 是三轨中方差最稳、信息量最全的一条, 也是纳入基准回归时优先选用的语篇结构控制。留篇门控采用 full-only 口径 (2026-06-29): 一篇报道是否算作留在样本内的一篇银行金融科技报道, 仅由 llm_verified_full == True 判定; 因此本轨的行宇宙就是全部 full 留篇集合, 银行-年内 n_articles 分母与该 full 留篇计数一致, ctx 与 ss 两轨降为 conditional-on-full 的稳健性测度、其行宇宙是本 full 留篇集合的子集。本列与同族 ctx/ss 列各自 just-identified 并排、互为稳健性不分主次, 严禁三轨同入一个 over-identified 的 Hansen J 过度识别检验。作为非嵌入的纯结构计数测度, 本列无 co-primary 的 _lg 孪生列, 也不参与 co-primary 双轨嵌入的 both-or-neither 联动。就实证使用而言, 本列既可作基准模型中的语篇复杂度控制变量, 也可作以词典情感分或 LLM 语气分为处理变量时的辅助稳健性协变量: 当逆接密度显著抬升时提示该银行-年的媒体叙事更趋两面性, 从而对情感分的单向解读构成一层可解释的对冲修正。逐 token 匹配走本模块私有的未注入 jieba Tokenizer, 与情感轨领域词注入完全隔离, 保证同一篇 full 文本无论上游任何模块是否 add_word 都给出逐位可复现的取值, 这也是本列可作确定性锚点参与 golden 复现的前提。

## VAR: avg_adversative_ctx

【变体差分】
本列与 canonical 的唯一差分在文本轨道: 采用 content_ctx (标题 + 银行实体上下文窗口), 即只在围绕目标银行实体的邻近窗口内统计逆接连词与有效词, 而非整篇正文。其构念意图是把逆接密度收敛到与目标银行直接相关的叙事片段, 剔除与该银行无关的段落对语篇两面性的稀释, 度量与主体更贴近的对冲语气。因窗口更窄, 本轨分母 token 数更小, 逐篇取值方差通常大于 full 轨, 在 T 较小的开发样本上可能出现更多零值或退化格。本轨为 conditional-on-full 的稳健性轨: 行宇宙是 full 留篇集合的子集, 银行-年聚合仍逐轨自算、共享 full-only 门控确定的留篇分母, 不借用 full 轨的分子分母。avg_adversative_ctx 与 avg_adversative_full、avg_adversative_ss 各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified 的 Hansen J。本列同为非嵌入结构计数测度, 无 _lg 双轨孪生。相对 full 轨, 本轨的价值在于把逆接语气锁定在与目标银行直接相邻的叙事片段: 一篇同时报道多家银行或多条主题的长文, 其整篇 full 逆接密度可能被无关段落摊薄, 而 ctx 窗口能把这层稀释剔除, 更忠实地刻画围绕本银行的正反权衡强度。窗口边界由 ctx_materializer 在 stage 14 依银行实体位置物化, 判定采用银行侧否定加短名过滤的口径; 当窗口内有效 token 极少时本列逐篇取值波动更大, 使用者应把它读作 full 轨的收敛稳健性对照而非独立信号, 二者在合理语料下应给出方向一致、幅度相近的逆接密度估计。

## VAR: avg_adversative_ss

【变体差分】
本列采用最窄的 content_ss 文本轨 (标题 + 银行与金融科技同句共现窗口), 只在既提及目标银行又提及金融科技的同句语境 ±N 句窗口内统计逆接密度, 度量恰好落在银行金科交叉叙事上的立场对冲。回退语义严格镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 优雅回退为全文正文 body、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母; 若 FINTECH_AC 为 None 则整轨 *_is_fallback 全 True 降级。因窗口最窄, 本轨是三轨中逐篇缺失与零方差退化最常见的一条, 在开发期 T=2 小样本上尤其明显, 生产期 T=18 语料方恢复正常分布。本轨同为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集合的子集, 分子分母严格逐轨自算、不借 full。avg_adversative_ss 与 full、ctx 两列各自 just-identified 并排、互为稳健性不分主次, 严禁三轨混入同一 over-identified 的 Hansen J 过度识别检验。作为纯结构计数、非嵌入测度, 本列无 co-primary 的 _lg 孪生列。本轨的独特意义在于把逆接语气进一步聚焦到银行与金融科技真正同句交汇的语境: 唯有当报道在同一句里既谈该银行又谈金融科技时, 其逆接标记才最可能反映针对该银行金科议题本身的立场对冲 (例如先肯定其数字化投入、再转折点出风险敞口), 因而 ss 轨是三轨中构念最贴近研究主题、但样本最稀疏的一条。使用者须清楚其分母窗口最窄、回退与零方差退化最频繁, 在小样本上宜与 full/ctx 并列报告而非单独依赖; 三轨给出一致方向时, 逆接密度对结论的稳健性支撑最强, 这正是本族刻意物化三条并排轨道而非单一测度的方法论用意。

<!-- rendered-citations:begin -->
Li, F., Yang, M., & Zhang, T. (2023). Does prospectus readability matter for bond issuance pricing? Evidence from China. Pacific-Basin Finance Journal, 80, 102074. https://doi.org/10.1016/j.pacfin.2023.102074
Bochkay, K., Brown, S. V., Leone, A. J., & Tucker, J. W. (2023). Textual analysis in accounting: What's next?. Contemporary Accounting Research, 40(2), 765-805. https://doi.org/10.1111/1911-3846.12825
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Bonsall, S. B., IV, Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. Journal of Accounting and Economics, 63(2-3), 329-357. https://doi.org/10.1016/j.jacceco.2017.03.002
Hope, O.-K., Hu, D., & Lu, H. (2016). The benefits of specific risk-factor disclosures. Review of Accounting Studies, 21(4), 1005-1045. https://doi.org/10.1007/s11142-016-9371-1
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. The Journal of Finance, 69(4), 1643-1671. https://doi.org/10.1111/jofi.12162
Li, F. (2008). Annual report readability, current earnings, and earnings persistence. Journal of Accounting and Economics, 45(2-3), 221-247. https://doi.org/10.1016/j.jacceco.2008.02.003
<!-- rendered-citations:end -->
