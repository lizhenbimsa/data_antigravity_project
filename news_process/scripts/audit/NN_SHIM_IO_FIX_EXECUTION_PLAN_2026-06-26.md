# NN_*.py Shim 输入/输出审核 — 修复执行计划 (2026-06-26)

> 依据: 纯代码取证标准 (不采信 docstring/注释/CLAUDE.md/memory) 的第二轮多智能体审核
> (58 agent / 576 万 tokens) + 作者独立确定性脚本核验。结论: **0 P0**; 暴露 **3 P1**
> (可复现性/血缘) + 若干 P2/P3 (命名/磁盘/原子性/潜在脆弱)。本计划只列**确认成立**的项,
> 每条给精确 file:line + old→new + golden 安全性 + 验证门禁。

> **🔎 本计划已经第二道对抗审核 (wf_ba814d0b, 9 agent) + 作者确定性复核。审核结论 (v2 已并入)**:
> - **A1 / A4 = approve** (逐字可套用, 修复正确, golden-safe; A1 可选用 `EmbeddingOfflineMissError(RuntimeError)` 子类替代裸 RuntimeError, nit)。
> - **A3 / A6 / A7 = approve_with_fixes** (修复正确, 但须补配套: A3 同步 2 处源码文本锁测试; A6 git rm 仅 3 个已跟踪文件 + .gitignore 加根级; A7 第二处插入补唯一锚点) — **已并入下方**。
> - **A2 = 审核否决 → 撤回** (P1-② 系误报: stage 75 只读 21 不读 24_herd, 现有守卫本就正确; 加 24_herd 反而引入误跳)。
> - 净结论: **真正落地的 P1 代码修复 = A1 + A3 两项** (P1-② 撤回); P2 = A4/A6/A7 + B1; D1 接受披露。

> **🏁 末轮定稿认证 (wf_65491007, 8 agent, 双向 steelman + 字节级套用复核 + 全新遗漏普查)**:
> - **严重度最终校准**: 在最严格审视下, **无任何活跃 P0/P1**。**A1 → P3** (机制属实但: 嵌入对同输入是确定函数、现盘缓存 0-miss 实证、命中即字节复现 → 仅潜伏可复现性披露 + 安全加固, 非活跃缺陷); **A3 → P2** (真实血缘缺陷但 4 道现有门把暴露收窄到 opt-in 固有边界)。**A2 撤回经独立 steelman 确认正确** (75 只读 21)。
> - **字节级套用复核 = all_apply, 0 blocker**: A1/A3-code/A3-test1/A3-test2/A4/A6-1504/A6-1682/A6-consumer/A7-arg/A7-insert 全部 old_string `exists_unique` + fix `yes`。本计划可逐字套用。
> - **全新遗漏普查 = 0 新活跃 bug**: 仅得若干 P3 门禁/覆盖缺口 (golden 门禁对行序/列序盲属 P3 加固项; "stage40/46/51 .dta 无验证" 被证伪 — 实存 stata_audit.py::audit_stata_compatibility)。
> - **A1/A3 修复仍建议实施 (作健壮性加固, golden-safe)**, 仅严重度由 P1 校准为 P3/P2。

---

## 0. 总原则 (铁律)

1. **本机绝不跑生产阶段 / 不触 data/processed / 不重生 golden**: 本机为 9490 行小样, 非全量
   18.2M/T=19。一切产物重生、golden 重生留与全量语料环境**统一消费** (DEFERRED §8)。
2. **全部 Tier A 代码改动须 golden-safe**: 只动守卫 / 元数据血缘 / 路径解析 / 命名, **不改任何
   数据列的计算逻辑或字节**。每条单列 golden 安全性论证。
3. **共享工作树纪律**: 提交一律 by-name `git add <file>`, 严禁 `git add .`/`-A`; 排除并发会话
   正在处理的 `../data/processed/v3_5_1_constants.json` 与 `validation/eval_reports/*` (后者正是
   A6 要处理的对象, 见 §10)。
4. **新建 commit, 不 amend; 不跳 hooks**。

