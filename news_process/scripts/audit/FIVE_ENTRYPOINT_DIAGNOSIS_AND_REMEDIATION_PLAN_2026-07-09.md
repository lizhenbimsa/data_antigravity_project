# 五入口顺序执行 — 诊断与整改执行计划 (最终版)

> 日期 2026-07-09 · HEAD 2eeb65e9 · 执行环境: OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP_NUM_THREADS=1 / HF_HUB_OFFLINE=1)
> 用户决策: 真跑+保留新产物 · company 全链含 01 · run_paper dry-run 全部 + 实跑 bank_fintech_tone
> 本版已吸收: 16 问题对抗验证 + 三轮独立最高标准评审(完整性/技术正确性/可执行性) + 首席综合(20 agent, 裁决=ship-after-revisions)

## 0-bis. 实施状态 (2026-07-09 已落地)
✅ **全部 A1-A10 + B4 代码修复 + pytest 回归 gate 已实施** (20 文件: 18 改 + 2 新增); ruff `All checks passed`; 40 个相关 gate 全绿 (含 test_pipeline_runner_bridge / test_run_paper_dispatcher / test_run_pipeline_function 无回归)。经实施前最后一次计划评审 (7-agent, classificationFinal=true) 与实施后三轮结果评审收口。
- **批次1**: A1 兜底 console handler (io.TextIOWrapper errors=backslashreplace + try/except 回退 + import io) · A4 dry-run 语义 (env 构造/日志移到 continue 后) · A6 子进程 env 精确 5 键 (PYTHONUNBUFFERED/PYTHONIOENCODING=utf-8:replace/PYTHONUTF8/KMP_DUPLICATE_LIB_OK + 强制 HASHSEED=0), company_tax 01/02/03 + company_listed 全步
- **批次2**: A5 锁 acquire 留 try 外 + _init 入 try + 双 `if not args.dry_run` 守卫 + finally 释放 · A9 os.write OSError → close(fd)+unlink 再抛
- **批次3**: A2 validation argparse (-h/--help + --dry-run 用 print 不获锁) · A3 RUN_ID emit 下沉函数入口 (保留模块级 logger) · A10 run_main_pipeline(argv) 透传 + 11 家 analysis parse_known_args + bridge 零参兼容
- **批次4**: A7 `--no-emit-dta` 对 02 固定 + 03 glob 的 .dta 统一守卫 · B4 `_stage21_skip_is_compatible` 按 `_full` 后缀匹配 · pytest gate (test_five_entrypoint_hardening + 扩展 lock ×2)
- **B/C 类** (I-1/F7/P#5/F3/B5/B6/II-1/A8/I-2/II-2): 文档/守卫/by-design, 说明见 §3/§4/§5。

## 0. 结论速览
- **入口运行**: ①主线 ②验证 ③run_paper ④company_listed ⑤company_tax **5/5 全部真实运行成功坐实 (EXIT=0)**。⑤ 03 重跑 **TAX03 EXIT=0**(墙钟 3552s≈59min · budget 1.0B 双加权引擎 + 双 6.5GB dta 写盘 · 0 真 ERROR · 双 dta/parquet+互验报告全刷新 10:xx · 无残留进程/锁)。**首次 03 会话级后台中断已排除(非 pipeline 缺陷): tax 03 近 1 小时远超其它入口(①16.5min/②3.5min/③16min/④11min), 触后台任务上限; 属残余风险 §7-1 运营项。**
- **运行期无任何真 ERROR、无崩溃、无付费** (LLM+嵌入+BERT 全 OFFLINE 命中, stage21 缓存 13896/0-miss)。全部 stage 级 WARNING 均为 **T=2 dev 语料预期退化**或 **by-design 优雅降级**, 无一为真缺陷。
- **真正的整改对象 = 入口脚本层 (orchestrator/CLI/日志) 健壮性 + 跨模块顺序耦合**, 全部 **golden 安全**(只动 orchestrator/CLI/日志层, 不触测度/parquet/缓存/确定性逻辑)。
- **问题定级(经对抗验证+三轮评审修订)**:
  - **A. 真缺陷 (建议修复) 8 项**: A1 · A2 · A3 · A4 · A5 · A7 · A9 · A10 (A1 为 latent 纵深防御, 唯一触发=A4)
  - **B. 设计特性/需文档或守卫 7 项**: B1(I-1) · B2(P#5) · B3(F3) · B4(F6) · B6(F12) · **A6(F2, 由 A 降入: 潜伏确定性缺口)** · **F7(由 C 升入: 条件性顺序耦合)**
  - **C. 已核实 by-design/预期 (仅记录) 9 项**: I-2 · II-1 · II-2 · 主线 T=2 退化 WARNING 族 · **validation 侧 by-design WARNING(61/62/63/64/67)** · **A8(F5, 由 A 降入)** · **B5(F-config, 由 B 降入)** · F8 · F9
- **无 P0 代码级阻断**; 假阴性排查(I-2/II-1/II-2/F8/F9)与假阳性排查(A 类无把 T=2 退化误当缺陷)均确认干净。

## 1. 运行结果总览
| 入口 | 结果 | 墙钟 | 关键观测 | 日志锚点 |
|------|------|------|----------|----------|
| ① run_pipeline_function | ✅ EXIT=0 | 989.3s | 全16阶段✓; stage00=522s(53%); 嵌入15/16/25/26+LLM21+BERT23 全 OFFLINE 命中$0; 全 WARNING=T=2退化 | 01_run_main.out:16327 |
| ② run_pipeline_validation | ✅ EXIT=0 | ~3.5min | 全16阶段(60-75)✓; 72最慢148.6s; 66/70 OFFLINE 优雅跳过(冷缓存变体prompt) | 02_run_validation.out(VALIDATION EXIT=0) |
| ③ run_paper | ✅ EXIT=0 | dry-run×11 + 984.9s | dry-run全11篇✓; --stage all=主线重跑984.9s(≈①989.3s确定性等价)+Table1 CSV+Figure1 PDF | 03_run_paper_tone.out(PAPER EXIT=0) |
| ④ company_listed_bank | ✅ EXIT=0 | 680.4s | 01(3.6s,registry sha 023cdc91幂等)→02(76.8s)→03(599.3s/12.6GB); **git干净**(registry.yaml字节不变); I-1下游传导 | 04_run_listed.out(LISTED EXIT=0) |
| ⑤ company_tax_bank | ✅ EXIT=0 | 01=16.8s · 02=263.1s · 03=3552s(59min) | 01(sha 4f580e3f匹配锚)+02(6558MB dta)+03(双权源 city引擎1466s+county引擎, 双6.5GB dta+双parquet+互验md全刷新10:xx, 0 ERROR, 无残留); 首次03偶发中断已重跑坐实 | 05b:262/316 TAX03 EXIT=0 |

**入口④ I-1 下游传导实证**: 04_run_listed.out 报 `3 个注册在案基名盘上缺全部源列`= cross_media_alpha / cross_outlet_tone_variance / n_events → cross_media 相关权列全 NaN(优雅降级非崩); 根因见 B1。
**确定性验证**: 入口③ pipeline 984.9s ≈ 入口① 989.3s, run_paper→run_main_pipeline→run_pipeline 封装等价。**成本**: 全程 $0。
> **⑤ 03 坐实行 [待补]**: 核 05b 出现 `步骤 03 完成`+`全部步完成`+`三权互验报告` 收尾 banner + company_tax_bank/data 下 branch_city/county 双 dta+parquet 齐备 + TAX03 EXIT=0, 方可把 §0 升为 5/5。

## 2. A. 真缺陷 (建议修复, 全 golden 安全)

### A1 · [低·latent 纵深防御] company_* orchestrator 兜底 console handler 遇 emoji → UnicodeEncodeError
- **位置**: company_tax_bank/run_pipeline.py:46-51 (模块顶兜底 StreamHandler) + :464-467 (env 注入日志含 ⚠ U+26A0); listed 同构兜底 handler 但**无现成 emoji 触发点**(其 dry-run 可达路径 :434-440 仅 emit `─`(U+2500,在GBK码表)+desc+命令)。
- **根因**: dry-run 不走 `_init_stage_logging`(:360)→不走 setup_logging 的 `_configure_standard_streams`(core/logging.py:50-56)reconfigure; 兜底 handler 写未 reconfigure 的 cp936 stdout。**唯一现存触发路径 = A4 的 dry-run emoji 泄漏**(:464 的 ⚠), A4 修复后本条在所有路径不再可复现 → 实为纵深防御, 非独立活跃 bug。
- **失败场景(已复现)**: 裸 `--dry-run` 在**重定向/管道/legacy-stdio stdout(cp936)** 下 → step03 ⚠ 触发 UnicodeEncodeError, 被 logging.handleError 吞(非致命)、丢该行。(现代交互控制台走 _WindowsConsoleIO(utf-8) 不崩; 自动化恒重定向故仍真实。)
- **修复(评审精修)**: 优先给兜底 StreamHandler 包 `errors='backslashreplace'` 的流; **或与 A4 合并**(把 :459-470 移到 `continue` 之后)直接消除触发点。**⚠ 不要在 import 期对全局 sys.stdout/stderr 做 reconfigure**(会干扰 pytest capture / --help / 父进程)。
- **golden**: 安全(仅 console 编码)。

### A2 · [中] run_pipeline_validation.py 无 argparse → 误参数/--help 即全量实跑+持锁
- **位置**: run_pipeline_validation.py:294-295 `if __name__=='__main__': run_validation()` (全文 Grep 零 argparse/parse_args/add_argument)。
- **根因**: 与主线 `_parse_cli_args`(:499)+`__main__`(:828) 不对称; Python 忽略 sys.argv → 任何参数(含 `--help`)静默进 `run_validation()`(:142)→ 无条件 `with PipelineLock`(:173) 全量实跑 16 阶段(:253)。
- **失败场景(已亲历)**: `python run_pipeline_validation.py --help` 立即全量实跑并覆写 stage61 human_samples 等产物; 无 `--dry-run` 预检。(OFFLINE 下 $0, 仅覆写产物+占锁~3.5min, 无数据正确性损害 → 定[中]。)
- **修复**: 对称主线加 argparse: `-h/--help`(argparse 自带) + 可选 `--dry-run`(只打印 STAGES_VALIDATION 清单不获锁不实跑); 保留无参=全量默认(向后兼容, 不影响 test_dag_consistency 的 import)。
- **golden**: 安全。

### A3 · [低] 主线/验证入口 import 期即截断对应 .log
- **位置**: run_pipeline_function.py:110-111 / run_pipeline_validation.py:75-76 (模块级 `logger=setup_logging` + 立即 `logger.info(RUN_ID)`)。
- **根因**: `_DelayedTruncatingRotatingHandler`(delay=True) 本身不截断, 是相邻的立即 `logger.info(RUN_ID)` 首写 emit 触发 `_open()` 以 mode='w' 截断上次日志。`--help`/pytest import 同理。
- **修复(评审最小改法, 零 churn)**: **模块级保留 `logger=setup_logging(...)`(delay 下 import 不截断), 仅把 :111/:76 唯一的 `logger.info(RUN_ID)` 单条 emit 下沉进 `run_pipeline()`/`run_validation()` 入口**(配 `global logger`)。**⚠ 禁止搬迁 setup_logging 或模块级 logger 绑定**(两文件 66-80 处 logger 引用, 下沉会 NameError)。须一并覆盖 **run_paper→run_main_pipeline 懒 import 触发 :111 emit 的同源截断路径**。A3 独立成 commit 便于复核。
- **golden**: 安全(仅日志时机)。

### A4 · [低] company_tax dry-run 在 continue 前构造 child_env + 打印含 ⚠ 的 env 注入日志
- **位置**: company_tax_bank/run_pipeline.py:459-470 (child_env 构造 :461 + env 注入日志 :464-467, ⚠ 在 :466) 在 `if args.dry_run: continue`(:472) 之前, 无 dry_run 守卫; `--steps` 默认含 03 故裸 `--dry-run` 必触发。
- **失败场景**: dry-run 输出多余 env 注入日志(违反"只打印命令"语义, 且文案误导——dry-run 未真注入) + 触发 A1 的 UnicodeEncodeError。
- **修复**: 把 :460-470 移到 `continue` 之后, 或加 `if not args.dry_run` 守卫。**⚠ 须保留 :471 命令打印在 continue 之前**(属 dry-run 合法输出, 勿连带移动)。与 A1 一并修(批次1)。
- **golden**: 安全。

### A5 · [低] company_* 锁 acquire+init 在 try/finally 之外 → init 失败 fd 泄漏+锁残留
- **位置**: company_listed_bank/run_pipeline.py:342-353 · company_tax_bank/run_pipeline.py:359-370 (`lock_fd=_acquire_single_instance_lock()` + `_init_stage_logging()` 在 `try:` 之前, 仅 `_run()` 被 try/finally 包)。
- **根因/边界**: `_init_stage_logging()`(:45-59) 可抛(importlib exec_module / setup_logging 'w' 开文件 OSError) → finally 不执行 → fd 泄漏 + 锁残留(含死 PID)。**评审降级依据**: `_acquire`(:83-108) 有陈旧锁 PID 存活自愈(读残留 PID→判死→清除重试), 进程崩溃后 fd 由 OS 回收、残留锁下次自愈; 真硬失败仅"崩溃 PID 被无关进程复用→误判拒启"这一窄边界。与姊妹 A9 同构[低]。
- **修复(评审承重铁律)**: **保持 `_acquire_single_instance_lock` 先于 `_init_stage_logging`**(锁须先于 setup_logging: 否则被拒的第二实例经 'w' 开日志会截断在跑实例的 run_pipeline.log); 结构改为 `lock_fd=acquire()` → `try: _init_stage_logging(); return _run()` → `finally: if lock_fd is not None: release`。被拒实例报错仍走模块顶 console 兜底(不触盘)。
- **golden**: 安全。

### A7 · [低] tax --no-emit-dta 下对**步骤 02**故意跳过的 .dta 报"产物缺失"WARNING
- **位置**: company_tax_bank/run_pipeline.py:254-274 `_log_step_done` → `_iter_artifacts`(:173-195), warning 在 :266。
- **范围(评审收窄)**: **仅步骤 02 触发**——其 dta 是**固定路径**(:179 无条件 yield), `--no-emit-dta` 下 write_outputs(:599)显式 unlink 陈旧 dta → 必缺席 → 报"产物缺失"。**步骤 03 的 dta 是 glob 枚举**(:190 `glob("*w_panel.dta")`), `--no-emit-dta` 下 glob 为空 → 不 yield → **不告警**。计划初稿"02/03 都报"为高估, 已更正。
- **修复**: `_iter_artifacts`/`_log_step_done` 感知 `no_emit_dta` 跳过 dta 检查或降 info(需新增 flag 入参, 签名微改无风险)。**顺带隐患**(评审提示, 可选): 非 `--no-emit-dta` 下若盘残留陈旧 dta, glob/固定路径会把旧 dta 当新产物汇报。
- **golden**: 安全(仅日志)。

### A9 · [低] _acquire_single_instance_lock 在 os.write 失败时泄漏 fd
- **位置**: company_listed_bank/run_pipeline.py:85-87 · company_tax_bank/run_pipeline.py:95-97 (L85/95 `os.open(O_CREAT|O_EXCL)` 后 L86/96 `os.write(fd,pid)`, except 仅捕 FileExistsError)。
- **失败场景/边界**: `os.write` 抛非-FileExistsError 的 OSError(ENOSPC 磁盘满)→ 绕过 except 上抛, fd 未 close → 泄漏 + 留 0 字节锁文件。**评审注**: 触发极罕见(4 字节 PID 写入遇磁盘满); 且 0 字节锁下次启动 `read_text().strip() or "0"`→holder=0 falsy→直入陈旧锁 unlink 重试, 不持久阻塞。
- **修复**: `os.write` 包 try, 失败则 `close(fd)`+`unlink(missing_ok=True)` 再抛。与 A5 一并加固锁路径(批次2)。
- **golden**: 安全。

### A10 · [低中] run_paper 无法把流水线 flag 透传给主管道
- **位置**: run_paper.py:748-751(`forwarded.extend(unknown)`)+ papers/bank_fintech_tone/analysis.py:54(`parse_args` 严格) + pipeline_runner.py:29(`run_main_pipeline()` 无参→run_pipeline() 默认 Namespace)。
- **失败场景**: `run_paper.py bank_fintech_tone --skip-21-if-exists` → flag 进 unknown → 透传给 analysis 严格 `parse_args` → SystemExit(2); 即便改 parse_known_args, run_main_pipeline 无参仍静默丢 flag。**双重缺陷**(半实现转发契约)。
- **修复(评审明确覆盖范围)**: ① analysis 改 `parse_known_args`(注意会静默吞真拼错 flag, 轻微回退); ② **须对所有能跑 `--stage pipeline` 的 paper 统一处理**(仅改 bank_fintech_tone 一家则跨 paper 不一致), 或在 run_paper 层白名单化流水线 flag 后转发; ③ 打通 `run_main_pipeline(args=None)→run_pipeline(args)` 通道(加形参即可, 5 处调用向后兼容)。
- **golden**: 安全(`--skip-21-if-exists` 命中与否在缓存 0-miss 下数值等价)。

## 3. B. 设计特性 / 需文档或守卫

### B1 · [中] I-1 主线↔验证 cross_media 顺序耦合 (真·跨模块顺序依赖)
- **机制(源码核实)**: 主线 stage40 步骤8c `_merge_optin_feature_panels`(runner.py:382)用 **mtime 新鲜度守卫**(runner.py:400-404: `getmtime(上游21) > getmtime(75) → 判陈旧 → warning+跳过 merge`, fix omni-g-runner-16 刻意加)条件 merge `75_cross_media_alpha.parquet`(dag.py:456 stage75 属 validation, 不在主线)。
- **传导链(双实证)**: ①本会话 03_run_paper_tone.out:4943 当场捕获守卫 WARNING; ②入口④ 04_run_listed.out `3 基名缺源列`→cross_media 权列全 NaN。
- **判定**: 真·跨模块顺序耦合(属 by-design 防陈旧守卫的副作用, 非代码 bug); 优雅降级非崩。
- **处理**: 见 §5 (执行顺序, 已修正)。文档化 + 可选把 40 的守卫 WARNING 升为更醒目的摘要行(仅日志安全, 勿接失败 gate)。

### B2 · [文档] P#5 run_paper <paper> --stage all = 再次全量重跑主线, 非触发 Stata
- **事实**: analysis.py:74-76 → run_main_pipeline() → run_pipeline() 跑 00→51 全主线, 无 Stata 调用; Stata 复现是独立路径 `stata_runner build-replication`。analysis.py docstring:10-14 已明确"pipeline: 运行整套数据流水线(相当于 run_pipeline_function.py)"。
- **处理**: 纯文档(对 AskUserQuestion 交互中"触发 Stata"措辞的自我纠正); 代码级文档已充分, 可选 --help/docstring 微调。

### B3 · [中] F3 company 锁与主管道 PipelineLock 互不感知 → 并发读半写 data/processed
- **机制(源码核实)**: company 锁=company_*/logs/_run_pipeline.lock(仅护本目录单实例); 主管道 PipelineLock=data/processed/.pipeline.lock; 两锁不感知。主管道 :737-744 os.remove+非原子重写窗口; company(listed 02:248 / tax 01:727)读同批 40/51/27/16/21_full。
- **实证**: 诊断中读 40_panel_yearly.parquet 遇入口③预清理删除窗口 → WinError 2。
- **处理**: (a) 文档化"company 派生管线须在主管道空闲时运行"(串行纪律); (b) company 启动时检测 data/processed/.pipeline.lock **须读 sidecar PID 做存活判定**(非仅判文件存在, 否则主崩溃残留锁误拒启动), 属尽力而为、不能消除"company 先读→主启动"窗口。**并一并说明**: listed×tax 并发(各自独立锁, 单实例锁只防同一 orchestrator 双跑; 两者仅只读 data/processed + 各写自有 data/ 目录, 风险低)。
- **golden**: 安全(仅锁/文档)。

### B4 · [低·脆弱] F6 _stage21_skip_is_compatible 依赖 OUTPUT_REGISTRY 位置序 [0]/[1]
- **位置**: run_pipeline_function.py:389([0] main)/:390([1] full) (计划初稿写 388-389, **行号更正**: 388 仅 output_dir 赋值)。
- **判定(评审)**: 非活跃 bug——`get_stage_outputs` 保序返回 OUTPUT_REGISTRY(main 在前 full 在后), 当前口径正确; 且即便手改 registry 调换, `upstream_rows≠full_rows` 或缺 `llm_verified_full` 列触 except → return False → reject skip 重跑 stage21, 是 **fail-safe**(不误用旧数据)。**"有测试守护"表述不准**(test_run_pipeline_function.py:66 硬编码正确顺序、未经 _get_stage_output_files, 不守护 registry 重排)。
- **修复(可选)**: 按 `_full` 后缀而非全名匹配(文件名可被 config['filenames'] 覆盖)。维持[低]。

### B6 · [低] F12 编排器只钉 HASHSEED=0 不 setdefault BLAS 线程=1
- **位置**: core/stage.py:255 强制 HASHSEED=0; :239-246 仅 setdefault 编码/OMP 四件套, 无 BLAS 注入。
- **判定(评审)**: **by-design 刻意不对称**——HASHSEED 强制因零性能代价且非零值会静默击穿 jieba 确定性; BLAS=1 有真实性能代价(生产 T=18 对每 stage setdefault=1 会把嵌入/网络重数值 stage 逼成单线程 BLAS 大幅拖慢正常跑)。金标 BLAS=1 靠 golden-regen SOP + M0 审批门覆盖。
- **修复(评审, fixSafe=risky)**: **以纯文档路径收口, 勿盲目在 run_stage 加 setdefault BLAS=1**。

### A6 · [低·潜伏, 由 A 降入 B] F2 company 子进程 subprocess.run 未注入 HASHSEED/UTF-8 env
- **位置**: company_listed_bank/run_pipeline.py:442(无 env) · company_tax_bank/run_pipeline.py:475(仅 step03 建 child_env 加 BUDGET, **01/02 步 env=None**); 与 run_stage:239-255(强制 HASHSEED=0 + setdefault UTF-8 三件套)不对称。
- **判定(评审降级)**: **两失败场景非活 bug, 属潜伏确定性缺口/纵深防御**——①确定性: 子脚本刻意用 sorted()(03:719/849 显式注"sorted: HASHSEED 免疫"; 01 registry 锚受 EXPECTED_REGISTRY_SHA256=4f580e3f gate 守护, HASHSEED 敏感则 gate 早 flaky)→ 现有确定性不依赖该 env; ②GBK emoji: 子脚本 main() 首条即 _init_stage_logging→reconfigure 自身 stdout, 注入前仅中文无 emoji, 窗口不存在。本轮靠父 shell 已 export HASHSEED=0 规避。
- **修复(原子化, 评审)**: **对 tax 01/02/03 全部步骤 + listed 均构造 `env=dict(os.environ)` setdefault UTF-8 三件套 + 强制 PYTHONHASHSEED=0**(镜像 run_stage:239-255), tax 03 再叠加 budget。**golden 安全前提(须显式记录)**: 本轮 registry sha=4f580e3f 恰等 gate 锚 EXPECTED_TAX_REGISTRY_SHA256(在 HASHSEED=0 下)→ 强制 HASHSEED=0 是**复现锚非改锚**; 裸跑亦收敛同锚。
- **golden**: 安全(前提已由本轮 sha 匹配坐实)。

### F7 · [低·条件, 由 C 升入 B] --skip-unchanged 开启时 stage40 漏检 75 变更
- **机制(评审纠正)**: stage40 **确登记在 STAGE_CONFIG_FILES**(run_pipeline_function.py:176)→ 是 `--skip-unchanged` 可跳候选; 而 `75_cross_media_alpha` **不在 40 的 input_hashes 追踪集**(opt-in 合并的 validation 产物)→ `--skip-unchanged` 开启时 stage40 被跳 → `_merge_optin_feature_panels` 的 mtime 守卫根本不执行 → 面板静默保留旧/缺 cross_media。**属 I-1 同族"75 未登记为 40 input"盲区的 --skip-unchanged 旁路变体**; 初稿"倾向不成立"根因判断不准, 只是被"--skip-unchanged 默认关闭 + 前缀守卫"掩盖。
- **处理**: 与 B1/I-1 合并说明; 文档化"使用 `--skip-unchanged` 时 opt-in 特征列(cross_media/staleness)可能保留陈旧值"。

## 4. C. 已核实 by-design / 预期 (仅记录, 无需修复)
- **I-2** 词典消融变体名超 Stata 32 字符: stage46 stata_export 有 `shorten_long_column_names`(缩写→截断→md5去重)+ `_assert_track_triplet_unique`(:785)+ collision raise(:818)双 fail-loud 守卫; stage46 成功=无碰撞。**已妥善处理**。
- **II-1** OFFLINE 下 66/70(entity masking / prompt sensitivity)优雅跳过: 变体 prompt 冷缓存不可离线重判, WARNING 明示"在线运行不受影响"; 属 OFFLINE 覆盖边界。**复现披露义务(评审)**: 在 replication README/data appendix 明记"66/70 两张稳健性表需在线付费 LLM 方能复现", 而非仅日志一行。
- **II-2** stage71 三轨 κ 超 sentinel 上限 0.70(locus ctx_ss=0.78/collab 0.81-0.87): T=2 小样本诊断信号, validation 职责所在。
- **主线 T=2 退化 WARNING 族**: IV弱工具/基期share one-hot退化63-87%/DiD不可识别(sandbox/dcep/depins_post全0晚于面板末年2018)/零方差(brokerage_fire_sale/numpy除零)/覆盖151→142/benefit负锚⑨投影翻正(_lg兜底)/6词典关键词含jieba边界字符剔除 — 日志自标"T=2预期", 生产 T=18 恢复。
- **validation 侧 by-design WARNING(61/62/63/64/67)** [评审补列]: 62 小样本(10076行,全量以405万行为准) / **63 demo_mode 合成标注——⚠严禁进入任何论文/复现引用(人工标注完成后重跑)** / 64 覆盖率非单调 Δα + 旧工作台 xlsx 弃用提醒 / 61 旧工作台 + 媒体占比 100%(T=2抽样倾斜) / 67 时间稳定性<3年。均预期/职责所在。
- **A8(F5)** [由 A 降入] validation 无输出预清理: 验证阶段 60-75 全在 schemas.py::EXPECTED_NO_OUTPUT_STAGES → 即便照搬主线逻辑, 预清理循环对验证阶段皆**空操作**, 不预清理是 registry 设计的直接后果(非遗漏); "半写CSV下游误读"场景弱(验证CSV不链式消费, 重跑覆盖)。**⚠ 不要对 validation 做整目录对称预清理**(可能误删 stage40 待读的 75/72/73 未登记 parquet, 与 B1 耦合冲突); 若加只补"阶段成功但登记产物缺失"存在性校验、不引入删除动作。
- **B5(F-config)** [由 B 降入] skip21 键 output_14 vs 值 15_*.parquet 编号不一致: 非缺陷——paths.yaml:77 值/代码回退(:400)/schemas.py:59 三端已对齐, skip 检查永命中真实产物; 即便失配也 fail-safe(重跑不误用旧数据)。paths.yaml:66-70 已注释声明键号为"历史稳定句柄"。加注释即可; 键名对齐有 35+ call-site churn 不建议改。
- **F8** PipelineLock unlink TOCTOU + company PID 复用: 理论边界(Windows 无 FILE_SHARE_DELETE 天然缓解)。
- **F9** PipelineLock RuntimeError 二次包裹: cosmetic(功能正确, 信息冗余)。

## 5. I-1 正确执行顺序 (§5 已按评审 P1 修正)
> ⚠ **评审当场证伪的错误顺序(勿用)**: `validation(产75)→main(全量重跑)→company`。因 main 全量重跑会**重跑 stage21 → 21_tone_llms mtime 变为最新 → 先产的 75 相对之陈旧 → runner.py:400-404 守卫仍跳过 cross_media merge**, 100% 得不到 cross_media 且静默退化(已被 03_run_paper_tone.out:4943 实证)。

**唯一 lineage 一致的正确顺序** (若需含 cross_media 列的完整面板):
```
① run_pipeline_function        (产新鲜 21_tone_llms[_full])
② run_pipeline_validation       (产 75_cross_media_alpha, 此刻 75 mtime > 21)
③ python 40_panel_export_main.py  (单独补跑 40, 不重跑 21 → 75 相对 21 恒新鲜 → 守卫放行 merge)
④ company_listed_bank / company_tax_bank  (读含 cross_media 的 40 面板)
```
**替代**(若坚持 validation 先行): main 必须传 `--skip-21-if-exists`(21 mtime 保持旧值 < 75, 守卫放行)。
**本次按用户指定顺序 ①→②→④⑤, cross_media 列缺失属预期, 已优雅降级**(company 权列 NaN 非崩)。⚠ 另: `--skip-unchanged` 开启时会跳过 stage40 绕过 75 守卫(F7), 同族盲区。

## 6. 修复批次建议 (评审修订)
- **批次1 (dry-run/编码语义, 一次提交)**: **A4**(env 构造+⚠日志移到 continue 后, 保留命令打印) + **A1**(兜底 handler `errors='backslashreplace'`; A1 唯一触发=A4, 合并后消触发) + **A6**(**原子化**: tax 01/02/03 + listed 全构造 child_env 注入 UTF-8 三件套 + **HASHSEED=0**, 显式记 golden 前提)。
- **批次2 (锁健壮性, 一次提交)**: **A5**(try/finally 边界, 保持 acquire 先于 init 的承重铁律) + **A9**(os.write 失败 close(fd)+unlink)。
- **批次3-a (validation CLI, 独立提交)**: **A2**(argparse + --dry-run/--help)。
- **批次3-b (日志截断, 独立提交)**: **A3**(最小改法: 仅下沉 :111/:76 单条 emit, 保留模块级 logger; 覆盖 run_paper 懒 import 路径)。
- **批次3-c (flag 透传, 独立提交)**: **A10**(跨 paper 统一 parse_known_args + run_main_pipeline args 通道)。
- **批次4 (次要/文档)**: A7(F4 --no-emit-dta 缺失告警) + B1/F7(I-1 执行顺序 §5 + --skip-unchanged 盲区文档) + B2(P#5 docstring) + B3(F3 跨管线并发文档/跨锁守卫) + B4(F6 后缀匹配) + B6(F12 纯文档) + C 类 II-1 复现披露 + A8/B5 注释。
- **验证升级为自动化 gate (评审 P2)**: 为 **A2/A3/A5/A9/A10** 各补 tests/ 下最小 pytest 回归(monkeypatch/subprocess 断言: --help 不获锁不实跑 / import 不截断 log / _init 异常锁清理 / os.write OSError fd 清理 / flag 透传), 纳入批次门禁, 而非仅一次手工冒烟。
- 每批次跑相关 gate + 裸 GBK(重定向)终端 `--dry-run` 冒烟。**所有修复 golden 安全**, 不触发付费 LLM/嵌入/golden 重生。

## 7. 残余风险 (评审汇总, 8 项)
1. ✅ **入口⑤ 03 已坐实**(TAX03 EXIT=0 / 墙钟 3552s≈59min / 双 dta+双 parquet+互验 md 全刷新 10:xx / 0 ERROR / 无残留进程锁)。**暴露运营项: tax 03 近 1 小时(budget 1.0B 双引擎+双 6.5GB dta), 生产 T=18 更长, 长跑须前台/nohup 或分步 --no-emit-dta, 勿依赖会话级后台。**
2. **非原子 ~6.8GB dta 写盘的崩溃安全缺口**: 长跑 03 被 kill 中途留半写 dta 供 Stata 误读(本次⑤当场演示, 与 2026-07-07 branchw 688MB 半成品同构); A5/A9 只修锁与 fd, 单实例锁自愈只清锁不清残 dta。**处理**: 长跑 03 前台/nohup + 完成后校验 dta 完整性 + 明确"中断=产物不可信须重跑"纪律; 中长期 03 dta 写盘走 temp+原子 rename(**触数据层、golden 不安全 → DEFERRED 但须明列**)。
3. **跨管线并发未完全封死**: listed×tax、company×主管道(尽力而为跨锁守卫不能消除"company 先读→主启动"时序窗口)。
4. **--skip-unchanged 开启时 cross_media 陈旧路径真实存在**(F7, 默认关+前缀守卫, 与 I-1 同盲区)。
5. **OFFLINE 下 66/70 两张稳健性表无产出**, 复现需在线付费 LLM(II-1)。
6. **A6 golden 安全前提**依赖 committed registry 锚在 HASHSEED=0 下生成(已由本轮 sha=4f580e3f 匹配坐实; 若锚曾在非零 seed 下生成, 强制 HASHSEED=0 反可能翻红 gate)。
7. **BLAS 线程=1 仅靠 shell 约定**(F12/B6), 生产 golden 重生须遵 golden-regen SOP + M0 审批门; setdefault BLAS=1 有性能代价不宜盲加。
8. **生产 T=18 vs 本 T=2 试跑非同量级**: tax 03(双 6.8GB dta + 千万行加权引擎)/boilerplate 等墙钟与内存放大, 长跑须前台/nohup 或分步(--no-emit-dta), 勿依赖会话级后台(本次⑤首跑中断即此教训)。

## 8. 评审记录
- **对抗验证**: 16 个 A/B 问题各 1 独立 agent(high effort)读源码核实真实性/行号/判定/golden 安全 → 14 项确认保留, A8→C、B5→C、F7→B、A6→B、A1/A2/A5 降级。
- **三轮独立评审**(xhigh, 均 okToShip=false 后修订): 轮1 完整性/遗漏(假阴/假阳排查干净)、轮2 技术正确性(揪出 §5 执行顺序 P1 错误)、轮3 可执行性/风险(揪出 5/5 悬空 + 半写 dta 崩溃安全 + pytest gate)。
- **首席综合**: ship-after-revisions, 无 P0 代码级阻断; 本最终版已逐条吸收 3 处 P1(§0 5/5坐实 / findings 可回溯 / §5 顺序修正) + 全部 P2/NIT。
