---
family_id: F603
columns:
- washing_ratio_bert
- washing_ratio_bert_ctx
- washing_ratio_bert_ss
unit: 比率/占比 (proportion, [0,1]; 面板层年度聚合, 由文章级分类计数相除得到)
formula: 'washing_ratio_bert{track} = bert_pos_symb_count{track} / _svd_denom(bert_pos_substvalid_count{track}, bert_pos_count{track}); _svd_denom 为整列 schema 级兜底 (若 bert_pos_substvalid_count{track} 列存在于 panel 则整列采用之, 否则整列回退 bert_pos_count{track}), 非逐行取大值'
producer: "pipeline/panel/runner.py (方法 E: BERT 均值合成); pipeline/panel/export.py (Stata 标签注入, 含三轨机械派生循环)"
upstream: [pipeline/sentiment/tone_berts.py, pipeline/panel/encode.py, pipeline/panel/network_spillover.py]
citations:
- doi: 10.1016/j.frl.2022.102776
  type: journal
  authors: Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N.
  year: 2022
  title: "Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures"
  venue: Finance Research Letters
  vol: '47'
  pages_or_artno: '102776'
- doi: 10.2307/2393593
  type: journal
  authors: Westphal, J. D., & Zajac, E. J.
  year: 1998
  title: 'The symbolic management of stockholders: Corporate governance reforms and shareholder reactions'
  venue: Administrative Science Quarterly
  vol: '43'
  issue: '1'
  pages_or_artno: 127-153
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.18653/v1/N19-1423
  type: journal
  authors: Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K.
  year: 2019
  title: 'BERT: Pre-training of deep bidirectional transformers for language understanding'
  venue: Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT)
  pages_or_artno: 4171-4186
- doi: 10.1016/j.frl.2026.109684
  type: journal
  authors: Song, X., Hou, W., Ouyang, Z., & Hao, F.
  year: 2026
  title: 'AI washing: Strategic disclosure and backlash'
  venue: Finance Research Letters
  vol: '95'
  pages_or_artno: '109684'
new_dois: []
---

## CORE

【构念与来源】
washing_ratio_bert 家族刻画的是"洗稿"(washing) —— 媒体报道在情感基调上表现为正面, 但在内容实质上属于象征性 (symbolic) 而非实质性 (substantive) 陈述的比例。构念直接继承 Westphal & Zajac (1998, Administrative Science Quarterly) 关于公司治理改革"实质—象征"二分的经典框架: 企业(或此处为媒体报道)可以采纳某种正面表态而不伴随可验证的实质行动或事实内容, 从而制造"言而无实"的印象管理效果。该二分被移植到金融文本挖掘领域后, 常与 Bingler, Kraus, Leippold & Webersinke (2022, Finance Research Letters) 提出的"cheap talk vs. cherry-picking"判据相呼应 —— 后者用于识别企业气候信息披露中言辞正面但缺乏具体承诺的套话段落, 与本处银行金科报道中"正面但空洞"的判别逻辑同源。更晚近地, Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 在 "AI washing" 语境下把这一诊断思路系统化为策略性披露与市场反噬的实证框架, 说明"洗稿率"类测度已成为文本型公司传播研究中的一条活跃诊断线。washing_ratio_bert 是该诊断线在本项目情感三法 (LLM 投票 / 词典 / BERT) 中 BERT 一支上的具体实现: 分子锁定"正面且象征性" (pos & symb) 的文章计数, 分母锁定"正面且实质有效" (pos & substvalid, 退化时回落到全部正面 pos) 的文章计数, 比值越高说明该银行-年样本中的正面报道越多是"说得好听但缺实质内容"的洗稿式报道, 而非可验证的实质性正面报道。

