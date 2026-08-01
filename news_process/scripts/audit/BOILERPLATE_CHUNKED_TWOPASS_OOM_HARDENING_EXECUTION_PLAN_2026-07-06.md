# boilerplate 生产 T=19 OOM 硬化 — exact two-pass (chunked + disk-tier) 执行计划 (2026-07-06)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 状态: **v2 — 四路对抗评审后修订** (作者: Claude Opus 4.8, 会话 2026-07-06; 评审: 4 镜头对抗 agent + 首席终裁, 见 §10)。v1 判 `needs_revision`: 核心算法与 §9 字节等价论证实证严密, 但内存机理主张倒置 + 4 处 gate 自相矛盾, 均已在 v2 修订。
> 权威基线: `main=1e310b0c`; 行号 = HEAD 口径 (脏树并发产物与本模块无交叠)。
> 触发: 项目说明书 8-agent 缺陷审计确认 boilerplate.py docstring L25-30 自陈的 code review 2026-06-20 P1「生产 T=19 单遍 `fit_transform` OOM」未兑现。
> ⚠ 本计划仅撰写与评审, **不含实施** (用户指令)。实施须另行批准。

---

## §0 目标与范围

### 问题陈述
`compute_boilerplate_ratios()` (boilerplate.py:83-168) 以**单遍全语料** `CountVectorizer(analyzer='char_wb', ngram_range=(4,6)).fit_transform(docs)` 一次性构建两个规模敏感结构：
- **驱动 1 — CSR 计数矩阵 X**: doc×ngram, `nnz ∝ 语料总 n-gram 出现数 ∝ N` (线性)。
- **驱动 2 — vocabulary dict**: `M(D) = 语料唯一 (4,6)-gram 数`, Heaps 亚线性 (∝ N^β, β≈0.5–0.8) 但随 N 持续增长。

二者**同时驻留**。T=19 生产 gated 子集 (stage-22 输入 = 21_tone_llms gated 子集, 10⁵–10⁶ 篇) 会 OOM。本机 T=2 (≈847 文级) 可行。

### 核心事实修正 (v1→v2, 评审 P1-A)
> **⚠ 内存机理**: 在生产 gated 量级 (10⁵–10⁶ 篇), **驱动 2 (vocab dict) 是 binding constraint, 驱动 1 (CSR) 是较小加项** —— 因绝大多数 (4,6)-gram 仅现于单文, `nnz ≈ O(M)` 与 vocab 同阶, 而 vocab 每 entry (str+int+dict slot) 的常数字节数远大于 CSR 每 nnz (int32 data+int32 index)。∴ 仅"分块不物化全量 CSR"**不足以**根治 OOM; 真正撑爆内存的 vocab/DF 词表必须**另行**从 RAM 移除。本计划据此设**两层 exact 解法** (§2.2), 二者**均字节等价**, 选层由 §3-P0 实测外推裁定。

### 目标
将 `compute_boilerplate_ratios` 内部改造为 **golden 字节安全的 exact two-pass**, 分两层控内存, 且输出与单遍逐字节一致 (零 golden 重生):
- **Tier 1 — chunked 内存路径**: 分块流式, 消除**驱动 1 (全量 CSR)** 的瞬时物化; vocab/DF 仍以 `global_df` dict 驻留 RAM。**适用条件**: P0 外推证实 `global_df` 落 128GB 预算内。
- **Tier 2 — disk-backed 精确 DF**: 全局 DF 累加落盘 (外部归并 / SQLite / LMDB), 消除**驱动 2 (vocab dict)** 的 RAM 驻留。**适用条件**: P0 外推显示 `global_df` 超预算或落跨预算区间 → **生产 P0 裁定后必做** (非可选; ⚠ "生产首版实施"时间轴, 与计划修订版本 v1/v2/v3 无关, 本 dev 会话 DEFERRED)。
- 二者共享同一 Pass-2 (逐块用固定小 `boiler_set` 词表算命中率, 内存恒有界)。

### 本次实施范围 (v3 定案, tier1-only + fail-loud 硬闸)
> **⚠ 诚实定位 (Round1 P1)**: 本会话在 dev (T=2, ~847 文) 只实施 **tier 1 (chunked 内存, 字节等价)**; **tier 2 (disk-backed) DEFERRED** —— 其必要性与字节等价须靠**生产 T=19 的 P0 外推**裁定, 本机无生产语料无从验证。∴ **tier1-only 交付 = 消除 CSR 驱动 (较小的非 binding 项) + 建立分块两遍骨架 + 全部 P2 硬化**, **不等于"生产 OOM 已解决"** —— vocab/`global_df` (binding 项) 的生产可产性仍 gated on tier2。
> **无悔性**: tier 1 字节等价 → golden 零漂移 → dev 可验; 是 tier 2 的必备前置结构 (二者共享 Pass-2 与 boiler_set 契约)。
> **fail-loud 硬闸 (替代缺失的运行时兜底, Round1 P1)**: tier1-only 下必须有运行期硬天花板 —— `global_df` 超 `df_dict_budget_hard` → `SystemExit(1)` (镜像 stage13 `keep<min_keep_frac` 先例, **拒绝跑优于被 OOM-killer 静默 SIGKILL**); `memory_tier=disk` 或 `auto` 解析到需 disk → `raise SystemExit` (Final-A P2: 用 `SystemExit`⊂BaseException 穿透调用方 `except Exception`, 非 `NotImplementedError`⊂Exception 会被吞), **绝不静默回落 tier1 跑到 OOM** (§2.2/§2.3)。

### 范围
| 改 | 不改 |
|---|---|
| `compute_boilerplate_ratios` **内部算法** (单遍 → exact two-pass, tier 1/2) | `enrich_with_boilerplate` API、`(text_col,out_col)` 形参对、三轨槽循环 (L201-218) |
| `_MAX_SAFE_DOCS` 守卫 + **其 banner 引用 L193-197** (§2.4, 评审 P1-B) | `_clean` 退化守卫 (L64-80, 保值铁律逐字节) |
| 新增 `config/sentiment.yaml::boilerplate` 段 + 接线机制 (§2.3) | 测度定义 / `DF_RATIO_THRESHOLD=0.10` / `NGRAM_RANGE=(4,6)` / `OUT_COL` / 列名 |
| 构念效度 top-k/DF 谱日志的**数据来源** (改从 global_df; **集合等价非逐序**, §2.5) | 三轨铁律、非嵌入 carve-out、SAFE 四态语义、round(,6) |

### 不在范围 (§7)
改测度/阈值/n-gram range；任何**近似**算法 (§6 拒斥)；其它 char_wb 模块 (herd_decay 已分桶)；benefit/surface_staleness；chunk 级并行化 (§7 正交项)。

---

## §1 现状事实基础 (实读核实, boilerplate.py @ main=1e310b0c)

