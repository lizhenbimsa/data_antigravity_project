# 三轨文本架构权威参考 (full / ctx / ss)

> **本文性质**: 代码核验的架构参考 (非审计报告)。
> **核验方式**: 2026-06-18 六-agent 只读工作流精读 6 个子系统 → 48-agent 顶刊标准对抗复核 (逐锚点二次核验 + 6 维度架构审计 + 完整性批判 + 对抗终审, 0 假阳性), 全部 file:line 锚点经实读确认。
> **适用版本**: v3.9.0 (`_ss` 第三主轨) + v3.10.0 (stage 12b)。盘面状态以 2026-06-18 实读为准。
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

`full` 测"银行整体口碑", `ctx` 把镜头拉到银行身上, `ss` 进一步逼近"媒体真的把银行和金科**放在一起谈**"的语义。三角度方向一致 ⇒ 结论稳健; 只有 `ss` 显著 ⇒ 信号确实来自"银行×金科"共现叙事。`ss` 独立成轨 (非 ctx 子集) 是因为实测**银行句仅约 34% 顺带提金科** (主题漂移率 65.76%)。⚠ 此 65.76% 来自 **disk 1170 篇小样、非生产规模、不可外推到全量 17M/T=18**; 全量跨 2007–2024 早年金科叙事稀薄, 漂移率会逐年剧烈变化, "独立信号成立"须俟生产 run 逐年复测后方可坐实 (见 §9 待测矩阵)。

---

## 2. 唯一物化点: stage 13 `ctx_materializer`

三轨文本**只在一处生成** —— `pipeline/text/ctx_materializer.py` (stage 13, 注册产物 `13_news_with_ctx.parquet`, `core/schemas.py:55`)。纯 CPU (pandas + 正则分句 + Aho-Corasick), 不调任何 LLM / 嵌入 / BERT, 逐位可复现。

**输出 5 列** (`ctx_materializer.py:60-62`), 原始 `内容` / `标题` 列**原样保留不动**:

| 列 | 公式 | 锚点 |
|---|---|---|
| `content_full` | `prepend_title(标题, 全文 body)` | `:294` |
| `content_ctx` | `prepend_title(标题, extract_entity_context(...))` | `:264-273,295` |
| `content_ss` | `prepend_title(标题, extract_bank_fintech_cooccurrence(...))` | `:276-296` |
| `ctx_is_fallback` | bool, `(ctx_body == 全文 body)` | `:311-315` |
| `ss_is_fallback` | bool, `(ss_body == 全文 body)` | `:316-319` |

`prepend_title` (`core/text/entity_context.py:66-81`): 标题为空→原样返回 body; body 已以标题开头→不重复拼 (防双标题); 标题末已是句末标点 (`。！？!?；;…`)→直接相连, 否则插中文句号 `。` (`_TITLE_SEP`)。

**为何物化在 stage 13 (早于情感打分 stage 21)?** 让 stage 14 (fintech 强度) / stage 15 (政策对齐) 在 LLM 阶段**之前**即可消费 ctx/ss, 做到真三轨。把"切文本"从"打分"里解耦。

**幂等守卫** (`:168-221`): 五列俱全→短路跳过; 旧 schema (仅 `content_ctx`)→兼容回填, 以**哨兵** `content_ss=content_full` / `ss_is_fallback=True` 填充 (**不重算 ss**)。⚠ 要拿真 `_ss` 列须删 `content_ctx` 触发全量重算; 审计 ss 非空率时须区分"真共现回退"与"哨兵回填" (各阶段缺列回退口径完整对照见 **§6.1 统一矩阵**)。

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

⚠ **判定细节**: `*_is_fallback` 比较"**去标题后的 body**" (`ctx_body`/`ss_body` vs 原始 `内容` 列 body, `:303-305`), 不是带标题的 `content_*`。标题前缀对三轨相同, 不影响 entity-miss 语义。

