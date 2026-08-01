# 致命缺陷整改执行计划 (FATAL_DEFECT_REMEDIATION_EXECUTION_PLAN_2026-07-16)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是**小样试跑面板**
> (2017–2018 两年, 文中或以「disk 1170 篇 / 172 行 / dev 盘」等措辞出现)。**2026-07-27/28 生产
> 全链跑通后, 本机盘面即为 T=19 全量** —— `40_panel_yearly` 23,693 行 × 4,183 列 /
> 1,247 banks × 19 years (2007–2025), 2026-08-01 以 pyreadstat 直读 `.dta` 元数据复核。
> 下文一切「盘上/当前/dev」规模陈述均为**成文当时**的事实记录, **不代表当前状态**, 且不得再被
> 援引为「样本太小/识别力不足/待全量复核」的现成理由。


**状态**: v1.4-final (R1-R4 四轮共 112 条评审全数裁定并入, 详见 §8)
**审计出处**: 2026-07-16 致命缺陷专项审计, 定谳 9 条独立 confirmed_new (1 fatal + 8 major) + 4 minor。完整证据链: 会话 scratchpad `tasks/wma8ou6f2.output`; 摘要: 记忆库 `fatal-defect-audit-2026-07-16.md`。
**授权状态**: **用户已于 2026-07-16 完全授权实施** (含 D1-D7 默认口径与 §5.1 CLAUDE.md 一句话增补)。全部修复 $0 (零付费 API、零 golden 重生、零 M0 门触碰)。

---

## §0 总则与铁律约束 (全 WP 通用)

0. **基线口径**: 工作树描述为起草时点快照; **一切以起跑前一刻 §0.5 重取的快照为准**。起草时点 (2026-07-16): HEAD = 90c40e92, 12 个脏文件 (⚠ M4 两目标文件在内, 见 §2-M4 前置闸)。
1. **golden 语义分级** (决定验证方式):
   - **字节等价类** (产物逐位不变): WP-F1、WP-F2 (对现存语料)、WP-F7 (纯行为)、WP-M1。验证 = 等价性单测 + A/B 测试差分 0 新增红灯 + (F1) §4.3-C2 盘级**数据层**判等 (禁文件级 sha256, 见 §4.3-C2)。
   - **测度值变更类**: WP-F3、WP-F4、WP-F5、WP-F6 (**dev 上 bal 列族 dormant, A/B 预期零 diff**, §2-F6)。验证 = §4.1 测试 A/B + §4.2 面板值域 A/B (白名单 diff)。
   - **模板/验证侧类** (不触面板): WP-F8/F9/M2/M3/M4。
   - ⚠ 措辞纪律: CLAUDE.md 本机套路原文是"改测度类改动本机**不动 parquet** → baseline-stash A/B"; 本计划 §4.2 要重写盘上 40/46/51 产物, 是对该套路的**受控扩展** (先备份、A/A 对照基线、白名单 diff、notes 重放; 修复后的盘面即新正确态, 不回滚) — 显式承认, 不宣称与原套路一致。
