---
family_id: F440
columns:
- media_hhi
- sum_media_authority_weight
unit: media_hhi 为 Herfindahl-Hirschman 集中度指数, 取值区间 (0,1], 无量纲; sum_media_authority_weight 为归一化权威性权重之和, 无量纲 (量级近似"篇数", 因权重经均值归一到 1)
formula: 'media_hhi = Σ_j s_j^2 (s_j = 银行-年内媒体来源 j 的报道占比, 由 df.groupby([target_bank, year])[媒体(中文)].value_counts(normalize=True) 得到); sum_media_authority_weight = Σ_i media_authority_weight_i (bank-year 内逐篇 media_authority_weight 之和, media_authority_weight = raw_weight / mean(raw_weight), raw_weight 由 media_weights.json 精确匹配 → 去括号归一化匹配 → default 三级回退取得)'
producer: pipeline\panel\attention_media.py (media_hhi, 维度⑤媒体来源集中度) ; pipeline\panel\encode.py::compute_media_authority_weights (media_authority_weight 篇章级计算) + encode.py::build_aggregation_dict (sum_media_authority_weight bank-year sum 聚合, 亦作 MW-Tone 加权语调族的分母)
upstream: [11_news_bank, 40_panel_export_main]
citations:
- doi: 10.2308/TAR-2020-0104
  type: journal
  authors: Holzman, E. R., Miller, B. P., & Twedt, B. J.
  year: 2023
  title: 'Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements'
  venue: The Accounting Review
  vol: '98'
  issue: '7'
  pages_or_artno: 315-345
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: What Drives Media Slant? Evidence from U.S. Daily Newspapers
  venue: Econometrica
  vol: '78'
  issue: '1'
  pages_or_artno: 35-71
- doi: 10.1016/j.jfineco.2021.08.015
  type: journal
  authors: Heese, J., Pérez-Cavazos, G., & Peter, C. D.
  year: 2022
  title: When the Local Newspaper Leaves Town The Effects of Local Newspaper Closures on Corporate Misconduct
  venue: Journal of Financial Economics
  vol: '145'
  issue: '2'
  pages_or_artno: 445-463
- doi: 10.1111/jofi.12179
  type: journal
  authors: Peress, J.
  year: 2014
  title: The Media and the Diffusion of Information in Financial Markets Evidence from Newspaper Strikes
  venue: The Journal of Finance
  vol: '69'
  issue: '5'
  pages_or_artno: 2007-2043
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: Political Incentives to Suppress Negative Information Evidence from Chinese Listed Firms
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行-年报道样本在"媒体来源"这一维度上的结构特征, 与情感/语调本身正交, 回答的是"报道从哪里来、来源集中还是分散、来源权威性高还是低"而非"报道说了什么"。两列分属两条独立但常被联合解读的测度线索: media_hhi 度量报道来源的集中度 (是否被少数几家媒体主导), sum_media_authority_weight 度量报道来源的权威性总量 (是否偏重高权威财经媒体), 二者常在稳健性讨论里并排引用但不构成同一构念的两个刻面, 不应互相替代。
media_hhi 直接借用产业组织学的赫芬达尔-赫希曼指数 (Herfindahl-Hirschman Index, HHI) 构念, 把"媒体来源"当作一个类比"厂商市场份额"的离散分布: 对银行-年单元内每家媒体来源 j 计算其在该单元全部报道中的占比 s_j, 再取占比平方和 Σs_j²。HHI 越接近 1, 说明该银行-年的报道几乎全部由单一媒体来源贡献 (来源高度集中); HHI 越接近 1/N (N 为不同来源家数), 说明报道在多家媒体间均匀分散。该构念呼应媒体经济学文献里关于"信息供给结构如何影响信息扩散/纠偏能力"的讨论 — 若某银行的媒体曝光被单一来源垄断, 该来源的立场/风格 (地方性、监管背景、商业关系) 会不成比例地主导该银行的"媒体图景", 缺乏多来源交叉验证/纠偏的机制; 这与 Gentzkow & Shapiro (2010) 关于媒体立场系统性差异 ("media slant") 的发现相呼应 — 若报道集中于立场偏向一致的少数来源, 该银行观测到的媒体基调更可能是"来源结构的产物"而非"银行基本面的真实反映", 因此 media_hhi 常被用作情感/语调稳健性检验里的一个协变量或异质性分组变量, 用以排除"集中度驱动语调"这一竞争性解释。
sum_media_authority_weight 的构念来源不同: 它承接 Holzman, Miller & Twedt (2023, *The Accounting Review*) 关于媒体权威性差异化影响力的方法论 — 该文 Appendix A "Outlet Impact Media Sent" 通过滚动回归估计每家媒体报道对股票换手率的边际贡献, 再按估计出的边际贡献排名百分位对媒体分层加权, 体现"同一条负面/正面报道, 出自《人民日报》还是出自地方都市报, 对企业/银行的实际市场冲击并不等权"这一核心洞见。本项目受限于本地无法逐媒体做滚动回归估定影响力 (样本量/计算成本), 因此使用 `config/media_weights.json` 中预先编制的静态权威性评分表 (10–100 分区间) 作为该方法论的简化替代 — 这是一个刻意的方法学退让, 须在文献定位段与已知局限段明确交代, 而非把静态评分表包装成 Holzman 方法的忠实复刻。sum_media_authority_weight 本身是权重的 bank-year 加总 (而非语调的加权平均), 它是下游"媒体权威性加权语调" (MW-Tone, `{短名}_tone_mw{track}` 等列族, 定义为 Σ(weight_j × tone_j) / Σ(weight_j)) 的分母部件, 数值大小近似反映该银行-年"权威性调整后的有效报道量"; 单独看该列时, 其大小既受篇数驱动也受篇均权威性驱动, 二者混杂, 解读须谨慎 (详见方法学与计算段)。

