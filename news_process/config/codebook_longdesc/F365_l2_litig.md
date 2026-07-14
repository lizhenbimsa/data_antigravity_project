---
family_id: F365
columns:
- litig_frac_ctx
- litig_frac_full
- litig_frac_ss
unit: 比率/占比 (proportion, [0,1] 区间; 词频数除以该轨文本总词数, 未乘百分号)
formula: 'litig_frac_{trk} = count(litigious 词命中数, content_{trk}) / count(该轨分词后剔除纯数字与标点 token 的真词数, content_{trk}); {trk} ∈ {full, ctx, ss}'
producer: pipeline\sentiment\lm_non_sentiment.py ; pipeline\sentiment\tone_words.py
upstream:
- 14_materialize_ctx (content_full/content_ctx/content_ss 三轨文本物化)
- config/codebook_longdesc/tone_dicts.json (Loughran-McDonald 中文译本 litigious 子词典)
citations:
- doi: 10.1111/j.1540-6261.2010.01625.x
  type: journal
  authors: Loughran, Tim; McDonald, Bill
  year: 2011
  title: When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks
  venue: The Journal of Finance
  vol: '66'
  issue: '1'
  pages_or_artno: 35-65
- doi: 10.1111/1475-679X.12123
  type: journal
  authors: Loughran, Tim; McDonald, Bill
  year: 2016
  title: 'Textual Analysis in Accounting and Finance: A Survey'
  venue: Journal of Accounting Research
  vol: '54'
  issue: '4'
  pages_or_artno: 1187-1230
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Chao; et al.
  year: 2022
  title: Dictionary-based textual sentiment and political-word weighting in Chinese financial text
  venue: Review of Finance
  pages_or_artno: n/a
new_dois: []
---

## CORE

