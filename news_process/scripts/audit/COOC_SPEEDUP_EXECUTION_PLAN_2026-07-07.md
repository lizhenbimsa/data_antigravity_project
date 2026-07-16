# 银企共现流水线提速执行计划 (COOC_SPEEDUP, v4 施工版, 2026-07-07)

> 状态: **v4 施工版 (R1+R2+R3 三轮评审; 用户已授权执行)**。
> R2 终判: A=needs_revision(3 条文字级, v3 已落) / B=ok_to_ship(3 P2) / C=ok_to_ship(3 P2)。
> R3 终审 (新鲜视角 D 冷读 + E 施工就绪核查, 见 §11): D 9 条 (3 P1) + E 4 漂移点,
> 全部文字/清单级, 本 v4 已逐条落; E 判定 blocked(暂时) 均为 C5 已预设前置。
> R1 评审史见 §9: A=位级/浮点 (8 findings) / B=契约/测试面 (11) / C=性能/内存实证 (8),
> 三方一致 needs_revision; v2 已逐条吸收, 含一次**核心结构升级** (WP-S1 改为
> "一次对齐 + int-codes 分组", 采 C-F3 方案) 与**收益数字诚实化** (C-F1/F2)。
> 范围: `company_listed_bank/02` 加权引擎性能 (+03 三行分段计时日志); **零数值改动**。
> 非目标: 01 registry / 数学口径与列 schema / 生产 T=19 播种。
> ⚠ 行号纪律 (R1-B/F1, A/F8): 本文一切行号均为 **informative** (并发会话持续编辑 02,
> 已实测漂移 ~+12 行); 施工一律以**内容锚** (函数名/注释关键字 grep) 定位, 动工前
> 对 HEAD 重读引擎函数区全文。

---

## §0 目的与硬约束

用户令: 加快银企共现功能的速度和效率。dev T=2 全链实测 ~47 分钟, 97% 在 03。
本计划目标: **branch 引擎段提速 ~6–15×, 非 branch 引擎段塌缩到秒级; 03 全阶段
收敛到 ~550–850 秒 (3–5×)** (R3-D/F5 统一口径) — 收敛点由 ~315–440 秒的 dta
写盘地板决定 (C-F2, §1), 写盘重叠属 opt-in 二期 (WP-S6)。
**速度数字是 informative 披露, 唯一硬闸 = 位级等价 (G1/G2) + RSS (G4)**;
若实测增速低于预期不构成回滚事由, 如实写入 §8 即可 (位级分叉才回滚)。硬约束:

- **C1 位级等价 (bit-identity)**: 主验收 = G1 (uint64 视图逐位断言, 见 R1-A/F3 修订)
  + G2 (产物列内容 SHA256, 枚举见修订版)。任何位级分叉 = 失败回滚, 禁容差解释。
- **C2 契约冻结**: `compute_weighted_panel(weights, measures, registry, chunk=100)`
  签名**零变更** (R1-B/F4 定案: 新常量 `BUDGET_CELLS` = 模块级常量 + 环境变量
  **`NEWS_PROCESS_COOC_BUDGET_CELLS`** 覆盖 [R3-D/F1: 与 §3-5 统一为此唯一名字],
  **不加函数参数、不加 argparse flag**, CLI 面零变化);
  输出列名/列序 (registry SSOT)、index 名 (`company_listed_name`, `year`)、
  02 八组内联 gate、03 批量 gate、**99 项既有测试零改动全绿** (R1-B/F3 已核实
  计数与调用面成立; 测试只增不改)。
- **C3 registry 零漂移**: 01 不碰 → sha256 仍 = `023cdc9158ec52ba…`。
- **C4 SSOT 不破 + 三路径角色归档** (R1-B/F5): 改后 02 内并存三条计算路径,
  职责如下, 写入引擎 docstring 防未来误判 D18 违例:
  ① 生产路径 = 新"一次对齐+宽内核"; ② `_compute_weighted_panel_percol` = 现逐列
  实现原样冻结的**位级参照臂** (私有不导出, gate 存在即禁删, 镜像 boilerplate
  `single_pass` 先例); ③ 既有 `_sparse_equivalence_check` = 实跑内**数学对照臂**
  (60 列抽样稀疏矩阵法 isclose, 不动, 免费提供 G2 之外的交叉验证)。
- **C5 并发纪律 (R1-B/F11 升级为 A/B 窗口独占)**: 另一会话持续在 01/02 上编辑
  (其 `_log_stage_header` 不一致已由对方自行收尾 — B 评审实核) 且 15:10 又启动过
  全链重跑。动工前置条件: ① 对方**提交并推送**后 `git pull`, 把基线 commit hash
  钉入 §8; ② 树静默 (git status 干净 + 生产日志 mtime 静默 ≥120s); ③ 对引擎函数区
  与对方收尾版逐行 diff 确认无交叠; ④ **A/B 全窗口独占**: 基线采集 → 施工 → 改后
  复跑 期间禁任何第三方 pipeline run, 违反即基线作废重采。
