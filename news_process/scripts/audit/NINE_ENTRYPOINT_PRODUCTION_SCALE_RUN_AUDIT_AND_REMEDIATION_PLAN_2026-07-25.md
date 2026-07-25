# 九入口**生产规模**顺序真跑审计与整改执行计划 (2026-07-25)

基线: main=`de6d7a83` (stage21 平局重试预算解耦后)。工作树起点干净; 本轮前置整改已入库
main=`6e5beb89` (F1/F2/F3/F4/F5 + 10 个新 gate + 本计划文档)。

**与前九轮的本质差异**: 前九轮 (2026-07-10..07-22) 的 ②③④⑤⑥⑦ 全部跑在 **T=2 dev 语料**
(833–1,151 行) 上; 本轮是主线 **stage 22 及其下游 (22/23/24/25/26/40/46/51) 首次在生产语料上真跑**
—— 上游 00→21 已于 2026-07-24/25 完成生产真跑 (stage 21 输出 **169,807 行 / 保留率 70.17%**)。
∴ 本轮暴露的问题以「**只在生产规模才触发**」为主, 与前九轮的 dev 规模发现不同型, 不可互相援引。

---

## §1 运行矩阵

| # | 入口 | 模式 | 结果 | 耗时 | 备注 |
|---|------|------|------|------|------|
| ① | LLMs_for_FinTech_dic/00_LLMs_for_dic.py | `LLMS_DIC_OFFLINE=1` | **EXIT=0** | 43.65s | 0 ERROR / 0 WARNING; 阶段②保留 696/915 (76.07%); 产 `bank_keywords_20260725_215401.xlsx` |
| ② | run_pipeline_function.py | 无 flag 全 16 阶段 (生产语料) | (§6 回填) | — | 2026-07-25 23:56:18 启动 (PID 22088); 与 stage25 播种**刻意重叠**, 见下方时序说明 |
| ③ | run_pipeline_validation.py | 全 16 验证阶段 | (§6 回填) | — | |
| ④ | run_paper.py | `--list` + 逐篇 `--stage tables` / `--stage figures` (**刻意不用默认 `all`**, 见 F13) | (§6 回填) | — | |
| ⑤ | 80_placebo_and_alt_anchor.py | — | (§6 回填) | — | |
| ⑥ | 81_stata_data_audit.py | — | (§6 回填) | — | 上轮基线 0 FAIL / 18 WARN / 142 PASS |
| ⑦ | 82_export_stats_excel.py | — | (§6 回填) | — | |
| ⑧ | company_listed_bank/run_pipeline.py | 全链 01→04 | (§6 回填) | — | |
| ⑨ | company_tax_bank/run_pipeline.py | 全链 01→04 | (§6 回填) | — | |

**前置工作与实际时序 (⚠ 与初稿计划不同, 据实记录)**:
- **②启动前已完成**: ① 真跑; **P0 内存校准** (CLAUDE.md 明载「T=19 首播前必先跑」) → F1;
  **F1/F2/F3/F4/F5 代码整改 + 两组字节等价 A/B 实证** + 10 个新 gate; fast 基线复核
  (12 FAILED + 20 ERROR = 11 慢性 + 21 docid 半迁移, **0 新增**)。
- **②启动时仍在进行**: **stage 25 嵌入生产首播播种** (三轨并集去重 539,282 唯一文本;
  MAIN 与 `_lg` 各 miss 377,520 条)。
  **刻意重叠的依据**: ② 的执行序为 00→…→24→25, 从 00 跑到 25 至少 6–8 小时, 而两家播种
  ETA 分别 ~1.5h / ~2.7h ⟹ ② 抵达 stage 25 时播种早已收尾; 重叠可省 ~2.7 小时墙钟。
  **风险与兜底**: 播种是网络/TPM 受限 (CPU 占用低), ② 是 CPU 受限, 资源面基本正交;
  播种器具块级容错 + 8 遍收敛; §9-3 中止判据仍对「stage 25 整轨 NaN」保持硬止损。
  ⚠ 该重叠是**运行决策**, 若复现本轮请按各自机器实测 ETA 重新判断, 勿照抄。

---

## §2 定谳发现 (四闸: 真 / 可验证 / 非设计 / 值得)

