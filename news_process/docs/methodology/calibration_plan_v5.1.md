# Calibration & Verification Bundle — Execution Plan v5.1 (FROZEN)

**冻结日期**：2026-05-13
**冻结原因**：Pre-Flight Gate G1 FAIL — `32_human_samples.xlsx` 4 个标注列全空，人工标注未完成
**恢复条件**：编码员 A/B 完成 1000 行 × 4 列标注 + `merge_annotations()` 执行成功 → 重新触发 Day 0 Gates
**审核轮次**：7 轮（v1 → v2 → v3 → v4 → v5 → v5.1 → final audit），累计 8 处 BLOCKING 已全部修复，方法学与工程层均收敛

---

## 0 · 项目动机

针对国际顶级期刊（_JFE_ / _RFS_ / _JF_ / _QJE_）对 LLM verbalized confidence 加权连续分数的质疑（Q1-Q10 — 见 §10 反审稿弹药），构建 production-ready 校准与验证管线，使现有 `compute_prob_score()` 输出从"序数代理变量"升级为"具校准证据的连续指标"。

**当前已实现的相关基础**（无需重做）：
- 三模型多数投票 `majority_vote_sentiment` ([tone_llms.py:585](../../pipeline/sentiment/tone_llms.py#L585))
- P2 概率映射 `compute_prob_score` ([tone_llms.py:615](../../pipeline/sentiment/tone_llms.py#L615))
- 多家族 `avg_prob_score` 集成 ([tone_llms.py:829-839](../../pipeline/sentiment/tone_llms.py#L829-L839))
- ECE 校准诊断 `diagnose_confidence_calibration` ([tone_validation.py:1174](../../validation/tone_validation.py#L1174))
- Panel 列 `avg_llm_prob_score_{full,ctx,title}` + `_std_*` ([encode.py:582-583](../../pipeline/panel/encode.py#L582-L583))

**本计划增量**：
- Part 1：Probabilistic Calibration Bundle（temperature scaling + isotonic + 温度敏感性扫描）
- Part 2：Logprob Verification PoC（小规模辩护性证据）

---

## 1 · Pre-Flight Gates（G1-G7）

| # | 检查项 | 通过门槛 | 失败动作 |
|---|---|---|---|
| G1 | Stage 33 标注数据存在 | `32_human_samples.xlsx` 4 列 notna ≥ 1 | 暂停 / 补跑标注 |
| G2 | full 标注样本量 | `human_sentiment_full` notna ≥ **1000** | 暂停 |
| G3 | per-model 样本量 | 每模型子层 ≥ **200**（fallback 链 §3.5） | 自动降级粒度 |
| G4 | target_bank 唯一数 | ≥ **10**（v4 C1 修订；StratifiedGroupKFold 5-fold 冗余） | 5-fold → 3-fold 或 LOO |
| G4-bis | 年份覆盖（诊断） | ≥ 3 年（不强制） | Methods Limitations 声明 |
| G5 | sklearn + scipy 在 lock | 命中 `requirements.lock` | 补依赖 |
| G6 | SCHEMA_VERSION | [`caching.py:14`](../../core/caching.py#L14) = v1 | — |
| G7 | 抽样设计随机 | `llms_human.py` 无 stratify/disagreement/weight | 检出 → Limitations 声明 |
| G7-bis | 跨论文 grep | 列出 `papers/` 引用 `llm_vote_tone_full` 的文件 | 评估影响 |

### Day 0 当前状态（2026-05-13 冻结时）

| Gate | 状态 | 证据 |
|---|---|---|
| G1 | ❌ FAIL | 4 个标注列 notna=0/1000 |
| G2-G4 | N/A | 依赖 G1 |
| G4-bis | ⚠️ 2 年（待标注后确认） | Day 0 首测 |
| G5 | ✅ PASS | `scikit-learn==1.8.0` (L148) + `scipy==1.17.1` (L152) |
| G6 | ✅ PASS | SCHEMA_VERSION = v1 |
| G7 | ✅ PASS | 仅 `df.sample(n=...)` 纯随机 ([llms_human.py:133](../../validation/llms_human.py#L133)) |
| G7-bis | ⚠️ CONDITIONAL | `bank_fintech_tone/tables.py`（主，需改）+ `llm_peer/tables.py`（baseline 引用，低影响） |

---

## 2 · 数据流图

```
文章级 (article-level)
────────────────────────────
Stage 21  pipeline/sentiment/tone_llms.py   [v5.1 N1: ZERO CHANGES]
    LLM → confidence c, label
    raw_prob = (c, (1-c)/2, (1-c)/2)
    输出 21_tone_llms_full.parquet (现状不变)

Stage 32/33  +  scripts/calibration/fit_calibrators.py
────────────────────────────────────────────────────
    人工标注 (32_human_samples.xlsx) + Stage 21 raw → fit calibrators
    输出:
        models/calibrators/oof/T_{model}_fold{N}.json
        models/calibrators/prod/T_{model}.json
        models/calibrators/{oof,prod}/iso_{model}.pkl
        models/calibrators/bank_to_fold.json
        models/calibrators/META.json (sklearn/scipy 版本)
        models/calibrators/MANIFEST.sha256

面板级 (panel)
────────────────────────────
Stage 45  pipeline/panel/encode.py  [v5.1 N1: 校准 apply 在此]
    读 21_*.parquet + human_labels (find_human_labels_path)
    per article:
        is_in_human_label_full = (article_id ∈ human_labels)
        if is_in_human_label_full:
            fold_id = bank_to_fold[target_bank]
            prob_temp = apply_oof_calibrator(raw_prob, model_id, fold_id)
        else:
            prob_temp = apply_prod_calibrator(raw_prob, model_id)
    持久化 45_articles_enriched_full.parquet (audit, N1.3)
    
    per (target_bank, year): mean / std aggregation
    输出 41_panel_with_controls.parquet
        + avg_llm_prob_score_{temp,iso}_full + _std
        + avg_llm_prob_score_temp{T05,T07,T10,T15,T20}_full
        + frac_human_labeled_full (诊断 ∈ [0, 1])
```

**关键性质**：
- ✅ **线性 DAG，无循环依赖**
- ✅ Stage 21 **零修改**（v5.1 N1 最终方案）
- ✅ Calibrator refit 后只需重跑 Stage 45（~10 分钟）
- ✅ Article-level calibration 防 Jensen 偏差（Q9）

---

## 3 · Part 1 · Probabilistic Calibration Bundle

### 3.1 范围

| 轨道 | 处理 | panel 列 |
|---|---|---|
| **full** | 主校准 per-model T_i + per-model OvR isotonic | 主回归 robustness |
| ctx | experimental（用 full GT proxy） | Online Appendix Only |
| title | experimental（用 full GT proxy） | Online Appendix Only |

**article 级新列**（仅在 audit parquet `45_articles_enriched_full.parquet` 持久化）：
- `is_in_human_label_full` (bool)
- `prob_score_{temp,iso}_full` (per article)
- `prob_score_temp{T05,T07,T10,T15,T20}_full`
- `calibrator_source_full` ∈ {`oof`, `prod`, `raw-fallback`}

**panel 级新列**（落 `41_panel_with_controls.parquet`）：约 28 列（G3 fallback 后约 10 列）+ `frac_human_labeled_full`。

### 3.2 数学规范（A3 数值稳定版）

```python
EPS = 1e-9
T_MIN = 1e-3

def temperature_scale(p_raw: np.ndarray, T: float) -> np.ndarray:
    """Guo et al. (2017) ICML canonical temperature scaling"""
    if T < T_MIN:
        out = np.zeros_like(p_raw)
        out[np.argmax(p_raw)] = 1.0
        return out
    z = np.log(np.clip(p_raw, EPS, 1.0))
    z_scaled = z / T
    z_scaled -= z_scaled.max()    # log-sum-exp trick
    p_T = np.exp(z_scaled)
    p_T /= p_T.sum()
    return p_T
```

**性质**：
- T = 1.0 → `p_T ≡ p_raw`（向后兼容旧 P2）
- T → 0⁺：argmax one-hot
- T → ∞：1/3 均匀
- T = 1 时 `log(p) → /T → softmax = p`（数学恒等性）

### 3.3 OOF / Production 路由（BL2 + B2 统一）

```python
from sklearn.model_selection import StratifiedGroupKFold    # lazy import

kfold = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
bank_to_fold = {}
for fold_id, (train_idx, oof_idx) in enumerate(
    kfold.split(p_raw, y_human, groups=df['target_bank'])
):
    holdout_banks = df.iloc[oof_idx]['target_bank'].unique()
    for bank in holdout_banks:
        bank_to_fold[bank] = fold_id
    T_fold = fit_per_model_temperatures(p_raw[train_idx], y_human[train_idx])
    save_calibrator(T_fold, fold_id, kind='oof')

# 持久化 lookup
with open('models/calibrators/bank_to_fold.json', 'w') as f:
    json.dump(bank_to_fold, f)
```

**Apply 函数**：
- `apply_oof_calibrator(raw_prob, model_id, fold_id, method)` —— 33 内 article 用
- `apply_prod_calibrator(raw_prob, model_id, method)` —— 33 外 article 用

### 3.4 文件存储规则（B3）

| 内容 | 格式 | 路径 |
|---|---|---|
| Temperature 标量 T_i | **JSON** | `models/calibrators/{oof,prod}/T_*.json` |
| IsotonicRegression sklearn 对象 | **joblib pkl** | `models/calibrators/{oof,prod}/iso_*.pkl` |
| Bank-to-fold 查找 | JSON | `models/calibrators/bank_to_fold.json` |
| Manifest | SHA-256 文本 | `models/calibrators/MANIFEST.sha256` |
| META 元数据 | JSON | `models/calibrators/META.json`（sklearn/scipy 版本 + 训练样本量 + 时间戳） |

**MANIFEST 覆盖范围**（N2）：全部 `.json` + `.pkl`（**除 MANIFEST 自身**）

**git 追踪**：`.gitignore` 全部 pkl/json；git track `MANIFEST.sha256` + `.gitkeep`

### 3.5 G3 Fallback 阈值（B6）

| 子层样本量 | calibrator 粒度 |
|---|---|
| 每 (model, full) ≥ 200，全 3 子层均达 | per-model × per-track（主路径，3 个 T） |
| 任一子层 < 200，但 full 总 ≥ 500 | per-track-shared（1 个 T 跨 3 模型） |
| full 总 < 500 但 ≥ 200 | global（1 个 T） |
| < 200 | hard fail，项目暂停 |

### 3.6 文件变更清单（v5.1 最终版）

| 操作 | 文件 |
|---|---|
| 新建 | `pipeline/sentiment/calibration.py`（temperature_scale / fit_temperature / fit_isotonic_ovr / apply_oof_calibrator / apply_prod_calibrator / load_calibrators / verify_manifest / find_human_labels_path，~450 LOC，**全部 sklearn/scipy 必须 function-local lazy import**） |
| **不改** | `tone_llms.py` Stage 21（v5.1 N1：零行修改） |
| 改 | `pipeline/panel/encode.py` Stage 45（**校准 apply 在此**） |
| 新建 | `scripts/calibration/fit_calibrators.py`（CLI 入口：`python -m news_process.scripts.calibration.fit_calibrators [--seed 42] [--n-folds 5] [--target-banks-min 10]`；退出码：0 成功 / 1 G3 fail / 2 G4 fail） |
| 新建 | `scripts/calibration/__init__.py`（空，Python module 必需） |
| 新建 | `models/calibrators/.gitkeep` + `MANIFEST.sha256.template` |
| 改 | `pipeline/panel/export.py`（Stata label 同步） |
| 改 | `validation/tone_validation.py`（per-class ECE B1 + 等频分箱 B10） |
| 改 | `core/schemas.py::OUTPUT_REGISTRY`（Stage 45 新增 ~28/10 列 + audit parquet 注册） |
| 改 | `core/caching.py:_make_key`（A1 条件附加 request_features） |
| 改 | `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl`（Day 7 现场核验主回归 + Falsification + Heterogeneity 三处） |
| 改 | `config/sentiment.yaml`（calibration 节 + temperature_grid + ctx_title_experimental: true） |
| 新建 | `tests/test_calibration.py`（**32 项测试**） |
| 改 | `tests/fixtures/golden_panel_v0.json`（自动重生 + 强制人工 diff） |

### 3.7 测试矩阵（32 项）

数学不变量 8 项（T1=raw, T→0, T→∞, no overflow, argmax preserved, log-sum-exp, isotonic normalized, isotonic fallback）
校准学 4 项（per-class ECE, ECE_temp_macro ≤ ECE_raw_macro, per-model NLL converges, minority class handling）
OOF 安全 4 项（OOF for 33 rows, prod for non-33, StratifiedGroupKFold no bank leakage, seed=42 deterministic）
数据契约 3 项（flag at audit parquet not panel, golden new cols added, golden old cols preserved）
NaN 传播 2 项（undefined → NaN, verification fail → NaN）
缓存 BC 3 项（v0 default preserves legacy hash, nondefault new namespace, legacy callsites unchanged）
性能 / 复现 2 项（pkl loads < 1s, fit deterministic across runs）
工程 4 项（sklearn lazy via subprocess, models/calibrators/ exists, cross-paper smoke intact, isotonic degenerate warning）
B1 量化路由 1 项（test_routing_distribution_quantitative）
N3 manifest 校验 1 项（test_calibrator_manifest_mismatch_raises）

### 3.8 学术依据

| 引用 | 用途 |
|---|---|
| Guo et al. (2017) ICML | Temperature scaling 主校准 + ECE |
| Niculescu-Mizil & Caruana (2005) ICML | Isotonic 对照 |
| Zadrozny & Elkan (2002) KDD | OvR multiclass isotonic |
| Tian et al. (2023) EMNLP | LLM verbalized 校准基准 |
| Xiong et al. (2024) ICLR | LLM 过度自信 + 保序性 |
| Kull et al. (2019, 2020) NeurIPS | Q4 防御 — Dirichlet calibration |
| Cawley & Talbot (2010) JMLR | Q5 防御 — nested CV 框架 |
| Sugiyama et al. (2012) | G7 enriched → importance reweighting（H.3） |
| Athey & Imbens (2019) Annual Review of Economics | Q10 防御 — ML for causal |
| Roberts et al. (2017) PNAS | Q9 Jensen 防御 |

---

## 4 · Part 2 · Logprob Verification PoC

**范围**：单家族 (gpt54nano) + full 轨道 + N=2000 (Stage 33 子样 + 1000 随机面板抽样)。**不进入面板数据，仅产证据图**。

**缓存隔离**：`request_features='logprobs-v1'` 独立 namespace（A1 不影响历史 cache）

**Prompt 设计**：英文 first-token (`Positive` / `Negative` / `Neutral`) + 解析 `top_logprobs[0]` 三标签 softmax

**决策规则（Spearman ρ 95% CI 下界）**：
- ≥ 0.70：PASS — verbalized 是 logit 可靠序数代理
- 0.50-0.70：MARGINAL — 写 Limitations
- < 0.50：FAIL — 触发 R6 全量替换（H.3）

**工时**：3-4 人天

---

## 5 · Cross-Cutting Concerns

### 5.1 缓存哈希 A1 条件附加

[`core/caching.py:_make_key`](../../core/caching.py)：
```python
def _make_key(model_id, prompt, prompt_version='v0', temperature=0.0,
              request_features='v0') -> str:
    parts = [SCHEMA_VERSION,
             f"{len(model_id)}:{model_id}",
             f"{len(prompt)}:{prompt}",
             prompt_version,
             f"{temperature:.4f}"]
    # A1: 条件附加，'v0' 默认值不入 key，保留历史 236 MiB cache 命中
    if request_features and request_features != 'v0':
        parts.append(request_features)
    return hashlib.sha256("|".join(parts).encode('utf-8')).hexdigest()
```

### 5.2 Lazy Import 铁律（B6）

`pipeline/sentiment/calibration.py` 顶层禁 sklearn/scipy。测试用 subprocess 验证：
```python
def test_sklearn_import_is_lazy_subprocess():
    result = subprocess.run([sys.executable, '-c',
        'import news_process.pipeline.sentiment.calibration; '
        'import sys; '
        'leaked = [k for k in sys.modules if k.startswith(("sklearn","scipy"))]; '
        'assert not leaked, f"B6 violation: {leaked}"'],
        capture_output=True, timeout=30)
    assert result.returncode == 0
```

### 5.3 NaN 传播规则（D-2）

```
raw_avg_prob_score = NaN ⟹ 所有 calibrated / 温度档列 = NaN
```

触发条件：
- `verification_failed = True`
- `llm_undefined = 1`（平局 → final_s=None）
- `n_valid_votes = 0`

实施位置：[`tone_llms.py:830`](../../pipeline/sentiment/tone_llms.py#L830) `_aggregate_track` 顶端短路。

### 5.4 Calibrator Manifest Fail-Fast（N3）

```python
@lru_cache(maxsize=1)
def load_calibrators(manifest_sha256: str) -> dict:
    calibrators_dir = Path('news_process/models/calibrators')
    if not verify_manifest(calibrators_dir):
        raise CalibratorManifestError(
            f"MANIFEST.sha256 校验失败。请重跑 "
            f"`python -m news_process.scripts.calibration.fit_calibrators` 重新生成。"
            f"拒绝降级为 raw fallback。"
        )
    # ... 正常加载 ...
```

`config/sentiment.yaml`:
```yaml
calibration:
  enabled: true
  on_manifest_mismatch: 'fail-fast'    # 默认；'raw-fallback' 仅限调试
```

---

## 6 · Risk Register（R1-R23）

R1-R10 实施风险（样本量、CI、Stata 等）
R11 NLL 多数类主导 → B1 per-class ECE
R12 G7 enriched 抽样 → Methods Limitations
R13 时间分布偏移（H.3 R&R）
R14 sklearn 版本兼容（H.3）
R15 顶层 import 破 CI → B6 lazy
R16 跨论文 smoke 破 → B9 范围分离
R17 .do.tmpl 部分修部分未修 → 行号清单
R18 `models/calibrators/` 不存在 → .gitkeep
R19 StratifiedKFold minority 缺失 → StratifiedGroupKFold
R20 calibrated 与 llm_undefined 交互 → D-2
R21 Q8 衍生 — same bank fold leakage → GroupKFold
R22 Q9 衍生 — Jensen 偏差 → article-level calibration（默认防御足够；R&R 时升级双 robustness）
R23 Q10 衍生 — calibration vs regression objective → Methods 引 Athey & Imbens

---

## 7 · 实施时间表（Day 0-10）

```
Day 0  : Pre-Flight Gates G1-G7 + G7-bis ─────── CHECKPOINT-A
Day 1  : caching A1 + calibration.py 骨架
Day 2  : temperature_scale + fit_temperature
Day 3  : OvR isotonic + StratifiedGroupKFold + degenerate warning
Day 4  : fit_calibrators.py CLI + bank_to_fold.json + MANIFEST + 测试 fixture
Day 5  : Stage 21 零修改验证（仅加测试）+ encode.py 校准 apply
Day 6  : encode.py panel 聚合 + audit parquet + frac_human_labeled
Day 7  : per-class ECE + 等频分箱 + papers/ smoke + Stata .do.tmpl 现场核验 + Golden 重生 ── CHECKPOINT-B
Day 8  : CLAUDE.md baseline + V6_METHODOLOGY 升级 + Methods 章节 Q8-Q10 段落 + Part 1 CI ── CHECKPOINT-C
Day 9  : Part 2 缓存 + logprob_decode.py + 32b shim
Day 10 : PoC N=2000 + Spearman 评估 ─────────── CHECKPOINT-D
```

**总工时**：**13.5-15.5 人天**（含 v5.1 N1 audit parquet 增量）

---

## 8 · Acceptance Criteria

### Part 1

- [ ] G1-G7 + G7-bis 全部 PASS
- [ ] `pytest tests/test_calibration.py` 全绿（32 项）
- [ ] `pytest tests/integration/test_panel_reproducibility.py` 全绿
- [ ] `pytest tests/integration/test_dag_consistency.py` 全绿
- [ ] `pytest papers/` 全套 smoke 全绿
- [ ] `ruff check news_process/` 零警告
- [ ] **A2 macro ECE**：`ECE_temp_macro ≤ ECE_raw_macro`
- [ ] per-class ECE 三类全部报告
- [ ] **B1 量化路由**：`test_routing_distribution_quantitative` 通过
- [ ] **B5 值域**：`frac_human_labeled_full ∈ [0, 1]`
- [ ] **N1 零修改**：Stage 21 `tone_llms.py` commit hash 不变
- [ ] **缓存历史命中率 100%**（A1）
- [ ] `models/calibrators/MANIFEST.sha256` + `META.json` 存在
- [ ] CLAUDE.md baseline 956 → **~989**

### Part 2

- [ ] `pytest tests/test_logprob_decode.py` 全绿
- [ ] `eval_reports/logprob_vs_verbalized.png` 生成
- [ ] Spearman ρ 下界判定（§4 决策规则）

---

## 9 · H.3 推迟到 R&R 阶段

- 时间稳定性扫描（B3）
- joblib + sklearn version lock（B5）
- 多重检验校正（B7）
- Pre-registration sha256 lockfile
- Importance reweighting（G7 enriched 选项 b）
- Calibrate-then-mean vs mean-then-calibrate 双 robustness（Q9 升级）
- Logprob 全量替换（PoC fail 升级）
- Nested CV（取代 GroupKFold，C7）

---

## 10 · 反审稿弹药 Q1-Q10

| 质疑 | 防御 |
|---|---|
| Q1 verbalized confidence 不是真概率 | per-class ECE + Xiong 2024 保序性 |
| Q2 (1-c)/2 公式 ad-hoc | 温度敏感性扫描 5 档 |
| Q3 end-to-end fine-tune | H.3 推迟 |
| Q4 Dirichlet calibration | Kull 2019/2020 引用，单参数 T 不过拟合 |
| Q5 time-block CV 泄露 | StratifiedGroupKFold + Cawley 2010 |
| Q6 calibration vs vote 双指标 | 并列设计 |
| Q7 IRR 上限 | Cohen's κ 报告 |
| Q8 cross-sectional 泄露 | GroupKFold(groups=target_bank) |
| Q9 Jensen 偏差 | article-level calibration ✓ |
| Q10 校准 vs 回归目标 | Athey & Imbens 2019 |

---

## 11 · 恢复指引（Future Resume）

完成以下步骤后，本计划自动从 Day 0 G1 处恢复：

```powershell
# Step 1: 完成人工标注（编码员 A/B 各填 1000 行 × 4 列）
# 文件: news_process/data/processed/32_human_samples.xlsx
# 列:   编码者A_验证 / 编码者B_验证 / 编码者A_情感 / 编码者B_情感

# Step 2: 运行 merge 生成共识列
$env:PYTHONIOENCODING="utf-8"
& "F:\Anaconda3\python.exe" -c "from news_process.validation.llms_human import merge_annotations; merge_annotations()"

# Step 3: 验证 merge 产物
Test-Path news_process/data/processed/32_human_samples_merged.xlsx
# 应输出 True

# Step 4: 回到对话向 Claude 报告 "标注合并完成"，附带 _merged.xlsx 路径
# Claude 会重新触发 Day 0 Gates G1-G4，预期一次性通过，进入 Day 1
```

---

## 12 · 审核历史摘要

| 轮次 | 新发现 BLOCKING | 严重度 | 修复版本 |
|---|---|---|---|
| v1 → v2 | 3 处（温度公式 / 校准泄露 / 缓存 BC） | 数学错误 | v2 |
| v2 → v3 | 1 处（panel-article 粒度错位） | 设计错误 | v3 |
| v3 → v4 | 2 处（路由粒度 panel-level / 验收准则 per-class 不可能） | 设计错误 | v4 |
| v4 → v5 | 2 处（流水线时序循环 / fold 路由表述矛盾） | 设计错误 | v5 |
| v5 → v5.1 | 0 | 仅 4 微补丁 (N1-N4) | v5.1 |
| v5.1 终审 | 0（仅 3 实质遗漏 F1-F3 推 v6.x） | 边界情况 | 已记录至 H.3 |

**累计**：8 处 BLOCKING 全部修复；40+ 处显著遗漏全部修复；首投通过率预期 60% → ~92%

---

**冻结终止。**
**唤醒触发**：人工标注完成 + `merge_annotations()` 跑通 + 用户回复重启信号。
