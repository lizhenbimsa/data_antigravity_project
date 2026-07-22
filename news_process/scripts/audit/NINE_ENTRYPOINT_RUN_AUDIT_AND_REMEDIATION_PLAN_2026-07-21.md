# 九入口顺序真跑审计与整改执行计划 (2026-07-21/22, 修订版 r2)

基线: main=`b7b70b08` (fintech_dict.json 607 词换血后首轮全链真跑)。
评审链: 计划 R1 (事实核验) + R2 (完备性/风险) 两路对抗评审已并入 (~1 BLOCKER + 9 MAJOR + 12 MINOR
全处置); R3 = 实施者终审。台账镜像: 会话 scratchpad `run9/LEDGER.md`; 本文件为权威归档。

## §1 运行矩阵 (九入口, 单入口/单次执行 ≤3h 约束全部满足)

| # | 入口 | 模式 | 结果 | 耗时 | 备注 |
|---|------|------|------|------|------|
| ① | LLMs_for_FinTech_dic/00_LLMs_for_dic.py | LLMS_DIC_OFFLINE=1 | EXIT=0 | 12s | 0 ERROR/3 WARNING(2 零温披露+1 历史重试重放); 591 词 AI 认可与基线一致 |
| ② | run_pipeline_function.py | 离线证伪→定点播种→在线回填 | EXIT=0 全16阶段 | 2377s | §2 miss 面; stage21 复验 9423/9423 0 miss |
| ③ | run_pipeline_validation.py | 在线 | EXIT=0 全16阶段 | ~60min | 0 ERROR; 19 WARNING 全命中已知慢性族 |
| ④ | run_paper.py | --list + 11 篇白名单逐篇 (无参默认 --stage all) | --list EXIT=0 + **11/11 EXIT=0** | each ~1230s | 终值见 §1a |
| ⑤ | 80_placebo_and_alt_anchor.py | OFFLINE=1 (全命中 $0) | EXIT=0 | 2s | 833 篇/115 bank-year; ⚠ §4.1 顺序耦合: 产物含「自助银行」placebo 臂=临时口径, S13 决策后须重跑 |
| ⑥ | 81_stata_data_audit.py | OFFLINE=1 | EXIT=0 | 3s | 160 项计数结构保持: **0 FAIL / 18 WARN / 142 PASS** (上轮 20 WARN, 值漂移属换血正当) |
| ⑦ | 82_export_stats_excel.py | OFFLINE=1 | EXIT=0 | 1s | 4 阶段 / 12 sheet |
| ⑧ | company_listed_bank/run_pipeline.py | 全链 01→04 | EXIT=0 | 781s | 01=3.9s/02=77s/03=576s/04=123s; pair 双向锁 ✓; 0 ERROR |
| ⑨ | company_tax_bank/run_pipeline.py | 全链 01→04 | EXIT=0 | 1866s | 03=1423s/04=466s; 0 ERROR; 单实例锁干净释放 |

§1a 终值回填区 (2026-07-22 由九入口执行会话回填):
- ④ 11 篇逐篇 (顺序执行, 均 EXIT=0, 各自日志 0 ERROR): attention 1254s / collab 1235s /
  locus 1284s / substance 1257s / tone 1187s / disagreement 1238s / clarity 1244s /
  benefit_society 1232s / brokerage_network 1231s / llm_peer 1230s / strategic_diff 1229s。
  判读: `--stage all` 内含重跑主线 pipeline (产品化封装设计), 主线产物 mtime 终归
  strategic_diff (04:17-04:28) — 由此产生的「75 早于 21」时序哨兵见 F8。
- ⑧ 监视方法论教训: Start-Process 返回的 PID 是启动壳, 真 orchestrator PID 须经
  Win32_Process CommandLine 匹配获取 (⑧ 壳=35328 / 真=27088), 否则误报提前退出。

## §2 核心数据流定谳: 词典 1506→607 换血的**四类**缓存 miss 面 (F1, by-design)

