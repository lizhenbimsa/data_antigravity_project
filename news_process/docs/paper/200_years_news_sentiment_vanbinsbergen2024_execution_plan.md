# 文件二：项目重构与优化执行计划书

**关联文件**：文件一《基于 van Binsbergen et al. (2024) 的项目分析与诊断报告》

---

## 1. 优先级排布

### 速赢项（Quick Wins）——1-3天内完成

| 序号 | 任务 | 预期收益 | 实施成本 |
|------|------|---------|---------|
| QW-1 | 在 `43_panel_indicators_geography.py` 中新增跨银行情感离散度(Dispersion)计算 | 新增与水平情感正交的预测维度，直接对标论文 Table 4 | 极低(groupby + std, ~30行代码) |
| QW-2 | 在 `43_panel_indicators_geography.py` 的标准化白名单中注册新变量 | 确保新指标进入 Fama-MacBeth 标准化流程 | 极低(添加变量名到列表) |
| QW-3 | 更新 `45_panel_export_main.py` 中 `STATA_LABELS` 添加新变量标签 | Stata回归模板可直接引用新变量 | 极低 |

### 核心攻坚项——1-2周

| 序号 | 任务 | 预期收益 | 实施成本 |
|------|------|---------|---------|
| CA-1 | Current vs. Future 情感分解：按 `forward_looking_ratio` 阈值将文章分两组分别聚合 | 释放前瞻性情感的独立预测力，直接对标论文 Table 7 的核心发现 | 中(需在41模块聚合逻辑中新增分支) |
| CA-2 | 情感正交化去偏：构建"非金融科技情感"并在面板中实施 OLS 残差正交化 | 消除媒体环境趋势污染，提升情感系数的因果可信度 | 中(需确定非FT情感数据来源后实施) |
| CA-3 | Stata 回归模板重构：新增正交化情感、分解情感、离散度的完整回归规格 | 直接产出可发表的实证结果 | 低(仅更新do-file模板) |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：情感离散度与分解（第1周）

#### 动作1.1：跨银行情感离散度计算 [QW-1]

**指令**：

1. 打开 `43_panel_indicators_geography.py`
2. 在 `compute_composite_indicators()` 函数末尾（约 L161 前）新增以下逻辑：

```python
def compute_sentiment_dispersion(panel: pd.DataFrame) -> pd.DataFrame:
    """步骤 7e: 跨银行情感离散度 (van Binsbergen et al. 2024, NBER 32026).

    学术依据:
      van Binsbergen, J.H., Bryzgalova, S., Mukhopadhyay, M. & Sharma, V.
      (2024). (Almost) 200 Years of News-Based Economic Sentiment.
      NBER Working Paper No. 32026. Table 4.
      → 跨截面情感离散度(Dispersion)负向预测GDP增长
      → 捕捉信息不确定性/异质信念维度

    三层离散度:
      1. 全行业级: 所有银行在年度t的情感截面标准差
      2. 银行类型级: 同类型银行(国有/股份/城商/农商等)在年度t的标准差
      3. 省份级: 同省银行在年度t的标准差

    新增列:
      industry_dispersion_full/ctx  — 全行业情感离散度
      type_dispersion_full/ctx      — 银行类型内离散度
      prov_dispersion_full/ctx      — 省份内离散度
    """
    logger.info("=" * 60)
    logger.info("步骤 7e: 跨银行情感离散度 (van Binsbergen et al. 2024)")
    logger.info("=" * 60)

    has_news = panel['n_articles'] > 0

    for track in ['_full', '_ctx']:
        tone_col = f'llm_vote_tone{track}'
        if tone_col not in panel.columns:
            continue

        # --- 全行业级离散度 ---
        out_col = f'industry_dispersion{track}'
        yearly_std = panel[has_news].groupby('year')[tone_col].transform('std')
        panel[out_col] = np.nan
        panel.loc[has_news, out_col] = yearly_std
        valid = panel[out_col].dropna()
        logger.info(f"  {out_col}: mean={valid.mean():.4f}, "
                    f"std={valid.std():.4f}, 非空={len(valid):,}")

        # --- 银行类型级离散度 ---
        if 'bank_type' in panel.columns:
            out_col = f'type_dispersion{track}'
            type_std = panel[has_news].groupby(
                ['bank_type', 'year']
            )[tone_col].transform('std')
            panel[out_col] = np.nan
            panel.loc[has_news, out_col] = type_std
            valid = panel[out_col].dropna()
            logger.info(f"  {out_col}: mean={valid.mean():.4f}, "
                        f"std={valid.std():.4f}, 非空={len(valid):,}")

        # --- 省份级离散度 ---
        if 'bank_province' in panel.columns:
            mask = has_news & (panel['bank_province'] != '')
            out_col = f'prov_dispersion{track}'
            prov_std = panel[mask].groupby(
                ['bank_province', 'year']
            )[tone_col].transform('std')
            panel[out_col] = np.nan
            panel.loc[mask, out_col] = prov_std
            valid = panel[out_col].dropna()
            logger.info(f"  {out_col}: mean={valid.mean():.4f}, "
                        f"std={valid.std():.4f}, 非空={len(valid):,}")

    return panel
```