- **C6 提交纪律**: by-name, 排除并发产物与 data 产物 (~13GB 恒不入库), 不 amend
  不 --no-verify, HEREDOC + `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`
  (注: CLAUDE.md 原文 trailer 为 Opus 4.8, 按当前 harness 约定取 Fable 5 —
  仓面既有漂移, 此处显式归档取舍, R1-B/F10)。

---

## §1 耗时证据与归因 (R1-C/F1/F7 修正版)

⚠ 两轮实测均与并发负载重叠, 数字标注"量级参考, 负载未受控"; 施工基线须按 §4-G0
在树静默下重采并分段计时。

| 段 | 14:04 轮 | 15:10 轮 | 归因 (修正) |
|---|---|---|---|
| 01 registry | 秒级 | 秒级 | 不碰 |
| 02 全阶段 | 211 s | **78.18 s** | 其中 dta 写盘段实测 **49.14 s** (15:10 轮 ⏱③, 63%) |
| 03 全阶段 | 2,743 s | — | |
| 03·loan 面板 | 71 s | 106.7 s | **≈ 引擎 ~50s + 写盘 ~50s + gate 数秒** (日志口径本含三者) |
| 03·branch 面板 | 1,591 s | — | 长表 ≈405 万行 (日志吞吐×秒复核, C-F4 确认) |
| 03·四臂+shareholder | ~920 s | — | 长表合计 ~7.8 万行 → 固定开销 + 写盘为主 |

**修正后的归因** (v1 曾把写盘+gate 混入"逐列固定开销", 高估约一半 — C-F1):
1. **引擎逐列固定开销**: 每输出列对 ~4 次分组键哈希 + Series 装配, ~2,360 列对/权源
   × 8 权源消费点 — 主修复对象 (WP-S1)。
2. **dta 写盘地板**: 每面板 105,032 行 × ~1,900 列 dta + 同名伴生 parquet,
   pyreadstat 单线程 ~40–55s/份 × 8 份 ≈ **315–440 s**, WP-S1 一秒不减 —
   v1 §7 "写盘非瓶颈"的说法**作废**; 提速后它是第一瓶颈, 处置 = 诚实计入收敛点
   + WP-S6 opt-in。
3. **03 批量 gate**: 105k×2,360 布尔全帧归约 + 逐列 dropna 循环, 每面板估 5–15s —
   次级, 挂 WP-S6。
4. **branch 数据量**: 405 万行是固定开销的放大器, 兼由 WP-S1 结构消解。

## §2 根因 (读码确认, 内容锚 = `compute_weighted_panel` 函数体)

现实现对每个测度列单独执行 4 条 `groupby([sub["company"], sub["year"]])` 聚合
(num/den/ce/nvalid), 同键被重复哈希 ~9,400 次/权源; 且每 chunk 对 Wt 全表重做一次
left-merge。分块 (chunk=100) 只护内存不省分组。数学上四条全是"同键宽表聚合"。

## §3 工作包

### WP-S1 (主收益, 核心结构 v2 升级): 一次对齐 + int-codes 分组 + 宽内核

v1 的"每 chunk merge + 每 chunk grouper"被 C-F3 证伪 (自适应 chunk 会把 branch 的
merge 从 24 次放大到 ~171 次 × 405 万行 ≈ 170–500s, 新瓶颈是方案自己引入的)。
v2 结构: **对齐与分组编码各只算一次/`Wt`, chunk 只切"哪些列同批"** (R3-D/F6
措辞定稿: 媒体权源含 track 列, `Wt = W[W.track==t]` 逐轨不同 → pos/codes 为
3 次/权源; 无 track 权源三轨的 `Wt` 是同一帧 → 对齐/编码**提升到轨循环外**只算
一次, todo/mcol 仍逐轨构造):

