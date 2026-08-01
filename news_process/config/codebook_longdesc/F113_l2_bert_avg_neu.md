---
family_id: F113
columns:
- bert_avg_neu_app_ctx
- bert_avg_neu_app_full
- bert_avg_neu_app_ss
- bert_avg_neu_ctx
- bert_avg_neu_full
- bert_avg_neu_ss
- bert_avg_neu_tech_ctx
- bert_avg_neu_tech_full
- bert_avg_neu_tech_ss
unit: 概率 (无量纲, 中性类后验概率, 取值 [0,1])
formula: "bert_avg_neu{suffix}{track} = mean_{b in THREE_CLASS_MODELS}( {b}_neu{suffix}{track} ); 逐模型列 {b}_neu 本身 = 该 BERT 模型对 bank-year 内相关文章中性类 softmax 后验概率的均值; suffix ∈ {'', _tech, _app}; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/geography.py::compute_composite_indicators
upstream:
- 23_tone_berts.parquet
- 40_panel_yearly.parquet (per-model {b}_neu{suffix}{track} 逐模型中性概率列)
citations:
- doi: 10.1016/j.nlp.2025.100148
  type: journal
  authors: Sun, Y., Yuan, H., & Xu, F.
  year: 2025
  title: "Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features"
  venue: Natural Language Processing Journal
  vol: 11
  pages_or_artno: 100148
- doi: 10.1111/1911-3846.12832
  type: journal
  authors: Huang, A. H., Wang, H., & Yang, Y.
  year: 2023
  title: "FinBERT: A large language model for extracting information from financial text"
  venue: Contemporary Accounting Research
  vol: 40
  issue: 2
  pages_or_artno: 806-841
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/07421222.2018.1440766
  type: journal
  authors: Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W.
  year: 2018
  title: "On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services"
  venue: Journal of Management Information Systems
  vol: 35
  issue: 1
  pages_or_artno: 220-265
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.48550/arXiv.1810.04805
  type: arxiv
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2018
  title: "BERT: Pre-training of deep bidirectional transformers for language understanding"
  venue: arXiv
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: "10.1002/isaf.1549"
  title: "Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions"
  authors: "Todd, A., Bowden, J., & Moshfeghi, Y."
  year: 2024
  venue: "Intelligent Systems in Accounting, Finance and Management"
  type: "journal"
new_dois:
  - "10.1002/isaf.1549"
---

## CORE

【构念与来源】
本家族测度的是银行-年面板层面「银行金科报道的中性情感浓度」, 即 BERT 三分类情感模型判为中性 (既非正面亦非负面) 的类后验概率, 在跨模型集成后的水平。它与正面浓度 (bert_avg_pos)、负面浓度 (bert_avg_neg) 构成同一概率单纯形上的三个坐标, 三者在三分类模型族内近似满足 pos+neu+neg≈1 的恒等约束。中性浓度这一维度在金融文本测度里长期被当作「残差」而遭忽视, 但它承载独立的经济含义: 高中性占比往往对应事实陈述型、程序性披露型、无明确褒贬立场的报道语域, 是媒体「信息中介」而非「情绪放大器」角色的直接刻画。数据来源链条为: 原始中文银行/金科新闻经预处理与银行、金科实体识别 (stage 11/12)、共现硬过滤 (stage 13) 与三轨文本物化 (stage 14) 后, 在 stage 23 由多个中文金融领域微调的 BERT 模型逐篇打分, 输出每篇文章正/中/负三类的 softmax 后验概率; 这些逐篇概率先在 encode 层按银行-年聚合为逐模型面板列 (形如 finbert_cn_neu_full、fin_sent_zh_neu_full), 再于 stage 40 的面板综合指标步骤 (geography.py::compute_composite_indicators) 跨模型取行均值, 得到本家族的九个集成列。

