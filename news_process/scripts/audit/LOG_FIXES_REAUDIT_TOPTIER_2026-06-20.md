# 日志生产者缺陷修复 + 顶刊标准再审报告

> 续 `LOG_FILES_ENRICH_AUDIT_TOPTIER_2026-06-20.md` (§9 修复清单) 的【全部落地 + 再审】
> 日期: 2026-06-20
> 方法: 主控逐处落地 18 文件修复 → 57-agent 再审工作流 (16 源码级修复核验 + 39 日志二次扫描 + 对抗完整性批判 + 汇总) → 主控复核 + 收口 3 残留
> 工件: `scripts/audit/_logaudit_20260620/` (FIXES_20260620.diff · reaudit_verify.md · reaudit_rescan.md · reaudit_critic.md · reaudit_synthesis.md) · 工作流 wf_3105aba8-6ca

---

## 0. 总裁决

**§9 修复清单全部落地 (18 文件, +87/−45), 经 57-agent 再审【0 FAIL / 16-16 文件全 PASS / golden-safe / 零新引入 bug】, ruff 全绿, 定向测试 exit 0。** 再审另揪出 4 条残留, 其中 3 条已即时收口 (P1-A 陈旧红测 / P2-C depins_post 零方差守卫 / P3-B CLAUDE.md `_ss` 缓存时态), 第 4 条 (提交隔离) 为提交时机械操作纪律 (本次仅落工作树, 未提交)。**当前工作树 = 顶刊级干净的纯 validation/log/doc 修复, 与并行会话零逻辑耦合。**

| 维度 | 评级 |
|---|---|
| 修复集本体质量 | **A** (27 处修复全部正确、golden-safe、零新 bug、py_compile 全绿) |
| golden 安全性 | **A** (diff 零 panel-producer; 仅 validation/log/doc; golden_panel_v0.json 改动属并行会话) |
| 诚信 (引用/声明) | **B+** (主动订正 Bybee/Carlson 归属/cosine/AMP/SIF 等错挂; 仍 ≥4 处待 Crossref 核验) |
| 可复现性 (代码层) | **A−** (stage 21 离线 0-miss 已实证; 扣分=多数 stage 日志缺 sha256/版本自证锚 R12) |
| 可复现性 (取证层) | **B−** (生产日志被 pytest fixture/import 经 file_mode='w' 覆写 R1, 系统性, 见 §4) |

---

## 1. 落地的修复 (18 文件)

> 全量 diff: `scripts/audit/_logaudit_20260620/FIXES_20260620.diff`。所有修复仅动 validation 诊断 / 日志文本 / 文档, **不碰主面板生产逻辑、不触 golden**。

### A 纯日志文本/标签/注释 (零行为·零数值)
- `validation/tone_validation.py` — `_ss` 轨标签二元三目→三路映射 (1436/1662, 对齐 canonical 2516); 多数投票判读改动态众数 `_dom_lab/_dom_pct` (2597+); stratified docstring 阈值改 q33/q66 (1026-1028)
- `pipeline/sentiment/tone_berts.py` — 3 处 AMP/共享分词陈旧字符串改 `USE_AMP`/`DEVICE` 联动 (987/991/1131-1133)
- `pipeline/sentiment/tone_words.py` — negonly verdict 去写死 "0.998-0.999" → "r≥0.95 即稳健 + T18 参照" (1944)
- `core/dag.py` — 32a 注释 "4 个阈值"→"5 个阈值 (0.70/0.75/0.80/0.85/0.90)" (356)
- `validation/dedup_threshold.py` — 日志标签 "(config.yaml)"→"(config/preprocessing.yaml::...)" (214)
- `run_pipeline_validation.py` — docstring 把 Carlson&Burbano 从 stage36 移到 stage33; stage36 改锚 SSRN-4558295+Landis&Koch (29/31)
- `pipeline/text/article_sbert.py` — banner+docstring "revision 钉死"→"ensure_torch_determinism 保证 + revision 当前未钉死" (63/258-261)
- `pipeline/filtering/policy_alignment.py` — banner cosine "0~1"→"∈[-1,1], 实务多落 0~1" (1031)
- `config/validation.yaml` — 32a 注释 "约2.5小时"→"实测~80min; DAG 硬超时 43200s/12h" (25)
- `pipeline/filtering/cooccurrence_filter.py` — 小样本警告口径统一 "过滤前 n_in/n_banks_in → 过滤后 n_out/n_banks_out" (351)

