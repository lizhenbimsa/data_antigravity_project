# news_process 功能冗余度评估 v2 — 全量 18.2M / T=19 修正版（国际顶刊标准）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**日期**: 2026-06-05  **取代**: `REDUNDANCY_AUDIT_TOPJOURNAL_2026-06-05.md`（v1，T=2 试跑样本假设下的诊断，头号结论已被新事实证伪）
**触发**: 用户披露实际持有 **18,198,978 条银行媒体报道文本 / 2007–2025（T=19）**，当前管线只在 **9,427 篇 / 2.5 个月（≈0.052%）** 的试跑样本上跑过。
**方法**: 可行性/成本基线 + 9 子系统在 T=19 下逐功能重分类 + 高风险论断三/双镜头对抗复核（112 agent / 7.5M token / 1851 次取证 / 全部基于磁盘真值与代码注释）
**性质**: 只读审计，未改任何代码/数据。

---

## 〇、为什么要重写：一个事实颠覆了头号结论

v1 报告的头号根因是 **「根因① T=2 浅面板，识别机器集体装饰化（最致命）」**，它驱动了 v1 约 80% 的"砍/合并"裁定。但这个 T=2 **不是数据的真实深度，而是 2.5 个月试跑样本的假象**：

| 维度 | v1 误以为的"全部数据" | 真实数据 |
|---|---|---|
| 文本量 | 9,427 篇 | **18,198,978 条** |
| 时间跨度 | 2017-11-13 → 2018-01-30（2.5 个月） | **2007–2025（18 年）** |
| 面板 | T=2 / 176 行 | 目标 T=19 / N≥200 / 3000+ 行 |
| 已处理比例 | （误当 100%） | **≈ 0.052%** |

三条铁证（实读，非推断）：
1. **代码注释自己招供"试跑假象、全量恢复"**：`iv_did.py:586-588` 写明 `[DiD 不可识别] _post 全为 0 … production T≥3 面板下自然恢复可识别`；`network_spillover.py:46-51` 写明 `…须待 production run 扩 T≥3 + 结局变量取数后重估`；`article_topic.py:22` 写明 BERTopic `min_cluster_size=5000, 400k 文章 → K≈15-30`（即它本就为 40 万篇配置，1170 篇试跑必崩）。
2. **政策冲击时点全部落在窗口内**：DCEP 2019/2020/2022 + 沙盒 2020/2021/2022，6 个处理年全 ∈ [2007,2024]，且 `policy_shocks.json` 自带"先入为主"交错采纳 + never-treated 控制组（宁夏/内蒙古/西藏/青海）——这正是 Callaway-Sant'Anna csdid 所需结构。`post≡0` 的**唯一**原因是试跑样本停在 2018-01，早于最早处理年 2019。
3. **没有任何 config 日期截断**：`load.py` + `preprocessing.yaml` 全文无 `date_range/start_date/sample/nrows`。2.5 个月是测试 Excel 的自然边界，喂全量同一管线即产出 2007–2025 全跨度。

> **结论**：v1 判为"装饰性冗余、不可识别"的整套识别机器（Bartik IV / 交错 DiD / 事件研究 / 网络溢出 / 5 年滚动 z_score），在全量 T=19 下**全部恢复为可执行的因果识别**。它们不是冗余，而是**为全量正确建造、被 0.052% 试跑数据喂不动的休眠脚手架**。

---

## 一、修正后的一句话结论

> 上一轮"砍 80%"系统性**高估**了冗余。真实图景是：
> **约一半的"被判砍"功能是休眠脚手架（REINSTATE / SCALE_BLOCKED，保留待全量激活，勿删）；约 17 项是与数据深度无关的真冗余（SURVIVES_REDUNDANT，仍建议自上而下退役）；仅 3 处磁盘残渣是可立即清理的死东西。**
> 真正的瓶颈**不是功能太多，而是处理吞吐**——你只处理了 0.052%。最高标准的路径不是删代码，而是**分阶段喂数据 + 控预算激活识别 + 把 11 篇收敛为 6 篇连贯纲领**。
> 而且：上一轮我称"唯一可安全硬删"的 placebo-DiD 死代码，本轮被**推翻**——全量下它是顶刊必备的安慰剂检验。**全量下，识别机器里没有任何一项应被硬删。**

---

## 二、修正后的四分类（重分类 109 项功能判定）

```
重分类后状态分布
REINSTATE 恢复(试跑误伤的潜在能力)   ████████████████  32
SCALE_BLOCKED 待处理(卡预算/算力/外部数据) ███████████████  31
KEEP 本就保留                        ██████████████  29
SURVIVES_REDUNDANT 真冗余            ████████  17
STILL_CUT 死代码/残渣                █  少数
```

