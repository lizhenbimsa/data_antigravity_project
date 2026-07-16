# 指标审计修复落地 — 闭合报告 (2026-06-10)

> 对 `METRIC_AUDIT_TOPTIER_2026-06-09.md` + `METRIC_AUDIT_METAVERIFY_CLOSURE_2026-06-10.md` 三层审计确认的缺陷做修复落地。分支 `fix/metric-audit-toptier-2026-06-10`(基 `5bbb00b1`)。**未提交,待 user。**

**口径**: $0 本地重算 (无付费 API; `_llm_cache.db` 未动)。golden 已定向重生; 全链验证。
**安全网**: 修前备份 `_audit_fix_bak_20260610/`(40/46/51 panel + golden + 各 stage log)。

---

## 1. 已落地 + 已验证 (panel 重生 + golden 重生 + 测试绿)

### 1a. 公式/引文/标签 (golden 不变, 纯文档)
| 修复 | 文件 | 说明 |
|---|---|---|
| Tetlock 2011 **JF→RFS** 24(5):1481-1512 | 11 文件 14 处 (herd_decay/article_staleness/encode/geography/export/runner/dag + 3 config) | "All the News…" 实为 RFS |
| Berger 2022 → **LeSage-Pace 2009 + Leary-Roberts 2014** | network_spillover.py:299 | peer_fintech_exposure 锚点勘误 |
| auth_sim Hassan → **Hoberg-Phillips/Guzman-Li** | policy_similarity.py:70 | cosine-to-anchor 非 Hassan |
| llm_peer cutoff **difflib≠TNIC** 澄清 | llm_peer_iv.py:691 | difflib 串匹配严格度, 非语义阈值 |
| attention_index **extensive≠Hassan intensive** | attention_media.py:225 | ln(1+Σ) 累积曝光 |
| network-04 **同期 LOO 不解 Manski 反射** | network_brokerage.py:33,301 | 去自相关 ≠ 排他性 |
| z_score **CAR 变体≠L&L** | paper_spec.yaml:65 | 监管 CAR 非 equity/assets |
| BW2012 **裸比率≠残差 discretion** | paper_spec.yaml:71 | residual 未实现 |
| benefit median-center **非 Mu-Viswanath 法** | benefit_society.py:623 | 各向异性是动因非方法 |

### 1b. panel-layer 值修复 (golden 重生; 实测仅意图列变, 0 副作用)
| 修复 | 文件 | 实测效果 (盘上 T=2) |
|---|---|---|
| **peer_tone + peer_cov** fillna(0)→观测重归一 | network_spillover.py:270-323 | peer_tone_2nd min 0.0→**0.948**, 伪零 4→**0**; 二阶现为观测邻居加权均值 |
| **JF 分母 (P+N)²→t²**(含中性) | runner.py:1493 | 仍 [-1,1]; mean\|JF\| 0.998→**0.939**(中性主导行不再虚高) |
| **bartik 'other' 排除分母** | iv_did.py:304 | media 行和 0.727→**1.000**(与 type/scale 可比) |
| **strategic/auth JSD base=2** | strategic_diff.py:468,1125 | strat_diff_n5_lda max 0.826→**0.992**; coh_lda 底 0.181→0.017 ([0,1] 真) |
| **geography prox_frac 分母→可定位文章** | geography.py:929,940 | T=2 全可定位故无变 (scale 正确) |
| **geography 区域 phantom 守卫** | geography.py:1073 | 跳过空/缺失区域 (T=2 全匹配故 latent) |
| **clarity 加权均值 valid 分母** | encode_collab.py:528 | 各指标 valid-mask 分母 (T=2 无 NaN clarity 故无变, scale 正确) |
| **num_intensity valid 分母** | encode_collab.py:624 | 同上 (T=2 无空文本故无变) |

> 副作用核验: 新 40_panel vs 备份逐列比对 (排除 3 个 BLAS-FP 网络中心度列) → 17 列变, **全部为意图修复列或其直接下游** (auth_sim_lda=同 JSD 修; bartik_media_iv=share×shift 下游)。**0 个非意图列变化。**

