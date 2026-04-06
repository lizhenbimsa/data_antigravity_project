# 基于《Media Sentiment, Financial Services, and Corporate Investment Levels》的项目分析与执行计划

> **参考论文**: Qu, L., & Yang, R. (2024). "Media sentiment, financial services, and corporate investment levels."
> **项目**: `news_process` — 银行金融科技新闻情感分析与 Bank-Year 面板构建流水线
> **生成日期**: 2026-04-06

---

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断

#### 1.1 论文核心机制提炼

| 维度           | 论文框架                                                     | 当前项目现状                                                   |
| -------------- | ------------------------------------------------------------ | -------------------------------------------------------------- |
| **研究对象**   | 中国 A 股上市公司 (2008-2023)，35,473 公司-年观测值           | 中国银行业金融科技新闻，Bank-Year 面板                           |
| **核心自变量** | `mediasen` — 基于 NLP 的媒体情感指数（连续变量）               | 多源情感指数：LLM 三模型投票 + 词典法 (5本) + BERT (5模型) 的双轨 (full/ctx) 体系 |
| **调节变量**   | `Finratio1` — 金融服务便利度综合指数（熵权法加权：负债率、融资渠道多样性、融资成本） | **缺失** — 当前未构建金融服务便利度变量                          |
| **因变量**     | `invest` — 企业投资水平（购建固定资产等现金/期初总资产）        | **不适用** — 项目因变量为银行金融科技相关指标，非企业投资水平    |
| **交互效应**   | `mediasen × Finratio1` — 金融服务对媒体情感→投资的调节效应     | **缺失** — 未构建交互项机制                                     |
| **异质性检验** | (1) 收入增速高/低分组 (2) 上市时长长/短分组                    | 已有分组：银行类型、银行规模、媒体类型等 Bartik IV 分组          |
| **内生性处理** | `finwave`（金融市场波动）作为工具变量，2SLS                    | 已有 29 套 Bartik Shift-Share IV + 省级/城市级/经济圈 LOO IV + DID 双政策冲击 |
| **固定效应**   | 个体 FE + 年份 FE                                            | Bank FE + Year FE (标准配置)                                    |
| **控制变量**   | Board, Dual, Top5, Debtraio, TobinQ, INST, Occupy             | **缺失** — 当前面板无公司治理控制变量                            |
| **稳健性检验** | 替换金融服务代理变量 (Finratio2, Finratio3)                    | 极其丰厚：双轨 (full/ctx)、VW/MW/EW 三种加权、IDF 变体、BERT 变体 |

#### 1.2 真实落差定位

**落差 A：金融服务便利度变量（调节机制）缺失**
> 论文的核心发现是 `Finratio1` 对 `mediasen → invest` 的显著正向调节效应（β₃ = 0.0045***）。当前项目的情感指标构建极其完备，但**完全缺少金融服务/融资便利度维度的变量**。这意味着无法检验"金融服务是否放大或缓解了媒体情感对银行金融科技发展的影响"这一关键调节机制。

**落差 B：公司治理控制变量缺位**
> 论文使用了 Board, Dual, Top5, INST, Occupy 等 7 个治理变量。当前面板缺少等价的银行治理控制变量（如董事会规模、独立董事比例、股权集中度、机构持股比例等），可能导致遗漏变量偏误。

**落差 C：异质性分析维度单一**
> 论文从**收入增长水平**和**上市时长**两个维度做调节效应异质性分析（中位数分组 → 子样本回归）。当前项目虽有丰富的 Bartik IV 维度分组（类型/规模/媒体），但缺少**银行经营绩效**和**成立年限/上市时长**维度的异质性检验。

---

### 2. 实质性改进项

#### 改进 A：构建金融服务便利度综合指数（核心调节变量）

- **具体修改建议**: 在面板构建阶段 (`43_panel_indicators_geography.py`) 新增金融服务便利度综合指数 `fin_service_index`，采用熵权法对银行级别的以下指标加权合成：(1) 银行资产负债率变动（融资约束代理）；(2) 同区域金融机构密度（Number of Branches per 10k Pop, CBRC 数据）；(3) 数字金融普惠指数（北京大学数字金融研究中心 PKU-DFIIC）。
- **论文依据**: Qu & Yang §4.2 — `Finratio1` 构建方法论（熵权法加权综合）。
- **边际贡献**: 引入调节机制后，可检验 H3-H5 型假设：金融服务便利度是否调节了媒体情感对银行金融科技发展的边际效应，从而揭示"信息—资源互补"的传导路径。这将把项目从单纯的"情感→行为"叙事升级为"情感 × 资源→行为"的交互叙事。

