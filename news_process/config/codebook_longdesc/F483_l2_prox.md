---
family_id: F483
columns:
- prox_100km_frac
- prox_100km_neg_frac
- prox_100km_neg_frac_ctx
- prox_100km_neg_frac_ss
- prox_100km_pos_frac
- prox_100km_pos_frac_ctx
- prox_100km_pos_frac_ss
- prox_150km_frac
- prox_150km_neg_frac
- prox_150km_neg_frac_ctx
- prox_150km_neg_frac_ss
- prox_150km_pos_frac
- prox_150km_pos_frac_ctx
- prox_150km_pos_frac_ss
- prox_200km_frac
- prox_200km_neg_frac
- prox_200km_neg_frac_ctx
- prox_200km_neg_frac_ss
- prox_200km_pos_frac
- prox_200km_pos_frac_ctx
- prox_200km_pos_frac_ss
- prox_50km_frac
- prox_50km_neg_frac
- prox_50km_neg_frac_ctx
- prox_50km_neg_frac_ss
- prox_50km_pos_frac
- prox_50km_pos_frac_ctx
- prox_50km_pos_frac_ss
unit: 比率/占比 (proportion, [0,1]; 分母口径逐列见 formula)
formula: 'frac: n_within(d)/n_geocoded, n_within(d)=haversine(bank_hq, media_city_or_prov)<=d 的文章数, n_geocoded=该 bank-year 内媒体侧可地理编码(城市或省会回退)的文章数(≠全部文章数 n_total); pos_frac{sfx}/neg_frac{sfx}: within(d) 子集内 is_positive{track}/is_negative{track} 的均值(逐轨二值指标比例), sfx∈{"" ,_ctx,_ss} 对应 track∈{_full,_ctx,_ss}; n_geocoded=0 时该 bank-year 全部 prox_* 诊断列记 NaN(而非 0), 与"圈内有无媒体未知"语义对齐'
producer: pipeline\panel\geography.py::compute_geo_proximity_buffers ; pipeline\panel\export.py
upstream:
- 24_herd_decay
citations:
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: '67'
  issue: '2'
  pages_or_artno: 561-598
- doi: 10.1016/j.jfineco.2022.07.009
  type: journal
  authors: Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R.
  year: 2022
  title: Bank transparency and deposit flows
  venue: Journal of Financial Economics
  vol: '146'
  issue: '2'
  pages_or_artno: 475-501
- doi: 10.1016/j.eap.2024.08.019
  type: journal
  authors: Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C.
  year: 2024
  title: Does improved credit access promote pollution reduction? The role of bank proximity
  venue: Economic Analysis and Policy
  vol: '84'
  pages_or_artno: 78-97
- doi: 10.1080/0034340052000320887
  type: journal
  authors: Boschma, R.
  year: 2005
  title: "Proximity and innovation: A critical assessment"
  venue: Regional Studies
  vol: '39'
  issue: '1'
  pages_or_artno: 61-74
- doi: 10.1111/1475-679X.12071
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2015
  title: "Political incentives to suppress negative information: Evidence from Chinese listed firms"
  venue: Journal of Accounting Research
  vol: '53'
  issue: '2'
  pages_or_artno: 405-459
- doi: "10.1186/s40854-025-00764-1"
  title: "Geographical distance and stock price synchronization: evidence from China"
  authors: "Xiong, X., Ruan, C., & Meng, Y."
  year: 2025
  venue: "Financial Innovation"
  type: "journal"
new_dois:
  - "10.1186/s40854-025-00764-1"
---

## CORE

