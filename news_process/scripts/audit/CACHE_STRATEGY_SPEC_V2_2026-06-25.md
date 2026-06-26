# 全项目缓存策略 — 实现规格 v2 (CACHE_STRATEGY_SPEC_V2_2026-06-25)

> **本文件是实现的唯一权威来源 (single source of truth)。** 取代 v1 (`CACHE_STRATEGY_DIFF_SPEC_2026-06-25.md`)。
> v1 + 验证报告 (`CACHE_STRATEGY_VERIFICATION_2026-06-25.md`) 保留作审计轨迹/出处, 实现时**只读本文件**。
>
> 沿革: 上层计划 (EXECUTION_PLAN) → v1 diff 规格 → 9-agent 对抗式验证 (18 confirmed + 6 驳回 + 2 golden 重分类)
> → 本 v2 (折入全部 18 修正 + 2 重分类; W5 重做; 三处陷阱块改写为唯一正确版)。
> 决策 (2026-06-25): 全 13 项 · CF-1 用「哈希 YAML 文件内容」口径 · needs-regen 攒 DEFERRED golden 窗口。

---

## §0 状态总览

| 项 | 标题 | 裁决 | golden | 批次 |
|---|---|---|---|---|
| W1 | batch_size 纳入 t2v 版本纪律 | go | safe | 批1 |
| W3 | PEER_PROMPT frozen-hash 护栏 | go | safe | 批1 |
| §5 | 缓存版本门治理规范 (写进 caching.py docstring) | go | safe | 批1 |
| W6 | StageSpec 加 inputs/fingerprint_cols | go | safe | 批2 |
| W5 | 通用 --skip-unchanged 阶段级增量 (**已重做**) | go (重做后) | safe | 批2 |
| W4 | 验证缓存隔离 _llm_cache_validation.db | go | safe | 批2 |
| W9 | MinHash 签名 sidecar | go | safe | 批2 |
| W11 | Stata run_do 内容寻址跳过 | go | safe | 批2 |
| W12 | HF 离线 (引擎单点 + stage15 模块顶; stage15 保裸路径) | go | safe | 批3 |
| W13 | legacy 死代码清理 (+test 同步) | go | safe | 批3 |
| W7 | SBERT 复用穿透缓存 | go | **needs-regen** | 批4 |
| W8 | BERT 推理缓存 (默认关) | go | **needs-regen** | 批4 |
| W10 | 词典 powerset 单次扫描重构 | go | **needs-regen** | 批4 |

golden 总账: **10 safe / 3 needs-regen** (W7/W8/W10)。批1/2/3 全 safe、离线 $0、可独立提交; 批4 攒 DEFERRED 统一受控重生。

---

## §1 实现纪律 (落地前必读)

1. **三处陷阱块: 本文给的就是唯一正确版, 已无错版。** (验证发现 v1 把正确版藏散文、字面块是错版 → 已在 v2 改正)
   - W3 frozen-hash: 必须 **EOL 归一** `PEER_PROMPT.replace('\r\n','\n').encode('utf-8')` (Windows 仓库, `.py` 未标 binary)。
   - W9 MinHash: 必须 **bytes 序列化** `hashvalues.astype('<u8').tobytes()` (uint64; list[int]→parquet int64 在 >2^63 符号回绕)。
   - W10 matched_words: 必须 **`'word': r['token']`** (保留 token, 字节等价; `''` 会破 sentiment_details + `test_omni_fix_tonewords.py:222-223`)。
2. **共享 helper 强制复用** (禁各造 sha256 轮子): 内容寻址一律用 `core/data_versioning.py::compute_file_hash` (文件) /
   `compute_config_hash` (dict, 已含 `default=str` 兜底); LLM/嵌入缓存一律用 `core/caching.py::LLMCache` 类 + `make_key`。
3. **golden 铁律**: 勿删 `_llm_cache.db`; 离线 (`NEWS_PROCESS_LLM_OFFLINE=1`) 严禁 `cache.delete`; needs-regen 项首跑须受控环境
   (`PYTHONHASHSEED=0` + `MKL/OPENBLAS/NUMEXPR/OMP_NUM_THREADS=1` + 保留 GPU + `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`);
   任何 memoization/重构落地前须**真机字节级 `==` 测试** (非 approx)。
4. **safe 批验收硬标准**: 离线跑相关 stage, 产物 content-sha256 与改动前**逐位一致**。

---

## §2 批1 — 失效护栏 (纯注释/文档/单测, 零行为变更)

### W1 · batch_size 纳入 t2v 版本纪律
- **golden**: safe。**锚点已验证**: `config/features.yaml:39` `batch_size: 128` / `:41` `text_pipeline_version: "v2-2026-05-29-t2v"`;
  `embedding_engine.py:598-599/607/641-645` 证 batch_size 不入键 (键=`(model_id, chunk文本, version)`); `:218` `spec_version` 缺 key 回退 `'v0'`。
- **改动**:
  - `config/features.yaml` batch_size 注释块尾追加硬约定 (值不动 `v2-2026-05-29-t2v`): "★ 版本门 §5-C: batch_size 不进缓存键; 改
    batch_size/device/dtype/torch 版本必同 diff bump 下方 text_pipeline_version 标号, 由 test_t2v_batch_version_lock 守护。"
  - `embedding_engine.py:599` 后加 inline 注释指向该约定 (不改逻辑)。
