# 日志文件富集 + 顶刊标准全量审核报告

> 批次: `logs/` 目录全量编号阶段日志群 (39 份当前 + 2 份 `archive/2026-06-17/`)
> 日期: 2026-06-19 富集与审计 → 2026-06-20 主控复核收口
> 方法: 63-agent 多智能体工作流 (10 富集 = 调研→对抗核验 · 41 单文件审计并行 · 1 汇总 · 1 对抗完整性批判) + 主控亲验关键结论
> 工件: `scripts/audit/_logaudit_20260620/` (logs_snapshot/ 固定快照 · audit_digest.md · synthesis.md · critic.md · enrich_blocks.md)
> 任务来源: 用户 — (1) 对内容较少的日志做顶刊标准富集; (2) 对全部日志做最系统最全面的评审/审核/验证, 多智能体确保万无一失。

---

## 0. 一句话总裁决

**本批日志诚信通过 — 无系统性数据造假、无真实 P0 数据缺陷。** 唯一标 P0 的条目 (`21_tone_llms.log`) 经核实是「import 期模块 banner 被误当 stage 21 运行记录」的 **provenance 错配 (防误读 P0)**, 非数据伪造。主要问题集中在三条横切主线: ① 测试/import 进程经 `file_mode='w'` 覆盖了真实生产日志 (provenance 在编排层断裂); ② 真实生产日志普遍缺 sha256/库版本/git commit 等自证锚点; ③ 当前 T=2 盘面上多个情感/构念测度呈**单侧退化** (finbert2 ~98% 正面 / LLM 象征性轴恒坍缩 / 证伪检验零反例)。**所有数值结论必须在生产 17M / T=18 全量重跑 + golden 受控重生后才能定稿**, 当下盘面仅验证管道正确性。

可复现性整体评级 **B−** (A=2 · B=22 · C=8 · D=7; D 级全为夹具/截断片段, 不代表真实阶段)。

---

## 1. 任务 (1) — 稀疏日志富集 (已落地)

对 10 份"内容较少"的日志 (≤~2KB / 1–9 行) 做了顶刊标准富集。**诚信铁律**: 整数运行结果**绝不编造**; 富集内容只补充可在仓库中验证出处的 **功能 / 方法 / 判读框架 / 真实参考文献 / 为何本次稀疏 (基于 PID·时间戳·临时路径的实证) / 可复现性元信息**。

**落盘方式 (可审计、不污染原始日志)**:
- 每份富集块以 `# ` (井号+空格) 开头, 醒目标注「文档补充 · DOCUMENTATION SUPPLEMENT · 非运行时输出 · 人工审计富集」, 读者一眼区分人工标注 vs 机器日志。
- 原始运行时日志行**逐字节保留** (header 与 footer 之间, 由 `# ──── 以下为本次运行原始运行时日志 (verbatim, 未改动) ────` 分隔)。
- 每份经"起草 agent → 对抗核验 agent"两道工序: 逐条 claim 核对 `file:line`、删除任何无法验证出处的引用、订正 PID/行号偏差。10 份全部 `verified=True`; 9 份 `integrity_ok=True`, 1 份 (`run_pipeline_validation`) 的 `integrity_ok=False` **仅表示草稿存在被核验者发现并已修正的引用错挂** (Carlson&Burbano→误挂 stage36 应为 stage33; L&M→误挂 39e 应为 33; Krippendorff 版本), 终稿已全部订正。

