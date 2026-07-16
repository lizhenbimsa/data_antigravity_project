# P2 attention 4 度量 — 顶刊支撑方法全菜单（任务 0 决策依据）

**日期**: 2026-06-05  **用途**: P2 (bank_fintech_attention, 对标 Hassan 2019 QJE firm-level exposure, 主张 "cumulative attention **WITHOUT sign**", 投 JCF/JFE) 的 4 个处理变量 `attention_index_full / attention_index_ctx / attention_disp_full / attention_pct_full` 的构造选单。
**方法**: 6 方法家族扇出 52 提案 → 引文真实性 + 可计算性双镜头对抗复核（13 agent）。去重后约 30 个独立方法。
**数据基线（实读确认）**: 全部公式落在 `14_fintech_intensity.parquet`（文章级，含 `fintech_intensity_score_full/ctx`、`doc_length`、`媒体(中文)`、`target_bank_mention_count`、`fintech_total_count`、`fintech_distinct_keywords`、`fintech_in_title`、`target_bank_in_title`、`co_mentioned_banks`、`日期`）+ `12_fintech_news_full.parquet`（全部银行新闻，提供"占比"分母）。两文件零空值。当前 2.5 月样本仅作接线/测试，全量 2007–2024 后所有时间维方法激活。

> **怎么用这份菜单**: 每列我给一个 ⭐**推荐默认**（第一遍处理就用它）+ 多个**备选/进阶**（作稳健性附录或审稿追加）。先定推荐项即可开工，其余随时可加。

---

## 〇、唯一需你拍板的研究决策

| 决策 | 选项 | 影响 |
|---|---|---|
| **index 用累积 Σ 还是均值 mean** | Σ（累积）/ mean（篇均）| 差异化主张写 "**cumulative** attention" → 倾向 **Σ**；mean 抹掉体量，作正交稳健 |
| **强度分还是裸计数** | `fintech_intensity_score`（IDF×SIF 提纯）/ 文章计数 | 强度分已扣复读/长文/泛词偏差，更稳；裸计数最透明 |
| **是否做 ctx 双轨** | 是 / 否 | ctx = 实体窗口归因（消多银行混排），是 Hassan proximity 的真落地，强烈建议保留 |

---

## 一、`attention_index_full`（主处理变量）—— 量"曝光总量/强度"

### ⭐ 推荐默认
> **`attention_index_full = ln(1 + Σ_d fintech_intensity_score_full_d)`**（bank-year 内累积技术强度 + log 压偏）
> 白话：把该行该年每篇 fintech 文章的"已提纯技术重度分"加总，取 log。**直接字面对齐"cumulative attention without sign"**（无符号、累积）。
> 文献：Hassan 2019 QJE（exposure 把每篇命中加总到 firm-quarter）+ Loughran-McDonald 2011 JF（IDF 加权优于裸计数）+ Fang-Peress 2009 JF（log 化进回归）。实测 Σ_full∈[0.09, 51.4]，skew 4.2→log 后 1.5。

### 备选与进阶（全部可算）

| 方法 | 公式（bank-year）| 量什么 | 文献 | tier |
|---|---|---|---|---|
| 原始 fintech 文章计数 | `Σ 1` = COUNT(fintech 文章) | 最朴素曝光体量（extensive）| Fang-Peress 2009 JF; Da-Engelberg-Gao 2011 JF; Bybee 2024 RFS | 推荐(baseline) |
| **Hassan 式频率** | `mean_d(fintech_total_count_d / doc_length_d)` | 篇内 fintech 浓度（intensive，控文长）| Hassan 2019 QJE（exposure 核）| 推荐 |
| 平均技术强度 | `mean_d(fintech_intensity_score_full_d)` | 单篇平均 fintech 深度（体量正交）| Tetlock 2007 JF; LM 2011 JF | 推荐 |
| **提及加权强度** | `Σ_d (intensity_full_d × target_bank_mention_count_d)` | 强度×银行是否为焦点（最接近 Hassan 联合构念）| Hassan 2019 QJE; Barber-Odean 2008 RFS | 推荐 |
| 主题广度 | `Σ_d fintech_distinct_keywords_d` 或年内关键词并集数 | 覆盖多少种 fintech 子话题（谱宽）| Bybee 2024 RFS; GST 2019 Econometrica | 备选 |
| 标题显著加权 | `Σ_d (1 + λ·fintech_in_title_d)·w_d` | 标题级曝光显著度（salience）| Barber-Odean 2008 RFS; Da 2011 JF | 备选 |
| 跨媒体覆盖广度/HHI | distinct outlet 数 / `Σ_o s_o²`（媒体(中文)）| 曝光来源广度/集中（系统性）| Fang-Peress 2009 JF; Cookson-Niessner 2020 JF | 进阶 |
| 仅熔断通过累积 | `Σ_{verified_full} intensity_full_d` | 去伪信号稳健版 | Da 2011 JF; BBD 2016 QJE | 备选 |
| 高强度文章计数/峰值 | `Σ 1[intensity≥q90]` / `max_d intensity` | 极端/爆点级关注（分布上尾）| Da 2011 JF; Garcia 2013 JF | 进阶 |

