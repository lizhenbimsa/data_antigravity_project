# 执行计划 — stage 13 (12b) 共现硬过滤口径由「严格同句 radius=0」改回「±1 句窗口邻近共现 radius=1」

> **权威计划**。版本: 2026-06-29。作者: Claude (Opus 4.8, 1M context)。
> 配套提交将引用本文件路径。

---

## 0. 一句话目标

在 stage 13 (`13_cooccurrence_filter.py`, 历史称 stage 12b) **共现保留判据已纳入标题
（`match_in_title=true`，标题+正文一起切句）** 的基础上，把**正文侧的银行×金科共现窗口
由「严格同句 (sentence_radius=0)」放宽为「±1 句窗口邻近共现 (sentence_radius=1)」**：
即只保留「目标银行与 ≥1 金融科技词在 **命中句前后各 1 句（共 3 句）窗口内** 邻近共现」的
文章行，丢弃其余。

这是用户 2026-06-29 决策，**取代** 2026-06-27 的「只保留银行∧金科同句报道 (radius 1→0)」
决策（提交 `7b7cf3a1`）。`match_in_title=true`（2026-06-29 提交 `d78a4503`）**保留不动**。

---

## 1. 背景与精确语义

### 1.1 引擎本就支持 radius=1（这是 2026-06-27 之前的原默认）

判据原语 `core/text/entity_context.py::has_bank_fintech_cooccurrence_within_radius`
是**通用 radius** 函数（`sentence_radius` 形参驱动）：

- `radius=0`：窗口闭区间 `[i, i]` 坍缩到银行锚句自身 → 要求银行与金科**同句**共现（最严特例）。
- `radius=1`：窗口闭区间 `[i-1, i+1]` → 银行锚句 i **或其前一句、后一句**含 ≥1 金科词即命中
  （邻近共现）。`radius=1` 的 keep 集 **⊇** `radius=0` 的 keep 集（单调放宽，删得更少）。

因此本次**功能改动只有一个配置值**：`cooccurrence_filter.sentence_radius: 0 → 1`。
引擎逻辑、列 schema、阶段计数**零改动**。其余全部是为对齐项目「口径文档须与生产
默认一致」铁律而做的**散文/日志/测试/披露同步**（即 `7b7cf3a1` 的镜像反转，但保留
`d78a4503` 加入的 `match_in_title` 内容）。

### 1.2 与标题（match_in_title）的交互（无需改代码）

`filter_cooccurrence` 在 `match_in_title=true` 时把标题 `prepend_title` 拼到正文前再切句，
标题成为句序列的第 0 句（若标题自含句末标点可能为多句）。radius=1 时：

- 银行在标题句（S0）、金科在正文首句（S1）→ 在 ±1 窗口内 → **保留**（radius=0 时仅当
  标题句自身同时含银行∧金科才保留）。
- 银行在正文深处句 i (i≥2)、金科只在标题 → 标题在 S0，距 i ≥2 句 > radius 1 → **不命中**
  （符合邻近语义，正确）。

这是**既有 `prepend_title` + 通用 radius 代码的自然组合**，无需任何代码逻辑改动。

### 1.3 `_ss` 轨交互的**进一步恢复**（三态口径，重要：正向副作用，须披露）

`_ss` 轨（`content_ss`，独立概念，**本次不动**）的命中判据是**严格同句**
（`extract_bank_fintech_cooccurrence`，radius 控制的是输出扩窗、命中仍要求同句）。
`frac_ss_fallback` 须按**三态**披露（**勿沿用旧二态「radius=0→≈0 全坍缩」叙事**——会与
`config/filtering.yaml:130-131` 既有 `match_in_title` 披露打架）：

- **radius=0 + `match_in_title=False`（最旧态）**：12b 存活行均含银行∧金科**同句** →
  `ss_is_fallback` 几乎恒 False → `frac_ss_fallback → ≈0`（零方差全坍缩）。
- **radius=0 + `match_in_title=true`（当前盘上 HEAD `d78a4503`）**：纳入标题后，「标题点明
  银行∧金科、正文跨句」的回补行其正文无同句共现 → `ss_is_fallback=True` →
  `frac_ss_fallback` **已部分恢复 ∈ (0,1)**（`config:130-131` 已披露）。
- **radius=1 + `match_in_title=true`（本次目标态）**：再**新增**「仅邻句共现、非同句」的存活
  行（其正文亦无银行∧金科同句）→ `frac_ss_fallback` **进一步恢复**（在部分恢复基础上增量）。

即本次是「部分恢复 → 进一步恢复」的**增量**（非「≈0 → 恢复」的全量）。所有声称
「`frac_ss_fallback→≈0` 坍缩」且**未带 match_in_title caveat** 的披露须更新为三态口径
（含 `cooccurrence_filter.py` docstring、`entity_context.py:399-400`、CLAUDE.md）。

### 1.4 keep 率方向与守卫（数值逻辑不变）

