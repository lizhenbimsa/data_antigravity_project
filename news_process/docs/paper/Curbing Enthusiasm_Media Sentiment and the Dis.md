# 基于《Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements》的项目诊断与执行计划

> **参考论文**: Holzman, E.R., Miller, B.P. & Twedt, B.J. (2023). "Curbing Enthusiasm: Media Sentiment and the Disciplining Role of Quarterly Earnings Announcements." *The Accounting Review*, 98(4), 261–286.
>
> **审计范围**: `F:\WiseSearch\data_antigravity_project\news_process` 全管线
>
> **审计日期**: 2026-04-06

---

## 第一部分：基于参考论文的项目分析与诊断报告

### 1. 范式映射与盲区诊断

**论文核心机制（三层递进）**：

论文揭示了一个完整的"媒体情感→短期错误定价→财务报告纠偏"因果链：

| 层级 | 机制 | 论文核心测度 | 关键创新 |
|------|------|------------|---------|
| **第一层：情感测量** | 媒体对公司的季度情感累积 | `Unweight Media Sent`、`Outlet Impact Media Sent`、`Article Uniqueness Media Sent`、`Outlet & Article Wgt Media Sent` | ①媒体影响力通过**滚动季度换手率固定效应回归**动态估计Outlet Impact权重（Appendix A, eq.(a)）；②文章新颖度通过RavenPack `G_ENS`评分实现指数衰减 |
| **第二层：正交化情感驱动收益** | 剥离风险因子和基本面信息后，纯粹由媒体情感驱动的季度股票收益 | `Qtrly Returns - Media Sent Driven` | 通过**滚动年度回归**（Appendix A, eq.(b)），在控制Fama-French-Carhart四因子、分析师预测修正、新闻稿情感、8-K后，提取β₁系数——媒体情感对日收益的边际弹性。最终测度 = Σ(β̂₁ × daily_media_sent) over [-60,-3]窗口 |
| **第三层：纪律约束验证** | 盈余公告[0,1]窗口的异常收益与季度媒体情感的**负向关联** = 纠偏效应 | `EA [0,1] Abn Return` 对 `Qtrly Media Sent` 的回归系数β₁ < 0 | **Higher Order Belief**框架下的截面异质性：零售/短期机构投资者交易量高时效应更强（Table 4）；基本面不确定性高（R&D/盈余波动/亏损）时更强（Table 5）；卖空约束高时更强（Table 6） |

**当前项目精准落差诊断**：

经代码级审计（`41_panel_encode_aggregate.py` L1-702、`42_panel_attention_media.py` L1-469、`45_panel_export_main.py` L1-1142、`config.yaml` L1-393），当前项目呈现**"三面领先、两处断裂"**的格局：

**✅ 已领先论文的三个维度（维持原状）**：

1. **媒体权威性加权**（`compute_media_authority_weights`）：项目已实现基于`media_weights.json`的媒体权威性分层加权（Tier 1-6），概念上对标论文的`Outlet Impact`维度。**但需注意**：论文采用的是**动态滚动回归**估计每季度的outlet固定效应（基于换手率），而项目采用**静态专家评分**——在中国银行业金融科技新闻这一垂直领域，静态权重更为稳定可解释，**维持原状优于论文方案**。
2. **LLM多模型投票情感分析**：项目的三模型投票（GPT5nano/Gemini3/Claude4h）+ BERT多头方案，在情感测量的颗粒度和鲁棒性上远超论文依赖的RavenPack ESS单一评分。**维持原状**。
3. **面板结构与IV体系**：项目的Bank-Year平衡面板 + Bartik IV + 地理LOO设计，在因果识别策略上已形成自洽的研究设计。**维持原状**。

**❌ 两处关键盲区**：

