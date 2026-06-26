# 文献理论锚点扩充报告 · 第四补编(第 6 轮日志学术化富集 in-log 引证新增 · APA 第 7 版 · Crossref DOI→标题回比全核验)

- **日期**: 2026-06-26
- **定位**: 本文件是 `LITERATURE_ANCHORS_2026-06-13.md`(主编, 12 族/143 条)、`LITERATURE_ANCHORS_SUPPLEMENT_2026-06-21.md`(补编, 10 族/102 条)、`LITERATURE_ANCHORS_EXPANSION_2026-06-22.md`(第二补编, 10 子族/63 条)、`LITERATURE_ANCHORS_SUPPLEMENT_III_2026-06-24.md`(第三补编, 24 桶/108 条)之后的 **第四补编**, 五者**合为一套**。
- **起因**: 第 6 轮"日志学术化富集"工作流(`log-enrich-round6`, 106 智能体)对 49 个生产模块的 `logger.*` 输出补/深 `📖 方法论依据` 块, 共 emit **58 个唯一 DOI** 进运行日志。经全 diff DOI 抽取 + 独立 Crossref 批量回比(58/58 resolved)+ 注册表成员核对, 其中 **56 条已在前四份注册表内**(直接复用已核验锚点), 仅 **2 条为新引入**——本补编登记这 2 条, 使"注册表 = 在日志中引用的单一事实源(SSOT)"重新闭合。
- **核验铁律**: "查实-或-不存在"。两条新锚点均经 `GET https://api.crossref.org/works/{DOI}` 实时解析、回读标题逐字比对; 严禁自我生成参考文献。下方"Crossref 回读标题"为接口实际回读值。
- **golden 影响**: 无。本轮全部改动为 log-only(经 sig4 AST 扫描 / golden-diff 分类器 / 全 diff 产物写模式 grep 三重确认: 0 处产物列/return/dtype/控制流改动), parquet 产物字节不变, golden 快照不受影响。

---

## 〇、白话导读

**这份补的是什么**: 第 6 轮把项目里 49 个流水线模块的"运行日志"升级成"带文献引证 + 四位有效数字统计"的方法报告。绝大多数引文直接取自前四份已核验文献库; 但有两篇是这一轮才第一次写进日志、而文献库里还没收的——一篇是"可复现计算研究十准则"(给数据版本/血缘追踪模块当方法依据), 一篇是"多维构念分析框架"(给跟风衰减模块解释"为什么要做全文/邻域/同句三轨")。这两篇都**不是编的**: 都被 Crossref 官方接口查到、标题逐字对上了。本补编把它们正式登记入库。

---

## 一、第 6 轮新引入已核验锚点(2 条)

### 四补-1. 可复现计算研究 / 出处与版本追踪 (core/data_versioning.py)

> 锚定 `core/data_versioning.py` 的 `📖 方法论依据` 日志块(内容寻址 / git commit + config hash + 输入文件 SHA-256 + 依赖版本的可复现血缘记录)。该模块在前四份注册表中无对口锚点(既有 robustness 桶为 Oster δ / Romano-Wolf / PPML / qreg 等计量估计方法, 与"数据版本追踪"无方法学锚定), 故新登记此条。

- Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for reproducible computational research. *PLoS Computational Biology, 9*(10), e1003285. https://doi.org/10.1371/journal.pcbi.1003285
  - *锚定* `data_versioning (parquet schema metadata 血缘 / 内容寻址 / 输入哈希)` — method-origin/construct-anchor — 可复现计算研究的经典准则文(规则 4-6 直接对应"记录所有中间结果、版本与精确出处"); 本模块以 git commit + config_hash + 输入 SHA-256 + 依赖版本将每个 parquet 产物落实为可溯源、可复现校验。
  - 〔Crossref 回读标题: Ten Simple Rules for Reproducible Computational Research〕
  - 〔Crossref 著录: PLoS Computational Biology, 2013〕

### 四补-2. 多维构念分析框架 / 测量-处理匹配 (pipeline/sentiment/herd_decay.py)

> 锚定 `pipeline/sentiment/herd_decay.py` 的 `📖 方法论依据` 日志块, 解释"双/三轨化动因"(measurement-treatment matching): 全文相似度 ≠ 银行邻域/同句相似度, 故 full/ctx/ss 三轨各自度量不同子构念。

- Edwards, J. R. (2001). Multidimensional constructs in organizational behavior research: An integrative analytical framework. *Organizational Research Methods, 4*(2), 144-192. https://doi.org/10.1177/109442810142004
  - *锚定* `herd_decay 三轨 (full/ctx/ss) staleness 度量动因` — construct-anchor — 多维构念的整合性分析框架(构念应按其维度结构选择聚合/分解的测量与建模方式); 锚定本项目"按文本归因窗口(全文/实体邻域/同句)将跟风-陈旧度拆为三个并列子构念测量"的构念效度论证。
  - 〔Crossref 回读标题: Multidimensional Constructs in Organizational Behavior Research: An Integrative Analytical Framework〕
  - 〔Crossref 著录: Organizational Research Methods, 4(2), 2001〕

---

## 二、第 6 轮 in-log 引证全量 DOI 核验快照(58/58 resolved)

- **抽取口径**: 对 49 个改动文件 `git diff` 的全部新增(`+`)行抽取 `10.\d{4,9}/...` 形态 DOI, 去重得 **58 个唯一 DOI**。
- **独立批量核验**: 逐 DOI 直连 `api.crossref.org/works/{DOI}`(404 回退 `api.datacite.org/dois/{DOI}`), 回读标题/年份/期刊。结果 **58/58 resolved, 0 unresolved, 0 臆造**。
- **注册表成员**: 其中 56 条已见于前四份注册表(本套既有已核验锚点), 2 条(上节 Sandve 2013 / Edwards 2001)由本补编新登记。
- **2024–2026 密度**: 58 条中约 30 条为 2024–2026(其中 JEL 2026 DiD 指南、QJE 2025 技术扩散、JPE 2024 GIV/金融创新、Econometrica 2024 同伴效应、RES 2026 jackknife 聚类 SE、JBES 2025 wild bootstrap 多向聚类、SMJ 2025 LLM 标注、ManSci 2025 ChatGPT-文本分析、ARFE 2025 Generative AI & Finance、JF 2025 监管碎片化、RFS 2025 finance-benefits-society 嵌入法等)。

> 全套合计: 前四份 416 条 + 本补编 2 条 = **418 条已核验唯一锚点**。后续全语料复核(`audit_dois.py`)已纳入本文件。
