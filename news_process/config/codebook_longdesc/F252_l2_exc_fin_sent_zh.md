---
family_id: F252
columns:
- exc_fin_sent_zh_正面_ctx
- exc_fin_sent_zh_正面_full
- exc_fin_sent_zh_正面_hw_ctx
- exc_fin_sent_zh_正面_hw_full
- exc_fin_sent_zh_正面_hw_ss
- exc_fin_sent_zh_正面_ss
- exc_fin_sent_zh_正面_w_ctx
- exc_fin_sent_zh_正面_w_full
- exc_fin_sent_zh_正面_w_ss
unit: 停刊媒体剔除后 bank-year 的 fin_sent_zh 正面概率(或加权正面概率)算术均值, 无量纲; 无权变体 ∈ [0,1], 加权变体随权重尺度平移但仍以概率为核
formula: "exc_fin_sent_zh_正面_[w|hw]_track = mean_{i ∈ alive_media(bank,year)} x_i; 其中 alive_media = 剔除隐性停刊媒体(_is_ceased_media==0)后的文章集; x_i = fin_sent_zh_正面{track}(无权) 或 fin_sent_zh_正面{track}·mention_density_i(_w, VW) 或 fin_sent_zh_正面{track}·herd_weight_track_i(_hw)"
producer: news_process/pipeline/panel/attention_media.py (停刊稳健性 C.4 动态发现块, _SCORE_PATTERNS 含 'fin_sent_zh_正面_'; 逐 alive-media groupby(['target_bank','year']).mean())
upstream:
- 23_bert_tone.parquet (fin_sent_zh_正面{track} 文章级正面概率)
- pipeline/panel/runner.py 步骤 3b/3d (mention_density VW 权重 _w、herd_weight 三轨 _hw 的文章级加权列预计算)
- pipeline/panel/attention_media.py::detect_defacto_cessation (_is_ceased_media 隐性停刊标记)
citations:
- doi: 10.1007/s00521-024-10603-6
  type: journal
  authors: Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y.
  year: 2025
  title: "Chinese fine-grained financial sentiment analysis with large language models"
  venue: Neural Computing and Applications
  vol: 37
  issue: 30
  pages_or_artno: 24883-24892
- doi: 10.1016/j.eswa.2024.125739
  type: journal
  authors: Ma, Y., Zhang, T., & Zhang, P.
  year: 2025
  title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application"
  venue: Expert Systems with Applications
  vol: 264
  pages_or_artno: 125739
- doi: 10.1002/isaf.1549
  type: journal
  authors: Todd, A., Bowden, J., & Moshfeghi, Y.
  year: 2024
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  venue: Intelligent Systems in Accounting, Finance and Management
  vol: 31
  issue: 1
  pages_or_artno: e1549
- doi: 10.1093/rfs/hhad044
  type: journal
  authors: Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A.
  year: 2023
  title: "Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1"
  venue: Review of Financial Studies
  vol: 36
  issue: 12
  pages_or_artno: 4919-4964
- doi: 10.1007/978-3-030-32381-3_16
  type: book
  authors: Sun, C., Qiu, X., Xu, Y., & Huang, X.
  year: 2019
  title: "How to fine-tune BERT for text classification?"
  venue: Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science
  vol: 11856
  pages_or_artno: 194-206
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
本家族是"隐性停刊稳健性"(ceased-media robustness / survivorship robustness)变量族在 fin_sent_zh 这一 BERT 情感模型正面概率上的落地实例。构念要回答的问题是: 当我们把那些在样本期内事实上退出报道覆盖(de-facto cessation, 即某来源在后续年份不再产出目标银行相关报道)的媒体来源整批剔除之后, 该银行-年度的媒体情感信号会不会发生系统性移动。这一问题不是可有可无的润色, 而是媒体计量经济学的一个真实识别威胁: 媒体来源的进入与退出并非随机, 退出往往与其报道立场、地域覆盖、财经专业度相关, 若不加处理, 存活下来的来源会让情感指标向幸存者一侧倾斜, 进而污染以媒体暴露为工具变量(Bartik / leave-one-out 暴露)的两阶段最小二乘, 使排他性约束在来源构成漂移的年份被削弱。attention_media.py 的停刊稳健性块因此对全部主流情感测度(LLM 投票、各厂商大模型、六部词典、三家 BERT)一律并排产出一个"剔除停刊后重算"的孪生列, fin_sent_zh 的正面概率就是其中一支。

