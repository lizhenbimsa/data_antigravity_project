# semantic_staleness_ss 执行计划 — 关闭 stage 18 语义陈旧度的唯一三轨平价缺口

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 版本: **v1.2** (2026-06-21, 经第二轮 42-agent 顶刊系统审计修订, 见 §13; v1.1 见 §12) · 作者: Claude Opus 4.8 (ultracode) · 状态: **✅ Phase A 已实现并提交 main** (用户 2026-06-21 放行+授权提交; 代码+单测全绿 + ruff clean + 真实端到端微验证 + 四轮审计三重坐实; 见 §14-§17) · **Phase B (生产 T=19 重跑 + golden 重生) 待生产 run**
> 关联: [[third-track-ss-plan-2026-06-14]] · `THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md` (§④/§7.5/line 109/171 DEFER 原决策) · [[golden-regen-omp-determinism-2026-06-18]]
> 触发: 用户 2026-06-21 指令「请参考 ctx 轨实现 ss 轨」(在我建议 DEFER 后明确选择实现)

---

## §0 摘要 / 决策 (TL;DR)

surface_staleness 已产三轨 (`_full`/`_ctx`/`_ss`), semantic_staleness 仅 `_full`/`_ctx`。本计划补 **`semantic_staleness_ss`**, 关闭全项目**唯一**的三轨平价缺口。

**三条必须先入脑的事实** (决定本计划的全部结构):

1. **真正的改动不在 stage 18, 而在 stage 30a。** stage 18 (`article_staleness.py`) 侧只是 3 行镜像 ctx; 其 `aggregate_to_bank_year` 循环**早已预留** `semantic_staleness_ss` (article_staleness.py:383, 缺列即跳过)。瓶颈是**上游 stage 30a** (`article_sbert.py`) 当前只编 `emb_full`/`emb_ctx` 两轨, 未为 `content_ss` 产 `emb_ss`。这正是 surface_ss 当初**零成本**而 semantic_ss 被 DEFER 的根因: surface 的 MinHash 直接吃 `content_ss` 文本 (自带于 stage 18), semantic 必须先有上游嵌入。

2. **金钱成本 $0, 真实成本 = 算力 + 强制 golden 重生。** stage 30a 用**本地** SBERT (`shibing624/text2vec-base-chinese`), 非付费 API。加 `emb_ss` = 多一条全量编码轨 (≈ stage 30a 从 2 轨变 3 轨, +50% 编码时间; 全量 18.2M 文章 GPU 4-6h 量级)。`semantic_staleness_ss` + `semantic_highstale_ss` 是**列 schema 变更** → 必须重生 golden。

3. **零下游消费 (诚实披露)。** 全项目 grep: 11 篇 `paper_spec.yaml`、全部 Stata 模板、`config/*.yaml` 对 `semantic_staleness_*` (含 full/ctx) **零按名引用**。这些是 robustness-only 诊断列 (G-D2.1 互补性)。**实现本列是"平价完整性 / 审稿防御", 非分析刚需** (详见 §3 必要性裁决)。

**决策**: 按用户指令实现, 采用**两阶段交付** (§7.5): **Phase A** 代码层 ($0, 合成单测验证, 向后兼容可独立提交; C2.1/C2.2/C3.0 须原子同 commit) + **Phase B** 生产 T=19 重跑 + golden 受控重生 (延后到生产 run, 受 M0/生产 gate)。

**计数不变** (纯列内扩展, 无阶段增删, 镜像 v3.9.0 三轨先例): STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY 文件数不变 (列就地加在既有 `26_*` parquet)。

---

## §1 背景与现状

### 1.1 当前盘面 (golden v0 实证)

`tests/fixtures/golden_panel_v0.json` 权威登记:

| 产物 | 列数 | staleness 列 |
|---|---|---|
| `26_article_staleness.parquet` (golden:977-1011) | 8 | surface_{full,ctx,**ss**} + semantic_{full,ctx} — **无 semantic_ss** |
| `26_staleness_panel.parquet` (golden:1013-1059) | 12 | surface_{staleness,highstale}_{full,ctx,**ss**} (6) + semantic_{staleness,highstale}_{full,ctx} (4) + target_bank + year — **无 semantic_staleness_ss / semantic_highstale_ss** |

用户前提**完全准确**: semantic 轨现真就只有 full/ctx, 连 NaN 占位都没有 (`aggregate_to_bank_year` 只对 art_df 中已存在的列产出, stage 18 不算 semantic_staleness_ss → 该列在面板里物理不存在)。

### 1.2 原 DEFER 决策 (非疏漏, 是深思熟虑的取舍)

`THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md`:
- line 109: `stage 30a SBERT ss(最贵收益低，可延后)`
- line 171: `semantic_staleness_ss 延后（stage 30a SBERT，低 ROI）：article_staleness.py 须优雅跳过（NaN）直到 30a ss 上线——文档化，勿被审稿读成平价漏洞`

当前代码忠实执行了该决策: `article_sbert.py:297-308` 显式跳过 emb_ss 并 log; `article_staleness.py:22-26,576-580` docstring 标 DEFER; `ctx_materializer.py` 已物化 `content_ss` (输入就绪)。本计划即"30a ss 上线"动作。

### 1.3 数据流 (确认 content_ss 输入就绪)

```
stage 13 ctx_materializer → 14_news_with_ctx.parquet  (含 content_ss 列, v3.9.0 五列三轨物化)
   ↓
stage 30a article_sbert → 25_article_embeddings.parquet  (现 emb_full/emb_ctx;  本计划 +emb_ss)
   ↓
stage 18 article_staleness → 26_article_staleness.parquet + 26_staleness_panel.parquet
   (现 semantic_full/ctx;  本计划 +semantic_staleness_ss / semantic_highstale_ss)
   ↓
runner 8c _merge_optin_feature_panels → 40_panel_yearly  (通用左连接, 不硬编码列名 → 自动流入)
```

`content_ss` 回退语义 (镜像 ctx; prepend 标题 `ctx_materializer.py:296-298`, 回退全文 body `:287-293`, `ss_is_fallback` 旗标 `:318-321`): 无"银行∧金科同句共现" → `content_ss = 全文 body` 且 `ss_is_fallback=True`; `FINTECH_AC=None` (词典缺失) → 全部回退。

**关键推论 (经对抗审计修正 — 原 v1 高估了冗余)**:
- **嵌入层** (成立): 回退行 `content_ss[i] ≡ content_full[i]` (真实文本, 非 NaN) → 同一次 stage 30a run 内 `encode_articles` 对**同一输入文本**确定性前向 → `emb_ss[i] == emb_full[i]` (CPU 逐位; GPU 因 batch 组成不同可能差 ~1e-6, 故测试用 `np.allclose(atol=1e-6)` 而非严格 `==`, 见 C3-T3)。
- **陈旧度层** (⚠ **不**成立, 原 v1 误称 `semantic_staleness_ss ≡ semantic_staleness_full`): `semantic_staleness_ss[i] = max_j cos(emb_ss[i], emb_ss[j])` over 同 7d 日窗 j。即便 `emb_ss[i]≡emb_full[i]`, **参照窗口里的邻居 `emb_ss[j]` 对非回退邻居 j ≠ `emb_full[j]`** → 两轨陈旧度比的是**不同的参照语料**, 故 `semantic_staleness_ss[i] ≠ semantic_staleness_full[i]` (除非该窗内全部邻居也回退)。
- **修正后的语义**: semantic_ss **不是回退行的纯冗余** —— 查询向量虽等于 full, 但被拿来和"ss 语料"(银行+金科同句子集) 比对, 仍带独立信号。唯一退化等价 = **全语料皆回退** 时 `emb_ss ≡ emb_full` 整列 → 两轨陈旧度整列相等 (这正是 C3-T3 的干净可测不变量)。全回退有**两种**触发: ① `FINTECH_AC=None` (词典加载失败); ② FINTECH_AC 已加载但**每篇均无银行∧金科同句** (`ss_is_fallback` 全 True)。

---

## §2 范围与不变量

### 2.1 IN SCOPE
- stage 30a (`article_sbert.py`): 新增 `emb_ss` 编码轨 (镜像 emb_ctx)。
- stage 18 (`article_staleness.py`): 新增 `semantic_staleness_ss` 计算 (镜像 semantic_staleness_ctx)。
- 文档/注释: 把两文件 docstring 的 DEFER 段改为"已产出"。
- 测试: 新增**正向锁** (emb_ss 存在 + semantic_staleness_ss 产出 + 镜像等价性); 翻转任何描述 DEFER 的注释/log。
- golden: 列 schema 变更 → 受控重生 (Phase B)。

