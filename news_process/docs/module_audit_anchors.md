# 模块审计锚点矩阵 (Module Audit Anchors)

> Phase 2 产出：逐模块代码精读后提取的审计锚点
> 生成时间：2026-04-06
> 覆盖范围：13个核心模块 + 7个验证模块 + utils

---

## 一、模块架构总览

```
数据流: 00_preprocessing → 11_news_bank → 12_news_fintech
        → 21_tone_llms → 22_tone_words → 23_tone_berts
        → [31-39 验证模块群]
        → 45_panel_export_main (入口, 编排 41→42→43→44→45)
          → 41_panel_encode_aggregate
          → 42_panel_attention_media
          → 43_panel_indicators_geography
          → 44_panel_iv_did
          → 45_panel_export_main (入口)
        → 51_falsification_test
```

---

## 二、核心模块审计锚点

### 2.1 `11_news_bank.py` — 银行新闻分类与展开

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **核心算法** | Aho-Corasick 自动机 (O(N) 线性匹配) | ✅ 算法复杂度最优 |
| **展开策略** | Phase 1 提早展开 (article→article×bank) | ✅ 避免下游重复展开 |
| **别名系统** | `bank_names.json` 多变体匹配 | 需审查: 别名覆盖率 |
| **共提及银行** | `co_mentioned_banks` 字段 (`;`分隔) | 用于 Bartik IV 基期份额 |
| **标题匹配** | `target_bank_in_title` 布尔列 | 用于 Bartik 稳健性检验 16 |
| **学术引用** | 无显式引用 | **面板诊断**: 建议引用 Hassan et al. (2019) firm-level exposure |
| **可调参数** | 无可调阈值 (全量展开) | 设计合理 |

### 2.2 `12_news_fintech.py` — 金融科技新闻判断

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **核心算法** | Aho-Corasick 自动机 + 上下两半分割 | 创新: 分布均匀性要求 |
| **分类策略** | 多样性条件 (≥MIN_DISTINCT_KEYWORDS) + 分布条件 | ✅ 减少假阳性 |
| **可调参数** | `SPLIT_RATIO=0.5`, `MIN_UPPER=1`, `MIN_LOWER=1`, `MIN_DISTINCT_KEYWORDS=3` | 可配置 |
| **全量保存** | `12_fintech_news_full.parquet` (过滤前) | ✅ 为 51_falsification 提供基础 |
| **学术引用** | 无显式引用 | **面板诊断**: 建议引用胡俊(2023)关键词法 + 下游LLM验证形成二阶段筛选 |
| **验证机制** | 依赖 31_bank_fintech_threshold.py 外部验证 | ✅ 独立验证 |

### 2.3 `21_tone_llms.py` — LLM 情感分析 (多模型投票)

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **核心框架** | 双轨 (full/ctx) × 多模型 (gpt5nano/gemini3/claude4h) | ✅ 学术级消融设计 |
| **投票机制** | 多数投票 + 一致率 (agreement_rate) | ✅ 引用合理 |
| **置信度** | 模型返回 confidence 分数 | 用于连续编码 `cont = direction × confidence` |
| **学术引用** | Carlson & Burbano (2026, SMJ) 已引用 | ✅ 最新文献 |
| **Prompt设计** | 三分类 (正面/中性/负面) + 置信度 | 需审查: 是否需要 5-point Likert |
| **可调参数** | `sentence_radius`, 模型列表 | 可配置 |
| **面板诊断** | Chiu & Hung (2024, IRFA) Dirichlet 校准未实现 | **已在 34_tone_validation L30 引用但降级** |