607 词换血后, 下游缓存键随之漂移, 离线守卫处处 fail-loud — **全部行为符合契约, 非 bug**;
本轮以「离线证伪 → 最小在线回填 → 复验 0-miss」闭环:

1. **词表级嵌入** (stage 15): 289 新词 × 2 co-primary 轨全 miss。离线首跑精确崩于 `_lg` 轨
   `RuntimeError: … n_missing=289` (Qwen 轨因播种竞态先到已命中)。处置: 生产引擎
   `embed_texts` 定点播种 289×2 (<$0.01), 探针复核 **607/607 双轨全命中**。
2. **ss 轨 LLM prompt** (stage 21): `content_ss`=银行∧金科同句窗, 文本随词典变 → 2,304 miss
   (768/模型 ×3 家, 全部集中 ss 轨; full/ctx 轨 0 miss)。② 在线回填 (240s), 复验
   `verify_stage21_cache_coverage` → 9423/9423, 0 miss。
3. **ss 轨文章嵌入** (stage 16/25/26 + 锚点族): 同因; ② 在线回填 (16 号 386s / 25 号 190s)。
4. **llm_peer_iv PEER prompt** (stage 40 步骤 8z 内, R2-MAJOR-1 补列): 过筛句条件含
   「≥1 金科词」→ 句集随词典变 → prompt 漂移 miss; ② 在线跑时已静默回填 (含离线
   miss→raise 守卫, `llm_peer_iv.py:449-455`)。无专用验钞机 → 由 §6.2 终局离线全链
   重放兜底证明 0 miss。
5. **strategic_diff/policy bank-year 超级文档 `_lg` 轨** (RR2-MAJOR-1 实证补列, 第五面):
   2026-07-22 00:55-00:57 (④ attention 篇在线窗口) `_lg` API 瞬时失败 → 重试耗尽 →
   twin 软降级 NaN、**未入缓存** (8 条超级文档只有 Qwen 侧入库, 缓存库时间线取证)。
   终局重放 (05:41-05:44) 命中 Qwen、`_lg` miss ×12 条 WARNING → 该族 `_lg` 列在重放代
   为 NaN (twin 软诊断不中断, Qwen 主轨完好)。处置: 定点在线重跑 stage 40 回填 `_lg` →
   离线单跑 40 复验 0 twin-miss。**✅ 回填闭环终值 (2026-07-22 06:25-06:40)**: 在线单跑
   stage 40 EXIT=0 (593s, 0 twin 异常, `_lg` 8 条超级文档已入库) → 离线 (OFFLINE=1) 单跑
   stage 40 EXIT=0 (502s, **0 twin 异常 / 0 n_missing**) — 第五面 $0 复现锚恢复得证。
   遗留观察: ② (23:3x) 与重放 (05:4x)
   的超级文档文本集不全同 (重放恰含 attention 代的 8 条) — 文本集对上游产物代敏感,
   但同代内确定 (重放 Qwen 全命中即证); 列为 watch 项, 不阻塞验收。

**非缓存类确定性重算面** (R2-MINOR, $0, 数值漂移属换血正当后果): 22 号词典分与
strategic_diff word/LDA 轨的 jieba 注入词表漂移; 65/69 号敏感性、67 号覆盖审计同理。
词典换血的面板数值副作用 (n_articles/fintech_share/keep 率新口径 90.96% 等) 须在
manuscript 披露 (镜像 CLAUDE.md 对 Google→Qwen 换血的披露铁律)。

观察: 13 号 keep 率 90.96% (1047/1151; 2017=90.41%/2018=92.73%), 距 min_keep_frac=0.001
极远。stage 15 IDF 语料命中 312 个不同金科关键词; 新词典 0 个空格/顿号/拉丁词 →
jieba 全词可匹配 (旧 1506 有 6 词不可匹配)。

## §3 整改工作包 (本轮实施; 全部为注释/文档/日志文案层, 计算行为零变化)