2. **$0 原则**: 全部修复与验证离线完成。⚠ **stage 40 编排含内联嵌入/llm_peer 子步 (25/27/48), 缓存 miss 时会静默付费** — 故 §4 的**每一次**重跑 (A/A、C3-C6 链式、收口全链) 一律强制前缀 `NEWS_PROCESS_LLM_OFFLINE=1` (+重跑 23 号需 `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`); "$0" 成立以 OFFLINE=1 + 0-miss 为前提, miss 即 raise 属预期守卫而非故障。任何一步发现需要联网付费 → 停下, 属计划缺陷。
3. **不触碰面**: 35 个 NN_*.py shim (⚠ 本计划只**运行**它们, 不改动) / core/dag.py / core/schemas.py::OUTPUT_REGISTRY / config YAML 键结构 / prompt v8 冻结锚 / `_llm_cache.db` / 一切 DEFERRED-M0 项。
4. **提交协议**: by-name stage; 排除起跑时点 `git status --porcelain` 实测的并发脏文件与 `*constants.json`/`eval_reports` 等并发产物, 绝不夹带; 绝不 amend / 绝不 --no-verify; HEREDOC + `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer (CLAUDE.md 规定原文)。每个 WP 独立 commit (§3)。
5. **并发纪律**: ① 起跑前一刻重取共享树基线 (HEAD + status 快照存 scratchpad); ② 与用户约定执行窗口内共享树提交冻结; ③ §4.1 B 侧漂移哨兵兜底。
6. **测试运行**: 从 repo 根 (`F:\WiseSearch\data_antigravity_project`) 用 `F:\Anaconda3\python.exe -m pytest`。日志检索用 Bash grep (logs/ 被 gitignore)。
7. **fail-loud 红线**: §4.2 面板 diff 中任何**白名单外**列的值/列集漂移 = 停止、回滚该 WP、按新缺陷立案 — 不允许"顺手收进白名单"。白名单与预期锚**事前写死** (本计划 §4.2), 事后不改; **方向性描述不作停线判据** (只锚变化格集合与列白名单, 见 §2-F3 教训)。§4.2 步骤 1 的 A/A 对照跑负责剥离环境性/预登记漂移。

---

## §1 工作包总表

| WP | 缺陷 | 严重度 | 文件 | golden 分级 | 提交序 |
|----|----|----|----|----|----|
| F1 | 嵌入引擎整语料物化 ~13.5× 内存放大 (含离线 0-miss 复现路径) | **fatal** | pipeline/text/embedding_engine.py | 字节等价 | C2 |
| F2 | tiktoken 裸 encode() 特殊 token 毒丸 | major | embedding_engine.py + core/text/token_utils.py + strategic_diff.py + policy_alignment.py | 字节等价* | C1 |
| F3 | avg_llm_conf 宏平均计入无效模型格 | major | pipeline/panel/encode.py (+F3b: validation/llms_evaluation.py) | 测度值变更 | C3 |
| F4 | ATT-2 后 docid 去重行序依赖 | major | pipeline/panel/attention_media.py | 测度值变更 | C5 |
| F5 | log_sent_ctx/_ss 门控错配 → 伪中性 0.0 | major | pipeline/panel/runner.py | 测度值变更 | C4 |
| F6 | ROBUSTNESS_WINDOWS 右端点 2024 → 生产 bal_* 剔 2025 | major | attention_media.py + export.py + tests | 测度值变更 (dev dormant) | C6 |
| F7 | --skip-21-if-exists 指纹缺三轨文本/回退列 | major | run_pipeline_function.py + 2 个测试文件夹具 | 字节等价(行为) | C7 |
| F8 | 01_data_prep 幻影列 → r(111) master 链死 | major | 01_data_prep.do.tmpl | 模板 | C8 |
| F9 | 创新维度人工验证 docid join 错位配对 | major | validation/llms_evaluation.py | 验证侧 | C9 |
| M1 | 嵌入归档顺序倒置 | minor | embedding_engine.py | 字节等价(产物) | C10a |
| M2 | 20_tableA1 陈旧列名 indep_frac_cs | minor | 20_tableA1_inter_track_kappa.do.tmpl | 模板 | C8 |
| M3 | 10_table1 幻影列名 ×5 (R1 扩) | minor | 10_table1_descriptives.do.tmpl | 模板 | C8 |
| M4 | company 02 codebook 推荐动作年界前提失效 (+tax 镜像) | minor | company_{listed,tax}_bank/02_*.py | 旁路管道 | C10b |

*F2 对现存语料字节等价; 对含毒丸的未来语料是"崩溃→正常处理", 属修复本意。

---

## §2 工作包详规

### WP-F1 嵌入引擎缓存拼装流式化 (fatal)

**根因**: `embedding_engine.py::get_embeddings_api` L278-282 全量物化 N 条缓存 JSON 字符串 (~90KB/条实测), L509-517 再全量 `json.loads` 成 Python 列表 — 双份同活 ~217KB/条 vs 最终 float32 16KB/条 ≈ 13.5× 放大; 分批仅在网络 miss 侧 (L341-361)。stage 16/25 整语料单次调用 → 生产 ≥~55 万篇越过 128GB; **离线 0-miss 复现路径同样中招** (L322-329 守卫只拦 miss 分支)。

**修法** (纯内部重构, 无 config 开关; 实施首步通读全函数 L253-517, 外部签名与返回契约零变化):
1. **命中侧流式**: 单遍遍历 `texts`: 逐条 `cache.get(...)` (与原列表推导同为逐条 get, sqlite 访问模式不变); 首个命中 `json.loads` 取 `dim`, 预分配 `out = np.empty((N, dim), dtype=np.float32)`; 此后每个命中断言 `len(row) == dim` (**含首个之后的每行**, 防 len-1 标量广播静默填行) 后 `out[i] = row` 即释放; miss 只记 `missing_indices`。命中分桶诊断 (L296-314) 同遍累加计数器, 日志格式不变。
2. **miss 网络侧**: 保持动态分批/并发/重试结构; **`_embs_by_idx` 退役** — 批是 `missing_texts` 的连续切片 (L341-361 分批代码的连续性假设实施时亲核), 批构建期预存**该批对应的 `missing_indices` 子数组**, `_process_batch` 成功后**立即** `out[np.asarray(该子数组)] = batch_embs` 并释放 (**fancy indexing — hit/miss 交错时全局行号非连续, 禁写 `out[offset:offset+m]` 连续切片**, 仅全 miss 时才退化为连续行段; T2 正是该错位的红绿锚。asyncio 单线程写行原子, 完成乱序无碍); 全 miss 时 `dim` 由**首个完成的批**确定, 分配带 None 守卫。
3. **不变量保持清单** (逐条入测试):
   - 离线守卫位置不变 (miss 且 OFFLINE → 网络调用前 raise);
   - 空输入早退 / 单条超限 raise / base_url·api_key 校验下移语义 / put_batch·归档行为 (M1 另批) / dtype=float32 / 行序严格一致;
   - **任一批 `EmbeddingRetryExhaustedError` → 整函数 return None** (L486-499 契约), 部分填充的 out 绝不外泄; 已成功批的 put_batch/归档副作用照旧保留;
   - **逐批数量断言 (R2; 机制经 R3 修正)**: 每批成功响应后校验 `len(batch_embs) == len(batch)` — 旧 L506-508 全局断言的逐批等价迁移, 防 API 短响应被 numpy (1,dim)→(m,dim) 静默广播成整段复制行。⚠ **禁用裸 `assert`**: 该校验落在 `_process_batch` try 块内, AssertionError 会被 L469-476 `except Exception` 泛捕获转入 80×10s 重试后 return None (fail-loud 退化为慢速降级); 必须 `raise ValueError(f'批 {batch_idx} 返回数量异常: expected/got …')` — 镜像 L396-399 缺 'data' 键的既有 fail-loud 先例, 经 L467-468 `except ValueError: raise` 穿透重试环。不符 → 禁写 out / 禁 put_batch。(hit 侧逐行 len(row)==dim 校验在重试环之外, 保持 assert 即可);
   - **写行完备计数 (R2)**: 维护 `_rows_written` (命中逐行 +1, 每批 +len(batch) — 计数量非位置), 返回前 `assert _rows_written == N` — 旧全局断言的第二道流式等价物, 防漏写/双写/错位;
   - **数值逐位等价**: 逐行 `np.asarray(lst, dtype=float32)` 与旧 `np.array(list_of_lists, dtype=float32)` 同 JSON 输入逐位相同, 测试断言 `tobytes()` 相等。
4. **内存预算日志**: 分配前 `logger.info` 预估 `N×dim×4` 字节。

**测试 gate** (新 `tests/test_embedding_engine_streaming.py`; mock 一律夹具, 不触真实 data/processed 写路径):
- T1 等价性: 主体用**合成 JSON** (json.dumps(随机 float 列表), double→float32 舍入语义与真条目同构); "盘上真条目"子用例加 `pytest.mark.skipif(not <db>.exists())` 护栏 (data/ 不随 checkout 分发, 防裸树永久红);
- T2 hit/miss 交错次序还原 (顺带断言 `_rows_written` 语义); T3 全 miss 等价; T4 OFFLINE+miss → RuntimeError 且 0 网络调用; T5 维度不齐 fail-loud (含"首个命中后某行 len=1"标量广播场景); T6 空输入;
- T7 峰值内存: **夹具钉死 N≥50 × dim=4096**; 唯一断言 = 新实现 peak < 3×final (R3 算术勘误: N=50 时 final = 50×4096×4B ≈ **0.8MB**, 逐行瞬态 ~220KB → peak ≈ 1.27×final, 距 3× 阈值裕度真实; N 越大裕度越宽); "旧实现 >10×"仅注释 (前提: mock 串在 tracemalloc 窗口内惰性生成; 预物化实测仅 ~9×);
- **T8 重试穷尽**: mock 一批成功一批恒 5xx; `monkeypatch RETRY_DELAY→0` (否则真睡 10-20s); 用 asyncio.Event 令失败批在成功批 put_batch 落地后才穷尽 (副作用锚确定性, 非调度巧合) → 断言返回恰为 None + 成功批 put_batch 已调;
- **T9 乱序完成**: 全 miss 多批, 按 batch_idx 逆序注入 await 延迟 → 输出与串行参考臂逐位相等 (锁批→行映射; 旧 extend 乱序错位有前科);
- **T10 短响应 (R2; R3 补 mock)**: mock 某批 (m>1) 返回恰 1 条合法嵌入, `monkeypatch RETRY_DELAY→0` (镜像 T8 — 否则误实现为可重试路径时 T10 呈现 ~13 分钟挂起红而非秒级干净红) → 断言 raise ValueError 而非静默返回矩阵/返回 None;
- 既有嵌入相关测试全绿。

**A/B 预期**: 产物零变化。盘级验证 = 数据层判等 (**禁文件级 sha256**), 权威流程与依据见 §4.3-C2 (含 A/A 参照臂)。

**残余风险 (登记)**: 修后单调用峰值 ≈ N×dim×4B 属必需; stage 25 六矩阵驻留 N=1.5M 时仍 ≈129GB — §6.2 sizing 探针。**验收口径 = 消除 13.5× 放大, 非"嵌入 T=19 OOM 已解决"**。
**回滚**: 单文件单函数 revert。

---

### WP-F2 tiktoken 特殊 token 毒丸 (major)

**根因**: cl100k `encode()`/`encode_batch()` 默认 `disallowed_special='all'`, 语料含 `<|endoftext|>` 等字面量即 ValueError, 在分批/重试/降级之前无捕获 → 嵌入消费阶段单篇毒丸整段崩。

**修法**: 全部裸调用点加 `disallowed_special=()`:
- `embedding_engine.py`: L246 / L346 / L617;
- `core/text/token_utils.py`: L43 (count_tokens) / L51 (truncate_to_max_tokens 截断) / L64 (split_into_chunks 分段);
- `strategic_diff.py`: L267;
- `policy_alignment.py`: `encode_batch` 调用点 (~L198-210) — **顺带把 `_count_tokens_batch` docstring 的"同 disallowed_special 默认"改为"同 disallowed_special=() (F2 2026-07-16)"** (R2, 保持逐位等价声明与实现同步);
- 收尾 grep `\.encode(\|encode_batch(` 全仓非测试扫尾 (人工排除非 tiktoken 同名)。

**为什么不是 try/except 降级**: 毒丸是合法语料, 正确语义是照常嵌入; 跳过会破坏行宇宙与 parity。
**缓存/golden**: 缓存键=文本键, 零漂移; 现存文本 encode 逐 token 相同 → 字节等价。
**测试 gate** (新 `tests/test_tiktoken_special_tokens.py`): T1 毒丸串过全部改点不抛; T2 100 条无特殊 token 中文样本修前后逐 token 相等; T3 超长毒丸切块正常。
**A/B 预期**: 零变化。**回滚**: 参数级 revert。

---

### WP-F3 avg_llm_conf 无效模型格稀释 (major)

**根因**: stage 21 缺席模型写 `sentiment_confidence=0.0` 非 NaN (tone_llms.py:1627-1633/1655-1658; 落列 :2565/2607/2647); `encode.py:377` 宏平均计入 0.0, :380 仅文章级掩码; :399-404 逐模型列却有 per-model 掩码 — 双重标准。
**盘面事实 (R1/R2 双验)**: dev 21 号 parquet 宇宙**无缺席行** (缺席格存在于缓存/归档层与生产在线路径); 盘上 conf==0.0 全为在场 verified=False 兜底格。掩码判据 `score.notna()` (encode.py:308-315: verified=False → score=NA) 同时剔: ① 缺席格 (conf=0.0); ② 在场判伪/缺标格 (conf 为真实值)。**本修复是构念级口径统一**: avg_llm_conf 从"在场三模型宏平均"改为"**投出有效票的模型宏平均**" (与 `_conf_valid_{short}`、omni-g-tonellms-12、`_avg_innovation_confidence` 同口径) — 决策点 **D5** (默认采, 用户可否决)。

**修法** (消费侧掩码, 镜像 omni-g-encode-02; 不动 stage 21 哨兵, §6.1)。**替换范围显式化 (R2)**: 只替换宏平均取数表达式; 原 :383-384 (缺 vote_col 退化警告) 与 :396-397 (无 conf 列跳过警告) 两个 else 分支、:381-382 合成 info、:388-395 分布诊断块**原样保留** (仅 `len(conf_cols)` 换 `len(_masked)`):
```python
_masked = {}
for s in LLM_MODELS:
    m_conf, m_score = f'{s}_sentiment_confidence{track}', f'{s}_score{track}'
    if m_conf in df.columns:
        _masked[s] = (df[m_conf].where(df[m_score].notna())
                      if m_score in df.columns else df[m_conf])   # 缺 score 列回退 raw + WARNING
if _masked:
    _conf_macro = pd.DataFrame(_masked).mean(axis=1)   # 无效模型格不入分子亦不入分母
    if vote_col in df.columns:
        _conf_macro = _conf_macro.where(df[vote_col].notna())
        ...原 info 日志...
    else:
        ...原 :383-384 退化警告...
    df[f'avg_llm_conf{track}'] = _conf_macro
    ...原 :388-395 分布诊断...
else:
    ...原 :396-397 跳过警告...
```
`avg_llm_conf_std` 聚合 (:882-883) 与 geography z (geography.py:437) 零代码变化。日志追加"无效模型格掩码剔除 {n} 篇×模型格"计数。

**F3b (第二消费者; R2 构念修正 — 与 D5 刻意不同构, 禁互相套用)**: `llms_evaluation.py` ~L1389-1392 对三模型 `verification_confidence` 宏平均喂 wrong_high_conf 等 FP/FN 诊断。该诊断的正确域 = "**模型参与了验证**" (`{short}_verified{track}.notna()`) — 在场 verified=False 是**有效验证票**, 其 verification_confidence 是真实值且正是诊断对象, **必须保留**; 只剔缺席哨兵格 (verified=None → 唯一的结构性 0.0 来源)。该 df 宇宙实测无 score 列, D5 的 score.notna() 判据在此**不可用也不该用**。掩码 = `.where(df[f'{short}_verified{track}'].notna())` + 对账日志。测试: 在场 verified=False 真值 conf 保留、缺席 0.0 剔除。

**测试 gate** (定死: 扩 `tests/test_omni_fix_encode.py`):
- T1 缺席: 0.9/0.85 verified + 缺席 (conf=0.0, score=NA) → 0.875 (旧 0.5833);
- T2 回归锚: **三模型全部投出有效票**时与旧实现逐位一致;
- T5 在场判伪: verified conf=0.9 + 在场 verified=False conf=0.7 (score=NA) + verified conf=0.8 → (0.9+0.8)/2;
- T3 全无效 → NaN; T4 缺 score 列回退 + WARNING; F3b 两例; 既有对称夹具全绿。

**A/B 预期 (dev 盘, R1 实测 + R2 复核锚)**:
- 变化行 = valid-vote 域内任一模型 score 无效的文章所在格; dev 实测 full 136 篇/63 格, ctx 81/50, ss 67/39 (起跑时点重测为准, 事前写入执行记录);
- **方向: 逐格双向 (下移格占多数、均值净上移 +0.059 均属预期), 不作停线判据** — 验收只锚变化格集合与列白名单;
- 列白名单: `avg_llm_conf{trk}`/`avg_llm_conf_std{trk}` 仅受影响格变化; geography z 衍生在受影响格所在**年份全截面**变化 (属预期); `40_article_bank_level.parquet` 文章级 conf 三列同步。

**文档同步**: F052 formula 行补"该模型自身 score 无效 (缺席/判伪/缺标) 即剔出分子分母" (§5.2); §5.4 披露沿用"逐格双向"措辞。
**回滚**: 单块 revert (+F3b 单块)。

---

### WP-F4 ATT-2 行序依赖的 fintech 身份 (major)

**根因**: `attention_media.py` L781-790 对级重标后 L795 按 docid keep='first' 去重 — 行序决定身份; L1022-1027 LOO own_ft 对级统计与首行口径错配, L1041 clip 静默吞。

**修法**:
1. 文章级身份 = 任一对级 verified:
```python
df_unique = df_all.drop_duplicates(subset=['docid']).copy()
df_unique['is_fintech_news'] = df_unique['docid'].map(
    df_all.groupby('docid')['is_fintech_news'].any())
```
   注释写明双前提 (R2): 值域 — L790 后为 numpy bool, any 无 NaN 歧义; **键域** — docid 由 preprocessing 生成非空 (:578-590 已守卫), groupby dropna 不触发 (可加零成本 `assert df_all['docid'].notna().all()`)。
2. **数学性质注释 (范围限定)**: "在 docid→geo 归属恒定不变量下, any() 消除 ATT-2 判伪导致的 own_ft > cell_ft 成因" — 不得写"恒不成立" (跨 geo 幽灵 docid 是独立合法成因, test_omni_fix_attention.py:346-376 依赖 clip)。clip 保留; 哨兵 = `logger.warning` 双成因分诊。
3. fail-open 路径: is_fintech_news 保持文章级常量 → any() ≡ first → 零行为变化。
4. **LOO 比值上界预分析**: 实施前只读脚本预算修后 `ft_attn_*` 值域 + 通读值域守卫 (`_validate_attention_index` 或同名): 可能越界 → 决策点 **D6** (默认: WARNING 披露 + 保留自然值 + 放宽守卫预期); §4.4 预登记为已知次生现象。

**测试 gate** (扩 `tests/test_omni_fix_attention.py`): T1 双银行分裂两种行序逐位相同且计入 _ft; T2 own_ft ≤ cell_ft (仅 ATT-2 分裂场景, 不与 :346 跨 geo 场景冲突); T3 全伪不计入; T4 fail-open 不变。
**A/B 预期 (dev, R1+R2 双验锚)**: **7 个 docid first≠any 分歧 (全为 False→True)** → 面板六列 (`ft_attn_yr/ft_vol_yr/ft_attn_prov/ft_vol_prov/ft_attn_city/ft_vol_city`) + 侧产物 `40_attn_index_{year,province_year,city_year}.{parquet,csv}` 的 `fintech_articles`/`ft_attn_*`/`ft_vol_*` 值漂移 (_ft 只增不减; ft_vol 仅年表侧产物在列, R4)。
**回滚**: 单函数块 revert。

---

### WP-F5 log_sent ctx/ss 轨门控错配 (major)

**根因**: `runner.py:348-353` 三轨统一 full 轨 `n_articles>0` 门控; ctx/ss "有覆盖但全轨无效"时输出伪中性 0.0。盘上 ctx 15 行 / ss 11 行 (R1 复算 + R2 二次复算精确匹配, 且全部 n_articles>0)。

**修法**: full 轨保留 `n_articles` 物理门控 (逐位保持; full-only 门控下与 valid 经验恒等 — dev 0 行不等; SSOT 措辞: n_articles='size' 物理篇数, llm_valid='count' 有效票篇数, 恒等属门控副产非定义); ctx/ss 用 `n_articles_llm_valid{track}` (encode.py:918/921 实名), 缺列回退 n_articles + WARNING (镜像 encode_collab.py:452)。docstring 追加: "ctx/ss 对齐 jf 的 per-track valid 分母 (runner.py:2353); full 轨为字节稳定保留物理分母 (jf 对 full 用 valid 分母, 经验恒等); 理论残余 §7-R6, 生产重生窗口统一。"

**测试 gate** (定死: 扩 `tests/test_omni_fix_runner.py::TestGatedLogSent`, 既有 5 个 full 轨用例修后全绿): T1 ctx n_articles=5/valid_ctx=0/pos=neg=0 → NaN; T2 ctx valid_ctx=3 数值不变; T3 full 轨逐位一致; T4 缺列回退 + WARNING。
**A/B 预期 (dev)**: **恰 ctx 15 行 + ss 11 行 {0.0→NaN}**, 两列外零变化 (51 号同列同步)。强锚不符 → 停线。
**文档同步 (R2 扩)**: `F411_l2_log.md` **全文 grep n_articles 逐处核改** (起草时点实测 **7 处**: 行 8 formula / 行 12 frontmatter 依赖 / 行 50 家族方法学段 / 行 58/64/70/76 逐轨正文), ctx/ss 改述为 n_articles_llm_valid_{trk}, full 轨措辞同 docstring; 收尾 grep 断言不再含"同一 n_articles"类三轨共享门控措辞 (§5.2)。
**回滚**: 单函数 revert。

---

### WP-F6 ROBUSTNESS_WINDOWS 右端点 + 列族更名 (major)

**根因**: `attention_media.py:203-207` 三窗右端点 2024; 90c40e92 改了模板侧与 4 处注释漏此常量 → **生产** bal_* 静默剔 2025。
**dev 事实 (R1 定谳 + R2 复核)**: 平衡子集恒空 → :239-244 continue, **列族不落地** (40 号 3442 列 / 51 号 3453 列均 0 个 bal_*) → dev 面板 A/B 预期 = 逐位零变化, 验证力全在单测 + grep。

**修法** (D1 默认更名):
1. `ROBUSTNESS_WINDOWS = [(2007, 2025, 'w0725'), (2010, 2025, 'w1025'), (2011, 2025, 'w1125')]`;
2. 消费者横扫 (grep 实测仅 3 个 py 文件): attention_media.py 本体; export.py:1074-1082 九标签键+文本 (**_ss 标签由 export.py:1451 _ctx→_ss 机械派生环自动跟随, 已实证无缺口**); tests/test_omni_fix_attention.py — 夹具承重更新: FULL 媒体扩 2007-2025、**GAP 端点同步 (2007, 2025) 保持中间全缺** (维持新旧判据判别力)、panel 夹具年谱 range(2007, 2026)、逐用例通读窗口断言;
3. **扫尾 grep scope 写死 (R2)**: `grep -rn "w0724\|w1024\|w1124\|bal_w" --include="*.py" --include="*.do.tmpl"` — **显式排除 build/ (build/codebook_inputs/*/source_excerpt.md 是侧线 longdesc 管道的源码摘录快照, 陈旧命中属预期排除项, 非 §5.3 重生范围)、scripts/audit/ 计划文档、记忆库**; 命中仅限上述 3 文件即通过;
4. 新 gate T5: `all(end == 2025 ...)` + 后缀名实一致 (`f'w{start%100:02d}{end%100:02d}'`)。

**测试 gate**: 更新后 test_omni_fix_attention 全绿 + T5。
**A/B 预期 (dev)**: 面板/侧产物**逐位零变化**; §4.2-C6 白名单 = 空集。
**生产披露 (§5.4)**: 生产重生才现 w0725 列族 (列集置换), 覆盖 2007-2025, 与模板侧合一。
**回滚**: 常量+标签+测试三处同回。

---

### WP-F7 --skip-21-if-exists 指纹补列 (major)

**根因**: 九列指纹 (run_pipeline_function.py:319-329) 不含 ctx/ss 轨 prompt 真实文本输入; 改窗口参数后 skip 误放行, 旧标签+旧轨文本静默下传。

**修法**:
1. 指纹扩为 **13 列** (R2: flag 列两侧在位性已实测为真 — 与 content 列同级证据, 一并纳入, 语义闭合, 原 R7 残余关闭):
```python
_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS = (
    'docid', 'pubcode', 'target_bank', 'co_mentioned_banks',
    '日期', '标题', '内容',
    'content_ctx', 'content_ss',           # F7: ctx/ss 轨 prompt 真实文本输入
    'ctx_is_fallback', 'ss_is_fallback',   # F7: 回退语义位 (两侧 parquet 实测在列; bool→astype string 可排序)
    'fintech_intensity_score', 'intensity_verified',
)
```
2. 两侧在位性: dev 盘 15 号与 21_full 号 parquet **四列全部实测在列** (R1 content 两列 + R2 flag 两列)。legacy 缺列 → `pd.read_parquet(columns=...)` 抛错 → :507 except → reject skip (离线 $0 重放回填, 属预期非故障 — reason 写明)。
3. `_STAGE21_FILTERED_FINGERPRINT_COLUMNS` 不动。
4. 性能披露: 指纹已含 `内容` 全文, 新增 ≈ ×2-3, 远低于重跑 21; 入注释。
5. **既有测试夹具承重更新**: `_stage14_df` values 扩为 **13 项** (与常量顺序严格对位) + `assert len(values) == len(_STAGE21_UPSTREAM_FINGERPRINT_COLUMNS)` 防 zip 静默截断; 波及: `tests/test_run_pipeline_function.py` (accepts/rejects_stale) + `tests/test_v9_pre1_skip_version_guard.py` (branch_a/branch_c, import 同夹具) — 列入 C7。
6. **:507 except 消息追加提示 (R3 升格为编号项)**: `failed to compare ...` 消息尾部追加 `(若为 legacy 缺列: 离线 $0 重放回填属预期)` — 该 except 兜所有比对异常 (含文件损坏), 故用条件式措辞。

**CLAUDE.md 同步 (§5.1, 用户逐字批准, 随 C7 入库)**: 在"2 处门控副本必须同步翻"句后加: `; skip 指纹含三轨文本+回退列 (F7 2026-07-16), 改动轨道物化参数后指纹自动 reject, 无需手动强制重跑`。

**测试 gate**: T1 仅 content_ss 单字符差异 → reject; T2 全同 → allow; T3 legacy 缺列 → **只断言 reject + 不抛未捕获异常** (R3: 消息文案不作强断言 — 修法第 6 条的提示文案属可读性增强, 断言锚在行为不在文案); 既有 4 用例修后全绿。
**A/B 预期**: 产物零变化; dev 两侧带列 → 修后判定与修前一致 (allow)。
**回滚**: 常量 + 夹具 revert。

---

### WP-F8 01_data_prep 幻影列 (major)

**根因**: :37-38 直拼无重映射; :59 `foreach of varlist` 启动期校验 → lf/sf r(111), :60 守卫死代码; master 裸 do 链死。范式已修 11_table2/21_tableA2/20_tableA1/31, 漏 01 与 10 (M3)。

**修法**: ① :37-38 → if/else 重映射 (lf→`tech_frac`, sf→`symb_frac`; 镜像 11_table2:76-89, **else 分支内容保持缩进** — 源级负断言的前提); ② :59 → `foreach var in ...` (守卫变活; :71 既有范式); ③ 占位符集合零变化。

**测试 gate (结构断言, 禁子串否定; regex 统一容忍多空格对齐风格 — R2)**:
- 源码级: 模板不再含无条件直拼行 `re.search(r'^local main_locus\s+tech_frac_\{\{MAIN_LOCUS_TRACK\}\}', tmpl, re.M)` (前提 = else 分支缩进, 实施须保持否则负断言失效);
- 实例级 (lf/sf): 产物含 `re.search(r'^\s*local main_locus\s+tech_frac\s*$', out, re.M)` + `if "lf" == "lf"`; lc/sc: 含 `tech_frac_lc`;
- :59 行级: 含 `foreach var in`, 不含 `foreach var of varlist`。

**验证 (可选)**: Stata 冒烟 (`/b`, ad-hoc 末尾 `exit, clear`, r(###) 扫描加非字母边界)。
**A/B 预期**: 面板零变化。**回滚**: 单模板 revert。

---

### WP-F9 创新维度人工验证 join 键 (major)

**根因**: llms_evaluation.py:1119-1125 非唯一 docid 单键双侧 keep='first' → 错位配对/静默丢弃。

**修法**:
1. 复合键优先; 降级分支**双侧对称剔歧义** (先算掩码再过滤, 日志在过滤前用各自掩码计数 — 顺序勿颠倒):
```python
if 'target_bank' in df_mv.columns and 'target_bank' in df_pred.columns:
    join_keys = ['docid', 'target_bank']
else:
    join_keys = ['docid']
    _amb_pred = df_pred['docid'].duplicated(keep=False)
    _amb_mv = df_mv['docid'].duplicated(keep=False)
    logger_inst.warning(f"  innovation join 降级 docid 单键: pred 剔歧义 {int(_amb_pred.sum())} 行, mv 剔 {int(_amb_mv.sum())} 行 (gold 宁缺勿错配)")
    df_pred, df_mv = df_pred[~_amb_pred], df_mv[~_amb_mv]
df_mv = df_mv.drop_duplicates(subset=join_keys, keep='first')
df_pred = df_pred.drop_duplicates(subset=join_keys, keep='first')
df_joined = df_mv.merge(df_pred, on=join_keys, how='inner', suffixes=('_mv', ''))
```
2. 对账日志: join 前后行数/去重丢弃/未匹配 gold; 未匹配率 >5% → WARNING。
3. mv 侧 schema (D3): 实施首步核证生成器 target_bank 列; 缺则生成器补列, 既发放窗口文件不动, 降级兜底。
4. 既有 "R2C-04 / test 14" 测试: 语义升级为"复合键 + 降级双侧剔歧义", mv 侧一并覆盖。

**测试 gate** (扩既有 R2C-04 所在测试文件, 实施时 grep 定位): T1 同 docid 两银行复合键各配各零丢弃; T2 降级模式 — 含 "mv 侧 d0 两行 + pred 侧 d0 唯一" 夹具, 断言 d0 整体剔除; T3 权重对账; T4 单银行回归锚逐位一致。
**A/B 预期**: 面板零变化; dev 63 号 R 列全空时依旧 pending。
**回滚**: 单函数 revert。

---

### WP-M1 嵌入归档顺序 (minor)

镜像 tone_llms.py:757-791 `_archive_ok` 范式 (以其现实现为 SSOT 逐行比对后镜像): 归档前移, put_batch 以 `_archive_ok` 为条件; 归档失败 → 不缓存 + WARNING。测试: mock archive 抛错 → put_batch 未调; 正常 → 均调; enable_archive=False → 只 put_batch。A/B: 产物零变化。

### WP-M2 20_tableA1 陈旧列名 (minor)

`indep_frac_cs` 共 3 处 = :123 注释 (同步改写为 "ss 轨 collab frac 已物化为 indep_frac_cm_ss (encode.py:2083)") + :140 confirm + :142 correlate。gate: 模板全文 grep 0 命中 (含注释)。

### WP-M3 10_table1 幻影列名 ×5 (minor)

① :11 `llm_prob_score_` → `avg_llm_prob_score_` (encode.py:1190 实名); ② :13-17 四个幻影 (`tech_frac/app_frac_{{MAIN_LOCUS_TRACK}}`、`sub_frac/symb_frac_{{MAIN_SUBST_TRACK}}`) 套用 correctness-04 if/else 重映射 (46 dta 实测幻影全缺、裸名全在)。
gate (防自红): `(?<!avg_)llm_prob_score_` 0 命中; lf/sf 实例产物结构断言裸名 (regex 容忍多空格, 同 F8 范式); 其余 degrade 型模板缺口 → §7-R8。

### WP-M4 company 02 推荐动作 (minor)

**改动面 (R2 引文补全)**: listed :1178 全行 = `keep if year<=2024 & year>=ipo_year   // 2025 无语料假零 + 上市样本裁剪 (推荐默认动作)`; tax 镜像 :972 = `keep if year<=2024 & year>=reg_year` (税调企业无 IPO, **下界变量 = reg_year, 勿照抄 ipo_year**)。
**修法 = 保结构替换**: 只动年份上界 — 尾部零篇年存在 → `year<=<最后非零年>` (由 :1077 `yearly` 动态取); 无尾零 → 删上界子句; **各管道既有下界子句原样保留** (listed=`& year>=ipo_year` / tax=`& year>=reg_year`); 注释按分支改写。
**前置闸 (起草时点两管道 10 文件全脏)**: C10b 动 M4 前核目标文件干净; 脏则 (a) 等并发收口 / (b) 用户确认对方 hunk 一并入库并在 commit message 披露。
**tracked 生成物处置 (R2, §7-R10)**: 两份库内 codebook md 的陈旧 `keep if year<=2024` 行**保持陈旧至下轮 02 真跑** (正规刷新途径 = 重跑旁路管道 02, 重 IO 长跑不在本计划范围) — 登记为预期不立案; 若用户要求即刻一致, 备选 = 手工同步该行 + commit message 披露。
**测试 gate (R3 修正 — 既有测试对推荐动作行 0 覆盖, "更新既有断言"不可执行)**: 两管道既有 gate 全绿 + **新增断言**: 对 02 的推荐动作生成逻辑断言 ① 尾部零篇年存在时上界 = 最后非零年; ② 无尾零时无上界子句; ③ 下界子句 (listed=ipo_year / tax=reg_year) 原样保留。若实施发现新增断言成本不成比例, 降格为 §7 登记 "M4 无自动 gate, 验收 = 下轮 02 真跑目检" (二选一, 禁留空)。

---

## §3 执行顺序 / 依赖 / 提交切分

**总时序**: §4.2.0 备份 → §4.2.1 A/A 对照跑 → **§4.3-C2① stage-16 未改码 A/A 臂 (必在 C1 之前, R4)** → §4.1 pytest_A → C1..C9 (每个测度 C 后链式重跑+diff) → C10a/C10b → pytest_B → C11 收口 (D7 全链跑 + codebook 重生 + 文档)。

| 提交 | 内容 | 测试落点 (定死) | 依赖 |
|---|---|---|---|
| C1 | WP-F2 全点 | 新 tests/test_tiktoken_special_tokens.py | 无 |
| C2 | WP-F1 流式化 | 新 tests/test_embedding_engine_streaming.py | C1 (共文件) |
| C3 | WP-F3 + F3b | 扩 tests/test_omni_fix_encode.py | 无 |
| C4 | WP-F5 | 扩 tests/test_omni_fix_runner.py::TestGatedLogSent | 无 |
| C5 | WP-F4 | 扩 tests/test_omni_fix_attention.py | 无 |
| C6 | WP-F6 + export 标签 + 夹具 | 扩 tests/test_omni_fix_attention.py | 无 |
| C7 | WP-F7 + 夹具×2 + CLAUDE.md 一句 (用户批准后) | 扩 tests/test_run_pipeline_function.py + test_v9_pre1_skip_version_guard.py | 无 |
| C8 | WP-F8 + M2 + M3 | 新 tests/test_stata_template_phantom_columns.py | 无 |
| C9 | WP-F9 | 扩既有 R2C-04 所在测试文件 | 无 |
| C10a | WP-M1 | 扩 tests/test_embedding_engine_streaming.py | C2 (共文件) |
| C10b | WP-M4 (过前置闸; 阻塞不挟持 C10a) | 两管道既有 gate | 独立 |
| C11 | §5 收口 (D7 全链跑 → codebook 重生 → longdesc → 计划回填 → 记忆库) | — | C1-C10a (+C10b 若已落地) |

C3-C6 无代码依赖, 但 §4.2 面板 A/B **逐提交链式做** (每个 C 与上一 C 产物比对, 每次只放行一个白名单族)。

---

## §4 全局验收协议

**执行时序**: 备份 (§4.2.0) → A/A 对照跑 (§4.2.1) → stage-16 未改码 A/A 臂 (§4.3-C2①, 必在 C1 之前) → pytest_A (§4.1.1) → 各 C → pytest_B → C11。**备份未完成前禁止任何重跑。**

### 4.1 测试差分 (A/B, 禁 stash) + 漂移哨兵
1. **A 基线 (在 A/A 对照跑之后取, 使 G9 列集与重跑态进入基线)**: `pytest -q` 全量 → `pytest_A.txt`; 同时记录 HEAD + `git status --porcelain` + 关键目录 mtime 快照。
2. **B 对照**: 全部 WP 落地后同命令 → `pytest_B.txt`。B 前复核漂移哨兵: 窗口内有并发提交/编辑 → 新增红灯先在"仅含并发改动"参照点 (git worktree 只读检出) 归因; 归因不清按未通过处理。
3. **判据**: B 失败集 ⊆ A 失败集 ∪ {夹具更新重命名用例} ∪ {**预登记豁免通道**: 直读 data/processed 面板并断言值/列集的既有测试, 因 C3-C5 故意值修正而翻红 — 逐条列名归因为预期修正, 禁 blanket 豁免}; 0 未归因新增红灯; 新 gate 全绿。

### 4.2 面板值域 A/B (链式)
0. **备份 (第一步, R2 顺序修正; 产物清单 R3 补全, 单点维护)**: 定义**「重跑产物清单」**(后续快照复用同一清单): stage 40 的 OUTPUT_REGISTRY 5 parquet + 40_panel_yearly.dta (registry 不含但 export_panel 每跑必重写) + **3 个 40_attn_index_*.csv** (C5 白名单成员, 每跑重写) + 46 全部产物 (dta + labels.do + codebook.xlsx 等每跑重写件) + 51_panel_with_controls.{parquet,dta}。把该清单 + 16_article_alignment.parquet (C2 用) 复制至 `scratchpad/run_pre/` (只复制不动原件)。
1. **A/A 对照跑**: 钉死环境重跑 40 → 46 → 51, 命令写死 (repo 根执行, PowerShell 每条前置 env):
   `$env:NEWS_PROCESS_LLM_OFFLINE='1'; $env:PYTHONHASHSEED='0'; $env:MKL_NUM_THREADS='1'; $env:OPENBLAS_NUM_THREADS='1'; $env:NUMEXPR_NUM_THREADS='1'; $env:OMP_NUM_THREADS='1'; F:\Anaconda3\python.exe news_process\40_panel_export_main.py` (→ 46_stata_export.py → 51_falsification_test.py, 同 env)。
   与 `run_pre/` 备份比对, **预登记三项处理** (两项已知差异 + 一项排除规则): ① 单独重跑 40 时 mtime 守卫 (runner.py:399-410) 判 75_cross_media 新鲜 → 并入恰 9 列 (3442→3451, G9 预登记, R2 已双向核实); ② dta notes 注入态 (~66MB) → 干净态 (~8.2MB), **dta 比对仅走 pyreadstat 值层**, 尺寸/字节差勿立案; ③ BLAS 非确定 9 列按全名 drop 后再比。剥离后应零漂移 — 有其余漂移先定谳环境再开工。**A/A 跑完立即把「重跑产物清单」快照至 `scratchpad/chain_AA/`** (R3-P1: 重跑一律原地覆写 data/processed, 不快照则 A/A 基线在 C3 重跑时即被销毁, 链式 diff 物理不可执行)。
2. 每落一个 C3/C4/C5/C6: 同 env 同命令重跑 40 → 46 → 51; **重跑完成后立即把「重跑产物清单」快照至 `scratchpad/chain_C{n}/`**。**每环 diff = 相邻两快照** (chain_AA vs chain_C3, chain_C3 vs chain_C4, …), 一律不与盘面原位文件比。
3. diff 脚本逐列比对: 列集 + 逐格值; **判等 = `np.array_equal(a, b, equal_nan=True)` 逐位 (唯一放行判据, R2); `np.isclose` 仅用于漂移出现后的诊断分级报告, 不作放行判据**。白名单 (事前写死):
   - **C3**: 40/51 面板 `avg_llm_conf*` + `*avg_llm_conf*` z 衍生 (受影响格所在年份**全截面**变化属预期) + 40_article_bank_level conf 三列; 预期变化格 ≈ full 63 / ctx 50 / ss 39; **方向双向不作判据**;
   - **C4**: `log_sent_ctx/log_sent_ss` 两列, 变化格恰 {0.0→NaN}, **ctx=15 / ss=11 行** (强锚); 46 号 codebook.xlsx 中该两变量的 n_non_null 行随之变化, 按 var_name 归因为白名单内派生, 勿误判 (R4);
   - **C5**: 面板六列 + `40_attn_index_*` 的 `fintech_articles`/`ft_attn_*`/**`ft_vol_*`** (R4 补: 年表侧产物五列 schema 实含 `ft_vol_yr = log1p(_ft)` [attention_media.py:808], 必随修复漂移; 省/市侧产物无 ft_vol 列, 出现即属异常) (7-docid 分歧, _ft 只增不减); 值域告警按 D6 预登记;
   - **C6**: **白名单 = 空集, 预期逐位零 diff**;
   - 白名单外漂移 → §0.7 停线。
4. **46/51 重跑后 notes 重放**: `scripts/apply_stata_notes.ps1` (K7 护栏版, 覆盖 40/46/51 全部被重写 dta), 按既定法对账。

### 4.3 定向验证
- **C7**: scratchpad 只读驱动脚本, **镜像 tests/test_run_pipeline_function.py::_patch_config 机制** (进程内改 rpf.CONFIG 指向 scratchpad); 副本 = 15 + 21 main + 21_full **三件**; ① 原样断言 allow; ② **变异点 = 15 号副本的 content_ss 一字符** (避开 21 parquet 的 prompt_version schema metadata — pandas 重写会丢 metadata 走 legacy 兜底, 语义漂移) → 断言 reject 且 reason 含 "fingerprint differs"。⚠ 不存在"干跑到判定点"模式; 全链真跑归入 C11-D7。
- **C2 (R3 修正: 数据层判等 + A/A 参照臂 + 同 env 四钉)**: ① **执行点 = 紧随 §4.2.1、C1 落码之前** (R4: F2 先入树后"未改代码工作点"即不存在, 时序已入 §3/§4 总时序): 以 §4.2.1 同款 env (OFFLINE=1 + PYTHONHASHSEED=0 + BLAS 四钉) 重跑 stage 16 一次, 与 `run_pre/` 备份做**数据层判等** (read_parquet 双侧, 列集相等 + 逐列 array_equal(equal_nan=True), 排除 schema metadata) — A/A 臂应逐位相等, 红灯先定谳环境; ② F1+F2 落码后同 env 再重跑再判等 (预期逐位相等)。⚠ 禁用文件级 sha256 — parquet footer 内嵌 `data_version` schema metadata (UTC 微秒时间戳 + git_commit, data_versioning.py:180/:200/:264-283), 每跑必变, 文件级比对必然假红。
- **C8** (可选): Stata 冒烟。

### 4.4 日志扫描
真跑后 Bash grep ` - ERROR - ` 精确匹配; `│` 镜像行去重; r(###) 非字母边界。预登记: C5 后 ft_attn_* 值域告警 = F4 已知次生 (D6), 不停线; F4 own>cell 哨兵 = WARNING 双成因。

---

## §5 文档同步与收口 (C11)

1. **CLAUDE.md (+1 句, 逐字 diff 见 §2-F7)**: **随 C7 入库** (用户勾选批准后); 本节仅列为批准项, C11 不再动它。
2. **codebook longdesc** (单会话锁惯例): `F052_l2_llm_conf.md` (F3, D5 措辞) + `F411_l2_log.md` (F5, **全文 7 处核改**, §2-F5) + `F318/F320` (F4 any() 口径一句, 顺检)。锁的可操作判据: `.session_lock` 已永久入库 (b95a9535, 内容冻结 2026-07-10), 无运行时强制 — 占用判定 = 是否存在**活跃** longdesc 编排会话 (07-15 侧线已收口; 不明则问用户), 编辑时不动锁文件本体。
3. **收口全链跑 + codebook 重生 (决策点 D7; 命令与硬闸 R3 写死)**: §4.2 重跑后盘面为 G9 并入态 (51 号 3453→3462, 含 9 个 cross_media 列; 其中 8 列不在任何 longdesc 家族/structural_whitelist → 直接重生 codebook 会把 fallback 计数 0→8, 违反长文库终验归零惯例)。**默认处置 = C11 先做离线全链真跑**, 命令写死 (repo 根, §4.2.1 同款 env 前缀 + `HF_HUB_OFFLINE=1`/`TRANSFORMERS_OFFLINE=1`): `F:\Anaconda3\python.exe news_process\run_pipeline_function.py` — **显式禁带 `--skip-21-if-exists` / `--skip-unchanged`** (R3 实测: F7 修后 13 列指纹双侧 digest 相等 → skip 会放行, 21 号不重写 → 75 号 mtime [00:54] 仍新于 21 号 [00:45] → 9 列继续并入, 面板停在 3451 而非 canonical, D7 目标落空)。~67 分钟单实例窗口, 面板回 canonical 且携带 C3-C5 修正值 → 46/51 → notes 重放 → **两条硬闸**: (a) 重生 codebook 前实读列数 **40==3442 且 51==3453** (不满足禁止重生, 先查因); (b) **post-C11 收口 diff**: C11 后 51 号 vs chain_C6 快照的 51 号 — 预期 = 恰少 9 个 cross_media 列, 共有列除 BLAS 9 列外逐位相等 (F1/F2 在 25/26 全链真实路径 + 21 离线重放确定性的最终兜底锚)。然后重生 codebook (`F:\Anaconda3\python.exe news_process\scripts\generate_codebook.py`, 读 51 优先 + 缺失拒跑 — 前序已保证在位)。**完成判据 (R3)**: codebook 重生后、提交前定向跑 `pytest tests/test_codebook_longdesc.py tests/test_omni_fix_codebook.py tests/test_stata_notes_do.py -q` (或 `pytest -m fast`), 对照 pytest_B 零新增红灯方可提交 (pytest_B 在 C11 前, 最终提交态须被测试扫过)。用户若裁定跳过全链跑 → 按备选预登记 "+9 条目 & fallback 0→8" 单列用户裁定后再重生。产物 build/codebook/* 与代码同批 by-name 提交。
4. **生产重生披露清单**: avg_llm_conf 族 (D5 口径, 逐格双向)、ft_attn/ft_vol 族 + attn_index 侧产物 (any() 修正)、log_sent_ctx/ss (伪零→NaN)、bal_* (更名+扩 2025, 生产才可观测) — 均为缺陷修正非测度重设计。
5. **记忆库**: `fatal-defect-audit-2026-07-16.md` 追加修复状态与 commit 哈希。

---

## §6 刻意不做

1. **不改 stage 21 的 0.0 哨兵写入** (F3 根因侧): 哨兵语义被 stage 64 A1 修复与三轨存档块消费; 改 NaN 牵动 schema 契约/skip 守卫/离线重放宇宙; 消费侧掩码是既定形态。登记: v9/golden 重生窗口一并清理。
2. **不解决 stage 25 六矩阵驻留** (F1 残余): 登记生产播种前 sizing 探针 (post-13 行数 → N×dim×4×同驻数估峰值 → 超 0.7×128GB 先做 per-track 写盘释放), 与 M0 合并评估。
3. **不动 boilerplate tier2 / golden 重生 / 网络播种 / 人工标注窗口** (M0 在案)。
4. **不做 12 条已证伪候选的预防性加固**。
5. **不新增 config 开关/双代码路径** (F1 直接替换; 等价性由单测 reference arm 锚定)。
6. **不横扫 01/10 号以外的 degrade 型模板幻影名** (~7 个, §7-R8; 有守卫不崩只静默降级, 属敞口清理批)。

---

## §7 风险登记与开放决策点

| # | 决策点/风险 | 默认口径 | 挂谁 |
|---|---|---|---|
| D1 | bal_* 更名 (w0724→w0725 等) vs 保名只改端点 | 更名 (名实相符) | 用户可否决 |
| D2 | ATT-2 文章级身份 = any(对级 verified) | any() (LOO 自洽) | 用户可否决 |
| D3 | F9 mv xlsx target_bank 列; 缺则生成器补列 + 降级兜底 | §2-F9.3 | 实施时核证 |
| D4 | M4 动态推荐动作 (保结构替换) | 动态化 | 用户可否决 |
| D5 | F3 口径: 剔除"在场判伪/缺标"格的真实 conf (构念 = 有效票模型宏平均)。⚠ F3b 与 D5 **不同构** (验证参与域), 禁互相套用 | 采 | 用户可否决 |
| D6 | F4 次生: any() 后 LOO 比值理论可 >1 的处置 | WARNING 披露 + 保留自然值 + 放宽守卫预期; 实施前 dev 预分析 | 用户可否决 |
| D7 | **C11 收口全链跑 (R2)**: G9 并入态下直接重生 codebook 会 +9 条目 & fallback 0→8 | 先离线全链跑回 canonical 再重生 (~67 min); 跳过则预登记差异单列裁定 | 用户可否决 |
| R3 | 共享树并发: 基线重取 + 提交冻结 + B 侧哨兵 | §0.5/§4.1 | 登记 |
| R4 | C6 更名遗漏隐蔽消费者 | grep (scope 已写死) + A/B 零 diff 锚 | 已内置 |
| R5 | own_ft>cell_ft 双成因 (跨 geo 幽灵 docid 合法, test:346-376 依赖 clip) | 哨兵 WARNING 分诊, clip 保留 | 已内置 |
| R6 | F5 full 轨残余 (verified-but-undefined 全年, dev 0 行) | 登记, 生产重生窗口统一 | 登记 |
| R8 | degrade 型模板同族幻影名 ~7 个 | 登记, 后续敞口清理批 | 登记 |
| R9 | M4 目标文件为并发脏文件 | C10b 前置闸 (§2-M4) | 已内置 |
| R10 | **M4 tracked codebook md 陈旧行 (R2)**: 保持陈旧至下轮 02 真跑 | 预期不立案; 备选手工同步+披露 | 登记 |
| — | 已关闭项: 原 R1 (bal _ss 标签, 证伪见 §2-F6.2) / 原 R2 (指纹缺列, 证据见 §2-F7.2) / 原 R7 (flag 已扩入 13 列指纹, §2-F7.1) | — | 关闭 |

---

## §8 评审记录

四轮评审共 112 条 issue 全数裁定并入正文 (过程明细存档于会话 workflow 输出, 出处见文头证据链):

- **R1** (10 路逐条对码): 58 条 (1 P0 + 24 P1 + 22 P2 + 11 NIT), 全数采纳并入正文。
- **R2** (8 路: R1 闭环复核 + 新角度): 35 条 (8 P1 + 15 P2 + 12 NIT), 全数采纳并入正文。
- **R3** (4 路终审 + 首席评审官): 17 条 (2 阻塞 P1 已修 + 9 P2 + 6 NIT), 首席判词「并入 v1.3 后即可发船」; 首席独立抽验背书正文全部强锚 (13 列指纹 digest 相等 / F3 63-50-39 / F5 15-11 / F411 7 处 / G9 mtime / 全部行号引用零漂移); 独立闭环终验 10/10 簇 closed。
- **R4** (3 路终查 + 1 路删减): 2 条 P1 已修 (stage-16 A/A 臂时序落位; C5 侧产物白名单补 ft_vol_*); 代码对码路 0 issue (约 60 处引用零漂移, 数字锚独立复算全命中, F2 改点全仓反查恰 8 处无漏); 无关内容按删减提案压缩。

**终局状态: v1.4-final — 用户已完全授权实施 (2026-07-16), 按 §3 总时序执行。**

---

## §9 执行记录 (2026-07-16 实施完毕)

- **提交**: C1=9a88ec82 / C2=5214106c / C3=d0aeab2c / C4=e1a2cb40 / C5=152022c3 / C6=02a06586 / C7=c784a8a7 / C8=ca085dc4 / C9=ca1ac316 / C10a=23ab886e / C11=本提交; **C10b (M4) 按 §2-M4 前置闸选项(a) 顺延** — 两管道目标文件为并发会话活跃脏文件, 待其收口后单独实施。
- **验收全过**: A/A 对照跑恰 G9 九列并入+共有列零漂移; stage-16 A/A 臂两次 IDENTICAL (F1/F2 字节等价盘级铁证); 链式 diff 四环全部精确命中事前锚 (C3: 63/50/39 格+136/81/67 篇+z 全截面 / C4: **恰 ctx 15+ss 11 格** 0.0→NaN / C5: 六列+侧产物, 年表增量 +5/+2=**恰 7 篇** / C6: **12/12 IDENTICAL 零 diff**); pytest B⊆A (唯一新增红灯经取证归因并发会话 company_tax 未提交中间态, 我方提交 0 触碰该域); F8 复现包 Stata 实机冒烟 PASS (winsor 主循环真执行, 220×3451 加载, _prepared_panel 落盘); C11 全链跑 EXIT=0 + 双硬闸 (40==3442/51==3453; 收口 diff 恰少 9 列且共有列逐位相等) + notes 对账 3442/3442/3453 + codebook 重生 **fallback=0** + 定向 pytest 91 用例全绿。
- **每次重跑后 notes 均已重放** (A/A, C3-C6, C11 共 6 次, 对账全绿)。
- **残余登记不变**: §6.2 stage-25 sizing 探针 (M0 合并) / §7 R6 (F5 full 轨理论残余) / R8 (degrade 模板批) / R10 (M4 tracked md 陈旧至下轮 02 真跑) / C10b 顺延。

### §9-bis 执行结果严审勘误与补记 (4 路独立审核 + 首席终判 = acceptable_with_notes, 0 P0/0 P1/0 阻塞)

- **提交计数勘误**: "12 个提交" = 11 个整改提交 + 1 个计划提交 (69e0c355)。
- **CLAUDE.md F7 句披露**: 实际入库文本相对 §2-F7 批准原文做了**语义等价扩写** (增"上游"+四列名括注+标点调整, 准确超集零功能差) — 待用户追认; 若要求逐字可单独 docs commit 回改。
- **"定向 pytest 91 用例" 勘误**: 该读数不可复核 (当时控制台输出截断误计); 三路审核在 HEAD 独立重跑判据三文件 = **163 用例 0 失败** (更强), 结论不变。
- **panel_diff 覆盖面补证**: DEFAULT_FILES 未含 46 codebook.xlsx/labels.do (计划清单承诺项); 审核路已用留存快照补比四环 — 仅 C3→C4 恰 log_sent_ctx/ss 两行预期变化, 其余零 diff, 无实害; 教训 = diff 工具清单与备份清单应共用 SSOT。
- **C7 实盘驱动验证补跑 PASS**: 真实 15/21/21_full 三件副本 (1544 行) 原样 allow; 15 号副本 content_ss 单字符变异 → reject "fingerprint differs" (证据: scratchpad/c7_disk_driver_verification.txt)。
- **证据补档**: c6_diff.txt (12 件零 diff) / c11_closing_diff.txt (恰 2 件差 = −9 cross_media 列) / c2_stage16_equality.txt (run_pre 16 号 vs 全链终态数据层全等 — F1/F2 经真实全链路径的字节等价终证)。
- **时序备注**: C10a (M1) 落码先于 C6 链式重跑 — 离线 0-miss 下归档/缓存写路径不可达, 对链产物中性, 且被 C6 零 diff 锚顺带覆盖。
- **并发追认**: 并发会话当晚已将 company_* 域工作入库 (main=3ccd5df4, 含 G9 registry 激活), 与本计划零冲突; pytest_B 唯一新红即其未提交中间态所致, 已随其收口自然消退预期。
- **C10b/M4 收口 (1aca77f1)**: 并发收口后前置闸打开, 当晚即补齐 — 保结构替换年上界 (yearly×year_max 动态判定, 下界 listed=ipo_year / tax=reg_year 原样), tax 侧经 engine() 复用 listed helper (T-D10); +3 gate, 双管道套件 93 用例绿 (含并发收口后转绿的锁测试)。**至此 13/13 全部落地, 无顺延项**; §7-R9 (脏文件闸) 与 R10 (tracked md 陈旧) 关闭 — 下轮 02 真跑将以动态行重生 codebook md。

### §9-ter 推送前终局评审 (第一遍 4 路 + 首席 = ok_to_push, 0 P0/0 P1) 收尾勘误

- **"93 用例" 勘误** (与 "91→163" 同款控制台读数误计): HEAD 以文件重定向复核 = 双管道 panel 两套件 **130/130** (加 clamp gate 后 131/131)、panel+lock 四套件 145/145 全绿, 结论不变且更强。教训固化: 用例计数一律 `--collect-only`/文件重定向复算后入档。
- **M4 clamp 防御补齐** (终局评审 NIT): `recommend_year_keep_line` 的尾零判定按 `year_max` 钳制 (误标日期越窗的零星文章不干扰; 普查口径下纯防御) + gate 用例。
- **R10 措辞更正**: 双管道 panel codebook md 实为 gitignored 生成物 (从未被 git 跟踪), 旧 "tracked" 表述比事实更重 — 仓库从未携带陈旧 keep 行, 方向更安全。
- **证据目录复原**: scratchpad/c7_driver 的 15 号 parquet 已从变异态复原为原样副本并附注记 (防未来复跑 allow 臂得到 reject 假象)。
- 首席亲验背书: 13/13 修复锚在位 + 279 gate 全绿 + 待推送集密钥/大文件/夹带扫描零命中 + 盘面终态不变量 4/4 (40/51=3442/3453 列、log_sent 伪零三轨 0 行、avg_llm_conf 值域收敛、notes 三份在位)。