1. **算法三步**: L89-96 `_clean`+过滤 → L112-114 `X=vec.fit_transform(docs)` (单遍全语料, 峰值双驱动) → L119-121 第一遍 `df_counts=(X>0).sum(0)`, `boiler_mask=(df_counts/n_docs)≥阈值` → L163-167 第二遍 `total=X.sum(1)`, `boiler=X[:,boiler_mask].sum(1)`, `out[i]=round(boiler/total,6) if total>0 else nan`。
2. **确定性** (L20,L128): CountVectorizer 固定参数 + sklearn vocab 字面排序 → 无 HASHSEED; round(,6)。⚠ 默认 `lowercase=True` —— 逐文档操作, 与语料无关 (§9 不变量 II)。⚠ **默认 `min_df=1, max_df=1.0, max_features=None`** —— **字节等价的隐性硬前提** (评审 P2, §2.6): 任一改为语料级剪枝即破不变量。
3. **SAFE 降级四态** (须逐字保留, 且**态 (a)(c)(d) 可达、态 (b) 在 `_clean`≥4 实字下不可达 = 既有死分支**, 本会话亲测证实): (a) 全空/哨兵→全 nan (L92-94); (b) CountVectorizer 空词表 ValueError→全 nan (L115-117, **死分支**); (c) 套话集空 `n_boiler==0`→全 nan+WARNING (L123-127); (d) 小语料饱和 `n_docs<⌈1/阈值⌉`→比率≈1.0 WARNING (L106-111, 不改值)。`_clean` 退化守卫 (L64-80): 剔零宽+空白后实字<`_MIN_REAL_CHARS=4`→`''`→nan; 非退化返回 `text.strip()` 逐字节同旧版。**⚠ 态 (b) 不可达机制 (本会话实测, 订正 Round1 误判)**: char_wb 对短于 `min_n` 的词会把整个 padded 短词 emit 一次 (如 `中 国 银 行`→feature `{' 中 ',' 国 ',' 银 ',' 行 '}`, total=4, **非空**), 故凡过 `_clean` (≥4 实字 ⇒ `.split()` ≥1 词) 的文档必产 ≥1 gram; 唯有 0 词 (空/纯空白, 已被 `_clean` 滤除) 才空词表。∴ Round1"`中 国 银 行` 零 gram 致 reachable 崩溃"事实错误; 但 §2.1 的 `np.zeros`+显式 except 仍作零成本防御保留 (belt-and-suspenders)。
4. **构念效度日志块** (L134-161, log-only/discarded): top-10 高 DF 套话短语 (`feats=get_feature_names_out()`+`df_counts`, **L144 用 `np.argsort(df_counts[masked_pos])[::-1]` = 非稳定 quicksort, 并列内序非字典序**) + DF 占比谱 [min/中位/max]。不进面板/golden。
5. **调用链**: `tone_words.py:2340-2343` → `enrich_with_boilerplate(processed_df, text_col=_bp_col)` (stage 22 子步骤); 三轨槽 (L201-218) **逐轨顺序**调用 `compute_boilerplate_ratios`, 词表不叠加 → 峰值 = 单轨峰值。
6. **`_MAX_SAFE_DOCS=50_000`** (L57): L100-105 守卫 warn + **L193-197 子步骤 banner 硬引用两处** (`'单遍安全规模上界 _MAX_SAFE_DOCS=%s'` 格式串 + `f"{_MAX_SAFE_DOCS:,d}"` 实参) —— **改名/删除须同步此 banner, 否则 NameError** (评审 P1-B)。
7. **config**: boilerplate **无独立 config 段**; 函数签名 `(texts, df_ratio_threshold, ngram_range)` **无 config 形参**, 模块**不 import config** (评审 P2, §2.3 须定接线)。
8. **golden 覆盖 (评审核实, v1→v2 订正)**: `tests/fixtures/golden_panel_v0.json` **含 `boilerplate_phrase_ratio_full` 且列哈希 = `a5667be2b3fce425` (本列独有、非全 nan 哨兵), full 轨受真实保护**; 但 **`_ctx`/`_ss` 两轨未落入 fixture** (golden 系三轨化前旧快照)。∴ golden 仅护 full 轨; ctx/ss 保护**完全依赖** §4-1 单元字节等价 gate + §3-P5 dev A/B (强制门槛)。

---

## §2 设计决策

### §2.1 核心算法: exact two-pass (字节等价; 三遍分词优化为两遍, 评审 P2)

**签名契约 (Round1 P2, 消歧)**: `compute_boilerplate_ratios(texts, df_ratio_threshold=DF_RATIO_THRESHOLD, ngram_range=NGRAM_RANGE, *, chunk_size=_DEFAULT_CHUNK_SIZE, memory_tier=_DEFAULT_TIER, df_dict_budget_warn=_DEFAULT_BUDGET_WARN, df_dict_budget_hard=_DEFAULT_BUDGET_HARD)`; kwargs-only 新参默认 = 模块常量 (= config 样例默认值); enrich 三轨 slot **各自穿透**这些 kwargs (§2.3)。`chunks_with_index(docs, chunk_size)` **契约**: 产 `(chunk_rows, idx)`, `idx = np.arange(start, stop)` 是该块文档在**去空后语料 docs 中的全局位置**, 且 `chunk_rows[k] == docs[idx[k]]` 同序 (`per_doc_total` 尺寸 = `len(docs)` 按全局位置寻址, 非块内局部序)。

**Pass 1 — 流式精确全局 DF + 顺带存逐文 total** (tier 1 内存版; tier 2 见 §2.2):
```
N = len(docs)
global_df: dict[str,int] = {}                 # n-gram 字面(含 char_wb 边界空格) → 全局文档频率
per_doc_total = np.zeros(N, float)            # 逐文全 n-gram 出现数; np.zeros(非 empty): 未写入位=fail-safe 0→nan, 非垃圾值 (Round1 P1)
for chunk, idx in chunks_with_index(docs, chunk_size):   # idx = 全局位置 np.arange(start,stop)
    vec_c = _make_vectorizer(ngram_range=ngram_range)     # §2.6 工厂: 穿透 ngram_range 防死参; min_df/max_df/max_features 断言
    try:
        Xc = vec_c.fit_transform(chunk)       # 块内矩阵 (即弃)
    except ValueError:                        # 空词表块 (整块 0 gram); _clean≥4 下不可达=死分支 (§9), 仍显式防御
        per_doc_total[idx] = 0.0              # → 逐文 total=0 → nan (死分支零成本防御; 若假设性可达, 仅置本块 nan)
        continue
    feats = vec_c.get_feature_names_out()
    df_c = np.asarray((Xc>0).sum(0)).ravel()
    for j, ng in enumerate(feats):
        global_df[ng] = global_df.get(ng, 0) + int(df_c[j])
    per_doc_total[idx] = np.asarray(Xc.sum(1)).ravel()   # 不变量 II: 块内行和 = 单遍行和
    if len(global_df) > df_dict_budget_hard:  # ⚠ 运行期硬闸 IN-LOOP (Round2 P1): RAM 耗尽前抢先 fail-loud, 防 OOM-killer 静默 SIGKILL
        raise SystemExit(f"boilerplate: global_df {len(global_df)} entry 超硬上限 {df_dict_budget_hard}; "
                         f"tier1 不可产, 到生产机跑 §3-P0 外推裁定 tier2 (DEFERRED)")
boiler_set = [ng for ng, d in global_df.items() if d/N >= threshold]   # 精确套话集; 若空或 global_df 空 → SAFE 态 c 短路全 nan
```
**Pass 2 — 流式逐文命中 (仅一次向量化, 固定小词表)**:
```
vec_boiler = _make_vectorizer(ngram_range=ngram_range, vocabulary=sorted(boiler_set))    # 固定 boiler 词表; sorted 消除 dict 序依赖
for chunk, idx in chunks_with_index(docs, chunk_size):
    boiler_c = np.asarray(vec_boiler.transform(chunk).sum(1)).ravel().astype(float)   # 逐文套话数
    for k, i in enumerate(idx):
        t = per_doc_total[i]
        out[nonempty_idx[i]] = round(boiler_c[k]/t, 6) if t > 0 else float('nan')
```
- **分词遍数**: Pass1 一遍 (产 DF + total) + Pass2 一遍 (产分子) = **2 遍** (v1 的 3 遍已优化, 评审 P2)。CPU ≈ 单遍的 ~2× (§5 披露)。
- **每块 fit_transform 加 try/except ValueError** (评审 P2 零成本防御): 空词表块 → 该块对 global_df 贡献 0、`per_doc_total[idx]=0` (→逐文 nan)。⚠ **措辞收紧 (Round2 P2)**: 这是**死分支的零成本字面防御** (单遍/chunked 在 `_clean`≥4 下均不可达); 非"精确复现单遍整语料 nan"——单遍空词表返回**整语料全 nan**, chunked 空块仅置**该块** nan。功能无害 (不可达), 保留作 belt-and-suspenders。

