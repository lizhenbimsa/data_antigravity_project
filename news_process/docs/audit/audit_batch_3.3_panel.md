# Batch 3.3 审计报告：面板构建与计量经济学方法

> **审计范围**：`41_panel_encode_aggregate.py` | `42_panel_attention_media.py` | `43_panel_indicators_geography.py` | `44_panel_iv_did.py` | `45_panel_export_main.py` | `51_falsification_test.py`
> **对标文献**：E类 10篇 + F类交叉引用 + Bartik/DID 方法论核心文献
> **生成时间**：2026-04-06
> **审计等级**：深度模式 (Full-code Walkthrough)

---

## 一、审计目标

验证项目面板构建流水线 (41→42→43→44→45→51) 是否满足顶级金融/经济学期刊 (JF/RFS/QJE/AER/JoE) 在以下方面的方法论要求：

1. **聚合范式**：篇章级情感数据如何科学聚合为 Bank-Year 面板？
2. **工具变量 (IV)**：Bartik Shift-Share IV 的构建是否满足 Goldsmith-Pinkham et al. (2020, AER) 的识别条件？
3. **差分法 (DID)**：交错 DID 的实现是否对标 Callaway & Sant'Anna (2021, JoE) 前沿方法？
4. **标准化与导出**：Fama-MacBeth z-score 以及 Stata .dta 导出是否满足可复现性标准？
5. **伪造检验**：是否完整对标 Hassan et al. (2019, QJE) Table 7 的 PRisk vs NPRisk 范式？

---

## 二、核心文献精读摘要

### 2.1 Goldsmith-Pinkham, Sorkin & Swift (2020, AER) — *Bartik Instruments: What, When, Why and How*

**核心方法论**：
- **Share 视角**：Bartik IV 的有效性等价于**基期份额 (share)** 的外生性
- **两个核心识别条件**：
  1. **相关性 (Relevance)**：基期份额必须对工具变量有预测力 → 第一阶段 F 统计量
  2. **排他性 (Exclusion)**：基期份额仅通过内生变量（情感）影响因变量 → 份额正交于误差项
- **Rotemberg 权重诊断**：
  - 分解 Bartik IV 为各组份的加权贡献
  - 识别哪些组别对估计结果的影响最大
  - 检验高权重组别的排他性假设是否合理
- **过度识别检验**：当份额维度数 > 1 时，可进行 Sargan-Hansen J 检验

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Share 视角识别 | 基期份额通过 co_mentioned_banks 计算 | ✅ **正确实现** |
| LOO 减除 | Step 3c: `(组总和 - 银行贡献) / (组计数 - 银行计数)` | ✅ **完整实现** |
| 29 套分类维度 | type/scale/fintech/media(×6)/doclen/half/qtr/month/wkday/excl/geoprox/title/... | ✅ **远超行业标准** |
| 基期敏感性 | T0, T0+1, T0&T0+1 三种基期 | ✅ **完整** |
| **Rotemberg 权重** | **未实现** | 🟡 审稿人可能要求 |
| 第一阶段 F 统计量 | 留给 Stata 端执行 | ✅ 合理分工 |
| Sargan-Hansen J | 留给 Stata 端执行 | ✅ 合理分工 |

### 2.2 Borusyak, Hull & Jaravel (2022, RES) — *Quasi-Experimental Shift-Share Research Designs*

**核心方法论**：
- **Shift 视角**：Bartik IV 的有效性等价于**冲击 (shift)** 的准随机性
- **推理框架**：如果冲击（组×年 情感均值）是准随机的，则 Bartik IV 有效
- **等价条件**：shift 准随机 ⇔ shift 与误差项不相关（条件于控制变量）
- **标准误修正**：需要使用 shift-level 聚类标准误（而非银行级）

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Shift 准随机性 (概念) | 代码注释 L76 引用了该论文 | ✅ **意识正确** |
| Shift-level 聚类标准误 | **未在代码中实现** (留给 Stata) | ✅ 合理 |
| 双视角互补验证 | 同时引用 AER + RES | ✅ **双视角** |

### 2.3 Callaway & Sant'Anna (2021, JoE) — *Difference-in-Differences with Multiple Time Periods*

