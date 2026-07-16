---
family_id: F154
columns:
- city_leave1out_tone_ctx
- city_leave1out_tone_full
- city_leave1out_tone_ss
unit: 语调得分 (无量纲, 约 [-1,1]; 同城异行年度均值, bank-year 粒度)
formula: "city_leave1out_tone_{trk}[i,t] = (Σ_{j∈G(city_i), j≠i} tone_{j,t,trk}) / (N_{G,t,trk} − 1); G = 银行 i 注册城市分组, N = 该 (城市, 年) 内有非缺情感得分的银行数"
producer: news_process/pipeline/panel/geography.py::compute_leave_one_out_sentiment (步骤 7d); 标签见 news_process/pipeline/falsification/controls.py::STATA_LABELS_41
upstream:
- 40_panel_yearly.parquet (bank-year tone 聚合列)
- 21_tone_llms.parquet (三轨情感原料)
citations:
- doi: 10.1016/j.iref.2024.01.067
  type: journal
  authors: Fang, Y., Wang, Q., Wang, Y., & Yuan, Y.
  year: 2024
  title: "Media sentiment, deposit stability and bank systemic risk: Evidence from China"
  venue: International Review of Economics and Finance
  vol: 91
  pages_or_artno: 1150-1172
- doi: 10.1016/j.jfineco.2022.11.006
  type: journal
  authors: García, D., Hu, X., & Rohrer, M.
  year: 2023
  title: "The colour of finance words"
  venue: Journal of Financial Economics
  vol: 147
  issue: 3
  pages_or_artno: 525-549
- doi: 10.1093/rof/rfac052
  type: journal
  authors: Goldstein, I.
  year: 2023
  title: "Information in financial markets and its real effects"
  venue: Review of Finance
  vol: 27
  issue: 1
  pages_or_artno: 1-32
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jeconom.2020.07.053
  type: journal
  authors: Shapiro, A. H., Sudhof, M., & Wilson, D. J.
  year: 2022
  title: "Measuring news sentiment"
  venue: Journal of Econometrics
  vol: 228
  issue: 2
  pages_or_artno: 221-243
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
- doi: 10.1111/j.1540-6261.2007.01232.x
  type: journal
  authors: Tetlock, P. C.
  year: 2007
  title: "Giving content to investor sentiment: The role of media in the stock market"
  venue: Journal of Finance
  vol: 62
  issue: 3
  pages_or_artno: 1139-1168
- doi: 10.1111/j.1468-0262.2005.00615.x
  type: journal
  authors: Romano, J. P., & Wolf, M.
  year: 2005
  title: "Stepwise multiple testing as formalized data snooping"
  venue: Econometrica
  vol: 73
  issue: 4
  pages_or_artno: 1237-1282
- doi: "10.1086/728743"
  type: journal
  authors: "Gabaix, X., & Koijen, R. S. J."
  year: 2024
  title: "Granular Instrumental Variables"
  venue: "Journal of Political Economy"
new_dois:
  - "10.1086/728743"
---

## CORE

【构念与来源】
本家族三列是城市级 (city-level) 留一 (leave-one-out) 地理平均情感, 作为银行情感的工具变量 (IV) 而构建, 落在面板生成步骤 7d 的 geography 模块。对面板中每个 Bank-Year 观测 (i, t), 城市留一情感的取值等于: 把银行 i 注册城市 G(city_i) 内、同一年度 t 的其他所有银行 (排除银行 i 自身) 的情感得分做算术平均。直觉是: 一家银行所在城市里同城同行当年被媒体报道出的情感基调, 可以作为该银行自身情感的一个外生驱动源 —— 城市层面的媒体环境、区域舆论气候与地方性冲击会同时影响同城银行, 但 (在排他性约束成立的前提下) 只通过"同城情感溢出"这一渠道进入银行 i 的结果变量, 而不直接影响 i 的财务结果。这正是媒体情感文献中把地理同群均值当外生变异来源的思路的落地实现。与之并列的还有省级 (province) 留一情感 (31 个省), 城市级则细化到 329 个城市, 变异来源更精细。二者可同时进入过度识别检验 (Hansen J test), 检验排他性约束是否同时成立。

【方法学与计算】
计算采用向量化的 leave-one-out 公式, 复杂度 O(N): 先对每个 (城市, 年) 分组求组内所有银行 (含自身) 的情感总和 group_sum 与组内有非缺情感得分的银行数 group_cnt, 再对每个成员用 (group_sum − tone_i) / (group_cnt − 1) 剔除自身, 得到严格排除 i 的同城均值。分母 N_{G,t} − 1 是"同城异行有效计数减一", 组内只剩一家银行时留一均值无定义 (记为缺失)。情感原料 tone_{j,t} 是银行 j 在年度 t 的 bank-year 情感聚合值, 上游取自三轨情感流水线 (stage 21 LLM 情感等), 数值域约在 [-1, 1]。⚠ 三轨 (full/ctx/ss) 严格逐轨构建: 留一均值在哪条轨上算, 分子分母就都取哪条轨的同城银行情感, 不跨轨借分母。⚠ 铁律: full / ctx / ss 三轨各自 just-identified 并排, 互为稳健性、不分主次, 禁混进同一 over-identified Hansen J; 城市级与省级两个地理层级则是刻意设计的 over-id 组合入口, 二者可同时进 Hansen J, 与三轨不可混同是两码事。留篇门控沿用 full-only 口径 (2026-06-29): 银行 j 是否算一篇有效银行金科报道、进而形成有效 bank-year 情感, 由 full 轨判定; ctx/ss 是 conditional-on-full 的测度/稳健性轨, 其行宇宙是 full 留篇集的子集。