**峰值内存 (tier 1)**: `max(sizeof(global_df) + per_doc_total(8B×N), 单块矩阵)`。单块矩阵由 `chunk_size` 控 (与 N 解耦); **`global_df` 仍随 M(D) 增长, 是 binding** (§2.2)。

### §2.2 内存两层与规模裁定 (评审 P1-A 核心修订)

**口径矛盾调和 (评审 P1-A/gate)**: docstring L26 记「847 文→2.4M n-gram≈231MB」(疑含 CSR 或用 `sys.getsizeof(dict)` 只算哈希表 ~96B/entry); §2.2-v1 记「global_df 单独 480MB」(200B/entry) —— 二者差 2× 且 dict 不可能大于全量, **v1 估算不可信**。→ **P0 必做**: 用 `psutil` 进程 RSS delta 或 `resource.getrusage(RU_MAXRSS)` **分别实测** (i) 单遍 vocab dict、(ii) 单遍 CSR (nnz×字节)、(iii) tier-1 峰值三项, 拆开而非合并, 校准真实 per-entry 字节数与哪项主导。

**规模外推 (评审 P1-A, 禁假阴)**: dev 拟合 M(D) 外推 T=19:
- ⚠ **禁重采样/复制式放大** (重复文档不带新 n-gram → vocab 饱和 → M(D) 严重低估 → OOM 假阴乐观); 须用**生产语料真实互异子样** (或按 vocab 增长率而非文档数拟合)。
- 放大点覆盖 ≥ 200k 篇或近生产量级 (勿在 β 不定的幂律上外推 1–2 量级)。
- 以 **β=0.7 与 β=0.8 双假设**给预算区间 (示意: β=0.7→全语料 M≈2×10⁸→~20–40GB; β=0.8→~7×10⁸→~70–140GB, 恰跨 128GB 两侧)。

**裁定规则 (P0 硬放行门槛)**:
| P0 外推结论 | v1 实施路径 |
|---|---|
| `global_df` 稳落预算内 (含安全余量) | **tier 1** (chunked 内存) 足够 |
| 超预算, 或落 [~40GB, ~140GB] **跨预算区间** | **tier 2** (disk-backed 精确 DF) **生产首版必做** (本 dev 会话 DEFERRED), 不赌乐观外推 |

**Tier 2 最小设计 (disk-backed 精确 DF, 仍字节等价)**:
- **累加**: Pass1 逐块产 (ngram, block_df) 对, 落**外部归并计数** (sort-merge: 各块 DF 写临时文件 → 外部归并按 ngram 合并求和 → 得精确全局 DF) 或 **LMDB/SQLite 批量 upsert** (ngram→累加 DF)。二者均产**精确** global_df (与 tier 1 逐 n-gram 相等) → boiler_set 同集 → 字节等价。
- **boiler_set 提取**: 归并/查询出 `d/N≥threshold` 的 n-gram → 载入 RAM (boiler_set 小, 有界)。
- **吞吐量估算 (P0 须证可行)**: 10⁸ 量级 n-gram 的外部排序/upsert wall-clock (sort-merge 通常远快于逐条 upsert); 若 disk I/O 使总耗时不可接受 → 触发 §6 才重议近似 (须显式 golden 重生)。
- ⚠ **禁 HashingVectorizer / sketch 求 DF** (碰撞/近似破 exact, §6)。

**两级预算的定位 (Round1 P1 强化)**:
- `df_dict_budget_warn` (软, 默认 8M entry): 仅 `loud WARNING` 提示 global_df 逼近预算, **不改路径不是兜底**。
- **`df_dict_budget_hard` (硬, 新增)**: **Pass1 逐块循环内周期检查** (Round2 P1, 每块累加后 `len(global_df) > df_dict_budget_hard` → **`SystemExit(<可操作信息>)`**, 见 §2.1 伪码) —— **必须 in-loop**: 若放循环后, 生产 global_df 在累加中途撑爆 RAM 会被 OOM-killer 先 SIGKILL, 永远到不了检查点; in-loop 才能在 RAM 耗尽前抢先 fail-loud (镜像 stage13 `keep<min_keep_frac→SystemExit(1)` 先例)。**这是 tier1-only 唯一的运行期兜底 —— 拒绝跑优于被 OOM-killer 静默 SIGKILL**。真正的规模解法仍是 P0 事前裁定 tier 2 (DEFERRED)。⚠ **默认值 (Round2 P2)**: 样例 40M entry 为**保守占位**; 真实上限须 P0 实测 per-entry 字节数 (§2.2 口径调和, 当前不可信) 后按 128GB 安全分数反推校准 (config 可覆盖) —— **勿**将 40M 当作已由 128GB 反推的既成值。

**hopeless-pruning (opt-in, 默认关, 评审 P2)**: 仅在 tier 1 且 global_df 逼近预算时启用瘦身; ⚠ **安全判据 (Round1 P2, 防漏剪)**: 只有 `d_cur + N_remaining < cutoff` (即使后续未处理文档全命中也**无望**达标) 才可剪, **禁**单看 `d_cur < cutoff` (某 n-gram 可能在靠后块才跨阈值, 早剪则漏出 boiler_set → 分子发散)。`cutoff = 最小满足 d/N≥threshold 的整数 d` (与主判据**同构整数 cutoff**, 一次算好复用, 避免 `⌈threshold·N⌉` 浮点乘 vs `d/N≥threshold` 浮点除的 IEEE754 边界不一致)。**仅降累积 dict 冗余、不降峰值** (峰值控靠 tier 2 / hard 闸)。启用须过 §4-6 gate (含"某 n-gram 靠后块才跨阈值"用例)。

### §2.3 config 新增 + 接线机制 (Round1 P1 修复: 扁平根键 + fail-loud 契约)

