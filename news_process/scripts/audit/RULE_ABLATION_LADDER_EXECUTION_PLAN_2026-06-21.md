# 逐 token 状态机「分步中间变量」稳健性梯度 — 执行计划

> 状态: **代码已实现 (2026-06-21)。用户拍板: ① 全部 (full powerset 6 新变体) · ② 立即闭环 (T=2 golden) · ③ v3.11.1 · ④ 完整 (HEURISTIC_LABELS + codebook)。**
> 已完成: 引擎 + encode + 标签 + codebook + 测试 (90+ 绿) + ruff clean + dag 一致。
> **⛔ golden 重生待用户确认**: 盘上 `40_panel_yearly.parquet` **缺失** → 非"外科注入"而是**全 panel 重建** (multi-hour, 写共享 disk, 见 §5 更新)。
> 日期: 2026-06-21 · 作者: Claude (ultracode; 调研 9-agent `wf_08ac2166` + 实现复审 `wf_b012b7c2`)

---

## 0. 用户诉求 (逐字解析)

> 核心引擎 `_compute_sentiment_with_rules` 是一个逐 token 状态机，处理 **否定窗口、程度副词六级权重、转折增强** 三类语言学修饰。**每经过一个步骤都要留存中间变量作为稳健性检验。**

诉求 = 把"全规则一次算到底"改造为**分步可观测的规则消融梯度 (rule-ablation ladder)**: 在状态机依次施加 **① 否定翻转 → ② 程度缩放 → ③ 转折增强** 的过程中, 每加一条规则就落一个**独立自归一化**的中间得分列, 供论文做"主结果对每条语言学规则是否敏感"的稳健性检验。

---

## 1. 现状基线 (已读码核实, 非推测)

引擎: `pipeline/sentiment/tone_words.py::_compute_sentiment_with_rules` (L529-671)。

签名: `(tokens, sentiment_dict, apply_degree=True, apply_adversative=True)` → `(raw, normalized, pos_cnt, neg_cnt, matched_words)`。

三条规则在状态机中的施加顺序与开关现状:

| 规则 | 触发集合 | 数值效应 | 当前可否关闭 |
|---|---|---|---|
| ① 否定翻转 | `NEGATION_WORDS` (窗口 `NEGATION_WINDOW=2`) | `base → -base` | **否 (硬编码, 无 flag)** ← 缺口 |
| ② 程度副词 | `DEGREE_WORDS` (六级, 值域 `[0.3, 3.0]`) | `× degree_multiplier` | 是 (`apply_degree`) |
| ③ 转折增强 | `ADVERSATIVE_WORDS` | `× ADVERSATIVE_BOOST(=1.5)` | 是 (`apply_adversative`) |

归一化 (L669): `normalized = Σ(final) / Σ|final| ∈ [-1,+1]`。**每个变体各自 self-normalize → 分母 `Σ|final|` 随所启用规则改变。**

**已存在的消融变体** (= 梯度的两端 + 计数口径):
- `{dict}_score` (full = ①②③ 全开) — call site L1239-1240
- `{dict}_score_negonly` (①开 ②③关 = 仅否定) — call site L1259-1261
- `msent_score` (零规则原始极性计数) / `msent_negonly` (仅否定计数) — L1346/L1358-1362

> ⚠ **铁律 G0 — `negonly` 命名正确, 严禁改名。** 调研中 engine-math 子代理误判 `negonly` "应改名" (称其实为'全关')。**该判断错误**: `negonly` 调用 `apply_degree=False, apply_adversative=False`, 而否定为硬编码默认开 → 它确为"仅否定"。对抗验证与人工读码均确认。`negonly` / `msent_negonly` 列已被 panel 聚合 (`encode.py:580/644`)、stata 标签 (`stata_export.py:275-317`)、golden、6 个 stata 模板、paper_spec 消费 — **任何改名都是 breaking change, 不在本计划范围。** 本计划新增的"全关基线"另起名 `_raw` (见 §2)。

---

## 2. 核心设计决策 (经对抗验证收敛)

