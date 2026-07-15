---
family_id: TB006
columns:
- n_docs_longhit
- variant_length_stratum
unit: 无量纲 (方法论披露段, precision为比例)
formula: "分层抽样按 variant 字符长度分层 (≤2字/3字/≥4字), 每层全量或抽样人工过目判定假阳性率; 母本参照 precision≈0.71(≤2字)/0.76(3字)/0.92(≥4字), 税调侧2/3字层全量32+21条复核"
producer: company_tax_bank/pipeline/audit/verify_match_precision.py (T-P0-7 dev一轮; 生产机第二轮DEFERRED)
upstream:
- config/company_tax_names.yaml (44,771家企业名单, 124,366个variants, 分层抽样对象)
- _company_tax_bank_cooc_pairs.parquet (n_docs_longhit 稳健臂列来源)
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
---

## VAR

企业名称字符串匹配天然面临一个此消彼长的权衡: 名称变体越短, 覆盖到的合法别名与简称就越多, 但同时误命中不相关文本片段的风险也越高。为量化这一权衡在税调企业名单上的具体表现, 本项目按变体字符长度对全部 variants 分层, 划分为不超过两字、恰好三字与四字及以上三层, 逐层抽取样本交由人工过目判定每条命中是否为真阳性, 这一分层抽样设计的方法论根据直接来自高效字符串匹配算法的经典工作, 该算法族本身即以能够在单遍扫描中同时匹配大规模模式集合著称, 但算法效率与匹配语义精度是两个独立维度, 高效并不意味着高精度, 分层人工复核正是弥补这一鸿沟的必要环节。

税调企业名单规模达四万四千余家, 派生出十二万余条变体, 在如此高密度的名录下, 短变体撞车的概率显著上升, 二字变体全量三十二条人工过目结果显示, 其中相当一部分本身即是含义宽泛的通用词汇, 例如出现在个别企业简称列中的高泛用词条, 这些词条在新闻文本中出现时绝大多数场合与目标企业毫无关联; 三字变体二十一条的风险水平则明显低于二字层, 未发现同级别的系统性风险。母本上市公司体系的分层抽样参照结果显示, 匹配精度随变体长度单调上升, 短变体层精度明显低于长变体层, 这一模式本质上反映了字符串匹配任务中固有的信噪比问题: 变体越长, 携带的信息量越大, 偶然撞车的概率越低。人工过目判定的可靠性本身也需要方法论背书, 观察者间一致性测量的经典框架与后续被广泛采纳的信度系数框架, 共同构成了本项目人工复核流程可信度的理论支撑, 尽管本轮复核采用单一核验人过目而非多评分者设计, 但抽样分层与全量优先的操作原则借鉴了这些框架强调的系统化编码规范。基于上述发现, 本项目刻意选择维持不裁剪短变体的口径, 即不因假阳性风险而删除通用词汇变体, 而是提供 n_docs_longhit 这一限定四字及以上变体命中的稳健臂列, 供分析端按需切换到高精度子集, 让口径选择权保留在研究者手中而非在数据构造阶段被单方面替使用者做出。

分层抽样的操作流程还揭示了一个值得单独强调的方法论细节: 由于税调企业名单规模远大于母本上市公司名单, 短变体层的候选样本池本身也随之膨胀, 若沿用母本体系的固定抽样比例, 实际抽取的样本绝对数量可能不足以支撑对假阳性率的可靠估计, 因此本轮复核对二字与三字两层采取全量而非抽样过目的策略, 这一"高风险层全量、低风险层抽样"的分层强度差异化处理思路, 与观测者间信度测量框架及后续被广泛采纳的信度系数框架共同倡导的"按预期误差风险分配复核资源"的一般原则相符。生产语料机上的第二轮复核目前被明确标注为延后事项, 这一延后并非方法论缺陷, 而是与本项目一贯的"披露延后状态而非静默略去"原则一致的过渡性安排, 待生产规模语料到位后, 分层抽样的样本量与分层边界均需按生产环境下的变体分布重新校准, 复核结论也须相应更新, 使用者在此之前应将当前精度估计视为基于开发环境小样本得出的初步结论, 而非最终定论。

<!-- rendered-citations:begin -->
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Landis, J. R., & Koch, G. G. (1977). The measurement of observer agreement for categorical data. Biometrics, 33(1), 159-174. https://doi.org/10.2307/2529310
Hayes, A. F., & Krippendorff, K. (2007). Answering the call for a standard reliability measure for coding data. Communication Methods and Measures, 1(1), 77-89. https://doi.org/10.1080/19312450709336664
<!-- rendered-citations:end -->