---

## 1. 范围与分层总表

| 编号 | 源审核项 | 严重度 | 类型 | golden-safe | 门禁 |
|---|---|---|---|---|---|
| A1 | P1-① stage16 嵌入无离线守卫 | P1 | 代码 | ✅ (仅加 raise 闸, 命中路径不变) | ruff + 嵌入相关 test |
| ~~A2~~ | ~~P1-② stage40←75 守卫补 24_herd~~ | ~~P1~~ → **撤回** | — | — | **审核否决, 见 §2 A2** |
| A3 | P1-③ stage15 血缘漏主语料 ctx_path | P1 | 代码 | ✅ (仅扩 input_files 元数据) | ruff + test_w5 + **2 处源码文本锁测试** |
| A4 | P2-④ stage82 直接下标→.get | P2 | 代码 | ✅ (audit-only, 不进 golden) | ruff |
| A5 | P2-⑦ stage21 tie-retry 在线写回非确定 | P2 | 代码 | ✅ (加 env 门, 离线不变) | ruff + test_21* |
| A6 | P2-⑨ stage70 产物落点写进源码树/git | P2 | 代码+git | ✅ (产物不进 golden) | ruff + git 核对 |
| A7 | P2-⑫ stage80 默认 --output cwd 相对 | P2 | 代码 | ✅ (audit-only) | ruff |
| B1 | P2-⑩ 陈旧孤儿磁盘清理 | P2 | 运维 | ✅ (gitignored+untracked) | ls 核对 |
| B2 | P2-⑤ stage00 缺 data_version 元数据 | P2 | 运维(DEFERRED) | ✅ (自愈, 须全量重跑) | §8 |
| C1 | P2-⑥ stage00 双写无原子性 | P2 | 设计评审 | 需评审 | §4 |
| D1 | P2-⑧ 配置键号错位 (5键) | P2 | 接受披露 | ✅ (行为已证正确) | §5 |
| P3 族 | 见 §6 | P3 | 可选 | ✅ | — |

---

## 2. Tier A — golden-safe 代码修复

### A1 (P1-①) `pipeline/text/embedding_engine.py` — 嵌入缓存 miss 加离线守卫

**问题**: `get_embeddings_api` 缓存 miss 即真实联网 (`session.post(/embeddings)`), 全文 0 处
`NEWS_PROCESS_LLM_OFFLINE` 守卫 → 产物 `policy_cosine_sim_*` (stage16) 列值依赖网络浮点返回,
结构性跨-run 非确定 (与 stage21 的 raise-on-miss 不对称)。

**精确改动** — 在 `if missing_texts:` (line 417) 之后、现有注释 (line 418) 之前插入离线闸:

old (`embedding_engine.py:417-418`):
```python
    if missing_texts:
        # fix(2026-06-19 run-check F1): API spec 校验 + headers 构造下移至此 —
```
new:
```python
    if missing_texts:
        # P1 fix (2026-06-26): 与 stage 21 (tone_llms.LLMCacheMissError) 对称的离线确定性闸 —
        # NEWS_PROCESS_LLM_OFFLINE=1 时嵌入缓存 miss 即 raise (在 session.post 之前), 杜绝
        # 付费/非确定网络调用污染产物列, 兑现"离线 $0/零网络/逐位复现"契约。命中路径与生产
        # 首跑 (env 未设) 完全不变 → golden-safe。
        if os.environ.get('NEWS_PROCESS_LLM_OFFLINE', '').strip().lower() in (
                '1', 'true', 'yes', 'on'):
            raise RuntimeError(
                f"离线确定性模式 (NEWS_PROCESS_LLM_OFFLINE=1) 嵌入缓存 miss: "
                f"model={embedding_model} prompt_version={text_pipeline_version} "
                f"n_missing={len(missing_texts):,}; 需在线回填嵌入缓存或检查语料/"
                f"text_pipeline_version 是否相对 golden 漂移"
            )
        # fix(2026-06-19 run-check F1): API spec 校验 + headers 构造下移至此 —
```

