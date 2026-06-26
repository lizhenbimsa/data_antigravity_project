# 全项目缓存策略 — 执行计划 (CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25)

> **本文件 = 策略层 (WHY / 路线图)。逐文件实现细节 (HOW / diff) 一律以
> `CACHE_STRATEGY_SPEC_V2_2026-06-25.md` (v2) 为唯一权威来源。** 本计划与 v2 已对齐, 凡冲突以 v2 为准。
>
> 文档链: 本执行计划 → diff 规格 v1 (已废, 仅存档) → 9-agent 对抗验证 (`CACHE_STRATEGY_VERIFICATION_2026-06-25.md`,
> 18 CF) → **v2** (折入全部修正, 唯一实现来源) → 本执行计划对抗验证 (`CACHE_STRATEGY_PLAN_VERIFICATION_2026-06-25.md`,
> 20 confirmed + 2 新发现) → 本计划已据此重建对齐。
>
> ⚠ **恢复说明**: 本文件曾在一次工作流验证中被某 agent 越权删除 (损坏仅此一文件); 现据历史内容 + 验证修正**重建为
> v2 对齐版** (非 stale 原版)。原版的 18 处 stale 内容 (与 v1 同源) 已全部修正。

---

## §0 核心判断

本项目**不缺缓存, 而是已有两套事实上的统一缓存层**, 策略重点 = **补漏 + 加一个关键功能**, 非另造:

1. **内容寻址计算缓存层** = `core/caching.py::LLMCache` (`_llm_cache.db`, SQLite)。键 =
   `sha256(SCHEMA_VERSION | model | 逐字内容 | prompt_version | temperature[|seed])`。已覆盖 LLM API (stage21/48) +
   embedding API (stage16/27/network/strategic) + 本地 text2vec (`_encode_local_cached`, 2026-06-23)。**golden 复现锚点, 勿删。**
2. **阶段级粗粒度缓存** = 每 stage 落 `data/processed/NN_*.parquet`; 但编排器**不消费**它做跳过 (仅 stage21 一个特例)。

四件事 (非"造新缓存"):
- **A 补"最后一公里"**: `data_versioning.py` 已把 `config_hash + input_hashes` 写进每个 parquet 的 schema metadata,
  但编排器**从不读它**做 skip → 实现通用 `--skip-unchanged` (ROI 最高单一杠杆; 见 W5)。
- **B 堵 silent-staleness**: 4 个"改代码但缓存仍命中旧值"漏洞 (`batch_size` / `MEDIA_NAME_OVERRIDES` / `PEER_PROMPT` / prompt byte-identical)。
- **C 推广现成模板到 2 个未缓存昂贵路径**: stage25 SBERT + stage23 BERT (复用 `_encode_local_cached`)。
- **D 缓存卫生**: 验证阶段变体响应写进了生产锚点库 → 建独立验证 DB 隔离; MinHash 签名持久化。

**P0 = 无** (LLM/embedding/preprocess 三大缓存设计正确, 无救火项)。

## §1 现状基线 — 已成熟、不要动 (keep-as-is)

| 缓存 | 机制 | 现状 (本轮验证已逐字核实) |
|---|---|---|
| LLM 投票 / embedding API / 本地 text2vec | `LLMCache` 穿透 | 6 个生产 callsite + `SCHEMA_VERSION='v1'`; prompt_version 接入; 离线守卫 |
| stage00 预处理 per-file | parquet + `config_hash` + `PREPROCESS_CODE_VERSION` | 内容寻址范本 (`_constants.py:131`) |
| HF 模型离线 | `HF_HUB_OFFLINE=1` | stage23/25 已设 (`tone_berts:130`/`article_sbert:90`) |
| stage21 单点跳过 | 三重指纹安检 | 唯一已落地的阶段级内容寻址跳过 |