### D1 — 梯度只在「幅度口径」非退化, 计数口径已完备 ⭐ (定范围的关键洞察)

`msent` 用 **final 的符号计数** ((neg−pos)/(pos+neg))。程度 (②) 与转折 (③) 是**严格正乘子**, 只缩放幅度、**永不翻转符号** → 对计数零影响。故:

```
msent_raw   ≡ msent_score    (退化, 不新增)
msent_negdeg ≡ msent_negonly  (退化, 不新增)
```

**结论: 计数口径 (`msent`/`avg_msent`) 梯度已由 `msent_score` + `msent_negonly` 完整覆盖, 本计划不新增任何 `msent_*` / `avg_msent_*` 列。** (对抗验证 single-pass-correctness §iii 确认 "degree/adversative 严格正、不翻号"。)

幅度口径 (`{dict}_score`, `Σ|final|` 归一化) 才是程度/转折真正改变取值的地方 → 梯度只在此族展开。

### D2 — 全 powerset 梯度 (用户拍板「全部」), 8 组合 / 7 物化变体 + full

三规则 (neg/deg/adv) 全 powerset = 2³=8 组合; full `(T,T,T)` 为主列 `{dict}_score`, 余 7 入梯度谱:

| suffix | flag `(neg,deg,adv)` | 含义 | article 列 | 状态 |
|---|---|---|---|---|
| `raw` | `(F,F,F)` | 零规则基线 | `{dict}_score_raw{track}` | **新增** |
| `negonly` | `(T,F,F)` | 仅否定 (L&M 档) | `{dict}_score_negonly{track}` | 已有 (折入谱) |
| `degonly` | `(F,T,F)` | 仅程度 | `{dict}_score_degonly{track}` | **新增** |
| `advonly` | `(F,F,T)` | 仅转折 | `{dict}_score_advonly{track}` | **新增** |
| `negdeg` | `(T,T,F)` | 否定+程度 (= full−adv) | `{dict}_score_negdeg{track}` | **新增** |
| `negadv` | `(T,F,T)` | 否定+转折 (= full−deg) | `{dict}_score_negadv{track}` | **新增** |
| `degadv` | `(F,T,T)` | 程度+转折 (= full−neg, LOO) | `{dict}_score_degadv{track}` | **新增** |
| (none) | `(T,T,T)` | 全规则 | `{dict}_score{track}` | 已有 (主列) |

→ **新增 6 个 article 变体** (negonly 折入单一事实源 `_RULE_ABLATION_VARIANTS`, 物化字节不变 → golden-safe)。本谱**含**累积梯度 (raw→negonly→negdeg→full)、单规则隔离 (degonly/advonly)、leave-one-out (degadv/negadv/negdeg = full 各减一条)。各变体独立 `Σ|final|` 自归一化 (非可加分解, 见 D5)。

### D3 — 引擎最小改动: 加 `apply_negation`, 只 gate 翻号算术

签名扩为 `(tokens, sentiment_dict, apply_negation=True, apply_degree=True, apply_adversative=True)`。

唯一逻辑改动在翻号处 (L628):
```python
# 现:  if negation_remaining > 0:
# 改:  if negation_remaining > 0 and apply_negation:
```
**`NEGATION_WORDS` 的识别 / `continue` / 窗口递减 (L663-664) 一律不动** — 与 2026-06-13 negonly 修复确立的铁律一致: **共享 detect/continue/decrement 骨架, 只锁数值效应**。对抗验证 single-pass §(i) 确认: "no-negation 变体仍须消费窗口位置", 本设计天然满足 (递减在骨架内、与 flag 无关)。

**默认 `apply_negation=True` → 100% 向后兼容**: 现有 5 处 call site (full L1240 / negonly L1259 / union L1283 / msent_negonly L1358 / idf L1374) 行为**字节不变**。仅 2 个新 call site 传 `apply_negation=False` (L0 raw)。

### D4 — N-call 而非 single-pass (对抗验证裁决: single-pass 可行但脆弱)

