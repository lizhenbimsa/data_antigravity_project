# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

# Communication

- Always respond in Simplified Chinese.
- Explain code changes in Chinese.
- Code comments: technical terms in English, explanations in Chinese where the file already mixes both (the de facto convention across `core/`, `pipeline/`, `papers/`).

## Project Overview

**news_process** is a research data pipeline that transforms raw Chinese news articles into panel datasets for econometric analysis. It processes bank and fintech news through multiple stages: preprocessing, classification, sentiment analysis (LLM/dictionary/BERT), and panel construction.

**Current version**: v3.7.4 (Panel D/E stratified robustness + bootstrap CI + Q1-Q5 empirical anchor, 2026-05-26);
**v3.7.4 NON-BREAKING (additive, 9 轮 pre-exec + 20 轮 post-exec audit / 53 finding 全闭, 2026-05-26)**: **Plan A v1.0 实施完成**: (1) **新 shared lib** `core/text/title_indicators.py` (4 函数: compute_title_mentions_fintech / compute_title_length_bucket / detect_title_sentiment_word / detect_bank_alias_in_title; EP-B3 L2 audit ↔ L3 prod 共源消除 indicator drift)。(2) **新 schema validator** `papers/_common/paper_spec_schema.py` (P0.7 9 轮 audit 假设其存在但实际为 false — 本批新建; validate_paper_spec + is_valid_audit_response_ref; 5 testcases)。(3) **stage 13 ctx_materializer 扩展** `_add_title_indicators` 函数 +30 LOC (调用 P3.0 lib 写 title_mentions_fintech + title_length_bucket 2 列; **执行期 P0 修正**: 使用 load_fintech_dict() + config.paths.fintech_dict_file = 1506 关键词, 非 cfg['filtering'].fintech_keywords)。(4) **panel encode 聚合扩展** +5 行 (frac_title_mentions_fintech + frac_title_long mean agg, append-only)。(5) **stata_export.py core_patterns + HEURISTIC_LABELS** +2 列 (frac_title_mentions_fintech / frac_title_long ≤ 80 UTF-8 bytes labels)。(6) **stage 39g bootstrap CI + 4-cell strata 扩展** +200 LOC (BOOTSTRAP_N_DEFAULT=1000 / BOOTSTRAP_SEED=42 / MIN_CELL_N=30; per-cell graceful skip; Henseler-Ringle-Sarstedt 2015 JAMS strict cutoff < 0.85 acceptance)。(7) **9 paper_spec.yaml × 3 字段补丁** (`audit_response_ref` 指向 methodology §5 = SoT + panel_d_caveat + panel_e_caveat; MA-4 SoT 不 inline)。(8) **9 Stata 模板 × Panel D + Panel E** (主线 25_tableA8_title_robustness + 7 paper-specific + benefit_society/26_bs; Panel D: stratify by frac_title_mentions_fintech across τ ∈ {0.3, 0.5, 0.7} per Antweiler-Frank 2004 JF; Panel E: stratify by frac_title_long per Da-Engelberg-Gao 2011 JF; per-cell N ≥ 30 graceful skip)。(9) **L4 lint script** `scripts/audit/loc_summation_check.py` (4.D mechanical enforcement: `<!-- loc-summation-check -->` opt-in marker / --from-stdin / --self-check; 8 unit tests)。(10) **L1 doc**: Report v2.6 (191 LOC) + methodology v1.1 (§4 标题改 "Methodological Acceptance and Validity Framework" + §4.4 Joint-occurrence Problem and Conditioned-sentiment Resolution + §4.5 Panel D/E Acceptance Criteria + §5 audit response 升级到 v1.1 含 7 直接顶刊 analog)。**学术锚点 v3.7.4 新增**: Tetlock-Saar-Tsechansky-Macskassy (2008 JF 63(3) "More Than Words", DOI 10.1111/j.1540-6261.2008.01362.x **CrossRef verified**); Antweiler-Frank (2004 JF 59(3)); Henseler-Ringle-Sarstedt (2015 JAMS 43)。**Q1-Q5 实证 (P2 audit script first-run, 2026-05-26)**: Q1 title length median=20 (p5=9 p95=39 mean=21.5); Q2 body length median=1528.5 (mean=1883.5); Q3 P(F∈title)=29.8%; Q4 P(B∈title)=25.6%; **Q5 joint-occurrence rate=0.68%** (8/1170 文章, framing zone "<15%"; provenance: git d9bdea9d + parquet SHA256 + lexicon 1506 keywords); **Q5 远低于 Q3×Q4 = 7.6%** 独立假设 → 标题倾向"提银行 OR 金融科技但极少 both+sentiment 同居" → **conditioned-sentiment 范式获决定性实证支持**。**测试 +51** (test_loc_summation_check 8 + test_title_indicators_v374 24 + test_panel_d_e_stratification_consistency 19) / 现 1880 fast pass + 3 pre-existing fail (与 v3.7.4 无关); 32/32 v3.7.4 新增 fast tests 全绿。**LOC 实测**: 1325 新增 + ~260 Edit = ~1585 LOC (±20% epistemic band [1268, 1902]; v1.7 plan declared 1728; within band)。**Audit history**: 9 轮 pre-exec (53 finding 全闭含 LOC 数字 8 轮硬错 → mechanical lint enforcement 终局闭合) + 20 轮 post-exec (3 P1 residual + 1 execution-time P0 = fintech_lexicon path bug 已修)。**P3.1.7 golden snapshot 不重生** (panel 14-40 未复跑, panel.parquet 未变化; defer 到 production panel run); P5 / P10 / P11 / git commit by user 决策保持 deferred。**$0 LLM 增量** / 0 panel 列改动 (panel-level 列等下次 production run 出现); **2 propagator scripts** (`scripts/migrate/v3_7_4_append_panel_de.py` + `v3_7_4_patch_paper_specs.py`) 替代 18 个独立 Stata 模板写入 + 9 个 paper_spec 编辑, 1 次 run idempotent。详见 [title_track_robustness_report_v2_6.md](docs/methodology/title_track_robustness_report_v2_6.md) + methodology v1.1。
**Current version (历史)**: v3.7.3 (Plan A v1.0 — _title 切片轨 Tier-B supplementary robustness 升级, 2026-05-26);
**v3.7.3 NON-BREAKING (additive, Plan A v1.0 + execution-period v1.0.1, 2026-05-26)**: 14 轮 audit + 1 轮实证地基重建 (78 finding 中实证证伪 9 项 / 误判 4 项 / 真正影响交付 5 项, finding inflation 率 94.6% 暴露前 13 轮未实证 verify 的方法学失败)。**Plan A v1.0 实施**: (1) **新 stage 39g** `pipeline/audit/track_discriminant_validity.py` + thin shim `39g_track_discriminant_validity.py` (HTMT 3×3 across `_full`/`_ctx`/`_title` 切片轨, 复用 39d HTMT + permutation seed=42 公共函数; STAGES_VALIDATION 17→**18**, EXPECTED_NO_OUTPUT +1, shim 实测 40→**41**, 含 v2.3 后加入的 27c_placebo_and_alt_anchor V2.0 J-L-M alignment 工具 shim 但未注册 DAG, 见 MEMORY shim_inventory)。(2) **9 paper_spec.yaml 升级**: 8 篇 (P1+P2-P5 + brokerage_network + llm_peer + strategic_diff) 填 `tables.tA8.template = '25_tableA8_title_robustness'` + benefit_society 用 paper-specific extension `title_robustness_table.template = '26_bs_title_robustness'` (v1.0.1 执行期发现: bs 的 tA8 已被 v3.5.1 A3 num_intensity 占用, 不可覆盖)。(3) **9 个 Stata 模板**: 主线根目录 `25_tableA8_title_robustness.do.tmpl` (P1) + 7 paper-specific 子目录 + benefit_society/26_bs_title_robustness.do.tmpl, 统一 `version 19 + set maxvar 32767`, 3 panel 设计 (Panel A title-only 替换 main / Panel B main+title Wald test 信息冗余 / Panel C +tone_gap_title_full Engelberg 2008 hard-soft control)。(4) **学术锚点**: Heston-Sinha (2017) FAJ + Loughran-McDonald (2016) JAR survey §6 + Boudoukh et al. (2019) JFE + Campbell-Fiske (1959) MTMM + Hassan et al. (2019) QJE + 14 篇顶刊证据 (详见 `docs/methodology/title_track_as_robustness.md`)。**R3-H1 兼容性维持**: A1 clarity + A3 num_intensity 在 `_title` 上仍排除 (text < 50 char unstable denominator), 仅 sentiment-family 指标 (LLM/dict/BERT) 进入 Table A8。**NEW-B1 false alarm 纠正 (v1.0.2)**: 初轮 audit 在 PowerShell GBK code page 下看到 `����` 误判 panel 含 mojibake; 实测 Unicode codepoint scan 揭示**实际是合法 UTF-8 中文字符** (0x6b63=正 / 0x9762=面 / 0x8d1f=负, 共 ~117 列, 形如 `finbert_cn_正面_w_sum_title`, v3.5.2 LM 4 子词典 sentiment label 设计), 非 GBK/UTF-8 双重编码污染。stage 39g 保留 `_is_mojibake_column` 防御过滤 (U+FFFD detect, 真 mojibake watchdog) + `tests/integration/test_panel_no_mojibake.py` 含 strict U+FFFD 检测 (实测 panel 0 个) + Chinese-column 诊断 (≥50 expected); stata_export.py rename 层已处理 Stata 中文变量名兼容性。**实证发现**: panel 已含 **~410 个 `_title` 后缀列** (远超调研报告"12-18 列"低估) + **17 个 `tone_gap_*` 列** (含 `tone_gap_title_full` Engelberg 2008 hard-soft asymmetry 测度已存在), `_title` 轨已是深度部署的完整稳健性体系, **本计划只是把既有产出从 audit-only 提升为 9 篇 Tier-B robustness 论文消费**。**测试 +30** (`test_39g_track_discriminant.py` 15 + `test_panel_no_mojibake.py` 4 + `test_paper_spec_tA8_filled.py` 11)。**$0 LLM 增量** / 0 panel 列改动 / 0 golden snapshot 重生成。**P10/P11 deferred to v3.7.4** (path B SSRN + G3 治理解锁路径不在本批次)。**P5 bank_fintech_collab deferred** (paper_spec.yaml::tables.tA8.deferred_until + v3.5.1 R3 known issue: P5 manuscript/refs.bib onboarding 未完成, 25_tableA8_title_robustness.do.tmpl 文件已就位但暂不可达 build_derivative_replication_package; 独立 PR follow up)。**stage 39g first-run 实证 (2026-05-26 disk panel 168×2060, n_articles ≥ 2 mask N=64)**: `overall_verdict: pass_title_discriminant` ✅ — HTMT(full, ctx)=0.965 (设计自相关, 与 Hassan 2019 QJE entity-proximity sub-window 一致, lenient pass 0.90), HTMT(full, title)=0.627 (**strict pass** < 0.85), HTMT(ctx, title)=0.628 (**strict pass** < 0.85), 5 indicator (llm_vote_tone / dict_avg_tone / bert_avg_pos / llm_models_avg_tone / dict_avg_idf_tone) 全跑, 0 mojibake skip (NEW-B1 false alarm 已纠正)。**Stata 模板 9 paper instantiate 测试**: P1 主线 + 7 derivative 全部 instantiate 成功 (placeholder-clean)。详见 [title_track_as_robustness.md](docs/methodology/title_track_as_robustness.md) §7.1 empirical first-run + §7.2 known limitations;
**v3.7.2 baseline (历史)**: v3.7.2 + v2.3 implementation (R8-H1 全管道延伸: ctx_is_fallback + frac_ctx_fallback 公共列, 2026-05-26);
**⚠ Disk 实测状态** (2026-05-16 baseline,本节"代码 ready"≠"disk 落地"): disk parquet 冻结于 2026-05-16,`40_panel_yearly.parquet` = 168×2024 **尚未含** v3.5.2-v3.7.2 声明的新增列 (LM 4 子词典 / A1 clarity / A3 num_intensity / EPU / D-group 5 stage / R8-H1 ctx_fallback = 共 15+ 列)。下游消费需先**重跑 stage 13/16/17/18/19/22/30a + 后续聚合**或显式等待 production run。Production run = M0 gate 锁定 (见 memory `paper_portfolio_decision_gates`,43-73 次 user 授权 / 3-5 年)。
**v3.7.2 NON-BREAKING (additive, R8-H1 全管道延伸, 2026-05-26)**: 4 轮 audit (R1 改进 + R2 7 finding + R3 scope split + R4 方法学诚实度) 收敛。**新 article-level 列** `ctx_is_fallback: bool` (ctx_materializer.py:108 + tone_llms.py:1207 双路径同源) — True iff content_ctx ≡ content_full (entity-miss / fallback)。**实测 R4-1 fallback 率 10.43%** (disk 13_news_with_ctx.parquet 1170 行)。**新 panel 列** `frac_ctx_fallback` + `n_articles_for_ctx_independence` (encode.py:577 build_aggregation_dict + size-bias-free 绝对独立文章数) — 用于 P1 (`llm_vote_tone_ctx`) / P11 (`mean_clarity_score_ctx`) 论文 measurement-error robustness (Hassan 2019 QJE proximity)。**stata_export.py core_patterns +2 列**, IC 余量 1925 (123/2048)。**lexical_discriminant_validity.py:20 docstring 修复**: R8-H1 docstring 此前声称"实现锁定"实则未实施, 改为"已暴露公共信号 + 39d 暂不实施 (validation-only ROI 低)"。**测试 +7** (test_13_materialize_ctx.py: column creation × 3 + parquet roundtrip × 1 + panel agg × 2 + intensity_verified 共线诊断 × 1)。**Pre-existing fail**: test_39_prompt_sensitivity::test_f2_aggregate_variant_contract (18 vs 16 unpacking, 与本 PR 无关, 见 `_aggregate_track` line 888 schema drift)。Shim 数不变, DAG 不变, jieba/prompt v8 锁不动。
v2.3 NON-BREAKING (additive, 17 轮 audit + 10 P0/P1 bug 全修): **v3.5.2 词典层** (PR #1-#4) — `core/text/cn_text_utils.py` (中文 splitter + jieba tokenizer + 200 词金融停用词, 50 fast tests) + `pipeline/sentiment/lm_non_sentiment.py` (LM 2011 JF 4 子词典 v0.1.5: uncert 83 / litig 104 / constr 76 / modal_strong 51 = 314 词, 14-41% LM 原版覆盖, 待专家审定 v0.2) + `pipeline/sentiment/forward_looking.py` (A2 Li 2010 JAR FLS 双门控 future 72 ∧ time 59 = 131 词) + `pipeline/audit/lm_discriminant_validity.py` stage 39e (HTMT + Cronbach α + 1000-rep permutation seed=42). Stage 22 `_dual_analyze` 真集成 LM+FLS → panel +10 列. **v3.6.1 集成层** (PR #5-#8.5) — `pipeline/external/epu_merge.py` stage 16 (Baker-Bloom-Davis 2016 QJE 中国 EPU; graceful fallback path-not-exist) + `pipeline/panel/encode.py::compute_media_tier_weights` (Solomon 2012 RFS 3 级 tier 权重 _tier 列 append-only, runner.py:267 真接入) + 4 Stata 模板 ritest 启用 (含 collab 补 boottest+ritest) + requirements +requests/+5 v3.7.0 包注释化. **v3.7.0 D 组** (PR #9-#13) — `pipeline/text/article_sbert.py` stage 30a (shibing624 持久化) + `pipeline/text/article_topic.py` stage 17 D1 BERTopic + `pipeline/text/article_staleness.py` stage 18 D2 双指标 (**算法 O(N²)→O(N·k) 重写 720× speedup**) + `pipeline/audit/cross_media_alpha.py` stage 39f D3 Krippendorff α (outlet×day matrix, 与第 10 篇 cross_outlet_tone_variance 对齐) + `pipeline/sentiment/executive_ner.py` stage 19 D4 LLM CEO NER (yunwu sync + LLMCache + DC3 archive). **PR #14 集成**: schemas OUTPUT_REGISTRY +5 (16/17/18/19/30a), EXPECTED_NO_OUTPUT +2 (39e/39f), STAGES_MAIN 15→**20**, STAGES_VALIDATION 15→**17**, stata_export core_patterns append +28 列. **Shim count 32→39** (v2.3 +7). **10 bug 全修**: S1.1 runner 接入 + S1.2 stage 22 集成 + S1.3 staleness O(N²) + S1.4 LLM 真接入 + S2.2 BERTopic merge + S2.3 Krippendorff matrix + B1 requests + B2 LLMCache + C1 epu path + C2 媒体双归属. **测试 baseline +77**: cn_text_utils 50 + lm_and_fls 25 + media_tier_and_epu 14 + d_group_modules 18 = **127/127 PR-touched green**. **4 D-0 实测项**: EPU 实际覆盖年份 / Stata ssc install ritest / BERTopic K / LLM CEO NER P/R. **21 项 USER_ACTION_REQUIRED** (Layer 2-6): 见 [docs/methodology/v2_3_remaining_user_work.md](docs/methodology/v2_3_remaining_user_work.md). 详见 [v3_5_2_v2_3_supplementation_plan.md](docs/methodology/v3_5_2_v2_3_supplementation_plan.md) + sidecar `config/v2_3_implementation_constants.json`.
**v3.7.0 (历史 baseline)**: 第 10/11 篇 立项 + DC3 LLM archive + DC2 outcome dry-run + DC5 implicit guarantee 框架, 2026-05-18;
v3.7.0 NON-BREAKING (additive): **第 10 篇** `bank_media_disagreement` 立项 (RFS / JFE target, path B = SSRN + `_full` main, treatment = `cross_outlet_tone_variance_full`, V4 R3 critical 修复); **第 11 篇** `bank_news_clarity` 立项 (JAE / JAR target, path C = No-SSRN + `_ctx` G3 解锁, treatment = `mean_clarity_score_ctx`, V4 reframe 为 external information environment quality 而非银行透明度); **DC3 LLM archive 模块** `pipeline/llm_archive/` (archive.py + manifest.py + tests/test_llm_archive.py 14/14 PASS, V4 F-P2.1 critical 修复; 顶刊 reproducibility 硬约束: 即使 GPT-5.4→5.5 升级仍可从 append-only JSONL + SHA-256 manifest 复现); **C1 集成** tone_llms.py (覆盖 stage 21/34/36/39) + llm_peer_iv.py (stage 48) 加 `archive_record(...)` 调用 (失败不阻塞 pipeline); **C2 stage 49** `49_risk_taking_outcomes.py` thin shim + `pipeline/panel/risk_taking_outcomes.py` (~300 行 Z-score + NPL formation + RWA ratio + LLP discretion + SOE/tier merge), DAG 注册 STAGES_MAIN 14→15 + OUTPUT_REGISTRY +1; **DC5 implicit guarantee 框架** `docs/methodology/implicit_guarantee_framework.md` (Acharya-Anginer-Warburton 2016 RFS 中国 banking setting 应用, 6 国有 + 3 政策性 + 5 D-SIB 股份制 + 18 上市城商 frozen at 2024-Q4); **C3 bank_list.yaml** frozen 39 行 (国有 6 + 政策性 3 + D-SIB 5 + 股份制 7 + 上市城商 18, M1 待补 ~460 行); **C4 .gitattributes Git LFS** `data/llm_archive/responses/*.jsonl` 配置 (~5GB 预估, GitHub LFS data pack $5/月); **DC2 outcome dry-run** `scripts/data_acquisition/` 3 脚本骨架 (banking_outcome_dry_run + outcome_schema_validator + fallback_decision α/β/γ 自动判定) + `docs/data/outcome_acquisition_protocol.md` 协议 (Wind/银保监/PDF 三级 fallback, 用户运行获取真实可得率). **审稿历程** 4 轮 audit 收敛: V1 (58 finding) → V2 (90 finding, 10 simulated rounds) → V3 (5 diamond critical, meta-audit) → V4 (白话回归, 4 真 critical + reframe) → DC1 决策 (分篇路线 path B+C). Shim count 31→**32** (含新 stage 49); test_dag_consistency 14→**15 stage** count.
**v3.6.0 (历史 baseline)**: Plan E execution — 上游单轨缺口闭合 + main treatment 切 _ctx;
v3.6.0 NON-BREAKING + 1 BREAKING (停用 herd_weight 单列): **P1 B3** herd_decay 双轨 (`herd_weight_{full,ctx}` 替代 v3.5.x 单列, Edwards 2001 ORM measurement-treatment matching, runner.py hw 加权 + encode.py agg/hw_denom 双轨独立); **P3 B2** policy_alignment 双轨 (`policy_cosine_sim_{full,ctx}`, cache key `-dual` 局部 namespace 隔离, ~$4 OpenAI 成本, 不动 features.yaml::text_pipeline_version 避免波及 benefit_society/strategic_diff/network_spillover 3 callsite); **P4 A1** 新 stage **13_materialize_ctx** 前置 `content_ctx` 物化 (新 `pipeline/text/ctx_materializer.py` + thin shim `13_materialize_ctx.py`, DAG 12→13→14→15, shim 数 30 → **31**, test_dag_consistency 14 stage); **P4 B1** fintech_intensity 双轨 (`fintech_intensity_score_{full,ctx}` + `intensity_verified_{full,ctx}`, main() 优先读 stage 13 输出, legacy alias 保留); **P4 D2** panel `avg_ft_intensity_{full,ctx}` (encode.py 双轨 agg); **P4 G3** P1 bank_fintech_tone spec main = `llm_vote_tone_ctx` (No SSRN preprint + 单作者 + 数据授权 三治理解锁, Tetlock 2007 JF 现代标准), batch migration script `scripts/migrate/plan_e_g3_paper_spec_ctx_switch.py` user-run 其余 8 paper; **P7 C1/C3/C4** stage 35/38a/38b 加 v3.6.0 双轨 stub marker (深度实施 follow-up P7.b); **P2** brokerage_network REPLICATION_README + 9 paper AI_DISCLOSURE_TEMPLATES.md (Nature/AER/JF/ASQ/RP/CSSCI 6 系列); ATT 漂移监控 `scripts/audit/att_drift_simulation.py` (user-run gate). Test baseline +14: test_24_herd_decay_dual 12/12 + test_15_policy_alignment_dual 14/14 + test_dag_consistency 14 stage count. git tag `plan-e-pre-execution` 锚定 v3.5.x 回滚点. **9 paper portfolio EV** (修正 Plan E §3 治理解锁后): brokerage/llm_peer/strategic_diff 立投 + B3/B2 killer fix + G3 main switch ≈ 3-5 paper 接收 (KPI 11 需治理重审).
**v3.5.1 (历史 baseline)**: Stage 3 supplementation — A1 Lexical Clarity + A3 Numerical Intensity 真双轨;
继承 v3.5.0 D2/D3/D4 + v3.4.0 P5 立项 + v3.3.0 multi-paper + v3.2.0 BREAKING Stage 3 双轨化;
**Prompt v8 字节级冻结** + **jieba == 0.42.1 frozen at D0** (不重跑 stage 21, $0 LLM 成本);
v3.5.1 NON-BREAKING (2026-05-17): A1 激活 you_2018 hhx055 Panel C 388 + Panel D 178 词 (LM 2011 JF + Bonsall 2017 JAE)
通过新 `_compute_clarity_for_text` 在 `_dual_analyze` 内对 content_full + content_ctx 真独立扫描 (修双轨假化);
A3 新模块 `pipeline/sentiment/numerical_intensity.py` (~250 行, Hales 2011 CAR Eq.1 + cn2arab 5 标准样例 frozen + 不定数排除);
panel +8 列 (A1 6 + A3 2): mean_clarity_score_{full,ctx} / mean_frac_definite_{full,ctx} / frac_amb_articles_{full,ctx} / mean_num_intensity_{full,ctx};
全 8 列进 stata_export.py core_patterns (core ~95→103 远低于 IC 2048) + 8 HEURISTIC_LABELS ≤ 80 UTF-8 bytes;
stage 39d 新 validation: HTMT 双 cutoff 0.85/0.90 + Cohen κ + Cronbach α across 3 indicators + permutation seed=42 + pairwise on-disk < 1GB + ctx-fallback mask;
sidecar JSON `data/processed/v3_5_1_constants.json` 双 anchor (median_amb_d0 + prompt_v8_sha256 + stage21_last_run_timestamp, 修 panel.attrs 序列化丢失);
encode_collab.py +apply_v3_5_1 (~200 行, 与 apply_v3_5_0 并存; v3.6.0 合并方案预留);
9 paper_spec.yaml × tables.tA7/A8/A9 同步 (5 active: P3/P4/P5 tA7 + P1 tA9 + benefit_society tA8 / 其余 4 paper null explicit);
4 paper-specific Stata 模板 + 1 v3_5_1/ root 模板 (P1 例外); master plan §5.2.3.bis schema 扩 tA7/tA9/tA8 (epoch 7 audit cycle);
git tag `v3.5.0-augmentation` ✓ + `v3.5.1-plan-frozen` ✓ + `v3.6.0` ✓ (2026-05-18, 当前 HEAD) + `v3.5.1-supplementation` (planned, post-merge);
**97 finding 经 10 轮 audit closed** (V1-V15 + 同行 P1/P2/P3 + D-day 压力 + 完备性 + 对抗性 + 边缘 case + EiC + v0.3 复证);
plan v0.3 SHA256 (D-1.8 计算后填); 锚定: 继承 v3.5.0 + LM 2011 JF + You 2018 + Hales 2011 CAR + Bonsall 2017 JAE + Cohen 1960 + Cronbach 1951 + Nosek 2018 PNAS;
详见 [stage3_v3_5_1_a1_a3_supplementation_plan.md](docs/methodology/stage3_v3_5_1_a1_a3_supplementation_plan.md) + audit log；CHANGELOG.md 暂未维护，版本变更以本文件顶部 "Current version" 段为准)
**Test baseline (v3.7.0 实测 2026-05-18)**: **1629** fast / **284** integration / **1913** total tests collected (`pytest --collect-only`); 历史轨迹: v3.3.0 ~1175 → v3.4.0 ~1527 → v3.5.1 ~1590 → v3.6.0 1615 → v3.7.0 **1629** fast. v3.7.0 +14 fast tests: test_llm_archive 14/14 (TestAppendOnly 5 + TestArchiveRecord 3 + TestManifest 5 + TestSha256OfFile 1) + test_dag_consistency 14→15 stage 内部子断言. v3.6.0 Plan E +14 fast tests: test_24_herd_decay_dual 12 + test_15_policy_alignment_dual 14 + test_dag_consistency 14-stage count；继承 v3.5.1 +63: 12 clarity_score + 10 numerical_intensity + 8 a1_a3_panel_aggregation + 12 lexical_discriminant + 8 stata_export_v3_5_1 + 6 v3_5_to_v3_5_1_migration + 3 forward_compat + 4 dag_consistency/paper_spec_schema 扩 + 等)

