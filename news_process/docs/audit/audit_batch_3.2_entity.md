# Batch 3.2 审计报告：实体识别与上下文提取

> **审计范围**：`utils/entity_context.py` | `11_news_bank.py` | `12_news_fintech.py` | `35_radius_sensitivity.py` | `36_entity_masking_test.py`
> **对标文献**：8篇 (B类) + F类/G类交叉引用
> **生成时间**：2026-04-06
> **审计等级**：深度模式 (Full-text Analysis)

---

## 一、审计目标

验证项目的"实体特异性上下文提取→分类→对标"流水线是否满足顶级金融期刊 (JF/RFS/QJE) 在**企业级暴露度测度**方面的方法论要求。核心考察三个关键环节：

1. **实体-文本归因 (Entity-Text Attribution)**：新闻文本如何精确归因到特定银行/金融科技企业？
2. **上下文隔离 (Context Isolation)**：如何从长文本中提取与目标实体直接相关的语境窗口？
3. **分类精度控制 (Classification Precision)**：新闻行业标签 (银行/金融科技) 的假阳性假阴性如何控制？

---

## 二、核心文献精读摘要

### 2.1 Hassan, Hollander, van Lent & Tahoun (2019, QJE) — *Firm-Level Political Risk*

**核心方法论**：
- **句级 Proximity-based Attribution**：通过测量政治关键词与企业名称在财报电话会议记录中的共现距离，构建企业级政治风险指数 (PRisk/PSentiment)
- **核心假设**：如果政治词汇出现在提及企业名称的句子的**±1句**半径内，则认为该政治讨论与该企业直接相关
- **验证策略**：
  - Table 7 PRisk vs NPRisk（政治性 vs 非政治性伪造检验）——核心伪造逻辑
  - Panel 回归控制行业/年份/企业固定效应
  - Bartik IV 使用全国政治事件作为外生冲击

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| sentence_radius=1 (±1句) | `entity_context.py` 默认 `sentence_radius=1` | ✅ **完全一致** |
| 句号边界分割 | 实现中文句号/问号/叹号分割 | ✅ 一致 |
| 区间合并去重 | O(N log N) 排序合并 | ✅ **算法优化** |
| PRisk vs NPRisk 伪造 | `51_falsification_test.py` 完整实现 | ✅ **核心引用** |
| 短文本退化处理 | `fallback_char_radius=150` 字符级回退 | ✅ **超越**原文 |
| 距离衰减权重 | **未实现** | ⚠️ 见 Sautner (2023) |

### 2.2 Sautner, van Lent, Vilkov & Zhang (2023, JF) — *Firm-Level Climate Change Exposure*

**核心方法论**：
- **演进式关键词发现算法 (Keyword Discovery Algorithm)**：
  - Phase 1：种子词 (seed bigrams) 从 IPCC 报告 + 学术手动筛选
  - Phase 2：TF-IDF 扩展——从财报语料中提取与种子词高度共现的新词组
  - Phase 3：人工验证 + 迭代精炼 → 最终词典含 ~985 个 unigram/bigram
- **三级暴露度分解**：
  - 总体气候暴露 (CCExposure) = 对话中气候相关句子比例
  - 机遇暴露 (OpportunityExposure) = 正面语境
  - 风险暴露 (RiskExposure) = 负面语境
