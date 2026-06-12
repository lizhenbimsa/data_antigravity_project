# news_process 功能完整性系统评估报告

**日期**: 2026-06-05  **方法**: 13 子系统并行评估 + 删除候选双视角对抗复核（25 agent / 674 次取证）
**范围**: 142 个功能单元（阶段 / 论文 / 实现模块 / 基础设施 / Stata 模板 / 配置）
**性质**: 只读审计，未改动任何代码或数据

---

## 一句话结论

> **项目主干极其健康**：35 个注册阶段 + 13 个面板模块 + 19 个核心基础设施模块 **全部完整在用、零孤儿**。
> 真正"未完成"的部分都是**有意 gate 的 opt-in 功能或 provisional 论文骨架**（不可删，待补完）。
> 全仓**只有 2 处确认可安全删除**，都是已退役功能的**磁盘残渣**（非代码）。
> 初筛的 6 个删除候选中，**4 个被对抗复核推翻**——其中 1 个还反向逮出一个被遗漏的 Stata 崩溃隐患。

---

## 一、总体完整性分布

```
判定分布（142 单元，含按维度交叉计数）
KEEP（完整在用）         ████████████████████████████████  ~98 (69%)
INCOMPLETE_WIP（待补完） ████████████████                  ~38 (27%)
RETIRE_REMNANT（残渣）   ██                                  4  (3%)
DELETE_CANDIDATE→复核    █                                   2  (1%)
```

## 二、13 子系统健康度矩阵

| 子系统 | 单元数 | 平均完整度 | 结论 | 一句话 |
|---|---|---|---|---|
| 主线生产阶段(00–51) | 14 | ~98% | ✅ 全 KEEP | 每个都注册+落盘+测试+下游消费，名副其实 |
| 面板模块(stage45 内 41-47) | 13 | 100% | ✅ 全 KEEP | runner 硬 import 全部 11 个 compute 模块，零孤儿 |
| 核心基础设施(core/) | 19 | 100% | ✅ 全 KEEP | 14 core + 5 core/text 全活跃，重点嫌疑全部洗清 |
| 验证阶段 31–38b | 11 | ~99% | ✅ 全 KEEP | 稳健性附录材料，DAG+config+产物齐全 |
| 验证阶段 39 系列 | 6 | ~95% | ✅ 全 KEEP | 39f 还回并面板供第10篇消费 |
| 情感/特征实现模块 | 14 | ~95% | ✅ 13 KEEP / 1 WIP | forward_looking/lm/num 经 stage22 接线非孤儿 |
| audit/text 实现模块 | 13 | ~85% | ⚠ 10 KEEP / 2 WIP / 1 候选 | llm_contamination_test 唯一未接线 |
| 未注册 shim + 退役残渣 | 6 | — | ⚠ 3 KEEP / 3 残渣 | 27c/52/53 按设计不注册；3 处磁盘残渣 |
| 衍生论文(4篇) | 10 | ~73% | ⚠ 7 KEEP / 3 WIP | benefit_society 最成熟；3 个 NCD 模块卡 D4 |
| 主线论文(5篇) | 5 | ~58% | ⚠ 1 KEEP / 4 WIP | 仅 P1(tone)数据接通；P2-P5 缺处理列/外部数据 |
| provisional 论文(3篇) | 12 | ~65% | ⚠ 1 KEEP / 11 WIP | 入口/Table1 真实，Table2-5 esttab 占位 |
| 模板/验证/配置 | 14 | ~75% | ⚠ 7 KEEP / 6 WIP / 1 候选 | 2 个归档模板接近孤儿；2 个配置无生产消费者 |

---

## 三、删除候选「三重核查」结果（本报告核心）

初审标 6 个删除/残渣候选，每个派 **2 个对抗怀疑者**（代码用法视角 + 配置/数据/论文视角），任务是**尽力证明它在用、反驳删除**。结果：

| # | 候选 | 初审 | 视角A(代码) | 视角B(配置/论文) | **最终裁定** |
|---|---|---|---|---|---|
| 1 | `data/processed/39g_*.json` | 残渣 | 可删 | 可删 | **🟢 确认删除** |
| 2 | `16_epu_panel.parquet`(仅备份目录) | 残渣 | 可删 | 可删 | **🟢 确认删除** |
| 3 | `30_text2vec_indicators.csv` | 残渣 | — | 可删 | **🟢 可删(.csv)** |
| 3 | `30_text2vec_indicators.parquet` | 残渣 | 仍被 golden 测试消费 | 可删 | **🟡 先清理再删** |
| 4 | `llm_contamination_test.py` | 删除候选 | **推翻**:DC4必修 | **推翻**:2篇spec承诺 | **🟡 别删→接线补完** |
| 5 | `_title 情感轨残留` | 残渣 | **推翻**:迁移脚本是provenance | 可删但**逮出崩溃隐患** | **🔴 别删→修隐患** |
| 6 | `25_tableA6_dual_track_residual.do.tmpl` | 删除候选 | **推翻**:消费10列活产物 | **推翻**:D4活表 | **🟢 保留(误判)** |

