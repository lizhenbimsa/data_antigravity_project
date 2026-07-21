# LLMs_for_FinTech_dic 盲审「每家 3 次调用 + 内部 2-of-3 投票 + 过半数入选」执行计划 (v3, 终审版)

- **日期**: 2026-07-21 (v2: 方案 B 定稿 + 规模数字按盘上 manifest 实证纠正; **v3: 入选门槛按用户裁定由 >2/3 回调为严格过半数, 全部 13 处阈值触点逐一亲验枚举**)
- **状态**: 已终审, 待用户批准实施 (P5 付费门另行授权, 见 §8)
- **两项用户裁定** (2026-07-21):
  1. **方案 B** — 三轮统一新 tag `judge|rep{r}|try{n}` (r∈{0,1,2}), 现有判别缓存不再被新跑复用 (条目保留在库、不删除, 供历史 v1 manifest 冻结重放继续使用)。
  2. **入选门槛 = 严格过半数** (>1/2): `total_score > len(JUDGE_MODELS) * 0.5`, 13 家 → >6.5 → **≥7 票**入选 (取代现行 >2/3 → ≥9 票)。
- **范围**: 仅 `LLMs_for_FinTech_dic/` 判别 (盲审) 阶段。**生成阶段 `fetch_batch`/`build_generate_prompt`/`MODELS`/`NUM_REPEAT_PER_MODEL` 及其上游零触碰** (用户 2026-07-21 铁律)。
- **上位计划**: `LLMSDIC_JUDGE_REPLAY_EXECUTION_PLAN_2026-07-21.md` (复现三件套, 已验收, main=4e52dc9f+fbe354e2)。本计划叠加其上。

---

## 0. 白话版: 这次到底要干什么

现在的盲审: 候选词切批 (每批 100 词), 13 个大模型**每家对每批只判一次**, 一家一票, 拿到 9 票以上才进机器词典。

升级为两件事:
- **每票加内部复核**: 每家模型对每批**判 3 次** (3 次各自独立成功调用), 模型内部"三局两胜"——3 次里至少 2 次判"是", 这家才算投出赞成票。防止单次采样的偶然答案直接成为正式票。0/1 判分 + 3 轮 → 模型内永无平票。
- **入选门槛改为超过一半**: 13 家里拿到 **7 票及以上** (超过 13 的一半 6.5) 就入选, 不再要求 9 票。13 是奇数, 不存在"恰好一半"的平票。

配套 (白话):
1. **账记全**: 结果 Excel 里每家模型 3 轮判分、3 轮理由、内部投票各自成列 (每家 2 列 → 7 列), 逐票可核对。
2. **每次调用独立进缓存**: 缓存键带轮序号, 三轮绝不共用一个槽位——否则第 2、3 轮只是重放第 1 轮, "三局两胜"变假投票。
3. **完美可复现**: 跑完设 `LLMS_DIC_OFFLINE=1` 复跑, 0 付费、逐字节同结果; 复现三件套 (判决/manifest/验钞机) 全部升到"3 轮"口径, manifest 新增记录投票协议参数。
4. **花钱先报价**: 方案 B 下判别全量新付费, 按当前冻结词表约 **273 次调用** (13 模型 × 7 批 × 3 轮), 用户授权后才真跑。门槛改动本身 $0 (纯本地比较, 不进缓存键)。
5. **手稿同步**: 手稿已有 v2 banner 声明"代码已切 v2、数值待付费真跑"; 本次两项协议变更 (三轮投票 + 门槛回调) 追加进 banner, 真跑后回填全部数字。
6. **顺手修真伤**: 主测试套件现存 2 个红灯 (§5.3)。**门槛回调恰好自愈其中一个** (S2 测试的正则锚的就是过半数 `* 0.5` 形态, 07-17 收紧 2/3 时未同步才红); 另一个 (S12) 一并修复。

## 1. 现状基线 (2026-07-21 逐条亲验, 非记忆)

