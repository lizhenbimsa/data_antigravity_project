---
family_id: TB017
novelty_exempt_rationale: "该家族是merge 键与满骨架截断使用规范披露, 属构念定义/构造披露型条目而非独立新测度构念, 其学术依据以字符串匹配、记录关联、网络测度与银企关系等领域的奠基性方法论经典为构念锚, 该类经典按定义不可能落在近三年窗口内; 时效性文献已按构念契合原则在正文按需引入, 不以凑新颖度比例为目的机械追加, 故按主项目既有先例(构念定义型家族豁免)声明整族豁免新颖度占比闸。"
columns:
- usci
- year
- full_skeleton_truncation
unit: 无量纲 (merge/截断使用规范说明段, 非独立数值列)
formula: "merge 键=usci×year (18位统一社会信用代码, 首选键) 或 company_tax_name×year (等价备用键); 满骨架不裁行 (保留fillna(0)真零语义), L2口径下按外部工商注册年裁剪 keep if year<=当前年 & year>=reg_year"
producer: company_tax_bank/pipeline/panel/stata_export.py (merge示例与截断规范生成分支) + company_tax_bank_cooc_panel_codebook.md §⑥ (权威源)
upstream:
- company_tax_bank_cooc_panel.dta (usci主键来源, merge目标面板)
- config/company_tax_names.yaml (usci与外部工商注册年关联所需字段来源)
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
- doi: 10.1086/296668
  type: journal
  authors: Berger, A. N., & Udell, G. F.
  year: 1995
  title: "Relationship lending and lines of credit in small firm finance"
  venue: The Journal of Business
  vol: 68
  issue: 3
  pages_or_artno: 351-381
- doi: 10.1016/j.jfi.2021.100923
  type: journal
  authors: Banerjee, R. N., Gambacorta, L., & Sette, E.
  year: 2021
  title: "The real effects of relationship lending"
  venue: Journal of Financial Intermediation
  vol: 48
  issue: ""
  pages_or_artno: "100923"
- doi: 10.1257/jel.20201599
  type: journal
  authors: Abramitzky, R., Boustan, L., Eriksson, K., Feigenbaum, J., & Pérez, S.
  year: 2021
  title: "Automated linking of historical data"
  venue: Journal of Economic Literature
  vol: 59
  issue: 3
  pages_or_artno: 865-918
---

## VAR

税调企业银企共现面板与外部数据表进行合并时, 首选键是统一社会信用代码乘年份的组合, 统一社会信用代码是十八位定长编码, 在全部税调企业记录中做到全部填充且相互唯一, 这使其成为比企业全称更稳健的合并锚点, 因为企业名称在不同数据源中可能存在简繁体、括注信息或历史更名等书写差异, 而统一社会信用代码作为标准化行政编码不受此类书写差异干扰, 企业全称乘年份的组合仅作为等价备用键存在, 供统一社会信用代码字段在外部数据源中缺失时的应急替代方案。这种以标准化行政编码而非自由文本名称作为主合并键的设计选择, 其方法论根据可追溯到关联档案分析文献对跨源数据合并质量的系统论述, 该文献明确指出合并键的选择直接决定了后续关联结果中虚假匹配与遗漏匹配两类错误的相对比例, 标准化编码键相较自由文本键能够显著压低虚假匹配率。

面板本体在导出与分发环节坚持满骨架不裁行的原则, 即便绝大多数企业年观测在没有共现记录的情形下呈现为全零行, 这些全零行依然被完整保留在面板中, 这一设计的直接理由是裁行操作会破坏计数类列填零处理所承载的真零语义, 一旦裁去零值行, 后续任何人只依据面板本身已无法判断某一企业年组合究竟是本来就不存在还是被主动移除, 这与关系借贷背景下强调样本窗口构造透明度的经典研究立场一致, 也与探讨银行关系借贷真实经济效应研究中对样本选择偏误保持警觉的方法论态度相呼应。企业样本裁剪的责任因而完全下放给分析端: 由于税调企业名单本身是特定批次的时点快照, 不逐年反映企业的真实存续状态, 面板对名单覆盖窗口之外的年份同样机械铺零, 使用者若需要更贴近企业真实生命周期的样本, 应当以外部工商注册年份数据为准, 按照企业注册年份对样本做显式裁剪, 剔除企业尚未注册年份产生的机械性真零观测, 而不能想当然地假设面板内呈现的全部年份都对应企业真实存在的经营区间。

统一社会信用代码乘年份这一合并键在实际的 merge 操作中还有一个容易被忽视的技术细节值得提前声明: 由于该代码是定长十八位字符串, 若外部数据源在存储或导出过程中因软件差异被错误地转换为数值型或截断了前导字符, 合并时会出现大量本应成功匹配却因类型或格式不一致而失败的情形, 这类失败在 Stata 的 merge 命令输出中通常表现为异常偏高的仅主文件匹配或仅使用文件匹配计数, 使用者在执行合并前应显式核验两侧数据表中该字段的存储类型与字符长度完全一致, 这一核验步骤看似琐碎, 但关联档案分析文献明确指出, 跨源数据合并中由格式不一致引入的虚假不匹配是实证研究中一类高发且极易被忽视的数据质量问题, 其后果与关系借贷经典研究中反复强调的样本选择偏误问题同样不可轻视, 因为格式导致的合并失败往往并非随机分布, 而是系统性地集中在特定数据源或特定时期的记录上, 若不加核验直接沿用合并后的子样本展开分析, 极可能在不知不觉中引入选择性偏误。

以标准化标识符优先于名称字符串作为合并键的设计, 在经济学顶级综述文献中同样是明确建议: Abramitzky、Boustan、Eriksson、Feigenbaum 与 Pérez 于 2021 年对自动化数据关联方法的综述指出, 关联键的类型是关联误差结构的第一决定因素, 基于唯一标识符的关联在虚假匹配率上系统性优于基于姓名等自由文本的关联, 后者只应作为标识符缺失时的退路, 这正对应本面板以统一社会信用代码乘年份为首选键、企业全称乘年份仅作等价备用键的键序设计。

<!-- rendered-citations:begin -->
Kamat, G., & Gutman, R. (2026). Analysis of linked files: A missing data perspective. Statistical Science, 41(1). https://doi.org/10.1214/24-STS939
Berger, A. N., & Udell, G. F. (1995). Relationship lending and lines of credit in small firm finance. The Journal of Business, 68(3), 351-381. https://doi.org/10.1086/296668
Banerjee, R. N., Gambacorta, L., & Sette, E. (2021). The real effects of relationship lending. Journal of Financial Intermediation, 48, 100923. https://doi.org/10.1016/j.jfi.2021.100923
Abramitzky, R., Boustan, L., Eriksson, K., Feigenbaum, J., & Pérez, S. (2021). Automated linking of historical data. Journal of Economic Literature, 59(3), 865-918. https://doi.org/10.1257/jel.20201599
<!-- rendered-citations:end -->
