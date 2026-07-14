---
family_id: F106
columns:
- bartik_media_share_comp
- bartik_media_share_fin
unit: 基期份额 (proportion, 无量纲, 取值 [0,1]; 同一银行两类媒体份额相加为 1)
formula: "bartik_media_share_{type} = (基期银行 i 来自 type 类媒体的报道计数) / (基期银行 i 来自 fin 与 comp 两类媒体的报道计数之和); type ∈ {fin=财经专业媒体, comp=综合媒体}; 分母不含被剔除的 other 兜底类 (故两份额在 fin+comp 子空间内重归一化、相加为 1); 该基期份额与各媒体类型的全国 leave-one-out 增长率相乘并求和 → bartik_media_iv_{full,ctx}"
producer: pipeline\panel\runner.py (compute_bartik_iv_fintech 媒体维度份额与 IV 构造, category_col=_media_type; variable-label 在 pipeline\panel\export.py 落地)
upstream:
- 40_panel_yearly.parquet (基期银行×媒体类型报道计数)
citations:
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  issue:
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: "When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct"
  venue: Journal of Financial Economics
  vol: 145
  issue: 2
  pages_or_artno: 445-463
- doi: 10.1016/j.jfineco.2019.06.003
  type: journal
  authors: Gao, P., Lee, C., & Murphy, D.
  year: 2020
  title: "Financing dies in darkness? The impact of newspaper closures on public finance"
  venue: Journal of Financial Economics
  vol: 135
  issue: 2
  pages_or_artno: 445-467
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: "The media and the diffusion of information in financial markets: Evidence from newspaper strikes"
  venue: The Journal of Finance
  vol: 69
  issue: 5
  pages_or_artno: 2007-2043
- doi: "10.1111/jofi.13287"
  type: journal
  authors: "Fedyk, A."
  year: 2024
  title: "Front-Page News: The Effect of News Positioning on Financial Markets"
  venue: "Journal of Finance"
- doi: "10.1111/1911-3846.13046"
  type: journal
  authors: "Ma, Z., Stice, D., Stice, H., & Zhang, Y."
  year: 2025
  title: "Local newspaper closures and bank loan contracts"
  venue: "Contemporary Accounting Research"
- doi: "10.1287/mnsc.2023.02247"
  title: "Media Conglomeration, Local News, and Capital Market Consequences"
  authors: "Dyer, T., Lang, M., & Oh, J."
  year: 2025
  venue: "Management Science"
  type: "journal"
new_dois:
  - "10.1111/jofi.13287"
  - "10.1111/1911-3846.13046"
  - "10.1287/mnsc.2023.02247"
---

## CORE

【构念与来源】
本家族两列是 Bartik / shift-share 工具变量在「媒体类型」维度上的基期份额构件 (share component), 即构成移位-份额 (shift-share) 工具的「份额」原语, 而非工具变量本身。研究把每家银行在基期年份 (base period t0) 收到的媒体报道, 按报道来源的媒体类型分类为财经专业媒体 (financial media, 对应 bartik_media_share_fin)、综合媒体 (comprehensive / general media, 对应 bartik_media_share_comp) 与无法归入前二者的兜底类 other 三桶; 其中 other 桶在份额构造时被整体剔除 (media_map 保留 fin/comp 两个 kept groups, other 不进分子亦不进分母), 因此本家族两列只在 fin+comp 这一子空间内定义。某银行的份额定义为该桶报道计数占其基期 fin 与 comp 两类报道计数之和的比例——分母不是「基期全部媒体报道计数」而是「基期财经+综合两类报道计数之和」, 这一点是本家族口径的承重要点: fin 与 comp 两桶相对全部媒体并不穷尽 (被剔的 other 类不参与), 但在 fin+comp 子空间内二者互斥且穷尽, 经该子空间重归一化后同一银行两列相加恒为 1, 取值域 [0,1], 无量纲。剔 other 是刻意的口径统一决策: 与 type/scale 等相邻维度支「分母仅含 kept groups (排除 other/未映射 NaN)」的归一化一致, 否则 other 计入分母却不进分子会令基期份额和 < 1、跨维度工具的系数尺度不可比。份额只在基期计算一次、对该银行在样本期内时间不变 (time-invariant), 这正是 shift-share 设计对「份额」外生性的关键要求: 份额固定在处理前的基期结构, 使后续内生的暴露变动只通过外生的「移位」项 (各媒体类型报道量的全国增长率) 传导。这两列的用途是与各媒体类型的全国 leave-one-out 增长率相乘再求和, 生成媒体维度的 Bartik 工具 bartik_media_iv_full / bartik_media_iv_ctx (属另一相邻家族), 用作银行媒体暴露 (news exposure) 的外生变动来源, 服务于以银行媒体关注/情感为处理变量的因果识别。数据来源为 pipeline 上游对每家银行×媒体类型的基期报道计数聚合, 落地于 40_panel_yearly 面板; 变量标签在 pipeline\panel\export.py 的标签映射中登记 (Bartik Share: Financial Media / Bartik Share: Comprehensive Media), 份额与 IV 的实际构造在 pipeline\panel\runner.py 的 Bartik 引擎内完成。媒体维度 (media-type) 是 Bartik 家族「稳健性 3」这一支: 与之并列的还有银行类型维度 (type: SOE/joint/city/rural/private/foreign)、规模维度 (scale: L/M/S/XS)、金融科技类别维度 (fintech locus)、媒体权威性维度 (mauth) 与地理邻近维度 (geoprox), 各维度是同一识别策略在不同基期分组棱镜下的平行稳健性支, 互为稳健性、不分主次。

