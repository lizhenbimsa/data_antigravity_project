# 三轨文本架构权威参考 (full / ctx / ss)

> **本文性质**: 代码核验的架构参考 (非审计报告)。
> **核验方式**: 2026-06-18 六-agent 只读工作流并行精读 6 个子系统 (物化 / 共现原语 / 情感三轨 / 下游面板与 IV / 配置约束 / 12b-vs-ss 区分), 全部锚点经 Read 实读确认。
> **适用版本**: v3.9.0 (`_ss` 第三主轨) + v3.10.0 (stage 12b)。
> **历史订正**: 已不是旧版 full/ctx/**title** —— title 情感轨 v3.8.0 已删 (标题改 prepend 进三轨), `_ss` (银行+金科同句) 起作并列第三主轨。
> **关联**: `scripts/audit/THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md` (ss 轨执行计划) · `scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md` (编号阶段参考)。

---

## 0. 一句话总览

同一篇新闻、同一对 (文章, 目标银行), 在 **stage 13** 被切成三种"视角不同、长度递减"的文本; 下游每个情感方法对这三种文本各跑一遍, 产出机械加后缀 `_full` / `_ctx` / `_ss` 的平行列, **互为稳健性 (而非可加分解)**。

| 轨 | 文本列 | 文本 = | 锚定对象 | 后缀 | 角色 |
|---|---|---|---|---|---|
| **full** | `content_full` | 标题 + 整篇正文 | 无 (全文) | `_full` (5) | 全文基线 |
| **ctx** | `content_ctx` | 标题 + 含**目标银行**的句 ±1 句窗 | 银行实体 | `_ctx` (4) | 银行聚焦, P1 主轨 |
| **ss** | `content_ss` | 标题 + **银行∧金科同句**出现的句 ±1 句窗 | 银行+金科**同句** | `_ss` (3) | 同句共现, 第三主轨 |

后缀长度 `_full`(5) > `_ctx`(4) > `_ss`(3): ss 短于 ctx → 任何 ctx 能塞进 Stata 32 字符的列 ss 一定也能 → 无需新缩写规则。

---

## 1. 大白话版

一篇银行新闻常常很长, 既讲这家银行的罚款坏账, 也顺带提一句金融科技。若整篇喂给情感模型, 读到的"情绪"是全文大杂烩, 分不清是在评价**银行本身**还是**银行的金科业务**。三轨架构把同一篇裁成三个版本: ① 全文 (`full`); ② 只留"提到这家银行"的几句 (`ctx`); ③ 只留"银行和金科在**同一句**里"的几句 (`ss`)。再让词典 / BERT / LLM 三种打分器各打一遍。

`full` 测"银行整体口碑", `ctx` 把镜头拉到银行身上, `ss` 进一步逼近"媒体真的把银行和金科**放在一起谈**"的语义。三角度方向一致 ⇒ 结论稳健; 只有 `ss` 显著 ⇒ 信号确实来自"银行×金科"共现叙事。`ss` 独立成轨 (非 ctx 子集) 是因为实测**银行句仅约 34% 顺带提金科** (主题漂移率 65.76%)。

---

## 2. 唯一物化点: stage 13 `ctx_materializer`

三轨文本**只在一处生成** —— `pipeline/text/ctx_materializer.py` (stage 13, 注册产物 `13_news_with_ctx.parquet`, `core/schemas.py:55`)。纯 CPU (pandas + 正则分句 + Aho-Corasick), 不调任何 LLM / 嵌入 / BERT, 逐位可复现。

**输出 5 列** (`ctx_materializer.py:60-62`), 原始 `内容` / `标题` 列**原样保留不动**:

| 列 | 公式 | 锚点 |
|---|---|---|
| `content_full` | `prepend_title(标题, 全文 body)` | `:292` |
| `content_ctx` | `prepend_title(标题, extract_entity_context(...))` | `:262-271,293` |
| `content_ss` | `prepend_title(标题, extract_bank_fintech_cooccurrence(...))` | `:274-294` |
| `ctx_is_fallback` | bool, `(ctx_body == 全文 body)` | `:307-311` |
| `ss_is_fallback` | bool, `(ss_body == 全文 body)` | `:312-315` |

`prepend_title` (`core/text/entity_context.py:66-81`): 标题为空→原样返回 body; body 已以标题开头→不重复拼 (防双标题); 标题末已是句末标点 (`。！？!?；;…`)→直接相连, 否则插中文句号 `。` (`_TITLE_SEP`)。

**为何物化在 stage 13 (早于情感打分 stage 21)?** 让 stage 14 (fintech 强度) / stage 15 (政策对齐) 在 LLM 阶段**之前**即可消费 ctx/ss, 做到真三轨。把"切文本"从"打分"里解耦。

**幂等守卫** (`:168-219`): 五列俱全→短路跳过; 旧 schema (仅 `content_ctx`)→兼容回填, 以**哨兵** `content_ss=content_full` / `ss_is_fallback=True` 填充 (**不重算 ss**)。⚠ 要拿真 `_ss` 列须删 `content_ctx` 触发全量重算; 审计 ss 非空率时须区分"真共现回退"与"哨兵回填"。

---

## 3. 共现判定原语 (`core/text/entity_context.py`, 三函数禁互相复用)

| 函数 | 用途 | 命中口径 | radius | 返回 | 锚点 |
|---|---|---|---|---|---|
| `extract_entity_context` | **ctx 轨**物化 | 银行别名命中句 (仅锚银行) | 句窗扩输出 | 截窗文本 | `:144-221` |
| `extract_bank_fintech_cooccurrence` | **ss 轨**物化 | **银行∧金科严格同句** (radius=0 命中) | 命中后扩输出窗 | 截窗文本 | `:237-316` |
| `has_bank_fintech_cooccurrence_within_radius` | **stage 12b** 过滤判据 | **银行锚句 ±radius 邻句**含金科 (窗口邻近) | radius≥1 参与命中 | **bool** | `:371-436` |

**严格同句 vs 窗口邻近** (`:387-394`): `extract_*` (ss) 要求命中句**同一句内**既含银行又含金科 (`:296-304`); `*_within_radius` (12b) 允许银行句与金科句相隔最多 `radius` 句 (`:421-436`)。**严格同句是窗口邻近 radius=0 的子集**; radius≥1 时 12b keep 集 ⊇ 严格同句集。**禁互相复用**: 若 ss 复用 12b 窗口判据, ss 会被污染成"邻句共现"而非"同句共现", `frac_ss_fallback` 坍缩、丧失独立信号。

**不对称匹配口径 (有意设计, 非 bug)** (`:263-269,396-398`):
- **银行侧** `has_unexcluded_occurrence` (`core/text/ahocorasick.py:211-244`): 否定模式 (`NEGATION_AC`) + 短名歧义排除 (防"涉农行业"误锚"农行")。
- **金科侧** `_sent_has_fintech` (`:224-234`): 裸 Aho-Corasick 词典匹配 (1506 词), **不做任何否定/短名过滤**。
- 与审计脚本 `scripts/audit/measure_bank_fintech_cooccurrence.py` 同一事实源, 保证"审计 == 生产"逐字节一致。

**短文本 (<3 句)** 两原语都退化到 `_char_level_fallback` (`:319-368`): 银行出现位置 ±150 字符 (`fallback_char_radius`) 窗内须同含金科才开窗。⚠ 字符窗宽度与句窗不同, keep 率 gate 须分长/短文本两层披露。

---

## 4. 回退公理 (fallback axiom)

**ctx 无银行命中 / ss 无银行∧金科同句共现 → 退回全文 body, 旗标置 True。**

- `ctx_is_fallback=True` = 这篇没截到银行相关句 (entity-miss 信号)。
- `ss_is_fallback=True` = 无银行∧金科同句共现 (镜像 ctx 设计)。
- `FINTECH_AC=None` (金科词典加载失败) → `content_ss` **全部**退回全文 + `ss_is_fallback` 全 True (优雅降级, 不崩管道, `ctx_materializer.py:130-137`); 此时结果分析日志走守卫分支, **禁判读三轨稳健性**。

ss 回退是镜像 ctx → **与 ctx 共享 `n_articles` 分母, 不需独立计数列**。ss 回退率天然高于 ctx (大量银行新闻只讲罚款/坏账, 与金科无关)。

⚠ **判定细节**: `*_is_fallback` 比较"**去标题后的 body**" (`ctx_body`/`ss_body` vs 原始 `内容` 列 body, `:300-306`), 不是带标题的 `content_*`。标题前缀对三轨相同, 不影响 entity-miss 语义。

---

## 5. 各情感方法如何"三轨化"

三种打分器各自对 `content_full` / `content_ctx` / `content_ss` 跑一遍, 机械加后缀。**driver `['_full','_ctx','_ss']` 是散落在 30+ 文件的重复字面量, 无单一常量事实源** —— 改三轨须全仓同步。

### stage 21 LLM (付费, 核心, `pipeline/sentiment/tone_llms.py`)
- **单一事实源 = `iter_article_track_prompts`** (`:694`): 逐 (行 × 轨) yield `(row_idx, track, prompt)`; **生产 `run_all_llms` 与缓存覆盖审计 `verify_stage21_cache_coverage.py` 共用此生成器**, 保证缓存键字节级一致。
- **三轨同一循环、共用同一 `PROMPT_TEMPLATE`, `content` 是唯一变参** (`:737`)。**prompt v8 字节级冻结铁律**: 只交换 `content` 实参, 绝不改模板文本 —— 改一个字 → 缓存键全 miss → 13 万条旧答案作废、须重新付费。
- ctx/ss 喂 prompt 前用 `_strip_prepended_title` 剥标题 (`:727`, prompt v8 已有独立 `{title}` 字段)。
- 任务数 = `len(df) × len(models) × 3` (`:765-767`); main 对每篇调 `_aggregate_track` 三次 (full `:1905` / ctx `:1944` / ss `:1981`)。
- ⚠ **缓存键不含 track** (`core/caching.py:263`): 键 = `sha256(SCHEMA|model|prompt|prompt_version|temperature)`; track 仅靠 content 文本差异间接分区 → `_ss` 是**纯加性新增**, 不污染 full/ctx 既有命中。ss 缓存初始 0 条, 须线上付费首跑播种 ~3510 条。**勿删 `_llm_cache.db`**。

### stage 22 词典法 ($0, `pipeline/sentiment/tone_words.py`)
- `_dual_analyze` (`:1407`) 对三列各调 `_analyze_single_article`, 合并加后缀 (`:1424-1429`); `content_ss` 缺列→回退 `content_ctx`→再回退 `内容` (**优雅回退**, `_ss` 列仍写出)。
- ⚠ **IDF 权重三轨共享同一份 `content_full` 语料** (`:770`), 绝不按轨分语料 (与按轨独立的打分不同)。

### stage 23 BERT (`pipeline/sentiment/tone_berts.py`)
- 构建 `content_{full,ctx,ss}_list` 各调 `process_all_models` (`:1179-1196`), 写回带后缀。
- ⚠ ss 轨是**优雅跳过** (`:1156`): `content_ss` 缺列 → `output_ss=None` → 不写任何 `*_ss` 列。**与 stage 22 的"优雅回退"口径不同**。

---

## 6. 下游传播: 特征 / 面板 / IV / Stata

- **stage 14** (`fintech_intensity.py`): `fintech_intensity_score_{full,ctx,ss}`, 缺 ss 列回退 full。
- **stage 15** (`policy_alignment.py`): `policy_cosine_sim_{full,ctx,ss}`, ss 缺列→不产 `_ss` 列 (与 ctx 回退 full 不同)。
- **stage 45 panel encode**: ⚠ `llm_vote_tone_{full,ctx,ss}` **不是 stage 21 产出列**, 而在 encode 层把 `llm_sentiment_*` 经 `SENTIMENT_MAP` (正面=1/中性=0/负面=-1) → `llm_vote_score_*` → `groupby mean` 得到 (`encode.py:534-544`)。**P1 主变量 = `llm_vote_tone_ctx`**。

### ⚠ IV 列"对角命名例外" (chain-break 陷阱, `iv_extensions.py:566-583`)
大多数 IV 列机械 `_ctx→_ss`, 但**有几个轨内分子列不叫 `_ss`**:
- locus (P4) 创新 frac = **`tech_frac_ls`** (非 `_ss`)
- collab (P5) = **`collab_frac_cm_ss`**
- subst (P3) = **`sub_frac_ss`**

朴素把 `_ctx` 替换成 `_ss` 会撞不上这些非常规列名 → `lpeer_locus_iv_ss` / `collab_iv_ss` **静默全 NaN**, 毁 P4/P5。这是 v3.9.0 落地时 19-agent QA 才逮出的 bug (前几轮全漏), **必须硬编码这些例外**。

### Stata 写前守卫
`stata_export.py:615-653` `_assert_track_triplet_unique`: 断言 full/ctx/ss 三元组截断后不撞名。标签机械后缀: 中文 `(银行+金科同句)` / 英文 `(Bank+FinTech same-sentence)`。

### 计量铁律 (红线)
**`full × ctx × ss` 严禁混进同一 over-identified Hansen J** (`tone_llms.py:27-28`, `iv_extensions.py:516-523`)。三轨高度相关 (corr 可达 0.998), 混进 J 检验会零功效。正确做法: **三轨各自 just-identified、并排报告**。

---

## 7. ⚠ 易混点: stage 12b ≠ `_ss` 轨

全架构**最易混淆**的一对 —— 都基于"银行×金科共现", 但**用途完全相反**:

| | stage 12b 共现硬过滤 | `_ss` 同句轨 |
|---|---|---|
| 动作 | **丢行** (改行集/统计宇宙) | **列内扩展** (不丢行, 新增信号列) |
| 原语 | `has_bank_fintech_cooccurrence_within_radius` (窗口邻近 radius≥1) | `extract_bank_fintech_cooccurrence` (严格同句 radius=0) |
| 位置 | stage 12 与 stage 13 之间 (`dag.py:187-201`) | stage 13 内物化 `content_ss` |
| 配置 | `cooccurrence_filter.sentence_radius=1` / `min_keep_frac=0.001` | `context_window.ss_sentence_radius=1` |
| 产物 | `12b_cooccurrence_filtered.parquet` | `content_ss` + `ss_is_fallback` 列 |

- **12b 只保留**目标银行与 ≥1 金科词在 ±radius 句窗邻近共现的文章 (`cooccurrence_filter.py:102-159`), 降 stage 12 关键词判定的虚假相关 (Andreou et al. 2026)。
- **唯一 load-bearing 重指针** = stage 13 输入改读 `output_12b_cooccurrence` (`ctx_materializer.py:440-452`)。回滚只需把 `in_name` 改回 `output_12_fintech_news`。
- **SAFE-1 铁律** (`:107-112`): `FINTECH_AC=None` → 保留全部行 + loud WARNING (绝不静默清空整库); keep 率 < `min_keep_frac` 或 0 行 → `SystemExit(1)` (`:264-274`)。
- **路线 A 纯接受-披露**: 12b 仅丢行, 下游 `controls.py`/`encode.py` **零改动**。`fintech_share` 分母经"望远镜式坍缩"**恒不变** —— `all_n_articles = ft_dedup + nf ≡ |df_full|`, 12b 只把被丢中间集 C 从 ft 端移到 nf 端, 代数和守恒 (`controls.py:484-493,770-771`)。统计宇宙平移为"近邻相关金科"口径, 在 manuscript/codebook **如实披露** (非代码修复)。
- ⚠ **盲区例外**: 地理 attention 族 (`ft_attn_*`/`ft_vol_*`) 直读 `12_fintech_news_full`、**不经 12b**, 仍是原始关键词口径, 须单独披露。

---

## 8. 配置与实测覆盖率

`config/filtering.yaml`:
- `context_window` (`:86-89`): `sentence_radius=1` (ctx)、`fallback_char_radius=150`、`ss_sentence_radius=1` (代码默认回退到 `sentence_radius`, `ctx_materializer.py:225` —— 改 ctx 半径会连带改 ss)。
- `cooccurrence_filter` (`:103-105`): `sentence_radius=1`、`min_keep_frac=0.001`。

**实测覆盖率 (disk 1170 篇旧小样, `THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md:33-34`)**:
- 零共现 **14.27%** (回退全文, 少数) —— 这是**严格同句 radius=0 的上界**, 12b 窗口 radius≥1 实际丢行率更低。
- 主题漂移率 **65.76%** (银行句仅 34% 提金科 → ss ≠ ctx, **独立信号成立**)。
- ⚠ 来源是冻结的一次性度量脚本 `measure_bank_fintech_cooccurrence.py`; 全量 17M/T=18 须逐年重测 ss 非空率与 min-N。

---

## 9. 生产状态与待办 (诚实披露)

- **本机层已落地**: 三轨文本物化 + 三情感方法三轨循环 + 下游特征/面板/IV/Stata 三轨化 (v3.9.0 `_ss` + v3.10.0 stage 12b)。
- **生产层待办** (付费/受 gate): ① `_ss` LLM 缓存须线上付费首跑播种 ~3510 条; ② golden `schema_version` **当前仍是 2** (`generate_golden_snapshot.py:131` 硬编码, fixture 也是 2), 计划 2→3 (版本感知 loader, `schema_version==2` 时丢 `_ss` 列) 在 ss 列付费落盘后才升; ③ 3 个非确定网络中心度列及其 ss 派生仍排除字节级 repro。

---

## 10. 三概念区分 (防误删)

- **(α) 三轨** = `content_full` / `content_ctx` / `content_ss` 文本列 + 各情感方法的 `_full`/`_ctx`/`_ss` 后缀列。
- **(β) 标题显著性 / 分类门** = `in_title` / `target_bank_in_title` (`news_bank.py`) / `fintech_in_title` (`news_fintech.py`) / `headline_frac` (`controls.py`): 是显著性信号/分类门, **不是轨, 保留勿删** (v3.8.0 删 title 情感轨时刻意保留)。
- **(γ) 标题作输入** = 经 `prepend_title` 拼进三轨文本 (不单独成轨)。