- **测试** `tests/test_t2v_batch_version_lock.py`:
  - `test_t2v_batch_and_version_lockstep`: `cfg=load_config()['embedding_robustness']`; 在**同一断言**里断言
    `batch_size==128` and `text_pipeline_version=='v2-2026-05-29-t2v'` (任一改而另一未改即红)。
  - `test_t2v_version_is_lintable`: **用 `re.search(r'^v\d+-\d{4}-\d{2}-\d{2}', ver)`, 不加结尾锚 `$`** (CF-W1-low: 现值尾部是 `-t2v`, 加 `$` 会误红)。
  - `test_batch_size_not_in_cache_key` (回归锁): 用 `tmp_path` 建 `LLMCache`, 证 `make_key` 签名无 batch_size 维度。
- **验收**: `pytest tests/test_t2v_batch_version_lock.py -v` 绿; 手改 batch_size→64 不动 version → 该测试 FAIL; 改回 → PASS。

### W3 · PEER_PROMPT frozen-hash 护栏 (CF-5 已修)
- **golden**: safe。**锚点已验证**: `llm_peer_iv.py:322-335` PEER_PROMPT (含硬换行 + `{{"peers": []}}` 转义); `:339` `PEER_PROMPT_VERSION="v1-2026-05-13"`; `:367` `.format(bank_name=, year=, numbered_sentences=)` (占位符仅这 3 个)。
- **改动** `llm_peer_iv.py` `:339` 后追加 (PEER_PROMPT 正文/版本号**不动**):
  ```python
  # ★ 版本门 §5-D (内联常量须配 frozen-hash 单测): 下行冻结 PEER_PROMPT 的 EOL 归一字节。
  #   改 PEER_PROMPT 正文 → test_peer_prompt_frozen 红 → 强制本 diff 同时 bump PEER_PROMPT_VERSION 并重算下值。
  #   重算: python -c "import hashlib;from news_process.pipeline.panel.llm_peer_iv import PEER_PROMPT;\
  #          print(hashlib.sha256(PEER_PROMPT.replace(chr(13)+chr(10),chr(10)).encode('utf-8')).hexdigest())"
  PEER_PROMPT_SHA256 = "<落地时由实现者在真机仓库跑上行命令填入 64-hex>"
  ```
- **测试** `tests/test_peer_prompt_frozen.py` (**唯一正确版, EOL 归一**):
  ```python
  import hashlib
  from news_process.pipeline.panel.llm_peer_iv import PEER_PROMPT, PEER_PROMPT_SHA256, PEER_PROMPT_VERSION
  def test_peer_prompt_frozen():
      actual = hashlib.sha256(PEER_PROMPT.replace("\r\n", "\n").encode("utf-8")).hexdigest()
      assert actual == PEER_PROMPT_SHA256, (
          f"PEER_PROMPT 正文已变 (actual={actual!r})。有意修改须同 diff bump PEER_PROMPT_VERSION "
          f"(现 {PEER_PROMPT_VERSION!r}) 并把本 SHA256 改为 actual。")
  def test_peer_prompt_placeholders_intact():
      for ph in ("{year}", "{bank_name}", "{numbered_sentences}"):
          assert ph in PEER_PROMPT
  ```
  首跑会打印 actual, 用其填 `PEER_PROMPT_SHA256`。
- **不动** `check_prompt_headers.py` / `.pre-commit-config.yaml` (它只扫 `config/prompts/*.txt`, 内联常量不在其责; 强加会破其 stdlib-only 设计)。
- **验收**: 填值后 `pytest tests/test_peer_prompt_frozen.py` 绿; 改 PEER_PROMPT 一字 → 红。

### §5 · 缓存版本门治理规范 (CF-12 已修)
- **golden**: safe (纯文档/注释)。落点 = **追加到 `core/caching.py` 模块 docstring 末尾** (与代码同源, 避开 docs/ 目录定位歧义; `SCHEMA_VERSION='v1'`@141 不变量不碰)。
- **5 条铁律**:
  - **A** 新缓存键首字段 = `SCHEMA_VERSION` (沿用 `_make_key`), 保留全局一键失效。
  - **B** "改代码语义会改输出但不改键内既有字段"的参数, 进键或绑显式 version token (callsite+config 注释写死 bump 触发条件)。
  - **C** FP 敏感超参 (`batch_size`/`device`/`dtype`/线程数/`torch` 版本) **当版本维度对待** (W1 即此)。
  - **D** version token 优先放可 lint 位置 (`.txt` 首行 > yaml 字段 > 模块内联常量; 内联须配 frozen-hash 单测, 即 W3)。
  - **E** 资源文件 (词典/anchor/`MEDIA_NAME_OVERRIDES`) 以内容 sha256 入键 (preprocess 已对 noise/bank 做)。
  - 统一接口段须列三库分治: 生产 `_llm_cache.db` / 验证 `_llm_cache_validation.db` (W4) / 本地模型 `_local_model_cache.db` (W8), 均复用 `LLMCache` 类。
