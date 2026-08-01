# 人工标注顶刊级收口执行计划 (HUMAN_ANNOTATION_TOPTIER_CLOSEOUT)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**日期**: 2026-07-03 | **状态**: 计划态 (未实施) | **触发**: 用户要求按国际顶刊标准审计人工标注做法 → 审核改进点 → 本计划 → 二次审核
**前置计划**: `scripts/audit/MEASUREMENT_VALIDITY_PARITY_EXECUTION_PLAN_2026-06-22.md` (下称 **MVP-0622**)。本计划 = MVP-0622 在 **tone 双工具 (61/09)** 侧的补全收口 + 三个 MVP-0622 未覆盖的新缺口 (权重接线 / stage 13 漏检审计 / 误分类校正反哺)。**不重做、不推翻 MVP-0622 任何已落地交付**。

---

## §0 任务定位与时机

- **对象** = tone/verification 人工标注双工具: ① `61_human_samples.xlsx` (shim `61_news_llms_human.py` → `validation/llms_human.py`, 双编码员 × {验证,情感} 金标准考卷, config `validation.yaml::human_validation` sample_size=1000/seed=42); ② `09_sentiment_verify_{full,ctx,ss}.xlsx` (shim `64_tone_validation.py` → `validation/tone_validation.py::write_human_verification_sample`, 单编码员三轨情感复核, 现盘各 300 行 = 一致 100 + 分歧 200)。
- **时机关键 (零沉没成本)**: 两工具全部人工标注列 **0 非空** (2026-07-03 实测: 61 为 0/1000×4 列; 09 为 0/300×2 列×3 轨) → 现在重设计不作废任何已有人工劳动。
- **硬约束 (违诺风险)**: tone 手稿已承诺盲标 — `papers_assets/bank_fintech_tone/drafts/zh/manuscript.tex:346-354` "人工标注样本经 61_human_samples 抽样、由独立标注者**盲标**"。现行 61 工作台含 **98 列机器判定** (三家 LLM verified/sentiment/confidence × 三轨, 实测) → 若按现工作台启动标注, 手稿披露即不实。**⇒ WP-A 是任何真实标注启动的硬前置。**
- **生产时序**: 早期试跑盘曾为 T=2 dev 语料 (61 抽样框 = `21_tone_llms_full.parquet`)。本计划全部代码改动 + 工作台重生成本机可完成并验证 ($0); **真实标注**沿用 MVP-0622 deferred 时序 (生产 T=19 重生 21 parquet → 重生成工作台 → 发编码员; G0 tone 先行例外不变)。

## §1 审计终判 (7 项改进点, 2026-07-03 对抗核实后)

| # | 断言 | 终判 | 关键证据 |
|---|------|------|----------|
| C1 | 盲标被破坏 | **确认+升级为违诺风险** | 61 工作台 98 机器列 (实测); 09 刻意并入 13 方法列+多数投票+样本类型 (`tone_validation.py:566-571,607-620`); 手稿已承诺盲标 (`manuscript.tex:349`); MVP-0622 R0-5/F1 已判定 anchoring 为硬伤并**仅**在创新维度工具落地双文件协议 (`scripts/migrate/manual_validation_sampling.py:34,208`), tone 双工具生成器未改 |
| C2 | 09 单编码员, ctx/ss 效标薄弱 | **确认** | 09 仅 `人工判定_情感/理由` 两列 (`tone_validation.py:623-624`), 无 B 编码员列, 回读端无 ICR 路径; 61 双编码金标准判断依据=标题+内容 (full 口径), 无 ctx/ss 专属判定列; MVP-0622:184 将 09 定位为"窗口级金标准"且 :260 意图"tone 双编码者填 61/09", 但 09 结构不支持双编码 |
| C3 | 分歧剔除而非仲裁 | **部分修正: 剔除有披露, 仲裁工作流缺位** | 剔除非静默: stage 63 显式报 attrition + gold_source (`llms_evaluation.py:52,1869-1892,2104-2112`); `裁定备注` 列预留 (`llms_human.py:522-524`) 但全仓无消费者、无第三编码员列与再合并工作流; "金标准偏向简单样本→机器指标向上偏"的统计后果仍成立 |
| C4 | 过采样后无总体加权 | **确认 (接线缺口)** | 09 统计概览只记样本层计数 (一致100/分歧200/源963, 实测), 无总体层计数、无 `population_weight` 列; 回读端只报分层 accuracy (`tone_validation.py:946-996`); Manski-Lerman 加权基础设施在 Panel E/F **现成** (`llms_evaluation.py:277,1174-1215`, 由 population_weight 列驱动) 但 09 不带该列 → 纯接线问题 |
| C5 | 只测准头不测漏网 | **确认 (范围精确化)** | manual_validation Stratum A 仅覆盖 **LLM 门**拒判 (post-stage-13 宇宙内 `llm_verified_full==False`, `manual_validation_sampling.py:78-80`); **stage 13 共现过滤**拒判无任何审计; stage 51 是安慰剂对照变量构建 (`pipeline/falsification/controls.py:2`) 与过滤 recall 无关; 原料现成: 13 输入 (12 产出) 与 13 输出差集 = 被拒宇宙, $0 |
| C6 | 手册薄/无协议/独立性风险 | **确认** | 全仓无 `*PROTOCOL*.md` (glob 实测; 原 docs/methodology 计划书已随 docs/ 删除, `manual_validation_sampling.py:7`); 61 工作台**无指南 sheet** (单 sheet 验证数据, 实测); 09 指南仅 6 行; A/B 四列同文件无分发双副本机制; MVP-0622 G5 承诺协议+IRR 预注册+功效论证但文档未落盘 |
| C7 | 金标准未反哺计量 | **部分修正: 诊断有, 校正无** | Carlson-Burbano 误分类系统偏倚**诊断** 6 检验已实现 (`llms_evaluation.py:1248-1517` Panel D); 但 gold→下游估计的**校正** (DSL/PPI/加权重估) 全仓无实现, 147 个 `.do.tmpl` 无相关模板 |
| 小项 | 负类增样 / n 论证 | 确认 | 09 分层无预测类别层; n=1000/300 无落盘精度论证 (MVP-0622 F2 修正的功效论证只存在于计划文档) |

