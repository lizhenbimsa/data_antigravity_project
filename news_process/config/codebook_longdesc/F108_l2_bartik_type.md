---
family_id: F108
columns:
- bartik_type_share_city
- bartik_type_share_foreign
- bartik_type_share_joint
- bartik_type_share_rural
- bartik_type_share_soe
unit: "份额/占比 (proportion, 无量纲, 定义域 [0,1]; 同一银行的六类型份额在有效样本上求和为 1; 基期完全无共现文章的银行整行 NaN; 有文章但无任何非 'other' 共现时按 own_group 分叉: 映射到真实类型者走 one-hot 兜底=1、未映射者 NaN)"
formula: "bartik_type_share_{g} = count_base(bank i 的基期共现同业中类型为 g 的次数) / total_base(bank i 的基期非 'other' 同业共现总次数); 基期 T0 = max(panel.year.min, 2010) 且强约束 T0 < 政策冲击里程碑 (Goldsmith-Pinkham et al. 2020 基期外生性公理); 该组共现次数为 0 但存在非 'other' 分母 → 份额真零 0; 银行基期无任何非 'other' 共现 (total_base==0) 时按自身类型分叉: 若该行被映射到六类真实类型之一 (own_group ∈ groups) → one-hot 兜底 (own 组 share=1.0, 其余五列 0.0), 若未映射 (own_group='other') → 全六列 NaN; 基期完全无共现文章 (不进 base) 的银行整行 NaN"
producer: "news_process/pipeline/panel/iv_did.py::compute_bartik_iv (由 pipeline/panel/runner.py 以位置参数 group_prefix='type' 调用: compute_bartik_iv(panel, df_exploded, type_map, 'type', base_year=T0); 变量标签在 pipeline/panel/export.py 挂载)"
upstream:
- 13_cooccurrence_filter.parquet (银行共现文章; 提供 co_mentioned_banks 同业列表)
- config/bank_addresses.json (经 load_bank_group_maps 读取 CONFIG['paths']['bank_addresses_file']; nfra_type → NFRA_TO_SHORT 六类型映射)
- 40_panel_yearly.parquet (bank-year 骨架, 承接 share 与下游 bartik_type_iv_* 工具列)
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
- doi: 10.48550/arXiv.2404.17049
  type: arxiv
  authors: Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W.
  year: 2024
  title: "Overidentification in shift-share designs"
  venue: arXiv
- doi: 10.1093/jrsssa/qnad148
  type: journal
  authors: Apfel, N.
  year: 2024
  title: "Relaxing the exclusion restriction in shift-share instrumental variable estimation"
  venue: "Journal of the Royal Statistical Society Series A: Statistics in Society"
  vol: 187
  issue: 3
  pages_or_artno: 748-771
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
- doi: 10.1257/0002828054201242
  type: journal
  authors: Burgess, R., & Pande, R.
  year: 2005
  title: "Do rural banks matter? Evidence from the Indian social banking experiment"
  venue: American Economic Review
  vol: 95
  issue: 3
  pages_or_artno: 780-795
- doi: "10.1016/j.jfineco.2024.103934"
  type: journal
  authors: "Goldstein, I., Kopytov, A., Shen, L., & Xiang, H."
  year: 2024
  title: "Bank heterogeneity and financial stability"
  venue: "Journal of Financial Economics"
- doi: "10.3390/jrfm18080440"
  title: "An Empirical Study on the Impact of Financial Technology on the Profitability of China's Listed Commercial Banks"
  authors: "Yuan, X., Puah, C.-H., & Marikan, D. A. binti A."
  year: 2025
  venue: "Journal of Risk and Financial Management"
  type: "journal"
- doi: "10.1016/j.iref.2024.103788"
  title: "Empirical analysis of the impact of financial technology on the profitability of listed banks"
  authors: "Xiao, T., & Wang, Y."
  year: 2025
  venue: "International Review of Economics & Finance"
  type: "journal"
new_dois:
  - "10.1016/j.jfineco.2024.103934"
  - "10.3390/jrfm18080440"
  - "10.1016/j.iref.2024.103788"
---

## CORE

