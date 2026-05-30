# Stata 指标完整分类说明书 (v3.7.0 + v2.3 supplementation)

> **文件作用**：本项目 `news_process` 通过 stage 46 (`46_stata_export.py` → `pipeline/panel/stata_export.py`) 输出的所有 Stata `.dta` 列指标的**穷尽式分类说明**。
>
> **目标读者**：(1) 跑回归的研究者；(2) 写论文 Methods 节的作者；(3) 复现包接收方；(4) 审稿人。
>
> **覆盖版本**：v3.7.0（D 组 BERTopic / staleness / α / CEO NER）+ v2.3 集成（LM 4 子词典 + FLS + 媒体 tier + EPU + DC3 LLM archive）+ v3.6.0 Plan E（A1/B1/B2/B3 双轨）+ v3.5.0/v3.5.1（D2/D4 + clarity + numerical intensity）+ v3.4.0（collab_mode 第三维度）+ v3.2.0（Stage 3 双轨化 BREAKING）+ 全部历史 baseline。
>
> **当前最大 panel**：`51_panel_with_controls.dta` ≈ **2033 列**（IC 上限 2048 的 99%）。`46_panel_yearly_full.dta` ≈ **2024 列**；`46_panel_yearly_core.dta` 严格 ≤ 2048 列（当前 ~115 列）。
>
> **依据源代码（截至 2026-05-19）**：
> - [news_process/pipeline/panel/stata_export.py](../pipeline/panel/stata_export.py)（导出层 + 列名缩写 + value labels）
> - [news_process/pipeline/panel/codebook.py](../pipeline/panel/codebook.py)（学术元数据 + 双语 label）
> - [news_process/pipeline/panel/encode.py](../pipeline/panel/encode.py)（1513 行，篇章 → bank-year 聚合）
> - [news_process/pipeline/panel/runner.py](../pipeline/panel/runner.py)（1589 行，stage 45 主编排）
> - [news_process/pipeline/panel/encode_collab.py](../pipeline/panel/encode_collab.py)（v3.5.0/v3.5.1 D2+D4 追加 + clarity + num_intensity）
> - [news_process/pipeline/panel/attention_media.py](../pipeline/panel/attention_media.py)（注意力指数 + 媒体异质性）
> - [news_process/pipeline/panel/geography.py](../pipeline/panel/geography.py)（地理 LOO + 区域模仿）
> - [news_process/pipeline/panel/iv_did.py](../pipeline/panel/iv_did.py)（Bartik IV + DID + 政策冲击）
> - [news_process/pipeline/panel/network_spillover.py](../pipeline/panel/network_spillover.py)（22 网络中心度指标）
> - [news_process/pipeline/panel/network_brokerage.py](../pipeline/panel/network_brokerage.py)（信息经纪 + 火灾甩卖）
> - [news_process/pipeline/panel/llm_peer_iv.py](../pipeline/panel/llm_peer_iv.py)（LLM 同行网络 IV）
> - [news_process/pipeline/panel/risk_taking_outcomes.py](../pipeline/panel/risk_taking_outcomes.py)（stage 49 风险承担 outcome）
> - [news_process/pipeline/features/](../pipeline/features/)（benefit_society / strategic_diff / policy_similarity）

---

## 目录

