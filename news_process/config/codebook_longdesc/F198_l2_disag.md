---
family_id: F198
columns:
- disag_ctx
- disag_full
- disag_ss
unit: 无量纲分歧指数 (取值域 [0, 1])
formula: "disag = sqrt(1 - ((P - N) / (P + N))^2); 其中 P = avg_pos_ratio (银行-年度对篇章级正面词占比 pos_ratio 取的均值), N = avg_neg_ratio (银行-年度对篇章级负面词占比 neg_ratio 取的均值), 逐轨; P + N = 0 (两轨平均正负面词占比同为 0) 时置 NaN"
producer: news_process/pipeline/panel/runner.py (步骤 8b disag, (a) 词典综合分支, 输入 avg_pos_ratio / avg_neg_ratio) ; news_process/pipeline/panel/encode.py (逐轨 avg_pos_ratio{track} / avg_neg_ratio{track} = 对 pos_ratio / neg_ratio 取 bank-year mean)
upstream:
- 24_herd_decay.parquet (article×bank verified 精筛集, 逐轨聚合分母来源)
- 22_tone_words.parquet (union 词典逐篇 pos_ratio / neg_ratio = 正/负面词计数 ÷ word-token 数)
citations:
- doi: 10.1007/s11142-025-09897-1
  type: journal
  authors: Li, S. Z., & Luan, Z.
  year: 2025
  title: "News-based investor disagreement and stock returns"
  venue: Review of Accounting Studies
  vol: 30
  issue: 3
  pages_or_artno: 2312-2375
- doi: 10.1016/j.jfineco.2021.05.060
  type: journal
  authors: Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M.
  year: 2022
  title: "Network effects in corporate financial policies"
  venue: Journal of Financial Economics
  vol: 144
  issue: 1
  pages_or_artno: 247-272
- doi: 10.1613/jair.1.12752
  type: journal
  authors: Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M.
  year: 2021
  title: "Learning from disagreement: A survey"
  venue: Journal of Artificial Intelligence Research
  vol: 72
  issue: ""
  pages_or_artno: 1385-1470
- doi: 10.1111/jofi.12852
  type: journal
  authors: Cookson, J. A., & Niessner, M.
  year: 2020
  title: "Why don't we agree? Evidence from a social network of investors"
  venue: The Journal of Finance
  vol: 75
  issue: 1
  pages_or_artno: 173-228
- doi: 10.1287/mnsc.2015.2405
  type: journal
  authors: Cen, L., Wei, K. C. J., & Yang, L.
  year: 2017
  title: "Disagreement, underreaction, and stock returns"
  venue: Management Science
  vol: 63
  issue: 4
  pages_or_artno: 1214-1231
- doi: 10.1016/j.jfineco.2014.06.007
  type: journal
  authors: Carlin, B. I., Longstaff, F. A., & Matoba, K.
  year: 2014
  title: "Disagreement and asset prices"
  venue: Journal of Financial Economics
  vol: 114
  issue: 2
  pages_or_artno: 226-238
- doi: 10.1257/jep.21.2.109
  type: journal
  authors: Hong, H., & Stein, J. C.
  year: 2007
  title: "Disagreement and the stock market"
  venue: Journal of Economic Perspectives
  vol: 21
  issue: 2
  pages_or_artno: 109-128
- doi: "10.1093/rfs/hhag042"
  type: journal
  authors: "Bali, T. G., Kelly, B. T., Mörke, M., & Rahman, J."
  year: 2026
  title: "Machine Forecast Disagreement"
  venue: "The Review of Financial Studies"
new_dois:
- "10.1093/rfs/hhag042"
---

## CORE