【方法学与计算】
media_hhi 的计算路径: `attention_media.py` 对篇章级 DataFrame 按 `[target_bank, year]` 分组, 在每组内对 `媒体(中文)` 列调用 `value_counts(normalize=True)` 得到各来源占比 s_j, 再平方求和 `(s  2).sum()`, 得到该银行-年的 HHI 标量, 随后左连接回 bank-year 面板。该计算是篇章级来源标签的直接函数, 不依赖情感/语调判定结果, 因此不区分 full/ctx/ss 三轨 (三轨差异只体现在文本窗口/情感抽取上, 与"这篇报道出自哪家媒体"无关) — media_hhi 是track-agnostic 的元数据度量, 不参与三轨并排稳健性框架, 全库唯一一列。分母隐含为该银行-年全部留篇报道 (与情感留篇门控 full-only 口径独立, 因为 media_hhi 计算发生在情感判定之前的篇章级来源标签上, 不受 `llm_verified_full` 门控约束)。极限情形: 若某银行-年仅 1 篇报道 (或全部报道来自单一来源), media_hhi 恒为 1 (无法与"报道量少"和"来源集中"两种诱因区分, 须结合 n_articles 联合解读); 若某银行-年报道均匀分布于 N 家不同来源, media_hhi 趋近 1/N。
sum_media_authority_weight 的计算路径分两步。第一步 (篇章级, `encode.py::compute_media_authority_weights`): 对每篇报道的媒体来源名 `媒体(中文)` 依次尝试 (a) 与 `media_weights.json` 键精确匹配, (b) 去除括号后缀 (如"扬子晚报(数字报)" → "扬子晚报") 归一化匹配, (c) 均未命中则回落到该 json 文件的 `"default"` 键 (与 `68_media_diversity.py` 的默认权重取值口径一致); 三级匹配依次记为 exact/fuzzy/default 三个诊断计数并写入运行日志 (精确命中占比 ≥30% 判读为"权威匹配良好", 否则判读为"权重信号偏弱、多数落默认值"); 取得原始权重 raw_weight 后, 对全篇章级样本做均值归一化 `media_authority_weight = raw_weight / mean(raw_weight)`, 使整体量级 ≈ 等权版本 (归一化后 std 大小反映该银行样本内权威性区分度是否充分)。第二步 (bank-year 聚合, `build_aggregation_dict`): 对篇章级 `media_authority_weight` 按 `[target_bank, year]` 做 `sum` 聚合得到 `sum_media_authority_weight`。该列在下游被直接复用为 MW-Tone 加权语调族 (`llm_vote_tone_mw{track}` / `{short}_tone_mw{track}` / `{dict}_tone_mw{track}` / `{bert}_pos_mw{track}` 等) 的分母 (0 值经 `replace(0, np.nan)` 转为 NaN, 防除零), 因此 sum_media_authority_weight 本身既是一个可独立解读的"权威性报道量"测度, 也是理解 MW-Tone 族分母结构的必读前置列。⚠ LLM 族 MW 分母存在 valid-mask 修正 (`_llm_denom`, 因 LLM 打分存在无效/失败行, 分子分母须同域配对, 否则语调系统性向 0 偏), 该修正不影响 sum_media_authority_weight 本身的取值 (它是全域物理和, 修正只发生在语调族的分母替换里), 阅读者不应把 sum_media_authority_weight 误当作某个 track 的"有效样本量"。

