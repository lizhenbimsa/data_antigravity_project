# 基于参考论文的项目分析与执行计划

> **参考论文**: Tan, W., Liu, Y., & Teng, M. (2024). "When ESG news talks: How media sentiment shapes corporate financial behavior in China." *International Review of Financial Analysis*.
>
> **项目**: `F:\WiseSearch\data_antigravity_project\news_process`
>
> **生成日期**: 2026-04-07

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

| 维度 | 论文设计 | 项目现状 | 落差判定 |
|------|---------|---------|---------|
| **研究对象** | A股上市公司 ESG 新闻情感 → 企业金融化 | 商业银行金融科技新闻情感 → Bank-Year 面板 | 研究域不同，非同维可比 |
| **情感测度** | SnowNLP 连续分数 [0,1]，年度均值；FinBERT 稳健性 | 三模型 LLM 多数投票 + 5 本词典 + 5 个 BERT 模型，离散+连续双编码，双轨(Full/Ctx) | **项目远超论文**，维持原状 |
| **主题分类** | LDA 主题模型将新闻分为 E/S/G 三维度 | LLM 判别 + 关键词词典将金融科技新闻分为「底层技术/应用场景」 | 分类维度范式相同（子主题分解），**维持原状** |
| **IV 策略** | 2 个省级报纸 IV（报纸种类数 IV1、人均印刷量 IV2） | 29 套 Bartik Shift-Share IV + 省/市 Leave-one-out 地理 IV + DID 政策冲击 | **项目远超论文**，维持原状 |
| **固定效应** | 公司 + 行业×年 + 省份×年 FE | Bank-Year 面板，支持 bank FE + year FE + 交叉 FE 输出至 Stata | 结构匹配 |
| **媒体权威性** | 官方媒体加权（70/30 方案）；仅保留权威媒体（ESG_major） | Holzman et al. (2023, TAR) 媒体权威性加权 + media_classification.json 四维分类 + 媒体异质性情感缺口 | **项目远超论文**，维持原状 |
| **安慰剂检验** | 跨城市随机打乱 ESG 情感（500 次迭代） | `51_falsification_test.py`（75,875 字节）已实现伪造检验 | 需核实是否包含地理维度打乱 |
| **非目标新闻控制** | 控制非 ESG 新闻情感（NESG）作为遗漏变量纠正 | **无对应模块** — 未构建「非金融科技银行新闻情感」控制变量 | ⚠️ **真实盲区** |
| **遗漏变量压力测试** | 以 Fix 为基准变量，测试 1x/2x/3x 强度下系数稳定性（Oster-style） | 未实现该类可视化压力测试 | ⚠️ **可选改进** |

### 1.2 核心判断

论文的研究范式（ESG 情感 → 企业金融化）与项目的研究范式（金融科技情感 → 银行应用/创新）属于不同研究问题域。论文在 NLP 方法论上使用的 SnowNLP/FinBERT 单模型方案**显著落后于**项目的三模型 LLM 集成 + 多数投票 + 词典 + BERT 五重三角验证体系。论文在计量经济学识别策略上的 2 个省级报纸 IV **远不及**项目已有的 29 套 Bartik IV + 地理 Leave-one-out IV + DID 政策冲击变量。

因此，本诊断的核心结论是：**项目的 NLP 方法论与计量识别策略均优于论文，主体架构应维持原状。** 但论文中有两项具有实质边际贡献的设计值得集成。

---

## 2. 实质性改进项（宁缺毋滥）

### 改进 A：构建「非金融科技银行新闻情感」控制变量 (Non-Fintech Sentiment, NFTS)

- **具体修改建议**: 在面板构建阶段，利用已有的 `12_fintech_news_full.parquet`（含全量银行新闻），将 `is_fintech=False` 的非金融科技银行新闻按 Bank-Year 聚合为独立的情感控制变量 `nfts_tone_{full/ctx}`。
- **论文依据**: Table 2, Columns 2-4 — NESG（非 ESG 新闻情感）系数在 5-10% 水平显著为负（β=-0.0064* 至 β=-0.0068**）。纳入 NESG 后，ESG 系数从 -0.0085 略降至 -0.0066 但仍显著，表明 NESG 能吸收一部分一般性媒体环境效应。
- **预期边际贡献**:
  1. **解决遗漏变量偏误**: 当前面板中金融科技情感指标可能混入一般性银行新闻整体情感环境的效应。加入 NFTS 控制后，能更纯粹地识别金融科技特异性情感的边际影响。
  2. **增强审稿可信度**: 审稿人可能质疑"为什么只用金融科技新闻的情感？一般新闻情感是否也同向影响因变量？"NFTS 控制变量直接回应此质疑。
  3. **实施成本极低**: 数据已在 `12_fintech_news_full.parquet` 中，仅需在 `42_panel_attention_media.py` 或 `45_panel_export_main.py` 中增加一个聚合分支。

### 改进 B：遗漏变量稳健性压力测试 (Oster-style Coefficient Stability)

