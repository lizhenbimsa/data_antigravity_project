# v3.5.2 / v2.3 Implementation Supplementation Plan

**Status**: implemented (15/16 sub-PR, 87% real-usable);
**Branch**: `v2.3-followup-v2` (Layer 7+8 文档/精度修正, 第 17 轮 user-request 重建);
**Audit rounds**: 17 (累计 95+ 痕迹; 10 P0/P1 bug 全修)
**Tests baseline**: 127/127 PR-touched fast tests green

---

## 1. 方法学传承链

```
v3.5.0 (2026-05-15) Stage 3 augmentation
  └─ D2 cell decomposition + D3 NMI orthogonality + D4 dual-track residual
v3.5.1 (2026-05-17) A1 Lexical Clarity + A3 Numerical Intensity 真双轨
  ├─ _compute_clarity_for_text + _dual_analyze 架构 (真双轨范式)
  └─ stage 39d HTMT + Cronbach α + κ + permutation seed=42
v3.6.0 (2026-05-18) Plan E execution (上游单轨缺口闭合 + main treatment _ctx)
v3.7.0 (2026-05-18) 第 10/11 篇立项 + DC3 LLM archive + stage 49
─────────────────────────────────────────────────────────────────
v2.3 (2026-05-18) 实施 — 8 项国际顶刊指标 + 集成层 + 测试 baseline
```

## 2. 顶刊文献锚定矩阵

| PR | 指标 | 顶刊文献 | 中文化挑战 |
|---|---|---|---|
| #1 | cn_text_utils | Bybee et al. (2024) RFS 37(3) | jieba 0.42.1 frozen + 200 词金融停用词 |
| #2/#3 A1 | LM 4 子词典 | Loughran-McDonald (2011) JF 66(1):35-65 | 1219 词需专家中文化, v0.1.5 实测 314 词 (uncert 83 / litig 104 / constr 76 / modal_strong 51), 14-41% 覆盖 |
| #3 A2 | Forward-Looking Statements | Li (2010) JAR 48(5):1049-1102 | 中文分句 + 双门控 (future 72 ∧ time 59 = 131 词) |
| #4 stage 39e | HTMT discriminant validity | Henseler-Ringle-Sarstedt (2015) JAMS 43(1) | 与 v3.5.1 stage 39d 互补; 1000-rep permutation seed=42 |
| #5 EPU | Baker-Bloom-Davis EPU 中国版 | Baker-Bloom-Davis (2016) QJE 131(4):1593-1636 | 中国版数据时间范围 D-0 实测 |
| #6 媒体 tier | 3 级声誉权重 | Solomon (2012) RFS 25(8); Engelberg-Parsons (2011) JF 66(1) | 央媒权威性 ≠ 信息质量 (中国语境) |
| #7 ritest | Randomization Inference | Young (2019) QJE 134(2):557-598 + MacKinnon-Webb (2020) JBES 38(3) | 84-cluster 小, RI 必需 |
| #9 SBERT | shibing624/text2vec | Bybee 2024 标题+首段策略 | 512 token 截断避坑 |
| #10 BERTopic | Narrative topic | Bybee et al. (2024) RFS; Hansen et al. (2018) QJE 133(2) | 中文 fintech topic 与美国 corpus 结构不同 |
| #11 staleness | Article 新颖度 | Tetlock (2011) RFS 24(5):1481-1512 | 中文洗稿严重 → 分布右偏 |
| #12 α | Krippendorff α | Krippendorff (2004) SAGE | 与第 10 篇 bank_media_disagreement 重叠 |
| #13 D4 NER | CEO 媒体提及 | Kaustia-Rantapuska (2016) JFM 29:1-26 | 国企管理层任命路径与美国 superstar CEO 不同 |

## 3. 真双轨架构传承 (v3.5.1 → v2.3)

**v3.5.1 A1 范式** (`_dual_analyze` in `tone_words.py`):

```python
def _dual_analyze(row):
    content_full = str(row.get('内容', ''))
    content_ctx = str(row.get('content_ctx', content_full))
    clarity_full = _compute_clarity_for_text(content_full, _def_set, _amb_set)
    clarity_ctx = _compute_clarity_for_text(content_ctx, _def_set, _amb_set)
    # ... 合并 _full / _ctx 后缀 keys
```

