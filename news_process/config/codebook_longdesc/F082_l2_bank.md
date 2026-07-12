---
family_id: F082
columns:
- bank_city
- bank_province
unit: 文本类别标识 (省级/城市级行政区名称字符串, 无量纲)
formula: "bank_province = prov_map[target_bank] (未匹配→''); bank_city = city_map[target_bank] (未匹配→''); prov_map/city_map 取自 config/bank_addresses.json (以银行名为键、省与市为子字段的地址映射)"
producer: news_process/pipeline/panel/geography.py::merge_bank_geography (步骤 7c)
upstream:
- 40_panel_yearly.parquet (target_bank 键列)
- config/bank_addresses.json (银行总行注册地字典)
citations:
- doi: 10.1016/j.eap.2025.08.020
  type: journal
  authors: Wang, S., Zeng, S., & Xie, W.
  year: 2025
  title: "City commercial banks' expansion and firm innovation: Evidence from China"
  venue: Economic Analysis and Policy
  vol: 87
  pages_or_artno: 2658-2673
- doi: 10.1016/j.ememar.2022.100969
  type: journal
  authors: Wang, C., Dong, Y., & Ge, R.
  year: 2023
  title: "Bank branching deregulation and the credit risk of the regional banking sector: Evidence from city commercial banks in China"
  venue: Emerging Markets Review
  vol: 55
  pages_or_artno: 100969
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: "Language and domain specificity: A Chinese financial sentiment dictionary"
  venue: Review of Finance
  vol: 26
  issue: 3
  pages_or_artno: 673-719
- doi: 10.1016/j.jce.2019.09.005
  type: journal
  authors: Chen, Z., Poncet, S., & Xiong, R.
  year: 2020
  title: "Local financial development and constraints on domestic private-firm exports: Evidence from city commercial banks in China"
  venue: Journal of Comparative Economics
  vol: 48
  issue: 1
  pages_or_artno: 56-75
- doi: 10.1111/j.1540-6261.2012.01725.x
  type: journal
  authors: Gurun, U. G., & Butler, A. W.
  year: 2012
  title: "Don't believe the hype: Local media slant, local advertising, and firm value"
  venue: The Journal of Finance
  vol: 67
  issue: 2
  pages_or_artno: 561-598
new_dois: []
---

## CORE

【构念与来源】
本家族的两列 bank_province 与 bank_city 是银行总行注册所在地的省级行政区名称与城市名称, 属文本类别标识 (string), 而非任何情感、网络或嵌入得分。二者由 pipeline/panel/geography.py 的步骤 7c 函数 merge_bank_geography 生成: 以 Bank-Year 面板的 target_bank 列为主键, 从 config/bank_addresses.json (结构为 {银行名: {province, city, district, address}}) 抽取每家银行总行的注册省份与城市, 通过 pandas 的 .map() 逐行映射写入面板。未能在地址字典中命中的银行填入空字符串 ''(非 NaN), 这是刻意选择的缺失哨兵——在 Stata 中字符串空值即被视为缺失, 参与 vce(cluster) 时会把这些观测从估计样本中剔除。需强调: 本家族列不是"得分/指标", frontmatter 中残留的 network_spillover.py / strategic_diff.py 生产函数系机械 grep 的误判, 真实且唯一的生产入口是 geography.py 步骤 7c, 对应源码校对后已在本文件更正。

【方法学与计算】
计算链路极简且无浮点运算: prov_map 与 city_map 是两个从 bank_addresses.json 一次性构建的银行到省/市的确定性字典, 面板列即 target_bank 在字典上的查表结果, .fillna('') 兜底未匹配项。地址字典覆盖 1768 条记录 (含"中国人民银行"), 涵盖 31 个省级行政区与 329 个城市; bank_names.json 中的 1767 家银行全部包含在地址字典内, 多出的 1 条"中国人民银行"不在面板 target_bank 集合中, 因此在满语料下匹配率应为 100%。当 bank_addresses.json 缺失时, 函数仍生成两列并整列填 '' , 保证下游步骤不因列缺失而崩溃。这两列本身不进入任何回归右手侧, 其价值在于为下游提供两类基础设施: 其一是地理层级递进的聚类标准误锚点, 其二是留一法 (leave-one-out) 地理工具变量的前置分组键 (步骤 7d 依赖本列计算"同省/同城市其他银行的平均情感")。

聚类层级的方法学依据是 Cameron 与 Miller (2015) 关于聚类稳健推断的实务指南: 当扰动项在地理维度存在空间自相关时——例如同省银行共同暴露于相似的地方政策与媒体生态——仅在银行级聚类会低估标准误、使 t 统计量虚高。据此面板支持从银行级 (N≈1768) 递进到城市级 (329 个聚类) 再到省级 (31 个聚类) 的稳健性阶梯。其中 31 个省级聚类低于经验门槛 50, 渐近正态近似不再可靠, 因此省级聚类回归须在 Stata 中补充 wild cluster bootstrap (boottest) 加以确认; 城市级 329 个聚类超过门槛, 常规聚类推断可用。函数运行时输出省份/城市聚类数与 Top-5 分布诊断, 并在存在未匹配银行时打印样本一致性告警——因为空字符串观测被 vce(cluster) 剔除会使省/市级聚类样本相对银行级静默缩小, 构成跨聚类层级比较时的样本不一致隐患。

