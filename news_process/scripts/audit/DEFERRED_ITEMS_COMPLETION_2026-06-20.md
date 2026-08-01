# 延后项收口报告 (2026-06-20)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 收口 `LOG_FIXES_REAUDIT_TOPTIER_2026-06-20.md` §3/§4 的全部延后项。
> 方法: 主控直接处理 (含 WebSearch 引用核验 + 功能性验证 + 根因修复) → 实证确认。

---

## 总结: 4 项延后, 3 项已完成收口, 1 项生产门控 (本机物理不可执行, 已给 SOP)

| # | 延后项 | 状态 | 关键证据 |
|---|---|---|---|
| 1 | conftest 日志隔离盲区 (R1 根因) | **✅ 已修复 + 实证** | monkeypatch 后跑 import-heavy pytest, 富集日志 md5 前后一致 |
| 2 | R19 变量名 33 字符 | **✅ 已验证缓解** | 经生产 shorten_long_column_names → 32 唯一, 断言 PASS |
| 3 | 待核验引用 (≥4 处) | **✅ 已核验/订正** | Carlson/Andreou 经 web 证实为真且精确; Distel 标题已订正; SSRN 已诚实标注 |
| 4 | 受控 golden 重生 (T=19) | **⚠ 生产门控 (本机不可执行)** | 本机 data/raw 空 + 付费 M0 gate + 并行会话正占 panel/golden; 已给 SOP |

---

## 1. ✅ conftest 日志隔离盲区 (R1 根因修复)

**根因**: 多个 pipeline stage 模块在【模块顶层】调 `setup_logging()` 并随即 emit 横幅 (如 13/14/21 的 1-2 行 banner)。pytest 收集期 import 这些模块时, emit 发生在 *import 时刻* —— 早于任何 fixture (含原 session 级 handler 扫描), 故以 `file_mode='w'` 首写截断覆写 `logs/<stage>.log` 的真实生产记录 (即第一轮审计 "12b/37/47/39c/39e/39f/21 现盘日志实为测试产物" 的成因)。session/function 级 fixture 都无法阻止 import 期 emit。

**修复** (`tests/conftest.py`, 模块级, 收集开始前执行): monkeypatch `news_process.core.logging.setup_logging`, 使任何写【生产 `logs/` 目录】(经 `load_config()['paths']['log_dir']` 精确解析) 的调用强制 `console_only=True` (不创建文件 handler); 写 tmp 目录的调用 (test_helpers / test_pipeline_reporting 等单测) 经路径判别豁免, 行为不变。生产运行不导入 conftest → setup_logging 在生产中零副作用。

**实证**:
- 跑 import-heavy `pytest` (test_dag_consistency + test_helpers + test_stage_smoke + test_omni_fix_val_prompt) 前后, `logs/{14,13,21}` 的 md5 **逐位一致** (`7e1cb31e... / 5c49ea84... / 323fa577...` 不变) → 生产日志不再被测试覆写。
- 广测 312 passed / 0 failed (含 test_helpers 的 setup_logging 文件 handler 单测、test_stage_smoke、test_cleanup_prune_logs、test_pipeline_reporting) → 零回归。
- 此前 (修复前) 跑 test_dag_consistency 会把 `14/13` 覆写成 import-banner (PID:13604 实证)。

---

## 2. ✅ R19 变量名 33 字符 (`exc_jiang_2021_score_negonly_full`)

**功能性验证** (喂入生产 `stata_export.shorten_long_column_names` + `_assert_track_triplet_unique`):
```
exc_jiang_2021_score_negonly_full (33) → exc_jiang_2021_score_negonly_ful (32) [OK]
exc_jiang_2021_score_negonly_ctx  (32) → exc_jiang_2021_score_negonly_ctx (32) [OK]
exc_jiang_2021_score_negonly_ss   (31) → exc_jiang_2021_score_negonly_ss  (31) [OK]
all ≤32: True | unique: True | triplet uniqueness assertion: PASS
```
**结论**: 33 字符名经生产管道安全截断为唯一 ≤32 Stata 合法名, 三轨 (full/ctx/ss) 截断后仍互异。**不做源码改动** —— 重命名源列会改 `.dta` schema → 破坏 Stata 模板引用 + golden, 反而不安全。`pipeline/panel/runner.py` 写盘前的 WARNING 仅为信息性 (标记截断前的 33 字符名), 下游已有 `shorten_long_column_names`(md5 去重) + `_assert_track_triplet_unique` + `validate_stata_compat` 三重防护。