【构念与来源】
litig_frac 家族衡量一篇报道文本中"诉讼/监管风险"语义词的出现密度, 是 Loughran & McDonald (2011) 提出的 LM 2011 JF 十大类中文本情绪与语用子词典体系里 litigious (诉讼类) 一支在本项目里的中文实现。LM 2011 的核心洞察是: 通用情绪词典 (如 Harvard-IV Psychosociological Dictionary) 里被标记为"负面"的很多词, 在 10-K 之类的正式监管文书语境里并不承载真实的负面情绪信号 (例如 "tax"、"cost"、"liability" 本身是中性财务术语而非负面情绪词); 与之对称, 作者进一步细分出若干"语用类别"子词典, 其中 litigious 子词典专门刻画文本中涉及诉讼、法律纠纷、监管处罚、合规风险的措辞密度, 用以捕捉企业/机构面临的法律与监管不确定性, 而非情绪褒贬本身。本项目在 v3.5.2 PR #3 (与 forward_looking.py A2 FLS 同一 sprint) 把 LM 非情绪六子词典 (uncertainty / litigious / constraining / modal_strong / weak_modal / complexity) 移植进中文语境, v3.10.0 由原 4 类扩到现 6 类 (新增 weak_modal 与 complexity)。litig_frac 对应其中 litigious 一支: 词典源自 LM 2011 英文原始词表的中文译本 (载于 tone_dicts.json), 经人工审校纳入涉诉、涉罚、涉诉讼程序 (起诉、仲裁、罚款、整改、监管函、行政处罚等) 相关的中文词条。
在项目整体测度体系里, litig_frac 属于"词典法"三支柱之一 (LLM 三家投票 / 词典法 / BERT 三模型), 但它本身并不参与主情绪 (tone) 的褒贬打分, 而是作为一组独立的、非情绪的文本属性度量, 与 uncert_frac (不确定性)、constr_frac (约束语气)、modal_strong_frac / modal_weak_frac (强/弱模态动词)、complexity_frac (语言复杂度) 共同构成一套"文本风险语用画像"。这组画像的价值在于: 当一篇报道同时提及某银行与某金融科技合作事项时, 文本里涉诉/监管措辞的密度可以作为潜在合规摩擦、监管审查压力、法律纠纷风险的代理变量, 补充纯情绪打分无法捕捉的语用维度; 在稳健性检验里也常被用作控制变量, 排除"报道语气负面"是否单纯由诉讼类新闻带来的机械混淆。
【方法学与计算】
计算流程集成在 `pipeline.sentiment.tone_words::_dual_analyze` 内: 该函数对每篇文章的三段候选文本 (content_full / content_ctx / content_ss) 各调用一次 `lm_non_sentiment.py::_compute_lm_non_sentiment_for_text`, 该底层函数本身是 track-agnostic 的纯文本处理函数 (不知道自己在处理哪一轨), 三轨差异完全由调用方喂入哪一段文本决定, 模块本身无需为多轨改动。处理链路为: 先用 jieba (冻结版本 0.42.1, 确定性锚点) 对输入文本分词, 再逐词与 litigious 中文词典做精确匹配计数; 分母并非分词后的全部 token 数, 而是先用 `_LMFLS_NONWORD_RE` 剔除纯数字与标点 token 后剩下的"真词" token 数 (`word_tokens`/`n_tokens`), 命中数除以该真词数得到 litig_frac_{trk}。这一分母口径的历史修正见 `lm_non_sentiment.py` fix(lmfls-01, metric-audit 2026-06-10) 注释: 原实现分母含约 19% 的标点/纯数字 token, 相当于把"蛋糕"做大却没多放"料", 导致 uncert/litig/constr/modal_strong 四个 frac 系统性下偏; 修正后分母只数真正的词, 分子 (命中计数) 本身不受影响 (标点/数字本就不可能命中词典词)。数值域理论上落在 [0,1] 区间且通常远小于 1 (诉讼类措辞在新闻文本中是稀疏事件)。词典本身按语言学规则做过否定翻转/程度副词/转折三项规则的消融处理 (`_RULE_ABLATION_VARIANTS`), 但 litig_frac 是频次占比型测度而非褒贬打分型测度, 不参与该消融梯度 (消融梯度仅作用于情绪极性词典, 不作用于 LM 六个非情绪语用子词典)。三轨文本口径遵循全仓统一定义: full = 标题 + 全文正文 (prepend_title 拼接); ctx = 标题 + 目标银行实体所在句 ±1 句窗口; ss = 标题 + 目标银行∧金科词同句共现窗口 (窗口半径见 `config/filtering.yaml::context_window.ss_sentence_radius`, 默认 1)。当一篇文章不存在银行∧金科同句共现时, content_ss 按镜像 ctx 的回退语义退化为全文 body, 对应 `ss_is_fallback=True`, 此时 litig_frac_ss 是在全文文本上计算而非在真正的共现窗口上计算, 下游聚合到面板层时仍共享同一 n_articles 分母, 不做单独剔除。三轨 (full/ctx/ss) 之间是互为稳健性、不分主次的并排关系: 各轨各自作为一个 just-identified 测度独立进入下游回归, 禁止把 full/ctx/ss 三个版本的 litig_frac 混入同一个 over-identified 的 Hansen J 过度识别检验框架 (三个版本本质是对同一构念的三种文本范围口径, 混用会人为制造工具冗余而非增加识别力度)。
【文献定位】
LM 2011 (Loughran & McDonald 2011, Journal of Finance) 是文本情绪与语用词典法在金融/会计文献里的奠基性工作, 首次系统证明通用情绪词典直接套用在正式监管文书上会产生系统性误判, 并按语用功能拆分出包括 litigious 在内的多个专门子词典; 该文原始语料为美国 10-K 年报, 本项目将其移植到中文新闻语境, 是一次跨语言、跨文本类型 (年报 → 新闻报道) 的方法迁移。Loughran & McDonald (2016, Journal of Accounting Research) 是同一研究团队对文本分析方法在会计与金融领域应用的系统性综述, 总结了词典法的适用边界、常见陷阱 (如未做否定翻转导致的方向性误判) 与验证策略, 为本项目在中文语境下沿用词典法并辅以三条语言学规则 (否定/程度/转折) 提供方法学依据。Du et al. (2022, Review of Finance) 讨论的是中文金融文本情绪词典构建中"政治词"类别权重的敏感性问题 (本项目在政治词权重梯度 {0.0, 0.5, 1.0} 上直接沿用其思路), 该文原文针对的是情绪极性词的类别加权而非 litig_frac 这类非情绪语用子词典; 此处引用属于类比性引注而非文献原文结论的直接套用 (原文并未讨论 litigious 子词典的跨语言覆盖度问题) — 类比的落点在于: Du et al. 强调词典类别权重/覆盖度选择需做敏感性披露而非武断取单一值, 这一方法论态度同样应当延伸到理解 litig_frac 在跨语言移植时的效度边界。具体而言, 词典覆盖度、中文法律/监管术语的多样表达 (如"约谈"“责令整改"“立案调查"等非西方法律体系直译词) 未必与英文原始词表逐一对应, 使用者在解读该测度的绝对水平时应保持审慎, 更适合做跨时间/跨样本的相对比较而非绝对阈值判断。

