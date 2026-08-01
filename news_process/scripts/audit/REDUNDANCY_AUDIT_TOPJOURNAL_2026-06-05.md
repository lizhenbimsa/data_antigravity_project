> ⚠️ **本报告已被取代** — 见 `REDUNDANCY_AUDIT_TOPJOURNAL_2026-06-05_v2_FULLCORPUS.md`。
> 本 v1 的头号根因「T=2 不可识别」建立在"当前 176 行面板即全部数据"的错误前提上；用户实际持有 **18,198,978 条 / 2007–2025（T=19）** 文本，当前 176 行只是 0.052% 试跑样本。v1 约一半的"砍"裁定是试跑假象，全量下应翻为 REINSTATE/SCALE_BLOCKED。**v1 仅以下结论在 v2 仍成立**：C2 心理计量期刊家族错配、双轨 variable-farm、salami 论文身份是与数据深度无关的真冗余。下文保留作 T=2 视角的历史记录。

# news_process 功能冗余度评估（国际顶刊标准）

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**日期**: 2026-06-05  **镜头**: 顶刊审稿人 + 研究方法审计（不是"代码孤儿"检查）
**方法**: 1 基线 + 9 子系统逐功能定级 + 60 个删除候选 × 3 镜头对抗复核（190 agent / 11.6M token / 3356 次取证 / 全部基于磁盘真值实跑）
**性质**: 只读审计，未改任何代码/数据。所有结论为"按顶刊标准的取舍建议"，最终由作者决定。

> 与 `FEATURE_COMPLETENESS_AUDIT_2026-06-05.md` 的关系：那份是**工程视角**（代码是否孤儿/死代码），结论"几乎全保留"。本份是**学术视角**（顶刊是否需要/奖励），结论"学术冗余度极高"。**两份都对，且互补**——见第六节。

---

## 一句话结论

> 这个项目**不是"死代码冗余"，而是"学术冗余 + 数据不可识别"的双重过度建设**：
> 用 **1 份新闻语料 × 1 个 88 银行 × 2 年（176 行）的浅面板**，同时驱动 **11 篇论文 × 3 套情感方法 × 18 个校验阶段 × 95 个 Stata 模板 × 1565 列特征**。
> 按国际顶刊标准，**真正能投、能识别、不冗余的只有 1 篇（P1 媒体语调 → JFQA）的一小撮核心功能**；其余约 **80% 的上层功能要么顶刊不需要/不奖励，要么在 T=2 数据深度下计量上根本跑不出可信结果**。
> **但关键警告**：这些冗余功能**几乎都不能"硬删"**——golden 快照 / 通过的测试 / frozen paper_spec 把它们逐列钉死，60 个候选里只有 **1 个**（placebo-DiD 死代码）三镜头一致可安全删除。冗余必须**自上而下退役**（先砍论文 → 列/模板/校验随之收缩），不能自下而上 `rm`。

---

## 二、三大横切冗余根因（白话）

### 根因 ①　T=2 浅面板，识别机器集体"装饰化"（最致命）

实读 `51_panel_with_controls.parquet` = **176 行 × 1565 列，年份只有 {2017, 2018} → T=2，N=88 家银行**。
但 11 篇 `paper_spec.yaml` 的 `sample` 字段**全部写** `n_bank_min=200 / t_year=18 / obs_target_min=3000`——**规格宣称 18 年长面板，磁盘真值只有 2 年，差 9 倍**。

后果：为 econ/finance 顶刊准备的整套准实验识别机器，在 T=2 上**结构性失效**，且代码自己的注释已逐一招供：