1. **一次对齐 (取代逐 chunk merge)**: 每个 `Wt`:
   ```python
   pos = measures.index.get_indexer(
       pd.MultiIndex.from_arrays([Wt["bank"], Wt["year"].astype("int64")]))
   ```
   探针 year level **显式 astype(int64)** 对齐目标 index dtype (R3-D/F7: 生产
   pair 表 year 为 int32, 混 dtype level 的 get_indexer 匹配路径有全 -1 风险;
   值级恒等 cast 消除之, G1 样本点名覆盖)。
   此后每列 `x` 由 `measures[c].to_numpy().take(np.clip(pos, 0, None))` +
   `pos == -1` 位置置 NaN 构造 — 行集/行序与现 left-merge 逐行相同,
   **X 必须显式以 `index=Wt.index` 构造** (Wt 经过滤后 index 非连续, 禁依赖
   位置对齐 — R2-A/N3; G1 样本天然含非连续 index 情形)。
   **dtype 语义须复刻 left-merge 行级语义** (R2-B/N4 定稿措辞): "未匹配"是行级
   事实 — **本 Wt 存在任一未匹配行 (`(pos == -1).any()`) → 本批全部 int 列升
   float64** (merge 对该行右侧全列置 NaN 的全批升格语义), 而非逐列按自身 NaN
   判定; 无未匹配行 → 全部保源 dtype。
   前置断言 (只读零数值影响): ① `assert measures.index.is_unique` (重复键下
   fail-fast raise, 比 merge 静默行扩张更 loud — 语义收紧属改进; 良数据不可达:
   build_measure_library 的 concat 对齐先崩、聚合帧 groupby 天然唯一 — R2-B/N3
   实核); ② **逐测度列 `dtype ∈ {float64, int64}` 收紧断言** (R2-A/N1 定案:
   float32 列在 merge 下保 float32 而升格规则会升 float64 → ce 累加精度路径
   分叉, 与其复刻 float32 内核不如 fail-fast 拦下; 顺带拦 nullable/Arrow 后端)。
   ⚠ **前置普查义务** (R3-D/F3): 该断言不同于 ① 的"良数据不可达" — 盘上测度库
   可能真有小整型/float32 列 (02 pair/panel 侧就有 int32/int16/int8 用例)。
   G0 基线轮必须先只读普查 `measures.dtypes.value_counts()` 写入 §8; 若出现
   集合外 dtype, **施工前**决策 (扩集合并定该 dtype 的升格复刻规则 / 上游 cast),
   禁把普查留给运行时撞闸 (中途炸 = A/B 窗口作废重排);
   ③ `assert (codes != -1).all()` (R2-A/N2: factorize -1 哨兵组 vs 现 groupby
   dropna=True 丢行语义分叉, 键非空断言 fail-fast 封死)。
2. **一次分组编码**: `codes, uniques = pd.factorize(MultiIndex.from_arrays([Wt["company"], Wt["year"]]))`
   每 `Wt` 一次; 之后所有聚合 `DataFrame.groupby(codes)` — 内核逐行序累加不受
   分组标签表示影响, **每列算术与现窄路径同序同内核 (pandas 2.3.3 group_sum/
   group_mean, Kahan 补偿两侧一致 — R1-A/F1 已核)** → 位级 by construction。
   结果 index 由 `uniques` 重建为 (company, year) MultiIndex 并 `sort_index()`
   复刻现 sorted-groupby 序 (纯行置换, 位级无涉)。
3. **每 chunk 宽内核** (chunk 语义不变, 仍是"每批多少列"):
   ```python
   X   = <按 §3-1 对齐构造的本批宽帧>          # batch_cols 定义见下
   V   = X.notna()
   NUM = X.fillna(0).rmul(sub_w, axis=0).mul(V)   # NUM 复刻现乘序 (w*x)*valid —
                                                   # R1-A/F2 保守式 (限 NUM; DEN 的
                                                   # V×w 与现 w×valid 靠 IEEE 乘法
                                                   # 交换律位级同值 — R3-D/F9 限定)
   DEN = V.mul(sub_w, axis=0)
   g_num, g_den = NUM.groupby(codes).sum(), DEN.groupby(codes).sum()
   g_ce, g_nval = X.groupby(codes).mean(), V.groupby(codes).sum()
   cw  = g_num / g_den.replace(0, np.nan)   # den==0 → NaN 非 inf, 逐字保留现语义
                                             # (R3-D/F9: 唯一此前未点名的算术步)
   ```
   `batch_cols` 定义 (R1-B/F6③): 本批 `(out_name, mcol)` 中 mcol 存在于测度库者,
   **去重**后作宽帧列; 逐 (out_name, mcol) 从宽结果**按名取列**装配 (重复源列名 —
   track-agnostic 条目 — 天然共享同一聚合结果, 禁宽切片重复标签)。
   缺源列 → 空 Series 路径原样保留。
4. **N=1 短路** (保持现语义, R1-A/F4 修订): 由宽 `g_nval`/`g_den` 精确复刻现
   `nvalid==1 ∧ den>0` 命中组集 (两者已位级等于窄路径 → 命中集恒等; **命中集
   逐列不同**); **行成员掩码 = 本 chunk 全列命中 codes 的并集** (R3-D/F4 定稿:
   `np.isin(codes, union_hit_codes)` 每 chunk 一次 — 并集子集上 first 对任一列的
   命中组仍恒等; 禁按单列 hit_codes 做全 chunk 掩码, 也禁逐列重算组成员),
   逐列仍以各自 `one` 索引赋值; 命中列逐列在行子集上跑现 `x[valid].groupby(...).first()`
   (布尔过滤保序, nvalid==1 组仅 1 条 valid 行 → first 无顺序依赖, A 评审 CONFIRMED);
   赋值端复刻现 `cw.loc[one] = xonly.loc[one]` 的对齐-升格行为。
   **诚实披露** (A/F4): dev T=2 下大量组只挂 1 家银行 → 命中列数可能 ≈ 全列数,
   短路段退化为"小子集逐列 first" — 收益下调已计入 §0 收敛点区间。