### F1 [BLOCKER · 已修] stage 22 boilerplate 硬闸未校准 → 生产必然 `SystemExit` 连坐 nuke 整批

- **真**: `df_dict_budget_hard=40_000_000` 是 2026-07-06 计划写死的**未校准保守占位** (计划 §2.2
  自述「勿将 40M 当作已由 128GB 反推的既成值」)。
- **可验证 (P0 实测, 真实互异嵌套前缀, 禁重采样)**: 在生产 stage21 gated 语料 `content_full`
  (169,807 篇 / 256,764,710 字符) 上跑分块 Pass1, 得增长曲线:

  | D (篇) | global_df (entry) | ΔRSS |
  |---|---|---|
  | 2,000 | 4,052,566 | 0.66 GB |
  | 8,000 | 12,245,870 | 1.67 GB |
  | 16,000 | 21,975,166 | 2.44 GB |
  | 28,000 | 36,260,237 | 4.04 GB |
  | **32,000** | **40,282,765** | 4.32 GB |
  | 40,000 | 48,236,067 | 5.84 GB |

  Heaps 拟合 (后 10 点) **β=0.8266 / k=7,589**; per-entry = **130.1 B** (进程 RSS delta 实测,
  调和了旧文档 96B/entry 与 200B/entry 的口径矛盾)。
- **后果**: 硬闸在 **D≈32,000 篇 (全文轨约 19%)** 处触发 `SystemExit`; 而该 `SystemExit` 位于
  boilerplate 派生**保存之前** → 连坐 nuke 整个 stage-22 本轮已算产出 (6 词典 × 3 轨 × 8 变体 +
  IDF + clarity + LM + FLS 全部作废)。
- **修**: 按 128GB 反推重设 `df_dict_budget_hard=400_000_000` (≈52 GB) / `df_dict_budget_warn=100_000_000`
  (≈13 GB)。反推留量: 52 (global_df) + ~17 (worker) + ~10 (df/其它) ≈ 79 GB, 余 ~49 GB。
- **附带结论 (推翻既有铁律)**: 生产 D=169,807 外推 **M≈1.596 亿 entry ≈ 19.3 GB** → **tier1 对本
  语料规模已可产**, tier2 (disk-backed DF) **非必需**, 仅在外推 >4 亿 entry (约 D>50 万篇) 时才需
  裁定启用。CLAUDE.md「T=19 OOM 未解决」须订正 (§4 WP-D)。

### F2 [MAJOR · 已修] `embedding_engine` 写行完备计数在重试路径重复自增 → 瞬时 DB 故障放大成整轨崩溃

- **真 + 现场实证**: 2026-07-25 22:35 生产 stage25 播种实弹 —
  `AssertionError: 写行完备性异常: written=2108 != N=2000` (紧随一条
  `OperationalError: disk I/O error`)。超出量 108 与「一个 API 批 (50,000 token 预算下
  ≈108–142 条) 被重复计数一次」量级一致 (⚠ 批边界未逐条留证, 此为机理推断而非直接观测;
  但下方机理链本身可由代码行序独立证实, 不依赖该数字)。
- **机理**: `_rows_written += len(batch)` 位于 `cache.put_batch(...)` **之前**。put_batch 抛
  `sqlite3.OperationalError` (`disk I/O error` / 并发 `database is locked`) → 被外层泛
  `except Exception` 捕获 → **整批重试** → 重试成功后再次 `+= len(batch)` → 终局
  `assert _rows_written == len(texts)` 误报 → **AssertionError 冒泡**, 走的不是设计好的
  「重试耗尽 → 返回 None → 该轨优雅置 NaN」路径, 而是硬崩。
- **二次损害**: 该重试还会**重新调用一次付费 API** (向量本已算好并写入 `out`)。
- **修 (两处)**:
  1. 计数器 → **幂等写行掩码** `_written: np.ndarray(bool)`, 按全局行号置位 → 同批重试任意次
     结果不变; 断言语义 (防漏写/双写/错位) 不变, 且失败信息新增「未写行号前 10」。
  2. `cache.put_batch` 单独 `try/except`: 失败 → loud WARNING, **不重试、不重调 API**
     (本批向量本轮有效, 下次 run cache miss 重调自愈) —— 与既有归档失败语义 (`_archive_ok`) 对称。