- **WP-A 生产侧「1506/~1500」当下事实断言批改 (19 处)**:
  17 处 "1506": CLAUDE.md:27; core/text/entity_context.py:267,407; pipeline/text/
  ctx_materializer.py:55; pipeline/filtering/cooccurrence_filter.py:41; …/news_fintech.py:54;
  …/fintech_intensity.py:79,82,92,161,179,330,398,714; pipeline/features/strategic_diff.py:91,323;
  validation/threshold.py:127。+2 处 "~1500" (R2-MAJOR-3): validation/dict_coverage.py:69,888。
  措辞: 断言现状处改 "607 词 (2026-07-21 换血)"; 规模量级处 "~607 词"; fintech_intensity.py
  :79 与 :179 (R1-MINOR-5 同型) 的 "6/1506 空格/顿号" 改历史语境表述 + 注明现 607 词典
  0 特殊字符词、剔除数依旧 `len(unmatchable)` 运行期计算。
  ⚠ :714 是 `logger.info` **运行时字符串** (R1-MAJOR-3): 改动=stage 15 日志文案变更
  (计算行为不变), 于此显式声明, 供后续日志对账轮豁免。
  另: CLAUDE.md 头部 "Current version" 段补一句 607 换血事件记载 (R2-MINOR)。
- **WP-A2 codebook 长注释源批改 (R1-MAJOR-2/R2-BLOCKER-1)**: config/codebook_longdesc/
  下受限模式 (`1506 ?词|1506 ?金科|1506金科词|1506 ?关键词`) 命中文件逐行批改
  (**终数 = 38 文件 / 99 token**, 含超出声明模式的裸变体超额清洗, RR2-MINOR-1 回填;
  实施措辞为素 "607 词/词表" 不带日期后缀 — 长注释语境下日期由 CLAUDE.md/计划承载,
  RR2-MINOR-2 偏离披露), 逐行 diff 全体对校 0 误伤; 随后用项目生成器重生
  build/codebook/ 产物 (367 处命中的 variable_codebook.md 属生成物, 只改源+重生, 不手改)。
  .dta notes 重放不在本轮 (沿既有 apply_stata_notes.ps1 流程, 下轮重放自动携带新文案)。
- **WP-B 具名清理 ① 审计重放产物 (2 文件, R2-MINOR 证据先留档)**:
  删除前留档 sha256 → `bank_keywords_20260721_222632.xlsx` (对账: 14/14 sheet, 判别链
  全 0 差异, 唯 §4.3 排序并列 2 格) 与 `judge_manifest_20260721_222632.json`。
  canonical 144911 对不动。sha256 记录: (实施时回填于 §5 F5)。
- **WP-C 本计划文档入库** + **WP-D 记忆更新** (新 topic 文件 + MEMORY.md 索引;
  含 fintech_share 分母行集随词典变的披露钩子, R2-MINOR)。

**实施时序约束**: pipeline/core/validation 下 .py 的注释编辑一律等 ④⑤⑥⑦ 收官后进行
(它们运行中 import 这些模块, 防中途写文件撞上 import); ⑧⑨ 侧线经 grep 证实零主树 import →
⑧⑨运行窗口可安全编辑主树; codebook_longdesc/CLAUDE.md/计划文档随时可改。
**R3 终审注记**: ① `scripts/generate_codebook.py` 为无参生成器, 产物现含 351 处 "1506" —
WP-A2 编辑源+重生后须 grep 产物残差, 残差>0 时逐条溯源其它注入点 (如 pipeline/panel/
codebook.py 模板) 再处置; ② codebook 重生须排在 pipeline .py 注释编辑之后 (生成器 import
pipeline), 即顺序 = ④⑤⑥⑦收官 → .py 批改 → 生成器重生 → §6.4 受限 grep 验收。

## §4 报告项 (待用户研究决策, 本轮刻意不修)

