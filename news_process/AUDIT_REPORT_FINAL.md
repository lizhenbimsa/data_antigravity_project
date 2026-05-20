# news_process 系统评审 — 最终干净版报告 (AUDIT_REPORT_FINAL)

**最终评审日期**: 2026-05-20
**评审人**: Claude Opus 4.7 (1M context) + 三轮独立验证 (16 个并行代理)
**评审范围**: `F:\WiseSearch\data_antigravity_project\news_process\` + 仓库根
**约束**: 只读 / 不修改源代码 / 不允许中间态判定

## 评审历程

| 轮次 | 方法 | 输入 | 输出 |
|---|---|---|---|
| 1 | 6 并行专项审计 | 全代码库扫描 | 110 条原始 finding (AUDIT_REPORT.md) |
| 2 | 5 并行二次复核 | 110 条 | 90 CONFIRMED / 18 PARTIAL / 2 FALSE (AUDIT_REPORT_VERIFIED.md) |
| 3 | 5 并行最严格三审 | 110 条 (二元判定) | **73 REAL / 37 DELETE** (本文档) |

**最终保留率**: 73 / 110 = **66.4%** (37 条经最严格证据要求剔除)

---

## 一、最终统计

| 严重程度 | 数量 | 文件域 |
|---|---:|---|
| 🔴 Critical (P0) | **15** | secrets / executive_ner 完全失能 / 依赖缺失 / merge 防御 / Stata 硬编码 |
| 🟠 High (P1) | **17** | LLM 调用层 / Pandas dtype / 路径 / 重试 |
| 🟡 Medium (P2) | **26** | config/DAG/locking/caching/logging/dtype 报告 |
| ⚪ Low (P3) | **15** | 文档漂移 / 死代码 / Stata 模板配置 / 字体 fallback |
| **REAL 合计** | **73** | |

---

## 二、剔除的 37 条 (false positive / 不可坐实 / 已修复 / 概念错位)

(只列条目名,详细理由见 AUDIT_REPORT_VERIFIED.md 与各代理输出。)

| 编号 | 剔除原因 |
|---|---|
| P-001 | `.env` 已被 `.gitignore:34/52` 屏蔽,`git ls-files` 实测**未追踪**;只是本地工作副本含真 key, 属于运维而非代码 bug |
| P-002 | JSON 中的 key 前缀属已轮换的旧 key (`sk-djQqUuh0Q...`),与当前 `.env` 中 `sk-g6KIp...` 不同;12 字符无法重构,纯卫生噪音 |
| P-011 | `bank_name` 仅源自项目内部 `bank_list.yaml` 与 panel 输出的中文银行名,无不可信输入路径 |
| P-019 | `subprocess.Popen` 不传 env 时默认继承父环境;且所有 stage 在同一 user 下运行,无特权边界可越;"过度传播" 概念错位 |
| P-020 | `prompt_version="v0"` 默认值是有文档的向后兼容契约,非 bug |
| P-021 | 锁文件按 Plan P1-5 **设计上无内容** (`仅承载 OS 级锁`),诊断都在 sidecar;truncate-race 无内容可破坏 |
| P-026 | UA 轮换无安全边界, `random.choice` 在非安全场景数学上充分;且每次 `_cbirc_fallback` 都新选 UA |
| P-028 | CPython 3.1+ `repr(float)` 跨平台确定 (Gay 1990);生产 callsite 全传 literal,无算术派生温度 |
| P-029 | 生产历史 `TEMPERATURE = 0.0` 始终如此,无 0.7 era v0 entries;且 v0 fallback 显式 gate 在 `temperature == 0.0` |
| P-031 | 不计崩溃半行是 **预期行为** (incomplete record 不应进 manifest);可重现性审计的安全选择 |
| P-032 | `krippendorff` 库 native 处理 NaN 缺失数据;`n_valid_items >= 1` 保护 + try/except 包装,正确性 OK |
| P-033 | 39c/39d/39e 操作**不同** indicators (LM 6/lexical 3/NMI matrices);同 seed 在不同数据上 ≠ correlated nulls |
| P-035 | `rng.permutation` 顺序消费仍产生统计独立排列;"非独立" 混淆确定性顺序与统计依赖 |
| P-040 | `_SENT_DELIMITER_RE = r'(?<=[。！？\!\?])...'` **不含** ASCII `.`,原 claim 与另一文件正则混淆 |
| P-046 | `load.py:167-170` 显式 per-file object→string homogenize,跨 file pyarrow concat 无 dtype 飘移 |
| P-047 | `dedup.py:155-163` 显式 log `valid_dates/total_rows` + `logger.warning`,非静默 |
| P-048 | `config/media_weights.json` 是 `Dict[str, int]` 类型注解,所有值整数 literal,无小数权重 |
| P-049 | `preprocess/runner.py:312` 显式 `df = df.reset_index(drop=True)` 在 ArticleDeduplicator 之前;index 已保证唯一 |
| P-050 | `df = df[mask]` 是 rebind 非 chained;CoW 只破坏 `df[mask][col] = ...` 形式 |
| P-051 | pandas `.min()/.max()` 空 Series 返 NaN + FutureWarning,不 raise |
| P-052 | sum/mean/count 全部 skipna 一致;`is_positive` 与 `llm_vote_score_full` 同源 LLM 行,co-NaN by construction |
| P-054 | 纯 perf 担忧,128GB MP 19.5 不构成 OOM 风险;无正确性 bug |
| P-059 | 纯 perf,且 `if not content_ctx: ... else:` 两分支处理 **不同条件** (extraction 空 vs 无 bank), 非死代码 |
| P-060 | `news_bank.py:418-419` `if not res_df.empty: classified_dfs.append(res_df)` 显式过滤;空 shard 永不入 concat |
| P-064 | 原 claim "SE maxvar=2048" 事实错;Stata SE = 32767, 只 BE = 2048;项目策略已 Stata 19+ only |
| P-066 | 纯 perf 担忧,无正确性 bug |
| P-067 | pandas groupby 不产空 group;`ffill().iloc[-1]` 路径无 IndexError |
| P-068 | BOM-prefixed JSON 触发 `json.JSONDecodeError`,被 except + `logger.error` 显式捕获,非静默 |
| P-076 | python-dotenv 已 pin 在 requirements;ImportError fallback 路径在生产永不执行 |
| P-079 | 四计数器读取在 `with self._lock:` 内 (原子快照),`get/put` 写入也在锁内;无 race |
| P-080 | `os.makedirs` 在 `LLMCache.__init__` 而非 module import-time |
| P-081 | 现代 OS 保证 PID 唯一 (live processes);同秒同 PID 同 host **物理上不可能** |
| P-090 | 现代 pyarrow `cast(new_schema)` 元类型相同时仅 metadata,不复制 buffer;3× 内存 claim 错 |
| P-091 | 自承 "与 P-020 同根",冗余 |
| P-096 | 纯文档样式 nitpick (delta vs absolute) |
| P-099 | 实测 `STATA_IC_MAX_VARS` 单一定义 (`stata_export.py:40`) + 5 个 import;非散落魔法数 |
| P-100 | 引用路径 `news_process/.gitignore` **不存在**,误证 |

---

## 三、🔴 Critical 真实问题 (15 条 — P0 立即修)

### P-003 — pyproject.toml 版本严重漂移
**Proof** (`pyproject.toml:7` + `news_process/__init__.py:68`):
```toml
version = "3.3.0"
```
```python
__version__ = "3.3.0"
```
CLAUDE.md 声称 v3.7.0+v2.3 (2026-05-18 baseline),但包元数据停在 3.3.0。
**Fix**: `version = "3.7.1"` 同步两处。

### P-004 — `requests` 未声明但生产 import
**Proof**: `pyproject.toml:36-71` 依赖段无 requests;`pipeline/sentiment/executive_ner.py:116` + `scripts/data_acquisition/banking_outcome_dry_run.py:268` 直接 `import requests`。
**Fix**: `requests>=2.31.0,<3.0.0` 加入 `[project].dependencies`。

### P-005 — D-group 5 个必备包被注释
**Proof** (`requirements.txt:115-119`):
```
# bertopic>=0.16.0,<1.0.0
# umap-learn>=0.5.0,<1.0.0
# hdbscan>=0.8.30,<1.0.0
# faiss-cpu>=1.7.4,<2.0.0
# krippendorff>=0.5.0,<1.0.0
```
`pipeline/text/article_topic.py / article_staleness.py / audit/cross_media_alpha.py` 已 import 但 STAGES_MAIN 中 always_enabled。Fresh checkout 直接 ImportError。
**Fix**: 取消注释或加 `[d-group]` extras。

### P-006 — `executive_ner.py:188-200` LLMCache 构造完全错位
**Proof**:
```python
# executive_ner.py:
cache = LLMCache(namespace=cache_namespace)
cache_key = f"{model}:{hash(prompt)}"
```
```python
# core/caching.py:147 实际签名:
def __init__(self, db_path: str):
```
`LLMCache(namespace=...)` raise `TypeError`,被 `except (ImportError, TypeError, AttributeError)` 静默吞掉。stage 19 D4 NER **永远零缓存命中**,每跑 ~$12 LLM 预算全部白花。
**Fix**: `cache = LLMCache(CACHE_DB_PATH)` + `cache.get(model_id, prompt, prompt_version='d4_v0')`。

### P-007 — `executive_ner.py:208-214` archive_record 关键字全错
**Proof**:
```python
# executive_ner.py:
archive_record(stage='19_executive_ner', model=model, prompt=prompt,
               response=raw, metadata={'bank': bank_name, ...})