### 2.2 OUT OF SCOPE (刻意不做)
- **不改 `core/schemas.py::OUTPUT_REGISTRY`** (只登记文件名, 不固定列; 文件名不变)。
- **不改 `stata_export.py`** (line 615 `core_patterns` 已声明 `semantic_staleness_ss`; 现缺席触发 `assign_core_columns` "schema 漂移监测" WARN, `:666-670`)。⚠ **该 warning 是 pre-existing — 今天每次跑 stage 46 就在打** (615 早已声明、列一直缺席), **非本计划引入**; Phase A 不改变它; Phase B 列产出后它自动消失 + 列被标 `is_core`。Phase A release note 应注明"此 WARN 为既有过渡噪声, 待 Phase B 消除"。
  > ⚠ **2026-06-21 更新 (`CODEBOOK_ALL_CORE_COLUMNS_EXECUTION_PLAN_2026-06-21.md` 已落地, A2+β)**: `core_patterns` / `assign_core_columns` / `STATA_IC_MAX_VARS` / codebook `is_core` 列**已整体退役** (codebook 取消核心/辅助区分)。故本条对它们的依赖**作废**: 不再有 `semantic_staleness_ss` 的缺席 WARN, 也不再有"列被标 is_core"。**这不影响本计划功能目标** —— `semantic_staleness_ss` 仍由 stage 18/30a 照常产出落盘; 上面两句关于 "WARN 自动消失 / 列被标 is_core" 的过渡叙述已作废。`stata_export.py` 仍"不改"(本计划无须为该列改 stata_export)。
- **不改 thin shim** (`25_article_sbert.py` / `26_article_staleness.py` 是 ≤16 行纯转发, 无逻辑)。
- **不动 surface_ss** (已正确产出)。
- **不动 content_ss 物化 / FINTECH 词典 / 回退公理** (stage 13 已就绪)。
- **不接任何 Stata 模板 / paper_spec** (零下游需求; 若未来某篇要用, 再单独接线)。

### 2.3 计数不变量 (commit 前必须 reassert)
STAGES_MAIN=16 · STAGES_VALIDATION=16 · thin shim=35 · 注册=32 · OUTPUT_REGISTRY 文件数不变。
→ 验证: `pytest tests/integration/test_dag_consistency.py` 必须仍绿 (本计划不碰 DAG)。

---

## §3 必要性裁决 (诚实记录, 防未来自我质疑)

用户已拍板实现, 但计划须如实保留权衡 (供 manuscript 披露 + 未来回顾):

### 3.1 反对必要性的事实 (ROI 偏低)
- **零下游消费**: 不仅 `_ss` 无人用, 现有 `semantic_staleness_full/ctx` 也无任何回归/稳健性表按名消费; 纯 G-D2.1 互补性诊断 (article_staleness.py:614)。
- **构念边际信息小**: `content_ss` 是"银行+金科同句 ±1 句"**短窗**。文本越短, 字面 (char-3gram MinHash) 与语义 (SBERT cosine) 越收敛 → semantic_ss 相对**已免费的 surface_staleness_ss** 的增量, 比 full/ctx 更小。
- **短窗本身的边际**: 实测 disk 1170 篇零共现 14.27% / ctx↔ss 主题漂移 65.76%。回退行 (零共现) 的查询向量 emb_ss[i]≡emb_full[i], **但参照窗口仍是 ss 语料** (§1.3 修正) → 非纯冗余, 仅"查询端退化"; 真正信号增量受限来自短窗下 surface↔semantic 收敛, 而非回退冗余。(原 v1 把回退说成"纯冗余"已按 §1.3 修正。)

### 3.2 支持实现的理由 (用户采纳)
- **平价完整性 / 审稿防御**: 项目强承诺"全平价三轨"; semantic 是唯一不完整的第三轨。补齐后**消除对审稿人的 by-design 披露负担** (line 171 的"勿被审稿读成平价漏洞"从此不需要)。
- **搭车边际成本最低**: 若生产 T=19 全量重跑 + golden 重生本就要发生 (CLAUDE.md: 盘面仍 T=2, 生产跑未发生), 则加 emb_ss 是同一 job 内的廉价 rider。
- **对称性即正确性**: 三轨完全对称的代码比"两轨半"更易维护、更难出 silent bug (维护性收益)。

### 3.3 裁决
**实现, 但 manuscript/codebook 须如实披露**: ①semantic_ss 是平价扩展 (非独立分析需求); ②回退行 semantic_ss≡semantic_full; ③短窗下 semantic_ss 与 surface_ss 可能高度相关 (附录报 corr)。

---

## §4 改动清单 (逐文件, 字节级)

### C1 — `pipeline/text/article_sbert.py` (stage 30a, 核心改动)

**C1.1** `encode_articles` — 无需改 (content-agnostic, 换 content_col 即可)。

**C1.2** `_build_output_frame` 签名加 `embs_ss` 参数 + 输出加 `emb_ss` 列 (镜像 emb_ctx):
```python
# 现 (202-204):
def _build_output_frame(
    df: pd.DataFrame, embs_full: np.ndarray, embs_ctx: np.ndarray,
) -> pd.DataFrame:
# 改为:
def _build_output_frame(
    df: pd.DataFrame, embs_full: np.ndarray, embs_ctx: np.ndarray,
    embs_ss: np.ndarray | None = None,
) -> pd.DataFrame:
```
```python
# 现 (223-224):
        'emb_full': list(embs_full),   # list of 1D arrays (parquet-compatible)
        'emb_ctx': list(embs_ctx),
# 之后插入 (embs_ss is None 时不写该列, 保持旧 schema 向后兼容; 见 R1):
        **({'emb_ss': list(embs_ss)} if embs_ss is not None else {}),
```

**C1.3** `main()` — 加 emb_ss 编码 (镜像 291-295 的 emb_ctx 块), **删** 297-308 的 DEFER skip 块:
```python
# 现 (291-295):
    embs_ctx = (
        encode_articles(df, content_col='content_ctx', title_col=None)
        if 'content_ctx' in df.columns
        else np.full_like(embs_full, np.nan)
    )
# 之后插入 (镜像; content_ss 由 stage 13 v3.9.0 恒物化, 缺列才回退 NaN):
    embs_ss = (
        encode_articles(df, content_col='content_ss', title_col=None)
        if 'content_ss' in df.columns
        else None   # 旧 schema 无 content_ss → 不产 emb_ss, 下游优雅降级 (R1)
    )
```
```python
# 删 297-308 整块 ("ss SBERT embedding twin deferred ..." + if content_ss log skip)。
# _build_output_frame 调用 (312) 加 embs_ss:
    out_df = _build_output_frame(df, embs_full, embs_ctx, embs_ss)
```
> **note**: `else None` 分支仅为**后向兼容旧 parquet** —— `content_ss` 自 stage 13 v3.9.0 起**恒物化** (即便零共现也回退全文 body + 置 `ss_is_fallback=True`, `ctx_materializer.py:287-293,318-321`), 故生产 v3.9.0+ 数据**永走** encode 分支; None 分支在标准 14_news_with_ctx.parquet 上不可达。

**C1.4** docstring (23-34, DEFER 文本在 29-31) + banner (240-262) + 结果分析块 (393-398) 把"ss 延后/v1 延后/最贵收益低"改为"ss 已平价产出 emb_ss" (镜像 emb_ctx 的有效率/归一化体检, 加 emb_ss 一段)。**可选硬化**: emb_ss 编码不加 try/except (与 emb_full/emb_ctx 同 — 现有设计对编码失败即 fail-loud, ss 保持对称, 不单独优待)。

### C2 — `pipeline/text/article_staleness.py` (stage 18)

**C2.1** `_load_aligned_embeddings` 返回值加 `embs_ss` (向后兼容: emb_ss 列缺则返 None)。**两处改动 (返回语句 + 签名注解, 缺一不可)**:
```python
# (a) 签名返回类型注解 (现 401):
) -> tuple[np.ndarray, np.ndarray]:
# 改为:
) -> tuple[np.ndarray, np.ndarray, np.ndarray | None]:
```
```python
# (b) 返回语句 (现 471-473):
    embs_full = np.stack(emb_aligned['emb_full'].tolist())
    embs_ctx = np.stack(emb_aligned['emb_ctx'].tolist())
    return embs_full, embs_ctx
# 改为:
    embs_full = np.stack(emb_aligned['emb_full'].tolist())
    embs_ctx = np.stack(emb_aligned['emb_ctx'].tolist())
    # 三轨 ss (2026-06-21): emb_ss 列缺失 (旧 30a 未重跑) → None, 下游优雅跳过
    # semantic_staleness_ss (镜像 DEFER 行为, 不 fail-loud)。形状守卫: emb_ss 存在时
    # np.stack 后行数必 == embs_full (同 emb_aligned reindex 后行序), 不一致即 30a 内部错乱。
    embs_ss = (
        np.stack(emb_aligned['emb_ss'].tolist())
        if 'emb_ss' in emb_aligned.columns else None
    )
    return embs_full, embs_ctx, embs_ss
```
(辅键校验/provenance/fail-loud 逻辑全复用, 不改。)

