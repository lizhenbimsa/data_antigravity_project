# 基于 "Media Sentiment and Currency Reversals" 的项目分析与执行计划

> **参考论文**: Filippou, I., Taylor, M.P. & Wang, Z. (2021). "Media Sentiment and Currency Reversals." CEPR Discussion Paper DP16049 (SSRN: 3846136).
>
> **项目**: `F:\WiseSearch\data_antigravity_project\news_process`
>
> **审计日期**: 2026-04-06

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Filippou et al. (2021) 的核心贡献可凝缩为一条因果链：

```
FX 媒体情感 → 短期价格压力（过度反应）→ 中期均值回复（3-5个月）→ 反转策略可盈利
```

**五大机制支柱**：

| # | 机制 | 论文实现 | 关键发现 |
|---|------|----------|----------|
| M1 | **Bag-of-Words 情感度量** | Loughran-McDonald 词典；`Sent = (Pos - Neg) / TotalWords`；Negativity 非对称度量 | 两种度量结果一致 |
| M2 | **时序预测 + VAR 均值回复** | 面板回归 + 5阶 Panel VAR，双重固定效应 | 情感对 1-2 个月收益强负向预测（t=-2.77），3-5 月反转（Sum₂₋₅=0.593***） |
| M3 | **截面反转组合** | 6 分位 Sort，多 formation/holding 期组合；**买低卖高**情感策略 | REV(1,1) 年化 6.53%，SR=0.57（全样本）/0.80（发达国家） |
| M4 | **正交化检验** | 与 DOL、CAR（carry）、MOM（momentum）正交回归 | Alpha 4-8%/年，与 carry/momentum 低相关 |
| M5 | **分析师预测反驳** | 分析师预测反向排列 → 不能解释反转收益 | 分析师系统性预测错误 |

### 1.2 当前项目定位

| 维度 | 论文 | 项目现状 |
|------|------|----------|
| **资产类别** | 外汇（48 种货币） | 中国银行股/金融科技 |
| **情感来源** | 9 家英文媒体，120 万篇 | 中国大陆中文媒体（多类型） |
| **情感度量** | 基础 BoW（Loughran-McDonald） | **三层体系**：LLM 三角验证 + 5 本中文词典 + 5 个 BERT 模型 |
| **核心范式** | **反转策略**（过度反应 → 均值回复） | **截面 Tone → 因变量**（无反转/均值回复检验） |
| **时间粒度** | 月度/日度 | 年度（Bank-Year 面板） |
| **因果识别** | Fama-MacBeth、双重固定效应、双向排序 | Bartik IV（29 套）、Leave-one-out IV、DID |

### 1.3 真实落差诊断

**核心盲区**：项目当前是**静态年度截面**设计——将情感聚合为 Bank-Year 均值后直接回归。这完全忽略了论文揭示的**时间动态**：情感→短期过度反应→中期反转。年度聚合会将反转效应彻底对冲抹平，导致情感变量的经济效应被严重低估（attenuation bias 的极端情形）。

**四个关键落差**：

| 落差 | 论文视角 | 项目现状 | 严重程度 |
|------|----------|----------|----------|
| **L1: 缺乏时间动态建模** | 月度 Panel VAR，5 阶滞后，明确检验均值回复 | 年度聚合后无滞后结构 | 致命 |
| **L2: 无反转/momentum 信号** | 情感变化（ΔSentiment）的符号决定多空方向 | 仅使用情感水平值，不构建反转信号 | 高 |
| **L3: Negativity 非对称度量缺失** | 独立使用 `Neg = -N_neg / TotalWords` 作为稳健性检验 | 有 MSENT 指标但未按论文的 Negativity 逻辑独立构建 | 中 |
| **L4: 无 Fama-MacBeth 截面回归** | 显式 FM 回归检验情感对截面收益的预测能力 | 使用 IV 但无纯截面定价框架 | 中 |

---

## 2. 实质性改进项

### 改进 A：时间衰减型情感加权（Time-Decay Sentiment Weighting）

