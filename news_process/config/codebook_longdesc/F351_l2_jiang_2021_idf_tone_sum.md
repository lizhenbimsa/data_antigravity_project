---
family_id: F351
columns:
- jiang_2021_idf_tone_sum_ctx
- jiang_2021_idf_tone_sum_full
- jiang_2021_idf_tone_sum_ss
unit: 语调得分 (连续; 文章级 idf_score 是 IDF 加权正负词贡献自归一化后的比率, 有界于 [-1,+1]; 面板级 idf_tone_sum 是该有界比率在 bank-year 内的求和, 非均值, 理论上不设界)
formula: 'article: idf_score = normalized_score = Σ_{w命中词}final_score(w) / Σ_{w命中词}|final_score(w)| ∈ [-1,+1] (final_score 由 IDF 权重与否定翻转/程度副词/转折三条语言学规则共同决定; 即文章级已是自归一化、有界比率, 非未除以词数的原始加权和); panel: idf_tone_sum = 按 full/ctx/ss 轨对 bank-year 内全部留篇文章的 idf_score 求 sum (非均值; "sum" 指面板聚合动词, 被求和的对象本身已是逐篇 [-1,+1] 有界比率)'
producer: pipeline\sentiment\tone_words.py (词典打分与 idf_tone_sum 变体计算) ; pipeline\panel\encode.py (article→panel 聚合) ; pipeline\panel\export.py ; pipeline\panel\stata_export.py
upstream: [21_tone_llms, 22_tone_words]
citations:
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, 唐国豪
  year: 2021
  title: 媒体文本情绪与股票回报预测
  venue: 经济学(季刊)
  vol: "21"
  issue: "4"
  pages_or_artno: 1323-1344
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: "26"
  issue: "3"
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: "68"
  issue: "7"
  pages_or_artno: 5514-5532
- doi: 10.1111/ecin.13264
  type: journal
  authors: Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E.
  year: 2025
  title: 'Sentiment analysis of economic text: A lexicon-based approach'
  venue: Economic Inquiry
  vol: "63"
  issue: "1"
  pages_or_artno: 125-143
- doi: 10.1257/jel.20181020
  type: journal
  authors: Gentzkow, M., Kelly, B., & Taddy, M.
  year: 2019
  title: Text as data
  venue: Journal of Economic Literature
  vol: "57"
  issue: "3"
  pages_or_artno: 535-574
new_dois: []
---

## CORE

【构念与来源】
本家族测度中国金融文本情感研究中一条历史悠久的方法路线——词典法(dictionary-based sentiment)在本项目里对姜富伟等(2021)专用词典的一个具体计数变体: idf_tone_sum, 即"逆文档频率(IDF)加权的语调计数之和"。姜富伟、孟令超、唐国豪(2021, 《经济学(季刊)》)基于中国财经媒体语料构建了一部适配中文金融文本的情感词典(下称 jiang_2021 词典), 用以刻画媒体文本情绪对股票回报的预测力。项目将该词典移植到银行-金融科技(FinTech)报道语境, 作为 6 部情感词典(jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran)之一, 与另两条独立情感测度路线——三家大语言模型多数投票(gpt54nano/gemini31/deepseekv4)与三个金融领域 BERT 模型(finbert_cn/fin_sent_zh/finbert2)——并列, 三法各自 just-identified, 互为稳健性、不分主次, 共同构成本项目情感测度三角(词典法解释性强但对语境不敏感、LLM 法语境理解强但成本高、BERT 法居中)。idf_tone_sum 是词典打分家族里的一个具体聚合口径: 对文章中每个命中词典的正面词/负面词, 用该词在语料中的逆文档频率(而非等权 1)作为其对整体语调的贡献权重, 再对正面贡献求和、负面贡献求和, 取差得到该篇文章的 idf_tone_sum 原始值。IDF 加权的直觉是: 在语料中普遍出现的常用情感词(如"上涨""下跌")信息量有限, 而在少数文章中才出现的生僻但强烈的情感词往往携带更多辨识信息, 用 IDF 对其加权放大, 是信息检索(TF-IDF)思想向情感计数的自然延伸, 与 Barbaglia 等(2025, *Economic Inquiry*)在经济文本词典法综述中强调的"给予信息量更大的词更大权重"这一改进方向一致。

