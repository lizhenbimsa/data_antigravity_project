# P2 attention 度量 — 万无一失审核 + 双轨可行性裁定

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


**日期**: 2026-06-05  **方法**: 主控实跑 stage14(1170行)+12_full(4054行) 建真值地基 → 14 agent 工作流（双轨分类 35 方法 + 5 维坑猎 + 完整性批判），复核代理**逐字节重算全部相关系数确认零造假**。
**性质**: 只读审核。给 W2 实现的验收闸 + 双轨执行裁定。

---

## 一、双轨执行可行性裁定（核心问题，2026-06-05 按"双轨=互为稳健性"原则修订）

> **原则修正（推翻本报告初版的"正交性"框架）**：双轨 = **互为稳健性**。full（全文）与 ctx（实体窗口）是同一分析在两种归因口径下的对照，**相关性高低不决定是否双轨**——高相关=主结果对归因窗口稳健（好），低相关=更严归因仍成立（更强）。两轨**分别进各自回归**（main=full，robustness=ctx 复跑同规格），**从不同进同一 RHS**，故"多重共线"不适用。
> **唯一不能双轨的是 track-agnostic 度量**——输入是文章元数据（outlet名/计数/标题旗/is_fintech），full 与 ctx 用同一个数，**没有第二个输入值可算**（数据结构事实，与相关性无关）。

30 个方法三分类（实跑列 + 源码核验）：

| 状态 | 数 | 含义 | 双轨怎么执行 |
|---|---|---|---|
| **DUAL_AVAILABLE** | 13 | full/ctx 输入现成 | **直接双轨**：main=`_full`，robustness=`_ctx` 分离复跑 |
| **DUAL_EXTENDABLE** | 2 | ctx 版可由 `content_ctx` 重抽 | 在 content_ctx 上**重跑 AC 自动机**（$0，无 LLM）派生 ctx 计数轨 |
| **SINGLE_NO_CTX_INPUT** | 15 | 输入是元数据，真无第二轨 | 单轨；其稳健性搭档是"同构念替换"或别列的双轨，**不复制伪 ctx** |

**4 列的双轨执行裁定**：

| 列 | 双轨载体 | full/ctx 相关 | 稳健性叙事 |
|---|---|---|---|
| **index** | ✅ 全部强度型（累积Σ/篇均/提及加权/熔断/峰值）DUAL_AVAILABLE | 累积 0.984 / 篇均 0.785 / 提及加权 0.995 | **主结果对归因窗口稳健**（收紧到实体窗口、消多银行借位，排序几乎不变）→ Hassan proximity 不改变结论。**两列都产、分离复跑** |
| **index ctx 族扩展** | ✅ gap=`mean(full−ctx)`、归因份额=`Σctx/Σfull`、ctx 覆盖率 | — | 这些是双轨**派生的新构念**（full 单轨给不出），作机制/纯度变量进 main，**补充**而非替代双轨 |
| **pct** | ✅ 强度加权份额 DUAL_AVAILABLE；广度份额 DUAL_EXTENDABLE | 强度份额 0.872 | 计数份额/log-odds/标题加权是 track-agnostic（is_fintech 计数），**单轨**；强度加权份额双轨复跑 |
| **disp** | ✅ 强度 SD/CV DUAL_AVAILABLE（真双轨最有力）；ctx-加权 HHI | SD 0.656 / CV 0.418（最低） | **即便把强度归因收紧到实体窗口，离散度结论仍成立**；outlet/地理/月度 HHI 是 track-agnostic 单轨 |

