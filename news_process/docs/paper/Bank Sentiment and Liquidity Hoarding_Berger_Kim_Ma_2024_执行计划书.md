# Bank Sentiment and Liquidity Hoarding — 项目分析与执行计划

> **参考论文**: Berger, A.N., Kim, H.H., & Ma, X. (2024). "Bank Sentiment and Liquidity Hoarding." *Contemporary Accounting Research*.
>
> **项目路径**: `F:\WiseSearch\data_antigravity_project\news_process`
>
> **生成日期**: 2026-04-07

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Berger, Kim & Ma (2024) 构建了一条从**银行管理层情感**到**流动性囤积**的微观因果链：

| 机制环节 | 具体内容 | 方法论关键点 |
|---|---|---|
| **情感度量** | 10-K年报的 Net Negative Words Ratio (Loughran & McDonald 2011 词典) | 银行级、年度频率、文本来源为监管合规文件 |
| **情感分解** | 将 Net Negative Words 回归宏观基本面 + Location×Year FE → 残差 = **Unexp_Neg_Beliefs**，预测值 = **Exp_Neg_Beliefs** | Baker & Wurgler (2006) / Hribar et al. (2017) 范式，分离非基本面驱动的情感 |
| **因变量** | 综合流动性囤积 LH(total)/GTA = LH(asset) + LH(liab) + LH(off)，涵盖资产/负债/表外 | Berger et al. (2022) 全口径度量 |
| **内生性处理** | 外生天气条件 → LASSO 选择工具变量(2,090 个候选) → 2SLS | 云量覆盖哑变量，部分 F > 10 |
| **供需识别** | 信贷利差(DealScan) + 存款利差(RateWatch) 检验银行主动缩减供给 | 价格信号排除需求驱动假说 |
| **异质性** | 低流动性/高不确定性/高前瞻性比例 → 情感效应更强 | 机制验证：Basel III 约束 + 流动性不确定性 + 前瞻性陈述 |

### 1.2 当前项目与论文的结构性落差

#### ✅ 项目已覆盖（维持原状）

| 维度 | 现状 | 判断 |
|---|---|---|
| **多模型 LLM 情感三角验证** | 3模型(GPT-5 Nano, Gemini 3, GLM-4.5) × 多数投票 × 置信度加权 | **优于论文**：论文仅用 Loughran-McDonald 词典，项目的 LLM 多模型共识在语义拆解和抗实体偏误方面远超词典法 |
| **Bank-Year 面板聚合** | `41_panel_encode_aggregate.py` 已实现均值/总和/标准差/VW/MW 多维聚合 | **覆盖充分** |
| **Bartik IV 体系** | 29 套 Shift-Share IV (银行类型/规模/媒体/时间等) | **远超论文 IV 方案深度** |
| **地理 Leave-One-Out IV** | 同省/同城市其他银行均值情感 IV 已实现 | **等价于论文 Location×Year FE 的替代** |
| **媒体权威性加权** | Holzman et al. (2023, TAR) 权威性加权已实现 | **维持原状** |
| **前瞻性语言分析** | `forward_looking_ratio` / `forward_looking_count` 已在词典模块计算 | **与论文 Section 4.2 的 Forward-Looking Statement 分析等价** |
| **DID 政策冲击** | DCEP 试点 + 金融科技监管沙盒 双 DID 已实现 | **维持原状** |

#### 🔴 核心盲区（实质性落差）

| 盲区编号 | 描述 | 论文依据 | 严重度 |
|---|---|---|---|
| **G-1** | **缺少情感分解机制**：项目直接使用 LLM 原始情感输出，未将情感分解为"基本面驱动"(Exp_Neg_Beliefs) 和"非基本面驱动"(Unexp_Neg_Beliefs) 两个正交成分 | Section 3.1, Eq.(2): 回归净负面词比率 on 宏观变量 + 地理×年份 FE | **致命** |
| **G-2** | **缺少银行资产负债表控制变量**：当前面板仅包含新闻情感变量，未合并银行基本面控制变量（规模 Ln(GTA)、资本充足率、盈利能力、HHI 市场竞争度） | Section 4, Eq.(3): 完整控制变量集 X, W, S | **高** |
| **G-3** | **缺少流动性囤积因变量**：项目无 LH(total)/GTA 等综合流动性度量，面板因变量体系空白 | Section 3.2: 综合 LH 度量 = 资产+负债+表外 | **高** |
| **G-4** | **缺少利差验证模块**：未检验情感对贷款利差/存款利差的影响，无法与论文的供需识别策略对齐 | Section 5, Eq.(4)-(5) | **中** |
| **G-5** | **异质性分析框架缺失**：未构建基于流动性水平/流动性不确定性/前瞻性比例的分组回归 | Section 4.2, Table 3 | **中** |