⚠ **`ss_is_fallback` 不仅是 entity-miss 信号**: 它还被 **stage 24** 用作三轨独立性诊断的门控掩码 —— full-ss / ctx-ss 两对的 Spearman ρ **仅在 `ss_is_fallback==False` 的行上算** (`herd_decay.py:633-636`), 防回退行 (`content_ss≡全文 body → herd_weight_ss≡herd_weight_full`) 虚抬 ss 相关性 (详见 §5 stage 24 子节)。

---

## 5. 各情感方法如何"三轨化"

三种打分器 (+ stage 24 跟风衰减) 各自对 `content_full` / `content_ctx` / `content_ss` 跑一遍, 机械加后缀。**driver `['_full','_ctx','_ss']` 是散落在约 17 个生产源 .py 的重复字面量** (精确三元列字面量 ~115 处; 放宽到"含全部三后缀字面量"的逐文件口径达 ~33 个 .py — 含 `encode.py` · `runner.py` · `iv_extensions.py` · `tone_words.py` · `attention_media.py` · `iv_did.py` · `llms_evaluation.py` 等), **无各 driver 共享导入的单一常量事实源** (仅 `stata_export.py:635` 有函数局部 `_TRACK_SUFFIXES`, 专供 Stata 写前撞名断言, 不被任何 driver 复用) —— 改三轨须全仓同步。
- **同步不靠人肉清单, 而由自动护栏兜底**: `scripts/audit/check_static_enums.py` 扫 `pipeline`/`validation`/`papers` 全树, 对每处 `['_full','_ctx']` 双轨静态枚举断言邻近存在 `_ss` 兄弟或显式豁免, 缺一即 pytest 红线 `test_no_unconverted_two_track_enums` FAIL (当前 0 漏)。⚠ 该护栏**只覆盖机械后缀类枚举**, 抓不到 §6 的"对角命名"列 (`tech_frac_ls` / `collab_frac_cm_ss` / `sub_frac_ss`) —— 那几个非后缀别名必须**人工硬编码 + 对照 §6 锚点**, 是真正的静默 NaN 高危点。(注: 护栏位于 `scripts/audit/` 而 `testpaths=["news_process/tests"]`, 默认 sweep 不收, 须显式给路径或加薄包装才进 CI。)

### stage 21 LLM (付费, 核心, `pipeline/sentiment/tone_llms.py`)
- **单一事实源 = `iter_article_track_prompts`** (`:694`): 逐 (行 × 轨) yield `(row_idx, track, prompt)`; **生产 `run_all_llms` 与缓存覆盖审计 `verify_stage21_cache_coverage.py` 共用此生成器**, 保证缓存键字节级一致。
- **三轨同一循环、共用同一 `PROMPT_TEMPLATE`, `content` 是唯一变参** (`:737`)。**prompt v8 字节级冻结铁律**: 只交换 `content` 实参, 绝不改模板文本 —— 改一个字 → 缓存键全 miss → 13 万条旧答案作废、须重新付费。
- ctx/ss 喂 prompt 前用 `_strip_prepended_title` 剥标题 (`:727,732`); prompt 的 `{title}` 字段三轨同填**原始 `标题` 列** (`:716,742`), 标题侧零差异 (详见下文"标题三处接触点")。
- 任务数 = `len(df) × len(models) × 3` (`:765-767`); main 对每篇调 `_aggregate_track` 三次 (full `:1905` / ctx `:1944` / ss `:1981`)。
- ⚠ **缓存键不含 track** (`core/caching.py:263-270`): 键 = `sha256(SCHEMA|len:model|len:prompt|len:pv|temp[|seed])`; track **不进键**, 仅靠 prompt(=唯一变参 content)文本差异间接分区。
  - ⚠ **回退碰撞 (诚实计数)**: prompt 三轨共用同模板, `title`/`target_bank`/`co_mentioned_banks` 三轨逐行相同。**ss 回退到 full 时** (`ss_is_fallback=True`, §4), `content_ss=prepend_title(title, body)` 经 `_strip_prepended_title` (`tone_llms.py:374-380`) 在主导情形下精确还原为裸 `内容` body, 与 full 轨 content (`:710`) **逐字节相同 → 缓存键碰撞 → 该 ss 任务命中既有 full 条目, 是命中复用而非真新增** (碰撞读回同 content 的同一正确答案, **无害、零边际付费**; 仅文档自承 0.6% "body 以 title 开头" 边角例因 strip 非精确逆而产独立键)。故 `_ss` 对 full/ctx 既有命中**无害**, 但**不是纯加性 ~3510 条新增**: ss 任务总数 ≈ 1170×3 ≈ 3510, 其中只有"ss 窗口 ≠ 全文"的部分才是真新增, 回退/平凡行落在既有 full 条目上。**实测**首跑只有 **~2478 真 miss** (`memory third-track-ss-impl-pushed-2026-06-15`, 即 ~1032/3510 ≈ 29% 命中既有 full 条目)。**勿删 `_llm_cache.db`**。

