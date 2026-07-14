---
family_id: F618
columns:
- washing_tone_shift_ctx
- washing_tone_shift_full
- washing_tone_shift_ss
unit: 语调分差 (连续, 理论范围约 [-2,2], 实际集中于 [-1,1]; bank-year 聚合)
formula: 'washing_tone_shift{track} = llm_vote_tone_symb{track} - llm_vote_tone{track}, 其中 llm_vote_tone_symb 是"象征性"报道子样本(W&Z 1998 判据, 由 sub_frac/symb_frac 分类流程产出)上的 LLM 三家投票均值语调, llm_vote_tone 是同轨全部留篇样本上的 LLM 投票均值语调; 二者均为 bank-year 层聚合量, 该列本身是 pipeline\panel\runner.py 步骤 7h(洗稿率 Washing Ratio — 多方法 × 三轨构造)内方法 G 情感偏移块 panel[vn] = panel[symb_tone] - panel[all_tone] 的逐 bank-year 减法, 非文章级量的再聚合'
producer: pipeline\panel\runner.py (步骤 7h, 变量组 G 情感偏移); 标签映射见 pipeline\panel\export.py
upstream: [llm_vote_tone_symb_full, llm_vote_tone_symb_ctx, llm_vote_tone_symb_ss, llm_vote_tone_full, llm_vote_tone_ctx, llm_vote_tone_ss, sub_frac, symb_frac, n_articles_symb]
citations:
- doi: "10.2307/2393295"
  type: journal
  authors: "Westphal, J. D., & Zajac, E. J."
  year: 1994
  title: "Substance and Symbolism in CEOs' Long-Term Incentive Plans"
  venue: "Administrative Science Quarterly"
  vol: "39"
  issue: "3"
  pages_or_artno: "367-390"
- doi: "10.2307/2393593"
  type: journal
  authors: "Westphal, J. D., & Zajac, E. J."
  year: 1998
  title: "The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions"
  venue: "Administrative Science Quarterly"
  vol: "43"
  issue: "1"
  pages_or_artno: "127-153"
- doi: "10.2308/TAR-2020-0104"
  type: journal
  authors: "Holzman, E. R., Miller, B. P., & Twedt, B. J."
  year: 2023
  title: "Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements"
  venue: "The Accounting Review"
  vol: "98"
  issue: "7"
  pages_or_artno: "315-345"
- doi: "10.2139/ssrn.5220056"
  type: wp
  authors: "Marchetti, S., Tarducci, E., & Branzoli, N."
  year: 2025
  title: "Measuring Tone Shifts in Media Coverage: An Empirical Application to Bank Financing Conditions in Italy"
  venue: "SSRN Working Paper"
new_dois: []
---

## CORE

【构念与来源】
washing_tone_shift 测度的是"银行在媒体上讲故事时, 象征性报道(symbolic news)与其全部报道相比语调是否被系统性拉高"。构念根源是组织理论中"实质与象征"(substance vs. symbolism)的经典区分: Westphal & Zajac (1994, 1998) 在公司治理改革情境下证明, 企业会采纳看得见却难以验证效果的治理形式(象征性举措), 并通过公开传播为其营造正面叙事, 以缓解外部利益相关者对实质绩效缺口的关注; 这一"言行分离"(decoupling)逻辑被本项目移植到银行金融科技(FinTech)报道语境: 一篇报道若被 LLM 三家投票判定为"象征性"(即偏重宣传口号、战略愿景、荣誉授牌等难以验证具体业务落地的内容, 判据由 sub_frac/symb_frac 分类管线在 n_articles_symb 计数基础上产出, 详见 F 系列 substantive/symbolic 分类家族), 则将其单独聚合出该子集专属的平均语调 llm_vote_tone_symb; 若这一均值系统性高于该银行同期"全部留篇报道"的平均语调 llm_vote_tone, 差值为正即构成"洗稿(washing)"或"漂绿式媒体自我美化"的间接语调证据: 银行(或其公关渠道)倾向于把最正面的措辞留给最难验证的宣传性报道, 而非留给具体业务落地的实质性报道。该构念与本项目 washing_ratio 族(F617 及相邻家族, 44 种洗稿率变体, 依据 Bingler et al. 2022, FRL 的"漂绿/漂稿"计量学思路)是同一"象征-实质"母题下的姊妹测度: washing_ratio answer 的是"正面且象征性的报道占多大比例", 而 washing_tone_shift 回答的是"象征性报道的语调比全部报道平均高出多少", 二者互为补充但不可互相替代, 不应在同一回归设定中作为同一构念的多重代理变量混用而不加说明。