### F3 [MAJOR · 已修 · 性能] stage 22 两处 `prefer='threads'` 在生产语料上被 GIL 锁成单核

- **真**: `tone_words.py` 的 ③IDF 文档频率 (`_compute_chunk_df`) 与 ④三轨词典打分
  (`classify_batch`) 均为 `Parallel(n_jobs=-1, prefer='threads')`; jieba.cut 与打分状态机是纯
  Python 持 GIL → 32 核退化为单核。**与 stage 15 (2026-07-24, main=07c2b4c6) 同型病根**。
- **可验证**: 真数据实测 (2,400 行生产语料, 12 批) 线程臂 **218.2s** = 0.0909 s/篇 →
  外推 169,807 篇 ≈ **4.3 小时** (仅④); ③IDF 另 ≈6.5 分钟。
- **修**: 镜像 stage 15 §1b「工况自适应后端」— 批数 ≥ `_PROC_PARALLEL_MIN_BATCHES=8` 切 loky
  进程后端, 之下保持线程 (dev/pytest 零行为变化 + 免 Windows spawn 开销)。worker 侧
  `_ensure_worker_dicts()` 幂等自建同集同序词典 + jieba 注入态; **IDF 权重是语料级产物, 由主
  进程算好整体传入 worker, 绝不在 worker 重算**。
- **字节等价实证**: 2,400 行 × 12 批 A/B — **556 列逐列逐位一致 (含 NaN 位与 dtype) + 55 键
  stats 聚合一致**; IDF 权重逐词逐位相等。**提速 4.71×** (218.2s → 46.3s)。

### F4 [MAJOR · 已修 · 性能] boilerplate char_wb 分词串行 ≈52 篇/s → 三轨双遍 ≈3.7 小时

- **真**: exact two-pass 对 char_wb (4,6)-gram 分词两遍, 纯 Python CPU 热点; P0 实测
  1,000 篇 19.2s → **52 篇/s**。三轨 (full 1512 字 / ctx 932 / ss 608) 双遍合计 ≈3.7 小时。
- **修**: Pass1 (分块 feats/DF/totals) 与 Pass2 (固定 sorted 词表逐文命中) 均改 loky 进程并行,
  结果以 **generator 逐块消费即弃** (禁一次性物化 43 块 × ~200MB 序列化)。
- **字节等价论证 (by-construction)**: ① Pass1 的 `global_df` 值 = 各块 DF 的整数求和,
  结合/交换律 ⟹ 与块大小/完成序/n_jobs 无关 (模块既有「不变量 I」); ② `per_doc_total` 按全局
  行号回写 (不变量 II); ③ `boiler_set` 的 list 序随插入序变, 但下游只消费 `sorted(...)` 与
  order-independent 的 min/median/max, top-k 日志按 `(-DF, 字面)` 全序排序 ⟹ 无输出依赖插入序;
  ④ Pass2 逐文独立; ⑤ 并行段纯整数计数, **零浮点累加** ⟹ 无 FP 结合律风险。
- **字节等价实证**: 真实生产语料 6,000 篇三臂对拍 — **A (legacy 单遍) = B (串行分块) = C (进程
  并行) 逐位相等** (nan 位一致 + 非 nan 逐位相等)。

### F5 [MAJOR · 已修 · 本轮整改自身缺陷] 进程后端 `n_jobs=-1` 在 32 核机上 MemoryError

- **真 + 现场实证**: F3 首版用 `n_jobs=-1` → 32 个 loky worker, 每个各持一份六部词典
  (31,966 词条) + clarity/LM 子词典 + **注入 44,983 自定义词的 jieba Trie** (~0.6–2 GB/worker)
  → 2026-07-25 22:37 直接 **MemoryError** 崩掉整批 A/B。
- **修**: 进程臂固定 worker 上限 `_PROC_PARALLEL_MAX_WORKERS=12` + config 覆盖口
  `sentiment_analysis.tone_words.proc_workers`; 线程臂共享同一份词典/Trie, 无此问题, 仍沿用
  config `n_jobs` (行为与旧版一致)。boilerplate 侧同理 `n_jobs: 12` + `par_chunk_size: 4000`
  (控 worker 峰值 ≈1.4 GB)。
