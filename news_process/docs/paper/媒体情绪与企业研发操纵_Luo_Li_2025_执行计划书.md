# 媒体情绪与企业研发操纵 — 执行计划书

> **参考论文**: Luo, Q. & Li, H. (2025). "Media sentiment and corporate R&D manipulation."
> *Finance Research Letters*, 81, 107505.
>
> **项目**: `news_process` 金融研究管线
> **生成日期**: 2026-04-06
> **状态**: 诊断完成 · 待审批执行

---

## 一、论文核心方法论提炼

### 1.1 研究问题与因果链

```
正面媒体情绪 → 投资者乐观 → 管理层迎合 → 向上 R&D 操纵 (Abnormal_RD > 0)
负面媒体情绪 → 业绩压力   → 管理层避险 → 向下 R&D 操纵 (Abnormal_RD < 0)
```

### 1.2 关键变量定义 (Table A.1)

| 变量 | 定义 | 构建方法 | 数据源 |
|------|------|---------|--------|
| **Abnormal_RD** | 异常研发支出 | Gunny (2010) 残差模型: `RD/TA = f(1/TA, MV, TBQ, INT/TA, RD_lag/TA) + ε` | CSMAR |
| **Media_sentiment** | 媒体情绪 | 年度均值: `Σ News_tone / N` (Zhang & Wu, 2021) | Datago / 本管线 LLM |
| **Up_manipulation** | 向上操纵 | `max(Abnormal_RD, 0)` (Zhu et al., 2016) | 衍生变量 |
| **Down_manipulation** | 向下操纵 | `max(-Abnormal_RD, 0)` (Zhu et al., 2016) | 衍生变量 |
| **Turn** | 投资者情绪 | 年度换手率 (Baker & Stein, 2004) | CSMAR |
| **Press** | 业绩压力 | 盈余预期差 (Caskey & Ozel, 2017) | CSMAR |
| **Distance** | IV: 媒企距离 | `ln(平均媒体-企业地理距离)` (Gurun & Butler, 2012) | GIS/管线已有 |
| **Province_news_sentiment** | IV: 省级同行情绪 | Leave-one-out 省平均 (Hsu et al., 2024) | 管线已有 (7d) |

### 1.3 计量框架

**基准回归 (Table 2)**:
```
Abnormal_RD_{i,t} = β₀ + β₁ Media_sentiment_{i,t} + β_c Controls + IndustryFE + YearFE + ε
```

**IV 回归 (Table 3)**:
- IV₁: `Distance` (Gurun & Butler, 2012)
- IV₂: `Province_news_sentiment` (Hsu et al., 2024)
- Cragg-Donald Wald F > 10 (强 IV 检验)

**机制检验 (Table A.3/A.4)**:
- 交互项: `Turn × Media_sentiment`, `Press × Media_sentiment`
- 分组回归: 高/低 Turn, 高/低 Press 中位数分割
- 组间差异: Fisher 置换检验 (bootstrap 2000 次)

### 1.4 稳健性体系

| 检验 | 方法 | 论文定位 |
|------|------|---------|
| 替代指标 | `Media_sentiment_weight` (Piotroski et al., 2017) | Table A.2 Col.1 |
| 熵平衡 | Entropy balancing 处理选择偏差 | Table A.2 Col.2 |
| 省级聚类 | `vce(cluster province)` 空间自相关 | Table A.2 Col.3 |
| 排除 2015 | 删除股灾年度极端情绪 | Table A.2 Col.4 |
| Oster 检验 | δ = -6.05, 有界集 [0.2173, 0.4209] 不含零 | Table 4 |

---

## 二、管线现状诊断与对标映射

### 2.1 完全覆盖 (无需修改)