【构念与来源】
本家族是主 Bartik (shift-share) 工具变量的"份额 (share)"组件, 按银行类型维度切分。它回答一个基期性问题: 在样本最早的基期年 T0, 每一家目标银行在媒体报道里和"哪一类同业"走得最近。具体地, 引擎扫描基期年内该目标银行的全部共现文章, 取出每篇同现提及的其他银行 (co_mentioned_banks), 按国家金融监督管理总局口径的银行类型 (nfra_type, 经 NFRA_TO_SHORT 归并为六类: 国有大型商业银行 soe、股份制银行 joint、城市商业银行 city、农村商业银行 rural、民营银行 private、外资银行 foreign) 逐一贴签, 再统计各类型在该行基期同业共现里所占的比例。于是每家银行在基期就得到一个"类型暴露向量", 六个分量分别记为 bartik_type_share_{soe,joint,city,rural,private,foreign}, 各分量取值于 [0,1], 在有效样本上求和为 1。本家族收录其中五列 (soe、joint、city、rural、foreign; private 分量在盘上样本中不成列)。这一暴露结构一旦在基期算定即被"冻结"不再随年份变化, 是整个 Bartik 识别的横截面权重来源。

【方法学与计算】
计算发生在 pipeline/panel/iv_did.py::compute_bartik_iv 内, 由 runner.py 以位置参数 group_prefix='type' (第四个位置实参, 调用形如 compute_bartik_iv(panel, df_exploded, type_map, 'type', base_year=T0)) 传入类型映射 type_map 调用, 变量标签在 export.py 挂载; 该 type_map 由 load_bank_group_maps 从 config/bank_addresses.json (CONFIG['paths']['bank_addresses_file']) 逐行读取每家银行的 nfra_type 字段、经 NFRA_TO_SHORT 归并为六短码而成, 与 config/bank_list.yaml 无关。基期年 T0 = max(panel.year.min, 2010), 且在 runner.py 内受一道硬性外生性守卫: 若 T0 已达到或越过政策冲击里程碑 (_bartik_pre_cutoff), 直接 RuntimeError 中止, 因为基期份额一旦落入 post-treatment 区间就违反 Goldsmith-Pinkham et al. (2020) 所强调的"基期 share 外生性"公理。份额本身的算法是: 对每家在基期有文章的银行, 把它基期内所有同业共现按类型 explode-map-groupby 向量化计数, 分母是该行全部非 'other' 类型的共现总次数, 分子是落在类型 g 的共现次数, 二者相除即得 share。这里四类缺失/边界语义务必写清, 且分层不可混同: 其一, 基期完全无共现文章的银行 (根本不进 base、不出现在遍历的 target_bank 集合里), 不产任何 share 行, 经下游 merge 后六列整行保持 NaN 而非填零 —— 早期 fillna(0) 会把"工具缺失"伪装成"零暴露", 在下游二阶段最小二乘一阶段制造 incomplete-shares 伪零离群 (Goldsmith-Pinkham et al. 2020); 其二, 银行有基期文章、但其全部同业共现在归类后 total_base==0 (即无任何非 'other' 共现) 时, 并非一律 NaN, 而是按银行自身类型 own_group 分叉——若该行本身被映射到六类真实类型之一 (own_group ∈ groups), 引擎走 one-hot 兜底: 令 own 组份额=1.0、其余五列=0.0 (源码 iv_did.py: total==0 分支内 share = 1.0 if g==own_group else 0.0), 视作"该行只与自身类型自我暴露"的极限情形而非缺失; 其三, 承接其二, 只有当 total_base==0 且该行自身也未被类型字典映射到 (own_group=='other') 时, 才 continue 跳过、整行 NaN, 因为此时 one-hot 兜底会退化为全 0 行使 Σshare=0≠1、制造 IV 伪零; 其四, 银行有真实非 'other' 分母、但某个类型 g 一次都没共现到, 该列取真零 0 (有分母、分子为零), 这是常态的稀疏零而非缺失。三/四两点须与 compute_bartik_iv_fintech "基期文章全 'other'/未映射 → NaN" 的口径对齐。份额向下游与"冲击 (shift)"分量 (同类型别的银行的年度情感变化, 自身组走 leave-one-out) 相乘再求和, 汇成 bartik_type_iv_{full,ctx,ss} 工具列; 份额还派生 _t0/_t1/_t01 三个基期敏感性变体, 用来检验工具对基期年选择是否稳健, 其中任何令基期落入 post-treatment 的变体一律置 NaN 并告警。需强调本家族只是"份额半成品", 不是可直接进结果方程的回归变量; 它的意义在于诊断与识别透明度 (可读出每家银行的类型暴露构成、可算 Rotemberg 权重)。早期试跑盘上曾为 T=2 样本 (2017–2018), 基期结构高度退化, 份额分布稀疏属预期, 生产 T=19 语料下方回归常态。

