# 地方媒体污染情绪与企业绿色创新 — 项目审计与执行计划

> **参考论文**: He, Y., Lu, S., Wei, R. & Wang, S. (2024). "Local media sentiment towards pollution and its effect on corporate green innovation." *Journal of Corporate Finance*, 84, 102547.
>
> **审计对象**: `F:\WiseSearch\data_antigravity_project\news_process` 全流水线
>
> **核心结论**: 省级官方党报对环境污染的**负面情绪**通过**治理渠道**（而非信息渠道）促进企业绿色创新；市场化媒体负面情绪则通过信息渠道**抑制**绿色创新。

---

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断

#### 1.1 论文核心机制提炼

```
┌──────────────────────────────┐
│  省级官方党报污染报道         │
│  (Province × Year 粒度)      │
│                              │
│  MSENT = (Neg - Pos)         │
│         /(Neg + Pos)         │
└──────────┬───────────────────┘
           │
    ┌──────▼──────┐      ┌────────────────────┐
    │ 治理渠道    │      │ 信息渠道           │
    │ (Governance)│      │ (Information)      │
    │             │      │                    │
    │ 声誉压力    │      │ 融资约束↑          │
    │ + 行政干预  │      │ → 创新投入↓        │
    │ → 绿色创新↑ │      │ → 绿色创新↓        │
    └──────┬──────┘      └────────┬───────────┘
           │                      │
     ✅ 实证支持              ✗ 被推翻
     (官方党报)              (市场化媒体支持此渠道)
```

论文的五步文本处理流程：
1. **字典法粗筛** → 从 ~140万条党报新闻中筛出 ~40万条含污染关键词的新闻
2. **LDA 主题模型精筛** → 设30个主题，选定 topic 29 为企业环境污染主题，得 ~2万条
3. **字典法情感计算** → MSENT = (负面词 − 正面词) / (负面词 + 正面词)
4. **Province × Year 聚合** → 同省同年全部党报污染新闻的平均 MSENT
5. **与 Firm-Year 面板匹配** → 按企业注册地省份匹配

#### 1.2 当前项目与论文的范式对标

| 维度 | 论文方法 | 项目现状 | 差距评估 |
|------|---------|---------|---------|
| **媒体来源** | 省级官方党报（单一、纯净） | 全量媒体（报纸/网络/APP混合），通过 `media_types_to_exclude` 排除 APP/微博/政府/网页 | 🔴 **关键盲区**：未区分"党报"与"市场化报纸"；论文的核心发现恰恰依赖于二者的**方向性差异**（党报正效应 vs 市场化媒体负效应） |
| **主题筛选** | 字典法 + LDA 二级筛选（污染主题） | Aho-Corasick 银行关键词过滤（金融主题） | ⚪ 维持原状 — 项目研究对象不同（银行 vs 污染企业），主题筛选逻辑自洽 |
| **情感计算** | 纯字典法（正负词频比） | **三轨并行**：LLM 多模型集成 + 词典法 + BERT（远超论文） | ✅ **项目优于论文** — 项目的 LLM 多模型投票 + 置信度加权方案在方法论上严格优于论文的单一字典法 |
| **聚合粒度** | Province × Year → Firm-Year | Bank × Year（直接按企业维度聚合） | ⚪ 维持原状 — 项目的 Bank-Year 粒度比论文的 Province-Year 更精细，信息损失更少 |
| **IV 策略** | 省级海拔标准差（地理外生性） | Bartik Shift-Share IV + 经济圈 Leave-One-Out IV | ⚪ 各有千秋 — 项目的 IV 策略更适合其 Bank-Year 设计；论文的海拔 IV 仅适用于 Province-Year 设计 |
| **媒体异质性** | 官方党报 vs 市场化媒体（双轨对比） | 财经/综合/中央/地方 四维度异质性 | 🟡 **可增强**：项目已有"中央级 vs 地方级"维度，但缺少"官方党报 vs 市场化媒体"的独立分类 |
| **渠道检验** | 治理渠道（CEO 兼任、Big4审计、省级GDP） vs 信息渠道（融资约束）的分样本检验 | 无显式渠道检验 | 🟡 **可增强**：项目面板已具备分样本检验的基础设施（银行类型/规模分组），但缺少显式的渠道检验框架 |
| **MSENT 替代度量** | MSENT1（正负新闻占比差）、MSENT2（词频/总词数）、MSENT3（NRC 词典） | LLM 连续置信度 + 词典法 + BERT 三轨（已天然具备多度量稳健性） | ✅ 维持原状 |