---

## 2. 实质性改进项

### 改进 A：情感正交分解模块 (Unexp vs Exp Beliefs)

- **具体修改**: 在 `43_panel_indicators_geography.py` 中新增函数 `decompose_sentiment_beliefs()`，将 `llm_vote_tone_full` 回归于一组宏观基本面代理变量（GDP 增速、信贷环境、利率水平等）和银行注册地×年份交互固定效应，提取残差 `unexp_neg_beliefs_full` 和预测值 `exp_neg_beliefs_full`。
- **论文依据**: Section 3.1, Eq.(2): "We adapt this approach to the banking setting and regress the net negative words ratio on a more comprehensive set of fundamentals at the macro and bank location×year level."
- **边际贡献**: 解决当前最大的识别问题——无法区分情感中由基本面信息驱动的部分 vs 纯行为偏误驱动的部分。正交分解后，`unexp_neg_beliefs` 系数的经济学解释为"**不能被已知宏观条件解释的媒体悲观情绪每增加一个标准差，对银行行为的边际效应**"。

### 改进 B：银行基本面控制变量合并模块

- **具体修改**: 在 `45_panel_export_main.py` 的面板导出前，新增一步从外部数据源（CSMAR/WIND/银行年报数据库）合并银行基本面变量——总资产对数 Ln(GTA)、资本充足率(Capital_ratio)、ROA(Earnings)、存款集中度(HHI)、所在地人口/Tobin's Q/现金流等。
- **论文依据**: Section 4, Eq.(3): 完整控制变量集 X(银行), W(市场), S(宏观情感), EPU。
- **边际贡献**: 无控制变量的纯情感面板在实证检验中将面临严重的遗漏变量偏误，审稿人必然要求将银行基本面特征作为核心控制。

### 改进 C：流动性囤积因变量构建指引

- **具体修改**: 在面板导出数据的数据字典/文档中，明确标注因变量需求：LH(total)/GTA 需从 Call Reports（或中国等价物：银保监会 1104 报表 / 银行资产负债表）手工构建。为每个子项（LH_asset、LH_liab、LH_off）提供权重方案来源（Berger et al. 2022, Appendix S3）。
- **论文依据**: Section 3.2, Appendix S3.
- **边际贡献**: 即使自变量（情感指数）完备，因变量（流动性囤积）的缺失使得整个实证研究无法运行。

---

## 3. 冗余剥离

| 模块 | 判断 | 理由 |
|---|---|---|
| `22_tone_words.py` (词典法情感) | **保留但降级** | 论文使用 Loughran-McDonald 词典作为主度量，项目的 5 本中文词典可作为稳健性检验，但在 LLM 多模型共识已覆盖的情况下，**不应作为核心解释变量**，建议在面板中标注为 robustness-only |
| `23_tone_berts.py` (BERT 情感) | **保留但降级** | 同理，5 个 BERT 模型可作为方法论三角验证的补充证据，但不承担核心解释力 |
| `12_news_fintech.py` (金融科技筛选) | **维持原状** | 与论文研究主题不同（论文关注一般性银行情感），但金融科技聚焦是本项目的独特贡献，不可删除 |
| `38_media_diversity.py` + `38b_decay_sensitivity.py` | **维持原状** | 媒体异质性分析与论文 Section 4.3 中区分不同信息源的思路一致 |

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

### 🏃 速赢项 (Quick Wins) — 1-3 天

| 序号 | 任务 | 实施成本 | 预期收益 |
|---|---|---|---|
| QW-1 | 在面板导出中新增"情感正交分解"函数 | 低（回归残差提取） | **极高**：直接产出核心解释变量 |
| QW-2 | 导出数据字典标注因变量需求（LH 构建指引） | 极低（文档性） | 高：明确下游数据采集方向 |
| QW-3 | 在现有面板中构建异质性分组分裂变量（流动性高/低、前瞻性高/低） | 低 | 中：为异质性回归做准备 |

### 🔧 核心攻坚项 — 5-15 天

| 序号 | 任务 | 实施成本 | 预期收益 |
|---|---|---|---|
| CA-1 | 外部数据合并模块（银行基本面 + 宏观变量） | 高（数据获取+清洗） | **极高**：无此不能发表 |
| CA-2 | 流动性囤积因变量构建（需外部银行报表数据） | 高 | **极高**：因变量核心 |
| CA-3 | 利差验证模块（需商业银行贷款/存款利率数据） | 高 | 高：供需识别关键证据 |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：机制重塑与数据清洗 (Day 1-5)

#### 动作 1.1：情感正交分解函数

**文件**: `43_panel_indicators_geography.py`  
**函数名**: `decompose_sentiment_beliefs(panel: pd.DataFrame) -> pd.DataFrame`

