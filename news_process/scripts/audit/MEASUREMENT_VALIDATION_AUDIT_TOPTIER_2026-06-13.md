# 测度验证框架 · 国际顶刊级对抗审核报告

**日期**: 2026-06-13
**范围**: 全部测度验证框架 — `validation/`(stages 31/32/33/34/35/36/39) + `pipeline/audit/`(39a/39c/39d/39e/39f) + FLS(`forward_looking.py`) + 人工标注三件套
**基准**: AER / QJE / JF / RFS / ASQ / Management Science / SMJ 的测度效度与 LLM-as-annotator 报告标准
**方法**: 9 维并行发现 → 每条发现 3 名独立 skeptic 对抗证伪(factual / gap-reality / severity-calibration) → 完整性补漏。172 个 subagent / 9.23M tokens。主控亲核统计核心 + 落地修复。
**处置**: 报告 + 落地 golden-safe 修复(验证层 eval 产物, 不触面板/golden); 触面板列的仅报告。

> ⚠ 口径前提(贯穿全文): 三套人工标注工作簿**当前全部空白**(见 memory `human-annotation-pending-2026-06-13`), 故本审核判定的是**"填表后指标算得对不对 + 披露守卫够不够诚实"**, 而非空表本身。所有"伪人工验证"(轨/源/模型/prompt 自比的 κ/α)按项目既定立场属可接受稳健性, 仅要求标注清楚不得冒充人工编码者间信度。

---

## 0. 执行摘要

- 原始发现 **54** 条 → 经三人对抗证伪存活 **45** 条, 证伪/确认无缺陷 **9** 条。
- 大量重复(≈7 条都指向"缺置信区间", ≈4 条指向 Krippendorff α 实现), 去重后 = **约 20 个独立问题**。
- **真 P1(顶刊审稿可阻断, ≥2 lens 一致)**: 5 个 — 全在人工金标准设计层(非盲编码 / 单编码者回退 / 创新维度无信度 / 过采样未加权 / 收敛效度冒充构念效度)+ 缺置信区间。
- **争议 P1→实为 P2**(单一 factual lens 报 P1, 另两 lens 因已有披露/已有 Romano-Wolf 降为 P2): FLS 门控、多重比较校正、单指标 HTMT。
- **代码统计核心整体清白**: Cohen κ(混淆矩阵式)、radius/轨间 2-cat κ(且已带 bootstrap CI)、`merge_three_rater_majority`(≥2 多数票, 无 coder1 偏置)、`cross_media_alpha` α 取向/NaN 策略 — 均经对抗证伪确认**正确**, 勿误改。
- **本轮已落地 5 处 golden-safe 修复**(下文 §2), 定向测试 + 相关回归全绿(exit 0), ruff clean。

### 白话
真正需要真人动手的"考卷"(三套标注表)现在还都空着, 所以这次查的是"等真人填完了, 阅卷程序算分对不对、有没有把'机器自己跟自己比'吹成'人工验证'"。结论: **算分的数学内核是干净的**(κ、相关系数那些公式都对); 真正的硬伤集中在**给编码者发的考卷上印了 AI 的答案(非盲)、缺第二个人时偷偷拿一个人的当标准答案、给的分数没配误差棒(置信区间)**。这些里能安全就地改的(给准确率配误差棒、小样本换精确检验、单编码者时报警并禁止吹"双人共识"等)我已经改好并测过了; 改了会动面板数值的(要重算 golden 的)只写进报告等你定。

---

## 1. 已落地修复(golden-safe, 已测) — `validation/llms_evaluation.py`

> 全部为 validation 层 eval_reports 产物计算逻辑, **不触任何面板/golden 列**; 多为 additive(新增键/字段), 向后兼容。定向测试见 `tests/test_measurement_validation_audit_fixes.py`(新建), 回归覆盖 `test_33_evaluation` / `test_human_verification_readback` / `test_omni_fix_val_eval` / `test_35` / `test_39` 全绿。

