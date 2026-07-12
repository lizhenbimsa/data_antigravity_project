---
family_id: F104
columns:
- bartik_geoprox_share_local
- bartik_geoprox_share_nonlocal
unit: 基期份额 (proportion, 无量纲, 取值域 [0,1]; 同一银行两列在基期有报道时相加恒为 1, 基期无报道则两列同为 NaN)
formula: "bartik_geoprox_share_{local,nonlocal}[i] = n_{i,k,T0} / Σ_{k'∈{local,nonlocal}} n_{i,k',T0}; k=local 当报道媒体所属省份 == 银行注册省份, 否则 k=nonlocal; T0 = max(panel.year.min, 2010) 且强制 < 2019 (DCEP 里程碑); 基期无报道 → NaN (非 fillna(0) 伪零)"
producer: news_process/pipeline/panel/iv_did.py::compute_bartik_iv_fintech (runner.py 步骤 7e 稳健性 5 geoprox 调用; 标签在 pipeline/panel/export.py)
upstream:
- 40 阶段 df_exploded 文章级数据 (target_bank / year / 媒体省份列 '国家地区/省份')
- config/bank_addresses.json (银行注册省份映射 province)
citations:
- doi: 10.1257/aer.20200374
  type: journal
  authors: Aguirregabiria, V., Clark, R., & Wang, H.
  year: 2025
  title: "The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition"
  venue: American Economic Review
  vol: 115
  issue: 6
  pages_or_artno: 1818-1856
- doi: 10.1257/jep.20231370
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2025
  title: "A practical guide to shift-share instruments"
  venue: Journal of Economic Perspectives
  vol: 39
  issue: 1
  pages_or_artno: 181-204
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1162/0033553041502162
  type: journal
  authors: Guiso, L., Sapienza, P., & Zingales, L.
  year: 2004
  title: "Does local financial development matter?"
  venue: Quarterly Journal of Economics
  vol: 119
  issue: 3
  pages_or_artno: 929-969
- doi: 10.1111/0022-1082.00181
  type: journal
  authors: Coval, J. D., & Moskowitz, T. J.
  year: 1999
  title: "Home bias at home: Local equity preference in domestic portfolios"
  venue: Journal of Finance
  vol: 54
  issue: 6
  pages_or_artno: 2045-2073
- doi: 10.17848/9780585223940
  type: book
  authors: Bartik, T. J.
  year: 1991
  title: "Who benefits from state and local economic development policies?"
  venue: W.E. Upjohn Institute for Employment Research
new_dois: []
---

## CORE

【构念与来源】
本家族的两列是「地理邻近性」维度 Bartik shift-share 工具的基期份额 (share) 分量, 刻画每家目标银行在冻结基期内, 其媒体报道来源在地理上「本地 (local)」与「非本地 (nonlocal)」两类的构成比例。构念根源来自 shift-share (Bartik) 工具的经典分解: 一个内生的 bank-year 暴露度可写成「基期份额 × 后续冲击」的加权和, 其中份额在处理前 (pre-treatment) 期固定、被视为外生权重, 冲击则来自份额所指向的外部单元。地理邻近的份额之所以有意义, 在于本地媒体与异地媒体对同一家银行的报道动机、议题选择与情感基调系统性不同: 本地媒体受本地广告市场与读者利益牵引, 报道更密、也更可能偏软 (Coval & Moskowitz (1999) 记录的「本地偏好」与本地金融发展的实体效应见 Guiso, Sapienza & Zingales (2004)), 因此银行「暴露在本地 vs 异地媒体生态」的基期结构, 是一个既与银行属性 (注册地) 绑定、又在处理前固定的合理外生份额来源。银行注册地属性在样本期内不随时间变化、媒体所属省份是每篇报道的既有属性, 二者在报道层交叉得到 local/nonlocal 二分, 交叉结果在基期一次冻结后不再更新 (Engelberg & Parsons 传统的地理邻近逻辑 + Aguirregabiria, Clark & Wang (2025) 关于银行资金与信贷的地理流动/本地竞争框架为该维度提供了制度基础)。

