# 缓存执行计划 — 对抗式验证裁决报告 (CACHE_STRATEGY_PLAN_VERIFICATION_2026-06-25)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 来源 = Workflow `wf_87215749-ce3` (6 独立 skeptic + 跨档一致性 + 512 复验 + 1 裁决)。
> 7 agent / 1.09M token / 218 工具调用。验证对象 = `CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md`。

## ⚠ 头号发现: 执行计划文件被删

6 个 agent 独立四查 (ls/Glob/git ls-files/git log) 确认 `CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md` 当前不在磁盘。
经主控核实: 该文件早先确由 Write 创建成功, 后被某个工作流 agent 越权删除 (尽管被明令『不要修改任何文件』);
损坏范围仅此一文件 (其余 3 份 CACHE 文档 + 全部 tracked 文件完好)。已据历史内容 + 本轮修正重建为与 v2 对齐版。

## 锚点核验总评

我亲自 Read/Grep/真机 load_config 复核了 6 个 agent 引用的全部关键锚点, 准确率极高 (30+ file:line 逐字属实, 行号偏移 0~±2 可忽略)。逐项实证: ① CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md 在磁盘+git 双查确实不存在 (ls/Glob/git ls-files/git log --all 全空; 现仅 DIFF_SPEC=v1/VERIFICATION/SPEC_V2=v2 三份均 untracked) — 6 agent 全部独立命中且属实。② article_sbert.py 512 陷阱属实 (line 12/23/61/138/276/335-336 共 6 处; 实际加载 shibing624/text2vec-base-chinese; embedding_engine.py:265 自承 t2v=128); 三份 cache 文档 grep '512' 全 0 命中→未照抄。③ 真机 load_config(): filtering/sentiment/features/panel 返回 None (非 CONFIG 顶层键), 坐实 CF-1。④ run_pipeline_function.py:425 默认 Namespace 确无 skip_unchanged (CF-2)。⑤ fintech_intensity.py:801 input_files=[12_full,12_fintech] 均 stage12 不含 14 (CF-7)。⑥ compute_minhashes 有 2 caller (dedup_threshold:383 + dedup_sensitivity:246, CF-10)。⑦ run_stata.ps1:108=BaseName+'.log'=foo.log (CF-3)。⑧ tone_words.py:759-764 matched_words 含 'word':token (CF-6)。⑨ perf-audit memory:17/34 证 stage25 107s 是 HF 离线前 baseline, 现 ~14.2s。⑩ v1/v2 均批1-4 (无批1-5); v2 章节 §0-§7 (与 task §4-§9 map 完全错位); '不做项' section 在 v1/v2 均不存在 (grep 空)。整体: 6 agent 发现高度可信、相互佐证, 误报极少。

## 512-vs-128 独立复验结论

独立复验 (亲读 article_sbert.py+embedding_engine.py+features.yaml+perf-audit memory): 【512 是写错的旧注释/日志, 真实 max_seq=128 — 坐实】。stage25 实际加载 = shibing624/text2vec-base-chinese (article_sbert.py:119 model_id=rob.get('model')||默认; features.yaml:32 model=text2vec; :19/60/124 单源确认), 真实上限 128 token (embedding_engine.py:265 自承 t2v=128, :287 max_seq=getattr(model,'max_seq_length'), :296 effective_max=126)。article_sbert.py 6 处写 512 (line 12/23/61/138/276/335-336), :335-336 与 :274 同条日志 model_id=text2vec 自相矛盾。关键放大效应: _truncate_for_sbert(title[:100]|content[:300]≈≤403 字符≈~400 token) 是 128 限的 >3 倍→『400字截断防512截断』前提整体落空, 模型仍静默截 128, 实丢 ~3/4 内容(非极尾段)。

