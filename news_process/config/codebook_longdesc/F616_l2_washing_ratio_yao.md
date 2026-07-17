---
family_id: F616
columns:
- washing_ratio_yao_2021
- washing_ratio_yao_2021_ctx
- washing_ratio_yao_2021_ss
unit: 比率 (proportion, [0,1]; 分母为零时 NaN)
formula: 'washing_ratio_yao_2021{track} = yao_2021_pos_symb_count{track} / yao_2021_pos_substvalid_count{track} (分母缺失回退 yao_2021_pos_count{track} 并告警)'
producer: pipeline\panel\runner.py (步骤 7h, 洗稿率多方法×三轨构造) ; pipeline\panel\export.py (标签映射)
upstream:
- yao_2021_score_full/_ctx/_ss (pipeline\sentiment\tone_words.py, 姚加权等 2021 中文金融情绪词典打分)
- innovation_substantiveness_full (stage 21 LLM 实质性/象征性分类, W&Z 1998 typology)
citations:
- doi: 10.1093/rof/rfab036
  type: journal
  authors: Du, Z., Huang, A. G., Wermers, R., & Wu, W.
  year: 2022
  title: 'Language and domain specificity: A Chinese financial sentiment dictionary'
  venue: Review of Finance
  vol: '26'
  issue: '3'
  pages_or_artno: 673-719
- doi: 10.1111/eufm.12509
  type: journal
  authors: Gorovaia, N., & Makrominas, M.
  year: 2024
  title: Identifying greenwashing in corporate-social responsibility reports using natural-language processing
  venue: European Financial Management
  vol: '31'
  issue: '1'
  pages_or_artno: 427-462
- doi: 10.1016/j.pacfin.2024.102600
  type: journal
  authors: Fan, X., Tang, Z., Huang, W., & Yang, K.
  year: 2025
  title: "Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective"
  venue: Pacific-Basin Finance Journal
  vol: '89'
  pages_or_artno: Article 102600
- doi: 10.1086/693096
  type: journal
  authors: Piotroski, J. D., Wong, T. J., & Zhang, T.
  year: 2017
  title: Political bias in corporate news - The role of conglomeration reform in China
  venue: The Journal of Law and Economics
  vol: '60'
  issue: '1'
  pages_or_artno: 173-207
- doi: "10.1016/j.frl.2024.105265"
  type: "journal"
  authors: "Huang, J., & Ma, L."
  year: 2024
  title: "Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation"
  venue: "Finance Research Letters"
  vol: "63"
  pages_or_artno: "105265"
new_dois: []
---

## CORE

【构念与来源】
本家族刻画银行金融科技报道中"洗稿式漂洗"(washing)的强度: 一篇报道情感基调正面, 但其内容被 stage 21 LLM 判为"象征性"(symbolic, 空泛表态、无实质创新动作), 而非"实质性"(substantive, 有具体产品/合作/投入描述)。这一构念源自组织理论中的"象征性采纳 vs 实质性采纳"(symbolic vs substantive adoption) 区分传统(呼应 Westphal & Zajac 系列关于公司治理实践仪式化采纳的经典发现), 在文本分析语境下与 greenwashing 计量文献(Gorovaia & Makrominas 2024, European Financial Management; Fan et al. 2025, Pacific-Basin Finance Journal)一脉相承: 后者用自然语言处理从企业社会责任报告或披露文本中分离"言而不行"的漂洗式表述, 本家族将同一逻辑移植到银行-金融科技新闻报道场景, 检验媒体报道中银行科技形象是否存在系统性"言过其实"。washing_ratio_yao_2021 是洗稿率多方法族群中的方法 D2(单词典口径)分支, 使用姚加权等(2021)构造的中文金融领域情绪词典(annualReport 正面 3,592/负面 1,633 词 ∪ socialMedia 正面 912/负面 965 词, 去重后正面 3,844/负面 2,074 词; SSOT=`pipeline/sentiment/tone_words.py`)作为情感判定引擎, 是 DICT_NAMES 六部词典(jiang_2021/yao_2021/bian_2021/du_2022/you_2018/loughran)之一, 与同族的 du_2022(Du et al. 2022, Review of Finance)、jiang_2021、bian_2021、you_2018、loughran 各版本互为稳健性、不分主次, 各自 just-identified 并排, 严禁混进同一 over-identified Hansen J 设定。

