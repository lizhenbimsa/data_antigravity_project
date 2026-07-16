# 五入口顺序执行 — 再验证与整改执行计划 (2026-07-10 · 修订版 R1)

> 日期 2026-07-10 · HEAD **156af8c1** (dir-move 收尾后**首次**全链再验证) · 环境 OFFLINE+确定性 (NEWS_PROCESS_LLM_OFFLINE=1 / HF_HUB_OFFLINE=1 / TRANSFORMERS_OFFLINE=1 / PYTHONHASHSEED=0 / MKL·OPENBLAS·NUMEXPR·OMP_NUM_THREADS=1) · 解释器 F:\Anaconda3\python.exe (conda base 3.13.9)
> 五入口顺序 (用户指定): ① run_pipeline_function → ② run_pipeline_validation → ③ run_paper → ④ company_listed_bank/run_pipeline → ⑤ company_tax_bank/run_pipeline
> 方法: 真跑 5/5 (含 ③ +3 探针) + 列级确定性复核 + 7-agent 对抗审计 (证伪"全绿") + 独立坐实 + 7 项冒烟闭合覆盖缺口
> **修订 R1 (2026-07-10)**: 已吸收计划三轮最高标准评审 (完整性/技术正确性/可执行性风险) + 首席综合 (okToShip=false → 逐条落实 REV-1..REV-8 后本版)。**核心修订: 原 F1/F2 两项 P1 经评审证伪为"新发现实为已披露刻意决定 / 前瞻风险", 已降级重写; F1 级联 bump 方向纠正; A7 "live 坐实" 过度声称撤回; 计数校正。**
> 前置: 本轮是对 commit **8e0f34df** (五入口 A1-A10+B4 整改) 的**独立再验证**; 前次 5/5 EXIT=0 在 **2eeb65e9 (pre-fix)**, 之后落修复 + 移动 LLMs_for_FinTech_dic → 本轮是 dir-move **之后**首次端到端验证。

---

## 0. 结论速览

- **入口运行**: ①②③④⑤ **5/5 全部真实运行成功 (EXIT=0)**, 0 真 ERROR, 0 traceback, **$0** (LLM+嵌入+BERT 全 OFFLINE 命中; stage21 lookups=13,896 / hits=13,896 / misses=0 / hit_rate=1.000)。
- **A1-A10+B4 计 10 项代码修复** (A1/A2/A3/A4/A5/A6/A7/A9/A10 + B4; **A8 前次已降入 by-design/文档, 非代码修复**) 经 7-agent 对抗审计**逐一在当前源码 (HEAD 156af8c1) 坐实为 ALREADY_FIXED**, 无回归; A1/A2/A4/A5 另经本轮冒烟 live 坐实 (**A7 的产物缺失告警抑制本轮未 live 触发, 仅 pytest gate 覆盖 — 见 §1 冒烟行 / F16**)。**dir-move 对 pipeline 运行真正交** (全仓 pipeline 代码零引用, 词典独立走 config/fintech_dict.json, 仅 packaging find_packages 28→27)。
- **数据层可复现**: 今晨基线 vs 本轮 P1 逐列 value-multiset 哈希, 5 关键 parquet (40_panel 3442 列 / 51 3453 / 16 68 / 21_full 202 / 15 54) **0 列相异**; file-SHA 差纯属 parquet-metadata 噪声, **无确定性缺陷** (行级对齐更强口径见 F15)。
- **本轮无 P0 / 无 P1 阻断或"生产前必修"缺陷; 无新增崩溃**。全部 stage 级 WARNING 经对抗核实均为 **T=2 dev 语料预期退化**或 **by-design 优雅降级** (逐类坐实)。
- **评审证伪了初判 2 处** (本次多轮评审核心价值 — 均是"新发现实为已披露刻意决定/前瞻风险"陷阱):
  - **F1 (原 P1 → 降 P2)**: 税调名单短名假阳性**不是**"从未清理的数据缺陷", 是 codebook §7 L1 **已人工过目、刻意保留、已设缓解** (n_docs_longhit ≥4字稳健臂 + usci 剔除) 的**已披露限制** (与 listed 同口径)。真正可落地的残余 = **生成器 docstring 承诺"下游同银行侧短名过滤" 与 tax-02 实际"刻意不剔除只 surface"不一致** → 建议匹配层补 FP 过滤或据实更新 docstring + 强化披露; **不做无差别 source-clean** (会误删 建发/金地 合法品牌简称)。
  - **F2 (原 P1 → 降 P2)**: cross_media 顺序耦合 (main↔validation + mtime 守卫致标准顺序恒缺列) **属实且值得文档化**; 但"影响第 10 篇主处理变量"是**前瞻风险** — `cross_outlet_tone_variance_full` 在 paper_spec 标"待新建 (M2-M3)", 盘上同名列是 stage 39f 不同口径占位, 当前无活跃回归消费者失败。
  - **F3 (P2)**: company "40 全 NaN 加权列"归因**纠正** — 实为 BERT `nt_iyvol/iytrend`(T≥3)+`_ss`稀疏的 T=2 退化, cross_media 三基名 `emit_tracks=[]` 产 **0 列** (非 NaN)。两独立根因。