---

## 二、`attention_index_ctx`（实体归因轨）—— 量"指向本行的 fintech 注意力"

> ctx 用 `content_ctx` 实体窗口算的 `fintech_intensity_score_ctx`，落实 Hassan 的 **proximity-to-firm 归因**：多银行混排时不把别家 fintech 算到本家。实测 ctx 比 full 低（mean 0.279 vs 0.426），15.2% 文章 ctx=0（fintech 离本行远）。

### ⭐ 推荐默认
> **`attention_index_ctx = ln(1 + Σ_d fintech_intensity_score_ctx_d)`**（ctx 轨累积，与 full 同构）
> 文献：Hassan 2019 QJE（firm-proximity 归因频率），把 firm-quarter 改 bank-year、邻近频率换连续 ctx 强度分。

### 备选与进阶（全部可算）

| 方法 | 公式 | 量什么（full 无法分离）| 文献 | tier |
|---|---|---|---|---|
| **归因净额 gap** | `mean_d(intensity_full_d − intensity_ctx_d)` | 注意力借位/稀释度（多少 fintech 不是讲本行）| Hassan 2019 QJE; Hoberg-Phillips 2016 JPE | 推荐(→ disp) |
| 邻近归因份额 | `Σ ctx_d / Σ full_d` ∈[0,1] | 无量纲"归因纯度"（适合主回归 RHS）| BBD 2016 QJE; Bybee 2024 RFS | 推荐(→ pct) |
| 实体邻近覆盖率 | `Σ 1[verified_ctx_d] / N` | 广延边际：多少篇真"贴身"讲 fintech | Fang-Peress 2009 JF; Barber-Odean 2008 RFS | 推荐 |
| 提及加权邻近 | `Σ(w_d·ctx_d)/Σw_d`, `w=mention_count` | 银行中心度调整后的邻近注意力 | Hassan 2019 QJE; LM 2011 JF | 备选 |
| 共现折算净额 | `mean_d(ctx_d / (1+k_d))`, `k=co_mentioned_banks 数` | 扣多银行篇内共享稀释（最严归因）| Hassan 2019 QJE; Cookson-Niessner 2020 JF | 备选 ⚠见注 |
| 标题-邻近强调 | `mean_d 1[fintech_in_title ∧ target_bank_in_title]` | 本行×fintech 同进标题（最高显著位）| Barber-Odean 2008 RFS; Da 2011 JF | 备选 |
| 邻近-异常（截面 z）| `(ctx_att_{b,t}−mean_b' )/sd_b'` | 超常 fintech 关注冲击（横截面）| Da 2011 JF; BBD 2016 QJE | 进阶 ⚠T |

⚠ 共现折算：`co_mentioned_banks` 部分为空，先查填充率；大面积空则退化为推荐默认。

---

## 三、`attention_disp_full`（离散度）—— 量"曝光集中还是分散"

> 这是 full/ctx 都给不出的**分布形态**维度：同样篇数，挤在 1 家媒体 vs 铺满 30 家，注意力性质完全不同。