`radius=1` keep ≥ `radius=0` keep（单调）。盘上小样实测 `0.1427`（14.27%）零共现率是
**radius=0（严格同句）的丢行上界**；radius=1 的丢行率 ≤ 14.27%，keep ≥ 85.73%。

`cooccurrence_filter.py` 日志判读中的 `_keep_lower = 1.0 − 0.1427 = 0.8573` 仍是 radius=1 的
**有效下界**（radius=1 keep 应 ≥ 此线），数值判读逻辑无需改，仅须把「radius=0 是生产默认」
的框架表述改为「radius=1 是生产默认；radius=0 时 keep≈此线、radius=1 时 ≥ 此线」。
`min_keep_frac=0.001` 守卫与 SAFE-1 不变。

### 1.5 运行期标签已是 radius 无关（降低逻辑风险）

`cooccurrence_filter.py` 的运行期模式标签本就由 radius 值动态决定：
`_mode = "同句共现" if _sentence_radius == 0 else "窗口邻近共现"`；sidecar 同理
`_mode = "same_sentence" if _radius==0 else "windowed_cooccurrence"`。改 config 为 1 后，
日志与 sidecar **自动**显示「窗口邻近共现 / windowed_cooccurrence」。故**代码控制流零改动**，
只须改那些「把 radius=0 当生产默认」的**注释/docstring/banner 框架表述**。

---

## 2. 范围边界（务必遵守）

### 2.1 改（本次口径反转，镜像 `7b7cf3a1` 的 18 文件集【已含 CLAUDE.md / test_13 / test_dag_consistency】+ 本计划 md）

唯一**功能**改动 = `config/filtering.yaml::cooccurrence_filter.sentence_radius: 0→1`。
其余为散文/测试同步。逐文件清单见 §3。

### 2.2 **绝不**改（边界铁律）

1. **`_ss` 轨定义与所有 `content_ss` / `ss_is_fallback` / `ss_sentence_radius` 逻辑**
   （`extract_bank_fintech_cooccurrence`、`ctx_materializer` 的 ss 物化、`context_window.ss_sentence_radius`、
   conftest/test_14/test_content_ctx 等 ss 测试）。`_ss` 轨仍是严格同句，本次只改 **12b 过滤器**。
2. **`context_window.sentence_radius`（=1，ctx 轨输出窗）** 与 **`context_window.ss_sentence_radius`（=1）**：
   是 ctx/ss **输出轨**的扩窗参数，与 12b **过滤判据**是不同 config 键，**不碰**。
3. **`has_bank_fintech_cooccurrence_within_radius` / `extract_bank_fintech_cooccurrence` /
   `extract_entity_context` 的任何代码逻辑**（纯散文除外）。引擎数学层零改动。
4. **`match_in_title` 的任何代码/config 值**（保持 `true` + 其 docstring/测试）。
5. **`data/processed/*`（已 gitignore）**：parquet / csv / `13_cooccurrence_filtered.meta.json`
   一律不动、不重生（盘上仍显示 `same_sentence|radius=0`，DEFERRED 到生产语料机）。
6. **golden snapshot（`tests/fixtures/golden_panel_v0.json`）不动**：本机不重跑、不重生。
7. **`test_radius0_requires_same_sentence` 等原语层 radius 语义测试**：radius=0 在原语层仍
   要求同句，该测试**仍然正确**，**保留不改**（它锁的是原语 radius 语义，非生产默认）。
8. 阶段计数 STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16 **不变**。

---

## 3. 逐文件改动清单

> 术语：本次统一用「**±1 句窗口邻近共现 / 窗口邻近共现**」（生产默认 radius=1），并保留
> 「严格同句 (radius=0)」作为**稳健性备选 / 最严特例**表述。即把 `7b7cf3a1` 里「邻近→同句」
> 的散文翻转**反向**为「同句→邻近」，同时保留 `d78a4503` 的标题内容与 §1.3/§1.4 的更新披露。

