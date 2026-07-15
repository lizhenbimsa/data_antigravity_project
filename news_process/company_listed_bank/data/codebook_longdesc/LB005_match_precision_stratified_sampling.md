---
family_id: LB005
columns:
- match_precision_le2char_stratum
- match_precision_3char_stratum
- match_precision_ge4char_stratum
- n_docs_longhit
unit: precision 为比例, 取值范围[0,1]; 分层样本量 n 为整数条数
formula: "分层依据 = variant 字符长度(≤2字/3字/≥4字) 交叉 k^c 命中密度双维度; 各层独立抽样后人工逐条判读真阳性/假阳性, precision = 真阳性条数/该层抽样条数"
producer: company_listed_bank/pipeline/03_verify/WP3_R3-2_stratified_sampling.py (人工审核方法论脚本, dev 一轮已跑, 生产机重跑后再一轮)
upstream:
- _company_bank_cooc_pairs.parquet (待抽样命中记录来源)
- company_listed_names.yaml (variant 主清单, 抽样分层依据字段来源)
citations:
- doi: 10.1145/360825.360855
  type: journal
  authors: Aho, A. V., & Corasick, M. J.
  year: 1975
  title: "Efficient string matching: An aid to bibliographic search"
  venue: Communications of the ACM
  vol: 18
  issue: 6
  pages_or_artno: 333-340
- doi: 10.2307/2529310
  type: journal
  authors: Landis, J. R., & Koch, G. G.
  year: 1977
  title: "The measurement of observer agreement for categorical data"
  venue: Biometrics
  vol: 33
  issue: 1
  pages_or_artno: 159-174
- doi: 10.1080/19312450709336664
  type: journal
  authors: Hayes, A. F., & Krippendorff, K.
  year: 2007
  title: "Answering the call for a standard reliability measure for coding data"
  venue: Communication Methods and Measures
  vol: 1
  issue: 1
  pages_or_artno: 77-89
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: "Analysis of linked files: A missing data perspective"
  venue: Statistical Science
  vol: 41
  issue: 1
  pages_or_artno: ""
---

## CORE

本家族覆盖上市公司名称自动机匹配的精度评估方法论, 是理解本项目全部共现计数列可信度的关键背景材料。匹配引擎采用多模式串精确匹配算法, 对三轨文本一次扫描即可命中全部公司名称及其曾用名变体, 该算法自提出以来即成为大规模文本实体匹配任务的标准工具, 其效率优势使得对千万级语料的全量扫描在可接受时间内完成, 但效率优势并不天然保证匹配精度, 短字符变体尤其容易与常见词语或其他实体名称发生字面重合。

为量化这一风险, 本项目按 variant 字符长度与命中密度两个维度做双重分层抽样, 对每一层独立抽取命中记录做人工逐条判读, 判定真阳性或假阳性, 这一分层抽样加人工核验的流程借鉴了内容分析与文本编码研究中评估自动化标注质量的标准做法, 即用可控规模的人工标注样本估计整体误差率而非要求全量人工复核。核验结果显示, 两字及以下的短变体精度显著低于四字及以上的长变体, 说明短名歧义是本项目实体匹配误差的主要来源, 而长变体命中在绝大多数情况下对应真实公司提及。这一发现的直接后果是, 使用者若对匹配精度有较高要求, 应优先使用 n_docs_longhit 这一仅计入四字及以上变体命中的稳健计数列, 而非包含全部长度变体的原始计数列。人工判读结果的可靠性本身也需要度量, 本项目对判读者间一致性的评估方式沿用了内容分析领域广泛使用的信度系数框架, 该框架相比简单一致百分比更能纠正偶然一致带来的高估。分层抽样评估目前完成一轮, 后续在生产语料上重跑将提供覆盖真实数据规模的第二轮核验结果。

分层维度的双重设计还需要进一步说明其识别逻辑。字符长度这一维度捕捉的是名称本身的信息密度: 越短的字符串在自然语言中出现字面偶合的先验概率越高, 这是字符串匹配任务的一般性规律, 与所采用的具体匹配算法无关。命中密度这一维度则捕捉的是另一种独立的误差来源, 即某一变体在语料中的绝对命中频次异常偏高时, 往往意味着该变体同时是某个常见词语或高频短语的子串, 而非仅由该公司的真实提及贡献, 这类高频异常变体即使字符较长也可能存在系统性误判, 因此两个维度交叉分层能够比单一维度分层更完整地覆盖误差模式的异质性来源。抽样方法论上, 每一层独立抽样保证了各层精度估计各自具有可解释的置信区间, 而不会因为把不同误差风险的记录混同抽样而稀释掉高风险层本应获得的核验强度, 这一分层抽样思路是调查抽样与内容分析方法论中控制估计方差的标准手段。人工判读环节中判读者对同一条记录独立作出判断, 再计算判读者间一致性, 这一流程设计的意义在于, 若一致性系数偏低, 说明真阳性与假阳性之间的边界本身在语义上较为模糊, 此时报告的精度点估计应附带更宽的不确定性说明, 而非当作确定无疑的真值直接采信; 若一致性系数处于公认的高一致区间, 则精度估计的可信度相应更高, 这一因果链条是本项目对匹配质量做出可信量化陈述的方法论基础。

<!-- rendered-citations:begin -->
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
<!-- rendered-citations:end -->
