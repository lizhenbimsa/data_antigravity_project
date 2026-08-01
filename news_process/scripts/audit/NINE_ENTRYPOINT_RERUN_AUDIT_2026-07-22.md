# 九入口复跑验证审计与整改执行计划 (2026-07-22/23, 第二轮)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


基线: main=`587df032` (607 化收官后首轮全量复跑验证)。上一轮权威台账 =
`NINE_ENTRYPOINT_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-21.md` (词典换血整改轮);
本轮定位 = **复跑验证轮**: 验证 607 终代的 $0 离线复现锚、九入口健康度与 fast 基线,
理论预期「全链 $0 全命中、9/9 EXIT=0、恰 11 红」— **实测全部达成**。
评审链: 计划 R1 (事实核验) → R2 (完备性/风险) → R3 (实施者终审) 三轮已执行 (见 §7)。

## §1 运行矩阵 (九入口, 单入口/单次执行 ≤3h 约束全部满足)

| # | 入口 | 模式 | 结果 | 耗时 | 备注 |
|---|------|------|------|------|------|
| ① | LLMs_for_FinTech_dic/00_LLMs_for_dic.py | LLMS_DIC_OFFLINE=1 | EXIT=0 | 46.5s | 0 ERROR / 3 已知 WARNING (2 零温采样披露 + 1 历史重试重放); 结果链 13247→982→915→696→AI 认可 591 与基线一致; 判决「$0 离线逐字节复现 (0 降级/0 无响应 try/全格覆盖)」✓ |
| ② | run_pipeline_function.py | NEWS_PROCESS_LLM_OFFLINE=1 | EXIT=0 | 2720s | 16/16 阶段 ✓; 0 ERROR / 0 twin 异常 / 0 n_missing; 面板 **172×3442 未激活代**; 冻结 center ×6 消费值与 §8.3 重冻结终值逐一吻合 (full 0.09945/ctx 0.09797/ss 0.09827/lg_full 0.1096/lg_ctx 0.1116/lg_ss 0.1170); verify_stage21 = **9423/9423 0 miss**; 管道锁干净释放。耗时 2720s vs 上轮离线 1226s = 宿主争用伪回归 (既有裁定, 勿立案) |
| ③ | run_pipeline_validation.py | OFFLINE=1 | EXIT=0 | 663s | 16/16 阶段 ✓ (60–75); 0 ERROR; 66/70 号 1.2s 级完成 = 离线 $0 全命中; 75 号晚于 21 号重生, 代际口径正确 |
| ④ | run_paper.py | --list + 11 篇逐篇 (位置参数, OFFLINE=1) | --list EXIT=0 + **11/11 EXIT=0** | 计 ~4.2h | attention 1597s / collab 1160s / locus 1310s / substance 1264s / tone 1704s / disagreement 1224s / clarity 1619s / benefit_society 1609s / brokerage 1082s / llm_peer 1085s / strategic_diff 1091s (run_paper.log 追加档逐会话互证退出码 0) |
| ⑤ | 80_placebo_and_alt_anchor.py | OFFLINE=1 | EXIT=0 | 2s | 0 ERROR; 833 篇 / 115 bank-year; S13-v2 白名单代 (自助银行) 正常消费 |
| ⑥ | 81_stata_data_audit.py | OFFLINE=1 | EXIT=0 | 3s | 0 ERROR; **160 项: 0 FAIL / 18 WARN / 142 PASS** (与上轮结构一致); 核心恒等式族 46 项全无硬错; WARN 仅已知 T=2 稀疏族 |
| ⑦ | 82_export_stats_excel.py | OFFLINE=1 | EXIT=0 | 1s | 0 ERROR; 4 阶段 / 12 sheet |
| ⑧ | company_listed_bank/run_pipeline.py | 全链 01→04 | EXIT=0 | 789s | 0 ERROR; 单实例锁干净释放 |
| ⑨ | company_tax_bank/run_pipeline.py | 全链 01→04 | EXIT=0 | 2594s | 0 ERROR; 「所选步骤 rc 全 0, 硬依赖链完整闭合」; 锁干净释放。执行实例为并发协作会话 23:12 启动 (PID 57060), 本会话以其为准真跑, 不重复启动 (见 §3 OP-5) |