- **问题定级 (修订后)**: **P0=0 · P1=0 · P2=10 · NIT=5 (+ F16 覆盖声明, 不单独计严重度)**。逐条: **P2 = F1/F2/F3/F4/F5/F6/F7/F8/F9/F14 (10 项)** · **NIT = F10/F11/F12/F13/F15 (5 项)** · **F16 = 覆盖缺口显式声明 (本轮大部已闭)**。F1-F16 共 16 条, 全部**非阻断**。
- **golden 安全**: **F8** (半写 dta 原子化) 触数据层但字节等价 → **golden 中性/安全**; **仅 F1 方案 (a)** 落 SSOT 清洗才**非 golden 中性** (触 registry/面板重生, 受 M0, 见 §4/§5 carve-out)。其余修复均纯文档/日志/锁层, **golden 安全**。

---

## 0-bis. 实施状态 (2026-07-10 已落地 + 结果评审 R1 通过)

✅ **F1(b)/F2/F3/F4/F5/F6/F7/F8/F9/F10/F11/F12/F13/F14 全部 golden-safe 整改已实施** (11 源码 py + 2 README + `tests/test_papers_bank_fintech_tone_tables.py` 新增 F4 回归断言 + 本计划 md)。
- **静态验证**: `ruff check .` 全绿 · py_compile 全过 · 目标 pytest (company panel/lock + 五入口 hardening + run_paper dispatcher + tables) EXIT=0 (含新增 `test_write_table1_footnote_no_stale_nan_placeholder`)。
- **功能验证 (双 company 再跑)**: company_listed_bank EXIT=0 (锚 **023cdc91** 未变 / dta 字节等价 1,603,484,161 / 0 `.tmp`) · company_tax_bank EXIT=0 (锚 **4f580e3f** 未变 / 三 dta 字节等价 6.85–6.88GB / 0 `.tmp`) → **F8 原子写字节等价、F11/F12/F2/F3 均实证生效、registry 双锚未变 = 无测度/数据值/面板列变更 (golden 安全坐实)**。run_paper `--stage tables`(F4)/`--help`(F5)/function `--help`(F9) 冒烟均 EXIT=0 且新文案实证。
- **结果评审 R1** (3-lens diff: 正确性/golden无回归/完整性 + 首席; okToShip=true, **0 P0/P1/P2**): 深核 F8 temp+Path.replace 原子且字节等价 · F12 无死锁/线程泄漏/rc 语义保留 · F11 锁序铁律不破 · F2/F3 占位匹配 · F4 删的确为 stale 句 · F1(b) 与 tax-02 实现一致。R1 两 NIT 已闭 (F4 加回归 gate · F6 落点据实记录)。
- **F1(a) 刻意 DEFERRED (受 M0)**: 匹配层短名 FP 过滤 + 面板/registry 重生 = 对已披露刻意设计的再评估, 需成本收益论证; **未做 SSOT 清洗 (`company_tax_names.yaml` 零改动)**。
- **提交纪律**: 按文件名 by-name stage, **排除 `data/processed/v3_5_1_constants.json` 并发产物** (CLAUDE.md 提交铁律)。

## 1. 运行结果总览

| 入口 | 结果 | 墙钟 | 关键观测 (证据) |
|------|------|------|-----------------|
| ① run_pipeline_function | ✅ EXIT=0 | 1133s (18.9min) | 16/16 阶段 ✓; stage00=542s(48%)/stage40=298s/stage22=122s; stage21 离线 13896/13896 hit misses=0 $0 (21_tone_llms.log:99); 面板 220×3442 / article 1005×1305 / 51: 220×3453; 16 stage 日志 ERROR=0/TRACE=0 |
| ② run_pipeline_validation | ✅ EXIT=0 | 242s (4.0min) | 16/16 (60-75) ✓; stage72(NMI+null)=178s; 66/70 离线优雅跳过 (单行 WARNING, 零产物, 不污染); 全 16 子日志 ERROR=0/TRACE=0 |
| ③ run_paper (bare + 3 探针) | ✅ EXIT=0 | ~5s | bare catalog: 11 spec 全解析 (0 render 失败), +185 行; p3b `--stage pipeline --dry-run --skip-21-if-exists`: flag 无 SystemExit (A10 坐实); p3c Table1 CSV; p3d Figure1 PDF; 3 探针 0 traceback |
| ④ company_listed_bank | ✅ EXIT=0 | 730.6s (12.2min) | 01=4.2s/02=95.9s/03=629.7s; registry 锚 **023cdc91** 与测试锚一致; git 干净; 7 权面板 dta 各 1.53GB 满尺寸; 4 日志 ERROR=0/TRACE=0 |
| ⑤ company_tax_bank | ✅ EXIT=0 | 2397s (40.0min) | 01=20.4s/02=281.7s/03=2094s; registry 锚 **4f580e3f** 与测试锚一致; git 干净 (13GB dta 正确 gitignore); 双引擎 city(15.0M行→447710×1901)+county(7.97M行→447710×1902); 三 dta 各 6.85-6.88GB 满尺寸; 锁净释放; 4 日志 ERROR=0/TRACE=0 |

