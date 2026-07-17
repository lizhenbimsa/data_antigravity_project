---
family_id: F258
novelty_exempt_rationale: "exc_ 前缀家族是姜富伟等(2021)词典情感得分在'剔除疑似退出覆盖媒体'存活子样本上的幸存者偏差稳健性变体, 测度定义依据母族词典与其原始文献, 非独立新构念, 无需追加新文献。"
columns:
- exc_jiang_2021_score_ctx
- exc_jiang_2021_score_full
- exc_jiang_2021_score_hw_ctx
- exc_jiang_2021_score_hw_full
- exc_jiang_2021_score_hw_ss
- exc_jiang_2021_score_ss
- exc_jiang_2021_score_w_ctx
- exc_jiang_2021_score_w_full
- exc_jiang_2021_score_w_ss
unit: 无量纲情感得分 (signed; 存活媒体 bank-year 均值)
formula: "exc_{src} = mean_{i ∈ 存活媒体(非停刊代理) 文章}( jiang_2021_score{后缀}{track}_i ); 后缀 ∈ {等权(无后缀, 直接对 jiang_2021_score{track} 取均值), _w=jiang_2021_score{track}_i × mention_density_i 的未归一化乘积列再直接取均值(非 Σ(score·w)/Σw 的归一化加权平均), _hw=jiang_2021_score{track}_i × herd_weight{track}_i 的未归一化乘积列再直接取均值(同非归一化加权平均)}; track ∈ {_full, _ctx, _ss}"
producer: news_process/pipeline/panel/attention_media.py
upstream:
- 22_tone_words.parquet (jiang_2021_score{,_w,_hw}{_full,_ctx,_ss} 文章级)
- 24_herd_decay_processor.parquet (herd_weight 三轨, 供 _hw 加权口径参照)
- "40_panel_export_main (attention_media 步骤 6b/6c: 停刊代理检测 + 存活子样本聚合)"
citations:
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
- doi: 10.1016/j.jfineco.2018.10.001
  type: journal
  authors: Jiang, F., Lee, J., Martin, X., & Zhou, G.
  year: 2019
  title: "Manager sentiment and stock returns"
  venue: Journal of Financial Economics
  vol: 132
  issue: 1
  pages_or_artno: 126-149
- doi: 10.13821/j.cnki.ceq.2021.04.10
  type: journal
  authors: 姜富伟, 孟令超, & 唐国豪
  year: 2021
  title: "媒体文本情绪与股票回报预测"
  venue: 经济学(季刊)
  vol: 21
  issue: 4
  pages_or_artno: 1323-1344
- doi: "10.2139/ssrn.5024959"
  type: "wp"
  authors: "Cziraki, P., & Gider, J."
  year: 2024
  title: "Newspaper Closures and Trading in Local Stocks"
  venue: "SSRN"
  pages_or_artno: "5024959"
new_dois: []
---

## CORE

【构念与来源】
本家族测量的是"排除疑似退出覆盖媒体后, 基于姜富伟等 (2021) 中文金融情感词典对银行相关报道所计的情感得分"在 bank-year 层的均值。前缀 exc 取自 exclude-ceased, 指该测度只在存活媒体子样本上聚合, 是一族服务于幸存者偏差 (survivorship bias) 稳健性的替代指标。词典本体来自姜富伟等 (2021) 为中文金融文本构建的情感词表, 该词典以中文金融语料切分与正负词标注为基础, 被证明对股票回报具有样本外预测力; 项目以其正负词集在文章级计算带程度副词放大、否定翻转与转折折减规则的带符号情感得分 jiang_2021_score, 再由本家族聚合到银行-年。得分为无量纲带符号量: 正值表示存活媒体对该银行的报道整体偏正面, 负值偏负面, 数值不做外部标准化, 只在同口径列之间横向可比。构念上它回答的问题是: 如果把那些在样本期内疑似停止覆盖该话题的媒体剔除掉, 银行的媒体情感画像是否依旧稳定, 从而排除"情感信号被存活媒体的自选择所污染"这一竞争性解释。