## §2 核心验收终值

1. **九入口 9/9 EXIT=0** (≤3h/入口单次执行) ✓。
2. **$0 离线复现锚全面在位**: ② 全链 OFFLINE=1 EXIT=0 + verify_stage21 9423/9423 +
   冻结 center ×6 (dict_sha256 第 4 指纹守卫通过) + ③ 66/70 秒级 $0 + ④ 11 篇全程
   OFFLINE=1 成功 = 11 条论文管道离线锚实证 + ① 判别链逐字节复现判决 ✓。
3. **日志层**: logs/ 全目录 (主线+侧线+LLMs_dic) 真 ` - ERROR - ` 归零 — 唯一命中
   run_paper.log 5 条 = 3 条 2026-07-06 历史负例残留 (前轮 F6 豁免口径) + 2 条本轮会话侧
   锁拒绝记录 (§3 OP-2, by-design fail-loud)。**项目缺陷计 0**。
4. **fast 基线**: 干净环境 (清 OFFLINE env) 全量 -m fast = **恰 11 FAILED**
   (cohort ×2 + citation_gate ×8 + jieba isolation flake ×1), 构成与冻结基线逐一吻合,
   **0 新增**。
5. **代际终态**: 21 号 parquet (23:01, strategic_diff 内嵌重跑) > 75 号 (18:59) → 面板
   172×3442 未激活代 (无 cross_media 列), 与 G9 收官基线一致, 无需追加 ③ 补跑。
6. **静态不变量**: 词典 607 词 sha16=9c731b78379401e9; benefit sidecar 四指纹含
   dict_sha256; 1506 受限模式 grep 源码域 0 命中; DAG 16/16/16/35。

## §3 会话侧操作事件 (非项目缺陷, 方法论教训入记忆)

- **OP-1 `--paper` 旗标误用**: ④ 首轮 11×EXIT=2 (argparse fail-loud, 各 2s, 零产物
  副作用)。正确用法 = 位置参数 `run_paper.py <paper_id>`; F5 透传设计按注记工作。
  副产品: run_paper.log 追加档新增 11 条「退出码 2 (未知 paper_id…)」会话记录 (豁免)。
- **OP-2 「stopped」通知 ≠ 进程死亡 (重要)**: 会话重启时 harness 对后台包装任务发
  「stopped/无完成记录」通知, 但 Start-Process 分离的 OS 进程链全部存活并继续执行。
  基于失效通知误判「已击杀」+ bash 双引号转发 PowerShell 时 `$_` 被 bash 展开致进程
  查询静默空返 → 两次启动重复实例 (disagreement RUN2 21:05:03 / clarity 撞车 21:21:48),
  **均被主线管道单实例锁正确拒绝** (EXIT=1, stderr 诊断含占用者 PID) — 主线并发锁
  实弹验证 ×2 通过。教训: (a) 「stopped」只可信为「跟踪丢失」, 以 Win32_Process
  CommandLine 匹配为准; (b) PowerShell 进程查询勿经 bash 双引号转发; (c) 重启前必验
  锁持有者 PID 存活性。run_paper.log 由此新增 2 条 ERROR 记录 (§2.3 已豁免归档)。
- **OP-3 scratchpad 捕获文件双写损伤**: 冲突实例的 stdout 重定向截断 disagreement/
  clarity 两份会话侧捕获 (项目 logs/ 无影响; run_paper.log 追加模式完整, 以之为准)。
- **OP-4 mcp-stata 进程链澄清**: 17:46 起 3 python 进程链 = IDE 的 mcp-stata MCP 服务
  (uv 托管), 与管道无关, 不触碰。