## §2 工作包

> 编号续 MVP-0622 的 WS 域, 用 WP-A..F 避免冲突。**全部 $0** (无 LLM/嵌入调用)。

### WP-A 61/09 盲标化 — 双文件协议 (P0, 标注启动硬前置)

镜像 `manual_validation_sampling.py` 的 盲表/对账表 (reconciliation) 先例:

> ⚠ **R4 全局改键定音 (P0)**: 全部相关 parquet 的 **docid 非唯一** (article×bank 粒度; 21_full 1331u/1544 行、23_bert 917u/1005、12 号 1392u/1650 单 docid 最多 18 行) — R1–R3 只验了存在性未验唯一性。**本计划所有 "按 docid join/双射" 一律改为: 抽样后铸造合成行键 `_row_uid` (单调整数) 并落双侧文件, join/断言全用 `_row_uid`; docid 降级为展示/溯源列**。

- **A1** `llms_human.py` 生成端拆两文件:
  - `61_human_samples_blind_{A,B}.xlsx` × 2 (per-coder 独立副本, 同行序): 仅 `_row_uid, docid, 日期, 媒体类型(中文), 标题, 内容` + 本编码员 2 标注列 (**保留 `编码者{A,B}_验证/情感` 原列名** — R4: `set_excel_data_validation` L122/L129 硬编码该命名, 保前缀则该函数零改动直接可用, 每盲表天然只命中本编码员两列)。行序在共同 seed 抽样后 **shuffle** (镜像 `manual_validation_sampling.py:214` 防层界锚定; 两副本同 shuffle 保持行对齐)。
  - `61_human_samples_reconciliation.xlsx`: 全列 + `_row_uid`, 共识冻结后才用于对账 (不发编码员)。
  - 文件名从 config 键 `output_32_human_sample` 的 base 派生 `_blind_A/_blind_B/_reconciliation` 后缀 (镜像 merge L442-443 `_merged` 派生法, 不新增 config 键)。
  - 兼容: `merge_annotations` 改为读两份盲表按 `_row_uid` 合并 (集合+行数断言 fail-loud; 原单文件路径保留为 fallback, loud WARNING)。
- **A2** `tone_validation.py::write_human_verification_sample` 盲表化: 编码员表仅 `docid, 标题, 内容, 机器输入文本, 日期, 媒体(中文)` + 人工判定列; `词典_*/BERT_*/LLM_*/多数投票标签/样本类型` 全部移入 per-track reconciliation 文件; 编码指南 sheet 保留在盲表 (`样本来源说明` 行删除 — 它向编码员泄露一致/分歧抽样设计)。
  - ⚠ **docid 是新增基础设施而非现成能力** (R2-P2-1): 09 侧现行 `keep_cols` (`tone_validation.py:642-653`) **主动丢弃 docid** (全文 0 处 docid), 61 侧 docid 靠 179 列 passthrough 侥幸存活 — A2 须在 `keep_cols` 显式补 docid, A1 须在 `desired_front` 显式补 docid, 回读从"位置对齐"改为"键对齐"。