5. **自适应 chunk (仅护内存)**: `chunk_eff = max(1, min(chunk, int(_budget() // max(len(Wt),1))))`;
   `_budget()` 读 **`NEWS_PROCESS_COOC_BUDGET_CELLS`** (默认 6e7; R2-B/N2:
   遵全仓 `NEWS_PROCESS_*` 前缀约定, 且 02 头部日志环境段打印生效值供 G4 复现)
   — **v2 下 chunk 大小与
   merge/分组成本完全解耦** (对齐/编码在 chunk 外), 退化面消失 (C-F5 的
   chunk_eff=1 灾难路径不复存在, 仍保留 `chunk_eff < 4 → loud WARNING` 护栏)。
   chunk 划分不改任何列的行集/行序 → 位级等价与 chunk_eff 无关 (A/F5 CONFIRMED,
   其前提 measures.index 唯一已由 §3-1 断言钉死)。
6. **内存预算 (A/F6 + C/F4 + R2-C/N2 完整账)**: 每 chunk 瞬时 ≈ X/NUM/DEN
   3 帧 float64 + V 1 帧 bool + 链式临时 ~2 帧 ≈ **41B × len(Wt) × chunk_eff**;
   branch (4.05e6 行, chunk_eff≈14) → chunk 瞬时 ~2.3GB, 且 v2 已**消灭** merge
   产出 `sub` 常驻帧 (现路径本身的 ~3.4GB@chunk=100)。**真实峰值主项另有一笔
   与现路径共有的项** (R2-C/N2, 非回归): `results` 输出累积 + `pd.DataFrame`
   宽装配 ≈ 2 × (组数 × 列对数 × 8B), branch 尺度 ~4GB×2 — G4 峰值披露按
   "chunk 瞬时 + 输出装配"双项预期, 勿把 2.3GB 误当峰值全账。
   峰值方向结论不变: **不高于现状**。G4 的 RSS 口径 = psutil 终态读数
   (与现日志同口径) + 峰值以 dev 实测披露。

**冻结参照臂**: 现逐列实现整体原样冻结为 `_compute_weighted_panel_percol`
(含其内部 merge — 参照臂保持现路径的一切, 连低效一起冻结)。

**预期收益 (工程估算, 非承诺, 以 G4 实测为准 — A/F7, 数字经 R2-C/N1 复核修正)**:
非 branch 的 7 处消费 (长表 ≤7.7 万行) 塌缩到秒级; branch 引擎段 = ~171×4 次
宽内核 (ceil(787/14)≈57 chunk/轨 × 3 轨, 带宽受限: 4.05e6 行 × ~2,361 列 ≈
9.6e9 单元 × 4 内核族 + ~5 趟元素级) → **~100–250s** (非 v2 曾写的 "<100s");
另 `groupby(codes)` 每调用对 int64 codes 重 factorize 计 ~15–35s (R2-C/N3,
可接受; G4 实测冒头再以 Categorical.from_codes 零风险消除)。
**03 全阶段 2,743s → ~550–800s (上沿略紧, R2-C 复核 ≈550–850s); 全链 47 min →
~11–14 min** (写盘地板 ~315–440s 单列, 见 §1-2; 后续 WP-S6 落地可再探 ~350–450s)。

### WP-S2 (备胎, 默认不做): NumPy `np.add.at` 全列聚合
绕 pandas 内核 → 丢 Kahan 补偿, 位级不可 by-construction (A 评审确认 pandas 2.3.3
group_sum 带补偿求和)。仅当 S1 实测后 branch 引擎段仍 >400s 且用户显式认可数值
等价降级时启用。

### WP-S3 (opt-in 二期, 默认不做): branch 城市级预聚合再广播
数学精确、位级存疑 (组内行序变), 收益在 v2 结构下边际; 与既有 WP-E (branch
生产前重估) 合并评估。

### WP-S4 (刻意不做): 七面板进程级并行
branch 长杆 + Windows spawn 序列化 3GB 级测度库/骨架 + 日志交织破坏 12 号结构段。

### WP-S6 (opt-in 二期, 默认不做; 吸收 C-F2/F8 次级杠杆, 触碰 03 故独立成包)
① 写盘/计算流水线重叠 (面板 k 写盘线程化与面板 k+1 引擎重叠 — 纯 I/O 不碰数值,
位级平凡安全; 是打穿 ~350s 写盘地板的唯一途径); ② 03 批量 gate 向量化
(`notna()` 物化一次复用 + 逐列 dropna 改列块归约 — gate 只读, 位级无涉);
③ own-bank 剔除 isin 向量化复核 (branch 13s, 小头)。v1 全链"一个数量级"目标
若要达成必须启用本包; v2 默认收敛点不依赖它。

### WP-S5 (DEFERRED, 挂既有 WP-E): 02 AC 扫描生产侧
dev 17.84s 非痛点; 生产 18,198,978 篇按行数线性外推为真长杆, 与 branch/RSS 生产重估
(WP-E) 一并按生产语料实测定方案。

---

## §4 验收 gate (全过才许提交)

