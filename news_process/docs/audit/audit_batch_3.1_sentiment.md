# Batch 3.1 审计报告：情感分析方法论

> **审计范围**：`21_tone_llms.py` | `22_tone_words.py` | `23_tone_berts.py` | `34_tone_validation.py`
> **对标文献**：28篇 (A类) + 24篇 (G类·ML/NLP)
> **生成时间**：2026-04-06
> **审计等级**：深度模式 (Full-text Analysis)

---

## 一、审计目标

验证项目的"三方法×双轨"(Three-Method × Dual-Track) 情感分析框架是否满足顶级金融期刊 (JF/RFS/TAR) 的方法论要求，识别实现缺口，提出优先级排序的改进建议。

---

## 二、核心文献精读摘要

### 2.1 Lopez-Lira & Tang (2025, JF) — *Can ChatGPT Forecast Stock Price Movements?*

**核心发现**：
- GPT-4 对隔夜新闻的初始反应命中率达 **93.3%**，漂移策略年化 Sharpe Ratio = **2.97**
- **模型复杂度阈值效应**：GPT-1/GPT-2/BERT 基本无预测力 (Sharpe < 0)；GPT-3.5 中等 (SR=1.66)；GPT-4 最优
- **Topic Decomposition**：市场对盈余报告类高效吸收 (无漂移)，对内部人交易类系统性反应不足 (显著漂移)
- **效率衰减**：策略 Sharpe 从 2021Q4 的 6.54 降至 2024H1 的 1.22，与 LLM 普及一致

**项目启示**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| 三分类 (YES/NO/UNKNOWN) + 置信度 | 三分类 + confidence | ✅ 一致 |
| Prompt 含角色设定 + 公司名称锚点 | 已实现 entity-specific prompt | ✅ 一致 |
| 温度=0 以保证可复现性 | 未见温度参数显式设定 | ⚠️ 需确认 |
| 12个模型对比层级 | 3个LLM + 5个BERT + 5个词典 = 13 | ✅ **超越** |
| RavenPack 传统情感被 GPT-4 吸收 | 词典法作为独立方法保留 | ✅ 互补设计 |
| Fama-French 5因子 Alpha | Panel 导出已有标准化但无FF5 | ⚠️ 需下游验证 |

### 2.2 Chiu & Hung (2024, IRFA) — *Finance-specific LLMs: Advancing Sentiment with LLaMA 2*

**核心发现**：
- **AI驱动两步摘要法** (LongT5)：MD&A 全文→0.72%压缩率，解决 LLM 输入长度限制
- **Dirichlet 贝叶斯后验**：通过迭代采样 (500样本/批次) 估计模型在三分类上的概率分布
- **5个训练轮次变体** (E1-E5)：E5 最优，年化 BHR = 12.37% vs FinBERT 5.98%
- **金融动荡期鲁棒性**：LLaMA-2 在 2000-2009 期间仍显著，FinBERT 退化

**项目启示**：
| 文献要点 | 项目现状 | 差距程度 |
|---------|---------|---------|
| Dirichlet 后验概率估计 | `34_tone_validation.py` 引用但**降级为描述性统计** | 🔴 关键差距 |
| 两步摘要预处理 | 项目使用 `entity_context.py` 的句级上下文窗口 | ⚠️ 不同技术路径，可接受 |
| 5个训练epoch变体消融 | 未进行LLM微调 (使用API推理) | ℹ️ 设计取舍 |
| BHR + CAR 双重验证 | 项目面板支持回归，无BHR策略回测 | ⚠️ 下游分析 |
| 金融动荡期子样本分析 | 未见时期分层 | ⚠️ 可加入 Panel 稳健性 |

---

## 三、逐模块审计诊断

### 3.1 `21_tone_llms.py` — LLM 情感分析模块

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 多模型投票机制 | `majority_vote()` 多数投票 + `agreement_rate` | Lopez-Lira (2025) Table 5 模型对比 |
| 2 | 双轨 (full/ctx) 消融 | 每条新闻生成 full/ctx 两组特征 | Hassan et al. (2019) entity-specific |
| 3 | 公司名称锚定 Prompt | Prompt 含 `{bank_name}` 占位符 | Lopez-Lira (2025) §5 |
| 4 | 连续置信度编码 | `cont = direction × confidence` | Chiu & Hung (2024) Bayesian |
| 5 | 一致率诊断 | `agreement_rate` 跨模型一致性 | Carlson & Burbano (2026, SMJ) |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| S1 | **LLM 温度参数未显式锁定** | 🟡 中 | Lopez-Lira (2025) §5: "temperature=0 for reproducibility" | 在 config 中显式设定 `temperature=0.0` 并在论文方法部分说明 |
| S2 | **三分类 vs 五分类 Likert 未讨论** | 🟡 中 | 多篇文献使用 5-point (strong pos/pos/neutral/neg/strong neg) | 作为稳健性检验添加 5-point 变体 (39_prompt_sensitivity 可扩展) |
| S3 | **Dirichlet 概率校准降级** | 🔴 高 | Chiu & Hung (2024, IRFA) §2.1: empirically-driven Dirichlet Bayesian | 实现完整 Dirichlet 后验估计，产出分类概率分布图 |
| S4 | **缺乏 LLM 时间衰减分析** | 🟡 中 | Lopez-Lira (2025) §8.2: Sharpe 从 6.54→1.22 | 添加年度/季度子样本分析至 Panel 稳健性 |
| S5 | **Prompt 消融不充分** | 🟡 中 | Lopez-Lira (2025) Appendix C: 12种不同 Prompt | 39_prompt_sensitivity 可扩展更多变体 |

