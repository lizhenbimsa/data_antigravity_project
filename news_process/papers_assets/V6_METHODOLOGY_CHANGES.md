# v6 方法学变更说明（写论文必读）

> 适用于所有论文：bank_fintech_tone / benefit_society / brokerage_network / strategic_diff / llm_peer / 其他基于本项目 panel 数据的论文。
> 锁定时间：2026-05-05
> 与 v5 之前的 panel 不可直接对比；以下四项为根本性方法学变更，**必须**在论文方法章节如实声明。

---

## 1. F1：LLM 三家族真三角验证（取代 v5 单家族 / v3 错位）

**v5 之前的状态**：sentiment.yaml 中 `gpt54nano` / `gemini31111` / `claude4h` 三个 slot 的 model_name 错位（claude4h 实际跑的是 GLM 或 DeepSeek）。

**v3 锁定**：基于 yunwu.ai/v1 实际授权清单，确认三个独立家族可用：

| Slot | model_name | 家族 |
|---|---|---|
| `gpt54nano` | `gpt-5.4-nano` | OpenAI |
| `gemini31111` | `gemini-3.1-flash-lite` | Google |
| `deepseekv4`（原 `claude4h`）| `deepseek-v4-flash` | DeepSeek |

**论文方法章节建议表述**：

> "We employ three independent LLM families for sentiment annotation:
> gpt-5.4-nano (OpenAI), gemini-3.1-flash-lite (Google),
> and deepseek-v4-flash (DeepSeek). OpenAI (gpt-5.4-nano) and Google
> (gemini-3.1-flash-lite) are queried through the yunwu.ai
> OpenAI-compatible aggregator (base_url https://yunwu.ai/v1, YUNWU_API_KEY);
> DeepSeek (deepseek-v4-flash) is queried via its native endpoint
> (base_url https://api.deepseek.com, separate DEEPSEEK_API_KEY).
> All three use the OpenAI-compatible /v1/chat/completions schema with
> temperature=0 and seed=42 for
> deterministic outputs. Inter-family agreement is reported as Cohen's κ
> and Krippendorff's α; majority vote across families produces the final
> sentiment label, with ties marked as `undefined` (not `neutral`)."

---

## 2. F2：篇章级编码契约重写（消除 81.7% 中性标签污染）

**v5 之前的污染**：`verified=False ∩ sentiment="中性"` 行占所有"中性"标签的 81.7%（_full）/ 84.1%（_ctx）。这些"中性"标签实际是 verification 失败时的强制兜底，与真实中性新闻不可区分，导致下游 `is_neutral_*` / `pos_count_*` / `neg_count_*` 全部受污染。

**v3 锁定**：

| 修复点 | 行为 |
|---|---|
| `_aggregate_track`：单模型 verified=False 不再强制改 sentiment | 每个模型独立保留自己的 sentiment 判定 |
| `majority_vote_sentiment`：平局返回 None | 不再降级到"中性"；平局行标记 `llm_undefined=1` |
| `encode_sentiment`：使用 nullable Int8 + 4 类掩码 | `is_neutral` 仅在 verified=True ∧ undefined=0 ∧ call_failure=0 ∧ sentiment="中性" 时为 1 |
| 21 输出新增 10 列元数据 (5 类状态指标 × 2 轨 _full/_ctx)（后于 v3.9.0 / 2026-06-14 新增第三主轨 _ss 银行+金科同句共现 → 元数据实为 5 类状态指标 × 3 轨 _full/_ctx/_ss = 15 列） | `n_valid_votes_*` / `n_verifying_votes_*` / `llm_call_failure_*` / `llm_undefined_*` / `agreement_rate_s_*` |

**论文方法章节建议表述**：

> "Articles where (a) all three LLM families fail to return a valid response
> (`llm_call_failure=1`) or (b) the three sentiment votes split three ways
> with no majority (`llm_undefined=1`) are coded as **missing** rather than
> neutral. Articles where the bank-fintech relevance fails majority verification
> (`llm_verified=False`) likewise have their sentiment treated as missing.
> This is a deliberate departure from prior versions of the panel which
> coerced these to 'neutral' and conflated 81.7% of the neutral labels with
> measurement failure / verification rejection. Under listwise deletion, this
> reclassification removes a non-trivial number of bank-year × track
> observations (track ∈ {full, ctx, ss} (v3.9.0 起 _ss 银行+金科同句轨与 full/ctx 全平价); 标题情感轨已于 remove-title-track 移除)
> from regressions; counts before/after are reported in
> Table A.X (sample composition diagnostics)."

---

## 3. F3：零观测语义全局统一（NaN 主路径）

**v5 之前的混乱**：
- OpenAI-embedding 类相似度（`auth_sim_*` / `benefit_*` / `article_sim_*`）在零观测 bank-year 下被 `fillna(0.0)` 强制归零（错误注释为"零向量数学正交"）。
- text2vec 同概念变量保留 NaN。
- 两路在同一 panel 中产生**不可比样本量**：用 `auth_sim_full` 跑回归用全样本（含填零行），用 `policy_cosine_sim_t2v_full` 跑回归被 listwise 删除。

**v3 锁定（主路径全 NaN）**：

| 列族 | n_articles==0 行 | 新行为 |
|---|---|---|
| `auth_sim_*` (8 列) | NaN | 与 t2v 一致；listwise 删除 |
| `benefit_*` (8 列) | NaN（除真实零向量投影） | 同 |
| `article_sim_*`、`fintech_intensity_mean` | NaN | 同 |
| `token_adopt_*` / `hidden_adopt_*` / `subst_adopt_*` | NaN | 同 |
| `n_articles`、计数类、`_sum` 后缀列 | 0 | 数学合理（无观测=零计数） |

**论文方法章节建议表述**：

> "For bank-years with zero fintech news coverage (`n_articles=0`),
> cosine-similarity-based features (auth_sim_*, benefit_*, article_sim_*),
> ratios (token_adopt_*, hidden_adopt_*, subst_adopt_*), and continuous
> intensity scores (fintech_intensity_mean) are coded as undefined (NaN)
> rather than zero. We follow Allison (2001) and Heckman (1979) in treating
> these as missing-by-design and use listwise deletion in regressions.
> Count and sum-type variables (n_articles, pos_count, *_sum) remain at 0
> as the mathematically correct zero-observation value. The number of
> bank-year × track observations (track ∈ {full, ctx, ss} (v3.9.0 起 _ss
> 银行+金科同句轨与 full/ctx 全平价); 标题情感轨已于
> remove-title-track 移除) dropped is reported in Table A.X."

---

## 4. F4：Bartik IV 修剪（28 类外生性违规 IV 删除）

**v5 之前**：panel 含 ~30 类 Bartik IV，其中 ≥ 28 类违反 Goldsmith-Pinkham et al. (2020, AER) 外生性公理：
- post-treatment 文章特征（doclen / kwdiv / kwden / mden / sentlen / ttr）
- 编辑事后决策（author / page / pgnum / excl / title / mcount）
- 时间切分无因果通道（half / qtr / month / wkday）
- 媒体二分变体冗余（mcentral / mfin / mcomp / mofficial / mmarket / mfreq / mdeep / mdaily）
- 与已保留维度高度相关（mprov / breadth / pubfmt）

**v3 锁定（仅保留 6 类核心）**：

| IV 类 | 列数 (× 3 tracks: _full / _ctx / _ss，v3.9.0 起) | 文献依据 |
|---|---|---|
| `bartik_type_*` | type/scale 已 pre-treatment 固定 | Goldsmith-Pinkham, Sorkin & Swift (2020, AER) |
| `bartik_scale_*` | 同 | 同 |
| `bartik_fintech_lf_*` / `bartik_fintech_lc_*` | LLM 主题分类，须配合论证（v3.2 locus 拆分：lf=innovation_locus_full 基期份额 / lc=innovation_locus_ctx） | 项目内置 |
| `bartik_media_*` | 媒体三方分类 (fin/comp/other) | Snyder & Strömberg (2010, JPE) |
| `bartik_geoprox_*` | 银行注册地 vs 媒体省份 | Engelberg & Parsons (2011, JF) |
| `bartik_mauth_*` | 媒体权威性档位 (high/mid/low) | Holzman, Miller & Twedt (2023, TAR) |

**基期约束**：`bartik_base_year = max(panel.year.min(), 2010)`，强制 `< 2019`（DCEP 沙盒里程碑）。

**panel 列变化**：bartik_* 列从 ~214 列降至约 29 列（6 类核心 × 含 share / iv × 2 tracks（_full / _ctx）（注: v3.9.0/2026-06-14 起新增第三主轨 _ss 银行+金科同句共现，bartik IV 实为 ×3 轨 _full/_ctx/_ss，本节按旧两轨口径，IV 列数应相应上调；remove-title-track 后已无 _title 情感轨）。逐类列数随各类 share 分组数不同：type=8（iv×2 + 6 share）/ scale=6（iv×2 + 4 share）/ fintech=4（iv×2 + 2 share）/ media=4（iv×2 + 2 share）/ geoprox=2（仅 iv×2）/ mauth=5（iv×2 + 3 share），合计 ≈ 29 列。

**强制 Romano-Wolf 校正**：IV ≥ 6 类（按类计数），主表必须使用 step-down p 值（`rwolf` Stata 包）。

**论文方法章节建议表述**：

> "We construct Bartik (shift-share) instrumental variables following
> Goldsmith-Pinkham, Sorkin & Swift (2020, AER) along six exogenous
> dimensions: bank type, bank scale, fintech topic, media-type three-way
> classification, geographic proximity, and media authority tier. Earlier
> versions of this panel included up to 30 IV dimensions; we have removed
> 28 dimensions (article-length, keyword-density, publication-frequency,
> author / page / section, calendar splits, media binary subsets, etc.)
> that violate the share-exogeneity axiom of Goldsmith-Pinkham et al.
> Base year is set to max(panel.year.min(), 2010) and is mechanically
> blocked from exceeding 2019 (the DCEP regulatory sandbox milestone).
> First-stage Kleibergen-Paap rk Wald F and Hansen J statistics are
> reported for each IV; main tables apply Romano-Wolf step-down p-value
> correction (Romano & Wolf 2005) for joint inference across the six
> retained IV families."

---

## 5. 其他次级变更（无需在方法章节单独声明，但项目工程师须知）

| 变更 | 行为 | 文档位置 |
|---|---|---|
| **N4** 并发降级 | `max_concurrency: 300 → 40 (v6/N4)`（后于 2026-05-14 用户决策统一调至 100）+ 指数退避（cap 600s） | `config/sentiment.yaml` |
| **N7** 统一 API key | 新增 `YUNWU_API_KEY`，三 slot 全部引用 | `.env` + `sentiment.yaml` |
| **N8** lineage 元数据 | 每次 stage 21 重跑覆盖写入固定文件名 `21_tone_llms_lineage.json`（只保留最新一次快照；运行时间见文件内 `run_start_iso` 字段） | `data/processed/` |
| Stata 兼容 | export.py / controls.py 内联把 pandas nullable Int*/boolean dtypes 转 Float64（NaN 保留），Stata 端用 `mvdecode` 处理 | `pipeline/panel/export.py`、`pipeline/falsification/controls.py` |

---

## 6. Stata 端必做调整

在所有 .do 文件中：

```stata
* v6/F2: 处理 nullable Int8 转换后的 Stata 缺失值
* 注: 下例仅列 _full/_ctx；v3.9.0/2026-06-14 起须同步加 _ss 轨同名列 (llm_vote_score_ss / n_valid_votes_ss / n_verifying_votes_ss / bartik_*_iv_ss 等)
mvdecode is_positive_full is_negative_full is_neutral_full ///
    llm_vote_score_full llm_vote_score_ctx ///
    n_valid_votes_full n_valid_votes_ctx ///
    n_verifying_votes_full n_verifying_votes_ctx, mv(.)

* v6/F3: 零观测样本的相似度变量已为 NaN，listwise 自然处理
* 不需要额外的 if 条件（Stata 自动跳过）

* v6/F4: 主表使用 6 类 IV + Romano-Wolf 校正
local biv_main "bartik_type_iv_full bartik_scale_iv_full bartik_fintech_lf_iv_full bartik_media_iv_full bartik_geoprox_iv_full bartik_mauth_iv_full"
ivreg2 dep_var (treat = `biv_main') controls i.bank i.year, cluster(bank year) first

rwolf dep_var, indepvars(`biv_main') controls(...) reps(1000) seed(42)
```

---

**生成时间戳：2026-05-05  ~11:15 (UTC+8)**
**对应 git tag：`replan-v5-anchor-pre-audit` → `pre-E1-bundle-v6` → `pre-E2-bundle-v6` → `replan-v6-complete`**
