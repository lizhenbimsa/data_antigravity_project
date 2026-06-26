# 缓存策略 diff 规格 — 对抗式验证裁决报告 (CACHE_STRATEGY_VERIFICATION_2026-06-25)

> 来源 = Workflow `wf_7f658605-d83` (6 集群独立 skeptic + golden 对抗审 + 完整性对抗审 + 1 裁决 agent)。
> 9 agent / 1.65M token / 409 工具调用。验证对象 = `CACHE_STRATEGY_DIFF_SPEC_2026-06-25.md`。

## 锚点逐字核验总评

我亲自 Read/Grep/runtime 复核了规格中最关键、最有争议的约 30 个 file:line 锚点与事实断言, 覆盖全部 blocker/high 候选。结论: 8 个 agent 报告的代码锚点【绝大多数逐字属实, 行号 0-±1 偏移】(features.yaml batch_size/version、embedding_engine 键构造、PEER_PROMPT 322-335/VERSION 339/.format 367、caching.py make_key/get/SCHEMA_VERSION、StageSpec 字段、run_pipeline_function 主循环/默认 Namespace、tone_words matched_words['word']/sentiment_details json.dumps、dedup_sensitivity:246、schemas.EXPECTED_NO_OUTPUT_STAGES、stata_runner /b+stem.log、article_sbert _truncate_for_sbert/encode_local 分块阈值、_constants.py:131 PREPROCESS_CODE_VERSION 定义处)。我用真机 load_config() 决定性地证实了最大争议点: _SPLIT_DOMAINS 的 7 个域名中只有 paths/preprocessing/validation 是 CONFIG 顶层键, 而 filtering/sentiment/features/panel 在 CONFIG 中【不存在】(返回 None) — 这坐实了 W5 STAGE_CONFIG_DOMAINS 的 blocker。规格自身存在两处【事实错误】: ① W6 line 590 "锚点修正注" 称 stage15 input_files 双源=12_full+14, 实测 producer 记的是 12_full+12_fintech_news (均 stage12, 不含 14); ② §5 表把 PREPROCESS_CODE_VERSION "位置" 标为 runner.py 而非定义处 _constants.py:131。规格的若干 before 锚点片段对真实代码字节级一致, 但多处 after 伪 diff 的【缩进比插入点深一级】(W4 三处 cache_db/banner) 且【字面骨架与风险段推荐自相矛盾】(W3 frozen-hash EOL 归一 / W9 uint64 序列化 / W10 word 字段) — 这些是规格"载荷正确版藏在散文、字面代码块是错版"的系统性危险呈现模式。

## 整体裁决

整份规格的【代码锚点测绘质量高】(我抽查的约 30 个 file:line 绝大多数逐字属实、行号 0-±1), 且把 13 项的 golden 安全性分类基本判对 (10 safe / 3 needs-regen 方向正确)。8 个验证 agent 的对抗复审整体可信、相互佐证度高, 我复核后【确认 18 条真问题】(2 blocker + 6 high + 7 medium + 3 low), 驳回 6 条误报/重复/前瞻性非 bug。规格【不能直接作为实现依据】, 主因是两个 blocker 与 W5 设计层的根本缺陷: ① W5 STAGE_CONFIG_DOMAINS 把 YAML 文件名当 CONFIG 顶层键 (真机实证 filtering/sentiment/features/panel 在 CONFIG 中不存在), 落地 (3) 即引入 silent staleness — 这是缓存版本门纪律本身要防的灾难, 讽刺地出现在'缓存策略'规格里; ② W5 主循环漏改 args=None 默认 Namespace, 会让 10+ 个无参 run_pipeline() 调用方 (含全部 paper pipeline + 锁 helper) AttributeError 崩溃。除两 blocker 外, 规格有一个反复出现的【系统性危险呈现模式】: 把'载荷正确的实现'藏在散文/风险段, 而字面 before→after 代码块给的是错版 (W3 frozen-hash 无 EOL 归一 / W9 uint64 用 list 而非 bytes / W10 sentiment_details word='') — 实现者照抄字面块就会破 golden/破测试/破构建。前置必补: (a) 修复 W5 两 blocker + ③ 比对契约 + 删 step6 死代码; (b) 把 W3/W9/W10 的散文正确版提升为唯一主代码块; (c) 修 W11 .log 路径死功能 + W13 漏改 test_strategic_diff_embedding.py + W6 stage15 inputs 错误闭包; (d) 修正 W7 重生理由 (表征机制变非 1e-7) 并据实披露 Bybee 构念漂移; (e) §5/W4 文档定位 (PREPROCESS_CODE_VERSION 定义处、docs/ 父根) 与 3 处缩进。批1 (W1/W3/§5)、批3 (W12/W13) 修小问题后可优先落地; W5 必须 needs-rework 重审后才进批2; needs-regen 三项 (W7/W8/W10) 攒 DEFERRED 统一受控重生的策略正确。修完上述前置, 规格可作为可靠实现依据。

## golden 重分类