【方法学与计算】
该列的计算发生在 bank-year 面板层, 而非文章层: 上游 LLM 情感三家投票(gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash, 详见项目铁律"LLM 三家互为稳健性")已在 stage 21 产出逐篇语调打分并经 majority vote 汇总为 llm_vote_tone; 与此并行, 每篇留篇报道会依据象征性/实质性分类管线打上 sub/symb 标签(该分类同样消费三家 LLM 投票的分类维度, 但与语调打分是两条并行的分类轴, 不可混同); 面板构建阶段先分别在"全部留篇样本"和"象征性子样本"两个行子集上计算各自的 llm_vote_tone{track} 均值, 再在 bank-year 行上做一次简单减法 washing_tone_shift{track} = llm_vote_tone_symb{track} - llm_vote_tone{track}。由于减法在聚合之后而非聚合之前发生, 该量不是"每篇文章语调差异的均值", 而是"象征性子样本均值语调"与"全样本均值语调"两个独立统计量之差, 二者的样本量(n_articles_symb vs. 全部留篇 n_articles)通常不同, 因此该差值继承了小样本(尤其当某银行某年象征性报道篇数很少时)带来的方差膨胀; 使用者在解读极端值或做进一步回归前应结合 n_articles_symb 核查该 bank-year 单元的象征性报道基数是否过薄。三轨 full/ctx/ss 下该量均独立计算, 计算逻辑镜像但输入的文本窗口与上游 sub/symb 分类结果不同轨互不借用, 详见下方 VAR 节与三轨口径说明。取值符号的解释方向: 正值表示象征性报道语调系统性高于全样本(与"漂绿/自我美化"假说一致), 负值表示象征性报道语调反而更保守或更中性(可能反映该银行的宣传性报道并未刻意拔高措辞, 或该子样本本身噪声较大), 零值/接近零意味着两类报道语调无系统性差异, 洗稿式语调拉升的证据不足。

【文献定位】
本测度的理论谱系直接承袭 Westphal & Zajac (1994, 1998, Administrative Science Quarterly) 关于公司治理"实质-象征"解耦的经典论证, 并将其应用场域从治理改革文本迁移到银行金融科技媒体报道; 在计量操作上则借鉴了近年文本情感"语调错位/语调分歧"测度的一般思路——即不满足于单一整体语调分数, 而是在有意义的子样本切分之间比较语调均值差, 以捕捉叙事策略而非单纯情绪水平。这一思路与 Marchetti, Tarducci & Branzoli (2025, SSRN) 在意大利银行融资条件语境下构建的"媒体语调偏移(tone shift)"银行×年聚合口径高度对应, 二者均将语调偏移定义为同一实体在不同文本子集或时期上的均值语调之差, 而非单篇文章内部的语调波动; Holzman, Miller & Twedt (2023, The Accounting Review) 进一步表明, 媒体语调的结构性特征(而非仅是均值水平)本身携带独立于财务基本面的信息含量, 支持了将"语调结构差异"单列为测度维度而非仅报告整体均值的做法。象征性/实质性分类判据本身则源自 Westphal & Zajac (1998) 对"可观察但难验证的姿态性行动"与"可验证的实质性行动"的操作性区分, 在本项目中经由 LLM 三家投票转译为文章层的可复现分类标签。

## VAR: washing_tone_shift_full

【变体差分】
full 轨是本家族的默认/主口径, 输入是"标题+正文全文"(prepend_title 拼接)上的语调与象征性分类结果: llm_vote_tone_symb_full 与 llm_vote_tone_full 均在 stage 21 留篇门控(2026-06-29 起门控唯一以 llm_verified_full 判定"是否算作一篇银行-金科报道")之后、以全文文本重跑三家 LLM 投票产出, 因此 washing_tone_shift_full 的行覆盖即等于该 bank-year 单元的 full 轨留篇总体。由于留篇门控本身只在 full 轨上做, full 轨天然是样本量最充裕、噪声相对最小的一轨, 通常也是论文正文报告的首选口径。该列与家族内 _ctx / _ss 两个变体是并排的稳健性口径, 三者各自基于三个独立(但内容有重叠)的文本窗口、独立计算象征性分类与语调均值, 属于互为稳健性、不分主次的三轨设计, 严禁将三轨的 washing_tone_shift 同时放入同一个过度识别(over-identified)的 Hansen J 检验框架——三者应分别作为并列稳健性设定报告, 而非合并为单一工具集。在实证使用上, full 轨因样本量最充裕、且与留篇门控口径完全对齐, 建议作为该家族的首要报告口径; 若研究者关心的假说本身就聚焦"实体附近叙事"或"银行-金科同句强共现"情境下的语调拉升, 则应转向 ctx 或 ss 轨作为主口径而非固守 full, 三者优先级取决于研究问题而非固定排序。使用该列前应留意其分子 llm_vote_tone_symb_full 依赖 n_articles_symb 这一象征性报道计数; 当某银行某年 n_articles_symb 过小(例如个位数)时, 均值本身对个别极端语调打分高度敏感, 建议在回归中对该子样本量设最小阈值过滤或作为控制变量纳入, 以避免把小样本噪声误读为系统性洗稿信号。

