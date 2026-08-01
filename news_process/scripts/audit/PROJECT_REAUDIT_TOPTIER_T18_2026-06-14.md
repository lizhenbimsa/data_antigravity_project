# news_process 项目顶刊重审 (全量 T=19 前提) — 权威审计报告

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> PROJECT_REAUDIT_TOPTIER_T18_2026-06-14

---

## 元信息

- **审计对象**: news_process 银行—金融科技新闻面板研究流水线 + 11 篇论文组合 (8 fully-coded + 3 provisional)
- **审计日期**: 2026-06-14
- **审计身份**: JF / QJE / AER / RFS 资深 referee + Associate Editor
- **关键前提 (全量 T=19)**: 真实分析样本 = 2007–2025 年 (T=19) / 18,198,978 条新闻语料 / bank-year 面板。**早期试跑期硬盘产物为 T=2 试跑帧** (174 行 / year∈{2017,2018} / 87 banks / 9,427 篇 / 0.052% 子样本)。本报告一律以"论文宣称的 T=19 全量样本"为评判基准, 对 T=2 试跑产生的伪象单独标注, 不据其判缺陷。
- **方法学**: 12 个维度, 每条 finding 经 **find → verify (对抗式复核) → synth** 三段流程; 本报告**只采信 verdict ∈ {CONFIRMED, DOWNGRADED}** 的发现, 严重度以 `verdict.final_severity` 为准; verdict ∈ {REJECTED, ALREADY_MITIGATED} 的发现归入附录 (已复核排除 / 已化解)。
- **12 维度**: ① IV 工具变量 ② DiD/事件研究 ③ 情感构念效度 (SENT) ④ 注意力/文本构念效度 (ATTN) ⑤ 样本宇宙/选择偏误 (SAMPLE) ⑥ 跨年可比性/结构断裂 (XYEAR) ⑦ 推断/聚类/FWER (INFER) ⑧ 稳健性 battery 完备性 (ROBUST) ⑨ 计量设定/坏控制 (SPEC) ⑩ 论文组合/salami (PORT) ⑪ 可复现/诚信/引用 (INTEG) ⑫ 数据规模/T=19 就绪 (SCALE)。
- **跨引用基线**: 本轮在既有权威审计 `MEDIA_ATTENTION_AUDIT_TOPTIER_2026-06-14.md` / `REDUNDANCY_AUDIT_TOPJOURNAL_2026-06-05_v2_FULLCORPUS.md` / `MEASUREMENT_VALIDATION_AUDIT_TOPTIER_2026-06-13.md` 基础上扩展, 多条 finding 与其重叠 (已在逐条注明), 重叠项不重复计为全新缺陷。

---

## 执行摘要

**总裁决: MAJOR REVISION (大修可救, 非拒稿)。**

- **P0 (拒稿级) = 0**: 经对抗复核, 4 条原报 P0 全部被下调或推翻。**没有任何一条确认级缺陷动摇核心识别策略或使现有结论不可信**——所有最严重的发现要么是"已披露但未实现的稳健性/诊断交付", 要么是"投稿前必做的工程/重生流程前置", 要么是"内部开发态产物的卫生问题"。
- **P1 (major-revision 阻断) = 10**: 顶刊 referee 在 accept 前会要求逐条整改, 但均不致 desk reject。
- **P2 (minor / 披露) = 28**: 多为 $0 / golden-safe 的披露、措辞、稳健性补列。
- **已复核排除/已化解 = 3** (2 REJECTED + 1 ALREADY_MITIGATED)。

**一句话路线图**: 先在一次受控生产 run 中重生 panel + golden 闭合 T=2→T=19 自洽 (REPRO-1 + T18-1 元前提), 同步接通"声明已做但未执行"的识别/稳健性交付 (弱工具 AR-CI、Rotemberg 诊断、错时 DiD robust estimator、分时代稳定性、FWER battery、wild bootstrap), 修正 benefit_society 的 bank-FE 退化与 llm_peer 的同源 outcome, 并补主情感测度的 framing/披露——其中绝大多数为纯 Stata/spec/披露层 $0 改动, 仅 IDF 时变化、比值年标准化、benefit 脊柱/列值改动须 golden 重生。

> **就绪度元结论**: 当前盘面为 **T=2 试跑帧**, 全量 **T=19 run 尚未执行**。所有现有表/系数/golden 哈希都是 T=2 占位, 一旦全量重生将整体变化。**当下不存在任何一张"可投稿"的表**——这不是某指标算错, 而是整条证据链尚停在试跑态。识别策略 (Bartik / 错时 DiD / 事件研究 / 网络 / z_score) 的**设计**在 T=19 下成立 (REDUNDANCY v2 已证), 真正的阻断在于工程可执行性 + 协调式重生 + 上述声明—实现缺口的闭合。

---

## 总裁决与严重度分布表

| 维度 | 维度裁决 | CONFIRMED/DOWNGRADED P1 | P2 | 排除/化解 |
|---|---|---|---|---|
| ① IV 工具变量 | major revision | IV-2, IV-3 (2) | IV-1, IV-4, IV-5 (3) | — |
| ② DiD/事件研究 | major revision | DID-1, DID-2 (2) | DID-3, DID-4 (2) | — |
| ③ 情感构念效度 (SENT) | major revision | CV-1 (1) | CV-2, CV-3 (2) | CV-4 (mitigated) |
| ④ 注意力/文本构念 (ATTN) | major revision | — | CV-1, CV-2 (2) | — |
| ⑤ 样本宇宙/选择 (SAMPLE) | major revision | — | SU-1..SU-5 (5) | — |
| ⑥ 跨年可比性 (XYEAR) | major revision | CY-2 (1) | CY-1, CY-3 (2) | — |
| ⑦ 推断/FWER (INFER) | major revision | IV-3 (1) | IV-1, IV-2 (2) | — |
| ⑧ 稳健性 battery (ROBUST) | minor revision | — | (无确认级; RB-1..5 均无对抗裁决) | — |
| ⑨ 计量设定/坏控制 (SPEC) | major revision | IV-1 (1) | IV-2, IV-3 (2) | — |
| ⑩ 论文组合/salami (PORT) | major revision | SAL-3 (1) | SAL-1, SAL-2, SAL-4 (3) | — |
| ⑪ 可复现/诚信/引用 (INTEG) | major revision | REPRO-1 (1) | CITE-1, INTEG-1 (2) | REPRO-2 (rejected) |
| ⑫ 数据规模/T=19 就绪 (SCALE) | major revision (未就绪) | — | T18-2, T18-3, T18-4 (3) | T18-1 (rejected) |
| **合计** | **MAJOR REVISION** | **P0=0 / P1=10** | **P2=28** | **2 rejected + 1 mitigated** |

---

## 逐维度发现

> 下表仅列 verdict ∈ {CONFIRMED, DOWNGRADED} 的发现; 严重度 = `final_severity`。无对抗裁决 (verdict=null) 与被排除/化解者不在主表 (见附录)。

### ① IV — 因果识别·工具变量

