# data_antigravity_project / news_process

**银行金融科技舆情面板分析流水线** — 一套端到端的中文新闻文本处理系统，
从 ~37GB 原始 XLSX 媒体报道生成可用于计量经济学研究的银行—年面板数据，
支持 5 个独立的研究产品（论文）共享同一处理内核。

> **5 paper 成熟度梯度（Plan-r3 P1-6 显式化, 2026-05-09）**：
> - **`bank_fintech_tone`**（主线）— Python 包 276 行 + Stata 1075 行（含 1016 行 falsification template）+ manuscript 已起草。
> - **`benefit_society`** / **`brokerage_network`** / **`strategic_diff`**（半成熟）— Python `tables.py` 仅 Table 1 描述统计骨架（主回归 / 机制 / 异质性 表格全部在 `papers_assets/<id>/do/*.do` 中, 187 ~ 345 行 Stata 主回归脚本已落地）, manuscript 待起草。
> - **`llm_peer`**（全骨架, Plan-r3 P1-5 刚补齐资产目录）— Python 165 行骨架 + Stata 0 行（main_regression.do 等待 v3.0 补齐）+ manuscript 未起草。
> - 详见 `papers_assets/<id>/README.md`（仅 `llm_peer` 含, 其它 4 个 paper 在 `papers/<id>/__init__.py` 模块级 docstring）。

> **当前版本: v2.1.0 / phase-9-baseline (2026-05-08)**
> 八期重构（Phase 0 → 8）已完成；Phase 9（v2.1.0）做了 4 个子任务的
> post-restructure cleanup — 删除 5 个 broken audit/test 脚本、删除 5 个
> 空壳 ``papers/<id>/dag.py``、净化 paper analysis 中 5 处反射 import、
> 删除 orchestrator 的历史 OUTPUT_REGISTRY fallback dict（不引入新抽象，
> 不动 26 个 thin shim）。pytest 814 passed / 2 skipped / 0 failed (post-recode round 3 / Plan-r3 P0-P3 17 单元 + 两轮 recode + 一轮 review 修 2 个真 bug + 7 项改进; round 2 sidecar 化 baseline 786; round 1+2 baseline 782; v2.1.0 release tag frozen baseline 772)。
> 完整演进史见 [CHANGELOG.md](./CHANGELOG.md)，rollback tag 链：
> `baseline-pre-restructure → phase-{1..6}-baseline → phase-7a-baseline →
> phase-7b-baseline → phase-8-baseline → v2.0.0 → phase-9c-baseline →
> phase-9d-baseline → phase-9a-baseline → phase-9b-baseline →
> phase-9-baseline → v2.1.0`。

## 1. 顶层架构（v2.1.0 / phase-9-baseline 终态）

