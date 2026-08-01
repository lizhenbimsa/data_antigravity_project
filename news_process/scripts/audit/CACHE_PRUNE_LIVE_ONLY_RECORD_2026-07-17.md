# 三缓存库死条目清除收口记录 (2026-07-17)

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 用户裁定 (2026-07-16/17 会话): 对三大 LLM/嵌入/BERT 推理缓存库执行"只保留当前语料 ×
> 当前 prompt 构造可达键"的剪枝, **不备份、直接删除**全部死条目 (AskUserQuestion 三选项
> 中明确选"不备份，直接删除死条目", 拒绝 dry-run-only 与备份后删两案)。
> 本记录为该破坏性操作的仓库侧留档 (库文件本身在 gitignore 之外, 不随本记录入库)。

## 1. 结果

| 库 (data/processed/) | 条数 前→后 | 体积 前→后 | 删除内容 |
|---|---|---|---|
| `_llm_cache.db` | 213,323 → 29,088 | 2111.8 → 1327.5 MB | 三家 LLM 历史 prompt 版本 ~13.6 万; `gemini-3.1-flash-lite-preview` 31,477; 退役嵌入轨 `text-embedding-3-small` 9,655 / `text2vec` 4,880 / `bge-m3` 1,335; 现役两嵌入轨旧文本残渣 808; `fake-local-model` 测试泄漏 2 |
| `_llm_cache_validation.db` | 53,655 → 7,722 | 119.6 → 17.4 MB | 66/70 两阶段旧 prompt/旧样本变体条目 45,933 |
| `_local_model_cache.db` | 7,466 → 7,464 | 3.8 → 3.7 MB | 仅 `fake_a`/`fake_b` 测试泄漏行 2 |

活键基线 (T=2 语料, 剪枝时点): 生产库 29,088 = Qwen 8,567 / emb3-large 8,557 /
gpt-5.4-nano 4,012 / gemini31 3,976 / deepseek-v4 3,976; 验证库 7,722 (三家各 2,574);
本地 BERT 7,464 (三模型各 2,488)。

## 2. 活键枚举方法 (防漏枚举)

1. **运行时探针**: sitecustomize import-hook 包装 `core/caching.py::LLMCache.get/put/put_batch`,
   逐次记录 `库绝对路径|sha256 键` (含 v0 fallback 键); 经独立冒烟测试逐字节核验。
2. **生产库/本地库**: 八入口审计同环境 (OFFLINE+确定性, conda base 解释器) 真跑当前代码
   全执行面 — ① run_pipeline_function ② run_pipeline_validation ③ run_paper ④ 80 ⑤ 81
   ⑥ 82 + ⑦bis dimension_analysis (`--track all --include-lg`, 输出重定向 scratchpad)
   + verify_stage21_cache_coverage。⑦⑧ company 两管道经 grep 证实不消费这三库, 未跑。
3. **验证库 (66/70 在线付费 only, 离线整体跳过)**: 只读 fetch 桩 harness — 复刻两阶段
   main 的 fetch 前构造段 (确定性抽样 seed=42/N=1000 + 三轨掩码 / 4 变体 prompt), 直接调
   模块自身 `run_masked_llms`/`run_variant_llms`, `fetch_llm_async` 换成"仅 cache.get"桩,
   preflight 空转 — 零网络、零付费、零文件写入、绝不 cache.put (规避归档 mock 污染先例)。
   ⚠ 勿直接跑 66/70 的 main() 做枚举: 会覆写 eval_reports 真实报告。

## 3. 删除与验证

- 三段式: 死行先 `ATTACH` 转移至 scratchpad 隔离库 → `DELETE` + `wal_checkpoint(TRUNCATE)`
  + `VACUUM` → 全套复跑验证通过后物理清除隔离库 (兑现"不备份"裁定)。
- 安全闸 (全过): 现役模型族 (3 LLM + 2 嵌入 + 3 BERT) 每族活键数 > 0, 否则中止。
- 剪枝后验证 (全绿): ①② 离线复跑 EXIT=0 (离线 miss→raise, 误删必爆红);
  verify_stage21_cache_coverage = 13,896/13,896 全命中 0 miss; harness 复跑对剪枝后
  验证库命中 7,722 / 孤儿行 0 / 两轮枚举键集逐键一致 (46,332)。
- 主线 3 dta 变量级 notes 已按 `scripts/apply_stata_notes.ps1` 重放
  (40:3442 / 46:3442 / 51:3453 对账全等, sidecar 已刷新)。

## 4. 后果 (⚠ 永久性)

1. **历史 commit 离线复现锚失效**: checkout 旧 commit 后旧 prompt/旧模型键已物理不存在,
   `NEWS_PROCESS_LLM_OFFLINE=1` 离线 $0 复现自此**只对当前 HEAD 口径成立**。CLAUDE.md
   "勿删 `_llm_cache.db`" 铁律对今后仍有效 (库仍是当前口径确定性锚点)。
2. 退役模型 (旧 Gemini preview / emb3-small 等) 的付费响应**不可再生**, 已按用户裁定放弃。
3. 验证库既存事实 (非本次造成): 当前 66/70 构造需 46,332 键、库存仅 7,722 —
   S9 (2026-07-14) 修字后变体键大部分未播种, 属批次 E (M0 门) 付费补种范围。