**CLI 子命令** (`python -m news_process.papers._common.stata_runner <cmd>`):
- `build-replication`: 一键 instantiate 14 .do 模板 + spec 替换
- `list-templates [--verbose]`: 14 模板清单 + 占位符 inventory
- `doctor [--verbose]`: 5 段诊断 (deps + pipeline + LLM + Stata bin)
- `verify-replication <path>`: 5 段验证 replication 包结构

**v3.1.1 → v3.2.0 panel 迁移**: `python -m news_process.scripts.migrate.v3_1_to_v3_2_panel_upgrade`

## Architecture

### Pipeline Structure

The pipeline is a **declarative DAG** defined in `news_process/core/dag.py`. All stages are registered in `STAGES_MAIN` (production) or `STAGES_VALIDATION` (evaluation). The orchestrator (`run_pipeline_function.py`) executes stages as isolated subprocesses.

**Stage flow** (v3.6.0):
```
00_preprocessing → 11_news_bank → 12_news_fintech → 13_materialize_ctx
→ 14_fintech_intensity → 15_article_policy_alignment
→ 21_tone_llms / 22_tone_words / 23_tone_berts → 24_herd_decay_processor
→ 30_robustness_text2vec → 45_panel_export_main → 46_stata_export → 51_falsification_test
```
v3.6.0 Plan E P4 A1 新增 `13_materialize_ctx` 物化 `content_ctx` 列, 让下游 14/15 在 stage 21 之前即可消费 ctx, 实现 B1 fintech_intensity + B2 policy_alignment 真双轨化 (`*_full` / `*_ctx`).

