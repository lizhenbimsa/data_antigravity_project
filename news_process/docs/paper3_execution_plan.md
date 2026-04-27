# 文件二：项目重构与优化执行计划书

**关联文件**：文件一《基于参考论文的项目分析与诊断报告》

---

## 1. 优先级排布

### 速赢项（Quick Wins）——1-3天内完成

| 序号 | 任务 | 预期收益 | 实施成本 |
|------|------|---------|---------|
| QW-1 | Bartik IV 精简：在 `45_panel_export_main.py` 中注释/删除稳健性9-28的代码 | 消除弱IV嫌疑、减少运行时间约40% | 极低(仅删代码) |
| QW-2 | 在 `43_panel_indicators_geography.py` 中为现有 LOO 指标新增 "同类型银行LOO" 分组维度 | 得到 `peer_type_leave1out_tone`，可直接作为核心自变量初步测试 | 低(复用现有LOO基础设施) |
| QW-3 | 更新 Stata 变量标签映射 (`STATA_LABELS`)，删除被精简维度的标签 | 保持导出文件一致性 | 极低 |

### 核心攻坚项——2-4周

| 序号 | 任务 | 预期收益 | 实施成本 |
|------|------|---------|---------|
| CA-1 | 新建 `21b_news_classification.py`：利用LLM将新闻分为实质性/描述性二分类 | 核心方法论突破——解决"情感纯度"问题 | 高(需设计prompt、标注验证集、验证准确率) |
| CA-2 | 新建 Washing Index 计算逻辑(在41或43模块中) | 替代粗放的 `llm_vote_tone` 作为精炼代理变量 | 中(公式简明，但需handle分类后数据流) |
| CA-3 | 构建 `Peer_Washing_LOO` 核心解释变量 | 实现"负外部性"叙事，升维研究贡献 | 中(依赖CA-2输出) |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：机制重塑与数据清洗（第1-2周）

#### 动作1.1：Bartik IV 精简 [QW-1, QW-3]

**指令**：

1. 打开 `45_panel_export_main.py`
2. 定位 "稳健性 9" 至 "稳健性 28" 的代码块(约 L739-L1000)
3. 将这些Bartik IV构建代码块包裹在 `if PANEL_CFG.get('compute_extra_bartik', False):` 条件中(而非直接删除，保留回退能力)
4. 在 `config.yaml` 的 `panel_building` 下新增 `compute_extra_bartik: false`
5. 同步清理 `STATA_LABELS` 中对应的变量标签(可保留注释)

**交付物标准**：
- 面板导出运行时间减少30%以上
- Stata .dta 文件中仅包含8套Bartik IV的相关列
- 日志中明确记录"Extra Bartik IV disabled by config"

#### 动作1.2：新闻文本分类模块 [CA-1]

**指令**：

1. 在 `news_process/` 下创建 `21b_news_classification.py`
2. 设计分类Prompt(参考蔡真等表1的分类规则，迁移至银行金融科技语境)：

```
分类规则（银行金融科技新闻版本）：

实质性报道 (标记=2)：
- 含可验证的定量信息：交易额、用户数、不良率变化、产品发版号、监管批文编号
- 明确的产品名称+已上线/已部署的状态描述
- 第三方认证/评级/获奖(具体颁奖机构和名称)

描述性报道 (标记=1)：
- 战略愿景/理念表述："将大力推进"/"致力于打造"/"全面拥抱"
- 合作意向/框架协议(无具体执行细节)
- 行业趋势解读(主语非该银行具体行为)
- 前瞻性规划(无具体时间表和量化目标)

非金融科技相关 (标记=0)：
- 关键词在特定语境下非金融科技含义
```

3. 对每篇新闻调用LLM进行二分类，输出列 `news_substance_type`
4. 使用人工抽样200篇验证准确率(目标: >85%)
5. 输出追加到现有 `21_tone_llms.py` 的输出文件或独立Parquet

**交付物标准**：
- 分类准确率 > 85%(200篇人工验证)
- 输出包含 `news_substance_type` 列(0/1/2)
- 类别分布统计写入日志(预期：实质性30-50%，描述性50-70%)