【方法学与计算】
计算公式为对三分类模型子集 THREE_CLASS_MODELS 上的逐模型中性概率列取简单行均值: bert_avg_neu = mean_b({b}_neu)。关键实现细节有三。其一是聚合域的严格纪律: 修复 (omni-g-geography-06) 后, pos/neg/neu 一律只在三分类模型 (如 finbert_cn、fin_sent_zh) 上平均, 而二分类的 finbert2 被排除在集成之外——因为二分类模型把中性概率质量重归一进 pos/neg (pos+neg≡1), 若混入会破坏三类和为一的单纯形约束并系统性上偏 pos。finbert2 的逐模型列作为二分类稳健轨单独保留, 不进本集成。其二是缺列优雅降级: 底层 _safe_mean 只对面板中实际存在的逐模型列取均值, 任一模型的某轨列未落盘时不报错、退化为在现存列上求均值, 全缺时返回 NaN; 因此本家族在早期试跑 T=2 语料或某模型缺席时不会使阶段崩溃, per-model 独立降级 (缺 finbert2 仅掉其自身族, 而非 co-primary 嵌入那种 both-or-neither 连坐)。其三是集成语义: 跨模型行均值是「均值-ensemble」, 与跨模型多数投票 (LLM 侧的共识 headline) 是不同的聚合范式, 目的是降低单一模型的测量噪声, 而非产生一个门控判定。中性概率本身取值于 [0,1], 是无量纲后验概率, 不做任何归一化或标准化。三个中文 BERT 模型互为稳健性、不分主次: 各模型的逐模型子测度并排作为跨厂商/跨架构稳健轨, 各自 just-identified 并排, 严禁把不同模型的中性概率混进同一个 over-identified Hansen J 过度识别式; 本集成列是它们的均值展示轨, 跨模型一致性另由 Krippendorff α / Cohen κ 与根级跨模型 FWER 模板承担。

【文献定位】
本家族坐落在金融文本情感测度的机器学习转向脉络上。Devlin et al. (2018) 提出的 BERT 双向 Transformer 预训练是本家族全部逐模型打分器的架构基础; Huang et al. (2023) 的 FinBERT 证明领域微调的大型语言模型在抽取金融文本信息上系统性优于通用词典法, 为采用 BERT 概率而非纯词典计数提供直接依据。Frankel et al. (2022) 在 Management Science 上系统比较了机器学习与词典法的披露情感测度, 指出二者在不同语域下各有偏误、宜互为稳健而非彼此替代——这正是本项目让 BERT 概率轨与词典法情感轨、LLM 投票轨三足并立的方法论根据。Loughran and McDonald (2016) 对会计与金融文本分析方法的权威综述界定了情感词典与分类器的适用边界, 并强调中性/非情感类的处理直接影响测度效度。Sun et al. (2025) 更直接地把「中性特征」显式建模进预训练语言模型的金融情感分析, 呼应本家族把中性类概率单列为一等测度而非丢弃残差的取向。Tetlock (2007) 奠定了媒体语调对市场的信息传导框架, 说明报道中性/情绪成分的此消彼长本身即具经济后果。分类维度上的技术导向 (_tech) 与应用导向 (_app) 子样本区分, 概念上对应 Gomber et al. (2018) 对金融科技功能谱系的划分——基础技术层与面向用户的应用/服务层承载不同的叙事语域与情感基线。Todd, Bowden, & Moshfeghi (2024, Intelligent Systems in Accounting, Finance and Management) 系统综述金融文本情感分析文献并指出中性/非情感类处理是测度效度的关键未决问题, 呼应本家族将中性类概率单列为一等测度而非弃之为残差的取向。

## VAR: bert_avg_neu_full

