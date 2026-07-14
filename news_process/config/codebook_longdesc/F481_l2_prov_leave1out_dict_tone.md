---
family_id: F481
columns:
- prov_leave1out_dict_tone_ctx
- prov_leave1out_dict_tone_full
- prov_leave1out_dict_tone_ss
unit: 语调得分 (连续, 词典法综合语调 dict_avg_tone 的省级同侪均值, 约在 [-1,1] 区间; bank-year 面板层聚合)
formula: 'prov_leave1out_dict_tone_{trk} = ( sum_{j in same_province,year} dict_avg_tone_{trk,j} - dict_avg_tone_{trk,i} ) / ( n_{province,year} - 1 ), 先对该轨全表 (跨全部省份/年份汇总) 非缺失样本量作 <5 的全局最小样本守卫 (不足则整轨全部跳过不产出), 通过后逐 (省份,年份) 组要求组内有效银行数 > 1 (即 >=2 家, 不要求 >=5) 才对该组内各行赋值, 组内仅 1 家银行时该组记为缺失'
producer: pipeline\panel\geography.py (compute_leave1out_geo_iv 族循环体, extra_tone_cols/_OUT_STEM 派生段) ; 标签登记于 pipeline\panel\export.py (变量标签字典)
upstream:
- dict_avg_tone_full
- dict_avg_tone_ctx
- dict_avg_tone_ss
- bank_province
citations:
- doi: "10.1093/rof/rfab036"
  type: journal
  authors: "Du, Z., Huang, A. G., Wermers, R., & Wu, W."
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: "Review of Finance"
  vol: "26"
  issue: "3"
  pages_or_artno: "673-719"
- doi: "10.1287/mnsc.2021.4156"
  type: journal
  authors: "Frankel, R., Jennings, J., & Lee, J."
  year: 2022
  title: "Disclosure sentiment: Machine learning vs. dictionary methods"
  venue: "Management Science"
  vol: "68"
  issue: "7"
  pages_or_artno: "5514-5532"
- doi: "10.2139/ssrn.3446388"
  type: wp
  authors: "Bian, S., Jia, D., Li, F., & Yan, Z."
  year: 2021
  title: "A new Chinese financial sentiment dictionary for textual analysis in accounting and finance"
  venue: "SSRN Working Paper"
- doi: "10.1016/j.jfineco.2022.11.006"
  type: journal
  authors: "García, D., Hu, X., & Rohrer, M."
  year: 2023
  title: "The colour of finance words"
  venue: "Journal of Financial Economics"
  vol: "147"
  issue: "3"
  pages_or_artno: "525-549"
new_dois: []
---

## CORE

【构念与来源】
本家族 (F481) 度量的构念是"同省份其他银行的年度平均词典法语调, 排除本行自身" (province leave-one-out dictionary tone), 属于 Luo & Li (2025, FRL) 一支地理同侪构造的工具变量族在词典法测度上的具体实现。它不是对某家银行自身新闻语调的直接刻画, 而是把该行所在省份内其余银行的 `dict_avg_tone` 取算术均值 (排除自身), 用作捕捉"地区性媒体环境/行业景气度"共同冲击的代理变量。其经济含义建立在两个前提上: 一是同省银行常共享相近的区域宏观基本面、监管辖区与地方媒体生态, 使得同省同侪的语调呈现出与被解释变量 (个体银行自身语调) 相关的共同成分; 二是排除自身 (leave-one-out) 后, 该均值理论上不直接受被解释银行自身经营行为的机械反馈影响, 从而降低了"个体语调既是解释变量又是构造材料"带来的机械性内生 (mechanical reflection) 问题。该构念在 pipeline 内被登记为 provisional 类 (`l2_prov_` 词干), 意指其定位是候选工具变量族的一支, 供后续 IV 识别策略筛选与稳健性对照使用, 而非某篇论文的默认主处理变量。