**计时现状 (本轮验证 F16 订正; 真机 perf-audit T=2 RTX3090 实测)**:
- stage23 BERT ~297s → HF 离线后 ~194s (**真瓶颈**)。
- stage25 SBERT ~107s 是 **HF 离线前 baseline**; **现已 HF 离线, ~14.2s** (勿再把 107s 当当前态论证 SBERT 缓存收益)。
- stage22 词典 ~92s。
- ⇒ SBERT/BERT 缓存的真收益 = **整阶段免重算全量 4-6h** (配合 W5), 非省单次秒级。

**事实陷阱备案 (本轮验证 F5)**: `article_sbert.py` 6 处把所用模型 max_seq 误注释为 **512**, 实为 text2vec-base-chinese 的
**128** token。本计划与 v2/验证报告均未照抄此错 (grep '512' 全 0)。修 W7 时顺手订正源码 6 处。

## §2 缺口全景 (13 工作项)

| # | 工作项 | golden | 批次 |
|---|---|---|---|
| W1 | batch_size 纳入 t2v 版本纪律 | safe | 批1 |
| W3 | PEER_PROMPT frozen-hash 护栏 | safe | 批1 |
| §5 | 缓存版本门治理 (写进 caching.py docstring) | safe | 批1 |
| W6 | StageSpec 加 inputs/fingerprint_cols | safe | 批2 |
| W5 | 通用 --skip-unchanged 阶段级增量 | safe | 批2 |
| W4 | 验证缓存隔离 _llm_cache_validation.db | safe | 批2 |
| W9 | MinHash 签名 sidecar | safe | 批2 |
| W11 | Stata run_do 内容寻址跳过 | safe | 批2 |
| W12 | HF 离线 (引擎单点 + stage15 模块顶; stage15 刻意保裸路径不改走引擎, 见 v2 W12 DOC-1) | safe | 批3 |
| W13 | legacy 死代码清理 (+test 同步) | safe | 批3 |
| W7 | SBERT 复用穿透缓存 | **needs-regen** | 批4 |
| W8 | BERT 推理缓存 (默认关) | **needs-regen** | 批4 |
| W10 | 词典 powerset 单次扫描重构 | **needs-regen** | 批4 |

**golden 总账 = 10 safe / 3 needs-regen (W7/W8/W10)**。逐项 file:line diff 见 v2。

## §3 分批 (与 v2 §0/§2-§5 完全对齐)

- **批1 — 失效护栏** (纯注释/文档/单测, 零行为变更): W1 + W3 + §5。可立即上线。
- **批2 — safe 基建**: W6 (前置) → W5 (旗舰通用 skip) + W4 + W9 + W11。父进程只读元数据决定 spawn, 字节中性。
- **批3 — safe 清理** (同 PR): W12 + W13。
- **批4 — needs-regen** (攒 DEFERRED 统一受控重生): W7 + W8 + W10。

> **W5 设计要点 (本轮验证 F2/F3 修正, 以 v2 §3 为准)**: 用**哈希 split YAML 文件内容**口径 ——
> producer 把 7 个 YAML 的 `compute_file_hash` 写进 metadata, 编排器按 `STAGE_CONFIG_FILES` (stage→YAML 文件名) 比对,
> **绕开 CONFIG dict** (真机实证 `filtering/sentiment/features/panel` 非 CONFIG 顶层键, 旧"config 子树 hash"会对这 4 域全盲 =
> silent staleness)。默认 Namespace 须含 `skip_unchanged=False` (否则 10+ 无参 `run_pipeline()` 崩)。不接验证 runner (其 stage 无 parquet 产物)。

## §4 golden 耦合 & 重生窗口

- 批1/2/3 (10 项) 全 **safe**: 离线 $0, 不触 golden, 可独立提交。验收 = 产物 content-sha256 逐位一致。
- 批4 (W7/W8/W10) **needs-regen**: 首跑须受控环境 (`PYTHONHASHSEED=0` + `MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1` + 保留 GPU +
  HF offline), **与既有 DEFERRED 批** (`_allv` / inject-fintech / rule-ablation / media-canon) **一次合并受控重生 golden**,
  避免本机裸环境误 bless 3 个 BLAS-FP 网络列等无关漂移。