1. [总述：架构与命名约定](#1-总述架构与命名约定)
2. [A 主键与样本结构](#2-a-主键与样本结构)
3. [B 银行属性与时间结构控制](#3-b-银行属性与时间结构控制)
4. [C 新闻覆盖与文本特征](#4-c-新闻覆盖与文本特征)
5. [D 媒体加权三套体系](#5-d-媒体加权三套体系)
6. [E 注意力指数 (Stage 24/42)](#6-e-注意力指数-stage-2442)
7. [F LLM 投票情感（双轨主指标）](#7-f-llm-投票情感双轨主指标)
8. [G LLM 逐模型情感](#8-g-llm-逐模型情感)
9. [H LLM 置信度](#9-h-llm-置信度)
10. [I prob_score（Logit-to-Score 最大熵映射）](#10-i-prob_scorelogit-to-score-最大熵映射)
11. [J 词典法情感（五本 × 三轨 × 三统计）](#11-j-词典法情感五本--三轨--三统计)
12. [K BERT 情感（五模型 × 三轨）](#12-k-bert-情感五模型--三轨)
13. [L Value-Weighted (VW) 加权聚合](#13-l-value-weighted-vw-加权聚合)
14. [M Media-Authority-Weighted (MW) 加权聚合](#14-m-media-authority-weighted-mw-加权聚合)
15. [N Herd-Decay-Weighted (HW) 加权聚合](#15-n-herd-decay-weighted-hw-加权聚合)
16. [O 创新属性三维标签（项目灵魂）](#16-o-创新属性三维标签项目灵魂)
17. [P 创新属性置信度](#17-p-创新属性置信度)
18. [Q D2 八格分解 + D4 双轨残差](#18-q-d2-八格分解--d4-双轨残差)
19. [R Dual Gate 三互斥指示](#19-r-dual-gate-三互斥指示)
20. [S 三维 × tone 子集对角线](#20-s-三维--tone-子集对角线)
21. [T Tone Gap 系列](#21-t-tone-gap-系列)
22. [U 洗稿率 4-way 计数 + Washing Ratio 10 变体](#22-u-洗稿率-4-way-计数--washing-ratio-10-变体)
23. [V Lexical Clarity (v3.5.1 A1)](#23-v-lexical-clarity-v351-a1)
24. [W Numerical Intensity (v3.5.1 A3)](#24-w-numerical-intensity-v351-a3)
25. [X LM 2011 JF 4 子词典 (v3.5.2 A1)](#25-x-lm-2011-jf-4-子词典-v352-a1)
26. [Y Forward-Looking Statements / FLS (v3.5.2 A2)](#26-y-forward-looking-statements--fls-v352-a2)
27. [Z Herd Decay 双轨 (v3.6.0 B3)](#27-z-herd-decay-双轨-v360-b3)
28. [AA Policy Alignment 双轨 (v3.6.0 B2)](#28-aa-policy-alignment-双轨-v360-b2)
29. [AB Fintech Intensity 双轨 (v3.6.0 B1)](#29-ab-fintech-intensity-双轨-v360-b1)
30. [AC EPU 经济政策不确定性 (v3.6.1 B1)](#30-ac-epu-经济政策不确定性-v361-b1)
31. [AD BERTopic 主题聚焦度 (v3.7.0 D1)](#31-ad-bertopic-主题聚焦度-v370-d1)
32. [AE Staleness 内容陈旧度 (v3.7.0 D2)](#32-ae-staleness-内容陈旧度-v370-d2)
33. [AF Krippendorff α 跨媒体分歧 (v3.7.0 D3)](#33-af-krippendorff-α-跨媒体分歧-v370-d3)
34. [AG LLM CEO NER (v3.7.0 D4)](#34-ag-llm-ceo-ner-v370-d4)
35. [AH benefit_society 经营效益态度（Jha-Liu-Manela 2026 RFS）](#35-ah-benefit_society-经营效益态度jha-liu-manela-2026-rfs)
36. [AI 政策对齐 + Token/Hidden 四象限](#36-ai-政策对齐--tokenhidden-四象限)
37. [AJ Bartik IV（6 类 × 三轨 + 基期敏感性 + share + Rotemberg）](#37-aj-bartik-iv6-类--三轨--基期敏感性--share--rotemberg)
38. [AK 政策冲击 DID（DCEP + Sandbox）](#38-ak-政策冲击-diddcep--sandbox)
39. [AL 异质性交互项（SOE / Scale / HighCov / Stress / DDD）](#39-al-异质性交互项soe--scale--highcov--stress--ddd)
40. [AM 滞后 / 反转 / Concern Score](#40-am-滞后--反转--concern-score)
41. [AN J-F 系数](#41-an-j-f-系数)
42. [AO disag 情感分歧](#42-ao-disag-情感分歧)
43. [AP log_sent 对数降噪情感](#43-ap-log_sent-对数降噪情感)
44. [AQ algo_cater 算法迎合度](#44-aq-algo_cater-算法迎合度)
45. [AR Text2Vec 双轨稳健性](#45-ar-text2vec-双轨稳健性)
46. [AS 媒体异质性、平衡媒体稳健性、停刊检测](#46-as-媒体异质性平衡媒体稳健性停刊检测)
47. [AT 地理与 LOO IV](#47-at-地理与-loo-iv)
48. [AU 网络中心度（18 节点级 + 4 网络级 = 22）+ 网络溢出 + 认知邻近度](#48-au-网络中心度18-节点级--4-网络级--22-指标--网络溢出--认知邻近度)
49. [AV 信息经纪 + 火灾甩卖](#49-av-信息经纪--火灾甩卖)
50. [AW 战略差异度 (strat_diff) + 文本连贯性 (coh)](#50-aw-战略差异度-strat_diff--文本连贯性-coh)
51. [AX 权威政策响应度 (auth_sim, 4 方法 × 双轨 = 8 列)](#51-ax-权威政策响应度-auth_sim-4-方法--双轨--8-列)
52. [AY LLM Peer 动态竞争网络 IV（多阈值）](#52-ay-llm-peer-动态竞争网络-iv多阈值)
53. [AZ Embedding Peer 网络](#53-az-embedding-peer-网络)
54. [BA Stage 49 风险承担结果](#54-ba-stage-49-风险承担结果)
55. [BB Stage 51 Falsification 衍生列](#55-bb-stage-51-falsification-衍生列)
56. [BC Stata 列名缩写映射](#56-bc-stata-列名缩写映射)
57. [BD 缺失语义约定](#57-bd-缺失语义约定)
58. [附录 A：导出文件清单](#58-附录-a导出文件清单)
59. [附录 B：笛卡尔积命名模板枚举](#59-附录-b笛卡尔积命名模板枚举)
60. [附录 C：完整参考文献](#60-附录-c完整参考文献)
61. [修订日志](#61-修订日志)
62. [第四块：Stage 31-39 Validation / Audit 输出（**不进 panel**）](#62-第四块stage-31-39-validation--audit-输出不进-panel)

---

## 1. 总述：架构与命名约定

### 1.1 Stata 三件套

| 文件 | 列数 | 用途 |
|---|---|---|
| `46_panel_yearly_core.dta` | ≤ 2048（当前 ~115） | Stata IC 兼容入口；主论文回归用。`assign_core_columns()` 严格白名单。 |
| `46_panel_yearly_aux.dta` | 互补集 ≈ 1900+ | 稳健性 / heterogeneity / sensitivity 列；`merge 1:1 target_bank year` 回 core 还原 full。 |
| `46_panel_yearly_full.dta` | ≈ 2024 | 全列，本机 Stata MP 19.5（64-core/120k vars 上限）可直接读。 |
| `46_panel_yearly_labels.do` | n/a | `label var` + `label define` + `label values`，必须先 `do` 才能正确显示 0/1 → 中文/英文双语标签。 |
| `46_panel_yearly_codebook.xlsx` | n/a | 人类可读 codebook：var_name / original_name（缩写反查）/ label / dtype / value_labels / n_non_null / n_unique / is_core。 |
| `51_panel_with_controls.dta` | ≈ 2033 | falsification 阶段后的 panel；加入 placebo + 全控制变量后的终局面板。 |

### 1.2 核心设计语言

#### (a) 双轨 `_full / _ctx`（v3.2.0 BREAKING）
- `_full` = 整篇新闻文本作为 LLM/词典/BERT 的输入；
- `_ctx` = 仅取目标银行实体的前后窗口（Hassan et al. 2019 QJE entity-proximity 框架）；
- 两轨**独立判定**，不是 _ctx 由 _full 后处理而来。Prompt v8 在 stage 21 各跑一次。

#### (b) 三轨 `_full / _ctx / _title`
某些指标（特别是 LLM 投票、词典、BERT 系列）还有 `_title` 第三轨（只看标题）。

#### (c) 创新属性三维框架
| 维度 | 0 = baseline | 1 = 对照 | 锚定文献 |
|---|---|---|---|
| `innovation_locus` | 底层技术 | 应用场景 | Gomber, Kauffman, Parker, Weber (2018, JMIS) |
| `innovation_substantiveness` | 实质性 | 象征性 | Westphal & Zajac (1998, ASQ); Bingler et al. (2022, FRL) |
| `innovation_collab_mode` | 自主研发 | 外部协同 | Chesbrough (2003) Open Innovation; Laursen & Salter (2006, SMJ) |

> **编码方向约定**：所有三维分类变量统一 `0 = baseline / 1 = 对照`，这是项目的"洗稿率"框架——`positive_class` 始终对应**对照类**（象征性 / 应用场景 / 外部协同），与 `prob_score` 列的 `P(positive)` 编码方向严格对齐。详见 [stata_export.py:42-93](../pipeline/panel/stata_export.py#L42-L93)。

#### (d) 方法学三套并行（**实证来自 `config/sentiment.yaml`**）

| 方法 | 模型 short_name | 实际身份 |
|---|---|---|
| **LLM 投票** (stage 21) | `gpt54nano` | OpenAI GPT-5.4-nano |
| | `gemini31111` | Google Gemini-3.1.1.1.1 |
| | `deepseekv4` | DeepSeek V4（v3 从 `claude4h` 重命名以反映真实身份；旧代码引用仍可能用 claude4h） |
| **中文金融词典** (stage 22) | `jiang_2021` | 姜富伟（2021） |
| | `yao_2021` | 姚加权（2021） |
| | `bian_2021` | 边江泽（2021） |
| | `du_2022` | 杜剑（2022） |
| | `you_2018` | You 等（2018, hhx055） |
| **BERT 系列** (stage 23) | `finbert_cn` | 中文 finbert 通用（3-class，含中性） |
| | `fin_sent_zh` | 中文金融句子 BERT（3-class） |
| | `erlangshen` | 二郎神 finance 微调（2-class） |
| | `hw2942` | HW 2942 财经 BERT（3-class，未缓存 → offline fallback） |
| | `finbert2` | 私有 finbert2 微调（2-class，env `FINBERT2_MODEL_DIR`，缺失 graceful skip） |

源代码引用：[news_process/config/sentiment.yaml L29-L39 (LLM) + L262-L286 (BERT)](../config/sentiment.yaml)。

三套通过 stage 39d (lexical discriminant) / 39e (LM discriminant) / 39f (cross-media α) `discriminant validity` 互为验证。三套笛卡尔积是 panel ~2000 列的主要来源。

#### (e) 三套加权方式
| 加权 | 后缀 | 权重源 | 学术依据 |
|---|---|---|---|
| Value-weighted | `_vw` / `_w` | `mention_density` 单篇提及密度 | Hassan et al. (2019, QJE) entity-proximity |
| Media-Authority-weighted | `_mw` | `media_authority_weight`（10–100 媒体权威度归一化） | Holzman, Miller & Twedt (2023, TAR) |
| Herd-Decay-weighted | `_hw` | `herd_weight_full/ctx`（双轨独立衰减权重） | Tetlock (2011, RFS); Edwards (2001, ORM) |

每个 tone 主指标都派生 3 套加权版（mean、sum、vw、mw、hw），构成"3 方法 × 3 加权 × 3 轨"的庞大笛卡尔。

### 1.3 Stata 硬约束（来自 stata_export.py:37-40）

| 限制项 | 阈值 |
|---|---|
| 变量名 | ≤ 32 字符（超出走 [`shorten_long_column_names()`](../pipeline/panel/stata_export.py#L329) 缩写） |
| variable label | ≤ 80 UTF-8 字节 |
| IC max vars | 2048（core 强制 ≤ 此值） |
| 本机 MP max vars | 120,000（实际只占 ~2%） |
| 字符串 var | str#: 2,045 bytes / strL: 2 GB |
| value label string | 32,000 bytes |

### 1.4 缺失值语义

- `NaN` → Stata `.`（pandas backend）或 `.` / `.a` / `.b`（pyreadstat backend，extended missing）；
- `d4_data_quality_flag = 'insufficient'` → ctx coverage 不足，Stata 端 `keep if d4_data_quality_flag == "ok"`；
- v6/F3 关键修复：所有"无新闻 bank-year"列**保留 NaN**而非填 0，避免 TWFE 制造伪零质心污染系数（见 [runner.py:1041-1043](../pipeline/panel/runner.py#L1041-L1043) Allison 2001 + Heckman 1979 论证）；
- 计数类列（`n_articles*` / `*_sum` / `*_count` / `sum_media_authority_weight`）在 `balance_panel()` 中 fillna 为 0；比率类（`*_frac` / `*_ratio` / `*_tone` / `concern_score` / etc.）保留 NaN。

---

## 2. A 主键与样本结构

**整体说明**：bank-year 长面板的两个唯一键。所有指标围绕 `(target_bank, year)` 聚合；下游 Stata 必须先 `xtset target_bank year`。balance_panel() 强制完全笛卡尔积（288 银行 × 16 年 = 4,608 行），缺失年份自动补齐为 NaN 行 + 计数列填 0。

| 变量 | 类型 | 取值/范围 | 含义 / 来源 |
|---|---|---|---|
| `target_bank` | str | 288 家中国商业银行（6 国有 + 12 全国股份 + ~130 城商 + ~140 农商） | 标准化银行全称；stage 11 通过 `config/bank_list.yaml` 1771 行匹配派生 |
| `year` | int | 2008–2023（实际可用通常 2013–2023） | parse_time() 从 `日期` 列派生 |

---

## 3. B 银行属性与时间结构控制

**整体说明**：bank-level 时不变属性 + 时间断点 dummy，用作 panel 固定效应/控制变量/交互项底。来自 `bank_list.yaml`、`bank_addresses.json`、`implicit_guarantee_framework.md` 等 frozen 元数据。

| 变量 | 公式/来源 | 含义 |
|---|---|---|
| `bank_type` | bank_list.yaml 类别（soe / joint-stock / city / rural / policy / D-SIB） | 银行类型 |
| `is_soe` | `(bank_type == 'soe').astype(int)` | 国有大行哑变量 |
| `bank_size` | bank_list.yaml | 规模等级 |
| `bank_scale_ord` | `{'XS':1,'S':2,'M':3,'L':4}.get(bank_scale, 0)` | 规模有序编码（4 阶） |
| `bank_age` | year − established_year | 银行成立年龄（年） |
| `bank_province` | bank_addresses.json | 总部省份 |
| `bank_city` | bank_addresses.json | 总部城市 |
| `bank_zone` | bank metadata | 经济带（华东 / 华南 / …） |
| `bank_reg` | bank metadata | 监管类别（D-SIB / 非 D-SIB 等） |
| `_has_fintech` | `(panel['n_articles'] > 0).astype(int)` | 该 bank-year 是否有 fintech 新闻覆盖 |
| `digital_frontier` | 同 bank_type × year 中位数 n_articles 之上 = 1 | 数字化前沿哑变量（DDD 用） |
| `stress_period` | `year ∈ {2015, 2018, 2020}` | 银行业压力期（股灾 / 去杠杆 / 疫情） |
| `depins_post` | `year ≥ 2015` | 存款保险条例事件研究 dummy |
| `has_coverage` | `(n_articles > 0).astype(int)` | 有无报道二元 |
| `high_coverage` | 年内 `n_articles ≥ 中位数`（仅在有新闻银行中）= 1 | 高曝光银行哑变量 |

---

## 4. C 新闻覆盖与文本特征

**整体说明**：bank-year 内新闻量、文本长度、共现密度，是后续比率类指标的分母与样本量门控。也是 `min(n) ≥ 5` 抗 compositional confound 的门控源（[encode.py:778](../pipeline/panel/encode.py#L778)，v3.1.1 R8 audit）。

| 变量 | 公式 | 含义 |
|---|---|---|
| `n_articles` | `count(llm_vote_score_full)` per (bank, year) | 该银行该年的新闻篇数（核心样本量） |
| `ln_news_coverage` | `np.log1p(n_articles)` | 对数化覆盖度（缓解长尾） |
| `headline_frac` | `mean(in_title)` | 银行出现在标题中的篇章占比（显著性） |
| `multi_bank_frac` | `mean(bank_count > 1)` | 多银行共现篇章占比 |
| `avg_bank_count` | `mean(bank_count)` | 平均同篇共提银行数 |
| `max_bank_count` | `max(bank_count)` | 同篇最大共提银行数 |
| `bank_count` | 篇章级：`len(co_mentioned_banks.split(';')) + 1` | 篇章级 |
| `is_multi_bank` | 篇章级：`bank_count > 1` | 多银行篇章哑变量 |
| `ln_bank_count` | 篇章级：`np.log1p(bank_count)` | 篇章级对数 |
| `in_title` | 篇章级：`target_bank_in_title.astype(int)` | 银行是否出现在该篇标题中 |
| `avg_doc_length` | `mean(doc_length)` | 平均文本字符长度 |
| `sum_doc_length` | `sum(doc_length)` | 年度总字符数 |
| `sum_target_mentions` | `sum(target_bank_mention_count)` | 目标银行被提及总次数 |
| `sum_mention_density` | `sum(mention_density)` | 单位长度提及密度求和（VW 加权分母） |
| `avg_sent_len_full/ctx/title` | `mean(avg_sentence_len{track})` | 平均句长（Loughran & McDonald 2014 JF 可读性控制） |
| `avg_ttr_full/ctx/title` | `mean(type_token_ratio{track})` | 类型-令牌比 |
| `avg_cpw_full/ctx/title` | `mean(char_per_word{track})` | 平均字/词比 |
| `avg_pos_ratio_{track}` / `avg_pos_ratio_std_{track}` | 词级正面词比例的 mean/std | Berger, Kim & Ma (2024, CAR) + LM (2011, JF) |
| `avg_neg_ratio_{track}` / `avg_neg_ratio_std_{track}` | 词级负面词比例的 mean/std | 同上 |
| `avg_msent_{track}` / `avg_msent_std_{track}` / `msent_sum_{track}` | MSENT 计数型情感的 mean/std/sum | He et al. (2024, IRFA); Tetlock (2007, JF) |
| `avg_agreement_rate_full/ctx/title` | `mean(llm_agreement_rate{track})` | 三 LLM 一致率均值（reliability 信号） |
| `media_breadth` | `np.log1p(媒体(中文).nunique())` | 媒体来源多样性（对数化） |

---

## 5. D 媒体加权三套体系

**整体说明**：本项目同时维护三套媒体权重，分别用于不同的稳健性维度。这是 v3.6.1 PR #6 后的状态——原 `media_authority_weight`（连续）保留为 main，新增 `media_authority_weight_tier`（3 级 tier）作 sensitivity，不替换原列。

### 5.1 原始连续权重（Holzman et al. 2023, TAR）
| 变量 | 公式 | 含义 |
|---|---|---|
| `media_authority_weight` | `raw_weight / mean(raw_weight)`（10–100 评分归一化） | 单篇连续媒体权威度，main spec 用 |
| `sum_media_authority_weight` | bank-year 加权和 | MW 加权聚合分母 |

### 5.2 v3.6.1 媒体 3 级 tier（Solomon 2012 RFS + Engelberg-Parsons 2011 JF）
基于 `config/media_classification.json`（central 171 / financial 15 / comprehensive 27）。互斥优先级：financial > comprehensive > central > other。权重 dict：`{'central': 2.5, 'financial': 2.0, 'comprehensive': 1.5, 'other': 1.0}`。

| 变量 | 取值 | 含义 |
|---|---|---|
| `media_authority_weight_tier` | float ∈ {1.0, 1.5, 2.0, 2.5} | 3 级 tier 离散权重（Table A8 sensitivity） |
| `media_tier_label` | str ∈ {`central`, `financial`, `comprehensive`, `other`} | tier 字符串标签 |

### 5.3 媒体权威性档位（Bartik IV 4 用）
基于 `media_weights.json` 评分高低划档：`high ≥ 80 / mid ≥ 60 / low`。仅在 `runner.py::compute_bartik_iv_fintech(..., 'mauth')` 中作为 share，**不直接进 panel 列**，但派生 `bartik_mauth_iv_*` 系列 IV。

---

## 6. E 注意力指数 (Stage 24/42)

**整体说明**：基于 Da, Engelberg & Gao (2011, JF) Direct Attention + Fang & Peress (2009, JF) 媒体覆盖框架，指数化的"该年市场对该银行金融科技的关注度"，含**指数距离衰减**（地理/时间）。

| 变量 | 公式 | 范围 | 来源 |
|---|---|---|---|
| `ft_attn_yr` | `ln(1 + n_articles) × exp(-distance_decay)` | [0, +∞) | stage 24/42 attention_media.compute_fintech_attention_index |
| 副输出 parquet | — | — | `40_attn_index_year.parquet` / `40_attn_index_province_year.parquet` / `40_attn_index_city_year.parquet` 三个 parquet 不直接合并进 panel，作为外部 join 表 |

注：这三个 parquet 是 panel runner 的副产品，可用于 province-year / city-year 维度的注意力面板分析（论文 P2 attention 主线）。

---

## 7. F LLM 投票情感（双轨主指标）

**整体说明**：3 个 LLM（GPT-5.4-nano / Gemini-3.1-1.1.1 / DeepSeek-V4）独立标注，多数投票产出 sentiment。`_full` / `_ctx` / `_title` 各跑一次 prompt，独立判定（v3.2.0 BREAKING）。所有 LLM 原始响应通过 [DC3 LLM archive 模块](../pipeline/llm_archive/) 持久化为 append-only JSONL + SHA-256 manifest，满足顶刊 reproducibility 硬约束。

锚定：Cao et al. (2025 WP); Shapiro, Sudhof & Wilson (2022, JoE)；Törnberg (2024, arXiv:2307.13106)。

### 7.1 篇章级编码列（stage 21 → encode_sentiment）

| 列名 | 类型 | 含义 |
|---|---|---|
| `llm_vote_score_{full,ctx,title}` | `Int8` nullable | 投票后离散映射 `{正面:1, 中性:0, 负面:-1}`，verified=False/undefined/call_failure → `<NA>` |
| `is_positive_{full,ctx,title}` | `Int8` nullable | `(llm_vote_score == 1)`，invalid → `<NA>`（修 v6/F2 NaN 坍塌 bug） |
| `is_negative_{full,ctx,title}` | `Int8` nullable | `(llm_vote_score == -1)` |
| `is_neutral_{full,ctx,title}` | `Int8` nullable | `(llm_vote_score == 0)` 且仅 verified=True 且 undefined=0 且 failure=0 且 sentiment="中性" |
| `llm_vote_cont_{full,ctx,title}` | `Float32` | `score × agreement_rate`，NaN 自然传播 |
| `llm_agreement_rate_{full,ctx,title}` | float | 三模型一致率（0/3, 1/3, 2/3, 3/3） |
| `llm_verified_{full,ctx,title}` | bool | 投票是否通过验证 |
| `llm_call_failure_{full,ctx,title}` | bool | API 调用失败 mask |
| `llm_undefined_{full,ctx,title}` | bool | tie undefined mask |
| `llm_prob_score_{full,ctx,title}` | Float32 | Logit-to-Score 最大熵映射的连续概率分数 ∈ [0, 1] |

### 7.2 bank-year 聚合列

| 变量 | 公式 | 取值 |
|---|---|---|
| `llm_vote_tone_{full,ctx,title}` | `mean(llm_vote_score{track})` | [−1, 1] |
| `llm_vote_tone_sum_{full,ctx,title}` | `sum(llm_vote_score{track})` | 整数 |
| `llm_vote_tone_std_{full,ctx,title}` | `std(llm_vote_score{track})` | [0, ~1.4] |
| `llm_vote_cont_{full,ctx,title}` | `mean(llm_vote_cont{track})`（聚合后同名列） | [−1, 1] |
| `llm_vote_cont_sum_{full,ctx,title}` | `sum(llm_vote_cont{track})` | float |
| `pos_frac_{full,ctx,title}` | `mean(is_positive{track})` | [0, 1] |
| `neg_frac_{full,ctx,title}` | `mean(is_negative{track})` | [0, 1] |
| `pos_count_{full,ctx,title}` | `sum(is_positive{track})` | int |
| `neg_count_{full,ctx,title}` | `sum(is_negative{track})` | int |
| `llm_sentiment_{full,ctx}` | LLM 离散 sentiment 投票（字符串前）→ encode 后等价 `llm_vote_score` | 弃用别名（codebook 保留） |

### 7.3 v3.2.0 BREAKING 注意事项
`llm_sentiment_full` / `_ctx` 在 codebook 里仍保留作为"main LLM 情感"，但在 production 里**全部走 `llm_vote_tone_*` 主表**（v3.2.0 三模型投票替换单模型）。

### 7.4 内在含义解读（**深度增强**）

**度量什么**：每条 LLM tone 列度量的是"该 bank-year 内媒体语调的方向性强度"，是**情感信息含量**（informational tone）而非简单的好坏评价。

**为什么三模型投票而非单模型**：
- 单模型存在系统性偏差（GPT 系列偏中性、Gemini 偏正面、DeepSeek 偏波动）。三模型多数投票把"系统性偏差 + 真实信号"中的前者抵消（Cao et al. 2025 WP）；
- `llm_vote_tone` 用 `is_positive - is_negative / total` 归一化后 ∈ [-1, 1]，可与 Tetlock 2007 (JF) 的 pessimism index 框架直接对话；
- v6/F2 修复后，verified=False / undefined / call_failure 的 NaN 严格区分于"真实中性"——这避免了 Loughran-McDonald (2011 JF §IV) 警告的"中性坍塌偏差"。

**核心三列的关系**：
| 列 | 信号类型 | 经济学解读 |
|---|---|---|
| `llm_vote_tone_{track}` | 离散投票均值 ∈ [-1, 1] | 篇章级方向多数；适合做事件研究 OLS 主表 |
| `llm_vote_cont_{track}` | 离散 × 置信度（连续） | Shapiro-Sudhof-Wilson (2022, JoE) 信号质量加权；attenuation bias 校正 |
| `llm_prob_score_{track}` | Logit-to-Score Bernoulli ∈ [0, 1] | Törnberg (2024) 最大熵映射；适合做 Logit / Probit 因变量 |

**双轨 _full vs _ctx 的选择逻辑**：
- 主回归**默认 _ctx**（v3.6.0 G3 起 P1 paper main spec 即 `llm_vote_tone_ctx`）：实体邻近上下文规避了"该新闻提了银行但实际讲行业"的污染；
- 稳健性用 _full：完整文本捕获更多语义，但可能稀释信号；
- 两轨**一致** → 强证据；**分歧** → §43 disag 度量出现 → 论文需在 robustness 中讨论。

**典型 Stata 用法（P1 main spec）**：
```stata
xtset target_bank year
* Main spec (v3.6.0 G3 后)
reghdfe Y llm_vote_tone_ctx controls, absorb(target_bank year) cluster(bank_province)
* 稳健性：换 _full
reghdfe Y llm_vote_tone_full controls, absorb(target_bank year) cluster(bank_province)
* 测量误差校正（用 prob_score 作 IV）
ivreghdfe Y (llm_vote_tone_ctx = llm_prob_score_ctx) controls, absorb(target_bank year)
```

**典型使用陷阱**：
- ⚠ **稀疏 bank-year**：`n_articles < 5` 时 tone 估计噪音大，建议在主回归中过滤 `if n_articles >= 5`；
- ⚠ **零中性混淆**：v6/F2 前 `is_neutral` 会把 verification 失败也算成中性 → 旧 panel 的统计量需重跑；
- ⚠ **VW/HW/MW vs 等权**：加权版本（§13-15）系数会更小（高权重篇章往往主流且温和），论文需在 robustness 表展示三种加权对比。

---

## 8. G LLM 逐模型情感

**整体说明**：3 模型 × 3 轨 × 5 统计（mean/sum/std/cont_mean/cont_sum）= 45 列。命名模式：`{model}_tone{track}` 系列。模型集合在 [encode.py:54-56](../pipeline/panel/encode.py#L54-L56) 由 `config['tone_llm_processing']['models']` 注入：`gpt54nano` (OpenAI GPT-5.4-nano) / `gemini31111` (Google Gemini 3.1.1.1.1) / `deepseekv4` (DeepSeek V4)。

### 8.1 通用模板（每模型 × 每轨）

| 列名模板 | 公式 | 含义 |
|---|---|---|
| `{model}_score_{track}` | 篇章级 `Int8` nullable，map 后 `{正面:1, 中性:0, 负面:-1}`，verified=False → `<NA>` | 单模型离散 sentiment（篇章级） |
| `{model}_cont_{track}` | 篇章级 `score × {model}_sentiment_confidence{track}` | 连续置信加权 sentiment |
| `{model}_tone_{track}` | `mean({model}_score{track})` | bank-year 离散均值 |
| `{model}_tone_sum_{track}` | `sum({model}_score{track})` | bank-year 离散求和 |
| `{model}_tone_std_{track}` | `std({model}_score{track})` | bank-year 标准差 |
| `{model}_cont_mean_{track}` | `mean({model}_cont{track})` | 连续 tone 均值 |
| `{model}_cont_sum_{track}` | `sum({model}_cont{track})` | 连续 tone 求和 |

完整展开列名见 [附录 B](#59-附录-b笛卡尔积命名模板枚举)。

---

## 9. H LLM 置信度

**整体说明**：LLM verbalized confidence 衍生的 bank-year 信号清晰度指标。锚定 Shapiro et al. (2022, JoE) 信号噪音 → 衰减偏误（attenuation bias），高置信度 → 估计精度高。

| 变量 | 公式 | 含义 |
|---|---|---|
| `avg_llm_conf_{full,ctx,title}` | 篇章级先做 3 模型 confidence 宏平均，再 bank-year mean | 三模型置信度宏平均后的 bank-year 均值 |
| `avg_llm_conf_std_{full,ctx,title}` | 同上 std | bank-year 标准差 |
| `avg_{model}_conf_{full,ctx,title}` | `mean({model}_sentiment_confidence{track})` | 逐模型置信度均值（3 × 3 = 9 列） |
| `avg_il_confidence_{full,ctx}` | `innovation_locus_confidence_{track}` mean | locus 维度 LLM 置信度（v3.4.0 改名 il） |
| `avg_iss_confidence_{full,ctx}` | `innovation_substantiveness_confidence_{track}` mean | substantiveness 维度置信度 |
| `avg_icm_confidence_{full,ctx}` | `innovation_collab_mode_confidence_{track}` mean | collab_mode 维度置信度（v3.4.0 新增） |
| `innovation_collab_mode_confidence_{full,ctx}` | 篇章级 LLM verbalized | 单篇 collab_mode 原始置信度（Törnberg 2024） |
| `category_confidence_{full,ctx}` | LLM × keyword crossvalidation 杂交（+0.2 boost / ×0.5 penalty） | locus 篇章级杂交置信度（Gilardi 2023 PNAS） |
| `avg_category_confidence` | bank-year `mean(category_confidence)` | 平均杂交置信度 |
| `avg_agreement_rate_{full,ctx,title}` | 见 §4 | 三模型一致率（也是 reliability 信号） |

---

## 10. I prob_score（Logit-to-Score 最大熵映射）

**整体说明**：Plan v1.37 P2 / Törnberg (2024) 框架。把 LLM 离散类别 + verbalized confidence 通过 Bernoulli 最大熵映射成连续 ∈ [0, 1] 概率。`positive_class = 1 = 对照类`（象征性 / 应用场景），与 stata_export encoding 严格对齐。

锚定：Cover & Thomas (2006) §2 Bernoulli entropy; Jaynes (1957); Törnberg (2024); Shapiro et al. (2022); Plan v1.37 P2 §5.3.2。

### 10.1 主情感 prob_score（投票级，3 轨）

| 变量 | 公式 | 含义 |
|---|---|---|
| `avg_llm_prob_score_{full,ctx,title}` | `mean(llm_prob_score{track})` | bank-year 平均 prob_score |
| `avg_llm_prob_score_std_{full,ctx,title}` | std | bank-year 标准差 |
| `llm_prob_score_sum_{full,ctx,title}` | sum | 求和 |
| `llm_prob_score_w_sum_{full,ctx,title}` | VW 加权 sum | VW 加权求和（VW tone 分子） |
| `llm_prob_score_mw_sum_{full,ctx,title}` | MW 加权 sum | MW 加权求和 |
| `llm_prob_score_hw_sum_{full,ctx,title}` | HW 加权 sum | HW 加权求和 |
| `llm_vote_tone_vw_prob_{full,ctx,title}` | `llm_prob_score_w_sum / sum_mention_density` | VW prob_score（替代 sentiment） |
| `llm_vote_tone_mw_prob_{full,ctx,title}` | `llm_prob_score_mw_sum / sum_media_authority_weight` | MW prob_score |
| `llm_vote_tone_hw_prob_{full,ctx,title}` | `llm_prob_score_hw_sum / sum_herd_weight_{track 对应}` | HW prob_score |
| `prob_gap_title_full` | `avg_llm_prob_score_title − avg_llm_prob_score_full` | 标题-全文 prob_score 缺口（标题党检测） |

### 10.2 二分类 prob_score（创新属性二维 × 双轨 × 2 统计 = 8 列）

| 变量 | 公式 | positive_class |
|---|---|---|
| `avg_subst_prob_score_{full,ctx}` | `mean(compute_prob_score_binary(label, conf, positive_class="象征性"))` over models on innovation_substantiveness | 象征性 = 1 |
| `avg_subst_prob_score_std_{full,ctx}` | bank-year std | 同上 |
| `avg_locus_prob_score_{full,ctx}` | `mean(... positive_class="应用场景")` over models on innovation_locus | 应用场景 = 1 |
| `avg_locus_prob_score_std_{full,ctx}` | bank-year std | 同上 |

### 10.3 子集 prob_score（按 substantiveness/locus/collab_mode 子集均值）

`llm_prob_score_{tech,app,sub,symb,indep,collab}_{full,ctx,title}` + `_lc_ctx` / `_sc_ctx` / `_cm_ctx` 对角线列（共 ~30 列），由 [encode.py:909-918](../pipeline/panel/encode.py#L909-L918) 派生。

---

## 11. J 词典法情感（五本 × 三轨 × 三统计）

**整体说明**：5 本中文金融词典在 stage 22 对每篇文章打分，bank-year 聚合。词典清单：

| 短名 | 词典作者 | 简介 |
|---|---|---|
| `jiang_2021` | 姜富伟（2021） | 中国财经新闻情感词典（最常用） |
| `yao_2021` | 姚加权（2021） | 银行业新闻情感词典 |
| `bian_2021` | 边江泽（2021） | 政策语调词典 |
| `du_2022` | 杜剑（2022） | 金融科技新闻情感词典 |
| `you_2018` | You 等（2018, hhx055） | LM 中文化扩展词典 |

### 11.1 等权聚合（每词典 × 每轨）

| 列名 | 公式 |
|---|---|
| `{dict}_tone_{full,ctx,title}` | `mean({dict}_score{track})` |
| `{dict}_tone_sum_{full,ctx,title}` | `sum({dict}_score{track})` |
| `{dict}_tone_std_{full,ctx,title}` | `std({dict}_score{track})` |
| `_dict_avg_score_{full,ctx}` | 5 词典等权平均（篇章级，用于 disag/cater） |

5 词典 × 3 轨 × 3 stat = **45 列**。

### 11.2 IDF 加权（Gentzkow, Kelly & Taddy 2019, JEL）

| 列名 | 公式 |
|---|---|
| `{dict}_idf_tone_{full,ctx,title}` | `mean({dict}_idf_score{track})` |
| `{dict}_idf_tone_sum_{full,ctx,title}` | `sum({dict}_idf_score{track})` |
| `{dict}_idf_tone_std_{full,ctx,title}` | `std({dict}_idf_score{track})` |

5 词典 × 3 轨 × 3 stat = **45 列**。

### 11.3 词级正负面比例（Berger, Kim & Ma 2024, CAR）

| 列名 | 公式 |
|---|---|
| `avg_{dict}_pos_ratio_{full,ctx}` | `mean({dict}_pos_ratio{track})` |
| `avg_{dict}_neg_ratio_{full,ctx}` | `mean({dict}_neg_ratio{track})` |

5 词典 × 2 轨 × 2 stat = **20 列**。

### 11.4 词典法洗稿率 4-way 计数

| 列名 | 公式 |
|---|---|
| `dict_pos_count_{full,ctx}` | 词典综合正面篇章数 |
| `dict_pos_symb_count_{full,ctx}` | 词典综合正面 ∩ 象征性篇章数 |
| `{dict}_pos_count_{full,ctx}` | 单词典正面篇章数（5 × 2 = 10 列） |
| `{dict}_pos_symb_count_{full,ctx}` | 单词典正面 ∩ 象征性（10 列） |
| `{dict}_neg_count_{full,ctx}` | 单词典负面篇章数（Garcia 2013 → disag 输入）（10 列） |

---

## 12. K BERT 情感（五模型 × 三轨）

**整体说明**：5 个中文 BERT 模型在 stage 23 输出 `{model}_{正面/负面/中性}{track}` 篇章级概率，bank-year 聚合。模型集合在 [encode.py:62-72](../pipeline/panel/encode.py#L62-L72) 由 `config['sentiment_analysis']['tone_berts']['models']` 注入：

| 短名 | 模型 | 分类数 |
|---|---|---|
| `finbert_cn` | 中文 finbert 通用 | 3-class（含中性） |
| `fin_sent_zh` | 中文金融句子 BERT | 3-class |
| `erlangshen` | 二郎神 finance 微调 | 2-class |
| `hw2942` | HW 2942 财经 BERT（未缓存，offline fallback） | 3-class |
| `finbert2` | 私有 finbert2 微调（env `FINBERT2_MODEL_DIR`，缺失 graceful skip） | 2-class |

### 12.1 等权聚合

| 列名 | 公式 |
|---|---|
| `{bert}_pos_{full,ctx,title}` | `mean({bert}_正面{track})` |
| `{bert}_pos_sum_{full,ctx,title}` | `sum({bert}_正面{track})` |
| `{bert}_pos_std_{full,ctx,title}` | `std({bert}_正面{track})` |
| `{bert}_neg_{full,ctx,title}` | `mean({bert}_负面{track})` |
| `{bert}_neg_sum_{full,ctx,title}` | `sum({bert}_负面{track})` |
| `{bert}_neu_{full,ctx,title}` | `mean({bert}_中性{track})`（仅 3-class 模型有：`finbert_cn` / `fin_sent_zh` / `hw2942`） |
| `{bert}_neu_sum_{full,ctx,title}` | `sum({bert}_中性{track})` |

5 BERT × 3 轨 × (5 共通 + 2 三分类专属) ≈ **~60 列**。

### 12.2 BERT 综合

| 列名 | 公式 |
|---|---|
| `_bert_avg_pos_{full,ctx}` | 5 模型等权平均（篇章级） |
| `bert_avg_pos_{full,ctx}` | bank-year `mean(_bert_avg_pos{track})` |
| `bert_avg_neg_{full,ctx}` | 5 模型 neg 等权 bank-year mean |
| `bert_pos_count_{full,ctx}` | BERT 综合正面（>0.5）篇章数 |
| `bert_pos_symb_count_{full,ctx}` | BERT 综合正面 ∩ 象征性 |
| `{bert}_pos_count_{full,ctx}` | 单 BERT 正面（>0.5）篇章数（5 × 2 = 10 列）（Huang et al. 2023 CAR） |
| `{bert}_pos_symb_count_{full,ctx}` | 单 BERT 正面 ∩ 象征性（10 列） |
| `{bert}_neg_count_{full,ctx}` | 单 BERT 负面（>0.5）篇章数（10 列） |

### 12.3 高置信度子样本（方法 F）

| 列名 | 公式 |
|---|---|
| `pos_hc_count_{full,ctx}` | 高置信度（agreement_rate ≥ 0.67）正面篇章数 |
| `pos_symb_hc_count_{full,ctx}` | 高置信度正面 ∩ 象征性 |
| `pos_symb_hc_{full,ctx}_sc` | 同上但 substantiveness 用 ctx 轨判定 |

---

## 13. L Value-Weighted (VW) 加权聚合

**整体说明**：所有 tone 主指标都派生 VW 版本，权重 = 单篇 `mention_density`。锚定 Hassan et al. (2019, QJE) / Sautner et al. (2023, JF)：mention density 越高 → 该篇文章对银行的语义信号越纯。

### 13.1 篇章级加权预计算（runner.py:215-261）

每个 source 列乘以 `mention_density`（fillna 0），产出 `_w` 后缀篇章列：
- `llm_vote_score_w_{full,ctx,title}` / `llm_vote_cont_w_{full,ctx,title}`
- `is_positive_w_{full,ctx,title}` / `is_negative_w_{full,ctx,title}`
- `{model}_score_w_{full,ctx,title}` / `{model}_cont_w_{full,ctx,title}` (3 × 3 × 2 = 18)
- `{dict}_score_w_{full,ctx,title}` / `{dict}_idf_score_w_{full,ctx,title}` (5 × 3 × 2 = 30)
- `{bert}_正面_w_{full,ctx,title}` / `{bert}_负面_w_{full,ctx,title}` (5 × 3 × 2 = 30)
- `llm_prob_score_w_{full,ctx,title}`

### 13.2 bank-year VW sum 列（聚合后）

模板：`{prefix}_w_sum_{track}`：
- `llm_vote_score_w_sum_{track}` / `llm_vote_cont_w_sum_{track}`
- `pos_count_vw_{track}` / `neg_count_vw_{track}`
- `{model}_score_w_sum_{track}` / `{model}_cont_w_sum_{track}`
- `{dict}_score_w_sum_{track}` / `{dict}_idf_score_w_sum_{track}`
- `{bert}_正面_w_sum_{track}` / `{bert}_负面_w_sum_{track}`
- `llm_prob_score_w_sum_{track}`

### 13.3 VW tone（除以 sum_mention_density 后的最终 VW 指标）

模板：`{prefix}_vw_{track}` 或 `{prefix}_tone_vw_{track}`：
- `llm_vote_tone_vw_{full,ctx,title}` / `llm_vote_cont_vw_{full,ctx,title}`
- `{model}_tone_vw_{full,ctx,title}` (3 × 3 = 9)
- `{dict}_tone_vw_{full,ctx,title}` / `{dict}_idf_tone_vw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `{bert}_pos_vw_{full,ctx,title}` / `{bert}_neg_vw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `llm_vote_tone_vw_prob_{full,ctx,title}`

---

## 14. M Media-Authority-Weighted (MW) 加权聚合

**整体说明**：与 VW 同模式，权重换成 `media_authority_weight`。锚定 Holzman et al. (2023, TAR)：高权威媒体对市场情感的边际贡献大。

### 14.1 篇章级 `_mw` 列
完全对称 §13.1，把所有 `_w` 替换为 `_mw`。

### 14.2 bank-year MW tone
- `llm_vote_tone_mw_{full,ctx,title}` / `llm_vote_cont_mw_{full,ctx,title}`
- `{model}_tone_mw_{full,ctx,title}` (3 × 3 = 9)
- `{dict}_tone_mw_{full,ctx,title}` / `{dict}_idf_tone_mw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `{bert}_pos_mw_{full,ctx,title}` / `{bert}_neg_mw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `llm_vote_tone_mw_prob_{full,ctx,title}`

---

## 15. N Herd-Decay-Weighted (HW) 加权聚合

**整体说明**：v3.6.0 Plan E P1 B3 BREAKING 设计——`_full` 用 `herd_weight_full`、`_ctx` 用 `herd_weight_ctx`、`_title` 用 `herd_weight_full` fallback。这是 measurement-treatment matching（Edwards 2001 ORM）。原 v3.5.x 单列 `herd_weight` 会在新版触发 `legacy fake-dual` warning，需重跑 stage 24。

### 15.1 篇章级 `_hw` 列
对称 §13.1 / §14.1，把所有 `_w` / `_mw` 替换为 `_hw`。

### 15.2 bank-year HW tone
- `llm_vote_tone_hw_{full,ctx,title}` / `llm_vote_cont_hw_{full,ctx,title}`
- `{model}_tone_hw_{full,ctx,title}` (3 × 3 = 9)
- `{dict}_tone_hw_{full,ctx,title}` / `{dict}_idf_tone_hw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `{bert}_pos_hw_{full,ctx,title}` / `{bert}_neg_hw_{full,ctx,title}` (5 × 3 × 2 = 30)
- `llm_vote_tone_hw_prob_{full,ctx,title}`

---

## 16. O 创新属性三维标签（项目灵魂）

**整体说明**：每篇 fintech 新闻在 stage 21 的 prompt v8 中被独立打三组对偶范畴标签，构成 2×2×2 = 8 cell。三维度的正交性由 stage 39c NMI ≤ 0.15 验证。`_full` 与 `_ctx` 各跑一次 prompt，独立判定后投票——**双轨独立性是 ctx 可作 main spec 的关键**（plan v14 §3.1 R1-A）。

`stata_export.py::encode_categorical_columns()` 把中文字符串列 → `Int8` byte，附加 value labels（须 `do labels.do` 才会显示中文）。

### 16.1 innovation_locus — Gomber 2018 JMIS（locus 维度）

| 变量 | 编码 | 含义 |
|---|---|---|
| `innovation_locus_{full,ctx}` | `0 = 底层技术 (Enabling Technology)` / `1 = 应用场景 (Business Function)` | 这条新闻讲的是底层 fintech 技术，还是面向客户的业务应用 |

聚合方式：`majority_vote_3LLMs(innovation_locus | {full/ctx} prompt) + canonicalize_topic crossvalidation`，详见 [tone_llms.py](../pipeline/sentiment/tone_llms.py)。

### 16.2 innovation_substantiveness — W&Z 1998 ASQ（"洗稿率"框架源头）

| 变量 | 编码 | 含义 |
|---|---|---|
| `innovation_substantiveness_{full,ctx}` | `0 = 实质性 (Substantive)` / `1 = 象征性 (Symbolic)` | "实质性 = 真做事；象征性 = 洗稿"——主回归 treatment 焦点 |

### 16.3 innovation_collab_mode — Chesbrough 2003 + L&S 2006 SMJ（v3.4.0 第三维度）

| 变量 | 编码 | 含义 |
|---|---|---|
| `innovation_collab_mode_{full,ctx}` | `0 = 自主研发 (Closed Innovation)` / `1 = 外部协同 (Open Innovation)` | tie → 自主研发（uniform prior MAP） |

### 16.4 内在含义解读（**深度增强 — 项目灵魂**）

**为什么是三维而非一维**：传统金融文本研究只测 sentiment（好/坏），但中国银行金融科技战略选择有 **3 个正交决策维度**：
1. **Locus** = "做哪一层" → 底层技术（区块链 / AI 算法 / 云架构）vs 应用场景（信贷审批 / 客户服务 / 营销）
2. **Substantiveness** = "真做 vs 装做" → 实质性投入（自研 + 落地）vs 象征性宣示（PR 公告）
3. **Collab mode** = "自己做还是合作" → 自主研发 vs 外部协同（与 BigTech / 金融科技公司合作）

三维笛卡尔积 = 8 个战略 cell（§18 D2 分解）。**洗稿率 = Pr(Substantiveness = 象征性 | 报道正面)** 是项目核心 treatment。

**为什么双轨独立**：
- _full 轨从全文判定 → 受"行业新闻借提银行名"污染（如"区块链火热，工行也在跟进"实际讲行业）；
- _ctx 轨从实体前后窗口判定 → Hassan et al. (2019 QJE) entity-proximity，**真正针对该银行**；
- 双轨独立 prompt（不是后处理）→ 让 ctx 轨可作 main spec（v3.6.0 G3 解锁）。

**编码方向 0=baseline / 1=对照的统计意义**：
- 主回归 `reghdfe Y D` 中 D 是 binary，coefficient 解读为"对照类相对 baseline 类的边际效应"；
- 1 = 对照 = "象征性 / 应用场景 / 外部协同" → 三者都是"较不实质"的方向；
- `tone_gap_sub_symb` = 实质性 tone − 象征性 tone > 0 意味着**实质性文章语调更正面**——这是 W&Z (1998 ASQ) decoupling 框架的反向证据（论文常假设 < 0，即"洗稿文章 PR 修饰更夸张"）。

**置信度列（§17 P）的用法**：
- `category_confidence_{full,ctx}` 是 LLM × keyword crossvalidation 杂交（+0.2 boost / ×0.5 penalty），是**最严格的判定信心**；
- 论文常做 `if category_confidence_ctx >= 0.7` 的子样本 robustness；
- `avg_il/iss/icm_confidence_*` 是纯 LLM verbalized confidence，更宽松。

**典型论文 spec（P3 substantiveness main）**：
```stata
* Main: 象征性比例对 outcome 的影响
reghdfe Y symb_frac_sc loss_controls, absorb(target_bank year) cluster(bank_province)

* 稳健性 1: 用 tone gap 替代
reghdfe Y tone_gap_sub_symb_sc_ctx loss_controls, absorb(target_bank year)

* 稳健性 2: 高置信度子样本
reghdfe Y symb_frac_sc loss_controls if category_confidence_ctx >= 0.7, ///
    absorb(target_bank year)

* 稳健性 3: 双轨都通过验证
reghdfe Y symb_frac_sc loss_controls if llm_verified_dual_both == 1, ///
    absorb(target_bank year)
```

**常见使用陷阱**：
- ⚠ **不要混用 _full × _ctx**：例如 `llm_vote_tone_full × innovation_substantiveness_ctx` 是 measurement-treatment mismatch（Edwards 2001 ORM），plan v14 §2.2 明令禁止；
- ⚠ **n_articles < 5 子集 NaN**：`tone_gap_*` 在样本量过小的 bank-year 强制 NaN（防 compositional confound），Stata 端会自动 listwise drop；
- ⚠ **cell_id baseline cell 1**：回归把 cell 1 (sub.tech.indep) 作为 omitted baseline，其他 7 cell 系数解读为"相对 cell 1 的边际效应"。

---

## 17. P 创新属性置信度

见 [§9 H LLM 置信度](#9-h-llm-置信度) 中 `avg_il/iss/icm_confidence_{full,ctx}` + `category_confidence_{full,ctx}` + `innovation_collab_mode_confidence_{full,ctx}` 系列。

---

## 18. Q D2 八格分解 + D4 双轨残差

**整体说明**：v3.5.0 Stage 3 augmentation 的两个核心扩展，由 [encode_collab.py](../pipeline/panel/encode_collab.py) `apply_v3_5_0()` 在 panel 聚合后追加。

### 18.1 D2 八格分解（Sun & Abraham 2021 JOE cohort decomposition 类比）

公式：`cell_id = subst*4 + locus*2 + collab + 1 ∈ {1..8}`。baseline (cell 1) = (0, 0, 0) = 实质性·底层技术·自主研发。

#### 篇章级
| 变量 | 取值 | 含义 |
|---|---|---|
| `cell_id_full` | `Int8` nullable ∈ {1..8} | 三维 8 cell 编码（full 轨） |
| `cell_id_ctx` | `Int8` nullable ∈ {1..8} | 三维 8 cell 编码（ctx 轨） |

#### bank-year 8 cell 计数（基于 cell_id_full）
| 变量 | value label | 含义 |
|---|---|---|
| `n_articles_cell_1_full` | `sub.tech.indep` | 三维全 baseline 篇章数 |
| `n_articles_cell_2_full` | `sub.tech.collab` | 实质性·底层技术·外部协同 |
| `n_articles_cell_3_full` | `sub.app.indep` | 实质性·应用场景·自主研发 |
| `n_articles_cell_4_full` | `sub.app.collab` | 实质性·应用场景·外部协同 |
| `n_articles_cell_5_full` | `symb.tech.indep` | 象征性·底层技术·自主研发 |
| `n_articles_cell_6_full` | `symb.tech.collab` | 象征性·底层技术·外部协同 |
| `n_articles_cell_7_full` | `symb.app.indep` | 象征性·应用场景·自主研发 |
| `n_articles_cell_8_full` | `symb.app.collab` | 三维全 contrast 篇章数（最强洗稿信号） |

#### 恒等式校验（plan §2.1.2）
- 主：`n_articles == Σ n_articles_cell_{1..8}_full`
- 交叉：
  - `n_articles_indep == n_articles_cell_{1,3,5,7}_full`
  - `n_articles_collab == n_articles_cell_{2,4,6,8}_full`

失败计数写入 `panel.attrs['v3_5_0_diagnostics']`。

### 18.2 D4 跨轨残差信号（Loughran & McDonald 2011 类比 + W&Z 2001 decoupling）

#### 篇章级（3 维 × 3 信号 = 9 列）
对每个 `dim ∈ {subst, locus, collab}`：
| 变量 | 公式 | 不变量 |
|---|---|---|
| `{dim}_disagree` | `(full != ctx) ∧ both_valid` | bool |
| `{dim}_freerider` | `(full == baseline) ∧ (ctx == contrast)` | full 看着保守、ctx 暴露激进 |
| `{dim}_quietworker` | `(full == contrast) ∧ (ctx == baseline)` | full 看着激进、ctx 体现保守 |

不变量：(i) freerider + quietworker ≤ 1（互斥）；(ii) freerider + quietworker == disagree（定义式）；(iii) NaN propagation。

#### bank-year（3 维 × 3 信号 × 2 metric = 18 列）

| 变量模板 | 公式 |
|---|---|
| `{dim}_{signal}_frac` | `mean({dim}_{signal})`，`n_articles < 5` → `pd.NA` |
| `n_articles_{dim}_{signal}` | `sum({dim}_{signal}).astype('Int32')` |

展开为：`subst_disagree_frac / subst_freerider_frac / subst_quietworker_frac / locus_disagree_frac / locus_freerider_frac / locus_quietworker_frac / collab_disagree_frac / collab_freerider_frac / collab_quietworker_frac` + 9 个 `n_articles_*` 计数版。

#### 数据质量旗
| 变量 | 取值 | 含义 |
|---|---|---|
| `d4_data_quality_flag` | str ∈ {`ok`, `insufficient`} | ctx coverage 不足时 → `insufficient`，Stata 端 `keep if d4_data_quality_flag == "ok"` |

---

## 19. R Dual Gate 三互斥指示

**整体说明**：plan v14 §3.1 R1-A 致命修复——把"双轨都过"的严苛 AND 改为并集 `verified_full ∪ verified_ctx`，让 ctx-only 通过的 bank-year 也能独立作 main spec。锚定 Hassan et al. (2019, QJE) entity-proximity 独立性。

| 变量 | 公式 | 含义 |
|---|---|---|
| `llm_verified_dual_full_only` | `verified_full ∧ ¬verified_ctx` | 仅 full 轨通过验证 |
| `llm_verified_dual_ctx_only` | `verified_ctx ∧ ¬verified_full` | 仅 ctx 轨通过验证 |
| `llm_verified_dual_both` | `verified_full ∧ verified_ctx` | 两轨都通过（最强证据） |

---

## 20. S 三维 × tone 子集对角线

**整体说明**：把篇章按三维标签拆子集，每个子集内再算情感 / 概率 / 篇数。同维 × 同轨配对的"对角线规则"避免跨轨杂交（plan v14 §2.2）：
- `_full` 轨情感 × `_full` 轨标签（隐式 `_lf` / `_sf` / `_cmf`，省略后缀直接 `_tech` / `_sub` / `_indep` 等）
- `_ctx` 轨情感 × `_ctx` 轨标签（显式 `_lc_ctx` / `_sc_ctx` / `_cm_ctx`）

当 `min(n_a, n_b) < 5` 时 gap 列强制 NaN（v3.1.1 R8 audit 防 compositional confound）。

### 20.1 locus 子集（_full 轨标签）

| 篇数 | 比例 | LLM 投票 tone | 模型逐拆 | Cont/Prob |
|---|---|---|---|---|
| `n_articles_tech` / `n_articles_app` | `tech_frac` / `app_frac` | `llm_vote_tone_tech_{full,ctx,title}` / `llm_vote_tone_app_{full,ctx,title}` | `{model}_tone_tech_{full,ctx}` / `{model}_tone_app_{full,ctx}` | `llm_vote_cont_tech_{track}` / `llm_prob_score_tech_{track}` |

还有：
- 词典子集均值：`{dict}_tone_tech_{full,ctx,title}` / `{dict}_tone_app_{full,ctx,title}` (5×3×2=30)
- 词典 IDF：`{dict}_idf_tone_tech_{track}` / `{dict}_idf_tone_app_{track}` (5×3×2=30)
- BERT：`{bert}_pos_tech_{full,ctx,title}` / `{bert}_neg_tech_{full,ctx,title}` (5×3×2=30) + 对应 _app
- 3-class BERT 中性：`{bert}_neu_tech_{full,ctx,title}` / `{bert}_neu_app_{full,ctx,title}` (3×3×2=18)

### 20.2 locus 子集（_ctx 轨标签，Hassan 2019 entity-proximity）

| 篇数 | 比例 | LLM 投票 tone | Prob |
|---|---|---|---|
| `n_articles_tech_lc_ctx` / `n_articles_app_lc_ctx` | `tech_frac_lc` / `app_frac_lc` | `llm_vote_tone_tech_lc_ctx` / `llm_vote_tone_app_lc_ctx` | `llm_prob_score_tech_lc_ctx` / `llm_prob_score_app_lc_ctx` |

### 20.3 substantiveness 子集（_full 轨标签）

| 篇数 | 比例 | LLM 投票 tone | 模型逐拆 | Prob |
|---|---|---|---|---|
| `n_articles_sub` / `n_articles_symb` | `sub_frac` / `symb_frac` | `llm_vote_tone_sub_{full,ctx,title}` / `llm_vote_tone_symb_{full,ctx,title}` | `{model}_tone_sub_{full,ctx}` / `{model}_tone_symb_{full,ctx}` (3×2×2=12) | `llm_prob_score_sub_{full,ctx,title}` / `llm_prob_score_symb_{full,ctx,title}` |

### 20.4 substantiveness 子集（_ctx 轨标签）

| 篇数 | 比例 | LLM 投票 tone | Prob |
|---|---|---|---|
| `n_articles_sub_sc_ctx` / `n_articles_symb_sc_ctx` | `sub_frac_sc` / `symb_frac_sc` | `llm_vote_tone_sub_sc_ctx` / `llm_vote_tone_symb_sc_ctx` | `llm_prob_score_sub_sc_ctx` / `llm_prob_score_symb_sc_ctx` |

### 20.5 collab_mode 子集（_full 轨标签，v3.4.0）

| 篇数 | 比例 | LLM 投票 tone | 模型逐拆 | Prob |
|---|---|---|---|---|
| `n_articles_indep` / `n_articles_collab` | `indep_frac` / `collab_frac` | `llm_vote_tone_indep_{full,ctx,title}` / `llm_vote_tone_collab_{full,ctx,title}` | `{model}_tone_indep_{full,ctx}` / `{model}_tone_collab_{full,ctx}` (3×2×2=12) | `llm_prob_score_indep_{track}` / `llm_prob_score_collab_{track}` |

### 20.6 collab_mode 子集（_ctx 轨标签，v3.4.0）

| 篇数 | 比例 | LLM 投票 tone | Prob |
|---|---|---|---|
| `n_articles_indep_cm_ctx` / `n_articles_collab_cm_ctx` | `indep_frac_cm` / `collab_frac_cm` | `llm_vote_tone_indep_cm_ctx` / `llm_vote_tone_collab_cm_ctx` | `llm_prob_score_indep_cm_ctx` / `llm_prob_score_collab_cm_ctx` |

---

## 21. T Tone Gap 系列

**整体说明**：项目主回归 treatment 候选——同 bank-year 内不同子集的 tone 差。

| 变量 | 公式 | 含义 |
|---|---|---|
| `tone_gap_tech_app` | `llm_vote_tone_tech_full − llm_vote_tone_app_full`，`min(n_tech, n_app) ≥ 5` 否则 NaN | Tech − App 情感差（Adner & Kapoor 2010 SMJ） |
| `tone_gap_tech_app_lc_ctx` | ctx 轨同向 | ctx 版 tech-app gap |
| `tone_gap_sub_symb` | `llm_vote_tone_sub_full − llm_vote_tone_symb_full` | Substantive − Symbolic 情感差（**洗稿率核心**） |
| `tone_gap_sub_symb_sc_ctx` | ctx 轨同向 | ctx 版 sub-symb gap（论文 ctx main spec 主指标） |
| `tone_gap_indep_collab` | `llm_vote_tone_indep_full − llm_vote_tone_collab_full` | 自主 − 协同情感差（v3.4.0） |
| `tone_gap_indep_collab_cm_ctx` | ctx 轨同向 | ctx 版 collab gap |
| `tone_gap_symb_sub_{full,ctx}` | `llm_vote_tone_symb − llm_vote_tone_sub`（反向 gap） | Washing Ratio 方法 C 衍生指标 |
| `tone_gap_title_full` | `llm_vote_tone_title − llm_vote_tone_full` | 标题-全文情感缺口（标题党检测） |

### 21.1 内在含义解读（**深度增强 — 主回归 treatment 候选**）

**经济学直觉**：tone gap 度量"同一银行同年内**不同类别新闻之间**的语调差异"。这是**议题异质性**（issue heterogeneity）信号，远比单一 tone 均值更精准。

**3 个核心 gap 的论文用法**：

| Gap 名 | 度量什么 | 论文用作 |
|---|---|---|
| `tone_gap_tech_app` | 底层技术 vs 应用场景的语调差 | Adner & Kapoor (2010 SMJ) 生态系统位点效应；P4 paper main |
| `tone_gap_sub_symb_sc_ctx` | **实质性 vs 象征性的语调差**（ctx 轨）| **洗稿率核心指标**；P3 paper main 与 P1 secondary |
| `tone_gap_indep_collab_cm_ctx` | 自主 vs 协同的语调差 | Chesbrough (2003) open innovation；P5 paper main |

**经济学符号预期**：
- `tone_gap_sub_symb` **常常 > 0**（实质性文章语调更正）——这是 Westphal & Zajac (1998 ASQ) "decoupling 正向标签"的反向：实做的人也实说，洗稿的人话术更虚；
- 若实证发现 `tone_gap_sub_symb < 0` → 强 PR 主导市场 → 论文需要在 Discussion 节解释（典型 Bingler et al. 2022 FRL 的 cheap talk 情景）；
- `tone_gap_title_full > 0` → 标题党（标题更正面），是 SEC Form 10-K 文献的经典指标；

**n_articles 门控的统计意义**：
- `min(n_a, n_b) >= 5` 是 compositional confound 防御。原理：当某子集仅有 1-2 篇时，子集均值受单篇极值主导（high variance）→ gap 估计 unbiased 但方差爆炸 → 错误结论；
- 这个 gate 让稀疏 bank-year 自动 NaN drop，确保回归 SE 准确。

**典型 Stata 用法（P3 main spec）**：
```stata
* Main: 实质-象征 tone gap 对 outcome 的影响（ctx main）
reghdfe Y tone_gap_sub_symb_sc_ctx controls, absorb(target_bank year) cluster(bank_province)

* 稳健性: full 轨
reghdfe Y tone_gap_sub_symb controls, absorb(target_bank year)

* 稳健性: 提高门控
reghdfe Y tone_gap_sub_symb_sc_ctx controls if n_articles_sub_sc_ctx >= 10 & n_articles_symb_sc_ctx >= 10, ///
    absorb(target_bank year)

* 异质性: 国有 vs 非国有
reghdfe Y c.tone_gap_sub_symb_sc_ctx##i.is_soe controls, absorb(target_bank year)
```

**常见使用陷阱**：
- ⚠ **样本量缺失**：因 `min ≥ 5` 自动 NaN，论文报告时必须披露**回归样本量**远小于 panel 总行数（典型 4608 → ~1800-2400）；
- ⚠ **方向解释错误**：`tone_gap_sub_symb` > 0 不是"实质性更好"，而是"实质性文章语调相对更正"——这是**信号** 而非**结果**；
- ⚠ **不要平均双轨**：`(tone_gap_sub_symb + tone_gap_sub_symb_sc_ctx) / 2` 在统计上**没有意义**（两个独立估计的简单平均不是 MLE），论文应分别报告两套结果。

---

## 22. U 洗稿率 4-way 计数 + Washing Ratio 10 变体

**整体说明**：sentiment × substantiveness 笛卡尔积。"正面 × 象征性 = 洗稿信号"；"负面 × 实质性 = 真问题暴露"。
锚定：Bingler et al. (2022, FRL) cheap talk + Deephouse (2000, J Mgmt) reverse-validation。

### 22.1 篇章级前置标记（runner.py:391-528）

每 track ∈ `{_full, _ctx}` × 7 方法 = ~70 个 `_is_*` 篇章级 bool 列（不直接进 .dta，做完后被 `df.drop(columns=_tmp_cols)`）。但 bank-year 聚合后保留为 count 列：

| 4-way count（核心） | 公式 |
|---|---|
| `pos_symb_count_{full,ctx}` | LLM 投票正面 ∩ substantiveness_full=象征性 |
| `neg_sub_count_{full,ctx}` | LLM 投票负面 ∩ substantiveness_full=实质性 |

### 22.2 Washing Ratio 10 变体 × 2 轨 = 20+ 列（runner.py:1273-1372）

约定：`_full` 主指标省略后缀，`_ctx` 加 `_ctx` 后缀。

| 方法 | 变量名 | 公式 |
|---|---|---|
| A | `washing_ratio` / `washing_ratio_ctx` | `pos_symb_count / pos_count`（LLM 投票） |
| A2 | `washing_ratio_{gpt54nano,gemini31111,deepseekv4}` (+ `_ctx`) | `{llm}_pos_symb_count / {llm}_pos_count`（3 模型 × 2 轨 = 6 列） |
| B | `neg_sub_ratio_{full,ctx}` | `neg_sub_count / neg_count` |
| B'| `washing_asymmetry_{full,ctx}` | `neg_sub_ratio − (1 − washing_ratio)`（Deephouse 2000 非对称） |
| C | `tone_gap_symb_sub_{full,ctx}` | `llm_vote_tone_symb − llm_vote_tone_sub`（情感纯度缺口） |
| D | `washing_ratio_dict` / `washing_ratio_dict_ctx` | `dict_pos_symb_count / dict_pos_count`（词典综合） |
| D2 | `washing_ratio_{jiang_2021,yao_2021,bian_2021,du_2022,you_2018}` (+ `_ctx`) | 5 词典 × 2 轨 = 10 列 |
| E | `washing_ratio_bert` / `washing_ratio_bert_ctx` | `bert_pos_symb_count / bert_pos_count` |
| E2 | `washing_ratio_{finbert_cn,fin_sent_zh,erlangshen,hw2942,finbert2}` (+ `_ctx`) | 5 BERT × 2 轨 = 10 列 |
| F | `washing_ratio_hc` / `washing_ratio_hc_ctx` | `pos_symb_hc_count / pos_hc_count`（高置信度） |
| G | `washing_tone_shift_{full,ctx}` | `llm_vote_tone_symb − llm_vote_tone`（象征性篇章情感偏移） |

### 22.3 No-positive dummy
| 变量 | 公式 |
|---|---|
| `dummy_no_positive_news` | `(pos_count_full.fillna(0) <= 0).astype(int)` |

### 22.4 内在含义解读（**项目核心概念：洗稿率**）

**洗稿率（Washing Ratio）定义**：`WR = #{正面 ∩ 象征性} / #{正面}` = "**正面新闻中有多大比例是象征性 PR**"。

经济学直觉：
- WR = 0 → 所有正面新闻都讲实质（理想）；
- WR = 1 → 正面新闻全是 PR 洗稿（极端洗稿）；
- 实际 panel 中 WR 通常 ∈ [0.15, 0.60]，分布右偏。

**为什么用 4 way 计数**：
- `pos_symb_count`（洗稿信号正头）vs `neg_sub_count`（真问题暴露反头）——前者 → 洗稿率分子；后者 → "**反向验证**"（reverse-validation, Deephouse 2000 J Mgmt）防御 LLM 偏见；
- `washing_asymmetry = neg_sub_ratio − (1 − washing_ratio)` 度量"正负两侧不对称"，> 0 → 实质性的语调更尖锐（与象征性的温和形成对比）。

**10 种 washing ratio 变体的统计意义**：
- 方法 A（LLM 投票）→ main；
- 方法 A2（3 个单模型）→ inter-rater reliability 稳健性；
- 方法 D2（5 个单词典）→ method-source robustness；
- 方法 E2（5 个 BERT）→ deep-model robustness；
- 方法 F（高置信子样本）→ measurement-quality robustness；
- 方法 G（情感偏移 tone_shift）→ continuous version (vs binary ratio)。

10 方法 × 2 轨 = 20+ 列让论文可以做 Romano-Wolf 多重检验校正后的"方法稳健性表"。

**典型 Stata spec**：
```stata
* P1/P3 paper Main: washing ratio (LLM 投票, ctx)
reghdfe Y washing_ratio_ctx controls, absorb(target_bank year) cluster(bank_province)

* Romano-Wolf 多重稳健性: 10 方法
rwolf reghdfe Y i.D controls, ///
    indepvars(washing_ratio washing_ratio_ctx washing_ratio_dict washing_ratio_bert ///
              washing_ratio_jiang_2021 washing_ratio_yao_2021 washing_ratio_hc) ///
    absorb(target_bank year) reps(1000) seed(42)
```

**陷阱**：
- ⚠ **分母 0**：当 bank-year 全无正面新闻时 `pos_count = 0` → 分母为 0 → NaN（`_safe_ratio` 已处理），但论文样本量会缩小；可用 `dummy_no_positive_news` 控制；
- ⚠ **substantiveness 来自 full 轨**：washing ratio 默认基于 `innovation_substantiveness_full`；ctx 版用 `_sc` 后缀的 4-way 计数（runner.py:496-528 派生 `pos_symb_*_sc` 系列）。

---

## 23. V Lexical Clarity (v3.5.1 A1)

**整体说明**：LM 2011 JF uncertain + You et al. (2018) hhx055 Panel C (388 definite) / Panel D (178 ambiguous) 字典；**真双轨独立扫描** `content_full` 与 `content_ctx`。title 轨故意不纳入（title <50 字分母不稳，修 R3-H1）。

锚定：Loughran & McDonald (2011) JF 66(1); You et al. (2018) hhx055; Bonsall, Leone, Miller, Rennekamp (2017) JAE 63(2-3)。

### 23.1 篇章级（stage 22）
| 变量 | 含义 |
|---|---|
| `clarity_frac_definite_{full,ctx}` | You 2018 Panel C definite 词频比 |
| `clarity_frac_ambiguous_{full,ctx}` | You 2018 Panel D ambiguous 词频比 |
| `clarity_clarity_score_{full,ctx}` | `frac_definite − frac_ambiguous` ∈ [−1, +1] |

### 23.2 bank-year（encode_collab.aggregate_clarity_panel）
| 变量 | 公式 | 范围 |
|---|---|---|
| `mean_clarity_score_full` | `Σ w_i × clarity_score_full_i / Σ w_i` | [−1, 1] |
| `mean_clarity_score_ctx` | 同上 ctx 轨 | [−1, 1] |
| `mean_frac_definite_full` | `Σ w_i × frac_definite_full / Σ w_i` | [0, 1] |
| `mean_frac_definite_ctx` | 同上 ctx | [0, 1] |
| `frac_amb_articles_full` | `#{i: frac_ambiguous_full_i ≥ median_amb_d0 ∧ n_articles ≥ 2} / n_articles` | [0, 1] ∪ NaN |
| `frac_amb_articles_ctx` | 同上 ctx | [0, 1] ∪ NaN |

权重：`w = media_authority_weight × herd_decay_weight`。`median_amb_d0` 是 D0 frozen 全样本中位数，写入 sidecar `data/processed/v3_5_1_constants.json`。

---

## 24. W Numerical Intensity (v3.5.1 A3)

**整体说明**：Hales-Kuang-Venkataraman (2011, CAR 28:1) 数字披露强度。中文用 `cn2arab` 5 标准样例转化（D0 frozen）；不定数（"几千 / 数十亿"）不计为 token（修 R7-M2）。

### 24.1 篇章级
| 变量 | 公式 | 单位 |
|---|---|---|
| `num_intensity_full` | `n_digits_full / n_sentences_full`（lookahead/behind 排除小数点）| digits/sentence |
| `num_intensity_ctx` | 同上 ctx | digits/sentence |

### 24.2 bank-year（encode_collab.aggregate_num_intensity_panel）
| 变量 | 公式 | 范围 |
|---|---|---|
| `mean_num_intensity_full` | `Σ w_i × num_intensity_full_i / Σ w_i` | [0, +∞) |
| `mean_num_intensity_ctx` | 同上 ctx | [0, +∞) |

权重同 §23.2。

---

## 24bis 中间篇章列（不进 panel，但 stage 22 parquet 保留）

stage 22 `22_words_tone.parquet` 包含若干**篇章级**计数列，它们仅供 [`encode_collab.py`](../pipeline/panel/encode_collab.py) 在 panel 聚合时使用，**最终不进 bank-year panel**（不进 `46_*.dta` 三件套）：

| 篇章列 | 用途（agg → panel） |
|---|---|
| `clarity_n_definite_{full,ctx}` / `clarity_n_ambiguous_{full,ctx}` / `clarity_n_tokens_clarity_base_{full,ctx}` | 用于聚合 `mean_clarity_score_{full,ctx}` / `mean_frac_definite_*` / `frac_amb_articles_*`（§23.2） |
| `n_uncert` / `n_litig` / `n_constr` / `n_modal_strong` | 用于聚合 `uncert/litig/constr/modal_strong_frac_{full,ctx}`（§25） |
| `n_sentences` / `n_fls_sentences` | 用于聚合 `frac_fls_{full,ctx}`（§26） |

研究者若要在 stage 22 parquet 上直接做篇章级分析（非 bank-year），可以读这些中间列。但 Stata `.dta` 是 bank-year 长面板，已聚合后这些原始计数不存在。

---

## 25. X LM 2011 JF 4 子词典 (v3.5.2 A1)

**整体说明**：v3.5.2 PR #2 引入的 LM 4 子词典 v0.1.5（覆盖 14–41% LM 英文原版词汇，待专家审定 v0.2）。模块：[lm_non_sentiment.py](../pipeline/sentiment/lm_non_sentiment.py)。

锚定：Loughran & McDonald (2011) JF 66(1) non-sentiment dictionaries。

| 变量 | 子词典含义 | 词数 |
|---|---|---|
| `uncert_frac_full` / `uncert_frac_ctx` | 不确定性词频比（uncertain） | 83 |
| `litig_frac_full` / `litig_frac_ctx` | 诉讼/法律词频比（litigious） | 104 |
| `constr_frac_full` / `constr_frac_ctx` | 约束/合规词频比（constraining） | 76 |
| `modal_strong_frac_full` / `modal_strong_frac_ctx` | 强情态词频比（modal-strong） | 51 |

合计 8 列。bank-year 聚合方式：篇章级 `Σ w_i × frac_i / Σ w_i` 加权平均（与 clarity 同权重）。

---

## 26. Y Forward-Looking Statements / FLS (v3.5.2 A2)

**整体说明**：Li 2010 JAR FLS 双门控：future 词（72） ∧ time 词（59），**同句出现**才计为 FLS = 131 词模板。模块：[forward_looking.py](../pipeline/sentiment/forward_looking.py)。

| 变量 | 公式 | 范围 |
|---|---|---|
| `frac_fls_full` | bank-year 中含 FLS 句子的篇章占比 | [0, 1] |
| `frac_fls_ctx` | 同上 ctx 轨 | [0, 1] |

---

## 27. Z Herd Decay 双轨 (v3.6.0 B3)

**整体说明**：媒体扎堆衰减权重——当多家媒体在短时窗内复述同一事件，权重指数衰减。v3.6.0 BREAKING：替换 v3.5.x 单列 `herd_weight`，强制 measurement-treatment matching（Edwards 2001 ORM）——全文相似度 ≠ 对目标银行的报道相似度。

锚定：Tetlock (2011, RFS) 媒体新闻冗余 + return reversal；Sautner et al. (2023, JF) 文本相似度曝光度；Edwards (2001, ORM) measurement-treatment matching。

### 27.1 算法参数（[herd_decay.py:66-74](../pipeline/sentiment/herd_decay.py#L66-L74)）

| 参数 | 默认 | 含义 |
|---|---|---|
| `SIMILARITY_THRESHOLD` | 0.35 | 高于此 cosine 相似度视为"跟风" |
| `TIME_WINDOW_DAYS` | 7 | 同 target_bank 内时间窗 |
| `MAX_FEATURES` | 10000 | TF-IDF 维度封锁（峰值内存 < 30 GB） |
| `MIN_DF` / `MAX_DF` | 5 / 0.9 | TF-IDF 词频过滤 |
| 衰减公式 | `weight = 1 / (1 + n_similar_predecessors)` | 1 → 完全独立；< 1 → 复述新闻 |
| analyzer | `char_wb` ngram(2, 4) | 中文友好 |

### 27.2 篇章级输出（stage 24 → `24_herd_decay.parquet`）

| 变量 | 含义 |
|---|---|
| `herd_weight_full` | `_full` 轨（对'内容'TF-IDF 相似度）单篇衰减权重 ∈ [0, 1] |
| `herd_weight_ctx` | `_ctx` 轨（对 `content_ctx` TF-IDF）同向衰减权重 |
| `n_similar_articles_full` | 时窗内（同 bank）相似篇数 |
| `n_similar_articles_ctx` | 同上 ctx 轨 |

**注意**：v3.5.x 旧单列 `herd_weight` **已删除**，下游必须显式指定 `_full` / `_ctx`；新代码若意外使用 legacy 列会触发 [build_aggregation_dict() WARN](../pipeline/panel/encode.py#L625-L630)。

### 27.3 bank-year 聚合
| 变量 | 公式 |
|---|---|
| `avg_herd_weight_full` / `avg_herd_weight_ctx` | bank-year mean |
| `min_herd_weight_full` / `min_herd_weight_ctx` | bank-year min（最孤立报道） |
| `sum_herd_weight_full` / `sum_herd_weight_ctx` | bank-year sum（HW 加权分母，[encode.py:645-646](../pipeline/panel/encode.py#L645-L646)） |

---

## 28. AA Policy Alignment 双轨 (v3.6.0 B2)

**整体说明**：每篇文章对当年政策文本（央行/银保监公告）的语义对齐度，OpenAI embedding 余弦相似度。v3.6.0 BREAKING：cache key `-dual` 局部 namespace 隔离，~$4 LLM 成本完成真双轨。

### 28.1 篇章级（stage 15 → 15_article_alignment.parquet）
| 变量 | 含义 |
|---|---|
| `policy_cosine_sim` | legacy 单轨（v3.5.x 保留） |
| `policy_cosine_sim_full` | 全文 vs 政策文本余弦 |
| `policy_cosine_sim_ctx` | ctx vs 政策文本余弦 |

### 28.2 bank-year
| 变量 | 公式 |
|---|---|
| `article_sim_mean` | `mean(policy_cosine_sim)` |
| `article_sim_std` | `std(policy_cosine_sim)`，单篇 → 0 |

---

## 29. AB Fintech Intensity 双轨 (v3.6.0 B1)

**整体说明**：fintech 关键词密度 × TF-IDF × SIF 加权 × LLM 二次验证，是 P2 paper attention 主 treatment。v3.6.0 stage 13 先物化 `content_ctx` 列，让 stage 14 能真双轨化。

锚定：Li, Sun, Wang & Yannelis (2021, RFS) FinTech intensity score; Abraham, Olbert & Vasvari (2024, JAR) 相对披露密度。

### 29.1 篇章级（stage 14 → 14_fintech_intensity.parquet）
| 变量 | 含义 |
|---|---|
| `fintech_intensity_score` | legacy 单轨（v3.6.0 alias 到 _full 保留） |
| `fintech_intensity_score_full` | `_full` 轨 fintech 强度（0–1） |
| `fintech_intensity_score_ctx` | `_ctx` 轨 fintech 强度 |
| `intensity_verified` | legacy 单轨 LLM 二次验证 binary（gate） |
| `intensity_verified_full` | `_full` 轨 LLM 验证 |
| `intensity_verified_ctx` | `_ctx` 轨 LLM 验证 |
| `fintech_distinct_keywords` | 独立 fintech 关键词数（去重） |
| `fintech_total_count` | fintech 关键词总出现次数 |
| `_ft_word_ratio` | `fintech_total_count / doc_length`（Abraham 2024） |

### 29.2 bank-year
| 变量 | 公式 |
|---|---|
| `avg_ft_intensity` (+ `_std`) | legacy 单轨 mean/std |
| `avg_ft_intensity_full` (+ `_std`) | `_full` 轨 mean/std |
| `avg_ft_intensity_ctx` (+ `_std`) | `_ctx` 轨 mean/std |
| `avg_ft_word_ratio` (+ `_std`) | 纯关键词比例（未经 LLM 验证的对照） |
| `fintech_intensity_mean` | stage 45 7h-token 块产出的 mean（与 article_sim 一起 merge） |

---

## 30. AC EPU 经济政策不确定性 (v3.6.1 B1)

**整体说明**：[`epu_merge.py`](../pipeline/external/epu_merge.py)（218 行）。Baker-Bloom-Davis (2016, QJE) 中国 EPU 月度时间序列按 `(year, month)` 合并到 article-level，然后 bank-year 聚合输出 4 列宏观控制。

数据源：`data/external/epu_china_monthly_2007_2024.csv`（schema：`year:int, month:int, epu:float`）。`epu_china_csv` 可在 `config/paths.yaml` 覆盖。

锚定：
- Baker, Bloom & Davis (2016, QJE 131(4), 1593-1636) DOI: 10.1093/qje/qjw024
- Davis, Liu & Sheng (2019, NBER WP) 中国 EPU since 1949

### 30.1 输出列契约（[epu_merge.py:30-36](../pipeline/external/epu_merge.py#L30-L36)）

| 变量 | 公式 | 含义 |
|---|---|---|
| `epu_mean_year` | 按文章发布月份加权的年内月度 EPU 均值（有 date 列时）；或简单年均值（year-only fallback） | 该 bank-year 暴露的平均政策不确定性 |
| `epu_year_end` | 该年 12 月 EPU（或 `.last()` fallback） | 年末 EPU snapshot |
| `epu_std_year` | 年内月度 EPU std | 年内不确定性波动 |
| `epu_data_complete` | `(年内 12 月数据完整).astype(int)` | 0/1 数据完整旗 |

### 30.2 失败模式（graceful fallback 三级）

| 触发 | 行为 |
|---|---|
| `epu_china_csv` 不存在 | 全 NaN + `epu_data_complete = 0`，stage 不阻塞下游 |
| schema 缺列（year/month/epu） | logger.error + 全 NaN |
| article_df 缺 date 列 | logger.warning + 仅按 year merge（fallback path） |
| 2023–2024 月份缺失（policyuncertainty.com 止于 2022 的 D-0 实测项） | `epu_data_complete = 0` + 由用户决定是否 last-12m rolling carry-forward + dummy 标记 |

### 30.3 D-0 实测项（v2.3 G-B1.1，待用户运行）

1. policyuncertainty.com 实际覆盖年份
2. 若止于 2022 → 2023-2024 用 last-12m rolling carry-forward + dummy 标记
3. 与 GDP / M2 多重共线性检验（要求 `|corr| < 0.7`）

---

## 31. AD BERTopic 主题聚焦度 (v3.7.0 D1)

**整体说明**：[`article_topic.py`](../pipeline/text/article_topic.py)（320 行）。SBERT 嵌入（stage 30a 持久化）+ UMAP + HDBSCAN + BERTopic 聚类，量化 bank-year 报道的主题聚焦度（HHI）。

锚定：
- Bybee, Kelly, Manela & Xiu (2024, RFS 37(3), 887-936) 商业新闻 narrative topic
- Hansen, McMahon & Prat (2018, QJE 133(2), 801-870) FOMC 计算语言学
- Grootendorst (2022, arXiv:2203.05794) BERTopic

立 P10 paper (narrative-novelty) 的核心方法。

### 31.1 算法参数（[article_topic.py:75-95](../pipeline/text/article_topic.py#L75-L95)）

| 模块 | 关键参数 |
|---|---|
| UMAP | `n_neighbors=15, n_components=5, min_dist=0.0, metric='cosine', random_state=42`（必锁种子） |
| HDBSCAN | `min_cluster_size=5000, metric='euclidean', cluster_selection_method='eom'` |
| CountVectorizer | `tokenizer=cn_tokenize (jieba + 200 词金融停用词), max_features=10000, min_df=10, max_df=0.95` |
| Embedding | `embedding_model=None`（绕过 BERTopic 默认 all-MiniLM 下载，HF 网络限制；用 stage 30a 持久化 SBERT） |

### 31.2 K 自动发现 + 双轨对齐机制

**K 是 HDBSCAN 在 400k 文章上自动发现的**：`min_cluster_size=5000` → 预期 K ≈ 15-30（实际值由 stage 17 runtime 决定，写入 sidecar `17_topic_metadata.json`，[article_topic.py:137](../pipeline/text/article_topic.py#L137)）。

**双轨对齐零 K-drift**：
- full 轨：`topic_model.fit_transform(docs_full, embeddings_full)` 决定 topic embeddings
- ctx 轨：`topic_model.transform(docs_ctx, embeddings_ctx)` **复用** full 轨已 fit 的 topic_model，强制 K 一致（hierarchical alignment）

### 31.3 篇章级输出（stage 17 → 3 parquet）

| 文件 | 用途 |
|---|---|
| `17_article_topics.parquet` | 篇章级 topic 分配 |
| `17_topic_info.parquet` | 每个 topic 的 c-TF-IDF top-10 词（用于专家解读） |
| `17_topic_panel.parquet` | bank-year 聚合层（直接 merge 进 panel） |

篇章级关键列：
| 变量 | 含义 |
|---|---|
| `topic_id_full` | `_full` 轨 BERTopic ID（-1 = outlier，已去除） |
| `topic_id_ctx` | `_ctx` 轨 BERTopic ID |
| `topic_prob_full` / `topic_prob_ctx` | 主题归属最大概率（HDBSCAN soft cluster） |

### 31.4 bank-year 聚合

| 变量 | 公式 | 含义 |
|---|---|---|
| `topic_hhi_full` | `Σ frac_topic_k²` over K topics（_full 轨） | 主题聚焦度 Herfindahl 指数，高 = 报道集中单一话题 |
| `topic_hhi_ctx` | 同上 ctx 轨 | ctx 主题聚焦度 |
| `frac_topic_0_full` … `frac_topic_{K-1}_full` | bank-year 内各 topic 的篇章占比（_full） | K 个比例列；K 在 runtime 确定 |
| `frac_topic_0_ctx` … `frac_topic_{K-1}_ctx` | 同上 ctx | K 个比例列 |

合计：**2 HHI + 2 × K 比例列 = 2 + 2K 列**。预期 K = 15–30 → **总 32–62 列**。

### 31.5 D-0 实测项（v2.3 G-D1.1）
BERTopic K 自动发现实际值 + c-TF-IDF top-10 词中文金融专家解读准确率 ≥ 80%。

---

## 32. AE Staleness 内容陈旧度 (v3.7.0 D2)

**整体说明**：[`article_staleness.py`](../pipeline/text/article_staleness.py)（332 行）。双指标互补——surface（字面层）+ semantic（语义层）。v3.7.0 PR #11.5（S1.3 修复）把 surface 算法从 O(N²) 灾难重写为按 unique-day 分组的滚动 LSH，**约 50000× 加速**（400k 文章从 10+ 天 → 5–15 分钟）。

锚定：
- Tetlock (2011, RFS 24(5), 1481-1512) "All the news that's fit to reprint" — 主指标用 cosine staleness + return reversal 实证
- Gentzkow, Shapiro & Taddy (2019, JEL 57(3), 535-574) Text as data

### 32.1 算法参数（[article_staleness.py:65-66](../pipeline/text/article_staleness.py#L65-L66)）

| 参数 | 值 |
|---|---|
| `WINDOW_DAYS` | 7 |
| `SHINGLE_SIZE` | 3 字符 n-gram |
| `num_perm` (MinHash) | 128 |
| **surface 算法** | datasketch `MinHashLSHForest` + 按 unique-day 分组的滚动 forest 重建 |
| **semantic 算法** | Faiss IVFFlat + SBERT cosine（复用 stage 30a embeddings） |
| 双轨 | content_full + content_ctx 各算一次 |

### 32.2 篇章级输出（stage 18 → 2 parquet）

| 文件 | 用途 |
|---|---|
| `18_article_staleness.parquet` | 篇章级 staleness |
| `18_staleness_panel.parquet` | bank-year 聚合层 |

| 变量 | 公式 | 边界行为 |
|---|---|---|
| `surface_staleness_full` | 过去 7d 窗口内 MinHash jaccard `max` | 第 1 周内文章 → NaN（无前 7d 邻居） |
| `surface_staleness_ctx` | 同上 ctx 轨 | 同上 |
| `semantic_staleness_full` | 过去 7d 窗口内 SBERT cosine `max` | 同上 |
| `semantic_staleness_ctx` | 同上 ctx 轨 | 同上 |

### 32.3 bank-year 聚合

| 变量 | 公式 |
|---|---|
| `surface_staleness_full` / `surface_staleness_ctx` | bank-year mean（同名列，复用篇章列名） |
| `semantic_staleness_full` / `semantic_staleness_ctx` | bank-year mean |

注：**当前实现只产出 mean 聚合**——`_std / _max / _median` 变体未实现（D2 plan 留作未来扩展）。如需，下游 Stata `tabstat` 自行计算。

### 32.4 D-0 实测项（v2.3 G-D2.1）

`corr(surface_staleness, semantic_staleness) ∈ [0.3, 0.7]` ——两指标必须互补而非冗余，否则方法论失效。

### 32.5 诊断列（不进 panel）

| 量 | 含义 |
|---|---|
| `staleness_corr` | panel-level surface vs semantic 相关性（写入日志 + sidecar，不进 panel 列） |

---

## 33. AF Krippendorff α 跨媒体分歧 (v3.7.0 D3)

**整体说明**：[`cross_media_alpha.py`](../pipeline/audit/cross_media_alpha.py)（296 行）。**与第 10 篇 `bank_media_disagreement` paper 对齐**：variance 作为 main treatment，α 作为 robustness——启用前必须与第 10 篇作者协调 spec。

锚定：
- Krippendorff (2004) *Content Analysis* — α 多标注者 reliability（比 Cohen κ 更稳健）
- Tetlock (2007, JF 62(3), 1139-1168) 跨多源 tone 一致性 = 信号质量代理

### 33.1 事件检测算法（[cross_media_alpha.py:77-100](../pipeline/audit/cross_media_alpha.py#L77-L100)）

| 参数 | 值 |
|---|---|
| `EVENT_WINDOW_DAYS` | ±3 days |
| `MIN_OUTLETS_PER_EVENT` | 2 |
| `N_ARTICLE_PERCENTILE` | 0.90 |

事件定义：`bank-year 内某 day 文章数 ≥ 该 bank 的 p90`。窗口取 `[event_date − 3, event_date + 3]`。

### 33.2 双数据结构（修 S2.3）

对每个 `(bank, event_date)` 三元组：
- `outlet_tones`：outlet-level tone 均值 **1D array** → 用于 variance 计算（与第 10 篇 main 对齐）
- `daily_matrix`：outlet × day matrix（raters × items，NaN 填充） → Krippendorff α 真正可用的 reliability_data 输入

### 33.3 bank-year 4 列

| 变量 | 公式 | 含义 |
|---|---|---|
| `cross_outlet_tone_variance_full` | bank-year 加权均值（按 event 内文章数）的 `var(outlet_tones)` | **第 10 篇 main treatment** |
| `cross_outlet_tone_variance_ctx` | 同上 ctx 轨 | ctx 版本 |
| `cross_media_alpha_full` | bank-year 加权均值的 Krippendorff α（interval scale） | α robustness，∈ [0, 1] |
| `cross_media_alpha_ctx` | 同上 ctx 轨 | ctx 版本 |

### 33.4 失败模式
| 触发 | 行为 |
|---|---|
| 该 (bank, event) 仅 1 家媒体（< MIN_OUTLETS_PER_EVENT） | 该 event 不纳入聚合 |
| bank-year 无任何 event | 4 列均为 NaN |

### 33.5 依赖与 D-0 实测项

依赖：`pip install krippendorff>=0.5.0`（[requirements.txt:107](../requirements.txt) 默认注释化）。

D-0 实测项（v2.3 G-D3.1）：valid `(bank, event)` 三元组覆盖 ≥ 60% bank-year。

---

## 34. AG LLM CEO NER (v3.7.0 D4)

**整体说明**：[`executive_ner.py`](../pipeline/sentiment/executive_ner.py)（330 行）。zero-shot LLM 抽取银行高管提及（CEO / 董事长 / 总裁 / 行长 / 副行长 / 副总裁 / 首席执行官 / 首席风险官 / 首席信息官）。

锚定：
- Kaustia & Rantapuska (2016, JFM 29) CEO 媒体提及 × CEO 个人声誉与股价
- Bushee, Gow & Taylor (2018, JAR 56(1), 85-121) NER 抽 firm-level vs CEO-level disclosure
- Malmendier & Tate (2009, QJE 124(4), 1593-1638) Superstar CEOs

### 34.1 LLM Prompt 模板（[executive_ner.py:85-99](../pipeline/sentiment/executive_ner.py#L85-L99)）

```
请从以下中文银行/金融科技新闻文章中识别提到的银行高管姓名。
关注职位: CEO / 董事长 / 总裁 / 行长 / 副行长 / 副总裁 / 首席执行官 / 首席风险官 / 首席信息官。
仅返回 JSON 数组, 格式如下: [{"name": "姓名", "title": "职位", "mention_count": 提及次数}, ...]
若无任何高管提及, 返回空数组 [].
```

### 34.2 LLM client + 缓存 + DC3 archive

- 复用 stage 21 LLM client（yunwu API）+ `LLMCache`
- **DC3 LLM archive 接入**：每次 LLM 调用通过 `archive_record(...)` 写入 append-only JSONL + SHA-256 manifest（[executive_ner.py:76-82](../pipeline/sentiment/executive_ner.py#L76-L82)）——满足顶刊 reproducibility 硬约束（即使 GPT-5.4→5.5 升级仍可复现）
- 双轨：`content_full` + `content_ctx` 各跑一次

成本估算：~$6–12 yunwu API（400k × 0.3K tokens × $0.5/1M，100% miss 估算）；$15 预算上限（v2.3 G-D4.1 准入门控）。

### 34.3 bank-year 输出 6 列（stage 19 → `19_executive_ner_panel.parquet`）

| 变量 | 公式 | 含义 |
|---|---|---|
| `n_ceo_mentions_full` | bank-year 内所有 mention_count 求和（_full 轨） | 高管被提及总次数 |
| `n_ceo_mentions_ctx` | 同上 ctx 轨 | ctx 高管提及总次数 |
| `n_unique_execs_full` | bank-year 内 distinct(name) 数 | 去重高管数 |
| `n_unique_execs_ctx` | 同上 ctx | ctx 去重高管数 |
| `exec_hhi_full` | `Σ (n_mentions_exec_i / n_total_mentions)²` | mention 在 executives 上的 HHI（**聚焦度**） |
| `exec_hhi_ctx` | 同上 ctx | ctx 聚焦度 |

### 34.4 当前**未**实现的扩展（如需可手工后处理）

| 变量 | 备注 |
|---|---|
| `ceo_volatility` | CEO 提及在年内的方差 — 未实现 |
| `ceo_succession_event` | CEO 更替事件 dummy — 未实现 |
| `exec_replacement_rate` | 年度高管替换率 — 未实现 |

### 34.5 准入门控（D-0 实测项）

200 篇人工 gold standard 标注 → precision ≥ 0.85，recall ≥ 0.75。

---

## 34bis benefit_society Sibling 模块（audit-only，**不进主 panel**）

**整体说明**：v2.0 J-L-M 2026 robustness alignment plan 引入 3 个 sibling 模块——`benefit_society_alt_anchor` / `_placebo` / `_audit_combined`——它们**完全独立**于主 DAG，由 thin shim [`27c_placebo_and_alt_anchor.py`](../27c_placebo_and_alt_anchor.py) 触发：

```
27c_placebo_and_alt_anchor.py
  └─ benefit_society_audit_combined.main()
       ├─ benefit_society_alt_anchor.main()   # J-L-M Appendix A 5 对替代锚点族
       └─ benefit_society_placebo.main()       # 4 业务线 + 1 neutral filtering placebo
```

### 关键约束
- **不修改** 主 panel `40_panel_yearly.parquet` / `46_*.dta` 三件套 / golden snapshot
- **独立输出** `data/processed/27c_alt_anchor_and_placebo_panel.parquet`（独立 bank-year 长面板）
- **未注册**到 `core/dag.py::STAGES_MAIN / STAGES_VALIDATION` 或 `core/schemas.py::OUTPUT_REGISTRY`——orchestrator 永远不会触发；用户**显式手动**运行 `python news_process/27c_placebo_and_alt_anchor.py`
- 下游消费方：[`papers/benefit_society/analysis.py --stage robustness_stage_a`](../papers/benefit_society/analysis.py) → Stata 模板 P2.S1（替代锚点）+ P2.A2（业务线 placebo）

### 27c_alt_anchor_and_placebo_panel.parquet 列（独立 panel，不进 catalog 三件套）

| 系列 | 列模板 |
|---|---|
| 替代锚点投影（5 对） | `benefit_alt_anchor_{anchor_id}_mean_{full,ctx}` / `_std_{full,ctx}` / `_pos_frac_{full,ctx}` / `_neg_frac_{full,ctx}` —— 共 5 × 4 stat × 2 track = **40 列** |
| 业务线 placebo（4 + 1） | `benefit_placebo_{housing_loans, credit_cards, deposits, wealth_mgmt, neutral}_mean_{full,ctx}` 等 stat × track —— 共 5 × 4 stat × 2 track = **40 列** |
| Audit 元数据 | `audit_anchor_family` / `audit_sample_id` / `audit_run_ts` 等（具体由 `audit_combined.py` 决定） |

### Stata 端用法
```stata
* 替代锚点稳健性
use 27c_alt_anchor_and_placebo_panel.dta, clear
foreach a in family_a family_b family_c family_d family_e {
    reghdfe Y benefit_alt_anchor_`a'_mean_ctx X, absorb(target_bank year)
}

* 业务线 placebo
foreach b in housing_loans credit_cards deposits wealth_mgmt neutral {
    reghdfe benefit_placebo_`b'_mean_ctx X, absorb(target_bank year)
}
```

---

## 35. AH benefit_society 经营效益态度（Jha-Liu-Manela 2026 RFS）

**整体说明**：**第 7 篇 paper 主指标**。Jha, Liu & Manela (2026, RFS §1.3.2 Eq.1) 双极锚点投影。10 对正/负极锚点句构成"利好经营 vs 损害经营"语义轴，每篇新闻余弦投影到轴上。详见 [benefit_society.py:44-49](../pipeline/features/benefit_society.py#L44-L49)。

锚定：
- Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? *RFS*, 39(5), 1227–1266. DOI: 10.1093/rfs/hhaf012
- Kozlowski, Taddy & Evans (2019, ASR) Geometry of Culture
- Reimers & Gurevych (2019, EMNLP) Sentence-BERT（降级方案）

| 变量 | 范围 | 含义 |
|---|---|---|
| `benefit_mean_full` / `_ctx` | [−1, 1] | bank-year 态度均值 |
| `benefit_std_full` / `_ctx` | [0, 1] | bank-year 态度离散度 |
| `benefit_pos_frac_full` / `_ctx` | [0, 1] | 正态度（>0）篇章占比 |
| `benefit_neg_frac_full` / `_ctx` | [0, 1] | 负态度（<0）篇章占比 |

### 35.1 内在含义解读（**第 7 篇 paper 主指标**）

**度量什么**：Jha, Liu & Manela (2026 RFS) 的"**finance benefit society** 双极投影"。它**不**是一般情感（positive/negative），而是专门针对**银行 fintech 是否改善经营效率**这一**特定语义维度**的连续 score。

**与一般 sentiment 的区别**：
- `llm_vote_tone_ctx` 度量"该文章对银行的整体态度好坏"（通用情感）；
- `benefit_mean_ctx` 度量"该文章把 fintech 描述为对银行经营有利还是有害"（**特定方向**）；
- 一篇可以 sentiment 正面（语气温和）但 benefit_mean 负面（讲 fintech 削弱了银行）—— 两者**正交但互补**。

**双极锚点方法的几何直觉**：
1. 准备 10 对正/负极锚点句子（如"金融科技提升经营效率" vs "金融科技降低经营效率"）；
2. 把锚点向量化 → 求差得到"利好经营"方向轴 `p = mean(pos) − mean(neg)`；
3. 每篇新闻向量化后**投影**到该轴上（`cos(s_j, p)` ∈ [-1, 1]）；
4. 这就实现了 Kozlowski-Taddy-Evans (2019 ASR) 的 "**geometry of culture**" —— 把语义维度变成可度量的几何方向。

**4 列的关系**：
| 列 | 信号 | 论文用法 |
|---|---|---|
| `benefit_mean_ctx` | 投影均值，**main treatment** | 主回归因变量或 X |
| `benefit_std_ctx` | 投影离散度 | 信号方差，用于 Garcia-Schmidt-Levine (2025) volatility 分析 |
| `benefit_pos_frac_ctx` | 利好文章占比（discretized） | 二值化稳健性 |
| `benefit_neg_frac_ctx` | 不利文章占比 | 反向验证 |

**v6/F3 NaN 保留约定**：早期版本对无 fintech 新闻 bank-year `fillna(0)` → TWFE 出现伪零质心；现统一**保留 NaN**，Stata 端 listwise drop（详见 §57 BD）。

**典型 Stata spec（P7 main）**：
```stata
* Main: benefit 态度对 ROA / NPL 影响
reghdfe roa benefit_mean_ctx controls, absorb(target_bank year) cluster(bank_province)
reghdfe npl_ratio benefit_mean_ctx controls, absorb(target_bank year)

* 离散度作为不确定性 channel
reghdfe loan_growth c.benefit_mean_ctx##c.benefit_std_ctx controls, absorb(target_bank year)

* 稳健性: 27c 替代锚点族（§34bis）
use 27c_alt_anchor_and_placebo_panel.dta, clear
reghdfe roa benefit_alt_anchor_family_a_mean_ctx controls, absorb(target_bank year)
```

**陷阱**：
- ⚠ **锚点设计敏感**：Jha-Liu-Manela 原文 10 对锚点是经过专家校验的；项目复现时若改锚点 → 投影方向变 → 系数符号可能反转。这就是 27c sibling 模块（§34bis）做 5 替代锚点族的原因；
- ⚠ **SBERT 模型选择**：当前用 stage 30a 的 shibing624 SBERT；切换为其他 SBERT 会改变所有 benefit_* 数值（投影轴不同）→ 复现包必须冻结 SBERT model hash；
- ⚠ **与 substantiveness 区别**：`benefit_mean_ctx > 0` ≠ `innovation_substantiveness = 实质性`——前者讲"对经营有利"，后者讲"真做 vs 装做"。两者可任意组合（如"PR 公告说 fintech 提升效率"= symbolic + benefit positive）。

---

## 36. AI 政策对齐 + Token/Hidden 四象限

**整体说明**：基于 stage 15 输出的 `policy_cosine_sim` + stage 14 输出的关键词维度，按"词频 × 相似度"分四象限。runner.py:1045-1198。

锚定：
- Distel, Grimpe & Poetz (2026, Research Policy) S3.2.1 Token vs Hidden decoupling
- Westphal & Zajac (2001, ASQ) Decoupling policy from practice
- Royston, Altman & Sauerbrei (2006, Stat Med) 连续变量优于离散化

四象限定义：
- **Substantive**：词频 ≥ 分位数 AND 相似度 ≥ 分位数（言行一致）
- **Token**：词频 ≥ 分位数 AND 相似度 < 分位数（"洗科技"）
- **Hidden**：词频 < 分位数 AND 相似度 ≥ 分位数（"闷声干大事"）
- **Irrelevant**：词频 < 分位数 AND 相似度 < 分位数（不相关）

### 36.1 连续聚合（主回归）
| 变量 | 公式 |
|---|---|
| `article_sim_mean` | `mean(policy_cosine_sim)` per (bank, year) |
| `article_sim_std` | `std(policy_cosine_sim)`，单篇 → 0 |
| `fintech_intensity_mean` | `mean(fintech_intensity_score)` |

### 36.2 四象限占比（双轨 × 3 分位数 = 6 组）

双轨：
- Track A (kw)：`fintech_distinct_keywords`
- Track B (int)：`fintech_intensity_score`

分位数：`P ∈ {25, 50, 75}`（P50 = 中位数基准，P25/P75 = 稳健性）。

每 (track, pct) 派生 3 列 = 6 × 3 = **18 列**：

| 变量模板 | 公式 |
|---|---|
| `token_adopt_{kw,int}_p{25,50,75}` | `mean(_is_token_{track}_p{pct})` |
| `hidden_adopt_{kw,int}_p{25,50,75}` | `mean(_is_hidden_{track}_p{pct})` |
| `subst_adopt_{kw,int}_p{25,50,75}` | `mean(_is_subst_{track}_p{pct})` |

---

## 37. AJ Bartik IV（6 类 × 三轨 + 基期敏感性 + share + Rotemberg）

**整体说明**：shift-share Bartik IV，识别外生 fintech 暴露冲击。v6/F4 修复：从原 29 套 IV 修剪到 **6 类核心**，避免 multiple testing inflation。基期 `T0 = max(panel.year.min(), 2010)` 强制 < 2019（DCEP 沙盒前）。

锚定：
- Goldsmith-Pinkham, Sorkin & Swift (2020, AER §2) Bartik IV 外生性公理
- Borusyak, Hull & Jaravel (2022, RES §4.2) shift-share 解释
- Romano & Wolf (2005) step-down p 值校正（IV ≥ 6 时强制）
- Rotemberg (1983) 权重分解

每套 Bartik IV 同时产出**三种**列：(1) IV 本身（`bartik_{group}_iv_{track}`）；(2) 基期 share 列（`bartik_{group}_share_{value}`）—— 用于 Rotemberg 权重诊断；(3) 三轨 `_full / _ctx / _title`。

### 37.1 主 Bartik：银行类型（type, 5 group）

银行类型 groups（除 'other' 兜底外作为 share）：`soe / joint / city / rural / policy`。

| 变量 | 含义 |
|---|---|
| `bartik_type_iv_{full,ctx,title}` | 银行类型 shift-share IV（main） |
| `bartik_type_share_{soe,joint,city,rural,policy}` | 各类型基期份额（5 share 列，用作 Rotemberg α_k 诊断） |
| `bartik_type_iv_full_t0` / `bartik_type_iv_ctx_t0` | 基期敏感性 T0 |
| `bartik_type_iv_full_t1` / `bartik_type_iv_ctx_t1` | 基期敏感性 T0+1 |
| `bartik_type_iv_full_t01` / `bartik_type_iv_ctx_t01` | 基期敏感性 T0 ∪ T0+1 |

### 37.2 稳健性 1：银行规模（scale, 4 group）

scale groups：`L / M / S / XS`（'other' 兜底）。

| 变量 | 含义 |
|---|---|
| `bartik_scale_iv_{full,ctx,title}` | scale shift-share IV |
| `bartik_scale_share_{L,M,S,XS}` | 4 个规模基期份额 |

### 37.3 稳健性 2：金融科技类型（fintech_lf / fintech_lc，2 group，双套独立）

基于 innovation_locus_{full,ctx} 各做一套：

| 变量 | 含义 |
|---|---|
| `bartik_fintech_lf_iv_{full,ctx,title}` | share = innovation_locus_full 基期占比 |
| `bartik_fintech_lf_share_{tech,app}` | 2 share（_full 轨标签派生） |
| `bartik_fintech_lc_iv_{full,ctx,title}` | share = innovation_locus_ctx 基期占比（Hassan 2019 entity-proximity） |
| `bartik_fintech_lc_share_{tech,app}` | 2 share（_ctx 轨标签派生） |

### 37.4 稳健性 3：媒体三方分类（media, 3 group）

groups：`fin / comp / other`（'other' 通常排除）。

| 变量 | 含义 |
|---|---|
| `bartik_media_iv_{full,ctx,title}` | 媒体类型 shift-share（Snyder & Strömberg 2010 JPE） |
| `bartik_media_share_{fin,comp,other}` | 3 share |

### 37.5 稳健性 4：媒体权威性档位（mauth, 3 group）

groups：`high (≥80) / mid (≥60) / low`。

| 变量 | 含义 |
|---|---|
| `bartik_mauth_iv_{full,ctx,title}` | 媒体权威性档位 shift-share（Holzman 2023） |
| `bartik_mauth_share_{high,mid,low}` | 3 share |

### 37.6 稳健性 5：地理邻近性（geoprox, 2 group）

groups：`local / nonlocal`。

| 变量 | 含义 |
|---|---|
| `bartik_geoprox_iv_{full,ctx,title}` | 地理邻近性 shift-share（Engelberg & Parsons 2011 JF） |
| `bartik_geoprox_share_{local,nonlocal}` | 2 share |

### 37.7 经济圈 Leave-One-Out IV

| 变量 | 公式 |
|---|---|
| `zone_leave1out_tone_{full,ctx,title}` | 同经济圈其他银行（去自身）平均情感，`min_group_size ≥ 3` 否则 NaN |

注：旧名 `province_news_sentiment_loo_*` / `city_news_sentiment_loo_*` 不再产出——已统一到 `zone_leave1out_tone_*`，省/市级 LOO 由 [geography.py::compute_leave_one_out_sentiment](../pipeline/panel/geography.py) 派生（见 §47）。

### 37.8 Bartik IV 诊断（不进 panel 列，仅日志/json）

| 诊断 | 来源 | 用途 |
|---|---|---|
| Rotemberg α_k（每 share 权重） | `iv_did.diagnose_rotemberg_weights()` | Goldsmith-Pinkham 2020 §5.2 负权重检验 |
| HHI(\|α\|) | 同上 | < 0.25 = 分散；≥ 0.25 = 少数 share 主导 |
| Top-5 权重 share | 同上 | 论文 robustness 表 |

Stata 端复用 `ssc install bartik_weight` 配合 share 列做正式 Rotemberg 分解。

### 37.9 内在含义解读（**因果识别工具**）

**为什么需要 Bartik IV**：媒体 tone 与银行 outcome 之间存在**反向因果**——业绩好的银行获得更多正面报道（reverse causality）。Bartik shift-share IV 用"行业层面冲击 × 银行基期特征"构造**外生** instrument，识别 tone → outcome 的单向因果。

**Goldsmith-Pinkham-Sorkin-Swift (2020 AER) 的外生性公理**：
- `share` 必须在 **pre-treatment 期固定**且**独立于 outcome**；
- 这就是项目把 share 限定为 `bank_type / bank_scale`（pre-treatment 银行属性）+ `media / mauth / geoprox`（pre-treatment 媒体属性）的原因；
- v6/F4 删除的 28 类 IV 是因为它们的 share 是**post-treatment 编辑决策**（文档长度 / 标题选择 / 媒体分类）→ 违反公理 → identification fail；

**为什么基期 T0 = max(panel.year.min(), 2010)**：
- 2010 = 中国 fintech 萌芽前；
- DCEP 数字人民币里程碑 = 2019 → 强制 `T0 < 2019` 防止 share 已在 post-treatment 区间。

**Romano-Wolf 校正的统计含义**：
- 当 IV ≥ 6 套时，naive 单一 IV 的 p 值会因多重检验通胀；
- Romano-Wolf step-down 校正后的 p 值才是"真正显著"——论文 main table 必须报告校正后；
- Stata 实现：`rwolf` 包（`ssc install rwolf`）。

**Rotemberg 权重诊断的解读**：
- α_k > 0 大且集中 → 几个 share 维度主导 IV → 论文需在 robustness 表展示"剔除大权重维度后 IV 仍 work"；
- α_k < 0 → **misspecification 警告**（Goldsmith-Pinkham 2020 §5.2）→ 该 share 维度违反正交性 → 论文必须删除该维度或解释；
- HHI(|α|) < 0.25 → 分散 → IV 健康；
- HHI(|α|) ≥ 0.25 → 集中 → Borusyak-Hull-Jaravel (2022 RES) shift-share 解释下需慎用。

**典型 Stata spec（P2 attention IV）**：
```stata
* First stage
reghdfe ft_attn_yr bartik_type_iv_full controls, absorb(target_bank year)

* Second stage with Romano-Wolf
ivreghdfe Y (ft_attn_yr = bartik_type_iv_full bartik_scale_iv_full bartik_fintech_lf_iv_full ///
    bartik_media_iv_full bartik_mauth_iv_full bartik_geoprox_iv_full) controls, ///
    absorb(target_bank year) cluster(bank_province)
* 报 Kleibergen-Paap rk LM + Sanderson-Windmeijer F + Hansen J

* Romano-Wolf 校正 (6 IV)
rwolf ivreghdfe Y (ft_attn_yr = $iv_set) controls, ///
    indepvars(ft_attn_yr) reps(1000) seed(42)

* Rotemberg 分解
ssc install bartik_weight
bartik_weight Y bartik_type_iv_full bartik_type_share_*, absorb(target_bank year)
```

**陷阱**：
- ⚠ **share 列不要进入 second stage**：share 是 IV 的成分，与 LHS 直接关联会破坏排除性约束；
- ⚠ **基期敏感性必报**：`_t0 / _t1 / _t01` 三套对比展示 IV 不敏感于基期选择——若 t0/t1 差异 > 10% → IV 不稳；
- ⚠ **`_full` IV 配 `_full` outcome**：双轨 _full/_ctx 一致性原则同样适用 IV，不要交叉。

---

## 38. AK 政策冲击 DID（DCEP + Sandbox）

**整体说明**：[`merge_policy_shocks()`](../pipeline/panel/iv_did.py#L480) 读 `config/policy_shocks.json`，把每个政策（`prefix`）作为 staggered DID treatment。对每个政策（dcep / sandbox / ...）派生 **完整 12+ 列** 的 event-study 工具集，覆盖 Callaway & Sant'Anna (2021, JOE) 推荐的所有变量。

匹配优先级（先入为主）：(a) cities 精确匹配 → (b) full_province 整省匹配 → (c) new_cities 零散补充。城市名别名映射在 [iv_did.py:512](../pipeline/panel/iv_did.py#L512)（如雄安 → 保定）。

### 38.1 单个政策（`{prefix}` ∈ `{dcep, sandbox, ...}`）产出的完整列集

| 变量 | 公式 | 含义 |
|---|---|---|
| `{prefix}_treat_year` | int，0 = 控制组；>0 = 首次处理年份 | csdid 的 gvar，event-study gating |
| `{prefix}_treated` | `(treat_year > 0).astype(int)` | 处理组哑变量 |
| `{prefix}_post` | `(year ≥ treat_year).astype(int)` | 政策后哑变量 |
| `{prefix}_rel_year` | `year − treat_year`（控制组 NaN） | event-time 相对年（Callaway & Sant'Anna 2021） |
| `{prefix}_lead3` / `{prefix}_lead2` | `(rel_year == -k).astype(int)` | k ∈ {-3, -2}，pre-treatment 哑变量；k=-1 **omit 为基期** |
| `{prefix}_lag0` / `{prefix}_lag1` / `{prefix}_lag2` / `{prefix}_lag3` | 同上，k ∈ {0, 1, 2, 3} | post-treatment 哑变量 |
| `{prefix}_lead4plus` | `(rel_year ≤ -4 且 treated).astype(int)` | endpoint binning（pre） |
| `{prefix}_lag4plus` | `(rel_year ≥ 4 且 treated).astype(int)` | endpoint binning（post） |

合计 **每个政策 12 列**（不计 base 基期 k=-1）。

### 38.2 多政策正交性诊断（runner 日志，不进 panel）

`merge_policy_shocks()` 末尾自动跑 Cramér's V 交叉表（[iv_did.py:629-666](../pipeline/panel/iv_did.py#L629-L666)）：
- V < 0.3 → 弱相关 ✓（可同时纳入回归）
- V ≥ 0.3 → 中强相关（论文需讨论处理组重叠 + 分别估计）

### 38.3 非 DID 时间断点哑变量

| 变量 | 公式 | 含义 |
|---|---|---|
| `depins_post` | `(year ≥ 2015).astype(int)` | 存款保险条例全国统一实施（runner.py:952，**非 DID**：全国无控制组） |
| `stress_period` | `year ∈ {2015, 2018, 2020}` | 银行业压力期哑变量（runner.py:935，股灾/去杠杆/疫情） |

### 38.4 Stata 端典型用法

```stata
* csdid 交错 DID
csdid Y X, ivar(target_bank) time(year) gvar(dcep_treat_year)
estat event           // event-study plot
estat pretrend        // 平行趋势检验

* 手动 event-study (reghdfe)
reghdfe Y dcep_lead3 dcep_lead2 dcep_lag0 dcep_lag1 dcep_lag2 dcep_lag3 ///
    dcep_lead4plus dcep_lag4plus controls, absorb(target_bank year) cluster(bank_province)
```

### 38.5 内在含义解读（**因果识别 staggered DID**）

**为什么需要 staggered DID 而非传统 DID**：
- DCEP 数字人民币试点 2020-2024 分 4 批（深圳/苏州/北京等），不同银行省份在**不同时间**获得 treatment；
- 传统 DID（pre-post × treated-control）会用"晚期 treated"作为"早期 treated"的 control → bias（Goodman-Bacon 2021 JOE）；
- staggered DID + Callaway-Sant'Anna (2021 JOE) ATT(g, t) → 正确估计。

**为什么用 lead/lag dummy 而非线性 rel_year**：
- 线性 `rel_year` 假设效应随时间线性变化，**约束过强**；
- 6 个 lead/lag dummy 让效应"自由变化"，event study plot 可视化平行趋势 + 动态效应；
- `lead4plus / lag4plus` endpoint binning 防止极端 event-time 样本太少导致系数波动。

**关键平行趋势检验**：
- `lead2 / lead3 / lead4plus` 系数应**不显著** → 平行趋势成立；
- `lag0` 系数 = 政策当年效应；`lag1` = 一年后效应；
- 若 `lead3` 显著 → pre-trend 存在 → DID 估计有偏。

**`{prefix}_treated × controls` 异质性扩展**：
- `dcep_treated × is_soe` → 国有银行在 DCEP 下是否被赋予不同角色（国有大行通常是试点主力）；
- `dcep_post × digital_frontier` = §39.AL §39.2 的 DDD `dcep_ddd_digfront`。

**典型 Stata spec**：
```stata
* csdid main spec
csdid Y X, ivar(target_bank) time(year) gvar(dcep_treat_year)
estat event, window(-3 3) endpoints

* 手动 event-study + endpoint binning
reghdfe Y dcep_lead3 dcep_lead2 dcep_lag0 dcep_lag1 dcep_lag2 dcep_lag3 ///
    dcep_lead4plus dcep_lag4plus controls, ///
    absorb(target_bank year) cluster(bank_province)
test dcep_lead3 dcep_lead2          // 联合 pre-trend 检验

* DDD: DCEP × 数字前沿（runner.py:913-926 预算）
reghdfe Y dcep_ddd_digfront dcep_treated dcep_post digital_frontier ///
    dcep_treated#dcep_post dcep_treated#digital_frontier dcep_post#digital_frontier ///
    controls, absorb(target_bank year)

* 平行趋势 placebo (§55 BB)
reghdfe Y dcep_placebo2_did controls, absorb(target_bank year) cluster(bank_province)
* dcep_placebo2_did 应不显著
```

**陷阱**：
- ⚠ **`depins_post` 是非 DID**：全国 2015 统一实施，无控制组 → 只能做时间断点回归 → 不要用 `csdid`；
- ⚠ **多政策重叠**：Cramér's V ≥ 0.3 时（runner 自动诊断），dcep 和 sandbox 处理组高度重叠 → 论文必须分别估计或讨论；
- ⚠ **k=-1 是 omitted baseline**：lead/lag dummy 在 reghdfe 中**不要重新加入** `dcep_lead1`（不存在，因为 k=-1 是基期）。

---

## 39. AL 异质性交互项（SOE / Scale / HighCov / Stress / DDD）

**整体说明**：runner.py:836-961 集中预计算 7 类交互项，避免每次 Stata 跑回归都重算。锚定 Angrist & Pischke (2009) §3.4.2 + Brambor, Clark & Golder (2006, PA)。

### 39.1 Tone × bank-property 交互（双轨）

| 变量 | 公式 | 解释 |
|---|---|---|
| `tone_x_soe_{full,ctx}` | `llm_vote_tone × is_soe` | 国有银行的情感效应放大 |
| `tone_x_scale_{full,ctx}` | `llm_vote_tone × bank_scale_ord` | 规模异质性 |
| `tone_x_highcov_{full,ctx}` | `llm_vote_tone × high_coverage` | 高曝光银行边际效应 |
| `tone_x_stress_{full,ctx}` | `llm_vote_tone × stress_period` | 压力期非对称效应（Garcia 2013 JF） |
| `tone_x_depins_{full,ctx}` | `llm_vote_tone × depins_post` | 存保实施后的情感传导变化 |

### 39.2 DDD 三重差分（runner.py:913-926）
| 变量 | 公式 | 解释 |
|---|---|---|
| `dcep_ddd_digfront` | `dcep_treated × dcep_post × digital_frontier` | DCEP × 数字前沿三重差分 |
| `sandbox_ddd_digfront` | 同上 sandbox | Sandbox × 数字前沿 |

---

## 40. AM 滞后 / 反转 / Concern Score

### 40.1 滞后 / 反转（De Bondt & Thaler 1985 JF）
| 变量 | 公式 |
|---|---|
| `llm_vote_tone_full_lag1` / `llm_vote_tone_ctx_lag1` | `panel.groupby('target_bank')[tone].shift(1)` |
| `tone_reversal_{full,ctx}` | `llm_vote_tone − llm_vote_tone_lag1` |

### 40.2 复合关注度（runner.py:969-980）
| 变量 | 公式 | 范围 |
|---|---|---|
| `concern_score_{full,ctx}` | `ln_news_coverage × (senti_ratio + 1) / 2`，其中 `senti_ratio = (neg − pos) / (neg + pos)` | [0, +∞) ∪ NaN |

含义：高 concern_score = 负面新闻多 + 报道量大；全中性篇章 → NaN（语义合理：无方向性 → 关注度方向未定义）。

---

## 41. AN J-F 系数

**整体说明**：Janis & Fadner (1965); Deephouse (2000 SMJ) — 克服简单均值的零分悖论。

公式：
```
若 P > N: JF = (P² − P·N) / (P+N)²
若 N > P: JF = (P·N − N²) / (P+N)²
若 P = N: JF = 0
```

| 变量 | 范围 |
|---|---|
| `jf_coefficient_full` | [−1, +1] |
| `jf_coefficient_ctx` | [−1, +1] |
| `jf_coefficient_title` | [−1, +1] |

---

## 42. AO disag 情感分歧

**整体说明**：情感意见分歧指数。公式 `disag = sqrt(1 − ((pos − neg)/(pos + neg))²) ∈ [0, 1]`。0 = 完全一致；1 = 最大分歧。

锚定：姜富伟, 李梦如, 孟令超 (2024). 经济学（季刊）, 24(6), 2281-2300; Antweiler & Frank (2004, JF) JF 59(3), 1259-1294。

### 42.1 综合 disag（每轨）
| 变量 | 输入 |
|---|---|
| `disag_{full,ctx}` | 词典综合 `avg_pos_ratio` / `avg_neg_ratio`（词级比率） |
| `disag_llm_{full,ctx}` | LLM 投票 `pos_count` / `neg_count`（篇章计数） |
| `disag_bert_{full,ctx}` | BERT 综合 `bert_avg_pos` / `bert_avg_neg`（概率均值） |

### 42.2 单方法 disag（每轨）
| 变量模板 | 输入 |
|---|---|
| `disag_{dict}_{full,ctx}` (5 × 2 = 10) | 单词典 `avg_{dict}_pos_ratio` / `avg_{dict}_neg_ratio` |
| `disag_{llm}_{full,ctx}` (3 × 2 = 6) | 单 LLM `{llm}_pos_count` / `{llm}_neg_count` |
| `disag_{bert}_{full,ctx}` (5 × 2 = 10) | 单 BERT `{bert}_pos` / `{bert}_neg` |

**合计 32 个 disag 变量**（runner.py:1463 日志确认）。

---

## 43. AP log_sent 对数降噪情感

**整体说明**：Angelico et al. (2022, J Econometrics) 对数变换降噪。

| 变量 | 公式 |
|---|---|
| `log_sent_{full,ctx}` | `log(1 + pos_count) − log(1 + neg_count)` |

---

## 44. AQ algo_cater 算法迎合度

**整体说明**：检测词典法是否比 LLM/BERT 更倾向给出正面评分（潜在算法迎合）。锚定 Cao, Jiang, Yang & Zhang (2023, RFS) "How to talk when a machine is listening"; Huang, Wang & Yang (2023, CAR) FinBERT。

公式：`algo_cater = dict_tone − deep_model_tone`，正值 → 词典更正面（迎合）。

### 44.1 综合 vs 综合
| 变量 | 公式 |
|---|---|
| `algo_cater_{full,ctx}` | `dict_avg_tone − llm_vote_tone` |
| `algo_cater_b_{full,ctx}` | `dict_avg_tone − (bert_avg_pos − bert_avg_neg)` |

### 44.2 单词典 vs 综合深层
| `{dict}_cater_{full,ctx}` (5 × 2 = 10) | `{dict}_tone − llm_vote_tone` |
| `{dict}_cater_b_{full,ctx}` (5 × 2 = 10) | `{dict}_tone − (bert_avg_pos − bert_avg_neg)` |

### 44.3 综合词典 vs 单深层
| `cater_{llm}_{full,ctx}` (3 × 2 = 6) | `dict_avg_tone − {llm}_tone` |
| `cater_{bert}_{full,ctx}` (5 × 2 = 10) | `dict_avg_tone − ({bert}_pos − {bert}_neg)` |

**合计 ~40 个 cater 变量**。

---

## 45. AR Text2Vec 双轨稳健性

**整体说明**：text2vec（shibing624/text2vec-base-chinese）作为主轨嵌入（text-embedding-3-small）的稳健 twin，产出 strategic differentiation + policy alignment 指标，作为 LLM "幻觉偏移"（hallucination bias）的方法学对照。**2026-05-29 双模型重构**后，原独立 stage 30（`30_text2vec_indicators.parquet`）已退役，这些 `_t2v` 列改由 stage 25（strategic_diff，战略差异）与 stage 15（policy_alignment，经 runner.py 聚合，政策对齐）在主流程内联双模型产出；缺列由 `export.py::REQUIRED_PANEL_COLUMNS` fail-loud 守卫（export.py:216-232）。

| 变量 | 来源 | 含义 |
|---|---|---|
| `strat_diff_t2v_full` / `strat_diff_t2v_ctx` | stage 25（内联） | text2vec 战略差异度（vs LLM 版） |
| `policy_cosine_sim_t2v_full` / `policy_cosine_sim_t2v_ctx` | stage 15（内联，runner 聚合） | text2vec 政策对齐（vs LLM 版） |

**保留 NaN**（无新闻 bank-year）—— 修 v6/F3 fillna(0) 反模式。

---

## 46. AS 媒体异质性、平衡媒体稳健性、停刊检测

**整体说明**：[`compute_media_heterogeneity()`](../pipeline/panel/attention_media.py) 三大子模块：

(i) 媒体异质性 tone_gap 8 维度 × 3 轨；
(ii) `detect_defacto_cessation()` 数据驱动 + NPPA 交叉验证的隐性停刊检测（Heese et al. 2022 JFE; Gao et al. 2020 JFE）；
(iii) `compute_balanced_media_robustness()` 3 个时间窗口的平衡媒体面板稳健性（Wooldridge 2010 §19.9.3 attrition）。

### 46.1 8 维度 tone_gap × 3 轨 = 24 列

| 变量模板 | 公式（runner.py / attention_media.py 行号） | 含义 |
|---|---|---|
| `tone_gap_fin_other_{full,ctx,title}` | [attention_media.py:585](../pipeline/panel/attention_media.py#L585) | 财经媒体 − 其他媒体 |
| `tone_gap_comp_other_{full,ctx,title}` | [attention_media.py:588](../pipeline/panel/attention_media.py#L588) | 综合媒体 − 其他媒体 |
| `tone_gap_fin_comp_{full,ctx,title}` | [attention_media.py:591](../pipeline/panel/attention_media.py#L591) | 财经 − 综合 |
| `tone_gap_central_local_{full,ctx,title}` | [attention_media.py:616](../pipeline/panel/attention_media.py#L616) | 央媒 − 地方媒体 |
| `tone_gap_official_nonoff_{full,ctx,title}` | [attention_media.py:645](../pipeline/panel/attention_media.py#L645) | 官方 − 非官方 |
| `tone_gap_market_nonmkt_{full,ctx,title}` | [attention_media.py:674](../pipeline/panel/attention_media.py#L674) | 市场化 − 非市场化 |
| `tone_gap_deepdive_nondeep_{full,ctx,title}` | [attention_media.py:703](../pipeline/panel/attention_media.py#L703) | 深度报道 − 非深度 |
| `tone_gap_daily_nondaily_{full,ctx,title}` | [attention_media.py:732](../pipeline/panel/attention_media.py#L732) | 日报 − 非日报 |

### 46.2 地理维度 tone_gap（媒体地理偏袒度）

[attention_media.py:865](../pipeline/panel/attention_media.py#L865) 还派生**地理维度** 4 组 `tone_gap_{home_sfx}_{away_sfx}{track}`：
- `tone_gap_homeprov_otherprov_{full,ctx,title}` — 本省媒体 vs 外省媒体情感差
- `tone_gap_homecity_othercity_{full,ctx,title}` — 本市媒体 vs 外市媒体情感差

合计：8 媒体属性 + 2 地理属性 = 10 gap × 3 轨 = **30 列**。

### 46.3 停刊检测（cessation detection）

**学术**：Heese, Pérez-Cavazos & Peter (2022, JFE 145(2B)) 报纸停刊导致地方公司监督真空 + 违规增加；Gao, Lee & Murphy (2020, JFE 135(2)) 媒体退出的公共财政成本。

| 变量 | 含义 |
|---|---|
| `_is_ceased_media` | 篇章级：媒体在停刊名单（confirmed ∪ suspected）的 dummy（attention_media.py:98） |

派生 sample selection bias 检验列：副产物 `42_cessation_report.xlsx` 含 `cessation_status` ∈ {`active`, `confirmed`, `suspected`, `nppa_only`}。

### 46.4 平衡媒体稳健性窗口

3 个时间窗口（attention_media.py:114-118）：
- `w0724` = 2007–2024 全样本
- `w1024` = 2010–2024 排除金融危机恢复期
- `w1124` = 2011–2024 排除四万亿刺激期

每窗口产出（仅"全程在刊"的媒体子集）：

| 变量模板 | 数量 |
|---|---|
| `bal_{w}_tone_{full,ctx,title}` | 3 窗 × 3 轨 = **9 列** |
| `bal_{w}_{score_pattern_full列名}` | 动态发现，逐方法 × 3 窗 ≈ **30+ 列**（受 32 字符列名上限约束，部分缩写） |
| `n_media_bal_{w}` | 3 窗 = **3 列**（该窗内平衡媒体数） |

合计 ≈ **45+ 列** 平衡稳健性变量。

### 46.5 媒体集中度
| 变量 | 含义 |
|---|---|
| `media_hhi` | bank-year 媒体来源 Herfindahl 指数（runner 日志 attention_media.py:959 提及） |

---

## 47. AT 地理与 LOO IV

**整体说明**：[`merge_bank_geography()`](../pipeline/panel/geography.py) 从 `bank_addresses.json` 合并 `bank_province` / `bank_city`（[geography.py:432-433](../pipeline/panel/geography.py#L432-L433)）；下游：`compute_leave_one_out_sentiment` / `compute_geo_proximity_buffers` / `compute_regional_imitation_pressure`。

### 47.1 地理邻近 dummy（篇章级前置）
| 变量 | 含义 |
|---|---|
| `_is_homeprov` | 媒体省份 = 银行省份（含 `np.maximum(_is_homeprov, _is_homecity)` 升级语义） |
| `_is_homecity` | 媒体城市 = 银行城市 |

### 47.2 LOO 情感 IV（Luo & Li 2025 同省/同市）

[`compute_leave_one_out_sentiment()`](../pipeline/panel/geography.py)：对每条轨 `_full / _ctx / _title` 派生：

| 变量模板 | 含义 | 失败时 |
|---|---|---|
| `province_loo_tone_{full,ctx,title}` | 同省其他银行（去自身）平均情感 | n < min_group_size (3) → NaN |
| `city_loo_tone_{full,ctx,title}` | 同城其他银行（去自身）平均情感 | 同上 |
| `zone_leave1out_tone_{full,ctx,title}` | 同经济圈其他银行（去自身）平均情感（compute_zone_leave1out @ iv_did.py:436-472） | 同上 |

### 47.3 4 梯度地理距离缓冲（Gurun & Butler 2012; Engelberg & Parsons 2011）

[`compute_geo_proximity_buffers()`](../pipeline/panel/geography.py) 派生（按距离分桶聚合同 bank-year 内不同距离区间的篇章情感）：

| 变量模板 | 含义 |
|---|---|
| `geo_buf_0_50km_tone_{full,ctx,title}` | 0–50 km 缓冲圈情感均值 |
| `geo_buf_50_200km_tone_{full,ctx,title}` | 50–200 km |
| `geo_buf_200_500km_tone_{full,ctx,title}` | 200–500 km |
| `geo_buf_500plus_km_tone_{full,ctx,title}` | 500+ km |
| `geo_buf_*_n_articles` | 各桶篇数 |

### 47.4 区域模仿渗透率（Leary & Roberts 2014）

[`compute_regional_imitation_pressure()`](../pipeline/panel/geography.py) 六层 LOO 模仿压力：

| 变量模板 | 含义 |
|---|---|
| `imit_press_homeprov` | 本省其他银行 fintech 报道率 |
| `imit_press_homecity` | 本城其他银行 fintech 报道率 |
| `imit_press_homezone` | 本经济圈其他银行 |
| `imit_press_sametype_homeprov` | 同类型 ∩ 同省 |
| `imit_press_sametype_homecity` | 同类型 ∩ 同城 |
| `imit_press_sametype_homezone` | 同类型 ∩ 同经济圈 |

### 47.5 综合标准化变量

[`compute_composite_indicators()`](../pipeline/panel/geography.py) + [`standardize_panel_variables()`](../pipeline/panel/geography.py)：把若干核心指标做**年度截面标准化**（z-score），输出 `_z` 后缀列；具体清单按 config 决定，常见 `tone_z_{full,ctx}` / `attn_z` / `coverage_z` 等。

### 47.6 `_has_fintech` 篇章覆盖哑变量

| 变量 | 公式 |
|---|---|
| `_has_fintech` | `(n_articles > 0).astype(int)`（[geography.py:1017](../pipeline/panel/geography.py#L1017)，与 `has_coverage` 同义） |

---

## 48. AU 网络中心度（18 节点级 + 4 网络级 = 22 指标）+ 网络溢出 + 认知邻近度

**整体说明**：[`compute_bank_network_centrality()`](../pipeline/panel/network_spillover.py#L363) 基于银行共现邻接矩阵（`co_mentioned_banks` 解析）计算 **18 节点级 + 4 网络级** 中心度，共 22 项。原图与倒数图分别承担拓扑型与路径型指标——倒数图 `G_inv` 把"共现强度"反演为"距离"，符合空间计量经济学标准（LeSage & Pace 2009）。

锚定：Freeman (1979)；Bonacich (1972)；Burt (1992) Structural Holes；Estrada (2005)；Newman (2005)；Billio et al. (2012, JFE)；Watts & Strogatz (1998)；Dahlke et al. (2024, RP)。

### 48.1 节点级 18 指标（按原图 / 倒数图分组）

#### (a) 原图组 (12 指标，用于谱型 / 结构型 / 拓扑型)

| 变量 | 含义 | 失败 fallback |
|---|---|---|
| `bank_degree_cent` | Freeman 度中心度 `deg(i)/(n-1)` | — |
| `bank_strength_cent` | 加权度（max-normalize） | — |
| `bank_eigen_cent` | 特征向量中心度（Bonacich 1972） | 三级 fallback：power iter → numpy LCC → NaN |
| `bank_katz_cent` | Katz 中心度，α = 0.9/λ_max | NaN on failure |
| `bank_subgraph_cent` | Estrada 2005 子图中心度（不接受 weight） | 溢出 → NaN |
| `bank_cfbetween_cent` | Current-Flow Betweenness（电导语义），**仅 LCC** | LCC < 2 → NaN |
| `bank_clustering` | Watts-Strogatz 加权聚类系数 | — |
| `bank_constraint` | Burt 1992 structural constraint，degree < 2 → NaN | — |
| `bank_ego_density` | 邻居间边密度，`k ≤ 1` → NaN | — |
| `bank_effective_size` | Burt 1992 effective size，degree=0 → NaN | — |
| `bank_avg_nbr_deg` | 加权平均邻居度，degree=0 → NaN | — |
| `bank_coreness` | k-core 数（拓扑） | — |

#### (b) 倒数图 G_inv 组 (4 指标，用于路径型)

| 变量 | 含义 |
|---|---|
| `bank_between_cent` | 介数中心度（倒数图） |
| `bank_harmonic_cent` | Harmonic 中心度（倒数图，参数 distance） |
| `bank_closeness_cent` | 接近中心度（倒数图） |
| `bank_eccentricity` | 偏心度，**仅 LCC**，LCC < 2 → NaN |

#### (c) 衍生 2 指标

| 变量 | 公式 | 含义 |
|---|---|---|
| `bank_ci` | `1 / bank_constraint`（仅 constraint > 0 有效） | Burt collective influence |
| `bank_is_hub` | 度中心度 Top 10% = 1 | Hub binary |

### 48.2 网络级 4 指标（年度级，广播到所有银行）

| 变量 | 公式 |
|---|---|
| `net_density_yr` | `nx.density(G)` 年度网络密度 |
| `net_avg_cluster_yr` | 加权平均聚类系数 |
| `net_avg_path_yr` | LCC 上倒数图的平均最短路径长度，LCC < 2 → NaN |
| `net_degree_gini_yr` | 度分布 Gini 系数 |

### 48.3 网络溢出（peer_tone）

[`compute_network_spillovers()`](../pipeline/panel/network_spillover.py#L188)：用 Lag(Y-1) 的行随机标准化邻接矩阵 W 加权同行情感，规避 Manski (1993) 反射问题。

锚定：Leary & Roberts (2014, JF)；Manski (1993, RES)；LeSage & Pace (2009)；Berger, Guedhami, Kim & Li (2022, JFI)。

| 变量 | 公式 |
|---|---|
| `peer_tone_lag1_{full,ctx,title}` | `Σ_j W[i,t-1] × tone_j,t-1`（一阶溢出） |
| `peer_tone_2nd_lag1_{full,ctx,title}` | `W² × tone` 二阶溢出（邻居的邻居，LeSage & Pace 2009 分量模型） |
| `peer_fintech_exposure_lag1` | `Σ_j W[i,t-1] × ln_news_coverage_j,t-1`（同行 fintech 声量溢出，Berger et al. 2022 JFI） |

合计：**3 轨 × 2 阶 + 1 = 7 列**。

### 48.4 认知邻近度（cognitive proximity）

[`compute_cognitive_proximity()`](../pipeline/panel/network_spillover.py#L728)：每家银行当年新闻拼接为"超级文档" → TF-IDF (char_wb, ngram(2,4)) → cosine similarity → bank-year 与其他银行的均值。

锚定：Boschma (2005, Regional Studies)；Dahlke, et al. (2024, RP 53:2)。

| 变量 | 含义 |
|---|---|
| `bank_cogn_mean` | 该银行与所有其他银行的 TF-IDF cosine 均值；高值 = 同质化锁定风险 |

### 48.5 加权中心度（未实现 / 弃用提示）

虽然存在 `_w / _mw / _hw` 命名约定，但 `compute_bank_network_centrality` **目前不输出**加权中心度版本（即 `bank_degree_cent_w` 等不存在）。如有需要，可在后处理中自行用 mention_density / media_authority_weight 加权重建邻接矩阵后调用。

---

## 49. AV 信息经纪 + 火灾甩卖

**整体说明**：[`pipeline/panel/network_brokerage.py`](../pipeline/panel/network_brokerage.py)（426 行）。

锚定：Han, Subrahmanyam & Zhou (2024, RFS) 信息经纪；Manski (1993) reflection problem → LOO 解决；Coval & Stafford (2007, JFE) fire sale。

### 49.1 经纪中心度（`compute_brokerage_centrality`）

`brok_df` merge 进 panel（[network_brokerage.py:269](../pipeline/panel/network_brokerage.py#L269)）。具体列名由模块内部 `_compute_brokerage_metrics()` 决定，典型字段：

| 变量 | 含义 |
|---|---|
| `brokerage_central` | 信息经纪中心度（共同邻居数 / 总邻居数）—— 银行作为信息中转节点的强度 |
| `brokerage_betweenness_w` | 加权介数中心度（信息流量） |
| `brokerage_constraint` | Burt 1992 structural hole constraint |
| `brokerage_efficiency` | Burt 1992 effective size（信息桥效率） |

### 49.2 行业负面冲击与火灾甩卖（`compute_industry_neg_shock` + `compute_fire_sale_interaction`）

| 变量 | 公式 | 含义 |
|---|---|---|
| `_neg_ratio` | `neg_count_full / n_articles`（中间列，[network_brokerage.py:334](../pipeline/panel/network_brokerage.py#L334)） | 单银行负面率（panel 上保留以供下游使用） |
| `industry_neg_shock` | 行业去自身后的 _neg_ratio LOO 平均（[network_brokerage.py:353](../pipeline/panel/network_brokerage.py#L353)） | Manski 1993 LOO 反射规避 |
| `_lag1` | `panel.groupby('target_bank')['_neg_ratio'].shift(1)`（[network_brokerage.py:415](../pipeline/panel/network_brokerage.py#L415)） | 滞后自身负面率 |
| `brokerage_fire_sale` | `_lag1 × industry_neg_shock`（[network_brokerage.py:418](../pipeline/panel/network_brokerage.py#L418)） | 火灾甩卖交乘项（前期自身负面 × 当期行业负面冲击） |

---

## 50. AW 战略差异度 (strat_diff) + 文本连贯性 (coh)

**整体说明**：[strategic_diff.py](../pipeline/features/strategic_diff.py)（1498 行，4 方法 × N-NN 多近邻 + Fluidity + 文本连贯性 + Centroid + Ctx 轨）。

锚定：
- Guzman & Li (2023) 自然语言战略差异度
- Hoberg & Phillips (2016, JPE) text-based network industries
- Hoberg, Phillips & Prabhala (2014, JF) product market fluidity
- 谢佳松 (2025, 经济研究) 全行业向量法
- 欧阳志刚 & 胡雯华 (2024, 数量经济技术经济研究) 文本连贯性

### 50.1 N-最近邻差异度（4 方法 × N ∈ {3,4,5,6,7}，仅 Full 轨展开 N，Ctx 仅 N=5）

| 变量模板 | 公式 | 含义 |
|---|---|---|
| `strat_diff_n{3,4,5,6,7}` | TF-IDF char_wb cosine，与同年 N 家最相似同行的平均距离 | 字符级方法 A，main |
| `strat_diff_n{3,4,5,6,7}_w` | TF-IDF jieba 词级 | 词级方法 B（稳健性） |
| `strat_diff_n5_lda` | LDA 主题空间 + JSD 距离 | 主题级方法 C（稳健性） |
| `strat_diff_n5_emb` | Sentence Embedding cosine | 语义稠密向量方法 D（稳健性） |
| `strat_diff_n5_ctx` / `strat_diff_n5_w_ctx` / `strat_diff_n5_lda_ctx` / `strat_diff_n5_emb_ctx` | Ctx 轨同 4 方法，仅 N=5 | ctx 轨稳健性 |

### 50.2 最相似同行（sim_max）

| 变量 | 含义 |
|---|---|
| `strat_sim_max` / `strat_sim_max_w` | char/word TF-IDF 与最相似同行的相似度（distance 倒数） |
| `strat_sim_max_lda` / `strat_sim_max_emb` | LDA/embedding 与最相似同行 |

### 50.3 Centroid 全行业向量法（谢佳松 2025）

| 变量 | 含义 |
|---|---|
| `centroid_diff_tfidf_c` / `centroid_diff_tfidf_w` | char/word TF-IDF 与全行业质心的距离 |
| `centroid_diff_lda` / `centroid_diff_emb` | LDA/embedding 与全行业质心 |
| `centroid_diff_tfidf_c_ctx` / `centroid_diff_tfidf_w_ctx` / `centroid_diff_lda_ctx` / `centroid_diff_emb_ctx` | Ctx 轨同 4 方法 |

### 50.4 Product Market Fluidity（Hoberg-Phillips-Prabhala 2014）

| 变量 | 含义 |
|---|---|
| `strat_fluidity` | char-level 竞争者向自身"领地"移动的程度 |
| `strat_fluidity_w` | word-level 同义 |

### 50.5 相邻期文本连贯性（欧阳志刚 & 胡雯华 2024）

| 变量模板 | 含义 |
|---|---|
| `coh_tfidf_c_{full,ctx}` | 今年 vs 去年文本的 TF-IDF char-level cosine |
| `coh_tfidf_w_{full,ctx}` | word-level |
| `coh_lda_{full,ctx}` | LDA 主题分布相似度 |
| `coh_emb_{full,ctx}` | Embedding cosine |

合计：**4 方法 × 2 轨 = 8 列连贯性**。

### 50.6 Text2Vec 双轨稳健性别名（§45）
| 变量 | 含义 |
|---|---|
| `strat_diff_t2v_full` / `strat_diff_t2v_ctx` | text2vec 战略差异度（stage 25 内联，详见 §45；原 stage 30 已退役） |

---

## 51. AX 权威政策响应度 (auth_sim, 4 方法 × 双轨 = 8 列)

**整体说明**：[policy_similarity.py](../pipeline/features/policy_similarity.py)（191 行）。bank-year 内"超级文档"vs 权威政策文本的语义相似度。"极简同构映射"：政策文本挂载到该年所有银行文本列表末尾，构成 (N+1) 全集，提取最后一列即各银行对政策的相似度。无文章 → NaN（v6/F3 修复，删除原 `fillna(0)` 反模式，避免 TWFE 伪零质心）。

锚定：Hassan et al. (2019, QJE) entity-proximity；Allison (2001) Missing Data + Heckman (1979, ECMA)。

### 51.1 4 方法 × 双轨 = 8 列

| 变量 | 方法 | 公式（policy_similarity.py:173-176） |
|---|---|---|
| `auth_sim_tfidf_c_{full,ctx}` | TF-IDF char_wb | 字符 n-gram 相似度 |
| `auth_sim_tfidf_w_{full,ctx}` | TF-IDF jieba 词级 | 词级 cosine |
| `auth_sim_lda_{full,ctx}` | LDA 主题空间 + JSD 散度 | `1 − sqrt(JSD)` |
| `auth_sim_emb_{full,ctx}` | Sentence Embedding | 稠密语义 cosine |

注：旧名 `auth_sim_full` / `auth_sim_ctx`（无方法后缀）**不再产出**，已替换为 4 方法分别列名；旧名 `auth_sim_std_{full,ctx}` / `auth_sim_count_{full,ctx}` 同样不再产出。

---

## 52. AY LLM Peer 动态竞争网络 IV（多阈值）

**整体说明**：[llm_peer_iv.py](../pipeline/panel/llm_peer_iv.py)（757 行）。Cao et al. (2025 WP) 框架。

工作流（[llm_peer_iv.py:482-500](../pipeline/panel/llm_peer_iv.py)）：
1. 句级双重筛选：句中含 2+ 银行名 ∧ 含 fintech 关键词
2. GPT 判断哪几对是真竞争关系（输出 confidence ∈ [0, 100]）
3. 模糊匹配（rapidfuzz）把 LLM 输出的简称还原为标准 bank_list 全称
4. 按 `cutoff ∈ {80, 70, 60}` 三阈值分别构建 peer_map
5. Lag(Y-1) 加权同行情感作为 IV（规避 Manski 反射）

### 52.1 多阈值版本（每阈值 c ∈ {80, 70, 60} 派生 3 列）

| 变量模板 | 含义 |
|---|---|
| `llm_peer_tone_iv_full_{80,70,60}` | LLM 同行 cutoff=c 阈值下加权情感 IV（核心 IV） |
| `llm_peer_coverage_iv_{80,70,60}` | LLM 同行加权新闻覆盖度 IV（辅助 IV） |
| `llm_peer_count_{80,70,60}` | LLM 同行网络连通度（诊断变量） |

### 52.2 主阈值别名（与 Stata 模板对齐，cutoff=80）

| 变量 | 等价 |
|---|---|
| `llm_peer_tone_iv_full` | = `llm_peer_tone_iv_full_80` |
| `llm_peer_coverage_iv` | = `llm_peer_coverage_iv_80` |
| `llm_peer_count` | = `llm_peer_count_80` |

### 52.3 竞争强度指数（多阈值）

| 变量 | 公式 | 含义 |
|---|---|---|
| `peer_compete_idx_{80,70,60}` | 与 LLM 识别同行共现的文章比例 ∈ [0, 1] | 阈值化竞争强度 |
| `peer_compete_idx` | = `peer_compete_idx_80` 主阈值别名 | — |

---

## 53. AZ Embedding Peer 网络

**整体说明**：Hoberg & Phillips (2016) 框架，基于 Sentence Embedding 向量相似度构建动态同业网络权重矩阵，加权同行情感作为控制变量，补充共现网络的语义维度。

| 变量 | 含义 |
|---|---|
| `emb_peer_tone_full` / `emb_peer_tone_ctx` | embedding 加权同行情感 |
| `emb_peer_sim_idx` | 同业 SBERT 相似度均值 |
| `emb_peer_top5_tone_{full,ctx}` | top-5 最相似同业的加权情感 |

---

## 54. BA Stage 49 风险承担结果

**整体说明**：[`pipeline/panel/risk_taking_outcomes.py`](../pipeline/panel/risk_taking_outcomes.py)（455 行）。第 10/11 篇 paper outcome 变量。`aggregate_quarterly_to_yearly()` 把季度数据分 stock / intensive / flow 三类聚合（[risk_taking_outcomes.py:101-104](../pipeline/panel/risk_taking_outcomes.py#L101-L104)）：
- **stock**（年末或最后可得季度 forward-fill）：`total_assets, rwa, npl_balance, total_loans, loan_loss_provision`
- **intensive**（年内均值）：`roa, capital_adequacy_ratio, npl_ratio`
- **flow**（年内累计）：`loan_writeoffs`

锚定：Roy (1952) Safety-First Z-score；Berger, Klapper & Turk-Ariss (2009, JFS) 银行业 Z-score；Beatty & Liao (2014, JAE) LLP discretion；Acharya, Anginer & Warburton (2016, RFS) 隐性担保（implicit_guarantee_tier）。

### 54.1 `OUTPUT_OUTCOME_COLS` 完整字段（risk_taking_outcomes.py:69-82）

| 变量 | 公式 / 含义 |
|---|---|
| `z_score` | Roy (1952) Z-score = `(ROA + EQTA) / σ(ROA)`（破产距离）—— **注意是 `z_score` 不是 `zscore`** |
| `npl_formation_rate` | 不良贷款形成率 = `Δ NPL / loans`（流量） |
| `writeoffs_imputed` | 0/1，v3.7.0 M7 缺失补全旗（writeoffs imputation indicator） |
| `rwa_to_ta_ratio` | RWA / 总资产 = 风险密度 |
| `sigma_roa_5y_rolling` | ROA 5 年滚动标准差（Z-score 的分母原料） |
| `loan_loss_provision_discretion` | 原始 LLP/Loans 比率（BW 2012 残差化在 Stata 端做） |
| `roa` | 原始 ROA（fallback path γ 保留） |
| `npl_ratio` | 原始 NPL ratio（fallback 保留） |
| `is_soe` | 国有标识（与 panel 主 `is_soe` 一致） |
| `bank_type_id` | bank_type 数值编码（int） |
| `implicit_guarantee_tier` | Acharya-Anginer-Warburton (2016, RFS) 隐性担保层级 ∈ {`big6`, `dsib`, `policy`, `joint_listed_h`, `joint_listed_a`, `city_listed`, `other`} |

合计 **11 列**（不计 target_bank / year 两个主键）。

### 54.2 季度 → 年度聚合的 3 个中间 DataFrame（不进 panel）
| df | 含义 | 列 |
|---|---|---|
| `df_stock` | stock 类 forward-fill | total_assets / rwa / npl_balance / total_loans / loan_loss_provision |
| `df_intensive` | 强度类年均 | roa / capital_adequacy_ratio / npl_ratio |
| `df_flow` | 流量类年累 | loan_writeoffs |

### 54.3 缺失行为
| 列 | NaN 触发条件 |
|---|---|
| `z_score` | `sigma_roa_5y_rolling` 滚动窗 < 4 期 |
| `npl_formation_rate` | 前一期 NPL 或 loans 缺失 |
| `rwa_to_ta_ratio` | rwa 或 total_assets 缺失 |
| 所有 | bank-year 完全无 quarterly 数据（fallback path γ 触发） |

### 54.4 内在含义解读（**第 10/11 篇 paper outcome**）

**为什么是这 4 个 outcome 而非 ROA**：
- 论文核心问题是"fintech 报道如何影响**银行风险承担**"——ROA 是 outcome 但不是 risk 直接度量；
- **z_score**（Roy 1952 + Berger-Klapper-Turk-Ariss 2009 JFS）：破产距离，越高越安全 → 风险承担↓；
- **npl_formation_rate**（Δ NPL / loans）：**流量**指标，捕捉新增风险（vs `npl_ratio` 存量）；
- **rwa_to_ta_ratio**：风险加权资产 / 总资产 = 资产组合"密度"——监管视角的风险度量；
- **loan_loss_provision_discretion**（Beatty & Liao 2014 JAE）：LLP 中的会计 discretion 部分，捕捉"管理层主动调节准备金"行为。

**4 个 outcome 的因果链解读**：
```
fintech tone (Treatment) 
  → 银行战略选择（自主 vs 协同）
    → 风险承担行为
      → z_score ↑↓ (整体风险)
      → npl_formation_rate ↑↓ (信贷扩张质量)
      → rwa_to_ta_ratio ↑↓ (资产风险密度)
      → llp_discretion ↑↓ (盈余管理)
```

**`implicit_guarantee_tier` 异质性维度**：
- Acharya-Anginer-Warburton (2016 RFS) 框架：政府隐性担保高的银行（big6 / dsib）→ moral hazard → 风险承担更激进；
- 论文常做 `c.benefit_mean_ctx##i.implicit_guarantee_tier` 异质性分析。

**典型 Stata spec（第 10 paper main）**：
```stata
* Main: cross-media disagreement 对风险承担
foreach y in z_score npl_formation_rate rwa_to_ta_ratio loan_loss_provision_discretion {
    reghdfe `y' cross_outlet_tone_variance_full controls, ///
        absorb(target_bank year) cluster(bank_province)
}

* 异质性: 隐性担保层级
reghdfe z_score c.cross_outlet_tone_variance_full##i.implicit_guarantee_tier controls, ///
    absorb(target_bank year)

* LLP discretion: BW 2012 残差化 + tone 影响
* Step 1: 残差化（Stata 端做）
reghdfe loan_loss_provision_discretion L.npl_ratio L.loan_growth, absorb(target_bank year) resid
predict llp_resid, residual
* Step 2: tone → llp_resid
reghdfe llp_resid benefit_mean_ctx controls, absorb(target_bank year)
```

**陷阱**：
- ⚠ **数据来源 fallback 三级**：α (Wind) → β (银保监 PDF) → γ (估算)；`writeoffs_imputed = 1` 标识 imputation 行 → 论文应在 Robustness 中报告排除这些行的结果；
- ⚠ **季度 → 年度聚合规则**：stock 类用最后可得季度（v3.7.0 M8 修复 Q4 缺失即全年丢失的 bug），intensive 类用年均，flow 类用年累——这意味着 z_score 是**年均 ROA**算出的，与季度高频版不同；
- ⚠ **`z_score` 不是 `zscore`**：命名差异！老脚本可能引用错误名导致 KeyError。

---

## 55. BB Stage 51 Falsification 衍生列

**整体说明**：[`pipeline/falsification/controls.py`](../pipeline/falsification/controls.py)（1194 行）。在 `46_panel_yearly_full.dta` 基础上追加 **2 类衍生列**：(i) 非金融科技对照变量（nf_*/all_*/fintech_share/ln_*）；(ii) placebo DID（每个政策前移 k 年的伪 treatment）。

锚定：
- Fang & Peress (2009, JF 64(5), 2023-2052) `nf_ln_coverage = log(1+count)`
- Bushee, Core, Guay & Hamm (2010, JAR 48(1), 1-19) `nf_media_breadth` 信息环境
- Bertrand, Duflo & Mullainathan (2004, QJE) "Pre-treatment placebo tests are essential for validating parallel trends"

### 55.1 非金融科技对照变量（9 列，runner [controls.py:475-630](../pipeline/falsification/controls.py))

| 变量 | 公式 | 含义 |
|---|---|---|
| `nf_n_articles` | `count(非金融科技新闻)` per (bank, year) | 非 fintech 篇数 |
| `nf_ln_coverage` | `ln(1 + nf_n_articles)` | 对数化（Fang & Peress 2009） |
| `nf_media_breadth` | `nunique(媒体)` over non-fintech articles | 非 fintech 媒体来源数（Bushee et al. 2010） |
| `nf_headline_frac` | `mean(target_bank_in_title)` over non-fintech | 非 fintech 标题提及率 |
| `all_n_articles` | `n_articles + nf_n_articles` | 全部新闻总数（穷举） |
| `all_ln_coverage` | `ln(1 + all_n_articles)` | 全部对数化 |
| `fintech_share` | `n_articles / all_n_articles`（分母 0 → NaN） | fintech 新闻占比 |
| `ln_ft_articles` | `ln(1 + n_articles)` | fintech 对数化（与 nf 对偶） |
| `ln_nf_articles` | `ln(1 + nf_n_articles)` | non-fintech 对数化 |

恒等式校验：`all_n_articles == n_articles + nf_n_articles` 全行成立 ✓（[controls.py:636](../pipeline/falsification/controls.py#L636)）。

### 55.2 Placebo DID 变量（每个政策 prefix × 3 shift × 2 列）

[`generate_placebo_did_variables(panel, placebo_shifts=[1, 2, 3])`](../pipeline/falsification/controls.py#L929)：对每个 DID 政策冲击，将 `treat_year` 提前 k 年生成伪处理变量。

**每个 prefix（dcep / sandbox）+ 每个 shift k ∈ {1, 2, 3}** 派生 2 列：

| 变量模板 | 公式 |
|---|---|
| `{prefix}_placebo{k}_post` | `(year ≥ treat_year − k).astype(int)`（仅对 treated 银行） |
| `{prefix}_placebo{k}_did` | `treated × placebo_post`（伪 DID 交互项） |

**合计**：2 prefix × 3 shifts × 2 cols = **12 placebo 列**。

Stata 验证：
```stata
* Placebo DID 应不显著（若显著 → 平行趋势违反）
reghdfe Y dcep_placebo2_did X, absorb(bank_id year) cluster(bank_id)
```

### 55.3 列数核算（51_panel_with_controls.dta ≈ 2033 列）
| 来源 | 列数 |
|---|---|
| `46_panel_yearly_full.dta` 全列继承 | ~2024 |
| `nf_*` / `all_*` / `fintech_share` / `ln_*` 共 9 列 | +9 |
| `{dcep,sandbox}_placebo{1,2,3}_{post,did}` 共 12 列 | +12 |
| **合计** | **≈ 2045**（实测 2033 偏差源于某些 placebo 列因前置 DID 政策为空跳过） |

### 55.4 v6/F3 缺失约定（不填 0）
所有 nf_* / all_* / fintech_share 列在 `n_articles == 0` 时**保留 NaN**——Allison (2001) + Heckman (1979) 论证：强填 0 会在 TWFE 中制造伪零质心污染系数。Stata 端 listwise deletion 自然处理。

---

## 56. BC Stata 列名缩写映射

**整体说明**：超过 32 字符的列名被 [`shorten_long_column_names()`](../pipeline/panel/stata_export.py#L329) 自动缩写，原名记录在 `46_panel_yearly_codebook.xlsx::original_name`。

固定缩写规则（[stata_export.py:341-346](../pipeline/panel/stata_export.py#L341-L346)）：

| 原名子串 | 缩写 | 例 |
|---|---|---|
| `_idf_score_` | `_idfsc_` | `jiang_2021_idf_score_w_sum_full` → `jiang_2021_idfsc_w_sum_full` |
| `_leave1out_` | `_l1o_` | `province_leave1out_full` → `province_l1o_full` |
| `_dict_avg_tone_` | `_davg_t_` | `_dict_avg_tone_full` → `_davg_t_full` |
| `_bert_avg_pos_` | `_bavg_p_` | `_bert_avg_pos_full` → `_bavg_p_full` |

仍超 → 截断到 32 字符，冲突 → 加 `_1` / `_2` 后缀。

---

## 57. BD 缺失语义约定

**整体说明**：v6/F3 之后所有"无新闻 bank-year"列**保留 NaN**，由 Stata listwise deletion 自然处理（Allison 2001 §3 + Heckman 1979 ECMA）。

| 列类型 | balance_panel 填充策略 |
|---|---|
| `n_articles*` / 所有 `_sum` / 计数类 | fillna(0) |
| `ln_news_coverage` / `media_breadth` | fillna(0) |
| `sum_mention_density` / `sum_doc_length` / `sum_target_mentions` / `sum_media_authority_weight` | fillna(0) |
| `pos_count_vw` / `neg_count_vw` | fillna(0) |
| `tech_frac` / `app_frac` / `sub_frac` / `symb_frac` / `indep_frac` / `collab_frac` / `avg_category_confidence` | 保留 NaN |
| 所有 `*_tone` / `*_cont` / `*_frac` / `*_ratio` / `concern_score` | 保留 NaN |
| `auth_sim_*` / `benefit_*` / `policy_cosine_sim*` | 保留 NaN（v6/F3 修复，删除 `fillna(0)`） |
| `token_adopt_*` / `hidden_adopt_*` / `subst_adopt_*` | 保留 NaN |
| `strat_diff_t2v_*` / `policy_cosine_sim_t2v_*` | 保留 NaN |
| `d4_data_quality_flag` | 'ok' / 'insufficient' 字符串 |

Stata 端：必须用 `xtreg` / `reghdfe` 走 listwise deletion，禁止 `mi impute` 0 填充（会人为制造伪零质心）。

---

## 57bis 9 个 paper-specific 模块对 panel 的关系

**整体说明**：`papers/` 目录下 9 个 paper 子模块（bank_fintech_tone / attention / substance / locus / collab / benefit_society / brokerage_network / llm_peer / strategic_diff）的所有 `analysis.py` / `tables.py` / `figures.py` 都是**纯消费层**——读 panel → 跑 Stata 回归 → 写表/图。它们**不写回 stage 46 .dta 三件套**，也不修改主 panel。

### 设计意图
Panel = "方法学中立"的 data warehouse（Hassan 2019 QJE 风格）；论文 = "应用层"。Treatment 定义（如 `llm_peer_tone_iv_full_80` / `tone_gap_sub_symb_sc_ctx` / `cross_outlet_tone_variance_full`）**在 stage 21–49 已全部预计算**到 panel。Paper 端仅需选用已有列做回归。

### 9 个 paper analysis.py 的统一行为
| Paper | analysis.py | 调用链 |
|---|---|---|
| `bank_fintech_tone` | [analysis.py](../papers/bank_fintech_tone/analysis.py) | `run_main_pipeline()` → `tables.*` → `figures.*` |
| `bank_fintech_attention` (P2) | [analysis.py](../papers/bank_fintech_attention/analysis.py) | 同上 |
| `bank_fintech_substance` (P3) | [analysis.py](../papers/bank_fintech_substance/analysis.py) | 同上 |
| `bank_fintech_locus` (P4) | [analysis.py](../papers/bank_fintech_locus/analysis.py) | 同上 |
| `bank_fintech_collab` (P5) | analysis.py — **deferred**, 见 v3.7.3 known issue | manuscript/refs.bib onboarding 未完成; figures.py + tables.py + paper_spec.yaml 已就位, analysis.py 待补 |
| `benefit_society` | [analysis.py](../papers/benefit_society/analysis.py) | 同上 + `--stage robustness_stage_a` 触发 27c sibling pipeline |
| `brokerage_network` | [analysis.py](../papers/brokerage_network/analysis.py) | 同上 |
| `llm_peer` | [analysis.py](../papers/llm_peer/analysis.py) | 同上 |
| `strategic_diff` | [analysis.py](../papers/strategic_diff/analysis.py) | 同上 |

### `papers/_common/` 13 个共享工具模块
| 模块 | 职责 | 派生列 |
|---|---|---|
| [panel_loader.py](../papers/_common/panel_loader.py) | 加载 `46_*.dta` / `40_*.parquet`，仅 `pd.read_parquet()` | 无 |
| [paper_config.py](../papers/_common/paper_config.py) | 9 个 paper 的 `PaperConfig` dataclass（main spec / paths / Stata 模板路径） | 无 |
| [paper_registry.py](../papers/_common/paper_registry.py) | 9 个 paper 注册表 | 无 |
| [pipeline_runner.py](../papers/_common/pipeline_runner.py) | 子进程编排 `run_pipeline_function.py` | 无 |
| [stata_runner.py](../papers/_common/stata_runner.py) | CLI 子命令 `build-replication` / `list-templates` / `doctor` / `verify-replication` | 无 |
| [stata_postprocess.py](../papers/_common/stata_postprocess.py) | Stata 输出后处理（系数表、p 值校正） | 无（写 .tex / .csv 表格） |
| [tables.py](../papers/_common/tables.py) | 表格生成（descriptives / Table 1 / robustness） | 无 |
| [figures.py](../papers/_common/figures.py) / [paper_figures_ext.py](../papers/_common/paper_figures_ext.py) | 图表生成（matplotlib） | 无（写 .png / .pdf） |
| [stats_helpers.py](../papers/_common/stats_helpers.py) | 描述性统计辅助 | 无 |
| [derivative_replication.py](../papers/_common/derivative_replication.py) | replication 包结构验证 | 无 |
| [_git_utils.py](../papers/_common/_git_utils.py) | git 提交版本信息（写入 replication 包） | 无 |

### 结论
所有 paper 端的"派生指标"——例如某 paper 跑回归前对 `tone_gap_sub_symb_sc_ctx` 做了 winsorize / standardize / lag / DD interaction——都是**论文工作流的瞬时变换**，存在于 Stata `.do` 模板的局部 `gen` / `egen` 语句中，**不持久化到 stage 46 主 panel**。

复现包结构（[stata_runner.py](../papers/_common/stata_runner.py)）：
```
replication_{paper_id}/
├── data/processed/46_panel_yearly_full.dta    # 上游导出，未改动
├── data/processed/27c_*.parquet               # 27c sibling（仅 benefit_society）
├── stata/                                      # 14 主模板（实测）+ 8 paper-specific
│   ├── 00_master.do.tmpl              # 编排所有模板
│   ├── 01_data_prep.do.tmpl           # use .dta + label apply + 主键 xtset
│   ├── 10_table1_descriptives.do.tmpl # Table 1 描述统计
│   ├── 11_table2_main_m1m6.do.tmpl    # **Main regression** M1→M6 progressive controls/FE
│   ├── 12_table3_mechanism.do.tmpl    # 机制检验
│   ├── 13_table4_heterogeneity.do.tmpl # 异质性分析
│   ├── 14_table5_advanced_robustness.do.tmpl # 高级稳健性
│   ├── 20_tableA1_inter_track_kappa.do.tmpl  # Appendix A1 双轨 κ（消费 stage 39a）
│   ├── 21_tableA2_main_spec_switch.do.tmpl   # Appendix A2 main spec switch sensitivity
│   ├── 22_tableA3_bartik_iv.do.tmpl          # Appendix A3 Bartik IV (6 类 + Rotemberg)
│   ├── 23_tableA4_radius_sensitivity.do.tmpl # Appendix A4 radius 敏感性（消费 stage 35）
│   ├── 24_tableA5_dictionary_method.do.tmpl  # Appendix A5 词典法对比
│   ├── 30_figure1_event_study.do.tmpl        # Figure 1 event-study plot
│   └── 31_figure_coefplot_dual.do.tmpl       # Figure 2 双轨 coefplot
├── tables/                                     # .tex / .csv 输出
├── figures/                                    # .png / .pdf 输出
└── README.md                                   # AI Disclosure + reproducibility
```

---

## 58. 附录 A：导出文件清单

```
data/processed/
├── 46_panel_yearly_core.dta       # Stata IC 兼容 (≤ 2048 cols)
├── 46_panel_yearly_aux.dta        # core 互补集
├── 46_panel_yearly_full.dta       # 全列 (本机 MP 直接读)
├── 46_panel_yearly_labels.do      # variable labels + value labels apply 脚本
├── 46_panel_yearly_codebook.xlsx  # 人类可读 codebook (var_name + original_name + label + dtype + stat)
├── 51_panel_with_controls.dta     # falsification 后终局面板 (≈ 2033 cols)
├── variable_codebook.xlsx         # 完整变量字典 (codebook.py 生成)
├── variable_codebook.csv
├── variable_codebook.md
├── variable_codebook.json
├── v3_5_1_constants.json          # sidecar: median_amb_d0 + prompt_v8_sha256 + stage21_last_run_timestamp
├── v3_4_0_ctx_coverage_baseline.json   # D4 ctx coverage baseline
└── 17_topic_metadata.json         # BERTopic K + 主题元信息
```

辅助 Stata 模板（91 个 .do.tmpl，已全部 bump 到 `version 19`）：
- `papers/_common/stata_templates/` 主线 14 模板
- `papers/{paper_id}/` 8 个 paper-specific 子目录 74 模板
- `papers/_common/stata_templates/v3_5_0/` + `v3_5_1/` 历史归档 3 模板

---

## 59. 附录 B：笛卡尔积命名模板枚举

### B.1 模型/词典/BERT 集合

```python
LLM_MODELS  = ['gpt54nano', 'gemini31111', 'deepseekv4']                          # 3 个
DICT_NAMES  = ['jiang_2021', 'yao_2021', 'bian_2021', 'du_2022', 'you_2018']      # 5 个
BERT_MODELS = ['finbert_cn', 'fin_sent_zh', 'erlangshen', 'hw2942', 'finbert2']   # 5 个
THREE_CLASS_BERT = {'finbert_cn', 'fin_sent_zh', 'hw2942'}                         # 3 个含中性
TRACKS      = ['_full', '_ctx', '_title']                                          # 3 轨
TRACKS_DUAL = ['_full', '_ctx']                                                    # 2 轨 (无 title)
SUBSETS_LOCUS   = ['_tech', '_app', '_tech_lc_ctx', '_app_lc_ctx']
SUBSETS_SUBST   = ['_sub', '_symb', '_sub_sc_ctx', '_symb_sc_ctx']
SUBSETS_COLLAB  = ['_indep', '_collab', '_indep_cm_ctx', '_collab_cm_ctx']
WEIGHTS     = ['', '_w', '_mw', '_hw']   # 等权 + VW + MW + HW
```

### B.2 LLM 模板（完整笛卡尔展开）

```
{model}_score_{track}                   3 × 3 = 9 列 (篇章级)
{model}_cont_{track}                    3 × 3 = 9 列 (篇章级)
{model}_score_{w,mw,hw}_{track}         3 × 3 × 3 = 27 列 (篇章级加权)
{model}_cont_{w,mw,hw}_{track}          3 × 3 × 3 = 27 列 (篇章级加权)
{model}_tone_{track}                    3 × 3 = 9 列 (bank-year mean)
{model}_tone_sum_{track}                3 × 3 = 9 列
{model}_tone_std_{track}                3 × 3 = 9 列
{model}_cont_mean_{track}               3 × 3 = 9 列
{model}_cont_sum_{track}                3 × 3 = 9 列
{model}_score_{w,mw,hw}_sum_{track}     3 × 3 × 3 = 27 列
{model}_cont_{w,mw,hw}_sum_{track}      3 × 3 × 3 = 27 列
{model}_tone_{vw,mw,hw}_{track}         3 × 3 × 3 = 27 列 (最终加权 tone)
{model}_tone_{tech,app,sub,symb,indep,collab}_{full,ctx}   3 × 6 × 2 = 36 列 (子集均值)
```
**LLM 类合计** ≈ **234 列**（不计 prob_score）。

### B.3 词典模板

```
{dict}_score_{track}                    5 × 3 = 15 列 (篇章级)
{dict}_idf_score_{track}                5 × 3 = 15 列
{dict}_pos_ratio_{track}                5 × 3 = 15 列 (词级)
{dict}_neg_ratio_{track}                5 × 3 = 15 列
{dict}_score_{w,mw,hw}_{track}          5 × 3 × 3 = 45 列
{dict}_idf_score_{w,mw,hw}_{track}      5 × 3 × 3 = 45 列
{dict}_tone_{track}                     5 × 3 = 15 列 (bank-year mean)
{dict}_tone_sum_{track}                 5 × 3 = 15 列
{dict}_tone_std_{track}                 5 × 3 = 15 列
{dict}_idf_tone_{track}                 5 × 3 = 15 列
{dict}_idf_tone_sum_{track}             5 × 3 = 15 列
{dict}_idf_tone_std_{track}             5 × 3 = 15 列
{dict}_score_{w,mw,hw}_sum_{track}      5 × 3 × 3 = 45 列
{dict}_idf_score_{w,mw,hw}_sum_{track}  5 × 3 × 3 = 45 列
{dict}_tone_{vw,mw,hw}_{track}          5 × 3 × 3 = 45 列
{dict}_idf_tone_{vw,mw,hw}_{track}      5 × 3 × 3 = 45 列
{dict}_pos_count_{full,ctx}             5 × 2 = 10 列
{dict}_pos_symb_count_{full,ctx}        5 × 2 = 10 列
{dict}_neg_count_{full,ctx}             5 × 2 = 10 列
avg_{dict}_pos_ratio_{full,ctx}         5 × 2 = 10 列
avg_{dict}_neg_ratio_{full,ctx}         5 × 2 = 10 列
{dict}_tone_{tech,app,sub,symb}_{track} 5 × 4 × 3 = 60 列
{dict}_idf_tone_{tech,app,sub,symb}_{track}  5 × 4 × 3 = 60 列
disag_{dict}_{full,ctx}                 5 × 2 = 10 列
{dict}_cater_{full,ctx}                 5 × 2 = 10 列
{dict}_cater_b_{full,ctx}               5 × 2 = 10 列
washing_ratio_{dict}{_ctx}              5 × 2 = 10 列
```
**词典类合计** ≈ **570 列**。

### B.4 BERT 模板

```
{bert}_{正面,负面}_{track}              5 × 2 × 3 = 30 列 (篇章级原始)
{bert}_中性_{track}                     3 × 3 = 9 列 (3-class 模型)
{bert}_{正面,负面}_{w,mw,hw}_{track}   5 × 2 × 3 × 3 = 90 列
{bert}_pos_{track}, _neg_{track}, _pos_sum_{track}, _neg_sum_{track}, _pos_std_{track}
                                        5 × 3 × 5 = 75 列 (bank-year)
{bert}_neu_{track}, _neu_sum_{track}    3 × 3 × 2 = 18 列
{bert}_{正面,负面}_{w,mw,hw}_sum_{track}   5 × 2 × 3 × 3 = 90 列
{bert}_{pos,neg}_{vw,mw,hw}_{track}    5 × 2 × 3 × 3 = 90 列
{bert}_{pos,neg}_{tech,app,sub,symb}_{track}  5 × 2 × 4 × 3 = 120 列
{bert}_neu_{tech,app,sub,symb}_{track}  3 × 4 × 3 = 36 列
{bert}_pos_count_{full,ctx}             5 × 2 = 10 列
{bert}_pos_symb_count_{full,ctx}        5 × 2 = 10 列
{bert}_neg_count_{full,ctx}             5 × 2 = 10 列
disag_{bert}_{full,ctx}                 5 × 2 = 10 列
cater_{bert}_{full,ctx}                 5 × 2 = 10 列
washing_ratio_{bert}{_ctx}              5 × 2 = 10 列
```
**BERT 类合计** ≈ **618 列**。

### B.5 加权方式后缀汇总

| 后缀 | 含义 | 篇章级 / bank-year |
|---|---|---|
| `_w` | mention_density 加权（VW） | 篇章级 `_w` + bank-year `_w_sum` |
| `_vw` | VW 加权后的最终 tone（`_w_sum / sum_mention_density`） | bank-year |
| `_mw` | media_authority_weight 加权 | 同 `_w` / `_mw` |
| `_hw` | herd_weight_{full/ctx/full} 双轨加权 | 同上 |

### B.6 三轨 + 双轨指标分布（来自 docs/PANEL_DATA_INFO.md）

| 轨道 | 列数 | 说明 |
|---|---|---|
| `_full` | 511 | 全文输入 |
| `_ctx` | 531 | 实体前后窗口（Hassan 2019） |
| `_title` | 388 | 仅标题 |

---

## 60. 附录 C：完整参考文献

按字母序排列。括号内是本文档中引用本文献的章节锚点。

**A**
- Abraham, J., Olbert, M., & Vasvari, F. P. (2024). ESG disclosures in the private equity industry. *Journal of Accounting Research*, 62(5), 1611-1660. DOI: 10.1111/1475-679X.12570 *(§29)*
- Adner, R., & Kapoor, R. (2010). Value creation in innovation ecosystems. *SMJ*, 31(3), 306-333. *(§21)*
- Allison, P. D. (2001). *Missing Data*. SAGE. DOI: 10.4135/9781412985079 *(§45 §57)*
- Angelico, C., Marcucci, J., Miccoli, M., & Quarta, F. (2022). Can we measure inflation expectations using Twitter? *Journal of Econometrics*, 228(2), 259-277. *(§43)*
- Angrist, J. D., & Pischke, J.-S. (2009). *Mostly Harmless Econometrics*. Princeton University Press. *(§18 §39)*
- Antweiler, W., & Frank, M. Z. (2004). Is all that talk just noise? *JF*, 59(3), 1259-1294. *(§42)*

**B**
- Baker, S. R., Bloom, N., & Davis, S. J. (2016). Measuring economic policy uncertainty. *QJE*, 131(4), 1593-1636. *(§30)*
- Berger, A. N., Klapper, L. F., & Turk-Ariss, R. (2009). Bank competition and financial stability. *JFS*, 35(2), 99-118. *(§54)*
- Berger, P., Kim, J., & Ma, P. (2024). [Sentiment word ratios]. *CAR*. *(§4 §11)*
- Billio, M., Getmansky, M., Lo, A. W., & Pelizzon, L. (2012). Econometric measures of connectedness and systemic risk. *JFE*, 104(3), 535-559. *(§48)*
- Bingler, J. A., Kraus, M., Leippold, M., & Webersinke, N. (2022). Cheap talk and cherry-picking. *FRL*, 47B, 102776. *(§16 §22)*
- Bonsall, S. B., Leone, A. J., Miller, B. P., & Rennekamp, K. (2017). A plain English measure of financial reporting readability. *JAE*, 63(2-3), 329-357. *(§23)*
- Boschma, R. (2005). Proximity and innovation. *Regional Studies*, 39(1), 61-74. *(§48)*
- Brambor, T., Clark, W. R., & Golder, M. (2006). Understanding interaction models. *PA*, 14(1), 63-82. *(§39)*

**C**
- Cao et al. (2025). [LLM voting for financial sentiment]. *(§7 §52)*
  > **R1-R5 audit fix A11 (2026-05-27)**: 此 entry 此前用 "Cao S., Jiang W.,
  > Wang J., Yang B." 与 `pipeline/panel/llm_peer_iv.py:16-18` (Cao Y./Chen L./
  > Tucker J.W./Wan C., RAS 30(4):3344-3386 DOI 10.1007/s11142-025-09892-6) +
  > `papers_assets/llm_peer/README.md:47` (Cao Z./Li/Wang/Zhao, Review of Asset
  > Studies) 作者列表 + 期刊名全不一致 (>=3 处). 投稿前必须 CrossRef 验证唯一
  > 真实引用. 当前 canonical source: `llm_peer_iv.py:16-18`.
- Cao, S., Jiang, W., Yang, B., & Zhang, A. L. (2023). How to talk when a machine is listening. *RFS*, 36(9), 3603-3642. *(§44)*
- Chesbrough, H. W. (2003). *Open Innovation*. Harvard Business School Press. *(§16)*
- Cover, T. M., & Thomas, J. A. (2006). *Elements of Information Theory* (2nd ed.). Wiley. *(§10)*

**D**
- Da, Z., Engelberg, J., & Gao, P. (2011). In search of attention. *JF*, 66(5), 1461-1499. *(§6)*
- Dahlke, et al. (2024). [Cognitive proximity in financial networks]. *(§48)*
- Davis, A. K., & Tama-Sweet, I. (2012). Managers' use of language across alternative disclosure outlets. *CAR*, 29(3), 804-837. *(§24)*
- De Bondt, W. F. M., & Thaler, R. (1985). Does the stock market overreact? *JF*, 40(3), 793-805. *(§40)*
- Deephouse, D. L. (2000). Media reputation as a strategic resource. *Journal of Management*, 26(6), 1091-1112. *(§22 §41)*
- Distel, A. P., Grimpe, C., & Poetz, M. (2026). From evidence to impact. *Research Policy*, 55(3), 105426. *(§36)*

**E**
- Edwards, J. R. (2001). Ten difference score myths. *ORM*, 4(3), 265-287. *(§15 §27)*
- Engelberg, J. E., & Parsons, C. A. (2011). The causal impact of media in financial markets. *JF*, 66(1), 67-97. *(§5 §37 §47)*

**F**
- Fang, L. H., & Peress, J. (2009). Media coverage and the cross-section of stock returns. *JF*, 64(5), 2023-2052. *(§6 §39)*
- Fiss, P. C., & Zajac, E. J. (2006). The symbolic management of strategic change. *ASQ*. *(§16)*
- Freeman, L. C. (1979). Centrality in social networks conceptual clarification. *Social Networks*, 1(3), 215-239. *(§48)*

**G**
- Garcia, D. (2013). Sentiment during recessions. *JF*, 68(3), 1267-1300. *(§39 §42)*
- Gentzkow, M., Kelly, B., & Taddy, M. (2019). Text as data. *JEL*, 57(3), 535-574. *(§11 §13)*
- Gilardi, F., et al. (2023). ChatGPT outperforms crowd workers. *PNAS*. *(§17)*
- Goldfarb, A., & Tucker, C. (2019). Digital economics. *JEL*, 57(1), 3-43. *(§37)*
- Goldsmith-Pinkham, P., Sorkin, I., & Swift, H. (2020). Bartik instruments. *AER*, 110(8), 2586-2624. *(§37)*
- Gomber, P., Kauffman, R. J., Parker, C., & Weber, B. W. (2018). On the fintech revolution. *JMIS*, 35(1), 220-265. *(§16)*
- Gurun, U. G., & Butler, A. W. (2012). Don't believe the hype. *JF*, 67(2), 561-598. *(§47)*
- Guzman, J., & Li, A. (2023). [Strategic differentiation in firm narratives]. *(§50)*

**H**
- Hagedoorn, J. (2002). Inter-firm R&D partnerships. *Research Policy*, 31(4), 477-492. *(§16)*
- Hales, J., Kuang, X. J., & Venkataraman, S. (2011). Who believes the hype? *CAR*, 28(1), 223-259. *(§24)*
- Han, B., Subrahmanyam, A., & Zhou, Y. (2024). [Information brokerage networks]. *RFS*. *(§49)*
- Hassan, T. A., Hollander, S., van Lent, L., & Tahoun, A. (2019). Firm-level political risk. *QJE*, 134(4), 2135-2202. *(§7 §20 §51)*
- He, X., et al. (2024). MSENT counts. *IRFA*. *(§4)*
- Heckman, J. J. (1979). Sample selection bias as a specification error. *Econometrica*, 47(1), 153-161. *(§45 §57)*
- Hillert, A., Jacobs, H., & Müller, S. (2014). Media makes momentum. *JF*, 69(5), 2095-2143. *(§5)*
- Hoberg, G., & Phillips, G. (2016). Text-based network industries and endogenous product differentiation. *JPE*, 124(5), 1423-1465. *(§50 §53)*
- Holzman, E. R., Miller, B. P., & Twedt, B. J. (2023). Curbing enthusiasm. *TAR*, 98(7), 315-345. *(§5 §14)*
- Huang, A. H., Wang, H., & Yang, Y. (2023). FinBERT. *CAR*, 40(2), 806-841. *(§12 §44)*

**J**
- Janis, I. L., & Fadner, R. H. (1965). [J-F sentiment coefficient]. *(§41)*
- Jaynes, E. T. (1957). Information theory and statistical mechanics. *Physical Review*, 106(4), 620. *(§10)*
- Jha, M., Liu, H., & Manela, A. (2026). Does finance benefit society? *RFS*, 39(5), 1227-1266. *(§35)*

**K**
- Kozlowski, A. C., Taddy, M., & Evans, J. A. (2019). The geometry of culture. *ASR*, 84(5), 905-949. *(§35)*

**L**
- Laursen, K., & Salter, A. (2006). Open for innovation. *SMJ*, 27(2), 131-150. *(§16)*
- Leary, M. T., & Roberts, M. R. (2014). Do peer firms affect corporate financial policy? *JF*, 69(1), 139-178. *(§47 §48)*
- Li, K., Sun, T., Wang, B., & Yannelis, C. (2021). FinTech, financial inclusion, and income inequality. *RFS*. *(§29)*
- Li, F. (2010). The information content of forward-looking statements. *JAR*, 48(5), 1049-1102. *(§26)*
- Loughran, T., & McDonald, B. (2011). When is a liability not a liability? *JF*, 66(1), 35-65. *(§22 §23 §25)*
- Loughran, T., & McDonald, B. (2014). Measuring readability in financial disclosures. *JF*, 69(4), 1643-1671. *(§4)*
- Loughran, T., & McDonald, B. (2016). Textual analysis in accounting and finance. *JAR*, 54(4), 1187-1230. *(§22)*
- Luo & Li (2025). [Province-level news sentiment IV]. *(§37 §47)*

**M**
- Manski, C. F. (1993). Identification of endogenous social effects. *RES*, 60(3), 531-542. *(§49)*

**N**
- Nosek, B. A., et al. (2018). The preregistration revolution. *PNAS*. *(§16)*

**R**
- Reimers, N., & Gurevych, I. (2019). Sentence-BERT. *EMNLP*, 3982-3992. *(§35 §53)*
- Roy, A. D. (1952). Safety first and the holding of assets. *Econometrica*, 20(3), 431-449. *(§54)*
- Royston, P., Altman, D. G., & Sauerbrei, W. (2006). Dichotomizing continuous predictors in multiple regression. *Statistics in Medicine*, 25(1), 127-141. *(§36)*

**S**
- Sautner, Z., van Lent, L., Vilkov, G., & Zhang, R. (2023). Firm-level climate change exposure. *JF*, 78(3), 1449-1498. *(§13)*
- Shapiro, A. H., Sudhof, M., & Wilson, D. J. (2022). Measuring news sentiment. *Journal of Econometrics*, 228(2), 221-243. *(§7 §9 §22)*
- Snyder, J. M., & Strömberg, D. (2010). Press coverage and political accountability. *JPE*, 118(2), 355-408. *(§37)*
- Solomon, D. H. (2012). Selective publicity and stock prices. *RFS*, 25(8), 3306-3322. *(§5)*
- Sun, L., & Abraham, S. (2021). Estimating dynamic treatment effects in event studies. *JOE*, 225(2), 175-199. *(§18)*

**T**
- Tetlock, P. C. (2007). Giving content to investor sentiment. *JF*, 62(3), 1139-1168. *(§4)*
- Tetlock, P. C. (2011). All the news that's fit to reprint. *RFS*, 24(5), 1481-1512. *(§15 §27)*
- Tetlock, P. C., Saar-Tsechansky, M., & Macskassy, S. (2008). More than words. *JF*, 63(3), 1437-1467. *(§7)*
- Törnberg, P. (2024). Best practices for text annotation with large language models. arXiv:2307.13106. *(§7 §10)*

**W**
- Westphal, J. D., & Zajac, E. J. (1994). Substance and symbolism in CEOs' long-term incentive plans. *ASQ*, 39(3), 367-390. *(§16)*
- Westphal, J. D., & Zajac, E. J. (1998). The symbolic management of stockholders. *ASQ*, 43(1), 127-153. *(§16)*
- Westphal, J. D., & Zajac, E. J. (2001). Decoupling policy from practice. *ASQ*, 46(2), 202-228. *(§18 §36)*
- Wooldridge, J. M. (2010). *Econometric Analysis of Cross Section and Panel Data* (2nd ed.). MIT Press. *(§39)*

**Y**
- You, et al. (2018). hhx055 中文金融 LM 扩展词典 Panel C/D. *(§23)*
- 姜富伟, 李梦如, 孟令超 (2024). 调预期、防风险：央行金融稳定沟通效果研究. 《经济学（季刊）》, 24(6), 2281-2300. *(§11 §42)*

---

## 62. 第四块：Stage 31-39 Validation / Audit 输出（**不进 panel**）

**整体说明**：stage 31-39 共 16 个 audit/validation 模块均在 [`core/schemas.py::EXPECTED_NO_OUTPUT_STAGES`](../core/schemas.py#L185) 列表里——**不写 panel parquet**，只写 `data/eval_reports/*.csv` 或 `data/processed/*.csv|.parquet`，作为审稿人/复现包的支撑材料。Stata `.dta` 三件套不含这些列，但论文 Methods/Appendix 节会**引用这些 audit 报告**作为方法学正当性证据。

模块归属：3 个为 `pipeline/audit/`（v3.5.0+ 引入，39a/39c/39d/39e/39f），其余 13 个为 `news_process/validation/`。

### 62.1 整体定位
| 类别 | stage 号 | 用途 |
|---|---|---|
| 阈值敏感性 | 31, 32a, 35, 38b | 验证 production 阈值（计数/jaccard/radius/decay 半衰期）的选择不影响结论 |
| LLM vs 人工 | 32, 33 | LLM 标注质量 + 三模型一致率 + 与人工 gold standard 比较 |
| Tone 三角验证 | 34 | 5 词典 × 5 BERT × LLM 的 cross-method 收敛/区分效度 |
| Placebo | 36, 38a, 39 | 实体屏蔽 / 时间错位 / prompt 改写 → 平行趋势 + 测量稳健性 |
| 字典覆盖 | 37 | 5 词典 precision / coverage / stability 三维诊断 |
| 媒体多样性 | 38 | 11 维度 HHI / Shannon / Gini 跨 stage 媒体集中度 |
| 双轨 inter-track | 39a | full vs ctx Cohen κ 三维度（locus/subst/collab）|
| 三维 NMI | 39c | v3.5.0 D3 三维 normalized mutual information |
| HTMT discriminant | 39d, 39e | v3.5.1/v3.5.2 词典与 LLM 构念区分效度 |
| Cross-media α | 39f | 第 10 篇 paper main treatment（见 §33 AF） |

### 62.2 Stage 31: Bank/Fintech 阈值敏感性
- **入口**：[news_process/31_bank_fintech_threshold.py](../31_bank_fintech_threshold.py) → `validation/threshold.py`（628 行）
- **学术目的**：Loughran & McDonald (2011 JF) 分类阈值敏感性。`min_name_occurrences ∈ {1..10}` × `min_distinct_keywords ∈ {1..10}` 网格搜索，验证 production 阈值 (=3) 的稳健性。
- **输出**：`data/eval_reports/threshold_sensitivity_bank.csv` + `threshold_sensitivity_fintech.csv`
- **核心列**：`threshold` / `count` / `ratio` / `estimated_total` / `is_current`
- **gate**：stage 12 验证；论文 Online Appendix §C.1

### 62.3 Stage 32: LLM vs 人工双任务验证样本
- **入口**：[news_process/32_news_llms_human.py](../32_news_llms_human.py) → `validation/llms_human.py`
- **学术目的**：生成 500 条样本 Excel 工作台（编码者 A/B 双盲二维：真伪性 + 情感），与 Carlson & Burbano (2026, SMJ) LLM 注释透明度对标。
- **输出**：`32_news_llms_human_samples.xlsx`（含数据验证约束）
- **核心列**：`标题` / `内容` / `llm_verdict` / `编码者A_验证` / `编码者A_情感` / `编码者B_验证` / `编码者B_情感`
- **gate**：stage 33 输入依赖；P1 paper Methods §3.2 (Cao et al. 2025 投票 protocol)

### 62.4 Stage 32a: Dedup Jaccard 阈值敏感性
- **入口**：[news_process/32a_dedup_threshold_sensitivity.py](../32a_dedup_threshold_sensitivity.py) → `validation/dedup_threshold.py`（187 行）
- **学术目的**：Broder (1997 SEQUEN) MinHash LSH Jaccard 相似度敏感性，阈值 ∈ {0.75, 0.80, 0.85, 0.90}，验证 production 阈值 (=0.85) 的稳健性。
- **输出**：`data/eval_reports/dedup_sensitivity_report.csv`
- **核心列**：`Threshold` / `Retained` / `Dropped` / `Retained_Ratio` / `Is_Production`
- **gate**：论文 Appendix §D.2；无 Stata 消费（纯诊断）

### 62.5 Stage 33: LLM 投票一致性评估
- **入口**：[news_process/33_news_llms_evaluation.py](../33_news_llms_evaluation.py) → `validation/llms_evaluation.py`（1627 行）
- **学术目的**：Krippendorff (2018) Cohen κ ≥ 0.80 + Krippendorff α + McNemar 检验（规则 vs LLM 分类器）+ Carlson & Burbano (2026) 误分类系统相关性诊断。
- **输出**：`eval_reports/per_model_*.csv` + `cm_innovation_*.png`（混淆矩阵）
- **核心列**：`model` / `precision` / `recall` / `f1_score` / `kappa` / `alpha` / `mcnemar_pval`
- **gate**：P1/P3 paper Methods §3.2 + Appendix §C.3；LLM verification gate

### 62.6 Stage 34: Tone 三角验证（词典 / BERT / LLM）
- **入口**：[news_process/34_tone_validation.py](../34_tone_validation.py) → `validation/tone_validation.py`（1930+ 行）
- **学术目的**：Loughran & McDonald (2016 JAR 54(4)) 5 词典 + 5 BERT + LLM 的 Spearman ρ 相关矩阵 + Cronbach α ≥ 0.70 + 标签多数投票一致性 + Chiu & Hung (2025) Dirichlet 不确定性。
- **输出**：`34_tone_validation_cross_method.csv` + `34_tone_labels_consistency.csv` + `34_cronbach_alpha.csv`
- **核心列**：`method_pair` / `spearman_rho` / `pval` / `cronbach_alpha` / `agreement_rate` / `locus`
- **gate**：P1/P3 paper Appendix §B.1 tone validation；stage 40 panel 列验收门控

### 62.7 Stage 35: Entity Context Radius 敏感性
- **入口**：[news_process/35_radius_sensitivity.py](../35_radius_sensitivity.py) → `validation/radius_sensitivity.py`（687 行）
- **学术目的**：Hassan et al. (2019 QJE) proximity-based attribution：`sentence_radius ∈ {0, 1, 2, 3}` 阈值下词典情感得分 Spearman ρ + 标签一致性 (Cohen κ)。
- **输出**：`data/eval_reports/radius_sensitivity_full.json` + `radius_sensitivity_labels_consistency.csv`
- **核心列**：`radius` / `mean_score` / `std_score` / `label_agreement` / `kappa_vs_radius0` / `spearman_rho`
- **gate**：论文 Appendix §D.3；无强制 Stata 消费

### 62.8 Stage 36: 实体屏蔽 Placebo（双轨）
- **入口**：[news_process/36_entity_masking_test.py](../36_entity_masking_test.py) → `validation/entity_masking.py`（700+ 行）
- **学术目的**：SSRN-4558295 §7.2 银行名 → 匿名占位符替换后 LLM 重判（full + ctx 双轨），验证判定**非实体先验驱动**（Landis & Koch κ ≥ 0.81）。
- **输出**：`eval_reports/entity_masking_results.json` + `entity_masking_detail.csv` + `entity_masking_confusion.png`
- **核心列**：`article_id` / `baseline_locus` / `masked_locus` / `agreement` / `kappa_full` / `kappa_ctx` / `residual_entities`
- **gate**：P1 paper Appendix §E.2（placebo robustness check）

### 62.9 Stage 37: Fintech 词典覆盖率审计
- **入口**：[news_process/37_dict_coverage_audit.py](../37_dict_coverage_audit.py) → `validation/dict_coverage.py`（950+ 行）
- **学术目的**：Sautner et al. (2023 JF) 词典 precision (边际通过率) + coverage (关键词遗漏) + stability (时间衰减) 三维诊断，自动化评估词典系统性盲区。
- **输出**：`eval_reports/37_dict_precision_stability.csv` + `37_dict_coverage_*.csv`（多工作表）
- **核心列**：`keyword` / `occurrence_count` / `verified_rate` / `precision_95ci` / `trend_slope` / `coverage_gap` / `enk_score`
- **gate**：论文 Appendix §D.1；E-NEW-1 disclosure（Sautner 词典覆盖盲区估计）

### 62.10 Stage 38: 媒体多样性审计
- **入口**：[news_process/38_media_diversity.py](../38_media_diversity.py) → `validation/media_diversity.py`（1100+ 行）
- **学术目的**：Herfindahl (1950) HHI / Shannon (1948) 熵 / Pielou (1966) 均匀度 / Gini (1912) / Bushee et al. (2010 JAR) ENM (Laakso 1979) 跨 11 个 stage 的媒体多样性诊断。
- **输出**：`eval_reports/38_media_diversity.xlsx`（11 工作表含地域 / 名称 / 层级 / 长尾 / 时序 / 权重）
- **核心列**：`stage` / `hhi` / `entropy` / `gini` / `pielou_j` / `effective_n` / `coverage_rate` / `concentration_top10`
- **gate**：论文 Appendix §D.5；纯诊断不进 Stata

### 62.11 Stage 38a: Temporal Masking 前视偏误 Placebo
- **入口**：[news_process/38a_temporal_mask_test.py](../38a_temporal_mask_test.py) → `validation/temporal_mask.py`（190 行）
- **学术目的**：Tetlock et al. (2008 JF §4.2) 逐步掩码最新 N 年新闻，验证 bank-year 面板统计量稳定性（系数变化 < 20% 阈值）。
- **输出**：`eval_reports/temporal_mask_diagnostics.csv`
- **核心列**：`mask_window` / `llm_vote_mean` / `llm_vote_std` / `coefficient_change_pct` / `stability_pass`
- **gate**：论文 Appendix §E.1；单行 Stata 消费（稳定性确认）

### 62.12 Stage 38b: Herd Decay 半衰期敏感性
- **入口**：[news_process/38b_decay_sensitivity.py](../38b_decay_sensitivity.py) → `validation/decay_sensitivity.py`（785 行）
- **学术目的**：Sautner et al. (2023 JF §2.2) + Hassan et al. (2019 QJE) — uniform vs inverse vs exponential (λ=0.5) 距离衰减权重对词典情感得分的 Pearson/Spearman ρ 稳健性。
- **输出**：`eval_reports/38b_decay_sensitivity.csv`
- **核心列**：`dictionary` / `decay_function` / `mean_score` / `pearson_vs_uniform` / `spearman_vs_uniform` / `pval`
- **gate**：论文 Appendix §D.4；无 Stata 消费

### 62.13 Stage 39: LLM Prompt 改写敏感性
- **入口**：[news_process/39_prompt_sensitivity.py](../39_prompt_sensitivity.py) → `validation/prompt_sensitivity.py`（1220+ 行）
- **学术目的**：Carlson & Burbano (2026 SMJ §3.5) 4 prompt 变体（V1 角色 / V2 结构 / V3 精简 / V4 改写）在 full + ctx 双轨上的 Cohen κ + 标签一致性，量化 LLM 判定对措辞敏感性。
- **输出**：`eval_reports/prompt_sensitivity_results.json` + `prompt_sensitivity_detail.csv` + `prompt_sensitivity_heatmap.png`
- **核心列**：`variant` / `track` / `innovation_locus_kappa` / `innovation_substantiveness_kappa` / `label_agreement_rate` / `variant_effect_size`
- **gate**：P1 paper Appendix §E.3（LLM robustness）；Stata 单行验证

### 62.14 Stage 39a: Inter-Track Cohen κ（full vs ctx）
- **入口**：[news_process/39a_inter_track_kappa.py](../39a_inter_track_kappa.py) → `pipeline/audit/inter_track_kappa.py`（199 行）
- **学术目的**：Cohen (1960 EPM) + Landis & Koch (1977) — dual-track κ ∈ [0.50, 0.70] 预期区间（Gomber 2018 + W&Z 1994 框架），innovation_locus / innovation_substantiveness / innovation_collab_mode 三维度。bootstrap CI (n_boot=1000, 95%)。
- **输出**：`eval_reports/inter_track_kappa_table.csv`
- **核心列**：`field` / `kappa_point` / `ci_95_low` / `ci_95_high` / `n_obs` / `threshold` / `passes_threshold`
- **gate**：P1 paper Appendix §A.1；Stata 模板 [`20_tableA1_inter_track_kappa.do.tmpl`](../papers/_common/stata_templates/20_tableA1_inter_track_kappa.do.tmpl) 消费

### 62.15 Stage 39c: 三维构念正交性 NMI
- **入口**：[news_process/39c_construct_orthogonality.py](../39c_construct_orthogonality.py) → `pipeline/audit/construct_orthogonality.py`（370+ 行）
- **学术目的**：Vinh, Epps & Bailey (2010 JMLR) normalized mutual information (NMI) 3×3 矩阵（substantiveness × locus × collab_mode full+ctx 各组），permutation 1000-rep null distribution（Z > 2.58 → weak discriminant）。v3.5.0 D3 增量。
- **输出**：`data/processed/39c_nmi_point.parquet` + `39c_nmi_*.parquet`（6 文件）+ `39c_nmi_null_p95.parquet` / `39c_nmi_null_p99.parquet`
- **核心列**：`dim1` / `dim2` / `nmi_point` / `nmi_ci_low` / `nmi_ci_high` / `z_score` / `pval` / `sample_n`
- **gate**：v3.5.0 D3 释放门控；P3 paper Appendix §A.2（construct validity 证据）

### 62.16 Stage 39d: Lexical Discriminant Validity（v3.5.1 A1）
- **入口**：[news_process/39d_lexical_discriminant_validity.py](../39d_lexical_discriminant_validity.py) → `pipeline/audit/lexical_discriminant_validity.py`（324 行）
- **学术目的**：Henseler, Ringle & Sarstedt (2015 JAMS) HTMT dual cutoff（strict 0.85 / lenient 0.90）+ Fornell & Larcker (1981 JMR) φ² + Cohen (1960) κ + Cronbach (1951) α，A1 clarity vs LLM substance 的 3×3 discriminant validity matrix（pairwise on-disk OOM-safe，seed=42）。
- **输出**：`eval_reports/39d_lexical_htmt_matrix.csv` + `39d_ave_*.csv` + `39d_kappa.csv` + `39d_cronbach_alpha.csv` + `data/processed/39d_htmt.parquet`
- **核心列**：`indicator_pair` / `htmt_value` / `htmt_strict_pass` / `ave_clarity` / `ave_substance` / `phi_squared` / `kappa` / `cronbach_alpha` / `permutation_pval`
- **gate**：v3.5.1 A1 释放门控；P3 paper Methods §3.4（lexical clarity 与 numerical intensity HTMT 验证）

### 62.17 Stage 39e: LM 子词典判别效度（v3.5.2 A1）
- **入口**：[news_process/39e_lm_discriminant_validity.py](../39e_lm_discriminant_validity.py) → `pipeline/audit/lm_discriminant_validity.py`（240+ 行）
- **学术目的**：Henseler et al. (2015 JAMS) HTMT (0.85/0.90 dual cutoff) + Cohen κ + Cronbach α，LM 4 子词典（uncert_frac / litig_frac / constr_frac / modal_strong_frac）vs v3.5.1 clarity / num_intensity 的 6×6 panel-level discriminant validity（panel HTMT < 0.85 on 9000 bank-year，PR #14 gate G-A1.2）。
- **输出**：`eval_reports/39e_lm_htmt_matrix_ctx.csv` + `39e_lm_kappa_ctx.csv` + `39e_lm_cronbach_alpha_ctx.csv` + `39e_lm_permutation_ctx.csv`
- **核心列**：`indicator1` / `indicator2` / `htmt_ctx` / `kappa_ctx` / `cronbach_alpha_ctx` / `p95_perm` / `p99_perm` / `passes_strict`
- **gate**：v3.5.2 PR #4/14 释放门控；P3 paper Appendix §A.3（LM construct validity）；Stata 不消费（panel-only 诊断）

### 62.18 整合：16 stage 集体作为论文 Methods 附录支撑

```
论文 Methods/Appendix 引用关系（典型 P3 = substantiveness paper）:
─────────────────────────────────────────────────────────
Methods §3.2  LLM 投票 protocol  → §62.5 stage 33 (Cohen κ + McNemar)
Methods §3.3  实体屏蔽稳健性    → §62.8 stage 36 (placebo κ ≥ 0.81)
Methods §3.4  Discriminant validity → §62.16 stage 39d + §62.17 39e (HTMT < 0.85)
Methods §3.5  Construct validity  → §62.15 stage 39c (NMI Z < 2.58)
Methods §3.6  Inter-track κ      → §62.14 stage 39a (κ ∈ [0.50, 0.70])

Appendix §B.1  Tone 三角验证     → §62.6 stage 34 (5 dict × 5 BERT × LLM)
Appendix §C.1  阈值敏感性        → §62.2 stage 31
Appendix §D.1  词典覆盖率        → §62.9 stage 37
Appendix §D.2  Dedup 阈值        → §62.4 stage 32a
Appendix §D.3  Radius 敏感性     → §62.7 stage 35
Appendix §D.4  Decay 半衰期      → §62.12 stage 38b
Appendix §D.5  媒体多样性        → §62.10 stage 38
Appendix §E.1  时间错位 placebo  → §62.11 stage 38a
Appendix §E.2  实体屏蔽 placebo  → §62.8 stage 36
Appendix §E.3  Prompt 改写       → §62.13 stage 39
```

每个 stage 的 csv/json 都是**审稿人可独立打开核验**的客观证据。论文复现包（[stata_runner build-replication](../papers/_common/stata_runner.py)）会自动把这些 eval_reports/ 子树打包。

### 62.19 内部 / 辅助 audit 模块（未在主 DAG，无独立 stage 号）

以下 3 个模块存在于 `pipeline/audit/` 但未在 `STAGES_VALIDATION` 注册——它们是**辅助工具**，由其他 stage 调用或用户手动触发：

| 模块 | 用途 | 触发 |
|---|---|---|
| [`pipeline/audit/stata_audit.py`](../pipeline/audit/stata_audit.py) | Stata 导出层后处理审计：核对 `46_panel_yearly_full.dta` 的列数 / 类型 / value labels 与 `codebook.xlsx` 一致性；写 `52_stata_data_audit.log`。 | thin shim `52_stata_data_audit.py`；用户手动跑 `python news_process/52_stata_data_audit.py` |
| [`pipeline/audit/stats_excel.py`](../pipeline/audit/stats_excel.py) | 把 panel 所有列的描述性统计（n / mean / std / min / p25 / median / p75 / max / NaN 比例）汇总到 `53_panel_stats.xlsx`。 | thin shim `53_export_stats_excel.py` |
| [`pipeline/audit/llm_contamination_test.py`](../pipeline/audit/llm_contamination_test.py) | LLM 训练数据污染检测：抽样测试 LLM 是否"记得"训练截止日期后的银行新闻（pre-training contamination）。锚定 OpenAI 2023 data cutoff disclosure。 | 用户手动；论文 Appendix §E.4 引用 |

### 62.20 Preprocess 子模块（stage 00 的 5 个组件）

`pipeline/preprocess/` 包含 5 个**子模块**，统一通过 stage 00 (`00_preprocessing.py`) 调用，不单独出 parquet：

| 模块 | 职责 |
|---|---|
| [`preprocess/runner.py`](../pipeline/preprocess/runner.py) | stage 00 编排器 |
| [`preprocess/load.py`](../pipeline/preprocess/load.py) | 加载 `data/raw/*.xlsx` → DataFrame |
| [`preprocess/normalize.py`](../pipeline/preprocess/normalize.py) | 日期格式 / 标题文本 / 媒体名标准化 |
| [`preprocess/filter.py`](../pipeline/preprocess/filter.py) | 长度过滤 / 重复 URL 过滤 / 黑名单 |
| [`preprocess/dedup.py`](../pipeline/preprocess/dedup.py) | dedup 主算法（MinHash LSH jaccard ≥ 0.85）；与 stage 32a sensitivity 联动 |
| [`preprocess/_constants.py`](../pipeline/preprocess/_constants.py) | 路径 / 阈值常量（避免散布到各模块） |

合并产出 `00_preprocessing.parquet`（参 §C 新闻覆盖列的源头）。

### 62.21 DC3 LLM Archive（v3.7.0，**无列产出**）

| 模块 | 职责 |
|---|---|
| [`pipeline/llm_archive/archive.py`](../pipeline/llm_archive/archive.py) | `archive_record(...)` append-only JSONL 写入；每次 LLM 调用记录 prompt / response / model_version / timestamp |
| [`pipeline/llm_archive/manifest.py`](../pipeline/llm_archive/manifest.py) | SHA-256 manifest 维护，确保 `data/llm_archive/responses/*.jsonl` 防篡改 |

**用途**：顶刊 reproducibility 硬约束——即使 GPT-5.4→5.5 升级使在线推断无法重现，研究者仍可从 archive JSONL 复现历史所有 LLM 决策。V4 F-P2.1 critical 修复。`.gitattributes` 配置 Git LFS（~5GB 预估）。

接入点：[stage 21 tone_llms.py](../pipeline/sentiment/tone_llms.py) + [stage 34 tone_validation.py](../validation/tone_validation.py) + [stage 36 entity_masking.py](../validation/entity_masking.py) + [stage 39 prompt_sensitivity.py](../validation/prompt_sensitivity.py) + [stage 48 llm_peer_iv.py](../pipeline/panel/llm_peer_iv.py) + [stage 19 executive_ner.py](../pipeline/sentiment/executive_ner.py)（**6 处接入**）。失败不阻塞 pipeline（graceful skip）。

---

## 61. 修订日志

### v1.5 (2026-05-19, 终版最高标准全面评审) ✅ **发布就绪**

最后一次系统性评审，6 项检查全部通过，0 个 critical bug。修复 4 处 minor 遗漏后定版。

**评审范围**（最高标准全面核验）：
1. ✓ **file:line 引用准确性** —— 抽样 20+ 处 `[module.py:NNN](../path#LNNN)` 引用，全部在 ±3 行误差内
2. ⚠ **Stata 模板真实存在性** —— Glob 实测发现 catalog §58 写的模板名（`10_descriptives.do` / `30_main_regression.do` / `40_robustness.do` / `50_appendix.do`）**与实际不符**——本次修复为 14 个真实 .do.tmpl 完整清单
3. ✓ **OUTPUT_REGISTRY 全覆盖** —— `core/schemas.py::OUTPUT_REGISTRY` 22 个 (stage, parquet) 条目全部在 catalog 有专节
4. ⚠ **pipeline 模块全覆盖** —— Glob 发现 5 类辅助模块未提及：`audit/{stata_audit, stats_excel, llm_contamination_test}` + `preprocess/{filter, dedup, load, normalize, _constants, runner}` + `llm_archive/{archive, manifest}`——本次新增 §62.19 + §62.20 + §62.21 三个小节补全
5. ✓ **逻辑一致性** —— LLM 模型名 (`gpt54nano/gemini31111/deepseekv4`) / 三维编码方向 (0=baseline/1=对照) / outcome 列名 (`z_score`/`npl_formation_rate`/`rwa_to_ta_ratio`) 在所有引用处一致
6. ✓ **承诺实现完整** —— §59 笛卡尔积模板 + §60 参考文献抽样 10 篇全部能找到对应

**v1.5 具体修订**（4 minor fixes）：

| # | 章节 | 问题 | 修复 |
|---|---|---|---|
| 1 | §58 附录 A Stata 模板清单 | 写了 `10_descriptives.do / 30_main_regression.do / 40_robustness.do / 50_appendix.do` 等不存在的模板名 | 替换为 14 个 Glob 实测的真实 `.do.tmpl`（含 paper-specific 用途说明）：`00_master / 01_data_prep / 10_table1_descriptives / 11_table2_main_m1m6 / 12_table3_mechanism / 13_table4_heterogeneity / 14_table5_advanced_robustness / 20_tableA1_inter_track_kappa / 21_tableA2_main_spec_switch / 22_tableA3_bartik_iv / 23_tableA4_radius_sensitivity / 24_tableA5_dictionary_method / 30_figure1_event_study / 31_figure_coefplot_dual` |
| 2 | §62.19 新增 | `pipeline/audit/stata_audit.py` / `stats_excel.py` / `llm_contamination_test.py` 未提及 | 新增 §62.19 "内部 / 辅助 audit 模块"——明确：(a) `stata_audit.py` = stage 52 thin shim 调用，core/dta 一致性检查；(b) `stats_excel.py` = stage 53 描述性统计 Excel 导出；(c) `llm_contamination_test.py` = LLM 训练数据污染检测（论文 Appendix §E.4） |
| 3 | §62.20 新增 | `pipeline/preprocess/` 5 个子模块（load/normalize/filter/dedup/runner/_constants）未提及 | 新增 §62.20 "Preprocess 子模块"——说明 stage 00 由 5 个组件组成，dedup 主算法与 stage 32a sensitivity 联动 |
| 4 | §62.21 新增 | `pipeline/llm_archive/archive.py` + `manifest.py` 提及但缺细节 | 新增 §62.21 "DC3 LLM Archive"——完整说明 append-only JSONL + SHA-256 manifest 顶刊 reproducibility 框架；列出 6 处 stage 接入点；Git LFS 配置 |

**未修复但已记录的合理限制**：
- BERTopic K 是 runtime 动态发现（v1.2 已记录 §31）
- attention_media `bal_{w}_*` 是按 `_SCORE_PATTERNS` 动态匹配 + 32 字符截断（v1.3 已记录 §46.4）
- 这两类列名只有运行 stage 17 / stage 45 后才能 enumerate 到 `46_panel_yearly_codebook.xlsx`

**发布就绪结论**：

✅ **catalog v1.5 已达顶刊复现包级别的方法学说明书标准**：
- **指标层**：1700+ 列字面清单 + 笛卡尔积模板（v1.0-v1.3）
- **解读层**：8 个核心指标的经济学/计量学深度（v1.4 A）
- **使用层**：Stata 主回归 + 稳健性 + 异质性代码示例（v1.4 A）
- **验证层**：16 个 audit/validation stage + 4 个辅助 audit 模块 + DC3 archive 框架（v1.4 B + v1.5）
- **复现层**：14 真实 Stata 模板路径 + replication 包结构（v1.5）

可用于：
- 论文 Methods / Appendix 节直接引用（"详见 catalog §X"）
- 审稿人 / 复现包接收方独立核验每一列
- 新开发者 onboarding 单一权威文档
- LLM 辅助分析时的精确上下文注入

无 critical bugs。建议直接 commit + 作为 v3.7.0 文档主权威。

### v1.4 (2026-05-19, 第四轮评审 — 深度增强 + audit 章节)

**两件大事并行**：

**(A) 深度增强 — 为 8 个核心指标章节加"内在含义解读"段**（~3000 字新增内容）：
1. **§7.4 LLM 投票主指标**：经济学解读（informational tone vs 简单情感）+ 三模型投票防系统偏差 + 三主列关系表（vote_tone/cont/prob_score 各自适用场景）+ 双轨选择逻辑（v3.6.0 G3 起 _ctx 为 main）+ 典型 Stata spec + 4 个常见陷阱
2. **§16.4 创新三维**：为什么是三维而非一维 + 双轨独立的 entity-proximity 理由 + 编码方向 0=baseline / 1=对照 的统计意义 + 置信度列子样本 robustness 用法 + P3 paper main spec 完整代码 + 3 个陷阱（measurement-treatment mismatch / 稀疏 cell NaN / baseline cell 1）
3. **§21.1 Tone Gap**：3 个核心 gap 的论文映射表 + 经济学符号预期（W&Z 1998 decoupling 框架）+ `min ≥ 5` 门控的统计意义 + 异质性回归示例 + 3 个陷阱（样本量披露 / 方向误读 / 不要平均双轨）
4. **§22.4 洗稿率**：核心定义 `WR = Pr(symb | pos)` + 10 方法变体的统计意义（reliability/method/deep-model/measurement-quality/continuous）+ Romano-Wolf 多重稳健性 + 反向验证 `washing_asymmetry` 概念 + 分母 0 处理
5. **§35.1 benefit_society**：与一般 sentiment 的正交性 + 双极锚点几何直觉 + 4 列论文用法表 + Jha-Liu-Manela 2026 RFS 复现注意 + 与 substantiveness 区别（"对经营有利" ≠ "真做"）+ SBERT 模型 hash 冻结要求
6. **§37.9 Bartik IV**：因果识别需求（反向因果 reverse causality）+ Goldsmith-Pinkham 2020 AER 外生性公理 + 基期 T0 强制 < 2019 的政治经济学原因 + Romano-Wolf 校正必要性 + Rotemberg 权重诊断完整解读 + 6 IV 联合 spec + Stata `bartik_weight` 包用法
7. **§38.5 政策冲击 DID**：staggered DID vs 传统 DID（Goodman-Bacon 2021）+ Callaway-Sant'Anna (2021 JOE) ATT(g, t) + 为什么用 lead/lag dummy 而非线性 rel_year + 平行趋势检验完整流程 + Cramér's V 多政策正交性诊断 + DDD 三重差分用法
8. **§54.4 风险承担 outcome**：4 个 outcome 的因果链解读（fintech tone → 战略 → 风险）+ `implicit_guarantee_tier` Acharya-Anginer-Warburton 2016 RFS moral hazard 框架 + LLP discretion BW 2012 残差化两阶段流程 + 3 个陷阱（fallback 三级 / 季度→年度规则 / `z_score` vs `zscore` 命名）

**(B) 第四轮新增 §62 Stage 31-39 Validation/Audit 章节**（约 1500 字 + 1 个综合映射表）：
- 整体定位表 + 10 类用途分类
- 16 个 stage 逐个：入口（thin shim + pipeline 模块 + 行数）/ 学术目的（含主要文献）/ 输出文件路径 / 核心 audit report 列名 / 可用性 gate（哪个 paper / Stata 模板消费）
- §62.18 整合映射表：典型 P3 paper Methods/Appendix 各节 → 对应 audit stage 的引用关系
- 明示这些 stage 在 `EXPECTED_NO_OUTPUT_STAGES` 列表，**不写 panel parquet**，只产 `eval_reports/*.csv|json|parquet`
- 复现包打包说明：`stata_runner build-replication` 会自动把 eval_reports/ 子树纳入

**结论**：v1.4 是 catalog 的**信息密度跃迁**。前 3 轮主要是**列名穷尽枚举**（"它叫什么"），v1.4 增加了**经济学/计量学解读**（"它度量什么、为何重要、如何使用、有哪些陷阱"），并补全了 audit 层（"如何向审稿人证明"）。文档从"指标字典"演进为"**指标 + 解读 + 使用 + 验证**"四位一体的方法学手册。

### v1.3 (2026-05-19, 第三轮评审 — 残余盲点)

第三轮聚焦 v1.2 标注的 3 项未深入处理 + paper 端关系。新增 3 个 bis 小节 + 修正 stage 22 中间列定性。

**新增小节**：
1. **§24bis 中间篇章列**（stage 22 的 LM/FLS/clarity/numerical_intensity 篇章级 `n_definite` / `n_uncert` / `n_litig` / `n_constr` / `n_modal_strong` / `n_sentences` / `n_fls_sentences` 等计数列）——明示**不进 panel**，仅在 encode_collab.py 聚合时消费。研究者若要篇章级分析，可读 `22_words_tone.parquet` 中间层。
2. **§34bis benefit_society Sibling 模块**——明示 `benefit_society_alt_anchor` / `_placebo` / `_audit_combined` 三个模块**完全独立**于主 DAG，不在 `STAGES_MAIN` / `STAGES_VALIDATION` 注册；由 thin shim `27c_placebo_and_alt_anchor.py` 手动触发，产出独立 `27c_alt_anchor_and_placebo_panel.parquet`（约 80 列：5 锚点族 × 4 stat × 2 track + 5 业务线 placebo × 4 stat × 2 track）；下游 Stata 模板 P2.S1 + P2.A2 消费；Stata 端调用示例。
3. **§57bis 9 paper-specific 模块对 panel 的关系**——明示**全部 9 paper 是纯消费层**，不写回 stage 46 .dta；统一调用链 `analysis.py → run_main_pipeline → tables → figures`；13 个 `papers/_common/` 共享工具模块完整职责清单（panel_loader/paper_config/registry/pipeline_runner/stata_runner/postprocess/tables/figures/stats/derivative_replication/git_utils）；Stata 复现包结构（14 主模板 + 8 paper-specific 子目录）。

**结论**：v1.3 完成对**整条 panel 数据流**的字面列完整覆盖：
- 上游 stage 00-19 篇章级 → §C / §11 / §28-34
- Stage 21-24 sentiment → §F-K / §22-26
- Stage 30-39 audit/embedding → §AF / §AR
- Stage 41-46 panel 聚合 → §A-AC / §AS-AZ
- Stage 49 outcome → §BA
- Stage 51 falsification → §BB
- Sibling audit (27c) → §34bis（独立）
- Paper 端 → §57bis（消费层，不入 panel）

**仍是动态值（runtime 才能定）**：
- BERTopic K（HDBSCAN auto-discover，预期 15-30）→ `frac_topic_{0..K-1}_{full,ctx}` 列数运行时才知
- attention_media `compute_balanced_media_robustness` 每窗 ~30+ 列由 `_SCORE_PATTERNS` 动态匹配（受 32 字符截断）

这些在 catalog 中以模板形式列出，运行 stage 17 / stage 45 后用户可在 `46_panel_yearly_codebook.xlsx` 反查精确列名。

### v1.2 (2026-05-19, 第二轮评审 + 丰富 — stage 上游列)

第一轮主要修了 panel 后端聚合 + IV/网络。第二轮 focus 上游 stage 数据生产模块（17/18/19/24/30/33/51 等）的真实输出列字面：

**重大补全**：
1. **§7/§8/§12 方法学三套模型名实证**（§1.2(d)）：从 `config/sentiment.yaml` 实证 LLM `{gpt54nano (GPT-5.4-nano), gemini31111 (Gemini-3.1.1.1.1), deepseekv4 (DeepSeek V4，原 claude4h 重命名)}` + 5 BERT 模型分类数（3-class / 2-class 区分）。
2. **§27 Herd Decay**：补全算法参数（`SIMILARITY_THRESHOLD=0.35` / `TIME_WINDOW_DAYS=7` / `max_features=10000` / `char_wb ngram(2,4)`）；补 `n_similar_articles_{full,ctx}` 篇章列；明确 v3.5.x legacy `herd_weight` 已删除 + 触发 WARN 机制。
3. **§30 EPU**：补完整 schema（`year:int, month:int, epu:float`）+ 数据源路径 `data/external/epu_china_monthly_2007_2024.csv`；3 级 graceful fallback（文件缺失 → 全 NaN；schema 缺列 → error + 全 NaN；缺 date 列 → year-only fallback）；D-0 实测项（policyuncertainty.com 实际止于 2022？）。
4. **§31 BERTopic 主题**：实证 **K 是 HDBSCAN 自动发现**（`min_cluster_size=5000`，400k 文章 → 预期 K ≈ 15-30，runtime 决定，写入 `17_topic_metadata.json`）；明确 `frac_topic_{0..K-1}_{full,ctx}` 命名（不是占位 `frac_topic_k_*`）；补**双轨零 K-drift 机制**（ctx 用 `.transform()` 复用 full 已 fit 的 topic_model）；补 UMAP 固定 `random_state=42` + CountVectorizer `cn_tokenize`；补 3 个 parquet（`17_article_topics` / `17_topic_info` / `17_topic_panel`）；学术锚定 Bybee 2024 RFS + Hansen 2018 QJE + Grootendorst 2022。
5. **§32 Staleness**：补算法参数（`WINDOW_DAYS=7` / `SHINGLE_SIZE=3` / `num_perm=128`）；明确 surface (MinHashLSHForest, S1.3 修后 ~50000× 加速) + semantic (Faiss IVFFlat + SBERT) 两套独立算法；明确 bank-year 聚合**只产 mean 不产 std/max/median**；补 D-0 实测项（`corr(surface, semantic) ∈ [0.3, 0.7]` 互补 ≠ 冗余）；新增 `staleness_corr` 诊断量（不进 panel）。
6. **§33 Cross-Media α**：补事件检测算法（`p90 文章数` + `±3 days` 窗口 + `MIN_OUTLETS=2`）；明确 S2.3 修复（双数据结构：`outlet_tones` 1D for variance + `daily_matrix` 2D for α）；与第 10 篇 paper 协调约束。
7. **§34 LLM CEO NER**：补完整 prompt 模板 + 9 类高管职位枚举；明确 DC3 archive 接入机制（append-only JSONL + SHA-256 manifest）；显式标注 `ceo_volatility` / `ceo_succession_event` / `exec_replacement_rate` **未实现**；准入门控 precision ≥ 0.85, recall ≥ 0.75 + 200 篇 gold standard。
8. **§55 Falsification**（重写）：从原占位描述改为字面 21 列完整清单——9 个非 fintech 对照变量（`nf_n_articles` / `nf_ln_coverage` / `nf_media_breadth` / `nf_headline_frac` / `all_n_articles` / `all_ln_coverage` / `fintech_share` / `ln_ft_articles` / `ln_nf_articles`）+ 12 个 placebo DID（`{dcep,sandbox}_placebo{1,2,3}_{post,did}`，Bertrand-Duflo-Mullainathan 2004 QJE 平行趋势检验）；列数核算（46 全 2024 + 21 衍生 ≈ 2045，与实测 2033 偏差源自跳过空政策）；v6/F3 NaN 保留约定。

**验证已正确（无需改动）**：
- §11 stage 11 篇章列（`target_bank_in_title` / `target_bank_mention_count` / `mention_density` / `doc_length` / `co_mentioned_banks`）
- §29 stage 14 双轨 + legacy alias
- §34 CEO NER 6 列就是全部（无 ceo_volatility 等）
- §54 risk_taking_outcomes 11 列 OUTPUT_OUTCOME_COLS

**v1.2 仍未深入处理**：
- stage 22 中间临时列（如 LM 子词典的 `*_count` 变体）是否进 panel —— 需要等 stage 22 实际跑出 parquet 后再核验
- attention_media `compute_balanced_media_robustness` 动态发现的 50+ 全方法列具体枚举
- benefit_society 的 `_alt_anchor` / `_placebo` / `_audit_combined` 3 个 sibling features 模块是否有衍生列进 panel（看 runner.py 似乎没接入）

### v1.1 (2026-05-19, 第一轮评审 + 丰富)
基于 Explore agent 跨源代码核验报告 + 直接源代码细读做的修订：

**重大修订**：
1. **§37 Bartik IV**：补全 share 列名（`bartik_{group}_share_{value}`，共 23 列 share）；明示 6 类 group 的精确字典 `{soe, joint, city, rural, policy} / {L, M, S, XS} / {tech, app} × 2 套（lf/lc）/ {fin, comp, other} / {high, mid, low} / {local, nonlocal}`；新增 Rotemberg 权重诊断 §37.8；修正 zone_leave1out_tone 列名（原误为 `province_news_sentiment_loo_*`）。
2. **§38 政策冲击 DID**：从 6 列扩到 12 列/政策的完整 event-study 工具集（`{prefix}_treat_year` / `_treated` / `_post` / `_rel_year` / `_lead{2,3}` / `_lag{0,1,2,3}` / `_lead4plus` / `_lag4plus`）；移除 DepIns 单独列（已在 §39.AL 中作为非 DID dummy 处理）；新增多政策正交性 Cramér's V 诊断说明 + Stata 代码示例。
3. **§46 媒体异质性**：从 8 个 tone_gap × 3 轨补到 **10 个 × 3 轨 = 30 列**（新增地理维度 `tone_gap_homeprov_otherprov_*` / `tone_gap_homecity_othercity_*`）；新增 §46.3 停刊检测（cessation_status + Heese 2022/Gao 2020 学术依据）；新增 §46.4 平衡媒体 3 个时间窗稳健性（`bal_{w0724,w1024,w1124}_tone_*` 系列 ≈ 45+ 列）；新增 §46.5 `media_hhi`。
4. **§47 地理 LOO**：修正 LOO IV 列名（`province_loo_tone_{full,ctx,title}` / `city_loo_tone_*` / `zone_leave1out_tone_*`）；4 梯度地理缓冲后缀改 `_tone` + `_n_articles`；区域模仿渗透率 6 列具体命名（`imit_press_homeprov / homecity / homezone / sametype_homeprov / sametype_homecity / sametype_homezone`）。
5. **§48 网络中心度**：从 8 列扩到 **22 列**完整清单（18 节点级 + 4 网络级），分原图组 12 + 倒数图组 4 + 衍生组 2；删除文档错误声称的"加权中心度 `_w / _mw / _hw`"（实际未实现）；新增 §48.3 网络溢出从 2 列扩到 **7 列**（一阶 `peer_tone_lag1_*` + 二阶 `peer_tone_2nd_lag1_*` + `peer_fintech_exposure_lag1`）；新增 §48.4 认知邻近度 `bank_cogn_mean`（Boschma 2005）；新增 LeSage & Pace (2009) + Bonacich (1972) + Burt (1992) + Estrada (2005) + Newman (2005) + Watts-Strogatz (1998) 引文。
6. **§49 经纪**：补充行号引用 + 修正字段（`brokerage_fire_sale = _lag1 × industry_neg_shock`）；保留中间列 `_neg_ratio` + `_lag1` 显式列出。
7. **§50 strat_diff**：从 5 列扩到 **20+ 列**（4 方法 × N ∈ {3..7} 的 N-NN + sim_max + 4 方法 centroid_diff + Product Market Fluidity 2 列 + 文本连贯性 4 方法 × 2 轨 = 8 列 + Ctx 轨同模式）；新增 Hoberg-Phillips-Prabhala (2014) + 谢佳松 (2025) + 欧阳志刚 & 胡雯华 (2024) 引文。
8. **§51 auth_sim**：从 4 列改为 **4 方法 × 2 轨 = 8 列** 完整列表（`auth_sim_{tfidf_c,tfidf_w,lda,emb}_{full,ctx}`）；删除不存在的旧名 `auth_sim_full/ctx/std/count`。
9. **§52 LLM Peer IV**：从 4 列扩到 **多阈值 3 cutoff × 3 列 = 9 列**（`llm_peer_tone_iv_full_{80,70,60}` / `llm_peer_coverage_iv_{80,70,60}` / `llm_peer_count_{80,70,60}`）+ 主阈值 3 别名 + 竞争强度 `peer_compete_idx_{80,70,60}`。
10. **§54 risk_taking_outcomes**：修正 OUTPUT_OUTCOME_COLS 11 列完整字段（重要：`z_score` 不是 `zscore`；`npl_formation_rate` 不是 `npl_formation`；`rwa_to_ta_ratio` 不是 `rwa_ratio`；新增 `writeoffs_imputed` / `sigma_roa_5y_rolling` / `bank_type_id` / `implicit_guarantee_tier`）。

**遗漏补充**：
- v6/F3 NaN 保留约定全文统一标注
- benefit_society 实际是 4 stat × 2 track = 8 列（mean/std/pos_frac/neg_frac），原已正确
- v3.5.0 D2 cell_id value labels 完整列出（baseline = cell 1 = 三维全 0）

**待下一轮**：
- BERTopic K 的实测值（待 stage 17 集成 PR 完成）
- attention_media `compute_balanced_media_robustness` 动态发现的全方法列详细枚举
- stage 51 falsification placebo 列详细枚举

---

**文档版本**：v1.5 (2026-05-19，**终版最高标准全面评审 — 发布就绪 ✅**)。0 critical bug + 4 minor fixes 已应用。
**作者**：news_process v3.7.0 pipeline 源代码 + Claude Opus 4.7 整理。
**约定**：本文档与 [stata_export.py](../pipeline/panel/stata_export.py) + [codebook.py](../pipeline/panel/codebook.py) + 各 stage 源代码同步更新；新增 stage 时按"分类 → 单列"双层结构追加；同时在 §61 修订日志登记。
