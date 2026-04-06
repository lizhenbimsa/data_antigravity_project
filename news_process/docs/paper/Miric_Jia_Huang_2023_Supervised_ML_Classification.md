# 基于参考论文的项目分析与执行计划

> **参考论文**: Miric, M., Jia, N., & Huang, K. G. (2023). "Using supervised machine learning for large-scale classification in management research: The case for identifying artificial intelligence patents." *Strategic Management Journal*, 44(2), 491–519.
>
> **当前项目**: `news_process` — 银行金融科技新闻语义分类与情感分析流水线

---

# 第一部分：基于参考论文的项目分析与诊断报告

## 1. 范式映射与盲区诊断

### 1.1 论文核心机制提炼

Miric et al. (2023) 的核心方法论框架由四个关键支柱构成：

| 维度 | 论文核心主张 | 论文依据 |
|------|------------|---------|
| **分类范式选择** | 关键词法 (Keyword-based) vs 有监督 ML 法各有适用场景；当**词典难以穷举、语义存在歧义**时，ML 法显著优于关键词法 | Table 2; §2.2; F1 差异约 10% (Table 3) |
| **训练数据构建** | 训练集需通过**主动学习 (Active Learning)** 平衡类别分布，并做三项诊断：**充分性 (Size)、平衡性 (Balance)、代表性 (Representativeness)** | §4.2.1; Online Appendix A |
| **多模型竞赛** | 不可先验预判最优模型，必须系统性测试 多种 ML 分类器 + 多种文本表示（BoW、Embedding、Transformer），以 **k-fold 交叉验证** 的 F1/AUC 为基准选优 | §4.2.3; Table 3 (14 个模型比较) |
| **可解释性** | 使用 **Feature Importance** 回溯分类逻辑，揭示"哪些文本特征驱动了分类决策"，对冲"黑箱"批评 | §6.1; Figure 1 & 2 |

### 1.2 项目现状范式诊断

**当前项目的核心分类架构**：

```
阶段 11 (银行新闻分类)  →  关键词法 (Aho-Corasick 确定性匹配)
阶段 12 (金融科技新闻分类) →  关键词法 (Aho-Corasick + 多样性阈值)
阶段 21 (LLM 语义精筛)  →  多模型 LLM 多数投票 (GPT-5 Nano / Gemini 3 / GLM-4.5)
```

**精准落差识别**:

| 落差维度 | 当前项目状态 | 论文对标 | 严重程度 |
|---------|------------|---------|---------|
| **① 分类方法验证缺口** | 阶段 11/12 纯关键词法，**无 ML 基准对照** | 论文 Table 3 明确要求 keyword vs ML 的量化比较 | 🔴 **高** |
| **② 训练数据质证缺失** | 阶段 32 生成人工验证样本，但未做 Active Learning 三诊断（Size/Balance/Representativeness） | 论文 §4.2.1 mandatory | 🟡 **中** |
| **③ 多模型竞赛未覆盖传统 ML** | 仅 LLM 三角验证（3 个 LLM），未测试 Random Forest / SVM / BERT fine-tuning 等经典分类器 | 论文 Table 3 含 14 个模型横向比较 | 🟡 **中** |
| **④ Feature Importance 可解释性缺失** | 无分类特征权重分析、无"哪些关键词驱动分类"的回溯 | 论文 §6.1, Figure 1 & 2 | 🟡 **中** |

### 1.3 关键判断——哪些落差值得修补？

> **核心论点**: 本项目的分类对象是"银行金融科技相关新闻"，这是一个**语义边界模糊、词典难以穷举**的分类任务（例如"数字人民币"、"智能风控"等新兴术语不断涌现），**完全满足论文提出的"ML 优于 Keyword"的前提条件**。

- **落差①** 是最大的方法论风险点：审稿人有极高概率要求补充"关键词法 vs ML 法"的量化对比实验，以证明当前关键词法的准确性不逊于 ML 法，或反之证明应切换至 ML 法。
- **落差②③④** 属于增量改进，边际收益递减，可视工期弹性决定是否实施。

---

