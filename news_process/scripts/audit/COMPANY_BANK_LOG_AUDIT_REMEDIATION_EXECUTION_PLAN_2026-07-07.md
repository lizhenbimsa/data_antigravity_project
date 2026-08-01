# company_listed_bank 日志审计整改执行计划 (2026-07-07)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 审计对象: `company_listed_bank/logs/` 全部 4 份日志 (01/02/03/run_pipeline, 共 228 行, 逐行读毕)。
> 审计方法: 日志 ↔ 脚本源码 ↔ 测试夹具 ↔ 产物 mtime ↔ registry 哈希 五方交叉, 三轮确认。
> 总结论: **流水线三步 (10:46–11:17) 生产运行全部成功, 产物完整; 数据本身零异常。**
> 唯一真实缺陷是日志基建 (P0-A); 其余为需跟踪的已知口子。全部整改 $0 纯 CPU, 无 M0 审批门问题。

---

## §0 审定问题清单 (终版, 定级)

| # | 级别 | 问题 | 证据链 |
|---|------|------|--------|
| A | **P1 缺陷** | pytest 负例测试调 `mod.main()` → `_init_stage_logging` → `setup_logging` 首写截断, **覆盖了 10:47 成功生产运行的 02 日志**; 随后同 pytest 进程 (PID 99508) 内 `test_abs_year_domain_systemexit` (2000 篇×3 轨=6000 条 1970 年夹具 → "剔除 6000 (100.000%)") 与 `test_cross_year_warning` ("跨年 1 篇") 的 WARNING 追加进同一文件, 拼出一份**酷似"生产半途崩溃"的假日志** | 02 日志时间戳 11:18:18 晚于流水线收官 11:17:42; 工作目录=repo 根 (测试约定); 按 `build_year_map` (02 脚本 :257-263) 两行日志互斥; 测试夹具行数逐字对上; 产物 mtime 证 10:47 运行成功 |
| B | ✅ by-design (R1 改判) | 01 日志: 4 基名白名单豁免 WARNING (`llm_vote_tone_std` / `avg_subst_prob_score` / `avg_locus_prob_score` / `avg_collab_prob_score`) — R1 审核证实为 WP0-6 ③ 刻意审计留痕 (`INCLUDE_WHITELIST` 即正式 SSOT), 非缺口; 详见 §2 | 01 日志 :42-45; 01 脚本 :278-285, :528-536 |
| C | P2 跟踪 | 01 日志: 3 个注册基名盘上缺全部源列 (`cross_outlet_tone_variance` / `cross_media_alpha` / `n_events`) → 面板出**全 NaN 空壳列** (共享树 40 面板漂移/DEFERRED) | 01 日志 :46-49 |
| D | P2 跟踪 | 03 日志: DV2 未映射银行名 **18,297 种** (日志自标"关注"); 另有 分支权源 10 家公司缺 city (分支权全缺失) + 贷款公司码未命中 1,138 行 | 03 日志 :44,46,78 |
| E | P3 性能 | 03: branch 面板构建独占 22 分 42 秒 (10:49:47→11:12:29, 长表 405 万行, 七权源最大); RSS 峰值 2.77GB — **这是 T=2 dev; 生产 T=19 须重估** | 03 日志 :55-56,92 |
| F | ✅ 已闭环 | run_pipeline 尾行"registry sha 须 bump"提示 — 实测 `023cdc91…` 与 `tests/test_company_bank_cooc_registry.py::EXPECTED_REGISTRY_SHA256` 及 yaml 内嵌哈希**三方一致, 无需动作** | 本审计实测 |
| G | P3 缺陷 (R2 补) | 03 脚本两处**无参** `logger.info` 写 `%%` → 日志出现字面 "A≥90%%∧B≥95%%" (% 折叠仅在带 args 格式化时发生); 01/02/runner 已扫描无同类 | 03 日志 :13,:77; 03 脚本 :82,:1095 |
| A′ | ⚠ 升级 (R2 补) | 02 日志于 **13:39 被 pytest 第三次覆盖** (PID:2308, 同签名: header+两条夹具 WARNING, 45 行/2 秒) — 覆盖非一次性事故而是**复发性污染**, 每跑一次相关测试就清一次 | 02 日志现况实读 (10:47 生产→11:18 覆盖→13:39 再覆盖) |