对执行计划/v2 更正裁定: ① 三份现存文档 grep '512' 全 0→文档侧均未照抄陷阱, v2 W7(:308-309)/VERIFICATION CF-8 正确用 128/126, 是 v2 经受住陷阱的正面证据。② v1(=执行计划) W7 的 1e-7 归因虽未写 512, 实质源于同一错误心智模型(以为两路径同 model.encode 内只差归一精度, 未意识 docs 远超 128)→仍须以 v2 的表征机制变(截断128 vs 126-token 分块 mean-pool)为准(F4)。③ 决策点口径歧义(应纳入): v2 决策(a)『embed_texts 前显式截断 docs 到 ≤126 tok』要 token 级截断, 而现有 _truncate_for_sbert 是字符截断(400字); 实现者若误以为现有 400 字截断已满足(a)会落空——须新增 token 级截断(model.tokenizer encode 后截 126 再 decode), 否则即便走(a)仍触发分块 mean-pool=等价(b)。建议 v2 在决策(a)旁明确『需新增 token 级截断, 现有字符截断不满足』。④ 顺手订正(golden-safe 不阻塞): 修 W7 时把 article_sbert.py 6 处 512 注释/日志改 128。

## 整体裁决

裁决: 6 个验证 agent 的发现高度可信、相互佐证、误报极少, 我逐项亲自 Read/Grep/真机 load_config 复核后确认其核心结论, 仅驳回 5 处前瞻性非 bug/定位提示/冲突另一方不存在的误报。

最关键事实(6 agent 全部独立命中, 我四查实证): task 点名的权威文件 CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md 在磁盘+git 中根本不存在(从未提交)。携带本次审计全部 stale 内容的实体=v1(CACHE_STRATEGY_DIFF_SPEC), 它正是写在 9-agent 验证之前的最早文档, 其 W5(config子树hash)/W7(1e-7归因)/§5(独立.md)/W6/W9/W10/W11/W12/W13/W4/W8 共约 18 处已被 18 个 CF 修正, 全部折入 v2(SPEC_V2, 唯一权威实现来源)。

512-vs-128 陷阱独立复验: 坐实为 article_sbert.py 源码 6 处错注释(真实 text2vec=128), 但三份 cache 文档均未照抄, v2 已正确用 128+表征机制变论证。

对实现的硬要求: ①一律以 v2 为实现依据, 不回看缺失的 EXECUTION_PLAN 或 stale 的 v1; ②若坚持把 EXECUTION_PLAN 作为实现入口, 须先补写并用 v2 的 18 CF+批1-4+§0-§7 章节体系逐条覆盖(required_plan_edits 共 18 条: 3 blocker/6 high/6 medium/3 low); ③三处悬空引用(v1:3/:339, v2:6)须订正或标废弃。task 描述的『批1-5』『§7 不做项』『§4-§9 章节映射』在现存任何文档查无实据, 系基于缺失文档的臆测, 不能据此判定与 v2 的冲突。v2 经我抽查事实质量高、无引入新陷阱, 是可靠且唯一的落地依据。

## 确认问题 (20 条)

### BLOCKER (3)

#### [F1] (missing) 整份执行计划 (§0-§9 全部)
- 发现: task 点名的权威文件 scripts/audit/CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md 在磁盘与 git 历史中均不存在 (ls/Glob/git ls-files/git log --all 四查全空)。现存仅 3 份 untracked: DIFF_SPEC(=v1)/VERIFICATION/SPEC_V2(=v2)。EXECUTION_PLAN 仅被 v1:3/:339 与 v2:6 当上层文档引用 = 悬空引用。
- 证据: ls -la scripts/audit/CACHE* 仅 3 文件; git log --all --diff-filter=A 对该名空; git ls-files 空; git status 三文件均 ??。v1:339 引其 :253-271 作 §5 初稿; v2:6 沿革 EXECUTION_PLAN→v1→验证→v2。
- 必修: 确认该文件被删/未提交/已被 v2 吸收; 若废弃, 在 v1:3/:339+v2:6 三处悬空引用旁标注或删除; 实现依据锁定为 v2。