| 文件 | 原始 | run_type | 富集后行数 | 关键说明 |
|---|---|---|---|---|
| `14_fintech_intensity.log` | 1 行 | dag-import-test | 63 | import 期词典加载 banner, main() 未跑 |
| `13_materialize_ctx.log` | 1 行 | dag-import-test | 77 | 同 PID:13604 成对 import, main() 未跑 |
| `21_tone_llms.log` | 2 行 | mixed (import) | 83 | 面板构建进程 import 触发; **审计后被再次覆盖** (PID 40372→25852), footer 已据当前实测重述 |
| `36_entity_masking_test.log` | 1 行 | graceful-skip | 80 | `NEWS_PROCESS_LLM_OFFLINE=1` 离线守卫 early-return |
| `39_prompt_sensitivity.log` | 4 行 | pytest/smoke | 75 | 1 行×1 模型微型 smoke, 非 36000 请求全量 |
| `39c_construct_orthogonality.log` | 9 行 | partial-truncated | 59 | 截断于 `read_parquet` 之前 (无结果/无 Traceback) |
| `39e_lm_discriminant_validity.log` | 4 行 | pytest-fixture | 70 | 4 行=5 个定向单测的 fail-loud helper 残留 |
| `39f_cross_media_alpha.log` | 1 行 | pytest-fixture | 77 | 单测直调 `aggregate_to_bank_year` 回退分支 |
| `run_pipeline_function.log` | 1 行 | dag-import-test | 70 | `test_dag_consistency` import 副作用 |
| `run_pipeline_validation.log` | 1 行 | dag-import-test | 67 | 同上; 终稿已订正 3 处引用错挂 |

> ⚠ 既有约定提醒: `logs/` 为 git-ignored 运行时产物, 每次跑流水线 `file_mode='w'` 覆盖同名文件 (CLAUDE.md 2026-06-15 决策)。**本次富集的 `#` 文档块会在下次真实跑该阶段时被覆盖**; 需要长期留存的版本即本报告 + `_logaudit_20260620/enrich_blocks.md` + `logs_snapshot/`。

---

## 2. 任务 (2) — run_type 分布 (审核第一关)

> **关键提醒**: dag-import-test / pytest-fixture / graceful-skip 三类日志里的 ERROR/WARNING **几乎全部是良性夹具/离线守卫产物**, 不可作为流水线故障证据。同样一条域降级 ERROR 若出现在**真实生产日志**中则升级为 P1。

| run_type | 文件 | ERROR/WARNING 性质 |
|---|---|---|
| **生产-离线 (真实可信)** | 11,12,12b,15,22,23,24,30a,31,34,37,38b,40(=45),46_stata,46_spillovers,47,48,51,52,53 | 真实告警须当真; 本批多为设计内优雅降级/前视掩码守卫 |
| **真实 validation** | 35,38,39a | κ 哨兵 / t 检验 / T=2 退化披露 |
| **pytest 夹具** | 18,32,39,39e,39f | 全部 ERROR/WARNING = 故意构造的 fail-loud/负路径用例, 良性 |
| **dag-import-test** | 14,13,run_pipeline_function,run_pipeline_validation | 仅 import 期单行 banner, main() 从未运行 |
| **graceful-skip** | 27c,33(demo),36 | `NEWS_PROCESS_LLM_OFFLINE=1` 离线 / 缺输入退化 demo |
| **partial-truncated** | 32a(900s 误杀),39c(中途中断),46_spillovers(在途快照) | 无 ERROR 但内容不完整 |
| **mixed (import 覆盖)** | 21 | 2 行=import banner, 非 stage 21 运行 |

归档 2 份 (`archive/2026-06-17/39c·39d`) 均 real-validation, 提供跨日确定性旁证。

---

## 3. 真问题清单 (经对抗批判修正)

> 共 41 份审计、69 条 `is_real_problem=true`。下列已去重/合并跨文件同源, 并已纳入对抗批判 (critic) 对汇总的 3 处事实纠错与 4 处升级。**全部修复均 golden-safe** (validation/diagnostic/日志文本层, 不动主面板生产逻辑、不触 golden)。

### P0 (0 条真实数据缺陷)
- 全批唯一 P0 标记 = `21_tone_llms.log` 的 integrity-flag, 内核是"该 .log 非 stage 21 运行而是 import banner"——属**防误读 P0**, 已在富集 footer 中如实说明, 非代码/数据缺陷。