| # | 修复 | 位置 | 标准依据 | 性质 |
|---|------|------|---------|------|
| **F1** | McNemar: 分歧样本 `b+c<25` 改用**精确二项检验**(scipy `binomtest`, 无 scipy 手算两侧精确 p), 大样本沿用连续性校正卡方; 新增 `test_type` 字段 | `compute_mcnemar_test` | 小样本卡方近似不可靠是统计常识 | 改小样本 p 值(更正确), 大样本不变 |
| **F2** | Krippendorff α: `D_e` 仅基于**可配对单元**(m_u≥2)取值, 与 `D_o` 同口径(原实现把单编码者单元也计入 D_e, 偏离 Krippendorff 2004) | `compute_krippendorffs_alpha` | Krippendorff (2004) 定义性质: 单编码者单元对 α 零贡献 | 完整数据下逐位一致; 仅缺标时修正 |
| **F3** | Cohen κ 95% CI **截断至 [-1,1]** + 新增 `κ_CI方法` 字段诚实标注"渐近近似(Fleiss 简化 SE); 建议 bootstrap" | std_report(验证+情感双任务) | κ∈[-1,1], 正态 CI 在 κ→±1 时越界 | 仅修边界越界 |
| **F4** | `accuracy` 附 **Wilson score 95% CI**(新增 `accuracy_ci` 键, 复用本仓 `dict_coverage.wilson_ci` 同式) | `compute_classification_metrics` | 顶刊要求验证统计量附不确定性, 非裸点估计 | additive, 不改既有键 |
| **F5** | 单编码者金标准回退**显式告警 + 记录 `gold_source`**(two_coder_consensus/single_coder_A/demo); 并**门控**"双编码者共识"方法学表述(单编码者时改打诚实模板) | gold 提取 + std_report + 论文表述段 | 误报双编码者共识是 misreporting hazard | 仅加告警/字段/门控 |

---

## 2. 待办清单(按主题去重; 含精确补丁与状态)

### T-C 人工金标准设计 ★最关键★

| ID | 严重度 | 问题 | 补丁(全部 golden-safe, 验证层) | 状态 |
|----|--------|------|------|------|
| `non-blind-rater-workbook-leaks-llm-labels` | **P1**(3/3) | 发给编码者的工作簿带 LLM 自身答案: `manual_validation_sampling.py:155-168` 的 `v7ref_*` 列 + `stratum`(由 LLM 预测定义); `llms_human.py:145` 的 `other_cols` 把 21_tone_llms 的 `llm_*` 预测列也一并写入; `tone_validation.generate_validation_sample` 工作台含 `词典_/BERT_/LLM_` 方法列。**非盲编码 → 锚定/自动化偏误, 机械抬高 κ 与准确率**。前缀 `v7ref_` 与行 shuffle 不是 blinding。 | 编码者面向 sheet **只保留文本 + 人工填写列**; 把机器标签移到分析者持有的独立 keyed reconciliation 文件/隐藏 sheet, 回读端按 docid join。三处生成器同步改, 不改任何面板值。 | DEFER(改人工产物 schema, 需配套改回读 join + 测试) |
| `silent-single-coder-gold-fallback` | P1→部分已缓解 | 缺 `最终_验证` 共识列时静默回退编码者A单人作金标准, 仍打"双编码者共识"表述 | — | ✅**已落地 F5** |
| `majority-vote-discards-percoder-reliability` | **P1**(3/3) | `merge_three_rater_majority` 先把 R1/R2/R3 折叠成多数票 gold, 创新维度(实质性/落点)**永不报 κ/α**; 注释把它甩给已删除的 study-plan 工作流 → 结构性缺人工金标准信度。`compute_krippendorffs_alpha` 本身支持 ≥3 编码者却没被接上。 | 折叠**之前**对原始 R1/R2/R3 矩阵算 3 编码者 Krippendorff α, 写入 `inter_coder_reliability['innovation_*']`(空表时 pending)。原始列已在工作簿, 仅加 eval 输出。 | DEFER(additive, 低风险, 推荐尽快落地) |
| `innovation-panels-ignore-population-weight` | **P1**(3/3) | `manual_validation_sampling.py:126-133` 为撤销过采样算了 `population_weight`, 但 `_evaluate_innovation_panels` 调 `compute_classification_metrics` **从不传 sample_weight** → Panel E/F 是样本内未加权指标, 既非总体代表也未标注 stratum-conditional。`population_weight` 是死列。 | 把 `population_weight` 作 `sample_weight` 传入 sklearn(accuracy/PRF 均支持)报总体加权指标; 或显式标注"stratum-conditional, 不可外推总体"。 | DEFER(机械改, 需 `compute_classification_metrics` 加 `sample_weight` 形参) |
| `disagreement-attrition-not-bounded` | P2 | 分歧/待仲裁行从准确率分母剔除(已正确且已披露), 但 attrition 率未报告/未设上限 | eval 报告补 attrition 比例字段 | DEFER |

### T-A 置信区间体系