【方法学与计算】
计算分两步。第一步 (本家族两列): 对每家银行 i, 取其基期报道集合, 先将来源媒体映射为 fin / comp / other 三类, 剔除 other 后分别累计财经与综合两类的报道计数 n_fin(i) 与 n_comp(i), 令 share_fin(i)=n_fin(i)/(n_fin(i)+n_comp(i)), share_comp(i)=1−share_fin(i); 分母显式排除 other, 与 type/scale 维度 total=sum-over-non-other 的口径一致, 而非以银行基期全部媒体计数为分母。份额与 IV 的构造在 pipeline\panel\runner.py 内由 compute_bartik_iv_fintech (category_col=_media_type, media_map={fin,comp,other}) 完成, 而非属性维度所用的 compute_bartik_iv。第二步 (下游 IV, 非本家族列): 对每个媒体类型 k 计算其全国报道量的增长「移位」项 g_{k,t}, 通常采用 leave-one-out 口径 (剔除银行 i 自身以缓解份额与移位同时内生的反射性), 再令 bartik_media_iv(i,t)=Σ_k share_k(i)·g_{k,t}。之所以把份额冻结在基期, 是因为 shift-share 工具的可识别性依赖「份额外生」或「移位外生」二者之一: 本设计走份额固定路线, 让外生变动全部来自各媒体类型层面的共同冲击, 而单家银行既无法左右财经媒体或综合媒体的全国总量走势, 其基期结构相对当期处理又是前定的。留篇门控与三轨口径需在此厘清: pipeline 的留篇判定采 full-only 口径 (2026-06-29), 即一篇报道是否计入银行金科报道集合只看 full 轨的 LLM 验证结果; 媒体维度 Bartik 的 full/ctx 双轨差异出现在下游 IV 列 (bartik_media_iv_full/ctx), 而本家族的两列基期份额是这两条 IV 轨共享的同一份基期结构原语, 本身不带轨道后缀。铁律层面: Bartik 各维度支、full/ctx 双轨、co-primary 双轨嵌入下游若进入 2SLS, 须各自 just-identified 并排、互为稳健性不分主次, 严禁把不同维度或不同轨道的工具混进同一 over-identified Hansen J 过度识别检验 (跨轨/跨维度混装会污染过度识别统计量的解释)。

【文献定位】
移位-份额工具的现代计量基础由 Adão, Kolesár, and Morales (2019) 与 Borusyak, Hull, and Jaravel (2025) 奠定: 前者在 Quarterly Journal of Economics 上系统刻画了 shift-share 设计的推断问题与份额相关导致的标准误偏误, 后者在 Journal of Economic Perspectives 给出「份额×移位」的实操检查表, 明确处理不完全份额 (incomplete shares) 与重归一化选择的正确做法——本家族两列相加为 1 的归一化正对应其对完备份额的建议。用媒体作为信息传导外生冲击源的思路植根于金融媒体经济学: Peress (2014) 利用报纸罢工这一外生的媒体供给中断, 在 The Journal of Finance 上识别出媒体对金融市场信息扩散的因果作用; Heese, Pérez-Cavazos, and Peter (2022) 与 Gao, Lee, and Murphy (2020) 则以地方报纸关闭为外生冲击, 分别识别其对公司不当行为与地方公共财政的实质影响, 三者共同确立了「媒体覆盖的外生变动可作识别杠杆」的经验范式。就中国银行业同域证据而言, Fang, Wang, Wang, and Yuan (2024) 记录了银行级媒体情感对存款稳定与系统性风险的作用, 支持把银行媒体暴露作为有实质经济后果的处理变量。本家族按媒体类型 (财经 vs 综合) 切分基期结构, 正是把上述「媒体外生冲击」思路细化到不同媒体子市场的暴露组合, 使 Bartik 工具能利用财经与综合两类媒体报道量的差异化增长节奏来撬动银行暴露的外生变动。近期文献进一步充实了这一识别逻辑: Fedyk (2024, Journal of Finance) 利用彭博终端头条位置的外生变动识别新闻显著度对信息扩散速度的因果作用, 为本家族按媒体类型切分基期报道暴露、进而构造媒体维度 Bartik 工具提供了媒体显著度可作外生识别杠杆的最新证据; Ma, Stice, Stice, and Zhang (2025, Contemporary Accounting Research) 以地方报纸关闭作为外生媒体监督供给冲击, 识别其对银行贷款合同利差与契约严格度的因果影响, 呼应本家族以媒体报道类型基期份额构造银行外生媒体暴露工具的识别逻辑。Dyer, Lang, and Oh (2025, Management Science) 考察媒体整合导致的地方财经报道供给结构性变化及其资本市场后果, 支持把媒体类型报道量的差异化演变作为撬动银行媒体暴露的外生识别杠杆。

