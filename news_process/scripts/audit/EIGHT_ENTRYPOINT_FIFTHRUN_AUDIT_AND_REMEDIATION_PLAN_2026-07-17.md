# 八入口第五轮真跑审计与整改执行计划 (2026-07-17)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 基线 HEAD = f6fca46a (= origin/main, 起跑时工作树 clean)。
> 运行约束: 每入口墙钟上限 — 初始 3h, 11:20 用户改为 **1h**, 13:xx 用户对⑧单独豁免至 **2h**。
> 全程隐藏窗口 Start-Process + tasklist 轮询监视; ②③④⑤⑥ 以 `NEWS_PROCESS_LLM_OFFLINE=1` 启动
> (与 2026-07-17 缓存剪枝会话已验证口径一致; ①⑦⑧ 不需要, ① 实测缓存全命中)。

## §1 运行台账 (8/8 最终 EXIT=0)

| # | 入口 | 结果 | 墙钟 | 备注 |
|---|------|------|------|------|
| ① | run_pipeline_function.py | ✅ 16/16 阶段 | 3157s | 第3次运行成功 (见 E-1/E-3); stage21 离线 0-miss ($0) |
| ② | run_pipeline_validation.py | ✅ 16/16 阶段 | 677s | 第2次运行成功 (见 E-4); stage70 离线排除路径 1.4s |
| ③ | run_paper.py | ✅ EXIT=0 | 0.4s | 无参=组合总览, 与前四轮口径一致 |
| ④ | 80_placebo_and_alt_anchor.py | ✅ EXIT=0 | 1.1s | 警告=既登记 T=2 安慰剂功效族 |
| ⑤ | 81_stata_data_audit.py | ✅ EXIT=0 | 2.0s | WARN 十族全命中既有白名单, 0 新族 |
| ⑥ | 82_export_stats_excel.py | ✅ EXIT=0 | 0.45s | 12 sheet 正常 |
| ⑦ | company_listed_bank/run_pipeline.py | ✅ EXIT=0 | 2696s | 0 ERROR; 27号陈旧哨兵/BERT iyvol NaN 均既登记 |
| ⑧ | company_tax_bank/run_pipeline.py | ✅ EXIT=0 | 6289s | 第2次运行成功 (2h 豁免内); 第1次 61min 被 1h 上限击杀 (E-5) |

日志层横扫: 主线+验证+两侧线全部阶段日志 **0 真 ERROR** (run_paper.log 3 条 ERROR 均为
2026-07-06 历史窗负例测试); 全部 WARNING 逐族对照前四轮台账, **0 新增家族**。

## §2 环境级事件台账 (E-1..E-5, 均已处置, 非代码缺陷)

- **E-1 陈旧管道锁**: 01:06:41 的死实例 (PID 21624, 属并发会话) 遗留 `.pipeline.lock`,
  拦截首次启动。核实持有者死亡+无并发写者后手动清锁。锁 fail-loud 语义本身工作正常。
- **E-2 监视方法缺陷 (审计侧自纠)**: Git Bash `kill -0` 对 Windows 原生 PID 不可见 → 两次假
  "早退"误报。改 `tasklist //FI` 轮询后消失。
- **E-3 window-CLOSE 击杀 (P0 环境)**: ①第2次运行 01:58:26 在 stage 40 尾段被外部 window-CLOSE
  事件击杀 (forrtl error 200, 返回码 0xC000013A), 整棵控制台树连 finally 清锁一并死亡 → 锁泄漏。
  E-1 的死实例应属同款死法。处置: 清锁 + 改 `-WindowStyle Hidden` 重跑, 此后全程无复发。
- **E-4 stage70 在线重试风暴 (P0 环境)**: ②首跑未设离线变量, stage 70 对 ~38,610 个未播种
  提示词变体键 (S9 修字后合法延后 M0 付费补种, 见 CACHE_PRUNE_LIVE_ONLY_RECORD_2026-07-17)
  发起真在线调用; 网络间歇不可达 → 每格 80 次重试 × 数千行, 03:00→09:36 共 6.6h 后按上限击杀
  (该阶段子进程 timeout=43,200s, 不会自止损)。副作用: 网络间歇可用时**意外付费 ~1,164 次调用**
  (验证库 7,722→8,886 行, 键合法、响应正确入库, 属未来 M0 补种的净减项, 非污染; 特此披露)。
  eval_reports 无污染 (70 号被杀前未落盘, 66-69 号为完整正常产物)。重跑以
  `NEWS_PROCESS_LLM_OFFLINE=1` 11.3 分钟全绿。