- **教训 (方法论)**: 「整改本身必须再被审」再次兑现 —— 性能整改在 dev 规模不暴露内存面,
  必须在生产规模实弹后才敢定稿。

### F6 [MINOR · 报告 + 建议, 本轮刻意不改] `LLMCache` 并发写语义

- `core/caching.py::LLMCache.__init__` 用 `sqlite3.connect(db_path, check_same_thread=False)`,
  **未显式设 busy_timeout** → 取 Python 默认 5s (已实测 `PRAGMA busy_timeout` 返回 5000)。
- 更关键: `get()` 用 `fetchone()` 取单行, 语句未被走完 → 该连接残留**未耗尽的读事务**;
  其后 `put_batch` 的 INSERT 构成「读事务升级为写」, SQLite 为避免死锁**刻意不调 busy handler**,
  直接返回 SQLITE_BUSY → 即使把 busy_timeout 调到 600s 也**秒级** `database is locked`
  (2026-07-25 22:33 实测)。
- **定性**: 生产主线是**单写者**路径 → 现状不触发; 仅在「多进程同时写同一缓存库」(本轮双模型
  并行播种) 时暴露。∴ 本轮**不动**这一 golden 承重模块, 改以**分库写 + 事后单写者合并**规避
  (§3 P2), 并在此留档为后续加固候选 (建议: `get()` 改 `fetchall()[:1]` 或显式
  `cursor.close()`; `connect(timeout=...)` 显式化)。

### F7 [MINOR · 报告] `get_embeddings_api` 对同一次调用内的重复文本不去重 → 生产规模重复付费

- `missing_indices` 逐 index 收集, 同一文本出现 k 次即被请求 k 次。
- **实测重复率** (stage 25 文本构造 = `content_{track}[:400]`): full 轨 242,000 → 214,724 唯一
  (**11.27%** 重复) / ctx 2.88% / ss 4.46%。跨轨重复由缓存兜住 (第二轨命中), **轨内重复仍重复付费**。
- 本轮以播种器侧全局去重规避 (539,282 唯一文本 → 实际缺口 377,520/模型); 引擎侧去重列为建议。

### F8 [MINOR · 报告] 泛 `except Exception` 把 SQLite/磁盘错误一律记为「网络异常」

- `_process_batch` 的 `except Exception` 分支日志文案硬编码「网络异常 (batch N)」, 实际捕获到的
  是 `OperationalError: disk I/O error` / `database is locked`。与 2026-07-25 stage21
  「400 内容风控被误报为连续 80 次超时」**同型误导**。F2 的 put_batch 独立 try 已覆盖最主要的
  DB 误报源; 其余瞬时异常文案改写列为建议 (不在本轮改, 避免与 F2 同文件多点变更混淆归因)。

### F9 [观察 · 生产规模内存] stage 25/26 峰值

- T=2 基线 `25_article_embeddings.parquet` = 61.07 MB / **1,047 行** (实读 parquet 元数据校正,
  非 stage13 的 1,151) ≈ 58.3 KB/行 → 生产 242,000 行外推 **≈14.1 GB parquet**;
  内存态下界 (3 轨 × (4096+3072) float32 × 242,000) = **20.8 GB** (pandas object 列另加每行
  6 个 ndarray 对象头 ≈145 MB)。
- stage 26 再在其上建 Faiss `IndexFlatIP` 滚动窗口 (另一份 float32 拷贝) → 峰值估 **50–60 GB**。
  **须在 ② 运行期监控 RSS**; 若逼近 100 GB 须中止并改分轨/分窗流式 (本轮不预改, 无实证不动刀)。

### F9b [观察 · 生产规模] stage 40/46/51 面板链

- stage 40 在生产语料上首次消费 169,807 篇 (旧代 833 篇) → 步骤 8z (IV 扩展 · llm_peer PEER
  prompt)、网络三轨 ×33 指标 ×3 判据、benefit 六轨冻结中心等全部按新规模重算。