## 2. 实质性改进项

### 改进 A：构建"关键词法 vs 有监督 ML 法"对照实验框架

- **具体修改建议**: 新增 `13_classification_benchmark.py` 模块，在阶段 32 的人工验证 Ground Truth 上，系统性测试关键词法与至少 3 种 ML 分类器（Random Forest + BERT/RoBERTa fine-tuning + LLM zero-shot）的 Precision/Recall/F1/AUC 性能。
- **论文依据**: Table 3 (14 模型竞赛) + §5.2 (keyword vs ML 量化比较)
- **预期边际贡献**:
  - 若 ML 法显著优于关键词法 → 直接升级主流程分类器，提升分类准确性
  - 若关键词法与 ML 法持平 → 证明当前设计的合理性，用论文范式和量化证据回应审稿人
  - 无论哪种结果，**模型竞赛本身就是方法论贡献**，符合 SMJ 对 benchmark 实验的期待
  - 解决"关键词法效度未经量化验证"的内生性问题

### 改进 B：训练数据质量三诊断报告

- **具体修改建议**: 在 `33_news_llms_evaluation.py` 中新增三项诊断：① Learning Rate Curve (样本量 vs F1)；② Class Balance Distribution 可视化；③ 训练集与总体的特征分布代表性检验 (KS test)。
- **论文依据**: §4.2.1 + Online Appendix A.1/A.2/A.3
- **预期边际贡献**: 证明人工编码样本的 1000 条数据在大小、类别分布和特征代表性上均满足统计要求，堵住审稿人对"样本是否充分/有偏"的质疑通道。

### 改进 C：Feature Importance 可解释性分析

- **具体修改建议**: 在 Benchmark 模块中嵌入 Random Forest Feature Importance 和 SHAP 分析，输出"驱动金融科技分类的 Top-20 特征词"，与当前 `fintech_dict.json` 词典进行交叉比对。
- **论文依据**: §6.1, Figure 1 & 2
- **预期边际贡献**: ① 验证词典覆盖率——是否有高预测力的特征词未被词典收录；② 发现"伪需求词"——词典中哪些词预测力极低、可以安全剔除；③ 形成"ML 辅助的词典迭代优化"方法论创新点。

---

## 3. 冗余剥离

经审查，当前项目中**不存在需要剔除的冗余模块**。理由：

- `22_tone_words.py` / `23_tone_berts.py` 作为词典法和 BERT 情感分析方法，与 LLM 情感分析共同构成**三角验证**，这恰好是论文所倡导的"多方法交叉验证"精神（Table 3 多模型竞赛思路的情感分析延伸）。
- `31_bank_fintech_threshold.py` 的阈值敏感性分析和 `37_dict_coverage_audit.py` 的词典覆盖率审计，直接对标论文 §7.1 对"参数稳健性"和"词典完整性"的要求。
- `36_entity_masking_test.py` 和 `39_prompt_sensitivity.py` 虽不在论文范围内，但对标 Carlson & Burbano (2026, SMJ) 等更新文献，属于**独立创新模块**，维持原状。

**结论: 维持全部现有模块，无需剔除。**

---

# 第二部分：项目重构与优化执行计划书

## 1. 优先级排布

| 优先级 | 改进项 | 类型 | 实施成本 | 预期收益 | 理由 |
|--------|-------|------|---------|---------|------|
| **P0** | 改进 A: Keyword vs ML 对照实验 | 核心攻坚 | 高（需构建训练集 + 训练多模型） | **极高**（堵住审稿人最大攻击面） | 论文最核心贡献，是否被接受的关键 |
| **P1** | 改进 C: Feature Importance 可解释性 | 速赢 (Quick Win) | 低（Random Forest 端输出即可） | **高**（验证词典 + 揭示分类逻辑） | 改进 A 的自然附产品 |
| **P2** | 改进 B: 训练数据三诊断 | 速赢 (Quick Win) | 低（现有数据的统计分析） | **中**（方法论完备性加分项） | 对现有评估框架的增量扩展 |

---

## 2. 阶段化执行指令 (SOP)

