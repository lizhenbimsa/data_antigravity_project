# 八入口第六轮真跑审计与整改执行计划 (2026-07-18)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 基线 HEAD = 3cc89634 (审计取证时点快照; 并发 litanchor 会话其后已推进 HEAD 且工作树
> 持续存在其在途 md 批 — **实施与提交一律以起跑前一刻重取的 git status 实测为准**,
> by-name 仅纳入本计划 §8 逐文件清单, 其余全部排除; R1-3/I6 修订)。
> 运行约束: 每入口墙钟上限 **3h** (用户指令)。全程 `-WindowStyle Hidden` Start-Process
> + 退出码落盘 + tasklist 轮询 (E-2/E-3 教训); 全八入口统一确定性离线 env
> (`NEWS_PROCESS_LLM_OFFLINE=1` / `HF_HUB_OFFLINE=1` / `TRANSFORMERS_OFFLINE=1` /
> `PYTHONHASHSEED=0` / MKL·OPENBLAS·NUMEXPR·OMP=1 / `PYTHONIOENCODING=utf-8`),
> 解释器 F:\Anaconda3\python.exe, cwd=news_process\ (⑦⑧=各自子目录)。
> 审计方法: Wave-A 静态 8 路 (编排器/DAG/config/侧线/轻入口/近期提交) → Wave-V 对抗
> 核验 52 路 (P2 双镜头证伪+独立重推导 / NIT 单镜头) → 逐入口日志层深审 (对照第四/五轮
> 警告族台账, logs/ 被 gitignore 故一律 Bash grep)。

## §1 运行台账

| # | 入口 | 结果 | 墙钟 | 备注 |
|---|------|------|------|------|
| ① | run_pipeline_function.py | ✅ EXIT=0, 16/16✓ | 2439s | 19:50:15–20:30:53; stage21 离线 13,896/13,896 全命中 $0; 00=921.7s/40=842.2s/22=293.1s 三大头 |
| ② | run_pipeline_validation.py | ✅ EXIT=0, 16/16✓ | 702s | 01:05:36–01:17:18; 66/70 离线优雅跳过 (第五轮同带 677s) |
| ③ | run_paper.py | ✅ EXIT=0 | 1.0s | 无参=组合总览, 与历轮口径一致 |
| ④ | 80_placebo_and_alt_anchor.py | ✅ EXIT=0 | 2.2s | |
| ⑤ | 81_stata_data_audit.py | ✅ EXIT=0 | 2.7s | |
| ⑥ | 82_export_stats_excel.py | ✅ EXIT=0 | 1.2s | |
| ⑦ | company_listed_bank/run_pipeline.py | ✅ EXIT=0, 4/4 步 | 2907s | 01:18:31–02:06:56; 01=5.7/02=272.1/03=2181/04=447.6s (第五轮 2696s 同带) |
| ⑧ | company_tax_bank/run_pipeline.py | ✅ EXIT=0, 4/4 步 | 7340s | 02:07:41–04:09:59; 01=53.2/02=783.5/03=4474/04=2028s (3h 上限内; 第五轮 6289s 同带) |

**最终: 8/8 EXIT=0, 全部在 3h/入口上限内。**

环境备注: 起跑前并发会话 (litanchor 第十补编收口, 3cc89634) 的 `pytest -m fast`
(PID 40736, 6.4GB) 于 19:48 退出后才起跑① — 错峰纪律落实; 无陈旧管道锁。

## §2 日志层审计结论 (①–⑥)

- **①**: 0 真 ERROR (` - ERROR - ` 精确匹配 16 阶段 + 40 子日志全 0); WARNING 恰 34 条
  与第四轮白名单①34 条逐族同构零出入 (T=2 退化族/jieba 6-1506/同名副本去重/151→142/
  变量名33×3/one-hot 退化×10/Bartik<50%×6/DiD 不可识别×2/never-treated/75 号代际
  stale-skip[G9 预登记]/fire_sale 零方差)。计数链闭合: 00 census 183 源
  → 9,490 → 11: 5,031 → 12: 1,650 → 13: 1,544 (93.58%≥0.8573 下界) → 14 物化
  (ctx 回退 164, ss 252) → 21 门控 1,005 (65.09%) → 22/23/24 全 1,005 → 25/26 走
  14 号全集 1,544 (设计口径)。面板段: 40 号 220 行×3,442 列 (3,441+low_conf_flag
  by-design), 46 号 dta 3,442 round-trip 无丢行 (35 列缩名处置在场), 51 号
  996+4,009=5,005 anti-join 恒等 → 3,453 列。嵌入/BERT/LLM 三缓存全命中零付费,
  缓存库 29,088 条与剪枝台账逐位一致。
- **②–⑥**: 详见 §2-bis (三路审计回填)。

### §2-bis ②–⑥ 日志审计回填 (3 路完成, 0 立案)

- **②**: 0 ERROR; 16/16✓ 706.5s (=orchestrator 自报耗时合计; 墙钟 702s 见 §1,
  口径差为编排开销, RR1-L3-NIT-1 注); 阶段级 WARNING 20 条去重后全命中既登记九族
  (61 旗标×2/旧版工作台×4/媒体单类/62 输入 10,076/63 demo×2/64 Δα 三值逐位同第四轮/
  66·70 离线跳过×2/67 仅 2 年/71 κ 四哨兵逐位同第四轮); orchestrator 28 条=镜像+71 号
  RuntimeWarning 双通道回显, 0 原生。66/70 三零核验: 零付费零网络零 eval_reports 写入
  (66 四件 mtime 停 07-17 03:02 [E-4 首跑产物], 70 四件停 07-06 18:11)。75 号代际行为
  = D-1 机理左半程如实重演 (① 内 40 号 stale-skip WARNING 既登记 → ② 内 75 重算,
  盘上 75>21, 双值冻结集覆盖)。非立案观察: 72 号 ~579s (占 ② 82%) 回慢至第三轮量级,
  属 N7-R2 已定谳「慢化可自发再现」, 耗时不外推。
- **③**: 组合总览 11 篇清单完整 (8 fully-coded + 3 provisional), 0 ERROR/WARNING;
  库内仅存 3 条 ERROR 均为 2026-07-06 历史窗负例测试 (既登记)。
- **④**: 143 bank-year×29 列审计面板 + sidecar 落盘, 锚 sha 与日志一致, 嵌入同空间
  (1005,4096) Qwen; 警告全属既登记 T=2 安慰剂功效族 (命中<500×15 等)。
- **⑤**: 158 项 = 138 PASS/20 WARN/0 FAIL; 20 WARN 与第四轮 K3「十族白名单」逐族且
  数值逐字相同, 0 新增族; CSV 159 行落盘, 恒等式族 46 项全 PASS。
- **⑥**: 四输入漏斗 9,490/5,031/1,650/1,005 与第四轮逐位相同; 12 sheet 全 [OK],
  Excel 25,267B 落盘; 0 ERROR/WARNING。

## §3 静态审计发现台账 (Wave-A 33 条 × Wave-V 52 路对抗核验)

判定汇总 (L2-5 修订后统一口径): Wave-A 原始 33 条发现 + 台账细分为 **35 个条目**,
52 路对抗核验 **0 条被证伪**; 8 条 PARTIAL 修正已并入。终裁分级: **P2 定谳 15 条**
(D1–D14, D16) + **NIT 定谳 18 条** (N1–N17 + D15[原 P2 降 NIT]) + **处置记录 2 条**
(RC-F3 不修 / RC-F5 文案修并入 E-9)。D/N 编号为原始定级序号, 保留不重排。

### P2 级 (D1–D16)

- **D1 (=A1)** `run_pipeline_function.py:246-247` — `--skip-unchanged` 判据的
  config/资源哈希裸调违反同函数 :217-218「只读不抛」契约 (input_hashes 路径 :284-292
  有 except OSError 防护, 此处裸奔)。触发面 = 文件被锁/权限拒绝 (PermissionError) 或
  exists→open TOCTOU (「被删即崩」不成立 — exists()/is_file() 门挡住, 核验修正)。
  fail-loud 非静默, 仅 opt-in 可达。
- **D2 (=VAL-EXIT-01)** 验证模块 8 处「缺输入/缺必要列」错误分支 `logger.error+return`
  → 子进程 rc=0 → 编排器记✓ → 入口假绿: entity_masking:872-874,
  prompt_sensitivity:1888-1891/1930-1933, tone_validation:2495-2497,
  dedup_threshold:343-346/376-379, decay_sensitivity:1058-1060,
  radius_sensitivity:1288-1290/1304-1309, llms_human:416-418。对照组
  dict_coverage:917-925 与 llms_evaluation:1830/1837 同场景 sys.exit(1), 证明
  fail-loud 是本目录既有规范, 上列为漏网。架空入口「速败」契约 (:273-276)。