## VAR: litig_frac_full

【变体差分】
litig_frac_full 是家族的 canonical 轨, 输入文本 content_full = 标题 + 全文正文 (prepend_title 拼接), 不做任何银行实体窗口或银行∧金科共现窗口的裁剪。分母 (总词数) 覆盖全文所有分词 token, 因此该列反映的是"整篇报道"层面涉诉/监管措辞的密度, 既包含直接谈论目标银行与金融科技合作的段落, 也包含报道里与目标银行无直接关系但同处一篇文章的背景性法律/监管叙述 (例如整篇报道同时报道了行业监管新规, 而目标银行只是被提及的多家机构之一)。这一特性使 litig_frac_full 在信息量上更完整, 但也更容易被文章中与目标实体无关的诉讼类内容稀释或抬高, 因此在需要精确刻画"目标银行本身"的涉诉语境密度时, 应参照 litig_frac_ctx / litig_frac_ss 两个窗口化轨作为稳健性对照, 三者互为稳健性、不分主次、各自 just-identified, 不可混入同一 Hansen J 过度识别框架。留篇门控口径 (2026-06-29 起) 仅看 `llm_verified_full == True`, litig_frac_full 所在的 full 轨是唯一决定"是否算作一篇有效银行金科报道"的判据轨, ctx/ss 两轨在留篇意义上是 conditional-on-full 的测度/稳健性轨, 行宇宙是 full 留篇集合的子集。由于 full 轨判定门控地位, litig_frac_full 在 P1 (bank_fintech_tone) 与 provisional bank_news_clarity 等主线论文里, 即便主处理变量 (treatment) 用的是情绪打分而非本列, litig_frac_full 依然常被纳入稳健性/控制变量集合, 用来排除"报道语气偏负是否单纯由该篇报道恰好属于涉诉/监管类新闻"这一混淆渠道; 尤其在样本里银行与金融科技合作被媒体负面报道时, 相当一部分负面语气本质上来自诉讼/处罚事实陈述而非评价性情绪用语, litig_frac_full 提供了区分"事实性涉诉密度"与"评价性情绪极性"两个维度的手段。该列与 uncert_frac_full / constr_frac_full / modal_strong_frac_full / modal_weak_frac_full / complexity_frac_full 同属 LM 六子词典家族的 full 轨兄弟列, 彼此测的是不同语用维度而非同一构念的替代测量, 不应被误当作可以互相替换的同族变体。

## VAR: litig_frac_ctx