**维度裁决: major revision。** IV 工程地基扎实 (双轨 full×ctx 红线被正确执行、各自 just-identified、严禁拼 Hansen J、benefit/25 是 GPSS §5 跨族 over-id 范本、locus/20 正确兼用同期+_lag1)。但"声明的稳健性/诊断"与"实际跑出的统计量"系统性脱节。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| IV-2 | **P1** (CONFIRMED) | 13+ 个 2SLS 模板 (25_tableA6:144 / collab21:126 / locus20:127 / substance22:131 / benefit25:162 / brokerage 11,17,18,19,23 …) | 模板脚注规定 KP F < Stock-Yogo 时改读 Anderson-Rubin 弱工具稳健 CI, 但全项目 `weakiv/condivreg/rivtest` **零命令调用** (唯一出现是散文举例)。自己命名了决策规则却不提供被指引的统计量。 | Andrews-Stock-Sun 2019 ARE; Lee et al. 2022 AER (tF); Stock-Yogo 2005 | 每个 over-id/弱工具风险列后加 `weakiv` 块 + `capture which` 守卫, esttab stats lockstep 加 AR CI; doctor 补 ado 检查。Stata-only/$0/golden-safe。 | high |
| IV-3 | **P1** (CONFIRMED) | iv_did.py:17-28,860-984 (diagnose_rotemberg 死函数); iv_extensions.py:30-46,202-237; 22_tableA3_bartik_iv 全 156 行仅报 KP F | 全项目 IV 识别声明走 GPSS 2020 "基期 share 外生性"单一视角, 却零 Rotemberg 权重诊断 + 零 high-weight share 的 pre-trend/placebo。`diagnose_rotemberg_weights` 仅 test 调用 (runner/pipeline 零调用), 是死函数。声称走 GPSS 路线却不交 GPSS §5 入场费。 | Goldsmith-Pinkham-Sorkin-Swift 2020 AER §5 | 新建 Bartik 诊断模板调 `bartik_weight` ado (capture which 守卫) 输出 Rotemberg 权重表 + 对 top-权重 share 跑 pre-period placebo; 论文补基期 share 与 T0 显著性相关性披露。Stata-only/$0/golden-safe。与 MEDIA_ATTENTION ID-4 字节级一致。 | high |
| IV-1 | P2 (DOWNGRADED, 原 P1) | iv_extensions.py:126,183-191 (_lag1 物化); substance22:105/128, collab21:100/123, benefit25:135/159 (addnote 承诺 lag1 列但表里无 eststo) | 反射问题解药 `_lag1` 已全员物化, 却只有 locus/20 实跑, 其余 6 篇用同期 peer-LOO 做主工具 (Manski 反射对象); 且 3 处 addnote 白纸黑字承诺 lag1 稳健列但模板无该 eststo (导出还会被改名 `l1o_peer_*_iv_lag1`)。 | Manski 1993 REStud; Leary-Roberts 2014 JF | 补报已脚注的 lag1 稳健列 (镜像 locus/20), 或与同期版并列并以 _lag1 为 preferred。同期 peer-mean IV 带 year-FE+LOO+披露本身是 JF 可发表做法。 | high→med |
| IV-4 | P2 (DOWNGRADED, 原 P1) | iv_extensions.py:113-118 (group_col='bank_type'); bank_addresses.json (rural 1563 / 6 NFRA 类) | type-LOO peer 与 Bartik 按 6 类极偏斜分组 (rural 88%), year-FE 吸收后识别变异塌缩为 few-effective-groups。**但**仅 6/11 篇真用 type 基 (P1 用 31 省、benefit 有 zone fallback); KP F/N/AR-CI 已在每模板报齐, 仅 Rotemberg 集中度缺 (=IV-3)。 | GPSS 2020 few-share; Stock-Yogo 2005 | P3/P4 比照 P1/benefit 把 prov/zone LOO 升为并排主工具 + 补 Rotemberg ado (IV-3)。 | med |
| IV-5 | P2 (DOWNGRADED, 原 P1) | attention paper_spec.yaml:98-100 (承诺 Hansen J + corr/VIF); 19_attention_iv_first_stage:41-88 (三块各自 just-identified, 无 pooled) | spec 承诺 LOO×Bartik 跨族 over-id 解 P1-6 恰好识别 → Hansen J, 但模板从不跑 `(MAIN_TREAT = LOO Bartik)` pooled 列, J 永不产出。benefit/25 sibling 已完整实现该模式。 | GPSS 2020 §5; Parente-Santos-Silva 2012 EL | 补 `tsls_overid` 列兑现 spec (镜像 benefit/25:108-130), 或修订 note 收回 over-id 主张改"两 just-identified 工具并排"。主识别 just-identified LOO + KP F 已有效, Hansen J 仅附加稳健性。 | high |

### ② DID — 因果识别·DiD/事件研究/政策冲击

**维度裁决: major revision。** "声明的方法学"与"实际估计量"严重脱节, 但均落在机制/证伪/附录层, 非头条因果。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| DID-1 | **P1** (DOWNGRADED, 原 P0) | falsification_template:776,783 (DDD); brokerage12:32-63 (dcep_post×L_btw); iv_did.py:677-714 (gvar 已物化); csdid 仅日志字符串 | 可跑的错时 cohort (dcep_/sandbox_, 2019/2020/2022) 只被 plain TWFE 消费 (Goodman-Bacon 负权重场景), csdid/did_imputation/bacondecomp 在任何 .do 估计行**零调用**。**但**这两处错时设定都非任一论文的主识别 (attention 主=cross_sectional_intensity_did; brokerage 主=roa+二阶 IV; tone DDD 是 14+ falsification 之一), 仅机制/证伪表。 | Goodman-Bacon 2021 JoE; Callaway-Sant'Anna 2021; dCdH 2020 AER; Borusyak et al. 2024 | 在错时块加 `csdid ... gvar() notyet method(dripw)` + `estat event` + `bacondecomp` (capture which 守卫), TWFE 仅作对照列并脚注披露 Bacon 权重。$0/golden-safe (列已在盘), T=2 优雅跳过、T=19 自动激活。 | high |
| DID-2 | **P1** (DOWNGRADED, 原 P0) | locus19:36-63 (eventstudyinteract 喂缺失列); attention15:78-87 (M6 capture confirm 静默跳过); 全 pipeline grep post_E/treat_E_year 零生产者 | spec 承诺的 E1-E5b 事件研究永久空壳: post_E*/treat_E*_year/never_treated_E* 零生产者 → 复现包跑出空表。**但**这是 appendix 平行趋势/稳健性补充, 非 headline。**且 finder 两处误判已订正**: collab/19 自建 INLINE event_t×collab_open 截面强度 DiD 可跑 (非同病); E1-E5b 是 SYNCHRONOUS 同步政策, 不该 cohort 化 (locus/19 该改 collab/19 式 INLINE intensity 写法)。 | Sun-Abraham 2021 JoE; AER/JF Data Availability Policy | 把 locus/19 与 attention M6 改接 INLINE intensity-DiD (镜像 collab/19), 或重指已存在的 dcep_/sandbox_ 列。与 MEDIA_ATTENTION P1-B 同。新列落盘须重生 golden。 | high |
| DID-3 | P2 (DOWNGRADED, 原 P1) | attention18:47-52 / substance18:29-31 / locus18:30-32 (honestdid 仅注释); locus19:52-70 (无实际 pre-trend test) | HonestDiD (Rambachan-Roth 2023) 仅以 `* honestdid` 注释存在, 从未运行; 且无任何一处真跑正式 pre-trend 联合检验。**但** substance baseline 是 within-FE 面板非 DiD (不适用); 真正核心对象仅 P4 locus; 且它是建立在尚未运行的事件研究 (DID-2/P1-B) 之上的下游稳健性层。 | Rambachan-Roth 2023 RES; Roth 2022 AER:Insights | 先接线事件研究 (DID-2), 再把注释化的 honestdid 改为估计行 + 补正式 pre-trend 联合 F。并入同一事件研究 reconcile。$0/golden-safe。 | high→med |
| DID-4 | P2 (DOWNGRADED, 原 P1) | iv_did.py:633-642,779-799 (HQ-based 披露); 各 18_* 已有 excl_soe/excl_rural 列 | DCEP/Sandbox 处理 HQ-based + never-treated 趋空, 已自我披露但估计层未落实 notyet。**但** finder 两项诉求事实错误: 当前无任何模板调用 csdid (notyet 指向空集); soe/rural 子样本列**已存在** (attention18:114 / substance18:79,82 / locus18:79,82 进 esttab 白名单)。是 P1-B 子集。 | Callaway-Sant'Anna 2021 §6.1; dCdH 2020 AER | csdid 接线时 (DID-1) 一律加 notyet; 把 HQ-based 局限提升为政策 DiD 表脚注。列已在盘。 | high |

### ③ SENT — 测度·情感构念效度

**维度裁决: major revision。** 算分内核 (κ/prob_score/herd/VW-MW-HW 分母) 已被多轮证伪为干净, 不再是 finding。残留为【构念—数据】层。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| CV-1 | **P1** (DOWNGRADED, 原 P0) | encode.py:539 (llm_vote_tone=mean); 24_herd_decay.parquet (验证篇 正798/中33/负2=0.24%); llm_bias_diagnostic_full.csv | 主因变量 llm_vote_tone 负面类近乎退化 (盘上验证篇负面 0.24%, 三模型 0–0.6%), 双极"情感"实为单极正向倾向, 且 codebook/spec/任何审计零披露。中文银行新闻 PR-positive 语料伪迹 + LLM 乐观偏置, T=19 不会反转。**但** tone 变异不必来自负类 (正面 vs 中性边际 + 连续 prob_score std=0.23 仍有可观变异), 系数仍可解释为 favorability/optimism。 | Loughran-McDonald 2011 JF; Tetlock 2007 JF; King-Zeng 2001 | (a) codebook/.dta 标签 + spec measurement 节披露类别先验 + "负面近退化、tone 应解读为正向强度"; (b) 把构念主张从"情感"收敛为"正向报道倾向/乐观度"; (c) 报告负面子样本零方差诊断。$0 披露/framing, 不重生 golden。 | high |
| CV-2 | P2 (DOWNGRADED, 原 P1) | sentiment_cross_method_full.csv (LLM-词典 ρ=0.16 / LLM-BERT ρ=0.21); tone_validation.py:1895-1901 (收敛≠构念效度已落地) | 三法收敛效度对主测度很弱, 项目称"triangulation robustness battery"。**但** finder 范式套用错误: spec 明确 framing 为 Tetlock/L&M robustness battery (检验下游回归对替代测度稳健), 非 Campbell-Fiske MTMM 收敛。L&M 2011 范式下分歧测度产生一致结论是优点。前轮 measurement audit finding④ 已 CONFIRMED 落地修复措辞。 | L&M 2011 JF; Gentzkow-Kelly-Taddy 2019 JEL §3; Campbell-Fiske 1959 | 论文如实报告跨方法相关矩阵 + 脚注解释为构念差异/噪声; 撤回"triangulation 支持构念效度"措辞。$0/golden-safe, 不动面板值。 | high |
| CV-3 | P2 (DOWNGRADED, 原 P1) | encode.py:539 (离散 vote 均值) vs :901 (avg_llm_prob_score); 21_tableA2:64 (无连续 DV 稳健性) | 主 DV 用离散 3 点投票均值而非已物化的连续 prob_score; Shapiro 2022 衰减偏误原理被引却未据此选/补主 DV。**但** finder 放大器证伪: corr(离散, 连续)=0.66 (文章级)/0.77-0.84 (bank-year), 连续测度 89-96 唯一值 (非"近退化"); llm_vote_cont 已进 P1 Table 1。 | Shapiro-Sudhof-Wilson 2022 JoE; GKT 2019 JEL; Xiong et al. 2024 ICLR | (a) measurement 节说明主 DV 为离散投票均值理由; (b) 接线 avg_llm_prob_score 作稳健性 (列已在盘, golden-safe)。 | high→med |