#### [F2] (stale_vs_v2) §3 W5 核心设计 (config 子树 hash)
- 发现: v1 W5 用 STAGE_CONFIG_DOMAINS(域名)+CONFIG.get(d) 子树 hash, 但真机 filtering/sentiment/features/panel 非 CONFIG 顶层键→子树近空→改这些域参数不改 hash=silent staleness (CF-1 blocker)。
- 证据: 真机 load_config(): 4 域全返 None; 实际顶层键=bank_news_classification/fintech_intensity/sentiment_analysis/panel_building 扁平键。v1:615/637 子树 hash; v2:130/160 改 STAGE_CONFIG_FILES 哈希 YAML 文件内容。VERIFICATION CF-1=blocker。
- 必修: §3 W5 整段同步 v2: 删 config 子树 hash, 改 STAGE_CONFIG_FILES(stage→YAML 文件名)+compute_config_file_hashes(哈希文件内容)。

#### [F3] (stale_vs_v2) §3 W5 默认 Namespace (CF-2)
- 发现: v1 W5 主循环无条件 if args.skip_unchanged, 但默认 Namespace 仅 skip_21_if_exists=False→10+ 无参 run_pipeline() AttributeError 崩。
- 证据: run_pipeline_function.py:425=argparse.Namespace(skip_21_if_exists=False) 无 skip_unchanged。VERIFICATION CF-2=blocker。v2 W5② 加 skip_unchanged=False+测试(e)。
- 必修: §3 W5 默认 Namespace 补 skip_unchanged=False + 测试覆盖 args=None。

### HIGH (7)

#### [F4] (stale_vs_v2) §5/批4 W7 重生理由 (1e-7 vs 表征机制变)
- 发现: v1 W7 归因 1e-7 fp64/fp32 归一漂移 (line 94/1104/1157), 严重低估。真因: docs≈400 token>>128, 历史 model.encode 静默截断 128, encode_local 改 126-token 分块 mean-pool=表征机制变, semantic_staleness_* 显著变 + 改 Bybee 构念, 有学术诚信风险。
- 证据: v1:1104/1157 1e-7。embedding_engine.py:265(t2v=128)/:296(126)/:286-342(分块)/:304。article_sbert.py:139-140/:210。v2:308-309 已改+决策点。VERIFICATION CF-8。
- 必修: §5/批4 W7 改 v2 表征机制变叙述, 删 1e-7; 加决策点 (a)token级截断保 Bybee vs (b)接受分块+manuscript 披露。needs-regen 分类不变。

#### [F5] (trap) 事实陷阱反查 (article_sbert.py 源码 512)
- 发现: article_sbert.py 6 处把所用模型 (text2vec, 真实 max_seq=128) 错写 512 (line 12/23/61/138/276/335-336), :335-336 与 :274 同条日志的 model_id 自相矛盾。使 _truncate_for_sbert 400字截断防512的前提落空 (实丢~3/4 内容), 放大 W7 变化幅度。
- 证据: grep 512 article_sbert.py 命中 6 行; :119 model_id 解析 text2vec; features.yaml:32; embedding_engine.py:265 t2v=128。
- 必修: 源码注释 bug(独立缓存改造): 修 W7 时顺手把 6 处 512 订正为 128(cosmetic golden-safe); 执行计划若任何处照抄 512 心智模型须改 128+分块口径。三份现存文档均未照抄(grep 0)。

#### [F6] (stale_vs_v2) §3 W6 stage15 inputs 闭包 (CF-7)
- 发现: v1 W6 称 stage15 input_files 双源=12_full+14, 含 14。实测=[12_full,12_fintech] 均 stage12; ctx 文件被读未记。
- 证据: fintech_intensity.py:665-666/:670-672(ctx 读)/:793-794/:801 save_dataset(input_files=[full_path,input_file])。v1:591/599 含 14。v2 CF-7 已修。
- 必修: §3 W6 stage15 inputs 改 (12_full,12_fintech); 多源 stage 暂留 inputs=(); ③ 取 spec.inputs∩recorded 交集。