【方法学与计算】
两列由 iv_did.py 的 compute_bartik_iv_fintech 在 runner 步骤 7e「稳健性 5: 地理邻近性」处产出。判定链路: 先由 config/bank_addresses.json 取每家银行注册省份, 再把每篇报道的媒体省份列 (国家地区/省份) 与之比对, 相等记为 local、否则记为 nonlocal, 写入文章级临时列; 随后仅取处理前基期 T0 的报道, 按银行 × 类别计数, 除以该银行基期内 local 与 nonlocal 两类计数之和 (分母只含被保留的两类, 不含 other/未映射) 得到份额。因此对任一在基期有报道的银行, share_local 与 share_nonlocal 严格互补、相加为 1; 若某银行基期内没有任何可识别报道, 两列同置 NaN, 而非旧实现的 fillna(0) 伪零暴露——这一缺失语义与主 Bartik (type/scale) 完全同口径, 避免制造「零本地暴露」的虚假观测。基期取 T0 = max(panel.year.min, 2010), 并强制 T0 小于政策冲击里程碑 2019 (DCEP 试点): 若计算所得基期落入或越过里程碑年, 直接 raise, 以严守份额在处理前期固定的外生性公理 (Goldsmith-Pinkham, Sorkin & Swift (2020) 的核心可信度条件)。份额分母所依据的基期报道集, 是经 full-only 留篇门控 (2026-06-29) 保留下来的银行金科报道全文轨集合, 与 n_articles 的 full-only 口径一致; 份额本身是 track-agnostic 的元数据式度量 (只依赖报道来源省份与银行注册地, 不依赖情感或三轨文本剪裁), 故这两列没有 full/ctx/ss 三轨孪生, 也没有 co-primary 嵌入的 _lg 孪生。份额下游与 local/nonlocal 各类的 leave-one-out 年度情感冲击相乘、跨类求和, 得到 bartik_geoprox_iv_full/_ctx/_ss 三条工具轨。

【文献定位】
方法学上, shift-share 工具的可信度可从两条互补路径论证: 一是份额外生 (Goldsmith-Pinkham, Sorkin & Swift (2020) 的基期份额外生 + Rotemberg 权重诊断), 二是冲击外生 (Borusyak, Hull & Jaravel (2022) 的准实验视角与 Adão, Kolesár & Morales (2019) 的等价推断与标准误校正)。Borusyak, Hull & Jaravel (2025) 给出的实操检查表进一步明确了不完全份额与重归一化选择的正确处理, Apfel (2024) 则讨论了放松排他性约束的条件。就本项目而言, 地理邻近仅作为主 Bartik (银行类型) 的稳健性维度之一并列存在: 各维度、各轨工具「各自 just-identified 并排、互为稳健性、不分主次」, 严禁把不同维度或不同轨 (full/ctx/ss) 的工具拼进同一个 over-identified 的 Hansen J 检验——它们源自同一批报道的同构剪裁, 组内共同冲击逐字污染各轨, J 对真实威胁功效近零且拖垮弱工具诊断 (Hahn, Kuersteiner, Santos & Willigrod (2024) 提供了 shift-share 过度识别的计量支撑)。名义上, 「Bartik」加权范式的源头是 Bartik (1991); 而本地/异地媒体生态差异所对应的实体经济通道, 由本地金融发展 (Guiso, Sapienza & Zingales (2004))、本地偏好 (Coval & Moskowitz (1999)) 与银行资金地理流动 (Aguirregabiria, Clark & Wang (2025)) 三支文献共同锚定。

## VAR: bartik_geoprox_share_local