3. 在 `45_panel_export_main.py` 的 main() 流程中，`compute_composite_indicators()` 之后、`standardize_panel_variables()` 之前调用此函数。

**交付物标准**：
- 6个新列(`industry_dispersion_full/ctx`, `type_dispersion_full/ctx`, `prov_dispersion_full/ctx`)成功生成
- `industry_dispersion_full` 的年际变化应与宏观经济不确定性事件(如2020年疫情)呈正相关
- 日志中打印描述性统计

#### 动作1.2：Current vs. Future 情感分解 [CA-1]

**指令**：

1. 在 `41_panel_encode_aggregate.py` 的 `aggregate_panel()` 函数中，新增基于 `forward_looking_ratio` 的文章分组聚合逻辑：

```python
# --- K. Current vs. Future 情感分解 (van Binsbergen et al. 2024, Table 7) ---
# 学术依据:
#   论文核心发现: 所有GDP预测力集中在前瞻性(Future)情感成分,
#   回顾性(Current)成分无显著预测力。
#   将此发现迁移至银行面板: 前瞻性金融科技报道的情感应比
#   回顾性报道更强地预测银行未来绩效。
#
# 实现: 以 forward_looking_ratio 的年度中位数为阈值,
#   将文章分为"前瞻导向"和"回顾导向"两组,
#   分别计算 Bank-Year 情感均值。

for track in ['_full', '_ctx']:
    fl_col = f'forward_looking_ratio{track}'
    if fl_col not in df.columns:
        continue

    # 年度中位数阈值 (避免硬编码)
    yearly_median = df.groupby('year')[fl_col].transform('median')
    df[f'is_future_oriented{track}'] = (df[fl_col] > yearly_median).astype(int)

    # 前瞻性子集聚合
    future_df = df[df[f'is_future_oriented{track}'] == 1]
    if not future_df.empty:
        future_agg = {}
        for short in LLM_MODELS:
            src = f'{short}_score{track}'
            if src in future_df.columns:
                future_agg[f'{short}_tone_future{track}'] = (src, 'mean')
        future_agg[f'llm_vote_tone_future{track}'] = (f'llm_vote_score{track}', 'mean')
        future_agg[f'n_articles_future{track}'] = (f'llm_vote_score{track}', 'count')

        future_panel = future_df.groupby(
            ['target_bank', 'year']
        ).agg(**future_agg).reset_index()
        panel = panel.merge(future_panel, on=['target_bank', 'year'], how='left')

    # 回顾性子集聚合
    current_df = df[df[f'is_future_oriented{track}'] == 0]
    if not current_df.empty:
        current_agg = {}
        current_agg[f'llm_vote_tone_current{track}'] = (f'llm_vote_score{track}', 'mean')
        current_agg[f'n_articles_current{track}'] = (f'llm_vote_score{track}', 'count')

        current_panel = current_df.groupby(
            ['target_bank', 'year']
        ).agg(**current_agg).reset_index()
        panel = panel.merge(current_panel, on=['target_bank', 'year'], how='left')

    logger.info(f"  Current/Future 情感分解{track}: "
                f"Future文章 {len(future_df):,}, "
                f"Current文章 {len(current_df):,}")
```