### P1

**[R1] 测试/import 进程覆盖生产编排日志, provenance 在编排层断裂** ⭐最高优先, 跨 6+ 文件同源
- 文件: `run_pipeline_function.log` / `21_tone_llms.log` / `39e` / `39` / `13` / `14` / `39f`
- 实证: `core/logging.py` `file_mode='w'` 首写截断 + "只留最新一次运行"策略 → 一次 pytest import (RUN_ID=`test_dag_consistency`) 或面板构建 import 即把真实生产日志整段冲成单行。`run_pipeline_function.log` mtime 16:25:59, 早于产出面板的 stage 日志 (23:xx) 约 7 小时, 非同次运行。
- **活体复发 (critic A2)**: 审计进行中 `40_build_panel.log` 在 2026-06-20 00:32 被 PID:25852 再次覆盖 (审计看到的是 PID:10408@23:52) → 审计自身证据基座易失。
- 建议: 测试把 `log_dir` 隔离到 `tmp_path` (conftest monkeypatch); 或对 orchestrator/validation 日志改 run-id 后缀 / `console_only` import 守卫。审计 21/39e/39f 应以 `_runcheck` 快照 + `eval_reports/*.csv` 为准。

**[R2] `34_tone_validation` 两处标签/产物完整性缺陷** (直接导致日志/产物错误)
- ① `tone_validation.py:1431,1657` — `_ss` 轨 4.5a/4.5b 诊断小节标题用二元三目 `'全文' if track=='_full' else '上下文片段'`, 漏 `_ss` 分支 → 日志 `:510/527` 把 `_ss` 错印为 `[上下文片段]`。
- ② `tone_validation.py:2219,2264,2297,2338` — 4 张相关性热力图三轨用**同名**落盘 (无 `_full/_ctx/_ss` 后缀) → `_ss` 覆盖 `_ctx` 覆盖 `_full`, 盘上只剩 ss 轨图, 但日志 12 次声称"已保存"; 而同阶段 CSV/JSON/LaTeX 均带轨后缀, 命名不对称。
- 建议: ① 复用 `:2511` 的三路字典映射; ② 文件名拼 `{track}` 后缀。纯标签/命名层, golden-safe。

**[R3 · critic 升级] 测度单侧退化是测度效度红旗, 不只是"T=2 盘面退化"** (横切, 关乎 P3/BERT 能否成文)
- ① **finbert2 ~98% 正面 / 0% 中性** (`23_tone_berts.log:84/110/136`: 829/0/18, 825/0/22, 827/0/20)。根因: finbert2 以 **labels=2 (二分类)** 加载 (`:43`), 结构上不可能输出"中性", 又系统性偏正面。对照 finbert_cn (labels=3) 给健康的 63.6/36.1/0.2。已在日志披露 labels=2, 但二分类塞进三分类口径 + 极端正偏的**测度效度**含义未被命名。
- ② **39d LM 象征性二分轴三轨 κ=nan** (`39d:17/27/37`): mask 后 substance 概率 max 仅 0.278 (< 0.5 二分阈值) → 象征性轴恒为常量 → κ 数学未定义 (代码常量轴守卫正确置 NaN)。这意味着 **LLM 几乎从不把任何文章判为"象征性"**, P3 (substance 论文) 核心二元构念在当前阈值下单侧坍缩; T=18 若阈值不变会照样坍缩。
- 建议: 不可一律以"等 T=18"免责。须 (a) 复核 finbert2 二分类→三分类 label-map 是否对本语料定标错误; (b) 复核 substance 0.5 阈值是否对该 LLM 输出分布 (集中 0.27–0.46) 错标定; (c) 论文 §3.4 改用同时报告的 Spearman ρ 作方向证据并披露 κ 不可估之因。

### P2 (按主题合并)