- **G0 基线重采 (新增, C-F1/F7; R3-D/F8 + R3-E 补全)**: C5 前置条件满足后:
  ① **pytest 绿锚**: 先跑三个 company_bank 测试文件确认 99 项起点全绿 (本仓有
  flaky 前科, 无起点锚则 G5 失败无法归因);
  ② 给 03 七面板循环加**分段计时** — ⚠ R3-E 漂移点: 盘上已有另一会话加的整段
  计时器 `_tp/_elp` (单行合并汇报"引擎加权+批量 gate+dta 写盘"), 施工 = 把该
  合并计时**拆成 引擎/gate/写盘 三段** (改造既有行, 禁叠加双份计时);
  ③ 跑**树静默基线** (命令钉死: `F:\Anaconda3\python.exe <绝对路径>\company_listed_bank\run_pipeline.py --steps 02,03`
  — R3-E 核实支持跳过 01; 禁裸 `python`): 产出 §1 归因表受控版 + G2 基线哈希
  清单 + **测度库 dtype 普查** (§3-1② 前置义务) + 基线 commit hash 钉入 §8;
  ④ 基线轮与改后轮头部日志核对 pandas==2.3.3 与解释器一致 (位级分叉勿误判)。
  此步使 §6 改动面 = 4 文件 (02 + 03 + tests + 本计划)。
- **G1 冻结参照臂位级等价 (A/F3 + B/F6/F7 修订)**: 新 gate 测试断言新路径 vs
  `_percol` 参照臂: ① `assert_frame_equal(..., check_exact=True)` (契约面: 列序/
  index/dtype/NaN 位置); ② **真位级**: 逐 float64 列
  `a.to_numpy().view(np.uint64) == b.to_numpy().view(np.uint64)` 逐元素断言
  (NaN 同内核保 canonical 位型; ±0.0 分叉在此翻红 — assert_frame_equal 测不出);
  ③ 样本**钉死 seed**, 显式覆盖: 含 track/无 track、缺源列、track-agnostic 重复
  源列、**混合 N=1** (同组对列 A nvalid==1 对列 B nvalid>1)、den>0/den==0 边界、
  int64 测度列、整型 w、w=0 行、负值测度、含 NaN float 列、**有/无未匹配 (bank,year)
  两种对齐情形** (dtype 升格分支; 须点名"有未匹配行 + int 列在匹配行内自身无 NaN"
  组合 — R2-B/N4 行级升格语义的判别用例); ④ 参数化 `chunk ∈ {1, 3, 100}` 断言
  结果位级不随 chunk 变; ⑤ **重复键负例** (R2-B/N3): measures.index 含重复键 →
  断言新路径 raise (把 fail-fast 契约锁进测试, 防未来删 assert 使新路径退回
  merge 静默扩张语义; `_percol` 参照臂保留 merge 行为属刻意, 两臂在坏数据上
  分叉 by design, 负例只测新路径); ⑥ **混 dtype 键样本** (R3-D/F7):
  weights.year=int32 vs measures.index.year=int64 (生产媒体路径实态) →
  断言新路径与参照臂位级同值 (锁 §3-1 的 astype(int64) 探针 cast)。
- **G2 A/B 产物位级 (B/F2 修订; R3-D/F2 dtype 分派)**: 枚举 (实际文件名经 R3-E
  盘上核实) = **8 面板伴生 parquet (主哈希对象, 真复用 WP-A 幂等先例:
  `company_bank_cooc_panel.parquet` + 7 份 `company_bank_{scheme}w_panel.parquet`)
  + pair 长表 `_company_bank_cooc_pairs.parquet` + 7 份
  `_company_bank_altweights_{scheme}.parquet`**; dta 为辅: 读回后逐列哈希,
  **dtype 分派** — 数值列 `values.tobytes()`; object/str 列 (company_listed_name/
  stock_code 等) 用确定性序列化 `"\x1f".join(col.astype(str)).encode("utf-8")`
  (object 数组 tobytes 是指针字节, 跨进程恒分叉 — 禁用); 变量标签走
  `meta.column_names_to_labels`; 列名序入哈希 (dta 文件级 SHA256 因 pyreadstat
  头部时间戳不可复现, **禁**直接哈希文件字节)。逐列恒等 0 例外, 分叉即回滚查因。
  ⚠ R3-E: 盘上现存 dta 新旧混杂 (15:37 轮进行中, 旧轮无 stock_code 列),
  基线哈希必须取 C5 后完整重跑的同代产物, 现存文件一律不作基线。
- **G3 registry 恒等**: `023cdc9158ec52ba…` 不变。
- **G4 性能实测报告**: G0/改后两轮分段计时对照写入 §8; RSS = psutil 终态 ≤ 基线
  1.2× + dev 峰值披露 (口径写死, A/F6)。
- **G5 回归**: 99 项既有测试零改动全绿 + 新 gate 全绿 + ruff + py_compile +
  跑完 pytest 后四生产日志 mtime 零变化 (WP-A 守卫复验)。

## §5 风险与回滚