【方法学与计算】
washing_ratio_bert 属于家族 E (BERT 均值) 的面板层派生列, 由 `pipeline/panel/runner.py` 的方法 E 区块在情感三法交叉表格已经产出文章级"实质/象征"标签与 BERT 三模型分类计数之后计算得到。上游链路分两层: 第一层是文章级分类, 由 substance-symbolic 判据 (镜像 W&Z 1998, 落地在本项目的 sub_frac/symb_frac 家族) 把每篇文章标注为实质性 (substantive) 或象征性 (symbolic) 新闻; 第二层是 BERT 三模型 (finbert_cn / fin_sent_zh / finbert2, SSOT = `encode.BERT_MODELS`) 各自对每篇文章的情感极性 (正/负/中性) 分类, 并按上述实质/象征标签交叉计数, 产出 `bert_pos_count{track}` (BERT 判正面的文章数)、`bert_pos_symb_count{track}` (BERT 判正面且象征性的文章数)、`bert_pos_substvalid_count{track}` (BERT 判正面且实质性判据有效的文章数)。面板层计算调用统一的安全除法算子 `_safe_ratio`, 分母采用 `_svd_denom` 兜底逻辑: 该逻辑是整列级的 schema 存在性判断而非逐行数值比较——若 `bert_pos_substvalid_count{track}` 列存在于 panel 的列集合中, 则整列采用该实质有效计数作分母; 若该列在 panel schema 中根本不存在 (旧版本产物缺失该列), 才整列回退到未过滤的正面计数 `bert_pos_count{track}` 并记录告警日志, 避免旧 schema 缺列时直接崩溃。真正的"零值/缺失值"处理发生在更下游的 `_safe_ratio` 算子内: 分母在数值上小于等于零时, 该行结果被置为 NaN, 这是与 `_svd_denom` 相互独立的另一道逐行防护, 二者不应混为一谈——`_svd_denom` 只负责"该用哪一整列做分母", `_safe_ratio` 才负责"某一行的分母数值是否合法可除"。washing_ratio_bert 是"BERT 均值" (方法 E) 版本, 即先对三个 BERT 模型的正面/正面-象征计数做汇总再计算比率 (家族内还有方法 E2 逐模型版本 `washing_ratio_{finbert_cn,fin_sent_zh,finbert2}{track}`, 与本家族互为稳健性, 详见相邻家族条目), 对应地家族内还有方法 D/D2 (词典均值/逐词典)、方法 F (高置信度子样本)、方法 G (情感偏移) 等并列诊断口径, 均以"实质 vs. 象征"这一底层分类为共同锚点, 分别从不同情感测度引擎给出洗稿率的稳健性证据。全部 washing_ratio_* 系列在 `export.py` 的列标签映射与标签派生循环中统一贴上 "WR: <method> (<track>)" 前缀, 三轨机械派生: 在 full/ctx 两个字面量标签基础上, `_ctx→_ss` 派生循环自动补全 `_ss` 轨标签, 保证三轨标签体系一致而不需逐条手写。

【文献定位】
washing_ratio_bert 所刻画的实质/象征二分构念源自 Westphal & Zajac (1998, Administrative Science Quarterly) 关于公司治理改革"言行分离"的经典理论, 本项目将其从公司治理决策场景迁移到媒体文本报道场景, 用以诊断银行金科报道中的"言而无实"现象。方法学上, 判别"正面但空洞"文本段落的思路呼应 Bingler et al. (2022, Finance Research Letters) 在气候信息披露文本中提出的 cheap-talk/cherry-picking 判据, 以及 Gorovaia & Makrominas (2024, European Financial Management) 用自然语言处理方法识别企业 ESG 报告中"洗绿"(greenwashing) 迹象的实证策略 —— 两者均属"正面情感 + 缺乏实质内容"的诊断范式, 本家族将其应用对象从企业自我披露文本 (10-K/ESG 报告) 扩展到第三方媒体报道文本。更晚近的 Song, Hou, Ouyang & Hao (2026, Finance Research Letters) 把这一诊断范式系统化到 "AI washing" 情境, 佐证"洗稿率"类测度在识别策略性正面表态与市场后续反噬关系上的持续学术生命力。BERT 分类引擎本身以 Devlin, Chang, Lee & Toutanova (2019, NAACL-HLT) 提出的 BERT 双向 Transformer 预训练范式为技术基础, 本项目在此基础上分别接入三个针对中文金融文本微调的 BERT 变体 (finbert_cn / fin_sent_zh / finbert2), 以三模型均值 (本家族) 与逐模型 (相邻家族) 两条口径互为稳健性地给出情感极性标签, 再与实质/象征标签交叉合成洗稿率。washing_ratio_bert 与家族内 washing_ratio_dict (词典引擎均值)、washing_ratio (LLM 投票)、washing_ratio_hc (高置信度子样本) 等并列口径共同构成"洗稿率"这一测度的跨引擎稳健性矩阵: 三种独立情感测度技术 (LLM 三家投票 / 六部词典 / 三个 BERT 模型) 分别产出各自的洗稿率估计, 彼此互为稳健性、不分主次, 任何一条口径与结构解释变量构造过度识别 Hansen J 检验时均须与其余口径分列并排、绝不混入同一 J 统计量, 以避免跨引擎相关性人为夸大过度识别自由度。