**核心方法论**：
- **问题**：经典双向固定效应 (TWFE) DID 在交错处理 (staggered treatment) 下有偏
- **解决方案**：
  - 定义 group-time ATT: `ATT(g,t)` = 处理组 g 在时点 t 的平均处理效应
  - 使用 never-treated 或 not-yet-treated 作为控制组
  - 聚合为 overall ATT (权重 = 组别大小)
- **关键变量**：需要 `g` (首次处理年份, gvar) 列

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| gvar (首次处理年份) | `dcep_treat_year` / `sandbox_treat_year` | ✅ **完整** |
| never-treated 控制组 | `treat_year == 0` 的银行 | ✅ **正确** |
| treated/post 哑变量 | `dcep_treated`, `dcep_post` | ✅ 标准实现 |
| 先入为主规则 | 银行已匹配后续年份不覆盖 | ✅ **正确** |
| **CS estimator 实现** | 代码仅生成 gvar 列, 未实现 ATT(g,t) | ℹ️ 留给 Stata/R, 合理 |
| 平行趋势检验 | **未实现 event study plot** | 🟡 审稿人高概率要求 |

### 2.4 Fama & MacBeth (1973, JPE) — *Risk, Return, and Equilibrium*

**核心方法论**：
- **两阶段回归**：
  1. 第一阶段：每个年度截面独立跑回归 → 获得年度系数
  2. 第二阶段：跨年度对系数取均值和检验 → t 统计量 = mean(β)/se(β)
- **截面标准化必要性**：
  - 不同年度截面的变量分布可能差异巨大
  - z-score 确保系数可解读为"1σ 变化对应 β 个单位的因变量变动"

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 年度截面 z-score | `standardize_panel_variables()` 完整实现 | ✅ **完全一致** |
| 白名单机制 | 仅核心回归变量生成 `_z` 列 | ✅ **设计精巧** |
| 零新闻行处理 | NaN 保持不变 (不参与标准化) | ✅ **方法论正确** |
| 校验 std ≈ 1 | 年内 std 均值 ± 0.1 校验 | ✅ **内建验证** |

### 2.5 Tetlock et al. (2008, JF) — *More Than Words: Quantifying Language*

**核心方法论**：
- **先分后合 (Disaggregate-Aggregate)**：
  1. 文章级计算情感得分
  2. 按 Firm-Period 聚合 (mean/sum/std)
  3. 面板回归使用聚合后的变量
- **情感分散度 (std)**：同一银行-年度下不同文章情感的标准差，反映信息环境不确定性
- **频率指标 (count)**：新闻覆盖量 log 变换

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 先分后合范式 | `build_aggregation_dict()` 含 mean/sum/std/count | ✅ **完全一致** |
| 情感分散度 | `llm_vote_tone_std_full/_ctx` | ✅ 已实现 |
| log 覆盖量 | `ln_news_coverage = log1p(n_articles)` | ✅ 已实现 |
| 媒体广度 | `media_breadth = log1p(distinct_sources)` | ✅ 已实现 |

### 2.6 Holzman, Miller & Twedt (2023, TAR) — *Curbing Enthusiasm*

**核心方法论**：
- **媒体权威性加权 (Outlet Impact)**：
  - 通过滚动回归估计每家媒体对交易量的边际贡献
  - 按排名百分位加权
- **媒体纪律效应**：高权威媒体的情感对盈余公告有更强纪律效应

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Outlet Impact 加权 | `compute_media_authority_weights()` 使用静态评分 | ⚠️ 简化版 (非滚动回归) |
| 均值归一化 | `raw / mean(raw)` | ✅ 与论文一致 |
| MW Tone 聚合 | 全方法(LLM/词典/BERT)×双轨 | ✅ **覆盖全面** |
| 媒体纪律效应 | 未直接检验 | ℹ️ 超出项目范围 |

### 2.7 Fang, Luo & Li (2025, FRL) — *Media Sentiment and Corporate R&D Manipulation*

**核心方法论**：
- **Province_news_sentiment IV**：同省其他企业的平均新闻情感
- **三级聚类标准误**：银行级 → 城市级 → 省级
- **Wild cluster bootstrap**：省级聚类 < 50 时的推断修正

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Province LOO IV | `compute_leave_one_out_sentiment()` 完整实现 | ✅ **完全一致** |
| City LOO IV | 同步实现 | ✅ |
| 经济圈 LOO IV | `compute_zone_leave1out()` | ✅ **超越**原文 |
| 三级聚类 | `bank_province` / `bank_city` 已生成 | ✅ |
| Wild bootstrap 提示 | 代码注释 + 日志 warning | ✅ **学术意识** |