| 风险 | 等级 | 处置 |
|---|---|---|
| get_indexer 对齐与 left-merge 语义分叉 (dtype 升格/未匹配行) | 中 | §3-1 dtype 复刻规则 + G1 ③ 双情形样本 + G2 全量兜底 |
| codes 分组结果序与现 sorted 序不同 → 装配错位 | 低 | uniques 重建 MultiIndex + sort_index (纯置换); G1 ① index 断言 |
| N=1 短路命中集/赋值升格漂移 | 中 | 命中集由位级恒等的 g_nval/g_den 推导 (恒等传递); G1 ③ 混合 N=1 样本 |
| 宽帧瞬时内存 (branch) | 低 (v2 账 ~2.3GB, 低于现状) | 自适应 chunk + G4 RSS 闸 |
| pandas 未来版本换内核 / nullable 后端 | 低 | 版本锁 pandas==2.3.3 (requirements.lock) + 引擎入口 dtype 断言 |
| 并发会话撞车 | 高 | C5 四条前置 + A/B 窗口独占 (违反即基线作废) |
| 回滚 | — | 单一 by-name 提交 `git revert`; `_percol` 参照臂常驻可一键切回 |

## §6 交付物与提交纪律

改动面恰 **4 文件**: `company_listed_bank/02_*.py` (引擎重构 + `_percol` 参照臂 +
BUDGET_CELLS 常量/env) / `company_listed_bank/03_*.py` (仅 G0 三行分段计时日志) /
`tests/test_company_bank_cooc_panel.py` (新增 gate) / 本计划 (§8 执行记录)。
README/codebook 零改动 (B/F9: 前提 = 零 CLI 变化, 已由 C2 定案满足)。
提交纪律见 C6。

## §7 刻意不做清单 (归档理由, 防未来误启)

WP-S2 NumPy 路径 (丢 Kahan, 位级不可证) / WP-S3 城市预聚合 (位级存疑+边际) /
WP-S4 并行 (spawn 成本+日志交织) / float32 降精 (破位级) / dta 直接文件哈希
(pyreadstat 时间戳不可复现) / v1 的"每 chunk merge + 自适应缩 chunk"结构
(C-F3 证伪: merge 次数 ×7 放大)。

## §8 执行记录 (2026-07-07 实施, 全闸通过)

- [x] R1 评审 (3 视角, 全 needs_revision) → v2 修订 (结构升级 + 收益诚实化)
- [x] R2 收敛评审: A=needs_revision(3 文字级) / B=ok_to_ship / C=ok_to_ship → v3
- [x] R3 终审 (D 冷读 + E 就绪核查, §11) → v4
- [x] 用户授权施工 (用户令: "授权执行计划")
- [x] **C5 前置 (一处记录在案的偏差)**: 并发会话第三轮全链重跑 16:21:44 干净收官;
  四脚本 mtime 15:25–15:26 **早于**运行起点 15:33 → 该轮产物 = 盘上代码产出,
  直接充当 G0 基线运行 (A/B 独占窗口最短化, 不再重烧 45 分钟)。**偏差**: 对方
  "提交推送"未发生 (盘上 01/02/03/run_pipeline 含其未提交编辑, 自 15:26 起静默),
  引擎函数区与其编辑零交叠 (R3-E 实核) → 施工照进行, 提交按仓库既有
  hunk-拆-patch 先例只取本计划改动。基线代码态 = HEAD 59c14697 + 对方未提交编辑。
- [x] **G0**: ① pytest 绿锚 99/99 (0 FAILED); ② 03 计时拆三段 (改造既有 _tp/_elp);
  ③ 基线哈希 16 parquet + 8 dta 零缺失 (scratchpad baseline_hashes.json);
  **dtype 普查 (救了计划)**: 测度库 787 列 = float64 542 / **Float64 156** /
  **float32 42** / int64 25 / **Float32 21** / **Int64 1** — v4 的 {float64,int64}
  收紧断言在真数据必炸 → 定案改 **A-R2-N1 修法② 定义级复刻** (numpy 列 take_nd /
  EA 列 .take(allow_fill=True), 与 merge 内部同函数), 断言放宽为普查全集 6 种;
  index 唯一 ✓; ④ 解释器/pandas 一致 (F:\Anaconda3 python 3.13, **pandas 2.2.3** —
  结果评审 G/F1 更正: 实跑走 conda base 2.2.3, 2.3.3 是 requirements.lock 的 venv
  锁版; A/B 两轮同版本, 位级等价由 G1/G2 实证, "同内核"论证对 2.2.3 同样成立)。
- [x] **WP-S1 施工**: 02 引擎重构 (一次对齐 `_align_weight_frame` + factorize
  int-codes + 宽内核 + N=1 并集掩码 + 自适应 chunk `NEWS_PROCESS_COOC_BUDGET_CELLS`)
  + `_compute_weighted_panel_percol` 参照臂冻结 + 三路径角色归档注释;
  03 三段计时。施工中 gate **真抓到一处分叉**: MultiIndex.factorize 把 uniques
  的 year level 升 int64, 与参照臂 groupby-by-keys 的 int32 输出 index 分叉 →
  修 = set_levels astype 复刻键列原 dtype (G1 的存在价值实证)。
