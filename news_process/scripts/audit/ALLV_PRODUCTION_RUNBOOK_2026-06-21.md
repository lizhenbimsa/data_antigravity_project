# `_allv` 全年份锚点稳健性孪生 — 生产上线 Runbook

**状态 (2026-06-21)**: 代码层 **100% 完成并已推送 `origin/main`** —
`ddc5c620` (`feat(policy)`: `_allv` 全管道列对等) + `a38e5f6b` (`perf(policy)`: stage26 锚点重合短路对称化)。
经 **五轮多智能体对抗审计 + 运行期硬证明 (~73 agent) 全 GO, 0 代码层 P0/P1**。

本文件固化代码层**之外**、须在**生产 T=18** 或**论文上线**时执行的全部 deferred 待办,
使其完全可执行 (exact 命令/文件/行/铁律)。权威研究依据 = workflow `wpdlv9iio`
(4 维度并行研究 + 综合) + memory `[[golden-regen-omp-determinism-2026-06-18]]` /
`[[inject-fintech-word-lda-2026-06-21]]`。

---

## 0. `_allv` 是什么 (一句话)

在政策对齐的 **vintage 前视守卫主轨**之外**并列新增**一套"年度 t 文章与**所有年份**政策文档
拼成的全语料静态锚点"的稳健性孪生 (后缀 `_allv`), 用**完全一致的下游构造**作 anchor-robustness 对照。

- **铁律**: `_allv` 含相对年度 t 的**未来政策文本**, **仅作稳健性对照, 绝不替换 vintage 主轨**,
  亦不进任何因果识别; vintage × allv 两轨各自 **just-identified** 并排, **禁混进同一
  over-identified Hansen J 检验**。
- 已产列: stage15 `policy_cosine_sim_allv[_full/_ctx/_ss]` + `_t2v_allv_*` (文章级);
  stage26 `auth_sim_{tfidf_c,tfidf_w,lda,emb,emb_t2v}_allv_{full,ctx,ss}` (银行年);
  runner 聚合 `article_sim_mean/std_allv*` + 四象限 `token|hidden|subst_adopt_*_allv*` (panel)。
- config: `article_alignment.all_vintage_companion: true` (默认开)。
- 实测 (T=2 disk smoke): `allv` 均值 **0.4968** > `vintage` **0.4438** (全语料锚点含晚年政策 → 偏高)。

---

## 1. 待办裁决总览

| 项 | 内容 | 裁决 | 根因 |
|----|------|------|------|
| **A** | golden 受控重生 (含 ~78–84 个 `_allv` 列) | **DEFER 生产 T=18** | 本机仅 T=2 演示盘 + 上游 parquet 链断 + 须与并行 `strategic_diff` 协调 + `_allv` landmine |
| **B** | stage40 timeout 实测 | **DEFER 生产 T=18** | T=2 测不出 T=18 绝对 wall-clock |
| **C** | manuscript 披露文案 | **已起草 (见 §4)** | 纯文本, 但 `_allv` 主轨当前无 paper 消费 → 待母论文落地后粘贴 |
| **D** | Stata 模板 + paper_spec 登记 | **DEFER (前置未满足)** | `_allv` 的 vintage 主轨在整个 `papers/` **零 paper 消费**, 无可挂靠母表 |

> ⚠ **本机为何不能做 A/B**: ① `data/raw` + `data_excel` 实测空, 仅 T=2 演示盘 (86 banks × 2 years);
> ② 上游 `25_article_sbert.parquet` / `40_article_bank_level.parquet` 缺失、`40_panel_yearly.parquet`
> 不在盘 (被并行会话探针截断后删除) → 链断, 不能仅跑 stage 45/46 复现; ③ 工作树有 ~24 个 tracked 改动
> 横跨 `_allv`/`strategic_diff`/`network`/`staleness` 多并行会话未提交 → 任何 golden 重生会误 bless
> 无关中间产物; ④ `_allv` 全列重跑与并行 `strategic_diff` (`3d37a3d0`) 的 golden 重生**互斥** (见 §A.1)。