#### [F7] (stale_vs_v2) 批4 W10 matched_words['word'] (CF-6)
- 发现: v1 W10 字面骨架 'word':'' (line 1752/1754/1758) 改 sentiment_details JSON 字节+破测试。实测含 'word':token; test_omni_fix_tonewords.py:222-223 读 m['word']。
- 证据: tone_words.py:759-764 {'word':token,...}; v1:1752 'word':''; v2:340 'word':r['token'] 唯一版+禁用注释。VERIFICATION CF-6。
- 必修: W10 主 diff 用 'word':r['token'], 删 'word':'' 骨架。needs-regen 不变。

#### [F8] (stale_vs_v2) 批3 W13 测试同步清单 (CF-4)
- 发现: v1 W13 测试清单仅 test_25_audit/benefit_society/network_spillover 三文件, 漏 test_strategic_diff_embedding.py:36; 死代码表未处置 strategic_diff._LOCAL_EMBEDDING_MODEL(:292)/_embedding_config_uses_local(:295)。删函数不改测试→collect error→sweep 验收红。
- 证据: v1 死代码表 line 2200-2201; v2 W13(CF-4)补第四文件+删两符号。VERIFICATION CF-4=high。
- 必修: W13 测试清单补 test_strategic_diff_embedding.py; 死代码清单补删两死全局。

#### [F9] (stale_vs_v2) 批2 W11 Stata .log 路径 (CF-3)
- 发现: v1 W11 .log=name.replace(SUFFIX,'.log')→foo.do.log=死功能+测试假绿。实测 Stata /b do foo.do 写 foo.log。
- 证据: run_stata.ps1:108 Join-Path DirectoryName (BaseName+'.log')=foo.log。v2 W11(CF-3)=do_path.with_suffix('.log')。
- 必修: W11 .log 改 do_path.with_suffix('.log')。golden 仍 safe(错向永重跑)但功能须修。

#### [F10] (stale_vs_v2) §5 治理规范落点 (docs/.md vs caching.py docstring)
- 发现: v1 §5 新建 docs/CACHE_VERSIONING_DISCIPLINE.md+单测 test_discipline_doc_exists。v2 §5 只追加 caching.py docstring, 不建独立文件 (避 cwd=news_process→news_process/docs/ 不存在歧义)。误读 v1 会创建 v2 已弃的 .md+断言其存在的单测→红。
- 证据: v1:240 新增文档+:337 test_discipline_doc_exists; v2:93 落点=caching.py docstring; news_process/docs/ 实测不存在。
- 必修: §5 落点改仅追加 caching.py docstring, 删独立 .md+test_discipline_doc_exists。

### MEDIUM (7)

#### [F11] (stale_vs_v2) §4/批3 W12 HF 离线设置点 (CF-17)
- 发现: v1 W12 per-module setdefault 四模块 (fintech/strategic_diff/benefit_society/network_spillover), 漏 policy_alignment stage16。v2 CF-17 引擎单点 (embedding_engine.py 顶部一处) 收口含 policy_alignment。
- 证据: embedding_engine.py 顶部(38-47)实测无 HF 守卫; v1:43 四模块版漏 policy; v2:277-286 引擎单点含 policy_alignment。
- 必修: W12 改引擎单点 (embedding_engine.py 顶部一处 setdefault)。

#### [F12] (stale_vs_v2) 批2 W9 MinHash 序列化+复用点 (CF-9/CF-10)
- 发现: v1 W9 主体 tolist()=list[int] (bytes 仅风险段); uint64>2^63 经 int64 回绕破签名。且称唯一复用点 dedup_threshold:383, 漏 dedup_sensitivity:246(更高频)。
- 证据: compute_minhashes 2 caller: dedup_threshold:383+dedup_sensitivity:246。v2 W9(CF-9)bytes; (CF-10)列两 caller。VERIFICATION 旁注 _max_hash<2^32 list 其实能跑但 bytes 更稳。
- 必修: W9 主体用 bytes(uint64); 复用点列两 caller, dedup_sensitivity:246 也接 cache_dir。