- [x] **G1**: 新 gate 11 项全绿 (位级 6 seed×track + chunk{1,3,100} 不变量 +
  混合 N=1 + 重复键负例 + uint 视图逐位断言含 nullable 掩码/数据双比)。
- [x] **G2 (终裁)**: B 轮 vs 基线 — **24 文件 (16 parquet + 8 dta) / 30,487 列 /
  0 分叉, 全部位级恒等** (含 dta 读回 dtype 分派哈希 + 变量标签)。
- [x] **G3**: registry_sha256 = 023cdc9158ec52ba… 恒等, config/ 零改动。
- [x] **G4 (实测, informative)**: 03 全阶段 **2,764s → 556.7s (5.0×)**;
  02+03 全链 631.9s (~10.5 分钟, 原 ~47 分钟)。逐面板 (引擎+gate+写盘):
  loan 106.7→57.7 (引擎 3.85s) / **branch 1,591→174.4 (引擎 124.2s, ~12×,
  落在预估 100–250s 窗口)** / board 6.65 / supervisor 3.42 / exec 5.45 /
  dsg 7.19 / shareholder 2.62 — 非 branch 引擎段全部塌缩到秒级 ✓;
  写盘地板 ~50s/面板 恒定 (7×≈350s, 与预言一致); gate ~1.4s/面板。
  RSS: 03 终态 3,063MB ≤ 基线 3,083MB (1.2× 闸大幅富余, 且**低于现状**)。
- [x] **G5**: 110/110 (99 既有零改动 + 11 新 gate) / ruff 全过 / py_compile /
  pytest 后四生产日志 mtime 零变化 (WP-A 复验)。
- [x] **执行结果评审 (两路新鲜代理)**: F (实现正确性) = **ok_to_commit** —
  逐行对照两臂 + take_nd/EA.take 与 merge 的 dtype 语义探针实证, "数学复刻未发现
  任何遗漏或静默错误路径"; G (证据链) = **evidence_solid** — G2 独立复算 (24 文件
  30,487 列 0 分叉, 数字逐字复现) + 盘上直读重算 12/12 列哈希 MATCH 防伪 +
  时间线全链自洽 + G1 红灯有原始记录非事后编造。
  评审后落修 4 项 (均不触数值路径, G1 gate 112/112 复验兜底): ① §8 pandas 版本
  更正 2.2.3 (F/G 同发现); ② `_budget_cells` 补 OverflowError 兜底 (F-2, env=inf
  实证回退默认); ③ G1 补 no_unmatched 全匹配臂 ×2 + Float32 EA 列 (F-3 覆盖缺口);
  ④ 探针 cast 改取库侧 index 层 dtype 非硬编码 int64 (F-5 加固) + BUDGET_CELLS
  生效值一次性入日志 (G-F2, R2-B/N2 补落)。
  F-4 (weights index 隐性前提) 记录在案不改 (生产调用面均为干净 RangeIndex);
  G-F3 (基线日志被 B 轮覆盖无留存) 记录为流程教训: 下次重跑前先拷贝基线日志。
- [x] **by-name 提交**: 4 文件 (02 / 03 / tests/test_company_bank_cooc_panel.py /
  本计划)。⚠ 披露: 02/03 同时含另一会话同日未提交的日志富集 + stock_code 增列
  编辑, 与本计划改动纠缠 (03 的分段计时改写其未提交计时行) 无法拆 patch →
  按共享树先例 (5f8e9a62 曾将本会话盘上态一并提交) 整文件入库并在 commit
  message 披露; 01/run_pipeline (纯对方编辑) 与 v3_5_1_constants.json 等并发
  产物刻意不提交, 留对方会话收尾。

## §9 R1 评审史 (2026-07-07, 三代理并行, 全部 needs_revision → v2 吸收)

- **A (位级/浮点)**: F1 前提补全 (pandas 2.3.3 Kahan 宽窄同内核 ✓ / dtype 断言) ·
  F2 -0.0 论证不严 → 定案采保守 `.rmul` 复刻式 · F3 **G1 非位级闸** → 补 uint64
  视图断言+钉 seed · F4 N=1 短路性能前提未验证 → codes 掩码复用 + 诚实披露 ·
  F5 chunk 无关性成立 (补 index 唯一断言) · F6 内存账 6–8 帧当量 · F7 收益免责 ·
  F8 行号重锚。
- **B (契约/测试)**: F1 行号全线陈旧 (并发编辑实证) → informative 化 · F2 G2 枚举
  缺伴生 parquet + dta 哈希规范缺失 → 修订 · F3 99 项计数核实 ✓ (利好) · F4
  BUDGET_CELLS 与 C2 矛盾 → 定案 env 覆盖零签名 · F5 三路径角色归档 (含既有
  sparse 对照臂) · F6/F7 G1 样本缺口 (seed/混合 N=1/重复源列/int dtype) → 补 ·
  F8 attrs/稳健臂/index 名实核无恙 ✓ · F9 恰 3→4 文件 (G0 计时) · F10 trailer
  取舍归档 · F11 A/B 窗口独占。