| 识别机器 | T=2 下的真实状态 | 取证 |
|---|---|---|
| **DiD（DCEP/沙盒）** | 处理年 2019/2020/2022 **全在样本窗口外** → `dcep_post`/`sandbox_post` **恒为 0** | golden 列哈希 = `0000000000000000`；`iv_did.py:586` 自报 `[DiD 不可识别]` |
| **Bartik 移份额 IV** | 64%（112/176）bank-year 退化为 own-type one-hot，工具近共线于 bank-type FE，一阶段 F 弱 | `iv_did.py:29-35` 模块 docstring 自承 |
| **事件研究 ±3 年** | 2 个日历年最多 2 个相对时点，`forvalues -3/3` 的 7 个 lead/lag dummy 截尾后近全 0、共线丢弃 | `30_figure1_event_study.do.tmpl:34-43` |
| **网络溢出 W×tone / W²×tone** | lag 吃掉首年 → `peer_tone_lag1` 仅 **32/176 非空、全落 2018 单截面**；brokerage 2SLS 有效 N≈22 | `network_spillover.py:46-51` 自承 |
| **两路固定效应** | T=2 平衡面板上 `absorb(bank year)` 代数等价于一阶差分，有效样本 = N=88（**这条仍合法**，是少数幸存项） | 复核镜头实证 |

**白话**：论文 spec 里写的 DiD / Bartik IV / 事件研究 / 平行趋势 / placebo 这一套，在 2 年面板上**是装饰，不是可执行的因果识别**。顶刊审稿人看到 T=2 会当场否决这些识别声称。

### 根因 ②　11 篇 = 1 份数据切片，强 salami-slicing

全部 11 篇共用同一上游语料（`11_bank_news` 4054 行 + `12_fintech_news` 1170 行）和同一个 176 行面板，只在"因变量构念切片"上差异化（语调/曝光/实质性/底层应用/协同/分歧/清晰度…）。

更致命的是**磁盘真值**：除 P1 外，**10 篇的主处理变量或主结果变量在面板上根本不存在**（实跑逐列扫描）：

| 论文 | 目标刊 | 主处理/结果列 | 磁盘状态 |
|---|---|---|---|
| P1 媒体语调 | JFQA | `llm_vote_tone_ctx` | ✅ **唯一真接通** |
| P2 fintech 曝光 | JCF | `attention_index_full` | ❌ MISSING |
| P3 实质/象征 | SMJ | `long_run_roa_change_3yr`（需 ROA[t+3]） | ❌ T=2 下数学恒 NaN |
| P4 底层/应用 | RFS | `locus_layer_full` / `car_5day` | ❌ MISSING |
| P5 自主/协同 | SMJ | `innovation_collab_mode_full` / `m_and_a_fintech` | ❌ 双双 MISSING |
| benefit_society | RFS | `benefit_mean_full` | ⚠ 测度在、因果识别 T=2 失效 |
| brokerage_network | RFS | `peer_tone_lag1_full` | ❌ 仅 2018 单截面 |
| llm_peer（方法学） | RAS | `llm_peer_tone_iv_full` | ❌ 仅单截面有值 |
| strategic_diff | MS | `roa`（主回归 Y） | ❌ MISSING |
| bank_media_disagreement | RFS | `z_score`/`npl`/`rwa` 全套风险 outcome | ❌ 全 MISSING |
| bank_news_clarity | JAE | 同上风险 outcome | ❌ 全 MISSING |

**白话**：顶刊（尤其 econ/finance）极反感"一份数据切 N 篇"。这里不仅是 salami-slicing，10 篇连因变量都不在盘上——**它们目前是"选题骨架"，不是可投稿论文**。

### 根因 ③　econ ↔ 心理计量 双家族错配

18 个校验阶段**物理分层**成两套不兼容的学术惯例：

```
validation/ 子包  ── 12 个 ── 经济计量惯例（阈值/去重/半径/掩码/三角/词典覆盖/媒体多样性…）
                                服务 JFQA/RFS/JCF 的 Bartik+falsification 范式  ✅ 对口 8/11 篇
pipeline/audit/ 子包 ── 6 个 ── 心理计量构念效度（39a Cohen κ / 39c NMI / 39d HTMT+AVE /
                                39e LM HTMT / 39f Krippendorff α / 39h LLM 污染）
                                服务 SMJ/AMJ/ASQ/JAMS 的 Henseler 构念效度范式  ❌ 只对口 3/11 篇
```

**白话**：HTMT / AVE / Cronbach α / Krippendorff α 是**管理学/营销/心理计量**期刊（ASQ/AMJ/SMJ，Henseler-Ringle-Sarstedt 2015 JAMS 路线）的标配。**金融/会计顶刊（QJE/JF/RFS/JAE/JFQA）审稿人基本不索取、不阅读这些**。本项目 8/11 篇投 econ/finance/accounting，却建了一整套服务管理学期刊的构念效度机器——**这是为一个你不投的期刊家族买的保险**，叠加 T=2 浅面板更是空转（39d 样本塌到 n=64、39h post-cutoff 永远 n=0）。