【构念与来源】
本家族刻画的是某家银行在某一年度媒体报道语调上的分歧度 (disagreement), 即针对同一实体的新闻在情感极性上的对立与撕裂程度, 而非情感的方向或强弱本身。构念直觉来自金融市场中"意见分歧"这一独立于均值信号的信息维度: 当一家银行的当年报道既包含较高的正面词密度、又包含较高的负面词密度时, 舆论呈现高度分裂, 分歧指数取高值; 当报道用词几乎清一色偏正或清一色偏负时, 舆论一边倒, 分歧指数取低值。分歧度与情感均值 (tone) 是正交的两个测度, 均值近零既可能来自"无人置评"也可能来自"多空激烈对峙", 而本指数专门把后一种撕裂状态从前一种沉默状态中分离出来, 为下游把"市场对某银行金融科技叙事是否形成共识"作为独立解释变量或稳健性维度提供数据支撑。需要着重澄清本家族的真实原料: 它并非来自 stage 21 三家大语言模型的逐篇情感投票 (基于 LLM 投票计数构造的分歧列是独立列族 disag_llm{track}, 输入 pos_count / neg_count, 不属本家族), 而是来自 stage 22 词典法 (tone_words) 在篇章级算出的正面词占比 pos_ratio 与负面词占比 neg_ratio。这两个原料是 float 比率而非整数篇数: pos_ratio = 该篇报道命中 union 情感词典的正面词计数 ÷ 该篇 word-token 数 (排除纯标点与纯数字), neg_ratio 同理取负面词。这些篇章级词频比率经 stage 24 herd_decay 汇入 article×bank 的 verified 精筛集后, 在 panel 装配阶段按银行-年度逐轨取均值, 得到 avg_pos_ratio 与 avg_neg_ratio, 分别充当本公式的 P 与 N。

【方法学与计算】
计算落在 runner.py 步骤 8b (标记为 disag) 的 (a) 词典综合分支, 采用闭式公式 disag = 根号下 (1 减去 ((P 减 N) 除以 (P 加 N)) 的平方), 其中 P = avg_pos_ratio、N = avg_neg_ratio, 二者是银行-年度对篇章级正/负面词占比取的算术均值 (float 比率, 非整数计数)。令净极性 r = (P − N) / (P + N) ∈ [−1, 1] 为该银行-年度报道正负面词密度的规范化倾斜, 则 disag = 根号 (1 − r²)。该式几何上是单位圆上给定横坐标 r 时的纵向半弦长: r = 0 (平均正面词占比与平均负面词占比持平, 舆论最撕裂) 时 disag 取最大值 1; r = ±1 (报道用词几乎纯正或纯负) 时 disag 取最小值 0; 函数关于 r = 0 对称且随 |r| 单调递减, 因而它只吃"正负面词密度是否平衡"这一信息、对总体是偏正还是偏负不敏感, 这正是与 tone 均值测度解耦的数学根源。工程细节上, 引擎先把 P、N 转成 float64 再做除法与开方 (对本家族的比率输入是 no-op, 该转型主要为兄弟计数轨防整数回绕); 当 P + N = 0 (该银行-年度在该轨的平均正、负面词占比同时为 0, 即无任何情感词命中或全为缺失) 时公式退化为 0/0, 引擎置 NaN 而非 0, 以区分"无分歧的一致舆论"与"无从判断的空样本", 这一缺失语义与全流水线把未报道年份标 NaN 而非 0 的口径一致。P 与 N 严格逐轨取自各轨自身的 avg_pos_ratio / avg_neg_ratio, 不跨轨借分母; 且本家族分支与同函数产出的 disag_llm (吃 pos_count / neg_count 篇章计数)、disag_bert (吃 bert 概率均值)、各单词典 disag_{dict} 是并列而各自独立的输入版本, 切勿混淆。

【文献定位】
情感分歧作为独立于均值的信息维度, 在资产定价与文本金融文献中有稳固的理论与实证根基。Hong 与 Stein (2007) 在其观点分歧综述中系统论证了投资者意见分歧如何独立于基本面均值驱动交易量、波动与收益, 奠定了把分歧当作一等信息变量的范式。Carlin、Longstaff 与 Matoba (2014) 用抵押证券市场数据实证了分歧本身对风险溢价与预期收益的定价作用, 表明分歧不是均值信号的噪声残余而是自带信息含量。Cen、Wei 与 Yang (2017) 进一步刻画了分歧与市场反应不足、随后收益之间的关系, 说明高分歧期的信息消化更慢。文本度量侧, Cookson 与 Niessner (2020) 从投资者社交网络直接构造基于文本的分歧代理, 系统区分了同类内部分歧与跨类分歧, 是本家族用篇章级正负面词密度分布刻画分歧的直接方法学参照; Li 与 Luan (2025) 则把新闻文本分歧与横截面股票收益联系起来, 佐证了本指数以新闻语调对立为原料的合理性。方法学上, 本指数把当年围绕同一银行的众多报道各自的正/负面词占比视为一组彼此可能对立的语调信号, 而这些信号在同一实体上呈现的散布本身即为一种可度量的分歧信息, 这与 Uma 等 (2021) 关于"从分歧中学习"的综述所倡导的把分歧当作信息而非纯噪声的一般立场相呼应 (此处援引其对分歧信息性的立场, 与本家族基于词典比率、而非多标注者投票的具体实现无关)。银行间同行网络会让分歧沿关联传导, Grieser 等 (2022) 关于企业金融政策网络效应的证据提示本指数可与同行溢出、网络中心度族联合解读。Bali、Kelly、Mörke 与 Rahman (2026, The Review of Financial Studies) 提出以异质机器学习模型的收益预测离散度构造分歧测度并证明其对未来收益的预测力, 呼应本家族用正负面词占比失衡刻画舆论撕裂的"分歧独立于均值信号"这一构念逻辑。

