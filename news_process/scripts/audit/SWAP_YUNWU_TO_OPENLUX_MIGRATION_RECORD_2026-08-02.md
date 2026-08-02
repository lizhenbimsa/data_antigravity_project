# 聚合中转平台迁移记录: yunwu.ai → OpenLux (2026-08-02)

> 用户指令：「全面更换 AI 模型聚合中转平台，将 yunwu.ai 聚合代理全部修改为 OpenLux 聚合代理。
> 变量 `YUNWU_API_KEY` 修改为 `OPENLUX_API_KEY`，`YUNWU_FULL_KEY` 修改为 `OPENLUX_FULL_KEY`。
> OpenLux 的 Base URL 是 `https://api.openlux.ai/v1`。以最高标准进行最系统最全面的评审、审核和验证。」

> 前置基线：`git status` 干净树 (HEAD = `3c5cd152`)。

---

## 0. 变更摘要

| 项 | 迁移前 | 迁移后 |
|---|---|---|
| OpenAI / Google 两家 LLM base_url | `https://yunwu.ai/v1` | **`https://api.openlux.ai/v1`** |
| `_lg` co-primary 嵌入孪生轨 base_url | `https://yunwu.ai/v1` | **`https://api.openlux.ai/v1`** |
| 主密钥变量 | `YUNWU_API_KEY` | **`OPENLUX_API_KEY`** |
| 词典管道密钥变量 | `YUNWU_FULL_KEY` | **`OPENLUX_FULL_KEY`** |
| 词典管道端点覆盖变量 | `YUNWU_BASE_URL` | **`OPENLUX_BASE_URL`** |
| 密钥**值** | (51 字符) | **不变** (用户裁定沿用同一串; 已实测 OpenLux 认此 key) |
| DeepSeek 直连 `api.deepseek.com` | — | **零改动** |
| 硅基流动 Qwen 嵌入主轨 `api.siliconflow.cn` | — | **零改动** |

## 1. 🔑 最重要的不变量: 缓存零失效

缓存键 = `SHA256(model_id, prompt, prompt_version, temperature[, seed])`
(`core/caching.py::_make_key`) —— **不含 base_url / 端点 / 密钥**。链条逐层核实:

| 环节 | 键输入取自 | 本次 diff 是否触及 |
|---|---|---|
| stage 21 LLM | `model_id = model_cfg['model_name']` (`tone_llms.py:721`) | ❌ 未触及 |
| 嵌入 | spec 的 `model` + `text_pipeline_version` (`embedding_engine.py:372`) | ❌ 未触及 |
| prompt / temperature | Prompt v8 冻结 / 0.0 | ❌ 未触及 |

**机械证据**: 对 `config/{sentiment,features}.yaml` 的 diff 过滤
`model_name|short_name|model:|text_pipeline_version` → **零命中**。

**实证**: 缓存库前 3000 行 `model_id` 分布 = `gpt-5.4-nano` / `deepseek-v4-flash` /
`gemini-3.1-flash-lite`，与迁移后 config 的 `model_name` 逐字相同。

⟹ 137 GB `_llm_cache.db` 全部条目迁移后**仍逐位命中**: 零付费重播种、golden 零漂移、
离线 `NEWS_PROCESS_LLM_OFFLINE=1` 复现不受影响。
⚠ 反向纪律: 换端点时**切勿**顺手改 `model_name` / `model` / `text_pipeline_version` —— 那才会炸缓存。

## 2. 处置口径 (三分法, 用户逐项裁定)

| 类别 | 处置 | 依据 |
|---|---|---|
| **活代码 / 配置 / 测试 / 文档 / 生成产物** | 全量改 OpenLux | 描述的是当前技术栈 |
| **历史取证** (审计报告 / 原始探针响应 / API 存档 / 运行日志 / 日期归档) | **保留原文** + 加 `2026-08-02 状态订正` 横幅 | 记录的是当时对 yunwu.ai 的真实调用; 改写即伪造取证链 |
| **11 篇论文手稿** | 改 OpenLux + 加 provenance 脚注 | 正文反映当前栈, 脚注说明本文数据的推理发生在迁移前、经确定性缓存逐位复现 |

