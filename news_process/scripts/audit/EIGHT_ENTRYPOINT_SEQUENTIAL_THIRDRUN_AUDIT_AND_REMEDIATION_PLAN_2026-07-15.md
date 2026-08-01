# 八入口顺序真跑第三轮审计 — 审计与整改执行计划 (2026-07-15 · R1 修订版, 评审记录见 §8)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 日期 2026-07-15 · 环境 OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP=1 / PYTHONIOENCODING=utf-8) · 解释器 F:\Anaconda3\python.exe (conda base 3.13.9) · cwd=news_process\ (⑦⑧=各自子目录) · 每入口 2h cap · 运行窗 11:47–15:43。
>
> 本轮 = 07-14 复审 (`EIGHT_ENTRYPOINT_SEQUENTIAL_RERUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-14.md`, 下称「上轮计划」) 之后, 跨 15 提交 (c306a424..26e1b609: codebook WP4 S08-S14 置 final 655/655 + 新颖度闸两轮 + WP5 YAML 误解析修复 38 家族 + 批次 A H2/H3/D1 + **26e1b609 stata_export 中和硬化**) 的第三次全谱复跑。批次 A (H2 46 号 logger / H3 N2 措辞) 与 26e1b609 硬化均为本轮**首次全管道真跑**。运行时代码增量收敛度高: 除批次 A 与 26e1b609 外, 全部 524 个增量文件为 codebook_longdesc 内容 (经 variable_codebook.json 只影响 46 号 notes 文本; 另有 build/codebook 产物 ×4 [即该 json 通道] 与审计文档 md ×2, 区间合计 536 文件 — R4 账面补记)。
>
> ⚠ **基线时间线披露 (R1 勘误)**: 审计开场快照 (~11:36) 时 stata_export 硬化尚为工作树未提交改动; WP5 会话于 **11:42:01 将其提交为 26e1b609 并推送 origin/main** (恰 1 文件 +18/-1, 与快照所见 hunk 逐字同 — 内容等同性已核), 早于 ① 起跑 11:47:32 → 本轮 8 入口实际全程跑在 **HEAD=26e1b609** 上, 运行结论零影响; 本计划 R0 初稿按「未提交世界」书写的全部文句已于 R1 改写到「已入库世界」。工作树剩余改动 = v3_5_1_constants.json (stage21 时间戳, run-dependent); R4 时点另核到并发会话新增 3 件未跟踪 (SIDEPROJECT_LONGDESC 计划 md ×2 + check_sideproject_citation_count.py, 归其会话提交, 本计划各批次 by-name 天然排除) — **codebook longdesc 侧线仍活跃**, N5 处置须计入此观察。
>
> 审计方法 = 静态预审 (增量影响矩阵 + 工作树 diff 逐行 + G9 机械口径核实) + 8 入口顺序真跑 (驱动脚本含 H4 修正, 逐入口 sentinel/console 归档) + 跑后逐入口锚对账 (主笔亲核) + 3 路只读深审代理 (主/验证日志 · 双 company 日志 · 产物态差分) + N7 根因五点取证 (盘测/CPU 满载计数器/powercfg)。证据归档: 会话 scratchpad `audit_2026-07-15\` (console/sentinels/pre_logs/snapshots + LEDGER.md)。
>
> ⚠ 本计划所引日志行号 = 2026-07-15 运行快照, 后续重跑行号漂移勿以行号立案。

## 0. 结论速览

- **8/8 成功 EXIT=0 · 0 真 ERROR · 0 Traceback · $0** (stage21 离线 13,896/13,896 全命中; 嵌入/BERT 全离线; ⑧ cap 违约 +116s 见 N8)。
- **golden 全谱零漂移 (本轮优于上轮)**: 面板 220×3442 / 文章 1005×1305 / 51: 220×3453 逐项同上轮; listed 10 dta 字节锚 10/10 全等 (主 1,610,634,683 / 7 权各 1,603,484,161 / frozenw 1,606,426,983 / mainbankw 1,617,142,173); tax 5 dta 字节**逐一全等**且区间端点与上轮逐字节同 (6,845,811,481–6,898,645,113); 双 registry 锚 023cdc9158ec52ba / 4f580e3fc458be0c 五点复算全链一致; **两 company 库 49 产物文件字节逐一全等 (0 B, 上轮 ±14…2,802 B 微漂本轮未现)**; 81 审计 158 项 0 FAIL / 20 WARN 逐位同上轮; 82 漏斗 9,490→5,031→1,650→1,005 复现; 三 notes 部件 .do + manifest 11/11 与今晨 11:28 WP5 版字节全等 (确定性 + 提交前工作树版与 26e1b609 输出一致双证)。
- **上轮跨轮义务 7/7 全兑现**: D2 (上轮编号) sidecar 6 警归零 (A 路核 40_build_panel.log benefit 警=0, sidecar mtime 仍 07-14 19:12 未动) · V9 grandfather 0 命中 · G9 修正口径准时 (全管道跑 → 75 陈旧 → stale-skip loud-warn 12:32:42, 面板守 3442; **+9 列只在 standalone 40 重跑触发**, 上轮 R1 的「下轮单独重跑 stage 40」表述准确, 本轮 ② 已再重生 75 → 振荡对未来 standalone 40 继续上膛) · H2 三锚首次入 stage log + 编排器镜像 (46 盲区闭合 live; 镜像形态漂移属上轮 §5-3 预登记, 不立案) · H3 新文案与同轮 2 条旗标 WARNING 语义成对 · G2a 哨兵 ⑦⑧ 各恰 1 次实弹, 指纹 d66f929b36eae28a 双管道核符 · H1 错峰纪律全程执行 (审计侧运行窗内零重 IO)。
- **本轮最大发现 (N7)**: 全链 ~3× 慢化的根因 = 电源方案 AC「最大处理器状态」被设为 **95%** → 按 Windows 文档口径阻止进入睿频档 → i9-13900K 满载钉在 69-70% 性能百分比 (重度限频实锤; 精确机制见 §3-N7 保留意见)。**07-14 计划 H1/D3 的「宿主争用伪回归」归因不完备, 本条为其修正案** (争用只解释 ~7%)。磁盘退化假说被实测反证 (F: 顺序写 1436 MB/s 健康)。产物数值零影响。决策 (恢复 100% 与否) 挂用户 — 13900K 属 Raptor Lake Vmin 退化受影响 SKU, 95% 上限可能是有意的稳定性缓解。
- **本轮定级: P0=0 · P1=2 (N1 代码+测试, N7 运行环境·挂用户) · P2=1 (N8 治理·随 N7) · NIT=5 (N3, N4, N5, N6, N9; 其中 N3/N4 为 NIT·SOP 子类 — 标尺沿用上两轮四级 [P0/P1/P2/NIT], SOP 仅为 NIT 内子标注, 镜像上轮 H4「NIT·审计 SOP」先例) · 记录=1 (N2) · 销案=4 (D1–D4)**。全部非阻断; 唯一代码修 = N1 (纯文本层 golden-safe)。
- 上轮 §7 增量四项逐项对账: H1 → 本轮 N7 修正案; H1-cap → N8 (随 N7 呈报); R2 纪律 (上轮编号) → **本轮遵守** (codebook json 最后重生 10:56 / notes 注入 11:33 结束, 与 ① 运行窗 11:47 起零重叠); D2 (上轮编号) → 归零兑现。
- 静态预审吸收声明: 预审三预测全兑现零废弃 — (a) G9 全管道口径修正 (预测 stale-skip 警告 + 面板守 3442, 精确兑现); (b) N1 测试必红 (预测恰 1 红, 实跑 1/39 兑现); (c) 46 号 notes 重生与 11:28 版字节全等 (兑现 11/11)。

## 1. 运行结果总览

| # | 入口 | 结果 | 墙钟 | 上轮 (07-14) | 07-10 基线 | 关键证据 |
|---|------|------|------|------|------|---------|
| ① | run_pipeline_function | ✅ 0 | 2775.8s | 2875.8s | 2313.7s | 16/16; 13,896 离线全命中; 220×3442 / 1005×1305 / 220×3453; 34 WARNING 全白名单; 75 stale-skip 12:32:42 准时 |
| ② | run_pipeline_validation | ✅ 0 | 722.6s | 691.2s | 635.8s | 16/16; H3 文案 live; 66/70 离线跳过; κ 哨兵 0.7794/0.8149 复现; 72 号 ~9min 静默 CPU 段 (单核 94% 活跃, 非挂死) |
| ③ | run_paper (裸跑) | ✅ 0 | 1.2s | 0.9s | 0.8s | 11/11 篇 0 render 失败, 0 ERROR |
| ④ | 80_placebo_and_alt_anchor | ✅ 0 | 2.0s | 1.7s | 1.6s | 143×29; sidecar 落盘; embedding_dim=4096 |
| ⑤ | 81_stata_data_audit | ✅ 0 | 2.9s | 2.6s | 2.6s | 158 项 0 FAIL / 20 WARN 逐位同上轮; 40=3442 / 51=3453; 恒等式族 46 项全绿 |
| ⑥ | 82_export_stats_excel | ✅ 0 | 1.4s | 1.0s | 1.0s | 漏斗 9,490→5,031→1,650→1,005 |
| ⑦ | company_listed_bank | ✅ 0 | 2877.2s | 2950.6s | 1880s | 锚 023cdc9158ec52ba ×8; 10/10 dta 字节锚全等; G2a ×1 指纹核符; F11 锁干净释放 |
| ⑧ | company_tax_bank | ✅ 0 ⚠cap+116s | 7316.1s | 7896.4s ⚠cap | 2636.6s | 锚 4f580e3fc458be0c ×8; 5 dta 字节逐一全等; 447,710 ×21; 建碁 668 同形; 01=61.4/02=986.8/03=4498/04=1766 (vs 上轮 = 105.1%/93.0%/91.4%/95.4% → N7) |

驱动层注: 首次启动 ① 时驱动脚本 cmd /c 嵌套引号缺陷致 python 未拉起即 EXIT=1 (0 副作用, N4 当轮已修, batch 文件中转模板干跑三项验证后 8/8 全程可信)。

## 2. 白名单对账 (上轮已裁定项, 本轮全谱同形复现, 不再立案)

- ①: 34 条 WARNING 全命中 (Bartik 弱 IV 族 / share one-hot ×8 / 前视掩码 ×2 / 零方差常量 ×2 / stage13 掉 9 家 151→142 / 变量名 33 字符 ×3 (exc_jiang_2021 族) / 跨目录同名副本 ×1 / csdid never-treated / DiD HQ-based / 负极句 #3 投影 0.1416 / 6-1506 jieba / 小样本 T=2 ×2 / 75 陈旧跳过 [G9 预登记])。
- ②: 旧版单文件工作台 ×4 (61/64 各处, DEFERRED 清理批既载) / 61 旗标放行 ×2 (与 H3 汇总语义成对) / 62 输入 10,076 行 / 63 demo_mode / 66·70 冷缓存离线跳过 / F14 覆盖率非单调 Δα 三值 (-0.3184/-0.1523/-0.1250) / 媒体单类 100% / κ sentinel range ×4。
- ⑦⑧: G2a 哨兵各恰 1 次 (指纹 d66f929b36eae28a 双管道逐字一致, 预登记「应当出现」兑现; 27 号仍 07-03 旧代, 生产前须按 §7-G2 三参数重生) / 40 加权列全 NaN (F3) / 3 基名缺源列 (G8 DEFERRED) / 豁免基名 ×4 / 建碁 67.9% (668/984, G12 义务维持) / mainbankw tie / 磨损与左截断 by-design 披露 / tax 03 反向证据三件套对称 (branch_county 0.3688× 1 个点名, 同形)。
- 深审三路独立复核: 白名单外 WARNING **0 新增** (A 路 35 日志 / B 路 10 日志逐条聚类对账)。
- 预登记防误立案: 46_network_spillovers 输入行 df_exploded 显示 1,005×**1,356** = 1305 + 51 个 BERT 分布文章级临时列 (documented, runner 步骤 9 前单点 drop, 落盘仍 1305) — 中间态宽度非漂移, 勿以 1356≠1305 立案。

### §2-bis · 本轮「预期形态变化」对账 (变化≠缺陷)

| 变化 | 归因 | 判定 |
|---|---|---|
| ① 镜像含 46 号模块 INFO/三锚, `│⚠` 计数与上轮不同 | H2 修复 (28716f93) 首次全管道生效 | ✓ 上轮 §5-3 预登记兑现, 永久新形态 |
| 61 号汇总行新文案「未被 N2 拦截…」 | H3 修复首次管道内出现 | ✓ 预期 |
| 40/46/51 三 dta 8,191,835 / 8,254,163 / 8,218,235 B (今晨曾为 66.4-66.6 MB) | 今晨 11:30-11:33 WP5 注入 notes 膨胀 (+58MB 注释文本), ① 重生为干净无 notes 正常态 (220×3442×8B≈6MB+开销, 与 parquet 4.7MB 比例正常) | ✓ by-design; notes 重放义务见 N2 |
| `_spotcheck_notes.do/.log` 消失 | 今晨注入自检临时件, 被 46 号预清理 | ✓ 合理清理 |
| `dedup_sensitivity_summary.json` 980→1798 B | 今晨 08:36 某会话局部工具产物被 ① 恢复为管道全量格点规范态 (未跟踪 run-artifact) | ✓ 良性恢复, 销案 D2 |
| company 双库 parquet 本轮 0 B 漂移 (上轮 ±14…2,802 B) | 上轮微漂归因候选 (40/51 BLAS-FP → company 加权衍生) 本轮未触发 — 与「本轮 40/51 数值与上轮完全同代」一致 | ✓ 优于预期; 微漂非必然, 维持 run-dependent 判定 |

## 3. 新问题台账 (N 系; 每条已主笔亲核或双源坐实)

### N1 · [P1 · 代码+测试 · NEEDS_FIX] 26e1b609 只入库了硬化的一半 (缺 ①-c 顺序调换 + 配套测试) → **origin/main 套件常驻 1 红**
- **证据**: HEAD=26e1b609 (`fix(stata_export): notes 文本层补齐 {}/{/* 中和…`, 07-15 11:42:01, 已推送 origin/main, 恰 1 文件 `pipeline/panel/stata_export.py` +18/-1) 新增 ①-b2 花括号全量中和 (:1297-1303 `{`→`｛` `}`→`｝`) + ④-b `/*`→`／＊` (:1309-1317), **未随行任何测试更新** (test_stata_notes_do.py 最后触碰仍是 2da33939); `tests/test_stata_notes_do.py:66` 断言 `'＄{brace}' in out2` **必红** (三方独立实跑确认恰 1 失败/39)。根因 = ①-b2 插在 ①-c ($ 窄面中和 :1304-1306) **之前**: `${brace}` 先变 `$｛brace｝`, `$` 后接全角 `｛` 不再命中 lookahead `[A-Za-z_{]` → `$` 残留 ASCII。Stata 语义惰性安全 ($+非宏名起始字符 probe 先例; R1 技术路模拟确认 `$｛`/`$｝` 残留同类安全、④/④-b 交互零新破), 但比双中和弱一档且与测试期望冲突。**红灯已在远端主干, 任何人跑 fast sweep 即见 — 紧迫度高于 R0 初判的「工作树未提交漂移」一档。**
- **背景 (承重修复, 补全后闭环)**: 26e1b609 是今晨 WP5 会话 r(198) 三 dta notes 注入全灭事故的防御纵深半边 (另半边 = a44d4217 修 38 家族 YAML 源头); 已被实机验证 — 11:28 用该代码重生部件 → 11:30-11:33 三 dta 注入成功 (NOTES_MASTER_DONE ×3, 对账 3442/3442/3453 恰合列数); 本轮 ① 46 号重生与 11:28 版 SHA256 11/11 全等再证输出稳定。
- **修法 (5 步, 单 follow-up commit)**:
  1. `stata_export.py`: ①-c 块 ($ 窄面, :1304-1306, 含注释共 3 行) **整体挪到 :1297 (①-b2 注释首行) 之前** (唯一解: ③换行→①-a→①-b→①-c→①-b2→④→④-b→⑤) → `${brace}` 产出 `＄｛brace｝` 双中和。**标号处置**: 保留各步原标号不重编 (①-c 物理位置前移但名字不变, diff 最小), ①-c 注释整段替换为: 「①-c $ 窄面中和 (仅后接合法宏名起始字符时危险; 执行序刻意在 ①-b2 花括号中和**之前** — `${` 序列由本步先中和 $, 再由 ①-b2 中和 {, 产出 ＄｛ 双中和; probe 边界实证 $100 / "$ " / 行尾 $ 原样入库安全)」。
  2. 同文件 docstring 处理顺序清单 (:1273-1288): 在现步骤 4 ($ 窄面) 条目内加半句「(执行序在花括号中和之前, `${` 产 `＄｛` 双中和)」; 其后插入新条目「4-bis. 一切 `{`/`}` → 全角 ｛｝ (全量 — 2026-07-15 追加, 行尾孤立 { 触发 r(198) 实证)」; 在现步骤 5 (//) 条目后插入「5-bis. 一切 `/*` → ／＊ (全量 — 2026-07-15 追加, /* 块注释无需前导空白且跨行吞括号)」。
  3. `tests/test_stata_notes_do.py:66` 期望 `'＄{brace}'` → `'＄｛brace｝'`。
  4. 同文件补 2 用例 (归属 class = `TestNotesTextFuzz` [:51], 各自调用 `_assert_neutralized`): (a) `_stata_notes_text("sfx in {'', _hw}")` → 断言 == `"sfx in ｛'', _hw｝"` 且无 ASCII `{`/`}`; (b) `_stata_notes_text('*_full/*_ctx/*_ss')` → 断言 == `'*_full／＊_ctx／＊_ss'` (R1 双路亲手推演一致)。可选加固: `_assert_neutralized` 增三断言 `'{' not in text` / `'}' not in text` / `'/*' not in text` (已核对全部既有调用点零冲突)。
  5. by-name 提交 (恰 2 文件: `pipeline/panel/stata_export.py` + `tests/test_stata_notes_do.py`), commit message = 26e1b609 的 follow-up (①-c 执行序调换 + docstring 补录 + 配套测试), 姊妹链引用 a44d4217 + 26e1b609。
- **副作用披露**: ①-c 顺序调换只改变「`$` 后接 `{`」序列的输出 (`$｛`→`＄｛`)。**实测现有语料该序列计数 = 0** (11 件 .do 中 `$｛` 恰 0 命中, 源 json 无 `${` 正文) → 46 号重生 notes .do **预期与现版字节全等** (gate ③ 主判据); 若未来 codebook 正文引入 `${`, 输出为双中和形态 (§7 条件式尾巴)。golden 零风险 (纯 notes 文本层, 不触任何数值列)。
- **gate**: 见 §5 (逐条命令/前置/判据/副作用已机械化)。
- **归属披露**: 26e1b609 为 WP5 会话所提交; 本计划的 follow-up commit 代为补全测试与顺序, 提交前 `git log --oneline -3` 确认无 WP5 更新的后续提交插队 (有则先 rebase 阅读其意图)。

### N2 · [记录 · 义务] ① 按设计覆写今晨刚注入 notes 的三 dta — 重放义务挂 §7
- ① 的 40/46/51 重生把 dta 归位为干净无 notes 态 (D1); notes .do 族幂等可重放 (部件/master/manifest/注入 log 全存活, 且 ① 重生版与 11:28 注入用版 SHA256 11/11 全等 — 快照 `snapshots/pre_notes_do_sha256.txt`, 字节不等须立案的判据本轮以全等通过)。义务: 管道任意重跑后、论文交付前, 重放 `scripts/apply_stata_notes.ps1` (46 号日志 :66 明示入口; 零参调用即可, 脚本自动跑三 master + 前后快照 + 对账 + `^r\(\d+\)` 行首锚扫 [比 N3 口径更严, 引文子串免疫] + exit 0/1 机械判定); N1 落地后重放用重生后的 .do (预期与现版字节全等, 见 §3-N1 副作用)。重放副作用披露 (R4): 重写三 dta 并膨胀回 ~66MB 带 notes 态 (+ `_notes_{pre,post}inject_snapshot.json` 2 件 + 3 个 master .log), 40/51 dta 的干净态字节自此变化, 属预期形态勿立案。

### N7 · [P1 · 运行环境根因 · 决策挂用户 · 零代码] 全链 ~3× 慢化根因 = AC「最大处理器状态」95% → 睿频被阻断
- **证据链 (五点, 均本轮实测; 分段比值 R4 实算勘误)**: ① ⑧ 独占窗 (审计侧零并发 IO) 7316.1s = 上轮「争用态」7896.4s 的 **92.65%** (分段 01/02/03/04 = 105.1%/93.0%/91.4%/95.4% — 三重段 02/03/04 落 91-96%, 01 为 ~60s 短步启动噪声级反超, 不改变同构判读) → 争用最多解释 ~7-9%; ② F: 盘顺序写实测 **1436 MB/s** (2GB fsync 基准, NVMe 健康) → 上轮 §7-H1「独占下纯写盘 <15 MB/s 则查盘硬件」判据虽触发 (dta 7-9 MB/s) 但**查盘结果 = 盘无病**, dta 慢是 pyreadstat 单线程 CPU 瓶颈在限频下的表现; ③ 16 线程满载态 `\Processor Information(_Total)\% Processor Performance` 钉死 **69-70%** (i9-13900K 健康满载应 150-190%); ④ `powercfg /query SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX`: **AC=0x5F (95%)** / DC=0x64 (100%) — Windows 文档口径: 最大处理器状态 <100% 阻止进入睿频档 (经典 99% 关睿频技巧同源; R1 技术路保留意见: 13900K 走 HWP, 严格说是最大性能比例压制而非二值开关, 且 95% 算术上不能直接推出满载 69-70% — 可能叠加功耗墙/EPP/P·E 核基准混合, 精确机制以 gate 实测定谳, 不影响「重度限频在场且该设置是首要可操作变量」的结论); ⑤ 变化窗口 = 07-10 (⑧ 2636.6s 快) → 07-14 (7896.4s 慢); 07-07 KB5094126/KB5094135 早于快跑, **排除系统更新源**; 07-12 16:31 三 idle python + 三 powershell 遗留会话与窗口重合 (相关非因果, 无直接证据)。⚠ 诚实性注 (R2): 07-10 时点的 PROCTHROTTLEMAX 取值**无直接观测记录** (powercfg 无历史审计), 「窗口内变更」系由 07-10 快跑数值反推 (若 95% 彼时已在场, 2636.6s 与限频态 ~7300s 不相容), 非现场取证; 散热退化假说有反证 (满载性能百分比钉死 69-70% 恒定不波动, 热限特征应随温度波动), 非 Windows-Update 通道的 BIOS/微码变更未逐一排除 — 但三选一决策框架对根因误判稳健 (选 (a) 自带定谳 gate 且 powercfg 改动可逆零损失, gate 失败即当场证伪转入深查)。
- **影响 (白话)**: CPU 睿频被关, 所有算密集段 (加权引擎 / LDA / pyreadstat 写 dta / stage 72 正交性) 一律 ~2.5-3× 变慢; ⑧ 连续两轮击穿 2h cap 的直接原因; 产物数值零影响 (全部字节/行列锚全等)。
- **动作 (不擅自执行, 呈报用户三选一)**:
  - (a) 恢复: `powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 100; powercfg /setactive SCHEME_CURRENT` — **前提 = 用户确认 95% 非有意设置**。⚠ i9-13900K 属 Raptor Lake Vmin 退化受影响 SKU, 95% 上限是业界常见稳定性缓解; 若机器曾有不稳/蓝屏史或由维修方设置, 恢复前建议先确认 Intel 微码已更新 (0x12B 及以后) 且知悉风险。执行注 (R4): `setacvalueindex` 可能需管理员权限 (报「拒绝访问」则换管理员 PowerShell); 本机 powercfg 输出为中文本地化, 改后核验判据 = `/query` 输出的「当前交流电源设置索引」行 = `0x00000064` (勿按英文 'AC' grep)。**回滚命令** (出现任何不稳当场执行, 恢复现测原值): `powercfg /setacvalueindex SCHEME_CURRENT SUB_PROCESSOR PROCTHROTTLEMAX 95; powercfg /setactive SCHEME_CURRENT` (DC 侧 0x64 本就未动不碰; 执行前后各 `/query` 一次留痕);
  - (b) 保留 95%: 接受新常态, 全部耗时预算按本轮实测重校准 (⑧≈7300s, ⑦≈2880s, ①≈2780s), ⑧ 的 2h cap 上调或拆分;
  - (c) 折中: PROCTHROTTLEMAX=99% (仍禁睿频但略升) — 不推荐, 不解决问题。
- **连带修正 (07-14 计划勘误, 零代码文档面)**: 上轮 H1/D3「宿主 IO/CPU 争用伪回归」归因**不完备**: 真实构成 = 限频 (主, ~3×) + 争用 (次, ~7%); 上轮「⑧ 步骤 02 段争用实锤 = ⑦ 深审代理 15GB 哈希」只是次要分量; H1「独占时段硬义务 + per-步骤预算 ×3 争用系数」两项的经验基础随之失效, 按用户对本条的决策重写 (若恢复睿频 → 预算回 07-10 基线口径; 若保留 → 按本轮实测)。上轮计划不改写正文, 以本计划为修正案挂链 (镜像上轮对 07-10 计划的处理方式)。公允性注 (R4): 上轮 §0 本就预登记「产物零影响结论不依赖争用归因完备性, §7 独占复测为裁决试验」— 本条正是该试验的裁决结果, 属上轮方法论的既定后续, 而非推翻。
- **gate (R4 机械化)**: 用户决策 (a) 后单跑 ⑧ 步骤 01 (`company_tax_bank` 内 01 号, 按 §5 gate 4 tax 侧同式, 幂等只读; 本轮限频态 61.4s): **≤35s 判 PASS** (较 61.4s ≥1.75×); >35s 且满载 counter 仍 <100% → (a) 当场证伪, 转 §3-N7 保留意见深查 (功耗墙/微码/BIOS)。counter 测量命令 (01 运行期间另窗采样取 max): `Get-Counter '\Processor Information(_Total)\% Processor Performance' -SampleInterval 1 -MaxSamples 10` — 判据 max >150% (英文 counter 路径在中文 locale 实测可用)。决策 (b) 则无 gate, §7 预算表更新即收口。

### N8 · [P2 · 运行治理 · 随 N7 决策] ⑧ 连续第二轮击穿 2h cap (本轮独占窗 +116s)
- 7316.1s vs cap 7200s。本轮再次按 07-14 H1 先例裁量「健康推进放行」(进程无挂死, 杀 mainbankw 写盘中 1.6GB dta 损失>收益), 全程留痕, 违约如实立案。cap 语义 (kill-at-cap vs 健康放行) 上轮已挂用户未决, 本轮与 N7 绑定呈报: N7 选 (a) 恢复睿频 → ⑧ 预期回 ~2600s, cap 自然满足; 选 (b) → cap 必须上调至 ≥2.5h 或接受每轮违约。

### N3 · [NIT·SOP · 文档] r(###) 日志扫描引文年份假阳性
- 今晨三注入 log 各 3×`r(1965)` + 21×`r(2018)` 命中, 逐条核验全为 "Gombe**r(2018)**" / "…e**r(1965)**" 引文子串, 0 真错误。既有 SOP「扫同名 .log 的 r(###) 取真实结果」在 notes 正文含学术引文后必然假阳。修正: 扫描一律用 `grep -E "(^|[^A-Za-z])r\([0-9]+\)"` (非字母前置边界)。落点: 本计划本条 + memory stata-launch-batch-mode 更新 + 后续审计 SOP 沿用。零代码。
### N4 · [NIT·SOP · 当轮已修] 审计驱动层 cmd /c 嵌套引号缺陷 (H4 家族)
- `Start-Process -ArgumentList '/c', $cmdline` 拼接破坏嵌套引号 → python 未启动即 EXIT=1 (首启 ①, 0 副作用)。修法 = 驱动生成 batch 文件中转 (退出码透传 / env 继承 / UTF-8 三项干跑验证后 8/8 全程可信)。记录防再犯, 驱动模板归档于会话 scratchpad, 不入 repo。
### N5 · [NIT · 待并发会话确认] 陈旧会话残留
- `config/codebook_longdesc/.session_lock` (2026-07-10, owner=codebook-longdesc-orchestrator; WP4 已 655/655 收官 + WP5 注入已成功) + 3 个 2026-07-12 16:31 启动的 idle python 进程 (累计 CPU ~10min/3 天) + 同窗 3 个 powershell。若 codebook 编排确已收官 → 锁可删、进程可杀; **须先经用户/该会话确认, 不单方面动** (07-12 16:31 恰在 N7 变化窗内, 杀前留意其身份)。⚠ R4 新证据: 并发会话当日新增 SIDEPROJECT_LONGDESC 扩展计划 ×3 件 — **longdesc 侧线仍活跃**, 「已收官」前提被削弱, 锁与进程的清理在侧线收口前**建议维持现状** (删锁可能干扰其单会话锁机制); 即使获得全量授权, 本条也应按此新证据保守执行并留痕。
### N6 · [NIT] 工作树取证杂物
- repo 根 `blob_shas.txt`/`blob_sizes.txt`/`blobs_list.txt`/`candidates2.txt` + `news_process/scratch_seg.txt` (上轮 RR5 NIT-a 已点名, 仍在)。清理或留置由用户定; 任何提交一律 by-name 排除。
### N9 · [NIT · 观察] ② stage 72 静默长杆
- 72_construct_orthogonality 有 ~9min 无日志输出的单核计算段 (CPU 活跃 94%, 非挂死; ② 总墙钟仍 722.6s 正常)。限频解除后预期显著回落; 若生产 T=19 仍长, 可补进度日志。本轮不动。

### 销案 (D 系, 查过非缺陷)
- **D1 · 三 dta「回落至 8.2MB」非异常**: 8,191,835/8,254,163/8,218,235 B = 干净无 notes 正常态 (220×3442 float64 ≈6MB + 开销; 与 parquet 4.7MB 比例 ~1.7× 正常); 今晨 66.4-66.6MB 系 notes 注入膨胀态 (+58MB 文本)。审计中间稿曾以 66MB 为预期属主笔笔误, C 路代理纠正, 特此留痕防后人再立案。
- **D2 · dedup_sensitivity_summary.json 980→1798B**: ① 恢复管道全量格点规范态; 980B 为今晨 08:36 某会话局部产物; 未跟踪 run-artifact, 良性。
- **D3 · ② 72 号 9min 静默**: CPU 活跃实证 (5s 采样 delta 4.69s), 收 N9 观察, 非挂死非缺陷。
- **D4 · F11 锁只记释放不记获取**: by-design (能释放即证已获取), B 路核双管道成对干净。

## 4. 修复批次 (先过 gate 再 commit; by-name stage, 排除并发产物与 N6 杂物)

- **批次 A (N1, 1 follow-up commit, 恰 2 文件)**: `pipeline/panel/stata_export.py` (①-c 顺序调换 + 注释整段替换 + docstring 补两步) · `tests/test_stata_notes_do.py` (:66 期望 + 2 新用例 + 可选辅助断言收紧)。预算: 编辑 20min + gate 15min。⚠ 工作树 `v3_5_1_constants.json` (run-dependent 时间戳) 按 by-name 纪律排除。
- **批次 B (repo 文档, 1 commit)**: 本计划 md 终稿 (§8 评审记录回填) + 上轮计划 §7 增量挂链一行 (N7 修正案引用, 不改写上轮正文; 插入点 = 上轮 §7 D2 行之后、承接行之前 [R4 预演定位 :122/:123 之间], 文本: 「- [x→修正案] **H1/H1-cap (2026-07-15 第三轮定谳)**: 慢化根因 = AC PROCTHROTTLEMAX=95% 限频 (争用仅 ~7-9%), 独占硬义务与 ×3 争用系数的经验基础失效; 预算/cap 以第三轮计划 §3-N7/N8 + 用户决策为准, 见 EIGHT_ENTRYPOINT_SEQUENTIAL_THIRDRUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-15.md。」)。**commit 外动作** (memory 在 repo 外, 不入 commit): memory 更新 N3 SOP (r(###) 边界口径入 stata-launch-batch-mode) + 26e1b609 基线漂移与 N7 根因入本轮 topic 文件。
- **呈报用户决策 (零代码, 不随批次)**: N7 三选一 (电源设置) · N8 cap 语义 (随 N7) · N5 清理授权 · N2 notes 注入重放时机 (批次 A 落地后重放, 或与下次 codebook 重生合并)。
- **DEFERRED (维持, 逐项点名防断链)**: G2(b) 硬锁层 (M0) · G6(b) 81 扩检 46_full · G10 census from-summary · 清理批 (t2v 孤儿 + 弃用工作台 ×4) · F1(a) 税调匹配层过滤 · R2 根治族 (codebook json 原子写 + 46 侧校验 + benefit sidecar 原子写) · boilerplate tier2 · G9 振荡根治 (75 并入主管道或 40 侧 lineage 锁, 现状 loud-warn 可接受)。
- **刻意不做**: N7 的擅自恢复 (用户硬件稳定性权衡) · N5 单方面清理 (跨会话) · N9 性能修 (限频解除前无意义) · G2a 哨兵消音 (实弹验证通道) · 上轮计划正文改写 (以修正案挂链)。

## 5. 验证 gate (批次 A, 全部 cwd=`F:\WiseSearch\data_antigravity_project\news_process`, 解释器 F:\Anaconda3\python.exe; gate 1 的 pytest 建议从 repo 根 `F:\WiseSearch\data_antigravity_project` 跑 [pyproject testpaths 所在层], 或 A/B 双侧严格同 cwd — 与 env 口径同理)

1. **步骤 0 基线先行**: `pytest -m fast` 记录当前红灯清单 (含 N1 已知 1 红) → 编辑 → 复跑, 差分 **0 新增失败且 N1 红转绿**。预期红灯 ≈ 上轮基线 3 红 (benefit cohort ×2 + jieba isolation ×1, 上轮 §7-bis/RR4 存档) + N1 恰 1 红 = **4 红**; 跨 15 提交若基线漂移, 以步骤 0 实录差分为准, 勿以绝对数立案。env 口径 (上轮 RR4 原文): fast sweep **不带** NEWS_PROCESS_LLM_OFFLINE 跑, 或 A/B 双侧严格同 env — 带 OFFLINE 会翻转 3 个离线守卫敏感测试 (fetch_llm ×2 + lg soft-degrade), 单侧带则差分失真。
2. `pytest tests/test_stata_notes_do.py -q` **41 项全绿** (前提 `build/codebook/variable_codebook.json` 在盘; 若缺席则为 40 pass + 1 skip [`test_loader_reads_real_wp1_output_when_present`], 同样算过)。
3. **单跑 46 (notes .do 确定性 A/B, 已机械化)**:
   - 步骤 3a **基线保全 (必须先做, 重生即覆写)**: 把 `data/processed/` 下 11 件 (apply_notes_part01..07.do + 3 个 *_apply_notes_master.do + apply_notes_manifest.json) `Copy-Item` 到 scratchpad 基线目录并 `Get-FileHash -Algorithm SHA256` 留档;
   - 步骤 3b 前置: 40_panel_yearly.parquet 与 variable_codebook.json 双在盘; 竞态防护: 单跑前后各取 json (size, mtime_ns) 一致, 不一致则该次作废重跑;
   - 步骤 3c: `F:\Anaconda3\python.exe 46_stata_export.py` EXIT=0;
   - 步骤 3d **主判据: 重生 11 件与 3a 基线 SHA256 逐件比较, 预期 11/11 全等** (依据: 现语料 `$｛` 计数实测 = 0, ①-c 调序对现语料输出零差; **0 差异即为预期, 全等勿疑 gate 未生效**);
   - 步骤 3e 降级判定树 (仅当 3d 有不等时): 允许集**仅** `$｛→＄｛` — 机械判: new 中 `＄｛` 计数 == old 中 `$｛` 计数, 且 new 中 `$｛` 计数 == 0, 且按 `* ---- <col> ` 分块后仅受影响列块 (定义 = old 侧块内 `$｛` 计数 >0 的块) 有差; **分块判据仅施于 apply_notes_part0*.do** (master/manifest 无 `* ---- ` 分隔且不含 notes 正文, manifest 无哈希键不受 part 变更连带) — **master 或 manifest 出现任何字节差 → 直接 FAIL 须查**; 其余任何差异 (含 `｛｝`/`／＊` 类新差 — 基线本就出自 26e1b609 代码, 这两类不应再变) = **FAIL 须查**。判据依据的主锚 = **源 json `${` 计数 = 0** (`grep -cF '${' build/codebook/variable_codebook.json`, R2 复测 0; .do 侧 `$｛` 计数为旁证 — 段边界跨段形态被源侧 0 排除);
   - 副作用披露: 46 号全套产物重写 (46_panel_yearly_full.dta [format-118 头部时戳字节必变, 不在字节锚清单] + 46_*_labels.do + 46_*_codebook.xlsx), 均可接受。
4. **双 registry 锚复算** == 023cdc9158ec52ba / 4f580e3fc458be0c (批次不触 company 代码, 廉价保险)。可复制操作 (机械, 各管道目录下):
   - listed: `Set-Location F:\WiseSearch\data_antigravity_project\news_process\company_listed_bank; F:\Anaconda3\python.exe (Get-ChildItem 01_*.py).Name` → 跑完 `Select-String 'registry_content_sha256|sha256' logs\01_*.log | Select-Object -Last 3` 与锚 023cdc9158ec52ba 比对 (01 号上轮 5.6s / 本轮 4.8s 量级);
   - tax: 同式于 company_tax_bank (01 号本轮 61.4s), 锚 4f580e3fc458be0c。
   (01 号只读重建 registry, 幂等无副作用 — 本轮 ⑦⑧ 内 01→02→03→04 五点复算链先例。)
5. `ruff check pipeline/panel/stata_export.py tests/test_stata_notes_do.py` 全绿; 35 shim ≤30 行铁律不触碰 (批次 A 零 shim 文件)。
6. **跨轮义务 (下轮任意复跑顺带)**: G9 SOP (A/B 差分前核 cross_media_alpha_full 在场性) 继续有效; N1 落地后 46 重生 .do 与本版**字节全等或仅 `＄｛` 差**均属预期形态, 预登记勿立案; N7 决策后首跑记录新耗时基线并回填 §7 预算表。

## 6. 残余风险

1. **N7 决策悬置期间**: 所有长跑预算须按本轮实测 (⑧≈7300s) 编排, 任何固定 2h cap 对 ⑧ 必然违约; 13900K 若为退化缓解设置, 恢复睿频有稳定性风险 — 决策权与风险知情均在用户。
2. **N1 未落地期间**: **origin/main 常驻 1 红** (test_dollar_narrow_neutralization) — 26e1b609 已推送而测试未随行, 任何人/CI 跑 fast sweep 即见; 且 `${` 类正文在 ①-c 现顺序下只得单边中和。建议尽快授权批次 A (follow-up commit)。
3. **notes 注入态**: 三 dta 当前为干净无 notes 态 (① 覆写), 论文侧若需带 notes 的 dta 须先重放注入 (N2; 若批次 A 已落地, 用重生后的 .do)。
4. G2 混代根治 (M0) / 27 号旧代 / 生产 T=19 前置项: 上两轮 §7 全部继续有效, 本轮零解除。
5. 本机并发会话可能继续推进 HEAD/重生产物; 本计划锚以 11:47–15:43 运行窗 + 16:0x 深审快照为准。

## 7. 生产 T=19 checklist (本轮增量, 与上两轮 §7 并存)

- [x] **N7 (已决, 2026-07-15)**: 用户裁定维持 95% 现状 (方案 b) → 全链耗时预算 = 本轮实测口径 (①2780/⑦2880/⑧7300s), ⑧ cap = 预算+健康放行; §3-N7(a) 恢复/回滚命令留档备用。
- [x→修正案] **N7/N8 (2026-07-16 第四轮定谳)**: 慢化已自发消退 (powercfg 未变+无重启, 睿频实测 >100%), 95% 设置非充分根因, 新常态预算作废; 第四轮实测 ①933/②194/⑦771/⑧2099s 为新参照, ⑧ 2h cap 自然满足; 见 EIGHT_ENTRYPOINT_SEQUENTIAL_FOURTHRUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-16.md §3-N7-R2。
- [ ] **N2**: 主管道任意重跑后, 论文交付前重放 `scripts/apply_stata_notes.ps1` (三 master, 对账 3442/3442/3453 + NOTES_MASTER_DONE ×3; 扫 log 用 N3 修正后的 r(###) 边界口径)。
- [ ] **N1-gate③ 尾巴 (条件式)**: 批次 A 落地后首次生产 46 重生 — 先 `grep -c '\${' build/codebook/variable_codebook.json` (BRE 转义按工具适配): **=0 则记「0 命中, 判据自动满足」直接打勾**; >0 则抽对应部件核 `＄｛` 双中和形态在场 (现语料实测 =0, 该分支预期为主)。
- [ ] (承接上两轮 §7 全部项, 特别 G2 三参数重生 27 号 / G12 建碁 longhit / G13 LDA 压测 / 离线冷缓存前置 / R2 codebook 竞态窗。)

## 7-bis. 实施记录 (2026-07-15 晚, 用户完全授权后; R4/R5 追加评审亦系用户当轮指示)

- **批次 A (commit 3786ced5, 已推送 origin/main; by-name 恰 2 文件)**: ①-c 移位+注释整段替换 / docstring 4-bis·5-bis / test :66 期望 + 2 新用例 (TestNotesTextFuzz) + `_assert_neutralized` 收紧三断言。**gate 全绿**: 步骤 0 基线 fast sweep 恰 4 红 (与 §5-1 预测逐条一致) → 改后恰 3 红 (N1 转绿, 0 新增, 3 残红逐条同基线) / 定向 41/41 / 单跑 46 EXIT=0 9.7s + json (size,mtime_ns) 前后一致 + **11/11 SHA256 与 3a 基线全等 (3d 主判据精确命中, 3e 降级树未启用)** / 双锚复算 023cdc9158ec52ba…d082dd30 与 4f580e3fc458be0c…b6e4c034 未变 / ruff 绿。提交时并发 be370155 插队经核零文件交集。
- **N2 重放 (已执行)**: apply_stata_notes.ps1 零参; 三 dta 注回 notes 态且字节与今晨注入态逐字节同 (66,450,164/66,505,604/66,617,018); 对账 3442/3442/3453 + MASTER_DONE 各 ×1 + 真 r(###) 0 (N3 边界口径)。⚠ 执行注: 前台 10min 超时杀掉了脚本**收尾快照/汇总步** (三注入本体已完成), postinject snapshot 陈旧 — 对账由主笔按脚本同口径手动补齐等效; 下轮重放走后台分离模式。
- **N7 (用户终局裁定 2026-07-15 晚: 「放过这个问题」= 采方案 (b) 维持 95% 现状)**: powercfg 改动先被 Claude Code 权限分类器拦截, 用户亲执行两次未成 (Git Bash `/` 参数路径转换坑), 随后明示放下 → **新常态耗时口径生效**: ①≈2780s / ⑦≈2880s / ⑧≈7300s (本轮实测); 恢复命令与回滚保留在 §3-N7(a) 备用, 未来任意时点可重启该决策。
- **N8 (随 N7(b) 落定)**: ⑧ 的 2h cap 在新常态下**必然违约** → cap 语义定为「预算 ≈7300s + 健康推进放行, 挂死才 kill」; 后续排期按新常态预算表编排。
- **N5 (按 R4 新证据保守执行)**: 侧线当日活跃实锤 (SIDEPROJECT 计划 + LB001-012 实时改动 + be370155 提交) → 锁与 6 进程 (3 python + 3 powershell, 另见 5 个 07-12/今晨 cmd 残壳) **维持现状不动**, 挂侧线收口后处置。
- **N6 (已执行)**: 4 件 repo 根取证杂物已删 (blob_shas/blob_sizes/blobs_list/candidates2, 全部先归档 scratchpad `n6_junk_archive\`); scratch_seg.txt 因侧线活跃保守留置 (归档副本已存)。
- **N3 (已执行)**: memory stata-launch-batch-mode 已补 r(###) 非字母边界口径。
- **批次 B (本 commit)**: 本计划终稿 (§7-bis/§8-R4/R5 回填) + 上轮计划 §7 修正案挂链行。
- **实施期新增 SOP 教训 ×3 (H4 家族扩编, 记录防再犯)**: ① `powershell -File` 的参数值以 `-` 开头 (如 `-m pytest…`) 会被误绑为参数名 → 驱动秒崩零痕迹; ② 等待型监控**必须带心跳与失败覆盖** (进程消失告警), 否则静默死亡 = 无限白等 (本轮实赔 3.5h); ③ cmd 的 `echo X=%ERRORLEVEL%> file` 数字粘连 `1>` 被吃成流重定向 → 用 `set EC=…` + 括号 echo。

## 8. 评审记录 (逐轮回填; 收口标准 = ≥3 轮独立评审且末轮 0 未决 P0/P1 [决策项以显式挂用户视同已决], 全部 NEEDS_FIX 有 file:line 落点或显式 DEFER, §5 gate 逐条可机械执行, 终判 ok_to_ship 由主笔签字回填)

- **R0**: 主笔初稿。
- **R1 (三路并行: 完整性 / 技术正确性·证据回落 / 可执行性·gate 机械化; okToShip = false/false/true-有条件)**: 已逐条落实全部 19 条 —
  - 完整性 6 条: **P1-1 (本轮最大评审发现)** N1「工作树未提交」前提被盘上事实推翻 — 硬化已于 11:42:01 提交为 26e1b609 并推送 origin/main (恰 1 文件无测试, ①-c 顺序未调换, 红灯常驻远端主干), 早于 ① 起跑 5 分钟 → 头注/§0/§3-N1/§4/§6.2 全部改写到「已入库世界」+ 基线时间线披露段 + LEDGER 同步勘误; P2-1 N2 无台账条目却被引用 4 次 → §3 补 N2 条目 + §0 普查补「记录=1」; NIT×4 (D4→D2 编号 / SOP 子类声明 / 批次 B memory 拆分 / R2 纪律遵守半句) 全落。
  - 技术 3 条: N1 前提 REFUTED (同上, 双路独立坐实); 其余全 CONFIRMED (行号四组锚精确 / 调序推演双实现模拟字节级一致 + ④与④-b 交互零新破 + `$｛`/`$｝` 残留同类安全 / 39 用例逐输入排查唯 :66 受影响 / 新用例输出亲手推演 / powercfg 独立复测 0x5f / G9 机械推演严格成立含 75=2键+9payload 实读 / D1 销案数学严丝合缝含 17KB/列↔json 17.5KB/条 1:1 旁证 / 81·⑧dta·notes 11/11 三锚回落全中); N7 语义措辞降一档 (HWP 比例压制非二值开关, 95% 算术不能直接推出 69-70%, gate 实测为最终定谳) 已落; LEDGER「96%」笔误勘误为 92.65%≈93%。
  - 可执行性 10 条: **P1-1** gate 3 基线保全缺步 (重生即覆写 11 件, 比较对象先没了) → 补步骤 3a; **P1-2** 「仅中和类差异」不可机械判定 + 允许集过宽 (`｛｝`/`／＊` 类不应再变) → 主判据改「11/11 SHA256 全等为预期」(依据 = 现语料 `$｛` 计数实测 0) + 降级判定树 (仅 `$｛→＄｛` 允许集, 计数恒等式 + 分块归位) + 「0 差异同为预期」对称预登记; P2×4 (gate 4 可复制操作 [改为复跑 01 号 + grep 锚, 幂等无副作用] / docstring 插入位置与标号处置写死 [保留原标号, ①-c 注释整段替换文本给全文] / §7-N1 尾巴改条件式 [grep json `${` 先行, =0 自动满足] / gate 1 env 口径原文抄入); NIT×4 (gate 2 容 1 skip 条件 / gate 3 副作用补 46 全套 / N2 落点 scripts/apply_stata_notes.ps1 [46 日志 :1885 实证] / `_assert_neutralized` 措辞消歧) 全落。
  - R1 后待澄清清单复核: 可执行性路 6 项澄清问题逐项已有落点 (3a 备份目的地=scratchpad 基线目录 / 判定树已采纳 / gate 4 操作已给 / docstring 位置已写死 / ①-c 注释全文已给 / skip 容差与 memory 拆分已落)。
- **R2 (对抗复核, okToShip=TRUE, 攻破 5 处全为文档措辞层, 已当即全部落实)**: **核心攻击未攻破** — gate 3 判定树数学被 120,000 条随机 fuzz + 30 定向边界包坐实「两序差异**当且仅当**输入含 `${`, 且形态恰为 `$｛→＄｛`」0 反例 (三向量逐一核死: 字符类 `{` 字面性 / ⑤ marker regex 零交互 / ③①a①b 不制造邻接); 四组行号锚在 26e1b609 盘上态逐一精确 (含「①-c 含注释共 3 行」); §1 表 8/8 sentinel 逐格相等 + rev-list 15 提交 + cap+116.1s + 92.65% 全对; N7 三选一决策框架对根因误判稳健 (选 (a) gate 自定谳且可逆)。攻破并已落实 5 处: ① §0 「工作树硬化」半截残留 → 「提交前工作树版与 26e1b609」; ② §3-N1 「高于工作树漂移」自相指涉 → 「高于 R0 初判…一档」; ③ (must-fix) 3e 判定树补句 — 分块判据仅施于 part 文件 + 「受影响块」定义 + master/manifest 任何字节差直接 FAIL + 主锚改源 json `${`=0 (R2 复测 0, .do 侧计数降为旁证, 段边界跨段盲点被源侧 0 排除); ④ (must-fix) N7 证据链⑤诚实性注 — 07-10 时点设置值系反推非现场取证 + 散热假说反证 (69-70% 恒定不波动) + BIOS/微码通道未逐一排除但决策框架稳健; ⑤ §2 补 df_exploded 1,356=1305+51 预登记行。NIT-b (LEDGER N1 初判正文保留旧世界措辞) 按存档惯例不动, 顶部勘误段已覆盖。
- **R3 (终审签核, ok_to_ship=TRUE「愿为该判定的后果签名」)**: 24 条修订逐条落实核对 **24/24** (含指定重点 5 项: 26e1b609 世界观五处一致零残留 / gate 3 五步齐备含 3e 两补句 / N7 诚实性注 / df_exploded 预登记行 / §0 普查两声明); 3 条承重断言**亲手实跑** 3/3 (test 恰 1 红/39 · json `${`=0 · powercfg AC=0x5f) + 加固性盘上四锚 (26e1b609 恰 1 文件 +18/-1 / 四组行号锚 / 工作树现场核实仅剩 constants / 上轮计划被引锚逐一在场); §8 收口标准 4/4 达标; 内部引用 N1-N9/D1-D4 无缺号重复、跨文件锚全解析; 一票否决排查 0 项 (三呈报决策表述无误导)。唯一 NIT (本轮 D2 与上轮 D2 同名异指) 已当即以「(上轮编号)」限定词落实。**计划层收口: 三轮五路评审全绿 (R1 三路 + R2 对抗 + R3 终审); 批次 A/B 待用户授权执行; N7/N8/N5/N2 四项决策呈报用户。** — 主笔签字回填, 2026-07-15。
- **R4 (用户追加两轮评审之一 · 双路并行: 实施预演「从实施后世界倒推」 / 全文一致性再取证; okToShip = true / true-有条件)**: 已逐条落实全部 13 条 —
  - 一致性路 P2×2 (承重): **P2-1 ⑧ 分段比值「93-96% 逐步同构」失实** — R4 实算 = 105.1%/93.0%/91.4%/95.4% (01 短步反超为启动噪声级), 且原文与 92.65% 数学不相容 → §1 表 + §3-N7 证据① 两处已改写 (N7 结论方向不受影响, 03 段甚至强化); **P2-2 powercfg 回滚命令缺失** → 动作 (a) 已补 (95 原值回滚 + 前后 /query 留痕 + DC 不碰)。NIT×6: N2 行号 :1885→:66 (悬空勘误) / N3·N4 标签统一 [NIT·SOP] / 头注增量账面 536=524+4+2+批次A+26e1b609 / §5-4 listed 01 轮次标注 (上轮 5.6s/本轮 4.8s) / `$｛`/`$｝` 措辞两处 / N7 公允性注 (上轮预登记的裁决试验)。数字全量对账 ≥8 项盘上复核 100% 中 (三 dta 逐字节 / listed 10 dta / tax 端点 / parquet 3 形状 pyarrow 实读 / powercfg / json `${`=0 / N1 红亲跑复现 / D1 数学 1.75×)。
  - 预演路补文本 ×5: §5-1 预期 4 红句 (上轮基线 3 红存档) / N7 三补 (管理员权限 + 中文 locale 判据 0x64 + counter 命令 + ≤35s 机械阈 + §5-gate4 交叉引用) / N2 重放副作用句 (膨胀回 ~66MB + 快照 2 件 + 3 log) / 头注工作树现态更新 (并发 sideproject 3 件, by-name 天然排除) / 新用例 class 点名 TestNotesTextFuzz。批次 B 挂链插入点定位 (上轮 §7 :122/:123 间) + 文本已写死。第四方独立复核四组承重锚全在场 (①-c 三行 / test:66 唯一命中 / json `${`=0 / AC=0x5f); N2 重放通道预演 = apply_stata_notes.ps1 零参自动三 master + 自带对账 + `^r\(` 行首锚扫 (引文子串免疫), 机械判定充分。
  - **R4 新证据改判**: 并发会话当日新增 SIDEPROJECT_LONGDESC ×3 → longdesc 侧线仍活跃 → **N5「已收官可清理」前提被削弱, 改判为侧线收口前维持现状** (已回填 §3-N5; 即使全量授权也按新证据保守执行)。
- **R5 (绝对终局签核, ok_to_implement=TRUE「愿为该签核的后果承担终局责任」)**: R4 修订 **13/13** 逐条盘上核对 (含分段比值数学亲算自洽: 反推上轮四段和 7891.9≈7896.4 残差 0.06%, 92.65% 精确闭环; 批次 B 插入点 :122/:123 亲验精确); §4-§5 实施路径全程走查无卡点 (HEAD/工作树世界观 live 复核 + 全部 file:line 锚亲验 + 新用例双手推); **3 项此前五轮均未复核的承重断言亲手验证 3/3 精确坐实** (21 号日志 :99 `lookups=13,896 hits=13,896 misses=0 hit_rate=1.000` / sidecar mtime 07-14 19:12:09 + benefit 警 0 / apply_stata_notes.ps1 通读: 零参三 master + `^r\(` 行首锚 + exit 0/1 与台账逐点吻合); 静默丢弃终审 = 五轮 38 条 + 1 显式不采纳 (R2 NIT-b, 理由成立) **0 无声消失**; 一票否决 0 项。唯一非阻断 NIT (gate 1 cwd 口径半句) 已当即落实于 §5 头注。**计划终局收口, 全量实施据此启动。** — 2026-07-15。
- **§8-bis 结果评审补记 (实施后两轮, 用户指示)**: **RR1 (实施结果六维: diff 符合度/测试终态/N2 重放终态/git 推送终态/文档自洽/副作用边界) 全 PASS 0 FAIL** — 3786ced5 恰 2 文件逐 hunk 与 §3-N1 五步吻合零夹带; 41/41 实跑绿; 重放对账三锚独立复算; notes .do 11 件哈希与基线全等独立复证; 40/51 parquet mtime 零触碰 (golden-safe 独立证实)。**RR2 (绝对终局, ok_to_close=TRUE 签字)** — 用户委托 8 项全兑现且零美化 (cap 违约/N7「放过」裁定/两次执行失败细节全留痕); 待推送 diff 逐行卫生 (0 secrets/0 U+FFFD); 亲验 5 项终态断言含 2 项 commit 外物理态 (N2 三 dta 字节锚 / N3 memory 落痕); N/D/checklist 全量清点 0 无着落。**预登记 (防下轮误立案)**: ⑦⑧ 的 15 份 dta 已于当晚被并发侧线 8ea92a75 notes 注入重写 (+~68-90KB, 其 commit 自证值哈希 15/15 逐位相等) — 本计划 §0/§1 的 listed/tax dta 字节锚自此为**运行窗历史态快照**, 下轮勿以字节不等立案; N9 的「限频解除后回落」前提句随 N7(b) 失效, 兜底句仍有效。
