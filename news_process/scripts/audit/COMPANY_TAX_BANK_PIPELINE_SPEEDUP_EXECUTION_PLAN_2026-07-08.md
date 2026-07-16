# COMPANY_TAX_BANK 流水线提速执行计划 (v2, 2026-07-08)

**定位**: `company_tax_bank/` 三步派生流水线 (01 registry → 02 主面板 → 03 双权互验) 的运行
效率优化。上游功能已完结并推送 (`main=1891e48c`, v7 年窗 2011–2020); 本计划**不改任何
数据口径/测度/gate 判据**, 只削墙钟。权威功能计划 = `COMPANY_TAX_BANK_COOC_PANEL_EXECUTION_PLAN_2026-07-08.md` (v7)。

**触发**: 用户令"分析 `company_tax_bank/logs` 全部日志, 找出所有问题, 最重要是提高运行速度和
效率, 严禁遗漏"。本计划 = 日志全量取证 (四文件逐行) 后的结论 + 提速方案菜单, 待评审后执行。

**v2 更正**: v1 经 42-agent 多路对抗评审 (8 维度 × 独立核验), 确证 34 处缺陷 (2 P0 / 12 P1 /
20 P2, 0 驳回)。**最重的根因**: v1 系统性把税调 dta 写路径引成共享 listed 引擎, 实为 tax 02
本地 `write_outputs` → L3/L5/L6 的边界/内存/gate 判定连锁失据。v2 已逐条更正 (见 §9 v2 记录)。

---

## §0 TL;DR

- **一次全链跑 = 2215s ≈ 36.9 分钟** (2026-07-08 16:33 实测, `run_pipeline.log:68`)。
- **两项占 93.9%**: ① 03 引擎加权 1093.3s (49.4%) ② 写盘 (dta 为主项) 985.9s (44.5%)。
- **这两大头与语料规模无关** (§1.3), 生产 T=19 上耗时**几乎不变**; 但全链总墙钟 **生产 > dev**,
  因 02 的**纯 AC 扫描** (dev 仅 ~1s) 随 18.2M 语料线性放大, 生产可达十几~三十分钟 (§1.3, 待实测)。
- **日志零代码缺陷**: 三步 rc 全 0、gate + 双覆盖锚全过、registry 哈希未变。所有 WARNING 均为
  by-design 披露 (§2)。曾疑似的 "logger 名不带 tax" 已核实 = **刻意的跨管道溯源** (非 bug)。
- **提速杠杆按 ROI×安全 排序**: L1 (budget, golden-safe, 立即) → L2 (03 写盘重叠) →
  L5 (--no-emit-dta dev 快速模式); L2b (双引擎块级并行) / L3 / L4 / L6 需治理或 DEFER。

### 现状墙钟分解 (证据行号; ⚠标注估算/推算项)

| 活动 | 耗时 | 占比 | 证据 | 语料相关? |
|---|---|---|---|---|
| 03 引擎加权 (city 781.1 + county 312.2) | 1093.3s | 49.4% | `03:154,157` | **否** (网点地理驱动) |
| 写盘·dta 为主项 (02 写盘段 530.9 + city dta 239.1 + county dta 215.9) | 985.9s | 44.5% | `02:224` `03:154,157` | **否** (行数=名单×年窗) |
| 02 ②中纯 AC 扫描 | ~1s | 0.05% | `02:144-145` | **是** (文本线性; 生产 ~15-30min) |
| 02 ②中聚合/加权/gate (gate 遍历固定 447,710×1914 面板) | ~31s | 1.4% | `02:223` `02:165-173` | **大部分否** (面板尺寸驱动) |
| 加载/setup (02 load 17.02 + 03 建表/DV2 ~44⚠) | ~61s | 2.8% | `02:222` `03:1→153` | 部分 |
| 01 registry (D4 对照表 ~15s 为主) | 16.4s | 0.7% | `01:143-145,179` | 否 |
| 03 三权互验 | ~14s⚠ | 0.6% | `03:158-173` | 是 (共同支撑) |

> ⚠ **口径注**: (a) 02 写盘段 530.9s (`02:224`) 是 dta+parquet+pair+codebook **整段**, 其中 dta
> 为绝对主项; 02 未单列 dta-only 时长 (dta-only ≈525s 由吞吐反推, 见 §1.2)。city/county 的
> 239.1/215.9 (`03:154,157`) 才是日志**分列**的 dta-only 实测。(b) 03 "建表 ~44s" 与 "互验 ~14s"
> 均为**时间戳跨度/残差推算**非子阶段直读 (03 只直读 ①0.77/②1612/③0.001s, `03:212-214`); 44s =
> `03:1`(16:06:15)→`03:153`(16:06:59) 跨度, 14s = ②1612−建表44−城1023−县531 残差。(c) 两项合计
> (1093.3+985.9)/2215 = **93.9%** (直接口径; v1 的 "93.7%" 系两个已舍入分项相加所致, 已更正)。