---

## 三、9 子系统冗余度矩阵

| 子系统 | 顶刊真正需要的核心 | 现状规模 | 冗余度 | 一句话裁定 |
|---|---|---|---|---|
| A 情感三联(21-24) | 1 个 LLM ensemble main + 1 套收敛验证 | 3 方法×(3LLM+5词典+3BERT)+IDF+per-model 切片，数百列 | 🔴 高 | 留 `llm_vote_tone_ctx` + 1 套三角；其余 CONSOLIDATE |
| B 双轨 full/ctx | ctx 主轨 + full 1 条稳健 | **1279/1565 列(82%)是双轨变体** | 🔴 高 | ctx 核心思想 NECESSARY；二级方法×加权的 ctx 笛卡尔积 CONSOLIDATE |
| C1 经济系稳健(12) | 4-6 个核心(31/32/33/34) | 12 个 | 🟡 中 | 38a 时间掩码 REMOVE；35/38b/32a 择一；36/39 付费重跑留 1 |
| C2 心理计量(6) | 几乎为 0（错配家族） | 6 个 | 🔴 高 | 仅 39c+39f 的 variance 半留作三角；39a/39d/39e/39h 砍或保 opt-in 禁用 |
| D 面板识别 vs T=2 | 41 聚合 + 51 falsification | Bartik/DiD/事件研究/一二阶网络/经纪二分图 | 🔴 **最高** | 整套识别机器 NON_IDENTIFIABLE；留 41+51，其余降权/退役待 T≥3 |
| E 论文组合(11) | 1 篇旗舰(P1) | 11 篇(5+3+3)，10 篇数据未接通 | 🔴 **最高** | 留 P1；benefit/llm_peer/strategic 降级为 P1 附录；其余 6 篇砍/搁置 |
| F opt-in 未跑(17/18/19/49) | 仅 49 待真实数据 | 4 个投机性 D 组 feature + 30a 前置 | 🔴 高 | 30a 留；17/19 砍；18 至多留 hook；49 待 outcome 采集 |
| G Stata 复制(95) | ~14 主线(P1→JFQA) | 95 模板 + CLI + 33 三件套 | 🔴 高 | ~85-90% 随 salami/识别机器膨胀；核心<15% |
| H 核心基建(core/) | 几乎全部工程必需 | 14 模块 | 🟢 **保留** | ENGINEERING_KEEP；但其复杂度近半是被上层冗余倒逼出来的 |

---

## 四、删除候选「三镜头对抗复核」总览（用户要求的"再三核查"）

60 个候选，每个派 **3 个独立怀疑者**：① 顶刊辩护（尽力证明该留）② 依赖契约（删了会不会崩）③ T=2 数据识别（能不能跑出可信结果）。共识分布：

```
三镜头共识分布（60 候选）
CONSOLIDATE 合并收编  ████████████████████████████  28 (47%)
REMOVE 删除            ████████████████████          20 (33%)
KEEP_AS_OPTIONAL 降级  ████████                       8 (13%)
ARCHIVE 归档           ██                             2  (3%)
KEEP 推翻保留          ██                             2  (3%)
```

### ⚠ 本次复核最重要的发现：学术冗余 ≠ 可安全硬删

**"依赖契约"镜头（镜头②）几乎对每一项都判 `ARCHIVE` 而非 `REMOVE`**。原因：

- `tests/fixtures/golden_panel_v0.json` 逐列冻结了哈希/dtype，删任何面板列都破坏 `test_panel_reproducibility`；
- `test_dag_consistency.py:113` 硬断言 `len(STAGES_VALIDATION) == 18`，删任何校验阶段必红；
- `test_papers_b_route.py:142` 断言模板恰好 95、`test_paper_spec_schema` 断言论文恰好 11；
- 多篇 frozen `paper_spec.yaml` 把列名写进 `identification.iv.primary` / `controls`。

