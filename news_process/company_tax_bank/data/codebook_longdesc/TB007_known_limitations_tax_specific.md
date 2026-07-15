---
family_id: TB007
novelty_exempt_rationale: "该家族是税调特有已知局限的诚实披露条目, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- n_docs_longhit
- company_tax_name
- county_key_ok
- is_bank_company
unit: 无量纲 (局限披露段, 非独立数值列)
formula: "L1短简称假阳性 / L2名单时点性 / L3县权结构性缺失 / L4县改区错位 / L5分支权构念差异 / L6银行系企业 / L7own-bank子串映射残余, 七条并列局限, 不裁剪只披露"
producer: company_tax_bank/pipeline/02_build_cooc_panel.py + 03_build_altweight_panels.py (§7 已知局限段生成分支, 税调特有部分)
upstream:
- config/company_tax_names.yaml (44,771家企业名单, L1/L2/L6/L7 局限来源)
- _company_tax_bank_altweights_branch_county.parquet (L3/L4 县权局限来源)
citations:
- doi: 10.1214/24-STS939
  type: journal
  authors: Kamat, G., & Gutman, R.
  year: 2026
  title: "Analysis of linked files: A missing data perspective"
  venue: Statistical Science
  vol: 41
  issue: 1
  pages_or_artno: ""
- doi: 10.1111/j.1540-6261.1994.tb04418.x
  type: journal
  authors: Petersen, M. A., & Rajan, R. G.
  year: 1994
  title: "The benefits of lending relationships: Evidence from small business data"
  venue: The Journal of Finance
  vol: 49
  issue: 1
  pages_or_artno: 3-37
- doi: 10.1145/360825.360855
  type: journal
  authors: Aho, A. V., & Corasick, M. J.
  year: 1975
  title: "Efficient string matching: An aid to bibliographic search"
  venue: Communications of the ACM
  vol: 18
  issue: 6
  pages_or_artno: 333-340
---

## VAR

税调企业银企共现面板体系存在七条税调数据特有的已知局限, 本项目一贯的处理哲学是全量披露而不做静默裁剪, 让每一位使用者都能在充分知情的前提下自行判断某条局限是否会实质影响其具体研究设计。第一条局限是短简称带来的假阳性风险: 四万四千余家企业名录本身密度极高, 不超过四字的短变体命中密度随之上升, 这一风险与文本字符串匹配算法本身的信噪比特性直接相关, 高效匹配算法能够穷尽命中所有模式串, 但无法区分命中是否具有实质语义关联, 该风险的应对工具是限定长变体命中的稳健臂列, 而非裁剪短变体本身。第二条局限涉及名单的时点性: 税调企业名单是特定批次的快照, 并不逐年反映企业的存续状态, 面板构造因而在缺乏该批次覆盖年份之外的年份铺零值, 这与关系借贷经典研究中强调样本窗口选择会系统影响关系强度测度可信度的方法论提醒是一致的, 使用者若需要更精确的存续窗口约束, 应结合外部工商注册年份数据自行裁剪样本。

第三与第四条局限均涉及县域网点权的构造缺口: 一部分企业因区县字段本身不可对齐或指向非民政建制区划, 导致县域层权重结构性缺失, 另有部分企业面临权源快照与税调批次两个时间点之间的行政区划变更错位问题, 这两类缺口共同指向一个更一般的方法论问题, 即行政区划关联数据在跨越不同来源与不同时点整合时天然存在缺失模式, 关联档案分析框架从缺失数据视角系统梳理了这一类问题, 提醒研究者区分真实缺失与结构性不可观测两种性质截然不同的缺失情形, 本项目正是沿着这一区分逻辑设计了缺键标识列, 以避免使用者把技术性缺键误判为经济意义上的真零。第五条局限是分支网点权本身的构念属性: 网点数量测度的是本地银行供给暴露而非企业与特定银行之间的直接关系强度, 这一构念差异并非数据质量瑕疵, 而是权重设计初衷本身的性质使然。第六与第七条局限共同指向银行系企业与own-bank剔除机制的残余风险: 银行系税调企业剔除自家银行共现后行仍保留在面板中, 但基于子串规则的own-bank识别在批次快照下仍可能存在识别残余, 后续名单扩充须重新审视这一识别规则, 现有的翻红检测机制为此兜底。

七条局限之间存在一定的相互作用而非彼此完全独立, 例如短简称假阳性风险与银行系企业own-bank识别残余风险在同一批次数据中可能同时命中同一家企业, 使得该企业观测点上的共现测度受到两重风险叠加的影响, 使用者若仅逐条孤立地评估每条局限对研究结论的潜在冲击, 容易低估多条局限同时作用下的复合风险敞口。银行系企业剔除机制的设计初衷是防止银行通过其关联企业间接对自身形成虚假共现暴露, 这一关切与关系借贷经典研究中强调借贷双方经济利益关联可能扭曲测度构念的方法论立场是同源的, 若不加剔除, 银行系企业与其控股银行之间近乎必然的高频共现会在样本中制造出与真实市场关系强度无关的机械性正相关, 污染后续基于共现测度展开的因果或相关性分析。翻红检测机制作为own-bank识别残余风险的兜底手段, 会在每次名单批次更新后重新扫描已识别的own-bank关系是否仍然成立, 但这一机制本身仍然依赖批次快照的时点性, 无法对批次之间发生的股权变更做到实时捕捉, 这也解释了为何第六与第七条局限须与第二条名单时点性局限联合理解而非孤立看待。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
<!-- rendered-citations:end -->