【方法学与计算】
计算管线分两段, 数学口径须区分清楚: 文章级产出的并非未归一化的原始加权和, 而是一个已自归一化、有界于 [-1,+1] 的比率。文章级(stage 22 `tone_words.py`): 先用 jieba(冻结版本 0.42.1, 保证跨次运行分词结果确定性可复现)对文章文本分词, 再在词典词表上匹配正面词与负面词; 每个命中词依 IDF 权重(在项目语料上预先估计并冻结)与三条语言学规则——否定翻转/程度副词/转折——共同决定其最终贡献 final_score(w), 随后对全部命中词的 final_score 求和并除以其绝对值之和做自归一化, 得到 idf_score = Σfinal_score(w) / Σ|final_score(w)| ∈ [-1,+1]。也就是说, "IDF 加权"体现在逐词贡献的权重构造上, 而非体现在最终产出量纲上——最终产出已经是一个有界比率, 与"是否除以词数"这一常见的 raw/avg 二分法不完全对应, 更接近于一个自身内部已做过尺度归一化的语调强度指标。该文章级 idf_score 在 stage 22 内部计算, 供后续聚合消费。面板级(stage 40 `encode.py`/`export.py`): 对通过留篇门控的 bank-year 样本内全部文章, 按轨(full/ctx/ss)分别对文章级 idf_score 取 sum(聚合动词为求和而非均值), 得到本家族三个面板列 jiang_2021_idf_tone_sum_{full,ctx,ss}。因此面板列名中的"tone_sum"准确描述的是聚合方式(对篇计数求和), 而被求和的对象——文章级 idf_score——本身早已是归一化比率, 二者不可混为一谈; 篇均含义应通过与 n_articles 相除另行还原, 本列不预先做该归一化。三轨的差异纯粹来自扫描文本的范围, 而非算法本身。留篇门控口径为 full-only(2026-06-29 起): 一篇报道是否计入"银行-金融科技"样本, 只看 full 轨大语言模型三家投票结果(`llm_verified_full == True`), 与词典打分完全独立的两条测度路线判定其是否留篇; ctx/ss 轨的 idf_tone_sum 值是在 full 轨已确定的留篇文章行宇宙子集上、各自扫描各自的文本窗口(ctx=标题+实体窗口, ss=标题+银行∧金科同句±N窗)计算的稳健性/条件测度, 不构成独立的样本纳入判据。当某篇文章不存在银行与金科词的同句共现窗口时, ss 轨依 CLAUDE.md 铁律镜像 ctx 轨的回退语义: 退化为使用全文 body 作为 content_ss, 并将 ss_is_fallback 标记为真、与 ctx 共享 n_articles 分母, 从而在稀疏共现场景下不静默丢文章。