**结论**：学术上"该砍"的功能，工程上**几乎都不能裸 `rm`**——会打挂绿盘。正确动作是 **ARCHIVE（协调式退役：同步重生 golden + 改测试计数 + 收回 spec/registry）**，且应**自上而下**做（先砍论文身份 → 列/模板/校验自然收缩），不能逐列删。

**60 个候选里，三镜头（含依赖契约）一致 `REMOVE`、可立即安全硬删的，只有 1 个**：

| 唯一可安全硬删 | 三镜头 | 理由 |
|---|---|---|
| **placebo-in-time DiD 变量**（`controls.py:947-1029` `generate_placebo_did_variables`，产 `dcep_placebo{k}_did`） | REMOVE / REMOVE / REMOVE | 真·永不执行死代码：处理年全在窗口外，placebo 前移更不可能落进 2017-2018；无任何 golden/spec/测试引用。与"业务线 placebo"同名但完全独立，勿混淆。 |

### 各子系统候选裁定明细（节选关键项）

**A 情感三联**（9 候选）
| 候选 | ①顶刊 / ②契约 / ③T=2 | 处置 |
|---|---|---|
| LLM 三家族集成（main） | KEEP_OPT / ARCHIVE / CONSOLIDATE | 留 vote+agree_rate 进 P1，per-model 64×3 列收编 |
| 5 家词典集成 | CONSOLIDATE×2 | 留 1-2 家（you_2018 含 definite/ambiguous 子表，是 clarity 主测度，**不可连带删**） |
| IDF 加权轨 / per-model disagreement / tone_gap 28 列 / MSENT 8 列 | 多为 CONSOLIDATE，契约镜头 ARCHIVE | robustness-of-robustness，收编 |
| herd_decay 跟风衰减 | CONSOLIDATE（95 模板 0 引用） | 降为内部 hygiene，非可发表 feature |

**C2 心理计量**（5 候选）
| 候选 | ①/②/③ | 处置 |
|---|---|---|
| 39d Lexical HTMT+AVE | **REMOVE** / ARCHIVE / **REMOVE** | 家族错配 + 样本塌到 n=64；砍 |
| 39f Krippendorff α | REMOVE / ARCHIVE / CONSOLIDATE | variance 半是第10篇 main 须留，**α 半砍** |
| 39e LM HTMT | CONSOLIDATE | 与 39d 机制重复（代码自承），并入 |
| 39h LLM 污染(DC4) | KEEP_OPT / ARCHIVE / ARCHIVE | 2 篇 frozen spec 承诺项，T=2 永空转，**保 opt-in 禁用** |

**D 面板识别**（11 候选）
| 候选 | ③T=2 镜头 | 处置 |
|---|---|---|
| Bartik IV / DiD 政策冲击 | REMOVE（不可识别） | KEEP_AS_OPTIONAL 休眠脚手架，待 T≥3 |
| Rotemberg 权重 / 网络 W×/W² / 经纪 fire-sale | REMOVE | 不可识别；ARCHIVE（连函数带 3 测试原子移除） |
| 28 梯度地理缓冲 / 22 中心度 | REMOVE / CONSOLIDATE | 信息塌缩为 1-2 维，留省级 1 套作横截面描述 |
| 两路 FE 78 处 absorb | **KEEP**（推翻初判） | T=2 下等价一阶差分，**合法估计量，保留** |

**E 论文组合**（10 候选）：P2/brokerage/disagreement/clarity → REMOVE（数据双端皆空）；P3/P4/P5/benefit/llm_peer/strategic → CONSOLIDATE（构念真实但作独立投稿不可识别，降为 P1 附录）。

**F opt-in**：17 BERTopic（1170<5000 必崩）/ 19 NER（$12 产无归宿列）→ REMOVE；18 staleness → REMOVE/留 hook；49 → ARCHIVE（待真实 outcome 数据）。

**G Stata**：Bartik/event-study/network 模板 + 2 provisional 的 10 模板（use 不存在的 `49_*.dta`）→ REMOVE；benefit 22 模板留 6-8；**11 篇三件套 → KEEP**（推翻初判：参数化薄包装，33 文件仅 3045 LOC，逻辑全在共享 `_common`）。