**前置核实**: `os` 已在模块导入 (line 58-59 用 `os.environ`); `embedding_model` / `text_pipeline_version`
均为本函数形参, 在作用域内。
**golden-safe**: env 未设时分支不进, 命中路径字节不变。
**门禁**: `ruff check pipeline/text/embedding_engine.py`; 跑任何 mock 嵌入的 test (确认未误触发)。

---

### ~~A2 (P1-②)~~ `pipeline/panel/runner.py` — 75 merge 守卫补 24_herd_decay 【审核否决, 撤回】

> **审核结论 (wf_ba814d0b, X-completeness block + 作者复核)**: **本项撤回, 不实施**。
> P1-② 系误报 (原 RA1 升级基于错误前提)。

**否决依据 (纯代码)**: stage 75 (`pipeline/audit/cross_media_alpha.py`) 的唯一输入是
`21_tone_llms[_full]` (line 407/409 构造 src_path, line 468 `pd.read_parquet(src_path)`),
**全文不读 `24_herd_decay`**。新鲜度守卫 (runner.py:388-393) 的正确语义是"特征文件不得早于其
**真实计算来源**" —— 75 的来源是 21, 守卫已正确比较 75 vs 21 (mtime(21)>mtime(75) 即判陈旧)。

- 原 RA1 设想的"24 推进而 21 静止 → 75 陈旧"在 75 上**不成立**: 75 仅由 21 派生, 21 不变则盘上 75
  与当前 21 数据一致、并无陈旧 (RA1 混淆了"面板代际"与"75 的来源代际")。
- 若按 A2 把 24_herd 塞进 75 上游集, 反而**引入 false-positive skip**: 生产环境只重跑 22-24
  (24_herd mtime 变新) 而 21/75 不动时, 守卫会判 24_herd 比 75 新 → **错误跳过 merge → 把本就
  有效的 `cross_outlet_*` 列静默剔出发表面板**。这是对 75 合法状态的误杀, 与 golden-safe 相悖。
- 与 26_staleness 的不对称是**正确的**: `article_staleness.py:518-527` 经 `_restrict_to_panel_domain`
  真实内连 `24_herd_decay`, 故 26 登记 24 是对的; 75 无此依赖, 故不登记 24 也是对的。不对称源于
  依赖不同, 非缺陷。

**对 P1-② 的最终定性**: 现有守卫**本就正确**, 无需改代码。stage 40←75 跨执行器边仅为 **P2 结构性
观察** (单趟主线 75 不存在 → graceful skip → cross_outlet 列合法缺失), 已由 exists+mtime 守卫妥善
处理。可选治理 = 文档/codebook 把 `cross_outlet_*` 标注为 "validation-conditional" (见 §6 P3)。

---

### A3 (P1-③) `pipeline/filtering/fintech_intensity.py` — 血缘补真实主打分语料

**问题**: stage15 主打分 df 读自 `ctx_path`(=14_news_with_ctx.parquet, line 736-738), 但
`save_dataset(input_files=[full_path, input_file])` (line 814-821) 只记 12_*_full(IDF 参考)+
12_fintech_news(存在性 gate), 真实主源 ctx_path 缺席 → `--skip-unchanged` 内容门查不到 14 变更
(与 stage13/14/16 "读=记" 约定不对称)。

**精确改动** — 把真实主源纳入血缘 (替换 line 812-821):

old (`fintech_intensity.py:812-821`):
```python
    input_file = os.path.join(CONFIG['paths']['output_dir'],
                              CONFIG['filenames']['output_12_fintech_news'])
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="15_fintech_intensity",
        config=CONFIG,
        input_files=[full_path, input_file],
    )
```
new:
```python
    # P1 fix (2026-06-26): 把真实主打分语料纳入血缘 (与 stage 13/14/16 "读=记" 约定一致)。
    # 上方 (line 736-749) df 优先读 ctx_path(=stage13 输出, 真实评分行源), 缺失才 fallback
    # filtered_path; full_path 仅作 IDF 参考语料。原 input_files 漏掉主源 ctx_path, 致
    # --skip-unchanged 内容门对 14_news_with_ctx 变更失明 (stage15-only 分跑静默陈旧窗口)。
    _primary_src = ctx_path if os.path.exists(ctx_path) else filtered_path
    save_dataset(
        df=df,
        output_path=output_path,
        logger=logger,
        stage_name="15_fintech_intensity",
        config=CONFIG,
        input_files=[full_path, _primary_src],
    )
```