### ⭐ 推荐默认
> **`attention_disp_full = Σ_o s_{b,t,o}²`（跨媒体 HHI，媒体(中文) 份额平方和）**，或报 `1−HHI` 作分散度。
> 白话：该行该年 fintech 报道按媒体来源切份额算集中度。HHI→1 单一媒体垄断；→0 广泛分散。
> 文献：Fang-Peress 2009 JF（覆盖广度）+ Cookson-Niessner 2020 JF / Antweiler-Frank 2004 JF（HHI/熵度量来源分散）。实测每 bank-year distinct outlet [1, 4.7, 48]。

### 备选与进阶

| 方法 | 公式 | 视角 | 文献 | tier |
|---|---|---|---|---|
| 跨媒体 Shannon 熵 | `−Σ_o s_o ln s_o`，归一 evenness `H/ln O` | 对长尾更敏感（HHI 头部敏感）| Antweiler-Frank 2004 JF; Cookson-Niessner 2020 JF | 备选 |
| 媒体覆盖广度 | distinct 媒体(中文) 数 `O_{b,t}`（或 log）| 直接"有多少家"（Fang-Peress 本义）| Fang-Peress 2009 JF | 推荐 |
| 强度离散 SD/CV | `std_d(intensity_full_d)` / `SD/mean` | 报道技术含金量的参差（二阶矩）| LM 2011 JF; Cookson-Niessner 2020 JF | 进阶 |
| ctx 跨媒体 HHI | 同 HHI 但份额按 ctx 强度归因 | 邻近注意力的来源分散 | Fang-Peress; Cookson-Niessner | 进阶 |
| 跨地理 HHI（省/市）| `Σ_r s_r²`（国家地区/省份 或 城市）| 全国性 vs 区域性曝光 | Cookson-Niessner 2020 JF | 进阶 ⚠引文见注 |
| 媒体集中 Gini | outlet 份额的 Gini | HHI(头部)/熵(长尾) 外第三视角 | — | 备选 ⚠引文见注 |
| 月度计数离散 | `CV(月度 fintech 计数)` / Gini | 全年铺开 vs 某月集中（稳健）| BBD 2016 QJE; Bybee 2024 RFS | 备选 ⚠T |
| 月内突发度 burstiness | `(σ−m)/(σ+m)`，间隔 τ | 扎堆爆发 vs 细水长流 | Goh-Barabási 2008（**物理刊**）| 进阶 ⚠T+引文 |

---

## 四、`attention_pct_full`（占比/份额）—— 量"fintech 占该行媒体议程的份额"

> 对"该行整体曝光量"做归一，使大行小行可比（大行 fintech 文章多但份额未必高）。

### ⭐ 推荐默认
> **`attention_pct_full = N_ft_{b,t} / N_all_{b,t}`**（fintech 文章数 / 全部银行新闻数）
> 白话：该行该年新闻里 fintech 主题占比。最纯的"fintech 注意力议程份额"，无符号，正中 P2 主张。分子读 stage14，**分母必须读 12_full（含非 fintech 行）**。实测年均 share ≈ 0.24。
> 文献：Fang-Peress 2009 JF（coverage ratio）+ BBD 2016 QJE（按期总量归一）。

### 备选与进阶（全部可算，除标注）

| 方法 | 公式 | 量什么 | 文献 | tier |
|---|---|---|---|---|
| 强度加权份额 | `Σ intensity_full_d / N_all` | 质量加权份额（广度×深度）| Tetlock 2007 JF; LM 2011 JF | 推荐 |
| **平滑对数几率** | `ln((N_ft+0.5)/(N_all−N_ft+0.5))` | 映射到全实轴、对小份额敏感、回归友好 | GST 2019 Econometrica（log-odds +0.5 平滑）| 备选 |
| 年度去均值异常份额 | `share_{b,t} − mean_b'(share_{·,t})` | 剔年度宏观热度，留银行特异 | Da 2011 JF; BBD 2016 QJE | 备选 |
| 标题加权份额 | `(N_ft + λ·N_ft,title)/N_all` | 显著度加权（标题主打 fintech）| Barber-Odean 2008 RFS; Fang-Peress 2009 JF | 推荐 |
| 广度归一份额 | `mean(distinct_kw)×(N_ft/N_all)` | 主题宽度×份额 | Bybee 2024 RFS; GST 2019 Econometrica | 备选 |
| 媒体广度调整份额 | `(N_ft/N_all)×(1−HHI_outlet)` | 剥离单一信源刷量的"可信份额" | Fang-Peress 2009 JF; Cookson-Niessner 2020 JF | 备选 |
| 同业类型内相对份额 | `share_{b,t} / mean_{Type(b)}(share)` | 类型内 fintech 关注领先度 | Da 2011 JF; Hoberg-Phillips 2016 JPE | ⚠**需外部银行分类表** |