- **关键技术细节**：
  - **加权距离衰减** (Weighted Distance Decay)：距离目标实体越远的句子，权重越低
  - **分母归一化**：用总对话长度归一化，消除文档长度偏差
  - **行业-年份中心化**：暴露度减去行业-年份均值，提取企业级异质性

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 演进式关键词发现 | `bank_names.json` 手动维护 | ⚠️ 技术路径不同，可接受 |
| TF-IDF 扩展机制 | `22_tone_words.py` 有 IDF 加权但非扩展 | ℹ️ 不同目的 |
| **加权距离衰减** | `entity_context.py` 使用**均匀权重**窗口 | 🟡 **可改进** |
| 分母归一化 (文档长度) | 未显式对文本长度归一化 | 🟡 下游 Panel 聚合时隐式处理 |
| 行业-年份中心化 | `43_panel_indicators_geography.py` Fama-MacBeth z-score | ✅ **功能等价** |
| 三级暴露度分解 | 项目有 pos/neg/neutral 三分类 | ✅ 逻辑类似 |
| 人工验证迭代词典 | `37_dict_coverage_audit.py` 覆盖率审计 | ✅ 验证机制存在 |

### 2.3 Fan, Gillan, Haviland, Li & Nong (2025, Management Science) — *Measuring Misinformation in Financial Markets*

**核心方法论**：
- **信息网络构建 (Information Network)**：
  - 每篇新闻映射到 (Source → Firm → Signal) 三元组
  - Source 为媒体来源，Signal 为该篇新闻的情感/主题判断
- **可靠性加权基准 (Reliability-weighted Benchmark)**：
  - 不同信息源的可靠性通过历史准确率估计
  - 加权平均构建"真实信号"基准
  - 个别新闻与基准的偏差 = 该新闻的"错误信息含量"
- **多标签主题分类**：
  - 每篇新闻可同时属于多个主题 (earnings, M&A, governance...)
  - 使用 BERT-based 分类器生成多标签
- **关键启示**：
  - 实体提取不仅需要"该新闻提到了哪家公司"，还需要"该新闻在哪个主题维度上讨论了该公司"
  - 来源可靠性权重是情感测度精度的关键调节器

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 信息网络三元组 | 项目有 (source → bank → sentiment) 隐含映射 | ⚠️ 未显式建模 |
| **可靠性加权** | `42_panel_attention_media.py` 有 Holzman 媒体权威加权 | ✅ **功能等价** |
| 多标签主题分类 | 项目仅有 fintech/bank 二元标签 | 🟡 可扩展但非核心需求 |
| 错误信息检测 | 未实现 | ℹ️ 超出项目范围 |

### 2.4 Hassan, Hollander, van Lent & Tahoun (2024) — *Text as Data in Economic Analysis*

**核心方法论**：
- **文本即数据 (Text-as-Data) 综合框架**：
  - 系统化梳理"表示→预测→因果推断"三步走流程
  - 强调 **文档定义** (document definition) 对后续分析的根本性影响
  - PRisk/PSentiment 的方法论延伸讨论
- **关键最佳实践**：
  - 验证字典方法需要 Human Audit (手动审计)
  - 文档粒度选择需要做敏感性分析
  - 特征选择需要报告 TF-IDF 或 χ² 筛选标准

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Human Audit 验证 | `32_news_llms_human.py` + `33_news_llms_evaluation.py` | ✅ **完整实现** |
| 文档粒度敏感性 | `35_radius_sensitivity.py` 测试多个 radius | ✅ **完整实现** |
| 特征选择报告 | 关键词列表在 config JSON 中 | ⚠️ 建议补充筛选过程说明 |

### 2.5 Gentzkow, Kelly & Taddy (2019, JEL) — *Text as Data*

**核心方法论**：
- **表示-预测-因果推断 三步框架**：
  - Step 1：原始文本 D → 数值矩阵 C (bag-of-words, n-grams, tf-idf)
  - Step 2：C → 预测值 V̂ (词典法/回归/生成模型/深度学习)
  - Step 3：V̂ → 因果/描述分析
- **词典法的适用条件**：
  - 当缺乏训练数据、先验知识强时适用
  - 必须进行 **Manual Audit** 验证词典有效性 (Baker et al. 2016 的人工审计方案)
