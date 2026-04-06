# 《Using Machine Learning to Measure Conservatism》项目分析与执行计划书

> [!IMPORTANT]
> 本报告基于顶刊论文《Using Machine Learning to Measure Conservatism》（Bertomeu, Cheynel, Liao & Milone, 2021, JAR/CAR）的理论框架，结合 `F:\WiseSearch\data_antigravity_project\news_process` 目录下的银行金融科技新闻流水线现状进行深度对标与诊断。
> 全文力求**拒绝形式主义**，以**最高学术标准**实现从"理论洞察"到"代码工程"的硬核映射。

---

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 论文核心方法论精要

**核心创新点：** Bertomeu et al. (2021) 提出了一种基于神经网络的"机器学习保守性度量"（Machine Learning Conservatism, MLC），通过**放松函数形式限制**来改进会计稳健性（Conservatism）的实证测度。相较于传统的线性模型（Basu 1997 的差异及时性、Khan & Watts 2009 的 C-Score），MLC 具有以下核心优势：

| 维度 | 线性模型 (KW C-Score) | 神经网络 (MLC2) |
|------|----------------------|----------------|
| **函数形式** | 强制线性：$c(Y_i) = \lambda_0 + \lambda_1 Size + \lambda_2 M/B + \lambda_3 Lev$ | 半参数化：$c(Y_i) = f_{NN}(Y_i)$，任意非线性 |
| **特征数** | 3个 (Size, M/B, Leverage) | 8个 (+Volatility, NOAcc, CFOA, InvCycle, Age) |
| **约束条件** | 无正则化 | 强制 $g(·) > 0$, $g(·)+c(·) > 0$（指数激活函数） |
| **拟合度 $R^2$** | 0.269 (L1y) | **0.523** (MLC2y), **0.478** (MLC2) |
| **时间稳定性** | Spearman $\rho_{t-1,t}$ = 0.678 | Spearman $\rho_{t-1,t}$ = **0.831** |
| **误设定稳健性** | MAE 常超 1 个标准差 | MAE ≈ 0.5 标准差（全 DGP 下最优） |

**核心公式（Eq 1.1）：**
$$X_i = \underbrace{f(Y_i) + R_i g(Y_i) + R_i D_i c(Y_i) + D_i d(Y_i)}_{=m(Y_i, R_i)} + \epsilon_i$$

其中 $c(Y_i)$ 即为保守性度量（C-Score），论文关键贡献在于**不预设 $c(·)$ 的参数形式**，而是由神经网络自动学习。

### 2. 范式映射与盲区诊断

#### 2.1 映射点：论文逻辑 → 项目架构

论文的核心学术命题是：**传统保守性度量（线性 C-Score）受制于Pre-specified的函数形式，大量"信息性变异（informative variation）"被丢弃为噪声**。这一命题直接映射到当前项目的以下结构性痛点：

**映射关系表：**

| 论文概念 | 项目等价物 | 当前实现 | 诊断 |
|---------|-----------|---------|------|
| **差异及时性（Differential Timeliness）** | 新闻情感对银行绩效的不对称响应 | `22_tone_words.py` 词典法 + `23_tone_berts.py` BERT | ⚠️ 词典法为线性映射（$\pm 1$ 极性），等同于论文批判的 L1 模型 |
| **函数形式约束** | 情感量化方法的表达力上限 | 词典法：$\text{score} = \frac{\sum w_i}{n}$（归一化线性加性） | 🔴 完全线性，无特征交互，无非线性捕获能力 |
| **多特征交互** | 情感的上下文依赖 | BERT 滑动窗口 + 概率加权 (`23_tone_berts.py` L380-450) | ✅ 已部分实现（BERT 本身具有非线性能力） |
| **半参数估计** | ML 辅助的情感度量 | LLM 多模型投票 (`21_tone_llms.py`) | ✅ 已实现（LLM 是比 NN 更强的半参数估计器） |
| **时间稳定性验证** | 年际一致性检测 | `34_tone_validation.py` L660-754: Spearman 趋势检验 | ✅ 已实现（temporal_drift 检验） |
| **误设定分析（MAE 矩阵）** | 跨方法稳健性 | `34_tone_validation.py`: Cronbach's α + 相关矩阵 | ⚠️ 逻辑相似但未实现完整的交叉 DGP 蒙特卡洛模拟 |
| **重述事件检验** | 外部事件触发验证 | `51_falsification_test.py`: Hassan (2019) 伪造检验 | ✅ 方向一致（外部验证逻辑） |