- **OP-5 ⑨ 并发协作**: 并发会话 23:12:19 先行启动 ⑨ 全链 (PID 57060); 本会话 23:24 的
  启动尝试被 company_tax_bank 单实例锁正确拒绝 (第 3 次锁实弹验证, 侧线锁) → 遵循
  「不打编辑战」先例, 以并发实例为准真跑并哨兵监视至收官 (23:55:33, 0 ERROR)。

## §4 定谳发现 (四闸: 真/可验证/非设计/值得)

- **F1 ① 生成侧转储 sheet 行序非确定 (观察项, 报告不修)**: 重放工作簿 14/14 sheet 中,
  判别链/决策承载 11 sheet 逐格 0 差异; 3 个生成侧原始转储 sheet (1-原始生成/1b-去重后
  原始/原始-含有金融科技) 出现大面积**行序置换** (64,185 差异格), 但**行多重集
  (keyword×model) 完全恒等 (0 内容差异)**。机制 = 生成侧 `concurrent.futures.as_completed`
  完成序写行 (00_LLMs_for_dic.py:1697), 线程完成序运行间天然非确定; 上轮重放 (222632)
  恰巧同序仅 2 格拼音并列差异, 本轮 (175908) 模型块序置换。判别决策零影响 (591 词
  逐字一致)。**处置 = 报告 + 台账留痕, 不修** — 修复须触生成阶段冻结区
  (2026-07-21 用户铁律「生成侧零触碰」), 且内容级恒等已证。
- **F2 陈旧 __pycache__ 字节码 2 件 (轻微, 具名清理)**: `core/text/__pycache__/
  entity_context.cpython-314.pyc` (历史错环境裸 python 3.14 编译残迹) 与
  `pipeline/filtering/__pycache__/fintech_intensity.cpython-313.pyc` — 均含旧 "1506"
  字面量 (源文件已净), gitignored, 无行为影响; 按「清理必逐条具名」铁律具名删除,
  解释器按需重生。
- **F3 v3_5_1_constants.json 时间戳漂移**: 仅 `stage21_last_run_timestamp`
  (06:48→15:03 UTC, strategic_diff 内嵌 21 号重跑所致) → 按 b90fbea8 先例做
  chore(constants) 收口提交。