【变体差分】
本列是家族的 canonical 集成中性浓度: 全部留篇文章 (无分类维度子样本限定, suffix 为空) 在 full 轨上的跨三分类模型中性概率行均值。full 轨的文本口径是「标题 prepend + 全文正文」(content_full), 即把标题前置拼接进正文后对整篇打分, 是信息最完整、样本量最大的轨道。留篇门控是 full-only 口径 (2026-06-29): 一篇报道是否计入银行金科报道宇宙, 只看其 full 轨是否被判定为一篇合格的银行金科报道 (llm_verified_full == True); 因此 full 轨的行宇宙即整个留篇集, 本列的银行-年分母与 n_articles 的 full-only 口径严格一致。作为 canonical, 本列是同族其余八列 (两条其他轨 + 两个分类维度各三轨) 差分比较的参照基准。它与 bert_avg_pos_full、bert_avg_neg_full 在三分类族内近似构成概率单纯形, 三者水平相加约为一。经济解读上, 本列取值偏高意味着银行在该年金科报道以事实陈述、程序性披露、无明确褒贬立场的语域为主, 媒体更多扮演信息中介而非情绪放大器角色; 取值偏低则意味着报道情感极化程度更高, 正负立场更鲜明。作为主线 canonical, 本列是描述统计表与稳健性对照表里 BERT 集成中性浓度的默认列, 也是同族其余八列做轨道差分与分类维度差分时的分母/参照基准。它与 ctx/ss 两轨互为稳健性、不分主次, 各自 just-identified 并排, 严禁把三轨的中性概率混进同一 over-identified Hansen J 过度识别式; 亦不与词典法、LLM 投票等其他方法的情感测度混入同一过度识别式。

## VAR: bert_avg_neu_ctx

【变体差分】
本列与 canonical 的唯一差分在文本轨道: 采用 ctx 轨 (content_ctx) 而非 full。ctx 轨的文本口径是「标题 prepend + 实体上下文窗口」, 即只保留银行/金科实体附近的上下文片段 (而非整篇正文) 后交由三分类 BERT 打分, 再跨模型取行均值。相对 full 轨, ctx 轨聚焦于与目标实体直接相关的语句, 削弱了整篇长文中无关段落对情感基线的稀释, 因而其中性浓度刻画的是「就银行金科话题本身而言」的中性程度。留篇门控仍是 full-only: ctx 轨是 conditional-on-full 的测度轨, 其行宇宙是 full 留篇集的子集, per-track 列在该子集上照常计算。分类维度上本列不设子样本限定 (suffix 为空), 与 canonical 同为全留篇口径。由于剔除了整篇长文中与银行金科无关的段落, ctx 轨的中性基线通常与 full 轨不同: 无关段落多为背景性、事实性叙述, 其剔除会改变中性质量的相对占比, 因此本列刻画的是话题相关语句上的中性程度, 而非整篇文档的中性程度。本列作为 full 轨的首要稳健性对照存在, 与 full/ss 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨中性概率混进同一 over-identified Hansen J, 亦不与其他方法测度混入同一过度识别式。ctx 源列任一模型未落盘时 _safe_mean 优雅降级为现存列均值或 NaN, per-model 独立降级不连坐其他模型。

## VAR: bert_avg_neu_ss

【变体差分】
本列的差分维度是 ss 轨 (content_ss)。ss 轨是三轨中口径最严的一条: 文本只保留「银行与金科词在同一句内共现 (±N 句窗, 默认半径 1)」的语句片段, 标题同样 prepend。其回退语义严格镜像 ctx 轨——当某篇报道不存在银行∧金科的同句共现时, content_ss 回退为全文 body, 且 ss_is_fallback 置为 True, 与 ctx 共享 n_articles 分母; 若上游金科自动机 FINTECH_AC 为 None 则 *_is_fallback 全 True 优雅降级。因此 ss 轨中性浓度刻画的是「银行与金科被同句并置叙述」这一最贴近共现语义处的情感中性程度, 是三轨里对话题相关性要求最高的轨道。留篇门控仍为 full-only, ss 轨为 conditional-on-full 的子集测度轨。分类维度不设限 (suffix 为空)。在早期试跑 T=2 语料上, ss 轨因同句共现样本稀薄常出现某些模型某轨列未落盘, 由 _safe_mean 优雅返回 NaN 属预期退化, 生产期 T=19 恢复正常。因回退分支的存在, ss 轨在同句共现稀薄的银行-年会退化为近似 full 轨口径, 这一 both-track 混合特性使其在生产期成为「话题贴近度最高、但样本约束最强」的一条测度; 解读时须结合 ss_is_fallback 的占比判断该银行-年究竟落在严格同句语义还是回退全文语义上。本列与 full/ctx 互为稳健性、不分主次, 各自 just-identified 并排, 严禁三轨中性概率混进同一 over-identified Hansen J, 亦不与其他方法测度混入同一过度识别式。per-model 独立降级, 缺某模型仅掉其自身贡献而不连坐其余三分类模型。

