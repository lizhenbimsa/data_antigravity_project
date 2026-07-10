# company_listed_bank — 银企共现面板生产流水线

上市公司×年 银企共现媒体报道面板 (105,032 行) 的三步生产脚本。
权威执行计划 = `scripts/audit/COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03.md` (v34)。

## 执行顺序 (序号即顺序, 不可颠倒)

| 步骤 | 脚本 | 消费 | 产出 |
|---|---|---|---|
| 01 | `01_build_company_bank_cooc_registry.py` (WP0) | 五上游 parquet 列名 + 裁剪负清单 + 两名单 SSOT | `config/company_bank_cooc_registry.yaml` (加权引擎唯一 SSOT) |
| 02 | `02_build_company_bank_cooc_panel.py` (WP1) | **01 的 registry yaml** (启动复算并校验哈希锚 — canonical 式经 importlib 复用 01 的 `registry_content_sha256`; 缺/不自洽则不跑) | 主面板 dta/parquet + codebook + `_company_bank_cooc_pairs.parquet` (pair 长表) |
| 03 | `03_build_company_bank_weight_validation.py` (WP5) | **01 的 registry yaml** (DV2 常量双向锁, 缺区段即拒) + **02 的 pair 长表** (缺文件/缺内嵌指纹/指纹 stale 均 `SystemExit`: "无锚即无互验") | 七替代权长表 + 七权面板 ×7 + 互验报告 |

顺序为硬依赖 (fail-loud 闸), 非约定: 02 缺 registry / 03 缺 pair 长表均直接退出。

## 目录布局 (日志与产物)

- `logs/` — 各脚本运行日志 `<脚本名>.log` (含 `run_pipeline.log`)。复用主管道日志基建
  (`core/logging.py::setup_logging`): 格式 `时间 - 名称 - PID - 级别 - 消息`、每次运行覆盖
  只留最新、50MB rotate — 与 `news_process/logs/` 各阶段日志完全一致。整目录 gitignore。
- `data/` — 02/03 的全部数据产物 (主面板/pair 长表/codebook/七权长表/七权面板/互验报告,
  共 26 文件 ≈13GB)。整目录 gitignore (镜像 `data/processed` 不入库惯例)。
- 例外: 01 的产物 registry yaml 落 `config/` — 它是入库 SSOT (02/03 与 gate 测试的消费锚),
  属配置而非数据结果。
- 上游输入不变: 五上游 parquet 仍从 `data/processed/` 读取 (只读), 四权源商业 dta 在 `config/`。

## 模块 import 说明

- 序号前缀 (`01_` 等) 非合法 Python import 语句标识符, 跨脚本复用一律
  `importlib.import_module("0X_...")` (01→03 取 DV2 常量落 registry 区段; 03→02 复用
  SSOT 双函数 `build_measure_library`/`compute_weighted_panel`, 禁第二份实现)。
- 模块依赖方向 (01 import 03 的常量) 与执行顺序无关 — 常量在 import 时可得, 产物才分先后。

## 运行 (从 news_process/ 目录, conda base python)

一键全链 (orchestrator, 子进程隔离 + fail-loud 中断 + 计时):

```bash
python company_listed_bank/run_pipeline.py               # 全链 01→02→03
python company_listed_bank/run_pipeline.py --steps 02,03 # registry 已就绪时从 02 起
python company_listed_bank/run_pipeline.py --dry-run     # 只打印将执行的命令
```

或逐步手跑:

```bash
python company_listed_bank/01_build_company_bank_cooc_registry.py
python company_listed_bank/02_build_company_bank_cooc_panel.py
python company_listed_bank/03_build_company_bank_weight_validation.py
```

gate 测试四件 (pytest 收集实数, 增删测试后以 `--collect-only -q` 为准同步此处与各脚本 banner):
`tests/test_company_bank_cooc_registry.py` (12) + `tests/test_company_bank_cooc_panel.py` (58) +
`tests/test_company_bank_weight_validation.py` (54) + `tests/test_company_bank_run_pipeline_lock.py` (5) = 129。

⚠ 生产 T=18 复跑注意 (计划 §9.4 DEFERRED): registry 哈希锚锚死盘上态, 有意重跑 01 后须
bump `tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256` 并级联重跑 02 (pair
指纹)→03 (双向锁); 四权源商业 dta (`config/*.dta`) 恒不入库。

## 与主管道的顺序 / 并发纪律 (F2/F7/F9, 2026-07-10 五入口再验证)

- **cross_media 顺序耦合 (F2)**: 本管线 02 消费主管道 `data/processed/40_panel_yearly.parquet`。若主管道按自然
  顺序 `run_pipeline_function → run_pipeline_validation` 跑, 则 stage40 (group=main) 建面板时 stage75
  (`75_cross_media_alpha`, group=validation) **恒晚于**刚重生的 stage21 → `pipeline/panel/runner.py` 的 mtime
  新鲜度守卫**恒跳过** cross_media merge → 40 面板缺 `cross_media_alpha`/`cross_outlet_tone_variance`/`n_events`
  三基名源列 → 本管线 registry 对该三基名 emit_tracks=[] **不产对应加权列 (0 列, 非全 NaN; 与 02 日志 F3 拆因一致)** (非 bug, 非 T=18 可恢复; 标准/生产顺序皆恒缺)。
  **需含 cross_media 的完整面板**须走: `① function → ② validation → ③ 单独补跑 python 40_panel_export_main.py
  (不重跑 21, 使 75 相对 21 新鲜) → ④ 本管线`, 或主管道传 `--skip-21-if-exists`。
- **跨管道串行纪律 (F7)**: 本管线单实例锁 (`logs/_run_pipeline.lock`) 只防同目录 orchestrator 双跑, **与主管道
  PipelineLock (`data/processed/.pipeline.lock`) 互不感知**。本管线 02/03 只读 `data/processed/`, 而主管道收尾有
  os.remove + 非原子重写窗口 → **务必在主管道空闲时运行本管线** (否则可能读到预清理/重写窗口的半写/缺文件,
  诊断中曾遇 WinError 2)。listed × tax 两派生管线之间可并发 (各写自有 `data/`, 仅只读 `data/processed`)。
- **--skip-unchanged 盲区 (F9)**: 主管道以 `--skip-unchanged` 重跑时 stage40 可能被跳过 (75 不在其 input_hashes
  追踪集), cross_media/staleness 等 opt-in 特征列会保留旧/缺值 — 需这些列时勿配该 flag, 或先单独重跑 stage40。