- **D3 (=DAG-GATE-1)** `test_dag_consistency.py` 只有 STAGES→registry 单向包含,
  无反向断言/无 len==16 → 删阶段忘删 registry 条目时孤儿键静默漂移,
  CLAUDE.md「OUTPUT_REGISTRY=16」计数不变量无测试等价物。
- **D4 (=DAG-GATE-2, PARTIAL 修正)** 35 个 shim 中仅 4 个 (72/80/81/82) 有盘上
  存在性守卫, 31 个 (含全部 16 个 MAIN 注册 shim) 无; `StageSpec.script ↔ 盘上文件`
  链接与 35 计数本身零 gate。误删时 fail-loud 生产期暴露 (无静默数据风险, 浪费前置
  阶段时长)。
- **D5 (=CFG-01)** `pipeline/preprocess/runner.py:587-590` 配置 provenance 横幅读
  全仓不存在的键 `{min_title,min_content,max_content}_chinese_chars` (真实键
  `title_min_length/content_min_length/content_max_length`), 横幅恒打印硬编码默认
  2/100/10000 — data appendix 供数面与真实口径可静默不一致 (当前值恰等默认故潜伏)。
- **D6 (=CFG-02)** `sentiment.yaml:86-88` `pos_threshold/neg_threshold` 只被验证 65
  消费 (radius_sensitivity:148-149), 生产 22 不读 (tone_words.py:919 函数默认参数,
  调用点 1504/1654 不传) → 改键即验证/生产静默分叉, 65 自称「与 22 逐行对齐」失效。
- **D7 (=LST-F1)** `tests/test_company_bank_altagg.py:274` 仍单值锚
  `assert disk == treg.EXPECTED_REGISTRY_SHA256`, 未纳入 3938a2df 双值冻结集
  (tax 侧 :261 已改 in FROZEN) — 第五轮修法四文件清单遗漏 listed altagg,
  「杜绝来回翻红」目标在 listed 臂未达成。
- **D8 (=LST-F2)** listed `03:1207-1212` pair stale 校验只锁 registry_sha256 一把,
  缺 04:838-844 的 `input_fingerprint` 第二把 → 21_full 重生而 registry sha 不变时
  03 静默混代产互验报告 (日志却称「同代」), 同盘面 04 会 SystemExit。tax 03 同病
  (实施时核对行号)。02 banner「步骤 03 启动双向校验」文档承诺落空。
- **D9 (=TAX-RP-01+LST-F4)** 两侧线 docstring 用法示例 `--steps 02,03` 违反同
  docstring 上文「重跑 02 须补跑 04」级联义务 (banner 已改 02,03,04, 证明漏改);
  orchestrator `_run` 无「02 in ran 且 04 not in ran」stale 告警分支 (唯一级联提醒
  在 `if "04" in ran` 内 = 只在义务已履行时打印)。核验降格意见: 运行时三重缓解在场,
  但文档→操作通道真实, 维持修。
- **D10 (=TAX-RP-02)** 两侧线 `_log_registry_anchor_status` 级联文案 (a) 系统性漏 04
  (自述证据链四级含 04); (b) 失败路径按成员资格判「已级联」— 02 失败时为假陈述
  (tax :658/:667-668, listed :600/:609-610)。
- **D11 (=A81-F1)** `pipeline/audit/stata_audit.py:1130-1131` 40+51 双缺 →
  audit_results=[] → 空 DataFrame 取 'status' 列 KeyError 崩溃; :1159-1161 专设
  空结果守卫在其后不可达死代码; CSV 不落盘。
- **D12 (=A81-F2)** 同文件 :1078-1082 主面板 40 缺失仅 logger.error 不记 FAIL 项
  → 51 在且无 FAIL 时 main 返 0 — 主面板未受检却报「通过」, 与 banner「FAIL=必修
  硬错→退出码 1」契约不一致。
- **D13 (=A82-F3)** `pipeline/audit/stats_excel.py:193-194` `read_parquet(columns=)`
  下推后, 缺列时 pyarrow (21.0.0) 抛 ArrowInvalid 直接崩, :199-202 缺列警告跳过守卫
  成死代码 — 与 docstring :25 「字段列不存在则警告跳过」契约矛盾。
- **D14 (=A82-F4)** 同文件 :182 `pd.ExcelWriter` 构造即截断输出 xlsx → 四输入全缺
  (0-sheet close 抛 IndexError) 或读盘异常时旧良品 Excel 被毁 (实测残留 ~3.3KB 损坏
  文件)。D13 使缺列场景也走此毁产物路径 (触发面比原述更宽)。
- **D15 (=RC-F1, 降 NIT 定谳)** `FILES_WHITELIST_ANCHOR` 13→14 (49c87f66) 与断言
  13→14 (3cc89634) 不同批 → 49c87f66/5f917e35/1b9704d0 三提交上全量 pytest 该 gate
  必红 (历史红窗, HEAD 已自洽)。**无代码行动** (历史不可重写), 仅台账登记 + 流程纪律
  (锚计数与断言必须同 commit)。
- **D16 (=RC-F2)** `annual_reports/baidu_asypaddle_ocr.py:272` OCR 毒丸判据
  `os.path.exists` 未修 (1b9704d0 仅删毒丸文件): download_results_text 全失败静默
  返空 (:230-234) → save_text 写 0 字节 md (:239-244) → :272 存在即永久 skipped。
  再生通道开放 (07-17 清理会话已知待办, 本轮授权范围内修)。

### NIT 级 (N1–N17)

- **N1 (=A2)** 编排器预清理失败仅 warning + 成功核验只查存在性 → 双条件叠加的窄陈旧
  产物放行通道 (run_pipeline_function.py:846-850/:862-872)。
- **N2 (=A3)** generate_pipeline_summary 失败 logger.error 但 exit 0 + 成功横幅 —
  「ERROR 级+整体成功+exit 0」三者不一致 (:883-888)。
- **N3 (=A4)** core/locking.py:252-258 _cleanup 删 sidecar 无属主校验, 窄竞态下删掉
  新持锁者 sidecar → 诊断退化 (互斥不受影响)。
- **N4 (=VAL-EXIT-02)** run_pipeline_validation.py:290-292 ⏭ 标记 (elapsed==0.0 且
  success) 不可达死分支; 66/70 离线跳过在汇总表与真跑不可区分。
- **N5 (=VAL-EXIT-03)** 旧编号残留承重注释: run_pipeline_validation.py:274「36 依赖
  21」(36→66); entity_masking.py:813「阶段 36」; prompt_sensitivity.py:1724-1725
  「阶段 39」(→70)。
- **N6 (=DAG-GATE-3)** CLAUDE.md 称 test_dag_consistency「强制无重名」但无 STAGES
  列表 script 唯一性断言 (现状无重名)。
- **N7 (=CFG-03)** preprocessing.yaml:6/:8 `fasttext_model_path`/`min_lang_detect_length`
  死键 (全仓 *.py 零消费, 与 lid.176.bin 悬空互证)。
- **N8 (=CFG-04)** `ensemble_method` (sentiment.yaml:23) 与 `aggregation_frequency`
  (panel.yaml:24) 死键且无「仅作记录」标注 (对比 enabled/compute_* 族均有)。
- **N9 (=CFG-05, PARTIAL 修正)** policy_alignment.py:159 死读不存在键
  'policy_alignment' 随即被 :169 覆盖 — 仅此一点成立; policy_similarity.py:329
  文案指的是共享实现模块非配置节, 不改。
- **N10 (=CFG-06)** policy_similarity.py:338 provenance 读不存在顶层键
  `embedding_model` 恒打印 '(default)', 与 _lg 轨打印真实 model 不对称。
- **N11 (=CFG-07, PARTIAL 修正)** validation/threshold.py:542 读不存在 'project' 节,
  版本恒取默认字面量 — 当前值恰正确 (两轮 sweep 均同步过), 问题是「伪 config 驱动」
  误导写法本身。
- **N12 (=CFG-08, PARTIAL 修正)** 真正完全无 YAML/schema 声明的仅 `num_workers`
  一键 (runner.py:296); auth_probe_timeout 有 schema 登记, request_spacing_seconds
  validation 侧有声明 — 原发现范围收窄。
- **N13 (=LST-F3)** F8 原子写覆盖缺口: listed 02:1702 pair 长表 (「被删加权列唯一
  重构载体」) 直写终路径; 03 七长表/互验 md/codebook 整文件重写同为非原子。半写
  parquet 下游 footer fail-loud, 无静默数据通道。
- **N14 (=TAX-RP-03)** tax 03:201-202 budget 建议文案停留 v1「≈500M」, orchestrator
  注入 v2 默认 1.0B (run_pipeline.py:48/:721, README:75)。