### stage 22 词典法 ($0, `pipeline/sentiment/tone_words.py`)
- `_dual_analyze` (`:1407`) 对三列各调 `_analyze_single_article`, 合并加后缀 (`:1424-1429`); `content_ss` 缺列→回退 `content_ctx`→再回退 `内容` (**优雅回退**, `_ss` 列仍写出)。
- ⚠ **IDF 权重三轨共享同一份 `content_full` 语料** (`:770`), 绝不按轨分语料 (与按轨独立的打分不同)。

### stage 23 BERT (`pipeline/sentiment/tone_berts.py`)
- 构建 `content_{full,ctx,ss}_list` 各调 `process_all_models` (`:1179-1196`), 写回带后缀。
- ⚠ ss 轨是**优雅跳过** (`:1156`): `content_ss` 缺列 → `output_ss=None` → 不写任何 `*_ss` 列。**与 stage 22 的"优雅回退"口径不同** (完整对照见 §6.1)。

### stage 24 跟风衰减 (`herd_decay.py`, v3.9.0 已三轨化)
- 三轨各对 `content_{full,ctx,ss}` 独立做 char_wb(2,4) TF-IDF + 余弦相似度 (`:549-564`), 窗内相似度达阈记为跟风前驱, 衰减权重 → 输出 `herd_weight_{full,ctx,ss}` + `n_similar_articles_{full,ctx,ss}` 六列 (`:507-512,573-574`)。与 ctx/ss 同动因 (measurement-treatment matching): 全文相似度 ≠ 银行邻域相似度 ≠ 同句共现相似度, 三轨各自判定不混用。
- 缺 `content_ss` → ss 轨回退 full (`ss_counts=full_counts`, `:563-564`, 镜像 ctx 缺列回退 `:556-557`); 缺 `content_full` → 回退裸 `内容`。单列 `herd_weight=herd_weight_full` 作 _full 轨 NON-BREAKING 别名 (`:608`)。
- ⚠ **ss_is_fallback 门控** (与 §4 回退公理直接耦合): 三轨独立性诊断 (Spearman ρ) 对 full-ss / ctx-ss 两对**仅在 `ss_is_fallback==False` 行上算** (`:633-636`, `valid = valid & _ss_real`, `_ss_real = ~df['ss_is_fallback']`); 缺 `ss_is_fallback` 列时宽松按全部行非回退 (`:623-626`, graceful)。

### ⚠ 标题在三轨中的三处接触点 (可比性前提, 已核实无双标题)
标题对 full/ctx/ss **完全对称**, 全程注入恰好一次:

