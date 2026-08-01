# 日志群最终审计裁决 (第三轮 · 收口)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 续 `LOG_FILES_ENRICH_AUDIT_TOPTIER_2026-06-20.md`(首轮) + `LOG_FIXES_REAUDIT_TOPTIER_2026-06-20.md`(再审) + `DEFERRED_ITEMS_COMPLETION_2026-06-20.md`(延后收口)。
> 方法: 46-agent 最终审计工作流 (5 延后核验 + 39 日志终扫 + 终极对抗批判 + 终审) + 主控 WebSearch 引用核验 + 收口新发现 golden-safe 项。
> 工件: `scripts/audit/_logaudit_20260620/` (final_sweep / final_critic / final_verdict / reaudit_* / FIXES_20260620.diff / _final_junit.xml)。工作流: 富集+审计 wf_eec23a98-048 · 再审 wf_3105aba8-6ca · 终审 wf_313c48ba-bb1。

---

## 0. 最终总裁决

**三轮审计 + 修复链收口完成: 日志群达到顶刊"无数据造假、零真实 P0、零未决 P1、零回归"标准。**
- 终审对全部 ~40 份日志逐一裁断 **integrity_ok=true**(零造假/零完整性破坏)。
- 我的累计修复 = **24 文件 (golden-safe, 全 validation/log/doc 层, 零 panel-producer 逻辑改)**, 经 ruff 全绿 + **333 定向测试 0 失败 0 错误** + conftest R1 修复实证(生产日志 md5 跑测试前后逐位不变)。
- 唯一硬遗留 = **受控 golden 重生 (T=19)**, 三重生产门控 (本机 data/raw 空 + 付费 M0 gate + 并行会话占用), 非缺陷, 已给 SOP。
- 与并行 loughran 会话(7 文件)**零文件交集、零逻辑冲突**; 我的 24 文件已隔离, 未提交。

| 维度 | 最终评级 |
|---|---|
| 诚信 (无造假) | **A** — ~40 日志全 integrity_ok=true; 引用经 WebSearch 核验(见 §2) |
| 修复质量 | **A** — 24 文件全 golden-safe, 零回归, 333 测试 0 失败, 终极批判逐项确认无新 bug |
| 可复现性 (代码层) | **A−** — stage 21 离线 0-miss 实证; R1 根因已修(测试不再覆写生产日志) |
| 可复现性 (取证层) | **B+ → A−** — R1 修复后 pytest 不再污染生产日志(此前为 B−) |

---

## 1. 延后项收口 (5/5, 终审独立核验全 PASS)

| ID | 项目 | 终审裁决 |
|---|---|---|
| D1 | conftest R1 根因 monkeypatch | **PASS** — 38 caller 全核无冲突; import-heavy pytest 前后生产日志 md5 逐位不变; tmp 单测豁免不误伤 |
| D2 | entity_masking SSRN-4558295 诚实标注 | **PASS** — EMNLP 2023 替换锚点 web 实证; 无等价性误称 |
| D3 | Distel 标题订正 | **PASS** — en/zh refs.bib 改为 web 字节匹配真实标题 |
| D4 | R19 变量名 33 字符 | **PASS** — 截断 ≤32 唯一, 不改源正确(改名破 golden) |
| D5 | golden 重生阻塞判定 | **PASS** — 三阻塞实测成立; 修复 golden-safe 不依赖重生 |

---

## 2. 引用 WebSearch 核验 (推翻"普遍造假"假设)

- **Carlson & Burbano (2026, SMJ 47(3):699-725)** — ✅ 真且精确 (DOI 10.1002/smj.70023)。"造假签名"为虚惊。
- **Andreou et al. (2026, RP 55(3):105409)** — ✅ 真且精确 ("Measuring R&D activity through 10-K narrative disclosures")。
- **Distel/Grimpe/Poetz (2026, RP 55(3):105426)** — 卷期页 DOI 对, refs.bib 标题伪造 → ✅ 已订正为真实 "From Evidence to Impact: The Use of Scientific Research in Policy Documents"。
- **SSRN-4558295** — ⚠ web/SSRN 无法解析 → ✅ 已诚实标注待核验 + 给已发表方法学锚点 (EMNLP 2023 Findings 2023.findings-emnlp.728)。

> 教训: 先核验再下结论, 避免按启发式误删两篇真引用。

---

## 3. 终审新发现 → 本轮额外收口的 golden-safe 修复 (6 处)

终审日志终扫的 `newly_found` 全为 P2/P3(无新 P0/P1)。其中可即修的 golden-safe 项已收口:

