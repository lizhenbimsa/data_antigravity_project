# data_antigravity_project / news_process

**银行金融科技舆情面板分析流水线** — 一套端到端的中文新闻文本处理系统，
从 ~37GB 原始 XLSX 媒体报道生成可用于计量经济学研究的银行—年面板数据，
支持 5 个独立的研究产品（论文）共享同一处理内核。

## 1. 顶层架构（Phase 5 终态）

```
news_process/
├── core/                       # 共享内核 (Phase 1)
│   ├── config.py               #   YAML loader + .env + split-mode + prompt 内联
│   ├── logging.py              #   带 NEWS_PROCESS_RUN_ID 隔离的多进程日志
│   ├── parallel.py             #   joblib / ProcessPoolExecutor 包装
│   ├── reporting.py            #   parquet/csv/dta 持久化 + 数据集摘要
│   ├── stage.py                #   subprocess stage executor
│   ├── locking.py              #   PipelineLock (跨平台文件锁)
│   ├── caching.py              #   LLMCache (sqlite-backed)
│   ├── quality.py              #   数据质量校验
│   ├── schemas.py              #   OUTPUT_REGISTRY 单源 (stage → parquet 文件名)
│   ├── dag.py                  #   STAGES_MAIN / STAGES_VALIDATION 声明式 DAG
│   └── text/                   #   AC自动机 + 规范化 + 实体上下文抽取
│
├── pipeline/                   # 模块化流水线 (Phase 2-4)
│   ├── preprocess/             #   阶段 00: load + normalize + filter + dedup
│   ├── filtering/              #   阶段 15: 文章级政策语义对齐
│   ├── sentiment/              #   阶段 21-23 (待 Phase 6 迁入)
│   ├── features/               #   阶段 25-27: 战略差异度 + 政策对齐 + 经营态度
│   ├── panel/                  #   阶段 41-48 + 45 主面板组装
│   └── falsification/          #   阶段 51: 对照变量构建
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
├── data_processed/             # 各阶段 parquet/dta/csv 输出 (gitignored)
├── tests/                      # pytest 测试套件 (778 tests, 100% pass)
│   └── integration/            #   跨阶段集成测试 (含 Phase 0 reproducibility)
├── scripts/
│   ├── audit/                  #   一次性审计脚本 (sys.exit-style)
│   ├── legacy/                 #   归档的孤立模块
│   └── migrate/                #   迁移辅助脚本
├── stata/README.md             # 历史标记: 5 个 .do 已迁至 papers_assets/<paper>/do/
├── 00_preprocessing.py         # 根级 thin shim (CLI: ``python 00_preprocessing.py``)
├── 11_..52_*.py                # 21 个 fully-bodied 阶段脚本 (Phase 6 待迁入 pipeline/)
├── run_pipeline_function.py    # 主管线编排 (消费 core.dag.STAGES_MAIN)
├── run_pipeline_validation.py  # 验证管线编排 (消费 core.dag.STAGES_VALIDATION)
├── run_paper.py                # 多论文 CLI 调度器
└── pyproject.toml              # setuptools.packages.find = ["news_process*"]
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
# 全套 (~5 分钟)
python -m pytest news_process/tests/

# 仅红线集成测试
python -m pytest news_process/tests/integration/

# 指定阶段单测
python -m pytest news_process/tests/test_00_preprocessing.py -v
```

期望结果（Phase 5 末态）:`778 passed, 7 skipped, 0 failed`

## 3. 配置系统（Phase 4d）

`news_process.core.config.load_config()` 自动检测两种模式:

- **Split mode (优先)**: `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
  全部存在 → deep-merge 加载，外部 prompt `.txt` 自动内联到对应 `_template` 键
- **Legacy mode (向后兼容)**: 任一 split YAML 缺失 → 退回单文件 `config/config.yaml`

`tests/integration/test_config_split_equivalence.py` 守护两种模式语义等价。

## 4. 多论文产品（Phase 3）

每篇论文是 `papers/<paper_id>/` 下的独立 Python 包，包含：
- `dag.py` — 论文专属 DAG (从 `core.dag.STAGES_MAIN` 切片，identity-preserved)
- `analysis.py` — CLI 入口 (`--stage pipeline|tables|figures|all`)
- `tables.py` — Table 1+ 生成器 (调 `papers/_common/tables.py:summary_stats`)
- `figures.py` — Figure 1+ 生成器 (用 `papers/_common/figures.py` 期刊级风格)

非代码资产（`.do`、draft、output）一律放 `papers_assets/<paper_id>/`，
通过 `core.config['paths']['papers_assets_root']` 间接寻址。

## 5. Stata `.do` 调用契约（Phase 4a）

每个 `.do` 顶部含统一前奏块:

```stata
if "$panel_dta" == "" {
    global panel_dta "../../../data_processed/40_panel_yearly.dta"
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
phase-5-baseline   ← 当前
phase-4-baseline
phase-3-baseline
phase-2-baseline
phase-1-baseline
baseline-pre-restructure
```

每个 phase 内的子任务也单独 commit，可单点 `git revert <hash>`。

## 7. 已知 deferred 项

- **Phase 4f / 5b** (高风险, 独立授权): `data_processed/` → `data/processed/<group>/` 物理分组迁移
- **Phase 7+** (可选): 21 个根级 `[0-9]*_*.py` fully-bodied 脚本进一步 body relocate 到 `pipeline/<sub>/` + `validation/<x>/`，根文件变 thin shim（Phase 2c 模板复制）。Phase 6 已完成 utils 引用清理 + utils/ 删除，body relocate 是纯架构优化，非功能必须。
- **Phase 7+**: `validation/` 包内填 stages 31-39

## 8. 文献依据汇总

详见 `CHANGELOG.md` 中各 phase 提交的学术对标 + `news_process/papers/<paper>/__init__.py` 的论文级引用。