**[R4] `34_tone_validation` 判读逻辑/口径缺陷** (4 条同篇)
- ① `:132/319/504` "需先运行阶段23"——**这是 producer/consumer 后缀口径错挂, 非死代码** (critic A3 纠正汇总): stage23 写 `bert_num_windows_{track}` (带轨后缀, `23:62-64` 实证), stage34 `:1221` 查无后缀 `bert_num_windows` → 永不命中, 窗口数分层永不执行。修法 = 改 `f'bert_num_windows{track}'` (对齐后缀), 不是删 stage34 检查。
- ② `:136/323/508` Δα 单向判读: 仅 `delta>0.10` 报警, `_full` 轨 `Δα=−0.227` 反向大缺口却打"✓ 仍稳健"。改 |Δα| 双向评估。
- ③ `:213/398/586` 多数投票模板写死"(如'中性'占绝大多数)", 真实分布 96–98% 偏**正面**, 方向相反。改众数类别动态填充。
- ④ `:166/179/538` ECE 被 `conf=0` 尖峰主导, `conf=0` 高度可疑为失败解析回退被编码为 0。剔为 invalid 并注明语义。

**[R5] `38_media_diversity` 已评级家数语义 bug (污染 Excel) + 6 次复发** (critic B4)
- `media_diversity.py:475` `rated_media = sum(1 for t,c in tier_counter.items() if 'Tier 6' not in t)` 统计的是 **Tier 类别数 (恒=4)** 而非媒体家数; `unrated_media` 却是真家数 → 口径不对称, `:82` 报"已评级 4 家 (2.4%)" 与同段 Tier2-5 合计 85 家 (≈51.8%) 直接矛盾。该错误占比经 `result['metrics']` 写入 Excel "跨阶段总览" sheet, **不止日志文案**; 且该分析块对 6 个语料各跑一遍 → bug **复发 6 次** (`:31/188/342/486/630/774`)。
- 建议: 改 `rated_media = sum(tier_counter[t] for t in tier_counter if 'Tier 6' not in t)`。论文"样本代表性"引用该 Excel 前必修。validation-only, 不触 golden。

**[R6] `33_news_llms_evaluation` demo_mode 标签/provenance 缺陷** (2 条)
- `:371 vs 363`: sentiment ICR 同篇 `n=0` vs `N=200` 自相矛盾 (`llms_evaluation.py:1495-1496` demo 分支只重赋 `n_both_ver` 未重赋 `n_both_sen`, `:2199` 用后者)。
- `:18-19` header 写 "real data" 实为合成数据 (后文 `:22/365/369` 纠正); 缺 seed=42 / 输入 xlsx sha256。
- 建议: demo 分支对称重赋 `n_both_sen` (或 `:2199` 改用 kappa result dict 的 `n_samples`); 退化时把 seed/合成标志写入摘要。

**[R7] `23_tone_berts` 报告体陈旧字符串** (3 条, 纯日志文本)
- `:987` strict CPU 模式 (USE_AMP=False) 仍打"FP32 (AMP推理时动态转换)" (只判 DEVICE 是否 cuda, 未判 USE_AMP)。
- `:991` 打"多模型并行加载: 已启用 (共享分词)", 与 g-berts-01 修复 (各模型按自身 tokenizer 分窗) 矛盾, 实际窗口数逐模型不同已自证。
- `:1133` 预加载提示"(FP32, AMP推理)" 同 strict 模式不符。
- 建议: 三处与 `USE_AMP` 联动或去掉 AMP 字样。纯日志层, golden-safe。

**[R8] `22_tone_words` verdict 写死区间与实测数字不符** (`tone_words.py:1944`)
- verdict 硬编码"符合预期 0.998–0.999", 但本次实测三轨 `corr(msent, msent_negonly)` = 0.9940 / 0.9872 / 0.9831 全部低于该区间; 代码"稳健"判据实为 `r>=0.95`。区间字样无论 r 落点都照贴 → 文案声称区间与展示数字冲突。
- 建议: 改动态描述 ("r>=0.95 即稳健") 或注明 0.998–0.999 为 T=18/bank-year 聚合参照值。golden-safe。