**冒烟闭合覆盖缺口 (7/7 EXIT=0)**: validation --help(347B,不获锁) · validation --dry-run(1511B,"未获锁未实跑") · function --help · run_paper --help · tax --dry-run(**err=0B, 无 emoji 崩 + dry-run 只打印命令未注入 env = A1/A4 坐实**) · tax --no-emit-dta --dry-run(**仅坐实 flag 解析+透传; A7 的 dta 缺失告警抑制在 :530 `_log_step_done`, dry-run 于 :495 `continue` 短路未触达 → A7 告警抑制本轮未 live, 仅 pytest gate 覆盖, 见 F16**) · listed --dry-run; 全程无 `.pipeline.lock` 残留 (A2/A5 语义坐实)。

---

## 2. 正向坐实 (对抗审计未能证伪; 予以确认)

1. **A1-A10+B4 计 10 项代码修复 ALREADY_FIXED** (audit:fixes 逐行核; **A8 非代码修复**): A1 兜底 handler backslashreplace+try/except (tax:47-65/listed:38-55) · A2 validation argparse (:299-321) · A3 RUN_ID emit 下沉 (function:620/validation:173) · A4 dry-run env 下沉 continue 后 (tax:495-518) · A5 锁 acquire 先于 init + try/finally (tax:390-406/listed:365-381) · A6 子进程确定性 env (tax:502-507/listed:472-477) · A7 --no-emit-dta dta 守卫 (tax:197/208/220) · A9 os.write 失败清理 (tax:110-120/listed:99-109) · A10 flag 透传全链 (run_paper:687/748 + 11 家 analysis parse_known_args + pipeline_runner:21-36) · B4 _stage21_skip 按 _full 后缀 (function:396-401)。
2. **dir-move 正交** (audit:fixes): grep 全仓 pipeline 代码对 `LLMs_for_FinTech_dic` 零命中; 目录内脚本 `Path(__file__)` 自定位; pyproject setuptools/ruff exclude 已更新新路径; 词典独立走 config/fintech_dict.json。
3. **stage21 离线零成本零 API**: 13896/13896 hit, writes=0; stage48_llm_peer_iv 36 次亦纯缓存。
4. **产物完整**: OUTPUT_REGISTRY 全部登记产物 (22 parquet + 46_stata 的 dta/do/xlsx) 磁盘实存本轮 mtime; 面板 dta round-trip 无丢行; 漏斗 1650→1544(93.58%)→1005 一致。
5. **company registry 双锚稳定** (023cdc91/4f580e3f), dta 满尺寸无半写, 双/七引擎全非空, 跨年去重键不含 year, 覆盖 SystemExit 闸全过。
6. **数据列级可复现** (今晨≡P1, 5 文件 0 列相异)。
7. **63 demo_mode 合成标注隔离优秀**: 双醒目 WARNING『严禁引用进论文』+ 全产物 `_DEMO` 文件名。
8. **披露纪律扎实**: BERT/LLM Cronbach α<0.70 显式标『需改进』; 人工验证 pending 显式声明『不得宣称顶刊效度』。

---

## 3. 问题清单 (经对抗审计 + 三轮评审证伪修订; 本轮无 P0/P1 — **F17 为 2026-07-10 八入口审计后补 P1**, 见 F16 之后)

> 图例: verdict∈{NEEDS_FIX 建议修 · RE-EVAL 再评估 · DISCLOSURE 论文/复现披露 · DOC 文档}; golden: 安全=不触测度/缓存/确定性。