【文献定位】
姜富伟等(2021)在《经济学(季刊)》构建的这部词典是本项目 6 部情感词典之一, 与 Du 等(2022, *Review of Finance*)提出的针对中国金融文本领域特异性的情感词典构成同类中文金融专用词典路线的两个代表——两文均强调通用情感词典(如英文 Loughran-McDonald)直接翻译或移植到中文金融语境会因语言结构与领域用词差异而失真, 需要基于本地语料重新构建词表与极性判定规则。本项目并列纳入 jiang_2021/du_2022/bian_2021/you_2018/yao_2021/loughran(经中文主译改造)六部词典, 既是对"哪一部词典更优"这一开放问题不做预设立场的稳健性设计, 也呼应 Frankel、Jennings 与 Lee(2022, *Management Science*)关于机器学习方法与词典方法在披露情感测量上系统性分歧的发现——词典法本身对词表选择、权重方案高度敏感, 单一词典的点估计不足以支撑因果推断的稳健性主张。idf_tone_sum 这一 IDF 加权口径, 是在"是否加权""如何归一化"两个维度上, 与家族内其余变体(如未加权 raw 计数、除以词数的比率 tone、仅保留否定规则的 negonly 等)共同构成的消融/口径梯子的一环。其加权思想的方法学锚点是 Gentzkow、Kelly 与 Taddy(2019, *Journal of Economic Literature*)对文本作为经济学数据(text as data)的系统性综述——该文将 tf-idf 式的词加权确立为文本量化研究中处理"不同词信息量不等"这一问题的经典工具, 逆文档频率越高(即在语料中越普遍出现)的词, 其对单篇文本区分度的边际贡献越低, 理应赋予更小权重; 反之在少数文章中才出现的生僻但强烈的情感词往往携带更多辨识信息, 应予放大。本项目将这一源自信息检索、经 Gentzkow 等系统化梳理的加权框架应用到中文金融情感词典打分算子上, 构成 idf_tone_sum 相对于未加权 raw 计数变体的方法学依据。同时, Barbaglia 等(2025, *Economic Inquiry*; 另有 2024 年 arXiv 工作论文版本)在经济文本词典法综述中进一步佐证了"对高信息量、低频次情感词赋予更大权重"这一改进方向在词典法情感分析实践中的可行性, 二者共同支撑本列的构造动机: 部分缓解纯计数词典法对语境不敏感、易被套话与高频套语词稀释的固有缺陷。

## VAR: jiang_2021_idf_tone_sum_ctx

【变体差分】
本列是 idf_tone_sum 在 ctx(实体窗)轨上的取值: 扫描文本为标题+目标银行与金融科技实体附近的窗口文本(而非全文), 由 stage 14 `ctx_materializer` 在 stage 21 之前物化为 content_ctx 列(标题前置拼接, prepend_title)。ctx 轨与 full 轨、ss 轨三者是彼此独立、各自 just-identified 并排的稳健性测度, 互为稳健性、不分主次, 严禁在同一 over-identified 的 Hansen J 设定中把三轨混入同一组过度识别的工具/矩条件——三轨应分别单独进入各自的回归设定, 而不是作为同一构念的多个工具同时使用。ctx 轨的样本行宇宙受 full-only 留篇门控约束(是否留篇由 full 轨 LLM 判定, ctx 只是在已确定留篇的文章上做条件测度), 因此本列反映的是"聚焦实体窗口而非全文时, 姜富伟词典 IDF 加权语调测度是否仍然稳健"这一构念区分问题的实证答案。当某篇文章缺乏可识别的实体窗口时, content_ctx 会退化为标题+全文(fallback), 对应的 ctx_is_fallback 标记为真, 该情形下本列的取值实质上与 full 轨高度接近, 但仍按 ctx 轨的分母口径计入统计。相较 full 轨的全文扫描, ctx 轨的价值在于剔除与目标实体无关的段落(如文章中穿插的其他银行/其他业务介绍、免责声明、套话式结尾), 使逐篇 idf_score(自归一化于 [-1,+1] 的 IDF 加权语调比率)更紧密地对应"这篇报道究竟怎么谈论目标银行的金融科技活动", 而不被无关段落的情感用词稀释或反向拉扯; 其代价是窗口内可命中词典词的样本容量缩小, 使单篇 idf_score 对短窗口内偶发的强情感词更敏感(命中词少时, 单个词的 final_score 在归一化分母中占比更高), 波动性相应更高, 面板级按 bank-year 求和得到的 idf_tone_sum_ctx 也随之继承这一波动性。ctx 轨物化(content_ctx 列)发生在 stage 14, 早于 stage 21 情感三法运行, 使得词典法(本列)、LLM 三家投票法与 BERT 三模型法在同一个物化好的 ctx 文本上各自独立打分, 三条方法路线之间不存在因文本切分时点不同而产生的口径错位。

## VAR: jiang_2021_idf_tone_sum_full