【文献定位】
地理注册地作为媒体—银行关系的分组维度, 其构念动机根植于 Gurun 与 Butler (2012) 在顶级金融学期刊的发现: 本地媒体对本地企业的报道存在系统性正向倾斜 (local media slant), 且该倾斜与本地广告投放及企业价值相关。这为"同省/同城市银行共享相似媒体报道环境"提供了直接理论支撑, 也是本家族列作为地理聚类与地理留一法工具变量分组键的合法性来源。在中国城商行制度语境下, 银行注册地的经济学意涵尤为丰富: Chen、Poncet 与 Xiong (2020) 论证城市商业银行的地方性金融发展显著影响本地私营企业的出口约束; Wang、Dong 与 Ge (2023) 从分支机构管制放松角度刻画区域银行业信用风险; Wang、Zeng 与 Xie (2025) 进一步将城商行扩张与本地企业创新相联系——三者共同表明"银行总行所在城市/省份"并非中性标签, 而是承载了地方金融供给、监管边界与经济生态的结构性信息。此外, 本项目的中文金融情感测度以 Du、Huang、Wermers 与 Wu (2022) 的领域专用词典为基, 该文强调语言与领域特异性; 地理列在此语境下服务于把情感测度按地方媒体生态分层检验的稳健性目标。综上, bank_province 与 bank_city 是纯标识性列, 但其下游计量用途 (聚类层级、留一法地理 IV) 使其成为识别策略中的基础设施性变量。

## VAR: bank_province

【变体差分】
本列是家族中的省级 (省/自治区/直辖市) 粒度标识, 取值为总行注册省份的中文名称字符串, 直辖市 (如"北京""上海""天津""重庆") 单独作为一级取值列出而非归入某省。与同家族的 bank_city 相比, 唯一差分维度是行政区聚合粒度: 本列为较粗的省级层级, 满语料下约 31 个不同取值 (省级聚类数)。因聚类数 31 低于 Cameron 与 Miller (2015) 提出的经验门槛 50, 使用 vce(cluster bank_province) 时渐近正态近似不可靠, 标准聚类标准误可能偏小, 因而以本列作为聚类层级的回归须补充 wild cluster bootstrap (Stata boottest) 才能得到可信推断; 本列亦可用于 absorb(bank_province) 以在替换银行固定效应时吸收省级异质性。取值来源与生成逻辑与家族 canonical 完全一致 (target_bank 在 bank_addresses.json 的 province 字段上查表, 未匹配填 '')。空字符串观测在 vce(cluster) 下被视为字符串缺失并从估计样本剔除, 故当匹配率不足 100% 时, 省级聚类回归样本会相对银行级聚类静默缩小, 跨层级比较前须核对样本一致性。作为下游步骤 7d 留一法地理工具变量的分组键, 本列定义"同省其他银行"集合, 用于构造省级 leave-one-out 平均情感 (变量名前缀 prov_, 见 _GEO_SHORT 映射); 该分组比城市级更粗, 组内银行更多, 留一法均值的估计更稳但地理精度更低——省级与城市级两条地理工具变量互为稳健性、不分主次, 各自在其分组粒度上 just-identified, 禁混入同一 over-identified Hansen J 过度识别检验。

## VAR: bank_city

【变体差分】
本列是家族中的城市级粒度标识, 取值为总行注册城市的中文名称字符串, 满语料下约 329 个不同取值 (城市级聚类数)。与 bank_province 的唯一差分维度同样是行政区聚合粒度: 本列为较细的城市层级, 聚类数 329 远超 Cameron 与 Miller (2015) 的门槛 50, 因此使用 vce(cluster bank_city) 时常规聚类稳健标准误的渐近推断可靠, 无须额外的 wild cluster bootstrap 补强——这是本列相对省级列在推断实务上的关键差异。取值来源与生成逻辑与家族 canonical 完全一致 (target_bank 在 bank_addresses.json 的 city 字段上查表, 未匹配填 '' 空字符串哨兵), 空值观测在 Stata vce(cluster) 下被剔除, 故匹配率不足时城市级聚类样本亦会静默缩小。作为下游步骤 7d 留一法地理工具变量的分组键, 本列定义"同城市其他银行"集合, 用于构造城市级 leave-one-out 平均情感 (变量名前缀 city_, 见 _GEO_SHORT 映射, 缩写为 city 以规避变量名超 32 字符截断); 该分组比省级更细, 组内银行更少, 因而某城市某年仅 1 家银行有情感数据时其留一法值为 NaN——这是方法论上正确的处理 (无法从自身推断同地区媒体生态)。城市级与省级两条地理工具变量互为稳健性、不分主次, 各自在其粒度上 just-identified, 禁混入同一 over-identified Hansen J; 在识别策略上, 城市级提供更高地理分辨率的媒体生态外生冲击, 省级提供更保守的空间自相关校正, 二者并排检验主结论对地理聚合粒度的稳健性。

<!-- rendered-citations:begin -->
Wang, S., Zeng, S., & Xie, W. (2025). City commercial banks' expansion and firm innovation: Evidence from China. Economic Analysis and Policy, 87, 2658-2673. https://doi.org/10.1016/j.eap.2025.08.020
Wang, C., Dong, Y., & Ge, R. (2023). Bank branching deregulation and the credit risk of the regional banking sector: Evidence from city commercial banks in China. Emerging Markets Review, 55, 100969. https://doi.org/10.1016/j.ememar.2022.100969
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Chen, Z., Poncet, S., & Xiong, R. (2020). Local financial development and constraints on domestic private-firm exports: Evidence from city commercial banks in China. Journal of Comparative Economics, 48(1), 56-75. https://doi.org/10.1016/j.jce.2019.09.005
Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype: Local media slant, local advertising, and firm value. The Journal of Finance, 67(2), 561-598. https://doi.org/10.1111/j.1540-6261.2012.01725.x
<!-- rendered-citations:end -->