### ④ ATTN — 测度·注意力/文本构念效度

**维度裁决: major revision。** 构念—声称匹配在【披露层】扎实 (attention_index 的 Fang-Peress extensive 加权而非 Hassan intensive 已三处一致披露)。残留为构念效度硬伤。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| CV-1 | P2 (DOWNGRADED, 原 P1) | tone_validation.py:1-16 (仅情感轨); attention_media.py:469-480; encode.py:716-726 (salience 列全物化但孤立) | 注意力指数族零内部/外部效度检验, 引 DEG 2011 (核心贡献正是注意力代理对照基准验证) 却没做; salience 基准列已全物化但从未与 attention_index 做收敛核验。**但** 与 MEDIA_ATTENTION P1-C 重叠 (违不重复律); 且 salience 基准与 attention 同源文本计数, 高相关只证内部一致 (类 Cronbach α), 非 DEG 意义的 criterion validity (需独立于媒体的 turnover/收益)。 | DEG 2011 JF; Fang-Peress 2009 JF; Hassan 2019 QJE | 产 attention_index 与已物化 salience 输入的 bank-year 相关矩阵作内部 nomological 证据; 外部 criterion 留待财务/外部数据 (P1-C)。$0/golden-safe。 | high→med |
| CV-2 | P2 (DOWNGRADED, 原 P1) | attention_media.py:399-403,440; attention paper_spec.yaml:50 (secondary); 18_attention_robustness:129-136 (未控 n_outlets) | attention_disp (outlet-HHI) 在低覆盖 bank-year 机械=1, 混淆"集中度"与"低覆盖量", 回归未控 n_outlets; T=19 长尾/早期年份仍大量单 outlet, 不随 N 消失。**但** disp 是 secondary/robustness 测度 (非主处理), codebook 已披露"单 outlet=1"并列 n_outlets 为诊断列。 | Cookson-Niessner 2020 JF; HHI 小 N 退化 | disp 进回归时强制控 ln(n_outlets)/n_fintech_articles, 或仅 n_outlets≥3 子样本; codebook+spec 补"低覆盖机械产高 HHI"披露。$0 (n_outlets 已在盘)。 | high |

### ⑤ SAMPLE — 样本宇宙/选择偏误

**维度裁决: major revision。** verified 域门控地基健全 (ATT-1 firm-level 已正确 semi-join), 但样本宇宙构造层有真硬伤; 多条与 MEDIA_ATTENTION 重叠且严重度经复核下调。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| SU-1 | P2 (DOWNGRADED, 原 P1) | encode.py:1837 (脊柱=covered-banks-unique); news_bank.py:117 (Aho-Corasick 扫全 18.2M); figures.py:33-78 (已披露 conditional on ≥1 article) | 面板脊柱 conditional-on-coverage, 丢弃名册约 95% 从未覆盖银行。**但** finder 三重证伪: ① 不是"管线丢弃名册"而是"数据 0 提及"(全 1767 名册经 AC 自动机均有匹配机会); ② "现盘 87 家=5%"是 T=2 试跑数 (违禁用试跑数判缺陷); ③ "conditional on ≥1 article"限制已在 figures.py 显式披露。Heckman 排除限制不可识别 (村镇行 0 提及无 outcome)。 | Heckman 1979 ECMA; Wooldridge 2010 Ch.19 | 显式样本限制声明 (已有) + 被剔除集的 tier/规模构成表。拒绝 Heckman 分支 (无有效工具)。$0 分析层。 | high |
| SU-2 | P2 (DOWNGRADED, 原 P1) | attention_media.py:561-562,657 (geo 注意力未门控) vs 376/395 (firm-level 已门控); docstring 320-323 (ATT-2 deferred) | geo 注意力族 ft_attn_*/ft_vol_* 仍未门控, 含约 26.8% LLM 判伪文章。**但** finder 隐去了 MEDIA_ATTENTION 终裁: 已下调 P2 (仅喂 Table 1 描述性行, 有 year-FE 吸收脚注, 不喂任何 IV/回归系数); "升级为污染 IV"是假设性的 (实际 Bartik shift=已门控的 fintech_intensity, geo 列结构上非 article-level shift 候选; 实际 geo IV=prov/city LOO tone 非 attention)。 | Fang-Peress 2009 JF; GPSS 2020 AER | geo-IV 激活前镜像 ATT-1 门控 (仅门控分子) 作 wire-ahead; 当前仅需 Table 1 脚注注明门控不对称。改列值须重生 golden。 | high |
| SU-3 | P2 (DOWNGRADED, 原 P1) | dedup.py:364-405 (lsh.query 簇直删无真 Jaccard 复核); :116 (fallback 0.85); git: 28b4ab93 非 HEAD 祖先 | 本分支生产 dedup 缺 main 已合并的 N4 pairwise-真-Jaccard 复核, LSH 传递过删非随机下偏计数测度。**但** N4 修复实测过删 = 9427 集仅 1 篇 (~0.01%, 单向); 且修复在 origin/main 也未应用到产物 (盘上 00_preprocessing=06-05 早于 N4), 本分支产物与 origin/main 字节一致 → 纯源码 rebase 卫生问题。MEDIA_ATTENTION DI-1 钉为 item7 P3 hygiene。 | Bushee et al. 2010 JAR; Wooldridge 2010 Ch.19 | cherry-pick/rebase 28b4ab93 到本分支 (勿重实现), golden 在生产 dedup 重跑后重生。 | high |
| SU-4 | P2 (DOWNGRADED, 原 P1) | dedup.py:331,287-289,234 (全 18.2M 单 in-RAM MinHashLSH); runner.py:443-445 (裸调用) | 18.2M 去重无分块/无 OOM 守卫。**但** finder 的 P1 支柱"OOM→静默采样→破坏 golden 确定性"被代码证伪: 唯一调用方裸调用, 无 try/except/sample/nrows; OOM 在 Python 是 MemoryError 硬崩 (loud), 无任何降级采样路径。可复现性/Heckman 论证是范畴错误。 | AEA Data Editor policy | 移植 article_staleness 的 per-day 窗口 + 加输入/输出行数断言。生产前工程前置, 两份审计已披露为 P3 hygiene。golden-safe。 | high |
| SU-5 | P2 (DOWNGRADED, 原 P1) | attention_media.py:564,670 (ft/total 比值); detect_defacto_cessation:45-130 (仅退出代理); 主规格 15:54-55 absorb year | 比值测度跨 19 年构成漂移无专门审计 (无 entry/wire-ratio/篇均长度/分时代表)。与 MEDIA_ATTENTION 头号 P1-A 一字对应。**但** 主规格已 TWFE 含 year_fe, 完整吸收银行间共同的水平漂移 (标题主打的"水平不可比"被 year FE 差分掉); 残存的仅是与横截面交互的构成漂移, 加 IV 后是披露/稳健性附录而非识别崩塌。 | Gentzkow-Shapiro 2010 ECMA; Baker-Bloom-Davis 2016 QJE | 逐年 outlet entry/exit + wire-ratio + 分时代 (2007-12/2013-18/2019-25) 稳定性表 + data 段披露 + 限识别窗 post-2013 子样本。$0/golden-safe。⚠ 注: 项目权威审计仍按 P1 列 (评的是全 attention 论文族横切聚合后果, 与单条 finding 可拒稿性口径不同, 二者不矛盾)。 | high |

### ⑥ XYEAR — 跨年可比性/结构断裂