Sentiment methods (21/22/23) are conditionally enabled via `config/sentiment.yaml::sentiment_analysis.enabled_methods`.

### Directory Layout

```
news_process/
├── core/           # Kernel: config, logging, caching, DAG, stage runner
├── pipeline/       # Stage implementations (filtering, sentiment, panel, etc.)
├── papers/         # Multi-paper module dirs (11: 9 fully-coded + 2 立项 v3.7.0)
├── validation/     # Robustness tests (threshold sensitivity, entity masking, etc.)
├── config/         # Split YAML configs + prompt templates (config.yaml is a legacy stub)
├── data/           # Input (raw/) + output (processed/*.parquet)
├── tests/          # 1615 fast / 284 integration / 1899 total (v3.6.0 实测 collect-only)
└── NN_*.py         # 41 thin shim scripts under news_process/ (≤30 lines each,
                    # NN ∈ {00, 11..19 (incl. 13/16/17/18/19), 21..24, 27c, 30, 30a,
                    #       31..39 (incl. 32a/38a/38b/39a/39c/39d/39e/39f/39g),
                    #       45, 46, 49, 51..53};
                    # delegate to pipeline/; planned retirement: Plan-r3 P3-18
                    # (拆分约束见 pipeline/panel/runner.py:159).
                    # 38 registered in core/dag.py (20 STAGES_MAIN + 18 STAGES_VALIDATION);
                    # 3 unregistered by design: 27c (audit-only sibling, jlm2026 plan §P1.6),
                    # 52/53 (user-CLI wrappers, schemas.py:182 显式排除).
```

