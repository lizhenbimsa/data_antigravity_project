# 致命问题审计整改执行计划 (2026-07-10, R1 评审已整改)

> 来源: 两轮多智能体对抗审计 (32 finder 单元 + 双透镜验证) + 独立 fast 测试线 + 亲自逐行复核。
> **R1 评审整改** (6 维度对抗评审, 2026-07-11): F1 safe=False→safe=True + 收窄 except; F8 扩 allow-list 覆盖 fintech_intensity_score/llm_prob_score 两族且须实跑转绿; F4 钉死 flag 契约 + gate; defer 段 cohort/fast 红事实订正。F2/F3/F5/F7 经多维实证 SHIP-AS-PLANNED。
> **R2/R3 结果评审** (18-agent 对抗式逐-fix diff 评审 + 字节 A/B + 通读, 2026-07-11): 7 fix × 5 维对抗校验 + 疑虑第二 lens 独立复核。**唯一 confirmed concern = F1 P2** (premise-only 测试只锁 pyarrow cast 语义、不覆盖 runner 集成路径, 回退 try/except 仍全绿) → **已闭环**: 补 `test_f1_preprocess_schema_divergence_no_crash` (列集分歧 + 同步 executor 驱动真 `load_and_process_data`, 锁不崩+跳源对账)。F2/F3/F4/F5/F7/F8 零 confirmed (NIT 均被反驳)。F3 字节 A/B 实证 SHA256 恒等 (aa9a6c27, 8 对 0 孤儿)。golden gate 14 阶段红全属盘上 parquet-vs-冻结 golden 慢性陈旧, 本会话重生零 parquet → 逐字节独立于本 diff。
> 硬约束: **golden 确定性铁律** (CLAUDE.md「确定性/golden」段)。ship-now 项必须在 T=2 上按构造字节不变; 改测度列的一律 defer。本机 data/raw 空、T=2 dev、不可本地重生 golden。

## 判据分类总表

| ID | finding | 严重度 | 处置 | R1 裁决 |
|----|---------|--------|------|---------|
| F1 | preprocess ParquetWriter schema 崩 | 🔴CRITICAL | **SHIP** (safe=True 修订) + defer F1b 根治 | SHIP-WITH-REVISION |
| F2 | clarity 图缺列崩 | 🟠HIGH | **SHIP** | SHIP-AS-PLANNED (三维证真修复) |
| F3 | network per-year 单边孤儿 | 🟠MEDIUM | **SHIP** | SHIP-AS-PLANNED (SHA256 恒等 no-op) |
| F4 | 编排器日志先于锁截断 | 🟠MEDIUM | **SHIP** (钉契约+gate) | SHIP-WITH-REVISION |
| F5 | regen 驱动漏跑 stage 51 | 🟡MEDIUM | **SHIP** | SHIP-AS-PLANNED |
| F7 | strat_diff 值域桶错分 | 🟡LOW | **SHIP** | SHIP-AS-PLANNED |
| F8 | fast: dual_track allow-list 漂移 | (测试) | **SHIP** (扩两族+实跑转绿) | SHIP-WITH-REVISION |
| F6 | tone_llms innovation confidence 漏门控 | 🟡LOW休眠 | **DEFER** | 改测度列→golden, 休眠不急 |
| F1b | preprocess 标识列归 string 根治 | (F1 根治) | **DEFER** (impl 时按 test_00 复核可否提前) | 改 docid dtype→golden; 与 F1 同生产窗口 |
| — | fast: cohort (2红) | (测试) | **DEFER/调查** | 模块导出 110 家、CSV 缺失 |
| — | fast: jieba/codebook order-flaky (最多3红) | (测试卫生) | **DEFER** | 全局态泄漏, 隔离过; 生产子进程隔离安全 |

---

## F1 🔴 CRITICAL — stage 00 预处理 ParquetWriter schema 崩溃 (生产首跑阻断)