【文献定位】
media_hhi 沿用产业组织学标准的 HHI 构念 (Σ 份额平方和), 在媒体/新闻经济学脉络下, 与 Gentzkow & Shapiro (2010, *Econometrica*, doi: 10.3982/ECTA7195) 关于媒体立场系统性来源差异的发现相呼应 — 该文证明不同媒体在同一事件上的措辞/立场存在稳定的跨报社差异 ("what drives media slant"), 意味着报道来源结构本身携带信息, 不是中性噪声; media_hhi 把这一构念转化为可在 bank-year 面板层面直接使用的集中度标量, 用于排除"语调差异由来源结构驱动"这一竞争性解释, 或作为异质性分组变量 (集中度高 vs 分散的银行子样本分别估计)。sum_media_authority_weight 的方法论锚点是 Holzman, Miller & Twedt (2023, *The Accounting Review*, doi: 10.2308/TAR-2020-0104) 的 Outlet Impact Media Sent 加权框架, 其核心贡献是证明"按媒体对市场的边际影响力加权后的语调测度, 比简单等权语调测度对盈余公告后的价格发现更具解释力"; 本项目的静态评分表替代方案是对该框架计算成本的简化, 同一权重族亦服务于文本情感文献中常见的"先分后合" (先在篇章级构造测度, 再加权聚合到实体-期间层面) 面板构建范式, 该范式在 `encode.py` 模块 docstring 中另有标注 (未纳入本家族 citations 白名单核验范围, 此处仅转述计算范式本身、不作点名年份/期刊的学术依据引用)。两列共同服务于论文里对"媒体覆盖结构 (来源多寡/权威高低) 是否混淆语调-结果关系"的稳健性论证, 但在识别策略上各自独立: media_hhi 是纯计数几何构造, sum_media_authority_weight 依赖外部权重表这一测度选择, 二者不应被合并进同一个过度识别 (over-identified) 设定里联合检验, 而应作为并列的、各自 just-identified 的协变量/稳健性维度使用。

## VAR: media_hhi

