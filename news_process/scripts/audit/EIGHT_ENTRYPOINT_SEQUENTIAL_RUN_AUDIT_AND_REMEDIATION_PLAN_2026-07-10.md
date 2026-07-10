# 八入口顺序真跑 — 审计与整改执行计划 (2026-07-10 · 修订版 R5 · 八路评审收口, 已获用户完全授权实施)

> 日期 2026-07-10 · 环境 OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP=1 / PYTHONIOENCODING=utf-8) · 解释器 F:\Anaconda3\python.exe (conda base 3.13) · cwd=news_process\ · 每入口 2h cap。
>
> 本轮 = 用户指定顺序 8 入口 (五入口再验证 2026-07-10 之后**首次**含 80/81/82 + 双 company 步骤 04 的全谱真跑)。审计方法 = 1 路静态数据流预审 + 4 路分入口日志深审 (逐条对 F1-F16 台账/codebook §7/T=2 白名单对账) + 主笔逐条源码/产物亲核承重发现。
>
> **修订 R1**: 已吸收三路最高标准评审 (完整性/技术正确性/可执行性; 三路首轮均 okToShip=false)。核心修订: G4 修法从"全局 std>0"改为**配对子集判法** (原口径被盘上数据构成现成反例证伪); gate-2 从 `--steps 02` 改 `--steps 02,03,04`; 冒烟命令强制 `--output` scratchpad (防覆写生产 27 号自毁哨兵夹具); 新增 G14 (80 安慰剂披露); 计数/行号/gate 全量补齐。
> **修订 R2 (对抗复核)**: 撤销 R1 的"暴露面 48→84 列"错改 (**反更正回 48 列/管道** — 84 是按 `cw_/ce_benefit_*` 前缀计数, 其中 36 列源自 40/51 同代产物, 不在混代暴露面; 真实口径 = registry `source=='27'` 恰 8 基名 × 3 轨 = 24 源列 × {cw_,ce_}, 双 registry YAML 已亲核同谱); G2(a) 哨兵基准改**保守超集主方案** (真实父代文件在 02 无 resolve 句柄); tax pair metadata 写点纠为 **main() 内联自有副本 02:1140-1142, 必须与 listed 双改**; 删除"02 重跑打回 codebook 占位"错误论据 (tax 02:838-841 实为**保留既有章**); G4 补 `pd.notna` 保留 + inf 语义注 + RangeIndex 前提注 + gate 作用域收窄; §2 补 stage13 掉 9 家与 Bartik 前视掩码; 计数口径注 + §7 追溯修正。
>
> **修订 R3 (max-effort 终审)**: 哨兵重生命令逐字补 `--track all --include-lg` (裸命令会重生残缺 27 号 — 比"陈旧"更糟); gate-2 插入"步骤 0 先存基线再动代码"; resolve None 缺席分支; §6 共享树并发第 6 条; §8 R1 错改条目标注推翻。
>
> 状态: **计划层收口 (R1 三路 + R2 对抗 + R3 + R4 + R5 终审, 五轮八路全部落实; R4/R5 均 ok_to_ship=true), 用户已完全授权实施**。评审记录见 §8。
> R5 随手项已折入: §2 预登记哨兵 WARNING 白名单 / 字节漂移前瞻 (批次 C 落 F 台账) / F 台账 §3 标题同步 / 日志行号锚免责 / G4 gate 两段式断言 (catch_warnings 包真函数不会翻红 — try/except 外壳吞警告, 红信号必须来自 caplog: ①修后判定逻辑在 try 外 error-filter 重演证无警告 ②调真函数断言 caplog 无"混淆诊断失败"且有"跳过" INFO) / mtime_ns 取舍在 commit message 记录 (保留 mtime_ns 取证时间线, 代价 = pair parquet/80 sidecar 文件级字节自此 run-dependent by-design)。
>
> ⚠ 本计划所引日志行号 = 2026-07-10 运行快照; 批次 A/B 落地后重跑, 行号锚以新日志为准, 勿以行号漂移立案。

## 0. 结论速览

- **8/8 EXIT=0 · 0 真 ERROR · 0 Traceback · $0** (stage21 lookups=13,896 hits=13,896 misses=0; 嵌入/BERT 全离线命中)。
- **golden 安全坐实**: 面板 220×3442 / article 1005×1305 / 51: 220×3453 与上轮基线逐项相等; listed 7 权 dta 字节等价 1,603,484,161; registry 双锚未变 (listed 023cdc91… / tax 4f580e3f…); tax 五面板 447,710 行不变量全绿。
- **慢化是伪回归**: ①=2313.7s (上轮 1133s) 与 ⑦=1880s (上轮 730.6s) 的倍差经日志内部分段计时定谳为**宿主机 IO/CPU 并发争抢** (⑦ 同 run 内写盘双峰 9→21MB/s 铁证; 争用窗 ~12:30–13:43); ⑧ 剔除新增步骤 04 后**实为提速 321s** (争用已消退)。行列/字节证据证数值零影响。
- **本轮定级: P0=0 · P1=2 (G1,G2) · P2=8 (G3,G4,G5,G6a,G6b,G7,G12,G14) · NIT=4 (G8,G9,G10,G11; G14 附带 NIT 子项随主条计, 不另计) · 记录=1 (G13)**。全部非阻断; G1/G4/G8/G11 为 golden-safe 小修, G2/G3 为代际锚补齐 (仅 pair parquet metadata 与 sidecar 字节变, **7-dta 字节等价锚保留**), 其余为文档/披露/生产 checklist。
- 静态预审 (A–E 五节 + Top5) 的吸收声明: Top1 (company 崩) / Top3 (80 假成功) **证伪** (27 号在盘 + 80 真产 143×29 面板); Top2 (stage40 离线崩) 条件未触发 (缓存全热, 其"离线冷缓存 = ① 最脆弱前置"判断收入 §7 checklist); Top4 (81 吞退出码) **坐实为 G1**; Top5 (81 审 40/51.dta 而论文消费 46_full.dta) **坐实为 G6(b)**。A 节输入契约用于跑前预检 (全部齐备); B1/B4 收编入 G2; B2/B3 无行动项 (孤例澄清/只产不消无害); C 节 offline 语义收入 §7; D2/D3 收编入 G1; D4=G6(b); E2 的 read_cols 无守卫在 27 号在盘时不触发, 收入 G2 文档面。**无第六项被静默丢弃。**

## 1. 运行结果总览