**前置核实**: `ctx_path` (line 691) / `filtered_path` (line 688) / `full_path` (line 685) 均在
作用域内; 删除原 `input_file` 变量 (仅此处用过, 不留悬挂引用 → 不触 ruff F841)。
**golden-safe**: 只改写盘 metadata 的 input_files 列表, 不改 df 数据列; 产物数据列字节不变
(golden 只哈希数据列)。**须重生 stage15 产物 metadata 后新血缘才生效** (DEFERRED §8, 本机不跑)。

**⚠ 配套 — 必须同步更新 2 处源码文本锁测试 (审核 block; 否则 A3 必致测试失败)**:
两处测试用源码字符串逐字断言旧字面量, A3 改后该字面量消失 → 双双 fail:
1. `tests/test_lineage_input_contract.py:31`
   old: `    assert "input_files=[full_path, input_file]" in fintech_intensity`
   new: `    assert "input_files=[full_path, _primary_src]" in fintech_intensity`
2. `tests/test_omni_fix_fintech.py:256` (test_lineage_contract_string_preserved)
   old: `        assert 'input_files=[full_path, input_file]' in _SRC`
   new: `        assert 'input_files=[full_path, _primary_src]' in _SRC`
(执行前先 Read 两文件确认行号/引号风格; 二者均 git 已跟踪, by-name add。)

**门禁**: ruff; `pytest tests/test_w5_skip_unchanged.py tests/test_lineage_input_contract.py
tests/test_omni_fix_fintech.py`; 新增覆盖测试 (改 14_news_with_ctx 内容后断言 stage15 不被跳; 见 §7)。

---

### A4 (P2-④) `pipeline/audit/stats_excel.py` — 直接下标改 .get 与本阶段容错契约一致

**问题**: stage82 对缺文件走 print-跳过容错, 但用 `config['filenames']['output_*']` 直接下标读键,
键缺失即 KeyError 硬崩 (split-mode 下键恒存在故当前不触发, 属潜在脆弱)。

**精确改动** (`stats_excel.py:131-140`):

old:
```python
        {'label': '00_preprocessing',
         'filename': config['filenames']['output_00_preprocessing']},
        {'label': '11_news_bank',
         'filename': config['filenames']['output_11_bank_news']},
        # 注 (2026-06-15): 读 stage 12b 邻近共现硬过滤【之前】的关键词金科阶段 (pre-12b);
        #   本审计逐阶段统计原始关键词口径, 非 12b 过滤后的分析宇宙 (后者经 13→21 链)。
        {'label': '12_news_fintech',
         'filename': config['filenames']['output_12_fintech_news']},
        {'label': '21_tone_llms',
         'filename': config['filenames']['output_21_tone_llms']},
```
new:
```python
        {'label': '00_preprocessing',
         'filename': config['filenames'].get('output_00_preprocessing', '00_preprocessing.parquet')},
        {'label': '11_news_bank',
         'filename': config['filenames'].get('output_11_bank_news', '11_bank_news.parquet')},
        # 注 (2026-06-15): 读 stage 12b 邻近共现硬过滤【之前】的关键词金科阶段 (pre-12b);
        #   本审计逐阶段统计原始关键词口径, 非 12b 过滤后的分析宇宙 (后者经 13→21 链)。
        {'label': '12_news_fintech',
         'filename': config['filenames'].get('output_12_fintech_news', '12_fintech_news.parquet')},
        {'label': '21_tone_llms',
         'filename': config['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet')},
```

**golden-safe**: stage82 audit-only, 不进 OUTPUT_REGISTRY/golden; 默认值=paths.yaml 登记值。
**门禁**: ruff。