```
news_process/
├── core/                       # 共享内核 (Phase 1)
│   ├── config.py               #   YAML loader + .env + split-mode + prompt 内联
│   ├── logging.py              #   带 NEWS_PROCESS_RUN_ID 隔离的多进程日志
│   ├── parallel.py             #   joblib / ProcessPoolExecutor 包装
│   ├── reporting.py            #   parquet/csv/dta 持久化 + 数据集摘要
│   ├── stage.py                #   子进程隔离的阶段执行器
│   ├── locking.py              #   PipelineLock (跨平台文件锁)
│   ├── caching.py              #   LLMCache (SQLite 持久化)
│   ├── quality.py              #   数据质量校验
│   ├── schemas.py              #   OUTPUT_REGISTRY 单源 (stage → parquet 文件名)
│   ├── dag.py                  #   STAGES_MAIN / STAGES_VALIDATION 声明式 DAG
│   └── text/                   #   AC自动机 + 规范化 + 实体上下文抽取
│
├── pipeline/                   # 模块化流水线 (Phase 2-4 + 7a)
│   ├── preprocess/             #   阶段 00: load + normalize + filter + dedup
│   ├── filtering/              #   阶段 11/12/14/15: 银行/金融科技分类 + 强度 + 政策对齐
│   ├── sentiment/              #   阶段 21/22/23/24: LLM/词典/BERT/跟风衰减
│   ├── features/               #   阶段 25-27: 战略差异度 + 政策对齐 + 经营态度
│   ├── panel/                  #   阶段 41-48 + 45 主面板组装
│   ├── falsification/          #   阶段 51: 对照变量构建
│   └── audit/                  #   阶段 52/53: Stata 数据审计 + 摘要导出
│
├── validation/                 # 验证模块 (Phase 7b 扁平 13 文件)
│   ├── text2vec.py             #   阶段 30: 文本相似度稳健性
│   ├── threshold.py            #   阶段 31: 阈值敏感性
│   ├── llms_human.py           #   阶段 32: 人工抽样
│   ├── dedup_threshold.py      #   阶段 32a: 去重阈值敏感性
│   ├── llms_evaluation.py      #   阶段 33: LLM 一致性评估
│   ├── tone_validation.py      #   阶段 34: 情感三角验证
│   ├── radius_sensitivity.py   #   阶段 35: 上下文窗口半径
│   ├── entity_masking.py       #   阶段 36: 实体掩码
│   ├── dict_coverage.py        #   阶段 37: 词典覆盖率
│   ├── media_diversity.py      #   阶段 38: 媒体多样性
│   ├── temporal_mask.py        #   阶段 38a: 时间掩码 (前视偏误)
│   ├── decay_sensitivity.py    #   阶段 38b: 距离衰减权重
│   └── prompt_sensitivity.py   #   阶段 39: Prompt 措辞敏感度
│
├── papers/                     # 多论文产品层 (Phase 3)
│   ├── _common/                #   PaperConfig + load_panel + tables + figures + stata_runner
│   ├── bank_fintech_tone/      #   主线: 银行金融科技语调
│   ├── benefit_society/        #   衍生 1: Jha-Liu-Manela 2026 RFS
│   ├── brokerage_network/      #   衍生 2: Han et al. 2024 信息经纪网络
│   ├── llm_peer/               #   衍生 3: Cao et al. 2025 LLM 同业 IV
│   └── strategic_diff/         #   衍生 4: Guzman-Li 2023 + Hoberg-Phillips 2016
│
├── papers_assets/              # 非代码研究资产
│   ├── literature/             #   文献库 (PDF/MD, gitignored)
│   └── <paper_id>/{do,output,drafts}/  # 论文专属 .do/产出/手稿
│
├── config/                     # Phase 4d 拆分配置
│   ├── config.yaml             #   stub (历史兼容; loader 检测 split-mode 后跳过)
│   ├── paths.yaml              #   paths + filenames + parallel
│   ├── preprocessing.yaml      #   preprocessing + normalization + deduplication
│   ├── filtering.yaml          #   bank/fintech_news_classification + ...
│   ├── sentiment.yaml          #   tone_llm_processing(去 prompt) + sentiment_analysis + herd_detection
│   ├── features.yaml           #   embedding_api + benefit_society
│   ├── panel.yaml              #   panel_building + temporal_mask_test
│   ├── validation.yaml         #   human_validation + validation + 多个 *_test
│   └── prompts/
│       ├── unified_cot.txt     #   阶段 21 LLM Chain-of-Thought 提示词模板
│       └── title_sentiment.txt #   标题轨道情感分析提示词
│
├── data_excel/                 # 原始 XLSX 数据 (gitignored)
├── data/processed/             # 各阶段 parquet/dta/csv 输出 (gitignored, Phase 8 重命名)
├── tests/                      # pytest 测试套件 (772 用例, 当前全通过; v2.1.0 baseline)
│   └── integration/            #   跨阶段集成测试 (含 Phase 0 可复现性门槛)
├── scripts/
│   ├── audit/                  #   一次性审计脚本 (sys.exit-style)
│   ├── legacy/                 #   归档的孤立模块
│   └── migrate/                #   迁移辅助脚本
├── stata/README.md             # 历史标记: 5 个 .do 已迁至 papers_assets/<paper>/do/
├── 00_preprocessing.py … 53_export_stats_excel.py   # 26 个极薄 CLI 适配层 (≤30 行/个, 保留历史 ``python NN_xxx.py`` 契约)
├── run_pipeline_function.py    # 主管线编排 (消费 core.dag.STAGES_MAIN)
├── run_pipeline_validation.py  # 验证管线编排 (消费 core.dag.STAGES_VALIDATION)
├── run_paper.py                # 多论文 CLI 调度器
└── pyproject.toml              # setuptools.packages.find = ["news_process*"]; version = "2.1.0"
```