| 事实 | 证据位置 |
|---|---|
| 13 家判别模型; 现行门槛 `> len(JUDGE_MODELS) * 2 / 3` → ≥9 票 | `config.py::JUDGE_MODELS` / `00:1727` |
| 每家每批判 1 次; try 序号只为解析重试 | `judge_batch` (`00:1066`), tag=`judge\|try{n}` (`00:1107,1116`) |
| **最新冻结口径: 696 词 / 7 批 / 13 模型 = 91 任务** (verdict 9048 格按词计 = 13×696) | `judge_manifest_20260721_021518.json` 实读 |
| 审计键 (model, batch_idx); manifest 任务键 `{model}\|batch{bi}`; schema v1; **不含门槛字段** | `00:736,744,904,913` + manifest 实读 |
| 验钞机按 `judge\|try{n}` 枚举, schema 门只认 v1 | `verify_judge_cache_coverage.py:40,85` |
| 冻结重放 `--judge-only --from-manifest`, schema 门只认 v1; DataFrame 构建与 main **双副本** | `00:1930-` |
| claude 两家温度参数被过滤 → 三轮真随机采样; 其余 11 家零温 (三轮可能同答) | `SAMPLING_PARAM_FILTERED_MODELS` 披露 |
| Excel 条件格式只认表头 `endswith("_score")`/`total_score` | `_format_excel_workbook` (`00:1393`) |
| 日志分析器判别正则要求 `批次\d+\]` 紧邻 | `02_analyze_log.py:150,160,169` |
| κ 脚本硬编码读 `bank_keywords_20260302_011050.xlsx` (**盘上已不存在** → 现即报 Error), 列选 `endswith('_score')` | `calculate_kappa.py:90,92` |
| 本目录 `tests/` **为空**; 真正的门在主套件 `tests/test_prompt_audit_s2_s12.py`, 现有 2 红 | §5.3 pytest 实跑证据 |
| **"2/3" 阈值触点全枚举 = 13 处**: `00:289,328-329,1613,1721-1723,1727,1877-1883` (10 处) + `02_analyze_log.py:187,299` (2 处) + 手稿 banner `:3` (1 处); `config.py`/`academic.py`/验钞机/主套件其它测试**零触点** | 全目录 + tests/ grep 实证 |
| dry-run 只估生成阶段, 不估判别 | `00:1454-1474` |
| `bank_keywords_*.xlsx` 判别列**无任何目录外消费方** (主仓 `bank_keywords_file` 指银行名 JSON, 同名不同物) | 全仓 grep 实证 |
| 手稿 v2 banner 已声明「v1 数值失配、v2 数量链与 κ 待付费真跑、勿引用」, 其中记 "2/3 超多数阈值 ≥9 票" | `FinTech_Dictionary_LLMs_Paper_Final.md:3` |

**零触碰清单**: `build_generate_prompt` / `build_judge_prompt` / `REASONS` / `fetch_batch` / `MODELS` / `DOMAINS` / 既有缓存条目 (含旧 judge 条目, 保留不删) / `config/fintech_dict.json`。两个 Prompt 一个字都不改。S2 测试的三个文本锚 (`fix(S2` 字面 / "阈值不进…缓存键" 声明 / 严格 `>` 比较符) **必须保留**。

## 2. 核心设计

### 2.1 config 常量
```python
NUM_JUDGE_REPS: int = 3                    # 模型内 self-consistency 判别轮数
JUDGE_REP_MAJORITY: int = NUM_JUDGE_REPS // 2 + 1   # = 2 (三局两胜门)
```
注释写明: 运行期协议参数, 非 Prompt 字段; 手稿锁步影响走 banner 披露 (§7)。

### 2.2 入选门槛回调 (v3 新增, 用户裁定)
- 表达式 `00:1727` 改为: `df_final["total_score"] > len(JUDGE_MODELS) * 0.5`
  - **刻意写 `* 0.5` 而非 `/ 2`**: 主套件 S2 测试正则锚定 `len\(JUDGE_MODELS\)\s*\*\s*0\.5` 且断言比较符为严格 `>` ——此形态使现存红灯 S2 **零测试改动自愈**, 并延续该测试"禁回退 `>=` 含平票"的守门语义。
  - 13 家 → >6.5 → ≥7 票; 平票仅当偶数家时可能出现, 严格 `>` 本就排除。
- 注释台账 (`00:1721-1723`) **追加**日期条目 (不删历史): `更新(2026-07-21): 由 2/3 严格多数回调为严格过半数 (>1/2), 用户裁定; 当前 13 家 → >6.5, 即至少 7 票`; 保留 `fix(S2` 与"阈值不进 LLM 缓存键"字面 (测试锚)。
- `_min_pass` (`00:1880`) 改 `len(JUDGE_MODELS) // 2 + 1` (=7); 口径声明文本 (`00:1877-1883`) 同步改"严格过半数", 平票注记改为"恰好半数仅偶数家存在; 13 家奇数无此临界票"。
- 其余 5 处**叙述性文本**同步: `00:289` (阶段注释) / `00:328-329` (run header: "2/3 严格多数 (supermajority)" → "严格过半数 (strict majority, >1/2 家)") / `00:1613` (判别阶段日志) / `02_analyze_log.py:187,299`。
- **收口 grep 门**: 改完后 `grep -n "2/3\|三分之二\|8\.67\|supermajority" 00_LLMs_for_dic.py 02_analyze_log.py` 仅允许命中注释台账里的**历史条目行** (1721-1723 一带), 活语义文本 (日志字符串/表达式/口径声明) 零命中。
- 门槛不进 LLM 缓存键 (既有事实) → 本项改动 $0、与缓存/复现完全正交。