本家族的直接输入是词典法综合语调 `dict_avg_tone_{full,ctx,ss}` (stage 22 六词典聚合而来的 canonical 词典测度), 以及银行注册地省份标识 `bank_province` (来自银行面板标识符骨架的地理信息, 见 geography.py 中 `_GEO_REFERENCES` 引用的 Luo & Li 2025, FRL, Table A.2)。producer 端 (`pipeline\panel\geography.py`) 在同一循环体内, 除本词典法语调外, 还并行产出 BERT 正面概率的省级/城市级 leave-one-out 均值 (`prov_leave1out_bert_avg_pos_*`、`city_leave1out_bert_avg_pos_*`), 二者共同构成"多情感度量 LOO IV 扩展" (源码标注 G-08), 学术依据是过度识别检验 (Hansen J test) 要求至少两个相互独立的工具变量; 若 `llm_vote_tone`、`dict_avg_tone`、`bert_avg_pos` 三支度量各自的 LOO IV 均可用, 则可以在 Stata 中对同一构念的多种测量实现执行 overid 检验。本家族三列即该扩展中"词典法"一支在省级地理粒度上的产出; 城市级同源姊妹列 (`city_leave1out_dict_tone_*`) 属另一独立家族, 二者共享同一构造逻辑但地理粒度不同, 不应混同或相加。

需要特别澄清一个命名史实: producer 注释记录了一次列名压缩修复 (`omni-g-panel-export-04`, 2026-06-11)。原始拟定列名 `prov_leave1out_dict_avg_tone_full` 长达 33 字符, 超过 Stata 变量名 32 字符上限, 曾被 `sanitize_stata_columns` 单侧截断, 导致同一构念的 full/ctx 两轨在落盘后词干不对称 (一支保留 `dict_avg_tone` 词干, 另一支被压缩), 使得 Stata 通配符 `*_leave1out_dict_avg_tone_*` 只能捕获其中一轨, 造成三轨对称性的静默破坏。修复方案是把词干统一压缩为 `dict_tone` (即本家族列名中的 `dict_tone`), 使 full/ctx/ss 三轨在压缩后字符数上均 ≤32、无需再触发单侧截断, 从而恢复三轨命名的完全对称。这段历史提示读者: 本家族列名中的 "dict_tone" 是 "dict_avg_tone" 的产出端词干压缩, 二者指代同一构念, 不是两种不同的词典测度。

【方法学与计算】
计算发生在 stage 40 之后的面板导出/地理扩展环节 (`geography.py` 内 leave-one-out 地理 IV 构造函数), 输入是已完成 bank-year 聚合的面板 `dict_avg_tone_{trk}` 列与 `bank_province` 列。具体步骤须区分两层不同粒度的门槛, 二者不可混为一谈: 第一层是"全表最小样本守卫"——先筛出 `bank_province` 非空且 `dict_avg_tone_{trk}` 非缺失的样本子集 (此时尚未按省份-年份分组, 是跨全部省份/年份汇总后的整表行数), 若该子集总行数小于 5, 直接跳过该轨的全部输出 (整个 `_{trk}` 列在本次导出中不产出任何值), 用意是避免在词典法语调本身覆盖度过低的极端情形下 (例如整轨几乎全为缺失) 仍强行构造几乎无信息量的同侪均值。第二层才是真正逐组决定"这一行是否有值"的门槛——通过第一层守卫后, 按 (省份, 年份) 分组计算 `dict_avg_tone_{trk}` 的组内和 (`transform('sum')`) 与组内计数 (`transform('count')`), 只对组内计数 > 1 (即该省该年至少有 2 家银行有效) 的行赋值, 执行 `(组内和 - 自身值) / (组内计数 - 1)`, 得到排除自身后的组内均值; 组内仅 1 家银行时该行的 leave-one-out 分母为 0, 直接记为缺失, 这是方法论上正确的处理 (无法从自身推断"其他银行"的地区语调), 而非"样本不足 5 家"的门槛。也就是说, 单个 (省份, 年份) 组只需 2 家银行即可产出该组内各行的值, 5 这个数字只出现在跨组汇总的全局守卫上, 并非逐组必须满足的组规模下限。producer 端还额外记录诊断日志 (有效值计数与"单一银行组"计数), 用于事后核查是否存在因组内银行数过少 (仅 1 家) 而无法产出的省份。

