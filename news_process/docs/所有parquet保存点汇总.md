# 所有Parquet保存点汇总

基于代码搜索，找到以下保存点：

## 方式1：直接使用 `.to_parquet()`（7个调用点）

1. `pipeline/filtering/news_bank.py:438`
2. `pipeline/filtering/news_fintech.py:300` (full版本)
3. `pipeline/filtering/news_fintech.py:315` (filtered版本)
4. `pipeline/sentiment/tone_words.py:1156`
5. `pipeline/sentiment/tone_berts.py:782`
6. `pipeline/sentiment/herd_decay.py:279`
7. `pipeline/panel/attention_media.py:381`

## 方式2：使用 `save_dataset()` 封装函数（10个调用点）

`save_dataset()` 内部调用 `.to_parquet()`（在 `core/reporting.py:58`）

1. `pipeline/preprocess/runner.py` - 使用 ParquetWriter（特殊情况）
2. `pipeline/filtering/fintech_intensity.py:372` - save_dataset
3. `pipeline/filtering/policy_alignment.py:587` - save_dataset
4. `pipeline/sentiment/tone_llms.py:829` - save_dataset (第1个输出)
5. `pipeline/sentiment/tone_llms.py:1047` - save_dataset (full版本)
6. `pipeline/sentiment/tone_llms.py:1240` - save_dataset (filtered版本)
7. `pipeline/panel/export.py:243` - save_dataset (panel)
8. `pipeline/panel/export.py:1031` - save_dataset (article)
9. `pipeline/falsification/controls.py:793` - save_dataset
10. `validation/text2vec.py:249` - save_dataset

## 总计

- **直接 `.to_parquet()`**: 7个调用点
- **通过 `save_dataset()`**: 10个调用点
- **特殊情况（ParquetWriter）**: 1个
- **总计**: 18个保存点需要集成数据版本控制

## 对应的阶段

| 阶段 | 文件 | 方法 | 输出文件 |
|------|------|------|---------|
| 00 | preprocess/runner.py | ParquetWriter | 00_preprocessing.parquet |
| 11 | filtering/news_bank.py | .to_parquet() | 11_bank_news.parquet |
| 12 | filtering/news_fintech.py | .to_parquet() x2 | 12_fintech_news.parquet + full |
| 14 | filtering/fintech_intensity.py | save_dataset | 14_fintech_intensity.parquet |
| 15 | filtering/policy_alignment.py | save_dataset | 15_article_alignment.parquet |
| 21 | sentiment/tone_llms.py | save_dataset x3 | 21_tone_llms.parquet + full |
| 22 | sentiment/tone_words.py | .to_parquet() | 22_words_tone.parquet |
| 23 | sentiment/tone_berts.py | .to_parquet() | 23_bert_tone.parquet |
| 24 | sentiment/herd_decay.py | .to_parquet() | 24_herd_decay.parquet |
| 30 | validation/text2vec.py | save_dataset | 30_text2vec_indicators.parquet |
| 45 | panel/export.py | save_dataset x2 | 40_panel_yearly.parquet + article |
| 45 | panel/attention_media.py | .to_parquet() | 其他panel输出 |
| 51 | falsification/controls.py | save_dataset | 51_panel_with_controls.parquet |

## 集成策略

### 策略A：修改 `save_dataset()` 函数（推荐）

**优点**：
- 只需修改1个函数（`core/reporting.py:save_dataset`）
- 自动覆盖10个调用点
- 代码改动最小

**缺点**：
- 需要传递额外参数（stage_name, config, input_files）到所有调用点
- 可能影响函数签名

### 策略B：逐个替换所有调用点

**优点**：
- 每个调用点都明确控制
- 不影响现有函数签名

**缺点**：
- 需要修改18个位置
- 工作量大
- 容易遗漏

### 策略C：混合策略（最佳）

1. **修改 `save_dataset()` 函数**，添加可选参数
2. **直接替换7个 `.to_parquet()` 调用**
3. **更新10个 `save_dataset()` 调用点**，传入新参数

**优点**：
- 平衡了工作量和灵活性
- 向后兼容（可选参数）
- 覆盖所有保存点

## 建议

采用**策略C（混合策略）**：

1. 修改 `core/reporting.py:save_dataset()`，添加可选参数
2. 修改7个直接 `.to_parquet()` 调用
3. 修改10个 `save_dataset()` 调用点
4. 特殊处理 `preprocess/runner.py` 的 ParquetWriter

**预计工作量**: 4-5小时