### B 诊断输出值 (validation-only, 不入面板/golden)
- `validation/media_diversity.py` — `rated_media` 误把 Tier 类别数(=4)当家数 → `sum(c ...)` 汇总各档家数 (475; 同步修正 Excel "已评级媒体占比")
- `validation/llms_evaluation.py` — demo 分支补 `n_both_sen=len(df_both_sen)`, 消 ICR-情感 n=0 vs N=200 矛盾 (~1606)
- `validation/dict_coverage.py` — `effect_size` 进问题清单门槛 5.0→3.0, 与本文件 ~974 (abs<3.0) 及 3pp 健康线统一 (749)

### C 行为/产物 (validation 层, 已查无下游引用)
- `validation/tone_validation.py` — `bert_num_windows`→`f'...{track}'` 后缀对齐 producer (1221/1254/1256, 激活原死分层, 双门控防崩); 4 张热力图加 `{track}` 后缀消互覆写 (2224/2269/2302/2343); Δα 改 |Δα| 双向判读 (新增 `elif delta<-0.10`, 1315-1330)
- `pipeline/panel/network_brokerage.py` — fire_sale 零方差 WARNING (常量列下游无识别力; 不改数值, 531+)

### D 文档
- `config/v2_3_implementation_constants.json` — Bybee anchor "RFS 37(3):887-936"→"JF 79(5):3105-3147" (111)
- `CLAUDE.md` — 面板行数 176→172(86 banks; 53/302); 最宽 dta 1569→2782 (297); radius {0,1,2}→{0,1,2,3} (21); **`_ss` 缓存时态校准 (58, P3-B)**
- **故意保留为历史锚** (经再审确认正确): `1170/14.27%/65.76%` (`_ss` 设计时点磁盘小样测量, CLAUDE.md 自带 "disk 小样" 限定) + "176→174 行漂移" (过去事件叙述)

### 再审收口的 3 残留
- **[P1-A] 陈旧红测** `tests/test_omni_fix_val_prompt.py:202` — 断言 `{'full','ctx'}` 早于 `_ss` 第三轨, 实跑 FAILED (`{'ctx','full','ss'}=={'ctx','full'}`)。源 `run_variant_llms` 自 v3.9.0 硬迭代三轨 (prompt_sensitivity.py:634-637), content_ss 缺列回退 content_full。修: 断言改 `{'full','ctx','ss'}` + 补 `prompts['ss'].count(title)==1`。→ 修后 29 passed。
- **[P2-C] depins_post 零方差守卫** `pipeline/panel/runner.py:1457+` — 与 R18 fire_sale 对称: 盘面 T=2 仅 {2017,2018} 全 ≥2015 → depins_post 恒常量 1, tone_x_depins* 退化无识别力。加常量列 WARNING (不删列; 生产 T=18 跨 2015 断点恢复方差)。
- **[P3-B] CLAUDE.md `_ss` 缓存时态** (58) — "须线上付费首跑播种" 是已被证伪的现在式声明 (2026-06-19 实测离线 10125/10125 0-miss)。加时态限定: 引入时点为 0、现已全播种、离线 $0 可复现。

---

## 2. 再审核验结论 (57-agent)

- **修复核验 (16 文件 / 27 fix)**: 23 PASS + 4 PASS-WITH-NOTE, **0 FAIL**。全部 NOTE 均为 "对称约定 / 事后并行漂移 / 双门控守卫" 性质, 非缺陷。
- **对抗风险逐一排除** (critic 实读源码确认): `_dom_lab=vote_dist.idxmax()` 受 `_vote_total>0` 双重守卫 → 空 Series 不崩; heatmap `{track}` 后缀是**消除**3 轨互覆写 (全仓无裸名读者) 而非引入冲突; `bert_num_windows{track}` 激活的分层受 `valid_mask.sum()>=40` + 每组 `<20:continue` 双门控, T=2 退化落 skip 不崩、不 mutate df; Δα `elif` 分支变量在域、NaN 已守; `n_both_sen` 重赋在两分支赋值之后、非 demo 恒等 no-op; `rated_media=sum(c)` 与 `unrated_media`/`rated_media_pct` 同口径。
- **日志二次扫描 (39 份)**: `newly_found` 全部为 **P2/P3/low** (无新 P0/P1)。第一轮已记项不重复。