### F1 · [P2 · RE-EVAL/DISCLOSURE] 税调名单短名假阳性 = 已披露刻意保留限制; 唯一残余 = 生成器 docstring 与 tax-02 实际口径不一致
- **事实 (已独立坐实, 属已披露)**: `config/company_tax_names.yaml` 部分企业 variants 含 ≤2 字通用/截断 token (建碁科技 含裸 `"科技"` + 截断 `"科技（中山）有限公司"`); tax 02 报单企业占 full 轨共现 67.9% (668/984)。**codebook §7 L1 已全量披露**: `02_...cooc_panel.py:793-808` 明载"2 字 variants 32 条全量人工过目 (含 科技/电脑/空中/商检, 源自简称列) — 维持不裁剪口径 (**与 listed 一致**), 分析端可按 usci 剔除受污企业行"; 分层精度 ≤2字≈0.71 / 3字≈0.76 / ≥4字≈0.92; "不裁剪只披露, 稳健工具 = **n_docs_longhit** (≥4字命中臂)"。
- **评审证伪 (撤回原 P1 定性)**: 原 F1 断言"从未清理 / listed 已清税调未清 / §7 只禁运行时过滤"**三点均被证伪**: (a) `generate_company_tax_names.py:27-32` "已知非问题(刻意保留)"明写 2 字超短简称 (建发/金地) **刻意保留**; (b) codebook 明载"与 listed 一致" — 两名单同为不裁剪口径, listed 的 iFind 清理针对 OCR 碎片非通用简称, "listed已清税调未清"是**伪平行**; (c) 我方"32 家≤2字/52 家≤3字"扫描实为**复算** codebook 早载的"2字32/3字21"(且 52 系口径误差, 应为 32+21=53 或"3字21")。**无差别最短长度门会误删 建发/金地 类合法品牌简称** — 反引入数据质量缺陷。这正是记忆警示的"改前必读 codebook§7 局限, 多数新发现已披露"陷阱。
- **唯一可落地残余 (真 P2)**: `generate_company_tax_names.py:27-32` 承诺"下游实体匹配自行做短名防误报 (**同银行侧短名过滤口径**)", 但 tax-02 匹配层 (`02:1165` "设计刻意不剔除, 仅 surface — 对冲工具 = n_docs_longhit + codebook §7 L1") **并未实现**该短名 FP 过滤 (银行侧有 `bank_name_exclusions.json` 否定+短名过滤; 税调侧无等价)。即**生成器 docstring 声称的下游缓解 与 02 实际选择 不一致**。
- **修复 (二选一 + 披露)**: (a) 在 tax-02 匹配引擎补短名假阳性过滤 (兑现 docstring 承诺, 对齐银行侧口径) — 触匹配层/面板重生 (见级联); **或** (b) 更新 generator docstring 据实反映 tax-02 的选择 (surface + n_docs_longhit 稳健臂, 非硬过滤) + 强化 canonical(n_docs) 污染的**复现披露** (论文须以 n_docs_longhit 为稳健主测度或 usci 剔除受污行)。**均不做无差别 source-clean**; 若确要针对**真截断碎片** (如 "科技（中山）有限公司" 丢 建碁 前缀) 做定向源清洗, 须: 通用词/截断碎片黑名单 + 合法品牌白名单豁免 + 清洗前后合法短名保留率人工抽检 + 与既有 longhit/usci 缓解的成本收益论证。
- **级联 (纠正, REV-2)**: 清洗**非银行系**企业 variants **不 bump** `EXPECTED_TAX_REGISTRY_SHA256` — 结构锚 (`01:321 registry_content_sha256`) 只压 `entries`(特征列, 源 16/21/27/51)/`bank_company_map`(仅 280 家银行系企业吃 variants)/`excluded`/`dv2_constants`, **meta 刻意不入锚**。真正翻红门 = `test_name_list_hash_anchor` (比对盘上 yaml 与 `meta.company_names_sha256`), **靠重跑 01 (廉价 20.4s) 自动复位**; "02 pair 指纹"= 同一 `meta.registry_sha256` **非独立第三项**; DV2 双向锁与 variant 清洗**正交**。⚠ panel 单测用合成 fixture (甲税企/乙税企) **不锁真实 cooc 数值** → 清洗的数据层效果**无 gate 兜底**, 若落清洗须**新增数据层回归 gate** (如断言无 ≤2字截断 variant / 单企业占比<阈值)。
- **优先级**: P2 (非阻断; 既有 longhit+usci 缓解已在位)。方案 (b) 纯文档 golden 安全; 方案 (a) 触匹配层+面板重生 (受 M0)。

### F2 · [P2 · DOC] cross_media 顺序耦合 (标准顺序恒缺列; paper-10 影响为前瞻风险)
- **机制 (源码+mtime 链坐实)**: `core/dag.py:316` stage40=group **main** / `:459` stage75=group **validation**; `runner.py:400-410` mtime 新鲜度守卫 (75 早于登记上游 21 → 跳过 cross_media merge)。main 每跑必先重生 stage21 → stage40 建面板时盘上 75 恒早于刚生的 21 → **恒跳过**。本轮 mtime 链 21_full@22:27 → 40@22:35(守卫触发) → 75@22:42。**非 T=2、非生产可恢复** — 任何 `main→validation→company` 顺序恒缺 cross_media 三基名。
- **评审校准 (REV-5, 降 P1→P2)**: `cross_outlet_tone_variance_full` 在 `papers/bank_media_disagreement/paper_spec.yaml:87` 标 **"待新建 (M2-M3)"** (尚未构建进流水线), 盘上同名列是 stage 39f **不同口径**占位 (:88-95 已披露)。故 paper-10 复现阻断是**前瞻/潜伏风险** (待该变量按 spec 口径建成后受此耦合制约), **非当前活跃回归失败**。company 日志"生产 T=19 上游全列重生后减少"对 cross_media 子集**误导排障方向**。
- **修复 (纯文档/日志 golden 安全)**: (1) 文档化 canonical 顺序 (主线+company README): 需含 cross_media 列的完整面板须走 `①function → ②validation → ③单独补跑 40_panel_export_main.py (不重跑21) → ④⑤company`; 替代 = 主线 `--skip-21-if-exists`。(2) 纠正 company 侧对 cross_media 子集的"T=19 恢复"误导文案 (改为"main↔validation 顺序耦合, 须按 §5 顺序或补跑 stage40")。(3) 可选 runner.py skip WARNING 升为运行末尾醒目摘要行。(4) DEFERRED (不建议): 提升 cross_media 为主线阶段 / 放宽守卫。
- **反向补遗 (2026-07-10 八入口审计 G9)**: validation 重生 75 后其 mtime 晚于 21 → **下轮单独重跑 stage 40 时守卫必放行, cross_media +9 列并入 (3442→3451)**; 下轮全主线重跑 (21 重生) 又跳过回落 3442 — 面板列数随"跑法"在 3442↔3451 间**振荡**, schema 不再是 stage 40 自身输入的纯函数。**A/B 差分 SOP: 比较前先核 `cross_media_alpha_full` 列在场性**, 9 列差异勿误判回归 ("validation 后单跑 40 = +9 列属预期, 全主线重跑 = 回落属预期")。并入侧安全性有守卫兜底 (重复键 fail-loud / 行数断言 / 只并新列)。