#### 改进 B：补充银行治理控制变量

- **具体修改建议**: 在面板导出阶段 (`45_panel_export_main.py`) 通过 CSMAR/Wind 数据源新增以下控制变量：(1) `board_size`（董事会规模取对数）；(2) `ind_dir_ratio`（独立董事比例）；(3) `top5_share`（前五大股东持股比例）；(4) `inst_share`（机构投资者持股比例）；(5) `npl_ratio`（不良贷款率，银行特有）。
- **论文依据**: Qu & Yang Table 1 — 控制变量定义。
- **边际贡献**: 消除因治理结构差异导致的遗漏变量偏误，提升情感变量系数的因果可信度。

#### 改进 C：新增收入增速与成立年限异质性分组

- **具体修改建议**: 在 `44_panel_iv_did.py` 的 `load_bank_group_maps()` 中新增两个分组映射：(1) `growth_map`：按银行年度营收增速中位数分为高/低增速组；(2) `age_map`：按银行成立年限中位数分为新银行/老银行组。在面板构建后执行分样本回归的交互项检验。
- **论文依据**: Qu & Yang §5.7, Table 8-9 — 调节异质性分析。
- **边际贡献**: 检验金融服务调节效应在不同经营特征银行间的异质性，为差异化监管政策提供微观实证基础。

---

### 3. 冗余剥离

**维持原状，无需剥离。**

> 论文使用的是标准 NLP 媒体情感指数（单一测量方法），而当前项目采用 LLM 三模型投票 + 词典法 (5本) + BERT (5模型) 的三角验证体系，在情感度量的精度和稳健性上**远超论文水平**。项目现有的以下高价值模块均应保留：
>
> - ✅ **多模型 LLM 投票共识机制** (`21_tone_llms.py`) — 论文仅用单一 NLP 方法
> - ✅ **双轨 (full/ctx) 设计** — 论文无此维度
> - ✅ **29 套 Bartik IV** (`44_panel_iv_did.py`) — 论文仅用单一 IV (`finwave`)
> - ✅ **DID 双政策冲击** (DCEP + Sandbox) — 论文无此设计
> - ✅ **Entity Masking / Prompt 敏感性测试** (`36/39`) — 论文无此类稳健性检验
> - ✅ **Media Authority Weighting** (Holzman et al. 2023, TAR) — 论文无此设计

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布

| 优先级  | 改进项                                 | 实施成本 | 预期收益 | 分类         |
| ------- | -------------------------------------- | -------- | -------- | ------------ |
| **P1**  | 构建金融服务便利度综合指数 + 交互项    | 中       | **极高** | 核心攻坚项    |
| **P2**  | 补充银行治理控制变量                   | 低-中    | 高       | 速赢项        |
| **P3**  | 新增收入增速与成立年限异质性分组       | 低       | 中       | 速赢项        |

---

### 2. 阶段化执行指令 (SOP)

---

#### 阶段一：数据准备与变量构建

##### 任务 1.1：金融服务便利度综合指数构建

**目标文件**: `43_panel_indicators_geography.py`（新增函数 `compute_financial_service_index`）

**核心动作**:

1. **数据源准备**:
   - 下载北京大学数字金融普惠指数 (PKU-DFIIC) 省级年度数据 → 存放至 `data_excel/pku_dfiic.xlsx`
   - 从 CBRC/银保监会公开数据获取各省银行业金融机构网点密度 → 存放至 `data_excel/bank_branch_density.csv`
   - 从 Wind/CSMAR 获取样本银行的资产负债率年度数据 → 存放至 `data_excel/bank_leverage.csv`

2. **指数构建逻辑** (熵权法):

   ```python
   def compute_financial_service_index(panel: pd.DataFrame) -> pd.DataFrame:
       """
       构建金融服务便利度综合指数 (Qu & Yang 2024, §4.2)
       
       子指标:
         (1) pku_dfiic_total: 北大数字金融普惠指数 (省级)
         (2) branch_density: 银行机构网点密度 (省级, per 10k pop)
         (3) leverage_ratio: 银行资产负债率 (银行级)
       
       加权方法: 熵权法 (Entropy Weighting Method)
       """
   ```