**Key invariant**: `news_process/NN_*.py` scripts are thin shims. All logic lives in `news_process.pipeline.*`. Never add business logic to shims.

### Single Sources of Truth

1. **DAG**: `core/dag.py::STAGES_MAIN` / `STAGES_VALIDATION`
2. **Output registry**: `core/schemas.py::OUTPUT_REGISTRY` (stage → parquet files)
3. **Config**: split YAMLs in `config/{paths,preprocessing,filtering,sentiment,features,panel,validation}.yaml`
4. **Dependencies**: `pyproject.toml::[project].dependencies` (requirements.txt is a fallback)

### Data Flow

- **Input**: `data/raw/*.xlsx` (raw news articles)
- **Intermediate**: `data/processed/*.parquet` (one per stage, e.g., `21_tone_llms.parquet`)
- **Final**: `data/processed/40_panel_yearly.parquet` (bank-year panel for Stata)
- **Logs**: `logs/runs/<run_id>/<stage>.log` (one run_id per pipeline execution)

## Development Commands

### Environment Setup

```bash
# From repository root
# Create virtual environment
python -m venv venv
# Linux/macOS:
source venv/bin/activate
# Windows cmd.exe:
venv\Scripts\activate
# Windows PowerShell (本项目主环境):
venv\Scripts\Activate.ps1

# Install dependencies (choose one)
pip install -e .                                  # Development: runtime deps only
pip install -e ".[dev]"                           # Development + dev tools (pytest, pre-commit, pytest-cov)
pip install -r news_process/requirements.lock && pip install -e . --no-deps  # Exact deps + editable package
pip install -r news_process/requirements.txt && pip install -e . --no-deps   # Fallback for pip-only users

# Configure environment
cp news_process/.env.example news_process/.env
# Edit .env: set YUNWU_API_KEY (required for LLM stages)

# V4 T1.4: enable local pre-commit hooks (one-time per dev machine)
pre-commit install
# Now `git commit` auto-runs: check-prompt-headers + ruff check
# Manual run against full repo: pre-commit run --all-files
```