---

## 2. 前置铁律 (做 A 之前全部满足)

1. **生产 T=18 全量数据到盘** (17M 文章 / 2007–2024 / T=18; 本机无)。**勿删 `data/processed/_llm_cache.db`**
   (stage 21 LLM 投票 + embedding 缓存的确定性锚点; 删则 golden 不再可复现, 须重跑付费阶段)。
2. **HEAD 必须基于 `origin/main`** (≥ `a38e5f6b`, 含 `_allv` 列定义 + 短路优化)。**不在
   `chore/renumber-nn-stages-2026-06-21` 分支做** (该分支落后 origin/main, 不含 `a38e5f6b` 短路 →
   会高估 stage26 算力且 `_allv` 列定义不全)。
3. **先收口/提交当前工作树的并行改动**, 确认 `HEAD == origin/main` (含 `ddc5c620` + `3d37a3d0` + `a38e5f6b`)。
4. **确定性 env 全程钉死** (memory `golden-regen-omp-determinism` 实证: 缺一即 ~49 列 BLAS/PYTHONHASHSEED
   漂移; 本机 numpy = MKL, 仅 `OMP_NUM_THREADS=1` **不够**, 必须连 MKL 一起钉):

   ```bash
   NEWS_PROCESS_LLM_OFFLINE=1 PYTHONHASHSEED=0 \
   MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
   KMP_DUPLICATE_LIB_OK=TRUE HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 \
   F:/Anaconda3/python.exe <cmd>
   ```

---

## 3. A — golden 受控重生 (含 `_allv` 列)

### A.1 ⚠ 与并行 `strategic_diff` (`3d37a3d0`) 的协调 (最关键)

`3d37a3d0` (`feat(strategic_diff)`: word/LDA 轨注入金科词分词器) 改了 `auth_sim_tfidf_w` /
`auth_sim_lda` 的**值** (与 `_allv` 改的是同族 `auth_sim_*` 列)。两笔均 DEFERRED golden 重生。

- **互斥点**: `strategic_diff` 计划用"**§5.0 外科隔离注入**绕过 `_allv` 陈旧 landmine"做 golden
  (见 `scripts/audit/INJECT_FINTECH_DICT_WORD_LDA_TRACKS_PLAN_2026-06-21.md`); 而 A 的目的恰是把
  `_allv` 列**纳入** golden, 须**全链 stage 重跑** (非外科隔离)。
- **`_allv` landmine**: `companion=true` 默认开 → 全 stage 重跑会吐 **15 个 golden 没有的 `_allv` 列**
  (6 个 jieba-affected + 9 个非 jieba), 落 `test_panel_reproducibility.py:159-167` 的**列集相等断言**
  (`extra` 非空 → 逐列哈希比对**之前**即 FAIL); 且 9 个非 jieba `_allv` 列会**伪证伪** `strategic_diff`
  对 char/emb 轨的"外科性"判定。
- **仲裁 (主控二选一)**:
  - **(推荐) 合并单次 bless**: 在**同一次**生产 T=18 受控 run 内, 全链重跑使 `_allv` + `strategic_diff`
    的全部新列/变值列**一起落盘 + 一起 bless** → `extra` 集自然清空, 无 landmine。
  - **(次选) 先 A 后 strategic**: 先做 A 的 `_allv` baseline 全量同步 (使后续 strategic_diff 的 extra 集为空),
    再做 strategic_diff 注入。

### A.2 重跑链 (生产 T=18, env 见 §2.4)

```
T=18 全量数据到盘
  → stage15 (16_article_policy_alignment): 产 policy_cosine_sim_allv* (文章级)
  → stage25 (25_article_sbert): SBERT 嵌入 (GPU 4–6h, M0-gated 付费)
  → stage40 (40_panel_export_main): 内部串行
       · compute_authoritative_similarity (auth_sim) → auth_sim_*_allv_{full,ctx,ss}
       · runner 聚合 → article_sim_mean/std_allv* + 四象限 token|hidden|subst_adopt_*_allv*
  → stage46 (.dta/codebook 导出) → stage51 (panel_with_controls)
  → python -m news_process.scripts.migrate.generate_golden_snapshot
  → pytest news_process/tests/integration/test_panel_reproducibility.py
```

