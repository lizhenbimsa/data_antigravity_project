---
family_id: F239
columns:
- exc_bian_2021_score_raw_ctx
- exc_bian_2021_score_raw_full
- exc_bian_2021_score_raw_ss
unit: 情感倾向分值 (无量纲, 自归一化 ∈ [-1, +1]; bank-year 均值)
formula: "exc_bian_2021_score_raw_{track} = mean over articles from non-ceased media of bian_2021_score_raw_{track}; bian_2021_score_raw = Σ(signed_match) / Σ|signed_match|, 零语言学规则 (apply_negation=apply_degree=apply_adversative=False)"
producer: news_process/pipeline/panel/attention_media.py::compute_media_heterogeneity (C.4 停刊稳健性 exc-media 均值循环)
upstream:
- 22_tone_words.parquet (bian_2021_score_raw_{full,ctx,ss} 文章级得分)
- 面板装配期媒体元数据 (attention_media.compute_media_heterogeneity 对文章级 df 运行 detect_defacto_cessation, 就地产临时列 _is_ceased_media 停刊标记, 不落盘于 40_panel_yearly.parquet)
citations:
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
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1080/19312458.2020.1869198
  type: journal
  authors: van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M.
  year: 2021
  title: "The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms"
  venue: Communication Methods and Measures
  vol: 15
  issue: 2
  pages_or_artno: 121-140
- doi: 10.2139/ssrn.3446388
  type: wp
  authors: Bian, S., Jia, D., Li, F., & Yan, Z.
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: SSRN Working Paper
  pages_or_artno: No. 3446388
new_dois: []
---

## CORE

【构念与来源】
本家族度量在剔除疑似退出覆盖的媒体来源之后, 银行-年层面基于 Bian et al. (2021) 中文金融情感词典、零语言学规则口径计得的情感倾向均值。列名前缀 exc_ 的语义不是"排他词典"或"独占词", 而是 exclude-ceased-media (排除停刊媒体): 上游 detect_defacto_cessation 把在样本末段若干年不再产出银行-金科报道的媒体标记为疑似覆盖退出 (de-facto coverage cessation), 本家族只对存活媒体 (非停刊子集) 的文章重算词典情感均值, 作为幸存者偏差 (survivorship bias) 的稳健性对照轨。中间词根 bian_2021 指该情感倾向来自 Bian et al. (2021) 构建的中文金融文本情感词典 (褒贬词表), 词尾 raw 指规则消融梯度中的 L0 零规则基线变体: 逐词打分时既不施加否定翻转、也不施加程度副词六级缩放、更不施加转折连词增强, 只对命中词典的褒义词记正、贬义词记负后做自归一化。因此每一列都可以读作"在去掉可能因媒体消失而污染样本的观测、且不做任何中文语法修饰规则的前提下, 这家银行这一年被报道的金融情感底色是偏正还是偏负"。

【方法学与计算】
文章级底料在 stage 22 (22_tone_words.parquet) 生成: 对每篇报道的每条轨道文本分词后, 逐 token 状态机以 apply_negation=apply_degree=apply_adversative 三个开关全部关闭的方式扫过 Bian et al. (2021) 词表, 命中正极词累加 +1 幅度、命中负极词累加 -1 幅度, 最终得分 = Σ(signed) / Σ|signed|, 恒有界于 [-1, +1] (分母为加权幅度绝对值之和, 见 tone_words 归一化修正)。零规则口径使这一列成为整条规则消融梯度 (raw / negonly / degonly / advonly / negdeg / negadv / degadv, 以及施加全部三条规则的无后缀 canonical score) 的最下沿基线。随后在面板装配阶段, compute_media_heterogeneity 先由 detect_defacto_cessation 依据每家媒体的首末报道年份与最小报道量识别疑似覆盖退出集 (confirmed ∪ suspected, 并经 NPPA 新闻出版机构注销/停办/休刊名录交叉验证仅改报告标签、不收窄排除集), 在 df_alive (_is_ceased_media == 0) 子集上按 target_bank × year 分组对 bian_2021_score_raw_{track} 取均值, 左连接回面板得到本家族三列。分母为该银行-年在存活媒体上的报道篇数, 未报道格保持 NaN (比例/情感类按契约不做零填, 只有计数类如 n_articles_exc 填 0)。

