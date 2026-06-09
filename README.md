# data_antigravity_project / news_process

**银行金融科技舆情面板分析流水线** — 一套端到端的中文新闻文本处理系统，
从 ~37GB 原始 XLSX 媒体报道生成可用于计量经济学研究的银行—年面板数据，
支持 9 个独立的研究产品（论文）共享同一处理内核（Bank-FinTech 主线 5 篇 P1-P5 + 衍生 4 篇）。

> **下方"5 paper 成熟度梯度"快照定格在 v3.2.0 / 2026-05-15 commit 8d33c46；v3.4.0+ 已扩为 9 paper portfolio，完整分布见 [CLAUDE.md §Multi-Paper Support](news_process/CLAUDE.md) 与 [docs/plan/B_route_master_plan_v2.md](news_process/docs/plan/B_route_master_plan_v2.md)。**

> **5 paper 成熟度梯度（post-P4 / commit 8d33c46, 2026-05-15）**：
> - **`bank_fintech_tone`**（主线）— Python 包 + Stata 14 主模板 (v3.2.0 M7) + 1016 行 falsification template + en/zh 双语 manuscript 骨架 (114 行/12 TODO)。
> - **`benefit_society` / `brokerage_network` / `strategic_diff` / `llm_peer`**（4 衍生 paper, 全部 P0-P4 落地）—
>     - Python `tables.py` 含 Table 1 + Table 2-5 (主回归 / 机制 / 异质性 / 稳健性, 读 Stata esttab CSV)
>     - Python `figures.py` 含 Figure 1-3 (分布 + coefplot + forest)
>     - Stata 模板 8 个 / paper @ `_common/stata_templates/<paper>/` (00_master ~ 30_figure1) + paper-specific override .do 保留
>     - en/zh 双语 manuscript 骨架 (86 行/10 TODO 每语种) + refs.bib
>     - 复现包: `python -c "from news_process.papers._common.derivative_replication import build_derivative_replication_package as b; b('<paper_id>')"`
> - **详见**: 每个 paper 的 `papers_assets/<id>/README.md` (5 paper 全有) 与 `papers/<id>/__init__.py` 模块级 docstring。
> - **仍待用户补充**: manuscript 内 `\NoteThis{...}` 占位实质内容 + 会计变量 (ROA/NPL/Z) 并入 panel。

> **当前版本: v3.7.4 (2026-05-30; 权威以 [news_process/CLAUDE.md](news_process/CLAUDE.md) 顶部 "Current version" 段为准; 最近独立 git tag: v3.6.0)**
> <!-- audit S5 (2026-05-30): 单一版本指针, 避免本 README 内 v3.7.0/v3.7.4/v3.7.1 三处横幅互相矛盾 -->
> <!-- 旧横幅曾写 v3.7.0; 实际 HEAD 已到 v3.7.4 (见下方 §6 演进表与 README L179) -->
> _注: 下文部分版本号/测试计数为历史快照, 可能滞后于 CLAUDE.md 权威值。_
> 八期重构（Phase 0 → 8）+ Phase 9 (v2.1.0) post-restructure cleanup + v3.2.0
> 三轨化双轨核心 + post-v3.2.0 multi-paper extension (8d33c46, 4 衍生 paper) +
> v3.4.0 第三维度 collab_mode + v3.5.0/v3.5.1 Stage 3 augmentation +
> v3.6.0 Plan E 双轨闭合 + v3.7.0 D 组 (staleness / α) +
> v2.3 集成层 (LM 4 子词典 + FLS + 媒体 tier + EPU + DC3 LLM archive).
> **pytest baseline (v3.7.0)**: **1629 fast / 284 integration / 1913 total**
> (`pytest --collect-only` 实测; 历史: v2.1.0 release = 772 / v3.2.0 = 1144 /
> post-v3.2.0 = 1388 / v3.5.1 ≈ 1590 / v3.6.0 = 1615 / v3.7.0 = 1629).
> 完整演进史见 [CHANGELOG.md](./CHANGELOG.md) 与 [news_process/CLAUDE.md](news_process/CLAUDE.md) 顶部 "Current version" 段，rollback tag 链：
> `baseline-pre-restructure → phase-{1..6}-baseline → phase-7a-baseline →
> phase-7b-baseline → phase-8-baseline → v2.0.0 → phase-9c-baseline →
> phase-9d-baseline → phase-9a-baseline → phase-9b-baseline →
> phase-9-baseline → v2.1.0 → v3.2.0 → 8d33c46 → v3.6.0 (2026-05-18)`。
> v3.5.2 / v3.6.1 / v3.7.0 / v3.7.1 / v2.3 系列已合入 main 但未独立 tag。