```
真签名 (`pipeline/llm_archive/archive.py:202`): keyword-only `cache_key/model_id/model_version/prompt/response_raw/prompt_version/temperature/api_endpoint/http_status`。每次调用 `TypeError`,被宽 except 吞掉。**DC3 LLM archive 顶刊 reproducibility 硬约束被实质违反**, V4 F-P2.1 主张失实。
**Fix**: 用真参数重写。

### P-008 — `executive_ner.py:190` `hash(prompt)` 非确定性 cache key
**Proof**:
```python
cache_key = f"{model}:{hash(prompt)}"
```
PYTHONHASHSEED 随机化,跨进程不同。即便 P-006 修复, cache 仍永不命中。
**Fix**: `hashlib.sha256(prompt.encode()).hexdigest()`。

### P-009 — 3 处无界 `while True` 重试
**Proof**:
- `pipeline/filtering/policy_alignment.py:251-292`
- `pipeline/features/benefit_society.py:292-366`
- `pipeline/features/strategic_diff.py:542-609`

均无 `MAX_RETRIES`;持续 429/5xx 永远卡死。父端 `timeout=3600` 最终 SIGKILL,但 SQLite cache 半写状态残留。
**Fix**: 三处统一改 `for attempt in range(MAX_RETRIES): ...` + 耗尽后 `raise`。

### P-010 — LLM archive 含完整中文文章 + 银行元数据
**Proof** (`pipeline/llm_archive/archive.py:249-262`):
```python
record = {
    'cache_key': cache_key, 'model_id': model_id, 'model_version': model_version,
    'prompt_version': prompt_version, 'temperature': temperature,
    'prompt': prompt, 'response_raw': response_raw, ...
}
```
`prompt` 包含完整 Chinese 文章 + bank 名;`.gitattributes:36` LFS 配置 `data/llm_archive/responses/*.jsonl` 指向期刊 replication 发布;无任何 redaction。
**Fix**: 拆 archive (a) 模板 hash + content_sha256 (review 包用) (b) 加密内容 blob (本地用);加 `content_redacted` 模式。

### P-012 — `article_staleness.py:245-257` 双 bug (lambda 闭包 + dead .agg)
**Proof**:
```python
agg_cols[col.replace('staleness', 'highstale')] = (
    lambda s, c=col: (article_df[c] > 0.9).mean()  # bug 1: outer df ref
)
panel = (
    article_df.groupby(['target_bank', 'year'], as_index=False)
    .agg({col: 'mean' for col in agg_cols})  # bug 2: 丢弃 lambdas, 直接 'mean'
)
```
两个 bug 叠加: lambda 引用外层 `article_df[c]`(global 均值非 group), 且 `.agg()` 直接传 `{col: 'mean'}` 丢弃 lambdas → `surface_highstale_full` 这种 key 不在 `article_df.columns` → `KeyError`。函数 dead-on-arrival。
**Fix**: `lambda s: (s > 0.9).mean()` + 把 lambdas 真正传入 `.agg()`。

### P-013 — `article_staleness.py:217-234` NaT 比较窗口失效
**Proof**:
```python
while window_start_idx < i and dates.iloc[window_start_idx] < cutoff:
    window_start_idx += 1
```
`NaT < cutoff` → False, while 循环退出,窗口起点卡在 NaT 行;后续文章窗口涵盖所有历史。
**Fix**: 进 compute_semantic_staleness 前 `df = df[dates.notna()]`。

### P-014 — `encode.py` 8 处 merge 全无 `validate=`
**Proof** (`pipeline/panel/encode.py` 行 836/915/941/996/1064/1117/1177/1231):
```python
panel = panel.merge(cat_panel, on=['target_bank', 'year'], how='left')
```
任一 cat_panel 含重复 key 即 silent fan-out;`n_articles` 双计。
**Fix**: 八处统一加 `validate='one_to_one'`。

### P-015 — `runner.py:1184-1185` 嵌套 merge 6 次连乘
**Proof**:
```python
for track_name, freq_col in _tracks:                # 2 tracks
    for pct in _percentiles:                         # 3 percentiles
        _quadrant_agg = df_align.groupby(...).agg(...).reset_index()
        panel = panel.merge(_quadrant_agg, on=['target_bank','year'], how='left')
```
6 次循环 merge 无 validate;一处 dup key 即指数 fan-out 至 64×。
**Fix**: `validate='one_to_one'` + 调用前 `assert _quadrant_agg.set_index(['target_bank','year']).index.is_unique`。

### P-016 — Stage 19 always_enabled + 6h timeout + $12 LLM 无 opt-in
**Proof** (`core/dag.py:194-199`):
```python
StageSpec(
    name="阶段19: LLM CEO/Chairman zero-shot NER (v3.7.0 D4)",
    script="19_executive_ner.py", group="main", kind="sentiment",
    timeout=21600,
),
```
无 `enabled_when=`,默认 `always_enabled`。Fresh checkout `python run_pipeline_function.py` 直接触发完整 NER ~$12 yunwu 预算。
**Fix**: `enabled_when=ner_enabled` 谓词 + `config/sentiment.yaml::executive_ner.enabled` 默认 false。

### P-017 — Stata 模板硬编码 F:/WiseSearch 路径
**Proof**:
- `papers/bank_media_disagreement/stata_templates/00_master.do.tmpl:14`:
  ```stata
  local project_root "F:/WiseSearch/data_antigravity_project"
  ```
- `papers/bank_news_clarity/stata_templates/00_master.do.tmpl:13`: 同。

主线 7 paper 用 `{{PROJECT_ROOT}}` 占位符;只这两个新 paper 烙路径。任何外部 reviewer 立即 "directory not found"。
**Fix**: 两模板改 `local project_root "{{PROJECT_ROOT}}"`,走 `_substitute_placeholders`。

### P-018 — Stage 22 dual-track cache key 共享
**Proof** (`pipeline/sentiment/tone_llms.py:416, 446`):
```python
cache.get(model_id, prompt, prompt_version=prompt_version)
cache.put(model_id, prompt, result_text, prompt_version=prompt_version)
```
cache key = `(model_id, prompt, prompt_version)`;`track` **不在 key 命名空间**。当 ctx 物化 fallback 路径 `content_ctx == content_full` 时,两轨共享 cache,downstream `_dual_analyze` ablation 在该子集坍塌。
**Fix**: cache key 加 `track ∈ {full, ctx, title}` 维度。

### P-022 — `executive_ner.py:102-150` `_yunwu_chat_sync` 零重试
**Proof**:
```python
try:
    resp = requests.post(..., timeout=timeout)
    if resp.status_code != 200:
        logger.debug(...)
        return ''
    return data['choices'][0]['message']['content'] or ''
except Exception as e:
    logger.debug(...)
    return ''
```
单次 POST。任何 429/502/503/504/timeout → 静默 `return ''` → 调用方视为 "无高管提及"。系统性测量误差。
**Fix**: `for attempt in range(MAX_RETRIES): ...` + 指数退避 + 耗尽前不返回空字符串。

---

## 四、🟠 High 真实问题 (17 条 — P1)

### P-023 — `network_spillover.py:999-1015` embedding 单次 POST 无重试
单 `session.post`,任何 !=200 即 RuntimeError;丢失同 batch 全部 in-flight cache 写入。
**Fix**: 与 strategic_diff.py 同模板的 retry + backoff;复用 `build_llm_connector(...)`。

### P-024 — `v7_wz_audit.py:75-100` `_read_env_key` + 单次 POST
`_read_env_key` 不展开 `${VAR}`;`session.post` 无 retry, 非 200 还硬解析 `data['choices'][0]` → 不透明 KeyError;异常栈可能含 Authorization。
**Fix**: 用 `dotenv.dotenv_values`;包装 retry/sanitize headers in exception。

### P-025 — `executive_ner.py:144` debug log 含完整 response 文本
```python
logger.debug(f"  LLM HTTP {resp.status_code}: {resp.text[:200]}")
```
yunwu 401 错误体常含 key request id 片段。
**Fix**: 复用 tone_llms.py 的 `_summarize_auth_failure` 字段脱敏。

### P-027 — `core/caching.py` 无淘汰策略
`created_at` 字段存了但永不查询;`put/put_batch/size/close` 全有但无 `delete/prune/evict`。
**Fix**: 加 `prune(keep_days=90)` 方法 + 定期维护任务。

### P-030 — `llm_archive/archive.py:135-158` JSONL append-only 跨进程 race
`threading.Lock()` 仅 intra-process;orchestrator 子进程不共享。`response_raw` 经常超 PIPE_BUF (Linux 4096B,Windows 无保证),并发写交错破坏 JSONL。
**Fix**: 改 `fcntl.flock` (POSIX) / `msvcrt.locking` (Windows), 或 per-PID 文件名 + 合并。

### P-034 — `lm_discriminant_validity.py:204-209` HTMT NaN → 'FAIL' 假阳性
```python
max_htmt = htmt.max().max()  # NaN if all off-diagonal NaN
f"({'PASS' if max_htmt < HTMT_STRICT else 'FAIL (need expert audit)'})"
```
`nan < 0.85` → False → 'FAIL'。空 dict (P-039 触发) 即假报警。
**Fix**: 加 NaN 分支 → `'NAN_UNDEFINED'`。

### P-036 — `strategic_diff.py:541-615` aiohttp 无 TCPConnector
```python
async with aiohttp.ClientSession() as session:
```
未传 `connector=build_llm_connector(...)`。Windows TIME_WAIT 240s 累积 → 端口耗尽。
**Fix**: 复用 `tone_llms.py:201` `build_llm_connector` (`limit=safe_limit, limit_per_host=safe_limit, ttl_dns_cache, keepalive_timeout, enable_cleanup_closed=True`)。

### P-037 — `strategic_diff.py:439` LDA K 永远 10
```python
K = max(10, n_banks // 30)
```
对当前 panel 84 banks → K=10。无 perplexity 选 K, 无 config 调。
**Fix**: 从 `CONFIG['features']['strategic_diff']['lda_K']` 读;附 sensitivity sweep。

### P-038 — `forward_looking.py` `望` substring 误命中
```python
"望" in _FUTURE_WORDS  # line 57
has_future = any(fw in sentence for fw in _FUTURE_WORDS)  # line 108
```
`"望" in "绝望"` / `"希望"` / `"展望"` 均 True。双门控 (must have time marker) 部分降伪阳, "绝望地等待未来三年" 仍误命中。
**Fix**: 改 jieba token 精确匹配;`望` 单字移出或加 retrospective filter (`已/过去/上`)。

### P-039 — `lm_non_sentiment.py:60-77` 缺词典文件静默回退
```python
if not _LM_DICT_PATH.exists():
    return {s: frozenset() for s in _SUBSETS}  # 静默
```
无 `logger.error/warning`。下游 `uncert_frac_*` 全 0 →触发 P-034 HTMT NaN 假阳性。
**Fix**: 缺文件 `raise RuntimeError` 或至少 `logger.error`。

### P-041 — `numerical_intensity.py:175` `(?!元)?` 失效
```python
text = re.sub(r'(\d+(?:\.\d+)?)\s*(万亿|亿|万)(?!元)?', ...)
```
`(?!元)?` — `?` 让 lookahead 总成功。`元` 永被消耗。
**Fix**: 删 `?` 或重写两次替换。

### P-042 — `numerical_intensity.py:96-120` `_cn_number_to_arabic("两万亿")` 错 5 个数量级
**Algorithm trace**:
- `两` → number=2
- `万` (unit=1e4) → section=2, total += 2×1e4 = 2e4, reset
- `亿` (unit=1e8) → section=0, total += (0 or 1)×1e8 = 1e8
- **Final: 100020000 ≈ 1×10⁸** (真值 2×10¹²)

5 个数量级误差。"100 万亿" 同 bug。
**Fix**: 用 `cn2an` 库,或预处理 "万亿" 复合单位。

### P-043 — `tone_llms.py:590-616` `parse_json_response` 吞所有错
```python
except Exception:
    return {}
```
无 per-model 失败计数器;3-模型 ensemble 中某模型持续 malformed JSON 时静默退化为 2-模型。
**Fix**: 改 `except json.JSONDecodeError as e: _PARSE_COUNTERS[model_id] += 1; logger.warning(...); return {}`;panel 加 `json_parse_failure_count` 列。

### P-044 — `tone_llms.py:521-583` 无账户级 token bucket
3 model × 8 concurrency × 短 prompts → burst > yunwu 账户 RPM,429 cascades。
**Fix**: 加 `AsyncAccountRateLimiter(rpm=...)` token bucket;`config/sentiment.yaml::llm.account_rpm`。

### P-045 — `tone_llms.py:414-418` cache 命中绕过 archive
```python
if cache is not None:
    cached_response = cache.get(model_id, prompt, prompt_version=prompt_version)
    if cached_response is not None:
        return row_idx, model_id, cached_response, track  # 早 return,不入 archive
```
V4 F-P2.1 主张 "archive 是 source of truth"; 重跑 cache pre-warmed 时 archive **空**。
**Fix**: cache 命中也调 `_llm_archive_record(..., cache_hit=True)`,或文档明确 "archive 仅 first-run"。

### P-053 — `encode.py:1458-1459` 空 panel `range(NaN, NaN+1)` 崩
```python
all_years = list(range(panel['year'].min(), panel['year'].max() + 1))
```
empty panel → `min()` = nan → `range(nan, nan)` → `TypeError`。
**Fix**: 函数顶 `if panel.empty: return panel`。

### P-058 — `article_topic.py:263-264` `np.stack` 失败模式
```python
embs_full = np.stack(art_df['emb_full'].tolist())
```
任一行 NaN/wrong-dim → `ValueError: all input arrays must have the same shape`。6h 计算后才发现, 损失工时。
**Fix**: 入栈前 `art_df['emb_full'].apply(lambda v: isinstance(v, np.ndarray) and v.shape==(768,)).all()` 断言。

---

## 五、🟡 Medium 真实问题 (26 条 — P2)

### P-055 — `runner.py:934, 952` 政策年份硬编码
```python
STRESS_YEARS = {2015, 2018, 2020}
panel['depins_post'] = (panel['year'] >= 2015).astype(int)
```
`51_falsification_test.py:897-899` 复制同值, 仅靠手写注释维持一致。
**Fix**: 移到 `config/panel.yaml::policy_events`。

### P-056 — `epu_merge.py:147-159` 无 coverage 断言
左 merge 不验证 `panel['epu_mean_year'].notna().mean()`。EPU 2023-2024 缺失即静默全 NaN。
**Fix**: `assert merged['epu'].notna().mean() > 0.80` 或同步阈值告警。

### P-057 — `epu_merge.py:136-141` `.agg('last')` 未先 sort
```python
year_epu = epu_df.groupby('year').agg(epu_year_end=('epu', 'last'), ...)
```
线 170 已修复主路径,但 line 136 fallback 分支仍依赖隐式 chronological。
**Fix**: 加 `.sort_values(['year','month'])` 显式。

### P-061 — `encode_collab.py:332` `open()` 无 encoding=
```python
with open(ctx_baseline_path) as f:
    baseline = json.load(f)
except (KeyError, ValueError, OSError) as e:
    ... fallback threshold_low = 0.5
```
Windows cp936 → UnicodeDecodeError (ValueError 子类) 被 catch → 静默 fallback 错阈值。
**Fix**: `open(..., 'r', encoding='utf-8-sig')` + 加 UnicodeDecodeError 分支显式 logger.error。

### P-062 — `stata_export.py:200-202` 标签 char 截断 vs byte 检查
```python
if len(label.encode('utf-8')) > STATA_VAR_LABEL_MAXLEN:
    label = label[:STATA_VAR_LABEL_MAXLEN - 3] + '...'
```
检查按 byte (80) ,截断按 char。CJK 3 byte/字 → 77 char = 231 byte ≫ 80。Stata `to_stata` 拒收。
**Fix**: byte-aware truncator,`while len(label.encode('utf-8'))>77: label=label[:-1]`。

### P-063 — `stata_export.py:350-374` 列名截断碰撞
`[:32]` 截断 + `_1` 后缀 → t0/t1, full/ctx 等关键 suffix 被吃,Bartik IV 变体不可区分。
**Fix**: hash-suffix `new_col[:25] + '_' + md5(col)[:6]`,并写 rename_map。

### P-065 — `panel/export.py:291` 反向依赖 (kernel ← product)
```python
from news_process.papers._common.tables import sanitize_stata_columns
```
pipeline (kernel) import papers (product) — 层级反转。
**Fix**: 下沉 `sanitize_stata_columns` 到 `pipeline/panel/_stata_helpers.py`。

### P-069 — `core/dag.py` enabled 默认不对称
`_validation_flag(key, default=True)` vs `temporal_mask_enabled` / `risk_taking_outcomes_enabled` 默认 False。同 DAG 文件两套语义。
**Fix**: 统一为 opt-in (默认 False) + 文档明确。

### P-070 — `core/dag.py` 无 import-time uniqueness 断言
重复 StageSpec 仅 `test_dag_consistency.py` 抓得到。
**Fix**: 模块底加 `_validate_dag_invariant()` (镜像 `schemas.py:303` 模式)。

### P-071 — STAGES_MAIN ↔ OUTPUT_REGISTRY 无 import-time cross-check
新 stage 漏 OUTPUT_REGISTRY 仅 test 抓。
**Fix**: 把 cross-check 下沉至 `schemas.py::_validate_registry_invariant`。

### P-072 — `core/dag.py:131` 默认 `timeout=3600`
源码 line 210 注释自承"会被父端 proc.kill() 强杀, 留下 partial parquet"。
**Fix**: 默认提至 7200 / kind-based 默认 (`sentiment` → 21600)。

### P-073 — `core/config.py:198-224` partial split-mode 死路 fallback
错误建议 "删 split YAML 回退 legacy"; legacy 是 stub → 再 raise。
**Fix**: 重写提示, 删除 stub fallback 路径。

### P-074 — `core/config.py:244-254` env placeholder 仅 warn
缺 YUNWU_API_KEY 仅 warning → 4h preprocessing 后 401。
**Fix**: `REQUIRED_ENV_VARS = ('YUNWU_API_KEY',)` 缺即 raise。

### P-075 — `core/config.py:55-65` `_deep_merge` 类型不匹配静默丢
dict-over-scalar 或 scalar-over-dict 时无 warning 即被覆盖。
**Fix**: type 不一致 `logger.warning` 或 raise (strict mode)。

### P-077 — `core/locking.py:78-100` sidecar 写入 race
OS lock 后 sidecar 写入前进程 A 被抢占 → B 见锁但 sidecar 不存在,显示 "未知"。源码 line 157 自承 race 窗口。
**Fix**: 写 sidecar `.tmp + os.replace` 原子化;入锁前先写 sidecar。

### P-078 — `core/locking.py` 无 stale-lock 自动检测
SIGKILL 后 lock + sidecar 滞留, 错误提示要用户手删。
**Fix**: 用 `psutil.pid_exists(lock_pid)` 检活,stale 自动清除。

### P-082 — `core/run_id.py:28` hostname 非法字符
```python
host = _socket.gethostname().split(".")[0][:24]
```
只 split `.`,不洗 `\/:#?*`。被用于 `logs/runs/<run_id>/...` 路径组件。
**Fix**: `re.sub(r'[^A-Za-z0-9_-]', '_', host)`。

### P-083 — `core/logging.py` 无 secret redaction filter
`Grep "redact|secret|api_key" core/logging.py` 0 hits。`logger.info(f"... {api_key}")` 直接进 50 MB × 3 backup 文件。
**Fix**: `_RedactFilter` 扫已知 secrets 模式 attach 到所有 handlers。

### P-084 — `core/logging.py` RotatingFileHandler 多进程不安全
docstring 自承,但无 runtime enforcement;子进程忘记 `console_only=True` 即 rotation race。
**Fix**: 子进程 / 同文件并发场景强制 `concurrent-log-handler` 或 per-PID 文件名。

### P-085 — `core/logging.py:50-59` 第三方 logger level 全局覆盖
每次 setup_logging 都强制 transformers/urllib3 → ERROR;无 opt-out。
**Fix**: `quiet_third_party: bool = True` 参数。

### P-086 — `core/reporting.py:199` `np.issubdtype` 在 nullable Int64 失败
```python
elif np.issubdtype(dtype, np.number):
```
pandas `Int64Dtype` 非 numpy 子类 → False, 跳过数值统计分支。
**Fix**: `pd.api.types.is_numeric_dtype(dtype)`。

### P-087 — `core/reporting.py:240` `string[pyarrow]` 未被分类
```python
elif pd.api.types.is_object_dtype(dtype) or _is_categorical(dtype):
```
pandas 2.1+ pyarrow-backed string 既不是 object 也不是 Categorical → 全分支跳过, 无 top-K 统计。
**Fix**: 加 `is_string_dtype(dtype)`。

### P-088 — `core/data_versioning.py:67-74` `default=str` 跨平台 hash 飘移
```python
json.dumps(config, ..., default=str)
```
`WindowsPath('a/b')` → `"a\\b"`, `PosixPath('a/b')` → `"a/b"`。同逻辑配置跨平台不同 SHA-256。
**Fix**: 预 normalize Path → POSIX 字符串。

### P-089 — `core/data_versioning.py:245-257` `verify_data_integrity` 缺失输入静默 pass
```python
for input_file, expected_hash in metadata.get("input_hashes", {}).items():
    if Path(input_file).exists():
        ...check hash...
# missing file → silently skipped
return True
```
全部 input 被删的情况下仍返 True + 输出"验证通过"。
**Fix**: 缺失 input 视为 verification failure。

### P-097 — `pyproject.toml:218-249` ruff ignore 全局 20+ 规则
E712 (10 处), F541 (193 处), 等全局忽略。E712 仅在 pandas 场景需要, 全局屏蔽掩盖非 pandas 真 bug。
**Fix**: 拆 per-file-ignores;F541 单次 `ruff check --fix --select F541` 修。

### P-098 — `.pre-commit-config.yaml:19-43` 仅 2 hook
仅 ruff + check-prompt-headers;无 `detect-private-key / check-added-large-files / check-yaml`。`.env` 二次防线缺失。
**Fix**: 加 `pre-commit-hooks` repo 3 hook (上述列表)。

---

## 六、⚪ Low 真实问题 (15 条 — P3)

### P-092 — `27c_placebo_and_alt_anchor.py` orphan shim
不在 STAGES_MAIN 也不在 OUTPUT_REGISTRY。
**Fix**: 注册或下沉至 `scripts/audit/`。

### P-093 — `scripts/replace_v6_to_v3.py` 全 no-op + 硬编码 F: 路径
**Fix**: 直接 `git rm`。

### P-094 — `news_process/models_output.json` 死文件
31 行 yunwu 模型 dump,无任何 .py 引用。
**Fix**: 移至 docs/reference/ 或删除。

### P-095 — README scripts 布局漂移
`news_process/scripts/legacy/` 不存在,但 README L106-110 声称存在。`update_deps.sh` bash 在 Windows-PS 项目。
**Fix**: 同步 README 实情。

### P-101 — 根 `.gitignore` 缺 `.gemini/ .cursor/`
两目录在仓库根存在但未屏蔽;`.gemini/skills/...` 数百文件可能误 commit。
**Fix**: `.gitignore` 追加两行。

### P-102 — CI baseline 阈值 820 远低于实际 2088
1268 测试静默回归窗口。
**Fix**: 阈值上调至 1900+ 或动态读最近基线。

### P-103 — CLAUDE.md L38 test baseline 1629 过期
实测 `pytest --collect-only` = **1804 fast / 284 integration / 2088 total**。漂移 +459 fast / +175 total。
**Fix**: 同步 CLAUDE.md / README / CI workflow 文档。

### P-104 — `docs/methodology/plan_e_p7_dual_track_validation.md` 不存在
3 validation 模块引用但 `Glob` 0 hits。
**Fix**: 创建 skeleton 文档或改引用 GitHub issue。

### P-105 — `paper_registry` 缺 3 个新 paper
缺 `bank_fintech_collab` (P5) / `bank_media_disagreement` (第10) / `bank_news_clarity` (第11)。
**Fix**: 注册前先解决 P-106。

### P-106 — 两 paper 缺 `analysis.py / figures.py / tables.py`
`bank_media_disagreement` 与 `bank_news_clarity` 仅有 `__init__.py + paper_spec.yaml + stata_templates/`;CLAUDE.md 已宣传立项,但实际是 skeleton-only。
**Fix**: stub `analysis.py` 或文档明确 M5 pending,registry 暂不收。

### P-107 — `stata_runner.py:570-579` 硬编码 14 .do
derivative paper 仅 4-9 .do 即被 false-fail。
**Fix**: 参数化 `expected = paper_spec.expected_do_files`。

### P-108 — 105 个 Stata 模板缺 `set processors`
`Grep "set processors" papers/` = 0。MP 19.5 64-core license 下 bootstrap/rwolf 单线程跑。
**Fix**: `00_master.do.tmpl` 加 `capture set processors 64`。

### P-109 — `version 19` + `46_panel_yearly_core.dta` (IC ≤2048) 矛盾
`version 19` 排除 Stata 18 用户;但 IC core split 只为 IC 用户准备 — 受众不重叠。
**Fix**: 二选一: (a) 删 IC split → 用 `_full.dta`; (b) 降 `version 17`。

### P-110 — `papers/_common/figures.py:67-70` 无 CJK 字体 fallback
```python
'font.family': 'serif',
'font.serif': ['Times New Roman', 'DejaVu Serif', 'serif'],
```
中文 label 渲染豆腐块。`core/plotting.py::configure_matplotlib_chinese_fonts` 已存在但未被调用。
**Fix**: 在 `apply_publication_style` 调用 `configure_matplotlib_chinese_fonts()` 把发现的 CJK 字体 prepend 到 stack。

---

## 七、横切集群 (整改路径建议)

### Cluster A — Stage 19 `executive_ner.py` 完全失能 (P-006/P-007/P-008/P-016/P-022/P-025)
6 个 bug 同住一文件,全被 `except Exception` 静默吞掉。CLAUDE.md L29 "S1.4 LLM 真接入" **在生产中不成立**。单文件 PR 可同修。

### Cluster B — Pandas merge 防御 (P-014/P-015)
8 + 6 处 merge 全无 `validate=`。一次 sweep PR ≈ 85 行修改可覆盖整个 pipeline。

### Cluster C — HTTP retry 模板化 (P-009/P-022/P-023/P-024/P-030)
`tone_llms.py` 已有 bounded 退避基线 + `build_llm_connector`;5 处 callsite 应同模板化:
- `policy_alignment.py` / `benefit_society.py` / `strategic_diff.py` 三处 while True
- `executive_ner.py` 零重试
- `network_spillover.py` 零重试
- `v7_wz_audit.py` 零重试

### Cluster D — LLM archive 完整性 (P-030 + P-045 + P-010)
V4 F-P2.1 reproducibility 主张有 3 处独立漏洞:跨进程 race + cache-hit 不入档 + 全文+银行名无 redaction。三 fix 合并为一次 archive layer 重构。

### Cluster E — 数值解析 + 词典 (P-038/P-039/P-041/P-042)
四 bug 集中在 `pipeline/sentiment/` 4 文件;P-042 (两万亿 5-order 误差) 是最严重。建议引入 `cn2an` 库 + jieba token 精确匹配 + 词典 fail-loud 加 sweep。

### Cluster F — 第10/11 paper 工程化空缺 (P-017/P-105/P-106/P-109)
4 个 finding 同根: 新 paper 处占位符状态但 CLAUDE.md 已声称立项;F:/ 硬编码 + version 19 + IC 矛盾形成 silent reality gap。

### Cluster G — 文档与基线漂移 (P-003/P-095/P-102/P-103/P-104)
单次"文档同步 PR"可关 5 条:
- pyproject.toml 版本 → 3.7.1
- README scripts 布局描述
- CI baseline 820 → ~1900
- CLAUDE.md test baseline 1629 → 1804
- Plan E P7 doc 创建或重定向引用

### Cluster H — core/dag/schemas 一致性 (P-069/P-070/P-071/P-072)
4 个 finding 都在 `core/dag.py`,可一次模块底加 `_validate_dag_invariant()` + 默认 timeout 调整 + 谓词 default 统一。

### Cluster I — 编码 + 字体 (P-061/P-110)
2 处编码/字体修复, 一次 sweep。

### Cluster J — pre-commit + secret 防线 (P-098/P-101 + 历史 P-001)
加 `detect-private-key / check-added-large-files / check-yaml` 三 hook + `.gitignore` 加 `.gemini/.cursor/`,补全二次防线。

---

## 八、整改优先级建议

| 阶段 | 时长 | 关闭 finding | 目标 |
|---|---|---|---|
| Sprint 1 | 1 周 | P-003, P-004, P-005, P-006, P-007, P-008, P-016, P-017, P-022 | Fresh install + stage 19 修复 |
| Sprint 2 | 1 周 | P-009, P-014, P-015, P-018, P-042 | 数据完整性 + retry 收敛 |
| Sprint 3 | 2 周 | Cluster D (P-010/P-030/P-045) + Cluster E + Cluster H | 复现性 + LLM 层 + DAG SSOT |
| Sprint 4 | 1 周 | Cluster F (P-105/P-106 等) + Cluster G + Cluster J | 文档同步 + paper 工程化 + 二次防线 |
| 持续 | — | 其余 Medium/Low | 跟版本节奏整改 |

---

## 九、评审结论

1. **110 → 73 真实问题** (37 剔除率 33.6%) — 反映了二次 / 三次复核能有效过滤过宽的初判,但同时也确认大部分原 finding 是真问题。
2. **15 P0 / 17 P1 / 26 P2 / 15 P3** — 严重性分布合理,无 false alarm 占主导。
3. **顶级风险集群**: Stage 19 完全失能 (6 bug) + Stata 模板硬编码 (2 paper) + 包发布无法 install (P-003~P-005) — 这三处 silent reality gap 直接挑战 CLAUDE.md/README 的可信度。
4. **核心建议**: 优先一周内闭合 Sprint 1 (9 条 P0), 让 fresh checkout 能跑通 + stage 19 真正工作。其他可按版本节奏。

---

**附录**: 完整复核轨迹见同目录 `AUDIT_REPORT.md` (原始 110 条) 与 `AUDIT_REPORT_VERIFIED.md` (二轮 PARTIAL 细节)。本文档 `AUDIT_REPORT_FINAL.md` 是最严格的最终交付物,所有 73 条均经 3 轮独立验证 + 源码 quote 证据 + 二元判定。