【文献定位】
Bartik (shift-share) 工具变量把内生自变量拆成"基期份额 × 外部冲击"的加权和, 其份额外生性识别路径由 Goldsmith-Pinkham, Sorkin & Swift (2020) 在《美国经济评论》系统化, 并给出 Rotemberg 权重这一"哪几个份额在真正驱动识别"的诊断工具, 本管道正是沿其份额视角构造工具 (而非 Borusyak, Hull & Jaravel 2022 的冲击准随机视角), 两条路径的区分与相应诊断清单见 Borusyak, Hull & Jaravel (2025) 的实操指南。份额型设计的推断校正 (跨截面相关、有效样本量塌缩) 由 Adão, Kolesár & Morales (2019) 奠定, 排他性约束的松弛与检验思路见 Apfel (2024)。就类型维度多工具并用而言, Hahn, Kuersteiner, Santos & Willigrod (2024) 讨论了 shift-share 设计中的过度识别问题, 构成本管道一条铁律的计量支撑: 银行类型、规模、金融科技类别三套 Bartik 工具各自 just-identified 并排、互为稳健性不分主次, 严禁混入同一 over-identified 的 Hansen J 检验; 同理主工具的三条文本轨 (full/ctx/ss, ss 语义镜像 ctx: 无银行与金科同句共现时回退全文) 与基期敏感性变体亦各自 just-identified 并排, 不得合并过度识别。类型切分之所以经济上有意义, 是因为不同类型银行的功能定位差异实在 —— 例如 Burgess & Pande (2005) 证明面向农村的银行网点扩张对减贫与产出有真实因果效应, 提示农商行、城商行等地方性类型与国有大行、外资行的暴露结构不可互换。Goldstein, Kopytov, Shen & Xiang (2024, Journal of Financial Economics) 建立银行异质性影响系统性风险传导的模型, 佐证本家族按国有大行、股份制、城商、农商、外资六类切分同业暴露结构的经济含义。Yuan, Puah & Marikan (2025, Journal of Risk and Financial Management) 实证发现金融科技对国有大行与股份制银行盈利的负面冲击比中小银行更显著, 支持按银行类型切分同业暴露结构的经济含义; Xiao & Wang (2025, International Review of Economics & Finance) 基于33家上市银行文本挖掘构造金融科技指数, 证明金融科技对银行盈利的影响因银行类型异质而不同。

## VAR: bartik_type_share_city

【变体差分】
本列是类型暴露向量在"城市商业银行 (city)"分量上的取值。它度量在基期年 T0, 目标银行的同业媒体共现里有多大比例落在城商行类型: 分子是该行基期共现同业中被 NFRA_TO_SHORT 归为 city 的次数, 分母是该行全部非 'other' 同业共现总次数。城商行是中国银行体系里地方性、区域深耕特征最鲜明的一类, 其份额高意味着该目标银行在报道叙事中更常与本地/区域性同业绑定, 从而在下游 Bartik 工具里承接"城商行群体年度情感冲击"的更大权重。与家族其余四列的唯一区别就在类型桶 g='city' 这一分组标签, 计算口径、基期 T0、外生性守卫、NaN/零缺失语义完全一致 —— 六个类型分量共享同一分母、共享同一批基期共现文章, 因而在有效样本上求和为 1, 彼此是同一暴露向量的互补分量而非独立测度。它不做轨道、模型、阈值区分 (份额是 track-agnostic 的横截面元数据, 三轨差异只体现在下游相乘的 shift 与最终 bartik_type_iv 工具列); 城商行份额本身不入结果方程, 与规模维度、金融科技类型维度的对应份额各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。基期无共现的银行本列为 NaN, 城商行一次未共现到但有其他共现的银行本列为真零。

