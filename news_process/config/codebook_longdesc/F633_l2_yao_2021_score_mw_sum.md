---
family_id: F633
columns:
- yao_2021_score_mw_sum_ctx
- yao_2021_score_mw_sum_full
- yao_2021_score_mw_sum_ss
unit: 无量纲得分 (词典命中词条加权计数之和, 未归一化)
formula: 'score_mw_sum(panel, bank-year) = Σ_{article} [yao_2021_score{track}(article) × media_authority_weight(article)]; mw = media-authority-weighted (Holzman, Kova, Petkevich & Teoh 2023, TAR 方法), 非"多字词条"; media_authority_weight 由 pipeline/panel/runner.py::compute_media_authority_weights 依据媒体来源权威性打分, 逐篇乘到该篇的 yao_2021 未加权词典分数 yao_2021_score{track} 上, 得到文章级 yao_2021_score_mw{track}, 再在 encode.py 按银行-年 sum 聚合成本列; 与同族 score_hw_sum (herd-decay 加权, stage 24 产 herd_weight)、score_w_sum (mention_density 加权, Hassan 2019 QJE value-weighted exposure) 是三种互不相同、互不可加的加权方案的乘积聚合, 不满足 w = hw + mw 之类恒等式'
producer: pipeline\panel\runner.py ; pipeline\panel\encode.py ; pipeline\panel\export.py ; pipeline\panel\stata_export.py
upstream:
- news_process/pipeline/sentiment/tone_words.py
- news_process/config/tone_dicts.json
- news_process/pipeline/panel/runner.py
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1287/mnsc.2021.4156
  type: journal
  authors: Frankel, R., Jennings, J., & Lee, J.
  year: 2022
  title: 'Disclosure sentiment: Machine learning vs. dictionary methods'
  venue: Management Science
  vol: '68'
  issue: '7'
  pages_or_artno: 5514-5532
- doi: 10.1162/COLI_a_00049
  type: journal
  authors: Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M.
  year: 2011
  title: Lexicon-based methods for sentiment analysis
  venue: Computational Linguistics
  vol: '37'
  issue: '2'
  pages_or_artno: 267-307
new_dois: []
---

## CORE

【构念与来源】
本家族衡量的是"一篇报道在 Yao (2021) 中文金融情感词典上的原始打分, 按该篇所刊载媒体的权威性做加权后的银行-年累加值"。Yao (2021) 词典是本仓 6 部情感词典梯子 (`jiang_2021`/`yao_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran`) 之一, 由 `pipeline/sentiment/tone_words.py` 统一装载 (SSOT = `config/tone_dicts.json`), 对每篇文章文本做基于词条匹配的加性打分, 产出文章级未加权分数 `yao_2021_score{track}`。`score_mw_sum` 中的 `mw` 指 media-authority-weighted (媒体权威加权), 与词条字符长度、"多字词条"/"单字词条"/"head-word" 毫无关系, `tone_words.py` 中根本不存在按词条长度切分打分的逻辑。真正的加权与聚合发生在 `pipeline/panel/runner.py`: 该模块以 `compute_media_authority_weights` 依据媒体来源的权威性计算逐篇的 `media_authority_weight`, 再把它乘到该篇的未加权词典分数上, 得到文章级 `yao_2021_score_mw{track}`; `pipeline/panel/encode.py` 随后把三轨文章级 mw 分数按银行-年 sum 聚合, 落到面板层即为本列。同族三支加权分数 `score_hw_sum` / `score_mw_sum` / `score_w_sum` 分别对应三种互不相同的加权方案而非同一分数的三种切分: `hw` = herd-decay-weighted (跟风衰减加权, 权重来自 stage 24 `herd_decay_processor` 产出的 `herd_weight_{full,ctx,ss}`), `mw` = media-authority-weighted (本列), `w` = value-weighted (基于 `mention_density` 的提及密度加权, Hassan et al. 2019, QJE value-weighted exposure 方法)。三者各自把同一未加权原始分数乘以不同的权重再求和, 是三条独立、互不可加的加权聚合路径, 不满足 `score_w_sum = score_hw_sum + score_mw_sum` 之类恒等式, 也不构成对某个总量的"子集划分"。`sum` 后缀表明这是加权后的累加值, 不做进一步归一化处理 (与 `yao_2021_tone_{track}` 那种正负相抵、除以命中词数或篇幅得到的有向语调分数是两个不同层级的产出: `tone` 是可比的情感极性测度, `score__sum` 是其上游的、按不同加权方案分别落地的原始信号, 主要用于事后核验语调结论对"媒体权威性/跟风衰减/提及密度"三类加权方案是否稳健, 不直接作为面板回归的自变量使用)。