## 2. 快速上手

### 2.1 环境准备

```bash
# 假定 Python 3.13 + Anaconda
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r news_process/requirements.txt

# 复制 .env 模板, 填入 LLM API 密钥
cp news_process/.env.example news_process/.env
# 编辑 .env: GPT5NANO_API_KEY / GEMINI3_API_KEY / CLAUDE4H_API_KEY / EMBEDDING_API_KEY
```

### 2.2 跑整条流水线（主线论文）

```bash
# 方法 A: 直接调用主管线
python news_process/run_pipeline_function.py

# 方法 B: 经多论文 CLI (等价)
python -m news_process.run_paper bank_fintech_tone --stage all
```

### 2.3 跑单篇论文表/图

```bash
# 列出所有可调度论文
python -m news_process.run_paper --list

# 仅生成主线论文的 Table 1 (要求 pipeline 已跑过)
python -m news_process.run_paper bank_fintech_tone --stage tables

# 干跑 (打印 DAG, 不真实执行)
python -m news_process.run_paper benefit_society --dry-run
```

### 2.4 跑测试

```bash
# 全套 (~33 秒含 jieba warm cache; HEAD baseline = 814 passed / 2 skipped; v2.1.0 release tag = 772 passed)
python -m pytest news_process/tests/

# 仅红线集成测试
python -m pytest news_process/tests/integration/

# 指定阶段单测
python -m pytest news_process/tests/test_00_preprocessing.py -v
```

期望结果:
- v2.1.0 release tag (frozen baseline): `772 passed, 6 skipped, 0 failed`
- post-recode round 1+2 baseline: `782 passed, 6 skipped, 0 failed`
- post-round 2 sidecar 化后 (P1-5 SKIP→PASS, Win 兼容): `786 passed, 2 skipped, 0 failed`
- post-recode round 3 / 17 单元 + 两轮 recode + 一轮 review (HEAD): `814 passed, 2 skipped, 0 failed`
  - 增量来源: 17 单元 +19 + 两轮 recode +5 + 一轮 review +6
  - 两轮 recode + 一轮 review 共发现 2 个真 bug + 7 项改进, 加 6 个新不变量测试:
    - bug 1 (recode): cache key `.4f` 让 1e-30 ≡ 0.0 碰撞 → `repr()` 修复
    - bug 2 (final recode): cache key `None` ≡ `""` 共用 namespace → 哨兵区分修复
    - review R1-R8: CI rapidfuzz / 单跑 pytest / prompt_version 状态文档 / env 间接引用递归 / smoke 副作用清理 / Makefile 守门 / 哨兵 ASCII 化

## 3. 配置系统（Phase 4d）

`news_process.core.config.load_config()` 自动检测两种模式:

- **Split mode (优先)**: `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
  全部存在 → deep-merge 加载，外部 prompt `.txt` 自动内联到对应 `_template` 键
- **Legacy mode (向后兼容)**: 任一 split YAML 缺失 → 退回单文件 `config/config.yaml`

`tests/integration/test_config_split_equivalence.py` 守护两种模式语义等价。

## 4. 多论文产品（Phase 3, 经 Phase 9a 简化）

每篇论文是 `papers/<paper_id>/` 下的独立 Python 包，包含：
- `analysis.py` — CLI 入口 (`--stage pipeline|tables|figures|all`)；
  顶部 `STAGES = list(STAGES_MAIN)` 替代原 `dag.py` 子模块（Phase 9a）；
  调主流水线走 `_common.run_main_pipeline()` 规范桥接（Phase 9b）
- `tables.py` — Table 1+ 生成器 (调 `papers/_common/tables.py:summary_stats`)
- `figures.py` — Figure 1+ 生成器 (用 `papers/_common/figures.py` 期刊级风格)

非代码资产（`.do`、draft、output）一律放 `papers_assets/<paper_id>/`，
通过 `core.config['paths']['papers_assets_root']` 间接寻址。

## 5. Stata `.do` 调用契约（Phase 4a）

每个 `.do` 顶部含统一前奏块:

```stata
if "$panel_dta" == "" {
    global panel_dta "../../../data/processed/40_panel_yearly.dta"
}
if "$out_dir" == "" {
    global out_dir "../output"
    capture mkdir "$out_dir"
}
use "$panel_dta", clear
```

调用方法:

```stata
// 方法 1: cd 到 .do 文件所在目录, 直接 do
cd news_process/papers_assets/bank_fintech_tone/do
do 50_robustness_text2vec_stata.do