| 工作项 | from | to | 理由 |
|---|---|---|---|
| W5(整体, 默认路径 + (3)落地) | safe | safe-only-after-blocker-fix (条件 safe) | 默认 flag 关闭路径在修复 CF-2 (args=None Namespace 加 skip_unchanged) 后对既有 golden 字节中性 (不重跑 stage21=不动 _llm_cache.db)。但 (3) 落地写 config_subtree_hash 后, 因 CF-1 的空子树 bug 会驱动错误跳过决策 → 用陈旧产物冒充新产物 = 等效污染下游/golden 输入。这不是改字节的 golden 问题而是 correctness blocker, 但其后果会脏化未来 golden 重生的输入。故 W5 的 'safe' 必须附条件: 先修 CF-1+CF-2, 且 ③ 覆盖 recorded 全集。 |
| W7 | needs-regen (理由: 1e-7 归一舍入) | needs-regen (理由修正: 截断→128-token 分块 mean-pool 的表征机制变化, 幅度远大于 1e-7) | golden 分类 needs-regen 本身正确无需改, 但【重生理由与变化幅度】被规格错误描述。审阅者须知 semantic_staleness_* 列会显著变 (非微变), 且这等于悄悄改了 Bybee 2024 截断构念, 应在 manuscript/codebook 披露, 而非当作纯性能改造的中性副作用。见 CF-8。 |

## 确认问题 (去重裁决后)

### BLOCKER (2)

#### [CF-1] W5 — STAGE_CONFIG_DOMAINS 用域名 filtering/sentiment/features/panel 作 CONFIG.get(d,{}) 的键, 但这些是 YAML 文件名, 不是 CONFIG 顶层键。真机 load_config() 实测: 仅 paths/preprocessing/validation 在 CONFIG 中; filtering/sentiment/features/panel 全部返回 None。故 _config_subtree_hash 对 stage11-16(filtering)/21-24(sentiment)/15/16/25/26/40(features)/40/46/51(panel) 算出的子树几乎全空 (仅 paths 非空)。一旦 (3) 落地写 config_subtree_hash 并据此比对, 改 cooccurrence_filter.sentence_radius / fintech_intensity 阈值 / sentiment_analysis / panel_building 等真实参数都【不会】改子树 hash → stage 被错误跳过 → 消费陈旧产物 = silent staleness。这恰是整个缓存版本门纪律要防的灾难, 并污染下游/golden 输入。规格 §A.1:33/§A.3:55 反而双重强化'域名取 _SPLIT_DOMAINS'的错误心智模型, 全程未察觉。
- **证据**: core/config.py:24-27 (_SPLIT_DOMAINS=YAML文件名); 真机 load_config(): cfg.get('filtering')/('sentiment')/('features')/('panel')→None; config/filtering.yaml 顶层键=bank_news_classification/fintech_intensity/cooccurrence_filter/article_alignment/context_window; sentiment.yaml=tone_llm_processing/sentiment_analysis/herd_detection/article_staleness; features.yaml=embedding_api/embedding_robustness/benefit_society/strategic_diff; panel.yaml=panel_building; spec line 621-638 + 664-667 (domains→CONFIG.get(d,{}))
- **必修**: 把 STAGE_CONFIG_DOMAINS 的域名集替换为真实 CONFIG 顶层键集 (filtering→{bank_news_classification,fintech_news_classification,fintech_intensity,article_alignment,context_window,cooccurrence_filter}, sentiment→{tone_llm_processing,sentiment_analysis,herd_detection,article_staleness}, features→{embedding_api,embedding_robustness,benefit_society,strategic_diff}, panel→{panel_building}), 或直接哈希对应 YAML 文件【内容】(compute_file_hash); 并加单测断言每个声明键 ∈ CONFIG 顶层键集 (而非 ⊆ _SPLIT_DOMAINS)。在修正前禁止落地 W5(3)。
- _提出者_: C-skip(blocker), 横切完整性(blocker); golden-safety 间接(risky)

