# Using GPT to Measure Business Complexity — 项目分析与执行计划

> **参考论文**: Bernard, D., Blankespoor, E., de Kok, T., & Toynbee, S. "Using GPT to Measure Business Complexity." *The Accounting Review* (forthcoming).
>
> **当前项目**: `F:\WiseSearch\data_antigravity_project\news_process` — 银行金融科技新闻情感分析与 Bank-Year 面板构建流水线

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Bernard et al. 的核心创新在于一个**三层嵌套的复杂度测量框架**：

| 层级 | 机制 | 关键公式/逻辑 |
|------|------|---------------|
| **Fact-level** | 对 iXBRL 标签的每一个数值事实，微调 LLM（Llama 3 8B）预测其 XBRL 标签分类，取 `Complexity_fact = 1 - Confidence` | 置信度越低 → 概念越难理解 → 复杂度越高 |
| **Filing-level** | 将报告内所有事实级复杂度取均值 → `Complexity_filing = mean(Complexity_fact)` | 捕获整体业务复杂度 |
| **Category-level** | 按脚注类别（29类交易类别）分组聚合 → 逐类别复杂度 | 允许分解复杂度来源（如债务 vs 收入确认） |

**核心验证**：复杂度越高 → IPE（价格发现效率）越低（Table 4, β = -0.040***），且增量显著超越 FOG、Filing Length、ARC 等传统代理变量。

### 1.2 当前项目与论文的关键落差

#### 落差 A：置信度的利用深度（中等落差）

- **论文做法**：将 LLM 置信度**反转**为复杂度度量（`1 - confidence`），作为核心因变量/自变量进入回归。
- **项目现状**：`21_tone_llms.py` 中已提取每个模型的 `verification_confidence` 和 `sentiment_confidence`（L288-289），并在 `41_panel_encode_aggregate.py` 中聚合为 `avg_llm_conf` 列（L125-131）。但项目仅将置信度用于**加权调节**（衰减偏误控制, Shapiro et al. 2022），**未**将其反转构建为独立的"信息复杂度"指标。
- **边际贡献**：引入 `info_complexity = 1 - avg_llm_conf` 作为银行金融科技新闻的"理解难度"代理变量，可直接检验"复杂度越高 → 市场反应越慢/投资者注意力分配越偏"的假说，为项目增添一个**全新的研究维度**。

#### 落差 B：缺乏 Fact-level 粒度（低落差 — 结构差异所致）

- **论文做法**：iXBRL 标签提供天然的 fact-level 粒度（每个数字一个置信度）。
- **项目现状**：项目的分析单元是**新闻文章**，不存在 iXBRL 式的数值标签结构。LLM 输出的是文章级判断（真伪 + 情感），而非逐句/逐段的概念分类。
- **诊断结论**：这是**数据结构差异**导致的合理差距，非设计缺陷。项目的"事实级"等价物应为**文章级**的置信度，已具备。

#### 落差 C：缺乏 Category-level 复杂度分解（中等落差）

- **论文做法**：按 29 个交易类别（债务、公允价值、租赁等）分解复杂度，发现不同类别的决定因素和后果截然不同（Table 5, Table 7 vs Table 3）。
- **项目现状**：项目已具备 `fintech_category`（底层技术/应用场景）二分类（L481-496 in `21_tone_llms.py`），并在面板中按类别聚合（`n_articles_tech`, `n_articles_app`）。但**未**按类别计算差异化的"复杂度"指标。
- **边际贡献**：论文的关键发现之一是"子类别复杂度的决定因素可能方向相反"（如 Size 对整体复杂度为正，对债务复杂度为负）。按底层技术/应用场景分别构建 `info_complexity_tech` / `info_complexity_app` 可检验：底层技术报道是否系统性地比应用场景报道更难理解？这一异质性是否影响市场信息效率？

### 1.3 论文机制与项目的可迁移性矩阵