【方法学与计算】
producer 为 `pipeline/panel/runner.py`: 篇章级(每条报道)标记阶段位于 970-1044 行(早于 2165 行处标签为"步骤 7h"的面板级聚合代码块), 先标记 `_is_yao_2021_pos_symb{track}` = (yao_2021_score{track} > 0) ∧ (innovation_substantiveness_full == '象征性'), 再标记 `_svd_yao_2021_pos{track}` = (yao_2021_score{track} > 0) ∧ (象征性/实质性已测量, 即 innovation_substantiveness_full 落在有效标签集合内); 该标记阶段与其下游"步骤 7h"面板级除法聚合前后衔接、共享同一构造逻辑, 但两者在代码位置上并非同一循环块。步骤 7h 聚合到银行-年面板得到 `yao_2021_pos_symb_count{track}`(分子: 姚词典判正面且象征性的报道数)与 `yao_2021_pos_substvalid_count{track}`(分母: 姚词典判正面且实质性/象征性已被 LLM 成功测量的报道数)。面板级最终列 `washing_ratio_yao_2021{track} = yao_2021_pos_symb_count{track} / yao_2021_pos_substvalid_count{track}`, 分母为 0 或缺失时经 `_safe_ratio` 返回 NaN(非 0, 避免虚假精确)。分母采用"同域化"口径(fix omni-g-runner-10/14, 2026-06-11 修订): 早期实现分母误用全体词典正面报道数, 但分子隐式要求实质性标签已测量, 二者定义域不一致 —— 当 LLM 分类失败率上升时会人为压低洗稿率(把"未判出"误当"非象征性"计入分母而不计入分子), 造成系统性下偏假象。现行分母改为仅数"词典判正面 且 实质性标签已成功测量"的同域子集(`yao_2021_pos_substvalid_count{track}`), 若该列因旧 schema 缺失则回退物理分母 `yao_2021_pos_count{track}` 并记 WARNING 日志, 不静默降级。若 stage 21 未产出 innovation_substantiveness_full 或 yao_2021 词典打分列缺失, 该轨全体 washing_ratio_yao_2021{track} 直接跳过赋值(保持 NaN), 不做插补。

【文献定位】
姚加权等(2021)词典本身脱胎于中文金融文本情绪测度传统, 与本仓库另一并排词典 Du et al.(2022, Review of Finance)同属"针对中文金融语境重新构造情绪词表, 而非直接套用英文 Loughran-McDonald 通用金融词典"的方法学路线, 两者互为稳健性检验(Du et al. 2022 本身即以"语言与领域特定性"为核心论点, 主张通用词典跨语言/跨领域迁移会系统性失真, 为本家族按词典分轨对照提供直接理论支撑)。washing_ratio 系列的"情感正面∧内容象征性"构念设计与 Gorovaia & Makrominas(2024)、Fan et al.(2025)在漂绿/漂洗计量上"言辞多于行动"的 NLP 识别实践相互印证; Piotroski, Wong & Zhang(2017, Journal of Law and Economics)则提示中国情境下企业新闻报道存在系统性的政治/媒体偏向, 是解读洗稿率跨银行/跨年份差异时需要控制的背景机制之一(媒体报道本身的正面基调可能部分来自政治动机而非企业真实行为, 与本家族分子分母同域化的处理逻辑呼应)。 晚近文献进一步把这一二分推进到金融科技议题本身: Huang 与 Ma (2024) 以金融科技发展为解释变量, 检验其对企业实质性绿色创新与象征性绿色创新的差异化影响, 在中国情境中直接采用与本家族同源的"实质性 vs 象征性"中文二分表述, 与分子所依赖的 innovation_substantiveness_full 标签在概念与措辞上同域对应。迁移边界须明示: 该文的实质/象征由专利类型(发明 vs 实用新型/外观)客观划分, 主体为非金融上市公司, 金融科技处于解释变量位置; 而本家族的实质/象征由 LLM 对新闻文本逐篇判定, 主体为银行, 金融科技即被报道的议题本身。该文亦未构造任何比率型 washing 指标, 故它仅锚定二分构念在金融科技域的同域适用性, 不锚定本列的比率化口径, 亦不涉及姚加权等(2021)词典这一判定环节。
## VAR: washing_ratio_yao_2021

【变体差分】
本列是三轨中的 full 轨(标题+正文全文), 无轨道后缀, 是家族内的默认/主口径, 亦是本机 dev(T=2)与生产(T=19)语料上样本覆盖最完整的一支。分子分母均在 full 轨文本上计算: `yao_2021_score_full` 用姚加权等(2021)词典打分判定报道情感正负, `innovation_substantiveness_full` 判定该报道属实质性(具体产品/合作/投入描述)还是象征性(空泛表态、无实质创新动作); 两者相乘条件构成分子标记 `_is_yao_2021_pos_symb_full`, 分母为同域化的 `yao_2021_pos_substvalid_count_full`(词典判正面 且 实质性标签已被 LLM 成功测量的报道数, 而非全部词典判正面报道数)。该分类判定本身固定使用 full 轨文本(标题+全文), 与三轨门控铁律一致: 2026-06-29 起 stage 21 是否计入"一篇有效银行金科报道"只看 `llm_verified_full`, full 轨样本量因此不受实体窗定位失败或同句共现缺失的额外过滤条件约束, 通常在三轨中最大、最稳定, 是解读该家族洗稿率数值水平的首要参照系。需要强调的是, full 轨"样本更全"并不意味着它比 ctx/ss 更"准确"或构念上更优 —— 三者是对"洗稿信号出现在文本何处"这一不同问题的并行回答, 与 _ctx、_ss 两个变体各自 just-identified、互为稳健性并排, 不设主次高低, 三者严禁混入同一 over-identified Hansen J 设定; 在回归表中应分列汇报, 而非取三者均值或以某一轨作为"稳健性检验通过与否"的裁决标准。

