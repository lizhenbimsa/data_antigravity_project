"""news_process — bank-fintech news to bank-year panel pipeline package.

This file makes the project root a real Python package, enabling
``import news_process.<sub>`` from any cwd. See the project root README.md
for the layered topology (core / pipeline / papers / papers_assets /
validation / config split / etc.) and CHANGELOG.md for the phase-by-phase
architectural evolution.

v2.0.0 / phase-8-baseline (2026-05-04): the full restructuring program
(Phases 0 → 8) is complete. End state:
  - 26 numeric-prefix root scripts: all ≤30-line thin shims
  - news_process.{core, pipeline, papers, validation, scripts, config}:
    full canonical layout, single declarative DAG (core/dag.py)
  - 7-domain split config + externalized prompts
  - Multi-paper productization (papers/ + papers_assets/)
  - Data layout normalized: data_processed/ → data/processed/ (Phase 8)
  - Full pytest: 778 passed / 7 skipped / 0 failed.

v2.1.0 / phase-9-baseline (2026-05-08): post-restructure cleanup of
Phase 3 / Phase 7a residue, no new abstraction introduced:
  - 9c: 5 broken audit/test scripts removed (Phase 7a fallout)
  - 9d: orchestrator OUTPUT_REGISTRY fallback dict removed; new
    STAGES_MAIN ↔ OUTPUT_REGISTRY consistency test added
  - 9a: 5 papers/<id>/dag.py shells (5×``STAGES = list(STAGES_MAIN)``)
    removed; public API ``papers.<id>.dag`` retired (no external
    consumers); STAGES guard transferred to analysis module
  - 9b: 5 reflection-import blocks in paper analysis.py replaced by
    canonical-import bridge ``papers/_common/pipeline_runner.py``;
    Phase 2a reflection-purge invariant restored for production code
  - 26 thin shims: untouched (preserved for true v3.0)
  - Full pytest: 772 passed / 6 skipped / 0 failed (v2.1.0 release tag baseline).

Post-v2.1.0 HEAD (recode round 1+2 + feat/refactor 5 个子 commit):
  - +10 回归测试 (test_dag_consistency 增 cross-stage uniqueness invariants 等)
  - Full pytest: 782 passed / 6 skipped / 0 failed.

Post-recode round 3 (Plan-r3 P0-P3, 2026-05-09): 第二轮 17 单元修复
  - P0-1: yunwu API key 轮换 + git filter-repo 改写 3 commit history + force push
  - P0-2: pipeline/panel/export.py STATA_LABELS dedupe (9 dup -> 0); +2 invariant test
  - P1-5/6/7: papers_assets/llm_peer/ 资产目录补齐 + 4 衍生 paper 骨架文档显式化
              + 5 god function v3.0-split TODO 锚点
  - P1-8: 6 个零测试 stage 加 import + main-callable smoke test (+12 test)
  - P2-11/12/13/14: core/caching+quality 头部修正; thefuzz 评估 + requirements.lock;
                   ruff pyproject 接入 + F601/B023/F811/B033 修复; 13 处 swallow except 文档化
  - P3-15/16/17/18: Makefile cleanup; god function docstring; LLM cache key 升级;
                   26 thin shim v3.0 退役 plan
  - sidecar 化 (round 2 P1-5) baseline 跃迁: 782 -> 786 (+4 SKIP→PASS, Win 兼容性)
  - 本轮 baseline 跃迁: 786 -> 814 (P0-2 +2 + P1-4 +2 + P1-8 +12 + P3-17 +3 +
                                       recode +3 + final recode +2 + round-3 review +6)
  - 两轮 recode + 一轮 review 共发现 2 个真 bug + 7 个改进项:
      bug 1: P3-17 cache key .4f 格式化让 1e-30 与 0.0 碰撞 → 改用 repr() 修复
      bug 2: _make_key 让 model_id=None 与 '' 共用 namespace (接口契约违反)
             → 用 ASCII 哨兵 '<<NULL_SENTINEL>>' 区分修复 (round-3 R8 由 \\x00 改 ASCII)
      review R1: ci.yml light job 补装 rapidfuzz (与 pyproject 对齐)
      review R2: ci.yml full job 合并两次 pytest 为一次 (减半 CI 时长)
      review R3: caching.py 明示 prompt_version 为 'infrastructure ready, NOT YET wired'
      review R5: _validate_env_placeholders 加间接引用递归校验
      review R6: test_stage_smoke 加 conftest fixture 清理 logs/ 副作用
      review R7: Makefile purge-all 加 CONFIRM=yes 守门 (与 cleanup.py 一致)
      review R8: cache _NONE_SENTINEL 由 \\x00 改 ASCII (避 sqlite 跨版本边角)
      M1 (rapidfuzz/thefuzz parity) + M2×2 (env indirect ref) + R8 limitation +6 不变量
  - Full pytest: 814 passed / 2 skipped / 0 failed (recode-3 baseline).

后续 v3.0 / v3.1 / v3.2 / v3.3 版本基线见 CHANGELOG.md + CLAUDE.md.
本 docstring 仅保留 Phase 0-9 + recode 历史记录, 不再追加新版本节。
"""

__version__ = "3.8.0"