### 1c. audit/validation 代码 (不进 golden panel)
| 修复 | 文件 |
|---|---|
| Int8+Int8 裸加法回绕 → astype('int64') | stata_audit.py:357 |
| temporal_mask 读不存在列 → 从 llm_sentiment 派生数值票 | temporal_mask.py:93 |
| radius_sensitivity 零方差守卫 (NaN 相关防污染裁决) | radius_sensitivity.py:497 |
| cross_media_alpha p90 `>=`→`>`(防 100% 天判事件) | cross_media_alpha.py:100 |

### 1d. 上游 stage 代码修 (golden 落盘 defer 到 production run)
| 修复 | 文件 | 落盘说明 |
|---|---|---|
| herd_decay **stable 排序+内容次键** (确定性) + **NaT 内部窗排除** | herd_decay.py:154,289 | 需 stage 24 重跑 |
| LM 分母 **仅计 word token**(排标点/数字) | lm_non_sentiment.py:117 | 需 stage 22 重跑 |
| 测试更新: peer_tone_2nd renormalize 语义 (-0.5→-1.0, B→NaN) | test_metric_audit_v3_fixes.py:149 | — |

---

## 2. 原 staged 复杂项 —— 现已全部实现 + 专用单测 (2026-06-10 第二批)
fix-safety 复核警示的 4 个复杂项已按精确设计落地, 各配专用单测 (共 12 个), 全链验证零回归:

### 2a. golden-impacting (已重生 golden, 已验证)
- **VW/MW/HW LLM 族 valid 分母** `runner._build_llm_valid_masked_weights` (3b/3c/3d 各建 valid-mask
  权重列) + `encode._llm_denom` (LLM 族除以 sum_wd_{wtag}_{group}{track}, dict/BERT 仍 physical)。
  **关键 nuance 已坐实**: 重生后 `llm_vote_tone_vw/mw/hw` **CHANGED**(valid 分母生效),
  `{dict}_tone_vw` / `{bert}_pos_vw` **SAME**(无反向失配); +30 列 sum_wd_*。3 单测
  (LLM→valid 1/3 / dict→physical 1/8 / mask 排无效行)。
- **fintech_share 去重计数基** `build_non_fintech` 经 df_nf.attrs 暴露 `ft_n_articles_dedup`,
  `merge_to_panel(..., ft_dedup_agg=)` 重定义 `fintech_share = ft_dedup/(ft_dedup+nf)`(可选参
  → 向后兼容旧测)。实测 ft_dedup=**849**(去重) vs 物理 857; `fintech_share==ft_dedup/(ft_dedup+nf)`
  全行成立。3 单测(8/13 去重 / 10/15 物理回退 / attrs 去重计数=2)。

### 2b. golden-deferred (代码+单测就位, 落盘待 production run)
- **prob-score verified 门控** `tone_llms.py:1190` —— 仅 verified=True 模型计入 avg_prob_score
  (镜像 s_votes_verified_only)。2 单测(0.85 仅验证 / 0.0 双验证均值)。落盘待 stage 21 重跑
  (piecemeal 注入行噪声)。
- **tone_words IDF 语料** `tone_words.py:1297` —— IDF DF 改在 content_full(与 TF 同语料)算,
  缺则回退 '内容'。1 单测(IDF 随 text_col 语料变)。落盘待 stage 22 重跑。
- **forward_looking FLS jieba** `forward_looking.py:_is_fls_sentence` —— 多字标记补 **≥3 字
  substring** 命中(纯加性, 不像 add_word 那样拆掉 '未来三年' 的 '未来' future token, 无回归)。
  3 单测(下一财年 substring 命中 / 双门控仍需 future / 未来三年 component 仍命中)。落盘待 stage 22。

**第二批验证**: golden repro+dag **39 passed**; VW LLM 改/dict+BERT 不改/+30 列; fintech_share
去重一致; 全量 sweep **24 failed = 同 baseline 0 新失败**; 12 新单测全绿; ruff clean。

---