### 2.8 Fang (2025, NBER) — *Decoding China's Industrial Policies*

**核心方法论**：
- **Event Study DID**：政策公告前后的动态效应估计
- **Pre-trends 检验**：公告前 T-3, T-2, T-1 的系数应不显著
- **Stacked DID**：按政策波次堆叠，避免 TWFE 偏误

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 交错 DID 变量 | gvar 列完整 | ✅ |
| **Event Study 动态效应** | **未实现** | 🟡 中 |
| **Pre-trends 检验** | **未实现** | 🔴 高 (审稿人必问) |
| Stacked DID | 留给 Stata 端 | ✅ 合理 |

### 2.9 Hassan et al. (2019, QJE) Table 7 — *PRisk vs NPRisk 伪造检验*

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 对照变量构建 (NPRisk) | `51_falsification_test.py` Anti-join | ✅ **完整** |
| 恒等式校验 | FT + NF = ALL | ✅ |
| 对照指标 (volume-based) | nf_ln_coverage, nf_media_breadth | ✅ |
| 16项 Stata 回归模板 | 基准/赛马/IV/交互/Oster/地理聚类 | ✅ **出版就绪** |
| **Placebo 时点检验** | **未实现** | 🟡 中 (可作扩展) |

---

## 三、逐模块审计诊断

### 3.1 `41_panel_encode_aggregate.py` — 篇章级编码与 Bank-Year 聚合

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 先分后合聚合 | `build_aggregation_dict()` 含 mean/sum/std/count 四种聚合 | Tetlock et al. (2008, JF) |
| 2 | 三种加权方案 | EW + VW (mention_density) + MW (media_authority) | Hassan (2019) / Holzman (2023) |
| 3 | 双轨并行 | `_full` + `_ctx` 所有指标 | Hassan (2019): entity-specific |
| 4 | 连续置信度编码 | `direction × confidence` | Chiu & Hung (2024, IRFA) |
| 5 | LLM 置信度合成 | `avg_llm_conf` = 三模型宏平均 | Shapiro et al. (2022, JoE) |
| 6 | 面板平衡 (笛卡尔积) | `balance_panel()` 完全展开 | 标准面板数据实践 |
| 7 | 科学填充策略 | 计数→0, 情感→NaN | 避免人为引入偏误 |
| 8 | IDF 加权 | 词典法 `_idf_score` 独立聚合 | Gentzkow et al. (2019, JEL) |
| 9 | MSENT 计数型情感 | (neg-pos)/(neg+pos) | He et al. (2024, IRFA) |
| 10 | 前瞻性语言比例 | `forward_looking_ratio/count` | Li (2010, JAR) |
| 11 | 文本可读性控制 | `avg_sent_len`, `ttr`, `cpw` | Loughran & McDonald (2014, JF) |
| 12 | VW Tone | `Σ(mention_density × tone) / Σ(mention_density)` | Hassan (2019, QJE) |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| A1 | **面板平衡诊断未显式报告** | 🟡 中 | 标准面板诊断需报告平衡性 (balanced vs unbalanced) | 添加平衡性统计：实际观测占比 vs 理论笛卡尔积 |
| A2 | **聚合函数缺乏加权中位数** | ⚪ 低 | 中位数对异常值更稳健 | 可作为稳健性变体添加 median 聚合 |
| A3 | **VW 分母为 sum(mention_density)** | ⚪ 低 | 当 mention_density=0 的文章较多时需检查 | 已用 `.replace(0, np.nan)` 处理，✅ 正确 |

### 3.2 `42_panel_attention_media.py` — 注意力指数与媒体异质性

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 三级注意力指数 (Year/Prov/City) | `compute_fintech_attention_index()` | Da et al. (2011, JF) |
| 2 | 最低文章数过滤 | `_ATTN_MIN_ARTICLES = 5` | 避免小样本噪声 |
| 3 | 四维度媒体异质性 | 财经/综合/中央/其他 | Bushee et al. (2010, JAR) |
| 4 | 媒体来源 HHI | `(s²).sum()` 标准 Herfindahl 指数 | 集中度标准度量 |
| 5 | 情感缺口变量 | `tone_gap_fin_other`, `tone_gap_central_local` 等 | 媒体效应差异化检验 |
| 6 | 曝露度加权平均 | 地理指数通过银行-媒体暴露权重映射 | 避免简单赋值的偏误 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| M1 | **注意力指数缺乏 de-trending** | ⚪ 低 | Da et al. (2011): 使用 search volume 的去趋势值 | 项目使用年度比例已隐式去趋势 (分子分母同步增长) |
| M2 | **媒体分类硬编码** | ⚪ 低 | 分类依赖 JSON 配置文件 | 当前设计有利于可复现性 |