三轨语义严格镜像其上游 `dict_avg_tone_{full,ctx,ss}` 三轨: `_full` 轨的输入是基于全文文本 (标题+正文) 计算的词典法语调; `_ctx` 轨的输入是基于标题+目标银行实体窗口文本计算的词典法语调; `_ss` 轨的输入是基于标题+银行与金科同句共现窗口 (±N 句, 默认半径 1) 计算的词典法语调, 当某篇文章不存在银行∧金科同句共现时, `_ss` 轨按 CLAUDE.md 铁律回退为全文 body (`ss_is_fallback=True`), 与 `_ctx` 轨的回退语义完全镜像。三轨在本家族内各自独立完成"省份分组—求和—排除自身求均值"的全部步骤, 即 `_ctx` 轨的 leave-one-out 计算只使用 `dict_avg_tone_ctx` 作为输入, 与 `_full`/`_ss` 轨互不借用彼此的文本口径或分母。按 CLAUDE.md 载明的口径铁律, full/ctx/ss 三轨在识别策略层面各自 just-identified 并排、互为稳健性、不分主次, 严禁把三轨同时塞进同一个 over-identified 的 Hansen J 检验框架; 同理, 本家族 (词典法 leave-one-out) 与同一 G-08 扩展下的 LLM/BERT leave-one-out IV 族之间是"多种测量实现互为稳健性"的关系, 而不是彼此嵌套或相加的关系, 只有在明确构造"多工具-单内生变量"的过度识别检验时, 才允许把词典法、LLM 投票法、BERT 三支 leave-one-out IV 并列作为独立工具变量同时纳入同一 Hansen J 统计量。

值得强调的是, 词典法语调 `dict_avg_tone` 本身是六个词典 (含中国金融情感专用词典与通用中文情感词典) 综合聚合、并叠加语言学消融规则的产物; 本家族的 leave-one-out 聚合发生在这一综合语调之上, 不再重复六词典与语言学规则消融的内部差异, 而是把 `dict_avg_tone` 视为一个既定的单一输入序列。因此本家族与词典消融梯度家族 (`{dict}_score_{raw,negonly,degonly,...}`) 属于不同层级的稳健性维度: 前者是"同一综合词典测度在不同地理同侪范围上的工具变量化", 后者是"词典测度本身在语言学规则组合上的消融"; 二者正交, 不应混淆或相互替代。

【文献定位】
地理同侪 leave-one-out 均值作为工具变量的构造思路直接呼应 Du, Huang, Wermers & Wu (2022, Review of Finance) 建立中文金融情感词典 (即本 pipeline 词典法综合测度所依赖的核心词典之一) 时对词典法情感测度信度与外部效度的系统性检验, 该文强调金融语境专用词典相较通用词典在中国资本市场文本上的显著优势, 是本家族上游 `dict_avg_tone` 构念合法性的直接文献支撑。Frankel, Jennings & Lee (2022, Management Science) 系统比较了机器学习法与词典法两类情感测度在信息含量与预测力上的差异, 明确指出词典法情感测度与机器学习法情感测度可以互为稳健性对照而非相互替代, 这为本项目在 stage 21 (LLM) / 22 (词典) / 23 (BERT) 三法并行、并在 G-08 扩展中把三法各自的 leave-one-out IV 并排构造过度识别检验提供了直接的方法论先例。Bian, Jia, Li & Yan (2021, SSRN working paper) 提出的中文金融情感词典是本 pipeline 词典聚合池中的另一支核心词典 (对应家族 F127-F136 一族), 其构造经验 (二元极性词表在会计与金融文本上的适用性) 支撑了本家族上游综合词典测度的内容效度。García, Hu & Rohrer (2023, Journal of Financial Economics) 对"金融词汇色彩"的系统性研究进一步佐证了词典法情感测度在识别财经文本情感倾向时的稳健性边界及其局限, 提示读者在解读本家族的省级同侪语调差异时需注意词典法测度本身固有的语境敏感性。