**维度裁决: major revision。** 比值/强度测度族在 T=19 上系统性跨年不可比, 是顶刊对长面板媒体测度的硬要求且当前几乎全漏。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| CY-2 | **P1** (CONFIRMED) | attention18:118-121 (excl_pre year>=2013); 33_tableA9:97-204 (仅 hub/size 切分); Bai-Perron/Chow/sbsingle 全树零命中 | 全代码库无结构性断点/分时代稳定性检验; 唯一时间维稳健性 excl-pre2013 是 era-stability 的反面 (假设跨时代不变并验"去早期仍成立")。2007-2025 跨 2013 余额宝/2016 P2P/2019 DCEP 多 regime, pooled intensity-DiD 若关系断裂会把异质效应平均成有偏均值。**修正**: 2 provisional 篇 (disagreement/clarity 13_table4) 已有 4 分时段 regime 面板可直接移植; Bai-Perron 对面板 DiD 非硬要求, 真要求是分时代系数稳定性表 + treatment×era 交乘。与 P1-A 高度重叠。 | Bai-Perron 1998 ECMA; Hansen 2001 JEP | 新增 era-stability 模板 (三时代分段回归 + era 交乘 + Wald 相等性检验); 主 DV 跑 estat sbsingle/sbknown (可选)。capture which 守卫, golden 零影响。 | high |
| CY-1 | P2 (DOWNGRADED, 原 P1) | attention15:7,45-56 (主处理=attention_index_full); attention_media.py:419 (log-sum 非比值); geography.py:242-269 (_z 白名单仅情感族) | 注意力比值族无时变基准归一化, 却对情感语调族已施加 Fama-MacBeth 年度标准化 (称"选择性遗漏")。**但** 两根承重柱误读: ① attention 主处理是 attention_index_full=log-sum (非比值), ft_attn_yr/fintech_share 在任何回归中均非主处理; ② 情感主回归 DV 也用原始列非 _z (_z 是可解读性辅助孪生, 非跨年可比修正), 不存在"选择性"对比。ft_attn_yr 为 year-const 已被 year-FE 吸收且 tables.py 披露。 | Fama-MacBeth 1973 JPE; BBD 2016 QJE; GSS 2011 AER | 与 P1-A 同 substance 的语料构成漂移诊断表 + data 段一句披露。$0/golden-safe。 | high |
| CY-3 | P2 (DOWNGRADED, 原 P1) | fintech_intensity.py:247-380 (W_i=IDF_i×CosSim 单一池化常量, 时不变); 各规格 absorb(bank_id year) | 称 IDF 在全 18 年合并语料算一次把跨年词频漂移"焊进"测度。**但核心机制断言事实错误**: 固定 IDF 是时不变权重, 相同 TF/长度文章无论哪年得逐字相同分数 → 固定 IDF 恰是最可比的 text→score 映射 (非"焊进漂移"); finder 把 GKT 2019 §2.2 标准引反了 (该标准本身要求 IDF 在全参考语料计算); year FE 吸收年度尺度位移。 | GKT 2019 JEL; L&M 2011 JF | method 段披露池化 IDF + 指向年标准化; 年度 IDF 孪生列为 nice-to-have。$0 披露层 (P2)。 | high |

### ⑦ INFER — 推断·聚类/多重检验 FWER

**维度裁决: major revision。** 核心算法层正确 (geography 三档聚类、benefit wild bootstrap、brokerage 22 中心度 wyoung battery、agg_robustness 双向 cluster+boottest)。残留在 FWER 覆盖与 small-G 推断。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| IV-3 | **P1** (CONFIRMED) | derivative_replication.py:125 (CLUSTER_VAR=prov_id); brokerage11:33-34,54-60 (主 2SLS 省级聚类无 G<50 脚注/无 boottest); brokerage12:36-63 (政策 DiD cluster prov_id 无 bootstrap); brokerage21:101 (唯一 boottest 写死 cluster(bank_id) 大 G 层) | brokerage 主 2SLS (G≈31) 与 DCEP/Sandbox 政策 DiD (few-treated-clusters) 在省级聚类但主规格无 wild/subcluster bootstrap; 唯一 boottest 跑在不需要的 bank_id 大 G 层, 恰恰避开真正需要小 G 修正的省级层。 | Cameron-Miller 2015 JHR; MacKinnon-Webb 2017/2018; Conley-Taber 2011; Roodman et al. 2019 | 主 2SLS+政策 DiD 补 `boottest <treat>, reps(9999) bootcluster(prov_id) cluster(prov_id)` 并把 wild p 进表; 错时披露 G_treated, 极小时改 ritest/Conley-Taber; 把 agg_robustness 的 boottest 从 bank 改到 prov 层。Stata/$0/golden-safe。与 MEDIA_ATTENTION ID-5 同。 | high |
| IV-1 | P2 (DOWNGRADED, 原 P1) | attention18:44-45 / substance18:26-27 / locus18:27 (rwolf 全注释); 唯一活跃=brokerage20:68 (wyoung); attention18:162 (脚注称 supplemental log 但 rwolf 从未运行) | 测度农场全族零 FWER 校正, rwolf 在 attention/substance/locus 全被注释 (claimed-but-never-run), 误导性 supplemental-log 脚注。**但** 本项目最权威同主题审计 (80-agent) 已把完全相同 finding 归入 P2 must-fix (FWER 不在其三个 P1 内); 每篇有单一预设主 DV×主处理, 替代测度/加权是 robustness 非 co-equal headline; 双轨是"互为稳健性"高相关孪生非独立假设。 | Romano-Wolf 2005 ECMA; Westfall-Young 1993; List-Shaikh-Xu 2019; Anderson 2008 | 把 rwolf 从注释转活跃, 或移植 brokerage/20 wyoung battery; 异质性/多测度族加 FWER 校正后 p 进 esttab。$0/golden-safe。 | high |
| IV-2 | P2 (DOWNGRADED, 原 P1) | 9 篇 spec 全无 cluster 块 (仅 disagreement 有); attention spec 列 primary+3 secondary | 8 篇已编码论文 spec 零 cluster 块、零 PAP/单一主假设声明。**但** finder 误读: 每篇 spec 已显式声明 treatment.primary/outcome.primary (单一) + secondary 标 robustness = 事实层 confirmatory vs exploratory; 缺的是形式化 family 定义而非"毫无纪律"; List-Shaikh-Xu/Olken 是 RCT 预注册标准, 顶刊对观测性研究不强制 OSF/PAP。与 ID-5/FWER 重叠。 | List-Shaikh-Xu 2019 EE; Olken 2015 JEP; Romano-Wolf 2005 | 每篇 spec 增 `inference:` 块声明单一 confirmatory 主规格 + family 定义 + 其余标 exploratory; 镜像 disagreement spec 加 cluster 块。$0/spec 层。 | high |

### ⑧ ROBUST — 稳健性 battery 完备性

**维度裁决: minor revision。** battery 整体完备且做工扎实 (FE 饱和阶梯 / qreg-rreg / Oster δ / 子样本-lead 安慰剂 / PPML / 缩尾敏感性 / EW-VW-MW-HW / 双向聚类+wild bootstrap 均已落地并接进 10 master)。任务首要关切 Oster psacalc mcontrol 误用已在 attention/20、collab/23、strategic/16、substance/24、benefit/26、llm_peer/16 全部正确修为 materialized year-FE 哑变量。**本维度的 RB-1..RB-5 (rreg 静默吞列/Oster estadd-after-restore/HonestDiD 注释脚手架/benefit 头注 stale/brokerage Oster factor 未实测) 均未提供对抗裁决 (verdict=null)**, 故按规则不计入确认级。它们是 referee 会注意到的"声称做了却没出现"的一致性瑕疵, 修复路径已在姐妹模板中现成存在, 建议作为 minor revision 整改清单 (详见附录 B)。

### ⑨ SPEC — 计量设定/坏控制

