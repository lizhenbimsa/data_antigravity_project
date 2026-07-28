# 全入口性能优化执行计划 (2026-07-28) — v4 (终版)

> **版本沿革**: v1 → 第一轮 (53 提出/49 成立) → v2 → 第二轮 (50 提出/42 成立, **12 条是 v2 自造新错**) → v3 → 第三轮终审 (54 提出/38 成立, **9 条是 v3 自造新错**) → **v4 终版**。
> 全部被替换的数字均经**我亲自复算复核**, 不盲信评审输出; 复核脚本口径见 §10。三轮整改台账见 §13/§14/§15。
> ⚠ 本仓铁律「整改本身必须再被审」**连续三轮全部实证**: v1 错在诊断 → v2 修好诊断却把处方写成**字面不可执行** (§3.2 第 4 条) → v3 修好处方却把**收益目标算乐观了 2.4×** (§4.2 P1-3)。三轮共 157 条提出 / 129 条成立。

**范围 (显式边界)**:
- ✅ 根目录 35 个 `NN_*.py` (thin shim → 其底层 `pipeline.*`/`validation.*` 实现);
- ✅ 两个侧线编排器 `company_listed_bank/run_pipeline.py` · `company_tax_bank/run_pipeline.py` 及各自 4 个子步;
- ✅ 共用件 `core/caching.py` / `pipeline/text/embedding_engine.py` / `core/logging.py` / `run_pipeline_function.py`;
- ❌ **不含** `run_paper.py` (九入口④; `logs/run_paper.log` 2026-07-22 实测单篇 ~1,084–1,091s, 全 11 篇约 4h **且是 T=2 dev 面板**)。理由: 主体是 Stata 回归批处理 + 图表生成, 与本计划的 Python 热点治理正交, **另行立项**;
- ❌ **不含** `LLMs_for_FinTech_dic/` (九入口①)。理由: 用户 2026-07-21 铁律「盲审改造严禁动生成阶段」, 且离线重放实测仅 15.32s。

**证据档**: `scripts/audit/PERF_HOTSPOT_EVIDENCE_2026-07-28.md` (141 条发现, 逐条带 `file:line` + 实测/微基准)。

**基线读数来源**: 2026-07-25 23:56 → 2026-07-28 15:38 的**多次**生产规模调用 (00~26 与 40/46/51 分属不同编排器调用)。
⚠ §1.1 的「合计 41.72h」是**各阶段自报耗时之和**, 不是单趟连续墙钟 (该窗口真实墙钟约 63.7h)。
✅ **基线是目标语料全量, 非抽样**: 183 个去重源文件 / 原始 18,198,978 行 → 8 步过滤 → 4,298,566 → 去重 → 3,710,051
(去重保留率 86.3%, 在日志自陈的 85–95% 健康区间内) → 242,000 留篇 → 169,811 explode; 面板 23,693 行 × 4,183 列 = 1,247 银行 × 19 年。
⚠ **基线可信度声明见 §1.7 (本趟是"部分失败趟", 必读)**。

---

## §0 结论先行 (TL;DR)

1. **16 阶段耗时合计 41.7 小时里, stage 40 占 67.1% (28.0h)**; stage 40 内部 **93.9% 集中在 4 个子步**
   (`7h-auth` 10.57h + `7h-strat` 9.58h + `7h-emb` 5.69h + `7h-net/cogn` 0.45h) —— 共同形态是**「逐轨 × 逐年」三重 `for` 恒串行, 32 逻辑核只用 1 个**。
2. **单条最大杠杆是循环级进程并行, 不是 GPU**。零本地嵌入模型; 唯一 GPU 阶段 (23) 已跑在 3090 上, 推理缓存已写满 **1,264,299 条**, 同输入重跑 ≈100s (§1.4)。
3. **第二大杠杆是嵌入缓存读取路径**, 但必须走**只读多进程分片**: 实测 `WHERE IN` 批量单独只有 **1.08×**, 线程池对 `json.loads` 实测 **0.94–0.96× (更慢, 该 C 解码器持 GIL)**。
4. **API 退避覆盖 stage 40 墙钟 14,051s (3.90h = 13.9%) —— 这是墙钟上界不是可回收量**
   (实测退避深度中位仅 16/250 槽, 槽时闲置占比 7h-emb ≤10.7% / 7h-strat ≤7.5%)。
   分布极不均: `7h-emb` 42.0% / `7h-strat` 15.8% / **最大单点 `7h-auth` 为 0%** ⟹ 退避治理 (P0-5) 对最大的那块**零效果**。
5. **141 条发现: 120 byte_equal / 14 unknown / 7 needs_golden_regen** (6 条进 M0 包, F-07 因本机 triton 不可用先行否决)。**主线提速不必动 golden**。
6. **收益承诺 (自下而上逐项求和 + 脚本校验, 见 §4.0 明细表; 两口径由恒等式绑定)**:
   - **暖 23 口径 (主算, 缓存已写满)**: 35.81h → **10.9–14.8h** (**2.43–3.27×**)
   - **冷 23 口径 (机械导出)**: 41.72h → **16.9–20.7h** (**2.02–2.48×**)
   - 🔒 **恒等式**: `冷_after − 暖_after ≡ (21,390−100)/3600 = 5.914h` (因 P0+P1 **无一条**触及 stage 23)。
   ⚠ **三个历史版本的承诺均已作废**: v1「8–12h」(混口径) · v2「13.6–16.5h」(未满足恒等式) ·
   v3 首版「8.9–12.1h」(7h-strat 目标未扣除「已被 F25/F26 并行的 15,818s」)。
   ⚠ 其中 P1-4 (7h-emb, 占位 10,000–14,000s) 标 **TBD**, 须先做暖复跑归因 (§4.2 P1-4) —— 该段已计入上述合计, 但不作承诺。

---

## §1 基线

### 1.1 主线 16 阶段 (阶段自报耗时)

| 阶段 | 实测(s) | 小时 | 占比 | 口径 | 出处 |
|---|---:|---:|---:|---|---|
| 00 预处理 | 3,467 | 0.96 | 2.31% | **热缓存** | `logs/00_preprocessing.log` (07-25 23:56→07-26 00:54) |
| 11 银行判断 | 123.5 | 0.03 | 0.08% | — | `logs/11_news_bank.log` |
| 12 金科判断 | 79.1 | 0.02 | 0.05% | — | `logs/12_news_fintech.log` |
| 13 共现硬过滤 | 21.0 | 0.01 | 0.01% | — | `logs/13_cooccurrence_filter.log` |
| 14 三轨物化 | 41.6 | 0.01 | 0.03% | — | `logs/14_materialize_ctx.log` |
| 15 金科强度 | 554.9 | 0.15 | 0.37% | — | `logs/15_fintech_intensity.log` |
| 16 政策对齐 | 3,635 | 1.01 | 2.42% | 嵌入缓存全命中 | `logs/16_article_policy_alignment.log` |
| 21 LLM 情感 | 1,449 | 0.40 | 0.96% | **缓存全命中** (2,178,000 查询 / miss 142) | `logs/21_tone_llms.log:246` |
| 22 词典情感 | 3,738 | 1.04 | 2.49% | — | `logs/22_tone_words.log` |
| **23 BERT 情感** | **21,390** | **5.94** | **14.24%** | **冷启动** (推理缓存 hit_rate 42.61%) | `logs/23_tone_berts.log:607` |
| 24 跟风衰减 | 5,408 | 1.50 | 3.60% | — | `logs/24_herd_decay_processor.log` |
| 25 SBERT 持久化 | 2,639 | 0.73 | 1.76% | 嵌入缓存全命中 | `logs/25_article_sbert.log` |
| 26 staleness | 6,762 | 1.88 | 4.50% | — | `logs/26_article_staleness.log` |
| **40 面板编排** | **100,800** | **28.00** | **67.11%** | ⚠ 混合 (见 §1.2 口径列) | `logs/40_build_panel.log` 阶段摘要 |
| 46 Stata 导出 | 34.5 | 0.01 | 0.02% | — | `logs/46_stata_export.log` |
| 51 伪造检验 | 61.9 | 0.02 | 0.04% | — | `logs/51_falsification_test.log` |
| **合计 (冷 23)** | **150,205** | **41.72** | **100%** | | |
| **合计 (暖 23, 23→100s)** | **128,915** | **35.81** | — | | §1.4 |

⚠ **两套时间口径不可混用**: 本表 = **阶段自报耗时**; `tests/test_stage_timeout_calibration.py::MEASURED_PRODUCTION_SECONDS`
= **编排器墙钟 (sig4 显示值)** —— 故 11 号 351s vs 本表 123.5s 存在系统性差值。**超时闸一律用编排器墙钟口径**。
⚠ stage 00 的「冷缓存 6,708s」不在本趟, 出处 `core/dag.py:176-178` (2026-07-24 另一趟, 该趟热缓存 3,785s)。

### 1.2 stage 40 内部分解 (里程碑时间线, 非重叠, 逐行相加 = 100,793s)

| 窗口 (07-27/28) | 秒 | 小时 | 子步 | 主模块 | **缓存口径** |
|---|---:|---:|---|---|---|
| 11:35:46→12:24:16 | 2,910 | 0.81 | 步骤 1–7g (含 6b-3 去重敏感性 2,132s / 6c 285s / 步骤12 75s / 步骤13 259s / Bartik 64s) | `panel/runner.py` | 本地 |
| 12:24:16→12:51:06 | 1,610 | 0.45 | 7h-net 共现网络 33 指标×3 判据 (含 7h-cogn 1,431s) | `panel/network_spillover.py` | 本地 |
| 12:51:06→22:25:48 | **34,482** | **9.58** | **7h-strat 战略差异度** | `features/strategic_diff.py` | **本地 + 嵌入段冷播种** |
| 22:25:48→09:00:14 | **38,066** | **10.57** | **7h-auth 权威政策相似度 (ghost-anchor)** | `features/policy_similarity.py` | 本地为主 (退避 0%) |
| 09:00:14→09:18:23 | 1,089 | 0.30 | 7h-benefit 态度投影 + 6 个 .npy 落盘 | `features/benefit_society.py` | 嵌入缓存 |
| 09:18:23→09:23:12 | **289** | 0.08 | 7h-token 四象限 + 7h-brok 经纪中心度 (251.9s) + 7h-neg (5.1s) + 7h-fire (1.1s) | `panel/network_brokerage.py` | 本地 |
| 09:23:12→15:04:23 | **20,471** | **5.69** | **7h-emb 嵌入同业网** (模块自报 20,470s) | `panel/network_spillover.py` | 🔴 **冷播种** (19,715 重试行 / 19,295 次 429) |
| 15:04:23→15:33:56 | 1,773 | 0.49 | 7h-llmpeer `peer_compete_idx` | `panel/llm_peer_iv.py` | 本地 |
| 15:33:56→15:35:39 | 103 | 0.03 | 8z IV 扩展族 + 诊断 + 多格式导出 | `panel/iv_extensions.py`/`export.py` | 本地 |
| **合计** | **100,793** | **28.00** | (阶段总墙钟 100,800s, 差 7s = 首尾 banner; 与 §1.3 四行窗口和一致) | | |

> 两条独立路径交叉验证, 对 7h-strat/7h-auth 给出**完全相同**的 34,482s / 38,066s。

### 1.3 API 退避统计 (口径已明确; 并集是**上界**不是可回收量)

**口径定义**: **重试行数** = 含「休眠」的日志行 (每行 = 一次 10s 睡眠); **退避事件数** = 含「重试 1/80」的行;
**退避覆盖秒数** = 每行覆盖 `[t, t+10)` 取**并集**。⚠ 严禁把行数×10s 当墙钟 (那是跨并发的累计核秒 452,170s)。

| 类别 | 重试行数 | 退避事件数 | 类内并集(s) |
|---|---:|---:|---:|
| 429 TPM limit (硅基流动 Qwen) | 43,006 | 2,070 | 11,013 |
| HTTP 500 (网关返回 HTML 错误体) | 715 | 370 | 2,187 |
| 网络 TimeoutError | 1,081 | 609 | 1,789 |
| 429 (Azure East US, text-embedding-3-large) | 291 | 61 | 745 |
| ClientPayloadError | 34 | 8 | 247 |
| 429 上游负载饱和 (yunwu) | 88 | 65 | 190 |
| ClientOSError 10054 | 2 | 2 | 20 |
| **合计** | **45,217** | **3,185** | — |
| **退避覆盖秒数 (≥1 并发在退避的秒; 墙钟上界)** | | | **14,051 (3.90h = stage 40 的 13.9%)** |

**逐子步分解 (P0-5 收益归属的唯一依据)**:

| 子步 | 窗口(s) | 退避覆盖(s) | 覆盖率 | **槽时闲置占比** (退避深度/并发上限 250) |
|---|---:|---:|---:|---|
| **7h-emb** | 20,471 | **8,601** | 42.0% | **≤10.7%** (深度中位 16 / p90 64 / max 90) |
| **7h-strat** | 34,482 | **5,450** | 15.8% | **≤7.5%** (深度中位 65 / max 98) |
| **7h-auth (最大单点)** | 38,066 | **0** | 0.0% | 0% |
| 其余全部子步 | 7,774 | 0 | 0.0% | 0% |
| (四行窗口和 = 100,793s ≈ 阶段自报 100,800s, 差 7s = 首尾 banner) | | | | |

🔴 **「覆盖率」≠「可回收量」**: depth=1 的秒与 depth=90 的秒在并集里等权, 但前者仅 1/250 槽闲置。
真实可回收上限 ≈ 槽时闲置占比。**§10 已把这条立为口径纪律。**

### 1.4 stage 23 的特殊性 (改变优先级判断, 必读)

`config/sentiment.yaml:437 inference_cache: true`。`logs/23_tone_berts.log:607`:
`lookups=1,528,299 hits=651,183 misses=877,116 writes=877,116 hit_rate=42.61% (_local_model_cache.db 现 1,264,299 条)`

**四个数字必须区分**:
- `lookups = 1,528,299` = 查询次数 = 169,811 × 3 轨 × 3 模型;
- `writes = 877,116` = 本趟写入调用次数; 起跑库内 `423,801` 条 (`:75`);
- **库条数 = 1,264,299** (盘上实测 671,285,248 B);
- ⚠ `423,801 + 877,116 = 1,300,917 ≠ 1,264,299`, **差 36,618 是同键重复写** (`INSERT OR REPLACE`) ——
  缓存键是**文本级**而非 (文章×轨) 级, 而 `ss_is_fallback` 的文章其 `content_ss` 经 `prepend_title` 后与 `content_full` 逐字相同 ⟹ 同一键在两轨各查一次、各写一次, 只落一行。

⟹ **21,390s 是冷启动一次性成本且已付掉**; 同输入重跑 ≈100s
(76s 缓存 lookup + 载入 8s + 模型加载 1.6s + 落盘 13s; 由 `logs/23_tone_berts.log:64/76/604/708` 重建)。
⟹ 复合键刻入 `det_mode / amp / stride / inference_batch_size / articles_per_batch / vocab 指纹`,
改这些会作废 1,264,299 条。⚠ **TF32 开关不在该键内** —— 那是**更危险**的一类 (不作废、而是新旧值静默混算), 处置见 P0-6③。

### 1.5 两个侧线 (**基线趟不同**: 2026-07-22 23:57 → 07-23 01:01)

| 管道 | 总墙钟 | 01 | 02 | 03 | 04 | 出处 |
|---|---:|---:|---:|---:|---:|---|
| company_listed_bank | 1,211s | 6.4s | 134.8s | **940.7s (77.7%)** | 128.4s | `company_listed_bank/logs/run_pipeline.log` |
| company_tax_bank | 2,562s | 18s | 265s | **1,812s (70.7%)** | 466s | `company_tax_bank/logs/run_pipeline.log` |

合计 3,773s, **独立于主线 41.72h 之外**。瓶颈: 03 的加权引擎列循环 + `pyreadstat.write_dta` 序列化
(实测 31.4 MB/s, **非磁盘瓶颈** — 盘是 Samsung 990 PRO NVMe, 合成基准同为 32.6 MB/s ⟹ pyreadstat 单线程 C 序列化)。

### 1.6 硬件与运行时约束

- CPU **i9-13900K: 24 物理核 (8P+16E) / 32 逻辑线程**。⚠ E 核吞吐约 P 核一半, `n_jobs` 12→24 约 1.25–1.5× 而非 2×。
- **内存: 128 GB 物理; 基线趟起跑 `Available` 仅 104.57 GB** (`logs/00_preprocessing.log:44`), 并行处理开始前 104.21 GB (`:404`)。
  ⚠ **本趟无峰值仪表** (`core/logging.py::log_stage_summary` / `::log_memory_usage` 只取 `memory_info().rss` 的瞬时/终态):
  已知 stage 00 **终态 60.33 GB** (`:503`, 途中「去重前」采样 45.59 GB), stage 40 **终态 34.41 GB** (真峰值落在被 worker 冲掉的日志区间, 已丢失)。⟹ **P0-0**。
- GPU 单张 **RTX 3090 24 GB**, torch 2.6.0+cu124; **faiss 1.14.3 CPU-only 构建** (`get_num_gpus()==0`); 无 cupy/polars/orjson。
- Windows **spawn** (非 fork): 每 worker 重 import, **任务实参逐份 pickle 并在 worker 侧驻留独立副本**。
- **BLAS 线程恒钉 1** 是确定性硬要求 ⟹ 只能走进程级并行。⚠ 见 §3.2 第 4 条。
- 缓存库 (盘上实测 2026-07-28): `_llm_cache.db` = **147,267,403,776 B = 147.3 GB (137.2 GiB) / 3,596,160 条**;
  `_local_model_cache.db` = 671,285,248 B / 1,264,299 条。
  ⚠ **CLAUDE.md 的「98.9 GB / 3,037,107 条」已陈旧** (2026-07-25 读数), 须同步订正 (§11)。
  ⚠ 库 137.2 GiB **> 可用内存 104 GB** ⟹ `mmap_size` 不得按全库设。
- 磁盘: F: 盘剩余 **1,769 GiB** (`data/processed` 现 228.7 GiB) —— checkpoint 与 `.npy` 空间充裕。
- ⚠ `CLAUDE.md` 记「Stata 64-core」实为 **StataMP-64 的 64 位版本代号**, 非 64 物理核。

### 1.7 🔴 基线可信度声明 (必读, 影响所有以 7h-strat / 7h-emb 为分母的倍数)

**本趟是"部分失败趟"**: `logs/run_pipeline_function.log:21894` (07-27 16:40:30, batch 201) 与 `:31597` (18:24:44, batch 237)
两次记录 `嵌入 API 重试 80 次仍失败 → 返回 None (该轨列将置 NaN)` + `Embedding 连贯性: 重试耗尽返回 None → 该轨置 NaN`。
后果不是末位漂移而是**整轨列缺失** (`strategic_diff.py:1429-1432`: `if emb is None: return coherence` 空 dict),
落盘为 **恰好 4 列 × 23,693 行全 NaN** —— 我已在盘上逐列核实, 列名精确为
`coh_emb_ctx` / `coh_emb_lg_ctx` / `coh_emb_ss` / `coh_emb_lg_ss`
(= Embedding 连贯性的 **ctx 与 ss 两轨 × 双嵌入空间**; 2 次耗尽 × both-or-neither = 4 列)。
两次均落在 7h-strat 窗口内; `_full` 轨幸免 (`coh_emb_full` 的 null 数 19,802 = 23,693 − **3,891**,
与日志「3891 个 Bank-Year 对」逐位吻合, 与其余 11 个健康 `coh_*` 列同值)。
✅ **并发会话已在修**: `ec39ac3b` (2026-07-29 00:13:43) = 「F28 留痕 — both-or-neither 静默塌缩改 ERROR + 逐列点名; 零数值改动」
⟹ P0-5′ 的「非静默」诉求已被部分满足, 但**降级本身 (置 NaN) 仍在**, 裁定项不变。

⟹ ① 所有以 7h-strat / 7h-emb 为分母的加速倍数须标注「基于降级趟」;
⟹ ② 该失败**不入缓存**且由供应商 TPM 瞬时态触发, **跨趟不可复现** ⟹ 它是 §3.3 A/B 对拍的**非确定源**, 处置见 §3.3 前置条件;
⟹ ③ P1-3 的目标区间在拿到一次**四列非空**的成功趟之前只作规划值, 不作承诺值。

---

## §2 阶段依赖图与并发拓扑

### 2.1 实测依赖 (逐个 `read_parquet` 反查)

```
00 → 11 → 12 → 13 → 14
                     ├─→ 15 ──┬─→ 16 ──────────────────┐
                     │        └─→ 21 → 22 → 23 → 24 ───┤
                     └─→ 25 ────────────→ 26 ──────────┤   (26 需 25 且需 24)
                                                       ↓
                                                      40 → 46
                                                         → 51
```
⚠ 相对 v1 订正三处: **补 `26 → 40`** (`runner.py:416` opt-in merge `26_staleness_panel`, 承重 **18 列**);
**删 `25 → 40`** (runner 从不读 25 的 parquet, 只做 mtime 比对; 25 的唯一消费者是 26);
另有 `75_cross_media_alpha` (验证阶段) → 40 的 opt-in merge (9 个测度列) —— 跨管道边, **P2-3 必须处理**。

关键事实:
- `21 → 22 → 23 → 24` 是**列追加链** (21=203 列 → 22=601 → 23=649, 均 169,811 行)。
- **23 的计算不读 22 产的列** (只用 `标题/内容/content_ctx/content_ss`, `tone_berts.py:1494-1509`),
  **但 23 的产物承载 22 的 399 列**, 而 stage 64 (`validation/tone_validation.py:2485-2493`) 正是读 `23_bert_tone.parquet`
  取「词典/BERT/LLM 三方法同帧」⟹ **22→23 是产物契约边**。
- **25 只依赖 14**; **16 与 21 互不依赖**。

### 2.2 可开的并发 (口径统一到「P1 之后」)

