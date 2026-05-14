# Prompt 方法学术语映射 (v3.0.0 / v8 - 2026-05-15)

本文档建立 [unified_cot.txt](../../config/prompts/unified_cot.txt) 内部术语与国际金融学/管理学顶刊方法学章节标准术语的对应关系，用于论文 Methodology Section 撰写与 replication 包说明。

**核心约定 (v3.0.0)**：v6/v7 翻译层已废除。panel 列值即 LLM 原始输出。列名后缀正名为 `_sub` (substantive) / `_symb` (symbolic) / `_tech` (technology) / `_app` (application)，与 Westphal & Zajac (1998 ASQ) 框架严格对齐。

---

## 1. 三阶段名称映射

| Prompt 内部 (v7) | 论文英文术语 | 论文中文学术术语 | 文献锚定 |
|---|---|---|---|
| 阶段一：主体-议题关联识别 | Entity-Topic Relevance Identification | 主体-议题关联识别 | Bybee, Kelly, Manela, & Xiu (2024, JF) |
| 阶段二：情感属性分类 | Sentiment Attribute Classification | 情感属性分类 | Loughran & McDonald (2011, JF); Tetlock (2007, JF) |
| 阶段三：创新属性分类 | Innovation Attribute Classification | 创新属性分类 | Westphal & Zajac (1994, 1998, ASQ); Fiss & Zajac (2006, ASQ); Gomber et al. (2018, JMIS) |

---

## 2. JSON 输出字段映射

| Prompt 字段 (v7) | JSON 值域 | panel 列值 | 论文英文术语 | 文献锚定 |
|---|---|---|---|---|
| `is_bank_fintech_news` | true/false | bool | Article-Level Relevance Indicator | Loughran & McDonald (2011, JF) |
| `confirmed_bank` | 银行名/null | str | Confirmed Entity Mention | Hassan, Hollander, van Lent, & Tahoun (2019, QJE) |
| `fintech_topic` | free text | str | Topical Tag | Bybee et al. (2024, JF) |
| `verification_confidence` | 0.0-1.0 | float | Classifier Confidence Score | LMD (2011, JF) |
| `sentiment` | 正面 / 中性 / 负面 | str | Polarity: Positive / Neutral / Negative | LMD (2011, JF); Garcia (2013, JF) |
| `sentiment_confidence` | 0.0-1.0 | float | Polarity Confidence | — |
| **`innovation_substantiveness`** | **实质性 / 象征性** | **实质性 / 象征性** | **Innovation Substantiveness: Substantive vs Symbolic** | **Westphal & Zajac (1994, 1998, ASQ); Fiss & Zajac (2006, ASQ)** |
| **`innovation_substantiveness_confidence`** | 0.0-1.0 | float | W&Z Substantiveness Confidence | — |
| **`innovation_locus`** | **底层技术 / 应用场景** | **底层技术 / 应用场景** | **Innovation Locus: Technology Layer vs Application Layer** | **Gomber, Kauffman, Parker, & Weber (2018, JMIS); Adner & Kapoor (2010, SMJ)** |
| **`innovation_locus_confidence`** | 0.0-1.0 | float | Locus Confidence | — |
| `*_reason` 字段 | free text | str | Chain-of-Thought Rationale | De Kok (2025) Appendix C; Wei et al. (2022, NeurIPS) |

---

## 3. v3.0.0 术语正名 (翻译层废除)

### v6 → v7 → v8 (v3.0.0) 演进历史

| 版本 | LLM 端值域 | panel 端值域 | panel 列后缀 | 翻译层 |
|---|---|---|---|---|
| v6 | 实质性 / 描述性 | 实质性 / 描述性 | `_sub` / `_desc` | 无 (LLM 直接输出"描述性") |
| v7 | 实质性 / 象征性 | 实质性 / **描述性** | `_sub` / `_desc` | **有** (tone_llms.py 内联: 象征性→描述性) |
| **v8 (v3.0.0)** | **实质性 / 象征性** | **实质性 / 象征性** | **`_sub` / `_symb`** | **废除** |

