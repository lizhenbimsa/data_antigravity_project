# 八入口顺序真跑第四轮审计 — 审计与整改执行计划 (2026-07-16 · R1 修订版, 评审记录见 §8)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 日期 2026-07-16 · 环境 OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP=1 / PYTHONIOENCODING=utf-8) · 解释器 F:\Anaconda3\python.exe (conda base 3.13.9) · cwd=news_process\ (⑦⑧=各自子目录) · 每入口 cap=10800s (本轮用户指令 3h) · 有效运行窗 00:36:08–01:42:52 (总 67 分钟)。
>
> 本轮 = 07-15 第三轮 (`EIGHT_ENTRYPOINT_SEQUENTIAL_THIRDRUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-15.md`, 下称「上轮计划」) 之后, 跨 7 提交 (26e1b609..b95a9535: 3786ced5 批次A stata_export 收口 + 399fa901 计划入库 + 8ea92a75 侧线 P4 收口/15 dta notes 注入 + 4f4f6060 终局收口 + 6b24aba6 LB017 整改 + f053a72c constants + b95a9535 会话遗留 2 件) 的第四次全谱复跑。运行时代码增量收敛度极高: 仅 `pipeline/panel/stata_export.py` (3786ced5, 已过上轮五步 gate) + `tests/test_stata_notes_do.py`; 其余全为侧线 codebook 内容/审计文档/constants 时间戳。基线 = 起跑前一刻复核 HEAD=b95a9535、工作树 clean 0 脏项 (吸收上轮「gitStatus 快照会说谎」教训)。
>
> 审计方法 = 静态预审 (7 提交增量影响矩阵 + 跑前物理态快照 246 行 + notes .do 11 件 SHA256 + 三库 logs 备份) + 8 入口顺序真跑 (驱动 v2, 逐入口 sentinel/console/心跳/死亡告警) + 跑后逐入口锚对账 (主笔亲核) + 3 路只读深审代理 (A 主/验证日志 41 文件 · B 双 company 日志跨轮 diff · C 产物态 246 行逐行差分) + fast sweep A 基线 + R1 三路计划评审 (完整性/技术·证据回落/可执行性, 见 §8)。证据归档: 会话 scratchpad `audit_2026-07-16\` (console/sentinels/misfire_v1/pre_logs/snapshots + LEDGER.md + driver2_transcript)。
>
> **编号约定 (R1 修订; RR4-A 勘误扩号)**: 本轮新问题一律用 **K 系 (K1–K7; K7 为批次 A 实施期新增)** + DRV-1 + N7-R2 命名, 与历史轮次 F 系 (07-10) / G·H 系 (07-14) / N 系 (07-15) 严格不冲突; 正文引用历史编号时一律带「(07-10 轮)」等限定词。D 系销案为本轮局部编号 (与上轮 D 系同名异指, 引用上轮时写「上轮 D2」)。
>
> ⚠ 本计划所引日志行号 = 2026-07-16 运行快照, 后续重跑行号漂移勿以行号立案。

## 0. 结论速览

- **8/8 成功 EXIT=0 · 0 真 ERROR · 0 Traceback · $0** (stage21 离线 13,896/13,896 全命中 misses=0 writes=0; BERT 推理缓存 9,045/9,045; 全仓无任何在线调用痕迹 — A 路正则全扫 0 命中)。
- **golden 全谱零漂移 (连续第二轮 0 字节级漂移)**: 面板 220×3442 / 文章 1005×1305 / 51: 220×3453 逐项同上轮; 主线三 dta 干净态字节逐位=上轮锚 (8,191,835/8,254,163/8,218,235); notes .do 11/11 与跑前 SHA256 全等; listed 10 dta 字节锚 10/10 逐位 (主 1,610,634,683 / 7 权 1,603,484,161 / frozenw 1,606,426,983 / mainbankw 1,617,142,173); tax 5 dta 字节逐一逐位 (6,845,811,481 / 6,847,602,963 / 6,876,264,107 / 6,858,349,287 / 6,898,645,113); 双 registry 锚 023cdc9158ec52ba…d082dd30 / 4f580e3f…b6e4c034 各恰 8 处全链复现; pair 指纹 a50a9cc2e990a0cd 同代; 两库 parquet 族 0 字节漂移; Spearman 全套逐字 (含 city×county +0.9009 n=903,506); 81 审计 158 项 0 FAIL / 20 WARN; 82 漏斗 9,490→5,031→1,650→1,005; κ 哨兵 0.7794/0.8149/0.8525/0.8663 逐位; config registry yaml ×2 字节级全等重生 (git diff 空)。
- **WARNING 全谱白名单**: ① 34 条 / ② 28 条 / ⑦ 10 条 / ⑧ 11 条, 三路代理独立复核白名单外实质新增 = 0。fast sweep 恰 3 残红 (benefit cohort ×2 + jieba isolation ×1) 逐条同上轮基线, 0 新增 (存档口径 = 本会话实跑 + LEDGER 记录; 无原始输出落件, 复核可重跑 `pytest -m fast` 证伪)。
- **本轮最大发现 ×2 (均非管道缺陷)**: ① DRV-1 = 审计驱动层 GBK 编码陷阱误杀事故 (v1 首启 8 入口全灭, 数据产物零损伤, 当轮已修并复跑成功 — H4 家族第 7 例, 见 §3); ② N7-R2 = 上轮「全链 ~3× 慢化」已**自发消退** (全谱 3.0–3.7× 提速, powercfg 未变+无重启), 上轮 N7 归因修正 + 新常态预算作废 (见 §3)。
- **本轮定级: P0=0 · P1=3 (DRV-1 驱动层·当轮已修 / N7-R2 环境修正案·文档面 / K7 apply_stata_notes.ps1 假阴性护栏·批次 A 实施期发现并已修) · P2=1 (K2 侧线 codebook md 携带·呈报) · 记录=1 (K1 notes 双重放义务·本轮执行) · NIT=3 (K3 白名单收编 [含 2 子项] / K4 run_paper.log 追加模式 / K5 孤儿 dta) · 观察=1 (K6) · 销案=3 (D1–D3)**。标尺沿用四级 [P0/P1/P2/NIT] + 记录/观察辅助类 (上轮先例)。全部非阻断; **管道 (16+16 阶段) 代码零缺陷; 唯一代码修 = K7 编排脚本等待语义 (批次 A 实施期实弹发现, 非管道数据路径, golden 零风险)**。
- 上轮跨轮义务对账: N2 (上轮编号) 重放义务 → 本轮重跑再抹、再挂 (§4 批次 A 本轮执行, 扩为主线+侧线双重放); N1-gate③ 条件式尾巴 → `grep -cF '${' variable_codebook.json` = 0 自动满足, 打勾; N7(b) 新常态预算 → 被 N7-R2 作废; G9 口径 → 75 陈旧 stale-skip loud-warn 00:51:21 准时, 面板守 3442 (预登记兑现); H2 46 号三锚/镜像 → live; H3 文案 → live 且与旗标 WARNING ×2 成对; N5/N6 (上轮编号) 残留 → 会话锁已随 b95a9535 用户裁定入库 (该半边销案), `scratch_seg.txt` 仍在 repo 根、07-12 idle 进程现存性本轮未复核 → 并入清理批呈报 (§4)。
- 静态预审吸收声明: 跑前预测 (LEDGER P-①..P-⑧/P-G2a/P-46/P-fast) **除耗时字段外**全部兑现 (耗时预测按上轮新常态口径 ~2780/~7300s, 落空 3 倍 — 该落空本身即本轮最大发现 N7-R2, R2-A4 勘误), 含「⑦⑧ 跑前 notes 态字节与锚不等属预期」与「主线 3 dta 跑前 = notes 态 66,450,164/66,505,604/66,617,018 B 与 07-15 晚重放锚逐位相等」两条预登记 (后者 = 上轮 N2 重放成果跨轮存活的确认)。

## 1. 运行结果总览

| # | 入口 | 结果 | 墙钟 | 上轮 (07-15) | 提速 | 关键证据 |
|---|------|------|------|------|------|---------|
| ① | run_pipeline_function | ✅ 0 | 933s | 2775.8s | 2.98× | 16/16; 13,896 全命中; 220×3442 / 1005×1305 / 220×3453; 34 WARN 白名单; 75 stale-skip 00:51:21 准时; 三 dta 干净态字节逐位 |
| ② | run_pipeline_validation | ✅ 0 | 194s | 722.6s | 3.73× | 16/16; κ 四哨兵逐位; 66/70 离线跳过; 72 号 135.9s (上轮 ~9min, 上轮 N9 观察随频率恢复回落) |
| ③ | run_paper (裸跑) | ✅ 0 | 1s | 1.2s | – | 11/11 篇 0 render 失败; 今日段 0 ERROR (log 追加模式含 07-06 陈旧 ERROR ×3, 销案 D1) |
| ④ | 80_placebo_and_alt_anchor | ✅ 0 | 2s | 2.0s | – | 143×29; embedding_dim=4096 |
| ⑤ | 81_stata_data_audit | ✅ 0 | 3s | 2.9s | – | 158 项 0 FAIL / 20 WARN; 40=3442 / 51=3453; 恒等式族全绿 |
| ⑥ | 82_export_stats_excel | ✅ 0 | 1s | 1.4s | – | 漏斗 9,490→5,031→1,650→1,005 |
| ⑦ | company_listed_bank | ✅ 0 | 771s | 2877.2s | 3.73× | 锚 023cdc9158ec52ba ×8; 10/10 dta 字节锚; G2a ×1 真哨兵; F11 (07-10 轮) 锁成对; 分段 01/02/03/04 = 1.45×/3.10×/3.78×/4.01× (01 仅 3.8s 常数开销主导, 1.45× 非异常) |
| ⑧ | company_tax_bank | ✅ 0 | 2099s | 7316.1s | 3.49× | 锚 4f580e3fc458be0c ×8; 5 dta 字节逐位; 主面板 447,710×1,914 (20 固定列含 usci + 加权列; 上两轮「×21」速记无日志落点, 自本轮弃用); 建碁 668=67.9% 同形; 分段 01/02/03/04 = 3.67×/3.82×/3.30×/3.83× (03 偏低系 13.4GB dta 写盘占比高, 盘速不随睿频放大 — 均匀性成立) |

驱动层注: v1 首启事故见 §3 DRV-1 (8 入口全灭 → 全 ASCII v2 重启 → 8/8 全程可信; misfire 现场归档 misfire_v1\)。⑧ 2099s 在 2h cap 内 — 上轮 N8「cap 必然违约」随 N7-R2 一并失效。

## 2. 白名单对账 (上轮已裁定项, 本轮全谱同形复现, 不再立案)

- ①: 34 条全命中 (Bartik 弱 IV 族 / share one-hot 退化族 / 前视掩码 ×2 / 零方差常量 ×2 [brokerage_fire_sale, depins_post] / stage13 掉 9 家 151→142 / 变量名 33 字符 ×3 / 跨目录同名副本 ×1 / csdid never-treated / DiD HQ-based + sandbox_post·dcep_post 全 0 / 负极句 #3 投影 0.1416 / 词典披露 6-1506 / 小样本 T=2 ×2 / 75 陈旧跳过 [G9 预登记])。
- ②: 28 条全命中 (旧版工作台 ×4 / 旗标 ×2 / 62 输入 10,076 / 63 demo_mode / 66·70 离线跳过 / Δα 三值 -0.3184/-0.1523/-0.1250 逐位 / 媒体单类 100% / 时间稳定性 2 年 / κ range ×4)。
- ⑦⑧: 豁免基名 ×4 双库 / G8 (07-14 轮) 三基名缺源列 (DEFERRED 维持) / G2a 哨兵各恰 1 (指纹 d66f929b36eae28a 同上轮 = 27 号本轮确未重生, 真哨兵; 生产前仍须按既有 §7-G2 三参数重生) / 40 加权列全 NaN (F3, 07-10 轮编号) / 建碁 67.9% / mainbankw tie 28.47%·51.11% (INFO) / 磨损左截断披露 (INFO) / tax 03 反向证据三件套对称 (branch_county 0.3688× n=456 点名, INFO)。
- **白名单收编 ×2 (K3, 本计划即为收编落点)**: (a) ① 的 share one-hot 退化 WARNING 实测 10 处 ([type]×4 + [scale]/[fintech_lf]/[fintech_lc]/[media]/[mauth]/[geoprox] 各 1), 上轮白名单「×2」系口径压缩 — 自此按「one-hot 退化族 ×10 (Bartik IV 构造块, T=2 确定性退化)」收编; (b) ⑤ 81 号 20 项 WARN 十族 (高缺失 609 变量 [tone_std 族零新闻行天然 NaN] / llm_vote_tone_ctx·ss 缺失 10.49%·7.69% / dict_avg 5σ ×1 / LOO-IV r=0.030 / DiD 不可识别 ×2 / Stata 列名 116 + Nullable dtype 3330·3341 / 零新闻占比 35%) = 体检报告 stage 的设计产物, 收编白名单⑤, 判据锚 = 「158 项 0 FAIL」行。
- 预登记复核 (防误立案, 全部兑现): 46 号输入 df_exploded 1,005×1,356 = 1305+51 临时列 (中间态非漂移) / dedup_sensitivity_summary.json 980→1,798 B = 上轮 D2 同款良性恢复 (销案 D2, **现态注**: 01:50 审计窗后又被并发会话覆写回 980 B — 两版均含 4 格点顶层键, 差异在每格字段丰度; 980↔1,798 振荡进行中, 属跨会话 run-artifact 抖动, 批次 A 执行时再遇勿立案) / 65_radius_sensitivity.json ±1 B = meta 墙钟字段位数漂移 (run-dependent, 销案 D3) / 上游 4 parquet sha 跨轮变化但字节**数**不变 (run-dependent 预登记; R2-A4 字面勘误 — 同字节必同 sha, 实义为尺寸不变) / 5 个 07-07 孤儿 dta mtime 未动 (K5 维持现状) / 主线 3 dta 跑前 notes 态字节与 07-15 晚重放锚逐位相等 (上轮 N2 成果存活确认)。
- **上轮 N5/N6 残留后续 (R1 补录)**: `.session_lock` 已由 b95a9535 用户裁定入库 → 该半边销案; `news_process/scratch_seg.txt` 仍在 (07-15 11:19); 07-12 idle 进程 (3 python + 3 powershell) 现存性本轮未复核 (本轮 K6 只覆盖 00:28 启动的 3 个 mcp-stata 服务进程) → 与 K5 一并挂清理批呈报, 不单方面动。

## 3. 新问题台账 (本轮 K 系 + DRV-1 + N7-R2; 每条已主笔亲核或双源坐实)

### DRV-1 · [P1 · 审计驱动层 · 当轮已修 · H4 家族第 7 例] driver.ps1 无 BOM UTF-8 + 中文注释 → GBK 解码吞换行 → 8 入口全灭误杀
- **事故**: v1 驱动 (00:25:59 启动) 8 个入口全部 ~1s 即被 taskkill, .done 全谱 EXIT=CAPKILL_10800s、WALL=6s (窗 00:25:59–00:26:46)。
- **根因 (实证定谳)**: driver.ps1 由 Write 工具以无 BOM UTF-8 (LF 行尾) 落盘; `powershell.exe -File` 对无 BOM 文件按 ANSI/GBK 解码; 行内中文注释「…可能取不到」尾字「到」(E5 88 B0) 的尾字节 B0 被 GBK 当作双字节首字节吞并后续 LF → **下一行 `$deadline = $t0.AddSeconds(10800)` 整行并入注释** (66 行文件 GBK 实读只剩 65 行) → `$deadline=$null` → `(Get-Date) -lt $null` 恒 False → while 等待循环 0 次进入 → 误入 CAPKILL 分支 taskkill。证据: `Get-Content -Encoding Default` 实读第 41 行 = 注释与赋值同行 (归档 misfire_v1\; R1 技术路以字节级 `e5 88 b0 0a` 复核); 纯 ASCII minidriver 同构通过 → 隔离变量=中文注释编码; v1 期间 HEARTBEAT.txt 从未出现 = 循环体 0 次执行旁证 (misfire_v1 内现存 HEARTBEAT 为事后 00:30:46 minidriver 诊断产物, 已核不混淆)。⚠ 复现方法注记: iconv 不能复现换行吞并 (只弃无效字节保留 LF), 定谳必须用 Windows 原生解码器 (`Get-Content -Encoding Default` 行数对账 66→65)。
- **副作用评估 (全部无损)**: 8 python 均死于任何 parquet/dta/xlsx 写入前 → 数据产物零损伤 (C 路 246 行差分独立复证); 覆写 9 个 log (跑前已备份 pre_logs\); 残留 3 锁文件 = OS 级 msvcrt 字节锁, 进程死亡即自动释放, 惰性无害 (core/locking.py 语义实读), 未清理、由 v2 重跑正常 open('w') 重加锁覆盖。
- **修复 (当轮已落)**: driver2.ps1 全 ASCII + Start-Transcript + `$deadline` 非空断言; v2 全程 8/8 EXIT=0, transcript 逐入口 clean, deadline=t0+3h 计算正确。
- **SOP 教训 (H4 扩编第 7 例, 入 memory)**: 凡经 `powershell.exe -File` 执行的 .ps1 — 要么全 ASCII, 要么带 BOM (UTF-8-BOM/UTF-16); 无 BOM UTF-8 + CJK 注释 = 换行可被 GBK 双字节吞并, **下一行代码静默并入注释** (比 mojibake 更险: 语法不报错、逻辑静默改变)。核验口径 = `Get-Content -Encoding Default` 行数与源行数相等 (对全 ASCII 恒真, 对含 CJK 文件才有判别力)。等待循环类驱动必须带「条件恒假防御」(哨兵变量非空断言 + Transcript)。
- 零 repo 代码 (驱动在 scratchpad, 不入库)。

### N7-R2 · [P1 · 运行环境 · 修正上轮 N7 · 零代码] 上轮「全链 ~3× 慢化」已自发消退 — 95% 限频设置非充分根因, 新常态预算作废
- **证据链 (四点, 均本轮实测, R1 技术路逐点复核)**: ① 全链 3.0–3.7× 提速 (①933s=2.98× / ②194s=3.73× / ⑦771s=3.73× / ⑧2099s=3.49×), 且 ① 内部逐阶段**带内一致**提速 (22: 3.827× / 40: 4.586×; 例外两端 = 00 号 1.928× [IO 重段, 盘速不随睿频放大] 与 26 号 6.03× [超出纯频率解释, 机制未取证, 不影响主判定] — R1 亲算)、⑧ 分段 3.30–3.83× 带内一致 — 频率状态恢复特征, 非缓存/结构性 (词典 22 号纯 CPU 无缓存亦 3.8×; driver2 env 与上轮等价、BLAS 全钉 1 — R2 核, 排除「多核加速误读」替代解释); ② `powercfg /query` 起跑前复核 AC=**0x5f (95%) 未变**; ③ **无重启** (LastBoot=2026-07-07 13:20:04, uptime 8.5 天覆盖慢化全窗口); ④ 睿频实测在场: `% Processor Performance` 两窗采样 = ① 完成后轻载 97.8–106.4% / ⑦ 运行中 109–115.6% (上轮满载钉死 69-70%)。**跨轮链 (R2-A3 补)**: 「本轮 933s 快于 07-10 的 2313.7s」不构成矛盾 — 07-10 计划当轮已判其 ① 2313.7s 为「争用窗慢化」(其更早健康锚 ≈1133s), 本轮 933s 与健康锚同量级且在睿频 >100% 下自洽。
- **判定**: 上轮 N7「AC 95% → 睿频被阻断」的机制解释**不完备** (其 R1 保留意见「95% 算术不能直接推出 69-70%, 可能叠加功耗墙/EPP/P·E 核混合」兑现): 95% 设置在场时睿频照常 >100%。07-14/07-15 两轮的慢化 = **瞬态退化** (功耗墙/EPP/电源驱动态/热管理栈某处滞留, 精确机制无法事后取证 — 现场已消失), 与 95% 设置最多相关、非充分因果。上轮 N7(b) 用户裁定「维持 95% 现状」本身零成本、无需翻案; 但随裁定生效的**新常态预算表 (①2780/⑦2880/⑧7300s) 作废**, 本轮实测为新参照 (①933/②194/⑦771/⑧2099s); ⑧ 2h cap 自然满足, 上轮 N8「cap 必然违约」失效。
- **动作 (零代码, 文档面)**: 本计划为上轮 N7/N8 的修正案挂链 (镜像上轮对 07-14 H1/D3 的处理 — 不改写上轮正文, §4 批次 B 在上轮计划 §7 N7 行后插一行修正案引用); memory 同步 (本轮 topic 文件 + 上轮 topic 文件加更正注)。
- **SOP (入 §7)**: 每轮起跑前采 5s `Get-Counter '\Processor Information(_Total)\% Processor Performance'` 样本留痕; 慢化再现时先做两个 5 分钟实测 (满载计数器 + 盘顺序写) 再谈预算/争用; 任何一轮的耗时基线都不可外推为常态 — 预算表按「最近一轮同状态实测 + 计数器佐证」滚动维护。

### K1 · [记录 · 义务 · 本轮执行] ①⑦⑧ 重跑按预期抹除 18 份 dta 的 notes — 主线+侧线双重放
- ① 抹主线 3 dta (40/46/51; 46 号日志 :66/:69 明示重放入口 `scripts/apply_stata_notes.ps1`); ⑦⑧ 抹侧线 15 dta (8ea92a75 于 07-15 22:49 注入, 预登记「重跑 02/03/04 即抹」兑现)。
- **两类 notes 载体不同 (承重, R1 可执行性路定谳)**: 主线 = **变量级** `notes {short}:` (stata_export.py `_render_notes_block`) — pyreadstat `meta.notes` **不可见** (只暴露 `_dta` 数据集级), 对账只能走 log/console/sidecar 层; 侧线 = **数据集级** `notes _dta:` — pyreadstat 可读, 条数 = 期望+1 (note0 计数标记为 dta 格式固有)。
- **期望锚 SSOT**: 三份 `_notes_applied_fingerprint.json` — 主线一份 (news_process/data/processed/, `n_notes_applied` 三键 = 3442/3442/3453); 侧线两份 (company_listed_bank/data/ 与 company_tax_bank/data/, 逐 dta `expected_notes`: LB 10 份各 24; TB cityw/countyw 各 32、cooc 30、frozenw/mainbankw 各 23; `notes_count` 恒 = expected+1)。⚠ sidecar「陈旧」仅指其 `sha256`/`value_hash` 快照 (dta 已被本轮重生), `expected_notes`/`families` 字段仍为重放期望 SSOT, 有效。⚠ P4 记录的「合计 244 条」与逐 dta 求和 (240+140=380) 不符 — 「跨家族去重切段口径」系本计划推断 (P4 记录无明文出处, R2-A4 标注), 唯一确定的是两数非同一口径; 对账一律用逐 dta `expected_notes`, 勿用 244。
- **本轮动作 (批次 A)**: 主线重放 = apply_stata_notes.ps1 零参后台分离 (命令形态与判据见 §5-1; 上轮教训: 前台 10min 超时会杀掉收尾快照步; 脚本内置逐 dta 1800s Wait-Process 护栏); 侧线重放 = 15 个 `_notes_inject_*.do` 串行 `/b` 批处理 (参数与判据见 §5-2; 吸收 07-15 执行插曲教训: 起进程→轮询 log DONE 标记→兜底击杀, 防 Stata 僵尸挂 -Wait)。
- **对账铁律 (侧线收口会话 07-15 存档, 本轮沿用)**: (a) notes 在场性判定用条数/哈希, **不得以尺寸单锚** (46 号带 notes 也可 8.2MB 的先例); (b) 多重集比对非顺序拼接; (c) r(###) 扫描一律 `(^|[^A-Za-z])r\([0-9]+\)` 非字母边界 (上轮 N3 口径, 引文年份免疫)。

### K2 · [P2 · 侧线携带 · 呈报] 两侧线 codebook md 的 07-15 会话版被 canonical 重生部分覆盖
- 现象: `company_bank_cooc_panel_codebook.md` 跑前 (07-15 21:32 会话版) 21,479 B → 重生 20,568 B (**净减 911 B** = 被覆盖丢失的净量); tax 同款净减 195 B (25,967→25,772)。携带证据 = 02 生成段 216→226 行 (+10 行跨轮进入 canonical 输出, 两轮 02 log :182 逐字对照) — 即 preserve-chapter 机制**携带了部分章节**, 其余会话期盘上修订被 canonical 重生覆盖。侧线收口会话已预登记该风险 (「P3 修订只在盘上, data/** 忽略不入库」— memory 07-15 §遗留)。面板/dta/指纹/registry 锚零受影响 (B 路复核)。
- 处置: 本会话无该修订源内容、不可代为恢复; **呈报用户/侧线会话** 三选一 — (a) 接受 canonical 态; (b) 侧线会话按其记录重放修订; (c) 根治 = 修订固化进 02 生成器 preserve-chapter 白名单 (侧线 P4 级建议既载)。本计划仅记录, 不动侧线资产。

### K3 · [NIT · 白名单收编 · 本计划即落点] one-hot ×10 口径 + 81 号 20 WARN 十族 → 已收编 §2, 第五轮起按新口径对账。
### K4 · [NIT · 观察] run_paper.log 为追加模式 (含 07-06 陈旧 ERROR ×3), 与「每跑覆盖」惯例不同
- 属 user-CLI 调度器多会话审计需求的合理形态 (每次调度一段, 保留历史)。不改代码; 审计 SOP = run_paper.log 一律按 `^YYYY-MM-DD` 窗口过滤 (§7 载入)。
### K5 · [NIT · 维持 DEFER] `news_process/data/processed/company_bank_*w_panel.dta` ×5 孤儿 (~8GB, 07-07 dir-move 前残留, 字节 1,602,853,327 ≠ 子库现锚 1,603,484,161)
- 本轮验证 mtime 未被触碰 (确非活跃产物)。清理不可逆 → 维持挂清理批/用户, 与既有 t2v 孤儿、弃用工作台 ×4、scratch_seg.txt、07-12 idle 进程复核 (上轮 N5/N6 残余半边) 同批呈报。
### K6 · [观察] 运行窗后 data/processed 目录 mtime 仍推进 (瞬态条目, find -newermt 无存活文件命中) — 并发进程 (含 3 个 mcp-stata 服务 00:28 启动) 痕迹, 存活产物零影响, 仅记录。

### K7 · [P1 · repo 脚本缺陷 · 批次 A 实施期发现并已修] apply_stata_notes.ps1 假阴性护栏 — 等进程退出而非等 DONE 标记, 僵尸态下把成功注入误判为失败并删 sidecar 键
- **实弹 (批次 A 主线重放首跑)**: 三 master 注入本体全部成功 (log 各含 `NOTES_MASTER_DONE=` + r(###) 边界扫描=0; 三 dta **字节数**与 07-15 注入态锚相等 66,450,164/66,505,604/66,617,018 — dta 118 头部含 save 时戳, 跨 run 逐位相等物理不可能 [07-10 先例], RR2-NIT-2 措辞口径; 注入实际耗时 ~19s/份), 但 Stata 进程在 `exit, clear` 后**全谱僵尸滞留** (3/3, 各挂满 1800s) → 旧 `Invoke-StataBatch` 的 `Wait-Process -Timeout` 护栏逐一误判 TIMEOUT 失败 → 连坐 `sidecar-remove` 删掉 40/46/51 三键 → 脚本 exit 1。**假阴性设计缺陷**: 完成信号 (log DONE 标记) 与等待对象 (进程退出) 错位; 07-15 P4 会话已实弹过同款僵尸 (shareholderw) 并给出「轮询 DONE→兜底击杀」正确策略, 但该策略未回流到本脚本。
- **僵尸系统性注记**: 07-15 仅偶发 1 例; 本日 3/3 主线 + 15/15 侧线 + R2 probe 全部滞留 — 环境因素疑与 00:28 起常驻的 mcp-stata 服务相关 (相关非因果, 未取证; 不动他会话进程)。修复不依赖根因: 无论僵尸与否, DONE 标记轮询语义都正确。
- **修复 (已落, 恰 1 文件 `scripts/apply_stata_notes.ps1`)**: `Invoke-StataBatch` 等待段改为 — 轮询 log 行首 `NOTES_MASTER_DONE=` (10s 间隔) → 见 DONE 且进程滞留: 60s 干净退出宽限后按僵尸击杀、**判成功**; 无 DONE 且超时: 击杀判失败 (护栏保留); 进程自然退出: 走原 log/r(###)/对账判定。+ 先取 `$p.Handle` (07-14 教训)。golden 零风险 (纯编排层, 不触任何数据代码路径)。
- **失败态修复 (已执行)**: 首跑被误删的 sidecar 三键按 helper 同口径手动补齐 — applied 从三 master log 的 `NOTES_APPLIED_PART*` 求和 = 3442/3442/3453, 与 helper `expected` 逐一相等后 `sidecar-update` 回写 (n_notes_applied + 注入态 sha256)。
- **gate**: 修复版脚本幂等重放一遍端到端 — 预期 exit 0 + stdout 三行对账 (`applied=3442`×2/`applied=3453`×1, master_done=True) + 收尾行 + sidecar 三键自动刷新 (见 §7-bis 回填)。

### 销案 (D 系, 本轮编号, 查过非缺陷)
- **D1 · ③ run_paper.log 3 条 ERROR**: 全为 2026-07-06 陈旧行 (负例测试 ×2 + 历史异常 ×1; 07-06 当日 logs 已经该轮全量取证审计裁定全绿, 见 memory log-audit-and-a1-ece-fix-2026-07-06), 今日段 0 ERROR、退出码 0。追加模式产物, 收 K4。
- **D2 · dedup_sensitivity_summary.json 980→1,798 B**: 上轮 D2 同款 — 会话局部产物被 ① 恢复为 4 格点全量规范态 (j70w5/j75w5/j80w10/j70w10 实读), 良性; 现态与振荡预登记见 §2。
- **D3 · 65_radius_sensitivity.json −1 B**: meta `processing_time_seconds` 位数漂移, run-dependent 良性。

## 4. 修复批次 (先过 gate 再 commit; by-name stage, 排除并发产物与孤儿)

- **批次 A (物理态收口, 零 commit)**: K1 双重放 — (i) 主线 apply_stata_notes.ps1 后台分离; (ii) 侧线 15 .do 串行 `/b`。gate 见 §5-1/2/3。**顺序依赖**: 批次 A 全 gate 过并将执行结果回填本计划 §7-bis 后, 才跑批次 B; 侧线任一 .do 失败按 §5-2 安全分支处置, 失败未决时批次 B 照常但 §7-bis 如实记 FAIL。
- **批次 B (repo 文档 + constants + K7 修复, by-name 3 commit)**:
  - (0) **K7 修复 commit (实施期新增)**: 恰 1 文件 `scripts/apply_stata_notes.ps1` (`Invoke-StataBatch` DONE 标记轮询 + 僵尸兜底 + Handle 先取); subject 参考 `fix(scripts): apply_stata_notes 假阴性护栏 — 等进程退出改为等 NOTES_MASTER_DONE 标记 (K7, 僵尸滞留 3/3 实弹)`; gate = 修复版幂等重放端到端全绿 (§7-bis)。
  - (i) 本计划 md 终稿 (§7-bis/§8 回填) + 上轮计划 §7 修正案挂链一行。插入点 = 上轮计划 §7 内 `**N7 (已决, 2026-07-15)**` 行 (当前 :141, 全 §7 唯一) 之后、N2 行 (:142) 之前; 文本: 「- [x→修正案] **N7/N8 (2026-07-16 第四轮定谳)**: 慢化已自发消退 (powercfg 未变+无重启, 睿频实测 >100%), 95% 设置非充分根因, 新常态预算作废; 第四轮实测 ①933/②194/⑦771/⑧2099s 为新参照, ⑧ 2h cap 自然满足; 见 EIGHT_ENTRYPOINT_SEQUENTIAL_FOURTHRUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-16.md §3-N7-R2。」。commit subject 参考: `docs(audit): 八入口第四轮全谱零漂移收口 — DRV-1 GBK 定谳 + N7-R2 修正案挂链 + notes 双重放`; HEREDOC + `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer (CLAUDE.md 协议)。
  - (ii) `news_process/data/processed/v3_5_1_constants.json` stage21 时间戳收口同步, 单独 chore commit (镜像 f053a72c 措辞, 日期改 2026-07-16)。