## VAR: disag_full

【变体差分】
本列是分歧指数的 full 轨版本, 也是三轨中的规范 (canonical) 主轨。full 轨文本口径 = 标题 prepend 到正文之前的全篇内容 (content_full), stage 22 词典法在整篇文本上数出正、负面情感词并算出篇章级 pos_ratio_full / neg_ratio_full。据 2026-06-29 起生效的 full-only 留篇门控, 一篇报道是否被判为"银行金融科技报道"并计入银行-年度分母, 只由 llm_verified_full == True 决定; 因此 full 轨的 P (avg_pos_ratio_full) 与 N (avg_neg_ratio_full) 建立在留篇宇宙的完整集上取的均值, ctx 与 ss 轨则是该留篇集之上 conditional-on-full 的子测度轨。本列公式 disag_full = 根号 (1 − ((P_full − N_full) / (P_full + N_full))²), P_full + N_full = 0 时置 NaN。三轨 (full / ctx / ss) 互为稳健性、不分主次, 各自 just-identified 并排进入分析, 禁混进同一 over-identified Hansen J; full 轨因是门控主轨, 在主回归里通常作为首要测度, ctx / ss 作为文本窗口稳健性。就语义而言, 本列在整篇报道尺度上度量舆论撕裂: full 轨对每篇报道以其全文的正/负面词占比表征其语调, 再在银行-年度上把这些篇章比率平均, 因而 full 轨的分歧更多反映不同报道之间 (跨篇) 的正负面词密度对立, 也吸纳单篇内部正负面用词并存的混杂。相较 ctx / ss 两条收窄窗口轨, full 轨吃进最完整的语境, 参与平均的篇章样本通常最多, 分歧指数的采样噪声最低、辨识力最稳; 但代价是可能把与目标银行金融科技主题弱相关的段落用词也计入词频比率, 这一"语境宽泛"风险恰由 ctx / ss 两轨对冲。凡涉本列与另两轨的联合使用, 一律遵循三轨各自 just-identified 并排、互为稳健性不分主次的口径。

## VAR: disag_ctx

【变体差分】
本列是分歧指数的 ctx 轨版本, 与 full 轨互为稳健性。ctx 轨文本口径 = 标题 prepend 加实体上下文窗口 (content_ctx), 即只保留目标银行实体附近的语境句而非整篇, 目的在于剥离与目标银行无关的段落对情感词计数的干扰。stage 22 词典法在 ctx 轨文本上重新数正、负面词并算出篇章级 pos_ratio_ctx / neg_ratio_ctx, 由此银行-年度聚合出 P_ctx (avg_pos_ratio_ctx) 与 N_ctx (avg_neg_ratio_ctx)。本列公式 disag_ctx = 根号 (1 − ((P_ctx − N_ctx) / (P_ctx + N_ctx))²), P_ctx + N_ctx = 0 时置 NaN, 分子分母严格取自 ctx 轨自身的平均词占比, 绝不借 full 轨分母。因留篇门控为 full-only, ctx 轨行宇宙是 full 留篇集的子集, 本列属 conditional-on-full 的窗口稳健性测度。三轨各自 just-identified 并排、不分主次, 禁混进同一 over-identified Hansen J; 在开发期 T=2 的短面板上, ctx 轨因窗口收窄可能出现词占比退化 (方差偏低), 属预期现象, 生产期 T=18 语料上恢复正常辨识力。与 full 轨相比, 本列的差分核心在于文本进料: full 轨吃整篇, ctx 轨只吃目标银行实体附近的语境句, 因此 ctx 轨的词频比率剔除了与目标银行无关段落的用词扰动, 度量的是"围绕该银行本身的报道"这一更聚焦语料上的正负面词密度撕裂。当一篇报道大段谈论行业或他行、只有零星几句涉及目标银行时, full 轨可能被无关段落的整体用词带偏, 而 ctx 轨把计数锚定在银行实体窗口内, 由此两轨在同一银行-年度上可能给出不同的分歧读数; 这种差异不是误差而是设计意图——它让研究者能检验"结论是否依赖把整篇用词都归到目标银行头上"这一测量假设。本列与 full / ss 三轨互为稳健性、不分主次、禁混同一 over-identified Hansen J。