| 接触点 | 位置 | 行为 |
|---|---|---|
| ① stage 13 prepend | `ctx_materializer.py:294-296` | `content_{full,ctx,ss}` 各 = `prepend_title(同一 title, body/ctx_body/ss_body)` |
| ② stage 21 strip + 独立 `{title}` | `tone_llms.py:716,727,732,742` | ctx/ss 喂 prompt 前 `_strip_prepended_title` 剥前缀; prompt 的 `{title}` 字段三轨同填原始 `标题` 列 (`:716` 单一赋值, `:742` 同循环内 `format(title=title,...)`) |
| ③ stage 22/23 再调 prepend | `tone_words.py:1415-1416` / `tone_berts.py:1159-1160` | 读已 prepend 的 `content_ss` 后再调 `prepend_title` — 守卫幂等 (`entity_context.py:77-78` `body.startswith(title)→return body` 短路, no-op) |

**结论**: ① ss 轨 prompt 的 `{title}` = 与 full/ctx 同一原始 `标题` 列, 三轨 `{title}` 字节一致 ⇒ 标题侧零差异, 三轨可比性仅由 `content` 差异承载。② ss 轨**无双标题**: stage 22/23 读的是 stage 13 已 prepend 的 `content_ss` (恒以 title 开头), 再调 `prepend_title` 被守卫短路, 二次拼接是 no-op。

---

## 6. 下游传播: 特征 / 面板 / IV / Stata

- **stage 14** (`fintech_intensity.py`): `fintech_intensity_score_{full,ctx,ss}`, 缺 ss 列回退 full (值 ≡ _full)。
- **stage 15** (`policy_alignment.py`): `policy_cosine_sim_{full,ctx,ss}`, ss 缺列→不产 `_ss` 列 (与 ctx 回退 full 不同)。
- **stage 45 panel encode**: ⚠ `llm_vote_tone_{full,ctx,ss}` **不是 stage 21 产出列**, 而在 encode 层两段生成: (a) **篇级编码** —— `SENTIMENT_MAP` 定义 (正面=1/中性=0/负面=-1, `encode.py:82`) 把 `llm_sentiment_*` 映射成 `llm_vote_score_*` (`encode.py:138-142`); (b) **组级聚合** —— `build_aggregation_dict` 声明 `llm_vote_tone{track}=(llm_vote_score{track},'mean')` (`encode.py:544`), 真正的 `groupby(['target_bank','year']).agg` 落地在 `encode.py:1153`。**P1 主变量 = `llm_vote_tone_ctx`**。

### ⚠ IV 列"对角命名例外" (chain-break 陷阱, `iv_extensions.py:550-583`)
大多数 IV 列机械 `_ctx→_ss`, 但 P3/P4/P5 三论文的轨内分子 frac 列名**其 ctx 名本身就不以 `_ctx` 结尾** (用"判别字母+轨字母"中缀 `_sc`/`_lc`/`_cm` 编码, 不含字面 `_ctx` 子串), 故字符串级 `_ctx→_ss` 替换对三者**全部失效** (是 no-op, 而非命名个例):

| 论文 | full 轨 frac | ctx 轨 frac (不含 `_ctx`!) | ss 轨 frac | 锚点 |
|---|---|---|---|---|
| subst (P3) | `sub_frac` | `sub_frac_sc` | `sub_frac_ss` (后缀仍标准 `_ss`, 不规则在中缀 `_sc`) | `iv_extensions.py:550-556` (sub 读 `:555`) |
| locus (P4) | `tech_frac` | `tech_frac_lc` | `tech_frac_ls` (**唯一连后缀都不规则**, 以 `_ls` 收尾) | `iv_extensions.py:566-573` (`:572`) |
| collab (P5) | `collab_frac` | `collab_frac_cm` | `collab_frac_cm_ss` (后缀标准 `_ss`, 不规则在中缀 `_cm`) | `iv_extensions.py:576-583` (`:582`) |