补充确证 (审核第三轮):
- 覆盖机制 = `core/logging.py::_DelayedTruncatingRotatingHandler` (:155-180) "本进程首写截断" (`file_mode='w'`) — 主管道刻意设计 (每次运行只留最新), 病根在**测试进程也走了这条路**。
- 01/03/run_pipeline 与 02 是同一 `_init_stage_logging` 模式 (01:44 / 03:41 / runner:42), 但其测试目前**不调 main()** → 现阶段仅 02 实际中招; 01/03 属潜在同病, 修复须四处同步。
- 丢失的 10:47 生产 02 日志**不可恢复**; 其运行成功性由间接证据链确认 (run_pipeline 报完成 72s + pair/panel mtime + 03 读 pair 6,159 行且 registry 指纹校验通过)。

---

## §1 WP-A (P1): 堵死"pytest 覆盖生产日志" — 本计划核心

**方案**: `_init_stage_logging()` 开头检测 pytest 环境即 no-op:

```python
def _init_stage_logging() -> None:
    import os
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return  # 测试进程绝不接管文件日志 (2026-07-07 审计: 负例测试曾覆盖生产 02 日志)
    ...
```

- **四处同步改** (同模式同修, 缺一即残留病灶): `company_listed_bank/{01_build_company_bank_cooc_registry,02_build_company_bank_cooc_panel,03_build_company_bank_weight_validation,run_pipeline}.py`。
- **不动** 02 脚本现有 `propagate = True` 修复 (2026-07-07 实弹注释: 保 caplog 可捕) — no-op 早退后该行不执行, 但 logger 从未被 setup_logging 置 False, 默认即 propagate=True, caplog 语义无损; 仍须跑 `test_cross_year_warning` 实证。
- 注记 (R1): `PYTEST_CURRENT_TEST` 会被子进程继承 — 若未来测试拉起 run_pipeline 子进程, 子进程同样跳过文件日志, **这恰是期望行为** (测试永不写生产日志), 非副作用。
- **新增 gate 测试** (加入 `tests/test_company_bank_cooc_panel.py`): 在 pytest 内调 `mod._init_stage_logging()` + 一条 `mod.log()`, 断言 `company_listed_bank/logs/02_*.log` 的 mtime/内容不变 (文件不存在则断言仍不存在)。覆盖三脚本可参数化。
- 先例参照: 与 stage66/70 借用 21 号 logger 首写截断同类病 (`tone-llms-logger-redirect-2026-06-27`), 但方向相反 (彼=生产内互踩, 此=测试踩生产), 修法独立。

**顺序铁律 (R2)**: "重跑 02 补健康日志"**必须在守卫落地并验证之后**执行 — 否则下次任何人跑相关测试, 健康日志再次被清 (13:39 已实证第三次覆盖)。
**附带小修 (R2, 与 WP-A 同 commit)**: 03 脚本 :82/:1095 两处无参 `logger.info` 的 `%%` → 单 `%` (纯日志字面, golden-safe; 01/02/runner 无同类)。

**验收**: ① 修复后跑 `pytest tests/test_company_bank_cooc_panel.py tests/test_company_bank_cooc_registry.py tests/test_company_bank_weight_validation.py -v` 全绿; ② 跑完测试后 4 份日志 mtime/内容零变化; ③ `test_cross_year_warning` caplog 仍捕获; ④ 重跑 03 (或下次生产跑) 日志中 "A≥90%∧B≥95%" 单百分号正常。

## §2 WP-B (R1 审核后降级: 刻意不做, 留可选路径): 4 条白名单豁免 WARNING

**R1 审核推翻原定性** (读 01 脚本 :278-285, :514-536 证实): 这 4 条 WARNING **不是缺口, 是 by-design 审计机制**——
- `INCLUDE_WHITELIST` 常量 + WP0-6 ③ 补注册循环就是 v33/v34 计划评审定下的正式 SSOT; WARNING 是"白名单豁免列须证入纳入域"核查义务的**刻意留痕**, 消掉反而丢审计信号;
- CUT_LIST_v23 的 CUT 侧被硬闸锚死"恰 410 基名" (:516-517, 不等即 SystemExit), 且负清单是带评审史的冻结产物; 真要收编须动 KEEP 段 + 版本 bump v23→v24 + 01 脚本内文件名引用同步 + 条目序变 → sha 变 → 测试锚 bump + 级联 02→03 (~31 分钟)。
**判定**: 成本 ≫ 收益 (仅消 4 条刻意 WARNING), 归入 §7 刻意不做。可选路径 (仅当未来 CUT_LIST 因其它原因升版时顺带): 把 4 基名并入 KEEP 段, 使补注册循环静默跳过。

