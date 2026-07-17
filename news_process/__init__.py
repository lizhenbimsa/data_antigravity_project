"""news_process — 银行-金融科技新闻 → bank-year 面板的流水线包。

本文件使项目根成为真正的 Python 包, 任意 cwd 下均可
``import news_process.<sub>``。分层拓扑 (core / pipeline / papers /
papers_assets / validation / config split 等) 见仓库根 README.md;
逐 phase 的架构演进记录见 CHANGELOG.md。

v2.0.0 / phase-8-baseline (2026-05-04): 完整重构计划 (Phases 0 → 8)
完成。终态 (以下为当时的历史快照):
  - 26 个数字前缀根脚本: 全部为 ≤30 行 thin shim
  - news_process.{core, pipeline, papers, validation, scripts, config}:
    完整 canonical 布局, 单一声明式 DAG (core/dag.py)
  - 7 域 split config + 外部化 prompt
  - 多论文产品化 (papers/ + papers_assets/)
  - 数据布局规范化: data_processed/ → data/processed/ (Phase 8)
  - 全量 pytest: 778 passed / 7 skipped / 0 failed。

v2.1.0 / phase-9-baseline (2026-05-08): 重构后清理 Phase 3 / Phase 7a
残留, 不引入新抽象:
  - 9c: 移除 5 个失效的 audit/test 脚本 (Phase 7a 遗留)
  - 9d: 移除 orchestrator 的 OUTPUT_REGISTRY fallback 字典; 新增
    STAGES_MAIN ↔ OUTPUT_REGISTRY 一致性测试
  - 9a: 移除 5 个 papers/<id>/dag.py 空壳 (5×``STAGES = list(STAGES_MAIN)``);
    公共 API ``papers.<id>.dag`` 退役 (无外部消费方);
    STAGES 守卫转移至 analysis 模块
  - 9b: paper analysis.py 中 5 处反射式 import 块替换为 canonical-import
    桥 ``papers/_common/pipeline_runner.py``; 生产代码恢复 Phase 2a
    "禁反射" 不变式
  - 26 个 thin shim: 不动 (留待真正的 v3.0)
  - 全量 pytest: 772 passed / 6 skipped / 0 failed (v2.1.0 release tag 基线)。

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

import os as _os

# OpenMP 双运行时防御 (OMP Error #15).
# 本机环境叠了三层 site-packages: conda base 的 numpy/scipy/sklearn 走 MKL ->
# 加载 Intel OpenMP `Library/bin/libiomp5md.dll`; per-user site 的 pip torch
# 自带 `torch/lib/libiomp5md.dll`. 同一进程同时 import numpy(MKL) 与 torch 时
# 两份 libiomp5md.dll 各自初始化 -> "OMP: Error #15 ... already initialized" 中止.
# 该 env var 必须在 *第二份* OpenMP 运行时 (torch) 加载前生效; 本 __init__ 是所有
# 项目入口 (NN_*.py shim / `python -m news_process...` / pytest) 最先执行的项目代码,
# 远早于任何 pipeline 子模块 import torch, 故在此 set 必然及时.
# 用 setdefault: 不覆盖调用方/golden 重生 SOP 已显式导出的值. 这是本项目既定的
# canonical 解 (见各 audit runbook); 确定性由线程钉死=1 单独保证, 与本 flag 正交.
_os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

__version__ = "3.16.0"