【构念与来源】
F483 是「银行总部—报道媒体」地理接近度族, 刻画在 50/100/150/200 公里四个同心圈半径内, 报道目标银行的媒体来源与银行注册地/总部城市之间的空间邻近程度, 以及该邻近范围内报道情感的正负面构成。构念直接承接 Gurun & Butler (2012, The Journal of Finance) 关于本地媒体报道 (local media coverage) 影响企业价值与信息环境的经典发现: 地理上更接近企业总部的媒体, 因记者驻地采编便利、本地读者关注度更高等机制, 往往产生更高频、更贴近一手信息的报道, 二者构成一种非随机的"本地媒体暴露"结构。本族把这一构念应用到中国银行业媒体报道场景, 用于检验银行是否因总部所在地理位置获得系统性差异化的媒体关注强度与情感基调, 呼应 Boschma (2005) 对"地理邻近性"作为多维邻近性之一维、独立于社会/组织/认知邻近性的理论界定, 以及 Chen, Goldstein, Huang & Vashishtha (2022, Journal of Financial Economics) 关于银行透明度与信息流动的讨论。产出函数为 `pipeline/panel/geography.py::compute_geo_proximity_buffers`, 在 stage 40 面板导出阶段 (`pipeline/panel/export.py`) 并入年度 bank-year 面板。
【方法学与计算】
计算分两层。第一层是几何覆盖层, 只用 `prox_{d}km_frac` (d∈{50,100,150,200}) 表达, 与情感/文本无关: 先用 haversine 公式计算银行总部城市坐标与每篇报道所属媒体来源城市 (或省份省会回退, Level-3 插补) 坐标之间的球面距离, 再统计落在半径 d 公里内的文章数 `n_within(d)`, 除以该 bank-year 内媒体侧可地理编码的文章总数 `n_geocoded` (即坐标查得成功的文章数, 不是全部文章数 n_total — 这是 2026-06-10 metric-audit 修复的分母口径: 若把未能定位的文章计入分母, 会人为稀释地理覆盖度, 造成 valid-vs-physical 域不匹配)。四个半径满足拓扑单调关系 prox_50km_frac ≤ prox_100km_frac ≤ prox_150km_frac ≤ prox_200km_frac (同心圈嵌套, 该单调性在 producer 内有断言校验)。第二层是圈内情感构成层, 由 `prox_{d}km_pos_frac{sfx}` / `prox_{d}km_neg_frac{sfx}` 表达: 在落入半径 d 公里圈内的文章子集上, 取该轨 (full/ctx/ss) 文章级二值指标 `is_positive{track}` / `is_negative{track}` (来自 stage 21 三家 LLM 多数投票, encode.py 产出) 的均值, 即圈内正面/负面文章占比。命名上刻意保留历史惯用法: 无后缀 (即 `pos_frac`/`neg_frac` 不带 `_ctx`/`_ss`) 隐式对应 full 轨, `_ctx`/`_ss` 后缀分别显式对应 ctx 轨与 ss 轨, 这是项目"隐式 full + 显式 ctx/ss"命名对角线的一贯约定, 目的是零重命名地兼容既有下游 Stata 模板与 golden 快照。文章级 `is_positive{track}`/`is_negative{track}` 是 nullable 整数类型 (NA=测量失败或三家平局), 聚合前先转 float64 归一, 避免 pandas 把混入 pd.NA 的列错误推断为 object dtype。若某 bank-year 该 bank-year 媒体侧全部不可地理编码 (`n_geocoded=0`), 家族内全部诊断列 (frac/is_local/n_media/n_articles 及 pos_frac/neg_frac 各轨) 记为 NaN 而非 0 — 这是"圈内有无媒体尚属未知"与"确知圈内为空"两种不同缺失语义之间的区分 (omni-g-geography-02 修复), 若圈内确有 0 篇但媒体本身可定位, 则 frac 正常记 0。若圈内 `n_within(d)=0` (可定位但均在圈外) 而对应 `is_positive{track}`/`is_negative{track}` 源列缺失, pos_frac/neg_frac 同样优雅降级为 NaN, 不外推填补。
【文献定位】
本族与 Gurun & Butler (2012) 的本地媒体倾向性设计同构, 也呼应 Chao et al. 系一类空间/生态多层级分解思路在地理维度上的类比应用; 与 Piotroski, Wong & Zhang (2015, Journal of Accounting Research) 关于负面信息压制的政治经济学发现相关联 — 若本地媒体存在系统性负面信息抑制, `neg_frac` 会在近圈 (50km) 与远圈 (200km) 之间呈现非单调差异, 可作为地方保护主义假说的间接证据。三轨 (full/ctx/ss) 意在把"整篇文章基调"(full)、"银行实体窗口基调"(ctx)、"银行-金科同句共现基调"(ss) 三种情感提取口径并排放入同一地理接近度结构中, 检验地理邻近对基调的影响是否稳健于文本口径的选择, 而不是某一口径独有的产物。
凡涉及本族 full/ctx/ss 三轨的比较, 三轨各自 just-identified 并排、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验; ss 轨的回退语义镜像 ctx 轨 (银行∧金科同句未共现时 content_ss 退化为全文 body, `ss_is_fallback=True`, 与全文共享 n_articles 分母), 但本族 pos_frac/neg_frac 并不直接消费 content_ss 文本, 而是消费三轨情感分类结果 is_positive{track}/is_negative{track}; 若上游 stage 21 采用 full-only 留篇门控 (2026-06-29 起生产口径), 则本族 ctx/ss 轨的 `n_within(d)` 分母集合是 full 留篇集的子集, 属 conditional-on-full 测度, 与 full 轨的样本宇宙对齐而非独立扩样。四个距离阈值 (50/100/150/200km) 亦互为稳健性梯度, 不预设"更近即更强"的单调因果结论, 仅作接近度定义的敏感性展示。Xiong, Ruan & Meng (2025, Financial Innovation) 基于中国沪深上市公司数据发现机构投资者与企业间地理距离越大, 股价同步性越高(源于信息不对称加剧), 为中国情境下地理邻近性影响信息环境提供了实证支持, 与F483的空间接近度分档设计相呼应。