## 3. 落盘清单

| 批次 | 文件数 | token 数 | 手段 |
|---|---|---|---|
| 活代码/配置/测试/文档/longdesc SSOT/手稿 | 137 | 557 | 受控迁移器 (有序规则 + 字节闸 + 幂等) |
| `.env` (真实密钥, gitignored) | 1 | — | 保值改名; 备份 `.env.bak.20260802` |
| `build/codebook/*` + `data/processed/variable_codebook.{csv,xlsx}` | 4 | — | **按 SSOT 重生** (`scripts/generate_codebook.py`, EXIT=0) |
| `data/processed/apply_notes_part*.do` | 7 | 1,179 | 同规则字节闸迁移 |
| `build/codebook_inputs/*/source_excerpt.md` + `build/manual_facts/*` | 16 | 31 | 同规则字节闸迁移 |
| 手稿 provenance 脚注 | 14 | — | 12 `\footnote{}` (挂句末) + 2 markdown 披露句 |
| 历史文档状态横幅 | 22 | — | 19 份 H1 后横幅 + 3 份探针 docstring 注记 |
| 失实归属订正 (自审发现) | 8 | 18 | 见 §5 |

## 4. 验收闸 (全部通过)

1. **字节级闸**: 把 before 的 OLD token、after 的 NEW token 各替换为同一哨兵后两串
   逐字节相等 ⟹ 证明「替换 span 之外零改动」。137/137 + 16/16 + 7/7 全过。
2. **幂等**: 迁移器二次运行 → 0 命中。
3. **SSOT 重生零漂移**: `build/codebook/variable_codebook.json` **逐字节等于**
   「提交版施加同一替换规则」的结果; `.md` 在 **208,671 行中恰好 1 行不同 = 生成时间戳**。
4. **全仓零残留**: 无 gitignore 约束的全仓扫描共 141 个文件仍含 `yunwu`,
   **逐一归入刻意保留类** (91 历史审计+取证 / 33 原始 API 响应存档 / 8 运行日志 /
   3 日期归档 / 3 历史变更记录 / 1 已废弃脚本 / 1 venv dist-info / 1 本次 .env 备份),
   **未归类真残留 = 0**。活代码中 `YUNWU_*` 读取点 = 0, 活端点残留 = 0。
5. **config 加载**: `-W error::UserWarning` 下零警告 (证 `.env.example` ↔ yaml `${VAR}` 契约完好);
   5 个槽位占位符全部正确解析; `YUNWU_*` 已从进程环境消失。
6. **静态**: 改动 `.py` 全部 `py_compile` 通过; `ruff check news_process` → All checks passed。
7. **测试**:
   - 受迁移直接影响的 7 个测试文件: **88/88 passed**。
   - **迁移安全性定向集** (`-m fast -k "config or cache or dag or shim or llm or embed or
     prompt or env or archive or radius or masking or schema or lineage or determin"`,
     覆盖平台迁移可能破坏的全部表面): **899 例 = 898 passed + 1 skipped, EXIT=0, 零失败**。
   - **`pytest -m fast` 全量** (排除既有超慢文件 `test_dedup_sensitivity.py`, 见 §6.6):
     **5,235 例 = 5,195 passed / 28 failed / 12 skipped**。28 个失败经逐条归因,
     **全部为既有红灯, 零新增** —— 归因见 §4a。
8. **端点连通** (只读, $0): `GET /v1/models` → HTTP 200, 481 个授权模型;
   `gpt-5.4-nano` / `gemini-3.1-flash-lite` / `text-embedding-3-large` **三个生产依赖模型全部在授权列表内**。
9. **端到端 schema 冒烟** (绕缓存直连, 共 42 token):
   - `gpt-5.4-nano` HTTP 200, `response_format=json_object` 生效, `choices[0].message.content` 可 `json.loads`;
   - `gemini-3.1-flash-lite` 同上;
   - `text-embedding-3-large` HTTP 200, `data[0].embedding` **维度 3072, 与 config 契约一致**。

## 4a. fast 全量 28 个失败的逐条归因 (结论: 零新增)