> ⚠ **[P0 — 对抗审计抓出, 原 v1 漏]** `_load_aligned_embeddings` 改 3-tuple **会破现有测试** (它们按 2-tuple 解包)。**C2.1 + C2.2 + 下方测试更新三者必须同一 commit 原子落地** (Phase A 内不可拆): 单独落 C2.1 会让 `article_staleness.py:584` 与两测试行 `ValueError: too many values to unpack`。

**C2.2** `main()` 解包 + 计算 (镜像 585-590 的 ctx 块):
```python
# 现 (584-590):
        embs_full, embs_ctx = _load_aligned_embeddings(art_df, emb_path)
        art_df['semantic_staleness_full'] = compute_semantic_staleness(art_df, embs_full)
        art_df['semantic_staleness_ctx'] = compute_semantic_staleness(art_df, embs_ctx)
# 改为:
        embs_full, embs_ctx, embs_ss = _load_aligned_embeddings(art_df, emb_path)
        art_df['semantic_staleness_full'] = compute_semantic_staleness(art_df, embs_full)
        art_df['semantic_staleness_ctx'] = compute_semantic_staleness(art_df, embs_ctx)
        # 三轨 ss (2026-06-21, 镜像 ctx): emb_ss 存在 (30a 已上线 ss 轨) 才算;
        # 旧 30a parquet (无 emb_ss) → embs_ss=None → 跳过, 保 DEFER 向后兼容。
        if embs_ss is not None:
            art_df['semantic_staleness_ss'] = compute_semantic_staleness(art_df, embs_ss)
```
> ⚠ **`if embs_ss is not None` 守卫不可删/不可内移**: `compute_semantic_staleness(df, embeddings)` 签名期待 `embeddings: np.ndarray`, **无 None 守卫** —— 传 None 会在内部 `embeddings.shape` / `embeddings[sort_idx]` 处 `AttributeError`/`TypeError` 崩。守卫**必须**在此 call-site (line 204), 而非 compute 内部 (compute 是 full/ctx/ss 三轨共用纯函数, 不该为 ss 特例加 None 分支)。

**C2.3** `aggregate_to_bank_year` (376-390) — **无需改** (循环 380-383 已硬编码 `semantic_staleness_ss` 项, `if stale_col in df.columns` 守卫已就绪)。注: 该项现为**休眠** —— 仅当 C2.2 落地、main() 真把 `semantic_staleness_ss` 写进 art_df 后, 守卫才命中并产出 `semantic_staleness_ss` + `semantic_highstale_ss` (经 `.replace('staleness','highstale')`) 面板列; C2.2 前守卫恒跳过 (= 当前 DEFER 行为)。

**C2.4** 模块 docstring (17-27, 56-62) + main banner (525-526, 575-580) + DEFER 说明 log (671-673) 改为"已产出 semantic_staleness_ss"; G-D2.1 诊断可选扩展报 ss 轨 surface↔semantic corr。

**C2.5** 文本锁约束 (重要): `tests/test_omni_fix_embed.py:6` g-embed-02 锁了 Tetlock 构念披露文本; `tests/test_citation_integrity_2026_06_14.py::test_text_as_data_authorship_correct_in_staleness` (函数 def :57, 受锁字面串在 :58-64) 锁 "Text as data" 第二作者=Kelly。**改 docstring 时勿动这两处受锁字符串** (Gentzkow/Kelly/Taddy + 构念保真披露两点偏离), 否则破文本锁测试。

### C3 — 测试 (1 处**必改** + 新增正向锁)

**C3.0 [P0 必改] 更新 `tests/test_omni_fix_embed.py` 的 2-tuple 解包** (对抗审计抓出):
```python
# :161 现: embs_full, embs_ctx = _load_aligned_embeddings(art_df, str(p))
#     改: embs_full, embs_ctx, _ = _load_aligned_embeddings(art_df, str(p))
# :223 现: embs_full, _ = _load_aligned_embeddings(art_df, str(p))
#     改: embs_full, _, _ = _load_aligned_embeddings(art_df, str(p))
```
(`:228` 的源文本断言 `'_load_aligned_embeddings(art_df, emb_path)' in src` **不受影响** —— C2.2 保留该调用字面, 仍绿。)

**无其它破坏性断言**: 其余引用 staleness 列的测试 (test_omni_fix_runner / test_panel_orphan_merges / test_metric_audit_p0_fixes) 都自造 `surface_staleness_full` stub 测合并/聚合机制, **无固定列集合断言**; 无任何测试断言 semantic_staleness_ss 缺席 (早前子代理称 "test_omni_fix_embed.py:671-673 断言缺席" 是把 `article_staleness.py:671` 的 log 误判为测试 — 已证伪); 无 25_article_embeddings 列数硬断言 (`test_omni_fix_embed.py:224 assert embs_full.shape==(2,3)` 是断返回**数组**形状, 非 parquet 列数, 不受加列影响)。

**C3.1 新增** `tests/test_semantic_staleness_ss.py` (放 `tests/` 根, 非 integration/; 正向锁, 镜像 g-embed 风格, `pytest.importorskip('faiss')`; **全部用合成 mock 嵌入, 不调真 SBERT** → Phase A 即可跑, 不依赖 30a 重跑):
- **T1**: 30a `_build_output_frame(df, full, ctx, ss)` 产出含 `emb_ss` 列; `embs_ss=None` 时**不含**该列 (向后兼容 D3)。
- **T2**: stage 18 `_load_aligned_embeddings` 对含 / 不含 `emb_ss` 列的合成 30a parquet 分别返回 `(full, ctx, ndarray)` / `(full, ctx, None)`。
- **T3 [重设计 — 原 v1 不变量错误]**: 干净等价 = **全语料皆回退** 场景。构造 mock `embs_ss = embs_full.copy()` (模拟 content_ss≡content_full 整列), 断 `np.array_equal(compute_semantic_staleness(df, embs_ss), compute_semantic_staleness(df, embs_full))` (**同一确定性函数 + 同一输入数组 → 输出逐位相等**, 无需 atol; `compute_semantic_staleness` 仅用 Faiss exact IP + stable argsort, **无 BLAS 累积浮点**, 故逐位确定 —— 与 §1.3 的 SBERT GPU **嵌入层** 1e-6 差异是两码事: T3 喂的是同一份 mock 数组, 不经 SBERT)。⚠ **不**测"部分回退行 semantic_ss==semantic_full" (§1.3 已证伪: 参照窗口不同, 该不变量为假)。
- **T3b (可选, 嵌入层)**: 若跑真 SBERT (慢, 标 `slow`), 断同输入文本两轨 `np.allclose(emb_ss_row, emb_full_row, atol=1e-6)` (GPU batch 噪声容差)。
- **T4**: `aggregate_to_bank_year` 在 art_df 含 `semantic_staleness_ss` 时产出 `semantic_staleness_ss` + `semantic_highstale_ss` 面板列 (镜像 surface_ss)。

### C4 — 文档 (CLAUDE.md + codebook)
- **CLAUDE.md**: 顶部 v3.9.0 段 / Disk 状态段把 "semantic_staleness_ss DEFER" 改为 "已平价"; "嵌入轴仅 full/ctx" → "full/ctx/ss 三轨"。
- **codebook.py**: 无 staleness 专属标签行 (现 grep 仅在别的变量描述里提"与 staleness 正交") → semantic_staleness_ss 走自动标签, **可选**补一行 codebook 定义 (低优先, 无人消费)。

---

## §5 关键技术决策

| # | 决策 | 理由 |
|---|---|---|
| D1 | emb_ss 回退语义 = **镜像 ctx, 自动继承 (仅嵌入层等价)** | content_ss 已含回退 (无共现→全文 body, `ctx_materializer.py:287-293`); emb_ss 直接编码该文本, 回退行**嵌入层** emb_ss[i]≡emb_full[i]。⚠ **陈旧度层不等价** (§1.3 修正): 参照窗口邻居的 ss 嵌入 ≠ full 嵌入 → semantic_ss[i]≠semantic_full[i] (除非全语料皆回退)。不需在 30a/18 额外处理回退, 公理在 stage 13 已闭合。 |
| D2 | `title_col=None` (同 full/ctx) | **已核实**: content_ss 由 stage 13 `prepend_title(title, ss_body)` 注入标题恰好一次 (`ctx_materializer.py:298`, 与 ctx `:297` / full `:296` 同型); 传 title_col 会标题×2, 破对称 (article_sbert.py:273-283 同款铁律)。 |
| D3 | **向后兼容 = embs_ss=None 优雅降级** (不 fail-loud) | 旧 30a parquet 无 emb_ss 列时, `_load_aligned_embeddings` 返 None, stage 18 **call-site 守卫** `if embs_ss is not None` 跳过 (compute_semantic_staleness **无** None 守卫, 守卫必须在调用点, 见 R1) → 退回当前 DEFER 行为, 不崩。**避免硬耦合** (stage 18 不强制要求 30a 已重跑)。这是分步交付 (§7.5) 的技术地基。 |
| D4 | emb_ss 全 NaN 不会发生 | 唯一全 NaN 路径 = content_ss 列**整列缺失** (旧 schema) → 走 None 分支跳过, 不传 NaN 给 Faiss。content_ss 存在时即便全回退也是**真实文本** (=content_full)。边角: 个别行 content_ss='' (内容空) → `fillna('')` 后 SBERT 编码空串得**有效归一化向量** (非 NaN, 但退化近零信息), 不破 Faiss; codebook 须注短窗语义陈旧度对空/极短文本的解读边界。 |
| D5 | 25_article_embeddings.parquet 的 golden 不受影响 | golden 对该文件记 `error: unhashable numpy.ndarray` (golden:1061-1063, 嵌入是数组无法哈希) → 加 emb_ss 列不改其 golden 条目。**只有下游 26_* 的 golden 变**。 |