| 盲区 | 论文对标 | 当前管线现状 | 严重程度 |
|------|---------|------------|---------|
| **盲区A：软性信息衰减缺失** | `Article Uniqueness Media Sent`：首发报道权重100%，后续跟风报道按`G_ENS`指数衰减 | 仅有硬性文本去重（MinHash/Jaccard > 0.8），同一银行金融科技事件在跨媒体重复报道的情感被**等权累加**，导致"羊群效应放大器"偏误 | **高**：直接导致情感指标的测量偏误（measurement bias），高频媒体关注的银行-年份系统性高估 |
| **盲区B：情感内生性未控制** | `Qtrly Returns - Media Sent Driven`：通过滚动回归正交化，剥离风险因子和基本面信息 | 年度聚合的原始情感得分 = f(银行基本面) + f(政策环境) + f(纯媒体态度)，三者缠绕不分。在Stata回归中即使加入银行基本面控制变量，仍无法排除"情感不过是基本面的映射"的审稿人质疑 | **致命**：这是从"描述性发现"晋升到"因果机制论证"的核心方法论门槛 |

### 2. 实质性改进项（宁缺毋滥）

#### 改进 A：引入基于事件链的时间衰减权重（Article Uniqueness Weighting）

- **论文依据**：Appendix A "Article Uniqueness Media Sent"——利用RavenPack的`G_ENS`（Global Event Novelty Score），首发报道权重100%，后续同一事件报道按衰减函数递减至0，确保独立信息冲击被最准确地捕捉。
- **预期的边际贡献**：当前管线中，某银行发布一则金融科技重大合作新闻后，可能在3-7天内产生20-50篇跟风报道（中国金融媒体的典型传播模式）。这些报道在硬性去重后仍保留（因表述不同Jaccard<0.8），导致该事件的情感贡献被机械放大。引入时间衰减机制后，每个独立信息冲击的边际贡献将被精确校准——**解决的核心问题是情感指标中由媒体羊群效应造成的测量偏误**。
- **项目适配方案**：由于项目无RavenPack的G_ENS字段，需构建替代方案：在`confirmed_bank` + `fintech_topic`维度内，以首篇报道日期为锚点，对同一事件簇后续报道施加指数衰减函数 `novelty_weight = max(0.1, exp(-λ × Δdays))`。

#### 改进 B：构建剥离基本面的正交化金融科技情感指标（Orthogonalized Fintech Sentiment）

- **论文依据**：Appendix A "Qtrly Returns - Media Sent Driven"——通过滚动年度回归（eq.(b)），在日度层面控制Fama-French-Carhart四因子、分析师预测修正、公司新闻稿情感和8-K发布后，提取β₁系数作为媒体情感对收益的边际弹性，用于构建正交化的"媒体情感驱动收益"。
- **预期的边际贡献/解决的内生性问题**：当前pipeline中`llm_vote_cont`情感得分包含了银行真实基本面向好（如盈利增长、资产规模扩大）带来的"自然向好"成分。在下游实证回归中，即使控制了ROA、总资产等变量，仍面临**遗漏变量偏误**和**反向因果**的审稿人挑战。通过面板OLS回归剥离基本面映射后提取残差，可获得纯粹的"媒体舆论额外增量立场"——**这是从描述性研究跃升至因果推断的方法论关键**。
- **项目适配方案**：鉴于项目采用年度面板（非日度），将论文的日度滚动回归**降频适配**为年度截面回归：`Raw_Sentiment = α + β·Bank_Fundamentals + γ·Year_FE + ε`，残差ε即为`Orthogonalized_Fintech_Sentiment`。

### 3. 冗余剥离

| 论文内容 | 是否引入 | 理由 |
|---------|---------|------|
| **MIDAS混频数据抽样模型**（Table 7） | ❌ **坚决不采纳** | 论文使用MIDAS是为了在季度DV中纳入日度自变量的异质效应。当前项目的数据架构为**年度平衡面板**（`aggregation_frequency: yearly`），整体研究问题是银行金融科技的宏观战略性影响验证。强行引入日度混频模型是偏离主线的"伪需求"，且项目数据不具备日度收益率。**维持年度频次原状** |
| **日度异常收益率事件研究**（EA [0,1] Abn Return分析） | ❌ **坚决不采纳** | 项目不涉及股票日度收益率数据（银行报表数据为年度），且研究目标是舆情对银行行为的年度影响而非短期市场定价效率。引入盈余公告窗口事件研究属于完全不同的研究范式 |
| **零售/机构投资者交易分区**（Table 4） | ❌ **坚决不采纳** | 论文的Higher Order Belief截面检验依赖13F持仓和TAQ逐笔交易数据，这些数据仅存在于美股市场。中国银行业语境下无对标数据源，且与项目核心问题无关 |
| **卖空约束分区**（Table 6） | ❌ **坚决不采纳** | 同上理由，且中国银行板块的融券卖空受严格限制，截面变异不足以支撑检验 |
| **词典情感五本冗余**（`DICT_NAMES`中的jiang_2021/yao_2021/bian_2021/du_2022/you_2018） | ⚠️ **建议降级** | 项目已有LLM三模型投票+BERT五模型体系，词典方法的边际信息增量极低。建议在主回归中仅保留作为稳健性测试的备用测度，不再作为核心变量输出 |