1. **S13 placebo 交集漂移**: 交集由 {智能柜员机} 变 {自助银行} (前者已出局, 后者是 607
   新入词, 同时在 placebo `branch_channel` 桶)。`TestS13PlaceboFintechIntersection` ×2 红 =
   冻结白名单锁按设计报警。选项: (a) 从 placebo yaml 删「自助银行」; (b) 重走 §2 S13 审计,
   白名单改 {自助银行} + 更新 yaml:28,81 头注 (现「1506 词/恰1词=智能柜员机」双重失实);
   (c) 用与 607 词典零交集的替代词换掉「自助银行」保持桶覆盖, 并重议「恰 1 词交集」设计
   是否保留 (R2-MINOR 补列)。
   ⚠ **顺序耦合披露 (R2-MAJOR-6)**: ⑤ 80 号管道实读 placebo yaml → 本轮 ⑤ 产物
   `80_alt_anchor_and_placebo_panel.parquet` 的 placebo 臂含真金科词「自助银行」(污染方向:
   placebo 应与金科正交)。产物标记**临时口径**, S13 决策落地后须重跑 ⑤。
2. **locus_split 289 新词未编码**: locus_split.yaml 仍旧 1506 三桶 (492/758/256); 对 607 交集
   仅 318, 289 新词无桶, 1188 词已出局。红断言 (fast 口径 1 条 union; 全量口径另有
   :68 len==1506、:89 三桶和、:211 双编码 1506 行, R2-MINOR 补列)。路径: (a) 重走 WP-R3
   全量双编码+仲裁; (b) 增量方案 — 318 交集词沿用既有仲裁 (locus_split_double_coding_
   2026-07-14.csv 可复用), 仅 289 新词双编码 (R2-MINOR 低成本选项)。
3. **生成侧排序并列疵** (①, 只披露): 「银企直联/银企直连」lazy_pinyin 同键并列, 重放相邻
   互换 2 格; 决策承载 sheet 全 0 差异。生成侧冻结铁律 → 不修。
4. **benefit 冻结中心 sidecar 词典盲区 (R2-MAJOR-2, 隐藏数据流问题)**:
   `_benefit_center_sidecar.json` 守卫仅校验 model_id/anchor_sha256/text_pipeline_version,
   **不含词典指纹** → 词典换血改变 ss/ctx 轨语料分布, 但 `benefit_score_*` 冻结 median
   仍是旧 1506 词典语料上冻结的值, 被**静默沿用** (无 fail-loud; CLAUDE.md 删 sidecar 铁律
   只写了换嵌入场景)。选项: (a) 删 sidecar 重冻结 (阈值反映现语料, 但跨 run 可比性断点) +
   重跑 40/80; (b) 刻意沿用 + manuscript 披露。建议 (a); 另建议无论何选, 给 sidecar 守卫
   补词典 sha 字段 (代码级加固, 待决策后一并做)。

## §5 全部定谳发现汇总 (四闸: 真/可验证/非设计/值得)

- F1 词典换血四类缓存 miss 面 + 确定性重算面 (§2, by-design, 已回填闭环)。
- F2 「1506/~1500」陈旧断言: 生产侧 19 处 (WP-A) + codebook 源 32 文件 (WP-A2)。
- F3 研究决策红: fast 口径 3 条 (S13×2 + wpr3 union); 全量口径另加 wpr3 :68/:89/:211
  (口径于此声明, 消除 §5/§6 计数歧义)。
- F4 keep 率/覆盖观察 (§2 尾, 无风险)。
- F5 ① 重放工作簿对账: 14/14 sheet, 判别链 0 差异; 唯 §4.3 排序并列 2 格。删除前 sha256 留档:
  bank_keywords_20260721_222632.xlsx = `2b5a0f61defdc31bd8de1b5e683a8713229c3a536055098df31ef12d63d43f77`;
  judge_manifest_20260721_222632.json = `e50d18c089c8c12f41cba666002617e71b4b97a7a01a88f9be4cf8d441742f29`。
- F6 run_paper.log 3 条 ERROR = 2026-07-06 历史负例残留 (⚠ RR2-MINOR-3 修正: 该日志为
  **追加**模式非覆盖, 3 条旧 ERROR 仍在盘上 — §6.3 判据按「历史残留豁免」口径执行)。