3. **交互项生成**: 在面板中生成 `mediasen × fin_service_index` 的交互列，供 Stata 回归使用。

**交付物标准**:
- `fin_service_index` 列存在于最终面板 `40_panel_yearly.parquet` 和 `.dta` 中
- 描述性统计输出至日志：mean, std, min, max
- 交互项列名: `llm_vote_tone_x_finserv_full`, `llm_vote_tone_x_finserv_ctx`（双轨）

##### 任务 1.2：银行治理控制变量补充

**目标文件**: `45_panel_export_main.py`（在 main() 的步骤 7c 后新增合并逻辑）

**核心动作**:

1. 准备银行年度治理数据文件 `data_excel/bank_governance.csv`，包含字段:
   - `bank_name`, `year`, `board_size`, `ind_dir_ratio`, `top5_share`, `inst_share`, `npl_ratio`

2. 在面板构建中通过 `(target_bank, year)` 键合并至面板:
   ```python
   panel = panel.merge(governance_df, 
                        left_on=['target_bank', 'year'],
                        right_on=['bank_name', 'year'], 
                        how='left')
   ```

3. 对 `board_size` 取对数: `panel['ln_board_size'] = np.log(panel['board_size'])`

**交付物标准**:
- 5 个治理变量列存在于最终面板中
- 缺失率诊断输出至日志（缺失率 > 30% 时发出警告）
- Stata 变量标签已添加至 `STATA_LABELS` 字典

##### 任务 1.3：异质性分组映射新增

**目标文件**: `44_panel_iv_did.py`（扩展 `load_bank_group_maps`）

**核心动作**:

1. 从 `bank_addresses.json` 或新建的 `bank_characteristics.json` 中读取:
   - 银行年度营收增速 → 按中位数分为 `high_growth` / `low_growth`
   - 银行成立年份 → 与面板年份差值 → 按中位数分为 `young` / `mature`

2. 新增两个映射返回值:
   ```python
   def load_bank_group_maps() -> tuple:
       # ... 现有 type_map, scale_map ...
       growth_map = {}   # {银行名 → 'high_growth' / 'low_growth'}
       age_map = {}      # {银行名 → 'young' / 'mature'}
       return type_map, scale_map, growth_map, age_map
   ```

3. 在 `45_panel_export_main.py` 中调用 `compute_bartik_iv` 生成对应的 Bartik IV 稳健性变体。

**交付物标准**:
- `bank_growth` 和 `bank_age` 列存在于面板中
- 对应 Bartik IV 列已生成

---

#### 阶段二：实证模型重构与检验

##### 任务 2.1：基准回归设定（建议 Stata .do 文件）

**回归方程** (对标论文 Eq.1-3):

```stata
* H1: 媒体情感 → 银行金融科技发展 (基准)
reghdfe Y llm_vote_tone_full Controls, absorb(bank_id year) vce(cluster bank_province)

* H2: 金融服务 → 银行金融科技发展
reghdfe Y fin_service_index Controls, absorb(bank_id year) vce(cluster bank_province)

* H3: 交互效应检验
reghdfe Y llm_vote_tone_full fin_service_index c.llm_vote_tone_full#c.fin_service_index Controls, absorb(bank_id year) vce(cluster bank_province)
```

##### 任务 2.2：内生性处理

**工具变量策略** (对标论文 §5.6):

```stata
* 方案一: Bartik IV (已有, 远超论文 finwave)
ivreghdfe Y Controls (llm_vote_tone_full = bartik_type_iv_full), absorb(bank_id year) cluster(bank_province)

* 方案二: LOO 地理工具变量 (已有)
ivreghdfe Y Controls (llm_vote_tone_full = prov_leave1out_tone_full), absorb(bank_id year) cluster(bank_province)
```

##### 任务 2.3：稳健性检验矩阵