### 逐条核查详情

**🟢 #1 `39g_track_discriminant_validity.json` —— 确认安全删除**
- 4509 字节，mtime `2026-05-30`（早于 v3.8.0 删除提交 `6382cc67`），被 `.gitignore` 忽略未跟踪。
- 内容含 `htmt_full_title`/`htmt_ctx_title` 键 = v3.8.0 已删的 `_title` 判别效度轨产物。
- 两视角穷尽搜索：全仓 `.py/.yaml/.json/.do.tmpl` 零按名引用；生产者模块与 shim 已删；仅有的 5 处代码引用全是"确认已删"的迁移脚本与测试断言。
- ✅ **可直接删，无需任何配套改动。**

**🟢 #2 `16_epu_panel.parquet`（EPU 宏观控制，2026-06-05 移除）—— 确认安全删除**
- 活跃代码树 **100% 干净**：`core/dag.py`/`core/schemas.py`/`pipeline/` 零真实命中（仅 `repurchase`/`Deephouse`/`keepusing` 等子串假阳性）；`pipeline/external/` 与 `data/external/` 目录已不存在。
- 残留仅在两个带时间戳的**整目录备份快照**：`data/processed_bak_20260531_2226/` 与 `data/processed_metricaudit_bak_pre_regen/`。
- ✅ **属备份目录整体清理范畴，危害极低，可连同备份目录择期清理。**

**🟡 #3 `30_text2vec_indicators.parquet / .csv`（stage 30 text2vec 退役遗留）—— 拆分处理**
- 两文件 mtime `2026-05-29`（= stage 30 退役当日），gitignored 未跟踪。
- **`.csv`**：全仓零引用 → ✅ 可直接删。
- **`.parquet`**：⚠ 仍被 `golden_panel_v0.json`（6列/157行哈希）+ `test_panel_reproducibility.py:122`（**实跑 1 passed**）+ `_ORPHAN_WHITELIST` 三处追踪。直接删会**破坏 golden 漂移闸门测试**。
  - ✅ 正确处置：先从 `golden_panel_v0.json` + `generate_golden_snapshot.py::_ORPHAN_WHITELIST:44` + `test_panel_reproducibility.py:98,122` 三处移除，重生 golden，再删。
- ⚠ **勿误删活跃的 `shibing624/text2vec-base-chinese` 嵌入模型**（stage 15/25 在用，与退役 stage 同名易混）。

**🟡 #4 `pipeline/audit/llm_contamination_test.py`（DC4 LLM 污染检验）—— 别删，接线补完**
- 初审标"纯 CLI 孤儿：无 shim、未注册 DAG、无人 import"——**两视角均推翻**：
  - 它是 **2 篇 frozen paper_spec 明确承诺的 DC4 必修交付物**：`bank_news_clarity/paper_spec.yaml:118,222` + `bank_media_disagreement/paper_spec.yaml:108,205`（`llm_contamination_holdout`）。
  - 有 **9 个通过的 fast 单元测试**（`test_llm_contamination_test.py`），删模块即破 CI 绿色基线。
  - 算法完整且活跃维护（Fisher z + permutation + Bayes factor，多轮修复）。
- ⚠ 但确**未接线**：是同目录 6 个 audit 兄弟（39a/39c/39d/39e/39f/52 各有 shim+注册）中**唯一缺 shim+注册**的。
- ✅ **正确处置：补 `5X_*` shim + 注册进 STAGES_VALIDATION + 接 stage 49 outcome 列，而非删除。**

**🔴 #5 `_title 情感轨残留` —— 别删，且修一个被遗漏的崩溃隐患**
- `_title` 情感轨在活跃管线中**已无死代码**（v3.8.0 正确退役）。残留分两类：
  - **迁移脚本**（`scripts/migrate/remove_title_track.py` 等）：是 v3.8.0 不可逆破坏性变换的 **provenance 记录**，且 `stata/` 标签管线被测试 pin（`test_dta_name_sanitizer_consistency.py`）→ **归档而非删除**。
  - **🔴 对抗复核反向逮出的崩溃隐患**（初审漏判）：
    - `papers_assets/bank_fintech_tone/do/falsification_template.do.tmpl:126` 仍有**未守卫的** `reghdfe Y prob_gap_title_full X`，而当前 `51_panel_with_controls.parquet`（1565 列，2026-06-05 重生）**已无任何 title 列** → 该回归对当前 .dta **会运行期报错**。
    - `stata/05_label_advanced.do:66` 与 `data/processed/variable_codebook.csv:1155` 仍吐出**幻影 `prob_gap_title_full`** 行（codebook 是 6-05 重生的构建物，schema 不符）。