## 3. 验证 (万无一失闸门)
- **golden 重生 + 复现**: stage 45→46→51 + generate_golden_snapshot 全 exit 0; `test_panel_reproducibility` + `test_dag_consistency` **39 passed**。
- **副作用**: 新旧 panel 逐列比对, 仅意图列(+直接下游)变, 0 非意图。
- **值正确性 (主控亲验)**: peer_tone 伪零清零 / JF∈[-1,1] 且降虚高 / JSD∈[0,1] / bartik 行和=1, 全符合预期。
- **回归**: 改动模块定向测试全绿 (herd bucketing 对拍 / iv_did / metric_audit / dual_track parity / numerical / lexical / 39d / orphan_merges); 网络测试按 renormalize 修正语义更新后绿。
- **全量 sweep**: 24 failed (grep -c 精确), 与 degradation baseline ("24 failed") **逐项一致** —— 16 opencc 缺包 (canonicalization/cell_id/preprocess_normalize×11/preprocess_load) + 5 pytest-asyncio 缺包 (aggregate_track_decoupling×3/pipeline_robustness×2) + 1 statsmodels 缺包 (benefit_shrinkage mixedlm) + 2 repo-state (cohort_csv commit 检查/v3_3→v3_4 migration)。**触碰模块零新失败** (network/encode/encode_collab/runner/iv_did/geography/strategic_diff/herd_decay/stata_audit/cross_media_alpha/radius_sensitivity/temporal_mask/lm_non_sentiment 均不在失败列表; 2 个 benefit_society 失败为 repo-state CSV + statsmodels, 非本批 comment 改动)。
- **ruff**: 21 文件 All checks passed。

---

## 4. 诚实边界
1. 验证基于 T=2 盘上样本; clarity/num_intensity/prox/regional 修复 scale 正确但在该无-NaN/全匹配样本上无值变 — 全量 T=19 (有空文本/未定位/未匹配) 方显效。
2. VW/MW/HW / fintech_share / prob-score / tone_words IDF / forward_looking 为 staged (设计就位, 未落实现) — 见 §2。
3. 上游 (stage 21/22/24) 代码修的 golden 落盘 defer 到 production run (piecemeal 重跑风险)。
4. Stata 模板侧 (Table 2 declared-vs-implemented design gap, 3rd-layer P1) 属 manuscript/spec 层, 未在本批代码修。
5. 未提交; 改值类需 user 确认 golden 重生方向。

**结论**: 三层审计确认的缺陷中, **可 $0 干净落盘的绝大多数已修复 + 全链验证 (golden 绿 / 0 副作用 / 值正确)**; 4 个 fix-safety-flagged / stage-21-hazard 复杂项以精确设计 staged。当前分支在已验证范围内**无新纰漏**。

---

## 5. 对修复的对抗复核闭合 (review-closure, 2026-06-10)
对全部修复 diff 跑 11-族对抗复核工作流 (2.6M tok) + 主控亲验。**controls-fintech-share 全清白**; NSP-B 经对抗 verifier 推翻(2nd-order renorm 是正确性改进非过度修正)。逮出并已处置:

### 5a. 真实缺陷 (已修)
- **NSP-1 (major, missed-sibling)**: `emb_peer_tone`(稠密嵌入同行网, network_spillover.py:1254)**仍用 fillna(0)** —— 与 peer_tone 同病根。已改观测重归一。⚠ **NSP-A**: 该轨依赖 30a_article_embeddings(缺), stage 45 未重跑嵌入 pass → 盘上/golden 暂未反映(repro 仍绿因二者同陈旧); T=2 上为近-no-op(缺 tone 银行 coverage=0→权重~0, 旧≈新), 真实差异仅 T=19, **落盘待带 embeddings 的 production run**。
- **PROBGATE-1 (major)**: prob-score 门控只做了模型级、漏了**文章级**(final_v=False/tie→final_s=None 时 avg_prob_score 未置 nan)。已补 `if final_s is None: avg_prob_score=nan`。
- **radius_sensitivity F1 (major)**: 零方差守卫返 NaN 但下游 min/mean **非 NaN-safe** → 仍污染裁决。已把 7 处 pearson 聚合改 np.nanmin/np.nanmean。
- **vwmwhw-F1 (minor, broken-invariant)**: 新 30 列 sum_wd_* 漏"计数/和→0"零填契约 → 零新闻行残 NaN。已加 sum_wd_ 入 zero_fill(本轮 golden-impacting, 已重生)。
- **cross_media_alpha F2 (minor, over-correction)**: 严格 '>' 漏掉 p90==max 的真峰值。已改 '>= p90 且 p90>pmin'(方差守卫), 常量分布 0 事件、真分布保全峰值。
- **citations F1 (nit, missed-sibling)**: llm_peer_iv.py:755 仍留 'TNIC 标准' 误标(同 L691)。已订正。
- **NSP-B (minor→非issue)**: 2nd-order renorm 对所有行改标度(路径概率和→邻居均值), 已加披露注(brokerage IV 对工具标度不变, 不破坏识别)。