对抗验证 single-pass-correctness 裁决 **partial**: 单遍多累加器**可行** (分支路由 flag 无关), 但"等价于 N 次调用"**有条件且脆弱** — 每个变体须独立持有 `degree_multiplier_v` + `total_score_v` + `total_abs_score_v` 寄存器, 等价性依赖"乘子严格正 → 符号不变"这一**未来可能被破坏**的不变量 (若有人加负程度权重就静默 desync)。

**采纳 N-call**: 在 `_analyze_single_article` 内对每个新变体各调一次引擎 (复刻 negonly L1259-1261 模式)。理由: 无条件 by-construction 正确 / 每个 flag 组合自文档化、可独立测试 / 引擎 O(tokens)、在已分词输入上多调几次开销可忽略 (jieba 分词才是热点, 已共享一次)。

> single-pass 仅在 T=19 全量 profiling 证明 tone_words 为热点时才考虑, 且须 gate 在"逐列 byte-equal vs N-call 参考"的测试之后 (本计划不做)。

### D5 — 非可加分解的强制披露 (audit MATH-1)

引擎注释 (L1254 / L565-571) 已记录: `(full − negonly)` **非**可加分解 (各自 self-normalize 分母不同 + 否定×程度交互)。新梯度同此性质。

**强制框架**: 所有中间列文档/codebook/论文必须表述为**独立自归一化的消融变体** (ablation), **非**"某规则的纯贡献"。

- **代码层 (本计划已实现, golden-safe)**: 定性 MATH-1 非可加披露已落 `codebook.py::_RULE_ABLATION_NOTE` (逐 `{d}_{sfx}_tone` 列幂等注入) + 引擎/encode 注释 + 本计划。实测 corr(full,各变体)≈0.990–0.999 / 变号 0.3–1.3% (loughran full, 300 文) 已记录于会话。
- **论文层 (DEFERRED, ex-post, 不在代码 DoD)**: 定量披露三件套 —— (a) 七变体两两 corr 矩阵; (b) 逐变体**变号文章占比** (sign-flip rate, 非仅幅度差); (c) 多重共线性诊断 (VIF, 因 corr≈0.99 高度共线, 严禁同式并入) + 声明规则施加有序含 negation×degree 交互 —— 由论文 onboarding 时以 Stata 附录表实现 (可选 `35_tableAX_rule_ablation_mathdisclosure.do.tmpl`), **非本代码计划交付物**。

---

## 3. 列规格 (精确, 含 32 字符核验)

### 3.1 Article 级 (写入 `22_words_tone.parquet`, 无 Stata 32 约束)

每词典 (6) × 每轨 (`_full`/`_ctx`/`_ss`) × **6 新变体** (raw/degonly/advonly/negdeg/negadv/degadv) = **108 新列** `{dict}_score_{sfx}{track}`。

(无 zscore / idf / msent 衍生 — 严格复刻 negonly 的"裸 score 一列"最小形态。)

### 3.2 Panel 级 (`encode.py` 聚合 → `40_panel_yearly.parquet` + `51_panel_with_controls.parquet`)

每词典 (6) × 每轨 (3) × **6 新变体**, **mean-only** = **108 新列** `{d}_{sfx}_tone{track}` ← `({dict}_score_{sfx}{track}, 'mean')`。

**32 字符核验** (对抗验证 naming-32char, 最长词典 = `jiang_2021`=10 非 loughran):

| panel 列 (最坏 = jiang_2021 + `_full`) | 长度 | ≤32? |
|---|---|---|
| `jiang_2021_raw_tone_full` | 24 | ✅ |
| `jiang_2021_negdeg_tone_full` | 27 | ✅ |
| (假设加 `_std`/`_sum`) `..._full_std` | 28 / 31 | ✅ (但本计划 mean-only, 不加) |

安全余量充足。**mean-only** 决策复刻 negonly (`encode.py:578` 注释: sum/std 后缀贴 32 边界)。`_assert_track_triplet_unique` (stata_export.py:494-532) 自动校验 full/ctx/ss 截断后不撞名 — 本命名短, 必过。

### 3.3 列增量汇总