- **现存版本门全景表** (供规范引用; **CF-12 修正**): `PREPROCESS_CODE_VERSION` 的**定义**在 `pipeline/preprocess/_constants.py:131`
  (`v3-2026-06-25-media-canon`); `runner.py:129` 仅 import、`:197` 使用 → 表中"位置"列指向**定义处** `_constants.py:131`。
  其余: `SCHEMA_VERSION`@`caching.py:141`; `unified_cot.txt:1`; `PEER_PROMPT_VERSION`@`llm_peer_iv.py:339`;
  `text_pipeline_version` ×2 @`features.yaml:29`(api)/`:41`(t2v)。

---

## §3 批2 — safe 基建 (W6→W5, W4, W9, W11)

### W6 · StageSpec 加 inputs/fingerprint_cols (W5 前置; CF-7 已修)
- **golden**: safe (向后兼容默认空, `test_dag_consistency` 不破)。**锚点**: `core/dag.py:129-154` `@dataclass(frozen=True) StageSpec`, 末字段 `enabled_when`(:154)。
- **改动** `dag.py` StageSpec 在 `enabled_when` 后追加:
  ```python
  enabled_when: Callable[[dict[str, Any]], bool] = always_enabled
  # W6: 通用 --skip-unchanged 的声明式依赖 (向后兼容默认空)。
  #   inputs = 上游产物的 OUTPUT_REGISTRY 逻辑键 (shim 文件名), 用于增量跳过时比对 input_hashes。
  inputs: tuple[str, ...] = ()
  fingerprint_cols: tuple[str, ...] = ()
  ```
- **填 inputs 纪律** (CF-7): **必须以 producer 真实 `save_*(input_files=...)` 闭包为准, 不靠 DAG 直觉。**
  - ⚠ **CF-7 修正**: v1 把 stage15 inputs 写成含 `14_materialize_ctx.py` 是**错的**。实测 `fintech_intensity.py:801`
    `save_dataset(input_files=[full_path, input_file])`, 其中 `full_path=12_fintech_news_full.parquet`(:666) /
    `input_file=12_fintech_news.parquet`(:793-794) — **均 stage12 产出, 不含 stage14** (14 被读但未记入 input_files)。
  - **首批只填确认能通过比对的线性链** (如 `11→12→13→14`, `51←40` 等单源链); 多源 fan-in / producer 漏记上游的 stage
    (15 / 40 等) **暂留空** `inputs=()` (留空 = 该 stage 不参与跳过 = 保守永远重跑, safe)。
  - W5 的比对契约只比 `spec.inputs ∩ recorded input_hashes` 交集 (见 W5), 故留空或填子集都不会误跳。