数据源头是 stage 23 (23_bert_tone.parquet) 输出的文章级 fin_sent_zh 正面概率列 fin_sent_zh_正面{track}。fin_sent_zh 指 bardsai/finance-sentiment-zh-base 这一在金融短语库(Financial PhraseBank)上微调的中文三分类(中性/正面/负面)BERT, 是本项目三家 BERT(finbert_cn、fin_sent_zh、finbert2)之一。它给每篇报道输出对"正面"这一类的 softmax 概率, 长文超出模型上下文窗口时用 50% 重叠的滑动窗口分段推理再按置信度合并。停刊标记来自同一 producer 内的 detect_defacto_cessation, 它扫描来源在时间轴上的出现-消失模式, 给每篇报道打 _is_ceased_media 标签; 本家族只对 _is_ceased_media==0 的存活媒体文章做 groupby(['target_bank','year']).mean() 聚合。

【方法学与计算】
计算链路极简且刻意不做二次归一化: 先在 runner 步骤 3b/3d 把文章级正面概率乘上相应权重预计算出 fin_sent_zh_正面_w{track}(乘 mention_density, 即 Hassan et al. (2023) 一脉以文本提及密度构造暴露度的价值加权思路)与 fin_sent_zh_正面_hw{track}(乘 herd_weight, 跟风衰减权重), 无权变体则保留裸概率; 随后 attention_media.py 的 C.4 动态发现块按 _SCORE_PATTERNS 前缀匹配到 fin_sent_zh_正面_*, 剔除停刊媒体行后对每个变体做 bank-year 算术均值, 冠以 exc_ 前缀落面板。注意这里是对"概率(或概率×权重)"直接取组内 mean, 而非像面板主轨 tone 那样除以权重和; 因此加权变体 exc_fin_sent_zh_正面_w / _hw 的数值尺度随权重均值平移, 应作稳定性并排读, 不与无权变体直接比较绝对水平。C.4 显式跳过 media-authority 加权(_mw_)与 IDF(_idf_)变体, 故本家族只含无权、mention-density 价值加权(_w)、herd 跟风衰减加权(_hw)三支 × 三轨共九列, 没有 mw 孪生。

三轨(full/ctx/ss)在此严格并排: full=标题 prepend + 全文正文, ctx=标题 + 银行实体上下文窗, ss=标题 + 银行∧金科同句窗; ss 轨采用镜像 ctx 的回退语义(无同句共现时退回全文并置 fallback 标志), 缺列时 producer 内 `if src in df_alive.columns` 守卫优雅跳过。留篇门控口径与全项目 2026-06-29 的 full-only 裁决一致: 一篇报道是否计入 bank-year 宇宙由 full 轨判定, ctx/ss 为 conditional-on-full 的稳健性轨。三轨、三权重变体各自 just-identified、互为稳健性、不分主次, 严禁把它们混进同一 over-identified 的 Hansen J 过度识别检验——这是本项目贯穿三轨、co-primary 双轨嵌入、词典消融/政治词权重/阈值梯子的统一铁律。fin_sent_zh 与另两家 BERT(finbert_cn、finbert2)之间同样是 co-equal 跨模型稳健, per-model 独立降级(某模型缺席仅掉自身族, 非嵌入 both-or-neither)。

【文献定位】
停刊稳健性的方法学动机直接承袭幸存者偏差与媒体覆盖内生的经典关切, producer 源码注释即锚定 Fang & Peress 与 Gentzkow 等对媒体覆盖非随机性的论证; 而本家族赖以剔除的暴露权重则对应 Hassan et al. (2023) 一脉的 firm-level exposure 测量思路——以文本中的提及密度构造价值加权暴露, 使高显著度报道获得更大权重, 正是 _w 变体的理论出处。就情感抽取本身, fin_sent_zh 的中文金融判读能力落在 Todd et al. (2024) 综述所勾勒的文本金融情感谱系内, 与 Lan et al. (2025) 的中文细粒度大模型情感、Ma et al. (2025) 的中文投资者细粒度情感词典构成互补的方法学三角; BERT 微调判读的工程口径则依 Sun et al. (2019) 的 fine-tune 范式。更宏观地, 媒体文本的措辞质量本身携带定价信息(Hwang & Kim, 2017)这一顶刊证据, 为"值得对情感测度做停刊剔除、来源构成、加权口径三重稳健性"提供了信号价值层面的正当性: 若媒体语调不含信息, 就无需如此审慎地防其被幸存来源污染。

