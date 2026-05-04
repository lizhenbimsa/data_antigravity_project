# `OUTPUT_REGISTRY` — 阶段输出文件单源真值

`news_process.core.schemas.OUTPUT_REGISTRY` 是流水线**所有 stage** 的
parquet 输出文件名的**单源映射**。orchestrator 在每个 stage 启动前用它
预清理陈旧输出（防止失败阶段的旧数据污染下游）。

## 1. 数据结构

```python
# news_process/core/schemas.py
OUTPUT_REGISTRY: dict[str, list[str]] = {
    '00_preprocessing.py': ['00_preprocessing.parquet'],
    '11_news_bank.py': ['11_bank_news.parquet'],
    '12_news_fintech.py': ['12_fintech_news.parquet',
                           '12_fintech_news_full.parquet'],
    '14_fintech_intensity.py': ['14_fintech_intensity.parquet'],
    '15_article_policy_alignment.py': ['15_article_alignment.parquet'],
    '21_tone_llms.py': ['21_tone_llms.parquet',
                        '21_tone_llms_full.parquet'],
    '22_tone_words.py': ['22_words_tone.parquet'],
    '23_tone_berts.py': ['23_bert_tone.parquet'],
    '24_herd_decay_processor.py': ['24_herd_decay.parquet'],
    '45_panel_export_main.py': [
        '40_panel_yearly.parquet',
        '40_article_bank_level.parquet',
        '40_attn_index_year.parquet',
        '40_attn_index_province_year.parquet',
        '40_attn_index_city_year.parquet',
    ],
    '51_falsification_test.py': ['51_panel_with_controls.parquet'],
}
```

* **Key** = stage script 文件名（与 `StageSpec.script` 完全对应）
* **Value** = 该 stage 写出的 parquet 文件列表（相对 `output_dir`）

## 2. 公开 API

### `get_stage_outputs(script_name)`

```python
from news_process.core.schemas import get_stage_outputs

# 返回该 stage 的输出文件名列表
files = get_stage_outputs('11_news_bank.py')
# → ['11_bank_news.parquet']

# 找不到时返回 []
files = get_stage_outputs('99_unknown.py')
# → []
```

orchestrator 用它做**预清理**：

```python
# news_process/run_pipeline_function.py:_get_stage_output_files()
def _get_stage_output_files(stage_script: str) -> list:
    from news_process.core.schemas import get_stage_outputs
    files = get_stage_outputs(stage_script)
    # 找不到 → 回退本地 legacy mapping（safety net）
    return files

# 在 stage 启动前预清理：
output_files = _get_stage_output_files(script)
for filename in output_files:
    output_path = os.path.join(CONFIG['paths']['output_dir'], filename)
    if os.path.exists(output_path):
        os.remove(output_path)
```

## 3. 设计动机

### 3a. 防止陈旧数据污染下游

如果阶段 21 失败但残留旧的 `21_tone_llms.parquet`，阶段 24 仍会读取它，
基于错误的中间数据继续执行 → 隐蔽 bug。

**解决**：每个 stage 启动前预清理自己的输出，确保上游必须重新执行。

### 3b. 单源映射，避免重复硬编码

旧版本（v1.x）这个映射散落在多个地方：
* `run_pipeline_function.py` 内联 dict
* `tests/integration/test_panel_reproducibility.py` 内联 list
* 各 stage 自己的 `output_path` 拼接

任何变更（如阶段 12 新增 `_full` 输出）需要在 3+ 处同步修改，极易遗漏。

**v2.0 解决**：`OUTPUT_REGISTRY` 单源；orchestrator 通过 `get_stage_outputs()`
查询；测试也走同一 API。

## 4. Legacy fallback

`run_pipeline_function.py` 中保留了一份 legacy mapping 作为 safety net：

```python
def _get_stage_output_files(stage_script: str) -> list:
    files = _registry_outputs(stage_script)
    if files:
        return files

    # Legacy fallback (preserved verbatim — Phase 2d deprecation safety net).
    stage_num = stage_script.split('_')[0]
    output_map = {
        '00': ['00_preprocessing.parquet'],
        '11': ['11_bank_news.parquet'],
        # ...
    }
    return output_map.get(stage_num, [])
```

正常情况下 registry 命中，legacy fallback 不可达。但保留它防止 registry
未注册的新 stage 完全失去预清理保护。

## 5. 添加新 stage 的输出注册

详见 [新增 Stage 指南 §Step 5](../guides/adding_stage.md)。简言之：

```python
# news_process/core/schemas.py
OUTPUT_REGISTRY: dict[str, list[str]] = {
    # ... 已有 ...
    '25_aspect_based.py': ['25_aspect_based.parquet'],   # ← 新加
}
```

如果新 stage 写出多个文件（如 `_full` + 主输出），都列出来：

```python
'25_aspect_based.py': [
    '25_aspect_based.parquet',
    '25_aspect_based_full.parquet',
],
```

## 6. 关于 validation 阶段

`OUTPUT_REGISTRY` 当前**仅覆盖主流水线**（`STAGES_MAIN` 11 阶段）。验证
阶段（`STAGES_VALIDATION`）输出大多是 `eval_reports/<...>` 子目录下的
csv/png/tex/json，每个 stage 输出文件多达几十个，不适合统一注册。

验证阶段不做预清理 — 旧 eval_reports 文件被新文件直接覆盖，无副作用。

## 7. 关于 dta / csv 副本

`40_panel_yearly.dta` 与 `40_panel_yearly.csv` 是 `40_panel_yearly.parquet`
的同步导出副本，不在 `OUTPUT_REGISTRY` 中。理由：
* 它们是 panel.export 内部一次性写入的，不会单独失败
* 删除它们而保留 .parquet 不会破坏下游
* 预清理 .parquet 即可，dta/csv 自然在下次跑时一起重写

## 8. 测试

`OUTPUT_REGISTRY` 的正确性由 `tests/integration/test_panel_reproducibility.py`
间接保证 — 该测试断言每个 registered stage 的输出在磁盘上**存在**且
列 hash 与 golden snapshot 一致。

```bash
.venv/Scripts/python.exe -m pytest \
    news_process/tests/integration/test_panel_reproducibility.py -v
```

## 9. 见也

* [`core.schemas` API 参考](../api/core.md)
* [`StageSpec` 参考](dag.md)
* [新增 Stage 指南](../guides/adding_stage.md)
