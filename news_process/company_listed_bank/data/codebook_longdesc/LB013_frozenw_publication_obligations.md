---
family_id: LB013
novelty_exempt_rationale: "该家族是frozenw 发表义务与使用规范披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- base_year_full
- base_year_ctx
- base_year_ss
- frozenw_publication_obligations_conceptual
unit: base_year 列为年份整数(float64 存储, NaN=该轨窗内无共现); 义务说明列无独立数值量纲
formula: "base_year(company,track) = 面板窗内该(公司,轨)首个 n_docs>0 的年份(canonical 不门控计数); 基期份额冻结后逐年乘以当年银行侧测度, 引擎逐年限非缺失重归一"
producer: company_listed_bank/pipeline/04_build_altagg_panels.py (frozenw 分支)
upstream:
- _company_bank_cooc_pairs.parquet (基期年份判定与基期份额来源)
- news_process 40_panel_yearly.parquet (逐年银行侧测度取值来源)
citations:
- doi: 10.1093/qje/qjz025
  type: journal
  authors: Adão, R., Kolesár, M., & Morales, E.
  year: 2019
  title: "Shift-share designs: Theory and inference"
  venue: The Quarterly Journal of Economics
  vol: 134
  issue: 4
  pages_or_artno: 1949-2010
- doi: 10.1257/aer.20181047
  type: journal
  authors: Goldsmith-Pinkham, P., Sorkin, I., & Swift, H.
  year: 2020
  title: "Bartik instruments: What, when, why, and how"
  venue: American Economic Review
  vol: 110
  issue: 8
  pages_or_artno: 2586-2624
- doi: 10.1093/restud/rdab030
  type: journal
  authors: Borusyak, K., Hull, P., & Jaravel, X.
  year: 2022
  title: "Quasi-experimental shift-share research designs"
  venue: The Review of Economic Studies
  vol: 89
  issue: 1
  pages_or_artno: 181-213
- doi: 10.3982/ECTA19367
  type: journal
  authors: Borusyak, K., & Hull, P.
  year: 2023
  title: "Nonrandom exposure to exogenous shocks"
  venue: Econometrica
  vol: 91
  issue: 6
  pages_or_artno: 2155-2185
---

## CORE

本家族覆盖 frozenw 基期冻结替代聚合面板的发表义务与基期年份诊断列, frozenw 与主面板加权测度以及 mainbankw 面板并排构成十种聚合臂之一, 其核心构造思路是把每个公司与银行体系的共现份额结构固定在其在样本窗内首次出现共现的那一年, 此后各年份的加权测度均以这一冻结份额为权重, 只允许被加权的银行侧测度本身随年份变化, 这一构造在方法论谱系上直接对应初始份额工具变量的构造传统。

frozenw 的核心风险在于份额本身可能内生于结果变量, 这正是份额乘冲击类识别设计文献长期关注的核心问题, 相关文献系统论证了此类设计下常规聚类标准误往往过窄, 须采用针对暴露结构稳健的标准误估计方法; 基期份额的选择本身也是研究者的一项识别假设, 而非客观给定的事实, 使用初始入样年份作为基期是本项目的具体选择, 但由于 pair 长表完整保留, 使用者可以零成本重新定义基期年份并重新计算冻结权重, 不必依赖面板重新生产。识别假设的核心陈述是基期份额对企业结果的影响仅通过银行侧冲击这一条通道传导, 这一假设的合理性随基期设定的时点特征而变化: 基期年份本身可能与企业首次进入媒体视野的时点相关, 而非独立于结果变量的外生事实, 越晚的基期与当期实际权重会越收敛, 意味着基期选择的去内生化力度存在异质性衰减。此外, frozenw 面板与主面板的非缺失格点集合并不互相包含, 左截断、当期零共现年仍可能有值的解耦设计、以及银行退出面板带来的第三类缺失通道三重因素共同导致两臂的样本覆盖并不一致, 任何跨臂系数比较都应先取两臂共同的非缺失样本集合再展开估计, 不应在各自全样本上直接比较回归系数, 这一共同样本对齐原则是保证跨臂比较有效性的前提条件。

frozenw 面板发表时须履行的义务清单还包括对基期分布本身的描述性披露。由于基期年份逐(公司,轨)取值, 不同公司进入样本的基期年份并不整齐划一, 早年进入媒体视野的公司与近年才首次被观测到共现的公司在基期分布上呈现出明显的时间错位, 这种错位本身构成了一种事实上的交叉分组设计, 与近年份额乘冲击文献中反复讨论的"不同暴露起点的处理组异质性"问题高度类似, 发表时应至少报告基期年份的分布直方图或分位数摘要, 使读者能够判断基期错位的严重程度是否可能通过双向固定效应模型中已知的负权重问题影响估计结果的可信度。另一项义务性披露涉及冻结份额本身的时间稳定性检验: 研究者可以将基期份额与样本期内后续年份的实际观测份额做相关性比较, 若二者高度接近, 说明冻结假设对样本内绝大多数格点而言只是对已经相对稳定的关系结构做形式化处理, 冻结带来的信息损失有限; 若二者出现系统性偏离, 则说明企业与银行体系的共现份额结构本身存在显著的时间演化, 冻结处理可能掩盖了真实存在的动态关系变化, 这类相关性诊断结果建议作为附录表格随论文一并发表, 以便审稿人与后续研究者独立评估冻结假设的经验合理性, 而非仅凭方法论描述做出主观判断。

<!-- rendered-citations:begin -->
Adão, R., Kolesár, M., & Morales, E. (2019). Shift-share designs: Theory and inference. The Quarterly Journal of Economics, 134(4), 1949-2010. https://doi.org/10.1093/qje/qjz025
Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments: What, when, why, and how. American Economic Review, 110(8), 2586-2624. https://doi.org/10.1257/aer.20181047
Borusyak, K., Hull, P., & Jaravel, X. (2022). Quasi-experimental shift-share research designs. The Review of Economic Studies, 89(1), 181-213. https://doi.org/10.1093/restud/rdab030
Borusyak, K., & Hull, P. (2023). Nonrandom exposure to exogenous shocks. Econometrica, 91(6), 2155-2185. https://doi.org/10.3982/ECTA19367
<!-- rendered-citations:end -->