- F7 fast 合跑 4 条瞬红 (iss_llm_score×2 + 两侧 partition×2) = 与④并发重写产物的读写竞态;
  单跑全绿, 非缺陷 (合跑/单跑口径声明, 镜像第六轮 RR3-Z 教训)。
- F8 「75 早于上游 21」staleness 哨兵 = 入口执行顺序固有的正确代际披露, 非缺陷 (③重生
  75 后消失; ④逐篇/②重放再跑 21 后按设计再现, 05:47 曾在报)。**终态 = 已消失**: ③离线
  重放 (05:53-06:04) 重生 75 (05:56) 晚于 21 (05:37), 06:26 离线 40 单跑确认正常合并 0 告警。
- F9 benefit sidecar 词典盲区 (§4.4, 报告+建议)。
- F10 `27_benefit_dimensions_panel.parquet` 代际陈旧 (2026-07-03 代, 建于旧 1506 词典):
  ⑧⑨ 侧线消费时按既有哨兵机制披露降级 (非缺陷)。其重生 (--track all --include-lg
  --df-exploded) 与 §4.4 sidecar 决策纠缠 (benefit 族共用冻结中心) → 并入 §4 决策捆绑包:
  S13/sidecar 决策落地后, 同批重跑 27 → 80 → ⑧⑨ altagg。
- 慢性红盘点 (勿再立案): cohort ×2, citation_gate ×8, jieba isolation flake ×1。

## §6 验收判据 (R1/R2 重写版)

1. 九入口全部 EXIT=0 (≤3h/入口单次执行)。
2. **终局离线全链重放**: 全部入口跑完与整改落地后, `NEWS_PROCESS_LLM_OFFLINE=1` 复跑
   ② 全链 EXIT=0 — 一举证明四类 miss 面 (含 llm_peer) 全部 0 miss、$0 复现锚全面恢复;
   另附 `verify_stage21_cache_coverage` 0 miss + 词表探针 607/607 双轨。
   **✅ 已达成 (2026-07-22 05:27-05:48)**: OFFLINE=1 重放 EXIT=0 全 16 阶段 / 1226s / 0 ERROR;
   verify_stage21 = 9423/9423 0 miss; 词表探针 = 两轨 607/607。
3. 日志层: 真 ` - ERROR - ` 0 条 (历史残留除外); WARNING 全数归入已知族; F8 哨兵消失。
   **✅ 已达成 (2026-07-22 05:53-06:04)**: 终局重放后补跑 ③ 离线重放 EXIT=0 全 16 阶段 /
   0 ERROR / $0 全命中 (66=1.3s, 70=1.2s) → 75 代际归位, F8 哨兵消除法已执行;
   九入口日志真 ERROR 合计 0 条 (run_paper.log 3 条为 2026-07-06 历史残留, 豁免口径)。
4. WP-A/A2 后: **受限模式** `grep -E "1506 ?词|1506 ?金科|1506金科词|1506 ?关键词|1506 ?金融科技|~1500"`
   (实施中抓获漏网变体「1506 金融科技词」1 处 (F505_l2_strat_diff_n5_lda.md:202) → 模式已扩);
   豁免清单补入 fintech_intensity.py:79,179 (WP-A 刻意的「旧 1506 词表/词典」历史语境表述,
   RR2-MAJOR-2 判据自洽修正)
   在 {core,pipeline,validation,config/codebook_longdesc,CLAUDE.md} 域 0 命中 (显式豁免:
   LLMs_for_FinTech_dic/ 冻结链、fintech_locus_split.yaml 冻结派生表、placebo yaml (§4.1)、
   news_fintech.py:357,485 历史注记、test_omni_fix_fintech 历史裁决语境、
   lexical_complexity.py:15 页码、数据资产偶然数字/DOI); ruff 通过。