⚠ **接线纠错 (Round1 P1, 实读 core/config.py + load_config() 核实)**: `load_config()` 把 7 域 YAML **`_deep_merge` 成扁平根 dict, 域文件名 (`sentiment`) 不是嵌套键**。实测: `'sentiment' in load_config()` = **False** (会 KeyError!); `'sentiment_analysis'` = True (子键 enabled_methods/tone_words/tone_berts); 全仓一致用 `config.get('sentiment_analysis', {})` (config.py:538)。∴ v2 的 `load_config()['sentiment']['boilerplate']` **键名+层级双错**, 照写必 KeyError 崩 stage22 (enrich 的 try/except 只包 banner/结果分析, 不包 slot 循环前的 config 读取)。**修法**: `boilerplate` 作 sentiment.yaml **顶层块** (deep-merge 后即根键; schemas_yaml 仅校验 3 域, 新顶层键 schema-safe), 读 **`load_config().get('boilerplate', {})`**。

```yaml
# config/sentiment.yaml —— 顶层块 (0 缩进, deep-merge 后 = 根键 'boilerplate')
boilerplate:
  memory_tier: in_memory       # in_memory=tier1(唯一已实现); single_pass=legacy 单遍(§4-1 参照臂); disk/auto=NOT-YET-IMPLEMENTED→raise
  chunk_size: 20000            # 每块文档数; 纯性能参数, 不改输出 (§4-2 gate 锁)
  df_dict_budget_warn: 8000000 # global_df entry 软预算, 超则 loud WARNING (非兜底)
  df_dict_budget_hard: 40000000 # global_df entry 硬上限, 超则 SystemExit (§2.1 IN-LOOP); ⚠ 40M=保守占位, P0 实测 per-entry 字节后按 128GB 反推校准
```
- **接线**: `enrich_with_boilerplate` 读 **`load_config().get('boilerplate', {})`** (缺段→`{}`→全走模块常量默认), 作为 kwargs-only 参数下传 `compute_boilerplate_ratios` (签名见 §2.1)。**三轨 slot 循环三次调用各自穿透**。`compute_boilerplate_ratios` **保持无 config import** → `test_boilerplate*` 零 config 直调走默认。
- **clamp 执行位置 (Round2 P2)**: clamp 在 **`compute_boilerplate_ratios` 入口** (靠近 `chunks_with_index` 处) 执行, 使 **enrich 注入与直调两条路径都受保护** —— 否则 gate/测试直调 `compute(chunk_size=0)` 会 `chunks_with_index(docs,0)` 死循环/除零。§4-2/§4-9 覆盖直调畸值。
- **memory_tier dispatch (Round1 P1, tier1-only 契约)**:
  - `in_memory` → tier 1 (§2.1)。
  - `single_pass` → 保留的 legacy 单遍旧码 (§4-1 字节等价参照臂; **只要 gate 存在即禁删**)。
  - **`disk` / `auto`** → **`raise SystemExit('tier2 disk-backed DF DEFERRED 未实现; 请设 in_memory, 或到生产机跑 P0 外推后启用 tier2')`** (⚠ Final-A P2: 用 `SystemExit`⊂BaseException **非** `NotImplementedError`⊂Exception —— 调用方 tone_words `except Exception` graceful-skip 会吞后者致**静默丢 boilerplate 三轨列**, SystemExit 穿透硬停, 与 hard 闸统一 fail-loud) —— 绝不静默回落 tier1 跑到 OOM。是**已知但未实现值**, 纳入 dispatch 分支 (区别于"未知值→默认")。
- **畸值 clamp**: `chunk_size=max(1,int(chunk_size))`; `df_dict_budget_warn/hard` 非正→禁用对应闸; **未知** `memory_tier` (非上述四值) → `in_memory` + loud WARNING。
- `chunk_size`/`memory_tier(in_memory vs single_pass)` **均不改输出** (同 exact DF; chunk 划分与不变量正交) → §4-1/§4-2 gate 锁。

### §2.4 `_MAX_SAFE_DOCS` 守卫改造 (评审 P1-B, banner 同步)
- L100-105 单遍规模上界 warn → `global_df` entry 数逼近 `df_dict_budget_warn` 的 loud WARNING。
- **⚠ 同步 diff 清单 (P3 必含, 否则 NameError)**: `enrich_with_boilerplate` banner **L195 格式串**「单遍安全规模上界 `_MAX_SAFE_DOCS`=%s」→「`global_df` 预算上界=%s」+ **L197 实参** `f"{_MAX_SAFE_DOCS:,d}"` → 改指 `df_dict_budget_warn` (虽 banner 有 try/except 吞 NameError 成 WARNING, 但语义错+日志误导, 必须一并改)。
- 保 loud 语义, 不改返回值。
- **⚠ `_MAX_SAFE_DOCS` 常量保留 (Round2 P2, 防 legacy 臂 NameError)**: §2.3 的 `memory_tier=single_pass` legacy 参照臂沿用旧单遍代码, 其 L100-105 引用 `_MAX_SAFE_DOCS`。∴ **常量本身保留** (仅由 legacy 臂消费, 不再是 tier1 主守卫); tier1 路径与 banner 改用 `df_dict_budget_warn/hard`。**legacy 臂落地方式二选一并写死**: (a) 函数内 `if memory_tier=='single_pass':` 分支保留旧码; 或 (b) 整体快照进 `_compute_single_pass_legacy()` helper (内部符号含 `_MAX_SAFE_DOCS` 冻结)。推荐 (b) 隔离更干净。
- **披露卫生 (收口验证补 + Round2 P2)**: 模块 **docstring L25-30 / 常量注释 L56** 须随改造刷新: ① `_MAX_SAFE_DOCS` 措辞更新为"legacy 单遍臂守卫"; ② **删除/改写 docstring L27-30 推荐的 "HashingVectorizer/min_df 求套话集 → CountVectorizer(vocabulary=)" 与 "分块/限词表二遍" 旧修法** —— 该建议与本计划 §2.1 exact two-pass (精确 DF, 非 min_df/Hashing) + §6 拒斥表 (HashingVectorizer 碰撞破 golden) **自相矛盾**, 须订正为 exact two-pass 口径, 避免遗留已否决方法的误导披露。

### §2.5 三轨 / SAFE / 构念效度日志 (评审 P1-D, top-k 集合等价)
- 三轨槽循环 (L201-218) 不动; 逐轨独立建 global_df/boiler_set (峰值=单轨)。
- SAFE 四态 + `_clean` + banner/结果分析/方法论 log 块全保留。
- **构念效度 top-k/DF 谱 (L134-161) 从 global_df 复现, 但仅要求集合等价, 非逐序** (评审 P1-D): 单遍 L144 用 `np.argsort(...)[::-1]` (非稳定 quicksort, 并列内序非字典序), chunked 无法用 `sorted(-df,ngram)` 复现其 tie 序。∴ **该 log-only 块降为集合语义**: top-k **短语集合**由 global_df 取 DF 最高 k 个 (tie 任意但确定); **DF 谱 [min/中位/max] 数值精确等** (由不变量 I, order-independent)。§8 陷阱-2 相应订正 (放弃逐序承诺)。

