# Media Narratives and Price Informativeness — 执行计划

## 目标

将 Dim, Sangiorgi & Vilkov (2024) 《Media Narratives and Price Informativeness》(SSRN 4323093) 的核心方法论框架集成到 `news_process` 管道中。

---

## 前置依赖确认

> [!IMPORTANT]
> 以下数据源是 Phase 2-3 的**阻塞性依赖**，需在开发前确认：
> 1. **银行日度收益率**: 中国上市银行 A 股日度收益率 (来源: CSMAR / Wind / Tushare)
> 2. **中国因子模型**: CH-3 或 CH-4 因子日度收益率 (来源: CSMAR 或自建)
> 3. **市场微观结构数据**: 日度成交量、买卖价差 (用于 BNPW VAR)

---

## Phase 1: LDA 叙事话题提取

### 新建文件: `25_topic_lda.py`

#### 输入
- `data_processed/00_preprocessed.parquet` (清洗后新闻语料)

#### 输出
- `data_processed/25_lda_model/` (训练好的 LDA 模型目录)
- `data_processed/25_topic_daily_attention.parquet` (日×话题 注意力矩阵)
- `data_processed/25_topic_attention_shocks.parquet` (日×话题 5日差分冲击)

#### 任务清单

- [ ] **1a. 语料二次预处理**
  - jieba/pkuseg 中文分词
  - 加载中文停用词表 (哈工大 + 百度)
  - 过滤低频词 (df < 5) 和高频词 (df > 50%)
  - 最短文档阈值: 20 词 (与论文一致)
  - 输出: 词袋矩阵 (scipy sparse) + 词典 (gensim Dictionary)

- [ ] **1b. 话题数选择 (交叉验证)**
  - 候选范围: K ∈ {10, 15, 20, 25, 30, 33, 35, 40, 50}
  - 交叉验证策略: 按新闻来源×年份分折 (论文使用 WSJ Section×Year)
  - 评价指标: log-perplexity + coherence score (C_v)
  - 可视化: 肘部法则图 → 保存为 `eval_reports/25_topic_cv.png`
  - 在 `config.yaml` 的 `topic_modeling` 节配置参数

- [ ] **1c. LDA 模型训练**
  - 使用 gensim `LdaMulticore` (多核并行)
  - 超参数: α=auto, η=auto, iterations=1000, passes=20
  - 保存模型到 `data_processed/25_lda_model/`
  - 生成 Top-100 unigram/bigram 词表 → CSV 供人工标注

- [ ] **1d. 日频注意力聚合**
  - 公式: θ_{l,τ} = (1/M) Σ θ_{m,l,τ} / D_τ
  - 归一化: 确保每日所有话题注意力之和 = 1
  - 输出: `25_topic_daily_attention.parquet` (columns: date, topic_0..topic_K)

- [ ] **1e. 注意力冲击计算**
  - 公式: Δθ_{l,τ} = θ_{l,τ} - (1/5) Σ_{i=1}^{5} θ_{l,τ-i}
  - 处理缺失日期: 非交易日使用前一交易日值前移
  - 输出: `25_topic_attention_shocks.parquet`

- [ ] **1f. 话题标签与诊断**
  - 人工标注 Top-100 关键词 → 为每个话题命名
  - 可视化: 话题注意力时序图 (对标论文 Figure 1)
  - 诊断: 话题间相关性矩阵, 确认低相关 (|r| < 0.3)

#### config.yaml 新增配置

```yaml
topic_modeling:
  n_topics: 33                    # 默认话题数 (交叉验证后可调)
  cv_topic_range: [10, 15, 20, 25, 30, 33, 35, 40, 50]
  min_doc_length: 20              # 最短文档词数
  min_df: 5                       # 最小文档频率
  max_df_ratio: 0.5               # 最大文档频率比例
  lda_iterations: 1000
  lda_passes: 20
  attention_shock_window: 5       # 注意力冲击的回溯窗口 (日)
  random_state: 42
```

---

## Phase 2: Narrative Exposure 计算

### 新建文件: `26_narrative_exposure.py`

#### 输入
- `data_processed/25_topic_attention_shocks.parquet`
- 银行日度收益率数据 (外部数据源)
- 中国因子模型日度收益率 (外部数据源)