### W5 · 通用 --skip-unchanged 阶段级增量 (**已重做**: CF-1 + CF-2 + CF-11)
- **golden**: safe (默认 flag 关; 父进程只读元数据决定 spawn, 不进 stage 内存, 字节中性; 修复后**不会**误跳)。
- **设计 = 哈希 YAML 文件内容 (CF-1 用户选定口径; 绕开 CONFIG dict, 永不盲)**。

  **① producer 侧 — `core/data_versioning.py` 记录 split YAML 内容哈希** (W5(3), 已验证 golden-safe: golden 只哈希数据列, 不碰 schema metadata):
  ```python
  # data_versioning.py — 新增模块级 helper
  _SPLIT_YAML_FILES = ("paths.yaml","preprocessing.yaml","filtering.yaml",
                       "sentiment.yaml","features.yaml","panel.yaml","validation.yaml")
  def compute_config_file_hashes(config_dir: str | Path) -> dict[str, str]:
      """对 config/ 下 7 个 split YAML 各算内容 sha256 (compute_file_hash 复用)。缺失文件跳过。"""
      out = {}
      for fn in _SPLIT_YAML_FILES:
          p = Path(config_dir) / fn
          if p.exists():
              out[fn] = compute_file_hash(p)
      return out
  ```
  `DataVersionMetadata.__init__` 增可选参数 `config_dir`, 记 `self.config_file_hashes = compute_config_file_hashes(config_dir)`;
  `to_dict()` 增 `"config_file_hashes": self.config_file_hashes`。`save_parquet_with_metadata` 增可选 `config_dir`
  (默认从 `core.config` 的 config 目录常量取, 各 producer 无需改 call-site)。

  **② 编排器侧 — `run_pipeline_function.py`**:
  - **CF-2 必修**: `:425` 默认 Namespace 改为
    ```python
    args = argparse.Namespace(skip_21_if_exists=False, skip_unchanged=False)
    ```
    (否则 10+ 个无参 `run_pipeline()` 调用方 — `core/locking.py:31` / `papers/_common/pipeline_runner.py:30` / 8 个 paper `analysis.py` — 命中 `AttributeError` 整链崩。)
  - `_parse_cli_args` 加 `--skip-unchanged` (action="store_true")。
  - **stage→YAML 文件映射** (CF-1 核心; 用文件名, **不用 CONFIG dict 键**):
    ```python
    # 每个 stage 绑定它消费 config 的 split YAML 文件; 改这些文件内容即失效该 stage (永不盲)。
    STAGE_CONFIG_FILES: dict[str, tuple[str, ...]] = {
        "00_preprocessing.py": ("preprocessing.yaml", "paths.yaml"),
        "11_news_bank.py": ("filtering.yaml", "paths.yaml"),
        "12_news_fintech.py": ("filtering.yaml", "paths.yaml"),
        "13_cooccurrence_filter.py": ("filtering.yaml", "paths.yaml"),
        "14_materialize_ctx.py": ("filtering.yaml", "paths.yaml"),
        "15_fintech_intensity.py": ("filtering.yaml", "features.yaml", "paths.yaml"),
        "16_article_policy_alignment.py": ("filtering.yaml", "features.yaml", "paths.yaml"),
        "21_tone_llms.py": ("sentiment.yaml", "paths.yaml"),
        "22_tone_words.py": ("sentiment.yaml", "paths.yaml"),
        "23_tone_berts.py": ("sentiment.yaml", "paths.yaml"),
        "24_herd_decay_processor.py": ("sentiment.yaml", "paths.yaml"),
        "25_article_sbert.py": ("features.yaml", "paths.yaml"),
        "26_article_staleness.py": ("features.yaml", "paths.yaml"),
        "40_panel_export_main.py": ("panel.yaml", "features.yaml", "paths.yaml"),
        "46_stata_export.py": ("panel.yaml", "paths.yaml"),
        "51_falsification_test.py": ("panel.yaml", "paths.yaml"),
    }
    ```
    (映射缺项 → 该 stage 不跳, 保守。映射宁可多列 YAML 文件: 粒度粗=多重跑, 但**永不漏失效** — 用户已接受此口径。)
  - **跳过判定** (放在主循环 `:538` 预清理删除**之前**, 照 stage21 `:522` 控制流):
    ```python
    def _stage_skip_unchanged_is_safe(script: str) -> tuple[bool, str]:
        from news_process.core.data_versioning import (read_parquet_metadata,
            compute_config_file_hashes, compute_file_hash)
        outputs = _get_stage_output_files(script)
        if not outputs:                       # CF-11: validation/无产物 stage 永不跳
            return False, "无登记 parquet 产物 (validation/audit), 不参与增量跳过"
        out_dir = CONFIG['paths']['output_dir']
        cur_cfg = compute_config_file_hashes(CONFIG_DIR)   # CONFIG_DIR = config/ 绝对路径
        want_files = STAGE_CONFIG_FILES.get(script)
        if want_files is None:
            return False, f"{script} 未登记 STAGE_CONFIG_FILES, 保守重跑"
        for fn in outputs:
            p = os.path.join(out_dir, fn)
            if not os.path.exists(p):
                return False, f"产物缺失 {fn}"
            meta = read_parquet_metadata(p)
            if not meta or 'config_file_hashes' not in meta:
                return False, f"{fn} 无 config_file_hashes 元数据 (旧产物), 保守重跑"
            rec_cfg = meta['config_file_hashes']
            for wf in want_files:             # 只比该 stage 相关的 YAML 文件
                if rec_cfg.get(wf) != cur_cfg.get(wf):
                    return False, f"config 文件 {wf} 内容已变"
            # 上游产物 input_hashes 比对 (只比 spec.inputs ∩ recorded 交集; CF-7)
            spec = _SPEC_BY_SCRIPT.get(script)
            rec_inp = meta.get('input_hashes', {})
            for up_logical in (spec.inputs if spec else ()):
                up_files = _get_stage_output_files(up_logical)
                for uf in up_files:
                    up_path = os.path.join(out_dir, uf)
                    if uf in {os.path.basename(k) for k in rec_inp}:   # 交集才比
                        rec_h = next(v for k, v in rec_inp.items() if os.path.basename(k) == uf)
                        if not os.path.exists(up_path) or compute_file_hash(up_path) != rec_h:
                            return False, f"上游产物 {uf} 内容已变"
        return True, "config 文件 + 上游产物 input_hashes 均未变"
    ```
    主循环插入 (预清理前):
    ```python
    if args.skip_unchanged and not (args.skip_21_if_exists and script == '21_tone_llms.py'):
        ok, why = _stage_skip_unchanged_is_safe(script)
        if ok:
            logger.info(f"  ⏭ {name}: --skip-unchanged 命中, 已跳过 ({why})")
            stage_timings.append((name, 0.0, True))
            continue
    ```
- **CF-11 必修**: **不**给 `run_pipeline_validation.py` 加该机制 (validation 阶段 `_get_stage_output_files` 恒返 `[]` →
  判定第一步即 `False` → 死代码)。v1 的 step6 验证 runner 接入**整段删除/不实现**。
- **测试** `tests/integration/test_skip_unchanged.py`:
  - (a) 二次跑 (产物+元数据齐, config/上游未变) → 目标 stage 全 ⏭。
  - (b) 改某 stage 的 split YAML 文件内容 → 该 stage **不**跳 (config_file_hashes 失配)。
  - (c) 改上游产物内容 → 下游 input_hash 失配 → 不跳。
  - (d) **不带 flag** → 行为与现状逐字节一致 (默认全量, 不跳)。
  - (e) **CF-2 回归**: `run_pipeline(args=None)` 路径不抛 `AttributeError` (覆盖默认 Namespace 含 skip_unchanged)。