| # | 入口 | 结果 | 墙钟 | 上轮 | 关键证据 |
|---|------|------|------|------|---------|
| ① | run_pipeline_function | ✅ 0 | 2313.7s | 1133s | 16/16 ✓; stage21 离线 13,896/13,896; 面板 220×3442; 慢化=争用 (40 内两 LDA 子步 370s+288s) |
| ② | run_pipeline_validation | ✅ 0 | 635.8s | 242s | 16/16 ✓; 66/70 离线优雅跳过; 72/75 产物重生 |
| ③ | run_paper (裸跑) | ✅ 0 | 0.8s | ~5s | 11 篇组合总览, 0 render 失败; 历史段 3 ERROR = 2 负例测试 + 1 KeyboardInterrupt (非本轮) |
| ④ | 80_placebo_and_alt_anchor | ✅ 0 | 1.6s | — | 真产 80 面板 143 bank-year × **29 列** (嵌入全缓存 $0); placebo 5 规格命中数入 sidecar; 安慰剂量级披露义务见 G14 |
| ⑤ | 81_stata_data_audit | ✅ 0 | 2.6s | — | 158 项: PASS=138 / WARN=20 / **FAIL=0**; 报告落 eval_reports/81_stata_data_audit.csv; 20 WARN 归类表见 §2-bis |
| ⑥ | 82_export_stats_excel | ✅ 0 | 1.0s | — | 4 阶段 × 3 字段 = 12 sheet 全覆盖; 漏斗 9,490→5,031→1,650→1,005 与 80 sidecar 交叉一致 |
| ⑦ | company_listed_bank | ✅ 0 | 1880s | 730.6s | 01=5.5/02=236.7/03=1484/04=151.9; 锚 023cdc91 未变; 9 dta 满尺寸, 7 份字节等价; 04 磨损三段断言全绿 |
| ⑧ | company_tax_bank | ✅ 0 | 2636.6s | 2397s | 01=19.2/02=316.2/03=1740/04=559.1; 锚 4f580e3f 未变; 5 dta 6.85–6.90GB; 锁链闭合 (03 registry-sha 单锁 + 04 双向锁); F11/F12 生效 |

## 2. 白名单对账 (已知非问题, 本轮复现且行为与台账一致 — 不再立案)

- **T=2 退化全谱**: DiD 全 0 (dcep/sandbox) / Bartik 弱 IV·share one-hot 退化 **+ 前视掩码致 IV 有效率 24.6–49.6% <50% (T=2 基期结构, 口径设计非弱工具, `40_build_panel.log:645-682`)** / 零方差常量 (depins_post, brokerage_fire_sale) / BERT `nt_iyvol/iytrend` NaN / `_std` 族高缺失 66.8–70.0% / 零新闻 bank-year 35% / 建碁 67.9% 形态放大 (§7 硬义务见 G12) / 62 输入 10,076 行 / 67 时间稳定性 <3 年 / 22 词典 joblib 单批 / **stage 13 银行覆盖掉出 9 家 (151→142, 无金科邻近共现; 硬过滤 by-design 的 T=2 形态 — R2 补录, 生产掉出名单须留档供 data appendix, 入 §7)**。
- **既有 by-design 披露 (07-06 日志审计已裁定, 点名归档防再立案)**: DiD HQ-based 处理分配假设 (`run_pipeline_function.log:3943`) / csdid never-treated 仅 2 家→改 notyet (`:3957`) / 63 demo_mode 合成标注严禁入论文 / jieba 边界词 6/1506 / 变量名 33 字符 ×3 / 00 跨目录同名副本去重 1 个。
- **F 台账项实证复现**: cross_media 陈旧跳过 (F2, `40_build_panel.log:1206` 显式落痕) / company "40 加权列全 NaN" 双根因文案 (F3, 02 侧生效; 01 侧漏改=G8) / 66/70 离线优雅跳过 (F6/F10) / stage64 覆盖率非单调 (F14, `64_tone_validation.log:176,376,576`)。
- **整改实证生效**: F8 原子写 (0 `.tmp` 残留) / F11 锁 release INFO (`run_pipeline.log:149/157`) / F12 子步 stderr `│⚠` 转发 (双管道逐条可对)。
- **company 01 豁免补注册 ×4** (listed `01:131-134` / tax 同构; llm_vote_tone_std + avg_{subst,locus,collab}_prob_score 按 WP0-6 ③ 先例收编): 共享树 40 面板列漂移的显式信号, by-design 留痕, 结果与锚一致。
- **validation 弃用工作台提醒 ×4** (61_human_samples.xlsx + 09_sentiment_verify_{full,ctx,ss}.xlsx, `run_pipeline_validation.log:257,1510,1710,1913`): 悬空清理项, 与 t2v 孤儿同性质, **挂后续清理批, 不入本批** (确认无已填标注后手删)。
- **61 抽样媒体单类占比 100%** (`run_pipeline_validation.log:264`): T=2 抽样倾斜, 日志自带"须在 33/34 代表性检验披露"义务 → 并入 §7 生产复测项。
- **(预登记, 批次 B 落地后生效) G2a 哨兵 WARNING "27_benefit_dimensions_panel 代际陈旧"** = dev 常态预期 (27 号由 paper 侧独立生产), 下轮日志审计勿立案; 生产口径见 §7-G2。§5-2 实跑时该 WARNING **应当出现**, 本身即哨兵的免费实弹验证。

### §2-bis · 81 的 20 WARN 逐条归类表 (10 检查 × 40/51 双面板镜像)

| 检查项 | 归类 | 判读 |
|---|---|---|
| 高缺失率变量 >50%: 609 个 (`*_tone_std_*` 族 66.8–70.0%) | T=2 预期 | `_std`=组内标准差, n≤1 篇格恒 NaN; T=18 大幅收缩但不归零; 变量表注明"定义域 = n≥2 篇格"即可 |
| llm_vote_tone_ctx 缺失 10.49% / _ss 7.69% | 已知口径 | conditional-on-full 轨 by-design |
| dict_avg_tone_full 1 obs >5σ | T=2 预期 | 220 行单点 |
| LOO-IV r=0.030 (prov) | T=2 预期 + 披露 | → G6(a) |
| dcep/sandbox DiD 不可识别 ×2 | T=2 预期 | 报告自证 "vacuous PASS" |
| 116 列名含中文 | 已知口径 | stage 46 rename_map 短名注入在案 (07-10 varattr 计划) |
| Nullable dtype 3330/3341 | 已知口径 | 导出层统一 cast |
| 零新闻 bank-year 35% | T=2 预期 | data appendix 报告样本构成 |

## 3. 新问题台账 (G 系, 承接 F1-F16; 收编判据 = 跨轮持续跟踪项才收编 F 系; 每条已主笔亲核或双源坐实)

### G1 · [P1 · 潜伏 · NEEDS_FIX] 81/82 shim 吞退出码 — 审计工具的"报警器没装电池"
- **证据**: `news_process/81_stata_data_audit.py:20-22` 裸调 `main()`; 底层 `pipeline/audit/stata_audit.py:1273` FAIL 时 `return 1`、`:1276-1277` 模块直跑 `sys.exit(main())` → shim 路径下 FAIL 恒退 0。`82_export_stats_excel.py:22-23` 同病 (底层 `stats_excel.main` 全文件零 return 恒 None → `sys.exit(None)`=0, 改齐字节等价无副作用)。`80_placebo_and_alt_anchor.py:22` 已是 `sys.exit(main())` (口径基准)。
- **影响 (白话)**: 官方入口跑出"必修硬错" (重复键/份额溢出/恒等式破裂) 时进程仍报成功, 外层看退出码必漏报。本轮 0 FAIL 未触发, 属潜伏。
- **修法**: 两 shim 改 `sys.exit(main())`。各 1 行, golden 零风险。
- **gate**: **新建** `tests/test_pipeline_shims.py`: 断言 80/81/82 三个不注册 shim 源文件均以 `sys.exit(main())` 收尾 (文本/AST 断言)。

