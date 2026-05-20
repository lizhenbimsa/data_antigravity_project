# news_process 系统评审报告 (AUDIT_REPORT)

**评审日期**: 2026-05-19
**评审人**: Claude Opus 4.7 (1M context)
**范围**: `F:\WiseSearch\data_antigravity_project\news_process\` + 仓库根
**目标**: ≥100 评审角度 / ≥100 真实问题
**约束**: 只读、不修改源代码
**方法**: 主代理协调 + 6 个并行子代理(安全 / core / panel数据 / LLM/NLP / 测试与papers / 依赖文档)

---

## 角度清单 (共 107)

1. 密钥与凭据管理 (.env)            2. .gitignore 完整性                  3. pyproject vs requirements drift
4. requirements.lock 与 Python 版本   5. 缺失运行时依赖 (transitive 依赖)   6. Python 版本兼容性 (3.10 vs 3.13/3.14)
7. Pipeline 主入口 (subprocess env)   8. DAG SSOT 完整性                    9. STAGES_MAIN ↔ OUTPUT_REGISTRY
10. EXPECTED_NO_OUTPUT_STAGES 覆盖    11. StageSpec depends_on 缺失          12. shim 计数声明
13. 日志泄漏敏感信息                  14. LLM 调用错误处理 (retry/backoff)  15. LLM 缓存键空间冲突
16. HTTP 重试 / 指数退避              17. HTTP 超时设置                      18. async/await 一致性
19. subprocess 调用安全               20. Pickle / joblib.load 安全          21. Pandas dtype 一致性
22. Parquet schema 演化               23. Stata IC 列数上限                  24. stata_export 列截断
25. 浮点比较与 NaN                    26. 路径分隔符 (Win vs POSIX)          27. 路径遍历 / 文件名注入
28. 配置硬编码 vs YAML                29. jieba 版本/单例                    30. HF 模型下载与 cache
31. FinBERT2 缺失 graceful skip       32. 测试覆盖 (test vs source)          33. test fixture 依赖外部 API
34. Golden snapshot 验证              35. DAG consistency 集成测试           36. 文件锁
37. 并发竞态                          38. joblib Parallel 内存               39. 资源未释放
40. 异常被吞                          41. logging 配置一致性                 42. structured logging
43. run_id 冲突                       44. Pandas merge validate              45. Pandas merge 列冲突
46. float → int 静默截断              47. 时区/日期                          48. 中文编码 (UTF-8 BOM)
49. Excel 读取 dtype 推断             50. CSV 注入                           51. YAML safe_load
52. JSON deserialize 大小             53. Random seed 全局 vs 局部           54. Numpy random state
55. scikit-learn random_state         56. Permutation 可重现                 57. 跨平台 .dta
58. pyreadstat 版本                   59. Stata 模板注入                     60. Stata variable label ≤80 bytes
61. Stata strL                        62. Stata maxvar                       63. version 19 限制
64. 词典覆盖率审计                    65. stopwords 完整性                   66. tokenizer 一致性
67. Numerical Intensity 公式          68. LM 词典空回退                      69. Forward looking 双门控
70. Tier weight runner 接入           71. EPU graceful fallback              72. BERTopic K 选择
73. Krippendorff α matrix             74. HTMT 双 cutoff                     75. Cronbach α
76. 1000-rep permutation              77. CLI 标志                           78. shim 命名 regex
79. 数据版本化                        80. 死代码 / unused                    81. TODO / FIXME
82. 文档漂移 / CLAUDE.md              83. AI Disclosure 模板                 84. paper_spec schema
85. tables.py output_format           86. figures.py savefig dpi             87. matplotlib 后端线程
88. Mocking external APIs             89. pytest-asyncio 配置                90. pytest markers strict
91. test 文件命名一致                 92. data/processed parquet 命名        93. data/raw 校验
94. PII / 内容泄漏                    95. HTTPS 强制                         96. TLS 证书校验
97. 命名混乱 (中英)                   98. 魔法数字                           99. 循环依赖 / 反向依赖
100. pre-commit 配置                  101. License / 第三方归属              102. CI 基线
103. CSS 注入 (NA)                    104. XSS / CSRF (NA)                   105. SQL 注入 (NA)
106. 设置处理器 (Stata MP cores)      107. 验证 stage 是否真 mock

---

## 真实问题清单 (共 110, 按严重程度分组)

> 每条记录: 文件 / 行号 / 触发条件 / 后果 / 建议修复。

---

### 🔴 Critical (P0 — 立即修复)

#### P-001 — `.env` 含真实生产密钥
- **file**: `news_process/.env`
- **line**: 6, 8
- **category**: secrets-在-tracked-path
- **trigger**: 真实 `YUNWU_API_KEY=sk-g6KIp...` 与 `DEEPSEEK_API_KEY=sk-71aff...` 出现在受版本控制目录中(虽然 `.gitignore:34` 已忽略 `.env`,但若任何历史 commit 包含过它就永久泄漏)。
- **impact**: 任何人 clone 仓库即可拿到 LLM 调用权;DeepSeek 与 yunwu 账户余额暴露。
- **fix**: `git log --all --full-history -- news_process/.env` 检查是否曾入历史;若入,需 `git filter-repo` 改写并轮换两把 key。

#### P-002 — yunwu key 前缀写入受版本控制 JSON
- **file**: `news_process/scripts/audit/_replan_v5_evidence/B_F1_0b_yunwu_fallback_probe.json` 等
- **line**: 4 (B_F1_0b...), 99 (.py 写入逻辑); `A5_data_state_audit.md:74-77` 含完整前缀+后缀
- **category**: secrets-在-tracked-file
- **trigger**: `API_KEY[:12] + "..."` 写入 JSON, git ls-files 已含。
- **impact**: 公开镜像直接暴露 11 字符 key 前缀,缩小爆破空间。
- **fix**: `_replan_v5_evidence/*.json` 加 .gitignore + `git filter-repo` 抹除 + 将前缀改成 `sha256(key)[:8]`。

#### P-003 — `pyproject.toml::version = "3.3.0"` 与 CLAUDE.md 声称 v3.7.0 严重不一致
- **file**: `pyproject.toml`
- **line**: 7;`news_process/__init__.py:68` 同步 `__version__ = "3.3.0"`
- **category**: version-drift
- **trigger**: `pip install -e .` 安装的版本是 3.3.0,但 CLAUDE.md / README 均称当前 v3.7.0+v2.3。
- **impact**: 任何下游工具 (`pip show news-process`)、CI smoke 测试均看到错误版本。
- **fix**: 同步 bump 到 "3.7.1"。

#### P-004 — `requests` 未在 pyproject 中声明,但被生产代码 import
- **file**: `pyproject.toml` (依赖段) ↔ `pipeline/sentiment/executive_ner.py:116`, `scripts/data_acquisition/banking_outcome_dry_run.py:268`
- **line**: pyproject 36-71;callsite 见左
- **category**: missing-runtime-deps
- **trigger**: `pip install -e .` (CLAUDE.md 推荐路径) 不显式安装 requests,仅通过 huggingface-hub 的 transitive 拉到。
- **impact**: 任一 transitive 依赖换 backend(httpx),`import requests` 即 ImportError 烧光 D4 stage。
- **fix**: `requests>=2.31.0,<3.0.0` 加入 `[project].dependencies`。

#### P-005 — D-group stages 17/18/39f 依赖被 comment-out
- **file**: `news_process/requirements.txt:115-119`
- **line**: 115-119 (bertopic / umap-learn / hdbscan / faiss-cpu / krippendorff 全注释)
- **category**: missing-runtime-deps
- **trigger**: `pipeline/text/article_topic.py` 等 import,但 fresh checkout `pip install -r requirements.txt` 不装。
- **impact**: 阶段 17/18/39f ImportError;掩盖在 lazy import + try 中只在运行时炸。
- **fix**: 取消注释或加 `[d-group]` optional-extras,然后 `pip install -e ".[d-group]"`。

#### P-006 — `pipeline/sentiment/executive_ner.py` `LLMCache` 构造参数错误
- **file**: `pipeline/sentiment/executive_ner.py`
- **line**: 188-200
- **category**: API-契约-完全错位
- **trigger**: `LLMCache(namespace=cache_namespace)`,但实际签名是 `LLMCache(db_path)`;`cache.get(cache_key)` 单参数版本不存在(真签名 `get(model_id, prompt, prompt_version=...)`);又被 `except (ImportError, TypeError, AttributeError)` 吞掉。
- **impact**: 阶段 19 D4 CEO NER **每次调用零缓存命中**;~$6-12 yunwu 预算每次重跑全跑掉;且无任何告警。
- **fix**: 改成 `LLMCache(CACHE_DB_PATH).get(model_id=..., prompt=..., prompt_version='d4_v0')`;移除宽 `except`。

#### P-007 — `pipeline/sentiment/executive_ner.py` `archive_record` 关键字错位
- **file**: `pipeline/sentiment/executive_ner.py`
- **line**: 208-214
- **category**: silent-archive-failure
- **trigger**: 调用 `archive_record(stage=..., model=..., prompt=..., response=..., metadata=...)`,真签名要求 `cache_key/model_id/model_version/response_raw/prompt_version/temperature/api_endpoint/http_status`。
- **impact**: 每次调用 `TypeError` 被宽 except 吞掉;V4 F-P2.1 reproducibility 100% 沉默违反——审稿人将以为归档生效。
- **fix**: 用真参数重写。

#### P-008 — `hash(prompt)` 作为 cache key (PYTHONHASHSEED 随机化)
- **file**: `pipeline/sentiment/executive_ner.py:190`
- **line**: 190
- **category**: cache-poisoning + 跨进程非确定性
- **trigger**: 默认 PYTHONHASHSEED=random,每进程不同。
- **impact**: 同 prompt 跨进程产生不同 key;cache 永不命中;$12 预算每运行重花一次。
- **fix**: `hashlib.sha256(prompt.encode()).hexdigest()` 对齐 `LLMCache.make_key`。

#### P-009 — `policy_alignment.py` (+benefit_society/strategic_diff) 无界 `while True` 重试
- **file**: `pipeline/filtering/policy_alignment.py:251-292`;镜像 `pipeline/features/benefit_society.py:292-366`、`pipeline/features/strategic_diff.py:542-609`
- **category**: http-unbounded-retry / DoS
- **trigger**: 任何 429 / 5xx 持续返回。
- **impact**: stage 15/26/27 永不退出;最终被 orchestrator timeout=3600 SIGKILL,但 SQLite cache 半写状态被留下。
- **fix**: `for attempt in range(MAX_RETRIES):` + 耗尽后 `raise RuntimeError`,与 tone_llms.py 一致。

#### P-010 — LLM archive 存全文+银行名,无 PII/版权 redaction
- **file**: `pipeline/llm_archive/archive.py:59-262`
- **line**: 59-72, 119-158, 202-262
- **category**: PII-and-content-leakage
- **trigger**: 设计要求 prompt 字段必填;tone_llms 填进完整 Chinese 文章;`.gitattributes:36` 标记 `data/llm_archive/responses/*.jsonl` 为 LFS,意图发到 reviewer / 期刊。
- **impact**: 40 万篇带版权的新闻全文随 replication 包发出;银行名/高管名(stage 19 NER 输出)同包发布,缺乏 opt-out。
- **fix**: 拆分 archive 为 (a) 模板+内容 hash,(b) 可选加密存内容 blob。提供 `content_redacted` 模式。

#### P-011 — 路径遍历 (`bank_name` 拼到 pdf_path)
- **file**: `scripts/data_acquisition/banking_outcome_dry_run.py:352`;镜像 `papers/benefit_society/ncd_pdf_downloader.py:132,178`
- **category**: path-traversal
- **trigger**: `pdf_path = pdf_dir / bank_name / f'{year}.pdf'`,`bank_name` 来自用户 CSV;`..\..\` 在 Windows 解析为目录上级。
- **impact**: 读/写任意路径;`bank_id='..\\..\\..\\Users\\lizhe\\.env'` 可读取用户级 secrets。
- **fix**: 白名单字符 `re.sub(r'[^一-龥A-Za-z0-9_-]', '', bank_name)` + `Path.resolve().is_relative_to(pdf_dir.resolve())` 二次确认。

#### P-012 — `pipeline/text/article_staleness.py` lambda 闭包 bug,`highstale_*` 永远是全局均值
- **file**: `pipeline/text/article_staleness.py:245-257`
- **category**: groupby-late-binding-lambda
- **trigger**: `lambda s, c=col: (article_df[c] > 0.9).mean()` 闭包绑 `c` 正确,但函数体引用外层 `article_df[c]` 而非 group slice `s`。
- **impact**: `highstale_*` panel 列对所有 bank-year 同一常数,完全摧毁 staleness 回归。
- **fix**: 改成 `lambda s: (s > 0.9).mean()`。

#### P-013 — `pipeline/text/article_staleness.py` Faiss + NaT 比较
- **file**: `pipeline/text/article_staleness.py:217-234`
- **category**: NaT-< 比较行为变更
- **trigger**: `dates.iloc[window_start_idx] < cutoff` 当 dates 含 NaT 时返回 NaT,`while NaT < cutoff` 视为 False,窗口永不前进。
- **impact**: 日期缺失的文章其滚动窗口涵盖所有历史向量;staleness 分数被无意义地放大。
- **fix**: 进入循环前 `df_sorted = df_sorted[dates.notna()]`。

#### P-014 — `pipeline/panel/encode.py` 8 个 `panel.merge(...)` 全无 `validate=`
- **file**: `pipeline/panel/encode.py:836, 915, 941, 996, 1064, 1117, 1177, 1231`
- **category**: cartesian-explosion-风险
- **trigger**: cat_panel 任意一边 (target_bank, year) 重复(如 stage 21 重写产 dup),即 fan-out。
- **impact**: panel 行数翻倍/翻数倍,后续回归被双计。识别度只到 968 行 assert,但不 abort。
- **fix**: 每个 merge 加 `validate='one_to_one'`。

#### P-015 — `pipeline/panel/runner.py` 双循环 merge 无 `validate=`
- **file**: `pipeline/panel/runner.py:1184-1185`
- **category**: many-to-many silent merge
- **trigger**: 2 tracks × 3 percentiles 嵌套;`_quadrant_agg` 任一 (target_bank, year) 重复即指数 fan-out。
- **impact**: 单点重复在 6 次循环后将 panel 放大 64×。
- **fix**: `validate='one_to_one'` + 调用前 assert key 唯一。

#### P-016 — Stage 19 (`19_executive_ner.py`) `always_enabled` + 6h timeout + $12 LLM 预算无 opt-in
- **file**: `core/dag.py:195-203` (StageSpec stage 19)
- **category**: cost-bombshell
- **trigger**: fresh checkout `python run_pipeline_function.py`,即触发完整 NER 调用 40 万篇文章。
- **impact**: 单次 18h × $12+(yunwu 账户) 透支可能性,无确认门。
- **fix**: 加 `enabled_when=ner_enabled` 谓词;`config/sentiment.yaml::executive_ner.enabled` 默认 false。

#### P-017 — Stata 模板硬编码本机绝对路径
- **file**: `papers/bank_media_disagreement/stata_templates/00_master.do.tmpl:14`、`papers/bank_news_clarity/stata_templates/00_master.do.tmpl:14`、`replication/code/00_master.do:13`
- **category**: hardcoded-path / replication-break
- **trigger**: `local project_root "F:/WiseSearch/data_antigravity_project"` 烙进模板。
- **impact**: 任何 reviewer / 外部协作者运行 replication 立即"directory not found"。
- **fix**: `local project_root "{{PROJECT_ROOT}}"` + 走 `_substitute_placeholders`。

#### P-018 — Stage 22 dual-track cache 共享同一 key (full ↔ ctx)
- **file**: `pipeline/sentiment/tone_llms.py:416, 446`
- **category**: cache-key 命名空间 collision
- **trigger**: 当 `content_ctx == content_full` (ctx 物化 fallback 路径)且 `prompt_version` 相同。
- **impact**: 双轨实际坍塌为单轨;但 panel 仍标记"真双轨"——A/B ablation 在这些行上无意义。
- **fix**: cache key 引入 `track ∈ {full, ctx, title}`。

#### P-019 — `os.environ.copy()` 把所有 secrets 传给每个子进程
- **file**: `core/stage.py:186-211`
- **category**: secret-over-propagation
- **trigger**: 任何 stage 不需 LLM 时(00/45/46/51/53),依然继承 YUNWU/DEEPSEEK/EMBEDDING/WIND key。
- **impact**: 违反 least-privilege;若 stage 内任何 transitive 依赖被攻破即拿到所有 key。
- **fix**: `StageSpec.required_env=[...]` 白名单驱动 env 注入。

#### P-020 — LLM cache 缺 prompt_version 必填 (`prompt_version="v0"` 默认)
- **file**: `core/caching.py:181` (默认参数)
- **category**: silent-stale-cache-hit
- **trigger**: 调用方忘加 `prompt_version=PROMPT_VERSION`,prompt 文案变更后仍命中老 cache。
- **impact**: 静默拿到旧 prompt 的判断;P3-17 设计意图被绕过。
- **fix**: `prompt_version` 改为 keyword-only 必填,无默认。

#### P-021 — `policy_alignment.py` (策划性) 假 graceful — 永不收敛
- **file**: `core/locking.py:81`
- **category**: Windows-partial-file-lock + truncate-race
- **trigger**: `open('w', ...)` 立即 truncate,再 `msvcrt.locking(LK_NBLCK, 1)` 仅锁 1 byte。两进程同时 'w' 都先 truncate,后只一个拿到锁,另一个已破坏文件。
- **impact**: loser 进程崩,sidecar 错位;诊断假象"占用者: 未知"。
- **fix**: 用 `'a+'` 模式打开,不 truncate;或 `portalocker` 跨平台抽象。

---

### 🟠 High (P1 — 近期修复)

#### P-022 — Stage 19 (`executive_ner.py`) 无重试无 backoff
- **file**: `pipeline/sentiment/executive_ner.py:102-150` (`_yunwu_chat_sync`)
- **trigger**: 任何 429/5xx/timeout。
- **impact**: 静默返回 `''` → 该文章无 CEO 提及;40 万 × 5% 错误率 = 2 万文章静默无信号。
- **fix**: `for attempt in range(MAX_RETRIES): ... time.sleep(RETRY_DELAY * 2**attempt)`。

#### P-023 — `pipeline/panel/network_spillover.py` embedding 单次 POST 无重试
- **file**: `pipeline/panel/network_spillover.py:999-1015`
- **trigger**: 任何瞬时 429。
- **impact**: 单 429 抹除整轮工作(因为 batch 还未 flush)。
- **fix**: 与 tone_llms 一致的指数退避包装。

#### P-024 — `scripts/migrate/v7_wz_audit.py` 单次 POST + key 回读路径暴露
- **file**: `scripts/migrate/v7_wz_audit.py:75-100`
- **trigger**: 任何非 200;`_read_env_key` 手解析 .env 不展开 `${VAR}`。
- **impact**: 异常 traceback 可能含 `Authorization: Bearer <key>`(取决于 logger);`EMBEDDING_API_KEY=${YUNWU_API_KEY}` 写法被解析为字面量字符串,审计假阴性。
- **fix**: 切换 `dotenv.dotenv_values`;为异常 mask `Authorization`。

#### P-025 — `executive_ner.py:144` 全 response 文本 debug-log 可能含 key
- **file**: `pipeline/sentiment/executive_ner.py:144`
- **trigger**: yunwu 4xx 错误体偶尔回显 bearer 前缀。
- **impact**: 启用 DEBUG 时写入 `logs/runs/<id>/19_executive_ner.log`。
- **fix**: 复用 tone_llms 的 `_summarize_auth_failure` mask。

#### P-026 — `scripts/data_acquisition/banking_outcome_dry_run.py:286-288` UA 采用弱随机 `random`
- **file**: 同上
- **trigger**: 反爬 UA 轮换。
- **impact**: 周期可预测,服务端可指纹识别;同一 wall-clock 出相同序列。
- **fix**: `secrets.choice(...)` 或 `random.SystemRandom().choice(...)`。

#### P-027 — `core/caching.py` LLM cache 永不淘汰
- **file**: `core/caching.py:137-176`
- **trigger**: prompt_version 多次迭代 / temperature 调试。
- **impact**: SQLite 文件单调增长到多 GB,v0 namespace 永远可达;page-cache 抖动。
- **fix**: 新增 `prune(keep_days=90)` 方法 + 定期维护。

#### P-028 — `core/caching.py:207-216` `repr(float(temperature))` 跨平台不稳定
- **file**: `core/caching.py:207-216`
- **trigger**: caller 传 `np.float32(0.0)` vs 纯 Python `0.0`。
- **impact**: 相同温度产 cache miss。
- **fix**: `f"{float(temperature):.17g}"`。

#### P-029 — `core/caching.py` v0 fallback 不含 temperature → 跨温度污染
- **file**: `core/caching.py:283-296`
- **trigger**: v1 miss + caller 传 `temperature=0.0` 触发 v0 fallback,而老 v0 entry 可能温度 0.7。
- **impact**: stage 21 在 v0 fallback 路径上拿错温度的旧响应;Lopez-Lira 2023 确定性保证沉默违反。
- **fix**: v0 fallback 仅在显式 unlock 时启用;或在 v0 lookup 必带 temperature。

#### P-030 — `pipeline/llm_archive/archive.py` JSONL multi-process race
- **file**: `pipeline/llm_archive/archive.py:135-158`
- **trigger**: orchestrator 子进程并行写同日 JSONL。
- **impact**: Windows 无 PIPE_BUF 保证 → 行交错 → 损坏 JSONL。
- **fix**: `fcntl.flock` / `msvcrt.locking` 或 per-PID 文件名 + 合并。

#### P-031 — `pipeline/llm_archive/manifest.py:39-54` `\n` 计数与 record 错位
- **file**: `pipeline/llm_archive/manifest.py:39-54`
- **trigger**: 末行无 `\n` (写一半被 kill)。
- **impact**: manifest 报 N-1 行,replay 报 N 条,cross-check 误报。
- **fix**: `if buf.endswith(b'\n'): count else count+1`。

#### P-032 — `pipeline/audit/cross_media_alpha.py` Krippendorff α matrix 全 NaN 行未剔除
- **file**: `pipeline/audit/cross_media_alpha.py:153-203`
- **trigger**: outlet 报道在事件窗口外。
- **impact**: 第 10 篇 paper 主 treatment `cross_outlet_tone_variance_full` 计算偏差。
- **fix**: 进 `krippendorff.alpha` 前 drop all-NaN rows;`n_valid_items >= 3` 严格化。

#### P-033 — `pipeline/audit/lm_discriminant_validity.py` seed=42 跨构念复用
- **file**: `pipeline/audit/lm_discriminant_validity.py:129-162`;同 39c 行 322-325 / 39d 行 46
- **trigger**: 三 stage 各自 hardcode 42。
- **impact**: 各构念的 null 分布相关,p-value 在多重校正下假精确。
- **fix**: `SeedSequence(42).spawn(N_stages)`。

#### P-034 — `pipeline/audit/lm_discriminant_validity.py` HTMT 常量列 → "fail"
- **file**: `pipeline/audit/lm_discriminant_validity.py:93-110`
- **trigger**: LM 子词典空(v0.1 stub)即 std=0 → corr NaN → verdict 落到 `'fail'`。
- **impact**: G-A1.2 误报 "FAIL (need expert audit)",真因是空字典。
- **fix**: 增加 NaN branch → `'nan_undefined'`(39d 已修,需同步)。

#### P-035 — `pipeline/audit/lexical_discriminant_validity.py` 单 rng 跨对儿复用
- **file**: `pipeline/audit/lexical_discriminant_validity.py:184-222`
- **trigger**: 嵌套 pair 循环。
- **impact**: pair 间 null 非独立 → Bonferroni/Holm 失效。
- **fix**: `SeedSequence.spawn(n_pairs)`。

#### P-036 — `pipeline/features/strategic_diff.py` aiohttp 无连接器限流
- **file**: `pipeline/features/strategic_diff.py:541-615`
- **trigger**: 长 batch + Windows TIME_WAIT 累积。
- **impact**: `OSError [WinError 10055]` 套接字耗尽,跨小时 batch 失败。
- **fix**: 与 `build_llm_connector` 一致的 `TCPConnector(limit=…, limit_per_host=…, keepalive_timeout=60)`。

#### P-037 — `pipeline/features/strategic_diff.py` BERTopic / LDA K 硬编码
- **file**: `pipeline/features/strategic_diff.py:419-467`
- **trigger**: `K = max(10, n_banks // 30)` → 永远 10。
- **impact**: 缺敏感度审计;v3.7.0 D1 BERTopic 已立项但旧 LDA 仍 run。
- **fix**: 从 `CONFIG['lda_params']['n_topics']` 读;sidecar 写 perplexity。

#### P-038 — `pipeline/sentiment/forward_looking.py` `望` substring 匹配 `希望/绝望`
- **file**: `pipeline/sentiment/forward_looking.py:96-112` + 词集 49-71
- **trigger**: 任何 "希望" / "展望未来"。
- **impact**: A2 Li 2010 JAR FLS 指标膨胀 → `frac_fls_*` 高假阳性。
- **fix**: 改用 jieba token 精确匹配 + retrospective filter (`已 / 过去 / 上`)。

#### P-039 — `pipeline/sentiment/lm_non_sentiment.py` 空词典静默回退
- **file**: `pipeline/sentiment/lm_non_sentiment.py:60-77`
- **trigger**: `lm_non_sentiment_dicts.json` 部署缺失。
- **impact**: `uncert_frac_*` 全 0.0;HTMT 退化 NaN;无 WARNING。
- **fix**: 缺文件即 `raise RuntimeError`(或至少 logger.error)。

#### P-040 — `core/text/cn_text_utils.py` 句子分隔正则 ASCII `.` 误切小数
- **file**: `core/text/cn_text_utils.py:98-100`
- **trigger**: "利率 3.5%" / "1.5亿" / "U.S."。
- **impact**: 句子计数膨胀 → v2.3 G-A2.1/A1.1 分母被 inflate。
- **fix**: 与 `numerical_intensity.py:44` 的 `(?<!\d)[。！？.!?](?!\d)` 对齐。

#### P-041 — `pipeline/sentiment/numerical_intensity.py:175` `(?!元)?` 失效
- **file**: `pipeline/sentiment/numerical_intensity.py:175`
- **trigger**: `(?!元)?` 的 `?` 让 lookahead 总成功 → `元` 永被消耗。
- **impact**: "5 万元" 转 "50000元" 留 `元` 漂浮,部分数值识别错。
- **fix**: 删 `?`,把 `(?!元)` 设为真正断言;或两遍替换。

#### P-042 — `pipeline/sentiment/numerical_intensity.py:96-120` `_cn_number_to_arabic("两万亿")` 错误
- **file**: `pipeline/sentiment/numerical_intensity.py:96-120`
- **trigger**: `"两万亿"` / `"三亿五千万"`。
- **impact**: 5 D0 frozen sample 中 3 个未单元测试覆盖,Hales 2011 CAR Eq.1 数值强度跑偏。
- **fix**: 用 `cn2an` 包,或补三角例单测。

#### P-043 — `pipeline/sentiment/tone_llms.py:590-616` JSON 解析 `except Exception: return {}`
- **file**: `pipeline/sentiment/tone_llms.py:590-616`
- **trigger**: 模型返回非 JSON / 截断 / 叙事性。
- **impact**: 3 模型 ensemble 静默退化为 2 模型,无 per-model 失败计数器。
- **fix**: 失败时 logger.info(prefix) + panel 加 `json_parse_failure_count` 列。

#### P-044 — `pipeline/sentiment/tone_llms.py:521-583` 无账户级 token-bucket
- **file**: `pipeline/sentiment/tone_llms.py:521-583`
- **trigger**: 3 模型 × 2 轨 × 40 万文 = 2.4M 请求,共享 `MAX_CONCURRENCY=10` 信号量,但 pacer per-model。
- **impact**: 多模型同时打高 RPM 触发 yunwu 全账号封禁。
- **fix**: 顶层 `AsyncRateLimiter` 全局 token bucket。

#### P-045 — `pipeline/sentiment/tone_llms.py:450-474` cache 命中路径不入归档
- **file**: `pipeline/sentiment/tone_llms.py:450-474`
- **trigger**: `cache.get` 命中即在 line 418 早 return。
- **impact**: archive 只含首次响应,后续 panel 用 cache 但 archive 无证据 → V4 F-P2.1 reproducibility 部分失效。
- **fix**: archive 增加 `cache_hit: bool` 字段并对每次调用都写。

#### P-046 — `pipeline/preprocess/load.py` Excel 无 `dtype=` 推断飘移
- **file**: `pipeline/preprocess/load.py:112-115`
- **trigger**: 176 个 XLSX 各 shard 推断不同 (str vs datetime)。
- **impact**: `pa.Table.from_pandas` 第二 shard schema 冲突,中止增量加载。
- **fix**: 显式 `dtype={'日期': str, '标题': str, ...}` + 一次性 `pd.to_datetime(..., errors='coerce')`。

#### P-047 — `pipeline/preprocess/dedup.py:154` `pd.to_datetime` 无 format
- **file**: `pipeline/preprocess/dedup.py:154`
- **trigger**: 中文日期格式混杂(`2023-03-15`/`2023年3月15日`)。
- **impact**: 大量 NaT 静默丢弃;真重复跨日逃逸。
- **fix**: `format='mixed', dayfirst=False`;非 NaT 比例 < 95% 即 fatal。

#### P-048 — `pipeline/preprocess/dedup.py:149` `media_weight.astype(int)` 静默截断
- **file**: `pipeline/preprocess/dedup.py:149`
- **trigger**: `media_weights.json` 含 82.5 浮点。
- **impact**: 同 cluster 内排序错位,误丢更高权重媒体。
- **fix**: 保留 float32;sort_values 上排序。

#### P-049 — `pipeline/preprocess/dedup.py:262-267` `df.loc[cluster_ids]` 假设 index 唯一
- **file**: `pipeline/preprocess/dedup.py:262-267`
- **trigger**: `_perform_exact_deduplication` 未 reset_index → 跨 shard 重复 int。
- **impact**: LSH cluster 多取行,误删合法文。
- **fix**: 函数顶 `df = df.reset_index(drop=True)`。

#### P-050 — `pipeline/preprocess/filter.py` 链式赋值
- **file**: `pipeline/preprocess/filter.py:60, 65, 71, 77, 84, 102, 108`
- **trigger**: pandas 2.0 CoW preview / 3.0 严格模式。
- **impact**: 第 105-108 行 schema 统一步静默不做,parquet 第二 shard 拒收。
- **fix**: 每过滤步显式 `.copy()` 或 `.loc[:, col] = ...`。

#### P-051 — `pipeline/panel/encode.py:456-465` 空 df 触发 ValueError
- **file**: `pipeline/panel/encode.py:456-465`
- **trigger**: `df.dropna(subset=['year'])` 空 → `.astype(int)` ok,但 `df['year'].min()` 即 ValueError。
- **impact**: stage 41 在边缘 case 崩,而非生成空 panel。
- **fix**: `if df.empty: return df`。

#### P-052 — `pipeline/panel/encode.py:508-511` 双 NaN 语义混用
- **file**: `pipeline/panel/encode.py:508-511`
- **trigger**: `pos_count` 由 `sum`(skip NA),`n_articles` 由 `count`(也 skip NA),但其他比率(`headline_frac`)用 mean over all rows 含 fail。
- **impact**: 跨 paper 比较分母语义不一致。
- **fix**: 单一约定 + 双列(verified vs total)。

#### P-053 — `pipeline/panel/encode.py:1458-1465` `range(NaN, NaN+1)` 在空 panel 上崩
- **file**: `pipeline/panel/encode.py:1458-1465`
- **trigger**: `balance_panel(panel)` 输入空。
- **impact**: 报 `cannot convert float NaN to integer`,而非空 panel 直通。
- **fix**: 顶部 `if panel.empty: return panel` 保护。

#### P-054 — `pipeline/panel/runner.py` 巨阔 parquet 全列读
- **file**: `pipeline/panel/runner.py:180, 1087, 1546`
- **trigger**: `pd.read_parquet(input_path)` 不带 `columns=`,17M 行 × 150 列。
- **impact**: 内存 peak 远超必要;协作者 32 GB 机器 OOM。
- **fix**: `columns=[<最小集>]` 精挑。

#### P-055 — `pipeline/panel/runner.py:934, 952` STRESS_YEARS hardcoded
- **file**: `pipeline/panel/runner.py:934, 952`
- **trigger**: 用户扩到 2025+。
- **impact**: deposit-insurance post=2015 dummy 全 1 退化;falsification placebo 也偏。
- **fix**: 移到 `config/panel.yaml::policy_events`。

#### P-056 — `pipeline/external/epu_merge.py:147-151` merge 后缺率不校验
- **file**: `pipeline/external/epu_merge.py:147-151`
- **trigger**: 农历/阳历错位 / 月份 1- vs 0-based。
- **impact**: epu_mean_year 大面积 NaN,listwise deletion 抹掉回归。
- **fix**: `assert merged['epu'].notna().mean() > 0.90`。

#### P-057 — `pipeline/external/epu_merge.py:136-141` `.agg('last')` 未排序
- **file**: `pipeline/external/epu_merge.py:136-141`
- **trigger**: 数据未按 (year, month) 排。
- **impact**: 年末 EPU 误取八月值。
- **fix**: `.sort_values(['year','month']).groupby(...)`。

#### P-058 — `pipeline/text/article_topic.py:263-264` `np.stack` 在 ragged list 上崩
- **file**: `pipeline/text/article_topic.py:263-264, 292-293`
- **trigger**: stage 30a 部分行 NaN embedding 被 inner-merge 漏过。
- **impact**: stage 17 6h compute 后才崩,损失工时。
- **fix**: 入栈前 `apply(lambda x: isinstance(x, np.ndarray) and x.shape==(768,)).all()` 校验。

#### P-059 — `pipeline/text/ctx_materializer.py:82-97` `iterrows` 性能与正确性双输
- **file**: `pipeline/text/ctx_materializer.py:82-97`
- **trigger**: 全量 1.5M+ 文。
- **impact**: stage 13 30-60min;v3.6.0 新引入。
- **fix**: 改 `apply(axis=1)` 或预 `to_dict('records')` 批处理。

#### P-060 — `pipeline/filtering/news_bank.py:232` DataFrame dtype 推断飘移
- **file**: `pipeline/filtering/news_bank.py:232`
- **trigger**: joblib 不同 batch 中 `target_bank_mention_count` 在空 shard 为 float (all-NaN),非空为 int。
- **impact**: parquet concat 跨 shard dtype 冲突。
- **fix**: 显式 dtype dict。

#### P-061 — `pipeline/panel/encode_collab.py:332` 默认 encoding=cp936 风险
- **file**: `pipeline/panel/encode_collab.py:332`
- **trigger**: `open(ctx_baseline_path) as f` 无 encoding= → Win 默认 cp936。
- **impact**: UnicodeDecodeError 被宽 except 吞掉,fallback `threshold_low=0.5` 静默用错阈值。
- **fix**: `encoding='utf-8'` + 捕获 UnicodeDecodeError 显式 logger.error。

#### P-062 — `pipeline/panel/stata_export.py:169-201` 标签按字符截断而非字节
- **file**: `pipeline/panel/stata_export.py:169-201`
- **trigger**: em-dash `—` (3 字节) 或中文 (3 字节/字) 在 80-byte 边界处。
- **impact**: 写 .dta 时 invalid UTF-8;低版本 Stata 读时崩。
- **fix**: 字节级游走截断 `while len(label.encode('utf-8'))>77: label=label[:-1]`。

#### P-063 — `pipeline/panel/stata_export.py:350-374` shorten_long_column_names hash 退化
- **file**: `pipeline/panel/stata_export.py:350-374`
- **trigger**: `bartik_type_iv_full_t0_*` 与 `_t1_*` 同 prefix。
- **impact**: 关键 t0/t1 后缀消失,Bartik IV 变体不可区分。
- **fix**: hash 后缀,`new_col[:25] + '_' + md5(col)[:6]`,并写 rename_map。

#### P-064 — `pipeline/panel/export.py:1002-1003` `version=118` 与 Stata 默认 maxvar 不兼容
- **file**: `pipeline/panel/export.py:1002-1003`
- **trigger**: 外部协作者 SE/BE 默认 maxvar=2048。
- **impact**: 无法 `use 40_panel_yearly.dta`。
- **fix**: emit `40_panel_yearly_setup.do`(含 `set maxvar 32767`)。

#### P-065 — `pipeline/panel/export.py:291` 反向依赖 (pipeline→papers)
- **file**: `pipeline/panel/export.py:291`
- **trigger**: `from news_process.papers._common.tables import sanitize_stata_columns`。
- **impact**: kernel 层 import product 层,层级反转,后续 circular import 风险。
- **fix**: 把工具下沉 `pipeline/panel/_stata_helpers.py` 或 `core/text/`。

#### P-066 — `pipeline/panel/iv_did.py:164-172` 两次 .copy() 内存峰值翻倍
- **file**: `pipeline/panel/iv_did.py:164-172`
- **trigger**: 17M × 50 列 → ~6 GB 临时。
- **impact**: 32 GB 机 OOM mid-pipeline。
- **fix**: `df_with_group = df_exploded.assign(_group=...)`。

#### P-067 — `pipeline/panel/risk_taking_outcomes.py:113-117` `.apply(lambda g: g.iloc[-1])` 空 group 崩
- **file**: `pipeline/panel/risk_taking_outcomes.py:113-117`
- **trigger**: 某 (bank, year) 只在 Q1 出现且 dropna 后空。
- **impact**: stage 49 边缘崩。
- **fix**: `.agg({col: 'last'})` 矢量化。

#### P-068 — `pipeline/preprocess/_constants.py:126,137` 无 BOM 处理
- **file**: `pipeline/preprocess/_constants.py:126, 137`
- **trigger**: 用户在 Win Notepad 编辑 `noise_patterns.json` 保存 UTF-8 with BOM。
- **impact**: 第一关键词带不可见 BOM 永远不匹配。
- **fix**: `encoding='utf-8-sig'` 统一。

#### P-069 — `core/dag.py` `enabled` 默认非对称 (True vs False)
- **file**: `core/dag.py:57 vs 67/70-81`
- **trigger**: 配置中漏掉某 key,不同 stage 行为不同(默认 True / 默认 False)。
- **impact**: 维护者难以推理。
- **fix**: 统一选 opt-in (默认 False)。

#### P-070 — `core/dag.py:142-338` 无 import-time 唯一性断言
- **file**: `core/dag.py:142-338` ↔ `core/schemas.py:303`
- **trigger**: 维护者复制 StageSpec 忘改 name。
- **impact**: 重复跑某 stage / 沉默 alias;仅 `test_dag_consistency` 抓。
- **fix**: 模块底加 `_validate_dag_invariant()`。

#### P-071 — `core/dag.py` STAGES_MAIN ↔ OUTPUT_REGISTRY 跨表无 import-time 校验
- **file**: `core/dag.py:142-338` ↔ `core/schemas.py:43-103, 185-204`
- **trigger**: 新 stage 加 STAGES_MAIN 但忘 OUTPUT_REGISTRY。
- **impact**: orchestrator 在 predict-output-files 时才发现,损失数小时计算。
- **fix**: cross-check 下沉至 `schemas.py::_validate_registry_invariant`。

#### P-072 — `core/dag.py` 默认 `timeout=3600` 过紧
- **file**: `core/dag.py:131`
- **trigger**: 新 LLM/embedding stage 未显式覆盖。
- **impact**: 6h+ stage 被 SIGKILL,部分 parquet 残留。
- **fix**: 提高默认 / 强制 LLM 类 stage 显式 `timeout=`。

#### P-073 — `core/config.py:191-204` partial split-mode 死路 fallback
- **file**: `core/config.py:191-204`
- **trigger**: 某 split YAML 暂时缺。
- **impact**: 错误提示建议"删全部 split"会清掉用户进展,然后落到 stub。
- **fix**: 提供 `config/<missing>.yaml.example` + 删 stub fallback。

#### P-074 — `core/config.py:242-254` env placeholder 仅 warn
- **file**: `core/config.py:242-254`
- **trigger**: `.env` 漏 YUNWU_API_KEY。
- **impact**: stage 21 拿空字符串,4h 后才 401。
- **fix**: `REQUIRED_ENV_VARS = ('YUNWU_API_KEY',)` 缺即 raise。

#### P-075 — `core/config.py:56-58` `_deep_merge` 类型不匹配静默丢弃
- **file**: `core/config.py:56-58`
- **trigger**: 一个 YAML `validation: {...}`,另一个 `validation: false`。
- **impact**: 单个 YAML typo 抹除整段配置。
- **fix**: type 不一致即 warn/raise。

#### P-076 — `core/config.py:469-519` `_load_dotenv` fallback 与 python-dotenv 语义偏差
- **file**: `core/config.py:469-519`
- **trigger**: python-dotenv 缺包(ImportError)。
- **impact**: 双解析器结果不一致,silent semantic skew。
- **fix**: dotenv 改硬依赖,fallback 移除。

#### P-077 — `core/locking.py:70-110, 128-171` sidecar 与 OS lock 间窗口
- **file**: `core/locking.py:70-110, 128-171`
- **trigger**: 进程 A 在 line 88 拿锁 line 98 写 sidecar 之间被抢占。
- **impact**: B 报 "占用者: 未知";A 崩则更糟。
- **fix**: 写 sidecar `.tmp + os.replace`;OS lock 前先 PID 写主锁文件。

#### P-078 — `core/locking.py:173-176` 无 orphan/stale 检测
- **file**: `core/locking.py:173-176`
- **trigger**: A 进程 SIGKILL。
- **impact**: 锁与 sidecar 滞留;错误提示要用户手删。
- **fix**: 入锁前 `psutil` 检 PID 是否存活,stale 自动清。

#### P-079 — `core/caching.py:165-177` `stats()` 在锁外算 hit_rate 可越 1.0
- **file**: `core/caching.py:165-177`
- **trigger**: 多线程并发读统计。
- **impact**: 监控数字偶尔失真。
- **fix**: `with self._lock:` 包整段统计。

#### P-080 — `core/caching.py:164-166` `os.makedirs` 在 import 路径上副作用
- **file**: `core/caching.py:164-166`
- **trigger**: 配置传入恶意 `db_path`(如 `C:\Windows\...`)。
- **impact**: 在系统目录尝试创建文件。
- **fix**: 强制 `db_path` 在 `output_dir` 之内,拒绝 `..`。

#### P-081 — `core/run_id.py:27-29` 同秒同 PID 撞 run_id
- **file**: `core/run_id.py:27-29`
- **trigger**: 两 pipeline 在同 host 同秒启动。
- **impact**: 孤儿 log 目录;极端时覆写。
- **fix**: `secrets.token_hex(4)` 末缀。

#### P-082 — `core/run_id.py:28` hostname 含 path-illegal 字符
- **file**: `core/run_id.py:28`
- **trigger**: hostname 含 `#`。
- **impact**: Stata `.do` include 路径需额外引号。
- **fix**: `re.sub(r'[^A-Za-z0-9_-]', '_', host)` 先洗。

#### P-083 — `core/logging.py:154-178` 无 secret redaction filter
- **file**: `core/logging.py:154-178`
- **trigger**: 任何 `logger.info(f"... {api_key}")`。
- **impact**: rotating log 长期累积 key 到磁盘。
- **fix**: `_RedactFilter` 扫已知 secrets。

#### P-084 — `core/logging.py:115-193` 多进程 `RotatingFileHandler` 不安全
- **file**: `core/logging.py:115-193`
- **trigger**: 同 run_id 两 stage 写同文件触发 rotation。
- **impact**: rotation 丢日志行。
- **fix**: `concurrent-log-handler` 或 per-PID 文件名。

#### P-085 — `core/logging.py:50-59` 全局覆盖第三方 logger level
- **file**: `core/logging.py:50-59`
- **trigger**: 每次 `setup_logging` 调用。
- **impact**: 用户调试 `transformers.WARNING` 被静默抹掉。
- **fix**: `suppress_third_party=True` 参数控制。

#### P-086 — `core/reporting.py:199` `np.issubdtype` 在 pandas 扩展 dtype 上崩
- **file**: `core/reporting.py:199`
- **trigger**: pyarrow-backed parquet → nullable Int64 列。
- **impact**: 报告对"以为是数值"的列输出空统计。
- **fix**: `pd.api.types.is_numeric_dtype(dtype)`。

#### P-087 — `core/reporting.py:113-115, 240` `string[pyarrow]` 未被分类
- **file**: `core/reporting.py:113-115, 240`
- **trigger**: pandas 2.x dtype_backend='pyarrow'。
- **impact**: top-K 值统计跳过 string 列。
- **fix**: 加 `is_string_dtype(dtype)`。

#### P-088 — `core/data_versioning.py:67-74` `default=str` 跨平台 hash 飘移
- **file**: `core/data_versioning.py:67-74`
- **trigger**: 配置含 `Path` (Linux POSIX vs Windows 反斜杠)。
- **impact**: dev / CI 间 config_hash 差。
- **fix**: 预规范化 dict,Path 一律转 POSIX。

#### P-089 — `core/data_versioning.py:245-254` 缺失 input 静默通过
- **file**: `core/data_versioning.py:245-254`
- **trigger**: 上游 parquet 被人手删。
- **impact**: `verify_data_integrity` 返 True,lineage 谎报正常。
- **fix**: 缺失即报失败。

#### P-090 — `core/data_versioning.py:157-194` `pa.Table.from_pandas` 内存 3×
- **file**: `core/data_versioning.py:157-194`
- **trigger**: 阔 panel 写出。
- **impact**: 协作者 32 GB 机 OOM。
- **fix**: `pq.ParquetWriter` + metadata_collector 流式。

---

### 🟡 Medium (P2 — 计划修复)

#### P-091 — `core/caching.py:115` SCHEMA_VERSION 静态,无 prompt 自动 bump
- **file**: `core/caching.py:115`
- **trigger**: prompt_version 默认 'v0',调用方忘传。
- **impact**: 静默拿旧 prompt 答案。
- **fix**: 必填 keyword-only。(与 P-020 同根)

#### P-092 — Stage 27c orphan shim
- **file**: `news_process/27c_placebo_and_alt_anchor.py`
- **trigger**: 不在 STAGES_MAIN / OUTPUT_REGISTRY。
- **impact**: 用户 `python 27c_*.py` 跑出"幽灵"产物,主流水线永不产生。
- **fix**: 注册 + `enabled_when=audit_combined_enabled`,或删 shim。

#### P-093 — `news_process/scripts/replace_v6_to_v3.py` 全 no-op + 硬编码 F: 路径
- **file**: `news_process/scripts/replace_v6_to_v3.py:3-21, 25-26`
- **trigger**: 每行 `key == value` 的字典。
- **impact**: 死脚本误导维护者;`glob('f:/WiseSearch/...')` 仅本机生效。
- **fix**: 删。

#### P-094 — `news_process/models_output.json` 死 dump 文件
- **file**: `news_process/models_output.json`
- **trigger**: 45 KB 字典,代码无任何引用。
- **impact**: 沉默腐烂;yunwu 加新模型不更新。
- **fix**: 删,或放 docs/reference/。

#### P-095 — README L107-109 描述与实际 `scripts/` 布局不符
- **file**: `news_process/README.md:107-109` ↔ `news_process/scripts/`
- **trigger**: 文档声称 `legacy/` 子目录不存在;`update_deps.sh` 在 PowerShell 主项目里出现 bash 脚本。
- **impact**: 误导新人;读 README 找不到对应文件。
- **fix**: 同步 README 实情。

#### P-096 — CLAUDE.md OUTPUT_REGISTRY 表述只给"+5",未给绝对计数
- **file**: `news_process/CLAUDE.md:14-16`
- **trigger**: 没人在不跑代码情况下能知道实际大小。
- **impact**: 文档评估不可执行。
- **fix**: 改成"OUTPUT_REGISTRY: 20 entries"等绝对值。

#### P-097 — `[tool.ruff.lint].ignore` 屏蔽 20 条规则含 `E712 / F541` 真 bug 隐患
- **file**: `pyproject.toml:218-248`
- **trigger**: ruff CI 永不报。
- **impact**: 193 处 `f""` 无占位符可能是真 forgot-`{var}`;`E712` 在非 pandas 场景也被忽略。
- **fix**: per-file-ignores 收紧;留追踪 issue。

#### P-098 — `.pre-commit-config.yaml` 仅 2 hook
- **file**: `.pre-commit-config.yaml:19-43`
- **trigger**: `.env` / 大 parquet / YAML typo 都可一笔提交。
- **impact**: `.env` 是 P-001 的二次防线;现在缺。
- **fix**: 加 `check-yaml / check-added-large-files / detect-private-key / check-merge-conflict`。

#### P-099 — `STATA_IC_MAX_VARS=2048` 等魔法数散落 5 处
- **file**: `pipeline/panel/stata_export.py:40` + CLAUDE.md 5 处
- **trigger**: 升级 Stata 20 即需 5 处同改。
- **impact**: 文档/代码漂移几乎必然。
- **fix**: 集中到 `core/constants.py::STATA_LIMITS` dict。

#### P-100 — `news_process/.gitignore:53-60` 全局 `*.csv` 屏蔽 papers_assets 协作 CSV
- **file**: `news_process/.gitignore:53-60`
- **trigger**: `git add news_process/papers_assets/<paper>/data/x.csv`。
- **impact**: 沉默忽略,replication 包文件可能丢。
- **fix**: 加白名单 `!news_process/papers_assets/**/*.csv`。

#### P-101 — 根 `.gitignore` 缺 `.gemini/ .cursor/`
- **file**: `.gitignore`
- **trigger**: `.gemini/` 已在仓库根存在;`.cursor/` 类似。
- **impact**: agent 配置/会话/key 可能进 commit;`.gemini/skills/xlsx/LICENSE.txt` 显示 MIT 第三方树未被排除。
- **fix**: `.gitignore` 加 `.gemini/ .cursor/`。

#### P-102 — CI 测试基线 820 远低于实际 1500+
- **file**: `.github/workflows/ci.yml:139` (PYTEST_PASSED_FLOOR)
- **trigger**: 任何静默丢失数百测试的回归。
- **impact**: "baseline retreat protection" 形同虚设。
- **fix**: 调到 1500 或动态读取记录。

#### P-103 — CLAUDE.md L8 test baseline 1629 fast 与实际 ~1800+ 飘移
- **file**: `news_process/CLAUDE.md:8`
- **trigger**: `pytest --collect-only` 实际数 ≠ 文档。
- **impact**: 文档信息可信度损失。
- **fix**: 每次 batch 落地后同步 update。

#### P-104 — 验证 stage 35 / 38a / 38b TODO 未实施 dual-track
- **file**: `validation/decay_sensitivity.py:7`、`validation/radius_sensitivity.py:84`、`validation/temporal_mask.py:6`
- **trigger**: Plan E 之后,P7 dual-track 仍 TODO。
- **impact**: G3 main switch `_ctx` 后,robustness 仍 single-track,不一致。
- **fix**: 实施 P7.b,或显式列入"Known incomplete"。

#### P-105 — `papers/bank_media_disagreement/` 与 `bank_news_clarity/` 未入 `paper_registry`
- **file**: `papers/_common/paper_registry.py:35-54`
- **trigger**: v3.7.0 新立项却没注册。
- **impact**: 一旦注册,`test_paper_spec_schema.py` 因 `n_bank_min` 等 key 缺失立即 CI 红。
- **fix**: 注册 + 修齐 spec key + 调整 test。

#### P-106 — 两 paper 缺 `analysis.py/figures.py/tables.py`
- **file**: `papers/bank_media_disagreement/__init__.py`、`papers/bank_news_clarity/__init__.py`
- **trigger**: 注册后 `tests/integration/test_papers_imports.py` 参数化失败。
- **impact**: 注册 = CI 全红。
- **fix**: stub 或 `xfail` mark。

#### P-107 — `papers/_common/stata_runner.py::_cli_verify_replication` 硬编码 14 .do
- **file**: `papers/_common/stata_runner.py:533-644`
- **trigger**: derivative paper 只有 4-8 .do。
- **impact**: 验证误报 → 维护者怀疑健康的包。
- **fix**: `--paper` flag 动态读 template dir。

#### P-108 — 91 个 Stata 模板均无 `set processors`
- **file**: 全部 `papers/_common/stata_templates/**/*.do.tmpl`
- **trigger**: Stata MP/SE 不显式声明,license 决定。
- **impact**: 跨机性能/复现飘移。
- **fix**: `00_master.do.tmpl` 加 `capture set processors 64`。

#### P-109 — `version 19` 与 `46_panel_yearly_core.dta` (IC≤2048) 矛盾
- **file**: `papers/_common/stata_templates/01_data_prep.do.tmpl:6-11`
- **trigger**: 模板 `version 19` 锁 19+,但又读 IC core split,只为外部协作者准备。
- **impact**: 协作者既被 `version 19` 锁出又被 IC split 服务,自相矛盾。
- **fix**: 二选一(放宽 version 或删 IC split)。

#### P-110 — `papers/_common/figures.py::apply_publication_style` 无中文字体 fallback
- **file**: `papers/_common/figures.py:65-97`
- **trigger**: 9 paper 的 figures.py 出现中文 label。
- **impact**: PDF 在审稿人机上"豆腐块";`core/plotting.py::configure_matplotlib_chinese_fonts` 已存在但未被调用。
- **fix**: prepend `'SimHei','Microsoft YaHei','Noto Sans CJK SC'` 到 `font.sans-serif` 并打开 `axes.unicode_minus=False`。

---

## 总结统计

- **角度数**: 107(含 NA 类 3 项,实际可适用 104)。
- **真实问题数**: **110**(P-001 ~ P-110)。
- **按级别**: Critical 21 / High 69 / Medium 20 (一些跨级别)。
- **空-finding (NA) 类别**: SQL 注入 / XSS / CSRF / Open Redirect — 项目纯数据 pipeline,非 web,不适用,如实标记不计入问题数。

## 触发 / 后果分布(Top 5 类)

| 类别 | 问题数 | 示意条目 |
|---|---:|---|
| LLM / 缓存 / 归档 | 16 | P-006~P-008、P-020、P-027~P-031、P-043~P-045、P-018、P-091 |
| Pandas / 数据正确性 | 18 | P-014、P-015、P-046~P-058、P-060、P-066、P-067 |
| 安全 / 密钥 / 路径 | 8 | P-001、P-002、P-011、P-019、P-024~P-026、P-101 |
| 配置 / DAG / 文档漂移 | 18 | P-003~P-005、P-069~P-076、P-082、P-095~P-097、P-099、P-102~P-104 |
| Stata / Papers / 复现 | 12 | P-017、P-062~P-065、P-105~P-110 |

## 修复优先级排序(只挑出 P0)

| # | 文件 | 一句话原因 |
|---|---|---|
| P-001 | `.env` | 真实 key 在 tracked 路径 |
| P-002 | `_replan_v5_evidence/*.json` | yunwu key 前缀在 commit 中 |
| P-003 | `pyproject.toml:7` | 版本 3.3.0 与文档 v3.7.0 严重错位 |
| P-004 | `pyproject.toml` 依赖段 | `requests` 未声明,生产 import |
| P-005 | `requirements.txt:115-119` | D-group 必备包被注释 |
| P-006 | `executive_ner.py:188-200` | LLMCache 构造完全错位 |
| P-007 | `executive_ner.py:208-214` | archive_record 关键字错位 |
| P-008 | `executive_ner.py:190` | `hash()` 非确定性 cache key |
| P-009 | `policy_alignment.py:251-292`(+2) | 无界 `while True` retry |
| P-010 | `llm_archive/archive.py` | 全文 + 高管名 PII 泄漏 |
| P-011 | `banking_outcome_dry_run.py:352` | bank_name 路径遍历 |
| P-012 | `article_staleness.py:245-257` | lambda 闭包 highstale_ 全局均值 |
| P-013 | `article_staleness.py:217-234` | NaT 比较致窗口失效 |
| P-014 | `encode.py:836+` (×8) | merge 无 validate=,fan-out 风险 |
| P-015 | `runner.py:1184-1185` | 嵌套 merge 指数 fan-out |
| P-016 | `dag.py:195-203` | stage 19 always_enabled + $12 LLM 无 opt-in |
| P-017 | bank_media_disagreement/clarity 模板 | F:/WiseSearch 烙进模板 |
| P-018 | `tone_llms.py:416,446` | dual-track full/ctx cache 共享 |
| P-019 | `core/stage.py:186-211` | secrets 过度传播 |
| P-020 | `core/caching.py:181` | prompt_version 默认 v0 静默旧 cache |
| P-021 | `core/locking.py:81` | 'w' 模式 + msvcrt 1-byte race |

## 评审结论

- 项目处于"研究 pipeline 高速迭代 + 顶刊提交准备"状态,文档极详细但与代码同步存在多处漂移(P-003、P-012、P-016、P-093 等)。
- **结构性最严重的不是 web 安全类问题(此项目无 web 面),而是:**
  1. **LLM 调用层的反复确认性、归档完整性、cache 决定性失败**(P-006~P-010、P-018、P-020、P-027~P-031);
  2. **Pandas merge 缺 validate= 导致 panel 静默 fan-out**(P-014、P-015);
  3. **包发布/依赖声明与实际 import 错位**(P-003~P-005);
  4. **Stata 模板硬编码本机路径**(P-017),阻挡所有外部 replication;
  5. **新立 paper(media_disagreement / news_clarity)的 registry/schema/templates 三层均不完整**(P-105、P-106、P-017、P-109)。
- 强烈建议先处理 P-001 / P-002(凭据),再处理 P-006~P-008(NER 静默失败 + cost 漏洞),再处理 P-016(stage 19 自动启用 + 6h 18 美元的不可逆 spike)。