- ✅**已落地**: accuracy Wilson CI(F4)、κ CI 截断(F3)、McNemar 小样本精确(F1)。
- **DEFER**(`no-ci-on-accuracy-or-f1` 残余 / `no-ci-on-alpha-fleiss-crossmedia` / `kappa-ci-*-no-bootstrap`, P1): 为 **macro-F1 / per-class F1 / Krippendorff α / Fleiss κ** 加 **nonparametric bootstrap CI**(配对重抽 2000 次百分位)。建议提取通用 `bootstrap_ci` 工具(`inter_track_kappa._compute_kappa_with_bootstrap` 已是模板), 接入各 eval 输出。golden-safe。

### T-B Krippendorff α 实现一致性
- ✅**已落地** F2(D_e 可配对单元修正)。
- 已澄清(无需改): `cross_media_alpha` 用 `krippendorff` 库且 α 取向(outlet×day=raters×items)/NaN 策略**正确**; `krippendorff-nonstandard-Do-normalization` 经核 = **假阳性**(D_o 按 Σm_u 归一化是标准式)。
- 可选(P2): 统一全仓改用 `krippendorff` 库以消除手写实现维护风险。

### T-D 构念效度框架 · 诚实标注

| ID | 严重度 | 问题 | 补丁 | 状态 |
|----|--------|------|------|------|
| `convergent-vs-criterion-conflation` | P1(overclaim) | `tone_validation.main` 把跨方法 Cronbach α / Spearman ρ 称"构念效度(Construct Validity)符合顶级期刊标准", 而 criterion 效度(vs 人工)恒 pending → 实际只产出**收敛效度**(方法间一致) | 措辞改为"收敛效度(convergent, 方法间趋同); criterion 效度待人工标注"; 日志/报告同步 | DEFER(措辞/披露, 低风险) |
| `single-indicator-htmt-vacuous` | P2(3/3) | 每构念单指标 → HTMT 退化 = `|corr|`, `AVE=1.0` by fiat, Fornell-Larcker 平凡满足。已在 docstring 披露, 但 `39d_htmt_matrix.json` 仍发 `htmt_verdict:strict_pass`/`AVE=1.0` 无单指标 caveat | 产物/Stata 模板加 `single_item=true` caveat, 主打 permutation-null(本身有效)而非 HTMT 通过/失败 | DEFER(标注) |
| `inter-track-kappa-csv` / `cross-media-alpha` / `prompt-fleiss` | P2 | 机器自比一致性(轨/源/prompt 变体)输出未在 CSV/TeX 列头显式标注"非人工 ICR" | 各 eval 输出加一列/脚注"机器自比一致性, 非人工编码者间信度" | DEFER(披露) |

### T-E 稳健性体系完整性

| ID | 共识严重度 | 问题 | 补丁 | 状态 |
|----|--------|------|------|------|
| `radius-llm-notimplemented-phantom` | P1 | `radius_sensitivity_llm.py:181` `parse_track_results_from_cache` raise NotImplementedError, `--launch` 仅 scaffold, 但 TableA4 宣称该稳健性 | 诚实标注 not-run(eval 写"未执行")或剪除 TableA4 宣称; 真实现需付费 LLM 重跑(超本轮范围) | DEFER(诚实标注) |
| `fls-ga2-precision-gate-unenforced` | P1→**P2 争议** | FLS 文档承诺"500 句人工标注 precision≥0.80"门控但无实现/无 artifact; `frac_fls` 无条件入面板。**但** docstring 已标 USER_ACTION_REQUIRED(2/3 lens 据此降 P2) | 把 pending 披露**传播到** `variable_codebook` 与 .dta 列标签(现仅 docstring 有); 不改 `frac_fls` 值(改值非 golden-safe) | DEFER(披露传播) |
| `no-multiple-comparisons-correction` | P1→**P2 争议** | radius 配对 t 检验族(`radius_sensitivity.py:657-695`)数显著个数无 FDR; κ/α 门控无联合错误率。**但** paper 主表已强制 Romano-Wolf(`runner.py:997`), κ 门控本是描述性 | radius t 族加 BH-FDR + 报校正后计数; 各报告显式标 κ/α 门控为描述性(Landis-Koch)非推断 | DEFER(可落地, additive) |
| `no-temporal-lookahead-robustness` | P1(conf 中) | stage 38a temporal_mask_test 已于 2026-06-12 移除后, battery 无前视/look-ahead 检验; 而 `frac_fls` 是显式前瞻测度 | 重加轻量 as-of 检验, 或在稳健性节文档化"文本日期严格早于结果年, 前视由构造排除" | REPORT(需用户定是否重加阶段) |