【方法学与计算】
计算分两步。第一步是停刊代理 (cessation proxy) 检测: attention_media 在面板导出步骤对每篇文章标注 _is_ceased_media, 判据是媒体来源在样本后段是否疑似退出对该话题的覆盖 (topic-exit), 而非经证实的报纸停刊; 源码显式声明这是保守代理, 下游 exc_* / n_articles_exc / ceased_media_frac 只能解读为"疑似退出覆盖媒体"的稳健性口径, 论文中不得表述为严格出版停刊。第二步是在存活子样本 df_alive (即 _is_ceased_media == 0 的文章) 上, 按 target_bank × year 分组对文章级得分求均值, 落成 exc_ 前缀列。得分层面存在三种后缀口径, 且须准确区分其统计构造: 无后缀为等权, 即直接对文章级 jiang_2021_score{track} 求 bank-year 均值, 每篇文章等权重进入。_w 与 _hw 并非归一化的加权平均 Σ(score·w)/Σw (encode.py 中 llm_vote_tone_hw/vw 等列才是这种严格意义上的加权均值), 而是在文章级先构造未归一化的"得分×权重"乘积列——jiang_2021_score_w{track} = jiang_2021_score{track} × mention_density, jiang_2021_score_hw{track} = jiang_2021_score{track} × herd_weight{track}——再对该乘积列直接取 bank-year 简单均值, 既不除以 Σweight 也不做任何量纲归一化。这意味着 _w / _hw 两族六列的数值量纲随权重 (mention_density / herd_weight) 的绝对大小整体漂移, 不能解读为"报道越充分/越独立的文章在均值中占据越大话语权"这一加权平均语义, 而应解读为"情感方向与报道强度 (提及密度或跟风衰减系数) 的交互强度"这一未归一化的复合信号: 数值同时携带情感符号与权重量级两重信息, 权重整体偏高的 bank-year 即便逐篇情感符号不变, 其 _w/_hw 列也会系统性偏离等权列的数值水平, 因此 _w/_hw 列与等权列之间不宜做数值量级上的直接对比, 只宜在同口径列内部做横向比较, 或用于检验"情感方向 × 权重强度"的联合信号是否稳健。文本侧存在三条并行轨道: full 轨为标题 prepend 全文正文, ctx 轨为标题加银行实体上下文窗口, ss 轨为标题加银行与金融科技同句共现窗口; ss 轨在无同句共现时按镜像 ctx 的回退语义退化为全文 body, 并共享 n_articles 分母。三加权口径 × 三轨道交叉给出本家族九列。零文章或全部媒体判为退出的 bank-year 情感类列按契约保持 NaN (不与计数类的 n_articles_exc 零填连坐)。

【文献定位】
本家族坐落在中文金融文本情感的词典法传统与媒体样本稳健性两条脉络的交叉处。词典法一端, 姜富伟等 (2021) 与 Du 等 (2022) 分别给出中文金融情感词典的构建与效度证据, Jiang 等 (2019) 则在英文语境证明经理层情绪 (以文本情感度量) 对股票回报的预测力, 三者共同支撑"词典法情感得分携带资产定价相关信息"的前提。方法可信度一端, van Atteveldt 等 (2021) 系统比较人工标注、众包、词典与机器学习四类情感测量, 指出词典法在特定语料上可能低估效度, 因而词典法结果应作为与机器学习/大模型法互为稳健性的一轨而非唯一真值; Frankel 等 (2022) 进一步在披露文本上直接对比机器学习与词典法情感, 为项目"多方法互为稳健性、不分主次"的设计提供先例。样本稳健性一端, 媒体来源在长面板中进出会引入幸存者偏差并污染基于媒体暴露的工具变量, exc 家族正是对此的针对性回应: 通过在剔除疑似退出媒体的子样本上重算情感得分, 检验主结论是否被媒体样本的时间构成变化所驱动。需强调本家族的三轨道、三加权口径互为稳健性并排, 各自 just-identified, 禁混进同一 over-identified 的 Hansen J 检验; 它们既不与全样本情感列互斥, 也不宣称比全样本更"真", 只是回答"剔除疑似退出媒体后信号是否稳定"这一单一稳健性问题。 就媒体退出本身的经济后果, Cziraki 与 Gider (2024) 以美国本地报纸的真实停刊事件为冲击, 实证显示报道供给退出会改变本地股票的交易行为, 说明媒体样本的进出并非无关的数据噪声, 而是具有真实经济后果的样本组成变化——这为 exc 家族在剔除疑似退出覆盖媒体后重算词典得分提供了现实动机。迁移边界须诚实交代: 该文为尚未经同行评审的工作论文, 其停刊判定取自外部事件数据、被解释变量为本地股票的交易活动; 本家族的 ceased_set 则是 detect_defacto_cessation 自语料内部推断出的「疑似退出覆盖」保守代理 (confirmed ∪ suspected), 并非严格的停刊事实, 且仅用于构造稳健性子样本, 不承担任何识别冲击的角色。
## VAR: exc_jiang_2021_score_full

