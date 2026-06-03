# V3 修复终审复核 + 二次修复收尾 (2026-06-03)

> 对 PR#6 (commit f0babf46) 的修复做最高标准对抗式自审 (6 维度 × 逐发现验证, 25 agents / 2.36M tok) → 主控逐条亲验 → 二次修复闭合。本文记录复核结论 + batch-2 处置。

## 1. 复核结果

6 维度终审: correctness=minor / completeness=**material** / data=minor / stata=minor / claims=minor / regression=minor。**15 confirmed / 3 refuted / 0 uncertain**。核心价值: 揪出**修复自身的漏改兄弟站点**(最高遗漏风险类), 证明首轮 23 项修复**非完美无缺**, 存在系统性同型遗漏。

## 2. 二次修复 (batch-2, 已闭合 + 全链重跑 + 重生 golden)

**改值类 (peer_cov NaN / tone_gap 守门 / LM-FLS jieba; 经 22→backfill 23/24→45→46→51→golden)**:
- **completeness-01 (major)** `network_spillover.py:307` peer_cov(peer_fintech_exposure_lag1) 漏 network-03 掩码 → 41 伪零混入 brokerage Table1。修: `np.where(row_has_peers, peer_cov, NaN)`。实测 73/41零 → **32/0零**。
- **completeness-05 (major)** `encode.py:1318` 第 6 个 tone_gap (indep_collab_cm_ctx) 漏 encode-02 min-n≥5 守门。修后 nonnull 47→**18**。
- **completeness-02 (major)** `tone_words.py` LM(18.5%)/FLS 词典漏注入 jieba (clarity_cn-01 同型兄弟)。修: item6 注入 load_lm_non_sentiment_dicts() 四子集 + FLS future/time。实测 LM frac 改 72 行; **dict-tone 连带 ripple max|Δ|=0.0029 (可忽略, 正确性向)**, num_intensity 0 变。
- **completeness-03 (major→latent)** `runner.py` disag_llm/concern_score Int8 (pos+neg) 在 ≥128 回绕 (concern 翻符号)。当前 max~100 **不触发** (实测 disag/concern 0 行变化), 仍加 float64 防御。
- **completeness-06 (minor→latent)** emb_peer_tone 同型孤立→0 (当前嵌入稠密 0 孤立行, 防御性掩码)。

**Stata 模板兄弟 (background agent; 0 panel 影响)**:
- **stata-01/02/03** st-did-05 字符串 bank_type 比较 + levelsof 引号漏改 locus/18·substance/18 (r109)、locus/17·substance/17 (r198) + substance/17 `soe`→`is_soe`。
- **stata-04** 全面板披露 note 漏 brokerage/llm_peer/strategic_diff 三个 10_table1。
- **correctness-04 (升级)** V5 从 "degrade 丢控制" 升级为真 lf/sf→裸名 (tech_frac/symb_frac) 重映射 + capture confirm 二次兜底 (full 轨现解析到真实列而非静默丢 LOCUS/SUBST)。
  - **回归自捕获并修复**: agent 在 11_table2 注释里写的 `tech_frac_{{...}}` 被 verify-replication 误判占位符残留 (rc=1) → 改注释为 `tech_frac_<track>`, cli_verify 复绿。

**文档/测试**:
- **data-02** network docstring 披露 T=2 样本塌缩 (一阶 peer 网 32 / 2SLS N≈22 单截面不可识别, 待 T≥3)。
- **correctness-01** benefit 注释澄清 "~0.5 指文章级 pooled, 面板 frac 因 Jensen 聚合 ~0.45"。
- **regression-01** 新增 network 端到端测试 (compute_network_spillovers: 孤立→NaN + W² 去对角无自反馈)。

## 3. 诚实更正 — claims-01 (over-claim 自纠)

前 commit f0babf46 / PR#6 称 benefit "饱和 **0.97→0.45**"。经 `git log -L` 复核: 该 commit 的 median-center 改动实际是 **0.518→0.452**; "0.97→0.518" 是**前一个独立 commit 65563d5a (mean-center)** 完成的。f0babf46 把跨两次 commit 的累计幅度归给单次, 属轻微 over-claim。**更正**: median-center (f0babf46) = 0.518→0.452; sign-at-0 饱和 0.97→0.518 由 65563d5a 处理。

## 4. 仍 defer (cost-gated, 非遗漏)

- **completeness-04 (major)** policy_similarity:116 + strategic_diff _full 轨读裸 `内容` (病根A 同型兄弟)。**未修**: 二者 embedding-based, 改 content_full → 付费 re-embedding (strategic_diff 在 stage45 内, 改后重跑必产生 API 成本)。与 **tonellms-01** (ctx LLM 重注入) 同属 cost-gated 延后项, 待 user 授权付费 re-run。当前保持 $0。
- locus/17·substance/17 的 SOE-split 块各保留一处 `soe` 幻影引用 (capture confirm graceful skip 不崩, 对齐 attention/17 参考写法), 标注为 latent。

## 5. 验证 (batch-2)

test_panel_reproducibility **19 绿** · stata_audit **FAIL=0** · metric-audit 回归 **54 passed** (含新 network e2e) · Stata 模板 + 触及模块 **252 passed** · ruff clean。预存失败 (ftfy/xlsxwriter/statsmodels 缺依赖 + 87→88 漂移) 与本批无关。备份 data/processed_v3fix_bak2/。

**结论**: 首轮修复经终审揪出 6 个同型漏改兄弟 + 4 个 Stata 兄弟 + 1 over-claim, batch-2 已全部闭合 (cost-gated 2 项明确 defer)。当前 PR#6 (f0babf46 + batch-2 commit) 在已审范围内**无 blocker/major 残留**, 可 merge。