### W4 · 验证缓存隔离 (CF-13 + CF-14 已修)
- **golden**: safe (键算法零改、验证 prompt 与生产键互异、verify 仍读生产库)。**锚点**: `prompt_sensitivity.py:1583` / `entity_masking.py:941`(main 体内 **4 空格**) / `entity_masking.py:732`(try 内 **8 空格**) LLMCache 实例化。
- **改动**:
  - `config/paths.yaml` filenames 块尾 (现末条 `output_27_benefit_cache`@:83) 后加: `output_llm_cache_validation: _llm_cache_validation.db`
    (CF-16: 同时为生产库补 `output_llm_cache: _llm_cache.db` 作对称键, 并把 W7 引用统一到此键, 见 W7)。
  - 三处 `LLMCache(...)` 指向验证库路径 (经 config 取 `output_llm_cache_validation`)。
  - ⚠ **CF-13 必修**: after 块缩进**降到与插入点同级** — `:941` 处 **4 空格**, `:732` 处 **8 空格** (v1 字面块多缩进一级, 逐字粘贴会 `IndentationError`)。
- **文案 (CF-14)**: 隔离收益是 **hygiene** (验证阶段 `cache.size()` 日志纯净 + 生产 `_llm_cache.db` 不因跑验证而增长),
  **不是** "verify_stage21_cache_coverage 计数不被稀释" (该脚本点查生产键, 本就对验证键免疫)。paths.yaml 注释与设计说明按此改。
- **验收**: 跑一次 prompt_sensitivity → 生产库 `size()` 不增, 变体落 `_llm_cache_validation.db`。

### W9 · MinHash 签名 sidecar (CF-9 + CF-10 已修)
- **golden**: safe (签名确定 → 命中逐位等价; datasketch 版本入 key 作版本门; 生产 stage00 默认不启用)。**锚点**: `dedup.py:292 compute_minhashes` (返回 `pd.Series(idx→MinHash)`, `hashvalues` 是 uint64)。
- **改动** `dedup.py compute_minhashes` 增可选 `cache_dir: str | None = None`:
  - key = `compute_config_hash({"datasketch": <datasketch.__version__>, "num_perm": self.num_perm, "ngram_size": self.ngram_size, "corpus": <corpus_fingerprint>})` (复用 `compute_config_hash`; datasketch 版本入 key = 版本门)。
  - ⚠ **CF-9 必修 (唯一正确版, bytes 序列化)**: 落 parquet 用 binary 列
    ```python
    # 写: 每个 MinHash → bytes (uint64 小端)
    payload = {"idx": list(series.index),
               "sig": [m.hashvalues.astype("<u8").tobytes() for m in series.values]}
    # 读回: np.frombuffer(b, dtype="<u8") → MinHash(num_perm=..., hashvalues=arr)
    ```
    (禁用 `list[int]`→parquet int64: datasketch hashvalues 是 uint64, >2^63 会符号回绕破坏签名。)
  - **CF-10 必修**: 给**第二个 caller** `pipeline/panel/dedup_sensitivity.py:246` 也传 `cache_dir` (它经 runner step 6b-3 在每次 stage40 面板构建跑全语料 MinHash, 是更高频生产路径); 同步更正 v1 "唯一复用点 dedup_threshold:383" 措辞 (实有两 caller)。
- **测试**: sidecar 往返 — 含 `hashvalues` 最大值的 MinHash 经 bytes 路径重建后 `hashvalues` 逐位等价; 改 datasketch 版本号 (mock) → key 变 → 不命中。

### W11 · Stata run_do 内容寻址跳过 (CF-3 已修)
- **golden**: safe (编排层不进 40_panel; 默认 skip 关)。**锚点**: `stata_runner.py:86-146 run_do`, `cmd=[bin,'/b','do',str(do_path)]`, `cwd=do_path.parent`。
- **改动** `run_do` 增可选 `skip_if_unchanged: bool = False`; sidecar 落 `<output_dir>/_rundo_cache/<key>.json` (不污染模板源树, 免改 .gitignore):
  - key = `compute_config_hash({"do": compute_file_hash(do_path), "dta": {p: compute_file_hash(p) for p in 输入dta}, "stata": _stata_fingerprint(bin_path), "ado": <关键 ado 版本指纹>})` (复用 `compute_file_hash`/`compute_config_hash`, CF-W11 shared-helper)。
  - ⚠ **CF-3 必修 (唯一正确版)**: Stata `/b do foo.do` 写的 log 是 **`foo.log`** (去 `.do` 扩展, 见 `run_stata.ps1:108` `$do.BaseName + '.log'`), **不是** `foo.do.log`。跳过命中判定的 log 路径:
    ```python
    log_path = do_path.with_suffix(".log")   # 正确; v1 的 .name.replace(SUFFIX,'.log') 得 foo.do.log → 永不命中=死功能+测试假绿
    ```
  - `_stata_fingerprint(bin)` = exe 文件 `size+mtime+basename` (妥协: 不启 GUI 探版本, 符合 CLAUDE.md 铁律; git checkout/重装改 mtime → 保守失效, 可接受)。