```
核心逻辑:
1. 从外部加载宏观变量时间序列 CSV（需预置在 config/ 或 data_excel/ 下）:
   - GDP 增速 (gdp_growth_t)
   - M2 增速 (m2_growth_t) 
   - 国债利差 (term_spread_t)
   - 信用利差 (credit_spread_t)
   - 沪深300收益率 (market_return_t)
   - 消费者信心指数 (consumer_conf_t)
   - 经济政策不确定性 EPU_China (epu_t)

2. 基座回归（对每个 track: full/ctx）:
   llm_vote_tone_{track}_{i,t} = α + β₁·gdp_growth_t + β₂·m2_growth_t
       + β₃·term_spread_t + β₄·credit_spread_t + β₅·market_return_t
       + β₆·consumer_conf_t + β₇·epu_t
       + Location_i × Year_t FE  (bank_province × year)
       + ε_{i,t}

3. 输出:
   - unexp_neg_beliefs_{track} = ε̂ (残差) — 核心解释变量
   - exp_neg_beliefs_{track} = ŷ (预测值) — 控制变量
   - R² 需记录并汇报 (论文为 0.805)

4. 对 dict_avg_tone_{track}、bert_avg_pos_{track} 同步执行分解
   → unexp_dict_tone_{track}, unexp_bert_pos_{track}
```

**交付物标准**:
- R² ∈ [0.30, 0.90] 视为合理（中国新闻语料 vs 美国 10-K 存在差异）
- 残差均值应趋近 0（OLS 性质）
- 日志中记录各宏观变量的 t 值和显著性

#### 动作 1.2：宏观变量数据准备

**文件**: `config/macro_fundamentals.csv`

```
必需字段:
  year, gdp_growth, m2_growth, term_spread, credit_spread,
  market_return, consumer_conf, epu_china

数据源:
  - GDP/M2: 国家统计局 / WIND
  - 利差: 中国债券信息网 / 国泰安 CSMAR
  - 沪深300: CSMAR / Tushare
  - 消费者信心: 国家统计局消费者信心指数
  - EPU: Baker, Bloom & Davis 中国 EPU (policyuncertainty.com)
```

#### 动作 1.3：银行基本面控制变量文件

**文件**: `config/bank_fundamentals.csv` 或 `data_excel/bank_fundamentals.xlsx`

```
必需字段:
  bank_name, year, total_assets, equity_ratio, roa, roe,
  npl_ratio, provision_coverage, deposit_ratio, loan_ratio

来源:
  - 银行年报 / CSMAR 银行数据库 / WIND 金融库
  - 资本充足率 / 不良率 / 拨备覆盖率: 银保监会年报

合并位置:
  45_panel_export_main.py → 步骤 7 后新增 merge 步骤
  → panel = panel.merge(bank_fund, on=['target_bank', 'year'], how='left')
```

---

### 阶段二：实证模型重构与检验 (Day 6-12)

#### 动作 2.1：核心回归设定

**参照论文 Equation (3)**:

```stata
* === 基线回归 ===
reghdfe LH_total_gta  unexp_neg_beliefs_full  exp_neg_beliefs_full  ///
    ln_gta  capital_ratio  earnings  hhi  population  tobins_q  cashflows  ///
    corporate_sent  investor_sent  consumer_sent  epu_china  ///
    , absorb(target_bank_id quarter_id)  ///
      cluster(target_bank_id year)

* === 异质性: 低流动性 vs 高流动性 ===
* 按 LH_total_gta 前四期均值的中位数分组
bysort target_bank_id (year): egen avg_lh_prior = mean(L.LH_total_gta) if _n <= 4
xtile liq_group = avg_lh_prior, nq(2)

reghdfe LH_total_gta  unexp_neg_beliefs_full  exp_neg_beliefs_full  ///
    [controls]  if liq_group == 1, absorb(i) cluster(i year)
reghdfe LH_total_gta  unexp_neg_beliefs_full  exp_neg_beliefs_full  ///
    [controls]  if liq_group == 2, absorb(i) cluster(i year)

* === 异质性: 流动性不确定性 ===
* 使用项目已有的 llm_vote_tone_std_full 作为不确定性代理
xtile uncert_group = llm_vote_tone_std_full, nq(2)
```

#### 动作 2.2：IV 回归（利用现有 Bartik 体系）

```stata
* === LASSO 选择 IV (类比论文 LASSO 天气 IV) ===
* 项目已有 29 套 Bartik IV → 用 LASSO 从中选择最优子集

* 第一阶段 F 检验
ivreghdfe LH_total_gta  exp_neg_beliefs_full [controls]  ///
    (unexp_neg_beliefs_full = bartik_type_iv_full bartik_scale_iv_full  ///
     bartik_media_iv_full bartik_mcentral_iv_full)  ///
    , absorb(target_bank_id quarter_id) cluster(target_bank_id year)  ///
      first
```

