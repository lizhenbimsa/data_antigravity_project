# P4 收尾执行命令清单 —— 第三轨 `_ss` 付费跑 + golden 重生 + 终审

> ⚠ **2026-08-01 状态订正 (全仓 T=2 → T=19 清扫)**: 本文成文时, 本机盘上是**小样试跑面板**
> (2017–2018 两年, 文中或以「disk 1170 篇 / 172 行 / dev 盘」等措辞出现)。**2026-07-27/28 生产
> 全链跑通后, 本机盘面即为 T=19 全量** —— `40_panel_yearly` 23,693 行 × 4,183 列 /
> 1,247 banks × 19 years (2007–2025), 2026-08-01 以 pyreadstat 直读 `.dta` 元数据复核。
> 下文一切「盘上/当前/dev」规模陈述均为**成文当时**的事实记录, **不代表当前状态**, 且不得再被
> 援引为「样本太小/识别力不足/待全量复核」的现成理由。


> 2026-06-14。前置: P0–P3 代码已完成并验证 (检查点 A 字节平价 / 261 测试绿 / check_static_enums exit 0 / ruff 仅 4 预存)。
> **本清单在配好密钥+依赖的生产/干净环境执行。** ⚠ golden 重生**必须在干净 checkout** 上做 (见 §6 安全红线)。
> 平台: Windows PowerShell (本项目主环境); 命令从仓库根 `F:\WiseSearch\data_antigravity_project` 跑。

---

## 1. 环境变量
```powershell
# YUNWU_API_KEY: 已在 news_process/.env (本机实测 SET); 若新环境需手设:
$env:YUNWU_API_KEY = "<你的密钥>"
# 裸环境 SSL 修复 (yunwu.ai 证书): 见 memory yunwu-ssl-certifi-fix
$env:SSL_CERT_FILE = (python -c "import certifi; print(certifi.where())")
# stage 23 BERT 离线 (用本地缓存, 连不上 hf.co 时必设): 见 memory stage23-bert-rerun-hf-offline
$env:HF_HUB_OFFLINE = "1"; $env:TRANSFORMERS_OFFLINE = "1"
# NEWS_PROCESS_LLM_OFFLINE: 播种跑【不设/=0】(允许付费 miss); 播种完成后【=1】锁定 $0 离线复现
Remove-Item Env:\NEWS_PROCESS_LLM_OFFLINE -ErrorAction SilentlyContinue
```

## 2. 付费前置 (免费, 必做 —— 先看清成本再付钱)
```powershell
# (a) 重生 stage 14: 物化 content_ss / ss_is_fallback (FREE, 纯 pandas/AC)
python news_process/14_materialize_ctx.py
# (b) 重生 stage 15: fintech_intensity 三轨 (FREE) —— 让 stage 21 输入含 content_ss
python news_process/15_fintech_intensity.py
# (c) 实测 ss 真缺口 (= 你的付费敞口): 读缓存, 不调 API
python -m news_process.scripts.audit.verify_stage21_cache_coverage
#     → 预期 ss misses ≈ 非回退文章数 × 3 模型 (盘面 ~960×3≈2880; 全量按语料比例放大)。
#     ⚠ 别被旧值"15 misses"误导: 那是旧 14_*.parquet 无 content_ss → ss 假回退 full 的假象。
```

## 3. 付费播种 (stage 21 ss —— P4 唯一付费主项)
```powershell
# (d) 线上跑 stage 21 ss: 仅对 ss 真缺口调 API, full/ctx 全缓存命中 ($0)。
#     prompt v8 字节冻结, 仅 content 实参换 content_ss。
python news_process/21_tone_llms.py
# (e) 播种后核验: 期望 misses=0 (此后全离线 $0 可复现)
python -m news_process.scripts.audit.verify_stage21_cache_coverage
$env:NEWS_PROCESS_LLM_OFFLINE = "1"   # 锁定离线 (防后续误付费)
```

## 4. 下游阶段 (免费 / 本地)
```powershell
python news_process/16_article_policy_alignment.py   # 嵌入低成本 (ss 文本短; 缓存键于 text)
python news_process/22_tone_words.py                 # FREE (词典)
python news_process/23_tone_berts.py                 # FREE/本地 BERT (HF 离线)
python news_process/24_herd_decay_processor.py       # FREE
python news_process/40_panel_export_main.py          # 面板 (三轨 _ss 列落盘)
python news_process/46_stata_export.py               # .dta + 标签 + codebook
python news_process/51_falsification_test.py
# —— 或一键跑全 DAG (推荐, 自动按依赖序; ss 阶段 always-on 自动纳入):
# python run_pipeline_function.py
```

## 5. golden 重生 + codebook (在干净 checkout 上)
```powershell
# (f) 重生 golden snapshot (新增全部 _ss 列哈希)
python news_process/scripts/migrate/generate_golden_snapshot.py
#     → 手动: golden_panel_v0.json 的 schema_version 2→3; loader 改版本感知
#       (schema_version==2 时丢 _ss 列, 单一 golden 文件)。
# (g) codebook / 标签产物随 stage 46 重生: variable_codebook.{csv,json,md,xlsx} + 46_*_labels.do
# (h) repro 闸门
python -m pytest news_process/tests/integration/test_panel_reproducibility.py -q
```

## 6. 终审 (golden 重生后)
```powershell
python news_process/scripts/audit/check_static_enums.py        # 期望 exit 0 (0 漏列/0 陈旧注释)
python -m ruff check news_process/                              # 期望仅 4 预存 (_nx_probe / 审计脚本 SIM110)
python -m pytest news_process/ -q                              # 全量 sweep
# + 本会话已跑的【code-vs-code 平价审计】(铁律 §7.5#1); 若改了代码再跑一次
```

## 安全红线 (务必遵守)
- ⚠ **golden 重生只在干净 checkout** (`git checkout` 一个干净分支): 本机工作树有 176 改动 (多会话) + 3 个 BLAS 非确定网络中心度列 (`bank_clustering`/`cfbetween`/`harmonic`), 在脏树上 regen 会**误 bless 无关漂移**, 把 repro 闸门搞红 (memory: panel-3-network-cols-nondeterministic / golden 本机不可安全 regen)。
- ⚠ **勿删 `_llm_cache.db`** (407MB 确定性锚点); 播种只追加 ss 条目, 不动 full/ctx。
- ⚠ **prompt v8 字节冻结**: 改任何 prompt 模板会废掉全部 10530 缓存 → 重付费。
- 付费敞口随语料放大: 盘面 1170 篇 ~2880 calls; 全量 18.2M/T=19 须先用 `measure_bank_fintech_cooccurrence` 逐年估 ss 非空率再决定预算 (项目 LLM 预算量级见 memory paper_portfolio_decision_gates)。

## 已知预存失败 (非本次改动, 别误判为回归)
- `test_aggregate_track_decoupling` 3 async → `pytest-asyncio` 未装。
- `test_papers_benefit_society_shrinkage::test_mixedlm` → `statsmodels` 未装。
- `test_benefit_society_dual_track::test_cohort_csv_is_committed` → cohort CSV 缺盘 (git-ignored)。
- `test_column_hashes_match_golden[*]` → golden/盘面 desync (P4 重生即解)。
- 装齐 `pip install statsmodels pytest-asyncio opencc-python-reimplemented` 可消前三类。