| 并发组 | 收益 (冷 23) | 收益 (暖 23) | 依赖/风险 |
|---|---|---|---|
| `16` ∥ `21` | P1 后 min(T16'=521–771, 1,449) = **省 521–771s** | 同左 | ⚠ 共享 `_llm_cache.db` **写**路径 (miss 时写) → R-3 |
| `25` ∥ `15→16` | P1 后 min(T25'=636–986, T15'+T16'=781–1,031) = **省 636–986s** | 同左 | ⚠ 需先做 G-10; ⚠ v3 首版写「≈2,000s」是 P1 **前**的 min, 高估约 3×, 且该重叠此前未进 R-4 |
| `22` ∥ `23` | P1-10 后 min(2,000–2,400, 21,390) = **省 2,000–2,400s** | **省 ≈100s (几乎归零)** | ⚠ 需 P2-1 + stage 64 硬前置 ⟹ **暖口径下不成立**; v3 首版冷列写 3,738s 是 stage 22 **基线**值 |

---

## §3 铁律与验收框架

### 3.1 三档确定性判定

| 档 | 定义 | 验收 |
|---|---|---|
| **A. byte_equal** | 输出逐字节不变 | ①算子级 A/B (**必做, 每条改动**); ②阶段产物 sha256 (**按批做**); ③全链 golden diff (**末次做**) |
| **B. unknown** | 理论等价但受 FP 求和顺序/分组序影响 | 先在**真数据**上 A/B 实证; 通过才降 A, 否则升 C 或放弃 |
| **C. needs_golden_regen** | 必然改数值 | **一律推到 M0 付费审批门后** (§5) |

**A 档 carve-out (仅此三类, 不得扩大)**:
① 9 个 BLAS-FP 网络列 (`bank_clustering`/`bank_cfbetween_cent`/`bank_harmonic_cent` × 三判据);
② 🔴 因 `EmbeddingRetryExhaustedError` 置 NaN 的整轨列 —— **不是 carve 掉差异, 而是判该趟基线作废** (§3.3 前置条件 2);
③ 🔴 **【第三轮新增】文件头/metadata 内嵌时间戳的产物, 与一条具名的产物形态变更**:
   - **`.dta`**: pyreadstat format-118 头部写**分钟级墙钟时间戳** (实读 `40_panel_yearly.dta` = `28 Jul 2026 15:35` /
     `46_panel_yearly_full.dta` = 15:36 / `51_panel_with_controls.dta` = 15:37) ⟹ 同内容两次写**必得不同 sha256**;
     而 `46_panel_yearly_full.dta` 是 `core/schemas.py::OUTPUT_REGISTRY` 登记的正式产物 ⟹ 不 carve 则该批层级 2 **100% 必红**。
     判据改为「**文件字节数 + `hash_pandas_object(index=False)` 列哈希**」(照抄本仓 2026-07-10 已定谳口径)。
     ⚠ 同批的 `46_panel_yearly_labels.do` (无时间戳) 与 `codebook.xlsx` (zip 条目时间恒为 1980-01-31) **不受影响, 仍用 sha256**。
   - **侧线 pair parquet**: `upstream_snapshot` 内嵌 `mtime_ns`, 同上处理。
   - **G-10 (唯一具名的形态变更)**: `.npy` 化必然改变 `25_article_embeddings.parquet` (现 17,905,405,623 B) 的字节与列集,
     判据下沉为「**反序列化后 `np.array_equal` + 全部下游阶段产物按本节判据相同**」。**仅此一条获此豁免, 不得类推。**

### 3.2 并行化的字节等价充分条件 (所有 `process_parallel` 项共用)

> 沿用本仓已验证的护栏 (`strategic_diff.py:995-1004` 的 F25 四条), 并补三条 v1/v2 写错或缺失的:

1. **循环体之间零共享可变状态、零随机源** (随机源须 `random_state=42` 钉死);
2. **任务切分与串行循环同序同筛选** —— 切分口径一旦漂移就是静默改测度;
3. **结果按提交序归并** (`joblib.Parallel` 按提交序返回), 且**不改变任何浮点归约的次序**;
4. 🔴 **worker 的 BLAS 线程数不是 1, 且 v2 给的处方字面不可执行**。
   - 诊断 (实测): joblib `_parallel_backends.py:183` `default_n_threads = max(cpu_count() // n_jobs, 1)`,
     `:191 os.environ.get(var, default_n_threads)` ⟹ **父环境未设该 env 时** worker 拿 `32 // n_jobs`
     (`n_jobs=6 → 5`, `12 → 2`, `20 → 1`)。
   - 🔴 **处方 (v2 写错, v3 已实跑订正)**: 二选一, **不得依赖默认**:
     - **选项 A**: `joblib.parallel_config(backend='loky', inner_max_num_threads=1)` ——
       ⚠ **`backend=` 必须同批给出**, 否则 joblib 1.4.2 `parallel.py:397-404 _check_backend` **无条件 raise ValueError**
       (我已实跑复现: 不带 backend → `ValueError: inner_max_num_threads and other constructor parameters backend_params are only supported when backend is not None.`);
       且 `supports_inner_max_num_threads` 仅 `LokyBackend` 为 True (`_parallel_backends.py:528`; 基类 `:32` 为 False, 传 threading 后端会在 `parallel.py:434` assert 失败)。
     - **选项 B (推荐, 本仓既有先例)**: worker 首行 `with threadpool_limits(limits=1):`
       (`strategic_diff.py:664` / `:1155` 已如此)。**新增并行点一律沿用 B, 以免动 backend 语义。**
   - 依据: F26 实测「不钉 BLAS 时并行/串行 **265/277** 键位模式不同; **钉后 277/277 相同**」(`strategic_diff.py:1150-1153`)。
5. 🔴 **嵌套 `Parallel` 会静默退化为线程**。joblib 1.4.2 `_parallel_backends.py:144-155`: `nesting_level==1` 时
   `get_nested_backend` 返回 **ThreadingBackend**, 而日志仍打印 `prefer='processes'`。
   ⟹ 内层若必须并行须**显式写 `backend='loky'`** (实测可逃出降级), 或**改用单层扁平任务网格**;
   并在 `_run_year_tasks` 类驱动函数里加 `get_active_backend()[0] is not LokyBackend → loud WARNING` 的退化探测。
6. **worker 日志纪律 (F27 后语义, v2 的根因表述已陈旧)**:
   - ✅ **文件 handler 截断已被 F27 根治** (`e94bf57f`, 2026-07-28 23:16:52; `core/logging.py:255-265`:
     `if _is_spawned_child_process(): console_only = True`) —— 「子进程首写即截断阶段 .log」在结构上不再可能。
   - 🔴 **但残余风险变成「worker 体内 logger 调用被 loky 静默丢弃」**, F27 注释自陈:
     「F25 立下的『worker 体内零 logger 调用, 告警回传父端 emit』纪律**仍然必须遵守**, 本闸不是它的替代品」。
   - ⟹ 两种模式, 不可混用: **模式 A** `_silence_worker_logging()` (`tone_words.py:1406`, 适用于 worker 绝不被父进程直接调用);
     **模式 B** worker 体内零 logger + 告警回传父端 emit (`strategic_diff.py:1027-1030`, 适用于存在**串行回落路径**)。
     `_run_year_tasks` 家族必须用**模式 B**。
   - ⟹ 每条并行项 (P1-2/3/4/5/5b/7/8/13/14) 落地时**必须附一张「循环体内 logger 点 → 回传/保留」的逐条映射**,
     至少把**降级类 WARNING** 全部纳入回传 (否则降级会静默消失)。
   - 📌 实弹存档: 基线趟 `40_build_panel.log` 337,012 B 中 **216,731 B (64.3%) 为 NUL**, 首行即 worker PID 33888
     经 `strategic_diff.py:387-389` 发出, 抹掉 11:35→21:28 约 10h; 同时证伪 `strategic_diff.py:1001-1004` 的
     「本模块 loky worker import 不会截断生产日志 / worker 体内零 logger 调用」两句自述 —— **同批订正该注释**。

### 3.3 强制验收 (两级 + 三条前置)

**两级验收**:
```
层级 1 (每条改动, 必做):  算子级 A/B —— np.array_equal / assert_frame_equal(check_exact=True)
层级 2 (每批合并后一次):  阶段产物按 §3.1 carve-out③ 的分类型判据 —— parquet/npy/xlsx/do 用 sha256; .dta 用「字节数 + 列哈希」
层级 3 (§8 ⑩ 一次):      全链 golden diff (排除 §3.1 carve-out)
```
⚠ 层级 2/3 才需要整阶段跑; **禁止**把每条改动都按「28h × 2」执行 (那是 v2 未澄清的成本陷阱)。

**三条前置条件 (缺一即该趟基线无效)**:
1. 🔴 **删净 checkpoint**: A/B 对拍趟一律先删 `_ckpt_7h_*` / stage 24 sidecar, 或带 `NEWS_PROCESS_NO_CKPT=1` (⚠ 该开关**当前全仓不存在**, 须随 P0-3 一并实现; 在此之前只走「删净」这条主路径)。
   **checkpoint 只服务断点续跑, 绝不服务验收** —— 否则改后趟会读回改前 checkpoint, sha256 必然相同 = **恒真假绿**。
2. 🔴 **嵌入退避耗尽计数双侧为 0**: 基线趟与改后趟的 `嵌入 API 重试 .* 次仍失败` 计数必须均为 0;
   **命中即该趟作废重跑**, 而不是把差异 carve 掉 (§1.7)。该判据的实现载体 = P0-5′ 的「非静默汇总闸」。
3. **环境双侧同钉**: `PYTHONHASHSEED=0` + `MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1`;
   若生产不钉线程, 须显式披露差异或把 BLAS=1 提升为生产默认。

**外加 gate**:
- `pytest -m fast` **零新增失败** —— 判据只认当日 baseline-stash 的 `comm` 逐项集合相等, **不认绝对条数**
  (最近记录: 2026-07-25 共 **32** 项, 见 `STAGE21_LOG_DEFECT_AUDIT_AND_REMEDIATION_PLAN_2026-07-25.md:468`; 此后又换过一代产物, 以执行当日实跑为准);
- `test_dag_consistency.py` / `test_pipeline_shims.py` / **`test_stage_timeout_calibration.py`** 必绿。

### 3.4 不可触碰清单

- 35 个 `NN_*.py` 保持 ≤30 行 thin shim; 改动落在 `pipeline.*`/`validation.*`。
- `_llm_cache.db` (**147.3 GB / 3,596,160 条**) 与 `_local_model_cache.db` (**0.67 GB / 1,264,299 条**):
  **只增不删, 且不得原地改写编码/页结构** (除非已完成 §4.3 P2-5 的 ①–⑤ 前置)。
  任何会改缓存键的参数改动按 **C 档**处理。
- Prompt v8 字节冻结; `jieba==0.42.1` 冻结; `_compute_weighted_panel_percol` 冻结参照臂。
- 两侧线的启动哈希锚复算 + 03 双锁 fail-closed。

---

## §4 实施计划

### 4.0 批次总览与逐项收益明细

| 批 | 主题 | 条目数 | 确定性 | §8 步骤 |
|---|---|---:|---|---|
| **P0** | 阻断性正确性/鲁棒性 | **9** (+1 待裁定 P0-5′) | A | ①–③ |
| **P1** | 字节等价大杠杆 | **16** (P1-6 已移出不计) | A | ①④–⑨ |
| **P2** | 结构性/需实证 | **5** | A/B | ⑪ |
| **P3** | 需 golden 重生 | **6** (+1 先行否决 F-07) | C | ⑪ (M0 窗口) |
| **X** | 已证伪 / 明确不做 | **9** + 3 条撤回 + 4 条无编号结论 | — | — |

**🔒 逐阶段 baseline → target 明细 (两口径均由本表求和, 严禁手写区间)**

| 阶段/子步 | baseline(s) | target(s) | 依据 |
|---|---:|---|---|
| 00 | 3,467 | 2,000 | P1-9 |
| 11–14 | 265 | 265 | 不做 (§6) |
| 15 | 555 | 260 | P1-11 |
| 16 | 3,635 | 521–771 | P1-1 (嵌入段 3,614→500–750) |
| 21 | 1,449 | 1,449 | 不做 |
| 22 | 3,738 | 2,000–2,400 | P1-10 |
| **23** | **21,390 (冷) / 100 (暖)** | **同 baseline** | 🔒 **P0+P1 零改动** |
| 24 | 5,408 | 900–1,800 | P1-8 |
| 25 | 2,639 | 636–986 | P1-1 (嵌入段 2,453→450–800) |
| 26 | 6,762 | 1,000–1,500 | P1-7 |
| **40 · 步骤1-7g** | 2,910 | 1,424 | P1-9/H-03 (6b-3 1,501→15) |
| **40 · 7h-net/cogn** | 1,610 | 339–419 | P1-5 (cogn 1,431→160–240) |
| **40 · 7h-strat** | 34,482 | **12,500–16,500** | P1-3 ⚠ 已按三段实测下调 (② 已被 F25/F26 并行) |
| **40 · 7h-auth** | 38,066 | 5,000–8,000 | P1-2 |
| **40 · 7h-benefit** | 1,089 | 250–400 | P1-1 |
| **40 · 7h-token/brok** | 289 | 289 | 不做 |
| **40 · 7h-emb** | 20,471 | **TBD** (占位 10,000–14,000) | P1-4 ⚠ 须先暖复跑归因 |
| **40 · 7h-llmpeer** | 1,773 | **250–400** | P1-5b (按整窗口径; 证据档 I-07 原文即 1,772s → 250–400s) |
| **40 · 8z+导出** | 103 | 103 | 不做 |
| **40 小计** | **100,793** | **30,155–41,535 (8.38–11.54h)** | |
| 46 + 51 | 96 | 82 | P1-12 |
| **主线合计 (暖 23)** | **128,907 (35.81h)** | **39,368–53,148 (10.9–14.8h)** | **= 基线的 2.43–3.27×** |
| **主线合计 (冷 23)** | **150,197 (41.72h)** | **60,658–74,438 (16.9–20.7h)** | 🔒 = 暖 + 5.914h; = 基线的 2.02–2.48× |

> ✅ **本表已由脚本逐行求和校验** (口径见 §10): 40 小计 = 九行之和; 主线合计 = 十二行之和;
> `冷_after − 暖_after = 21,290s = 5.9139h` 恒等式两端均成立。
> ⚠ 行内秒数为四舍五入值 (11–14 实为 265.2s, 46+51 实为 96.4s), 故合计与 §1.1 的 150,205 差 8s。
> ⚠ v1「8–12h」、v2「13.6–16.5h」、v3 首版「8.9–12.1h」均已作废 —— 前两者混口径/未满足恒等式, 后者的 7h-strat 目标未扣除「② 已被 F25/F26 并行」的 15,818s。

| 其他表 | 基线 | P1 后 |
|---|---|---|
| **验证管道 16 阶段** | **未在生产规模跑过, 全为外推** (T=2 dev 趟 = 662s, 其中 72 号 551s) | 待 P0-2 的校准跑产出 |
| **两条侧线** | 3,773s | ≈2,100–2,400s |

---

### 4.1 P0 — 阻断性正确性与鲁棒性

| ID | 问题 | 位置 | 处置 |
|---|---|---|---|
| **P0-0** | **无内存峰值仪表** ⟹ R-2 的 `n_jobs` 与 §9 的内存验收线无从校准。 | `core/logging.py::log_stage_summary` (现 :581-582) · `::log_memory_usage` (:549-555) · `::log_and_time` (:407, RSS 采样在 :423/:436) ⚠ v3 首版误写 `log_execution`, 全仓零命中 | **双口径且以①为验收标的**: ① 阶段起采样线程 (1–5s) 记 `psutil.virtual_memory().available` **最低水位** (机器口径, 天然覆盖所有 worker 与并发的 Stata/IDE); ② `Process()+children(recursive=True)` 的 RSS 之和高水位 (进程树口径, 归因用)。父进程 `peak_wset` (Windows psutil **已验证可用**) 仅作辅助。⚠ **worker 侧仪表一律以返回值回传父端, 不得靠 logger** (§3.2-6)。**排 §8 最前**。 |
| **P0-1** | **stage 72 超时闸 10,800s < 生产外推 ≈6.9h** ⟹ 必被强杀且无断点 = 归零。F19/F19b **第三次同型**。 | `core/dag.py:496` | 先做 P1-13 (外推 6.9h → 17–21min), **同批**按整改后**实测**重设; P1-13 落地前提到 **90,000s**。 |
| **P0-2** | 验证阶段超时全按 T=2 设定。**继承默认 7,200s 的是九个**: 60/61/63/64/65/67/68/69/71; 73/74 = 900s。其中 **65 号外推 4,271s / 7,200s = 1.7× 余量**最薄。 | `core/dag.py:410-524` | ①全部验证阶段统一临时提到 **90,000s** (与 P0-1 同值, 消除 v2 的 43,200↔90,000 冲突; 统一值须 ≥ 各阶段已知外推需求 ×3); ②各跑一次实测产出「验证管道基线表」; ③**把 `tests/test_stage_timeout_calibration.py` 的覆盖从 `STAGES_MAIN` 扩到 `STAGES_VALIDATION`** —— 行锚 `:26 import` / `:54 _spec` / `:79 offenders` / `:89 scripts`, `_spec` 与 `scripts` 集合改为在 `STAGES_MAIN + STAGES_VALIDATION` 上查找, 保留 `test_no_main_stage_silently_inherits_default_timeout` 的 MAIN 语义或另起 VALIDATION 版。 |
| **P0-3** | **stage 40 零中间持久化**: 28h 全在内存 (F19b 已烧掉 6h)。 | `pipeline/panel/runner.py:1828-2165` (7h-cogn/strat/auth/benefit/emb 五处分支边界) | 五分支各落 `_ckpt_7h_<branch>.parquet`。🔴 **三条硬约束**: ① **key = 输入指纹 ⊕ `_<BRANCH>_CODE_VERSION`** (照抄 `PREPROCESS_CODE_VERSION` 范式, 改该分支算法即 bump; 配 frozen 单测, 登记 §11) —— 否则验收复跑会读回改前 ckpt = **恒真假绿**; ② **产物与指纹合并为单一写点** (指纹写进 parquet schema metadata), 一律 `.tmp` 写完再 `Path.replace` (照抄本仓 F8 范式, `company_listed_bank/02:1125-1131` 等 9 处); ③ 读侧对 `ArrowInvalid`/校验失败做「删 ckpt + 重算 + loud WARNING」自愈。 |
| **P0-4** | **stage 24 零检查点**: 991 家银行 5,408s 只在内存。 | `pipeline/sentiment/herd_decay.py:654` | 逐银行结果落 sidecar, 断点续跑。**同 P0-3 的三条硬约束** (`_HERD_CKPT_CODE_VERSION` + 原子写 + 自愈)。 |
| **P0-5** | **重试/节流**: 现为 **flat 10s × 80 次** (`embedding_engine.py:85-86`), 对 429 TPM 无效; 无 TPM 令牌桶。 | `pipeline/text/embedding_engine.py` | ①退避改**指数 + 抖动 + 读 `Retry-After`**, **必须显式给 cap 使单请求最坏累计 ≤ 800s** (维持 2026-06-26 全项目口径上界; `tone_llms.py:359-367` 已记载「无 cap 的指数退避 ×80 ≈12h/请求 + 占住并发槽」的删除理由), 或给出新上界 X 并**同批**更新 `embedding_engine.py:113-114` 注释; ②按 TPM 预算做令牌桶节流。⚠ **必须先于 P0-1/P0-2 的超时重校落地** (否则重校用旧分母)。⚠ **不是提速项** (R-10)。 |
| **P0-5′** | 🔶 **待用户裁定**: 「重试耗尽 → 该轨置 NaN」是否改 fail-loud。 | 同上 | ⚠ v1 把它写成 P0 是**错的**: 该降级是 **2026-06-23 用户决策** (`embedding_engine.py:88-94`) + **CLAUDE.md 的 co-primary both-or-neither 铁律**, 与 stage 21「80 次后缺席投票」刻意对称; 且 v1 引作依据的「stage 13 `FINTECH_AC=None` loud 先例」**引反了** (那是 WARNING + 保留全部行)。改 SystemExit 会把「某轨 NaN」升级成「28h 阶段归零」, 与 P0-3 自相矛盾。**推荐替代 (无需裁定即可做)**: 保留降级, 阶段收尾加**非静默汇总闸** (统计本趟置 NaN 的 spec/轨/年) —— 该闸输出即 §3.3 前置条件 2 的判据载体, **须排在 §8 ⑦ 之前**。若裁定采纳 fail-loud, 须同批改 CLAUDE.md + `embedding_engine.py:88-94` + `policy_similarity.py:152-156` + `test_embedding_coprimary_parity`。 |
| **P0-6** | 缓存资产保护。 | `config/sentiment.yaml:400-437` / `config/features.yaml:28-40` | ①**两处横幅分开写**: sentiment.yaml → 「⚠ 改此值 = 作废 `_local_model_cache.db` 的 1,264,299 条 BERT 推理缓存 (下趟 stage 23 从 ≈100s 退回 21,390s)」; features.yaml → 「⚠ 改 `text_pipeline_version` = 使 `_llm_cache.db` 内该模型槽的全部嵌入条目失配 → **付费**在线重播种 (库现 3,596,160 条 / 147.3 GB)」。②加 `test_cache_key_params_frozen`。③🔴 **TF32 守卫必须零缓存代价** (v2 写「加第 12 维或 bump」是**自造新错** —— 两种写法都会 100% 作废 1,264,299 条, 与 §3.4 自订铁律冲突, 且 F-02 已在 M0 门后、当前 TF32 全仓零命中): 采用 **(a) fail-loud 断言** —— `_BERT_INFERENCE_CACHE=True` 时于模型加载处 `assert torch.backends.cuda.matmul.allow_tf32 is False` (与 `tone_berts.py:462-464` 的 amp fail-fast 范式同构) + `test_bert_tf32_not_enabled`; **(b) 若坚持入键, 必须条件式追加** `tf32_part = '|tf32=1' if allow_tf32 else ''` (对齐 `caching.py:288-297` 的 `seed_part` 先例), 保证 TF32=off 时 composite 串**逐字节不变**, 并给新参数默认值 `tf32: bool = False` 以免打红 `tests/test_w8_bert_inference_cache.py:176-193/294-315`。「真要入键」的动作整体挪进 §5 F-02 的 M0 包。④补 `CUBLAS_WORKSPACE_CONFIG` (现全仓零命中, 而 `tone_berts.py:196` 用 `warn_only=True`; 实测代价 -0.6%)。 |
| **P0-7** | 🔴 **stage 40 超时余量仅 1.29×, 且守闸表陈旧呈假绿**。`core/dag.py:374 timeout=129600` ÷ 实测 100,800s = **1.286×** (< MIN_MARGIN=3.0); `tests/test_stage_timeout_calibration.py:45-46` 仍写 `(39600, '…尚无完整实测')` ⟹ gate 按 129600/39600=3.27 判**绿**。 | `core/dag.py:374` + `tests/test_stage_timeout_calibration.py:45-46` | 提闸到 **≥302,400s**, **同批**回填 `(100800, '2026-07-28 15:36 生产实测跑完, logs/run_pipeline_function.log:58520')`。⚠ 100,800 是 sig4 显示值 (真值 100,818s), 与该表既有全部条目同口径, 刻意保持一致。**排在 §8 ③, 先于任何需重跑 stage 40 的验收批**。 |
| **P0-8** | **SQLite 并发写未加固**。嵌入路径 miss 时**要写**; 137.2 GiB WAL 库上多路并发写, 现行处置是 `embedding_engine.py:585-590` warning 后丢弃 ⟹ **该缓存条目丢失** (本轮产物仍正确, 但下趟重付费; 离线 $0 复现时该条目变 hard-fail)。 | `core/caching.py:225-227` | ①显式 `PRAGMA busy_timeout=30000` (现仅 `sqlite3.connect` 默认 5s); ②`put`/`put_batch` 对 `database is locked` 定向退避重试; ③加**丢弃写入计数器**并在阶段收尾 loud 汇报 (现有 warning 无法 grep 监控; **worker 侧计数以返回值回传**); ④WAL checkpoint 改手动/管控。 |

---

### 4.2 P1 — 字节等价大杠杆

#### P1-1 · 嵌入缓存读取路径 = **只读多进程分片** 【影响 15/16/25/26/27/40】
- **现状**: `embedding_engine.py:354` 逐条 `cache.get()` (单键 SELECT) → `json.loads()` (82.5 KB JSON 文本 = 4096 维)。
  `core/caching.py:410` 把向量存成 **JSON 十进制文本** (值本身 82.5 KB vs float32 二进制 16,384 B = **5.0×**; 计入行开销后整行平均 89.9 KB = **5.6×**)。
- 🔴 **v1 的改法已被实测证伪**: `get_batch`/`WHERE IN` 单独只有 **1.08×**; 线程池并行 `json.loads` 实测 **0.94–0.96×** (v1 写的「json 解析释放 GIL」是**假机制**); `np.frombuffer` 前提是 BLOB 存储 (已排除到 P2-5)。
- **正确改法 (证据档 C-01/G-06 原方案)**: **loky 只读多进程分片** —— K=8–12 worker,
  每 worker `sqlite3.connect('file:...?mode=ro', uri=True)` 独立连接, worker 内自算 key + `json.loads`,
  回传 `(row_idx, float32 块)`; 主进程只做按 index 回填 + miss 集合的付费路径。
  `get_batch` 与 PRAGMA 保留但**标注「单独实测仅 1.08×, 不计入收益」**; `mmap_size` **不得按全库设** (137.2 GiB > 104 GB)。
- **预期**: I/O 项 1,874s → 250–400s + json 项 1,077s → 110–160s ⟹ stage 16 嵌入段 3,614s → **500–750s**; stage 25 2,453s → 450–800s; 7h-benefit 1,089s → 250–400s。
  ⚠ 若最终不做多进程, 预期必须下调到 **≈1.05–1.1×**, 并同步撤销它在 §8 的闸门地位与 P1-2/P1-4 的叠加乘数。
- **对应发现**: C-01 / C-03 / C-04 / C-05 / G-06 / G-08 / G-09 / I-01 / I-02 / D-04。

#### P1-2 · 7h-auth 权威政策相似度: 逐轨逐年进程并行 【38,066s = 单点最大】
- `policy_similarity.py:390` 三重串行 `for track(3) → for year(19) → _ghost_anchor_metrics`, 共 57 个独立单元。
- 叠加: `:420/:432` 同 (track, year) 银行侧被算两遍 (C-09); `:125` 同批超级文档被 jieba 分词两次 (C-10);
  **I-05 (perplexity 重分词) 按 111:57 与 P1-3 分摊, 本条占 66%** (见 P1-3 的 LDA 分布订正)。
- **预期**: 38,066s → **5,000–8,000s (4.8–7.6×)**。⚠ 本子步**退避占比 0%**, 纯本地计算 ⟹ 收益不受 API 配额封顶, **最干净的一块**。
- **风险**: 57 worker 各持一份 jieba Trie + sklearn 词表 ⟹ `n_jobs` 由 **P0-0 的真峰值**反推。
- **对应发现**: C-08 / C-09 / C-10 / I-03。

#### P1-3 · 7h-strat 战略差异度 【34,482s → 12,500–16,500s】

🔴 **目标已按三段实测归因下调 (v3 的 5,000–7,000s 过于乐观, 第三轮定谳)**。34,482s 内部实测三段:

| 段 | 窗口 | 秒 | 占比 | 现状 | 目标 |
|---|---|---:|---:|---|---|
| ① 战略差异度主循环 | 12:51:06→14:39:44 | 6,518 | 18.9% | **未并行** (`:1692` 主年循环) | 1,200–1,600 |
| ② 相邻期文本连贯性 | 14:39:44→19:03:22 | **15,818** | **45.9%** | 🔴 **F25/F26 已并行** (`:1381 _run_year_tasks`) | 9,000–11,500 |
| ③ ctx/ss 子轨等尾段 | 19:03:22→22:25:48 | 12,146 | 35.2% | **未并行** (子轨循环) | 2,200–3,000 |

⟹ **可再并行的只有 ①+③ = 18,664s (54.1%)**; ② 已是并行后的结果, 其剩余空间来自
**P0-5 修好退避** (该段含 5,450s 退避覆盖, 其中两次耗尽白烧约 4,457s) + 提高 worker 数 (现硬上限 12), **不来自新增并行**。
⚠ `_lda_coherence_year_worker` **不调 `perplexity`** ⟹ **I-05 对 ② 无效**, 只作用于 ①③ 与 7h-auth。

- **靶点 (⚠ 行锚已因 `ec39ac3b` 腐化, 见 R-13, 开工前必须重锚)**:
  `strategic_diff.py::compute_strategic_differentiation` 的主年循环 (v3 落盘时 `:1692`) 与
  `::_sub_tracks` 的 ctx/ss 子轨循环 (v3 落盘时 `:1920-1934`, **`ec39ac3b` 后已移至 `:1961`**);
  I-11 的 `strat_fluidity` 落列 (v3 落盘时 `:1806`, **现已移至 `:1818/:1820`**; `:1806` 现在是无关的 `if all_results:`)。
- 🟢 **字节等价先例已实测存在**: `:1150-1153` 记 F26「不钉 BLAS 时并行/串行 265/277 不同; **钉后 277/277 相同**」,
  而 `_build_lda_jsd_matrix:663-666` **已带同一个 `with _threadpool_limits(limits=1)` 护栏**。
  ⟹ 复用**已验证的 `_run_year_tasks`** (`:1053`)。**仍须做主循环自身的 A/B 对拍, 不得假定继承。**
- 📌 **同批修文档缺陷**: `:1006-1008` 的「唯独 `_compute_lda_coherence` … **该函数恒串行**」是 F26 之前的陈旧注释, 与活代码 `:1381`(已并行) 矛盾, 会误导实施者; `:1001-1004` 的「worker import 不会截断日志 / worker 体内零 logger」已被基线趟实弹证伪 (§3.2-6)。
- 叠加: `:666` `lda.perplexity(cv.transform(texts))` 只为打日志就重新分词整批 (I-05); `:1320` `_compute_lazy_distances` (I-06); `:1806` 落列 `apply(axis=1)` → `map`+`MultiIndex` (I-11)。
- **🔴 LDA 实测分布订正 (v2 写错)**: 全趟 168 次 `LDA K=` 日志, 实测 **7h-strat 57 次 / 7h-auth 111 次**
  (v2 写「全部来自 7h-strat」是错的 —— 自洽性检查 `168 × 274s = 46,032s > 34,482s` 本该当场拦住该断言)。
  两处都来自 `_build_lda_jsd_matrix:667` (唯一日志点), 分别由 strategic_diff 主循环与 policy_similarity 的 `_ghost_anchor_metrics` 调用 ⟹ **全部 168 次仍确在未并行的串行循环里**, 只是 66% 的量在 P1-2 名下。
- **预期**: 34,482s → **12,500–16,500s (2.1–2.8×)** = ①1,200–1,600 + ②9,000–11,500 + ③2,200–3,000。
  ⚠ 目标区间在拿到一次**四列非空**的成功趟前只作规划值 (§1.7)。
  ⚠ v3 首版写「5,000–7,000s (4.9–6.9×)」已作废 —— 它把并行倍数套在了整个 34,482s 上, 未扣除已被 F25/F26 并行的 ② 段。

#### P1-4 · 7h-emb 嵌入同业网 【20,471s → **TBD**】
- `network_spillover.py:1834` 的 `for year` 串行跑 18 个滞后年, 该函数又被调 **6 次** (MAIN/_lg × W-轨 full/ctx/ss) ⟹ 108 个独立单元全串行。
- 🔴 **不可用嵌套并行** (§3.2 第 5 条)。改为**单层扁平任务网格**: 6 × 19 展平成 ≤114 个 `(spec, w_track, year)` 任务。
- 🔴 **前置**: 入参必须先做**列投影窄帧** (照抄 `herd_decay.py:643-646` 的 `_need` 范式) —— spawn 下每 worker 驻留独立 pickle 副本, 现签名传 169,811 × 1,356 的 `df_exploded` (pandas 实际驻留 5 GiB 量级)。
- 🔴 **目标标 TBD, 不进 §0 承诺**: 本子步是**冷播种趟** (19,715 重试行 / 19,295 次 429), 且已跑在 TPM 配额天花板上;
  **令牌桶把吞吐钉在上限, 不提高上限**。
  **落地前必须先做一次零改动的暖复跑归因**: HEAD `e94bf57f` 已提供 `NEWS_PROCESS_NS_LOG_LEVEL=INFO`
  (commit message 原文「7h-emb 的 API/CPU 分段归因需要」), 打开后 `embedding_engine.py:383-390` 的
  「缓存拦截: 命中 N 条, 缺失 M 条」即可落盘, 给出暖跑真基数; 再用「提交 token 总量 ÷ 实测 TPM」求墙钟地板。
  在此之前占位 10,000–14,000s, **收益仅可归因于「命中段并行」, 不得归因于「消除退避」**。

#### P1-5 · 7h-cogn 认知邻近度三轨并行 【1,431s → 160–240s】
`network_spillover.py:1502/1615/1623` 三轨 × 19 年串行 → 扁平任务网格 (I-10)。

#### P1-5b · 7h-llmpeer 【1,613s → 80–250s, effort=S】
`llm_peer_iv.py:893` 双层循环内对整个 `df_exploded` 做全表布尔掩码 (≈80 亿次比较) → 一次 `groupby(['target_bank','year'], sort=True)` (I-07);
`:289/:302` 逐句子串搜索 → **AC 自动机全命中模式** (禁 longest-match) + 按 docid 去重切句 (I-08)。

#### P1-6 · 【已移出 P1 编号空间 → §4.3 P2-2】
理由: 与 P1-2/3/4 **互斥**而非「收益不可叠加」—— 用 joblib 实现分支间并发会使分支**内**的 `_run_year_tasks` 全部退化为线程臂, 吃掉 5–8× 退回 ~1×, **且日志仍打印 `后端=processes`**。

#### P1-7 · stage 26 MinHash 并行 【6,762s → 1,000–1,500s】
`article_staleness.py:186` surface 轨 MinHash 是纯 Python 单线程逐 shingle 循环, 三轨合计 6,180s = **91.4%**。
G-11 (进程并行 10–20×) + G-12 (三轨共用去重文本集) + G-13 (LSHForest 按天重建 6,655 次, 388s)。
⚠ 不换 faiss-gpu (Windows 无 wheel); 语义轨 `IndexFlatIP` 非瓶颈。

#### P1-8 · stage 24 跟风衰减 【5,408s → 900–1,800s】
- **G-01 (A 档)**: `herd_decay.py:479` as-of 前缀对整个前缀算相似度却只采纳当年区间。切的是**行**范围、原样保留候选窗 `[lo, i)` ⟹ 候选对集合不变。
- **G-03 拆两半**:
  - **(a) A 档**: `:468` `prefix_end <= 2000` 硬阈值的 dense↔bucketed **选路**改成本模型 (两条路已由 `tests/test_24_herd_decay_bucketing.py` 对拍守护) —— 中型行 20–100×;
  - **(b) 🔴 day-block 变体 = 不做 / 或降 B 档**: 「同日文章共享窗口 `[lo, i_start)`」把上界从 per-article 的 `i` 拍成 per-day 的 `i_start`, **整批漏掉同日更早的前驱** (稠密参照臂 `:270-271` 的 `tril(k=-1)` 明确计入) ⟹ **改测度而非浮点末位**; 援引的「镜像 stage 26 day-bucket」是**反向证据** (`article_staleness.py:229-234` 刻意排除当天)。
- **G-02 混合粒度**: F20 粒度是「整家银行」且 `n_jobs` 写死 12, 并行效率仅 32%。
  ⚠ 全量「银行×年」细粒度**违反 R-6** (5,968 任务里 72.5% 只有 ≤5 篇), 且 as-of 前缀语义使 IPC 放大 **8.54×** (基数约 2.1 GiB ⟹ 约 18 GiB)。
  **判据**: 只对 `len(bank_df) >= 阈值` (按 >2000 篇口径, 约 15–40 家) 拆 bank×year, 其余整行提交 ⟹ 任务数 5,968 → ~1,300。

#### P1-9 · stage 00 去重层 【3,467s → ~2,000s; 复跑趟 → ~1,200s】
去重层独占 **72.8%**。三条**同批**落地 (有顺序依赖):
- **A-01**: `dedup.py:179` 每篇都 `MinHash(num_perm=128)`, ~99% 时间在 `_init_permutations`。传 `permutations=` 缓存: **482.6 µs → 2.0 µs (241×)**。⚠ 必须**同时**打 `:391-393` 的 `MinHash(hashvalues=...)` (544.0 → 1.0 µs)。
  📌 **跨阶段记账**: 同一处 `:391-393` 修复对 **stage 40 步骤 6b-3 另有 1,501s → ≈15s 的独立收益** (H-03), 该收益**记在 stage 40 名下, 不重复计入 stage 00**。
- **A-02**: `:330` 逐行 pickle (3,375 B/行 × 409 万 = 13.8 GB) → 批量返回 `(N,128) uint64`; worker 内内联置换算式 (已实测与 `update_batch` 逐位相同)。
  🔴 **须同批把 `_MINHASH_TOKENIZER_VERSION` 扩为覆盖签名计算路径的版本 token 并 bump** (`dedup.py:349-352` 的 F2 注释同批扩写触发条件); 且 §3.3 的 A/B 中 6b-3 一趟**必须删掉/绕开 `_minhash_cache/` 强制重算**, 否则该路径的字节等价结论不成立。
- **A-03**: `:563` 生产路径**没传 `cache_dir`** (而 `panel/dedup_sensitivity.py:282` 传了) ⟹ 签名 sidecar 从未启用。⚠ **不先做 A-01 就开缓存 = 负优化**。
- **A-04**: `raw_census.py:106` 每趟为写日志重解析 44 GB Excel (540s), 而它已有 `--from-summary` 通道从未被 runner 使用 → 内容寻址 memo。
- **A-05**: `:491` LSH 查询逐篇 query, 绝大多数是单例 → 向量化 band 桶预筛。
- **H-04**: `panel/dedup_sensitivity.py:289` 4 变体串行重建 LSH (613s → ≈200s)。⚠ 禁 pickle 166 万个 MinHash 对象, 走 `(N,128) uint64` npy + mmap。

#### P1-10 · stage 22 词典情感 【3,738s → 2,000–2,400s】
**E-06 先做** (仪表, 否则 E-01/E-04 无法量化验收) → **E-01** (`numerical_intensity.py:528` 三个 list comprehension 单线程跑 509,433 行, 5–8×) →
**E-02** (`tone_words.py:1622` 对同一 token 序列调 `_compute_sentiment_with_rules` **58 次/篇/轨** → 共享中间量, 合成实测 9–13×) →
**E-03** (两处进程池硬钉 12 → 20, E 核异构预期 1.25–1.5×) → **E-04/E-05/E-07/E-08**。

#### P1-11 · stage 15/16 本地段 【15: 555s → ~260s】
**C-11** (`fintech_intensity.py:384` 全局 DF 每趟在 164 万篇上重算 294s → 内容寻址 sidecar; ⚠ **指纹须含 `DF_CODE_VERSION`**) ·
**C-07** (`:275` 逐篇 `set(jieba.cut(text)) & kw_set` → AC 自动机直扫 607 词, 4–5×) · **C-06** (MAIN/_lg 两次调用的公共前置)。

#### P1-12 · 全阶段读盘优化 —— 🔴 **按处方类型分三类, 不可一律"列投影"**
| 类 | 项 | 处方 |
|---|---|---|
| **(a) 真·列投影** | K-02(65) / K-07(68, 16.8 GB→~60 MB) / K-10(67) / K-16(63) / L-05(71/72/75, 78×) / L-07(80) / J-01(51) / N-06(侧线 03/04) | `pd.read_parquet(path, columns=[...])` |
| **(b) 🔴 行级惰性抽样, 禁列投影** | **K-15 (61 号)** —— 它读全表只为 `df.sample(n)`, 若改列投影会**改变抽样总体** | `pq.ParquetFile.metadata.num_rows` + `RandomState(RANDOM_SEED).choice` + `read_table().take(pos)`; **保留 `len(df) <= target_sample_size` 的全选分支** |
| **(c) 混合** | K-08 (60 号) | 位置复算 + `iter_batches(columns=['内容','标题'])` |
| **(d) 其他** | J-02 (anti-join 元组化 → `MultiIndex.isin`) / J-03 (四产物并发写) / J-04 (5 次全帧 `df.copy()`) / J-05 (重复 `read_parquet`) | — |
| **🔴 前置项** | **P1-4 / P2-2** | `_compute_embedding_peer_network_pass` 入参改窄帧 (3.1 GiB → ~1.7 GiB) |
⚠ **落地纪律**: 前缀/后缀驱动的列族一律改用「先读 `schema.names` 再按同一前缀规则筛」的同源写法, 防止"读少了"。

#### P1-x · 内存面前置批 (解锁并行度上限)
- **G-10**: `article_sbert.py:333` 6 个嵌入列以 list-of-1D-array 写进 **17,080 MB parquet**, stage 26 整片读回再 `np.stack` ⟹ 写 180s / 读 48s / **峰值 41 GB**。改 `.npy` + `open_memmap`: 写 → ~25s, 读 → ~5s, 峰值 → <8 GB (盘上 13.60 GiB, 反而比现 16.68 GiB 省)。
  ⚠ 它压在 §2.2 想开的 `25 ∥ 15→16` 并发窗上。
  🔴 **同步清单 (四处, 缺一即崩)**: ① `core/schemas.py::OUTPUT_REGISTRY['25_article_sbert.py']`;
  ② **`core/schemas.py::_OUTPUT_FILENAME_KEYS` 的配对 `(script, filename)` 条目** (与 ① 同批, 否则 import 期崩);
  ③ stage 26 的 6 处 `_stack_track`; ④ F22 `--skip-unchanged` 指纹须纳入 `.npy` 的 sha256。
  另需裁定: `.npy` 是否进 OUTPUT_REGISTRY —— 进则须同批加固 `tests/test_stage2526_skip_metadata.py` 的 `n_calls >= n_outputs` 判据 (改为只对 `.parquet` 计数)、`tests/test_omni_fix_embed.py::test_build_output_frame_has_provenance_columns`、`tests/test_semantic_staleness_ss.py` 全套夹具。
- **K-09 / K-11**: `dict_coverage.py:576` / `tone_validation.py:1331,1372` 对完整帧 `df.copy()` 只为加两列。
- (**H-05** = P2-2 前置, 随之延后; **A-11** 判 unknown, 不进 P1。)

#### P1-13 · 审计阶段 71/72/75/64/63 向量化 + 并行
- **L-01**: `construct_orthogonality.py:209` 把 object dtype 中文标签列直接喂 `normalized_mutual_info_score` (**84,048 次调用**) → 先编码成 int codes (20–25×)。
  🔴 **必须用 `np.unique(..., return_inverse=True)`, 严禁 `pd.factorize` 默认** (出现序 ≠ 字典序); **L-04 的编码须与 `cohens_kappa_2cat` 的 `sorted(set(...))` 同序**。
  (裁决备注: 当前生产 9 个维度列恰全为 2 类, 真数据上两者 NMI 逐位相同 48/48, 1000 次 bootstrap 亦 0/1000 差异 ⟹ 该修正的价值在**与证据档硬约束对齐 + 防御未来 ≥3 类维度** (合成 2×2 随机边际翻动基率 12.5%), **不是修一个当下正在发生的破坏**。)
- **L-02** (`:178`/`:292` 双重 for 全串行, 8–12×) · **L-04** (1000 次 bootstrap 在 object dtype 上重算 κ, 实测 **17.6×**) ·
  **L-06** (`cross_media_alpha.py:252` 每事件在 16.98 万行全表上重算掩码, 5.1×) · **L-08/L-09** ·
  **K-12** (逐行 `value_counts` 求众数, 12–25×) · **K-13** (Krippendorff α 三重纯 Python 循环, 30–80×, **判 unknown 需实证**)。

#### P1-14 · 敏感性扫描阶段的参数网格并行
**K-01** (65 号「4 radius × 逐文章」`iterrows`, 10–16×) · **K-03** (69 号同型, 8–12×) ·
**K-04** (62 号 5 阈值串行重建 LSH, 4–4.8×) · **K-05** (62 号接上 `cache_dir`) · **K-06** · **K-14** (70 号 4 变体各建新事件循环/session)。

#### P1-15 · 两侧线
⚠ **先读 N-11 的共用边界**: `compute_weighted_panel` / `_align_weight_frame` / `load_input21` / `_budget_cells` 是
**listed 02 单一实现, tax 侧经 importlib 只读复用** ⟹ **改一处两侧线同时生效**;
而 `scan_hits` / `build_pair_table` / `write_outputs` / 两个 `run_pipeline.py` 是**同构两份**, 必须各改一次。

| ID | 内容 | 收益 |
|---|---|---|
| N-01 / M-01 | 加权引擎测度列分批循环 (`02:894`) 单进程 → 进程并行 | 03 段 3–5×; 侧线全链 -30%~-35% |
| N-02 / M-02 / M-07 / N-07 | `pyreadstat.write_dta` 后台线程写 (已有 `03:1300 ThreadPoolExecutor` 先例) | dta 段 1.5–2× |
| N-03 / M-11 | 03 ∥ 04 并跑 | 侧线全链 -18% |
| N-05 | `company_tax_names.yaml` 16.6 MB 被 pure-Python `yaml.safe_load` 解析 **3–4 次** → CSafeLoader / JSON sidecar | 4.4×~180× |
| M-03 / M-04 / N-08 | D4b 三重嵌套循环 (**373×**) / `drop_own_bank` 逐行 apply (**34×**) / `groupby.apply(lambda)` 向量化 (10–50×) | — |
| N-04 | `scan_hits` 纯 Python 逐行 AC 扫描 → 进程并行 | 生产 6–10× |
| M-05/M-06/M-08/M-09/N-09/N-10 | 无 track 列免跑三轨 / 4 次 groupby 归约降 2 次 / object-string 反复哈希改 factorize / budget per-scheme 化 | 引擎段 1.2–1.6× |

---

### 4.3 P2 — 结构性 / 需实证

| ID | 内容 | 前置条件 |
|---|---|---|
| **P2-1** | 解 `21→22→23` 列追加链 ⟹ 开 `22 ∥ 23` | 🔴 **收益双口径**: 冷 23 省 3,738s / **暖 23 省 ≈100s (净 2.6%)**。<br>🔴 **stage 64 硬前置**: `23_bert_tone.parquet` (649 列) 是 stage 64 的唯一载体; 若按「24 前 merge」实施, 该文件掉到 ~251 列, **词典臂 (每轨 12 列 × 3 轨 = 36 score + 36 label) 整条消失, 且 exit 0 + WARNING 静默着陆** (`tone_validation.py:2824` 只 warning)。<br>合规实现只有一种: **merge 结果必须回写 `23_bert_tone.parquet`, 保持 649 列累积契约**。<br>**结论: 暖口径下不值得做, 仅当计划中还有一次 BERT 冷启动才重新评估。** |
| **P2-2** | stage 40 五分支进程级并发 (原 P1-6 / H-01) | 🔴 **与 P1-2/3/4 互斥** (§3.2 第 5 条): 若必须做只能用 `subprocess`/独立解释器, 或内层显式 `backend='loky'`。🔴 前置 **H-05** (`runner.py:179` `_append_columns` 9 次全量深拷贝)。必须在 P1-2/3/4 **实测后**重估。 |
| **P2-3** | 编排器 DAG 级并发调度 | 🔴 依赖边落在 **`core/dag.py::StageSpec.inputs`** (W5/W6 为此预留、现全空), **不动** `OUTPUT_REGISTRY` 的 `Mapping[str, list[str]]` 形状 (被 `_validate_registry_invariant` import 期校验 + panel_loader + `test_dag_consistency` 三处锁死)。<br>⚠ `core/dag.py:145-148` **明确声明** `inputs` 空着是刻意的 (规避 CF-7 类误编排) ⟹ 必须**同批**配一个从 `read_parquet` 反查的自动比对 gate。<br>前缀守卫改为「**派发前**算出本轮执行集合 S, X 的传递上游 ∩ S ≠ ∅ 则 X 禁跳」; 预清理提前到**派发前统一执行**, 覆盖 `runner.py:416` / `article_staleness.py:560` 这类 `os.path.exists` 型软依赖。 |
| **P2-4** | G-04 stage 24 TF-IDF 增量 fit | 判 unknown, 需实证 idf 逐位一致性 |
| **P2-5** | C-02/G-07 嵌入存储 JSON → BLOB (5.0×/5.6× 放大) | 🔴 **五条硬前置 (v2 誊抄时丢失, 已补回)**: ① 迁移前完整 `copy` 一份 `_llm_cache.db.bak` 并核对 sha256 (F: 余量 1,769 GiB, 可行); ② 全库 dry-run 对拍 (随机 ≥1 万条 `assert np.asarray(json.loads(txt),f32).tobytes()==blob`); ③ 迁移期间**独占**, 严禁任何 pipeline 并发读写; ④ 迁移需 ~150–170 GB 临时磁盘; ⑤ **旧库副本在 golden 对拍通过前不得删除**; 另迁移后跑 `verify_stage21_cache_coverage` 且条数只增不减。**它是 P1-1 突破解析地板的唯一出路。** |

---

## §5 P3 — 需 golden 重生 (**一律 M0 门后, 单独打包**)

| ID | 内容 | 收益 | 为什么不在 P1 |
|---|---|---|---|
| F-01 | stage 23 开 AMP | 2.6–3.1× (5.94h → 1.9–2.3h) | 改数值 **且**作废 1,264,299 条 BERT 缓存 ⟹ 净收益可能为负 |
| F-02 | 开 `matmul.allow_tf32` | 1.4–1.5× | 🔴 **理由与 F-01 不同**: TF32 **不入** `_compute_composite` 的 11 维复合键, 也不 bump `_BERT_CACHE_VERSION` (`tone_berts.py:416` 固定字面量) ⟹ **不作废缓存, 而是旧 FP32 命中值与新 TF32 值静默混算** —— 确定性算错。**强制前置 = P0-6③ 的守卫**; 「真要入键」的动作在本条 M0 包内完成 |
| F-06 | `window_stride_ratio` 0.5 → 0.75/1.0 | 1.7–1.9× | 改测度定义, 属**研究口径变更** — **需用户裁定** |
| M-10 | 侧线稠密权源改算法内核 | branch 段 10–30× | 会破坏侧线手算锚 |
| J-08 | codebook xlsx 引擎切换 | 3–8× | 会改 xlsx 字节, codebook 入复现包 |
| A-12 | stage 00 冷路径文件级并行度调整 | 5–10% | 收益小 |
| ~~F-07~~ | torch.compile / ORT / TensorRT | — | 🔴 **本机 triton 不可用, 先行否决, 不进 M0 包** (见 §6) |
| ~~A-09~~ | opencc 换实现 | — | 🔴 **B(unknown) 档不是 C 档**, 已移入 P2 |

> **决策建议**: F-01+F-02+F-06 只在 M0 窗口内一次性打包。若近期无重生计划, **明确不做**。

---

## §6 已证伪 / 明确不做

| ID | 方向 | 实测结论 |
|---|---|---|
| F-03 | 加大 `INFERENCE_BATCH_SIZE` | ≈1.00–1.05× (已饱和) |
| F-04 | 全局按长度排序减 padding | padding 浪费本就很小, ≈1.00–1.05× |
| F-07 | torch.compile / ONNX Runtime / TensorRT | torch.compile **本机不可用** (triton `Failed to find CUDA`); ORT-CUDA FP32 乐观 1.1–1.3×, 工程量 XL, 且改运行时=改数值 |
| F-09 | 「tokenize 单线程拖慢 GPU」 | CPU 侧合计 ≤5%, GPU 已是真瓶颈 |
| I-12 | networkx 22 项中心度 / brokerage / attention_media / geography / iv_did / iv_extensions | 均已足够快, 明确 1.0× |
| K-17 | stage 66 并发不足 | 已是单事件循环 + `Semaphore(250)` + 单 session |
| M-12 | 侧线 01 步 | 实测 6.4s = 侧线全链 0.53% |
| J-06 | pyreadstat → pandas 后端 | 维持现状 = 0; 换后只值 15 秒 |
| J-07 | `write_notes_do_file` 优化 | -10%~-20% (5.26s → 4.3s), **不建议实施** |
| **73/74/81/82 (无编号结论)** | 四个审计阶段 | **T=2 dev 实测**: 73 ≈15s / 74 ≈16s / 81 ≈10–20s / 82 ≈3s (出处 `logs/run_pipeline_validation.log`、`logs/81_stata_data_audit.log`、`logs/82_export_stats_excel.log`)。⚠ 按生产规模外推**结论不变**; 唯 **81 号**有真实规模跳变 (两个 790 MB `.dta` 走 `pd.read_stata`), 若未来把 81 挂进常规验收需复测 |
| A(撤回 ×3) | opencc 触发字集跳过 / opencc 分段记忆化 / calamine `usecols` | 命中率 100% 零收益 / 实测 **0.66× 反而更慢** / pandas 先逐 cell 过 `_convert_cell` 才应用 usecols |

> **B 簇 (stage 11/12/13/14, 8 条)**: 四阶段合计 265.4s = 全链 0.18%, 证据档自陈「本簇不是瓶颈」⟹ **量级不足, 本轮不做**。
> **D 簇 (stage 21, 6 条)**: D-04 已并入 P1-1; 其余 5 条量级 <2%, 本轮不做。

---

## §7 风险登记

| ID | 风险 | 缓解 |
|---|---|---|
| R-1 | **并行放大 429 风暴** (基线趟 429 实为 43,385 行 / 2,196 次退避事件) | **P0-5①② 必须先于 P1-2/P1-3/P1-4 上线**。⚠ **令牌桶把吞吐钉在上限, 不提高上限** |
| R-2 | **内存**: 现有读数**都不是峰值**, 可用内存 **104.2 GB 非 128 GB** | **先做 P0-0 拿真峰值**, 再定 `n_jobs`; **不得用未优化的 34.4/60.3 GB 反推 worker 数**; 每条并行改动须写出「任务实参字节数 × n_jobs」预算表 |
| R-3 | **SQLite 争用 (读为主 + miss 时写)**, 137.2 GiB WAL 库; 现行处置是 warning 后丢弃缓存条目 | 见 **P0-8**。⚠ 监控不能靠 grep `database is locked` (被 try/except 吞), 必须加显式丢弃计数器 |
| R-4 | **收益不可叠加 / 互斥关系登记表** | (a) **P1-2/3/4 × P2-2 = 互斥**; (b) **P1-10 × P2-1** 压同一块 3,738s; (c) **P1-1/P1-11 × P2-3 的 16∥21 窗** (P1-1 把 stage 16 压到 521–771s 后, `min(T16', 1449)` 的可省量随之缩水, 不得按基线 1,449s 记); (d) **P1-1 × P1-2/P1-4** (嵌入读取乘数已含在后者目标里); (e) **P1-9/A-01 的 1,501s 记 stage 40 6b-3, 不记 stage 00**; (f) **I-05 按 111:57 由 P1-2/P1-3 分摊** |
| R-5 | **E 核异构**: `n_jobs` 12→24 不是 2× | 每次调整必须实测 |
| R-6 | **spawn 开销 + IPC 放大**: 粒度不得低于 ~5s | P1-8 已按「>2000 篇才拆」写死判据 |
| R-7 | **超时闸连锁** | 只按「**未并行需求** × 3」设定, **绝不为让 gate 变绿而调小分母**; 并行后实测只用于更新 `MEASURED_PRODUCTION_SECONDS` 的记录值 |
| R-8 | **共享树并发会话** (本会话期间已实弹发生: `e94bf57f` 由并发会话提交) | 严格 `git add <file>` by-name, 排除 `*constants.json` / `eval_reports`; **提交前 `git log -1` 复核 HEAD 是否漂移** |
| R-9 | **worker 日志丢失** (F27 后截断已根治, 残余是 loky 丢弃 worker logger) | 按 §3.2 第 6 条选正确模式; 每条并行项附 logger 点映射表 |
| R-10 | **供应商配额是硬天花板** | P1-4 目标标 TBD; 突破需提配额, 不是代码问题 |
| R-11 | **回滚**: 改前基线产物一旦未存就再也回不去 | 🔴 **每批改动前必须归档改前产物** (`data/processed/_baseline_<batch>/` 或 sha256 清单 + 关键 parquet 副本); F: 余量 1,769 GiB 足够。**无归档不得开工。** |
| R-13 | 🔴 **计划自身行锚随并发提交腐化 (已实弹两次)**: `e94bf57f` (07-28 23:16) 使 `core/logging.py` 463→588 行; `ec39ac3b` (07-29 00:13, **本计划落盘后 5 分钟**) 使 `strategic_diff.py` 靶点下移 +44 行, 且**新位置恰是形似的另一段 `panel.apply(axis=1)` 落列代码, 极易误改** | **§8 ⓪ 前先做一次全文行锚复检**: 逐条打印当前行内容与计划描述比对, 凡被改过的文件全部重锚; 至少给 P0/P1 处方涉及的锚补 `::函数名` (§10 已立双写纪律但 v3 全文 77 个 `x.py:NNN` 锚中 0 处落实) |
| R-14 | 🔴 **本计划与证据档两份 .md 目前 `untracked` 且未被 gitignore** (同目录已 tracked 196 个文件), 是 141 条发现的唯一副本; 本仓有 `git clean -fdX` 打掉承重资产的实弹先例 | **开工前第一件事: by-name `git add` + commit 两份 .md**; §7 增「本目录严禁跑 `git clean`」 |
| R-12 | **并行 worker 崩溃/OOM 的部分结果** | joblib 默认整批抛异常, 但须验证不会留下半写产物; 配合 P0-3 的原子写与自愈 |

---

## §8 实施顺序 (强制)

```
⓪  **纯常量提闸先行** (零风险, 5 分钟): `core/dag.py` 把 stage 72 与全部验证阶段 timeout 提到 90,000s;
    ⚠ 必须先于 ②, 因 ② 的 P1-12(a) 含 L-05 (覆盖 71/72/75), 而 72 号现闸 10,800s < 外推 ≈6.9h,
    若按 §3.3 层级 2 用编排器跑整阶段会当场重演 F19 同型强杀 (该阶段无断点 = 归零)
①  P0-0 内存峰值仪表                     ← 后续所有 n_jobs 与 §9 内存验收的校准前提
②  P1-12 读盘三类 + P1-x 内存面          ← 低风险; 同时是 P1-4/P2-2 的 OOM 前置
③  P0-7 (stage40 提闸+回填校准表) → P0-5①② → P0-8 → P0-1/P0-2 → P0-3/P0-4 → P0-6
    ⚠ 顺序不可换: P0-5① 改退避上界 = 改超时分母, 必须先于 P0-1/P0-2 重校
    ⚠ P0-5′ 的「非静默汇总闸」在本步落地 (§3.3 前置条件 2 的判据载体)
④  P1-1 缓存只读多进程分片               ← 公共乘数
⑤  P1-9 / P1-10 / P1-11                  ← 上游阶段 (00/15/16/22)
⑥  P1-7 / P1-8                           ← 26 / 24
⑦  P1-3 → P1-2 → P1-4 → P1-5 → P1-5b     ← stage 40 五大子步 (先 strat: 有 F25/F26 现成 helper)
    ⚠ P1-4 落地前先做一次零改动暖复跑归因 (NEWS_PROCESS_NS_LOG_LEVEL=INFO)
⑧  P1-13 / P1-14                         ← 验证/审计 (P1-13 是 P0-1 最终重校的前置)
⑨  P1-15                                 ← 两侧线 (先做 N-11 边界梳理)
⑩  全链重跑 → 三张新基线表 → 按「未并行需求×3」回填超时闸 + 同批更新 MEASURED_PRODUCTION_SECONDS
⑪  P2 评估 (P2-2 需重估) → P3 (仅在 M0 窗口)
```
**每批开工前**: 归档改前产物 (R-11)。**每批提交时**: 附改前/改后实测、层级 1 算子级 A/B 结果、
批末层级 2 产物 sha256、`pytest -m fast` A/B 差分、Available 最低水位。
⚠ 走 checkpoint/sidecar 的分支 (P0-3/P0-4/C-11/A-03), 两趟均须删净或绕开缓存 (§3.3 前置条件 1)。

---

## §9 验收清单

**正确性**
- [ ] 层级 1: 每条 P1 改动的算子级 A/B 通过 (`np.array_equal` / `assert_frame_equal(check_exact=True)`)
- [ ] 层级 2: 每批阶段产物 sha256 **逐字节相同**; 层级 3: §8 ⑩ 一次全链 golden diff
- [ ] **两趟的「嵌入 API 重试 .* 次仍失败」计数双侧为 0** (命中即该趟作废重跑)
- [ ] **两趟均已删净 `_ckpt_7h_*` / stage 24 sidecar / `_minhash_cache/`**
- [ ] `pytest -m fast` 相对当日 baseline-stash **`comm` 逐项集合相等**
- [ ] `test_dag_consistency.py` / `test_pipeline_shims.py` / **`test_stage_timeout_calibration.py`** 全绿
- [ ] `_compute_composite` 对现有 11 维参数组合的返回值**逐字节不变** (P0-6③ 回归测试)
- [ ] 35 个 `NN_*.py` 仍 ≤30 行

**执行证据 (防 checkpoint 假绿)**
- [ ] 改后趟日志中被改分支的计算痕迹条数 > 0 (如 7h-strat 的 `LDA K=` 行数 > 0)
- [ ] `40_build_panel.log` 首行为阶段 banner、**NUL 字节占比 = 0** (F27 后应恒成立; 基线趟实测 64.3% NUL)
- [ ] **`26_staleness_panel` 的「特征面板已合并」必现 1 次**; `75_cross_media_alpha` **或合并成功、或以「早于其上游」WARNING 显式记录** (二者必居其一, 不得两者皆无)
      ⚠ v3 首版写「出现 **2 次**」**不可达**: 75 属验证管道、主线从不重生, 盘上 75 (07-22 18:59) 已早于上游 21 (07-26 02:43), 必走 `runner.py::_merge_optin_feature_panels` 的 by-design graceful skip;
      且强行凑成 2 次会给面板加约 9 列 (基线实测 23,693 × 4,183, `cross_media` 列数 = 0), 反而打红层级 2/3 —— 若确要 2 次, 须在 §8 ⑩ 前显式编排「重跑 75 → 再跑 40」, 在 R-4 登记该跨管道顺序依赖, 并声明面板变为 4,192 列、不能沿用旧 golden 与旧 sha256

**性能 (v2 缺失)**
- [ ] **按批** (非按条) 检查改后墙钟 ≤ 改前 × 0.95; 未达标则记录并复核归因, 显著劣化才回退并记入 §6
- [ ] ⚠ **显式豁免**「使能/仪表/前置」类改动: E-06 (纯仪表, 证据档自标 0×)、A-03 (须与 A-01 同批, 单独为负优化)、P1-12 的窄帧前置

**资源与基线**
- [ ] 全链由**一次连续** `run_pipeline_function.py` 产出新基线, 同时记录墙钟与阶段和两个口径
- [ ] 产出**三张**新基线表: 主线 16 阶段 / **验证管道 16 阶段 (首次生产规模)** / 两条侧线
- [ ] 超时闸按「未并行需求×3」回填, **同批**更新 `MEASURED_PRODUCTION_SECONDS`
- [ ] `_llm_cache.db` 与 `_local_model_cache.db` 条数**只增不减**; **因锁竞争丢弃的写入批次数 = 0**
- [ ] **阶段内 `Available` 最低水位 ≥ 24 GB** (即峰值占用 ≤ 80 GB, 按可用 104.2 GB 计)
- [ ] (若做 P2-1) `64_tone_validation.log` 中每轨 `--- 词典法: N 个词典 ---` 满足 **N == 6** 且 `词典法: [...]` 列表长度 == 6
      (⚠ v2 写的「列数 ≥ 42」**不可 emit 且数值错** —— 该日志从不打印列数, 真值是每轨 12 列 × 3 轨 = 36 score + 36 label)

---

## §10 度量口径声明

- **「实测」** = 生产规模真跑日志中的直接读数, **逐条标注日志文件与趟次**; **「外推」** = 按真实行/列数 × dev 单位成本换算。
  **验证阶段 60–75 的耗时全部是外推** (T=2 dev 趟 = 662s)。**外推值不得写进超时闸分母**。
- 两套时间口径不可混用: **阶段自报耗时** (§1.1) vs **编排器墙钟** (超时闸口径, sig4 显示值)。
- 重试统计三口径 (§1.3): 重试行数 / 退避事件数 / **退避覆盖秒数 (并集)**。
  🔴 **并集是墙钟上界, 不可直接当可回收量** —— 真实可回收上限 ≈ 槽时闲置占比 (退避深度 ÷ 并发上限)。
- 内存: **RSS 瞬时/终态 ≠ 峰值**。P0-0 落地前所有内存数字只能当**下界**用。
- 「预期加速」一律给保守区间, 已扣除 spawn/IPC/异构核折损; **凡涉及线程池的提速项必须先给 GIL 释放证据, 否则按 1.0× 计入**。
- **代码行锚一律「函数名 + 行号」双写** (本仓教训: 行锚严禁硬编码, 会漂)。
- ⚠ 已内化的教训: ①「被杀时按已完成比例外推」系统性低估 (stage 23 低估 2.45×);
  ②「没有完整实测基线的阶段, 超时闸宁可给到荒谬地宽」;
  ③ **整改本身必须再被审** —— v2 的 12 条新错全是誊抄证据档/写处方时自造的;
  ④ **反推法会骗人** —— v2 的「168 次 LDA 全在 7h-strat」被 `168×274s > 34,482s` 的自洽检查当场证伪 (实为 57:111)。

---

## §11 SSOT / 文档同步清单

| 触发 | 须同批更新 |
|---|---|
| 任何 `core/dag.py` 超时改动 | `tests/test_stage_timeout_calibration.py::MEASURED_PRODUCTION_SECONDS` (含证据来源字符串) |
| P0-2 落地 | 同上文件覆盖范围扩到 `STAGES_VALIDATION` (行锚 `:26/:54/:79/:89`) |
| P0-3 / P0-4 落地 | 新增 `_<BRANCH>_CODE_VERSION` / `_HERD_CKPT_CODE_VERSION` 常量 + 各配 frozen 单测 (对齐 `tests/test_peer_prompt_frozen.py` 范式) |
| P0-5① 落地 | `embedding_engine.py:113-114` 的「800s 重试耐心」运维判据注释 |
| P0-5′ 若裁定采纳 | `CLAUDE.md` both-or-neither 条款 + `embedding_engine.py:88-94` 用户决策注释 + `policy_similarity.py:152-156` + `test_embedding_coprimary_parity` |
| P0-6③ 落地 | `tone_berts.py::_compute_composite` + `tests/test_w8_bert_inference_cache.py:176-193/294-315` |
| P1-3 落地 | `strategic_diff.py:1006-1008` 的陈旧「恒串行」注释 + `:1001-1004` 被证伪的两句自述 |
| P1-9/A-02 落地 | `_MINHASH_TOKENIZER_VERSION` 扩为覆盖签名路径并 bump + `dedup.py:349-352` 的 F2 注释扩写 |
| P1-11/C-11 落地 | 新增 `DF_CODE_VERSION` 常量 |
| P1-x/G-10 落地 | `OUTPUT_REGISTRY` + **`_OUTPUT_FILENAME_KEYS`** + stage 26 六处 `_stack_track` + F22 `--skip-unchanged` 指纹 + 三个测试夹具 |
| **本计划落盘即刻 (既有文档陈旧, 顺带订正)** | `CLAUDE.md`「`_llm_cache.db` 98.9 GB / 3,037,107 条」→ **147.3 GB / 3,596,160 条**; 「Disk 状态 172 行 / dta≈3453 列」→ **23,693 行 / 4,183 列**; Stata「64-core」措辞; **登记 F27 (`e94bf57f`)** |

---

## §12 141 条发现 → 批次映射 (**脚本生成, 已校验: 无重复、无幽灵 ID、合计 == 141**)

| 归宿 | 条数 | 发现 ID |
|---|---:|---|
| **P0** | 4 | L-03(→P0-1) · G-05(→P0-4) · H-02(→P0-3) · F-05(→P0-6)。另 P0-0/P0-2/P0-5/P0-5′/P0-7/P0-8 六条为评审新增, 无原始 ID |
| **P1** | 100 | A-01..A-08 · C-01,C-03..C-11 · E-01..E-08 · G-01,G-02,G-03,G-06,G-08,G-09,G-10..G-13 · H-03,H-04 · I-01..I-11 · J-01..J-05 · K-01..K-16 · L-01,L-02,L-04..L-09 · M-01..M-09,M-11 · N-01..N-11 · D-04 |
| **P2** | 7 | C-02 & G-07 (同一处, →P2-5) · G-04(→P2-4) · H-01(→P2-2) · H-05(→P2-2 前置) · A-09 · A-11 |
| **P3 (M0)** | 6 | F-01 · F-02 · F-06 · M-10 · J-08 · A-12 |
| **X 明确不做** | 9 | F-03 · F-04 · F-07 · F-09 · I-12 · K-17 · M-12 · J-06 · J-07 |
| **留档 (量级不足, 本轮不做)** | 15 | A-10 · B-01..B-08 · D-01,D-02,D-03,D-05,D-06 · F-08 |
| **合计** | **141** | **未分配 = 0** ✅ |

> 另: 证据档簇 A 自述**主动撤回**的 3 条 opencc/calamine 反例与簇 L 的 73/74/81/82 四条**无编号结论**
> 均不在 141 个编号 ID 内, 已单列进 §6。

---

## §13 v1 → v2 整改台账 (第一轮)

| 严重度 | 提出 | 成立 | 已整改 | 被驳倒 |
|---|---:|---:|---:|---|
| fatal | 7 | 7 | 7 | — |
| major | 28 | 24 | 24 | **D1-05** (16∥21 判断经实测正确) · **D4-04/D4-05** · **D5-5** (§1 按定义只收实测) |
| minor | 18 | 18 | 18 | — |

⚠ **D4-04/D4-05 的驳回理由需订正**: 第一轮驳回依据是「评审引用的 `core/logging.py:264-265` 代码不存在」——
**该判断在第一轮执行时(2026-07-28 白天)成立**, 但 F27 (`e94bf57f`) 于当日 23:16:52 由**并发会话**提交后,
该代码已存在于 `core/logging.py:255-265` (文件从 463 行增至 588 行)。
⟹ 驳回结论(「计划的 R-9 表述无需改」)**在 HEAD 上已不成立**, v3 已按 F27 后语义重写 §3.2 第 6 条与 R-9。
这是一条**并发会话导致的时点性失效**, 不是评审失误。

## §14 v2 → v3 整改台账 (第二轮)

| 严重度 | 提出 | 成立 | 已整改 | 被驳倒 |
|---|---:|---:|---:|---|
| fatal | 6 | 6 | 6 | — |
| major | 26 | 21 | 21 | E1-06 · E7-5 · E7-6 · E7-7 · E7-10 (措辞/假两难/旗舰证据失效) |
| minor | 18 | 15 | 15 | E2-01 (sig4 口径与既有表一致) 等 3 条 |

**v2 自造的 12 条新错 (已在 v3 全部修正)**:
1. §3.2 第 4 条选项 A `parallel_config(inner_max_num_threads=1)` **字面不可执行** (缺 `backend='loky'`, 实跑 ValueError);
2. P0-6③ TF32 「加第 12 维或 bump」会 **100% 作废 1,264,299 条缓存**, 与 §3.4 自订铁律冲突;
3. P0-3/P0-4 checkpoint 缺 `code_version` 维 ⟹ 验收**恒真假绿**;
4. P0-3/P0-4 缺原子写 (本仓 F8 范式已在侧线落地 9 处);
5. §0.6 两口径差值 5.0–5.1h 违反自设恒等式 5.914h, 冷口径偏乐观 1.2–1.6h;
6. §1.3 「全局并集 (权威墙钟口径)」把覆盖率当占用率;
7. §1.3 第四行「其余全部子步 27,839s」应为 7,774s;
8. §12 对账表六行中四行计数错、混入 7 个不存在的 ID;
9. P1-3 「168 次 LDA 全在 7h-strat」错 (实为 57:111);
10. §9 「64 号日志词典法列数 ≥ 42」不可 emit 且数值错 (真值 36);
11. P1-12 把 K-15 (行级抽样) 误并入「列投影」类, 会**改变抽样总体**;
12. §3.2 第 6 条根因表述被 F27 (`e94bf57f`) 作废。

**v3 新增的、v2 完全没有的内容**: §1.7 基线可信度声明 (部分失败趟 F28) · §4.0 逐阶段 baseline→target 明细表 ·
§3.3 两级验收 + 三条前置条件 · P1-12 三类拆分 · R-11 回滚归档 / R-12 worker 崩溃 · §9 执行证据类与性能类验收 ·
§12 脚本生成对账 · §14 本台账 · 全文行锚「函数名+行号」双写纪律。


## §15 v3 → v4 整改台账 (第三轮终审)

| 严重度 | 提出 | 成立 | 已整改 | 被驳倒 |
|---|---:|---:|---:|---|
| fatal | 3 | 2 | 2 | T1-06 |
| major | 33 | 24 | 24 | T1-01/T1-02/T1-04/T4-1/T7-2/T7-7/T7-8 等 9 条 |
| minor | 18 | 12 | 12 | 6 条 |

**v3 首版自造的 9 条新错 (v4 已全部修正)**:
1. 🔴 **§4.2 P1-3 目标乐观 2.4×** —— 4.9–6.9× 被套在整个 34,482s 上, 但其中 **15,818s (45.9%) 的「相邻期文本连贯性」F25/F26 已经并行过**;
   实测三段 6,518 / 15,818 / 12,146, 可再并行的只有 54.1% ⟹ 目标改 **12,500–16,500s**, 并连带把 §0.6 从 8.9–12.1h 改为 **10.9–14.8h**;
2. **§4.0 三个合计手写而非求和** (40 小计高端多 100s; 主线暖低端多 294s、高端多 170s) —— 违反表头自设 🔒; v4 已改脚本求和并标注校验;
3. **§9「特征面板已合并出现 2 次」不可达** —— 75 属验证管道、主线从不重生, 且强行凑成 2 次反而给面板加 ~9 列打红层级 2/3;
4. **§3.3 层级 2「产物 sha256 逐字节相同」对含 `.dta` 的阶段恒假** —— pyreadstat format-118 头部写分钟级时间戳 (实读 15:35/15:36/15:37);
5. **§9 性能闸「每条 ≤ 改前 × 0.95」** 与计划自身处方冲突 (E-06 是纯仪表 0×、A-03 单独为负优化却须同批);
6. **§2.2 表头声明「口径统一到 P1 之后」但第 2/3 行仍是基线口径** (第 2 行高估约 3×);
7. **`core/logging.py::log_execution` 全仓零命中** (真名 `log_and_time`, def :407);
8. **`NEWS_PROCESS_NO_CKPT` 全仓零命中且无人负责实现**, 却被 §3.3 前置条件与 §8 当作现成开关引用;
9. **§8 排序缺口**: 批 ② 含 L-05(71/72/75), 而 72 号提闸在批 ③ ⟹ 已新增 **⓪ 步「纯常量提闸先行」**。

**v4 新增的、v3 完全没有的内容**: §3.1 carve-out 第 ③ 类 (`.dta`/mtime_ns/G-10 形态变更) · §8 ⓪ 步 ·
R-13 (行锚随并发提交腐化, **已实弹两次**) · R-14 (两份 .md untracked, 开工前必须先 commit) ·
§4.2 P1-3 的三段实测归因表 · §1.7 的 4 个 NaN 列精确列名与 F28 修复状态 · §15 本台账。

---

## §16 交付状态

**ship_with_fixes** —— v4 可交付, 但**开工前必须先做三件事** (均 ≤30 分钟, 无技术风险):
1. 🔴 **by-name commit 两份 .md** (R-14: 目前 untracked, 是 141 条发现的唯一副本);
2. 🔴 **全文行锚复检重锚** (R-13: `ec39ac3b` 已使 `strategic_diff.py` 的靶点下移 +44 行且新位置形似);
3. 🔴 **§8 ⓪ 步纯常量提闸** (stage 72 与全部验证阶段 timeout → 90,000s)。

**残余已知不确定性 (已在正文就地标注, 不阻断开工)**:
- P1-4 (7h-emb) 目标为 **TBD**, 须先做零改动暖复跑归因;
- P1-3 目标基于**部分失败趟** (§1.7), 拿到一次四列非空的成功趟前只作规划值;
- 验证管道 16 阶段**从未在生产规模跑过**, 其全部耗时为外推 (P0-2 的校准跑将首次产出真基线);
- P0-5′ (重试耗尽是否改 fail-loud) **待用户裁定**; 但 v4 已把「非静默汇总闸」设计成无需裁定即可落地, §8 不会因此卡死。

**最小可交付子集 (若只做三条)**: ① P1-3 + P1-2 (stage 40 两大子步, 占全链 48.3%);
② P1-1 (嵌入缓存只读多进程分片, 一改惠及六处); ③ P0-7 + ⓪ 步 (两个超时闸, 防止下一次生产跑被强杀归零)。


---

## §17 🔴 并发实施状态 (2026-07-29 00:53 快照, 开工前必读)

**本计划撰写期间, 并发会话已在同一工作树上推进 HEAD 四次**, 其中后三次与本计划**直接相关**:

| commit | 时间 | 内容 | 对本计划的影响 |
|---|---|---|---|
| `f0c06ddf` | 07-27 11:29 | F25 连贯性/流动性逐年进程并行 + F26 LDA 钉死 BLAS 线程 | 本计划的基线与字节等价先例来源 (§3.2 第 4 条 / P1-3) |
| `e94bf57f` | 07-28 23:16 | **F27 子进程日志截断硬闸** + F29 孤儿模块 ERROR | 使 §3.2 第 6 条根因改写; 使第一轮对 D4-04/D4-05 的驳回时点性失效 (§13) |
| `ec39ac3b` | 07-29 00:13 | **F28 both-or-neither 静默塌缩改 ERROR + 逐列点名** | 部分满足 P0-5′ 的「非静默」诉求 (降级本身仍在, 裁定项不变); **使 `strategic_diff.py` 行锚下移 +44 行 (R-13)** |
| `04835123` | 07-29 00:53 | **S4 共享并行契约 — `_run_year_tasks` 加 `min_tasks`/`n_jobs` + OOM 兜底; 默认路径逐字节不变** | 🔴 **这正是本计划 P1-2 的前置改造** —— 其 docstring 明写新增参数是为「`policy_similarity` 的『3 轨 × N 年』扁平池」, 且独立得出与本计划相同的两条结论: ① 阈值不能跨模块硬借 (否则单测的 monkeypatch 桩不传播进 loky 子进程 ⟹ 测试失真); ② 并行度必须可控 (首跑 P=8 观测 RSS 再上 12) |

⟹ **执行者开工前必须**:
1. `git log` 确认 HEAD, **重新核对本计划全部行锚** (R-13; 已实弹腐化两次);
2. 复核 P1-2/P1-3 的**剩余工作量** —— `_run_year_tasks` 的契约扩展已由 S4 完成, 本计划这两条应改为「消费该契约」而非「新建并行」;
3. 与并发会话对齐分工, 避免两处重复实施 (R-8)。

📌 **一个正面信号**: 并发会话在不知本计划的情况下独立收敛到相同设计 (扁平任务池 / 可配并行度 / OOM 兜底 / 默认路径逐字节不变),
这为 §4.2 P1-2/P1-3 的技术路线提供了一次独立交叉验证。