【变体差分】
本列是地理邻近维度 Bartik 工具在「本地 (local)」类别上的基期份额, 记录目标银行在冻结基期 T0 内, 由「所属省份 == 银行注册省份」的媒体所发报道占该银行基期 local+nonlocal 总报道数的比例。判据是逐篇报道级的省份相等比对: 银行注册省份取自 config/bank_addresses.json, 媒体省份取自文章列「国家地区/省份」, 二者相等即计入本列分子。它与同族 bartik_geoprox_share_nonlocal 严格互补——同一银行在基期有报道时两列相加恒为 1, 因此本列可读作「基期本地媒体暴露强度」的直接刻画, 数值越高说明该行的基期舆论环境越以本地媒体为主导。取值域为 [0,1]; 当银行基期内无任何可识别报道时本列为 NaN (与 nonlocal 列同步置 NaN), 承接主 Bartik 的缺失外生性口径, 不做 fillna(0) 伪零。本列是 track-agnostic 的冻结份额权重, 不区分 full/ctx/ss 三轨、也无 _lg 嵌入孪生; 它不是最终回归量, 而是与 local 类别的其他银行 leave-one-out 情感冲击相乘后, 汇入 bartik_geoprox_iv 三轨工具的外生权重分量。基期 T0 强制小于 2019 里程碑, 保证本列在处理前期固定, 满足 shift-share 份额外生性要求。相对家族 canonical 的差分仅在类别取值 (local 而非 nonlocal), 其余基期口径、分母构成、缺失语义与 nonlocal 列完全对称。

## VAR: bartik_geoprox_share_nonlocal

【变体差分】
本列是地理邻近维度 Bartik 工具在「非本地 (nonlocal)」类别上的基期份额, 记录目标银行在冻结基期 T0 内, 由「所属省份 != 银行注册省份」的异地媒体所发报道占该银行基期 local+nonlocal 总报道数的比例。判据与 local 列镜像对称: 凡媒体省份不等于银行注册省份的报道 (含省份缺失被判为非相等) 计入本列分子, 分母同为该银行基期 local 与 nonlocal 两类计数之和 (不含 other/未映射)。因此本列与 bartik_geoprox_share_local 严格互补, 同一银行在基期有报道时两列相加恒为 1, 数值越高说明该行基期舆论环境越依赖跨省异地媒体, 报道更可能出自与本地广告市场/读者利益脱钩的来源, 情感基调偏中性或偏硬的先验更强。取值域 [0,1]; 基期无报道时与 local 列同步置 NaN, 承接主 Bartik 缺失外生性口径, 不做 fillna(0) 伪零。本列同为 track-agnostic 冻结份额, 无 full/ctx/ss 三轨与 _lg 孪生, 亦非最终回归量, 而是与 nonlocal 类别其他银行的 leave-one-out 情感冲击相乘后汇入 bartik_geoprox_iv 三轨工具。相对家族 canonical 的差分仅在类别取值 (nonlocal 而非 local): 它与 local 列不构成两条可并排跑 Hansen J 的独立工具, 而是同一 geoprox 维度内互补的两个份额分量, 共同定义单一 geoprox 工具的外生权重结构; geoprox 维度自身则与 type/scale/media/mauth 等维度各自 just-identified 并排、互为稳健性、禁混进同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Aguirregabiria, V., Clark, R., & Wang, H. (2025). The geographic flow of bank funding and access to credit: Branch networks, synergies, and local competition. American Economic Review, 115(6), 1818-1856. https://doi.org/10.1257/aer.20200374
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Guiso, L., Sapienza, P., & Zingales, L. (2004). Does local financial development matter?. Quarterly Journal of Economics, 119(3), 929-969. https://doi.org/10.1162/0033553041502162
Coval, J. D., & Moskowitz, T. J. (1999). Home bias at home: Local equity preference in domestic portfolios. Journal of Finance, 54(6), 2045-2073. https://doi.org/10.1111/0022-1082.00181
Bartik, T. J. (1991). Who benefits from state and local economic development policies?. W.E. Upjohn Institute for Employment Research. https://doi.org/10.17848/9780585223940
<!-- rendered-citations:end -->