## VAR: washing_ratio_bert

【变体差分】
washing_ratio_bert 是本家族的 full 轨 canonical 列, 分子分母均取自标题+正文全文 (`content_full`, prepend_title 已内嵌标题) 上的 BERT 三模型正面/正面-象征交叉计数: `bert_pos_symb_count` / `_svd_denom(bert_pos_substvalid_count, bert_pos_count)`。full 轨是留篇门控 (2026-06-29 起) 的唯一门控轨: 一篇文章是否计入"银行金科报道"样本只看 `llm_verified_full == True`, 因此本列所依赖的分母/分子文章集合即为该门控下的行宇宙全集, 无需额外的子集限定。full 轨同时是三个正文长度最完整、覆盖信息量最大的观测口径 —— 不做实体窗口截断也不做同句限制, 因而在三轨谱系中提供的是"最宽松语境下、样本量最大"的洗稿率估计, 通常也是各 paper 主线回归中优先采用的测度轨。作为家族内三条并列轨道 (full/ctx/ss) 之一, washing_ratio_bert 与 washing_ratio_bert_ctx、washing_ratio_bert_ss 各自 just-identified 并排、互为稳健性、不分主次, 三者禁止混入同一过度识别 Hansen J 检验。同时, washing_ratio_bert 作为 BERT 均值方法 (方法 E) 的产出, 与同轨的方法 D (词典均值 washing_ratio_dict)、方法 A/LLM 投票 (washing_ratio)、方法 F (高置信度子样本 washing_ratio_hc) 等跨引擎稳健性口径并排, 三种情感测度技术各自独立提供洗稿率估计, 互不作为对方的稳健性检验基准, 而是共同构成对"洗稿"这一现象是否稳健存在的多引擎证据链; 与家族内方法 E2 (逐模型 washing_ratio_{finbert_cn,fin_sent_zh,finbert2}) 相比, 本列是三模型均值汇总口径, 用于抵消单一 BERT 模型特异性噪声, 而逐模型列则用于跨厂商/跨微调语料的模型间一致性检验, 两者同为 co-equal 不设 ensemble 优先级。

## VAR: washing_ratio_bert_ctx