| 落点 | 新增列数 | golden 受影响 parquet |
|---|---|---|
| `22_words_tone.parquet` | +108 (per-dict article) | ✅ tracked |
| `40_panel_yearly.parquet` | +108 per-dict + **18 跨词典 `dict_avg_{sfx}_tone`** = +126 | ✅ tracked (**当前缺盘**) |
| `51_panel_with_controls.parquet` | +126 | ✅ tracked |

> **跨词典 roll-up (final-audit critic 补)**: `geography.py::compute_composite_indicators` 既有 `dict_avg_negonly_tone` (三点谱 full/negonly/msent)。为镜像 negonly 先例完整性, v3.11.1 扩为全 powerset → 6 新变体各产 `dict_avg_{sfx}_tone{track}` (18 列, ≤26 字符)。codebook `_RULE_ABLATION_RE` 加 `dict_avg` 别名 → 跨词典列得 rule-specific 标签 + MATH-1 披露 (并惠及既有 negonly 跨词典列); stata `_ABL_DICT_REF` 加 `dict_avg='across 6 dicts'` → .dta 标签。

---

## 4. 逐文件改动清单 (PLAN-ONLY, 勿执行)

### F1 — `pipeline/sentiment/tone_words.py` (引擎 + 物化 + 契约)
1. **L529-534 签名**: 加 `apply_negation: bool = True` (置于 `apply_degree` 前)。
2. **L628 翻号**: `if negation_remaining > 0 and apply_negation:`。其余状态机**不动**。
3. **L535-580 docstring**: 补 `apply_negation` 语义 + 重申"骨架共享、仅锁翻号"铁律 + 引 audit MATH-1。
4. **L1259-1261 后 (在 `_analyze_single_article` 内)**: 新增 2 个 call site (复刻 negonly):
   - `_, raw_norm, _, _, _ = _compute_sentiment_with_rules(tokens, sentiment_dict, apply_negation=False, apply_degree=False, apply_adversative=False)` → `result[f'{dict_name}_score_raw'] = round(raw_norm, 4)`
   - `_, nd_norm, _, _, _ = _compute_sentiment_with_rules(tokens, sentiment_dict, apply_negation=True, apply_degree=True, apply_adversative=False)` → `result[f'{dict_name}_score_negdeg'] = round(nd_norm, 4)`
   - 词典缺失分支 (L1229-1237) 补 `_score_raw`/`_score_negdeg = 0.0` (复刻 negonly L1236 语义)。
5. **L1149-1183 `_empty_article_result`**: 每词典补 `result[f'{dict_name}_score_raw'] = float('nan')` / `..._score_negdeg = float('nan')` (空文本 NaN 契约, 复刻 negonly L1168; 轨后缀由 `_dual_analyze` 追加, 此处**不**带后缀)。
6. **L1484-1507 `classify_batch` 列提取**: 在 negonly 提取块 (L1504-1507) 旁加 `_score_raw{track}` / `_score_negdeg{track}` 提取 (`r.get(k, float('nan'))`)。
7. **模块顶部 docstring L78「输出列」**: 追加两新变体说明。
8. **`compute_lexical_complexity` / IDF / clarity 路径**: **不动** (正交, 不入梯度)。

### F2 — `pipeline/panel/encode.py` (聚合)
- **L569-580 negonly 块**旁, 新增两 `for d in DICT_NAMES` × `for track` 循环 (mean-only):
  - `agg[f'{d}_raw_tone{track}'] = (f'{d}_score_raw{track}', 'mean')`
  - `agg[f'{d}_negdeg_tone{track}'] = (f'{d}_score_negdeg{track}', 'mean')`
- `valid_agg` (L1144-1161) 自动 graceful-skip 缺列 → **legacy parquet 向后兼容, 无需门控**。
- **不改 `msent`/`avg_msent` 块** (D1: 计数口径已完备)。
- **不动 runner.py 加权/分歧循环** (L593/639/704/769/836/856…): 新变体是纯 article→bank-year mean 稳健性列, **无 `_w`/`_hw`/`_mw` 加权孪生** (复刻 negonly: negonly 亦只有 `_negonly_tone` mean, 无加权)。