## VAR: bert_avg_neu_tech_full

【变体差分】
本列在 canonical 基础上叠加分类维度子样本限定: 只在被判为「技术导向」(_tech) 的金科报道子样本上聚合, 轨道仍为 full。技术导向维度对应 Gomber et al. (2018) 金融科技功能谱系中偏向底层技术与基础设施 (如支付清算技术、区块链、云计算、数据基础设施) 的报道语域, 与应用/服务导向相对。实现上, 只有当分类计数列 n_articles_tech 存在于面板中时本列才生成, 逐模型中性概率列形如 finbert_cn_neu_tech_full, 跨三分类模型取行均值; 分母是该技术导向子样本内的文章数, 而非全留篇集。留篇门控整体仍是 full-only, 分类维度是在留篇集之上的进一步子样本切分。本列刻画的是「银行涉技术导向金科报道」的中性情感浓度, 与应用导向轨 (_app) 并排作为分类维度的规格稳健性梯子: 两分类维度各自 just-identified 并排、互为稳健性不分主次, 严禁把 tech 与 app 的中性概率混进同一 over-identified Hansen J。与无后缀 canonical 相比, 本列的银行-年覆盖更稀疏, 缺列由 _safe_mean 优雅降级为现存列均值或 NaN。经济上, 技术导向报道多围绕基础设施升级、系统安全、技术合作等相对中立的议题, 其中性情感基线通常异于应用导向报道, 因而 tech 与 app 两列的对照本身即构成一条「叙事语域差异」的规格稳健性证据: 若主结论在两分类维度上同号同量级, 则说明结论不被特定语域驱动。本列须与应用导向 full 轨读作一对, 而非单独解释。

## VAR: bert_avg_neu_tech_ctx

【变体差分】
本列是技术导向 (_tech) 分类维度与 ctx 轨的组合。相对同维度的 full 轨 (bert_avg_neu_tech_full), 差分在文本口径: ctx 轨只取银行/金科实体上下文窗口而非整篇正文; 相对同轨的无维度 canonical ctx 列 (bert_avg_neu_ctx), 差分在样本域: 只保留 n_articles_tech 判定的技术导向子样本。因此本列刻画的是「就技术导向金科话题的实体上下文而言」的集成中性浓度。生成前提是面板中存在 n_articles_tech 计数列, 逐模型源列形如 finbert_cn_neu_tech_ctx, 跨三分类模型行均值, 分母为技术导向子样本篇数。留篇门控仍为 full-only, 本列为 conditional-on-full 的分类维度子样本×ctx 轨测度。它与本维度的 full/ss 两轨、以及应用导向维度的对应列均互为稳健性、不分主次, 各自 just-identified 并排, 严禁分类维度或三轨的中性概率混进同一 over-identified Hansen J。开发期该组合样本极稀, 某些逐模型轨列缺失时 _safe_mean 优雅返回 NaN 属预期退化, 生产期 T=19 方恢复稳定取值。本列是「技术导向×实体上下文」两个正交约束的交叉, 其取值不应与无维度 ctx 列或 tech_full 列直接做水平比较, 因为分母样本域与文本口径均不同; 恰当的用法是把它放进以三轨为轴、以分类维度为轴的二维稳健性网格中, 与同网格邻居 (tech_full、tech_ss、app_ctx) 做同号一致性检验。per-model 独立降级, 缺某模型仅掉其自身贡献。

## VAR: bert_avg_neu_tech_ss

