# Stage 13 同句共现判据纳入标题 — 执行计划 (2026-06-29)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 状态: **草案 / 待用户批准**。本计划只描述改动, 不含已落地代码。
> 作者上下文: 由"stage 21 full-only 留篇 vs stage 13 同句硬过滤"数据流讨论收敛而来。

## 0. 一句话

把 stage 13 (12b) 银行×金科**同句共现保留判据**的扫描文本从「**仅正文** `内容`」改为「**标题 + 正文**」(`prepend_title(标题, 内容)`), 让"**标题已点明 银行∧金科**"的报道即便正文用指代/承前省略主语 (银行别名与金科词被分到不同句) 也能保留 —— 与下游 stage 21 full 轨 (读 `content_full = 标题+正文`) 的口径对齐, 堵上 stage 13 唯一一种 stage 21 无法修复的**单向假阴性** (错删真报道)。

## 1. 动机 (问题精确陈述)

- **现状**: stage 13 判据只读正文 `df['内容']` ([cooccurrence_filter.py:162](../../pipeline/filtering/cooccurrence_filter.py#L162)), radius=0 要求**银行别名与金科词在同一正文句内**共现, 否则**硬删行**。
- **不一致**: stage 21 full 轨读的是 `content_full = 标题 + 正文` ([ctx_materializer.py:166](../../pipeline/text/ctx_materializer.py#L166))。即 **stage 13 看不到标题, stage 21 看得到标题**。
- **后果 (单向、不可逆、不可观测的假阴性)**: 一篇标题已写明《X银行加码区块链》、正文用"该行/其/承前省略主语"行文 (银行全名与金科词跨句) 的报道:
  - stage 13 (仅正文, 同句) → **删**;
  - stage 21 full 轨 (标题+正文) 本可凭标题判为真报道 → **但永远看不到它** (stage 13 在上游已删)。
- **为什么标题口径是最干净的修法**: 若**标题本身**就把"X银行 + 金科词"并在一句, 这篇按任何合理标准都**是**银行金科报道, 保留它**几乎零假阳性风险** → 精度不降、召回回补。

> 范围声明: 本改动**只**修 stage 13 的"标题盲区"假阴性 (type-b 中最干净、最可辩护的一类)。它**不**处理"标题也没点明、正文纯指代跨句"的更深尾巴 (那需放宽 radius 或更激进语义, 留作 robustness 网格量化, 见 §7)。

## 2. 精确语义 (radius=0 下)

改后保留判据 = 「`标题+正文` 切句后, **存在某一句同时含 (银行别名) ∧ (金科词)**」。

- 标题经 `prepend_title` 成为前导句 ([entity_context.py:67](../../core/text/entity_context.py#L67); 标题非句末标点则插中文句号分隔, 故标题自成一句)。
- 若标题这一句内同时有银行别名与金科词 → **命中保留** (这是新增能保下来的那批)。
- **刻意不跨句桥接**: radius=0 仍是严格同句, **不会**把"标题里的银行名"与"正文里的金科词"跨句配对 (那是被否决的更松方案, 见 §3)。
- `标题=''`/缺失 → `prepend_title` 原样返回正文 → **与旧行为字节一致** (无标题的行零回归)。
- `内容` 以标题开头 (部分抓取源把标题嵌进正文) → `prepend_title` 的 `startswith` 守卫不重复拼接, 无双标题伪命中。
- 短文 (<3 句) 走 `_char_level_fallback` 字符窗: 拼标题后, 标题若自身在 ±150 字内配对 → 命中, 口径一致。

## 3. 备选方案与取舍

| 方案 | 语义 | 裁决 |
|---|---|---|
| **A (本计划)** | 标题 prepend 进文本, 仍 radius=0 严格同句 | ✅ **采纳**。只保"某一句 (含标题句) 配对"的报道; 精度近乎不降, 召回回补"标题点题"那批 |
| B | 标题供银行名, 允许与正文任意金科句跨句桥接 | ❌ 太松。等价"标题提了银行 ∧ 正文任意处提金科即留" → 把 stage 13 要砍的虚假相关又放回来 |
| C | 放宽 `sentence_radius≥1` | ❌ 偏题。那是另一维稳健性 (已由 65_radius_sensitivity 覆盖), 不针对"标题盲区"且会同时放大正文侧噪声 |

## 4. 代码改动 (外科最小)

### 4.1 `pipeline/filtering/cooccurrence_filter.py`

1. import 增 `prepend_title`:
   ```python
   from news_process.core.text.entity_context import (
       get_target_aliases,
       has_bank_fintech_cooccurrence_within_radius,
       prepend_title,            # 新增
   )
   ```
2. `filter_cooccurrence()` 取列+循环 (现 L155–182) 改为:
   ```python
   _match_in_title = _cfg.get('match_in_title', True)   # 默认开
   _banks  = df['target_bank'].tolist() if 'target_bank' in df.columns else [None]*len(df)
   _bodies = df['内容'].astype(str).tolist() if '内容' in df.columns else ['']*len(df)
   _titles = (
       df['标题'].fillna('').astype(str).tolist()
       if (_match_in_title and '标题' in df.columns) else ['']*len(df)
   )
   keep = []
   for target_bank, body_full, title in zip(_banks, _bodies, _titles):
       if not _is_valid_bank(target_bank):
           keep.append(False); continue
       tb = str(target_bank).strip()
       if tb not in _alias_cache:
           _alias_cache[tb] = get_target_aliases(tb, _bnf)
       # match_in_title: 把标题拼到正文前再判同句 → 让"标题已点明 银行∧金科"的报道
       # 即便正文用指代/承前省略主语 (别名与金科词跨句) 也保留, 与 stage 21 full 轨
       # (读 content_full=标题+正文) 对齐。title='' 时退化为纯正文判据 (旧行为字节一致)。
       text_for_match = prepend_title(title, body_full) if _match_in_title else body_full
       keep.append(
           has_bank_fintech_cooccurrence_within_radius(
               text_for_match, _alias_cache[tb], FINTECH_AC,
               sentence_radius=_sentence_radius,
               negation_ac=NEGATION_AC,
               short_name_exclusions=SHORT_NAME_EXCLUSIONS,
               context_window=CONTEXT_WINDOW,
               fallback_char_radius=_fallback_char_radius,
           )
       )
   ```
3. **provenance sidecar** `_write_sidecar_meta` 的 `criterion` 串追加 `|match_in_title={_match_in_title}` → `criterion_sha256` 反映新语义 (审稿可追溯)。
4. **日志** `_log_environment_and_config` / 结果分析块加一行: 打印 `match_in_title` 取值 + "标题已纳入同句判据"。(纯日志, golden 无关。)

> ⚠ **`match_in_title=False` 分支 = 现行盘上 golden 的字节级旧行为** (`text_for_match=body_full`)。故 flag 关时与既有 golden 完全兼容, 为 §7 消融提供"旧宇宙"基线。

### 4.2 `config/filtering.yaml`

`cooccurrence_filter` 块加键 (现 L131–133):
```yaml
cooccurrence_filter:
  sentence_radius: 0
  min_keep_frac: 0.001
  match_in_title: true     # 新增: 同句判据纳入标题 (标题+正文一起切句判共现);
                           #   true=与 stage 21 full 轨口径一致, 保住"标题点明银行∧金科"的报道;
                           #   false=旧行为(仅正文), 供消融/复现旧 golden 宇宙。
```
并在块上方注释补一段"标题盲区"披露 (镜像既有"路线A纯接受-披露"风格)。

### 4.3 `tests/test_13_cooccurrence_filter.py` (加锁)

- `test_title_pairs_kept_when_body_anaphora_only`: 标题《建设银行加码区块链应用》+ 正文"该行…区块链…"(银行名与金科词跨正文句) → `match_in_title=True` **保留**; `False` **丢弃**。
- `test_neither_title_nor_body_pairs_dropped`: 标题《建设银行发布半年报》(无金科) + 正文跨句 → 仍**丢弃** (标题未配对, 不误放)。
- `test_match_in_title_false_is_body_only_identical`: flag=False 时 keep mask 与纯正文判据逐行相等 (golden-compat 锁)。
- `test_empty_title_no_regression`: 标题缺失/空 → 与旧行为一致。
- (可选) 短文 + 标题配对走 char-fallback 命中锁。

## 5. 下游 / golden 影响

- **keep 率 ↑** (回补"标题点题"被误删的行) → `min_keep_frac` 下限守卫更安全, 不触发误删中止。
- **测度变更 → golden DEFERRED (生产语料机)**: 存活行集变大 → 链路 13→14→15→16→21→22→23→24→40→46→51 的统计宇宙整体右移 (n_articles/情感/强度/面板)。镜像本仓所有测度变更惯例: **不动盘上 parquet, 本机 0 新增失败**; 生效须生产全量重跑 + golden 受控重生。stage 21 缓存命中不受影响 ($0): 新增存活行的 content 由 stage 14 物化, 其 LLM 投票若该文之前因别轨已缓存则命中, 否则首跑付费 (仅限真正新进入候选集的文章)。
- **stage 21 仍是最终 full-only 留篇门 (本改动零触碰)**: 这一步只**加宽 stage 21 能看到的候选集**, 完全服务"让最强的全文裁判先看到再决定"的口径; 是否最终留篇仍由 `llm_verified_full` 定。
- **副作用 (正向): 回补 `_ss` 回退变异**。新增存活行的正文无"银行∧金科同句" → 其 `ss_is_fallback=True` → 缓解既有 `frac_ss_fallback→≈0` 坍缩 (config 注释里"留另议"的那条), 让 `ss_is_fallback` 指示列恢复非零方差。须在披露里点明。
- **计数不变**: STAGES_MAIN=16 / STAGES_VALIDATION=16 / thin shim=35 / OUTPUT_REGISTRY=16 (纯阶段内判据改动, 无阶段/列增删)。

## 6. 披露草案 (manuscript / codebook)

> Stage 13 (银行×金科同句共现预过滤) 的保留判据在**标题与正文的并集**上评估: 一篇 (文章, 目标银行) 行被保留, 当且仅当其**标题或正文中存在某一句同时包含目标银行别名与至少一个金融科技词**。纳入标题的依据: (i) 中文财经新闻的主题相关性高度集中于标题, 而 (ii) 正文常以指代 ("该行/其") 或承前省略主语行文, 使银行全名与金融科技词被分配到相邻而非同一正文句; (iii) 下游 LLM 全文精筛 (stage 21) 本就在"标题+正文"上判定相关性, 故 stage 13 忽略标题与之口径不一致。本调整使二者口径对齐。残余的保守召回损失 (标题与正文均未在单句内配对、且语义相关性仅由跨句指代承载者) 经由 §7 的标题×半径消融网格量化并如实报告; 其方向偏保守 (against-H1)。

## 7. 量化"到底回补了多少"(测度问题的可执行答案)

生产语料机上:
1. **keep-set diff**: 同语料分别跑 `match_in_title ∈ {false, true}`, 取存活行集差 = 被标题口径回补的行 → 报回补绝对数/占比、逐年分布、银行覆盖增量。
2. **回补行的真实性复核**: 把回补行喂给 stage 21 full 轨 judge, 报 `llm_verified_full` 通过率 → 若高 (≈ 与原存活集相当) ⇒ 这批确为真报道, 证明标题口径在补真阳性而非引噪声。
3. **2×4 稳健性网格**: `match_in_title ∈ {false,true}` × `radius ∈ {0,1,2,3}` (复用 [65_radius_sensitivity.py](../../65_radius_sensitivity.py)), 报主结论对该网格的稳定性。

## 8. 风险与回滚

- **风险 (低)**: 标题含多句 (中间有 。！？；) 时, 若银行名与金科词落在不同**标题**句, radius=0 不桥接 → 该极端 (罕见) 仍漏; 可接受 (同正文侧的同句铁律)。
- **风险 (极低假阳性)**: 标题反讽/否定式 (如"X银行否认布局区块链") → 银行侧已过 `negation_ac`/短名排除, 但语义否定非本判据职责; 交由 stage 21 全文精筛兜底 (它读全文能识别)。
- **回滚**: 设 `match_in_title: false` 即逐字节回到旧行为 (无需改码); 或 revert 单文件 diff。

## 9. 落地顺序 (建议)

1. 改 `cooccurrence_filter.py` + `config/filtering.yaml` + 加 4–5 个锁测试。
2. `pytest tests/test_13_cooccurrence_filter.py -q` + `ruff check pipeline/filtering/cooccurrence_filter.py` 绿。
3. 全量 sweep 对 baseline stash 取差, 证 **0 新增失败** (本机 T=2, 不动盘上 parquet)。
4. 提交 (by-name, 排除并发会话文件 / `data/processed/` / `eval_reports`)。
5. 披露段并入 codebook + CLAUDE.md "后续" 登记; golden 重生 + §7 量化 **DEFERRED 生产语料机**。

---
**计数**: 16/16/35/16 不变 · **golden**: DEFERRED · **付费**: 仅真·新进入候选集文章的 stage 21 首跑 (其余缓存命中 $0)