#### 动作 2.3：稳健性矩阵

| 检验 | 方法 | 对应论文位置 |
|---|---|---|
| 替换情感度量 | 用 dict_avg_tone / bert_avg_pos 替换 LLM 投票情感 | Table 4, Panel A (2)-(4) |
| CEO 固定效应 | 若可获取银行行长/CEO 姓名 → CEO FE | Table 4, Panel A (1) |
| 排除过期情感 | 仅用最近一期情感度量 | Table 4, Panel A (5) |
| 可读性控制 | 已有 `avg_sent_len` / `avg_ttr` / `avg_cpw` | Table 4, Panel A (6) |
| 大/小银行分组 | 按 GTA 中位数分组 | Table 4, Panel B (1)-(2) |
| 情感效应时间衰减 | 领先 1-4 期因变量 | Appendix S9 |

---

### 阶段三：结论重构 (Day 13-15)

#### 动作 3.1：核心发现汇总框架

```
Claim 1: 媒体负面情感（正交化后的非基本面成分）显著增加银行流动性囤积
         → 系数符号 / 统计显著性 / 经济显著性 (1σ → Δ LH/GTA = ? pp)

Claim 2: 效应在流动性约束严格的银行中更强
         → 低流动性组 β > 高流动性组 β, 差异检验 p-value

Claim 3: 效应在前瞻性语言比例较高时更强
         → 利用 forward_looking_ratio 分组 (已有)

Claim 4: 供给驱动而非需求驱动
         → 存贷利差对 unexp_neg_beliefs 正向响应 (需外部利率数据)

Claim 5: Bartik IV 支持因果解释
         → 2SLS 系数方向一致且 F > 10
```

---

## 3. 风险预案 (Plan B)

### 风险点 1：宏观变量时间序列不可得或覆盖年份不足

**Plan B**: 
- 使用年份固定效应 (Year FE) 吸收所有时间序列共同因素，替代逐个宏观变量控制
- 正交分解退化为: `llm_vote_tone ~ bank_province × year FE`，残差仍可解释为"同年同省内个体银行的异常情感"
- 这仍然有效，因为论文的 Location×Year FE 已解释 80% 的变异

### 风险点 2：银行基本面数据合并率低（银行名称不匹配）

**Plan B**:
- 利用项目已有的 `bank_names.json` 别名映射构建 fuzzy matching
- 对无法匹配的银行使用行业均值/中位数填充（并标记 `imputed_fundamentals` 哑变量）
- 在稳健性检验中排除 imputed 观测

### 风险点 3：流动性囤积因变量无法构建（中国商业银行报表可达性问题）

**Plan B**:
- 退化为**可观测的流动性代理**:
  - 流动性比率 = (现金+证券) / 总资产（银保监会公开数据）
  - 存贷比 = 贷款余额 / 存款余额
  - 同业拆借净额 / 总资产
- 或将研究问题重新聚焦于"情感对贷款增速的影响"（贷款增速数据更容易获取）

### 风险点 4：情感正交分解后残差变异过小

**Plan B**:
- 检查 R² 是否异常高（> 0.95）——若是，说明模型过拟合，应剔除部分交互固定效应
- 逐步剔除 Year FE / Province FE / Province×Year FE 的层级，选择 R² ∈ [0.40, 0.85] 的设定
- 报告多种 FE 设定下的结果（类似论文 Appendix S1 的做法）

---

## 附录：文件修改清单

| 文件 | 修改类型 | 内容 |
|---|---|---|
| `config/macro_fundamentals.csv` | **[NEW]** | 宏观基本面时间序列 |
| `data_excel/bank_fundamentals.xlsx` | **[NEW]** | 银行基本面控制变量 |
| `43_panel_indicators_geography.py` | **[MODIFY]** | 新增 `decompose_sentiment_beliefs()` |
| `45_panel_export_main.py` | **[MODIFY]** | 新增银行基本面合并步骤 + 面板增加 unexp/exp beliefs 列 |
| `config/config.yaml` | **[MODIFY]** | 新增 `paths.macro_fundamentals_file` 和 `paths.bank_fundamentals_file` |

> ⚠️ **红线提醒**: 本计划严格遵循"拒绝形式主义"原则。项目现有的 LLM 多模型情感、Bartik IV 体系、媒体权威性加权、双轨消融设计均已逻辑自洽且优于论文方案，一律**维持原状**。改进仅聚焦于论文提示的、项目确实欠缺的**情感正交分解**和**基本面数据合并**两个核心缺口。