- **A3** 回读端适配 (R2-P1-1 定式, R4 修正契约细节): **loader 层先做 盲表(人工列) ⋈ reconciliation(机器列) by `_row_uid` → join 成单帧后交单帧核**。两侧契约不同 (R4-P1-3):
  - 61 侧 `diagnose_misclassification_bias` 入参本就是 DataFrame → 定式直接成立, 零改动; stage 63 在 `llms_evaluation.py` L1752-1762 加载 df_verify 后加 loader join (检测盲表结构→读 reconciliation ⋈), 下游 L1777-2180 单帧契约不变。⚠ R4 证伪"stage 63 零改动"假设: 它从人工 Excel **同帧**读机器列 (L1998/2050/2122/2180), 不加 loader 则盲表化后机器指标**静默消失** (L2069 `列 X 不存在，跳过`) — A3 是硬必做。
  - 09 侧 `evaluate_human_verification` **入参是路径非 frame** (`tone_validation.py:822`, 函数体内 read_excel) → 拆分定式: L871-1018 主体抽为单帧核 `_evaluate_human_verification_frame(...)`, 原路径签名保留为薄壳 (读旧结构直调核, 读到盲表结构 fail-loud 指引走 blind loader), 新增 `evaluate_human_verification_blind(blind_A, blind_B, reconciliation, track, ...)` = 读 A/B ⋈ 对账 + 共识 + κ/α 后调同一核。
  - `_row_uid` 双侧断言必过 (行数+集合相等, fail-loud)。
  - ⚠ R4 新发现联动: 09 生成端防覆盖守卫 (`tone_validation.py:2878-2887` `count_human_annotations`) 须改为对 **A/B 双盲表**计数, 否则盲表化后守卫失效 (可能覆盖已填标注)。
- **Gate**: 新增 `tests/test_blind_workbench.py` — 盲表列**白名单**断言 (出现任何 `_tone|_verified|_sentiment|词典_|BERT_|LLM_|投票|样本类型` 模式列即红); 两副本行序一致性; **61 与 09 两侧生成端**的 reconciliation docid 双射。
- ⚠ 联动 (R2-P0-1, **三个**既有测试须与 WP-A/B 同批重写, 否则 fail-loud 政策自动打红 G-5):
  1. `tests/test_human_verification_readback.py` 合成工作台 fixture (L52-74) — 人工列与方法列分离进两个 frame;
  2. `tests/test_omni_fix_val_tone.py:355-392` — 直接调 `generate_validation_sample` 并断言 `'机器输入文本' in data.columns` / 读 `验证数据` sheet 列集合, 须按盲表+reconciliation 新结构改断言;
  3. `tests/test_omni_fix_val_eval.py:179-185,226-250` — 单帧 fixture (编码者列+机器列同帧) 调 `evaluate_human_verification`/`diagnose_misclassification_bias`; A3 loader 层 join 定式下函数内部契约不变, 该 fixture 只需改为经 loader 入口或维持单帧直调 (函数签名不变则可能零改动 — 实施时实证判定)。

### WP-B 09 双编码 + 总体权重 (P0)

- **B1** 09 盲表按 WP-A2 出 per-coder 两副本 (`09_sentiment_verify_{trk}_blind_{A,B}.xlsx`); 回读端合并共识 (镜像 `merge_annotations` 语义: 一致→gold, 分歧→待仲裁), 并报 Cohen κ + Krippendorff α (复用 `llms_evaluation.compute_cohens_kappa` / `compute_krippendorffs_alpha`, 后者缺标感知)。
- **B2** 生成端落盘 `population_weight` 列 (reconciliation 内): 层权 = (总体层行数/总体行数) / (样本层行数/样本行数), 层 = {一致, 分歧} (可选第三层 predicted-negative, 见 B3); **统计概览 sheet 增记总体层计数** (现只有样本层, 权重不可从成品恢复 — 日志每 run 覆盖不可依赖)。回读端接 Panel E/F 现成 Manski-Lerman 口径 (`accuracy_weighted_corpus` + `compute_cohens_kappa_weighted`), 与未加权/分层指标并排输出。
- **B3** (可选, 与 B2 同改动面) 抽样加第三层: 多数投票=负面 的 predicted-negative 过采样 (负类基率低, per-class recall CI 过宽); 三层权重同 B2 公式。默认开, config 键 `validation.yaml::human_validation.oversample_negative: true` (⚠ R3-P2-B: 该键实际作用于 **09/tone** 侧抽样而 human_validation 块本为 61 配置域 — yaml 注释须写明作用侧, 或实施时移入 09 专属子块, 二选一在实施时定, 勿静默混域)。

### WP-C 仲裁工作流 (P1)

- `merge_annotations` 升级: 盲表合并后分歧行写入 `61_pending_adjudication.xlsx` (仅 docid+文本+A/B 判定**不含**机器列, 仲裁人 = 第三位资深编码员填 `编码者C_仲裁` 列) → `merge_annotations --with-adjudication` 二次合并: A=B→共识; A≠B∧C 有值→C; A≠B∧C 空→保持待仲裁 attrition (现行为=下限回退, 不破坏 stage 63 现有哨兵语义 `-1`/`待仲裁`)。
- 09 共识合并 (B1) 同规则复用同一实现 (提为 `llms_human.py` 公共函数, 09 侧 import)。
- **报告义务**: stage 63 输出 剔除分歧口径 vs 仲裁后口径 两套指标并排 (主口径=仲裁后), 供手稿 robustness 披露。
- **Gate**: `tests/test_annotation_adjudication.py` — 四象限合并真值表 + 哨兵语义不变断言。