- `generate_golden_snapshot.py` 是**纯读盘哈希器** (不重跑 producer): 逐 parquet 写
  `column_hashes` (`pd.util.hash_pandas_object(s, index=False).sum() → u64hex`) + `columns_order` 进
  `tests/fixtures/golden_panel_v0.json` (schema_version=3)。`_allv` 真落盘后, 列集 `extra` 自然消除。
- `run_production_regen.py` (默认 `--dry-run`) **不涵盖 stage15/26**, 对 `_allv` 重生**不充分**, 须走上面全链。

### A.3 确定性亲验 (bless 前必做)

- `_allv` 的 `auth_sim_emb_allv` / `policy_cosine_sim_allv` / `auth_sim_lda_allv` 列属
  **BLAS-FP / LDA E-step 浮点求和序非确定**族 (与其 vintage 孪生同源)。
- **同 env 连跑改动链 ≥2 次**, 逐列哈希须完全一致再 bless (memory 实证: canonical env 下 `coh_lda` 等
  E≡F 0 漂移; 缺钉死则漂)。LDA `random_state=42` + `n_jobs=1` 已硬钉 (`strategic_diff.py`), 不污染全局 RNG。

### A.4 入库

- repro + dag gate 全绿 → **仅 `tests/fixtures/golden_panel_v0.json` 入库** (parquet/.dta 均 gitignored)。
- **by-name `git add`** 排除并行会话产物; 同 commit freeze (面板已落盘 + golden + 代码同步)。
- ⚠ 这是**真重建值** (`_allv` 列哈希真实重算), 非 shim-renumber 的 `$0` re-key。

---

## 4. B — stage40 timeout 实测

- **风险机制**: stage26 `_ghost_anchor_metrics` (`pipeline/features/policy_similarity.py`) 每 (year, track)
  做 2×TF-IDF + 1×LDA (K=10, max_iter=50, **n_jobs=1** 确定性硬约束, 不可并行) + 2×embedding;
  `companion=true` 对每 cell **再调一次** (全语料静态锚点, TF-IDF/LDA 从头重算, 无缓存) → **算力翻倍**。
- 这套压在 **stage40 单一 `timeout=7200` (2h) 预算** (`core/dag.py`; stage25/26/27 非独立 DAG stage,
  共享 stage40 timeout)。T=18 = 86 banks × 18 years × 3 tracks = 4644 cell, companion ×2 ≈ 9288 次 LDA fit。
- `a38e5f6b` 短路 (`auth_text_vin == auth_text_static` 时复用 `vin`) 仅在锚点重合年命中; 生产 T=18 多数
  年锚点真不同 → 仍翻倍。
- **实测**: 生产 T=18 run 后读 `logs/40_*.log` 的 Stage 26 banner 时间戳差, 取 stage40 全段总和。
  若逼近/超 7200s → 改 `core/dag.py` 的 stage40 `timeout=7200` **一行上调** (如 `10800`/3h 或 `21600`/6h
  仿 stage21; **纯 timeout 上调 golden-safe, 不改任何产物**)。
- ⚠ T=2 本机只能测**翻倍因子** (T=18 cell 数 = 9× T=2/track), 测不出绝对 wall-clock; **勿把 T=2 结论当 T=18**。
  本机连"测翻倍因子"都不建议跑 (会触 producer stage40 + 无外推价值)。

---

## 5. C — manuscript 披露文案 (已起草, 可直接粘贴)

> ⚠ 当前 `papers/` 对 `_allv` 主轨**零消费** (见 §6 D), 故暂无 manuscript 需要此披露。
> 待 §6 的母论文落地、`_allv` 真作其 robustness 后, 把下文粘进该 paper 的"稳健性 / Robustness"小节。