- **C (性能/内存)**: F1 归因混入写盘+gate (loan ≈ 引擎 50 + 写盘 50) → §1 重列 ·
  F2 **写盘地板 ~315–440s 打穿 v1 收敛点** → 200–350s 作废, 改 550–800s +
  WP-S6 opt-in · F3 **每 chunk merge ×171 次新瓶颈** → 核心结构改一次对齐
  get_indexer + codes 分组 · F4 内存账修正 (v2 反而低于现状) · F5 chunk_eff=1
  退化在 v2 结构下消失 · F6 生产外推成立 (骨架/branch 长表不随 T=19 膨胀;
  真长杆 = 02 扫描, 挂 WP-E ✓) · F7 两轮数字漂移 → G0 受控基线 · F8 次级杠杆
  清单 → WP-S6。

## §11 R3 终审史 (2026-07-07, 新鲜视角 D 冷读 + E 施工就绪, → 本 v4)

- **D (needs_revision → 修后可施工)**: F1 [P1] C2/§3-5 env 名矛盾 → 统一
  `NEWS_PROCESS_COOC_BUDGET_CELLS`; F2 [P1] G2 dta 辅哈希 object 列 tobytes=
  指针字节不可复现 → dtype 分派定稿; F3 [P1] dtype 收紧断言缺盘上普查 → G0③
  普查义务 + 施工前决策; F4 N=1 掩码歧义 → 全列命中并集定稿; F5 §0 与 §3 收益
  口径矛盾 → 统一 6–15×/550–850s + "速度 informative、硬闸=位级+RSS"; F6 对齐
  "一次/权源"对媒体路径为假 → "一次/Wt + hoist 结构"定稿; F7 G1 缺混 dtype 键
  样本 (year int32 生产实态) → §3-1 探针 astype(int64) + G1⑥; F8 §8 缺 pytest
  绿锚/复跑命令/解释器钉定 → G0①③④; F9 代码片缺 cw 行 + "复刻乘序"限定 NUM。
  核实通过: 99 计数 ✓ / 8 消费点 ✓ / 全部数字账自洽 ✓。
- **E (blocked 暂时, 均 C5 预设前置; 代码层 ready)**: 漂移点 = ① 02 引擎函数体
  与对方未提交编辑**零交叠** (对方逻辑改动仅 stock_code 一项, 在 main/write_outputs);
  ② 固定列 19→**20** (stock_code, G1/G2 按 20 列); ③ 03 已有 `_tp/_elp` 整段
  计时 → G0② 改造既有行而非叠加; ④ 盘上 dta 新旧混杂禁作基线。产出施工重锚表
  (内容锚+当前行号) / G2 实际文件名清单 / `run_pipeline.py --steps 02,03` 可用 /
  子进程 `[sys.executable, -u, ...]` cwd=REPO、pytest 须从 repo 根。

## §10 R2 收敛评审史 (2026-07-07, 同三员带 R1 上下文复核 v2 → 本 v3)

- **A (needs_revision → 修后 ok)**: R1 F1–F8 **8/8 closed**; 新结构位级审查:
  get_indexer+take 主干 ✓ / groupby(codes) 同内核同行序 ✓ / uniques+sort_index
  纯置换 ✓。新缺陷: **N1 [P1]** float32 列升格规则与 merge 分叉 → 定案 dtype
  断言收紧 `∈ {float64, int64}` (§3-1②); N2 factorize -1 哨兵 vs dropna 语义 →
  `assert (codes != -1).all()` (§3-1③); N3 X 须显式 `index=Wt.index` (§3-1)。
- **B (ok_to_ship)**: R1 F1–F11 **11/11 closed**; G0 三行计时日志与测试面零冲突
  (实核: 无测试断言 03 日志内容); is_unique 断言良数据不可达/mock 不触发实核 ✓。
  P2: N2 env 前缀 → `NEWS_PROCESS_COOC_BUDGET_CELLS` + 头部日志打印 (§3-5);
  N3 G1 补重复键负例 (G1⑤); N4 dtype 升格是**行级全批**语义 → §3-1 措辞定稿
  + G1③ 点名判别用例。
- **C (ok_to_ship)**: R1 F1–F8 closed (F4 partial → 本版 N2 补账后 closed);
  量级复核: 一次对齐/编码 <10s/权源 ✓; branch 引擎 ~100–250s (修正 v2 的
  "<100s" 与 "24×4" 笔误 → "~171×4", §3 收益段); N2 内存峰值补
  "results 累积+装配 ~4GB×2 (与现路径共有)" (§3-6); N3 codes 重 factorize
  ~15–35s 记录, G4 冒头再消 (§3 收益段)。
- **收敛依据**: 三方一致剩余项均为文字/断言级、不动结构不改 gate 框架,
  "修订后无需再开一轮评审"。