### 2.4 `22_tone_words.py` — 词典法情感分析

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **词典数量** | 5本中文金融词典 (蒋/姚/卞/杜/尤) | ✅ 多词典交叉 |
| **语言规则** | 否定词翻转 + 程度词加权 + 转折词处理 | ✅ 超过LM标准 |
| **IDF加权** | `_idf_score` 变体 (Gentzkow et al. 2019, JEL) | ✅ 稳健性检验 |
| **双轨** | full/ctx 并行 | ✅ 消融设计 |
| **学术引用** | Loughran & McDonald (2016, JAR) 隐含遵循 | 建议显式引用 |
| **面板诊断** | 无 domain-adapted 扩展 | 可考虑 Ke, Kelly & Xiu (2020, RFS) SentimentR |

### 2.5 `23_tone_berts.py` — BERT 情感分析

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **模型数量** | 5个 BERT 模型 (finbert_cn/fin_sent_zh/erlangshen/hw2942/finbert2) | ✅ 多模型集成 |
| **滑动窗口** | 超过512 token 时自动分割 + 置信度加权池化 | ✅ 长文本处理 |
| **GPU加速** | AMP (自动混合精度) | ✅ 性能优化 |
| **三分类/二分类** | 自动检测 label_map | ✅ 灵活适配 |
| **学术引用** | 隐含引用 FinBERT (Huang et al. 2023) | 建议显式引用 |
| **面板诊断** | 无 fine-tuning 能力 | 使用预训练推理, 可接受 |

### 2.6 `utils/entity_context.py` — 实体特异性上下文提取

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **核心算法** | 句号边界分割 + 滑动窗口 + O(N log N) 区间合并 | ✅ 高效 |
| **学术引用** | Hassan et al. (2019, QJE) proximity-based attribution | ✅ 核心引用正确 |
| **参数** | `sentence_radius=1` (默认), `fallback_char_radius=150` | 经 35_radius_sensitivity 验证 |
| **退化处理** | <3句 → 字符级回退 | ✅ 鲁棒性 |
| **Gap** | 未实现 Sautner et al. (2023) 的加权距离衰减 | 可作为稳健性扩展 |

### 2.7 `45_panel_export_main.py` — Bank-Year 面板构建 (入口, 编排 41→42→43→44→45)

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **聚合范式** | Tetlock et al. (2008, JF) 先分后合 | ✅ 学术标准 |
| **三种加权** | EW (等权) + VW (提及密度, Hassan 2019) + MW (媒体权威, Holzman 2023) | ✅ 三重加权 |
| **标准化** | Fama-MacBeth (1973) 年度截面 z-score | ✅ 学术级 |
| **Bartik IV** | 29套维度 (Goldsmith-Pinkham et al. 2020, AER) | ✅ **超出行业标准** |
| **DID** | Callaway & Sant'Anna (2021, JoE) 交错DID | ✅ 前沿方法 |
| **LOO IV** | 省级/城市级/经济圈 Leave-One-Out | ✅ 三级LOO |
| **Stata导出** | .dta + variable_labels (≤80字符) | ✅ 回归就绪 |
| **面板诊断** | G-07 面板平衡性诊断 (`45_panel_export_main.py`) | ✅ 已实现 |

### 2.8 验证模块群 (`31-39`)

| 模块 | 功能 | 学术依据 | 状态 |
|-----|------|---------|------|
| `31_bank_fintech_threshold.py` | 分类阈值敏感性 | — | ✅ |
| `32_news_llms_human.py` | 人工验证样本生成 | Carlson & Burbano (2026, SMJ) | ✅ |
| `33_news_llms_evaluation.py` | LLM vs 人工评估 | — | ✅ |
| `34_tone_validation.py` | 三角验证 (Cronbach α/Spearman) | Loughran & McDonald (2016, JAR) | ✅ |
| `35_radius_sensitivity.py` | sentence_radius 敏感性 | Hassan et al. (2019, QJE) | ✅ |
| `36_entity_masking_test.py` | 实体遮蔽消融 | — | ✅ |
| `37_dict_coverage_audit.py` | 词典覆盖率审计 | — | ✅ |
| `38_media_diversity.py` | 媒体多样性审计 (HHI/Shannon/Gini/Pielou) | Shannon(1948)/Herfindahl(1950) | ✅ |
| `39_prompt_sensitivity.py` | Prompt 敏感性 | — | ✅ |

