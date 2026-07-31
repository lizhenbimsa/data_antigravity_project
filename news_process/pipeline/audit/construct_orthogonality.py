"""news_process.pipeline.audit.construct_orthogonality — v3.5.0 D3 NMI 正交性测度.

Stage 39c: 在 article 层算 substantiveness × locus × collab_mode 三 construct 的
normalized mutual information (NMI) matrix + permutation null distribution,
作 paper Appendix A.2 "Construct Validity Evidence" 的实证证据.

学术锚点 (v3.5.0 D3):
    - Vinh, Epps & Bailey (2010 JMLR 11:2837-2854) NMI arithmetic averaging
    - Fred & Jain (2003 CVPR) NMI for clustering comparison
    - Bagozzi & Yi (1988 JAMS 16:74-94) discriminant validity in CFA

Dependency stability (修 F35):
    sklearn 1.5-1.8 已验证 `normalized_mutual_info_score(..., average_method='arithmetic')`.
    若升级到 sklearn 2.x 必须 (a) 跑全 14 单元测试; (b) 比对 v3.5.0 baseline parquet hash
    (允许 ≤ ±0.001 漂移 per H-NEW-1 LLM stochasticity); (c) breaking change 触发 epoch 7 audit.

Reproducibility lock (修 H-NEW-1):
    输入 = data/processed/21_tone_llms.parquet @ v3.4.0 commit hash 450c1aa7
    (per plan §0 Tag-over-hash anchor; 实际 anchor 由 v3.4.0-baseline-frozen git tag 决定).

Performance (2026-07-29 S11 **生产实测**, 取代此前的估算):
    ⚠ 本段旧文写「Total wall-time ≈ 77 min single-thread」+「n_jobs=16 → ~5 min」——
    **两句都是估算且都被证伪**, 而 DAG timeout=10800s 正是照那 77 min 设的, 导致
    2026-07-29 入口③ 阶段 72 被强杀、73/74/75 连坐跳过 (同一根因第 4 次: 15/23/40/72).
    真数据微基准 (N=169,811, 比旧文假设的 400k 还**小**):
        bootstrap  单次迭代 754 ms → 48 cell × 1000 = 10.05h
        permutation 单次迭代 774 ms → 48 cell × 1000 = 10.32h
        ⟹ 串行需求 **20.4h**, 约旧估算的 16 倍。
    S11 (上三角镜像 + 逐 cell 进程并行) 后生产单跑实测 **8,270s (2.30h)**:
        nmi_matrices 6,340s / permutation_null+classify 1,925s (10:59:25→13:17:15, EXIT=0)
    ⟹ 8.88× 提速。DAG timeout 现为 108,000s, 按**串行兜底路径** (20.4h) 定而非
    按 2.30h 定 —— OOM 触发 `_run_cells` 回落串行时仍须跑得完。

Concurrency (修 F7 + F43; 2026-07-29 S11 更新):
    SeedSequence.spawn **预分配** seeds ⟹ 结果与迭代顺序无关, 故并行是字节安全的
    (A/B 实测 54/54 格逐位相同)。现默认走 `prefer='processes'` 逐 cell 并行,
    工作量 (cells × n) 低于 `_NMI_PARALLEL_MIN_WORK` 时自动串行; 旁路 `NEWS_PROCESS_NMI_JOBS`.
    sklearn `normalized_mutual_info_score` 在 1.5-1.8 **基于源码 review 判断单调用线程安全**
    (无官方 claim, 谨慎说法) —— 走进程并行后该风险不再承重。
    ⚠ **两侧都不再镜像 (S12, 2026-07-31)**。permutation 从来不可镜像: (i,j) 打乱第 j 列、
    (j,i) 打乱第 i 列, 是两次不同的随机化 (真数据 0/5 逐位相同)。bootstrap 侧 S11 曾按
    "NMI 逐位对称" 镜像, 该前提已被真数据复测**证伪** —— 全 15 对 × 40 次重采样中
    6/600 非逐位对称 (全集中在 collab_mode_full × collab_mode_ctx 一对, max|Δ|=1.11e-16)。
    ⚠ 该 1 ulp 在矩阵级被分位数吸收 (撤销前后 A/B 0 格不同), 故撤销的定性是
    **前提证伪 + 稳健性加固**, 非修正错数; 代价由整数编码吸收, 端到端实测净快 9.2×。
    见 `test_nmi_parallel_mirror.py`。

Logging 约定 (修 F13):
    与 v3.4.0 main pipeline 一致, 通过 logger.info / logger.warning 输出.
    stage 内禁止 print() 直接输出; 诊断信号全部走 logger.

白话: 这个阶段检验我们造的三个创新测度 (实质性/落点/协同模式) 是不是
真的在测三件不同的事。NMI (归一化互信息) 衡量两个标签之间"互相能猜出
多少"; 如果两两 NMI 都低 (与随机打乱后的水平差不多), 说明三个测度各管
各的、没有重复计量, 论文附录就能放心声称"构念正交"。

========================================================================
【阶段功能权威说明 — 2026-06-15 三层核查定稿】
（对应 thin shim: 72_construct_orthogonality.py；摘自 scripts/audit/PIPELINE_NUMBERED_PY_REFERENCE_2026-06-15.md，
  经"文档生成→对抗逐行核对代码→跨文件终审"三层核对。）

■ 详细功能说明

**输入**: 读 `21_tone_llms.parquet`(文章级, 可经 STAGE_21_PARQUET 环境变量覆盖; 可复现锚点=v3.4.0 commit 450c1aa7, 见 docstring/summary.json)。用三个创新构念列的三轨版: substantiveness / locus / collab_mode 的 _full/_ctx/_ss。

**处理步骤**(`run_stage`):
- 用 `np.random.SeedSequence(seed=42)` 派生根序列, `.spawn(2)` 取 bootstrap 与 permutation 两个独立子种子状态(避免 seed+1 耦合; 实际 compute_nmi_matrix 内部又各自 SeedSequence.spawn(bootstrap_n) 派生整行 resample 种子)。
- `compute_nmi_matrix` 对 full/ctx/ss 各算 3×3、对 ALL_DIMS(=DIMS_FULL+DIMS_CTX, 6 维)算 6×6 cross: 默认 sample_strategy='listwise_complete'(全 dims 同时非缺整行剔除, 保证所有格子同样本可比); 对角线 NMI=1.0 直接填(跳 bootstrap); 非对角格用 sklearn `normalized_mutual_info_score(average_method='arithmetic')` 算点估计, 再对该 pair 的两列 [d1,d2] 做 1000 次有放回 row resample(SeedSequence.spawn 跨 numpy 版本可复现)取 2.5%/97.5% 为 CI; 守卫: 缺列→全 NaN 矩阵 + warning、样本<100 跳过、退化常量列(nunique<2)跳过并 logger.error、bootstrap 退化>5% warning。
- `compute_permutation_null` 对 ALL_DIMS(落盘 null_p95/p99)与(另单独对 DIMS_FULL 同域, 仅供分类)各算 1000 次置换: 打乱 d2 标签算 null NMI, 取 95%/99% 分位(默认 seed=43, run_stage 传 perm_seed_state)。
- `classify_orthogonality` 只对 full 3×3, 且与 DIMS_FULL 同 listwise 域的 null 比: obs≤null_p95→'strong'、≤p99→'moderate'、>p99→'weak'(关键修复 omni-g-audit-family-04: 观测 point_f 与 null 必须同 DIMS_FULL 3 列 listwise 域, 否则 NMI 有限样本偏差随 N 错配)。

**关键算法/公式**: Vinh-Epps-Bailey(2010 JMLR) 算术平均归一化互信息 NMI=MI(X,Y)/mean(H(X),H(Y)); 阈值口径=置换 null 的**单侧** 95%/99% 分位(≈单侧 Z 1.645/2.326, 非旧注释宣称的双侧 1.96/2.58, 旧未引用常量已删)。

**输出**: 上列 7 件; summary.json 含 max_off_diag_nmi、classify_full_3x3、interpretation(strong/moderate/mixed/undefined; 修复了 classify 全 undefined 时"空真"错报 strong 的 bug, CR-15)、classify_threshold_scale 口径披露、reproducibility 锚点。

**外部依赖/超时/性能**: 依赖 sklearn(1.5–1.8 已验证, lazy import); 无 LLM/Embedding/_llm_cache.db。docstring 估算 N≈40 万标签单线程约 77 分钟(bootstrap 1000 + permutation 1000), 故 DAG timeout=10800(3 小时上限); 64 核 MP 上 n_jobs=16 约 5 分钟(注: 当前实现为 single-thread 串行, n_jobs 并行为 docstring 给出的可选加速路径, 代码默认不并行)。

**DAG 位置**: 验证阶段 39c(STAGES_VALIDATION, 紧跟 39a/39 序列, 避开 40 panel_export), 上游=stage 21, 产物供论文 Appendix A.2 "Construct Validity Evidence"。

■ 白话说明

**这一步在做什么**: 我们造了三把"创新尺子"——一把量这家银行的创新是真干实事还是喊口号(实质性)、一把量是底层技术还是表面应用(落点)、一把量是自研还是合作(协同模式)。这一步像质检员检查"这三把尺子是不是真的在量三件不同的事, 还是其实有两把量的是同一个东西"。它用一个叫 NMI(归一化互信息)的指标衡量"知道一把尺子的读数, 能猜出另一把多少", 再把标签随机打乱一千遍看"纯属巧合时能有多像", 只有比巧合明显更像才算"真有重叠"。

**为什么需要它**: 顶刊审稿人会质疑"你这三个新指标会不会是换汤不换药、在重复计量同一件事"。这一步用统计证据回答: 如果三把尺子两两的关联都只跟随机打乱差不多(正交), 就能在论文附录理直气壮地写"三个构念各自独立、没有重复造轮子"。

**对最终面板/论文的影响**: 它不往银行-年度面板里加任何主回归用的列(产物只是诊断矩阵和一份小结), 但它直接决定论文"我们的三维创新测度是有效、可区分的构念"这一方法学主张能不能站住。做得好, 三个指标可以放心分别进各自的回归; 做得不好(发现高度重叠), 论文就得暂缓那部分构念效度声明、请专家复核。
========================================================================
"""
from __future__ import annotations