### G2 · [P1 · 代际锚盲区 · NEEDS_FIX(记录层) + DOC(重生纪律) · **收编为 F17**] company 双管道 input_fingerprint 只锚 21_full 的"尺寸|行数"; 40/51/16/27 不入锚 — 本轮已实弹混代
- **证据**: tax `02:1139` `sha256(f"{p_input.stat().st_size}|{len(input21)}")`, `p_input`=仅 `21_tone_llms_full.parquet` (`:998`); listed 侧同构 (`02:1299` p_input / `02:1435` fingerprint; tax 经 `engine()` importlib 复用 listed 02)。盘上 mtime 实锤: `27_benefit_dimensions_panel.parquet`=07-03 03:32 (唯一生产者=`papers/benefit_society/dimension_analysis.py:881` 主产物/`: 534` merge 副本, 8 入口顺序不重生它), 16=07-10 12:44 / 21_full=12:45 / 40/51=13:07 → **本轮 02 混代消费**。暴露面 = registry `source=='27'` 条目 (4 维 × {'','_lg'} = **8 基名 × 3 轨 = 24 源列**, listed `01:504-511`; 双 registry YAML 亲核同谱) → 双管道各 **48 列** (× {cw_, ce_}) — listed × 10 面板, tax × 5 dta。⚠ 勿按 `cw_/ce_benefit_*` 前缀计数 (=84): 其中 36 列 (mean/pos_frac/neg_frac × 6 轨 × 2 前缀) 源自 40/51 **同代**产物, 不在混代暴露面 (R2 反更正)。锁链 (02 复算锚 / 03 registry-sha 单锁 / 04 双向锁) 全绿不报警; 01 的"域外恒 25"只能抓列名漂移抓不了同 schema 换值。
- **影响 (白话)**: 这批列的原料是一张没盖生产日期章的旧表。本轮恰好没坏 (27 号值未变, 7 dta 字节等价佐证); 但生产 T=18 换嵌入/重跑主管道后若 27 号不同步重生, 论文面板会**静默混用两代嵌入测度**, 没有任何闸翻红。与 F2/F9 同族 (顺序/新鲜度耦合), 暴露面直接落论文交付物, 故 P1。
- **修法 (两层)**:
  - (a) **记录层 (本批实施, golden-safe)**: 双管道 02 启动时对五上游 (21_full/40/51/16/27; 路径**复用 02 内既有 `resolve(...)` 句柄**, 勿二次硬编码; 实名 = `21_tone_llms_full.parquet` / `40_panel_yearly.parquet` / `51_panel_with_controls.parquet` / `16_article_alignment.parquet` / `27_benefit_dimensions_panel.parquet`) 计算 `size|mtime|sha256 前 16 hex (流式)` 三元组 (盘上合计 ~33MB, <0.5s; T=18 由 21_full 主导亦仅 10–60s 级, 占 02 自身 <1%; **不退化为 size|mtime 弱锚** — mtime 恰是要治的盲区维度), 写入日志 + **pair 长表 parquet 的 schema_metadata 追加键 `b"upstream_snapshot"`** (JSON bytes)。**落点 = 两处独立写段, 必须双改** (R2 纠正): listed `02:1436-1438` + tax `02:1140-1142` — tax 的 pair metadata 段是 main() 内联自有副本, **不经 engine() 复用** (engine 只覆盖 default_paths/load_input21/build_measure_library 等六纯函数), 只改 listed 一处 tax 不生效。03 点取 `registry_sha256`、04 点取 `registry_sha256`+`input_fingerprint` 两键 (tax `03:937-944`/`04:629-654`, listed `03:1031-1036`/`04:637-662`; 03 全文无 input_fingerprint 读点) — 多一个键零影响, **锁不翻**; 04 fp_now 只吃 21_full 的既有红/绿语义不变。**snapshot schema (R4 钉死, 双管道逐字同构)**: 键 = resolve 句柄名五个 `{input, panel, alignment, benefit, controls}`; 值 = `{"file": 实文件名, "size": int, "mtime_ns": int (st_mtime_ns, 勿用 float epoch — repr 跨写法漂移), "sha256_16": hex}`; 缺席上游 = `null`。同时加**新鲜度哨兵 (主方案 = 保守超集)**: `mtime(27) < max(mtime(p_panel), mtime(p_input))` — 两句柄 (`40_panel`/`21_full`) 均在 02 resolve 白名单内, 零新增路径; 代价 = "21 重生而 40 未重生"场景多产良性误报。⚠ 27 号真实父代 (`40_article_bank_level.parquet` / `27_benefit_embeddings_full.npy`) 在 02 中**零读点、resolve 拿不到**, 如要真实父代基准须在 `default_paths()` 显式加键, 作可选强化不作默认。触发时单行 loud WARNING: "27_benefit_dimensions_panel 早于本轮主管道产物 (代际陈旧), benefit 48 列取值属旧代 — 重生入口 = 从 repo 根跑 python -m news_process.papers.benefit_society.dimension_analysis **--track all --include-lg --df-exploded news_process/data/processed/40_article_bank_level.parquet** (缺 --df-exploded 则 anchors-only 不落面板; 若 27 号确已同步重生, 本警告为保守误报, 以 upstream_snapshot 内 benefit 的 sha256_16 为准)"。⚠ 实施冒烟定谳 (2026-07-10): `--df-exploded` default=None → 缺之则 anchors-only **EXIT=0 假成功不落面板**, 命令三参数缺一不可。⚠ R3 定谳: 重生命令**必须带** `--track all --include-lg` — `--track` 默认 both (仅 full+ctx)、`--include-lg` 默认关 (`dimension_analysis.py:620-633`), 裸命令会重生出只剩 8/24 源列的残缺 27 号 (ss+`_lg` 半边消失), 比"陈旧"更糟; 且 `--output` 默认相对路径须 cwd=repo 根。⚠ 缺席分支: `resolve("benefit")` 非 required, 27 缺盘时返回 **None** (listed `02:1261-1274`) — snapshot 对缺席上游写 null 条目、哨兵在句柄为 None 时跳过 (勿 AttributeError 崩 02, 哨兵存在的意义恰是覆盖降级环境)。借 runner F2 的 loud-warn 风格; ⚠ **语义与 F2 守卫相反须写明**: runner=陈旧则跳过 merge 不并列, 本哨兵=**警告后照并旧值** (27 号由 paper 侧独立生产, 陈旧在 dev 常态, 警不崩)。
  - (b) **硬锁层 (DEFERRED, 受 M0)**: 五上游全量并入 `input_fingerprint` 本体 → 语义变为"任何上游重生必须重跑 02→03→04 全链"。强纪律成本收益生产 T=18 首播前定谳。