**维度裁决: major revision。** 多数论文 FE/估计设定符合顶刊范式, 残留三类设定问题。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| IV-1 | **P1** (CONFIRMED) | benefit11:39-70 / benefit14:36-93 (全表 absorb(bank_type year)); paper_spec.yaml:48 (承诺 bank_fe); 01_data_prep:14-15 (真 bank_id 存在); 原始作者 do 全程 absorb(bank_id year) | benefit_society 主表与全部稳健性表用 bank_type FE (~4-7 类) 而非 spec 承诺的 bank_fe, 把所有时不变行级混淆 (规模/商业模式/地域, 均与媒体态度相关) 留在误差。spec/实现/原始 do/同组合其余 10 篇四重不一致。treatment=benefit_mean_full 与时不变行级特征高度相关。非 T=2 退化 (bank FE 在 T=2 也识别)。 | Gormley-Matsa 2014 RFS; Angrist-Pischke 2009 MHE §5 | 把 benefit/11 与 14 的 absorb(bank_type...) 全改 absorb(bank_id year), bank_type 降为粗粒度对照列。纯 Stata 模板层 $0/golden-safe。 | high |
| IV-2 | P2 (DOWNGRADED, 原 P1) | benefit spec:44-45 (CONTROLS=coverage 代理); strategic11:28,32,41 (fluidity/sim_max/coherence 入 RHS); strategic14:20-95 (备择各自单跑) | benefit/strategic 把媒体覆盖与文本派生量当控制。**但** 两半轻重悬殊: A 半 (benefit) 基本误读——benefit_mean 是逐文章态度均值 (强度边际), coverage 是覆盖总量 (外延边际), 研究语调效应时控覆盖量是 Tetlock/Fang-Peress 标准做法 (混淆变量非后处理中介); B 半 (strategic) 真但被高估——sim_max 与 strat_diff 同源机械互补, 但 Table 5 已各自单跑 (=修复 b), spec 已列为 alternative treatment。 | Angrist-Pischke 2009 MHE §3.2.3; Hoberg-Phillips 2016 JPE | 媒体覆盖代理论证为 pre-determined 混淆 (已 framing=visibility_confounder); strategic 把 sim_max 从主表同时规格降级 + 补 VIF/相关披露。$0/模板层。 | high→med |
| IV-3 | P2 (DOWNGRADED, 原 P1) | 11_table2_main_m1m6:16-26 (占位/方向相反自披露),109-135 (M4-M6 携 LOCUS/SUBST),141 (title "Main Results" 无 placeholder 脚注); tables.py 不消费 table2_main.csv | P1 主表 M4-M6 把同源 LLM 分类 frac (tech/symb) 当控制 (collider 候选)。**但** finder 误读"被 tables.py 消费有误引风险" (实读 P1 tables.py 只建 Table 1, 零引用 table2_main.csv); 本表 spec+模板已自披露为 pre-enrichment 占位, 财务列落地后重写为 funding_cost~tone 时 frac 自动出控制集; digital_frontier 实为基年新闻量切分 (collider framing 过度)。真有效内核=渲染产物标题"Main Results"无 placeholder 脚注, 外部研究者可能误引。 | Angrist-Pischke 2009 MHE §3.2.3 | 表头/脚注标 descriptive-placeholder + 财务接入后重写正向方程。$0/golden-safe。 | med |

### ⑩ PORT — 论文组合/贡献/salami

**维度裁决: major revision (组合层)。** portfolio-level least-publishable-unit 问题。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| SAL-3 | **P1** (CONFIRMED) | encode.py:890 (avg_ft_intensity_full=mean(fintech_intensity_score_full)); attention_media.py:419 (attention_index_full=ln1p(sum(同一信号))); llm_peer spec:22-30; derivative_replication.py:180 | llm_peer 新主 outcome (avg_ft_intensity_full) 与 P2 attention 的 treatment 同一底层 fintech 强度量 (mean vs ln(1+sum)), 把"同业语调→本行 fintech 战略响应"的 Y 设成同一媒体语料派生文本量, 反映共同覆盖因子而非真实公司行为; 违反 spec 自身锚定的 Leary-Roberts 2014 JF (Y=真实杠杆政策)。方法学篇尤须证 LLM-peer IV 对真实经济结局的增量识别力。spec 未披露与 P2 同源性。2026-06-13 outcome 重定位是用一个问题换了另一个 (新增未决项)。 | Leary-Roberts 2014 JF; Cao et al. 2025 RAS | 主 outcome 改回 real-economy 财务/创新结局 (roa/ln_fintech_investment/patent), avg_ft_intensity 降为 first-stage 机制佐证; 或整体降为主线方法学附录。$0/golden-safe spec 层。 | high |
| SAL-1 | P2 (DOWNGRADED, 原 P0) | unified_cot.txt:84 (2³=8 cells); encode.py 同函数产 sub/tech/app/collab_frac; cell_id_full=subst*4+locus*2+collab+1 | P3/P4/P5 是同一条 LLM prompt 产出的 2³ 正交分类的三个维度, 切成三篇顶刊投稿。**但** P0 高估三证: ① 三篇 outcome 真不同 (P3 cost_income_ratio_change_3yr / P4 citation_weighted_patent / P5 m_and_a_fintech, 不同机制=反 salami 最强信号); ② 理论锚不同 (W&Z 脱耦 / Gomber-Goldstein-Jiang-Karolyi / Chesbrough); ③ finder keystone 证据 19_table6_cell_decomposition 只存于归档 v3_5_0/, 三篇 live master 零调用 cell_id。 | LPU 反对 (AER/QJE/JF/RFS 投稿政策); Angrist-Pischke 2009 MHE Ch.5 | portfolio framing + 跨篇互引 (minor 披露)。P5 collab 理论最弱, salami 风险相对高但不足以定 P0。$0/spec 层。 | high |
| SAL-2 | P2 (DOWNGRADED, 原 P1) | disagreement spec:39,58-59 + clarity spec:38,65-66 (primary_formula 字节级相同, "可同时跑") | 两 provisional 共享同一 outcome panel/z_score, spec 自承可同跑, 应合并。**但** 两篇均 status=new/卡 G0 (provisional, 无 manuscript), referee 无从拒未写的稿; 差异化站得住 (disagreement=cross-outlet variance RFS / clarity=single-text readability JAE, 不同构念/文献/IV/审稿池); 风险已 in-spec 治理 (SSRN 间隔/IV 互斥/minimize self-citation)。 | Cookson-Niessner 2020 RFS; Bushman-Williams 2012 JAE | 合并为一篇"Media Information Environment Quality and Bank Risk-Taking", 两测度作互补维度 + 联合 PCA composite。组合战略建议 (P2)。 | high |
| SAL-4 | P2 (DOWNGRADED, 原 P1) | benefit spec:22 (primary roa PAP 锁) + brokerage spec:24 (primary roa); 主线五篇主 DV 已零撞车 | benefit_society 与 brokerage_network 主 outcome 同为 roa, 与主线五篇共用同一识别骨架。**但** finder 框架在当前状态事实错误: 主线五篇无一以 roa 为 primary (P1 funding_cost / P2 ln_fintech_investment / P3 cost_income_ratio / P4 citation_patent / P5 m_and_a); finder 引的 REDUNDANCY v2 表是 2026-06-13 outcome 重定位前的陈旧快照。残余仅 benefit↔brokerage 两篇 roa 对内撞车, 但架构刻意把唯一性落在 treatment.primary 非 outcome。 | 一个 identification=一篇 (顶刊连贯纲领); Han et al. 2024 RFS | benefit/brokerage 论文明示 roa 共享纯属同纲领差异化卫星; brokerage 可改 sigma_roa/interbank_share 脱钩 (spec:31 已列)。$0/spec 层。 | high |

### ⑪ INTEG — 可复现/诚信/引用

**维度裁决: major revision。** 引用诚信经多轮修复已基本干净 (Hillert→RFS / Text-as-Data→Kelly 已订正且有回归测试守护; Hassan QJE qjz021 / Tetlock JF&RFS / Fang-Peress / Bushee DOI 全抽验正确)。残留为可复现自洽性 + 两处误引残留。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| REPRO-1 | **P1** (DOWNGRADED, 原 P0) | 40_panel_yearly.parquet mtime=06-10 vs 21=06-12 / 24=06-13 (+thr cols); test_panel_reproducibility.py 实跑 3 failed | 硬盘产物内部不自洽: 主面板比其上游 21/24 旧, 重跑 pipeline 用更新的 21/24 重建会改列集 → 与已提交面板及 golden 不匹配; reproducibility 闸门当前 RED。**但** P0 高估: ① 全部 parquet+golden 均 gitignore (复现包交付的是现导 .dta+原始数据+代码, golden 是内部 dev CI tripwire 非 AEA archival artifact); ② RED 是已披露的设计性过渡态 (golden 重生 deferred 到 M0 付费 stage-21 之后); ③ 尚未投稿。但投稿前必须闭合, 是 major-revision-blocking 过程闸门。 | AEA Data and Code Availability Policy; JF/RFS replication | 一次受控 run 重跑 45/46 + generate_golden_snapshot.py + 面板/golden/code 同 commit, 投稿前 freeze archival run; 此后禁单独重跑上游 stage 而不连带重建下游+重生 golden。 | high |
| CITE-1 | P2 (DOWNGRADED, 原 P1) | paper_spec.yaml:44 (误标 RFS + 杜撰卷页 33:4327-4373) / :267 / :275 / run_paper.py:84 / replication/README.md:53 / instantiate_paper_stata.py:113 | Cookson-Niessner (2020) 误标 RFS (正确=JF 75(1):173-228) 残留。**但** ① finder "全树仅 2 处"为假 (实读 6+ 处, 漏掉最严重的 spec:44 杜撰卷页); ② 全是开发者注释+YAML 元数据+replication README, 服务 provisional 第10篇 (无 manuscript/refs.bib), 误引未传播到任何 referee 可见书目; ③ 机器生成 SSoT (variable_codebook.json/codebook.py) 已全部正确标 JF。 | APA 7th; Cookson-Niessner 2020 JF DOI 10.1111/jofi.12852 | 覆盖全部 6+ 处改 JF, 尤其消除 spec:44 杜撰卷页; 扩展 test_citation_integrity 加 Cookson∉RFS 断言。$0/golden-safe。 | high |
| INTEG-1 | P2 (DOWNGRADED, 原 P1) | brokerage REPLICATION_README.md:3,13 ("IRB 授权"/"完整 panel 174 obs"/"1998 列"/"可立即投稿") | 复现包 README 用 IRB 描述新闻数据 + 把 T=2 试跑盘冒充"完整 panel"。**但** load-bearing 前提"呈给外部审稿人"为假: 该文件被 .gitignore (papers/**/*.md) 忽略永不分发, 是内部 scratch; 外部研究者拿到的是 build-replication 打包产物 (README 源=stata_templates/brokerage_network/README.md, 干净, 自动附 git commit hash+dirty 检测); 全仓 grep IRB/完整panel/可立即投稿仅命中此 1 个 ignored 文件。 | AEA/JF replication; ICMJE | 删 IRB 句/完整 panel/可立即投稿/硬编码列数, 或删此冗余 scratch 文件。$0 卫生层。 | high |