### WP-D stage 13 漏检 (假阴性) 审计 (P1)

- 新脚本 `scripts/migrate/stage13_reject_audit_sampling.py` (**不建 root shim, 不动 16/16/35/OUTPUT_REGISTRY 计数不变量**, 镜像 `manual_validation_sampling.py` 落位先例): 被拒宇宙 = stage 13 输入 (`12_fintech_news.parquet`) − 输出 (`13_cooccurrence_filtered.parquet`) 的**行级 anti-join** (⚠ R4-P1-2: docid 集合差集**不成立** — 实测集合差 61 vs 真实被拒 106 行, 同一 docid 部分行被拒部分存活; 用 `(docid, target_bank)` 复合键或 merge indicator=left_only 做行级差); 按 年×`媒体类型(中文)` 分层抽 N=300 (seed=42, 层权落盘, 铸 `_row_uid`) → 盲表 A/B (文本+`编码者{A,B}_验证 {1,0}` 双编码) + reconciliation。
- 回读脚本同文件 `readback` 子命令: 假阴性率点估 + Wilson 95% CI (⚠ R3-P2-D: `compute_classification_metrics` 的 Wilson CI 绑定在 accuracy 上, 假阴性**率**的 CI 应复用通用式 `validation/dict_coverage.py::wilson_ci`) + Manski-Lerman 总体外推; 产 `data/processed/eval_reports/stage13_reject_audit.csv`。
- 手稿联动 (落地时): tone/attention 手稿 data appendix 增一句被拒宇宙审计披露 (数值待真标注, wire-ahead 措辞)。
- ⚠ T=2 dev 上被拒行数可能 < 300 → `min(N, 可用)` + loud 提示; 生产机重抽才有效度意义。

### WP-E 标注协议文档 + 指南补齐 (P1)

- 新文档 `scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md` (放 scripts/audit/ 保证入库; ⚠ `.gitignore:132` 忽略 papers/**/*.md 勿放那里): 四任务统一协议 = 任务定义与合法值域 / 正反例与边界规则 (混合情感、引用他行负面、监管处罚 vs 风险提示、转述与评论区分) / **试标资格门** (pilot 50 篇 → κ≥0.667 tentative 进入正式, 报告阈值 α≥0.80, 沿用 `llms_evaluation.py:27-29` 已锚定口径; 不达标→修订手册重试标, 循环记录) / 编码员背景·报酬·独立性条款 (per-coder 独立盲表文件, 禁互通) / n 精度论证 (n=1000 ⇒ accuracy ±3.1pp @95%; per-class 由 B3 增样保障) / 仲裁规则 (=WP-C) / 与 MVP-0622 G5 四维统一指南的衔接声明 (本协议为其 tone 侧实例化, 创新维度侧以 MVP-0622 为准)。
- 61 盲表增 `编码指南` sheet (从协议摘编码员可见部分; 09 已有指南 sheet, 仅按 A2 删泄密行)。

### WP-F 误分类校正反哺 (P2, wire-ahead 休眠, DEFERRED 至真标注回填)

- 在 Panel D 诊断之上补**校正**: 新根级模板 `29_tableA14_misclassification_correction.do.tmpl` — 用 gold 子样本估计混淆矩阵 → 处理变量 bias-corrected 敏感性 (最简先做: Aigner 1973 attenuation bound + gold-subset IV 式重估; DSL/PPI 作为 prose 引用与未来扩展, 不在本 WP 实现估计器)。文献锚: Egami et al. (2023, NeurIPS DSL) / Angelopoulos et al. (2023, Science 382, PPI) / Carlson & Burbano (2026, SMJ) — 前两条须先入 `audit_dois.py` 复核流程再进手稿。
- ⚠ 根级模板联动清单 (R2-P2-3 落实为实仓真实清单, 镜像 27/28 先例): ① `stata_runner.py:682::_EXPECTED_ROOT_DO` 21→22; ② `00_master.do.tmpl`; ③ `test_papers_b_route.py:176` expected_count 147→148; ④ `tests/test_stata_templates.py`; ⑤ `tests/test_build_replication_package.py`; ⑥ build-replication 真跑 smoke; ⑦ `CLAUDE.md` 计数口径行 (147/21)。**数值产出 deferred**: 人工列全空 → 模板 instantiate 后无 gold 输入时须优雅 no-op (镜像 :104 取 p + wire-ahead 休眠先例)。

## §3 全局铁律与安全论证