### Running the Pipeline

```bash
# Full pipeline (all enabled stages)
python run_pipeline_function.py

# Validation pipeline (robustness tests)
python run_pipeline_validation.py

# Single stage (for debugging)
python 21_tone_llms.py
```

### Testing

> **Must run pytest from the repository root** (`f:\WiseSearch\data_antigravity_project\`).
> Running from `news_process/` subdir may bypass the parent `pyproject.toml::testpaths`
> setting; the `news_process/conftest.py::collect_ignore_glob` covers the common case
> (excluding `data/`), but root-level invocation gives consistent behavior.

```bash
# Run all tests (from repo root)
pytest

# Run specific test file
pytest news_process/tests/test_21_tone_llms.py

# Run specific test
pytest news_process/tests/test_21_tone_llms.py::TestToneLLMs::test_basic_flow

# Run integration tests only
pytest news_process/tests/integration/

# Run with verbose output
pytest -v

# Run tests matching pattern
pytest -k "test_golden"

# V4 T1.6: tiered runs (auto-tagged by tests/conftest.py)
pytest -m fast              # 1615 fast tests (~30s, run before every commit; v3.6.0 实测)
pytest -m integration       # 284 integration tests (parquet IO, mocked LLM, ~5min)
pytest                       # full sweep (1899 tests collected)
```

### Linting & Formatting

```bash
# Lint with ruff (configured in pyproject.toml)
ruff check .

# Auto-fix issues
ruff check --fix .

# Check specific file
ruff check news_process/core/config.py
```

### Regenerating Golden Baseline

After schema changes that add/remove columns:

```bash
python scripts/migrate/generate_golden_snapshot.py
pytest tests/integration/test_panel_reproducibility.py
```

## Critical Constraints

### Git Commit Protocol

1. **Never amend commits** unless explicitly requested. After pre-commit hook failures, create a NEW commit (amending would modify the wrong commit).
2. **Stage specific files** by name. Avoid `git add .` or `git add -A` (risk of committing `.env` or secrets).
3. **Commit message format**: Use HEREDOC with `Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>` trailer.
4. **Never skip hooks** (`--no-verify`) unless explicitly requested.

### Code Modification Rules

1. **Stage shims are frozen**: The 41 `news_process/NN_*.py` scripts are thin shims (≤30 lines; NN includes stage 13 from v3.6.0 Plan E, lettered variants 32a/38a/38b/39a/39c/39d/39e/39f/39g, plus stages 49/52/53). All logic belongs in `news_process.pipeline.*` or `news_process.validation.*`.
2. **DAG consistency**: Any stage added/removed must update:
   - `core/dag.py::STAGES_MAIN` or `STAGES_VALIDATION`
   - `core/schemas.py::OUTPUT_REGISTRY` (if it produces parquet)
   - Run `pytest tests/integration/test_dag_consistency.py` to verify
3. **Config split is active**: `core/config.py::load_config()` prefers the 7-domain YAML split and falls back to legacy single-file mode only when all split files are absent. Keep split files semantically equivalent to the legacy config contract.
4. **Golden baseline**: After column schema changes, regenerate `tests/fixtures/golden_panel_v0.json` via `scripts/migrate/generate_golden_snapshot.py`.

### Testing Requirements

- **Integration gate**: `tests/integration/test_panel_reproducibility.py` must pass (validates column hashes against golden baseline).
- **DAG consistency**: `tests/integration/test_dag_consistency.py` enforces:
  - All `STAGES_MAIN` entries are in `OUTPUT_REGISTRY` or `EXPECTED_NO_OUTPUT_STAGES`
  - No duplicate stage names across STAGES_MAIN / STAGES_VALIDATION
  - Orchestrator imports match `core/dag.py` (identity check via `is`)
- **Mock external APIs**: Tests must mock LLM/embedding APIs (see `tests/test_25_audit.py` for fixture examples).

## Common Patterns

### Adding a New Stage

1. Create implementation in `news_process/pipeline/<module>/<stage>.py`
2. Create thin shim `NN_<stage>.py` under `news_process/` (≤30 lines, imports and calls pipeline function)
3. Register in `core/dag.py::STAGES_MAIN` with `StageSpec(...)`
4. If it produces parquet, add to `core/schemas.py::OUTPUT_REGISTRY`
5. Add tests in `tests/test_XX_<stage>.py`
6. Run `pytest tests/integration/test_dag_consistency.py` to verify

### Modifying Config Schema

1. Edit the owning split YAML under `config/`
2. Update `core/config.py::load_config()` only if loader semantics change
3. Regenerate golden baseline if column schema changes
4. Run full test suite to catch downstream breakage

### Debugging Pipeline Failures

1. Check `logs/runs/<run_id>/<stage>.log` for the failed stage
2. Run the stage in isolation: `python news_process/NN_<stage>.py`
3. Use `pytest tests/test_XX_<stage>.py -v` to reproduce in test environment
4. Check `data/processed/` for intermediate outputs

## Environment Variables

Required in `.env`:

- `YUNWU_API_KEY`: Unified API key for LLM sentiment analysis (stages 21, 32a, 33, 34, 36, 39) and embedding (stage 15, 27)
- `EMBEDDING_API_KEY`: Defaults to `${YUNWU_API_KEY}` (can override for separate endpoint)
- `FINBERT2_MODEL_DIR`: Optional local BERT model path (stage 23 gracefully skips if missing)

## Multi-Paper Support

The `papers/` directory contains 11 paper-specific module directories (v3.4+ multi-paper portfolio; 9 fully-coded + 2 立项 v3.7.0 — `bank_media_disagreement` / `bank_news_clarity` — which currently ship only `paper_spec.yaml` + `stata_templates/` + `replication/`, pending M5/M7 module creation)。

**P1–P5 Bank-FinTech 主线五篇**（统一 `bank_fintech_*` 命名；paper-level ID 引自 `docs/plan/B_route_master_plan_v2.md`，各 paper README 顶部标记格式不统一：P2/P3/P4 用 `(Px)`、P5 用 `P5 —` 前缀、P1 在 README L1 标"主线论文"未显式写 P1）：
- `bank_fintech_tone/` (P1, master plan 主线): bank-fintech 媒体语调；P1 三轨化 spec `locus × subst × sent = 2³`（v3.6.0 G3: main = `llm_vote_tone_ctx`）
- `bank_fintech_attention/` (P2): firm-level fintech attention intensity (Hassan 2019 QJE 框架)
- `bank_fintech_substance/` (P3): W&Z 实质/象征二元属性
- `bank_fintech_locus/` (P4): Gomber 底层/应用二元属性
- `bank_fintech_collab/` (P5, v3.4.0 epoch 5 立项): Chesbrough 自主研发 vs 外部协同

**衍生四篇**（非 Bank-FinTech 主线，独立 paper id）：
- `benefit_society/`: Social benefit analysis
- `brokerage_network/`: Network brokerage effects（v3.6.0 已加 `REPLICATION_README.md`）
- `llm_peer/`: LLM peer review (方法学)
- `strategic_diff/`: Strategic differentiation

> 注: CLAUDE.md 顶部 "Current version" 段中的 `P1/P2/P3/P4/P7` 标号指 **Plan E 内部步骤**, 与本段 paper-portfolio 的 `P1..P5` paper ID 是两个独立编号空间。

Most papers have `analysis.py` (Stata runner), `figures.py`, and `tables.py` (exceptions: `bank_media_disagreement` / `bank_news_clarity` ship spec + templates only, pending M5/M7; `bank_fintech_collab` lacks `analysis.py`). Common utilities are in `papers/_common/` (含 v3.6.0 新增 `AI_DISCLOSURE_TEMPLATES.md` 6 系列：Nature/AER/JF/ASQ/RP/CSSCI).

## Stata Environment

**本机 Stata：StataNow/MP 19.5**（2026-05-16 通过 `about` 命令实测确认）。
- 安装路径：`C:\Program Files\StataNow19\StataMP-64.exe`（115 MB）
- Build：Revision **14 Jan 2026**（StataNow 滚动通道；非年度主版 19.0）
- 平台：Windows 64-bit x86-64
- 许可：**64-core lab perpetual**（MP 并行核心数 = 64）
- 硬件：物理内存 128 GB，可用 98 GB
- 默认 `set maxvar = 5,000`（已高于 IC 上限 2,048，可一直上调到 MP 上限 120,000）
- License note：Unicode 支持开启，>2 billion observations 允许

所有 `.do` 模板、replication 脚本与下游回归（reghdfe / ivreg2 / csdid / sdid /
synth / coefplot 等）以 MP 上限为天花板编写。

### Stata/MP vs SE vs BE 技术上限（Stata 19 官方文档，2026-05 抓取；19 vs 18 硬上限未变）

| 限制项 | Stata/BE | Stata/SE | **Stata/MP（本机）** |
|---|---:|---:|---:|
| Max observations | 2,147,483,619 | 2,147,483,619 | **1,099,511,627,775** (≈1.1 兆) |
| Max variables (`maxvar`) | 2,048 | 32,767 | **120,000** |
| Max RHS variables in model | 798 | 10,998 | **65,532** |
| matrix dimension (`matsize`) | 800 × 800 | 11,000 × 11,000 | **65,534 × 65,534** |
| String var `str#` | 2,045 bytes | 2,045 bytes | 2,045 bytes |
| String var `strL` | 2 GB | 2 GB | 2 GB |
| Variable name length | 32 chars | 32 chars | 32 chars |
| Variable label length | 80 chars | 80 chars | 80 chars |
| Value label string | 32,000 bytes | 32,000 bytes | 32,000 bytes |
| Characters in command | 264,408 | 4,227,159 | 4,227,159 |
| Characters in macro | 264,392 | 4,227,143 | **15,480,200** |

来源：https://www.stata.com/products/detailed-size-limits/ +
https://www.stata.com/products/which-stata-is-right-for-me/

### 对本项目（v3.6.0）的含义

1. **当前列数全部在 MP 上限内、远未触顶**：
   - `46_panel_yearly_full.dta` / `40_panel_yearly.dta`：2024 列
   - `46_panel_yearly_core.dta`：49 列（IC 兼容入口）
   - `46_panel_yearly_aux.dta`：1977 列（与 core 互补，merge 1:1 可还原 full）
   - `51_panel_with_controls.dta`：**2033 列（当前最大）**
   - **裕度**：MP 上限 120,000 − 2033 ≈ **117,967 列**，可放心继续加稳健性 / BERT 变体特征。
2. **`pipeline/panel/stata_export.py::STATA_IC_MAX_VARS = 2048` 是 IC 兼容性保留**，
   不是本机限制。`core / aux` 双切分是为外部协作者用 IC 跑通预留的；本机 MP 可
   直接读 `*_full.dta` 或 `51_panel_with_controls.dta` 跳过切分。
3. **matsize 在 Stata 19 已自动管理（Stata 16+ 起 deprecated）**：MP 19.5
   下 `set matsize` 仍可设但被 Stata 内部统一处理，`reghdfe` / `ivreg2`
   等主流命令走 Mata 矩阵不受 matsize 约束。仅在使用 `regress` 原生命令 +
   极多 RHS 时才需要显式 `set matsize 11000`（SE 上限）或更高。
4. **行数维度**：当前 panel 168 行（84 banks × 2 years, 2017–2018）远低于
   MP 上限 1.1 兆，受限的是**面板深度（T=2）**而非 Stata 容量；任何 panel
   扩展瓶颈都在上游数据来源 / stage 41，不在 Stata。
5. **64 核并行**：MP 19.5 license 是 64-core，跑 `bootstrap`、`permute`、
   `rwolf`、`ritest`、`csdid` 多重 placebo / wild bootstrap 时可拉满
   `set processors 64`（默认按 license 上限走，无需手动）；这是当前 v3.6.0
   稳健性矩阵性能上的关键资源。

### 修改 Stata 配置时的注意

- **不要在通用模板中硬编码 BE/IC 才有意义的列截断逻辑**：若发现 .do 模板里
  写了 "前 2048 列" 之类的截断，那是 IC 兼容遗留，本机 MP 应改读 full 版本。
- **新增列时优先扩 `aux.dta`，保持 `core.dta` ≤ 2048**：保留 IC 协作者的
  入口契约，不要因为本机是 MP 就把 core 撑爆。
- **项目策略 (2026-05-16 起): Stata 19+ only, 无需向下兼容**。
  `papers/_common/stata_templates/**/*.do.tmpl` 全部 **104 个模板** = 主线 15 (直接位于
  `stata_templates/` 下) + 8 个 paper-specific 子目录 86 (attention 8 / collab 9 /
  locus 9 / substance 10 / benefit_society 23 / brokerage_network 9 / llm_peer 9 /
  strategic_diff 9) + 历史归档 `v3_5_0/` 2 + `v3_5_1/` 1。全部已统一 bump 为
  `version 19` + `clear all` + `set maxvar 32767` + `set linesize 120`
  （见 `00_master.do.tmpl:13-16`）。新增模板直接复用此头部。
- **可放心使用 v17+ / v19 独有命令**: `xtdidregress` (v17)、`frames` 增强
  (v16/v18)、`bayesmh` GPU、`pystata` 集成、新版 `meta` suite 等无需任何
  `version` 守卫；`version 19` 已锁定最低要求。
- **设置 `version 19` 的副作用**: Stata 18 及更老版本会直接报
  "version 19 is not a valid version" 拒跑 — 这正是 "19+ only" 策略的
  执行机制。外部协作者若仍在 Stata 18，需先升级再跑 replication 包。
- **`set maxvar 32767` 仍是防御性保留**: 本机 MP 19.5 默认 5,000 对当前
  2033 列已够用，但 stage 46 输出可能继续向 IC 上限 2048 逼近；这一行让
  模板独立于 maxvar 默认值（不论用户是 MP / SE）都能装下 full .dta。
  ⚠ `maxvar 32767` 是 SE 上限；如果未来 panel 列数突破 32,767（远期），
  需上调到 `set maxvar 120000`（MP 上限）。
- **pyreadstat 写出的 `.dta` 仍用 format version 118**（见
  `pipeline/panel/stata_export.py:369`、`papers/_common/tables.py:102`）。
  这是 **.dta 文件格式版本**（spec 编号），不是 Stata 应用程序版本；
  118 是 pyreadstat 当前能稳定写出的最高 .dta spec，Stata 19 读取无任何
  限制（变量名 32 字符 / value label 32K bytes 等都满足）。不要把它和
  `version 19` 混为一谈。

## Known Issues & Workarounds

1. **Windows line endings**: Git may warn about CRLF. This is expected on Windows. The repo-root `.gitattributes` marks `*.parquet`/`*.xlsx`/`*.db` as binary; source files keep their on-disk EOL (no forced normalization to avoid churning the existing mixed-CRLF history).
2. **FinBERT2 model**: Stage 23 requires a private fine-tuned model. If `FINBERT2_MODEL_DIR` is unset or invalid, the stage gracefully skips that model (other BERT models still run).

## Phase History

The project underwent 9 restructuring phases (v1.x → v2.1.0):
- **Phase 0-1**: Package skeleton + DAG single-source
- **Phase 2**: Split monoliths + OUTPUT_REGISTRY + acceptance gate
- **Phase 3-7**: Multi-paper productization + active 7-domain config split
- **Phase 8**: Data layout normalization (`data_processed/` → `data/processed/`)
- **Phase 9**: Cleanup of Phase 3/7a residue

Current HEAD baseline tracked in line 16 (top of file).
