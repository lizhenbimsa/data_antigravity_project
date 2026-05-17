# Stage 3 v3.5.0 Augmentation Plan — Cell Decomposition + Orthogonality + Residual

> **状态**: DRAFT v0.2 (2026-05-17, post epoch-6-streak-1/3 audit; 46 findings 全量修正)
> **范围**: v3.4.0 baseline 之上的**纯方法学层增量** — 不改 prompt、不重跑 stage 21、不增 LLM 成本
> **基线**: HEAD `450c1aa7` (v3.4.0; prompt v8; test baseline 1153 → ~1175 passed)
> **关联**: [stage3_dual_track_plan_v3.2.0.md](stage3_dual_track_plan_v3.2.0.md) / [stage3_third_dim_plan_v3.4.0.md](stage3_third_dim_plan_v3.4.0.md) / [innovation_collab_mode_framework.md](innovation_collab_mode_framework.md) / [wz_framework_boundary_justification.md](wz_framework_boundary_justification.md)
> **Audit log**: [stage3_v3_5_0_augmentation_plan_audit_log.md](stage3_v3_5_0_augmentation_plan_audit_log.md) (epoch 6, streak 1/3 fail → v0.2 修正中)
> **Version history**: v0.1 → v0.2 修正 trail 详见 §11

---

## §0. Pre-registration Freeze (Nosek 2018 §4 标准 — 修 A-NEW-4)