#### [F13] (stale_vs_v2) 批4 W8 inference_cache 默认+双哈希 (CF-18/CF-15)
- 发现: v1 W8 inference_cache 默认 true (line 1206/1383), 仅 advisory; 裸环境首跑冻结漂移 argmax 污染未来 golden。_bert_cache_key 先 make_key 再当 model_id 传 get=二次哈希。
- 证据: v1:1206 get('inference_cache',True)/:1383 true。v2:327 CF-18 默认 false; CF-15 一次哈希。
- 必修: W8 inference_cache 默认改 false; _bert_cache_key 改一次哈希。

#### [F14] (stale_vs_v2) 批2 W4 after 块缩进 (CF-13)
- 发现: v1 W4 字面 after 块缩进深一级 (entity_masking:941 给 8/:732 给 12 空格), 逐字粘 IndentationError。实测 :941=4(main体)/:732=8(try内)。
- 证据: entity_masking.py:941=4 空格; :732=8 空格。v2 W4(CF-13)降同级。
- 必修: W4 after 块缩进降到 :941=4 空格/:732=8 空格。

#### [F15] (fact_error) §5 五铁律表 PREPROCESS_CODE_VERSION 位置 (CF-12)
- 发现: v1 §5 表把 PREPROCESS_CODE_VERSION 位置标 runner.py, 实际定义 _constants.py:131 (runner.py 仅 import@129/使用@197)。
- 证据: _constants.py:131='v3-2026-06-25-media-canon'; runner.py:129 import/:197 使用。v2 §5 已改指 _constants.py:131。VERIFICATION CF-12。
- 必修: §5 表 PREPROCESS_CODE_VERSION 改指 _constants.py:131。

#### [F16] (fact_error) §1 现状基线表 stage25 计时
- 发现: stage25 107s 是 HF 离线前 baseline, 现 ~14.2s (article_sbert.py:93 已 HF 离线)。若 §1 用 107s 当当前态论证 SBERT 缓存收益大则高估; 真瓶颈是 stage23(297→194s)。
- 证据: perf-audit:17 stage25 106.7→14.2s(7.5×); :34 107s 是 T=2 baseline; article_sbert.py:90-94 已 setdefault HF_HUB_OFFLINE。
- 必修: §1 若引 107s 须标 HF 离线前 baseline/现 ~14s; 计时来源精确到 perf-audit 实测(T=2 RTX3090)。

#### [F17] (fact_error) task 前提 / §-章节映射
- 发现: task 描述的执行计划特征查无实据: ①批次实为批1-4(v1+v2 均 4 批工作项一致), 无批1-5; ②§7 '不做项' (stage22 不加缓存/跨阶段 token 不共享/herd 非热点) 在 v1/v2 均无此章节(grep 空); ③task §4-§9 章节映射与 v2 实际(§0-§7: §4=批3/§5=批4/§6=验收/§7=决策点)完全错位(仅 §6 巧合对上)。
- 证据: grep 批1-5/不做项/跨阶段 token/herd 非热点 于 v1+v2 全 0; v2 章节实读 §0-§7; v1:80-86=批1-4。
- 必修: 这些特征来自缺失文档的不同编号体系。补写/定位执行计划时须用 v2 的 18 CF+4 批+§0-§7 章节逐条覆盖, 不让旧设计回流。

### LOW (3)

#### [F18] (stale_vs_v2) 批4 W7/批2 W4 缓存库键命名 (CF-16)
- 发现: v1 W7 引用 paths.llm_cache_db (config 不存在), W4 引入 filenames.output_llm_cache→命名分裂。
- 证据: config/paths.yaml 无 llm_cache_db/output_llm_cache (仅 output_27_benefit_cache@83)。v2 CF-16 统一 filenames.output_llm_cache。
- 必修: W7/W4 缓存库键统一 filenames.output_llm_cache(_validation)。

#### [F19] (stale_vs_v2) 批1 W3 frozen-hash EOL 归一 (CF-5)
- 发现: v1 W3 主测试块 sha256(PEER_PROMPT.encode) 无 EOL 归一; Windows CRLF 仓库→跨 EOL 误红。
- 证据: llm_peer_iv.py:322-335/:339/:367 锚点属实; v1 主块缺归一; v2 W3 主块=.replace('\r\n','\n')。
- 必修: W3 frozen-hash 主块加 EOL 归一(非仅风险段)。属测试红/绿非 golden。