- **具体修改**：在 `41_panel_encode_aggregate.py` 的 `aggregate_panel()` 中，增加**月度子面板**中间层，为同一 Bank-Year 内的文章赋予基于发表月份的指数衰减权重。
- **论文依据**：Filippou et al. (2021) Table 3 VAR 结果表明，Sentiment_{t-1} 影响最强（β=-0.119），随后 3-5 月反转。这意味着**近期情感的信息含量远高于远期情感**。
- **预期边际贡献**：在年度聚合约束下最大化保留论文发现的时间衰减结构，缓解年度等权平均对近期信号的稀释。实证上，若项目的因变量为年末截面指标（如年报绩效），则年末发表的新闻情感应有更高权重。
- **实施公式**：`w_j = exp(-λ * (12 - month_j))`，λ=0.1 为基准，月末文章权重最高。

### 改进 B：反转预测指标构建（Reversal Signal Construction）

- **具体修改**：在 `43_panel_indicators_geography.py` 的 `compute_composite_indicators()` 中新增以下变量：
  1. `tone_reversal_signal = tone_{t} - tone_{t-1}`（年度情感变化量）
  2. `tone_momentum = (tone_{t} + tone_{t-1}) / 2`（两年滑动均值）
  3. `tone_delta_sign = sign(tone_{t} - tone_{t-1})`（方向信号）
- **论文依据**：Filippou et al. (2021) Section 5.3, Eq.(2) 的时间序列反转策略基于 ΔSentiment 的符号进行多空决策。静态水平值无法捕捉这种方向性信息。
- **预期边际贡献**：`tone_reversal_signal` 直接对标论文的核心交易信号。在面板回归中，该变量预期对因变量具有显著相反符号效应（高变化 → 后续反转），从而**在年度面板中复现论文的月度反转发现**。

### 改进 C：Negativity 非对称度量

- **具体修改**：在 `22_tone_words.py` 的 `_analyze_single_article()` 中新增输出列 `negativity_score = -neg_count / total_words`。在 `41_panel_encode_aggregate.py` 中聚合为 `avg_negativity_{track}`。
- **论文依据**：Filippou et al. (2021) Section 4, Eq.(3) 独立构建 Negativity 度量，引用 Tetlock (2007) 发现投资者判断**主要由负面情感驱动**而非正负面净值。论文全文结果在 Negativity 上高度一致。
- **预期边际贡献**：现有 `msent_score` 使用 `(Neg-Pos)/(Neg+Pos)` 比率，与论文的 `Neg/TotalWords` 有本质区别。后者不受正面词比例扰动，是更纯净的悲观信号代理。作为独立稳健性检验，可评估中文语境下负面词驱动假说是否成立。

### 改进 D：面板 VAR 均值回复检验

- **具体修改**：在 `51_falsification_test.py` 中新增 Panel VAR 检验模块。使用 Bank-Year 面板，估计 `DV_{i,t} = α_i + τ_t + Σ_{k=1}^{3} β_k * Tone_{i,t-k} + γ * Controls_{i,t-1} + ε_{i,t}`（3 阶滞后对应年度数据的合理窗口）。
- **论文依据**：Filippou et al. (2021) Table 3 的核心检验——通过计算 `Sum_{2-3}` 并执行 Wald 检验判断是否存在反转（即情感的短期负向效应是否在后续期间被反转）。
- **预期边际贡献**：**直接验证反转假说在中国银行金融科技语境下是否成立**。若 β₁ < 0 且 Sum_{2-3} > 0 且显著，则证明论文机制具有跨市场/跨资产类别的泛化性。这是项目目前完全缺失的关键实证检验。

### 改进 E：Fama-MacBeth 截面回归框架

- **具体修改**：在面板导出后的下游分析中，实现 Fama-MacBeth 两步法截面回归：第一步每年对银行截面回归 `DV_i = λ₀ + λ₁ * Tone_{i,t-1} + λ₂ * Controls_{i,t-1} + ε_i`；第二步对时序 λ 序列取均值并计算 NW-t 统计量。
- **论文依据**：Filippou et al. (2021) Table 6，FM 回归是外汇文献中截面定价检验的金标准。论文发现控制 forward discount 和 lagged return 后，sentiment 仍是截面收益的强负向预测因子。
- **预期边际贡献**：FM 回归避免了面板回归中截面与时序效应混淆的问题（Petersen 2009, RFS），提供纯截面层面的情感预测力证据。当前项目的 Bartik IV + 面板 FE 回归解决的是因果识别问题，FM 回归则回答"情感是否包含截面定价信息"这一更基础的问题。

---

