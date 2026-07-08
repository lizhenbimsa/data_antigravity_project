# company_tax_bank — 税调企业—银行共现面板生产流水线

税调企业×年 银企共现媒体报道面板 (447,710 行 = 44,771 家税调企业 × 10 年 2011–2020) 的三步生产脚本。
面板与外部数据 merge 键 = **`usci × year`** (18 位统一社会信用代码, 全填全唯一; `company_tax_name × year`
为等价备用键)。产出**三个互为稳健性的权重** (共现报道权 + 城市网点权 + 县域网点权, 不分主次)。
权威执行计划 = `scripts/audit/COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08.md` (v7)。

与姊妹管线 `company_listed_bank/` 完全隔离 (零字节交集); 唯一交集 = 02/03 只读 import 其加权引擎 (见下)。

## 执行顺序 (序号即顺序, 不可颠倒)

| 步骤 | 脚本 | 消费 | 产出 |
|---|---|---|---|
| 01 | `01_build_company_tax_bank_cooc_registry.py` (WP0) | 五上游 parquet 列名 + 裁剪负清单 + 税调名单 SSOT (`config/company_tax_names.yaml`) + 银行清单 | `config/company_tax_bank_cooc_registry.yaml` (加权引擎唯一 SSOT) |
| 02 | `02_build_company_tax_bank_cooc_panel.py` (WP1) | **01 的 registry yaml** (启动复算并校验哈希锚 — canonical 式经 importlib 复用 01 的 `registry_content_sha256`; 缺/不自洽则不跑) | 主面板 dta/parquet (20 固定列 [含 usci] + 加权列) + codebook + `_company_tax_bank_cooc_pairs.parquet` (pair 长表) |
| 03 | `03_build_company_tax_bank_weight_validation.py` (WP5) | **01 的 registry yaml** (DV2 常量双向锁, 缺区段即拒) + **02 的 pair 长表** (缺文件/缺内嵌指纹/指纹 stale 均 `SystemExit`: "无锚即无互验") + `config/银行业金融机构基本信息表.dta` (城市/县域两层级网点权源) | 双替代权长表 ×2 (`branch_city`/`branch_county`) + 双权面板 ×2 + 三权互验报告 |

顺序为硬依赖 (fail-loud 闸), 非约定: 02 缺 registry / 03 缺 pair 长表均直接退出。

## 目录布局 (日志与产物)

- `logs/` — 各脚本运行日志 `<脚本名>.log` (含 `run_pipeline.log`)。复用主管道日志基建
  (`core/logging.py::setup_logging`): 格式 `时间 - 名称 - PID - 级别 - 消息`、每次运行覆盖
  只留最新、50MB rotate — 与 `news_process/logs/` 各阶段日志完全一致。整目录 gitignore。
- `data/` — 02/03 的全部数据产物 (主面板/pair 长表/codebook/双权长表/双权面板/互验报告)。
  两份 13GB dta (主面板 + 03 双权面板) 使整目录约 40GB 级。整目录 gitignore (镜像 `data/processed` 不入库惯例)。
- 例外: 01 的产物 registry yaml 落 `config/` — 它是入库 SSOT (02/03 与 gate 测试的消费锚),
  属配置而非数据结果。
- 上游输入不变: 五上游 parquet 仍从 `data/processed/` 读取 (只读); 权源商业 dta
  (`config/银行业金融机构基本信息表.dta`) 恒不入库; 税调名单 `config/company_tax_names.yaml` 已入库。

## 模块 import 说明

- 序号前缀 (`01_` 等) 非合法 Python import 语句标识符, 跨脚本复用一律
  `importlib.import_module("0X_...")` (税调 01→03 取 DV2 常量落 registry 区段; 税调 03→02 复用管道内
  SSOT `write_outputs`, 禁第二份实现)。WP5-stub 前置 (03 的 `DV2_CONSTANTS` 模块级常量先落) 使 01
  首跑即得终值 dv2 区段、registry 哈希锚一次定终, 免"写 03 → 重跑 01"级联回填。