**结论**：
- **凡输入是 `fintech_intensity_score_full/ctx` 或 `intensity_verified_full/ctx` 或 `content_full/ctx` 的方法，全部双轨执行作互为稳健性**——`attention_index_full`/`_ctx`、强度加权 `pct_full`/`_ctx`、强度 SD `disp_full`/`_ctx` 等都产两列，main 进主表、ctx 复跑 robustness 附录，**绝不同进一个 RHS**。
- **index 0.984 高相关不是弃 ctx 的理由，而是"对归因口径稳健"的正面证据**（写进 Methods/robustness）。
- **track-agnostic 度量**（原始计数、outlet HHI、地理 HHI、Gini、月度、log-odds、标题加权份额、标题-邻近）**没有第二个输入值**——单轨即可，强行加 `_ctx` 是逐字伪复制。
- **2 个 DUAL_EXTENDABLE**（Hassan 频率 `fintech_total_count/doc_length`、广度归一份额）：现成列只存全文 AC 命中，但可在 `content_ctx` 上**复用 stage14 的 AC 自动机重跑**（$0）派生 ctx 计数轨——作审稿追加储备。
- 此外仍可保留 gap/share/覆盖率等**双轨派生的归因新构念**作机制变量（它们是 full−ctx / ctx÷full，本身已含两轨信息，不再分离复跑）。

---

## 二、万无一失 — BLOCKER 清单（W2 实现前必须解决）

> 这些是**纸面推演发现不了、实跑才暴露**的坑。每条都有实跑取证。

### 🔴 数据完整性（最致命）

| # | 问题 | 实跑证据 | 确切修法 |
|---|---|---|---|
| B1 | **面板脊柱选择偏差**：脊柱由 fintech 过滤后的 24_herd 建（`encode.py:1541`），**128 家"零 fintech"银行被静默丢弃** | stage14=117 行 vs 12_full=245 行；bank-year 157 vs 349 | **必须在 `balance_panel` 前用 12_full 全 bank-year 重建脊柱**，不能在 compute 内 LEFT-join 补救（脊柱本身缺银行）|
| B2 | **pct 分母错源**：若分母沿用脊柱的 fintech-only `n_articles`，得到 ≈1 的伪份额 | 192/349 bank-year 是零-fintech，须 `fillna(0)` | 分母 `N_all` **独立从 12_full** 两次 groupby；零-fintech 行 `n_ft.fillna(0)`，`assert (n_all>0).all()` |
| B3 | **强度加权份额不是 [0,1]**：`Σintensity/N_all` 范围 [0, 1.44]，自相矛盾 | 实跑 max 1.44 | **改名 `attention_intensity_density`** + codebook 声明值域 [0,∞)；或归一后再除。**禁止称"份额"** |
| B4 | **归因份额越界 >1**：菜单声称 `Σctx/Σfull∈[0,1]` 为假 | 24/157 cell >1，max 1.2227（ctx 在更短窗 TF-IDF×SIF 权重被放大）| `.clip(0,1)` + 注明非严格∈[0,1]。**复用 PR#5 的 ctx-分母 frac 闭合修复**（同根问题已有先例）|

### 🔴 接线/契约协调

| # | 问题 | 修法 |
|---|---|---|
| B5 | **golden 四契约硬门**：4 新列入盘 → `test_panel_reproducibility:157`（严格列集相等）+ `test_dag_consistency` + codebook + spec **全部翻红** | **协调式重生**：实现后跑 `generate_golden_snapshot.py` 重生 golden + 注册 codebook + 跑 repro/dag。这是 W2 真正的验收门（不是"值对不对"，是"4 列入盘能否一把过四契约同步重生"）|
| B6 | **命名空间撞车**：`ft_attn_yr` 已存在（= year 级 fintech 份额，已注册/已进 golden），与 `attention_pct_full`（bank-year 版）**是同一构念** | **先收编 ft_attn_yr 再扩 bank-year**，不要平行另起一套（否则正中 variable-farm 冗余）|
| B7 | **Stata 主回归硬崩（exit 198）**：`01_data_prep.do.tmpl:31-37` 对缺失 `{{MAIN_TREAT}}` 报错退出 | 实现 B1 的 4 列后自动通过；列名须与模板逐字一致（不能用 `ft_attn_*` 别名）|

### 🟠 数值守卫（HIGH）

