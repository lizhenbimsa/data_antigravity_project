# 基于参考论文 "Adding Fuel to the Fire: Media Coverage of ESG and Earnings News" 的项目分析与执行计划

> **参考论文**: Bhojraj, S., Guest, N., Wang, E., & Yu, E. (2025). "Adding Fuel to the Fire: Media Coverage of ESG and Earnings News." Cornell University / Baruch College, June 2025.
>
> **当前项目**: `news_process` — 中国商业银行金融科技新闻情感分析流水线

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Bhojraj et al. (2025) 揭示了一个**三层级联传导机制**：

| 层级 | 机制 | 论文核心发现 |
|------|------|-------------|
| **L1: 注意力传导** | 社会层面 ESG 关注度 → 企业层面 ESG 新闻报道量 | ESG_AttentionIndex ↑ → ESG_Coverage% ↑ (β=1.316, t=5.14) |
| **L2: 挤出效应** | ESG 报道量 ↑ → 盈余新闻报道量 ↓；ESG 情感渗透至盈余新闻情感 | ESG_Coverage% ↑1σ → Earnings_Coverage% ↓2.2% (均值下降 3.6%) |
| **L3: 市场后果** | ESG 报道挤出盈余报道 → ERC 下降 + 异常交易量上升 | ESG_Coverage% ↑1σ → ERC ↓8.67%; ESG 所有权高的公司交易量效应更强 |

### 1.2 与当前项目的关键范式落差

**落差 A：缺少"覆盖率结构"变量体系 (Coverage Composition)**

- **论文范式**: 将媒体报道拆分为 ESG_Coverage% 与 Earnings_Coverage%，核心研究变量是**报道类别占比** (proportion of coverage by topic)，而非简单的新闻总量或情感均值。
- **项目现状**: 项目构建了 `n_articles`、`ln_news_coverage`、`media_breadth` 等**总量指标**，以及 `tech_frac / app_frac` (底层技术 vs 应用场景占比)，但**缺少与银行其他类型新闻 (如监管、信贷、人事等) 的覆盖率对比结构**。
- **实质落差**: 项目仅看"金融科技新闻有多少"，无法回答"金融科技新闻占比提升是否挤出了该银行的其他关键报道 (如经营绩效类新闻)"这一核心问题。ESG_Coverage% 的概念在项目中没有直接对应物。

**落差 B：缺少"注意力指数→覆盖率"的外生传导链条**

- **论文范式**: 构建**社会层面** (society-wide) ESG_AttentionIndex (季度-全市场所有 ESG 新闻占比) 作为**外生冲击**变量，用以识别企业层面 ESG 覆盖率变化的外生来源。这是该论文因果识别的关键设计——社会层面 ESG 情绪波动对特定公司而言是外生的。
- **项目现状**: 已有 `ft_attn_yr / ft_attn_prov / ft_attn_city` (三级地理注意力指数)，但**仅作为面板控制/调节变量使用**，未被嵌入"社会关注度 → 企业覆盖率 → 情感溢出"的因果链条中。
- **实质落差**: 注意力指数已具备基础设施，但缺少：(i) 将注意力指数作为企业层面覆盖率变化的**核心解释变量**的回归框架；(ii) 相应的覆盖率结构因变量。

**落差 C：缺少"情感溢出/渗透"(Sentiment Spillover) 检验**

- **论文范式**: 检验 ESG 新闻情感 → 盈余新闻情感的**溢出关系** (Table 5)，以及 ESG 情感与盈余方向冲突时的**衰减效应** (Table 6)。关键发现：即使盈余惊喜 (SUE) 为正，低 ESG 情感也会压低盈余新闻的正面报道。
- **项目现状**: 情感分析已实现三角验证 (LLM×3 + 词典×5 + BERT×5)，但**不同类别新闻之间的情感交叉影响**从未被量化。
- **实质落差**: 缺乏检验"金融科技新闻情感是否渗透至同银行同期非金融科技新闻情感"的分析框架。

### 1.3 项目已有的优势模块（维持原状）

以下模块已逻辑自洽或优于论文，**维持原状**：