| 论文机制 | 可迁移性 | 迁移方式 | 论文依据 |
|----------|----------|----------|----------|
| GPT 置信度 → 复杂度 | ✅ 高 | `1 - avg_llm_conf` → 面板变量 | §III, Eq(1) |
| Complexity ↔ IPE 验证 | ⚠️ 中 | 需股票市场数据（CRSP/CSMAR） | §IV, Table 4 |
| Category-level 分解 | ✅ 高 | 按 `fintech_category` 分组聚合置信度 | §V, Table 5 |
| 确定因素分析 (Table 3/7) | ✅ 高 | 对 `info_complexity` 做 OLS/FE 回归 | §IV, Table 3 |
| Fine-tuning 开源 LLM | ⚠️ 低 | 项目使用 API 调用而非微调，无需改变 | §III, Appendix B |
| 可读性鲁棒性测试 (Figure 1) | ⚠️ 中 | 简化 Prompt → 重测置信度 → 验证度量稳健性 | §III, Figure 1 |

---

## 2. 实质性改进项

### 改进 A：构建 LLM 置信度驱动的"信息复杂度"指标

- **具体修改**：在 `43_panel_indicators_geography.py` 的 `compute_composite_indicators()` 中新增：
  ```python
  # Bernard et al.: Complexity = 1 - Confidence
  for track in ['_full', '_ctx']:
      panel[f'info_complexity{track}'] = 1 - panel[f'avg_llm_conf{track}']
  ```
- **论文依据**：§III "Complexity Measure" — "for every prediction, we calculate complexity as 1 minus the confidence score"
- **预期边际贡献**：
  1. 提供一个**全新的 Bank-Year 级变量**，度量投资者/分析师理解该银行金融科技新闻的"认知处理成本"
  2. 可与现有 `llm_vote_tone` 联合检验：复杂度是否调节情感对银行绩效/股价的传导效率（交互项）
  3. 可与 `fintech_exposure` 联合检验：金融科技暴露越高的银行，其相关新闻是否系统性地更复杂

### 改进 B：按金融科技类别计算差异化复杂度

- **具体修改**：在面板聚合阶段，新增按 `fintech_category` 分组的置信度均值聚合：
  ```python
  for cat_label, suffix in [('底层技术', '_tech'), ('应用场景', '_app')]:
      df_cat = df[df['fintech_category'] == cat_label]
      cat_conf = df_cat.groupby(['target_bank', 'year'])[f'avg_llm_conf{track}'].mean()
      panel[f'info_complexity{suffix}{track}'] = 1 - cat_conf
  ```
- **论文依据**：§V "Category-Level Business Complexity" — "the sources of complexity may differ" + Table 7 showing Size has opposite signs for filing-level vs debt complexity
- **预期边际贡献**：检验底层技术（AI、区块链等）vs 应用场景（移动支付、智能风控等）的信息复杂度是否存在系统差异，以及差异化复杂度对银行行为的异质性影响

---

## 3. 冗余剥离

经审查，当前项目**无需剥离**任何模块。理由如下：

| 候选剥离模块 | 诊断结论 |
|-------------|----------|
| 词典法情感 (`22_tone_words.py`) | **维持原状** — 论文虽批评 FOG 等传统文本指标缺乏增量解释力（Table 4, FOG 不显著），但项目的词典法服务于三角验证（Cronbach's α），是审稿人标准要求 |
| BERT 情感 (`23_tone_berts.py`) | **维持原状** — 多方法验证是项目核心设计优势，论文未否定 BERT 路线 |
| Entity Masking (`36_entity_masking_test.py`) | **维持原状** — 论文 Figure 1 的可读性鲁棒性测试本身就是一种"改变输入、验证输出稳定性"的设计，与 Entity Masking 逻辑一致 |
| 29 套 Bartik IV (`44_panel_iv_did.py`) | **维持原状** — 论文未涉及因果识别策略，项目的 IV 体系是论文方法无法替代的独立贡献 |