| 论文需求 | 管线模块 | 对标精度 |
|---------|---------|---------|
| Media_sentiment 年均值 | `41_panel_encode_aggregate.py` → `aggregate_panel()` | ★★★ 完全一致，`llm_vote_tone_full` 即为年度均值 |
| Province_news_sentiment IV | `43_panel_indicators_geography.py` → `compute_leave_one_out_sentiment()` | ★★★ 完全一致，`prov_leave1out_tone_full` 变量已生成 |
| Distance IV 基础设施 | `44_panel_iv_did.py` + `43_panel_indicators_geography.py` → 银行地理信息 | ★★★ `bank_province`/`bank_city` 已合并 |
| 省级聚类标准误 | `43_panel_indicators_geography.py` → `merge_bank_geography()` | ★★★ 31 省级聚类已配置，含 Cameron & Miller (2015) 诊断 |
| VW 权重替代指标 | `41_panel_encode_aggregate.py` → `llm_vote_tone_vw_full` | ★★★ 对标 `Media_sentiment_weight` |
| Fama-MacBeth 标准化 | `43_panel_indicators_geography.py` → `standardize_panel_variables()` | ★★★ `_z` 后缀列可直接用于标准化系数 |
| 多情感度量 LOO IV | G-08 扩展: `prov_leave1out_dict_avg_tone_full` 等 | ★★★ 过度识别检验基础设施 |
| 伪造检验 | `51_falsification_test.py` — Non-Fintech 对照组 | ★★★ Hassan (2019) 范式 |
| Oster 检验 | `51_falsification_test.py` — 已内嵌 Stata 模板 | ★★★ δ 统计量与有界集 |

### 2.2 需要增补的模块 (增量修改)

| 论文需求 | 缺口描述 | 优先级 | 修改位置 |
|---------|---------|--------|---------|
| **Abnormal_RD 构建** | 论文核心因变量，管线未实现 Gunny (2010) 残差模型 | 🔴 P0 | Stata 模板新增 |
| **Up_/Down_manipulation 拆分** | 基于 Abnormal_RD 的方向性操纵指标 | 🔴 P0 | Stata 模板新增 |
| **Turn × Media_sentiment 交互** | 投资者情绪调节效应 | 🟡 P1 | Stata 模板新增 |
| **Press × Media_sentiment 交互** | 业绩压力调节效应 | 🟡 P1 | Stata 模板新增 |
| **Fisher 置换检验** | 组间系数差异检验 (bootstrap 2000) | 🟡 P1 | Stata 模板新增 |
| **排除 2015 股灾** | 删除极端情绪年份 | 🟢 P2 | Stata 模板 (子样本) |
| **熵平衡** | Hainmueller (2012) 重加权法 | 🟢 P2 | Stata (ebalance 包) |

### 2.3 关键诊断: 因变量语境转换

> **⚠️ 核心差异**: 本管线的原始语境是 **银行金融科技新闻** (Fintech tone → 银行行为)。
> Luo & Li (2025) 的语境是 **上市公司一般性新闻** (Media sentiment → R&D 操纵)。
>
> **方法论桥接**: 管线的媒体情绪测度方法（多模型 LLM 集成、LOO IV、地理聚类）
> 完全适用于论文的研究设计。差异仅在于:
> 1. 因变量从管线内部变量 (如 Tobin's Q) 替换为 Abnormal_RD (需从 CSMAR 获取 R&D 数据);
> 2. 控制变量集从银行财务特征扩展为论文的 9 个控制变量。
>
> **结论**: 管线输出的面板 (`.dta` 文件) 中的 `llm_vote_tone_full` 可直接作为
> `Media_sentiment` 的替代度量; `prov_leave1out_tone_full` 直接对标
> `Province_news_sentiment` IV。所有增补工作在 **Stata 端** 完成。

---

## 三、三阶段实施方案

### 阶段 1: 因变量构建 (Stata 端, Gunny 2010)

**目标**: 在 Stata 中实现 Abnormal_RD 残差模型，生成向上/向下操纵变量。

```stata
* ============================================================
* 阶段 1: Abnormal_RD 构建 (Gunny 2010, CAR, 27(3), 855-888)
* ============================================================
* 数据准备: 从 CSMAR 提取以下变量并合并到面板
*   RD      = 研发支出 (R&D expenditure)
*   TA      = 总资产 (Total assets)
*   MV      = ln(市值)
*   TBQ     = Tobin's Q
*   INT     = 营业利润 (Operating income)
*   RD_lag  = 上期研发支出
*   sic2    = 证监会二级行业代码

use "51_panel_with_controls.dta", clear

* ── 合并 CSMAR 财务数据 ──
merge 1:1 target_bank year using "csmar_financial.dta", ///
    keepusing(RD TA MV TBQ INT RD_lag sic2 Age Lev Cashflow ///
              Roa Institution Top1 Board) ///
    keep(match master)

* ── 变量预处理 ──
gen RD_TA     = RD / L.TA           // 研发密度 (以滞后总资产标准化)
gen inv_TA    = 1 / L.TA            // 1/TA_{t-1}
gen INT_TA    = INT / L.TA          // 营业利润密度
gen RD_lag_TA = L.RD / L.TA         // 滞后研发密度

* ── Winsorize (P1/P99) ──
foreach var in RD_TA inv_TA MV TBQ INT_TA RD_lag_TA {
    winsor2 `var', cuts(1 99) replace
}