### ⑫ SCALE — 数据规模/T=19 生产就绪

**维度裁决: major revision (未就绪)。** 元层面占位态 + 上游工程可执行性。Stata MP 容量远未触顶 (clean bill)。herd_decay O(N²)→bucketing 与 DET-1 缓存覆盖证明已闭合。

| id | 严重度 | 位置 | 问题 | 顶刊标准 | 修复 | 置信 |
|---|---|---|---|---|---|---|
| T18-2 | P2 (DOWNGRADED, 原 P1) | tone_llms.py:36-37 (输入=14_fintech_intensity 非 raw 18.2M); :1687/708/725-735 (整帧+results_map+全量 real_tasks); 无 checkpoint/resume | stage 21 LLM 编排在大规模上一次性装载整帧+全部协程+results_map, 无 checkpoint/分片, 编排层 OOM 风险。**但** 行数事实错误: stage 21 读 fintech 子集非 raw 18.2M (REDUNDANCY v2 推荐生产配置=分层 ~1.5M); 审稿镜头错位 (工程非识别问题, reviewer 走暖缓存离线 run 跑产出 panel 子集, 永不重跑 18.2M); log_memory_usage 使 OOM 可观测非 silent。残留真问题=中档配置全量 real_tasks/results_map 内存压力 (上全量前 wire-ahead)。 | AEA/QJE/JF Data Policy; Christensen-Miguel 2018 JEL | 按 (bank 或日期窗) 分片流式 + 中途 to_parquet 增量落盘 + --resume + peak-RAM 断言。缓存全命中下逐位等价。 | high |
| T18-3 | P2 (DOWNGRADED, 原 P1) | dedup.py:287-308,331-345,234 (全 N MinHash 物化+单 LSH+全文拷贝); :52-55 (docstring 自承 O(N)) | dedup 全 18.2M 单次 in-RAM MinHash/LSH 无分块。**但** finder 算法类别误读: MinHash/LSH 本就 O(N) (非 herd_decay 的 O(N²), "镜像分块"是范畴错误); finder 援引为模板的 article_staleness 自身也把全 N MinHash 入 RAM; OOM 是硬 raise (非静默采样); 日期窗分块会改结果 (跨窗簇成员漏判)。MEDIA_ATTENTION DI-6 钉为 P3 hygiene。 | Christensen-Miguel 2018 JEL; Fang-Peress 2009 JF | 加内存基准 + 行数断言 + ≥1M 行确定性压测; N4 真-Jaccard rebase (28b4ab93, 已落地 main) 是独立项。生产前工程项。 | high |
| T18-4 | P2 (DOWNGRADED, 原 P1) | test_panel_reproducibility.py:166 (精确哈希无容忍); golden incomplete=True/missing 30a (=ndarray unhashable); network 3 列 BLAS-FP 漂移 | 全量 golden 重生是未演练的高风险一次性操作, 本机不可安全重生 (付费/联网/BLAS-FP/脏树误 bless)。**但** "incomplete→连 T=2 都没闭合"误读 (incomplete 唯一触发=30a emb ndarray unhashable, 30a 不在 repro parametrize, 对门禁零影响; 40/51 column_hashes 全覆盖); framing 错误 (golden 仅 dev 期防回归内部门禁, papers/.do 零引用, referee 永远看不到, 复现包交付=.dta+.do)。残留=repro 测试未排除 3 个 BLAS-FP 列 + 重生 SOP 未脚本化。 | Christensen-Miguel 2018 JEL; AEA Data Editor | repro 测试对 3 个 BLAS-FP 列建白名单/容差; 受控环境演练子样本全链重生 SOP 脚本化; 闭合 incomplete golden 的 30a (内部 CI/devops 卫生)。 | high |

---

## 跨维度横切根因

对抗复核后, 反复出现的系统性根因可归纳为五条 (按出现频次):

1. **"声明—实现"缺口 (claimed-but-not-run)** — 出现于 IV-2 (AR-CI 弱工具脚注无 weakiv)、IV-3 (GPSS 路线无 Rotemberg)、IV-5 (spec 承诺 Hansen J 无 pooled)、IV-1 (addnote 承诺 lag1 无 eststo)、DID-1/DID-2 (csdid/event-study 仅注释/喂空)、DID-3 (HonestDiD 仅注释)、INFER IV-1 (rwolf 全注释 + 误导性 supplemental-log 脚注)、INFER IV-3 (boottest 跑在错误层级)、ROBUST 全族 (rreg/Oster estadd 静默吞列)。**这是本项目最普遍、最易被 referee 复现识破的系统性病灶**: 模板脚注/docstring/spec note 描述了一套顶刊级方法学, 但对应估计行从未真正执行。修复几乎全是 $0/Stata 层把注释转活跃命令 + capture which 守卫。

2. **跨年构成漂移 (cross-year compositional drift)** — 横切 XYEAR (CY-1/CY-2/CY-3)、SAMPLE (SU-5)、ATTN (隐含)。比值/强度测度的分母在 2007-2025 量级暴涨+构成重组, 同一数字跨年含义不同; 全代码库无分时代稳定性/结构断点检验。year-FE 只吸收水平不吸收"含义漂移", 威胁全部 T=19 跨年识别。**这是单条 finding 视角多为 P2 (year-FE 已吸水平 + 主处理多为 log-sum 非比值), 但全 attention 论文族聚合后 (CY-2) 升为 P1**。

3. **未门控 / 选择性域不对称** — SAMPLE SU-1 (脊柱 conditional-on-coverage)、SU-2 (geo 注意力 ATT-2 未门控)、SENT CV-1 (负面类退化)、PORT SAL-3 (outcome 与 treatment 同源)。底层共性是"哪些观测/信号进了哪条管线"缺乏一致的、可披露的门控契约。多数已部分披露, 修复在 wire-ahead 门控 + framing 披露。

4. **FWER / small-G 推断缺失** — INFER IV-1/IV-2/IV-3。海量回归 (双轨×三法×四加权×多测度) 无跨族 Romano-Wolf/Westfall-Young 校正 (唯一活跃仅 brokerage 一处 wyoung); 省级/cohort 小 G 聚类无 wild/subcluster bootstrap (唯一 boottest 跑在不需要的大 G 层)。

5. **T=2 占位待重生 (元就绪度)** — SCALE T18-1 (REJECTED 但作为元前提保留)、INTEG REPRO-1、SAMPLE/ATTN 中所有"现盘 87 家/174 行"论据。**所有现有结果、golden 哈希、graceful-skip 守卫都建在 0.052% 试跑帧上; 全量 T=19 run 尚未执行**。这既是评判其他 finding 严重度时的"试跑假象"过滤器 (凡基于 T=2 数字判缺陷者一律下调), 也是投稿前必须闭合的协调式重生工序。

---

## 优先级修复路线图

> 排序原则: 先闭合元就绪度 (重生闸门) → 再接通声明—实现缺口 (识别/稳健性) → 再修设定/组合 → 最后披露/卫生。标注 $0/golden-safe/需生产重生。

### 阶段 0 — 元就绪度闸门 (投稿前硬前置)
1. **[T18-1 / REPRO-1, 需生产重生]** 一次受控生产 run (或 REDUNDANCY v2 §七 第一阶段分层子样本 ~200 banks × 2015-2024): 按 DAG 重跑 stage 45/46 重建 40/51 → `generate_golden_snapshot.py` 重生 golden → 确认 `test_panel_reproducibility.py` 全绿 → 面板+golden+code 同一 commit。投稿前 freeze archival run, 此后禁止单独重跑上游 stage 而不连带重建下游。
2. **[T18-4, devops]** repro 测试对 3 个 BLAS-FP 网络列建白名单/数值容差; 重生 SOP 脚本化; 闭合 incomplete golden 的 30a (ndarray unhashable)。