**v2.3 A1 LM + A2 FLS 扩展** (同 `_dual_analyze`):

```python
    # v3.5.2 PR #3 (A1 LM 4 子词典)
    lm_full = _compute_lm_non_sentiment_for_text(content_full, _lm_dicts)
    lm_ctx = _compute_lm_non_sentiment_for_text(content_ctx, _lm_dicts)
    # 4 子集 × 2 轨道 = 8 panel 列

    # v3.5.2 PR #3 (A2 FLS)
    fls_full = compute_fls_for_text(content_full)
    fls_ctx = compute_fls_for_text(content_ctx)
    # 1 metric × 2 轨道 = 2 panel 列
```

**关键**：v3.5.1 的真双轨纪律（修 R3-C2 假双轨 anti-pattern）在 v2.3 全部保留。

## 4. 10 项 bug 修复表 (第 11-14 轮自审)

| ID | 缺陷 | 修复 | 验证 |
|---|---|---|---|
| S1.1 | PR #6 caller 未接入 | `runner.py:267` 真调用 | test_runner_imports_compute_media_tier_weights |
| S1.2 | PR #3 stage 22 未集成 | `_dual_analyze` 内 LM+FLS | test_dual_analyze_emits_lm_fls_keys |
| S1.3 | PR #11 surface O(N²) | unique-day 分组 flush O(N·k) | test_algorithm_complexity_subquadratic, 720× |
| S1.4 | PR #13 NotImplementedError | `_yunwu_chat_sync` 真接入 | test_call_llm_no_api_key_graceful |
| S2.2 | PR #10 BERTopic merge type | 3 路 if/else 拆分 | import OK |
| S2.3 | PR #12 Krippendorff 1 item N raters | outlet × day matrix | test_returns_dict_with_outlet_tones_and_matrix |
| B1 | requests 不在 requirements | `requirements.txt:51-53` declare | import OK |
| B2 | get_or_compute_llm 不存在 | 改用 `LLMCache` 类 | test_call_llm_no_api_key_graceful |
| C1 | epu_merge 显式 path 不存在未退化 | `Path.exists()` 检查 | test_missing_file_returns_empty |
| C2 | 媒体双归属优先级未测 | financial > comprehensive > central | test_priority_financial_over_comprehensive_over_central |

## 5. 准入门控清单 (17 项)

| ID | Description | 验收方式 | USER_ACTION |
|---|---|---|---|
| G-S4 | cn_text_utils 1000 句人工分句一致率 ≥ 95% | 实测 | ❌ 需用户标注 |
| G-A1.1 | LM 4 子词典专家审定 ≥ 90% | 1 人·周 | ❌ 需中文金融专家 |
| G-A1.2 | panel-level HTMT < 0.85 on ~9000 obs | stage 39e | ❌ 需 M0 panel 扩展 |
| G-A1.3 | LM article precision ≥ 0.80 on 200 篇 | 标注 | ❌ 需标注员 |
| G-A2.1 | FLS 词表 ≥ 100 词 + 500 句 precision ≥ 0.80 | 标注 | ✅ 词表 v0.1.5 131 词;❌ 500 句标注 |
| G-B1.1 | EPU 实际覆盖 2007-2024 | 数据下载 | ❌ 需 policyuncertainty.com |
| G-B1.2 | corr(EPU, GDP_growth) < 0.7 | 实测 | ❌ EPU 加载后 |
| G-C1.1 | tier 权重 3 组 sensitivity 符号一致率 ≥ 70% | paper Table A8 | ❌ panel 跑通后 |
| G-C2.0 | Stata `ssc install ritest` 跑通 | D-0 实测 | ❌ Stata 命令行 |
| G-C2.1 | ritest vs wild bootstrap p-value 一致率 ≥ 80% | paper Table 5 | ❌ Stata 跑通后 |
| G-30a | SBERT 400k 双轨编码 < 6 h | 实测 | ❌ GPU/CPU 跑 |
| G-D1.1 | BERTopic K ∈ [10, 30] | 实测 | ❌ 跑通后 |
| G-D1.2 | c-TF-IDF top-10 词 ≥ 80% 可解读 | 专家 | ❌ 专家 |
| G-D2.1 | surface 与 semantic staleness corr ∈ [0.3, 0.7] | 实测 | ❌ 5 包启用后 |
| G-D3.1 | valid 三元组覆盖 ≥ 60% bank-year | 实测 | ❌ 跑通后 |
| G-D4.1 | LLM CEO NER 200 篇 precision ≥ 0.85 | 标注 | ❌ 标注员 + LLM API |
| G-M0 | panel 扩展 168 → ≥ 1000 行 | 计算 | ❌ M0 master plan 阶段 |