* ── Abnormal_RD 残差回归 ──
* Gunny (2010, Eq. 3): 按行业-年度分组 OLS, 残差即 Abnormal_RD
* 注: 论文使用 Industry FE 而非逐组回归, 两者等价于 LSDV 框架
reghdfe RD_TA inv_TA MV TBQ INT_TA RD_lag_TA, ///
    absorb(sic2 year) vce(cluster target_bank)
predict Abnormal_RD, resid

* ── 方向性操纵变量 (Zhu et al. 2016) ──
gen Up_manipulation   = cond(Abnormal_RD > 0, abs(Abnormal_RD), 0)
gen Down_manipulation = cond(Abnormal_RD < 0, abs(Abnormal_RD), 0)

* ── 描述性统计校验 ──
* 论文 Table 1: Abnormal_RD mean=0.0251, SD=0.8450
summarize Abnormal_RD Up_manipulation Down_manipulation, detail

label variable Abnormal_RD     "Abnormal R&D (Gunny 2010, residual)"
label variable Up_manipulation  "Upward R&D Manipulation (|Abnormal_RD| if >0)"
label variable Down_manipulation "Downward R&D Manipulation (|Abnormal_RD| if <0)"

save "panel_with_rd_manipulation.dta", replace
```

### 阶段 2: 基准回归与内生性处理

**目标**: 复现 Table 2 (OLS) + Table 3 (2SLS) + Table 4 (Oster)。

```stata
* ============================================================
* 阶段 2: 基准回归 + IV + Oster 检验
* ============================================================

use "panel_with_rd_manipulation.dta", clear

* ── 核心自变量映射 ──
* 管线 llm_vote_tone_full → Media_sentiment (论文)
* 可同时使用 llm_vote_tone_vw_full 作为 Media_sentiment_weight 替代指标
rename llm_vote_tone_full  Media_sentiment
rename llm_vote_tone_vw_full Media_sentiment_weight

* ══════════════════════════════════════════════════════════════
* 2.1 基准回归 (Table 2)
* ══════════════════════════════════════════════════════════════

* Col. (1): 无控制变量
reghdfe Abnormal_RD Media_sentiment, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store base_1
* 预期: β₁ > 0, p < 0.01

* Col. (2): 全控制变量
reghdfe Abnormal_RD Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store base_2
* 预期: β₁ ≈ 0.42, t ≈ 8.09

* ══════════════════════════════════════════════════════════════
* 2.2 稳健性检验 (Table A.2)
* ══════════════════════════════════════════════════════════════

* Col. (1): 替代指标 Media_sentiment_weight
reghdfe Abnormal_RD Media_sentiment_weight ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store robust_1

* Col. (2): 熵平衡 (需安装: ssc install ebalance)
* 按 Media_sentiment 中位数分为处理/对照组
gen treat = Media_sentiment > r(p50)
ebalance treat Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    gen(eweight)
reghdfe Abnormal_RD Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    [pw=eweight], ///
    absorb(sic2 year) vce(cluster target_bank)
    est store robust_2

* Col. (3): 省级聚类标准误
* 使用管线已生成的 bank_province 列
reghdfe Abnormal_RD Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster bank_province)
    est store robust_3

