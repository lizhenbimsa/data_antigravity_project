# data_antigravity_project / news_process

**银行金融科技舆情面板分析流水线** — 一套端到端的中文新闻文本处理系统，
从 ~37GB 原始 XLSX 媒体报道生成可用于计量经济学研究的银行—年面板数据，
支持 5 个独立的研究产品（论文）共享同一处理内核。

> **当前版本: v2.0.0 / phase-8-baseline (2026-05-04)**
> 八期重构（Phase 0 → 8）已完成。26 个根级数字前缀脚本全部统一为极薄 CLI 适配层；
> `news_process/{core, pipeline, papers, validation, scripts, config}` 形成完整 canonical 包结构；
> 数据物理布局规范化为 `data/processed/`。pytest 778 passed / 7 skipped / 0 failed。
> 完整演进史见 [CHANGELOG.md](./CHANGELOG.md)，rollback tag 链：
> `baseline-pre-restructure → phase-{1..6}-baseline → phase-7a-baseline →
> phase-7b-baseline → phase-8-baseline → v2.0.0`。

## 1. 顶层架构（v2.0.0 终态）

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
├── tests/                      # pytest 测试套件 (778 用例, 当前全通过)
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
└── pyproject.toml              # setuptools.packages.find = ["news_process*"]; version = "2.0.0"
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
python -m news_process.run_paper news_process --stage all
```

### 2.3 跑单篇论文表/图

```bash
# 列出所有可调度论文
python -m news_process.run_paper --list

# 仅生成主线论文的 Table 1 (要求 pipeline 已跑过)
python -m news_process.run_paper news_process --stage tables

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
phase-5-baseline   ← 当前
phase-4-baseline
phase-3-baseline
phase-2-baseline
phase-1-baseline
baseline-pre-restructure
```

每个 phase 内的子任务也单独 commit，可单点 `git revert <hash>`。

## 7. 已知 deferred 项 (Phase 8 之后还可选的进一步优化)

- **Phase 9+ (极低优先级)**: `data/processed/<group>/` 业务组子分区。当前 Phase 8 的"单层重命名"方案保留扁平布局；若未来出现存储分层、按组冷存储保留策略等场景，可参考 `scripts/migrate/migrate_data_layout.py` 完成深一级分组。但需注意：跨阶段交叉读取（如 stage 21 读 stage 14、stage 24 读 stage 23）会迫使 `CONFIG['filenames']` 携带组前缀信息，反向增加耦合，违反 DRY — 不推荐做此细分。

> **Phase 7a (2026-05-04)** 已完成 8 个 pipeline 类 root body 迁入 `pipeline/<sub>/` + thin shim 化。
> **Phase 7b (2026-05-04)** 已完成 13 个 validation 类 root body 迁入 `news_process/validation/` 扁平布局 + thin shim 化。
> **Phase 8 (2026-05-04)** 已完成 `data_processed/` → `data/processed/` 单层重命名。

## 8. 文献依据汇总

详见 `CHANGELOG.md` 中各 phase 提交的学术对标 + `news_process/papers/<paper>/__init__.py` 的论文级引用。