- **commit 外动作 (memory 在 repo 外)**: 本轮 topic 文件 (DRV-1 GBK 教训 + N7-R2 + 全谱零漂移 + 重放执行记录) + MEMORY.md 索引行 + 上轮 topic 文件 N7 段加更正注。
- **呈报用户 (零代码, 不随批次)**: K2 侧线 codebook md 三选一 · K5 清理批授权 (含孤儿 5 dta + scratch_seg.txt + 07-12 进程复核, 维持 DEFER)。
- **DEFERRED (维持, 逐项点名防断链)**: G2(b) 硬锁层 (M0) · 27 号旧代三参数重生 (生产前) · G6(b)/G10 (07-14 轮) · 清理批 (t2v 孤儿 + 弃用工作台 ×4 + 本轮 K5 并入) · F1(a) 税调匹配层 (07-10 轮) · R2 根治族 (codebook json 原子写族) · boilerplate tier2 · G9 振荡根治 · 侧线 tier_by_col↔02 互锁闸 (侧线 P4 级)。
- **刻意不做**: K2 代为恢复 (无源内容) · K4 改代码 (合理形态) · K5 单方面清理 (不可逆) · N7 机制深查 (现场已消失, 不可事后取证) · 重跑 fast sweep B 侧 (零代码改动, A 基线即终态) · 侧线 15 dta 值哈希全量复核 (**指 pandas 全解析值哈希** 15 份 ≈50GB 解析读, 以抽验 2 份替代, §5-2(e); ⚠ 与之区分: fingerprint `sha256` 字段刷新的顺序字节读 15 份**仍做**, §5-2 尾条 — 两者勿混淆连带跳过, R2-A4 消歧)。