- **E-5 ⑧ 1h 上限击杀与豁免重跑**: ⑧首跑 61min 处于 step 03 county 引擎段被上限规则击杀;
  原子写模式 (.tmp→rename) 保住旧 dta, 唯一残片 6.0GB `.dta.tmp` 已删。用户裁定对⑧豁免至 2h
  后全链重跑成功 (104.8min), 混代状态被整体消解。

## §3 缺陷定谳 (本轮唯一代码级缺陷)

**D-1 registry sha 锚与规范复跑序结构不相容 (P1)**
5 个 fast gate 红灯: `test_company_bank_cooc_registry.py::{test_registry_hash_anchor,
test_registry_content_sha256_function}` / `test_company_tax_bank_cooc_registry.py::同两项` /
`test_company_tax_bank_altagg.py::test_registry_sha_anchor_unchanged`。

证据链 (三方对齐):
1. 今日 ⑦⑧ 重建的盘上 registry 内容 sha: listed=`023cdc91…`, tax=`4f580e3f…`, 均内部自洽
   (meta 与复算相等), 且**逐字节等于 3ccd5df4 (07-16) bump 前的旧锚** → 内容零漂移。
2. 3ccd5df4 把三处锚 bump 到"激活代" (listed=`4a2f79fd…`, tax=`b2464710…`) — 其成立前提是
   40 面板处 +9 列 (3,451) 状态使两 registry 预注册基名激活; 该提交自己预登记了
   "40 面板其后又被并发重写回 3,442 列, 上游稳定后按级联规则再收口"。
3. 规范八入口顺序下 40 号**结构性落在 3,442 列** (① 内 21 每轮重生, 必新于上轮 ② 的 75 号
   → cross_media +9 列不并入, 40 号日志有既登记 WARNING), 故 ⑦⑧ step 01 重建的 registry
   永远是"非激活代" → 单值激活代锚在规范复跑下必红。
4. 旁证: jieba 隔离测试 (第6红) 静默树复测转绿 = 并发负载 flake, 销案。

**修法 (双值冻结集, 4 文件)** — 在 G9 级联收口 (上游 75/21 时序稳定或生产重生) 前, 两代均为
合法已提交世代, 锚必须同时冻结两值, 杜绝来回翻红/反复 bump:
- `tests/test_company_bank_cooc_registry.py`: 保留主常量 `EXPECTED_REGISTRY_SHA256 = <非激活代
  023cdc91…>` (规范复跑态; run_pipeline._expected_registry_anchor 正则以行首+全名提取, 格式不动),
  新增 `EXPECTED_REGISTRY_SHA256_ACTIVATED = <4a2f79fd…>` 与 `FROZEN_REGISTRY_SHAS = {两值}`;
  两处断言改为 `in FROZEN_REGISTRY_SHAS`。注释写明振荡机理与收敛条件 (收口后回归单值)。
- `tests/test_company_tax_bank_cooc_registry.py`: 同款 (`EXPECTED_TAX_REGISTRY_SHA256 =
  <4f580e3f…>` 主值 + `…_ACTIVATED = <b2464710…>` + `FROZEN_TAX_REGISTRY_SHAS`)。
- `tests/test_company_tax_bank_run_pipeline_lock.py`: 镜像常量同步回 `<4f580e3f…>` (与 gate 件
  主常量保持字节同步 — 该文件正例断言 = _expected_registry_anchor() 提取值一致性)。
- `tests/test_company_tax_bank_altagg.py`: 断言改 `disk in treg.FROZEN_TAX_REGISTRY_SHAS`。

新常量名 `…_ACTIVATED` 与主常量前缀重叠但 `\s*=` 边界使 run_pipeline 正则不误配 (已逐字符核)。
run_pipeline 锚状态披露在"激活代盘面"下会 WARNING 提示 bump — 属可容忍的警示级噪声, 本轮不改
生产代码 (scope 纪律); G9 收口时一并消解。

