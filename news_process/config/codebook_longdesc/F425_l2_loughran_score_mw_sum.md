---
family_id: F425
columns:
- loughran_score_mw_sum_ctx
- loughran_score_mw_sum_full
- loughran_score_mw_sum_ss
unit: 媒体权威加权的净极性得分和 (无量纲运行和, 加权均值语调的分子, 未归一化)
formula: "loughran_score_mw_sum{track} = Σ_i (loughran_score_i{track} × media_authority_weight_i); 其中 loughran_score_i{track} 为文章 i 在 Loughran & McDonald (2011) 中文主译本 loughran_mcdonald_zh_2026 词典下经全套语言学规则 (否定翻转 / 程度副词六级 / 转折 ×1.5 / 句末重置) 逐词打分后自归一化所得的净极性得分 = Σ(final_score)/Σ|final_score| ∈ [−1,+1] (由 tone_words._compute_sentiment_with_rules 施加规则化, 区别于零规则的裸计数比 (neg−pos)/(pos+neg)≡msent_score), media_authority_weight_i = raw_authority_i / mean(raw_authority) 为均值归一化的媒体权威权重; 求和域 = 该 bank-year 内落入 {track} 轨的文章集"
producer: news_process/pipeline/panel/runner.py (步骤3c 媒体权威加权 MW 预计算 loughran_score_mw{track}; 与步骤3b 的提及密度加权 VW 无关) ; news_process/pipeline/panel/encode.py::_aggregate_bank_year (bank-year 求和 → loughran_score_mw_sum{track})
upstream:
- 14_materialize_ctx.parquet (content_full / content_ctx / content_ss)
- 22_tone_words.parquet (loughran_score{track} 文章级净极性)
- 40_panel 内 media_authority_weight (compute_media_authority_weights)
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2011
  title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks"
  venue: The Journal of Finance
  vol: 66
  issue: 1
  pages_or_artno: 35-65
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2016
  title: "Textual analysis in accounting and finance: A survey"
  venue: Journal of Accounting Research
  vol: 54
  issue: 4
  pages_or_artno: 1187-1230
- doi: 10.1146/annurev-financial-012820-032249
  type: journal
  authors: Loughran, T., & McDonald, B.
  year: 2020
  title: "Textual analysis in finance"
  venue: Annual Review of Financial Economics
  vol: 12
  issue: 1
  pages_or_artno: 357-375
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: "Sentiment analysis of economic text: A lexicon-based approach"
  venue: Economic Inquiry
  vol: 63
  issue: 1
  pages_or_artno: 125-143
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: Management Science
  vol: 68
  issue: 7
  pages_or_artno: 5514-5532
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: "Lexicon-based methods for sentiment analysis"
  venue: Computational Linguistics
  vol: 37
  issue: 2
  pages_or_artno: 267-307
- doi: "10.1111/eufm.70025"
  type: journal
  authors: "Jacobs, H., & Lauber, A."
  year: 2025
  title: "Media Sentiment and Price Run-Ups"
  venue: "European Financial Management"
new_dois:
  - "10.1111/eufm.70025"
---

## CORE

【构念与来源】
本家族刻画的是: 在一个银行-年 (bank-year) 单元内, 以 Loughran & McDonald (2011) 中文主译本词典 (config/tone_dicts.json 中登记为 loughran_mcdonald_zh_2026, 列前缀别名 loughran) 对每篇报道判定的净极性得分, 按该报道所属媒体的权威性加权后求和所得的运行和。它不是一个已归一化的语调指标, 而是媒体权威加权语调 (media-authority-weighted tone) 的分子: 下游把本列除以同一 bank-year 的媒体权威权重之和 sum_media_authority_weight, 才得到加权均值语调 loughran_tone_mw。之所以单独物化并落列, 是因为分子与分母各自具有可审计的经济含义 — 分子承载"极性 × 声量"的合成信号, 分母承载"总声量", 二者比值才是无量纲语调; 把分子独立成列便于稳健性检验中替换分母口径 (等权、提及密度权、羊群衰减权) 而复用同一分子逻辑。构念来源有二: 极性判定源于 Loughran & McDonald (2011) 在《Journal of Finance》提出、原为英文 10-K 文本设计的金融情感词典 (positive 1,295 词 / negative 3,729 词, 另含 5 类非极性词类), 经中文主译本移植到本项目所用的中文金融新闻语域; 该词典是本仓 6 部情感词典之一, 与本地化开发的 jiang_2021 / yao_2021 / bian_2021 / du_2022 / you_2018 并列, 共同构成固定 union 词典的成员之一。权重来源于媒体权威性度量 media_authority_weight, 由报道所属媒体的权威评级经均值归一化 (raw_authority / mean_authority) 得到, 使权重均值恒为 1, 从而加权和在总体量纲上与等权和可比。