> 订正: `sub_frac_ss` / `collab_frac_cm_ss` **确实以 `_ss` 结尾**; 唯一连后缀都不规则的是 `tech_frac_ls`。chain-break 真因 = **ctx 名无字面 `_ctx` 子串** (`_sc`/`_lc`/`_cm`) → 从 ctx 名朴素 `_ctx→_ss` 替换三者皆 no-op → `lpeer_subst_iv_ss` / `lpeer_locus_iv_ss` / `lpeer_collab_iv_ss` 若不显式喂真名会**静默全 NaN**, 毁 P3/P4/P5。`iv_extensions.py:555/572/582` 已**显式硬编码全部三个真名**。这是 v3.9.0 落地时 19-agent QA 才逮出的 bug (前几轮全漏), **必须硬编码这些例外**。

### Stata 写前守卫与标签后缀
- **写前守卫** `stata_export.py:622-662` `_assert_track_triplet_unique`: Stata 写前唯一性断言, 仅断言 full/ctx/ss 三元组 sanitize 截断后不撞名 (撞名 `raise ValueError`), **不发标签**。
- **ss 轨标签后缀** (机械 `_ctx→_ss` 镜像):
  - 中文 `(银行+金科同句)` —— 产于 `stata_export.py:335-375` 的 `HEURISTIC_LABELS` 字典。
  - 英文全后缀 `(Bank+FinTech same-sentence)` —— **不在 `stata_export.py`** (该文件英文用压缩形 `SS-track`/`same-sent`); 整串出现于 `controls.py:1001,1004` (`STATA_LABELS_41`)、`validation/entity_masking.py:560` 等。

### 计量铁律 (红线)
**`full × ctx × ss` 严禁混进同一 over-identified Hansen J** (`tone_llms.py:27-28`, `iv_extensions.py:516-523`)。三轨高度相关 (corr 可达 0.998), 混进 J 检验会零功效。正确做法: **三轨各自 just-identified、并排报告**。

### ⚠ 6.1 三轨缺列/回退口径统一矩阵 (auditing ss 非空率必读)
`content_ss` (或下游 `_ss` 源列) 缺失时, 各阶段回退语义**互不相同**, 共 6 种"空"。审计 ss 非空率 / min-N 前必须先按本表区分, 否则统计宇宙判错 (例: stage14 的 `_ss` 看似有值实为 full 拷贝; stage15 根本无此列; IV 是显式 NaN)。

| 阶段 | `content_ss` / `_ss` 源缺时行为 | `_ss` 列是否产出 | 空值语义 | 对 ss 非空率统计的影响 | 锚点 |
|---|---|---|---|---|---|
| stage 13 (旧 schema) | 哨兵 `content_ss=content_full`, `ss_is_fallback=True` | 文本列产出 (=full) | **哨兵回填** | 全部记 fallback, 非真共现回退 | `ctx_materializer.py:168-221` |
| stage 13 (无共现, 新 schema) | 退回全文 body, `ss_is_fallback=True` | 文本列产出 (=full body) | **真回退 full** | 计入 fallback 率 (镜像 ctx) | `ctx_materializer.py:276-319` |
| stage 14 fintech_intensity | `score_ss = scores_full` | **产出 (值 ≡ _full)** | **回退 full (非空拷贝)** | `_ss` 非 NaN 但 ≡ `_full` → 误判"有信号" | `fintech_intensity.py:669-674` |
| stage 15 policy_alignment | `ss_texts=None` → 跳过 | **不产出 (退回 5 列)** | **None / 不产列** | 列直接缺失, 须按列存在性判定 | `policy_alignment.py:790-797,910-913` |
| stage 22 词典法 | 回退 `content_ctx`→`内容` | **产出** | **优雅回退 (非空, ≡ctx/内容)** | `_ss` 非 NaN 但 ≡ ctx/full → 误判"有信号" | `tone_words.py:1415-1416` |
| stage 23 BERT | `output_ss=None` | **不产出** | **优雅跳过 / 不产列** | 列直接缺失, 须按列存在性判定 | `tone_berts.py:1156,1186,1194-1196` |
| IV (iv_extensions) | `_ss` 源缺 → 列置 NaN | **产出 (全 NaN)** | **置 NaN** | `_ss` 列存在但全 NaN | `iv_extensions.py:240-255,373-414` |