**文件**: `pipeline/preprocess/runner.py:348-356`
**根因** (亲自逐行确认): `pa.Table.from_pandas`(350)+`pq.ParquetWriter(output_path, table.schema)`(351-354, 首个完成 worker 永久锁 schema)+`writer.write_table(table)`(355) 全在 try/except 之外。`load.py:500-503` dtype 归一是 `if dtype=='object'` (仅 object→str) 放过数值列。盘上 `00_preprocessing.parquet` 实测 **`docid: int64`** + 12 列 string → T=18 多源语料下 `docid`/`页号`/`pubcode` 跨文件 int64↔float64(含缺失)↔string 分歧 → 首 worker 锁定某 dtype 后, 分歧文件 `write_table` 抛未捕获 `ValueError` → 冒泡出 `main()` → **DAG 根阶段硬崩**。崩不崩取决于 `as_completed` 完成顺序 (非确定)。T=2 单源同构永不触发。

**SHIP 修复 (字节安全网, R1 修订: safe=True + 收窄 except)**:

```python
# 当前 (348-356):
                if df_cleaned is not None and not df_cleaned.empty:
                    source_rows[file_name] = source_rows.get(file_name, 0) + len(df_cleaned)
                    table = pa.Table.from_pandas(df_cleaned)
                    if writer is None:
                        writer = pq.ParquetWriter(output_path, table.schema, compression='snappy')
                    writer.write_table(table)
                    total_rows += len(df_cleaned)

# 改为:
                if df_cleaned is not None and not df_cleaned.empty:
                    table = pa.Table.from_pandas(df_cleaned)
                    try:
                        if writer is None:
                            writer = pq.ParquetWriter(output_path, table.schema, compression='snappy')
                        elif table.schema != writer.schema:
                            # 多源 dtype 推断分歧 (docid int64↔float64↔str 等): 对齐到已锁 schema。
                            # safe=True (默认): 有损/越界 cast (fractional float→int / string→int) raise→
                            # failed_files 对账; NaN→null 与无损加宽 (int→float/int→string) 仍成功写入。
                            # 绝不 nuke 根阶段 (审计 F1)。⚠ 首 writer 锁哪个 dtype 由 as_completed 完成序
                            # 决定 → T=18 跨次可产出不同 (int64 null vs float64); 该非确定性由 F1b (标识列
                            # 归 string) 根治, F1(本项)与 F1b 须同生产窗口落地, 前者仅作防崩安全网。
                            table = table.cast(writer.schema)
                        writer.write_table(table)
                    except (pa.ArrowInvalid, pa.ArrowTypeError, pa.ArrowNotImplementedError, ValueError) as e:
                        # 仅接 schema/cast 类异常; 真正的 I/O 写失败 (磁盘满/权限) 不在此列 → 仍 fail-loud。
                        logger.error(f"schema 不兼容, 跳过 {file_name} (计入 failed_files 对账): {e}")
                        failed_files.append((file_name, f"schema mismatch: {e}"))
                        source_rows.setdefault(file_name, 0)
                        continue
                    source_rows[file_name] = source_rows.get(file_name, 0) + len(df_cleaned)
                    total_rows += len(df_cleaned)
```