1. **golden 零风险**: 61/09/新审计脚本产物均为 xlsx/csv, **不在** `core/schemas.py::OUTPUT_REGISTRY` (grep 实证无 human_sample/sentiment_verify 条目), 不进 40/46 面板 → 面板列/golden 字节不受任何 WP 影响。WP-F 只加模板不改列。
2. **$0**: 全部改动为生成端/回读端/文档; 无 LLM、无嵌入调用; 不触 `_llm_cache.db`。
3. **计数不变量不动**: 不新增/删除 stage; WP-D 走 scripts/ 脚本 (16/16/35/32 注册数全不变, `test_dag_consistency` 无涉)。
4. **不碰 MVP-0622 已落地资产**: `manual_validation_sampling.py` / Panel E/F / validity_claim_gate (4 paper_spec + `test_validity_claim_gate_consistency.py`) 只复用不修改。
5. **旧盘文件处置**: WP-A/B 落地后 61/09 旧结构文件重生成 (人工列全空, 无劳动损失); 旧文件**不得**发编码员 (含机器列)。回读端不做旧结构兼容 (fail-loud 提示重生成), 避免双代码路径。
6. **手稿联动**: tone `manuscript.tex:346-354` 措辞与 WP-A 后实现一致 (无需改); en 语种对应段落核对一次; WP-D/F 的手稿披露句在真标注回填时一并落 (与 MVP-0622 deferred 手稿项合批)。
7. **"现盘可启动"措辞刷新** (R2-P2-2): `papers/bank_fintech_tone/paper_spec.yaml:171` 与 MVP-0622 :365/:381 的 G0 "currently-disk startable" 在 WP-A 落地前须理解为"**盲表重生后**可启动" (现盘 61 含 98 机器列, 直接启动即违手稿盲标承诺); WP-A 落地时同步刷新 paper_spec 该行**注释** (仅描述性文字, 与第 4 条"gate 机制只复用不修改"不冲突)。gate **逻辑**不变 (真 κ 回填前不解锁), 仅描述性事实过期 — 非与 MVP-0622 的逻辑冲突。
8. **提交纪律**: by-name staging (排除并发会话产物 `*constants.json`/eval_reports/papers_assets 手稿); 绝不 amend / 绝不 --no-verify。

## §4 验收 Gates

| Gate | 内容 |
|------|------|
| G-1 | `tests/test_blind_workbench.py` 全绿 (盲表白名单 / 双副本行序 / reconciliation **`_row_uid`** 双射 — R4: docid 非唯一不可作键) |
| G-2 | `tests/test_annotation_adjudication.py` 四象限真值表 + 哨兵不变 |
| G-3 | `tests/test_human_verification_readback.py` + `test_omni_fix_val_tone.py` + `test_omni_fix_val_eval.py` 三文件在盲表改造后全绿 (前两者重写为新结构 fixture; eval 测试按 A3 实证结果或改 loader 入口或维持单帧直调, R3-P2-A)。断言须含: 加权指标键 + demo_synthetic 路径 + **09 双编码 κ/α 出键** (R3-P2-C, WP-B 核心产出的点名断言) |
| G-4 | 真跑冒烟: 本机重生成 61×3 文件 (盲表A/B+对账表) + 09×9 文件 (3 轨 × 盲表A/B+对账表) + WP-D 抽样, 逐文件断言列集合与填写状态 |
| G-5 | 全量 pytest baseline-stash A/B 差分 0 新增失败 (Select-String FAILED 全量抓取, 勿取尾 N 行) |
| G-6 | ruff 0 新增; WP-F 落地时 build-replication smoke 过 |

## §5 执行顺序

```
WP-A (盲标化, P0) ──┬─→ WP-B (双编码+权重) ─→ WP-C (仲裁) ─→ 重生成工作台 + G-1..G-5
                    └─→ WP-E (协议文档, 可并行)
WP-D (漏检审计脚本) — 独立, 可并行; 本机功能验证, 生产机重抽
WP-F — DEFERRED (真标注回填后), 仅先占位文献与模板设计
真实标注启动 (生产 T=19): 依 MVP-0622 deferred ①②③④ 时序, 前置 = 本计划 WP-A/B/C/E 全落 + pilot 资格门
```

## §6 刻意不做 (归档防重提)

1. **不给 61 加 ctx/ss 人工判定轨** — MVP-0622 F25 已裁定抽样框不强求统一; ctx/ss 效标由 09 (双编码化后) 承接; 61 三轨×双编码 = 编码负担 ×3 无边际效度收益。
2. **不把 tone 升 3 编码员** — 双编码+第三人仲裁已达顶刊惯例; 3 编码员多数票保留给创新维度 (MVP-0622 既定)。
3. **不动 `manual_validation_sampling.py`** — 已达标 (盲表/分层/权重/shuffle); 其未运行状态 (盘上无 manual_validation_samples.xlsx) 属 MVP-0622 deferred, 非本计划范围。
4. **不做外部预注册平台** — 内部协议文档 + git 时间戳即为预注册载体 (与项目全内部惯例一致)。
5. **不在 WP-F 实现 DSL/PPI 估计器** — attenuation bound 先行; 完整半参估计器等真 gold 数据落地后按需评估 (避免对空数据过度工程)。
6. **不改 stage 13 过滤本体** — WP-D 只审计不调参; 若假阴性率超预期, 调参是另一个计划 (须 golden 重生, M0 门)。