【变体差分】
本列是 full 文本轨、等权 (无加权后缀) 口径下的存活媒体情感均值, 是本家族最接近 canonical 的参照列。full 轨的文本口径为标题 prepend 全文正文, 即把标题拼到正文之前后对整篇报道计词典情感, 覆盖面最广、召回最高。等权意味着每篇存活媒体文章以相同权重进入 bank-year 均值, 不因篇幅或跟风程度而增减话语权, 因而它对"典型一篇存活媒体报道的情感"给出无偏 (未加权) 估计。与 _w / _hw 的区别在于加权口径: 本列不做任何篇幅或跟风加权; 与 ctx / ss 的区别在于文本轨: 本列取全文而非实体窗口或同句窗口。相对全样本 (非 exc) 的姜氏情感列, 本列的唯一差分是把疑似退出覆盖媒体的文章从聚合分组中剔除, 从而检验情感信号是否稳健于媒体样本的时间构成变化。数值取无量纲带符号量, 正值表示存活媒体报道整体偏正面、负值偏负面, 不做外部标准化, 只在同口径列间横向可比; 其分母口径与计数类的 n_articles_exc 同源于存活子样本, 但情感均值列在零存活文章时按契约保持 NaN 而非零填, 以免与计数零填契约冲突而在下游 Stata 侧误判为真零情感。作为最接近 canonical 的参照, 本列通常充当稳健性表的基准行, 主结论应先对齐本列再与其余八轨/加权口径比较。它与家族内其余八列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_ctx

【变体差分】
本列是 ctx 文本轨、等权口径下的存活媒体情感均值。ctx 轨与 full 轨的唯一区别在文本范围: ctx 只取标题加银行实体上下文窗口 (银行实体附近的句子窗口), 而非整篇正文, 因而它把情感计算聚焦到真正谈及目标银行的局部语境, 牺牲召回换取更高的构念精度, 抑制正文中与银行无关段落带来的情感噪声。加权口径与 full 等权列一致 (每篇存活文章等权), 剔除疑似退出覆盖媒体的存活子样本口径也一致。相对同轨的全样本姜氏情感列, 本列差分仅为存活媒体子样本; 相对本家族的 _full 列, 差分仅为文本窗口从全文收窄到实体上下文窗口; 相对 _w / _hw 列, 差分为不施加篇幅或跟风加权。ctx 轨作为 full 轨的稳健性对照, 用来检验情感信号是否被正文中非银行语境的情感成分驱动: 若本列与 _full 列符号一致、量级相近, 则说明全文情感确由银行语境主导而非无关段落堆砌。数值为无量纲带符号量, 存活子样本零文章时按契约保持 NaN。因 ctx 窗口召回低于 full, 本列在报道稀薄的 bank-year 上更易出现小样本波动, 解读时应结合同格 n_articles_exc 观察分母厚度, 避免把窗口收窄引致的方差放大误读为情感变化。三轨道 (full/ctx/ss) 与三加权口径各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_ss