> 注: WP-B 降级后, 本计划不再有任何触发 registry sha 变更的工作包; 全链重跑 (为补回 02 健康日志) 产出 sha 应与现锚 `023cdc91…` **一致**, 不一致即新漂移须停下排查。

## §3 WP-C (P2): 3 全 NaN 基名上游回填跟踪

- 归属主管道 (40 面板漂移), 非本流水线缺陷。行动: 生产复跑前核查 `cross_outlet_tone_variance` / `cross_media_alpha` / `n_events` 是否已回归 40 面板;
  - 已回归 → 级联重跑本链, WARNING 自消;
  - 长期缺席 → 在 registry 条目加 DEFERRED 注记 + codebook 披露"空壳列", 防下游误用全 NaN 列进回归。
- 验收: 01 日志该 WARNING 消失, 或 codebook 有显式空壳披露 (二取一)。

## §4 WP-D (P2): DV2 未映射名称复核

- 读 `company_listed_bank/data/_company_bank_weight_validation.md` 审计附录 top-50, 人工判定是否存在**高频且可映射**的银行名变体 (有 → 补 DV2 映射规则, 注意与 registry 区段双向锁联动, 同样触发 sha 级联);
- 生产 T=19 复跑时把"未映射种数/占比"列入必查项 (当前 18,297 种是 dev 语料基数, 生产口径须重估)。
- 附带: 分支权源缺 city 的 10 家公司与贷款未命中 1,138 行在生产语料上复核规模, 无需改代码 (均已显式记账无静默丢弃)。

## §5 WP-E (P3, DEFERRED 至生产前): branch 性能与内存重估

- 生产 T=19 首跑前 profile 03 的 branch 构建段 (dev 已 22m42s / 405 万行长表; RSS 2.77GB @T=2):
  - 长表行数随语料×年数放大, 先以生产四权源 dta 实际行数外推;
  - 若外推 RSS 逼近机器上限 (128GB), 按 boilerplate tier2 先例做分块 (镜像 `BOILERPLATE_..._OOM_HARDENING` 计划方法论);
- 与主管道既有铁律并列: 此为 company_listed_bank 链生产首跑前的第二个容量闸 (第一个是主管道 stage-22 的 §3-P0 校准)。

## §6 总验收 gate (全 WP 完成后)

1. 三测试文件全绿 + 全量 `pytest -m fast` A/B 差分 0 新增失败 (baseline-stash 法, committed golden 本就陈旧);
2. 跑完 pytest 后 `company_listed_bank/logs/` 4 份日志 mtime 零变化 (WP-A gate);
3. WP-A 落地后**单独重跑 02** (72 秒, 幂等; WP-B 降级后无 sha 变更, 无需 31 分钟全链) → 02 日志含完整收尾 banner ("阶段执行完毕"), 假日志被健康日志替换; 重跑后 pair/panel 列内容哈希与现盘一致 (§5.3 确定性实证口径), 03 产物无需重产;
4. registry sha 三方一致且**等于现锚** `023cdc91…` (yaml / 测试锚 / 日志; 变了=新漂移, 停下排查);
5. 产物 (~13GB) 不入库 (`.gitignore` 已覆盖, 恒例); 提交 by-name, 排除 `*constants.json`/eval_reports 等并发产物。

## §7 刻意不做 (归档)

- **WP-B "收编 4 白名单基名进 CUT_LIST" (R1 审核降级)** — 4 条 WARNING 是 WP0-6 ③ 刻意审计留痕, `INCLUDE_WHITELIST` 已是正式 SSOT; 收编须动冻结负清单 (v23→v24 + 恰410锚 + 脚本引用 + sha 级联), 成本 ≫ 收益, 详见 §2;
- 恢复被覆盖的 10:47 生产 02 日志 — 物理不可能, 由间接证据链归档其成功性 (本文件 §0-A);
- 给 01/03 的测试补 main() 调用 — 无此需求; WP-A 的 no-op 守卫 + gate 测试已覆盖三脚本;
- 改 `setup_logging` 本体 (core/logging.py) — 主管道 35 shim 共用, "每次运行只留最新"是刻意设计; 修在 company_listed_bank 侧入口, 不动 kernel;
- 把 branch 22 分钟当 bug 修 — dev 语料下属数据规模驱动, 无算法错误证据; 归 WP-E 生产前重估。

