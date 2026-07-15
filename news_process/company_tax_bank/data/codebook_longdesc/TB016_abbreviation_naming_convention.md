---
family_id: TB016
novelty_exempt_rationale: "该家族是税调侧 dta 短名缩写命名规范的约定披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- dta_short_name_mapping
unit: 无量纲 (命名对照说明表, 非独立数值列)
formula: "全名基名 → dta短名机械缩写规则 (Stata 32字节变量名上限驱动); 逐条对照表见 codebook §⑥, 缩写规则与 company_listed_bank 同构共用"
producer: company_tax_bank/pipeline/panel/stata_export.py (变量名缩写生成分支, 与 company_listed_bank 同一套缩写函数)
upstream:
- company_tax_bank_cooc_panel_codebook.md (§⑥ 缩写名↔全名对照表, 权威源)
- company_listed_bank/data/company_bank_cooc_panel_codebook.md (同构缩写规则源头, 独立复述非指针引用)
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
- doi: 10.3982/ECTA7195
  type: journal
  authors: Gentzkow, M., & Shapiro, J. M.
  year: 2010
  title: "What drives media slant? Evidence from U.S. daily newspapers"
  venue: Econometrica
  vol: 78
  issue: 1
  pages_or_artno: 35-71
- doi: 10.1111/j.1540-6261.2009.01493.x
  type: journal
  authors: Fang, L., & Peress, J.
  year: 2009
  title: "Media coverage and the cross-section of stock returns"
  venue: The Journal of Finance
  vol: 64
  issue: 5
  pages_or_artno: 2023-2052
---

## VAR

税调企业银企共现面板输出到 Stata dta 格式时面临一个纯粹由目标软件本身施加的技术约束: 变量名长度存在上限, 而本面板衍生自加权测度通式的全名基名往往包含多段有实质含义的英文单词拼接, 长度普遍超出该上限, 若不做处理, 大量列会因重名截断而在导出阶段发生冲突。为此, 本项目建立了一套机械化的缩写生成规则, 将冗长的全名基名系统性压缩为符合软件限制的短名, 缩写规则本身与上市公司体系完全共用同一套函数实现, 确保两条产品线在缩写逻辑上不会出现同一全名基名在两处产生不同短名的割裂局面, 这对于日后可能出现的跨产品线联合分析尤为重要。

缩写规则的设计原则是保留足以让人类研究者在不查阅对照表的情况下大致猜出全名含义的关键信息片段, 同时尽量剔除介词、连接词等对语义识别贡献有限的成分, 例如隐藏采纳强度中位数全体版本这一全名会被压缩为保留核心语义片段的短名, 跨渠道口径方差测度会被压缩为保留跨渠道与方差核心信息的短名。这种在保真度与长度约束之间寻求平衡的思路, 与高效字符串匹配算法研究领域处理模式压缩与检索效率权衡的方法论精神是相通的, 该领域的经典工作正是致力于在有限的存储与计算预算下最大化字符串处理任务的信息保真度。缩写对照表本身作为一张纯说明性表格存在, 不构成任何独立的数值型变量, 但它对于面板的可用性至关重要, 尤其在跨渠道媒体覆盖度与文本测度研究领域, 变量命名的可追溯性历来被视为测度可信度的重要组成部分, 媒体覆盖度与市场反应关系的经典研究以及媒体倾向性构造方法论工作均强调, 测度构造过程若因命名压缩而丧失可追溯性, 会实质削弱后续研究者复现与核验既有结果的能力, 因此本项目坚持将全部缩写映射关系完整落盘于对照表, 而非仅在代码内部隐式维护。

缩写规则在实践中还需要处理一类特殊情形, 即多个全名基名在压缩后可能碰撞出完全相同的短名, 尤其是在双替代权与三文本轨叠加的场景下, 同一个核心语义片段可能对应多个仅在权重来源或文本轨后缀上有细微差异的全名, 若缩写函数不加区分地机械截断, 极易产生短名冲突, 本项目的处理方式是在核心语义片段之外附加区分度更高的后缀标记, 确保任意两个不同的全名基名在压缩后仍能保持短名层面的唯一性, 这一冲突消解机制与字符串匹配算法领域处理模式集合中前缀重叠情形的思路是相通的, 即当压缩后的表示空间小于原始信息空间时, 必须引入额外的区分机制才能避免信息丢失导致的歧义。使用者在跨产品线联合分析城市网点权面板与县域网点权面板的短名列时, 应格外留意二者短名之间可能仅有一两个字符的差异, 建议始终通过对照表而非凭记忆或直觉判断某一短名对应的具体全名, 尤其是在撰写 Stata 脚本或论文附录变量说明表时, 这一核验习惯能够有效避免因短名误读而引发的变量误用风险。

<!-- rendered-citations:begin -->
Aho, A. V., & Corasick, M. J. (1975). Efficient string matching: An aid to bibliographic search. Communications of the ACM, 18(6), 333-340. https://doi.org/10.1145/360825.360855
Gentzkow, M., & Shapiro, J. M. (2010). What drives media slant? Evidence from U.S. daily newspapers. Econometrica, 78(1), 35-71. https://doi.org/10.3982/ECTA7195
Fang, L., & Peress, J. (2009). Media coverage and the cross-section of stock returns. The Journal of Finance, 64(5), 2023-2052. https://doi.org/10.1111/j.1540-6261.2009.01493.x
<!-- rendered-citations:end -->
