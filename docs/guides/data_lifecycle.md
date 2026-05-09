# 数据目录生命周期

> Plan P2-10 (2026-05-09) 交付:明确 `news_process/data/` 与
> `news_process/data_excel/` 下各子目录的来源、保留策略、清理时机,
> 让历史快照不再"无主"占用磁盘。

本文档与 [`docs/architecture.md`](../architecture.md) 互补:架构文档讲数据
*流*,本文档讲数据 *存*。

---

## 1. 一览表

| 路径 | 体量 (HEAD 实测) | 类别 | 谁产生 | 保留策略 | 清理触发条件 |
|------|----------------|------|--------|----------|--------------|
| `data_excel/wisers_*.xlsx` | ~MB,3 个文件 | **生产输入** | 人工从 Wisers 平台下载 | 永久保留(stage 00 唯一输入源) | 永不清理(版本由文件名时间戳隐式表达) |
| `data_excel/back/` | 43 GB,176 个文件 | **历史输入备份** | 人工归档(每次 Wisers 重抓时主目录搬入) | 截止一篇 paper 提交且接收后, 至少保留至下一次 *主目录* 数据冻结 | 主目录新一批数据通过 stage 00 + sanity check 后,可整目录搬走/删除(见 §3) |
| `data/processed/00_*.parquet` ~ `45_*.parquet` 等主输出 | ~9.4 GB | **管线产出** | stage 00-51 的 parquet/dta/csv 输出 | 滚动覆盖(每次 `run_pipeline_function.py` 重写) | 上游 stage 重跑时由 OUTPUT_REGISTRY 驱动的预清理自动清掉 |
| `data/processed/_backup_pre_issue5_fix_v6/` | 99 MB | **数据修复回滚锚点** | issue #5 调查阶段人工 `cp -r data/processed → _backup_*` 保留旧结果以便对照 | 修复 commit merge 后保留 1 个 release 周期 | issue #5 在 v2.1.0 已修复, 可在 v3.0 release 一并清除 |
| `data/processed/_cache/` | 由 stage 21/15/27 LLM/Embedding API 产生 | **缓存** | LLM 与 Embedding API 调用的批量缓冲(batch processing 中间态) | 滚动覆盖,不参与 reproducibility 契约 | 任意时刻可整目录删除,下次跑会重建(代价:重新调 API) |
| `data/processed/_llm_cache.db` | SQLite,容量随调用次数增长 | **LLM 请求级缓存** | `news_process.core.caching.LLMCache`(prompt+model_id → response) | 跨 release 保留,因为 prompt 改动会自动失效 cache key(prompt 文本变 → SHA256 变) | 仅在 `temperature` / `force_json` 等非-prompt 参数变更时手动整库清空 |

---

## 2. 命名约定

- `data_excel/`(无后缀) - **当前活跃** 的 Wisers 原始数据。
- `data_excel/back/` - **已归档** 的历史 Wisers 数据,只读访问。
- `data/processed/` - 当前活跃的管线产出。
- `data/processed/_backup_<reason>/` - 一次性数据修复锚点;`<reason>` 须含 issue 号或 PR 号。
- `data/processed/_cache/` - 临时缓冲;以 `_` 开头的目录意为 "可被工具自动清理"。
- `data/processed/_<filename>.db` - 持久化缓存;以 `_` 开头的文件意为 "非管线产出"。

---

## 3. 主输入数据(`data_excel/`)迁移流程

当 Wisers 重抓数据需要替换 `data_excel/wisers_*.xlsx` 时,执行:

```bash
# 1. 把当前活跃数据搬到归档
cd news_process/data_excel
mkdir -p back/
mv wisers_*.xlsx back/

# 2. 解压新一批数据到当前目录
unzip ~/Downloads/new_wisers.zip -d .

# 3. 跑一次 stage 00 sanity check
cd ..
python run_pipeline_function.py  # 仅 stage 00 必跑通; 其它失败先排查 stage 00 输出
```

**清理时机**:
- 不要 在 stage 00 sanity check 通过当天清理 `back/`
- 等到至少一篇基于新数据的 paper 走完 R&R(或被 desk reject)后再清理
- 清理时整目录 `rm -rf data_excel/back/<old_batch>/`,而不是逐文件

**复盘风险**:任何"跑了一半发现新一批数据有 bug,要回滚到旧一批" 的场景,
都依赖 `back/` 的存在,建议保留 ≥6 个月。

---

## 4. 管线产出(`data/processed/`)清理

### 4.1 主输出文件 (00_*, 11_*, ..., 51_*)

由 [`news_process/core/schemas.py`](../../news_process/core/schemas.py) 中
`OUTPUT_REGISTRY` 单源管理,每个 stage 重跑前由
[`run_pipeline_function.py`](../../news_process/run_pipeline_function.py)
预清理对应文件,无需用户介入。

如需 **强制全量重跑**:

```bash
cd news_process/data/processed
# 仅删主输出, 保留 _cache 与 _llm_cache.db (省 LLM 调用费)
rm -f [0-9]*.parquet [0-9]*.csv [0-9]*.dta
cd ..
python run_pipeline_function.py
```