【文献定位】
词典法情感测度在会计金融文本分析中长期作为"透明、可复现、跨观测稳定"的旁证工具与大模型/BERT 情感互为稳健。Du et al. (2022) 系统比较多部中文金融情感词典, 论证语言与领域专用词表相对英文直译词表在中文语料上的增益, 为选用 Bian et al. (2021) 这类本土词典提供依据; Bian et al. (2021) 本身即针对会计金融文本构建中文情感词表。Frankel et al. (2022) 在 Management Science 上比较机器学习与词典法披露情感, 确立"两法并行、以一致性互证"的稳健性范式, 正是本项目把词典情感与三家 LLM、三部 BERT 并列的先例。van Atteveldt et al. (2021) 通过人工标注、众包、词典与机器学习四法对照, 揭示词典法作为独立测量通道的效度边界。Barbaglia et al. (2025) 在 Economic Inquiry 系统阐述经济文本的 lexicon-based 打分框架, 其纯词表计数思路与本家族的 raw 零规则口径直接对应。停刊剔除动机则承接报纸退出地方覆盖引入选择偏误的实证脉络。凡涉三轨 (full/ctx/ss) 者, 三条轨道各自 just-identified 并排、互为稳健性、不分主次, 严禁混进同一 over-identified Hansen J; 留篇门控为 full-only (2026-06-29), ctx/ss 系 conditional-on-full 测度轨, 其行宇宙是 full 留篇集的子集。

## VAR: exc_bian_2021_score_raw_ctx

【变体差分】
本列是 exc_bian_2021_score_raw 家族的 ctx 轨变体, 差分维度是轨道文本口径。ctx 轨的底料文本 content_ctx = 标题 prepend + 含目标银行的句子及其 ±1 句窗口 (context window), 即把情感打分收窄到与目标银行邻近的语境段, 而非全文。相对 full 轨, ctx 剔除了与目标银行无关的段落噪声, 使词典情感更聚焦于涉行语境; 相对 ss 轨, ctx 只要求命中目标银行、不额外要求金科词同句共现, 因而语境窗口更宽。其余口径与家族一致: 停刊剔除 (仅对非停刊存活媒体的文章取 bank-year 均值)、Bian et al. (2021) 词典、raw 零规则 (无否定/程度/转折修饰) 自归一化。在留篇门控 full-only 框架下, ctx 属 conditional-on-full 稳健性轨, 其行宇宙是 full 留篇集的子集, per-track 分母为该银行-年存活媒体上的 ctx 轨有效报道篇数。ctx 与 full、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。dev 语料 T=2 上 ctx 轨可能出现窗口内命中稀疏而方差退化, 属预期, 生产 T=18 恢复正常。需强调 ctx 轨与家族无后缀 canonical (施加全部三条中文语法规则) 的区别正交于本轨道差分: raw 词尾锁定零规则, ctx 词缀锁定语境窗口, 两个维度互不干涉。停刊剔除口径在 ctx 轨与 full/ss 完全一致 — 均只对 detect_defacto_cessation 判定为非退出覆盖的存活媒体文章取均值, 因此本列与不剔停刊的对应主轨 (bian_2021_raw_tone_ctx) 之差, 恰是幸存者偏差方向的稳健性证据, 而非另一个独立信号。

## VAR: exc_bian_2021_score_raw_full