* Col. (4): 排除 2015 股灾
reghdfe Abnormal_RD Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if year != 2015, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store robust_4

* ══════════════════════════════════════════════════════════════
* 2.3 IV 回归 (Table 3)
* ══════════════════════════════════════════════════════════════

* IV₁: Distance (Gurun & Butler, 2012)
* → 需从 bank_addresses.json 和媒体地理数据计算平均距离
* 管线 43 模块已有银行地理信息, Distance 需额外计算

* IV₂: Province_news_sentiment (管线已有)
* → prov_leave1out_tone_full (43_panel_indicators_geography.py 步骤 7d)
rename prov_leave1out_tone_full Province_news_sentiment

* 2SLS with Distance only
ivreghdfe Abnormal_RD ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    (Media_sentiment = Distance), ///
    absorb(sic2 year) cluster(target_bank)
    est store iv_1
* 报告: Cragg-Donald Wald F statistic (论文 = 69.03)
estat firststage

* 2SLS with Province_news_sentiment only
ivreghdfe Abnormal_RD ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    (Media_sentiment = Province_news_sentiment), ///
    absorb(sic2 year) cluster(target_bank)
    est store iv_2
* 报告: Cragg-Donald Wald F statistic (论文 = 536.576)
estat firststage

* ══════════════════════════════════════════════════════════════
* 2.4 Oster (2019) 遗漏变量检验 (Table 4)
* ══════════════════════════════════════════════════════════════

* 安装: ssc install psacalc
* R_max = 1.3 × R² (short → full)

* Short regression (仅 Media_sentiment)
qui reghdfe Abnormal_RD Media_sentiment, ///
    absorb(sic2 year) vce(cluster target_bank)
local r2_short = e(r2)
local beta_short = _b[Media_sentiment]

* Full regression (+ Controls)
qui reghdfe Abnormal_RD Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
local r2_full = e(r2)
local beta_full = _b[Media_sentiment]