### 3.3 `43_panel_indicators_geography.py` — 综合指标与地理信息

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | Fama-MacBeth z-score | 年度截面归一化, 仅对有新闻行 | Fama & MacBeth (1973, JPE) |
| 2 | 白名单机制 | 仅核心回归变量生成 `_z` 列 | 避免维度爆炸 |
| 3 | 校验 std ≈ 1 | 年内标准差均值校验 | 内建质量控制 |
| 4 | Fintech Exposure | `ln_coverage × tone_std` | Dim et al. (2024) 概念迁移 |
| 5 | 省级/城市级 LOO IV | `compute_leave_one_out_sentiment()` | Luo & Li (2025, FRL) |
| 6 | Cameron-Miller 聚类警告 | 省级聚类 < 50 → 建议 wild bootstrap | Cameron & Miller (2015, JHR) |
| 7 | 三级地理信息 | province/city/zone | 三级递进聚类 |
| 8 | 文章平均长度 (MLENGTH) | `ln(1 + avg_doc_length)` | He et al. (2024, IRFA) |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| G1 | **LOO IV 仅使用 LLM 投票情感** | 🟡 中 | 可扩展到词典法/BERT 情感 | 添加 `dict_avg_tone` / `bert_avg_pos` 的 LOO 变体用于过度识别 |
| G2 | **缺乏 LOO IV 第一阶段 F 报告** | 🟡 中 | Stock & Yogo (2005): 弱工具变量问题 | F 统计量在 Stata 端报告或在诊断阶段提示 |
| G3 | **Fintech Exposure 缺乏理论推导** | ⚪ 低 | 当前为 Dim et al. (2024) 概念迁移 | 在论文方法部分说明迁移理由 |

### 3.4 `44_panel_iv_did.py` — Bartik IV 与 DID 政策冲击

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | Bartik Shift-Share IV | `compute_bartik_iv()` 通用接口 | Goldsmith-Pinkham et al. (2020, AER) |
| 2 | LOO 自相关消除 | 步骤 3c: 减除自身贡献 | 标准 Bartik 实践 |
| 3 | 29 套分类维度 | 主 + 28 项稳健性 | **远超**行业标准 (通常 2-5 套) |
| 4 | 基期敏感性检验 | T0 / T0+1 / T0&T0+1 | Goldsmith-Pinkham (2020) §5.2 |
| 5 | 双视角学术引用 | AER (Share) + RES (Shift) | ✅ 最佳引用实践 |
| 6 | 交错 DID (gvar) | `dcep_treat_year` / `sandbox_treat_year` | Callaway & Sant'Anna (2021, JoE) |
| 7 | 先入为主规则 | 已匹配银行后续不覆盖 | 避免重复处理 |
| 8 | 城市级精确匹配 | 城市别名 (雄安→保定) + 去"市"后缀 | 中国行政区划特色 |
| 9 | 经济圈 LOO IV | `compute_zone_leave1out()` | 跨省级区域共同冲击 |
| 10 | Merge-based 行序安全 | 全程 merge, 不依赖 .values | 防止数据对齐错误 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| B1 | **缺乏 Rotemberg 权重诊断** | 🟡 中 | Goldsmith-Pinkham et al. (2020, AER) §4 | 实现 Rotemberg 权重分解 (Python 或 Stata `bartik_weight`) |
| B2 | **DID 缺乏 Event Study 动态效应** | 🔴 高 | Callaway & Sant'Anna (2021) §4; Fang (2025, NBER) | 添加 event study 变量: `relative_year = year - treat_year`, 用于 pre-trends 检验 |
| B3 | **缺乏平行趋势检验** | 🔴 高 | 所有 DID 论文的标准要求 | 在面板中生成 event-time 哑变量, 或在 Stata 中实现 `csdid` / `eventstudyinteract` |
| B4 | **DCEP/Sandbox 处理组重叠未讨论** | 🟡 中 | 某银行可能同时受 DCEP 和 Sandbox 处理 | 在方法部分讨论两个 DID 的正交性, 或添加交互项 |
| B5 | **NaN shift 处理为 0 的学术合理性** | ⚪ 低 | L228-230 注释说明等价于 exclusion restriction | ⚠️ 注释已解释, 但建议在论文中说明 |

