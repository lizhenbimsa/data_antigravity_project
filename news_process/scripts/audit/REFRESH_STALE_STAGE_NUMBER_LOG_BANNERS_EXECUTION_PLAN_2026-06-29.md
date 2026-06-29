# 执行计划：刷新底层模块运行期日志 banner 的自指旧阶段号 (option a)

**日期**: 2026-06-29
**性质**: golden-safe · log-only · 纯文本 (无列/值/路由/schema 改动)
**目标**: 让每个阶段的 `logs/<stage>.log` 里"本阶段自报的阶段号"与其文件号/DAG 号一致 (v3.11.0 NN 重编号的日志可读性收尾)
**状态 (2026-06-29 执行完毕)**: 用户决策 27c→80 (选项 i) + 现在执行。**已应用 59 处编辑** (57 脚本 + 2 Edit工具) 跨 23 文件, 全部 token-only/交叉引用保留。验证闸全绿: ruff clean · py_compile 23/23 · §9.2 完整性闸 0 自指残留 · §9.3 lm 39e→74/39d保留实证 · **§9.4 全量 pytest A/B = 0 新增失败** (30 预存共有 + 1 flaky baseline-only) · constants.json SHA256 不变。分支 `chore/refresh-stage-banner-numbers`, **未提交** (待用户决定)。⚠ 同期工作树另有并发会话 WIP (CLAUDE.md/sentiment.yaml/test_w8, 非本计划, by-name 提交须排除)。

---

**(以下为评审历史)** **三轮对抗评审全部完成** (R1 26模块全读 / R2 23模块全新穷举 / R3 22模块逐条 logger 枚举上千调用)。发现曲线 **+11 → +9 → +1 单调收敛**; 累计补入 21 漏项 (§4.5/§4.7/§4.8), 27c 扩为 3 处 (§5.2)。golden-safe / test-safe / 回滚 / 提交协议 / 验证闸 经多路独立确证 **sound**。终审裁决 **GO (有条件)** → **唯一 BLOCKING = §5.2 的 27c 用户决策 + 执行批准**。**本计划制定至今 0 行代码改动** (仅本 .md, git diff 空)。

> **外部引用说明 (消歧)**:
> - 文中 **"§17.2"** 一律指 **v3.11.0 重编号权威计划 `scripts/audit/RENUMBER_SHIMS_PLAN_2026-06-20.md` 的 §17.2** (该节把"散文/注释/docstring 内的旧 stage 号"定为接受的 P3, 不机械替换), **非本文档章节** (本文档仅 §0–§12)。
> - 文中 **"影响扫描①②③④"** 指**本计划制定前**运行的发现工作流的 4 路影响扫描 (① tests 断言 / ② 日志解析消费者 / ③ Stata 模板与 labels / ④ golden 与复现), 其结论见本计划 §6/§7 与**附录 C** 摘要。

---

## 0. 背景与目标

v3.11.0 (nn-stage-renumber) 把 35 个 `NN_*.py` shim 全量重编号, **承重 token** (文件名 / 产物名 / `STAGE_NAME` 常量 / DAG label / golden 键 / test 断言) 已全迁并经 POSITIVE-grep 验证。但按 §17.2 的明确决策, **散文层** (docstring / 注释 / 日志 banner 描述文字) 的旧号被**刻意保留为接受的 P3** —— 因为旧/新号空间重叠 (旧 stage-13=ctx→14, 新 stage-13=cooccurrence), 机械替换会 mangle。

本计划只处理其中**会打进日志、被用户/审稿人看到**的那一类: **运行期 `logger.*` banner 里的【自指】旧号**。改完后, 每个阶段日志开头自报的 "阶段 NN: ……" 与该阶段文件号一致。

### 0.1 为什么 docstring / 注释不在本次范围 (关键收窄)

- **docstring / 模块注释从不打进 `logs/<stage>.log`** (日志文件名只取 `STAGE_NAME` 常量, 见 `core/logging.py:237` `log_file = ...f"{stage_name}.log"`; banner 文本不参与) → 改它们对"日志自洽"这个目标**零贡献**。
- docstring 里的自指旧号**与交叉引用旧号混在同一行** (见 §2 的 mangle 陷阱实例), 单独改自指会制造**新的行内矛盾** → 高风险。
- §17.2 已明确把这类散文旧号归为**接受的 P3**。

故 docstring/注释自指旧号 **本次不动** (DEFER, 见 §1)。这与用户在 option (a) 的原话一致 ("运行期 logger banner 旧号统一刷成新号; docstring 散文可留可改")。

**负向实证 (第一轮评审)**: 全仓 grep 确认**无任何模块**把 `__doc__` / docstring 对象传给 `logger.*()` (仅 `dict_coverage.py:722` / `threshold.py:521` 两处"见 docstring"的引用说明文字, 非把 docstring 打进日志) → docstring 旧号确实**永不进 `logs/<stage>.log`**, DEFER 它对目标零损失。

---

## 1. 范围界定 (Scope)

| 类别 | 处置 | 理由 |
|---|---|---|
| **IN — 运行期 `logger.*` banner 里的【自指】旧号** | **改** (old→new) | 唯一进日志、被看到的; 直接达成目标 |
| DEFER — docstring / 模块注释里的【自指】旧号 | **不动** | 不进日志; 与交叉引用混行有 mangle 风险; §17.2 接受 P3。可作未来独立 pass |
| EXCLUDE — 所有【交叉引用】旧号 (描述上游/下游/姊妹阶段) | **绝不动** | 描述的是别的阶段, 用旧号也是历史正确; 误改即引入错误 (见 §2) |
| EXCLUDE — `config/paths.yaml::filenames` 的 `output_XX_*` 键号 | **不动** | v3.11.0 刻意保留的稳定抽象句柄 (paths.yaml:64-70 已披露) |
| EXCLUDE — 测试文件里的旧号 (docstring / assert 失败消息) | **不动** | 测试不断言生产 banner 文本 (见 §7); 这些是测试自身散文, 改它们是另一范围 |
| EXCLUDE — Stata `.do.tmpl` / 生成的 labels 里的旧号 | **不动** | 仅对数据源的交叉引用散文 (如 "stage 39f"), 不影响功能 (影响扫描③ CLEAN) |
| SPECIAL — `runner.py` L641 "阶段 45" | **改 (含特别处理)** | 45 是 panel 内部子步号; 见 §5.1 |
| OPEN — `benefit_society_audit_combined.py` "阶段 27c" (L458/L477/L813) | **待用户决策** | 27c 可能是 benefit_society 审计【论文】阶段标识; 见 §5.2 |