**刻意不做**: ① 40 号 cross_media 并入逻辑的 mtime 依赖修复 (改主管道行为 + 列 schema 变更
→ golden 重生义务, 按铁律 DEFERRED 生产机, 挂 G9 级联规则); ② stage70 43,200s 子进程超时的
收紧 (生产付费播种时该上限有其存在理由, 挂 M0 批次 E 议题); ③ 未播种 38,610 键补种 (M0)。

## §4 验证方案 (实施后逐项)

1. 5 个红灯测试 + jieba 隔离项单独复跑 → 6/6 绿。
2. 两 registry gate 文件全家族复跑 (listed 27 项 + tax 27 项 + altagg + 两 lock 件) → 全绿。
3. `_expected_registry_anchor()` 单元探针: 两侧 run_pipeline 提取值 == 各主常量 (正则未破)。
4. fast 全量 sweep → 与本轮起跑前基线比对 **0 新增红** (基线 = 6 红, 修后应 0 红)。
5. notes 重放: `scripts/apply_stata_notes.ps1` (本轮 ①⑦⑧ 重写 dta 抹掉 notes, 按第四轮收口
   惯例重放, 以 log DONE 标记 + applied=expected 对账, 勿等进程退出)。
6. git status 全量走查 → by-name 提交 (排除并发产物), 推送 main。

## §5 评审记录

- R1 (计划自评): 修法最小面 (仅测试件 4 文件, 零生产代码); 正则边界已逐字符核;
  锁镜像同步义务已覆盖; altagg import 链已覆盖; 回滚成本 = revert 单 commit。
- R2 (对抗自评): "双值集稀释锚强度"质疑 — 驳回: 两值均为已提交合法世代 sha, 任何第三值仍
  fail-loud; 单值方案在 G9 收口前必然导致 bump 拉锯, 审计噪声更大。"应改 run_pipeline 警示
  文案"质疑 — 采纳为 G9 收口时一并处理 (本轮零生产代码面纪律优先)。
- R3 (结果评审): 见 §6 执行记录。

## §5-bis fast 全量残留红灯定谳 (0 新增)

修法后 fast 全量残留 3 红, 逐项 stash A/B 定谳为**既有慢性红/flake, 与本轮运行及修法无关**:
- `test_benefit_society_dual_track.py::test_cohort_module_exports_84_banks` (断言 87 家 vs 盘上
  110 家) + `::test_cohort_csv_is_committed_in_repo` (`data/raw/cohort/benefit_society_84banks.csv`
  从未入库 [gitignore 无例外] 且本机盘上已失): 干净基线 (stash) 上同红 → 慢性红, 属 07-14
  记录的 main 全量基线 21 慢性红家族。前四轮"全绿"口径 = 定向 gate 文件集, 不含此二项。
  处置 = 挂 benefit_society 论文侧裁量 (重锚 110 或恢复 87 口径 csv + gitignore 例外), 本轮不修。
- `test_omni_fix_strategic.py::TestFintechInjectionWordLDA::test_global_jieba_stays_pure_isolation`:
  仅全套件内红 (修法前 13:37 已红), 单跑三次+stash 单跑均绿 → 套件顺序性全局 jieba 污染 flake,
  预存项, 挂下轮定位污染源。

## §6 执行记录 (实测回填)

- [x] §3 四文件修法落地 (另随提交: 两 registry yaml 的去激活化 meta 级回归, 与主锚自洽)
- [x] §4.1 六红灯复跑: 5 registry 项转绿; jieba 项单跑绿 (见 §5-bis)
- [x] §4.2 两 registry gate 全家族 + 两 lock 件复跑 58 项全绿
- [x] §4.3 锚提取探针: listed/tax _expected_registry_anchor() == 各主常量 MATCH
- [x] §4.4 fast 全量: 0 新增红 (残留 3 红定谳见 §5-bis)
- [x] §4.5a 主线 notes 重放 3/3: applied=expected (3442/3442/3453), K7 僵尸护栏 2 次触发按例处置
- [x] §4.5b 侧线 notes 重放 15/15 OK: DONE 计数与 07-15 记录期望逐一相等 (LB 10×24; TB 32/32/30/23/23,
      合计 244 条), r(###)=0, 僵尸滞留 14/15 按 K7 护栏击杀 (与 07-16 全谱系统性记录一致)
- [x] §4.6 提交推送 main (本 commit)