## 5. 验证 gate (批次 A; 解释器 F:\Anaconda3\python.exe; cwd=news_process\)

1. **主线重放 (机械化命令形态)**:
   - 启动: `$p = Start-Process powershell -ArgumentList '-NoProfile','-ExecutionPolicy','Bypass','-File','F:\WiseSearch\data_antigravity_project\news_process\scripts\apply_stata_notes.ps1' -RedirectStandardOutput <scratchpad>\apply_notes_stdout.log -RedirectStandardError <scratchpad>\apply_notes_stderr.log -PassThru; $null=$p.Handle` (⚠ 必须重定向 stdout — 脚本的 applied/expected 对账与 [OK]/[FAIL] 走 Write-Host console, 不落 Stata log); 轮询 `HasExited`; 总预算 3×1800s + 300s 收尾余量, 超预算才考虑击杀。
   - 判据: (a) `$p.ExitCode` = 0; (b) stdout.log 含三行对账且 ASCII 子串 `applied=3442` ×2 + `applied=3453` ×1 + `master_done=True` ×3 + 收尾行 (ASCII 片段 `===` 与 `sidecar` 同行) — **⚠ stdout.log 落盘编码为 CP936/GBK (R2 实测), 中文字面须以 `Get-Content -Encoding Default` 读, UTF-8 工具搜「对账」恒 0 命中, 判据以 ASCII 子串为准**; (c) 3 个 `NN_apply_notes_master.log` 各含行首 `NOTES_MASTER_DONE=`; (d) `grep -E "(^|[^A-Za-z])r\([0-9]+\)"` 三 master log = 0 命中; (e) 持久化复核: 主线 `_notes_applied_fingerprint.json` 三键 `n_notes_applied` == 3442/3442/3453 (helper sidecar-update 自动刷新, 读回即验)。**⚠ 禁用 pyreadstat 复读主线 notes 条数** — 主线为变量级 notes, `meta.notes` 不可见 (K1 承重, R2 probe dta 实证)。**失败分支 (R3-NIT-2)**: 判据 (a)–(e) 任一不满足 → 幂等重放一次 (46 log :66 幂等声明); 再败 → §7-bis 如实记 FAIL, 批次 B 照常。