- **具体修改建议**: 在 `51_falsification_test.py` 中新增一个子模块，选取面板中绝对系数最大的控制变量作为基准（参照论文选用 Fix），按 1x、2x、3x 基准强度假设遗漏变量存在，绘制系数估计值和 t 统计量的稳定性图。
- **论文依据**: Fig. 2a/2b — 即使假设存在 3 倍于 Fix 强度的遗漏变量，ESG 系数仍为负且显著。
- **预期边际贡献**:
  1. **图形化展示识别策略可信度**: 比仅报告 R² 变化更直观地说明核心结论不受遗漏变量威胁。
  2. **符合 Oster (2019) 方法论标准**: 近年来顶刊（QJE/AER/JFE）日益要求此类稳健性检验。
  3. **实施成本低**: 纯统计计算，不涉及新数据采集或 NLP 模型调用。

---

## 3. 冗余剥离

经全面审查，**当前项目不存在需要剔除的伪需求模块**。论文为我们提供的反面启示是：

- **SnowNLP 单模型路线不应引入**: 论文使用的 SnowNLP 算法（Table 4, Column 3 用 FinBERT 做稳健性）属于词级情感聚合，远不及项目已有的 LLM 思维链句级/篇章级语义理解。引入 SnowNLP 看似"多一重验证"，实际降低方法论水准。**严禁引入**。
- **LDA 主题模型不应替代 LLM 分类**: 论文用 LDA 做 E/S/G 分类是因 2007-2022 数据时代缺乏 LLM 能力。项目当前的 LLM 验证 + 关键词词典双重分类体系已证明有效（Entity Masking ≥90% 一致, Prompt Sensitivity ≥85%），引入 LDA 是退步。**严禁引入**。

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 序号 | 改进项 | 类型 | 实施成本 | 预期收益 | 优先级 |
|------|-------|------|---------|---------|-------|
| A | 非金融科技新闻情感控制变量 (NFTS) | 速赢项 | 🟢 低（纯聚合逻辑，数据已有） | 🔴 高（直接回应审稿人遗漏变量质疑） | **P0** |
| B | Oster-style 遗漏变量压力测试 | 速赢项 | 🟢 低（纯统计计算） | 🟡 中（图形化增强论文可信度） | **P1** |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：非金融科技新闻情感控制变量 (NFTS) — 数据构建

**目标**: 在 Bank-Year 面板中新增 `nfts_tone_full`、`nfts_tone_ctx` 等控制变量。

**核心动作指令**:

1. **数据源**: 读取 `12_fintech_news_full.parquet`（阶段 12 全量输出，含 `is_fintech` 标志列）。
2. **过滤逻辑**: 提取 `is_fintech == False`（或等价的非金融科技银行新闻子集）。
3. **情感继承**: 这些非金融科技新闻在阶段 21 中未经过 LLM 情感标注（因被 `12_fintech_news.parquet` 过滤排除）。因此需采用以下策略之一：
   - **方案 α（推荐）**: 仅使用词典法（阶段 22 的五本词典）对非金融科技新闻计算情感分数，生成 `nfts_{dict_name}_score_{full/ctx}` 列。这避免了额外的 LLM API 成本。
   - **方案 β（备选）**: 若需更高精度，对非金融科技新闻样本也执行 LLM 情感分析（需评估 API 成本）。
4. **聚合**: 按 `(target_bank, year)` 聚合为年度均值，生成：
   - `nfts_tone_full` / `nfts_tone_ctx` — 非金融科技新闻情感均值
   - `nfts_n_articles` — 非金融科技新闻篇数（用于加权或诊断）
   - `nfts_coverage` — `ln(1 + nfts_n_articles)`
5. **合并**: 左连接至已有 Bank-Year 面板，零新闻填充 `nfts_n_articles=0`，情感列保持 NaN。

**交付物标准**:
- `45_panel_export_main.py` 新增 NFTS 构建函数。
- Stata .dta 文件中包含 `nfts_tone_full`、`nfts_tone_ctx`、`nfts_n_articles`、`nfts_coverage` 四列及对应 variable labels。
- 面板诊断日志输出 NFTS 变量的描述性统计（mean, std, 非零覆盖率）。

**修改涉及文件**:
- `45_panel_export_main.py` — 在步骤 6b (compute_fintech_attention_index) 之后新增 NFTS 构建步骤
- `41_panel_encode_aggregate.py` — 若采用方案 α，需在 `build_aggregation_dict()` 中新增 NFTS 聚合项

---

### 阶段二：Oster-style 遗漏变量压力测试

**目标**: 在伪造检验模块中新增遗漏变量系数稳定性可视化。

**核心动作指令**:

1. **基准变量选择**: 从面板控制变量中选取绝对系数最大者（如 `media_breadth` 或 `ln_news_coverage`）作为 benchmark。
2. **压力测试逻辑**:
   - 运行四次回归: 无遗漏变量、1x/2x/3x benchmark 强度
   - 每次回归记录核心解释变量（如 `llm_vote_tone_full`）的系数估计值和 t 统计量
   - 此处"强度"的实现方式：参照 Oster (2019, QJE) 或 Altonji et al. (2005)，计算 δ（selection on unobservables relative to observables 的比率），取 δ=1, 2, 3