## VAR: bartik_type_share_foreign

【变体差分】
本列是类型暴露向量在"外资银行 (foreign)"分量上的取值, 度量基期年 T0 目标银行同业共现里外资银行类型所占比例: 分子为基期共现同业中被归为 foreign 的次数, 分母为该行非 'other' 同业共现总次数。外资银行在中国银行业中数量少、区域集中于开放前沿城市、业务定位偏跨境与高端, 其暴露结构与本土大行、地方法人差异显著; 份额较高的目标银行在下游工具里更多吸收"外资银行群体年度情感冲击", 这一维度天然稀疏, 在早期试跑 T=2 样本上多为零或 NaN 属预期退化, 生产 T=19 语料下才见常态分布。本列与家族其余四列的唯一差别是类型桶 g='foreign', 其余口径 (基期 T0=max(panel.year.min,2010)、post-treatment 外生性守卫、分母去 'other'、基期无文章整行 NaN、未映射银行 NaN) 逐字相同。作为同一暴露向量的一个互补分量, 它与 soe/joint/city/rural (及盘外的 private) 份额求和为 1, 不是独立构念。份额是横截面元数据不分文本轨道, 不设阈值与滞后 (滞后语义体现在下游 shift 与工具列); 本列与规模、金融科技类型两套 Bartik 份额各自 just-identified 并排、互为稳健性不分主次, 严禁并入同一 over-identified Hansen J。需要提醒的是, 外资类型的高稀疏性意味着本列在小样本上的方差主要来自少数几家与外资行有共现的目标银行, 解读其在 Rotemberg 权重诊断中的贡献时应格外审慎, 避免把早期试跑样本的退化误读为经济上的零暴露。

## VAR: bartik_type_share_joint

【变体差分】
本列是类型暴露向量在"股份制银行 (joint, joint-stock)"分量上的取值, 度量基期年 T0 目标银行同业共现里全国性股份制商业银行所占比例: 分子为基期共现同业中被 NFRA_TO_SHORT 归为 joint 的次数, 分母为该行非 'other' 同业共现总次数。股份制银行是介于国有大行与地方法人之间的全国性市场化主体, 网络覆盖广、市场化程度高, 是媒体金融叙事中高频共现的一类; 股份制份额高的目标银行在下游 Bartik 工具里承接"股份制群体年度情感冲击"的更大权重。本列区别于家族其余四列的唯一维度是类型分组标签 g='joint', 计算链路、基期定义、外生性守卫、缺失语义与其余分量完全对齐, 六分量共享同一批基期共现文章与同一分母, 在有效样本上求和为 1, 构成同一暴露向量的互补切片而非彼此独立的测度。份额为 track-agnostic 横截面元数据, 不做 full/ctx/ss 三轨、模型、阈值、权重、滞后的区分 (这些差异全部下沉到与之相乘的 shift 及最终 bartik_type_iv_{full,ctx,ss} 工具列); 股份制份额与银行规模维度、金融科技类型维度的对应份额各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。基期无共现的银行本列 NaN, 有共现但股份制零次的银行本列为真零 0。

## VAR: bartik_type_share_rural