### 阶段 1 — 接通"声明—实现"识别/稳健性缺口 (绝大多数 $0/golden-safe/Stata)
3. **[IV-2, P1, $0]** 每个 over-id/弱工具列后加 `weakiv` 块 + AR CI 进 esttab stats; doctor 补 ado 检查。
4. **[IV-3, P1, $0]** 新建 Bartik 诊断模板调 `bartik_weight` ado 输出 Rotemberg 权重 + top-share pre-trend placebo。
5. **[DID-1, P1, $0]** 错时块加 `csdid ... gvar() notyet` + `estat event` + `bacondecomp`, TWFE 降为对照列 + Bacon 权重脚注。
6. **[DID-2, P1, 需重生]** locus/19 + attention M6 改接 INLINE intensity-DiD (镜像 collab/19) 或重指 dcep_/sandbox_ 列。
7. **[CY-2, P1, $0]** 新增 era-stability 模板 (三时代分段 + era 交乘 + Wald), 移植 disagreement/clarity 13_table4 的 regime 面板。
8. **[INFER IV-3, P1, $0]** brokerage 主 2SLS+政策 DiD 补 `boottest bootcluster(prov_id)`, 错时披露 G_treated, agg_robustness boottest 从 bank 改 prov 层。
9. **[IV-5 / IV-1 / DID-3 / DID-4, P2, $0]** 补 attention pooled over-id 列; 补 lag1 稳健列; 接线事件研究后补 HonestDiD + pre-trend F; csdid 加 notyet。

### 阶段 2 — 计量设定 / 组合 (spec/Stata 层)
10. **[SPEC IV-1, P1, $0]** benefit/11 + 14 的 absorb(bank_type)→absorb(bank_id year), bank_type 降对照列。
11. **[PORT SAL-3, P1, $0]** llm_peer 主 outcome 改回 real-economy 结局 (roa/ln_fintech_investment/patent), avg_ft_intensity 降 first-stage。
12. **[PORT SAL-1/SAL-2/SAL-4, P2, $0]** portfolio framing + 跨篇互引; 考虑 P3/P4/P5 合并与两 provisional 合并; benefit/brokerage roa 共享明示为差异化卫星。

### 阶段 3 — 构念效度 / 披露 / 卫生 (纯披露层 $0)
13. **[SENT CV-1, P1→披露, $0]** codebook/.dta/spec 披露负面类近退化 + 构念收敛为 favorability/optimism + 负面子样本零方差诊断。
14. **[INFER IV-1/IV-2, P2, $0]** rwolf 转活跃 / 移植 wyoung battery; 每篇 spec 增 `inference:` 块 + cluster 块。
15. **[CITE-1 / INTEG-1, P2, $0]** Cookson-Niessner 全 6+ 处改 JF (含消除 spec:44 杜撰卷页); 删/修 brokerage scratch README 的 IRB/完整 panel/可立即投稿措辞。
16. **[其余 P2 披露, $0]** CV-2/CV-3/ATTN CV-1/CV-2/SU-1/SU-2/CY-1/CY-3/SPEC IV-2/IV-3 的披露与稳健性补列。

### 需生产重生 (golden 重生) 的子集
- DID-2 (新事件研究列)、SU-2 (geo 门控改列值)、CY 比值年标准化、IDF 时变孪生、benefit 脊柱/列值。这些与阶段 0 的协调式重生合批执行, 避免多次 golden bless。

---

## 附录 A: 已复核排除 (REJECTED) 与已化解 (ALREADY_MITIGATED) 项

> 以下经对抗复核被推翻或确认已修复, 不计入确认级缺陷; 简列理由。

| id | 维度 | 原报严重度 | verdict | 一句话理由 |
|---|---|---|---|---|
| REPRO-2 | INTEG | P1 | **REJECTED** (→P2 文档披露) | 根因误判: 3 网络列漂移源不是 BLAS 多线程 FP, 而是 PYTHONHASHSEED; core/stage.py:209 已对每个 stage 子进程强制 `PYTHONHASHSEED=0` (有专测守护), 实测固定后三列字节级一致 → "逐位复现按构造不可能"为假。残留仅 README 未说明须经 orchestrator 运行 (P2)。 |
| T18-1 | SCALE | P0 | **REJECTED** (→none) | 不是缺陷而是项目披露最充分的已知状态 (CLAUDE.md 多处明文 T=2 试跑 + 专门 memory); golden 自标 incomplete/baseline-pre-restructure 是回归门禁非估计样本认证; 仓库零 manuscript 把 T=2 当投稿结果; "投稿前跑生产 run"是通用前置非本库可定位缺陷。其可操作子项已各自单列。 |
| CV-4 | SENT | P1 | **ALREADY_MITIGATED** (→P2 待办) | 情感主测度零 criterion validity 属实且顶刊会问, 但: ① 非新缺陷 (MEDIA_ATTENTION P1-C/GOLD-1 已逐字登记为未决 P1, 重提违不重复律); ② referee 会阻断的"方法间一致冒充构念/效标效度"已被前轮 measurement audit CONFIRMED 落地修复 (tone_validation.py:13-16 免责声明 + gold_source 门控 + fail-close); ③ 残余=抽 300-500 篇双盲人工标注的研究执行任务, 已正确标 pending; ④ 主 DV 是 ctx 轨 (α=0.7724 过 Nunnally), 0.69 是次轨。 |

## 附录 B: 无对抗裁决 (verdict=null) 的发现 — 不计入确认级, 供整改参考

> 这些 finding 未提供 verdict 字段, 按任务规则不采信为确认级 (不计入 P0/P1/P2 计数)。但多为 referee 会注意到的一致性瑕疵, 修复路径多已在姐妹模板中现成存在, 建议作为 minor revision 整改清单参考。

- **IV 维**: IV-6 (brokerage 11/17 在生产机 ivreghdfe r301 下无 ivreg2 回退→静默 exit 199, 建议镜像 llm_peer/11 的 capture noisily+回退)、IV-7 (geography.py G-08 日志推荐 llm/dict/bert 三套同源 LOO 拼 Hansen J=近共线陷阱, 建议改日志文案)、IV-8 (outlet-composition IV 排他性论证单薄, 须控 media volume exposure)。
- **DID 维**: DID-5 (30_figure1/collab19 头注引 Sun-Abraham 实跑 plain TWFE, 头注—估计量不一致)、DID-6 (lead/lag 硬编码 ±3, T=19 浪费功效且 4plus binning 列成死列)。
- **SENT 维**: CV-5 (3 异构模型 temp=0 投票引 Wang 2023 self-consistency=单模型多采样, 引文与代码未对齐)。
- **ATTN 维**: CV-3 (hard_char 常用字集由 jieba 词频自指派生而非官方《通用规范汉字表》)、CV-4 (specificity_index 把 Hope-Hu-Lu 企业自我披露构念跨主体迁移到媒体报道无验证)、CV-5 (within_doc_redundancy_han 与字符版 corr≈0.99 仍作独立面板列=variable-farm 暴露)、CV-6 (rare_word_ratio 实测覆盖 57% distinct 词=非高频词率而非低频 20% 尾部, 构念—名称错配)。
- **SAMPLE 维**: SU-6 (无年份越界校验, 单条畸形日期给每家银行造幻影年)、SU-7 (media cessation 排除集把未经 NPPA 证实的 suspected 全量纳入, 须 confirmed-only 双口径对照)。
- **XYEAR 维**: CY-4 (geo 指数 min_articles=5 阈值时间不变→逐年样本选择漂移)、CY-5 (spec 把 year-FE 当跨年可比充分防御)。
- **INFER 维**: IV-4 (全组合 headline 单向 bank 聚类, 双向仅在附录; coded 篇单向 vs provisional 篇双向不一致)、IV-5 (省/市级聚类升级时空字符串 bank_province 被 Stata 静默剔除→跨层级样本不一致)、IV-6 (省级+市级 LOO 同信号嵌套地理聚合作 Hansen J over-id=零功效)。
- **ROBUST 维**: RB-1 (rreg 离群稳健列在 locus/22、llm_peer/16、brokerage/22 三处被 capture 静默吞掉, factor/dummy-trap 修复未跨篇传播)、RB-2 (locus/22 Oster δ 用 estadd-after-restore, stats 行静默空白)、RB-3 (18_* HonestDiD/Romano-Wolf 仍注释脚手架)、RB-4 (benefit/26 头注 mcontrol($controls) 与已修代码矛盾)、RB-5 (brokerage/22 Oster 受控回归含 i.year factor, psacalc 解析未实测验证)。
- **SPEC 维**: IV-4 (P4/P5 计数 outcome 主表仍线性 reghdfe, PPML 仅附录)、IV-5 (M5 +macro 在 year FE 下与 gdp/m2 共线被 drop 且缺列静默复用 M4)、IV-6 (P3 主 outcome 3 年前向变化损末 3 年样本 + M6 同表切换 DV 违反 progressive-spec)、IV-7 (P4 layer+scenario 同源二元指标同列需 VIF/共线披露)。
- **PORT 维**: SAL-5 (outcome 重定位后部分新主 outcome 与理论锚自洽性偏弱: P4 结构对仗、P3 t+3 尾部、strategic tobin_q 上市子样本与 n_bank_min 不符)、SAL-6 (11 篇 outlet 高度集中 RFS×5/SMJ-ASQ×2, 同源数据并发投同一审稿池放大 self-plagiarism 暴露)。
- **INTEG 维**: AIDISC-1 (LLM 经第三方聚合器+非快照模型名, 复现仅靠 407MB 不可分发缓存, 披露未说明此限制)、AIDISC-2 (AI 披露把"代码辅助"与"LLM-as-测量"混为一谈, 后者所需人工金标准当前为空)、REPRO-3 (Data Availability "available upon request" 低于 2019+ AEA 标准)、CITE-2 (清白核验: Hillert/Text-as-Data 两处误引已订正且有回归测试守护, 勿重做)。
- **SCALE 维**: T18-5 (LLM 计费基覆盖含 ~57% 非 fintech 篇, relevance 预筛缺位)、T18-6 (clean bill: Stata MP 容量远未触顶, 瓶颈在上游吞吐与重生而非分析层)。