## VAR: exc_fin_sent_zh_正面_ctx

【变体差分】
本列是无权变体的 ctx 轨: 对剔除隐性停刊媒体后的存活文章集, 取 fin_sent_zh_正面_ctx(fin_sent_zh BERT 在"银行实体上下文窗"文本上判出的正面类概率)的 bank-year 算术均值。相对家族 canonical(可视 full 轨无权列为参照), 它的差分维度是"文本轨=ctx"而非权重: ctx 轨的输入文本是标题 prepend 后再截取围绕目标银行实体的上下文窗口(窗口半径见 filtering.yaml), 剥离了与银行无关的段落, 因而比 full 轨更聚焦、但样本更易受实体识别噪声影响。权重维度为空——既不乘 mention_density 也不乘 herd_weight, 是裸正面概率的组内均值, 数值严格 ∈ [0,1]。它与 exc_fin_sent_zh_正面_full / _ss 三轨并排, 各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。作为 conditional-on-full 的稳健性轨, 其 bank-year 行宇宙是 full 轨留篇集的子集, 但 per-track 概率均值照各自 alive-media 文章集独立计算。dev T=2 语料上 ctx 与 full 常高度共线属预期, 生产 T=19 方显分辨力。此外须留意, exc_ 前缀带来的样本收缩会让本列在停刊媒体占比高的银行-年度上与非停剔孪生产生可观差距, 而在几乎无来源退出的银行-年度上二者趋同; 这种"差距随停刊强度变化"的结构本身就是稳健性叙事要展示的诊断信号, 而非需要抹平的噪声。fin_sent_zh 作为 Financial PhraseBank 微调的中文三分类器, 其正面类概率对 ctx 轨这种截断文本的判读稳定性弱于 full 轨, 故本列读数应与同轨 finbert_cn / finbert2 的 exc 孪生并置互证, per-model 独立降级、不因某模型缺席而连坐。

## VAR: exc_fin_sent_zh_正面_full

【变体差分】
本列是无权变体的 full 轨, 可作本家族最贴近 canonical 的参照列: 对剔除隐性停刊媒体后的存活文章集, 取 fin_sent_zh_正面_full 的 bank-year 算术均值。full 轨输入文本 = 标题 prepend + 完整正文, 是三轨中信息最全、也是全项目留篇门控(2026-06-29 full-only 裁决)据以判定"是否一篇银行金科报道"的唯一轨。权重维度为空: 裸正面概率的组内均值, 数值 ∈ [0,1], 越大表示存活媒体对该银行当年的整体语调越偏正面。它与家族内 _w_full(mention-density 价值加权)、_hw_full(herd 跟风衰减加权)构成"同轨不同权"的三支并排, 与 _ctx / _ss 构成"同权不同轨"的三支并排; 六向并排一律互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。与其非停剔孪生(面板主轨 fin_sent_zh_pos_full 一类)相比, 本列的唯一区别是分子文章集已剔除 _is_ceased_media==1 的退出来源, 因此二者系数的稳定性对比即是幸存者偏差诊断本身。作为 full 轨无权列, 它在本家族九列里方法学假设最少(不加权、只做停刊剔除、用信息最全的全文轨), 因而适合充当稳健性表格里的基准锚: 若基准锚与加权、窄轨诸列结论一致, 则说明主结果既不被幸存来源驱动、也不被暴露加权口径或文本窗选择驱动。fin_sent_zh 正面概率在 full 轨上判读最稳, 本列亦是与另两家 BERT 的 exc_finbert_cn_正面_full / exc_finbert2_正面_full 做跨模型互证的首选并置对象, per-model 独立降级。

## VAR: exc_fin_sent_zh_正面_hw_ctx

