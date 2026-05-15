# Stage 3 双轨化方法学 (plan v14 / v3.2.0)

> 本文档由 plan v14 冻结后转正为方法学正式文档。
> 锚定 tag: `plan-stage3-dual-track-frozen` + `v3.2.0`

## 1. 核心问题

`innovation_locus` 与 `innovation_substantiveness` 是 v7 prompt stage 3 的两条并列输出。v3.1.x 之前**仅 full 轨产出标签**（ctx 轨结果被 [tone_llms.py:1298-1324](../../pipeline/sentiment/tone_llms.py#L1298-L1324) 主动丢弃），但 LLM 已对 ctx 轨调用。这违反了 Hassan 2019 QJE 以来的"非情感属性也走 entity-proximity"主线方法学。

## 2. v3.2.0 双轨化变更

### 2.1 篇章级 (stage 21)

| v3.1.x 列 | v3.2.0 列 | 变更 |
|---|---|---|
| `innovation_locus` | `innovation_locus_full` + `innovation_locus_ctx` | BREAKING rename + add |
| `innovation_substantiveness` | `innovation_substantiveness_full` + `innovation_substantiveness_ctx` | 同 |
| `category_confidence` | `category_confidence_full` + `category_confidence_ctx` | 同 |
| — | `llm_verified_dual_full_only` / `_ctx_only` / `_both` | NEW (三互斥指示) |

### 2.2 致命修复 R1-A

[tone_llms.py:1416](../../pipeline/sentiment/tone_llms.py#L1416) 原 `df_filtered = df[df['llm_verified_full'] == True]` 让 ctx 轨样本**完全 conditional on full**，使 ctx 轨不能作 main spec。v3.2.0 改并集 `verified_full | verified_ctx`，与 Hassan 2019 QJE entity-proximity independence 一致。

### 2.3 平局策略对称（plan v14 §3.1 P1.5）

ctx 轨与 full 轨**完全同策略**：
- locus 平局 → `应用场景`（modal class prior, MAP under uniform prior）
- substantiveness 平局 → `象征性`（W&Z framework 下实质性需充分证据，平局倾向象征性是保守审慎）
- 空票回退：locus → `canonicalize_topic(topics_track)`；substantiveness → `None`

### 2.4 关键词分类器双轨独立（plan v14 R3-B）

`canonicalize_topic(topics_full)` 与 `canonicalize_topic(topics_ctx)` **独立运行**——每个轨道的 LLM `fintech_topic` 字段独立汇总后跑关键词规则。+0.2 / ×0.5 confidence 调整双轨独立适用。

## 3. Panel 层（stage 45）

### 3.1 子集 mean 对角线（plan v14 §2.2 Action #5）

| 子集 | 分类轨 | 情感轨 | 命名后缀 |
|---|---|---|---|
| 底层技术 | full | full | `_tech_<隐式 lf>_full` (current `_tech_*_full`) |
| 底层技术 | ctx | ctx | `_tech_lc_ctx` |
| 应用场景 | full | full | `_app_<lf>_full` |
| 应用场景 | ctx | ctx | `_app_lc_ctx` |
| 实质性 | full | full | `_sub_<sf>_full` |
| 实质性 | ctx | ctx | `_sub_sc_ctx` |
| 象征性 | full | full | `_symb_<sf>_full` |
| 象征性 | ctx | ctx | `_symb_sc_ctx` |

**规则**：mean 聚合仅产对角线（`_lf × _full`、`_lc × _ctx` / `_sf × _full`、`_sc × _ctx`）；非对角线无方法学先例，不产出。

### 3.2 篇章级 count 4-way（plan v14 §2.3）

洗稿率定义涉及 `sentiment ∧ substantiveness` 交叉。Bingler 2022 FRL 用 disclosure-segment sentiment × firm-level substantiveness 的混合，所以 count 走 4-way：

```
_is_pos_symb_<sent_track>_<subst_track>
sent_track ∈ {full, ctx}; subst_track ∈ {sf, sc}
4 组合: full_sf, full_sc, ctx_sf, ctx_sc
```

## 4. Bartik IV 双套（plan v14 §3.4）

- `bartik_fintech_lf_share_{tech,app}` + `bartik_fintech_lf_iv_{full,ctx,title}`：share = `innovation_locus_full` 基期占比
- `bartik_fintech_lc_share_{tech,app}` + `bartik_fintech_lc_iv_{full,ctx,title}`：share = `innovation_locus_ctx`

论文用法：main spec 选 `_lf` 或 `_lc` 之一（论文 Methods §4 决定），另一作 Robustness Appendix。

## 5. main spec 选择（plan v14 §3.6 Action #3）

工程仅产 4 套 spec 列，main spec **不由工程决定**。推荐方向（论文可改）：
- Locus：`_lc`（Sautner 2023 JF entity-proximity 同构）
- Substantiveness：`_sf`（W&Z 1998 ASQ 全文判定优先，decoupling 信号需 article-level triangulation）
- Sentiment：`_ctx`（Hassan 2019 QJE）

## 6. 文献锚定

- Hassan, Hollander, van Lent, Tahoun (2019, QJE) — Firm-level political risk: Measurement and effects.
- Sautner, Van Lent, Vilkov, Zhang (2023, JF) — Firm-level climate change exposure.
- Bingler, Kraus, Leippold, Webersinke (2022, FRL) — Cheap talk and cherry-picking: What ClimateBert has to say.
- Westphal, J.D. & Zajac, E.J. (1994, 1998, ASQ) — Substantive vs symbolic management.
- Gomber, Kauffman, Parker, Weber (2018, JMIS) — On the Fintech Revolution.
- Fiss, P.C. & Zajac, E.J. (2006, ASQ) — Decoupling.
- Adner, R. & Kapoor, R. (2010, SMJ) — Value creation in innovation ecosystems.
- Wang et al. (2023, ICLR) — Self-consistency improves chain of thought reasoning.
- Carlson & Burbano (2026, SMJ §3.5) — Prompt sensitivity multi-window robustness.

## 7. 审计统计

- v1 → v14 累计 **62 轮极致审计**（68 finding 全部修复）
- 用户 **9 项 Action Items** 书面确认
- v3.2.0 实施期 **7+ 个 milestone commit**（M0-M7+）
- 测试基线 994 → 1046 passed (+52 测试)

## 8. 复现链路

```bash
# 1. 切到 v3.2.0
git checkout v3.2.0

# 2. 装依赖 (含新加 pyreadstat)
pip install -e .

# 3. 跑 pipeline (含 stage 46 Stata 数据导出)
python news_process/run_pipeline_function.py

# 4. 选 main spec + 打 replication 包
from news_process.papers._common.stata_runner import build_replication_package
pkg = build_replication_package({
    'MAIN_LOCUS_TRACK': 'lc', 'MAIN_SUBST_TRACK': 'sf', 'MAIN_SENT_TRACK': 'ctx',
    'PROJECT_ROOT': '/local/path',
})

# 5. 跑 Stata
cd pkg/code; stata -b do 00_master.do
```