- **golden 影响**: registry 锚只压 entries/bank_company_map/excluded/dv2 (listed `01:288` / tax `01:321`, docstring 明言 meta 不入锚) → 双锚 023cdc91/4f580e3f **不 bump**; `upstream_snapshot` 只进 pair parquet metadata → **仅 pair 长表 parquet 字节变, 10+5 面板 dta 与主面板 parquet 数据字节不动, 7-dta 字节等价锚保留**。
- **gate**: 双管道各 1 pytest (pair metadata 含 `upstream_snapshot` 五键 + 哨兵在 27 陈旧夹具下 caplog 出 WARNING + **缺 27 夹具下不崩且写 null 条目**); 实跑 gate 见 §5-2。

### G3 · [P2 · 可审计性 · NEEDS_FIX] 80 sidecar 无上游数据指纹
- **证据**: `data/processed/80_alt_anchor_and_placebo_panel.sidecar.json` 仅记 3 个 YAML/方向向量 sha + 计数/模型/seed; 不记 `27_benefit_embeddings_{full,ctx,ss}.npy` / `27_benefit_direction.npy` / `40_article_bank_level.parquet` 的 sha/mtime (本轮同代系 mtime 人工核出, 非 sidecar 自证)。写点 = `pipeline/features/benefit_society_audit_combined.py:348-353` (调用 :656), `schema_version "1.1"` 在 :332。消费者全仓仅 `tests/test_benefit_society_audit_combined.py:205-206` 子集键断言, 追加键不破。
- **影响 (白话)**: 事后无法仅凭 sidecar 证明 80 面板用的是哪一代嵌入; 只重跑 stage 27 不重跑 80 时 sidecar 无法暴露陈旧。80 本体已有 len(df)==len(npy) 硬校验 (`:216-236`) 兜底行数级错配, 本修补足"同长度换代"盲区。
- **修法**: 追加 `upstream_snapshot` (同 G2(a) schema, 覆盖实际接线的全部输入) + `schema_version` 1.1→1.2。⚠ 落点 (R4): **在 main() 内、`write_sidecar_json` 调用 (:656) 前追加键** — metadata dict 构造在 `build_audit_panel` (:325-343) 不持有输入路径, 且 `test_...:355` mock 了 build_audit_panel 返回值, 新键若在被 mock 函数内产生 gate 走 main 路径拿不到; `schema_version "1.1"` 字面量在 :332 (build_audit_panel 内), bump 点与追加点分居两函数须都改。仅 sidecar JSON 变, 80 面板 parquet 本体不动, golden-safe。
- **gate**: `tests/test_benefit_society_audit_combined.py` 扩断言 (upstream_snapshot 键 + schema_version==1.2); 实跑复跑 80 核 sidecar, 见 §5-2。

### G4 · [P2 · NEEDS_FIX] network_brokerage 混淆诊断块零方差 corrcoef → 4 行原生 numpy RuntimeWarning 漏 stderr
- **证据**: `pipeline/panel/network_brokerage.py:912-920` `_lag_cs.corr(panel['industry_neg_shock'])` 无零方差预判; T=2 下 lag 后配对子集仅 2018 且该年 shock 全 0 → numpy `c /= stddev` 除 0, NaN 被 `pd.notna` 静默吞、4 行警告漏 stderr (`run_pipeline_function.log:4598-4602`)。
- **修法 (R1 提出配对子集判法, R2 终版加固 — 保留 `pd.notna` 守卫 + inf 语义注)**: 原"全局 std>0 双侧判"已被盘上数据证伪 (shock 2017 年 std=0.00025 非零而 lag 仅 2018 非空, 全局判定放行后配对子集仍除零); `dropna()` 不剔 ±inf (std=inf>0 可放行而 corr 仍 NaN), 故原 `pd.notna` 分支必须保留:
  ```python
  _pair = pd.concat([_lag_cs, panel['industry_neg_shock']], axis=1).dropna()
  if len(_pair) >= 2 and _pair.iloc[:, 0].std() > 0 and _pair.iloc[:, 1].std() > 0:
      _corr_cs = _pair.iloc[:, 0].corr(_pair.iloc[:, 1])
      if pd.notna(_corr_cs):   # 保留原守卫: dropna 不剔 inf, corr 仍可能非有限
          ... (原 INFO 行)
      else:
          logger.info("     · 混淆诊断: 配对子集 corr 无定义 (非有限值), 跳过")
  else:
      logger.info("     · 混淆诊断: 配对子集样本不足/零方差, 跳过 (T=2 常见)")
  ```
  ⚠ 禁用全序列 `std(skipna)>0` 判定 — `Series.corr` 是 pairwise dropna 语义, 全局有方差不代表配对子集有方差。⚠ 前提注 (写入代码注释): `panel` 在 `:878-880` 已 `reset_index(drop=True)` 为唯一 RangeIndex, concat 对齐依赖此前提, 勿在两点之间改 index。⚠ 替换范围 (R4): **仅替换 `:914-918` 判定与日志段, 保留 `:912`/`:919-920` 的 try/except 外壳 ("诊断块绝不崩阶段" 兜底) 与 `:913` `_lag_cs` 定义行**。纯日志路径, golden-safe。
- **gate**: 扩展 `tests/test_network_tritrack_expansion.py` (或同目录新建 test_network_brokerage_diag.py): 零方差配对夹具下以 `warnings.catch_warnings()` + `simplefilter("error", RuntimeWarning)` **只包 _pair/corr 那几行的等价重演** (勿包整个 47 子步 — 防 pandas/numpy 未来版本无关 RuntimeWarning 假红) 断言无警告 + caplog 出"跳过"INFO。(⚠ 勿用 `pytest.warns(None)` — pytest≥7 已移除。)

### G5 · [P2 · DISCLOSURE] stage 71 分类维度轨间 κ 4 处超 0.70 哨兵上限 (不在 F 台账)
- **证据**: `run_pipeline_validation.log:3942-3963` — innovation_locus[ctx_ss] κ=0.7794; innovation_collab_mode 三对 κ=0.8525/0.8149/0.8663 (哨兵语义 ">0.70 = tracks redundant")。
- **判读**: T=2 下 `_ss` 回退镜像 + full-only 门控使轨间子集高度重叠, 方向预期; 但属台账未覆盖的哨兵触发。**动作**: 入台账 + 生产 T=18 复测; 若仍 >0.70, 论文披露 "ctx/ss 对分类维度增量信息有限"。零代码。

### G6 · [P2 ×2 · DISCLOSURE] 计量披露双项 (零代码, 入论文/生产 checklist)
- **(a) LOO-IV relevance r=0.030** (`logs/81_stata_data_audit.log:106,232`): T=2 机械退化, 但 relevance 本质是经验问题非样本量问题, **T=18 不保证自愈**。生产必查一阶段 KP rk F; F<10 → 该 IV 引擎降级附录稳健性; IV 策略节预留弱工具诊断 + AR 置信区间。
- **(b) 81 审计对象 vs 论文消费对象错配**: 81 盖章 `40_panel_yearly.dta`+`51_*.dta` (`stata_audit.py:1064-1069`), 而 11 篇论文 `.do` 模板消费 `46_panel_yearly_full.dta` (`stata_export.py:57` 自承)。46 号的精度/标签/nullable 未受 81 检。**动作**: 台账披露 + (后批可选) 81 扩一档 46_full 抽检; 本批不动代码。