2. **侧线重放 (机械化参数)**: 串行逐 .do; `Start-Process 'C:\Program Files\StataNow19\StataMP-64.exe' -ArgumentList '/b','do','"<绝对路径>.do"' -WorkingDirectory <该 .do 所在 data\ 目录> -PassThru` + 先取 Handle; 轮询同名 `.log` 尾部 `NOTES_DTA_DONE=` 每 15s; 超时预算 listed 600s/份、tax 2400s/份 (R2 注: 07-15 限频态实测 listed ~8s/份、tax ~18s/份 [log mtime 推算], 本预算为宽上界防误杀, 非耗时预估); 串行总时长实测预期 ~3–10 min。
   - 判据: (a) 15 log 各含 `NOTES_DTA_DONE=<n>`, n == 该 dta 的 `expected_notes` (fingerprint sidecar `dta.<文件名>.expected_notes` 字段; .do 尾部 display 硬编码与 sidecar 逐份相等已由 R2 全核); (b) r(###) 边界扫描 15 log = 0; (c) pyreadstat metadataonly 复读 15 dta `meta.notes` 条数 == expected+1; (d) 行×列不变 (105,032 / 447,710); (e) 值哈希抽验 2 份 (listed cooc + tax frozenw), **含配方校准步 (R2-A1)**: fingerprint `value_hash` 的归约配方仓内无记录 → 重放前先对当前干净态 dta (值与注入态恒等) 试算候选配方 (`sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes())` 及 index=True 变体等), 命中 fingerprint `value_hash` 者冻结为配方并回填本条; 重放后以冻结配方复算 == fingerprint `value_hash`; **若无候选命中 → 降格判据**: 以固定配方 (index=False 变体) 重放前/后哈希相等 (同样证 notes-only 变更), 并如实记「fingerprint value_hash 本轮不可复验」。
   - **兜底击杀安全分支**: 击杀前先看 log — 已见 `NOTES_DTA_DONE=` → 数据安全 (save 已完成), 纯僵尸可杀 (07-15 shareholderw 同款先例); 未见且超时 → 杀后必以 pyreadstat **完整开读**该 dta 验损; 损坏则该 dta 走 ⑦/⑧ 对应引擎重生后重注, **勿直接重放 .do** (会 use 到坏文件)。
   - **fingerprint 刷新 (P2-3 采 (a) 案)**: 15 dta 全部重放成功后, 用 python 就地刷新两侧线 sidecar 的逐 dta `sha256` (+ 追加 `resha_at` 时间戳字段), **`expected_notes`/`notes_count`/`value_hash`/`families`/`rows`/`cols` 一律不动** — 保持 sidecar 作为跨轮对账锚的有效性; 主线 sidecar 由脚本自刷新, 无需手动。
3. **零副作用边界**: 重放前后各取 `os.stat(...).st_mtime_ns` 逐位比对 40/51 两 parquet; 重放新写文件全集 (逐名, 均被 gitignore) = 主线 3 dta + 3 master .log + `_notes_{pre,post}inject_snapshot.json` + `_notes_applied_fingerprint.json` (processed 下) / 侧线 15 dta + 15 `_notes_inject_*.log` + 2 个 fingerprint sidecar 的 sha 字段; `git status --porcelain` 期望全集 = ` M v3_5_1_constants.json` + `?? 本计划 md` 恰 2 行 (批次 B 前), 0 意外新增。
4. **批次 B**: commit 前 `git log --oneline -3` 确认无并发插队 (有则先阅读其意图); by-name add — commit(i) 恰 2 文件 (本计划 md [新增] + 上轮计划 md [修改]); commit(ii) 恰 1 文件 (constants); push 后 `git status` clean + `git log origin/main -3` 核实。
5. **无 pytest/ruff gate**: 本轮零 .py 改动 (fast A 基线 3 残红即终态, 存档=LEDGER 记录 + 本会话实跑输出)。

## 6. 残余风险

1. **N7-R2 判定的对称暴露**: 慢化既可自发消退亦可自发再现 — 任何长跑排期须按「最近一轮实测 + 起跑前计数器采样」滚动预算, 不可再固化任何一轮为「常态」。再现时优先做 §3-N7-R2 SOP 两个 5 分钟实测。
2. **notes 注入态的循环义务**: 任何入口重跑都会再抹 (①→主线 3 / ⑦→listed 10 / ⑧→tax 5); 交付前重放是永久性 checklist 项, 不是一次性整改。
3. **K2**: 侧线 codebook md 的会话修订在 canonical 重生下持续易失, 根治前每次 02/03 重跑都可能重演 — 归侧线会话收口。
4. G2 混代 (27 号旧代) / 生产 T=19 前置项: 上三轮 §7 全部继续有效, 本轮零解除。
5. 本机并发会话可能继续推进 HEAD/重生产物 (本轮已实证: dedup json 01:50 被覆写、目录 mtime 窗后推进); 本计划锚以 00:36–01:43 运行窗 + 01:43–02:3x 深审快照为准。

## 7. 生产 T=19 checklist (本轮增量, 与上三轮 §7 并存)

- [x] **N1-gate③ 尾巴 (上轮遗留)**: 本轮 46 重生后 `grep -cF '${' variable_codebook.json` = 0 → 判据自动满足, 打勾。
- [x] **N7-R2 (本轮定谳)**: 新常态预算作废; 预算滚动维护口径生效 (最近一轮实测 + 计数器佐证); ⑧ cap 回 2h 语义。
- [ ] **K1 循环义务**: 主管道/侧线任意重跑后、论文交付前, 重放对应 notes (主线 apply_stata_notes.ps1 后台分离+stdout 重定向 / 侧线 15 .do 按映射串行); 对账用 §3-K1 铁律 (主线禁 pyreadstat、走 log/sidecar; 侧线 pyreadstat 条数=期望+1; 禁尺寸单锚; r(###) 非字母边界)。
- [ ] **审计 SOP 增量**: run_paper.log 按日期窗过滤 (K4); 起跑前 Get-Counter 采样留痕 (N7-R2); .ps1 驱动全 ASCII 或带 BOM, 核验用 Get-Content -Encoding Default 行数对账 (DRV-1); 白名单新口径 (K3: one-hot ×10 + 81 号十族); G9 SOP (上轮 §5-6: A/B 差分前核 cross_media_alpha_full 在场性) 继续有效。
- [ ] (承接上三轮 §7 全部项: G2 三参数重生 27 号 / G12 建碁 longhit / G13 LDA 压测 / 离线冷缓存前置 / R2 codebook 竞态窗 / M0 门族。)

## 7-bis. 实施记录 (2026-07-16 批次 A 执行完毕后回填; 用户于任务发起时预授权「完全授权所有执行计划」)

- **批次 A-主线 (首跑 02:57 + K7 修复后 gate 重放 04:45, 双次收口)**: 首跑注入本体 3/3 成功但触发 K7 假阴性 (三 master 全谱僵尸滞留挂满 1800s → 误判 FAIL → sidecar 三键被删; 注入实际 ~19s/份, dta **字节数**与 07-15 注入态锚相等 66,450,164/66,505,604/66,617,018 [头部时戳致逐位必异, RR2-NIT-2 口径]); 失败态修复 = applied 从 master log `NOTES_APPLIED_PART*` 求和与 helper `expected` 逐一相等 (3442/3442/3453) 后 `sidecar-update` 回写。K7 修复落 `scripts/apply_stata_notes.ps1` 后**幂等重放端到端全绿**: 僵尸击杀路径 3/3 正确行使 (「DONE 已见但进程滞留 — 按僵尸击杀 (数据已安全)」) + 对账三行 applied=expected + master_done=True + sidecar 自动刷新 ×3 + 收尾行; r(###) 边界扫描 0×3。
- **批次 A-侧线 (04:30:55–04:42:28, ~11.5 分钟串行 15 .do; RR1 勘误原「12.5」笔误)**: 15/15 DONE_ZOMBIE_KILLED (僵尸全谱系统性, 驱动按 DONE 轮询正确兜底, 每份 46s); 五判据全绿 — DONE=expected 逐份 (24×10 + 32/32/30/23/23) / r(###)=0×15 / pyreadstat 条数=期望+1 逐份 / 行数 105,032·447,710 不变 / **值哈希抽验 2/2 与重放前冻结基线相等** (listed cooc `31f805fa…` / tax frozenw `c35ec183…`, 配方 `sha256(pd.util.hash_pandas_object(df, index=False).values.tobytes())` — R2-A1 校准步实测 4 候选配方均未命中 07-15 fingerprint `value_hash` → 按预案降格判据, fingerprint value_hash 本轮不可复验如实记录); fingerprint 15 键 `sha256`+`resha_at` 已刷新 (`expected_notes`/`notes_count`/`value_hash`/`families` 不动)。
- **零副作用边界 (§5-3 全绿)**: 40 号两 parquet + 51 诊断 csv mtime_ns 逐位不变; porcelain = 恰 4 项且全在预期集 (constants M + ps1 M [K7] + 上轮计划 M [修正案挂链] + 本计划 ??), 0 意外新增。
- **K7 发现与修复 (实施期新增, 详 §3-K7)**: 唯一 repo 代码修 (恰 1 文件, 编排层, golden 零风险); gate = 上述端到端重放全绿。
- **memory 已同步 (commit 外)**: 本轮 topic 文件 + MEMORY.md 索引行 + 上轮 topic N7 更正注。
- **批次 B**: 3 个 by-name commit (K7 修复 / 审计文档 ×2 / constants) — 提交与推送记录及 RR 结果评审见 §8-bis。

## 8. 评审记录 (逐轮回填; 收口标准 = ≥3 轮独立评审且末轮 0 未决 P0/P1, 全部 NEEDS_FIX 有落点或显式 DEFER, §5 gate 逐条可机械执行, 终判 ok_to_ship 由主笔签字回填)

- **R0**: 主笔初稿。
- **R1 (三路并行: 完整性 / 技术正确性·证据回落 / 可执行性·gate 机械化; okToShip = false / true-附修订 / false)**: 已逐条落实全部 29 条 (三路原始意见含跨路重复计数 [如 ×21 锚双路各计一次], 去重后 29 = 12+5+12; R3-NIT-1 算术勘误) —
  - 完整性 12 条: **P1-1 F 系编号与 07-10 轮 F 系二义** → 本轮改用 K 系 + 头注编号约定 + 历史引用逐处加轮次限定; P2-1 §0 定级标尺与台账标签互证 (P3 取消, K2 定级 P2, 普查改「NIT=3 [K3 含 2 子项]」); P2-2 N7-R2 计数器两窗数字统一 (97.8–106.4% 轻载 / 109–115.6% ⑦ 运行中, 双出处) + LEDGER 同步; P2-3 「447,710×21」无日志落点 → 改 447,710×1,914 并声明弃用 ×21 速记; P2-4 F3 (R0 草稿编号)→K1 占位符 :?? 回填 :66/:69; P2-5 上轮 N5/N6 残留后续补录 §2 (锁半边销案 + scratch_seg/进程并入清理批); NIT×6 (G9 SOP 前向携带 / NIT 计数同构 / ⑦ 分段格式修复 / 跑前 notes 态字节核验入 §2 / sidecar 陈旧消歧 [仅 sha/value_hash 陈旧, expected_notes 仍 SSOT] / D1 补 07-06 审计交叉引用) 全落。
  - 技术 5 条 (okToShip=true 附修订; 10 项承重断言 CONFIRMED 含 18/18 dta 字节锚、DRV-1 字节级 e5 88 b0 0a 复核、N7-R2 四点、14 个日志数值锚 13 中 1 无落点): ×21 锚同 P2-3; K2 「+911B 进入」方向纠正 (911=净减量, 携带证据=+10 行); fast 存档强度注明; D2 现态与振荡预登记; DRV-1 iconv 弱验证 → Get-Content -Encoding Default 行数对账口径。
  - 可执行性 12 条: **P1-1 主线 pyreadstat 判据不可执行** (变量级 notes 对 meta.notes 不可见, 照跑恒假红) → §5-1 判据全部改 log/console/sidecar 层 + 显式禁用条款; **P1-2 后台分离无命令形态且 console 对账证据会丢失** → §5-1 给出完整 Start-Process + RedirectStandardOutput 形态与逐条判据字面量; P2-1 侧线 15 .do 执行参数 (串行/WorkingDirectory=各自 data\/轮询 15s/超时 600s·2400s/总时长预估) 写死; P2-2 兜底击杀安全分支 (DONE 已见=僵尸可杀 / 未见=杀后完整开读验损, 损坏走引擎重生勿重放 .do); P2-3 fingerprint 重放后 sha 失锚 → 采 (a) 案就地刷新 sha 字段、其余字段不动; P2-4 3442 字面锚独立落点 (stdout 重定向 + sidecar n_notes_applied); P2-5 §5-3 机械命令 (mtime_ns 逐位 + porcelain 全集 2 行) + 重放新写文件逐名清单; NIT×5 (expected_notes 字段点名+期望值写死+244 口径二义排雷 / 插入点唯一锚 :141 亲验 / commit message 模板与 trailer / §7-bis 节新增+批次顺序依赖显式 / 值哈希抽验 2 份条款) 全落。
- **R2 (对抗复核, okToShip=TRUE 附修订; 「核心攻击全部未攻破」明确声明)**: 六大承重点全部经独立实证存活 — K1 双载体判定 (probe dta 现做实证: 变量级对 `meta.notes` 完全不可见、数据集级=期望+1; 附带复现 exit,clear 后 Stata 僵尸 → 轮询+兜底击杀策略必要性旁证) / DRV-1 (66→65 行 + `e5 88 b0 0a` 偏移 2251 字节级复现) / N7-R2 主判定 (driver2 env 与上轮等价、BLAS 全钉 1 → 多核误读替代解释被排除) / §5-1 判据字面量逐字核符 (对账行/收尾行/exit 语义/BOM 在场/零参任意 cwd 成立) / §5-2 (15 .do display 硬编码与 sidecar expected_notes 逐份相等; log 落 WorkingDirectory; save→display→exit 顺序使安全分支前提成立; metadataonly 可行) / 批次 B (:141 唯一 + porcelain 恰 2 行实测 + gitignore 逐一核)。数值锚抽验 ≥20 项全中, R1 落实 33 条抽查 12 条全落实。攻破 4 项已全部当即落实: **A-1 (P2)** value_hash 配方仓内无出处 → §5-2(e) 增配方校准步 + 降格判据双轨; **A-2 (P2)** stdout.log 落盘 CP936/GBK (实测 Write-Host 确被 -RedirectStandardOutput 捕获, 但中文字面 UTF-8 工具 0 命中) → §5-1(b) 判据改 ASCII 子串 + Encoding Default 读注; **A-3 (P2 文档)** 933s vs 07-10 2313.7s 矛盾 → 补跨轮链 (07-10 当轮已判争用慢化, 健康锚 ≈1133s) + 「均匀」改「带内一致 (00/26 两端例外注)」; **A-4 (NIT×4)** 预测兑现措辞 / sha-字节数字面 / 50GB 两类读消歧 / 244 口径推断标注 + 超时预算实测注 — 全落。未验证声明如实保留 (fast 3 残红未复跑 [证伪路径已给] / 07-12 进程 [已挂清理批] / 次要锚)。
- **R3 (终审签核, ok_to_ship=TRUE「愿为该判定的后果签名」)**: R1 段抽查 12/12 全落实 (含盘上实证: scratch_seg 3,613B 07-15 11:19 / 46 log :66·:69 亲验 / LEDGER 同步勘误在场) + R2 段 A-1..A-4 4/4 逐一核对且判据字面量与 apply_stata_notes.ps1 源码 (:109 对账行 / :131 收尾行) **零间隙**; §0↔§3↔§4↔§5↔§7 三向一致性终扫 0 承重不一致 (§1 墙钟合计 4,004s≈67 分钟自洽); 3 条指定承重断言亲手实跑 3/3 (`${`=0 / 上轮 :141 唯一+:142=N2 / porcelain 恰 2 行) + 15 项盘上字节/字面锚超额加固全中 (含侧线 15 .do 尾部 display 与 sidecar 逐字相等 → §5-2 安全分支前提实证); gate 可执行性逐条核查仅 1 处非阻断空隙; 一票否决排查 0 命中 (全部未验证项如实标注)。3 条 NIT 已当即落实: NIT-1 「33 条」→29 条 + 折算口径; NIT-2 §5-1 补主线失败分支; NIT-3 「F3(旧)」→「F3 (R0 草稿编号)」。**计划层收口: 三轮五路评审全绿 (R1 三路 + R2 对抗 + R3 终审); 批次 A/B 据用户预授权 (「完全授权所有执行计划」) 启动执行。** — 主笔签字回填, 2026-07-16。
- **§8-bis 结果评审补记 (实施后三轮, 2026-07-16)**: **RR1 (实施结果六维: diff 符合度/主线终态/侧线终态/零副作用/文档自洽/判据无放水) 6/6 全 PASS 0 FAIL** — ps1 唯一 hunk 与 §3-K7 修法逐点吻合零夹带; 挂链行插入文本程序化逐字比对 spec==actual:True; 主线 sidecar 三键 + 40 号 dta SHA256 亲算逐位; 侧线 15 键 + 2 份亲算 SHA256 逐位; parquet mtime 未动; porcelain 恰 4 项; §5 判据逐条「判据→实测→满足」清单 (降格判据系 R2-A1 预案非事后放水); 唯一 NIT (「12.5 分钟」→~11.5) 已修。**RR2 (对抗复证, 五攻击面 0 推翻)** — K7 修复六路攻击 (秒退窗口/数组 -match 语义/log 锁/tail 窗口/ExitCode 忽略/PS5.1 兼容) 全部「不可触发或 fail-safe」且三重独立护栏 (全文 doneMark + PART 求和==expected + r(###) 行首扫) 封死假成功通道; **注入真实性二进制物理层独立证实** (直接解析 dta118 characteristics 段: 40 号 21,660 个 ch 条目、note0=3442、变量级 note1=3442 真实中文长描述 — 同时证实「pyreadstat 不可见」论断); 隐藏副作用 -newermt 全集与 §5-3 声明集逐名恰等 0 计划外; §7-bis 诚实性核验 (首跑 3×TIMEOUT 失败如实入账, 原始 GBK 落件时序自洽 02:57+3×1800s=04:27=mtime); fingerprint 刷新仅 sha256+resha_at 其余字段全保留。2 NIT 已当即修: NIT-1 ps1 tail 5→50 加宽 (修后 BOM 在场复核 + Parser 0 错误); NIT-2 「逐位相等」→「字节数相等」两处 + memory 同步。**RR3 (终局签核, ok_to_push=TRUE「愿为该判定的后果签名」)**: 待推送 diff 逐行卫生 (4 文件级对象逐 hunk; 0 secrets/0 U+FFFD/0 夹带) / 三 NIT 修订终态 3/3 在场 / ps1 终态健康 (BOM EF BB BF + Parser 0 错误 + 除 K7 段零改动) / 全量清点 0 无着落 (台账逐条落点 + 3 commit 对 4 脏项三向一致) / memory 一致性抽 8 项全中 / 一票否决 0 命中 (DRV-1 全灭、K7 首跑误判、value_hash 降格、fast 未复跑等不利事实全数如实入账)。唯一 residual = memory「已提交」措辞超前数分钟 (推送后自愈)。**批次 B 提交与推送随即执行, 哈希记录于 memory topic 文件。** — 2026-07-16。
- **§8-ter 推送后终验补记 (用户指示追加两轮, 2026-07-16)**: **RR4 双镜头 (A 推送内容终验 / B 物理态与跨文档终验) 12/12 全 PASS 0 FAIL 0 新立案** — A: 三提交文件数与 §4 承诺逐一相符 (恰 1/2/1), K7 hunk 零夹带, 挂链插入行 byte-exact, 本地==远端==0aebdd08 双向空, 入库计划终稿 0 U+FFFD/0 未回填占位, trailer 协议逐字合规 (hook 执行按可验证性边界如实声明「无反证」); 唯一 NIT = 头注「K1–K6」未随 K7 扩号 (本 commit 已修)。B: 18 dta notes 终态全锚命中 (主线三键 3442/3442/3453 + 侧线 15 键 + pyreadstat 抽验 2 份新样本 25=24+1/31=30+1), 管道产物零扰动 (40 号两 parquet 仍 00:51 窗 + golden 未动 + 15 侧线 parquet 未动), 跨文档三角 (入库计划↔memory topic↔MEMORY.md 索引) 10/10 数字互证零矛盾, 证据链存档 11/11 在场非空, 现场 0 新增意外。**RR5 (绝对终局签核, ok_to_close=TRUE「愿为终局收口的后果承担责任」)** — 工作树差分恰 1 处 (本 NIT 修) / 六轮评审记录完备 / **用户委托八项 8/8 兑现且有据** (①v1 误杀后 v2 完整按序重跑满足实质, 最长 2099s≪3h) / 自由抽查 8 项全 PASS (含绕过日志的 pyreadstat 物理层亲读与 K7 三重护栏源码在场性) / 一票否决终扫 0 命中 (v1 全灭·K7 首跑误判·value_hash 降格·fast 不复跑·244 口径推断五处不利事实全数如实入账); residual 全部非阻断 (终局 commit 顺序义务=本 commit 兑现 / DEFER 族无断链 / frozenw 1,904 列备考非矛盾)。**本轮绝对收口。** — 2026-07-16。