---

### A5 (P2-⑦, 可选) `pipeline/sentiment/tone_llms.py` — 在线 tie-retry 写回与 golden 解耦

**问题**: `_resolve_unresolved_sentiment_tracks` 对平局/空票以 `force_refresh=True` 绕缓存重调 API
并 `INSERT OR REPLACE` 回写 → 在线跑漂移确定性锚点 `_llm_cache.db`。**离线 (LLM_OFFLINE=1) 下已被
守卫隔离** (force_refresh 在 session.post 前 raise)。

**建议** (二选一, 默认不改代码, 走流程闸):
- **方案 1 (推荐, 流程闸)**: golden 重生一律设 `NEWS_PROCESS_LLM_OFFLINE=1` 跑 stage21 (现三轨缓存
  已全命中) → 在线 tie-retry 路径根本不执行, 锚点不漂移。无需改代码。
- **方案 2 (代码闸, 可选)**: 加 env `NEWS_PROCESS_ALLOW_TIE_RETRY_WRITEBACK`, 未置位时 tie-retry
  重调结果只用于本次 results_map 聚合、**不 cache.put** (不覆盖锚点)。须改 `_resolve_unresolved_*`
  写回处, 不动 force_refresh 读取侧 (读取侧必须绕缓存否则平局永不可破)。

**本批结论**: 采方案 1 (流程闸, 0 代码改动); 方案 2 列为可选后续。
**golden-safe**: 方案 1 不改代码; 方案 2 离线路径不变。

---

### A6 (P2-⑨) `validation/prompt_sensitivity.py` — 产物落点对齐 + 移出源码树/git

**问题**: stage70 四产物写 `os.path.dirname(__file__)/eval_reports` = `news_process/validation/
eval_reports/` (源码树内, **被 git 跟踪** → 正是当前 git status 的 M 文件), 与全部同族阶段
(`CONFIG['paths']['output_dir']/eval_reports` = data/processed/eval_reports/) 背离。

**精确改动 (生产者, 2 处)**:

old (`prompt_sensitivity.py:1504`):
```python
        _report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eval_reports')
```
new:
```python
        _report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
```

old (`prompt_sensitivity.py:1682`):
```python
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'eval_reports')
```
new:
```python
    report_dir = os.path.join(CONFIG['paths']['output_dir'], 'eval_reports')
```

**配套 (消费者 + git, 须原子同步; 审核已逐项核实更正)**:
1. 同步改唯一**生产路径**文件消费者 `scripts/migrate/summarize_v7_sensitivity_results.py:13`
   (实测: `RESULTS_JSON = PROJECT_ROOT / 'news_process' / 'validation' / 'eval_reports' /
   'prompt_sensitivity_results.json'`, `PROJECT_ROOT = parents[3]` line 12):
   old: `RESULTS_JSON = PROJECT_ROOT / 'news_process' / 'validation' / 'eval_reports' / 'prompt_sensitivity_results.json'`
   new: `RESULTS_JSON = PROJECT_ROOT / 'news_process' / 'data' / 'processed' / 'eval_reports' / 'prompt_sensitivity_results.json'`
   注: `tests/test_70_prompt_sensitivity.py:514` 与 `tests/test_omni_fix_val_prompt.py:436` 也引用
   该 basename, 但均写/读 **pytest tmp 目录** (非生产路径) → **A6 不影响这两个测试**, 无需改。
2. **git 移出版本库 (审核更正: 仅 3 个文件被跟踪; 原列的 detail.csv 已被根 `.gitignore:55 *.csv`
   忽略且未跟踪, 列入会致 `git rm` pathspec 不匹配而整条 abort)**。从 `news_process/` 目录内执行:
   ```
   git rm --cached validation/eval_reports/prompt_sensitivity_results.json \
                   validation/eval_reports/prompt_sensitivity_table.tex \
                   validation/eval_reports/prompt_sensitivity_heatmap.png
   ```
   (产物改由重跑写到 gitignored 的 `data/processed/eval_reports/`; 该目录已被根 `.gitignore:92
   news_process/data/` 整树忽略。)