| 模块 | 评价 | 理由 |
|------|------|------|
| **LLM 三角验证 (21)** | ✅ 维持原状 | 论文使用 RavenPack 内置情感评分 (DOCUMENT_SENTIMENT)，为单一闭源来源。项目的三模型投票 + 多方法三角验证远优于此。 |
| **媒体异质性四维度 (42)** | ✅ 维持原状 | 论文未涉及媒体来源异质性。项目的财经/综合/中央/地方四维度分拆在方法论上更先进。 |
| **Bartik IV 29套 (44)** | ✅ 维持原状 | 论文因果识别依赖于 F.E.+clustering，无工具变量。项目的 Bartik shift-share 框架在识别策略上具有显著优势。 |
| **Entity Masking 稳健性 (36)** | ✅ 维持原状 | 论文无此类检验。项目独有的稳健性设计。 |
| **Prompt 敏感度检验 (39)** | ✅ 维持原状 | 论文未使用 LLM，无此问题。项目基于 Carlson & Burbano (2026, SMJ) 的系统性 Prompt 测试为创新贡献。 |

## 2. 实质性改进项

### 改进 A：构建"覆盖率结构"变量体系 — 金融科技覆盖占比及挤出检验

- **具体修改**: 在面板数据中新增 `fintech_coverage_pct` (= 金融科技新闻数 / 该银行同年总新闻数) 和 `non_fintech_coverage_pct` (= 1 - fintech_coverage_pct)。构建回归检验 `fintech_coverage_pct` 与 `non_fintech_n_articles` 的负相关关系。
- **论文依据**: Eq.(2a) — ESG_Coverage% 对 Earnings_Coverage% 的挤出系数 β₁ 显著为负 (Table 4)。
- **边际贡献**: 将项目的研究问题从"金融科技新闻的情感如何影响银行绩效"拓展为"金融科技报道对银行信息环境的结构性重塑"。这直接对标 Bonsall et al. (2020, JAE) 的资源约束假说——媒体资源有限，金融科技报道增加可能挤出银行经营绩效相关报道，降低投资者信息集质量。

### 改进 B：将注意力指数嵌入"社会关注→企业覆盖"的因果传导框架

- **具体修改**: 在 Stata/Python 实证分析阶段，新增回归模型：`fintech_coverage_pct_i,t = β₁ * ft_attn_yr_t + β' * Controls + γ_i + ε_i,t`。本质上是复现 Bhojraj et al. Eq.(1a) 的中国金融科技版本。
- **论文依据**: Eq.(1a) — ESG_AttentionIndex 对 ESG_Coverage% 的系数 β₁ = 1.316*** (t=5.14, Table 3 Panel A)。
- **边际贡献**: 当前项目的 `ft_attn_yr` 仅作为面板变量存在，缺乏统计检验其"驱动企业覆盖率"的因果链条。嵌入此框架后，可论证"社会层面金融科技关注度的外生冲击通过媒体资源再配置传导至银行层面报道结构"——这为下游情感分析提供了外生性来源。

### 改进 C：构建"情感溢出/渗透"检验框架

- **具体修改**: 在篇章级数据中区分金融科技新闻与非金融科技新闻的情感，构建回归：`non_fintech_sentiment_i,t = β₁ * fintech_sentiment_i,t + Controls + F.E.`。进一步检验当 `fintech_sentiment` 方向与银行实际经营状况 (如 ROA 变化方向) 冲突时，`non_fintech_sentiment` 是否被拉向 `fintech_sentiment` 的方向。
- **论文依据**: Eq.(2b) + Table 5 — ESG_Sentiment 对 Earnings_Sentiment 的正向溢出；Table 6 — SUE×LowESGSentiment 交互项显著为负。
- **边际贡献**: 揭示金融科技正面报道是否"污染"同期负面经营新闻的情感判定（或反之），直接挑战媒体作为"客观信息中介"的假设。对中国银行业监管环境下的媒体角色具有独特政策含义。

## 3. 冗余剥离

经全面审计，当前项目**不存在需剔除的冗余模块**。

- 词典法情感 (22) 虽非项目主力方法，但作为三角验证的基准维度，其存在具有方法论合理性。论文本身仅使用单一情感来源 (RavenPack)，项目的多方法架构是优势而非冗余。
- 所有 Bartik IV 维度均服务于识别策略，无"伪需求"维度。

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 序号 | 改进项 | 类型 | 实施成本 | 预期收益 | 优先级 |
|------|--------|------|---------|---------|--------|
| A | 覆盖率结构变量 | 🟢 速赢 | 低 (仅需利用已有数据 `12_fintech_news_full.parquet` 计算占比) | 高 (直接新增核心解释变量) | **P0** |
| B | 注意力→覆盖率因果链 | 🟢 速赢 | 低 (已有 `ft_attn_yr`，仅需新增 Stata 回归规范) | 高 (补全因果识别关键环节) | **P0** |
| C | 情感溢出检验 | 🟡 核心攻坚 | 中 (需区分同期金融科技/非金融科技新闻情感并构建新的回归框架) | 高 (揭示信息溢出的新机制) | **P1** |