### §2.6 vectorizer 工厂 + 剪枝参数断言 (评审 P2, 字节等价命门)
- 新增 `_make_vectorizer(ngram_range=NGRAM_RANGE, vocabulary=None)` 单一工厂, Pass1/Pass2 共用, **显式** `analyzer='char_wb', lowercase=True` + **穿透 `ngram_range` 形参** (Round1 P2: compute 的 public `ngram_range` 参数须传入工厂, 否则工厂硬编码常量 → 该 public 参数变**静默死参**, 与单遍 L113 用形参的行为发散)。
- **类型感知断言 (Round1 P2, 防 int/float 混淆逃逸)**: `assert type(min_df) is int and min_df == 1` (int-1=无剪枝 vs float-1.0=100%剪枝, 但 `1==1.0` 为 True 会放行错值); `assert isinstance(max_df, float) and max_df == 1.0 and not isinstance(max_df, bool)`; `assert max_features is None`。违反 raise。因工厂内部硬编码这些值, assert 主防**未来有人改写工厂**引入语料级剪枝。
- 理由: 不变量 I/II **仅**在无语料级剪枝 (min_df/max_df/max_features 默认) 时成立; 任一侧加剪枝会使单遍扣全局剪枝 n-gram 计数、分块因块成分不同剪枝不同 → total/DF 静默发散、golden 悄漂。工厂+assert 把隐性前提转为运行时硬约束。§4-7 gate 锁定 (含 int-1 vs float-1.0 混淆用例)。

---

## §3 实施步骤 (Phase; 本计划仅规划)

| Phase | 内容 | 门槛 |
|---|---|---|
| **P0** 基线+内存裁定 | main 后取 HEAD; dev 单遍存三轨输出快照 (A 基线); **分项实测** (RSS/getrusage) vocab dict / CSR / tier1 峰值三项调和口径矛盾; **真实互异子样**放大拟合 M(D) (禁重采样), ≥200k 覆盖, β=0.7/0.8 双假设定预算区间; 核 golden fixture boilerplate 三轨覆盖态 | **硬放行门**: 外推超/跨预算 → tier 2 v1 必做 (§2.2 裁定表); 出 M(D) 外推表 + 分项内存表 |
| **P1** 核心改造 | `compute_boilerplate_ratios` → exact two-pass (§2.1); tier 1 内存版 + (若 P0 裁定) tier 2 disk 版; 工厂+assert (§2.6); per-doc total 在 Pass1 存 | 单元字节等价 gate 绿 |
| **P2** config 接线 | `boilerplate` 段 + `enrich` 读 config 下传 kwargs (§2.3); clamp | 缺段/畸值 graceful gate 绿 |
| **P3** 守卫+banner | `_MAX_SAFE_DOCS`→`df_dict_budget_warn` + **L193-197 banner 同步** (§2.4) | banner 无 NameError; 超预算 loud warn |
| **P4** gate 测试 | §4 十项 | 全绿 |
| **P5** 回归 | 全量 pytest + golden 复现 (**full 轨 UNCHANGED**) + **dev A/B**: `memory_tier=single_pass` (legacy 参照臂 A) vs `in_memory` (B) 三轨逐字节等 ⚠ **须传小 `chunk_size` (如 50–100)** 令 T=2 (~847 文) 真实 ctx/ss 文本**跨多块** (默认 20000 落单块 = 零多块覆盖, ctx/ss 无 fixture 唯靠此保护) | 0 新增失败; golden 零漂移; ctx/ss 多块 A/B 字节等 |

---

## §4 Gate 测试 (tests/test_boilerplate_chunked.py)