【方法学与计算】
计算分三步。第一步在 stage 22 (tone_words) 的文章级层面, 对每篇报道用 loughran 词典逐词打分并施加全套语言学规则得净极性得分 loughran_score{track}: 该 canonical 无后缀分数并非简单的正负词裸计数比 (neg − pos)/(pos + neg), 而是由 tone_words._compute_sentiment_with_rules 对命中词依次施加否定翻转、程度副词六级放缩、转折连词 ×1.5、句末重置等规则后, 取最终逐词得分的自归一化比 Σ(final_score)/Σ|final_score|, 取值落在 [−1, 1], 无有效极性词时按缺省口径处理为缺失或零。零规则的裸计数比 (neg − pos)/(pos + neg) 另有其列 (msent_score 变体), 与本家族口径不同, 不可混同。词典加载时对 loughran 的 positive∩negative 跨类重叠词做了两阶段处理: 原始 61 个重叠词经 2026-06-24「两侧保留判断」消歧, 38 词已归单侧, 余 23 词判定为不可约简、按用户决策"保留并两侧计数" (登记入 _BOTH_SIDED_BY_DICT), 打分时对该 23 词同时计入 pos/neg, 使该词典个体的 loughran_score 净语调拉向中性而非武断选边; union/msent/ratio 等固定词典聚合测度不受影响, 因重叠词以 (+1,−1) 平衡双票喂入 build_union_dictionary, 极性 margin 守恒。第二步在面板装配 (runner 步骤3c, 媒体权威加权 MW; 与步骤3b 的提及密度加权 VW 无关) 计算 media_authority_weight = raw_authority / mean(raw_authority): 媒体名先做精确匹配、再做去括号后缀的模糊匹配, 未评级媒体赋默认权重, 全样本均值归一化保证权重中心为 1; 随后逐篇相乘得文章级加权得分 loughran_score_mw{track} = loughran_score{track} × media_authority_weight。第三步在 encode 的 bank-year 聚合中对该加权得分求和, 得本列 loughran_score_mw_sum{track}。三轨 full / ctx / ss 各自独立走完这条链路: full 轨文本 = 标题 prepend + 全文正文, ctx 轨 = 标题 + 银行/金科实体上下文窗, ss 轨 = 标题 + 银行与金科同句共现窗 (ss 无同句共现时回退镜像 ctx 语义、以全文 body 兜底并置 ss_is_fallback)。留篇门控为 full-only (2026-06-29): 一篇报道是否计入某 bank-year 的"银行金科报道"总体只看 full 轨的 llm_verified_full; ctx/ss 是 conditional-on-full 的子集测度, 行宇宙为 full 留篇集的子集, 但 per-track 分子仍逐轨照算。零新闻或该轨无留篇报道的银行-年按 Σ over ∅ = 0 落 0, 与其他权重和兄弟列保持同一"和"契约, 不残留为点号缺失。