### F3 — `pipeline/panel/stata_export.py` (.dta 标签, 主载荷路径)
- **L271-317 negonly 标签块**旁, 显式补 **36 条** `HEURISTIC_LABELS` 键 (per dict × track × 2 变体)。模式:
  - `'{dict}_raw_tone_{track}': "Avg Tone {DictRef} (raw, no-rule baseline) {track}-track"`
  - `'{dict}_negdeg_tone_{track}': "Avg Tone {DictRef} (negation+degree, no-adversative) {track}-track"`
- 约束: ASCII 英文, ≤80 UTF-8 字节 (test_variable_label_length_under_80), 规则语义写进标签文本 (避免 codebook `_infer_label` 回退泛型标签)。
- **`_infer_label` (codebook.py:1580-1627)** 是缺标签时的兜底; 不补 HEURISTIC_LABELS 则新列得泛型 "Sentiment Tone" 标签 → 故必补。

### F4 — `pipeline/panel/export.py` (parquet 路径标签, 可选)
- L501-506 negonly 在此仅有 `dict_avg_negonly_*`/`avg_msent_negonly_*` 跨词典聚合名 (非 per-dict)。本计划新列为 per-dict → **主标签落 F3**。`export.py` STATA_LABELS 为 stage-40 parquet-only 路径, 可选补 (不补不破 `test_heuristic_labels_match_export_stata_labels` — 该测试只校验固定 8 个 A1/A3 列, 不含本族)。
- 决策: **不改 export.py** (除非用户要 parquet 侧也带标签), 降 churn。

### F5 — `pipeline/panel/codebook.py` (可选 VariableMetadata 策展)
- 可选: 为 36 新列补 curated `VariableMetadata` (category=`Sentiment-Rule-Ablation`, track, notes 引 MATH-1 非可加披露), 优先级高于 HEURISTIC_LABELS。
- 不补则走 F3 的 HEURISTIC_LABELS (已足够)。`is_core` 已于 2026-06-21 整体退役 → 无核心/辅助分流负担。

### F6 — 测试 (见 §6 矩阵)
新增/扩展 `test_22_tone_words.py` / `test_omni_fix_tonewords.py` (article 正确性) + golden 重生后 `test_panel_reproducibility.py` 自动覆盖。

### F7 — `config/sentiment.yaml`
- **无新 key** (house style: 2026-06-13 起全 always-on, 无 enabled flag; 新列无条件产出)。可加文档注释说明梯度复用既有 `degree_words`/`negation_window`/`adversative_boost`。

### F8 — 文档 / 版本
- `CLAUDE.md` 顶部 changelog 加一条 (列增量 +36 panel; 计数不变: STAGES_MAIN=16 / VALIDATION=16 / shim=35 / OUTPUT_REGISTRY 不变 — **纯列内扩展, 无阶段增删**)。
- 版本: 建议 `v3.11.1` (additive 列扩展) 或并入当前 v3.11.0 changelog (用户定)。
- **OUTPUT_REGISTRY (`core/schemas.py`) 不改** (无新 parquet, 列就地加在既有文件)。

### 涉及但**明确不改**的文件 (铁律)
- `validation/radius_sensitivity.py:213` / `validation/decay_sensitivity.py` 的**引擎副本**: 刻意发散 (无 ablation 参数、4-tuple 返回), 设计如此, **scope OUT** (config-validation-twin 确认: negonly 当年也未下放到 twin)。如未来要 twin 梯度, 另起 phase。
- `pipeline/panel/encode_collab.py`: 不引用 DICT_NAMES score 列 (cell_id 分层基于 locus/subst/collab), **无同步负担**。
- `runner.py` 加权/分歧循环: 见 F2 说明, 不动。

---

## 5. Golden / 确定性 / 受控重生 (核心门禁)