## 3. 冗余剥离

### 3a. 维持原状：LLM 三角验证体系

**判定：维持原状**。论文使用的是基础 Bag-of-Words 方法（Loughran-McDonald 词典），项目的 LLM 三角验证 + 5 本中文词典 + 5 个 BERT 模型体系**严格优于**论文方法。论文本身在 Section 6.6 中承认 LDA topic modeling 只是稳健性检验，并非核心方法改进。项目的多模型集成在精度和稳健性上已远超论文范式，没有退化为纯词典法的必要。

### 3b. 维持原状：Bartik IV 体系

**判定：维持原状**。论文未涉及工具变量识别策略（依赖非参数组合排序 + FM 回归）。项目的 29 套 Bartik IV 是面板因果推断的核心支撑，与论文方法形成互补而非替代关系。

### 3c. 建议精简：过多的双重排序模式

**判定：审视必要性**。论文 Table 9 的双重排序（Country Risk x Sentiment, Volatility x Sentiment 等）针对的是 FX 市场特有的流动性/波动性分层假说。项目场景（中国银行截面）的异质性维度应当是银行类型、规模、地域等——这些已在 Bartik IV 的分组变量中覆盖。无需额外复制论文的 FX 特有双重排序。

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 改进项 | 类型 | 实施成本 | 预期收益 | 优先级 |
|--------|------|----------|----------|--------|
| **A. 时间衰减加权** | 速赢 | 低（仅修改聚合逻辑） | 中（保留时间结构信息） | P1 |
| **B. 反转信号构建** | 速赢 | 低（新增 3 列计算） | 高（直接可用于回归） | P1 |
| **C. Negativity 度量** | 速赢 | 低（词典模块微调） | 中（稳健性检验新维度） | P2 |
| **D. Panel VAR 检验** | 核心攻坚 | 中（需 VAR 估计框架） | 极高（核心理论检验） | P0 |
| **E. Fama-MacBeth 回归** | 核心攻坚 | 中（需两步法实现） | 高（截面定价标准检验） | P1 |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：机制重塑 / 数据清洗

**目标**：在不破坏现有管道的前提下，增加时间动态变量。

#### 指令 1.1：时间衰减加权（改进 A）

- **位置**：`41_panel_encode_aggregate.py` → `aggregate_panel()`
- **动作**：
  1. 在 GroupBy 之前，从 `日期` 列提取月份 `month_j`
  2. 计算衰减权重 `w_decay = exp(-λ * (12 - month_j))`，λ=0.1
  3. 创建加权情感列 `llm_vote_score_decay_{track} = llm_vote_score_{track} * w_decay`
  4. 在 `build_aggregation_dict()` 中新增聚合条目：`llm_vote_tone_decay_{track} = sum(weighted) / sum(weights)`
- **交付物**：面板新增 `llm_vote_tone_decay_full` / `_ctx` 两列

#### 指令 1.2：Negativity 非对称度量（改进 C）

- **位置**：`22_tone_words.py` → `_analyze_single_article()`
- **动作**：
  1. 在计算 `msent_score` 后，新增 `negativity_score = -best_neg_count / len(tokens)` （对标论文 Eq.3）
  2. 在 `41_panel_encode_aggregate.py` 的 `build_aggregation_dict()` 中新增聚合：
     - `avg_negativity_{track} = (negativity_score_{track}, 'mean')`
     - `avg_negativity_std_{track} = (negativity_score_{track}, 'std')`
- **交付物**：篇章级 `negativity_score_{track}`，面板级 `avg_negativity_{track}`

#### 指令 1.3：反转信号构建（改进 B）

- **位置**：`43_panel_indicators_geography.py` → `compute_composite_indicators()`
- **动作**：
  1. 计算 `tone_lag1_{track} = panel.groupby('target_bank')['llm_vote_tone_{track}'].shift(1)`
  2. 构建 `tone_reversal_{track} = llm_vote_tone_{track} - tone_lag1_{track}`
  3. 构建 `tone_momentum_{track} = (llm_vote_tone_{track} + tone_lag1_{track}) / 2`
  4. 构建 `tone_delta_sign_{track} = np.sign(tone_reversal_{track})`
- **交付物**：面板新增 6 列（reversal / momentum / delta_sign x 双轨）