#### 2.2 核心盲区识别

**盲区 A：词典法的"线性陷阱"与论文的直接矛盾**

论文 Table 3 以不可辩驳的数据证明：**即使一个极简的8特征线性模型 L2（36个参数），其 $R^2 = 0.316$ 也远超3特征线性模型 L1 的 $R^2 = 0.109$**。而词典法 (`22_tone_words.py`) 的数学本质是：

$$\text{Norm\_Score} = \frac{\sum_{w \in \text{dict}} \text{polarity}(w) \times \text{degree}(w) \times \text{negation}(w)}{|\text{matched words}|}$$

这是一个**零维交互、纯加性、固定权重**的映射，比论文批判的最弱基准模型 L1 还要简陋。尽管 `22_tone_words.py` 加入了否定词/程度副词/转折连词等语言学规则（L120-354），但所有这些仍然是**局部的、串行的、预定义的**修正，根本无法捕获论文强调的"多特征非线性交互"。

**盲区 B：缺少"保守性"这一会计维度的度量**

论文的核心贡献是提出了一个**会计层面**的度量框架。当前项目虽然拥有完善的"情感"度量体系（词典/BERT/LLM 三角验证），但完全**缺失"保守性"这一独立的会计特征维度**。在银行金融科技研究中，保守性具有特殊含义：
- **资产减值的及时性**：银行对金融科技投资失败的损失确认速度
- **利润确认的不对称性**：金融科技业务带来收入时确认较慢，亏损时确认较快

这一维度在当前面板（`41_panel_encode_aggregate.py`）中完全空白。

**盲区 C：缺少半参数情感估计的基础设施**

论文的 MLC 使用定制神经网络（Fig 1-2）以 ensemble 方式（100个种子求均）训练。当前项目中：
- LLM 投票（`21_tone_llms.py`）是最接近"半参数估计"的方法，但其输出是**离散的三类标签**，而非连续的 C-Score
- BERT 概率（`23_tone_berts.py`）输出连续值，但属于**预训练模型的迁移学习**，而非论文提出的**针对特定关系的半参数拟合**

### 3. 实质性改进项（宁缺毋滥）

#### 改进 A：将"保守性度量"引入面板特征（核心攻坚）

- **论文依据**：论文 Eq(1.1) 定义了差异及时性的完整结构，MLC2 使用 8 个经济特征以神经网络半参数地估计 c(Y_i)
- **预期边际贡献**：在当前 Bank-Year 面板中新增"保守性"维度变量，利用银行财务数据（来自 CSMAR/Wind/CNRDS）构建中国银行业的保守性代理变量。具体方案为：
  1. **KW C-Score 基准实现**：用 Khan & Watts (2009) 的线性方法，基于银行规模、市账率、杠杆率，逐年回归提取 C-Score（作为基准控制变量）
  2. **MLC-Style 升级（可选）**：如数据量允许，训练一个简单的神经网络来替代线性 C-Score，引入更多银行财务特征（资产波动率、经营现金流、不良贷款率等）
  3. **面板交互**：将保守性度量与金融科技情感交叉，检验"保守银行对金融科技坏消息是否更敏感"——这是论文"差异及时性"逻辑在金融科技语境中的直接应用

#### 改进 B：以论文的验证框架升级情感度量的内部对标