1. **stage 31 金科轨边界关键词丢失** (`threshold.py:209-219`) — 旧物理切片 `text[:mid]/text[mid:]` 各扫一遍会漏掉横跨 `mid` 的关键词 (与生产 analyze_fintech_matches 已修的 omni-g-entity-07/11 同源 bug 模式)。**改为单遍扫全文 + 按起始位置切 upper/lower**, 无边界丢失。validation-only, 不触 panel/golden。
2. **stage 31 banner 过度声称** (`threshold.py:491`) — 旧称"金科轨复用与 stage 11/12 完全一致逻辑"(银行轨属实, 金科轨是独立实现)。**改为如实区分**: 银行轨 = analyze_bank_matches 一致; 金科轨 = 本 stage 独立全文扫 + 位置切分, 与 stage 12 高度一致但非逐字复刻 (±1 篇边缘分歧)。
3. **stage 48 llm_peer_iv banner** (`llm_peer_iv.py:132`) — 旧打 `models={len(MODELS)}`=3, 实际只用 `MODELS[0]` 单模型 + flat retry。**改为** `models_used=1 (仅 MODELS[0], 配置共 3)` + 标注 flat sleep。
4. **stage 32a 去重前语料量级错挂** (`dedup_threshold.py:433/437-439`) — 旧标"去重前 ~385万行", 32a 日志实证去重前 = **405万 (4,046,188)**, 385万 = 精确去重后(MinHash 基数, 3,853,947)。**已订正**为 405万去重前 / 385万 MinHash 基数。
5. **tone_berts 3 处 AMP 代码注释** (`:422/:435/:1077`) — R7 修了 log 行, 残留 docstring/注释仍写"(FP32, AMP推理)"。**已对齐** USE_AMP/DEVICE 口径 (完成 R7)。
6. **tone_words negonly 注释** (`:1934`) — 加 T=19 全量参照 vs T=2 盘面限定, 与 R8 verdict 文案一致。

---

## 4. 终审复核为【非缺陷】的项 (先核验再决定, 未改)

- **stage 39a inter_track_kappa κ 方向** — 终审初疑"高 κ 既当冗余又当稳健"自相矛盾; 主控实读源码确认 **内部一致**: κ∈[0.50,0.70] 为甜区 (>0.70 冗余 / <0.30 噪声 / 中间=互补稳健), WARNING 与 docstring 兼容, 非矛盾。**不改**(改则错)。
- **finbert2 ~98% 正面 / 39d substance κ=nan / 51 证伪零反例** — T=2 盘面测度单侧退化, 已如实披露为 §3.4 / T=19 重投资项, 非造假, 非可即修缺陷。

---

## 5. 文档化的遗留 (本批之外, 投稿/生产前)

- **stage 31 金科轨与 stage 12 逐字对齐** — 本轮已修边界丢失 bug + 诚实化 banner; 若要 100% 逐字复刻 analyze_fintech_matches (含其窗口/去重细节), 需在 T=19 重生时让 stage 31 直接复用生产函数 (行为变更, 需重跑 stage 31 + 验证)。
- **并行 loughran 会话责任** (NOT 本批): `decay_sensitivity.py:896` "15 列"应为 18 列 (6 词典×3); `export.py:109` `38_decay_sensitivity.csv` 漏 'b' 致 G-14 摘要静默跳过 → 由该会话顺修, 勿并入本批。
- **R12 复现自证锚点** (横切 ~15 份生产日志) — 普遍缺 input parquet sha256 / 库版本 / git commit / OMP_NUM_THREADS / seed 值; 纯日志增量、golden-safe, 建议统一增打 (批量, 投稿前)。
- **受控 golden 重生 (T=19)** — 生产门控 (见 DEFERRED_ITEMS_COMPLETION §4 SOP); `OMP_NUM_THREADS=1` 排除 3 个 BLAS-FP 网络列; 勿删 `_llm_cache.db`。

---

## 6. 三轮累计成果

| 轮次 | 产出 |
|---|---|
| 首轮 (富集+审计) | 富集 10 稀疏日志 + 审计 41 日志 → **69 真问题** 全修 |
| 再审 | 16/16 文件 PASS + 4 残留 → 修 3 (R1 conftest 根因 / media rated_media / 等) |
| 终审 (本轮) | 5 延后收口 (4 done + 1 生产门控) + 引用 WebSearch 核验 + 6 新 golden-safe 修复 + κ 方向复核为非缺陷 |
| **累计** | **~79 真问题修复 + 引用净化 + R1 根因根治; 24 文件 golden-safe; 333 测试 0 失败; 零造假; 未提交** |

---

## 7. 给用户的下一步
1. **提交 (若需)**: by-name 只 `git add` 本批 **24 文件**, 严格排除 7 个并行 loughran 文件 (`attention_media.py`/`export.py`/`stata_export.py`/`decay_sensitivity.py`/`radius_sensitivity.py`/`golden_panel_v0.json`/`test_omni_fix_attention.py`) + `_regen_backup_20260620/` + `dicts_excel/.../_work/`。pre-commit ruff 须绿。
2. **转告并行会话**: decay_sensitivity:896 / export.py:109 两处 loughran 责任项。
3. **投稿/T=19 前**: 统一增打 R12 复现锚点 + 受控 golden 重生 (排 BLAS-FP 列) + stage 31 逐字对齐 (可选)。