【变体差分】
本列是技术导向 (_tech) 分类维度与 ss 轨 (最严同句共现轨) 的组合, 是家族中样本约束最强的列之一: 既要求报道属技术导向金科子样本 (n_articles_tech 门控), 又要求文本落在银行∧金科同句共现窗口 (content_ss) 内。ss 轨的回退语义严格镜像 ctx: 无同句共现时 content_ss 回退全文 body 且 ss_is_fallback=True, 与 ctx 共享分母; FINTECH_AC 为 None 时优雅全回退。逐模型源列形如 finbert_cn_neu_tech_ss, 跨三分类模型取行均值。留篇门控为 full-only, 本列是 conditional-on-full 的分类维度子样本×ss 轨测度轨。它刻画的是「银行与技术导向金科被同句并置叙述处」的中性情感浓度。本列与本维度的 full/ctx 两轨、以及应用导向维度的对应列互为稳健性、不分主次, 各自 just-identified 并排, 严禁分类维度与三轨的中性概率混进同一 over-identified Hansen J。在早期试跑 T=2 语料上, 技术导向×同句共现的交叉子样本极稀薄, 多数银行-年该列由 _safe_mean 优雅返回 NaN 属预期退化, 生产期 T=19 方恢复有效取值。本列位于「技术导向×同句共现」两个最强约束的交叉点, 是家族里语义最纯、覆盖最窄的一列, 因而更适合作为对主结论的最严苛稳健性探针而非主检验列; 解读时须同时结合 ss_is_fallback 占比与 n_articles_tech 规模判断该银行-年的有效性, 并把它放入以三轨为轴、分类维度为轴的稳健性网格与 tech_full、tech_ctx、app_ss 做同号一致性核对。per-model 独立降级, 缺某模型仅掉其自身贡献而不连坐其余三分类模型。

## VAR: bert_avg_neu_app_full

【变体差分】
本列在 canonical 基础上叠加应用导向 (_app) 分类维度子样本限定, 轨道为 full。应用导向维度对应 Gomber et al. (2018) 金融科技功能谱系中偏向面向用户的应用与服务层 (如网络借贷、财富管理、数字银行、消费金融等直接触达客户的金科服务) 的报道语域, 与技术导向 (_tech) 相对。生成前提是面板中存在 n_articles_app 计数列, 逐模型源列形如 finbert_cn_neu_app_full, 跨三分类模型取行均值; 分母为应用导向子样本内的文章数而非全留篇集。留篇门控整体仍为 full-only, 分类维度是留篇集之上的进一步切分。本列刻画的是「银行涉应用导向金科报道」的集成中性情感浓度, 与技术导向轨并排作为分类维度规格稳健性梯子: 两分类维度各自 just-identified 并排、互为稳健性不分主次, 严禁把 app 与 tech 的中性概率混进同一 over-identified Hansen J。经济上, 应用导向报道多围绕消费金融、数字银行、财富管理等直接触达用户的服务, 往往伴随更鲜明的褒贬立场 (成功/纠纷/监管), 其中性基线通常低于技术导向报道; 因此 app 与 tech 两列的水平差本身即刻画了两类金科叙事的情感极化差异。相对无后缀 canonical, 本列银行-年覆盖更稀疏, 缺列由 _safe_mean 优雅降级为现存列均值或 NaN, per-model 独立降级不连坐。

## VAR: bert_avg_neu_app_ctx