---

## §6 golden 重生策略 (Phase B 核心)

### 6.1 机制 (必须理解, 否则误 bless)
`generate_golden_snapshot.py` **不重跑管道**, 只对 `data/processed/` **当前盘面**的 parquet 逐列哈希 (脚本 docstring:4-9)。
→ **必须先实跑 stage 30a (emb_ss) + stage 18 (semantic_staleness_ss) 落盘, 再跑 snapshot 脚本**。
→ **在 T=2 盘面跑 snapshot 就会把 T=2 误 bless** → 必须在**生产 T=19 语料**上重生。

### 6.2 golden 变更 (列 schema)
| 产物 | 现 → 新 | gate 覆盖 (见 §6.5) |
|---|---|---|
| `26_article_staleness.parquet` | 8 → 9 列 (+`semantic_staleness_ss`) | **无** (不在 parametrize) |
| `26_staleness_panel.parquet` | 12 → 14 列 (+`semantic_staleness_ss`, +`semantic_highstale_ss`; **highstale 由 `aggregate_to_bank_year:387` 的 `.replace('staleness','highstale')` 自动派生**, 一处 stage 18 改动出两列) | **无** (不在 parametrize) |
| `40_panel_yearly` / `51_panel_with_controls` | ⚠ **见 §6.5b** —— 这两个**被** gate parametrize, 但当前 golden **完全不含任何 staleness 列** | 有 (但当前无 staleness) |

### 6.3 确定性 (是否安全 bless)
- semantic_staleness 建于 **Faiss IndexFlatIP (精确内积) + stable argsort** over SBERT 嵌入; SBERT 由 `ensure_torch_determinism()` 钉死 → **逐位可复现**。
- semantic_staleness **不在已知非确定列集** (4 个网络中心度列 bank_eigen/harmonic/cfbetween_cent+clustering 受 PYTHONHASHSEED; ~45 个 LDA/嵌入/strat 列 coh_lda/auth_sim_emb/strat_*/emb_peer_lag1 受 BLAS 线程数 — semantic_staleness 均不在内, 且现有 semantic_full/ctx 已在 golden 且 repro gate 视其为稳定 → semantic_ss 继承同确定性画像)。
- **铁律 (沿用 [[golden-regen-omp-determinism-2026-06-18]])**: 重生须在 canonical pinned env 下跑, 且 **stage 30a (emb_ss 编码) 与 stage 18 (semantic_staleness_ss) 必须同一 OS session、同一 env** (30a 嵌入端的 BLAS 漂移会下传 18): `PYTHONHASHSEED=0` + `MKL_NUM_THREADS=1` + `OMP_NUM_THREADS=1` + `OPENBLAS_NUM_THREADS=1` + `NUMEXPR_NUM_THREADS=1`。⚠ 这些 env **必须在 python 进程启动前于 shell 设好** —— `ensure_torch_determinism()` 在进程内调用, 对 numpy 导入时已锁定的 BLAS 线程状态**追溯无效** (它只钉 torch/random seed)。
- **bless 前必做 2-run A/B 确定性检验**: 对新 `semantic_staleness_ss`/`semantic_highstale_ss` 两列, 同 env 跑两遍 stage 30a→18, 确认列哈希 0 漂移再写 golden。

### 6.4 重生方式
**不可手工注入** (不像 loughran exc_* 那次是确定性媒体异质性重算; semantic_ss 是 SBERT 派生真值, 必须实跑)。走全量受控重跑 (Phase B)。

### 6.5 ⚠ 校验盲区与 repro-gate 行为 (v1.2 经第二轮 42-agent 审计**实测订正** — 原 v1.1 此节有错)

> **v1.1 错误更正**: v1.1 曾称"下游 `26_*` 列哈希**有** golden 校验"。**这是错的** (第二轮审计 + 实读 `test_panel_reproducibility.py:116-135` parametrize 列表证实)。下面是实测后的准确图景。

**§6.5a — `test_panel_reproducibility.py` 的 per-列哈希 gate 覆盖谁 (实读 :116-135)**: parametrize 列表共 **18** 个文件 = `00/11/12/12_full/13/15/21/21_full/22/23/24/30/40_panel_yearly/40_article_bank_level/40_attn_index_{year,province,city}/51_panel_with_controls`。**不含 `26_article_staleness` / `26_staleness_panel` / `25_article_embeddings` / `14` / `16`**。
- → **`26_*` 加 `semantic_staleness_ss`/`highstale_ss` 有 ZERO per-列 gate 覆盖** (即便 golden 26_* 条目过时, 无任何测试比对它们)。验证**只能**靠 C3 合成单测 (T1-T4) + Phase B 2-run A/B。
- → `25_article_embeddings.parquet` 同样无覆盖: 它在 golden 记 `error: unhashable numpy.ndarray` (golden:1061-1063, 嵌入是数组) → `test_panel_reproducibility.py:147-151` 因 `column_hashes` 缺失 `pytest.skip`; **且也不在 parametrize 列表**。**该 error 条目永久** (加 emb_ss 后仍 unhashable, 不因加列改变)。

**§6.5b — staleness 在 gate-checked 面板里的真实状态 (我方独立实读 golden)**: `40_panel_yearly` / `51_panel_with_controls` **被** parametrize, **但当前 golden 里这两文件完全不含任何 staleness 列** (grep golden: `staleness` 仅出现在 `26_*` 条目 977-1059, 40/51 条目零命中)。即 **opt-in 特征 staleness 合并 (`_merge_optin_feature_panels`) 在已 bless 的盘面状态里未体现** (pre-existing: 该合并未反映进 blessed 40_panel)。
- → **本特征对 per-列 repro gate 是 gate-neutral**: 既不经 26_* (不被查), 也不经 40_panel (当前根本无 staleness) 触发 gate 红。**Phase A 与 Phase B (就 staleness 列而言) 都不会让 repro gate 变红。**
- → ⚠ 但若**未来某次生产全量重建**让 staleness 真流入 `40_panel_yearly`/`51`, 那将是一次**大 schema 变更** (surface 3 轨 + semantic full/ctx/ss 一并新增, 非仅 +semantic_ss), 须重生 golden —— 这是 pre-existing 的"合并未接进 blessed 面板"问题, **非本特征引入**, 本计划不负责修。

**§6.5c — `registry-drift` gate (另一个测试, 须注意)**: `test_panel_reproducibility.py:96-113` 断 `golden_stages ⊆ OUTPUT_REGISTRY ∪ orphan`。`26_*` 已在 `OUTPUT_REGISTRY` (schemas.py:59-61) → 加列不触此 gate。✅ 不受影响。

**§6.5d — 可选硬化 (Phase B, 推荐但非阻断)**: 可把 `26_article_staleness.parquet` + `26_staleness_panel.parquet` 追加进 parametrize 列表 (`:135` 前), 让 gate 自此守住 26_* 的 schema。⚠ **三条注意**: ① 须**与 golden 重生同批**做 (否则盘面 26_* 出新列而 golden 旧 → gate 红); ② 可能**顺带暴露 pre-existing 的 26_* disk-vs-golden 漂移** (26_* 此前从未被 gate 查, 当前 disk 是否真 == golden 未知) → 做时要准备处理无关漂移; ③ 因②, 这是**独立的 gate 硬化项, 非本特征的阻断要求** —— 不做也不影响 semantic_ss 正确落地。

---

## §7 成本与执行顺序

### 7.1 成本
- **stage 30a**: +1 全量编码轨 ≈ +50% 编码时间 (线性外推: 2 轨→3 轨; 须实测验证)。本地模型, **金钱 $0**。全量 18.2M: GPU ~+2-3h / CPU ~+4-8h。⚠ **timeout 风险**: 现 `timeout=21600` (6h); 若 2 轨 baseline 已近 4-6h, 3 轨可能逼近/超过 6h → 执行前在 10k 文小样上基准 2 轨 vs 3 轨, 必要时上调 timeout 或并行 emb_ss 编码。
- **存储**: emb_ss 列 ≈ 768×4 byte/篇 × 有效篇数; 全量 ~+若干 GB (含回退行的 emb_ss≡emb_full 冗余存储, 无压缩)。可接受 (对称性代价)。
- **stage 18**: +1 次 compute_semantic_staleness (Faiss FlatIP 滚动窗口, 分钟级)。
- **golden**: snapshot 脚本秒级; 但前置的 30a→18→45→46 生产重跑是大头。
- **stage 21 (LLM)**: **$0 不触碰** (本计划不碰情感轨; emb_ss 与 LLM 投票无关)。