| 检验类型             | 具体方法                                                  | 论文对标        |
| -------------------- | --------------------------------------------------------- | --------------- |
| 替换自变量           | `llm_vote_cont_full` (连续) / `llm_vote_tone_ctx` (上下文) | Table 5         |
| 替换调节变量         | PKU-DFIIC 分指数分别作为 Finratio2/Finratio3 代理          | Table 5         |
| 替换 IV              | 29 套 Bartik IV 逐一检验                                   | **超越论文**    |
| 替换情感度量         | 词典法/BERT 情感 替换 LLM 情感                             | **超越论文**    |
| 加权方案替换         | VW / MW / EW 三种方案                                     | **超越论文**    |
| 双轨消融             | Full 轨道 vs Ctx 轨道 对比                                 | **超越论文**    |

##### 任务 2.4：异质性分析（对标论文 §5.7）

```stata
* H4: 收入增速异质性 (中位数分样本)
* 低增速组
reghdfe Y llm_vote_tone_full fin_service_index c.llm_vote_tone_full#c.fin_service_index Controls if bank_growth=="low_growth", absorb(bank_id year) vce(cluster bank_province)

* 高增速组
reghdfe Y llm_vote_tone_full fin_service_index c.llm_vote_tone_full#c.fin_service_index Controls if bank_growth=="high_growth", absorb(bank_id year) vce(cluster bank_province)

* H5: 成立年限异质性 (中位数分样本)
* 类似逻辑...
```

---

#### 阶段三：结论重构

##### 核心动作:

1. **假设验证映射**: 将回归结果与论文 H1-H5 逐一对照，特别关注：
   - 交互项 `β₃` 的符号和显著性（正向 → 金融服务放大情感效应）
   - 异质性分组中交互项系数的差异显著性（Chow 检验）

2. **叙事升级方向**: 从"媒体情感影响银行金融科技发展"升级为"媒体情感与金融服务便利度共同驱动银行金融科技转型"的交互叙事，突出以下核心发现：
   - 金融服务便利度是否显著调节了媒体情感的传导效率？
   - 该调节效应在不同类型银行间是否存在异质性？
   - 当前项目的多源三角验证和 29 套 IV 体系在内生性控制上远超论文。

---

### 3. 风险预案 (Plan B)

| 致命卡点                                            | 风险等级 | 替代方案                                                      |
| --------------------------------------------------- | -------- | ------------------------------------------------------------- |
| PKU-DFIIC 省级数据无法获取/时间跨度不匹配           | 中       | 使用央行《中国区域金融运行报告》中的"金融机构存贷比"作为替代代理 (省级) |
| 银行治理数据 (board_size 等) 非上市银行缺失严重     | 高       | (1) 仅对上市银行子样本做稳健性检验；(2) 使用银行年报中可获取的"员工人数对数"作为规模控制变量替代 |
| 营收增速数据缺失（部分中小银行未公开）              | 中       | 使用资产规模增速 (总资产 YoY%) 替代营收增速                     |
| 交互项系数不显著                                    | 低       | (1) 检查金融服务指数的变异是否充分（std/mean ratio）；(2) 尝试非线性调节（分组交互替代连续交互） |
| 金融服务指数与情感指数高度共线                       | 低       | (1) 计算 VIF，确保 < 10；(2) 对金融服务指数做正交化 (Frisch-Waugh 分解) |

---

## 附录：与当前项目架构的兼容性评估

| 项目模块                     | 兼容性 | 说明                                                     |
| ---------------------------- | ------ | -------------------------------------------------------- |
| `21_tone_llms.py`            | ✅ 完全兼容 | 情感分析已远超论文水平，无需改动                           |
| `22_tone_words.py`           | ✅ 完全兼容 | 词典法作为三角验证支撑                                     |
| `23_tone_berts.py`           | ✅ 完全兼容 | BERT 作为三角验证支撑                                      |
| `41_panel_encode_aggregate.py` | ✅ 完全兼容 | 双轨聚合框架无需改动                                       |
| `43_panel_indicators_geography.py` | ⚠️ 需扩展 | 新增 `compute_financial_service_index()` 函数             |
| `44_panel_iv_did.py`         | ⚠️ 需扩展 | `load_bank_group_maps()` 新增 `growth_map` 和 `age_map`   |
| `45_panel_export_main.py`    | ⚠️ 需扩展 | 新增治理变量合并 + 金融服务指数步骤 + Stata 标签           |
| `config/config.yaml`         | ⚠️ 需扩展 | 新增数据文件路径配置                                       |

---

> **⚠️ 执行约束**：本文档为分析与规划文档，**严禁未经审批直接修改任何代码或配置文件**。所有改动需逐项审批后方可执行。