## VAR: prox_100km_frac

【变体差分】
本列是 100 公里同心圈的几何覆盖比例, 属四阈值梯度中的第二档, 与情感、三轨口径均无关(track-agnostic, 不消费 is_positive/is_negative 等任何文章级情感分类列, 纯粹是地理坐标层面的覆盖统计, 不区分 full/ctx/ss)。分子 `n_within(100)` 为银行总部城市坐标与媒体来源城市 (或省份省会 Level-3 回退坐标) 之间 haversine 球面距离 ≤100 公里的文章数, 分母 `n_geocoded` 为该 bank-year 内媒体侧可成功地理编码的文章总数——不是全部文章数 n_total, 这一分母口径修复自 2026-06-10 metric-audit (fix(prox-frac-denominator)): 若把无法定位坐标的文章计入分母, 会人为稀释地理覆盖度, 造成可验证覆盖率与物理覆盖率两种不同分母域的混淆(P3 级测度勘误)。四档满足单调拓扑关系 prox_50km_frac ≤ prox_100km_frac ≤ prox_150km_frac ≤ prox_200km_frac, producer 内对该单调性设有断言校验, 任何一档违反单调关系都会在面板构建阶段直接暴露, 不会静默通过。当该 bank-year 媒体侧全部不可地理编码时 (`n_geocoded=0`), 本列记 NaN 而非 0, 与圈内有无媒体尚属未知的语义对齐, 不与确知圈内为空的场景混淆——这是 omni-g-geography-02 修复所解决的诊断列间自相矛盾问题 (此前 is_local 记 0 而 frac 记 NaN, 两列互相矛盾, 现已统一为同一 NaN 语义)。该列同时是同阈值下 `prox_100km_pos_frac`/`neg_frac` 系列 (含 full/ctx/ss 三轨孪生共 6 列) 共享的圈内文章样本量基准: 二者共用同一 `n_within(100)`/`n_geocoded` 定义, 但服务不同构念——本列刻画地理覆盖广度, 情感占比列刻画圈内报道基调构成, 不应把二者混同为同一测度的不同表达。与相邻阈值档 (prox_50km_frac 与 prox_150km_frac) 互为接近度定义的稳健性梯度, 不预设单一最优半径, 仅提供距离敏感性展示窗口, 使用时不应孤立看待单一半径档的数值。