### 7.2 执行顺序 (DAG 依赖)
```
[Phase A — 代码层, $0, 合成单测验证 (不跑真重型阶段)]
1. 改 C1 (article_sbert.py 加 emb_ss) + C2 (article_staleness.py) — C2.1/C2.2/C3.0 原子同 commit
2. 改 C3.1 (新增 test_semantic_staleness_ss.py 合成单测) + C4 文档
3. ruff check . && pytest tests/test_semantic_staleness_ss.py tests/integration/test_dag_consistency.py \
       tests/test_omni_fix_embed.py tests/test_citation_integrity_2026_06_14.py \
       tests/test_omni_fix_runner.py tests/test_panel_orphan_merges.py
   → 全绿 (单测用合成 mock 嵌入, 不需 30a 重跑; 见 C3.1)
4. (可选, 非必须) 若要在真盘面验证: ⚠ data/processed 是 gitignored, **不能 git checkout 还原**
   → 先备份 25_article_embeddings/26_*.parquet (或指向 scratch output_dir 跑), 验完还原备份
   → (本特征对 gate 中性, §6.5/§7.6; 仅当重建让 staleness 流入 40_panel 才会触 gate)

[Phase B — 生产 T=19, 受 M0/生产 gate, 延后]
5. 生产环境 canonical pinned env (§6.3) 全量重跑 stage 30a (emb_ss) → stage 18。
   ⚠ env 须在 shell 启动 python 前设好 (同一 session 贯穿 30a+18), 例:
       export PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 \
              OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1
       python news_process/25_article_sbert.py   # 产 emb_ss
       python news_process/26_article_staleness.py  # 产 semantic_staleness_ss
   (Windows PowerShell: `$env:PYTHONHASHSEED='0'; $env:MKL_NUM_THREADS='1'; ...` 再跑)
6. 重跑 stage 45 (panel 聚合) → stage 46 (stata_export, 重导 codebook; ⚠ codebook is_core 列已于 2026-06-21 退役, 不再"自动标 is_core")
   → 核验: 读 40_panel_yearly.parquet 是否含 semantic_staleness_ss/highstale_ss
     (⚠ 取决于 staleness 合并是否流入 40 — 见 §6.5b: 当前 blessed 态未流入; 若仍未流入, semantic_ss 只落 26_*)
7. 2-run A/B 确定性检验 (§6.3) → 两列 0 漂移
8. python scripts/migrate/generate_golden_snapshot.py
   (8.5 可选硬化: 把 26_* 加进 test_panel_reproducibility parametrize, 见 §6.5d 三条注意)
9. pytest tests/integration/test_panel_reproducibility.py (repro gate 绿)
```

### 7.3 Phase A 可独立提交吗?
**可以** (推荐), 但 **C2.1 + C2.2 + C3.0 必须同一 commit 原子落地** (§C2.1 P0: 拆开会破 import/解包)。Phase A 整体向后兼容 (D3): 提交后在 30a 未重跑前, emb_ss 缺 → semantic_ss 仍缺席 (= 当前行为), **不产生任何算力成本** (30a 不重跑就不编 emb_ss)。**故 Phase A 不存在"stranded 算力成本"** —— 代码休眠零开销, 唯一过渡负担 = §2.2 那条 pre-existing stata_export WARN (本就在打)。**但** commit message 须显式登记 "golden 重生 deferred to Phase B production run" + §7.6 gate 处置。

---

## §7.5 向后兼容 / 分步交付契约

| 场景 | 行为 |
|---|---|
| Phase A 已提交, 盘面 30a **未**重跑 (无 emb_ss) | `_load_aligned_embeddings` 返 embs_ss=None → stage 18 跳过 → semantic_ss 缺席 (= 当前 DEFER 行为, 零回归) |
| Phase A 已提交, 盘面 30a **已**重跑 (有 emb_ss) | semantic_ss 产出于 `26_*` (不被 gate 查, §6.5a); golden 26_* 条目变陈旧但无测试强制; 若 staleness 同时流入 40_panel 则那才触 gate (§6.5b) |
| 老用户重跑旧 30a parquet | emb_ss 列不存在 → 优雅降级, 不崩 (D3) |
| content_ss 列整列缺 (远古 schema) | 30a embs_ss=None → 不产 emb_ss 列 → 18 跳过 (D4) |

### §7.6 Phase A 的 repro-gate 处置 (v1.2 订正 — 见 §6.5)
Phase A **不重跑真重型阶段** (§7.2 走合成单测) → 盘面不变 → `test_panel_reproducibility.py` **Phase A 自然保持绿**。这是首选路径。
- **关键事实更正 (§6.5a/b)**: `26_*` 根本**不在** gate parametrize 列表 → 即便真重跑 30a/18 让 `26_*` 出新列, **per-列 gate 也不会因此红** (26_* 不被查)。会变红的唯一路径是 staleness 流入**被查的** `40_panel_yearly`/`51` —— 而当前 golden 这两文件**零 staleness 列** (§6.5b), 故本特征对 gate **中性**。
- **仅当** 真重跑触发了更广的面板重建 (让 staleness 首次进 40_panel): 此时二选一 ① 从备份还原盘面 parquet (gitignored 不能 git checkout); ② 确为生产重跑则进 Phase B 重生 golden。
- **不建议** 给 gate 加 `@pytest.mark.skip` (掩盖真实漂移); "盘面保持旧态 / 备份还原"更干净。

---

## §8 测试与门禁

| 门禁 | 期望 | 备注 |
|---|---|---|
| `test_dag_consistency.py` | 绿 (16/16 不变) | 本计划不碰 DAG |
| `test_semantic_staleness_ss.py` (新) | 绿 | C3 正向锁 |
| `test_omni_fix_embed.py` | 绿 | **C3.0 必改 :161/:223 解包**后绿; 勿破 g-embed-02 文本锁 (C2.5) + :228 源文本断言 |
| `test_citation_integrity_2026_06_14.py` | 绿 | 勿破 DI-7 Kelly 文本锁 (C2.5) |
| `test_omni_fix_runner.py` / `test_panel_orphan_merges.py` | 绿 | 合并机制测试, 加列不影响 |
| `ruff check .` | clean | |
| `test_panel_reproducibility.py` | Phase A/Phase B **均保持绿** (本特征 gate-neutral, §6.5) | 26_* 不在 parametrize → 加列不触 gate; 40_panel 当前零 staleness → 也不触 |

---

## §9 风险与回滚

| # | 风险 | 缓解 |
|---|---|---|
| R1 | 旧 30a parquet 无 emb_ss 列 → stage 18 崩 | D3 双层: ① `_load_aligned_embeddings` 用 `if 'emb_ss' in columns` 守卫返 None (绝不裸 `emb_aligned['emb_ss']`); ② **call-site** `if embs_ss is not None` 守卫 (compute_semantic_staleness 无 None 守卫, 守卫必须在调用点否则 None 传入崩) |
| R2 | 在 T=2 盘面误跑 snapshot → 把 T=2 bless 进 golden | §6.1 铁律: golden 重生**只在生产 T=19**。⚠ **data/processed 是 gitignored, 不能 `git checkout data/` 还原** → Phase A 不在 canonical 盘面跑真重型阶段 (走合成单测 §7.2); 若必须真跑则先备份 parquet 验后还原 (§7.6) |
| R2b | C2.1 改 3-tuple 但漏改测试解包 → import/解包崩 | **C3.0 [P0]**: test_omni_fix_embed.py:161/:223 与 C2.1/C2.2 同 commit 原子改 (对抗审计抓出) |
| R3 | 短窗下 semantic_ss 与 surface_ss 高度共线, 增量信息小 | §3.3 披露 (manuscript 附录报 corr); 非阻断, 是 by-design 接受 |
| R4 | golden 重生引入无关漂移 (脏树/并行会话误 bless) | 重生前 `git status` 确认盘面干净 + canonical pinned env + 2-run A/B (§6.3) |
| R5 | 改 docstring 误伤文本锁测试 | C2.5: 不动 Tetlock 构念披露 / Gentzkow-Kelly-Taddy 字符串 |
| R6 | emb_ss 编码使 stage 30a 内存/时间超 timeout(21600) | 全量 18.2M 时监测; 必要时 batch_size 上调 / 分块 (现 timeout 6h 含 3 轨仍有裕度) |

**回滚** (任意阶段): 删 C1 的 emb_ss 编码块 + `_build_output_frame` emb_ss 参数 + C2 的 embs_ss 解包/compute → 退回两轨; golden 还原到 pre-change commit (`git checkout tests/fixtures/golden_panel_v0.json`)。`aggregate_to_bank_year` 循环里的 semantic_staleness_ss 项**留着无害** (缺列即跳过, 本就是 DEFER 设计)。

---

## §10 验证 checklist (执行时逐项打勾)