- **N15 (=E80-F5, PARTIAL 修正)** 无 sys.path 注入的编号 shim 实为 3 个:
  14_materialize_ctx / 46_stata_export / 80_placebo_and_alt_anchor (非「80 唯一」);
  editable install 下不触发, 裸环境 fail-loud。
- **N16 (=RP-F6)** run_paper.py `_EXIT_CODE_MEANINGS[2]`='未知 paper_id' 但 argparse
  用法错误同样 SystemExit(2) → 取证日志错标原因。
- **N17 (=RC-F4)** 两侧线 run_pipeline 收尾判读只认单一主锚: 激活代 (双值冻结集内
  合法世代) 盘面下 WARN「须 bump EXPECTED_REGISTRY_SHA256」— 指引与冻结政策相反,
  照做即重演 D-1 (3ccd5df4 教训)。
- **(不修记录) RC-F3** 3cc89634 提交信息叙述的 clean_text/fix_caps「代码修复」无仓库
  载体 (一次性 agent 工具链) — 登记防复发风险, 本轮不建闸 (content-QA 正则误伤风险
  大于收益, 下轮补编时人工复核)。
- **(不修记录) RC-F5** batch_longdesc_gate.py:14/:73 与 admit_new_dois.py:288
  「874 白名单」陈旧字面 → 归入 WP-E 文案批。

## §4 整改工作包 (全部 golden-safe: 测试件/日志层/审计 CLI/守卫层, 零生产数据字节影响)

> ⚠ **实施起点闸 (R2-MAJOR-1)**: 全部 WP (尤其 WP-D) 一律待 §1 ⑦⑧ EXIT 码落账后
> 启动; 禁编辑任何在跑入口的文件面。§6.4 fast A/B 基线 = 实施第 0 步 (任何编辑前)。

### WP-A 主编排器与锁 (news_process 主线, 生产代码但纯守卫/日志层)
- **A-1 (D1)**: run_pipeline_function.py:246-247 包 try/except OSError → 保守
  `return False, "config/资源哈希无法核验 (...), 保守重跑"` — 镜像 :284-292 既有范式
  (返回形态 tuple[bool,str] 与 :210 签名一致, R1 镜头1 已核)。
- **A-2 (N1, I3 修订)**: 预清理 os.remove 失败时记录 `{path: mtime_ns}` — 记录侧
  `os.stat` **必须再包 try/except OSError** (except 分支内文件可能已消失 [TOCTOU
  FileNotFoundError], stat 失败 = 视作已清理不记录, 绝不让守卫自身冲出预清理循环);
  阶段成功后复核: 置于既有 missing_outputs 判失败**之后**, 复核 stat 同样包
  try/except (缺文件已由前守卫判负, 直接跳过); mtime_ns 未变 → 改判失败。为可测试性,
  预清理与复核各抽为模块级小函数 (`_precleanup_stage_outputs` / `_stale_outputs_after_success`)。
- **A-3 (N2)**: 摘要生成失败 logger.error → logger.warning (摘要=附属产物, 与 exit 0
  语义对齐)。
- **A-4 (N3, R2-MINOR-1 修订)**: locking.py _cleanup 删 sidecar 前核对首行 PID ==
  self.pid, 不符则跳过 (读/解析失败按不符处理, 保留 sidecar)。同批把同款属主校验
  镜像进 tests/test_pipeline_lock_standalone.py 的内联副本 _cleanup (该副本自述
  「与生产同步」, 不镜像即契约破裂)。
- **A-5 (N5, L2-6+R2-1+C2-NIT-9a 修订)**: **5 处**旧编号: run_pipeline_validation.py:274
  (「如 36 依赖 21」36→66), entity_masking.py:2 (docstring「阶段36」→66, 无空格写法),
  entity_masking.py:813 (36→66), prompt_sensitivity.py:1723 (「同阶段 36」→66),
  :1724-1725 (39→70)。完工判据: `grep -nE '阶段 ?3[0-9]|如 3[0-9] 依赖'
  run_pipeline_validation.py validation/entity_masking.py validation/prompt_sensitivity.py`
  清零 (空格可选模式, R2-1 修正)。
- **A-6 (L2-3, R2-NIT-1+R2-5 修订)**: 新建 tests/test_orchestrator_guards.py (fast):
  ① monkeypatch **news_process.core.data_versioning.compute_config_file_hashes**
  (rpf 内为函数级 import, rpf 模块无此属性) 抛 OSError → _stage_skip_unchanged_is_safe
  返 (False, 含「保守重跑」); ② 参数化三子场景: (a) remove 抛 OSError + stat 正常 →
  记录成功, 复核 mtime 未变 → 判 stale; (b) 同 (a) 但 mtime 已变 → 不判; (c) remove
  抛 + 记录侧 stat 亦抛 → 不记录、循环不冲出; ③ PipelineLock: sidecar 首行他人 PID
  → _cleanup 保留, self.pid → 删除。

### WP-B 验证阶段 fail-loud 化 (D2; R1-1/L2-1/I7 修订: **12 段 checklist / 8 模块**)
逐条 `logger.error+return` → `sys.exit(1)` (镜像 dict_coverage:917-925 先例), 完工判据
= 下表逐行勾销 (行号按内容定位, ±5 漂移容许):
1. threshold.py:577-580 (阶段00输出缺失; **R1-1 补入**, 模块 :78 已 import sys)
2. entity_masking.py:872-874 (输入 parquet 缺失)
3. prompt_sensitivity.py:1888-1891 (输入 parquet 缺失)
4. prompt_sensitivity.py:1930-1933 (必要列缺失)
5. tone_validation.py:2495-2497 (22/23 双缺)
6. dedup_threshold.py:343-346 (回退输入缺失)
7. dedup_threshold.py:369-371 (df.empty; **L2-1/I7 补入**)
8. dedup_threshold.py:376-379 (文本列缺失)
9. decay_sensitivity.py:1058-1060 (候选双空)
10. radius_sensitivity.py:1288-1290 (无输入)
11. radius_sensitivity.py:1304-1309 (缺列, 段内两条 return 均改)
12. llms_human.py:416-418 (三级回退落空)
注意: ① 66/70 **离线优雅跳过分支不动** (by-design, entity_masking:815-820 /
prompt_sensitivity:1726-1731); ② 63 号 _DEMO 纪律不动; ③ 各 shim 裸调 main(),
sys.exit 子进程内直接生效, 无需改 shim。
④ **grep 全量复核处置表 (C2-MAJ-1 预枚举, 勿现场裁量)** — `grep -n 'logger.error'`
8 模块命中按四类处置: 【fatal 化】= 上表 12 段, 不增不减; 【§5 既登记不动】
tone_validation:2865 (§5.9) / entity_masking:1049 (§5.10); 【保护性 fail-closed,
绝不 fatal 化】llms_human:251/:266 + tone_validation:3172 (人工标注保护, 误改会在
有标注盘面打红 61/64 号); 【手动子命令/优雅降级镜像生产, 不动】llms_human
:680/:699/:703/:706/:713/:725/:886 (merge_annotations 手动路径) +
decay_sensitivity:301/:304/:306 + radius_sensitivity 同型降级处。实施时 grep 实测
若出现表外新命中 → 停手按四类归类后记入 §8(b), 不得默默 fatal 化。
⑤ **docstring 契约同步 (C2-MIN-7)**: 随 #5/#12 同批改 tone_validation.py:70 与
llms_human.py:27 两行 docstring 为「…则 sys.exit(1) 速败」; 完工 grep 复核确认
8 模块无与新行为矛盾的 return 措辞残留。
前置条件 (I2): §2-bis 已回填确认 ② 本轮 0 ERROR ⇒ 12 分支本轮 0 触发 ⇒ fatal 化
对现盘面零行为变化 — 已满足。
同批登记不动: radius_sensitivity_llm.py:608 同病但脚手架未接 DAG (--launch 仅打警告)。

### WP-C gate/测试层 (D3/D4/D7/N6)
- **C-1 (D3, L2-10 修订)**: test_dag_consistency.py 单向包含升级为集合恒等
  `set(OUTPUT_REGISTRY) == {s.script for s in STAGES_MAIN}` (+ EXPECTED_NO_OUTPUT_STAGES
  == STAGES_VALIDATION scripts 恒等), 附 len==16 双重保障; 断言失败消息写明放宽路径:
  「若有意新增 MAIN 无输出阶段, 须放宽本恒等式为 ∪-覆盖+互斥并更新 CLAUDE.md 计数
  不变量」。
- **C-2 (D4)**: tests/test_pipeline_shims.py 追加 2 个 fast 静态用例: ① 遍历两 STAGES
  断言 `(pkg_dir/spec.script).exists()` 且非空行 ≤30; ② 盘上 `NN_*.py` glob 计数==35
  且文件名集合 == 32 注册 ∪ {80,81,82} (集合等式同时抓孤儿与缺失)。