【变体差分】
本列是 ss 文本轨、等权口径下的存活媒体情感均值, 是三轨中构念最窄、最保守的一列。ss 轨的文本口径为标题加银行与金融科技同句共现窗口 (银行∧金科在同一句正负 N 句窗内共现的局部文本), 因而它只在报道确实把目标银行与金融科技并置讨论时才计入实质情感, 最贴近"银行金融科技叙事"这一核心构念。ss 轨采用镜像 ctx 的回退语义: 当某篇报道无银行与金科同句共现时, content_ss 退化为全文 body, ss_is_fallback 置真, 并与其余轨共享 n_articles 分母, 保证优雅降级而非丢样本。加权口径与其余等权列一致, 存活媒体子样本口径也一致。相对 _full / _ctx 列, 本列差分为文本窗口进一步收窄到同句共现窗口并带回退语义; 相对 _w / _hw 列, 差分为不施加加权。数值为无量纲带符号量, 存活子样本零文章时按契约保持 NaN。由于同句共现是三轨中最严格的判据, 在报道稀疏或未大量并置银行与金融科技的 bank-year 上, 大量文章走回退路径, 本列会向 ctx 口径收敛, 因而其独立信息量在样本稀薄时最弱、在报道密集的大行上最强; 使用时应把它当作"最保守构念下情感是否仍稳健"的下界检验, 而非首选主测度。ss 轨与 full/ctx 轨各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_w_full