- **跨管道引擎复用 (T-D10/T-D18)**: 税调 02/03 经 `importlib` + `sys.path` 注入姊妹目录
  `company_listed_bank/`, **只读复用**其加权引擎的公司无关件 (`build_measure_library` /
  `compute_weighted_panel` / `_compute_weighted_panel_percol` 位级参照臂 / `load_input21` 等纯函数,
  禁第二份实现)。`company_listed_bank/` 目录、其 registry、gate、产物 — **零字节改动** (边界铁律)。
  耦合披露: 姊妹引擎演进 → 税调 gate (手算锚 + bitwise) 翻红 = 故意的漂移探测器。
- 模块依赖方向 (01 import 03 的常量) 与执行顺序无关 — 常量在 import 时可得, 产物才分先后。

## 运行 (从 news_process/ 目录, conda base python)

一键全链 (orchestrator, 子进程隔离 + fail-loud 中断 + 计时 + 单实例锁):

```bash
python company_tax_bank/run_pipeline.py               # 全链 01→02→03
python company_tax_bank/run_pipeline.py --steps 02,03 # registry 已就绪时从 02 起
python company_tax_bank/run_pipeline.py --dry-run     # 只打印将执行的命令
```

或逐步手跑:

```bash
python company_tax_bank/01_build_company_tax_bank_cooc_registry.py
python company_tax_bank/02_build_company_tax_bank_cooc_panel.py
python company_tax_bank/03_build_company_tax_bank_weight_validation.py
```

- **单实例锁**: orchestrator 入口 O_CREAT|O_EXCL 原子创建 `logs/_run_pipeline.lock` (内容=PID) —
  并发双跑会交错覆写同一套日志与 ~13GB 产物 (2026-07-07 listed 姊妹管线实弹), 第二实例 fail-loud 拒启;
  陈旧锁 (持有者 PID 已不存活) 自愈清除。绕过 orchestrator 直跑单步脚本仍无互斥, 并发纪律同样适用。
- **03 内存预算 (T-D13 / WP-S1 提速 v2)**: run_pipeline 在 03 子进程注入默认
  `NEWS_PROCESS_COOC_BUDGET_CELLS=1000000000` (1.0B; 城网点长表 15M 行 / 县 8M 行, v7 年窗 2011–2020 口径)。
  1.0B 使加权引擎 chunk_eff = city 33→66 / county 62→100 (cap), 减 chunk 数提速; 引擎默认 60M 会把
  chunk_eff 收缩到 2 触发内存吃紧 WARNING + groupby 轮次暴涨。峰值 ~35-45GB (128GB 安全)。用户已
  `export` 该变量则不覆盖。手跑 03 时须自行设置 (否则回退引擎默认 60M, 次优)。

## gate 测试四件

pytest 收集实数以 `--collect-only -q` 为准 (增删测试后同步此处与各脚本/run_pipeline banner):

`tests/test_company_tax_bank_cooc_registry.py` (15) + `tests/test_company_tax_bank_cooc_panel.py` (61) +
`tests/test_company_tax_bank_weight_validation.py` (47) + `tests/test_company_tax_bank_run_pipeline_lock.py` (6) = 129
(v7 各 +1 窗口守卫: panel `test_panel_year_window_2011_2020` / weight `test_weight_year_window_2011_2020`;
提速 v2 各 +1: panel `test_write_outputs_emit_dta_flag` [WP-S3] / weight `test_wps2_join_background_writes_semantics` [WP-S2])。

⚠ 生产 T=18 复跑注意 (计划 §6 DEFERRED): dev T=2 语料只证管线正确性, 生产全量 21_full 重跑得真面板
(面板窗 2011–2020 完整内嵌语料域 2007–2025, 生产各窗内年均有语料; dev T=2 仅 2017–2018 有语料、
其余窗内年整年 0 属预期; dev 产物不可用于任何回归)。registry 哈希锚锚死盘上态, 有意重跑 01 后须
bump `tests/test_company_tax_bank_cooc_registry.py::EXPECTED_TAX_REGISTRY_SHA256` 并级联重跑 02 (pair
指纹) → 03 (双向锁); 权源商业 dta (`config/银行业金融机构基本信息表.dta`) 恒不入库。