| 失败簇 | 例数 | 归因 (与本次迁移无因果的证据) |
|---|---|---|
| `test_stata_labels_zh` 三门 + `test_codebook_family_map` | 4 | 断言主体全是 **`bal_w0725_*` 列族** (缺中文标签 / 面板有而家族图无 741 列), 与 T=19 面板的列族扩张同步性有关; 该字符串既不含 `yunwu` 也不含 `OpenLux` |
| `test_company_{bank,tax_bank}_{altagg,cooc_registry}` SHA 锚 | 7 | registry sha 锚随 T=19 生产面板重生漂移 (见 commit `f1f358ba`「两个 cooc registry 随 T=19 生产面板重生 3,442→4,183 列」) |
| `test_citation_gate_hardening::TestAdmitNewDois` | 8 | Crossref 网络依赖门, 与聚合代理无关 (不同域名、不同凭据) |
| `test_benefit_society_dual_track` cohort 两项 | 2 | 已记载的慢性红 (memory `eight-entrypoint-fifthrun-audit`: 「cohort 2 项 + jieba 套件 flake = 慢性红勿再立案」) |
| `test_omni_fix_strategic::test_global_jieba_stays_pure_isolation` | 1 | 同上, jieba 全局态 flake |
| `test_strategic_diff_year_parallel` ×2 + `test_subprocess_log_isolation::test_ns_level_env_override` | 3 | 断言的是 `EMB_API_CONCURRENCY` / `NEWS_PROCESS_NS_LOG_LEVEL` 两个环境变量的**跨进程传播**, 二者本次 diff **均未触碰** |
| `test_omni_fix_attention::test_intermittent_media_excluded` | 1 | 平衡面板媒体覆盖逻辑, 与 API 路由无关 |
| `test_qwen_semantic_validity::test_qwen_large_cosine_agreement` | 1 | ⚠ 唯一初判可疑项, 已查实: 该测试 **`_load_panel()` 只读盘上面板 parquet, 零 API 调用**; 面板 mtime = 2026-08-01, 早于本次迁移且 `git status` 无任何 `.parquet`/`.dta` 改动 ⟹ 五对 ρ∈[0.52,0.66] 是**面板既有事实**, 不可能由本次改动产生 |

**已排除的全部致因机制**:
① 缓存键 —— 不含端点, 三个键字段零改动 (§1);
② 面板数据 —— `.parquet`/`.dta` 零改动;
③ codebook 产物 —— 重生结果**逐字节等于**「提交版 + 同一改名规则」(§4.3);
④ 环境变量 —— 失败涉及的两个 env var 均未被本次改名触及;
⑤ Stata 标签长度预算 —— 平台名**零次**进入变量标签 (标签 max=39 字符, 上限 80, 零超限),
   仅出现在无紧预算的长描述/notes 中;
⑥ 平台名字面 —— 28 个失败的断言文本中 `yunwu`/`OpenLux` 出现次数 = **0**。

## 5. ⚠ 自审发现并订正的失实归属 (18 处)

机械替换会把**在旧平台观测到的、带日期的经验事实**整体改挂到新平台名下 —— 属
memory `mechanical-sweep-damage-patterns` 的「禁把当前换成新值」误伤型。已逐处订正:

| 现象 | 处数 | 订正为 |
|---|---|---|
| 「OpenLux 中转自 **2026-07-10 00:00** 起静默过滤采样参数」(该日期早于本次迁移) | 9 | 「中转平台自 2026-07-10…」+ 标注观测于迁移前的 yunwu.ai 代理、OpenLux 未复测 |
| 「实测 kimi-k2.6 在 **OpenLux** 代理下默认上限偏低 (约 4,096)」(实测做在旧平台) | 2 | 「在中转代理下…(实测于迁移前的 yunwu.ai 代理, OpenLux 未复测)」 |
| 「v3 锁定基于 **OpenLux** /v1/models 授权清单」(v3 锁定发生在旧平台) | 1 | 「v3 锁定时基于中转平台清单; 2026-08-02 迁 OpenLux 后已实测三家均在其授权列表内」 |
| 「v6/N7 之后统一的 **OpenLux** key」(v6/N7 是旧平台上的收敛) | 2 | 拆为「v6/N7 起三 slot 共用单 key」+「2026-08-02 平台迁移、变量更名」 |
| SSL 证书主机名写成品牌名 | 2 | `api.openlux.ai 证书` |
| 并发上限缺迁移限定语 | 3 | 见 §6 |