### 阶段一：训练数据准备与质量诊断（改进 B 前置部分）

**核心动作指令**:

1. **人工验证数据升级**：确认阶段 32 的 `32_human_samples.xlsx` 已完成人工编码（`最终_验证` 列和 `最终_情感` 列），作为 Ground Truth。若未完成，需优先执行人工编码。

2. **补充正负样本平衡**：当前人工编码样本 1000 条中，若金融科技新闻（正例）占比低于 20%，需通过 Active Learning 策略增量采样正例至 ≥ 20% 占比：
   - 使用现有 LLM 预测在**低置信度区间** (`verification_confidence ∈ [0.4, 0.7]`) 中随机采样追加
   - 追加样本的人工编码仅需标注 `验证` 和 `情感` 两列

3. **三诊断报告生成**：在 `33_news_llms_evaluation.py` 中新增 `diagnose_training_data()` 函数：
   - **Size 诊断**: 绘制 Learning Rate Curve — 以 [100, 200, 300, ..., 1000] 步长递增训练集大小，记录每步的 5-fold CV F1，观察是否进入"平台期"
   - **Balance 诊断**: 输出正负样本比例 + 各情感类别分布
   - **Representativeness 诊断**: 对训练集与总体（阶段 12 全量）进行 KS 检验，比较文本长度、关键词密度等特征分布

**交付物**:
- `data_processed/eval_reports/training_data_diagnostics.csv`
- `data_processed/eval_reports/learning_rate_curve.png`
- `data_processed/eval_reports/class_balance_distribution.png`

---

### 阶段二：分类模型竞赛与 Benchmark（改进 A + C 核心部分）

**核心动作指令**:

1. **新增 `13_classification_benchmark.py`**:
   - 读取 Ground Truth（阶段 32 人工验证数据 + 阶段 21 的 LLM 预测 + 阶段 12 的关键词法预测）
   - 构建文本特征表示：
     - **BoW**: TF-IDF (bigram, max_features=10000) — 对标论文 Random Forest + BoW 路线
     - **Embedding**: 使用 `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` 中文嵌入
   - 训练并评估以下分类器（5-fold CV）：
     - (a) **Random Forest** (BoW) — 论文最佳模型，F1=0.90
     - (b) **Logistic Regression** (BoW) — 基线对照
     - (c) **SVM with RBF Kernel** (BoW) — 论文 Row 7
     - (d) **BERT/RoBERTa fine-tuning** (Embedding) — 论文 Row 5/8，需 GPU
     - (e) **LLM zero-shot** (现有三模型投票) — 提取现有结果即可
     - (f) **关键词法** (Aho-Corasick 现有逻辑) — 提取阶段 12 结果
   - 输出: Table 3 风格的完整比较表（Accuracy / Precision / Recall / F1 / AUC / False Positive Rate）

2. **Feature Importance 分析**（改进 C，嵌入步骤 1 的 Random Forest 输出）：
   - 提取 Random Forest 的 Top-20 Feature Importance bigrams
   - 与 `config/fintech_dict.json` 词典进行交叉比对：
     - 高权重 + 在词典中 → 验证词典覆盖
     - 高权重 + 不在词典中 → **候选新增词汇**
     - 在词典中 + 低权重 → **候选剔除词汇**
   - 输出: Figure 1 & 2 风格的特征权重柱状图

3. **McNemar 检验**：
   - 对关键词法 vs 最佳 ML 模型执行 McNemar 卡方检验（论文 §5.2 的精神延伸）
   - 检验两种分类器在边缘样本上的差异是否具有统计显著性

**交付物**:
- `data_processed/eval_reports/classification_benchmark_table.csv` — 模型竞赛结果表
- `data_processed/eval_reports/classification_benchmark_table.tex` — LaTeX 版
- `data_processed/eval_reports/feature_importance_top20.png` — 特征权重图
- `data_processed/eval_reports/feature_importance_vs_dict.csv` — 词典交叉比对
- `data_processed/eval_reports/mcnemar_keyword_vs_ml.json` — McNemar 检验结果