### G7 · [P2 · 观察 · DISCLOSURE] benefit 负极锚点句 #3 在 Qwen 空间投影为正 (0.1416)
- **证据**: `40_build_panel.log:1063` (锚点轴整体仍判 "✅ 锐利", 最小对间隔 0.06481>0.02)。单句反号被 mean(pos)−mean(neg) 稀释, 非缺陷; 换嵌入模型时该句措辞宜复核。**动作**: 记入 `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN` 复核清单 (批次 C by-name); 零代码。

### G8 · [NIT · NEEDS_FIX] F3 整改 01 侧文案漏改 (listed+tax 双镜像)
- **证据**: listed `01_build_company_bank_cooc_registry.py:693` / tax `01_build_company_tax_bank_cooc_registry.py:800` 仍称缺源列基名"按缺列容错出全 NaN 列", 实际默认分支 `emit_tracks=[]` **产 0 列** (listed `01:668-687`; 02 侧新文案正确, 同 run 两步自相矛盾)。
- **修法**: 双 01 WARNING 文案改为 "…按缺列容错**默认不产列** (emit_tracks=[], 面板无此列族; boilerplate/rare_word DEFERRED 家族例外仍出全 NaN 列)" — 收窄措辞防对 DEFERRED 家族 (listed `01:684-685` 恒 emit 全轨) 说反。纯日志字符串, 不进锚复算输入域 (锚只吃 registry dict 四内容区段) → **锚不 bump**。
- **gate**: 跑双 01 后 grep 新文案 + `test_company_*_registry` 锚断言不变红。

### G9 · [NIT · DOC] cross_media 列数 3442↔3451 振荡 (F2 反向补遗)
- **机制** (`runner.py:368-379` 上游登记 / `:395-434` mtime 守卫+并入): 本轮 ② 重生 75 号 (11 列 = 2 键 + 9 特征) 后其 mtime (13:18) 已晚于 21_full (12:45) → **下轮单独重跑 stage 40 时守卫必放行**, +9 列 (3442→3451); 下轮全主线重跑 (21 重生) 则又跳过回落 3442。面板 schema 不再是自身输入的纯函数, 随"跑法"振荡。
- **动作**: F2 台账条目 (`FIVE_ENTRYPOINT_REVERIFICATION_AND_REMEDIATION_PLAN_2026-07-10.md`) 补写反向方向 + A/B 差分 SOP 规定"比较前先核 `cross_media_alpha_full` 列在场性" (同步入 §7); 并入侧安全性已有守卫 (重复键 fail-loud / 行数断言 / 只并新列)。零代码。

### G10 · [NIT · 可选优化] raw_census 每跑全量重算 700.8s (占 ① 的 30%)
- **证据**: `00_preprocessing.log:54,396`; 调用路径不走 `--from-summary` 渲染 (`raw_census.py:560-592` 支持但管道内未接)。by-design (用户 2026-06-20 需求"每次运行写进日志"); 现成开关 `raw_census_logging=false`。**本批不动**; 生产 T=18 排期时决策 (见 §7)。

### G11 · [NIT · NEEDS_FIX] company 产物清单日志只记 4 位有效数字 MB, 无法机器对账
- **证据**: `company_tax_bank/logs/run_pipeline.log:51,70-71,85-87`; 上轮日志被覆盖后字节级等价从日志不可证。
- **修法**: 双 `run_pipeline.py` 产物清单行追加精确字节数 (`{size:,d} B`); dta 不算 sha (太大), parquet 可选 sha 前缀。纯日志, golden-safe, 双管道对称。
- **gate**: 双管道任一步重跑后 grep 产物清单行含精确字节数, 且与 `ls -l` 实测相等 (见 §5-1/§5-2)。

### G12 · [P2 · 生产 checklist] 建碁科技 67.9% 共现灌水形态 (§7 L1 池内已挂账)
- dev 上单企业吃掉 2/3 full 轨共现计数 (`company_tax_bank/logs/02_*.log:188`)。**不做 source-clean** (F1 评审已证伪该方向, 会误删合法品牌简称); 动作 = 生产 T=18 复跑后 `n_docs_longhit` ≥4 字稳健臂复核为**硬义务**, 入 §7。

### G13 · [记录] 非问题澄清 (防后人误判)
- ③ 历史段 3 ERROR = 2026-07-06 白名单负例测试 ×2 + KeyboardInterrupt ×1 (`run_paper.log:79,161,2171-2213`), 非缺陷。
- ⑧ "慢化"伪命题 (04 新增 559s; 剔除后提速 321s); ①⑦ 慢化=争用窗, 数值零影响。生产注: ① 内 40 的两个 LDA 子步 (战略差异度 370s + authoritative_similarity 288s @143 docs) 是 T=18 规模外推压测对象 (→ §7)。
- 22 词典 joblib 单批 (1,005<5,000 batch_size, `22_tone_words.log:116`) 近似串行属 T=2 形态, 生产自然分批。
- msent_score "均值=-0.7097 (整体偏正面)" 是"越大越负面"口径 (`22_tone_words.log:210-211`), 非反号 bug。
- `27_benefit_*_t2v*.npy` (06-26) 为已移除 t2v 轨孤儿文件, 无消费者; **挂后续清理批** (与 validation 弃用工作台 ×4 同批), 不入本批防误删连坐。

### G14 · [P2 · DISCLOSURE] 80 安慰剂信号量级披露义务 (R1 新增, 原稿遗漏)
- **证据**: `logs/80_placebo_and_alt_anchor.log:69` — "⚠ 5 条安慰剂信号量级 ≥ 替代锚点一半 (housing_loans, credit_cards, intermediate_business, branch_channel, general_corporate): 需在论文稳健性附录中正面回应是否伪相关"。
- **附带 NIT 子项**: `:57` ratio 阈值 0.5/1.0 自承 "ad-hoc 日志启发式, 非 alt_anchor.py:10 文档的回归 β 比值判据" — 文档/实现判据口径不一致 (纯披露, 不改代码)。
- **动作**: 入台账 + §7 "T=18 复跑 80 后按回归 β 判据正式裁定 5 条安慰剂; 论文稳健性附录正面回应"; dev 命中数 21–273 篇 <500 效力不足, 不在 T=2 定谳。零代码。

## 4. 修复批次 (按独立提交, 全部先过 gate 再 commit; by-name stage, 排除并发产物)

- **批次 A (golden-safe 小修, 1 commit; 7 源文件 + 1–2 测试)**:
  `81_stata_data_audit.py` · `82_export_stats_excel.py` (G1) · `pipeline/panel/network_brokerage.py` (G4) · `company_listed_bank/01_build_company_bank_cooc_registry.py` · `company_tax_bank/01_build_company_tax_bank_cooc_registry.py` (G8) · `company_listed_bank/run_pipeline.py` · `company_tax_bank/run_pipeline.py` (G11) · **新建** `tests/test_pipeline_shims.py` (G1 gate) · 扩展 `tests/test_network_tritrack_expansion.py` 或新建 diag 测试 (G4 gate)。全部日志/退出码路径, 零数据值影响。⚠ **税调 token 白名单闸 (R4)**: `tests/test_company_tax_bank_cooc_registry.py:80-101,311-315` 扫 tax 五脚本非注释代码行, 命中 `{company_bank, company_listed_name, stock_code, company_listed_bank}` 任一 token 且不在恰 4 条白名单内即红 (**代码行的行尾注释不豁免**) — tax 侧新增行 (含行尾注释) 禁含这四个字面量。