**golden-safety 证明** (R1 golden-safety-breaker 实证): T=2 单源 → 所有 df_cleaned 同 schema (`schema ==` 忽略 pandas metadata) → 首文件建 writer, 后续 `table.schema == writer.schema` → 不进 cast → `writer.write_table(table)` 逐字节等价; try/except T=2 永不触发。本机 data/raw 空 → Step-2 循环根本不进。`source_rows` 计数移到成功写后 (语义: 只统计真写入行), T=2 无失败 → 一致。
**诚实披露** (R1 fix-correctness 更正 + R2 精化): 本安全网把「崩」换成: (a) 有损 cast (fractional/含空串或非数字 string→int) 或列集不匹配 → raise → failed_files 对账 (整源文件被跳, 生产可达百万行, 有 logger.error+sidecar); (b) 无损分歧 (float64 含 NaN ↔ int64) → NaN→null **被写入** (非 skip); (c) 锁定 dtype 方向由 worker 完成序决定 → T=18 跨次非确定。**(b)(c) 由 F1b 根治**。
- ⚠ **R2 NIT (b) load-bearing 前提**: 「NaN→null 写入」依赖 `pa.Table.from_pandas` 的 null-masking (NaN→arrow-null); 裸 `pa.array([...NaN...]).cast(int64)` (NaN-valued 非 null-masked) 会 **RAISE**。当前路径 (df_cleaned→from_pandas→cast) 恰走 null-mask 分支; 未来若以产 NaN-valued 数组的路径重构, 该分支会静默变「raise→整源文件落 failed_files」(数据丢失)。注释须点明此前提。
- ⚠ **R2 硬门 (升级)**: 「F1+F1b 同生产窗口落地」从指引升为**硬发布门** (F1 不得单独 ship 到 T=18 窗口而缺 F1b); 首次生产重生建议 `NEWS_PROCESS_STRICT_SOURCES=1` 默认令丢源 fail-loud 而非静默 reconcile。
**测试影响**: `test_00_preprocessing.py` 无 docid/dtype/schema/ParquetWriter 断言 (grep 零命中) → 零影响。
**验证** (R2 confirmed P2 闭环): ① `test_f1_cast_safety_net_premises` 锁 pyarrow cast 三语义原语 (防升级漂移); ② **R2/R3 补** `test_f1_preprocess_schema_divergence_no_crash` — 列集分歧两源 (a=2列/b=3列, cast 双向皆 ValueError → 中和 as_completed 完成序非确定, total 恒=2) + 同步 executor 替换 ProcessPool (Windows spawn 下跨进程 monkeypatch 失效) 驱动真 `load_and_process_data`, 断言不崩根阶段 + 分歧源被跳 + `source_reconciliation.json` 计入 failed_files/zero_contribution。回退 runner try/except → ValueError 冒泡即变红 (锁住 premise 测遗漏的集成路径)。

**DEFER 根治 (F1b)**: `load.py` 把标识列 (docid 等数值推断列) cast string → 跨文件 schema 恒同、零文件跳、消除非确定。下游 `raw_census.py:152-157` 本就 `astype(str)` → 语义无害。改 T=2 docid dtype (int64→string) → 改 stage00 golden。**impl 时先查 test_00_preprocessing 是否 byte-compare stage00 输出**: 若否 (仅逻辑/计数断言) 且不本地重生 → 可与 F1 一并 ship (代码改、盘上 parquet 不变、生产窗口重生时 golden 自洽); 若 test_00 byte-compare → defer 到生产窗口。R2 评审据此定夺。

---

## F2 🟠 HIGH — clarity 分布图缺列崩溃 + 假安全注释 (SHIP-AS-PLANNED)

**文件**: `papers/bank_news_clarity/figures.py:46-48`
**根因** (亲自确认): `columns=[mean_clarity_score_{full,ctx,ss}]` 透传给 `pd.read_parquet`; docstring 谎称 skip-if-missing。缺列时 L46 先抛 `ArrowInvalid` (非 FileNotFoundError), `analysis.py:69` 只捕 FileNotFoundError → CLI 崩。兄弟图 `bank_media_disagreement/figures.py:48-52` 有正确写法。