#### 1.3 核心盲区总结

> **唯一实质性盲区**：项目缺少"**媒体所有制/性质分类**"这一论文的核心制度变量。论文的全部理论框架建立在"官方党报（治理功能）vs 市场化媒体（信息功能）"的对比之上。当前项目的 `42_panel_attention_media.py` 已有"中央级 vs 地方级"和"财经 vs 综合 vs 其他"的四维度分类，但**缺少"党委机关报 vs 市场化报纸"的独立分类维度**。

---

### 2. 实质性改进项（宁缺毋滥）

#### 改进 A：新增"官方党报 vs 市场化媒体"双轨情感指标

- **具体修改**：在 `config/media_classification.json` 中新增 `"official_party_press"` 和 `"market_oriented_press"` 两个标签组；在 `42_panel_attention_media.py` 的 `compute_media_heterogeneity()` 中新增 **维度⑤：所有制异质性**，生成 `tone_official_media`, `tone_market_media`, `tone_gap_official_market` 三组情感变量
- **论文依据**：Table 6, Columns (3)-(4) — 官方党报负面情绪系数为 +0.380***（促进创新），市场化媒体负面情绪系数为 −1.327***（抑制创新），二者同时纳入回归后系数方向和显著性均不变
- **边际贡献**：
  - 直接测试"治理渠道 vs 信息渠道"的**竞争性假说**
  - 为项目的银行研究提供制度差异维度：银行业作为强监管行业，官方媒体的治理效应可能更强
  - 加入后项目面板构建代码几乎零增量修改（复用 `42_panel_attention_media.py` 的现有框架）

#### 改进 B：新增 Province × Year 级情感环境变量

- **具体修改**：在 `41_panel_encode_aggregate.py` 的 `aggregate_panel()` 中，基于 `国家地区/省份` 字段计算省级年度情感均值 `prov_media_tone`，作为银行面临的**区域媒体情感环境**控制变量
- **论文依据**：Eq. (2) 中 MSENT 为 province-level × year-level 变量；Panel A.2 控制了省级 PM2.5、环境法规数量、GDP 三个省级变量
- **边际贡献**：
  - 解决现有 Bank-Year 面板缺少**宏观媒体环境**控制变量的遗漏变量偏误
  - 省级情感均值 ≠ 银行特定情感（银行特定 = 报道该银行的新闻情感，省级 = 该省所有银行新闻的整体情感基调），二者编码独立信息
  - 实施成本极低：仅需在聚合阶段增加一个 groupby 操作

#### 改进 C：新增渠道识别分样本检验框架

- **具体修改**：在 `45_panel_export_main.py` 输出面板时，增加分样本标记变量：`is_soe`（国有大型银行 vs 非国有，对应内部治理强度差异）、`is_high_regulation_province`（高/低监管省份，对应外部治理差异），这些变量已可从 `bank_addresses.json` 中的 `nfra_type` 和省份信息推导
- **论文依据**：Table 5, Panels A-E — 分样本检验是区分治理渠道与信息渠道的**核心识别策略**
- **边际贡献**：
  - 使项目具备渠道识别能力（当前仅有总效应估计）
  - 银行业的"国有 vs 非国有"以及"所在省份经济发达程度"是天然的治理结构差异代理变量

---

### 3. 冗余剥离

| 模块 | 评估 | 建议 |
|------|------|------|
| `22_tone_words.py` 词典法情感分析 | 论文使用纯字典法，但当前项目已有 **LLM三模型投票 + BERT五模型**，词典法为第三轨道 | **维持原状** — 论文证明词典法在中国媒体语境中仍有效（Table 3, MSENT1-3 均显著），保留作为稳健性检验基准 |
| `44_panel_iv_did.py` 中的 Bartik IV | 论文使用海拔标准差作为 IV | **维持原状** — Bartik IV 更适合 Bank-Year 面板；海拔 IV 仅在 Province-Year 设计下有效 |
| `42_panel_attention_media.py` 中的金融科技注意力指数 | 与本文完全无关 | **维持原状** — 该模块服务于项目自身的金融科技研究主线，与本文无冲突 |