| # | 问题 | 实跑证据 | 守卫 |
|---|---|---|---|
| H1 | **disp 不能被 zero-fill 污染** | 强度 SD 仅 80/157 可算（77 个 N=1→NaN）；HHI=1 的 84/157 单 outlet | disp 列**禁止进 balance_panel 的 zero_fill**；命名**避开 `_sum/_count` 后缀**（否则 `balance_panel:1580` 正则强制 fillna(0)，把"无法算/真零/无文章"三义压成 0）；并出 `n_outlets`/`n_articles` 诊断列 |
| H2 | **时间维方法当前 0 可算** | 0/157 bank-year 有 ≥3 个月（样本仅 2017-11→2018-01 共 3 个 year-month）| Da 异常/AR/burstiness/月度离散/EPU 期归一 **config-gate off + graceful skip**（`groupby.year.nunique().max()>=3` 才启用），**绝不在试跑样本吐时序数值** |
| H3 | **IDF 全语料非平稳** | intensity_score=TF-IDF×SIF，IDF 是全语料统计量 | 从 1170 篇扩到 18.2M，**同篇 intensity 数值会变** → attention 列漂移；试跑标定的阈值/winsor 界全失效；**golden 全量后须二次重生**。（jieba 字节冻结保护的是分词，不是 IDF）|
| H4 | **HHI groupby-apply = 第二个性能炸弹** | `attention_media.py:742` `groupby.apply(_hhi)` Python 回调 | 与 W1 修的 herd_decay O(N²) 同族；18.2M 头部银行会卡死。disp 用 HHI **必须改 vectorized**（`groupby.size` 算份额平方和）|

### 🟡 其余（MEDIUM/披露）

- **co_mention 折算法（M4.6）80% 空**（936/1170）→ 对 80% 行退化为基线，**从 W2 备选直接移除**，别当稳健性。
- **doc_length == len(内容) 精确**（非 content_full）→ Hassan 分母用的是正文不含 prepend 标题；菜单 §六"len(content_full)"应订正为 doc_length 本身。
- **`fintech_total_count < distinct` 在 11/1170 行**（计数基不一致）→ 上游核查，勿断言 total≥distinct。
- **媒体类型(中文) 当前单值"报纸"** → 媒体类型异质性归全量后；勿与 `媒体(中文)`（94 outlet，disp 用此列）混淆。
- **year 派生/中文列名访问**：复用 `attention_media.py:255` 的 `dt.year` 派生；坚持中文字面量直读（已验证可行，勿改位置索引）。

---

## 三、"现在可落地" vs "全量后激活"（防在试跑样本跑出误导数值）

| 现在即可稳健落地（无 T 依赖、无除零） | 全量 2007–2025 后才激活 |
|---|---|
| ✅ `attention_index_full = ln(1+Σintensity_full)`（[0.086,3.959] 无 NaN）| ⏳ 所有时间维：Da 异常 / AR(1) / burstiness / 月度离散 / EPU 期归一 |
| ✅ `attention_pct_full = N_ft/N_all`（全集分母，[0,1] 无 NaN/inf）| ⏳ within-bank / DiD / 事件研究（当前是 2.5 月伪面板，非真 T=2）|
| 🟡 disp 跨媒体 HHI（加 N_outlets 诊断 + 退化披露）| ⏳ 媒体类型异质性（当前单值）|
| 🟡 disp 强度 SD 双轨（加 N≥2 守卫）| ⏳ co_mention 折算（待填充率改善）|

---

## 四、诚实边界（不因审核充分而夸大）

1. **W2 ≠ P2 可跑**：即便 4 个 treatment 列完美物化，P2 主回归仍缺 **outcome `ln_fintech_investment` + IV**（外部 CSMAR/Wind，v2 阶段二待办）。物化 attention 只解决自变量端。
2. **当前样本是 2.5 月伪面板**（3 个 year-month），比"T=2"还弱——4 度量现在**只能做横截面分布/相关 sanity check**，任何识别推断须等全量。
3. **前阶段定级修正**（完整性批判推翻 4 处）：坑猎 D5 把"T=2 退化"列为 blocker 是**定级错误**——按 v2 全量审计，那些是试跑假象、全量自然恢复，应降为披露项；**唯独 index 0.984 近共线与 T 无关，维持有效**。
4. **未审尽的盲区**（诚实标注）：HHI 全量真实 wall-clock 未实测（需分层子样本压测）；attention 是否被 `iv_did.py` 的 bartik_attention_iv 半成品消费未 grep；paper_spec_schema 是否硬断言 treatment 列存在未确认。