### 2.9 `51_falsification_test.py` — 伪造检验

| 锚点维度 | 当前实现 | 审计观察 |
|---------|---------|---------|
| **核心方法** | Hassan et al. (2019, QJE) Table 7 PRisk vs NPRisk | ✅ 核心论文完整对标 |
| **Anti-join** | Fintech + Non-Fintech = 全量 (穷举) | ✅ 恒等式校验 |
| **对照变量** | nf_ln_coverage (Fang 2009) + nf_media_breadth (Bushee 2010) | ✅ 学术标准 |
| **Stata模板** | 16项回归模板 (基准/赛马/IV/交互/Oster/地理聚类) | ✅ **出版就绪** |
| **面板诊断** | 无 placebo test (随机时点伪造) | 可作为扩展 |

---

## 三、全局审计锚点汇总

### 已引用的核心文献 (项目代码中已出现)

| 文献 | 引用位置 | 引用方式 |
|-----|---------|---------|
| Tetlock et al. (2008, JF) | `41_panel_encode_aggregate.py` | 聚合范式 |
| Hassan et al. (2019, QJE) | `entity_context.py` L32, `51_falsification.py` L11 | 实体暴露+伪造检验 |
| Goldsmith-Pinkham et al. (2020, AER) | `44_panel_iv_did.py` L73 | Bartik IV Share视角 |
| Borusyak, Hull & Jaravel (2022, RES) | `44_panel_iv_did.py` L76 | Bartik IV Shift视角 |
| Callaway & Sant'Anna (2021, JoE) | `44_panel_iv_did.py` L451 | 交错DID |
| Holzman et al. (2023, TAR) | `41_panel_encode_aggregate.py` L188 | 媒体权威性加权 |
| Fama & MacBeth (1973) | `43_panel_indicators_geography.py` | 截面标准化 |
| Fang & Peress (2009, JF) | `51_falsification.py` L18 | 对数覆盖量 |
| Bushee et al. (2010, JAR) | `51_falsification.py` L27 | 媒体广度 |
| Shannon (1948) | `38_media_diversity.py` L23 | Shannon熵 |
| Carlson & Burbano (2026, SMJ) | `34_tone_validation.py` L43 | LLM注释方法论 |
| Chiu & Hung (2024, IRFA) | `34_tone_validation.py` L42 | Dirichlet校准(降级) |
| Loughran & McDonald (2016, JAR) | `34_tone_validation.py` L40 | 多度量方法效度 |
| Gentzkow, Kelly & Taddy (2019, JEL) | `45_panel_export_main.py` L521 | IDF加权 |

### 识别的方法论差距 (待 Phase 3 审计验证)

| # | 差距描述 | 涉及模块 | 对标文献 |
|---|---------|---------|---------|
| G1 | LLM 概率校准未完整实现 (仅描述性统计) | `34_tone_validation.py` | Chiu & Hung (2024, IRFA) |
| G2 | 未实现 Ke-Kelly-Xiu SentimentR 连续情感 | `22_tone_words.py` | Ke et al. (2020, RFS) |
| G3 | 实体距离衰减权重未实现 | `entity_context.py` | Sautner et al. (2023, ECGI) |
| G4 | Placebo 时点检验未实现 | `51_falsification.py` | Hassan et al. (2019, QJE) |
| G5 | 面板平衡性诊断缺失 | `41_panel_encode_aggregate.py` | 标准面板数据实践 |
| G6 | 词典法无 domain adaptation 机制 | `22_tone_words.py` | Rizinski et al. (2024) |
| G7 | BERT 模型无 temporal drift 监控 | `23_tone_berts.py` | Anis et al. (2024) |
| G8 | LLM Prompt 三分类 vs 五分类 Likert 未讨论 | `21_tone_llms.py` | Lopez-Lira & Tang (2023) |