【文献定位】
把媒体情感当作对银行结果有实质影响的信息变量, 直接承接媒体金融文献的主线: Tetlock (2007) 证明媒体悲观基调对股市有可度量的定价效应; Fang & Peress (2009) 揭示媒体覆盖度进入股票横截面收益; Shapiro et al. (2022) 系统化了新闻情感的测度方法。就中国银行业场景而言, Fang et al. (2024) 直接刻画媒体情感如何影响存款稳定性与银行系统性风险, 是本家族外生变异经济机制 (同城舆论气候 → 存款流动 → 银行结果) 的同域证据; Goldstein (2023) 从"金融市场信息及其实体效应"的角度为这一渠道提供理论定位。情感测度本身的效度依托中文金融词典与文本情感度量的方法学积累, 如 Du et al. (2022) 的中文金融情感词典与 García et al. (2023) 对金融词汇色彩的刻画。识别辩护上须如实披露反射问题: Manski (1993) 证明线性均值模型下同期组均值与个体结果不可分离识别 (reflection problem), Bramoullé et al. (2009) 的网络识别条件要求非传递三元组, 而同城分组是完全图不满足该条件 —— 因此本 IV 是稳健性/证伪展示用途而非强因果主 IV, 论文须明写。多测度并排时的族错误率控制走根级 rwolf 模板, 方法学依据见 Romano & Wolf (2005)。⚠ 弱工具警告 (T=2 当前面板实测): 城市级一阶段 F ≈ 0.037, 甚至弱于省级 F ≈ 0.25, 根因是面板深度浅 + 地理稀疏使留一后变异枯竭; 生产 T=19 下同城年度银行数增加, 工具强度才可能改善, 需届时重测。Gabaix & Koijen (2024, Journal of Political Economy) 提出用同群体内其他成员的留一 (leave-out) 加权均值构造工具变量以识别因果参数的通用方法论, 为本家族城市留一情感 IV 的构造逻辑与弱工具/识别强度讨论提供直接方法学依据。

## VAR: city_leave1out_tone_full

【变体差分】
本列是 full 轨的城市留一情感。full = 标题 prepend 到全文正文后的完整文本轨, 是三轨中语料最全、也是留篇门控 (2026-06-29 full-only 口径) 的判定轨: 一家同城银行 j 是否被计为有效银行金科报道、进而贡献一个 bank-year 情感值到城市留一分子, 由 full 轨的 llm_verified_full 判定。因此 full 轨的同城均值分母 N_{G,t,full} − 1 是"当年该城市里 full 轨有有效情感的异行数减一", 是三轨里行宇宙最完整、分母通常最大、缺失最少的一条。与家族另两轨相比, full 轨的语义差分仅在于文本轨来源: 情感原料 tone_{j,t,full} 取自 full 轨情感, 逐轨对齐, 绝不与 ctx/ss 混算。作为 IV, 本列与 city_leave1out_tone_ctx、city_leave1out_tone_ss 互为稳健性、不分主次, 各自 just-identified 并排, 禁三轨混进同一 over-identified Hansen J; 但本列可与同轨的省级留一情感 prov_leave1out_tone_full 一起进 Hansen J 做过度识别检验 (地理层级维度的 over-id, 非轨道维度)。在与已在面板的城市级金科关注度 IV (ft_attn_city, 捕获媒体来源地金融科技文章占比这一"媒体关注度"外生变异) 的区分上, 本列捕获的是"情感溢出"维度的外生变异 —— 同城其他银行当年被媒体报道出的情感基调, 两者从不同角度提供外生变异, 构念不重叠, 可同时作为 IV 进入 overid test。full 轨作为留篇门控轨, 是三轨里最适合当主展示轨的一条, 也是数值缩水风险最小 (语料最全) 的一条。⚠ 弱工具警告同家族 CORE: T=2 面板下城市级 full 轨一阶段工具强度极弱 (F ≈ 0.037), 仅作证伪/稳健性展示, 不得当强因果主 IV, 生产 T=19 下工具强度须届时重测。

## VAR: city_leave1out_tone_ctx