- **批次 B (代际锚补齐, 1 commit; 3 源 + 3 测试)**:
  `company_listed_bank/02_build_company_bank_cooc_panel.py` · `company_tax_bank/02_build_company_tax_bank_cooc_panel.py` (G2a; ⚠ pair metadata 写段是**两处独立副本必须双改** — listed `02:1436-1438` + tax `02:1140-1142` main() 内联, 不经 engine() 复用) · `pipeline/features/benefit_society_audit_combined.py` (G3) · `tests/test_company_bank_cooc_panel.py` · `tests/test_company_tax_bank_cooc_panel.py` · `tests/test_benefit_society_audit_combined.py`。⚠ 验证要点: 双 registry 锚**不得 bump**; 仅 pair parquet metadata 与 80 sidecar 字节变; 面板数据列值列哈希 0 相异。
- **批次 C (文档/台账/披露, 1 commit)**:
  本计划 md (§3 终稿+评审记录) · `FIVE_ENTRYPOINT_REVERIFICATION_AND_REMEDIATION_PLAN_2026-07-10.md` (F2 反向补遗 + F17=G2 收编) · `SWAP_GEMINI_TO_QWEN3_SILICONFLOW_EXECUTION_PLAN` (G7 锚点句复核清单)。
- **DEFERRED (受 M0 / 后批)**: G2(b) 硬锁层; G6(b) 81 扩检 46_full; G10 census from-summary; 清理批 (t2v 孤儿 + 弃用工作台 ×4); F1(a) 税调匹配层过滤 (维持既有 DEFERRED)。

## 5. 验证 gate (每批次)

1. **批次 A**: 新建/扩展 pytest 子集全绿; 单跑 47 子步夹具确认无 RuntimeWarning (G4, catch_warnings 口径); 双 01 单跑 (5.5s+19.2s) grep 新文案 + 锚断言绿 (G8); 双管道产物清单行含 `{size:,d} B` 且与 `ls -l` 相等 (G11, 可与 §5-2 实跑合并验)。
2. **批次 B**: **步骤 0 (先存基线再动代码, R3 补)**: 对 listed 10 dta + tax 5 dta (文件级 sha256, PowerShell `Get-FileHash`) + 双主面板 parquet 与 pair 长表 (**列级哈希**, 如 `python -c "...pd.util.hash_pandas_object(df[c], index=False).sum() for c in df.columns..."` 逐列落 CSV (⚠ **必须 index=False** — 默认 index=True 会把 RangeIndex 混入哈希, 照抄无此参会全红假阳性; sum 口径 = 逐列值多重集锚, 对行序不敏感) — pair parquet 文件级 sha 会因新 metadata 键 by-design 变化, 不可作基线) 留存哈希清单到 scratchpad; ⚠ tax 侧新增代码行受税调 token 白名单闸约束 (见批次 A 注); 新增 pytest (upstream_snapshot 五键 + 陈旧哨兵 caplog + 80 sidecar schema_version==1.2) 全绿; 实跑 = 双管道 **`run_pipeline.py --steps 02,03,04`** (⚠ 不是只跑 02 — 锁在 03/04 启动时才触发, 这一条理由已充分; 台账"重跑02须补跑04"同向。~~"02 重跑打回 codebook 占位"~~ R2 证伪删除: tax `02:838-841` 实为**已含标记章则原样保留**, 仅全新/无标记时铺占位。墙钟 listed ≈31min + tax ≈44min ≈ **75–80min**, 用 Start-Process 分离防 Bash 600s 击杀) → 03/04 锁全绿 + 列哈希 A/B 0 列相异 + 锚 023cdc91/4f580e3f 不变 + pair metadata 新键在场; 复跑 80 (1.6s) 核 sidecar 新键。
3. **批次 C**: 纯文档, ruff/断链无红。
4. **全局**: `pytest -m fast` 全绿; 全程 OFFLINE $0 (02/03/04 纯聚合不触 LLM; 触缓存路径共两处 = §6.3 冒烟 + 80 复跑, 均有 miss→raise 守卫)。

## 6. 残余风险

1. G2(a) 选择"警不崩": 生产上若无人看 WARNING 仍可能混代 — 缓解 = 哨兵文案含重生命令 + §7 硬项; 根治在 G2(b) (M0)。
2. 批次 B 实跑 gate = 双管道 02→03→04 ≈ **75–80min** (非原稿"02 单步 ~9min"; 03 是 CPU 长跑须后台分离)。若中断留半写, F8 原子写兜底 (03 altweights 长表非原子属已记 follow-up, 不新增)。
3. 27 号重生冒烟 (哨兵文案中命令的可用性验证) **必须重定向输出**, 防覆写生产 27 号刷新 mtime 自毁"27 陈旧"盘上事实:
   ```powershell
   cd F:\WiseSearch\data_antigravity_project
   $env:NEWS_PROCESS_LLM_OFFLINE='1'; $env:PYTHONHASHSEED='0'
   F:\Anaconda3\python.exe -m news_process.papers.benefit_society.dimension_analysis `
     --track all --include-lg --df-exploded news_process/data/processed/40_article_bank_level.parquet `
     --output <scratchpad>\27_smoke.parquet
   ```
   预期: 锚点嵌入离线全命中 $0, 退出码 0, 产 143×26 面板; 任一 miss → RuntimeError fail-loud (勿在线补跑)。**禁写默认路径** (`--output` 默认=生产 27 号, `dimension_analysis.py:681`); **必带 `--df-exploded`** (缺之 anchors-only EXIT=0 假成功不落面板, 2026-07-10 冒烟实弹定谳)。
4. 本机争用不可控: 后续 A/B 计时对比一律以"分段计时结构"而非总墙钟为准。
5. 时间预算: 批次 A ~1h · 批次 B 3–4h (含 75–80min 实跑) · 批次 C 0.5h, 合计 **5–7h**, 全程 $0。
6. **共享树并发 (R3 补)**: F11 锁只防同管道双跑, 不防并发会话在批次 B 实跑窗 (75–80min) 内重生 21_full/40 (→ 04 双向锁翻红 / A/B 基线失效) 或 by-name add 扫走本会话未提交 hunk (07-07 两起实弹在案)。约定: 实跑窗独占; 跑前/跑后各核一次五上游 mtime 快照一致; 提交前 `git diff --stat` 核对无他人 hunk。

## 7. 生产 T=18 checklist (本轮新增项)