## VAR: disag_ss

【变体差分】
本列是分歧指数的 ss 轨 (single-sentence, 银行与金融科技同句共现窗) 版本。ss 轨文本口径 = 标题 prepend 加"目标银行与金融科技词在同一句子及其上下 N 句窗内共现"的句子集 (content_ss, 窗半径由 config 的 ss_sentence_radius 控制, 默认 1), 是三轨中语境最紧的一轨, 只吃银行与金融科技真正并置的表述。其回退语义镜像 ctx: 当某篇报道不存在银行与金融科技的同句共现时, content_ss 回退为全文正文、ss_is_fallback 置 True, 并与 ctx 共享 n_articles 分母。stage 22 词典法在 ss 轨文本上数正、负面词并算出篇章级 pos_ratio_ss / neg_ratio_ss, 聚合出 P_ss (avg_pos_ratio_ss) / N_ss (avg_neg_ratio_ss)。本列公式 disag_ss = 根号 (1 − ((P_ss − N_ss) / (P_ss + N_ss))²), P_ss + N_ss = 0 时置 NaN, 平均词占比严格逐轨。ss 轨同为留篇门控 full-only 下的 conditional-on-full 稳健性轨, 三轨互为稳健性、不分主次、各自 just-identified 并排, 禁混进同一 over-identified Hansen J; T=2 开发面板上 ss 轨词占比退化 (常近零方差) 属预期, 生产 T=18 语料恢复。本列相对 full / ctx 两轨的差分核心在于最严的语境锚定: 只有目标银行与金融科技词真正同句 (或紧邻窗内) 并置的表述才进入词频计数, 因而 ss 轨度量的是"该银行金融科技这一具体叙事"上的舆论撕裂, 语义纯度最高但样本最稀。当报道虽提及银行、也提及金融科技却分处两段互不关联时, ss 轨走回退 (退为全文并置 ss_is_fallback), 以避免对"实为空共现"的样本强行计词; 这一回退设计与 ctx 严格镜像, 保证两轨在无共现情形下不产生孤儿读数。正因 ss 轨语料最窄, 其分歧指数在短面板上方差最易塌缩, 但在生产语料上它提供了 full / ctx 无法替代的"就事论事"分歧视角。三轨各自 just-identified 并排、互为稳健性不分主次、禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Li, S. Z., & Luan, Z. (2025). News-based investor disagreement and stock returns. Review of Accounting Studies, 30(3), 2312-2375. https://doi.org/10.1007/s11142-025-09897-1
Grieser, W., Hadlock, C., LeSage, J., & Zekhnini, M. (2022). Network effects in corporate financial policies. Journal of Financial Economics, 144(1), 247-272. https://doi.org/10.1016/j.jfineco.2021.05.060
Uma, A. N., Fornaciari, T., Hovy, D., Paun, S., Plank, B., & Poesio, M. (2021). Learning from disagreement: A survey. Journal of Artificial Intelligence Research, 72, 1385-1470. https://doi.org/10.1613/jair.1.12752
Cookson, J. A., & Niessner, M. (2020). Why don't we agree? Evidence from a social network of investors. The Journal of Finance, 75(1), 173-228. https://doi.org/10.1111/jofi.12852
Cen, L., Wei, K. C. J., & Yang, L. (2017). Disagreement, underreaction, and stock returns. Management Science, 63(4), 1214-1231. https://doi.org/10.1287/mnsc.2015.2405
Carlin, B. I., Longstaff, F. A., & Matoba, K. (2014). Disagreement and asset prices. Journal of Financial Economics, 114(2), 226-238. https://doi.org/10.1016/j.jfineco.2014.06.007
Hong, H., & Stein, J. C. (2007). Disagreement and the stock market. Journal of Economic Perspectives, 21(2), 109-128. https://doi.org/10.1257/jep.21.2.109
Bali, T. G., Kelly, B. T., Mörke, M., & Rahman, J. (2026). Machine Forecast Disagreement. The Review of Financial Studies. https://doi.org/10.1093/rfs/hhag042
<!-- rendered-citations:end -->