【变体差分】
本列是 herd-decay 加权(_hw)变体的 ctx 轨。差分维度有二: 其一权重=herd_weight_ctx, 即 runner 步骤 3d 用跟风衰减(Tetlock 2011; Edwards 2001 式)对 ctx 轨相似度扎堆报道降权后得到的文章级权重, 乘进 fin_sent_zh_正面_ctx 后再对存活文章取组内均值; 其二文本轨=ctx(标题 + 银行实体上下文窗)。herd_weight 的用意是压低同期高度相似、互相跟风的报道对情感均值的重复贡献, 使一篇独立报道与十篇雷同转发不被等同计数。因是"概率×权重"直接取 mean 而非除以权重和, 本列数值尺度随 herd_weight_ctx 的均值平移, 不应与无权 _ctx 列比绝对水平, 只作系数稳定性并排。herd_weight 三轨独立: _ctx 轨用 herd_weight_ctx, 与 full / ss 轨的 herd 权重严格分轨, 缺列时优雅回退。本列与家族内无权、_w 两支变体, 以及 _hw_full / _hw_ss 两个同权异轨列并排, 各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。本列叠加了停刊剔除与跟风衰减两层净化, 又落在信息量居中的 ctx 轨上, 因而在稳健性表中承担"若同时防幸存者偏差与媒体羊群、且只看银行相关段落, 正面情感信号是否仍成立"的问询。dev T=2 上 herd_weight_ctx 的分辨力有限, 常与 full 轨权重高度共线, 应以生产 T=19 语料为准判读; 缺 herd_weight_ctx 列时按 legacy 单列或 herd_weight_full 优雅回退, 此时本列退化为与无权 ctx 列高度相关的近似, 须结合日志确认权重来源后再解读。

## VAR: exc_fin_sent_zh_正面_hw_full

【变体差分】
本列是 herd-decay 加权(_hw)变体的 full 轨。权重=herd_weight_full: runner 步骤 3d 对 full 轨(标题 prepend + 全文)计算的跟风衰减权重, 对同期相似度扎堆的报道降权, 抑制媒体羊群效应导致的情感重复计数(Tetlock 2011; Edwards 2001)。计算为剔除隐性停刊媒体后, 对 fin_sent_zh_正面_full·herd_weight_full 取 bank-year 算术均值——直接对加权概率取 mean 而非归一化, 故数值随权重均值平移, 仅作稳定性并排, 不与无权 _full 或 _w_full 比绝对水平。三重差分同时叠加于本列: 停刊剔除(exc_)+ herd 跟风衰减加权(_hw)+ full 全文轨。它是本家族里方法学假设最强的一支(既信 full 轨全文、又信 herd 降权、又信停刊剔除), 因而在稳健性叙事里承担"三重净化后主结论是否仍成立"的角色。与家族内其余八列并排, 三权重变体各自 just-identified、互为稳健性、不分主次, herd 权重三轨(full/ctx/ss)亦各自分轨并排, 一律禁混同一 over-identified Hansen J。正因假设最强, 本列在稳健性叙事中的位置也最"苛刻": 它检验的是同时信任 full 全文判读、herd 降权抑制羊群、以及停刊剔除防幸存者三重净化之后, 存活媒体对该银行当年的 fin_sent_zh 正面语调是否仍与主轨同号同量级。若本列系数在三重净化下依旧稳定, 是主结论稳健性的强证据; 若显著漂移, 则提示情感信号可能部分来自扎堆报道或退出来源, 需回到机制层面追因。它应与另两家 BERT 的对应 _hw_full exc 列并置跨模型互证, per-model 独立降级。

## VAR: exc_fin_sent_zh_正面_hw_ss

【变体差分】
本列是 herd-decay 加权(_hw)变体的 ss 轨(银行∧金科同句窗)。权重=herd_weight_ss, 由 stage 24 镜像 ctx 逻辑对 ss 轨相似度扎堆报道计算的跟风衰减权重, 乘进 fin_sent_zh_正面_ss 后对存活文章取组内均值。ss 轨文本是三轨中最窄的: 标题 + 目标银行与金融科技词同句共现的句子窗(半径见 filtering.yaml::context_window.ss_sentence_radius), 语义最聚焦于"银行谈金科"的语境, 但也最易退化——无银行∧金科同句共现时 ss 轨镜像 ctx 回退语义置 fallback 标志、退回全文 body。因此本列在 dev T=2 上常出现零方差或大量回退属预期, 生产 T=19 方具分辨力。数值因"概率×herd 权重"直接取 mean 而随权重尺度平移, 只作并排稳定性读。缺 herd_weight_ss 列时 producer 内守卫优雅跳过或回退 herd_weight_full。本列与 _hw_full / _hw_ctx 同权异轨并排、与 ss 轨的无权及 _w 变体同轨异权并排, 各自 just-identified、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J。本列是本家族里退化倾向最强的一支: ss 轨已因同句共现稀疏而大量回退, 再叠加 herd_weight_ss(本身也依赖 ss 轨相似度计算)与停刊剔除的样本收缩, 三重因素叠加使 dev T=2 上极易出现全 NaN 或零方差, 属预期而非缺陷, 须以生产 T=19 语料为准。判读时应把它当作"最窄语境 + 最强净化"的极端稳健性点位, 与同轨无权 _ss、价值加权 _w_ss 并置, 观察三权重口径是否给出方向一致的 ss 轨结论; 缺 herd_weight_ss 时按守卫回退 herd_weight_full, 此时本列语义弱化, 须结合日志核实。