### F3 · [P2 · NEEDS_FIX/DOC] company "40 个加权列全 NaN = 缺源列" 诊断误标 (两独立根因)
- **证据 (实读 parquet 坐实)**: 40 个全 NaN 列**全部**为 `cw_/ce_{finbert_cn,fin_sent_zh,finbert2}_nt_{iyvol,iytrend}_{full,ctx,ss}` (36 列, 需 T≥3 且 ≥6 有效月, dev T=2 全 NaN 属预期) + `cw_/ce_{neg_sub_ratio_ss,washing_asymmetry_ss}` (4 列, ss 轨 T=2 稀疏)。cross_media 3 基名 registry `emit_tracks=[]` → 实产 **0 列** (非全 NaN)。**纠正了初判 RUN_NOTES 的 "40 NaN = cross_media 传导" 错误归因。**
- **修复**: 拆分 02 WARNING/⑥ 文案为两类 (BERT T=2 时间深度 → T=19 填充 / cross_media emit_tracks=[] → 顺序耦合见 F2)。**设计裁定 (回应 audit "核对是否落占位列", REV-8)**: cross_media 三基名属 GAP_UNPLANNED/待新建, **刻意不落全 NaN 占位列以免污染 schema** (故 01 "按缺列容错出全 NaN 列" 对 emit_tracks=[] 基名措辞须校正为"实际不产列"); 若为 T=19 级联审计可见性需要, 另行评估落显式占位列的利弊。golden: 安全 (纯日志文案)。

### F4 · [P2 · NEEDS_FIX] tables.py 硬编码脚注声称 ft_vol_* 为 NaN 占位, 与实产 CSV 真实值矛盾
- **证据**: `papers/bank_fintech_tone/tables.py:113-120` 无条件脚注末句 "ft_vol_* are NaN-placeholder until the panel is rebuilt"; 产物 `table1_summary_stats.csv` 中 `ft_vol_yr`(N=220, Mean=5.9555) / `ft_vol_prov`(N=194, Mean=4.1573) 均真实非-NaN。误导审稿人。
- **修复**: 删除/据实改写末句; 或改为按列 `isna()` 动态判定后有条件追加 (避免面板状态漂移致脚注永久失真)。golden: 安全。

### F5 · [P2 · NEEDS_FIX] parse_known_args 使拼错的流水线 flag 在 dry-run/tables/figures 路径静默吞掉
- **证据**: `run_paper.py:687` + `analysis.py:54` 逐层 parse_known_args; 严格校验只在真跑路径 (`run_pipeline_function.py:545`) 发生。--dry-run (analysis.py:68-72 提前 return) 与 --stage tables/figures 下拼错 flag 被静默吞并 exit 0。真跑路径仍 fail-loud, 隐患有限 (A10 已知轻微回退)。
- **修复**: (可选) run_paper/analysis 层维护透传 flag 白名单; 或 --dry-run 也把 _extra 过 _parse_cli_args 纯校验; **至少**文档/--help 明示"拼错的 pipeline flag 仅在真跑时报错"。golden: 安全。