**SHIP 修复** — 去 `columns=` 整盘加载 (镜像兄弟图):
```python
    # 不传 columns= 过滤: pd.read_parquet 对缺列 raise ArrowInvalid (逃逸 analysis.py 的 except),
    # ss 轨在 P4 付费 run 前盘上必缺 — 整盘加载后用 `col in panel.columns` skip-if-missing 才兑现
    # docstring 承诺 (审计 F2, 镜像 bank_media_disagreement)。
    panel = load_panel('40_panel_yearly.parquet', paper_id=pc.paper_id, project_config=pc.config)
```
**R1 三维实证**: `panel_loader.py:79` 仅文件不存在时 raise FileNotFoundError (被 analysis.py:69 捕获); `figures.py:54` skip-if-missing 生效; 全盘加载仍只画三列 → 图像等价; 无残余异常逃逸。图表产物不入 golden。
**验证**: 从缺 `mean_clarity_score_ss` 的 mock 面板调 `plot_clarity_distribution`, 断言不抛、正常出图。

---

## F3 🟠 MEDIUM — co-primary 嵌入 per-year 单边孤儿 (SHIP-AS-PLANNED)

**文件**: `pipeline/panel/network_spillover.py`
**根因** (亲自确认): both-or-neither 守卫是 pass 级 `main_ok = bool(emb_results)` (2143-2144), 只在整遍 pass 空时对称置 NaN; per-year 单侧 miss → 单边孤儿。

**SHIP 修复** — 加行级 parity helper, 在 return 前调:
```python
def _enforce_row_parity(panel):
    """行级 both-or-neither 补强 (审计 F3): 对每对 (canonical, _lg) 嵌入网络列, 任一 NaN → 两列同置 NaN。"""
    net_lg = [c for c in panel.columns if '_lg' in c and ('emb_peer_tone' in c or 'bank_emb_sim' in c)]
    for lgc in net_lg:
        can = re.sub(r'_lg(?=_|$)', '', lgc, count=1)  # 边界感知单次剥离 (R1 NIT 采纳; 当前 8 列与 .replace 等价)
        if can in panel.columns:
            orphan = panel[can].isna() ^ panel[lgc].isna()
            if orphan.any():
                logger.warning(f"  行级 parity 补强: {can}/{lgc} {int(orphan.sum())} 单边孤儿 → 同置 NaN")
                panel.loc[orphan, [can, lgc]] = np.nan
    return panel
```
- 调用点: `compute_embedding_peer_network` 的 2152 早退 + 2213 正常 return 前各插 `panel = _enforce_row_parity(panel)`。
- **R1 note**: 第三个 return (2104, `llm_vote_tone_full not in panel.columns` 降级) 在任何 emb 列 merge 之前, net_lg 为空 → helper 天然 no-op, 无需插入 (无缺口)。

**golden-safety 证明** (R1 golden-safety-breaker 独立实证): 把 helper 应用于盘上全 40 面板 → 全表 **SHA256 恒等 aa9a6c27…**, 列序/dtype/`DataFrame.equals` 全保, orphan 告警未触发 (8 对 canonical/_lg NaN 完全同构, 单边孤儿=0)。`.replace('_lg','')` 对当前 8 列各 `_lg` 恰 1 次 → 配对全正确 (R1 F3-pairing-deep 逐列实测)。
**R1 future-proof NIT (非阻塞)**: `.replace('_lg','')` 是全替换无边界; 当前列集安全, 但为防未来 `_lg`-邻接命名, 可选用 `re.sub(r'_lg(?=_|$)', '', lgc, count=1)`。**采纳**: 落地时用边界感知单次剥离 (等价当前行为 + 未来鲁棒)。
**验证**: 新增 `test_network_row_parity` (含孤儿输入被对称清 NaN; 无孤儿输入 no-op)。

---

## F4 🟠 MEDIUM — 编排器日志先于锁截断 (SHIP-WITH-REVISION, finding 建议已更正)

**文件**: `run_pipeline_function.py:622` + `run_pipeline_validation.py:180` + `core/locking.py`
**根因** (亲自确认, 更正 finding): finding 建议「移 RUN_ID 进锁内」不完整。`PipelineLock.__enter__` 获锁失败调 `_handle_lock_failure()` → `self.logger.error`(187) 经模块级 (`:110`) delayed-truncating file handler **首写截断** A 日志。被拒实例 B 的这条 error 是其唯一 pre-raise file emit (R1 fix-correctness 核实: B 的 RuntimeError 从 __main__:844 裸传播 → Python 写 stderr traceback 非 file handler)。