【方法学与计算】
未加权词典打分发生在 stage 22 (`tone_words.py`), 对每篇文章的三条文本轨 (`content_full`/`content_ctx`/`content_ss`, 由 stage 14 `ctx_materializer` 物化) 分别执行基于 jieba 分词 + Yao (2021) 词典条目匹配的扫描, 命中即按条目预设权重 (词典自带正负极性/强度系数) 计入正负两侧, 得到文章级未加权分数 `yao_2021_score{track}`。媒体权威加权发生在下游 `pipeline/panel/runner.py`: `compute_media_authority_weights` 基于媒体来源的权威性 (参照 Holzman, Kova, Petkevich & Teoh 2023, The Accounting Review 的媒体权威加权方法学) 为每篇文章打一个 `media_authority_weight`, 权重与该篇文本轨无关 (同一篇文章的 full/ctx/ss 三轨共用同一 `media_authority_weight`), 但分别乘到各轨未加权分数上, 得到三条各自独立的 `yao_2021_score_mw_full` / `_ctx` / `_ss`。三轨行宇宙遵循 full-only 留篇门控 (2026-06-29 起): 只看 `llm_verified_full == True` 判定一篇是否为有效银行金科报道, ctx/ss 两轨的行宇宙是该留篇集合的子集; `_ss` 轨的文本范围若无银行∧金科同句共现, 镜像 `_ctx` 回退语义降级为全文 body (`ss_is_fallback=True`, 与同族 `_ss` 列共享同一 `n_articles` 分母)。三轨口径遵循全库统一的三轨架构: full/ctx/ss 各自 just-identified 并排, 互为稳健性、不分主次, 严禁混入同一 over-identified Hansen J 设定。文章级加权分数经 `pipeline/panel/encode.py` 按银行-年 sum 聚合到面板层 (与其它文章级词典分数一致的 sum 聚合口径), 并在 `pipeline/panel/export.py`/`stata_export.py` 层落盘挂标签。

【文献定位】
词典法情感测度在中文金融文本场景下的方法学基础可追溯至 Du, Huang, Wermers & Wu (2022, Review of Finance) 对通用情感词典 (如 Loughran-McDonald 系) 在中文金融语境下语言/领域特异性不足的系统性诊断, 这一发现是本仓引入多部专门构建的中文金融情感词典 (含 Yao 2021) 的直接方法学动因。词典法与机器学习/LLM 法互为稳健性而非替代关系的立场, 参照 Frankel, Jennings & Lee (2022, Management Science) 对"披露情感: 机器学习 vs 词典方法"的系统对比, 二者在不同语料特征下各有优劣, 本仓的三法并行架构 (LLM 三家投票 / 词典六部 / BERT 三模型) 正是对这一发现的工程化落地。本列所代表的"按媒体权威性对情感信号加权"这一做法, 承接的是 lexicon-based 情感分析范式对"信号来源异质性会影响测度效度"这一问题的一般性关注 (Taboada, Brooke, Tofiloski, Voll & Stede, 2011, Computational Linguistics 对词典法整体方法学谱系的系统梳理), 但其具体实现 (媒体权威加权) 与词典条目本身的长度、词性等语言学特征无关, 而是把"报道该篇的媒体渠道有多权威"这一外生媒体特征引入情感测度的权重结构, 是词典法情感打分与媒体经济学 (media economics) 交叉的一处具体落地, 与同族 `score_hw_sum` (跟风衰减)、`score_w_sum` (提及密度) 分别对应"时间维度的信息衰减"与"篇幅/提及强度维度的价值加权"两类互不相同的权重结构并排存在。