**范围边界 (明确)**: 本计划仅覆盖 **STAGES_MAIN(16) + STAGES_VALIDATION(16) 的实现模块 + audit-only shim 80** 的 **runtime logger banner 自指旧号**。以下**明确不在范围** (第一轮评审确认):
- **panel 内部子步号 (41–48)**: `encode.py`(40_build_panel) / `network_spillover.py`(46) / `network_brokerage.py`(47) / `llm_peer_iv.py`(**48**) 的 `STAGE_NAME` 与 banner 用的是 stage 40 的**内部子步号约定** (dag.py name "阶段40 (内含 41+42+43+44+46+47)" 的延伸), **不是 v3.11.0 被重编号的 shim 旧号** → 不动。其中 `llm_peer_iv.py` 自称 "stage 48" (L108 logger / L119 STAGE_NAME) 是内部子步号 (无对应 shim), 若要规整属**另一独立决策**, 本计划不处理 (登记于附录 B)。
- **papers/ 衍生论文 CLI 入口** (`papers/**/analysis.py` 等): 独立 CLI、独立日志库, 不属 STAGES_MAIN/VALIDATION → 不动。
- **codebook / 转换工具脚本 / Stata `.do.tmpl` / 生成 labels**: 见 §1 表 EXCLUDE 行。

---

## 2. 核心判据：自指 (改) vs 交叉引用 (绝不动)

> **铁律**: 只改"模块描述**它自己这个阶段**"时用的旧号。模块引用"**别的**上游/下游/姊妹阶段"时用的号 (无论新旧) **一律不动**。

**mangle 陷阱实例** (`pipeline/filtering/fintech_intensity.py` = stage 15, 旧号 14):
```
L71 (docstring): STAGES_MAIN 阶段14, ... 上游 = stage 12 + stage 13 (materialize_ctx), 下游 = stage 15 (policy_alignment)
                          └ 自指(→15)              └ 交叉(对)   └ 交叉:materialize_ctx现为14   └ 交叉:policy_alignment现为16
```
同一行四个号: `阶段14`=自指(应→15)、`stage 13`=交叉指 materialize_ctx(它现在才是14)、`stage 15`=交叉指 policy_alignment(它现在是16)。**若只把自指 `阶段14`→`阶段15`, 该行会同时出现两个"15"指代不同阶段** → 制造新矛盾。这正是本计划**把整条 docstring 行排除在外**、只动**纯自指的 runtime banner**(下面 L701 那种)的原因:
```
L701 (logger banner): logger.info("阶段 14: 金融科技技术重度评分 (TF-IDF + IDF 加权关键词质心, 三轨 full/ctx/ss)")
                                      └ 纯自指, 无交叉引用同行 → 安全改为 "阶段 15:"
```

**判定流程 (逐处)**: ① 该 token 出现在 `logger.*(...)` 调用里吗? 否→跳过 (docstring/注释, DEFER)。② 该号 == 本模块旧号且语义在"自报本阶段"吗? 是→SELF, 改。③ 该号指别的阶段吗? 是→CROSS, 不动。

**④ 同一 logger 行/块里既有自指又有交叉引用 — 两子情形 (第三轮精炼, 替代旧"一律整行排除")**:
- **(4a) 自指号 ≠ 交叉号** (token 可区分; 如 lm_discriminant L159 `39e mask ... 与 39d 对齐`: 自指=39e、交叉=39d): **只替换自指那一个 token** (`39e`→`74`), 交叉 token **逐字保留** (`39d` 不动)。安全, 无 mangle、无碰撞 → §4.8 #56 即此。
- **(4b) 自指号 == 交叉号 或 改后会与同行交叉号撞号** (真碰撞风险): **整行排除** (列入 §12 风险, 不改)。典型反例 fintech L71 docstring `阶段14` 改 15 会与同行交叉 `stage 15`(policy) 撞号 —— 但该行是 docstring 本就 DEFER。
- **实测口径**: 范围内所有 logger 自指+交叉混行**均属 (4a) 号不同** → 按 (4a) 只改自指; (4b) 仅作铁律兜底, 当前范围内无命中。

---

## 3. old→new 映射表 (v3.11.0 权威)

主线: `12b→13 · 13→14 · 14→15 · 15→16 · 30a→25 · 18→26 · 45→40`
(00/11/12/16/21/22/23/24/46/51 自身号本就=新号)
验证: `31→60 · 32→61 · 32a→62 · 33→63 · 34→64 · 35→65 · 36→66 · 37→67 · 38→68 · 38b→69 · 39→70 · 39a→71 · 39c→72 · 39d→73 · 39e→74 · 39f→75` (无 39b)
未注册: `27c→80 (见§5.2) · 52→81 · 53→82` (81/82 banner 已是新号, 无需改)

---

## 4. 编辑清单 (runtime logger banner 自指号) — 【非权威, 随评审增长的已知最小集】

> 🔴 **完整性的唯一权威保证 = §9.2 验证闸, 不是本清单。** 本清单是【非穷尽、随评审持续增长的已知最小集】: 已知数 35 (初版) → 46 (第一轮 +11) → **55 (第二轮 +9)**, 且第二轮在第一轮判"clean"的 `lm_discriminant_validity.py` 里又查出 3 处 → **证明任何手工冻结清单都无法证明完整**。执行者**必须**按 §4.6 派生规则逐 (模块,旧号) 独立穷举 + 用 §9.2 闸 (post-edit case-insensitive grep 断言 logger 自指归零) 做完成判据, **不得把本清单当完整**。
>
> **"改为"列约定 (统一, 消歧)**: 每格只标【自指旧号 token 替换后的值】, 即 `旧→新` (如 `阶段 13`→`阶段 14`); 除该 token 外**整行逐字不变** (§4.6 token-only 铁律) —— 含 "· 阶段: " 前缀、" / 25_article_sbert" 后缀、版本前缀 `v3.5.x`、shim 文件名 `64_xxx.py`、`{占位符}`、内部子步 `→45`、所有交叉引用号, 一律不动。
>
> ⚠ **定位以"逐字字符串匹配"为准, 不以行号为准** (本仓常有并发会话改动致行号漂移; Edit 工具按 old_string 精确匹配)。下表行号 / 现文本为 2026-06-29 实读快照且**多为缩写片段** (用 `...` 省略); 执行时**必须先 Read 该行取完整逐字文本**再 Edit, 不可直接用表中缩写串做 old_string。