> **结论**：项目当前设计在方法论覆盖面和稳健性检验深度上已逻辑自洽。改进应为**增量叠加**（新增复杂度指标），而非替换现有模块。

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 优先级 | 任务 | 实施成本 | 预期收益 | 类型 |
|--------|------|----------|----------|------|
| 🟢 P0 | 构建 `info_complexity` 面板变量 | 极低（~10行代码） | 中高 — 全新研究维度 | 速赢项 (Quick Win) |
| 🟢 P0 | 按类别构建差异化复杂度 | 低（复用已有聚合框架） | 中 — 异质性分析 | 速赢项 |
| 🟡 P1 | Stata 回归验证（复杂度 → 调节效应） | 中（需 Stata do-file） | 高 — 实证检验 | 核心攻坚项 |
| 🟡 P1 | 可读性鲁棒性测试（简化 Prompt → 重测） | 中（需重新调用 LLM API） | 中 — 度量稳健性 | 核心攻坚项 |
| 🔴 P2 | IPE 价格发现效率检验 | 高（需 CSMAR/Wind 日频数据） | 高 — 但数据依赖强 | 备选项 |

## 2. 阶段化执行指令 (SOP)

### 阶段一：信息复杂度指标构建（机制重塑）

> **目标**：将 LLM 置信度反转为"信息复杂度"度量，集成到 Bank-Year 面板。

#### 步骤 1.1：`43_panel_indicators_geography.py` — `compute_composite_indicators()` 增量修改

- **动作**：在函数末尾新增以下指标计算（插入位置：现有 `fintech_exposure` 计算之后）：

```python
# ── 信息复杂度 (Bernard, Blankespoor, de Kok & Toynbee, TAR) ──
# 核心原理: Complexity = 1 - Confidence
# LLM 对新闻判定的平均置信度越低 → 信息越复杂/模糊 → 处理成本越高
for track in ['_full', '_ctx']:
    conf_col = f'avg_llm_conf{track}'
    if conf_col in panel.columns:
        panel[f'info_complexity{track}'] = 1 - panel[conf_col].fillna(panel[conf_col].median())
        logger.info(f"  info_complexity{track}: mean={panel[f'info_complexity{track}'].mean():.4f}, "
                    f"std={panel[f'info_complexity{track}'].std():.4f}")
```

- **交付物标准**：
  - `info_complexity_full` 和 `info_complexity_ctx` 出现在 `40_panel_yearly.parquet` 和 `.dta` 文件中
  - 描述性统计与论文 Table 2 可比较（论文 mean=0.118, std=0.038）

#### 步骤 1.2：按金融科技类别构建差异化复杂度

- **动作**：在 `41_panel_encode_aggregate.py` 的 `aggregate_panel()` 函数中，分类聚合段新增置信度均值聚合：

```python
# 在分类聚合循环内追加:
for track in ['_full', '_ctx']:
    conf_src = f'avg_llm_conf{track}'
    if conf_src in df_cat.columns:
        cat_agg[f'avg_llm_conf{suffix}{track}'] = (conf_src, 'mean')
```

- 在 `43_panel_indicators_geography.py` 中新增分类复杂度计算：

```python
for suffix in ['_tech', '_app']:
    for track in ['_full', '_ctx']:
        conf_col = f'avg_llm_conf{suffix}{track}'
        if conf_col in panel.columns:
            panel[f'info_complexity{suffix}{track}'] = 1 - panel[conf_col]
```

- **交付物标准**：
  - `info_complexity_tech_full`, `info_complexity_app_full` 等列出现在面板中
  - 验证 `info_complexity_tech > info_complexity_app`（预期：底层技术更复杂）

#### 步骤 1.3：Stata 变量标签更新

- **动作**：在 `45_panel_export_main.py` 的 `STATA_LABELS` 字典中新增：