* R_max = 1.3 * R²_full
local r_max = 1.3 * `r2_full'

* δ 统计量
psacalc delta Media_sentiment, ///
    rmax(`r_max') beta(`beta_full') r2dxj(`r2_full') model(reghdfe)
* 论文: δ = -6.045, bounded set = [0.2173, 0.4209]

psacalc beta Media_sentiment, ///
    rmax(`r_max') delta(1)
* 论文: β*(δ=1, R_max=1.3R) 不含零 → 排除遗漏变量偏误
```

### 阶段 3: 机制分析 (Further Analysis)

**目标**: 复现 Table A.3 (Down_manipulation) + Table A.4 (Up_manipulation)。

```stata
* ============================================================
* 阶段 3: 机制分析 — 投资者情绪 & 业绩压力
* ============================================================

use "panel_with_rd_manipulation.dta", clear
rename llm_vote_tone_full Media_sentiment

* ── 构建调节变量 ──

* Turn: 年度换手率 (Baker & Stein, 2004)
* 从 CSMAR 股票交易数据计算
* Turn = Σ(日交易量) / 流通股本

* Press: 业绩压力 (Caskey & Ozel, 2017)
* Press = 1 if 实际盈余 < 分析师预期盈余, 0 otherwise
* 从 CSMAR 分析师预测数据构建

* ── 生成交互项 ──
gen Turn_x_Sentiment  = Turn * Media_sentiment
gen Press_x_Sentiment = Press * Media_sentiment

* ── 分组变量 ──
egen Turn_med  = median(Turn)
gen high_Turn  = Turn >= Turn_med
egen Press_med = median(Press)
gen high_Press = Press >= Press_med

* ══════════════════════════════════════════════════════════════
* 3.1 向下操纵检验 (Table A.3)
* ══════════════════════════════════════════════════════════════

* Col. (1): Turn 交互项
reghdfe Down_manipulation Turn Media_sentiment Turn_x_Sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_1
* 预期: β(Media_sentiment) < 0, β(Turn×Sentiment) 不显著

* Col. (2): Press 交互项
reghdfe Down_manipulation Press Media_sentiment Press_x_Sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_2
* 预期: β(Press×Sentiment) < 0, p < 0.05

* Col. (3)/(4): 投资者情绪分组
reghdfe Down_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Turn == 1, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_high_senti

reghdfe Down_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Turn == 0, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_low_senti

* Col. (5)/(6): 业绩压力分组
reghdfe Down_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Press == 1, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_high_press

reghdfe Down_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Press == 0, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store down_low_press

* Fisher 置换检验 (bootstrap 2000 次)
* 使用 permtest 或手动置换程序检验组间系数差异
* 论文 Table A.3: P value for difference (Press) = 0.045

* ══════════════════════════════════════════════════════════════
* 3.2 向上操纵检验 (Table A.4)
* ══════════════════════════════════════════════════════════════

* Col. (1): Turn 交互项
reghdfe Up_manipulation Turn Media_sentiment Turn_x_Sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_1
* 预期: β(Turn×Sentiment) > 0, p < 0.01

* Col. (2): Press 交互项
reghdfe Up_manipulation Press Media_sentiment Press_x_Sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_2
* 预期: β(Press×Sentiment) 不显著

* Col. (3)/(4): 投资者情绪分组
reghdfe Up_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Turn == 1, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_high_senti

reghdfe Up_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Turn == 0, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_low_senti

* Col. (5)/(6): 业绩压力分组
reghdfe Up_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Press == 1, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_high_press

reghdfe Up_manipulation Media_sentiment ///
    Size Lev Cashflow Age Fix Roa Institution Top1 Board ///
    if high_Press == 0, ///
    absorb(sic2 year) vce(cluster target_bank)
    est store up_low_press

* Fisher 置换检验
* 论文 Table A.4: P value (Turn) = 0.090

* ══════════════════════════════════════════════════════════════
* 导出回归表
* ══════════════════════════════════════════════════════════════
esttab base_1 base_2 robust_* using "table_baseline.tex", ///
    se star(* 0.1 ** 0.05 *** 0.01) label nomtitles replace

esttab iv_1 iv_2 using "table_iv.tex", ///
    se star(* 0.1 ** 0.05 *** 0.01) label nomtitles replace

esttab down_* using "table_down_manipulation.tex", ///
    se star(* 0.1 ** 0.05 *** 0.01) label nomtitles replace

esttab up_* using "table_up_manipulation.tex", ///
    se star(* 0.1 ** 0.05 *** 0.01) label nomtitles replace
```

---

## 四、管线 → 论文变量映射速查表

| 论文变量 | 管线输出变量 | 文件来源 | 备注 |
|---------|-------------|---------|------|
| Media_sentiment | `llm_vote_tone_full` | `41_panel_encode_aggregate.py` | 主指标 |
| Media_sentiment_weight | `llm_vote_tone_vw_full` | 同上 | 权威加权指标 |
| (备用度量 1) | `dict_avg_tone_full` | 同上 | 词典法均值 |
| (备用度量 2) | `bert_avg_pos_full` | 同上 | BERT 正面概率 |
| Province_news_sentiment | `prov_leave1out_tone_full` | `43_panel_indicators_geography.py` | LOO IV |
| (城市级 IV) | `city_leave1out_tone_full` | 同上 | 扩展 IV |
| Distance 基础 | `bank_province` / `bank_city` | 同上 | 地理信息 |
| 省级聚类 | `bank_province` | 同上 | 31 省 |
| 城市级聚类 | `bank_city` | 同上 | 329 市 |
| 媒体权威 | `llm_vote_tone_mw_full` | 同上 | Holzman (2023) |
| _z 标准化 | `llm_vote_tone_full_z` | 同上 | Fama-MacBeth |
| Overid IV₁ | `prov_leave1out_dict_avg_tone_full` | 同上 (G-08) | Hansen J |
| Overid IV₂ | `prov_leave1out_bert_avg_pos_full` | 同上 (G-08) | Hansen J |

---

## 五、约束声明

### 5.1 反形式主义红线

本计划严格遵守以下约束:

1. **零代码修改**: 管线 Python 代码不做任何修改。所有增量工作在 **Stata 端** 完成。
2. **无冗余模块**: 不新增 Python 模块。词典法 (`22_tone_words.py`) 已作为稳健性备选保留。
3. **可追溯性**: 每个 Stata 命令均标注对应的论文表格编号和方法论来源。
4. **幂等性**: Stata 脚本可重复运行，不依赖管线内部状态变化。

### 5.2 数据依赖清单

| 外部数据 | 来源 | 字段 | 用途 |
|---------|------|------|------|
| R&D 支出 | CSMAR | RD, RD_lag | Abnormal_RD (Gunny 2010) |
| 财务指标 | CSMAR | TA, MV, TBQ, INT | 残差模型自变量 |
| 控制变量 | CSMAR | Size, Lev, Cash, Age, Fix, Roa | 基准回归 |
| 治理结构 | CSMAR | Institution, Top1, Board | 控制变量 |
| 换手率 | CSMAR | Turn | 调节变量 (Baker & Stein 2004) |
| 盈余预期 | CSMAR | EPS forecast vs actual | Press (Caskey & Ozel 2017) |
| 行业代码 | CSMAR | sic2 | Industry FE |

---

## 六、验证计划

### 6.1 描述性统计对标

| 变量 | 论文均值 | 论文 SD | 对标策略 |
|------|---------|---------|---------|
| Abnormal_RD | 0.0251 | 0.8450 | 构建后比对 |
| Media_sentiment | 0.5025 | 0.1419 | `sum llm_vote_tone_full` 验证量级 |

### 6.2 回归系数对标

- Table 2 Col.(2): β₁ ≈ 0.42, t ≈ 8.09
- Table 3 Col.(2): IV β₁ ≈ 3.16, t ≈ 3.73 (Distance)
- Table 3 Col.(4): IV β₁ ≈ 0.50, t ≈ 1.76 (Province_news_sentiment)
- Oster: δ ∈ [-6.05, ∞), bounded set 不含零

### 6.3 管线输出完整性校验

```python
# 在 Python 中验证面板输出包含所有必要变量
import pandas as pd
panel = pd.read_parquet('data_processed/51_panel_with_controls.parquet')

required_cols = [
    'target_bank', 'year',
    'llm_vote_tone_full', 'llm_vote_tone_vw_full',
    'prov_leave1out_tone_full', 'city_leave1out_tone_full',
    'bank_province', 'bank_city',
    'llm_vote_tone_full_z',
]
missing = [c for c in required_cols if c not in panel.columns]
assert not missing, f"缺失变量: {missing}"
print(f"✓ 面板含 {len(panel)} 行, 所有必需变量已就位")
```

---

## 七、参考文献

| 编号 | 引用 | 用途 |
|------|------|------|
| [1] | Luo, Q. & Li, H. (2025). FRL, 81, 107505. | 主参考论文 |
| [2] | Gunny, K.A. (2010). CAR, 27(3), 855-888. | Abnormal_RD 定义 |
| [3] | Zhu, H., Wang, D., & Li, T. (2016). 南开管理评论, 19(4), 36-48. | Up/Down manipulation |
| [4] | Baker, M. & Stein, J.C. (2004). JFM, 7(3), 271-299. | Turn 定义 |
| [5] | Caskey, J. & Ozel, N.B. (2017). JAE, 63, 121-141. | Press 定义 |
| [6] | Gurun, U.G. & Butler, A.W. (2012). JF, 67(2), 561-598. | Distance IV |
| [7] | Hsu, Y. et al. (2024). EFM, 30, 1587-1617. | Province_news_sentiment IV |
| [8] | Oster, E. (2019). JBES, 37(2), 187-204. | 遗漏变量检验 |
| [9] | Piotroski, J.D. et al. (2017). JLE, 60(1), 1-33. | 加权指标 |
| [10] | Cameron, A.C. & Miller, D.L. (2015). JHR, 50(2), 317-372. | 聚类推断 |
| [11] | Zhang, Z. & Wu, Z. (2021). 管理世界, 37(1), 170-185. | 情绪测度 |
| [12] | Goldsmith-Pinkham, P. et al. (2020). AER, 110(8), 2586-2624. | Bartik IV |