**[R9] `37_dict_coverage_audit` 健康阈值双标准** (`dict_coverage.py:749` vs `:369`)
- banner/结果分析用 `|差异|<3pp` 为健康, 但问题清单门槛是 `abs(effect_size)>=5.0` → 3–5pp 灰区会"判不健康却不列入问题"。本次 −29pp 远超两阈值未显形, 属潜在代码层瑕疵。统一阈值。

**[R10] LOO-IV/弱工具 FDR/效应量缺失 + 大 N 显著性** (`35:161/183/195` · `52:76/200`)
- `35` 全部 15/15 配对 t 检验 p<0.05 (n=847 下 0.01–0.03 微差必然显著), 无 FDR、无 Cohen d。`52` LOO-IV 弱相关系 T=2 退化产物。建议报 Cohen d + FDR; 生产 T=18 用 KP rk F / Stock-Yogo 实测工具强度。

**[R11] `40_build_panel` staleness 列因代际守卫被跳过** (`40:639`)
- `18_staleness_panel.parquet` 早于上游 13/24 → loud-warn 跳过 merge (守卫行为正确, fix omni-g-runner-16) → 本次面板缺 staleness 列族。面板重生 SOP 须显式列入"先重跑 stage 18 (确保 faiss-cpu/datasketch 已装) 再重建面板"。

**[R12] 复现要素普遍缺失** (跨 ~15 份真实生产/validation 日志, 最高频共性)
- 日志声明"逐位可复现"却正文不含: 输入 parquet sha256/行列数、关键库版本 (jieba/torch/transformers/sklearn/scipy/datasketch/networkx/pandas)、git commit、(涉随机的) random_state、`OMP_NUM_THREADS`/`NEWS_PROCESS_LLM_OFFLINE` 取值、词典版本哈希。当前确定性靠外部 SOP + 本地缓存兜底, 而非日志自证。
- 特例 `30a:7 vs 24` (critic C2): banner 称"revision 钉死保证逐位可复现", provenance 行却写"model_revision=(未钉死)" → **同一文件 banner 自相矛盾**; `config/features.yaml::embedding_robustness` 无 revision 键。须在生产重生前钉死 HF commit hash, 或先弱化 banner 文案 (否则是主动误导)。
- 建议: 统一在各 stage 收尾打 "input sha256 + 行列数 + 关键库版本 + seed + OMP_NUM_THREADS"。纯日志增量, golden-safe。

### P3 (代表性, 非穷举)
- **[R13] `core/dag.py:356` 注释"4 个阈值" vs 代码/日志 5 阈值** (`dedup_threshold.py:267` thresholds=5 个)。改注释 4→5。
- **[R14] `dedup_threshold.py:214`** 标"生产去重阈值 (config.yaml)" 实为 `config/preprocessing.yaml:248` (config.yaml 是 legacy stub)。改标签。
- **[R15] `32a` 超时描述漂移**: DAG 实际 `timeout=43200s/12h` (`dag.py:361`), 但注释/validation.yaml/FINDINGS 残留 7200/2h/2.5h → 正是本次 32a 被 900s 卡帽误杀的同源认知误差。统一为 12h。
- **[R16] `12b` 小样本警告口径混排** (`:18`): 行数用过滤前 1168、银行数用过滤后 113 (1168↔117 家, 1125↔113 家)。统一口径。
- **[R17] `15_article_policy_alignment:5`** banner 标 cosine 值域 0–1, 实际 −1~1 (实测 0.18–0.88)。改 banner。
- **[R18] `47_network_brokerage:16` fire_sale 恒为常量 0**: 2018 industry_neg_shock 全 0 → 乘积恒 0, 无零方差检测。加零方差 WARNING; 生产 T=18 移除。
- **[R19] `40_build_panel:241` 变量名超长 33 字符** `exc_jiang_2021_score_negonly_full` (> Stata 32 上限)。确认写前三元组唯一性断言覆盖或加 `negonly` 缩写规则。
- **[R20] `run_pipeline_validation.py:31` docstring 误把 Carlson&Burbano 挂 stage 36** (实为 stage 33)。订正 docstring。
- **[R21] 代码注释 N≈9000 vs 盘面 T=2** (`lexical_discriminant_validity.py:65` / `core/dag.py:431`): 应标 9000 为 T=18 全量目标规模, 非当前盘面 (172 行→mask 62 obs)。