> ⚠️ **反形式主义声明**：本次审计**不建议任何架构级重构**。项目现有的三轨情感分析 + Bartik IV + 四维度媒体异质性框架已远超论文的方法论水平。全部三项改进均为**数据层面的增量扩展**，利用现有代码框架即可完成。

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布

| 优先级 | 改进项 | 类型 | 实施成本 | 预期收益 |
|--------|--------|------|---------|---------|
| **P0** | 改进 A：官方党报 vs 市场化媒体双轨 | 速赢项 | ⭐ 极低（改配置 + 复用现有框架） | ⭐⭐⭐ 极高（开启渠道识别） |
| **P1** | 改进 B：省级情感环境变量 | 速赢项 | ⭐ 极低（一个 groupby） | ⭐⭐ 高（控制变量完备性） |
| **P2** | 改进 C：渠道识别分样本标记 | 核心攻坚 | ⭐⭐ 低-中（需确认银行分类准确性） | ⭐⭐⭐ 极高（方法论完整性） |

---

### 2. 阶段化执行指令 (SOP)

---

#### 阶段一：数据层扩展与媒体分类重构

**目标**：为项目面板增加"所有制异质性"维度（官方党报 vs 市场化媒体）

##### 动作 1.1：扩展 `config/media_classification.json`

**文件**: `config/media_classification.json`

**操作**：在现有 `financial_media`, `comprehensive_media`, `central_media` 三组之外，新增两组：

```json
{
  "official_party_press": [
    "人民日报", "光明日报", "经济日报", "解放军报",
    "北京日报", "天津日报", "河北日报", "山西日报",
    "内蒙古日报", "辽宁日报", "吉林日报", "黑龙江日报",
    "解放日报", "新华日报", "浙江日报", "安徽日报",
    "福建日报", "江西日报", "大众日报", "河南日报",
    "湖北日报", "湖南日报", "南方日报", "广西日报",
    "海南日报", "重庆日报", "四川日报", "贵州日报",
    "云南日报", "西藏日报", "陕西日报", "甘肃日报",
    "青海日报", "宁夏日报", "新疆日报"
  ],
  "market_oriented_press": [
    "21世纪经济报道", "第一财经日报", "中国经营报",
    "每日经济新闻", "证券日报", "证券时报",
    "上海证券报", "中国证券报", "经济观察报",
    "华夏时报", "新京报", "南方都市报",
    "南方周末", "财经", "财新"
  ]
}
```

**交付物标准**：
- JSON 格式合法，UTF-8 编码
- 与 `media_weights.json` 中的媒体名称完全一致（需交叉校验）
- 党报列表至少覆盖 31 个省级党委机关报

##### 动作 1.2：在 `42_panel_attention_media.py` 中新增维度⑤

**文件**: `42_panel_attention_media.py` — `compute_media_heterogeneity()` 函数

**操作**：在现有维度④（中央级 vs 地方级）之后，新增维度⑤：

```python
# ── 维度⑤: 官方党报 vs 市场化媒体 (He et al. 2024, JCF) ──
OFFICIAL = set(media_cls.get('official_party_press', []))
MARKET = set(media_cls.get('market_oriented_press', []))

df['_is_official'] = df['媒体(中文)'].isin(OFFICIAL).astype(int)
df['_is_market'] = df['媒体(中文)'].isin(MARKET).astype(int)

# 占比
for flag, col in [('_is_official', 'official_media_frac'),
                  ('_is_market', 'market_media_frac')]:
    frac = (df.groupby(['target_bank', 'year'])[flag]
            .mean().reset_index(name=col))
    panel = panel.merge(frac, on=['target_bank', 'year'], how='left')

# 双轨情感均值 + 缺口
for track in ['_full', '_ctx']:
    src = f'llm_vote_score{track}'
    if src not in df.columns:
        continue
    for flag, sfx in [(OFFICIAL, 'official'), (MARKET, 'market')]:
        mask = df['媒体(中文)'].isin(flag)
        tone = (df[mask].groupby(['target_bank', 'year'])[src]
                .mean().reset_index(name=f'tone_{sfx}_media{track}'))
        panel = panel.merge(tone, on=['target_bank', 'year'], how='left')
    panel[f'tone_gap_official_market{track}'] = (
        panel.get(f'tone_official_media{track}', np.nan)
        - panel.get(f'tone_market_media{track}', np.nan))
```