---

## §1 根因分析

### 1.1 引擎加权 (49.4%) — 已 12× 优化, 剩余多为固有算术
- 长表规模: **branch_city 15,013,456 行 / branch_county 7,965,690 行** (落盘/剔 own-bank 后,
  `03:145,147`; ⚠ `03:139,143` 是剔除**前**构建完成数 15,015,883 / 7,967,989, 各减 2,427 / 2,299
  见 `03:144,146`)。落盘长表才是喂入引擎的行集。来源 = `银行业金融机构基本信息表.dta`
  (603,907 网点记录, 商业固定数据), 由网点地理决定, **与语料无关**。
- 引擎 = `company_listed_bank/02::compute_weighted_panel` (`listed 02:659`), 2026-07-07 COOC_SPEEDUP
  v4 已把 branch 引擎提速 12× (memory `cooc-speedup-bitwise-engine`)。
- **chunk 只护内存、不改任何输出值** (`listed 02:703` "chunk 划分不改行集/行序 → 位级无涉")。
  总算术 = 787 列 × 15M 行, **与 chunk_eff 无关**; chunk_eff 只改"每 chunk pandas 对象开销"次数
  → 提高 budget = 纯提速 (L1)。**该不变性由 `test_engine_chunk_invariance_bitwise`
  (chunk∈{1,3,100} 逐位==参照臂) 锚死**; `test_engine_bitwise_equiv_*` 只锚默认 chunk 下"新路径==
  参照臂", **不遍历 chunk_eff** (见 §4 WP-S1 gate 更正)。
- 分支: 500M budget 下 branch_city `chunk_eff = 500M // 15,013,456 = 33` (`listed 02:704`),
  branch_county = `500M // 7,965,690 = 62`。city (33) 偏小是主受益者; county (62) 次要 (§4)。

### 1.2 写盘·dta 为主项 (44.5%) — 单线程 C 序列化的固定成本
- 写盘 = **`company_tax_bank/02::write_outputs`** (税调**本地**函数, `tax 02:537-575`;
  rename@570 → `pyreadstat.write_dta`@574 → `to_parquet`@575), **非** listed 引擎的 write_outputs
  (那是独立第二实现, 税调从不调用)。pyreadstat 单线程 C 库, 无压缩 (Stata format 118 定长)。
- 三份 dta 各 ~6.53GB (447,710 行 × ~1,900 列 × 8 字节 float64 + usci str18 + 中文企业名定长串)。
- 吞吐: 02 dta-only ≈12.5 MB/s (≈525s, 由整写盘段 530.9s 扣伴生 parquet/pair/codebook 反推;
  02 未单列 dta 时长), 03 city 27 MB/s (239.1s), county 30 MB/s (215.9s) — 全 CPU-bound。
- **面板 99% 空**: 44,771 家仅 85 家有媒体共现 (`02:196`); branch 面板较稠密但仍主要是结构行。
  但**平衡骨架是设计要求** (xtset / survivorship, `02:193-195`), 不可删行。

### 1.3 铁律级洞察: 两大头**与语料无关** (但 AC 扫描随语料放大, 故总墙钟生产 > dev)
- 面板行数 **447,710 = 44,771 家 × 10 年**, 由名单×年窗决定, **与 18.2M 语料无关** (`02:184,194`)。
  → 写盘 (986s) 生产**同值**。