- **论文依据**：论文 Table 4（MAE 矩阵）展示了"交叉 DGP 稳健性"的验证范式——每个模型假设自己是真实 DGP，看其他模型的恢复能力
- **预期边际贡献**：在 `34_tone_validation.py` 中增加一组"交叉度量稳健性"检验：
  1. 以每种方法（词典/BERT/LLM）的输出作为"假设真值"
  2. 计算其他方法对该"假设真值"的 MAE/相关系数
  3. 此矩阵直接回答"哪种方法最具稳健性代表力"，复现论文 Table 4 的诊断逻辑

#### 改进 C：以 Spearman 自相关分析替换/增强时间稳定性检验

- **论文依据**：论文 Table 7 展示了 1/2/5 年自相关系数，是度量质量的"黄金标准"
- **预期边际贡献**：当前 `34_tone_validation.py` 已有年际趋势检验（temporal_drift），但**缺少论文提出的"度量层面自相关"分析**。新增功能：
  1. 对每种情感度量，计算 Bank-Year 面板中相同银行的 $\rho_{t-1,t}$、$\rho_{t-2,t}$、$\rho_{t-5,t}$ 的 Spearman 和 Pearson 自相关
  2. 预期 LLM 投票指标的自相关应高于词典法（平行于论文中 MLC > KW 的结论）
  3. 产出 Table 7 格式的 LaTeX 输出

### 4. 冗余剥离

> [!WARNING]
> 必须"下狠手"剔除毫无学术增量、甚至阻碍结论稳健性的伪需求模块。

- **降级 `22_tone_words.py`（静态词典法模块）至纯稳健性检验角色**：论文 Table 3 已铁证如山地证明，线性加性度量（$R^2 = 0.109$）的信息捕获能力不到非线性方法的四分之一。当前词典法在学术逻辑上等同于论文中被全面碾压的 L1 模型。**如之前多份执行计划已一致建议：词典法不应再作为主要度量方法，仅保留为稳健性检验的对照基准。** 如果已在其他执行计划中完成此降级，则本项不重复执行。

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布

| 优先级 | 改进项 | 工程复杂度 | 学术增量 | 前置依赖 |
|--------|--------|-----------|---------|---------|
| 🔴 高 | **改进 A**：保守性度量引入面板 | 高（需外部财务数据） | 极高（新增独立维度） | CSMAR/Wind 银行财务年报数据 |
| 🟡 中 | **改进 B**：交叉 DGP 稳健性矩阵 | 中（扩展已有验证模块） | 高（方法论贡献） | 阶段 34 已完成 |
| 🟢 低 | **改进 C**：自相关稳定性分析 | 低（仅面板计算） | 中等（验证增强） | 阶段 45 已完成 |

### 2. 阶段化执行指令 (SOP)

#### 阶段一：保守性特征提取基础设施（改进 A — 核心）

**【前置条件】** 需要获取中国上市银行的结构化财务数据（年报级别），包括：
- 总资产（Size）、市账率（M/B）、杠杆率（Leverage）
- 资产波动率（Volatility）、经营现金流/总资产（CFOA）
- 不良贷款率（NPL Ratio，银行特有）、拨备覆盖率（Provision Coverage）
- 累计股票收益率（Return）、负回报哑变量（$D_i = 1$ if $R_i < 0$）

**【动作 1】** 新建脚本 `60_conservatism_score.py`，实现以下逻辑：

```python
# 步骤 1: 加载银行年报财务数据 (Parquet/CSV from CSMAR/Wind)
# 步骤 2: 逐年 OLS 回归 Khan & Watts (2009):
#   X_i = β_0 + β_1*D_i + R_i*(μ_1 + μ_2*Size + μ_3*MB + μ_4*Lev)
#                       + R_i*D_i*(λ_1 + λ_2*Size + λ_3*MB + λ_4*Lev)
#                       + (δ_1*Size + δ_2*MB + δ_3*Lev) + ε
# 步骤 3: 提取 C-Score = λ_1 + λ_2*Size_i + λ_3*MB_i + λ_4*Lev_i
# 步骤 4: P1/P99 Winsorization (与 22_tone_words.py build_idf_weights 同构)
# 步骤 5: 存储为 {Bank, Year, CScore, GScore} 的 Parquet
```

