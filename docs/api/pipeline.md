# `news_process.pipeline` — 业务流水线 API

`pipeline` 包含所有**主线流水线**（``run_pipeline_function.py`` 调度）的业务模块，
按业务域划分为 **9 个子包**（v3.5+/v3.7.0 新加 `text/` / `external/` / `llm_archive/`）。

```{eval-rst}
.. autosummary::

   news_process.pipeline.preprocess
   news_process.pipeline.filtering
   news_process.pipeline.text
   news_process.pipeline.sentiment
   news_process.pipeline.features
   news_process.pipeline.panel
   news_process.pipeline.falsification
   news_process.pipeline.audit
   news_process.pipeline.external
   news_process.pipeline.llm_archive
```

## 子包速查

### `pipeline.preprocess` — 阶段 00 数据预处理

| 模块 | 职责 |
|---|---|
| `runner.py` | 主入口 `main()`，编排 load → normalize → filter → dedup |
| `_constants.py` | 模块级常量、CONFIG、logger、预编译正则 |
| `load.py` | Aho-Corasick 自动机 + 单文件并行处理 |
| `normalize.py` | OpenCC 简繁、HTML 清洗、噪声去除、尾部清理 |
| `filter.py` | 区域 / 媒体类型 / 关键词多步过滤 |
| `dedup.py` | 精确去重 + MinHash LSH 近似去重 |

### `pipeline.filtering` — 阶段 11/12/14/15 新闻筛选

| 模块 | 阶段 | 职责 |
|---|---|---|
| `news_bank.py` | 11 | Aho-Corasick 银行新闻分类 |
| `news_fintech.py` | 12 | Aho-Corasick 金融科技新闻分类 |
| `fintech_intensity.py` | 14 | TF-IDF + SIF 词向量质心连续型强度评分 |
| `policy_alignment.py` | 15 | 文章级政策语义对齐度（Distel et al. 2026） |

### `pipeline.text` — 阶段 13 / 18 / 30a 文本预处理与表示（v3.5+/v3.7.0）

| 模块 | 阶段 | 职责 |
|---|---|---|
| `ctx_materializer.py` | 13 | content_ctx 列前置物化（v3.6.0 Plan E A1，让下游 14/15 真双轨化） |
| `article_staleness.py` | 18 | 文章 staleness 双指标（O(N²)→O(N·k) 重写，720× speedup） |
| `article_sbert.py` | 30a | shibing624 Sentence-BERT 持久化 |

### `pipeline.sentiment` — 阶段 21-24 情感分析

| 模块 | 阶段 | 职责 |
|---|---|---|
| `tone_llms.py` | 21 | 多 LLM 双轨 + 标题轨道，多数投票共识 |
| `tone_words.py` | 22 | 词典法 + 语言学规则增强 |
| `tone_berts.py` | 23 | BERT 系列预训练模型情感分析 |
| `herd_decay.py` | 24 | 跟风/抄袭检测 + 衰减加权（Tetlock 2011） |
| `lm_non_sentiment.py` | 内嵌 22 | LM 2011 JF 4 子词典（uncert / litig / constr / modal_strong），v3.5.2 |
| `forward_looking.py` | 内嵌 22 | Li 2010 JAR FLS 双门控（future ∧ time），v3.5.2 |
| `numerical_intensity.py` | post-22 | Hales 2011 CAR 数值强度双轨（v3.5.1 A3） |

### `pipeline.features` — 阶段 25-27 特征工程

| 模块 | 阶段 | 职责 |
|---|---|---|
| `strategic_diff.py` | 25 | 战略差异度（Guzman-Li 2023, Hoberg-Phillips 2016） |
| `policy_similarity.py` | 26 | Bank-Year 政策对齐 |
| `benefit_society.py` | 27 | 经营态度对社会福祉的投影（Jha-Liu-Manela 2026） |

### `pipeline.panel` — 阶段 45/46/49 主面板组装

| 模块 | 职责 |
|---|---|
| `runner.py` | 主面板编排器 (`main()`，1,589 行) |
| `encode.py` | 文章级编码 + Bank-Year 聚合（1,513 行） |
| `encode_collab.py` | v3.5.0/v3.5.1 D2+D4 追加 + clarity + num_intensity |
| `attention_media.py` | 金融科技注意力 + 媒体异质性 |
| `geography.py` | 地理缓冲 + 区域模仿压力 |
| `iv_did.py` | Bartik IV + DID + 政策冲击 |
| `network_spillover.py` | 同行网络溢出 + 中心度 22 指标 |
| `network_brokerage.py` | 经纪网络 + LOO 冲击 + 火灾甩卖 |
| `llm_peer_iv.py` | LLM 同业工具变量 |
| `risk_taking_outcomes.py` | stage 49 风险承担 outcome（Z-score + NPL + RWA + LLP discretion） |
| `codebook.py` | 学术元数据 + 双语 label |
| `export.py` | 多格式 (parquet) 导出 |
| `stata_export.py` | stage 46 Stata `.dta` 导出（核心/aux/full 三件套 + value labels + 缩写） |

### `pipeline.falsification` — 阶段 51 伪造检验

| 模块 | 职责 |
|---|---|
| `controls.py` | 对照变量构建 + Stata 回归模板 |

### `pipeline.audit` — 阶段 39/52/53 数据审计与构念验证

| 模块 | 阶段 | 职责 |
|---|---|---|
| `inter_track_kappa.py` | 39a | full/ctx 双轨间 Cohen κ 一致性 |
| `construct_orthogonality.py` | 39c | v3.5.0 D3 NMI 正交性 |
| `lexical_discriminant_validity.py` | 39d | v3.5.1 HTMT + κ + α + permutation seed=42 |
| `lm_discriminant_validity.py` | 39e | v3.5.2 LM 4 子词典 HTMT + Cronbach α |
| `cross_media_alpha.py` | 39f | v3.7.0 D3 Krippendorff α (outlet × day matrix) |
| `llm_contamination_test.py` | — | LLM 训练数据污染检测 |
| `stata_audit.py` | 52 | Stata 用面板数据完整性审核 |
| `stats_excel.py` | 53 | 统计摘要表 Excel 导出 |

### `pipeline.external` — 阶段 16 外部数据合并（v3.6.1）

| 模块 | 阶段 | 职责 |
|---|---|---|
| `epu_merge.py` | 16 | Baker-Bloom-Davis 2016 QJE 中国 EPU 指数合并（graceful fallback path-not-exist） |

### `pipeline.llm_archive` — DC3 LLM 响应归档（v3.7.0）

| 模块 | 职责 |
|---|---|
| `archive.py` | append-only JSONL + SHA-256 manifest（顶刊 reproducibility 硬约束） |
| `manifest.py` | manifest 生成与验证 |