在识别策略脉络上, 本家族服务于 Luo & Li (2025, FRL, Table 3) 一支"地理同侪杠杆"工具变量构造思路: 用同区域其他被解释对象 (银行) 的媒体语调均值作为工具, 以处理媒体报道语调与银行自身经营/融资决策之间可能存在的联立性偏误。该识别策略的成立前提隐含"同省银行共享区域性媒体冲击, 但个体银行自身语调不直接决定同省其他银行语调"这一排他性假设, 使用者在将本家族列作为工具变量代入 2SLS/IV 回归前应结合具体研究设计单独检验该假设的合理性 (例如是否存在跨行传染或竞争性新闻叙事的反向渠道)。

## VAR: prov_leave1out_dict_tone_ctx

【变体差分】
本列是 F481 家族在 `_ctx` (标题+目标银行实体窗口) 文本轨上的 leave-one-out 实现: 其唯一输入序列是 `dict_avg_tone_ctx`, 即同一省份、同一年份内其他银行基于 `_ctx` 轨词典法语调的均值 (排除自身), 计算规则 (跨全轨的 <5 行全局最小样本守卫、组内有效银行数 >1 才产出、组内和减自身再除以 n-1) 与家族其余两轨完全一致, 差异只体现在上游语调序列的文本口径不同。`_ctx` 轨的文本窗口聚焦标题与目标银行实体附近语境, 相较 `_full` 轨排除了与该银行实体距离较远的段落噪声, 相较 `_ss` 轨又不要求银行与金科词严格同句共现, 因此其省级同侪均值可以理解为"聚焦银行实体本身语境的地区性语调基准", 适合在识别策略上作为 `_ctx` 轨主处理变量 (若研究设计以 `_ctx` 轨语调为内生解释变量) 的配套工具变量使用。按留篇门控 full-only 铁律 (2026-06-29 起), `_ctx` 轨的样本行宇宙是 full 轨留篇集合的条件子集, 即某篇报道是否被计入"银行金科报道"由 `llm_verified_full` 单一判定, `_ctx` 轨只是在该既定行集合上提供额外的测度/稳健性视角, 本列继承这一行宇宙约束: 若上游 `dict_avg_tone_ctx` 因该门控而在某些 bank-year 缺失, 本列的省级分组求和与计数会相应减少参与银行数; 逐 (省份, 年份) 组只需组内有效银行数 > 1 即可产出该组, 减少到仅剩 1 家银行时该组才整体输出缺失 (并非需 >=5 家)。

## VAR: prov_leave1out_dict_tone_full

【变体差分】
本列是 F481 家族在 `_full` (标题+全文正文) 文本轨上的 leave-one-out 实现, 也是家族内文本覆盖面最广的一轨: 其输入 `dict_avg_tone_full` 基于文章全文计算, 不做实体窗口或同句共现的裁剪, 因而在词汇覆盖上最完整, 受词典命中稀疏性的影响也相对最小。计算规则与家族其余两轨相同 (跨全轨的 <5 行全局最小样本守卫、省份-年份分组、组内有效银行数 >1 才产出、组内和减自身除以 n-1)。按 CLAUDE.md 载明的口径, `_full` 轨是留篇门控的锚定轨: 是否判定某篇报道为"一篇银行金科报道"完全由 `llm_verified_full==True` 决定, 这一判定同时决定了 `dict_avg_tone_full` (进而本列) 与 `_ctx`/`_ss` 两轨的共同行宇宙边界。在多数 P1/P2 主线论文以 `*_full` 作为处理变量主口径的场景下, 本列是与之配套、地理粒度最直接可用的省级同侪工具变量之一, 但仍需与 `bert`/`llm` 两支同粒度 leave-one-out IV 各自 just-identified 并排使用, 不得混入同一 over-identified Hansen J 统计量。