### T-F 代码边界(P2, 多为披露/防御)
- `verification-macro-degenerate-allones-gold`: 验证 gold 全 1 时规则分类器 macro-F1 退化 → 加 disclosure。
- `verification-nan-imputed-to-false`: NaN 验证预测被填 False → 复核语义。
- `ok-status-zero-methods-scored`: 0 方法被打分时 status 仍 'ok' → 改 'insufficient'。
- `macro-f1-over-absent-classes-undisclosed`: `zero_division=0` 使无支持类拉低 macro-F1, 未披露。
- `mangled-dup-false-positive-silent-drop`: `_is_mangled_dup` 仅当基名也在列集才删, 风险低(实测较安全), 监控即可。
- `innovation-panel-csv-no-demo-guard`: 创新 Panel CSV 缺 `_DEMO` 标记(验证/情感有)。
- `threshold-plotpr-empty-list-vacuous-true`: `_plot_pr_curve` `all([])==True` 空列表会 KeyError(永不喂空 → 潜伏); 防御性加空检查。

### T-G 面板触及 → **NOT golden-safe, 仅报告**
- `cmalpha-derived-tone-overwrites-and-equal-weight-panel`(P2): `cross_media_alpha` 把 3 点序数 tone(`{正面:1,中性:0,负面:-1}`)当 **interval** 尺度算 α(`level_of_measurement='interval'`), 并写 6 个面板列(`39f_cross_media_alpha.parquet` → 面板/golden)。建议: 披露"3 点序数当 interval"局限 + 可选报 nominal α 敏感性; **改编码/加权须重生 golden**, 本轮不动。(注: cell-mean 使多文章日实际连续, 削弱了该批评。)
- `sampling-frame-is-1170-pilot`(P1, 速率限制掉队已复核): 验证样本抽自 1170 篇**试跑**语料而非全量分析语料(见 memory `fullcorpus-17M-T18-not-T2`)。全量 run 时须从分析语料重抽, 并在输出披露抽样框。

---

## 3. 经对抗证伪确认**无缺陷**(clean, 勿误改)
- `compute_cohens_kappa`(混淆矩阵式, 含 p_e=1 / n<2 退化守卫)— **正确**。
- `radius_sensitivity_llm.cohens_kappa_2cat` + `inter_track_kappa._compute_kappa_with_bootstrap`(已带 NaN-aware bootstrap CI)— **正确**。
- `merge_three_rater_majority`(≥2 多数票, 0/1 有效与平局均 None, **不**偷取 coder1)— **正确**。
- `cross_media_alpha.compute_variance_and_alpha`(α 取向 outlet×day、NaN 策略、α-returns-NaN 披露)— **正确/诚实**。
- `krippendorff-nonstandard-Do-normalization`、`docstring-threshold-citation-mismatch`、`pseudo-validation-labeled-honestly` — **假阳性/已诚实**。

## 4. 速率限制掉队、需后续复核(非证伪)
- `masking-permodel-vs-aggregate-denominator-mismatch`(`entity_masking.py`): per-model 一致性用 `df_result`(notna 过滤)而 aggregate 用 per-protocol fail-mask on `df_valid` — 同报告内两个分母, 疑似不一致, **3 个 lens 均因 session limit 未跑**, 需人工复核确认是否真缺陷。

## 5. 文献锚点(投稿前须 [verify] DOI/页码 — 本项目有误引史)
Wilson 1927 JASA · Fleiss/Cohen/Everitt 1969(κ SE)· Krippendorff 2004/2018 · Hayes & Krippendorff 2007 · Byrt-Bishop-Carlin 1993(PABAK)· Henseler-Ringle-Sarstedt 2015 JAMS(HTMT)· Fornell-Larcker 1981 JMR · Benjamini-Hochberg 1995 · Romano-Wolf 2005 · Manski-Lerman 1977 ECMA(choice-based 加权)· Carlson & Burbano 2026 SMJ(LLM 标注报告)· Li 2010 JAR / Bozanic-Roulstone-Van Buskirk 2018 RAST(FLS)· Tetlock 2007 JF / Tetlock-Saar-Tsechansky-Macskassy 2008 JF。

---

