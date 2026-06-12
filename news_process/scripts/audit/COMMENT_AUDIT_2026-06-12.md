# 全仓注释审计·英译中·白话补注 报告 (2026-06-12)

> 白话版: 这次把整个项目里所有代码注释过了一遍——(1) 核对注释说的话和代码做的事是否一致, 不一致就改注释;
> (2) 纯英文注释翻译成中文 (技术术语/论文引用/修复编号保留英文); (3) 特别难懂的注释追加 "白话:" 行,
> 用大白话解释是什么/为什么。改动只碰注释和 docstring, 零代码改动, 测试与改前基线逐项一致。

## 1. 范围与执行方式

- 覆盖: `core/`(19) + 根目录 shim(39) + `pipeline/`(61) + `validation/`(14) + `papers/` py(~60) +
  Stata 模板 `.do.tmpl`(105, 含 paper-specific) + `scripts/`(50) + `config/*.yaml`(14) + `tests/`(188)。
- 执行: 15 个并行批次 agent + 主控收尾 (papers 批 agent 中途撞每周限额, 余量由主控亲自补完)。
- **禁区全程未触碰**: `config/prompts/`(Prompt v8 字节冻结)、`_llm_cache.db`、`{{...}}` 模板占位符、
  一切字符串字面量 (log/错误消息/Stata 标签/argparse help)、断言、fixture 数据。
- 保留不译 (按约定): 论文引用 (APA/DOI)、修复编号 (F-xx/V1-V5/P0/omni-g-* 等)、标识符/列名/命令名、
  URL、lint 指令、被源码锁测试断言的英文文本 (只追加中文行不替换)。

## 2. 量级统计 (各批次自报汇总)

- 实际修改文件: 约 150+ 个; 英文注释/docstring 翻译: 约 450+ 条; 新增 `白话:` 注释: 约 50 条
  (已有白话的复杂注释不重复添加, 避免噪音)。
- 终扫核验: 全仓剩余英文注释 95 处, 逐项核对均为合规保留项 (APA 引文原文/符号映射/覆盖率标记/标识符枚举)。

## 3. "注释与代码不符" 修正要点 (节选, 全量见各批次明细)

| 位置 | 问题 |
|---|---|
| run_pipeline_function.py (3处) | 称 23/24 随 enabled_methods 启停 — 实际已无条件 always-on |
| run_pipeline_validation.py:7 | 称 validation 由 config.yaml 控制 — 实际在 config/validation.yaml (config.yaml 是 legacy stub) |
| pipeline/__init__.py | 称入口被不存在的 "cli orchestrator" 消费; 子包清单漏 text/llm_archive |
| pipeline/filtering/__init__.py | 称 intensity 是 "SIF" 实现 — 实为 IDF 加权质心 (omni-g-fintech-02 已坐实) |
| fintech_intensity.py:553 | 称 full 轨读 '内容' — 实际优先读 content_full |
| preprocess/runner.py:32 | 称去重 "媒体权重优先保留" — 实际第一键是日期, 媒体权重仅同日 tiebreak |
| article_sbert.py | 称 stage 30a 需手动触发 — 实际已注册 STAGES_MAIN always-on; 称下传 stage 17 — 17 已移除 |
| policy_alignment.py (3处) | 称产出单列 policy_cosine_sim — 实际 5 列族 (双轨+t2v twin) |
| tone_berts.py:810 | docstring 称 df 需含 '内容' 列 — 实际只用 len(df) |
| validation/tone_validation.py:1659 | docstring 称输出 `34_*` 文件 — 实际输出 sentiment_validation_* 等 5 类产物 |
| stata_export.py:389 | 孤儿注释引用已删的 title indicator core patterns |
| encode_collab.py:15 | "v3.8.0 可 deprecate" 易误读为已发生 — 实际 collab_mode 仍 2-class |
| llm_peer/14_table5 模板 | 称 R1 为 "覆盖度加权 IV" — 实为等权均值 (producer 侧早已勘误, 模板漏改) |
| clarity 13_table4 模板 | 头注称 5 维度 — 实际 Panel A-D 4 维度 |
| locus/attention 18_robustness | "(6) Spillover SUTVA" 节无实现/全注释态 — 已标注占位 |
| benefit_society/30_figure1 模板 | 头注称含 heatmap — 实际只有直方图 |
| test_34_tone_validation.py:397 | 注释 "仍为 1.0" 与断言 `== 0.0` 自相矛盾 |
| test_panel_modules_smoke.py | "5 个模块 + iv_did" — 实际 6 个且不含 iv_did; _infer_track 仍列 title |
| test_paper_namespace_isolation 等 3 文件 | "8 papers" 陈旧计数 — 实际 11 (断言本来就是 11) |
| 52/53 shim | schemas.py 行号引用漂移 (182→156) |
| convert_parquet_to_stata.py:25 | 易把 .dta format 118 误读为 Stata 应用版本 |

## 4. 字节锁哈希同步 (唯一的非注释改动)

`tests/test_benefit_society_alt_anchor.py::test_sha256_stable` 锁定 `config/jlm2026_chinese_anchors.yaml`
的文件字节 SHA-256。本次 yaml 注释英译中导致字节变化 (锚点句/键值经 `yaml.safe_load` 递归相等验证,
逐位未动)。按测试内注释自带指引 ("若有意修改 yaml 内容, 需同步更新此期望 hash") 更新期望值:
`b56a610c…` → `0e35d996917c8910bd9f6293cf920e2898438bd0fd225ab5957ad3f1acb57c4d`, 并留审计注记。

## 5. 存疑未动清单 (留给 user 裁决)