【变体差分】
本列是 idf_tone_sum 在 full(全文, 标题+正文)轨上的取值, 是三轨中样本行宇宙的锚定轨: 一篇报道是否被认定为"银行-金融科技"报道、从而进入本家族的分母(bank-year 内的留篇文章集合), 完全由 full 轨的大语言模型三家多数投票结果(`llm_verified_full == True`)决定(留篇门控口径 full-only, 2026-06-29 起生效)。full 轨同时也是本项目多数 paper 主线(如 P1 情感处理变量 llm_vote_tone_full)所采用的 headline/canonical 文本范围, 但需注意: idf_tone_sum_full 本身是词典法测度, 与 LLM 法的三家投票、BERT 法的三模型 是三条彼此独立、互为稳健性、不分主次的平行测度路线, 词典法内部的 full/ctx/ss 三轨敏感性检验与情感测度方法之间的三角互证是两个不同维度的稳健性设计, 不应混同。本列取全文范围扫描, 能够捕捉标题之外正文段落里出现的姜富伟词典命中词, 相较 ctx/ss 两个窗口更窄的轨, 更少受实体窗口/同句判据误判或漏判的影响, 但也因此更容易被与银行-金科主题无关的段落(如套话、免责声明、其他业务介绍)稀释, 是三轨口径权衡中信息覆盖面最广、语境聚焦度相对最低的一端。作为样本行宇宙的锚定轨, full 轨的单篇 idf_score 天然基于最大的可命中词典词样本容量(全文词数通常远多于 ctx/ss 窗口词数), 命中词越多, 归一化分母 Σ|final_score| 与分子 Σfinal_score 中偶发极端词的相对占比越小, 单篇 idf_score 的绝对值分布往往更收敛, 但面板级按 bank-year 对全部留篇文章求和得到的 idf_tone_sum_full, 由于分母是最大的可命中样本容量、纳入求和的篇数与命中密度也相对最高, 其加总值绝对值一般也大于 ctx/ss 两轨——这一差异是扫描范围与样本容量机制性带来的, 不代表 full 轨"情感更强烈", 解读跨轨数值差异时应予注意, 更适合的跨轨比较方式是看三轨内部各自随时间/银行变化的相对排序或标准化后的系数, 而非直接比较原始 idf_tone_sum 水平值。

## VAR: jiang_2021_idf_tone_sum_ss

【变体差分】
本列是 idf_tone_sum 在 ss(同句)轨上的取值: 扫描文本为标题+目标银行与金融科技词汇在同一句子内共现(±N 句窗口, N 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置, 默认 1)的文本片段, 是三轨中语境聚焦度最高、判据最严格的一支, 判定原语与 stage 13 共现硬过滤所用的 ±1 句窗口邻近判据("有无共现"层面)不同, 是更严格的"严格同句"层面判据。ss 轨的回退语义镜像 ctx 轨: 当某篇留篇文章不存在银行与金科词的同句共现窗口时, content_ss 退化为使用全文 body, 对应 ss_is_fallback 标记为真, 并与 ctx 共享同一个 n_articles 分母, 从而保证在共现稀疏(如仅标题提及、正文未再度紧邻出现)场景下不会因空文本而静默丢弃样本行。本列与 ctx、full 两列是彼此独立并排的稳健性测度, 互为稳健性、不分主次, 严禁混入同一 over-identified 的 Hansen J 设定; 由于 ss 轨扫描范围最窄、单句窗口内可命中词典词的数量最少, 单篇 idf_score 对偶发强情感词的敏感度在三轨中最高; 面板级按 bank-year 求和得到的 idf_tone_sum_ss, 在纳入求和的有效命中篇数与命中密度上通常也小于 ctx/full 两轨, 其加总值绝对值在样本量层面通常小于 ctx/full 两轨的对应值, 解读时应以"同一构念在不同语境聚焦度下的条件测度"而非"数值可比的强度指标"看待, 且本列样本行宇宙同样受 full 轨留篇门控约束, 不构成独立的样本纳入判据。

<!-- rendered-citations:begin -->
姜富伟, 孟令超, 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
<!-- rendered-citations:end -->
