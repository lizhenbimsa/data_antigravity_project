---
family_id: LB015
columns:
- main_bank_share_full
- main_bank_share_ctx
- main_bank_share_ss
- main_bank_tie_full
- main_bank_tie_ctx
- main_bank_tie_ss
unit: main_bank_share 为比例, 取值范围(0,1]; main_bank_tie 为0/1旗标; 逐轨三份对应三种文本处理口径
formula: "main_bank(company,year,track) = 当年 n_docs 的 argmax 银行(与主 cw 权重同时点); 三级确定性平票规则 = n_docs → n_docs_longhit → 银行名规范码点升序; main_bank_share = 该主办行 n_docs 占该(公司,年,轨)总 n_docs 之比; main_bank_tie = 是否触发平票判定(0/1)"
producer: company_listed_bank/pipeline/04_build_altagg_panels.py (mainbankw 分支)
upstream:
- _company_bank_cooc_pairs.parquet (主办行 argmax 判定来源)
- news_process 40_panel_yearly.parquet (主办行测度取值来源)
citations:
- doi: 10.1111/j.1540-6261.1994.tb04418.x
  type: journal
  authors: Petersen, M. A., & Rajan, R. G.
  year: 1994
  title: "The benefits of lending relationships: Evidence from small business data"
  venue: The Journal of Finance
  vol: 49
  issue: 1
  pages_or_artno: 3-37
- doi: 10.1086/228631
  type: journal
  authors: Bonacich, P.
  year: 1987
  title: "Power and centrality: A family of measures"
  venue: American Journal of Sociology
  vol: 92
  issue: 5
  pages_or_artno: 1170-1182
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
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

本家族覆盖 mainbankw 主办银行替代聚合面板的诊断列与缺失语义, 这两组诊断列是判读 top-1 主办行聚合结果可靠性的必要配套信息, 不可脱离主办行测度本身单独解读。mainbankw 的构造思路是把每个公司在每一年的银行关系简化为当年共现计数最高的单一主办行, 这一简化对应了公司金融文献中长期存在的主银行制概念, 即企业与某一家银行建立起相对于其他银行更为紧密和优先的关系, 该银行在信息生产与危机应对中承担相对特殊的角色。

主办行认定采用三级确定性平票规则, 优先按共现计数取最大值, 若出现并列则依次退让到长变体命中计数、最终依名称规范码点升序作为确定性兜底, 这一多级退让设计的目的是保证同一批数据在任意环境下重复运行都能得到完全一致的主办行判定, 避免依赖不确定的排序稳定性。main_bank_share 与 main_bank_tie 两组诊断列正是为使用者揭示这一简化过程可能带来的信息损失: 份额越接近于一, 说明该公司当年的共现高度集中在单一银行, top-1 简化对信息损失很小; 份额越低, 说明当年共现在多家银行间较为均衡分布, 此时把关系强度简化为单一主办行会丢失相当比例的真实关系结构信息, 建议使用者对低份额格点做降权判读或结合 cw 加权臂并排解释。tie 旗标标记的是触发过平票退让规则的格点, 这类格点的主办行认定对单篇报道的计数噪声更为敏感, 单篇误配即可能翻转主办行判定, 这一击穿点极低的特征是 top-1 聚合方式固有的构念代价, 而非实现缺陷, 与关系强度测度文献中强调的测量误差敏感性问题相呼应, 也与链接数据分析中对稀疏关系判定不确定性的一般性讨论一致, 提醒使用者在使用主办行相关结论时应将 tie 与低份额两类诊断信息同时纳入稳健性判读流程。

主银行制这一构念在跨国比较公司金融文献中一直存在制度背景差异的争议, 一些银行主导型金融体系下的主银行关系具有相对稳定的长期契约特征, 而在以市场为主导的金融体系中, 企业与单一银行的紧密绑定关系相对松散, 主办行随年份切换的频率更高。本项目样本处于转轨经济体的银行体系背景下, 使用者在解读跨年度主办行切换现象时, 应意识到切换既可能反映真实的银企关系结构性调整, 也可能仅仅是本项目基于当年媒体共现计数做出的 top-1 判定在计数噪声下的技术性翻转, 而非企业与银行关系实质发生变化, 三级平票规则与 tie 旗标正是为了帮助使用者甄别后一种情形。mainbankw 与 frozenw 两支聚合臂虽然都属于把复杂的银企关系结构压缩为某种简化表征的聚合逻辑, 但二者压缩的维度截然不同: frozenw 保留了全部银行关系但把份额结构冻结在时间维度上, mainbankw 则保留了当期的份额结构但把银行关系压缩到单一实体维度上, 二者是正交的简化策略而非同一简化逻辑的不同版本, 严禁将二者交叉组合成冻结基期下的主办行判定, 这类交叉组合会引入难以单独解释的复合识别假设, 相关禁止性说明详见替代聚合面板刻意不做清单中的对应条目。使用者若同时报告 mainbankw 与 cw 加权臂的回归结果作为互为稳健性证据时, 应在文本中明确说明二者各自对应的识别假设差异, 而非笼统地将二者并列为"稳健性检验通过"。

<!-- rendered-citations:begin -->
Petersen, M. A., & Rajan, R. G. (1994). The benefits of lending relationships: Evidence from small business data. The Journal of Finance, 49(1), 3-37. https://doi.org/10.1111/j.1540-6261.1994.tb04418.x
Bonacich, P. (1987). Power and centrality: A family of measures. American Journal of Sociology, 92(5), 1170-1182. https://doi.org/10.1086/228631
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
<!-- rendered-citations:end -->