> ### ⚠ 执行方法学（第一轮评审 P1#1/#2/#3 修订，**取代任何具体行号**）
>
> **本计划 §3.E–O 不再给行号**（旧稿行号抄自镜像 commit 上下文、已偏移数百~上千行，按行号机械
> 执行会改错位置）。执行一律走 **grep 驱动 + 逐条人工分类**：
>
> 1. **唯一权威反转源**：`git show 7b7cf3a1`（CWD-相对 pathspec）逐 hunk diff。该提交把「邻近→
>    同句」，本次把其中每条**反向**（同句→邻近）。
> 2. **镜像之后的代码漂移须额外纳入**（不在 18 文件 diff 内，但描述【12b 过滤】生产默认）：
>    - `pipeline/text/ctx_materializer.py` 的 2026-06-28 运行期判读块（含「stage 12b 同句共现硬
>      过滤 (生产 radius=0)」「ss 真·无共现≈0」「仅当 12b radius ≤ ss_sentence_radius」）—— 见 §3.L。
>    - `match_in_title`（`d78a4503`）在 `config/filtering.yaml` 与 `cooccurrence_filter.py` 里把
>      【12b 判据本身】命名为「同句判据 / 再判同句」的散文 —— 见 §3.B / §3.C。
>    - `cooccurrence_filter.py` 的**硬编码运行期日志串**（phase_durations 键「②同句共现过滤」、
>      过滤摘要、stage banner、结果分析/年份分层）—— 这些**不**随 radius 动态，须一并中性化，见 §3.C。
> 3. **`_ss` 轨 / ctx 轨 / 学术谱系 通用陈述 严禁翻**（grep「同句」会大量命中它们）。每改一个文件前
>    先 `git grep -n '同句' <file>` 列全，逐条判定「此条说 **12b 过滤生产默认** 还是 **下列豁免类**」，
>    仅翻前者。**豁免类（保留「同句」不动）白名单**：
>    - 任何含 `content_ss` / `ss_is_fallback` / `第三轨` / `ss 轨` / `银行+金科同句` / `同句共现轨`
>      的行（`_ss` 轨定义，genuinely 同句）。
>    - `core/text/entity_context.py::extract_bank_fintech_cooccurrence` docstring（含 ~L275「同句
>      (same-sentence, radius=0) 即…proximity 谱系最严特例」）—— `_ss` 提取器 + 通用学术谱系，**严禁翻**。
>    - `tests/test_entity_context.py`（`extract_entity_context` ctx 轨在 radius=0 的原语测试）、
>      `tests/test_radius_sensitivity_llm.py` / `test_omni_fix_val_prompt.py`（radius=0 与 12b 默认无关）。
>    - `tests/test_13_cooccurrence_filter.py::test_radius0_requires_same_sentence`（原语层 radius=0
>      仍要求同句，**真陈述，保留**）。
> 4. **改后核验**：每个文件改完 `git grep -n '同句共现\|同句判据\|生产 radius=0\|生产默认 radius=0' <file>`，
>    残留必须**仅剩豁免类**（_ss/通用谱系）。全仓 `git grep -n '生产 radius=0\|生产默认 radius=0'` 须为 **0**。

### A. 功能值（唯一硬改动）
- **`config/filtering.yaml`** — `cooccurrence_filter.sentence_radius: 0 → 1`，行内注释（值所在行）改为
  「生产默认 1 = ±1 句窗口邻近共现（命中句前后各 1 句，共 3 句）；0 = 严格同句最严特例，
  稳健性备选」。

### B. config 散文（同文件 `config/filtering.yaml`）
- `cooccurrence_filter` 上方大披露块：把「生产默认操作化 = 严格同句」框架改为「生产默认 = ±1 句
  窗口邻近共现」；radius=0 降为最严特例/稳健性备选。
- `_ss` 轨交互披露：把「`frac_ss_fallback→≈0` 坍缩」更新为「radius=1 下 `frac_ss_fallback ∈ (0,1)`
  **恢复**（仅邻句非同句的存活行 → ss 严格同句判据回退）」。
- `context_window` 上方 Andreou 注释：把「生产默认操作化 = 严格同句 (sentence_radius=0)」改为
  「= ±1 句窗口邻近 (sentence_radius=1)；radius=0 同句为最严特例」。
- **【P1#3 新增】`match_in_title` 段（披露块 + `match_in_title: true` 值注释）内对【12b 判据本身】的
  命名中性化**：把「**同句判据 / 再判同句**」→「**共现判据**」（radius 无关措辞）。`match_in_title`
  的**功能语义**（纳入标题 / 堵单向假阴性 / 与 stage 21 full 轨对齐）**保留不动**，仅判据命名去「同句」。
  改后该 stanza 不再「值注释说 ±1 窗口邻近、紧邻行说同句判据」自相矛盾。

### C. `pipeline/filtering/cooccurrence_filter.py`（**全文 grep 驱动，不限行号**）
执行前 `git grep -n '同句' pipeline/filtering/cooccurrence_filter.py`（当前约 50 处），逐条按
§3 方法学分类，把描述【12b 过滤生产默认】的全部改为 radius=1 ±1 句窗口邻近：
- 模块 docstring：默认框架同句→±1 句窗口邻近；保留 match_in_title 段的**功能语义**，但把段内
  「**同句判据 / 再判同句**」命名中性化为「**共现判据 / 判共现**」（P1#3，含 L13/150/199 + 日志串 L305）；
  更新 `_ss` 交互披露（frac_ss_fallback 恢复）。
- `filter_cooccurrence` docstring：默认同句→±1 句窗口邻近。
- 日志判读框架：把「radius=0 是生产默认」改为 radius=1 默认；`_keep_lower=0.8573` 数值逻辑**不动**，
  仅改框架文字（radius=0 时 keep≈此线，radius=1 时 ≥ 此线）。