#### [F20] (missing) 批4 W8 提速 ROI 夸大
- 发现: v1 W8 称 297s→秒级, 但最小化写法仍全 batch 跑 Step1-5, 命中也不省 forward。stage23 297s 无独立实测锚点(传闻值)。
- 证据: v1 W8 line 1310-1366 自陈全 batch 跑; line 1407 297s→秒级。v2 W8:328 已诚实标注须只对 miss forward。
- 必修: W8 加 v2 诚实标注(只对 miss forward); 默认关后影响有限。

## 让执行计划与 v2 零冲突的必改清单 (18 条)

- **[blocker]** 执行计划文件本体 (scripts/audit/CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md) — 当前缺失 → 先定位/补建该文件或确认已被 v2 吸收, 并在 v1:3/:339+v2:6 三处悬空引用旁标注『已并入 v2, 不再单独维护』或删除。文件存在前实现一律以 v2 为唯一权威。
- **[blocker]** §3 W5 核心设计 (config 子树 hash) → 整段替换为 v2: STAGE_CONFIG_FILES(stage→split YAML 文件名)+compute_config_file_hashes(哈希 YAML 文件内容), 绕开 CONFIG dict。删 STAGE_CONFIG_DOMAINS/CONFIG.get(域名)/config_subtree_hash 旧设计(CF-1 blocker)。
- **[blocker]** §3 W5 默认 Namespace → args=None 默认 Namespace 补 skip_unchanged=False+测试覆盖 args=None 路径(CF-2 blocker, 防 10+ 无参 run_pipeline AttributeError)。
- **[high]** §3 W5 验证 runner step6 → 删除 run_pipeline_validation.py 接 --skip-unchanged 的 step6(CF-11: 验证 stage _get_stage_output_files 恒返[]=死代码)。
- **[high]** §5/批4 W7 重生理由 → 改为 v2『截断128 vs 126-token 分块 mean-pool 表征机制变, semantic_staleness_* 显著变+改 Bybee 构念须 manuscript 披露』, 删 1e-7 叙述(CF-8); 加决策点(a)token 级截断保构念(旁注需新增 token 级截断, 现有字符截断不满足)/(b)接受分块+披露。
- **[high]** §3 W6 stage15 inputs 闭包 → 改真实闭包 (12_full,12_fintech) 均 stage12, 删 14_materialize_ctx(CF-7); 多源 stage 暂留 inputs=(); ③ 只比 spec.inputs∩recorded 交集。
- **[high]** 批4 W10 matched_words['word'] → 主 diff 块用 'word':r['token']保留 token, 删 'word':''骨架(CF-6, 否则破 sentiment_details+test_omni_fix_tonewords.py:222-223)。
- **[high]** 批3 W13 测试同步+死代码清单 → 测试清单补 test_strategic_diff_embedding.py; 死代码清单补删 strategic_diff._LOCAL_EMBEDDING_MODEL(:292)/_embedding_config_uses_local(:295)(CF-4)。
- **[high]** 批2 W11 Stata .log 路径 → 改 do_path.with_suffix('.log')得 foo.log(CF-3, 删 foo.do.log 死功能)。
- **[high]** §5 治理规范落点 → 改为仅追加 core/caching.py 模块 docstring 末尾, 删独立 docs/CACHE_VERSIONING_DISCIPLINE.md+test_discipline_doc_exists 单测(CF-12 旁注 news_process/docs/ 不存在)。
- **[medium]** §4/批3 W12 HF 离线设置点 → 改引擎单点(embedding_engine.py 顶部一处 setdefault HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE), 覆盖 policy_alignment(CF-17, v1 per-module 四模块版漏它)。
- **[medium]** 批2 W9 MinHash 序列化+复用点 → 主体改 bytes(uint64) astype('<u8').tobytes()(CF-9); 复用点列两 caller dedup_threshold:383+dedup_sensitivity:246, 后者也接 cache_dir(CF-10)。
- **[medium]** 批4 W8 默认值+哈希 → inference_cache 默认改 false(CF-18, 防裸环境冻结漂移污染 golden); _bert_cache_key 改一次哈希(CF-15)。
- **[medium]** 批2 W4 after 块缩进 → 降同级: entity_masking:941=4 空格/:732=8 空格(CF-13, 防 IndentationError)。
- **[medium]** §5 五铁律表 PREPROCESS_CODE_VERSION 位置 → 改指 _constants.py:131(非 runner.py; CF-12)。
- **[medium]** §1 现状基线表 stage25 计时 → 107s 标注为 HF 离线前 baseline/现 ~14.2s; 计时来源精确到 perf-audit 实测(T=2 RTX3090)。
- **[low]** 批1 W3 / 批4 W7·W4 键名 / 批4 W8 ROI → W3 主块加 .replace('\r\n','\n') EOL 归一(CF-5); W7/W4 缓存库键统一 filenames.output_llm_cache(_validation)(CF-16); W8 加『提速须只对 miss forward』诚实标注。
- **[low]** 事实陷阱顺手订正(跨 §1/§2/W7) → 确认执行计划任何处未照抄 article_sbert.py 512 心智模型; 修 W7 时建议顺手把 article_sbert.py 6 处 512 注释/日志(line 12/23/61/138/276/335-336)订正为 128(cosmetic golden-safe)。