3. 在**仓库根** `.gitignore` (F:/WiseSearch/data_antigravity_project/.gitignore, 其 pattern 用
   `news_process/` 前缀) 增 `news_process/validation/eval_reports/` 排除规则杜绝复发。**勿**加进
   `news_process/.gitignore` (其 pattern 相对 news_process/, 该前缀会多一层失配)。

**golden-safe**: stage70 ∈ EXPECTED_NO_OUTPUT_STAGES, 不进 OUTPUT_REGISTRY/golden; 仅诊断产物迁移。
**⚠ 共享树**: 这 3 个 M 文件可能正被并发会话处理 (见 git status); 执行前与并发会话对齐, 避免冲突。
**门禁**: ruff; `git ls-files validation/eval_reports/` 改后应为空。

---

### A7 (P2-⑫) `pipeline/features/benefit_society_audit_combined.py` — 默认 --output 走 config

**问题**: `--output` 默认硬编码 cwd 相对字面量 `"news_process/data/processed/80_*.parquet"`, 不经
`output_dir` 解析 → 非 repo-root cwd 运行时 `Path()` 相对 cwd 解析到错误嵌套目录并 mkdir 写入
(audit-only, 不污染主链)。

**精确改动**:

old (`benefit_society_audit_combined.py:364-369`):
```python
    parser.add_argument(
        "--output",
        type=str,
        default="news_process/data/processed/80_alt_anchor_and_placebo_panel.parquet",
        help="Output parquet path",
    )
```
new:
```python
    parser.add_argument(
        "--output",
        type=str,
        default=None,  # P2 fix (2026-06-26): 默认延后到 main() 经 config output_dir 解析 (cwd 无关)
        help="Output parquet path (默认: <output_dir>/80_alt_anchor_and_placebo_panel.parquet)",
    )
```
并补默认填充 (审核更正: 给唯一锚点, 落在 setup_logging 收尾 `)` 与 banner 注释之间 = line 389~390,
在 `args.output` 首次消费 (line 430 日志 / line 551 `Path(args.output)`) 之前):
old (`benefit_society_audit_combined.py:388-390`):
```python
    )

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
```
new:
```python
    )

    # P2 fix (2026-06-26): --output 默认延后到此经 config output_dir 解析 (cwd 无关; audit-only)。
    if args.output is None:
        args.output = os.path.join(
            load_config()['paths']['output_dir'],
            '80_alt_anchor_and_placebo_panel.parquet',
        )

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39c)。
```
(banner 注释全文件唯一 → 锚点唯一; 此处 `load_config` 已于 line 383 import, `os` 已于 line 76 import。)
**前置核实**: 模块须已 `import os`; `load_config` 在 main() 内已 import (line 383)。文件名仍为
`80_alt_anchor_and_placebo_panel.parquet` 不变 → 下游 Stata 模板路径不动。
**golden-safe**: audit-only, 不进主面板/golden。
**门禁**: ruff。

---

## 3. Tier B — 运维 / 磁盘 (无代码改动)

### B1 (P2-⑩) 陈旧孤儿磁盘清理 (本机, gitignored+untracked, 零仓库风险)

当前代码已无任何 writer 产出下列旧号文件 (生产者写新号 67/68/69/81/track-suffixed):
```
data/processed/35_radius_sensitivity.json  35_radius_sensitivity.tex
data/processed/35_radius_label_distribution.png  35_radius_correlation_heatmap.png
data/processed/eval_reports/37_coverage_distribution.csv  37_keyword_frequency.csv
data/processed/eval_reports/37_temporal_drift.csv  37_zero_hit_keywords.csv
data/processed/eval_reports/38_media_diversity.xlsx  38b_decay_sensitivity.csv
data/processed/eval_reports/52_stata_data_audit.csv
data/processed/eval_reports/heatmap_cross_all.png  heatmap_cross_method.png
data/processed/eval_reports/heatmap_within_bert.png  heatmap_within_words.png
```
**执行前**: 逐个 `git check-ignore` 确认 untracked + 全仓 grep basename 0 个 .py writer (审核已证)。
**操作**: 手工 `rm` (不写进任何脚本; 不改代码)。