- **已知强耦合**: `_benefit_center_sidecar.json` 的四指纹含 `dict_sha256` (2026-07-22 加固),
  词典未变 ⟹ 冻结中心**沿用**; 但其 median 是在 **833 篇 T=2 语料**上冻结的 → 生产 169,807 篇
  语料下该阈值的代表性存疑。**本轮记为报告项** (是否重冻结属研究决策, 不擅自改)。
- 面板行数将由 172 行 (86 banks × 2 years) 跃至生产规模 (bank_list 全量 110 家 × 2007–2025);
  最宽 dta 列数随之漂移 → **勿以旧基数心算**, 一律实读。

### F10 [观察 · 生产规模墙钟] stage 23 BERT

- `deterministic_mode: cpu_strict` ⟹ GPU 路径关 AMP + 关 cuDNN benchmark (刻意, 为位级可复现),
  FP32 推理; 3 模型 × 3 轨 × 滑窗 (stride 0.5, max_length 512)。RTX 3090 24GB。
- `inference_cache: true` ⟹ 首跑昂贵、重跑廉价 (`_local_model_cache.db` 现仅 4.7 MB = T=2 代)。
- 本轮**不改**任何 BERT 数学层/批大小 (改 `inference_batch_size` 会改缓存复合键且可能改 cuBLAS
  kernel 选择 → 破位级可复现)。实际墙钟以 ② 日志为准 (§6 回填)。

### F13 [MAJOR · 运行契约不可扩展 · 本轮以参数规避并披露] 入口④ `--stage all` 内嵌重跑整条主线

- **真 (代码级)**: `run_paper.py` 默认 `--stage all` → 各 paper 的 `analysis.main()` 中
  `if args.stage in ('pipeline', 'all'): run_main_pipeline(_extra)` → 直接调
  `run_pipeline_function.run_pipeline()` **全 16 阶段**。
- **T=2 无感, 生产不可扩展**: 上轮 (2026-07-22) 11 篇各 ~1,230s 因为主线在 T=2 只要 ~20 分钟;
  生产语料下主线单趟 ~10–16 小时 ⟹ 11 篇 = **110–176 小时**, 且会把 stage 21/25 的
  预清理-重跑循环重复 11 次 (含每次少量 cache miss 的付费调用)。
- **本轮处置 (刻意偏离 + 披露)**: ② 已在同一代际跑完主线 ⟹ ④ 改为
  `--list` + 逐篇 `--stage tables` 与 `--stage figures`。二者并集 = `all` 减去**冗余的**
  主线重跑, paper 侧产物 (表/图) 覆盖率 100%。
  - 备选 B (未采用): `--stage all --skip-21-if-exists --skip-unchanged` 让内嵌主线自跳过 —
    更贴近「原样跑入口」, 但 `--skip-unchanged` 带 F9 已知边界 (stage 40 可能被跳过 →
    opt-in 特征列保留旧值), 且 11 次跳过校验本身也要小时级, 收益不抵风险。
- **建议 (研究决策, 本轮不改代码)**: 给 `run_paper.py` 增一个 `--assume-pipeline-fresh`
  或把 `--stage` 默认值从 `all` 改为 `tables,figures`, 使生产规模下的默认路径不再隐含
  一次全链重跑。

### F15 [研究决策已裁定 · 2026-07-26 用户指令] stage 25 输入构造 v1 (Bybee 400 字) → v2 (整篇)

- **裁定**: 用户 2026-07-26 指令「将语义陈旧度改成整篇」。落点在 **stage 25** 的文本构造
  (⚠ 用户表述为「stage 26 播种」, 实际 stage 26 不调任何 API — 纯 CPU MinHash+faiss,
  只消费 stage 25 的向量; 已当面澄清后按 stage 25 执行)。
- **改法**: 与 stage 16 `policy_alignment.main()` **逐字节同构** —— full 轨 `.str.strip()`,
  ctx/ss 轨**不** strip (照抄其既有不对称), 无预截断, 超长交引擎切块+token 加权池化。
  新增 `INPUT_STRATEGY` 开关 ('whole_text_v2' 现行 / 'bybee400_v1' 退役可回退) + 产物
  provenance 列 `sbert_input_strategy`。