## 2. 阶段化执行指令 (SOP)

---

### 阶段一：覆盖率结构变量构建（估时：0.5天）

**目标**: 在面板构建流程中新增"金融科技覆盖率占比"变量族

#### 指令 1.1：在 `41_panel_encode_aggregate.py` 或 `45_panel_export_main.py` 中新增覆盖率计算

```
操作节点: 45_panel_export_main.py → main() → 步骤 5 聚合之后、步骤 6 平衡之前
```

**数据源**: `12_fintech_news_full.parquet` (已存在，包含 `is_fintech_news` 标记和 `target_bank`)

**计算逻辑**:
```python
# 从 12_fintech_news_full.parquet 计算每 Bank-Year 的:
#   total_bank_articles:     该银行同年所有新闻 (含 fintech + non-fintech)
#   fintech_articles:        该银行同年金融科技新闻
#   non_fintech_articles:    total - fintech
#   fintech_coverage_pct:    fintech / total
#   non_fintech_coverage_pct: 1 - fintech_coverage_pct
```

**交付物标准**:
- 面板新增列: `total_bank_articles`, `fintech_coverage_pct`, `non_fintech_articles`, `non_fintech_coverage_pct`
- 覆盖率 ∈ [0, 1]，无 NaN (零新闻行 coverage_pct 设为 NaN)
- Stata 变量标签: `Fintech Coverage Share (Da et al. 2011 analog)`

#### 指令 1.2：构建非金融科技新闻情感

**数据源**: `12_fintech_news_full.parquet` 中 `is_fintech_news == False` 的子集

**计算逻辑**:
```python
# 对 is_fintech_news == False 的文章:
#   如已有 LLM 情感标注 → 直接使用
#   如未标注 (因 pipeline 仅对 fintech=True 做 LLM) → 需记录为缺失
# 聚合至 Bank-Year: non_fintech_tone = mean(sentiment of non-fintech articles)
```

> [!IMPORTANT]
> 当前流水线仅对 `is_fintech_news == True` 的文章执行 LLM 情感分析 (步骤 21)。
> 因此，非金融科技新闻**没有 LLM 情感标注**。
> 
> **处理方案**:
> - 短期：使用词典法 (步骤 22 已对所有银行新闻运行) 的得分作为非金融科技新闻情感代理
> - 中期：考虑对高频非金融科技新闻子样本补做 LLM 标注 (成本需评估)

**交付物标准**:
- 面板新增列: `non_fintech_tone_dict_full` (词典法均值)
- 篇章级 tag: 在 `12_fintech_news_full.parquet` 中确保 `is_fintech_news` 列的完整性

---

### 阶段二：实证模型构建与检验（估时：1天）

**目标**: 构建 Bhojraj et al. 三层因果链的中国金融科技版本

#### 指令 2.1：L1 因果链 — 社会关注度 → 企业覆盖率

**Stata 回归规范**:
```stata
* Eq.(1a) 复现: 注意力指数 → 金融科技覆盖率
reghdfe fintech_coverage_pct ft_attn_yr ///
    LMktCap Leverage ROA ln_news_coverage ///
    , absorb(target_bank) vce(cluster target_bank year)

* 分别检验省级和城市级注意力指数
reghdfe fintech_coverage_pct ft_attn_prov ft_attn_city ///
    LMktCap Leverage ROA ln_news_coverage ///
    , absorb(target_bank) vce(cluster target_bank)
```

**预期结果**: `ft_attn_yr` 系数显著为正 → 社会层面金融科技关注度越高，银行层面金融科技新闻覆盖率越高。

#### 指令 2.2：L2 因果链 — 覆盖率挤出效应

**Stata 回归规范**:
```stata
* Eq.(2a) 复现: 金融科技覆盖率 → 非金融科技覆盖率挤出
reghdfe non_fintech_coverage_pct fintech_coverage_pct ///
    LMktCap Leverage ROA ///
    , absorb(target_bank) vce(cluster target_bank year)
```

**预期结果**: `fintech_coverage_pct` 系数显著为负 → 挤出效应存在。

#### 指令 2.3：L2 因果链 — 情感溢出

**Stata 回归规范**:
```stata
* Eq.(2b) 复现: 金融科技情感 → 非金融科技情感
* (使用词典法情感作为非金融科技新闻情感代理)
reghdfe non_fintech_tone_dict_full llm_vote_tone_full ///
    fintech_coverage_pct ///
    LMktCap Leverage ROA ///
    , absorb(target_bank) vce(cluster target_bank year)
```