2. 在 `balance_panel()` 的计数类零填充列表中追加 `n_articles_future_full/ctx` 和 `n_articles_current_full/ctx`。

**交付物标准**：
- `llm_vote_tone_future_full`, `llm_vote_tone_current_full` (及ctx对应列)成功生成
- Future/Current 文章分布比例应约为 50/50 (中位数分割)
- 两组情感的相关系数应低于0.9 (确保非冗余)

#### 动作1.3：标准化白名单与标签注册 [QW-2, QW-3]

**指令**：

1. 在 `43_panel_indicators_geography.py` 的 `_STANDARDIZE_COLS` 列表中追加：

```python
# van Binsbergen et al. (2024) 新增指标
'industry_dispersion_{t}',
'type_dispersion_{t}',
'prov_dispersion_{t}',
'llm_vote_tone_future_{t}',
'llm_vote_tone_current_{t}',
```

2. 在 `45_panel_export_main.py` 的 `STATA_LABELS` 中追加：

```python
# --- van Binsbergen et al. (2024, NBER 32026) ---
'industry_dispersion_full':    'Sentiment Dispersion (Industry, Full)',
'industry_dispersion_ctx':     'Sentiment Dispersion (Industry, Ctx)',
'type_dispersion_full':        'Sentiment Dispersion (Bank Type, Full)',
'type_dispersion_ctx':         'Sentiment Dispersion (Bank Type, Ctx)',
'prov_dispersion_full':        'Sentiment Dispersion (Province, Full)',
'prov_dispersion_ctx':         'Sentiment Dispersion (Province, Ctx)',
'llm_vote_tone_future_full':   'Future-Oriented Sentiment (Full)',
'llm_vote_tone_future_ctx':    'Future-Oriented Sentiment (Ctx)',
'llm_vote_tone_current_full':  'Current-Event Sentiment (Full)',
'llm_vote_tone_current_ctx':   'Current-Event Sentiment (Ctx)',
'n_articles_future_full':      'N Articles Future-Oriented (Full)',
'n_articles_current_full':     'N Articles Current-Event (Full)',
'net_ft_tone_full':            'Net FinTech Sentiment Orthogonalized (Full)',
'net_ft_tone_ctx':             'Net FinTech Sentiment Orthogonalized (Ctx)',
```

**交付物标准**：
- 所有新变量在 `_z` 标准化列中出现
- Stata .dta 导出文件中包含正确的变量标签

---

### 阶段二：情感正交化与实证检验（第2周）

#### 动作2.1：非金融科技情感构建与正交化 [CA-2]

**指令**：

1. **数据来源选择**（推荐路径B）：

   如果项目数据库中存储了被 `11_news_bank.py` 匹配到银行但**不含金融科技关键词**的新闻，可直接使用这些"非FT新闻"的情感均值。

   如果不存在此类数据，使用**行业级年度均值去均值化**作为替代：

   ```python
   # 在 43 模块中新增
   def compute_orthogonalized_sentiment(panel: pd.DataFrame) -> pd.DataFrame:
       """步骤 7f: 情感正交化 (van Binsbergen et al. 2024, Section III.1).

       实现路径B: 在面板回归中直接通过行业年度均值去均值化
       实现近似正交化效果。

       公式:
         net_ft_tone_{i,t} = llm_vote_tone_{i,t} - mean(llm_vote_tone_{*,t})

       此方法去除了年度全行业共同情感趋势(类比论文的non-economic
       sentiment), 保留银行特异性信息。

       注意: 这不是完整的OLS正交化(论文是对非经济情感做回归取残差),
       而是一个更简洁的实现。完整版需要非FT新闻数据。
       """
       logger.info("=" * 60)
       logger.info("步骤 7f: 情感正交化 (van Binsbergen et al. 2024)")
       logger.info("=" * 60)

       has_news = panel['n_articles'] > 0

       for track in ['_full', '_ctx']:
           tone_col = f'llm_vote_tone{track}'
           out_col = f'net_ft_tone{track}'

           if tone_col not in panel.columns:
               continue

           # 年度行业均值
           yearly_mean = panel[has_news].groupby('year')[tone_col].transform('mean')

           panel[out_col] = np.nan
           panel.loc[has_news, out_col] = (
               panel.loc[has_news, tone_col] - yearly_mean
           )

           valid = panel[out_col].dropna()
           # 校验: 正交化后年度均值应≈0
           yearly_check = panel[has_news].groupby('year')[out_col].mean()
           max_deviation = yearly_check.abs().max()
           logger.info(f"  {out_col}: mean={valid.mean():.6f}, "
                       f"std={valid.std():.4f}, "
                       f"年均值最大偏差={max_deviation:.6f} "
                       f"{'✓' if max_deviation < 1e-10 else '⚠️'}")

       return panel
   ```