对抗复核稳健性：46 个 REINSTATE 经独立"识别可行性"镜头**维持**，仅 8 个被翻案（4 个收紧为 SCALE_BLOCKED、4 个回到真冗余）；22 个 SURVIVES_REDUNDANT 经"残余冗余"镜头**维持为真冗余**。重分类经得起对抗。

| 类别 | 含义 | 代表功能 | 处置 |
|---|---|---|---|
| **REINSTATE** | 上轮因 T=2 误判，全量恢复可识别 | 交错 DiD、Bartik IV、事件研究、网络 W/W²、经济圈 LOO、**placebo-DiD**、stage 17 BERTopic、stage 18 staleness、38a 时间掩码、benefit 因果、39f variance | **保留勿删**，打"待全量激活"标签 |
| **SCALE_BLOCKED** | 可识别有价值，卡在吞吐/预算/外部数据 | stage 21 全量 LLM、stage 49 z_score 三件套、风险 outcome（z/NPL/RWA）、embedding 15/25/27、stage 23 BERT 全量、herd_decay（须先优化）、stage 19 NER | **待处理**，非冗余 |
| **SURVIVES_REDUNDANT** | 与数据深度无关的真冗余 | C2 心理计量 HTMT/AVE/Cronbach α（39d/39e/39a 大部）、双轨二级笛卡尔积 ~300 列、per-model 切片/IDF/tone_gap/MSENT、22 中心度长尾、strategic_diff 四轨 | **可砍/合并**（自上而下退役） |
| **STILL_CUT** | 即便全量也删的死东西 | 3 处磁盘残渣（39g json / text2vec csv / 备份 epu parquet） | **可立即删** |

---

## 三、识别解锁图（全量 T=19 下哪套识别恢复）

| 识别策略 | 所需最小数据 | 全量 2007–2025 满足? | 解锁服务的论文/顶刊 | 取证 |
|---|---|:--:|---|---|
| 交错 DiD（Callaway-Sant'Anna csdid） | T≥3 且覆盖 ≥2019；理想 pre 2015-18 + post 2023-24 | ✅ | brokerage_network/clarity/disagreement → RFS/JAE | `iv_did.py:586-655` csdid 命令已产 |
| Bartik 移份额 IV（GPSS 2020） | T≥3 + 200 银行基期截面变异 | ✅ | P2 attention / llm_peer → JCF | `iv_did.py:95-272` |
| 事件研究 / Sun-Abraham 2021 | pre≥3 + post≥3（实质 ≥7 年跨 treat） | ✅ | 全 DiD 论文平行趋势 | `30_figure1_event_study.do.tmpl` |
| 网络 W²-2SLS（Bramoullé 2009） | T≥3 + 结局变量 ROA | ✅（须 merge 财务） | brokerage_network → RFS 二阶 IV | `network_spillover.py:46-51` |
| 5 年滚动 σ(ROA) z_score（Laeven-Levine 2009） | **T≥5 连续年 ROA（实质 2015-24）** | ✅（须外部财务） | clarity/disagreement 主结果 | `risk_taking_outcomes.py:25-27` |
| placebo-in-time DiD（安慰剂） | 处理组 2016-18 有 pre 期 | ✅ | DiD 论文必备 falsification | `controls.py:978-979`（锚 Hassan 2019 QJE Table 7） |

**关键：解锁不必全量 18.2M。** 识别靠"(bank,year) cell 有非缺失情感均值 + 处理时点变异"，不靠篇数本身。**最小可识别配方**：200 银行（含处理组 + never-treated 控制组）× 2015–2024（硬覆盖 2019–2022 处理窗）× 每 cell ≥5–10 篇 ≈ 数万相关篇，即达 `obs_target_min=3000`，LLM 预算落 **~$3k 低带**。

---

## 四、新的真正瓶颈：处理吞吐与预算（不是功能冗余）

### 18.2M 文本处理成本模型（带明确假设，须以 yunwu 实时报价校准）

计费基数（`tone_llms.py:565`）= 进入 stage 21 的银行新闻篇数 × 3 模型 × 2 轨（full/ctx）= **每篇 6 次 LLM 调用**。

| 预算档 | 计费篇数 | token 量 | 现金成本 | wall-clock（单 key） |
|---|---|---|---|---|
| 低（分层子样本） | ~1.5M | ~2.6e10 | **~$3.3k** | 数天 |
| 中（全量银行新闻 ~43%） | ~7.8M | ~1.3e11 | **~$28k** | ~31 天 |
| 高（全 18.2M 送 LLM） | 18.2M | ~3.1e11 | **~$126k** | 数月 |