**【动作 2】** 修改 `45_panel_export_main.py`，在面板构建步骤 7c（银行地理信息合并）后新增步骤 7f：

```python
# --- 7f. 银行保守性度量合并 ---
# 从 60_conservatism_score.py 的输出中按 (target_bank, year) left join
# 新增列: kw_cscore, kw_gscore
# Stata 标签: 'KW C-Score (Conservatism)', 'KW G-Score (Timeliness)'
```

**【动作 3】** 在 `config.yaml` 中注册新阶段：

```yaml
# conservatism_measurement:
#   enabled: true
#   data_source: "config/bank_financials.csv"  # 银行财务数据路径
#   features: [size, mb_ratio, leverage, volatility, cfoa, npl_ratio]
#   winsorize: [0.01, 0.99]
#   method: "kw_linear"  # 或 "mlc_neural" (高级模式)
```

#### 阶段二：交叉 DGP 稳健性矩阵（改进 B）

**【直接指示】** 在 `34_tone_validation.py` 中新增函数 `cross_dgp_robustness_matrix()`：

```python
def cross_dgp_robustness_matrix(all_scores_df: pd.DataFrame,
                                 track: str = '_full') -> pd.DataFrame:
    """
    复现 Bertomeu et al. (2021) Table 4 的交叉 DGP MAE 矩阵。

    逻辑:
      对于每对 (方法A, 方法B):
        1. 假设方法A的输出为"真值" C_true
        2. 计算方法B对 C_true 的 MAE: E[|C_B - C_A|]
        3. 以方法A的标准差归一化: MAE / std(C_A)
      
      输出: 对称矩阵，行=估计方法，列=假设DGP
      对角线为0（自身完美匹配），非对角线越小越好

    学术依据:
      Bertomeu, J., Cheynel, E., Liao, Y. & Milone, M. (2021).
      "Using Machine Learning to Measure Conservatism."
      Table 4: Model mean absolute errors (MAE)
    """
```

**预期产出**：一个 N×N 矩阵（N = 方法数），行表示使用的估计模型，列表示假设的真实 DGP。最稳健的方法应在所有列中表现一致（MAE 最低）。

#### 阶段三：度量自相关稳定性分析（改进 C）

**【直接指示】** 在面板导出阶段（`45_panel_export_main.py` 的 `log_diagnostics()` 之后）或 `34_tone_validation.py` 中新增：

```python
def compute_measure_autocorrelations(panel: pd.DataFrame, 
                                      tone_cols: list,
                                      lags: list = [1, 2, 5]) -> dict:
    """
    复现 Bertomeu et al. (2021) Table 7: 度量层面的时间自相关。

    对每个 tone_col:
      1. 按 target_bank 分组
      2. 计算 lag=1,2,5 年的 Spearman 和 Pearson 相关
      3. 仅保留连续观测的银行（排除缺失年份）

    学术依据:
      Givoly et al. (2007) 提出度量应具有时间持续性
      Bertomeu et al. (2021) Table 7 以此验证 MLC > KW

    预期结论:
      LLM 投票指标的自相关 > 词典法自相关（平行于 MLC > L1y）
      BERT 指标应介于两者之间
    """
```

### 3. 风险预案 (Plan B)

> [!CAUTION]
> 致命卡点预判与挽救措施

- **潜在卡点 1**：中国银行业样本量问题。论文使用 US Compustat 的 229,387 firm-year 观测训练神经网络。中国上市银行仅约 42 家（A 股），年度财务数据的 Bank-Year 面板通常仅有 ~500 行。**这意味着 MLC 的神经网络方法在小样本情境下可能严重过拟合。**
  - **替代方案**：放弃 MLC 的神经网络实现，退守 KW 线性 C-Score（L1y 级别），并将其作为纯控制变量（而非核心度量）引入面板。小样本下线性方法反而更稳健（论文 Table 4 中 L2 在自身 DGP 下 MAE = 0.058，远优于过拟合的复杂模型）。