- **v1 理由已失效 (改动依据)**: v1 的书面理由是「避免 SBERT max_seq_len=512 截断丢尾」,
  属 v3.14.0 之前的**本地 SentenceTransformer** 时代; API 化后单条上限 8191 token,
  生产实测块扩展因子 **1.0118** (99% 单块直送)。
- **收益 (实测)**: 只读探针 — 三轨并集 **582,724 唯一块**, MAIN 与 `_lg` 各
  **582,724/582,724 命中 miss=0** ⟹ 本阶段**零新增付费嵌入**, 全部复用 stage 16 已播条目。
- **⚠ 头号陷阱 (已在代码/日志三处写死告警)**: 模块注释原写「改输入构造必须 bump
  `_TEXT_PIPELINE_VERSION`」—— 但该值是 **spec 级共享**命名空间 (`embedding_api.
  text_pipeline_version`), 被 stage 15/16/26/27/40 共用, **一 bump 全项目 117 万条已播
  嵌入整体作废需重播**。本变更**恰好不需要 bump** (新键与 stage 16 已有正确条目重合);
  代际改由不进缓存键的 `sbert_input_strategy` 列承载。gate `test_sbert_whole_text_v2.py`
  第 ③ 条锁死该不变量。
- **下游传导 (第一轮审核实查, 订正了初判)**: `25_article_embeddings.parquet` 的**唯一**
  真实消费者是 stage 26 (`article_staleness`) → `semantic_staleness_{full,ctx,ss}` +
  3 个 `_lg` 孪生 → 面板与 40/46/51。
  - ✅ **网络嵌入轨不受影响**: `network_spillover` 的 `W_emb` 由 `_embed_peer_texts` 自行
    嵌入 **bank-year 聚合超级文档**, 并不读 25 的产物 (其 L1922 注释「本嵌入轨依赖
    25_article_embeddings」是**第三处陈旧注释**, 同句还提到不存在的「stage 45」→ 并入 F14)。
  - ✅ 无基于语义嵌入的冻结 sidecar (grep 实证); stage 26 的 provenance 校验是宽松
    `if col in columns` 形式 → 新增列安全。
- **须复核的构念风险 (每次重生都要看)**: stage 26 的 surface 轨本就是**整篇** MinHash,
  semantic 轨改整篇后两者互补性可能下降。stage 26 已 emit G-D2.1 诊断
  (`corr(surface_staleness_full, semantic_staleness_full)`, 期望带 **[0.3, 0.7]**) →
  ②跑完必须读该值并如实披露; 若越出带外, 须在 manuscript 说明或重议口径。
- **沉没成本 (据实记录)**: 变更前已按 v1 口径播种 400 字嵌入 —— MAIN 侧 136/189 块
  (~27.2 万条, **已写入主库 `_llm_cache.db`**, 成为孤儿条目, 约 +25GB, 不影响正确性);
  `_lg` 侧 ~17 万条写在独立库 `_llm_cache_seed_lg.db` (6.5GB, **刻意不合并**, 保留在盘上
  以便万一回退 v1 时可用; 同理保留 `data/llm_archive_seed_lg/`)。
- **时序**: 变更时入口② 正跑在 stage 00, 尚未 import `article_sbert` (各阶段独立子进程,
  用时才起) ⟹ 编辑安全, 且②抵达 stage 25 时将自动使用 v2 新码。
- **待验 (② 抵达 stage 25 前必做)**: ② 会重生 `14_news_with_ctx.parquet`; 须在其重生后
  **重跑一次只读探针**确认仍 100% 命中 (理论上确定性重跑逐字节相同, 但不得假定)。

### F14 [MINOR · 陈旧注释误导 · 报告] 「stage 25 = strategic_diff」是重编号残留, 且其缓存论断已被实测证伪

- **三处** (第三处于 2026-07-26 F15 审核时追加): `core/dag.py:296` / `pipeline/filtering/
  policy_alignment.py:880` / `pipeline/panel/network_spillover.py:1922`。第三处写「本嵌入轨
  依赖 25_article_embeddings(当前缺), stage 45 未重跑嵌入 pass」—— 实际该轨由
  `_embed_peer_texts` 自行嵌 bank-year 超级文档、**从不读** 25 的产物, 且 `stage 45`
  不在 `STAGES_MAIN` 中。