import json
import logging
import os
import platform
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from news_process.core.logging import pct4, sig4

logger = logging.getLogger(__name__)

DIMS_FULL = [
    'innovation_substantiveness_full',
    'innovation_locus_full',
    'innovation_collab_mode_full',
]
DIMS_CTX = [d.replace('_full', '_ctx') for d in DIMS_FULL]
# 第三轨 ss = 银行+金科同句共现轨 (content_ss / suffix _ss): 机械 _full→_ss swap
# (继承同三维度, 非新维度); ss 仅出 3×3 NMI 诊断, 不参与下文正交性分类 (见
# run_stage: 分类只对 full 3×3 做, ss 是 NMI-diagnostic only — 有意不对称)。
DIMS_SS = [d.replace('_full', '_ss') for d in DIMS_FULL]
ALL_DIMS = DIMS_FULL + DIMS_CTX

# 分类阈值口径 (fix(omni-g-audit-family-04, 2026-06-11)): 实现为 permutation null
# 分布的**单侧** 95% / 99% 分位 (≈ 单侧 Z 1.645 / 2.326), 而非旧注释宣称的
# "pre-registered 双侧 Z 1.96 / 2.58" — 旧 Z_STRONG/Z_MODERATE 常量从未被任何
# 代码引用, 预注册口径与执行口径不符, 已删除; 权威口径见 classify_orthogonality.


def _lazy_import_nmi():
    """把 sklearn import 推迟到函数作用域 (CI 轻量 job 只在阶段真跑时才加载)。"""
    from sklearn.metrics import normalized_mutual_info_score
    return normalized_mutual_info_score


# ════════════════════════════════════════════════════════════════════════════
# S11 (2026-07-29): NMI bootstrap / permutation 的进程并行 + 上三角镜像
# ════════════════════════════════════════════════════════════════════════════
# **为何**: 2026-07-29 入口③ 生产真跑, 本阶段 (72) **被 10,800s 超时闸强杀**, 后续
# 阶段 73/74/75 连坐跳过, 整个验证管道判 ✗。这是同一根因第 4 次复发 (stage 15 /
# 23 / 40 / 72): **超时按 T=2 dev 或估算定, 从未按生产规模复核**。
# 本模块 docstring 原写「N≈40 万标签单线程约 77 分钟, 故 timeout=10800」——
# 真数据实测证伪:
#     单次 bootstrap 迭代 754 ms  → 单 cell(1000 次) 12.6 分钟
#     单次 permutation 迭代 774 ms → 单 cell(1000 次) 12.9 分钟
#     48 个非对角 cell ⟹ bootstrap 10.05h + permutation 10.32h = **20.4 小时**
# (N=169,811 listwise 完整样本, 比 docstring 假设的 40 万还小, 却是估算的 ~16×。)
# 同 docstring 还写着「64 核 MP 上 n_jobs=16 约 5 分钟」—— 但**代码里根本没有并行**,
# 那只是一句从未兑现的说明。本次把它兑现。
#
# **两条独立的加速, 各有各的证据边界**:
#   ① ~~上三角镜像 (只对 bootstrap)~~ —— **S12 (2026-07-31) 已撤销, 见下**。
#   ② ⚠ **permutation 绝不可镜像**: (i,j) 打乱第 j 列而 (j,i) 打乱第 i 列, 是
#      **两次不同的随机化**。实测 0/5 逐位相同 (值差若干量级)。镜像它 = 静默改数。
#      故 permutation 只并行、不减半。
#
# ════════════════════════════════════════════════════════════════════════════
# S12 (2026-07-31): 整数编码 (真加速) + 撤销上三角镜像 (真修正)
# ════════════════════════════════════════════════════════════════════════════
# **① 撤销镜像 —— S11 的立论被真数据证伪**。
#   S11 写「点估计 3/3 对、bootstrap 重采样 3/3 对 ⟹ 严格 2×, 零数值改动」。
#   在真实 `21_tone_llms.parquet` 六维 listwise 样本 (N=156,102) 上把抽查扩到
#   **全 15 对 × 40 次真实 bootstrap 重采样** 后:
#       点估计   0/15  非对称  (确实逐位对称)
#       bootstrap 6/600 非对称 (1%), **全部集中在**
#                 innovation_collab_mode_full × innovation_collab_mode_ctx,
#                 该对 6/40 命中, max|Δ| = 1.11e-16 ≈ 1 ulp
#   机理: 交换两列 = 转置列联表, 而 `contingency_matrix` 按行主序装配 ⟹ 求和序变,
#   差 1 ulp 是正常浮点行为, 不是 bug —— **bug 是拿它当"零数值改动"的依据**。
#   ⚠ **不要把这条说过头** (撤销时自查后订正): 迭代级的 1 ulp 非对称**并未**在矩阵级
#   显形。同一真数据上把撤销前/后两版逐格对拆 (bootstrap_n=40):
#   point / ci_low / ci_high / n_pair **全部 0 格不同** —— 因为 CI 端点是 40 个值的
#   2.5%/97.5% 分位, 个别值动 1 ulp 通常选不出不同的次序统计量。
#   ⟹ 本条的性质是 **前提证伪 + 稳健性加固**, 不是 "修正了已发布的错数"。
#   仍然撤销的理由: ① 代码自带的审计依据是错的, 留着它下一个人会继续照信;
#   ② "分位数会吸收掉" 不是受控保证 —— 换数据 / 换 bootstrap_n (生产是 1,000)
#      是否仍吸收, 没有任何东西保证; ③ 代价已被 ② 的整数编码完全吸收 (见下),
#      真数据实测撤镜像+编码合起来仍净快 **9.2×**。
#   (教训与 F26/F41 同型: "抽查 3 个样本通过" 不等于 "逐位成立"。)
#
# **② 整数编码 —— 把撤销镜像的 2× 代价连本带利赚回来**。
#   NMI 只依赖列联表, 而列联表在**保序**重标号下不变。sklearn 内部每次调用都要在
#   原始标签上跑一遍 `np.unique`(含排序); 生产是 15.6 万行 object 列 × 每格 1,000 次,
#   这才是真瓶颈。把这一步提到列级做一次 (`_encode_codes`, 必须用 `np.unique` 的
#   排序序而非 `pd.factorize` 的出现序):
#       单次 NMI  902.3 ms → 49.9 ms   (真数据实测)
#       单次 resample 9.6 ms (不受影响)
#       每格 1,000 次: 912 s → 59.5 s  ⟹ **15.3×**
#   净账 (真数据端到端实测, 非推算): 同一 `compute_nmi_matrix(N=156,102, 6 维,
#   bootstrap_n=40)` 撤销前 685.2 s → 撤销后 74.5 s = **9.2×**, 已含格数 24→48 的
#   双倍代价。permutation 侧从不镜像, 拿到的是完整的单格倍数。
#   逐位等价实证 (同一真数据): 点估计 15/15 · bootstrap 100/100 · permutation
#   100/100 与原 object 路径 `struct.pack('<d')` 逐位相同, 且重采样下标序列与
#   置换排列亦逐一相同。
#
# **确定性**: bootstrap/permutation 的种子都由 `SeedSequence.spawn(N)` **预先派生**,
# 每次迭代 (以及每个 cell) 取的是同一份 `seeds[k]` ⟹ 迭代之间零耦合, 谁先谁后都
# 得同一个值。并行只改执行顺序, 不改任何数值。
#
# **护栏**: worker 体内零 logger 调用 (退化计数回传父端 emit); 结果按 (i,j) 回填,
# 与串行写入序无关; 工作量低于阈值时**逐字节走原串行路径**。
# ⚠ 阈值按 **cells × bootstrap_n** 而非 cell 数: 现存单测用的维度数与生产相同
#   (DIMS_FULL 3 维 / ALL_DIMS 6 维), 只把 bootstrap_n 调小到 20–100, 按 cell 数
#   设闸会让单测一起走进并行分支。