【变体差分】
本列是 full 文本轨、_w 口径下的存活媒体情感均值。_w 并非归一化的加权平均: 文章级先构造未归一化乘积列 jiang_2021_score_w_full = jiang_2021_score_full × mention_density, 再对该乘积列直接取 bank-year 简单均值, 不除以 Σmention_density。因此本列数值同时携带情感符号与提及密度量级两重信息, 其绝对水平会随 bank-year 内 mention_density 的整体高低而系统性漂移, 不能解读为"报道越充分的文章获得越大权重"这一加权平均语义, 而应解读为"情感方向与提及密度的交互强度"这一复合信号。这与无后缀等权列的区别正在此处——等权列对文章级情感原始值直接求均值, _w 列对得分×提及密度的乘积求均值; 与 _hw 列的区别在于乘数不同——_hw 用 herd_weight 而非 mention_density。文本轨为 full (标题 prepend 全文正文), 与 ctx/ss 的差分在文本范围; 存活媒体子样本口径 (剔除疑似退出覆盖媒体) 与家族其余列一致。本列应与等权 _full 列的符号 (而非数值量级) 做比较: 若符号一致, 说明情感方向不因引入提及密度这一乘数而反转; 数值量级上的差异是乘数机制的必然结果, 不构成"情感信号对报道充分度敏感"的证据, 解读时不应把 _w 列与等权列的量级差异误判为异质性发现。数值为无量纲带符号量 (但量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN。它与家族其余八列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_w_ctx

【变体差分】
本列是 ctx 文本轨、_w 口径下的存活媒体情感均值。它在两个维度上分别偏离家族 canonical: 文本轨从 full 收窄到 ctx (标题加银行实体上下文窗口), 加权口径从等权切换到 _w。_w 并非归一化加权平均: 文章级先构造未归一化乘积列 jiang_2021_score_w_ctx = jiang_2021_score_ctx × mention_density, 再对该乘积列直接取简单均值, 数值量级随 mention_density 绝对大小漂移, 不宜解读为"提及更密集的报道贡献更大权重"这一加权平均语义。与 _w_full 的区别仅在文本轨 (实体窗口 vs 全文); 与等权 _ctx 列的区别仅在是否对得分×提及密度的乘积 (而非得分本身) 取均值; 与 _hw_ctx 的区别在乘数不同 (mention_density vs herd_weight)。存活媒体子样本口径 (剔除疑似退出覆盖媒体) 保持不变。本列应与 _w_full、等权 _ctx 两列做符号 (而非量级) 层面的交叉核对: 符号一致说明情感方向不因窗口收窄或引入提及密度乘数而反转; 量级差异是未归一化乘积机制的必然产物, 不构成额外的异质性证据。数值为无量纲带符号量 (量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN; 因 ctx 窗口召回本已低于 full, 叠加乘数后稀薄格上数值波动更大, 解读须结合分母厚度。三轨道与三口径各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_w_ss

【变体差分】
本列是 ss 文本轨、_w 口径下的存活媒体情感均值, 是 _w 族里构念最窄的一列。文本轨为标题加银行与金融科技同句共现窗口, 采用镜像 ctx 的回退语义 (无同句共现时退化为全文 body 并置 ss_is_fallback 真, 共享 n_articles 分母); _w 口径为文章级得分与 mention_density 的未归一化乘积再取简单均值 (jiang_2021_score_w_ss = jiang_2021_score_ss × mention_density, 非 Σ(score·w)/Σw 的归一化加权平均), 因而本列数值量级随 mention_density 绝对大小漂移。与 _w_full / _w_ctx 的区别在文本轨的收窄程度 (同句共现窗口 vs 全文/实体窗口); 与等权 _ss 列的区别仅在是否对乘积 (而非得分本身) 取均值; 与 _hw_ss 的区别在乘数 (mention_density vs herd_weight)。存活媒体子样本口径一致。本列检验的是在"银行金融科技同句叙事 + 未归一化提及密度乘数 + 仅存活媒体"三重最保守口径下情感方向是否稳定, 因而在数据稀疏时 (如 T=2 试跑) 最易退化为 NaN 或近零, 属预期行为而非缺陷。数值为无量纲带符号量 (量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN。三重收窄叠加意味着本列的独立信息量在整族里最有限, 一般不宜单独作主测度, 而应与 _w_full / _w_ctx 做符号层面的并置阅读以判断情感方向是否随文本窗口收窄而反转; 量级差异属乘数机制的必然产物, 不宜解读为稳健性衰减的证据。它与家族其余列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_hw_full

【变体差分】
本列是 full 文本轨、_hw (herd-weighted) 口径下的存活媒体情感均值。后缀 _hw 表示文章级先构造未归一化乘积列 jiang_2021_score_hw_full = jiang_2021_score_full × herd_weight_full, 再对该乘积列直接取 bank-year 简单均值, 并非 Σ(score·herd_weight)/Σherd_weight 的归一化加权平均。herd_weight 的谱系借 Tetlock 一脉的跟风衰减系数, 对同一事件短时间内被多家媒体扎堆重复报道赋予较低系数, 但由于本列不做归一化, herd_weight 的绝对水平会直接乘进最终数值, 数值量级因而随 bank-year 内跟风衰减系数的整体高低系统性漂移, 不能解读为"跟风扎堆报道被降权后情感均值更接近独立信息含量"这一严格加权平均语义, 只能解读为"情感方向与跟风衰减强度的交互信号"。这与等权列的区别在于是否对得分×herd_weight 的乘积取均值, 与 _w 列的区别在于乘数是 herd_weight 而非 mention_density。文本轨为 full (标题 prepend 全文正文), 与 ctx/ss 差分在文本范围; 存活媒体子样本口径 (剔除疑似退出覆盖媒体) 与家族其余列一致。本列应与等权 _full 列做符号层面的比较: 符号一致说明情感方向不因引入 herd_weight 乘数而反转; 数值量级差异是未归一化乘积机制的必然结果, 不应被误读为"原始情感被跟风报道放大"的独立异质性证据。数值为无量纲带符号量 (量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN。herd_weight 与 mention_density 是两条正交的乘数来源, 二者不应混同, 二者在本家族内均以未归一化乘积-均值的方式实现, 而非分别代表两种加权平均。它与家族其余八列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_hw_ctx

【变体差分】
本列是 ctx 文本轨、_hw 口径下的存活媒体情感均值。它在文本轨与加权口径两个维度上分别偏离家族 canonical: 文本轨从 full 收窄到 ctx (标题加银行实体上下文窗口), 加权口径从等权切换到 _hw。_hw 并非归一化加权平均: 文章级先构造未归一化乘积列 jiang_2021_score_hw_ctx = jiang_2021_score_ctx × herd_weight_ctx, 再对该乘积列直接取简单均值, 数值量级随 herd_weight 绝对大小漂移, 不宜解读为"对跟风扎堆报道降权后二者叠加聚焦银行语境"这一加权平均语义。与 _hw_full 的区别仅在文本轨; 与等权 _ctx 列的区别仅在是否对乘积取均值; 与 _w_ctx 的区别在乘数 (herd_weight vs mention_density)。存活媒体子样本口径保持不变。本列应与 _hw_full、等权 _ctx 两列做符号层面的交叉核对: 符号一致说明情感方向不因窗口收窄或引入 herd_weight 乘数而反转; 量级差异是未归一化乘积机制的必然产物。数值为无量纲带符号量 (量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN; 因 ctx 窗口召回本已低于 full, 叠加乘数后稀薄格上数值波动更大, 解读须结合分母厚度。三轨道与三口径各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: exc_jiang_2021_score_hw_ss

【变体差分】
本列是 ss 文本轨、_hw 口径下的存活媒体情感均值, 是 _hw 族里构念最窄的一列。文本轨为标题加银行与金融科技同句共现窗口, 采用镜像 ctx 的回退语义 (无同句共现时退化为全文 body 并置 ss_is_fallback 真, 共享 n_articles 分母); _hw 口径为文章级得分与 herd_weight 的未归一化乘积再取简单均值 (jiang_2021_score_hw_ss = jiang_2021_score_ss × herd_weight_ss, 非 Σ(score·w)/Σw 的归一化加权平均), 因而本列数值量级随 herd_weight 绝对大小漂移。与 _hw_full / _hw_ctx 的区别在文本轨的收窄程度 (同句共现窗口 vs 全文/实体窗口); 与等权 _ss 列的区别仅在是否对乘积取均值; 与 _w_ss 的区别在乘数 (herd_weight vs mention_density)。存活媒体子样本口径 (剔除疑似退出覆盖媒体) 一致。本列检验的是在"银行金融科技同句叙事 + 未归一化跟风衰减乘数 + 仅存活媒体"三重最保守口径下情感方向是否稳定, 在数据稀疏时最易退化为 NaN 或近零, 属预期退化。数值为无量纲带符号量 (量纲随权重绝对大小漂移), 存活子样本零文章时按契约保持 NaN。三重收窄叠加令本列成为整族信息量最有限、也最保守的一列, 一般不宜单独作主测度, 而应与 _hw_full / _hw_ctx 做符号层面的并置阅读以判断情感方向是否随文本窗口收窄而反转; 量级差异属乘数机制的必然产物, 不宜解读为稳健性衰减的证据。它与家族其余列各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
van Atteveldt, W., van der Velden, M. A. C. G., & Boukes, M. (2021). The validity of sentiment analysis: Comparing manual annotation, crowd-coding, dictionary approaches, and machine learning algorithms. Communication Methods and Measures, 15(2), 121-140. https://doi.org/10.1080/19312458.2020.1869198
Jiang, F., Lee, J., Martin, X., & Zhou, G. (2019). Manager sentiment and stock returns. Journal of Financial Economics, 132(1), 126-149. https://doi.org/10.1016/j.jfineco.2018.10.001
姜富伟, 孟令超, & 唐国豪. (2021). 媒体文本情绪与股票回报预测. 经济学(季刊), 21(4), 1323-1344. https://doi.org/10.13821/j.cnki.ceq.2021.04.10
Cziraki, P., & Gider, J. (2024). Newspaper Closures and Trading in Local Stocks. SSRN No. 5024959 [Working Paper]. https://doi.org/10.2139/ssrn.5024959
<!-- rendered-citations:end -->