## VAR: bartik_media_share_comp

【变体差分】
本列是媒体类型维度基期份额的「综合媒体」桶: 度量某银行基期报道中来自综合 / 一般性媒体 (comprehensive / general-interest outlets, 非财经专业化的报纸与通讯渠道) 的报道计数占该银行基期全部报道计数的比例。它与家族另一列 bartik_media_share_fin 构成对同一基期报道集合的二分互补切分, 二者相加恒等于 1, 因此在同一 Bartik 求和式内两列不是独立自由度而是一组结构约束下的对偶份额: 综合媒体份额高等价于财经媒体份额低。语义上, 高 bartik_media_share_comp 的银行其基期媒体暴露更偏向大众化、议题更宽泛的报道流, 其下游 Bartik 预测暴露会更多地由综合媒体报道量的全国增长节奏驱动。该列为基期一次性计算、对银行时间不变, 不带 full/ctx 轨道后缀 (轨道差异体现在下游 bartik_media_iv_full/ctx), 也不带滞后或阈值后缀。与其它 Bartik 维度支 (类型/规模/金科/权威/地理) 的份额列相比, 本列的分组棱镜是「媒体是否财经专业」而非银行属性或地理属性, 因此它捕捉的是暴露的媒体子市场构成而非机构构成。铁律: 本列所属的媒体维度 IV 与其它维度 IV、与 full/ctx 双轨须各自 just-identified 并排、互为稳健性不分主次, 禁混进同一 over-identified Hansen J。

## VAR: bartik_media_share_fin

【变体差分】
本列是媒体类型维度基期份额的「财经专业媒体」桶: 度量某银行基期报道中来自财经 / 金融专业化媒体 (financial / business-specialized outlets) 的报道计数占该银行基期全部报道计数的比例, 是 bartik_media_share_comp 的互补对偶, 二者相加恒为 1。语义上, 高 bartik_media_share_fin 的银行基期媒体暴露更集中于专业财经报道流——这类报道通常信息密度更高、读者更接近投资者与市场参与者, 因此该份额高的银行其下游 Bartik 预测暴露会更敏感于财经媒体报道量的全国增长, 而财经媒体与综合媒体两类报道量的增长节奏在样本期内并不同步, 正是这一差异化「移位」给了 shift-share 工具在媒体维度上的识别力来源。该列同为基期一次性计算、银行时间不变, 无 full/ctx 轨道后缀 (双轨差异在下游 IV 列)、无滞后与阈值后缀。相对家族内其它维度支, 本列的切分依据是报道来源的媒体专业化程度; 它与 bartik_media_share_comp 联合定义了媒体子市场暴露组合, 喂入 pipeline\panel\runner.py 的 Bartik 引擎与全国 leave-one-out 增长率相乘求和, 生成 bartik_media_iv_full/ctx。铁律同前: 媒体维度工具与相邻维度工具、full/ctx 双轨各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified Hansen J 过度识别检验。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the local newspaper leaves town: The effects of local newspaper closures on corporate misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Gao, P., Lee, C., & Murphy, D. (2020). Financing dies in darkness? The impact of newspaper closures on public finance. Journal of Financial Economics, 135(2), 445-467. https://doi.org/10.1016/j.jfineco.2019.06.003
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Peress, J. (2014). The media and the diffusion of information in financial markets: Evidence from newspaper strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Fedyk, A. (2024). Front-Page News: The Effect of News Positioning on Financial Markets. Journal of Finance. https://doi.org/10.1111/jofi.13287
Ma, Z., Stice, D., Stice, H., & Zhang, Y. (2025). Local newspaper closures and bank loan contracts. Contemporary Accounting Research. https://doi.org/10.1111/1911-3846.13046
Dyer, T., Lang, M., & Oh, J. (2025). Media Conglomeration, Local News, and Capital Market Consequences. Management Science. https://doi.org/10.1287/mnsc.2023.02247
<!-- rendered-citations:end -->