#### 动作1.3：Washing Index 公式实现 [CA-2]

**指令**：

1. 在 `43_panel_indicators_geography.py` 中新增函数 `compute_washing_index(panel, df_exploded)`
2. 实现公式：

```python
def compute_washing_index(panel, df_exploded):
    """
    Washing_Score_{i,t} = Max(0, Desc_Tone_{i,t} - Median(Desc_Tone_{type,t}))
    
    其中:
    - Desc_Tone_{i,t} = 银行i在年份t的描述性报道(news_substance_type==1)
                         的 llm_vote_tone 均值
    - Median(Desc_Tone_{type,t}) = 同类型银行在年份t的描述性报道语调中位数
    """
    # Step 1: 筛选描述性报道
    desc = df_exploded[df_exploded['news_substance_type'] == 1]
    
    # Step 2: 计算银行级描述性报道语调均值
    desc_tone = desc.groupby(['target_bank', 'year'])['llm_vote_score_full'].mean()
    desc_tone.name = 'desc_tone'
    
    # Step 3: 合并银行类型
    panel = panel.merge(desc_tone, on=['target_bank', 'year'], how='left')
    
    # Step 4: 计算年度-类型中位数
    type_median = panel.groupby(['bank_type', 'year'])['desc_tone'].transform('median')
    
    # Step 5: 异常语调 = Max(0, 个体 - 中位数)
    panel['washing_score'] = (panel['desc_tone'] - type_median).clip(lower=0)
    
    return panel
```

3. 在 `45_panel_export_main.py` 的 main() 中，在 `compute_composite_indicators()` 之后调用此函数

**交付物标准**：
- `washing_score` 列成功生成且分布合理(均值应 > 0 但 < 0.1，std约0.03-0.08)
- 描述性统计写入日志

---

### 阶段二：实证模型重构与检验（第2-3周）

#### 动作2.1：同群传染效应变量构建 [CA-3]

**指令**：

1. 在 `43_panel_indicators_geography.py` 的 `compute_leave_one_out_sentiment()` 之后新增函数：

```python
def compute_peer_washing_loo(panel):
    """
    构建同类型/同省份银行的LOO平均Washing Score
    
    Peer_Washing_Type_{i,t} = mean(Washing_Score_{j,t}) for j in same_type, j != i
    Peer_Washing_Prov_{i,t} = mean(Washing_Score_{j,t}) for j in same_province, j != i
    """
    for group_col, prefix in [('bank_type', 'type'), ('bank_province', 'prov')]:
        # 组级聚合
        group_agg = panel.groupby([group_col, 'year'])['washing_score'].agg(['sum', 'count'])
        
        # merge回面板
        panel = panel.merge(group_agg, on=[group_col, 'year'], how='left', suffixes=('', f'_{prefix}_grp'))
        
        # LOO: (组和 - 自身) / (组数 - 1)
        remain_sum = panel[f'sum'] - panel['washing_score'].fillna(0)
        remain_cnt = panel[f'count'] - 1
        panel[f'peer_washing_{prefix}'] = np.where(
            remain_cnt > 0,
            remain_sum / remain_cnt,
            np.nan
        )
        panel = panel.drop(columns=['sum', 'count'])
    
    return panel
```

2. 在 `STATA_LABELS` 中添加：

```python
'washing_score':           'Bank Washing Score (Desc-Tone Excess)',
'peer_washing_type':       'Peer Washing LOO (Same Bank Type)',
'peer_washing_prov':       'Peer Washing LOO (Same Province)',
```

**交付物标准**：
- `peer_washing_type` 和 `peer_washing_prov` 两列均成功生成
- LOO校验：任意单银行被移除后，组均值应发生变化(选3个银行抽查)
- 变量间相关系数矩阵写入日志

#### 动作2.2：Stata 回归模板重构

**指令**：更新 Stata do-file 模板，新增以下回归规格：