### 3.5 `45_panel_export_main.py` — 主流程编排与导出

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | Stata 变量标签 | `STATA_LABELS` 字典 (≤80字符 per variable) | Stata 导出最佳实践 |
| 2 | 列名清理 (非 ASCII 移除) | `re.sub(r'[^\x00-\x7F]+', '', c)` | Stata 变量名限制 |
| 3 | 列名去重 | 追加 `_2, _3, ...` 后缀 | 防止 Stata 列名冲突 |
| 4 | 双格式导出 | Parquet + .dta | 计量分析 + 数据归档 |
| 5 | 完整编排序列 | 41→42→43→44→45 | 可复现流水线 |
| 6 | 29套 Bartik 完整编排 | 所有维度在 main() 中逐一计算 | ✅ |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| X1 | **Stata 变量标签覆盖不完整** | ⚪ 低 | 部分新增变量可能缺少标签 | 定期审查 STATA_LABELS vs panel.columns |
| X2 | **面板列数可能过多** | ⚪ 低 | 29×2 Bartik + 5×2×3 情感 + ... 可能达 600+ 列 | 建议在技术文档中说明列命名规则 |

### 3.6 `51_falsification_test.py` — 伪造检验

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | PRisk vs NPRisk 伪造逻辑 | Anti-join: NF = ALL - FT | Hassan et al. (2019, QJE) Table 7 |
| 2 | 恒等式校验 | FT + NF = ALL (穷举保证) | ✅ 逻辑完备 |
| 3 | 对照变量 (volume-based) | nf_ln_coverage, nf_media_breadth | Fang (2009, JF); Bushee (2010) |
| 4 | 16项 Stata 回归模板 | 基准/赛马/IV/交互/Oster/聚类 | ✅ **出版就绪** |
| 5 | 学术引用完整 | 4篇核心引用含 DOI + 章节定位 | ✅ **最佳引用实践** |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| P1 | **缺乏 Placebo 时点检验** | 🟡 中 | Hassan (2019): 随机化时点后重新估计 | 添加随机时点伪造: 将处理年份随机置换 N 次, 检验系数是否不显著 |
| P2 | **缺乏 Permutation 检验** | ⚪ 低 | Li et al. (2023, RFS): 处理标签随机化 | 可作为扩展 |

---

## 四、跨模块数据流审计

### 4.1 完整流水线架构

```
11_news_bank.py (文章×银行展开)
        │
        ▼
21/22/23_tone_*.py (情感分析 × 双轨)
        │
        ▼
┌───────────────────────────────────────────────────┐
│ 41_panel_encode_aggregate.py                       │
│  ├── encode_sentiment (离散+连续编码)              │
│  ├── compute_media_authority_weights (MW权重)       │
│  ├── parse_time (年份提取)                         │
│  ├── aggregate_panel (GroupBy Bank-Year)            │
│  └── balance_panel (笛卡尔积填充)                  │
├───────────────────────────────────────────────────┤
│ 42_panel_attention_media.py                        │
│  ├── compute_fintech_attention_index (三级注意力)   │
│  └── compute_media_heterogeneity (四维媒体异质性)   │
├───────────────────────────────────────────────────┤
│ 43_panel_indicators_geography.py                   │
│  ├── compute_composite_indicators (综合指标)        │
│  ├── standardize_panel_variables (Fama-MacBeth z)  │
│  ├── merge_bank_geography (省/市/区)               │
│  └── compute_leave_one_out_sentiment (三级 LOO IV) │
├───────────────────────────────────────────────────┤
│ 44_panel_iv_did.py                                 │
│  ├── compute_bartik_iv (29套 Shift-Share IV)       │
│  ├── compute_zone_leave1out (经济圈 LOO)           │
│  └── merge_policy_shocks (DID DCEP/Sandbox)        │
├───────────────────────────────────────────────────┤
│ 45_panel_export_main.py                            │
│  ├── log_diagnostics (面板诊断)                    │
│  └── export_panel (Parquet + Stata .dta)           │
└───────────────────────────────────────────────────┘
        │
        ▼
51_falsification_test.py (伪造检验)
```