### B2 (P2-⑤, DEFERRED 本机) stage00 缺 data_version 元数据 → 全量重跑自愈

代码 (runner.py:630 save_parquet_with_metadata) 已正确; 盘上 9490 行文件 mtime 早于 W5 commit,
属重生前残留。**本机不重跑** (小样, 会以 ./data_excel 覆盖语料)。留全量语料环境跑一次 stage00
即写入 data_version, W5 --skip-unchanged 对 stage00 即生效。可选代码硬化 (非必需): runner.py
写盘后 `assert read_parquet_metadata(output_path) is not None`。

---

## 4. Tier C — 需设计评审 (本批不改)

### C1 (P2-⑥) stage00 双写无原子性

`load_and_process_data` 裸写 output_path (无元数据) → main() read-back+去重+metadata 重写。中途
失败留"未去重/无元数据"中间态, 下游 stage11 `os.path.exists` 守卫通过 → 静默消费未去重数据。
**为何列设计评审而非快改**: 裸写到最终路径是全量语料流式落盘的内存边界设计; 真正修复 (中间名
`00_preprocessing.raw.parquet` + 去重后原子 rename 到最终名) 牵动 read-back 路径与下游 gate 语义,
需独立设计 + 全量验证。**建议**: 单列设计评审项, 与 B2 全量重跑同期评估; 不进本批。

---

## 5. Tier D — 接受披露 (行为已证正确, 不改代码)

### D1 (P2-⑧) 配置键号 vs 文件号错位 (5 键)

`output_12b→13_* / output_13→14_* / output_14→15_* / output_15→16_* / output_32→61_*`: 经作者
确定性脚本 (66/66 .get 默认值 + 32/32 下标键四端逐字一致) + import-time `_validate_registry_invariant`
三重证实**路由 100% 正确**。重命名键 = 35+ call-site churn + KeyError 风险 + 测试脆断, 零行为收益。
**处置**: 仅在 `config/paths.yaml:65` 键名格式注释补一行: "自 v3.11.0 NN 重编号起, 键号为历史
稳定句柄, 可能 ≠ 当前脚本号/文件号; 路由以 schemas._OUTPUT_FILENAME_KEYS 字面量元组为准"。
(纯注释, 不动代码/键。)

---

## 6. P3 族 (可选, 低优先)

| 项 | 处置 |
|---|---|
| stage82 读 pre-12b 关键词口径致漏斗口径混淆 | 改读 `output_12b_cooccurrence` 或加 12b 行 (仅人看 Excel) |
| stage80 输出完全孤儿 / direction .npy sidecar 守卫不对称 | direction .npy 补 sidecar 强制校验 |
| stage51 .dta+诊断 CSV 未登记 OUTPUT_REGISTRY | 可选登记 (与 46 对称) |
| stage24 herd max_features 默认 10000 vs config 5e6 | 默认对齐 config (仅缺键时回退) |
| ~45 处 panel merge 无 validate= | 可选加 `validate='1:1'/'m:1'` 防御纵深 |
| 多处 lineage 直接下标 vs 主路径 .get 防御不对称 | 统一为 .get(默认) |

---

## 7. 验证门禁

执行顺序: 每完成一个 Tier A 项即跑该项门禁; 全部完成后跑总门禁。

1. **静态**: `ruff check .` (须 clean)。
2. **单测子集** (本机可跑, 不触付费/全量):
   - `pytest tests/test_w5_skip_unchanged.py tests/test_lineage_input_contract.py tests/test_omni_fix_fintech.py` (A3 — 后两者为源码文本锁, **必须随 A3 同步改**, 见 A3 配套)
   - `pytest tests/integration/test_dag_consistency.py` (不变式不破)
   - `pytest tests/test_21_tone_llms.py` 或 `-k "tone_llms"` (A5 若采方案 2)
   - stage82/stage80 相关 test (A4/A7)
   - (A2 已撤回, 无对应门禁)