5. 安静窗口 **fast (-m fast) 口径**全量 = 14 红基线 (cohort 2 + citation_gate 8 + jieba 1 +
   词典决策红 3), 0 新增; golden 14 阶段红=慢性陈旧独立于本轮 diff (CLAUDE.md 既有裁定),
   词典数值副作用披露入 manuscript 由 §2 尾声明承接。
   **✅ 已达成 (2026-07-22 06:05)**: 安静窗口干净环境 fast 全量 = 恰 14 FAILED (构成逐一
   核对与基线一致), 0 新增。⚠ 方法论教训: 测试进程若继承 NEWS_PROCESS_LLM_OFFLINE=1
   会假红 3 条在线失败路径 mock 测试 (aggregate_track_decoupling ×2 +
   benefit_society_embedding lg 软降级 ×1) — 跑套件前必须清该 env; 三条已无 env 单跑复核全绿。
6. 工作树: by-name 提交推送 main; **排除并发产物** `data/processed/v3_5_1_constants.json`
  (会话起点已 M, 非本轮所有) 及一切 eval_reports/缓存 db。基线漂移注记 (RR2-MINOR-4):
  本轮提交落在 main=`5d281079` (并发会话「并发上限 100→250」用户决策提交) 之上,
  非计划起点 `b7b70b08`。

## §8 第二阶段: 全项目 607 化落地 (2026-07-22 用户裁定「全部使用 607 新词典、严禁 1506 旧词典」)

§4 报告项全部按 607 方向落地 (用户授权不计付费):

1. **S13-v2** (原 §4.1, 采选项 b 镜像 2026-07-14 先例): placebo yaml 头注更新 (交集披露
   智能柜员机→自助银行, 词数 607) + 行内注双更新; 测试白名单 `_ALLOWED_INTERSECTION`
   换血 {自助银行}, 精确锁测试更名 test_self_service_bank_*。复验: 该测试文件 14/14 绿。
2. **locus_split v2** (原 §4.2, 采增量方案 b, 兑现 v1 yaml「扩表须重复①-③」铁律):
   289 新词双人盲编码 (子 agent A/B 互盲) → po=0.9066 / **κ=0.8418** (>0.7 门槛, 与 v1
   0.8375 同带) → 27 分歧词第三方仲裁 (聚类一致性: 容灾/备份簇 6 词→unassigned 按
   v1「通用 IT 运维词」语义; 品牌名 2 词→unassigned 镜像掌上生活; 泛化经营/运营簇 5 词
   →unassigned 镜像数字化转型; 生态/轻型银行→func 镜像体验/全景银行; 文本/语音机器人
   →tech 镜像智能语音)。产物: `config/locus_split_double_coding_2026-07-22.csv` (289 行)
   + yaml v2-2026-07-22 重建 (**tech=215/func=307/unassigned=85**, 并集=607 零遗漏两两
   不交, 318 保留词沿用 v1 冻结终判, v1 CSV 冻结存档不动)。测试同步 (双表契约+增量账本
   互锁), 复验 35/35 绿; 消费者 triangulation 实跑验证 (dev 规模 fail-loud 闸 + --dry-run
   确认均按设计, 读出 v2 215/307/85)。
   跨代际张力披露 (RR-607 MINOR-1/2, v1 冻结协议固有代价, 非仲裁错误): v1 保留词
   「智能运营」=func 与 v2 仲裁泛化运营簇 (智慧/数字化/数字运营=unassigned) 同型异判;
   v1「敏捷银行」=unassigned 与 v2「银行业务模式→func」原则 (生态/轻型银行) 存在回溯
   张力 — 318 保留词按协议不重编码, 两处张力披露备查, 如需一致化须另启 v3 全量重编码。
3. **benefit sidecar** (原 §4.4, 采选项 a + 守卫加固): `_get_frozen_center` 增第 4 指纹
   `dict_sha256` (config/fintech_dict.json 字节 sha256; 同款 fail-loud/回填/冻结语义,
   包根锚定路径解析防异 cwd); 旧 sidecar (6 条旧 1506 代 median, 文件 sha16=113b48c2)
   **删除前逐值记录于此** (RR-607 MINOR-4: 文件本体未另存, 此清单即对账物):
   full=0.0982446 / ctx=0.0971527 / ss=0.0952325 / lg_full=0.108083 / lg_ctx=0.110328 /
   lg_ss=0.113674 → 删除后 stage 40 在线重跑重冻结 6 轨新 median (full 0.09945/
   ctx 0.09797/ss 0.09827/lg_full 0.1096/lg_ctx 0.1116/lg_ss 0.1170, n=833,
   全带 dict_sha256=9c731b78)。
