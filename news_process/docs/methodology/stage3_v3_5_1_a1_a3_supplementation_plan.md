# Stage 3 v3.5.1 Supplementation Plan — A1 Lexical Clarity + A3 Numerical Intensity

> **状态**: DRAFT v0.3 (2026-05-17, **post 9 轮 V1-V15+同行+D-day+完备+对抗+边缘 case+EiC audit; 97 findings 闭环**)
> **范围**: v3.5.0 baseline 之上的**纯文本指标补强层** — 不改 prompt、不重跑 stage 21、不增 LLM 成本
> **基线**: v3.5.0-augmentation tag (D-1 day **必补打** at v3.5.0 release commit per CHANGELOG hash)
> **关联**: [stage3_v3_5_0_augmentation_plan.md](stage3_v3_5_0_augmentation_plan.md) / [stage3_third_dim_plan_v3.4.0.md](stage3_third_dim_plan_v3.4.0.md)
> **Audit log**: [stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md](stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md) — 9 轮 97 finding 详
> **Version history**: v0.1 → v0.2 → **v0.3 (双轨真化 + 97 闭环)**；详见 §11
> **SHA256 anchor**:
> - **Freeze anchor** (at git tag `v3.5.1-plan-frozen`, D-1.8 锚定 v0.3 initial freeze): `ac9088672fd25c7fa6ab06aef541e6d2cb31198afeeb9ffa3592c9cbc18b6b79`
> - **Current doc state** (post final-audit R1+R2 补全): 重新计算 via `sha256sum plan.md`; 与 freeze anchor 差异为正常 audit 反馈迭代 (R1 §2.5.3 20_substance 三角化 + R2 §2.6 README × 3 paper)

---

## §0. Pre-registration Freeze (Nosek 2018 PNAS additive supplementation — 修 R6-H2)

**关键 invariant**: 本 plan §2.1.3 article 公式（含真双轨）、§2.1.4 panel 聚合公式、§2.3.1 HTMT 阈值 0.85/0.90 双 cutoff、§2.4.2 Stata core_patterns 注入清单必须在 git tag `v3.5.1-plan-frozen` 之前**字节级冻结**。任何 D-day 启动后的 post-hoc revision 触发 epoch 7 audit + paper limitations 段标准声明。

**D-1 day 强制前置动作（修 R5-B1 + R9-BLOCKER-1）**：

| 序号 | 动作 | 验收 |
|---|---|---|
| D-1.1 | 检查/补打 `v3.5.0-augmentation` git tag at v3.5.0 release commit（CHANGELOG `../CHANGELOG.md` 顶部 hash）| `git tag --list \| grep v3.5.0-augmentation` |
| D-1.2 | grep `_analyze_single_article` 实际 token 流 + 否定词翻转语义 | 锁定分母 = 否定词翻转**前**的 jieba 分词 token count |
| D-1.3 | grep `tone_dicts.json::you_2018.definite/ambiguous` 完整结构 | 确认 list[str] / 388 词 / 178 词 |
| D-1.4 | cn2an PyPI 包评估（依赖增量决策） | 决策记录写入 audit log |
| D-1.5 | **先扩展 master plan `B_route_master_plan_v2.md §5.2.3.bis` schema 加 tA7/tA9/tA8 字段定义** | master plan epoch 7 audit cycle 触发 |
| D-1.6 | grep `stata_runner.py:303 build_replication_package` glob 行为 | 锁定 Stata 模板路径策略 |
| D-1.7 | 实测 shim count / test count / panel 列数；CLAUDE.md + plan 同步 | 一次性对齐 |
| D-1.8 | 计算 plan v0.3 SHA256 → 写入 §0 → `git tag v3.5.1-plan-frozen` | tag 创建 |

D-1 合计 ~1.9 wd（独立计入 §6）。

**Tag-over-hash 强制**：v3.5.0-augmentation 必须先存在 immutable git tag；plan 内所有 v3.5.0 commit references 解读为 "the commit pointed to by v3.5.0-augmentation tag at D0 day"。

---

## §1. 增量范围（in scope / out of scope）

### 1.1 in scope（v3.5.1 仅做 2 项 + 1 validation stage + Stata 全栈）

| 模块 | 内容 | 文献锚 | LLM 成本 |
|---|---|---|---|
| **A1** Lexical Clarity 激活（**真双轨**, 修 R3-C1）| 激活 `tone_dicts.json::you_2018.definite/ambiguous`；**`_analyze_single_article` 对 content_full + content_ctx 各调用一次**；article 派生 `clarity_score_{full,ctx}` 等 6 列；panel 聚合 6 列 | Loughran-McDonald (2011) JF 66(1); You (2018) hhx055; Bonsall (2017) JAE | $0 |
| **A3** Numerical Intensity（**真双轨**, 修 R3-C2）| 新模块 `numerical_intensity.py`；`compute_num_intensity` 对 content_full + content_ctx 各调用一次；article 派生 2 列；panel 聚合 2 列 | Hales-Kuang-Venkataraman (2011) CAR 28(1) | $0 |
| **39d** Lexical Discriminant Validity | HTMT (Henseler 2015 JAMS) + AVE/φ² (Fornell-Larcker 1981) + Cohen κ (1960 EPM) + Cronbach α (1951 Psychometrika) **across all 3 indicators** (修 R9-M2) | Henseler/Fornell/Bagozzi-Yi/Cohen/Cronbach | $0 |
| **Stata layer** | core_patterns +8 + HEURISTIC_LABELS +8（**单 SoT**：export.py from .stata_export import; 修 H2'）+ codebook +8 entries + Stata 模板 routing | 项目 R42-A | $0 |

### 1.2 out of scope（明确 defer）

