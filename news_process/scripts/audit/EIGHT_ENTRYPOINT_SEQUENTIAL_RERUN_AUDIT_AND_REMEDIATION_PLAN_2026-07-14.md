# 八入口顺序真跑复审 — 审计与整改执行计划 (2026-07-14 · 终版 R5 · 五轮七路评审收口, 批次 A/B 已实施, 实施记录见 §7-bis · 三轮结果评审见 §8-bis)

> 日期 2026-07-14 · 环境 OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP=1 / PYTHONIOENCODING=utf-8) · 解释器 F:\Anaconda3\python.exe (conda base 3.13.9) · cwd=news_process\ (⑦⑧=各自子目录) · 每入口 2h cap。
>
> 本轮 = 2026-07-10 八入口审计 (`EIGHT_ENTRYPOINT_SEQUENTIAL_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-10.md`, 下称「上轮计划」) 之后, 跨 27 个提交 (f441478a..c306a424: fatal-audit F1-F8 / 致命再审计 6 修 / prompt-audit 批次 A-F+V9-PRE-1 / codebook WP4 基建) 的**首次全谱复跑**。审计方法 = 1 路静态数据流预审 (27 提交 × 8 入口路径影响矩阵) + 4 路分入口日志深审 (逐条对 F/G 台账与 §2 白名单对账, 每项给 file:line 锚) + 主笔逐条亲核承重发现 + 三路计划评审 (完整性/技术正确性/可执行性, 首轮均 okToShip=false, 修订记录见 §8)。
>
> **修订 R1**: 已吸收三路首轮评审全部 17 条。承重修正: §0/H1 吞吐数字**跨口径拼接错误反更正** (2.735 MB/s 是 03 步级墙钟吞吐 [含计算+IO] 非 branch_county 纯写盘 [实为 ≈7.35 MB/s]; 「×8 衰减」系两个不可比口径相除, 删除 — 同口径衰减 = 步级 7.7→2.735 ≈ ×2.8 / 纯写盘 30→7.35 ≈ ×4.1, 与四步均匀 ×2.8–3.4 同构等比, 争用叙事反而更自洽); 「数值零影响铁证」降格为「schema/行列/定宽体量零漂移铁证」(dta 定宽字节数不感知值漂移, 勿引作逐值相等证据); parquet 微漂归因降格为候选; ⑦⑧ 窗内争用源归因如实化 (含本审计自身活动); H2 修法写死 A 案落点 + 「勿照搬模块级 setup_logging」暗坑警示; H2 gate 镜像半句拆解 (单跑 shim 无编排器不可验); 批次 A 「2 源文件」笔误更正为 3; gate 命令/前置/副作用补全; DEFERRED 补 F1(a); §8 补收口标准; 定级标尺统一回四级 (H2→P2, H3→NIT); D1/D2 行号微调 (302-316 / :426 / 584-609 / 610-630)。
>
> ⚠ 本计划所引日志行号 = 2026-07-14 运行快照; 后续重跑行号会漂移, 勿以行号漂移立案。证据全量归档于会话 scratchpad `audit_2026-07-14\` (console/sentinels/post_logs/snapshots 四目录 + pre/post 产物快照 934/941 行); 正文标注「快照佐证」的数字以 scratchpad 归档为出处, 盘上不可复核。

## 0. 结论速览

- **8/8 成功 (①退出码见 §1 脚注) · 0 真 ERROR · 0 Traceback · $0** (stage21 离线 13,896/13,896 全命中; 嵌入/BERT 全离线; 80 复跑锚点嵌入全缓存)。
- **golden 全谱零漂移**: 面板 220×3442 / article 1005×1305 / 51: 220×3453 与上轮逐项相等 (pyarrow 实读); listed 10 dta 字节锚 10/10 全等 (主 1,610,634,683 / 7 权各 1,603,484,161 / frozenw 1,606,426,983 / mainbankw 1,617,142,173); tax 5 dta 字节判等 (6,845,811,481–6,898,645,113 B, 与上轮 6.85–6.90GB 口径逐一同); 双 registry 锚 023cdc9158ec52ba / 4f580e3f 复算未变; tax 五面板 447,710 行不变量全绿; 81 审计 158/138/20/0 与上轮**逐位相同**; 82 漏斗 9,490→5,031→1,650→1,005 复现。
- **上轮整改全谱 live 生效** (11 项实证, 见 §2-ter): G1/G2a/G3/G4/G8+RR6/G11/F12/N2-P1/M3/V9-PRE-1/S3。其中 G2a 陈旧哨兵在 ⑦⑧ 各实弹触发 1 次且指纹核符 (benefit=07-03 旧代 d66f929b36eae28a, 双管道逐字一致) — §2 预登记的「应当出现」兑现。
- **慢化 = 宿主 IO/CPU 争用伪回归** (G13 同构判例三连): ①=2875.8s(上轮2313.7) / ⑦=2950.6s(1880) / ⑧=7896.4s(2636.6, ×3.0)。证据链: 慢化集中于既知重段且 I/O 段与 CPU 段等比放大 (⑧ 四步 ×3.04/3.36/2.83/3.31; ⑧ 步骤03 整体落盘吞吐 2.735 MB/s [`run_pipeline.log:76`, 13,460MB/4922s 墙钟口径含计算+IO; 上轮同口径 ≈7.7 MB/s (推算值: 本轮落盘量按 dta 字节锚判等代入上轮墙钟 1740s; 上轮日志已覆盖无法回核, 见 R3), ×2.8], branch_county dta 纯写盘 931.6s ≈ 7.35 MB/s [6,847,602,963 B; 07-08 speedup 计划基线 county 215.9s @ 30 MB/s, ×4.1] — 两口径衰减比与四步均匀放大同构等比) / 产物字节·行列锚全等 (schema/行列/定宽体量零漂移铁证; 数值层面除既判 run-dependent 的 BLAS-FP 网络列族及其 company 加权衍生列 [cw_/ce_*] 外无漂移证据 — dta 定宽字节数不感知值漂移, 勿引作逐值相等证据) / 慢段代码本区间零改动 / 争用源: ① 窗内实锤 (并发 codebook 会话 19:10 重生 ~100MB 产物并 19:11 提交, 恰落 stage 40 LDA 窗 18:56–19:12), ⑧ **步骤 02 段**实锤 (本审计 ⑦ 深审代理 20:26–20:40 对 ~15GB listed 产物流式 sha/实读, 覆盖步骤 02 [20:25–20:42] 的 14/17.7min, ~18 MB/s 持续读同盘), ⑧ 步骤 01/03/04 段与 ⑦ 全窗争用源未完全定位 (候选=并发会话工作树活动/盘缓存后效) — 产物零影响结论**不依赖**争用归因完备性, §7 独占复测为裁决试验。
- **⑧ 突破 2h cap** (7896.4s = 2h11m36s): 唯一 cap 违约, 四步均匀 ×2.8–3.4 争用放大所致; 进程健康推进无挂死, 审计裁定放行跑完 (杀写盘中的 6.9GB dta 风险 > cap 严格执行收益), cap 违约本身立案为 H1。
- **本轮定级: P0=0 · P1=1 (H1, 运行治理非代码缺陷) · P2=1 (H2) · NIT=2 (H3, H4) · 销案=3 (D1-D3) · 记录=3 (R1-R3)**。全部非阻断; 代码修仅 H2/H3 两处纯日志 golden-safe (+D1 可选注)。
- 静态预审吸收声明: 预审产出 = 27 提交影响矩阵 (逐文件定级, 结论「零新增无条件红灯」) + Top5 条件性预测。矩阵内全部条件性项经真跑证实**不触发** (F1 多源 cast / WP-A4 空表闸 / S10 `_lg` 穿透 / WP-A1 观测闸 / N2 硬拦臂); Top5 去向: Top1 (61 N2 硬拦) 未触发且放行语义 live 验证, 其汇总文案矛盾坐实为 **H3**; Top2 (benefit S10 miss 穿透) 未触发 (六轨 npy+sidecar 在盘, S3 迁移落盘自愈, 收 D2); Top3 (stage21 缓存缺口) 未触发 (13,896 全命中, 21 号双 parquet 首次带版本戳, 收 §2-ter); Top4 (dta 字节漂移误报) 部分兑现 — dta 字节数**未**变, parquet 微漂坐实并给归因候选 (§2-bis); Top5 (encode_collab sidecar 双副本) 跑前排雷确认单副本, 未触发。**无预测被静默丢弃。**

## 1. 运行结果总览

| # | 入口 | 结果 | 墙钟 | 上轮 | 关键证据 |
|---|------|------|------|------|---------|
| ① | run_pipeline_function | ✅ 0* | 2875.8s | 2313.7s | 16/16 ✓; stage21 离线 13,896/13,896; 面板 220×3442; 21 号双 parquet 首次带 `news_process.prompt_version='v8-2026-05-17'` 戳 (V9-PRE-1); benefit sidecar S3 迁移落盘 (D2) |
| ② | run_pipeline_validation | ✅ 0 | 691.2s | 635.8s | 16/16 ✓; 61 N2-P1 旗标放行 live; 66/70 离线优雅跳过 (F6/F10 同形); 72/75 产物重生; G5 κ 四值级复现 (0.7794/0.8525/0.8149/0.8663, 快照佐证) |
| ③ | run_paper (裸跑) | ✅ 0 | 0.9s | 0.8s | 11/11 篇总览 0 render 失败; 本轮段 0 ERROR/WARNING |
| ④ | 80_placebo_and_alt_anchor | ✅ 0 | 1.7s | 1.6s | 143×29; sidecar schema_version=1.2 + upstream_snapshot 五键 (G3 live); G14 同 5 条安慰剂复现 |
| ⑤ | 81_stata_data_audit | ✅ 0 | 2.6s | 2.6s | 158 项: PASS=138/WARN=20/FAIL=0 **逐位同上轮**; 恒等式族 46 项全绿; G1 修后 shim 退出码可信 |
| ⑥ | 82_export_stats_excel | ✅ 0 | 1.0s | 1.0s | 4 阶段 × 12 sheet; 漏斗 9,490→5,031→1,650→1,005 复现 |
| ⑦ | company_listed_bank | ✅ 0 | 2950.6s | 1880s | 01=5.6/02=263.8/03=2182/04=494.6; 锚 023cdc91 未变; 10 dta 字节锚 10/10 全等; G2a 哨兵实弹 ×1 (预期); 04 磨损三段断言全绿 |
| ⑧ | company_tax_bank | ✅ 0 ⚠cap | 7896.4s | 2636.6s | 01=58.4/02=1061/03=4922/04=1852 (×3.04/3.36/2.83/3.31); 锚 4f580e3f 未变; 5 dta 字节判等; 五面板 447,710 全绿; 建碁 67.9% (668/984) 同值同形 (G12) |

\* ① 的驱动 sentinel `EXIT=` 为空 (H4 驱动层缺陷, 当轮即修), 成功判定以编排器日志「✓ 管道全部阶段执行成功」+ 16/16 阶段摘要 + 产物实读三重自证; ②-⑧ 的 EXIT 均为驱动修复后可信值。

## 2. 白名单对账 (上轮已裁定项, 本轮全谱同形复现 [W1-W7 与验证侧各簇均值级对上], 不再立案)

- **T=2 退化全谱**: DiD 全 0 ×2 / Bartik 弱 IV·share one-hot / 零方差常量 (depins_post, brokerage_fire_sale) / BERT `nt_iyvol/iytrend` NaN / `_std` 族高缺失 66.82–70.00% (609 个) / 零新闻 bank-year 35.00% / 62 输入 10,076 行 / 67 时间稳定性 <3 年 / stage13 掉 9 家 (151→142) / 变量名 33 字符 ×3 / 建碁 67.9% (668/984, 值级同上轮; §7 L1 硬义务维持) / mainbankw tie 率 28.47% (⑦ `04:153`) / 双管道 40 加权列全 NaN (F3 文案版)。
- **by-design 既有披露**: 跨目录同名副本去重 ×1 / jieba 边界词 6/1506 / csdid never-treated→notyet / 63 demo_mode / DiD HQ-based 假设 / msent_score 反向口径 / 61 抽样媒体单类 100% (33/34 复测义务维持) / benefit 负极句 #3 投影 0.1416 (G7) / listed+tax 01 豁免注册 ×4 + 3 基名 emit_tracks=[] (G8 修后文案 live) / 03 反向证据三件套对称披露 / F14 覆盖率非单调 (Δα 三值级复现, 同行号 176/376/576)。
- **G2a 哨兵 WARNING ×1/管道** (⑦ `02_….log:140` / ⑧ `02_….log:142`): §2 预登记「应当出现, 本身即免费实弹验证」兑现 — benefit 条目 sha256_16=d66f929b36eae28a / mtime=07-03 03:32 双管道逐字一致且盘上重算核符, 哨兵**准确非误报**; 三参数重生命令 (`--track all --include-lg --df-exploded`) 完整落痕。27 号同步重生义务照旧挂 §7-G2 (生产 checklist), 本轮 dev 态刻意不重生 (重生会自毁「27 陈旧」盘上事实且 dev 无消费需求)。
- **81 的 20 WARN**: 与上轮 §2-bis 归类表逐条同构且数值级复现 (66.82/68.18/70.00% 高缺失三值 / ctx 10.49% / ss 7.692% / LOO-IV r=0.03020 / dict_avg 1 obs>5σ / 116 中文列名 / Nullable 3330/3341); 新增=0, 消失=0。

### §2-bis · 本轮「预期形态变化」对账 (变化≠缺陷, 逐条归因)

| 变化 | 归因 | 判定 |
|---|---|---|
| 21 号双 parquet 新增 `news_process.prompt_version` schema metadata 键 | V9-PRE-1 (18d2619d) 写侧版本戳, 重放后首次落戳 | ✓ 预期; 下轮起 grandfather WARNING 通道永久关闭 |
| `_benefit_center_sidecar.json` 六条目新增 anchor_sha256/text_pipeline_version 字段 (mtime 2026-07-14 19:12:09) | S3 (1fea954d, 07-14 12:58 入库) 迁移回填**落盘** (center 值零改动, 日志逐值核符) | ✓ 一次性自愈; 见 D2 验证义务 |
| 11 份 listed 面板 parquet 字节微漂 ±14…357 B / 5 份 tax 面板 parquet ±16…2,802 B (快照佐证) | **归因候选** = 上游 40/51 BLAS-FP 9 网络列族及其 company 面板 cw_/ce_ 加权衍生列浮点微漂 → parquet 压缩页字节变, 与 F17 run-dependent 字节并列; 未做列级 diff 定位 | ✓ 先例同族; 行列锚全等排除结构漂移 |
| 75_cross_media_alpha mtime (19:29) > 21_full (18:45) | ② 重生 75 号 | ⚠ **G9 振荡已上膛** (R1): 下轮单独重跑 stage 40 必 +9 列 (3442→3451); A/B 差分 SOP = 先核 `cross_media_alpha_full` 在场性 |
| 46 导出三 master notes .do + apply_notes_manifest.json 重生 (n_cols_total=3453, 7 子卷, skipped_empty=0) | codebook WP4 基建 (2da33939) + 并发会话 19:10 重生 variable_codebook.json | ✓ fail-soft 消费成功; dta 3442/3442 列中文标签 round-trip 实读核符 (快照佐证)。⚠ 口径注: **3453 = 51 面板全集口径** (variable_codebook.md 头部「220×3453」同源), 46_full dta = 3442, 差 11 列 = 51 独有 (controls 族), notes 机制对 46_full 缺席列按子卷生成时的列集口径自然跳过 — 两数并排 by-design, 勿立案 |

### §2-ter · 上轮整改 live 生效实证 (11 项, 均给锚)

G1 (81/82 shim `sys.exit(main())`, ⑤⑥ EXIT 可信) · G2a (⑦⑧ 五键快照逐字段与盘上 size/mtime_ns/sha256_16 相等) · G3 (80 sidecar v1.2 + upstream_snapshot 五键) · G4 (47 号 0 原生 RuntimeWarning + `47_….log:74`「配对子集样本不足/零方差, 跳过」新 INFO) · G8+RR6 (双 01 新文案「默认不产列 emit_tracks=[]…DEFERRED 例外」live) · G11 (⑦ 28 条 / ⑧ 15 条产物清单精确字节行与 ls 逐一相等) · F12 (`│⚠` stderr 镜像 ① 40/40 逐条一致, 快照佐证) · N2-P1 (61 旗标在位+零标注→警告放行, 未硬拦) · M3 (61/64 盲表 target_bank+机器输入文本 9/9 列就绪, coding_note 构念文案) · V9-PRE-1 (grandfather 零行为变化 + 重放后落戳) · S3 (sidecar 迁移落盘, center 零改动)。

## 3. 新问题台账 (H 系, 承接 G 系; 每条已主笔亲核或双源坐实)

### H1 · [P1 · 运行治理 · 非代码缺陷] ⑧ 突破 2h cap: 宿主 IO 争用下 tax 管道墙钟不可预算
- **证据**: ⑧ 总 7896.4s (cap 7200s, 超 ~11.6min); 四步均匀 ×3.04/3.36/2.83/3.31 (01=58.4/19.2, 02=1061/316.2, 03=4922/1740, 04=1852/559.1); 03 内 branch_county dta 纯写盘 931.6s ≈ 7.35 MB/s (6,847,602,963 B; 07-08 speedup 计划基线 county 215.9s @ 30 MB/s, ×4.1 衰减); 步骤 03 整体落盘吞吐 2.735 MB/s (`run_pipeline.log:76`, 13,460MB/4922s 含计算+IO; 上轮同口径 ≈7.7 MB/s, ×2.8); 04 frozenw/mainbankw 落盘 944.3s/823.3s。争用源: ⑧ 步骤 02 段实锤 = 本审计 ⑦ 深审代理 (20:26–20:40) 对 ~15GB listed 产物流式 sha/实读; 步骤 01/03/04 段未定位 (候选=并发会话工作树活动/盘缓存后效)。产物侧零结构影响 (5 dta 字节判等 / 五面板 447,710 全绿 / 锁链全闭合)。
- **影响 (白话)**: 管道本身没病, 但同一台机器上多件事并行时, 要写 34.5GB+14GB 的 tax 管道墙钟会不可控地放大 3 倍, 任何固定时长 cap 都会被击穿。本轮若严格 kill 在 7200s, 会把写到一半的 6.9GB dta 留在盘上 (03 altweights 长表非原子 = 上轮计划 :165 已记 follow-up), 损失 > 收益。
- **动作 (零代码)**: ① 生产 T=18 排期铁律 = **独占时段跑双 company 管道** (入 §7, 升硬义务); ② cap 语义决策挂用户: 建议改为「per-步骤预算 ×3 争用系数 + 健康推进 (日志 5min 内有新行) 则放行, 挂死才 kill」— 本轮按此裁量执行并全程留痕 (§6.1 自认未获授权); ③ 后续同类审计跑 ⑧ 前先确认无并发重负载, 且审计自身的重 IO 动作 (产物哈希/实读) 与被审管道运行窗**错峰**。
- **gate**: 无 (治理项)。§7 新增两项。

### H2 · [P2 · 可观测性 · NEEDS_FIX] stage 46 模块 logger 未挂 stage 文件 handler — 证据链日志静默丢失
- **证据**: `pipeline/panel/stata_export.py:81` `logger = logging.getLogger(__name__)`; `main()` (:2119-2120) 另建 `setup_logging('46_stata_export', …)` 的 stage logger (`core/logging.py:224-277` 同名单例挂 file/console handler, propagate=False), 两 logger 名不同、无父子关系, 模块 logger 记录冒泡到 root (无 handler) 即丢 (lastResort 仅 ≥WARNING 到 stderr) → 「Full .dta 已写入」(:1832)/「notes .do 族」(:1861)/⑦⑧⑨计时行 (:1884) **既不落 stage log 也不进编排器镜像** (`46_stata_export.log:50→51` 19:13:24 直跳 19:13:41 中段零行)。40-path (`encode.py:47-48` 模块级 setup_logging 共享) / 51-path 的同类行正常在档。本轮 46 号实际工作完整 (apply_notes_manifest.json + dta 3442 列中文标签 round-trip 实读自证), 纯观测缺口。
- **影响 (白话)**: stage 46 干了什么只能翻盘上产物倒推, 日志审计对它是盲区; 若未来 46 号出错, 第一现场缺失。
- **修法 (A 案, 3 行 diff)**: `STAGE_NAME = '46_stata_export'` 提升为模块级常量 (置 :81 附近), :81 改 `logger = logging.getLogger(STAGE_NAME)`, main() :2119 局部定义改用模块级常量。机理 = getLogger 按名单例, main() 的 setup_logging 配置的就是同一对象, 模块内全部 `logger.*` 即刻入档; 46-path 之外的行为**等价性** (R2 补全论证): 消费路径共三条 — 40/51-path (`export.py::_apply_label_fallback` 等 import 复用 `build_variable_labels`) + ③ run_paper (`papers/_common/tables.py:80-83` lazy-import 列名工具) — 新旧 logger 名均为「自身无 handler、无被配置的祖先」直接冒泡 root (全仓 24 处 basicConfig 均在 `__main__`/入口③/独立脚本, runner/encode/orchestrator 子进程零 basicConfig, 亦无 `news_process.*` 祖先 logger 被配置), 改名前后仅 `%(name)s` 变 — 40/51 子进程照旧丢弃, ③ 进程 (root 有 basicConfig handler) 改名前后同样打印, 行为逐路径不变。⚠ **R4 证伪并修正**: 「tests/ 无按旧 logger 名捕获的 caplog 断言」原断言**不成立** — `tests/test_stata_export.py:399-400` 与 `tests/test_omni_fix_stata_export.py:41,363` 按旧名 `news_process.pipeline.panel.stata_export` 捕获; A 案改名后 INFO 路必红 (pytest 无 log_level 配置 → root=WARNING → 发射端压掉 INFO → caplog 空)。**甲案修法 (随批次 A 双测试同改)**: 两处 logger 名改 rename-proof 的 `se.logger.name`; 另 `test_stata_export.py:513` 端到端 `se.main()` 会把 stage handler 持久挂上模块 logger (propagate=False, 会话内污染后续 caplog) — 用例尾补 `se.logger.handlers.clear(); se.logger.propagate = True` 恢复 (P2, 当前无排后消费者不现红, 防埋雷)。备选 B 案 = main() 内 `global logger; logger = log` 仅 46 进程改绑。⚠ **勿照搬 encode.py 式模块级 setup_logging**: build_variable_labels 被 40/51-path import 复用, 模块级挂接会在 40/51 运行中首条日志即截断并污染 `logs/46_stata_export.log` (delay=True + truncate-on-first-open)。纯日志, golden 零风险。
- **gate**: 单跑 46 号 shim (命令见 §5-1) → `logs/46_stata_export.log` 同时出现「Full .dta 已写入」+「notes .do 族:」+「⏱ 阶段计时」三锚 = 绿; 编排器镜像不在本 gate (单跑无编排器) — 机制自证 (stage logger 的 console handler 写 stdout, 被 ① 的 PIPE 捕获即必然入镜像, `core/logging.py:262-268` 结构性保证) + 挂 §5-3 跨轮义务 (下轮任意 ① 复跑顺带 grep 镜像)。

### H3 · [NIT · 日志措辞 · NEEDS_FIX] 61 号 N2 汇总 INFO 与同轮 WARNING 事实矛盾
- **证据**: `validation/llms_human.py:485-487` else 分支汇总「N2: blind_A/B 均无既有非空标注**且无'标注进行中'旗标 (或此前不存在)**, 正常生成」— 但 N2-P1 (2fcc56e1) 降格后「旗标单独在位」也走到该分支, 本轮旗标实际在盘且同轮已发 2 条「检测到'已发放'旗标…按确定性重生放行」WARNING (`61_….log:42,44`; 汇总矛盾行 :47; 旗标写盘后重建, mtime 与盲表同秒)。字面陈述与事实矛盾, 属措辞未随 N2-P1 同步的双副本漂移 (代码注释 :474-479 自证意图=「未被拦截」)。
- **修法**: 汇总行改为「blind_A/B 无既有非空标注, 未被 N2 拦截 (旗标单独在位者已按确定性放行并另行警告), 正常生成」。1 行字符串, golden-safe。
- **gate**: 已 grep 证实无任何既有测试断言旧文案 (唯一命中 test_60_threshold.py:350 为无关 docstring) → 既有 N2 测试族不动承诺成立; 防回漂 = `tests/test_n2_blind_overwrite_guard.py` 追加 1 条 **source-lock 断言** (读 llms_human.py 源文本含新文案关键短语「未被 N2 拦截」且不含旧短语「且无'标注进行中'旗标」— 镜像 test_pipeline_shims 文本断言先例; ⚠ R2 定谳: 勿用 caplog 断言 — 汇总 INFO 在 `main()` (:337 起) 内, :76 用例只直调 `_write_blind_workbook`, caplog 断言必红); 单跑 61 号 grep 新文案落痕 (前提=当前零标注/人工窗口未开, 窗口开启后此单跑 gate 禁用)。

### H4 · [NIT · 审计 SOP · 不入 repo] 驱动层 ExitCode 陷阱 (本会话自身教训, 记录防再犯)
- PowerShell `Start-Process -PassThru` 后不先取 `$p.Handle` 就 `WaitForExit()`, 则 `ExitCode` 为空 — 入口① sentinel `EXIT=` 空实弹; 当轮已修 (`$null = $p.Handle`), ②-⑧ 退出码全部可信。后续审计驱动脚本沿用修正版模板。

### 销案裁定 (D 系, 查过非缺陷, 防后人再立案)

- **D1 · 3441 vs 3442**: `pipeline/panel/export.py:426` 调 `_materialize_low_conf_flag` (:302-316) 在 REQUIRED 校验 (:411-422) 后无条件物化 `low_conf_flag`, 原地变异同对象 → `runner.py:2721` (导出前) 计 3,441, `:2809` (`log_stage_summary`, 导出后) 计 3442。by-design schema 稳定设计 (fix omni-g-panel-export-05)。可选 NIT (随批次 A 顺手落): :2721 行文案追加「(导出前计数, 不含导出期无条件物化的 low_conf_flag — 阶段摘要处 +1 为 by-design, 见 export._materialize_low_conf_flag)」。
- **D2 · benefit sidecar 回填 6 警 = 一次性迁移, 已落盘自愈**: `pipeline/features/benefit_society.py:610-630` warning (:621-625) + 原地补字段 + json.dump 重写 (:627-628; center 绝不改, 三字段 [model_id/anchor_sha256/text_pipeline_version] 双方在场且不匹配才 fail-loud, :584-609)。盘上定谳: sidecar mtime=2026-07-14 19:12:09, 6 条目字段齐, center 与日志逐值吻合。「今早 10:30 也警过」= S3 代码 12:58 才入库, 10:30 跑的是旧代码。**验证义务 (入 §5-3)**: 下轮主管道复跑此 6 警应归零, 再现则立案查覆写者。⚠ 附带残余 (R2): 回填写盘**非原子** (直接 open('w')+json.dump, 无 temp+rename), 且损坏 sidecar 走 :576-578 JSONDecodeError 捕获后「按首跑重建」— 冻结守卫在损坏场景静默失效并重冻结; 销案不受影响 (本轮三重验证在案), 原子写并入 §4 DEFERRED R2 根治族。
- **D3 · 慢化三连 (①⑦⑧)**: 争用伪回归, 证据链见 §0 (吞吐同口径对比 + 等比放大 + 行列/字节锚 + 代码零改动); 争用归因部分未定位不影响结论 (产物锚独立成立); 不解除 §7 既有 LDA 压测义务 (G13)。

### 记录 (R 系)

- **R1 · G9 振荡已上膛**: 见 §2-bis 表; 下轮 A/B 差分前必核 `cross_media_alpha_full` 列在场性。
- **R2 · 共享树并发竞态实录 (本轮无害, 生产有害)**: 并发 codebook 会话在 ① 运行中 (19:10) 重生 `build/codebook/variable_codebook.{json,md}` (56.8+56.6MB) 并提交 (HEAD c306a424→1bc3e5e4, 19:11); ① 的 stage 46 (19:13) 消费了该 19:10 新生 json — 本轮内容完整 (3453 条) 故无害, 但「46 号读取窗与并发重生窗重叠」的竞态真实存在。若并发写到一半被 46 读到, fail-soft 会退化为无 notes 导出 (静默降级)。动作: 入 §7 — 生产跑主管道时禁止并发重生 codebook json; 根治候选 (json 原子写 + 46 侧完整性校验) 挂后批; 上轮 §6-6 共享树约定继续有效。
- **R3 · 07-10 原始日志已被后续会话覆盖**: 跨轮对比一律以上轮计划文档记录数字为锚 (本轮已如此执行); 「gate 复跑前先归档日志」教训 (上轮 RR2) 本轮已内化为跑前归档 SOP (pre_logs_archive)。

## 4. 修复批次 (按独立提交, 全部先过 gate 再 commit; by-name stage, 排除并发产物)

- **批次 A (纯日志 golden-safe 小修, 1 commit; 3 源文件 + 3 测试, R4 后共 6 文件)**: `pipeline/panel/stata_export.py` (H2, A 案 3 行) · `validation/llms_human.py` (H3 措辞 1 行) · `pipeline/panel/runner.py` (D1 可选注 :2721) · `tests/test_n2_blind_overwrite_guard.py` (H3 source-lock 断言 +1, 模块级, `inspect.getsource(llms_human)` 取源 — :25 已 import, :216-222 有 inspect 先例; 断言双向干净: 新短语「未被 N2 拦截」现 0 命中, 旧短语「且无'标注进行中'旗标」唯一命中 :486 即被改行) · `tests/test_stata_export.py` (R4 甲案: :400 logger 名改 `se.logger.name` + :513 用例尾 logger 状态恢复) · `tests/test_omni_fix_stata_export.py` (R4 甲案: :41 `_LOGGER_NAME` 改 `se.logger.name`)。零数据值影响; 双 registry 锚不 bump; 面板列哈希 0 相异预期。⚠ 共享树并发: 提交前 `git diff --stat` 核对无他人 hunk; by-name 恰 6 文件。预算: 编辑 30-45min + gate <15min (无隐藏长跑)。
- **批次 B (文档/台账, 1 commit)**: 本计划 md 终稿 (§8 评审记录回填) · 上轮计划 §7 checklist 增量同步 (H1 独占时段 + R2 codebook 竞态; 以引用本计划为准, 不改写上轮正文)。
- **DEFERRED (维持/新增, 逐项点名防断链)**: G2(b) 硬锁层 (M0) · G6(b) 81 扩检 46_full · G10 census from-summary · 清理批 (t2v 孤儿 + 弃用工作台 ×4) · F1(a) 税调匹配层过滤 (维持上轮 DEFERRED 原状) · **H1-cap 语义决策 (挂用户)** · R2 根治族 (codebook json 原子写+46 侧校验 + benefit sidecar 原子写 [D2 附带], 后批) — 全部不越界。
- **刻意不做**: 慢化性能修 (争用非代码病) · sidecar 警告抑制 (D2 自愈型, 下轮自然归零) · G2a 哨兵在 dev 的消音 (预登记形态, 消音反而自毁实弹验证通道)。

## 5. 验证 gate (每批次)

1. **批次 A** (全部命令 cwd=`F:\WiseSearch\data_antigravity_project\news_process`, 解释器 `F:\Anaconda3\python.exe`, env 沿用本计划头 OFFLINE 全套):
   - `pytest -m fast` 以 baseline-stash A/B 差分证 **0 新增失败** (committed golden 本就陈旧, 绝对红灯数非判据);
   - H2: 前置断言 `data/processed/40_panel_yearly.parquet` **与** `build/codebook/variable_codebook.json` 均在盘 (json 缺席时 :1864 走「notes .do 生成跳过」优雅分支, gate 会误红) → 单跑 `F:\Anaconda3\python.exe 46_stata_export.py` (~21.2s, 争用下 ≤2min) → grep 三锚 (「Full .dta 已写入」/「notes .do 族:」/「⏱ 阶段计时」)。⚠ R4-P2-2 竞态防护: 并发 codebook 会话今晚仍在重生该 json (23:29 实测) — 单跑 46 **前后各取一次** json 的 (size, mtime_ns), 不一致则该次 gate 作废重跑 (fail-soft 撞半写 json 会假红)。副作用披露: 重写 `46_panel_yearly_full.dta` (format-118 头部时戳字节必变 — 46 产物本就不在字节锚清单, 可接受)。追加 gate (R4, **口径经 R5 更正**): 旧 logger 名 `news_process.pipeline.panel.stata_export` 的 **logger-语境 0 残留** — 仅指 caplog `logger=` kwarg 与 `_LOGGER_NAME = '...'` 字符串赋值两形态; 该字符串同时是模块 import 路径 (全仓合法命中 ~50 处: shim import/tables.py/controls.py/export.py/生成物 header), 按字面全仓 grep 必假红, 勿误"修" import;
   - H3: 单跑 `F:\Anaconda3\python.exe 61_news_llms_human.py` → grep 新文案; 新增 **source-lock 断言**绿 (R3 更正: 勿写 caplog 断言, §3-H3 gate 已定谳必红)。副作用披露: 重写盲表 A/B+旗标 (前提=零标注态, 人工窗口开启后此单跑 gate 禁用);
   - 双锚 sanity (批次 A 不触 listed/tax 代码, 廉价保险): 各管道 01 号 SSOT `registry_content_sha256` 复算 == 023cdc91… / 4f580e3f… (秒级; 字面命令形如 `F:\Anaconda3\python.exe -c "import importlib.util as u; ..."` 按各管道 01 内 SSOT 函数调用, 先例见上轮计划 §5-2)。
2. **批次 B**: 纯文档, 断链/ruff 无红。
3. **跨轮验证义务 (下轮任意主管道复跑时顺带)**: D2 sidecar 6 警归零; V9-PRE-1 grandfather WARNING 不再出现 (parquet 已带戳); G9 按 SOP 核列在场性; H2 编排器镜像 grep「notes .do 族」确认镜像通路。⚠ **预登记 (R2)**: H2 落地后下轮 ① 的镜像行数与 F12 `│⚠` 对账形态**必然漂移** (46 模块级 INFO 新进 stdout 镜像; 模块级 WARNING 从 lastResort-stderr 迁往 stage log + 双流 console) — 属预期形态变化, 勿立案。
4. **全局**: 全程 OFFLINE $0; 不触碰并发会话的 codebook_longdesc 工作区。

## 6. 残余风险

1. **H1 cap 语义未决**: 本轮「健康推进则放行」是审计裁量, 非用户授权的常设规则; 生产排期前须用户定夺 (kill-at-cap vs 预算×争用系数)。
2. **R2 竞态窗**: 46 号 fail-soft 读并发半写 json → 静默无 notes 导出; 本批不加锁 (跨会话文件锁超出本批范围), 靠 §7 排期纪律缓解; 根治候选挂后批 (§4 DEFERRED)。
3. **G2 记录层已修 ≠ 混代根治** (上轮 RR2/RR5 提醒继续有效): 27 号在盘仍是 07-03 旧代, benefit 48 列/管道取值属旧代 — dev 无害, 生产 T=18 必须按 §7-G2 三参数命令同步重生。
4. 本机争用不可控: 后续 A/B 计时对比一律以分段计时结构为准 (本轮三连判例再次坐实); 审计自身重 IO 动作与被审管道错峰 (H1 动作③)。
5. 本计划评审期间并发会话可能继续推进 HEAD / 重生产物; 计划内全部锚以 2026-07-14 18:26–22:36 运行窗快照为准。

## 7. 生产 T=18 checklist (本轮增量, 与上轮 §7 十一项并存且全部继续有效)

- [ ] **H1**: 双 company 管道生产跑 = 独占时段硬义务; 排期预算 = 上轮分段计时 × 3 争用系数上限; 独占复测吞吐口径注明 = **步级落盘吞吐** (run_pipeline.log「MB/s」行, 含计算+IO) 与 **单文件纯写盘吞吐** (字节/dta 写盘秒) 双报 — 独占下步级仍 <5 MB/s 或纯写盘仍 <15 MB/s 则查盘硬件。
- [ ] **H1-cap**: 与用户定夺生产 cap 语义 (kill-at-cap vs 健康推进放行)。
- [ ] **R2**: 主管道运行窗内禁止并发重生 `build/codebook/variable_codebook.json`; 或落地原子写+46 侧校验后解除。
- [ ] **D2**: 下轮主管道复跑核 sidecar 6 警归零 (再现则立案)。
- [ ] (承接上轮 §7 十一项全部有效, 特别 G2 三参数重生 27 号 / G12 建碁 longhit 臂 / G13 LDA 压测 / 离线冷缓存前置。)

## 7-bis. 实施记录 (2026-07-15 凌晨, 用户完全授权后)

- **批次 A (commit 28716f93; 3 源 + 3 测试恰 6 文件 by-name)**: H2 A 案 (STAGE_NAME 模块常量 + :81 改名 + main() 复用 + 双测试 `se.logger.name` + :513 尾 logger 裸态恢复) · H3 (汇总文案 1 行 + source-lock 断言) · D1 (:2721 导出前计数注)。
- **gate 全绿**: 基线先行 `pytest -m fast` A/B 差分 **0 新增失败** (3 既有红 [benefit cohort ×2 + jieba isolation ×1] 逐条同基线) / 定向 3 测试文件 68 项全绿 / ruff 6 文件全绿 / 单跑 46 EXIT=0 21.11s **三锚全部落档** (修复前 :50→51 静默断档段现已有证据链行) + codebook json (size,mtime_ns) 前后一致 (竞态防护首用即绿) / 单跑 61 EXIT=0 新文案 live 且与 WARNING 语义一致 / 旧 logger 名 logger-语境 0 残留 / 双锚复算 023cdc9158ec52ba / 4f580e3fc458be0c 与 registry meta 相符。
- **副作用 (已披露口径内)**: 46_panel_yearly_full.dta 重写 (46 产物不在字节锚清单) / 61 盲表+旗标重生 (零标注态前提成立)。
- **批次 B (本 commit)**: 本计划终稿 (R5 记录 + §5-1 gate 口径更正回填) · 上轮计划 §7 增量两项 (H1 独占时段 / R2 codebook 竞态, 引用本计划)。

## 8. 评审记录 (逐轮回填; 收口标准 = ≥3 轮独立评审且末轮 0 未决 P0/P1 [治理项以显式 DEFER 视同已决], 全部 NEEDS_FIX 有 file:line 落点或显式 DEFER, §5 gate 逐条可机械执行, 终判 ok_to_ship 由主笔签字回填本节)

- **R0**: 主笔初稿。
- **R1 (三路: 完整性 / 技术正确性·证据回落 / 可执行性·gate 可写性; 三路首轮均 okToShip=false)**: 已逐条落实 17 条 —
  - 完整性 8 条: P1-1 吞吐跨口径拼接失实 (三处改写, 与技术路 P1-1 同源双坐实) / P2-1 批次 A 文件计数矛盾 / P2-2 争用源归因与时间窗不吻合 (①②⑦ 在 ⑧ 起跑前已结束, 不构成同窗争用 — 改述为部分定位+候选+独占裁决试验, 并如实补入本审计自身 ⑦ 深审代理的 15GB 哈希/实读为 ⑧ 窗前段实锤) / P2-3 codebook 3453 vs 3442 口径差钉死 (51 全集 vs 46_full, 差 11 列 51 独有) / P2-4 静态预审吸收声明补矩阵项 / NIT 定级标尺统一 (H2→P2, H3→NIT) + §0 EXIT 脚注 + W1-W7 对账行 + H3 gate 断言化。
  - 技术 7 条: P1-1 (2.735 MB/s = 03 步级墙钟吞吐非 branch_county 纯写盘 [7.35 MB/s], ×8 删除, 同口径 ×2.8/×4.1) / P2-2 「数值零影响铁证」降格 (dta 定宽字节不感知值漂移) / P2-3 parquet 微漂归因降格候选 / P2-4 H2 修法暗坑 (勿模块级 setup_logging, 40/51-path import 复用链会截断污染 46 log) / NIT-5 镜像 gate 拆解 / NIT-6 行号微调 (302-316/:426/584-609/610-630) / 快照佐证标注。
  - 可执行性 9 条: P1-1 H2 镜像 gate 不可机械执行 (拆解为机制自证+跨轮义务) / P1-2 「2 源文件」笔误 / P2-1 H2 落点写死 A 案 (STAGE_NAME 提升 + :81 改名, 3 行; B 案备选) / P2-2 gate 命令/前置 (40 parquet + codebook json 双在盘)/副作用 (46 dta 重写可接受 + 61 盲表重写零标注前提) 补全 / P2-3 DEFERRED 补 F1(a) / P3-1 §8 收口标准 / P3-2 D1 插注行文 / P3-3 H3 gate caplog 断言化 (grep 证实无测试锁旧文案) / NIT 双锚复算入口 + 批次 A 预算 <15min。
- **R2 (对抗复核, okToShip=false → 已逐条落实)**: 攻击面 = R1 修订自身 + 三路共同盲区。**全部核心攻击未攻破** (吞吐三处数字自洽且锚落盘可查 / ⑧ 争用实锤时间窗重叠+量级双成立 / H2 A 案行为逐路径等价 [24 处 basicConfig 全在 `__main__`/③] / ③④⑤⑥ 证据与代际耦合无漏 [82 四输入 mtime 18:41-18:45 全①新代, 81 审计对象 mtime 19:13-19:14 全新代, 唯一旧代消费=27 号已被 G2a 哨兵覆盖] / H1=P1·H2=P2 定级标尺可辩护 / D2 销案成立)。攻破 1 条: **P2-1** H3 caplog 断言落点错位 (汇总 INFO 在 main() 内, :76 用例只直调 `_write_blind_workbook`, 断言必红) → 改 source-lock 断言 (镜像 test_pipeline_shims 先例)。附带落实 4 NIT: H2 等价性论证补全 (第三条消费路径 tables.py + basicConfig 全仓证据) / 镜像形态漂移预登记 (§5-3) / 7.7 MB/s 标注推算值 / ⑧ 实锤精确为步骤 02 段 + sidecar 非原子入 DEFERRED。
- **R3 (终审签核, ok_to_ship=TRUE「愿为该判定的后果签名」)**: 22 条修订逐 grep 核对 21.5/22 落实, 唯一半截残留 = §5-1 H3 gate 旧表述「caplog 断言绿」与 §3-H3 source-lock 定谳矛盾 — 签核条件, 已当即修正 (本条即回填 commit); H2/H3 gate 三处口径闭环; 收口标准自查达标 (P1=H1 治理项显式 DEFER 挂用户, 标准句已补「视同已决」半句); 用户六项要求逐项兑现且 ⑧ cap 违约披露诚实 (§6.1 自认裁量未获授权); 3 个最承重断言抽样复核 3/3 坐实 (H2 双 logger 事实+盘上 0 命中实锤 / basicConfig 恰 24 处+tables.py 第三路径实存 / H3 caplog-必红定谳正确)。随手项 2 (双锚字面命令) 与 3 (收口标准半句) 已一并落实。**计划层收口: 三轮五路评审全绿, 待用户授权实施批次 A/B。** (用户于当日完全授权, 触发 R4/R5 实施前双终审。)
- **R4 (实施前终审一, 「从实施后世界倒推」预演视角; ok_to_ship=false → 已逐条落实)**: **P1-1 (本轮最大发现)** = R2 期「无测试锁旧 logger 名」断言被实读证伪 — `test_stata_export.py:399-400` (INFO caplog, A 案后必红: pytest root=WARNING 压掉 INFO) + `test_omni_fix_stata_export.py:41,363` 按旧名捕获 → 甲案修法 (两测试改 `se.logger.name`, by-name 4→6) 回写 §3-H2/§4; P2-1 `:513` `se.main()` 会话内 logger 持久污染 → 用例尾恢复 (同批落); P2-2 codebook json 竞态现势成立 (23:29 仍在重生) → 单跑 46 前后核 json (size, mtime_ns) gate 句; NIT-1 source-lock 落点定死 (模块级 + inspect.getsource, 断言双向干净实证)。其余六项预演全绿 (import 期零 logger 调用 / H3 非 f-string 替换安全 / D1 注 E501-ignored / gate 前置盘上态含盲表零标注 live 实证 / 批次 B 落点 [上轮计划 git 干净, :190 后插两行] / 共享树现势 HEAD→743d29da 七个 codebook-only 提交与本批零交集)。
- **R5 (实施前终审二, ok_to_ship=TRUE 签字, 附 1 条 gate 口径更正)**: R4 修订 4/4 落实且时序有序; **对抗 R4 机理复核** — 「root=WARNING 发射端压掉 INFO」因果链独立证实**准确** (caplog handler 挂 root 不按名过滤, 直接机理非「捕不到」而是 at_level 作用于旧名 logger 后新名 logger 继承 root=WARNING 在 `isEnabledFor` 压掉; 修法不变); 附带澄清 omni:363 为 WARNING 级捕获, A 案后即使不改也不红, 改 `se.logger.name` 属 rename-proof 防御 (R4 记录的「必红」只归 INFO 路 :399-400, 精确)。**P2 更正**: §5-1 旧名 0 残留 gate 按字面必假红 (字符串=import 路径合法命中 ~50 处) → 更正为 logger-语境口径 (已回填正文)。抽样加固 ×2: conftest fast 自动标记证 3 测试文件必入 A/B 覆盖; core/logging.py 同名单例+stdout console 结构性保证。给出九步实施顺序 (基线先行→编辑→定向→全量→46 gate [json 前后采]→61 gate→双锚→commit A→批次 B), 实施已按此执行。

## 8-bis. 结果评审记录 (实施后)

- **RR1 (diff 符合度, okToShip=TRUE, 0 P级)**: 批次 A 恰 6 文件 / 批次 B 恰 2 文档, 与 §4 分组逐一吻合, 零夹带零跨批越界零无主 hunk; H2 甲案落点 / H3 source-lock 断言 (含全角/半角引号逐字符核, 双向干净) / D1 计数注均与 R4/R5 定谳逐字一致; §7-bis 与实际执行双向闭合 (gate 痕迹时间戳早于 commit A); DEFERRED 零越界。2 NIT 记录性 (「A 案 3 行」实为 +7/-1 含说明注释 / commit A message 引用计划文件早于其入库 83 秒的悬空窗)。
- **RR2 (独立复算, okToShip=TRUE, 无保留意见)**: 不采信自述逐项亲测 — 定向 68 项 + 旁路 39 项全绿; 46 号日志三锚在档且盲区闭合经源码机制级验证 (三锚发射点均走模块 logger, 修复前冒泡 root 即丢); dta 220×3442 + 3442/3442 中文标签实读; 40/51 parquet mtime 未触碰 (golden-safe 独立证实); 61 同轮 WARNING/INFO 并读矛盾消除 + 盲表零标注态保持 (0/1000 ×2); 40/51-path 日志零 '46_stata_export' 泄漏 (结构性不可能: setup_logging 具名+propagate=False)。
- **RR3 (终局签核, ok_to_push=TRUE「愿为推送后果签名」)**: push 安全 (origin/main..HEAD 恰 2 提交零并发夹带 / 远端无超前 / 分支=main 非 detached [开场快照 'HEAD' 系陈旧伪影]); 终态卫生 (0 secrets [2 命中均 monkeypatch 形参误报] / 0 .env / 最大 168KB 无二进制 / 45,404 字节 diff UTF-8 0 U+FFFD); 35 shim 全 ≤30 行铁律不破 (批次 A 零触碰 shim, 抽查 46=11/61=22/80=22/81=22/82=23 行)。前置动作 = 本 §8-bis 补记 (随本 commit 闭)。