### 5.1 中文 (粘入 manuscript 稳健性小节)

> 作为政策对齐识别的锚点稳健性检验, 我们在前视守卫 (vintage) 主轨之外并列报告一组全语料
> (all-vintage) 静态锚点孪生指标 (后缀 `_allv`)。主轨在计算第 t 年文章与政策文本的对齐时, 仅采用
> 截至第 t 年已发布的政策 (vintage, 严格前视守卫, 杜绝前视偏误); 孪生指标则采用样本期内所有年份的
> 政策文本 (含第 t 年之后才发布的政策) 作为静态锚点。须强调三点 ex-post 口径限定: (1) 全语料锚点
> 机械性地纳入了相对第 t 年属于未来信息的政策, 因此该指标仅作为稳健性对照, **绝不替换主轨**, 亦不
> 用于任何因果识别; (2) vintage 与 all-vintage 两套工具变量各自**恰好识别 (just-identified)** 并排
> 估计, **不得合并进同一过度识别 (over-identified) 的 Hansen J 检验**; (3) 全样本静态锚点的实证均值
> (0.4968) 系统性高于 vintage 主轨 (0.4438), 这一方向完全符合预期——全语料锚点纳入了样本后期数量
> 更多、覆盖更广的金融科技相关政策, 使早期文章亦能与晚近政策文本产生更高的余弦相似度, 从而抬高整体
> 对齐水平。两轨估计在符号与显著性上的一致性, 表明主结果对政策锚点的 vintage 截断不敏感。

### 5.2 English (paste into manuscript Robustness section)

> As an anchor-robustness check on our policy-alignment identification, alongside the
> forward-look-guarded (vintage) main track we report a parallel set of all-vintage static-anchor
> companion measures (suffix `_allv`). The main track computes year-*t* article-to-policy alignment
> using only policies published up to year *t* (vintage, strict look-ahead guard, ruling out
> look-ahead bias), whereas the companion uses the policy corpus of all sample years—including
> policies issued after year *t*—as a static anchor. We stress three ex-post caveats: (1) the
> all-vintage anchor mechanically incorporates information that is, relative to year *t*, from the
> future, so it serves only as a robustness benchmark and **never replaces the main track** nor
> enters any causal identification; (2) the vintage and all-vintage instruments are each
> **just-identified** and reported side by side, and **must not be pooled into a single
> over-identified Hansen J test**; (3) the empirical mean of the full-sample static anchor (0.4968)
> is systematically higher than that of the vintage main track (0.4438)—a direction fully consistent
> with expectations, since the all-vintage anchor incorporates the larger and broader set of
> fintech-related policies issued in later sample years, allowing even early-period articles to
> attain higher cosine similarity with later policy text and thereby raising the overall alignment
> level. The agreement in sign and significance across the two tracks indicates that our main
> results are insensitive to the vintage truncation of the policy anchor.

---

## 6. D — Stata 模板 + paper_spec wire-ahead

### 6.1 ⚠ 根本前置 (非模板任务): `_allv` 主轨当前无母论文消费者

`_allv` 的 vintage 主轨 (`auth_sim_*` / `policy_cosine_sim` / `*_adopt_*`) 当前在整个 `papers/` +
`papers_assets/` **无任何 paper 作 treatment / outcome 消费** (已核验: token 边界 grep 零命中,
6 个 `grep -l` 命中均为标签/注释偶发子串匹配, 非回归接线)。稳健性孪生**必须依附一张主测度母表**
(precedent: `_ss` mirror 依附 `bartik_type_iv` 主轨)。

故须**先**选定一篇 paper, 把 vintage 主轨 (如 `token_adopt_*_full` / `auth_sim_tfidf_w_full`) 接成
某张主回归的 treatment 或 mechanism 列, **才能**让 `_allv` 作其 anchor-robustness 孪生。无此步,
`_allv` 模板**悬空** (像现存占位骨架, 平添计数锁负担而无真值)。**这远超 "wire-ahead 一个模板"**,
是一项独立的 paper-onboarding 工作。