- ✅ **正确处置：修复/守卫这 3 处 stale title 引用（防 Stata 崩溃），而非删 `_title` 相关文件。**

**🟢 #6 `v3_5_0/25_tableA6_dual_track_residual.do.tmpl`（归档模板）—— 保留（初审误判）**
- 初审标"连 spec 都不引用，仅靠 test 存活，建议删"——**两视角均推翻**：
  - 它消费的 **10 个 D4 列**（`subst/locus/collab × disagree/freerider/quietworker_frac` + `d4_data_quality_flag`）是 **活跃产物**：由 `encode_collab.apply_v3_5_0()` 在 stage 45 内**无条件产出**（`encode.py:1341`），已落盘 `40_panel_yearly` / `51_panel_with_controls`（174 行真实数据）。
  - 有 `test_residual_signals.py`（12 测试）+ 计数不变量 `test_papers_b_route.py:138`（rglob 断言恰好 95 模板）守护。
  - 与被 3 篇 spec 引用、公认 KEEP 的同目录 sibling `19_table6_cell_decomposition` 命运应一致。
- ✅ **保留。**（初审"grep 仅 3 处"只对字面文件名成立，漏掉了它消费的列）

---

## 四、保留 vs 删除 总原则

**为什么主干几乎全部保留（理由维度）**：

| 维度 | 主干表现 |
|---|---|
| 接线(wired) | 35 阶段全在 `core/dag.py` 注册；面板 11 模块被 runner 硬 import；core 全被两 runner / pipeline import |
| 产物(output) | `data/processed/` 28 个 parquet 全为 2026-05-31~06-05 新近重生 |
| 测试(tests) | 134 个测试文件，全量 ~2581 passed；DAG 一致性 + golden 复现双闸门 |
| 下游消费 | 面板 → .dta → 论文回归 / Stata 模板，闭环可追溯 |

**真正"未完成"的三类（都不可删，需标注待补完）**：
1. **opt-in 阶段**（17 BERTopic / 19 NER / 49 风险结果）：代码完整，因**缺依赖包 / $12 LLM 预算 / 缺上游数据**被 config gate，从未实跑。
2. **provisional 论文**（collab / disagreement / clarity）：入口 + Table1 + Fig1 真实可跑，但 Table2-5 是 esttab 占位、缺 manuscript/refs.bib、部分缺面板处理列。
3. **规划骨架**（`exogenous_shocks.yaml` DiD 事件库 / `pipeline_v34_rerun.yaml` 重跑预算 / 2 个归档模板 / `radius_sensitivity_llm` LLM 升级路径）：自标 skeleton，受 T=2 面板深度或 M0 付费 gate 约束，待未来实施。

---

## 五、可执行行动清单

### A. 可立即安全删除（零配套改动）
- [ ] `data/processed/39g_track_discriminant_validity.json`（gitignored 陈旧 json）
- [ ] `data/processed/30_text2vec_indicators.csv`（全仓零引用）
- [ ] 备份目录里的 `16_epu_panel.parquet`（仅存于 `data/processed_bak_*` 快照）

### B. 需先做配套清理再删
- [ ] `data/processed/30_text2vec_indicators.parquet` —— 先从 golden 三处移除并重生 golden，再删

### C. 别删，要"补完/修复"（对抗复核推翻的）
- [ ] `llm_contamination_test.py` —— 补 shim + 注册 STAGES_VALIDATION + 接 stage 49（DC4 必修，2篇 spec 已承诺）
- [ ] **修 stale title 崩溃隐患** —— 守卫/移除 `falsification_template.do.tmpl:126` 的 `prob_gap_title_full` 回归 + `stata/05_label_advanced.do:66` + 重生 codebook 去幻影行
- [ ] `_title` 迁移脚本 —— 归档（provenance，勿删）

### D. 标注"待补完"，按 roadmap 推进（不动代码）
- opt-in 17/19/49、provisional 3 篇、`exogenous_shocks.yaml`/`pipeline_v34_rerun.yaml`、2 个归档模板、`radius_sensitivity_llm`

### E. 顺手可提质（非必须）
- 补 `30a_article_sbert` / `39e` / `stata_export 标签链` 的独立单元测试（当前仅 DAG 间接覆盖）
- 清理 `core/stage.py` docstring 里"Phase 3 Stage ABC"未兑现蓝图注释（run_stage 本体活跃，仅注释陈旧）