**SHIP 修复 (两步 + R1 钉契约)**:
1. `core/locking.py::PipelineLock.__init__` 加参 `console_only_on_reject: bool = False`; `_handle_lock_failure` 在其为真时把 `error_msg` 写 `sys.stderr` (print) 而非 `self.logger.error` → 被拒路径不触 file handler。
2. `run_pipeline_function.py` / `run_pipeline_validation.py`: (a) RUN_ID emit (622/180) 移入 `with PipelineLock(...)` 块内; (b) `with PipelineLock(logger, output_dir, console_only_on_reject=True)`。
   - **R1 更正措辞**: 移入后 A 的真正首条 file emit 是 `__enter__` 内 `locking.py:117 已获取管道锁` (A 截断自己新鲜日志, 正确); RUN_ID 移入仅为消除其作为 B 的 pre-lock 截断源。

**R1 钉死三契约 (防脆弱不变量)**:
- (1) `console_only_on_reject` 默认必须 **False** (保 cooc 及其它用户行为);
- (2) **绝不**在 `tests/test_pipeline_lock.py` 任何 PipelineLock 构造透传该 flag (否则 L86/L184-188/L491 四处「reject 走 logger.error」断言集体翻红);
- (3) 仅两个 run_pipeline 入口的 `with` 传 True。
- (4) **补 gate 断言** (镜像 A3): 断言 `run_pipeline`/`run_validation` 函数体内 `with PipelineLock` 之前无任何 `logger.info(`/`logger.` file emit (源码正则), 结构化护住「with 前不得 emit」不变量。
- (5) `test_pipeline_lock_standalone.py` 内联副本不追随新参数 (doc-drift, 测试自足不翻红) — 于该副本注释补一行说明「锁契约冻结骨架, 不追随 console_only_on_reject」。

**golden-safety**: 纯日志, 不入 golden。**测试影响**: A3 (RUN_ID 函数级) 仍过; 默认 False → test_pipeline_lock reject 断言仍过。
**验证**: 新 gate 测试 (with 前无 emit) + 复跑 test_pipeline_lock*.py + test_five_entrypoint_hardening。

---

## F5 🟡 MEDIUM — golden 重生驱动漏跑 stage 51 (SHIP-AS-PLANNED)

**文件**: `scripts/migrate/run_production_regen.py:120-129`
**根因** (亲自 + R1 双证): [步骤1] 只跑 40+46, SOP 步骤1 明列须跑 51; 51 硬读 40、注册 OUTPUT_REGISTRY(schemas.py:94)、被 generate_golden_snapshot 逐列哈希 (line 149-155) → 财务列落盘后 `--execute` 会 bless 40-新/51-旧不自洽面板且自检恒绿。R1 completeness 确认: 40 的注册-parquet 下游唯 51, 无其它遗漏。

**SHIP 修复** — 46 之后补 51:
```python
        # 审计 F5: stage 51 硬读 40_panel_yearly 且注册 OUTPUT_REGISTRY, 属 40 下游 — 必须同步重建
        # (对齐 PRODUCTION_REGEN_SOP 步骤1), 否则 golden 会 bless 40-新/51-旧不自洽面板。
        rc = _run([sys.executable, "51_falsification_test.py"], execute=execute, env=det_env)
        if execute and rc:
            print(f"    [STOP] stage 51 退出码 {rc}"); return rc
```
(并把 120 行 [步骤1] 文案「stage 40 → 46」→「40 → 46 → 51」。)
**golden-safety**: driver 脚本, 正常运行不触发; 本机 --execute 被 preflight (缺财务列, runner 108-115) 挡死 → 零副作用。

---