---

## 五、通用变换（可叠加于上面任一 index/share）

| 变换 | 公式 | 何时用 | 文献 |
|---|---|---|---|
| log1p | `ln(1+X)` | 计数/求和量右偏必用 | Fang-Peress 2009 JF; LM 2011 JF |
| winsorize 1/99 | 缩尾 | 去极端长文/刷量 | 计量惯例 |
| 年内 rank/decile | 年内百分位/十分位 | 非参、抗异常、跨年可比（审稿稳健性必备）| Da 2011 JF |
| EPU 式期归一+单位 SD | `X/(Σ_b X)` 再 `(·−μ_t)/σ_t` | 跨 19 年可比（吸收媒体总量趋势）| BBD 2016 QJE |
| Da 异常（时序）| `X_{b,t} − MA_{[t−k,t−1]}` | 留"超常关注冲击" | Da 2011 JF ⚠需 T≥3 |
| AR(1) 持久/冲击分解 | `X=ρX_{t−1}+η` | 分"持续关注"vs"事件冲击" | Tetlock 2007 JF ⚠需 T≥3 |

---

## 六、复核发现的引文/可计算性修正（诚实边界）

对抗复核确认绝大多数引文为真实顶刊，但有以下**须在论文里如实处理**的点：

| 项 | 问题 | 处理 |
|---|---|---|
| **Hassan 分母"总词数"** | 现成只有 `doc_length`=**字符数**，非词数 | 用 `doc_length`/`len(content_full)` 近似（二者相关 1.0）；若审稿坚持词数，用 jieba 分词派生（本仓已锚 jieba==0.42.1）|
| **GST 2019 归属** | "phrase frequency 加权" 与 "log-odds 平滑" 分属两文 | log-odds+0.5 → **GST 2019 Econometrica**（组间差异）；IDF/TF-IDF 综述 → **Gentzkow-Kelly-Taddy 2019 JEL**（Text as Data）。勿混引 |
| **地理 HHI 引文** | Drake-Roulstone-Thornock 2012 是 **JAR 非 JF** | 落 spec 时署正确刊名（JAR）|
| **burstiness 引文** | Goh-Barabási 2008 是 **EPL（物理刊）非金融顶刊** | 明示是借自复杂网络物理学的方法迁移，非金融内生度量 |
| **Gini-on-outlet** | HHI/熵有顶刊锚（Cookson-Niessner），Gini 用在 outlet 份额上锚定弱 | 作 HHI 的稳健替代，不单独主张 |
| **upper/lower 列** | 是文档"上下半段位置"计数，**非关键词重要性分级** | 勿误读；可做"前文 fintech 强调"弱信号 |
| **媒体类型(中文)** | 当前样本恒="报纸"单值 | 现阶段不可做媒体类型异质性；全量后或可 |
| **T 依赖方法** | Da 时序异常 / AR(1) / burstiness / 月度离散 | 当前 T=2 退化，**全量 2007–2024 后激活**（不是缺陷，是数据深度）|
| **需外部数据** | 同业类型内相对份额 | 需 245 银行的"类型"映射表（央行/银保监分类）|

---

## 七、一句话推荐起步集（先用这套开工）

| 列 | 推荐默认 | 配套稳健性（附录）|
|---|---|---|
| `attention_index_full` | `ln(1+Σ intensity_full)` | 原始计数、Hassan 频率、提及加权 |
| `attention_index_ctx` | `ln(1+Σ intensity_ctx)` | 归因份额、覆盖率、gap |
| `attention_disp_full` | 跨媒体 HHI | Shannon 熵、覆盖广度 |
| `attention_pct_full` | `N_ft/N_all` 计数份额 | 强度加权份额、log-odds |

> 这 4 个推荐项**全部当前样本即可算、全部顶刊锚定、全部 sign-free 契合 P2**。定了它们，W2 任务 1（聚合实现）就能直接落地；其余 ~26 个方法作审稿追加/稳健性储备。