【变体差分】
media_hhi 是本家族内唯一的集中度测度, 无同族姊妹变体、无轨道/模型/阈值/权重梯子。它在计算链条上区别于 sum_media_authority_weight 的关键差分点有三: 其一, 计算原语不同 — media_hhi 是对来源标签本身的 `value_counts` 平方和, 是纯粹的计数几何构造, 不引用 `media_weights.json` 里任何权威性评分; 其二, 值域不同 — media_hhi 严格落在 (0,1] 区间且可与"1/来源家数"这一理论下界对照解读, sum_media_authority_weight 无固定上界, 量级随篇数与篇均权重变化; 其三, track 属性不同 — media_hhi 是 track-agnostic 的元数据度量 (不区分 full/ctx/ss, 因为报道的"媒体来源"标签在情感抽取窗口切分之前就已固定), 而全家族乃至同模块内的 MW-Tone 加权语调族都严格区分三轨。使用该列时须与 n_articles (报道量) 联合解读, 因为极小样本 (如仅 1–2 篇) 会机械地推高 media_hhi 而与"来源结构性集中"这一构念本意无关, 属于小样本退化情形而非测度缺陷。样本量随年份/银行差异很大时, 跨单元直接比较 media_hhi 水平须格外谨慎: 报道量本身少的银行-年天然更容易落在 HHI 高值区, 这是离散计数分布的机械性质而非该银行真实"媒体来源被少数几家垄断"。因此更稳妥的用法是把 media_hhi 当作控制变量或分组变量放入回归, 而非直接做跨单元排序比较; 若需要跨单元可比的集中度水平, 应考虑同时报告样本量分层结果, 或在稳健性附录里对小样本单元 (如 n_articles 低于某阈值) 做敏感性排除。该列与 sum_media_authority_weight 在解读上互补但不可替换: media_hhi 回答"来源是否集中", sum_media_authority_weight (及其篇均版本) 回答"来源是否权威", 一个银行-年完全可能同时呈现"来源集中但权威性高" (被单一权威媒体持续报道) 或"来源分散但权威性低" (被大量小报零散报道) 等组合, 论文在引用时应避免把二者混为一谈, 亦不应将二者同时作为过度识别工具变量塞入同一 Hansen J 设定。

## VAR: sum_media_authority_weight

【变体差分】
sum_media_authority_weight 是本家族内权威性权重之和这一测度线索下的唯一落盘列 (对应的均值归一化中间列 `media_authority_weight` 是篇章级列, 不落盘到 bank-year 面板); 它区别于 media_hhi 的核心差分是"依赖外部权重表"这一测度选择本身 — 权威性评分来自 `config/media_weights.json` 静态表 (10–100 分区间, 精确匹配 → 去括号归一化匹配 → default 三级回退取得原始权重, 再做全样本均值归一化), 而非任何情感/语调判定结果, 因此该列同样不区分三轨 (它统计的是"报道来源的权威性", 与情感抽取窗口无关); 但与 media_hhi 不同的是, sum_media_authority_weight 在下游被结构性复用为 MW-Tone 加权语调族的分母部件 (`llm_vote_tone_mw{track}` 等), 而 media_hhi 无此下游复用关系, 是纯粹的独立协变量。解读 sum_media_authority_weight 时须注意其量级混杂性: 数值越大既可能因为该银行-年报道篇数本身多, 也可能因为篇均权威性评分高 (来源偏权威财经媒体), 单独看该列无法区分这两种驱动力, 若需分解应联合 n_articles 与 sum_media_authority_weight/n_articles (篇均权威性) 一并考察; 与后续 `media_authority_weight_tier` (3 级离散声誉分类权重, 并行存在于 `encode.py`、作 paper Table A8 敏感性检验、不覆盖本列所用的连续型主口径权重) 互为稳健性、不分主次, 二者不应混入同一过度识别设定联合估计。
<!-- rendered-citations:begin -->
Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements. The Accounting Review, 98(7), 315-345. https://doi.org/10.2308/TAR-2020-0104
Gentzkow, M., & Shapiro, J. M. (2010). What Drives Media Slant? Evidence from U.S. Daily Newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Heese, J., Pérez-Cavazos, G., & Peter, C. D. (2022). When the Local Newspaper Leaves Town The Effects of Local Newspaper Closures on Corporate Misconduct. Journal of Financial Economics, 145(2), 445-463. https://doi.org/10.1016/j.jfineco.2021.08.015
Peress, J. (2014). The Media and the Diffusion of Information in Financial Markets Evidence from Newspaper Strikes. The Journal of Finance, 69(5), 2007-2043. https://doi.org/10.1111/jofi.12179
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political Incentives to Suppress Negative Information Evidence from Chinese Listed Firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
<!-- rendered-citations:end -->
