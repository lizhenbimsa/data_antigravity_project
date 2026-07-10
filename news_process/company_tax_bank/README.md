# company_tax_bank — 税调企业—银行共现面板生产流水线

税调企业×年 银企共现媒体报道面板 (447,710 行 = 44,771 家税调企业 × 10 年 2011–2020) 的四步生产脚本。
面板与外部数据 merge 键 = **`usci × year`** (18 位统一社会信用代码, 全填全唯一; `company_tax_name × year`
为等价备用键)。产出**三个互为稳健性的权重** (共现报道权 + 城市网点权 + 县域网点权, 不分主次)
+ 04 两个替代聚合臂 (frozenw 基期冻结 / mainbankw top-1 主办银行, 与三权并排同律)。
权威执行计划 = `scripts/audit/COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08.md` (v7);
步骤 04 = `scripts/audit/FROZEN_BASE_WEIGHTS_AND_MAINBANK_EXECUTION_PLAN_2026-07-10.md` (v3)。

与姊妹管线 `company_listed_bank/` 完全隔离 (零字节交集); 唯一交集 = 02/03/04 只读 import 其加权引擎 (见下)。

## 执行顺序 (序号即顺序, 不可颠倒)

| 步骤 | 脚本 | 消费 | 产出 |
|---|---|---|---|
| 01 | `01_build_company_tax_bank_cooc_registry.py` (WP0) | 五上游 parquet 列名 + 裁剪负清单 + 税调名单 SSOT (`config/company_tax_names.yaml`) + 银行清单 | `config/company_tax_bank_cooc_registry.yaml` (加权引擎唯一 SSOT) |
| 02 | `02_build_company_tax_bank_cooc_panel.py` (WP1) | **01 的 registry yaml** (启动复算并校验哈希锚 — canonical 式经 importlib 复用 01 的 `registry_content_sha256`; 缺/不自洽则不跑) | 主面板 dta/parquet (20 固定列 [含 usci] + 加权列) + codebook + `_company_tax_bank_cooc_pairs.parquet` (pair 长表) |
| 03 | `03_build_company_tax_bank_weight_validation.py` (WP5) | **01 的 registry yaml** (DV2 常量双向锁, 缺区段即拒) + **02 的 pair 长表** (缺文件/缺内嵌指纹/指纹 stale 均 `SystemExit`: "无锚即无互验") + `config/银行业金融机构基本信息表.dta` (城市/县域两层级网点权源) | 双替代权长表 ×2 (`branch_city`/`branch_county`) + 双权面板 ×2 + 三权互验报告 |
| 04 | `04_build_company_tax_bank_altagg_panels.py` | **01 的 registry yaml** (启动复算哈希锚) + **02 的 pair 长表** (metadata 锚 stale 即 `SystemExit`) + 五上游 parquet (测度库经 02 的 `engine()` 与之同源) | frozenw/mainbankw 替代聚合面板 ×2 (dta+parquet) + 权重长表 ×2 + codebook「替代聚合面板章」 |

顺序为硬依赖 (fail-loud 闸), 非约定: 02 缺 registry / 03·04 缺 pair 长表均直接退出。
⚠ **级联义务**: 重跑 02 会重生 pair 长表, 且 02 整文件重写 codebook 只保留 03 标记块 →
04 产物与「替代聚合面板章」stale/被抹, **重跑 02 后须补跑 04**。

## 目录布局 (日志与产物)

- `logs/` — 各脚本运行日志 `<脚本名>.log` (含 `run_pipeline.log`)。复用主管道日志基建
  (`core/logging.py::setup_logging`): 格式 `时间 - 名称 - PID - 级别 - 消息`、每次运行覆盖
  只留最新、50MB rotate — 与 `news_process/logs/` 各阶段日志完全一致。整目录 gitignore。
- `data/` — 02/03/04 的全部数据产物 (主面板/pair 长表/codebook/双权长表/双权面板/互验报告/
  替代聚合面板×2+权重长表×2)。主面板与 03 双权 + 04 双替代聚合共五份 ~7GB 级 dta, 整目录约
  55GB 级 (04 dev 可 `--no-emit-dta` 跳 dta)。整目录 gitignore (镜像 `data/processed` 不入库惯例)。
- 例外: 01 的产物 registry yaml 落 `config/` — 它是入库 SSOT (02/03 与 gate 测试的消费锚),
  属配置而非数据结果。
- 上游输入不变: 五上游 parquet 仍从 `data/processed/` 读取 (只读); 权源商业 dta
  (`config/银行业金融机构基本信息表.dta`) 恒不入库; 税调名单 `config/company_tax_names.yaml` 已入库。

## 模块 import 说明

- 序号前缀 (`01_` 等) 非合法 Python import 语句标识符, 跨脚本复用一律
  `importlib.import_module("0X_...")` (税调 01→03 取 DV2 常量落 registry 区段; 税调 03→02 复用管道内
  SSOT `write_outputs`, 禁第二份实现)。WP5-stub 前置 (03 的 `DV2_CONSTANTS` 模块级常量先落) 使 01
  首跑即得终值 dv2 区段、registry 哈希锚一次定终, 免"写 03 → 重跑 01"级联回填。