- **【P1#1/P2 新增】硬编码运行期日志串**（不随 radius 动态，须一并中性化，否则 radius=1 真跑日志
  自相矛盾）：`phase_durations` 键「**②同句共现过滤**」（其 set 与 read 两处须同改否则 KeyError）、
  过滤摘要日志「同句共现过滤: 保留…」、`main()` stage banner、`_log_environment_and_config` /
  结果分析 / 年份分层 日志中的「同句共现」描述 → 改为「邻近共现 / 窗口邻近共现」。
- `_write_sidecar_meta` 注释框架更新（`_mode = "same_sentence" if _radius==0 else "windowed_cooccurrence"`
  **映射逻辑不动**，radius=1 时自动产 `windowed_cooccurrence`）。
- ⚠ **【R2 P2 严禁动的动态分支字面量】**：`_mode = "同句共现" if _sentence_radius == 0 else
  "窗口邻近共现"`（line ~164）、`_mode = "same_sentence" if _radius==0 else "windowed_cooccurrence"`
  （line ~228）、`_mode_txt = "严格同句 (radius=0)" if _radius==0 else f"窗口邻近 (radius={_radius})"`
  （line ~478）——这三处的 `if radius==0` 分支里的「同句共现/same_sentence/严格同句」字面量是
  **radius=0 时的正确标签**，radius=1 时自动走 else 分支 → **严禁替换**（替了会破坏 radius=0
  稳健性备选的运行期标签）。`_ss_zero_cooc = 0.1427` 注释「严格同句 radius=0 零共现率」准确
  （0.1427 确为 radius=0 基线），**保留**（可加「作 radius=1 keep 下界」）。
- ⚠ **【R2】动态文案的「生产默认」框架须迁移**：line ~303 的三目把「生产默认 0 = 严格同句」放在
  `radius==0` 分支——须把「生产默认」标注从 radius==0 分支**移到** else 分支（radius==0 分支改
  「严格同句 (radius=0 最严特例)」，else 改「±1 句窗口邻近 (生产默认 radius=1)」），使两分支文案
  在新默认下都正确。

### D. `core/text/entity_context.py`
- `has_bank_fintech_cooccurrence_within_radius` docstring：**两处**生产默认断言均须翻——
  ① 函数头「生产默认 radius=0 = 严格同句」② 「⚠ 生产 stage 12b 默认已切到 radius=0 …
  frac_ss_fallback→≈0」段 → 均改为「生产默认 radius=1 = ±1 句窗口邻近；frac_ss_fallback ∈ (0,1) 恢复」。
  「radius=0 时窗口 [i,i] 坍缩到同句」等**通用 radius 语义陈述保留**（仍真）。**函数体代码零改动。**