---

## 4. critic 升级主题 — 测度单侧退化 (顶刊一审会直接发问)

汇总把 finbert2 98%正面 / 39d substance 坍缩 / 51 证伪零反例分别归入"4 findings 之外 / benign-by-disclosure / B 级通过", 三者叠加指向**未被命名的系统性问题: 多个情感/构念测度在当前语料上单侧退化** (几乎全正面 / 几乎无象征性 / 永远支持 H1)。顶刊审稿不接受"等 T=18 再说", 会问"为何 T=2 分布已病态, 凭什么相信 T=18 自愈"。
- **51_falsification (262KB/2181 行) 的"全绿"风险** (critic B3): `grep -c ERROR|WARNING`=0; 真实 H1 判读仅 `:198-228` (effective n=103, 8 个 |r| 全 0.036–0.11, 无一例外 "<0.30 弱相关→支持 H1")。日志体积虚高源于把整段 Stata `.do` 模板灌进 `.log` (易被"行数多=审得透"误导)。须复核 |r|<0.3 在 n=103 下的功效, 以及是否存在任何配置能让它"不支持 H1" (否则是 confirmatory theater)。

---

## 5. 跨文件交叉问题 (X8 已撤销)

| 编号 | 内容 | 裁决 |
|---|---|---|
| **X1** | 面板行数 172 vs 176 | 日志 (86 银行×2=172) **正确**; CLAUDE.md:53/302 "~176 行" 陈旧待订正 (critic C1: 锚点用 `24:23 共86家` + `40:99 86×2=172`, **勿写无据的"88→86"叙事**) |
| **X2** | 文章数 1170/1168/1125/847 | 不同口径/快照, **非矛盾**: 1170 历史小样 → 1168 (12 关键词金科) → 1125 (12b 过滤后) → 847 (verified) |
| **X3** | stage21 `_ss` 缓存状态 | 日志/MEMORY (已播种, 离线 0-miss 可复现) 正确; CLAUDE.md v3.9.0 "ss 须付费首跑" 滞后待更新 |
| **X4** | 版本号 v3.5.1/v3.7.0/v3.9.0 | **非 stale**: 各阶段"引入版本"冻结锚, 非项目当前版本 |
| **X5** | radius 网格 0–2 vs 0–3 | CLAUDE.md:21 (0–2) vs `filtering.yaml:80` (0–3) 文档不一致, 统一为实现 |
| **X6** | Bybee 2024 JF vs RFS | 日志/代码 (JF) **正确**; `config/v2_3_implementation_constants.json:111` (RFS) 残留待清 |
| **X7** | 产物 mtime 早于日志运行时间 | 良性: runcheck 后"数据从备份还原原盘", logs/ 未还原; 因确定性, 旧盘产物与日志数字逐位相同, 非造假 |
| ~~X8~~ | ~~编排时序倒置 (46 早于 45)~~ | **❌ 已撤销 (critic A1, 主控亲验)**: `46_stata_export` 启动 23:52:34、`51` 启动 23:52:36, 均在 23:52 生产 stage45 完成**之后**; 汇总误把 stage45 的**启动**时间当成 46 的**完成**时间。当前 `40_build_panel.log` 的 00:32 是**另一次** PID:25852 重建, 与 23:52 生产链无关。**DAG 顺序正确, 无倒置。** |