### 4.1 主线模块 (pipeline/)

| # | 文件 | 行 | 现文本片段 (自指旧号) | 改为 |
|---|---|---|---|---|
| 1 | `pipeline/text/ctx_materializer.py` | 564 | `logger.info("阶段 13: 三轨文本物化 ...")` | `阶段 14:` |
| 2 | `pipeline/text/ctx_materializer.py` | 599 | `· 阶段: {STAGE_NAME} (stage 13 三轨文本物化; STAGES_MAIN)` | `stage 14` |
| 3 | `pipeline/filtering/fintech_intensity.py` | 605 | `· 阶段: {STAGE_NAME} (金融科技..., STAGES_MAIN 阶段14; 三轨...)` | `阶段15` |
| 4 | `pipeline/filtering/fintech_intensity.py` | 701 | `logger.info("阶段 14: 金融科技技术重度评分 ...")` | `阶段 15:` |
| 5 | `pipeline/filtering/policy_alignment.py` | 1194 | `logger.info("阶段 15: 文章级政策语义对齐度 ...")` | `阶段 16:` |
| 6 | `pipeline/text/article_staleness.py` | 580 | `logger.info("阶段 18: Article-level staleness ...")` | `阶段 26:` |
| 7 | `pipeline/text/article_staleness.py` | 605 | `· 阶段: {STAGE_NAME} (..., STAGES_MAIN 阶段18, kind=robustness)` | `阶段26` |
| 8 | `pipeline/text/article_sbert.py` | 279 | **多行** `logger.info(\n  "阶段 30a: Article-level SBERT 嵌入持久化 "\n  ...)` | `阶段 25:` |
| 9 | `pipeline/panel/runner.py` | 641 | `logger.info("阶段 45: 面板导出 ... (41+42+43+44+46+47→45)")` | `阶段 40:` (内部子步 `→45` 处理见 §5.1) |

> ⚠ **#8 (article_sbert L279) 是自查时用单行 grep 漏掉、靠全读 main() 才发现的多行 f-string banner** —— 实证 §12 R2 风险真实存在, 故 §4.4 的"全读"是硬要求, 非可选。

### 4.2 pipeline/audit 验证模块

| # | 文件 | 行 | 现文本片段 | 改为 |
|---|---|---|---|---|
| 9 | `pipeline/audit/inter_track_kappa.py` | 363 | `logger.info("阶段 39a: 轨间一致性 Cohen's κ ...")` | `阶段 71:` |
| 10 | `pipeline/audit/construct_orthogonality.py` | 386 | `logger.info("阶段 39c: 创新构念正交性检验 ...")` | `阶段 72:` |
| 11 | `pipeline/audit/construct_orthogonality.py` | 517 | `logger.info(f"v3.5.0 D3 stage 39c reading: ...")` | `stage 72` |
| 12 | `pipeline/audit/lexical_discriminant_validity.py` | 608 | `logger.info("阶段 39d: 文本指标判别效度 ...")` | `阶段 73:` |
| 13 | `pipeline/audit/lexical_discriminant_validity.py` | 509 | `logger.info(f"v3.5.1 stage 39d [{suffix}] 完成: ...")` | `stage 73` (借鉴 L726/743/767 已用 "stage 73") |
| 14 | `pipeline/audit/lm_discriminant_validity.py` | 362 | `logger.info("阶段 39e: LM 词典 8 维判别效度 ...")` | `阶段 74:` |
| 15 | `pipeline/audit/cross_media_alpha.py` | 385 | `logger.info("阶段 39f: 跨媒体源 tone 一致性 ...")` | `阶段 75:` |
| 16 | `pipeline/audit/cross_media_alpha.py` | 585 | `logger.warning("  三轨均无有效输出 ...; 跳过 stage 39f")` | `stage 75` |

### 4.3 validation/ 验证模块

| # | 文件 | 行 | 现文本片段 | 改为 |
|---|---|---|---|---|
| 17 | `validation/threshold.py` | 514 | `logger.info("阶段 31: 银行×金科分类阈值敏感性 ...")` | `阶段 60:` |
| 18 | `validation/llms_human.py` | 144 | `logger.info("阶段 32: LLM×人工金标准采样器 ...")` | `阶段 61:` |
| 19 | `validation/llms_human.py` | 166 | `· 阶段: {STAGE_NAME} (..., 验证支线 stage 32; ...)` | `stage 61` |
| 20 | `validation/dedup_threshold.py` | 212 | `· 阶段: {STAGE_NAME} (阶段 32a 去重阈值参数敏感性, ...)` | `阶段 62` |
| 21 | `validation/dedup_threshold.py` | 295 | `logger.info("阶段 32a: 去重阈值参数敏感性 ...")` | `阶段 62:` |
| 22 | `validation/dedup_threshold.py` | 573 | `logger.info(f"阶段 32a 完成: 测试 {len(thresholds)} 个阈值, ...")` | `阶段 62` |
| 23 | `validation/llms_evaluation.py` | 1596 | `logger.info("阶段 33: 新闻分类模型评估 ...")` | `阶段 63:` |
| 24 | `validation/tone_validation.py` | 2033 | `logger.info("阶段 34: 情感验证 (三轨主控) ...")` | `阶段 64:` |
| 25 | `validation/radius_sensitivity.py` | 1254 | `logger.info("阶段 35: 实体上下文窗口半径敏感性检验 ...")` | `阶段 65:` |
| 26 | `validation/entity_masking.py` | 833 | `logger.info("阶段 36: Entity Masking 实体掩码稳健性测试 ...")` | `阶段 66:` |
| 27 | `validation/dict_coverage.py` | 815 | `· 阶段: {STAGE_NAME} (..., 验证支线 stage 37; ...)` | `stage 67` |
| 28 | `validation/dict_coverage.py` | 886 | `logger.info("阶段 37: 金融科技词典覆盖率审计 ...")` | `阶段 67:` |
| 29 | `validation/media_diversity.py` | 1141 | `· 阶段: {STAGE_NAME} (..., STAGES_VALIDATION 支线 stage 38)` | `stage 68` |
| 30 | `validation/media_diversity.py` | 1231 | `logger.info("阶段 38: 媒体名称与地域多样性审计 ...")` | `阶段 68:` |
| 31 | `validation/decay_sensitivity.py` | 1010 | `logger.info("阶段 38b: 距离衰减权重敏感性检验 ...")` | `阶段 69:` |
| 32 | `validation/prompt_sensitivity.py` | 1440 | `· 阶段: 70_prompt_sensitivity / 阶段 39 (...)` | `阶段 70` (仅改 "阶段 39"; "70_prompt_sensitivity" 已对) |
| 33 | `validation/prompt_sensitivity.py` | 1458 | `logger.info("=== 阶段 39: Prompt 措辞敏感度量化测试 ... ===")` | `阶段 70:` |
| 34 | `validation/prompt_sensitivity.py` | 1525 | `logger.info("阶段 39: Prompt 措辞敏感度量化测试 (Carlson & Burbano 2026 SMJ §3.5)")` | `阶段 70:` |