- **【R2 P2 新增】`entity_context.py:397「二者在 sentence_radius=0 时于命中检测上等价 (= 生产口径)」**：
  radius 0→1 后 12b 过滤（radius=1）与 `_ss` 提取器（恒严格同句）**不再等价**，故「(= 生产口径)」
  变假 → 须改为「(radius=0 最严特例时等价)；生产默认 radius=1 时本函数更宽，二者不等价
  (keep 集 ⊋ 同句集)」。**不可当「通用 radius 语义」误豁免。**
- ⚠ **`extract_bank_fintech_cooccurrence` docstring（含 ~L248-358 / L275「同句 (same-sentence,
  radius=0) 即…最严特例」）严禁翻**——那是 `_ss` 提取器 + 通用学术谱系，非 12b 生产默认。
  L395「extract_bank_fintech_cooccurrence (严格同句): 命中句须同一句」描述 `_ss` 函数语义，亦保留。
  L590/611（entity_context 运行期日志的「ss(银行∧金科同句)」「以金科词同句命中」）= `_ss` 轨，保留。

### E–O. 全仓口径散文（镜像 `7b7cf3a1` 反向，「同句共现」→「邻近共现」）
> **执行=以 `git show 7b7cf3a1 -- <file>` 逐 hunk 为权威，把其中每条 邻近→同句 反向施加；diff
> 未触及行不动；含 `_ss`/`第三轨`/`content_ss` 行严禁翻。**（不给行号；下列仅标文件与命中要点。）
- **E** `core/dag.py`：12b StageSpec 注释 + `name=` 标签「同句共现预过滤」→「邻近共现预过滤」。
  ⚠ **【R2 P3】该 mirror hunk 是 3 删 4 增重构（非纯 token swap）**：镜像新增了「生产默认…
  在【同一句话】内共现 (sentence_radius=0 = 严格同句; ≥1 放宽为窗口邻近, 仅稳健性备选)」框架 →
  须**整段 hunk 反向**（撤回该 radius=0 框架，还原「±sentence_radius 句窗口内邻近共现」表述 +
  改回 radius=1 默认），不可仅做「同句→邻近」逐 token 替换。
  ⚠ **同文件紧邻的 `第三轨 content_ss…银行+金科同句共现轨` 严禁翻**（mirror 未碰）。
- **F** `core/reporting.py`：12b 摘要注释「同句共现硬过滤」→「邻近共现硬过滤」。
- **G** `core/schemas.py`：OUTPUT_REGISTRY + _OUTPUT_FILENAME_KEYS 两处 12b 注释「同句共现硬过滤」→「邻近共现硬过滤」。
- **H** `config/paths.yaml`：`output_12b_cooccurrence` 注释「同句共现硬过滤」→「邻近共现硬过滤」。
- **I** `pipeline/audit/stats_excel.py`：pre-12b 注释「同句共现硬过滤【之前】」→「邻近共现硬过滤【之前】」。
- **J** `pipeline/filtering/__init__.py`：模块 docstring 12b 行「同句共现硬过滤」→「邻近共现硬过滤」。
- **K** `pipeline/filtering/fintech_intensity.py`（多处）：描述 12b 的「同句共现过滤」→「邻近共现过滤」。
  ⚠ **同文件 `ss 轨…同句共现` 行严禁翻**。
- **L** `pipeline/text/ctx_materializer.py`：① mirror 命中的 12b「同句共现硬过滤」→「邻近共现硬过滤」；
  **② 【P1#2 新增】2026-06-28 运行期判读块**（硬写「stage 12b 同句共现硬过滤 (生产 radius=0)」
  「ss 真·无共现≈0」「仅当 12b radius ≤ ss_sentence_radius」）须按 radius=1 **重写**（非机械替换）：
  「生产 radius=0」→「生产 radius=1 邻近共现」；「真·无共现≈0」→「radius=1 下存活含非同句邻句行 →
  ss 回退恢复 frac_ss_fallback∈(0,1)」；包含关系子句修正为「**仅当 12b radius=0 严格同句时** keep ⊆ ss 同句集」。
  ⚠ **同文件 `第三轨 content_ss…同句共现轨` 等 `_ss` 定义/物化行严禁翻**。
- **M** `run_pipeline_function.py`：ASCII 流程图 12b 注释「同句共现硬过滤」→「邻近共现硬过滤」。
- **N** `validation/media_diversity.py`：pre-12b 注释「同句共现硬过滤【之前】」→「邻近共现硬过滤【之前】」。
- **O** `validation/radius_sensitivity.py`：pre-12b 注释「同句共现硬过滤【之前】」→「邻近共现硬过滤【之前】」。

### P. `13_cooccurrence_filter.py`（thin shim）
- docstring（1–11 行）：「银行×金科同句共现硬过滤 … sentence_radius=0 = 严格同句」→
  「银行×金科邻近共现硬过滤 … sentence_radius=1 = ±1 句窗口邻近；0 = 严格同句最严特例，稳健性备选」。

### Q. `tests/test_13_cooccurrence_filter.py`（核心测试改动）
1. 文件 docstring（1–3 行）：默认同句→±1 句窗口邻近。
2. **`test_production_default_is_same_sentence`（57–69 行）→ 改为 `test_production_default_is_window_radius1`**：
   断言 `radius == 1`，docstring 改为「生产默认 ±1 句窗口邻近；若改回 0 须同步更新断言+config+
   docstring+CLAUDE.md」。
3. **`test_production_config_drops_adjacent_only`（72–85 行）→ 改为 `test_production_config_keeps_adjacent`**：
   radius=1 下 `same` 与 `adjacent` **均保留** → 断言 `["same","adjacent"]`；docstring 锁「±1 窗口
   保留邻句共现」。
4. **新增 `test_production_config_drops_far_apart`**：用 `cf` fixture（读真 config=1），银行 S0、
   金科 S3（距 3 > radius 1）→ 端到端**丢弃**，锁 radius=1 不退化为全保留。⚠ **【P2】该测试
   DataFrame 不含 `标题` 列**（或标题不含任何金科词）——否则 `cf` 读真 config 的 `match_in_title=True`
   会把标题作 S0 拼入、可能拉近距离致 r=1 命中而翻转；docstring 注明此约束（已实证：无标题列时
   `_titles=['']*len` → 纯正文判据，远隔稳定 drop）。
5. `test_short_text_charfallback_ignores_radius`（128–146 行）docstring：把「radius 1→0 对短文零
   影响」「生产 radius=0 同句口径」框架改为 radius=1 默认（断言代码 radius 无关，**不改**）。
6. **保留断言/数据不改，但中性化注释**：`test_radius0_requires_same_sentence`（原语层 radius=0 真陈述，
   **整测保留**）、`test_keep_adjacent_within_radius1`、`test_drop_far_apart_radius1`、
   `test_radius_monotone_keeps_when_widened`、所有 SAFE-1/min_keep/schema/granularity 测试（radius=1 下
   行为不变，见 §5）。⚠ **【P2】match_in_title 测试块（约 284–362 行）内的「严格同句路径 / 同句配对 /
   同句判据」注释**同步中性化为「共现路径 / 共现配对 / 共现判据」（断言代码与数据不动；区块行标题
   `# ── match_in_title: 同句判据纳入标题` → `共现判据纳入标题`）；并实跑确认 radius=1 下全块仍 PASS。