### 4.2 同 stage 多格式产出 (parquet + csv + dta)

- `parquet`:Python 读取(stage 间默认)
- `dta`:Stata 读取(`papers_assets/<id>/do/*.do` 用)
- `csv`:仅历史兼容 + 人眼检查;**未来 v3.0 将默认关闭 csv 输出**(见
  [thin_shim_pattern.md](thin_shim_pattern.md) 末尾的 v3.0 路线)

如需当前节省磁盘,可手动:

```bash
cd news_process/data/processed
rm -f *.csv  # 删除全部 csv (parquet + dta 仍保留)
```

下次重跑会重新生成 csv;如需永久关闭,改 `core/reporting.py:save_dataset()`
里的 `formats=` 默认值。

### 4.3 `_backup_pre_issue5_fix_v6/` 的处置

此目录是 v6 issue #5 调查时的快照,issue 在 v2.1.0 已 close。

**清理时机**:在打 v3.0 tag 前的最后一个 prep commit 中删除,
commit message 写明"v3.0 release 前清理 v2.x 数据修复回滚锚点"。

```bash
# v3.0 release prep 阶段执行
cd news_process/data/processed
git rm -r _backup_pre_issue5_fix_v6/  # 不在 git 中, rm -rf 即可
```

### 4.4 `_cache/` 与 `_llm_cache.db`

- `_cache/` 任意时刻可清(代价:下次跑会重新调 API)
- `_llm_cache.db` 不建议清,因为重跑成本极高(stage 21 单次冷缓存 ~7200 秒)。
  仅在以下场景手动 truncate:
  - `temperature` / `force_json` / `top_p` 等 *非 prompt* 调用参数发生变化
    (因为 [`core/caching.py:_make_key`](../../news_process/core/caching.py)
    只哈希 `(model_id, prompt)`,这些参数变化时 cache key 不会自动失效)
  - LLM provider 升级了模型权重但 model_id 字符串不变
  - 怀疑 cache 被污染(API 返回过 garbled 内容并被错误持久化)

---

## 5. v3.0 子目录分层蓝图(暂不实施)

未来若需要把 `data/processed/` 进一步分层,推荐结构:

```
news_process/data/
├── processed/        # 当前管线产出 (滚动覆盖)
├── snapshots/        # 历史回滚锚点 (现 _backup_* 搬入此处)
├── cache/            # 当前 _cache/ 搬入此处
└── exports/          # Stata .dta、CSV 等次生格式 (现混在 processed/)
```

但此举会让 `CONFIG['filenames']` 携带子目录前缀,跨阶段交叉读取时增加耦合,
违反 DRY,因此暂不实施(见 [README.md §7](../../README.md))。

---

## 6. .gitignore 状态

```
news_process/data/        # 整个 data 目录 gitignored
news_process/data_excel/  # 整个 data_excel 目录 gitignored (含 back/)
```

任何修改 [`news_process/.gitignore`](../../news_process/.gitignore) 让某些
processed 文件可被 commit 的 PR,reviewer 必须确认这些文件不会膨胀仓库
(>10 MB) 与不含 PII / API key。

---

## 7. 自动化清理工具 (Plan-r3 P3-15)

二轮诊断核验时实测 `data/processed/` **9.4 GiB**（远超此前估算的 1 GiB），
但本仓库一直无配套清理工具。Plan-r3 P3-15 落地后提供两套等价工具：

### 7.1 Makefile target（Linux / WSL / mingw32-make）

```bash
make help            # 列出全部 target
make sizes           # 显示各 cleanup target 当前可释放体积
make clean-cache     # 删 _cache/ + _llm_cache.db          (~236 MiB; LLM 缓存归零)
make clean-backup    # 删 _backup_*/                        (~99 MiB; 仅在 release 后执行)
make clean-derived   # 删 stage 14+ parquet/csv/dta         (保留 stage 11/12 上游)
make clean-logs      # 清空 news_process/logs/
make purge-all       # 上述全部 + logs                       (DANGER: 完全重置)
```

### 7.2 纯 Python 版（Windows 友好，无 make 依赖）

```bash
python -m news_process.scripts.cleanup sizes
python -m news_process.scripts.cleanup clean-cache
python -m news_process.scripts.cleanup clean-backup
python -m news_process.scripts.cleanup clean-derived
python -m news_process.scripts.cleanup clean-logs
python -m news_process.scripts.cleanup purge-all --yes
```

两套工具行为等价（Makefile target 内部即调 Python 单行 inline），输出格式一致。
源码: [`news_process/scripts/cleanup.py`](../../news_process/scripts/cleanup.py)、
项目根 [`Makefile`](../../Makefile)。

### 7.3 推荐使用频率

| 操作 | 触发场景 | 频率 |
|---|---|---|
| `clean-cache` | LLM prompt 模板有变更 / 想验证 cache 命中率改进 | 周级 |
| `clean-derived` | 上游 stage 11/12 数据重抓 | 月级（每次 wisers 重抓时） |
| `clean-backup` | issue 已 release 后 | release 级（v3.0 时清 issue #5 backup） |
| `purge-all` | 仅在完全重置开发环境时（极少） | 年级 |
