---
family_id: F630
columns:
- yao_2021_pos_substvalid_count_ctx
- yao_2021_pos_substvalid_count_full
- yao_2021_pos_substvalid_count_ss
unit: 篇数/计数 (count, bank-year 汇总)
formula: 'bank-year 求和 { 1[ yao_2021_score{track} > 0 ] ∧ 1[ innovation_substantiveness{track} ∈ {"象征性","实质性"} ] }, track ∈ {full, ctx, ss}, 逐篇 0/1 指示先在 panel/runner.py::aggregate_panel 内构造为 `_svd_yao_2021_pos{track}`, 再由 `_pool_svd_substvalid_counts` 按 target_bank×year 求和并更名为 `yao_2021_pos_substvalid_count{track}`'
producer: pipeline/panel/runner.py (aggregate_panel 内联 washing_cols 构造 + _pool_svd_substvalid_counts 聚合; 消费方 stata_export.py 仅做标签映射)
upstream: [pipeline/sentiment/tone_words.py, pipeline/panel/encode.py]
citations:
- {doi: "10.1016/j.eswa.2024.125739", type: journal, authors: "Ma, Y., Zhang, T., & Zhang, P.", year: 2025, title: "The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application", venue: "Expert Systems with Applications", vol: "264", pages_or_artno: "125739"}
- {doi: "10.2139/ssrn.3446388", type: wp, authors: "Bian, S., Jia, D., Li, F., & Yan, Z.", year: 2021, title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance", venue: "SSRN Working Paper No. 3446388"}
- {doi: "10.1111/j.1540-6261.2010.01625.x", type: journal, authors: "Loughran, T., & McDonald, B.", year: 2011, title: "When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks", venue: "The Journal of Finance", vol: "66", issue: "1", pages_or_artno: "35-65"}
- {doi: "10.1257/jel.20181020", type: journal, authors: "Gentzkow, M., Kelly, B., & Taddy, M.", year: 2019, title: "Text as data", venue: "Journal of Economic Literature", vol: "57", issue: "3", pages_or_artno: "535-574"}
- {doi: "10.1016/j.jfineco.2022.07.009", type: journal, authors: "Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.", year: 2022, title: "Bank transparency and deposit flows", venue: "Journal of Financial Economics", vol: "146", issue: "2", pages_or_artno: "475-501"}
- {doi: "10.5465/amj.2006.23478255", type: journal, authors: "Fiss, P. C., & Zajac, E. J.", year: 2006, title: "The symbolic management of strategic change: Sensegiving via framing and decoupling", venue: "Academy of Management Journal", vol: "49", issue: "6", pages_or_artno: "1173-1193"}
new_dois: []
novelty_exempt_rationale: "该家族是洗稿率方法D2的'同域分母'修正列(_svd_前缀),非独立提出的情感测度,而是既有pos_count/pos_symb_count分子分母定义域匹配的技术性衍生指示列,其测度依据已在词典原始文献(Yao 2021)与洗稿率母族构念中给出,属衍生/一致性修正变体家族。"
---

## CORE

【构念与来源】
本家族三列是 Yao (2021) 中文金融情感词典阳性语调判定与 LLM 实质性 (substantiveness) 分类交叉后的"同域分母"计数, 供洗稿率 (washing ratio) 方法 D2 单词典口径消费, 本身不是一个独立提出的情感测度, 而是既有 pos_count / pos_symb_count 两族在计算除法前必须匹配的分母修正列。命名中的 substvalid 拼出"substantiveness-valid"——即该篇报道的 LLM 实质性/象征性二分类结果确实被判出 (非缺失/非平局/非拒判), 而不是任意口径下的"有效"。三列分别对应全文轨 (`_full`)、实体窗轨 (`_ctx`)、银行∧金科同句轨 (`_ss`), 三轨各自独立聚合, 互为稳健性并排, 不分主次, 依 CLAUDE.md 铁律禁止混入同一 over-identified Hansen J。
该家族诞生于一次显式的度量学修正 (fix(omni-g-runner-10/g-runner-14), 2026-06-11 提交历史可查): 洗稿率原定义为"正面且被 LLM 判为象征性的报道数" 除以 "词典阳性报道数" (物理计数, 即 `yao_2021_pos_count{track}`)。分子隐含要求 `innovation_substantiveness{track}` 已被 LLM 成功分类为象征性 (NaN 经 `astype(str)` 变为字符串 'nan', 恒不等于 '象征性', 故分类失败的报道永不计入分子); 但旧分母仍照数全部词典阳性报道, 不问该报道的实质性分类是否成功。这造成分子/分母定义域不匹配: 当 LLM 实质性分类失败率系统性上升 (例如某年报道措辞晦涩、模型置信度低、批次拒判增多) 时, 分子按比例萎缩而分母纹丝不动, 洗稿率被人为拉低——这是分类失败率的假象, 不是真实的洗稿行为下降。修复方案是为每种方法各建一族"同域分母"指示列, 只统计"词典阳性 ∧ 实质性分类确实成功"的报道, 使分子分母共享同一个可测量子集。yao_2021 词典是六部中文金融情感词典之一 (与 jiang_2021/bian_2021/du_2022/you_2018/loughran 并列, 六部构成词典消融梯度的成员测度), 该家族即其单词典 (方法 D2) 分母口径的实例化。
【方法学与计算】
计算分两步, 均落在 `pipeline/panel/runner.py::aggregate_panel` 内。第一步 (篇章级, aggregate_panel 前段): 对每篇候选报道, 先取该轨情感语调分数 `yao_2021_score{track}` (词典打分, >0 判为阳性), 再取该轨 LLM 实质性分类标签 `innovation_substantiveness_full` (⚠ v3.2.0 起该字段本身即只有 `_full` 单轨版本, 不再逐轨分裂——该字段测的是"这篇报道整体讲的是不是实质性创新举措", 是文章属性而非轨道相关的文本子集属性, 因此三个 substvalid_count 列虽然轨道后缀跟随 `yao_2021_score{track}` 变化, 但实质性判定输入统一取自 `_full` 轨), 判定该标签是否落在 `_SUBST_VALID_LABELS`(即 {"象征性","实质性"} 两个有效类别之一, 与 NaN/其他拒判态互斥)。两个条件 (词典阳性 ∧ 实质性标签有效) 逻辑与后得到 0/1 指示列 `_svd_yao_2021_pos{track}` (`_svd_` 前缀 = subst-valid denominator, 私有中间列, 不落文章级 parquet, 供本阶段内消费即弃)。第二步 (bank-year 聚合): `_pool_svd_substvalid_counts` 把全部 `_svd_*` 列按 `target_bank`×`year` 分组求和, 再将列名从 `_svd_{name}_pos{track}` 机械改写为 `{name}_substvalid_count{track}`, 与 bank-year panel 左连接合并。这一计数随后仅在 `_svd_denom` 辅助函数内被消费一次: 作洗稿率方法 D2 (`washing_ratio_yao_2021{track} = yao_2021_pos_symb_count{track} / yao_2021_pos_substvalid_count{track}`) 的分母, 若该列因旧 schema 缺失, 才优雅回退到物理计数 `yao_2021_pos_count{track}` 并记 WARNING (新 schema 下不应触发)。计数本身是非负整数 (bank-year 内报道篇数之和), 不做任何标准化或缩尾, 单位是"篇数"。
【文献定位】
分子分母同域匹配是文本挖掘转分类文献里的通用度量学问题: 当分类器 (LLM 或词典规则) 存在拒判/缺失, 而计算比率类指标 (占比、意愿率) 时若分母仍用未经同一分类过滤的全样本, 会引入与分类失败率相关的系统性偏误。这与 Gentzkow, Kelly & Taddy (2019, *Journal of Economic Literature*) 综述文本量化方法时强调的"测度构造须显式核算分类不确定性传导路径"一脉相承——本家族即是把这一原则在洗稿率计算链路上具体落地为一组分母修正列。洗稿率本身的构念——"象征性语调多于实质性行动的报道占比"——呼应 Westphal & Zajac (1994, 2001, *Administrative Science Quarterly*) 关于象征性管理 (symbolic management) 与解耦 (decoupling) 的经典框架, 后续被 Fiss & Zajac (2006, *Academy of Management Journal*) 系统化为"框架化—解耦"机制。中文语境下的金融情感词典分支 (Loughran & McDonald 2011, *The Journal of Finance* 中文译介传统的直接后继) 是本家族赖以计分的词典来源之一; Yao (2021) 词典与 Bian, Jia, Li & Yan (2021, SSRN 3446388)、Ma, Zhang & Zhang (2025, *Expert Systems with Applications*) 构建的 CN-FSD 中文细粒度投资者情感词典同属为中文财经文本本地化构建的情感词表分支——后者明确以英文 L&M 词典为方法论蓝本、面向中国境内投资者语料重新标定正负词表, 与 Yao (2021)/Bian et al. (2021) 的本地化路径高度可比; 六部词典并列构成本项目词典消融梯度的横截面。实质性分类的 LLM 三家投票机制则见 CLAUDE.md「LLM 三家/BERT 三模型互为稳健性」条目, 三家各自 just-identified 并排, 本列的"实质性标签有效"判定即建立在该三家投票共识产出的 `innovation_substantiveness_full` 字段之上。

## VAR: yao_2021_pos_substvalid_count_ctx

【变体差分】
本列是三轨中的实体窗轨 (`_ctx`)。轨道差异体现在两处输入: 一是 `yao_2021_score_ctx` (词典逐词扫描的文本范围限定为标题+目标银行实体窗口, 而非全文), 二是同一篇报道判为阳性的门槛随扫描文本收窄而变化——ctx 轨只统计围绕目标银行实体窗口内的词典命中, 与 full 轨基于全文扫描的阳性判定可能不一致 (同一篇报道在 full 轨阳性、在 ctx 轨阴性, 或反之, 均属正常); 实质性标签 `innovation_substantiveness_full` 输入本身不随轨道变化 (该字段只有 `_full` 单轨版本, 三个 substvalid_count 列共享同一份实质性判定输入)。因此 ctx 与 full/ss 三列之间的差异完全来自词典阳性判定所依赖的文本范围, 而非实质性分类口径的差异。ctx 轨的分母是"实体窗内词典判阳 ∧ 实质性分类有效"的报道计数, 在下游用于 `washing_ratio_yao_2021_ctx` 的除法分母。三轨 (full/ctx/ss) 依 CLAUDE.md 铁律各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J; 无银行∧金科同句共现的报道在 ctx 轨仍以其实体窗口回退文本参与判定 (ctx 本身不设 `_is_fallback` 语义, 该回退语义专属 ss 轨), 因此 ctx 轨相对 full 轨是"窗口收窄"而非"缺失回退"关系。留篇门控依 2026-06-29 起的 full-only 口径: 一篇报道是否被计入"银行金科报道"总体由 `llm_verified_full` 判定, ctx 轨的行宇宙是该 full 留篇集的子集, 每轨内部再各自计算词典判定与实质性交叉。

## VAR: yao_2021_pos_substvalid_count_full

【变体差分】
本列是三轨中的全文轨 (`_full`), 是该家族的口径基准 (canonical), 也是留篇门控本身依附的轨道——stage 21 判定一篇报道是否算作"一篇有效银行金科报道"只看 `llm_verified_full`, 因此 full 轨的行宇宙就是全体留篇集, ctx/ss 是其 conditional-on-full 的子集测度。full 轨的词典阳性判定 `yao_2021_score_full > 0` 基于标题+全文正文文本逐词扫描 (jieba 分词 + 词典命中规则, 含否定翻转/程度副词/转折三条语言学规则的全规则 full 变体, 与消融梯度的其余 7 个非-full 变体正交), 实质性标签同样取自 `innovation_substantiveness_full` (本身即全文轨判定, 与本列轨道口径天然一致, 不存在跨轨错配问题——这也是三列中唯一"词典轨道"与"实质性判定轨道"严格同源的一列)。full 轨分母计数供 `washing_ratio_yao_2021` (无轨道后缀, 即主指标) 的除法分母消费。作为三轨中样本量最大、覆盖面最宽的一轨 (全文本扫描不受实体窗口/同句半径约束), full 轨通常给出三轨中最大的计数值, 但这只反映扫描文本范围更宽泛导致更多报道被判为词典阳性, 不代表 full 轨在方法论上优于 ctx/ss——三者依然是互为稳健性、不分主次的并排关系, 差异应作为文本范围敏感性披露, 而非以相关系数高低取舍主轨。

## VAR: yao_2021_pos_substvalid_count_ss

【变体差分】
本列是三轨中的银行∧金科同句轨 (`_ss`), 词典扫描文本限定为"目标银行实体与金科词在同一句 (±N 句窗, 默认 N=1) 内共现"的句子集合 (`config/filtering.yaml::context_window.ss_sentence_radius`); 判定原语与 stage 13 硬过滤所用的邻近共现判据 (`entity_context.py::has_bank_fintech_cooccurrence_within_radius`) 是不同口径的严格同句抽取函数, 二者不可互相复用。ss 轨镜像 ctx 轨的回退语义: 若某篇报道不存在银行∧金科同句共现, 则 `content_ss` 整体回退为全文 body、`ss_is_fallback` 标记为 True, 该报道仍以全文文本参与词典阳性判定, 与 ctx 轨的"实体窗内扫描"在文本粒度上不同但回退兜底逻辑一致 (共享 `n_articles` 分母口径); 若 `FINTECH_AC=None` (金科词典未加载), 则 `*_is_fallback` 对全体报道一律为 True, 优雅降级为等同全文轨的词典判定。因此 ss 轨的 substvalid 计数在同句共现覆盖率低的样本 (如 T=2 开发集小样本) 中可能与 full 轨高度趋同, 这是回退兜底导致的预期现象, 不代表 ss 轨测度失效。实质性标签输入同 ctx 轨, 统一取自 `innovation_substantiveness_full`, 不随 ss 轨道重新分类。ss 轨分母计数供 `washing_ratio_yao_2021_ss` 的除法消费, 与 full/ctx 两列共同构成三轨并排稳健性证据链, 禁止三者混入同一 over-identified 识别方程。三轨对比的解读须格外留意 ss 轨的窄口径特性: 严格同句共现是三种文本范围界定里最苛刻的一种, 命中率天然低于实体窗口 (ctx) 与全文 (full), 因此在样本较小的开发集上 ss 轨回退触发比例偏高、substvalid 计数与 full 轨趋同的现象属预期, 不应据此判定 ss 轨测度失灵或需要额外校准; 生产语料规模下, 同句共现命中率上升, 三轨数值差异会更充分地体现文本范围本身对词典阳性判定的影响。

<!-- rendered-citations:begin -->
Ma, Y., Zhang, T., & Zhang, P. (2025). The construction of a Chinese fine-grained sentiment dictionary for Chinese domestic investors (CN-FSD) and its application. Expert Systems with Applications, 264, 125739. https://doi.org/10.1016/j.eswa.2024.125739
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
Loughran, T., & McDonald, B. (2011). When is a liability not a liability? Textual analysis, dictionaries, and 10-Ks. The Journal of Finance, 66(1), 35-65. https://doi.org/10.1111/j.1540-6261.2010.01625.x
Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. Journal of Economic Literature, 57(3), 535-574. https://doi.org/10.1257/jel.20181020
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change: Sensegiving via framing and decoupling. Academy of Management Journal, 49(6), 1173-1193. https://doi.org/10.5465/amj.2006.23478255
<!-- rendered-citations:end -->