【变体差分】
washing_ratio_bert_ctx 是本家族的 ctx (context) 轨, 计算公式与 canonical 列结构一致, 但分子分母 (`bert_pos_symb_count_ctx` / `_svd_denom(bert_pos_substvalid_count_ctx, bert_pos_count_ctx)`) 均取自 `content_ctx` (标题+实体窗口文本, 而非全文) 上重跑的 BERT 三模型分类与实质/象征交叉计数。ctx 轨在 full-only 留篇门控确立后, 其行宇宙被限定为 full 轨判定为"银行金科报道"的文章子集 (conditional-on-full), 即 ctx 轨不再独立决定一篇文章是否留样, 而是作为该留篇集合上的一条测度/稳健性轨, 用较窄的实体窗口文本重新验证洗稿率的方向与量级是否与 full 轨一致。相较 full 轨, ctx 轨剔除了与目标银行/金科实体无直接文本邻近关系的段落, 更贴近"报道正文中围绕该实体展开的论述是否空洞"这一诊断意图的字面语义, 但代价是可用文本量收窄, 在极短实体窗口下 BERT 分类的判据信号可能更稀薄; 若窗口内文本过短导致实质性判据无法有效判定, `_svd_denom` 兜底逻辑会自动回落到未过滤的正面计数分母, 与 full 轨共享同一降级规则, 不因轨道不同而改变分母兜底口径。ctx 轨与 full 轨、ss 轨各自 just-identified 并排、互为稳健性、不分主次, 三轨禁止混入同一过度识别 Hansen J 检验; 三轨之间不存在"以窄文本纠正宽文本"或反之的层级关系, 而是分别从"全文语境"与"实体局部语境"两个观测尺度给出洗稿率估计, 用以检验现象是否对文本窗口选择敏感。

## VAR: washing_ratio_bert_ss

【变体差分】
washing_ratio_bert_ss 是本家族的 ss (same-sentence) 轨, 分子分母 (`bert_pos_symb_count_ss` / `_svd_denom(bert_pos_substvalid_count_ss, bert_pos_count_ss)`) 取自 `content_ss` 文本上的 BERT 三模型分类与实质/象征交叉计数; `content_ss` 定义为标题与"银行∧金科同句 (±N 句窗口, 默认 N=1) 共现"片段拼接的文本。ss 轨的回退语义严格镜像 ctx 轨: 当某篇文章不存在银行与金科词汇同句共现时, `content_ss` 退化为全文 body, 对应 `ss_is_fallback=True` 标记, 且该回退文章仍计入 `n_articles` 分母 (与 ctx 轨共享同一回退语义与分母口径); 若 `FINTECH_AC=None` (金科词自动机未装载), 则 `*_is_fallback` 全部置 True, 三轨优雅降级为等价于 full 轨口径。与 ctx 轨相同, ss 轨在 full-only 留篇门控下同样是 conditional-on-full 的测度/稳健性轨, 行宇宙限定于 full 轨留篇集合的子集, 不独立参与是否留样的判定。washing_ratio_bert_ss 与 washing_ratio_bert (full)、washing_ratio_bert_ctx 各自 just-identified 并排、互为稳健性、不分主次, 三轨禁止混入同一过度识别 Hansen J 检验; ss 轨提供的是"银行-金科话题在同一句子内紧密并置"这一最严格语境窗口下的洗稿率估计, 与 ctx 轨 (实体窗口, 通常宽于单句) 和 full 轨 (全文) 共同构成从宽到窄三个文本粒度上的洗稿率稳健性谱系。由于同句共现条件比 ctx 轨的实体窗口更严格, ss 轨在生产语料上触发回退 (`ss_is_fallback=True`) 的文章占比通常高于 ctx 轨, 意味着本列的有效判别样本 (真正落在窗口内计算而非回退到全文的样本) 是三轨中最窄的一支, 解读回归系数时应结合该轨的回退占比一并考量, 避免把回退样本占比过高误读为现象本身的弱化。

<!-- rendered-citations:begin -->
Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking: What ClimateBert has to say on corporate climate risk disclosures. Finance Research Letters, 47, 102776. https://doi.org/10.1016/j.frl.2022.102776
Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders: Corporate governance reforms and shareholder reactions. Administrative Science Quarterly, 43(1), 127-153. https://doi.org/10.2307/2393593
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Devlin, J., Chang, M.-W., Lee, K., & Toutanova, K. (2019). BERT: Pre-training of deep bidirectional transformers for language understanding. Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics (NAACL-HLT), 4171-4186. https://doi.org/10.18653/v1/N19-1423
Song, X., Hou, W., Ouyang, Z., & Hao, F. (2026). AI washing: Strategic disclosure and backlash. Finance Research Letters, 95, 109684. https://doi.org/10.1016/j.frl.2026.109684
<!-- rendered-citations:end -->
</content>