- **W7 重生理由 (本轮验证 F4 修正)**: 不是 1e-7 归一漂移, 而是**表征机制变化** (截断 128 vs 126-token 分块 mean-pool),
  `semantic_staleness_*` 显著变 + 涉 Bybee 构念 → 见 v2 §5 W7 的 (a)/(b) 决策点 (含 token 级截断细节)。

## §5 统一治理: 版本门纪律 (横切; 成稿落 `core/caching.py` docstring 末尾, 见 v2 §2)

5 条铁律: **A** 新键首字段=`SCHEMA_VERSION`; **B** 改语义参数进键或绑 version token; **C** FP 敏感超参
(`batch_size`/`device`/`dtype`/线程/`torch`版本) 当版本维度; **D** version token 优先放可 lint 位置 (内联常量须配 frozen-hash 单测);
**E** 资源文件 (词典/anchor/`MEDIA_NAME_OVERRIDES`) 以内容 sha256 入键。

现存版本门定位 (本轮验证 F15 修正): `PREPROCESS_CODE_VERSION` **定义在 `pipeline/preprocess/_constants.py:131`** (非 runner.py);
其余 `SCHEMA_VERSION`@`caching.py:141` / `unified_cot.txt:1` / `PEER_PROMPT_VERSION`@`llm_peer_iv.py:339` /
`text_pipeline_version`@`features.yaml:29`(api)/`:41`(t2v)。

## §6 验收门禁

- `pytest -m fast` + `test_dag_consistency` (W6 后) + 新增单测 全绿; `ruff check` clean。
- safe 批: 离线跑相关 stage, 产物 content-sha256 与改动前逐位一致。
- needs-regen 批: 受控环境冷跑 == 暖跑逐位一致 → 受控重生 golden → `test_panel_reproducibility` 绿。
- 计数不变 (W6 加字段向后兼容默认空): STAGES_MAIN/VALIDATION / shim / OUTPUT_REGISTRY 不变。

## §7 明确"不做" (防误优化)

- stage22 词典法不加 LLMCache (纯 CPU $0, 加缓存反增失效负担; jieba pin 是事实版本门)。
- 跨阶段共享 jieba token 缓存 (15/22/24 是刻意隔离的不同注入态, 盲共享会改语义破 golden)。
- 去重 LSH 索引跨阈值复用 (阈值进 banding 构造, 固有不可复用; 阶段内 `_tok_cache` 已最优)。
- stage24 herd TF-IDF 细粒度记忆化 (非热点; 靠 W5 整阶段 skip 覆盖)。
- build_replication / codebook / figure PNG 细粒度缓存 (廉价确定性, golden 无关, ROI 太低)。

## §8 推荐执行顺序

批1 (W1/W3/§5) → 批2 (W6→W5/W4/W9/W11) → 批3 (W12/W13) → [以上全 safe, 离线 $0] → 批4 (W7/W8/W10, 攒 DEFERRED 统一重生)。

## §9 决策点 (2026-06-26 已结)

1. ✅ **W7 = (b) 分块 mean-pool** (用户拍板): 用满标题+300字 + 与全项目 t2v 一致 + 修潜伏 bug; batch4 实现, 落地须 manuscript 披露构念变 + 报新旧 staleness 相关性。详见 v2 §5 W7 (切勿加 token 截断)。
2. ✅ **W1 不补 bump** (用户拍板): _t2v 缓存盘上本就 batch=128 自洽; 版本号保持 `v2-2026-05-29-t2v`, 留 batch4 DEFERRED 重生顺手 bump (免费)。
3. ✅ 批4 (W7(b)/W8/W10 + W1 顺手 bump) 攒 DEFERRED golden 窗口统一受控重生 (与 _allv/inject-fintech/rule-ablation/media-canon 合并)。
4. **进度**: 批1/2/3 的 **10/10 safe 项全部已落地+验证** (W1/W3/§5/W6/W5/W4/W9/W11/W12/W13); 仅 batch4 (W7(b)/W8/W10, needs-regen) 留 DEFERRED 窗口。