---

## 五、W2 实现的最小正确姿势（综合裁定）

> ✅ **W2 代码实现已完成并验证（2026-06-05）**：`attention_media.py::compute_attention_treatments()`（12 列，全 foolproof 守卫 B1/B2/B3/B4/H1/H4 + 双轨=互为稳健性）+ 接线 `runner.py:6b-2` + codebook 注册 12 列（track 自动识别 full/ctx）+ `tests/test_attention_treatments.py`（11 测试，真实数据验证全部守卫）。验证：11 attention + 39 DAG/golden 闸门 + panel/P0 全绿，ruff clean。**物化已完成（方式 B 完整重建, 2026-06-05）**：跑 stage 45（panel build, exit 0, 暖缓存 $0）→ stage 51（exit 0, 51 带 attention）→ 重生 golden → 验收闸 56 passed（repro+dag+panel_columns+attention）+ 更广 integration 回归 exit 0。40_panel 真实 delta = **+12 attention 列（零列移除, UTF-8 核验）**, 实测双轨 corr(index)=0.9864 / corr(sd)=0.6514 与审计吻合。最终选 B（剔除旁路 exec_ner）: 把 `19_executive_ner_panel.parquet` 挪为 `.w2bak`（备份可恢复, runner.py:1606 缺文件优雅跳过）→ 重建 45/51 → 重生 golden。**最高标准核查结果（完美无缺）**:
- golden delta vs git-HEAD = **精确 +12 attention / exec=0 / other=0 / 移除=0**（40+51 两面板一致）。
- **attention 12 列跨两次独立重建逐位完全一致（mismatch=0）→ 完全确定性/可复现**。
- 6 列加固复核（compute_attention_treatments 对抗复核 6 agent）: 仅 2 个防御项（log1p 前 sum.clip(lower=0) 防上游 IDF 负值; 校验器补 sd 列）已加固, 对当前数据零行为变更; 其余 B1/B2/B4/H1/零-fintech 语义/join/dtype/HHI vectorized 全部实证 OK（重算 vs 落盘 max diff=0.0）。
- 验收: 全闸门 56 passed + 广回归 378 passed/1 skipped, ruff clean。
- ⚠ **既有非确定性（与 W2 无关, 须知晓）**: 3 列 networkx 中心度 `bank_clustering`/`bank_cfbetween_cent`/`bank_harmonic_cent` 在任意重建间漂移（`current_flow_betweenness` 等 BLAS FP 非确定）, golden 对这 3 列非逐位可复现——是流水线既有问题, 非本 W2 引入。
下方为原始裁定。

```
1. 先扩脊柱：balance_panel 的 all_banks 取 12_full 全集 245 银行（修 B1）→ 否则后面全是空中楼阁
2. index_full = ln(1+Σ intensity_full)          [main RHS; 现在可落地, 零-fintech 行 Σ=0→0 真值]
   index_ctx  = ln(1+Σ intensity_ctx)            [双轨=互为稳健性: robustness 附录复跑同规格, 不与 full 同进一 RHS]
   + 归因 gap=mean(full−ctx) / 份额=Σctx/Σfull   [双轨派生的归因新构念, 作机制变量补充(非替代双轨)]
3. pct_full = N_ft/N_all                          [分母独立读 12_full + fillna(0), 收编 ft_attn_yr 而非另起]
   + 强度加权份额 Σintensity_full/N_all 双轨      [DUAL_AVAILABLE: full main + ctx robustness 复跑; 改名 intensity_density 防 B3]
4. disp_full = vectorized 跨媒体 HHI              [track-agnostic 单轨; 改 vectorized 防 H4; 加 n_outlets; 避 _sum/_count 命名]
   + 强度 SD 双轨 (N≥2 守卫)                       [disp 唯一真双轨载体, full main + ctx robustness 分离复跑]
5. 时间维方法全部 config-gate off + graceful skip [H2]
6. 注册 codebook 4+ 列 + 重生 golden + 跑 repro/dag [B5, 验收门]
7. 文档披露: W2≠P2可跑(缺outcome); 试跑期disp退化; 全量后golden二次重生(IDF漂移)
```