**审计判定规则**: 见到一个"空 `_ss`", 先查本表确定它是 ①哨兵回填 / ②真回退 full / ③回退 full(非空拷贝) / ④优雅回退(非空, ≡ctx/内容) / ⑤None 不产列 / ⑥置 NaN, 再决定是否计入 ss 非空率分子。⚠ ③④ (stage14/22) 的陷阱: `_ss` 列**非 NaN 也非缺失**, 但值是 full/ctx 的逐元素拷贝 → 不能只看 `notna()`, 须用"独立于 full"判定 (`_ss != _full` 逐元素比对) 才能识别真共现信号。这是 §2 "区分真共现回退与哨兵回填"的全阶段放大版。

---

## 7. 三轨在 validation 阶段的延伸 (stage 36 / stage 39)

三轨不止生产情感阶段, 两个 validation-only 稳健性阶段也对 full/ctx/ss **各跑一遍**, 用以证明"生产-验证口径一致"。两者都读 `21_tone_llms_full.parquet` 的三轨列, 都是**增量付费 LLM 请求** (掩码/变体 prompt 与生产不同 → 冷缓存须线上跑)。

### stage 36 entity_masking (`validation/entity_masking.py`, 实体掩码稳健性)
- 三轨各做掩码替换 (银行别名→匿名占位符) + LLM 重判: `mask_entity` × 三轨 → `masked_text_{full,ctx,ss}` (`:315-317`), main 主循环逐轨跑 `mask_entity`+`verify_masking_completeness` (full/ctx `:781-818`, ss 段 `:822-843`)。
- `content_ss` 缺列 → 回退全文 body (`:754-757`, 镜像 `ss_is_fallback` 回退公理); 算四维一致性指标 (验证一致率/情感一致率/Cohen's κ/逐模型) × 三轨, gate = full/ctx/ss AND。

### stage 39 prompt_sensitivity (`validation/prompt_sensitivity.py`, prompt 措辞敏感度)
- 4 变体 × 3 模型 × **三轨** (`run_variant_llms:596-654`), 输出 `{variant}_*_{full,ctx,ss}` (`:683-690`); gate = full/ctx/ss 三轨各自全 criteria AND。
- **复用生产同源聚合**: `aggregate_variant_results` 用 `_aggregate_track`, locus 直接 import 生产 `tone_llms._resolve_locus_track` 保证规则同源 (`:687,693`)。
- ctx/ss 变体 prompt 构造前 `_strip_prepended_title` 剥标题 (`:625-632`), 镜像生产 `iter_article_track_prompts`。

**口径一致性**: 验证层与生产层共用 `_aggregate_track`/`_resolve_locus_track` 同一聚合规则 + 同步 `_strip_prepended_title` 剥标题, 保证"生产怎么判、验证就怎么判"。

---

## 8. ⚠ 易混点: stage 12b ≠ `_ss` 轨

全架构**最易混淆**的一对 —— 都基于"银行×金科共现", 但**用途完全相反**:

| | stage 12b 共现硬过滤 | `_ss` 同句轨 |
|---|---|---|
| 动作 | **丢行** (改行集/统计宇宙) | **列内扩展** (不丢行, 新增信号列) |
| 原语 | `has_bank_fintech_cooccurrence_within_radius` (窗口邻近 radius≥1) | `extract_bank_fintech_cooccurrence` (严格同句 radius=0) |
| 位置 | stage 12 与 stage 13 之间 (`dag.py:187-201`) | stage 13 内物化 `content_ss` |
| 配置 | `cooccurrence_filter.sentence_radius=1` / `min_keep_frac=0.001` | `context_window.ss_sentence_radius=1` |
| 产物 | `12b_cooccurrence_filtered.parquet` | `content_ss` + `ss_is_fallback` 列 |

- **12b 只保留**目标银行与 ≥1 金科词在 ±radius 句窗邻近共现的文章 (`cooccurrence_filter.py:102-159`), 降 stage 12 关键词判定的虚假相关 (Andreou et al. 2026)。
- **唯一 load-bearing 重指针** = stage 13 输入改读 `output_12b_cooccurrence` (`ctx_materializer.py:444-456`)。回滚只需把 `in_name` 改回 `output_12_fintech_news`。
- **SAFE-1 铁律** (`:107-112`): `FINTECH_AC=None` → 保留全部行 + loud WARNING; keep 率 < `min_keep_frac` 或 0 行 → `SystemExit(1)` (`:264-274`)。
- **路线 A 纯接受-披露**: 12b 仅丢行, 下游 `controls.py`/`encode.py` **零改动**。`fintech_share` 分母经"望远镜式坍缩"**恒不变** —— `all_n_articles = ft_dedup + nf ≡ |df_full|`, 12b 只把被丢中间集 C 从 ft 端移到 nf 端, 代数和守恒 (`controls.py:484-493,770-771`)。统计宇宙平移为"近邻相关金科"口径, 在 manuscript/codebook **如实披露** (非代码修复)。
- ⚠ **盲区例外① (地理 attention 族)**: `ft_attn_*`/`ft_vol_*` 直读 `12_fintech_news_full`、**不经 12b**, 仍是原始关键词口径 (分子分母同处 pre-12b, 比值口径内部一致), 须单独披露。
- ⚠ **盲区例外② (firm-level attention 族, 分裂宇宙)**: `attention_pct_*` / `attention_intensity_density_{full,ctx,ss}` 的**分子**取自 `14_fintech_intensity` (经 stage 13 已是 12b 子集) 并在 `attention_media.py:398` 再 `restrict_to_verified` 收缩到 verified 集 → 分子口径 = 『12b 近邻 ∩ verified』; 而**分母** `_n_all` 直读 `12_fintech_news_full` = pre-12b 全量银行新闻 (`attention_media.py:388-390,452-458`)。两端非同一统计宇宙 → 比值被系统性压低, 须在 codebook/manuscript 显式披露该分子分母异宇宙口径。

---

## 9. 配置与覆盖率

`config/filtering.yaml`:
- `context_window` (`:86-89`): `sentence_radius=1` (ctx)、`fallback_char_radius=150`、`ss_sentence_radius=1` (代码默认回退到 `sentence_radius`, `ctx_materializer.py:227` —— 改 ctx 半径会连带改 ss)。
- `cooccurrence_filter` (`:103-105`): `sentence_radius=1`、`min_keep_frac=0.001`。

**实测覆盖率 (disk 1170 篇旧小样, `THIRD_TRACK_SAME_SENTENCE_PLAN_2026-06-14.md:33-34`)**:
- 零共现 **14.27%** (回退全文) —— 这是**严格同句 radius=0 的上界**, 12b 窗口 radius≥1 实际丢行率更低。
- 主题漂移率 **65.76%** (银行句仅 34% 提金科 → ss ≠ ctx, 在小样下**独立信号成立**)。
- ⚠ **两数字均来自 disk 1170 篇旧小样、非生产规模、不可外推到全量 17M/T=18** (冻结脚本 `measure_bank_fintech_cooccurrence.py`)。全量跨 2007–2024 (T=18), 金科命中率/漂移率随年份剧烈漂移 (早年几乎无金科叙事), 若某些年份退化为 ss≈ctx, 第三轨正当性被削弱 → 须按下表逐年生产复测。

**生产规模待测矩阵 (生产 run 必填)**:

| 指标 | disk 1170 小样 | 全量 17M / T=18 (待测) |
|---|---|---|
| ss 非空率 (1−回退率) | 85.73% | 逐年填 (2007…2024) |
| 主题漂移率 (ss≠ctx) | 65.76% | 逐年填 |
| 每文均句数 / min-N | 2.75 句 / 直方图 0:167 | 逐年 min-N 守卫 |
| ss-LLM 真新增缓存条数 | ~2478 (3510 任务 −1032 碰撞命中) | 全量篇数×3 模型×回退率估算 |

---

## 10. 生产状态 (2026-06-18 实读盘面)

⚠ **重要订正**: ss 轨**已落地, 非"待付费首跑"** (此前文档此处方向写反, 经实读盘面纠正):

- **本机已落地 (含 ss LLM)**: `_ss` LLM 轨已线上付费首跑并落盘 —— disk `40_panel_yearly.parquet` (2026-06-18 重生) = 172 行 × 2661 列, 含 **760 个 `_ss` 列**, `llm_vote_tone_ss` 真实填充 (109/172 非空, mean≈0.955, 与 `llm_vote_tone_ctx` 数值不同); `13_news_with_ctx.parquet` 的 `ss_is_fallback` True 率 ≈14.4% (非 100% 哨兵), `content_ss != 内容` 在 1124/1125 行 (走真共现重算); `_llm_cache.db` ≈504 MiB (528 MB 十进制) / 154,793 条 (含 ss)。golden fixture `golden_panel_v0.json` 亦已对该含-ss 面板**重生过** (`40_panel_yearly` 记录 760 个 `_ss` 列 / 2661 列 / 172 行与盘面逐一一致; commit `98efb2ec`)。
- **唯一真残留 (golden 版本戳)**: golden `schema_version` 字段**仍是 2** —— `generate_golden_snapshot.py:131` 硬编码 `"schema_version": 2` 未随数据重生 bump 到 3 (**数据已 bless, 仅版本戳过时**); 计划升 2→3 + 版本感知 loader (`schema_version==2` 时丢 `_ss` 列向后兼容)。另: 3 个非确定网络中心度列及其 ss 派生仍排除字节级 repro。
- **12b keep 率硬 gate 尚未实现**: 当前 `cooccurrence_filter.py:256` 的 `keep_frac=n_out/n_in` 以 stage 12 自身输出 (已是 ≥3 关键词金科子集) 作分母, 12b 又只取其近邻共现子集, 结构上必然偏高 ("自证假~100%"); `min_keep_frac=0.001` 只能防近乎清空, **防不住静默大规模过删**。生产首跑须按 CLAUDE.md:21 实现真 gate: 读 **pre-12b** 真候选集做下界校验 + 按逐年/长短文本/银行分层报 keep 率; 银行整家掉出 (当前 117→113) 应升级为硬上界守卫。
- **生产规模覆盖率矩阵未填** (见 §9 待测矩阵): 14.27%/65.76% 均为 disk 1170 小样推算, 全量逐年须在生产 run 落盘后回填; 在此之前"独立信号成立"仅为小样结论。

---

## 11. 三概念区分 (防误删)

- **(α) 三轨** = `content_full` / `content_ctx` / `content_ss` 文本列 + 各情感方法的 `_full`/`_ctx`/`_ss` 后缀列。
- **(β) 标题显著性 / 分类门** = `in_title` / `target_bank_in_title` (`news_bank.py`) / `fintech_in_title` (`news_fintech.py`) / `headline_frac` (**裸 panel 列, 生产者 `encode.py:685` = mean(`in_title`)**; `controls.py:658-665` 内是其 NF 对照组孪生 `nf_headline_frac` = mean(`target_bank_in_title`)): 是显著性信号/分类门, **不是轨, 保留勿删** (v3.8.0 删 title 情感轨时刻意保留)。
- **(γ) 标题作输入** = 经 `prepend_title` 拼进三轨文本 (不单独成轨)。