- 前两处均写
  「stage 16 (policy_alignment) + **stage 25 (strategic_diff)**」。前者已于 2026-07-14
  fix(D5) 把 policy_alignment 从「stage 15」订正为「stage 16」, 但**漏改同句的 stage 25**。
- **实际**: `25_article_sbert.py` 才是 stage 25 (article-level 嵌入持久化); `strategic_diff`
  由 `pipeline/panel/runner.py` (stage 40 步骤 8e) 与 `policy_similarity.py` 消费, 无任何
  `25_*.py` 引用 (grep 实证)。
- **附带失实**: policy_alignment.py:880 据此断言「stage 25 嵌的是 (bank,year) 聚合超级文档
  (非文章级), **粒度错配不可能共享缓存**」。对**真正的** stage 25 (article_sbert) 而言此
  论断为假 —— 2026-07-25 实测: stage 25 三轨并集 539,282 唯一文本中 **161,762 条 (30.00%)
  直接命中既有缓存** (逐轨 ss 49.6% / ctx 26.0% / full 12.5%), 命中来源正是 stage 16/27
  的文章级嵌入 (当整篇文本 ≤400 字时, stage 25 的 `[:400]` 截断与整篇同字节 ⟹ 同缓存键)。
- **处置**: 本轮只报告 (注释层, 计算行为无关)。建议随下一轮注释批改把两处 stage 25 订正为
  「stage 40 步骤 8e (strategic_diff)」, 并删除已被证伪的「不可能共享缓存」论断。

### F11 [清理] 未跟踪残留

- `LLMs_for_FinTech_dic/data_processed/` 5 个 `judge_manifest_*.json` (07-23 ×4 + 本轮 ×1)
  + 本轮 ①离线重放产物 `bank_keywords_20260725_215401.xlsx`。按 2026-07-21 先例: 留档 sha256
  → 与 canonical 对账 → 删除重放产物, canonical 不动。

### F12 [文档] CLAUDE.md 承重断言须订正

- 「⚠ **生产 T=19 铁律**: … T=19 OOM 未解决, 须补 tier2 (DEFERRED); `df_dict_budget_hard=40M`
  是未校准占位, 生产 global_df 极可能超之 → Pass1 内 `SystemExit` 连坐 nuke 整批 stage-22 →
  T=19 首播前必先跑计划 §3-P0 按 128GB 反推校准硬闸」
  → **P0 已跑完并落地**, 该段须整体重写 (见 §4 WP-D)。

---

## §3 前置工作包 (② 启动前)

- **P0**: 见 F1, 已完成 (校准脚本与曲线留档于本文件 §2-F1 表)。
- **P1 代码整改**: F1 (预算) + F2 (掩码/put_batch) + F3/F4 (并行) + F5 (worker 上限)。
  验收 = ruff 通过 + `test_boilerplate_chunked` (17) + `test_boilerplate` (9) +
  `test_embedding_engine_streaming` 全绿 (41 passed) + 两组真数据 A/B 字节等价。
- **P2 stage 25 嵌入生产首播播种**: 沿用 2026-07-24 stage 16 首播先例的**分块播种器**
  (块级容错 + 多遍收敛), 文本构造逐字节复刻 `article_sbert._build_track_docs(title_col=None)`
  (= `content_{track}[:400]`)。
  - 缺口盘点 (只读, $0): 三轨并集去重 **539,282** 唯一文本; MAIN (Qwen3-8B @硅基流动) 与
    `_lg` (text-embedding-3-large @yunwu) 各 miss **377,520** 条。
  - **并行策略**: `_lg` 写入独立缓存库 `_llm_cache_seed_lg.db` + 独立归档根
    (`data/llm_archive_seed_lg/`), 规避 F6 的跨进程写锁与 `threading.Lock` 只在进程内生效导致的
    jsonl 交错损坏; 播种完成后以**单写者**方式合并回 `_llm_cache.db`。
  - 收尾验收: 两模型各 0 剩余 miss (播种器终验) + 合并后主库探针复核。

---

## §4 整改工作包 (跑完后)