---

## 3. ✅ 待核验引用 (WebSearch 核验, 推翻"普遍造假"假设)

| 引用 | 核验结果 | 动作 |
|---|---|---|
| **Carlson & Burbano (2026, SMJ 47(3):699-725)** | **真, 精确** — "The use of LLMs to annotate data in management research: Foundational guidelines and warnings", SMJ 47(3):699-725, DOI 10.1002/smj.70023 | 无需改 (卷/期/页全对; "造假签名"为虚惊) |
| **Andreou et al. (2026, RP 55(3):105409)** | **真, 精确** — "Measuring R&D activity through 10-K narrative disclosures", RP 55(3):105409, core-contextual word-pairing | 无需改 |
| **Distel/Grimpe/Poetz (2026, RP 55(3):105426)** | 卷/期/页/DOI 对, 但 **`refs.bib` 标题错** | **已订正** refs.bib (en+zh): "Token vs. Hidden Adoption in Innovation Research" → 真实标题 "The Use of Scientific Research in Policy Documents" (`policy_alignment.py` 本就正确) |
| **SSRN-4558295 §7.2** (entity_masking) | **无法解析** (web 检索 0 命中, SSRN 直取 403) — 裸 SSRN 编号无作者/标题/年 | **已诚实标注** (`entity_masking.py:32`): 标 "投稿前须核验, 不可确认则降级 working paper" + 给方法学已发表锚点 "Robustness of Named-Entity Replacements for In-Context Learning" (Findings of EMNLP 2023) |

> 关键: WebSearch 核验**避免了误降级两篇真引用** (Carlson/Andreou) —— 顶刊诚信的正确做法是先核验再下结论, 而非按"未来日期+精确卷期=造假"的启发式盲删。

---

## 4. ⚠ 受控 golden 重生 (T=19) — 生产门控, 本机物理不可执行

**为何不能在本机完成** (非偷懒, 是硬约束):
1. **无生产数据**: 本机 `data/raw/` 空 (CLAUDE.md: "本机 data/raw 空、T=2 跑不了"); 全量 18.2M 文章 / 2007-2025 / T=19 语料不在此机。当前盘面是 T=2 (172 行 = 86 banks × 2017-2018) 占位样本。
2. **付费 M0 gate**: stage 21 全量在线 + stage 36/39 在线付费需成本审批 (M0 gate, 见 memory `paper_portfolio_decision_gates`)。
3. **并行会话冲突**: 当前有并行会话正对 panel/golden 做 (T=2 loughran) 重生 (`golden_panel_v0.json` / `40_panel_yearly.parquet` mtime 00:58-01:16), 本会话再跑会撞车。

**生产 SOP** (待 T=19 数据就位 + M0 审批后执行, 单机干净环境):
```
设 OMP_NUM_THREADS=1 + KMP_DUPLICATE_LIB_OK=TRUE (BLAS 单线程确定性, 见 memory golden-regen-omp-determinism-2026-06-18)
→ 干净树, 重跑改动链 (22→24→45→46) 或全量 run_pipeline_function
→ stage 21 在线全量 (三轨 full/ctx/ss) + stage 36/39 在线付费
→ generate_golden_snapshot.py 重生 golden_panel_v0.json
→ 逐位比对【排除】3 个 BLAS-FP 网络中心度列 (bank_eigen/harmonic/cfbetween_cent + clustering, 任意两跑都漂)
→ radius∈{0,1,2,3} 稳健性网格
→ 二次重建验确定性全绿 (test_panel_reproducibility)
铁律: 勿删 data/processed/_llm_cache.db (删则 golden 不再 $0 确定性复现)
```
本次所有修复均 **validation/log/doc 层, 不触 panel/golden** → 不要求 golden 重生即可成立; golden 重生仅为未来 T=19 投稿样本所需。

---

## 5. 本轮新增改动 (4 文件, 在前述 18 文件之外)
- `tests/conftest.py` — R1 根因 monkeypatch
- `validation/entity_masking.py` — SSRN-4558295 诚实核验标注
- `papers_assets/benefit_society/drafts/en/refs.bib` — Distel 标题订正
- `papers_assets/benefit_society/drafts/zh/refs.bib` — Distel 标题订正

全 ruff 绿 / py_compile 通过 / 312 定向测试 0 失败 / golden-safe / 未提交。