```stata
* ===== 核心回归: 同群粉饰 -> 自身表现 =====
* 基准回归
reghdfe Y peer_washing_type L.washing_score Controls, ///
    absorb(target_bank year) vce(cluster target_bank)

* 替换分组维度 (省份)
reghdfe Y peer_washing_prov L.washing_score Controls, ///
    absorb(target_bank year) vce(cluster bank_province)

* IV: 使用 Bartik TYPE IV 工具化 peer_washing
ivreghdfe Y (peer_washing_type = bartik_type_iv_full) Controls, ///
    absorb(target_bank year) first vce(cluster target_bank)
```

**交付物标准**：
- 一阶F统计量 > 10 (Stock-Yogo threshold)
- 核心系数 `peer_washing_type` 显著为负(预期: p < 0.05)，方向符合"同群传染挤出"假说

---

### 阶段三：结论重构（第3-4周）

#### 动作3.1：机制检验

**指令**：参照论文双渠道机制，设计对应的银行业版本：

| 论文机制 | 银行业等价 | 被解释变量候选 |
|---------|-----------|--------------|
| 产品市场: 市场势力 | 银行市场份额 | 存贷款市场份额 |
| 产品市场: 营销难度 | 获客成本 | 存款增长率 |
| 产品市场: 盈利能力 | ROA/ROE | 净息差 |
| 资金市场: 融资能力 | 同业融资 | 同业负债占比 |
| 资金市场: 监管资源 | 补贴/试点资格 | 是否获批试点 |

#### 动作3.2：异质性分析

**指令**：参照论文三维异质性(市场份额/社会责任/财务风险)，设计银行业版本的调节效应：

```stata
* 按银行规模分组
reghdfe Y c.peer_washing_type##c.bank_assets Controls, ///
    absorb(target_bank year) vce(cluster target_bank)

* 按信息透明度分组 (分析师覆盖 = 研报数量)
reghdfe Y c.peer_washing_type##c.analyst_coverage Controls, ///
    absorb(target_bank year) vce(cluster target_bank)
```

**交付物标准**：
- 大银行的peer_washing系数绝对值应更大(劣币驱逐良币效应更显著)
- 分析师覆盖高的银行，peer_washing系数减弱(信息透明度缓解逆向选择)

---

## 3. 风险预案 (Plan B)

### 风险1：LLM分类准确率不达标 (< 80%)

**卡点原因**：银行金融科技新闻边界模糊，实质性/描述性区分难度大于上市公司年报MDA。

**Plan B**：
- ~~放弃三分类，改用二分类~~ **已采纳**：当前即为二分类（实质性 vs 描述性）
- 或使用**连续打分**(0-10分实质性程度)替代硬分类
- 极端情况: 直接使用已有的 `forward_looking_ratio` 作为"描述性程度"的代理(前瞻性比率越高，描述性成分越大)，无需额外分类模块

### 风险2：Washing Index 变异不足

**卡点原因**：银行样本量(约100-200家)远小于上市公司(36000+)，行业中位数可能不稳定。

**Plan B**：
- 将分组维度从"银行类型"放宽至"全体银行"(去掉分类维度)
- 或使用年度均值替代中位数(均值对极端值更敏感，可能产生更大变异)
- 或使用年度P60/P70分位数替代中位数(提高"漂绿门槛")

### 风险3：Peer Washing LOO 组内样本过少

**卡点原因**：某些银行类型(如"民营银行"、"外资法人银行")可能仅有3-5家，LOO后几乎没有有效观测。

**Plan B**：
- 合并稀疏类型：民营+外资归入"其他"
- 或使用省份维度的LOO替代类型维度
- 或使用 Bartik Shift-Share 结构(基期份额 x 组别冲击)替代简单LOO，借助跨组暴露增加有效变异

### 风险4：一阶F统计量低于10 (弱工具变量)

**卡点原因**：Bartik IV 的 shift-share 结构对基期份额的稳定性敏感。

**Plan B**：
- 使用 Anderson-Rubin 弱IV稳健推断
- 或使用 LIML 替代 2SLS
- 或放弃IV识别，转向 Oster (2019, JBES) 的有界分析(coefficient stability test)