### 3.2 `22_tone_words.py` — 词典法情感分析模块

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 多词典交叉验证 | 5本中文金融词典 (蒋/姚/卞/杜/尤) | Loughran & McDonald (2016, JAR) |
| 2 | 语言规则增强 | 否定词翻转 + 程度词加权 + 转折词 | 超越 LM 原始方法 |
| 3 | IDF 加权变体 | `_idf_score` 列 | Gentzkow, Kelly & Taddy (2019, JEL) |
| 4 | 双轨 (full/ctx) | 与 LLM 模块一致 | Hassan (2019) |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| D1 | **未实现 SentimentR 连续情感度量** | 🟡 中 | Ke, Kelly & Xiu (2020, RFS): 每个词的边际情感贡献 | 技术难度高，可作为"未来研究方向"在论文中讨论 |
| D2 | **词典 domain adaptation 缺失** | 🟡 中 | Rizinski et al. (2024): domain-specific dictionary refinement | 利用 LLM 辅助扩展词典 (可行性高) |
| D3 | **词频倒排索引优化** | ⚪ 低 | 工程优化，非学术差距 | 当前性能足够 |

### 3.3 `23_tone_berts.py` — BERT 情感分析模块

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | 多模型集成 | 5个 BERT 模型 | Lopez-Lira (2025) Table 5 |
| 2 | 滑动窗口推理 | 超512 token 自动分割 | Chiu & Hung (2024): LongT5 也面临此问题 |
| 3 | 置信度加权池化 | 按模型置信度加权合并 | 学术标准实践 |
| 4 | AMP 混合精度 | GPU 加速 | 工程最佳实践 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| B1 | **无 temporal drift 监控** | 🟡 中 | Anis et al. (2024): 预训练模型时效性退化 | 添加分年份准确率追踪 (与 34_tone_validation 集成) |
| B2 | **无 fine-tuning 路径** | ⚪ 低 | Chiu & Hung (2024): LLaMA-2 fine-tune 显著优于 FinBERT | 设计取舍：使用预训练推理降低复杂度，可接受 |
| B3 | **label_map 自动检测未文档化** | ⚪ 低 | — | 添加代码注释说明自动检测逻辑 |

### 3.4 `34_tone_validation.py` — 三角验证模块

#### ✅ 已对标的文献最佳实践

| # | 最佳实践 | 实现方式 | 学术支撑 |
|---|---------|---------|---------|
| 1 | Cronbach's Alpha 内部一致性 | 三方法聚合度量 | Loughran & McDonald (2016, JAR) |
| 2 | Spearman 秩相关 | 跨方法排序一致性 | 标准心理测量实践 |
| 3 | LLM 置信度校准引用 | 引用 Chiu & Hung (2024) 和 ECE | ✅ 学术意识正确 |
| 4 | Cohen's Kappa | 评分者间一致性 | 标准分类验证 |

#### 🔴 识别的方法论差距

| # | 差距 | 严重等级 | 文献依据 | 修复建议 |
|---|-----|---------|---------|---------|
| V1 | **Dirichlet 校准降级为描述性** | 🔴 高 | Chiu & Hung (2024) §2.1: Bayesian update with Dirichlet prior | 实现完整迭代采样 → 后验分布图 |
| V2 | **ECE (Expected Calibration Error) 未实现** | 🟡 中 | 标准校准度量 | 添加 reliability diagram + ECE/MCE 计算 |
| V3 | **缺乏 McNemar 检验** | 🟡 中 | 统计显著性检验标准 | 添加成对方法显著性检验 |
| V4 | **缺乏 Topic-Level 分解** | 🟡 中 | Lopez-Lira (2025) Table 4: 按新闻类型分析准确率 | 按新闻来源/主题细分验证结果 |

---

## 四、优先级排序矩阵