### R. `tests/integration/test_dag_consistency.py`（约 91、102、104、206 行）
- 阶段计数测试的描述串「同句共现硬过滤」→「邻近共现硬过滤」（纯散文，计数 16 不变）。

### S. `CLAUDE.md`
- 顶部新增「**2026-06-29 后续 (stage 12b 口径改回 ±1 句窗口邻近共现, radius 0→1)**」条目：记录
  本决策、取代 2026-06-27、保留 match_in_title、frac_ss_fallback **三态进一步恢复**（§1.3）、
  golden DEFERRED、计数不变。
- 更新 2026-06-27 后续段（约 49–51 行）：标注「**已被 2026-06-29 取代**」，并把其 `_ss` 坍缩
  披露改为三态口径（radius=0+title=False→≈0；radius=0+title=true→部分恢复；radius=1→进一步恢复）。
- **【R2 P2】更新约 51 行「全仓文档口径已统一为"同句共现"」子句**：本次反转后成反事实，须加括注
  改为「(该口径已于 2026-06-29 反转回"邻近共现"，见顶部新条目)」，不留裸反事实断言。
- 更新约 75 行 sentence_radius 沿革注释（引入=1 → 2026-06-27=0 → **2026-06-29 改回=1**）。
- **【R2 P3 protected，严禁翻】**：CLAUDE.md:25（full-only 段「ss 轨 (银行∧金科同句)」提及）、
  line 80-87（v3.9.0 `_ss` 定义「银行+金科同句」）= `_ss` 谱系，**不在本次改动范围**，保留不动。

### T. 本执行计划
- `scripts/audit/STAGE13_COOCCURRENCE_RADIUS0_TO_1_EXECUTION_PLAN_2026-06-29.md`（本文件）。

---

## 4. golden / 数据 / 生产 DEFERRED

- **本机零 parquet 改动**：仅改 config/源码注释/测试/CLAUDE.md，**不动任何 `data/processed/*`**
  （已 gitignore）。盘上 panel/golden 仍为旧宇宙；既有 golden 测试照常（预期 **0 新增失败**，
  与 `7b7cf3a1`/`d78a4503` 同款 baseline-stash-diff 证据）。
- **测度变更 → golden DEFERRED（生产语料机）**：radius 0→1 放宽过滤 → 存活行集变化 → 下游
  panel 派生量变（`n_articles`/`fintech_share` 分子/`attention 族①`/NF/`frac_ss_fallback` 等）。
  生效须：① 生产全量重跑**全链**：stage 13 → **14 (ctx_materializer 重物化存活集，纯 CPU $0)** →
  15/16/21/22/23/24/**25 (article_sbert)**/26 → 40/46/51（21 缓存命中 $0，仅删/恢复行，存活行
  content 不变）。**⚠【R2 P2】与 full-only 段相反**：本次 radius 改在 stage 13 **上游** → stage 25
  article_sbert 读**变化后的存活集**，**本次受影响**（CLAUDE.md:31「stage 25 不受门控影响」是
  full-only 门控在 stage 21 下游的结论，不可套用到本次）；
  ② golden 受控重生（生产机带 `PYTHONHASHSEED=0` + BLAS 线程钉 1，排除 3 个 BLAS-FP 网络中心度列）；
  ③ radius=1 keep 率 gate 实测（读 pre-12b `12_fintech_news.parquet` 作候选集，14.27% 仅 radius=0
  上界估计，radius=1 实际丢行率更低）；④ manuscript/codebook 披露口径由「同句」改回「±1 句窗口邻近」。
- **fintech_share 分母守恒**：12b 只丢/恢复行，分母经「望远镜式坍缩」恒不变（同 §路线 A），不受
  radius 改动影响。
- **勿删 `_llm_cache.db`**（stage 21 复现锚；本次不触碰 LLM）。

---

## 5. 受影响测试逐一核验（radius=1 下预期结果）