## 6. 大白话总结
1. **干净的部分**: 所有"算一致性、算准确率"的数学公式本身没错(经反复对抗检验)。
2. **已经帮你修好的(改了不影响最终面板数据, 已测)**: ①小样本时改用更靠谱的精确检验; ②一个一致性系数(α)在有人漏标时算得更标准; ③准确率/κ 现在都带"误差范围"且不会超出合理区间; ④只有一个人评分时会报警并禁止程序吹成"两个人达成共识"。
3. **还需要你拍板/后续做的(多数是"等填表前先改好发卷子的方式"或"措辞别夸大")**: 最重要的是**别让打分的人看到 AI 的答案**(否则验证不算数)、**给创新维度也报一个三人一致性**、**把过采样的权重真正用上**、给更多指标配 bootstrap 误差棒。
4. **会动到面板数据、必须重算 golden 才能改的**: 跨媒体 α 的尺度处理、验证样本要从全量语料(不是试跑的 1170 篇)重抽 — 这些只写进报告, 等你决定。

---

## 附录 A · 5 个真 P1 专项复核裁决(2026-06-13 第二轮, 主控亲读代码逐条核)

> 由主控直接读引用代码逐行核(比再派 agent 读同样行更可靠)。每条给: 事实裁决 / 定级校正 / 处置。

| P1 | 事实裁决(读真代码) | 校正 | 处置 |
|----|------|------|------|
| **①非盲编码** `non-blind-rater-workbook-leaks-llm-labels` | **CONFIRMED**。`manual_validation_sampling.py:155-168` 把 `v7ref_*`+`stratum`(由 LLM 预测定义)写入编码者表; `llms_human.py:145-148` 的 `other_cols` 把 21_tone_llms 的 `llm_*` 预测列写入 32_human_samples; `tone_validation.generate_validation_sample` 工作台含 `词典_/BERT_/LLM_` 方法列。三套表全中。**关键事实**: stage 33/创新评估的 y_pred 实际来自 `21_tone_llms.parquet` 的 docid join, **不读工作簿里的机器列** → 32_human_samples 与 manual_validation 的机器列纯属"给编码者看的参考", 删掉对评分无影响。stage 34 回读则**确从工作簿读** `词典_/BERT_/LLM_` 列, 需 sheet 拆分。 | 维持 **P1** | **DEFER(改人工产物 schema, 需用户确认)**: 编码者面向 sheet 只留文本+人工列; 机器列移到分析者持有的独立 keyed 文件(stage32/创新, 安全直删)或独立 sheet(stage34, 回读改读该 sheet)。改的是空工作簿, 不动面板, 但改变发给真人的考卷格式, 须你拍板后落地。 |
| **②创新维度无信度** `majority-vote-discards-percoder-reliability` | **CONFIRMED**。`merge_three_rater_majority` 折叠后原始三编码者向量未保留; `_evaluate_innovation_panels` 仅消费折叠 gold 算分类指标, 全程无 κ/α; ICR dict 刻意只 2 键(R27B-02 测试锁)并把创新信度甩给已删工作流。`compute_krippendorffs_alpha` 本支持 ≥3 编码者却没接上。 | 维持 **P1** | ✅**已落地**: 折叠前对原始 R1/R2/R3 建 (3×n) 矩阵算 Krippendorff α, 存入**独立键** `results['innovation_inter_coder_reliability']`(不碰 2-键不变量)。空表→pending。新测试验证: 有分歧时 α<1, 全一致 α=1.0。 |
| **③过采样未加权** `innovation-panels-ignore-population-weight` | **CONFIRMED(机制需更正)**。`population_weight` 算了(`sampling.py:128-133`)但 `compute_classification_metrics(898)` 从不传 sample_weight。⚠更正: 实盘**稀有层 C/D/E 被普查(weight≈1), 反而众数层 A/B 被过权(8.01/3.21)** — "稀有类放大5x"的叙事错, 但"未加权≠总体代表、权重列是死的"结论成立。 | 维持 **P1** | ✅**已落地**: 创新评估处附**精确总体加权 accuracy** `accuracy_weighted_corpus`(Σw·correct/Σw)+ `accuracy_note` 标注两者口径(未加权=stratum-conditional/加权=总体)。不改 `compute_classification_metrics` 签名、不碰 CI。新测试验证加权(3/13)≠未加权(0.75)。 |
| **④收敛冒充构念效度** `convergent-vs-criterion-conflation` | **CONFIRMED**。`tone_validation.py:1890-1891` 日志称跨方法 Cronbach α/Spearman ρ"确保构建效度符合顶级期刊标准", 而效标效度(vs 人工)恒 pending。 | P1(overclaim) | ✅**已落地**: 日志+模块 docstring 改为明确"本阶段=收敛效度(方法间趋同); 效标效度由人工回读/stage33 提供, 未填表 pending; 不得仅凭方法间一致宣称构念效度达标"。 |
| **⑤缺置信区间** `no-ci-*` 族 | **CONFIRMED(部分已解)**。 | P1 | ✅**已落地一半**: accuracy Wilson CI(F4)+ κ CI 截断[-1,1](F3)。**残余 DEFER**: macro-F1/per-class F1/Krippendorff α/Fleiss κ 的 bootstrap CI(提取通用 `bootstrap_ci` 工具, `inter_track_kappa._compute_kappa_with_bootstrap` 是模板)。additive/golden-safe, 可后续落地。 |