**交付物标准**：
- `official_media_frac` 和 `market_media_frac` 均在 [0, 1] 区间内
- `tone_gap_official_market` 在 [-2, +2] 区间内
- 二者占比之和 **不必** ≤ 1（存在既非党报也非市场化的媒体，如科技类报纸）

##### 动作 1.3：新增省级情感环境变量

**文件**: `41_panel_encode_aggregate.py` — `aggregate_panel()` 函数

**操作**：在 Bank-Year 聚合完成后，追加省级聚合：

```python
# ── 省级年度情感环境 (He et al. 2024, Table 4, Panel A.2) ──
if '国家地区/省份' in df.columns:
    prov_tone = (df.groupby(['国家地区/省份', 'year'])
                 ['llm_vote_score_full'].mean()
                 .reset_index(name='prov_media_tone'))
    # 通过 bank_addresses.json 匹配银行注册省份
    # ... (利用现有 bank_province 映射)
    panel = panel.merge(prov_tone, on=['bank_province', 'year'], how='left')
```

**交付物标准**：
- `prov_media_tone` 为 Province × Year 级常量（同省同年的银行取值相同）
- 覆盖率 ≥ 90%（少量银行可能缺少省份映射）

---

#### 阶段二：渠道识别与分样本标记

**目标**：为面板输出增加渠道检验所需的分样本标记变量

##### 动作 2.1：银行治理结构代理变量

**文件**: `45_panel_export_main.py`

**操作**：从 `bank_addresses.json` 推导以下变量：

| 变量名 | 定义 | 论文对标 |
|--------|------|---------|
| `is_soe` | `nfra_type == '国有大型商业银行'` → 1, 否则 0 | Panel A: CEO duality（内部治理） |
| `is_listed` | 上市银行 → 1, 否则 0 | Panel B: Big4 audit（外部治理） |
| `is_high_gdp_province` | 银行注册省份 GDP 高于样本中位数 → 1 | Panel C: Province GDP |
| `bank_type` | 已有 `bank_type` 列 (soe/joint/city/rural/...) | 直接复用 |

**交付物标准**：
- 所有标记变量为二值整数 (0/1)
- `is_high_gdp_province` 需合并外部省级 GDP 数据（可从 CSMAR 或统计年鉴获取）

##### 动作 2.2：Stata 导出增强

**文件**: `45_panel_export_main.py`

**操作**：确保以下新增变量被正确导出至 `.dta` 文件：

```
新增导出列:
- official_media_frac, market_media_frac
- tone_official_media_full, tone_official_media_ctx
- tone_market_media_full, tone_market_media_ctx
- tone_gap_official_market_full, tone_gap_official_market_ctx
- prov_media_tone
- is_soe, is_listed, is_high_gdp_province
```

**交付物标准**：
- Stata `describe` 显示所有新增变量
- 变量标签 (variable labels) 包含论文溯源信息

---

#### 阶段三：稳健性检验设计

**目标**：为下游实证提供预构建的稳健性检验变量

##### 动作 3.1：替代情感度量变量（论文 Table 3 对标）

当前项目已天然具备多度量稳健性（LLM/词典/BERT 三轨），无需额外操作。仅需在面板导出时确保以下变量同时可用：

| 项目变量 | 论文对标 |
|---------|---------|
| `tone_llm_vote_mean_full` (LLM投票+置信度) | MSENT (基准) |
| `tone_dict_composite_mean` (词典法复合) | MSENT2 (Neg-Pos/Total) |
| `tone_bert_ensemble_mean` (BERT集成) | MSENT3 (NRC词典) |