#: 走并行的**总工作量**下限 (非对角 cell 数 × bootstrap_n)。
#: ⚠ **按"单次调用"算, 不是按全阶段总和算** (2026-08-01 终审订正: 上一版写成
#: "48×1000=48,000" 是把四次调用的格数**总和**当成了单次的 min_work)。实测每次调用:
#:   bootstrap  3 维轨 6 格 ⟹ 6,000 (×3 轨) · 6 维 cross 30 格 ⟹ 30,000
#:   permutation 同样是 6 格/30 格 ⟹ 6,000 与 30,000
#: 全阶段格数总和 bootstrap 48 / permutation 36 (两者**不**同量)。
#: ⟹ 生产侧最小的一次是 **6,000**, 相对本闸值 5,000 只有 **1.2× 余量** (不是 9.6×);
#: 单测侧最大 30×30=900。调高本闸值前必须复算这 1.2×, 否则会把生产的三条 3 维轨
#: 静默推回串行。
_NMI_PARALLEL_MIN_WORK = 5000
#: worker 上限 (与本仓其它并行点同档; 每 worker 各持一份两列样本, 内存轻)。
_NMI_MAX_WORKERS = 12
#: 运维旁路: 不改代码即可下调并行度 (本阶段单跑以小时计, 出事重跑代价高)。
_NMI_JOBS_ENV = 'NEWS_PROCESS_NMI_JOBS'


def _nmi_workers(n_tasks: int) -> int:
    """并行度 = min(硬上限, 可用核-2, 任务数); env 可覆盖; 至少 1。"""
    raw = os.environ.get(_NMI_JOBS_ENV, '').strip()
    if raw:
        try:
            v = int(raw)
            if v >= 1:
                return min(v, n_tasks)
        except ValueError:
            pass
    n_cpu = os.cpu_count() or 1
    return max(1, min(_NMI_MAX_WORKERS, n_cpu - 2, n_tasks))


def _encode_codes(frame: pd.DataFrame) -> pd.DataFrame:
    """把标签列整体换成 **int 码** (0..k-1, 按 ``np.unique`` 的排序序)。

    S12 (2026-07-31): NMI 只依赖列联表 (contingency table), 而列联表在**保序**重标号
    下完全不变 —— sklearn 内部本就用 ``np.unique(..., return_inverse=True)`` 把标签
    压成码, 我们只是把这一步从"每次调用都做一遍"提到"整列做一次"。生产 bootstrap
    对每个 cell 调 1,000 次 NMI, 每次都在 15.6 万行 object 列上重跑一次 unique+排序,
    这是本阶段的真瓶颈。

    ⚠ **必须用 ``np.unique`` 而不是 ``pd.factorize``**: 前者按**排序序**赋码, 与
    sklearn 内部完全同序 ⟹ 列联表逐格同位置 ⟹ 浮点求和序不变 ⟹ 逐位等价;
    后者按**出现序**赋码, 列联表行列会被置换, 求和序随之改变 —— 本数据上二者恰好
    重合 (实测 elementwise 全等), 但那是数据巧合, 不可依赖。

    实证 (真实 `21_tone_llms.parquet` 六维 listwise 样本 N=156,102):
    点估计 15/15 · bootstrap 100/100 · permutation 100/100 逐位相同
    (``struct.pack('<d')`` 比较), 且三者的重采样/置换下标序列亦逐一相同。
    """
    return pd.DataFrame(
        {c: np.unique(frame[c].to_numpy(), return_inverse=True)[1]
         for c in frame.columns},
        index=frame.index,
    )


def _run_cells(tasks, worker, *extra, min_work: int, n_jobs: int | None = None,
               label: str = 'cells'):
    """串/并自适应执行, 结果**按提交序**返回 (joblib 语义)。

    与 ``strategic_diff._run_year_tasks`` 同型 (含 OOM 兜底整批回落串行), 但本模块
    不 import 那边 —— audit 层不应反向依赖 features 层。

    S12 (2026-07-31) 补一行**选臂披露**: 原实现静默二选一, 日志里看不出这一批究竟
    走了串行还是并行, 于是 "阈值是否卡在了不该卡的地方" 无从事后判断 (两个调用点
    共用 `_NMI_PARALLEL_MIN_WORK` 一个常量, 而 bootstrap 的单位工作量比 permutation
    重得多)。这一行让口径可核: 生产侧每次调用的 min_work 是 6,000 (3 维轨) 或
    30,000 (6 维 cross), 都应显示 parallel; 单测 (≤900) 都应显示 serial。
    ⚠ 最小的一次只有 6,000, 距闸值 5,000 仅 1.2× —— 这条披露行正是为了让这个薄余量
    在日志里看得见 (上一版注释误记为 48,000/9.6×, 2026-08-01 订正)。
    """
    _serial_reason = None
    if min_work < _NMI_PARALLEL_MIN_WORK:
        _serial_reason = f'min_work {min_work:,d} < {_NMI_PARALLEL_MIN_WORK:,d}'
    elif len(tasks) < 2:
        _serial_reason = f'tasks {len(tasks)} < 2'
    if _serial_reason is not None:
        logger.info(f"  {label}: 串行臂 ({_serial_reason}), tasks={len(tasks):,d}")
        return [worker(t, *extra) for t in tasks]
    n = _nmi_workers(len(tasks)) if n_jobs is None else max(1, int(n_jobs))
    if n <= 1:
        logger.info(f"  {label}: 串行臂 (并行度解析为 {n}), tasks={len(tasks):,d}")
        return [worker(t, *extra) for t in tasks]
    logger.info(
        f"  {label}: 并行臂 n_jobs={n}, tasks={len(tasks):,d}, "
        f"min_work={min_work:,d} (闸值 {_NMI_PARALLEL_MIN_WORK:,d})")
    from joblib import Parallel, delayed
    try:
        return Parallel(n_jobs=n, prefer='processes')(
            delayed(worker)(t, *extra) for t in tasks)
    except Exception as exc:  # noqa: BLE001 — 含 TerminatedWorkerError (OOM/被杀)
        logger.error(
            f"🔴 NMI 并行执行失败 ({type(exc).__name__}: {str(exc)[:150]}) — "
            f"worker={getattr(worker, '__name__', worker)} tasks={len(tasks)} "
            f"n_jobs={n}; **整批回落串行重跑** (慢 ~{n}× 但不丢 run)。"
            f"若反复出现请用 {_NMI_JOBS_ENV} 调低并行度。")
        return [worker(t, *extra) for t in tasks]