---

## 6. 良性披露项 (`is_real_problem=false` — 供顶刊读者明确非缺陷)

- **离线 $0 守卫**: `36`/`27c` WARNING、`33` demo、各 runcheck 副本头部空 API-key GBK mojibake — 全部 `NEWS_PROCESS_LLM_OFFLINE=1` + 空 key 预期产物, 在线全量跑不触发。
- **pytest 夹具 fail-loud**: `18` 5 ERROR (域降级断言)、`32:32` 缺文件 ERROR、`39e/39f` 缺列/小样本跳过 — 故意构造的负路径用例, 生产不触发。
- **设计内方法学披露**: `24` max_features=10000 截断咬合 (omni-g-herd-02)、`40` DiD/Bartik 前视掩码 NaN、`finbert2` 全 NaN 优雅跳过 (FINBERT2_MODEL_DIR 未配)、`51` 地理 IV 分子未门控 ATT-2 披露、`12b` 银行 117→113 掉 4 家 (路线 A 纯丢行预期, **但 critic E: 须查掉出的 4 家是否系统性偏向某类银行**)。
- **cutoff 惰性**: `48` 五档 cutoff (0.70–0.90) 结果逐位相同 (omni-g-llm-peer-05, 表注须声明 cutoff 维度无识别变差)。
- **引用已核验正确**: Fang-Peress 2009 JF 64(5):2023-2052 · Tetlock 2007 JF 62(3):1139-1168 · Garcia 2013 JF 68(3):1267-1300 · Sautner 2023 JF · Jha-Liu-Manela 2026 RFS · Bybee 2024 JF · Hassan 2019 QJE · Han 2024 RFS · Manski 1993 RES · GPSS 2020 AER · HRS 2015 JAMS · Cronbach 1951 · Krippendorff 2004/2018 · Landis-Koch 1977 · Vinh-Epps-Bailey 2010 JMLR 等均交叉核对通过 (排除历史 RFS↔JF / Shapiro↔Kelly 错挂)。
- **待外部核验引用** (唯一): `33` 的 **Carlson & Burbano (2026, SMJ 47(3):699-725)** 未来日期 + 精确卷期 = 经典造假签名, 项目有前科 → 投稿前须 Crossref/DOI 核验, 不可独立确认则降级 forthcoming/working paper。

---

## 7. 可复现性短板与补强 (评级 B−)

1. **日志正文缺自证锚点 (R12, 最普遍)** → 各 stage 收尾打 `input.parquet sha256 + 行列 + 关键库版本 + seed + OMP_NUM_THREADS + NEWS_PROCESS_LLM_OFFLINE`。
2. **测试覆盖生产日志 (R1)** → 测试 `log_dir` 隔离 tmp_path; orchestrator/validation 日志改 run-id 后缀。
3. **SBERT revision 未钉死 (R12/30a)** → 生产重生**前**在 `config/features.yaml` 钉死 HF commit hash; 未钉死前弱化 banner。
4. **BLAS-FP 非确定网络列** (`bank_eigen/harmonic/cfbetween_cent`+clustering) → golden 重生须 `OMP_NUM_THREADS=1 + KMP_DUPLICATE_LIB_OK=TRUE`, 逐位比对**排除**这 4 列 (与既有 SOP 一致)。
5. **截断/误杀须给足时限** → 32a 单跑 ≥2h (实际 ~80min, 被 900s 误杀); `39c` 中途中断未产出 (盘上 39c 产物仍是 06-17 旧跑)。run-check 须据实标注未完成阶段。

---

## 8. 审计自身的局限 (诚信披露 — critic A2/E)