- **测试**: 命中用例须用**真实 `do_path.with_suffix('.log')`** 路径 (防 v1 那种"自造 foo.do.log → 假绿")。
- 修 v1 描述里"增 3 vs 列 4"的计数自相矛盾。

---

## §4 批3 — safe 清理 (W12 + W13 同 PR)

### W12 · HF 离线 (引擎单点 + stage15 模块顶) (CF-17 已修; **DOC-1 落地校正**)
- **golden**: safe (切加载来源不改权重, 有 `tone_berts:133`/`article_sbert:93` 先例 + 真机背书)。
- **改动 (实际落地; 与本段早期"stage15 改走引擎"草案不同, 见 DOC-1)**:
  - ⚠ **CF-17 必修**: 采**引擎单点**方案 — 在 `pipeline/text/embedding_engine.py` 顶部 import 区一处:
    ```python
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    ```
    一处覆盖所有经引擎的本地模型路径 (含 `policy_alignment` stage16 — v1 per-module 版漏了它)。
  - **stage15 `fintech_intensity.py` 保留裸 `SentenceTransformer(EMBEDDING_MODEL).encode(kw_list)`**, 仅在**模块顶**加 HF 离线 setdefault (F14, 与三先例一致)。
    ⚠ **DOC-1 (2026-06-26): 刻意不改走 `_eng.encode_local`** —— 改走会新增 `ensure_torch_determinism` / 分块逻辑, GPU 上可致 FP 位差 (需真机字节核); 保裸路径 = **字节恒等、零 golden 风险**, 收益 (词级 ~1500 词缓存) 太小不值, 故降级为"仅加模块顶 HF 离线"。
- **验收**: stage15 保裸路径 → HF 离线只切加载源不改权重 → 输出逐位不变 (无需 encode_local 的 FP 核; 与三先例同理)。

### W13 · legacy 死代码清理 (CF-4 已修)
- **golden**: safe (删的全是 grep 实证生产 0 调用的 legacy; 活路径全走 `_eng.embed_texts`)。
- **删除** (grep 确认 0 callsite): `benefit_society._encode_embeddings_local`/`_get_embeddings_api`;
  `strategic_diff._get_embeddings_api`/`_encode_embeddings_local` + **`_LOCAL_EMBEDDING_MODEL`(:292)/`_embedding_config_uses_local`(:295)** (死孤儿, 一并删);
  `network_spillover._encode_embeddings_local`(:1445, 确认死后删, 活则改走 `_eng.embed_texts`)。
- **保留**: `policy_alignment._get_embeddings_api_dynamic` (契约测试锁)。
- ⚠ **CF-4 必修 (v1 漏的第四个测试文件)**: 测试同步清单 = `test_25_audit.py` + `test_benefit_society_embedding.py` +
  `test_network_spillover_embedding.py` + **`test_strategic_diff_embedding.py:36`** (它 `monkeypatch.setattr(sd,'_LOCAL_EMBEDDING_MODEL',None)`,
  删该符号后 patch 抛 `AttributeError` 整文件 collect error → 全量 sweep 红)。四个文件**同 PR**改 (改 mock `_eng.embed_texts` 或移除对已删符号的 patch)。删除必与 production 删同 PR (否则 collect error)。
- **验收**: `pytest`(全量 sweep) **无新增失败** + `ruff check` clean。

---

## §5 批4 — needs-regen (攒 DEFERRED 统一受控重生)

> 三项首跑须受控环境播种 + 受控重生 golden, **与既有 DEFERRED 批** (`_allv` / inject-fintech / rule-ablation / media-canon) **一次合并消费**, 避免本机裸环境误 bless 3 个 BLAS-FP 网络列等无关漂移。

### W7 · SBERT 复用穿透缓存 (CF-8 + CF-16 已修; **研究构念决策已定 = (b) 分块 mean-pool**)
- **golden**: **needs-regen**。**CF-8 重生理由修正**: 不是 v1 说的"fp64 vs fp32 归一 ~1e-7", 而是**表征机制变化** —
  历史 `model.encode(docs, normalize_embeddings=True)` 对超长 doc (`_truncate_for_sbert`= `title[:100]|content[:300]` ≈ 400 中文字符 >> text2vec max_seq=128) 走模型内部**静默截断到 128 token**; 而 `encode_local`(:286-342) 对 >126 token 改为**分块 + 逐块 L2 归一 + token 加权 mean-pool**。`semantic_staleness_*` 余弦会**显著变**(非微变), 且改变了 Bybee 2024 "标题+首段截断"构念口径。
