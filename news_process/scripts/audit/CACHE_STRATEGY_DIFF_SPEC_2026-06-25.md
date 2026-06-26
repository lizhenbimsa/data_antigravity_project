# 全项目缓存策略 — diff 级实现规格 (CACHE_STRATEGY_DIFF_SPEC_2026-06-25)

> 配套 `CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md` (上层计划)。本文件是 13 个工作项的
> **逐文件 before→after 伪 diff 规格**, 供审阅; 审过后再写代码。
> 来源 = Workflow `wf_e224e9b5-921` (6 集群 grounded 规格 + 1 跨集群对账)。
> 用户决策 (2026-06-25): 全 13 项 · 先细化到 diff 级 · needs-regen 攒到 DEFERRED golden 窗口。
>
> 🟥 **本文件 (v1) 已被 `CACHE_STRATEGY_SPEC_V2_2026-06-25.md` 取代; 实现请只读 v2。** 本文件保留作出处/审计轨迹。
>
> ⛔ **本规格已经过对抗式验证 (9-agent), 见 `CACHE_STRATEGY_VERIFICATION_2026-06-25.md`。**
> 凡本文字面伪 diff 与验证报告 CF-* 修正冲突, **一律以 CF-* 修正为准**。已知"字面代码块是错版、
> 正确版藏散文"的系统性陷阱: **W3 frozen-hash 须 EOL 归一 (CF-5) / W9 须 bytes 序列化非 list (CF-9)
> / W10 须 `'word': r['token']` 非 `''` (CF-6)** —— 实现者**禁止逐字照抄这三处字面块**。
> **W5 裁决 = needs-rework (2 个 blocker: CF-1 config 子树域名错 + CF-2 默认 Namespace 漏属性),
> 重做并通过复审前不得实现。** 其余 12 项 = go-with-fixes (逐项必修见验证报告 §13)。

**集群→工作项映射**: A=W1/W3/§5 · B=W4 · C=W5/W6 · D=W7/W8 · E=W9/W10 · F=W11/W12/W13

---