## VAR: yao_2021_score_mw_sum_ctx

【变体差分】
本列是 `yao_2021_score_mw_sum` 家族的实体窗轨 (ctx = context)。未加权词典分数的扫描文本为 `content_ctx` (标题 + 目标银行/金科实体窗口截取文本, 由 stage 14 物化, `prepend_title` 拼接标题), 与 `_full` 轨的差异仅在于未加权分数 `yao_2021_score_ctx` 的文本范围收窄到实体邻近上下文, 意在剔除全文中与银行-金科关系无关段落 (如报道末尾的行业背景铺垫、无关业务条线介绍) 对情感命中计数的稀释或污染。乘到该未加权分数上的 `media_authority_weight` 本身与文本轨无关 (同一篇文章三轨共用同一媒体权威权重, 权重差异只来自不同文章刊载媒体不同), 因此本列与 `_full`/`_ss` 两轨的差异完全来自未加权分数的文本范围差异, 而非加权方案本身的差异。留篇行宇宙 = full 轨留篇集合的子集 (full-only 门控, 2026-06-29 起); 本列不单独承担是否为有效报道的判定, 只在已判定为有效的行内计算。与 `_full`/`_ss` 两轨互为稳健性、不分主次, 三轨应作为并排的 just-identified 设定分别代入下游回归, 不得在同一 over-identified 设定 (如 Hansen J 检验) 中混用。作为媒体权威加权后的累加分数, 本列未做进一步归一化, 数值受该轨文本长度分布影响, 使用时须留意与 `_full` 轨在篇幅上的系统性差异 (ctx 轨截取文本通常显著短于全文)。本列与同轨的 `yao_2021_score_hw_sum_ctx`(跟风衰减加权)、`yao_2021_score_w_sum_ctx`(提及密度加权) 三者是对同一未加权 `yao_2021_score_ctx` 施加三种互不相同权重方案后各自独立求和的结果, 不构成可加或子集关系, 三者并排用于核验语调结论是否对"媒体权威性/跟风衰减/提及密度"三类加权方案稳健。本列不进入任何一篇论文的主回归设定 (treatment/DV), 仅作为词典法情感测度构念效度的内部稳健性诊断信号存档。

## VAR: yao_2021_score_mw_sum_full

【变体差分】
本列是 `yao_2021_score_mw_sum` 家族的全文轨 (full), 是三轨中的默认/主口径参照: 未加权词典分数扫描文本为 `content_full` (标题 + 完整正文, stage 14 物化)。留篇门控直接锚定本轨 (`llm_verified_full == True` 决定一篇报道是否计入银行-金科报道留篇集合), ctx/ss 两轨的行宇宙均是本轨留篇集合的子集, 因此本列的样本覆盖面在三轨中最广。本列 = 全文未加权分数 `yao_2021_score_full` 乘以该篇的 `media_authority_weight` (媒体权威加权, 与文本轨无关的篇级权重) 后按银行-年 sum 聚合, 反映"整篇报道"层面按刊载媒体权威性调整后的情感信号累计强度。与同轨的 `score_hw_sum_full`(跟风衰减加权)、`score_w_sum_full`(提及密度加权) 均以同一 `yao_2021_score_full` 为分子, 但各自乘以三种互不相同的权重方案 (媒体权威 / 跟风衰减 / 提及密度), 是三条并排、互不可加的加权聚合结果, 不满足 `score_w_sum_full = score_hw_sum_full + score_mw_sum_full` 之类恒等式, 也不构成对全部词典命中的子集切分, 使用者不应据此写代码断言二者之和逐行等于第三者。与 ctx/ss 两轨互为稳健性、不分主次, 三轨并排使用, 不进同一 over-identified Hansen J。全文轨覆盖面最完整, 是三轨中最不受"截取窗口边界效应"影响的一轨, 但代价是更容易把全文中与银行-金科主题无关段落 (行业综述、企业历史沿革、无关业务条线介绍等) 的情感命中一并计入并按媒体权威加权, 使得本列相对 ctx/ss 两轨更偏"报道整体基调经媒体权威调整后的水平"而非"银行-金科关系专属语调"。与其余五部词典 (`jiang_2021`/`bian_2021`/`du_2022`/`you_2018`/`loughran`) 各自的 hw/mw/w 三元组同理并排, 六部词典之间同样互为稳健性、不分主次。