## §7 审核记录

- **R1 (撰写前, 2026-07-03)**: 7 项改进点对抗核实, 终判见 §1 — 2 项确认、2 项确认+精确化、2 项部分修正、1 项升级违诺风险; 修正了初判中"分歧静默剔除"(实有 attrition 披露) 与"完全无反哺"(实有 Panel D 诊断) 两处过度陈述。
- **R2 (撰写后, 2026-07-03, 独立对抗评审 agent, 只读实证 48 tool-uses)**: 终判 **needs_fixes → 修订后 ok_to_ship**。
  - 事实核对: §1 全部 file:line 与实测数字抽查 12+ 处**零实质错误**; 数据侧 docid 齐备性获独立确认 (六 parquet 全含 docid: 21_tone_llms_full/21_tone_llms/22_words_tone/23_bert_tone/12_fintech_news/13_cooccurrence_filtered, WP-A/D join 可行)。
  - **P0-1 (已修)**: `test_omni_fix_val_tone.py:355-392` / `test_omni_fix_val_eval.py:179-250` 两个既有测试被盲表改造波及但未列入范围 → fail-loud 政策下必红, G-5 结构性不可过。修法: 纳入 WP-A ⚠联动清单 (现为 3 项) + G-3。
  - **P1-1 (已修)**: demo_mode/单帧契约隐藏耦合 → WP-A3 定式为 "loader 层 join 成单帧再交既有函数, 函数内部契约与 demo 合成器零改动"。
  - **P2-1 (已修)**: 09 侧 docid 现被 keep_cols 主动丢弃 (全文 0 处 docid), 61 侧靠 passthrough 侥幸 → WP-A2 明示 docid 为新增基础设施, keep_cols/desired_front 显式补列。
  - **P2-2 (已修)**: paper_spec.yaml:171 / MVP-0622 "现盘可启动" 描述性事实在 WP-A 前过期 → §3.7 登记措辞刷新义务 (非逻辑冲突)。
  - **P2-3 (已修)**: WP-F "七联动" 落实为实仓 7 项真实清单 (含 test_stata_templates.py; 剔除本仓不存在的 test_stata_replication_matrix.py)。
  - **P2-4 (已修)**: reconciliation "179 列 + docid" 重复计数措辞 → "179 列 (docid 已在其中)"。
  - 遗漏面清扫: 全仓 22 个 61_human_samples/09_sentiment_verify 引用点逐一核对, 其余 (run_pipeline_validation banner / paths.yaml / readback 测试) 均已覆盖或无结构断言。与 F25/G0/validity_claim_gate **无逻辑冲突**。
- **R3 (修订版终审, 2026-07-03, 第二个独立只读 agent, 与 R2 不同视角)**: 终判 **ok_to_ship, 0 P0 / 0 P1**。
  - 六项 R2 修订逐项核对**全部真实落地且自洽**; "联动第 3 条 vs G-3" 被特查判定结果兼容非矛盾 (仅措辞 over-claim, 即 P2-A)。
  - 内部一致性: §3 编号 1-8 / Gates / §5 顺序 vs 优先级 / G-4 文件计数 (61×3, 09×9) / WP-C⋈B1 引用链 / Panel E/F 复用链 (`accuracy_weighted_corpus` 为 population_weight 驱动的 metrics 键非独立函数) 全部闭合; 另确认 `compute_cohens_kappa` 双副本 (radius_sensitivity/llms_evaluation) 因 B1 带模块名引用而无歧义。
  - 可执行性: 六 WP 均"改动文件+设计要点+验收方式"齐备可开工; B3 config 增量键与现 `human_validation` 块 (仅 sample_size/random_seed 两键) 结构兼容。
  - **P2×4 (已修)**: P2-A G-3 措辞放宽 (eval 测试允许维持单帧直调); P2-B `oversample_negative` 配置域错位加注 (作用于 09 侧, 实施时定注释或移块); P2-C G-3 补"09 双编码 κ/α 出键"点名断言 (WP-B 核心产出原仅间接覆盖); P2-D WP-D 假阴性率 CI 改指 `dict_coverage.py::wilson_ci` 通用式 (原引用的 CI 绑定 accuracy)。
  - 另: 撰写者自检修正 2 处 (G-4 09 侧计数 6→9; R2 记录 docid parquet 清单补全为 6 文件全名)。