### 关键含义 (v3.0.0)

| 列名后缀 | 学术语义 | 文献依据 |
|---|---|---|
| `_sub` | substantive | W&Z (1994, 1998 ASQ); Fiss & Zajac (2006 ASQ) |
| `_symb` | **symbolic** (替代 v6/v7 的 `_desc`) | W&Z (1994 ASQ symbolic management) |
| `_tech` | enabling technology layer | Gomber et al. (2018 JMIS) |
| `_app` | business function layer | Gomber et al. (2018 JMIS) |

### v3.0.0 迁移影响清单

- **38 个 panel 列名** 重命名（`*_desc*` → `*_symb*`），含主列 8 + 中间列 30
- **panel 列值** 改回 LLM 原始输出（`"描述性"` → `"象征性"`）
- **tone_llms.py** 删除翻译映射 (`if tt_str == '象征性': tt_str = '描述性'`)
- **encode.py** `tt_mapping` 改为 `[('实质性', '_sub'), ('象征性', '_symb')]`
- **Stata .do 标签** Descriptive News → Symbolic News (W&Z 1998)
- **codebook.py** 头部说明 v6→v7→v8 演进
- **golden_panel_v0.json** 重生成
- **测试基线** 991 → 986 (删除 test_translation_layer.py 5 个测试)

详见 [CHANGELOG.md](../../../CHANGELOG.md) v3.0.0 条目。

---

## 4. 论文 Methodology Section 模板片段

### 4.1 Innovation Substantiveness (substantive vs symbolic)

> Following Westphal and Zajac (1994, 1998), we classify each fintech-related news article along the **substantive-symbolic** dimension. A *substantive* (实质性) article documents actions with real economic or operational consequences—genuine resource commitments (capital, headcount, infrastructure), independently verifiable capability building (deliverables to users, disclosed scale, executed key agreements, granted patents/licenses, completed system integration), or traceable correspondence with the bank's actual operations or strategic trajectory. A *symbolic* (象征性) article reflects legitimacy signaling or impression management without corresponding substantive economic outcomes (slogans, vision statements, target commitments without concrete inputs or timelines; press-conference-style releases without independent evidence of operational impact; ceremonial activities; trend-following announcements; or decoupling of declarations from disclosed actions, in the sense of Fiss and Zajac, 2006). Panel columns suffixed `_sub` (substantive) and `_symb` (symbolic) follow this classification.

### 4.2 Innovation Locus (technology vs application)

> Following Gomber, Kauffman, Parker, and Weber (2018) and Adner and Kapoor (2010), we further classify each article along the **technology-application** dimension of fintech innovation locus. *Technology-layer* (底层技术) articles concern enabling technology infrastructure (AI, blockchain, big data, cloud computing, quantum computing, biometrics). *Application-layer* (应用场景) articles concern specific business-function applications (digital payment, open banking, intelligent risk control, robo-advisory, digital credit). Panel columns suffixed `_tech` and `_app` follow this classification.

---

## 5. 复现与变更指南

### 5.1 论文 replication 包变量名

v3.0.0 replication 包中所有 `_symb` 命名变量按 W&Z (1994) symbolic 解释；旧 `_desc` 命名仅在 baseline/pre-v6 tag 之前的版本中存在。

### 5.2 重命名追踪

GitHub commit hash `<v3.0.0 commit>` 包含完整重命名清单。`git log baseline/pre-v6..HEAD -- news_process/pipeline/panel/encode.py` 可查看核心改动。

### 5.3 与 v6 panel 兼容性

v3.0.0 引入 BREAKING CHANGE，与 v6/v7 panel 不兼容。下游 Stata 脚本与 papers/ 模块已同步更新。任何引用旧 `_desc` 列名的外部代码需迁移至 `_symb`。