- **潜在卡点 2**：银行财务数据可得性。如无法获取完整的 CSMAR/Wind 银行年报数据。
  - **替代方案**：直接使用银行年报 PDF 的文本分析（已有 OCR 基础设施 `papers/` 目录），通过 LLM 提取关键财务指标（总资产、净利润、不良率），作为 C-Score 计算的数据源。

- **潜在卡点 3**：保守性维度与金融科技情感的交叉效应不显著。
  - **替代方案**：保留 C-Score 为面板控制变量（而非交叉项），在 Stata 回归模版（`51_falsification_test.py` L778-850）中仅作为右侧控制量出现，用于"对冲"因银行保守性差异带来的情感量化偏误。

### 4. 与现有模块的兼容性说明

> [!NOTE]
> 本执行计划的所有改进项均为**纯增量操作**，不修改或破坏任何现有模块。

| 现有模块 | 影响 | 说明 |
|---------|------|------|
| `21_tone_llms.py` | 无变更 | LLM 情感提取逻辑不受保守性度量影响 |
| `22_tone_words.py` | 降级（非新增） | 多份执行计划已一致建议降级为稳健性角色 |
| `23_tone_berts.py` | 无变更 | BERT 推理与保守性度量正交 |
| `34_tone_validation.py` | **扩展** | 新增交叉 DGP 矩阵和自相关分析 |
| `41_panel_encode_aggregate.py` | 无变更 | 保守性合并在 45 中进行 |
| `45_panel_export_main.py` | **扩展** | 新增步骤 7f + Stata 标签 |
| `51_falsification_test.py` | **扩展** | Stata 模版新增 C-Score 控制量 |

### 5. Stata 回归模版增量

```stata
* ============================================================
* 保守性度量交叉检验 Stata 模版
* 对标: Bertomeu et al. (2021) + Hassan et al. (2019) 
* ============================================================

use "51_panel_with_controls.dta", clear

* ── 检验 1: 保守性作为控制变量 ──
* 目的: 控制银行固有保守性倾向后, fintech tone 是否保持显著
reghdfe Y llm_vote_tone_full kw_cscore X, ///
    absorb(target_bank year) vce(cluster target_bank)
    est store ctrl_cscore

* ── 检验 2: 保守性的非对称效应 ──
* 目的: 高 vs 低保守性银行, 对金融科技坏消息的反应差异
gen high_cscore = (kw_cscore > r(p50))
gen tone_x_highc = llm_vote_tone_full * high_cscore
reghdfe Y llm_vote_tone_full high_cscore tone_x_highc X, ///
    absorb(target_bank year) vce(cluster target_bank)
    est store asym_cscore

* ── 检验 3: 分样本稳健性 ──
* 论文期望: 高保守性银行对负面金融科技情感更敏感
* (即 tone_x_highc 系数应为负且显著)
```

---

## 参考文献

- Bertomeu, J., Cheynel, E., Liao, Y. & Milone, M. (2021). "Using Machine Learning to Measure Conservatism." *SSRN Working Paper No. 3924961*.
- Basu, S. (1997). "The Conservatism Principle and the Asymmetric Timeliness of Earnings." *Journal of Accounting and Economics*, 24(1), 3-37.
- Khan, M. & Watts, R.L. (2009). "Estimation and Empirical Properties of a Firm-Year Measure of Accounting Conservatism." *Journal of Accounting and Economics*, 48(2-3), 132-150.
- Givoly, D., Hayn, C. & Natarajan, A. (2007). "Measuring Reporting Conservatism." *The Accounting Review*, 82(1), 65-106.
- Ettredge, M., Huang, Y. & Zhang, W. (2012). "Earnings Restatements and Differential Timeliness of Accounting Conservatism." *Journal of Accounting and Economics*, 53(3), 489-503.
- Hassan, T.A., Hollander, S., van Lent, L. & Tahoun, A. (2019). "Firm-Level Political Risk: Measurement and Effects." *The Quarterly Journal of Economics*, 134(4), 2135-2202.