+ stage 23 BERT 三模型：~80–170 GPU·小时（本地 $0 增量，须 `HF_HUB_OFFLINE=1`）
+ embedding 15/25/27：~$470（共享）~ $2.1k（须确认三 stage 复用同一篇 embedding）

### 真正的工程瓶颈（按优先级）

1. **LLM 预算 + 网关吞吐**：约 4.7e7 请求 / 单 key max_concurrency=100 ≈ 31 天；yunwu 429 限流会雪崩。→ 多 key / batch API 半价 / **先用便宜单模型做 relevance 预筛再跑三模型集成**（当前先全跑后过滤，浪费 ~57% 调用在 `is_bank_fintech_news=false` 篇上——这是一处真实的架构降本点）。
2. **herd_decay O(n²) cliff + OOM**（代码自爆点 `herd_decay.py:150-162`）：头部银行（工农中建招）全量数十万篇走纯 Python 双循环 + N×N 相似度矩阵 → 既慢又 OOM。**上全量前必须先落地注释里的 7 天窗 day-bucketing 优化（O(N²)→O(N·window)，数值等价，~50000× 提速）**。
3. **外部财务数据闸门（最硬）**：风险 outcome（z_score/NPL/RWA）须 merge CSMAR/Wind 银行季度财报（stage 47/49 读 `47_outcomes/*.parquet`，当前不存在）。无此数据，clarity/disagreement 两篇的因变量永空——这不是代码问题，是**数据采集待办**。
4. **去重 MinHash 内存**：18.2M 上是第二大本地算力瓶颈，须分块 LSH。
5. **可复现性/golden 重生规模**：全量重生后 golden 行数暴涨、列哈希全变，`test_panel_reproducibility` / `test_dag_consistency(==18)` / `test_papers_b_route(95)` 这套"逐列钉死"契约会大规模翻红，须**协调式重生**。

---

## 五、诚实残余冗余（即便全量 T=19 也成立，不因新事实翻案）

REINSTATE 解决的是"能不能识别"，解决不了下面三类**与数据深度无关**的真冗余：

**A. C2 心理计量构念效度家族 = 期刊家族错配**（最该诚实保留的冗余）
- HTMT / AVE / Cronbach α / Krippendorff α 是 Henseler-Ringle-Sarstedt 2015 JAMS 路线的**管理学/营销/心理计量**标配。
- 本项目 **8/11 篇投 econ/finance/accounting（JFQA/RFS/JAE）**，这些审稿人基本不索取构念效度三件套。**数据长到 T=100 也不会让 RFS/JAE 审稿人开始要 HTMT。这不是"喂不动"，是"喂了也没人要"。**
- 处置：39d/39e/39a 大部降为 opt-in 默认禁用；仅当真投 SMJ/ASQ 的 3 篇（substance/locus/collab）才需。**例外保留**：39h LLM 污染检验（DC4，任何 LLM 标注论文都可能索取）、39f 的 variance 半（第 10 篇 main）。

**B. 双轨纯翻倍 + variable-farm**（与识别力无关）
- 1565 列里 1279（82%）是 full/ctx 双轨变体。ctx 主轨思想 NECESSARY，但"二级方法（5 词典/3 BERT/IDF）× 加权 × ctx"的笛卡尔积（~300+ 列）是 robustness-of-robustness 纯翻倍。
- per-model 切片（LLM 64×3 列）/ tone_gap 28 列 / MSENT 8 列：顶刊只奖励 1 main ensemble + agree_rate。
- 全量只会让这些列更宽，不会更有价值。**例外**：`you_2018` 词典含 definite/ambiguous 子表，是 clarity 篇主测度，不可连带删。

**C. 11 篇 salami-slicing 的论文身份问题**（部分仍在）
- 即便数据接通，"一份语料切 11 篇因变量构念"对 econ/finance 顶刊仍是减分项。见第六节组合纪律。

> ⚠ **REINSTATE ≠ 立即可激活**：多数 REINSTATE 项仍带历史 metric-audit 的崩溃隐患（`exec_ner`/`staleness` 的 `groupby('year')` KeyError；attention 幽灵列未物化；`39e fill_diagonal` 在 pandas 3.0 CoW 崩；`falsification_template.do.tmpl:126` 的 `prob_gap_title_full` 残留）。这些"全量也会崩"的真缺陷必须先修，才能喂全量。

---

## 六、论文组合纪律：11 → 6 篇连贯纲领

实读各 `paper_spec` 的 outcome/treatment/identification 后，**主线 5 篇是真差异化，不是换标签薄片**：