#### [CF-2] W5 — run_pipeline_function.py:424-425 的 args is None 兼容分支 `args = argparse.Namespace(skip_21_if_exists=False)` 不含 skip_unchanged 属性。W5 主循环 (spec line 922) 无条件 `if args.skip_unchanged:` → 所有以 run_pipeline()(无 args) 调用的路径命中 AttributeError 整链崩溃。该路径是文档明确支持的向后兼容入口, 实测有 10+ 调用方: core/locking.py:31 / papers/_common/pipeline_runner.py:30 / 8 个 paper analysis.py (tone/collab/substance/attention/locus/bank_media_disagreement/benefit_society/bank_news_clarity)。W5 测试 (d) 只测 _parse_cli_args([]).skip_unchanged, 不覆盖 args=None Namespace 路径 → 测不出。
- **证据**: run_pipeline_function.py:424-425 (Namespace 仅 skip_21_if_exists=False); grep run_pipeline( 命中 core/locking.py:31 + papers/_common/pipeline_runner.py:30 + 8 paper analysis.py; spec line 922/954 `if args.skip_unchanged:`
- **必修**: 同步把 run_pipeline_function.py:425 改为 argparse.Namespace(skip_21_if_exists=False, skip_unchanged=False); 并新增覆盖 args=None 路径的回归测试。
- _提出者_: C-skip(blocker), golden-safety(high), 横切完整性(blocker)

### HIGH (6)

#### [CF-3] W11 — _rundo_can_skip 把 .log 路径算成 stamp_path.name.replace(_RUNDO_STAMP_SUFFIX,'.log')→对 foo.do 得 foo.do.log。但 Stata /b do foo.do 实际写的 log 是 foo.log (去 .do 扩展)。故 log 存在性检查永远失败 → _rundo_can_skip 恒返 False → W11 内容寻址跳过功能实质从不命中 (dead-on-arrival)。且 test_run_do_skips_on_matching_key 自造同款 foo.do.log 路径 → 测试自洽通过 → 给假信心 (假绿)。golden-safe (错向永远重跑, 绝不误命中), 但功能失效。
- **证据**: scripts/run_stata.ps1:108 `$logPath = Join-Path $do.DirectoryName ($do.BaseName + '.log')` (BaseName=去扩展名); stata_runner.py:130-135 cmd=[bin,'/b','do',str(do_path)]; spec line 1883 _stamp_path=do_path.with_suffix(suffix+SUFFIX) + line 2007 .log 推导
- **必修**: 改为 log_path = do_path.with_suffix('.log') (即 do_path.parent/(do_path.stem+'.log')); 同步修测试使其用真实 stem.log 路径, 防假绿。
- _提出者_: F-cleanup(high), 横切完整性(high)

#### [CF-4] W13 — W13 死代码/测试同步清单只列 test_25_audit.py / test_benefit_society_embedding.py / test_network_spillover_embedding.py 三个文件, 完全遗漏第四个嵌入测试 tests/test_strategic_diff_embedding.py:36 (monkeypatch.setattr(sd,'_LOCAL_EMBEDDING_MODEL',None))。实测 strategic_diff._LOCAL_EMBEDDING_MODEL(:292)/_embedding_config_uses_local(:295) 经 grep 均零内部引用=死孤儿 (与将删的 _encode_embeddings_local 同型)。两难: (a) 若实现者按'清死全局'本能删 sd._LOCAL_EMBEDDING_MODEL → 该测试 monkeypatch (默认 raising=True) 抛 AttributeError 整文件 collect error → 全量 sweep '无新增失败'验收失败; (b) 若按规格字面只删两函数保留 _LOCAL_EMBEDDING_MODEL → 测试过但死全局残留, 与 W13 对 network/benefit 的同型清理标准不一致、与 ruff-clean 目标冲突。规格须显式二选一并同步此文件。
- **证据**: tests/test_strategic_diff_embedding.py:36,38; grep strategic_diff.py: _LOCAL_EMBEDDING_MODEL 仅 :292 / _embedding_config_uses_local 仅 :295 / _encode_embeddings_local 仅 :300 (均零内部引用); spec line 2191-2192 死代码表只列 _encode_embeddings_local/_get_embeddings_api, 验收命令 line 2278 不含 test_strategic_diff_embedding
- **必修**: 把 test_strategic_diff_embedding.py 纳入 W13 测试同步清单, 与其它三个同型重写 (改 monkeypatch _eng._LOCAL_MODELS 或保留对存在符号的 patch); 并在死代码表明确 _LOCAL_EMBEDDING_MODEL/_embedding_config_uses_local 是删还是留, 与测试改动一致。
- _提出者_: F-cleanup(high), golden-safety(high), 横切完整性(blocker)

#### [CF-5] W3 — W3 frozen-hash 主测试代码块 (spec L214-220) 写 hashlib.sha256(PEER_PROMPT.encode('utf-8')) 【未含 EOL 归一】, 而风险段③ (L227) 正确指出 Windows CRLF 风险并推荐 .replace('\r\n','\n') 归一。两处给了【两套互斥】哈希口径: 主块给的实现 EOL 敏感, 跨 EOL checkout/CI 误红; 若照风险③归一则首填的 PEER_PROMPT_SHA256 也须按归一字节算。llm_peer_iv.py 在 Windows 仓库且 .gitattributes 未把 .py 标 binary → PEER_PROMPT 三引号内换行随盘 EOL。规格未把风险③归一版提升为主块唯一实现, 是落地隐患 (实现者二选一易选错)。
- **证据**: pipeline/panel/llm_peer_iv.py:322-335 (PEER_PROMPT 含硬 \n 换行) Windows 仓库; spec L215 主块无归一 vs L227 风险③建议归一; .gitattributes 未标 .py binary
- **必修**: 把风险③的 EOL 归一 (.replace('\r\n','\n')) 烘进主测试块为唯一实现, 删除/修正无归一的主块; PEER_PROMPT_SHA256 首填值按归一后字节计算; 注释写明归一规则。
- _提出者_: A-guards(high), 横切完整性(medium)

#### [CF-6] W10 — W10 包装层重建 matched_words 的字面伪 diff (spec L1743-1750) 用 'word':'' (最小内存版), 只在散文开放问题 (L1753+) 说'审阅时按保留 token 落地'。实测 sentiment_details 是 stage22 真实输出列: tone_words.py:1439-1440 sorted(union_matched,...)[:20] 后 json.dumps(top_detail) 整条 dict (含 matched_words.append 的 'word':token, L759-764) 序列化进 JSON。若照字面骨架 'word'='' → sentiment_details JSON 字节变 → 破字节等价 (即便 needs-regen 也无意改值), 且 tests/test_omni_fix_tonewords.py:222-223 直接读 m['word'] 断言 '下跌'/'上涨' ∈ words → 立即 FAIL。规格字面代码块是错版, 载荷正确版藏散文。
- **证据**: tone_words.py:759-764 (matched_words 含 'word':token), 1439-1440 (json.dumps(top_detail)); tests/test_omni_fix_tonewords.py:222-223; spec L1743/1745/1749 'word':''
- **必修**: 主 diff 体直接给 'word': r['token'] (保留 token) 版, 删除/修正 'word'='' 最小内存骨架; 确保 _scan_sentiment_trace 中间表带 token 字段供包装层重建。
- _提出者_: E-withinstage(high), golden-safety(medium), 横切完整性(medium)

#### [CF-7] W6 — W6 示例 inputs (spec L582) 把 stage15 inputs 写成 ('14_materialize_ctx.py','12_news_fintech.py'), 且 L590 '锚点修正注'声称'stage15 input_files 双源=12_full+14'。两者都与 producer 实况不符: fintech_intensity.py:801 save_dataset(input_files=[full_path, input_file]), 其中 full_path=12_fintech_news_full.parquet(L666), input_file=12_fintech_news.parquet(L793-794) — 【均为 stage12 产出, 不含 stage14】(14_news_with_ctx.parquet 被读 L671-672 但未记入 input_files)。按 W5 ③ 比对契约, _stage_skip_is_safe 要求每个上游产物 basename ∈ recorded input_hashes; 声明 14 但 recorded 无 14 → 永久 return False → stage15 结构性永不可跳。更广: stage12 产 2 文件、stage40 产 5 文件 (含 3 个 40_attn_index_*) 而下游只读子集, 凡上游 fanout 多产物或 producer 漏记上游, ③ 必 False → stage13/15/51 等多数 stage 增量价值=0。规格 '锚点修正注' 是事实错误。
- **证据**: fintech_intensity.py:666(full_path=12_full)/793-794(input_file=12_fintech_news)/801(input_files=[full_path,input_file])/671-672(读14但不记); spec L582+L590; export.py(stage40 5产出)/controls.py(stage51 漏记 attn_index)
- **必修**: 按 producer 真实 input_files 闭包填 inputs (stage15 顶多 ('12_news_fintech.py',) 且仍要保证 12_full+12_fintech 两 basename 都在 recorded); 修正 L590 错误'修正注'; W5 ③ 改为只比对 spec.inputs∩recorded 交集, 或要求各 producer 把声明上游全记入 input_files; 首批只填确认能通过的线性链。
- _提出者_: C-skip(high anchor fact_wrong+missed), 横切完整性(部分)

#### [CF-8] W7 — W7 把 SBERT encode_articles 的 forward 从 model.encode(docs, normalize_embeddings=True) 改走 embed_texts→_encode_local_cached→encode_local。规格仅把数值差归因为 'fp64 vs fp32 归一化舍入 ~1e-7'(spec L1095)。但实测路径更深: docs=_truncate_for_sbert= title[:100]\|content[:300] ≈ 400 中文字符 ≈ ~400 token >> text2vec max_seq=128; 历史 model.encode 对超长 doc 模型内部【静默截断】到 128 token, 而 encode_local(L286-342) 对 len(ids)>effective_max(126) 改为【分块 + 逐块 L2 归一 + token 加权 mean-pool】。这是截断 vs 分块池化的【表征机制变化】, 远大于 1e-7 归一漂移 → semantic_staleness_* 余弦会显著变, 且改变了 Bybee 2024 '标题+首段300字截断'构念口径。needs-regen 分类正确, 但 spec 严重低估变化幅度, 'definitively 定性不变'/微变叙述有学术诚信风险。
- **证据**: article_sbert.py:133-143(_truncate_for_sbert title[:100]\|content[:300]), 210-218(历史 model.encode normalize_embeddings=True); embedding_engine.py:265(t2v=128 静默截断注释),286-342(encode_local 分块mean-pool),304-305(len(ids)<=effective_max 才直送); spec L1058-1093(走 embed_texts)+L1095(归因1e-7)
- **必修**: 在 manuscript/codebook 如实披露 W7 后 SBERT 表征从'模型截断 128tok'变为'126-token 分块 mean-pool'(纳入本应丢弃的尾段), 非 1e-7 微变; 若团队要保 Bybee 截断构念, 需在 embed_texts 前显式截断 docs 到模型上限或保留 model.encode 截断路径 (当前 spec 无此设计)。
- _提出者_: D-localmodel(high), golden-safety(medium), 横切完整性(medium)

### MEDIUM (5)

#### [CF-9] W9 — W9 主 diff 体 (spec L1510/1535) 用 list[int] 落 parquet + np.asarray(uint64) 读回; 正确的 bytes 版 (m.hashvalues.astype('<u8').tobytes()) 仅放在风险段 (L1579)。datasketch hashvalues 是 uint64, 经 parquet int64 往返, >2^63 的值符号回绕→重建 MinHash 错误→破 dedup 阈值敏感性 (validation 旁路但仍 bug)。注: 实测 datasketch _max_hash=4294967295 (<2^32), 真实数据 list 路径其实能跑 (此风险对真实输出过度保守), 但 bytes 版确更稳健且符合 spec 自陈最终意图。同 W3/W10 一样字面骨架 vs 散文推荐割裂。
- **证据**: spec L1510/1535(list骨架)/L1579(bytes推荐); datasketch 实测 _max_hash=4294967295
- **必修**: 主 diff 体直接给 bytes 序列化版 (astype('<u8').tobytes() 存 binary 列, np.frombuffer 读回), 删除 list[int] 骨架; 单测覆盖 hashvalues 往返逐位等价。
- _提出者_: E-withinstage(medium), golden-safety(medium), 横切完整性(medium)

#### [CF-10] W9 — W9 多处声称 validation/dedup_threshold.py:383 是 compute_minhashes 的'唯一复用点/唯一 load-bearing 重指针'(§A.2+W9 line 1550)。实测有第二个 caller: pipeline/panel/dedup_sensitivity.py:246 (compute_dedup_sensitivity_treatments 内, 同款'MinHash 签名一次计算, 变体间复用'意图), 经 runner step 6b-3 在每次 stage40 生产面板构建时跑全语料 MinHash — 这是更高频、更高价值的生产路径缓存目标却被忽略。加 cache_dir=None 默认不破该 caller, 但'唯一复用点'是事实错误且漏掉生产路径缓存收益。
- **证据**: pipeline/panel/dedup_sensitivity.py:243-246 (dedup.compute_minhashes(arts_prep)); spec §A.2 line 44 + W9
- **必修**: 更正'唯一复用点'措辞; 同步给 dedup_sensitivity.py:246 接入 cache_dir 以获生产路径缓存收益 (或显式说明刻意不接)。
- _提出者_: E-withinstage(medium), 横切完整性(medium)

#### [CF-11] W5 — W5 step6 验证 runner 接入对全部验证阶段 60-75 是死代码。schemas.py:172-193 EXPECTED_NO_OUTPUT_STAGES 含 60-75 全部 (包括 72/73/75 — 它们虽物理写 data/processed/72\|73\|75_*.parquet 但显式不进 OUTPUT_REGISTRY)。_get_stage_output_files 只返 OUTPUT_REGISTRY 文件 → 对 60-75 全返 [] → _stage_skip_is_safe 第①步 if not outputs: return False → 永远重跑。spec line 949 称'对 72/73/75 等真产 parquet 且声明 inputs 的验证 stage 生效'是错的; 整段 validation-runner 接入 (新增 argparse+import+循环判定) 零功能价值, 徒增 CLI 复杂度与维护面。golden-safe。
- **证据**: core/schemas.py:172-193 (EXPECTED_NO_OUTPUT_STAGES 含 60-75 全部 + 72/73/75 注释); run_pipeline_function.py:115-155(_get_stage_output_files 对非 registry 返 []); spec line 949
- **必修**: 删除 W5 step6 整段验证 runner 接入 (零价值), 或明确标注'为未来产 OUTPUT_REGISTRY parquet 的验证 stage 预留, 当前 no-op'; 修正 line 949 对 72/73/75 的错误断言。
- _提出者_: C-skip(medium), 横切完整性(high)

#### [CF-12] §5/W4 — §5 治理文档表把 PREPROCESS_CODE_VERSION 的'位置'标为 pipeline/preprocess/runner.py, 但其【定义】在 pipeline/preprocess/_constants.py:131 (PREPROCESS_CODE_VERSION='v3-2026-06-25-media-canon'); runner.py 仅 import (L129) 并使用 (L197 等)。作为'单一事实源'治理文档, 把版本门常量指向错误文件会误导维护者去 runner.py 找/改。
- **证据**: _constants.py:131 (定义); runner.py:129(import)/197(使用); spec §5 表 line 251
- **必修**: §5 表'位置'列改为 pipeline/preprocess/_constants.py:131 (定义处), 治理文档行号须指向定义处才是单一事实源。
- _提出者_: A-guards(medium), 横切(间接)

#### [CF-13] W4 — W4 三个 cache_db/banner 替换点 (prompt_sensitivity:1583 / entity_masking:941 / entity_masking:732) 的 spec after 块缩进比真实插入点【深一级】: 实测 entity_masking:941 cache_db 在 main 体内是 4 空格、:732 banner 在 try 内是 8 空格; 而 spec after 块对应给的是 8 空格 / 12 空格。逐字粘贴会触发 IndentationError (unexpected indent)。逻辑正确, 系统性缩进抬高一级。
- **证据**: validation/entity_masking.py:941(4空格)/732(8空格); spec L408-414(_val_cache_fn/cache_db/with 用 8空格, logger 12空格) vs 真实 4/8
- **必修**: 落地时把 after 块缩进降到与插入点同级 (cache_db/with 处 4 空格; banner 处 8 空格); 实现者勿逐字复制缩进。
- _提出者_: B-valcache(medium×3)

### LOW (5)

#### [CF-14] W4 — W4 设计说明与 paths.yaml 注释称隔离让 'verify_stage21_cache_coverage 的 hits/misses 计数只反映生产语料, 不被验证键稀释' (收益①)。实证不成立: verify 脚本 (L111-127) 对生产键做点查 cache.get(prompt_version=tone_llms.PROMPT_VERSION, 生产 prompt 文本); 验证键 prompt_version 不同+prompt 文本不同 → 永不被该脚本 lookup → 即使同库共存也 0 影响 hits/misses。真实收益仅: (a) 两验证阶段 cache.size() 日志计数更纯, (b) 生产 .db 文件不因跑验证而增长。隔离仍 safe/无害, 但收益①是 hygienic 非 verify 正确性修复, 定性 overstated。
- **证据**: scripts/audit/verify_stage21_cache_coverage.py:111-127 (点查生产键计数); spec/paths.yaml W4 注释 line 362-363
- **必修**: 修正 paths.yaml/设计说明措辞: 隔离收益是 hygiene (size 日志纯净 + 生产库不增长), 而非'verify 计数不被稀释'(后者本就由点查免疫)。
- _提出者_: B-valcache(medium→low)

#### [CF-15] W8 — W8 _bert_cache_key 经 LLMCache.make_key(model_slot,content,pv='bert-v1') 算出 64-hex 哈希, 再把该哈希当 model_id 传 get/put → LLMCache.get 内部再 _make_key(<哈希>,content_i,'bert-v1') 二次哈希 → content 进键两次、_bert_cache_key 输出被浪费。因 get/put 同款双哈希仍能 round-trip (功能不破), 但与 §A.3 自称'把复合身份串塞进 make_key 的 model_id 槽'写法不符, 冗余易误。非 golden 问题, 代码质量瑕疵。
- **证据**: caching.py:277(make_key)/302-324(get 内部 _make_key); spec L1264-1272/1311-1313/1341-1343
- **必修**: 正确写法: cache.get(model_slot_composite_string, content, prompt_version='bert-v1') 不预哈希 (复合身份串直接塞 model_id 槽, 让 _make_key 一次哈希); 删除 _bert_cache_key 预哈希。
- _提出者_: D-localmodel(high→实为low), golden-safety(low)

#### [CF-16] W7/W4 — 缓存库 config 键命名空间跨集群不一致: W4 把生产库键放在 filenames.output_llm_cache, 而 W7 (spec L1111) 引用 paths.llm_cache_db — 实测 config/paths.yaml 既无 llm_cache_db 也无 output_llm_cache (均为拟新增/依赖默认)。W7 的 llm_cache_db 与 policy_alignment.py:150 既有写法一致 (永走 fallback '_llm_cache.db'), 功能上靠默认回退正确, 但与 W4 引入的对称键命名分裂。§A 跨集群对账未捕获此矛盾。
- **证据**: config/paths.yaml(无 llm_cache_db / 无 output_llm_cache); spec W7 L1111 (paths.llm_cache_db) vs W4 L365 (filenames.output_llm_cache); policy_alignment.py:150
- **必修**: 统一缓存库键命名 (建议都用 filenames.output_llm_cache 或都用 paths.llm_cache_db), 跨集群对齐, 避免维护混乱。
- _提出者_: D-localmodel(low/medium), 横切完整性(low)

#### [CF-17] W12 — W12 per-module HF offline setdefault 只覆盖 fintech_intensity/strategic_diff/benefit_society/network_spillover 四处, 漏 policy_alignment (stage 16, 同样经 _eng.embed_texts→encode_local→裸 SentenceTransformer 走本地轨)。单独跑 stage 16 且无前述模块先被 import 时, 进程无 HF offline → 会做 hf.co revision 网络解析 (正是 W12 要消除的)。规格 A.3/开放问题倾向'引擎单点'方案可一并覆盖, 但落地伪 diff 给的是 per-module 版且漏 policy_alignment。
- **证据**: policy_alignment.py 无 HF offline guard; spec W12 逐文件版四模块不含 policy_alignment; §A.6 line 92 倾向引擎单点
- **必修**: 采纳引擎单点方案 (embedding_engine.py 顶部一处 setdefault) 根本收口, 或在 per-module 版补 policy_alignment。
- _提出者_: F-cleanup(medium→low), 横切(medium)

#### [CF-18] W8 — W8 inference_cache 默认 true (spec L1374) + _DETERMINISTIC_MODE 默认 cpu_strict → 缓存默认 ENABLED; 而 W8 标 needs-regen (argmax 边界冻结)。若在 DEFERRED golden 受控重生前, 有人在 BLAS 未钉死环境跑 stage23, 缓存会冻结漂移的 argmax 值并持久化到 _local_model_cache.db, 此后离线复现锁死错误值→污染未来 golden bless。§A.5 建议'若 W5 落地则降级默认关'仅 advisory, 未在逐文件 diff 强制。foot-gun。
- **证据**: spec L1374(inference_cache:true) vs §A.5 line 77-78(建议降级默认关); tone_berts.py:170(cpu_strict default)
- **必修**: 在受控重生窗口前把 inference_cache 默认设 false (或硬绑 W5 落地条件), 仅手动单 stage 调试时开 + 受控播种。
- _提出者_: D-localmodel(medium), 横切完整性(medium→low)


## 被驳回的误报 (附理由)

- **驳回**: (D-localmodel high) W7 借机把 model_revision 钉死进缓存键 是对既有 _load_sbert_model load-time revision 钉死(article_sbert:168-170)的回归, 因 encode_local→SentenceTransformer(model_id,device) 不传 revision
  - 理由: 实测 features.yaml embedding_robustness 块【无 revision 字段】, 当前 _SBERT_REVISION/spec revision 恒为 None → 既有 _load_sbert_model 的 revision 钉死 (L168-170) 在当前配置下本就是 no-op (走 L170 无 revision 分支)。W7 走 encode_local 同样无 revision 也只是另一个无 revision 路径。故'回归既有钉死能力'在当前配置下无实际差异 (两路径都加载默认 HEAD)。这是前瞻性隐患而非当前 bug; D-agent 自己也标'当前 revision=None 故无即时 bug'。不构成 confirmed real-bug, 降为提示。
- **驳回**: (D-localmodel/B 多处) radius_sensitivity_llm 模块 docstring 自称 STAGES_VALIDATION 是 spec 引入的错误 / radius :341/:379 硬编码 _llm_cache.db 是 W4 遗漏
  - 理由: B-agent 自己核实 radius_sensitivity_llm 模块【未注册进 DAG】(仅 65_radius_sensitivity.py 无 _llm 后缀), docstring 自称 STAGES_VALIDATION 是该模块【既有误述】非 spec 引入; :341/:379 硬编码是未实装模块的死路径, 现无害。spec 已在 :161 加'W4 未来'注释。这是模块自身的既有瑕疵, 不是本规格的缺陷, 不计入对规格的 confirmed_findings (最多是规格注释覆盖不全的 low 提示)。
- **驳回**: (C-skip) W5 _stage_skip_is_safe ③ 默认不做(3)时词典内容变更检测失效 → 改 bank_names.json 内容被错跳 (high/needs-rework)
  - 理由: 部分成立但被 CF-1 的 blocker 修复覆盖, 不另立: 该问题的根因与修法都收敛到'③ 应遍历 recorded input_hashes 全集 (含词典) 而非仅声明 inputs'。但需注意: 默认部署若只走 ①整config_hash回退 + ③, 而 producer 已把词典 sha256 记进 input_hashes (news_bank.py:695/news_fintech.py:441 实证), 则只要 ③ 改为比对 recorded 全集即可覆盖。这是 CF-1/CF-7 必修项的一部分 (W5 ③ 改比对 spec.inputs∩recorded 或 recorded 全集), 已在 CF-7 required_fix 中收口, 不重复计为独立 finding 以免双计。
- **驳回**: (D-localmodel) W12 stage15 改走 encode_local 会因 chunk 路径 L2 归一致 centroid 漂移 (初判担忧)
  - 理由: D-agent 与横切 agent 均自行复核并撤回: embedding_engine.py:324-325 `if len(chunks)==len(texts): return raw` — 关键词全是短词 (≤126 token, 单 chunk) 时直接返回未归一的 model.encode raw 输出, 与原 fintech_intensity.py:371 model.encode(kw_list) 字节一致。fintech 关键词 (~1500 词) 均短, 不触分块。故 W12 stage15 byte-equal 成立 (与 W7 的长文档分块情形不同)。此担忧已被 324-325 早返分支化解, 不是 bug。
- **驳回**: (横切/golden) W8 needs-regen 应改 should_be_safe (首跑空 db 全 miss→用刚 forward 的 res 与无缓存路径字节相同)
  - 理由: 该重分类逻辑在'首跑环境==golden 环境'前提下成立, 但前提脆弱: argmax 边界 + round4 在 BLAS 未钉死/GPU 浮点漂移环境下首跑会冻结漂移值 (恰是 CF-18 的 foot-gun)。保留 needs-regen 是更安全的保守分类 — 与项目'宁可多重生绝不误 bless'铁律一致。不接受 should_be_safe 重分类; 维持 needs-regen, 并以 CF-18 (默认关缓存) 兜住风险。
- **驳回**: (C-skip) W5 命中跳过减少非确定源触发 → golden-safe (claimed safe)
  - 理由: 在【正确判定】前提下方向正确, 但因 CF-1 (子树 hash 对 filtering/sentiment/panel 域全盲) 落地后会错误跳过真正变更的 stage → 消费陈旧产物冒充新产物 = 等效污染 golden 输入。故该 'safe' 标注在 (3) 落地后应降级。但这不是独立 finding — 它是 CF-1 blocker 的下游后果, 已在 CF-1 中说明; 此处仅驳回其'无条件 safe'的乐观结论, 修复 CF-1 后方成立。

## 13 工作项逐项裁决

| 工作项 | 裁决 | 必修 |
|---|---|---|
| W1 (batch_size 纳入 t2v 版本纪律 注释+单测) | **go-with-fixes** | 安全无误的纯注释+单测。仅 1 处 low: test_t2v_version_is_lintable_string 须用 re.search (不加 $ 尾锚), 因 'v2-2026-05-29-t2v' 日期段在中间、尾部是 -t2v; 规格补一句'勿加结尾锚'。golden safe, 锚点全对 (features.yaml:39/41, embedding_engine:598-607/641-645, spec_version 回退 v0@218)。 |
| W3 (PEER_PROMPT frozen-hash 单测+lint决策) | **go-with-fixes** | 必修 CF-5 (high): 把 EOL 归一 .replace('\r\n','\n') 烘进 frozen-hash 主测试块为唯一实现, 删无归一主块, SHA256 首填按归一字节算。其余锚点全对 (PEER_PROMPT 322-335/VERSION 339/.format 367/{{peers}} 转义), 不动 check_prompt_headers/pre-commit 决策正确。golden safe。 |
| §5 (CACHE_VERSIONING_DISCIPLINE.md + caching docstring 追加) | **go-with-fixes** | 必修 CF-12 (medium): §5 表 PREPROCESS_CODE_VERSION '位置'改为定义处 _constants.py:131 (非 runner.py)。澄清 docs/ 是【父仓库根】docs/ (cwd=news_process 时相对 docs/ 会落错位置 news_process/docs/, 该目录不存在); 验收 grep 命令与新建文件用父根绝对路径。纯文档+注释, golden safe, SCHEMA_VERSION='v1'@141 不变量不碰。 |
| W4 (验证缓存隔离 _llm_cache_validation.db) | **go-with-fixes** | 修 CF-13 (medium, 3处 after 块缩进降到插入点同级防 IndentationError) + CF-14 (low, 修正'verify 计数不被稀释'overstated 措辞为 size 日志/库不增长 hygiene)。建议同步 tone_llms.py:2023/2224 两处生产硬编码到 output_llm_cache 键以兑现'对称化'(否则该键 dormant)。golden safe (键算法零改、验证 prompt 与生产键互异、verify 仍读生产库)。 |
| W5 (--skip-unchanged 通用增量跳过) | **needs-rework** | 两 blocker 必修: CF-1 (STAGE_CONFIG_DOMAINS 域名改真实 CONFIG 顶层键集或哈希 YAML 内容, 否则 filtering/sentiment/features/panel 域 config 变更全部不可见=silent staleness) + CF-2 (run_pipeline_function.py:425 默认 Namespace 加 skip_unchanged=False, 否则 10+ 无参 callsite AttributeError 崩)。再修 CF-7 (③ 比对 spec.inputs∩recorded 交集/recorded 全集, 解 fanout 永不可跳 + 词典内容检测) + CF-11 (删 step6 验证 runner 死代码或标 no-op)。新增测试须覆盖 args=None 路径与真实子树域。修复前不得落地。 |
| W6 (StageSpec 加 inputs/fingerprint_cols) | **go-with-fixes** | dataclass 字段扩展 (frozen + tuple 默认空) 本身 golden-safe 且 test_dag_consistency 不破。但必修 CF-7 (high): 修正 L590 错误'修正注'(stage15 input_files 是 12_full+12_fintech 非 14); 各 StageSpec inputs 须以 producer 真实 save_dataset(input_files=) 闭包为准, 首批只填确认能通过比对的链, 多源 fan-in/漏记上游的 stage 暂留空。与 W5 ③ 修复联动。 |
| W7 (SBERT 复用穿透缓存) | **go-with-fixes** | needs-regen 分类正确, 锚点全对。必修 CF-8 (high): 在 manuscript/codebook 如实披露 W7 后 SBERT 从'模型截断128tok'变'126-token 分块 mean-pool'(表征机制变, 非1e-7), 修正 spec L1095 归因; 若要保 Bybee 截断构念须 embed_texts 前显式截断 docs。CF-16 (low) 统一 llm_cache_db 键命名。并入 DEFERRED 受控重生。 |
| W8 (BERT 推理缓存) | **go-with-fixes** | 维持 needs-regen (拒 should_be_safe 重分类, argmax 边界脆弱)。必修 CF-18 (默认 inference_cache=false 直到受控重生窗口, 防裸环境冻结漂移 argmax 污染未来 golden)。修 CF-15 (low, 删 _bert_cache_key 预哈希避免双哈希冗余); 修 W8 get-override 仍全量 forward 的'297s→秒级'提速名不副实 (或改 Step1-5 只对 miss 文章构窗); _checkpoint_fingerprint 对 HF hub 模型退化为 no-ckpt:<id> 失去换版保护 (medium, 应披露)。W5 落地后本项可降级可选。 |
| W9 (MinHash 签名 sidecar) | **go-with-fixes** | golden-safe (validation 旁路、签名确定→命中逐位等价、生产 stage00 不启用)。必修 CF-9 (medium, 主 diff 体直接用 bytes 序列化版, 删 list[int] 骨架) + CF-10 (medium, 更正'唯一复用点'并给 dedup_sensitivity.py:246 也接 cache_dir)。datasketch 版本入键作版本门正确。 |
| W10 (词典 powerset 单次扫描重构) | **go-with-fixes** | 引擎数学层经独立 208 用例真机复现【逐位等价】(E-agent 实证, struct.pack bit-exact), 重构本身正确。必修 CF-6 (high): 主 diff 体直接给 'word': r['token'] 保留 token 版, 删 'word'='' 骨架 (否则破 sentiment_details 输出 + test_omni_fix_tonewords.py:222-223 FAIL)。采保留 token 后本身 golden-safe, 搭车既有 rule-ablation DEFERRED 批 + 真机==测试为门。 |
| W11 (Stata run_do 内容寻址跳过) | **go-with-fixes** | 必修 CF-3 (high): _rundo_can_skip 的 .log 路径改 do_path.with_suffix('.log') (Stata /b 产 stem.log 非 foo.do.log), 否则跳过永不命中=死功能且自带测试假绿。修 W11 描述句计数自相矛盾 (增3 vs 列4)。建议 _compute_rundo_key 复用 core/data_versioning.compute_config_hash/compute_file_hash (§A.3)。golden safe (编排层不进 panel, 默认 skip 关)。 |
| W12 (HF offline + stage15 走 encode_local) | **go-with-fixes** | HF offline 是 tone_berts:133/article_sbert:93 已落地先例+真机背书, 切加载来源不改权重=safe; stage15 短关键词不触分块 (encode_local:324-325 早返直送) byte-equal 经核实成立。修 CF-17 (low/medium, 采引擎单点 HF offline 收口或补 policy_alignment)。规格'逐位一致'依赖其验收 L2171 的真机改前后 sha256 比对 (须执行, 因 encode_local 新增 ensure_torch_determinism 而旧裸路径未设, GPU 上理论可致 FP 位差)。 |
| W13 (legacy 死代码清理) | **go-with-fixes** | 删的 6 函数经 grep 实证生产 0 调用, 活路径全走 _eng.embed_texts → golden-safe; 保留 policy_alignment._get_embeddings_api_dynamic 决策正确 (契约测试锁); test_25_audit fixture 改 mock _eng.embed_texts 是真修复。必修 CF-4 (high): 把 test_strategic_diff_embedding.py 纳入测试同步清单并明确 strategic_diff._LOCAL_EMBEDDING_MODEL/_embedding_config_uses_local 死全局是删是留 (与测试改动一致), 否则全量 sweep 'no new failure' 验收会红。 |

## 附: 8 验证 agent 原始裁决

| agent scope | verdict |
|---|---|
| 集群 A-guards (W1 batch_size 版本纪律 + W3 PEER_PROMPT frozen-hash + §5 CACH | minor_fixes |
| 集群 B-valcache (W4 验证缓存隔离 _llm_cache_validation.db) — spec 行 338-494。逐字 | minor_fixes |
| 集群 C-skip (W5 通用 --skip-unchanged + W6 StageSpec inputs/fingerprint_co | major_fixes |
| 集群 D-localmodel (W7 SBERT 复用穿透缓存 + W8 BERT 推理缓存), spec 文件 scripts/audi | major_fixes |
| 集群 E-withinstage 验证: W9 (MinHash 签名持久化 sidecar, dedup.py + dedup_thres | minor_fixes |
| 集群 F-cleanup (W11 Stata run_do 内容寻址跳过 / W12 HF 离线守卫+stage15 走引擎 / W13  | major_fixes |
| 横切【golden 安全性对抗审】跨全部 13 工作项 (W1/W3/§5/W4/W5/W6/W7/W8/W9/W10/W11/W12/W1 | minor_fixes |
| 横切【完整性对抗审】跨全部 13 个工作项 — 主攻 missed (遗漏的必改文件/callsite/测试/边界) + diff_issu | major_fixes |