## VAR: exc_fin_sent_zh_正面_ss

【变体差分】
本列是无权变体的 ss 轨。对剔除隐性停刊媒体后的存活文章集, 取 fin_sent_zh_正面_ss(fin_sent_zh BERT 在"银行∧金科同句窗"文本上判出的正面概率)的 bank-year 算术均值, 无任何权重, 数值 ∈ [0,1]。差分维度是文本轨=ss: 三轨中最窄、最聚焦"银行谈金融科技"语境的一轨。ss 轨采用镜像 ctx 的回退语义——某篇报道无银行与金科词同句共现时, content_ss 退回全文 body 并置 ss_is_fallback=True(与 ctx 共享 n_articles 分母), FINTECH_AC=None 时整体优雅降级、fallback 全 True。因此本列在 dev T=2 上易退化(大量回退或零方差), 应以生产 T=19 为准。它与 exc_fin_sent_zh_正面_full / _ctx 构成无权三轨并排, 与同轨的 _w_ss / _hw_ss 构成同轨三权重并排; 全部并排各自 just-identified、互为稳健性、不分主次, 禁混同一 over-identified Hansen J。作为 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, 但正面概率均值照 ss 轨自身 alive-media 文章集独立计算。作为无权最窄轨, 它检验的是"只看银行与金科同句语境、且剔除退出来源后, fin_sent_zh 正面语调是否仍稳定", 是三轨无权族里语义最锐利也最脆弱的一支。它与 full / ctx 无权列的落差, 反映从全文到同句窗逐步收窄语境时正面信号的衰减或增强, 可与 finbert_cn / finbert2 的同轨 exc 孪生并置, 检验这一轨道敏感性是否为跨模型一致的稳健现象, per-model 独立降级、非嵌入 both-or-neither。

## VAR: exc_fin_sent_zh_正面_w_ctx

【变体差分】
本列是 mention-density 价值加权(_w)变体的 ctx 轨。权重=mention_density: runner 步骤 3b 依 Hassan et al. (2023) 一脉以文本提及密度构造暴露度的思路, 用报道中目标银行的提及密度作权重, 乘进 fin_sent_zh_正面_ctx 后对剔除停刊后的存活文章取 bank-year 算术均值。其立意是让高显著度、密集提及目标银行的报道在情感均值中占更大分量, 弱化一笔带过式提及的稀释效应。文本轨=ctx(标题 + 银行实体上下文窗)。因对"概率×mention_density"直接取 mean 而非除以密度和, 本列数值尺度随 mention_density 均值平移, 只作稳定性并排, 不与无权 _ctx 或 herd 加权 _hw_ctx 比绝对水平。它与家族内无权、_hw 两支变体, 以及 _w_full / _w_ss 两个同权异轨列并排, 三权重变体各自 just-identified、互为稳健性、不分主次, 三轨亦各自分轨并排, 严禁混进同一 over-identified Hansen J。价值加权与 herd 跟风衰减加权的立意方向相反却互补: 前者放大高暴露报道的贡献、后者压低扎堆报道的重复贡献, 二者在 ctx 轨上与无权列三方并置, 恰好从"该不该给密集提及加权"和"该不该给雷同报道降权"两个正交维度检验情感均值的稳健性。本列在 dev T=2 上因 mention_density 方差有限而分辨力受限, 生产 T=19 语料方能体现价值加权与等权的实质差异, 判读须以生产规模为准, 并结合 exc_fin_sent_zh_正面_ctx 无权列读其增量。

## VAR: exc_fin_sent_zh_正面_w_full