- **C-3 (D7)**: test_company_bank_altagg.py:274 改 `assert disk in
  treg.FROZEN_REGISTRY_SHAS` + 注释更新双值冻结口径 (G9 收口后随姊妹件回归单值)。
- **C-4 (N6)**: test_dag_consistency.py 加 script 唯一性断言
  `len(scripts)==len(set(scripts))` 两侧各一。

### WP-D 侧线管线 (D8/D9/D10/N13/N14/N17, listed/tax 对称)
- **D-1fix (D8, I1 修订)**: listed 03 + tax 03 pair 加载处补第二把锁: 读 pair metadata
  `input_fingerprint` (缺失即 SystemExit, 镜像 registry_sha256 分支; 键在两侧 02 写侧
  真实存在 [listed 02:1698 / tax 02:1366, R1 已核]), 在 21_full 载入后复算
  `sha256(f"{size}|{rows}")` 比对, 不同代 SystemExit「先重跑 02」。⚠ **size 必须取
  03 实际载入的 `p_input`** (listed 03:1323 支持 `--input` 覆盖, 04 无此参数 — 逐字抄
  `dp['input']` 会在 --input 覆盖时锁错文件被静默绕过); rows 取 03 自身 len(input21)。
  **tax 03 同有 --input (:1066/:1260, C2-MIN-5 定谳)**, 同款以其 p_input 复算;
  ⚠ tax 侧指纹计算须在 :1263 载入后、:1269 `del input21` **之前**完成 (或先取
  len 存局部变量, R2-6)。防回退锚 (C2-MIN-6):
  tests/test_company_bank_weight_validation.py 与 tests/test_company_tax_bank_
  weight_validation.py 各加 1 个 fast 静态用例 `assert 'input_fingerprint' in
  (SIDE_DIR/'03_….py').read_text(encoding='utf-8')` (断言消息注明「D8 第二把锁读点,
  删除即回退」)。
- **D-2fix (D9)**: 两 docstring 示例 `--steps 02,03` → `--steps 02,03,04`
  (tax :19, listed :16); `_log_run_summary` 加
  `if "02" in ran and "04" not in ran: logger.warning(级联义务提醒)` (两侧对称)。
- **D-3fix (D10)**: `_log_registry_anchor_status` 增参 completed 集合 (调用点传
  step_stats 完成集), 文案改证据驱动:「02→03→04」全链目标 + 按实际完成集写
  已级联/须补跑 (两侧对称镜像)。
- **D-4fix (N17, I8+R2-4 修订)**: 两侧线锚判读增加 `_ACTIVATED` 副锚提取 (新正则,
  主锚正则不动); **两侧目标常量名不同, 严禁互抄** (R2-4):
  listed = `^EXPECTED_REGISTRY_SHA256_ACTIVATED\s*=`, tax =
  `^EXPECTED_TAX_REGISTRY_SHA256_ACTIVATED\s*=`。post_sha == activated 时打「激活代
  合法盘面 (双值冻结集内), 勿 bump 主锚, G9 收口后回归单值」, 不再误导「须 bump」。
  gate 测试 `_expected_registry_anchor()==主常量` 不受影响 (主提取器不动)。防
  fail-open 回归锚: 两侧 lock gate 测试各 +1 用例断言新副锚提取函数能从 gate 文件
  取回 64 位 hex (镜像既有 readable 用例款式)。顺手: 两 gate 测试文件 `_ACTIVATED`
  常量行上补「行格式勿动 (run_pipeline 副锚正则提取)」镜像注释。
- **D-5fix (N13, 最小面)**: listed 02:1702 pair 长表改 .tmp→os.replace 原子写
  (5 行); tax 02 镜像处同改 (实施时核对); 03 七长表/md/codebook 重写不动 (半写
  fail-loud 已兜底, 登记为接受)。
- **D-6fix (N14, C2-MIN-5 定谳)**: 仅改 tax 03:202 一处建议文案 500M→1.0B (与注入
  默认/README 对齐); listed 侧无 500M 文案与 budget 注入 (grep 已核零命中), no-op。

### WP-E config/日志供数层 (D5/D6/N7-N12/RC-F5)
- **E-1 (D5)**: runner.py:587-590 三键名改真实键 (默认回退 2/100/10000 保留), 注释
  标注与 load.py:180-182 双副本同步义务。
- **E-2 (D6, I4 修订)**: tone_words.py 模块层接线 `POS_THRESHOLD/NEG_THRESHOLD =
  SENTIMENT_PARAMS.get(...)` 并在 1504/1654 显式传入 + 日志字面量改插值。接线行与
  radius_sensitivity.py:148-149 **逐字同款 (均不加 float())** — 保住「逐行对齐」;
  yaml 值类型纪律由现值 (0.1/-0.1 数值字面) 保证, 两侧同读
  sentiment_analysis.tone_words 节 (tone_words:179 / radius_sensitivity:142, R1 已核)。
  当前值恒等默认 → 零字节漂移。
- **E-3 (N7)**: preprocessing.yaml 删除 fasttext_model_path/min_lang_detect_length
  两死键 (实施前核 schemas_yaml 无必填引用; 若有则改为注释保留)。
- **E-4 (N8)**: ensemble_method/aggregation_frequency 两键加「仅作记录, 运行时无
  消费者」注释 (对齐 enabled/compute_* 族惯例)。
- **E-5 (N9)**: 删 policy_alignment.py:159 死读行。
- **E-6 (N10)**: policy_similarity.py:338 改读 `CONFIG.get('embedding_api',{}).get('model',...)`。
- **E-7 (N11)**: threshold.py:542 简化为直接字面量 `'v3.16.0'` (去伪 config 查找,
  归入 sweep 批改范式)。
- **E-8 (N12)**: preprocessing.yaml 加注释声明 num_workers 缺省语义 (纯注释,
  零 schema 风险)。
- **E-9 (RC-F5, L2-7 修订, grep 驱动)**: scripts/audit 下全部「874 白名单/874-DOI」
  陈旧字面统一改「FILES_WHITELIST_ANCHOR 全集动态派生」措辞: batch_longdesc_gate.py
  :14/:73, admit_new_dois.py:288, **build_codebook_family_map.py :932/:1421/:1435**
  (L2-7 补) + **tests/test_codebook_longdesc.py:39** (R2-2 补) +
  **tests/test_batch_longdesc_gate.py:26** (R3-NIT-2 补, 「不触真实 874」措辞族) —
  合计 **8 处/5 文件** (全仓 grep 实测全集, 其余 '874' 命中均为 DOI 10.1086/728743
  子串非陈旧字面)。完工判据 = 8 处逐条勾销 + 裸 `grep -rn '874' --include='*.py'`
  复核仅剩 DOI 子串行 (R3-MIN-2 防假阴性), 逐处列名入 §8(c)。

### WP-F 审计 CLI 与 shim (D11-D14/N15/N16)
- **F-1 (D11)**: stata_audit.py:1130 后补空表列骨架 (columns=['category','check',
  'status','severity','detail'] 与 record() 键序一致) → 1159 守卫复活、CSV header-only
  落盘。
- **F-2 (D12, R3-MIN-1 修订)**: 存在性检查**无条件 record 双分支**: 40 存在→
  record('文件加载','40_panel_yearly 存在性','PASS',...) / 缺失→FAIL(CRITICAL);
  51 存在→PASS / 缺失→WARN — 健康盘面 158→**160 项=140/20/0** (与 §6.5-⑤ 判据
  互锁), 缺失盘面 n_fail≥1 → exit 1; CSV 159→161 行预登记。
- **F-3 (D13)**: stats_excel.py:194 读取前 pq.read_schema 求交集, 缺列 print 警告
  + 只读 present 列; present 空则 continue (复活文档承诺的降级语义)。
- **F-4 (D14)**: stats_excel.py 输出改 tmp+os.replace 原子写; 进 writer 前预扫四输入,
  全缺则警告+return (不构造 ExcelWriter, 杜绝 0-sheet 毁产物)。
- **F-5 (N15, R1-4/I5/L2-9 修订)**: 14/46/80 三 shim 补 sys.path 注入 — **同款 =
  81/82 现行款式**: 注入置于任何 `from news_process` import **之前**, 且把顶层
  from-import 收进 `if __name__ == "__main__":` 块 (避免注入死代码与 ruff E402);
  14/46 各补 3 行 (import pathlib/sys + insert) 并移 import, 80 补 2 行 (已有
  import sys)。行数余量安全 (现最长 shim 17 非空行, C-2 的 ≤30 断言相容);
  实施后 ruff 过闸 + py_compile 冒烟。