---

## 第二部分：项目重构与优化执行计划书

### 1. 优先级排布

| 排序 | 改进项 | 类型 | 实施成本 | 预期收益 | 优先级 |
|------|--------|------|---------|---------|--------|
| **1** | **改进B：正交化金融科技情感** | 速赢项 (Quick Win) | **低**：仅需在`45_panel_export_main.py`的面板生成后追加一段OLS残差提取逻辑，≤50行代码 | **极高**：直接解决内生性核心质疑，将项目论证从描述性提升至准因果推断 | 🔴 **最高** |
| **2** | **改进A：新颖度衰减权重** | 核心攻坚项 | **中**：需在`41_panel_encode_aggregate.py`中新增事件簇识别和衰减权重计算逻辑，~100行代码 | **高**：消除媒体羊群效应导致的测量偏误，提高情感指标的信噪比 | 🟠 **高** |

### 2. 阶段化执行指令 (SOP)

#### 阶段一（速赢/实证模型重构）：基本面正交化情感指标构建

**定位**：这是论文方法论中最具移植价值的核心贡献——剥离基本面信息后的纯媒体情感残差。

**核心动作指令**：

1. **读取面板**：加载阶段41-44已生成的`40_panel_yearly.parquet`面板，确认包含以下字段：
   - 因变量方向：各模型情感得分（`llm_vote_cont_full`、`llm_vote_cont_ctx`等）
   - 银行基本面控制项：需从外部银行报表数据源合并

2. **定义基本面控制集**：根据论文eq.(b)的精神——排除风险因子和基本面信息——在年度面板框架下构建控制变量矩阵：
   ```
   控制变量 = {
     银行规模:     ln(总资产),
     盈利能力:     ROA, ROE,
     资产质量:     不良贷款率,
     资本充足:     资本充足率,
     成长性:       总资产增速,
     报道体量:     当年新闻总数 (n_articles),    ← 对标论文的 Number of Qtrly Articles
     年份固定效应:  Year_FE
   }
   ```

3. **执行正交化回归**：
   ```python
   # 对每个情感测度 s ∈ {llm_vote_cont_full, llm_vote_cont_ctx, ...}
   Raw_Sentiment_s = α + Σ β_k · Bank_Fundamental_k + Year_FE + ε
   # 截取残差 ε → 命名为 Orthogonalized_Fintech_Sentiment_s
   ```
   - 回归方法：Pooled OLS with year fixed effects（年度面板样本量有限，FE优于RE）
   - 标准误：聚类至银行层面（`target_bank`）

4. **持久化输出**：将正交化情感变量追加至面板 Parquet/Stata 文件，字段命名约定：`ortho_{原始情感变量名}`
   - 示例：`ortho_llm_vote_cont_full`, `ortho_llm_vote_cont_ctx`, `ortho_finbert_cn_mean_full`

**交付物标准**：
- ✅ 正交化情感指标与银行ROA的Pearson/Spearman相关系数_p>0.10_（即统计不显著）
- ✅ 正交化情感指标与原始指标的相关系数 r ∈ [0.60, 0.95]（保留足够变异，但已剥离基本面成分）
- ✅ Excel/日志中自动输出正交化回归的R²、F-stat和各系数t值，作为方法论可追溯性凭证