| 测试 | radius=1 下 | 处置 |
|---|---|---|
| `test_keep_same_sentence` (r=1) | 同句仍命中 → True | 不变 ✅ |
| `test_keep_adjacent_within_radius1` | 邻句 r=1 命中 → True | 不变 ✅ |
| `test_radius0_requires_same_sentence` | 原语层 r=0 邻句 False / r=1 True | **保留**（原语语义锁）✅ |
| `test_production_default_is_same_sentence` | 断言 radius==0 | **改** → `==1` ✏️ |
| `test_production_config_drops_adjacent_only` | adjacent 现保留 | **改** → keeps_adjacent + 新增 drops_far_apart ✏️ |
| `test_drop_far_apart_radius1` | 距 3 > r1 → False | 不变 ✅ |
| `test_radius_monotone_keeps_when_widened` | r2 False / r3 True | 不变 ✅ |
| `test_drop_bank_only` / `test_drop_fintech_only` | 无共现 → False | 不变 ✅ |
| `test_short_text_charfallback_*`（3 个） | 短文走字符回退、radius 无关 | 断言不变；仅 1 个 docstring 改 ✏️ |
| `test_fintech_ac_none_returns_false` / `test_empty_inputs_*` | 不变 → False | 不变 ✅ |
| `test_filter_keeps_and_drops` (cf, r=1) | d1 同句留 / d2,d3 无共现丢 | 不变 ✅ |
| `test_empty_target_bank_dropped` | 全丢 | 不变 ✅ |
| `test_schema_preserved` | d1 同句留 / d2 无关丢 | 不变 ✅ |
| `test_per_bank_row_granularity` | 工行同句留 / 建行距 3 丢 | 不变 ✅ |
| `test_graceful_degrade_fintech_ac_none` | SAFE-1 全保留 | 不变 ✅ |
| `test_min_keep_guard_raises` (mock r=1) | 无共现全删 → SystemExit | 不变 ✅ |
| `test_production_match_in_title_default_true` | 断言 match_in_title is True | 不变 ✅ |
| `test_title_pairs_kept_when_body_anaphora_only` | 标题救回（同句路径，与 r 无关） | 不变 ✅ |
| `test_neither_title_nor_body_pairs_dropped` | 无配对丢（标题/正文 r=1 邻句也无金科同窗） | 不变 ✅（见下注） |
| `test_match_in_title_false_is_body_only_identical` | a 行正文银行 S0、金科 S2（距 2 > r1）→ 丢；b 行同句留 | 不变 ✅（见下注） |
| `test_empty_or_missing_title_no_regression` | 正文同句留 / 无金科丢 | 不变 ✅ |

> **注（两个潜在边界，须执行时实跑确认）**：
> - `test_neither_title_nor_body_pairs_dropped` 数据：标题「工商银行发布半年报」(银行无金科)、正文
>   「工商银行业绩稳健。该行持续推进数字化转型。区块链项目进展顺利。」。拼接后句序列：
>   `[标题S0(银行), 正文S1(银行), 正文S2(数字化-不在测试词典), 正文S3(区块链-无银行)]`。
>   radius=1 时银行锚句 S0 窗口[S0,S1]、S1 窗口[S0,S2] 均无金科（区块链在 S3，距银行锚句 ≥2）→
>   仍**丢弃**。**断言不变，但因 r=0→1 边界移动，须执行时实跑此测试确认仍 drop。**
> - `test_match_in_title_false_is_body_only_identical` 的 `a` 行正文「工商银行召开会议。今天天气
>   晴朗。该行推进区块链。」：银行 S0、区块链 S2，距 2 > radius 1 → r=1 仍丢；`b` 行同句留。
>   断言 `["b"]` 不变。**须执行时实跑确认。**
>
> 这两条是「断言文本不变但 radius 边界移动」的测试，必须在执行后**实际运行 test_13 全量**核验，
> 不可纸面假定。若任一在 r=1 下结果翻转，须微调测试数据的句距使其语义意图（「非邻近 → 丢」）
> 在 r=1 下仍成立，并在计划评审中记录。

---

## 6. 门禁（执行后必过）

1. `ruff check .` clean（至少改动文件无新增告警）。
2. `python -c "import ast; ast.parse(open(f).read())"` 对每个改动 .py 编译通过 / yaml 可加载。
3. `pytest news_process/tests/test_13_cooccurrence_filter.py -q` 全绿（含改/新增测试）。
4. `pytest news_process/tests/test_entity_context.py news_process/tests/test_content_ctx_materialization.py
   news_process/tests/test_14_materialize_ctx.py -q` 全绿（确认 ss/ctx 轨未被误伤）。
5. `pytest news_process/tests/integration/test_dag_consistency.py -q` 全绿（计数 16 不变）。
6. **baseline-stash-diff**：`git stash` → 全量 `pytest -q` 收集失败集（baseline）→ `git stash pop`
   → 再全量 `pytest -q` → 两失败集**逐项一致**（**0 新增失败**）。这是 golden DEFERRED 的核心证据。