## VAR: prox_100km_neg_frac

【变体差分】
本列是 100 公里圈 full 轨 (全文正文+标题) 的负面文章占比: 分子取 `is_negative_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_negative_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_neg_frac_ctx`(ctx 轨) 及 `prox_100km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_pos_frac` (正面占比) 互补 (prox_100km_neg_frac+prox_100km_pos_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_100km_neg_frac_ctx

【变体差分】
本列是 100 公里圈 ctx 轨 (标题+银行实体窗口) 的负面文章占比: 分子取 `is_negative_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_negative_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_neg_frac`(full 轨) 及 `prox_100km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_pos_frac_ctx` (正面占比) 互补 (prox_100km_neg_frac_ctx+prox_100km_pos_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_100km_neg_frac_ss

【变体差分】
本列是 100 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的负面文章占比: 分子取 `is_negative_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_negative_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_neg_frac`(full 轨) 及 `prox_100km_neg_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_pos_frac_ss` (正面占比) 互补 (prox_100km_neg_frac_ss+prox_100km_pos_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_100km_pos_frac

【变体差分】
本列是 100 公里圈 full 轨 (全文正文+标题) 的正面文章占比: 分子取 `is_positive_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_positive_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_pos_frac_ctx`(ctx 轨) 及 `prox_100km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_neg_frac` (负面占比) 互补 (prox_100km_pos_frac+prox_100km_neg_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_100km_pos_frac_ctx

【变体差分】
本列是 100 公里圈 ctx 轨 (标题+银行实体窗口) 的正面文章占比: 分子取 `is_positive_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_positive_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_pos_frac`(full 轨) 及 `prox_100km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_neg_frac_ctx` (负面占比) 互补 (prox_100km_pos_frac_ctx+prox_100km_neg_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_100km_pos_frac_ss

【变体差分】
本列是 100 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的正面文章占比: 分子取 `is_positive_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤100km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_100km_frac` 的圈内可定位文章集合 `n_within(100)`, 若该值为 0 或 `is_positive_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_100km_pos_frac`(full 轨) 及 `prox_100km_pos_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 100 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_100km_neg_frac_ss` (负面占比) 互补 (prox_100km_pos_frac_ss+prox_100km_neg_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径居中偏窄, 相较 50km 档样本量已明显改善, 但仍显著窄于 150km/200km 档。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_frac

【变体差分】
本列是 150 公里同心圈的几何覆盖比例, 属四阈值梯度中的第三档, 与情感、三轨口径均无关(track-agnostic, 不消费 is_positive/is_negative 等任何文章级情感分类列, 纯粹是地理坐标层面的覆盖统计, 不区分 full/ctx/ss)。分子 `n_within(150)` 为银行总部城市坐标与媒体来源城市 (或省份省会 Level-3 回退坐标) 之间 haversine 球面距离 ≤150 公里的文章数, 分母 `n_geocoded` 为该 bank-year 内媒体侧可成功地理编码的文章总数——不是全部文章数 n_total, 这一分母口径修复自 2026-06-10 metric-audit (fix(prox-frac-denominator)): 若把无法定位坐标的文章计入分母, 会人为稀释地理覆盖度, 造成可验证覆盖率与物理覆盖率两种不同分母域的混淆(P3 级测度勘误)。四档满足单调拓扑关系 prox_50km_frac ≤ prox_100km_frac ≤ prox_150km_frac ≤ prox_200km_frac, producer 内对该单调性设有断言校验, 任何一档违反单调关系都会在面板构建阶段直接暴露, 不会静默通过。当该 bank-year 媒体侧全部不可地理编码时 (`n_geocoded=0`), 本列记 NaN 而非 0, 与圈内有无媒体尚属未知的语义对齐, 不与确知圈内为空的场景混淆——这是 omni-g-geography-02 修复所解决的诊断列间自相矛盾问题 (此前 is_local 记 0 而 frac 记 NaN, 两列互相矛盾, 现已统一为同一 NaN 语义)。该列同时是同阈值下 `prox_150km_pos_frac`/`neg_frac` 系列 (含 full/ctx/ss 三轨孪生共 6 列) 共享的圈内文章样本量基准: 二者共用同一 `n_within(150)`/`n_geocoded` 定义, 但服务不同构念——本列刻画地理覆盖广度, 情感占比列刻画圈内报道基调构成, 不应把二者混同为同一测度的不同表达。与相邻阈值档 (prox_100km_frac 与 prox_200km_frac) 互为接近度定义的稳健性梯度, 不预设单一最优半径, 仅提供距离敏感性展示窗口, 使用时不应孤立看待单一半径档的数值。

## VAR: prox_150km_neg_frac

【变体差分】
本列是 150 公里圈 full 轨 (全文正文+标题) 的负面文章占比: 分子取 `is_negative_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_negative_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_neg_frac_ctx`(ctx 轨) 及 `prox_150km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_pos_frac` (正面占比) 互补 (prox_150km_neg_frac+prox_150km_pos_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_neg_frac_ctx

【变体差分】
本列是 150 公里圈 ctx 轨 (标题+银行实体窗口) 的负面文章占比: 分子取 `is_negative_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_negative_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_neg_frac`(full 轨) 及 `prox_150km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_pos_frac_ctx` (正面占比) 互补 (prox_150km_neg_frac_ctx+prox_150km_pos_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_neg_frac_ss

【变体差分】
本列是 150 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的负面文章占比: 分子取 `is_negative_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_negative_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_neg_frac`(full 轨) 及 `prox_150km_neg_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_pos_frac_ss` (正面占比) 互补 (prox_150km_neg_frac_ss+prox_150km_pos_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_pos_frac

【变体差分】
本列是 150 公里圈 full 轨 (全文正文+标题) 的正面文章占比: 分子取 `is_positive_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_positive_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_pos_frac_ctx`(ctx 轨) 及 `prox_150km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_neg_frac` (负面占比) 互补 (prox_150km_pos_frac+prox_150km_neg_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_pos_frac_ctx

【变体差分】
本列是 150 公里圈 ctx 轨 (标题+银行实体窗口) 的正面文章占比: 分子取 `is_positive_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_positive_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_pos_frac`(full 轨) 及 `prox_150km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_neg_frac_ctx` (负面占比) 互补 (prox_150km_pos_frac_ctx+prox_150km_neg_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_150km_pos_frac_ss

【变体差分】
本列是 150 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的正面文章占比: 分子取 `is_positive_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤150km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_150km_frac` 的圈内可定位文章集合 `n_within(150)`, 若该值为 0 或 `is_positive_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_150km_pos_frac`(full 轨) 及 `prox_150km_pos_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 150 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_150km_neg_frac_ss` (负面占比) 互补 (prox_150km_pos_frac_ss+prox_150km_neg_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径已跨出同一都市圈, 覆盖相邻地级市乃至半个省域, 样本量通常介于窄档与宽档之间, 是本族区分本地与区域媒体暴露的过渡半径。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_frac

【变体差分】
本列是 200 公里同心圈的几何覆盖比例, 属四阈值梯度中的最宽档(梯度上界), 与情感、三轨口径均无关(track-agnostic, 不消费 is_positive/is_negative 等任何文章级情感分类列, 纯粹是地理坐标层面的覆盖统计, 不区分 full/ctx/ss)。分子 `n_within(200)` 为银行总部城市坐标与媒体来源城市 (或省份省会 Level-3 回退坐标) 之间 haversine 球面距离 ≤200 公里的文章数, 分母 `n_geocoded` 为该 bank-year 内媒体侧可成功地理编码的文章总数——不是全部文章数 n_total, 这一分母口径修复自 2026-06-10 metric-audit (fix(prox-frac-denominator)): 若把无法定位坐标的文章计入分母, 会人为稀释地理覆盖度, 造成可验证覆盖率与物理覆盖率两种不同分母域的混淆(P3 级测度勘误)。四档满足单调拓扑关系 prox_50km_frac ≤ prox_100km_frac ≤ prox_150km_frac ≤ prox_200km_frac, producer 内对该单调性设有断言校验, 任何一档违反单调关系都会在面板构建阶段直接暴露, 不会静默通过。当该 bank-year 媒体侧全部不可地理编码时 (`n_geocoded=0`), 本列记 NaN 而非 0, 与圈内有无媒体尚属未知的语义对齐, 不与确知圈内为空的场景混淆——这是 omni-g-geography-02 修复所解决的诊断列间自相矛盾问题 (此前 is_local 记 0 而 frac 记 NaN, 两列互相矛盾, 现已统一为同一 NaN 语义)。该列同时是同阈值下 `prox_200km_pos_frac`/`neg_frac` 系列 (含 full/ctx/ss 三轨孪生共 6 列) 共享的圈内文章样本量基准: 二者共用同一 `n_within(200)`/`n_geocoded` 定义, 但服务不同构念——本列刻画地理覆盖广度, 情感占比列刻画圈内报道基调构成, 不应把二者混同为同一测度的不同表达。与相邻阈值档 (prox_150km_frac) 互为接近度定义的稳健性梯度, 不预设单一最优半径, 仅提供距离敏感性展示窗口, 使用时不应孤立看待单一半径档的数值。

## VAR: prox_200km_neg_frac

【变体差分】
本列是 200 公里圈 full 轨 (全文正文+标题) 的负面文章占比: 分子取 `is_negative_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_negative_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_neg_frac_ctx`(ctx 轨) 及 `prox_200km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_pos_frac` (正面占比) 互补 (prox_200km_neg_frac+prox_200km_pos_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_neg_frac_ctx

【变体差分】
本列是 200 公里圈 ctx 轨 (标题+银行实体窗口) 的负面文章占比: 分子取 `is_negative_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_negative_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_neg_frac`(full 轨) 及 `prox_200km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_pos_frac_ctx` (正面占比) 互补 (prox_200km_neg_frac_ctx+prox_200km_pos_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_neg_frac_ss

【变体差分】
本列是 200 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的负面文章占比: 分子取 `is_negative_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_negative_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_neg_frac`(full 轨) 及 `prox_200km_neg_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_pos_frac_ss` (正面占比) 互补 (prox_200km_neg_frac_ss+prox_200km_pos_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_pos_frac

【变体差分】
本列是 200 公里圈 full 轨 (全文正文+标题) 的正面文章占比: 分子取 `is_positive_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_positive_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_pos_frac_ctx`(ctx 轨) 及 `prox_200km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_neg_frac` (负面占比) 互补 (prox_200km_pos_frac+prox_200km_neg_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_pos_frac_ctx

【变体差分】
本列是 200 公里圈 ctx 轨 (标题+银行实体窗口) 的正面文章占比: 分子取 `is_positive_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_positive_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_pos_frac`(full 轨) 及 `prox_200km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_neg_frac_ctx` (负面占比) 互补 (prox_200km_pos_frac_ctx+prox_200km_neg_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_200km_pos_frac_ss

【变体差分】
本列是 200 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的正面文章占比: 分子取 `is_positive_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤200km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_200km_frac` 的圈内可定位文章集合 `n_within(200)`, 若该值为 0 或 `is_positive_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_200km_pos_frac`(full 轨) 及 `prox_200km_pos_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 200 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_200km_neg_frac_ss` (负面占比) 互补 (prox_200km_pos_frac_ss+prox_200km_neg_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档半径最宽, 往往覆盖整个省域或跨省相邻地级市群, 样本量在四档中通常最充裕、数值最稳定, 适合作为距离梯度组内的稳健性基准。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_frac

【变体差分】
本列是 50 公里同心圈的几何覆盖比例, 属四阈值梯度中的最窄档(梯度下界), 与情感、三轨口径均无关(track-agnostic, 不消费 is_positive/is_negative 等任何文章级情感分类列, 纯粹是地理坐标层面的覆盖统计, 不区分 full/ctx/ss)。分子 `n_within(50)` 为银行总部城市坐标与媒体来源城市 (或省份省会 Level-3 回退坐标) 之间 haversine 球面距离 ≤50 公里的文章数, 分母 `n_geocoded` 为该 bank-year 内媒体侧可成功地理编码的文章总数——不是全部文章数 n_total, 这一分母口径修复自 2026-06-10 metric-audit (fix(prox-frac-denominator)): 若把无法定位坐标的文章计入分母, 会人为稀释地理覆盖度, 造成可验证覆盖率与物理覆盖率两种不同分母域的混淆(P3 级测度勘误)。四档满足单调拓扑关系 prox_50km_frac ≤ prox_100km_frac ≤ prox_150km_frac ≤ prox_200km_frac, producer 内对该单调性设有断言校验, 任何一档违反单调关系都会在面板构建阶段直接暴露, 不会静默通过。当该 bank-year 媒体侧全部不可地理编码时 (`n_geocoded=0`), 本列记 NaN 而非 0, 与圈内有无媒体尚属未知的语义对齐, 不与确知圈内为空的场景混淆——这是 omni-g-geography-02 修复所解决的诊断列间自相矛盾问题 (此前 is_local 记 0 而 frac 记 NaN, 两列互相矛盾, 现已统一为同一 NaN 语义)。该列同时是同阈值下 `prox_50km_pos_frac`/`neg_frac` 系列 (含 full/ctx/ss 三轨孪生共 6 列) 共享的圈内文章样本量基准: 二者共用同一 `n_within(50)`/`n_geocoded` 定义, 但服务不同构念——本列刻画地理覆盖广度, 情感占比列刻画圈内报道基调构成, 不应把二者混同为同一测度的不同表达。与相邻阈值档 (prox_100km_frac) 互为接近度定义的稳健性梯度, 不预设单一最优半径, 仅提供距离敏感性展示窗口, 使用时不应孤立看待单一半径档的数值。

## VAR: prox_50km_neg_frac

【变体差分】
本列是 50 公里圈 full 轨 (全文正文+标题) 的负面文章占比: 分子取 `is_negative_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_negative_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_neg_frac_ctx`(ctx 轨) 及 `prox_50km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_pos_frac` (正面占比) 互补 (prox_50km_neg_frac+prox_50km_pos_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_neg_frac_ctx

【变体差分】
本列是 50 公里圈 ctx 轨 (标题+银行实体窗口) 的负面文章占比: 分子取 `is_negative_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_negative_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_neg_frac`(full 轨) 及 `prox_50km_neg_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_pos_frac_ctx` (正面占比) 互补 (prox_50km_neg_frac_ctx+prox_50km_pos_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_neg_frac_ss

【变体差分】
本列是 50 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的负面文章占比: 分子取 `is_negative_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_negative_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_neg_frac`(full 轨) 及 `prox_50km_neg_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_pos_frac_ss` (正面占比) 互补 (prox_50km_neg_frac_ss+prox_50km_pos_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_pos_frac

【变体差分】
本列是 50 公里圈 full 轨 (全文正文+标题) 的正面文章占比: 分子取 `is_positive_full` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_positive_full` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_pos_frac_ctx`(ctx 轨) 及 `prox_50km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_neg_frac` (负面占比) 互补 (prox_50km_pos_frac+prox_50km_neg_frac 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 full 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_pos_frac_ctx

【变体差分】
本列是 50 公里圈 ctx 轨 (标题+银行实体窗口) 的正面文章占比: 分子取 `is_positive_ctx` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_positive_ctx` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_pos_frac`(full 轨) 及 `prox_50km_pos_frac_ss`(ss 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_neg_frac_ctx` (负面占比) 互补 (prox_50km_pos_frac_ctx+prox_50km_neg_frac_ctx 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ctx 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

## VAR: prox_50km_pos_frac_ss

【变体差分】
本列是 50 公里圈 ss 轨 (标题+银行∧金科同句共现窗口(句子半径由 config/filtering.yaml::context_window.ss_sentence_radius 控制,默认1;无共现回退全文,对应 ss_is_fallback=True)) 的正面文章占比: 分子取 `is_positive_ss` (来自 stage 21 三家 LLM 多数投票产出的文章级二值指标) 在圈内 (haversine ≤50km 且可地理编码) 文章子集上的均值, 分母对齐 `prox_50km_frac` 的圈内可定位文章集合 `n_within(50)`, 若该值为 0 或 `is_positive_ss` 源列缺失, 本列优雅降级为 NaN 而非 0, 与家族内几何覆盖列共享同一未知-vs-确知为空的 NaN 语义, 不外推填补。与同阈值 `prox_50km_pos_frac`(full 轨) 及 `prox_50km_pos_frac_ctx`(ctx 轨) 构成三轨并排组: 三者共享同一 50 公里地理圈定义, 差异仅在情感判定所消费的文本窗口不同, 各自 just-identified、互为稳健性、不分主次, 禁止混入同一 over-identified Hansen J 检验。与同阈值 `prox_50km_neg_frac_ss` (负面占比) 互补 (prox_50km_pos_frac_ss+prox_50km_neg_frac_ss 一般 <1, 差值由中性判定占据)。若上游情感留篇门控采用 full-only 口径 (2026-06-29 起生产口径), 则 ss 轨的样本宇宙是 full 轨留篇集合的子集 (conditional-on-full), 而非独立扩样, 与其余 full 轨列共享同一行样本定义。本档地理半径最窄, 圈内可定位文章数通常最少, 是家族内小样本/缺失风险最高的一档, 解读时须结合圈内文章数一并考察, 不宜孤立看待单一比例值。与更宽/更窄阈值档 (即 50/100/150/200km 中除本档外的其余三档) 的同轨同符号列构成距离梯度稳健性组, 各阈值互为稳健性、不预设“距离越近占比越高/越低”的单调因果方向, 仅作接近度定义的敏感性展示, 结论应由实证数据决定而非测度本身内含的假设。

<!-- rendered-citations:begin -->
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
Chen, Q., Goldstein, I., Huang, Z., & Vashishtha, R. (2022). Bank transparency and deposit flows. Journal of Financial Economics, 146(2), 475-501. https://doi.org/10.1016/j.jfineco.2022.07.009
Guo, L., Zhu, H., Zhang, C., Liu, Y., & Yang, C. (2024). Does improved credit access promote pollution reduction? The role of bank proximity. Economic Analysis and Policy, 84, 78-97. https://doi.org/10.1016/j.eap.2024.08.019
Boschma, R. (2005). Proximity and innovation: A critical assessment. Regional Studies, 39(1), 61-74. https://doi.org/10.1080/0034340052000320887
Piotroski, J. D., Wong, T. J., & Zhang, T. (2015). Political incentives to suppress negative information: Evidence from Chinese listed firms. Journal of Accounting Research, 53(2), 405-459. https://doi.org/10.1111/1475-679X.12071
Xiong, X., Ruan, C., & Meng, Y. (2025). Geographical distance and stock price synchronization: evidence from China. Financial Innovation. https://doi.org/10.1186/s40854-025-00764-1
<!-- rendered-citations:end -->