2. 在 `45_panel_export_main.py` 的 main() 中，`compute_sentiment_dispersion()` 之后调用。

**交付物标准**：
- `net_ft_tone_full/ctx` 成功生成且年度均值 < 1e-10
- `net_ft_tone` 与 `llm_vote_tone` 的相关系数应高于 0.85 (仅去除趋势，保留银行间差异)
- `net_ft_tone` 与年度虚拟变量的相关系数应接近 0 (趋势已去除)

#### 动作2.2：Stata 回归模板重构 [CA-3]

**指令**：更新 Stata do-file 模板，新增以下三组回归规格：

```stata
* ===== 组1: 情感正交化检验 (van Binsbergen et al. 2024, Table A3 概念迁移) =====
* 基准: 原始情感
reghdfe Y llm_vote_tone_full_z Controls, ///
    absorb(target_bank year) vce(cluster target_bank)
est store m_raw

* 正交化情感 (行业去均值化)
reghdfe Y net_ft_tone_full_z Controls, ///
    absorb(target_bank year) vce(cluster target_bank)
est store m_orth

* 对比: 系数和显著性应保持一致(仅去除共同趋势)
esttab m_raw m_orth, se star(* 0.10 ** 0.05 *** 0.01) ///
    title("Orthogonalization Robustness Check")


* ===== 组2: Current vs. Future 分解 (van Binsbergen et al. 2024, Table 7) =====
* 同时放入 Future + Current 情感
reghdfe Y llm_vote_tone_future_full_z llm_vote_tone_current_full_z Controls, ///
    absorb(target_bank year) vce(cluster target_bank)

* 预期: future_tone 系数显著, current_tone 系数不显著或小得多
* 这将验证"前瞻性信号驱动预测力"的核心假说


* ===== 组3: 情感离散度预测 (van Binsbergen et al. 2024, Table 4) =====
* 在银行类型层级检验: 组内情感越分散, 银行表现越差?
reghdfe Y llm_vote_tone_full_z type_dispersion_full_z Controls, ///
    absorb(target_bank year) vce(cluster target_bank)

* 预期: type_dispersion 系数为负(信息不确定性→负面影响)
* 与论文发现一致: 跨截面离散度负向预测宏观增长
```

**交付物标准**：
- 组1: `net_ft_tone` 系数与 `llm_vote_tone` 系数方向一致，量级相当
- 组2: `future_tone` 系数绝对值 > `current_tone` 系数绝对值
- 组3: `type_dispersion` 系数为负(p < 0.10)

---

### 阶段三：结论重构与文档更新（第2周后半）

#### 动作3.1：论文贡献重述

**指令**：在研究论文的方法论部分增加以下段落：

> 为确保情感度量的信息纯度，我们借鉴 van Binsbergen et al. (2024) 的正交化策略，将银行级金融科技情感对行业年度均值情感进行去均值化处理，获得"净金融科技情感"(Net FinTech Sentiment)。该操作去除了年度共同的媒体环境趋势（如舆论管控变化、行业热点周期），使残差仅反映银行特异性的情感信号。

