# company_listed_bank — 银企共现面板生产流水线

上市公司×年 银企共现媒体报道面板 (105,032 行) 的三步生产脚本。
权威执行计划 = `scripts/audit/COMPANY_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-03.md` (v34)。

## 执行顺序 (序号即顺序, 不可颠倒)

| 步骤 | 脚本 | 消费 | 产出 |
|---|---|---|---|
| 01 | `01_build_company_bank_cooc_registry.py` (WP0) | 五上游 parquet 列名 + 裁剪负清单 + 两名单 SSOT | `config/company_bank_cooc_registry.yaml` (加权引擎唯一 SSOT) |
| 02 | `02_build_company_bank_cooc_panel.py` (WP1) | **01 的 registry yaml** (启动校验哈希锚, 缺则不跑) | 主面板 dta/parquet + codebook + `_company_bank_cooc_pairs.parquet` (pair 长表) |
| 03 | `03_build_company_bank_weight_validation.py` (WP5) | **01 的 registry yaml** (DV2 常量双向锁) + **02 的 pair 长表** (缺则 `SystemExit`: "无锚即无互验") | 七替代权长表 + 七权面板 ×7 + 互验报告 |

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

gate 测试: `tests/test_company_bank_cooc_registry.py` (11) +
`tests/test_company_bank_cooc_panel.py` (34) + `tests/test_company_bank_weight_validation.py` (51+2)。

⚠ 生产 T=18 复跑注意 (计划 §9.4 DEFERRED): registry 哈希锚锚死盘上态, 有意重跑 01 后须
bump `tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256` 并级联重跑 02 (pair
指纹)→03 (双向锁); 四权源商业 dta (`config/*.dta`) 恒不入库。