## 6. 🔴 遗留风险与后续待办 (未由本次迁移解决)

1. **并发上限系在旧网关上标定, OpenLux 限流特性未实测** ——
   `sentiment.yaml::max_concurrency=500` (2026-07-25 决策)、
   `validation.yaml` 两处 `max_concurrency=250` (2026-07-21 决策) 均基于 yunwu 网关。
   不同聚合商的 QPS/TPM 策略不同, **迁移后首次生产跑 stage 21 必须盯 429 与弃票率**;
   若雪崩, 降序回退 250 → 100。三处均已就地加限定语。
2. **`apply_notes_part*.do` 的既有阻塞未变** —— CLAUDE.md 记载的「生成期快照被就地半改、
   须先按 SSOT 重生再重放」阻塞**依旧成立**。本次只做了 yunwu→OpenLux 归一 (使其不会把
   陈旧平台名灌进交付 `.dta`), **不等于**解除该阻塞; 正式重放前仍须走 stage 46 `stata_export` 重生。
3. **`docs/reference/env_vars.md` 的模型名示例陈旧** (仍写 v6 的 `gpt5nano`/`gemini3`/`grok41`,
   与 v3 锁定的 `gpt54nano`/`gemini31`/`deepseekv4` 不符) —— **本次未改** (属既有文档陈旧,
   非平台迁移范围)。建议单独订正。
4. **`LLMs_for_dic/保存20260214/` 日期归档快照刻意冻结** —— 其 `config.py` 仍读
   `YUNWU_API_KEY`/`YUNWU_BASE_URL`, 迁移后若直接运行会取到空 key。归档件按定义冻结,
   如需运行请用已迁移的 `LLMs_for_dic/` 活根或 `news_process/LLMs_for_FinTech_dic/`。
6. **`pytest -m fast` 全量含一个既有超慢用例 (非本次引入)** ——
   `news_process/tests/test_dedup_sensitivity.py` 单文件 **>240s 未结束**、pytest 进程 RSS 约
   **33 GB** (MinHash/LSH 去重敏感性)。同批邻近文件耗时对照: `test_cross_model_kappa` 2s /
   `test_d_group_modules` 3s / `test_data_versioning` 5s / `test_derivative_replication` 16s。
   本次 diff **未触及任何 dedup 相关文件** (`git status | grep -i dedup` 为空), 故与迁移无因果。
   ⚠ 连带订正 CLAUDE.md 旧载「`pytest -m fast` 快测 (~30s, commit 前)」—— 实测 fast 共
   **5,253 例**, 该描述已严重失真。建议单独立案: 给该用例加 `@pytest.mark.slow`
   或缩小其样本量, 否则 fast 门在实践中跑不完、形同虚设。
7. **`data/processed/21_tone_llms_lineage.json` 仍记 yunwu 端点** —— 它是 stage 21 每次运行
   重生的 provenance, 记录的是**上一次真实运行**的端点; 下次跑 stage 21 会自动写成 OpenLux。

## 7. 复现命令

```bash
# 端点探针 (只读, $0)
python - <<'PY'   # 见 §4.8; 或直接 curl
PY
curl -s -H "Authorization: Bearer $OPENLUX_API_KEY" https://api.openlux.ai/v1/models | head -c 200

# 零残留复扫 (无 gitignore 约束; 结果应全部落在 §4.4 的刻意保留类)
grep -ril yunwu . --exclude-dir=.git --exclude-dir=__pycache__ \
  --exclude=*.parquet --exclude=*.db --exclude=*.dta --exclude=*.xlsx --exclude=*.pdf --exclude=*.pyc

# 配置契约门 (须零警告)
python -W error::UserWarning -c "from news_process.core.config import load_config; load_config()"
```