## 1. 顶层架构（v3.7.x 当前态 / 下表 tree 仍反映 v3.2.0 epoch 命名）

```
news_process/
├── core/                       # 共享内核 (Phase 1)
│   ├── config.py               #   YAML loader + .env + split-mode + prompt 内联
│   ├── logging.py              #   带 NEWS_PROCESS_RUN_ID 隔离的多进程日志
│   ├── reporting.py            #   parquet/csv/dta 持久化 + 数据集摘要
│   ├── stage.py                #   子进程隔离的阶段执行器
│   ├── locking.py              #   PipelineLock (跨平台文件锁)
│   ├── caching.py              #   LLMCache (SQLite 持久化)
│   ├── data_versioning.py      #   parquet 元数据 + 血缘追踪
│   ├── run_id.py               #   运行 ID 生成
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
├── tests/                      # pytest 测试套件 (HEAD baseline: 1629 fast / 284 integration, v3.7.0)
│   └── integration/            #   跨阶段集成测试 (含 Phase 0 可复现性门槛)
├── scripts/
│   ├── audit/                  #   一次性审计脚本 (sys.exit-style)
│   ├── legacy/                 #   归档的孤立模块
│   └── migrate/                #   迁移辅助脚本
├── stata/README.md             # 历史标记: 5 个 .do 已迁至 papers_assets/<paper>/do/
├── 00_preprocessing.py … 53_export_stats_excel.py   # 39 个极薄 CLI 适配层 (≤30 行/个, 保留历史 ``python NN_xxx.py`` 契约; 含字母后缀 32a/38a/38b/39a/39c/39d/39e/39f/30a)
├── run_pipeline_function.py    # 主管线编排 (消费 core.dag.STAGES_MAIN)
├── run_pipeline_validation.py  # 验证管线编排 (消费 core.dag.STAGES_VALIDATION)
├── run_paper.py                # 多论文 CLI 调度器
├── requirements*.txt           # pip-only / lockfile 依赖入口
└── __init__.py                 # 包版本与重构状态说明
```

仓库根目录的 `pyproject.toml` 是 Python package metadata 与 editable install 入口。

## 2. 快速上手

### 2.1 环境准备

```bash
# 假定 Python 3.13 + Anaconda
python -m venv .venv
.venv/Scripts/python.exe -m pip install -e .
# 如需严格复现锁定依赖，也可使用：
# .venv/Scripts/python.exe -m pip install -r news_process/requirements.lock
# .venv/Scripts/python.exe -m pip install -e . --no-deps

# 复制 .env 模板, 填入 LLM API 密钥
cp news_process/.env.example news_process/.env
# 编辑 .env: 必填 YUNWU_API_KEY；可选覆盖 EMBEDDING_API_KEY / FINBERT2_MODEL_DIR
# GPT5NANO_API_KEY / GEMINI3_API_KEY / CLAUDE4H_API_KEY 仅为 legacy 探针脚本兼容项，主流程不读取。
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
# 全套 (HEAD baseline = 1629 fast + 284 integration = 1913 total; v2.1.0 = 772; v3.2.0 = 1144; post-v3.2.0 = 1388; v3.7.0 = 1629 fast)
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
- **HEAD (2026-05-30 实测, repo 根)**: fast `~2384 collected / ~2382 passed / 0 failed / 2 skipped` (`pytest -m fast`, exit 0); integration: 8 fail blocked by stale disk panel parquet (M0 gate, 见 docs/TECH-DEBT.md §[1-B][1-C])。<!-- audit S4: 旧记 "1892 passed" 已滞后, 以本次实跑为准; 0 failed 为硬不变式 -->
- **(历史 2026-05-27 quality-hardening 快照)**: `2200 total` (`--collect-only`); fast `1892 passed, 0 failed, 2 skipped`
- v3.7.0 (2026-05-18): `1629 fast / 284 integration / 1913 total`
- v3.6.0 (Plan E 双轨闭合): `1615 fast`
- v3.5.1 supplementation: `~1590 fast`
- post-v3.2.0 multi-paper extension (8d33c46, 2026-05-15): `1388 passed, 6 skipped`
- v3.2.0 release tag baseline: `1144 passed, 6 skipped, 0 failed`
- post-recode round 3 / 17 单元 + 两轮 recode + 一轮 review (v2.1.0 frozen): `814 passed, 2 skipped, 0 failed`
  - 增量来源: 17 单元 +19 + 两轮 recode +5 + 一轮 review +6
  - 两轮 recode + 一轮 review 共发现 2 个真 bug + 7 项改进, 加 6 个新不变量测试:
    - bug 1 (recode): cache key `.4f` 让 1e-30 ≡ 0.0 碰撞 → `repr()` 修复
    - bug 2 (final recode): cache key `None` ≡ `""` 共用 namespace → 哨兵区分修复
    - review R1-R8: CI rapidfuzz / 单跑 pytest / prompt_version 状态文档 / env 间接引用递归 / smoke 副作用清理 / Makefile 守门 / 哨兵 ASCII 化

## 3. 配置系统（Phase 4d）

`news_process.core.config.load_config()` 自动检测两种模式:

- **Split mode (优先)**: `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
  全部存在 → deep-merge 加载，外部 prompt `.txt` 自动内联到对应 `_template` 键