**预期结果**: `llm_vote_tone_full` 系数显著为正 → 金融科技新闻情感溢出至非金融科技新闻。

#### 指令 2.4：稳健性检验矩阵

| 检验 | 对标论文 | 操作 |
|------|---------|------|
| E/S/G 拆分 | Table 4 Panel B | 将 `fintech_coverage_pct` 替换为 `tech_frac` / `app_frac` 分别检验 |
| 时间固定效应 | Column (4) vs (3) | 替换 `absorb(target_bank)` 为 `absorb(target_bank year)` |
| 控制变量渐进 | Columns (1)-(4) | 从无控制到全控制逐步加入 |
| 聚合频率稳健性 | 已有半年度/季度 Bartik | 利用 `bartik_half / bartik_qtr` 维度验证 |

**交付物标准**:
- Stata .do 文件: `do_bhojraj_replication.do`
- 回归结果表格: `table_L1_attention_coverage.tex`, `table_L2_crowdout.tex`, `table_L2_spillover.tex`

---

### 阶段三：结论重构（估时：0.5天）

**目标**: 将新发现整合入论文叙事

#### 指令 3.1：核心叙事升级

**原叙事**: "金融科技新闻报道的情感影响银行绩效"

**升级叙事**: "社会层面金融科技关注度通过媒体资源再配置，驱动银行层面金融科技报道覆盖率上升，挤出其他关键经营信息报道，并通过情感渗透效应扭曲非金融科技新闻的客观性——这一级联传导机制系统性地削弱了媒体作为银行信息中介的功能"

#### 指令 3.2：与 Bhojraj et al. 的差异化贡献声明

| 维度 | Bhojraj et al. (2025) | 当前项目 (升级后) |
|------|----------------------|------------------|
| 场景 | 美国上市公司 × ESG vs 盈余 | 中国商业银行 × 金融科技 vs 经营绩效 |
| 情感度量 | RavenPack (单一闭源) | LLM×3 + 词典×5 + BERT×5 (三角验证) |
| 因果识别 | F.E. + Clustering | Bartik IV 29套 + Leave-one-out IV + DID |
| 媒体异质性 | 未涉及 | 四维度 (财经/综合/中央/地方) |
| 制度背景 | 自由媒体市场 | 中国媒体管制环境 (独特的政策含义) |

## 3. 风险预案 (Plan B)

### 风险 1：非金融科技新闻缺乏 LLM 情感标注

- **卡点**: pipeline 仅对 `is_fintech_news == True` 的文章执行 LLM 情感分析 (步骤 21)。非金融科技新闻没有高质量情感得分。
- **Plan B-1 (推荐)**: 使用词典法情感 (`22_tone_words.py` 已对全量银行新闻运行) 作为非金融科技新闻情感的代理变量。词典法虽不如 LLM，但作为跨类别比较的基准已足够。
- **Plan B-2**: 对非金融科技新闻的随机子样本 (e.g., N=5000) 补做 LLM 标注，用于校准词典法偏差。成本约 $15-30 (GPT-5-nano 价位)。

### 风险 2：`12_fintech_news_full.parquet` 中 `is_fintech_news == False` 的文章没有阶段 22 词典法得分

- **卡点**: 需确认词典法情感分析的输入是全量银行新闻 (`11_bank_news.parquet`) 还是仅限金融科技子集。
- **检查方法**: `22_tone_words.py` 的输入文件 → 如果读取的是 `21_tone_llms.parquet` (仅含 fintech)，则非 fintech 文章确实没有词典得分。
- **Plan B**: 在 `22_tone_words.py` 中增加一个模式，允许直接对 `11_bank_news.parquet` 全量运行词典法，输出 `22_words_tone_all_bank_news.parquet`。词典法为纯字典匹配，无 API 成本，全量运行仅增加几分钟计算时间。

### 风险 3：挤出效应在中国语境中不显著

- **卡点**: 中国媒体可能对银行各类新闻的报道由不同编辑团队负责，资源约束假说可能不成立。
- **Plan B**: 即使挤出效应不显著，"非存在"本身也是有价值的发现——可论证中国媒体市场与美国的结构性差异。同时，情感溢出效应可以独立成立 (Table 5 对应的检验不依赖于挤出效应)。

---

> [!CAUTION]
> **执行红线**: 本文档为分析与计划文档。在获得明确批准前，**严禁修改任何代码、配置文件或数据文件**。所有代码修改必须在批准后按照 SOP 顺序执行。