// 方法 2: 显式覆盖路径全局
global panel_dta "<custom path>"
do <full path to .do>
```

## 6. 可回滚锚点

```
v2.1.0 / phase-9-baseline   ← 当前 (recode follow-up: 见 HEAD)
phase-9b-baseline           Phase 9b: papers 反射 import 净化
phase-9a-baseline           Phase 9a: papers DAG 空壳清理
phase-9d-baseline           Phase 9d: OUTPUT_REGISTRY fallback 删除
phase-9c-baseline           Phase 9c: scripts dead code 清扫
v2.0.0 / phase-8-baseline   v2.0 八期重构终态
phase-7b-baseline           validation/ 扁平包 + 13 thin shim
phase-7a-baseline           pipeline/ 子包 + 8 thin shim
phase-6-baseline            utils/ 退役
phase-5-baseline            pipeline/ + tests/ utils.* 迁移
phase-4-baseline            7 域配置拆分 + Stata .do 归位
phase-3-baseline            multi-paper 产品化
phase-2-baseline            pipeline/ 子包 + importlib 反射净化
phase-1-baseline            news_process 真包 + core/dag.py
baseline-pre-restructure    重整起点
```

每个 phase 内的子任务也单独 commit，可单点 `git revert <hash>`。
完整 rollback 命令清单见 [`docs/reference/rollback_anchors.md`](docs/reference/rollback_anchors.md)。

## 6.5 数据目录生命周期

`news_process/data/processed/_backup_*` (99 MB)、`data_excel/back/` (43 GB)
等历史快照与缓存目录的保留 / 清理策略, 见
[`docs/guides/data_lifecycle.md`](docs/guides/data_lifecycle.md) (Plan P2-10 交付)。

## 7. 已知 deferred 项 (Phase 9 之后还可选的进一步优化)

- **v3.0 主迁移 (留待真正的 major bump)**: 删除 26 个数字前缀 thin shim,
  把 `core/dag.py:StageSpec.script` 从文件名改为 module path
  (`"news_process.pipeline.filtering.news_bank"`),
  把 `core/stage.py:run_stage` 从 `subprocess.Popen([python, script_path])`
  改为 `subprocess.Popen([python, "-m", module])`. 详细计划与外部影响面
  评估见 [`docs/guides/thin_shim_pattern.md`](docs/guides/thin_shim_pattern.md)。
- **极低优先级**: `data/processed/<group>/` 业务组子分区。当前 Phase 8 的"单层重命名"方案保留扁平布局；若未来出现存储分层、按组冷存储保留策略等场景，可参考 `scripts/migrate/migrate_data_layout.py` 完成深一级分组。但需注意：跨阶段交叉读取（如 stage 21 读 stage 14、stage 24 读 stage 23）会迫使 `CONFIG['filenames']` 携带组前缀信息，反向增加耦合，违反 DRY — 不推荐做此细分。
- **历史命名遗留** (Phase 9 范围外, 留待 v3.0): `papers/bank_fintech_tone/analysis.py:35` 的 `_LOGGER` name 仍含 v1.x paper id `news_process` (应为 `bank_fintech_tone`); 同文件 docstring 中 `python -m news_process.run_paper news_process` 同样残留; `pyproject.toml` 部分 NOTE 用 Phase 1/3 时态描述。

> **Phase 7a (2026-05-04)** 已完成 8 个 pipeline 类 root body 迁入 `pipeline/<sub>/` + thin shim 化。
> **Phase 7b (2026-05-04)** 已完成 13 个 validation 类 root body 迁入 `news_process/validation/` 扁平布局 + thin shim 化。
> **Phase 8 (2026-05-04)** 已完成 `data_processed/` → `data/processed/` 单层重命名。
> **Phase 9 (2026-05-08)** 完成 4 个 post-restructure cleanup 子任务 (9c/9d/9a/9b) + v2.1.0 release。

## 8. 文献依据汇总

详见 `CHANGELOG.md` 中各 phase 提交的学术对标 + `news_process/papers/<paper>/__init__.py` 的论文级引用。