3. **新增覆盖测试 (A3)**: 在 test_w5_skip_unchanged 加用例 — 改 `14_news_with_ctx.parquet` 内容后
   断言 `_stage_skip_unchanged_is_safe('15_fintech_intensity.py')` 返回 `(False, ...)`。
4. **A6 执行前复核**: Read `scripts/migrate/summarize_v7_sensitivity_results.py` 确认消费路径的
   实际行号/变量名 (计划记 line ~13, 须实测)。
5. **A6 执行后**: `git ls-files validation/eval_reports/` 应为空。
6. **不变式**: import `news_process.core.schemas` 不抛 (五项校验 PASS)。

---

## 8. golden / 全量重跑 DEFERRED 边界

- A1/A2/A3 改的是守卫/血缘/路径, **不改任何数据列计算** → 列哈希不变 → **golden-safe**。
- A3 的新血缘须 stage15 产物**重生 metadata** 才生效; A2 守卫扩展须面板重建才显效; B2 须 stage00
  全量重跑。**这些重生/重跑全部 DEFERRED 到全量语料环境**, 与既有 DEFERRED 批次 (`_allv` /
  inject-fintech / golden 重生) **统一消费**。本机绝不跑 (小样 + ./data_excel 覆盖风险)。
- golden 只哈希数据列 → 上述重生为 golden-safe (引擎/聚合确定性)。

---

## 9. 回滚

每项独立 commit (by-name)。回滚 = `git revert <sha>`。Tier A 全为加法式守卫/元数据, 回滚无副作用。
B1 删除的是 untracked 孤儿, 无法 "回滚" 但可由对应 validation 阶段重跑再生 (新号)。

---

## 10. 共享工作树注意事项

- 当前 `git status` 已有 M: `../data/processed/v3_5_1_constants.json`, `core/data_versioning.py`,
  `pipeline/preprocess/runner.py`, `run_pipeline_function.py`, `tests/test_w5_skip_unchanged.py`,
  `validation/eval_reports/prompt_sensitivity_*` 等 — 多为并发会话 (W5/缓存策略) 的在途改动。
- **本计划提交一律 by-name** `git add <精确文件>`; **排除** `v3_5_1_constants.json` (pytest 副作用)
  与并发会话占用的文件。
- A6 触及的 `validation/eval_reports/prompt_sensitivity_*` 正在 git status 中 (M) — 执行 A6 前
  须与并发会话确认这些文件归属, 避免 `git rm --cached` 与对方改动冲突。
- A3 触及 `tests/test_w5_skip_unchanged.py` (已 M) — 须先 Read 当前内容再增量加用例, 防覆盖在途改动。

---

## 11. 风险登记

| 风险 | 缓解 |
|---|---|
| A1 误触发 (生产首跑/在线回填被 raise 阻断) | 仅 env=1 时触发; 生产首跑不设该 env → 不触发 |
| ~~A2 守卫误跳~~ | **A2 已撤回** (审核否决, P1-② 误报); 现有守卫本就正确, 不动 → 零风险 |
| A3 改字面量破源码文本锁测试 | **已并入**: 同步改 test_lineage_input_contract.py:31 + test_omni_fix_fintech.py:256 (见 A3 配套) |
| A3 删 input_file 变量留悬挂引用 | 已确认 input_file 仅 812/820 两处; 改后无悬挂、无 F841 |
| A6 git rm 命中未跟踪文件整条 abort | **已并入**: git rm 仅列 3 个已跟踪文件 (去 detail.csv); .gitignore 加根级 |
| A6 改落点破坏既有消费者 | 同步改 summarize_v7 消费者 + git rm --cached, 三步原子 |
| 共享树并发冲突 | by-name add + 排除在途文件 + A6 前对齐 |
| 本机误跑全量/重生 golden | §0/§8 铁律: 本机绝不跑产 + DEFERRED 统一消费 |

---

*(权威依据: 第二轮纯代码取证审核 wf_3605ece2-1dc + 作者确定性脚本核验 fallback_check。)*
