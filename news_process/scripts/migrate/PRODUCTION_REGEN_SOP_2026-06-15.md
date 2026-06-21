# 生产/golden 协调式重生 SOP (REPRO-1 闭合)

> PRODUCTION_REGEN_SOP_2026-06-15 · 配套驱动脚本 `scripts/migrate/run_production_regen.py`
>
> **何时执行**: 银行财务 outcome 数据 + IV enrichment 列接入到盘后 (当前 gated, 数据后续补)。
> 本 SOP 把审计 `PROJECT_REAUDIT_TOPTIER_T18_2026-06-14.md` 的 **REPRO-1 (P1)** + **T18-4** 闭合工序脚本化,
> 使 "面板 + golden + 代码" 在一次受控 run 内重建到自洽, 此后 $0 离线逐位复现。

## 背景 (为什么)

当前硬盘产物内部不自洽: 主面板 `40_panel_yearly.parquet` 比其上游 stage 21/24 旧 →
`test_panel_reproducibility.py` 闸门当前 RED。这是**已披露的设计性过渡态** (golden 重生 deferred
到 M0 付费 stage-21 之后), 但**投稿前必须闭合**。主财务 outcome (roa/funding_cost/
cost_income_ratio_change_3yr/citation_weighted_patent/m_and_a_fintech/tobin_q/z_score) 依赖尚未到盘的
银行财务面板; wire-ahead (derived_columns + 各 paper 01_data_prep capture-confirm) 已就位, 数据落盘即激活。

## 前置铁律 (执行前必读)

1. **勿删 `data/processed/_llm_cache.db`** (~474MB / 13万+ 条) — golden 确定性锚点; 删则 stage 21
   须重跑付费 API。验证覆盖率: `python -m news_process.scripts.audit.verify_stage21_cache_coverage`。
2. **离线确定性**: 全程设 `NEWS_PROCESS_LLM_OFFLINE=1` (stage 21 缓存 miss 时 raise 不调 API);
   `PYTHONHASHSEED=0` 已由 `core/stage.py:209` 对每个 stage 子进程强制 (有专测守护)。
3. **裸环境付费阶段 SSL**: 若须线上 (新语料致缓存 miss / 首次 ss 播种), 设
   `$env:SSL_CERT_FILE=$(python -c "import certifi;print(certifi.where())")` (见 memory yunwu-ssl-certifi-fix)。
4. **prompt v8 字节级冻结** — 不改任何 LLM prompt 模板文本 (改则缓存键变, 全 miss)。
5. **单一受控环境**: 勿在脏工作树上重生 (会把并行会话的中间产物误 bless 进 golden)。

## 工序 (驱动脚本 `run_production_regen.py` 逐步执行)

### 步骤 0 — 财务/IV enrichment 列接入 (人工, 数据依赖)
- 把银行财务面板 (ROA/CAR/NPL/RWA/total_assets/tobin_q/...) 按 (bank_id, year) merge 进面板构建链
  (`pipeline/panel/` 的 derived_columns / runner 步骤; wire-ahead 已留)。
- ⚠ **大小写统一**: `derivative_replication.py` 的 benefit_society/brokerage_network MAIN_DV 现为大写
  `ROA` **sentinel** (未接入占位), 而 benefit/25 二阶段硬编码小写 `roa`、spec outcome.primary=`roa`。
  接入时**统一为小写 `roa`** (与 spec + 模板一致), 并同步改 `derivative_replication.py` 的 ROA sentinel
  + `test_*` 中 `ROA_SENTINEL_2` 断言 (memory outcome-redesign-2026-06-13)。
- 接入后构造各 paper 主 outcome 列: funding_cost / cost_income_ratio_change_3yr /
  citation_weighted_patent / m_and_a_fintech / tobin_q / z_score。

### 步骤 1 — 重建面板 (stage 40 → 46)
```
NEWS_PROCESS_LLM_OFFLINE=1 python 40_panel_export_main.py   # 重建 40_panel_yearly.parquet / 51_panel_with_controls
NEWS_PROCESS_LLM_OFFLINE=1 python 46_stata_export.py        # 重导 .dta + codebook (variable_codebook.{csv,json,md,xlsx})
```
(若上游 21/24 也漂移, 先按 DAG 重跑相关 stage; 缓存全命中下 stage 21 离线 $0 逐位等价。)

### 步骤 2 — 重生 golden
```
python scripts/migrate/generate_golden_snapshot.py          # 重写 tests/fixtures/golden_panel_v0.json
```
- 接入财务列后 schema 变 → golden schema_version 同步; 列集扩 (新增财务/IV outcome 列)。

### 步骤 3 — 复现闸门转绿
```
pytest tests/integration/test_panel_reproducibility.py -q
pytest tests/integration/test_dag_consistency.py -q
```
- **T18-4 (BLAS-FP 容差)**: 若 `bank_clustering` / `cfbetween` / `bank_harmonic_cent` 三列因 BLAS 浮点
  跨次重建漂移致 hash 失配, 给 repro 测试对这三列建**白名单/数值容差** (见下"可选代码改动")。
  注: `core/stage.py:209` 已强制 `PYTHONHASHSEED=0`, 实测固定后多为字节级一致 (REPRO-2 已证伪 BLAS 根因);
  仅当受控环境实测仍漂移时才加容差, 勿无脑放宽 (会掩盖真回归)。

### 步骤 4 — 同 commit freeze
- 面板 (.parquet/.dta/codebook) + golden + 代码**同一 commit** 落地; 投稿前打 archival tag。
- 此后**禁止单独重跑上游 stage 而不连带重建下游 + 重生 golden** (否则又 RED)。

## 可选代码改动 (T18-4, 受控环境实测确认须要后再做)

若 repro 测试对 3 个网络列失配, 在 `tests/integration/test_panel_reproducibility.py` 加:
```python
# BLAS-FP 非确定列白名单 (panel-3-network-cols-nondeterministic): 跨次重建间浮点末位漂移,
# 非逐位可复现; 仅这 3 列豁免精确 hash, 改数值容差比对 (rtol=1e-9)。
_BLAS_FP_TOLERANT_COLS = {"bank_clustering", "cfbetween", "bank_harmonic_cent"}
```
并在 column-hash 比对处对这些列改 `np.allclose(rtol=1e-9)` 而非精确 hash。**纯放宽门禁, 勿动面板值。**

## 验收
- `test_panel_reproducibility.py` 全绿 (或 3 BLAS 列在容差内)。
- `pytest -m fast` 无新增失败。
- `git status`: 面板/golden/代码同 commit; 无 N4 去重回退 (dedup.py/preprocessing.yaml 保持 origin/main)。
- 复现包 `python -m news_process.papers._common.stata_runner build-replication --paper <id>` 11 篇全通;
  `doctor` 全 [OK] (Stata ado 已装齐)。