**稳健性检验标准**:
- 关键词法 F1 ≥ 0.80 → 当前设计可维持，Benchmark 作为方法论验证
- 关键词法 F1 < 0.80 且 ML 法 F1 > 0.85 → 建议升级至 ML 分类器
- 所有模型 F1 < 0.75 → 需重新检查训练数据质量和标注一致性

---

### 阶段三：结论重构

**核心动作指令**:

1. **方法论贡献点重写**：
   - 将 Benchmark 实验的结果纳入论文方法论章节：
     - 若关键词法通过 Benchmark 验证 → 论述"我们通过 Miric et al. (2023) 的系统性 ML 竞赛框架验证了关键词法在本场景中的有效性（F1=X.XX），证明其准确性不逊于有监督 ML 分类器"
     - 若 ML 法胜出 → 论述"我们遵循 Miric et al. (2023) 的最佳实践，通过 14 模型竞赛发现 [最优模型] 显著优于传统关键词法，据此升级分类流程"
   
2. **Feature Importance 洞见**：
   - 报告"驱动金融科技分类的 Top 特征词"分析，作为对金融科技概念边界的实证贡献
   - 与论文 §6.1 的"AI 专利特征词"分析形成对仗

3. **更新 LaTeX 表格**：
   - 新增 Table: "Classification Method Comparison"（对标论文 Table 3）
   - 新增 Figure: "Feature Importance for FinTech Classification"（对标论文 Figure 1）

---

## 3. 风险预案 (Plan B)

### 风险一：训练数据不足（人工验证样本 < 500 条可用）

- **预案**: 采用 Semi-supervised Learning 扩展训练集——使用现有高置信度 LLM 标注 (`llm_agreement_rate_full ≥ 1.0` 且 `verification_confidence ≥ 0.95`) 作为"银标准"伪标签，与人工黄金标准混合训练
- **适用条件**: 高置信度样本 ≥ 3000 条
- **学术依据**: 论文 §4.2.1 Active Learning 策略的泛化

### 风险二：GPU 资源不足（无法 fine-tune BERT/RoBERTa）

- **预案**: 放弃 fine-tuning 路线，改用：
  - (a) Sentence-BERT embedding + Logistic Regression（零 GPU 需求）
  - (b) 仅保留 Random Forest (BoW) + LLM zero-shot 的对照
- **代价**: 丧失 Transformer 类模型的比较数据，但不影响核心方法论贡献
- **学术依据**: 论文 Table 3 中 Random Forest (BoW) 是最佳模型，证明 BoW 路线在特定场景中可媲美 Transformer

### 风险三：关键词法 F1 显著低于 ML 法（F1 差距 > 15%）

- **预案**: 不急于替换主流水线，而是：
  - (a) 将 ML 分类器的分类结果作为**稳健性检验变量** (`is_fintech_ml`)
  - (b) 在面板回归中同时报告关键词法和 ML 法样本的估计系数，证明核心发现不受分类方法影响
  - (c) 在修改稿中使用 ML 法作为主分类器，关键词法降级为对照
- **学术依据**: 论文 §7.1 "supervised ML methods allow us to generate a quantifiable measure of the degree of error"

### 风险四：LLM zero-shot 与人工标注一致性低（Kappa < 0.60）

- **预案**: 
  - (a) 诊断不一致模式——是否集中在特定银行/时间段/文章长度
  - (b) 若系统性偏差可识别 → 调整 Prompt 模板后重新运行少量样本
  - (c) 若随机噪声 → 增加 LLM 模型数（从 3 扩展到 5），提升多数投票的鲁棒性
- **学术依据**: 论文 §4.2.1 Active Learning 迭代 + Carlson & Burbano (2026) §3.5 Prompt Sensitivity

---

> **执行纪律**: 本计划按 P0 → P1 → P2 优先级严格排序。阶段一（训练数据准备）是阶段二（模型竞赛）的硬性前置依赖。若工期受限，P1 (Feature Importance) 可作为 P0 的附产品零成本获取，P2 (训练数据三诊断) 可精简为仅输出 Class Balance 分布图。