从样本覆盖角度看, `_full` 轨因不做实体窗口或同句共现裁剪, 理论上受词典命中稀疏性影响最小, 触发省份-年份组内仅剩 1 家银行 (即组无法产出) 或触发跨组汇总的全局 <5 行守卫的概率也相对最低, 因而是三轨中数据完整度最好的一支, 适合作为其余两轨 (`_ctx`/`_ss`) 因文本裁剪导致额外缺失时的对照基准。使用者在跨轨比较三支 leave-one-out IV 的第一阶段强度或过度识别检验结果时, 应先核对三轨各自的有效样本量是否一致, 避免把因样本损耗差异导致的统计力差异误读为构念本身的强弱差异。同时应注意, `_full` 轨语调因覆盖全文, 相对更容易吸收与目标银行本身报道主题无关的段落情感 (例如同一篇报道中涉及的宏观经济评论), 这是其与 `_ctx`/`_ss` 两轨在识别策略上互为稳健性、而非互相替代的核心原因。

## VAR: prov_leave1out_dict_tone_ss

【变体差分】
本列是 F481 家族在 `_ss` (标题+银行∧金科同句共现窗口, 默认半径 ±1 句) 文本轨上的 leave-one-out 实现: 其输入 `dict_avg_tone_ss` 只在文章中存在银行与金科词严格同句共现时才使用该同句窗口文本计算语调, 若某篇报道不存在这种同句共现, 则 `content_ss` 按镜像 `_ctx` 的回退语义退化为全文 body (`ss_is_fallback=True`), 与 `_ctx` 轨共享同一套 `n_articles` 分母口径。这意味着本列在窗口收窄到"同句共现"的严格判据下更聚焦银行与金科科技直接关联的语境, 是三轨中判据最严格、噪声理论上最小但样本损耗 (回退比例) 也可能最高的一支。producer 端源码注释特别提示: `dict_avg_tone_ss` 由上游 `compute_composite_indicators` 三轨化产出, 若该轨源列因某些历史或配置原因未落盘, 本列会通过 `if tone_col not in panel.columns: continue` 的显式守卫被优雅跳过而非报错, 即该省该年或该银行对应的 `_ss` 轨 leave-one-out 值可能整体缺失, 使用者在做三轨横向比较前应先核实 `_ss` 轨源列的实际覆盖度。三轨 (含本列) 在识别策略上互为稳健性对照、各自 just-identified 并排, 不构成互相嵌套或叠加关系。

由于 `_ss` 轨的判据 (同句共现) 比 `_ctx` 轨的判据 (实体窗口) 更严格, 满足严格判据的文章子集通常是 `_ctx` 轨文章子集的真子集, 这意味着本列在同一省份-年份组内实际参与计算的有效银行数量可能少于 `_ctx`/`_full` 两轨, 更容易在某组内衰减到仅剩 1 家银行 (从而该组无法产出, 门槛是组内 >1 家而非 >=5 家) 或拖累全轨跨组汇总的行数触发 <5 全局守卫, 尤其是在银行数量本就偏少的省份或本项目当前 T=2 的开发期样本上。使用者在生产级 T=18 全量语料上使用本列前, 应结合诊断日志中"有效值计数"与"单一银行组计数"核实该省份-年份格是否因组内仅 1 家银行而无法产出, 避免把"因样本不足而缺失"误读为"该地区不存在同侪语调信号"。此外, 由于 `_ss` 轨的回退语义与 `_ctx` 轨镜像 (同样退化为全文 body), 当某银行在某年内绝大多数报道都触发回退时, 其上游 `dict_avg_tone_ss` 实质上会趋近于该银行的 `_full` 轨语调, 此时本列与 `_full` 轨同侪均值列的经验相关性可能显著升高, 这是回退机制的自然结果, 不构成本列与 `_full` 轨列之间存在设计上的重复或冗余。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Frankel, R., Jennings, J., & Lee, J. (2022). Disclosure sentiment: Machine learning vs. dictionary methods. Management Science, 68(7), 5514-5532. https://doi.org/10.1287/mnsc.2021.4156
Bian, S., Jia, D., Li, F., & Yan, Z. (2021). A new Chinese financial sentiment dictionary for textual analysis in accounting and finance. SSRN Working Paper [Working Paper]. https://doi.org/10.2139/ssrn.3446388
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
<!-- rendered-citations:end -->
</content>
</invoke>