【变体差分】
本列是 exc_bian_2021_score_raw 家族的 full 轨变体, 也是留篇门控意义上的基准轨道。full 轨底料文本 content_full = 标题 prepend + 全文正文, 即对整篇报道 (不做语境收窄) 施加 Bian et al. (2021) 词典的 raw 零规则打分, 再在剔除疑似停刊媒体后按 target_bank × year 取存活媒体子集均值。full 轨承载留篇门控: 一篇报道是否计入某银行-年的报道宇宙, 由 full 轨 llm_verified 判定 (full-only 门控, 2026-06-29), 因此 full 轨的行宇宙是最完整的留篇集, ctx/ss 两轨的行集合皆为其子集。相对 ctx/ss 两轨, full 轨纳入全文所有涉情感词汇, 覆盖面最广但也可能引入与目标银行关系较弱段落的情感, 恰因此三轨并置才构成语境粒度上的稳健性阶梯。其余口径与家族一致: 停刊剔除、raw 零规则、自归一化 ∈ [-1, +1]。full 与 ctx、ss 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。分母为该银行-年在非停刊存活媒体上的 full 轨报道篇数, 无报道格保持 NaN (情感/比例类不做零填, 与计数类 n_articles_exc 填 0 的契约刻意分离)。full 轨的 raw 零规则口径使本列成为整条规则消融梯度在最广语境上的最下沿基线: 它与家族无后缀 canonical (施加否定翻转、程度缩放、转折增强三规则) 的 full 轨之差, 度量的正是三条中文语法修饰规则对情感强度的净贡献, 而与停刊剔除、轨道语境两个差分维度彼此正交、互不交叉。

## VAR: exc_bian_2021_score_raw_ss

【变体差分】
本列是 exc_bian_2021_score_raw 家族的 ss 轨变体, 差分维度是最严格的同句共现语境口径。ss 轨底料文本 content_ss = 标题 prepend + 目标银行∧金科词在同一句共现的句子及其 ±N 句窗口 (ss_sentence_radius, 默认 1), 即只保留银行与金融科技真正同句相邻出现的语境段做情感打分, 是三轨中语境最窄、涉行涉金科信号最纯的一轨。回退语义镜像 ctx: 当某篇报道不存在银行∧金科同句共现时, content_ss 回退为全文 body 且 ss_is_fallback=True, 与 ctx 的回退口径一致; 若 FINTECH_AC 词表缺失则 *_is_fallback 全 True 优雅降级。其余口径与家族一致: 停刊剔除 (仅存活媒体)、Bian et al. (2021) 词典、raw 零规则自归一化。在留篇门控 full-only 框架下, ss 属 conditional-on-full 稳健性轨, 行宇宙是 full 留篇集子集, per-track 分母为该银行-年存活媒体上的 ss 轨有效报道篇数。ss 与 full、ctx 三轨各自 just-identified 并排、互为稳健性、不分主次, 严禁三轨混进同一 over-identified Hansen J。dev 语料 T=2 上 ss 轨常因同句共现稀疏而近零方差, 属预期退化, 生产 T=18 正常。ss 轨与 ctx 轨的判定不对称口径须区分: 银行侧采否定+短名过滤, 金科侧采裸 AC 词表匹配。本列同时叠加停刊剔除与最严语境窗口两层收窄, 因而在三轨中样本最薄、信号最纯; 其与不剔停刊的对应主轨之差仍是幸存者偏差方向的稳健性证据, 与 raw 零规则、ss 语境两个差分维度彼此正交, 不并入同一识别式。

<!-- rendered-citations:begin -->
Barbaglia, L., Consoli, S., Manzan, S., Tiozzo Pezzoli, L., & Tosetti, E. (2025). Sentiment analysis of economic text: A lexicon-based approach. Economic Inquiry, 63(1), 125-143. https://doi.org/10.1111/ecin.13264
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper No. No. 3446388 [Working Paper]. https://doi.org/10.2139/ssrn.3446388
<!-- rendered-citations:end -->