3. **输出**: 生成两张诊断图（系数路径图 + t 统计量路径图），保存至 `data_processed/eval_reports/`。
4. **替代简化方案**: 若 Oster (2019) 方法实现复杂度过高，可直接采用论文的简化版本：
   - 逐步加入控制变量组（仅核心 → +财务 → +治理 → +媒体），记录核心系数变化
   - 若系数方向和显著性始终稳定，即报告"系数对可观测控制变量集的扩展不敏感"

**交付物标准**:
- `51_falsification_test.py` 新增 `run_oster_style_test()` 函数
- 输出 CSV 表格：`51_oster_stability.csv`（列: δ_level, coeff, se, t_stat, p_value）
- 输出诊断图：`51_oster_coefficient_path.png`、`51_oster_tstat_path.png`

**修改涉及文件**:
- `51_falsification_test.py` — 新增压力测试子模块

---

### 阶段三：结论重构

**目标**: 确保面板数据导出和项目文档反映新增变量。

**核心动作指令**:

1. **Stata 变量标签更新**: 在 `45_panel_export_main.py` 的 `STATA_LABELS` 字典中添加：
   ```python
   'nfts_tone_full':   'Non-Fintech News Tone (Full)',
   'nfts_tone_ctx':    'Non-Fintech News Tone (Ctx)',
   'nfts_n_articles':  'Non-Fintech News Count',
   'nfts_coverage':    'Non-Fintech News Coverage ln(1+N)',
   ```
2. **诊断日志更新**: 在 `log_diagnostics()` 中新增 NFTS 变量的描述性统计输出。
3. **项目文档更新**: 在 `docs/Project_Technical_Manual.md` 中补充 NFTS 控制变量的构建方法论说明和学术依据。

---

## 3. 风险预案 (Plan B)

### 风险 1：非金融科技新闻缺乏情感标注

- **致命卡点**: 非金融科技银行新闻在当前流水线中未经过 LLM 情感分析（被阶段 12 过滤后未进入阶段 21）。
- **Plan B**: 
  - **优先**: 使用五本词典法（阶段 22 的 jiang_2021 等）直接对非金融科技新闻文本计算正负词频比率。词典法不依赖 API，批量处理速度快。论文本身也使用了词典级工具（SnowNLP），因此作为控制变量的精度要求不需达到 LLM 级别。
  - **备选**: 从 `12_fintech_news_full.parquet` 中抽取非金融科技新闻子集，仅对其运行轻量 BERT 模型（如 `finbert_cn`）的批量推理，避免 LLM API 成本。

### 风险 2：非金融科技新闻样本量过少

- **致命卡点**: 若某些银行的非金融科技新闻在某些年份几乎为零，NFTS 变量大面积缺失。
- **Plan B**: 
  - 参照论文的 NESG 构建方式（年度均值），若 Bank-Year 非金融科技新闻不足 3 篇，该观测点 NFTS 设为 NaN（不填充伪值）。
  - 在回归中，NFTS 的缺失率作为诊断指标报告，若缺失率 >50%，改用「银行所在省份的非金融科技新闻情感均值」作为替代（省级聚合提高覆盖率）。

### 风险 3：Oster-style 测试实现复杂度

- **致命卡点**: Oster (2019) 原版方法需要估计 R²_max 和 δ，涉及较复杂的数学推导。
- **Plan B**: 直接采用论文 Fig. 2 的简化方案 — 选取系数最大的控制变量作为 benchmark，假设遗漏变量的偏倚方向和量级与 benchmark 成比例关系，逐级放大（1x, 2x, 3x），观察核心系数是否保持同号显著。这一方案的实现仅需对 OLS 残差做简单代数操作，无需调用专业计量包。

---

## 4. 维持原状确认清单

以下模块经与论文对比后确认**无需修改**，明确输出"维持原状"：

| 模块 | 维持原状理由 |
|------|------------|
| LLM 三模型集成 + 多数投票 (21_tone_llms.py) | 远超论文 SnowNLP 单模型方案，无下行风险 |
| 五本中文金融词典 (22_tone_words.py) | 论文未提供更优词典方案 |
| 五个 BERT 模型 (23_tone_berts.py) | 论文仅以 FinBERT 做单次稳健性，项目已实现五模型覆盖 |
| 29 套 Bartik IV (44_panel_iv_did.py) | 远超论文 2 个省级报纸 IV |
| Leave-one-out 地理 IV (43_panel_indicators_geography.py) | 论文无对应设计 |
| DID 政策冲击 (44_panel_iv_did.py) | 论文无对应设计 |
| 双轨分析 (Full/Ctx) | 论文无对应设计，项目独创 |
| Entity Masking + Prompt Sensitivity (36/39) | 论文无对应验证体系 |
| 金融科技分类 (底层技术/应用场景) | 与论文 E/S/G 分类同属子主题分解范式，已逻辑自洽 |
| 媒体权威性加权 (Holzman et al. 2023) | 远超论文 70/30 简单加权 |
| MinHash LSH 近似去重 (00_preprocessing.py) | 论文未涉及去重方法论 |

---

> **执行纪律**: 本文档生成后即停止。严禁未经用户同意修改任何代码和配置文件。