1. **"You et al. (2018) hhx055" 引用** (stata_export/export/codebook/locus 19/collab 20/clarity 11 等多处):
   memory 已标记该引用无法核实疑幻觉; 属论文引用按规则保留, 建议人工统一核对后修订 (refs.bib 同步)。
2. `v3_5_1/27_tableA9` 历史归档模板: 双维聚类 vce(cluster bank_id year) 违反 G_year=2 红线 + 双轨同进
   一条 RHS — 历史归档如实保留, 新模板已是修正写法。
3. `pipeline/panel/encode.py` balance_panel 内正则仍含 `title` 死分支 (匹配不到任何列, 无害) — 属可执行
   代码, 超出本任务权限, 仅记录。
4. `split_config_yaml.py` stub 字符串与 CLAUDE.md 对 split 回退语义表述不一致 (任一缺失 vs 全部缺失) —
   字符串字面量禁区, 未动。
5. `core/dag.py:288` "~168 行"、iv_did.py "84 banks" 等随 panel 重生漂移的体量数字 — 以实读为准, 未动。
6. lm_non_sentiment.py:93 等少量行号引用漂移 — 定位提示性质, 未逐一追改。

## 6. 验证结论

- `ruff check .` 全仓: **All checks passed**。
- `pytest -m fast`: 改后 FAILED=23, 与改前基线 (23, 存档 `_comment_audit_baseline_fast.txt`) **逐项一致,
  0 新增失败** (23 个均为本机裸环境缺依赖/Python 3.14 的 pre-existing 失败)。
- 各批次定向回归: 源码锁/模板锁/golden 门禁相关测试合计 2000+ 项通过; 模板占位符完整性测试通过
  (零 `{{`/`}}` 增删); 14 个 YAML `safe_load` 与 HEAD 递归相等 (零键值改动)。
- clarity/disagreement 模板与 `replication/code/*.do` 副本保持逐字节同步 (test_omni_fix_zscore_papers 绿)。
- 全量 sweep 结果见 `_comment_audit_fullsweep.txt`。

## 7. 终极核查轮 (用户"万无一失"要求, 2026-06-12 深夜)

> 白话: 在测试之外又加了三层独立证据 — (a) 用程序逐文件证明"除注释外一个字节的代码都没变";
> (b) 在干净的 HEAD 基线副本里重跑全部失败测试, 证明失败全是改动前就有的; (c) 派三个"专门挑错"
> 的复核 agent 逐 hunk 对照代码挑翻译毛病, 挑出 7 处小瑕疵并全部当场修正。

**机器级零代码改动证明** (全部通过, 修正后复跑仍通过):
- AST 等价: 273 个改动 .py 与 HEAD 在"剥离注释+docstring"后逐一等价; 唯一例外 = 白名单内的
  sha256 期望哈希更新 (§4)。
- YAML 语义等价: 13 个改动 .yaml 全部 `safe_load` 递归相等 (零键值改动)。
- Stata 模板: 106 个改动 .do/.do.tmpl 剥离注释后代码逐行零差异; `{{TOKEN}}` 占位符多重集零变化。
- 冻结区: diff 中无任何 .parquet/.dta/.db/golden fixture/config/prompts 文件。
- 根 shim 全部 ≤30 行; 改动文件无 BOM/非 UTF-8/新增 U+FFFD (test_panel_no_mojibake 的 6 个 U+FFFD
  是 HEAD 既有测试数据)。

**全量 sweep 失败逐项证伪** (HEAD 基线 worktree 复跑):
- 改后全量 sweep FAILED=25; HEAD 基线复跑同批测试文件 FAILED=24, 交集逐项一致。
- 2 个差集 (`test_column_hashes_match_golden[21_tone_llms*.parquet]`) 在基线 worktree 不失败是因
  worktree 缺 data/processed 数据; 其输入 (磁盘 parquet + golden json) 经 diff 证明本次零触碰 →
  失败必然预存 (即 CLAUDE.md 已记载的 stage 21 磁盘漂移)。`test_cohort_module_exports_84_banks`
  只在 worktree 失败 (缺数据文件), 真仓不失败。**回归 = 0**。

**对抗复核** (3 个挑错 agent, 逐 hunk 对照实现, 共坐实 7 处注释层瑕疵, 已全部修正):
1. benefit_society_placebo.py 白话举例"同业拆借"不存在 → 改为真实 4 业务线。
2. stata_export.py 白话及 4 处既有注释 "101..126" off-by-one → 101..127 (`.`=101, .a-.z=102-127);
   f-string 内同病字样属字面量未动。
3. 39a shim docstring 漏 collab_mode 第三维 → 补 (行数 18, 仍 ≤30)。
4. attention 18_robustness 模板白话把 HHI 集中度误说成"离散度"、议程份额误说成"百分位排名"
   (恰是 omni-g-attention-06 警示过的反向解读) → 改正。
5. derivative_replication.py 虚构 collab "独立 instantiation 路径" → 改为"P5 onboarding 未完成
   待接线" (test_omni_fix_papers_misc.py 同源注释一并修正)。
6. brokerage tables.py "二阶 (L2) 中心性" 与 IV 的 W² 二阶邻居撞车 → "二阶滞后 (L2.) 中心度"。
7. validation.yaml Landis & Koch 档位: 0.81–1.00 才是 almost perfect, 0.80 在 substantial 上沿 → 改正。
   另按项目立场软化 inter_track_kappa 白话 ("双轨去留不由相关性决定")。
- 第三批 (tests/validation/scripts) **零坐实问题**; sha256 哈希经独立计算逐位一致;
  计数注释 (31 阶段/15+16/11 papers/95 模板/13 测试) 抽验全对。

**修正后复验**: AST/YAML/模板三证明复跑全过; ruff 全过; 受影响 7 个测试文件 224 项全过 (exit 0)。