> **§5.0 盘面实况修正 (2026-06-21 实测)**: 计划原设"外科注入 committed `40_panel_yearly.parquet`",
> 但**该文件当前缺盘** (仅 `51_panel_with_controls.parquet` + `46_*.dta` 在盘; repro gate 已对
> `40_panel`/`40_article_bank_level` soft-skip)。⇒ 闭环**不是**外科注入, 而是**全 panel 重建**
> (stage 22 → encode/runner 40_panel → 45/46 → 51, multi-hour, 写共享 disk)。利好: ① repro gate
> 实测对 **on-disk 22/51 PASS** → 证并行未提交改动 golden-safe (未改 panel 列值); ② stage 22 / 聚合
> 确定性 ($0, 非 BLAS)。⚠ 须在 **canonical env (§5.3) + 无并行 writer** 下跑, 否则风险: 写盘撞并行
> 会话 + 全重建触 ~45 BLAS 列须钉线程。**故 golden 重生留用户确认盘面无并行写后执行** (见 §11-2)。

### 5.1 golden 必重生 — 无规避 (对抗验证 golden-impact: **confirmed**)
- `golden_panel_v0.json` (schema_version 3) 按 **parquet 文件名**键控, 存 `columns_order` + 逐列 `pd.util.hash_pandas_object` 哈希。
- `test_panel_reproducibility.py::test_column_hashes_match_golden` 对 `22_words_tone` / `40_panel` / `51_panel` 三者**强制列集相等** (extra ∧ missing 皆须空) + 逐列哈希。
- ⛔ **"只加 article 列以躲 golden" 不成立**: `22_words_tone.parquet` 本身 golden-tracked, 列集 gate 一样红。**36 新列 (article) + 36 (40) + 36 (51) 必须进 golden。**

### 5.2 stage 22 确定性 — 利好 (determinism-regen-gate)
- tone_words 纯 CPU + frozenset + `jieba==0.42.1` + `PYTHONHASHSEED=0` (core/stage.py:209 子进程强制) → **新列 byte-deterministic**。
- panel 聚合 = pandas group-mean, **无 BLAS** → 不牵入 4 个网络中心度 / ~45 个 LDA/嵌入 BLAS 敏感列。新列本身洁净。

### 5.3 受控重生 SOP — 外科注入法 (复刻 loughran-exc-cols-fix 2026-06-20 先例)
**canonical env (shell 启动前 pre-export, 早于 numpy import)**:
```
PYTHONHASHSEED=0  MKL_NUM_THREADS=1  OMP_NUM_THREADS=1  OPENBLAS_NUM_THREADS=1
NUMEXPR_NUM_THREADS=1  KMP_DUPLICATE_LIB_OK=TRUE  NEWS_PROCESS_LLM_OFFLINE=1
```
步骤 (本机 T=2 可闭环, 同 loughran-exc-cols — 因新列确定性、非 BLAS):
1. 离线跑 **stage 22** (stage 21 缓存 10125/10125 命中, $0) → 产含 36 新 article 列的 `22_words_tone.parquet`。
2. **validation gate**: 重算既有 negonly 列, 与 committed 0 失配 → 证注入忠实。
3. 隔离算 36 新 panel 列, **纯注入** committed `40_panel_yearly.parquet` (不全跑 stage 25/26 → 避 BLAS 漂移)。
4. 确定性再导出 `46`/`51` (40_panel 幂等再导出)。
5. `generate_golden_snapshot.py` **外科只改** `22`/`40`/`51` 三 entry 的新列哈希, 其余 byte-identical。
6. `pytest tests/integration/test_panel_reproducibility.py` 全绿。

### 5.4 生产 T=19 (标准 DEFERRED)
本机 T=2 (172 行) 闭环可保门禁绿、可提交 (同近期所有特征)。生产 T=19 (18.2M 行) 最终 bless = 受 **M0 gate** 的常设 deferred, 须 canonical env + 用户批准 (见 memory `golden-regen-omp-determinism-2026-06-18`)。

> ⚠ 铁律 G1: golden 重生**不在本计划自动执行**。须用户显式批准 + canonical env 已 pre-export, 否则会误 bless 4 网络列 / 45 BLAS 列的无关漂移。

---

## 6. 测试矩阵