- [ ] C1 改完: `grep emb_ss article_sbert.py` 见编码 + 输出 + 无 DEFER skip 残留
- [ ] C2 改完: `_load_aligned_embeddings` 签名注解 + 返 3 元组 + main 解包 3 元组 + **call-site `if embs_ss is not None` 守卫**
- [ ] **C3.0 [P0] 改完**: test_omni_fix_embed.py:161 (`, _`) + :223 (`, _, _`) 解包已更新
- [ ] C2.3 确认: `aggregate_to_bank_year` 未动 (循环已含 semantic_staleness_ss, 休眠待 C2.2)
- [ ] C2.5 确认: Tetlock/Kelly 文本锁字符串未动
- [ ] thin shim 未动 (已核: 25/26 shim 纯转发, 无 schema 逻辑)
- [ ] ruff clean
- [ ] 新测试 T1/T2/T3/T4 绿 (合成嵌入) + dag_consistency 绿 + 两文本锁测试绿 + omni_fix_runner/panel_orphan 绿
- [ ] (可选真跑) 走备份或 scratch dir, 不污染 canonical 盘面 (gitignored 不可 git 还原)
- [ ] (Phase B) 生产 canonical env (env 在 python 启动前设, 30a+18 同 session) 重跑 → 26_* 含新列; 核验 40_panel 是否流入 (§6.5b)
- [ ] (Phase B) 2-run A/B: semantic_staleness_ss/highstale_ss 两列哈希 0 漂移
- [ ] (Phase B) golden 重生 (snapshot 哈希现盘) — 注: 26_* 不在 repro parametrize, golden 26_* 条目更新后无 gate 强制 (§6.5a)
- [ ] (Phase B, 可选硬化) 把 26_* 加进 parametrize (§6.5d, 须同批 golden + 防 pre-existing 漂移)
- [ ] (Phase B) T4 绿: aggregate_to_bank_year 同时产 semantic_staleness_ss + semantic_highstale_ss
- [ ] (Phase B) 生产 canonical env 重跑 30a→18→45→46
- [ ] (Phase B) 2-run A/B: semantic_staleness_ss/highstale_ss 列哈希 0 漂移
- [ ] (Phase B) golden 重生 + repro gate 绿
- [ ] CLAUDE.md DEFER → 已平价 文案更新

---

## §11 引用锚点
- **Tetlock, P. C. (2011)**. All the news that's fit to reprint. *RFS* 24(5):1481-1512. (staleness 构念锚, 勿改受锁披露文本)
- **Bybee, Kelly, Manela & Xiu (2024)**. Business news and business cycles. *JF* 79(5):3105-3147. (30a 标题+首段截断策略)
- **Gentzkow, Kelly & Taddy (2019)**. Text as data. *JEL* 57(3):535-574. (DI-7 第二作者=Kelly 文本锁)
- `THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md` line 109/171 (原 DEFER 决策)
- `NONPOLARITY_DIMENSIONS_EXECUTION_PLAN_2026-06-20.md` line 113/125 (B2 boilerplate 援引本列为 DEFER 先例 — 本计划落地后该援引需更新)

---

---

## §12 对抗审计修订记录 (v1 → v1.1, 2026-06-21)

5-agent 顶刊对抗审计 (4 镜 + 完整性批判) 对 v1 跑了一轮; 我对每条 finding 对照真实代码裁决 (采纳真问题, 驳回误报)。**采纳并修订**:

| # | 严重度 | finding | 处置 |
|---|---|---|---|
| 1 | **P0** | `_load_aligned_embeddings` 改 3-tuple 破 `test_omni_fix_embed.py:161/:223` 的 2-tuple 解包 | **采纳** → 新增 C3.0 必改项 + R2b + §C2.1 原子耦合警告 (已核实两行确凿) |
| 2 | **技术错误 (我方 v1)** | §1.3 称回退行 `semantic_staleness_ss ≡ semantic_staleness_full` | **采纳并精确化**: 该等价**仅嵌入层成立**; 陈旧度层因参照窗口邻居不同而**不**成立 (反强化 ss 独立信号) → 重写 §1.3/§3.1/D1 + 重设计 C3-T3 (改全语料皆回退的干净不变量) |
| 3 | P1 | data/processed gitignored → `git checkout data/` 还原无效 (我 v1 R2 写错) | **采纳** → §7.2 改"合成单测优先 + 必要时备份/scratch"; R2 订正; §7.6 gate 处置 |
| 4 | P1 | 25_article_embeddings unhashable → repro gate 跳过它, emb_ss 加列无 gate 兜底 | **采纳** → 新增 §6.5 校验盲区披露 |
| 5 | P1 | 30a 与 18 须同 env (30a 嵌入端 BLAS 漂移下传) + env 须 python 启动前设 | **采纳** → §6.3 强化 |
| 6 | P1 | stata_export WARN 会在 Phase A 持续打 | **采纳但订正框架**: 该 WARN **pre-existing** (今天就在打), 非 Phase A 引入 → §2.2 注明 |
| 7 | P2 | 返回类型注解须同步改 / cost+50% 须验 timeout / 空串编码非 NaN / 存储冗余 | **采纳** → C2.1(b)/§7.1/D4 补 |

**驳回 (经反向核实为误报)**:
- "golden 26_staleness_panel 已 12 列, 12→14 存疑" — **驳回**: 亲读 golden:977-1059, 现确为 8 / 12 列 (无 semantic_ss), 8→9 / 12→14 正确 (审稿人混淆已存在的 surface_ss)。
- "stage 13 是否 prepend 标题到 content_ss 未验证" — **驳回**: 已核 `ctx_materializer.py:298 ss_list.append(prepend_title(title, ss_body))`, 与 ctx/full 同型, D2 成立 (已补引用)。
- "thin shim 未检查可能含 schema 逻辑" — **驳回**: 已读两 shim, ≤16 行纯 `import main; main()`, 无逻辑。
- "Phase A stranded +50% 算力成本" — **驳回**: 30a 不重跑就不编 emb_ss → Phase A 休眠零算力开销, 非 sunk cost (§7.3 订正)。
- "无 25_article_embeddings 列数硬断言须搜" — **驳回**: 已搜, 无; `:224 shape==(2,3)` 是断返回数组非 parquet 列数。

**裁决**: 修订后 **0 P0 残留** (P0 与技术错误已修)。计划达可执行态, 待用户放行 Phase A。

---

---

## §13 第二轮系统审计修订记录 (v1.1 → v1.2, 2026-06-21)

应用户"以国际顶刊最高标准、最系统最全面评审、再三确保万无一失"要求, 对 v1.1 跑了一轮 **42-agent 大型审计** (9 维并行评审 → 对每条 material 发现独立**对抗反驳验证** → 完整性批判)。结果: **37 findings / 32 material / 28 经反驳后存活 / 4 被反驳推翻**; 完整性批判另加 9 条。我对每条对照真实代码裁决。

**唯一真 material 问题 (P1, 我 v1.1 引入的回归 — 多 lens + 完整性批判 + 我独立实读三方坐实)**:
- **§6.5/§7.6 repro-gate 覆盖声明为假**。v1.1 曾称"下游 26_* 列哈希**有** golden 校验"并加了自相矛盾的 footnote 对冲。**实读 `test_panel_reproducibility.py:116-135` parametrize 列表 (18 文件) 不含 26_***。→ **v1.2 决定性重写 §6.5 为 a/b/c/d 四小节**: ①26_* 与 25_* 均**无** per-列 gate 覆盖 (验证只靠 C3 合成单测 + Phase B 2-run A/B); ②**我方独立实读 golden** 发现 gate-checked 的 `40_panel_yearly`/`51` **当前零 staleness 列** (合并未反映进 blessed 面板, pre-existing) → 本特征对 gate **中性** (不触红); ③registry-drift gate 不受影响; ④加 26_* 进 parametrize 是**可选独立硬化** (附 pre-existing 漂移风险注意), 非阻断要求。§7.6/§8/§6.2/§10 同步对齐。

**采纳的次要澄清 (P2, 提升可执行性, 非纠错)**: §1.3 全回退两触发 (FINTECH_AC=None / 全篇零共现) · T3 加"无 BLAS 累积浮点 → 逐位确定"论证 · C1.3 `else None` 仅后向兼容不可达说明 · C2.2 None 守卫不可删/内移 + 崩溃模式 · §7.2 Phase B canonical env shell 示例 (bash + PowerShell) · §6.2 highstale 自动派生注 · C2.5 Kelly 文本锁改函数锚点 · §10 checklist 对齐。

**驳回 (4 条被对抗验证推翻 + 我额外驳回的误报)**: "C2.1 签名位置隐式" (已写"现 401", 审稿误读) · "注册=32 不匹配" (16+16=32 是 CLAUDE.md 既有 DAG 注册数, 正确) · "必须 Phase A 强制加 26_* 进 parametrize" (会引入 pre-existing 漂移, 降级为可选硬化) · 若干 PASS-类"发现"实为确认计划正确。