| 项 | defer 到 | 原因 |
|---|---|---|
| A2 forward-looking 中文词表 | v3.5.2 | 词表 8-12 轮 audit |
| **LM 2011 中译版词典 (must-do robustness, 修 R4-M1 升级)** | **v3.5.2 must-do** | 与 A2 同批 ship；非 optional |
| **Du 2022 等其他词典对照 robust check (修 R9-M4)** | v3.5.2 | 与 LM 中译同批 |
| D3 媒体类型分类 | v3.6.0 | KB 500 媒体名整理 |
| B1 novelty / C1 exploration | v3.8.0+ | v3.5.0 plan §1.2 已 defer |
| B2 staleness | 独立立项 P10 | N² LSH + 新 paper_spec |
| A4 Fog 可读性 | 不做 | LM 2014 JF 公开反驳；**项目已实现近似版 `tone_words.py:372 _compute_readability`**，可在 v3.5.x 独立 PR ship（修 L1 + R3-L4'）|
| A5 NER | 不做 | LIWC concrete 不存在；A3 替代 |
| **Bartik IV for A1/A3** | v3.5.2 | A1/A3 作 **robustness 自变量**, 不替换主回归 (修 R5/M8) |
| build-replication **v2 升级版** CLI（修 R6-H3：v3.2.0 已有 v1 CLI per `stata_runner.py:440`）| v3.6.0 | v1 不变 |
| **A1 × text_coherence 互补** (strategic_diff) | v3.5.2 | 与 LM 中译同批 (修 M5') |
| **A1/A3 lagged design** | paper analysis.py 实现层 | 不在 plan 工程契约层 (修 L3') |
| **_compute_readability 聚合到 panel** | 独立 PR ship | 不与 A1/A3 同 PR (修 L4') |

### 1.3 与现有契约的不变量保证（修 R9-H4 加 jieba pin）

| 不变量 | 验证方式 |
|---|---|
| **Prompt v8 字节级冻结** | `config/prompts/unified_cot.txt` SHA256 锁定；CI hook 检 |
| **jieba == 0.42.1 frozen at D0**（修 R9-H4）| `requirements.lock:55` 已 pin；CI 自动检 |
| **9 paper_spec.yaml schema 兼容**（修 R6-C1）| **D-1.5 先扩 master plan §5.2.3.bis schema 加 tA*字段定义**；A1 仅扩 P3/P4/P5 tA7；A3 仅扩 P1 tA9 + benefit_society tA8；其余 4 paper explicit null |
| **CI 5 jobs 全绿** | A1/A3/39d/Stata 共 ~63 tests 均不 import torch |
| **panel schema 加列 idempotent** | 8 新列（修双轨 = 6 A1 + 2 A3）已存在则覆盖 |
| **Stata core/aux 边界 + 长期政策**（修 R7-H2 降 MED）| STATA_IC_MAX_VARS=2048；v3.5.1 +8 → ~103；v3.5.2 +6 → ~109；v3.6.0 +8 → ~117；v3.7.0 +30 → ~147；v3.8.0+ +6 → ~153。**v3.9.0+ 才需重审 core 政策** |
| **value_label 不涉及** | A1/A3 全 float64 |
| **golden v0 → v1 重生** | v0 archived 不删；test `parametrize(["v0","v1"])` 双轨过渡 |
| **回滚** | 整个 v3.5.1 PR `git revert` |
| **OUTPUT_REGISTRY 不触动** | 39d 是 validation stage |

---

## §2. 工程契约层

### 2.1 A1 Lexical Clarity 真双轨激活（修 R3-C1）

#### 2.1.1 修改 `pipeline/sentiment/tone_words.py`（**真双轨重写**）

| 位置 | 操作 | 行数 |
|---|---|---|
| `:172 load_all_dictionaries()` | 读 `you_2018.definite` (388) + `you_2018.ambiguous` (178)；返回 schema 加 2 frozenset；docstring `:34` 改 "v3.5.1 激活"。**D-1.3 验证 list[str] 结构**（修 R7-C1） | +15 行 |
| **新增 helper** `_compute_clarity_for_text(text, def_set, amb_set) -> dict` | 对**任意单一文本**做：jieba 分词（与现 `_analyze_single_article` 共用 token 流, **分母 = 否定词翻转前 jieba count**, D-1.2 验证）→ frozenset O(1) 计数 → 返回 `{n_definite, n_ambiguous, n_tokens_clarity_base}`；**这是真双轨的核心**——任意文本可独立扫描 | +30 行 |
| `:858 _dual_analyze()` | **在现有三轨循环内追加 A1 调用**：`res_full = _analyze_single_article(content_full)` 内嵌 `_compute_clarity_for_text(content_full)`；ctx 同；**title 轨不纳入**（修 R3-H1：text < 50 字符分母不稳）；写入 `clarity_*_full`, `clarity_*_ctx` 共 6 article 列 | +15 行 |
| `:1006 main()` | parquet 输出 +6 article 列 | +5 行 |

#### 2.1.2 修改 `pipeline/panel/encode_collab.py`

**命名锁定**：`apply_v3_5_0` 不动；新建独立入口 `apply_v3_5_1`；v3.6.0 合并方案（修 R9-M6）= 新建 `apply_supplementation` 统一入口，v3.5.0 entry 保留 deprecation alias 至 v3.7.0。

**签名差异说明**（修 L1'）：`apply_v3_5_1(df, panel) -> dict` 无 `ctx_baseline_path` 参数；v3.5.1 全样本派生不依赖 ctx coverage baseline。

| 函数 | 签名 | 行数 |
|---|---|---|
| `derive_clarity_signals(df) -> list[str]` | 从 article 6 列计算 `frac_definite_{full,ctx}` / `frac_ambiguous_{full,ctx}` / `clarity_score_{full,ctx}`；NaN 分母传播 | +30 行 |
| `aggregate_clarity_panel(df, panel) -> dict` | bank-year 聚合（详 §2.1.4）；**n_articles(b,t) ≥ 2 mask**（修 R8-H2）；返回包含 `median_amb_d0` 等 diagnostics | +35 行 |
| `apply_v3_5_1(df, panel) -> dict` | 顺序：A1 clarity → A3 num_intensity；**写 sidecar JSON `data/processed/v3_5_1_constants.json`**（修 C1' 序列化）含 `median_amb_d0` + `prompt_v8_sha256` + `stage21_last_run_timestamp`（修 R7-H1 双 anchor）| +25 行 |

#### 2.1.3 article 层公式（精确定义，frozen at D0；修 C3 + H1' + R8-M1）

```
# D-1.2 实测后锁定（不留二选项）：
n_tokens_clarity_base_i = jieba_token_count(text_i)
    [否定词翻转**前**计数；与 LM 2011 JF §3 一致 (后处理不影响分母)]
    [空/单字符 text → n_tokens_clarity_base = 0 → pd.NA]

frac_ambiguous_full_i  = n_ambiguous_full_i / n_tokens_clarity_base_full_i    [NA if 分母=0]
frac_definite_full_i   = n_definite_full_i  / n_tokens_clarity_base_full_i
clarity_score_full_i   = frac_definite_full_i − frac_ambiguous_full_i   ∈ [−1, +1]

frac_ambiguous_ctx_i   = n_ambiguous_ctx_i / n_tokens_clarity_base_ctx_i   [独立扫描 content_ctx]
frac_definite_ctx_i    = n_definite_ctx_i  / n_tokens_clarity_base_ctx_i
clarity_score_ctx_i    = frac_definite_ctx_i − frac_ambiguous_ctx_i
```

**ctx 分母 / full 分母不直接可比 disclosure**（修 R3-H2）：ctx 文本约为 full 的 20-50%，paper §3.4 加 limitation 段。

#### 2.1.4 panel 层聚合（精确定义，frozen at D0；修 H2 + R8-H2 + R9-M3）

```
w_i = stage21_media_authority_weight_i × herd_decay_weight_i
      [与 llm_vote_tone 同权重]

mean_clarity_score_full[b,t] = Σ_{i ∈ cell(b,t)} w_i × clarity_score_full_i / Σ w_i
mean_clarity_score_ctx[b,t]  = Σ_{i ∈ cell(b,t)} w_i × clarity_score_ctx_i  / Σ w_i

mean_frac_definite_full[b,t] = Σ w_i × frac_definite_full_i / Σ w_i  [连续指标, 不损信息, 修 R9-M3]
mean_frac_definite_ctx[b,t]  = (同上)

# D0 frozen 全样本中位数 (双 anchor, 写 sidecar JSON, 修 H2 + R7-H1 + C1')
median_amb_d0 = median(frac_ambiguous_full_i for i in ALL_articles_at_D0)
    [anchored to: prompt_v8 SHA256 + stage21_last_run_timestamp]
    [stored in data/processed/v3_5_1_constants.json (sidecar, in replication package)]

# 二值化指标（保留信息损失备份，连续版上面已并行报）
frac_amb_articles_full[b,t] = #{i: frac_ambiguous_full_i ≥ median_amb_d0 ∧ n_articles(b,t) ≥ 2} / n_articles(b,t)
frac_amb_articles_ctx[b,t]  = (同上)
    [n_articles=1 cell → pd.NA (修 R8-H2)]
```

#### 2.1.5 panel 列清单（A1 共 8 列，修 R9-M3 加连续指标）

| 列名 | 说明 | dtype |
|---|---|---|
| `mean_clarity_score_full` | A1 Full-track 连续 | float64 |
| `mean_clarity_score_ctx` | A1 Ctx-track 连续 | float64 |
| `mean_frac_definite_full` | A1 Full-track 连续 (备份) | float64 |
| `mean_frac_definite_ctx` | A1 Ctx-track 连续 (备份) | float64 |
| `frac_amb_articles_full` | A1 Full-track 二值化聚合 | float64 |
| `frac_amb_articles_ctx` | A1 Ctx-track 二值化聚合 | float64 |
| (—) | — | — |
| (—) | — | — |

实际 A1 = **6 panel 列**（原 plan 漏 `mean_frac_definite_*` 备份；v0.3 补齐 = 6 列）。

### 2.2 A3 Numerical Intensity 真双轨（修 R3-C2）

#### 2.2.1 新模块 `pipeline/sentiment/numerical_intensity.py`

| 函数 | 签名 | 行数 | 说明 |
|---|---|---|---|
| `_cn2arab(text: str) -> str` | 中文数字 → 阿拉伯字符串 | ~50 行 | **D-1.4 cn2an 评估后**：若引入 = wrapper ~10 行；若自实现 = 50 行（详 §11 cn2an 决策） |
| `_count_numerical_tokens(text: str) -> tuple[int, int]` | 返回 `(n_numeric_tokens, n_sentences)`；句子切分用 `r'(?<!\d)[。！？.!?](?!\d)'`（**lookahead/behind 排除小数点**, 修 M1'）；不计分号 `；`（与 LM 一致）；不定数（"几千" "数十亿"）**不计为数字 token**（修 R7-M2）| ~30 行 | — |
| `compute_num_intensity(content: str) -> float` | `n_numeric / max(n_sentences, 1)`；空文本/单字 → `pd.NA`（修 R8-M1）| ~15 行 | — |
| `enrich_with_num_intensity_dual_track(df) -> pd.DataFrame` | **post-processor for `_dual_analyze`**（修 R3-C2 + H4）：对 `df['内容']` 和 `df['content_ctx']` 各调用一次，写入 `num_intensity_full` + `num_intensity_ctx` 两列 | ~30 行 | 单向依赖 tone_words → numerical_intensity |

#### 2.2.2 cn2arab 5 标准样例（frozen at D0，修 H1）

| 输入 | cn2arab 输出 | 数字 token 数 |
|---|---|---|
| `两千万` | `20000000` | 1 |
| `三亿五千万` | `350000000` | 1（不拆 3 + 5） |
| `1.5 亿` | `150000000` | 1 |
| `百分之三十` | `30%` | 1 |
| `30 万亿元` | `30000000000000元` | 1 |
| **不定数 `几千` / `数十亿` / `上百万`** | **保留原文不转** | **0（不计为 token, 修 R7-M2）** |

#### 2.2.3 修改 `tone_words.py`（调用顺序锁定，修 H4）

```python
# tone_words.py main() 末尾追加
from news_process.pipeline.sentiment.numerical_intensity import enrich_with_num_intensity_dual_track
df = enrich_with_num_intensity_dual_track(df)
```

依赖方向 = `tone_words → numerical_intensity`（单向）。

#### 2.2.4 公式（精确定义，frozen at D0）

```
num_intensity_full_i = count(matches of digit_regex in cn2arab(content_full_i))
                     / max(count of [。！？.!?] in content_full_i with lookahead/behind, 1)
num_intensity_ctx_i  = (同上, 对 content_ctx_i 独立扫描；ctx 残半句已被 entity_context 完整句号过滤, 修 R3-H3)

mean_num_intensity_full[b,t] = Σ w_i × num_intensity_full_i / Σ w_i
mean_num_intensity_ctx[b,t]  = Σ w_i × num_intensity_ctx_i  / Σ w_i

# 中文 sentence 分母与英文 Hales 2011 不直接可比 disclosure (paper §3.4, 修 R7-M1)
# 同时报 word-level 替代版: digit_count / total_words (修 R4-m1, paper §4.3)
```

### 2.3 Stage 39d Lexical Discriminant Validity

| 项 | 值 |
|---|---|
| Shim | `news_process/39d_lexical_discriminant_validity.py` (~25 行) |
| 实现 | `pipeline/audit/lexical_discriminant_validity.py` (~200 行) |
| 注册 | `core/dag.py::STAGES_VALIDATION` 末追加 |
| **DAG 依赖（修 R7-M4）** | `dependencies=["22_tone_words.py", "46_panel_export_main.py"]` 双依赖 |
| 输出 | `data/processed/39d_lexical_discriminant.parquet` + `data/processed/39d_htmt_matrix.json` |
| 测试 | `tests/test_39d_lexical_discriminant.py` (~12 tests) |
| OUTPUT_REGISTRY | 不进 |
| **算法路径锁定（修 R7-H3 + R8-H3 OOM）** | **pairwise on-disk**: 每对 indicator 单独读 parquet 计算 cross-correlation；内存峰值 < 1 GB；CI heavy job 4 GB ceiling 安全 |
| **Permutation seed（修 R9-H3）** | `seed=42`（与 `pipeline/audit/inter_track_kappa.py:41` 一致） |

#### 2.3.1 检验矩阵（3 × 3，frozen at D0）

行/列 = T1 LLM substance / T2 A1 clarity / T3 A3 num_intensity（panel 层 bank-year obs）。

| 指标 | 计算 | **双 cutoff**（修 R4-M2）| 通过 | 失败 fallback |
|---|---|---|---|---|
| **HTMT_ij** (Henseler 2015) | `mean(cross-corr) / sqrt(mean(within-corr_i) × mean(within-corr_j))` | < 0.85 strict / < 0.90 lenient | strict | strict fail / lenient pass = paper §3.4 disclosure + reposition |
| **AVE_i / φ²_ij** (Fornell-Larcker 1981) | √AVE > max φ | — | — | — |
| **Cohen κ** (LLM substance vs `clarity_score < median`, **正向锁定**：象征性 (1) ↔ ambiguous (1), 预期正 κ, 修 M2') | 2-class nominal agreement | κ ∈ [0.2, 0.6] = 中度互补 | 0.2-0.6 | κ > 0.7 = 重叠；同时报 **Spearman ρ** (修 R4-m3) 避免 dichotomize 损失 |
| **Cronbach α** (**across all 3 indicators**, 修 R9-M2) | reliability of substance+clarity+num_intensity 作 reflective 测度 | α > 0.7 | reflective | reposition formative |

**ctx-fallback HTMT mask（修 R8-H1 + 合并组 CTXQ）**：HTMT 计算前剔除 `content_ctx == content_full` 的 article 子集（约 10-30%），避免假 disagree = 0 信号。

**Panel HTMT 适用性（修 R9-M1）**：传统 HTMT 假设 IID；本项目是 N=500 × T=18 panel。HTMT 计算用 bank-clustered SE bootstrap，**或在 paper §3.4 加 "applying cross-sectional HTMT to panel as conservative diagnostic per Henseler 2015 footnote 11" 的 limitation 声明**。

**双层 HTMT 并报（修 M11）**：

| 层 | sample | 时间 | CI job |
|---|---|---|---|
| article 层 | ~400K obs | pairwise on-disk 5-10 min | heavy |
| bank-year 层 | ~9K obs | < 1 min | light |

### 2.4 Stata Export Layer 全栈同步（修 plan v0.1 漏 + H2' 单 SoT）

#### 2.4.1 修改 `pipeline/panel/stata_export.py`

| 位置 | 操作 | 行数 |
|---|---|---|
| `:146 HEURISTIC_LABELS` | 加 8 entries（每条 ≤ 80 UTF-8 bytes；变量名 ≤ 32 char 已验证, 修 M3') | +12 行 |
| `:215 core_patterns` | 加 8 列名（core 列 ~95 → ~103, 远低于 IC 2048） | +10 行 |

**HEURISTIC_LABELS 8 entries（frozen at D0；修 R3-M2 描述更新）**：

| Panel 列 | English Label (≤ 80 bytes) |
|---|---|
| `mean_clarity_score_full` | `Mean Clarity Score from indep Full-text scan (LM 2011 JF; You 2018)` |
| `mean_clarity_score_ctx` | `Mean Clarity Score from indep Ctx-text scan (LM 2011 JF; You 2018)` |
| `mean_frac_definite_full` | `Mean Frac Definite from indep Full scan (You 2018 Panel C 388 words)` |
| `mean_frac_definite_ctx` | `Mean Frac Definite from indep Ctx scan (You 2018 Panel C 388 words)` |
| `frac_amb_articles_full` | `Frac Articles Ambiguous Full (>=D0 median, You 2018 Panel D)` |
| `frac_amb_articles_ctx` | `Frac Articles Ambiguous Ctx (>=D0 median, You 2018 Panel D)` |
| `mean_num_intensity_full` | `Mean Numerical Intensity Full (Hales 2011 CAR, dual-track)` |
| `mean_num_intensity_ctx` | `Mean Numerical Intensity Ctx (Hales 2011 CAR, dual-track)` |

#### 2.4.2 修改 `pipeline/panel/codebook.py`

为 8 新列添加 codebook 元数据（label / description / unit / range / source）；按现有结构追加。

#### 2.4.3 修改 `pipeline/panel/export.py`（**单 SoT**, 修 H2'）

```python
# export.py 顶部 import
from news_process.pipeline.panel.stata_export import HEURISTIC_LABELS as _STATA_LABELS
# var_label_map 不再独立维护 8 entries，直接引用 _STATA_LABELS
```

### 2.5 Stata Templates routing（修 plan v0.1 路径 + H3' build glob 风险）

#### 2.5.1 路径策略（**D-1.6 grep 后锁定**）

| 选项 | 触发条件 |
|---|---|
| **选项 A**：paper-specific 子目录（`bank_fintech_substance/21_xxx`）| `build_replication_package` glob **递归** to paper-specific 子目录 ✓ |
| **选项 B**（fallback）：`v3_5_1/` root 子目录（`v3_5_1/26_xxx`）| glob 非递归 → 必须放 v3_5_1/ 隔离区 |

#### 2.5.2 A1 + A3 模板路径锁定（按 D-1.6 决策）

**选项 A 路径（预期默认）**：

| 模板路径 | 用途 | 与现有模板关系 |
|---|---|---|
| `papers/_common/stata_templates/bank_fintech_substance/21_substance_clarity_robustness.do.tmpl` | A1 P3 Table A7 | 紧跟现 20_substance_disclosure_quality |
| `papers/_common/stata_templates/bank_fintech_substance/20_substance_disclosure_quality.do.tmpl` | 扩 +15 行：A1 与 ln_fintech_mdna_length **三角化** Panel C | 现有模板扩展 |
| `papers/_common/stata_templates/bank_fintech_locus/19_locus_clarity_robustness.do.tmpl` | A1 P4 Table A7 | 紧跟现 18_locus_robustness |
| `papers/_common/stata_templates/bank_fintech_collab/20_collab_clarity_robustness.do.tmpl` | A1 P5 Table A7 | 紧跟现 19_collab_event_study |
| `papers/_common/stata_templates/bank_fintech_tone/` (D-1.6 确认是否存在；若无→ `v3_5_1/27_tableA9_num_intensity.do.tmpl`) | A3 P1 Table A9 | — |
| `papers/_common/stata_templates/benefit_society/19_bs_num_intensity_robustness.do.tmpl` | A3 BS Table A8 | — |
| `papers/_common/stata_templates/01_data_prep.do.tmpl` | 扩 +5 行 winsorize 1%/99%（用 `capture confirm variable` guard, 修 M4'）| 现有共用模板 |

#### 2.5.3 Stata 模板示例（修 L6 JSON 注入）

`21_substance_clarity_robustness.do.tmpl`：

```stata
* Table A7: Lexical Clarity Robustness (LM 2011 JF style; dual-track)
version 19
clear all
set maxvar 32767

if "$data_dir" == "" global data_dir "../data"
if "$tables_dir" == "" global tables_dir "../output/tables"
use "$data_dir/_prepared_panel.dta", clear

* Panel A: Main DV on dual-track clarity
reghdfe {{MAIN_DV}} mean_clarity_score_full mean_clarity_score_ctx $bank_controls, ///
    absorb(bank_id year) vce(cluster bank_id year)
estimates store M1

* Panel B: LLM substance × clarity_full interaction (discriminant per HTMT)
reghdfe {{MAIN_DV}} c.mean_clarity_score_full##c.{{MAIN_TREAT}} $bank_controls, ///
    absorb(bank_id year) vce(cluster bank_id year)
estimates store M2

* Panel C: 三角化 (with ln_fintech_mdna_length, 修 §2.5.2)
capture confirm variable ln_fintech_mdna_length
if !_rc {
    reghdfe {{MAIN_DV}} mean_clarity_score_full ln_fintech_mdna_length {{MAIN_TREAT}} $bank_controls, ///
        absorb(bank_id year) vce(cluster bank_id year)
    estimates store M3
}

* HTMT diagnostic (jinja-rendered scalar, 修 L6)
local htmt_subst_clarity = "{{ HTMT_SUBST_CLARITY }}"
di "HTMT(substance, clarity) = `htmt_subst_clarity'"

esttab M1 M2 M3 using "$tables_dir/tableA7_clarity_robustness.tex", ///
    se star(* 0.10 ** 0.05 *** 0.01) replace
```

### 2.6 现有 codebook + README + memory 同步（修 plan v0.1 漏 + M4'）

| 文件 | 操作 |
|---|---|
| `pipeline/panel/codebook.py::get_variable_metadata_dict()` | +8 entries |
| `papers/_common/stata_templates/README.md` | 新模板表 |
| `papers/_common/stata_templates/bank_fintech_substance/README.md` | +21_xxx 行 |
| `papers/_common/stata_templates/bank_fintech_locus/README.md` | +19_xxx 行 |
| `papers/_common/stata_templates/bank_fintech_collab/README.md` (D-1.6 确认) | +20_xxx 行 |
| `MEMORY.md` 索引 | 加 `v3_5_1_landmarks.md`；shim_inventory.md **29→30**（实测）；`v3_5_0_landmarks.md` 反向 link（修 R6-M4） |

---

## §3. 数据流与 DAG 影响

| 阶段 | 当前 (v3.5.0) | v3.5.1 后 | 变更 |
|---|---|---|---|
| stage 22 (`tone_words`) | 5 词典 score 三轨（full+ctx+title） | 同上 **+** 6 A1 article 列 (full+ctx)（**title 不纳入**, 修 R3-H1）**+** 2 A3 article 列 (full+ctx) | schema-additive |
| stage 45/46 panel export | panel ~2024 列（D-1.7 实测对齐）| **panel ~2032 列 (+8)**：A1 6 + A3 2 | core ~95→103 远低于 IC 2048 |
| stage 39d (新加 validation) | — | 2 副产物到 `data/processed/` + sidecar `v3_5_1_constants.json` | 不进 OUTPUT_REGISTRY |

### 3.1 DAG 注册

```python
StageSpec(
    name="阶段39d: A1/A3 lexical discriminant validity (HTMT + AVE + κ + α; pairwise on-disk)",
    script="39d_lexical_discriminant_validity.py",
    dependencies=["22_tone_words.py", "46_panel_export_main.py"],  # 修 R7-M4 双依赖
    optional=True,
),
```

---

## §4. 测试 gate

### 4.1 新增测试（63 tests，修 M1 数字统一）

| 测试文件 | 数 | 关键 assertion |
|---|---|---|
| `tests/test_clarity_score.py` | 12 | 词典加载 388/178；`clarity ∈ [−1,+1]`；**双轨独立扫描验证**（content_full ≠ content_ctx 时 score 应不同）；空/单字符 NA；全角空格鲁棒；**list[str] 结构验**（修 R7-C1）|
| `tests/test_numerical_intensity.py` | 10 | 5 cn2arab 标准 + 不定数不计；句子 lookahead/behind 排除小数点；空文本 NA；单句多数字；跨段落；分号不计 |
| `tests/test_a1_a3_panel_aggregation.py` | 8 | 单 article cell（NA per R8-H2）；多 article weighted；ctx 缺失；NA 传播；idempotent；D2 cell_id 联动；D4 残差联动；order independence |
| `tests/test_39d_lexical_discriminant.py` | 12 | HTMT < 1.0；AVE/φ²；Cronbach α across 3 indicators > 0.7；κ ∈ [0.2,0.6]；**seed=42** 可重现（修 R9-H3）；ctx-fallback mask 排除（修 R8-H1）；pairwise on-disk 内存 < 1GB（修 R7-H3） |
| `tests/test_stata_export_v3_5_1.py` | **8**（修 L2'）| 8 新列 in core；8 label ≤ 80 bytes；变量名 ≤ 32 char（修 M3'）；STATA_IC_MAX_VARS 不越界；中英 label 一致；HEURISTIC_LABELS import 链（修 H2'）；codebook 同步；旧 panel graceful |
| `tests/integration/test_v3_5_to_v3_5_1_migration.py` | 6 | 加载旧 panel 自动补 8 列 NA；golden v0→v1 hash；双 idempotent；median_amb_d0 sidecar JSON 存在（修 C1'）；Stata IC core ≤ 2048；HEURISTIC_LABELS 与 var_label_map 同步 |
| `tests/integration/test_v3_5_1_forward_compat.py` | 3 | tokenizer 稳定；clarity 不被 forward-looking 污染；panel schema 前兼容 |
| `tests/integration/test_dag_consistency.py` (扩) | +2 | 39d in VALIDATION 且 not in REGISTRY |
| `tests/integration/test_paper_spec_schema.py` (扩) | +3 | P3/P4/P5 tA7 + P1 tA9 + BS tA8 字段（**修 R6-C1：master plan §5.2.3.bis 扩 schema 后才能加 test**）|
| `tests/integration/test_paper_spec_panel_col_reverse.py` | 3 | 反向 schema 验证 |
| **小计** | **67** | — |

> TDD ratio = 67 / ~500 行 = 0.13（项目历史 0.10-0.15 区间内）。

### 4.2 集成 gate

| Gate | 通过条件 |
|---|---|
| **G1 fast baseline** | `pytest -m fast` D-1.7 实测 baseline → +67 全绿 |
| **G2 integration** | 全绿 + golden v1 hash 对照 + sidecar JSON 存在 |
| **G3 panel reproducibility** | golden v1 下通过 |
| **G4 39d discriminant** | strict HTMT < 0.85 或 lenient < 0.90（修 R4-M2 双 cutoff） + seed=42 可重现 |
| **G5 Stata IC compat + 8 列写 .dta**（修 R5-H3 + plan v0.1 漏） | core ≤ 2048；8 label ≤ 80 bytes；codebook 不抛；**导出 .dta 后 Stata describe 验证 8 列存在且 float64** |
| **G6 CI 5-job 全绿（含 4GB memory ceiling）**（修 R8-H3） | 4 light + 1 heavy 全部 PASS, heavy peak memory < 4 GB |

### 4.3 Golden baseline 重生（修 R8-M3 prereq check）

```bash
# 0. Prereq: panel parquet 存在性 check（修 R8-M3）
[ -f data/processed/40_panel_yearly.parquet ] || { echo "ERROR: panel parquet missing"; exit 1; }

# 1. Archive v0
cp tests/fixtures/golden_panel_v0.json tests/fixtures/golden_panel_v0_archived.json

# 2. 重生
python scripts/migrate/generate_golden_snapshot.py --version v1

# 3. Schema-additive 检查
diff golden_panel_v0.json golden_panel_v1.json

# 4. 验证
pytest tests/integration/test_panel_reproducibility.py

# 5. Stata IC check
python -c "from news_process.pipeline.panel.stata_export import assign_core_columns; \
    import pandas as pd; df = pd.read_parquet('data/processed/40_panel_yearly.parquet'); \
    core = assign_core_columns(df); assert len(core) <= 2048"

# 6. Commit
git add tests/fixtures/golden_panel_v1.json tests/fixtures/golden_panel_v0_archived.json
git commit -m "v3.5.1: regenerate golden_panel_v1.json (+8 cols: 6 A1 + 2 A3 dual-track)"
```

---

## §5. 文档同步清单（**修 R6-H1 路径 + R6-M2/M3 漏**）

| 文件 | 改动 | 优先级 |
|---|---|---|
| `docs/methodology/stage3_v3_5_1_a1_a3_supplementation_plan.md` | **本文档 v0.3** | P0 |
| `docs/methodology/stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md` | **9 轮 97 finding 全闭环 audit log**（已创建） | P0 ✅ |
| **`../CHANGELOG.md`**（**项目根，非 news_process/**, 修 R6-H1） | v3.5.1 entry | P0 |
| `CLAUDE.md` | 顶部版本 v3.5.0→v3.5.1；test baseline D-1.7 实测对齐；shim 29→30 | P0 |
| `core/dag.py` | STAGES_VALIDATION 末追加 39d | P0 |
| `pipeline/sentiment/tone_words.py` docstring | "definite/ambiguous 仅存档" → "v3.5.1 真双轨激活" | P0 |
| `pipeline/sentiment/numerical_intensity.py` | **新建** | P0 |
| `pipeline/panel/encode_collab.py` | `apply_v3_5_1` + 3 函数 | P0 |
| `pipeline/panel/stata_export.py` | core_patterns +8 + HEURISTIC_LABELS +8 | P0 |
| `pipeline/panel/codebook.py` | +8 entries | P0 |
| `pipeline/panel/export.py` | import HEURISTIC_LABELS（单 SoT, 修 H2'） | P0 |
| `pipeline/audit/lexical_discriminant_validity.py` | **新建** 39d | P0 |
| `core/schemas_yaml.py`（修 R6-M3） | 检查是否需更新 schema | P0 |
| **`pyproject.toml::[project].dependencies`**（修 R6-M2 / R5-H2 cn2an）| D-1.4 决策后更新 | P0 |
| **`requirements.lock`**（修 R6-M1 cn2an）| `pip-compile` 重生 if cn2an 引入 | P0 |
| `papers/bank_fintech_substance/paper_spec.yaml` | `tables.tA7.clarity_robustness` | P0 |
| `papers/bank_fintech_locus/paper_spec.yaml` | `tables.tA7` | P0 |
| `papers/bank_fintech_collab/paper_spec.yaml` | `tables.tA7` | P0 |
| `papers/bank_fintech_tone/paper_spec.yaml` | `tables.tA9.num_intensity_robustness` | P1 |
| `papers/benefit_society/paper_spec.yaml` | `tables.tA8` | P1 |
| 其余 4 paper_spec.yaml | `tables.tA7/A8/A9` explicit null | P0 |
| **Stata 模板** | 详 §2.5 | P0/P1 |
| `papers/_common/stata_templates/README.md` | 新模板表 | P1 |
| 3-4 paper README | +1 行 | P1 |
| `data/processed/v3_5_1_constants.json` (**sidecar**, 修 C1') | D0 day 计算 median_amb_d0 + prompt_v8 SHA256 + stage 21 timestamp 后写入 | P0 |
| `MEMORY.md` 索引 | `v3_5_1_landmarks.md` + `v3_5_0_landmarks.md` 反向 link | P0 |
| **`B_route_master_plan_v2.md §5.2.3.bis`**（**修 R6-C1 prerequisite**）| 扩 schema 加 tA7/tA9/tA8 字段定义；触发 master plan epoch 7 audit | **D-1.5** |

---

## §6. 时间表（修 M10 + Stata 层 + D-1 day）

### 6.1 P50

| 阶段 | wd | 日期（2026-05-19 D-1）|
|---|---|---|
| **D-1** 8 项 prerequisite（详 §0 表）| **1.9** | 2026-05-19–20 |
| **D0** plan v0.3 freeze + SHA256 + sidecar JSON 计算 + audit log epoch 7 streak 1/3 入条目 | 0.5 | 2026-05-21 |
| **D1** A1 真双轨实施（_compute_clarity_for_text + _dual_analyze 嵌入 + 12 tests） | 1 | 2026-05-22 |
| **D2** A3 真双轨实施（_dual_track post-processor + cn2arab + 10 tests） | 1.5 | 2026-05-22–25 |
| **D3** 39d 实施（HTMT pairwise on-disk + AVE + κ + α + 12 tests + 双层 + seed=42） | 1.5 | 2026-05-26 |
| **D4** Stata 层（stata_export + codebook + export.py 单 SoT + 8 tests） | 1 | 2026-05-27 |
| **D5** paper_spec × 9 + Stata 模板 × 4-5 + 现有扩展 + golden v1 + sidecar JSON | 1 | 2026-05-28 |
| **D6** integration gate + CHANGELOG（`../`）+ CLAUDE.md + MEMORY.md | 1 | 2026-05-29 |
| **A1-A3** 多视角 audit ≥ **8 轮**（V1-V15 + EiC + 同行复审）（修 R6-L1 audit ≥ 8 项目标准） | **3.5** | 2026-05-30–06-05 |
| **release tag** `v3.5.1-supplementation` | 0.5 | 2026-06-06 |
| **合计** | **~13.4 wd** | **calendar ~17-20 wd** |

### 6.2 P99

| 风险触发 | 加 wd | 累积 |
|---|---|---|
| G4 HTMT > 0.90 → reposition | +2 | 15.4 |
| cn2arab 边界 5 轮 audit | +3 | 18.4 |
| Stata core 越界（极低）| +1 | 19.4 |
| golden v1 跨 paper 连锁 | +2 | 21.4 |
| paper_spec schema 微调 4-5 轮 | +3 | 24.4 |
| master plan epoch 7 audit 触发（D-1.5）| +2 | 26.4 |
| **P99 合计** | — | **~26.4 wd / calendar 35-40 wd** |

---

## §7. 风险矩阵（修 R7-M3 disclosure ex-ante 防御）

| ID | 描述 | 严重 | 概率 | mitigation |
|---|---|---|---|---|
| R1 | A1 HTMT > 0.90 | HIGH | 15% | reposition "convergent triangulation"；double cutoff (strict/lenient) |
| R2 | A3 cn2arab 边界 | MED | 25% | 5 标样 + 不定数排除 + 100 spot-check + cn2an 评估 |
| R3 | golden v1 跨 paper 连锁 | MED | 25% | v0 archived；`parametrize(["v0","v1"])` 双轨；具体受影响 paper = P1/P2/P3/BS（直接引列），其余 4 paper explicit null 隔离 |
| R4 | 39d 缺列 | LOW | 15% | track_optional + 与 D4 联动 |
| R5 | endogeneity | HIGH | 80% | A1/A3 **robustness 不替主**；现有 Bartik IV/Oster；**v3.5.2 补专属 IV** |
| R6 | LM 297 vs You 178 | MED | 40% | **v3.5.2 LM 中译 must-do**（修 R4-M1）|
| R7 | num_intensity 饱和 | MED | 30% | IQR/median ≤ 0.3 → winsorize 1%/99%；clarity 同 winsorize fallback（修 R8-M4） |
| R8 | 39d heavy job OOM | LOW | <5% | pairwise on-disk 1GB；CI 4GB ceiling |
| R9 | Stata core +8 越 IC | LOW | <1% | 当前 ~95+8=103 远低于 2048；G5 检测 |
| R10 | paper_spec tA* schema | LOW | 5% | D-1.5 先扩 master plan schema |
| R11 | P1 Stata 子目录缺 | LOW | 50% | D-1.6 实测；fallback v3_5_1/ root |
| **R12**（新, 修 R9-CRIT-1） | plan 跨 session 一致性 | LOW | 10% | git tag `v3.5.1-plan-frozen` + audit log 持久化 |

**Disclosure 累计降至 3 处**（修 R7-M3 ex-ante 防御后剩）：(1) A1 You 178 vs LM 297 覆盖差；(2) ctx 分母与 full 不直接可比；(3) Hales 2011 sentence 分母中文迁移。

---

## §8. 决策门控

| ID | 触发 | 用户决策 | 默认 |
|---|---|---|---|
| **G-A0** D-1 prerequisite | 8 项 D-1 动作全部完成 | 用户确认每项 | block |
| **G-A1** D0 plan v0.3 freeze | SHA256 + sidecar + median_amb_d0 | 用户确认 | block |
| **G-A2** 39d HTMT report | strict / lenient / fail | reposition / abort / pass | block |
| **G-A3** golden v1 重生 | 8 新列样例 | 用户审 | block |
| **G-A4** Stata 路径决策 (R11) | paper-specific vs v3_5_1/ root | 用户确认 | block |
| **G-A5** master plan §5.2.3.bis epoch 7 audit（**新, 修 R6-C1**） | schema 扩 tA* 完成 | 用户确认 master plan v2.x 释放 | block |
| **G-A6** release | CHANGELOG + paper_spec + Stata + codebook + sidecar 同步 | 用户确认 | block |
| **G-A7** (optional) Bartik IV 重跑 | 用户判断 | default skip |

合计 6 hard + 1 optional。

---

## §9. Release tag（修 R5-B1）

| Tag | 时机 | 锚定 |
|---|---|---|
| `v3.5.0-augmentation` | **D-1.1 补打** at v3.5.0 release commit | v3.5.0 release |
| `v3.5.1-plan-frozen` | D-1.8 | plan v0.3 SHA256 |
| `v3.5.1-impl-d6` | D6 | code + tests 全绿 |
| `v3.5.1-supplementation` | release | post-audit |

**回滚**：`git revert v3.5.1-supplementation..v3.5.0-augmentation && pytest -m fast`

---

## §10. 锚定文献清单（修 H3 + M5 + L4 + R6-H2）

| 引用 | 用途 | 卷期 |
|---|---|---|
| Loughran & McDonald (2011) | A1 主锚 | JF 66(1), 35-65 |
| **You et al. (2018) hhx055** (D-1 day 完整 BibTeX 核, 修 M5) | A1 中文 Panel C/D | (待 D-1 Google Scholar 核) |
| Bonsall, Leone, Miller, Rennekamp (2017) | A1 补强 | JAE 63(2-3), 329-357 |
| Baker, Bloom, Davis (2016) | A1 远锚 | QJE 131(4), 1593-1636 |
| Hales, Kuang, Venkataraman (2011) | A3 主锚 | CAR 28(1), 305-339 |
| Davis, Tama-Sweet (2012) (D-1 day 核, 修 L4) | A3 补强 | CAR 29(3), 804-837 |
| Henseler, Ringle, Sarstedt (2015) | HTMT | JAMS 43, 115-135 |
| Fornell, Larcker (1981) | AVE/φ² | JMR 18(1), 39-50 |
| Bagozzi & Yi (1988) | 构念效度 | JAMS 16, 74-94 |
| **Cohen (1960)** (修 H3) | κ | EPM 20(1), 37-46 |
| **Cronbach (1951)** (修 H3) | α | Psychometrika 16(3), 297-334 |
| **Nosek et al. (2018)** (修 R6-H2) | Pre-registration | **PNAS 115(11), 2600-2606** ("additive supplementation" framework) |

---

## §11. Audit Trail — v0.1 → v0.2 → v0.3 修正 mapping

> **完整 9 轮 97 finding 详**：见 [audit log 文件](stage3_v3_5_1_a1_a3_supplementation_plan_audit_log.md) §2

### 11.1 v0.1 → v0.2 27 findings closed（**真闭环验证, 修 R9-CRIT-1**）

| 修正组 | 真闭环度 | 验证位置 |
|---|---|---|
| 3 CRITICAL (C1+C2+C3) | ✅ 已在 v0.3 §0 D-1.1 + §2.1.2 命名锁定 + §2.1.3 公式锁定（不留二选项） | v0.3 §0 / §2.1 |
| 6 HIGH (H1-H6) | ✅ v0.3 §2.2.1 cn2arab 5 样例 frozen + §2.1.4 median_amb_d0 sidecar JSON + §10 Cohen/Cronbach + §2.2.3 调用顺序 + §3 panel 列数 D-1.7 实测 + §12 ρ 表述 | v0.3 各章节 |
| 11 MED (M1-M11) | ✅ v0.3 §4.1 测试数 67 + 各项已修 | v0.3 §4 / §10 / §6 / §7 |
| 7 LOW (L1-L7) | ✅ 各项已修 | v0.3 §1.2 / §5 / §2.1.1 / §10 / §7 / §2.5.3 / §11 |

### 11.2 v0.2 → v0.3 70 新 findings closed

| 来源轮次 | findings | 闭环 |
|---|---|---|
| R2 第 2 轮 V1-V12 (14) | C1' / H1'-H3' / M1'-M6' / L1'-L4' | ✅ 全闭（详 audit log §2） |
| R3 第 3 轮 V1-V15 (9, 含双轨核查) | R3-C1/C2 / R3-H1-H3 / R3-M1-M3 / R3-L1 | ✅ 全闭，R3-C1/C2 是 v0.3 主重写 |
| R4 第 4 轮 同行评议 (7) | R4-M1/M2 + R4-m1-m5 | ✅ 全闭 |
| R5 第 5 轮 D-day 压力 (6) | R5-B1 + R5-H1-H3 + R5-l1/l2 | ✅ 全闭 |
| R6 第 6 轮 完备性 (10) | R6-C1 + R6-H1-H3 + R6-M1-M4 + R6-L1/L2 | ✅ 全闭 |
| R7 第 7 轮 对抗性 (9) | R7-C1 + R7-H1-H3 + R7-M1-M4 + R7-L1 | ✅ 全闭 |
| R8 第 8 轮 边缘 case (9) | R8-H1-H3 + R8-M1-M4 + R8-L1/L2 | ✅ 全闭 |
| R9 第 9 轮 EiC desk check (14) | R9-BLOCKER-1 + R9-CRIT-1 + R9-H1-H5 + R9-M1-M7 + R9-L1/L2 | ✅ 全闭（含本 §11 本身 = R9-CRIT-1 修正）|

### 11.3 v0.3 期望状态

| 维度 | 目标 |
|---|---|
| Round 10 audit | finding = 0 |
| Plan 物理完整性 | ✅ audit log 存在 |
| 双轨契约真化 | ✅ |
| Pre-registration freeze | ✅ 0 BLOCKER + 0 CRITICAL |
| Disclosure 累积 | 3 处（不可消除）|
| Stata 层 | 99% |
| audit_rounds_target_min: 8 | ✅ 9 轮已达成 |
| Streak | epoch 7 streak 1/3 (v3.5.1 PR 启动) |

---

## §12. Non-technical Summary

**A1 给 P3/P4/P5 作者带来什么**：6 个新 panel 列（`mean_clarity_score_{full,ctx}` + `mean_frac_definite_{full,ctx}` + `frac_amb_articles_{full,ctx}`）；**真双轨**——对 content_full（全文）与 content_ctx（实体周围窗）独立词典扫描，**与项目现有 `_dual_analyze` 三轨契约一致**（修 R3-C1）；可作 P3 substance Table A7 主 robustness + 与 ln_fintech_mdna_length (P2 mediator) **三角化** Panel C；预期 LLM substance vote 与 `frac_ambiguous` 在 bank-year 层正相关 ρ（**by 39d HTMT 实测**；Bonsall 2017 JAE 财务披露类比 0.3-0.5，中文银行新闻**无先验，由实测决定**）；审稿人问"你的 LLM 判'象征性'是不是真的对应模糊话术" → Table A7 + Table A8（**A1 × D4 disagree 交互**, 修 R9-M5）。

**A3 给 P1 / benefit_society 作者带来什么**：2 个新 panel 列 `mean_num_intensity_{full,ctx}`，真双轨；量化披露强度 robustness；Table A9 = Hales 2011 CAR 风格补强。

**12 paper portfolio 对齐**（修 R9-H2）：P3 (substance) + P4 (locus) + P5 (collab) + P1 (tone) + benefit_society = **5 active updates**；其余 4 paper（attention/brokerage/llm_peer/strategic_diff）= explicit null；合 9 paper_spec.yaml 触动。

---

## §13. 执行清单（修 M7）

| 步骤 | Owner | wd | 验收 |
|---|---|---|---|
| **D-1** 8 项 prerequisite | claude (lead) + user (G-A0) | 1.9 | 详 §0 表 |
| D0 plan v0.3 freeze + sidecar JSON | claude | 0.5 | git tag `v3.5.1-plan-frozen` |
| D1 A1 真双轨实施 + 12 tests | claude | 1 | pytest -k clarity 全绿；**ctx ≠ full score** assertion |
| D2 A3 真双轨实施 + 10 tests | claude | 1.5 | pytest -k num_intensity 全绿；ctx ≠ full assertion |
| D3 39d 实施 + 12 tests + 双层 + seed=42 + pairwise on-disk | claude | 1.5 | G4 HTMT (strict or lenient) |
| D4 Stata 层 (export + codebook + 单 SoT) + 8 tests | claude | 1 | G5 Stata IC + 8 列写 .dta |
| D5 paper_spec × 9 (5 active + 4 null) + Stata 模板 × 4-5 + golden v1 + sidecar | claude | 1 | G3 reproducibility |
| D6 integration gate + ../CHANGELOG + CLAUDE.md + MEMORY.md | claude | 1 | G1+G2+G3+G4+G5+G6 全绿 |
| A1-A3 audit ≥ 8 轮 (V1-V15 + EiC + 同行复审) | claude + user (G-A2 to G-A6) | 3.5 | finding = 0 |
| Release | user (G-A6) | 0.5 | git tag `v3.5.1-supplementation` |

**总：~13.4 wd / calendar 17-20 wd / $0 LLM / +67 tests / +8 panel cols (全 core, 单 SoT label) / +1 stage 39d / +4-5 Stata 模板 + 2 现有扩 / +9 paper_spec (5 active + 4 null) / +1 sidecar JSON / +8 codebook entries / 0 prompt 触动 / 0 OUTPUT_REGISTRY 触动 / 真双轨契约**