| 优先级 | ID | 差距描述 | 影响面 | 实施难度 | 建议动作 |
|-------|-----|---------|-------|---------|---------|
| P1 | S3/V1 | Dirichlet 概率校准完整实现 | 全局 | 🟡 中 | **立即实施**: 在 `34_tone_validation.py` 添加 Dirichlet 后验模块 |
| P2 | V2 | ECE/Reliability Diagram | 验证 | 🟢 低 | **短期实施**: 添加校准图表生成函数 |
| P3 | S1 | LLM 温度参数显式锁定 | LLM | 🟢 低 | **立即确认**: 检查 API 调用是否已设 temperature=0 |
| P4 | S4 | 时间衰减分析 | 面板 | 🟡 中 | **中期实施**: Panel 增加年度子样本回归 |
| P5 | S2 | 5-point Likert 消融 | Prompt | 🟡 中 | **中期实施**: 扩展 39_prompt_sensitivity |
| P6 | V3 | McNemar 检验 | 验证 | 🟢 低 | **短期实施**: 添加成对检验 |
| P7 | D1 | SentimentR 连续度量 | 词典 | 🔴 高 | **论文讨论**: 作为 limitation/future work |
| P8 | B1 | BERT temporal drift | BERT | 🟡 中 | **中期实施**: 分年份准确率追踪 |

---

## 五、关键建议总结

### 5.1 必须修复 (Reviewer 大概率提出)

1. **Dirichlet 概率校准** (P1): 项目已引用 Chiu & Hung (2024) 但仅实现了描述性统计。审稿人会问："你引用了 Dirichlet 校准，具体如何实现的？" 需要：
   - 实现迭代采样 (≥500样本/批) → Dirichlet 后验更新
   - 产出三分类后验概率分布密度图 (类似 Chiu Fig.2)
   - ECE + Reliability Diagram 作为附录

2. **LLM 可复现性** (P3): Lopez-Lira (2025) 显式说明 temperature=0。项目需：
   - 确认所有 LLM API 调用的温度设置
   - 在方法部分说明随机种子/模型版本锁定

### 5.2 显著增值 (区分度提升)

3. **Topic-Level 分解** (V4): Lopez-Lira (2025) 通过 BERTopic 分解发现市场对不同主题的反应速度差异巨大。项目可：
   - 对银行新闻按来源类型（央媒/财经/地方）分层验证
   - 检验情感准确率是否因新闻来源而异

4. **时间衰减分析** (S4): 添加分年份/分时段面板回归，检验情感信号是否存在效率衰减

### 5.3 可作为论文 Limitation 讨论

5. **SentimentR** (D1): Ke-Kelly-Xiu (2020) 的连续情感方法需要训练数据，与项目的事后零样本推理路线不同
6. **BERT Fine-tuning** (B2): 项目选择多模型集成推理而非单模型微调，这是合理的设计取舍

---

## 六、文献覆盖矩阵

| 文献 | 项目引用 | 方法采纳 | 差距等级 |
|-----|---------|---------|---------|
| Lopez-Lira & Tang (2025, JF) | 隐含 | 部分 (多模型对比) | 🟡 |
| Chiu & Hung (2024, IRFA) | ✅ 显式 | 部分 (Dirichlet降级) | 🔴 |
| Tetlock (2007, JF) | ✅ 显式 | ✅ 完整 (词频范式) | ✅ |
| Tetlock et al. (2008, JF) | ✅ 显式 | ✅ 完整 (聚合范式) | ✅ |
| Loughran & McDonald (2016, JAR) | ✅ 显式 | ✅ 完整 (多度量) | ✅ |
| Gentzkow, Kelly & Taddy (2019, JEL) | ✅ 显式 | ✅ 完整 (IDF加权) | ✅ |
| Carlson & Burbano (2026, SMJ) | ✅ 显式 | ✅ 完整 (LLM注释) | ✅ |
| Ke, Kelly & Xiu (2020, RFS) | 未引用 | 未采纳 | 🟡 论文讨论即可 |
| Huang et al. (2023) FinBERT | 隐含 | ✅ 部分 (5模型之一) | ✅ |
| Hassan et al. (2019, QJE) | ✅ 显式 | ✅ 完整 (实体上下文) | ✅ |

---

## 七、Batch 3.1 审计结论

### 整体评分：**B+ / A-**

**优势**：
- "三方法×双轨"框架的消融设计 **超过** 大多数单方法金融情感文献
- 13个模型/词典的覆盖面 **对标** Lopez-Lira (2025) 的12模型对比
- 实体特异性上下文提取 (ctx轨) 是 **创新点**，文献中少见

**弱点**：
- Dirichlet 校准的 **引而不实** 是最大方法论漏洞
- 验证框架缺乏概率校准的定量指标 (ECE/MCE)
- 时间维度分析 (信号衰减、模型时效性) 缺失

**升级至 A 级所需**：
1. 实现 Dirichlet Bayesian 校准 → 后验概率分布
2. 添加 ECE + Reliability Diagram
3. 确认并锁定 LLM 温度/随机种子参数
4. 添加至少一项 Topic-Level 或 Time-Series 分层验证