def _boot_cell_worker(task, bootstrap_n, boot_seeds):
    """单个 (i,j) cell 的 1000 次 bootstrap —— 原内层循环**逐字节照搬**。

    ⚠ 体内零 logger: 退化计数回传父端 emit (worker 会被父进程直接调用于串行回落路径,
    在里面动 logger 会掐掉整个阶段的日志)。
    """
    i, j, d1, d2, clean_pair = task
    nmi_score = _lazy_import_nmi()
    boot = np.full(bootstrap_n, np.nan)
    n_degenerate = 0
    for k, s in enumerate(boot_seeds):
        state = int(s.generate_state(1)[0])
        clean_boot = clean_pair.sample(frac=1, replace=True, random_state=state)
        # 防 bootstrap resample 后 degenerate (极不平衡 label 时常见)
        if clean_boot[d1].nunique() < 2 or clean_boot[d2].nunique() < 2:
            n_degenerate += 1
            continue  # leave boot[k] as NaN
        boot[k] = nmi_score(clean_boot[d1], clean_boot[d2],
                            average_method='arithmetic')
    return i, j, boot, n_degenerate


def _perm_cell_worker(task, n_permutations, perm_seeds):
    """单个 (i,j) cell 的 1000 次 permutation —— 原内层循环逐字节照搬。零 logger。"""
    i, j, d1_series, d2_vals = task
    nmi_score = _lazy_import_nmi()
    null = np.empty(n_permutations)
    for k, s in enumerate(perm_seeds):
        rng = np.random.default_rng(s)
        d2_perm = rng.permutation(d2_vals)
        null[k] = nmi_score(d1_series, d2_perm, average_method='arithmetic')
    return i, j, null