**Stata do文件联动**：在导出的Stata .dta文件中同时包含原始和正交化变量，并在do文件头部添加说明注释：
```stata
/* 正交化情感指标（Orthogonalized Fintech Sentiment）
   方法论来源: Holzman, Miller & Twedt (2023, TAR) Appendix A, eq.(b)
   适配方案: 年度面板OLS残差法, 控制银行基本面 + Year_FE
   解释: ortho_* 变量 = 原始情感 - 银行基本面预测值
         代表剥离基本面信息后的纯媒体舆论增量立场 */
```

---

#### 阶段二（机制重塑/数据清洗）：文章新颖度衰减权重集成

**定位**：对标论文的`Article Uniqueness Media Sent`，解决中国金融媒体"一事多报"导致的情感放大偏误。

**核心动作指令**：

1. **事件簇识别**：在计算单个实体的聚合情感前（涉及`41_panel_encode_aggregate.py`的聚合逻辑），按 `confirmed_bank` + `fintech_topic_full`（或`fintech_topic_ctx`）作为聚类复合键。

2. **时间窗口内排序**：在每个事件簇内，按`日期`升序排列该银行关于该主题的所有报道。

3. **衰减权重计算**：
   ```python
   # 簇内首发报道
   novelty_weight = 1.0
   # 后续报道（Δdays = 当前报道日期 - 簇内首发报道日期）
   novelty_weight = max(0.1, exp(-λ × Δdays))
   # λ 衰减参数建议: λ = 0.3（半衰期≈2.3天, 对标论文G_ENS的中位衰减速度）
   ```
   - 生成新字段 `novelty_weight`，值域 [0.1, 1.0]

4. **复合权重融合**：在Bank-Year聚合时，使用双重复合权重：
   ```
   composite_weight = media_authority_weight × novelty_weight
   ```
   - 加权平均情感 = Σ(sentiment_i × composite_weight_i) / Σ(composite_weight_i)

5. **衰减参数敏感性**：λ ∈ {0.1, 0.2, 0.3, 0.5, 1.0} 的五组敏感性检验，输出五组加权情感指标并在Excel报告中并列。

**交付物标准**：
- ✅ 面板中新增 `novelty_weight` 列和 `composite_weight` 列
- ✅ 使用复合权重的加权情感与等权情感的相关系数 r ∈ [0.80, 0.98]（预期应高度相关但非完全相同）
- ✅ 输出"最大信息损失检查"：衰减后情感方差 / 衰减前情感方差 > 0.5（确保未过度平滑）
- ✅ 日志中报告："被衰减的报道比例"、"平均衰减幅度"、"受影响银行-年数"

---

#### 阶段三（核心结论重构）：以正交化指标替代原始指标进行全样本主回归

**动作指令**：

1. 在Stata导出的面板中，将 `ortho_llm_vote_cont_full`（正交化 + 完整分析）和 `ortho_llm_vote_cont_ctx`（正交化 + 上下文分析）作为核心解释变量，**替代原始情感指标**进入主回归。

2. 构建以下回归表格结构（对标论文Table 2的五列设计，适配为四列）：

   | 列 | 自变量 | 对应论文测度 |
   |----|--------|------------|
   | (1) | `llm_vote_cont_full`（原始等权） | Unweight Media Sent |
   | (2) | `wt_llm_vote_cont_full`（权威性加权） | Outlet Impact Media Sent |
   | (3) | `nov_llm_vote_cont_full`（新颖度衰减加权） | Article Uniqueness Media Sent |
   | (4) | `ortho_llm_vote_cont_full`（正交化） | Qtrly Returns - Media Sent Driven |

3. 核心论证逻辑："**剥离了银行真实基本面变化的成分后，纯粹基于外部媒体立场的金融科技情绪同样真实且显著地影响银行下一期的风险行为决策。**"

4. 稳健性检验矩阵（逐步添加，形成嵌套）：
   - ① 替换因变量（ROA → 不良贷款率变动/拨备覆盖率变动）
   - ② 替换情感模型（LLM投票 → BERT均值 → 词典方法）
   - ③ 替换衰减参数（λ = 0.1 vs 0.3 vs 1.0）
   - ④ 子样本测试：按银行规模分位（大型/中小型）、按年份分段（政策时期异质性）