- **F-6 (N16, R2-NIT-2 修订)**: run_paper.py `_EXIT_CODE_MEANINGS[2]` 文案改
  「未知 paper_id 或 CLI 用法错误 (argparse)」; 顺手同批改
  项目说明书/news_process_项目说明书.html:1382 同款退出码表述。

### WP-G annual_reports (仓库根, 主管道外; D16; L2-8+R2-3 修订)
路径 = F:\WiseSearch\data_antigravity_project\annual_reports\baidu_asypaddle_ocr.py
(git 根下, 非 news_process 内, C2-NIT-9c)。
- **G-1**: :272 改 `os.path.exists(output_path) and os.path.getsize(output_path) > 0`;
- **G-2 (R2-3 修订, 防付费重试风暴)**: 空解析结果**不 raise 入 error 重试队列**
  (raise → status='error' → :406-421 pending 重试 ×max_retries=1000 轮, 每轮付费
  create_ocr_job — 成本放大副作用); 改为返回终态 `status='parse_empty'` + loud
  WARNING, 在 :408 重试收集判据中排除该状态 (计入 failed 统计, 不写 0 字节 md,
  不重试)。瞬态坏帧由既有 error 路径覆盖, 不受影响。
  验证: `py_compile` + import 冒烟 (news_process tests 零引用该文件, R1 已核)。

## §5 刻意不修清单 (逐条理由)

1. **N4 (⏭ 死分支)**: 让 66/70 跳过在汇总层可见需引入 rc=2 协议或产物探测 —
   协议级改动风险 > 表示层收益; 挂后续 (与 D2 的 fail-loud 化正交, D2 不触离线跳过
   分支)。
2. **D15/RC-F1 历史红窗**: 历史不可重写 (禁 amend/force); 台账登记 + 流程纪律。
3. **RC-F3 幻影代码修复**: content-QA 正则闸误伤风险大; 下轮补编人工复核。
4. **radius_sensitivity_llm.py:608 同病**: 未接 DAG 的脚手架, 不动。
5. **03 侧非原子写全量补齐 (N13 余项)**: 半写 parquet 下游 footer fail-loud 已兜底,
   md/codebook 为文档产物; 只修 pair 长表最小面。
6. **CFG-08 的 YAML 实键补声明**: schemas_yaml unknown-field 校验风险, 改纯注释。
7. **G9 级联收口 / 40 号 cross_media mtime 依赖 / stage70 超时收紧 / 38,610 键补种 /
   boilerplate tier2 / golden 重生**: 均沿袭历轮 DEFER (M0/生产机义务), 本轮不动。