1. **test_chunked_equals_singlepass**: 合成语料 (含达阈值套话/退化文本/`_clean`过滤/total 非平凡分布/**过 `_clean` 但空格分隔单字 token 文档**与正常文档**跨 chunk 边界交错**), `memory_tier=single_pass` (legacy 参照臂) vs `in_memory` 输出**逐元素相等含 NaN 位置** (`assert_array_equal` NaN-aware); 且断言 `chunks_with_index` idx=全局位置 (多块划分下 out 回填 texts 正确)。
2. **test_chunk_size_invariance**: `chunk_size∈{1,7,N-1,N,2N}` 输出恒同 (证纯性能参数; 小 chunk_size 令退化文档单独成块验 except/zeros 路径)。
3. **test_tier_equivalence** (若 P0 裁定 tier 2): tier 1 内存 vs tier 2 disk 输出**逐字节等** (二者同 exact DF)。
4. **test_memory_structural_invariant** (评审 P1-C, 替换 tracemalloc): **monkeypatch/spy `CountVectorizer.fit_transform`, 断言每次收到文档数 ≤ chunk_size** (结构不变量, 确定性无 CI 抖动, 直证"从不物化全量 CSR")。**删除** v1 的「chunk_size 减半→峰值近半」断言 (与 global_df 主导矛盾)。可选: `resource.getrusage(RU_MAXRSS)` 观 C 层分配辅证 (非主 gate, 防 tracemalloc 测不到 numpy 缓冲)。
5. **test_safe_degradation_preserved**: 态 (a)(c)(d) 可达 + `_clean` 退化 → nan/warning 逐字节同单遍; **态 (b) 注明需 monkeypatch `_clean` 才可构造** (`_clean`≥4 下死分支), 测 chunked 加的 try/except 复现全 nan。
6. **test_pruning_output_invariance** (评审 P2): hopeless-pruning on/off 输出逐字节等 (含 `threshold·N` 恰为整数的边界语料); v1 默认 off 则加"启用即测"占位。
7. **test_vectorizer_params_locked** (评审 P2, §2.6): 断言 `_make_vectorizer` 产物**类型感知** `type(min_df) is int and min_df==1` / `isinstance(max_df,float) and max_df==1.0 and not bool` / `max_features is None`; **含 int-1 vs float-1.0 混淆用例** (篡改工厂引入 min_df=1.0 须 raise); `ngram_range` 形参穿透工厂。
8. **test_construct_log_set_equivalence** (评审 P1-D): chunked top-k **短语集合** == 单遍集合 + DF 谱 [min/中位/max] **数值精确等** (不比逐序)。⚠ 合成语料须构造 **top-k DF 互异 (第 k/k+1 名无并列)**, 否则单遍 quicksort 与 chunked 各自任意 tie-break 在 k-边界可能选出不等集合致假红; 或改比 **DF 多重集** (order+tie 无关)。
9. **test_config_wiring** (Round1 P1, 真穿透断言): ① 设**非默认** `boilerplate: {chunk_size: 7}` (顶层块) 经 `enrich` → monkeypatch/spy 观测 `compute_boilerplate_ratios` **真收到 chunk_size=7** (防 KeyError 崩 / `.get` 静默死接线两种发散); ② 缺 `boilerplate` 段→走默认常量; ③ 畸值 (`chunk_size≤0`/未知 tier) → clamp graceful; ④ `compute_boilerplate_ratios` 零 config 直调走默认。
10. **test_disk_tier_fail_loud** (Round1 P1 + Round2 P1 + Final-A P2): `memory_tier='disk'` 及 `'auto'` → `raise SystemExit` (tier2 DEFERRED, ⊂BaseException 穿透调用方 `except Exception` 硬停, 绝不静默回落 tier1/丢列); `len(global_df)>df_dict_budget_hard` (monkeypatch 小硬上限) → `SystemExit` **且携带非空可操作消息**; ⚠ **断言硬闸 in-loop 语义** (Round2 P1): 注入多块序列使 global_df 在**第 2 块**即越限, 验证在 Pass1 **累加未结束时**即 raise (证明非 post-loop, 防生产 RAM 撑爆前抢先 fail-loud)。
- **既有 gate**: `test_panel_reproducibility` (**full 轨列哈希 `a5667be2b3fce425` UNCHANGED**; ctx/ss 不在 fixture, 见 §1.8); `test_dag_consistency`; 全量 pytest 不新增失败。

---

## §5 Golden / 生产 / 成本 影响

- **Golden: 零漂移** (字节等价)。full 轨 fixture 列哈希不变 (§1.8); **ctx/ss 无 fixture 覆盖, 保护 = §4-1 单元字节等价 + P5 dev A/B 小 chunk_size 多块 (强制)**。tier 1/2 均 exact → 无论走哪层 golden 皆不变。
- **生产 T=19 (Round1 P1 收紧, 诚实)**: tier1-only 交付**仅**消除 CSR 驱动 (较小的非 binding 项, dev 实测占峰值 ~5% 量级待 P0 校准) + 建骨架 + 运行期 hard 闸 (超预算 `SystemExit(1)` 而非 OOM-killer 静默 SIGKILL)。**vocab-binding 生产可产性仍 gated on tier2 (DEFERRED)** —— 只有 P0 外推证实 global_df 落预算内 (走 tier1) 或补齐 tier2 后, 原本 OOM 产不出的列才真变可产。**不表述为"OOM 已修完"**。
- **CPU 时间 (评审 P2 披露)**: exact two-pass 分词 **2 遍** (Pass1 DF+total, Pass2 分子), 约单遍的 **~2×**; char_wb (4,6) 分词是 CPU 热点, 生产 10⁵–10⁶ 篇下须 P0 用 dev wall-clock 外推、评估是否值得 §7 并行化。tier 2 另加 disk I/O (外部归并), P0 须证吞吐可接受。
- ⚠ **披露**: tier 2 亦 exact/golden-safe; manuscript/codebook 口径不变 (测度定义未动)。

---

## §6 拒斥备选
| 备选 | 拒斥理由 |
|---|---|
| HashingVectorizer 求 DF | 哈希碰撞→DF 虚高→套话集变→**破字节等价/golden** |
| frequent-items sketch (Misra-Gries/Space-Saving/Count-Min) | 近似 heavy-hitters→套话集增删→破 exact (内存 O(1/ε) 虽省但违 golden 铁律; 仅 tier 2 disk 也不可行的极端规模才重议, 须显式 golden 重生+稳定性验证) |
| 全局 min_df/max_df 预剪 / 块内剪枝 | 全局阈值无法块内安全预剪 (块内稀有但全局常见 n-gram 被误删→套话集错, 同 §2.6) |
| per-chunk 独立算比率再平均 | 套话集是语料级构念, 分块独立→块级套话集→语义错 |
| 仅抬高 `_MAX_SAFE_DOCS` | 不解根因 (两驱动仍 OOM), 只推迟崩溃 |

---

## §7 刻意不做
改测度/阈值/列名/三轨口径; 近似化 (§6); 其它 char_wb 模块/benefit/surface_staleness; chunk 级并行化 (正交优化, 须防 BLAS/顺序非确定, 另议)。

---

## §8 已知陷阱 (实施须逐条防)
1. **char_wb 边界空格** (评审证实关键): `boiler_set` 必须是 Pass1 `get_feature_names_out()` **原样 feature-name 串** (两端含 padding 空格, 实测如 `' 有限公'`); 手工切 n-gram 传 `vocabulary=` 会零命中→分子恒 0。
2. **构念日志 top-k = 集合语义, 非逐序** (评审 P1-D 订正): 单遍 `np.argsort(...)[::-1]` 的 tie 序不可用 `sorted(-df,ngram)` 复现; §2.5/§4-8 只要求集合等价 + DF 谱数值等。**放弃 v1 的逐序对齐承诺**。
3. **确定性**: 整数计数 + `sorted()` 传 vocabulary 消除 dict 序依赖 + round(,6); 无 BLAS/HASHSEED。
4. **chunk 边界 off-by-one**: `idx→nonempty_idx[idx]→原 texts` 回填正确 (§4-1 非平凡 nan 分布捕获)。
5. **末块不满 / N<chunk_size 单块退化**: 等价单遍 (§4-2 覆盖)。
6. **boiler_set 空 (态 c) 与 global_df 空**: 建 `vec_boiler` **前**短路全 nan (评审补: global_df 空亦归态 c, 非仅 boiler_set 空)。
7. **空词表块 (评审 P2 补)**: Pass1/Pass2 逐块 `fit_transform` 加 try/except ValueError, 空块贡献 0 + `per_doc_total=0`; 使 `_clean`≥4 下不可达的态 (b) 亦有字面防御, 不因子块空而崩 (保 chunk_size 不变性)。
8. **int32 溢出 (评审 integration 补)**: 百万篇下逐文 `total`/`boiler` 求和用 **float 或 int64** (sklearn CSR 默认 int64 计数; `per_doc_total` 存 float), 防 int32 累加溢出。
9. **vectorizer 剪枝参数 (评审 P2)**: §2.6 工厂 assert `min_df==1∧max_df==1.0∧max_features is None`; 是不变量 I/II 的唯一语料依赖命门。
10. **config import 耦合**: `compute_boilerplate_ratios` 不 import config (保测试零 config 直调), config 仅经 `enrich` 注入 kwargs (§2.3)。

---

## §9 字节等价形式化论证 (评审实证严密, 保留)

设已 `_clean` 过滤的语料 D={d₁,…,d_N}, 单遍产 r_i; exact two-pass (tier 1/2 同 DF) 以任意划分 D=⊔_c C_c (每文恰属一块) 产 r'_i。证 r'_i=r_i ∀i:
- **不变量 I (DF 可加性)**: df(g)=|{d∈D:g∈d}|; global_df[g]=Σ_c|{d∈C_c:g∈d}|=|{d∈D:g∈d}|=df(g) (划分每文恰计一次) ⟹ boiler_set=boiler_mask 同集。∎
- **不变量 II (total 逐文独立)**: char_wb (4,6)-gram 分词逐文档 (评审实测: grams 仅由本文档 padded 词产生, 与语料无关, 前提 `min_df=1∧max_df=1.0∧max_features=None` §2.6); total_i=Σ_{g∈d_i}count(g,d_i)=:T(d_i) 只依赖 d_i; 块内 `Xc.sum(1)[d_i]=Σ_{g∈d_i}count(g,d_i)` (d_i⊆C_c⟹d_i 的 n-gram⊆vocab(C_c))=T(d_i)。∎
- **不变量 III (分子同值)**: `vocabulary=boiler_set` 固定, b'_i=Σ_{g∈boiler_set}count(g,d_i); 由 I boiler_set=boiler_mask⟹b'_i=b_i。∎
- ∴ r'_i=round(b'_i/T(d_i),6)=r_i (含 total=0→nan 同分支)。□

**硬前提** (§2.6 assert + §4-7 gate 锁定): 每文恰属一块 (I); char_wb 逐文确定 (II); vocabulary=Pass1 feature-name 原样串 (III, §8-1); **`min_df=1∧max_df=1.0∧max_features=None`** (I/II 的唯一语料依赖命门)。评审四路交叉确认核心数学无懈可击; 两条"reachable 空词表崩溃"经终裁实测 REFUTED (`_clean`≥4⟹每文≥1 gram, 态 b 死分支)。

---

## §10 评审记录

**v1 四路对抗评审 (2026-07-06, 4 镜头 + 首席终裁; 24 findings 归并)**:
- **verdicts**: equivalence=sound_with_fixes, **memory=flawed**, gate=sound_with_fixes, integration=sound_with_fixes; **终裁=needs_revision** (核心算法/§9 论证严密, 但内存卖点过度主张 + 4 gate 自相矛盾)。
- **4 P1 必改 (v2 已全落实)**: ① 内存机理倒置 (global_df binding, chunked 只砍 CSR) → §0/§2.2 两层重构 + P0 硬放行门 + tier 2 升 v1-conditional-required + 口径矛盾调和 + 禁重采样外推; ② `_MAX_SAFE_DOCS` 改名 vs banner 冲突 NameError → §2.4 banner 同步清单; ③ tracemalloc 测不到 CSR + "减半近半"矛盾 → §4-4 改结构不变量 spy gate; ④ top-k tie-break sorted vs quicksort 必红 → §2.5/§4-8 集合等价。
- **P2 已采纳**: vectorizer 工厂+assert (§2.6); Pass2 冗余分词优化 3→2 遍 + CPU 2× 披露 (§2.1/§5); 态 (b) 契约措辞+try/except 防御 (§2.1/§4-5); golden 仅护 full 轨订正 (§1.8/§5); config 接线机制 (§2.3); int32 溢出 (§8-8); pruning/budget/config gate 补齐 (§4-6/9)。
- **终裁 REFUTED (未改)**: 两条"过 `_clean` 却零 4-gram 致块崩溃"经实测证伪 (`中 国 银 行`→4 gram/total=4); df_dict_budget_warn 运行期自动切 disk 属可选增强非硬性。
- **经证明严密 (增强信心)**: §9 三不变量 (char_wb 逐文实测)、§8-1 边界空格、§6 拒斥推理、确定性分析、四路交叉命中 top-k tie-break —— 均实证正确。

> **v2 状态: 4 P1 全修 + 7 P2 采纳, 核心算法经实证严密。判定 ready_to_implement (待用户批准实施)。** 建议实施前 P0 内存外推作为第一硬门槛。

**Round1 复审 (2026-07-06, 4 镜头[残余正确性/实施歧义/测试golden/范围安全] + 首席终裁; 19 findings, 均 ready_with_fixes; 终裁=needs_minor_fix, tier1-only 范围正当=True; 本会话亲测复核两处事实断言)**:
- **4 P1 必改 (v3 已全落实)**: ① **config 接线真缺陷** — `load_config()['sentiment']` 会 KeyError (本会话实测: load_config 扁平根 dict, `'sentiment'` 非键, 真键 `sentiment_analysis`) → §2.3 改 `boilerplate` 顶层块 + `load_config().get('boilerplate',{})` + §4-9 真穿透断言; ② **tier1-only 无运行期兜底** → §0/§2.2/§2.3 补 `df_dict_budget_hard`→`SystemExit(1)` 硬闸 + `memory_tier=disk/auto`→`NotImplementedError` (绝不静默 OOM) + §4-10 gate; ③ `np.empty` 脏内存 + 伪码缺 except 0 填充 → §2.1 `np.zeros` + 显式 `except ValueError: per_doc_total[idx]=0`; ④ **ctx/ss 保护自相矛盾** (替换单遍后无参照臂) → §2.3 保留 `memory_tier=single_pass` legacy 参照臂 + §3-P5 强制小 chunk_size 令 ctx/ss 跨多块。
- **P2 已采纳**: int/float 类型感知 assert (§2.6, 防 `1==1.0` 逃逸); hopeless-pruning 安全判据 `d_cur+N_remaining<cutoff` (§2.2, 防靠后块跨阈值漏剪); `chunks_with_index` 全局 idx 契约 + compute 新签名明写 (§2.1); `ngram_range` 工厂穿透防死参 (§2.6); §5 "OOM 产不出变可产" 收紧为 tier2-conditional。
- **本会话实测订正 Round1 误判 (勿信底稿, 验方向)**: Round1 称"`中 国 银 行` 零 4-gram 致态b reachable 崩溃" — 亲测 char_wb 对短词 emit 整个 padded 短词一次 (`中 国 银 行`→4 feature/total=4), **态b 在 `_clean`≥4 下确实不可达 = 死分支** (v1 裁定才对); `np.zeros`+except 保留为零成本防御, 但**不**据错误前提改称"态b 可达"(§1.3 已注机制)。
- **经证明严密 (Round1 交叉确认)**: §9 三不变量 (实读核实)、§8-1 边界空格、§2.5/§4-8 top-k 集合等价、§4-4 spy 结构不变量、§2.4 banner 同步、Pass2 两遍优化、§6 拒斥 —— 均实证正确。

**Round2 最终确认复审 (2026-07-06, 3 镜头[v3修订正确性/可实施性/安全一致] + 首席终裁; 12 findings; correctness=confirmed_ready, 另两镜头 residual_fix; 终裁=needs_minor_fix, can_authorize_tier1=True)**:
- **1 P1 必改 (v4 已落实)**: `df_dict_budget_hard` 硬闸原置 Pass1 循环**后** → 生产 global_df 累加中途撑爆时被 OOM-killer 先 SIGKILL, 永远到不了检查点, 违背"拒绝跑优于静默 SIGKILL"承诺 → §2.1 伪码移入**循环内周期检查** + 补可操作 SystemExit 消息 + §2.2 措辞统一 in-loop + §4-10 gate 加"第2块即越限"断言。(⚠ dev T=2 ~2.4M entry 永不触发 40M, 不阻断本次授权; 生产潜伏。)
- **7 P2 已全采纳 (万无一失收口)**: ① §2.1 两处工厂调用补 `ngram_range=ngram_range` (与 §2.6 对齐防死参); ② 态b except "精确复现"措辞收紧 (单遍整语料 nan vs chunked 仅本块 nan); ③ `df_dict_budget_hard=40M` 标注"保守占位待 P0 校准"(消"128GB 反推"口径落差); ④ `_MAX_SAFE_DOCS` 常量**保留**供 legacy single_pass 臂 (防 NameError) + branch/snapshot 二选一; ⑤ clamp 在 **compute 入口**执行 (直调+enrich 双路径受保护, 防 chunk_size=0 死循环); ⑥ SystemExit 补非空消息; ⑦ "tier2 v1 必做"→"生产首版必做"(与计划版本 v1/v2/v3 脱钩防混淆); ⑧ §2.4 docstring 刷新清单补删 HashingVectorizer/min_df 旧建议 (与 §2.1/§6 一致)。
- **Round1 四修 v3 落地经 Round2 全部 confirmed_correct**: config 扁平根接线 (实读 config.py 二次确认)、int/float 类型感知 assert、top-k 集合等价、§4-4 spy 结构不变量、§9 三不变量、np.zeros+except 死分支防御、banner 同步、P5 小 chunk_size ctx/ss 多块、tier1-only 诚实定位、hopeless-pruning 安全判据、§8-1 边界空格 —— 11 项逐一实证正确。

> **v4 状态: v1+v2+Round1+Round2 累计 (9 P1 + 16 P2) 全落实; 两处 live 事实亲测钉死; 三轮独立对抗评审 (v1/R1/R2) 交叉确认核心算法字节等价数学严密。判定 ready_to_implement, can_authorize_tier1=True。本次授权实施 tier1 (字节等价 dev 可验), tier2 DEFERRED 待生产 P0。**

**═══ 实施记录 (2026-07-06, tier1 in_memory 已落地) ═══**
- **改动文件 (by-name)**: `pipeline/sentiment/boilerplate.py` (核心) + `config/sentiment.yaml` (boilerplate 顶层块) + `tests/test_boilerplate_chunked.py` (新 gate)。
- **落地内容**: `_make_vectorizer` 工厂 (类型感知 assert) + `_coerce_int` config 畸值兜底 (None/bool/±inf/nan/str→默认) + dispatcher `compute_boilerplate_ratios` (入口 clamp + memory_tier 分派) + `_compute_single_pass_legacy` (冻结参照臂) + `_compute_chunked` (tier1 exact two-pass: Pass1 流式 global_df+per_doc_total+in-loop 硬闸, Pass2 固定 boiler_set 词表 transform) + enrich config 接线 (`load_config().get('boilerplate',{})` 扁平根) + banner/docstring 刷新 (删 HashingVectorizer 旧建议)。
- **本机验证 (全绿)**: ① **字节等价实测**: single_pass vs in_memory 在 chunk_size∈{1,2,3,4,5,7,n-1,n,2n} + 退化文档跨块 + 阈值边界 **逐字节等** (reviewer 独立 1200 次差分 0 失败); ② 24 gate 全过 (test_boilerplate_chunked 16 + test_boilerplate 8); ③ ruff 干净; ④ **golden 复现 baseline-stash A/B: 0 新增失败** (17↔17 既存陈旧 parquet 红灯, 与本改动无关, `00_preprocessing` 等证); ⑤ 下游 (test_22_tone_words/test_paper_spec_schema/test_omni_fix_herd) 全绿。
- **DEFERRED (生产机)**: tier2 disk-backed DF (§3-P0 外推裁定后) + golden 生产重生 (字节等价故零漂移, full 轨哈希 a5667be2b3fce425 不变) + hopeless-pruning (§2.2 opt-in 默认关, 本次不落地, docstring 未承诺, 自洽)。

**Result 复审 Round1 (实施代码, 4 镜头[字节等价/边界SAFE/config接线/计划测试] + 终裁; 5 findings 全 P2, must_fix 空; 终裁=ship_ready)**: 4 镜头全判 correct, reviewer 独立跑 1200 次差分 + 手工 ctx/ss 三轨多块字节等价佐证。**3 个 P2 已修**: ① config `chunk_size:null`→`int(None)` TypeError 崩 → `_coerce_int` 兜底; ② config 穿透测试补断言全 4 键 (防 budget 键接线漂移); ③ 加三轨 ctx/ss 多块字节等价 gate (P5 dev A/B 固化为单元 gate)。余 2 P2 (canonical-unchanged 测试现 in_memory-vs-in_memory 表述 / pruning 未落地) 经判非缺陷、自洽。

**Result 复审 Round2 (最后一次, 3 镜头[最终正确性/回归集成/收尾一致] + 终裁; 2 findings; 终裁=ship_ready, can_commit=True)**: 3 镜头全 ship_ready。**1 个 P2 已修**: `_coerce_int` except 元组漏 `OverflowError` (`int(±inf)` 逃逸, config 写 `.inf` 会崩) → 并入捕获元组 + 加 inf/-inf/nan/bool/str 兜底 gate。另 1 为提交清单指引 (非缺陷)。经证正确: bool 排除防 True→1 / 双路径 clamp / nan→default / disk fail-loud / 恰 3 文件改动。

**Final 审计 Round A (提交后, 3 镜头[正确性深挖/生产集成/确定性golden] + 终裁; 5 findings→3 P2 潜伏; correctness_deep+determinism_golden=clean, prod_integration=fix_needed; 终裁=clean_ship, must_fix 空)**: 作者先做 ground-truth 自验证 (属性化 fuzz 1800 次 A/B 0 失败 + 真实 400 篇新闻多块 A/B 字节等 + 真实 enrich 无循环导入)。3 潜伏 P2 **全部主动加固** (超 must_fix 空的最低要求, 求"完美无缺"): ① **fail-loud 不对称 (真缺陷)**: `disk`/`auto` 的 `NotImplementedError`⊂Exception 被调用方 tone_words `except Exception` graceful-skip 吞 → 静默丢 boilerplate 三轨列, 与 fail-loud 意图相反 → **改 `SystemExit`⊂BaseException** 穿透硬停, 与 hard 闸统一 (实证穿透确认); ② **budget≤0 footgun**: 非正 budget 令 `0<budget<len` 恒假静默禁用 OOM 闸 → 加 **loud WARNING "硬闸已禁用"**; ③ **hard 闸连坐 stage-22 已算产出** (SystemExit 在保存前, 40M 未校准占位) → **docstring 显式披露** "生产 T=19 须先跑 §3-P0 校准硬闸避免误触 nuke 整批"。gate +2 (disk→SystemExit 穿透 + budget≤0 警告)。correctness_deep 亲测确认极长文档/重复文档/pandas NA/阈值边界/unicode/N=1 全字节等; determinism_golden 亲测 HASHSEED=0 vs =1 输出逐字节等 (global_df dict 序经 sorted(boiler_set) 消除、整数计数无浮点序依赖)。

> **最终状态: 计划 v4 + 实施 tier1 + Final-A 三潜伏加固 全部落地; 三轮计划 (v1/R1/R2) + 三轮结果 (R1/R2/Final-A) 对抗评审通过; 字节等价四重验证 (数学证明 + fuzz 1800 + 真实数据 400 + golden A/B 0 新增) + HASHSEED 确定性; 26 gate + ruff + 下游全绿。SHIP-READY。**

---

## §11 一句话白话总结
这段代码现在「把所有文章的所有 4–6 字词片一次性摊在内存里数」, 文章一多就爆内存。改法保证「分批数出来的结果和一次性数**一模一样**」(已用数学严格证明、四路评审交叉验证)。**但评审揪出一个关键误判**: 真正占内存的不是那张大计数表 (它其实较小), 而是「所有不同词片的清单」——分批也得留着它。所以真解法分两层: 轻量层 (分批, 去掉大计数表) 若清单还装得下就够; 装不下就走重量层 (把清单也挪到硬盘上精确累加)。走哪层, 先用真实数据实测外推决定, 绝不靠乐观估计赌。两层都保证结果一字节不变, 已有的 golden 基线一个字节都不用重生。