- **F4 core/caching.py 假 M**: 内容 diff 为空, 纯 EOL (LF→CRLF) 噪声 (已知事项 #1) →
  checkout 还原, 不提交。
- **F5 ① 重放产物对账与处置** (镜像上轮 WP-B): manifest 除 created_at/run_output_file/
  offline_mode 3 个运行元字段外全字段 0 差异; xlsx 对账见 F1。删除前 sha256 留档:
  `judge_manifest_20260722_175908.json` = `a08512143378bab85bd08877bad1f48aca9e51e5b0ed3d4af3ac7b4e505d7b87`;
  `bank_keywords_20260722_175908.xlsx` = `5cbaf1da3fd72fc889605a972f52fb4dd74646ac722aec545900def852f5b62b`。
  canonical 144911 对不动。
- 慢性红盘点 (勿再立案): cohort ×2, citation_gate ×8, jieba flake ×1; G-D2.1
  corr=0.7033 WARN、G-D3.1 覆盖 19.57%/21.15% WARN、herd 小样本提醒 = T=2 预期退化。

## §5 整改工作包

- **WP-1 本计划文档入库** (scripts/audit/, 即本文件)。
- **WP-2 ① 重放产物删除** (F5, sha256 已留档): 删 judge_manifest_20260722_175908.json +
  bank_keywords_20260722_175908.xlsx。
- **WP-3 chore(constants) 收口提交** (F3, by-name 单文件)。
- **WP-4 core/caching.py EOL 还原** (F4, `git checkout --`, 零内容变更)。
- **WP-5 __pycache__ 具名清理 2 件** (F2)。
- **WP-6 记忆更新**: nine-entrypoint topic 补第二轮小节 + MEMORY.md 索引 hook 更新。
- **WP-7 项目说明书更新**: HTML 真源增补「2026-07-22/23 复跑验证轮」运行记载
  (九入口矩阵终值 + $0 复现锚验证 + fast 11 红基线), 同步重生成 PDF (真源=HTML 铁律)。

## §6 验收判据

1. 九入口 9/9 EXIT=0 ✓ (§1); 日志层项目缺陷 0 ✓ (§2.3); fast 恰 11 红 0 新增 ✓ (§2.4)。
2. WP-2/5 后: 具名文件不存在; canonical 144911 完好; git status 不新增未跟踪项。
3. WP-3/4 后: 工作树除并发在途改动外干净; 推送 main 成功。
4. WP-7 后: 说明书 HTML 含本轮记载且无与 §1 矩阵矛盾的陈旧断言; PDF 与 HTML 同代。

## §7 评审链记录

- **R1 事实核验轮**: §1 矩阵逐格与 scratchpad 捕获/logs/*.log/run_paper.log 追加档/
  哨兵输出互证; §2 终值逐条与工具输出比对 (verify_stage21 原文、center ×6 数值、
  fast FAILED 清单构成)。修正 0 处事实错。
- **R2 完备性/风险轮**: (a) F1 若不查行多重集会误报「复现破坏」BLOCKER — 已以
  order-insensitive 对账证伪; (b) WP-2 删除动作与「生成侧零触碰」铁律相容性 — 重放
  产物为判别链运行产物且上轮已有删除先例 (WP-B), 相容; (c) ⑨ 采并发实例为准的
  风险 — 其日志 0 ERROR + rc 全 0 + 锁干净释放, 且入口/参数与本会话计划完全一致,
  无口径差; (d) 说明书更新遗漏风险 — WP-7 验收含「无矛盾陈旧断言」条款兜底。
- **R3 实施者终审**: 逐 WP 核对实施顺序依赖 (WP-2/5 删除先于 git 收尾; WP-7 先 HTML
  后 PDF; 提交 by-name 排除 core/caching.py 与一切缓存 db/eval_reports), 无循环依赖;
  全部 WP 均可逆或已留档 (sha256/git)。

## §8 双会话交叉互证注记 (2026-07-23, 复跑执行会话回填; 只增不改)

本轮系两会话并发协作 (镜像上轮先例, 未打编辑战)。另一会话主导台账/说明书/收口提交
(8337beb3 + 82bab02a + 5d980878, 均已推送); 本会话主导九入口真跑与独立验收, 回填三点:

1. **⑧⑨ 第二实例独立复跑互证**: 在 §1 所记实例收官后, 本会话又各完整重跑一次 —
   ⑧ EXIT=0 / 1214s (00:17 收官) 与 ⑨ EXIT=0 / 2564s (00:18-01:01), 均 0 ERROR、
   单实例锁干净释放。同链两代独立真跑双双全绿 = 侧线确定性与幂等性的实弹互证。
   盘上侧线产物终代为本会话 00:17/01:01 代 (与 §1 实例产物确定性等价)。
2. **F2 订正 (313 pyc)**: `fintech_intensity.cpython-313.pyc` 于 01:02 已由当前净源
   新鲜重编译, 其残余 1 处 "1506" 字面量 = 上轮 WP-A 显式豁免的「旧 1506 词表」历史
   语境表述在字节码中的如实镜像 — 删除后会原样重生, WP-5 对此件**无需也不应执行**
   (仅 cpython-314 错环境残迹属清理对象, 已删)。F2 的「源文件已净」措辞据此收窄为
   「源文件仅存豁免历史语境」。
3. **fast 11 红双会话独立复核**: 本会话安静窗口 (九入口全收官后、清 OFFLINE env)
   独立复测 -m fast = 恰 11 FAILED / 436s, 构成与 §2.4 逐条一致 — 基线判定非单点观测。