### 3. 风险预案 (Plan B)

#### 致命卡点 #1：银行基本面数据缺失

- **风险描述**：正交化回归（改进B）需要银行财务报表数据（ROA/总资产/不良贷款率等），若外部数据源不可得或无法匹配。
- **替代方案 (Plan B-1)**：降级为**年份-银行规模分组**内的Z-score标准化。具体：在每个year × bank_size_group中对情感得分做Z-score，利用"同组同期银行基本面相似"的假设近似消除基本面效应。虽不如OLS残差精确，但实施零外部数据依赖。

#### 致命卡点 #2：fintech_topic颗粒度过粗

- **风险描述**：LLM提取的`fintech_topic`可能过于宽泛（如统一标注"应用场景"），导致改进A的事件簇识别将不相关的报道误判为同一事件链，产生不当衰减。
- **替代方案 (Plan B-2)**：放弃事件级别识别，降维采用**时间窗口饱和度衰减**——在每个bank × month维度上，若金融科技报道总数超过阈值N（建议N=10），超出部分采用对数平滑权重 `weight = log(N+1)/log(count+1)`。
- **兜底方案 (Plan B-3)**：若Plan B-2仍不可靠，则**直接搁置改进A**。单改进B（面板残差剥离）的方法论升级已足够支撑一篇顶级期刊论文的内生性控制需求。

#### 致命卡点 #3：年度面板样本量受限

- **风险描述**：正交化回归需要足够的bank × year观测值来估计稳定的OLS系数（当前面板约40家银行 × 7-10年 ≈ 280-400个观测值）。
- **替代方案 (Plan B-4)**：将回归中的银行基本面控制变量从连续型改为分类型（如ROA高/中/低三分位），减少待估参数数量。或者采用**FWL（Frisch-Waugh-Lovell）定理**等价方法，分步回归以提高数值稳定性。

---

## 附录：论文-项目对照速查表

| 论文核心概念 | 论文测度 | 项目对标实现 | 对标状态 |
|------------|---------|------------|---------|
| 未加权媒体情感 | `Unweight Media Sent` | `llm_vote_cont_full/ctx` 等权聚合 | ✅ 已实现 |
| 媒体影响力加权 | `Outlet Impact Media Sent` | `compute_media_authority_weights` (静态权重) | ✅ 已实现（静态版，优于论文动态版在本场景的适用性） |
| 文章新颖度衰减 | `Article Uniqueness Media Sent` (G_ENS) | ❌ 待实现 | 🔴 **改进A** |
| 双重加权情感 | `Outlet & Article Wgt Media Sent` | ❌ 待实现（权威性 × 新颖度复合权重） | 🔴 **改进A** |
| 正交化情感驱动收益 | `Qtrly Returns - Media Sent Driven` | ❌ 待实现（年度面板OLS残差降频适配） | 🔴🔴 **改进B（最高优先级）** |
| 盈余公告异常收益 | `EA [0,1] Abn Return` | ❌ 不适用——项目年度面板无日度收益率 | ✅ 维持原状，不引入 |
| 五分位排名鲁棒性 | `Q(Qtrly Media Sent)` | 可简单实现：`pd.qcut(sent, 5)` | ⚪ 可选扩展 |
| 熵平衡匹配 | Entropy Balancing (Table 3D) | 可通过`ebalance`命令在Stata中实现 | ⚪ 可选扩展 |
| MIDAS混频模型 | Table 7 | ❌ 不适用——偏离年度面板范式 | ✅ 维持原状，坚决不引入 |
| 投资者类型截面 | Table 4 (散户/机构分区) | ❌ 不适用——缺少13F/TAQ数据 | ✅ 维持原状，坚决不引入 |
| 基本面不确定性截面 | Table 5 (R&D/波动率/亏损分区) | ⚪ 可部分实现（银行可按资产质量/规模分区） | ⚪ 可选扩展 |
| 卖空约束截面 | Table 6 | ❌ 不适用——中国银行板块融券受限 | ✅ 维持原状，坚决不引入 |