【变体差分】
litig_frac_ctx 的输入文本 content_ctx = 标题 + 目标银行实体所在句 ±1 句窗口 (窗口半径由 `config/filtering.yaml::context_window` 相关键控制), 在 stage 14 `ctx_materializer` 物化, 不含无关段落的稀释。相对 litig_frac_full, 该列把统计范围收窄到与目标银行实体直接相邻的语境, 因此更贴近"该银行本身是否处于涉诉/监管风险叙述之中"的构念, 代价是样本文本量更小、噪声方差可能更高 (尤其当目标银行在文中仅被提及一两句时)。分母同样是该轨 (content_ctx) 内部的总分词数, 而非 full 轨分母, 三轨严格各自归一化、不共享分母。litig_frac_ctx 与 litig_frac_full/litig_frac_ss 是并排稳健性轨, 禁止混入同一 Hansen J; 与其它 P1-P5 论文轨一致, ctx 轨在留篇门控切至 full-only (2026-06-29) 后降级为 conditional-on-full 的测度轨, 行宇宙是 full 留篇集合的子集, 但 litig_frac_ctx 本身的计算逻辑 (词典命中计数/分词分母) 不因此改变, 仅受影响的是哪些文章行会出现在该列非缺失的样本中。ctx 窗口的实体判定原语是 `entity_context.py` 里逐句扫描目标银行是否出现 (含否定/短名过滤规则), 与 stage 13 共现硬过滤所用的邻近共现判据同源但不完全等价 (stage 13 是行级硬过滤保留/丢弃整篇文章, litig_frac_ctx 是在已保留文章内部选取用于统计的句子子集, 两者作用层级不同)。在解读上, litig_frac_ctx 相对 litig_frac_full 的边际价值在于剔除文章里与目标银行完全无关的诉讼/监管背景段落 (例如报道行业整体监管新规时提到多家机构), 使该列更适合作为"该银行本身涉诉密度"的窄口径代理; 但由于窗口更窄, 命中词计数的绝对样本量更小, 在稀疏事件 (诉讼类措辞本就低频) 场景下零命中行的比例通常高于 full 轨, 使用者在做跨样本比较时应留意零膨胀分布特征而非直接套用连续变量的常规诊断。

## VAR: litig_frac_ss

【变体差分】
litig_frac_ss 的输入文本 content_ss = 标题 + 目标银行∧金科词同句共现的句子 ±N 句窗口 (N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 控制, 默认 1), 是三轨中范围最窄、判据最严格的一支: 只有当同一句子里同时出现目标银行实体与金融科技相关词时, 该句 (及其邻近窗口) 才会被纳入统计。当一篇文章不存在银行∧金科同句共现时, content_ss 按镜像 ctx 的回退语义退化为全文 body 计算 (与 litig_frac_full 在该行的取值来源相同但语义标记不同), 对应的 `ss_is_fallback` 指示列置 True, 说明该行 litig_frac_ss 并非真正在"同句共现窗口"上算出, 使用该列做窄口径解读时应先按 ss_is_fallback 过滤或至少披露回退比例; 当 `FINTECH_AC` (金科词自动机) 为 None 时, 全体行的 `*_is_fallback` 均降级为 True, 此时 litig_frac_ss 在数值上等同于 litig_frac_full。litig_frac_ss 与 litig_frac_ctx / litig_frac_full 三者并排、互为稳健性、各自 just-identified, 禁止混入同一 Hansen J 过度识别检验; 在留篇门控切至 full-only 之后, ss 轨与 ctx 轨同样降级为 conditional-on-full 的测度/稳健性轨, 行宇宙受限于 full 轨的留篇集合, 但底层"同句共现→分词→litigious 词典命中计数→除以该轨总词数"的计算规则本身与家族其余两轨一致, 不额外引入新的判据类型 (与 stage 13 共现硬过滤的 sentence_radius=1 判据是相近但独立的两个配置键, 不可混用)。

<!-- rendered-citations:begin -->
Loughran, Tim; McDonald, Bill. (2011). When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Loughran, Tim; McDonald, Bill. (2016). Textual Analysis in Accounting and Finance: A Survey. Journal of Accounting Research, 54(4), 1187-1230. https://doi.org/10.1111/1475-679X.12123
Du, Chao; et al. (2022). Dictionary-based textual sentiment and political-word weighting in Chinese financial text. Review of Finance, n/a. https://doi.org/10.1093/rof/rfab036
<!-- rendered-citations:end -->