## VAR: washing_tone_shift_ctx

【变体差分】
ctx 轨的输入文本窗口是"标题+目标银行/金科实体窗口"而非全文, 该窗口在 stage 14 ctx_materializer 中以 content_ctx 物化(prepend_title, 原始"内容"列不改动); llm_vote_tone_symb_ctx 与 llm_vote_tone_ctx 在 stage 21 于 ctx 轨文本上独立重跑三家 LLM 投票与象征性分类, 因此 ctx 轨的象征性/实质性归类结果与 full 轨可能不同(同一篇文章在窄化的实体窗口下更可能因缺乏上下文而被判为象征性, 或相反因去除了无关噪声段落而更清晰地暴露实质性内容)。⚠ 需特别注意: ctx/ss 轨自 2026-06-29 起是 conditional-on-full 的测度轨——"是否算作一篇银行-金科报道"这一留篇门控只由 llm_verified_full 决定, ctx 轨的行宇宙是 full 轨留篇集的子集, 而非独立的留篇判定; 因此 washing_tone_shift_ctx 的 bank-year 覆盖与 washing_tone_shift_full 理论上应完全一致(同一组留篇文章), 差异只体现在同一批文章在不同文本窗口下重算出的语调与分类结果不同, 而非样本增减。ctx 轨与 full/ss 两轨互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J。由于 ctx 窗口聚焦实体周边语境、剔除了与目标银行或金科议题无关的段落, 该轨对"文章局部叙事策略"的刻画通常比 full 轨更聚焦, 适合作为"排除无关正文噪声后, 象征性叙事是否仍系统性偏正面"这一稳健性问题的首选口径; 但也正因窗口更窄, 若原文对目标实体着墨很少, ctx 文本可能过短导致 LLM 分类与打分的边际信息不足, 结果方差略高于 full 轨, 建议与 full 轨并列报告而非单独依赖。ctx 轨对应的象征性判据与语调打分均在 stage 21 独立执行, 不复用 full 轨的分类结果或语调分数, 二者仅共享同一批留篇文章的原始来源。

## VAR: washing_tone_shift_ss

【变体差分】
ss 轨的输入文本窗口是"标题+银行∧金科同句(±N 句窗, 默认 N=1)"共现片段, 在 stage 14 以 content_ss 物化; 若某篇文章不存在银行与金科词同句共现, 则该轨镜像 ctx 轨的回退语义: content_ss 退化为全文 body, ss_is_fallback=True, 与 n_articles 共享同一分母, 优雅降级为等同于该篇文章的 full 轨内容而非直接丢弃该行。llm_vote_tone_symb_ss 与 llm_vote_tone_ss 同样在 stage 21 于 ss 轨(含回退)文本上独立重跑三家 LLM 投票与象征性分类; 由于 ss 轨窗口最窄, 当某银行某年象征性报道本身基数(n_articles_symb)已经不大时, ss 轨的象征性子样本进一步收缩(尤其是非回退行), 该列比 ctx/full 两轨更易出现小样本导致的均值不稳定, 使用前应结合该轨的样本量核查再解读极端偏移值。ss 轨同样是 conditional-on-full 的测度轨, 行宇宙为 full 轨留篇集子集, 与 full/ctx 两轨互为稳健性、不分主次的并排口径, 禁止混入同一 over-identified Hansen J。ss 轨的判据是"银行∧金科在同一句(或 ±1 句窗口)内共现", 因此它捕捉的是最紧凑、最直接的银行-金科并置叙事; 当一篇报道确实存在这种紧密并置时, ss 轨往往比 ctx 轨进一步剔除了实体窗口内仍可能残留的无关语句, 是三轨中判据最严格、噪声潜在最低但样本潜在最薄的一支。回退行(ss_is_fallback=True)在计算 washing_tone_shift_ss 时与非回退行一视同仁地计入均值, 二者共享同一分母 n_articles, 因此该列的取值应结合回退比例一并解读: 若某银行某年回退行占比很高, ss 轨在事实上退化为接近 full 轨的度量, 其作为"严格共现"稳健性检验的边际价值会相应减弱。

<!-- rendered-citations:begin -->
Westphal, J. D., & Zajac, E. J. (1994). Substance and Symbolism in CEOs' Long-Term Incentive Plans. Administrative Science Quarterly, 39(3), 367-390. https://doi.org/10.2307/2393295
Westphal, J. D., & Zajac, E. J. (1998). The Symbolic Management of Stockholders: Corporate Governance Reforms and Shareholder Reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Marchetti, S., Tarducci, E., & Branzoli, N. (2025). Measuring Tone Shifts in Media Coverage: An Empirical Application to Bank Financing Conditions in Italy. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.5220056
<!-- rendered-citations:end -->