- **R4 (开工前最终评审, 2026-07-03, 双独立实施规格 agent: 61 侧 + 09 侧, 合计 34 tool-uses 全实证)**: 抓到 R1–R3 **集体漏检**的系统性硬障碍, 已全部修入正文:
  - **P0 (改键定音)**: 全线 parquet docid 非唯一 (article×bank 粒度, 21_full 1331u/1544、23_bert 917u/1005、12 号 1392u/1650 max 18) — 此前只验存在性未验唯一性 → 所有 join/双射改用合成行键 `_row_uid`, docid 降级展示列 (WP-A 顶部定音 + G-1 改写)。
  - **P0 (命题证伪)**: "stage 63 消费端零改动" 不成立 — 它从人工 Excel 同帧读机器列 (L1998/2050/2122/2180), 盲表化后不加 A3 loader 则机器指标**静默消失**而非报错 (L2069 跳过分支) → A3 升级为硬必做 (已写入 A3)。
  - **P1 (WP-D 度量证伪)**: docid 集合差 (61) ≠ 真实被拒行数 (106), 同 docid 部分行被拒部分存活 → WP-D 改行级 anti-join (已写入)。
  - **P1 (契约错配)**: `evaluate_human_verification` 吃路径非 frame → 拆单帧核 `_evaluate_human_verification_frame` + 薄壳 + blind loader 三层定式 (已写入 A3)。
  - **P1**: `set_excel_data_validation` 硬编码 `编码者{A,B}_*` 列名 → 盲表保留原列名即零改动复用 (已写入 A1)。
  - **P1 (新联动)**: 09 生成端防覆盖守卫 `count_human_annotations` (L2878-2887) 须改对 A/B 双盲表计数 (已写入 A3)。
  - **P2 利好×2**: 总体层计数变量在生成端现成 (agree_idx/disagree_idx/valid, 权重落盘无新基础设施; 注意总体行数取 len(valid) 非 len(df)); `媒体(中文)`/`媒体类型(中文)` 列全部实存。
  - 函数名勘误: 09 生成函数实名 `generate_validation_sample` (L529, 计划此前误写 write_human_verification_sample); 09 唯一调用点 L2895-2899 (n_agree=100, n_disagree=200, seed=42), 三轨循环 L2223。
  - test_omni_fix_val_eval 精确化: 其 diagnose 单帧直调用例零改动; 仅 L217+ 的 61 端到端 fixture 属 WP-A1 联动。
- **终态**: 四轮审核 (R1 对抗核实 / R2 对抗评审 / R3 终审 / R4 双侧实施级评审) 闭环, 累计发现并修复 P0×3 / P1×5 / P2×10 + 自检 2 处; **R4 后批准开工** (WP-A/B/C/D/E + gate 测试; WP-F 按既定 DEFERRED)。

## §8 实施记录 (2026-07-03, WP-A/B/C/D/E 全落地)

**改动文件清单** (全部 $0, golden 无关):
- `validation/llms_human.py` — WP-A1+C: 新增 `derive_blind_paths`/`_write_blind_workbook`(内嵌编码指南 sheet)/`_write_reconciliation`/`_BLIND_CONTEXT_COLS`(**含 target_bank** — 任务定义所需上下文, 实体匹配产物非模型预测, 不构成锚定; 对计划 A1 白名单的实施期扩充)/`_ANNOTATION_COLS`; main() 抽样后 shuffle+铸 `_row_uid`+写三件套、不再产旧单文件 (存在则 loud 弃用警告); `merge_annotations(+with_adjudication)` 双盲表 `_row_uid` 合并 (fail-loud 断言+legacy fallback) + strict 双口径列 + 待仲裁工作台 (C 两列锁下拉、已填 C 拒覆盖) + `--with-adjudication` 二次合并; CLI dispatch 扩展。⚠ 实施期修复 2 处计划外: ① merge 入口存在性检查须覆盖派生盲表 (否则新协议恒被提前拦截); ② 待仲裁台下拉不可走 `set_excel_data_validation` 改名技巧 (同名 A 列命中错列), 改按列号直加。
- `validation/tone_validation.py` — WP-A2/B1/B2/B3: `generate_validation_sample` 拆盲表A/B+对账表 (shuffle+`_row_uid`+docid 显式入 keep 集; 指南删'样本来源说明'加'独立性'; 对账表落 `population_weight` 四格 poststratify {一致,分歧}×{预测负面,非负面} + 统计概览记总体层计数) + B3 negative 第三层 (config `oversample_negative`); `count_human_annotations` 守卫盖住双盲表; 新增 `_load_blind_consensus` (三文件 `_row_uid` 断言→双编码共识→κ/α); `evaluate_human_verification` 盲标协议优先 + legacy 单文件回读兼容保留 (R3-P2-A, 供历史工作台与既有单帧 fixture; **对 §3.5 fail-loud 条款的实施期澄清**: fail-loud 指编码员工作台分发与键漂移, 回读端保留 legacy 是刻意兼容) + 加权指标出键 (`accuracy_weighted_corpus`/`kappa_weighted_corpus`/`Accuracy_加权总体` CSV 列)。
- `validation/llms_evaluation.py` — WP-A3 (E-2): Step1 加载后盲标 loader join (无机器列+有 `_row_uid` → 读对账表 `_row_uid` ⋈ 单帧, 缺对账表/键漂移 SystemExit fail-loud); WP-C 双口径披露 (仲裁并入计数 + strict 保留说明; **strict 双口径全指标表 = wire-ahead**, 真标注回填后补产 — 对计划 C-4 的范围澄清: 空标注下双指标表恒空, 机制已备)。
- `scripts/migrate/stage13_reject_audit_sampling.py` — WP-D 新脚本: 行级 anti-join (键 `(docid,target_bank)` 双侧唯一性 fail-fast) → 真跑实证被拒宇宙 **106 行** (= R4 预言); 年×媒体分层+largest remainder+层权+shuffle+`_row_uid` → 盲表A/B+对账表; `readback` 子命令 = 双编码共识→假阴性率+`dict_coverage.wilson_ci`+加权外推→`eval_reports/stage13_reject_audit.csv`。
- `config/validation.yaml` — `human_validation.oversample_negative: true` (注释明示作用于 09/tone 侧, R3-P2-B)。
- `papers/bank_fintech_tone/paper_spec.yaml:171` — G0 注释刷新为"盲表重生后可启动" (§3.7)。
- `scripts/audit/HUMAN_ANNOTATION_PROTOCOL_2026-07-03.md` — WP-E 协议文档 (v1.0 预注册)。
- 测试: 新增 `tests/test_blind_workbench.py` (G-1+G-3, 9 用例) + `tests/test_annotation_adjudication.py` (G-2, 4 用例); 适配 `test_omni_fix_val_tone.py` (×2 处) 与 `test_human_verification_readback.py` (×1 处端到端); `test_omni_fix_val_eval.py` **零改动** (R4 预言成立)。⚠ 实施期新发现 2 个 R2/R4 均漏列的波及断言: `test_verify_xlsx_has_track_suffix` + `TestOverwriteGuardWired::test_annotated_workbook_survives_full_track_rerun` (端到端走 `_run_validation_for_track`), 均已按盲标协议重写。