def compute_nmi_matrix(
    df: pd.DataFrame,
    dims: list[str],
    sample_strategy: str = 'listwise_complete',
    bootstrap_n: int = 1000,
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """计算 NMI 矩阵 + bootstrap 95% CI + 每对样本数。

    Returns:
        (nmi_point, ci_low, ci_high, n_pair_matrix) — 4 个 DataFrame 均以 dims 为行列索引。

    sample_strategy:
        'listwise_complete' — 全 dims 同时非脏的 row (修 C-NEW-1; 矩阵推荐口径)
        'pairwise_complete' — 每 (d1, d2) 各自 dropna (legacy, sample size 不可比)

    Bootstrap 实现 (修 C1 + H-NEW-2):
        - 在 sampled DataFrame 上整体 resample (两列同步 row, 修 C1)
        - 用 NumPy 2.x SeedSequence.spawn 替代 rng.integers (跨 NumPy 版本 reproducible, 修 H-NEW-2)

    退化维度对 (修 F40):
        若 d1 或 d2 在 clean sample 上 nunique() < 2 (constant), 跳过该 pair 并 logger.error;
        n_pair[i, j] = 0; 写入 audit log §A.degenerate_dim_pair.

    白话: listwise = 只要任一维度缺值就整行丢掉, 保证所有格子用同一批
    样本、相互可比; pairwise = 每对维度各丢各的缺值, 样本量不一致,
    仅作历史兼容保留。
    """
    nmi_score = _lazy_import_nmi()

    n = len(dims)
    point = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_low = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    ci_high = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    n_pair = pd.DataFrame(np.zeros((n, n), dtype=int), index=dims, columns=dims)

    # F-56: Missing column guard (对称 encode_collab.compute_cell_id 防御).
    # Production stage 21 pre-v3.4.0 缺 collab_mode 列 → 之前直接 raise KeyError.
    # 现在 graceful: 缺列 → 返回全 NaN matrix + logger.warning, 让调用方判断.
    missing_cols = [d for d in dims if d not in df.columns]
    if missing_cols:
        logger.warning(
            f"  v3.5.0 D3 NMI: missing dim columns {missing_cols}; "
            f"returning all-NaN matrix. "
            "Production stage 21 may pre-date v3.4.0 (lacks innovation_collab_mode_*). "
            "解决方案: 重跑 stage 21 with prompt v8 (含 collab_mode 维度)."
        )
        return point, ci_low, ci_high, n_pair

    if sample_strategy == 'listwise_complete':
        clean_base = df[dims].dropna()
    elif sample_strategy == 'pairwise_complete':
        clean_base = None
    else:
        raise ValueError(f"Unknown sample_strategy: {sample_strategy}")

    seed_sequence = np.random.SeedSequence(seed)
    boot_seeds = seed_sequence.spawn(bootstrap_n)

    # S12 (2026-07-31): 标签 → int 码 (排序序), 逐位等价, 见 `_encode_codes`。
    # listwise 口径整表编码一次; pairwise 口径在循环内逐对编码 (各对样本域不同)。
    if clean_base is not None:
        clean_base = _encode_codes(clean_base)

    #: S12 起: **全部非对角格**的 bootstrap 任务 (不再只装上三角), 对角线不进池。
    _boot_tasks: list[tuple] = []

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if sample_strategy == 'pairwise_complete':
                # d1==d2 时去重列名, 避免重名列
                # (DataFrame[[d1,d1]] 会返回 DataFrame 切片而非 Series)。
                cols = [d1] if d1 == d2 else [d1, d2]
                clean = _encode_codes(df[cols].dropna())
            else:
                clean = clean_base

            if len(clean) < 100:
                continue

            # F40: 退化 (常量列) 守卫
            if clean[d1].nunique() < 2 or clean[d2].nunique() < 2:
                logger.error(
                    f"  v3.5.0 D3 degenerate dim-pair: ({d1}, {d2}) nunique < 2; "
                    "skipped per F40 (NMI undefined for constant cols)"
                )
                continue

            n_pair.iloc[i, j] = len(clean)

            # CR-9: 对角线 NMI(X,X) = 1.0 by definition (H(X,X)/H(X) = 1);
            # 跳过 bootstrap (省 ~1000 NMI calls 每个对角线; cross 6×6 节省 6×1000 calls)
            if d1 == d2:
                point.iloc[i, j] = 1.0
                ci_low.iloc[i, j] = 1.0
                ci_high.iloc[i, j] = 1.0
                continue

            # ── S11 的下三角镜像已于 S12 (2026-07-31) **撤销**, 此处不再跳过 j<i ──
            # S11 把 48 格砍到 24 格, 立论是「NMI 数学对称, 且真数据实测**逐位对称**
            # (点估计 3/3 + bootstrap 重采样 3/3) ⟹ 严格 2×, 零数值改动」。
            # 数学对称无疑; **逐位**对称被证伪 —— 交换两列会转置列联表 (sklearn 的
            # `contingency_matrix` 按行主序装配), 求和序随之改变, 差一个 ulp 是正常的
            # 浮点行为, 原依据只是 3 个样本的抽查, 抽中了对称的那些。
            # 真数据复测 (`21_tone_llms.parquet` 六维 listwise N=156,102, 全 15 对
            # × 40 次真实 bootstrap 重采样, `struct.pack('<d')` 比较):
            #   · 点估计   0/15  非对称 (确实逐位对称)
            #   · bootstrap 6/600 非对称, **全部集中在**
            #     (innovation_collab_mode_full, innovation_collab_mode_ctx) 这一对,
            #     该对 6/40 命中, max|Δ| = 1.11e-16 (≈1 ulp)。
            # ⟹ S11 "零数值改动" 的依据不成立。⚠ 但也别说过头: 撤销前/后两版在同一
            # 真数据上逐格对拆 (bootstrap_n=40), point/ci_low/ci_high/n_pair **0 格不同**
            # —— 1 ulp 被分位数步骤吸收了。故本条是**前提证伪 + 稳健性加固**, 不是
            # "修正已发布的错数"。撤销的理由是"分位数会吸收"不是受控保证 (生产
            # bootstrap_n=1,000, 数据也不同), 而代价已被整数编码吸收: 端到端实测
            # 685.2 s → 74.5 s = 9.2×。
            # ⚠ 上面所有守卫 (len<100 / F40 退化 / n_pair 填写 / 对角线) 本就对**全部**
            #   (i,j) 逐格执行, 故 n_pair 矩阵与 F40 的 logger.error 条数不受本改动影响。

            point.iloc[i, j] = nmi_score(
                clean[d1], clean[d2], average_method='arithmetic'
            )

            # CR-10: bootstrap 只对 [d1, d2] 两列 resample (省 listwise 共享 base
            # 的 6-列 memory; 对 N=400k × 6 cols × 1000 boot × 36 cells, 减 ~70% peak)
            _boot_tasks.append((i, j, d1, d2, clean[[d1, d2]]))

    # ── Bootstrap CI: 逐 cell 进程并行 (修 C1 整体 row-pair resample 语义不变) ──
    # CR-11: degenerate fallback 改 NaN + 用 nanpercentile + count
    # ⚠ 唯一的行为差异是**日志时序**: 退化告警原本与循环交错, 现统一在本段按提交序
    #   回放 (内容与条数不变)。数值与写入位置均由 (i,j) 决定, 与执行顺序无关。
    for _i, _j, boot, n_degenerate in _run_cells(
            _boot_tasks, _boot_cell_worker, bootstrap_n, boot_seeds,
            min_work=len(_boot_tasks) * bootstrap_n,
            label=f'bootstrap-CI ({bootstrap_n:,d} 次/格, 全非对角格)'):
        _d1, _d2 = dims[_i], dims[_j]
        # 记录 degenerate 比例 (审稿人 sanity check); >5% 触发 warning
        if n_degenerate > 0:
            degen_frac = n_degenerate / bootstrap_n
            if degen_frac > 0.05:
                logger.warning(
                    f"  v3.5.0 D3 bootstrap ({_d1}, {_d2}): "
                    f"{n_degenerate:,d}/{bootstrap_n:,d} = {pct4(degen_frac)} resamples degenerate; "
                    "CI computed via nanpercentile"
                )
        # nanpercentile 自动跳过 NaN; 若 boot 全 NaN, 留 ci 为 NaN
        valid_boot = boot[~np.isnan(boot)]
        if len(valid_boot) > 0:
            ci_low.iloc[_i, _j] = float(np.percentile(valid_boot, 2.5))
            ci_high.iloc[_i, _j] = float(np.percentile(valid_boot, 97.5))

    # ── S11 的下三角镜像回填已随 S12 撤销 (理由见上方主循环内的长注释) ──
    # 现在 point / ci_low / ci_high 的每一个非对角格都由它自己的 (i,j) 任务算出,
    # 不存在"用 (i,j) 去盖 (j,i)"这回事。

    return point, ci_low, ci_high, n_pair


def compute_permutation_null(
    df: pd.DataFrame,
    dims: list[str],
    n_permutations: int = 1000,
    seed: int = 43,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """基于置换 (permutation) 的 NMI 阈值 null 分布 (修 C3)。

    Returns (null_p95, null_p99) — 每对 (d1, d2) 的 null 分布 NMI 95% / 99%
    分位矩阵。作为预注册阈值参照, 替代拍脑袋的 0.15 / 0.30 固定阈值。

    只填非对角格 (i != j); 对角线为 NaN。

    白话: 把其中一列标签随机打乱一千次, 看"纯属巧合"时 NMI 能有多大,
    取其 95%/99% 分位当门槛 — 观测值只有超过这个门槛才算"真有关联",
    比直接定一个固定数字更有说服力。
    """
    # S11: 实际的 nmi 调用已下沉到 `_perm_cell_worker` (worker 侧各自 lazy import,
    # 子进程无法继承父进程的局部绑定)。此处仍显式触发一次 lazy import: 若 sklearn
    # 缺失/版本不符, 让它在**父进程**当场炸掉, 而不是等 12 个 worker 各炸一遍。
    _lazy_import_nmi()
    n = len(dims)
    null_p95 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)
    null_p99 = pd.DataFrame(np.full((n, n), np.nan), index=dims, columns=dims)

    # F-56: Missing column guard (对称 compute_nmi_matrix 防御).
    missing_cols = [d for d in dims if d not in df.columns]
    if missing_cols:
        logger.warning(
            f"  v3.5.0 D3 permutation null: missing dim columns {missing_cols}; "
            f"returning all-NaN matrices."
        )
        return null_p95, null_p99

    clean = df[dims].dropna()

    if len(clean) < 100:
        logger.warning(
            f"  v3.5.0 D3 permutation: clean sample {len(clean)} < 100, returning all-NaN"
        )
        return null_p95, null_p99

    seed_sequence = np.random.SeedSequence(seed)
    perm_seeds = seed_sequence.spawn(n_permutations)

    # S12 (2026-07-31): 同 `compute_nmi_matrix`, 标签整表换 int 码 (逐位等价, 见
    # `_encode_codes`)。⚠ 顺序要紧: 编码必须在 `len(clean) < 100` 守卫**之后**、
    # 建任务池**之前** —— 放守卫之前会让 `len()` 判据看一个新建对象, 徒增拷贝;
    # 放任务池之后则 worker 拿到的仍是 object 列, 白改。
    # ⚠ 置换是对 `clean[d2].values` 打乱, int 码与原标签**同下标序** ⟹
    #   `rng.permutation` 产生的排列一致 (真数据实测 100/100 排列逐一相同)。
    clean = _encode_codes(clean)

    # S11 (2026-07-29): 逐 cell 进程并行。
    # ⚠ **绝不镜像**: (i,j) 打乱第 j 列而 (j,i) 打乱第 i 列 —— 是两次**不同的随机化**,
    #   真数据实测 0/5 逐位相同 (值相差若干量级)。镜像它等于静默改数, 故这里
    #   **全部 48 个非对角格逐一计算**, 只把它们并行起来。
    #   (S11 时期 bootstrap 那半边曾镜像, 依据是 "NMI 实测逐位对称"; 该依据已被
    #    S12 的真数据复测证伪 6/600, bootstrap 侧现在也逐格全算 —— 两侧口径已统一。)
    _perm_tasks: list[tuple] = []
    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if i == j:
                continue
            if clean[d1].nunique() < 2 or clean[d2].nunique() < 2:
                continue
            _perm_tasks.append((i, j, clean[d1], clean[d2].values))

    for _i, _j, null in _run_cells(
            _perm_tasks, _perm_cell_worker, n_permutations, perm_seeds,
            min_work=len(_perm_tasks) * n_permutations,
            label=f'permutation-null ({n_permutations:,d} 次/格)'):
        null_p95.iloc[_i, _j] = float(np.percentile(null, 95))
        null_p99.iloc[_i, _j] = float(np.percentile(null, 99))

    return null_p95, null_p99


def classify_orthogonality(point: pd.DataFrame, null_p95: pd.DataFrame,
                           null_p99: pd.DataFrame) -> dict:
    """Permutation-null 单侧分位三档分类 (per plan §2.2.6).

    口径声明 (fix(omni-g-audit-family-04, 2026-06-11)): 阈值 = permutation null
    的单侧 95% / 99% 分位 (≈ 单侧 Z 1.645 / 2.326), 非双侧 Z 1.96 / 2.58.
    调用方必须保证 ``point`` 与 ``null_p95``/``null_p99`` 来自**同一 listwise
    样本域** (NMI 有限样本偏差随 N 变化, 域错配会使阈值失准).

    Returns dict per off-diagonal (d1, d2) pair:
        'strong'   if observed_NMI ≤ null_p95
        'moderate' if null_p95 < obs ≤ null_p99
        'weak'     if obs > null_p99 (triggers paper Appendix A.2 暂缓 per §2.2.6 R2)
    """
    result = {}
    for d1 in point.index:
        for d2 in point.columns:
            if d1 == d2:
                continue
            obs = point.loc[d1, d2]
            p95 = null_p95.loc[d1, d2]
            p99 = null_p99.loc[d1, d2]
            if pd.isna(obs) or pd.isna(p95) or pd.isna(p99):
                result[f'{d1}__{d2}'] = 'undefined'
                continue
            if obs <= p95:
                result[f'{d1}__{d2}'] = 'strong'
            elif obs <= p99:
                result[f'{d1}__{d2}'] = 'moderate'
            else:
                result[f'{d1}__{d2}'] = 'weak'
    return result


def run_stage(
    stage_21_parquet: Optional[str] = None,
    out_dir: Optional[str] = None,
    bootstrap_n: int = 1000,
    n_permutations: int = 1000,
    seed: int = 42,
) -> dict:
    """Stage 39c 入口: 读 stage 21 parquet, 算 NMI 矩阵 + null 分布, 写出产物。

    产物 (per plan §2.2.3 + 第三轨 ss 三轨化):
        72_nmi_matrix_full.parquet   — full 3×3 NMI + CI + n_pair (multi-frame parquet)
        72_nmi_matrix_ctx.parquet    — ctx  3×3 同
        72_nmi_matrix_ss.parquet     — ss   3×3 同 (银行+金科同句共现轨 NMI 诊断)
        72_nmi_matrix_cross.parquet  — 6×6 full ∪ ctx cross-matrix
        72_nmi_null_p95.parquet      — Permutation null 95% percentile reference
        72_nmi_null_p99.parquet      — 99% percentile
        72_nmi_summary.json          — {max_off_diag, classify_per_pair, interpretation}

    有意不对称 (plan §7.3-A3): 正交性分类 (classify_orthogonality) 只对 full
    3×3 做 — substantiveness/locus/collab 这些是 full/ctx 锚定的 LLM 分类构念;
    ss 是纯情感共现轨, 这里只产出它的 3×3 NMI 矩阵作诊断, 不进分类/解读。

    Reproducibility: 输入 parquet anchored to v3.4.0 commit 450c1aa7 (per plan §0 Tag-over-hash).
    """
    # 接入项目统一日志: 写 <log_dir>/72_construct_orthogonality.log。
    # 此前本阶段仅 getLogger(__name__) 而无 FileHandler, 故虽能产出 parquet/json,
    # 却不像 39a/39e 等同族 audit 阶段那样落 <stage>.log (logger.info 被 root 默认
    # 级别静默丢弃)。现对齐 setup_logging 约定 (见模块 docstring「Logging 约定 修 F13」)。
    global logger
    from news_process.core.config import load_config
    from news_process.core.logging import setup_logging
    config = load_config()
    logger = setup_logging(
        "72_construct_orthogonality",
        config["paths"].get("log_dir", "logs"),
    )

    # 功能说明 banner — 写入 <stage>.log, 让日志自带阶段用途说明 (仿 39e)。
    logger.info("=" * 72)
    logger.info("阶段 72: 创新构念正交性检验 (NMI + permutation null; v3.5.0 D3)")
    logger.info("=" * 72)
    logger.info("【功能】检验 substantiveness / locus / collab_mode 三个创新构念是否各自独立、")
    logger.info("        无重复计量 (论文 Appendix A.2 构念效度证据)。")
    logger.info("【方法】每对构念算 NMI (归一化互信息); 随机打乱标签 1000 次得 null 分布,")
    logger.info("        取单侧 p95/p99 为门槛; bootstrap 1000 次给 CI。NMI 越低越正交。")
    logger.info("【判读】obs≤p95→strong(充分正交,好); ≤p99→moderate; >p99→weak(超出随机的真重叠,不利)。")

    # ① 🧭 项目 / 环境信息 (日志富集, 2026-06-24; 失败不阻断阶段)
    try:
        logger.info("-" * 72)
        logger.info("① 🧭 项目 / 环境信息")
        logger.info(
            "     · 阶段 72 construct_orthogonality (验证支线; thin shim 72_construct_orthogonality.py)"
        )
        logger.info(
            "     · 项目:     news_process 研究数据流水线 (中文银行/金科新闻 → 计量面板) v3.16.0"
        )
        logger.info(f"     · 模块:     {os.path.abspath(__file__)}")
        logger.info(f"     · 工作目录: {os.getcwd()}")
        logger.info(f"     · Python:   {sys.version.split()[0]} @ {sys.executable}")
        logger.info(f"     · 平台:     {platform.platform()} | CPU 逻辑核={os.cpu_count()}")
        _run_id = os.environ.get('NEWS_PROCESS_RUN_ID')
        logger.info(
            f"     · PID={os.getpid()} | RUN_ID={_run_id or '(未设置)'} | "
            "纯 CPU / 无 LLM·嵌入·_llm_cache.db / 无网络 ($0)"
        )
        logger.info(
            "     · 确定性: SeedSequence(seed) 派生 bootstrap/permutation 子种子, "
            "跨 NumPy 版本可复现; sklearn NMI lazy import"
        )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"  (ENV banner 跳过: {_e})")

    # ④ 📖 方法论依据 (参考文献信息) — emit 进日志, 非仅留注释。
    # 注: 本模块核心锚点 (Vinh-Epps-Bailey 2010 JMLR / Fred-Jain 2003 CVPR /
    # Bagozzi-Yi 1988 JAMS) 不在经核验注册表内, 故按 docstring 既有作者-年-刊面
    # prose 形式诚实 emit, 不附 (未经核验的) DOI 链接 (铁律: 参考文献零伪造)。
    try:
        logger.info("-" * 72)
        logger.info("④ 📖 方法论依据 (构念正交性 / 判别效度)")
        logger.info(
            "     · NMI 算术平均归一化: Vinh, N. X., Epps, J., & Bailey, J. (2010). "
            "Information theoretic measures for clusterings comparison. Journal of Machine "
            "Learning Research, 11, 2837-2854. (JMLR 开放获取无 DOI; https://www.jmlr.org/papers/v11/vinh10a.html)"
        )
        logger.info(
            "     · NMI 用于聚类/标签比较: Fred, A. L. N., & Jain, A. K. (2003). Robust data "
            "clustering. Proceedings of the 2003 IEEE Computer Society Conference on Computer "
            "Vision and Pattern Recognition (CVPR), II-128–II-133. https://doi.org/10.1109/CVPR.2003.1211462"
        )
        logger.info(
            "     · 判别效度 (discriminant validity, CFA): Bagozzi, R. P., & Yi, Y. (1988). "
            "On the evaluation of structural equation models. Journal of the Academy of Marketing "
            "Science, 16(1), 74-94. https://doi.org/10.1007/BF02723327"
        )
        logger.info(
            "     · NMI 有偏须 chance 校正: Mahmoudi, A., & Jemielniak, D. (2024). Proof of biased "
            "behavior of Normalized Mutual Information. Scientific Reports, 14(1), Article 9021. "
            "https://doi.org/10.1038/s41598-024-59073-9"
        )
        logger.info(
            "       (白话: 形式证明 NMI 偏好更多簇/更细标签, 故本阶段不用 NMI 绝对值定阈, "
            "而以同域 permutation null 分位作 chance 校正基准 — 正对应此偏差告诫。)"
        )
        logger.info(
            "     · 判别效度报告准则 (现代更新): Rönkkö, M., & Cho, E. (2022). An updated guideline "
            "for assessing discriminant validity. Organizational Research Methods, 25(1), 6-14. "
            "https://doi.org/10.1177/1094428120968614"
        )
        logger.info(
            "       (白话: 判别效度 battery 的现代报告标准, 锚定本阶段'三构念各自独立'声明须有的证据规格。)"
        )
        logger.info(
            "     · 白话: 用 NMI 衡量两把'创新尺子'读数互相能猜多少, 再与置换 null 比, "
            "证明三个构念各自独立、无重复计量 (论文 Appendix A.2 构念效度证据)。"
        )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (METHOD banner 跳过: {_e})")

    # fix(2026-06-19 run-check F2): 默认路径改用 load_config 解析的 output_dir (绝对,
    # CWD 无关), 镜像兄弟阶段 39d/39e; 此前相对 'data/processed/...' 仅当 CWD==news_process/
    # 才有效, 经 run_pipeline_validation.py 子进程 (无 cwd=) 从仓库根启动时 FileNotFound。
    # env 覆盖 (STAGE_21_PARQUET/OUT_DIR) 保留; 输入文件名仍为 canonical 21_tone_llms.parquet。
    _output_dir = config['paths']['output_dir']
    if stage_21_parquet is None:
        # fix(stage21-read-config-wiring, 2026-06-25): 默认输入名经 config 单一真值解析
        # (output_21_tone_llms; 键存在值=默认 → golden-safe), 替代硬编码字面量
        # (env STAGE_21_PARQUET 覆盖仍优先)。
        _s21 = config['filenames'].get('output_21_tone_llms', '21_tone_llms.parquet')
        stage_21_parquet = os.environ.get(
            'STAGE_21_PARQUET',
            os.path.join(_output_dir, _s21),
        )
    if out_dir is None:
        out_dir = os.environ.get('OUT_DIR', _output_dir)

    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # ②📂 输入/输出 + ③⚙ 运行配置 (日志富集, 2026-06-24)
    try:
        logger.info("-" * 72)
        logger.info("②📂 输入 / 输出 文件")
        logger.info(f"     · 输入:   {stage_21_parquet} (canonical 21_tone_llms.parquet)")
        logger.info(f"     · 输出目录: {out_path}")
        logger.info(
            "     · 产物:   72_nmi_matrix_{full,ctx,ss,cross}.parquet + "
            "72_nmi_null_p95/p99.parquet + 72_nmi_summary.json"
        )
        logger.info("③⚙ 运行配置 (可调参数)")
        logger.info(
            f"     · bootstrap_n={bootstrap_n:,d} | n_permutations={n_permutations:,d} | "
            f"seed={seed:,d} | sample_strategy='listwise_complete'"
        )
        logger.info(
            "     · 维度轨: full=" + ",".join(d.replace('innovation_', '') for d in DIMS_FULL)
            + " | ctx/ss 同三维 | cross=ALL_DIMS 6 维 (full∪ctx)"
        )
        logger.info(
            "     · 分类阈值: permutation null 单侧 p95/p99 (≈单侧 Z "
            f"{sig4(1.645)}/{sig4(2.326)}); 观测与 null 同 DIMS_FULL listwise 域"
        )
        logger.info("     · config 来源: paths.yaml::{output_dir,log_dir}; env 覆盖 STAGE_21_PARQUET/OUT_DIR")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (CONFIG banner 跳过: {_e})")

    # ⑥ ⏱ per-phase 墙钟计时锚点
    _phase_t: dict[str, float] = {}
    _t0 = time.time()

    logger.info(f"v3.5.0 D3 stage 72 reading: {stage_21_parquet}")
    df = pd.read_parquet(stage_21_parquet)
    logger.info(f"  loaded {len(df):,} article rows")
    # ②📂 IO 溯源富集 (2026-06-29 Round-8): 列数 (schema 宽度) + 9 个构念维列逐列非空覆盖。
    # 这些覆盖篇数直接决定下游 listwise-complete 样本 (每个 NMI 格子的可比样本量), 故是
    # 真·输入溯源记录 — 尤其暴露 ss 轨 (银行+金科同句) 在未物化时的零覆盖, 让审稿人一眼
    # 看出每条正交性结论背后的有效样本来源。compute-and-discard, 仅喂 logger, 不回流下游。
    try:
        logger.info(f"  · 列数 (schema 宽度) = {df.shape[1]:,d} 列")
        logger.info("  · 构念维列逐列覆盖 (非空篇数 / 全样本 = 占比; 驱动 listwise 完整样本):")
        for _d in DIMS_FULL + DIMS_CTX + DIMS_SS:
            if _d in df.columns:
                _nn = int(df[_d].notna().sum())
                _cov = _nn / len(df) if len(df) else float('nan')
                logger.info(
                    f"      {_d:<38} 非空 {_nn:>7,d} / {len(df):>7,d} = {pct4(_cov)}"
                )
            else:
                logger.info(
                    f"      {_d:<38} (列未物化 → coverage=0; ss 轨未跑或 stage21 早于 v3.4.0)"
                )
    except Exception as _e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"  (IO-provenance 覆盖块跳过: {_e})")
    _phase_t['load_parquet'] = time.time() - _t0

    # CR-13: SeedSequence.spawn(2) 派生 2 个独立子序列, 避免 `seed + 1` 的耦合
    root_seq = np.random.SeedSequence(seed)
    boot_seed_state, perm_seed_state = (int(s.generate_state(1)[0])
                                        for s in root_seq.spawn(2))

    _t1 = time.time()
    # full 3x3
    point_f, lo_f, hi_f, n_f = compute_nmi_matrix(
        df, DIMS_FULL, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # ctx 3x3
    point_c, lo_c, hi_c, n_c = compute_nmi_matrix(
        df, DIMS_CTX, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # ss 3x3 (银行+金科同句共现轨; NMI 诊断 only, 不进正交性分类 — 见 docstring 不对称)
    # ss 列尚未物化时 compute_nmi_matrix 优雅返回全 NaN matrix (missing_cols 守卫)。
    point_s, lo_s, hi_s, n_s = compute_nmi_matrix(
        df, DIMS_SS, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    # cross 6x6
    point_x, lo_x, hi_x, n_x = compute_nmi_matrix(
        df, ALL_DIMS, bootstrap_n=bootstrap_n, seed=boot_seed_state,
    )
    _phase_t['nmi_matrices(full/ctx/ss/cross)'] = time.time() - _t1

    _t2 = time.time()
    # permutation null (独立 seed) — 6×6 cross-matrix 参考 (落盘用)
    null_p95, null_p99 = compute_permutation_null(
        df, ALL_DIMS, n_permutations=n_permutations, seed=perm_seed_state,
    )

    # fix(omni-g-audit-family-04, 2026-06-11): classify 的观测值 point_f 在 DIMS_FULL
    # 3 列 listwise 样本上计算, 旧实现却对照 ALL_DIMS 6 列 listwise 样本的 null 阈值 —
    # NMI 有限样本偏差随 N 变化, 观测/阈值样本域不一致 (轨间缺失差异越大错配越大).
    # 现为 DIMS_FULL 在其自身 listwise 域上单独重算 null, 与 point_f 同域.
    null_p95_f, null_p99_f = compute_permutation_null(
        df, DIMS_FULL, n_permutations=n_permutations, seed=perm_seed_state,
    )

    # 正交性分类 (有意只对 full 3 维 — 论文 Appendix A.2 叙事更简洁; plan §7.3-A3
    # 不对称: ctx/ss 仅出 3×3 NMI 矩阵作诊断, 不进分类/解读)
    classify = classify_orthogonality(point_f, null_p95_f, null_p99_f)
    _phase_t['permutation_null+classify'] = time.time() - _t2

    _t3 = time.time()
    # 写出产物
    def _save_matrix(name: str, point: pd.DataFrame, lo: pd.DataFrame,
                     hi: pd.DataFrame, n: pd.DataFrame) -> None:
        # 把 4 层矩阵堆成长表 DataFrame 再落 parquet
        long = []
        for d1 in point.index:
            for d2 in point.columns:
                long.append({
                    'd1': d1, 'd2': d2,
                    'nmi': point.loc[d1, d2],
                    'ci_low': lo.loc[d1, d2],
                    'ci_high': hi.loc[d1, d2],
                    'n_pair': int(n.loc[d1, d2]),
                })
        pd.DataFrame(long).to_parquet(out_path / name, index=False)  # CR-14

    _save_matrix('72_nmi_matrix_full.parquet', point_f, lo_f, hi_f, n_f)
    _save_matrix('72_nmi_matrix_ctx.parquet', point_c, lo_c, hi_c, n_c)
    # 第三轨 ss 3×3 NMI 诊断 (复用既有文件名模式; plan §⑪: 列内扩展, OUTPUT_REGISTRY 不新增)
    _save_matrix('72_nmi_matrix_ss.parquet', point_s, lo_s, hi_s, n_s)
    _save_matrix('72_nmi_matrix_cross.parquet', point_x, lo_x, hi_x, n_x)
    null_p95.to_parquet(out_path / '72_nmi_null_p95.parquet')
    null_p99.to_parquet(out_path / '72_nmi_null_p99.parquet')

    # summary 用的非对角最大值 (nan 安全, 防部分 pair 退化)
    off_diag_mask = ~np.eye(len(ALL_DIMS), dtype=bool)
    off_diag_vals = point_x.values[off_diag_mask]
    max_off_diag = float(np.nanmax(off_diag_vals)) if not np.all(np.isnan(off_diag_vals)) else float('nan')

    # CR-15: 空真 (vacuous truth) bug 修复 — 当 classify 全为 'undefined' 时
    # (如所有 permutation null 因维度退化而失败), 旧 `all(... if v != 'undefined')`
    # 对空集合返回 True (空真), 错报 'strong'。现先显式过滤再判。
    non_undefined = [v for v in classify.values() if v != 'undefined']
    if not non_undefined:
        interpretation = 'undefined'
    elif all(v == 'strong' for v in non_undefined):
        interpretation = 'strong'
    elif any(v == 'weak' for v in non_undefined):
        interpretation = 'mixed'
    else:
        interpretation = 'moderate'

    summary = {
        'max_off_diag_nmi': max_off_diag,
        'classify_full_3x3': classify,
        'interpretation': interpretation,
        # fix(omni-g-audit-family-04, 2026-06-11): 口径披露 — 观测与 null 同域 +
        # 单侧分位阈值 (非双侧 Z 1.96/2.58)
        'classify_threshold_scale': (
            'one-sided permutation percentile p95/p99 (≈ one-sided Z 1.645/2.326); '
            'observed NMI and null share the same DIMS_FULL 3-col listwise sample'),
        'reproducibility': {
            'stage_21_input': stage_21_parquet,
            'v3_4_0_anchor': '450c1aa7 (per plan §0 Tag-over-hash)',
            'bootstrap_n': bootstrap_n,
            'n_permutations': n_permutations,
            'seed': seed,
        },
    }
    with open(out_path / '72_nmi_summary.json', 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    _phase_t['write_products'] = time.time() - _t3

    # 结果分析 — 写入日志: full 3×3 逐对 NMI vs null 门槛 + 判读。
    logger.info("-" * 72)
    logger.info(
        f"【结果分析】full 3×3 构念对 (listwise n={int(n_f.iloc[0, 1])}; NMI 越低越正交):"
    )
    for i, j in ((0, 1), (0, 2), (1, 2)):
        d1, d2 = DIMS_FULL[i], DIMS_FULL[j]
        s1 = d1.replace('innovation_', '').replace('_full', '')
        s2 = d2.replace('innovation_', '').replace('_full', '')
        v1 = classify.get(f'{d1}__{d2}', 'undefined')
        v2 = classify.get(f'{d2}__{d1}', 'undefined')
        verdict = v1 if v1 == v2 else f'{v1}/{v2} (临界)'
        # [富集 2026-06-29 Round-8] 追加 bootstrap 95% 百分位 CI — headline 不确定性
        # 量化 (此前已逐对落 parquet, 但日志只见点估计)。lo_f/hi_f 均为已算 locals。
        logger.info(
            f"  {s1} × {s2}: NMI={sig4(point_f.iloc[i, j])}  "
            f"CI=[{sig4(lo_f.iloc[i, j])}, {sig4(hi_f.iloc[i, j])}]  "
            f"null_p95={sig4(null_p95_f.iloc[i, j])}  null_p99={sig4(null_p99_f.iloc[i, j])}  → {verdict}"
        )
    # [富集 2026-06-29 Round-8] ctx 3×3 与 ss 3×3 三对非对角 NMI — 与 full 平行的构念
    # 正交性证据 (此前只落 72_nmi_matrix_{ctx,ss}.parquet、日志完全不可见)。ss 列未物化时
    # compute_nmi_matrix 返回全 NaN 矩阵 → sig4(NaN) 良性。仅用已算 locals point_c/n_c/point_s/n_s。
    try:
        _n_ctx = int(n_c.iloc[0, 1])
        logger.info(f"  [ctx 轨] 3×3 非对角 NMI (listwise n={_n_ctx:,d}):")
        for i, j in ((0, 1), (0, 2), (1, 2)):
            s1 = DIMS_CTX[i].replace('innovation_', '').replace('_ctx', '')
            s2 = DIMS_CTX[j].replace('innovation_', '').replace('_ctx', '')
            logger.info(f"      {s1} × {s2}: NMI={sig4(point_c.iloc[i, j])}")
    except Exception as _e:  # noqa: BLE001 — 日志块绝不阻断阶段
        logger.warning(f"  (ctx 3×3 NMI 块跳过: {_e})")
    try:
        _n_ss = int(n_s.iloc[0, 1])
        logger.info(
            f"  [ss 轨/银行+金科同句] 3×3 非对角 NMI (listwise n={_n_ss:,d}; 0=ss 列未物化):"
        )
        for i, j in ((0, 1), (0, 2), (1, 2)):
            s1 = DIMS_SS[i].replace('innovation_', '').replace('_ss', '')
            s2 = DIMS_SS[j].replace('innovation_', '').replace('_ss', '')
            logger.info(f"      {s1} × {s2}: NMI={sig4(point_s.iloc[i, j])}")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (ss 3×3 NMI 块跳过: {_e})")
    logger.info(f"  cross 6×6 非对角最大 NMI = {sig4(max_off_diag)}")
    # [富集 2026-06-29 Round-8] cross 6×6 全 30 个非对角格的 NMI 分布 (均值/中位/标准差) —
    # 只报 binding max 会掩盖整体跨轨正交性水平; 报全分布给审稿人完整画像。off_diag_vals
    # 为上文已算 local (line ~593), 此处只读取派生统计后丢弃, 不回流下游。
    try:
        _od_valid = off_diag_vals[~np.isnan(off_diag_vals)]
        if _od_valid.size:
            logger.info(
                f"  cross 6×6 非对角 NMI 分布 (有效 {_od_valid.size:,d}/30 格): "
                f"均值={sig4(np.nanmean(off_diag_vals))}  "
                f"中位={sig4(np.nanmedian(off_diag_vals))}  "
                f"标准差={sig4(np.nanstd(off_diag_vals))}"
            )
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (cross 6×6 分布块跳过: {_e})")
    logger.info(
        f"  总判读 interpretation = {interpretation} "
        "(strong=全对正交; moderate=无 weak 但非全 strong; mixed=至少一对 weak; undefined=不可判)"
    )
    logger.info(
        f"  ⚠ 样本 = {len(df):,} 篇 (盘面 T=2 小样本, 仅验证管道正确性, 非全量生产结论)"
    )
    logger.info("-" * 72)

    # ⑥ ⏱ 阶段计时 — 各主要子阶段墙钟耗时汇总 (日志富集, 2026-06-24)
    try:
        logger.info("⑥ ⏱ 阶段计时 (各子阶段墙钟耗时, 秒)")
        for _name, _sec in _phase_t.items():
            logger.info(f"     · {_name:<34} {sig4(_sec):>10} 秒")
        logger.info(f"     · {'合计 (load→write)':<34} {sig4(sum(_phase_t.values())):>10} 秒")
    except Exception as _e:  # noqa: BLE001
        logger.warning(f"  (TIMING banner 跳过: {_e})")

    logger.info(
        f"  ✓ v3.5.0 D3 stage 72 done; max off-diag NMI = {sig4(max_off_diag)}; "
        f"interpretation = {summary['interpretation']}"
    )
    return summary