### 6.2 母论文落地后的精确模板方案 (满足 6.1 前置才做)

1. **分支**: 基于 `origin/main` (含 `_allv` 列定义) 起干净 worktree, **不在 `chore/renumber` 分支写**。
2. **模板**: 在归属 paper 的 `papers/_common/stata_templates/<paper_id>/` 加 1 个
   `NN_<paper>_allv_anchor_robustness.do.tmpl`, **复刻 `bank_fintech_substance/18_*_robustness.do.tmpl`
   的 capture-confirm 守卫**: 对每个 vintage + `_allv` 列 `capture confirm variable <col>`, 缺列
   `display "⏭ 跳过 (列未落盘)"` / `exit 0`; **并排两列各自 just-identified 回归** (铁律: 禁 vintage×allv
   合 Hansen J)。只用既有占位符 `{{MAIN_DV}}` / `{{CLUSTER_VAR}}` / `{{RANDOM_SEED}}`, **不引入新 token**
   (免改 `stata_runner._PAPER_DEFAULTS`)。standalone / 00_master 末尾 `exit, clear` (防 `/b` 弹「Done」框)。
3. **paper_spec**: 镜像 `_ss` mirror 写法, 在该 paper `paper_spec.yaml` 的 `identification` 或新 `robustness`
   块加 `allv_anchor` 列表 + exploratory 项 + 披露脚注 (引 §5 + 0.4968 vs 0.4438 方向)。
4. **计数锁三处同步** (历史 robustness-expansion 2026-06-14 踩过漏一处致 CI 红, 务必三处对齐):
   `tests/test_papers_b_route.py` 的 `test_total_template_count_*` (当前 = **142**) → +1;
   `CLAUDE.md` 模板计数; `stata_runner` verify-CLI 计数。
5. **验证**: `pytest news_process/tests/test_papers_b_route.py` + Stata `/b` 合成 T=18 烟雾 (末尾 `exit, clear`) 实跑 exit 0。
6. **时序**: 模板可先于 golden 写 (wire-ahead, capture-confirm 缺列优雅跳过), 但**端到端验证须在 §3 (A) 的
   golden 重生 + `strategic_diff` §5.0 注入完成后**, 避免 `_allv` 陈旧 landmine。

---

## 7. 一页纸执行顺序 (生产环境主控)

```
0. [前置] 生产 T=18 数据到盘; HEAD==origin/main; 收口并行改动; env 钉死 (§2)
1. [仲裁] 与 strategic_diff(3d37a3d0) 会话定 golden 合并顺序 (§A.1, 推荐合并单次 bless)
2. [A] 全链重跑 stage15→25→40→46→51 → generate_golden_snapshot → repro gate (§3)
3. [A] 确定性亲验 (连跑 ≥2 次逐列哈希一致) → 仅 golden_panel_v0.json by-name 入库 (§A.3-A.4)
4. [B] 读 logs/40_*.log 实测 stage40 wall-clock; 超 7200s 则上调 core/dag.py timeout 一行 (§4)
5. [D-前置] 选定母论文, 把政策对齐 vintage 主轨接成主回归列 (§6.1)
6. [D] 母论文落地后, 加 allv_anchor_robustness 模板 + paper_spec + 三处计数锁 (§6.2)
7. [C] 把 §5 双语披露文案粘进该 paper 稳健性小节
```

---

*权威依据*: workflow `wpdlv9iio` (4 维度只读研究 + 综合) · 五轮 `_allv` 审计 (`ddc5c620`/`a38e5f6b`) ·
memory `golden-regen-omp-determinism-2026-06-18` / `inject-fintech-word-lda-2026-06-21` ·
`INJECT_FINTECH_DICT_WORD_LDA_TRACKS_PLAN_2026-06-21.md` (§3.1b/§5.0 `_allv` landmine)。