**关键 invariant**: 本 plan §2.1.4 cell merge 规则、§2.2.4 NMI 阈值解读、§2.3.4 small-sample restriction 必须在 git tag `v3.5.0-plan-frozen` 之前**字节级冻结**。任何 D-day 启动后的 post-hoc revision 触发 epoch 7 audit + paper limitations 段标准声明 (per [stage3_third_dim_plan_v3.4.0.md §2.2](stage3_third_dim_plan_v3.4.0.md#L36)).

**Pre-registration timing**: NMI thresholds + cell merge rules MUST be frozen + git-tagged BEFORE encode.py D-day code change。

**v3.4.0 commit hash anchor** (修 F16): plan 中 `450c1aa7` 是 D0 day frozen 的 v3.4.0 baseline; 若 v3.4.0 在 D0 之后有 hotfix patch, 必须 (a) 更新 plan 全文 hash references (grep `450c1aa7`); (b) 重新跑 streak 2/3 audit; (c) 重新 git-tag `v3.5.0-plan-frozen-rev1`. v3.4.0 baseline 期间发现的 prompt v8 字节级变更 (按 §9.6 F8 约定) 自动触发本机制。

**Tag-over-hash 强制 (修 F33)**: v3.4.0 baseline 必须先存在 immutable git tag (e.g., `v3.4.0` 或 `v3.4.0-baseline-frozen`); plan 内所有 `450c1aa7` references 应解读为 "the commit pointed to by v3.4.0 tag at D0 day". 若 v3.4.0 git tag 不存在, **D0 day 第一动作 = 打 tag** (independent action 配合 §9.2 prompt-v8 tag 补打). 任何 force-push 覆盖 tag (Git 默认禁止覆盖 immutable tag) 触发 epoch 7 audit.

---

## §1. 增量范围（in scope / out of scope）

### 1.1 in scope（v3.5.0 仅做 3 项 + 1 refactor）

| 模块                                  | 内容                                                                                                                                                                                                                                                                          | 文献锚                                                                                                                                                    | LLM 成本 |
| ------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| **R0 (新加)** encode.py 拆分 refactor | 把 `_aggregate_by_collab_mode` ~200 行 block 抽到新文件 `pipeline/panel/encode_collab.py` (修 B-NEW-1)。**Rollback fallback (修 F5)**: 若 D2 day 强制全量 1175 测试 gate 失败, 回滚 refactor commit, 改为不拆分直接在 encode.py 内追加, 接受 1294 → ≈1470 行临时膨胀 (与 §1.1 R0 refactor 路径 1100 + 200 + 170 = 1470 等价算术, 修 F34)至 v3.6.0. **实施实际路径 (D0-D5 实测, 修 F48)**: 走 hybrid path — encode.py 仅 +20 行 delegate hook (1294 → 1314 行) + encode_collab.py 新文件 240 行 (D2 + D4 全量 derive + apply_v3_5_0 entry); **未做** _aggregate_by_collab_mode 拆分。原 §7 R10 rollback path (1294→1470 if-block 内联) 转为**未来 v3.6.0 实际拆分时** fallback。当前 hybrid path 通过 §7 R10 强制 baseline test gate 验证 (1487 fast tests pass, 0 v3.5.0-caused regression). | —                                                                                                                                                         | $0       |
| **D2** Cell decomposition             | 派生 `cell_id_{full,ctx}` ∈ {1..8} + Stata Table 6 模板                                                                                                                                                                                                                       | Angrist & Pischke (2009) Ch.5 saturated regression; Sun & Abraham (2021 JOE 225) cohort decomposition (修 I-NEW-3)                                        | $0       |
| **D3** NMI 正交性测度                 | article 层 3 维度 NMI matrix + 6×6 cross matrix + permutation null distribution                                                                                                                                                                                               | Vinh, Epps & Bailey (2010 JMLR 11) NMI; Fred & Jain (2003 CVPR) arithmetic averaging; Bagozzi & Yi (1988 JAMS 16) discriminant validity (修 C2 + D-NEW-4) | $0       |
| **D4** Dual-track residual            | 派生 `{subst,locus,collab}_{disagree,freerider,quietworker}` 9 article-level + 18 panel-level                                                                                                                                                                                 | 作者自创 measure；类比借用 Loughran & McDonald (2011 JF) tone-vs-context；类比借用 Westphal & Zajac (2001 ASQ) decoupling (修 C3 + m2)                    | $0       |

### 1.2 out of scope（明确 defer）

| 项                                       | defer 到 | 原因                                                                         |
| ---------------------------------------- | -------- | ---------------------------------------------------------------------------- |
| **A1** multi-class collab_mode (6-class) | v3.7.0   | 需 prompt v9 + 重跑 stage 21 ($2,000+) + 4 wk dev + paper_spec.yaml × 9 改动 |
| **A2** partner_count + partner_types     | v3.6.0   | 需 prompt v8 → v9 bump + mini-prompt 补抽 ~$640 LLM, buffer $520 不够        |
| **D1** prob_score 校准层                 | v3.6.0   | 依赖 calibration v5.2 G1 解封 + Platt 公式重写 (logit transform 包裹)        |
| B1-B5 第 4 维度候选                      | v3.8.0+  | 单独 epoch audit + LLM cap 重审                                              |

### 1.3 与现有契约的不变量保证

- **Prompt v8 字节级冻结**（修 I-NEW-1：v3.5.0 全程不触 prompt 文件）
- **9 个 paper_spec.yaml schema 兼容** — v3.5.0 PR 仅扩展 `tables.t6` 字段（详 §2.1.6 + §5）
- **CI 5 jobs 全绿** — v3.5.0 新增 ~30 测试**均不 import torch**，4 个 light job 安全（修 E-NEW-3）
- **Feature-flag 策略** (修 F12): v3.5.0 不引入 runtime feature flag — panel schema 加列是 idempotent 安全操作 (下游若不 reference 新列则无感)。**回滚颗粒度** = 整个 v3.5.0 PR git revert (单 PR 设计, 不切多 PR 内部 stage)。golden baseline 副本策略 (§5) + SSRN 锁定策略 (§5) 联合提供回滚后数据一致性保证。

---

## §2. 工程契约层

### 2.1 D2 Cell Decomposition

#### 2.1.1 article-level cell_id 派生

新文件 `pipeline/panel/encode_collab.py` 中（refactor 后位置）：

```python
"""Cell decomposition derivation (v3.5.0 D2).

8-cell encoding: cell_id = subst*4 + locus*2 + collab + 1 ∈ {1..8}.
baseline (cell 1) = (0, 0, 0) = 实质性 × 底层技术 × 自主研发.

v3.7.0 breaking note: 当 collab_mode 升级到 6-class (multi-class A1),
CELL_LABEL_MAP 必须重写为 24 项；保留 v3.5.0 8-cell 仅作向下兼容（旧 paper 引用）。
(修 J-NEW-2)

Backward-compat 路径 (修 F29): v3.7.0 panel 同时保留 (a) `cell_id_v3_5_full` 列
(v3.5.0 8-cell 编码不变, 为 v3.4.0/v3.5.0 已 publish paper 的 replication 提供锚定),
(b) `cell_id_v3_7_full` 列 (v3.7.0 24-cell 新编码). 旧列可在 v3.8.0 deprecate.
"""

VALID_SUBST = {'实质性', '象征性'}
VALID_LOCUS = {'底层技术', '应用场景'}
VALID_COLLAB = {'自主研发', '外部协同'}

CELL_LABEL_MAP = {
    1: '实质性·底层技术·自主研发',   # baseline (s=0, l=0, c=0)
    2: '实质性·底层技术·外部协同',   # (0, 0, 1)
    3: '实质性·应用场景·自主研发',   # (0, 1, 0)
    4: '实质性·应用场景·外部协同',   # (0, 1, 1)
    5: '象征性·底层技术·自主研发',   # (1, 0, 0)
    6: '象征性·底层技术·外部协同',   # (1, 0, 1)
    7: '象征性·应用场景·自主研发',   # (1, 1, 0)
    8: '象征性·应用场景·外部协同',   # (1, 1, 1)
}

def _compute_cell_id(df: pd.DataFrame, track: str) -> pd.Series:
    """Returns Int8 in 1..8 (NA if any of 3 dims is NA or dirty on this track).

    Dirty label defense: 防 v3.4.0 encode.py:980 已显示的 "非预期 collab_mode 值"
    污染——空字符串 / '未知' 等不在 VALID set 的 label 被等同于 NaN 处理 (修 M3).

    Missing column guard (修 F28): 若 s_col / l_col / c_col 任一不在 df.columns,
    函数返回**全 NA 的 Int8 Series** + logger.warning, **不**抛 KeyError. 调用层
    可通过检查 `df[f'cell_id_{track}'].isna().all()` 探测 dim 缺列退化.
    """
    s_col = f'innovation_substantiveness_{track}'
    l_col = f'innovation_locus_{track}'
    c_col = f'innovation_collab_mode_{track}'

    # Missing column guard
    missing = [c for c in (s_col, l_col, c_col) if c not in df.columns]
    if missing:
        logger.warning(f"v3.5.0 D2 cell_id_{track}: missing columns {missing}, returning all-NA Int8")
        return pd.Series([pd.NA] * len(df), dtype='Int8', index=df.index)

    # pair-wise valid check including dirty label defense (修 F32 + F47 + F49)
    # F47: 用 module-level `_normalize_label(series)` 替代 closure (便于 unit test mock,
    #      可被 derive_residual_signals 共用)
    # F49: `_normalize_label` 内含 NaN dtype safety guard (若 series.dtype != object,
    #      e.g., 全 NaN 列 → float64, 跳过 .str.* accessor 直接 return).
    valid = (_normalize_label(df[s_col]).isin(VALID_SUBST) &
             _normalize_label(df[l_col]).isin(VALID_LOCUS) &
             _normalize_label(df[c_col]).isin(VALID_COLLAB))

    s_bit = (df[s_col] == '象征性').astype('int8')
    l_bit = (df[l_col] == '应用场景').astype('int8')
    c_bit = (df[c_col] == '外部协同').astype('int8')

    # universal pandas/numpy 兼容: .where(...) 而非索引赋值 (修 B-NEW-2 / m3)
    cell = (s_bit * 4 + l_bit * 2 + c_bit + 1).where(valid, pd.NA).astype('Int8')
    return cell

df['cell_id_full'] = _compute_cell_id(df, 'full')
df['cell_id_ctx']  = _compute_cell_id(df, 'ctx')
```

**编码一致性**：与 [stata_export.py:44-60](../../pipeline/panel/stata_export.py#L44-L60) 现有 `0=baseline, 1=对照` 模式严格一致 — cell 1 对应三维全 baseline, cell 8 对应三维全 contrast。

#### 2.1.2 panel 层聚合 + cross-identity 校验

```python
# v3.5.0 D2: 8-cell bank-year counts (命名约定保留 _full 标识, 修 J-NEW-3)
# 注: n_articles_indep / n_articles_collab 是 v3.4.0 encode.py:1018 已有的二元后缀列,
#     非 v3.5.0 D2 新派生; D2 仅新增 cell_1..8 列, cross-identity 是把 v3.4.0
#     二元后缀作为 D2 8-cell 的聚合约束验证 (修 F1).
for cell_id in range(1, 9):
    df_cell = df[df['cell_id_full'] == cell_id]
    panel[f'n_articles_cell_{cell_id}_full'] = df_cell.groupby(['bank','year']).size() \
        .reindex(panel.index, fill_value=0).astype('Int32')

# 主恒等式 (与 §2.3 D4 共存)
identity_main = (panel['n_articles'] ==
                 sum(panel[f'n_articles_cell_{i}_full'] for i in range(1, 9)))

# Cross-identity 校验 (与 v3.4.0 _indep/_collab 二元后缀一致性, 修 C-NEW-2)
# n_articles_indep == n_articles_cell_{1,3,5,7}_full (cell 1/3/5/7 collab=0=自研)
# n_articles_collab == n_articles_cell_{2,4,6,8}_full (cell 2/4/6/8 collab=1=外部)
identity_cross_indep = (
    panel['n_articles_indep'] ==
    sum(panel[f'n_articles_cell_{i}_full'] for i in [1, 3, 5, 7])
)
identity_cross_collab = (
    panel['n_articles_collab'] ==
    sum(panel[f'n_articles_cell_{i}_full'] for i in [2, 4, 6, 8])
)

n_fail_main = (~identity_main[panel['n_articles'] > 0]).sum()
n_fail_indep = (~identity_cross_indep[panel['n_articles_indep'] > 0]).sum()
n_fail_collab = (~identity_cross_collab[panel['n_articles_collab'] > 0]).sum()

if n_fail_main > 0 or n_fail_indep > 0 or n_fail_collab > 0:
    logger.warning(f"  ✗ cell_id identity 失败: main={n_fail_main}, "
                   f"indep_cross={n_fail_indep}, collab_cross={n_fail_collab}")
else:
    logger.info("  ✓ cell_id 8-cell + cross-identity 校验通过")
```

**边界 (修 F27 + F46)**: 实施采用 **graceful skip** 而非 hard `raise ValueError` (F46 修正: v3.4.0 baseline 测试 fixture df=20 / panel=15 必然触发 hard assert, 破坏 §7 R10 1175 test gate):

- **cell_id_full 全 NA** (LLM 输入列缺失或全 dirty label): `aggregate_d2_panel` return early + log info + `{'cell_aggregation_skipped': True, 'skip_reason': 'all_na_cell_id'}`
- **panel.shape[0] == 0**: log warning + return early + `{'skip_reason': 'empty_panel'}`
- **df.shape[0] < 1000** (small sample): 仅触发 `panel.attrs['D2_small_sample_warning'] = True` + log info, **继续聚合** (production threshold ≥ 100k 时不告警)

test_cell_id_panel.py 加 2 项: "all_na_cell_id_skip" + "tiny_panel_warning_attr"。

#### 2.1.3 Stata 编码与 value label

[stata_export.py:60](../../pipeline/panel/stata_export.py#L60) 之后追加：

```python
# v3.5.0 D2: cell_id 1..8 value label
CELL_ID_VALUE_LABEL: Dict[int, str] = {
    1: 'sub.tech.indep', 2: 'sub.tech.collab',
    3: 'sub.app.indep',  4: 'sub.app.collab',
    5: 'symb.tech.indep', 6: 'symb.tech.collab',
    7: 'symb.app.indep',  8: 'symb.app.collab',
}
```

#### 2.1.4 ★ Framework §2 升级 — Stata pre-regression 层合并（修 M2）

**合并发生层澄清**：article-level 派生**保留全部 8 cell**（panel 输出 `n_articles_cell_1..8_full` 8 列不变）。合并发生在 **Stata pre-regression decision 层**——单 paper Table 6 跑回归前由 .do 模板判定。

[innovation_collab_mode_framework.md §2](innovation_collab_mode_framework.md) 升级为 pre-registered decision rule（per Nosek 2018 PNAS additive supplementation）：

> "Cell 在 Stata 主回归层合并 ≠ panel 层合并。Panel 输出 8 cell 列不变。
>
> **主回归阶段** 单 paper 决策树（pre-registered, 每 paper Table 6 启动前固化）:
>
> | 条件                                                                                                 | 行动                                                                                     |
> | ---------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------- |
> | cell n ≥ 50 obs (rule of thumb for OLS cell-level fixed-effect estimation, NOT Cohen 1988 — 修 m1) | 独立 estimate, 入 Table 6                                                                |
> | cell 30 ≤ n < 50                                                                                    | **Priority A**: 与同 collab + 同 locus、相反 substantiveness 的 cell 合并          |
> | 合并后仍 n < 50                                                                                      | **Priority B**: 与同 collab、相反 locus 的合并                                     |
> | 仍 n < 50                                                                                            | **Priority C**: 该 cell 标 `merged_into_other`, 主回归 omit, Appendix 报描述统计 |
>
> 合并发生前后**必须**记录到 [stage3_v3_5_0_augmentation_plan_audit_log.md §B.cell_merge_history](stage3_v3_5_0_augmentation_plan_audit_log.md)。审稿人 replication 重现需引用 stage 21 输出 + 该 audit log row。
>
> **Cross-paper 一致性 (修 F26)**: 若 P3/P4/P5 中两个或以上 paper 都触发 cell merge, 不同 paper 的 merge 决策 (Priority A/B/C) 必须独立基于该 paper 的样本统计; **不要求** cross-paper merge 决策一致。但 audit log §B.cell_merge_history 必须每 paper 单独记录 (含 cell, n_obs, priority used, paper_id) 以让 cross-paper Table 6 比较时审稿人能看见每 paper 的 merge structure 差异。Paper-level Table 6 主结果**禁止**跨 paper 直接合并 cell, 仅允许 within-paper merge。"

#### 2.1.5 Stata Table 6 模板

新增 [papers/_common/stata_templates/v3_5_0/19_table6_cell_decomposition.do.tmpl](../../papers/_common/stata_templates/v3_5_0/19_table6_cell_decomposition.do.tmpl)（编号 19 是 v3.4.0 空号；实测 _common/ 目录有 14 个模板，编号占用 `00 / 01 / 10..14 / 20..24 / 30..31` — 修 M1）。

**Subdirectory 隔离 (修 F45)**: 新模板放 `v3_5_0/` 子目录，避免 v3.4.0 `build_replication_package` ([papers/_common/stata_runner.py:375](../../papers/_common/stata_runner.py#L375) 用 `glob('*.do.tmpl')` 非 rglob) 把新模板的 jinja 占位符 (`{{ panel_path }}` 等) 强行套 UPPERCASE_UNDERSCORE substituter 失败。v3.5.0 D6 day 通过 paper_spec.yaml 配置 + 未来 `stata_runner build-replication-v2` CLI (deferred to v3.6.0+) 渲染；当前阶段新模板**手动**用 jinja2 渲染或 paper analysis.py 内嵌套用。:

```stata
version 19
clear all
set linesize 120

use "{{ panel_path }}", clear

* Cell-level pre-regression merging by Stata-time decision (per plan §2.1.4):
* {{ cell_merge_decisions }}  // populated by stata_runner per paper

* 8-cell categorical treatment, base = cell 1 (sub.tech.indep)
* Reports 5-7 estimated coefficients (depending on merges), 1 base omitted (修 audit M1 typo)
reghdfe {{ outcome }} i.cell_id_full {{ controls }} [aw={{ weight }}], ///
    absorb(i.{{ bank_fe }} i.{{ year_fe }}) cluster({{ cluster_var }})

testparm i.cell_id_full

esttab using "{{ output_dir }}/table6_cell_decomp.tex", ///
    cells(b(star fmt(3)) se(par fmt(3))) ///
    keep(*.cell_id_full) ///
    label nogaps title("Table 6: 8-cell decomposition (base = cell 1)")
```

**模板总数口径**（修 D-NEW-1）：

- *news_process CLAUDE.md 口径*: 14 (`_common/`) + 47 (子目录) = 61 → v3.5.0 +2 → **63**
- *master plan v2.56 B-route 口径*: 77 → R89 升 84 → v3.5.0 +2 → **86**
  两口径同时增 2（D2 + D4 各 1）。

**Instantiation 路径** (修 F21): 模板用 jinja2 占位符 (`{{ panel_path }}` / `{{ outcome }}` / `{{ controls }}` / `{{ weight }}` / `{{ bank_fe }}` / `{{ year_fe }}` / `{{ cluster_var }}` / `{{ output_dir }}` / `{{ cell_merge_decisions }}`); paper authors 在 paper_spec.yaml 配置实例化参数, `stata_runner build-replication` CLI 子命令 (per [CLAUDE.md](../../CLAUDE.md) CLI 子命令段) 自动渲染并产出可运行 .do 文件。Paper author 不直接编辑模板, 仅在 paper_spec.yaml 内 declarative 配置。同规则适用于 §2.3.5 Table 25 模板。

**RHS variable 数估算** (修 F25): `i.cell_id_full` 生成 7 dummy (8 cell - 1 base omitted); 加 paper-specific controls (5 bank-level + 2 year-level per [bank_fintech_collab/paper_spec.yaml:56-57](../../papers/bank_fintech_collab/paper_spec.yaml#L56-L57)) + 2 FE absorbed by reghdfe (不计 RHS) = ~14 RHS variables. **MP 19.5 上限 65,532, IC 上限 798, SE 上限 10,998** — 14 << 所有 license. 即使加 het interaction 翻倍 = ~28 RHS, 仍远低于 IC 上限. 故 v3.5.0 Stata Table 6 模板**不需要** IC license 变体适配。

#### 2.1.6 paper-level 适用（修 M6 + G-NEW-2）

实测 [papers/](../../papers/) 9 个 paper_spec.yaml 全部存在：

| Paper ID                    | 是否用 D2 主回归 | tables.t6 字段                           |
| --------------------------- | ---------------- | ---------------------------------------- |
| bank_fintech_substance (P3) | ✓ Table 6 主用   | `template: 19_table6_cell_decomposition` |
| bank_fintech_locus (P4)     | ✓ Table 6 主用   | 同                                       |
| bank_fintech_collab (P5)    | ✓ Table 6 主用   | 同                                       |
| bank_fintech_tone (P1)      | ✗ 不用           | `null` (explicit, 防 schema test fail)   |
| bank_fintech_attention (P2) | ✗ 不用           | `null`                                   |
| benefit_society             | ✗ 不用           | `null`                                   |
| brokerage_network           | ✗ 不用           | `null`                                   |
| llm_peer                    | ✗ 不用           | `null`                                   |
| strategic_diff              | ✗ 不用           | `null`                                   |

#### 2.1.7 P5 paper_spec.yaml `treatment.alternative` 同步（修 A-NEW-2）

[bank_fintech_collab/paper_spec.yaml:48-52](../../papers/bank_fintech_collab/paper_spec.yaml#L48-L52) 当前 alternative 列表：

```yaml
treatment:
  primary: innovation_collab_mode_full
  alternative:
    - innovation_collab_mode_ctx
    - independent_minus_collab_gap
```

v3.5.0 加入 cell-based alternative：

```yaml
  alternative:
    - innovation_collab_mode_ctx
    - independent_minus_collab_gap
    - cell_id_full                       # v3.5.0 D2 cell decomposition treatment
  alternative_construction:
    independent_minus_collab_gap: innovation_collab_mode_full - (1 - innovation_collab_mode_full)
    cell_id_full: subst*4 + locus*2 + collab + 1  # v3.5.0 D2; see plan §2.1.1
```

### 2.2 D3 NMI 正交性测度

#### 2.2.1 新增 validation stage

新文件 [news_process/validation/39c_construct_orthogonality.py](../../validation/39c_construct_orthogonality.py)（修 B-NEW-5：紧跟 39a_inter_track_kappa.py / 39_prompt_sensitivity.py validation 序列，避开 NN=40 与 panel_export 段隐含冲突）。

shim：[news_process/39c_construct_orthogonality.py](../../39c_construct_orthogonality.py) (≤30 行)。

注册位置：

- [core/dag.py::STAGES_VALIDATION](../../core/dag.py) — 新增 StageSpec entry
- ~~[core/schemas.py::OUTPUT_REGISTRY](../../core/schemas.py) — **显式 entry**（修 B-NEW-3）~~ **撤回 (修 F44)**

**注 (修 F44)**：stage 39c 为 validation stage，按 [schemas.py:134](../../core/schemas.py#L134) 历史约定**不进** OUTPUT_REGISTRY (与 stage 31-39 一致：" OUTPUT_REGISTRY 历史上对 STAGES_VALIDATION (stage 31-39) 故意不登记")。stage 实际产出 4 parquet + 1 json 在 `data/processed/`，但通过 [core/dag.py STAGES_VALIDATION](../../core/dag.py) 单源注册，下游消费者 (paper Appendix A.2 渲染脚本) 直接路径引用 `data/processed/39c_*.parquet`，不走 OUTPUT_REGISTRY lookup。B-NEW-3 finding 在实施时被 schemas.py 历史约定纠偏。

CLAUDE.md shim enumeration 同步更新：`30..39 incl. 32a/38a/38b/39a/39c` (修 M4)。

**Logging 约定** (修 F13): 与 v3.4.0 main pipeline 一致 — stage 39c 输出至 `logs/runs/<run_id>/39c_construct_orthogonality.log`, 通过 `news_process.core.logging.get_logger(__name__)` 接入。`logger.info` / `logger.warning` 同时打印到 stderr (前台可见, run_pipeline_validation 实时监控) + log 文件 (审计可重现)。stage 内**禁止** `print()` 直接输出，所有诊断信号走 logger 以保证 audit log §F.runtime_observability 可 grep。

#### 2.2.2 算法（修破 audit C1 / C2 / H-NEW-1 / H-NEW-2 / C-NEW-1）

```python
"""validation/construct_orthogonality.py — D3 NMI matrix (v3.5.0).

锚定文献:
    Vinh, Epps & Bailey (2010 JMLR 11:2837-2854) NMI arithmetic averaging
    Fred & Jain (2003 CVPR) NMI for clustering comparison (arithmetic version)
    Bagozzi & Yi (1988 JAMS 16:74-94) discriminant validity in CFA

DROPPED:
    - Strehl & Ghosh (2002 JMLR 3) — 用的是 geometric averaging, 与本实现不匹配 (修 C2)
    - Cronbach α — 不适用于 3 个不同 construct (α 测同 construct 多 item internal consistency)

Dependency stability (修 F35):
    sklearn 1.5-1.8 已验证 `normalized_mutual_info_score(..., average_method='arithmetic')`
    API 兼容; 若升级到 sklearn 2.x 必须 (a) 运行 `tests/test_construct_orthogonality.py`
    全 14 测试; (b) 比对 v3.5.0 baseline NMI matrix parquet hash (允许 ≤ ±0.001 漂移 per
    H-NEW-1 LLM stochasticity); (c) 任何 API breaking change 触发 epoch 7 audit.

Reproducibility lock (修 H-NEW-1):
    本 stage 输入 = data/processed/21_tone_llms.parquet @ v3.4.0 final commit hash 450c1aa7
    NMI 数值有 ±0.005 stochasticity (LLM API minor non-determinism, see plan §2.2.5)
    任何 stage 21 rerun 必须重跑本 stage + 同步更新 v3.5.0 输出 hash.

Performance estimate (修 F3):
    full 3×3 matrix bootstrap: 9 cells × 1000 bootstrap ≈ 7 min
    ctx  3×3 matrix bootstrap: 9 cells × 1000 bootstrap ≈ 7 min
    cross 6×6 matrix bootstrap: 36 cells × 1000 bootstrap ≈ 30 min
    permutation null (off-diagonal only): 30 cells × 1000 perm ≈ 25 min
    总 wall-time ≈ 70 min on single core (sklearn NMI ~100 ms / call on N≈400k labels).
    D4 day 任务 1 wd 含 ~1.5 h compute + 6.5 h dev/test, 可行.

Concurrency (修 F7 + F43):
    本函数 single-thread 设计; SeedSequence.spawn 已 pre-allocate seeds 故 parallel 友好.
    sklearn `normalized_mutual_info_score` 内部 sparse contingency table 构造在
    sklearn 1.5-1.8 **基于源码 review 判断单调用线程安全** (无 sklearn 官方文档明确
    claim, 谨慎说法, 修 F43). joblib `n_jobs > 1` 可加速但需用 `prefer='processes'`
    (避免 GIL); 默认实现保持 single-thread, 加速需 paper authors 显式 opt-in 并报
    wall-time 改善到 audit log §E. **若 production parallel 触发 race condition 异常,
    立即 fallback `n_jobs=1` + audit log §E.thread_race_event 记录** (修 F43).

Recommended default for D4 day (修 F31):
    本机 [memory: stata_edition_mp] MP 19.5 = 64-core, 建议 D4 day 实跑用
    `n_jobs=16` (留 ~48 core 给系统 + 其它并发 task) → wall-time 70 min → ~5 min.
    仍为 reproducibility 提供 single-thread fallback (set `n_jobs=1` 复现 baseline
    hash). audit log §E.parallel_actual 记录实测 wall-time.
"""
import numpy as np
import pandas as pd
from sklearn.metrics import normalized_mutual_info_score

DIMS_FULL = ['innovation_substantiveness_full',
             'innovation_locus_full',
             'innovation_collab_mode_full']
DIMS_CTX = [d.replace('_full', '_ctx') for d in DIMS_FULL]
ALL_DIMS = DIMS_FULL + DIMS_CTX

def compute_nmi_matrix(df: pd.DataFrame, dims: list[str],
                       sample_strategy: str = 'listwise_complete',
                       bootstrap_n: int = 1000,
                       seed: int = 42
                       ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Returns (nmi_point, nmi_ci_low, nmi_ci_high, n_pair_matrix).

    sample_strategy:
        'listwise_complete' — 全 dims 同时非脏的 row (修 C-NEW-1; recommended for matrix)
        'pairwise_complete' — 每 (d1, d2) 各自 dropna (legacy, sample size 不可比)

    Bootstrap implementation:
        修 C1: bootstrap 在 sampled DataFrame 上整体 resample (两列同步 row),
               不是分别 resample d1 + 固定 d2.
        修 H-NEW-2: 用 NumPy 2.x SeedSequence.spawn 替代 rng.integers, 跨 NumPy 版本 reproducible.
    """
    n = len(dims)
    point = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_low = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_high = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    n_pair = pd.DataFrame(np.zeros((n, n), dtype=int), index=dims, columns=dims)

    # Listwise complete: 全 dims 同时有效 (修 C-NEW-1)
    if sample_strategy == 'listwise_complete':
        clean = df[dims].dropna()
        base_n = len(clean)
    else:
        clean = None  # will recompute pairwise per (d1, d2)
        base_n = None

    # NumPy 2.x reproducible seed sequence (修 H-NEW-2)
    seed_sequence = np.random.SeedSequence(seed)
    boot_seeds = seed_sequence.spawn(bootstrap_n)

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if sample_strategy == 'pairwise_complete':
                clean = df[[d1, d2]].dropna()
                base_n = len(clean)

            if base_n < 100:
                continue
            n_pair.iloc[i, j] = base_n

            # Point estimate
            point.iloc[i, j] = normalized_mutual_info_score(
                clean[d1], clean[d2], average_method='arithmetic'
            )

            # Bootstrap CI: integral row-pair resample (修 C1)
            boot = np.empty(bootstrap_n)
            for k, s in enumerate(boot_seeds):
                state = int(s.generate_state(1)[0])
                clean_boot = clean.sample(frac=1, replace=True, random_state=state)
                boot[k] = normalized_mutual_info_score(
                    clean_boot[d1], clean_boot[d2],  # ★ 两列同步 (修 C1)
                    average_method='arithmetic'
                )
            ci_low.iloc[i, j] = np.percentile(boot, 2.5)
            ci_high.iloc[i, j] = np.percentile(boot, 97.5)

    return point, ci_low, ci_high, n_pair


def compute_permutation_null(df: pd.DataFrame, dims: list[str],
                             n_permutations: int = 1000,
                             seed: int = 43
                             ) -> tuple[pd.DataFrame, pd.DataFrame]:  # 修 F4
    """Permutation-based null distribution for NMI thresholds (修 C3).

    Returns matrix of NMI 95% / 99% percentile of null distribution per (d1, d2).
    Used as pre-registered threshold reference rather than ad-hoc 0.15/0.30.
    """
    clean = df[dims].dropna()
    n = len(dims)
    null_p95 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    null_p99 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)

    seed_sequence = np.random.SeedSequence(seed)
    perm_seeds = seed_sequence.spawn(n_permutations)

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if i == j:
                continue
            null = np.empty(n_permutations)
            for k, s in enumerate(perm_seeds):
                rng = np.random.default_rng(s)
                d2_perm = rng.permutation(clean[d2].values)
                null[k] = normalized_mutual_info_score(
                    clean[d1], d2_perm, average_method='arithmetic'
                )
            null_p95.iloc[i, j] = np.percentile(null, 95)
            null_p99.iloc[i, j] = np.percentile(null, 99)

    return null_p95, null_p99
```

#### 2.2.3 输出

| 输出文件                       | 路径                                                   | 用途                                                                  |
| ------------------------------ | ------------------------------------------------------ | --------------------------------------------------------------------- |
| `39c_nmi_matrix_full.parquet`  | `data/processed/`                                      | full-only 3×3 NMI + CI + n_pair                                       |
| `39c_nmi_matrix_ctx.parquet`   | 同                                                     | ctx-only 3×3 NMI                                                      |
| `39c_nmi_matrix_cross.parquet` | 同                                                     | 6×6 full ∪ ctx cross-matrix                                           |
| `39c_nmi_null_p95.parquet`     | 同                                                     | Permutation null 95% percentile（pre-registered threshold reference） |
| `39c_nmi_null_p99.parquet`     | 同                                                     | Permutation null 99% percentile                                       |
| `39c_nmi_summary.json`         | 同                                                     | `{max_off_diag, observed_vs_null_p95, interpretation}`                |
| `39c_nmi_heatmap.png`          | `data/processed/` (修 m4, 不放 papers_assets/figures/) | 3 子图 heatmap                                                        |

#### 2.2.4 解读阈值（permutation-based, 修 C3）

```
Z = (observed_NMI - null_mean) / null_std
Interpretation:
  observed_NMI ≤ null_p95  → strong orthogonality (NMI 与随机配对 indistinguishable)
  null_p95 < obs ≤ null_p99 → moderate independence (with caveat in paper)
  obs > null_p99           → weak independence, signal detected
```

**Sensitivity analysis** (修 C3): 同时报 0.10 / 0.20 / 0.40 三档 raw NMI 阈值供对照，但**主要解读用 permutation null Z-score**。

**Extreme value diagnostics (修 F30 + F40)**: (a) **NMI ≈ 0** (< 0.001): trivial case — 一或两个 dim 接近常数 (e.g., 99% 文章都是 `实质性`), prompt 应被审视为何不区分; 写入 audit log §A.constant_dim_warning. (b) **NMI ≈ 1** (> 0.95): perfect dependence — 可能 label leakage (两个 LLM prompt 维度等价表达同一概念), 须立即 trigger §2.2.6 R2 contingency (paper 暂缓 + epoch 7 audit). (c) 中间值按 Z-score 三档解读 (Z ≤ 1.96 / 1.96-2.58 / > 2.58 per §2.2.6 contingency table)。 (d) **NMI = NaN / undefined** (修 F40, sklearn 视 version 返回 `nan` 或 1.0): d1 与 d2 均为常数 (H(X)=H(Y)=0, 0/0 undefined). 触发条件: 上游 stage 21 异常输出 (e.g., 全 `实质性`); `compute_nmi_matrix` 必须前置 `if clean[d1].nunique() < 2 or clean[d2].nunique() < 2: continue` 跳过 degenerate pair, 不写入 matrix + logger.error + audit log §A.degenerate_dim_pair 记录。

#### 2.2.5 paper-level 用法 + LLM stochasticity disclosure

进所有 P1-P5 paper 的 **Appendix A "Construct Validity Evidence"** Table A2（A1 留给 Cohen's κ）。

**Stage 21 LLM stochasticity disclosure** (per H-NEW-1)：

- NMI 数值在不同次 stage 21 run 间有 ~±0.005 噪声
- 阈值粒度 (0.05-0.10 width) 远大于此噪声 → 解读稳健
- Paper Appendix A.2 注释：N M I values are based on a single stage 21 run (commit 450c1aa7); replication may differ by < 0.01

#### 2.2.6 paper §1 / §7 contingency 修正（修 I-NEW-1）

**Pre-registered contingency tree** (frozen pre-experimental, 修 A-NEW-4):

| Permutation Z-score          | 解读                  | 行动                                                                                                                                                           |
| ---------------------------- | --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Z ≤ 1.96 (NMI ≤ null_p95)    | strong orthogonality  | paper Appendix A.2 直接 publish                                                                                                                                |
| 1.96 < Z ≤ 2.58 (≤ null_p99) | moderate independence | paper publish + caveat + Appendix A.3 sensitivity                                                                                                              |
| Z > 2.58 (> null_p99)        | weak independence     | **v3.5.0 不触 prompt** — paper Appendix A.2 暂不 publish（panel 列保留落盘）。v3.6.0+ scope 加 prompt 边界 epoch 7 audit。v3.5.0 本身仍可 ship（修 I-NEW-1）。 |

### 2.3 D4 Dual-track Residual Signals

#### 2.3.1 文献归因（修 m2 + C3 + 与 P5 derivation 区分 A-NEW-3）

**核心 measure**: 作者自创 (v3.5.0 新增, no prior literature)。

**类比借用** (非直接套用):

- Loughran & McDonald (2011 JF 66) "When Is a Liability Not a Liability?" — firm-wide tone vs context-specific tone 的 differential 思路
- Westphal & Zajac (2001 ASQ 46) decoupling policy-from-practice — **类比借用** 到 narrative-context 层面（v3.5.0 D4 是 textual; W&Z 2001 是 firm-action-level）

**与 P5 paper_spec.yaml 已 register derivation 的区分**（修 A-NEW-3）：

| derivation                                         | 层                      | scope         | source                    |
| -------------------------------------------------- | ----------------------- | ------------- | ------------------------- |
| `independent_minus_collab_gap = full - (1 - full)` | 单轨（full 内部）       | article-level | P5 paper_spec.yaml v3.4.0 |
| `collab_disagree = (full ≠ ctx)`                   | **跨轨**（full vs ctx） | article-level | v3.5.0 D4                 |
| `collab_freerider`, `collab_quietworker`           | **跨轨**（方向性）      | article-level | v3.5.0 D4                 |

paper §2.3.5 manuscript footnote 必须 explicit 区分。

#### 2.3.2 article-level 派生（9 列, 3 dim × 3 signal）+ invariants

```python
# v3.5.0 D4 article-level (修 C-NEW-4 加 invariants)
DIMS_D4 = [
    ('subst',  'innovation_substantiveness', '实质性',   '象征性'),
    ('locus',  'innovation_locus',           '底层技术', '应用场景'),
    ('collab', 'innovation_collab_mode',     '自主研发', '外部协同'),
]

residual_cols = []  # 修 m5: explicit 收集列名
for short, base, baseline, contrast in DIMS_D4:
    full_col = f'{base}_full'
    ctx_col  = f'{base}_ctx'
    if full_col not in df.columns or ctx_col not in df.columns:
        continue

    both_valid = df[full_col].notna() & df[ctx_col].notna()

    df[f'{short}_disagree']    = (df[full_col] != df[ctx_col]) & both_valid
    df[f'{short}_freerider']   = (df[full_col] == baseline) & (df[ctx_col] == contrast)
    df[f'{short}_quietworker'] = (df[full_col] == contrast) & (df[ctx_col] == baseline)

    residual_cols.extend([f'{short}_disagree', f'{short}_freerider', f'{short}_quietworker'])
```

**Invariants** (文档化 mathematical guarantees, 修 C-NEW-4):

```
∀ article a, ∀ dim d:
    (i)  freerider[a,d] + quietworker[a,d] ≤ 1   (互斥)
    (ii) freerider[a,d] + quietworker[a,d] == disagree[a,d]   (定义等价)
    (iii) NaN propagation: full NaN ∨ ctx NaN ⇒ 三 indicator 全 False (not NaN)
```

`tests/test_residual_signals.py` 必须含验证 (i)-(iii) 三个不变量的单测。

#### 2.3.3 panel 聚合 + small-sample restriction

```python
# bank-year level: 18 列 (3 dim × 3 signal × 2 metric [frac + count])
# 命名约定: {dim_short}_{signal}_{metric}

residual_frac_cols = []  # 修 m5: 显式列名集
residual_count_cols = []

for short, _, _, _ in DIMS_D4:
    for signal in ['disagree', 'freerider', 'quietworker']:
        col = f'{short}_{signal}'
        frac_col = f'{col}_frac'
        count_col = f'n_articles_{col}'

        panel[frac_col] = df.groupby(['bank','year'])[col].mean()
        panel[count_col] = df.groupby(['bank','year'])[col].sum().astype('Int32')

        residual_frac_cols.append(frac_col)
        residual_count_cols.append(count_col)

# Small-sample restriction (修 m5 + C-NEW-3)
# 阈值 n<5 = 经验 OLS/aggregation 噪音临界 (rule of thumb, not literature)
small_sample_mask = panel['n_articles'] < 5
for col in residual_frac_cols:
    panel.loc[small_sample_mask, col] = pd.NA
```

#### 2.3.4 ctx coverage 自适应警告（修 C-NEW-3）

不再用拍脑袋的 50% 阈值。改为基于 v3.4.0 baseline 的自适应：

```python
# 在 §9 prerequisite day 测定 v3.4.0 baseline 并 git-tag:
#   v3_4_0_ctx_coverage_baseline.json = {"mean": 0.74, "std": 0.08}

with open(BASELINE_PATH) as f:
    baseline = json.load(f)
threshold_low = baseline['mean'] - 2 * baseline['std']  # e.g. 0.58

current_coverage = df[ctx_col].notna().mean()
if current_coverage < threshold_low:
    logger.warning(
        f"  ⚠ ctx coverage {current_coverage:.2%} < 2σ-below-baseline "
        f"{threshold_low:.2%}; panel attribute data_quality marked: "
        "insufficient_ctx_coverage"
    )
    panel.attrs['D4_data_quality'] = 'insufficient_ctx_coverage'  # Python runtime only

# 修 F6: pandas attrs 不持久化到 parquet/dta, 必须额外显式列让 Stata 用户可见.
quality_flag = 'insufficient' if current_coverage < threshold_low else 'ok'
panel['d4_data_quality_flag'] = quality_flag   # str 列, 写入 parquet + dta
# Stata 端 value label: `label define d4_flag 0 "ok" 1 "insufficient"`
# 下游 Stata 用法: `keep if d4_data_quality_flag == "ok"` 过滤不可信样本.
```

#### 2.3.5 Stata Table 5 robustness 模板

新增 [papers/_common/stata_templates/v3_5_0/25_tableA6_dual_track_residual.do.tmpl](../../papers/_common/stata_templates/v3_5_0/25_tableA6_dual_track_residual.do.tmpl) — 编号 25 紧跟 24_tableA5_dictionary_method.do.tmpl，避开已占用的 22_tableA3_bartik_iv.do.tmpl（修 M1 + m4）。同 §2.1.5 F45 subdirectory 隔离规则适用。

#### 2.3.6 paper-level usage + methodological note (修 I-NEW-2)

**Robustness use**: 主回归加 `*_disagree_frac` 作 control，洗掉 "PR-only" 噪音。

**Independent paper hook (P10 candidate)**: D4 single-handedly 撑起 "Free-riding vs Quiet-working in Bank Fintech Communication" — 由于文献厚度仍薄（18 个新 measure，仅靠类比借用），P10 立项前必须先做：

- Short methodological note (≤8 pages) 发 SSRN preprint
- Calibration v5.2 增 `disagree/freerider/quietworker` stratum，验证 IRR/test-retest reliability
- 此 note 作为 P10 main paper 的 cite

P10 立项 defer 到 v3.6.0+，**v3.5.0 仅产数据列，不立项 P10 paper**。

---

## §3. Prompt 不变性保证 (v3.5.0 不触 prompt)

v3.5.0 **字节级**不动 prompt：

- [unified_cot.txt](../../config/prompts/unified_cot.txt) version header 保持 `v8-2026-05-17`
- 不 bump 为 v9（v9 留给 v3.6.0 A2 partner_count 用）
- 不重跑 stage 21
- `test_prompt_version_wired.py` 测试 gate 自然通过

**v3.5.0 git tag plan** (修 F-NEW-3):

- `prompt-v8-supplementation-released` tag 缺失 — **独立 hotfix PR**（10 分钟）补打，不计入 v3.5.0 day-1 任务
- v3.5.0 PR merge 后新打: `v3.5.0-augmentation` (panel-only, 不含 prompt 标识)
- Plan freeze tag: `v3.5.0-plan-frozen` (D0 day, freeze 本文档版本)

---

## §4. 测试 gate

### 4.1 新增测试（~50, 修 E-NEW-1 TDD ratio）

| 测试文件                                           | 测试数              | 覆盖                                                                                                                                                                                                                                                                                                                                                                                |
| -------------------------------------------------- | ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `tests/test_cell_id_derivation.py`                 | 8                   | D2 article cell_id 编号 + dirty label 防御 + NA propagation + Int8 nullable + edge values                                                                                                                                                                                                                                                                                           |
| `tests/test_cell_id_panel.py`                      | 6                   | D2 panel 8-cell 主恒等式 + cross-identity (indep/collab) + 与现有 _indep/_collab 并存                                                                                                                                                                                                                                                                                               |
| `tests/test_construct_orthogonality.py`            | **14** (修 E-NEW-1) | D3 NMI: arithmetic 算式正确 / bootstrap row-pair (防 C1) / permutation null / 3×3 + 6×6 shape / listwise vs pairwise sample / pair-wise dropna / extreme values (all-same, all-NaN) / threshold interpretation / json schema / heatmap smoke / dim-pair n consistency / seed reproducibility (cross numpy版本) / null vs raw threshold consistency / bootstrap CI vs naive σ sanity |
| `tests/test_residual_signals.py`                   | 12 (修 E-NEW-1)     | D4: article 派生 9 列 / invariants (i)/(ii)/(iii) / small-sample restriction / ctx coverage warning / cross-dim 独立性 / panel 18 列 / NaN-aware boolean / freerider × quietworker 互斥 / disagree definition equivalence / D4_data_quality attr                                                                                                                                    |
| `tests/integration/test_v3_4_to_v3_5_migration.py` | 6                   | golden baseline 列 hash diff / identity check /**保留** 11 个 v3_3_to_v3_4 migration tests as forward compat (修 m7) / paper_spec schema 扩展 / shim 39c enumeration update / encode_collab.py refactor coverage                                                                                                                                                                    |

**total**: ~46 新测 (含新建 `test_paper_spec_schema.py` ~12 项, 修 F2) → 实际 ~58 → v3.4.0 baseline 1175 → v3.5.0 ~1233 passed / 6 skipped。

**TDD ratio**: D2 ~14 test / ~80 production = 175%; D3 14 / ~150 = 93%; D4 12 / ~150 = 80%; 平均 ~110% ✓（健康范围）。

**Test fixture 策略 (修 F36)**: D3 NMI 单元测试用 **synthetic fixture** (N=2000 articles, 模拟 v3.4.0 stage 21 schema) 替代真实 400k panel; bootstrap_n=100 (而非 production 1000) 缩短 wall-time. `tests/fixtures/nmi_test_synthetic_v1.parquet` 由 D4 day 一次性 generate + git-commit + golden-checksum。`pytest -m fast` 整套 14 NMI 测试 < 30 s; integration full-data test (production bootstrap_n=1000) 标 `@pytest.mark.slow` 仅 nightly run。同规则适用于 D2 cell_id 派生测试 (small synthetic panel) + D4 residual 测试 (article-level fixture)。

### 4.2 集成 gate（修 E-NEW-2）

- `tests/integration/test_dag_consistency.py` — 校验 stage 39c 在 STAGES_VALIDATION + OUTPUT_REGISTRY
- `tests/integration/test_panel_reproducibility.py` — 必须**重新生成 golden baseline** (因加 ~70 列 = 8 cell + 18 residual + 6 cm_ctx residual + 6 nmi 元数据 + 其他)
- `tests/integration/test_prompt_version_wired.py` — v8 保持不变 (无需 bump)
- **`tests/integration/test_paper_spec_schema.py`** (修 E-NEW-2 + F2) — v3.4.0 实测此测试**不存在**于 baseline 1175 测试套件; v3.5.0 PR **新建** (D6 day) + 同步 schema 定义。基础 schema 沿用 master plan v2 §5.2.3.bis 定义，新建测试覆盖 9 paper_spec.yaml × `tables.t6` 字段 (P3/P4/P5 模板存在性 + 其余 6 paper null 显式声明) ≈ 12 项

### 4.3 golden baseline 重新生成

```powershell
F:\Anaconda3\python.exe scripts\migrate\generate_golden_snapshot.py
F:\Anaconda3\python.exe -m pytest news_process\tests\integration\test_panel_reproducibility.py
```

**audit trail**: golden snapshot diff (v3.4.0 → v3.5.0) commit hash 记录到 [stage3_v3_5_0_augmentation_plan_audit_log.md §C](stage3_v3_5_0_augmentation_plan_audit_log.md)。

**Cross-platform consistency** (修 H-NEW-3): golden baseline 只校验 NMI matrix **parquet hash**（确定性）+ 列 schema；PNG heatmap 仅 visual artifact，**不进 hash gate**。

**Panel 体积估算** (修 F24): v3.4.0 panel parquet ~30 MB (~2033 列 × 84 bank × 18 year row 估算上限), v3.5.0 +70 列 → parquet ~50 MB (Int8/Int32/bool 列 sparse 压缩好); .dta 同列规模因 byte 编码 (cell_id Int8 / indep_frac float64) 估 ~80 MB → 120 MB. Stata read 时间 v3.5.0 +30% (单机 < 30 s, 不影响 main regression turn-around). Replication 包体积影响 < +20 MB / paper。

### 4.4 CI 5 jobs 兼容（修 E-NEW-3）

**Invariant**: v3.5.0 新增 ~46 测试**均不 import torch / transformers / sentence-transformers**，仅依赖 sklearn 1.5+ / pandas 2.2+ / numpy 2.x（已在 light job runtime deps）。5 个 CI job（4 light + 1 full）全绿。

任何后续向 v3.5.0 加 torch-dependent test 必须 `pytest.importorskip('torch')` self-guard（per [memory: ci_matrix](../../../MEMORY.md)）。

---

## §5. 文档同步清单（全量, 修 D-NEW-2 + D-NEW-3 + M6 + G-NEW-2）

| 文档                                                                                                      | 修改                                                                                                                                                                                                                                                                                                                                                                                                                                | 优先级            |
| --------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- |
| [innovation_collab_mode_framework.md §2](innovation_collab_mode_framework.md)                             | 升级稀疏 cell 处理为 Stata-pre-regression-layer 决策树（§2.1.4）                                                                                                                                                                                                                                                                                                                                                                    | **P0** (blocking) |
| [stage3_third_dim_plan_v3.4.0.md](stage3_third_dim_plan_v3.4.0.md)                                        | 加 "下游延展: v3.5.0 §2.1 cell / §2.2 NMI / §2.3 residual" footnote                                                                                                                                                                                                                                                                                                                                                                 | P1                |
| [calibration_plan_v5.2_delta.md](calibration_plan_v5.2_delta.md) (修 F18)                                 | 加 D3 NMI 与 Cohen's κ 的并列方法说明 + D4 disagree/freerider/quietworker stratum proposal。**承接**: calibration v5.2 团队 owner 在 D6-D7 day 收到 v3.5.0 PR ping; calibration v5.2 G1 解封后 (per memory: calibration_plan_v5_1_frozen), 9 strata 标注扩为 12 strata (+disagree/freerider/quietworker), IRR 评估 deadline = v3.5.0 ship 后 +6 wk; 若 calibration v5.2 推迟则 D4 P10 立项 (§2.3.6) 同步推迟, v3.5.0 本身仍可 ship. | P1                |
| **[B_route_master_plan_v2.md](../plan/B_route_master_plan_v2.md)** §5.2.3.bis                             | **加 `tables.t6` schema 字段定义** + 全 9 paper schema 强制 explicit null/template (修 B-NEW-4)                                                                                                                                                                                                                                                                                                                                     | **P0** (blocking) |
| **[B_route_master_plan_v2_audit_log.md](../plan/B_route_master_plan_v2_audit_log.md)** (修 D-NEW-2 + F15) | 加 R93+ entries (R90-R92 epoch 5 close, R93 epoch 6 launch by v3.5.0)。**Entry 模板** (修 F15): (a) finding count = 0 (epoch 6 streak 标准); (b) 涉及 PR/commit hash; (c) plan SHA256 anchor (本 plan §11 audit trail 已 trace 全 finding); (d) 与 v2.55→v2.56 epoch 5 launch 的 streak 关系。具体格式见 R89 entry 为参考样式。                                                                                                     | **P0**            |
| `CHANGELOG.md` v3.5.0 entry                                                                               | D2/D3/D4 + ~46 tests + golden regen + R0 refactor encode_collab.py                                                                                                                                                                                                                                                                                                                                                                  | **P0**            |
| `news_process/CLAUDE.md`                                                                                  | bump v3.4.0 → v3.5.0; test 1175 → ~1221; shim enumeration 26 → 27 incl.**39c**                                                                                                                                                                                                                                                                                                                                                      | **P0**            |
| **[MEMORY.md](../../../MEMORY.md)** (修 D-NEW-3)                                                          | 新增:`v3_5_0_landmarks.md`; 更新 `shim_inventory.md` 26→27; 更新 `paper_portfolio_decision_gates.md` 加 epoch 6 streak 3/3 gate                                                                                                                                                                                                                                                                                                     | **P0**            |
| `paper_spec.yaml × 9 paper` (修 M6 + G-NEW-2)                                                             | P3/P4/P5:`tables.t6.template: 19_table6_cell_decomposition`; **其余 6 paper: `tables.t6: null` explicit** (防 schema test fail)                                                                                                                                                                                                                                                                                                     | P1                |
| **P5 paper_spec.yaml** (修 A-NEW-2)                                                                       | `treatment.alternative` 新增 `cell_id_full` + `alternative_construction.cell_id_full` 公式                                                                                                                                                                                                                                                                                                                                          | **P0**            |
| `news_process/papers/_common/stata_templates/19_*.do.tmpl`                                                | 新建 D2 cell decomposition 模板                                                                                                                                                                                                                                                                                                                                                                                                     | **P0**            |
| `news_process/papers/_common/stata_templates/25_*.do.tmpl`                                                | 新建 D4 dual-track residual 模板                                                                                                                                                                                                                                                                                                                                                                                                    | **P0**            |
| `news_process/pipeline/panel/encode_collab.py`                                                            | **新建 refactor 目标文件**（修 B-NEW-1）, 从 encode.py 抽 ~200 行 + 加 D2/D4 ~170 行                                                                                                                                                                                                                                                                                                                                                | **P0**            |

**SSRN replication package 锁定策略** (修 M5):

| 已 SSRN 上传 paper                                              | 锁定行为                                                                                                                                             |
| --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| bank_fintech_tone (P1)                                          | v3.4.0 panel snapshot saved as `40_panel_yearly_v3_4_0_locked.parquet` (git-tagged `v3.4.0-panel-frozen`); replication 包 pin v3.4.0 commit 450c1aa7 |
| benefit_society / brokerage_network / llm_peer / strategic_diff | 若有 SSRN preprint 同上锁定; replication 包不动                                                                                                      |
| P2-P5 + 未投 paper                                              | 用 v3.5.0 panel（含新列）                                                                                                                            |

**Golden baseline 副本策略** (修 F9): D7 day regen 前，将 `tests/fixtures/golden_panel_v0.json` v3.4.0 版本备份为 `tests/fixtures/golden_panel_v0_v3_4_0.json` (git-tagged `v3.4.0-golden-frozen`); v3.5.0 新 golden 命名 `golden_panel_v0.json` (覆盖默认入口) + 保留 v3.5.0 之前快照 1 份。回退路径 = `cp golden_panel_v0_v3_4_0.json golden_panel_v0.json` + revert encode_collab.py commits。

**Paper-level replication 包结构** (修 F17): 每 paper (P1-P5 + retrofit 4) 提交期刊时, replication 包**包含**: (a) panel snapshot pinned to v3.4.0 或 v3.5.0 (per SSRN 锁定策略); (b) 该 paper 的 `papers/<paper_id>/` 完整目录 (analysis.py, figures.py, tables.py, paper_spec.yaml); (c) `papers/_common/` 全部模板; (d) `pipeline/panel/` 完整 encode + encode_collab + stata_export 实现; (e) v3.4.0 OR v3.5.0 `requirements.lock` 对应版本; (f) README.md 说明运行步骤。v3.5.0 augmentation 仅对**用 v3.5.0 panel 的 paper** (P2-P5 + 未投) 出现; v3.4.0-pinned paper (P1 + 4 retrofit if SSRN-locked) replication 包不含 D2/D3/D4 任何输出。

**PR Reviewer & Sign-off Matrix** (修 F19): v3.5.0 PR 需 sign-off 自 (a) **Methodology Lead**: framework §2 升级 (D2.1.4 cell merge) + §2.2 NMI 三档解读 + §2.3 D4 文献归因; (b) **Code Owner pipeline/panel/**: encode.py refactor + encode_collab.py + stata_export.py; (c) **Paper Authors P3/P4/P5**: paper_spec.yaml `tables.t6` + `treatment.alternative` 修改 confirm; (d) **DAG Owner**: stage 39c 注册 + OUTPUT_REGISTRY entry。Sign-off 路径 = GitHub PR review (REQUIRED) + audit log §G.signoff_record 记录。

---

## §6. 时间表 (10 wd dev + 2-4 wd audit P50 / up to 22 wd P99 + calendar 14-16 wd P50 / up to 30-35 wd P99, 修 m8 + B-NEW-1 + F10 + F23 + F42)

**Calendar time vs work time** (修 F10 + F23 + F42): 总 dev wall-time 10 wd, **audit wall-time 2-4 wd (P50) / up to 22 wd (P99, 参 §7 R7 streak 11 轮历史)**, calendar time 14-16 wd (P50) / **up to 30-35 wd (P99 worst-case 如多次 streak reset)** 因 D0 含 §9.6 epoch 5 close + §9.7 user Q-gate 等待时间 (非 dev 工作但需 elapsed time). 该 P99 数字必须纳入 v3.5.0 owner 与 stakeholders 沟通 (§12 已同步).

| Day                                           | 任务                                                                                                                                                                                                                                        | 输出                                                           | 依赖              |
| --------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ----------------- |
| **D0** (calendar ≥ 1 wk, work ≤ 1 wd, 修 F10) | §9 前置条件全部 ✅ + Plan v0.2 git-tag `v3.5.0-plan-frozen`（per §0 pre-registration freeze）。**等待**: epoch 5 R90-R92 close + user 授权 framework §2 升级 Q-gate.                                                                         | tag + epoch 6 streak 2/3 reaudit                               | —                 |
| **D1**                                        | framework §2 升级 PR (D2.1.4) + B_route_master_plan_v2 §5.2.3.bis tables 字段 schema 定义                                                                                                                                                   | doc commits + epoch 6 audit Round-1                            | D0                |
| **D2**                                        | **R0: encode.py → encode_collab.py 拆分 refactor** (修 B-NEW-1)                                                                                                                                                                             | refactor commit, 1294 行 → 1100 行 + 新文件 200 行；旧测试全绿 | D1                |
| **D3**                                        | D2 cell_id + cross-identity 校验 + stata Table 19 模板 + 14 单测 + 2 panel 单测                                                                                                                                                             | encode_collab.py +80 行 + 16 tests                             | D2                |
| **D4**                                        | D3 stage 39c + dag/schemas/shim 注册 + 14 NMI 单测 + permutation null + listwise/pairwise + bootstrap fix                                                                                                                                   | stage 39c + 14 tests                                           | D2                |
| **D5**                                        | D4 article 派生 + invariants + ctx coverage 自适应 + small-sample restriction + 12 单测 + stata Table 25                                                                                                                                    | encode_collab.py +120 行 + 12 tests                            | D2                |
| **D6** (修 F11)                               | paper_spec.yaml × 9 同步 (P3/P4/P5 + 6 null) + test_paper_spec_schema**新建并填充** (~12 项, 非更新, F2 已澄清) + treatment.alternative cell_id_full 字段更新. 注: master plan v2 §5.2.3.bis schema 定义已在 D1 day 完成, D6 仅消费 schema. | spec yaml diffs + schema test 全绿                             | D3-D5 + D1 schema |
| **D7**                                        | 集成测试 + golden baseline regen + SSRN panel snapshot 锁定 + 11-paper 硬编码 scan                                                                                                                                                          | golden snapshot diff + scan report                             | D6                |
| **D8**                                        | CHANGELOG + CLAUDE.md + MEMORY.md + master plan audit log R93+ entry                                                                                                                                                                        | 所有 doc sync                                                  | D7                |
| **D9-D10** (修 F23)                           | **streak 2-3 epoch 6 audit (每轮 wall-time 0.5-2 wd 视 finding count 自适应)**                                                                                                                                                              | audit log Round-2 + Round-3 → ship                             | D8                |

**critical path** = D0 → D1 → D2 → D3/D4/D5 (并行) → D6 → D7 → D8 → D9 → D10

---

## §7. 风险与 mitigation（修 F-NEW-1 / F-NEW-2 / F-NEW-3 + m9）

| ID                        | 风险                                                                                                  | 严重     | mitigation                                                                                                                                                                                                                                                                                             |
| ------------------------- | ----------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| R1                        | framework §2 升级 D2.1.4 触发 epoch 6 audit 不通过                                                    | HIGH     | D1 先开 audit；driver 决策权回 user (Q-gate)；若驳，D3 退回 framework §2 原写法 "limitations only"，不合并 cell                                                                                                                                                                                        |
| R2 (修 I-NEW-1)           | NMI Z > 2.58 (weak independence)                                                                      | HIGH     | pre-registered contingency:**v3.5.0 paper Appendix A.2 暂不 publish**, panel 列保留落盘；v3.6.0+ scope 加 prompt 边界 epoch 7 audit；v3.5.0 本身**仍可 ship**                                                                                                                                          |
| R3 (修 C-NEW-3)           | D4 ctx coverage < (v3.4.0 baseline - 2σ)                                                              | MED      | encode_collab.py 抛 warning + 标 `panel.attrs['D4_data_quality']`；不阻 ship 但 paper 用时需 caveat                                                                                                                                                                                                    |
| R4                        | golden baseline regen 漏列                                                                            | MED      | D7 day 跑两遍 `test_panel_reproducibility.py` + diff golden_panel_v0.json before/after                                                                                                                                                                                                                 |
| R5 (修 F-NEW-2)           | paper_spec.yaml schema 校验失败                                                                       | LOW      | **D1 day 先**在 B_route_master_plan_v2 §5.2.3.bis 加 `tables.t6` schema 定义 + 同步 test_paper_spec_schema schema → D6 day 校验已可通过（破除原循环逻辑）                                                                                                                                              |
| R6 (修 F-NEW-3)           | prompt v8 git tag 缺失                                                                                | LOW      | **独立 hotfix PR** 在 v3.5.0 之外补打，10 分钟工作，不阻 v3.5.0 critical path                                                                                                                                                                                                                          |
| **R7 (新加, 修 F-NEW-1)** | **epoch 6 streak 3/3 任意轮 finding > 0**                                                             | **HIGH** | streak reset → 接受 dev 时间扩展（参 v2.55 epoch 3 streak 1 → 11 轮历史[B_route audit log L19](.../audit_log.md#L19)）；预计 v0.2 → v0.6 约 4-6 轮收敛                                                                                                                                                 |
| **R8 (新加, 修 m9)**      | NMI > null_p99 触发 R2 → paper_spec.yaml × 3 已 commit 的 t6 字段需回滚                               | MED      | **Rollback path**: `git revert <paper_spec commits>` 保留 panel 列 + Stata 模板（不进 paper）；audit log §D rollback_log 记录                                                                                                                                                                          |
| **R9 (新加, 修 G-NEW-1)** | P5 audit_rounds_target_min=8 已规划满, 新 D4 robustness 行超 budget                                   | MED      | D6 day 与 P5 paper authors confirm: D4 进 Table 5 行 OR 全部 omit；不 mid-flight 决策                                                                                                                                                                                                                  |
| **R10 (新加, 修 F5)**     | R0 encode.py → encode_collab.py refactor 引入 regression (v3.4.0 1175 测试某些 panel-level test fail) | MED      | D2 day 完成 refactor 后**强制运行**全量 `pytest news_process/tests/` (非仅新测试) → 必须 1175 测试全绿才能启动 D3。若任一 fail，**rollback**: git reset refactor commit，改为不拆分直接在 encode.py 内追加 D2/D4 代码（接受 1294 → ≈1470 行临时膨胀 (与 §1.1 R0 refactor 路径 1100 + 200 + 170 = 1470 等价算术, 修 F34)），J-NEW-1 maintainability 红线延后到 v3.6.0 处理。 |

---

## §8. 后续 milestone

### 8.1 M5 主回归 (P3/P4/P5)

cell_id + D4 residual 进 P3/P4/P5 Table 6 + Table 5。M5 阶段同步：

- D3 NMI 进 Appendix A.2 (per §2.2.6 三档分支)
- D4 进 robustness（R9 决定）

### 8.2 v3.6.0 plan（不在 v3.5.0 scope）

- **A2** partner_count + partner_types (prompt v8 → v9 bump)
- **D1** prob_score 校准（Platt 公式重写：先 logit transform → 再 sigmoid + isotonic pooled-fit）
- 需要 LLM cap $5,000 → $5,500 申请

**Ownership & handoff** (修 F22): v3.6.0 plan owner = v3.5.0 plan owner 同一人 (避免 handoff 损失); 启动条件 = v3.5.0 epoch 6 close (PLAN_VERSION 稳定) + calibration v5.2 G1 解封 + LLM cap $5,000 → $5,500 批准; A2 (partner_count) 与 D1 (prob 校准) 同步 ship (一 PR 拆 stages); 若任一前置阻塞, v3.6.0 plan 推迟至阻塞解除。

### 8.3 v3.7.0 plan

- **A1** multi-class collab_mode 6-class (prompt v9 → v10, 全量重跑 ~$2,000)
- 与 B1 (innovation_novelty) 同批 ship 摊薄 LLM 全量重跑成本
- **CELL_LABEL_MAP 重写** (修 J-NEW-2: 8 → 24 项 breaking change)

### 8.4 D4 P10 立项 (远期)

D4 single-handedly 撑起 "Free-riding vs Quiet-working" P10。立项条件:

- **Calibration v5.2 G1 解封** (修 F39: 受 v5.1 G1 fail 阻塞 — v5.1 阻塞解除是 v5.2 启动 hard prereq, per [memory: calibration_plan_v5_1_frozen](../../../MEMORY.md)) + 含 disagree stratum 实测 IRR ≥ 0.7
- SSRN methodological note 完成
- v3.5.0+ M5 阶段实测 Z > 1.96（有信号才值得立项）

---

## §9. 前置条件 (hard prerequisites, all ✅ before D0)

| ID                          | 条件                                                                                                           | 状态                                                                 | 检查方法                                                                                                                                                                                                                                                                                                                                              |
| --------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| §9.1                        | v3.4.0 baseline 测试 1175 passed                                                                               | 假设 ✅ (CLAUDE.md 声明)                                              | `pytest -q`                                                                                                                                                                                                                                                                                                                                           |
| §9.2                        | `prompt-v8-supplementation-released` git tag 存在                                                              | ❌ 实测 `git tag --list` 不显示 (CLAUDE.md/memory 声明 vs 实际不一致) | **独立 hotfix PR 在 v3.5.0 之外补打** (修 F-NEW-3, 不阻 D0)                                                                                                                                                                                                                                                                                           |
| §9.3                        | calibration v5.2 不阻塞 v3.5.0                                                                                 | ✅ (v3.5.0 不依赖 v5.2)                                               | 本计划 §1.2                                                                                                                                                                                                                                                                                                                                           |
| §9.4                        | LLM budget 状态 = $4,480 / $5,000 cap, buffer $520                                                             | ✅                                                                    | v3.5.0 $0 LLM, 不消耗 buffer                                                                                                                                                                                                                                                                                                                          |  |  |
| §9.5 (修 A-NEW-4)           | **§0 pre-registration freeze 启动: plan v0.2 git-tag `v3.5.0-plan-frozen`**                                    | ⏳ D0 启动                                                            | D0 day 行动项                                                                                                                                                                                                                                                                                                                                         |
| §9.6 (修 A-NEW-1 + m6 + F8) | **★ epoch 5 streak 3/3 achieved** (R90-R92 三轮 0-finding, epoch 5 close)                                      | ⏳ R89 后未跑 R90+                                                    | **必须在 D0 之前完成**; 不可越级启动 epoch 6。**热同步约定 (F8)**: R90-R92 期间若有任意 finding 涉及 (a) prompt v8 字节级变更 (b) panel schema breaking (c) paper_spec.yaml schema breaking (d) **`pipeline/panel/encode.py` 内部 `_aggregate_by_collab_mode` 函数签名或行边界 breaking change** (v3.5.0 R0 refactor 直接依赖此函数当前结构, hotfix 修改会让拆分目标失锚, 修 F41) — v3.5.0 plan v0.x **必须暂停**, 等 epoch 5 close + reaudit v3.5.0 plan compatibility 后再启动 D0; 其它无关 finding (plan 错字 / CHANGELOG 笔误) 不阻塞。 |
| §9.7 (修 A-NEW-4)           | framework §2 升级**用户授权 Q-gate** (D2.1.4 cell merge rule)                                                  | ⏳ 待 user 决策                                                       | D1 day 提 Q-gate question                                                                                                                                                                                                                                                                                                                             |
| §9.8 (新加)                 | D0 day 启动 epoch 6 streak 1/3 audit (R93+)                                                                    | ⏳ 待 §9.6 满足后启动                                                 | 创建[stage3_v3_5_0_augmentation_plan_audit_log.md](stage3_v3_5_0_augmentation_plan_audit_log.md)                                                                                                                                                                                                                                                      |
| §9.9 (修 G-NEW-3)           | D0 day 在 v3.5.0 plan 全文 grep "11 paper" / "12 paper" / "11-portfolio" 等硬编码，使用动态 `len(paper_specs)` | ⏳ 待 D0 启动                                                         | scan report 入 audit log §A                                                                                                                                                                                                                                                                                                                           |
| §9.10 (修 H-NEW-1)          | D0 day 测定 v3.4.0 ctx coverage baseline + git-tag `v3_4_0_ctx_coverage_baseline.json`                         | ⏳ 待 D0 启动                                                         | 1 行脚本读 stage 21 parquet 后保存 mean/std                                                                                                                                                                                                                                                                                                           |
| §9.11 (修 F14 + F38)        | Stage 10.5 PII scrubbing 已完成 (raw news → scrubbed parquet)                                                  | ⏳ **待验证** (D0 day 第一动作; 修 F38 撤回原假设✅)                   | grep stage 21 parquet header + 检查 raw news → scrubbed pipeline 实际 lineage; v3.5.0 仅消费 v3.4.0 stage 21 输出 (scrubbed labels, no raw text); 若验证失败 v3.5.0 暂缓启动                                                                                                                                                                            |
| §9.12 (修 F33)              | v3.4.0 immutable git tag 存在 (`v3.4.0` 或 `v3.4.0-baseline-frozen`)                                            | ⏳ 待验证 (若缺则 D0 day 第一动作打 tag)                              | `git tag --list \| grep v3.4.0` 验证; commit hash 锚定不可替代 immutable tag                                                                                                                                                                                                                                                                          |

---

## §10. 锚定文献（修 C2 + D-NEW-4 + I-NEW-3）

**新增 / 修订引用**:

- Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics: An Empiricist's Companion.* Princeton University Press. (D2 saturated regression 主类比)
- Bagozzi, R. P., & Yi, Y. (1988). On the evaluation of structural equation models. *Journal of the Academy of Marketing Science*, 16(1), 74-94. (D3 discriminant validity)
- Fred, A. L. N., & Jain, A. K. (2003). Robust data clustering. *2003 IEEE Conference on Computer Vision and Pattern Recognition*. (D3 NMI arithmetic averaging — **替换原 Strehl & Ghosh 2002 锚**, 修 C2)
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? *Journal of Finance*, 66(1), 35-65. (D4 类比借用)
- Nosek, B. A., Ebersole, C. R., DeHaven, A. C., & Mellor, D. T. (2018). The preregistration revolution. *PNAS*, 115(11), 2600-2606.
- Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies with heterogeneous treatment effects. *Journal of Econometrics*, 225(2), 175-199. (D2 cohort decomposition 类比, 修 I-NEW-3)
- Vinh, N. X., Epps, J., & Bailey, J. (2010). Information theoretic measures for clusterings comparison. *Journal of Machine Learning Research*, 11, 2837-2854. (D3 NMI 主锚)
- Westphal, J. D., & Zajac, E. J. (2001). Decoupling policy from practice. *Administrative Science Quarterly*, 46(2), 202-228. (D4 **类比借用**, 软化语气 — 修 m2)

**Dropped**:

- ~~Strehl & Ghosh (2002 JMLR 3)~~ — geometric averaging 版本与本实现不匹配 (修 C2)
- ~~Cohen (1988) "small-effect detection 下限"~~ — 误用 (修 m1); n<50 改述为 "OLS cell-level fixed-effect estimation rule of thumb"
- ~~Goodman-Bacon (2021 JOE) primary anchor~~ — staggered DiD 与 cross-sectional 8-cell 不同, 改为 secondary "思路类比" (修 I-NEW-3)

**继承 v3.4.0** (不变): Westphal & Zajac 1994/1998 ASQ; Gomber 2018 JMIS; Chesbrough 2003; Laursen & Salter 2006 SMJ; Hagedoorn 1993 SMJ; Cohen & Levinthal 1990 ASQ; Hassan 2019 QJE; Fiss & Zajac 2006 ASQ.

---

## §11. Audit Trail — v0.1 → v0.2 修正 mapping

完整 46 findings 修正落点。每 finding 可 reverse-trace 到具体 §。

### v0.1 → v0.2 CRITICAL 修正 (8)

| Finding                     | 来源 | v0.2 修正位置                                              |
| --------------------------- | ---- | ---------------------------------------------------------- |
| C1 NMI bootstrap row-pair   | 轮 2 | §2.2.2 `clean_boot[d1], clean_boot[d2]` 两列同步           |
| C2 NMI 文献错配             | 轮 2 | §10 dropped Strehl-Ghosh, added Vinh 2010 + Fred-Jain 2003 |
| C3 NMI 阈值无来源           | 轮 2 | §2.2.2 permutation null + §2.2.4 Z-score 解读              |
| A-NEW-1 epoch 5 未 freeze   | 轮 3 | §9.6 必须 R90-R92 close, §1 不变量                         |
| B-NEW-1 encode.py 1294 行   | 轮 3 | §1.1 R0 refactor + §6 D2 day + §2 encode_collab.py 拆分    |
| G-NEW-1 D4 与 P5 derivation | 轮 3 | §2.3.1 区分表 + R9 audit budget 决定                       |
| I-NEW-1 R2 prompt 矛盾      | 轮 3 | §2.2.6 contingency + §7 R2 paper 暂缓 / panel 落盘         |
| M1 Stata 编号 22 撞名       | 轮 2 | §2.1.5 = 19, §2.3.5 = 25                                   |

### v0.1 → v0.2 MAJOR 修正 (20)

| Finding                          | 来源 | v0.2 修正位置                                   |
| -------------------------------- | ---- | ----------------------------------------------- |
| M2 cell 合并发生层               | 轮 2 | §2.1.4 Stata pre-regression 层                  |
| M3 dirty label 防御              | 轮 2 | §2.1.1 VALID_SUBST/LOCUS/COLLAB isin            |
| M4 shim NN                       | 轮 2 | §2.2.1 改 39c + §5 CLAUDE.md 同步               |
| M5 SSRN 一致性                   | 轮 2 | §5 panel snapshot 锁定策略表                    |
| M6 paper × 5 → × 9               | 轮 2 | §2.1.6 9 paper 表 + §5 spec yaml × 9            |
| A-NEW-2 D2 treatment.alternative | 轮 3 | §2.1.7 P5 yaml diff + §5 P0 条目                |
| A-NEW-3 跨轨 vs 单轨             | 轮 3 | §2.3.1 区分表                                   |
| A-NEW-4 pre-reg timing           | 轮 3 | §0 + §9.5 freeze invariant                      |
| B-NEW-2 pandas Int8 NA           | 轮 3 | §2.1.1 `.where(valid, pd.NA)`                   |
| B-NEW-3 OUTPUT_REGISTRY          | 轮 3 | §2.2.1 显式 entry                               |
| B-NEW-4 tables 字段 schema       | 轮 3 | §5 master plan v2 §5.2.3.bis 加定义 + §7 R5 修  |
| C-NEW-1 NMI dim-pair n           | 轮 3 | §2.2.2 listwise_complete + n_pair_matrix        |
| C-NEW-2 cell cross-identity      | 轮 3 | §2.1.2 indep/collab 拆和校验                    |
| C-NEW-3 ctx coverage 阈值        | 轮 3 | §2.3.4 自适应 baseline - 2σ                     |
| C-NEW-4 disagree 互斥文档        | 轮 3 | §2.3.2 invariants (i)-(iii)                     |
| D-NEW-1 templates 数字撕裂       | 轮 3 | §2.1.5 双口径 footnote                          |
| D-NEW-2 audit log 同步           | 轮 3 | §5 master plan audit log R93+                   |
| D-NEW-3 MEMORY.md                | 轮 3 | §5 三 memory entry                              |
| E-NEW-1 TDD ratio                | 轮 3 | §4.1 NMI 8 → 14, residual 7 → 12                |
| E-NEW-2 paper_spec_schema gate   | 轮 3 | §4.2 加 integration gate                        |
| F-NEW-1 epoch 6 streak fail      | 轮 3 | §7 R7 新加                                      |
| F-NEW-2 R5 循环逻辑              | 轮 3 | §7 R5 改 D1 schema-first                        |
| G-NEW-2 paper_spec × 9           | 轮 3 | §5 9 paper 全列                                 |
| G-NEW-3 11-paper 硬编码          | 轮 3 | §9.9 D0 scan report                             |
| H-NEW-1 LLM stochasticity        | 轮 3 | §2.2.2 reproducibility lock + §2.2.5 disclosure |
| H-NEW-2 bootstrap seed           | 轮 3 | §2.2.2 SeedSequence.spawn                       |
| I-NEW-2 D4 文献厚度              | 轮 3 | §2.3.6 methodological note plan + P10 defer     |
| J-NEW-2 v3.7.0 升级              | 轮 3 | §2.1.1 CELL_LABEL_MAP 注释 + §8.3 breaking note |

### v0.1 → v0.2 MINOR 修正 (18)

| Finding                      | v0.2 修正位置                                  |
| ---------------------------- | ---------------------------------------------- |
| m1 Cohen 1988 误用           | §2.1.4 改 OLS rule of thumb                    |
| m2 W&Z 2001 语气             | §2.3.1 标 "类比借用" + §10 软化                |
| m3 Int8 NA 写法              | §2.1.1 `.where()` 写法（与 B-NEW-2 一致）      |
| m4 heatmap 路径              | §2.2.3 `data/processed/` 不进 papers_assets    |
| m5 residual_frac_cols 未定义 | §2.3.2 + §2.3.3 显式列表                       |
| m6 epoch streak 概念         | §9.6 R93+ streak 不跨 epoch（与 A-NEW-1 一致） |
| m7 v3_3_to_v3_4 migration    | §4.1 显式保留 11 个 forward compat             |
| m8 工时低估                  | §6 8 天 → 10 天                                |
| m9 paper_spec.yaml 回滚      | §7 R8 新加 rollback path                       |
| m10 audit 编号在注释         | §2.2.2 注释改业务描述                          |
| B-NEW-5 shim 39c             | §2.2.1 改 39c（与 M4 一致）                    |
| D-NEW-4 Fred-Jain 加锚       | §10 新增                                       |
| E-NEW-3 CI guarantee         | §4.4 invariant 声明                            |
| F-NEW-3 git tag 独立 PR      | §3 + §7 R6 + §9.2                              |
| H-NEW-3 PNG hash             | §4.3 PNG 不进 hash gate                        |
| I-NEW-3 Goodman-Bacon        | §10 dropped, 加 Angrist-Pischke + Sun-Abraham  |
| J-NEW-3 命名约定             | §2.1.2 `n_articles_cell_{i}_full` 保留 _full   |
| (隐含) plan v0.2 自洽 audit  | §11 本表 trace 表本身                          |

### v0.2 期望状态

| 维度      | v0.1 | v0.2 期望 | epoch 6 streak 3/3 标准 |
| --------- | ---- | --------- | ----------------------- |
| CRITICAL  | 8    | **0**     | 0                       |
| MAJOR     | 20   | **0**     | 0                       |
| MINOR     | 18   | **0**     | 0                       |
| **Total** | 46   | **0**     | **0 × 3 轮**            |

预计 v0.2 streak 2/3 reaudit 可能仍有 3-8 个 NEW findings（修正本身引入的、或前两轮漏审的）；预计 v0.3 / v0.4 收敛到 0。

---

## §12. Non-technical Summary (for Paper Authors & Reviewers, 修 F20)

v3.5.0 在不改 prompt / 不重跑 LLM / 不增预算的前提下，给 v3.4.0 panel 加 3 类后处理数据列：

- **D2 8-cell 组合标签** — 让 P3/P4/P5 paper Table 6 能跑 8 个机制 cell 的回归 (例如 "实质性 + 底层技术 + 自主研发" 是 cell 1, "象征性 + 应用场景 + 外部协同" 是 cell 8)。直接回答审稿人"机制问题"。
- **D3 三标签独立性诊断** — 在 400k 文章上实测 substantiveness × locus × collab 三标签的 NMI matrix, paper Appendix A.2 给硬证据回应"三 construct 是否真独立"。
- **D4 全文-段落判定差值信号** — paper Table 5 robustness 加 "搭便车 / 低调实干" 控制项, 洗掉 PR-only 噪音。

**Paper authors 影响**: P3/P4/P5 需在 paper_spec.yaml 加 `tables.t6.template` 字段（D6 day 由 plan owner 提交 PR commit, paper authors 仅需 review 确认）。其余 6 paper (P1/P2 + 4 retrofit) 加 `tables.t6: null` 显式声明。

**期刊审稿人影响**: replication 包包含 v3.4.0 OR v3.5.0 panel 对应版本（per §5 SSRN 锁定策略）。已 SSRN 上传 paper (P1) 锁定 v3.4.0 baseline, 不受 v3.5.0 augmentation 影响。

**预算 / 时间影响**: $0 LLM, 10 wd dev + 2-4 wd audit (P50, calendar 14-16 wd) **或 worst-case 22 wd audit / 30-35 wd calendar (P99, 多次 streak reset, 修 F42)**. 不消耗 v3.4.0 LLM budget buffer ($520 仍保留给 v3.6.0)。

**Paper authors review checklist (修 F37)**: P3/P4/P5 paper authors 收到 v3.5.0 PR notification 时, 仅需 review (a) 该 paper `paper_spec.yaml` diff (≤30 行, 加 `tables.t6.template: 19_table6_cell_decomposition` + `treatment.alternative` 加 `cell_id_full` + `alternative_construction` 加公式); (b) plan §2.1.4 cell merge decision tree 是否适用于该 paper sample; (c) plan §2.1.6 中该 paper `tables.t6` 状态是否 confirm。其余 6 paper (P1/P2 + 4 retrofit) 仅 review (a) `tables.t6: null` 显式声明 (1 行 diff)。