- 引擎处理 branch 长表 (15M/8M 行, 网点地理), **与语料无关** → 引擎 (1093s) 生产**同值**。
- ⚠ **唯一随语料线性放大的是 02 ②段里的纯 AC 扫描** (dev ~1s, `02:144-145`; `02:226` "AC 扫描对
  文本长度线性")。02 ②段总 32.33s (`02:223`) 中, 纯 AC ~1s + 聚合/加权 ~9s + **gate ~22s**
  (`02:165-173`; gate⑤ 对固定 447,710×1914 宽帧 `set_index` 是主项, **面板尺寸驱动、语料无关**)。
  生产 21_full ≈2.8M 行 (dev 为全量 0.055%, `02:215`) → 纯 AC 扫描按文本线性外推 **≈15-30 分钟**
  (受 1s 计时分辨率, 区间数分钟~40 分钟), 可成生产 02 头号项 (待 §6 实测校准)。
- 推论 (修正版): **两大头 (引擎 49.4% + 写盘 44.5% = 93.9%) 语料无关固定**, 生产上这部分 ≈ dev
  的 ~35 分钟; 但 AC 扫描是与主管道 stage 21 同性质的**语料线性项**, 生产 02 可能在 ~35 分钟固定
  成本之上再加 ~15-30 分钟 → **"纯固定成本" 仅对两大头成立, 全链总墙钟生产 > dev**。故 AC 扫描
  须单列杠杆或 DEFER (见 L7 / §7)。

---

## §2 已核验的非问题 (诚实澄清, 防误报)

三步全绿, 无一崩溃。逐条核验后, 以下**均非缺陷**:

1. **"logger 名不带 tax" = 刻意溯源, 非 bug** (`02 log:162,174` / `03 log:153` 记在
   `02_build_company_bank_cooc_panel`)。tax 02 (`:76-85`) 与 tax 03 (`:107-119`) 都有
   `_attach_engine_logging`, **刻意**把税调文件 handler 挂到被借的 listed 引擎 logger, 使 budget
   生效值/chunk 告警落进税调日志。`%(name)s` 显示引擎名 = 该行确由共享引擎代码发出的溯源标记
   (镜像主仓 `redirect_module_logger` 语义, **T-D10** 跨管道复用)。**无需修**。
2. 01:131-134 — 4 白名单豁免基名补注册 (WP0-6 ③, by-design)。
3. 01:135-138 — 3 基名缺全部源列 (`cross_outlet_tone_variance`/`cross_media_alpha`/`n_events`,
   共享树漂移, 优雅出 NaN, DEFERRED)。
4. 02:164 — 40 加权列全 NaN (dev 数据态, 生产上游重生后减少)。
5. 03:205 — branch_county ④b 篇数均值差 0.3688× (<1×, 反向证据, 已点名披露, dev 小样本)。
6. 03:173,196 — DV2 未映射 7,647 种名称 (政策性/村镇银行为主, canonical 刻意排除, 全量留痕)。
7. dev 数据态: 10 年窗仅 2017-2018 有语料 (`02:217-218`, 8 年整年 0 属预期); Spearman 偏低。

**性能异常 (非缺陷, 待深挖 2 项)**:
- A. 02 dta 写盘比 03 慢 2.2× (12.5 vs 27 MB/s, 同 6.53GB)。领先假设 = **`tax 02:570`**
  `dta = panel.rename(...)` 对 6.5GB 整帧全拷贝 + 更早 `tax 02:543` 的 `panel.copy()` (usci 注入)
  → 三帧内存压力 + AC 扫描遗留碎片 (02 写盘时 RSS 7460MB, `02:235`)。→ L3。
- B. 01 D4 对照表构建独占 01 的 ~15s (280 家银企名 × 银行 variant 子串匹配)。次要 (0.7%)。

---

## §3 提速杠杆总表

| # | 杠杆 | 预估收益 | golden | 风险 | 边界 | 优先级 |
|---|---|---|---|---|---|---|
| **L1** | 提高 03 注入 budget 500M→1.0B(→1.5B) | 引擎 ~95-170s (含 county) | **安全** (chunk 位级无涉) | 低, 可逆 | ✅ tax run_pipeline | **P0 立即** |
| **L2** | 03 内 city dta 写盘后台线程与 county 引擎**部分**重叠 | **≤239s (11%, 上限)** | 安全 | 中 (线程+GIL+内存) | tax 03 包裹层 | **P1** |
| **L2b** | 双分支面板**块级进程并行** (county 块藏进 city 块) — **取代**非叠加 L2 | ~531s (24%) | 安全 (输出无交叉) | 中-高 (2× 引擎峰值 + Windows spawn 重物化长表) | tax 03 外层 | **P1 (与 L2 互斥备选)** |
| **L5** | `--no-emit-dta` dev 快速模式 (跳 dta 仅写 parquet) | ~980s (44%, **dev only**) | 安全 (默认仍出 dta) | 低 (仅 1 条 dta 子断言降级) | tax 02:537 additive 参数 | **P1 (dev 提速)** |
| **L3** | 消除 `write_outputs` rename 全拷贝 (先 parquet→inplace rename→dta) | 02 写盘 + 峰值内存 | 安全 (仅顺序) | 低, 收益不确定 | tax 02:537 本地 (非 listed) | P2 |
| **L4** | 02→03 跨步重叠 | 最多 ~531s (24%) | 安全 | **高** (破 rc-gating 不变量) | orchestrator 架构改 | **DEFER/拒** |
| **L6** | 加权列 float64→float32 落 dta | ~490s (22%) | **破 golden** | 高 (精度+range_gate) | tax 02:537 本地 | DEFER |
| **L7** | 02 纯 AC 扫描多进程化 (`scan_hits` 天然按行并行) | 生产 ~15-30min (dev 非 binding) | 安全 (分块不改命中集) | 中 | tax 02 | DEFER (生产才收益) |

> ⚠ **边界铁律更正 (v1 错标)**: `company_listed_bank/` **零字节改动**铁律是 **T-D18** (非 T-D10);
> T-D10 = 跨管道引擎复用/禁第二份实现 (含 logger 溯源)。**L3/L5/L6 改的是 tax 02:537 本地
> `write_outputs`** (税调 03 经 `wp1.write_outputs` 复用), **对 company_listed_bank 零涉、T-D18
> 不适用** → v1 "触碰 listed 共享引擎须治理" 的框定作废。listed 加权引擎 (compute_weighted_panel
> 等) 仍零字节, 但与本三杠杆无关。

---

## §4 逐杠杆详细设计

### WP-S1 = L1: 提高 03 加权引擎内存预算 (P0, golden-safe, 立即)

**改点 (唯一)**: `company_tax_bank/run_pipeline.py:44` `_BRANCH_BUDGET_CELLS = 500_000_000` → 调高。
注入点 `run_pipeline.py:455-458` 只在 `step_id=='03'` 生效。

**chunk_eff = min(chunk=100, budget // len(Wt))** (`listed 02:660,704`):
- branch_city len(Wt)=15,013,456: 500M→**33** | 1.0B→**66** | 1.5B→**99** (未触 100 cap: 1.5e9//15,013,456=99)。
- branch_county len(Wt)=7,965,690: 500M→**62** | 1.0B→**100** (cap: 1e9//7,965,690=125→钳 100)。
- chunk 数 = ⌈787/chunk_eff⌉。city 24→(1.0B)12→(1.5B)8; county 13→(1.0B)8。

**收益 (预测, ⚠ 已被实测推翻为非单调)**: 主受益 branch_city (33 偏小); 原预测 **county 62→100
(chunk 13→8) 亦贡献次要增益 ~15-20s**, 合计 L1 ≈ **95-170s** (city ~80-150 + county ~15-20)。
⚠ **实测修正 (7db15e69 全链)**: budget 提速**非单调** — city 引擎 781→478s (−303s, 远超预测) 但
**county 引擎 312→510s = +198s 反变慢** (chunk_eff 62→100 大帧内存带宽 + WP-S2 城写盘重叠争用),
与本段"county 亦提速"的预测**方向相反**。L1 净值 ~105s 凑巧仍落在 95-170s 区间且总效应为正
(−660s), 但**生产 T=19 须 per-分支实测选最优 budget, 勿假定 county 随 budget 提高而加速**。
**非数量级, 但零成本零风险 (golden 位级不变)**。

**内存核算 (128GB 本机)**: 每 chunk 瞬时工作集 = X(8B)+V(1B)+NUM(8B)+DEN(8B) = **25B/cell**
(`listed 02:719,721,723,724`; NUM 链中间帧被 CPython 即时回收, 不额外增峰) × 15M × chunk_eff:
- 500M (C=33): ~12.4GB | 1.0B (C=66): ~24.7GB | 1.5B (C=99): ~37.1GB。
- ⚠ 另有贯穿引擎调用的**持久帧** (Wt/pos/codes ≈0.7-1GB, `listed 02:647,649,672`), 已含于下方
  总峰值估计的 buffer 内。**总峰值** ~35-45GB (1.0B) / ~50-60GB (1.5B), 128GB 余量 ~2-3×。

**落地**: 先设 **1.0B**, 跑一轮验证 + 量峰值, 有余量再试 1.5B。⚠ 现 03 日志 (`03:155,158,222`) 只有
**落盘后 RSS** (2617/2408/3205MB, 原文自述为下界), **无引擎/chunk 循环期峰值**; 故 "跑一轮量峰值"
须在**引擎加权段内**加一次 RSS 采样 (mid chunk 循环), 否则拿到的仍是落盘后下界、无法证实 24.7-37.5GB
投影。同步改注入日志文案 (`run_pipeline.py:459-460` 的 "防 chunk 收缩至 chunk_eff=2" → 已落地为
"防收缩至 city 3 / county 7" 反映 v7 年窗 15M/8M 行实值; 旧 "=2" 系 pre-v7 19 年窗遗留)。

**gate (更正)**: `test_engine_chunk_invariance_bitwise` (chunk∈{1,3,100} 位级不变, **L1 真锚**) +
`test_engine_bitwise_equiv_percol`/`_no_unmatched` (默认 chunk 下"新路径==参照臂") 全绿 +
**03 branch_city/county 面板 budget 前后『列内容哈希』实跑比对** (唯一跑在真实 03 no-track 路径且施
真实 budget 变化的检查)。⚠ 诚实声明: `test_engine_chunk_invariance_bitwise` 现仅 with_track=True
(`test:627`), 而 03 branch 是 no-track; 因 chunk 批处理循环 (`listed 02:710-`) track/no-track 共享、
行对齐在循环外先算, 覆盖缺口结构上偏弱 (非硬缺陷); 可选补一条 `_speedup_case(seed, with_track=False)`
+ chunk∈{1,3,100} 用例 (若加则 gate 计数 127→128)。dev 无 03 面板端到端 content-hash 单元测,
DEFER 到生产 T=19 复跑实证。

---

### WP-S2 = L2: 03 内 dta 写盘与下一面板引擎**部分**重叠 (P1)

**现状** (`tax 03:1065-1134` 串行循环): 每 scheme = 引擎加权 → gate → `write_outputs` (dta+parquet) →
`del panel`。branch_city dta 写 (239.1s) **阻塞** branch_county 引擎 (312.2s) 开始。

**设计**: `ThreadPoolExecutor(max_workers=1)`, branch_city 的 `write_outputs` 提交后台线程, 主线程
立即进入 branch_county 引擎; **`try/finally` 保证 `future.result()` 在 county gate 断言先抛时仍被
调用** (防 `ThreadPoolExecutor.__exit__=shutdown(wait=True)` 只等待不重抛而静默吞并发 city 写异常),
异常重抛 → fail-loud。

- ⚠ **GIL 更正 (v1 错)**: `pyreadstat.write_dta` **不释放 GIL** (`_readstat_writer.pyx` 行插入循环
  全程持 GIL, 0 处 `with nogil`); **但主线程 county 引擎的 pandas groupby.sum/mean + numpy ufunc**
  (`listed 02:719-751`) **释放 GIL** → 后台持 GIL 的写线程可在这些窗口重叠推进。故重叠为**部分并行**
  (≈ county 引擎 GIL-释放占比 × 写时长), 非全量; `to_parquet` 那段亦释放 GIL 可另重叠。**239s 是乐观
  上限, 现实约 0.3–0.9× (实测定)**。若要接近全量, 可选子进程写 dta (绕 GIL) 但须权衡 6.5GB panel
  的 IPC/重读代价。
- ⚠ **内存更正 (v1 少算一帧)**: bg 写 city dta 期间共存**三份** ~6.8GB 帧 (非 v1 的两份/13.5GB):
  ① 外层 03 city panel (WP-S2 把 `del panel` 移到 join 后故存活) ② `tax 02:543` `panel.copy()` (03
  面板缺 usci 必触发, `03:1124` 自证) ③ `tax 02:570` `dta=panel.rename(...)`。合计 ≈ **3×6.8 ≈ 20GB**。
  叠加 county 引擎 (~25-37GB@WP-S1) + 基线 → 峰值 **~45-62GB**。**治本**: 在 `tax 03:1075` 的 cols
  前置注入 usci → `tax 02:542` 判 False 消除 ② 这份多余 copy → 存活帧 3→2 (~13.5GB), 峰值回落至
  v1 所述 ~40-55GB。**若同时做 WP-S1(1.5B) + WP-S2, 峰值 ~60GB 无 2× 余量 → 联合 budget 上限钉 1.0B,
  或先做 usci 前置注入治本。**

**gate**: 新增 `test_wps2_join_background_writes_semantics` (落地名; 原提议名
`test_weight_dta_write_overlap_faildfast` 已改) — 覆盖 `_join_background_writes` 三分支: 主序正常
→ 后台写异常 fail-loud 上抛; 主序已异常 → 后台异常记录不掩盖原异常; 正常返回计时。断言 city 写失败
被 surfaced 非被 executor 吞) + 既有 dta-reading integration 全绿 (产物字节等价)。

---

### WP-S3 = L5: `--no-emit-dta` dev 快速模式 (P1, dev 提速 ~44%)

**动机**: dev 产物"不可用于任何回归" (T-D13, `02:219`/`03:209`); 三份 6.5GB dta 在 dev 是**纯废写**
(~980s)。parquet 伴生已含全量同数据 (`tax 02:575`, 未缩写全名)。生产默认仍出 dta, 行为不变。

**设计**:
1. **`tax 02:537` 本地 `write_outputs`** (税调本地文件, **不涉 T-D18/listed**) 加 additive 参数
   `emit_dta: bool = True` (默认真 → 税调默认路径零行为变化)。`False` 时跳 rename+`write_dta`, 只
   `to_parquet`。⚠ v1 误把改点定位为 listed write_outputs — 那是独立第二实现, 税调从不调用, 照 v1
   改 listed 会让 --no-emit-dta **完全失效** (税调仍走 tax 02 照写 dta)。
2. tax 02/03 + run_pipeline 加 `--no-emit-dta` flag, 透传到 tax 02 本地 write_outputs 的**三处调用点**:
   `tax 02:1110` (主面板) + `tax 03:1121` (两 branch, 循环内)。
3. **dta-reading gate 精确处置**: 唯一读**输出**面板 dta 的是 `test_usci_output_dtype_str18_in_products`
   (`test_company_tax_bank_weight_validation.py:562-577`, 混合 pq+dta 断言)。其现结构 `if dta.exists():`
   (`:573`) 在 --no-emit-dta 下会**静默丢弃** dta str18 子断言 (`:575-577`) 而 parquet 断言
   (`:570-572`) 仍过 → **dta 契约假绿**。WP-S3 须**仅对 dta 子块** `pytest.skip("--no-emit-dta: dta 未
   产出")` (**保留 parquet 强制断言, 禁整测试 skip 否则丢 parquet usci 覆盖**), 或让 gate 显式查
   --no-emit-dta 模式。⚠ 同文件 `:454/:477` 读的是**源** `BRANCH_DTA` (config 输入, 恒存在),
   不受 --no-emit-dta 影响, 无须改; 03 branch 输出 dta **无任何测试读取** (branch 校验全走 parquet)。
   备选 "改读同名 parquet" **仅对未 rename 的固定列 (usci/year) 成立**; cw_/ce_ 测度列 parquet=全名、
   dta=short_name (`tax 02:567-570`), 不可同名对读 → 优先选 pytest.skip 分支。

**边界/风险**: 改 tax 02 本地 write_outputs (**非 listed 共享引擎, T-D18 不涉**); additive 默认保行为
→ 对**税调**管线证默认路径产物零回归 (列内容哈希, 非字节 sha, 因 dta 头嵌墙钟)。**默认永远出 dta**,
快速模式须显式开启 → 生产零风险。--no-emit-dta 下**无任何 gate 转红** (仅 1 条 dta 子断言静默降级)。

**gate**: `test_write_outputs_emit_dta_flag` (False → 无 dta 有 parquet, 数据等价; True → 双出) +
`test_usci_output_dtype_str18` 的 dta 子块 skip 生效**且 parquet usci 子断言仍强制执行** + 税调 A/B
证默认路径零回归。

---

### WP-S2b = L2b: 双分支面板块级进程并行 (P1, 与 WP-S2 互斥备选)

**观察**: `tax 03:1065-1133` 单一串行 `for scheme in SCHEMES` (`:1062` "串行, 禁同持两面板"); city
块 ~1023s **完全先于** county 块 ~531s。但两块**无数据依赖**: 测度库一次构建 (`03:152`, 220 键×787
列 ≈1.4MB, 只读) + 两长表独立已落 parquet (`03:145,147`) + 各写各文件无交叉。故可块级并发, 把整个
county 块 (~531s) 藏进 city 块 (~1023s) 下 → **收益上界 ~531s = WP-S2 的两倍余, 且 subsumes WP-S2**
(二者作**互斥备选**, 不叠加)。

**风险/边界**: (a) **2× 引擎峰值**: 两引擎各 chunk 工作集, 与 WP-S1 提 budget 至 1.0B 叠加 → 2×24.7GB
+ 基线可能触破 §5 的 <60GB 目标 → 须实测, 或降 budget; (b) **Windows spawn** 须在每子进程重新物化
15M/8M 行长表 (IPC 或重读 parquet 成本); (c) 输出无交叉确定性/golden 安全。**状态**: 与 WP-S2 二选一;
因风险更高、须 profile 论证净收益, 建议先落 WP-S2 (简单包裹), L2b 作为若 WP-S2 重叠比不理想时的升级路径。

---

### WP-S4 = L3: 消除 `write_outputs` rename 全拷贝 (P2, 收益不确定)

**现状** (`tax 02:570-575`): `dta = panel.rename(columns=rename)` 复制 6.5GB (pandas 2.2.3 CoW 默认关,
rename 返回深拷贝) → `write_dta(dta)` + `panel.to_parquet(...)` 同时持两 6.5GB 帧 (叠加 `:543` 的
usci copy 实为三帧, 见 WP-S2)。疑为异常 A (02 写盘 2.2× 慢) 一因。

**设计**: `panel.to_parquet(...)` (原名) → `panel.rename(columns=rename, inplace=True)` → `write_dta(panel)`。
峰值省一份 6.5GB 拷贝。**边界**: 改 **tax 02:537 本地** write_outputs (**非 listed, T-D18 不涉**);
用**税调** A/B (列内容哈希) 复验产物字节等价。**建议**: 先做 WP-S1/S2, 若 02 写盘异常仍显著再 profile
确认 rename 拷贝确为瓶颈 (02 慢或主因是进程内存碎片而非 rename)。

---

### WP-S5 = L4: 02→03 跨步重叠 (DEFER / 倾向拒绝)

**观察**: 03 就 01/02 子流水线产物而言, 只依赖 pair 长表 (`02:177` 于 15:57:22 就绪) + registry +
branch dta, **不依赖 02 主面板 dta** (16:06:13 才完, 晚 531s)。⚠ 03 另读 **5 个主管道 processed
parquet** (`03:1044-1052`: input=21_full[required] / panel=40[required] / 16 / 27 / 51-controls
[可选]), 但这些是主管道 stage 产物、子流水线启动前即在盘, **不在 02→03 关键路径**, 反佐证 03 可在
pair 就绪即启。

**为何 DEFER/拒**: orchestrator (`run_pipeline.py:468`) 串行 subprocess + rc-gating (`:470` rc≠0 中断)
+ 单实例锁。跨步重叠破坏 rc-gating (02 未退出无法确认成功) + 若 02 dta 写在 03 已启后失败 → 03 基于
"失败的 02" 产出。高风险破 fail-loud 铁律, 收益 (531s) 不值。**本轮不做**。

---

### WP-S6 = L6: 加权列 float32 落 dta (DEFER, 破 golden)

**机理**: cw/ce ∈ tone[-1,1]/frac[0,1], float32 (~7 位有效) 或足够; dta 数值部分减半 → 写盘~减半。

**为何 DEFER**: ① 破 golden (列内容哈希在 ~1e-7 变) → 须受控全量重生; ② **cast 时点须消歧**: 若对
内存 cw/ce 列在 gate (`03:1102-1112`, 现读 float64) **之前**就地 cast (以校验真实落盘值), range_gate
1e-9 容差 (`03:1111`) 可能被 float32 舍入违例; 若仅在 write_outputs (`03:1121` 之后) 序列化处 cast,
gate 读 cast 前 float64 不受影响。③ 精度对下游 IV/Hansen 的影响须论证。改点在 **tax 02:537 本地**
write_outputs。**须独立 golden 决策**, 不在本轮。

---

## §5 边界与铁律 (改动前必读)

1. **T-D18**: `company_listed_bank/` (目录/registry/gate/产物) **零字节改动**。⚠ **L3/L5/L6 改的是
   `tax 02:537` 本地 `write_outputs` (03 经 `wp1.write_outputs` 复用), 对 company_listed_bank 零涉,
   T-D18 不适用**; listed 加权引擎仍零字节但与本三杠杆无关。
2. **T-D10**: 跨管道引擎复用 / 禁第二份实现 (含 logger 溯源, §2.1)。
3. **golden**: WP-S1 chunk 位级无涉 (安全, `test_engine_chunk_invariance_bitwise` 锚); WP-S2/S2b/S3
   仅 IO/顺序 (产物字节等价); L6 破 golden (DEFER)。
4. **rc-gating fail-loud** (`run_pipeline.py:470`): WP-S2 的 bg 写异常必须经 try/finally + future
   重抛; L4 破此不变量 → 拒。
5. **T-D13 内存**: WP-S1+S2 (或 S2b) 峰值叠加须**实测** (128GB, 目标峰值 <60GB 留 ~2× 余量);
   ⚠ 现日志只有落盘后 RSS (下界), 须在**引擎加权段内**采样才能证投影 (见 WP-S1)。
6. **确定性验收**: dta 头嵌分钟级墙钟 → 用**列内容哈希**非字节 sha256 (memory `company-tax-bank-cooc-plan`)。
7. **gate 计数**: 若加 WP-S1(可选 no-track 用例)/WP-S2/S3 的守卫测试, 同步 `README:74-75` + run_pipeline
   banner (`:208`) + 各脚本 docstring 的 gate 计数 (现 127)。
8. **共享树并发**: by-name `git add`, 排除 `*constants.json`/`eval_reports` 并发产物。

---

## §6 gate / 验收

- **WP-S1**: `test_engine_chunk_invariance_bitwise` + `test_engine_bitwise_equiv_*` 全绿 + 03 两
  branch 面板 budget 前后**列内容哈希** diff (dev 无此单元测 → DEFER 生产实证) + **引擎加权段内** RSS
  采样量峰值 + 引擎墙钟对比 (city 781→?)。
- **WP-S2**: 新 `test_..._write_overlap_faildfast` (含复合失败用例) + dta 产物字节等价 + 峰值 RSS 实测
  (证 <60GB) + 实测真实重叠比 (证 ≤239s 上限)。
- **WP-S2b** (若选): 双面板产物字节等价 + 2× 引擎峰值实测。
- **WP-S3**: 新 `test_write_outputs_emit_dta_flag` + `test_usci` dta 子块 skip 生效且 parquet 子断言
  强制 + **税调** A/B 证默认路径零回归 (非 listed A/B)。
- **本机验证套路**: 改代码类改动本机不动 parquet → baseline-stash A/B 差分证 "0 新增失败" (committed
  golden 本就陈旧, dev T=2 不新增红灯)。全量 fast 现存 8 红灯 = dev 盘上态, 全非税调 (A/B 隔离证)。
- **DEFERRED**: 生产 T=19 复跑再实测真实提速比 (§1.3 论证两大头生产≈dev, 但 AC 扫描/端到端 content-hash
  须实证)。

---

## §7 刻意不做 / DEFERRED

- L4 跨步重叠 (破 rc-gating, §WP-S5)。
- L6 float32 dta (破 golden, §WP-S6)。
- L7 AC 扫描多进程化 (dev ~1s 非 binding, 生产才收益; `scan_hits` 逐行 `itertuples`+`A.iter` 天然
  按行并行、分块不改命中集/行序 golden-safe; 生产量级待 §6 实测校准后评估是否升为杠杆)。
- WP-S2b 双引擎块级并行: 若 WP-S2 简单重叠实测收益不理想再升级 (2× 引擎峰值 + Windows spawn 重物化
  长表须先 profile)。
- **不重引入 core/aux IC 双切分 / "前 N 列"截断** (2026-06-21 已整体退役, 铁律); 单一全列 dta 不拆。
- sparse-matmul 重写引擎 (大工程 + golden 风险; 现引擎已 12× 优化位级冻结)。
- 01 D4 对照表 ~15s 优化 (次要, 0.7%)。

---

## §8 建议执行顺序 + 合成收益

1. **WP-S1 (L1 budget)** — 立即, 单行改, golden-safe, 跑一轮量峰值 (引擎段内 RSS) + 墙钟。**先落地拿基线**。
2. **WP-S2 (L2 03 写盘重叠)** — 与 S1 峰值联合核算 (usci 前置注入治本降至 2 帧) 后落地。
3. **WP-S3 (L5 --no-emit-dta)** — dev 迭代提速, 生产零风险 (默认出 dta)。
4. S1+S2+S3 后重跑, 对比新墙钟, 决定是否升级 WP-S2b / 是否做 WP-S4。

**合成收益 (范围口径, 诚实标注不确定性)**:
- **生产 (S1+S2)**: S1 ~95-170s (含 county, 稳) + S2 现实 ~70-239s (部分并行, 上限 239s, 实测定) →
  合计省 ~165-409s, 2215s 降至 **~1806~2050s (~7-18%; ~18% 仅乐观端, 中位约 13%)**。
- **dev (S1+S3; S2 在 dev 为 no-op — --no-emit-dta 下无 city dta 可重叠, **不叠减 239s**)**:
  2215s − S1(~95-170) − S3(~980) ≈ **1065~1140s (~49-52%, ~50%)**。⚠ v1 的 "~60%" 系把 S2 的 239s
  与 S3 的 980s 双减 (S2⊂S3), 已更正。

---

## §9 评审记录

- **v1 (2026-07-08)**: 初稿。四日志逐行取证 + 引擎/写盘/orchestrator/logger 源码核准。核实
  "logger 名" = by-design 溯源非缺陷 (§2.1)。
- **v2 (2026-07-08)**: 42-agent 多路对抗评审 (8 维度 × 独立核验), 确证 **34 处缺陷 (2 P0 / 12 P1 /
  20 P2, 0 驳回)**, 逐条落实。**核心更正**: ① [P0/P1] 税调 dta 写路径 = **tax 02:537 本地
  write_outputs** 非 listed 引擎 → L3/L5/L6 触 tax-local (**T-D18 不涉**), --no-emit-dta 须改 tax 02;
  ② [P1] L1 golden-safety 真锚 = `test_engine_chunk_invariance_bitwise` (非 `bitwise_equiv_*`, 后者
  不遍历 chunk_eff) + 03 branch content-hash; ③ [P1] L2 `write_dta` **持 GIL**, 靠主线程 county 引擎
  释放 GIL 做**部分**重叠, 239s 是乐观上限; ④ [P1] L2 内存实为**三帧 ~20GB** (usci copy), usci 前置
  注入可降至两帧; ⑤ [P1] AC 扫描生产 ~15-30min 未量化 → 补 §1.3 + L7; ⑥ [P1] dev 提速 ~50% 非 60%
  (S2⊂S3 双减); ⑦ [P1] "零字节" = **T-D18** 非 T-D10; ⑧ [P1] branch 行数引 `03:145,147` 非 139,143;
  ⑨ [P1] --no-emit-dta 的 dta 子断言假绿须仅子块 skip; ⑩ 补 WP-S2b 双引擎块级并行 (~531s, 与 L2 互斥);
  ⑪ 多处 P2 精度 (1.5B→99 非 cap / 980 非 981 / 44% 非 45% / 93.9% / dta≈525 估算标注 / county L1 增益)。