#### 输出
- `data_processed/26_narrative_betas.parquet` (Bank-Year-Topic 级别 β)
- `data_processed/26_narrative_exposure.parquet` (Bank-Year 级别 Exposure)

#### 任务清单

- [ ] **2a. 外部数据加载与对齐**
  - 加载银行日度收益率 (确认代码/名称与管道 target_bank 的映射)
  - 加载 CH-3/CH-4 因子日度数据
  - 日期对齐: 交易日历 + 注意力冲击序列

- [ ] **2b. 增强因子模型估计**
  - 对每家银行 n、每年 t、每个话题 l:
    ```
    r_{n,τ} = α + β_n^T F_τ + β_{n,t,l}^{narr} Δθ_{l,τ} + ε
    ```
  - 使用 OLS (statsmodels), 最少观测数: 120 天/年
  - 提取 β_{n,t,l}^{narr} → 叙事 Beta

- [ ] **2c. Narrative Exposure 聚合**
  - 公式: NarrExp_{n,t} = Σ_l |β_{n,t,l}^{narr}| × σ_t(θ_l) / Σ_l σ_t(θ_l)
  - σ_t(θ_l) = 话题 l 在年 t 的注意力日度标准差
  - 输出: Bank-Year 面板级变量

- [ ] **2d. 诊断与校验**
  - 与现有 `fintech_exposure` 的 Pearson/Spearman 相关性
  - 按银行规模分组的 Exposure 分布 (对标论文 Figure 1B)
  - 按年度的 Exposure 均值时序图 (对标论文 Figure 1A)
  - 增量 R² 检验: 因子模型中添加注意力冲击的边际贡献 (预期 < 0.1%)

---

## Phase 3: BNPW VAR 方差分解

### 新建文件: `27_var_decomposition.py`

#### 输入
- 银行日度收益率
- 市场指数日度收益率
- 日度成交量 / 订单流数据 (可选)

#### 输出
- `data_processed/27_var_decomposition.parquet` (Bank-Year × 4 方差分量)

#### 任务清单

- [ ] **3a. VAR 系统设定**
  - 变量: [收益率, 订单流代理, 公开信息代理]
  - 阶数: 5 (或 AIC/BIC 自动选择)
  - 估计单位: 每只银行股票每年度单独估计

- [ ] **3b. 结构分解 (Cholesky)**
  - 从 VAR 残差协方差矩阵提取 4 个方差分量:
    - MktInfo: 市场层面信息驱动的方差
    - PrivateInfo: 私有信息驱动的方差
    - PublicInfo: 公开信息驱动的方差
    - Noise: 噪声交易驱动的方差
  - 参考: Brogaard, Nguyen, Putnins & Wu (2022, RFS)

- [ ] **3c. 年度聚合 + 截面标准化**
  - 日度方差 → 年度方差 (直接求和)
  - 使用现有 43_panel z-score 流程标准化

- [ ] **3d. Narrative Exposure 与方差分量关系**
  - 截面回归: IdVar ~ NarrExp + Controls
  - 预期: NarrExp 解释 IdVar 的截面 R² > 80% (论文 86%)
  - 分通道回归: 各方差分量对 NarrExp 的敏感度排序

---

## Phase 4: 面板集成与导出

### 修改文件: `43_panel_indicators_geography.py` + `45_panel_export_main.py`

#### 任务清单

- [ ] **4a. 合并 Narrative Exposure 到面板**
  - 在 `compute_composite_indicators()` 后新增合并步骤
  - 从 `26_narrative_exposure.parquet` 读取, 通过 (target_bank, year) 左连接
  - 生成 `narrative_exposure` 列

- [ ] **4b. 合并 VAR 方差分量到面板**
  - 从 `27_var_decomposition.parquet` 读取
  - 生成 `mkt_info_var`, `private_info_var`, `public_info_var`, `noise_var` 四列

- [ ] **4c. 升级 fintech_exposure**
  - 保留原有 `fintech_exposure` (作为简化代理)
  - 新增 `narrative_exposure` (论文原始定义)
  - 在 z-score 白名单中添加新变量

- [ ] **4d. Stata 标签扩展**
  - 在 `45_panel_export_main.py` 的 `STATA_LABELS` 中添加:
    ```python
    'narrative_exposure':     'Narrative Exposure (Dim et al. 2024)',
    'mkt_info_var':           'Market Info Variance (BNPW)',
    'private_info_var':       'Private Info Variance (BNPW)',
    'public_info_var':        'Public Info Variance (BNPW)',
    'noise_var':              'Noise Variance (BNPW)',
    'narrative_exposure_z':   'Narrative Exposure Z-scored',
    ```