- **特征工程最佳实践**：
  - Stop words 移除需要应用特异性考量 (\"one researcher's stop words are another's subject of interest\")
  - n-gram 选择通常 2-3 阶最优
  - TF-IDF 平衡常见/罕见词
- **模型验证**：
  - 交叉验证 (K-fold CV) 作为 λ 选择标准
  - AICc/BIC 作为分析替代
  - Human Audit 始终必要

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 三步框架 (D→C→V̂) | 项目流水线完整遵循 | ✅ **完全一致** |
| Manual Audit 验证 | `32/33_news_llms_human/evaluation` | ✅ 完整 |
| TF-IDF 特征加权 | `22_tone_words.py` 的 `_idf_score` 列 | ✅ 已实现 |
| 词典适用性讨论 | 5本中文金融词典 + LLM 交叉验证 | ✅ **超越**单词典依赖 |
| 文档粒度敏感性 | `35_radius_sensitivity.py` | ✅ 完整 |
| N-gram 选择 | 关键词使用 unigram + 多词组 | ✅ 合理 |

### 2.6 Measuring Firm Exposure to Government Agencies (#97)

**核心方法论**：
- 在 Hassan et al. (2019) 框架基础上，将暴露度测度从"政治风险"扩展到"特定政府机构"
- 使用更细粒度的实体归因：不仅识别"是否提到政治风险"，还识别"与哪个具体机构相关"
- **多级实体层次结构**：总体 → 部门 → 具体机构

**项目对标**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 多级实体层次 | `bank_names.json` 含银行别名系统 | ⚠️ 深度不足 (缺乏银行类型/属性分类) |
| 部门级细分 | 未实现 | ℹ️ 可作为扩展 |

---

## 三、逐模块审计诊断

### 3.1 `utils/entity_context.py` — 实体特异性上下文提取引擎

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | Proximity-based Attribution | 句号边界分割 + ±N 句滑动窗口 | Hassan et al. (2019, QJE) §3 |
| 2 | 区间合并去重 | O(N log N) 排序 + 重叠区间合并 | 避免 Sautner (2023) 指出的双重计数 |
| 3 | 短文本退化处理 | <3句 → `fallback_char_radius=150` | **超越**原文 (Hassan 未讨论退化) |
| 4 | 参数敏感性外部验证 | `35_radius_sensitivity.py` 测试 radius=0,1,2,3 | Gentzkow et al. (2019, JEL) §3.4.2 |
| 5 | 实体遮蔽消融 | `36_entity_masking_test.py` | 标准消融实验设计 |
| 6 | 双轨 (full/ctx) 消融设计 | `21/22/23` 模块均生成 full/ctx 两组特征 | Hassan (2019): entity-specific vs whole-document |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| E1 | **均匀权重窗口 (无距离衰减)** | 🟡 中 | Sautner et al. (2023, JF) §2.2: 距离越远权重越低 | 添加可选的距离衰减函数 (如 `w(d) = 1/(1+d)` 或指数衰减) 作为稳健性变体 |
| E2 | **缺乏文档长度归一化** | 🟡 中 | Sautner et al. (2023): 用总对话长度归一化 | 项目下游在 Panel 聚合时通过 Fama-MacBeth z-score 隐式处理，可在文档中显式说明 |
| E3 | **未实现多实体竞争归因** | 🟡 中 | Fan et al. (2025): 同一段文本可能与多个实体相关 | 项目通过 `co_mentioned_banks` 记录共提及关系，但上下文窗口仍为独立提取。可在方法部分讨论 |
| E4 | **中文分句规则硬编码** | ⚪ 低 | 工程层面 | 当前实现 (句号/问号/叹号) 覆盖主要中文标点，可考虑添加分号/省略号作为次级边界 |

### 3.2 `11_news_bank.py` — 银行新闻分类与实体展开

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 高效字符串匹配 | Aho-Corasick 自动机 O(N) | 计算语言学标准 |
| 2 | 提早展开策略 | Phase 1 article→article×bank | Tetlock et al. (2008, JF): 先分后合 |
| 3 | 匹配位置记录 | `target_bank_in_title` 布尔列 | 用于 Bartik 稳健性子集 (标题匹配更相关) |
| 4 | 共提及关系记录 | `co_mentioned_banks` 分号分隔 | 用于 LOO-IV 和 Bartik 基期份额 |
| 5 | 别名系统 | `bank_names.json` 多变体 (全称/简称/英文/曾用名) | 避免遗漏 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| K1 | **缺乏显式学术引用** | 🟡 中 | 代码中未引用 Hassan (2019) 的 firm-level exposure 构建 | 在代码头部注释 + 论文方法部分添加引用 |
| K2 | **别名覆盖率未定量审计** | 🟡 中 | 缺乏"精确率-召回率"统计 | 抽样验证别名命中率：随机100条新闻 → 人工检查是否有遗漏/误匹配 |
| K3 | **标题匹配 vs 正文匹配未定量对比** | ⚪ 低 | Sautner (2023): 标题关键词权重应更高 | 报告标题匹配占比统计，作为描述性分析 |
| K4 | **缺乏银行属性元数据** | ⚪ 低 | Measuring Firm Exposure (#97): 多级实体层次 | `bank_names.json` 已有机构代码/类别，可扩展利用 |

### 3.3 `12_news_fintech.py` — 金融科技新闻判断

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 多条件筛选 (假阳性控制) | 关键词多样性 (≥3) + 上下半分布 | **创新设计**，文献未见类似方案 |
| 2 | 全量保存 (审计可追溯) | `12_fintech_news_full.parquet` | 支持 `51_falsification_test.py` |
| 3 | 外部独立验证 | `31_bank_fintech_threshold.py` 阈值敏感性 | Gentzkow et al. (2019): 参数敏感性检查 |
| 4 | 可配置阈值 | `SPLIT_RATIO`, `MIN_DISTINCT_KEYWORDS` 等 | 支持消融实验 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| F1 | **关键词选择过程未文档化** | 🟡 中 | Sautner (2023): Keyword Discovery Algorithm 系统化过程 | 在论文/技术文档中说明关键词的来源、筛选标准、迭代过程 |
| F2 | **缺乏显式学术引用** | 🟡 中 | 无 | 引用胡俊 et al. (2024, 中国管理科学)或相关金融科技分类文献 |
| F3 | **分布均匀性条件缺乏理论支撑** | 🟡 中 | Fan et al. (2025): 信息网络一致性验证 | 在方法部分提供"为何分布均匀性意味着更高的分类可靠性"的直觉解释 |
| F4 | **未利用 LLM 二阶段确认** | ⚪ 低 | de Kok (2024): LLM 作为 zero-shot 分类器 | 可将 LLM 作为第二阶段验证器，对关键词法筛出的结果进行确认 (可选扩展) |

### 3.4 `35_radius_sensitivity.py` — 窗口参数敏感性

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 多参数消融 | 测试 radius = 0, 1, 2, 3 | Hassan (2019): 默认±1句 |
| 2 | 独立验证模块 | 与 `entity_context.py` 解耦 | 可复现性最佳实践 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| R1 | **缺乏统计检验** | 🟡 中 | 需报告 radius 变化是否导致估计结果统计显著变化 | 添加跨 radius 的系数差异 Wald 检验 |
| R2 | **未测试字符级 radius** | ⚪ 低 | Sautner (2023): 使用基于字符距离的连续衰减 | 添加 char_radius = 100, 150, 200, 250 的消融 |

### 3.5 `36_entity_masking_test.py` — 实体遮蔽消融

#### ✅ 评价

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 实体替换实验 | 将目标银行名替换为占位符，检验情感是否变化 | 标准 NLP 消融设计 |
| 2 | 因果推断精神 | 检验情感分析是否真的依赖于实体信息 | Gentzkow (2019): 特征重要性验证 |

---

## 四、跨模块交互审计

### 4.1 `entity_context.py` → `21/22/23_tone_*.py` 数据流

```
11_news_bank.py  ──> article × bank 展开记录
                      │
                      ▼
entity_context.py ──> 提取 target_bank 的上下文窗口 (ctx)
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   21_tone_llms  22_tone_words  23_tone_berts
   (full + ctx)  (full + ctx)   (full + ctx)
          │           │           │
          └───────────┼───────────┘
                      ▼
            34_tone_validation (三角验证)
                      │
                      ▼
            45_panel_export_main (聚合入口, 编排 41→42→43→44→45)
```

**审计发现**：

| # | 交互点 | 状态 | 观察 |
|---|-------|------|------|
| I1 | ctx 窗口向情感模块传递 | ✅ | 双轨设计确保 full/ctx 对比可行 |
| I2 | 共提及银行向 Panel 传递 | ✅ | `co_mentioned_banks` 用于 Bartik IV 基期份额 |
| I3 | 标题匹配布尔列向 Panel 传递 | ✅ | `target_bank_in_title` 用于稳健性子集 |
| I4 | 窗口参数一致性 | ⚠️ | 需确认 21/22/23 模块是否使用相同的 `sentence_radius` 默认值 |

### 4.2 信息损失分析

| 环节 | 可能的信息损失 | 严重程度 | 文献参照 |
|------|-------------|---------|---------|
| 中文分句 | 省略号、分号后的文本可能被截断 | ⚪ 低 | entity_context.py E4 |
| ±1句窗口 | 距离>1的相关上下文被截断 | 🟡 中 | 35_radius_sensitivity 已覆盖 |
| 均匀权重 | 临近句 vs 远距句的重要性被等同化 | 🟡 中 | Sautner (2023) E1 |
| 二元分类 | fintech 判断为 0/1，丢失"相关程度"信息 | ⚪ 低 | 可接受的设计简化 |

---

## 五、优先级排序矩阵

| 优先级 | ID | 差距描述 | 影响面 | 实施难度 | 建议动作 |
|-------|-----|---------|---------|---------|---------|
| P1 | K1/F2 | 模块缺乏显式学术引用 | 全局 | 🟢 低 | **立即实施**: 在 `11_news_bank.py` 和 `12_news_fintech.py` 头部添加学术引用注释 |
| P2 | F1 | 关键词选择过程缺乏文档化 | 方法论 | 🟢 低 | **短期实施**: 在技术文档/论文方法部分补充关键词来源与筛选说明 |
| P3 | E1 | 距离衰减加权 (可选稳健性) | 上下文 | 🟡 中 | **中期实施**: 在 `entity_context.py` 添加 `decay_function` 可选参数 |
| P4 | K2 | 别名覆盖率定量审计 | 分类 | 🟡 中 | **短期实施**: 抽样100条新闻 → 精确率/召回率报告 |
| P5 | F3 | 分布均匀性条件的理论解释 | 分类 | 🟢 低 | **论文补充**: 在方法部分添加直觉性解释 |
| P6 | E3 | 多实体竞争归因讨论 | 上下文 | 🟡 中 | **论文讨论**: 在 limitation 部分说明共提及情况的处理方式 |
| P7 | R1 | 窗口参数统计检验 | 验证 | 🟡 中 | **中期实施**: 在 `35_radius_sensitivity.py` 添加 Wald 系数差异检验 |
| P8 | F4 | LLM 二阶段确认 | 分类 | 🔴 高 | **可选扩展**: 非核心，可作为 future work |

---

## 六、文献覆盖矩阵

| 文献 | 项目引用 | 方法采纳 | 差距等级 |
|-----|---------|---------|---------|
| Hassan et al. (2019, QJE) | ✅ 显式 (entity_context.py L32, 51_falsification.py L11) | ✅ **完整** (proximity-based attribution + PRisk/NPRisk) | ✅ |
| Sautner et al. (2023, JF) | 未引用 | **部分** (proximity 窗口，但无距离衰减) | 🟡 |
| Fan et al. (2025, ManSci) | 未引用 | **隐含** (媒体权威加权 ≈ 可靠性权重) | 🟡 |
| Hassan et al. (2024) Text-as-Data | 未引用 | ✅ 隐含遵循 (human audit, 文档粒度敏感性) | ✅ |
| Gentzkow, Kelly & Taddy (2019, JEL) | ✅ 显式 (45_panel_export.py L521) | ✅ **完整** (IDF加权, 三步框架) | ✅ |
| Measuring Firm Exposure (#97) | 未引用 | **部分** (单级实体，无多级层次) | ⚪ |

---

## 七、与 Batch 3.1 (情感分析) 的交叉依赖

| 交叉点 | 3.1 发现 | 3.2 影响 | 联合建议 |
|--------|---------|---------|---------|
| Dirichlet 校准 (S3/V1) | 🔴 关键差距 | E1 距离衰减可能改变校准基准 | 先实施 S3/V1，再实施 E1 |
| LLM 温度锁定 (S1) | 🟡 中 | 不影响 3.2 | 独立解决 |
| Topic-Level 分解 (V4) | 🟡 中 | F3 分类精度影响分解维度 | 先解决 F1/F3，再扩展 V4 |
| 5-point Likert (S2) | 🟡 中 | ctx 窗口长度影响 Likert 判断 | 独立实施 |

---

## 八、Batch 3.2 审计结论

### 整体评分：**A- / B+**

**优势**：
- `entity_context.py` 的 proximity-based attribution 与 Hassan et al. (2019, QJE) **完全一致**，是项目方法论最强锚点
- 双轨 (full/ctx) 消融设计在同类研究中**极为罕见**，是显著创新
- `51_falsification_test.py` 完整实现了 PRisk vs NPRisk 伪造检验，达到 QJE 级别验证标准
- 验证模块群 (35/36/37) 提供了三层消融：参数敏感性 + 实体遮蔽 + 词典覆盖率

**弱点**：
- **引用缺失**是最大的"纸面漏洞"：代码实现对标了核心文献，但 `11_news_bank.py` 和 `12_news_fintech.py` 未在代码中显式引用
- Sautner et al. (2023) 的距离衰减权重是一个**可选但有价值**的稳健性扩展
- 关键词选择过程的文档化不足，可能引发 Reviewer 对"为何选这些关键词"的质疑
- 别名系统的精确率-召回率缺乏定量报告

**升级至 A 级所需**：
1. 在 `11_news_bank.py` 和 `12_news_fintech.py` 顶部添加学术方法论引用注释
2. 为 `12_news_fintech.py` 的关键词列表补充来源说明 (种子词来源 → 筛选标准 → 最终词典)
3. 在 `entity_context.py` 添加可选的距离衰减函数作为稳健性变体
4. 对别名系统进行抽样精确率/召回率审计并报告结果

---

## 附录：Phase 3.2 精读文献清单

| # | 文献 | 精读深度 | 关键贡献 |
|---|------|---------|---------|
| 1 | Hassan et al. (2019, QJE) | ★★★★★ | Proximity-based attribution 基准方法 |
| 2 | Sautner et al. (2023, JF) | ★★★★★ | 距离衰减 + 演进式词典构建 |
| 3 | Fan et al. (2025, ManSci) | ★★★★★ | 信息网络 + 可靠性加权 |
| 4 | Hassan et al. (2024) | ★★★★ | Text-as-Data 综合框架 |
| 5 | Gentzkow, Kelly & Taddy (2019, JEL) | ★★★★ | D→C→V̂ 三步框架 + 验证范式 |
| 6 | Measuring Firm Exposure (#97) | ★★★ | 多级实体暴露度扩展 |