【文献定位】
Loughran & McDonald (2011) 是本列极性判据的原始出处: 该文在《Journal of Finance》上证明通用英文情感词表 (如 Harvard IV-4) 大量误判金融/法律文本中的中性词 (如 "liability"、"tax"、"cost") 为负面, 提出面向 10-K 文本量身定制的正负词表, 是文本金融领域最广泛采用的词典之一; 本仓的中文主译本正是把这一构念移植到中文金融新闻语域, 承袭其"领域专用词表优于通用词表"的核心主张。Loughran & McDonald (2016) 在《Journal of Accounting Research》系统综述会计与金融领域文本分析方法, 讨论了词典构建、语言学规则处理 (否定、程度、转折) 与常见陷阱, 是本项目消融梯度设计 (否定翻转/程度副词/转折规则可独立开关) 的方法学依据; Loughran & McDonald (2020) 在《Annual Review of Financial Economics》进一步综述文本分析在金融研究中的应用谱系, 确认词典法作为主流方法之一的地位。就词典法与其他情感测度方法的关系, Barbaglia et al. (2025) 系统论证了在经济金融文本上词典法相对纯机器学习的可解释性与可复现优势, 并给出以词表极性合成篇章语调的规范流程, 与本列"逐词计数 → 篇章净极性 → 单元加权求和"的构造同源; van Atteveldt et al. (2021) 通过与人工标注、众包编码、机器学习的系统比对, 界定了词典法效度的边界与适用条件, 提示本列这类词典分数应作为多测度体系中的一员而非唯一真值; Frankel et al. (2022) 比较了披露文本上词典法与机器学习法的一致性, 为本项目"词典 / LLM / BERT 三法互为稳健性、不分主次"的设计提供了直接先例。Taboada et al. (2011) 奠定了词典法中否定、程度、转折等语言学规则的处理范式, 是本项目规则消融梯度的方法学背景, 与 Loughran & McDonald (2016) 的综述互为呼应。Jacobs & Lauber (2025, European Financial Management) 用词典法构造的媒体语调度量考察价格急涨前后的媒体情绪动态, 为本列以媒体权威加权词典语调刻画声量×极性合成信号提供了2023年后的方法学新近佐证。需强调本列所属的媒体权威加权仅是加权口径梯子中的一臂: MW (媒体权威权重)、VW (提及密度权)、HW (羊群衰减权) 与等权聚合各自 just-identified 并排、互为稳健性、不分主次, 严禁把不同加权口径的分子混进同一 over-identified Hansen J; 同理三轨 full/ctx/ss 亦各自 just-identified 并排、禁混同一 over-identified Hansen J, loughran 词典轨与词典家族内其余五部词典 (jiang_2021/yao_2021/bian_2021/du_2022/you_2018)、以及词典法整体与 LLM/BERT 两法之间, 同样只作互为稳健性对照而不合并识别。

## VAR: loughran_score_mw_sum_full

【变体差分】
本列是三轨中的 full (全文) 轨, 也是家族内口径最完备的一列。其求和域覆盖该 bank-year 内全部 full 轨留篇报道: full 轨文本 = 标题 prepend 到全文正文, 因此 Loughran & McDonald 中文主译本词典的正负词计数扫描的是完整报道体裁, 净极性得分 loughran_score_full 基于全文语义, 再乘以媒体权威权重、在 bank-year 内求和得本列。与 ctx / ss 两轨相比, full 轨是留篇门控 (2026-06-29 full-only) 的判定轨: 一篇报道是否计入某 bank-year 的银行金科报道总体只看 full 轨的 llm_verified_full, 因此 full 轨的求和域即行宇宙本身, 而 ctx/ss 求和域是它的子集。这使本列在数值稳定性上通常强于 ctx/ss (分母基更大、退化格更少)。作为加权求和的分子, 本列须与同轨的媒体权威权重和 sum_media_authority_weight_full 配对使用方得加权均值语调 loughran_tone_mw_full; 单独看本列是"极性 × 声量"的运行和, 量纲随该单元报道条数与权威分布浮动, 不可直接跨单元比水平。与等权求和分子 (无 _mw 中缀) 相比, 本列仅在权重维度不同: 前者隐含权威权重恒为 1, 本列以媒体权威权重加权, 二者作为加权口径梯子的两臂互为稳健性、不分主次, 禁混同一 over-identified Hansen J。因媒体权威权重经均值归一化 (中心恒为 1), 本列与等权分子在总体量纲上可比, 差异纯粹来自权威分布的偏斜 — 当高权威媒体的报道极性系统性偏正或偏负时, 本列相对等权分子放大该方向的信号, 这正是媒体权威加权口径的经济含义所在: 让声量更大、可信度更高的媒体在语调合成中占更重份额。Loughran & McDonald 词典相对本仓其余五部本地化词典更偏保守 (negative 词表远大于 positive, 3,729 对 1,295), 因此本列的绝对水平常比同 bank-year 下 jiang_2021/bian_2021 等词典的对应 mw_sum 更偏负, 这一系统性差异属词典构念差异, 不是加权口径造成, 使用时应留意跨词典比较须先标准化。

## VAR: loughran_score_mw_sum_ctx

