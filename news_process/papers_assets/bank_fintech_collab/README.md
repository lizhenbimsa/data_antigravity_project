# P5 — Bank Fintech Collab Mode (v3.4.0 epoch 5)

## 概览

**Paper ID**: `bank_fintech_collab`
**Status**: NEW (M0 G0 frozen pending epoch 5 audit streak 3/3)
**Master plan**: 原 docs/plan/B_route_master_plan_v2.md (v2.56) 已随 docs/ 目录整体删除 (commit 1698bda5)，如需查阅请检出该 commit 之前的 git 历史。

## 研究问题

银行的 fintech 创新公告中，**自主研发** (closed innovation / in-house R&D) 与 **外部协同** (open innovation / external collaboration) 是否对长期 fintech 投资落地、M&A 活动、股票市场反应产生差异化影响？

## 学术框架

- **Chesbrough (2003)** Open Innovation: The New Imperative for Creating and Profiting from Technology. HBS Press.
- **Laursen & Salter (2006)** Open for innovation: The role of openness in explaining innovation performance among UK manufacturing firms. SMJ 27(2), 131-150.
- **Hagedoorn (2002)** Inter-firm R&D partnerships: An overview of major trends and patterns since 1960. Research Policy 31(4), 477-492.

## 与现有 8 paper 的差异化

详见 [paper_spec.yaml](../../papers/bank_fintech_collab/paper_spec.yaml) `differentiation_claim` 段。简言之：
- **P3 (substance)**: 度量公告的 W&Z 二元属性（实质/象征），与本 paper 概念正交
- **P4 (locus)**: 度量公告的 Gomber 二元属性（底层/应用），与本 paper 概念正交
- **三维交叉**: P3 × P4 × P5 = 2³ = 8 cross-tab cells（论证依据见 [paper_spec.yaml](../../papers/bank_fintech_collab/paper_spec.yaml) `differentiation_claim` 段；原 innovation_collab_mode_framework.md 已随 docs/ 目录整体删除 commit 1698bda5 而不存在）

## 关键变量

| 变量 | 类型 | 来源 |
|---|---|---|
| `innovation_collab_mode_full` | byte 0/1 | Stage 21 LLM (prompt v8) |
| `innovation_collab_mode_ctx` | byte 0/1 | Stage 21 LLM (entity-context, Hassan 2019 QJE 同构) |
| `m_and_a_fintech` | int | M0.5.11 Tonghuashun |
| `r_and_d_intensity` | float | M0.5.11 CSMAR 年报 |
| `car_5day_window` | float | M0.5.11 CSMAR daily returns |

## Pre-registration

本 paper 锚定 prompt v8 字节级冻结（v8 = v7 严格超集，additive supplementation per Nosek et al. 2018 PNAS；v8 SHA256 详见 CLAUDE.md L33 (Prompt v8 字节级冻结) / L40 (prompt_v8_sha256 sidecar) 与 `data/processed/v3_5_1_constants.json::prompt_v8_sha256`。专属 git tag `prompt-v8-supplementation-released` 尚未打，唯一已打的 prompt tag 是 `prompt-v7-released`）。W&Z 框架边界论证（collab mode 维度与 P3 substance / P4 locus 概念正交、不构成同一构念的重复测量）原 wz_framework_boundary_justification.md §4 已随 docs/ 目录整体删除 commit 1698bda5 而不存在。

## 投稿路径

```
SMJ (main) → AMJ → ASQ (cascade 终点)
任一阶段 reject 后 Salvage path: 改写为 absorptive capacity 框架投 Research Policy.
```

提交窗口: 2027-04-09 (原 master plan §4 timeline + R6-13 P5 加入推迟 +3.5wk; 该 master plan 已随 docs/ 目录整体删除)

## 目录结构

```
bank_fintech_collab/
├── README.md            # 本文件
├── manuscript_en.md     # 英文 manuscript 骨架 (M3 阶段填实)
├── manuscript_zh.md     # 中文 manuscript 骨架 (M3 阶段填实)
├── do/                  # Stata replication 输出 (build-replication CLI 生成)
├── drafts/              # 草稿与 reviewer 反馈
└── output/              # Tables/figures/logs 实际产出
```

## 实施状态 (v3.4.0)

- [x] paper_spec.yaml 冻结
- [x] `papers/bank_fintech_collab/__init__.py` 注册
- [x] Stata 8 模板镜像 locus 子目录
- [ ] M3 manuscript 8 section 填实
- [ ] M5 主回归实证
- [ ] M6 稳健性 battery
- [ ] M7 内审 + 投稿包