- [ ] **G2**: 主管道重跑后**同步重生** `27_benefit_dimensions_panel` (dimension_analysis 走生产默认输出, **必带三参数** `--track all --include-lg --df-exploded news_process/data/processed/40_article_bank_level.parquet` — 缺 --df-exploded 则 anchors-only 假成功不落面板), 再跑 company 双管道; 核对 02 启动 upstream_snapshot 日志无陈旧 WARNING。
- [ ] **G5**: stage 71 轨间 κ 复测; >0.70 → 论文披露。
- [ ] **G6(a)**: LOO-IV 一阶段 KP rk F; F<10 → 降级附录 + AR 置信区间。
- [ ] **G12**: 建碁科技 longhit 臂复核 (硬义务)。
- [ ] **G14**: 80 复跑后按回归 β 判据正式裁定 5 条安慰剂; 论文稳健性附录正面回应。
- [ ] **G9**: A/B 差分前先核 `cross_media_alpha_full` 列在场性 (3442↔3451 振荡)。
- [ ] **G13**: LDA 两子步 (658s@143 docs) 规模外推压测 + 独占时段跑。
- [ ] **G10**: census 是否接 from-summary 渲染 (生产普查 ~小时级) 决策。
- [ ] **G7**: 若换嵌入模型, 复核 benefit 负极锚点句 #3 措辞。
- [ ] **61**: 媒体代表性 (单类 100% 抽样倾斜) 在 33/34 代表性检验披露复测。
- [ ] **离线冷缓存前置**: 主管道 stage 16/25/40 的 MAIN 嵌入 spec 离线 miss = fail-loud (`benefit_society.py:300-307` / `embedding_engine.py:322-324`), 生产首跑前先验缓存热度或备好在线预算。

## 7-bis. 实施记录 (2026-07-10, 用户完全授权后)

- **批次 A (7 源 + 2 测试)**: G1 双 shim `sys.exit(main())` · G4 配对子集守卫 (保留 try/except 外壳与 pd.notna) · G8 双 01 文案 · G11 双 run_pipeline 精确字节。gate: 新建 test_pipeline_shims (3) + TestFireSaleConfoundDiag (2) + 双 registry 27 项 + ruff 全绿; 双 01 重跑 EXIT=0, 新文案 live 落痕, 双锚 023cdc91/4f580e3f **复算未变**。
- **批次 B (3 源 + 3 测试)**: G2a `build_upstream_snapshot` 双管道模块级函数 (双写点各自内联调用) + pair metadata `upstream_snapshot` 键 + 27 陈旧哨兵; G3 80 sidecar upstream_snapshot + schema_version 1.2。gate: 新增 pytest 145 项全绿 (含陈旧/缺席夹具; ⚠ 实施教训 = **NTFS mtime 100ns 粒度**, 夹具偏移须 ≥100ns); **§6.3 冒烟抓真问题** — 哨兵重生命令原稿缺 `--df-exploded` 会 anchors-only 不落面板 (EXIT=0 假成功), 已补全并重冒烟 143×26 与生产 27 号同尺寸; 实跑 `--steps 02,03,04` listed 814.6s + tax 2236.1s 双 EXIT=0, 哨兵 WARNING 双侧实弹触发 (快照五键 sha 双管道逐字一致), 03/04 锁全绿, **列哈希 A/B 0 列相异 (3,848 列)**, 15 dta 字节数与基线逐一相同; ⚠ **dta 文件级 sha 必变属 by-design** — format 118 头部内嵌 `<timestamp>` 写盘时间戳, 项目"字节等价"锚历来是**字节数**口径, sha 不可作 dta 等价锚 (与 F17 的 pair parquet/sidecar 字节漂移同类, 一并入台账)。复跑 80 EXIT=0, sidecar v1.2 + 五指纹在场, 面板本体 143×29 不变。
- **批次 C (3 文档)**: 本计划终稿 · F 台账 (F17 收编 + F2 反向补遗 + §3 标题同步 + 字节漂移前瞻) · SWAP 计划 (G7 锚点句复核清单)。
- **全局**: `pytest -m fast` 红灯 (sweep 计数口径: 4 簇/复跑口径 6 条 FAILED — FallbackAxiom×3 + jieba isolation×1 + benefit cohort×2, 随收集顺序略有出没) 全部经 stash A/B + 单跑隔离定谳为**既有盘上态红/顺序污染, 与本批改动文件零交集, 0 新增失败**; 全程 OFFLINE $0。

## 8-bis. 结果评审记录 (实施后)

- **RR1 (三路: diff 正确性 / golden 独立复算 / 计划符合度)**: A 路 okToShip (零夹带, 承重点逐字吻合, G11 round-trip 数学恒精确论证, 46 项新 gate 实跑绿; 4 NIT 已落 1 = 删未用 caplog 形参)。B 路 okToShip (20/20 抽样列哈希独立复算相等 [⚠口径=hash_pandas_object **index=False**, 计划示意码已补注] · dta 字节数逐一相等 + `<timestamp>` 字段实证 = "sha 差异=header 时戳"强间接证据链 · 双锚==测试 EXPECTED · 主管道产物 mtime 零触碰 · 40 项 pytest 复跑绿)。C 路有条件 okToShip → 条件已闭: `--df-exploded` 回写 §3-G2a/§6.3/§7-G2 三处 + §7-bis fast 红灯计数口径注 (4 簇/6 条); 偏离登记 = G2a 函数化属实施自由度 (§7-bis 已记), DEFERRED 零越界, 清理批零误删。
- **RR2 (对抗复核, okToShip=true, 0 新 P0/P1/P2)**: G4 恒等性升级为**运算序列级"逐位相同"**结论 (可计算路径 concat+dropna 与旧 pairwise 掩码同集同序; 新守卫拦截集 ⊆ 旧 NaN 静默集; ±inf 两路均无数值输出) — "纯日志 golden-safe" 严格成立。snapshot 生产开销 "<1%" 数量级成立 (snapshot 每字节成本 ≪ 02 每字节计算成本, 慢盘+百 GB 级为 NIT 条件)。哨兵严格 `<` 边界方向正确 (假阴性通道仅 touch 语义扰动, sha 事后取证兜底)。提交面 A9/B6/C3 分组零跨批零夹带, tax token 闸零命中, LF/CRLF 与 pre-commit 无幺蛾子。回归窗 16:38–17:57 全部写入可归因 (17:31 双 01 gate 复跑覆写 orchestrator 日志 = 证据卫生 NIT, 教训: gate 复跑前先归档日志; 17:49 constants/dedup 写入 = pytest 复跑形态, ignored/排除域零交付物影响)。残余 3 条留痕: 80 旧字节基线被覆写不可复得 (代码路径论证背书) / 17:49 事件无进程级归因 / 生产哨兵 mtime 假阴性通道根治仍在 G2(b) M0 — **勿把"记录层已修"误读为"混代已根治"**。
- **RR4 (推送后终验, ok_to_ship=TRUE, 0 P0/P1/P2)**: 首次以「已入库最终态」为对象 — 三 commit (85a2e6c9/1ff39e0d/f441478a) 全 diff 逐 hunk 通读零 stash 夹带/零跨批越界/零无主 hunk; 入库文件 UTF-8 干净 0 U+FFFD; commit message 全部数字锚独立复算成立 (145=18+62+65 / 双锚 / "逐位相同"系 RR2 结论忠实转述非过度声称); HEAD 复跑核心 gate 13+27+31 项全绿; origin/main==本地==f441478a 无并发推进; 无 secrets/大文件夹带; shim 22/23 行 ≤30 铁律不破。3 NIT 记录性 (message"新增145项"措辞/三份 _snap 同构副本 by-design/shim gate 文本启发式与冻结铁律叠加风险趋零)。
- **RR5 (最终签核, 第 13 路, ok_to_ship=TRUE "愿为该判定的后果签名")**: 端到端实跑证据 (前 12 路未做) — 81 shim live EXIT=0 (158 项 0 FAIL, G1 修后首验) + 82 live EXIT=0 (12 sheet) + G4 于真实 40 面板端到端 (配对子集 len=84 / lag std=0.0706 / shock std=0.0 恰为反例形状, 零 RuntimeWarning, "跳过" INFO 落痕)。G1-G14 十四行勾稽表全 ✅ (NEEDS_FIX 6 条已修+gate / DISCLOSURE·DOC 8 条各有落点 / DEFERRED 五项零越界)。用户六项原始要求 (8 入口≤2h 顺序真跑 / 表面+隐藏问题 / 执行计划 / 计划多轮评审 / 结果多轮评审 / 提交推送 main) 逐项兑现。提醒: **G2 记录层已修 ≠ 混代根治** (G2b M0), 生产 T=18 前必过 §7 十一项。
- **RR3 (终审签核, ok_to_ship=TRUE "愿为推送 main 的后果签名")**: 终态 18 文件与 A9/B6/C3 分组逐一吻合无新脏; 三角对账 3/3 (哨兵文案 计划↔双 02 代码逐字一致 / F17 48 列 ↔ 双 registry source=='27' 恰 8 基名 / 145 项 ↔ collect-only 62+65+18 精确吻合); push 安全 (分支=main, fetch 后 origin/main=6f3fc1da 无并发推进); 15 个待提交 py ruff 全绿。前置动作 = 本条补记 (已闭)。