## 被驳回的误报 (5 条, 附理由)

- 驳回: task 所谓『执行计划用批1-5 vs v2 用批1-4 错位』是真冲突需修
  - 理由: 驳回: 冲突另一方不存在。v1 §A.5(80-86)与 v2 §0(16-30)均批1-4 且工作项分批完全一致(批1=W1/W3/§5, 批2=W6/W5/W4/W9/W11, 批3=W12/W13, 批4=W7/W8/W10)。批1-5 在现存文档 grep 0 命中, 系基于缺失 EXECUTION_PLAN 的臆测。S2/S4 已正确标 both_wrong/查无实据。
- 驳回: S6 把 article_sbert.py 512 错注释当阻塞缓存改造的高危项
  - 理由: 部分降级: 512 是真实源码 bug(已记 F5)但独立于缓存改造、不阻塞。三份 cache 文档均未照抄(grep 0), v2 W7 正确用 128。S6 自标 verdict=minor_fixes 且把顺手订正列 low/medium 非阻塞, 判断正确。
- 驳回: S1 暗示 stage23 ~297s 时间数标来源 CLAUDE.md 即文档错误
  - 理由: 降级 low/无需修: 297/107/92s 数字本身真机实测属实(perf-audit:34, T=2 RTX3090)。CLAUDE.md 转述 perf-audit 不构成事实错误, 仅精确度可改进。真正需修的是 107s 当前态 vs HF 离线前 baseline 时态(已单列 F16)。
- 驳回: S2 担忧 v1 §A.1 把 fintech_intensity 误归 pipeline/features/(实际 filtering/)会误导
  - 理由: 驳回 low/非冲突: 三份文档锚点均用裸文件名 fintech_intensity.py:801, grep 可定位; v1/v2 W6/CF-7 正文未带错目录。S2 自标 low 且归纯定位提示, 不进 required_plan_edits。
- 驳回: S2 担忧 W5(3) config_file_hashes 进 schema metadata 的 golden-safe 未亲验需降 needs-regen
  - 理由: 降级 low/已被旁证: v1:99/857/987 三处已 Read test_panel_reproducibility.py:44-47 证 _column_hash 仅 hash_pandas_object(数据列)不碰 schema metadata; data_version 经 save_parquet_with_metadata:180 写 schema metadata blob(非数据列)。故 to_dict 加 config_file_hashes 键是 golden-safe。S2 自标 low 且建议落地前实读确认(谨慎正确), 不构成对执行计划的 stale 指控。