| 测试 | 当前断言 | 本计划影响 | 动作 |
|---|---|---|---|
| `test_22_tone_words.py` | article 指标动态计算 | — | **新增**用例: L0≤L1≤? 无序但应满足 `score_raw` 无规则、`score_negdeg` 介于 negonly 与 full 之间的方向性 + 退化样例 (无否定词时 raw==negonly; 无程度/转折词时 negdeg==full) |
| `test_omni_fix_tonewords.py` | union/口径 (无硬列集) | 无破坏 | **新增**用例验证 `msent` 口径**未**新增列 (D1 退化断言) |
| `test_panel_reproducibility.py` | 列集相等 + 哈希 | **会红** | golden 重生后转绿 (§5.3) |
| `test_dag_consistency.py` | MAIN=16/VAL=16 | 无 (纯列扩) | 不动 |
| `test_v3_2_panel_columns.py` | `n_cols ≥ 1400` | 计数↑仍 ≫1400 | 不动 (可顺手上调下界) |
| `test_stata_export.py` | 列名 ≤32 / 标签 ≤80B (泛型 loop) | 自动覆盖新列 | 须保证 §3.2 命名 + §F3 标签合规 |
| `test_stata_export_v3_5_1.py` | 固定 8 列 HEURISTIC↔export 一致 | 不含本族 | 不动 |

新增**可判别回归**: `test_rule_ablation_ladder_columns_present` (article + panel 36+36 列存在) + `test_msent_count_ladder_not_extended` (D1)。

---

## 7. 执行顺序 (批准后)

```
0. 创建 worktree (主树 chore/renumber-nn-stages 有并行脏改动, 隔离防 clobber)
1. F1 引擎 + 物化 + 契约 (apply_negation gate / 2 call site / _empty / 提取)
2. F2 encode 聚合 (2 循环)
3. F3 stata_export 36 标签  [+ F5 可选 codebook 策展]
4. F6 测试 (article 正确性 + 退化断言 + 列存在回归)
5. ruff check --fix  +  pytest -m fast  +  targeted (test_22 / test_omni_fix_tonewords / test_stata_export)
6. [GATED] §5.3 外科注入受控重生 golden (canonical env, 用户批准)
7. pytest tests/integration/ (repro + dag_consistency 全绿)
8. F8 文档 / 版本 / CLAUDE.md changelog
9. by-name 暂存提交 (排除并行脏文件), 不 git add -A
```

---

## 8. 验收标准 (DoD)
- [ ] 引擎 `apply_negation` 默认 True → 现有 5 call site 行为 byte 不变 (回归锁)。
- [ ] 36 article + 36 panel 新列按 §3 命名落盘, 全 ≤32 字符。
- [ ] 退化不变量成立: 无否定词文 `raw==negonly`; 无程度且无转折文 `negdeg==full`; `msent` 族未增列。
- [ ] 全 36 panel 列有 curated ≤80B 标签 (非泛型回退)。
- [ ] golden 重生后 `test_panel_reproducibility` 全绿; 既有列哈希**零漂移** (外科注入证忠实)。
- [ ] `ruff` clean; targeted + fast 测试 0 fail; dag_consistency 计数不变。
- [ ] 文档披露 MATH-1 非可加性 (codebook + changelog)。

---

## 9. 风险与铁律
- **G0**: `negonly`/`msent_negonly` 命名正确, 严禁改名 (§1)。新基线用 `_raw`。
- **G1**: golden 重生须用户批准 + canonical env pre-export (§5.4)。
- **MATH-1**: 中间列 = 独立自归一化消融, 非可加分解、非"规则纯贡献"; 强制披露 (D5)。
- **铁律**: full×ctx×ss 三轨禁混进同一 over-identified Hansen J (项目既有红线; 本梯度若进 IV 同此约束)。
- **scope**: 不动 validation twins / encode_collab / runner 加权循环 / IDF / msent 族 (§4)。
- **并行**: 主树有并行未提交改动 ([[allv-all-vintage-anchor-companion-2026-06-21]] 等); 用 worktree + by-name add, 防 clobber。
- **数据安全**: 审计/重生子代理**禁** exec producer 误写 `data/processed` (memory 多次教训: 曾污染 40_panel)。