##### 动作 3.2：滞后变量构建（论文 Eq.2 对标）

论文所有控制变量均取 $t-1$ 期。项目面板中银行特征变量如需滞后，可在 Stata 中操作（`L.variable`），但建议在 Python 导出前预构建：

```python
# 情感变量滞后一期
lag_cols = ['tone_llm_vote_mean_full', 'prov_media_tone',
            'tone_official_media_full', 'tone_market_media_full']
for col in lag_cols:
    panel[f'{col}_lag1'] = panel.groupby('target_bank')[col].shift(1)
```

##### 动作 3.3：置信度衰减稳健性（论文 Panel A.5 对标）

论文 Panel A.5 控制了新闻语言特征（长度 MLENGTH、强度 MINTEN、专指性 MSPECIFICITY）。项目在 `22_tone_words.py` 中已计算可读性指标（`flesch_reading_ease`, `dale_chall_readability`），可直接作为语言特征控制变量使用。

**交付物标准**：维持原状，无需额外计算。

---

### 3. 风险预案 (Plan B)

| 致命卡点 | 概率 | 预案 |
|---------|------|------|
| **`media_classification.json` 中的党报名称与 `media_weights.json` / 实际数据不匹配** | 中 | 在执行前先运行 `df['媒体(中文)'].unique()` 提取实际媒体名称列表，与分类名单交叉校验。不匹配的走模糊匹配 + 人工确认 |
| **党报+市场化媒体合计覆盖率过低（<30%）** | 低 | 项目数据源侧重银行新闻，而非全量报纸新闻。若覆盖率过低，改为"官方背景媒体 vs 商业媒体"的宽口径分类（可与 `central_media` 列表部分复用） |
| **省级 GDP 外部数据不可得** | 极低 | 使用 `bank_addresses.json` 中的 `enterprise_scale`（L/M/S/XS）作为替代。大型银行通常位于发达省份，形成代理变量 |
| **省级情感变量 `prov_media_tone` 与银行特定情感高度共线** | 中 | 检查 VIF。若 VIF > 10，改为省级情感的**残差**（正交化后的省级非银行特定情感），或直接使用**省级新闻数量**（`prov_news_count`）作为替代 |
| **分样本检验中部分组别样本量过小** | 中 | 若某组别（如 `is_soe == 1`）观测值 < 100，改用交互项回归 `MSENT × is_soe` 替代分样本 Chow 检验 |

---

## 附录：论文核心方程与项目变量映射

### 基准回归方程（论文 Eq.2）

$$
GreenInnovation_{i,t} = \beta_0 + \beta_1 MSENT_{j,t-1} + \lambda Controls_{i,t-1} + \delta Indus_i + \theta Year_t + \varepsilon_{i,t}
$$

### 项目变量映射

| 论文符号 | 论文定义 | 项目对应变量 | 备注 |
|---------|---------|------------|------|
| $MSENT_{j,t-1}$ | 省级年度党报污染新闻负面情绪 | `prov_media_tone_lag1`（新增）或 `tone_official_media_full_lag1`（新增） | 滞后一期 |
| $MSENT\_MARKET$ | 市场化媒体负面情绪 | `tone_market_media_full`（新增） | — |
| $GPT$ | 绿色专利数的对数 | — | 文的因变量，非本项目研究范围 |
| $SIZE$, $LEV$, $ROA$ 等控制变量 | 企业财务特征 | 银行财务特征（需外部匹配） | — |
| Industry / Year FE | 行业×年度固定效应 | `bank_type` + `year` | — |
| Elevation SD (IV) | 省级海拔标准差 | 不建议采用（项目为 Bank-Year 设计） | 项目使用 Bartik IV 更优 |

---

> **⚠️ 反形式主义声明**：以上执行计划严格遵循"不为改而改"的原则。项目现有的 LLM 三模型集成情感分析、Bartik IV 策略、四维度媒体异质性框架均**严格优于或等价于**论文方法，**维持原状**。三项改进均为基于论文核心发现的**数据层增量扩展**，总代码增量 < 100 行，不涉及任何架构变更。
