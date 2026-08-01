# 致命问题再审计收口执行计划 (FATAL_REAUDIT_CLOSEOUT) — 2026-07-12

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是 **T=2 试跑面板**
> (2017–2018 两年; 各文成文时点的具体行数以文内记载为准 —— 本仓 168/172/176 三值并存)。
> **2026-07-27/28 生产全链跑通后, 本机盘面即为 T=19 全量**
> —— `data/processed/40_panel_yearly` 23,693 行 × 4,183 列, 覆盖 1,247 banks × 19 years
> (2007–2025), 2026-08-01 实读复核 (`26_staleness_panel` 6,224 行 / year∈[2007,2025];
> `51_panel_with_controls` 23,693×4,194)。下文一切「T=2 / dev 盘面 / 试跑盘」表述均为**成文
> 当时**的事实记录, **不代表当前状态**, 且不得再被援引为「识别力不足/退化属预期/生产放大
> 后自然恢复」的现成理由 —— 其中 Bartik one-hot 退化一项已被 T=19 实跑证伪 (见
> `pipeline/panel/iv_did.py` 模块头第 3 条)。


> 状态: 已授权执行 (用户 2026-07-12 全量授权)。范围切分: §2 dev 侧 golden-safe 修复 = 本会话立即执行;
> §3 M0/生产窗口项 = 本机结构性不可执行 (付费不可逆/无生产语料/改测度列), 仅排程与依赖定序。
> 审计谱系: 三轮共 13 路只读 agent (5 发现 + 3 对抗 + 5 终审) + 主线逐行终验 + fast 套件实跑。
> 基线: main = b265f8f2 起审, 期间并发 codebook 会话推进至 0089dc75 (F144/F170 已随其修复入库)。
> 行号约定: 本文全部 file:line 为**起审基线 b265f8f2 坐标** (§2 实施后 encode.py/panel runner.py
> 行号已整体下移, 以 fix(reaudit) commit diff 为实施后权威坐标)。

## §0 终审问题台账 (全部经 ≥2 轮独立核验)

| # | 问题 | 终审定级 | 处置 |
|---|---|---|---|
| R1 | BERT vw/mw/hw 加权族物理域分母 vs 失败哨兵 NaN 分子 (生产条件性向 0 偏) | **P1 (生产条件性)** | WP-A1 观测闸 (立即) + WP-B1 掩码根治 (M0) |
| R2 | `strategic_diff.py:1815` ctx/ss 轨 LDA 零日志裸吞 | P2 (纯可观测性) | WP-A2 (立即) |
| R3 | `scripts/migrate/v7_wz_audit.py` miss 分支无离线守卫且写生产缓存 (与生产同 v8 键空间) | P2 | WP-A3 (立即) |
| R4 | `_constants.py:288` bank_keywords 加载失败 fail-open → 步骤 6 静默跳过 + 近重簇代表占位可丢样本 | P2 | WP-A4 (立即) |
| R5 | `encode.py:2176-2181` 与 `runner.py:441-442` 注释前提已被 NaN 哨兵契约 (omni-g-berts-02, 2026-06-11) 废止 | P2 (文档) | WP-A5 (立即) |
| R6 | CLAUDE.md 过期句: `_cache/_llm_cache.db 0 字节空壳` 已不存在; `LLMS_DIC_OFFLINE` 双开关未披露 | P3 (文档) | WP-A6 (立即) |
| R7 | codebook_longdesc frontmatter 值内裸冒号三连发 (F144→F170→F192, 均已对方自愈) | P2→已过时 | §4 转告项 (不触碰对方工作区) |
| R8 | entity_context 别名降级中间态 (单阶段调试可达 + strip/规范名两处口径不对称) | P3 观察项 | §3 后批 (与 R4 同族, 不阻塞) |

**经三轮对抗后维持"非问题"的结论** (不再复审): 门控双副本/缓存键/skip 守卫/DAG 计数/SSOT 现行值/
面板 frac 分母逐轨/per-model 门控分母/bert_distribution 数学/load.py 丢源 (F7 文档化设计)/
dict 族加权分母 (结构性不可达: stage 13 硬过滤 + prepend_title ⇒ 存活行必含真实 token, 盘上 90 列 NaN=0)。

## §1 R1 缺陷链终验记录 (逐行, 本会话主线亲验)

1. `tone_berts.py:1006-1009` `_failure_result` 概率 = `float('nan')`, label=None, num_windows=-1;
2. 防线唯一: 批级异常 → 逐篇重试**恰一次** (`:1066-1078`), 长度缺位也补失败哨兵 (`:1084-1085`);
3. `runner.py:436-476` `_build_llm_valid_masked_weights` 仅 LLM 族; `:441-442` docstring 拒绝 BERT 的
   理由 ("score=0 非 NA") 与 1 矛盾;
4. `encode.py:2209-2211/2239-2243` BERT pos/neg 的 vw/mw 分母 = 物理域 `denom`/`mw_denom`
   (HW 段同构); NaN 分子行被 groupby sum skipna 剔除而分母含其权重;
5. `grep infer_failed pipeline/panel/` 代码级消费 = **0** (仅 2 处注释) — 哨兵列
   `{sn}_infer_failed_{full,ctx,ss}` (`tone_berts.py:1154` + 主函数加轨后缀) 无人看。
影响列族: {finbert_cn, fin_sent_zh, finbert2} × {pos, neg} × {vw, mw, hw} × {full, ctx, ss} = 54 列
(mean 族 `{b}_pos/neg` 不受影响 — mean 分子分母同 skipna)。本机 T=2 实测失败率 0, 无现行污染。