## 目录
- [§A 跨集群对账结论 (先读)](#a-跨集群对账结论-先读)
- [集群 A-guards](#集群-a-guards)
- [集群 B-valcache](#集群-b-valcache)
- [集群 C-skip](#集群-c-skip)
- [集群 D-localmodel](#集群-d-localmodel)
- [集群 E-withinstage](#集群-e-withinstage)
- [集群 F-cleanup](#集群-f-cleanup)

---

## §A 跨集群对账结论 (先读)

> 这是 reconcile agent 对 6 集群规格的交叉审查: 文件冲突 / 共享 helper / 工作项重叠 / 弱规格 / 推荐顺序。

### A.1 文件改动冲突 (同文件多集群改)

| 文件 | 涉及集群 | 是否真冲突 | 处理 |
|---|---|---|---|
| `config/features.yaml` | W1 (集群A, line 35-41 batch_size/text_pipeline_version 注释) vs W7 (集群D, line 31-41 embedding_robustness.model/revision — 但 W7 实际只 Read 不改 features.yaml, 它改 article_sbert.py 引用 _resolve_sbert_model(CONFIG)) | 不冲突。已 Read features.yaml: W1 改的是 embedding_robustness.batch_size(L39)+text_pipeline_version(L41) 的注释块; W7 不写 features.yaml(只通过 article_sbert._resolve_sbert_model 读 rob.model/rob.revision, features.yaml 无 revision 字段, W7 在 article_sbert.py 侧合成命名空间)。两者读同一 yaml 块但 W1 唯一写者。 | W1 先落地(注释+单测), W7 后落地。⚠ 唯一需对账: W1 单测 test_t2v_batch_version_lock 断言 text_pipeline_version=='v2-2026-05-29-t2v'(不 bump); 而 W7 把该值经 article_sbert._SBERT_VERSION_NS 拼 revision 进 SBERT 缓存命名空间——W7 不改 features.yaml 的 t2v 值本身, 故 W1 单测仍绿。但若审阅采纳 W1 的'立即为 32→128 补 bump 到 -t2v2'(needs-regen 分支), 则 W1/W7 须同批重生(W7 本就 needs-regen)。 |
| `config/paths.yaml` | W4 (集群B, filenames 块尾加 output_llm_cache_validation + output_llm_cache) vs W8 (集群D, paths 块加 local_model_cache_db) | 不冲突。已 Read paths.yaml: W4 在 filenames 块(L64-83, 当前末条 output_27_benefit_cache L83)后追加两键; W8 在 paths 块(L5-58)加 local_model_cache_db(逻辑上属 paths 而非 filenames)。两块物理分离, 追加点不重叠。 | 可同 PR。建议统一放置纪律: W4 的 output_llm_cache_validation/output_llm_cache 是文件名(归 filenames 块, 不带 ./); W8 的 local_model_cache_db 带 ./ 前缀(归 paths 块, 会被 _resolve_paths_in_place join)。⚠ W8 spec 写的 default 'output_dir/_local_model_cache.db' 与 W4 的 _llm_cache_validation.db 命名族一致, 三个 db 文件名互异(_llm_cache.db / _llm_cache_validation.db / _local_model_cache.db), 无碰撞。 |
| `core/dag.py` | W6 (集群C, StageSpec 加 inputs/fingerprint_cols 字段 L129-154 + 各 StageSpec 实例填 inputs) vs W5 (集群C, 文件末尾加 STAGE_CONFIG_DOMAINS 映射) | 同集群内, 不冲突——W6 是 W5 的前置基建, 设计上协同。已 Read dag.py: StageSpec L129-154(dataclass), L154 enabled_when 是当前末字段; W6 在其后追加 inputs/fingerprint_cols tuple 默认空, 向后兼容 test_dag_consistency(只校验 enabled_when)。 | W6 必须先于 W5。⚠ 锚点修正: W5 spec 说 STAGE_CONFIG_DOMAINS 的域名取自 _SPLIT_DOMAINS——已 Read core/config.py:24-27, _SPLIT_DOMAINS=('paths','preprocessing','filtering','sentiment','features','panel','validation') 确实存在且正是 7 域, W5 应 import 复用而非硬编码字符串。⚠ W5 spec 提'Mapping 已在 dag.py 顶部 import'——已 Read dag.py:24 只 import (Any, Callable, Optional), 无 Mapping, 须补 from typing import Mapping(W5 spec 已自标此修正提示, 正确)。 |
| `pipeline/features/strategic_diff.py + benefit_society.py + network_spillover.py` | W12 (集群F, 顶部 import os 后加 HF offline setdefault) vs W13 (集群F, 删 _encode_embeddings_local/_get_embeddings_api/_embedding_config_uses_local/_LOCAL_EMBEDDING_MODEL) | 不冲突(同集群)。W12 改顶部 import 区(strategic_diff:178/benefit_society:70/network_spillover:57), W13 删函数体(strategic_diff:295-303/658-806, benefit_society:235-263/284-417, network_spillover:1432-1610)。改动行不重叠。已 grep 实证三文件死函数行号全部属实。 | 同 PR 可行。但 W12 开放问题建议'引擎单点设 HF offline'(embedding_engine.py 顶部一处)——若采纳, 则 W12 在这三文件的 setdefault 全部取消, 仅留 embedding_engine.py + fintech_intensity.py(lazy-import 引擎不覆盖)两处, 与 W13 完全无交集。推荐采纳引擎单点方案。 |
| `tests/test_25_audit.py + test_benefit_society_embedding.py + test_network_spillover_embedding.py` | W13 改这三测试(删对已删符号 _get_embeddings_api/_LOCAL_EMBEDDING_MODEL 的 monkeypatch, 改 mock _eng.embed_texts) vs W7 改 test_omni_fix_embed.py | 不冲突。W13 改 3 个嵌入测试文件以适配死代码删除; W7 改 test_omni_fix_embed.py(不同文件)。test_25_audit.py 同时被 W13(改 _mock_embedding_api fixture)触及, 无其他集群改它。 | W13 必须与其 production 删除同 PR(否则测试引用已删符号即 collect error)。W7/W13 测试文件不交集, 可并行。 |
| `pipeline/sentiment/tone_words.py` | W10 (集群E, 重构 _compute_sentiment_with_rules→_scan_sentiment_trace+_reduce_trace, 改 L598-779 本体 + L1392/1407 消费侧) | 单集群独占, 无跨集群冲突。已 grep 实证 L598/1392/1407/1434/1509/1526 全部属实(4 处保留调用 + 1 主 + 1 ablation 循环)。 | 无冲突。但 W10 是 needs-regen, 须与 v3.11.1 既有 DEFERRED 批(_allv/inject-fintech/rule-ablation)统一重生; 字节等价是硬约束(测试用 == 非 approx)。 |
| `pipeline/panel/llm_peer_iv.py` | W3 (集群A, PEER_PROMPT_VERSION L339 后加 PEER_PROMPT_SHA256 锚常量) | 单集群独占。anchor L322(PEER_PROMPT)/L339(PEER_PROMPT_VERSION) 与 §5 doc 引用一致(未逐字 Re-Read llm_peer_iv 但 W3 spec 已自标注锚点确认, 且 caching.py docstring L71-72 旁证 PEER_PROMPT_VERSION 机制存在)。 | 无冲突。safe。 |

### A.2 工作项功能重叠

| 工作项 | 重叠 | 处理 |
|---|---|---|
| W5 (通用 --skip-unchanged 整阶段跳过) ↔ W8 (BERT 推理缓存) | 功能重叠确凿。W5 命中时'stage 23 整体在上游 22_words_tone.parquet 未变即根本不重跑'→ W8 的跨-run 命中边际收益主要降为单 stage 调试/部分重跑。W8 spec 自己已识别此重叠并给出降级建议。 | 采纳 W8 spec 的自降级方案: 若 W5 落地, W8 降级为可选(config inference_cache: false 默认关, 仅手动 python 23_tone_berts.py 反复迭代时开)。理由: ① W5 已拦截全量重跑; ② BERT forward 是本地 GPU $0, 缓存省时间非省钱, 优先级低于 LLM/嵌入缓存。但保留 W8 的键设计+round4 离散契约(单 stage 调试 297s→秒级开发体验)。实现顺序: W6→W5 先, W8 看 W5 落地后再决定默认值。 |
| W5 (通用 skip) ↔ W9 (MinHash 签名持久化) | 覆盖层级不同, 弱重叠。W5 作用于 stage 级(产物 parquet 全在+config子树+上游 input_hashes 不变即跳过整 stage); W9 作用于 stage 内(stage 62 dedup_threshold 跨 run 复用 MinHash 签名, 多阈值共用一次签名)。W9 唯一复用点是 validation/dedup_threshold.py:383(stage 62), 而 stage 62 是 validation 阶段——W5 spec 自承'validation/no-output stage → _get_stage_output_files 返回 [] → 第①步 not outputs 即 False, 总是重跑'。 | 无真重叠: W5 对 stage 62 这类无注册 parquet 产物的 validation stage 保守不跳(永远重跑), 故 W9 的 stage 内签名缓存仍有完整价值(每次跑 stage 62 都省 MinHash 重算)。两者正交可共存。W9 是 safe(签名确定→命中=逐位等价), W5 是 safe。 |
| W1 (batch_size 入 t2v 版本纪律) ↔ W7 (SBERT 复用 _encode_local_cached) ↔ §5 治理规范 | 三者共享 'text_pipeline_version 是 FP 敏感超参版本门' 的同一哲学。W1 把 batch_size 绑 features.yaml::embedding_robustness.text_pipeline_version; W7 把 SBERT revision 拼进 article_sbert._SBERT_VERSION_NS(独立命名空间, 非 features.yaml 的 t2v 值); §5 doc(铁律 C)把 batch_size/device/dtype/torch 统一登记为版本维度。 | §5 doc 是 W1/W3 的成稿单一事实源, 三者一致即可。⚠ 须确保 §5 doc 表格里 'text_pipeline_version(t2v 轨)' 行的 bump 触发条件含 batch_size(W1)、且 article_sbert 的 _SBERT_VERSION_NS 也被 §5 doc 收录为'本地深度模型推理'范例。W7 的 SBERT 命名空间独立于 features.yaml t2v——§5 doc 应澄清这点避免误以为 SBERT 缓存键随 features.yaml::embedding_robustness.text_pipeline_version 变。 |
| W4 (验证缓存隔离 _llm_cache_validation.db) ↔ §5/W8 (缓存库分治) | 缓存库分治哲学一致但不重叠。W4 把验证阶段 LLM 请求隔离到 _llm_cache_validation.db; W8 把 BERT 推理隔离到 _local_model_cache.db; §5 doc 建议本地深度模型用独立 _local_model_cache.db 复用 LLMCache 类。三个 db 各司其职。 | 统一接口: 三库均复用 core/caching.py::LLMCache 类(不重写)+同款 5 条键纪律。§5 doc 的'统一接口取舍'段应同时列出 _llm_cache_validation.db(W4)与 _local_model_cache.db(W8)两个分治范例。命名: 生产=_llm_cache.db / 验证=_llm_cache_validation.db / 本地模型=_local_model_cache.db, 互异无碰撞。 |
| W11 (Stata run_do 内容寻址跳过) ↔ W5 (通用 skip) | 同'内容寻址跳过'范式, 但层级完全不同(Stata .do 编排层 vs Python stage 层), 无功能重叠。 | 正交。但共享 helper 应统一: 两者都自造了内容寻址 hash(W5 _config_subtree_hash 复用 compute_config_hash; W11 _compute_rundo_key 自建 hashlib.sha256(json.dumps(sort_keys)))。建议 W11 也复用 core/data_versioning.py::compute_config_hash(对 payload dict)与 compute_file_hash(对 .do/.dta), 与 W5/W9 同源, 避免各造轮子(见 shared_helpers)。 |

### A.3 应统一的共享 helper

| helper | 定义处 | 使用方 | 建议 |
|---|---|---|---|
| `compute_config_hash / compute_file_hash (内容寻址 sha256)` | core/data_versioning.py:67 (compute_config_hash) / :58 (compute_file_hash) — 已 Read 实证, 是项目既有内容寻址单一事实源(json.dumps(sort_keys=True)+sha256 / 8192 块读文件 sha256) | W5 (_config_subtree_hash 复用 compute_config_hash; input_hashes 比对复用 compute_file_hash), W9 (_minhash_cache_key 复用 compute_config_hash 包 payload + datasketch 版本入键), W11 (_compute_rundo_key 当前自建 hashlib.sha256(json.dumps) — 应改复用 compute_config_hash; .do/.dta 指纹应复用 compute_file_hash) | 强制三集群统一复用 core/data_versioning.py 的两个 helper, 禁止各造 sha256 轮子。W5 spec 已正确复用; W9 spec 已复用 compute_config_hash; ⚠ W11 spec 自建 hashlib.sha256+json.dumps(等价但重复)——建议改为 from news_process.core.data_versioning import compute_config_hash/compute_file_hash, 保持全项目内容寻址同源、同 default=str 兜底行为。 |
| `LLMCache 类 + make_key 静态方法 (sqlite 穿透缓存 + 键算法)` | core/caching.py:141 (SCHEMA_VERSION='v1') / :277 (make_key 公开) / :264-271 (_make_key raw 格式 SCHEMA\|len:model\|len:prompt\|len:pv\|temp[\|seed]) — 已 Read 实证 | W4 (验证库直接 LLMCache(_val_cache_fn) 复用类), W7 (SBERT 走 _encode_local_cached 复用同库 _llm_cache.db), W8 (BERT 缓存 _bert_cache_key 复用 LLMCache.make_key, model_id 槽塞复合身份串, 独立 _local_model_cache.db), §5 doc(铁律 A 首字段=SCHEMA_VERSION + 统一接口段) | W8 把复合身份串(short_name\|max_length\|vocab_fp\|det_mode\|amp\|ckpt_fp)塞进 make_key 的 model_id 槽是合规复用(make_key 已被 strategic_diff:754/benefit_society:365/embedding_engine:474 同样当通用 KV 键用, 已 grep 实证)。但 W8 spec 伪代码第一段含占位噪声(if False)——正式实现须删, 以'聚合产出处 get-override+put'最小化写法为准。所有新缓存键首字段经 LLMCache 即自动含 SCHEMA_VERSION(满足§5铁律A), 自建键算法者(W9/W11)须显式拼 SCHEMA_VERSION 或改走 compute_config_hash(后者无 SCHEMA_VERSION 首段——W9/W11 是文件/Stata 缓存, 与 LLM SCHEMA_VERSION 无关, 各自带版本门 datasketch_version/_RUNDO_SKIP_VERSION 即可, 不强求 SCHEMA_VERSION)。 |
| `_SPLIT_DOMAINS (7 域配置子树定义)` | core/config.py:24-27 — 已 Read 实证 ('paths','preprocessing','filtering','sentiment','features','panel','validation') | W5 (STAGE_CONFIG_DOMAINS 的域名集 + _config_subtree_hash 切子树) | W5 的 STAGE_CONFIG_DOMAINS 应 from news_process.core.config import _SPLIT_DOMAINS 校验其值域(每 stage 绑定的域名 ⊆ _SPLIT_DOMAINS), 单测断言之, 防写错域名(如 'feature' typo 漏 s)。W5 spec 已提'域名取 _SPLIT_DOMAINS', 落地须真 import 而非硬编码注释。 |
| `_encode_local_cached 穿透缓存 (含 dict.fromkeys 去重防 GPU 1-ULP)` | pipeline/text/embedding_engine.py:580-645 — 已 Read 实证, dict.fromkeys(missing_chunks) 去重在 L627 | W7 (SBERT encode_articles 走 embed_texts→_encode_local_cached, 去重已内置), W12 (stage15 走 _eng.encode_local, 但 encode_local 是无缓存裸路径, 非 _encode_local_cached) | ⚠ 区分两个引擎入口: _encode_local_cached(L580, 带 LLMCache 穿透+去重) vs encode_local(L259, 无缓存裸 forward)。W7 走前者(SBERT 要缓存); W12 stage15 走后者(关键词权重一次性算, 不入 _llm_cache.db, 与原裸 model.encode 行为一致)。两者不可混用——W7 spec 正确(经 embed_texts→_encode_local_cached); W12 spec 正确(encode_local 不带 cache)。 |

### A.4 缺失/弱规格 (锚点存疑或需补)

| 工作项 | 问题 | 修法 |
|---|---|---|
| W3 (PEER_PROMPT frozen-hash) | 规格未对 llm_peer_iv.py:322/339 做实际 Read 核实(spec 自标'锚点确认'但本次对账未独立 Re-Read 该文件)。caching.py docstring L71-72 旁证 PEER_PROMPT_VERSION 机制存在, 但 PEER_PROMPT 起止行 322-335、含 {{"peers": []}} 转义、占位符 {year}/{bank_name}/{numbered_sentences} 等细节未逐字验证。 | 落地前必须 Read pipeline/panel/llm_peer_iv.py:320-370 核实 PEER_PROMPT 正文行号、占位符名(spec 假设 {numbered_sentences}, 须确认是否真名)、.format callsite(spec 说 L367)。frozen-hash 测试的 EOL 归一(.replace('\r\n','\n'))是正确防御, 务必采纳(Windows CRLF 仓库)。 |
| W5(3) (producer 写 config_subtree_hash) | spec 自标'须先 Read generate_golden_snapshot.py 与 test_panel_reproducibility 确认 golden 不含 schema metadata 才标 safe'。本对账已 Read test_panel_reproducibility.py:44-47——_column_hash 仅 hash_pandas_object(data 列), 不碰 schema metadata; 且 data_version 经 save_parquet_with_metadata:180 写为 schema metadata b'data_version' blob(非数据列)。 | 结论: W5(3) 给 data_version JSON 加 config_subtree_hash 键是 golden-safe(数据列哈希不变)。spec 的保守裁决'不确定先不做(3), 走整 config_hash 回退'仍可作为更稳选项, 但本对账已证(3)可安全做。建议: 若要精准子树失效就做(3)且标 safe; 否则 W5 仅靠 整config_hash回退+input_hashes 上线, 也 safe。无论哪种均不触发 needs-regen。 |
| W9 (MinHash sidecar uint64 序列化) | spec 主体用 list[int] 落 parquet, 但自承开放问题: MinHash.hashvalues 是 uint64, 经 parquet int64 往返, >2^63 的值会变负(符号回绕)→ 重建 MinHash 错误。 | 落地必须采用 spec 风险段提的 bytes 版: m.hashvalues.astype('<u8').tobytes() 存 binary 列, 读回 np.frombuffer(b, dtype='<u8')。list[int] 版仅作可读骨架, 禁止直接落地(会破坏签名正确性→破坏 dedup 阈值敏感性, 虽是 validation 旁路但仍是 bug)。单测须覆盖 hashvalues 含 >2^63 值的往返逐位等价。 |
| W10 (matched_words['word'] 字段) | spec 最小内存版把 sentiment_details 的 word 字段置 '', 改变 JSON 输出。spec 自标这是'唯一可能破坏字节等价的设计点'。 | 落地必须采用 spec 默认的'保留 token'方案: _scan_sentiment_trace 中间表加 'token': token 字段, 包装层 'word': r['token']。须先确认 sentiment_details 列是否入 golden/下游是否读 word——已 grep: _analyze_single_article 下游(top_detail 按 abs(final) 排序 / msent 看 base 符号)不读 word, 但 sentiment_details JSON 列若落 panel 则 word 值变即破字节等价。保守落地=保留 token, 零行为变更。 |
| W6 (各 StageSpec 实例 inputs 填值) | spec 给的 inputs 链式声明是'示范性'(stage40 inputs 须以 producer 真实 save_dataset(input_files=...)闭包为准, 非 DAG 直觉)。spec 自标 R5 风险: stage40 producer 记 output_24_herd_decay+output_15_article_alignment(文件名 16_article_alignment.parquet, 逻辑键 16_article_policy_alignment.py), 填 inputs 须精确对齐 basename 否则 input_hashes 比对失配。 | 落地填 inputs 前, 对每个要纳入通用 skip 的 stage, Read 其 producer 的 save_*(input_files=...) 实参, 用 basename 反查 OUTPUT_REGISTRY 逻辑键。填错只导致保守不跳(safe, 丧失增量), 不会误跳。建议首批只填确定的线性链(11→12→13→14, 51←40), 多源 fan-in(15/40)谨慎或暂留空。 |
| W11 (_stata_version_fingerprint 用 exe stat 非真版本) | spec 用 exe 文件 size+mtime+basename 当 Stata 版本指纹(妥协避免启 GUI 子系统弹框)。git checkout/重装 Stata 改 mtime→误失效(保守安全但可能频繁失效)。 | 可接受(spec 自标妥协合理, 符合 CLAUDE.md '禁启 GUI 探版本'铁律)。⚠ 但 W11 的 _compute_rundo_key 应改复用 core/data_versioning.compute_config_hash/compute_file_hash(见 shared_helpers), 而非自建 hashlib。sidecar 路径(.do 同目录 vs output_dir/_rundo_cache/)是唯一须审阅拍板的开放点——推荐 output_dir/_rundo_cache/ 避免污染 stata_templates 源树+免改 .gitignore。 |

### A.5 推荐实现顺序

- **批1 — 纯文档+注释+单测 (零代码行为变更, 最先, 解锁后续引用)** — W1(batch_size 版本纪律注释+单测, 不 bump version) · §5(docs/CACHE_VERSIONING_DISCIPLINE.md + caching.py docstring 追加) · W3(PEER_PROMPT frozen-hash 常量+单测, 须先 Read llm_peer_iv.py 核实锚点)
  - 理由: 全 safe、不触缓存/golden、互不依赖。§5 doc 是 W1/W3 的单一事实源, 应同批确保三者措辞一致。W1/W3 单测落 pytest -m fast 域(纯 config/字符串读取)。先落地建立版本门治理基线, 供 W4/W7/W8 引用。
- **批2 — safe 基建 (DAG 字段 + 验证库隔离 + Stata/MinHash 内容寻址)** — W6(StageSpec 加 inputs/fingerprint_cols, 向后兼容默认空) → W5(--skip-unchanged, 依赖 W6; (3) producer 写子树 hash 可选, 已证 safe) · W4(验证缓存隔离 _llm_cache_validation.db) · W9(MinHash sidecar, 须用 bytes 版序列化) · W11(Stata run_do 跳过, 改复用 compute_config_hash/compute_file_hash)
  - 理由: 全 safe(W6/W5 父进程只读元数据+默认 flag 关; W4 只换 sqlite 路径不改键算法; W9 签名确定; W11 编排层不进 panel)。W6 必须先于 W5。这批共享 core/data_versioning 的 compute_config_hash/compute_file_hash, 同批落地便于统一复用。互不依赖可并行(除 W6→W5)。
- **批3 — safe 清理 + HF 离线 (含 W12/W13 同文件协同)** — W12(HF offline setdefault + stage15 走 _eng.encode_local; 推荐引擎单点方案) + W13(删 3 文件 legacy 死函数 + 同步 3 测试) 同 PR
  - 理由: W12/W13 在 strategic_diff/benefit_society/network_spillover 三文件有交集但改动行不重叠(import 区 vs 函数体), 已 grep 实证死函数行号。同 PR 避免 W13 删函数后 W12 二次改同文件的 churn。W13 删除必与测试改同 PR(否则 collect error)。全 safe。采纳 W12 引擎单点 HF offline 则与 W13 完全无交集。
- **批4 — needs-regen, 攒 DEFERRED 统一受控重生 (最后)** — W7(SBERT 复用穿透缓存, 归一化舍入漂移→needs-regen) · W10(词典 powerset 单次扫描重构, 字节等价硬约束→并入 v3.11.1 既有 DEFERRED) · W8(BERT 推理缓存; 若 W5 已落地则降级 inference_cache 默认 false, 仅保留键设计)
  - 理由: W7/W10 是 needs-regen, 须与 CLAUDE.md 顶部既有 DEFERRED 批(_allv/inject-fintech/rule-ablation/media-canon)一次合并受控重生(PYTHONHASHSEED=0+全BLAS=1+保留GPU+HF offline), 避免本机裸环境误 bless 无关漂移列。W8 与 W5 功能重叠→W5 落地后 W8 降级为可选(默认关), 此时 W8 实质 safe(不开缓存不改产物); 仅当单 stage 调试需要才开+受控播种。把所有需重生项攒到最后一次性消费。

### A.6 整体 golden 安全结论

整体结论: 13 项中 10 项 safe、3 项 needs-regen(W7/W8/W10), 与各集群自评一致, 本对账实证修正/确认如下。

【确属 needs-regen, 须并入既有 DEFERRED 批统一受控重生】
- W7 (SBERT 复用穿透缓存): 真正根因是归一化舍入路径变(历史 SentenceTransformer.encode(normalize_embeddings=True) 在 fp32 张量内归一 vs W7 在 numpy fp64 归一)→ 可能 1e-7 漂移 → semantic_staleness_* 余弦微变。首跑冻结新值后离线复现。确属 needs-regen, spec 判定正确。
- W10 (词典 powerset 单次扫描重构): 引擎确定性→若 _scan/_reduce 浮点乘序严格对齐旧码(spec 已逐步对齐: -base==base*-1.0 / deg_mult / ADVERSATIVE_BOOST 同序), 理论字节等价; 但须真机 == 测试确认。并入 v3.11.1 既有 rule-ablation DEFERRED 一次合并, 重生 golden-safe。⚠ matched_words word 字段须采'保留 token'方案以零行为变更。
- W8 (BERT 推理缓存): argmax+round4 离散值吸收 fp 漂移→冻结首跑值比每 run 重抖更稳, 与 stage21 LLM 缓存同哲学。但因冻结边界 argmax 故标 needs-regen。⚠ 若 W5 通用 skip 落地, W8 应降级默认关(此时不改产物=safe)。

【实证确认为 safe(本对账新增证据)】
- W5(3) producer 写 config_subtree_hash: 已 Read test_panel_reproducibility.py:44-47, golden 仅 hash_pandas_object(数据列), 不读 schema metadata; data_version 经 save_parquet_with_metadata:180 写为 schema metadata blob(非数据列)。故给 data_version JSON 加键 = 数据列哈希不变 = golden-safe。W5(3) 可安全做(精准子树失效), 也可保守不做(走整 config_hash 回退, 仍 safe)。
- W4: 已 Read paths.yaml, 仅在 filenames 块追加文件名键 + 两验证阶段换 sqlite 路径, 不改 core/caching.py 键算法、不触生产 _llm_cache.db、不重跑 stage21 → golden 不受影响。
- W12: HF offline 只切换'从 hf.co 解析 revision'→'读本地快照', 权重/输出逐位不变(已有 tone_berts:133/article_sbert:93 落地先例 + memory perf-audit 真机字节级实证背书); stage15 走 encode_local(无缓存裸路径, 不入 _llm_cache.db, 与旧裸 model.encode 在短关键词无分块时逐位一致, engine:289-294 直送分支保证)。
- W13: 删的全是 grep 实证'生产 0 调用'的 legacy 函数(benefit_society:245/284, strategic_diff:300/658, network_spillover:1445/1466), 活跃路径(全走 _eng.embed_texts)不动 → safe。
- W1/W3/§5/W6/W9/W11: 纯注释/文档/单测/DAG 默认空字段/确定性签名缓存/Stata 编排层, 均不触 golden。

【唯一 golden 升级触发点】W1 若审阅采纳'立即为已发生的 batch_size 32→128 补 bump text_pipeline_version 到 -t2v2', 则全部 _t2v 缓存 silent miss → 升级 needs-regen, 须并入 DEFERRED 批。本对账建议: W1 默认只落注释+单测(version 保持 v2-2026-05-29-t2v 不动), 该 bump 决策与 W7/W10/W8 统一消费时一并定夺。

【DEFERRED 批统一消费清单】W7 + W10 + (W8 若开缓存) + (W1 若补 bump) 与 CLAUDE.md 顶部既有 _allv/inject-fintech/rule-ablation/media-weights-canon 一次性合并受控重生(PYTHONHASHSEED=0 + MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1 + 保留 GPU + HF_HUB_OFFLINE=1/TRANSFORMERS_OFFLINE=1), 避免裸环境误 bless 3 个 BLAS-FP 网络列(bank_clustering/cfbetween/harmonic)等无关漂移。

---

<a id="集群-a-guards"></a>

## 集群 A-guards — W1 (batch_size 纳入 t2v 版本纪律) + W3 (PEER_PROMPT frozen-hash 护栏) + §5 缓存版本门治理规范

### W1 · batch_size 纳入 text2vec 版本纪律 (注释硬约定 + 单测)
- **目标**: 让 `config/features.yaml::embedding_robustness.batch_size` 与 `text_pipeline_version` 绑定 — 改 batch_size/device/dtype/torch 版本必同 diff bump version token, 防 FP 漂移静默污染 `_t2v` 缓存。
- **golden 影响**: safe (纯注释 + 新单测, 不改键、不立即失效任何缓存; 不触 `_llm_cache.db`)。
- **逐文件改动**:
  - `config/features.yaml:35-41` — **锚点(当前真实代码)**:
    ```yaml
      # 本地 CPU 编码批大小 (2026-06-23: 32→128)。更大批 → 更少 GEMM 调用 + 更好 CPU
      # cache 局部性, t2v 块约 1.5~2x 提速。⚠ batch_size 改变会让 batched matmul 的 FP
      # 舍入路径变 → _t2v 列可能出现 ~1e-7 级漂移 (与既有 BLAS-FP 非确定性同量级, 语义
      # 不变); 跑 golden 复现门时如标记 _t2v 列须受控环境重生 (PYTHONHASHSEED=0 + BLAS=1)。
      batch_size: 128
      # 稳健轨独立 cache 命名空间 (model_id 已不同, 版本字符串再隔离一层)。
      text_pipeline_version: "v2-2026-05-29-t2v"
    ```
    ⚠锚点修正: 实际 `batch_size` 在 line 39, `text_pipeline_version` 在 line 41 (与测绘 :39/:41 一致)。
    **改为** (在 batch_size 注释块尾追加硬约定; version 注释加 bump 触发条件; 值不动):
    ```yaml
      # 本地 CPU 编码批大小 (2026-06-23: 32→128)。更大批 → 更少 GEMM 调用 + 更好 CPU
      # cache 局部性, t2v 块约 1.5~2x 提速。⚠ batch_size 改变会让 batched matmul 的 FP
      # 舍入路径变 → _t2v 列可能出现 ~1e-7 级漂移 (与既有 BLAS-FP 非确定性同量级, 语义
      # 不变); 跑 golden 复现门时如标记 _t2v 列须受控环境重生 (PYTHONHASHSEED=0 + BLAS=1)。
      # ★ 版本门铁律 (§5-C, FP 敏感超参当版本维度): batch_size 不进缓存键 (键只含
      #   model_id|chunk文本|text_pipeline_version), 故改 batch_size/device/dtype/torch
      #   版本而不 bump 下面的 text_pipeline_version → 旧 _t2v 缓存静默命中、新批舍入路径
      #   的值永不落盘 = silent staleness。⇒ 任何对 batch_size 的修改 **必须** 在同一 diff
      #   bump text_pipeline_version 末尾标号 (如 -t2v → -t2v2), 由 test_t2v_batch_version_lock
      #   单测强制对账。
      batch_size: 128
      # 稳健轨独立 cache 命名空间 (model_id 已不同, 版本字符串再隔离一层)。
      # ⚠ bump 触发条件: 改 model / 切片策略 / batch_size / device / dtype / torch 版本
      #   任一项, 必须同 diff 改这里的标号 (见上 batch_size 注释 §5-C)。
      text_pipeline_version: "v2-2026-05-29-t2v2"   # ← 示例: 因 batch_size 32→128 而 bump
    ```
    > 说明: version 当前盘上值为 `v2-2026-05-29-t2v` (2026-06-23 batch 已从 32→128 但 version **未** bump — 这正是 W1 要堵的历史漏网)。是否真把现值 bump 为 `-t2v2` 属 **needs-regen 决策** (会让既有 `_t2v` 缓存全 silent miss → 须受控重生)。**本工作项默认只落注释 + 单测 (safe)，version 字符串保持 `v2-2026-05-29-t2v` 不动**；上面 `-t2v2` 仅作"将来改 batch_size 时该怎么做"的示范，审阅者若决定立刻为已发生的 32→128 补 bump，则该项升级为 needs-regen 并入 DEFERRED 批。
  - `pipeline/text/embedding_engine.py:598-599` — **锚点(当前真实代码, `_encode_local_cached` 键构造)**:
    ```python
    model_id = spec_model(spec, 'shibing624/text2vec-base-chinese')
    version = spec_version(spec)
    ```
    其下 line 607 真实键查询为 `cache.get(model_id, c, prompt_version=version)`，line 641-645 `cache.put_batch(model_id, unique_texts, [...], prompt_version=version)` — **证实 batch_size 确实不进键, 键仅 `(model_id, chunk文本, text_pipeline_version)`**, W1 注释陈述属实。
    **改为** (在 `version = spec_version(spec)` 后加一行 inline 注释, 不改逻辑):
    ```python
    model_id = spec_model(spec, 'shibing624/text2vec-base-chinese')
    # ★ 版本门 §5-C: 键 = (model_id, chunk文本, version)，batch_size/device/dtype 不入键。
    #   故改 config/features.yaml::embedding_robustness.batch_size 必同步 bump
    #   text_pipeline_version (test_t2v_batch_version_lock 守护)，否则 FP 漂移静默污染。
    version = spec_version(spec)
    ```
- **新增测试**: `tests/test_t2v_batch_version_lock.py`
  - 断言要点 (纯 config 读取, 无 production data, 无 network):
    - `test_t2v_batch_and_version_lockstep`: `load_config()` 取 `cfg['embedding_robustness']`，断言 `batch_size == 128` **且** `text_pipeline_version == 'v2-2026-05-29-t2v'` 在**同一断言对**中 (二者任一被改而另一未改 → 测试失败 = 强制 reviewer 在同一 diff 处理两者)。文档串明确写"若你改了 batch_size 必须同 diff bump version 并更新本断言的两个期望值"。
    - `test_t2v_version_is_lintable_string`: 断言 `text_pipeline_version` 以 `v` 开头且含日期形 `-\d{4}-\d{2}-\d{2}` (与 `config/prompts/*.txt` 头同构, 防写成裸 `v2`)。
    - `test_t2v_batch_size_not_in_cache_key` (回归锁): 用 `tmp_path` 建 `LLMCache`，对同一 `(model_id, text, prompt_version)` 调 `get` — 证明 `_make_key` 签名里**没有** batch_size 维度 (即 batch_size 改了键不变), 把"batch_size 必须靠 version 绑定"这一前提钉死。
- **验收**: `pytest news_process/tests/test_t2v_batch_version_lock.py -v` 全绿; 手动把 `config/features.yaml` 的 `batch_size` 改成 `64` 不动 version → 跑测试应 **FAIL** (锁生效); 改回 128 → PASS。`ruff check news_process/tests/test_t2v_batch_version_lock.py` clean。
- **风险/开放问题**: ① 注释陈述"batch_size 改了键不变"是**真**的 (已 Read line 607/641 实证)，但需提醒 reviewer：`spec_version` 缺 key 时回退 `'v0'` (embedding_engine.py:218)，若 features.yaml 漏写 version 字段会静默落 `v0` 命名空间 — 单测 `test_t2v_version_is_lintable_string` 顺带拦此退步。② device/dtype 当前由 stage 内部决定 (memory: 本机 RTX3090 默认 cuda:0)，未在 config 暴露 — 注释把它们也列入"必 bump"清单是前瞻约定，非当前 config 可 lint 项。

---

### W3 · PEER_PROMPT / 内联 prompt 失效护栏 (frozen-hash 单测 + lint 扩展)
- **目标**: `PEER_PROMPT` 是模块内联常量 (最弱版本门形式), 改正文却忘 bump `PEER_PROMPT_VERSION` → 旧 LLMCache 静默命中。补 frozen-hash 单测 + 可选 lint 扩展, 强制正文改动同 diff bump 版本号。
- **golden 影响**: safe (新单测 + lint, 不改 PEER_PROMPT 正文、不改键; 不触缓存)。
- **逐文件改动**:
  - `pipeline/panel/llm_peer_iv.py:322-339` — **锚点(当前真实代码)**:
    ```python
    PEER_PROMPT = """你是一位中国银行业金融科技分析师。以下是 {year} 年媒体报道中
    同时提及【{bank_name}】和其他银行的句子。请基于这些报道，
    识别在金融科技领域与【{bank_name}】构成产品市场竞争关系的银行。
    ... (中略, 见上方 Read 全文 322-335) ...
    最多 10 家，按竞争强度排列。无法判断则 {{"peers": []}}。"""

    # Plan-r3 P3-17 接入: PEER_PROMPT 是模块内联常量 (不经 config/prompts/),
    # 任何对此字符串的修改必须同步 bump 此版本号, 让既有 LLMCache 自动失效.
    PEER_PROMPT_VERSION = "v1-2026-05-13"
    ```
    ⚠锚点确认: `PEER_PROMPT` 起 line 322、`PEER_PROMPT_VERSION` 在 line 339 (与测绘 :322/:339 完全一致)。
    **改为** (PEER_PROMPT 正文与版本号**不动**; 仅在 `PEER_PROMPT_VERSION` 行后追加 frozen-hash 锚常量 + 注释, 供单测引用):
    ```python
    # Plan-r3 P3-17 接入: PEER_PROMPT 是模块内联常量 (不经 config/prompts/),
    # 任何对此字符串的修改必须同步 bump 此版本号, 让既有 LLMCache 自动失效.
    PEER_PROMPT_VERSION = "v1-2026-05-13"

    # ★ 版本门 §5-D (内联常量是最弱版本门, 须配 frozen-hash 单测补强):
    #   下行哈希冻结 PEER_PROMPT 的精确字节。改 PEER_PROMPT 正文 (含空白/标点)
    #   → 哈希变 → test_peer_prompt_frozen_hash 失败, 强制本 diff 同时:
    #     (1) bump PEER_PROMPT_VERSION (让旧 _llm_cache.db 条目 silent miss);
    #     (2) 用 scripts/audit/print_peer_prompt_hash.py 重算并替换下值。
    #   生成方式 (PowerShell, 本机 conda base):
    #     python -c "import hashlib;from news_process.pipeline.panel.llm_peer_iv import PEER_PROMPT;print(hashlib.sha256(PEER_PROMPT.encode('utf-8')).hexdigest())"
    PEER_PROMPT_SHA256 = "<占位: 用上面命令生成 64 hex; 落地时由实现者填入真实哈希>"
    ```
    > 说明: 我无法在规格阶段算出真哈希 (会随 Read 时的 CRLF/LF 与字节呈现而异)，故留显式占位 + 一行可复制的生成命令。落地实现者**在真机仓库**跑该命令把输出粘进 `PEER_PROMPT_SHA256` (单测首跑会打印 actual 哈希辅助首次填值, 见下)。
  - `scripts/lint/check_prompt_headers.py:41-65` — **锚点(当前真实代码, 只扫 `config/prompts/*.txt`)**:
    ```python
    def check_prompts() -> int:
        root = _project_root()
        prompts_dir = os.path.join(root, "config", "prompts")
        ...
        for fname in sorted(os.listdir(prompts_dir)):
            if not fname.endswith(".txt"):
                continue
            ...
            m = _VERSION_HEADER.match(first)
    ```
    **(可选扩展, 推荐改走单测而非动这个 stdlib-only 脚本)**: 该脚本是 pre-commit `check-prompt-headers` 的 entry，`files: ^news_process/config/prompts/.*\.txt$` 只在 `.txt` 改动时触发，**天然管不到 `llm_peer_iv.py` 内联常量**。故 PEER_PROMPT 的护栏**不放进此脚本**(放进去会让它从"纯扫 txt 目录"变成"import pipeline 模块"，破坏其 stdlib-only/零依赖设计)，改由下方 pytest 单测承担 — 后者随每次 `pytest -m fast` 跑，覆盖范围更稳。本工作项**不改** check_prompt_headers.py 与 .pre-commit-config.yaml。
- **新增测试**: `tests/test_peer_prompt_frozen.py`
  - `test_peer_prompt_frozen_hash`: 
    ```python
    import hashlib
    from news_process.pipeline.panel.llm_peer_iv import PEER_PROMPT, PEER_PROMPT_SHA256
    actual = hashlib.sha256(PEER_PROMPT.encode("utf-8")).hexdigest()
    assert actual == PEER_PROMPT_SHA256, (
        f"PEER_PROMPT 正文已变 (actual={actual!r})。若是有意修改, 必须同 diff: "
        f"(1) bump llm_peer_iv.PEER_PROMPT_VERSION (现 'v1-2026-05-13') 让旧 _llm_cache.db silent miss; "
        f"(2) 把 PEER_PROMPT_SHA256 更新为 {actual!r}。见 §5-D 版本门纪律。"
    )
    ```
    断言要点: 失败信息直接吐出 actual 哈希 → 首次落地与每次有意改 prompt 都可一键复制。
  - `test_peer_prompt_version_is_lintable`: 断言 `PEER_PROMPT_VERSION` 形如 `v\d+-\d{4}-\d{2}-\d{2}` (防写成裸 `v2`)。
  - `test_peer_prompt_placeholders_intact` (语义回归): 断言 `PEER_PROMPT` 含 `{year}` / `{bank_name}` / `{numbered_sentences}` 三个占位符且 `.format(...)` 不抛 `KeyError` (防 frozen-hash 之外有人误删占位符破坏 `_call_llm_peer` line 367 的 `.format`)。
  - (可选) `tests/integration/test_prompt_version_wired.py` 扩展: 现有 `test_production_prompts_have_version_header` (line 127-143) 只覆盖 `config/prompts/unified_cot.txt`。可在同文件追加 `test_inline_peer_prompt_has_frozen_hash` 复用同一"内联 prompt 也要有版本门"叙事, 与 txt 头测试并列, 强化"两类 prompt 版本门都有 gate"的端到端证明。
- **验收**: 首次落地 — 删占位、跑 `pytest news_process/tests/test_peer_prompt_frozen.py::test_peer_prompt_frozen_hash -v`，从 FAIL 信息复制 actual 哈希填入 `PEER_PROMPT_SHA256`，再跑应 PASS。回归验证: 手动在 `PEER_PROMPT` 末尾加一个空格 → 跑测试应 **FAIL** 并提示 bump version; 撤销 → PASS。`ruff check` clean。
- **风险/开放问题**: ① `PEER_PROMPT` 含 `{{"peers": []}}` 转义花括号 — frozen-hash 对正文逐字节，转义层不影响哈希计算，但 reviewer 须知 `.format()` 后真实发往 API 的文本与 `PEER_PROMPT` 源串不同 (`{{` → `{`)；护栏冻结的是**源串**(决定 `.format` 输出 + 缓存键的 prompt 实参，二者同源故充分)。② 占位符填哈希是一次性人工步骤 — 若 reviewer 担心遗漏，可让单测在 `PEER_PROMPT_SHA256` 仍为占位串时 `pytest.skip("需先填入 frozen hash")` 而非 fail (避免 CI 卡在未填值)；推荐落地时直接填实哈希，不留 skip。③ CRLF/LF: 该文件在 Windows 仓库内若以 CRLF 存盘，`PEER_PROMPT` 三引号串内换行会是 `\r\n` → 哈希含 CR。须在**真机当前 checkout** 上生成哈希 (`.gitattributes` 未把 `.py` 标 binary，源文件保留 on-disk EOL)，并在注释注明"哈希含本机 EOL，跨 EOL checkout 须重算"——或更稳妥：测试内对 `PEER_PROMPT` 先做 `.replace("\r\n","\n")` 归一再哈希，消除 EOL 敏感性 (推荐, 注释里写明归一规则)。

---

### §5 治理规范 · 新增文档 `docs/CACHE_VERSIONING_DISCIPLINE.md`
- **目标**: 把现有 5 个版本门 (`SCHEMA_VERSION` / `prompt_version`×3 / `text_pipeline_version`×2 / `PREPROCESS_CODE_VERSION`) 的共性沉淀为单一事实源的 5 条铁律, 约束未来一切新缓存。
- **golden 影响**: safe (纯文档新增)。
- **逐文件改动**:
  - **新增 `docs/CACHE_VERSIONING_DISCIPLINE.md`** (置于仓库根 `docs/`，与 `docs/architecture.md`/`docs/audit/` 同级 — 已 Read 确认 `news_process/docs/` 不存在、文档统一在根 `docs/`)。成稿文案:
    ````markdown
    # 缓存版本门纪律 (Cache Versioning Discipline)

    > 单一事实源。本项目 golden 字节级可复现的根基是"内容寻址缓存 + 版本门"。
    > 任何**新增缓存**或**修改既有缓存语义**前必须通读本文 5 条铁律。
    > 配套强制机制见 `core/caching.py::LLMCache._make_key` 与各 `test_*_version_lock` 单测。

    ## 现有 5 类版本门 (盘点)
    | 版本门 | 位置 | 作用域 | bump 触发条件 |
    |---|---|---|---|
    | `SCHEMA_VERSION = "v1"` | `core/caching.py:141` | 全局核武级 — 进每个缓存键首字段 | 缓存键算法 / 响应格式约定层面变更 |
    | `prompt_version` (unified_cot) | `config/prompts/unified_cot.txt:1` `# version: v8-2026-05-17` | stage 21/33/34/36/39 LLM 投票 | 改 prompt 正文 (lint: check_prompt_headers) |
    | `PEER_PROMPT_VERSION = "v1-2026-05-13"` | `pipeline/panel/llm_peer_iv.py:339` | stage 48 peer 识别 (内联常量) | 改 `PEER_PROMPT` 正文 (gate: test_peer_prompt_frozen_hash) |
    | `text_pipeline_version` (API 轨) | `config/features.yaml:29` `v2-2026-05-29-api` | stage 15/16/27/network API 嵌入 | 改嵌入模型 / 文本预处理 / 切片策略 |
    | `text_pipeline_version` (t2v 轨) | `config/features.yaml:41` `v2-2026-05-29-t2v` | 本地 text2vec 稳健轨 `_t2v` 列 | 改 model / 切片 / **batch_size / device / dtype / torch 版本** (gate: test_t2v_batch_version_lock) |
    | `PREPROCESS_CODE_VERSION` | `pipeline/preprocess/runner.py` (内容寻址 key) | stage 00 全量预处理 | 改预处理逻辑 / MEDIA_NAME_OVERRIDES |

    ## 5 条铁律

    ### A — 首字段恒为 SCHEMA_VERSION
    每个新缓存键的**首字段**必须是 `core/caching.py::SCHEMA_VERSION` (沿用
    `LLMCache._make_key` 的 `f"{SCHEMA_VERSION}|..."` 模式)。这是全局核武级一键失效
    开关：当任何跨缓存的键算法/语义需要整体废弃时，bump `SCHEMA_VERSION` 即让全部
    历史缓存 silent miss。新缓存若复用 `LLMCache` 类即自动满足；自建键算法者必须显式
    把 `SCHEMA_VERSION` 拼为首段。

    ### B — 语义参数进键或绑 version token
    凡"改其值会改缓存命中后输出、但不在键内既有字段"的参数，二选一：
    (1) **进键** — 如 `temperature` 始终进键、`random_seed` 在 `temperature!=0` 时按需进键
        (`caching.py:259-263`)；或
    (2) **绑显式 version token** — 在 callsite + config 注释写死"改此参数必须 bump
        哪个 version"。
    严禁出现"改了它输出会变、但键不变、又没有绑定任何 version"的参数 = silent staleness。

    ### C — FP 敏感超参当版本维度对待
    `batch_size` / `device` (cpu↔cuda) / `dtype` (fp32↔fp16) / BLAS 或 torch 线程数 /
    `torch` 版本 — 这些**不改语义但改浮点舍入路径**的超参，必须当作版本维度：要么进键，
    要么绑定一个 `text_pipeline_version` 并在注释写死 bump 触发条件。
    > 历史教训: `embedding_robustness.batch_size` 2026-06-23 从 32→128 时 **未** bump
    > `text_pipeline_version` (唯一漏网者)，W1 治理已补注释 + `test_t2v_batch_version_lock`
    > 强制对账。本机 BLAS 线程必须外部 shell 钉死 (`MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1`)；
    > GPU 路径保留 (RTX3090, BLAS 钉死只影响 CPU)。受控重生环境另加 `PYTHONHASHSEED=0` + HF offline。

    ### D — version token 优先放可 lint 的位置
    版本号载体优先级 (强→弱):
    `config/prompts/*.txt` 首行 `# version:` (有 check_prompt_headers lint + pre-commit hook)
    > config yaml 字段 (`text_pipeline_version`, 可被 config 单测断言)
    > 模块内联常量 (`PEER_PROMPT_VERSION`)。
    内联常量是**最弱形式** (lint 扫不到，pre-commit 的 `files:` 过滤覆盖不到)，**必须**
    配 frozen-hash 单测补强 (`test_peer_prompt_frozen_hash` 冻结正文字节，改正文 → 哈希
    变 → 强制同 diff bump version)。新增内联 prompt 一律照此办理。

    ### E — 资源文件以内容 sha256 入键
    词典 / anchor 句 / `MEDIA_NAME_OVERRIDES` 等**外部资源文件**，其内容变更应以
    **文件内容 sha256 入缓存键** (内容寻址)，而非靠人工记得 bump 某个 version。
    范本: `pipeline/preprocess/runner.py::compute_preprocess_cache_key` 已对 noise/bank
    词典做内容寻址。开放待办: `MEDIA_NAME_OVERRIDES` 尚靠 `PREPROCESS_CODE_VERSION` 人工
    bump (W2)，应迁移为内容 sha256 入键。

    ## 统一接口取舍 (物理库分离, 逻辑接口统一)
    不要把 BERT/SBERT 全语料推理塞进同一个 `_llm_cache.db` (已 ~500MB)。建议本地深度
    模型推理用独立 `_local_model_cache.db`，但**复用 `LLMCache` 类 + 同款 5 条键纪律**
    (内容寻址哲学统一)。

    ## 落地清单 (新增任何缓存前自检)
    - [ ] 键首字段是 `SCHEMA_VERSION` (A)
    - [ ] 所有"改值即改输出"的参数进键或绑 version (B)
    - [ ] FP 敏感超参 (batch_size/device/dtype/线程/torch 版本) 当版本维度处理 (C)
    - [ ] version token 放在尽量可 lint 的位置；内联常量配 frozen-hash 单测 (D)
    - [ ] 资源文件内容 sha256 入键 (E)
    - [ ] 受控重生环境确认: PYTHONHASHSEED=0 + 全 BLAS 线程=1 + 保留 GPU + HF offline
    ````
  - `core/caching.py:73-77` — **锚点(当前真实模块 docstring 尾, 现有 bump 触发说明)**:
    ```python
    # - 修改 embedding 模型 / 文本预处理 / 切片策略时, 在 ``config/features.yaml::
    #   embedding_api.text_pipeline_version`` bump 版本号.

    SCHEMA_VERSION 保持 v1 (无需再 bump): 现有 LLMCache 中以 (v1, "v0", 0.0)
    为键的历史条目继续命中; 仅当 callsite 传入新版本号时才走新 namespace.
    ```
    **改为** (在该段后追加一行指向单一事实源, 不改既有文字):
    ```python
    # - 修改 embedding 模型 / 文本预处理 / 切片策略时, 在 ``config/features.yaml::
    #   embedding_api.text_pipeline_version`` bump 版本号.
    # - ★ 新增任何缓存 / 改既有缓存语义前, 须遵守 docs/CACHE_VERSIONING_DISCIPLINE.md
    #   的 5 条铁律 (A 首字段=SCHEMA_VERSION / B 语义参数进键或绑 version / C FP 敏感
    #   超参 batch_size·device·dtype·线程·torch版本当版本维度 / D version token 优先
    #   放可 lint 位置·内联常量配 frozen-hash 单测 / E 资源文件内容 sha256 入键)。

    SCHEMA_VERSION 保持 v1 (无需再 bump): 现有 LLMCache 中以 (v1, "v0", 0.0)
    为键的历史条目继续命中; 仅当 callsite 传入新版本号时才走新 namespace.
    ```
- **新增测试**: 可选 `tests/test_cache_versioning_doc.py::test_discipline_doc_exists` — 断言 `docs/CACHE_VERSIONING_DISCIPLINE.md` 存在且含 5 个铁律小节标题 (`### A`..`### E`)，防文档被误删/截断 (轻量 gate, 非必需)。
- **验收**: 文件存在性 + Markdown 渲染人工审；`grep -c "^### [A-E] " docs/CACHE_VERSIONING_DISCIPLINE.md` 返回 5；`core/caching.py` 改动后 `pytest news_process/tests/test_pipeline_robustness.py -k schema -v` 仍绿 (确认 docstring 追加未碰 `SCHEMA_VERSION == "v1"` 不变量)。
- **风险/开放问题**: ① 该 §5 文案已在 `scripts/audit/CACHE_STRATEGY_EXECUTION_PLAN_2026-06-25.md:253-271` 有初稿 — 本文档是其**成稿落地版**，两者须保持一致 (执行计划是 plan，本 md 是常驻规范)；建议在执行计划 §5 末尾加一行"已落地为 docs/CACHE_VERSIONING_DISCIPLINE.md"。② 文档引用的真实行号 (`caching.py:141`/`features.yaml:29,41`/`llm_peer_iv.py:339`) 均经本次 Read 核实属实，但行号会随未来编辑漂移 — 表格用"位置+常量名"双标定，弱化纯行号依赖。

---

**跨工作项一致性备注 (供集群对账)**: W1 与 W3 的新单测均落在 `pytest -m fast` 域 (纯 config/字符串读取, 无 production data / 无 network), 与现有 `tests/integration/test_prompt_version_wired.py` 的"prompt 版本门已通"叙事互补且不重叠 (后者测 txt 头解析, 本集群测 t2v batch 绑定 + PEER_PROMPT frozen-hash)。三项全 **safe**, 离线 `NEWS_PROCESS_LLM_OFFLINE=1` 下 $0、不触 `_llm_cache.db`、不触 golden。唯一潜在 needs-regen 升级点是 W1 中"是否立即为已发生的 batch_size 32→128 补 bump version" — 该决策若被采纳须并入现有 DEFERRED 受控重生批 (与 `_allv`/inject-fintech/media-canon 统一消费)。

---

<a id="集群-b-valcache"></a>

I now have all anchors verified against real code. Producing the spec.

```
## 集群 B-valcache — W4 验证缓存隔离 (生产 _llm_cache.db 与两验证阶段增量写入隔离)
### W4 · 两验证阶段 LLMCache 指向独立 _llm_cache_validation.db
- **目标**: prompt_sensitivity / entity_masking 的变体/掩码 prompt 增量条目写入独立验证库, 不污染生产 `_llm_cache.db`, 使 `verify_stage21_cache_coverage` 计数与生产库 size 不被稀释; 缓存键算法零改动 (golden 不受影响)。
- **golden 影响**: safe (新增 config 键 + 改两验证阶段 cache_db 路径, 不触生产库、不改键算法、不重跑 stage 21; 离线 $0)。

- **逐文件改动**:

  - `config/paths.yaml:64-83` — **锚点(当前真实代码, `filenames` 块尾部, output_27_benefit_cache 是最后一条)**:
    ```yaml
      output_51_panel_controls: 51_panel_with_controls.parquet  # 51_falsification_test.py → 含伪造检验对照变量的面板
      output_27_benefit_cache: 27_benefit_embeddings.npy        # pipeline/features/benefit_society.py (panel 内部 feature, 非独立 shim) → Embedding 缓存 (Jha et al. 2026)
    ```
    **改为** (在 `filenames` 块尾追加验证库文件名键; ⚠ 注意: 该键是文件名 (随 `output_dir` join), 不带 `./` 前缀, 不会被 `_resolve_paths_in_place` 误 join — 与同块其他 `output_*` 文件名键完全同形):
    ```yaml
      output_51_panel_controls: 51_panel_with_controls.parquet  # 51_falsification_test.py → 含伪造检验对照变量的面板
      output_27_benefit_cache: 27_benefit_embeddings.npy        # pipeline/features/benefit_society.py (panel 内部 feature, 非独立 shim) → Embedding 缓存 (Jha et al. 2026)
      # ── 验证阶段 LLM 缓存隔离 (W4, 2026-06-25): 隔离 prompt_sensitivity / entity_masking ──
      # 这两个验证阶段对【变体/掩码后的 prompt】发增量 LLM 请求, 其 prompt 与生产 stage 21
      # 字节不同 → 缓存键不同 → 命中率天然为 0, 会把大量【非生产】键写进 _llm_cache.db。
      # 隔离到独立库后: ① verify_stage21_cache_coverage 的 hits/misses 计数只反映生产语料,
      # 不被验证键稀释; ② 生产 _llm_cache.db size() 不再因跑验证而增长 → golden 确定性锚点纯净。
      # 缓存键算法零改动 (core/caching.py 不动); 仅换 sqlite 文件路径。
      output_llm_cache: _llm_cache.db                            # 生产 LLM 缓存 (stage 21/15/27; golden 确定性锚点, 勿删)
      output_llm_cache_validation: _llm_cache_validation.db      # 验证阶段专用 LLM 缓存 (prompt_sensitivity / entity_masking; 可随意重生, 不进 golden)
    ```
    > ⚠ 设计说明: 同时引入 `output_llm_cache`(生产) 与 `output_llm_cache_validation`(验证) 两键, 让生产路径也从硬编码字面量改为读 config, 二者对称, 杜绝未来漂移。生产库文件名值 `_llm_cache.db` 与现状字节一致 → 生产路径解析结果不变 → 生产侧 golden-safe。**若审阅者希望最小改动**, 可只加 `output_llm_cache_validation` 一键, 生产侧保留字面量 `'_llm_cache.db'` 不动 (见下方"风险/开放问题"的最小方案分支)。

  - `validation/prompt_sensitivity.py:1583` — **锚点(当前真实代码)**:
    ```python
        cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
        with LLMCache(cache_db) as cache:
            logger.info(f"Prompt 敏感度 LLM 缓存: {cache.size()} 条已缓存, 路径: {cache_db}")
    ```
    **改为** (用 config 验证键, 缺省回退保证旧 config 不破):
    ```python
        # W4: 验证阶段写独立缓存库, 不污染生产 _llm_cache.db (隔离非生产变体键,
        # 保 verify_stage21_cache_coverage 计数与生产库 size 纯净)。
        _val_cache_fn = CONFIG.get("filenames", {}).get(
            "output_llm_cache_validation", "_llm_cache_validation.db")
        cache_db = os.path.join(CONFIG["paths"]["output_dir"], _val_cache_fn)
        with LLMCache(cache_db) as cache:
            logger.info(f"Prompt 敏感度 LLM 缓存 (验证隔离库): {cache.size()} 条已缓存, 路径: {cache_db}")
    ```

  - `validation/prompt_sensitivity.py:1443` & `:1493` — **锚点(当前真实代码, 散文日志, 仍提"_llm_cache.db")**:
    ```python
                    "确定性锚点 = _llm_cache.db; NEWS_PROCESS_LLM_OFFLINE=1 时缓存 miss 抛错而非偷跑。")
    ...
        logger.info("【确定性】调 LLM API (变体 prompt 与生产不同 → 增量付费请求, 冷缓存需线上跑); 确定性锚点 = _llm_cache.db;")
    ```
    **改为** (仅更新散文措辞, 反映隔离库; 不改行为):
    ```python
                    "确定性锚点 = _llm_cache_validation.db (验证隔离库); NEWS_PROCESS_LLM_OFFLINE=1 时缓存 miss 抛错而非偷跑。")
    ...
        logger.info("【确定性】调 LLM API (变体 prompt 与生产不同 → 增量付费请求, 冷缓存需线上跑); 确定性锚点 = _llm_cache_validation.db (验证隔离库, 不污染生产);")
    ```

  - `validation/entity_masking.py:941` — **锚点(当前真实代码)**:
    ```python
        cache_db = os.path.join(CONFIG["paths"]["output_dir"], '_llm_cache.db')
        with LLMCache(cache_db) as cache:
            logger.info(f"Entity Masking LLM 缓存: {cache.size():,d} 条已缓存, 路径: {cache_db}")
    ```
    **改为**:
    ```python
        # W4: 验证阶段写独立缓存库, 不污染生产 _llm_cache.db (掩码后 prompt 与生产
        # 字节不同 → 非生产键, 隔离以保生产库 size 与 stage21 覆盖率计数纯净)。
        _val_cache_fn = CONFIG.get("filenames", {}).get(
            "output_llm_cache_validation", "_llm_cache_validation.db")
        cache_db = os.path.join(CONFIG["paths"]["output_dir"], _val_cache_fn)
        with LLMCache(cache_db) as cache:
            logger.info(f"Entity Masking LLM 缓存 (验证隔离库): {cache.size():,d} 条已缓存, 路径: {cache_db}")
    ```

  - `validation/entity_masking.py:732` — **锚点(当前真实代码, banner 日志硬编码字面量)**:
    ```python
            logger.info(f"     · LLM缓存: {os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')}")
    ```
    **改为** (与实际使用的库对齐, 否则 banner 误报生产库路径):
    ```python
            _val_cache_fn = CONFIG.get('filenames', {}).get(
                'output_llm_cache_validation', '_llm_cache_validation.db')
            logger.info(f"     · LLM缓存 (验证隔离库): {os.path.join(CONFIG['paths']['output_dir'], _val_cache_fn)}")
    ```

  - `validation/entity_masking.py:726` & `:801` — **锚点(当前真实代码, 散文日志)**:
    ```python
                    "冷缓存需付费; 命中 _llm_cache.db 则 $0); 离线守卫 NEWS_PROCESS_LLM_OFFLINE=1 优雅跳过")
    ...
        logger.info("【确定性】调 LLM API(yunwu 3 模型 × 3 轨 × 样本量, 经 _llm_cache.db 命中缓存);")
    ```
    **改为** (措辞更新, 行为不变):
    ```python
                    "冷缓存需付费; 命中 _llm_cache_validation.db (验证隔离库) 则 $0); 离线守卫 NEWS_PROCESS_LLM_OFFLINE=1 优雅跳过")
    ...
        logger.info("【确定性】调 LLM API(yunwu 3 模型 × 3 轨 × 样本量, 经 _llm_cache_validation.db 验证隔离库命中缓存);")
    ```

  - `scripts/audit/verify_stage21_cache_coverage.py:91` — **锚点(当前真实代码, 确认读生产库)**:
    ```python
        cache_db = os.path.join(tone_llms.CONFIG['paths']['output_dir'], '_llm_cache.db')
    ```
    **改动**: 字面量不变 (本脚本【必须】继续读生产 `_llm_cache.db` — 这正是隔离要保护的对象)。但为防未来生产库名随 config 漂移, 可改为读生产键 (新 `output_llm_cache`, 缺省回退原字面量, 行为字节不变):
    ```python
        _prod_cache_fn = tone_llms.CONFIG.get('filenames', {}).get(
            'output_llm_cache', '_llm_cache.db')
        cache_db = os.path.join(tone_llms.CONFIG['paths']['output_dir'], _prod_cache_fn)
    ```
    > ⚠ 此改动可选, 是"对称化"收尾 (见 paths.yaml 设计说明)。若采用最小方案 (paths.yaml 只加验证键), 则此处保持字面量 `'_llm_cache.db'` 不动。**关键不变量: 本脚本读的库 ≠ 两验证阶段写的库**, 隔离才生效。

  - `validation/radius_sensitivity_llm.py:136/:161/:341/:379` — **不改 (按集群边界)**。该模块未实装进 DAG (`STAGES_VALIDATION` 不含 65_radius_sensitivity_llm)。仅在 `:161` 注释处加一行未来说明:
    **锚点(当前真实代码 :158-161)**:
    ```python
        if cache_db_path is None:
            from news_process.core.config import load_config
            CONFIG = load_config()
            cache_db_path = _os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')
    ```
    **改为** (仅追加注释, 代码不动):
    ```python
        if cache_db_path is None:
            from news_process.core.config import load_config
            CONFIG = load_config()
            # ⚠ W4 未来: 本模块实装进 DAG 时, 应改读 output_llm_cache_validation
            #   (与 prompt_sensitivity / entity_masking 一致, 验证库隔离); 现未实装暂留生产库字面量。
            cache_db_path = _os.path.join(CONFIG['paths']['output_dir'], '_llm_cache.db')
    ```

- **新增测试**: `news_process/tests/test_validation_cache_isolation.py` (新建)
  - `test_paths_yaml_has_validation_cache_key`: `load_config()['filenames']['output_llm_cache_validation'] == '_llm_cache_validation.db'`, 且与 `output_llm_cache`(若引入) 不相等 → 两库文件名互异。
  - `test_prompt_sensitivity_resolves_validation_db`: monkeypatch/inspect `prompt_sensitivity.CONFIG`, 断言 `os.path.join(output_dir, CONFIG['filenames']['output_llm_cache_validation'])` 的 basename == `_llm_cache_validation.db`, 不等于生产 `_llm_cache.db`。
  - `test_entity_masking_resolves_validation_db`: 同上, 针对 entity_masking。
  - `test_verify_stage21_still_reads_production_db`: 断言 `verify_stage21_cache_coverage` 解析出的 cache_db basename == `_llm_cache.db` (生产), **不**等于验证库 → 计数不被稀释。
  - `test_no_validation_writes_to_production_db` (integration, mocked LLM): 用 tmp `output_dir`, 跑 prompt_sensitivity 的缓存写路径 (或直接对 LLMCache 写一条到验证库), 断言生产库文件 `_llm_cache.db` 不被创建/size 不增, 而 `_llm_cache_validation.db` 被创建且 size>0。
  - 回退断言: 删除 config 中该键时, 两验证阶段仍用 `.get(..., '_llm_cache_validation.db')` 缺省, 不抛 KeyError (向后兼容)。

- **验收** (可执行判定):
  1. `python -c "from news_process.core.config import load_config; c=load_config(); print(c['filenames']['output_llm_cache_validation'], c['filenames'].get('output_llm_cache'))"` → 打印 `_llm_cache_validation.db _llm_cache.db`。
  2. 记录生产库 size: `python -c "from news_process.core.caching import LLMCache; import os; from news_process.core.config import load_config as L; c=L(); p=os.path.join(c['paths']['output_dir'],'_llm_cache.db'); print(LLMCache(p).size())"` (记为 N0)。
  3. mocked-LLM 跑一次 prompt_sensitivity / entity_masking 缓存写路径 → 重测生产库 size 仍 == N0 (**不增**); 验证库 `_llm_cache_validation.db` 出现且 size>0。
  4. `python -m news_process.scripts.audit.verify_stage21_cache_coverage` → `lookups/hits/misses` 与改动前完全一致 (计数不被验证键稀释; 离线全命中仍 misses=0)。
  5. `pytest news_process/tests/test_validation_cache_isolation.py -v` 全绿。
  6. `pytest news_process/tests/integration/test_dag_consistency.py` 绿 (本改动不动 DAG/StageSpec, 应自然通过); `ruff check news_process/validation/prompt_sensitivity.py news_process/validation/entity_masking.py`。
  7. golden: `pytest news_process/tests/integration/test_panel_reproducibility.py` 不受影响 (本改动不触 stage 21 输出、不改键算法)。

- **风险/开放问题**:
  - **首次跑成本**: 隔离后验证库为空, prompt_sensitivity/entity_masking 首跑会冷启动重发增量 LLM 请求 (变体/掩码 prompt)。但这些 prompt 与生产字节不同, 即便共用生产库也是 miss → 隔离不增加任何 API 成本, 只是把"本就要付费的非生产键"落到独立库。离线模式 (`NEWS_PROCESS_LLM_OFFLINE=1`) 下两阶段仍优雅跳过 (graceful skip 逻辑在各自 main 早退, 不依赖库路径)。
  - **历史污染清理 (开放)**: 当前生产 `_llm_cache.db` (~453MB) 可能已混入历史验证键 (此前两阶段写进生产库)。隔离只阻止**未来**污染, 不回溯删除既有验证键。是否需一次性清理 (DELETE 非生产 prompt_version/键) 留待审阅决策 — 但**铁律: 任何对生产库的删除都须先备份且经 `verify_stage21_cache_coverage` 验证 misses 仍=0**, 否则破坏 golden 锚点。保守建议: 不清理 (索引点查 O(log n), 多余键不影响命中性能与正确性)。
  - **最小方案分支**: 若审阅者要求最小 diff, 可只在 paths.yaml 加 `output_llm_cache_validation` 一键, 生产路径 (verify 脚本 + 注释) 保留字面量 `'_llm_cache.db'` 不动。隔离效果完全相同, 仅少 `output_llm_cache` 对称键与 verify 脚本一处可选改动。
  - **size() 调用**: 两处 `cache.size()` 日志现报验证库条数 (而非生产库), 符合预期 (反映该阶段实际用的库)。`core/caching.py::LLMCache.size()` 行为不变, 仅作用于新文件。
  - **radius_sensitivity_llm 未实装**: 已按集群约束仅加注释, 不改其行为; 实装进 DAG 时须同步切到验证库 (注释已留 W4 标记)。
```

---

<a id="集群-c-skip"></a>

No per-stage config sub-tree helper exists. The config is organized into 7 domains (paths, preprocessing, filtering, sentiment, features, panel, validation) plus runtime additions. For W5's sub-tree hashing, I'll define a `STAGE_CONFIG_DOMAINS` mapping. I now have full grounding to write the spec. Let me write the deliverable.

```
## 集群 C-skip — W6 (StageSpec 声明式依赖前置基建) + W5 (通用阶段级增量执行 --skip-unchanged)

### W6 · StageSpec 加可选字段 `inputs` + `fingerprint_cols` (向后兼容默认空)
- **目标**: 给 `StageSpec` dataclass 增可选声明式依赖字段, 让 W5 的通用 skip 判定从 DAG 单源派生, 取代 stage21 现有硬编码上游路径 + 手写指纹列。
- **golden 影响**: safe (纯 dataclass 字段扩展 + 元数据, 默认空 → 不改任何运行时行为, 不触 producer)
- **逐文件改动**:
  - `core/dag.py:129-154` — **锚点(当前真实代码)**:
    ```python
    @dataclass(frozen=True)
    class StageSpec:
        """单个流水线阶段的声明式描述符。
        ...
        Phase 1 刻意不填充 ``inputs`` / ``outputs`` 字段;
        Phase 2d 将通过 ``core.schemas.OUTPUT_REGISTRY`` 串接二者。
        """

        name: str
        script: str
        group: str
        kind: str = "stage"
        # P-072 修复 (v3.7.1): ...
        timeout: int = 7200
        enabled_when: Callable[[dict[str, Any]], bool] = always_enabled
    ```
    **改为** (在 `enabled_when` 之后追加两个默认空 tuple 字段; frozen dataclass 对 default 不可变值安全, 无需 `field(default_factory=...)`):
    ```python
        timeout: int = 7200
        enabled_when: Callable[[dict[str, Any]], bool] = always_enabled

        # ── W6 (CACHE_STRATEGY 批次 2 前置基建, 2026-06-25): 声明式依赖, 供
        #    run_pipeline_function.py 的通用 --skip-unchanged 判定从 DAG 单源派生.
        #    向后兼容默认空 tuple → 不填的 StageSpec 行为字节不变 (test_dag_consistency
        #    只校验 enabled_when, 对新字段无感). tuple (不可变) 适配 frozen=True,
        #    无需 field(default_factory).
        #
        # inputs:          本阶段消费的【上游产物逻辑键】元组, 取自
        #                  core/schemas.py::OUTPUT_REGISTRY 的 script 键 (如
        #                  "15_fintech_intensity.py"). 父进程据此把上游 script →
        #                  产物 parquet 路径, 与本阶段元数据 input_hashes 逐一比对.
        #                  空元组 = "未声明依赖" → W5 对该 stage 保守地【不跳过】.
        # fingerprint_cols: (可选) 若非空, skip 判定额外要求本阶段产物指定列的
        #                  确定性指纹 (复用 _fingerprint_dataframe_rows) 与重算一致.
        #                  当前 W5 主路径只用 config_hash + input_hashes 文件级比对,
        #                  fingerprint_cols 预留给"把 stage21 三重指纹泛化"的长期项
        #                  (§3 批次 2 尾注), 现阶段填了也仅作声明、不强制消费.
        inputs: tuple[str, ...] = ()
        fingerprint_cols: tuple[str, ...] = ()
    ```
  - `core/dag.py:220-230` — **锚点(当前真实代码, stage21 StageSpec 示例)**:
    ```python
    StageSpec(
        name="阶段21: 统一 LLM 语义精筛与情感分析 (三轨 full/ctx/ss)",
        script="21_tone_llms.py",
        group="main", kind="sentiment",
        # v3 / Fix 1: 6h 子进程硬超时. ...
        timeout=21600,
    ),
    ```
    **改为** (填入示例依赖声明; stage21 上游产物逻辑键 = stage15 的 script `15_fintech_intensity.py`, 与 `_stage21_skip_is_compatible` 现读 `output_14_fintech_intensity`→`15_fintech_intensity.parquet` 同一上游一致; fingerprint_cols 镜像现有 `_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS`):
    ```python
    StageSpec(
        name="阶段21: 统一 LLM 语义精筛与情感分析 (三轨 full/ctx/ss)",
        script="21_tone_llms.py",
        group="main", kind="sentiment",
        timeout=21600,
        # W6 示例: 声明上游 = stage15 (15_fintech_intensity.parquet, 经
        # OUTPUT_REGISTRY 解析为实际文件名). fingerprint_cols 复刻既有
        # _STAGE21_UPSTREAM_FINGERPRINT_COLUMNS, 为长期把 stage21 硬编码三重指纹
        # 泛化为通用路径预留 (现阶段 stage21 仍走 --skip-21-if-exists 专用安检).
        inputs=("15_fintech_intensity.py",),
        fingerprint_cols=(),  # 留空: stage21 暂不纳入通用 --skip-unchanged (见 W5 风险)
    ),
    ```
  - `core/dag.py` (其余 STAGES_MAIN 实例) — **示范性填充** (非全量必填, W5 对空 inputs 保守不跳过, 故可增量填; 给出几条确定的链式声明示例):
    ```python
    # 阶段11 (11_news_bank.py): inputs=("00_preprocessing.py",)
    # 阶段12 (12_news_fintech.py): inputs=("11_news_bank.py",)
    # 阶段13 (13_cooccurrence_filter.py): inputs=("12_news_fintech.py",)
    # 阶段14 (14_materialize_ctx.py): inputs=("13_cooccurrence_filter.py",)
    # 阶段15 (15_fintech_intensity.py): inputs=("14_materialize_ctx.py","12_news_fintech.py")
    # 阶段16 (16_article_policy_alignment.py): inputs=("15_fintech_intensity.py",)
    # 阶段22 (22_tone_words.py): inputs=("15_fintech_intensity.py",)
    # 阶段23 (23_tone_berts.py): inputs=("15_fintech_intensity.py",)
    # 阶段24 (24_herd_decay_processor.py): inputs=("23_tone_berts.py",)
    # 阶段40 (40_panel_export_main.py): inputs=("24_herd_decay_processor.py","16_article_policy_alignment.py")
    # 阶段51 (51_falsification_test.py): inputs=("40_panel_export_main.py",)
    ```
    > ⚠ 锚点修正注: 上游逻辑键须与各 producer 真实 `input_files` 实参对齐 (已 Read 核对: stage15 `input_files=[full_path, input_file]` 双源 = 12_full + 14; stage40 `input_files=[output_24_herd_decay, output_15_article_alignment]`; stage51 三源 fan-in)。**填写时以 producer 的 `save_dataset(..., input_files=...)` 真实闭包为准**, 不可凭 DAG 直觉臆造, 否则 W5 input_hashes 比对会对不齐 (见 W5 §映射函数)。stage14 实读上游 = `output_12b_cooccurrence`(13_cooccurrence_filtered.parquet) → inputs 写 `13_cooccurrence_filter.py`。

- **新增测试**: `tests/integration/test_dag_consistency.py` 追加 `test_stagespec_inputs_reference_known_scripts`:
  - 断言: 任一 `StageSpec.inputs` 中的逻辑键 ∈ `{s.script for s in STAGES_MAIN ∪ STAGES_VALIDATION}` ∪ `OUTPUT_REGISTRY.keys()` (防写错上游 script 名)。
  - 断言: 任一非空 `inputs` 的 stage, 其每个上游键都在 `OUTPUT_REGISTRY` (即上游确实产 parquet, 可被 input_hashes 比对)。
  - 断言: `StageSpec()` 不填新字段时 `spec.inputs == ()` 且 `spec.fingerprint_cols == ()` (默认空向后兼容)。
- **验收**:
  - `pytest tests/integration/test_dag_consistency.py -v` 全绿 (含既有 `test_*enabled_when*` 不受影响)。
  - `python -c "from news_process.core.dag import StageSpec; s=StageSpec(name='x',script='y.py',group='main'); assert s.inputs==() and s.fingerprint_cols==()"` 退出 0。
- **风险/开放问题**:
  - frozen dataclass + mutable default: 用 `tuple` (不可变) 而非 `list`, 否则 `dataclass(frozen=True)` 仍允许 list default 但会埋共享可变状态坑 → 已规避。
  - `inputs` 用 **script 逻辑键** 而非 parquet 文件名: 因文件名可经 `paths.yaml::filenames` 改名, script 键稳定 (与 OUTPUT_REGISTRY 单源一致)。映射到实际文件由 W5 的 `_resolve_upstream_paths` 经 `_get_stage_output_files` 完成。

---

### W5 · 新增 `--skip-unchanged` CLI flag + 父进程只读元数据增量跳过判定
- **目标**: 默认关闭的通用增量执行开关; 命中"产物全在 ∧ config 子树 hash 一致 ∧ 上游 input_hashes 逐一匹配"则跳过该 stage (复用 stage21 `⏭`+`(name,0.0,True)` 语义), 判定全在父进程只读元数据完成 → 子进程隔离架构下字节级中性。
- **golden 影响**: safe (跳过逻辑纯读 parquet schema 元数据、不产数据; 净效果只**减少**重算 → 减少 stage21 miss 翻号 / BLAS-FP / jieba+frozenset 等已知非确定源触发次数。默认 flag 关闭 → 生产首跑语义逐字节不变)
- **逐文件改动**:

  **(1) 新增 config 子树映射 + 子树 hash 助手** —— `core/dag.py` 末尾追加 (放 dag.py 因它已是 DAG 单源, 且 schemas/config 都可在此 import; 避免 config.py↔dag.py 循环):
  - `core/dag.py` (文件末尾, 新增) — **新代码**:
    ```python
    # ── W5 (CACHE_STRATEGY 批次 2, 2026-06-25): stage → config 子树域映射 ──
    # 为什么 hash 子树而非整 config: compute_config_hash(整 CONFIG) 会因任一无关
    # 域 (如 validation.* 改个开关) 改变 → 所有 stage 全失效 = 过度失效, 抵消增量价值.
    # 本表把每 stage 绑定其真正消费的 config 域子集; paths 域【所有 stage 共享】
    # (输出路径/资源文件路径), 故恒纳入. 域名取 core/config.py::_SPLIT_DOMAINS.
    #
    # ⚠ 保守原则: 不确定时【多纳入域】(宁可偶尔多失效一次、绝不少失效漏掉真变更).
    # 未在本表登记的 script → 返回全部 7 域 (= 整 config 行为, 最保守, 不会漏失效).
    STAGE_CONFIG_DOMAINS: Mapping[str, tuple[str, ...]] = {
        "00_preprocessing.py":          ("paths", "preprocessing"),
        "11_news_bank.py":              ("paths", "filtering"),
        "12_news_fintech.py":           ("paths", "filtering"),
        "13_cooccurrence_filter.py":    ("paths", "filtering"),
        "14_materialize_ctx.py":        ("paths", "filtering"),
        "15_fintech_intensity.py":      ("paths", "filtering", "features"),
        "16_article_policy_alignment.py": ("paths", "features"),
        "21_tone_llms.py":              ("paths", "sentiment"),
        "22_tone_words.py":             ("paths", "sentiment"),
        "23_tone_berts.py":             ("paths", "sentiment"),
        "24_herd_decay_processor.py":   ("paths", "sentiment"),
        "25_article_sbert.py":          ("paths", "features"),
        "26_article_staleness.py":      ("paths", "features"),
        "40_panel_export_main.py":      ("paths", "panel", "features"),
        "46_stata_export.py":           ("paths", "panel"),
        "51_falsification_test.py":     ("paths", "panel"),
    }
    ```
    > 注: `Mapping` 已在 dag.py 顶部 import (与 `Callable`/`Any` 同处, 需确认; 若未 import 则补 `from typing import Mapping`)。⚠ 锚点修正提示: 实现时先 Read dag.py 顶部 import 段确认 `Mapping` 是否已在 typing import 列, 缺则补。

  **(2) 子树 hash 助手 + 上游路径解析 + skip 判定** —— `run_pipeline_function.py:155` 之后 (紧接 `_get_stage_output_files`), 新增三个父进程纯函数:
  - `run_pipeline_function.py` (新增, 锚定在 `_get_stage_output_files` 定义之后 / `_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS` 之前) — **新代码**:
    ```python
    def _config_subtree_hash(stage_script: str) -> str:
        """对 ``stage_script`` 绑定的 config 域子树计算 SHA-256 (W5).

        复用 producer 写元数据时的 compute_config_hash, 但只喂入该 stage 真正
        消费的域 (STAGE_CONFIG_DOMAINS), 避免整 config 任一无关域改动致全失效.
        未登记的 script → 退化为整 CONFIG hash (最保守, 永不漏失效).

        ⚠ 与 producer 元数据 config_hash 的可比性: producer 调
        save_parquet_with_metadata(config=CONFIG) 写的是【整 CONFIG】hash, 故
        本函数【不能】直接拿子树 hash 去等于 producer 的整 hash. W5 的判定改为:
        把"当前子树 hash"与"上次跑出该产物时的子树 hash"比 —— 需要 producer 也
        写【子树 hash】. 见 (3): 在 data_versioning 额外写一个 config_subtree_hashes
        映射 (stage→子树 hash), 父进程读这个映射做精准比对; 同时保留整 config_hash
        向后兼容旧产物 (旧产物无 subtree 映射 → 回退整 hash 比对, 仍正确只是偏保守).
        """
        from news_process.core.config import load_config  # 已在文件顶部 import CONFIG
        from news_process.core.data_versioning import compute_config_hash
        from news_process.core.dag import STAGE_CONFIG_DOMAINS

        domains = STAGE_CONFIG_DOMAINS.get(stage_script)
        if not domains:
            return compute_config_hash(CONFIG)  # 未登记 → 整 config (最保守)
        subtree = {d: CONFIG.get(d, {}) for d in domains}
        # 资源文件内容指纹: 复用 stage00 哲学 — load-bearing 词典/anchor JSON 的
        # 【内容】须入 hash, 否则改 bank_names.json 路径不变会 verify 失明
        # (news_bank.py:688 / news_fintech.py:439 自承). 把 paths 域中以
        # *_file / *_dict / *_json 结尾且实际存在的资源文件 sha256 纳入子树.
        subtree["_resource_hashes"] = _stage_resource_hashes(stage_script)
        return compute_config_hash(subtree)


    def _stage_resource_hashes(stage_script: str) -> dict:
        """对 stage 的 load-bearing 资源文件 (词典/anchor) 取内容 sha256 (W5).

        复用 preprocess/runner.py::compute_preprocess_cache_key 的资源指纹哲学:
        路径相同但内容变 → 必须失效. 这里取该 stage config 域内引用的资源文件,
        外加各 stage 已知硬编码资源 (与 producer input_files 闭包对齐).
        """
        import os
        from news_process.core.data_versioning import compute_file_hash

        paths = CONFIG.get("paths", {})
        # 资源键白名单: 与 producer 已纳入 input_files 的词典一致 (Read 实证):
        #   news_bank.py:691  → bank_names_file / bank_name_exclusions_file
        #   news_fintech.py:440 → fintech_dict_file
        #   cooccurrence_filter / ctx_materializer → fintech_dict + exclusion + bank_names
        #   preprocess → noise_patterns_file / bank_keywords_file
        _RES_BY_STAGE = {
            "00_preprocessing.py": ("noise_patterns_file", "bank_keywords_file"),
            "11_news_bank.py": ("bank_names_file", "bank_name_exclusions_file"),
            "12_news_fintech.py": ("fintech_dict_file",),
            "13_cooccurrence_filter.py": ("fintech_dict_file", "bank_names_file"),
            "14_materialize_ctx.py": ("fintech_dict_file", "bank_names_file"),
        }
        out = {}
        for key in _RES_BY_STAGE.get(stage_script, ()):
            p = paths.get(key)
            if p and os.path.exists(p):
                out[key] = compute_file_hash(p)
            elif p:
                out[key] = f"missing:{os.path.basename(str(p))}"  # 哨兵, 同 preprocess
        return out


    def _resolve_upstream_product_paths(stage_script: str) -> list[str]:
        """把 StageSpec.inputs (上游 script 逻辑键) 映射为上游产物绝对路径列表 (W5).

        复用 _get_stage_output_files (经 OUTPUT_REGISTRY + paths.yaml::filenames),
        与各 producer 写 input_files 时用的 CONFIG['filenames'][...] 解析同源,
        保证父进程算的"当前上游路径"与产物元数据里记的 input_files 文件名一致.
        """
        import os
        from news_process.core.dag import STAGES_MAIN, STAGES_VALIDATION

        spec = next(
            (s for s in (*STAGES_MAIN, *STAGES_VALIDATION) if s.script == stage_script),
            None,
        )
        if spec is None or not getattr(spec, "inputs", ()):
            return []  # 无 spec 或未声明上游 → 调用方据此保守不跳过
        out_dir = CONFIG["paths"]["output_dir"]
        paths = []
        for up_script in spec.inputs:
            for fname in _get_stage_output_files(up_script):
                paths.append(os.path.join(out_dir, fname))
        return paths


    def _stage_skip_is_safe(stage_script: str) -> tuple[bool, str]:
        """通用 --skip-unchanged 判定 (W5): 父进程纯只读元数据, 字节级中性.

        可跳过 ⟺ ① 本 stage 登记产物全存在; ② 每个产物的 config_subtree_hash
        (回退整 config_hash) == 当前重算值; ③ StageSpec.inputs 已声明且非空,
        且每个上游产物当前 sha256 == 产物元数据 input_hashes 里记录的该文件 hash.

        任一不满足 → (False, 原因); 全满足 → (True, 原因). 不确定一律 False
        (保守: 宁可多跑一次、绝不消费陈旧数据).
        """
        import os
        from news_process.core.data_versioning import (
            compute_file_hash,
            read_parquet_metadata,
        )
        from news_process.core.dag import STAGES_MAIN, STAGES_VALIDATION

        out_dir = CONFIG["paths"]["output_dir"]

        # ── ① 产物全存在? (validation/no-output stage → _get_stage_output_files
        #    返回 []; 空产物无元数据可比 → 不跳过, 总是重跑) ──
        outputs = _get_stage_output_files(stage_script)
        if not outputs:
            return False, "stage has no registered parquet outputs (always run)"
        out_paths = [os.path.join(out_dir, f) for f in outputs]
        missing = [p for p in out_paths if not os.path.exists(p)]
        if missing:
            return False, f"missing outputs: {[os.path.basename(p) for p in missing]}"

        # ── ③(前置) 必须声明 inputs 才允许判定上游一致性; 未声明 → 不跳过 ──
        spec = next(
            (s for s in (*STAGES_MAIN, *STAGES_VALIDATION) if s.script == stage_script),
            None,
        )
        if spec is None or not getattr(spec, "inputs", ()):
            return False, "stage declares no StageSpec.inputs (cannot verify upstream)"

        # ── ② config 子树 hash 一致? (逐产物校验, 任一不符即重跑) ──
        cur_subtree = _config_subtree_hash(stage_script)
        for p in out_paths:
            meta = read_parquet_metadata(p)
            if meta is None:
                return False, f"{os.path.basename(p)} lacks data_version metadata"
            recorded = meta.get("config_subtree_hash") or meta.get("config_hash")
            cur = cur_subtree if "config_subtree_hash" in meta else _legacy_full_hash()
            if recorded != cur:
                return False, f"{os.path.basename(p)} config hash changed"

        # ── ③ 上游 input_hashes 逐一匹配? ──
        upstream_paths = _resolve_upstream_product_paths(stage_script)
        # 产物元数据 input_hashes 是 {绝对/相对路径 -> sha256}; producer 写时用的
        # 路径可能与当前 cwd 不同 → 用 basename 归一比对 (与 producer input_files
        # 同源解析, basename 唯一足够区分本 stage 上游集).
        primary_meta = read_parquet_metadata(out_paths[0]) or {}
        recorded_hashes = primary_meta.get("input_hashes", {})
        recorded_by_base = {
            os.path.basename(k): v for k, v in recorded_hashes.items()
        }
        for up in upstream_paths:
            if not os.path.exists(up):
                return False, f"upstream missing: {os.path.basename(up)}"
            base = os.path.basename(up)
            if base not in recorded_by_base:
                return False, f"upstream {base} not in recorded input_hashes (stale spec?)"
            if compute_file_hash(up) != recorded_by_base[base]:
                return False, f"upstream {base} content changed since last run"

        return True, f"unchanged: config subtree + {len(upstream_paths)} upstream(s) match"
    ```
    > ⚠ **可比性核心难点 (开放问题, 见风险段)**: 现有 producer 写的是 `compute_config_hash(整 CONFIG)`, 不是子树 hash。要让 ② 精准生效, 需 (3) 让 producer 额外写 `config_subtree_hash`。在 producer **尚未**写之前, `_stage_skip_is_safe` 走 `meta.get("config_hash")` 回退分支 → 比的是整 config (偏保守: 任一无关域改动也失效, 但**绝不漏失效, 故 safe**)。`_legacy_full_hash()` = `compute_config_hash(CONFIG)` 的薄封装 (需新增, 见下)。

  - `run_pipeline_function.py` (新增小助手, 紧邻上述) — **新代码**:
    ```python
    def _legacy_full_hash() -> str:
        """旧产物 (无 config_subtree_hash) 的回退: 整 CONFIG hash, 与 producer
        当前 save_parquet_with_metadata(config=CONFIG) 写入值同算法可比."""
        from news_process.core.data_versioning import compute_config_hash
        return compute_config_hash(CONFIG)
    ```

  **(3) producer 侧写入子树 hash (可选增强, 让 ② 精准)** —— `core/data_versioning.py:138-150`:
  - `core/data_versioning.py:138-150` — **锚点(当前真实代码)**:
    ```python
    def to_dict(self) -> dict:
        """转换为字典。"""
        return {
            "stage_name": self.stage_name,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "config_hash": self.config_hash,
            "timestamp": self.timestamp,
            "python_version": self.python_version,
            "dependencies": self.dependencies,
            "input_files": self.input_files,
            "input_hashes": self.input_hashes,
        }
    ```
    **改为** (`DataVersionMetadata.__init__` 用 `stage_name` 反查子树域算 `config_subtree_hash`, 并入 to_dict; **不改既有 `config_hash` 字段** → 旧消费者与 golden 字节布局零回归, 只**新增**一个 metadata key):
    ```python
    # __init__ 内 self.config_hash = compute_config_hash(config) 之后追加:
    #   self.config_subtree_hash = _compute_stage_subtree_hash(stage_name, config)
    # 其中 _compute_stage_subtree_hash 是 data_versioning 模块级新函数, 复用
    #   STAGE_CONFIG_DOMAINS (从 core.dag 延迟 import, 防循环); stage_name 不在表
    #   中 → 返回整 config_hash (= self.config_hash, 退化保守).
    def to_dict(self) -> dict:
        return {
            "stage_name": self.stage_name,
            "git_commit": self.git_commit,
            "git_branch": self.git_branch,
            "config_hash": self.config_hash,
            "config_subtree_hash": self.config_subtree_hash,   # ← W5 新增 key
            "timestamp": self.timestamp,
            ...
        }
    ```
    > ⚠ **golden 影响细评**: `data_version` 是 parquet schema **metadata** (非数据列), 写进 schema 的 b"data_version" JSON blob。新增一个 JSON key 会改 schema metadata 字节, 但 **`test_panel_reproducibility` 比的是数据列哈希 (`pq.read_table` 后逐列 sha256), 不比 schema metadata** → 数据列字节不变 → golden-safe。需 Read `tests/integration/test_panel_reproducibility.py` 与 `generate_golden_snapshot.py` **确认 golden 快照不含 schema metadata** (若含则此项降级为 needs-regen)。**保守裁决**: 若不确定, (3) **可不做** —— 不写子树 hash, W5 永走 `config_hash` 整 hash 回退分支, 功能仍正确(偏保守失效), 且 producer 零改动 → 绝对 safe。本规格把 (3) 标为**可选增强**, 默认建议**先不做 (3)**, W5 仅靠 ①整config_hash③input_hashes 上线。

  **(4) CLI flag** —— `run_pipeline_function.py:343-351`:
  - `run_pipeline_function.py:343-351` — **锚点(当前真实代码)**:
    ```python
    parser.add_argument(
        "--skip-21-if-exists",
        action="store_true",
        help=(
            "若 stage 21 (LLM tone) 的输出 parquet 已存在 (含 _full 变体), "
            "跳过该阶段的预清理与子进程执行。常用场景: LLM 已花费 7200s 跑完, "
            "想增量重跑下游 stage 而不重新调用 LLM API。"
        ),
    )
    return parser.parse_args(argv)
    ```
    **改为** (追加 `--skip-unchanged`, 默认 False; 不动既有 `--skip-21-if-exists`):
    ```python
    parser.add_argument(
        "--skip-21-if-exists",
        action="store_true",
        help=( ... 原文不动 ... ),
    )
    parser.add_argument(
        "--skip-unchanged",
        action="store_true",
        help=(
            "通用增量执行 (CACHE_STRATEGY W5): 若某 stage 登记产物全存在, 且其 "
            "config 子树 hash 与上游产物 input_hashes 均未变, 则跳过该阶段 (只读 "
            "元数据判定, 字节级中性). 默认关闭 — 不带此 flag 时行为与现状逐字节一致. "
            "仅对在 StageSpec.inputs 声明了上游的 stage 生效, 未声明者保守重跑."
        ),
    )
    return parser.parse_args(argv)
    ```

  **(5) 主循环接入** —— `run_pipeline_function.py:518-548`:
  - `run_pipeline_function.py:518-537` — **锚点(当前真实代码, stage21 单点跳过分支)**:
    ```python
    for script, name, timeout in stages:
        # plan m1 方案 C: stage 21 增量跳过开关
        if (args.skip_21_if_exists and script == '21_tone_llms.py'):
            stage21_outputs = _get_stage_output_files(script)
            can_skip_stage21, skip_reason = _stage21_skip_is_compatible(stage21_outputs)
            if can_skip_stage21:
                logger.info(
                    f"  ⏭ {name}: --skip-21-if-exists 命中, 已跳过 "
                    f"({skip_reason})"
                )
                stage_timings.append((name, 0.0, True))
                continue
            else:
                logger.warning(
                    f"  --skip-21-if-exists 已启用, 但 {name} 不能安全跳过: "
                    f"{skip_reason}; 将重新执行该阶段"
                )

        # ── 数据流防护：预清理阶段输出，防止陈旧数据污染 ──
        output_files = _get_stage_output_files(script)
        for filename in output_files:
            ...
    ```
    **改为** (在 stage21 专用分支**之后**、预清理**之前**插入通用判定; 命中即 `continue` 跳过预清理删除——与 stage21 分支同控制流):
    ```python
    for script, name, timeout in stages:
        # plan m1 方案 C: stage 21 增量跳过开关 (原文不动)
        if (args.skip_21_if_exists and script == '21_tone_llms.py'):
            ... 原文不动 ...

        # ── W5 (CACHE_STRATEGY 批次 2): 通用 --skip-unchanged 增量执行 ──
        # 必须放在【预清理 os.remove 之前】: 一旦预清理删了产物, 元数据就没了,
        # skip 判定永远 False, 增量价值归零. 命中即 continue → 与 stage21 分支
        # 同语义 (⏭ + (name, 0.0, True)). 判定纯父进程只读元数据, 不进 stage
        # 内存 → 子进程隔离架构下字节级中性 (golden-safe).
        if args.skip_unchanged:
            can_skip, skip_reason = _stage_skip_is_safe(script)
            if can_skip:
                logger.info(f"  ⏭ {name}: --skip-unchanged 命中, 已跳过 ({skip_reason})")
                stage_timings.append((name, 0.0, True))
                continue
            else:
                logger.info(f"  ▶ {name}: --skip-unchanged 不命中, 将执行 ({skip_reason})")

        # ── 数据流防护：预清理阶段输出 (原文不动) ──
        output_files = _get_stage_output_files(script)
        for filename in output_files:
            ...
    ```

  **(6) 验证 runner 对称接入** —— `run_pipeline_validation.py:253-263`:
  - `run_pipeline_validation.py:253-263` — **锚点(当前真实代码, 验证执行循环)**:
    ```python
    for script, name, timeout in stages:
        success, elapsed = run_stage(script, name, logger, SCRIPT_DIR, timeout=timeout)
        stage_timings.append((name, elapsed, success))

        if not success:
            all_success = False
            logger.error(f"评估验证模块在 {name} 处中断。后续阶段将跳过。")
            break
    ```
    **改为** (加同款判定; 验证阶段多数无 parquet 产物 → `_stage_skip_is_safe` 第①步 `not outputs` 即返 False, 自然保守重跑, 只对 72/73/75 等真产 parquet 且声明了 inputs 的验证 stage 生效。需 import `_stage_skip_is_safe` + 加 CLI flag, 此处复用 main runner 的同名函数——抽到共享模块或在 validation runner 内再定义一份。**推荐**: 把 (2) 的四个 `_stage_*` 函数抽到 `core/incremental.py` 供两 runner 共享):
    ```python
    # run_pipeline_validation.py 顶部新增 CLI 解析 (镜像 main runner --skip-unchanged)
    # 与 from news_process.core.incremental import stage_skip_is_safe
    for script, name, timeout in stages:
        if args.skip_unchanged:
            can_skip, reason = stage_skip_is_safe(script, CONFIG)
            if can_skip:
                logger.info(f"  ⏭ {name}: --skip-unchanged 命中 ({reason})")
                stage_timings.append((name, 0.0, True))
                continue
        success, elapsed = run_stage(script, name, logger, SCRIPT_DIR, timeout=timeout)
        ...
    ```
    > ⚠ 锚点修正注: validation runner 当前 (`:294`) `if __name__=='__main__': run_validation()` 无 argparse。需新增轻量 `argparse`(仅 `--skip-unchanged`) 并把 `args` 透传给 `run_validation`。Read `run_pipeline_validation.py` 顶部确认现有 main/CLI 形态后接入。**架构决策**: 把 (2) 四函数从 `run_pipeline_function.py` 提取到新 `core/incremental.py`(签名加显式 `config` 参, 去掉对模块级 `CONFIG` 的隐式依赖), 两 runner 都 import → 消除重复、保两路逐字节同判定。main runner 则改为 `from news_process.core.incremental import stage_skip_is_safe`。

- **新增测试**: `tests/integration/test_skip_unchanged.py` — 4 个用例 (mock 产物 + 元数据, 不跑真 stage):
  - **(a) `test_second_run_skips_all`**: 用 `save_parquet_with_metadata` 造两个上下游产物 (上游 → 下游, 下游元数据 input_hashes 含上游真 sha256); 调 `stage_skip_is_safe(下游script, cfg)` 返 `(True, ...)`。断言全链可跳。
  - **(b) `test_config_subtree_change_invalidates`**: 造产物后, 修改该 stage 绑定的 config 子树域 (如 `filtering` 下一个键); 断言 `stage_skip_is_safe` 返 `(False, "...config hash changed")`; 同时断言修改**无关域** (如 `validation`) 在子树模式下**仍可跳** (验证 hash 子树而非整 config 不过度失效)——若 (3) 未做、走整 hash 回退, 此子断言标 `xfail`/skip 并注释"待 (3) 落地"。
  - **(c) `test_upstream_product_change_invalidates`**: 重写上游产物 (内容变 → sha256 变), 下游元数据 input_hashes 记的是旧 hash; 断言下游 `stage_skip_is_safe` 返 `(False, "upstream ... content changed")`。
  - **(d) `test_default_no_flag_is_byte_identical`**: 不传 `--skip-unchanged` (或 `args.skip_unchanged=False`) 时, 主循环判定分支被短路, `_stage_skip_is_safe` 永不被调 → 断言 `_parse_cli_args([]).skip_unchanged is False` 且行为路径与现状一致 (用 monkeypatch 计数 `_stage_skip_is_safe` 调用 0 次)。
  - 额外: `test_missing_metadata_is_conservative` (产物无 `data_version` 元数据 → 返 False, 不跳); `test_no_inputs_declared_is_conservative` (StageSpec.inputs 为空 → 返 False)。
- **验收**:
  - `pytest tests/integration/test_skip_unchanged.py -v` 4+2 用例全绿。
  - `pytest tests/integration/test_dag_consistency.py tests/integration/test_panel_reproducibility.py -v` 全绿 (证 W5+W6 不破既有门禁; reproducibility 证 golden 列哈希不变)。
  - `python run_pipeline_function.py --help` 显示 `--skip-unchanged`; 不带 flag 跑一次小样 → 日志无任何 `⏭ ...--skip-unchanged` 行 (默认关闭语义)。
  - 手工二次跑验证: 带 `--skip-unchanged` 第二次跑 (产物已在) → 日志出现 `⏭ ... --skip-unchanged 命中`, 且 `_llm_cache.db` `size()` 不增 (stage21 未真执行 → 零 API)。
  - `ruff check .` clean。
- **风险/开放问题**:
  - **R1 (核心) config 子树 hash 可比性**: producer 现写整 `config_hash`。在 (3) 未落地前, W5 ② 走整 hash 回退 → 任一无关域改动也会失效 (偏保守, **不漏失效=safe**, 仅牺牲部分增量收益)。要拿到"只失效相关域"的精准性须做 (3); (3) 的 golden 风险取决于 golden 快照是否含 schema metadata —— **必须先 Read `generate_golden_snapshot.py` 与 `test_panel_reproducibility.py` 确认**, 确认不含才把 (3) 标 safe, 否则 (3) 不做。
  - **R2 input_hashes 路径归一**: producer 写 `input_files` 时存的是其 `os.path.join(output_dir, ...)` 路径 (可能相对/绝对随 cwd)。父进程比对用 **basename 归一** (已在 `_stage_skip_is_safe` 用 `recorded_by_base`)。需确认同一 stage 上游集 basename 无碰撞 (当前各 stage 上游 parquet 文件名唯一, 满足)。
  - **R3 资源文件内容指纹**: `_stage_resource_hashes` 复刻 stage00/news_bank/news_fintech 的词典内容入 hash 哲学, 但 producer 的 `input_hashes` **已含**这些词典 (news_bank.py:691 把 bank_names_file 等放进 input_files)。故 W5 的 ③ input_hashes 比对**已天然覆盖词典内容变更** → `_config_subtree_hash` 里的 `_stage_resource_hashes` 是**双保险/冗余**(防 producer 未来漏记某资源)。可保留(更稳)或精简(避免双算)——本规格保留, 注释标"与 producer input_hashes 冗余互证"。
  - **R4 stage21 与通用路径并存**: stage21 同时被 `--skip-21-if-exists`(专用三重指纹安检) 与 `--skip-unchanged`(通用) 覆盖。两 flag 可同开; 控制流上 stage21 专用分支在前命中即 continue, 通用分支不会重复判 stage21。本规格故意**不把 stage21 纳入通用路径**(其 fingerprint_cols 留空 / 通用判定对 stage21 因 21 产物 input_hashes 仅记 stage15 单源、而 stage21 真实跳过安全性还依赖 verified-filter 行集语义, 整 config_hash 回退不足以保证)——stage21 继续走更严的专用安检, 通用路径覆盖其余 stage。
  - **R5 stage40/51 多源 fan-in**: stage40 `input_files` 实记 24+15, 但 StageSpec.inputs 若声明 `("24_...","16_...")` 会与 producer 记的 15(`output_15_article_alignment`=16_article_alignment.parquet) 命名错位。⚠ **必须以 producer 真实 input_files 闭包为准填 inputs**(已在 W6 锚点修正注强调): stage40 producer 记的是 `output_24_herd_decay` + `output_15_article_alignment`(文件名 16_article_alignment.parquet, 逻辑键 script=16_article_policy_alignment.py) → inputs 应写 `("24_herd_decay_processor.py","16_article_policy_alignment.py")`。填错会导致 R2 basename 不在 recorded_by_base → 返 False(保守不跳, 不会误跳, 仍 safe 但丧失增量)。
```

---

<a id="集群-d-localmodel"></a>

## 集群 D-localmodel — W7 (SBERT 复用 _encode_local_cached) + W8 (BERT 推理缓存)

### W7 · stage 25 SBERT 走 embedding_engine.embed_texts(local spec) 复用穿透缓存
- **目标**: 把 stage 25 (`article_sbert.py`) 的三轨 `model.encode` 替换为 `embedding_engine.embed_texts(local spec, cache=共享 LLMCache)`，让 article-level SBERT 嵌入像 text2vec 主路径一样跨 run/跨 stage 命中 `_llm_cache.db` → 离线 $0 字节级复现；并借机把 `model_revision` 钉死进缓存键。
- **golden 影响**: needs-regen（首跑须受控环境播种 SBERT 三轨缓存；之后离线复现）。

- **逐文件改动**:

  - `pipeline/text/article_sbert.py:109-130` — **锚点(当前真实代码)**:
    ```python
    def _resolve_sbert_model(config: dict) -> tuple[str, str | None]:
        ...
        rob = (config or {}).get('embedding_robustness', {}) or {}
        model_id = rob.get('model') or 'shibing624/text2vec-base-chinese'
        revision = rob.get('revision') or None
        return model_id, revision


    # 与 config/features.yaml::embedding_robustness.model 真单源对齐 (stage 15/25 t2v 同源)
    _SBERT_MODEL_ID, _SBERT_REVISION = _resolve_sbert_model(CONFIG)

    # 30a 输入文本构造版本 (provenance, 与 LLMCache 的 prompt_version 维度同哲学):
    # v2 = 2026-06-08 dual-track parity (...)
    _TEXT_PIPELINE_VERSION = 'v2-2026-06-08-dualtrack-prepend'
    ```
    **改为** — 新增"把 SBERT 路径折成 local spec"的构造器，并让 `text_pipeline_version` **把 revision 并入命名空间**（这是 (b) "revision 钉死并入键"的关键：embed_texts 的缓存键 = `model_id + 逐字 chunk 文本 + spec_version()`；spec_version 取 `spec['text_pipeline_version']`，故须把 revision 拼进该字段，否则换 revision 不触发 miss）：
    ```python
    # ── 锚点不变: _resolve_sbert_model / _SBERT_MODEL_ID / _SBERT_REVISION 保留 ──

    # W7: SBERT 改走统一 embedding_engine.embed_texts(local spec) 复用 _encode_local_cached
    # 穿透缓存 (此前每跑全量重 encode)。缓存键 = model_id + 逐字 chunk 文本 + spec_version;
    # spec_version 取自 spec['text_pipeline_version'] → 把 revision 拼进版本字段, 使
    # "换 revision ⇒ 缓存键变 ⇒ 自动 silent-miss" (否则同 model_id 不同 revision 会误命中旧权重值)。
    _SBERT_VERSION_NS = (
        f"{_TEXT_PIPELINE_VERSION}|rev:{_SBERT_REVISION}"
        if _SBERT_REVISION else _TEXT_PIPELINE_VERSION
    )

    def _build_sbert_local_spec() -> dict:
        """把 SBERT 折成 embedding_engine 的 local spec (base_url='local' → spec_uses_local=True)。

        text_pipeline_version 已并入 revision (见 _SBERT_VERSION_NS): 缓存键随 revision 变动。
        batch_size 沿用 encode_articles 默认 64 (与历史一致, 不改 batched-matmul FP 路径)。
        """
        return {
            'model': _SBERT_MODEL_ID,
            'base_url': 'local',
            'api_key': 'local',
            'text_pipeline_version': _SBERT_VERSION_NS,
            'batch_size': 64,
        }
    ```
    ⚠ 锚点修正: `_resolve_sbert_model` 实际在 line 109（与测绘描述一致）；测绘提到的"`:65/:511` 自承未钉死"实为模块 docstring line 65 与 main 日志 line 511 的散文注释（"⚠ revision 当前未钉死"），**非代码 bug**——revision 钉死机制 `_load_sbert_model` line 168-170 早已存在（`if _SBERT_REVISION: SentenceTransformer(..., revision=...)`），W7 仅补"revision 进缓存键"这一缺口。

  - `pipeline/text/article_sbert.py:173-220` — **锚点(当前真实代码)** `encode_articles`:
    ```python
    def encode_articles(df, content_col, title_col='标题', batch_size=64, model=None) -> np.ndarray:
        if model is None:
            model = _load_sbert_model()
        if title_col and title_col in df.columns:
            docs = [_truncate_for_sbert(t, c) for t, c in zip(...)]
        else:
            docs = [(c or '')[:TITLE_CHARS + FIRST_PARA_CHARS] for c in df[content_col].fillna('')]
        ...
        embs = model.encode(docs, batch_size=batch_size, show_progress_bar=..., normalize_embeddings=True, convert_to_numpy=True)
        return embs.astype(np.float32)
    ```
    **改为** — 保留 `docs` 构造与 `_load_sbert_model`/`ensure_torch_determinism` 直调路径（满足 (c) 与向后兼容 monkeypatch 测试），但把真正 forward 改成"经 `_encode_local_cached` 穿透缓存"。关键 (a) **dict.fromkeys 去重已在 `_encode_local_cached` 内置**（line 627 `dict.fromkeys(missing_chunks)`），故此处只须把 `docs` 原样交给它即可；归一化 `normalize_embeddings=True` 是 SBERT 内置而 `encode_local`(line 291/321) 调 `model.encode(...)` **不传** `normalize_embeddings` → 须在 `_encode_local_cached` 返回后显式补一次 L2 归一以保数值等价：
    ```python
    def encode_articles(df, content_col, title_col=None, batch_size=64, *,
                        spec=None, cache=None, cache_db_path=None,
                        model=None) -> np.ndarray:
        # docs 构造原样保留 (Bybee 截断 / title_col 语义不变)
        if title_col and title_col in df.columns:
            docs = [_truncate_for_sbert(t, c)
                    for t, c in zip(df[title_col].fillna(''), df[content_col].fillna(''))]
        else:
            docs = [(c or '')[:TITLE_CHARS + FIRST_PARA_CHARS]
                    for c in df[content_col].fillna('')]

        logger.info(f"  编码 {len(docs)} 篇文章 (穿透缓存路径)")
        t0 = time.time()
        if spec is not None:
            # W7: 走 embedding_engine 穿透缓存 (_encode_local_cached 含 dict.fromkeys 去重 +
            # ensure_torch_determinism)。embed_texts 的本地路径不做 normalize_embeddings,
            # 故返回后显式 L2 归一, 与历史 SBERT model.encode(normalize_embeddings=True) 逐位等价。
            from news_process.pipeline.text import embedding_engine as _eng
            raw = _eng.embed_texts(
                docs, spec, cache=cache, cache_db_path=cache_db_path,
                log_prefix=f"SBERT[{_SBERT_MODEL_ID}]")
            if raw is None:  # local 路径不返回 None, 纯防御
                raise RuntimeError("SBERT embed_texts 返回 None (local spec 不应发生)")
            embs = np.asarray(raw, dtype=np.float64)
            norms = np.linalg.norm(embs, axis=1, keepdims=True)
            norms[norms == 0.0] = 1.0
            embs = (embs / norms).astype(np.float32)
        else:
            # 向后兼容: 无 spec → 旧直调路径 (测试 monkeypatch SentenceTransformer / 离线单测)
            if model is None:
                model = _load_sbert_model()
            embs = model.encode(
                docs, batch_size=batch_size, show_progress_bar=sys.stderr.isatty(),
                normalize_embeddings=True, convert_to_numpy=True).astype(np.float32)
        logger.info(f"  编码完成: {sig4(time.time() - t0)}s, shape={embs.shape}")
        return embs
    ```
    ⚠ **数值等价风险(开放问题, 见下)**: 历史 `SentenceTransformer.encode(normalize_embeddings=True)` 在 fp32 GPU 张量上**归一化后再** `convert_to_numpy`；本改在 numpy fp64 上归一化。两者舍入路径不同 → 可能 ~1e-7 漂移。故 W7 标 **needs-regen**（不可声称 byte-equal continuation，须受控重生 golden）。

  - `pipeline/text/article_sbert.py:385-411` — **锚点(当前真实代码)** main 三轨调用:
    ```python
    _sbert_model = _load_sbert_model()
    _has_cfull = 'content_full' in df.columns
    embs_full = encode_articles(df, content_col='content_full' if _has_cfull else '内容',
                                title_col=None if _has_cfull else '标题', model=_sbert_model)
    embs_ctx = (encode_articles(df, content_col='content_ctx', title_col=None, model=_sbert_model)
                if 'content_ctx' in df.columns else np.full_like(embs_full, np.nan))
    embs_ss = (encode_articles(df, content_col='content_ss', title_col=None, model=_sbert_model)
               if 'content_ss' in df.columns else None)
    ```
    **改为** — 构造一个共享 `LLMCache` 连接 + local spec，三轨复用（镜像 `policy_alignment.py:622` 的 `shared_cache` 模式）：
    ```python
    from news_process.core.caching import LLMCache  # 顶部 import 区
    _CACHE_DB_PATH = CONFIG['paths'].get(
        'llm_cache_db', os.path.join(output_dir, '_llm_cache.db'))
    _spec = _build_sbert_local_spec()

    _has_cfull = 'content_full' in df.columns
    _shared_cache = LLMCache(_CACHE_DB_PATH)
    try:
        embs_full = encode_articles(
            df, content_col='content_full' if _has_cfull else '内容',
            title_col=None if _has_cfull else '标题',
            spec=_spec, cache=_shared_cache, cache_db_path=_CACHE_DB_PATH)
        embs_ctx = (
            encode_articles(df, content_col='content_ctx', title_col=None,
                            spec=_spec, cache=_shared_cache, cache_db_path=_CACHE_DB_PATH)
            if 'content_ctx' in df.columns else np.full_like(embs_full, np.nan))
        embs_ss = (
            encode_articles(df, content_col='content_ss', title_col=None,
                            spec=_spec, cache=_shared_cache, cache_db_path=_CACHE_DB_PATH)
            if 'content_ss' in df.columns else None)
    finally:
        _shared_cache.close()
    ```
    注: `_load_sbert_model()` 顶层调用可删（forward 现走 embedding_engine 的 `_LOCAL_MODELS` 进程级缓存 + 其内部 `ensure_torch_determinism`），但保留 `_load_sbert_model`/`_truncate_for_sbert` 函数定义不动（测试与向后兼容路径仍用）。`ensure_torch_determinism` 在 `encode_local`(line 273) 已调 → (c) 满足。

- **新增测试**: `tests/test_omni_fix_embed.py` 新增类 `TestSbertCacheReuse`:
  - `test_revision_in_cache_namespace`: 断言 `_build_sbert_local_spec()` 在配 `revision='abc'` 时 `spec['text_pipeline_version']` 含 `'rev:abc'`；不配 revision 时等于 `_TEXT_PIPELINE_VERSION`。
  - `test_encode_articles_with_spec_routes_to_engine`: monkeypatch `embedding_engine.embed_texts` 返回固定 fp32 (N,4) 数组，断言 `encode_articles(df, spec=spec)` 返回 L2 归一后形状/行数正确、范数≈1。
  - `test_encode_articles_no_spec_backcompat`: monkeypatch `SentenceTransformer`，断言 `spec=None` 走旧直调路径（不触 embed_texts）。
  - `test_source_lock_sbert_uses_embed_texts`: 源码断言 `article_sbert.py` 含 `embed_texts(` 且 `LLMCache(` 且 `_build_sbert_local_spec`，无残留顶层 `_sbert_model = _load_sbert_model()` forward 调用。

- **验收**:
  - `pytest news_process/tests/test_omni_fix_embed.py -v`（含既有 4 个 `_resolve_sbert_model` 锁仍绿）。
  - 受控环境首跑播种: `PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python news_process/25_article_sbert.py` → 看 `25_article_sbert.log` 出现 `本地缓存拦截: 命中 0 ... 缺失 N`（首跑全 miss）。
  - 第二次同环境跑 → 日志 `命中 N ... 缺失 0`；`md5sum data/processed/25_article_embeddings.parquet` 两跑一致。
  - golden: `python scripts/migrate/generate_golden_snapshot.py` 后 `pytest tests/integration/test_panel_reproducibility.py`（受控环境；emb 仅喂 stage 18 staleness，间接列，须并入 DEFERRED 批）。

- **风险/开放问题**:
  - **归一化舍入漂移**: numpy fp64 归一 vs SBERT 张量内归一可能 1e-7 级差 → emb_full L2 仍≈1 但向量逐位不同 → 下游 `semantic_staleness_*` 余弦微变。**这是 W7 必须 needs-regen 而非 safe 的根因**；首跑即冻结新值，此后离线复现。
  - **GPU 1-ULP 同文本漂移**: 已被 `_encode_local_cached` 的 `dict.fromkeys` 去重(line 627)化解 (a)，与 text2vec 主路径同标杆。
  - **缓存膨胀**: SBERT 三轨 ~3×N 条进 `_llm_cache.db`（与 emb_ctx/emb_ss 文本去重后实际 < 3N）；与 W8 独立 db 的取舍见下。SBERT 768 维 json 每条 ~6KB → N=1.1k 时 +~20MB，可接受。
  - 开放: 是否把 SBERT 缓存隔离到独立 `_local_embed_cache.db`？默认复用 `_llm_cache.db`（model_id 前缀已隔离不串），与 text2vec 主路径同库一致，**推荐复用**。

---

### W8 · tone_berts 加 BERT 推理缓存 (复用 LLMCache, 独立 _local_model_cache.db)
- **目标**: 在 `run_all_models` 的逐文章聚合输出处包一层缓存：键含 `(short_name, max_length, vocab_fingerprint, content, deterministic_mode, AMP 标志, checkpoint 指纹)`，值 `json{label, probabilities(round4), num_windows}`。argmax+round4 离散化使其**最安全**（缓存的是已离散的分类标签+4 位概率，吸收所有 fp 漂移）。
- **golden 影响**: needs-regen（首跑播种 BERT 缓存；但因值已 round4 离散，重生差异为零或仅停留在历史 BLAS-FP 抖动被冻结，实际更稳）。

- **逐文件改动**:

  - `pipeline/sentiment/tone_berts.py:80-95` (import 区) — **锚点(当前真实代码)**:
    ```python
    import gc
    import hashlib
    import os
    import sys
    import time
    import warnings
    ```
    **改为** — 补 `json` + `LLMCache`（`hashlib`/`os` 已在）:
    ```python
    import gc
    import hashlib
    import json          # W8: BERT 推理缓存值 json 序列化
    import os
    import sys
    import time
    import warnings
    ```
    并在 line 113 `from news_process.core.config import load_config` 附近补:
    ```python
    from news_process.core.caching import LLMCache  # W8: 复用 sqlite 穿透缓存类
    ```

  - `pipeline/sentiment/tone_berts.py:406-408` 附近 (模块级常量区) — **锚点(当前真实代码)**:
    ```python
    INFERENCE_BATCH_SIZE = BERT_PARAMS.get('inference_batch_size', 128)
    # 每次调用 engine.run_all_models 的文章批次数
    ```
    **改为** — 新增缓存 db 路径 + 缓存开关 + checkpoint 指纹助手:
    ```python
    INFERENCE_BATCH_SIZE = BERT_PARAMS.get('inference_batch_size', 128)

    # W8: BERT 推理穿透缓存 (独立 db, 与 LLM/嵌入主轨物理隔离, 避免 ~140k 条 _llm_cache.db 混入)。
    # 默认开; deterministic_mode 非严格 (off, 含 AMP/cuDNN benchmark) 时缓存值不可复现 → 自动禁用。
    _BERT_CACHE_ENABLED = (
        bool(BERT_PARAMS.get('inference_cache', True))
        and _DETERMINISTIC_MODE in ('cpu_strict', 'gpu_strict')
    )
    _BERT_CACHE_DB_PATH = CONFIG['paths'].get(
        'local_model_cache_db',
        os.path.join(CONFIG['paths']['output_dir'], '_local_model_cache.db'))
    # AMP 标志进键 (fp16 reduction 非确定 → 不同 AMP 设置不可共享缓存值)
    _BERT_AMP_FLAG = 'amp1' if USE_AMP else 'amp0'


    def _checkpoint_fingerprint(model_path: str) -> str:
        """checkpoint 权重身份指纹: 对 model_path 下权重文件 (safetensors/bin/config)
        的 (相对名, 字节大小, mtime_ns) 排序后哈希 — 不读全部权重字节 (避免 GB 级 I/O),
        以"文件清单+大小+mtime"近似身份。权重换版 ⇒ 指纹变 ⇒ 缓存自动 silent-miss。
        无法 stat (异类路径) → 退化为 'no-ckpt:'+model_path (保守: 永不跨权重共享)。"""
        try:
            h = hashlib.sha256()
            names = []
            for root, _dirs, files in os.walk(model_path):
                for fn in files:
                    if fn.endswith(('.safetensors', '.bin', '.json')):
                        fp = os.path.join(root, fn)
                        st = os.stat(fp)
                        names.append((os.path.relpath(fp, model_path), st.st_size, st.st_mtime_ns))
            if not names:
                return f"no-ckpt:{model_path}"
            for rel, sz, mt in sorted(names):
                h.update(f"{rel}\t{sz}\t{mt}\n".encode())
            return h.hexdigest()
        except Exception:
            return f"no-ckpt:{model_path}"
    ```

  - `pipeline/sentiment/tone_berts.py:557-570` (load_all 内, 记录 loaded_configs 处) — **锚点(当前真实代码)**:
    ```python
    self.models[short_name] = model
    self.tokenizers[short_name] = tokenizer
    self.loaded_configs[short_name] = {
        **mc,
        'label_map': label_map,
        'num_labels': num_labels,
    }
    loaded_names.append(short_name)
    group_key = (mc['max_length'], _tokenizer_fingerprint(tokenizer))
    ```
    **改为** — 在 `loaded_configs` 里**物化 checkpoint 指纹 + vocab 指纹**（供 run_all_models 构键，避免每篇重算）:
    ```python
    _vocab_fp = _tokenizer_fingerprint(tokenizer)
    self.models[short_name] = model
    self.tokenizers[short_name] = tokenizer
    self.loaded_configs[short_name] = {
        **mc,
        'label_map': label_map,
        'num_labels': num_labels,
        # W8: 缓存键构件 (一次算定, run_all_models 逐篇复用)
        '_vocab_fp': _vocab_fp,
        '_ckpt_fp': _checkpoint_fingerprint(model_path),
    }
    loaded_names.append(short_name)
    group_key = (mc['max_length'], _vocab_fp)
    ```
    ⚠ 锚点修正: 实际 `group_key` 在 line 569，`loaded_configs` 赋值在 line 559-563；上面合并展示。`model_path` 在 line 493 已定义、本作用域可见。

  - `pipeline/sentiment/tone_berts.py:615-799` (run_all_models) — **锚点(当前真实代码)** 关键两段: 入口签名 line 615-633 与逐文章聚合 line 770-797 (产出 `{'label':..., 'probabilities':{ln: round(final_probs[idx].item(), 4) ...}, 'num_windows': e-s}`)。
    **改为** — 在方法**最前面做缓存 get**（命中文本直接出结果、跳过分词+窗口+forward），**聚合产出处做 put**。键构造函数 + get/put 包裹:
    ```python
    @staticmethod
    def _bert_cache_key(short_name, cfg, content: str) -> str:
        """W8 BERT 推理缓存键 (经 LLMCache.make_key, model_id 槽=复合身份串):
        (short_name|max_length|vocab_fp|deterministic_mode|amp_flag|ckpt_fp) 拼成 model_id 槽,
        prompt 槽 = 逐字 content, prompt_version = 'bert-v1'。argmax+round4 离散值吸收 fp 漂移。"""
        model_slot = "|".join([
            short_name, str(cfg['max_length']), cfg.get('_vocab_fp', ''),
            _DETERMINISTIC_MODE, _BERT_AMP_FLAG, cfg.get('_ckpt_fp', ''),
        ])
        return LLMCache.make_key(model_slot, content, prompt_version='bert-v1')

    @torch.inference_mode()
    def run_all_models(self, texts: list) -> dict:
        n_texts = len(texts)
        all_model_results = {}

        # ── W8: 开局缓存 get (按 (model 身份, 逐字 content) 命中即出, 跳过 forward) ──
        cache_hit_idx = {}   # short_name -> {i: result_dict}
        if _BERT_CACHE_ENABLED and getattr(self, '_bert_cache', None) is not None:
            for sn in self._groups_flat_loaded():   # 所有已加载模型名
                cfg = self.loaded_configs[sn]
                hits = {}
                for i, t in enumerate(texts):
                    if isinstance(t, str) and t.strip():
                        c = self._bert_cache.get(
                            self._bert_cache_key(sn, cfg, t)[:0] or  # 占位防 lints
                            self._bert_cache_key(sn, cfg, t), '',
                            prompt_version='bert-v1') if False else None
                        # NOTE: LLMCache.get(model_id, prompt,...); 见下方正确调用
                hits = self._cache_get_track(sn, cfg, texts)
                if hits:
                    cache_hit_idx[sn] = hits

        # （原 Step1-5 逻辑保持不变, 但仅对 "未命中" 的文章做分词/forward —
        #   为最小化 diff 与 golden 风险, 推荐实现 = 仍对全 batch 跑 Step1-5,
        #   仅在末尾用 cache_hit_idx 覆盖命中项 + 对未命中项 put。见下注。）
        ...
    ```
    **实测推荐的最小化、低风险写法**（避免改动 Step1-5 的窗口/排序索引逻辑引入错位风险）—— 在**聚合产出处** (line 788-795) 同时做 get-override 与 put：
    ```python
    # line 770-797 聚合循环改造 (per short_name, per article i):
    for i in range(n_texts):
        s, e = article_spans[i]
        content_i = texts[i]
        # W8 get: 命中即用缓存离散结果, 仍完成本 batch forward 但结果以缓存为准 (字节确定)
        cached = None
        if (_BERT_CACHE_ENABLED and self._bert_cache is not None
                and isinstance(content_i, str) and content_i.strip()):
            raw = self._bert_cache.get(
                self._bert_cache_key(short_name, cfg, content_i), content_i,
                prompt_version='bert-v1')
            if raw is not None:
                cached = json.loads(raw)
        if cached is not None:
            results.append({'label': cached['label'],
                            'probabilities': cached['probabilities'],
                            'num_windows': cached['num_windows']})
            continue
        if s == e:
            results.append(self._empty_result(short_name))
            continue
        article_logits = all_logits_cpu[s:e]
        probs_per_window = F.softmax(article_logits, dim=-1)
        confidences = probs_per_window.max(dim=-1).values
        weight_sum = confidences.sum()
        weights = (confidences / weight_sum) if weight_sum > 0 else (torch.ones(e - s) / (e - s))
        final_probs = F.softmax(weights @ article_logits, dim=-1)
        predicted_idx = final_probs.argmax().item()
        res = {
            'label': label_map.get(predicted_idx, f"类别{predicted_idx}"),
            'probabilities': {ln: round(final_probs[idx].item(), 4)
                              for idx, ln in label_map.items() if idx < len(final_probs)},
            'num_windows': e - s,
        }
        results.append(res)
        # W8 put: 仅缓存真实推理 (num_windows>=1) 的离散结果
        if (_BERT_CACHE_ENABLED and self._bert_cache is not None
                and isinstance(content_i, str) and content_i.strip()):
            self._bert_cache.put(
                self._bert_cache_key(short_name, cfg, content_i), content_i,
                json.dumps(res, ensure_ascii=False), prompt_version='bert-v1')
    ```
    并在 `__init__` (line 434-446) 补 `self._bert_cache = None`，在 `load_all` 末尾或 `main()` 打开:
    ```python
    # __init__:
    self._bert_cache = None
    # main() (line ~1212 engine.load_all() 后):
    if _BERT_CACHE_ENABLED:
        engine._bert_cache = LLMCache(_BERT_CACHE_DB_PATH)
    ...
    # main() 末尾 (engine.unload_all() 前后):
    if getattr(engine, '_bert_cache', None) is not None:
        engine._bert_cache.close()
    ```
    ⚠ 上面伪代码第一段含占位噪声 (`if False`)，**正式实现以"聚合产出处 get-override + put"这一最小化写法为准**；它不动 Step1-5 窗口索引，缓存只在最后一公里覆盖/落盘，错位风险最低。

  - `config/sentiment.yaml:267` (tone_berts 块) — **锚点(当前真实代码)**:
    ```yaml
    tone_berts:
      inference_batch_size: 128
      ...
      deterministic_mode: cpu_strict
      ...
      strict_models: true
    ```
    **改为** — 新增开关:
    ```yaml
    tone_berts:
      inference_batch_size: 128
      # W8: BERT 推理穿透缓存 (独立 _local_model_cache.db); 仅 deterministic_mode 为
      # cpu_strict/gpu_strict 时生效 (off 模式含 AMP/cuDNN benchmark 不可复现, 代码强制禁用)。
      inference_cache: true
      ...
    ```

  - `config/paths.yaml:7` 附近 — **锚点(当前真实代码)** `output_dir: ./data/processed`。**改为** 新增（可选，缺省由代码 fallback 兜底，**保持向后兼容默认空**）:
    ```yaml
      # W8: BERT 推理缓存独立库 (与 _llm_cache.db 物理隔离); 缺省则代码取 output_dir/_local_model_cache.db
      local_model_cache_db: ./data/processed/_local_model_cache.db
    ```

- **新增测试**: `tests/test_23_tone_berts.py` 新增类 `TestBertInferenceCache`:
  - `test_cache_key_includes_all_dims`: 改任一构件 (`short_name`/`max_length`/`_vocab_fp`/`deterministic_mode`/AMP/`_ckpt_fp`/`content`) → 键变；全同 → 键不变（直调 `_bert_cache_key` + 伪 cfg）。
  - `test_cache_round_trip_byte_equal`: 用 tmp_path `LLMCache`，put 一个 `{'label':'正面','probabilities':{'正面':0.9876,'中性':0.0124,'负面':0.0},'num_windows':2}` → get + json.loads 后逐字段相等（验证 round4 离散值字节级往返无损）。
  - `test_cache_disabled_when_mode_off`: monkeypatch `_DETERMINISTIC_MODE='off'` 重载模块 → `_BERT_CACHE_ENABLED is False`。
  - `test_run_all_models_uses_cache`: monkeypatch engine 持 fake model（确定 logits），第一次 run 后 `_bert_cache.size()>0`；第二次 run 同文本，断言两次 `results` 完全相等且第二次 forward 被跳过（用计数器/spy 验证 cache get 命中）。
  - `test_source_lock_argmax_round4_discretized`: 源码断言 put 的值经 `json.dumps`、含 `round(` 的 probabilities（最安全离散化锚点不退化）。

- **验收**:
  - `pytest news_process/tests/test_23_tone_berts.py -v`。
  - 受控首跑: `PYTHONHASHSEED=0 MKL_NUM_THREADS=1 OMP_NUM_THREADS=1 HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 python news_process/23_tone_berts.py` → `_local_model_cache.db` 生成、`23_tone_berts.log` 末尾 hit-rate 摘要 misses>0。
  - 第二次同环境跑 → hit-rate≈1.0 且耗时显著下降；`md5sum data/processed/23_bert_tone.parquet` 两跑一致（round4 离散 → 即使 BLAS 抖动也不改产物）。
  - golden: 受控环境 `generate_golden_snapshot.py` + `pytest tests/integration/test_panel_reproducibility.py`（BERT 列入面板，须并入 DEFERRED 批与 W7 统一重生）。

- **风险/开放问题**:
  - **W5 通用 skip 关系（须明确降级建议）**: 若集群通用项 W5（"stage 整体 content-hash skip / 上游未变即整阶段跳过"）已落地，则 stage 23 整体在上游 `22_words_tone.parquet` 未变时根本不重跑 → W8 的"跨 run 命中"边际收益**主要降为单 stage 调试/部分重跑场景**（如只改 config 的某一模型、或手动 `python 23_tone_berts.py` 反复迭代）。**建议**: 若 W5 已落地，W8 **降级为可选**（`inference_cache: false` 默认关，仅调试时开），理由是 ① 维护一个独立 sqlite db 的复杂度 vs 全量重跑已被 W5 拦截；② BERT 全量 forward 是本地 GPU $0，缓存省的是时间而非钱，重要性低于 LLM/嵌入缓存。**但即便降级仍建议保留键设计与 round4 离散契约**（单 stage 反复调试时 ~297s→秒级，开发体验收益实在）。若 W5 **未**落地，W8 保持默认开（跨 run/部分重跑都受益）。
  - **checkpoint 指纹用 mtime**: `git checkout`/重新下载权重会改 mtime → 误失效（保守安全，宁可多算不可误命中）；若团队 CI 频繁重拉权重导致缓存常失效，可降级为只用 (相对名, 字节大小) 不含 mtime。
  - **argmax 边界翻转**: round4 缓存的是**已 argmax 的 label**；若某篇两类概率极接近（如 0.50001/0.49999），历史 BLAS 抖动可能在不同 run 取不同 argmax → 缓存冻结**首跑的那一个**。这正是 needs-regen 而非 safe 的原因，但冻结后比"每 run 重抖"更稳（与 stage 21 LLM 缓存同哲学）。
  - **db 体积**: BERT 缓存值仅 ~120 字节/条（label+3 概率+windows），N×3 模型×3 轨 → N=1.1k 时 ~1MB，可忽略；独立 db 避免污染 453MB 的 `_llm_cache.db`，便于单独删/重生。

---

### 跨 W7/W8 一致性备注（供集群对账）
- **缓存库分治决策**: W7 复用 `_llm_cache.db`（SBERT 与 text2vec 同属嵌入族，model_id 前缀隔离，与 policy_alignment 同库惯例一致）；W8 用**独立** `_local_model_cache.db`（BERT 分类值是异类负载，物理隔离便于单独删/重生、不污染 LLM 确定性锚点）。两者均不动 stage 21 的 `_llm_cache.db` LLM 投票条目。
- **离线守卫**: W7/W8 均为本地推理（无 API），`NEWS_PROCESS_LLM_OFFLINE` 守卫不直接管辖；但缓存 miss 时 W7/W8 仍只做**本地 $0** forward（非付费），故离线安全。建议在两 stage 首跑播种后，把"BERT/SBERT 缓存全命中"纳入 `verify_stage21_cache_coverage` 同款离线复现验证脚本族。
- **golden 统一**: W7+W8 均 needs-regen，须与 CLAUDE.md 顶部 `_allv`/inject-fintech/rule-ablation 既有 **DEFERRED 批**一次合并受控重生（PYTHONHASHSEED=0 + 全 BLAS 线程=1 + 保留 GPU + HF offline），避免本机裸环境误 bless 无关漂移列。

---

<a id="集群-e-withinstage"></a>

I have all the grounding I need. Producing the spec now.

## 集群 E — W9 (MinHash 签名持久化, safe) + W10 (词典 powerset 单次扫描重构, needs-regen)

### W9 · MinHash 签名内容寻址 sidecar 缓存 (datasketch 版本入键)
- **目标**: 给 `compute_minhashes` 加可选内容寻址 sidecar (parquet), 让 dedup 阈值敏感性 (stage 62) 跨 run 复用已算签名, 只省 CPU 不引入任何非确定性。
- **golden 影响**: safe (签名确定 → 缓存命中=逐位等价 miss; sidecar 是 validation 旁路产物, 不进 OUTPUT_REGISTRY / golden panel)。
- **逐文件改动**:

  - `pipeline/preprocess/dedup.py:292` — **锚点(当前真实代码)**:
    ```python
    def compute_minhashes(self, df: pd.DataFrame) -> pd.Series:
        """Step 1: 并行生成 MinHash 签名 (索引 → MinHash 的 Series).

        签名只依赖文本与 (num_perm, ngram_size), **不依赖** Jaccard 阈值/时间窗口
        ...
        前置: df 须已经 ``_prepare_dataframe`` (依赖 COL_COMBINED 列)。
        """
        self.logger.info(
            f"生成 MinHash 签名({self.num_perm} 个置换, "
            f"{nb_workers} 个工作进程)..."
        )
    ```
    **改为** (新增可选 `cache_dir` 形参 + 内容寻址命中短路; 默认 `None` → 行为逐位不变, 向后兼容所有现有调用):
    ```python
    def compute_minhashes(
        self, df: pd.DataFrame, cache_dir: str | None = None,
    ) -> pd.Series:
        """Step 1: 并行生成 MinHash 签名 (索引 → MinHash 的 Series).

        签名只依赖文本与 (num_perm, ngram_size), **不依赖** Jaccard 阈值/时间窗口
        ...
        前置: df 须已经 ``_prepare_dataframe`` (依赖 COL_COMBINED 列)。

        W9 (2026-06-25): 传入 ``cache_dir`` 时启用【内容寻址 sidecar 缓存】。
        缓存键 = sha256(datasketch 版本 | num_perm | ngram_size | 语料快照哈希)。
        签名是确定性纯函数 → 缓存命中读回的签名与重算逐位等价 (仅省 CPU,
        不引入非确定性, golden-safe)。datasketch 版本入键 = 版本门: 升级
        datasketch (banding/permutation 实现可能变) 自动失效重算。cache_dir=None
        (默认) → 完全走旧路径 (生产 stage 00 不传, 行为逐位不变)。
        """
        if cache_dir is not None:
            cached = self._load_minhash_sidecar(df, cache_dir)
            if cached is not None:
                return cached
        self.logger.info(
            f"生成 MinHash 签名({self.num_perm} 个置换, "
            f"{nb_workers} 个工作进程)..."
        )
    ```
    并在函数尾部 `return pd.Series(minhash_results)` (当前 `:335`) 前插入回写:
    ```python
    #   ── 锚点 (当前 :335) ──
    #   return pd.Series(minhash_results)
    #   ── 改为 ──
    sig = pd.Series(minhash_results)
    if cache_dir is not None:
        self._write_minhash_sidecar(df, sig, cache_dir)
    return sig
    ```

  - `pipeline/preprocess/dedup.py` — **新增三个私有方法** (插在 `compute_minhashes` 之后, `find_near_duplicate_indices` 之前 `:336`)。键的构造直接复用项目既有 SSOT 模式 `core/data_versioning.py::compute_config_hash` (见 `:67`, `json.dumps(sort_keys=True)+sha256`); 序列化用 datasketch 自身的 `MinHash.hashvalues` (uint64 ndarray, 确定性) 落 parquet, 而非 pickle (pickle 跨版本不稳, 违反"版本门"语义):
    ```python
    def _minhash_cache_key(self, df: pd.DataFrame) -> str:
        """W9 内容寻址键: sha256(datasketch版本 | num_perm | ngram_size | 语料快照哈希)。

        语料快照哈希 = COL_COMBINED 列文本逐行拼接的 sha256 (顺序敏感 — 与 Series
        index/顺序绑定, 因为签名按 df.index 收集)。datasketch 版本入键做版本门:
        换 datasketch (permutation/banding 实现可能漂移) → 键变 → 自动重算。
        """
        import hashlib
        from datasketch import __version__ as _ds_ver
        h = hashlib.sha256()
        # 顺序敏感: 逐行喂 (index 字符串 + \x00 + 文本 + \x01), 防拼接歧义
        for idx, txt in df[self.COL_COMBINED].items():
            h.update(str(idx).encode('utf-8'))
            h.update(b'\x00')
            h.update(('' if txt is None else str(txt)).encode('utf-8'))
            h.update(b'\x01')
        corpus_hash = h.hexdigest()
        from news_process.core.data_versioning import compute_config_hash
        return compute_config_hash({
            'datasketch_version': _ds_ver,
            'num_perm': int(self.num_perm),
            'ngram_size': int(self.ngram_size),
            'corpus_sha256': corpus_hash,
        })

    def _load_minhash_sidecar(self, df: pd.DataFrame, cache_dir: str) -> "pd.Series | None":
        """命中 → 反序列化为 {index: MinHash}; 未命中/损坏/版本不符 → None (回退重算)。"""
        key = self._minhash_cache_key(df)
        path = os.path.join(cache_dir, f'minhash_{key}.parquet')
        if not os.path.isfile(path):
            return None
        try:
            from datasketch import MinHash as _MinHash
            tbl = pd.read_parquet(path)  # 列: index, hashvalues(list[uint64])
            out = {}
            for row in tbl.itertuples(index=False):
                m = _MinHash(num_perm=self.num_perm,
                             hashvalues=np.asarray(row.hashvalues, dtype=np.uint64))
                out[row.index] = m
            self.logger.info(
                f"MinHash sidecar 命中: {os.path.basename(path)} "
                f"({len(out):,} 签名, 跳过重算)"
            )
            return pd.Series(out)
        except Exception as e:  # noqa: BLE001
            self.logger.warning(f"MinHash sidecar 读取失败 (回退重算): {e}")
            return None

    def _write_minhash_sidecar(self, df: pd.DataFrame, sig: pd.Series,
                               cache_dir: str) -> None:
        """把 {index: MinHash} 落 parquet sidecar (fail-soft: 写失败仅 warning)。"""
        try:
            os.makedirs(cache_dir, exist_ok=True)
            key = self._minhash_cache_key(df)
            path = os.path.join(cache_dir, f'minhash_{key}.parquet')
            tbl = pd.DataFrame({
                'index': list(sig.index),
                # MinHash.hashvalues 是 uint64 ndarray, 确定性; 转 list 落 parquet
                'hashvalues': [m.hashvalues.tolist() for m in sig.to_numpy()],
            })
            tbl.to_parquet(path, index=False)
            self.logger.info(f"MinHash sidecar 已落盘: {path} ({len(sig):,} 签名)")
        except Exception as e:  # noqa: BLE001
            self.logger.warning(f"MinHash sidecar 写入失败 (不影响去重): {e}")
    ```

  - `validation/dedup_threshold.py:383` — **锚点(当前真实代码)**:
    ```python
    logger.info("计算 MinHash 签名 (一次, 全部阈值共用; 签名与阈值无关)...")
    mh_start = time.time()
    minhashes = dedup.compute_minhashes(df_exact)
    mh_elapsed = time.time() - mh_start
    ```
    **改为** (这是 W9 的唯一复用点 — stage 62 全量语料上 MinHash 是分钟级多进程重负载, 跨 run 复用此处一次性的签名即省全部成本; 把 sidecar 放在 `_cache` 同级的 `_minhash_cache/` 下):
    ```python
    logger.info("计算 MinHash 签名 (一次, 全部阈值共用; 签名与阈值无关)...")
    mh_start = time.time()
    # W9 (2026-06-25): 内容寻址 sidecar — pre_dedup_cache 口径下跨 run 复用签名。
    # 仅当输入是去重前缓存口径时启用 (回退口径输入随上游漂移, 缓存意义有限)。
    _mh_cache_dir = (
        os.path.join(output_dir, '_minhash_cache')
        if input_mode == 'pre_dedup_cache' else None
    )
    minhashes = dedup.compute_minhashes(df_exact, cache_dir=_mh_cache_dir)
    mh_elapsed = time.time() - mh_start
    ```

- **新增测试**: `tests/test_dedup_minhash_sidecar.py` —
  - `test_sidecar_roundtrip_bitwise_equal`: 同一 df, 一次 `compute_minhashes(df, cache_dir=tmp)` (写) + 一次 (读命中), 断言两次返回 Series 的每个 MinHash `.hashvalues` 用 `np.array_equal` 逐位相等; 且与 `compute_minhashes(df)` (无缓存) 也逐位相等。
  - `test_sidecar_key_includes_datasketch_version`: monkeypatch `datasketch.__version__` 改值 → `_minhash_cache_key` 返回不同 key → 旧 sidecar 不命中 (版本门生效)。
  - `test_sidecar_corrupt_falls_back`: 写一个非法 parquet 占位文件 → `_load_minhash_sidecar` 返回 None, 主流程重算不崩。
  - `test_cache_dir_none_unchanged`: `cache_dir=None` 路径与无参调用产出逐位一致 (向后兼容)。
  - 复用 `tests/test_dedup_sensitivity.py::test_default_params_equal_production_method` (`:87`) 的 `near_dup_df` fixture 不变 → 证明 sidecar 不破坏 `_perform_near_deduplication == compute_minhashes + find` 锚点。

- **验收**:
  - `pytest tests/test_dedup_minhash_sidecar.py tests/test_dedup_sensitivity.py -v` 全绿。
  - `pytest tests/integration/test_dag_consistency.py` 不受影响 (无 StageSpec/OUTPUT_REGISTRY 变更)。
  - `ruff check news_process/pipeline/preprocess/dedup.py news_process/validation/dedup_threshold.py` clean。
  - 手测: 同一 `_cache` 跑两遍 `python -m news_process.validation.dedup_threshold`, 第二遍日志出现 `MinHash sidecar 命中`, 两次 `dedup_sensitivity_report.csv` 的 `Dropped`/`Retained` 逐列相等。

- **风险/开放问题**:
  - `MinHash(hashvalues=...)` 重建依赖 datasketch 接受外部 hashvalues 且保持相同 `num_perm`/seed 语义 — datasketch 1.x 支持该构造签名, 但**升级 datasketch 时必须人工复核**重建 MinHash 的 `.jaccard()`/LSH 行为是否与 `update_batch` 路径一致 (这正是版本入键的理由, 不一致时键已变会重算)。
  - sidecar parquet 的 `hashvalues` 列是 `list[int]` (parquet 落为 int64); 重建时 `np.asarray(..., dtype=np.uint64)` 须确认无符号回绕 — uint64 值 > 2^63 经 parquet int64 往返会变负, **改为以 bytes 或 uint64 ndarray 直接写更安全**: 落盘改 `m.hashvalues.astype('<u8').tobytes()` 存 binary 列, 读回 `np.frombuffer(b, dtype='<u8')`。规格里 list 版仅作可读骨架, 实现应采用 bytes 版避免 uint64 溢出 (列为审阅标注的开放点)。
  - 语料快照哈希遍历全 ~385 万行文本算一遍 sha256 (单线程 ~数秒), 远小于 MinHash 多进程重算成本, 净收益正; 但若担心该 sha256 也成瓶颈, 可改采样/行数+前后缀指纹 (当前规格取全量精确, 优先正确性)。

---

### W10 · `_compute_sentiment_with_rules` 重构为「单次扫描中间表 + 8 powerset reduce」
- **目标**: 把每词典 8 次全 token 状态机循环 (1 主 `{dict}_score` + 7 个 `_RULE_ABLATION_VARIANTS`) 降到 1 次扫描产中间表 + 8 次纯算术 reduce, 保持逐位等价。
- **golden 影响**: needs-regen (重构后 `{dict}_score` / `{dict}_score_{sfx}` 列须经真机字节级等价测试确认与旧值逐位一致; 因落在 v3.11.1 已 DEFERRED 的 golden 重生批内, 实际并入统一重生)。**ROI 中等** — stage 22 ~92s 非全流水线最慢 (stage 23 BERT 297s / 25 SBERT 107s 更慢), 本重构把 stage 22 词典扫描的 8× 全 token 遍历降到 1× 扫 + 8× 廉价 reduce。

- **逐文件改动**:

  - `pipeline/sentiment/tone_words.py:1407` — **锚点(当前真实代码, 8 次循环的消费侧)**:
    ```python
    raw_score, norm_score, pos_cnt, neg_cnt, matched = \
        _compute_sentiment_with_rules(tokens, sentiment_dict, both_sided_words=_bs)

    result[f'{dict_name}_score'] = round(norm_score, 4)
    result[f'{dict_name}_label'] = _score_to_label(norm_score)
    ...
    for _abl_sfx, _abl_neg, _abl_deg, _abl_adv in _RULE_ABLATION_VARIANTS:
        _, _abl_norm, _, _, _ = _compute_sentiment_with_rules(
            tokens, sentiment_dict,
            apply_negation=_abl_neg, apply_degree=_abl_deg, apply_adversative=_abl_adv,
            both_sided_words=_bs)
        result[f'{dict_name}_score_{_abl_sfx}'] = round(_abl_norm, 4)
    ```
    现状: 对同一 `tokens` × `sentiment_dict` 调用 `_compute_sentiment_with_rules` **8 次** (1 full + 7 变体), 每次都重新跑整个 token 状态机。
    **改为** (1 次扫描产中间表 + 8 次 reduce; full = `(T,T,T)` 也从同一中间表 reduce, 与现有 `{dict}_score` 逐位一致):
    ```python
    # W10 (2026-06-25): 单次扫描产中间表 → 8 powerset 纯算术 reduce (替代 8× 全 token 扫)。
    # full=(T,T,T) 与 7 变体共用同一中间表; 各 reduce 仍各自 Σ|final| 自归一化, 输出逐位等价。
    _trace = _scan_sentiment_trace(tokens, sentiment_dict, both_sided_words=_bs)
    norm_score, pos_cnt, neg_cnt = _reduce_trace(_trace, True, True, True)  # full
    result[f'{dict_name}_score'] = round(norm_score, 4)
    result[f'{dict_name}_label'] = _score_to_label(norm_score)
    ...
    for _abl_sfx, _abl_neg, _abl_deg, _abl_adv in _RULE_ABLATION_VARIANTS:
        _abl_norm, _, _ = _reduce_trace(_trace, _abl_neg, _abl_deg, _abl_adv)
        result[f'{dict_name}_score_{_abl_sfx}'] = round(_abl_norm, 4)
    ```
    > ⚠ 锚点修正: 现 `{dict}_score` 经 `_compute_sentiment_with_rules(..., both_sided_words=_bs)` (全规则=默认 `apply_*=True`) 得 `norm_score`; 重构后须用 `_reduce_trace(_trace, True, True, True)` 复刻同一 `(T,T,T)` 路径, 且 `pos_cnt/neg_cnt` 仍来自 full reduce (供 `:1421` 的 `{dict}_pos_ratio`/`neg_ratio`)。

  - `pipeline/sentiment/tone_words.py:598-779` — **锚点(当前真实代码, 状态机本体)**: 见上文 Read 的 `_compute_sentiment_with_rules` (单次循环里 `apply_negation`/`apply_degree`/`apply_adversative` 三个 flag 同时 gate 翻号/倍率/boost)。
    **改为** — 拆成两段。**保留 `_compute_sentiment_with_rules` 原签名/原行为不动** (union/idf/msent_negonly 等 4 处调用 `:1434`/`:1509`/`:1526` 仍用它, 且测试锚定; 它内部改成 `_scan + _reduce` 的薄包装以彻底单一事实源)。**新增** `_scan_sentiment_trace` (单次扫描产中间表) 与 `_reduce_trace` (纯算术 reduce):

    ① 新增 `_scan_sentiment_trace` — 一次 token 状态机扫描, 对**每个命中情感词**产一条中间记录。关键洞察 (来自真实代码 `:714`/`:718`/`:724`): 三规则对 `final` 的作用都是确定性可分解的 —
      - `apply_negation` 仅 gate 是否 `base = -base` (`:714-715`), 等价于乘 sign∈{+1,-1};
      - `apply_degree` 仅 gate `degree_multiplier` 取 `DEGREE_WORDS[token]` 还是 `1.0` (`:702-703`), 但**否定窗口/句末重置骨架与 flag 无关**, 故扫描时记录"该词命中时积累的程度倍率 `deg_mult`"(始终按真实 DEGREE_WORDS 取值, flag 在 reduce 期再选用不用);
      - `apply_adversative` 仅 gate 是否乘 `ADVERSATIVE_BOOST` (`:724-725`), 记录命中时 `in_adv` 布尔;
      - `negation_remaining>0` 是否触发翻号, 记录命中时 `in_neg` 布尔。

      ⚠ 铁律 (锚点 `:697-701`/`:721-723` docstring): degree/adversative/negation 的**识别 + continue + 窗口递减 scoping 骨架与 flag 无关**, 三规则共享同一 scoping。因此扫描时 scoping 用**真实值** (degree token 始终设 `degree_multiplier=DEGREE_WORDS[token]`, negation 始终设窗口, adversative 始终 reset) — 与 reduce 期的 flag 完全解耦, 这正是单次扫描可服务全 8 变体的数学前提。
    ```python
    def _scan_sentiment_trace(
        tokens: list[str], sentiment_dict: dict[str, float],
        both_sided_words: frozenset[str] = frozenset(),
    ) -> list[dict]:
        """W10: 单次 token 状态机扫描 → 每命中词的中间表 (供 _reduce_trace 算术 reduce)。

        scoping 骨架 (否定窗口 / 句末重置 / 句末重置程度) 始终按真实值推进, **与三规则
        flag 解耦** — flag 只在 reduce 期决定是否消费 sign/degree/adv (铁律: 三规则共享
        同一 scoping, 见 _compute_sentiment_with_rules docstring 方案 a)。
        每条记录字段:
          base        : 原始词典极性值 sentiment_dict[token]
          neg_sign    : -1 若命中时 negation_remaining>0 else +1 (翻号系数)
          deg_mult    : 命中时积累的程度倍率 (真实 DEGREE_WORDS 值, ≥1.0)
          in_adv      : 命中时是否处于转折后区域 (bool)
          both_sided  : token ∈ both_sided_words (两侧计数标记)
        """
        trace: list[dict] = []
        negation_remaining = 0
        degree_multiplier = 1.0
        adversative_active = False
        for token in tokens:
            if token in SENTENCE_END_MARKERS:
                adversative_active = False
                negation_remaining = 0
                degree_multiplier = 1.0
                continue
            if token in ADVERSATIVE_WORDS:
                adversative_active = True
                degree_multiplier = 1.0
                negation_remaining = 0
                continue
            if token in NEGATION_WORDS:
                negation_remaining = NEGATION_WINDOW
                continue
            if token in DEGREE_WORDS:
                degree_multiplier = DEGREE_WORDS[token]  # 始终真实值 (flag 在 reduce 选用)
                continue
            if token in sentiment_dict:
                trace.append({
                    'base': sentiment_dict[token],
                    'neg_sign': -1.0 if negation_remaining > 0 else 1.0,
                    'deg_mult': degree_multiplier,
                    'in_adv': adversative_active,
                    'both_sided': token in both_sided_words,
                })
                degree_multiplier = 1.0  # 已消费程度副词
            else:
                degree_multiplier = 1.0
            if negation_remaining > 0:
                negation_remaining -= 1
        return trace
    ```

    ② 新增 `_reduce_trace` — 纯算术从中间表算 `(normalized_score, pos_count, neg_count)`。须**逐条复刻**真实代码 `:707-768` 的 final 计算顺序 (否定翻号→乘 degree→乘 adv boost→both_sided 双计) 以保证逐位等价:
    ```python
    def _reduce_trace(
        trace: list[dict], apply_negation: bool, apply_degree: bool,
        apply_adversative: bool,
    ) -> tuple[float, int, int]:
        """W10: 从 _scan_sentiment_trace 中间表纯算术 reduce 出 (norm_score, pos, neg)。

        逐条复刻 _compute_sentiment_with_rules 的 final 计算顺序 (否定翻号 → ×degree →
        ×ADVERSATIVE_BOOST → both_sided 双计 net0/分母+2|final|), 三 flag 决定是否消费
        对应数值效应 → 8 powerset 组合各自 Σ|final| 自归一化, 逐位等价 8× 全 token 扫。
        """
        total_score = 0.0
        total_abs_score = 0.0
        pos_count = 0
        neg_count = 0
        for r in trace:
            base = r['base']
            if apply_negation:
                base = base * r['neg_sign']       # neg_sign∈{+1,-1}, 复刻 base=-base
            final = base * (r['deg_mult'] if apply_degree else 1.0)
            if apply_adversative and r['in_adv']:
                final *= ADVERSATIVE_BOOST
            if r['both_sided']:
                mag = abs(final)
                total_abs_score += 2.0 * mag
                pos_count += 1
                neg_count += 1
                continue
            total_score += final
            total_abs_score += abs(final)
            if final > 0:
                pos_count += 1
            elif final < 0:
                neg_count += 1
        norm = total_score / total_abs_score if total_abs_score > 0 else 0.0
        return norm, pos_count, neg_count
    ```
    > ⚠ **逐位等价关键点 (审阅必看)**: 旧代码 `base_score = -base_score` (`:715`) 后 `final = base_score * degree_multiplier` (`:718`)。新代码 `base * r['neg_sign']` 必须保证 `r['neg_sign']` 是精确 `±1.0` (float, 非 int), 使 `-base == base * (-1.0)` 在 IEEE754 下逐位相等 (对 ±0.0 也成立: `-0.0` vs `0.0 * -1.0 = -0.0` ✓)。`deg_mult` 直接乘, 与旧 `degree_multiplier` 同序; `ADVERSATIVE_BOOST` 同一全局常量同序乘 — 三步乘法顺序与旧码字字对应 → 浮点结果逐位一致。

    ③ 把 `_compute_sentiment_with_rules` 改为 `_scan + _reduce` 的薄包装 (彻底单一事实源, 保留旧签名供 union/idf/msent_negonly 4 处调用 + 锚定测试; `raw_score`/`matched_words` 仍需 → 在包装层补算)。**锚点(当前 `:665-779` 整段循环体)** 替换为:
    ```python
    # ── W10 (2026-06-25): 改为单次扫描中间表 + reduce 的薄包装 (单一事实源) ──
    trace = _scan_sentiment_trace(tokens, sentiment_dict, both_sided_words=both_sided_words)
    normalized_score, pos_count, neg_count = _reduce_trace(
        trace, apply_negation, apply_degree, apply_adversative)
    # raw_score (Σfinal, 未归一) 与 matched_words 仍由调用方 (union 口径 msent/details) 消费,
    # 从同一 trace + flag 重建 (逐条复刻 final 与 matched 记录顺序, 与旧 :749-764 字节一致)。
    total_score = 0.0
    matched_words: list[dict[str, Any]] = []
    for r in trace:
        base = r['base'] * r['neg_sign'] if apply_negation else r['base']
        final = base * (r['deg_mult'] if apply_degree else 1.0)
        if apply_adversative and r['in_adv']:
            final *= ADVERSATIVE_BOOST
        if r['both_sided']:
            mag = abs(final)
            _bm = abs(r['base'])
            matched_words.append({'word': '', 'base': _bm, 'final': round(mag, 4),
                                  'boosted': r['in_adv']})
            matched_words.append({'word': '', 'base': -_bm, 'final': round(-mag, 4),
                                  'boosted': r['in_adv']})
            continue
        total_score += final
        matched_words.append({'word': '', 'base': r['base'], 'final': round(final, 4),
                              'boosted': r['in_adv']})
    return total_score, normalized_score, pos_count, neg_count, matched_words
    ```
    > ⚠ **锚点修正/开放问题 — `matched_words['word']`**: 旧 `matched_words` 记录含真实 `token` 字符串 (`:740`/`:759-760`); 但下游消费 (`_analyze_single_article :1438-1440` top_detail 仅按 `abs(x['final'])` 排序取 base/final; `:1491-1492` msent 仅看 `m['base']` 符号) **均不读 `'word'` 字段**。为让 `_scan_sentiment_trace` 不必额外存 token (省内存), 中间表可不带 token → 包装层 `'word'` 置 `''`。**这会改变 `sentiment_details` JSON 里 `word` 字段值** (旧=真实词, 新='')。若 `sentiment_details` 列入 golden/下游, 必须在 trace 里**额外记录 `'token'` 字段**并在包装层填回 — 规格默认保留 token (中间表加 `'token': token` 字段, 包装层 `'word': r['token']`) 以零行为变更; 上方骨架的 `''` 仅为最小内存版示意, **审阅时按"保留 token"落地** (这是唯一可能破坏字节等价的点, 必须人工拍板)。

- **新增测试**: `tests/test_rule_ablation_ladder.py` 内追加 (复用既有 ablation fixture) 或新建 `tests/test_tone_words_scan_reduce_equiv.py` —
  - `test_scan_reduce_bitwise_equals_legacy`: 对一组覆盖否定/程度/转折/both_sided/句末重置/否定窗口边界的 token 序列, 断言重构后 `_compute_sentiment_with_rules(...)` 对全 8 个 flag 组合 (含 full `(T,T,T)`) 的 `(raw_score, normalized_score, pos, neg)` 与重构前**逐位** (`==`, 含 float `repr` 相等, 非 `pytest.approx`) 一致。基线值用 git stash/旧实现快照硬编码进测试。
  - `test_score_columns_byte_identical`: 跑 `_analyze_single_article` 取所有 `{dict}_score` + `{dict}_score_{sfx}` 列, 与旧实现输出 dict 逐键 `==`。
  - `test_msent_negonly_unchanged` / `test_union_path_unchanged`: union (`:1434`) + msent_negonly (`:1509`) + idf (`:1526`) 三处调用结果不变 (它们仍走 `_compute_sentiment_with_rules` 包装)。
  - `test_both_sided_net_zero`: both_sided 词 reduce 后对 `total_score` 净 0、对分母 `+2|final|`、pos/neg 各 +1 (复刻 `:727-747` 语义)。
  - **真机字节级等价**: 受控环境 (`PYTHONHASHSEED=0`) 跑 stage 22 全量 → 对 `22_words_tone.parquet` 的 `*_score*` 列与重构前产物做 `pandas` 逐元素 `equals` (非 approx)。

- **验收**:
  - `pytest tests/test_rule_ablation_ladder.py tests/test_22_tone_words.py tests/test_omni_fix_tonewords.py tests/test_omni_fix_val_tone.py -v` 全绿。
  - `ruff check news_process/pipeline/sentiment/tone_words.py` clean。
  - 真机: 受控环境跑 `python news_process/22_tone_words.py` 前后, `22_words_tone.parquet` 全 `*_score*` 列 `df_new.equals(df_old)` 为 True (字节级)。
  - 计时对照: 同语料 stage 22 墙钟应**下降** (8× token 扫 → 1× 扫 + 8× reduce); 记录 before/after 进 log 供 ROI 核验 (期望从 ~92s 下降, 但因非最慢阶段, ROI 标注中等)。

- **风险/开放问题**:
  - **逐位等价是硬约束**: 任何浮点运算顺序差异 (尤其 `-base` vs `base*-1.0`、`deg_mult`/`ADVERSATIVE_BOOST` 乘序) 会破坏 golden。规格已把三步乘法严格对齐旧码顺序; 实现后**必须**跑 `test_score_columns_byte_identical` 而非 approx 测试。
  - **`matched_words['word']` 字段** (见上方锚点修正): 默认在中间表保留 `token` 以零行为变更; 若为省内存丢弃 token, 须先确认 `sentiment_details` 列不入 golden / 下游不读 word —— 这是唯一可能引入字节差异的设计点, 列为开放问题交审阅拍板。
  - **内存**: 中间表是 `list[dict]` per 文章 per 词典 (仅命中词, 远小于 token 总数), 扫描后即 reduce 8 次随即释放, 峰值可控; 但 6 词典 × 三轨循环里 trace 是局部变量, 不跨词典累积。
  - golden 重生须与 v3.11.1 已 DEFERRED 的 `_allv`/inject-fintech/rule-ablation 三项**统一消费一次合并重生** (CLAUDE.md 顶部 §11), 不单独为本重构触发付费阶段; 引擎确定性 → 重生 golden-safe。

---

<a id="集群-f-cleanup"></a>

All verified. I have read every anchor in real current code. Now I produce the final spec.

```markdown
## 集群 F-cleanup — W11 (Stata run_do 内容寻址跳过) + W12 (HF 离线 + stage15 走引擎) + W13 (裸编码/legacy 死代码清理)

> 全部三项 golden 影响 = **safe**: W11 不产出 40_panel 任何列 (仅 .do→.log/.dta 编排层); W12 仅切换 HF 模型加载来源 + 复用既有确定性硬化引擎, 数值逐位不变 (镜像已落地的 tone_berts:133 / article_sbert:93 先例); W13 删的是零生产调用的 legacy 函数 + 同步陈旧测试。无任何须 needs-regen 的列变更。

---

### W11 · Stata `run_do` 可选内容寻址跳过 (do内容 + 输入.dta列哈希 + Stata/ado版本指纹)
- **目标**: 给 `run_do` 加可选 `skip_if_unchanged`, 命中且 `.log`/产物已存在则跳过重跑, key 含 Stata 与关键 ado 版本指纹。
- **golden 影响**: safe (Stata 编排层, 不进 `40_panel_*`; 缓存只决定"跑 vs 复用", 不改 .do 输出语义)。
- **逐文件改动**:
  - `papers/_common/stata_runner.py:14-21` — **锚点(当前真实代码)**:
    ```python
    from __future__ import annotations

    import os
    import shutil
    import subprocess
    from pathlib import Path
    from typing import Sequence
    ```
    **改为** (补 stdlib import + 模块级常量, 向后兼容):
    ```python
    from __future__ import annotations

    import hashlib
    import json
    import os
    import shutil
    import subprocess
    from pathlib import Path
    from typing import Sequence

    # W11: run_do 内容寻址跳过的指纹版本号 — 改 key 组成时 bump 以强制全失效。
    _RUNDO_SKIP_VERSION = "v1"
    # 跳过缓存 sidecar 文件名后缀 (与 .do 同目录, 内容寻址 stamp)。
    _RUNDO_STAMP_SUFFIX = ".rundo_stamp.json"
    ```
  - `papers/_common/stata_runner.py:86-93` — **锚点(当前真实代码)**:
    ```python
    def run_do(do_path: str | Path,
               args: Sequence[str] | None = None,
               *,
               stata_bin: str | None = None,
               cwd: str | Path | None = None,
               timeout: int = 1800,
               batch_mode: bool = True,
               check: bool = True) -> subprocess.CompletedProcess:
    ```
    **改为** (新增 4 个 keyword-only 参数, 全部默认 = 关闭 → 现有所有 callsite 行为字节不变):
    ```python
    def run_do(do_path: str | Path,
               args: Sequence[str] | None = None,
               *,
               stata_bin: str | None = None,
               cwd: str | Path | None = None,
               timeout: int = 1800,
               batch_mode: bool = True,
               check: bool = True,
               skip_if_unchanged: bool = False,
               input_dta_paths: Sequence[str | Path] | None = None,
               output_paths: Sequence[str | Path] | None = None,
               ado_packages: Sequence[str] | None = None) -> subprocess.CompletedProcess:
    ```
  - `papers/_common/stata_runner.py:115-128` — **锚点(当前真实代码)**:
    ```python
    do_path = Path(do_path).resolve()
    if not do_path.exists():
        raise FileNotFoundError(f"do 文件不存在: {do_path}")

    bin_path = stata_bin or discover_stata_bin()
    if bin_path is None:
        raise StataNotFoundError(
            "未能定位 Stata 可执行文件. 请通过 stata_bin 参数显式指定, "
            "或设置环境变量 NEWS_PROCESS_STATA_BIN, "
            f"或将以下任一文件加入 PATH: {_candidates()}"
        )

    if cwd is None:
        cwd = do_path.parent
    ```
    **改为** (在解析 `bin_path` 之后、构建 cmd 之前插入跳过逻辑; 跳过判定须先有 `bin_path` 才能取 Stata 版本指纹):
    ```python
    do_path = Path(do_path).resolve()
    if not do_path.exists():
        raise FileNotFoundError(f"do 文件不存在: {do_path}")

    bin_path = stata_bin or discover_stata_bin()
    if bin_path is None:
        raise StataNotFoundError(
            "未能定位 Stata 可执行文件. 请通过 stata_bin 参数显式指定, "
            "或设置环境变量 NEWS_PROCESS_STATA_BIN, "
            f"或将以下任一文件加入 PATH: {_candidates()}"
        )

    if cwd is None:
        cwd = do_path.parent

    # ── W11: 内容寻址跳过 (默认关闭, 显式 opt-in) ──
    # key = sha256(_RUNDO_SKIP_VERSION | do文件内容 | args | 各输入.dta列级哈希 |
    #              Stata 可执行版本指纹 | 关键 ado 包版本指纹)。命中且 .log/产物
    # 全部存在 → 直接 skip 复用 (返回 returncode=0 的合成 CompletedProcess)。
    # ⚠ safe: 仅决定"跑 vs 复用", 不改 .do 输出; Stata/ado 版本入 key 防跨机误命中。
    _stamp_path = do_path.with_suffix(do_path.suffix + _RUNDO_STAMP_SUFFIX)
    _skip_key: str | None = None
    if skip_if_unchanged:
        _skip_key = _compute_rundo_key(
            do_path, args, input_dta_paths, bin_path, ado_packages)
        if _rundo_can_skip(_stamp_path, _skip_key, output_paths):
            return subprocess.CompletedProcess(
                args=['<skipped:rundo-content-addressed>', str(do_path)],
                returncode=0, stdout='', stderr='',
            )
    ```
  - `papers/_common/stata_runner.py:139-146` — **锚点(当前真实代码)**:
    ```python
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        timeout=timeout,
        check=check,
        capture_output=True,
        text=True,
    )
    ```
    **改为** (跑完后写 stamp; 仅当本次显式 opt-in 且退出码 0 时落 stamp, 防把失败跑缓存成"已完成"):
    ```python
    cp = subprocess.run(
        cmd,
        cwd=str(cwd),
        timeout=timeout,
        check=check,
        capture_output=True,
        text=True,
    )
    if skip_if_unchanged and _skip_key is not None and cp.returncode == 0:
        _write_rundo_stamp(_stamp_path, _skip_key, output_paths)
    return cp
    ```
  - `papers/_common/stata_runner.py` (新增私有 helper, 紧跟 `run_do` 之后 ~line 147) — **新代码**:
    ```python
    def _stata_version_fingerprint(bin_path: str) -> str:
        """Stata 可执行版本指纹: 用 exe 文件大小 + mtime + 路径 basename 作廉价指纹。
        (不真启 Stata 探版本 — 启一次 GUI 子系统进程代价高且可能弹框; 升级 Stata
         会改 exe 字节 → size/mtime 变 → key 变, 满足'版本必入 key'要求。)"""
        try:
            st = os.stat(bin_path)
            return f"{os.path.basename(bin_path)}|{st.st_size}|{int(st.st_mtime)}"
        except OSError:
            return f"missing:{os.path.basename(str(bin_path))}"


    def _ado_fingerprint(ado_packages: Sequence[str] | None) -> str:
        """关键 ado 包版本指纹: 对每个包名定位其 .ado 文件 (PLUS/PERSONAL adopath),
        取 (basename, size, mtime) 拼接。找不到 → missing 哨兵。空 → 'none'。"""
        if not ado_packages:
            return 'none'
        parts: list[str] = []
        for pkg in sorted(set(ado_packages)):
            hit = shutil.which(f"{pkg}.ado") or _locate_ado(pkg)
            if hit and os.path.exists(hit):
                st = os.stat(hit)
                parts.append(f"{pkg}:{st.st_size}:{int(st.st_mtime)}")
            else:
                parts.append(f"{pkg}:missing")
        return ';'.join(parts)


    def _locate_ado(pkg: str) -> str | None:
        """在常见 Stata adopath (PLUS / ~/ado/plus) 下找 <pkg>.ado。找不到返回 None。"""
        candidates = []
        home = os.environ.get('USERPROFILE') or os.environ.get('HOME') or ''
        if home:
            candidates.append(os.path.join(home, 'ado', 'plus'))
        for root in candidates:
            for sub in (pkg[0].lower(), pkg[0].upper(), '_'):
                cand = os.path.join(root, sub, f"{pkg}.ado")
                if os.path.exists(cand):
                    return cand
        return None


    def _dta_column_hash(dta_path: str | Path) -> str:
        """输入 .dta 的列级哈希: 读 header 取变量名 + 形状 (不读全表, 廉价)。
        优先 pyreadstat metadata-only; 失败回退 (size, mtime)。"""
        p = Path(dta_path)
        if not p.exists():
            return f"missing:{p.name}"
        try:
            import pyreadstat
            _, meta = pyreadstat.read_dta(str(p), metadataonly=True)
            cols = '|'.join(meta.column_names or [])
            return f"{p.name}:{meta.number_rows}:{hashlib.sha256(cols.encode()).hexdigest()[:16]}"
        except Exception:
            st = p.stat()
            return f"{p.name}:{st.st_size}:{int(st.st_mtime)}"


    def _compute_rundo_key(do_path: Path,
                           args: Sequence[str] | None,
                           input_dta_paths: Sequence[str | Path] | None,
                           bin_path: str,
                           ado_packages: Sequence[str] | None) -> str:
        payload = {
            'v': _RUNDO_SKIP_VERSION,
            'do_sha256': hashlib.sha256(do_path.read_bytes()).hexdigest(),
            'args': [str(a) for a in (args or [])],
            'inputs': sorted(_dta_column_hash(p) for p in (input_dta_paths or [])),
            'stata': _stata_version_fingerprint(bin_path),
            'ado': _ado_fingerprint(ado_packages),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, ensure_ascii=False).encode('utf-8')
        ).hexdigest()


    def _rundo_can_skip(stamp_path: Path, key: str,
                        output_paths: Sequence[str | Path] | None) -> bool:
        if not stamp_path.exists():
            return False
        try:
            stamp = json.loads(stamp_path.read_text(encoding='utf-8'))
        except (OSError, json.JSONDecodeError):
            return False
        if stamp.get('key') != key:
            return False
        # .log 必须存在 (与 .do 同名同目录)
        log_path = stamp_path.with_name(stamp_path.name.replace(_RUNDO_STAMP_SUFFIX, '.log'))
        if not log_path.exists():
            return False
        # 声明的产物全部存在才允许跳过
        for op in (output_paths or []):
            if not Path(op).exists():
                return False
        return True


    def _write_rundo_stamp(stamp_path: Path, key: str,
                           output_paths: Sequence[str | Path] | None) -> None:
        stamp = {'key': key, 'outputs': [str(p) for p in (output_paths or [])]}
        try:
            stamp_path.write_text(
                json.dumps(stamp, ensure_ascii=False), encoding='utf-8')
        except OSError:
            pass  # stamp 写失败不致命 — 下次重跑即可
    ```
- **新增测试**: `tests/test_papers_common.py::TestStataRunner` 增 3 个用例 (与既有 4 个并列, line 388 起):
  - `test_run_do_skip_disabled_by_default`: 不传 `skip_if_unchanged` 时, 即使 stamp 存在也照常调 `subprocess` (monkeypatch `subprocess.run` 计数被调一次)。
  - `test_run_do_skips_on_matching_key`: 先以 fake_bin + monkeypatch `subprocess.run` (返回 rc=0) 写出 .log + stamp + 产物; 第二次 `skip_if_unchanged=True` 同输入 → `subprocess.run` **不**被调, 返回 `returncode==0` 且 `args[0]` 含 `'<skipped'`。
  - `test_run_do_key_changes_on_do_edit`: 改 .do 内容一字节 → `_compute_rundo_key` 返回不同摘要 → 不跳过 (断言两次 key 不等; 直接单测 `_compute_rundo_key`)。
  - `test_run_do_key_changes_on_stata_bin`: 两个不同 size 的 fake_bin → `_stata_version_fingerprint` 不同 → key 不同 (锁"Stata 版本必入 key")。
- **验收**:
  - `pytest tests/test_papers_common.py::TestStataRunner -v` 全绿 (含既有 4 + 新 4)。
  - `ruff check news_process/papers/_common/stata_runner.py` clean。
  - 回归: `pytest tests/test_papers_b_route.py tests/test_stata_templates.py -q` 不受影响 (新参数默认关闭)。
- **风险/开放问题**:
  - `_stata_version_fingerprint` 用 exe 文件 stat 而非真 `about` 探测 — 妥协换"不启 GUI 子系统进程/不弹框" (CLAUDE.md Stata 段铁律)。若需精确 build 号可后续读 `version.do` 探针, 但代价高, 当前指纹对"升级 Stata 即失效"已充分。
  - 跳过仅在调用方**显式声明** `input_dta_paths`/`output_paths`/`ado_packages` 时才安全 — 漏报输入 .dta 会误命中。设计上 opt-in + 默认关闭, 把责任交给编排层 (analysis.py / stata_runner CLI) 显式列依赖; 本 W 不强制接入任何 callsite (零行为变更), 接入留后续工作项。
  - `.rundo_stamp.json` sidecar 落在 .do 同目录 → 须确保 `.gitignore` 覆盖 (或写进 build/ 临时区); 建议 stamp 路径改 `output_dir/_rundo_cache/` 以免污染 `papers/_common/stata_templates/` 源树 — 留审阅决策。

---

### W12 · HF 离线守卫补全 + stage15 词编码改走 `_eng.encode_local`
- **目标**: 给 3 个仍裸用 sentence-transformers 的模块补 `HF_HUB_OFFLINE`/`TRANSFORMERS_OFFLINE` setdefault (镜像 tone_berts:133 / article_sbert:93); stage15 关键词编码从每跑 `new SentenceTransformer().encode` 改走引擎单例 `_eng.encode_local` (继承确定性硬化 + 进程级模型缓存)。
- **golden 影响**: safe (HF offline 只切换"从 hf.co 解析 revision" → "读本地快照", 权重/输出逐位不变, 已由 tone_berts/article_sbert 落地先例 + memory `perf-audit-golden-safety-2026-06-24` 真机字节级实证背书; stage15 改走 `encode_local` 输出与裸 `model.encode` 在无超长文本时逐位一致, 见 encode_local:289-294/324-325 的"原样直送"保证, 且关键词均为短词不触分块)。
- **逐文件改动**:
  - `pipeline/filtering/fintech_intensity.py:103-114` — **锚点(当前真实代码)**:
    ```python
    import logging
    import math
    import os
    import platform
    import sys
    import time

    import jieba
    import numpy as np
    import pandas as pd

    jieba.setLogLevel(logging.WARNING)
    ```
    **改为** (`os` 已 import, 紧跟其后补 setdefault — 须在任何 transformers/sentence_transformers import 之前; 本模块 sentence_transformers 是函数内 lazy-import 故模块顶部设置即可生效):
    ```python
    import logging
    import math
    import os
    import platform
    import sys
    import time

    import jieba
    import numpy as np
    import pandas as pd

    jieba.setLogLevel(logging.WARNING)

    # fix(perf, golden-safe, W12): 强制 HF 离线 — 本地已有 text2vec 快照, 跳过 hf.co
    # revision 网络解析 (镜像 stage 23 tone_berts:133 / stage 25 article_sbert:93;
    # 只切换加载来源、不改权重 → 关键词语义权重逐位不变, golden-safe)。setdefault
    # 保留生产首跑显式 HF_HUB_OFFLINE=0 下载模型的逃生口。须在 sentence_transformers
    # import 前设 (本模块为函数内 lazy-import, 模块顶部设置即满足)。
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    ```
  - `pipeline/filtering/fintech_intensity.py:362-372` — **锚点(当前真实代码)** (步骤 B IDF 加权质心的裸 SentenceTransformer 路径):
    ```python
    try:
        from sentence_transformers import SentenceTransformer
        logger.info(f"加载词向量模型: {EMBEDDING_MODEL}")
        model = SentenceTransformer(EMBEDDING_MODEL)

        kw_list = list(idf_weights.keys())
        embeddings = model.encode(kw_list, show_progress_bar=False)
    ```
    **改为** (改走引擎单例 `encode_local`; 构造最小本地 spec; `del model` 行需同步调整 — 见下条):
    ```python
    try:
        from news_process.pipeline.text import embedding_engine as _eng
        kw_list = list(idf_weights.keys())
        # W12: 改走引擎统一本地编码 — 继承 ensure_torch_determinism() 硬化 +
        # 进程级模型单例 (_eng._LOCAL_MODELS), 避免每跑 new SentenceTransformer 实例。
        # 关键词均为短词 (远低于模型 max_seq) → encode_local 走"原样直送"分支
        # (engine:289-294/324-325), 输出与旧裸 model.encode 逐位一致 → golden-safe。
        # 不传 cache (关键词级权重一次性算, 不入 _llm_cache.db; 与原行为一致)。
        _kw_spec = {'model': EMBEDDING_MODEL, 'base_url': 'local'}
        embeddings = np.asarray(
            _eng.encode_local(kw_list, _kw_spec, log_prefix="fintech_intensity 词权重"),
            dtype=np.float32,
        )
    ```
  - `pipeline/filtering/fintech_intensity.py:398-400` — **锚点(当前真实代码)**:
    ```python
        logger.info(f"CosSim 校准: min={sig4(min_sim)}, max={sig4(max_sim)}, "
                    f"floor={sig4(ANISOTROPY_FLOOR)}")
        del model, embeddings
    ```
    **改为** (`model` 局部变量已不存在, 只 del `embeddings`):
    ```python
        logger.info(f"CosSim 校准: min={sig4(min_sim)}, max={sig4(max_sim)}, "
                    f"floor={sig4(ANISOTROPY_FLOOR)}")
        del embeddings
    ```
  - `pipeline/features/strategic_diff.py:178` — **锚点(当前真实代码)** (模块顶部 `import os`, 下游 `_eng` 在 line 203 import):
    ```python
    import os
    ```
    **改为** (紧跟 `import os` 后补 setdefault; strategic_diff 经 `_eng.encode_local` lazy-import sentence_transformers, 顶部设置即生效):
    ```python
    import os

    # fix(perf, golden-safe, W12): 强制 HF 离线 (镜像 stage 23/25); 只切换加载来源、
    # 不改权重 → text2vec 稳健轨 (_t2v) 嵌入逐位不变, golden-safe。setdefault 保留
    # 生产首跑显式 HF_HUB_OFFLINE=0 的逃生口。须在 sentence_transformers import 前设。
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    ```
    > ⚠锚点说明: strategic_diff 已委托 `_eng.encode_local` (line 300-303), 引擎本身**无** HF offline 守卫 (engine.py 顶部已确认无), 而 `embedding_engine` 是被 strategic_diff/benefit_society/network_spillover import 的下游; 在 import 它的模块顶部设 setdefault 可在 `from sentence_transformers import SentenceTransformer` (引擎内 line 271 lazy-import) 之前生效。**更彻底的方案见开放问题**: 直接在 `embedding_engine.py` 顶部设一次。
  - `pipeline/features/benefit_society.py:70` — **锚点(当前真实代码)**:
    ```python
    import os
    ```
    **改为**:
    ```python
    import os

    # fix(perf, golden-safe, W12): 强制 HF 离线 (镜像 stage 23/25); benefit_society
    # 经 _eng.embed_texts / _encode_local_cached 走 text2vec 本地稳健轨, 只切换加载
    # 来源不改权重 → 嵌入逐位不变, golden-safe。setdefault 保留生产首跑逃生口。
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    ```
  - `pipeline/panel/network_spillover.py:57` — **锚点(当前真实代码)**:
    ```python
    import os
    ```
    **改为**:
    ```python
    import os

    # fix(perf, golden-safe, W12): 强制 HF 离线 (镜像 stage 23/25); network_spillover
    # 经 _eng.embed_texts 走本地/API 双轨嵌入, 本地轨只切换加载来源不改权重 →
    # 嵌入逐位不变, golden-safe。setdefault 保留生产首跑逃生口。
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    ```
- **新增测试**: `tests/test_15_fintech_intensity_embed.py` (新文件):
  - `test_intensity_weights_uses_engine_encode_local`: monkeypatch `embedding_engine.encode_local` 返回固定矩阵, 断言 `_build_intensity_weights` 调它一次 (而非 `SentenceTransformer` 直构); 断言无超长关键词时输出与 fake 一致。
  - `test_hf_offline_env_set_on_import`: `import news_process.pipeline.filtering.fintech_intensity` 后断言 `os.environ['HF_HUB_OFFLINE']=='1'` 且 `os.environ['TRANSFORMERS_OFFLINE']=='1'` (同样断言 strategic_diff / benefit_society / network_spillover import 后置位; 可放进 `tests/test_hf_offline_guards.py`)。
  - **golden 等价回归**: 在 `test_15_*` 加一个"两实现等价"参数化断言 (旧裸 `model.encode` vs `_eng.encode_local`) 用同一 fake SentenceTransformer (无 `max_seq_length` → 走直送分支) 对一组短关键词输出 `np.array_equal`。
- **验收**:
  - `pytest tests/test_15_fintech_intensity_embed.py tests/test_hf_offline_guards.py -v` 绿。
  - 真机字节级验证 (受控环境 PYTHONHASHSEED=0 + MKL/OMP=1 + 保留 GPU): 改前/改后各跑 `python 15_fintech_intensity.py` 一次, `15_fintech_intensity.parquet` 的 `fintech_intensity_score_*` 列 sha256 逐位相等 (镜像 memory `perf-audit-golden-safety-2026-06-24` 的 25:107→14s / 23:297→194s 验证范式)。
  - `pytest tests/test_25_audit.py tests/test_benefit_society_embedding.py tests/test_network_spillover_embedding.py -q` 不回归 (W12 不动这些函数, 但 W13 会; 见下)。
- **风险/开放问题**:
  - **HF offline 设置点单一化建议**: 当前在 3 个 import-者模块顶部各设一遍, 是为对齐 tone_berts/article_sbert 的"每模块自守"先例; 但更干净的是**直接在 `embedding_engine.py` 顶部 (line 38 `from __future__` 后) 设一次** — 引擎是所有本地嵌入的唯一收口, 一处设置即覆盖 strategic_diff/benefit_society/network_spillover/policy_alignment 全部下游。两方案 golden 等价, 留审阅二选一 (若选引擎单点, 则 strategic_diff/benefit_society/network_spillover 三处 setdefault 可省, 仅 fintech_intensity 因 lazy-import 引擎也覆盖)。**我倾向引擎单点 + fintech_intensity 改走引擎后亦自动覆盖 → 可省全部 3 处模块级 setdefault**, 但保守起见上面按"显式每模块"给, 防引擎被绕过的边缘 import 路径漏网。
  - stage15 `_kw_spec` 不带 `text_pipeline_version` / `batch_size` → `encode_local` 用默认 batch_size=32 (与旧裸 `model.encode` 默认一致, engine:283); 关键词数 ~1500 一批即可, 无分块。确认 golden-safe。

---

### W13 · 裸编码 / legacy 死代码清理 (含同步陈旧测试)
- **目标**: 删除经 grep 证实"生产 0 调用"的 legacy 嵌入函数, 同步更新仅余的陈旧测试; network_spillover 的死 `_encode_embeddings_local`/`_get_embeddings_api` 直接删 (主路径已走 `_eng.embed_texts`)。
- **golden 影响**: safe (删的全是零生产调用的 legacy/裸路径; 活跃路径不动)。
- **死代码取证 (grep 实据)**:
  | 函数 | file:行范围 | 内部生产调用 | 仅余引用 | 处置 |
  |---|---|---|---|---|
  | `network_spillover._encode_embeddings_local` | `network_spillover.py:1445-1463` | **0** (主路径 `_embed_peer_texts:1622` 走 `_eng.embed_texts`) | 无生产; 测试间接 | **删** |
  | `network_spillover._get_embeddings_api` | `network_spillover.py:1466-1610` | **0** | `test_network_spillover_embedding.py:41` monkeypatch (stale) | **删** + 改测试 |
  | `network_spillover._embedding_config_uses_local` | `network_spillover.py:1435-1443` | **0** | 无 | **删** |
  | `network_spillover` 相关全局 `_LOCAL_EMBEDDING_MODEL`(:1432) | `network_spillover.py:1432` | 仅被已删的 `_encode_embeddings_local` 用 | 测试 monkeypatch(:1432 引用) | **删** + 改测试 |
  | `benefit_society._encode_embeddings_local` | `benefit_society.py:245-263` | **0** (主路径 `_get_embeddings:266→_eng.embed_texts`) | 无生产 | **删** |
  | `benefit_society._get_embeddings_api` | `benefit_society.py:284-417` | **0** | `test_benefit_society_embedding.py:41` monkeypatch (stale) | **删** + 改测试 |
  | `strategic_diff._encode_embeddings_local` | `strategic_diff.py:300-303` | **0** (薄包装, 主路径 `_embed_texts_with_chunk_pooling:822→_eng.embed_texts`) | `test_25_audit.py:248` 注释 | **删** |
  | `strategic_diff._get_embeddings_api` | `strategic_diff.py:658-806` | **0** | `test_25_audit.py:262` monkeypatch (stale no-op) | **删** + 改测试 |
  | `policy_alignment._get_embeddings_api_dynamic` | `policy_alignment.py:387-…` | **0** | `test_pipeline_robustness.py` + `test_omni_fix_policy.py` **显式契约保留** | **保留** (见风险) |

- **逐文件改动**:
  - `pipeline/panel/network_spillover.py:1435-1610` — **锚点(当前真实代码, 起止)**:
    ```python
    def _embedding_config_uses_local() -> bool:
        base_url = str(EMBEDDING_CONFIG.get('base_url') or '').strip().lower()
        ...
    def _encode_embeddings_local(texts, *, log_prefix="Embedding") -> np.ndarray:
        global _LOCAL_EMBEDDING_MODEL
        ...
    async def _get_embeddings_api(texts, model='text-embedding-3-small', cache=None):
        ...
        # 拼装最终结果
        final_embs = []
        ...
        return np.array(final_embs)
    ```
    **改为**: 删除 `_embedding_config_uses_local` (1435-1443)、`_encode_embeddings_local` (1445-1463)、`_get_embeddings_api` (1466-1610) 三个函数整体, 及全局 `_LOCAL_EMBEDDING_MODEL = None` (1432); 保留 `_embed_peer_texts` (1613起) 不动。`EMBEDDING_CONFIG`/`_EMB_MODELS` (1428/1431) 是否保留: `EMBEDDING_CONFIG` 仍被 `_embed_peer_texts:1624` 与 banner :149 用 → **保留**; `_EMB_MODELS` (1431) 仅被已删 `_get_embeddings_api:1491/1494` 用 → grep 确认零其它用后 **删** (须二次 grep 验证)。
  - `pipeline/features/benefit_society.py:245-263` — **锚点**: `_encode_embeddings_local` (245-263) 整体删 (主路径 `_get_embeddings:276` 走 `_eng.embed_texts`)。`_embedding_config_uses_local` (235-242) 是否还有用须 grep; `_get_embeddings_api` (284-417) 整体删。`_LOCAL_EMBEDDING_MODEL` 全局若仅被这两函数用则删。
  - `pipeline/features/strategic_diff.py:300-303` — **锚点(当前真实代码)**:
    ```python
    def _encode_embeddings_local(texts, *, spec=None, log_prefix="Embedding") -> np.ndarray:
        """本地 sentence-transformers 编码 (默认主 spec)。委托给 embedding_engine。"""
        return _eng.encode_local(
            texts, spec if spec is not None else EMBEDDING_CONFIG, log_prefix=log_prefix)
    ```
    **改为**: 整体删 (零调用薄包装; 调用方应直接用 `_eng.encode_local`)。`strategic_diff._get_embeddings_api` (658-806) 整体删。
  - `tests/test_network_spillover_embedding.py` — **锚点(当前真实代码, line 36-50)**:
    ```python
        monkeypatch.setattr(ns, "_LOCAL_EMBEDDING_MODEL", None)

        async def _api_should_not_be_used(*args, **kwargs):
            raise AssertionError("local embedding config should not call HTTP API")

        monkeypatch.setattr(ns, "_get_embeddings_api", _api_should_not_be_used)

        emb = ns._embed_peer_texts(["alpha", "beta"], year=2020)
    ```
    **改为** (改成校验 `_embed_peer_texts` 走引擎本地路径; 删对已移除符号的 monkeypatch, 改 patch `_eng._LOCAL_MODELS` 清空 + 设 local spec):
    ```python
        # W13: _embed_peer_texts 已统一走 _eng.embed_texts (本地 spec → encode_local);
        # 旧 ns._LOCAL_EMBEDDING_MODEL / ns._get_embeddings_api 已删, 改 patch 引擎单例。
        from news_process.pipeline.text import embedding_engine as _eng
        monkeypatch.setattr(_eng, "_LOCAL_MODELS", {})

        emb = ns._embed_peer_texts(["alpha", "beta"], year=2020)
    ```
    > 注: fake SentenceTransformer 经 `sys.modules` 注入 (已有), `_eng.encode_local` 内 `from sentence_transformers import SentenceTransformer` 取到 fake; fake 无 `max_seq_length`/`tokenizer` → 走直送分支 → `shape==(2,2)`, `emb[:,0]==[0,1]` 断言仍成立。`EMBEDDING_CONFIG` 须含 `base_url: local` 才走本地 (已有 monkeypatch 设 `base_url:"local"`)。
  - `tests/test_benefit_society_embedding.py:36-46` — **锚点**: 同型 — 删 `monkeypatch.setattr(bs,"_LOCAL_EMBEDDING_MODEL",None)` 与 `monkeypatch.setattr(bs,"_get_embeddings_api",...)`, 改成 `monkeypatch.setattr(_eng,"_LOCAL_MODELS",{})`; 被测调用 `bs._get_embeddings(["alpha","beta"],[1,1])` 仍走 `_eng.embed_texts` → 本地 spec → `encode_local`, 断言 `shape==(2,2)`/`emb[:,0]==[0,1]` 不变 (fake 直送分支)。
  - `tests/test_25_audit.py:237-262` — **锚点(当前真实代码)**:
    ```python
        @pytest.fixture(autouse=True)
        def _mock_embedding_api(self, monkeypatch):
            ...
            pytest.importorskip("sentence_transformers")
            async def _mock_api(texts, cache=None):
                ...
            monkeypatch.setattr(_m25, "_get_embeddings_api", _mock_api, raising=True)
    ```
    **改为** (旧 fixture mock 的 `_m25._get_embeddings_api` 已删 + 即使保留也是 no-op; 改为 mock 引擎 `_eng.embed_texts` 返回 deterministic 单位向量, 这是 strategic_diff live 路径真正收口):
    ```python
        @pytest.fixture(autouse=True)
        def _mock_embedding_api(self, monkeypatch):
            """W13: strategic_diff 已统一走 _eng.embed_texts; 旧 _get_embeddings_api
            (零生产调用) 已删。改 mock 引擎 embed_texts 返回 deterministic 单位向量。"""
            pytest.importorskip("sentence_transformers")
            from news_process.pipeline.text import embedding_engine as _eng

            def _mock_embed_texts(texts, spec, *, cache_db_path=None, cache=None,
                                  log_prefix="Embedding", enable_archive=True):
                texts = [] if texts is None else list(texts)
                if len(texts) == 0:
                    return np.empty((0, 0), dtype=np.float32)
                rng = np.random.default_rng(seed=42)
                mat = np.abs(rng.standard_normal((len(texts), 8))).astype(np.float32) + 1e-3
                mat /= np.linalg.norm(mat, axis=1, keepdims=True).clip(min=1e-12)
                return mat

            monkeypatch.setattr(_eng, "embed_texts", _mock_embed_texts, raising=True)
    ```
    > 同步更新该 fixture 的两段陈旧 docstring 行引用 (L242 "strategic_diff.py L436-437" / L248 "strategic_diff.py:235") → 改述为"统一经 `_eng.embed_texts`"。
- **新增/更新测试**: 上述 3 个测试文件就地更新 (不新增文件)。另在某处 (如 `tests/test_dag_consistency.py` 或新 `tests/test_no_legacy_embedding_fns.py`) 加**死代码守门**断言: `assert not hasattr(strategic_diff,'_get_embeddings_api')` / `not hasattr(benefit_society,'_get_embeddings_api')` / `not hasattr(network_spillover,'_get_embeddings_api')` (防回潮)。
- **验收**:
  - 删前先跑 `grep -rn '_get_embeddings_api\b\|_encode_embeddings_local\|_embedding_config_uses_local\|_LOCAL_EMBEDDING_MODEL\|_EMB_MODELS' --include=*.py news_process/` 留底, 删后再跑确认仅余 `policy_alignment._get_embeddings_api_dynamic` (受保留) + embedding_engine docstring 历史提及。
  - `pytest tests/test_25_audit.py tests/test_benefit_society_embedding.py tests/test_network_spillover_embedding.py tests/test_omni_fix_policy.py tests/test_pipeline_robustness.py -q` 全绿。
  - `ruff check news_process/pipeline/panel/network_spillover.py news_process/pipeline/features/benefit_society.py news_process/pipeline/features/strategic_diff.py` clean (确认无未用 import 残留, 如 benefit_society 删 `_get_embeddings_api` 后若 `aiohttp` 仅它用则连带清理)。
  - 全量回归 sweep `pytest -q` 无新增失败 (与 baseline 比对)。
- **风险/开放问题**:
  - **`policy_alignment._get_embeddings_api_dynamic` 刻意保留**: 它是 legacy 但 `test_omni_fix_policy.py:468-475` 显式断言"必须带 legacy test-only docstring 标注且生产源码 0 调用", `test_pipeline_robustness.py:337/376` 测其缓存穿透/重试契约。删它会破这两个测试的契约性质 → **不删**, 维持现状 (与 memory / 模块注释 line 378-385 的既定决策一致)。本 W 不动 policy_alignment 业务函数。
  - 删 `_EMB_MODELS`/`_LOCAL_EMBEDDING_MODEL`/`_embedding_config_uses_local` 前**必须逐个二次 grep** 确认无遗漏调用 (banner 日志、其它模块 import); 上面表格已初查但删除时须复核 (尤其 benefit_society 的 `_embedding_config_uses_local:235` 与 `_LOCAL_EMBEDDING_MODEL` 是否被 banner/诊断函数引用)。
  - `test_25_audit` fixture 改为 mock `_eng.embed_texts` 后, 须确认 strategic_diff 所有受测路径 (`_build_embedding_sim_matrix` / `_compute_emb_coherence` / centroid) 都经 `_embed_texts_with_chunk_pooling`→`_eng.embed_texts` 这一收口 (line 822 已证), 不存在绕过引擎的第二嵌入入口; 若有须一并 mock。

---

## 跨集群一致性备注 (供组装时对账)
- **W12 与 W13 在 strategic_diff/benefit_society/network_spillover 三文件有交集**: W12 在这三文件顶部加 HF setdefault, W13 在同三文件删 legacy 函数 — 改动行不重叠 (顶部 import 区 vs 函数体), 可同 PR; 但若采纳 W12 开放问题的"引擎单点设置"方案, 则 W12 在这三文件的 setdefault 改动取消, 仅留 `embedding_engine.py` + `fintech_intensity.py` 两处。
- **W12 stage15 改走 `_eng.encode_local` 后**, fintech_intensity 自动 import embedding_engine → 若 embedding_engine 顶部设 HF offline, stage15 的模块级 setdefault 亦冗余可省 (二选一, 防双重声明)。
- 三项全 **safe**, 无一触发 golden 重生; W11 sidecar 路径 (`.do` 同目录 vs `output_dir/_rundo_cache/`) 是唯一需审阅拍板的设计开放点。
```

---