## 6. 4 项 D-0 不可消除项

1. **policyuncertainty.com 中国 EPU 年份覆盖**: 若止于 2022 → 用 Huang-Luk 2020 R 代码自构 2023-2024
2. **Stata `ssc install ritest`**: 失败 → 手动从 IDEAS-RePEc 下载 .ado 到 PERSONAL ado
3. **BERTopic K 中文金融 corpus 实际值**: K < 10 → 降级 LDA K=15; K > 30 → 取 top-20 by article count
4. **LLM CEO NER precision/recall**: P < 0.7 → 降级规则版 (正则 + 高管 alias 列表)

## 7. 9 paper portfolio 接口

| Paper | v2.3 集成点 |
|---|---|
| P1 bank_fintech_tone | A1 robustness Table A7 + D3 cross-media α (heterogeneity) + D4 CEO mention (mechanism) |
| P2 bank_fintech_attention | C1 媒体 tier sensitivity Table A8 + C2.a ritest |
| P3 bank_fintech_substance | A1 + A3 robustness Tables A7/A9 + C2.a ritest |
| P4 bank_fintech_locus | A1 robustness Table A7 + C2.a ritest |
| P5 bank_fintech_collab | C2.b 补 boottest + ritest (原缺) |
| benefit_society | A1 + A3 sensitivity |
| brokerage_network | C2 ritest 补 (可选) |
| llm_peer | D4 CEO NER mechanism (可选) |
| strategic_diff | bank-level LDA (已有) + D1 BERTopic 对照 |
| **P10 bank_media_disagreement (新)** | **D3 α + variance main treatment** |
| **P11 bank_news_clarity (新)** | **mean_clarity_score_ctx main + D2 staleness mechanism** |

## 8. 与 v3.7.0 兼容性 (全 append-only)

| v3.7.0 既有 | v2.3 改动 | 兼容性 |
|---|---|---|
| 9 paper SSRN 草稿 | 新加 robustness Tables A7/A8/A9 | ✅ 不影响 main results |
| stage 49 risk_taking_outcomes (DC2) | 新加 stage 16/17/18/19/30a 互不干扰 | ✅ |
| pipeline/llm_archive (DC3) | D4 调用 archive_record (try/except) | ✅ |
| bank_list.yaml frozen | 不动 | ✅ |
| 第 10/11 篇 paper_spec | D3 α 与第 10 篇重叠 | ⚠️ 协调 gate |

## 9. SSRN v2 update 路线

```
v3.5.2 PR merge → main (已完成 2026-05-18)
  ↓
M0 panel 扩展 + Layer 2 用户操作
  ↓
Stage 22 重跑 → panel 含 LM + FLS 10 新列
  ↓
9 paper Stata 模板 keep 新列 + 重跑 Tables A7/A8/A9
  ↓
SSRN v2 update (4 paper 同步)
```

## 10. 参考链

- **方法学锚**: 12 顶刊文献 (见 §2)
- **架构锚**: v3.5.1 `_dual_analyze` 真双轨 + v3.6.0 main_treatment `_ctx`
- **测试锚**: 127/127 PR-touched fast tests
- **审核锚**: 17 轮累计 95+ 痕迹 (10 plan + 7 exec audit)
- **bug 锚**: 10 P0/P1 修复全部 grep + functional verify

---

**v2.3 implementation 在 v3.6.0 → v3.7.0 升级期间无缝并入, 不破坏任何既有 SSRN 草稿或 v3.7.0 DC3/DC5 数据治理框架.**

详见: `config/v2_3_implementation_constants.json` (sidecar frozen 常量) + `docs/methodology/v2_3_remaining_user_work.md` (USER_ACTION_REQUIRED 标注).