8. **cohort 2 慢性红 + jieba 套件 flake**: 第五轮已定谳勿再立案, 处置挂论文侧裁量。
9. **tone_validation.py:2865-2866 (total_methods<2 → return)**: 近不可达二重守卫
   (22/23 双缺场景已被 :2495 [WP-B #5] 硬失败拦截在前; 单缺时 total_methods≥2),
   涉及可选方法组合语义, 保守不动 (R1-1 登记)。
10. **entity_masking.py:1049-1050 (零替换 → return)**: 仅在线付费路径可达, 中途
    退出语义可辩 (已产生部分付费调用后避免半途产物), 本轮不动 (R1-1 登记)。
11. **F-1/F-3/F-4 失败路径无端到端实证**: 修的全是失败分支, ⑤⑥ 健康盘面复跑只证
    不回归; 以代码评审 + py_compile/import 冒烟为凭, §8 诚实披露 (I9 采纳披露路线)。
12. **旧编号残留大同类集 (RR2 镜头B 立案, 挂下轮 grep 驱动批清)**: A-5 只清了 3 文件
    中文形态; 全仓非测试尚有 中文 9 文件 12+ 处 + 英文 'stage 3X' 约 50 处 (含
    llms_human/tone_validation 运行时 logger.info ~35 处直接进 ② 日志、pipeline/audit
    四模块 39a-f→71-75、article_sbert:55、stata_runner:908-909)。修法 = 镜像 E-9 方法论:
    双形态 pattern '(阶段|[Ss]tage) ?3[0-9]' 枚举 → 现行指涉改新编号 / 历史语境白名单
    豁免 (schemas 历史注释/迁移字面量/已移除阶段引用) → 裸 grep 复核入台账; 优先
    运行时 logger 族。零行为影响, 本轮 scope 纪律不动。
13. **stats_excel 两微瑕 (RR2-C-NIT-3 登记)**: 循环体内 import pyarrow.parquet (首次后
    no-op) 与 [:-len('.xlsx')] 切片假定 (config 固定名下成立); 下轮顺手改 splitext。
14. **D8 指纹 size|rows 同尺寸假放行理论残余 (RR2-NIT-3 登记)**: 刻意继承 04 既有
    公式保六站点恒等; 未来强化须六站点同批改并重跑 ⑦⑧ 重产 pair。

## §6 验证方案 (实施后逐项; R1+R2 修订版)

> 顺序约束 (C2-MIN-8): §6 各复跑/重放一律待 ⑦⑧ 进程退出后串行执行 (tasklist 确认
> 无本项目 python/Stata 在跑); §6.4 基线 = 实施第 0 步 (任何编辑前)。

1. 受影响 gate 文件定向复跑 (L2-4/R1-6 补对称): test_dag_consistency.py /
   test_pipeline_shims.py / **tests/test_orchestrator_guards.py (A-6 新增)** /
   test_company_bank_{altagg,cooc_registry,run_pipeline_lock,weight_validation}.py /
   test_company_tax_bank_{altagg,cooc_registry,run_pipeline_lock,weight_validation}.py
   + 新增用例 → 全绿。
2. D2 修法冒烟 (C2-NIT-9b 命令形态): `F:\Anaconda3\python.exe -c "import
   news_process.validation.threshold, news_process.validation.entity_masking,
   news_process.validation.prompt_sensitivity, news_process.validation.tone_validation,
   news_process.validation.dedup_threshold, news_process.validation.decay_sensitivity,
   news_process.validation.radius_sensitivity, news_process.validation.llms_human"`
   零副作用导入 + 定向 pytest (tests/ 引用这些模块的既有用例) 零新红。
3. E-2 零漂移证: **仅走逻辑推演 + 全量 fast 回归** (值恒等默认 ⇒ 字节不变;
   禁重跑 stage 22 对比 — 会覆写 22 号 parquet 违反零字节自述, I4 裁定)。
4. fast 全量 sweep A/B (C2-MIN-8 机械化): 基线 = 实施第 0 步,
   `F:\Anaconda3\python.exe -m pytest news_process/tests -m fast -q` 全量输出落
   scratchpad\fast_pre.txt (**禁 -Last N 截断**, 第五轮教训); 修后同款落
   fast_post.txt; 判据 (R3-MINOR-2 flake 免疫版) = 两文件 `grep -E '^(FAILED|ERROR)'`
   集合的**对称差 ⊆ 慢性红白名单 3 项** {test_cohort_module_exports_84_banks,
   test_cohort_csv_is_committed_in_repo, test_global_jieba_stays_pure_isolation}
   → **0 新增红** (jieba 为间歇 flake, 可只现身单侧, 严格相等会假 FAIL)。
5. 入口复跑 (L2-2/I2 扩; C2-MAJ-2 快照化): **步骤 0 快照**: 复跑前
   `cp logs/*.log → scratchpad\pre_rerun\` + ⑤ CSV/⑥ xlsx 副本。② 以同款离线 env
   复跑 → EXIT=0 + 16/16✓ + 0 真 ERROR; 警告族同构判据 (机械):
   对 pre_rerun 与新 logs 各取 `grep -hE ' - WARNING - ' *.log | grep -v '│' |
   sed 归一化时间戳/耗时 | sort | uniq -c`, diff 为空 (60-75 族)。⑤ 复跑 →
   EXIT=0 且 158 项 = 138 PASS/20 WARN/0 FAIL + **新增 40/51 存在性 PASS 2 项**
   (F-2 改动后应为 160 项 = 140/20/0, 以实测为准登记 §8); ⑥ 复跑 → EXIT=0 +
   12 sheet [OK] + 漏斗 9,490/5,031/1,650/1,005 不变。
6. py_compile/import 冒烟 (L2-8): annual_reports\baidu_asypaddle_ocr.py + 14/46/80
   三 shim + ruff 过闸。
7. notes 重放 (C2-MAJ-3 参数内联): 本轮 ①⑦⑧ 重写 dta 抹掉 notes。主线 =
   scripts/apply_stata_notes.ps1 (判据: stdout 三行对账 ASCII 子串 `applied=3442`×2
   + `applied=3453`×1 + `master_done=True`×3; 3 个 NN_apply_notes_master.log 各含
   行首 `NOTES_MASTER_DONE=`; `r\([0-9]+\)` 非字母边界扫 0 命中; sidecar
   `_notes_applied_fingerprint.json` 三键 n_notes_applied == 3442/3442/3453;
   ⚠ stdout 落盘 GBK, 判据以 ASCII 子串为准; ⚠ 禁用 pyreadstat 复读主线变量级
   notes)。侧线 15 .do = company_listed_bank/data/_notes_inject_*.do (10) +
   company_tax_bank/data/_notes_inject_*.do (5), 串行 Start-Process StataMP-64
   '/b','do' + WorkingDirectory=各自 data\, 先取 Handle; 轮询同名 .log 尾部
   `NOTES_DTA_DONE=` 每 15s, 超时 listed 600s/份·tax 2400s/份; 对账表 =
   SIDEPROJECT_P4_NOTES_INJECTION_RECORD_2026-07-15.md, **分项为准 (逐份 DONE 计数:
   LB 10 份各 24 / TB 32/32/30/23/23); 记录文件的「合计 244」为已知转录滑笔 (实和
   380), 勿以合计为判据 (R3-NIT-1)**; DONE 已见即可按 K7 护栏击杀僵尸 Stata; r(###)
   非字母边界扫 0 命中。机械化参数权威源 = FOURTHRUN 计划 §5 (2026-07-16 md
   :108-112); **:113 的侧线 fingerprint sidecar sha 就地刷新步沿第五轮先例刻意省略**
   (sidecar sha 自 07-16 起不再承担跨轮字节锚, 防下轮以 sha 不匹配误立案; R3 镜头X
   登记)。
8. git status **提交时点重取实测** → by-name 仅纳入 §8 逐文件清单 (并发 litanchor
   在途 md 批与 LLMs_for_FinTech_dic 全排除) → 推送 main。

## §7 评审记录

- **R1 (计划评审第一轮, 3 路: 修法正确性/完备性/对抗风险)**: 3/3 ok_to_proceed
  (附修订前提), 0 BLOCKER / 4 实质 MAJOR / 10 MINOR / 5 NIT, **已全量并入 v2**:
  R1-1+L2-1+I7 (WP-B 同族清扫补 threshold.py:577-580 与 dedup:369-371, 12 段
  checklist 化, 近亲 2 处入 §5); L2-2+I2 (② 修后复跑入 §6.5 + 零行为变化推理);
  L2-3 (A-6 三 fast 单测); I1 (D-1fix p_input 修正 — 逐字镜像会锁错文件);
  R1-4+I5+L2-9 (F-5 注入位置陷阱 + ruff E402 + 81/82 款式); R1-5+I3 (A-2 stat
  双重 try/except); I4 (E-2 逐字同款不加 float + §6.3 禁选项 A); R1-3+I6 (基线/提交
  纪律改提交时点实测); L2-4+R1-6 (§6.1 listed 孪生 gate); L2-5 (§3 口径 35 条统一);
  L2-6 (A-5 第 4 处旧编号); L2-7 (E-9 grep 驱动 +3 处); L2-8 (G-2 显式 raise +
  py_compile); L2-10 (C-1 失败消息); I8 (_ACTIVATED 行保护注释); I9 (§5.11 诚实披露)。
  R1 亦独立实证: D-1fix 键在场 (listed 02:1698/tax 02:1366)、E-2 两侧同读同节、
  D-4fix 正则互斥、C-1/C-2/C-3 当前树立即绿、G 与 news_process tests 零关联、
  全 WP 单 commit 可逆。
- **R2 (计划评审第二轮, 3 路对抗: R1 并入正确性/新鲜对抗/可机械执行性)**: 3/3
  ok_to_proceed, 0 BLOCKER / 4 MAJOR / 10 MINOR·NIT, **已全量并入 v3**:
  R2-MAJOR-1 (§4 实施起点闸 — 待 ⑦⑧ 落账, 禁编辑在跑文件面); C2-MAJ-1 (WP-B 注④
  grep 处置表预枚举四类, 含人工标注保护 fail-closed 绝不 fatal 化); C2-MAJ-2 (§6.5
  快照步骤 + 归一化 diff 机械判据); C2-MAJ-3 (§6.7 notes 参数/路径/对账表内联);
  R2-MINOR-1 (A-4 镜像 standalone 副本); R2-1 (A-5 第 5 处「阶段36」+ 空格可选
  grep); R2-2 (E-9 范围放宽全仓 +tests 1 处); R2-3 (G-2 改终态 parse_empty 防 1000
  轮付费重试风暴); R2-4 (D-4fix 两侧常量名分立 + 防 fail-open 回归锚); R2-5 (A-6
  用例②三子场景参数化); R2-6+C2-MIN-5 (tax 03 --input 定谳 + del 位置约束; D-6fix
  定谳仅 tax 一处); C2-MIN-4 (§8 骨架 + §2-ter 占位); C2-MIN-6 (D-1fix 文本锚宿主
  与断言形态); C2-MIN-7 (WP-B 注⑤ docstring 契约同步); C2-MIN-8 (§6.4 命令形态 +
  防截断 + §6 顺序约束); R2-NIT-1 (A-6 patch 目标全名); R2-NIT-2 (F-6 顺手改说明书
  HTML); C2-NIT-9 (A-5 判据含「如 3[0-9] 依赖」/§6.2 import 命令/WP-G 绝对路径)。
  R2 亦独立实证七攻击面全部不可触发 (tests 零调用 12 个 main / 文本锁不覆盖助手 /
  35 计数现 HEAD 成立 / 文案零测试锁定 / F-1 骨架列序逐字一致 / 新测试导入可行)。
- **R3 (计划评审第三轮, 3 路终审: R2 并入终验/全文一票否决扫雷/自由取证)**:
  **3/3 ok_to_ship (「愿为执行后果签名」)**, 0 BLOCKER / 0 MAJOR / 3 MINOR / 5 NIT,
  已全量并入 v4-final: F-2 存在分支对称 PASS record (三镜头收敛, →160=140/20/0 与
  §6.5-⑤ 互锁); E-9 补第 8 处 tests/test_batch_longdesc_gate.py:26 + 裸 grep 判据
  防假阴性; §6.4 判据改「对称差 ⊆ 慢性红 3 项白名单」(jieba flake 免疫); §6.7
  「合计 244」滑笔括注 (实和 380, 分项为准) + FOURTHRUN :113 sidecar sha 刷新步
  刻意省略登记; §1 ⑦ 行状态同步 (已先行完成)。R3 亦终验: WP-B 注④ 处置表四类行号
  源码逐一属实 (llms_human:251/266 = SystemExit 后盾盲表保护 / :680 族 7 处全在
  手动路径 / tone_validation:3172 = fail-closed 保护); §6.7 参数与 FOURTHRUN
  :108-112 逐项一致; G-2 parse_empty 与 :406-421 白名单式判据接缝可行; §3 35 条与
  §4/§5 双向映射闭合, WP 间行号互斥无冲突改动; A-3 在 ① 编排器不影响 ② 复跑同构
  判据。附注: R2 记录「10 MINOR·NIT」实为 14 个标签 (R3-NIT-3 更正于此, 不改 R2
  原文)。首次运行 R3 因子代理配额瞬断 3/3 error, resume 重试后 3/3 完成 (如实登记)。
- **RR1 (结果评审第一轮, 3 路: diff↔计划双向符合度/修法对抗复证/零副作用与文档自洽)**:
  **3/3 PASS, 0 BLOCKER / 1 MAJOR / 4 MINOR / 8 NIT, 已全量落实**: 50 改动文件 + 2 新
  文件逐 hunk 双向对账零夹带零漏实施; 六路对抗复证全过 (E-2 逐字同款+两调用点+无第三
  处未传参 / WP-B 13 个 sys.exit 与四类处置表双向闭合 / D-1fix 指纹公式六站点逐字恒等
  / A-2 无跨轮误用 / F-4 修后正确 / D-4fix 正则逐字符无互抄); 生产 parquet 零触碰。
  落实项: CLAUDE.md :166/:171 同步 C-1 双向恒等门 (L3-MIN-2); C-1 注释「无注册 parquet
  输出」措辞 (L3-NIT-3); E-2 接线防回退锚入 test_22_tone_words (L2-NIT-1, 即跑即绿);
  §8(a) radius 行号校准 + WP-G 偏离标注 + §2-bis ② 口径注 + §6.5 ② 复跑固有 parquet
  重写入账 (L2-NIT-3/L1-NIT-1/L3-NIT-1/L3-MIN-1); §8(f) 落 constants.json 单独 chore
  处置 (L1-MINOR-1/L3-MIN-3); §8(d)/(f) 占位回填 (L3-MAJ-1, 于提交前完成)。
  记录不动: A-4 standalone 副本省略 else 日志行 (行为已同步, L1-NIT-2); F-4 0-sheet
  奇异组合剩余风险 (§8(e) 已披露, L2-NIT-2); §2-ter 节位置 (加指针即可, L3-NIT-2)。
- **RR2 (结果评审第二轮, 3 路对抗: RR1 落实核验/第七轮视角新鲜对抗/提交前状态)**:
  **3/3 PASS, 0 BLOCKER / 1 MAJOR / 3 MINOR / 8 NIT, 已全量落实**: 唯一 MAJOR =
  本轮 E-9 替换文案自身植入错位计数「1397」(纯锚集实测 1119, 1397=锚∪台账并集;
  重演 874 腐化模式) → 两处计数字面已删 (admit_new_dois:288/batch_longdesc_gate:73);
  §8(d) 标题陈旧已改; §8(f) 已按镜头C 归类回填 (constants.json 单独 chore 处置落账);
  D9 warning 粘连空格 ×2 已补; 旧编号残留大同类集 (~60+ 处双形态含运行时 logger 族)
  立案挂 §5.12 下轮 grep 批清; stats_excel 两微瑕挂 §5.13; D8 指纹理论残余挂 §5.14。
  RR2 亦独立实证: 三 gate 文件 32 passed / CLAUDE.md 新文与断言逐点等价 / E-2 锚
  8/8 绿 / WP-B 残余「优雅跳过」措辞全指向刻意保留分支零矛盾 / 82 shim G1 契约成立 /
  03 双向锁三盘面推演闭合 (规范链无自杀; 单跑 03 且 21 已重生 → SystemExit = D8
  设计意图) / 三 shim docstring 逐字保留 (增量 Edit 非重写) / fix-tag 日期全 07-18 /
  git status 54 项四类归类零无主 / logs 三处 gitignore 不可见确认。
- **RR3 (结果评审第三轮, 3 路终局签核: RR2 落实终验/推送就绪与诚实性清点/自由怀疑)**:
  X/Y 直接签核 (X 五项全过 0 立案, 含 test_batch_longdesc_gate 11 passed +
  test_codebook_longdesc 91 passed; Y 五项全过: 54 项四类归类闭合零无主 / §3 全 35 条
  逐条追至终局落点无一悬空 / 诚实性扫描 7 项指名不利事实全数如实入账另 6 项额外自曝 /
  TBD 残留仅 RR3 自身 / 5 数字锚逐位命中盘面)。**Z 首判拒签 (ok_to_push=false), 抓获
  RR3-Z-MAJ-1**: D-4fix 两 readable 用例裸姐妹 import 单跑假红 (见 §8(d) 补证) —
  按 Z 开出的转签条件 (方案① ≤3 行/文件修复 + 双文件单跑全绿 + §8(d) 入账) 全部
  完成, **转签推送**。Z 另录 2 NIT: §6.1 合跑口径已补注; G9 收口同步站点增至 ~7 处
  (FROZEN 集×2/_ACTIVATED 常量×2/lock 镜像常量×2/altagg 注释), 挂下轮 G9 计划列全
  站点清单。附 RR3-NIT-3 计数口径备查: 8 模块 grep 'sys.exit(1)' = 15 处 (代码级 13
  + docstring 契约文本 2), 下轮复核勿误判。

### §2-ter ⑦⑧ 日志审计回填 (判据同 §2: 0 真 ERROR / 警告族对照第五轮台账 / EXIT=0 / 墙钟 vs 3h cap)

(注: 本节物理位置在 §7/§8 之间系 C2-MIN-4 占位历史产物, 内容归属 §2; RR1-L3-NIT-2 指针已在此声明。)

- **⑦ (2 路审计, 0 立案)**: EXIT=0, 2907s (01=5.7/02=272.1/03=2181/04=447.6s, 第五轮
  2696s 同带 +7.8%)。0 真 ERROR (5 份日志); WARNING 恰 10 条与第四轮 ⑦ 白名单逐条
  同构 (豁免基名×4 / 3 基名缺源列 G8-DEFERRED×4 / 27 号陈旧哨兵 sha 逐字同×1 /
  40 加权列 T=2 退化×1), 新增=0。registry sha=023cdc9158ec52ba… 逐位命中主锚
  (非激活代, 规范复跑预期), 「须 bump」噪声本轮零出现 (INFO「已一致, 免级联义务」);
  01→02→03→04 四点同代锚链闭合 (023cdc91… + pair input_fingerprint a50a9cc2… 贯穿);
  **10/10 dta 字节锚与第四轮逐位相等 (字节级零漂移)**: 主 1,610,634,683 / 七权各
  1,603,484,161 / frozenw 1,606,426,983 / mainbankw 1,617,142,173; 八组内联硬闸+
  批量五闸+DV2/DV5 全绿; 骨架 105,032 行、40 面板 3,442 列口径全程一致; codebook
  02 重写→03 七权章→04 替代聚合章级联序正确; 单实例锁对称释放, tmp+replace 原子写
  在场。
- **⑧ (主循环亲审 + 快扫, 0 立案)**: EXIT=0, 7340s。5 份日志 ` - ERROR - ` 全 0;
  WARNING 01×8 + 02×3 + 03/04×0 (orchestrator 11 条全镜像): 01 = 豁免基名×4 + 3 基名
  缺源列 G8-DEFERRED×4 (与 ⑦ 同构); 02 = 27 号陈旧哨兵×1 + 40 加权列 T=2 退化×1 +
  **B1 单企业占比告警×1 (建碁科技 67.9% = 2026-07-09 刻意加的披露性告警, 裸 2 字
  variant「科技」, by-design 只告警不过滤)** — 全部既登记, 0 新增族。tax registry
  sha=4f580e3fc458be0c… 逐位命中主锚 (非激活代预期); DV2 常量双向锁 9 键通过; pair
  2,082 行 registry 指纹校验通过; 04 双向锁 (sha+input_fingerprint) 通过; 4/4 步
  rc=0, 单实例锁 (F11) 干净释放。

## §8 执行记录 (2026-07-18 实施回填)

### (a) 逐 WP 落点表 (全部落地)

- **WP-A**: A-1 run_pipeline_function.py cur_cfg/cur_res try/except OSError→保守重跑;
  A-2 抽 `_precleanup_stage_outputs`/`_stale_outputs_after_success` 两助手 (记录/复核侧
  stat 双重 try/except) + 主循环接线 + 成功后 stale 改判失败; A-3 摘要失败 error→warning;
  A-4 locking.py _cleanup sidecar 属主校验 (首行 PID==self.pid 才删) + standalone 副本
  镜像同步; A-5 五处旧编号 (run_pipeline_validation:274 / entity_masking:2·813 /
  prompt_sensitivity:1723·1724-1725), grep '阶段 ?3[0-9]|如 3[0-9] 依赖' 三文件清零✓;
  A-6 新建 tests/test_orchestrator_guards.py 6 用例全绿。
- **WP-B**: 12 段 checklist 全勾销 (threshold:580 / entity_masking:874 /
  prompt_sensitivity:1891·1933 / tone_validation:2497 / dedup_threshold:346·371·379 /
  decay_sensitivity:1060 / radius_sensitivity:1291·1308·1312 [RR1-L2-NIT-3 校准后
  实测行号] / llms_human:418 → sys.exit(1) + fix-tag 注释); docstring 契约同步
  tone_validation:70 + llms_human:27; 66/70 离线跳过分支未触碰。
- **WP-C**: C-1 两集合恒等+len==16+放宽路径消息; C-4 script 唯一性新用例;
  C-2 test_pipeline_shims.py +2 用例 (32 注册 script 存在性+thin ≤30 / 35 普查集合恒等);
  C-3 altagg :274 → in FROZEN_REGISTRY_SHAS + 双值冻结注释。
- **WP-D**: D-1fix 双侧 03 第二把锁 (pair_fp 读点 fail-closed + p_input 复算比对,
  tax 侧在 del input21 前) + 双侧 weight_validation gate 文本锚; D-2fix 双 docstring
  示例 02,03→02,03,04 + 双侧「02 无 04」warning 分支; D-3fix `_cascade_note` 证据驱动
  文案 (含 04) + anchor_status 增 completed 参数 + 4 调用点传完成集; D-4fix 双侧
  `_expected_registry_anchor_activated` (分侧常量名) + 激活代「勿 bump」判读 + 双 gate
  件副锚行保护注释 + 双 lock gate readable 用例; D-5fix 双侧 02 pair 长表 tmp+
  Path.replace 原子写 (os 仅函数级 import 故用 pathlib); D-6fix tax 03 budget 文案
  500M→1.0B 对齐 (listed 无同款, no-op 定谳)。
- **WP-E**: E-1 runner.py 三键名改真实键+双副本同步注释; E-2 tone_words
  POS/NEG_THRESHOLD 接线 (radius 逐字同款无 float) + 1504/1654 显式传参 + 2030 日志
  插值; E-3 preprocessing.yaml 删两死键 (schemas 无必填引用已核); E-4 ensemble_method/
  aggregation_frequency「仅作记录」标注; E-5 policy_alignment:159 死读删除;
  E-6 policy_similarity 改读 embedding_api.model; E-7 threshold.py 版本直字面量;
  E-8 num_workers 注释声明; E-9 八处 874 字面全改 (清零 grep 仅剩 DOI 10.1086/728743
  子串✓)。
- **WP-F**: F-1 stata_audit 空表列骨架 (record() 键序一致); F-2 存在性无条件双分支
  record (健康盘面 158→160=140/20/0); F-3 stats_excel pq.read_schema 交集读+缺列警告
  (旧守卫降二重保险); F-4 全缺预扫响亮中止 (return 1, 不碰旧产物) + tmp+os.replace
  原子写; F-5 三 shim (14/46/80) 注入先于 from-import + import 收进 __main__
  (14/46 保持裸 main() 调用约定零行为变化, 80 保持 sys.exit(main()) G1 契约);
  F-6 run_paper _EXIT_CODE_MEANINGS[2] 文案 + 说明书 HTML :1382 同步。
- **WP-G**: G-1 OCR :272 判据补 getsize>0; G-2 空解析 → 终态 parse_empty (不写 0 字节
  / 不入重试队列 [收集判据 ["error","limit_reached"] 天然排除] / 汇总段加计数披露)。
  **刻意偏离登记 (RR1-L1-NIT-1)**: 计划括注「计入 failed 统计」实现为独立 parse_empty
  计数披露行 (error_count 不含之, 不污染 error 重试语义) — 方向合理, 特此标注。

### (b) WP-B grep 全量复核处置

12 段 fatal 化如上; 表外命中按 §4 注④ 四类处置复核无新增类别 (llms_human:251/266 +
tone_validation:3172 保护性 fail-closed 未动; llms_human merge_annotations 手动路径
7 处未动; decay/radius by-design 降级未动; tone_validation:2865 / entity_masking:1049
按 §5.9/5.10 登记未动)。

### (c) E-9 清单

8 处/5 文件逐处勾销: admit_new_dois:288 / batch_longdesc_gate:14·73 /
build_codebook_family_map:932·1421·1435 / test_codebook_longdesc:39 /
test_batch_longdesc_gate:26; 修后裸 grep '874' --include=*.py 仅剩 DOI 子串行 ✓。

### (d) §6 逐项 (§6.1–6.7 已全部回填; §6.8 见 (f))

- §6.1 定向 gate 12 文件 219 用例 100% 通过 0 FAILED ✓ (含 6 处新增/改动断言;
  ⚠ 该数为**合跑口径**)。**§6.1 补证 (RR3-Z-MAJ-1)**: 两 lock gate 新 readable 用例
  首版裸姐妹 import 寄生 altagg 的 sys.path 注入 → 单跑必 ModuleNotFoundError 假红
  (RR3 镜头Z 双向实证抓获, RR1/RR2 合跑口径均漏); 已按方案① 改本地镜像常量+同步
  注释 (严格镜像既有款式), 修后两 lock 文件**各自单跑全绿** (8/8, 9/9)。
- §6.2 八模块 import 冒烟 IMPORT_SMOKE_OK ✓ + test_orchestrator_guards 6/6 ✓。
- §6.3 E-2 零漂移: 逻辑推演 (yaml 0.1/-0.1 恒等默认) + §6.4 fast 回归兜底 (执行中)。
- §6.6 py_compile 14 文件 ALL_OK ✓ + ruff 25 文件 All checks passed ✓。
- §6.4 fast_pre 已取 (4 红 = 慢性红 3 + 并发 WIP 红 1 [test_s2_threshold_is_strict_majority,
  由并发在途 LLMs_for_FinTech_dic/00_LLMs_for_dic.py S2 阈值 1/2→2/3 未提交改动引起,
  正则找不到 `* 0.5` 表达式; 非本会话所致, 该文件在禁触清单]); fast_post — 执行中。
- §6.5 全 PASS: ② 复跑 (05:21:59 起, EXIT=0) 三判据全过 — 16/16✓ (17 成功行含总横幅)
  / 0 真 ERROR / 警告族归一化 diff 空 (WARNING_FAMILY_ISOMORPHIC); ⑤ 复跑 EXIT=0,
  **160 项 = 140 PASS/20 WARN/0 FAIL 与计划互锁判据逐位命中**, CSV 161 行含 2 条新
  「文件加载」存在性记录; ⑥ 复跑 EXIT=0, 12 sheet [OK], 漏斗 9,490/5,031/1,650/1,005
  逐位不变。**入账 (RR1-L3-MIN-1)**: ② 复跑固有重写 10 个非注册验证 parquet
  (72×6/73×3/75×1, 05:35) + eval_reports/61 盲表 — 属 registry 外验证产物的 ② 固有
  行为, 生产 parquet (00–51/80) 零触碰; 下轮评审前提应表述为「② 复跑重写验证侧
  非注册 parquet 属预期」。
- **⚠ E6R 回归实弹 (如实入账)**: ⑥ 首次复跑 EXIT=1 — F-4 首版 tmp 名 `*.xlsx.tmp` 被
  pd.ExcelWriter 扩展名校验拒 (ValueError: Invalid extension 'tmp'); 旧良品 Excel
  **零受损** (崩在 tmp 构造, 原子设计首战即生效); 修法 = tmp 名改 `*.tmp.xlsx` 保
  尾缀, 复跑即绿。教训: ExcelWriter 按扩展名选引擎, 原子写 tmp 命名须保真实尾缀。
  本条同时证明 §6.5「修后复跑」闭环 (L2-2/I2 评审要求) 的必要性 — 若按 v1 计划仅
  ⑤⑥ 健康盘面免复跑, 该缺陷将潜伏至下轮八入口审计。
- §6.4 fast_post 完成: 失败集与 fast_pre **逐条恒等 (IDENTICAL_SETS_0_NEW_RED)**,
  对称差空集 ⊆ 白名单, 0 新增红 ✓。
- §6.7 notes 重放全 PASS: 主线 (06:11 起) — stdout ASCII 锚 applied=3442×2 +
  applied=3453×1 + master_done=True×3 + 收尾行✓; 3/3 master log 行首
  NOTES_MASTER_DONE=✓ (位于 data/processed/, 非 logs/); r(###) 非字母边界扫 0;
  sidecar 三键 3442/3442/3453✓。侧线 (06:19 起) — **15/15 done=True**, 逐份
  NOTES_DTA_DONE 与对账表逐一相等 (LB 10 份各 24; TB 32/32/30/23/23), r(###)=0;
  「合计 244」滑笔未用作判据 (分项为准, R3-NIT-1); sidecar sha 刷新步沿第五轮先例
  刻意省略 (§6.7 登记)。K7 护栏: 僵尸 Stata 按 DONE-已见即杀处置。

### (e) §5.11 诚实披露

F-1 (空表骨架)/F-3 (缺列降级)/F-4 (原子写+全缺中止) 修的全是失败路径, ⑤⑥ 健康盘面
复跑只证不回归不证修复生效; 以代码评审 + py_compile/ruff/import 冒烟为凭, 未做失败
路径端到端实弹 (I9 采纳的披露路线)。另: F-4 的「输入在盘但全列缺失→0 sheet」奇异
组合下 openpyxl 仍会抛 IndexError, 但原子写保证旧产物无损 (残留 .tmp 可人工清),
属可接受剩余风险。stats_excel 全缺分支现返回 1 (旧: None→exit 0) — fail-loud 方向
的刻意行为变化, 与 D2 口径一致。

### (f) by-name 提交清单 (RR2 镜头C 归类 + 提交时点重取终核)

- **入 commit**: 49 个 WP 修改文件 + 2 个新增 (本计划 md + tests/test_orchestrator_guards.py)
  — 提交时以 git status 实测终核, 逐文件 git add by-name。
- **排除 (刻意不提交)**: ① LLMs_for_FinTech_dic/{00_LLMs_for_dic,config}.py — 并发
  会话在途 WIP (S2 阈值 2/3 改动, 其所有权归该会话); ② **v3_5_1_constants.json** —
  ① 真跑运行产物 (仅 stage21_last_run_timestamp 一行), 按 L1-MINOR-1/L3-MIN-3 处置
  **单独 chore(constants) 提交** (镜像 b351721d 先例), 严禁与 WP 改动混同一 commit;
  ③ 并发 litanchor md 批 (若提交时点有新在途)。