```python
# 信息复杂度 (Bernard et al., TAR)
'info_complexity_full':        'Info Complexity (1-Conf, Full)',
'info_complexity_ctx':         'Info Complexity (1-Conf, Ctx)',
'info_complexity_tech_full':   'Info Complexity: Technology (Full)',
'info_complexity_tech_ctx':    'Info Complexity: Technology (Ctx)',
'info_complexity_app_full':    'Info Complexity: Application (Full)',
'info_complexity_app_ctx':     'Info Complexity: Application (Ctx)',
```

---

### 阶段二：实证验证（模型重构与检验）

> **目标**：在 Stata 中检验信息复杂度的经济后果和调节效应。

#### 步骤 2.1：复杂度的决定因素分析（复刻 Table 3）

```stata
* Bernard et al. Table 3 复刻（中国银行语境）
* DV: info_complexity_full
* IV: 银行规模、盈利能力、上市状态、金融科技暴露度等
reghdfe info_complexity_full ln_assets roa leverage fintech_exposure_full ///
    ln_news_coverage media_breadth, ///
    absorb(target_bank year) vce(cluster target_bank)
```

- **交付物标准**：回归表应报告 β、SE、t-stat、R²，与论文 Table 3 格式对标

#### 步骤 2.2：复杂度对情感传导的调节效应

```stata
* 核心检验: 复杂度是否削弱情感的信息效率
* 交互项: tone × complexity
reghdfe y_performance llm_vote_tone_full info_complexity_full ///
    c.llm_vote_tone_full#c.info_complexity_full controls, ///
    absorb(target_bank year) vce(cluster target_bank)
* 预期: 交互项系数 < 0（复杂度削弱情感传导）
```

#### 步骤 2.3：稳健性检验清单

| 检验 | 方法 | 论文对标 |
|------|------|----------|
| 替代度量 | 使用 `avg_llm_conf_std` 代替均值 | — |
| 双轨对比 | Full vs Ctx 轨道的复杂度比较 | 项目特有 |
| 子样本 | 按 `fintech_category` 分样本回归 | Table 7 |
| 控制变量 | 加入 FOG-like 可读性指标（如 `avg_sent_len`） | Table 4 col(2) |

---

### 阶段三：结论重构

#### 步骤 3.1：结论叙事整合

- 若 `info_complexity` 显著调节情感传导效率 → 叙事线："金融科技新闻的信息复杂度不仅反映了底层技术的认知门槛，更是投资者处理成本的代理变量，高复杂度新闻的情感信号被市场定价的速度更慢"
- 若分类复杂度存在显著异质性 → 子结论："底层技术类报道的信息复杂度系统性高于应用场景类，这一结构性差异建议监管机构在金融科技信息披露中采用分层简化策略"

#### 步骤 3.2：论文写作中的引用锚定

- 方法论部分引用 Bernard et al. (TAR) 的 complexity-as-confidence 范式
- 实证设计部分引用 Blankespoor et al. (2020) 的 IPE 框架（若数据可得）
- 讨论部分引用论文关于 "business complexity vs reporting complexity" 的概念辨析

---

## 3. 风险预案 (Plan B)

| 致命卡点 | 概率 | 替代方案 |
|----------|------|----------|
| `avg_llm_conf` 列方差过小（所有新闻置信度趋近 1.0） | 中 | 改用 `avg_llm_conf_std` 或逐模型最低置信度 `min(model_conf)` 作为替代 |
| 分类复杂度无显著差异（tech ≈ app） | 中 | 放弃类别分解，仅报告整体复杂度结果 |
| IPE 检验所需的高频市场数据不可得 | 高 | 放弃价格发现效率检验，聚焦于复杂度的决定因素和调节效应分析 |
| 审稿人质疑"LLM 置信度 ≠ 信息复杂度" | 中 | (1) 引用论文 §III 的构建验证逻辑；(2) 报告简化 Prompt 鲁棒性测试；(3) 阐述"认知处理成本"的理论基础 |

---

> **执行约束**：本文档为分析与规划阶段产出，**严禁在未获用户明确批准前修改任何代码或配置文件**。所有代码示例仅为方案说明，非实际执行指令。