【变体差分】
本列是三轨中的 ctx (实体上下文窗) 轨。其与 full 轨的唯一区别在于极性判定所扫描的文本范围: ctx 轨文本 = 标题 prepend + 银行/金科实体的上下文窗口 (由 config 的 context_window 控制), 而非全文正文, 因此 Loughran & McDonald 中文主译本词典只在实体邻近语境内统计正负词, 净极性得分 loughran_score_ctx 反映的是"围绕目标银行与金融科技实体的局部语调", 对远离实体的题外极性词不敏感。随后乘以媒体权威权重 (权重本身与轨无关, 恒取自报道所属媒体)、在 bank-year 内求和得本列。口径上须注意: ctx 轨是 conditional-on-full 的稳健性/子集轨 (2026-06-29 full-only 门控), 其求和域是 full 留篇集的子集 — 只有 full 轨已判为留篇的报道才可能进入 ctx 轨求和, 且该报道须有实体上下文窗可扫。在开发期 T=2 小样本上 ctx 轨可能出现较多退化格, 属预期。本列与 full 轨、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨分子混进同一 over-identified Hansen J; 与等权 ctx 分子相比仅权重维度不同, 同属加权口径梯子并排臂。作为加权均值语调 loughran_tone_mw_ctx 的分子, 本列须与 ctx 轨自身的权威权重和配对, 不可借用 full 轨分母。ctx 轨的设计意图是抑制远离目标实体的题外极性噪声: 一篇报道纵然全文语调偏正, 只要银行与金科实体所在段落语调中性, ctx 轨得分即趋近中性, 从而使本列相对 full 轨对"银行金科局部叙事"更敏感、对全文背景极性更钝感, 二轨的这一系统性差异本身即构成对语调测度稳健性的检验维度。Loughran & McDonald 词表以金融专业术语的语境化极性判定见长 (如区分中性财务用语与真正的负面披露信号), 在实体窗收窄后, 这一领域专用性优势更集中体现在紧邻银行/金科实体的表述上, 使本列相对通用词表构造的同轨列理论上更贴合本项目"金融科技对银行影响"的构念目标。

## VAR: loughran_score_mw_sum_ss

【变体差分】
本列是三轨中的 ss (同句共现窗) 轨, 口径最严。其极性判定所扫描的文本 = 标题 prepend + 目标银行与金融科技词在同一句内共现的窗口 (半径由 config filtering.yaml 的 context_window.ss_sentence_radius 控制, 默认 ±1 句), 因此 Loughran & McDonald 中文主译本词典只在"银行与金科真正同句共现"的最紧邻语境内统计正负词, 净极性得分 loughran_score_ss 捕捉的是银行-金科直接关联处的局部语调, 对仅在文中他处分别出现银行与金科而不同句的报道给予最弱信号。关键回退语义: 当某报道无银行与金科的同句共现时, ss 轨镜像 ctx 轨语义、以全文 body 兜底并置 ss_is_fallback=True (与 ctx 共享 n_articles 分母), FINTECH_AC 为空时 *_is_fallback 全 True 作优雅降级 — 此回退口径与 CLAUDE.md 三轨铁律一致, 不得写成"同句无共现即丢行"。随后乘以媒体权威权重、在 bank-year 内求和得本列。同 ctx 轨, ss 轨是 conditional-on-full 的子集/稳健性轨, 求和域为 full 留篇集子集。在 T=2 开发样本上 ss 轨常出现零方差或大量回退, 属预期退化, 生产期 T=19 恢复正常。本列与 full、ctx 各自 just-identified 并排、互为稳健性、不分主次, 禁混同一 over-identified Hansen J; 作为分子须与 ss 轨自身权威权重和配对得 loughran_tone_mw_ss。ss 轨是三轨中信噪取舍最激进的一端: 它以牺牲样本覆盖 (大量报道回退) 换取语义精确性, 只在银行与金科真正同句处采信极性信号, 因此本列相对 full/ctx 分子对"银行与金融科技直接关联事件"的语调最为敏感; 在稳健性叙事中, 若主结论在 full、ctx、ss 三轨分子上定性一致, 即说明结论不被文本窗口口径的松紧所驱动, 也不被 Loughran & McDonald 相对保守的正负词比例结构性驱动。

<!-- rendered-citations:begin -->
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance: A survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Loughran, T., & McDonald, B. (2020). Textual analysis in finance. Annual Review of Financial Economics, 12(1), 357-375. https://doi.org/10.1146/annurev-financial-012820-032249
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
Jacobs, H., & Lauber, A. (2025). Media Sentiment and Price Run-Ups. European Financial Management. https://doi.org/10.1111/eufm.70025
<!-- rendered-citations:end -->