| 论文 | treatment 构念 | outcome（关键：各不同） | 处置 |
|---|---|---|---|
| P1 tone → JFQA | 语调（有符号） | CAR_3day | **旗舰**（已接通，先投） |
| P2 attention → JCF | 曝光强度（无符号，Hassan 2019） | ln_fintech_investment | 差异化卫星 |
| P3 substance → SMJ | 实质/象征二元 | 3 年前向 ROA | 差异化卫星 |
| P4 locus → RFS | 底层/应用二元（2D） | CAR_5day + 专利 | 差异化卫星 |
| P5 collab → SMJ | 自主/协同二元 | M&A | 差异化卫星 |

**应合并的薄片**：
- benefit_society / llm_peer / strategic_diff / brokerage_network：outcome 全是 roa/car（方法学变体共享同一 Y）→ 收为主线的稳健性/IV 附录，各 ≤1 表。
- bank_media_disagreement + bank_news_clarity：同一风险 outcome、互为孪生（spec 文字近对称）→ **合并为一篇"媒体信息质量（分歧+清晰度）→ 银行风险承担"** → JAE/RFS。

> **净建议：11 篇 → 1 旗舰 + 4 差异化卫星 + 1 合并风险篇 = 6 篇连贯纲领**，其余降附录。顶刊认可连贯研究纲领，反感纯切片。

---

## 七、两阶段路线图

**阶段一（解锁识别，低成本 ~$3k）**——不必全量
1. 先修"全量也会崩"的真缺陷（exec_ner/staleness 的 `groupby('year')`、attention 幽灵列物化、39e fill_diagonal、falsification_template:126、herd_decay O(n²) bucketing）。
2. **分层子样本**（非随机 0.052%，非只抽 5 大行）：200 银行（处理组 + never-treated）× 2015–2024（硬保 2019–2022 处理窗）× 每 cell ≥5–10 篇。
3. 跑 P1 主回归 + DiD/Bartik/event-study/csdid **识别可行性证明**。

**阶段二（顶刊功效/稳健性，全量，中/高预算）**——前置硬门槛缺一不可
- (a) 落地 herd_decay day-bucketing 优化（防头部银行 OOM）；
- (b) 确认 stage 15/25/27 共享 embedding（降本）；
- (c) 装 faiss-cpu/datasketch/bertopic 解锁 stage 17/18；
- (d) **采集 DC2 银行财务 outcome**（CSMAR/Wind ROA/NPL/RWA）解锁 stage 49 + clarity/disagreement；
- (e) 显式解除 M0 预算 gate（18.2M LLM ~$28k–126k）+ 多 key/batch API；
- (f) stage 23 BERT 设 `HF_HUB_OFFLINE=1`；
- (g) 协调式 golden 重生（同步改三个计数断言测试 + 对齐 spec 的 IV 列引用）。

**立即可做（零风险，与全量无关）**
- 删 3 处磁盘残渣：`39g_*.json` / `30_text2vec_indicators.csv`（注：`.parquet` 仍被 golden 消费，须先从 golden 移除）/ 备份目录 `16_epu_panel.parquet`。
- 复核提交 `c4ea1757` 是否已守住 `falsification_template.do.tmpl:126` 的 `prob_gap_title_full` 崩溃隐患。

---

## 八、对 v1 的净修正（必须翻案的项）

| v1 裁定 | v2 修正 | 依据 |
|---|---|---|
| placebo-DiD = **唯一可安全硬删死代码** | **推翻 → REINSTATE** | 是 Hassan 2019 QJE Table 7 + CSA §4.3 平行趋势检验，全量下执行（`controls.py:978`）|
| D 组识别机器整体 NON_IDENTIFIABLE | **REINSTATE** | 代码注释自承 T≥3 恢复 |
| stage 17 BERTopic"1170<5000 必崩 → REMOVE" | **REINSTATE/SCALE_BLOCKED** | 为 40 万篇配置（`article_topic.py:22`）|
| 10 篇论文数据未接通 → 砍 | **REINSTATE/SCALE_BLOCKED** | 主列 MISSING 因 stage 21 未全量重跑 + 外部 outcome 待 merge，非构念假 |
| C2 心理计量家族错配（对 8 篇）= 冗余 | **维持 SURVIVES_REDUNDANT** | 与 T 无关，不翻案 |
| 双轨纯翻倍 / variable-farm = 冗余 | **维持 SURVIVES_REDUNDANT** | 与 T 无关，不翻案 |

> **一句话**：上一轮"砍 80%"应改写为——**约 50% 是为全量正确建造的休眠脚手架（保留待激活），约 30% 是与数据深度无关的真冗余（仍建议自上而下退役），仅极少数是死代码残渣。诚实区分二者，是本轮的核心修正。**
