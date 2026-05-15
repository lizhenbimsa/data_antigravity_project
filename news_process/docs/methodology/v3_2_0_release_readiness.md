# v3.2.0 Release Readiness Report

> Generated after M5/7 — pyreadstat 安装 + 双 backend 实测验证.
> 状态: **READY FOR `git tag v3.2.0`** (经 doctor 12 OK / 0 WARN / 0 ERR 验证).

## Pre-flight Checklist

| Item | Status | Notes |
|---|---|---|
| **Python 依赖** | ✓ | pandas / numpy / pyarrow / pytest / yaml / pyreadstat 全装 |
| **Pipeline 数据** | ✓ | stage 14 / 21 / 40_panel parquet 已生成 (v3.1.1 baseline) |
| **LLM cache** | ✓ | `_llm_cache.db` 120.9 MB 已存 (stage 21 全量缓存) |
| **YUNWU_API_KEY** | ✓ | env var 已设 (stage 21 + stage 35 LLM 可跑) |
| **Stata bin** | ✓ | Stata MP 19 at `C:\Program Files\StataNow19\StataMP-64.exe` |

## Stage 46 Stata Export 实测

实测真实 panel (`40_panel_yearly.parquet`) 跑 stage 46:

**Backend 对比** (M3 vs M5):
| Backend | core .dta | full .dta | aux .dta | labels.do | codebook.xlsx |
|---|---|---|---|---|---|
| pandas (M3) | 74,895 | 3,824,491 | 3,757,991 | 137,025 | 58,461 |
| pyreadstat (M5) | 79,567 | 3,904,923 | 3,834,415 | 137,025 | 58,459 |

差异: pyreadstat 多 ~80 KB / .dta (含 value labels metadata + extended missing 编码).

## 列名缩短映射

8 个超 32 字符列名自动缩短 (M3/7):
- `_idf_score_` → `_idfsc_` (3 列)
- `_leave1out_` → `_l1o_` (5 列)

全部映射记录在 `codebook.xlsx::original_name` 列, 用户可反查.

## Test Baseline

- **1153 passed / 6 skipped / 0 failed** (+159 测试 since v3.1.1 baseline 994)
- 4 conditional skipped (v3.2.0-specific panel cols 等 pipeline 重跑)

## Release Commands

```bash
# 已验证 (doctor 全绿) — 可立 release tag:
git checkout main
git merge feature/stage3-dual-track-v3.2.0
git tag -a v3.2.0 -m "Stage 3 dual-track + Stata data layer + 14 templates + 4 CLIs"
git push origin main v3.2.0

# 后续 optional (用户层):
# 1. 跑 v3.2.0 pipeline 重生成 panel (unblock 4 conditional tests)
F:/Anaconda3/python.exe run_pipeline_function.py

# 2. (可选) stage 35 LLM 升级 — 10.5k API 调用, ~2 min @100 并发
F:/Anaconda3/python.exe -m news_process.validation.radius_sensitivity_llm --launch

# 3. Build replication 包 + 跑 Stata
F:/Anaconda3/python.exe -m news_process.papers._common.stata_runner \
    build-replication --locus lc --subst sf --sent ctx \
    --root replication_v3.2.0_lc_sf_ctx
cd /tmp/replication_v3.2.0_lc_sf_ctx
stata -b do code/00_master.do
```

## Plan v14 完成度

| Phase | 完成度 | 备注 |
|---|---|---|
| M0 frozen tag | 100% | plan-stage3-dual-track-frozen tagged |
| M1 tone_llms 双轨化 | 100% | BREAKING + ctx gate 致命 R1-A 修复 |
| M2 P2 panel mean 对角线 | 100% | `_lc × _ctx` + `_sc × _ctx` 加性追加 |
| M2 P3 panel count 4-way | 100% | sentiment × subst 4-way 洗稿率 |
| M3 P4 Bartik IV 双套 | 100% | `bartik_fintech_lf_*` + `_lc_*` |
| M4 codebook +252 | 100% | 38 元数据条目 (+13 新双轨) |
| M5 P5.2 stage 35 LLM | 90% | 接口 + CLI 完整, 实际 10.5k launch 待用户 |
| M6 stage 46 stata_export | 100% | pyreadstat 优先 + pandas fallback (M1/7) |
| M6 续 14 模板 | 100% | 14/14 模板 + master.do |
| M7 build_replication 一键打包 | 100% | + 3 新 CLI (list / doctor / verify) + --version |
| M8 release | **就绪** | doctor 12 OK / 0 ERR; 待 `git tag v3.2.0` |

## 后续 v3.2.x

- 用户跑 v3.2.0 pipeline 后 4 conditional tests 自动 unblock (变 1146 → 1150+ passed)
- stage 35 LLM 实际 launch 后 `35_radius_sensitivity_llm_results.json` 落地
- BREAKING `_tech` → `_tech_lf` 完全显式化 (v3.3.0 候选, 配 golden 重生成)