7. 配置一致性：`load_config().get('cooccurrence_filter',{}).get('sentence_radius') == 1`。
8. **【P1/R2 残留核验】口径 grep 闸**（pattern 已按 R2 拓宽）：
   - **gate-1（12b 默认断言清零）**：对每个改动 .py/.yaml `git grep -n 'radius=0' <file>`，逐条人工确认
     残留**仅为通用 radius 语义/学术谱系/动态分支字面量**（如 `[i,i]` 闭区间定义、Andreou 零半径
     最严特例、`_mode` 三目 `if radius==0` 分支标签、`_ss_zero_cooc=0.1427` 基线注释），**无任一条**把
     radius=0 标为「生产默认/生产口径/生产默认 0/生产默认同句/生产 stage 12b 默认已切到 radius=0」。
     全仓 `git grep -nE '生产 ?radius=0|生产默认 radius=0|生产口径.*radius=0|默认已切到 radius=0|生产默认.*同句|生产默认 0 = 严格同句'`
     须为 **0**（除 dedup.py/llms_evaluation.py 的正交「生产口径」）。
   - **gate-2**：`git grep -n '同句判据\|再判同句'` 全仓须为 **0**（这两词仅用于 12b/match_in_title
     判据命名，无 `_ss` 合法用法）。
   - **gate-3**：`git grep -n '②同句共现过滤'` 为 0（phase_durations 键 set/read 两处已中性化）。
   - **gate-4**：每个改动文件 `git grep -n '同句共现' <file>` 残留仅豁免类（`_ss`/`第三轨`/
     `content_ss`/学术谱系/动态 `_mode` 字面量）。

---

## 7. 风险登记与缓解

| 风险 | 等级 | 缓解 |
|---|---|---|
| 误改 `_ss` 轨（content_ss/同句定义）当作 12b 过滤器 | 高 | §2.2 边界铁律；改动按 §3 逐行；ss 测试纳入门禁 4 |
| 误改 `context_window.sentence_radius`/`ss_sentence_radius` | 中 | 明确是不同 config 键，§2.2-2；只改 `cooccurrence_filter.sentence_radius` |
| 两个「断言不变但 radius 边界移动」测试在 r=1 下翻转 | 中 | §5 注；执行后**实跑 test_13 全量**，翻转则微调句距 |
| 散文翻转遗漏（镜像之后代码漂移 → 18 文件集不全） | 高 | **不只靠 mirror 集**：§3 方法学 grep 驱动 + 显式纳入 ctx_materializer 2026-06-28 块(P1#2) 与 match_in_title「同句判据」散文(P1#3) + §6.8 残留 grep 闸 |
| 按陈旧行号机械执行改错位置 / 腐蚀 `_ss` 注释 | 高 | §3 删全部行号，改 grep 驱动 + 逐条人工分类 + `_ss` 豁免白名单(P1#1) |
| 硬编码运行期日志串(②同句共现过滤等)未随 radius 改 → 真跑日志自相矛盾 | 中 | §3.C 全文 grep, phase_durations 键 set/read 两处同改防 KeyError |
| 误重生/误碰 data/processed 或 golden | 高 | §2.2-5/6；by-name 提交，排除 data/ 与 constants.json |
| 把 `match_in_title` 一并退回 false | 中 | §2.2-4；保留 true；门禁含 `test_production_match_in_title_default_true` |
| 跑 pytest 触发 `data/processed/.../v3_5_1_constants.json` bump | 低 | 提交前 `git checkout` 还原该文件，**绝不 stage** |

---

## 8. 执行顺序（建议）

1. `config/filtering.yaml`（值 + 三处散文）→ `config/paths.yaml`。
2. `pipeline/filtering/cooccurrence_filter.py`（docstring + 日志框架 + banner）。
3. `core/text/entity_context.py`（docstring）。
4. `core/dag.py` / `core/reporting.py` / `core/schemas.py`。
5. `pipeline/filtering/__init__.py` / `pipeline/filtering/fintech_intensity.py` /
   `pipeline/text/ctx_materializer.py` / `pipeline/audit/stats_excel.py`。
6. `run_pipeline_function.py` / `validation/media_diversity.py` / `validation/radius_sensitivity.py`。
7. `13_cooccurrence_filter.py`（shim docstring）。
8. `tests/test_13_cooccurrence_filter.py`（改 2 + 新增 1 + docstring）/ `tests/integration/test_dag_consistency.py`。
9. `CLAUDE.md`。
10. 跑门禁 §6 → 残留 grep 核验 → 提交。

---

## 9. 提交与推送

- **by-name** `git add` 仅本计划涉及的源码/config/测试/文档文件 + 本计划 md；**严格排除**
  `data/processed/*`、`tests/fixtures/golden_panel_v0.json`、`*/v3_5_1_constants.json`、
  任何并发会话的无关改动。
- commit message：`feat(filtering): stage 13 共现口径 radius 0→1 (严格同句→±1 句窗口邻近共现, 保留
  match_in_title; golden-DEFERRED)`，正文记录决策/取代 2026-06-27/frac_ss_fallback 恢复/计数不变/
  baseline-stash 0 新增/权威计划路径，末尾 `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`。
- 推送 `main`（pre-commit 钩子全过，不 `--no-verify`）。

---

## 10. 计数断言（不变）

STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16。纯阶段内判据
参数 + 标签/披露改动，无阶段/列增删。