## F7 🟡 LOW — strat_diff 值域桶错分 (SHIP-AS-PLANNED)

**文件**: `pipeline/features/strategic_diff.py:1985-1992` (`_log_robustness_diagnostics`)
**SHIP 修复**:
```python
        elif '_emb' in col or col.startswith('strat_diff_lg') \
                or col in ('strat_diff_full', 'strat_diff_ctx', 'strat_diff_ss'):
            lo, hi = 0.0, 2.0
```
**R1 golden-safety 实读**: strat_diff_{full,ctx,ss} = centroid_diff_emb 距离别名 (δ∈[0,2]); 盘上值 ∈[0.119,0.590]⊂[0,1] → 改桶 [0,1]→[0,2] 两界皆过 → assert 行为不变; `test_tfidf_out_of_bounds_raises` 用 strat_diff_n5 仍落 else 桶不受影响。
**验证**: `test_omni_fix_strategic.py` 补 `strat_diff_full:[1.9,0.1]` 锁死。

---

## F8 (测试) — fast: dual_track allow-list 漂移 (SHIP-WITH-REVISION, R1 扩范围)

**文件**: `tests/test_dual_track.py` (`_LLM_NAN_ALLOWED_PREFIXES` + finbert2 处理)
**根因** (亲自 + R1 实跑): 3 个 `test_no_nan_in_{full,ctx,ss}_track` 红。R1 实跑 `TestFallbackAxiom` 揭示 unexpected_nan **四族** (计划原只列前两族, R1 BLOCKER 补后两族):
- (a) per-model 分类列 `{gpt54nano,gemini31,deepseekv4}_{subst,locus,collab}_{full,ctx,ss}` — LLM 衍生 (LLM 失败→NaN 是设计信号);
- (b) **`finbert2_中性_{full,ctx,ss}`** (1005 全 NaN) — **R2 订正**: finbert2 **未缺席** (实测 `finbert2_{label,正面,负面,infer_failed}` 全 0-NaN, 已成功推理); finbert2 是 **2 类 Bernoulli (K=2) 模型** (CLAUDE.md 明示), neutral 中性类结构性无输出 → 该列**按设计恒 NaN** (与 `FINBERT2_MODEL_DIR` 无关, 生产带模型仍恒 NaN);
- (c) **`fintech_intensity_score{,_lg}_{full,ctx,ss}`** (15/104/118, canonical 与 _lg 逐轨相等) — 嵌入 co-primary 衍生, NaN = 空/短文本嵌入降级, 严格 both-or-neither (非 bug; ⚠ 仅 T=2 实证 0 单边孤儿, 见验收);
- (d) **`llm_prob_score_{ctx,ss}`** (73/114, full 轨 0-NaN) — LLM 聚合衍生 NaN。

**SHIP 修复** (扩四族, 每族给退化判定):
- allow-list 追加: per-model 分类前缀 (a) + `llm_prob_score` (d) + `fintech_intensity_score` (前缀 startswith 自动含 `_lg` 孪生) (c);
- finbert2 (b) **R2 订正机制**: 采用**逐列 all-NaN skip** (该判据在「finbert2 已跑=仅中性列 all-NaN」与「finbert2 真缺席=整族 all-NaN」两种情形下都稳健) **或** 精准白名单 neutral 列前缀 (`finbert2_中性`, K=2 结构性依据)。**三禁**: (i) 禁「整族 all-NaN + MODEL_DIR 未设」门控 (恒 False); (ii) 禁整测试 `pytest.skip` (会架空 a/c/d 三族校验成空验证); (iii) rationale 禁写「finbert2 缺席」(事实错误), 须写「K=2 Bernoulli neutral 结构性 NaN」;
- 逐族注释记录「其 NaN 为合法 LLM/嵌入/K=2 衍生退化 (both-or-neither 计数为证) 而非缺陷」, 不静默混入。
**验收 (R1 强制 + R2 加强)**: 实施后**必须实跑** `pytest news_process/tests/test_dual_track.py::TestFallbackAxiom -q` 三条**全 PASSED (非 skipped)** 再判 done。
- ⚠ **R2 MINOR 家族(a) 核验**: `gpt54nano_locus` NaN=419/442/452 (~42-45%) 是其自身 subst/collab (17/73/106) 的 6-25× 且唯它非对称 (gemini31/deepseekv4 三维对称) → **实施时须先核验此 ~42% NaN 是真 LLM 解析失败 (gpt54nano 响应格式 / locus 关键词回退) 还是 gpt54nano-locus 特异解析回归**; 若真失败→白名单+记录该发现; 若疑回归→上报为新 finding (不 fix, 改 stage21=付费/M0)。
- ⚠ **R2 MINOR 家族(c) 核验**: stage 15 fintech_intensity 的 both-or-neither 守卫是否行级 (非 F3 所修的 pass 级); 若无法确认→在 F8(c) 注明「both-or-neither 依据仅 T=2 实证」+ 加后续审计项 (stage 15 parity 粒度)。白名单不替代生产强制。
**golden-safety**: test-only。