**econometric 维度**: 该 lens 子代理未回结构化输出 (技术故障), 但其覆盖点已由完整性批判 + convention-counts lens 补齐: ①必要性/ROI 诚实性 (§3) 经查无夸大; ②**v1.1 回退非等价数学被独立判 "sound"** (参照窗口口径差异论证正确); ③Tetlock 构念保真披露充分; ④**IRON RULE (full×ctx×ss 禁混同一 Hansen J) 平凡满足** —— semantic_staleness 零下游消费, 不可能进任何 over-id GMM。

**裁决**: v1.2 **0 P0 / 0 未决 P1**; 唯一 material 问题 (gate 覆盖声明) 已决定性更正并经独立实读交叉验证。计划达"可直接执行、无错漏"态。

---

---

## §14 Phase A 执行记录 (2026-06-21, 用户放行后落地)

用户 2026-06-21 拍板"现在就实现",已执行 **Phase A** (代码层 $0, 合成单测验证; golden 重生留 Phase B 生产 run)。

**改动文件 (6)**:
- `pipeline/text/article_sbert.py` (C1): `_build_output_frame` +`embs_ss` 参数 + 条件写 `emb_ss` 列; `main()` 加 emb_ss 编码 (镜像 emb_ctx, title_col=None) + 删 DEFER skip 块 + `_build_output_frame(...,embs_ss)`; 结果分析块加 emb_ss 有效率体检; docstring/banner/白话 DEFER→平价。
- `pipeline/text/article_staleness.py` (C2): `_load_aligned_embeddings` 返 3-tuple (`tuple[ndarray,ndarray,ndarray|None]`, emb_ss 列缺→None); `main()` 解包 3-tuple + `if embs_ss is not None` call-site 守卫产 `semantic_staleness_ss`; `aggregate_to_bank_year` **未改** (循环已含, highstale 自动派生); docstring/注释/DEFER-log 更新。
- `tests/test_omni_fix_embed.py` (C3.0): :161 `, _` + :223 `, _, _` 解包 3-tuple (P0 原子耦合)。
- `tests/test_semantic_staleness_ss.py` (C3.1, **新增**): T1 (_build_output_frame emb_ss 条件写出, 3 例) + T2 (_load_aligned 优雅降级, 2 例) + T3 (全回退嵌入层等价→陈旧度逐位相等, faiss) + T4 (aggregate 产 semantic_staleness_ss + semantic_highstale_ss)。
- (C4 文档) CLAUDE.md 经核**无需改**: 其 v3.9.0 段无 "semantic_staleness_ss DEFER" 串 (DEFER 文本只在模块 docstring, 已更新); thin shim 纯转发未动。

**验证结果**: 新单测 **7/7 绿**; `py_compile` 两源文件 OK; Phase A 门禁 (test_semantic_staleness_ss + test_omni_fix_embed + test_citation_integrity + test_omni_fix_runner + test_panel_orphan_merges + test_dag_consistency) **117 passed / 0 failed**; 附加 staleness 测试 (test_metric_audit_p0_fixes + test_pipeline_robustness + test_omni_fix_embed) **68 passed**; `ruff check` clean。**向后兼容验证**: 盘面 30a 未重跑 (无 emb_ss) → embs_ss=None → semantic_staleness_ss 优雅缺席 (= 实现前行为, 零回归)。

**未做 (留 Phase B / 生产)**: stage 30a 全量重跑产 emb_ss + stage 18 产 semantic_staleness_ss 落盘 + golden 受控重生 (canonical pinned env + 2-run A/B, §6.3/§7.2)。**未提交 git** (待用户决定提交时机)。

---

---

## §15 真实端到端微验证 + 第二轮代码审计 (2026-06-21, Phase A 落地后)

### 15.1 真实 T=2 盘面端到端微验证 (最强证据: 备份→实跑→还原)
为以"实跑"而非"纸面"证明列真能正确物化, 在 T=2 盘面 (1125 篇, 含 content_ss) 实跑改后的 stage 30a→18 (本地 SBERT $0; data/processed gitignored 故先备份 3 parquet, 验后**还原 md5 逐字节一致**):
- **stage 30a**: 三轨编码全成功, `emb_ss` 有效行 **1125/1125 (100%)**; 25_article_embeddings.parquet 含 emb_ss 列 (11.6 MB, 2→3 轨)。
- **嵌入层等价 (实证 §1.3 修正)**: `ss_is_fallback` 162/1125 (**14.4%**, 合 ~14.27%); 回退行 **max|emb_ss−emb_full| = 1.34e-07** (≈0, 嵌入层等价); 非回退行 **= 0.21** (>0, ss 独立信号, 非纯冗余)。
- **stage 18**: `semantic_staleness_ss` 产出 (覆盖 97.7% / 均值 0.7926 / 高陈旧 9.92%), 与 semantic_full(0.7843)/ctx(0.7865) 同量级; G-D2.1 corr=**0.6746 (PASS ∈[0.3,0.7])**; 零 crash。
- **列 schema 实测吻合计划**: `26_article_staleness` **8→9**; `26_staleness_panel` **12→14** (semantic_highstale_ss 自动派生)。
- **盘面已还原**: 3 文件 md5 == 备份, blessed 态零漂移 (golden 不受污染)。

### 15.2 第二轮 17-agent 代码审计 (审 IMPLEMENTED 代码)
6 维并行 → 对抗验证 → 完整性批判。**核心两维 (sbert-correctness / staleness-correctness) 全 PASS (0 finding)**; ⚠ 验证阶段 6 子代理遇环境 auth (401) 中断 → 未自动验证者我**亲对照代码 + 用 §15.1 实跑结果裁决**。
- **唯一确认真缺陷 (P1, 已修)**: `article_sbert.py:281` 注释头残留"嵌入轴 full/ctx 两路编码 (ss v1 延后)", 与下方已实现三轨编码矛盾 → 改为"full/ctx/ss 三路编码 (ss 2026-06-21 平价上线)"。
- **采纳测试加固**: 新增 `TestNoneGuardNecessity` (证 compute_semantic_staleness 传 None 必崩→call-site 守卫 load-bearing + 旧 parquet→None→优雅跳过链)。
- **驳回/实跑证伪**: "emb_ss dtype/shape 未校验" (与既有 emb_full/ctx 同款, 非新缺陷; §15.1 实证 (1125,768) float32 正确) · "emb_ss/full 形状不匹配" (同 emb_aligned reindex, 行数恒等) · "content_ss 空串静默崩" (空串得有效向量; §15.1 实证 162 回退+963 窗口全正常)。
- backcompat/completeness/docs 维度均 PASS。**与并行 codebook core_patterns 退役无冲突** (本特征 3 文件 grep retired-symbols=0)。

### 15.3 最终状态
代码 (含 §15.2 P1 修复) + 单测全绿 (62 gate / ruff clean / py_compile OK); 真实端到端实跑证列正确物化; 盘面 blessed 态已还原。**Phase A 完成且经实跑+审计双重验证, 0 未决缺陷。** 仍**未提交 git**。

---

---

## §16 第四轮终审 (34-agent 定稿) — 实现洁净认证 + Phase B 风险加固 (2026-06-21)

应用户"最后一次, 国际顶刊最高标准, 万无一失"要求, 跑了**第四轮 34-agent 终审** (7 维并行 → 对抗验证 → 元批判)。**30 findings / 26 material / 15 经反驳后存活 / 11 推翻**; 元批判 verdict = **MINOR_ISSUES**。

**实现层洁净认证 (5/7 维 CLEAN)**: code-correctness-fresh / plan-vs-code-consistency / integration-crosscut **0 finding**; test-rigor 9 条全为 **PASS-确认** (T3 NaN 语义 sound / T4 聚合算术 / T5 None 守卫 load-bearing / 三轨 title_col=None parity / 条件列写向后兼容 / 全链优雅降级 — 均确认正确); meta-prior-audits 6 条全 PASS-确认 (无残留 DEFER 误导 / 测试全覆盖 C1+C2+C3)。**配合第四轮我方补做的 262-test 盘面回归 (0 fail) + 真实 T=2 端到端实跑 (§15.1), Phase A 实现代码经四轮审计 + 实跑 + 回归三重坐实, 0 defect。**