4. **27 号重生 + 下游同批重跑** (原 §4.1 耦合 + F10): 27 号三参数重生 (115×26, 消费
   09:02 新代 .npy); 46/51/80 重跑 EXIT=0; ⑧ 全链重跑 EXIT=0 (701s, 0 ERROR);
   ⑨ 全链重跑 (§8a 回填)。
5. **残留清扫**: innovation_proxy_triangulation.py:29 更新 v2 表述; news_fintech.py:485
   历史注记补今昔括注; CLAUDE.md 事件记载更新为「三决策项已落地」。受限模式 grep
   (含 config/tests/scripts 全域) 归零 (豁免仅剩: 带「旧/当时/换血」限定语的历史语境、
   v1 冻结 CSV、yaml v1_baseline 基准记录)。

§8a 终值回填区 (2026-07-22):
- **G9 振荡插曲与闭合**: §8.3-4 的单独重跑 40 使 75 (05:56) > 21 (05:37) → 40 合并
  opt-in 交叉媒体 9 列 → 面板临时进入 3451 激活代 → 5 条 codebook/labels 测试红
  (family map 孤儿 = cross_media_alpha/cross_outlet_tone_variance/n_events ×3 轨)。
  按「振荡勿追锚」铁律不改测试, 正解 = 全链 ② 终代重跑 (11:18-12:0x, EXIT=0 全 16 阶段,
  0 ERROR; 内部重跑 21 刷新代际) → 面板回 **3442 未激活代** (cross_media 列消失实证)
  → codebook 重生 → 27 (EXIT=0) → 80 (EXIT=0) → ⑧⑨ 终代重跑。5 红全闭
  (codebook_family_map + stata_labels_zh + wpr3 + s3_s10_s13 计 66/66 绿)。
  教训: **凡影响 40 面板的定点整改, 传导必须走全链 ② 而非单独重跑 40** (代际哨兵
  以 21 为基准, 单跑 40 必然吃到激活代)。
- fast 全量终验收 = **恰 11 红** (cohort×2 + citation_gate×8 + jieba×1, 全慢性族;
  词典决策红 3 条全部闭合, 0 新增)。
- ⑧ 终代重跑 12:13-12:2x EXIT=0 (0 ERROR, 锁干净释放); ⑨ 终代重跑 12:59-14:46 EXIT=0
  (0 ERROR, 锁干净释放)。
- 离线单跑 40 终验证 (OFFLINE=1, 14:48-14:5x): **0 twin 异常 / 0 n_missing / 0 ERROR
  ($0 全命中), 冻结 center 消费 ×6 (四指纹 dict_sha256 守卫通过读取), 面板保持
  (172, 3442) 未激活代** — 第二阶段全部验收判据达成。
- 评审链: RR-607 对抗评审 (0 BLOCKER / 0 MAJOR / 5 MINOR 全处置: 跨代际张力披露入
  §8.2、旧 center 六值对账清单入 §8.3、两测试文件裸 1506 注释补限定语、.gitignore
  v2 CSV negation 由 RR1 自审抓获补齐、§8a 本段即 MINOR-3 回填) + RR1 自审 (diff 面
  全读) + R3 终审 (验收清单逐条核签)。

## §7 播种支出记录 (完成用户指令所必需的最小定点回填)

- 词表嵌入 289×2: <$0.01。
- stage 21 ss 轨 2,304 次 LLM + ss 轨文章嵌入 (16/25/26) + llm_peer PEER prompt (40) +
  66/70 验证 LLM 回填 + ④ 逐篇管道零星 miss: 合计估 <$5。
- M0 边界: 以上为 T=2 dev 语料增量回填, 非 18.2M 生产语料付费重处理 (后者仍受 M0 门)。