### 5b. 弱测试缺口 — 高价值已补 (4)
prob-score 文章级门控(rewrite 3 测)、network 一阶部分观测重归一(1 测)、LM 词数分母(1 测)、herd bucketed-内部NaT 逐位等价(1 测)。

### 5c. 弱测试缺口 — 暂记 (fix 正确、仅覆盖不足, golden/pattern 已间接覆盖)
JF t² 单测(golden 已覆盖, 实测 jf 改)、bartik 'other'、2nd-order 多邻居、VW mw/hw/prob/fallback、encode_collab masked-denom(与 VW/numint 同型+真值正常)、geography prox/phantom(盘上 no-op)、stata_audit Int8 >127、IDF caller-level、herd 确定性(难单元隔离)、codebook 重生(31 新列)。

### 5d. golden-deferred (代码就位, 落盘待 production run)
emb_peer_tone(需 embeddings)、PROBGATE-1/prob-score(stage 21)、LM/IDF/FLS/herd(stage 22/24)。其盘上/golden 暂陈旧(repro 假绿), 全量 production run 自然落盘。

**review-closure 验证**: 重生 golden(45/46/51)→ repro+dag **39 passed**; sum_wd_ 已零填(NaN 0/30); 全量 sweep **24 failed = baseline 逐项一致, 0 新失败**; **25 个新回归测试全绿**(prob 文章级/network 一阶/LM 词数/herd 内部NaT + 既有); ruff clean。

**review-closure 结论**: 复核确实有效(逮出 emb_peer_tone 真兄弟 + prob-gate/radius 不完整 + sum_wd_ 契约 + cross_media 过度修正); 真实缺陷已全修 + 高价值测试已补 + 全链验证零新回归; 余为弱测试缺口(fix 正确, golden/pattern 间接覆盖)与 golden-deferred 落盘(emb_peer_tone/prob-score/LM·IDF·FLS·herd, 待 production run)。**分支在已验证范围内无新纰漏。**

---

## 6. 全campaign 汇总 (branch fix/metric-audit-toptier-2026-06-10, 未提交)
三层审计 + 三轮修复 + 对修复的对抗复核, 全部 $0 只读/本地重算:
- **batch-1 (~28)**: 引文勘误(Tetlock JF→RFS 等 9 族)+ panel 值修(peer_tone 伪零/JF t²/bartik other/JSD base2/clarity·numint valid 分母/geography prox·phantom)+ audit-validation(stata_audit Int8/temporal_mask/radius/cross_media)+ 上游(herd 确定性/LM 词数)。
- **batch-2 (4 复杂项)**: VW/MW/HW LLM 族 valid 分母 / fintech_share 去重计数基 / prob-score 门控 / IDF·FLS 语料。
- **review-closure (7 真缺陷)**: emb_peer_tone 漏改兄弟 / PROBGATE-1 文章级 / radius nan-safe / sum_wd_ 零填 / cross_media 过度修正 / llm_peer TNIC / NSP 注释。
- **测试**: 25 新回归锁(5 文件); 1 既有 test 更新(peer_tone_2nd renormalize 语义)。
- **golden 已重生并验证**(repro 39 / 全量 0 新失败 / ruff clean)。
- **golden-deferred 落盘**: emb_peer_tone(需 embeddings)/prob-score(stage21)/LM·IDF·FLS·herd(stage22/24)—— 代码+单测就位, 下次 production run 自然落盘。
- **未提交**, 待 user。