【变体差分】
本列是 ctx 轨的城市留一情感。ctx = 标题 prepend + 银行实体上下文窗口的文本轨 (只保留银行实体邻近窗口的正文, 而非全文), 因此其情感原料 tone_{j,t,ctx} 只反映同城异行在实体上下文窗口内被度量出的情感基调, 相较 full 轨更聚焦、噪声更少但语料更窄。ctx 轨是 conditional-on-full 的测度/稳健性轨: 一家同城银行是否进入留一分子, 仍由 full 轨留篇门控裁定 (full-only 口径), ctx 只在这批留篇集的子集上按 ctx 轨情感逐轨重算同城均值; 若某银行 ctx 轨缺情感值, 则该 (城市, 年) 的 ctx 分母 N_{G,t,ctx} 相应缩小, 分子分母严格逐轨、绝不借 full 轨分母回填。与 full/ss 两轨相比, 本列的唯一差分是文本轨口径 (实体窗口 vs 全文 vs 同句), 构念、留一公式、地理分组、年度对齐完全一致。作为 IV, 本列与 full/ss 两轨互为稳健性、不分主次、各自 just-identified 并排, 禁三轨混进同一 over-identified Hansen J; 可与同轨省级 prov_leave1out_tone_ctx 组过度识别检验。ctx 轨的价值在于: 若城市留一情感 IV 的结论在 full 轨与只保留实体窗口的 ctx 轨上同号同量级, 说明外生变异并非由全文里与银行无关的段落驱动, 而确实来自围绕银行实体的报道基调, 这是对排他性叙事的一层稳健性支撑。⚠ T=2 面板下 ctx 轨同城年度有效银行数更稀疏, 留一后变异可能退化至近零, 工具强度极弱, 仅作稳健性展示, 生产 T=19 下须重测工具强度。

## VAR: city_leave1out_tone_ss

【变体差分】
本列是 ss 轨的城市留一情感。ss = 标题 prepend + 银行与金融科技词同句 (±N 句窗, 默认半径 1) 共现片段的文本轨, 是三轨里语料最窄、最聚焦"银行∧金科同句共现"语境的一条; 其回退语义镜像 ctx: 当某报道无银行与金科同句共现时, ss 文本降级为全文 body、ss_is_fallback=True, 与 ctx 共享 n_articles 分母。因此情感原料 tone_{j,t,ss} 反映同城异行在银行金科同句语境 (含回退) 下被度量出的情感, 与 full/ctx 两轨的差分仅在文本轨口径。ss 轨同样是 conditional-on-full 的稳健性轨: 同城银行是否进入城市留一分子由 full 轨留篇门控裁定 (full-only 口径), ss 只在该留篇子集上按 ss 轨情感逐轨重算同城均值, 分子分母严格逐轨、绝不借 full 分母。作为 IV, 本列与 full/ctx 两轨互为稳健性、不分主次、各自 just-identified 并排, 禁三轨混进同一 over-identified Hansen J; 可与同轨省级 prov_leave1out_tone_ss 组过度识别检验。ss 轨在三轨中语境最严, 只锁定银行与金融科技词同句共现的片段情感, 因此它对应的外生变异最贴近"银行金科关联"这一研究焦点; 但语料最窄也意味着回退比例与缺失最高、留一后变异最易枯竭, 故 ss 轨的城市留一 IV 主要用途是极端聚焦口径下的证伪臂, 用来验证主结论不依赖宽口径文本轨。⚠ T=2 面板下 ss 轨最易出现同城年度内有效银行数为零或方差枯竭, 工具强度极弱 (甚至无法识别), 仅作证伪/稳健性展示, 生产 T=19 下须重测工具强度。

<!-- rendered-citations:begin -->
Fang, Y., Wang, Q., Wang, Y., & Yuan, Y. (2024). Media sentiment, deposit stability and bank systemic risk: Evidence from China. International Review of Economics and Finance, 91, 1150-1172. https://doi.org/10.1016/j.iref.2024.01.067
García, D., Hu, X., & Rohrer, M. (2023). The colour of finance words. Journal of Financial Economics, 147(3), 525-549. https://doi.org/10.1016/j.jfineco.2022.11.006
Goldstein, I. (2023). Information in financial markets and its real effects. Review of Finance, 27(1), 1-32. https://doi.org/10.1093/rof/rfac052
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. Journal of Econometrics, 228(2), 221-243. https://doi.org/10.1016/j.jeconom.2020.07.053
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
Tetlock, P. C. (2007). Giving content to investor sentiment: The role of media in the stock market. Journal of Finance, 62(3), 1139-1168. https://doi.org/10.1111/j.1540-6261.2007.01232.x
Romano, J. P., & Wolf, M. (2005). Stepwise multiple testing as formalized data snooping. Econometrica, 73(4), 1237-1282. https://doi.org/10.1111/j.1468-0262.2005.00615.x
Gabaix, X., & Koijen, R. S. J. (2024). Granular Instrumental Variables. Journal of Political Economy. https://doi.org/10.1086/728743
<!-- rendered-citations:end -->