【变体差分】
本列是 mention-density 价值加权(_w)变体的 full 轨。权重=mention_density, 按 Hassan et al. (2023) 一脉以文本提及密度构造暴露度的口径, 使密集提及目标银行的报道获得更大权重; 乘进 fin_sent_zh_正面_full(full=标题 prepend + 全文)后, 对剔除隐性停刊媒体的存活文章取 bank-year 算术均值。这是本家族里"价值加权"叙事最标准的一支: full 全文轨保证信息最全, mention-density 权重放大高暴露报道, exc_ 前缀再剔除退出来源, 三者叠加检验主结论对暴露加权口径的敏感性。因是加权概率直接取 mean、未除以密度和, 数值随权重均值平移, 仅作系数稳定性并排读, 不与无权 _full 或 herd 加权 _hw_full 比绝对水平。它与家族其余八列并排, 三权重变体(无权 / _w mention-density / _hw herd)各自 just-identified、互为稳健性、不分主次, 三轨(full/ctx/ss)各自分轨并排, 一律禁混同一 over-identified Hansen J。相对其非停剔孪生, 唯一差别是分子文章集已剔停刊来源, 故二者系数对比即幸存者偏差诊断。本列在稳健性表中通常与无权 _full 基准锚成对呈现: 两者若同号同量级, 说明主结论既不被幸存来源、也不被暴露加权口径驱动, 是较强的一致性证据; 两者若分歧, 则提示情感信号对"高提及密度报道"权重敏感, 需追问是否由少数高暴露报道主导。它同样应与 finbert_cn / finbert2 的 _w_full exc 孪生跨模型互证, 三家 BERT co-equal、per-model 独立降级, 不因某模型缺席而连坐掉列。

## VAR: exc_fin_sent_zh_正面_w_ss

【变体差分】
本列是 mention-density 价值加权(_w)变体的 ss 轨(银行∧金科同句窗)。权重=mention_density(Hassan et al. 2023 一脉的提及密度价值加权暴露), 乘进 fin_sent_zh_正面_ss 后对剔除停刊后的存活文章取 bank-year 算术均值。双重差分叠加: 文本轨=ss(三轨中最窄、最聚焦"银行谈金科"语境, 镜像 ctx 回退语义——无同句共现时退回全文 body 并置 fallback), 权重=mention-density 价值加权。因是加权概率直接取 mean 而非归一化, 数值随权重尺度平移, 只作并排稳定性读。ss 轨在 dev T=2 上易退化(大量回退或零方差), 生产 T=19 方具分辨力; 缺列或 FINTECH_AC=None 时 producer 内守卫优雅跳过或整体降级。它与 _w_full / _w_ctx 同权异轨并排、与 ss 轨的无权及 _hw 变体同轨异权并排, 全部各自 just-identified、互为稳健性、不分主次, 严禁把三轨、三权重变体混进同一 over-identified 的 Hansen J 过度识别检验。本列是本家族里同时叠加最窄文本轨(ss)、价值加权(_w)与停刊剔除三重设定的组合, 与 _hw_ss 分居"价值加权"与"跟风衰减加权"两端, 二者加上无权 _ss 构成 ss 轨的三权重稳健性并排。因 ss 轨大量回退叠加 mention_density 有限方差, dev T=2 上本列极易退化, 判读一律以生产 T=19 语料为准; 它更宜作为稳健性附表里的边角点位, 用于确认即便在最窄语境与价值加权口径下, 剔除退出来源后的 fin_sent_zh 正面语调仍与主轨方向一致, 而非充当主表测度。

<!-- rendered-citations:begin -->
Lan, Y., Wu, Y., Xu, W., Feng, W., & Zhang, Y. (2025). Chinese fine-grained financial sentiment analysis with large language models. Neural Computing and Applications, 37(30), 24883-24892. https://doi.org/10.1007/s00521-024-10603-6
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management, 31(1), e1549. https://doi.org/10.1002/isaf.1549
Hassan, T. A., Hollander, S., van Lent, L., Schwedeler, M., & Tahoun, A. (2023). Firm-level exposure to epidemic diseases: COVID-19, SARS, and H1N1. Review of Financial Studies, 36(12), 4919-4964. https://doi.org/10.1093/rfs/hhad044
Sun, C., Qiu, X., Xu, Y., & Huang, X. (2019). How to fine-tune BERT for text classification?. Chinese Computational Linguistics (CCL 2019), Lecture Notes in Computer Science. https://doi.org/10.1007/978-3-030-32381-3_16
Hwang, B.-H., & Kim, H. H. (2017). It pays to write well. Journal of Financial Economics, 124(2), 373-394. https://doi.org/10.1016/j.jfineco.2017.01.006
<!-- rendered-citations:end -->