- **证据基座易失**: 审计与富集进行中 `logs/` 仍被后台 stage 重跑覆盖 (`21`/`40_build_panel` 在 06-20 00:32 被 PID:25852 重写)。为此本次已把 39 份当前日志**固定快照**到 `_logaudit_20260620/logs_snapshot/`; 后续若要第三方重放, 应以快照为准。
- **未做受控重跑 + sha diff**: 本批反复声称"逐位可复现"但未在 `OMP_NUM_THREADS=1` 下对某确定性阶段 (如 30a/22) 受控重跑并逐列哈希比对 (归档 39c/39d 仅跨日"旁证"非受控重放)。这是 CLAUDE/MEMORY 已记 SOP 但本批未执行的角度。
- **golden 与当前盘同步状态未裁定**: `51:636/645` 明确 `ft_vol_prov/city 不存在 (golden 未重生)`, 且 `40_build_panel` 已被覆盖 → 当前 `data/processed/` 能否过 `test_panel_reproducibility` 本批未给结论 (投稿前最硬闸门)。

---

## 9. 可执行修复清单 (golden-safe, 待 greenlight)

> 全部为 validation/diagnostic/日志文本层, **不动主面板生产逻辑、不触 golden**。本报告**仅审核与建议**, 未改动任何生产源码 (任务为"评审/审核/验证"); 如需逐项落地请确认。

**A. 纯日志文本/标签/注释 (零行为·零数值变化, 最安全)**
- `tone_validation.py:1431,1657` `_ss` 标签三路映射 (R2①)
- `tone_berts.py:987,991,1133` 去/联动 AMP·共享分词陈旧字样 (R7)
- `tone_words.py:1944` verdict 区间动态化 (R8)
- `tone_validation.py:2597` 多数投票示例动态化 (R4③)
- `core/dag.py:356` 注释 4→5 阈值 (R13)
- `dedup_threshold.py:214` config.yaml→preprocessing.yaml (R14)
- `run_pipeline_validation.py:31` docstring 引用归属订正 (R20)
- `30a article_sbert` banner "revision 钉死" 弱化 (R12/30a)

**B. 改诊断输出值 (validation-only, 不入面板/golden)**
- `media_diversity.py:475` rated_media 家数口径 (R5, **同时修正 Excel 总览**)
- `llms_evaluation.py:2199` demo 分支 `n_both_sen` 对称重赋 (R6)
- `dict_coverage.py:749/369` 阈值统一 (R9)

**C. 改行为/产物 (须先确认无下游引用, 不建议随手改)**
- `tone_validation.py:1221` `bert_num_windows{track}` 后缀对齐 (R4①, 会激活原死分层分析)
- `tone_validation.py:2219+` 热力图加 `{track}` 后缀 (R2②, 会从 4 个文件变 12 个, 须查 figures 引用)
- `tone_validation.py:1315` Δα 双向判读 (R4②, 改 verdict 逻辑)
- `47 fire_sale` 零方差守卫 (R18)

**D. 文档 (CLAUDE.md, 与 06-19 comments-docs 审计的"历史锚点"决策协调后再改)**
- CLAUDE.md 176→172 行 (锚 86 银行) / 1170→1168 / `_ss` 缓存"已播种" / radius 0–2 vs 0–3 (X1/X2/X3/X5)
- `config/v2_3_implementation_constants.json:111` Bybee RFS→JF 残留 (X6)

---

## 10. 附录 — 工件位置

- 本报告: `scripts/audit/LOG_FILES_ENRICH_AUDIT_TOPTIER_2026-06-20.md`
- 固定日志快照 (39 份): `scripts/audit/_logaudit_20260620/logs_snapshot/`
- 逐文件审计明细 (41 份): `scripts/audit/_logaudit_20260620/audit_digest.md` (+ `audit_benign.md`)
- 汇总 / 对抗批判: `scripts/audit/_logaudit_20260620/{synthesis,critic}.md`
- 富集块全文 (10 份 header+footer+corrections): `scripts/audit/_logaudit_20260620/enrich_blocks.md`
- 工作流脚本: `…/workflows/scripts/logs-enrich-and-audit-wf_eec23a98-048.js` (Run ID wf_eec23a98-048)