- ✅ **决策已定 (2026-06-26, 用户拍板) = (b) 分块 mean-pool**: 用满"标题+首段300字"(`encode_local` 对 >126 token 分块 + 逐块 L2 归一 + token 加权 mean-pool), **兑现作者本意** (`_truncate_for_sbert` 注释本写"首段300字", 但历史模型只吃 ~128 token、后 ~3/4 内容一直被丢, 是潜伏 bug), 且让 stage25 与全项目其它 text2vec 阶段 (15/16/27/strategic_diff/network_spillover) **口径一致** (此前 stage25 是唯一仍走截断的异类)。
  - **落地义务 (batch4 实现 + DEFERRED 重生时必做)**: ① manuscript/codebook **如实披露** `semantic_staleness_*` 构念从"模型截断 128 token"变为"126-token 分块 mean-pool (纳入首段300字全文)"; ② 报**新旧 staleness 列相关性** (稳健性对照, 证定性结论不变)。
  - **未采纳 (a) 保截断**: 会冻结潜伏 bug + 留 stage25 为异类 → 已否决。
- **改动**: `article_sbert.py encode_articles` 的 `model.encode(...)` 改走 `embedding_engine.embed_texts(docs, spec=<local t2v spec>, cache_db_path=<output_llm_cache 键>)` (复用 `_encode_local_cached`: 去重防漂移 + json float32 无损往返); 保留 `ensure_torch_determinism`; **(b) 不做额外截断** —— 直接让 docs (标题+首段300字) 经 encode_local 分块 mean-pool (这正是兑现作者本意的关键, 切勿加 token 截断)。
- **CF-16**: 缓存库 config 键统一 = `filenames.output_llm_cache` (与 W4 对称; 勿用 v1 的 `paths.llm_cache_db` 裸键)。
- **成本现实 (本轮验证 F16)**: stage25 现已 HF 离线, 单次 ~14.2s (CLAUDE.md/旧文的 `107s` 是 HF 离线**前** baseline; 真机 perf-audit 实测 106.7→14.2s)。真瓶颈是 stage23 (297→194s)。W7 收益主因 = **整阶段免重算全量 4-6h** (配合 W5 通用 skip), 非省单次那 14s。
- **顺手订正 (本轮验证 F5, cosmetic golden-safe)**: `article_sbert.py` 有 6 处 (line 12/23/61/138/276/335-336) 把所用模型 max_seq 误注释/误日志为 **512**, 实为 text2vec-base-chinese 的 **128** (`embedding_engine.py:265` 自承); 改 W7 时一并把这 6 处订正为 128。

### W8 · BERT 推理缓存 (CF-15 + CF-18 已修; **默认关**)
- **golden**: **needs-regen** (argmax 边界冻结; 维持此分类, 拒 should_be_safe — 裸环境首跑会冻结漂移 argmax)。
- **改动** `tone_berts.py run_all_models` 批 forward 处包裹缓存 (独立 `_local_model_cache.db`, 复用 `LLMCache` 类):
  - ⚠ **CF-15 必修 (删双哈希)**: 直接把复合身份串塞 `make_key` 的 model_id 槽, **不预哈希**:
    ```python
    composite = f"{short_name}|maxlen={max_length}|vocab={vocab_fp}|det={deterministic_mode}|amp={amp_flag}|ckpt={ckpt_fp}"
    cached = cache.get(composite, content, prompt_version="bert-v1")      # 一次哈希
    # ... miss 才 forward ...
    cache.put(composite, content, json.dumps({"label":..,"probs":[round(p,4)..],"num_windows":..}), prompt_version="bert-v1")
    ```
    (v1 先 `make_key(...)` 再把 64-hex 当 model_id 传 get → 内部二次哈希, content 进键两次, 冗余。)
  - ⚠ **CF-18 必修**: `config/sentiment.yaml` 新增 `inference_cache: false` **默认关**, 直到 DEFERRED 受控重生窗口 (防裸环境冻结漂移 argmax 污染未来 golden); 仅手动单 stage 调试时开 + 受控播种。
  - 诚实标注: get-override 若仍全量 forward 则"297s→秒级"名不副实; 提速须只对 miss 文章构窗 forward。`ckpt_fp` 对 HF hub 模型退化为 `no-ckpt:<id>` 失去换版保护 (须披露)。
- **W5 联动**: W5 落地后, stage23 在"输入 parquet 哈希不变即整阶段 skip"层面已被覆盖 → W8 保持默认关即可 (此时不开缓存=不改产物=safe)。

### W10 · 词典 powerset 单次扫描重构 (CF-6 已修)
- **golden**: **needs-regen** (引擎数学层经 E-agent 真机 208 用例 `struct.pack` 实证**逐位等价**; 搭车既有 rule-ablation DEFERRED 批)。**锚点**: `tone_words.py:598 _compute_sentiment_with_rules`; `:759-764 matched_words` (含 `'word':token`/`'base'`/`'final'`/`'boosted'`); `:1439-1440 sentiment_details=json.dumps(top_detail)` (读 `x['final']`)。
- **改动**: 拆 `_compute_sentiment_with_rules` 为
  - `_scan_sentiment_trace(tokens, dict)` → 单次扫描产中间表, 每命中词记 `{token, base, applied_degree, in_negation_window, in_adversative}`;
  - `_reduce_trace(trace, *, apply_negation, apply_degree, apply_adversative)` → 8 个 powerset 变体用纯算术从中间表派生 `Σ(final)`/`Σ|final|`/pos/neg 计数 + matched_words。
  - 每词典 8 次全 token 循环 → 1 次扫 + 8 次 reduce。