## VAR: washing_ratio_yao_2021_ctx

【变体差分】
本列为 ctx(实体窗)轨变体: `yao_2021_score_ctx` 在 `content_ctx`(标题+目标实体窗口文本)上打分, `content_ctx` 由 stage 14 `ctx_materializer` 物化(`prepend_title` 将标题拼接到窗口正文前), 使分子分母的报道范围从整篇正文收窄到目标银行实体紧邻的窗口片段。构念意图是检验洗稿信号(词典判正面∧LLM判象征性)是否集中出现在直接谈论该银行的语境中, 还是散布/稀释在全文其余与该银行无直接关联的段落里 —— 若 ctx 轨洗稿率显著高于 full 轨, 提示报道对该银行本身的措辞比全文整体基调更"漂亮而空洞"; 若显著更低, 则提示正面-象征性偏差更多来自泛泛而谈的行业背景段落而非银行本身的直接表述。行宇宙仍是 full-only 留篇门控下的子集: 是否入样只看 `llm_verified_full`, ctx 轨本身降为 conditional-on-full 的测度/稳健性轨, 不单独扩展样本范围。若某行报道的 `content_ctx` 因无法定位到目标实体窗口而回退全文(`ctx_is_fallback=True`), 该行的 `yao_2021_score_ctx` 数值上退化为等同全文口径打分, 此时 ctx 与 full 轨在该行不再提供独立信息, 但分母 `n_articles` 口径仍与 full 轨共享、不因回退而剔除该行。本列与 washing_ratio_yao_2021(full)、washing_ratio_yao_2021_ss 三者各自 just-identified 并排, 互为稳健性检验, 禁止混入同一 over-identified Hansen J 设定, 不可读作对 full 轨的"改进版"或"更精细版本"。

## VAR: washing_ratio_yao_2021_ss

【变体差分】
本列为 ss(同句)轨变体, 其回退语义镜像 ctx 轨: `yao_2021_score_ss` 在 `content_ss`(标题+目标银行∧金融科技关键词严格同句共现窗口, 默认 ±1 句半径, 由 `config/filtering.yaml::context_window.ss_sentence_radius` 配置)上打分, 是三轨中判据最严格、文本噪声最低但样本覆盖最窄的一支 —— 只有银行实体与金融科技词汇在同一句话中出现时, 该句(及其邻句窗口)才进入打分文本。构念意图是把洗稿信号的检验收紧到"银行与金科真正被同时提及"的最强关联片段, 排除报道中与两者共现无关的段落对情感/实质性判定的稀释效应, 是三轨中信噪比最高但统计效力(样本量)最低的一支。若一篇报道未能在正文中找到银行∧金科的同句共现(即便该报道已通过 stage 13 的 ±1 句窗口"邻近共现"硬过滤而留在语料中), `content_ss` 回退为全文 body, `ss_is_fallback=True`, 与 ctx 轨共享 `n_articles` 分母口径, 此时该行 `yao_2021_score_ss` 亦退化为全文打分, 数值上不再独立于 full 轨。⚠ 须特别注意: ss 轨判定"同句"所用的判据原语(`extract_bank_fintech_cooccurrence`, 要求严格同句)与 stage 13 硬过滤阶段用于决定"是否保留该篇报道"的判据原语(`has_bank_fintech_cooccurrence_within_radius`, ±1 句窗口邻近共现)是两套不同口径的函数, 前者比后者更严格, 二者绝不可互相复用或在讨论样本覆盖时混为一谈。本列与 full、ctx 两个变体各自 just-identified 并排, 互为稳健性、不分主次, 三轨禁止混入同一 over-identified Hansen J 设定; 在 dev(T=2)小样本上 ss 轨因回退比例较高, 与 ctx 轨数值可能高度接近, 不应据此判定二者冗余 —— 生产语料(T=19)上二者的判据差异会产生更明显的分歧。

<!-- rendered-citations:begin -->
Du, Z., Huang, A. G., Wermers, R., & Wu, W. (2022). Language and domain specificity: A Chinese financial sentiment dictionary. Review of Finance, 26(3), 673-719. https://doi.org/10.1093/rof/rfab036
Gorovaia, N., & Makrominas, M. (2024). Identifying greenwashing in corporate-social responsibility reports using natural-language processing. European Financial Management, 31(1), 427-462. https://doi.org/10.1111/eufm.12509
Fan, X., Tang, Z., Huang, W., & Yang, K. (2025). Ownership concentration and corporate greenwashing in China's capital markets: Based on a multi-actors perspective. Pacific-Basin Finance Journal, 89, Article 102600. https://doi.org/10.1016/j.pacfin.2024.102600
Piotroski, J. D., Wong, T. J., & Zhang, T. (2017). Political bias in corporate news - The role of conglomeration reform in China. The Journal of Law and Economics, 60(1), 173-207. https://doi.org/10.1086/693096
Huang, J., & Ma, L. (2024). Substantive green innovation or symbolic green innovation: The impact of fintech on corporate green innovation. Finance Research Letters, 63, 105265. https://doi.org/10.1016/j.frl.2024.105265
<!-- rendered-citations:end -->