---

## §8 计划审核史

**R1 (2026-07-07, 对照 01 脚本源码逐 WP 复核)** — 1 实质推翻 + 2 小修 + 1 优化:
1. **推翻 WP-B 原定性** "CUT_LIST 4 基名缺口须收编": 读 01 脚本 :278-285 (`INCLUDE_WHITELIST`) 与 :528-536 (WP0-6 ③ 补注册循环) 证实 4 条 WARNING 是刻意审计留痕、白名单即正式 SSOT; 且 CUT 侧恰410硬闸 (:516-517) + 负清单为冻结评审产物 → 收编成本 ≫ 收益 → 降级入 §7。**教训 (镜像 A1-ECE 先例): "有 WARNING" ≠ "有缺口", 定性前必读产 WARNING 的代码及其设计注释。**
2. 小修: WP-A 守卫早退后 `propagate=True` 行不执行 — 确认 logger 默认即 True, caplog 无损 (原表述含糊)。
3. 小修: 注记 `PYTEST_CURRENT_TEST` 子进程继承是期望行为而非副作用。
4. 优化: WP-B 降级后全计划零 sha 变更 → 补 02 健康日志只需单独重跑 02 (72 秒幂等), 免 31 分钟全链; §6 gate 相应改为 "sha 必须等于现锚, 变了即停"。

**R2 (2026-07-07, 最高质量终审: 对抗性重扫日志原文字节 + 全脚本 pattern 扫描)** — 1 新缺陷 + 1 升级 + 1 假疑点排除:
1. **新缺陷 §0-G (首轮审计遗漏, 违反"零遗漏"承诺处诚实记账)**: 03 脚本 :82/:1095 无参 `logger.info` 内 `%%` 未折叠 → 日志字面 "90%%"; 修法并入 WP-A 同 commit。教训: 日志审计除语义外须扫**格式化残留** (`grep '%%'` 无参调用面)。
2. **升级 §0-A′**: 实读发现 02 日志已于 13:39 被 pytest **第三次**覆盖 (PID:2308) — 覆盖是复发性污染非一次性事故; WP-A 增加顺序铁律: 守卫先落地, 再补跑 02。
3. **假疑点排除**: 02 脚本 "输入(16\27\51)" 反斜杠八进制转义嫌疑 — `cat -A` 逐字节证实源码为 `(16/27/51)` 正斜杠, 系 Grep 工具输出的显示转义假象。教训: 字符级嫌疑必须 `cat -A` 验原始字节, 不能信工具转印。
4. 其余全部计划主张 (WP-A 机制/顺序耦合/WP-C/D/E/§6 gate/§7) 逐条复验通过, 无进一步修改。**终判: converged, ok to execute。**

**R3 (2026-07-07, 终极审核: 深层假设逐条实证 + 实弹验证)** — 1 决定性新事实 + 1 实弹证明 + 遗留清单:
1. **决定性新事实: 共享树并发会话已实施 WP-A 核心** — 四脚本 (01:48 / 02:48 / 03:45 / runner:46) 于 13:53/13:55 全部落入 `PYTEST_CURRENT_TEST` 早退守卫, 注释引用本计划 "WP-A" 字样, 实现与计划一致 (四处同步 ✓)。**本会话勿再编辑这四个文件, 防并发冲突** (承共享树 by-name/独立 worktree 先例)。
2. **实弹验证 ✅**: 跑 `test_company_bank_cooc_panel.py` 全部 34 项 (含调 main() 的负例) 全绿, 跑后四日志 mtime 与 02 日志 md5 **逐字节不变** — 守卫端到端有效, §6 gate-2 已提前兑现。
3. 顺带实证: "单独重跑 02 幂等" 的前提 (13:35 后改动仅限日志/路径注释层) 经 unstaged diff 抽查确认, 且 02 现输出目录=company_listed_bank/data/ (staged 版曾是 data/processed/, 以 worktree 版为准)。
4. **遗留三件 (执行方待办, 与并发会话协调后做)**: ① 03 脚本 `%%` 两处 (行号已漂移至 :85/:1098) 未修; ② §1 gate 测试未加 (R3 实弹已人工代证一次, 但须固化为回归测试); ③ 02 健康日志未补跑 (现盘仍是 13:39 污染版; 守卫已落地, 现在补跑即安全)。
**R3 终判: 计划三轮收敛无遗留缺陷; 核心修复已由并发会话落地并经实弹证明有效; 剩余为三件收尾。**