## §2 立即执行工作包 (全部 golden-safe by construction: 纯日志/守卫/注释, 零数值路径改动)

- **WP-A1** `pipeline/panel/runner.py` 主输入加载 (`:688` 后): 统计 `*_infer_failed_{full,ctx,ss}`
  列 `== True` 总数; >0 → `logger.error` 点名受影响加权族与根治 DEFER; =0 → 一行 info。
  判真用 `(df[cols] == True)` 而非 `.astype(bool)` (防 NaN→True)。
- **WP-A2** `strategic_diff.py:1815`: 镜像 `:1576-1577` 补 `logger.warning`, 带 `{_tsfx}`/`{year}`
  上下文 (两变量在作用域: `:1780`/`:1794`)。
- **WP-A3** `v7_wz_audit.py` `call_llm_with_cache` miss 分支 (`:74` 前): 仓内标准离线判式
  (`('1','true','yes','on')`, 同 embedding_engine.py:322-323) → `raise RuntimeError`。不改 CACHE_DB
  指向 (miss-only put 无法覆盖冻结条目, 保守最小改)。
- **WP-A4** `pipeline/preprocess/runner.py` `main()` banner 后: `BANK_KEYWORDS` 空 →
  `logger.error` + `SystemExit(1)` (镜像 `news_bank.py:577` 先例)。放 main() 运行期而非
  `_constants` import 期 (import 期 SystemExit 会误伤仅 import 的测试/工具)。config 正常时永不触发。
- **WP-A5** 注释更正: `encode.py:2176-2181` (dict=结构性无 NaN / BERT=失败哨兵 NaN 无掩码,
  根治 DEFER M0, 观测闸=WP-A1) + `runner.py:441-442` 同步。
- **WP-A6** CLAUDE.md: 删 `_cache/_llm_cache.db 0 字节空壳` 过期括注; Environment Variables 段
  补一行 `LLMS_DIC_OFFLINE` 双开关警示。

验证协议: 全量 fast 套件, 基线红 = cohort×2 + jieba order-flaky (2026-07-10 在案) + codebook YAML
红 (应已随 0089dc75 消失) — 判据 = **零新增红**。不动任何 parquet, 无需 baseline-stash A/B。
提交协议: 严格 by-name (仅本计划文件 + 6 个修点文件), 排除 codebook_longdesc/*、`*constants.json`、
`.session_lock`; git root = 父目录, 路径带 `news_process/` 前缀; 不 amend、不 --no-verify。

## §3 M0/生产窗口排程 (修正后的定序, 本机不可执行)

依赖链 (→ = 解锁):
1. **探针: 硅基流动 >256 批限流** — 最先 (最便宜, 解锁全部嵌入播种)。注意: 429 无自动降级
   (flat 重试 `EMB_MAX_RETRIES` 次×固定间隔, 耗尽同样崩), 400 立即 ValueError 崩; 必要时人工下调
   引擎批上限 (≤2000, 与 `_lg` 共享)。
2. **boilerplate §3-P0 分叉裁定** (与 1 并行): per-entry 字节实测 → 预算内=校准 40M 占位;
   超预算/跨 [~40GB,~140GB] 区间 = **tier2 必做非可选** (BOILERPLATE 计划 :114/:200)。
3. **F1b 标识列 dtype 根治** — 纯代码, 可提前 ship (FATAL 计划 R2: 硬发布门, F1 不得单独上 T=19;
   建议下一 dev 批实施 + `NEWS_PROCESS_STRICT_SOURCES=1` 首播)。勿与已实施的税调同名 F1(b) 混淆。
4. **网络轨嵌入播种费用实测 + stage 21 全量付费重跑** (依赖 1; 受 M0)。
5. **golden 全量重生 — 绝对最后** (依赖 2/3/4; `PYTHONHASHSEED=0` + BLAS 钉 1)。窗口内打包:
   **WP-B1 BERT 掩码根治** (镜像 `_build_llm_valid_masked_weights` 建 `_wd_{wtag}_{b}{track}`,
   dict 族刻意不动 — 结构性无 NaN, 改了反而假修) + F6 (innovation confidence verified 门控) +
   `_KNOWN_BLAS_RE` 宽清单 vs 9 列清单实证统一 + BERT net_tone 9 列 + gate 测试
   (fixture 含 infer_failed 行断言掩码分母)。
6. **决策项** (无数据依赖, 随时定谳): G2(b) cooc 五上游指纹硬锁 (EIGHT 计划 :75 "首播前定谳");
   税调 F1(a) 短名 FP 过滤 + 02/03 重生成本收益 (FIVE 计划, 受 M0); R8 entity_context strip 口径统一。
陈旧红基数以最新实测为准 (2026-07-11 FATAL R2 = 14 阶段, 随盘面漂移, 勿引旧数 17)。

## §4 转告项 (不触碰并发工作区)

codebook_longdesc 写手会话: frontmatter 标量含 `:` 一律加引号 (F144/F170/F192 三连发同病灶);
建议固化进写手 prompt 或骨架生成器 `build_codebook_family_map.py` 的转义逻辑。

## §5 SSOT 未来漂移点备案 (现值全一致, 无互锁, 低优先)

`export.py:1064-1350` 标签块 / `stata_audit.py:455` / `generate_all_labels.py:147-151` /
`build_codebook_family_map.py:637-714` 的模型名字面量副本; `stata_export.py:787` 与
`tone_validation.py:2621` 的 `except Exception` import 回退。改模型集时须 grep 同步。