**Gate 结果**: G-1/G-2/G-3 = 五文件 73 用例全绿; G-4 = 真跑 stage 61+64+WP-D 重生 15 文件逐项断言 PASS (61×3=1000 行 / 09×9=307/305/307 行含负面增样 7/5/7 / WP-D×3=106 行; 白名单零泄露、`_row_uid` 全双射、指南 sheet 全在、旧单文件零产出); G-6 ruff 全绿 (6 项 auto-fix)。**G-5 方法变更声明**: 共享树有并发会话未提交产物, baseline-stash A/B 会波及他会话 → 改为"单次全量 sweep + 失败归因" (改动模块相关五文件已 100% 绿, 其余失败须归因为既存盘面态/flaky)。**G-5 结果 (2026-07-03 实跑)**: 全量 sweep FAILED = **23**, 逐项归因**全部为文档在案的既存红灯、0 个与本计划模块相关**: ① `test_panel_reproducibility` golden 列哈希 ×17 — 盘上 parquet 与 committed golden 既存分叉 (golden 重生 DEFERRED 生产机, 多会话在案); ② `test_benefit_society_dual_track` ×2 — cohort CSV 被 `.gitignore:92` 永不可能 committed (契约债清偿会话在案); ③ `test_dual_track` NaN ×3 — 盘上数据态 (在案); ④ `test_omni_fix_strategic` jieba 隔离 ×1 — 顺序 flaky (在案)。人工标注/验证域 (llms_human/tone_validation/llms_evaluation/blind/adjudication) **零失败**。

**遗留 (DEFERRED, 与母计划一致)**: 真实标注 (生产 T=19 重生语料后, 先过 pilot 门); WP-F 校正模板; strict 双口径全指标表 (wire-ahead); 生产机重抽 WP-D (dev 106 行全选仅验功能)。

**R5 (提交前终审, 2026-07-04, 独立 agent 逐 hunk 审 12 文件全 diff, 21 tool-uses)**: 终判 **ok_to_commit, 0 P0 / 0 P1**。六攻击面 (边界空值/语义回归/确定性/无关混入/新文件质量/提交安全) 逐一核验: `_vp_base` 不重算恰对齐对账表命名 (刻意正确); NaN 层权被回读端 notna 剔除; pending/error/insufficient 状态机与 `_cleanup_stale_csv` 触发与原逻辑等价; count 三态契约保持; 双盲表严格同源同行序 (seed=42); 零无关改动混入; `wilson_ci`/`compute_cohens_kappa_weighted` 签名一致; 断言变异敏感性抽查有效; 无秘钥。**P2×3 已在提交前全修**: ① `_load_blind_consensus` 补人工判定列存在性守卫 (缺列→优雅 error, 禁 KeyError 中断三轨循环); ② 盲表存在但不可读/结构异常 → error 保留旧 CSV (不当 pending 清盘, 与 legacy 读失败不对称语义对齐); ③ WP-D docstring 去机器专属解释器路径。修后五文件回归+ruff 复绿。