### F6 · [P2 · NEEDS_FIX] 离线 66/70 无产出的复现披露义务未落实 (II-1)
- **证据**: grep 全仓 md, `entity_masking|prompt_sensitivity` 仅在 scripts/audit/* 与 CLAUDE.md, papers replication README / AI_DISCLOSURE_TEMPLATES.md 零记载。
- **修复 (已落地 2026-07-10)**: 披露已加进 `run_pipeline_validation.py` 顶部 docstring "复现/离线注意" 段 (dev 入口, 可提交落点)。⚠ 终端受众的**复现包 README / data appendix** 因 `papers/**/*.md` 被 `.gitignore:132` 忽略 + 由 `stata_runner build-replication` 生成, 无 committed 模板可直改 → **follow-up: build-replication 生成复现包时须把 66/70 在线付费披露带入 README/data appendix**。golden: 安全。

### F7 · [P2 · NEEDS_FIX] 跨管线锁互不感知 (company 单实例锁 vs 主管道 PipelineLock)
- **证据**: company 锁只护自身 `logs/_run_pipeline.lock`; 对 `data/processed/.pipeline.lock` 零引用; 反之亦然。company 只读 40/51/27/16/21_full, 主管道收尾有 os.remove+非原子重写窗口 (诊断曾遇 WinError 2)。
- **修复**: (a) company README 补"派生管线须在主管道空闲时运行"串行纪律 + "listed×tax 可并发"说明; (b) 可选 company 启动读 `.pipeline.lock` sidecar PID 做**存活判定**。仍无法消除"company 先读→主启动"窗口。golden: 安全。

### F8 · [P2 · NEEDS_FIX] 半写 ~6.85GB dta/parquet 崩溃安全缺口 (前次诊断计划 §7-2, 可从 DEFERRED 提升)
- **证据**: company 02/03 `pyreadstat.write_dta(...)` 与 `to_parquet(...)` 均**就地写**, 无 temp+rename。长跑 03 被 kill 留半写供 Stata 误读 (2026-07-07 branchw 688MB 半成品实弹)。单实例锁只防并发, 对单跑 kill 无保护。
- **golden 再评估 (评审确认成立)**: dta 头本嵌时间戳 (dta 字节 SHA 逐次漂移, golden gate 走 registry sha/列内容哈希非 dta 字节), 故 `out.dta.tmp` + `os.replace()` (Windows 同目录原子) 最终字节与就地写**等价**, 实质 **golden 中性** (且 replace 落在 write_outputs 内、future.join 前, 与 03 WP-S2 后台写盘不冲突)。
- **修复 (已落地 2026-07-10, 限 02/03 write_outputs)**: temp + `Path.replace` 双文件 (dta+parquet); 运营纪律 = 长跑 03 前台/nohup + "中断=产物不可信须重跑"。golden: 安全 (字节等价, 双 company 再跑坐实)。
- **follow-up (R2 结果评审观察, 超本轮 F8 声明范围)**: 03 的 altweights pair 长表 (`_company_*_altweights_*.parquet`, 诊断/重构用, **非** Stata 主回归消费的面板 dta) 仍为就地写; 03 长跑中途 kill 会留半写但下轮覆写, **低风险**。若追求 03 全写点崩溃安全, 后续可将这两处 `to_parquet` 亦改为 temp+`Path.replace` 与 write_outputs 对齐。

### F9 · [P2 · NEEDS_FIX] --skip-unchanged 开启时 stage40 漏检 75 变更 (F2 同族盲区)
- **证据**: stage40 登记在 `run_pipeline_function.py:179 STAGE_CONFIG_FILES`; 但 75 从不作为 stage40 输入被记入 input_hashes → 验证阶段重生 75 后以 --skip-unchanged 重跑主线时 stage40 被静默跳过 → 面板永久保留旧/缺 cross_media, 连 mtime 守卫都不执行。默认关 + 前缀守卫掩盖严重度。
- **修复**: 文档化 (--skip-unchanged help + README): "使用 --skip-unchanged 时 opt-in 特征列 (cross_media/staleness) 可能保留陈旧值"。与 F2 合并。golden: 安全。

### F10 · [NIT] 66/70 离线跳过遗留旧产物无新鲜度标记
- **证据**: `eval_reports/entity_masking_*` mtime=07-06, 本轮 66 跳过未覆写 → 可能误当本轮结果。对比 63 的 _DEMO 纪律, 66/70 缺护栏。validation-only 不入面板。
- **修复**: (可选) 66/70 skip 时落 `*_SKIPPED.txt`; 或文档记"新鲜度以 mtime 为准"。golden: 安全。

### F11 · [NIT] company 单实例锁 acquire/release 成功路径无 INFO 日志
- **证据**: company run_pipeline.log 无单实例锁 acquire/release 记录; "锁干净释放"仅靠 dta 完整性反推。
- **修复**: 锁成功获取/释放各打一行 INFO。golden: 安全。

### F12 · [NIT] company 编排器不转发子进程 stderr 进自身 .log
- **证据**: `company_*/run_pipeline.py:520 subprocess.run` 无 stdout/stderr 捕获 → 子步原始 stderr 只进本会话 capture, 不进 company .log (主线/验证经 `core/stage.py:319` 有转发)。故 ④⑤ "0 traceback" 权威 .log 无法覆盖子进程原始 stderr, 须靠 capture 佐证 (本轮 capture UTF-8 直读已证 0)。
- **修复**: company 编排器对齐 core/stage.py 转发子进程 stderr 进 run_pipeline.log。golden: 安全。

### F13 · [NIT · BY_DESIGN] BLAS 线程=1 仅靠 shell 约定
- **证据**: `core/stage.py:239-255` 只强制 HASHSEED=0, 无 BLAS 注入。刻意不对称 (BLAS=1 setdefault 对生产重数值 stage 有性能代价)。
- **修复**: 纯文档 (golden-regen SOP 明列全 BLAS 钉 1 + M0); **勿盲加 setdefault BLAS=1**。golden: 安全。

### F14 · [P2 · DISCLOSURE] stage64 揭示 LLM 两家近同质 + 覆盖率非单调 (论文披露, 非代码 bug)
- **证据**: `64_tone_validation.log:191` gpt54nano vs gemini31 JSD=0.0003780 "高度同质化(多数投票退化风险)"; `:176` 覆盖率非单调 Δα=-0.3184。均 T=2/1005 篇小样本。
- **修复**: 论文方法学章 (若引用 stage64) 披露多数投票两家近同质 + 覆盖率非单调, 以生产 T=19 复核为准。**代码无需改动。** golden: 安全。

### F15 · [NIT · METHODOLOGY] 确定性判定用列 value-multiset 哈希掩盖行序/跨列错位
- **证据**: 列 multiset 哈希对行序置换不变, 无法发现跨列逐行错位; "含 BLAS 列 0 相异"与文档化 ~45 列 BLAS 漂移未对账 (今晨线程钉设未知)。
- **修复 (后续复现验证纪律)**: 改用按 `(target_bank, year)` 排序对齐后的**行级哈希**, 或对 9 个已知 BLAS 列逐行 diff, 并对账。**注**: 本轮"数据可复现"结论在 multiset 口径下成立 (0 列相异); 行级为更强主张的收敛。golden: N/A (验证方法)。

### F16 · [COVERAGE · 本轮大部已闭 · 不计严重度] live 覆盖缺口 (显式声明)
- **本轮已 live 闭合** (冒烟): A1/A2/A4/A5 (A5 = --help/--dry-run 不获锁, 语义坐实)。
- **仍依赖 pytest gate (非本轮 live, 须显式声明非全覆盖)**: **A7 完整 --no-emit-dta RUN 的告警抑制** (dry-run 短路未触达) · lock-race 并发双跑 (破坏性) · --skip-unchanged 真跑 (会改 data) · run_paper --stage all 全量 paper。**验收记录须显式声明"上述路径依赖 `tests/test_five_entrypoint_hardening_2026_07_09.py` + 两 lock 测试 CI gate 覆盖, 非本轮 live 触发"**。golden: 安全。

### F17 · [P1 · 收编自 2026-07-10 八入口审计 G2 · 记录层已修] company 双管道 input_fingerprint 只锚 21_full 的"尺寸|行数"; 40/51/16/27 不入锚 — 27 号混代实弹
- **完整台账与证据链**: 见 `scripts/audit/EIGHT_ENTRYPOINT_SEQUENTIAL_RUN_AUDIT_AND_REMEDIATION_PLAN_2026-07-10.md` §3-G2 (八路评审收口)。要点: `27_benefit_dimensions_panel.parquet` 唯一生产者 = `papers/benefit_society/dimension_analysis.py` (标准八入口顺序不重生它), 2026-07-10 真跑实弹混代消费 07-03 旧代 27 号 — 暴露面 = registry `source=='27'` 8 基名 × 3 轨 = 24 源列 → **48 列/管道** (⚠ 勿按 `cw_/ce_benefit_*` 前缀计数=84, 其中 36 列源自 40/51 同代), 锁链全绿不报警。
- **已修 (记录层, 2026-07-10)**: 双管道 02 加 `build_upstream_snapshot` (五上游 `{file,size,mtime_ns,sha256_16}` 入日志 + pair parquet metadata 新键 `upstream_snapshot`; 03/04 按键点取不受影响, 锁不翻, registry 双锚不 bump) + 27 号新鲜度哨兵 loud WARNING (警不崩, 文案含完整重生命令 `--track all --include-lg --df-exploded …`; **dev 上该 WARNING 属常态预期, 日志审计勿立案**)。硬锁层 (五上游并入 fingerprint 本体) DEFERRED 受 M0。
- **⚠ 字节漂移前瞻 (by-design)**: snapshot 含 `mtime_ns` → 自此 pair 长表 parquet 与 80 sidecar 的**文件级字节随上游 mtime 漂移**; A/B 复现验证一律用**列级哈希** (pair) / 排除 `upstream_snapshot` 键后的 JSON 比对 (sidecar); 15 份面板 dta 与主面板 parquet 数据字节不受影响, 字节锚保留。

---

## 4. 修复批次建议 (按优先级 + 独立提交)

- **批次 A (再评估 + 文档, P2 无阻断)**:
  - **F1** (先决: 与 codebook §7 L1 / generator docstring 对账): 方案 (b) 纯文档 — 更新 generator docstring 据实 + 复现披露 canonical 污染须用 n_docs_longhit/usci 剔除 (golden 安全, 优先); 方案 (a) 匹配层补短名 FP 过滤 (触面板重生, 受 M0) 作为 RE-EVAL 备选 — 须先给"既有 longhit/usci 缓解为何不足"的成本收益论证。**不做无差别 source-clean**。
  - **F2** cross_media 顺序耦合: 文档化 canonical 顺序 + 纠正 company 误导文案 + (可选) runner.py 末尾摘要行 (纯文档/日志)。
- **批次 B (诊断文案/文档, P2, 全 golden 安全)**: F3 (40-NaN 拆因 + 占位列设计裁定文案) + F4 (tables.py 脚注据实/动态) + F6 (66/70 复现披露) + F9 (--skip-unchanged 盲区文档) + F14 (stage64 论文披露注)。
- **批次 C (锁/并发/崩溃安全, P2/NIT)**: F7 (跨管线串行纪律 + 可选 sidecar PID 守卫) + F8 (dta temp+os.replace 原子化, 字节等价 golden 中性) + F11 (锁 acquire/release INFO) + F12 (company 转发子进程 stderr)。
- **批次 D (CLI/元, P2/NIT)**: F5 (透传白名单/文档) + F10 (66/70 陈旧产物护栏) + F13 (BLAS 文档) + F15 (行级确定性验证纪律) + F16 (覆盖缺口显式声明)。
- **验证升级为 gate**: F4 文案改动加最小 pytest 断言 (脚注与 isna 一致); 若 F1 走方案 (a) 落数据层清洗须新增数据层回归 gate (panel 单测用合成 fixture 不锁真实 cooc, 无兜底)。
- **golden/执行边界**: 批次 B/D 全 golden 安全可先行; 批次 C 的 F8 字节等价 golden 中性; **F1 方案 (a) 与其面板重生受 M0 审批门** (dev 阶段可先落 generator docstring/披露文档 + 若清洗须**同步重跑 01 廉价 20.4s 复位 company_names_sha256 自洽门**, 昂贵 02/03 面板重生 DEFER 到生产)。

---

## 5. 残余风险

1. **F1 生产 canonical 污染是已披露既定权衡**: 项目立场 = 不裁剪只披露 + n_docs_longhit 稳健臂; 论文须以稳健臂为准或 usci 剔除受污行 (非 pipeline 缺陷)。若走方案 (a) 匹配层清洗须防误删 建发/金地 类合法短名。
2. **F1 执行期风险 (若落 SSOT/清洗, REV-6)**: ① SSOT 重生非原子写 (`generate_company_tax_names.py:151 OUT.write_text` 无 temp+rename) — 与 tax/listed 管线无跨锁, 重生瞬间管线读该 yaml 会 torn-read → 须管线空闲时执行或对 generator 加 temp+os.replace; ② dev 落清洗但 DEFER 面板/registry 重生时, 盘上 cleaned yaml 与 committed `meta.company_names_sha256` 失配 → `test_name_list_hash_anchor` **立即翻红** → 须**同步重跑 01 (廉价 20.4s)** 复位自洽门 (区分 廉价 01-regen 立即做 vs 昂贵 02/03-regen 走 M0)。
3. **F2 第 10 篇复现受耦合制约为前瞻风险** (变量待新建 M2-M3); 现无活跃回归失败, 但须文档化 canonical 顺序以免建成后踩坑 + 纠正误导文案。
4. **F8 长跑 03 非原子 dta 写**: 单跑 kill 留半成品 (本轮未复现, 40min 后台净完成); 前次诊断计划 §7-1 会话级后台中断风险对生产 T=19 更长跑仍在。**F8 temp+replace 瞬时磁盘 (终审 NIT)**: 重跑时 .tmp 与旧文件共存 → dta 峰值需 ~2× (T=19 单 dta ≥6.85GB → 瞬时 ~13.7GB); T=19 前须确保 data 目录 ~2× 头room; 陈旧 .tmp (上次 kill 残留) 下轮 write 直接覆写无害。**F8 逐文件非跨文件原子 (终审 NIT)**: dta.replace 与 parquet.replace 之间被 kill 会留新 dta+旧 parquet 版本错配对 (各自仍完整), 属 pre-existing 且被 F8 严格改善, Stata 单消费 dta 恒完整, 低风险。
5. **确定性金标 BLAS=1 仅 shell 约定** (F13/F15); golden 重生须遵 SOP + M0。
6. **本轮未 live 覆盖** (F16, 依赖 CI gate): A7 完整 --no-emit-dta RUN / lock-race / --skip-unchanged 真跑 / --stage all。

---

## 6. 验证方法学 + 评审记录

- **真跑**: 5 入口顺序 EXIT=0 (Start-Process WaitForExit(2h cap) + capture); ③ +3 探针; 7 冒烟闭合覆盖缺口。全程 OFFLINE → **$0, 零 API** (stage21 misses=0)。
- **确定性**: 今晨基线 (backup_processed 653MB/114 文件) vs P1 逐列 multiset 哈希 5 文件 0 列相异 (F15 注更强行级口径为后续收敛)。
- **对抗审计 (7-agent, 787K tok, 166 tool calls)**: 分片证伪 5 入口 + A1-A10+B4 + dir-move + 残余项 + 完整性批判; 每 finding 附 file:line。审计纠正初判 2 处 (F2 前瞻性 / F3 归因)。
- **三轮计划评审 (4-agent, 643K tok; 完整性/技术正确性/可执行性风险 + 首席综合, okToShip=false)**: 揪出并已修 **2 P1 (REV-1 F1 定性与 codebook §7 L1 冲突 = "已披露刻意决定"陷阱 / REV-2 F1 级联 bump 方向反)** + 4 P2 (REV-3 A7 live 过度声称 / REV-4 §0 golden carve-out / REV-5 F2 前瞻性 / REV-6 §5 F1 执行风险) + 2 NIT (REV-7 计数 / REV-8 F3 占位列裁定)。**本 R1 版逐条落实。**
- **独立坐实**: F1 codebook §7 L1 (02:793-808) + generator docstring (:27-32) + registry 锚字段 (01:321) + tax-02 不过滤 (02:1165) 逐一源码确认; 冒烟 7/7 EXIT=0。
- **保险**: data/processed 小产物 114 文件/653MB 快照; 全程无付费、无 golden 重生、无破坏性改动。

---

*本 R1 版已吸收三轮评审全部 REV-1..REV-8。待最后一轮确认评审 (核 REV 逐条闭合 + 无新引入错误) 收口。实施须逐批经 gate + ruff; F1 方案 (a) 面板重生受 M0 审批门。*