- **跨管道引擎复用 (T-D10/T-D18)**: 税调 02/03/04 经 `importlib` + `sys.path` 注入姊妹目录
  `company_listed_bank/`, **只读复用**其加权引擎的公司无关件 (`build_measure_library` /
  `compute_weighted_panel` / `_compute_weighted_panel_percol` 位级参照臂 / `load_input21` 等纯函数,
  禁第二份实现)。`company_listed_bank/` 目录、其 registry、gate、产物 — **零字节改动** (边界铁律)。
  耦合披露: 姊妹引擎演进 → 税调 gate (手算锚 + bitwise) 翻红 = 故意的漂移探测器。
- 模块依赖方向 (01 import 03 的常量) 与执行顺序无关 — 常量在 import 时可得, 产物才分先后。

## 运行 (从 news_process/ 目录, conda base python)

一键全链 (orchestrator, 子进程隔离 + fail-loud 中断 + 计时 + 单实例锁):

```bash
python company_tax_bank/run_pipeline.py                  # 全链 01→02→03→04
python company_tax_bank/run_pipeline.py --steps 02,03,04 # registry 已就绪时从 02 起
python company_tax_bank/run_pipeline.py --dry-run        # 只打印将执行的命令
python company_tax_bank/run_pipeline.py --no-emit-dta    # dev 快速模式 (02/03/04 跳 dta)
```

或逐步手跑:

```bash
python company_tax_bank/01_build_company_tax_bank_cooc_registry.py
python company_tax_bank/02_build_company_tax_bank_cooc_panel.py
python company_tax_bank/03_build_company_tax_bank_weight_validation.py
python company_tax_bank/04_build_company_tax_bank_altagg_panels.py
```

- **单实例锁**: orchestrator 入口 O_CREAT|O_EXCL 原子创建 `logs/_run_pipeline.lock` (内容=PID) —
  并发双跑会交错覆写同一套日志与 ~13GB 产物 (2026-07-07 listed 姊妹管线实弹), 第二实例 fail-loud 拒启;
  陈旧锁 (持有者 PID 已不存活) 自愈清除。绕过 orchestrator 直跑单步脚本仍无互斥, 并发纪律同样适用。
- **03 内存预算 (T-D13 / WP-S1 提速 v2)**: run_pipeline 在 03 子进程注入默认
  `NEWS_PROCESS_COOC_BUDGET_CELLS=1000000000` (1.0B; 城网点长表 15M 行 / 县 8M 行, v7 年窗 2011–2020 口径)。
  1.0B 使加权引擎 chunk_eff = city 33→66 / county 62→100 (cap), 减 chunk 数; 引擎默认 60M 会把
  chunk_eff 收缩到 city 3 / county 7 (city <4 触发内存吃紧 WARNING) + groupby 轮次暴涨。
  ⚠ **budget 提速非单调**: 实测 (7db15e69 全链) city 引擎 781→478s 大受益, 但 county 引擎 312→510s
  **反变慢** (chunk_eff 62→100 大帧内存带宽 + WP-S2 城写盘重叠争用); 1.0B 净效应仍为正 (总 −660s),
  但生产 T=18 须 **per-分支实测选最优 budget**, 勿假定 county 随 budget 提高而加速。峰值 ~35-45GB
  投影 (128GB 安全; mid-chunk RSS 采样 DEFERRED 到生产实测, 现日志仅落盘后 RSS 下界)。用户已
  `export` 该变量则不覆盖。手跑 03 时须自行设置 (否则回退引擎默认 60M, 次优)。

## gate 测试五件

pytest 收集实数以 `--collect-only -q` 为准 (增删测试后同步此处与各脚本/run_pipeline banner):

`tests/test_company_tax_bank_cooc_registry.py` (15) + `tests/test_company_tax_bank_cooc_panel.py` (62) +
`tests/test_company_tax_bank_weight_validation.py` (47) + `tests/test_company_tax_bank_run_pipeline_lock.py` (8) +
`tests/test_company_tax_bank_altagg.py` (15) = 147
(v7 各 +1 窗口守卫: panel `test_panel_year_window_2011_2020` / weight `test_weight_year_window_2011_2020`;
提速 v2 各 +1: panel `test_write_outputs_emit_dta_flag` [WP-S3] / weight `test_wps2_join_background_writes_semantics` [WP-S2];
04 替代聚合 +15 新文件 + panel parametrize +04 stem)。

⚠ 生产 T=18 复跑注意 (计划 §6 DEFERRED): dev T=2 语料只证管线正确性, 生产全量 21_full 重跑得真面板
(面板窗 2011–2020 完整内嵌语料域 2007–2025, 生产各窗内年均有语料; dev T=2 仅 2017–2018 有语料、
其余窗内年整年 0 属预期; dev 产物不可用于任何回归)。registry 哈希锚锚死盘上态, 有意重跑 01 后须
bump `tests/test_company_tax_bank_cooc_registry.py::EXPECTED_TAX_REGISTRY_SHA256` 并级联重跑 02 (pair
指纹) → 03 (双向锁) → 04 (pair 锚同代校验 + codebook 章重生); 权源商业 dta
(`config/银行业金融机构基本信息表.dta`) 恒不入库。

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
  2026-07-07 listed 姊妹管线曾遇 WinError 2)。listed × tax 两派生管线之间可并发 (各写自有 `data/`, 仅只读 `data/processed`)。
- **--skip-unchanged 盲区 (F9)**: 主管道以 `--skip-unchanged` 重跑时 stage40 可能被跳过 (75 不在其 input_hashes
  追踪集), cross_media/staleness 等 opt-in 特征列会保留旧/缺值 — 需这些列时勿配该 flag, 或先单独重跑 stage40。