**阶段一交付标准**：
- 面板维度不变（Bank x Year 笛卡尔积不受影响）
- 所有新增列通过 NaN 一致性检验（首年 lag 为 NaN 是预期行为）
- Stata .dta 文件正常导出，包含新增变量标签

---

### 阶段二：实证 / 模型重构与检验

**目标**：实现论文核心检验框架的项目化迁移。

#### 指令 2.1：Panel VAR 均值回复检验（改进 D）

- **位置**：`51_falsification_test.py` 新增函数 `test_panel_var_reversal()`
- **动作**：
  1. 使用 `linearmodels.panel.PanelOLS` 或 `statsmodels` 估计：
     ```
     DV_{i,t} = α_i + τ_t + β₁ * Tone_{i,t-1} + β₂ * Tone_{i,t-2} + β₃ * Tone_{i,t-3} + γ * Z_{i,t-1} + ε_{i,t}
     ```
  2. 构建 `Sum_{2-3} = β₂ + β₃`，执行 Wald 检验 H₀: Sum₂₋₃ = 0
  3. 输出结果表至 `data_processed/eval_reports/51_panel_var_reversal.csv`
- **稳健性标准**：
  - β₁ < 0 且显著（至少 5% 水平）→ 情感短期负向效应存在
  - Sum₂₋₃ > 0 且 Wald p < 0.10 → 均值回复/反转存在
  - HAC 标准误（Newey-West 1 阶）

#### 指令 2.2：Fama-MacBeth 截面回归（改进 E）

- **位置**：`51_falsification_test.py` 新增函数 `test_fama_macbeth()`
- **动作**：
  1. 第一步：对每个年份 t，运行截面回归：
     ```
     DV_i = λ₀ + λ₁ * Tone_{i,t-1} + λ₂ * Controls_{i,t-1} + ε_i
     ```
  2. 第二步：对时序 lambda_1 取均值，计算 Newey-West t 统计量
  3. 逐步加入控制变量（bare → +lagged DV → +size → full）
  4. 输出结果表至 `data_processed/eval_reports/51_fama_macbeth.csv`
- **稳健性标准**：
  - lambda_1 < 0 且 NW-t > 2.0 → 论文的截面反转效应在中国银行样本中成立

---

### 阶段三：结论重构

#### 指令 3.1：综合检验结果汇总

- **动作**：将 Panel VAR 和 FM 回归结果整合入面板文档和技术手册
- **结论框架**：
  - **若 VAR 反转显著**：中国银行金融科技报道存在"过度反应→均值回复"效应，与 Filippou et al. (2021) FX 市场发现一致 → 媒体情感的反转是资产定价的共性特征
  - **若 VAR 反转不显著**：银行金融科技报道的情感效应为**持久性**而非暂时性，与 FX 市场机制不同 → 可能因为银行股的套利限制更强或信息同质性更高
  - 两种结论均有学术价值

---

## 3. 风险预案 (Plan B)

| 致命卡点 | 概率 | 替代方案 |
|----------|------|----------|
| **年度数据不足以检测 VAR 反转**（T 过短，3 阶滞后吃掉过多 df） | 中 | (1) 将面板聚合降级为**半年度**（需修改 parse_time() 和 aggregate_panel()）；(2) 使用月度篇章级数据直接估计 VAR（绕过 Bank-Year 聚合） |
| **Fama-MacBeth 年份数不足**（T < 15 年，NW-t 不可靠） | 低 | 使用 Pooled OLS + 双聚类标准误（时间 + 银行）替代，这在项目现有框架中已可实现 |
| **Negativity 度量与 MSENT 高度共线**（r > 0.95） | 低 | (1) 仅保留 Negativity 作为论文对标变量，删除 MSENT；(2) 通过残差正交化后使用 |
| **衰减权重 lambda 敏感性**（不同 lambda 结果差异大） | 低 | 在 lambda = 0.05, 0.1, 0.15, 0.2 上做网格搜索，报告敏感性分析 |

---

**核心价值判断**：Filippou et al. (2021) 的最大启示不是方法论（项目的 LLM+BERT+Dict 三层体系远优于论文的基础词典法），而是理论机制——**媒体情感的预测力来自过度反应与均值回复的时间动态，而非简单的静态关联**。项目当前缺乏这一时间维度的建模和检验，这是本执行计划的核心攻坚目标。