**两 lens 提出的全部存活 findings 均为前瞻 Phase B 生产风险 (非 Phase A 缺陷)**, 处置:
- **[已落地 — 我方代码加固]** `_load_aligned_embeddings` 加 emb_ss shape 守卫 (`article_staleness.py`): emb_ss.shape != emb_full.shape (维度/行数) → fail-loud (镜像本函数既有 30a-陈旧守卫), 防生产时错维语义信号静默喂 Faiss; 配 test `test_emb_ss_dim_mismatch_fails_loud` 锁定。
- **[Phase B 前置, 文档]** **timeout**: stage 30a 3 轨在 T=19(18.2M) 可能超 21600s(6h)。Phase B 须: ① 先测 2 轨 baseline 墙钟; ② 若 `baseline×1.5 > 5.5h` 则 `core/dag.py` 的 30a timeout 21600→28800(8h); ③ 或保守直接预调 8h。(§7.1 已注, 此处升为 Phase B 必办步。)
- **[Phase B 前置, 文档]** **BLAS 确定性**: `core/stage.py:209` 子进程只钉 `PYTHONHASHSEED`, **未钉 BLAS 线程变量** (MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS); 而 BLAS 线程态在 numpy import 时即锁定 (早于子进程 Popen)。→ Phase B golden bless **必须在 shell 启动 orchestrator 前 pre-export** 这些变量 (§6.3 已述, 此处明确根因)。⚠ `core/stage.py` 是**共享编排 infra** (影响全部嵌入派生列, 非本特征引入, pre-existing) → **本特征不改它** (避免 scope creep + 并行冲突); 留作全管道独立 determinism 加固项 (可选: 在 stage.py:209 块补 `env.setdefault` 5 个 BLAS 变量)。
- **[Phase B 预期, 文档]** **40_panel 合并范围**: §6.5b 已述 blessed 40_panel 现零 staleness; Phase B 全量重跑若让 26_staleness_panel 新鲜度通过, `_merge_optin_feature_panels` 会把**全部** staleness (surface 3 轨 + semantic full/ctx/ss) 左连接进 40_panel_yearly/51 —— 这是预期且 gate-中性 (26_* 不在 parametrize); golden 重生须涵盖这批列。
- **[非缺陷]** "Phase A 未提交" (F3): 用户 2026-06-21 明确选"暂不提交, 保持工作树" → 设计内, 非缺陷。 "T3 用 mock 非真 SBERT" (F4): T3 锁数学等价契约 (同输入→同输出) 足够 Phase A; 真 SBERT 嵌入层等价已由 §15.1 实跑 (1.34e-07) 坐实, 可选 Phase B 落为可复跑 gate。

**裁决**: **Phase A 实现 0 未决缺陷, 经四轮审计 + 实跑 + 262-test 回归认证洁净**; 唯一新增代码加固 (emb_ss shape 守卫) 已落地+锁测。所有其余 findings 为 Phase B 生产前置 (timeout/BLAS/panel-merge), 已文档化为 Phase B checklist。Phase B 本身受 M0/生产 gate 延后, 不在本次交付范围。

---

---

## §17 提交记录 (2026-06-21, 用户授权后落地)

用户 2026-06-21 "授权执行计划, 完成所有的任务" → **本特征 5 文件已 by-name 提交并 FF 推送 main**。

**提交内容 (5 文件, 严格 by-name, 排除工作树 ~19 个并行会话脏文件)**:
- `pipeline/text/article_sbert.py` (C1: emb_ss 三轨编码 + 权威块文档 + final-audit 注释修)
- `pipeline/text/article_staleness.py` (C2: 3-tuple + None 守卫 + emb_ss shape 守卫 + 文档)
- `tests/test_omni_fix_embed.py` (C3.0: 2-tuple→3-tuple 解包 ×2)
- `tests/test_semantic_staleness_ss.py` (C3.1: 10 个正向锁单测, 新增)
- `scripts/audit/SEMANTIC_STALENESS_SS_EXECUTION_PLAN_2026-06-21.md` (本计划, 新增)

**安全法 (沿用项目惯例)**: HEAD == origin/main (renumber 工作已在 main, 无分支领先) → 干净 worktree off origin/main + by-name 拷入 5 文件 (我方源文件 diff 经 grep 证 0 并行污染) + FF 推送。**刻意未提交**: stata_export/encode/export/runner/policy_* 等 ~19 个并行会话脏文件 + 测试可能 bump 的 `data/processed/v3_5_1_constants.json` (按惯例还原)。

**未含 (留 Phase B / 生产, 非本提交)**: stage 30a 全量 T=19 重跑产盘面真列 + golden 受控重生 + §16 三项 Phase B 必办 (timeout/BLAS/panel-merge)。**当前盘面 26_* 仍旧 schema** (微验证后已还原), 待 Phase B 生产重跑才落真列。

---

## §18 第五、六轮终审 + 全量回归 (2026-06-21, 提交后认证)

提交后又跑了**第五轮 21-agent 提交后认证** (§16 已记) + **第六轮 12-agent 全息终审** + **全量单测回归**。

### 18.1 全量单测回归 (实测, 最强经验证据)
`pytest news_process/tests`(除 integration): **3740 passed / 14 failed / 8 skipped**。**14 失败逐一 grep 证实全部不引用本特征模块** (article_sbert/article_staleness/_load_aligned_embeddings/_build_output_frame/compute_semantic_staleness/emb_ss/semantic_staleness) → **0 失败源于本特征**; 全为 pre-existing 环境/盘面/并行: 缺盘 parquet (40_panel_yearly/cohort CSV)、23_bert_tone NaN (stage 23, 非本特征)、papers_assets git-ignored 目录、并行 codebook/zscore/val_mask 改动 (均见 memory 既有失败集)。**本特征自身单测 43 passed** (10 ss + 33 embed)。

### 18.2 第五/六轮审计裁决
- **第五轮 (21-agent)**: 5/5 lens + critic 全 **CERTIFIED_CLEAN** (post-commit 完整性/并发安全/代码复核/集成/诚实)。
- **第六轮 (12-agent)**: holistic-correctness + completeness-final **CERTIFIED_CLEAN** (committed 代码 0 缺陷); production-honesty lens 提 4 项, 经裁决**无一是本特征 5 文件的缺陷**:
  - `codebook.py::_infer_source_stage` 对 staleness 列返 'unknown' → **pre-existing** (波及全部 6 个 staleness 列, 含早于本特征的 5 个) + **并行会话正改 codebook.py** → 不碰 (避冲突/scope), 列为 codebook-session/Phase B 改进项。
  - `core/stage.py:209` 未钉 BLAS 线程变量 → **pre-existing 共享 infra** (波及全部嵌入派生列), §16 已诚实记 + shell pre-export 解法 → 不碰共享 infra。
  - stage 30a timeout 3 轨 T=19 风险 → **Phase B 生产前置** (Phase A 代码不受影响, timeout 仅 18.2M 规模才触), §16 已记"先测后调"。
  - commit 信息 "三前置...受 M0/生产 gate 延后" → 实为诚实 ("延后"=未就绪), 本节进一步明确: **此三项为 Phase B 必办待处理项, 非已就绪**。

### 18.3 Phase B 必办清单 (强化, 提升可发现性)
执行生产 T=19 重跑 + golden bless **前**必办 (均非 Phase A 代码缺陷, 为生产前置):
1. **timeout**: 先在 ~10k 文样测 stage 30a 2 轨墙钟; 若 `×1.5 > 5.5h` 则 `core/dag.py` 该阶段 timeout 21600→28800 (或保守预调 8h)。
2. **BLAS 确定性**: shell 启动 orchestrator **前** `export PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1` (因 `core/stage.py:209` 只钉 PYTHONHASHSEED; 全管道 pre-existing, 非本特征)。
3. **panel-merge**: 重跑后核验 staleness 是否流入 40_panel (runner 泛型左连接会自动拾取, gate-中性)。
4. **codebook**: (可选, codebook-session/并行处理) 给 `_infer_source_stage` 加 staleness→Stage 18 case (现返 'unknown', pre-existing 波及 6 列)。

### 18.4 最终裁决
**本特征 (semantic_staleness_ss, 5 文件) 经六轮审计 (5+42+17+34+21+12 = 131 agent) + 真实 T=2 端到端实跑 + 3740-test 全量回归三重认证, committed 代码 0 缺陷 / 0 回归。** 六轮所有"残留 finding"经裁决全部为 pre-existing 共享 infra / 并行会话 / Phase B 生产前置 / 命名约定 (stage 30a) / 智能体幻觉 — **无一是本特征交付物的缺陷**。Phase B 生产执行 (须全量 18.2M 语料, 本机无) 连同 §18.3 四项前置待生产环境进行。

---

*本计划经**六轮**顶刊多智能体审计 (v1→v1.1 5-agent §12; v1.1→v1.2 42-agent §13; Phase A 后 17-agent 代码审 §15.2; 第四轮 34-agent 终审 §16; 提交后第五轮 21-agent 认证 + 第六轮 12-agent 全息终审 §18), 共 131 agent, 全程 committed 代码 0 缺陷。**Phase A 已于 2026-06-21 用户放行后实现, 经真实端到端微验证 + 3740-test 全量回归 (0 源于本特征) + 六轮审计三重坐实** (§14/§15/§16/§18; 代码+单测绿, ruff clean, 实跑证列正确物化 8→9/12→14, 盘面已还原); **已于 2026-06-21 用户授权后 by-name 提交并 FF 推送 main (commit 3df4a4d9, 5 文件, 排除并行脏文件, 见 §17)**; Phase B (生产 T=19 重跑 + golden 重生; timeout/BLAS/panel-merge 三项 Phase B 必办见 §16/§18.3) 受 M0/生产 gate 延后。*