- [ ] **4e. 导出验证**
  - 检查 Parquet + Stata .dta 的新变量完整性
  - 确认 Stata 变量名 ≤ 32 字符

---

## Phase 5: 稳健性检验与扩展

### 修改文件: `51_falsification_test.py` (扩展)

#### 任务清单

- [ ] **5a. NBER 衰退期敏感性 (对标论文 Table 2 底部)**
  - 定义高叙事曝露期: 年度 NarrExp 截面均值 > 样本均值
  - 在 Fama-MacBeth 第二阶段加入高曝露哑变量
  - 输出 Stata 模板

- [ ] **5b. 单话题 Exposure 分组回归 (对标论文 Table OC5)**
  - 将 K 个话题分为 ~12 组 (按内容语义聚类)
  - 对每组单独计算 NarrExp 并运行 Eq. 4
  - 验证: 各组均应 b₂ < 0

- [ ] **5c. 准自然实验: 百分位跃升 DiD (对标论文 Tables 3-4)**
  - 处理变量: NarrExp 百分位排名年度跃升 ≥ 25pp
  - 匹配策略: 使用现有 Bartik IV 体系的 PSM 得分
  - DiD 估计: 利用 44 模块的 Callaway & Sant'Anna 框架

- [ ] **5d. NLP5 因子替代检验 (对标论文 Table OC6)**
  - 用 BKS (2023) NLP5 因子替代 Carhart 四因子
  - 重新估计 Narrative Exposure
  - 验证主要结果的稳健性

- [ ] **5e. Stata 回归模板输出**
  - Eq. 4 Fama-MacBeth 两阶段回归模板
  - 方差分量 × NarrExp 交互回归模板
  - Turnover 回归模板

---

## 验证计划

### 自动化验证

```bash
# 1. LDA 模型质量
python 25_topic_lda.py --validate
#   → 检查 perplexity, coherence, 话题间相关性

# 2. Narrative Exposure 诊断
python 26_narrative_exposure.py --diagnostics
#   → 相关性矩阵, 分组分布图, 增量 R² 检验

# 3. 面板完整性
python 45_panel_export_main.py
#   → 检查新变量非空率, z-score 校验
```

### 人工验证

| 检验项 | 预期结果 | 对标 |
|--------|----------|------|
| NarrExp vs fintech_exposure 相关性 | \|r\| < 0.3 | 论文 §2.4 |
| NarrExp 解释 IdVar 截面 R² | > 70% | 论文 86% |
| 增量 R² (因子模型 + 注意力冲击) | < 0.5% | 论文 < 0.1% |
| b₂ 符号 (Eq. 4 交互项) | 显著为负 | 论文 Table 2 |
| 小银行 NarrExp > 大银行 | 单调递减 | 论文 Figure 1B |

---

## 时间与资源估算

| Phase | 预估工时 | 阻塞依赖 |
|-------|---------|----------|
| Phase 1 (LDA) | 3-5 天 | 无 (语料已有) |
| Phase 2 (Exposure) | 5-7 天 | ⚠️ 银行日度收益率数据 |
| Phase 3 (VAR) | 5-7 天 | ⚠️ 市场微观结构数据 |
| Phase 4 (集成) | 1-2 天 | Phase 1-3 完成 |
| Phase 5 (稳健性) | 3-5 天 | Phase 4 完成 |
| **合计** | **17-26 天** | |

---

## 关键风险

> [!CAUTION]
> 1. **数据可得性**: 银行日度收益率和因子模型数据是 Phase 2-3 的硬依赖, 如不可得则需寻找替代方案 (如使用行业指数代理)
> 2. **中文 LDA 质量**: 中文分词质量直接影响 LDA 话题的可解释性, 可能需要多轮人工审查和参数调优
> 3. **样本量**: 中国上市银行数量 (~40 家) 远少于论文的美股样本 (~4000 家), 截面回归的统计功效可能不足
> 4. **话题数差异**: 中文金融新闻的话题结构可能与英文 WSJ 不同, 最优话题数 K 需独立确定