- **Legacy mode (向后兼容)**: 7 个 split YAML 全部缺失时 → 退回单文件 `config/config.yaml`
  （若只缺一部分 split YAML，loader 会显式报错以避免静默读到不完整配置）

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
v3.7.4 + v2.3 (HEAD)        ← 当前 (2026-05-30; Plan A title-track + Panel D/E + audit-verified 修复; 权威见 CLAUDE.md; 未独立 tag)
v3.7.1/3.7.2/3.7.3          中间增量 (ctx_fallback / title-track robustness; 未独立 tag)
v3.7.0 (PR #9-#13)          D 组 BERTopic + staleness + α + LLM CEO NER (未独立 tag)
v3.6.0                      Plan E 双轨闭合 + 新 stage 13 ctx 物化 (2026-05-18 锁定)
v3.5.x (v3.5.0/v3.5.1)      Stage 3 D2/D3/D4 augmentation + A1/A3 supplementation (未独立 tag)
v3.4.0                      第三维度 collab_mode (未独立 tag)
8d33c46                     post-v3.2.0 multi-paper extension (2026-05-15)
v3.2.0                      v3.2.0 release: Stage 3 dual-track + Stata 数据层 + 14 模板 + 4 CLIs
v2.1.0 / phase-9-baseline   v2.1.0 (recode follow-up: 见历史)
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

- **v3.0 主迁移 (留待真正的 major bump; shim 数已从 v2.1.0 的 26 增长到 v3.7.0 的 39)**: 删除全部数字前缀 thin shim,
  把 `core/dag.py:StageSpec.script` 从文件名改为 module path
  (`"news_process.pipeline.filtering.news_bank"`),
  把 `core/stage.py:run_stage` 从 `subprocess.Popen([python, script_path])`
  改为 `subprocess.Popen([python, "-m", module])`. 详细计划与外部影响面
  评估见 [`docs/guides/thin_shim_pattern.md`](docs/guides/thin_shim_pattern.md)。
- **极低优先级**: `data/processed/<group>/` 业务组子分区。当前 Phase 8 的"单层重命名"方案保留扁平布局；若未来出现存储分层、按组冷存储保留策略等场景，可参考 `scripts/migrate/migrate_data_layout.py` 完成深一级分组。但需注意：跨阶段交叉读取（如 stage 21 读 stage 14、stage 24 读 stage 23）会迫使 `CONFIG['filenames']` 携带组前缀信息，反向增加耦合，违反 DRY — 不推荐做此细分。
- **历史命名遗留** (Phase 9 范围外, 留待 v3.0): `papers/bank_fintech_tone/analysis.py:35` 的 `_LOGGER` name 仍含 v1.x paper id `news_process` (应为 `bank_fintech_tone`); 同文件 docstring 中 `python -m news_process.run_paper news_process` 同样残留。

> **Phase 7a (2026-05-04)** 已完成 8 个 pipeline 类 root body 迁入 `pipeline/<sub>/` + thin shim 化。
> **Phase 7b (2026-05-04)** 已完成 13 个 validation 类 root body 迁入 `news_process/validation/` 扁平布局 + thin shim 化。
> **Phase 8 (2026-05-04)** 已完成 `data_processed/` → `data/processed/` 单层重命名。
> **Phase 9 (2026-05-08)** 完成 4 个 post-restructure cleanup 子任务 (9c/9d/9a/9b) + v2.1.0 release。

## 8. 文献依据汇总

详见 `CHANGELOG.md` 中各 phase 提交的学术对标 + `news_process/papers/<paper>/__init__.py` 的论文级引用。