**H 核心基建**：全部 ENGINEERING_KEEP（仅 canonicalization 降 KEEP_AS_OPTIONAL，但它是 stage 21 硬 import，**不可删**）。

---

## 五、保留 vs 删除 总原则

**为什么 P1 旗舰必须保留（每个维度都过关）**：
| 维度 | P1 媒体语调 |
|---|---|
| 数据接通 | ✅ 唯一主处理列在盘 |
| T=2 识别 | ✅ 主回归是横截面/一阶差分，不依赖 lag/IV/DiD |
| 顶刊对口 | ✅ JFQA，entity-attributed tone 是 Tetlock 2007 JF/L&M 2016 JAR 标准 |
| 母测度 | ✅ 其余衍生构念都是它的切片 |

**为什么其余大量功能是冗余（但需归档而非硬删）**：
1. **学术冗余**：顶刊只需 1 main + 几个核心稳健，不需要 3 套情感 × 双轨 × 5 词典 × per-model 切片，更不需要错配家族的 HTMT/AVE。
2. **不可识别**：T=2 让所有 lag/IV/DiD/事件研究/网络/5 年滚动 σ 结构性失效。
3. **数据未接通**：10 篇主变量磁盘 MISSING。
4. **工程钉死**：golden/测试/spec 让它们不能逐个硬删，必须自上而下协调退役。

---

## 六、可执行处置路线图（自上而下退役）

> 原则：**先收缩论文身份，列/模板/校验会自然坍缩**；逐列硬删只会打挂绿盘。

**第 0 步（可立即做，零风险）**
- 删 `controls.py` 的 placebo-in-time DiD 死代码（三镜头一致）。
- 清磁盘残渣（接上一份工程审计）：`39g_*.json`、`30_text2vec_indicators.csv`、备份目录里的 `16_epu_panel.parquet`。

**第 1 步（定旗舰）**
- 确认 **P1（媒体语调 → JFQA）为唯一可投旗舰**；benefit_society / llm_peer / strategic_diff 降级为 P1 的稳健性/IV 附录（各留 ≤1 张表）。

**第 2 步（退役 salami 薄片，协调式 ARCHIVE）**
- 把 P2/P3/P4/P5 + bank_media_disagreement + bank_news_clarity **从 `PAPER_IDS_ALL` 摘除并归档**；同步改 `test_paper_spec_schema`（11→5）、`test_papers_b_route`（95→对应模板数）、收回各自 Stata 子目录与三件套注册。
- 随之坍缩：~80 个 Stata 模板、对应 _ctx/per-model 衍生列、心理计量校验。

**第 3 步（瘦身情感与双轨）**
- 情感留 `llm_vote_tone` ensemble + 词典或 BERT 择一作三角；砍 IDF 轨、per-model disagreement、tone_gap、MSENT、herd_decay 进面板的部分（重生 golden）。
- 双轨留 ctx 主 + full 1 条稳健；砍二级方法×加权的 ctx 笛卡尔积（~300+ 列）。

**第 4 步（校验家族对齐）**
- 心理计量 6 个：仅留 39c + 39f(variance)；39a/39d/39e/39h 归档或保 opt-in 禁用。
- 经济系 12 个：留 31/32/33/34 + 36/39 择一；38a 删、35/38b/32a 择一。

**第 5 步（识别机器休眠）**
- Bartik/DiD/事件研究/网络 模板与列**不删、改为 opt-in 休眠脚手架**，并在论文中**明确披露 T=2 限制**（模板头注已部分做到），待 production 扩 T≥3 再启用。

---

## 七、给作者的一句忠告

> 当前项目的工程质量很高（基建健康、零真孤儿、2581 测试绿），**问题不在"代码烂"，而在"学术雄心远超数据能支撑的识别"**。
> 把 80% 的精力从"维护 11 篇 × 3 套情感 × 双家族校验 × 95 模板"收回，**集中打磨 P1 这一篇能在 T=2 上真识别、能投 JFQA 的旗舰**——这比继续铺摊子更接近一篇顶刊接收。
> 其余构念不是没价值，而是**等数据长出来（T≥3、补齐 outcome）再激活**。在那之前，它们应该是休眠的脚手架，不是维护负担。