### 2.3 缓存 tag (方案 B 统一命名)
- 三轮一律 `judge|rep{r}|try{attempt}` (r∈{0,1,2})。轮序号必须进 tag: 判别是 temperature=0 同 prompt, 不带 rep 三轮即折叠成同一缓存条目 → 假投票。
- **旧条目处置**: 旧 tag `judge|try{n}` 条目保留在库 (不删、不迁移)。对新跑是死重 (~91 条级别), 但**是历史 v1 manifest 冻结重放的活依赖** (§4.4)。
- 后果如实披露: 新跑判别缓存全量 miss → 全额付费 (~273 次); 既有三份 v1 manifest 的"离线 $0 复现"能力**不受影响** (走 legacy tag 路径)。

### 2.4 `judge_batch` 改造
- 任务元组追加 `rep`: `(model, batch, batch_idx, rep, client_config)`; 返回值 `(model, rep, batch_results)`; task_id = `判别-{model}/批次{b}/轮{r+1}`。
- **tag 选择**: `rep` 为 int → `judge|rep{r}|try{attempt}`; `rep=None` (仅 v1 manifest 冻结重放传入) → legacy `judge|try{attempt}`。`_audit_tag`/`_audit_key` 与真实 cache_tag 严格同构 (双处同步, 沿用既有注释纪律)。
- 轮内解析重试 / ≥95% 部分采纳 / 打捞兜底 / 健康跳过 / 退避 / 费用保护逻辑**逐字保留**, 作用域从 (model,batch) 变 (model,batch,rep)。
- ⚠ 改动区间含 S12① 修复现场 (`for item in results_list: … result_map[kw] = (sc, rs)`), 该块是主套件沙盒测试的文本切片锚 — 块内结构 (try/except (TypeError, ValueError) + fix(S12 tag) 保持不动 (§5.3)。

### 2.5 主循环与投票
- 任务列表 = 13 模型 × 7 批 × 3 轮 = **273 任务** (数字随词表动态, 此处按当前冻结词表); 仍统一 shuffle + 线程池。
- 收集结构: `model_results[(model, rep)][kw] = [score, reason]`。
- 模型内投票 (纯本地, $0): `vote = 1 if Σ score_r0..r2 ≥ JUDGE_REP_MAJORITY else 0`; 缺轮 (hard_fail/health_skip 该轮补 0) 不改变公式, 由判决块曝光 (§4.1)。
- `total_score` = 13 家 vote 之和; 入选 = `total_score > len(JUDGE_MODELS) * 0.5` (§2.2)。

## 3. Excel 列契约

`5-AI判别结果` (及自动继承 df_final 的 `判别-{领域}` sheet), 每家模型 7 列:
```
{key}_score_r1  {key}_score_r2  {key}_score_r3     # 三轮原始判分 0/1
{key}_reason_r1 {key}_reason_r2 {key}_reason_r3    # 三轮理由 (序号已反查全文)
{key}_vote                                          # 内部 2-of-3 投票 0/1
```
- 列序: `id, keyword, total_score, [每家 7 列 × 13], …` ≈ 94 列。
- `total_score` 列名不变、语义变为"13 张内部多数票之和"——在口径声明处 (`00:1877-1884`) 补 vote 语义 (与 §2.2 门槛改文合并为一次改动)。
- **`_format_excel_workbook` 必改** (亲验发现): 条件格式匹配 `endswith("_score")` 对 `_score_r1..3`/`_vote` 全不命中 → 新列丢失红绿着色。改为正则匹配 `(_score(_r\d+)?|_vote|total_score)$`。
- **两处 DataFrame 构建副本同步改**: `main()` 与 `judge_replay_from_manifest()` (镜像 stage21 双门控教训)。

## 4. 复现三件套升级

### 4.1 判决 `_emit_replay_verdict`
- 审计键 (model, batch_idx) → (model, batch_idx, rep); 任务全格 = 13×7×3 = **273 任务无缺格**; 五路终局计数按 (任务=轮) 统计。
- 聚合对账双层: 分数格 13×696×3 = **27,144** + 投票格 13×696 = 9,048 (投票由分数纯函数派生, 对账分数格即足, 投票格作冗余核验)。
- 判决 dict 新增 `n_judge_reps`; STRICT_REPLAY 语义不变 (任何轮降级即不过)。

### 4.2 manifest v2
- schema → `llmsdic-judge-manifest/v2`; 任务键 `{model}|batch{bi}|rep{r}`; 新增协议字段 (复现凭证完备性):
  `n_judge_reps: 3` / `rep_majority: 2` / `final_vote_threshold: "> n_models * 0.5"` + 解析后最小票数 (13 家 → 7)。
- 其余字段 (wordlist_sha256/env/冻结口径) 照旧。

### 4.3 验钞机 `verify_judge_cache_coverage.py`
- **双版本**: v1 → 按 legacy tag `judge|try{n}` 枚举 (现行为逐字节保留, 历史三份 manifest 的核验能力不摧毁); v2 → 按 `judge|rep{r}|try{n}` 枚举 (model × batch × rep × try 全键)。

### 4.4 冻结重放 `--judge-only --from-manifest`
- schema 门放行 v1+v2; `n_judge_reps` = manifest 记录值 (v1 缺省 1)。
- v1 重放传 `rep=None` → legacy tag → 命中旧缓存条目 → **改造后 v1 重放行为与今日逐字节一致** (P3 验收项)。⚠ 唯一预期差异: 若重放路径复用新的入选/统计口径文本, 以冻结重放"只产判别语义 sheet"的现状为准——v1 重放产物比对以 `5-AI判别结果` 数值格为准。
- v2 重放按三轮全格重放。
- **修订 (2026-07-21 用户裁定, 实施后追加)**: 重放产物由「判别语义精简件 (4/5 两 sheet)」升级为**全阶段完整 workbook** — 生成阶段各 sheet 从 `manifest.run_output_file` 首跑产物**只读拷贝** (生成阶段零触碰铁律不破, 不执行任何生成计算, sheet 顺序保持首跑原样); 判别语义 sheet (`5-AI判别结果`/`判别-*`) 以重放结果重建; `4-最终结果` 恒以 manifest 冻结词表为准 (sha256 已验); 统计总览「AI认可」列 v2 口径按 manifest 冻结门槛重算 (v1 无冻结门槛字段→原样拷贝并留痕); 首跑产物缺失 → loud WARNING 降级回精简件。验收 (已过): v2 重放 14/14 sheet 与首跑产物逐格 0 差异; v1 重放判别语义两 sheet 与改前精简件 0 差异格 + 生成 sheet 完整拷贝。

## 5. 下游消费方同步 (逐个亲验后的完整清单)

### 5.1 `02_analyze_log.py`
- 三处判别正则 (`:150,160,169`) 形如 `\[判别-(.+?)/批次\d+\] 成功判别`, 要求 `批次\d+` 后**紧邻** `]`。新 task_id 含 `/轮{r}` → **三条正则全部静默失配, 判别统计归零** (不报错, 最危险的失败形态)。修复: `批次\d+(?:/轮\d+)?\]`, 可选组保证旧日志向后兼容。
- 两处 "2/3 严格多数" 叙述 (`:187,299`) → "严格过半数" (§2.2 收口 grep 门覆盖)。

### 5.2 `calculate_kappa.py`
- 更正记录 (v1 计划断言有误): 新列名 `_score_r1..3` **不会**被 `endswith('_score')` 误抓——真实问题是指向新产物时一列都抓不到。
- 亲验另发现: 硬编码输入 `bank_keywords_20260302_011050.xlsx` 盘上已不存在, 脚本当前即报 Error (慢性陈旧, 非本计划造成, 如实披露)。
- 修复: 输入参数化 (`--file`, 缺省取最新 `bank_keywords_*.xlsx`); sheet 名动态 `判别-{DOMAINS[0]['name']}`; 评分列优先抓 `_vote` (13 家正式票的 κ), 无则回退 `_score` (v1 产物兼容); 另输出轮内一致率 (3:0 vs 2:1 占比) 作 self-consistency 描述统计。
- ⚠ κ 口径从"13 次单判"变"13 张内部多数票", 预期上移 (投票吸噪), 与 v1 κ=0.5017 不可比, 手稿披露。κ 与入选门槛无关 (门槛改动不影响 κ)。

### 5.3 主套件 `tests/test_prompt_audit_s2_s12.py` — **HEAD 现存 2 红 (pytest 实跑证据, 非本计划造成)**
```
FAILED test_s2_threshold_is_strict_majority        # 正则锚 `* 0.5`, 代码 07-17 改 `* 2 / 3` 未同步
FAILED test_s12_bad_score_item_is_skipped_not_raised  # 沙盒 exec 缺 reason_text_from_index (07-19 引入未同步) → NameError
```
- **S2: 本次门槛回调即自愈, 零测试改动** (§2.2 刻意 `* 0.5` 形态; 其附属断言——严格 `>`、`fix(S2` 字面、"不进…缓存键"声明——由零触碰清单保证)。P3 复跑验证转绿。
- **S12: 修测试** — 沙盒 namespace 注入 `reason_text_from_index` (从 config import 或最小桩)。
- **A/B 基线纪律**: 实施前存档基线 = 2 红; 验收 = 0 红且全仓不新增红灯。
- 本目录 `tests/` 为空 (亲验); 新增测试放主套件 `tests/test_llmsdic_judge_reps.py` (纯文本结构断言 + 沙盒, **绝不 import** 00 脚本本体, 沿用既有纪律), 覆盖: ① 三轮 tag 互异且与 legacy tag 互异 (防折叠); ② 投票函数 2-of-3 边界 (含缺轮); ③ 门槛表达式为 `> … * 0.5` 严格形态 (与 S2 互补, 锚 13 家 → ≥7 语义); ④ manifest v1/v2 双版本枚举; ⑤ `02_analyze_log` 新旧 task_id 双格式命中。

### 5.4 无影响项 (亲验排除, 勿再触碰)
`01_test_models.py` (连通性探针) / `diag_claude.py` / `academic.py` (无阈值触点) / `verify_judge_cache_coverage.py` (无阈值触点, 只动 §4.3 的 rep 枚举) / 主仓 `bank_keywords_file` (同名不同物的银行名 JSON) / `银行金融科技词典20260715.xlsx` (v1 发表冻结件) / 主项目 `fintech_dict.json` (是否换发新词典 = 独立决策, 本计划不做)。

## 6. 确定性与统计披露 (进日志)

- 零温 11 家: 三轮大概率同答 → 内部投票多为 3:0。不是浪费: 把"该模型是否真确定"变成可证事实, 轮间翻转全被记录; claude 两家 (温度被过滤) 三轮真随机, 本改造对其收益最大。既有零温例外披露注释/WARNING 全保留, temp_key 仍 "0" 不改。
- `_log_run_header` 补一行: 判别协议 = 每家 `NUM_JUDGE_REPS` 轮 self-consistency + 13 家严格过半数 (≥7 票) 两层投票 (引文仅用 academic.py 引文池已有 handle, 不硬造)。
- dry-run 补判别规模行: 公式 `13 × ceil(词数/100) × 3`, 并读最新 manifest 给参考数 (696 词 → 273 任务); 无 manifest 时只打公式。

## 7. 手稿锁步

- 手稿处于「v1 数值冻结 + v2 banner 声明失配、勿引用」状态 (亲验 `:3`, banner 现记 "2/3 超多数阈值 ≥9 票"), 因此本次改 config 不产生新的"当场证伪"——但 banner 必须**在 P1 同批**追加一条 2026-07-21 条目, **同时记两项协议变更**: ① 判别升级为每家 3 轮内部 2-of-3; ② 入选门槛由 2/3 超多数 (≥9) 回调为严格过半数 (>1/2, ≥7); v2 数量链/κ 待付费真跑。
- P6 (真跑后): 方法段重写两层投票协议; 数量链末位、κ (新口径, 注明与 v1 不可比)、AI 认可数一律用真跑产物回填, **严禁占位编造**; Prompt 誊抄块零改动。

## 8. 执行顺序与授权门

| 步骤 | 内容 | 付费 | 门 |
|---|---|---|---|
| P0 | 改前基线: 跑 `test_prompt_audit_s2_s12.py` 存档 2 红基线; 备份最新 manifest/xlsx 清单 | $0 | — |
| P1 | config 常量 + **门槛回调 (§2.2, 含 13 处触点)** + `judge_batch` rep 化 + 主循环/投票/Excel 双副本 + `_format_excel_workbook` + banner 追加 | $0 | — |
| P2 | 三件套 v2 (判决/manifest/验钞机双版本) + `02_analyze_log` 正则 + kappa 参数化 + S12 测试修复 + 新增测试 | $0 | — |
| P3 | 离线验证: ① S2 测试自愈复核 + 全仓 pytest 对基线 A/B; ② `LLMS_DIC_OFFLINE=1 --judge-only` 用 **v1 manifest** 重放 → 判别数值格与改造前 0 差异 (legacy tag 回归证明); ③ 验钞机 v1 模式对三份历史 manifest 照旧盖章; ④ §2.2 收口 grep 门 | $0 | — |
| P4 | dry-run 报价: ~273 次判别调用 (13×7×3, 按当前冻结词表) + 生成阶段 0 新增 (全缓存) | $0 | **用户付费授权** |
| P5 | 在线真跑 (`LLMS_DIC_STRICT_REPLAY=1` 建议首跑即开): 生成阶段 $0 缓存重放 → 判别 273 任务全新付费; 跑完立即 `LLMS_DIC_OFFLINE=1` 全流程复跑 + 验钞机 v2 盖章 | 💰 | P4 授权后 |
| P6 | 手稿回填 (数量链/κ/方法段) + memory 更新 + 按文件名分批 commit (绝不 `git add .`) | $0 | — |

P5 运维注记: `MAX_TOTAL_RETRIES=50` 全局费用保护在 273 次全新调用下可能被瞬时故障耗尽 → 中断后**直接原样重跑即断点续传** (已入缓存的槽位 $0 命中, 只补 miss), 不调参不清库。

**验收标准** (全部亲验可复核):
1. 离线复跑与真跑产物 0 差异格; 验钞机 v2: 273 任务全键 0 miss / 0 漂移 / 0 降级;
2. v1 manifest 重放判别数值格与改造前逐字节一致 (legacy tag 回归);
3. 每家 7 列齐全; 每词每家 `vote == (Σ3轮 ≥ 2)`; `total_score == Σ vote`; **入选集 == `total_score > 13 * 0.5` (≥7 票)**;
4. `test_prompt_audit_s2_s12.py` 从 2 红 → 0 红 (S2 靠门槛回调自愈、S12 靠测试修复), 全仓无新增红灯 (基线 A/B);
5. 三轮缓存键两两互异且与 legacy 键互异 (测试硬锁);
6. §2.2 收口 grep 门: 两脚本活语义文本中 "2/3 / 三分之二 / 8.67 / supermajority" 零残留 (注释台账历史条目除外);
7. 手稿 banner 已含两项协议变更条目; 真跑后数字全部来自盘上产物。

## 9. 风险与雷区 (终审全表)

| # | 风险 | 防线 |
|---|---|---|
| R1 | 缓存折叠 (rep 不进 tag → 假投票) | tag 规范 §2.3 + 测试硬锁 |
| R2 | main/replay 双副本漂移 | §3 显式双改 + P3 对拍 |
| R3 | 验钞机/重放 schema 门只认 v1 → 历史 manifest 验伪或 v2 拒放 | §4.3/4.4 双版本 |
| R4 | `02_analyze_log` 判别统计**静默归零** (正则失配不报错) | §5.1 可选组 + 双格式测试 |
| R5 | 新列丢条件格式 (endswith("_score") 失配) | §3 正则化匹配 |
| R6 | kappa 抓不到列 / 输入文件已缺失 | §5.2 参数化 + `_vote` 优先 + 慢性陈旧披露 |
| R7 | 主套件 2 现存红被误归因于本改动 / 修复被误判夹带 | P0 基线存档 + §5.3 单列披露 |
| R8 | S2/S12 测试的文本锚被重构破坏 (阈值 `* 0.5` 严格 `>` 形态、fix-tag 注释、"不进缓存键"声明、result_map 块结构) | §1 零触碰清单 + §2.2/§2.4 锚保持 |
| R9 | 门槛文本 13 处触点漏改 → 日志/手稿声称 2/3 而代码已是 1/2 (声明与行为背离) | §1 全枚举 + §2.2 收口 grep 门 (验收 6) |
| R10 | 生成阶段误触 | diff 自查红线: `fetch_batch`/`build_generate_prompt` 零变更 |
| R11 | 手稿失配 | §7 banner 同批 (两项变更并记) + P6 真跑回填 |
| R12 | 费用保护中断留缓存空洞 | P5 注记: 原样重跑断点续传; STRICT 门拒绝带洞出结果 |