---

## 3. 残留 / 延后 (carry-over, 不阻塞工作树修复)

- **R19 变量名 33 字符** (`exc_jiang_2021_score_negonly_full`): 源码仅 WARN, 但 stata_export 写前由 `shorten_long_column_names`(md5 去重) + `_assert_track_triplet_unique` 兜底, 不致 Stata 写崩 → 低危, 下游有防护, 改名会动 .dta schema + golden, 故不在本批改。
- **待 Crossref/DOI 核验的引用** (投稿前): Carlson & Burbano (2026, SMJ 47(3):699-725) 未来日期+精确卷期=典型造假签名 (全仓 30+ 处); SSRN-4558295 §7.2 (裸编号); Distel/Grimpe/Poetz (2026, RP) 同-DOI-双标题 (policy_alignment.py:26 vs refs.bib:49); Andreou et al. (2026, RP 55(3):105409)。不可确认者降级 forthcoming/working paper。
- **conftest 日志隔离盲区** (取证层): `_isolate_loggers_from_production_files` (conftest.py:283, scope='session') 对夹具内惰性 import 的 pipeline 模块失效 → 12b/37/47/39c/39e/39f/21 等真实生产日志被 pytest fixture/import 经 `file_mode='w'` 覆写 (R1 横切共因)。建议改 function 级重扫 / 加 `console_only` / `NEWS_PROCESS_TESTING` 守卫。
- **受控重跑 + golden 重生** (M0 gate, 生产 T=18): stage 21 在线全量 / 36/39 在线付费; `OMP_NUM_THREADS=1 + KMP_DUPLICATE_LIB_OK` 单线程确定性重生, 排除 3 个 BLAS-FP 网络列; radius∈{0,1,2,3} 网格; 勿删 `_llm_cache.db`。**本次未重跑**: 并行会话正占用 panel/golden, 离线重跑会撞车 → 各 stage 日志仍是修复前输出, 待下次干净全量跑或受控重生时自然刷新。

---

## 4. 横切发现 (与第一轮一致, 系统性)

- **R1 测试/import 覆盖生产日志**: `file_mode='w'` 首写截断 + "只留最新一次运行" → 一次 pytest/import 即把真实生产日志覆写成单行 banner。本批修复**未触碰**此机制 (属日志架构改动, 非 §9 范围); 见上方 conftest follow-up。
- **R12 复现要素薄**: 真实生产日志声明"逐位可复现"但缺 sha256/库版本/git commit 自证锚; 30a 的 revision-钉死自相矛盾已订正 (本批), 其余待统一增打。

---

## 5. 并行会话隔离 (提交纪律)

工作树同时含本修复集 18 文件 + 一个**并行会话** (loughran 第6词典 + golden 重生) 的在途改动: `pipeline/panel/attention_media.py` (加 `'loughran_score_'` 前缀) + `tests/fixtures/golden_panel_v0.json` (golden 重生) + `tests/test_omni_fix_attention.py` + `_regen_backup_20260620/` + `config/dicts_excel/Loughran-McDonald/_work/`。

- **逻辑耦合评估 = 无冲突**: 本修复集零 panel-producer, 与 loughran 的 golden schema 变更正交。
- **提交纪律 (若后续提交)**: 严格 `git add` 本修复集 18 文件 by-name, **排除** 上列并行文件 (与 MEMORY 多次记载的"并行会话误并入"事故同型)。**本次仅落工作树, 未提交。**

---

## 6. 工件
- 本报告: `scripts/audit/LOG_FIXES_REAUDIT_TOPTIER_2026-06-20.md`
- 第一轮报告: `scripts/audit/LOG_FILES_ENRICH_AUDIT_TOPTIER_2026-06-20.md`
- 修复全量 diff (18 文件): `scripts/audit/_logaudit_20260620/FIXES_20260620.diff`
- 再审明细: `_logaudit_20260620/{reaudit_verify,reaudit_rescan,reaudit_critic,reaudit_synthesis}.md`
- 工作流: 富集+审计 wf_eec23a98-048; 再审 wf_3105aba8-6ca
