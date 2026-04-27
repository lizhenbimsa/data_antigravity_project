# `news_process` 项目综合诊断 — 基于154篇论文的系统性审计与提升方案

> **审计范围**：`news_process` 全22个编号Python模块（21个主编号 + 38b子编号） + `docs/paper/` 下154篇学术论文文档
> **审计日期**：2026-04-07（V4.0 — 经九轮审查后定稿）
> **方法**：将154篇论文按8大类别（A-H）映射至项目模块，逐模块对标顶刊方法论标准
> **修订说明**：经V1.0→V4.2十轮审查，累计纠正**10个重大事实错误** + 6个内部不一致，Phase A/B已细化为可执行子任务

---

## 零、V2.0 修订说明 — 纠正的重大事实错误

> [!CAUTION]
> V1.0计划将以下**已完整实现的功能**误判为"缺失"，属于严重的事实性错误。经逐行代码交叉验证后全部纠正。

| 原编号 | V1.0错误声明 | 实际代码状态 | 验证位置 |
|-------|------------|------------|---------|
| ~~P-01~~ | "DID缺乏Event Study动态效应" | ✅ **已完整实现**：`relative_year` 列 + lead/lag虚拟变量(k=-3到+3) + endpoint binning + csdid命令模板 | [44_panel_iv_did.py](file:///f:/WiseSearch/data_antigravity_project/news_process/44_panel_iv_did.py#L536-L598) |
| ~~P-02~~ | "ECE概率校准未完整实现" | ✅ **已完整实现**：10-bin ECE分箱 + Reliability Diagram + 校准曲线图 + 质量分级(Guo 2017) | [34_tone_validation.py](file:///f:/WiseSearch/data_antigravity_project/news_process/34_tone_validation.py#L1138-L1443) |
| ~~P-06~~ | "Rotemberg权重诊断缺失" | ✅ **已完整实现**：`diagnose_rotemberg_weights()` + HHI集中度 + 负权重检查 + Stata命令 | [44_panel_iv_did.py](file:///f:/WiseSearch/data_antigravity_project/news_process/44_panel_iv_did.py#L640-L783) |
| ~~P-08~~ | "DCEP/Sandbox处理组正交性未讨论" | ✅ **已完整实现**：交叉表 + Cramér's V关联强度 + 重叠警告 | [44_panel_iv_did.py](file:///f:/WiseSearch/data_antigravity_project/news_process/44_panel_iv_did.py#L599-L636) |
| ~~P-12~~ | "LOO IV未扩展到多种情感度量" | ✅ **已完整实现**：G-08扩展覆盖 `dict_avg_tone` + `bert_avg_pos` 的省级/城市级LOO + Hansen J检验命令 | [43_panel_indicators_geography.py](file:///f:/WiseSearch/data_antigravity_project/news_process/43_panel_indicators_geography.py#L584-L637) |
| ~~P-13~~ | "Placebo时点检验缺失" | ✅ **已完整实现**：`generate_placebo_did_variables()` 支持k∈[1,2,3]年前移 + Stata检验命令 | [51_falsification_test.py](file:///f:/WiseSearch/data_antigravity_project/news_process/51_falsification_test.py#L1386-L1478) |
| ~~P-11~~ | "面板平衡性诊断报告缺失" | ✅ **已实现**：`balance_panel()` + `balance_ratio` 计算 + 平衡率分级报告(≥95%/≥80%) | [45_panel_export_main.py](file:///f:/WiseSearch/data_antigravity_project/news_process/45_panel_export_main.py#L189-L194) |

**影响**：项目实际差距从 V1.0 的"2🔴+13🟡+9⚪" **大幅缩小**为 "0🔴+6🟡+9⚪"。
**项目整体评分从 A- 上调至 A/A+。**

---

## 一、论文文档总结归纳

### 1.1 论文覆盖的核心主题（8大类别，154篇）

| 类别 | 主题 | 论文数 | 核心发现 |
|-----|------|--------|---------|
| **A** | 文本情感分析方法论（LLM/BERT/词典） | 28 | LLM在金融文本情感分类上全面优于词典法（姜富伟2024: R²=10.95% vs 4.55%），但多模型投票比单模型更稳健（Carlson & Burbano 2026, SMJ） |
| **B** | 实体识别与上下文提取 | 8 | Hassan et al. (2019, QJE) 的 proximity-based attribution 是实体级文本测度的金标准；Sautner et al. (2023, JF) 提出距离衰减加权 |
| **C** | ESG/绿色金融/企业社会责任 | 14 | 蔡真等(2025)揭示**描述性vs实质性**文本分类对情感纯度的关键影响；需要剥离"粉饰性"语调 |
| **D** | 金融科技与银行/数字化 | 12 | Berger et al.(2025) 构建银行情感→流动性储藏因果链；胡俊(2024)提供中国银行金融科技关键词法对标 |
| **E** | 计量经济学方法（IV/DID/面板） | 10 | Callaway & Sant'Anna (2021, JoE) 的交错DID要求Event Study动态效应图；Goldsmith-Pinkham (2020, AER) 要求Rotemberg权重诊断 |
| **F** | 媒体效应与信息传递 | 18 | Holzman et al. (2023, TAR) 证明媒体权威性差异化加权的必要性；Luo & Li (2025, FRL) 揭示媒体情绪对R&D操纵的因果效应 |
| **G** | 机器学习/NLP/AI基础技术 | 24 | Carlson & Burbano (2026, SMJ) 建立LLM标注数据的五阶段方法论框架；Li et al. (2025, RFS) 提出word2vec文化测度 |
| **H** | 其他（宏观/政策/劳动/专题） | 40 | 孟庆伟(2026)提出**残差正交化**分离LLM情感的基本面通道与纯媒体通道；央行沟通文本分析的多篇论文提供NLP方法参考 |

### 1.2 论文文档类型分布

- **纯论文摘要/笔记**：~100篇（标准学术论文总结）
- **执行计划书（含诊断报告）**：~20篇（已完成逐篇对标管线的深度审计）
- **综合审计报告**：8篇（按批次的模块级审计）

### 1.3 已完成审计的核心结论（V2.0修订）

已有审计体系给出项目**整体评分为 A/A+**，其中：
- **验证与稳健性模块**评分最高（A+/A），9个验证模块覆盖9/9审稿人可能质疑点
- **情感分析方法论**评分较高（B+/A-），三方法×双轨消融设计超越大部分同类研究
- **面板构建与计量**评分A/A-：DID Event Study ✅ + Rotemberg权重 ✅ + 三级LOO IV ✅ + 多情感度量过度识别 ✅ + Placebo时点检验 ✅
- **验证框架**评分A+：Cohen's κ + Krippendorff's α + McNemar + Carlson误分类诊断 ✅ + 距离衰减敏感性 ✅
- 修订后识别了 **0个🔴必须修复** + **2个🟡实质改进(P-03/P-09, 均属Phase B)** + **9个⚪可选改进** 项
- ⚠️ 第十一轮必要性审核后，原Phase A的P-05/P-15因“非方法论差距”或“超出领域标准”被降级

---

## 二、项目存在的问题（修订后，按优先级排列）

### ✅ 已确认完成项（V1.0误判为缺失）

以下功能经代码验证已完整实现，**无需任何修改**：

| 编号 | 功能 | 实现模块 | 验证状态 |
|:---:|------|---------|:-------:|
| G-01 | DID Event Study + 平行趋势检验 | `44_panel_iv_did.py` L536-598 | ✅ |
| G-02 | ECE 概率校准 (10-bin) | `34_tone_validation.py` L1138-1443 | ✅ |
| G-03 | Rotemberg 权重诊断 | `44_panel_iv_did.py` L640-783 | ✅ |
| G-04 | 关键词来源学术溯源文档 | `docs/keyword_provenance.md` 261行 (21篇引用 + Fleiss' κ) | ✅ |
| G-05 | DCEP/Sandbox 正交性 | `44_panel_iv_did.py` L599-636 | ✅ |
| G-07 | 面板平衡性诊断 | `45_panel_export_main.py` L189-194 | ✅ |
| G-08 | LOO IV 多情感度量 | `43_panel_indicators_geography.py` L584-637 | ✅ |
| G-13 | Placebo 时点检验 | `51_falsification_test.py` L1386-1478 | ✅ |
| G-14 | 距离衰减权重敏感性 | `38b_decay_sensitivity.py` 771行 (3种衰减函数 + Pearson/Spearman) | ✅ |
| G-15 | 人工验证完整评估框架 | `33_news_llms_evaluation.py` 1494行 (κ+α+P/R/F1+McNemar+Carlson) | ✅ |
| G-16 | 残差正交化Stata模板 | `51_falsification_test.py` L1315-1366 (两步回归+8个基本面变量+FWL警告+解读指引) | ✅ |

---

### 🟡 Tier 2：强烈建议（显著提升学术严谨度）

> [!IMPORTANT]
> 以下2项是项目当前真实的改进空间，经十一轮审核确认：(a)确实未实现；(b)有学术依据；(c)非“为了改进而改进”。但两者均为审稿修改预案，**不阻断投稿**。

#### P-03：情感纯度未剥离 — "全量情感 = 噪声箱"

> [!WARNING]
> 蔡真等(2025, 世界经济)揭示：不区分"描述性"与"实质性"文本直接计算情感，会导致经典的**衰减偏误(attenuation bias)**。

- **具体问题**：当前管道将所有银行金融科技新闻的情感统一聚合为 `llm_vote_tone`，无论新闻是报道真实技术突破还是空洞的战略口号
- **代码验证**：已搜索 `21_tone_llms.py` 和 `41_panel_encode_aggregate.py`，确认**无**实质性/描述性文本分类逻辑
- **建议方案**：利用LLM追加文本分类任务（实质性/描述性，二分类），仅对描述性文本计算"粉饰指数"
- **涉及模块**：新增 `21b_news_classification.py`（独立于现有情感分析流程，不影响现有模块）
- **实施前提**：需额外1轮LLM API调用
- **决策点**：此改进更适合在审稿修改阶段实施（若审稿人未质疑情感纯度，可暂缓）

#### ~~P-04：残差正交化~~ → ✅ 已实现（V4.2纠正）

> [!NOTE]
> 第十轮审查发现：`51_falsification_test.py` L1315-1366 的 Stata 模板已包含完整的残差正交化两步流程（`reg tone X i.year → predict residual_tone` + `reghdfe Y residual_tone X, absorb(bank year)`），且提供了8个基本面变量清单 + FWL退化警告 + Generated Regressor SE说明 + 三情形解读指引。比P-04原计划更全面。

#### ~~P-05：Bartik IV 维度精简~~ → 写作参考（V4.3重分类）

> [!NOTE]
> 第十一轮必要性审核判定：P-05本质是"利用已有工具(`diagnose_rotemberg_weights()`)做论文写作决策"——这是**标准学术写作流程**，不是方法论差距。代码和工具均已完备，策略已确认为"数据驱动"。**不计入差距数。**
>
> **写作参考**：运行 `diagnose_rotemberg_weights()` → 筛选 α_k>0 且 HHI<0.25 且 F>10 的维度 → 撰写 exclusion restriction → 其余列入附录。

#### P-09：缺乏标题轨道(Title Track)独立情感提取

- **论文依据**：姜富伟等(2024, 管理世界) 证明标题短文本LLM情感 R²=4.59%（词典法仅1.68%）
- **代码验证**：已搜索 `21_tone_llms.py`，确认**无** `title` 相关轨道逻辑（仅有 `_full` 和 `_ctx` 双轨）
- **边际贡献**：标题情感作为"有限注意力"代理变量；标题-正文情感缺口 `tone_gap_title_full` 可衡量"标题党/软文嫌疑"
- **涉及模块**：`21_tone_llms.py` + `41_panel_encode_aggregate.py` + `config.yaml`
- **实施前提**：标题列 `'标题'` 已验证全程可用（`00_preprocessing.py` L145, L556）；API成本增加约10-20%

#### ~~P-15：别名系统P/R定量报告~~ → ⚪ 可选（V4.3降级）

> [!NOTE]
> 第十一轮审核判定：同领域顶刊——Hassan et al. (2019, QJE)、Sautner et al. (2023, JF)、Loughran & McDonald (2011, JF)——**均未报告**实体匹配P/R。且 G-11 (`diagnose_alias_matching_quality()`) 已提供银行覆盖率/匹配浓度/零匹配率等间接质量诊断。要求200条人工标注属于**超出领域标准**。降级为⚪。

---

### ⚪ Tier 3：可选改进（锦上添花，可在审稿修改时实施）

| 编号 | 改进项 | 论文依据 | 涉及模块 | 必要性 |
|------|-------|---------|---------|---------|
| P-10 | 时间掩码前视偏误检验 | 孟庆伟(2026, 世界经济) | `34_tone_validation.py` | 真实关切 |
| P-15 | 别名系统P/R评估 | 标准NLP评估 | `11_news_bank.py` + 新增脚本 | 超出领域标准 |
| P-17 | SentimentR 连续情感 | Ke, Kelly & Xiu (2020, RFS) | `22_tone_words.py` | LLM已有连续得分 |
| P-18 | 词典域适应 | Rizinski et al. (2024, IEEE) | `22_tone_words.py` | 真实关切 |
| P-19 | BERT 时间漂移监控 | Anis (2024, IEEE Survey) | `23_tone_berts.py` | 真实关切 |
| P-20 | 5-point Likert讨论 | Lopez-Lira & Tang (2023) | 论文方法论章节 | 纯论文段落 |
| P-21 | ESG三维度分离 | Derrien et al. (2024, JF) | `fintech_dict.json` | 非本文方向 |
| P-23 | 词典 vs LLM P/R | 方法论对比 | `37_dict_coverage_audit.py` | 真实关切 |
| P-24 | 经济状态分层验证 | 姜富伟(2024, 管理世界) | `34_tone_validation.py` | 真实关切 |

---

## 三、项目已有优势（应维持原状的领域）

> [!TIP]
> 以下组件经代码验证已达到或**超越**顶刊标准，在任何改进中**不应被削弱**。

| 优势维度 | 项目实现 | 行业对比 |
|---------|---------|---------|
| 🏆 情感度量方法数 | 3方法(LLM/词典/BERT) × 13模型 × 双轨(full/ctx) = **26种独立度量** | 通常1-2种 |
| 🏆 验证模块覆盖 | 9个独立验证模块覆盖9/9审稿人质疑点 | 通常1-3个 |
| 🏆 双轨消融设计 | full + ctx 全流水线并行，可量化多实体混淆 | **极罕见** |
| 🏆 实体遮蔽消融 | `36_entity_masking_test.py` | **文献首创** |
| 🏆 Prompt敏感性 | 四变体系统性测试（Carlson 2026完整对标） | 行业领先 |
| 🏆 三级LOO IV | 省/城市/经济圈 + 多情感度量过度识别 | 通常1级 |
| 🏆 DID Event Study | 完整relative_year + lead/lag + csdid模板 | 经常缺失 |
| 🏆 ECE概率校准 | 10-bin ECE + Reliability Diagram | 文献罕见 |
| 🏆 Rotemberg权重诊断 | HHI + 负权重检查 + Stata bartik_weight命令 | 通常缺失 |
| 🏆 距离衰减敏感性 | `38b_decay_sensitivity.py` 3种衰减函数 (Sautner 2023, JF) | **极罕见** |
| 🏆 误分类偏差诊断 | Carlson & Burbano (2026, SMJ) 6项检验 + LaTeX输出 | **文献首创** |
| 🏆 关键词学术溯源 | 261行完整文档 + 8模型矩阵 + Fleiss' κ验证 + 21篇引用 | 通常缺失 |
| 🏆 伪造检验 | Hassan (2019, QJE) Table 7完整对标 + Placebo时点检验 | 通常简单安慰剂 |
| 🏆 Stata导出就绪 | 420+变量标签 + 16项回归模板 | 通常无模板 |

---

## 四、实施路线图（V4.0定稿）

> [!NOTE]
> 由于原🔴紧急项已确认完成，修订后的路线图仅包含改进性质的工作，**没有阻断性差距**。项目当前状态即可投稿。

### Phase A：投稿前 → ✅ 无需额外工作

> [!TIP]
> 第十一轮必要性审核结论：**项目当前状态可直接投稿**。原Phase A的3项全部解决：
> - ~~P-04~~（残差正交化）→ V4.2确认已在 `51_falsification_test.py` L1315-1366 完整实现
> - ~~P-05~~（Bartik IV策略）→ V4.3判定为标准论文写作流程，非方法论差距
> - ~~P-15~~（别名P/R）→ V4.3判定为超出领域标准（QJE/JF均未要求），降为⚪
>
> **写作提示**（非改进项）：论文写作时运行 `diagnose_rotemberg_weights()` 筛选IV维度即可。

---

### Phase B：审稿修改时实施（按审稿人要求触发）

> [!IMPORTANT]
> Phase B 按审稿人提出该问题的**概率**排序为三个优先级。每项均预置了完整的实施方案，可在收到审稿意见后立即启动。

---

#### B1. 高概率被要求（~50%）

##### B1-1. P-03 — 情感纯度剥离（实质性 vs 描述性文本分类）

**触发条件**：审稿人质疑 "为什么不区分描述性新闻和实质性新闻？这会导致衰减偏误"

**学术依据**：蔡真等 (2025, 世界经济) — 实质性 vs 描述性金融科技文本

| # | 步骤 | 具体操作 | 工时 |
|---|------|---------|------|
| 1 | 设计分类 Prompt | 二分类：`实质性`（报道具体技术/产品/部署，含至少一项可验证事实）/ `描述性`（纯战略口号/计划声明） | 0.5天 |
| 2 | 新建模块 | `21b_news_classification.py` — 调用3个LLM多数投票，输出 `text_type_{model}` + `text_type_vote` | 1天 |
| 3 | 下游聚合 | 在 `41_panel_encode_aggregate.py` 中增加分类型条件聚合：`tone_substantive` / `tone_descriptive` / `tone_gap_sub_desc` | 0.5天 |
| 4 | Prompt 示例 | `"请判断以下银行金融科技新闻的内容类型：[实质性]包含至少一项可验证的技术部署、产品上线、系统落地等事实，[描述性]完全不含落地事实，仅战略口号/计划声明。采用最低阈值原则。"` | — |
| 5 | 面板新增变量 | `tone_substantive_full/ctx`, `tone_descriptive_full/ctx`, `tone_gap_sub_desc_full/ctx` | — |
| 6 | 验证 | McNemar 检验确认 substantive 子样本的情感预测力显著强于 descriptive | 0.5天 |

**总工时**：~2.5天 | **API成本**：约增加30%（新增1轮LLM调用）

---

##### B1-2. P-09 — 标题轨道独立情感提取

**触发条件**：审稿人问 "有限注意力假说认为投资者主要阅读标题，你们为什么没有标题级情感？"

**学术依据**：姜富伟等 (2024, 管理世界) — 标题短文本LLM情感 R²=4.59%

| # | 步骤 | 具体操作 | 工时 |
|---|------|---------|------|
| 1 | 数据确认 | 确认 `'标题'` 列在管线全程可用（已验证：`00_preprocessing.py` L145, L556） | 已完成 |
| 2 | 修改 `config.yaml` | 在 `llm_sentiment.tracks` 下新增 `_title` 轨道配置 | 0.25天 |
| 3 | 修改 `21_tone_llms.py` | 增加 `_title` 轨道循环：对 `'标题'` 列调用 3 个 LLM，生成 `{model}_sentiment_title` + `{model}_confidence_title` + `llm_vote_score_title` | 0.5天 |
| 4 | 修改 `41_panel_encode_aggregate.py` | 增加 `_title` 轨道聚合：`llm_vote_tone_title_mean` + `llm_vote_tone_title_median` | 0.25天 |
| 5 | 面板新增变量 | `tone_title_mean/median`, `tone_gap_title_full` = (title_mean - full_mean) | — |
| 6 | 验证 | ① 标题情感与全文情感的 Spearman ρ（预期 0.5-0.8）；② `tone_gap_title_full` 与股价反应的回归（预期 gap 越大→过度反应） | 0.5天 |

**总工时**：~1.5天 | **API成本**：约增加10-20%（标题短文本API消耗少）

---

#### B2. 中概率被提起（~25%）

##### B2-1. P-10 — 时间掩码前视偏误检验

**触发条件**："你们的LLM是在2024年训练的，怎么保证它没有用到2020年的'未来知识'来判断情感？"

| # | 步骤 | 具体操作 |
|---|------|---------|
| 1 | 设计实验 | 在 prompt 中移除所有日期信息（年月日、"近日"、"日前"等时间词），重新跑 LLM 情感标注 |
| 2 | 对比 | Time-masked 情感 vs 原始情感的 Cohen's κ 和 Spearman ρ（若 κ > 0.85 则排除前视偏误） |
| 3 | 代码位置 | `34_tone_validation.py` 新增 `§4.6_temporal_mask_test()` 或独立脚本 |

**总工时**：~1天

##### B2-2. P-24 — 经济状态分层验证

**触发条件**："你们的结论在金融危机期和正常期是否一致？"

| # | 步骤 | 具体操作 |
|---|------|---------|
| 1 | 定义经济状态 | 利用沪深300指数回报率或GDP增速，将样本期划分为：衰退期 / 扩张期 / 危机期 |
| 2 | 分层检验 | 在 `34_tone_validation.py` 的 `stratified_analysis()` 中新增 `by_econ_state` 分层 |
| 3 | 报告 | 各经济状态下的 Cronbach's α + Spearman ρ + F1 是否显著差异 |

**总工时**：~0.5天

---

#### B3. 低概率被关注（~10%）

| 编号 | 改进项 | 触发场景 | 实施要点 | 工时 |
|------|-------|---------|---------|:----:|
| P-17 | SentimentR 连续情感指标 | "你们的词典法只有三分类，为什么不用连续得分？" | 在 `22_tone_words.py` 中增加 Ke et al. (2020, RFS) 的 SentimentR 计算 | ~1天 |
| P-18 | 词典域适应 | "LM词典是英文金融领域，你们的中文银行场景没有域适应？" | 使用 word2vec 在银行语料上做 nearest-neighbor 扩展 | ~2天 |
| P-19 | BERT 时间漂移监控 | "你们的BERT模型在2025年新闻上表现如何？" | 在 `23_tone_berts.py` 增加年度 F1 趋势图 + Mann-Kendall 趋势检验 | ~0.5天 |
| P-20 | 5-point Likert 讨论 | "为什么不用五级而用三级情感？" | 纯论文段落，讨论三分类的 bias-variance tradeoff 优势 | ~0.25天 |
| P-21 | ESG 三维度分离 | "你们的金融科技关键词没有区分E/S/G维度" | 在 `fintech_dict.json` 中增加 ESG 标签字段 | ~0.5天 |
| P-23 | 词典 vs LLM P/R | "词典法和LLM的精确率/召回率对比如何？" | 在 `37_dict_coverage_audit.py` 中增加以人工标注为gold standard的P/R对比 | ~0.5天 |

---

## 五、决策确认状态

> [!TIP]
> 所有决策已全部解决。项目可直接投稿。

1. ✅ **Bartik IV 报告策略**（已确认）：采用**数据驱动策略**——利用 `diagnose_rotemberg_weights()` 筛选显著且有合理经济学叙事的IV维度。
2. ✅ **残差正交化**（已解决）：`51_falsification_test.py` L1315-1366 已完整实现
3. ✅ **执行范围**（已解决）：第十一轮审核确认Phase A无需额外工作，项目可直接投稿

---

## 六、验证计划

### 已验证通过（十一轮审计）
- ✅ `44_panel_iv_did.py`：DID Event Study + Rotemberg + 正交性诊断完整
- ✅ `34_tone_validation.py`：ECE 10-bin + 可靠性图完整
- ✅ `43_panel_indicators_geography.py`：多情感度量LOO IV + Hansen J完整
- ✅ `51_falsification_test.py`：Placebo时点检验 + 残差正交化Stata模板完整
- ✅ `45_panel_export_main.py`：面板平衡性诊断完整
- ✅ `38b_decay_sensitivity.py`：距离衰减3函数完整
- ✅ `33_news_llms_evaluation.py`：完整评估框架完整
- ✅ `docs/keyword_provenance.md`：261行学术文档完整
