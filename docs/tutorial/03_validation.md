# 跑验证模块矩阵

`run_pipeline_validation.py` 编排 12 个稳健性检验 / 三角验证 / 敏感性
分析阶段（`STAGES_VALIDATION`），是论文 Appendix 的标准产出来源。

## 1. 何时跑

* 主流水线（`run_pipeline_function.py`）已成功完成
* 想为论文 Appendix 生成稳健性 / 敏感性检验表与图
* 审稿人提出方法论质疑（"阈值是否敏感？" / "前视偏误？" / "Prompt 措辞？"）

```{warning}
验证模块**依赖**主流水线产出（特别是 `21_tone_llms.parquet`、
`40_panel_yearly.parquet`），先跑主线，否则各 validation 阶段会
因找不到输入文件直接 skip。
```

## 2. 验证矩阵全景

```{mermaid}
graph TB
    subgraph "敏感性 (Sensitivity)"
        S31[阶段 31<br/>threshold]
        S32A[阶段 32a<br/>dedup_threshold]
        S35[阶段 35<br/>radius_sensitivity]
        S38B[阶段 38b<br/>decay_sensitivity]
        S39[阶段 39<br/>prompt_sensitivity]
    end

    subgraph "三角验证 (Triangulation)"
        S33[阶段 33<br/>llms_evaluation]
        S34[阶段 34<br/>tone_validation]
    end

    subgraph "稳健性 (Robustness)"
        S30[阶段 30<br/>text2vec]
        S36[阶段 36<br/>entity_masking]
        S38A[阶段 38a<br/>temporal_mask]
    end

    subgraph "审计 (Audit)"
        S32[阶段 32<br/>llms_human]
        S37[阶段 37<br/>dict_coverage]
        S38[阶段 38<br/>media_diversity]
    end
```

## 3. 启动

```bash
# 跑全部 validation（默认）
.venv/Scripts/python.exe news_process/run_pipeline_validation.py
```

跑特定子集：编辑 `news_process/config/validation.yaml`，把不需要的开关
设为 `false`：

```yaml
validation:
  threshold_sensitivity: true
  dedup_sensitivity: true
  classification_eval: true
  sentiment_validation: true
  radius_sensitivity: false   # 跳过 35
  entity_masking: true
  dict_coverage_audit: true
  media_diversity: true
  prompt_sensitivity: false   # 跳过 39（耗时最长）
```

```{note}
**`38a_temporal_mask` 单独控制**：受 `temporal_mask_test.enabled` 控制
（默认 `false`），不在 `validation.*` 集合内。
**`32_news_llms_human` 与 `38b_decay_sensitivity`**：始终启用，无开关。
```

## 4. 输出 inventory

| 阶段 | 主输出 | 用途 |
|---|---|---|
| 30 | `data/processed/eval_reports/30_*.csv` | text2vec 相似度对照表 |
| 31 | `eval_reports/31_*.csv/png/tex` | 阈值网格搜索热图 + LaTeX |
| 32 | `data/processed/32_human_samples.xlsx` | 分层抽样人工标注样本 |
| 32a | `eval_reports/dedup_sensitivity_report.csv` | 去重阈值敏感性表 |
| 33 | `eval_reports/classification_eval_*.{csv,json,tex}` | Cohen's κ + Krippendorff's α |
| 33 | `eval_reports/cm_*.png` | 混淆矩阵热图 |
| 34 | `eval_reports/cronbachs_alpha_*.csv` | 三方法情感一致性 |
| 34 | `eval_reports/heatmap_{cross,within}_*.png` | 三方法相关热图 |
| 35 | `data/processed/35_radius_*.{json,tex,png}` | 窗口半径敏感性曲线 |
| 36 | `eval_reports/entity_masking_*.{csv,json,tex,png}` | 掩码前后情感对比 |
| 37 | `eval_reports/37_*.csv` + `eval_reports/coverage_distribution.csv` | 词典覆盖率 + Wilson CI |
| 38 | `data/processed/eval_reports/38_media_diversity.xlsx` | HHI / Shannon / Gini |
| 38a | `data/processed/temporal_mask_diagnostics_*.csv` | 时间掩码前视偏误 |
| 38b | `eval_reports/38b_decay_sensitivity.csv` | 衰减权重敏感性 |
| 39 | `eval_reports/prompt_sensitivity_*.{json,png,tex}` | Fleiss kappa + 措辞变体表 |

## 5. 跑时估算

| 阶段 | 主因 | 跑时（参考） |
|---|---|---|
| 30/31/32a/35/37/38/38b | 纯计算（pandas / scikit-learn） | 数分钟 |
| 32 | 人工抽样生成（无 API） | < 1 分钟 |
| 33/34 | Cohen's κ / Cronbach's α 计算 | 数分钟 |
| 36 | 实体掩码 + LLM 重新标注（**需 API 配额**） | 数小时 |
| 38a | 多次时间窗口 LLM 重新标注（**最贵**） | 数小时-1 天 |
| 39 | 多个 prompt 变体的 LLM 重新标注（**贵**） | 数小时 |

```{tip}
**首次跑**先把 36/38a/39 关掉，让前 9 个稳健性检验快速完成；确认
逻辑无误后再开 LLM 密集型的 3 个。
```

## 6. 解读输出（论文写作角度）

### 阈值敏感性（31）→ 论文 Appendix 表

`31_threshold` 输出阈值 grid search，论文 Appendix 用："我们在
[0.1, 0.2, 0.3, 0.4, 0.5] 上做敏感性检验，结果见表 A.X，发现核心系数符号
和显著性在所有阈值下保持稳定。"

### 三角验证（34）→ 论文方法节

`34_tone_validation` 输出词典 / BERT / LLM 三方法的 Cronbach's α。
论文方法节："情感测度采用三方法三角验证（Denzin 1978），词典法 / BERT /
LLM 间 Cronbach's α 为 0.78，超过 0.70 学术接受阈值。"

### 实体掩码（36）→ 论文稳健性节

`36_entity_masking` 输出掩码前后的情感判定一致率。论文："为排除 LLM
基于实体先验做出判定的可能（Carlson & Burbano 2026, SMJ），我们做实体
掩码稳健性测试，发现掩码前后一致率为 92%，证明情感判定主要依赖语义内容
而非实体先验。"

### Prompt 措辞敏感度（39）→ 论文方法节

`39_prompt_sensitivity` 输出 V0 baseline + V1...V8 措辞变体的 Fleiss kappa。
论文："我们设计 V0 baseline + 8 个措辞变体（角色改写 / 任务结构变换 /
评分尺度变换等），变体间 Fleiss κ = 0.73 > 0.667，证明 LLM 标注对
prompt 措辞具有稳健性。"

## 7. 故障排查

| 症状 | 处理 |
|---|---|
| 阶段 36 大量 timeout | 同主流水线 21 阶段：调低 `entity_masking_test.max_concurrency` |
| 阶段 39 OOM (大型 prompt 表) | 调小 `prompt_sensitivity_test.sample_size`（默认 1000） |
| `eval_reports/` 不存在 | 主流水线未跑或路径不对，先验证 `data/processed/40_panel_yearly.parquet` 存在 |

## 8. 下一步

* [Stata 集成](05_stata_integration.md) — 把 `40_panel_yearly.dta` 拉进 Stata
* [新增 Validation 模块指南](../guides/adding_stage.md) — 自定义新的稳健性检验