**本轮 P1 复核净结果**: 5 条 P1 **全部事实属实**(③的发生机制叙事需更正但结论成立); 其中 **②③④ 已就地落地修复**(全 golden-safe/additive, 定向测试 + 全部相关回归绿, ruff clean); **①** 因改人工考卷格式须用户确认后落地; **⑤** 已落地一半, 残余 bootstrap CI 为 additive 后续项。新增/扩展测试集中在 `tests/test_measurement_validation_audit_fixes.py`。**全部未提交**。

---

## 附录 B · 对"已落地修复"的再复核(第三轮: 数值对拍 + 对抗 diff 复核)

> 用户要求对修复本身"万无一失"。两路独立验证。

**B.1 数值对拍**(把我的实现 vs 权威参考逐用例比对, 一次性脚本跑后即删):
- F2 `compute_krippendorffs_alpha` **vs `krippendorff` 库 (nominal)**: 400 随机矩阵(含缺标)**0 不一致**; 完整数据 vs 旧实现 2000 例**逐位一致**(证实"完整数据不变"); 单编码者单元不变性 a0==a1 成立。→ **D_e 修复经权威实现确证为 canonical 正确**。
- F1 McNemar 精确手算回退 **vs `scipy.stats.binomtest`**: 全部 b+c<25 用例 max 误差 1.1e-16; 分支选择(<25 精确 / ≥25 卡方)正确。
- F4 accuracy Wilson CI **vs scipy `binomtest.proportion_ci(wilson)`**: 200 用例 0 不一致。
- P1-3 加权 accuracy **vs `np.average(weights=)`**: 一致。

**B.2 对抗 diff 复核**(5-agent 工作流, 各 slice 力图"击穿"修复): 4 个 slice **3 clean + 1 minor-issues**, 综合裁决 **0 blocker / 0 bug**。逐项确认: F1 b==c 与边界 b+c=25、F2 dead-code `n_total<2` 守卫(不可达但无害)、F3 clip-先-round 不会越界 [-1,1]、F4 新键不进 `classification_eval_summary.csv`/LaTeX 列(不破列数)、P1-2 矩阵取向(coders×items 非转置)+ 2-键不变量保持、P1-3 mask 对齐/suffix 不改名、F5 `gold_source` 全路径已定义(无 UnboundLocalError)+ boilerplate 门控顺序正确。**golden-safety 经 grep 确认**: `runner.py` 不 import 这些 compute_* / 模块, 8 处改动均仅落 eval_reports, 不触 40_panel/golden。

**B.3 据复核落地 2 处防御性硬化**(均 golden-safe, 新增 2 定向测试):
- **demo 误标**: demo 模式下 `_generate_demo_data` 填了 `最终_验证` → verification 分支把 `gold_source_ver` 误标 `two_coder_consensus`(与 `数据模式=模拟数据` 自相矛盾)。修: demo 时 `gold_source_ver/sen` 一律 `demo_synthetic`。(非阻断: 产物已带 `_DEMO` 后缀且方法学表述被 `demo_mode` 门控抑制, 仅 CSV 一字段。)
- **加权 accuracy 防御**: 仅当 `population_weight` 全部有限且非负时才计 `accuracy_weighted_corpus`, 否则置 None + note(防 partial-NaN 静默分叉 / 负权重越界 [0,1])。生产权重恒 >0, 此为防工作簿被手改。

**第三轮净结果**: 8 处落地修复**统计内核经权威实现确证 + 对抗复核 0 bug/0 blocker + golden-safety 确认**; 又据复核补 2 处防御硬化。测试全绿、cross-check 0 不一致、ruff clean。**仍全部未提交**。