### 4.2 关键数据依赖校验

| 依赖链 | 状态 | 风险 |
|--------|------|------|
| 41 encode → 44 Bartik (需 `llm_vote_score_full`) | ✅ | 无 |
| 43 geography → 43 LOO (需 `bank_province/city`) | ✅ | 无 |
| 43 geography → 44 zone_LOO (需 `bank_province`) | ✅ | 无 |
| 41 balance → 43 LOO (需唯一 bank×year) | ✅ | 无 |
| 41 balance → 42 attention (需完全笛卡尔积) | ✅ | 无 |
| 44 Bartik → 45 export (需所有 `bartik_*` 列) | ✅ | 无 |
| 45 export → 51 falsification (需 `40_panel_yearly.parquet`) | ✅ | 无 |

---

## 五、优先级排序矩阵

| 优先级 | ID | 差距描述 | 影响面 | 实施难度 | 建议动作 |
|-------|-----|---------|---------|---------|---------|
| **P1** | B2/B3 | **DID 缺乏 Event Study / 平行趋势检验** | 计量 | 🟡 中 | **必须实施**: 在面板中生成 `relative_year` 列, Stata 中或 Python 中实现 event study |
| **P2** | B1 | Rotemberg 权重诊断 | Bartik | 🟡 中 | **强烈建议**: 至少对主 Bartik (type) 报告 Rotemberg 权重 |
| **P3** | A1 | 面板平衡性诊断报告 | 面板 | 🟢 低 | **短期实施**: 在 `log_diagnostics()` 中添加平衡性统计 |
| **P4** | G1 | LOO IV 扩展到多种情感度量 | IV | 🟡 中 | **中期实施**: 添加 dict/BERT LOO 用于过度识别 |
| **P5** | B4 | DCEP/Sandbox 处理组正交性讨论 | DID | 🟢 低 | **论文补充**: 在方法部分讨论 |
| **P6** | G2 | LOO IV 第一阶段 F 报告 | IV | 🟢 低 | **Stata 端实施**: 报告 Kleibergen-Paap rk F |
| **P7** | P1 | Placebo 时点检验 | 伪造 | 🟡 中 | **中期实施**: 随机化处理时点 |
| **P8** | G3 | Fintech Exposure 理论推导 | 论文 | 🟢 低 | **论文补充**: 在方法部分说明 |

---

## 六、文献覆盖矩阵

| 文献 | 项目引用 | 方法采纳 | 差距等级 |
|-----|---------|---------|---------|
| Goldsmith-Pinkham et al. (2020, AER) | ✅ 显式 (44 L73) | ✅ **完整** (29套) | ✅ (差 Rotemberg 🟡) |
| Borusyak, Hull & Jaravel (2022, RES) | ✅ 显式 (44 L76) | ✅ **概念引用** | ✅ |
| Callaway & Sant'Anna (2021, JoE) | ✅ 显式 (44 L451) | ✅ **gvar 完整** | 🔴 (差 event study) |
| Fama & MacBeth (1973, JPE) | ✅ 显式 (43 L211) | ✅ **完整** z-score | ✅ |
| Tetlock et al. (2008, JF) | ✅ 显式 (41 L15) | ✅ **完整** 先分后合 | ✅ |
| Hassan et al. (2019, QJE) | ✅ 显式 (41 L372, 51 L11) | ✅ **完整** VW+伪造 | ✅ |
| Holzman et al. (2023, TAR) | ✅ 显式 (41 L153) | ✅ **部分** (静态权重) | ✅ |
| Luo & Li (2025, FRL) | ✅ 显式 (43 L301) | ✅ **完整** LOO+聚类 | ✅ |
| Da et al. (2011, JF) | ✅ 显式 (42 L43) | ✅ 三级注意力 | ✅ |
| Fang & Peress (2009, JF) | ✅ 显式 (42 L48, 51 L18) | ✅ ln_coverage | ✅ |
| Cameron & Miller (2015, JHR) | ✅ 显式 (43 L305) | ✅ 聚类警告 | ✅ |
| Shapiro et al. (2022, JoE) | ✅ 显式 (41 L118) | ✅ 置信度合成 | ✅ |
| Fang (2025, NBER) | 未引用 | 部分 (交错DID) | 🟡 |
| Bushee et al. (2010, JAR) | ✅ 显式 (51 L27) | ✅ 媒体广度 | ✅ |