- ⚠ **CF-6 必修 (唯一正确版, 保留 token)**: `_reduce_trace` 重建 matched_words 必须与现 `:759-764` **字节等价**:
  ```python
  matched_words.append({
      "word": r["token"],            # ← 保留 token (禁用 ''); 否则破 sentiment_details + test_omni_fix_tonewords.py:222-223
      "base": r["base"],
      "final": round(final_score, 4),
      "boosted": adversative_active,
  })
  ```
- **测试/验收**: 真机 `==` (非 approx) 对全量 (或大样) 文章逐位比对重构前后 6 词典 × 8 变体 + union + sentiment_details JSON 字节一致; `test_omni_fix_tonewords.py` 绿。

---

## §6 验收门禁 (每批提交前)

- `pytest -m fast` 绿; `tests/integration/test_dag_consistency.py` (W6 加字段后) 绿; 新增 `test_skip_unchanged.py` / `test_t2v_batch_version_lock.py` / `test_peer_prompt_frozen.py` 绿。
- `ruff check .` clean。
- **safe 批 (1/2/3)**: 离线 `NEWS_PROCESS_LLM_OFFLINE=1` 跑相关 stage, 产物 content-sha256 与改动前**逐位一致**。
- **needs-regen 批 (4)**: 受控环境 (PYTHONHASHSEED=0 + 全 BLAS=1 + 保留 GPU + HF offline) 冷跑 == 暖跑逐位一致 → 受控重生 golden → `test_panel_reproducibility` 绿。
- 计数不变 (W6 加 StageSpec 字段是向后兼容默认空): STAGES_MAIN/VALIDATION / shim / OUTPUT_REGISTRY 不变。

---

## §7 决策点 (2026-06-26 已结)

1. ✅ **W7 表征口径 = (b) 分块 mean-pool** (用户拍板): 用满"标题+首段300字", 与全项目其它 t2v 阶段一致 + 修潜伏 bug。落地义务 (batch4): manuscript/codebook 披露 `semantic_staleness_*` 构念变 + 报新旧相关性。见 §5 W7。
2. ✅ **W1 不补 bump** `text_pipeline_version` (用户拍板): 盘上 _t2v 缓存本就 batch=128 自洽; 现在补 bump 反致一次本可省的重生。护栏 (W1 注释+单测) 已防未来漂移; 版本号保持 `v2-2026-05-29-t2v` 不变, 留 batch4 DEFERRED 重生时**顺手** bump (免费)。
3. ✅ **批1/2/3 (safe) 全部完成**: **10/10 safe 项已落地+验证** (W1/W3/§5/W6/W5/W4/W9/W11/W12/W13); W13 死代码删除 (3 模块 12 符号/492 行 + 6 未用 import) + 4 测试改写, 149 测试绿 / ruff clean / 3 模块洁净 import / 12 个相关测试文件全过。
4. **批4 (needs-regen)**: W7(b)/W8/W10 攒 DEFERRED golden 窗口 (与 _allv/inject-fintech/rule-ablation/media-canon + W1 顺手 bump 一次合并受控重生)。

---

## 附: 18 CF → v2 落点对照 (可追溯性)

| CF | 严重度 | v2 落点 |
|---|---|---|
| CF-1 | blocker | W5 §3: STAGE_CONFIG_FILES 哈希 YAML 文件内容 (替代错误的 CONFIG.get(域名)) |
| CF-2 | blocker | W5 §3: 默认 Namespace 加 skip_unchanged=False + 测试 (e) |
| CF-3 | high | W11 §3: log_path = do_path.with_suffix('.log') |
| CF-4 | high | W13 §4: 测试同步补 test_strategic_diff_embedding.py + 删 _LOCAL_EMBEDDING_MODEL |
| CF-5 | high | W3 §2: frozen-hash EOL 归一为唯一实现 |
| CF-6 | high | W10 §5: matched_words 'word': r['token'] 唯一版 |
| CF-7 | high | W6 §3: stage15 inputs 真实闭包 (12_full+12_fintech 非 14) + ③ 交集比对 |
| CF-8 | high | W7 §5: 重生理由=表征机制变; 决策已定=(b) 分块 mean-pool (2026-06-26) + manuscript 披露 |
| CF-9 | medium | W9 §3: bytes 序列化唯一版 |
| CF-10 | medium | W9 §3: dedup_sensitivity:246 第二 caller 接 cache_dir |
| CF-11 | medium | W5 §3: 删验证 runner 死代码接入 |
| CF-12 | medium | §5 §2: PREPROCESS_CODE_VERSION 位置=_constants.py:131 |
| CF-13 | medium | W4 §3: after 块缩进降到 4/8 空格同级 |
| CF-14 | low | W4 §3: 收益改述为 hygiene |
| CF-15 | low | W8 §5: 删 _bert_cache_key 预哈希 |
| CF-16 | low | W7/W4: 缓存库键统一 filenames.output_llm_cache(_validation) |
| CF-17 | low | W12 §4: 引擎单点 HF offline (覆盖 policy_alignment) |
| CF-18 | low | W8 §5: inference_cache 默认 false |