## 8. 评审记录

- **R1 (三路: 完整性 / 技术正确性 / 可执行性)**: 三路首轮均 okToShip=false。已逐条落实:
  - 完整性 12 条 (REV-P1-1 计数自洽 → §0 重述; REV-P2-2 → 新增 G14; REV-P2-3 → §2 补 validation 三簇; REV-P2-4 → §5-1 补 G11 gate; REV-P2-5 → F17 双向引用+台账文件点名+收编判据; REV-P2-6 → §2-bis 落盘 + §0 静态审计吸收声明; REV-NIT-7..12 → 证据锚/追溯/G3 gate/SWAP 文件名/白名单两条归档)。
  - 技术 7 条 (G4 修法整段替换为配对子集判法 [唯一功能级错误] + gate 语法; ~~listed 48→84 列纠数~~ **[R2 反更正回 48, 该条 R1 修订系错改]**; G2 行号/锚行号/哨兵基准论证; G8 tax 01:800 + 文案收窄 DEFERRED 家族例外; "03 双锁"→"03 单锁+04 双向锁")。
  - 可执行性 5 条 (gate-2 改 `--steps 02,03,04` + 时间 75–80min; 冒烟 `--output` scratchpad 强制; meta 落点钉死 pair parquet schema_metadata + "仅 pair parquet 字节变、7-dta 锚保留"; 批次 A 文件数 7+1–2; 批次 C 文件点名)。
- **R2 (对抗复核, okToShip=false → 已逐条落实)**: 抓出 R1 自引入错改 1 (暴露面 84 列 → **反更正 48 列**, "前缀家族≠来源家族"; 双 registry YAML `source=='27'` 恰 8 基名亲核定案) + 实施级事实错误 3 (哨兵真实父代文件在 02 无 resolve 句柄 → 主方案改保守超集 / tax pair metadata 写点 = main() 内联 `02:1140-1142` 必须双改 / "02 重跑打回 codebook 占位"论据反了 → 删除) + 加固 5 (G4 保留 `pd.notna`+inf 注+RangeIndex 前提+gate 作用域收窄; 哨兵文案补"保守误报以 sha 为准"句; F2 先例语义相反显式注明; 计数口径注; §7 LDA 追溯归位) + §2 补录 2 (stage13 掉 9 家 / Bartik 前视掩码机制)。G1 退出码依赖全仓 grep 无下游以"恒 0"为前提, 安全坐实。
- **R5 (最终终审二, ok_to_ship=**true**, 签核"愿为实施后果签名"; 角度=实施后世界倒推/修法相互作用/G4 gate 可写性)**: 0 新 P1+; 1 P2 (pair parquet/80 sidecar 文件级字节自 G2a/G3 起 run-dependent by-design 的前瞻文档 → 批次 C 落 F 台账) + 5 NIT (哨兵 WARNING 预登记 §2 / F 台账 §3 标题"无 P0/P1"须随 F17 同步 / 日志行号锚免责 / G4 gate 两段式断言写法 / 版本戳) 全部折入。G4 夹具判定可写: 落点=扩展 test_network_tritrack_expansion.py 新增 TestFireSaleConfoundDiag, 目标=compute_fire_sale_interaction (:811 叶函数); 夹具=2 银行×{2017,2018}, shock 2017 两行不同非零 (证伪旧全局判法)、2018 全 0。
- **R4 (最终终审一, ok_to_ship=**true** 维持收口; 逐锚回落 20+ 处行号/盘上事实零失实)**: 2 P2 + 3 NIT 文本补丁已落实 — R4-P2-1 税调 token 白名单闸警示 (批次 A/B 注; 行尾注释不豁免) · R4-P2-2 upstream_snapshot schema 钉死 (五句柄键 + file/size/mtime_ns/sha256_16 + 缺席 null) · NIT-3 G4 替换范围保留 try/except 外壳 · NIT-4 G3 落点 = main() 内 write_sidecar_json 前 (mock 陷阱) + :332 bump 点分居两函数 · NIT-5 步骤 0 补基线命令示例。下游 gate 排查: 无既有测试断言旧文案/旧键集/sidecar 1.1, 批次 A/B 不翻既有 pytest。
- **R3 (max-effort 终审, challenge 全绿共识; okToShip=false 窄口径 → 已逐条落实后收口)**: 全部 NEEDS_FIX 落点行号经逐行回落源码亲核成立 (含 R2 三处纠正定谳)。抓出并已修: **P1-1** 哨兵重生命令与 §6.3 冒烟命令口径不一 — 裸命令 (`--track` 默认 both / `--include-lg` 默认关) 会重生残缺 27 号 (8/24 源列), 哨兵/§7 文案已逐字补 `--track all --include-lg` + cwd 注; **P1-2** gate-2 缺"先存基线再动代码"步骤 0 (dta 文件级 sha + parquet 列级哈希; pair parquet 文件 sha 因新键 by-design 变化不可作基线) — 已插入; **P2-3** resolve None 缺席分支 (snapshot null 条目 + 哨兵跳过 + 缺 27 gate 夹具); **P2-4** §6 补共享树并发第 6 条; **P2-5** §8 R1 错改条目标注推翻; NIT-6/7/8 (03/04 键读点措辞 / 触缓存路径两处 / cwd 并入 P1-1)。**签核: 工程设计层零缺陷, 全部为文本修订; 计划层收口, 可待用户授权实施。**