【变体差分】
本列是类型暴露向量在"农村商业银行 (rural)"分量上的取值, 度量基期年 T0 目标银行同业共现里农商行类型所占比例: 分子为基期共现同业中被归为 rural 的次数, 分母为该行非 'other' 同业共现总次数。农商行是数量庞大、扎根县域与农村金融、服务下沉市场的一类地方法人, 其功能定位与国有大行、外资行截然不同 —— 面向农村的银行网络对当地信贷可得性与产出的真实因果作用有既有证据支撑 (Burgess & Pande 2005), 使农商行暴露成为一个经济含义鲜明、不可与其他类型互换的维度。农商行份额高的目标银行在下游工具里更多承接"农商行群体年度情感冲击"。本列与家族其余四列的唯一区别是类型桶 g='rural', 其余口径 (基期 T0、外生性守卫、去 'other' 分母、基期无文章 NaN、未映射银行 NaN、有分母零分子取真零) 逐字一致, 作为同一暴露向量的互补分量与 soe/joint/city/foreign (及盘外 private) 求和为 1。份额为横截面元数据不分文本轨道、不设阈值滞后; 本列与规模、金融科技类型两套 Bartik 份额各自 just-identified 并排、互为稳健性不分主次, 严禁并入同一 over-identified Hansen J。正因农商行在地方金融叙事中的高频出现, 本列在生产语料下往往对地方性目标银行取到实质性正值, 是区分"地方法人—全国性主体"暴露结构的关键切片之一。

## VAR: bartik_type_share_soe

【变体差分】
本列是类型暴露向量在"国有大型商业银行 (soe)"分量上的取值, 度量基期年 T0 目标银行同业共现里国有大行类型所占比例: 分子为基期共现同业中被 NFRA_TO_SHORT 归为 soe 的次数, 分母为该行全部非 'other' 同业共现总次数。国有大型商业银行是体量最大、系统重要性最高、媒体曝光最密集的一类, 因此在同业共现网络里常处于高中心度位置, 多数目标银行的 soe 份额分量不为零; soe 份额高的目标银行在下游 Bartik 工具里承接"国有大行群体年度情感冲击"的更大权重, 这一群体的年度情感波动往往带有宏观与政策色彩, 是该工具外生冲击叙事的重要来源。本列区别于家族其余四列的唯一维度是类型分组标签 g='soe', 计算链路、基期年 T0=max(panel.year.min,2010) 及其 post-treatment 外生性守卫、去 'other' 分母、基期无文章整行 NaN、未映射银行 NaN、有分母而该组零次取真零 0 等口径, 与其余分量完全对齐; 六分量共享同一批基期共现文章与同一分母, 在有效样本上求和为 1, 是同一暴露向量的互补切片而非独立构念。份额为 track-agnostic 横截面元数据, 不做三轨 (full/ctx/ss)、模型、阈值、权重、滞后区分 (差异全部下沉到相乘的 shift 与 bartik_type_iv_{full,ctx,ss} 工具列); soe 份额与银行规模维度、金融科技类型维度的对应份额各自 just-identified 并排、互为稳健性不分主次, 禁混同一 over-identified Hansen J。

<!-- rendered-citations:begin -->
Borusyak, K., Hull, P., & Jaravel, X. (2025). A practical guide to shift-share instruments. Journal of Economic Perspectives, 39(1), 181-204. https://doi.org/10.1257/jep.20231370
Hahn, J., Kuersteiner, G., Santos, A., & Willigrod, W. (2024). Overidentification in shift-share designs. arXiv [Preprint]. https://doi.org/10.48550/arXiv.2404.17049
Apfel, N. (2024). Relaxing the exclusion restriction in shift-share instrumental variable estimation. Journal of the Royal Statistical Society Series A: Statistics in Society, 187(3), 748-771. https://doi.org/10.1093/jrsssa/qnad148
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Burgess, R., & Pande, R. (2005). Do rural banks matter? Evidence from the Indian social banking experiment. American Economic Review, 95(3), 780-795. https://doi.org/10.1257/0002828054201242
Goldstein, I., Kopytov, A., Shen, L., & Xiang, H. (2024). Bank heterogeneity and financial stability. Journal of Financial Economics. https://doi.org/10.1016/j.jfineco.2024.103934
Yuan, X., Puah, C.-H., & Marikan, D. A. binti A. (2025). An Empirical Study on the Impact of Financial Technology on the Profitability of China's Listed Commercial Banks. Journal of Risk and Financial Management. https://doi.org/10.3390/jrfm18080440
Xiao, T., & Wang, Y. (2025). Empirical analysis of the impact of financial technology on the profitability of listed banks. International Review of Economics & Finance. https://doi.org/10.1016/j.iref.2024.103788
<!-- rendered-citations:end -->