---

## DEFER 项 (文档记录, 非遗漏; R1 事实订正)

- **F6** `tone_llms.py:1256-1262`: 正确修 = 列表推导追加 `and parsed.get(f"{m['short_name']}_verified") is True`。改 innovation_*_confidence 计算值 → 改 21/40 parquet → 改 golden (测度类改动, M0 门)。grep 全仓无 .do/paper_spec 消费 → 休眠零急迫。→ golden-regen 窗口随手带。
- **F1b** load.py 标识列归 string: F1 根治, 消除 T=18 非确定。golden-affecting (docid dtype)。impl 时按 test_00 复核可否提前 ship (见 F1 段)。
- **cohort (2红, R1 订正事实)**: `test_cohort_module_exports_84_banks` 实为 `assert 110 == 87` 失败 (模块现导出 **110 家**, 与 CLAUDE.md『110 banks × 2 years』当前 T=2 面板一致); `test_cohort_csv_is_committed_in_repo` 因 `data/raw/cohort/benefit_society_84banks.csv` **文件缺失 (ABSENT)** 失败 (非『84 行陈旧』)。→ 处置 defer 到 golden-regen 窗口 (需 regenerate cohort manifest + 更新 test 期望 + committed CSV; 数据依赖)。
- **fast 红总数订正**: 权威 `-m fast` 跑批为 **6 条** (cohort×2 + dual_track×3 + `test_global_jieba_stays_pure_isolation`×1)。⚠ `test_omni_fix_codebook::TestScriptPanelSource` 2 条与 jieba 1 条均 **order-flaky** (隔离单跑通过 = 纯测试间全局态污染); 是否出现取决于套件顺序。**F8 修 dual_track×3**; 其余 defer。
- **jieba/codebook 测试间污染 (order-flaky)**: 全局态泄漏 (`fintech_intensity`/`decay_sensitivity`/`radius_sensitivity` 裸 `jieba.add_word` + codebook 模块全局)。生产子进程隔离安全 (`run_pipeline_function.py:645` 注释显式点名 jieba 全局态)。修 = test teardown 重置或三模块隔离化 (measure-risky 需 golden 验)。→ 测试卫生跟进。

---

## 执行顺序 (六步)
1. ✅ 计划 → R1 对抗评审 (完成, REVISE_THEN_PROCEED)。
2. R1 整改并入 (本版) → **R2 独立对抗评审** (复核 R1 整改落实 + 新风险 + ship/defer 定稿)。
3. 授权实施全部 ship-now。
4. 实施 (F1/F2/F3/F5/F7/F8 + F4; F1b 按 test_00 复核)。
5. 三轮结果评审 (测试全套 + 字节 A/B + diff 对抗 + 通读)。
6. by-name 提交 + 推送 main。