---

## §9 执行记录 + 执行后审核 (2026-07-07 14:01–14:15, 用户授权)

**并发安全协议**: 执行前后台监视源文件 mtime, 静默 120s+ 且无 `.tmp.*` 原子写残留才动手; 全程零撞车 (03 文件尺寸差恰等于本次删除的 4 字符)。

| 项 | 动作 | 审核证据 |
|----|------|----------|
| ① %% 修复 | 03 脚本 :85/:1229 两处无参 `%%`→`%` | `py_compile` 过; 复查现存 10 行 `%%` 全部位于**带参**格式化调用内 (合法转义), 零残留 |
| ② gate 测试 | `test_pytest_never_touches_stage_logs` 参数化四脚本 (mtime/size 快照恒等 + 无 FileHandler 双断言) 入 `tests/test_company_bank_cooc_panel.py` | 单跑 4/4 绿; 并入全量 99 项 (95+4) 全绿 exit 0 |
| ③ 02 健康日志补跑 | 独立重跑 02 (14:08:09–14:11:40, 211s), 115 行完整日志替换 13:39 污染版 | 首尾 banner 完整; 唯一 WARNING="40 个加权列全 NaN (缺源列/dev 数据态)"=§0-C 已知 dev 态; **无任何合法域外/跨年警告** — 反证假日志判定 |
| 幂等 gate | 重跑前快照 pair/panel parquet 列内容 SHA256 | 重跑后 **IDENTICAL×2** (pair 6,159×10 / panel 105,032×1,913) — 03 产物无需级联 |
| 防复发终验 | 三测试文件全量跑两遍 (含调 main() 负例) | 跑后四日志 md5 逐字节 OK — 守卫 + gate 测试双层防线在位 |

**执行后审核结论: 计划全项落地, 全 gate 通过, 零回归, 零并发冲突。** 遗留仅 §3-§5 生产前跟踪项 (WP-C/D/E, 无本机动作)。注: 重跑耗时 211s 高于历史 72s, 推断系并发会话 13:58 日志富集增加 I/O 汇报所致 (产物内容哈希不变, 无实质影响)。

**R4 终验 (2026-07-07 14:15+, 最高标准全量复核 — 专攻执行动作的次生损害面)**:
1. **高危假设排查→推翻**: "02 重跑冲掉 03 写入 codebook 的七权章" — 实测章节完好 (BEGIN :143→END :215), 且 02 `write_codebook` 自带保留逻辑 (:776-779, v34 R3 P1-2 预防在位) → 零次生损害。⚠ 途中自纠一次 grep 假阴性: "七权" 二字组在 "七替代权面板" 中不连续, 首次 grep 计 0 误导 → 以章节目录+标记行复核纠正 (教训: 中文关键词 grep 须用原文全词)。
2. pair parquet 自定义元数据健在: `registry_sha256=023cdc91…` (等锚) + `input_fingerprint` → 03 后续消费无碍。
3. gate 测试四模块 importlib 解析路径逐一实测 = company_listed_bank 下正确文件, 无 sys.path 劫持。
4. 三测试文件零 "90%/95%" 日志字符串断言 → %% 修复不可能破测试 (且修复后全量 99 项已两次全绿)。
5. 新 02 日志全量告警扫描: 恰 1 WARNING (已知 dev 态) / 0 ERROR / 0 CRITICAL。
6. git 暂存区未被本会话触碰 (index 中 03 为并发会话所 add; 本会话改动均在工作区, 未越权 stage/commit)。
7. 过程小疵如实记账: 两个临时 md5 比对文件曾落 /tmp (按会话规范应用 scratchpad); 幂等基准 JSON 已按规范存 scratchpad, 交付物零影响。
**R4 终判: 全部交付物 (代码修复/gate 测试/健康日志/产物幂等/计划/记忆) 复核完毕, 无错漏。**