> 此外，受论文中"Current vs. Future"情感分解启发，我们利用前瞻性陈述比率(forward-looking ratio)将每篇金融科技新闻按其时间导向分类，分别构建"前瞻性情感"和"回顾性情感"两个子指标。论文发现GDP预测力完全集中在前瞻性成分，我们在银行面板中对此进行了独立验证。

#### 动作3.2：项目技术手册更新

**指令**：在 `Project_Technical_Manual.md` 的相关阶段描述中补充：

1. 步骤 7e: 跨银行情感离散度 → 引用 van Binsbergen et al. (2024, Table 4)
2. 步骤 7f: 情感正交化 → 引用 van Binsbergen et al. (2024, Section III.1)
3. 聚合中新增 Current/Future 分解 → 引用 van Binsbergen et al. (2024, Table 7)

---

## 3. 风险预案 (Plan B)

### 风险1：非金融科技新闻数据不可得

**卡点原因**：如果项目的新闻采集范围严格限于金融科技关键词匹配的文章，则无法获取"同媒体/同银行的非FT新闻"作为正交化基准。

**Plan B（已内置于动作2.1）**：
- 使用**行业年度均值去均值化**替代完整OLS正交化
- 该方法在经济学含义上等价于在回归中加入年度固定效应——但优势在于产出一个显式的"净情感"变量可用于后续分析
- 极端兜底: 在Stata回归中直接加入 `year` 固定效应(absorb(year))已经隐式实现了这一功能

### 风险2：forward_looking_ratio 中位数分割导致 Future/Current 组不稳定

**卡点原因**：如果大部分金融科技新闻的前瞻性比率集中在一个窄区间，中位数分割可能导致分组不稳定（对阈值微小变化敏感）。

**Plan B**：
- 改用**三分位分割**: 取前瞻性比率的P33和P67，分为"明确前瞻"/"混合"/"明确回顾"三组，仅对比两个极端组
- 或使用**连续交互项**: 不做硬分割，而是在回归中加入 `tone × forward_looking_ratio` 交互项，测试前瞻性比率的调节效应

### 风险3：情感离散度变异不足

**卡点原因**：如果同类型/同省份银行数量太少（如外资银行仅3-5家），groupby后std的估计不可靠。

**Plan B**：
- 对组内银行数 < 5 的观测将离散度设为 NaN
- 或仅保留全行业级离散度(`industry_dispersion`)，这是最稳健的变量（基于所有银行计算）
- 或使用 **MAD (Median Absolute Deviation)** 替代标准差，对极端值更稳健

### 风险4：正交化后情感系数反而不显著

**卡点原因**：如果年度固定效应已经充分吸收了行业趋势，`net_ft_tone` 和 `llm_vote_tone` 在包含`absorb(year)`的回归中完全等价，正交化无增量贡献。

**Plan B**：
- 这不是"失败"而是"好消息"——说明现有回归设计（含年度FE）已隐式完成了去偏
- 在论文中可这样表述: "我们验证了在控制年度固定效应后, 情感正交化不改变核心系数, 说明本文的年度FE设计已充分吸收了媒体环境趋势"
- 转而强调 Current vs. Future 分解和 Dispersion 作为主要增量贡献

---

## 4. 校验矩阵

| 检查项 | 验证方法 | 预期结果 |
|--------|---------|---------|
| 离散度变量生成 | `panel['industry_dispersion_full'].describe()` | std > 0, mean > 0 |
| 离散度与宏观事件一致性 | 按年度绘图对比 | 2020年(疫情)离散度应最高 |
| Current/Future分组平衡 | `n_articles_future / n_articles` | 约40%-60% |
| Future/Current情感相关性 | `corr(future_tone, current_tone)` | < 0.90 |
| 正交化校验 | `panel.groupby('year')['net_ft_tone'].mean()` | ≈ 0 |
| Stata回归: Future vs Current | `future_tone` 系数 vs `current_tone` 系数 | Future > Current |
| Stata回归: Dispersion | `type_dispersion` 系数符号 | 负号(p < 0.10) |