## VAR: yao_2021_score_mw_sum_ss

【变体差分】
本列是 `yao_2021_score_mw_sum` 家族的同句轨 (ss = same-sentence)。未加权词典分数的扫描文本为 `content_ss` (标题 + 目标银行与金科词在同一句、默认 ±1 句窗口内共现的句子集合截取文本, `config/filtering.yaml::context_window.ss_sentence_radius` 控制窗口大小), 是三轨中文本范围最窄、判定条件最严格的一轨, 意在把情感命中限定在银行与金科概念真正"同句相关"的语境内, 排除同篇但不同段落的无关命中对分数的稀释或污染。乘到该未加权分数上的 `media_authority_weight` 与文本轨无关 (同一篇文章三轨共用同一媒体权威权重), 本列与 `_full`/`_ctx` 的差异完全来自未加权分数 `yao_2021_score_ss` 的文本范围差异。回退语义镜像 `_ctx` 轨: 若一篇报道 (已通过 full-only 留篇门控) 不存在银行∧金科同句共现, 本列退化为对全文 body 扫描 (`ss_is_fallback=True`), 与其余同族 `_ss` 列共享同一 `n_articles` 分母, 不因回退而单独产生孤儿分母。留篇行宇宙同样是 full 轨留篇集合的子集。与 `_full`/`_ctx` 两轨互为稳健性、不分主次, 三轨各自 just-identified 并排, 严禁混入同一 over-identified Hansen J 设定; 由于文本范围最窄, 本列的原始累加值 (未归一化, 已经媒体权威加权) 通常系统性低于同篇的 `_full`/`_ctx` 轨取值, 跨轨比较应以标准化后的相对变化而非原始水平为准。同句轨的判定原语与 stage 13 共现硬过滤所用的 ±1 句窗口判据同源但不同层: stage 13 的共现判据决定一篇报道是否进入下游情感/词典打分产线 (硬过滤丢行), 而本列的 `_ss` 文本截取判据决定的是在已进入产线的报道内部哪些句子被纳入词典扫描范围, 二者共享同一 `sentence_radius` 配置语义但作用对象不同, 不可混为一谈。当一篇报道存在多处银行-金科同句共现片段时, 本列会将这些片段拼接后统一扫描, 因此其情感命中既可能来自单一段落的密集表述, 也可能来自全文分散的多处同句片段的累加, 使用者若需区分"密集论述"与"分散提及"两种情形, 应结合同族的篇幅/句数控制列联合解读, 本列本身不做该区分。同族的 `score_hw_sum_ss`(跟风衰减加权)、`score_w_sum_ss`(提及密度加权) 与本列共享同一未加权 `yao_2021_score_ss`, 三者各乘不同权重方案后并排使用, 不构成可加关系。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Taboada, M., Brooke, J., Tofiloski, M., Voll, K., & Stede, M. (2011). Lexicon-based methods for sentiment analysis. Computational Linguistics, 37(2), 267-307. https://doi.org/10.1162/COLI_a_00049
<!-- rendered-citations:end -->