- **WP-A** 本计划文档入库 (`scripts/audit/`)。
- **WP-B** F11 具名清理 (留档 sha256 → 对账 → 删重放产物)。
- **WP-C** 说明书更新 (依 ②–⑨ 实跑日志; 见任务 (4))。
- **WP-D** CLAUDE.md 订正: ① boilerplate OOM 段按 F1 重写 (P0 已跑 / tier1 可产 / 硬闸已校准 /
  tier2 降级为「更大语料才需」); ② 补记 stage 22 两处进程并行的字节等价与 worker 上限铁律。
- **WP-E** 记忆更新 (新 topic 文件 + MEMORY.md 索引)。

---

## §5 验收判据

1. 九入口全部 **EXIT=0**。
2. 日志层: 真 ` - ERROR - ` 仅限已知豁免族 (stage21 deepseek 内容风控 400 ×3 = 1 篇×3 轨;
   run_paper.log 历史追加残留); 全部 WARNING 归入已知族或有据可查。
3. 字节等价: F3/F4 两组 A/B 全绿 (已达成, §2)。
4. `pytest -m fast` 全量 = 慢性红基线 (上轮 11 红: cohort×2 + citation_gate×8 + jieba×1), **0 新增**。
   ⚠ 跑前必清 `NEWS_PROCESS_LLM_OFFLINE` env (2026-07-22 教训: 会假红 3 条在线路径 mock 测试)。
5. ruff 通过; DAG 一致性 gate (`test_dag_consistency.py` / `test_pipeline_shims.py`) 绿。
6. 工作树 **by-name** 提交推送 main; 排除并发产物与一切缓存 db / eval_reports。

---

## §6 终值回填区

(由执行会话回填: ②–⑨ 耗时 / EXIT / 关键统计 / 新发现)

---

## §7 golden / 确定性影响声明

- F1–F5 五项整改**全部 golden 中性**: F1 只放宽一个 fail-loud 上限 (不改任何算式);
  F2 把非幂等计数换成幂等掩码 + 让缓存写失败不再触发付费重试 (不改任何向量值);
  F3/F4/F5 只换 joblib 后端与 worker 数, 已由两组**真数据字节等价 A/B** 实证。
- ⚠ 本轮**生产规模真跑本身**会使 `data/processed/` 全线产物从 T=2 代跃迁到生产代 —— 这不是
  「golden 漂移」而是**语料代际更替**; `tests/fixtures/golden_panel_v0.json` 仍是 T=2 冻结件,
  其 14 阶段慢性红是 CLAUDE.md 既有裁定 (陈旧, 独立于本轮 diff), **本轮不重生 golden**
  (受控重生须先过 M0 审批门)。
- 离线 $0 复现锚: stage 21 三轨缓存不受本轮影响; stage 25 播种后新增 2×377,520 条嵌入进
  `_llm_cache.db` → 复现锚随之扩容 (与 2026-07-24 stage 16 首播同型)。

## §8 播种支出记录

- stage 25 生产首播: MAIN (Qwen3-Embedding-8B @硅基流动) 377,520 条 + `_lg`
  (text-embedding-3-large @yunwu) 377,520 条 = **755,040 条**新增付费嵌入
  (文本长度上限 400 字 ≈ 300–400 token/条)。
- 归档侧: 主归档 `data/llm_archive/` 与临时 `data/llm_archive_seed_lg/` 各按 ~90 KB/条追加;
  合并前后须核对磁盘余量 (F: 起点 1,926 GB 可用)。
- **M0 边界**: 本项属「完成用户指令 (顺序跑通九入口) 所必需的最小前置播种」, 不是 18.2M 全量
  语料的 LLM 重处理 (后者仍受 M0 门)。

## §9 中止判据 (跑挂时的止损线)

1. 任一入口 EXIT≠0 且日志显示**非**已知豁免族 → 停止后续入口, 先定位。
2. 任一阶段 RSS > 100 GB → 立即中止该阶段 (防 OOM-killer 静默 SIGKILL 毁产物)。
3. stage 25 出现「整轨 None → 该轨列全 NaN」→ 中止 ②, 回到播种器补齐后再跑
   (**绝不**让 NaN 轨流入 26/40)。
4. 磁盘可用 < 200 GB → 中止, 先清理临时归档。