---

## 10. 明确不做 (Out of Scope)
- 不新增 `msent_*` / `avg_msent_*` 列 (D1 退化)。
- 不做 single-pass 引擎重构 (D4; 除非 T=19 profiling 证热点)。
- 不做 IDF / zscore / 加权 (`_w`) 梯度孪生 (复刻 negonly 最小形态)。
- 不改 validation 引擎副本、不动 stage 计数。
- 不在本计划执行 golden 重生 / 生产 T=19 跑 (PLAN-ONLY)。

---

## 11. 决策 (用户 2026-06-21 拍板) 与执行状态
1. **梯度范围 = 全部** (full powerset, 6 新变体 + negonly 折入)。✅ 已实现。
2. **golden = 立即闭环** (用户批准全重建)。⛔ **执行中止 — 撞跨会话 golden 债 (2026-06-21 实测)**:
   - **stage 22 重建成功** (canonical env, 108 新 article 列, msent 未扩展, 验证通过)。
   - **stage 40 panel 重建失败**: ① 我的 108 列需 `22→24→40` 链 (盘上 `24_herd_decay` 陈旧 → 聚合
     "因源列缺失跳过 (108)"); ② strategic_diff `_allv` (并行会话 `a38e5f6b` 合入) 嵌入**真实缓存未命中** →
     须**付费 embedding API**; ③ **committed golden 比本分支陈旧** (无 `_allv`/`inject-fintech` 重生,
     二者 golden 各自 DEFERRED) → 任何全重建会把**三项待重生 (_allv + inject-fintech + 我的消融) 混入
     一次 bless**, 污染他会话 deferred 工作。
   - **已洁净回滚**: 还原 backup 22 → repro gate 复绿 (40_panel 本就 soft-skip); **golden 全程未改**
     (从未跑 generate_golden_snapshot); config/40_attn 等无 golden 足迹。备份留 `data/_regen_backup_ablation_20260621/`,
     drift 校验脚本 `scripts/audit/_regen_ablation/diff_golden.py` 备用。
   - **建议**: golden 重生**并入用户"统一处理"消费** (用户已选 commit 统一处理) — 届时 `_allv`+`inject-fintech`+
     消融三项**一次合并重生** (付费 embedding 只跑一次), 而非我此刻孤立外科 (会与统一消费冲突/冗余)。
     备选: 若要孤立 bless, 走外科注入 (rebuild 24 + 关 _allv + 抽 108 + graft backup_51 + 外科 golden)。
3. **版本 = v3.11.1** 独立 changelog。⏳ CLAUDE.md 顶部待加条目 (该文件被并行会话改脏, 留合并时落)。
4. **标签 = 完整** (stata_export HEURISTIC_LABELS 108 条 + codebook _infer_label/描述/source-stage + MATH-1 备注)。✅ 已实现。

### 已完成 (本会话)
- 引擎 `apply_negation` + 单一事实源 `_RULE_ABLATION_VARIANTS`/`RULE_ABLATION_SUFFIXES` (negonly 折入, 字节不变)。
- `_analyze_single_article` / `_empty_article_result` / `classify_batch` 三处全 powerset 物化。
- `encode.py` panel 聚合 (108 panel 列, mean-only, 32 字符安全)。
- `stata_export.py` 108 标签程序化生成 (≤80 字节) + `codebook.py` 完整策展 (rule-specific 标签/描述/source-stage + MATH-1 披露)。
- `tests/test_rule_ablation_ladder.py` (变体谱/跨模块同步/apply_negation/退化/article→panel/标签/codebook)。
- 门禁: 90+ 定向测试绿 · ruff clean · dag_consistency 计数不变 · repro gate 绿 (with pre-existing skips)。

### 待执行 (gated)
- golden 全重建 + 外科 re-key (§5.0/§5.3, 待 §11-2 确认)。
- CLAUDE.md v3.11.1 changelog (待并行 CLAUDE.md 合并)。
- 提交 (worktree 外科分离并行脏 hunk — encode/stata_export/codebook/export 缠并行未提交改动)。