**小计**: 确认 35 处 runtime banner 自指改动 (主线 9 [含 article_sbert] + audit 8 + validation 18)。**此数为下限**, §4.4 全读复核后可能再增。

### 4.4 执行时必须【全读每个受影响模块的 banner 块 + grep 双保险】(防多行 f-string 漏项)

> **硬要求 (非可选)**: 单行 grep 会漏多行 f-string banner —— 本计划自查时 article_sbert L279 (#8) 即如此被漏, 全读 main() 才发现。故执行时对**每个**受影响模块 (§4.1/4.2/4.3 全部 + 下列重点) 必须: (1) `grep -nE 'logger\.(info|warning|error|debug)'` 列出全部 logger 行, (2) **逐个 Read 其 banner 块** (尤其 `logger.info(` 后接续行字符串的多行调用), (3) 用 §2 判据逐处判 self/cross, 补齐任何纯自指 runtime banner 残漏。

下列模块尤其须留意 (曾出现计数分歧 / 已知多行 banner):
- `validation/llms_evaluation.py` (上一轮称 L1596+L1618 两处; 本快照只确证 L1596 → 复核 L1618)
- `validation/entity_masking.py` (上一轮称 L833 banner + L813/L817 为注释/字符串 → 确认仅 L833 是 logger banner)
- `validation/prompt_sensitivity.py` (发现称 P0=4; 本快照确证 3 处 → 复核第 4 处)
- `pipeline/audit/lexical_discriminant_validity.py` (L628 `· 阶段: {STAGE_NAME} (... STAGES_VALIDATION 39d ...)` 若为 logger 行则补入)
- `validation/dict_coverage.py` / `validation/media_diversity.py` (确认 `· 阶段:` 行均已纳入)

**判据不变**: 只补"纯自指 + 在 logger 调用内 + 同行无交叉引用"的行; 任何与交叉引用混行者 → 列入 §12, 不改。

### 4.5 第一轮对抗评审补入的 banner (11 处, §4.1–4.3 漏项)

> 第一轮评审逐模块**全读**后, 又揪出 11 处 §4.1–4.3 漏掉的纯自指 runtime banner。漏因归三类: **(α) 大写 "Stage"/"STAGE"** (我的初版 grep 区分大小写只匹配小写 `stage`); **(β) 第二条 "· 阶段: NN / name" 明细 banner** (我只列了主 banner); **(γ) 多行 `logger.warning(...)` 自指 + 完成日志**。

| # | 文件 | 行 | 现文本片段 (自指旧号) | 改为 | 漏因 |
|---|---|---|---|---|---|
| 36 | `pipeline/filtering/policy_alignment.py` | 790 | `logger.info("开始计算: 文章级政策语义对齐度 (Stage 15)")` | `(Stage 16)` | α |
| 37 | `pipeline/filtering/policy_alignment.py` | 844 | `logger.warning("...跳过 Stage 15 计算。")` | `Stage 16` | α |
| 38 | `pipeline/text/article_sbert.py` | 320 | `· 阶段: 30a / 25_article_sbert (...)` (多行) | `30a`→`25` (保留 "· 阶段: " 与 " / 25_article_sbert") | β |
| 39 | `pipeline/audit/construct_orthogonality.py` | 399 | `· 阶段 39c construct_orthogonality (...)` (多行) | `39c`→`72` (保留 "construct_orthogonality" 等) | β |
| 40 | `pipeline/audit/construct_orthogonality.py` | 726 | `✓ v3.5.0 D3 stage 39c done; ...` (多行 f-string) | `stage 39c`→`stage 72` (保留 "v3.5.0 D3") | γ |
| 41 | `pipeline/audit/lexical_discriminant_validity.py` | 417 | `logger.info(f"v3.5.1 39d: {_mask_col} ≥ ...")` | `39d`→`73` (即 `v3.5.1 73: {_mask_col}...`, 保留前后) | γ |
| 42 | `validation/llms_evaluation.py` | 1618 | `· 阶段: 33 news_llms_evaluation (...)` | `33`→`63` (保留 " news_llms_evaluation ...") | β |
| 43 | `validation/tone_validation.py` | 2081 | `· 阶段: 34 tone_validation (...thin shim 64_...)` | `34`→`64` (保留 " tone_validation ... 64_...") | β |
| 44 | `validation/entity_masking.py` | 816 | `logger.warning("阶段 36 (Entity Masking) 需在线 LLM ...")` (多行) | `阶段 36`→`阶段 66` | γ |
| 45 | `validation/decay_sensitivity.py` | 917 | `· 阶段: 38b decay_sensitivity (...)` | `38b`→`69` (保留 " decay_sensitivity ...") | β |
| 46 | `validation/prompt_sensitivity.py` | 1428 | `logger.warning("阶段 39 (Prompt 敏感度) 需在线 LLM ...")` (多行) | `阶段 70` | γ |

**修订小计**: 已知 runtime banner 自指改动 **≥ 46 处** (§4.1–4.4 的 35 + 本节 11) + §5.2 的 27c 组 3 处 (待决策)。**此数仍标"≥", 非穷尽** —— 两轮发现共补出 12 处, 证明唯一可靠的完整性保证是 §4.4 全读派生 + §9 验证闸 (post-edit 对每个 (module, old#) 跑 case-insensitive grep 断言 banner 内旧号归零)。

### 4.6 派生规则 (执行时据此穷举, 不止照搬上表)

对每个 (受影响模块, 旧号) 对, banner 自指可能以下列**任一形态**出现, 须全覆盖:
1. 主 banner: `logger.info("阶段 <old>: <desc>")`
2. 明细 banner: `logger.info(f"     · 阶段: {STAGE_NAME} (... 阶段<old> ...)")` 或 `· 阶段: <old> / <new>_name (...)`
3. **大写/英文**: `Stage <old>` / `STAGE <old>` (grep 必须 **case-insensitive**)
4. **多行 f-string**: `logger.xxx(` 在一行、`"...<old>..."` 在续行 (必须全读 banner 块)
5. 完成/操作日志: `logger.info(f"... stage <old> done/完成/reading: ...")` / `f"v3.5.x <old>: ..."`
6. 在线/离线门控 warning: `logger.warning("阶段 <old> (...) 需在线 LLM ...")`

**替换铁律 (token-only)**: 每处**只替换自指旧号那几个字符** (`阶段 39c`→`阶段 72` / `Stage 15`→`Stage 16` / `v3.5.1 39d`→`v3.5.1 73`), 行内其余字符 (含版本前缀 v3.5.x、shim 文件名 `64_xxx.py`、内部子步 `→45`、所有交叉引用号) **逐字不变**。

### 4.7 第二轮对抗评审补入的 banner (9 处) — 又证清单非穷尽

> 第二轮用 §4.6 六形态规则做**全新独立穷举**, 在 §4.1–4.5 之外又补出 9 处 (集中在 **form 2 明细 banner** 与 **form 5 操作/完成日志**)。**尤值警惕**: `lm_discriminant_validity.py` 第一轮被 per-file agent 判 "clean", 第二轮却查出 3 处 → "complete" 裁决亦不可全信, §9.2 闸是兜底。"改为"列遵 §4 约定 (`旧→新`, 余字不变)。

| # | 文件 | 行 | 现文本片段 (自指旧号) | 改为 | 形态 |
|---|---|---|---|---|---|
| 47 | `pipeline/filtering/policy_alignment.py` | 832-833 | **多行** `logger.warning(f"找不到权威政策语料: {auth_path}。"\n  f"跳过 Stage 15 计算。")` | `Stage 15`→`Stage 16` | 4 |
| 48 | `pipeline/text/article_sbert.py` | 360 | `"为 stage 30a article-level SBERT 持久化提供最新方法学锚点。)"` | `stage 30a`→`stage 25` | 5 |
| 49 | `pipeline/audit/inter_track_kappa.py` | 294 | `· 阶段: {STAGE_NAME} (轨间一致性 Cohen's κ; STAGES_VALIDATION 39a)` | `39a`→`71` | 2 |
| 50 | `pipeline/audit/lexical_discriminant_validity.py` | 628 | `· 阶段: {STAGE_NAME} (文本指标判别效度; STAGES_VALIDATION 39d; 三轨...)` | `39d`→`73` | 2 |
| 51 | `pipeline/audit/lexical_discriminant_validity.py` | 705 | `logger.warning(f"v3.5.1 39d: panel 缺 ({panel_path}), graceful skip")` | `39d`→`73` | 5 |
| 52 | `pipeline/audit/lm_discriminant_validity.py` | 285-286 | **多行** `... DAG stage 39e)` | `stage 39e`→`stage 74` | 2 |
| 53 | `pipeline/audit/lm_discriminant_validity.py` | 164 | `logger.info(f"  39e: {_mask_col} ≥ ... mask")` | `39e`→`74` | 5 |
| 54 | `pipeline/audit/lm_discriminant_validity.py` | 392 | `logger.error(f"... 跳过 39e")` | `39e`→`74` | 5 |
| 55 | `pipeline/audit/cross_media_alpha.py` | 419 | `· 阶段: {STAGE_NAME} (跨媒体源 tone 一致性 Krippendorff α; 验证支线 39f)` | `39f`→`75` | 2 |

**修订小计**: 已知 runtime banner 自指改动 **≥ 55 处** (35 + 11 + 9) + §5.2 的 27c 组 3 处 (待决策)。**重申: ≥55 是下限, 非穷尽; 以 §9.2 闸归零为完成判据。**

> **runner.py L647 的裁定 (第二轮 flag, 判为 RETAIN 不改)**: `logger.info("【方法】串行 7 子步 (StageSpec 41→42→43→44→46→47→45): ...")` 行尾的 "→45" 与 §5.1 L641 行尾 "(41+...→45)" 同属**内部子步编排语义**, 非外层阶段自指, **保留不动** (见 §5.1)。

### 4.8 第三轮 (最终) 穷尽枚举: 收敛 + 唯一补入 #56

> 第三轮对 22 模块做**逐条 logger 调用枚举** (非搜索, 检视上千条 logger.* 调用) → **强收敛**: 仅补出 **1 处** (vs 第一轮 +11、第二轮 +9)。20/22 模块完全收敛; 另 construct_orthogonality L399 经核为**误报** (其 "72_construct_orthogonality.py" 是本阶段自己的 shim 文件名、非交叉引用, #39 本就正确)。

| # | 文件 | 行 | 现文本片段 | 改为 | 说明 |
|---|---|---|---|---|---|
| 56 | `pipeline/audit/lm_discriminant_validity.py` | 159-161 | **多行** `logger.warning(\n  f"  39e mask: panel 缺 ...,\n  f"不过滤 (与 39d 口径对齐失败, 结果与 39d 不可比)")` | **仅** `39e`→`74` (该行的 1 个 "39e mask"); **两个 "39d" 保留** (交叉引用 stage 73) | self+cross **号不同**, 安全只改自指 (见 §2 精炼判据) |

**最终已知数**: ≥ 56 处 runtime banner 自指改动 (35 + 11 + 9 + 1) + §5.2 的 27c 组 3 处 (待决策)。**三轮发现曲线 12→9→1 单调收敛**, 配合 §9.2 闸 → 完整性已达可放行水平。

---

## 5. 特殊项与开放决策

### 5.1 SPECIAL — `runner.py` L641 "阶段 45"
现: `logger.info("阶段 45: 面板导出 (主, 三轨承载) — Bank-Year 面板总装 (41+42+43+44+46+47→45)")`
- 外层阶段身份 = **40** (文件 `40_panel_export_main.py`, DAG name "阶段40 (内含 41+42+43+44+46+47)")。
- "45" = panel runner 内部最终导出子步号 (内部子步 41/42/43/44/46/47/45 是设计内文档化语义)。
- **处置**: 把开头自报 `阶段 45:` → `阶段 40:` (修正对外阶段身份); 行尾 `(41+42+43+44+46+47→45)` 的内部子步映射**保留**(它是内部编排语义, 非对外阶段号)。即仅改第一个 "45"。
- 注: dag.py name 自身列的是 "41+42+43+44+46+47" (不含 45), 与此处行尾 "→45" 已存在轻微不一致, 属既有内部子步表述, 不在本次扩大处理。

### 5.2 OPEN — `benefit_society_audit_combined.py` "阶段 27c" (共 3 处, 第一轮评审补全)
该模块自指 27c 的 runtime banner **共 3 处** (初版只列了 L813, 第一轮评审补出 L458/L477):

| 处 | 行 | 现文本片段 | 若决定改则改为 |
|---|---|---|---|
| a | 458 | `logger.info(\n  "阶段 27c: benefit_society 替代锚点 + 安慰剂审计 "...)` (多行) | `阶段 80:` |
| b | 477 | `· 阶段: 27c benefit_society ... (audit-only 旁支, shim 80_placebo_and_alt_anchor)` | `阶段: 80` (仅改首 27c; "shim 80_placebo..." 已是新号, 不动) |
| c | 813 | `logger.info("  ⏱ [phase] 阶段 27c 总墙钟 ...", ...)` | `阶段 80` |

- **冲突证据**: (a) 上一轮对抗审计判定 27c 是 benefit_society **审计论文**的阶段标识 (非项目 pipeline 号), 刻意保留; (b) 但**同一 stage-80 功能**的姊妹模块 `benefit_society_alt_anchor.py` (L643/658/666/759) 已用 "阶段 80_alt_anchor" 自报 → 同一项目阶段内两个模块自报号不一致。
- **溯源 (第一轮评审建议补)**: 27c 作为 benefit_society 审计旁支阶段号的出处 = `80_placebo_and_alt_anchor.py` docstring 的"权威说明"段 + `scripts/audit/` 下 benefit_society 审计计划 (J-L-M 2026 robustness alignment plan §3 P1.6) + benefit_society 论文 PAP。**注**: L477 自身已含 "shim 80_placebo_and_alt_anchor" → 项目层面该阶段的 shim 号确为 80。
- **两个选项**:
  - **(i) 改 27c→80 (3 处全改)** — 与姊妹 alt_anchor 及自身 L477 的 "shim 80" 对齐, 项目日志内阶段号自洽; **推荐, 一致性优先**。
  - **(ii) 保留 27c (3 处全留)** — 尊重"审计论文阶段标识"语义, 维持 §17.2 P3。
- **决策归用户**。在用户拍板前, 这 3 处**挂起不执行**, 其余 ≥56 处照常。**两选项内部一致** (要么 3 处全改, 要么 3 处全留, 不可只改部分)。

---

## 6. golden 安全性论证 (golden-safe)

| 约束 | 状态 | 论据 |
|---|---|---|
| 任何 `.parquet`/`.dta` 列名/值/schema | ✅ 不触碰 | 仅改 `logger.*(...)` 字面量, 不动任何 `to_parquet`/`save_dataset`/列构造 |
| `core/schemas.py::OUTPUT_REGISTRY` / `_OUTPUT_FILENAME_KEYS` | ✅ 不触碰 | 不改 schemas.py |
| `core/dag.py` StageSpec (name/script/计数) | ✅ 不触碰 | 不改 dag.py → 计数 16/16/35/16 不变 |
| `config/*.yaml` | ✅ 不触碰 | 无 YAML 改动 |
| `STAGE_NAME` 常量 | ✅ 不触碰 | 仅改 banner 文本, 常量本就是新号 |
| `golden_panel_v0.json` | ✅ 不受影响 | golden 存的是**逐列哈希**, 不含日志/banner 文本 (影响扫描④实证: 22 stage 列哈希清单无 banner 文本) |
| `test_panel_reproducibility` / `test_dag_consistency` | ✅ 不受影响 | 前者比对列哈希; 后者比对 StageSpec 身份/计数/脚本名 — 均与 banner 文本无关 |

**结论**: 纯 log-only 文本改动, **golden 零字节相关, 无需重生 golden**。

---

## 7. 测试安全性论证 (校正发现阶段影响扫描①的误判)

发现阶段"影响扫描①"曾给出"改 banner 会破 8 个测试"的**高风险结论, 该结论错误** —— 它把"测试文件自身 docstring/assert 消息里含旧号"误当成"测试断言生产 banner 文本"。逐条核验:

| 被指会破的测试 | 它实际断言什么 | 是否受本次改动影响 |
|---|---|---|
| `test_dag_consistency::test_main_stage_count` / `test_validation_stage_count` | `len(STAGES_MAIN/VALIDATION)` 计数 (读 dag.py) | ❌ 不受影响 (不改 dag.py) |
| `test_dag_consistency::test_v3_5_1_stage_39d_*` | dag 脚本名 `"73_..."` 在/不在注册表 | ❌ (脚本名是新号, 不动) |
| `test_71_inter_track_kappa::test_dag_registration` | `"73_..."` in scripts | ❌ ("39d" 仅在 assert 失败消息串里, 我们不改测试文件) |
| `test_13_cooccurrence_filter::test_production_default_is_window_radius1` | config `sentence_radius==1` | ❌ (与 banner 无关) |
| `test_construct_orthogonality::test_dag_registers_stage_39c` | `"72_..."` in dag | ❌ |
| `test_panel_orphan_merges::test_runner_has_feature_merge_block` | runner.py 源码含**文件名** `"26_staleness_panel.parquet"`/`"75_cross_media_alpha.parquet"` | ❌ (这些文件名串是独立行, 改 L641 banner 不触碰它们) |

**根因 (影响扫描②实证)**: 全仓**无任何**代码 `re.search/split/startswith/parse` 这些 banner 文本; 日志文件名只取 `STAGE_NAME` 常量 (`core/logging.py:237`)。**banner 文本不是任何代码/测试的契约**。

**结论**: 本次改动**不破任何测试**。仍以 §9 的全量 pytest baseline-stash 差分**实证** 0 新增失败 (不靠论证)。

> 旁注 (不在本范围): 测试文件自身的 docstring/assert 消息确实也含旧号 (如 `test_73_lexical_discriminant.py:1` "stage 39d"); Stata `.do.tmpl` 也有 "stage 39f" 交叉引用散文。这些是**独立的散文清理范围**, 本计划不动, 如需可作未来 pass。

---

## 8. 执行步骤 (有序)

1. **创建工作分支** (当前在 detached HEAD; 先 `git switch -c chore/refresh-stage-banner-numbers` 基于 main, 避免污染)。
2. **快照 baseline** (供 §9 差分): `git stash` 不适用 (无未提交改动); 改为先记录 `git rev-parse HEAD` + 跑一次基线 pytest 收集失败集到 `scratchpad/baseline_fails.txt` (见 §9 的 A/B 方法)。
3. **逐文件复核 + 应用编辑** (§4.1→4.2→4.3, 每处用 Edit 精确字符串替换; §4.4 模块先 grep 补漏)。**§5.2 的 27c 按用户决策决定是否纳入**。
4. **§5.1 runner.py 特别处理** (只改第一个 "45")。
5. 全程**不碰**: dag.py / schemas.py / config / 测试文件 / .do.tmpl / 任何 .parquet。

---

## 9. 验证闸 (post-edit gates, 全绿才算完成)

1. **静态**: `ruff check .` clean; 对每个改过的 .py 跑 `python -m py_compile` 通过。
2. **自洽 grep — 权威完整性闸 (正向, 最关键)**: 对**每个 (受影响模块, 旧号) 对** (§3 全 21 模块), 跑 **case-insensitive** grep `rg -i -n '(阶段|stage) ?<old>' <module>`; **并辅以 `rg -i -A3 'logger\.' <module>` 扫每个 logger 块的续行** (防 form 4 多行 f-string 把旧号放在续行而单行 grep 漏检)。然后**逐个命中目检**: 凡落在 `logger.*(...)` 调用内、描述本阶段自己 (self) 的命中**必须归零** (已全部改新号); 仍残留 → 即本快照漏项, 当场补改后重跑。**预期仍在**的命中 (不报错, 切勿误改): docstring/注释里的自指 (DEFER)、所有交叉引用 (描述别的阶段)、config 键。此闸是"≥55 非穷尽"清单的兜底, **以它的归零为完成判据, 而非以照搬上表为准**。
3. **未误伤 (负向)**: `git diff` 逐 hunk 目检 —— 每个 hunk 必须 (a) 只在 `logger.*` 行, (b) 只改了自指号字符, (c) 未触碰任何交叉引用号/文件名串/列名。**交叉引用旧号在 diff 中必须 0 出现于"删除行"**。
4. **测试 (实证, 非论证)**: 跑**全量 pytest**, 用 **A/B baseline 差分法** (with-edits vs HEAD-baseline) 证明**失败集逐项一致, 0 新增失败** (本仓 disk-state flakiness 已知, 须 A/B 对照, 不可只看绝对数; 见 memory `log-enrich-round8`)。
   - **降 flakiness 方差 (第二轮评审加固)**: baseline 与 with-edits **各跑 3 次取失败集【交集/并集】对比** (单次易受偶发 disk I/O 漂移污染致伪阳性); 两侧并集相同 → flakiness 排除。A/B 两次运行须**同机同 venv、间隔尽量短 (<1h)**, 期间不更新包、不跑其它长任务。
   - **新增失败归因器**: 若出现新增失败, 先看失败信息是否含 `stage/阶段/logger/STAGE_NAME` 关键字 → 含则可能真实 (本计划只改 banner, 理论上不会), 不含 (I/O/缓存/网络) → 疑 flakiness, 重跑确认。
5. **计数不变**: `pytest tests/integration/test_dag_consistency.py` 绿 (STAGES_MAIN=16 / VALIDATION=16 / shim=35 / OUTPUT_REGISTRY=16)。
6. **golden**: `pytest tests/integration/test_panel_reproducibility.py` 绿 (应无变化, 不重生 golden)。
7. **⚠ 还原副作用**: 跑 pytest 会 bump `data/processed/v3_5_1_constants.json` (或类似), **提交前还原, 勿 stage** (见 memory 多条)。**加固**: 编辑前对该文件取 SHA256 快照, 编辑后 (跑 pytest 前) 再取一次, 若一致 → 实证本计划改动确实未碰它 (它的 bump 纯属 pytest 运行副作用, 与 banner 改动无关)。

---

## 10. 回滚
全部改动为单分支可逆文本编辑: `git restore <file>` 或 `git switch main` + 删分支即可。无产物/golden 改动 → 无数据回滚负担。

---

## 11. 提交协议 (用户批准执行且验证全绿后)
- **by-name** `git add` 列出本次改过的具体文件 (绝不 `git add .` / `-A`; 排除 `v3_5_1_constants.json`、`eval_reports/*`、任何并发会话 WIP 文件)。
- HEREDOC commit message, 尾部 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 不 `--no-verify`, 不 amend; 让 pre-commit (check-prompt-headers + ruff) 跑过。
- ⚠ 本仓常有并发会话改同名文件 → add 前 `git status` 复核, 只提交本计划涉及的 banner hunk。

---

## 12. 已知风险与缓解

| 风险 | 缓解 |
|---|---|
| **R1 自指/交叉误判** (把交叉引用误改) | §2 逐处判据 + §9.3 负向 diff 目检 (交叉号不得出现在删除行); 混行者整行排除 |
| **R2 本快照漏项** (多行 f-string / 计数分歧模块) | §4.4 执行时逐文件 grep 复核 + §9.2 正向自洽 grep 兜底 |
| **R3 行号漂移** (并发会话) | §4 以逐字字符串匹配定位, 不依赖行号; Edit 失败即说明文本已变, 重新 grep |
| **R4 误触发 golden 重生** | §6 论证 + §9.6 panel_repro 实证; 全程不碰列/schema |
| **R5 27c 决策错误** | §5.2 挂起待用户拍板, 不擅自改 |
| **R6 半改 docstring 制造新矛盾** | docstring 整类 DEFER (§1), 本次只动 runtime banner |
| **R7 提交污染** (constants.json / 并发文件) | §9.7 还原 (+SHA256 快照) + §11 by-name add |
| **R8 多行 f-string 漏检** (三轮新暴露; article_sbert #8 等) | §4.4 全读 banner 块 (硬要求) + §4.6 form 4 + §9.2 `rg -A3` 续行扫描 |
| **R9 form-5 操作/完成日志系统性漏检** (三轮新暴露; lm/lexical 的 `<old>: ...mask`/`跳过 <old>`/`v3.5.x <old>:`) | §4.6 form 5 显式列入 + §9.2 case-insensitive 枚举闸; **以 §9.2 归零为完成判据, 不靠手工清单** |
| **R10 27c 范围歧义** (非 v3.11.0 映射内; benefit_society 审计旁支) | §5.2 显式挂起待用户决策 (3 处), 决策前其余 ≥56 处照常 |
| **R11 手工清单永不证完整** (三轮发现曲线 12→9→1, 仍非 0) | 清单降格为"非权威已知最小集"; **§9.2 验证闸 (post-edit 逐 (模块,旧号) grep 归零) 为唯一权威完整性保证** |

---

## 附录 A：本次**不动**的旧号样本 (供评审确认未误伤)
- **交叉引用** (482 处, 例): `fintech_intensity.py` "上游 stage 12 / stage 13"; `article_staleness.py` "依赖 stage 30a"; `lm_discriminant_validity.py` "与 39d 统一"; `cross_media_alpha.py` Stata 模板 "treatment 源自 stage 39f"。
- **docstring 自指** (DEFER, 例): `fintech_intensity.py:2` "阶段14"; `tone_validation.py:2` "阶段34"; `cooccurrence_filter.py:1` "stage 12b"; 各 `pipeline/audit/*` 模块 docstring 首行的 39a/39c/39d/39e/39f。
- **config 键**: `output_12b_cooccurrence` / `output_13_news_with_ctx` / `output_14_fintech_intensity` / `output_15_article_alignment` / `output_32_human_sample`。
- **测试文件 / Stata 模板** 里的旧号。

## 附录 B：明确考虑后排除的项 (非 v3.11.0 stale 自指, 本计划不处理)
- **`pipeline/panel/llm_peer_iv.py` 自称 "stage 48"** (`STAGE_NAME="48_llm_peer_iv"` L119; logger 消息 L108 "Stage 48 (LLM peer IV)"; 注释 L83/93)。它是 stage 40 panel 的**内部子步** (在 dag 文档化的 41/42/43/44/46/47 之后的延伸子步), **从来不是被 v3.11.0 重编号的独立 shim** (无 `48_*.py`), 故 48 **不在 old→new 映射内**, 无"目标新号"可言。规整它 (例如改成 `40.x-llmpeer` 风格) 属另一独立设计决策, 与本计划"刷新重编号 stale 自指"目标正交 → **本计划不动**。同理 `encode.py`(40_build_panel) / `network_spillover.py`(46_network_spillovers) / `network_brokerage.py`(47_network_brokerage) 的内部子步 STAGE_NAME 亦不动。
  - **与 runner.py L641 "45→40" 的原则性区分 (闭合第二轮一致性评审 I5)**: `runner.py` 是 shim `40_panel_export_main.py` 的**实现**, 其**外层阶段**正是 v3.11.0 被重编号的 `45→40` (45 **在** old→new 映射内, 有明确目标新号 40) → 故 L641 自报 "阶段 45" 是 stale 自指, 改 40。而 `llm_peer_iv.py` 的 "48" **不在映射内、无目标新号** → 不改。判据一致: **"在 old→new 映射内有目标新号" 才改**; runner 满足、llm_peer 不满足。
- **panel 内部子步 banner** (各子步模块的"阶段 4x"/"步骤 N"自报) — 第一轮元完整性核查确认: 除 `runner.py` L641 (已纳入 §5.1) 外, **无其它 panel 子步模块含 stale 自指 banner**。
- **papers/ 衍生论文 CLI** 与 **codebook/转换工具脚本** 的日志阶段号 — 独立日志库、非 STAGES_MAIN/VALIDATION, 见 §1 范围边界。

## 附录 C：制定前 4 路影响扫描结论摘要 (供 §6/§7 溯源)
计划制定前运行的发现工作流做了 4 路影响扫描, 结论 (经第一、二轮独立复验):
- **① tests 断言**: 全仓**无任何测试断言生产 logger banner 文本**。曾被疑"会破"的 8 个测试, 实际断言的是 StageSpec 计数 / 脚本名(新号) / config 值 / runner 源码里的文件名(新号) —— 均与 banner 文本无关 (详见 §7)。
- **② 日志解析消费者**: 全仓**无任何** `re.search/split/startswith/parse` 针对 banner 文本; 日志文件名只取 `STAGE_NAME` 常量 (`core/logging.py:237`) → banner 文本非任何代码契约。
- **③ Stata 模板与 labels**: `.do.tmpl` 仅含对数据源的**交叉引用散文** (如 "stage 39f"), 生成的 `*_labels.do` / codebook 纯变量定义无阶段号 → 不受影响, 且不在本计划范围。
- **④ golden 与复现**: `golden_panel_v0.json` 存 **8812 个逐列哈希**, 零 banner 文本; `logs/` 已整体 `.gitignore` (第一/二轮实证) → 改 banner 对 golden / `test_panel_reproducibility` / `test_dag_consistency` 零影响。