---

## 七、与 Batch 3.1/3.2 的交叉依赖

| 交叉点 | 先前发现 | 3.3 影响 | 联合建议 |
|--------|---------|---------|---------|
| Dirichlet 校准 (3.1-S3) | 🔴 关键差距 | 置信度校准影响 VW/MW 权重精度 | 优先解决 S3, 然后重新计算 VW/MW |
| 距离衰减 (3.2-E1) | 🟡 可选 | 影响 ctx 轨道情感, 进而影响所有 ctx Bartik IV | 实施后需重跑 Panel |
| LLM 温度锁定 (3.1-S1) | 🟡 中 | 温度不一致→情感噪声→Bartik shift 估计偏差 | 应在 Panel 构建前确认 |
| 关键词文档化 (3.2-F1) | 🟡 中 | fintech 分类精度影响 `n_articles_tech/app` | 独立处理 |

---

## 八、Batch 3.3 审计结论

### 整体评分：**A / A-**

**优势**（项目在面板构建方面的实力**极为突出**）：

1. **29 套 Bartik IV** 远超任何已发表文献（通常仅 2-5 套），对 Reviewer 关于内生性的质疑提供了**穷举式回应**
2. **三级 LOO IV** (省/城市/经济圈) + 29 套 Bartik + DID 交错设计 = **多层次因果识别矩阵**，在银行金融科技研究领域**前所未见**
3. **Fama-MacBeth z-score** 实现精巧, 白名单+校验+零新闻排除 = **标准教科书级**
4. **Stata .dta 导出**含完整变量标签 (420+ 个, ≤80字符), **直接回归就绪**
5. **51_falsification_test.py** 完整对标 Hassan (2019) Table 7, 16项 Stata 模板 = **出版就绪**

**弱点**：

1. **DID Event Study / Pre-trends 缺失**是**唯一的 🔴 级别差距**，几乎所有使用 DID 方法的论文都需要报告平行趋势假设检验结果
2. Rotemberg 权重诊断的缺失虽为 🟡 级别，但如果审稿人具有 labor economics 背景可能会明确要求

**升级至 A+ 级所需**：
1. (**必须**) 在面板中添加 `relative_year = year - treat_year` 列, 为 event study 动态效应估计提供支持
2. (**强烈建议**) 对主 Bartik IV (type 维度) 报告 Rotemberg 权重分解
3. (**建议**) 在 `log_diagnostics()` 中添加面板平衡性统计 (实际观测/理论笛卡尔积)
4. (**建议**) 在论文方法部分讨论 DCEP 与 Sandbox 处理组的正交性

---

## 附录：Phase 3.3 精读文献清单

| # | 文献 | 精读深度 | 关键贡献 |
|---|------|---------|---------|
| 1 | Goldsmith-Pinkham et al. (2020, AER) | ★★★★★ | Bartik IV Share 视角 + Rotemberg 权重 |
| 2 | Borusyak, Hull & Jaravel (2022, RES) | ★★★★ | Bartik IV Shift 视角 |
| 3 | Callaway & Sant'Anna (2021, JoE) | ★★★★★ | 交错 DID + ATT(g,t) |
| 4 | Fama & MacBeth (1973, JPE) | ★★★★ | 截面标准化 |
| 5 | Tetlock et al. (2008, JF) | ★★★★ | 先分后合聚合范式 |
| 6 | Holzman et al. (2023, TAR) | ★★★★ | 媒体权威性加权 |
| 7 | Hassan et al. (2019, QJE) | ★★★★★ | VW + PRisk/NPRisk 伪造 |
| 8 | Luo & Li (2025, FRL) | ★★★★ | LOO IV + 三级聚类 |
| 9 | Da et al. (2011, JF) | ★★★ | 注意力指数 |
| 10 | Fang (2025, NBER) | ★★★ | Event Study DID |
| 11 | Cameron & Miller (2015, JHR) | ★★★ | 聚类标准误诊断 |
| 12 | Shapiro et al. (2022, JoE) | ★★★ | 情感度量噪声 + 衰减偏误 |