【变体差分】
本列是应用导向 (_app) 分类维度与 ctx 轨的组合。相对同维度 full 轨 (bert_avg_neu_app_full), 差分在文本口径: ctx 轨只取银行/金科实体上下文窗口而非整篇正文; 相对同轨无维度 canonical ctx 列 (bert_avg_neu_ctx), 差分在样本域: 只保留 n_articles_app 判定的应用导向子样本。因此本列刻画的是「就应用导向金科话题的实体上下文而言」的集成中性浓度。生成前提为面板存在 n_articles_app 计数列, 逐模型源列形如 finbert_cn_neu_app_ctx, 跨三分类模型行均值, 分母为应用导向子样本篇数。留篇门控为 full-only, 本列为 conditional-on-full 的分类维度子样本×ctx 轨测度。它与本维度的 full/ss 两轨、以及技术导向维度的对应列互为稳健性、不分主次, 各自 just-identified 并排, 严禁分类维度或三轨的中性概率混进同一 over-identified Hansen J。开发期该组合样本较稀, 逐模型轨列缺失时 _safe_mean 优雅返回 NaN 属预期退化, 生产期 T=19 方恢复稳定取值。本列是「应用导向×实体上下文」两个正交约束的交叉, 不应与无维度 ctx 列或 app_full 列直接做水平比较, 因分母样本域与文本口径均不同; 恰当用法是把它放进以三轨为轴、以分类维度为轴的二维稳健性网格中, 与同网格邻居 (app_full、app_ss、tech_ctx) 做同号一致性检验, 检视主结论是否稳健于文本口径与叙事语域的联合扰动。per-model 独立降级, 缺某模型仅掉其自身贡献。

## VAR: bert_avg_neu_app_ss

【变体差分】
本列是应用导向 (_app) 分类维度与 ss 轨 (最严同句共现轨) 的组合, 与 tech_ss 对称, 是家族中样本约束最强的列之一: 既要求报道属应用导向金科子样本 (n_articles_app 门控), 又要求文本落在银行∧金科同句共现窗口 (content_ss) 内。ss 轨回退语义严格镜像 ctx: 无同句共现时 content_ss 回退全文 body 且 ss_is_fallback=True, 与 ctx 共享分母; FINTECH_AC 为 None 时优雅全回退。逐模型源列形如 finbert_cn_neu_app_ss, 跨三分类模型取行均值。留篇门控为 full-only, 本列是 conditional-on-full 的分类维度子样本×ss 轨测度轨, 刻画的是「银行与应用导向金科被同句并置叙述处」的中性情感浓度。本列与本维度的 full/ctx 两轨、以及技术导向维度的对应列互为稳健性、不分主次, 各自 just-identified 并排, 严禁分类维度与三轨的中性概率混进同一 over-identified Hansen J。在早期试跑 T=2 语料上, 应用导向×同句共现的交叉子样本极稀薄, 多数银行-年该列由 _safe_mean 优雅返回 NaN 属预期退化, 生产期 T=19 方恢复有效取值。本列位于「应用导向×同句共现」两个最强约束的交叉点, 与 tech_ss 对称, 是家族里语义最纯、覆盖最窄的一列, 适合作为对主结论的最严苛稳健性探针而非主检验列; 解读时须同时结合 ss_is_fallback 占比与 n_articles_app 规模判断该银行-年的有效性, 并把它放入以三轨为轴、分类维度为轴的稳健性网格与 app_full、app_ctx、tech_ss 做同号一致性核对。per-model 独立降级, 缺某模型仅掉其自身贡献而不连坐其余三分类模型。

<!-- rendered-citations:begin -->
Sun, Y., Yuan, H., & Xu, F. (2025). Financial sentiment analysis for pre-trained language models incorporating dictionary knowledge and neutral features. Natural Language Processing Journal, 11, 100148. https://doi.org/10.1016/j.nlp.2025.100148
Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT: A large language model for extracting information from financial text. Contemporary Accounting Research, 40(2), 806-841. https://doi.org/10.1111/1911-3846.12832
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution: Interpreting the forces of innovation, disruption, and transformation in financial services. Journal of Management Information Systems, 35(1), 220-265. https://doi.org/10.1080/07421222.2018.1440766
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2018). BERT: Pre-training of deep bidirectional transformers for language understanding. arXiv [Preprint]. https://doi.org/10.48550/arXiv.1810.04805
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Todd, A., Bowden, J., & Moshfeghi, Y. (2024). Text-based sentiment analysis in finance: Synthesising the existing literature and exploring future directions. Intelligent Systems in Accounting, Finance and Management. https://doi.org/10.1002/isaf.1549
<!-- rendered-citations:end -->