---

## 顶刊标杆文献清单

**工具变量 / shift-share 识别**
- Manski, C. (1993). "Identification of Endogenous Social Effects: The Reflection Problem." *RES* 60(3): 531-542.
- Leary, M. & Roberts, M. (2014). "Do Peer Firms Affect Corporate Financial Policy?" *JF* 69(1): 139-178.
- Goldsmith-Pinkham, P., Sorkin, I. & Swift, S. (2020). "Bartik Instruments: What, When, Why, and How." *AER* 110(8): 2586-2624.
- Borusyak, K., Hull, P. & Jaravel, X. (2022). "Quasi-Experimental Shift-Share Research Designs." *REStud* (对比视角).
- Parente, P. & Santos Silva, J.M.C. (2012). "A Cautionary Note on Tests of Overidentifying Restrictions." *Economics Letters*.
- Andrews, I., Stock, J. & Sun, L. (2019). "Weak Instruments in IV Regression." *Annual Review of Economics* 11: 727-753.
- Stock, J. & Yogo, M. (2005). "Testing for Weak Instruments in Linear IV Regression."
- Lee, D., McCrary, J., Moreira, M. & Porter, J. (2022). "Valid t-ratio Inference for IV." *AER*.

**DiD / 事件研究**
- Goodman-Bacon, A. (2021). "Difference-in-Differences with Variation in Treatment Timing." *JoE*.
- Callaway, B. & Sant'Anna, P. (2021). "Difference-in-Differences with Multiple Time Periods." *JoE*.
- de Chaisemartin, C. & D'Haultfœuille, X. (2020). "Two-Way Fixed Effects Estimators with Heterogeneous Treatment Effects." *AER*.
- Sun, L. & Abraham, S. (2021). "Estimating Dynamic Treatment Effects in Event Studies." *JoE*.
- Borusyak, K., Jaravel, X. & Spiess, J. (2024). "Revisiting Event-Study Designs." *REStud*.
- Rambachan, A. & Roth, J. (2023). "A More Credible Approach to Parallel Trends." *RES*.
- Roth, J. (2022). "Pre-test with Caution: Event-Study Estimates after Testing for Parallel Trends." *AER: Insights*.

**测度 / 文本即数据**
- Loughran, T. & McDonald, B. (2011). "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks." *JF* 66(1).
- Loughran, T. & McDonald, B. (2014). "Measuring Readability in Financial Disclosures." *JF* 69(4).
- Tetlock, P. (2007). "Giving Content to Investor Sentiment." *JF* 62(3).
- Gentzkow, M., Kelly, B. & Taddy, M. (2019). "Text as Data." *JEL* 57(3).
- Shapiro, A.H., Sudhof, M. & Wilson, D. (2022). "Measuring News Sentiment." *JoE*.
- Hassan, T., Hollander, S., van Lent, L. & Tahoun, A. (2019). "Firm-Level Political Risk." *QJE* 134(4) (DOI qjz021).
- Fang, L. & Peress, J. (2009). "Media Coverage and the Cross-Section of Stock Returns." *JF* 64(5).
- Da, Z., Engelberg, J. & Gao, P. (2011). "In Search of Attention." *JF* 66(5).
- Gentzkow, M. & Shapiro, J. (2010). "What Drives Media Slant?" *Econometrica* 78(1).
- Campbell, D. & Fiske, D. (1959). "Convergent and Discriminant Validation by the Multitrait-Multimethod Matrix." *Psychological Bulletin*.
- King, G. & Zeng, L. (2001). "Logistic Regression in Rare Events Data." *Political Analysis*.
- Gilardi, F. et al. (2023). "ChatGPT Outperforms Crowd Workers for Text-Annotation Tasks." *PNAS*.

**推断 / 聚类 / FWER**
- Romano, J. & Wolf, M. (2005). "Stepwise Multiple Testing as Formalized Data Snooping." *Econometrica*.
- Westfall, P. & Young, S. (1993). *Resampling-Based Multiple Testing*.
- List, J., Shaikh, A. & Xu, Y. (2019). "Multiple Hypothesis Testing in Experimental Economics." *Experimental Economics*.
- Anderson, M. (2008). "Multiple Inference and Gender Differences in the Effects of Early Intervention." *JASA*.
- Cameron, A.C. & Miller, D. (2015). "A Practitioner's Guide to Cluster-Robust Inference." *JHR*.
- MacKinnon, J. & Webb, M. (2017/2018). "Wild Bootstrap Inference for Wildly Different Cluster Sizes" / few-treated-clusters. *J. Applied Econometrics*.
- Conley, T. & Taber, C. (2011). "Inference with 'Difference in Differences' with a Small Number of Policy Changes." *REStat*.
- Petersen, M. (2009). "Estimating Standard Errors in Finance Panel Data Sets." *RFS*.
- Roodman, D. et al. (2019). "Fast and Wild: Bootstrap Inference in Stata using boottest." *Stata Journal*.

**稳健性 / 计量设定**
- Gormley, T. & Matsa, D. (2014). "Common Errors: How to (and Not to) Control for Unobserved Heterogeneity." *RFS* 27(2).
- Oster, E. (2019). "Unobservable Selection and Coefficient Stability." *JBES* 37(2).
- Altonji, J., Elder, T. & Taber, C. (2005). "Selection on Observed and Unobserved Variables." *JPE* 113(1).
- Koenker, R. & Bassett, G. (1978). "Regression Quantiles." *Econometrica* 46(1).
- Leone, A., Minutti-Meza, M. & Wasley, C. (2019). "Influential Observations and Inference in Accounting Research." *The Accounting Review* 94(6).
- Silva, J.M.C. & Tenreyro, S. (2006). "The Log of Gravity." *REStat* (PPML).
- Cohn, J., Liu, Z. & Wardlaw, M. (2022). "Count (and count-like) Data in Finance." *JFE* 146(2).
- Angrist, J. & Pischke, J.-S. (2009). *Mostly Harmless Econometrics* (bad controls §3.2.3).
- Hoberg, G. & Phillips, G. (2016). "Text-Based Network Industries and Endogenous Product Differentiation." *JPE*.

**组合 / 可复现 / 诚信**
- Heckman, J. (1979). "Sample Selection Bias as a Specification Error." *Econometrica*.
- Wooldridge, J. (2010). *Econometric Analysis of Cross Section and Panel Data*, Ch.19.
- Cookson, J.A. & Niessner, M. (2020). "Why Don't We Agree? Evidence from a Social Network of Investors." *JF* 75(1): 173-228 (DOI 10.1111/jofi.12852).
- Bushman, R. & Williams, C. (2012). "Accounting Discretion, Loan Loss Provisioning, and Discipline of Banks' Risk-Taking." *JAE*.
- Westphal, J. & Zajac, E. (1994). "Substance and Symbolism in CEO Long-Term Incentive Plans." *ASQ*.
- Kogan, L. et al. (2017). "Technological Innovation, Resource Allocation, and Growth." *QJE*.
- Christensen, G. & Miguel, E. (2018). "Transparency, Reproducibility, and the Credibility of Economics Research." *JEL*.
- AEA Data and Code Availability Policy (2019+, Data Editor reproduction).
- Baker, S., Bloom, N. & Davis, S. (2016). "Measuring Economic Policy Uncertainty." *QJE*.
- Bai, J. & Perron, P. (1998). "Estimating and Testing Linear Models with Multiple Structural Changes." *Econometrica*.

---

*报告完。本审计严格区分: 真缺陷 (须修) vs 已披露设计 (披露即可) vs T=2 试跑假象 (全量重生即消)。就绪度元结论已在执行摘要与横切根因第 5 条阐明: 当前 T=2 占位, 全量 T=19 run 尚未执行, 投稿前必须经一次受控协调式重生闭合自洽性。*
