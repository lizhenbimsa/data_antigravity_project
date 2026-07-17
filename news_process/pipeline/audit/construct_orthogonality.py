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

Performance estimate (修 F3):
    bootstrap 1000 × matrix cells: full 3×3 ≈ 7 min / ctx 3×3 ≈ 7 min /
    ss 3×3 ≈ 7 min (第三轨 NMI 诊断) / cross 6×6 ≈ 30 min;
    permutation 1000 × 30 off-diagonal ≈ 25 min.
    Total wall-time ≈ 77 min single-thread (sklearn NMI ~100 ms / call on N≈400k).
    Recommended default for D4 day (修 F31): n_jobs=16 → ~5 min on 64-core MP machine.

Concurrency (修 F7 + F43):
    本函数 single-thread 设计; SeedSequence.spawn 已 pre-allocate seeds 故 parallel 友好.
    sklearn `normalized_mutual_info_score` 内部 sparse contingency table 构造在
    sklearn 1.5-1.8 **基于源码 review 判断单调用线程安全** (无 sklearn 官方文档明确 claim,
    谨慎说法). joblib `n_jobs > 1` 可加速但需用 `prefer='processes'` (避免 GIL);
    默认实现保持 single-thread. 若 production parallel 触发 race condition 异常,
    立即 fallback `n_jobs=1` + audit log §E.thread_race_event 记录.

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

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if sample_strategy == 'pairwise_complete':
                # d1==d2 时去重列名, 避免重名列
                # (DataFrame[[d1,d1]] 会返回 DataFrame 切片而非 Series)。
                cols = [d1] if d1 == d2 else [d1, d2]
                clean = df[cols].dropna()
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

            point.iloc[i, j] = nmi_score(
                clean[d1], clean[d2], average_method='arithmetic'
            )

            # CR-10: bootstrap 只对 [d1, d2] 两列 resample (省 listwise 共享 base
            # 的 6-列 memory; 对 N=400k × 6 cols × 1000 boot × 36 cells, 减 ~70% peak)
            clean_pair = clean[[d1, d2]]

            # Bootstrap CI: integral row-pair resample (修 C1)
            # CR-11: degenerate fallback 改 NaN + 用 nanpercentile + count
            boot = np.full(bootstrap_n, np.nan)
            n_degenerate = 0
            for k, s in enumerate(boot_seeds):
                state = int(s.generate_state(1)[0])
                clean_boot = clean_pair.sample(frac=1, replace=True, random_state=state)
                # 防 bootstrap resample 后 degenerate (极不平衡 label 时常见)
                if clean_boot[d1].nunique() < 2 or clean_boot[d2].nunique() < 2:
                    n_degenerate += 1
                    continue  # leave boot[k] as NaN
                boot[k] = nmi_score(
                    clean_boot[d1], clean_boot[d2],
                    average_method='arithmetic'
                )
            # 记录 degenerate 比例 (审稿人 sanity check); >5% 触发 warning
            if n_degenerate > 0:
                degen_frac = n_degenerate / bootstrap_n
                if degen_frac > 0.05:
                    logger.warning(
                        f"  v3.5.0 D3 bootstrap ({d1}, {d2}): "
                        f"{n_degenerate:,d}/{bootstrap_n:,d} = {pct4(degen_frac)} resamples degenerate; "
                        "CI computed via nanpercentile"
                    )
            # nanpercentile 自动跳过 NaN; 若 boot 全 NaN, 留 ci 为 NaN
            valid_boot = boot[~np.isnan(boot)]
            if len(valid_boot) > 0:
                ci_low.iloc[i, j] = float(np.percentile(valid_boot, 2.5))
                ci_high.iloc[i, j] = float(np.percentile(valid_boot, 97.5))

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
    nmi_score = _lazy_import_nmi()
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

    for i, d1 in enumerate(dims):
        for j, d2 in enumerate(dims):
            if i == j:
                continue
            if clean[d1].nunique() < 2 or clean[d2].nunique() < 2:
                continue

            null = np.empty(n_permutations)
            d2_vals = clean[d2].values
            for k, s in enumerate(perm_seeds):
                rng = np.random.default_rng(s)
                d2_perm = rng.permutation(d2_vals)
                null[k] = nmi_score(
                    clean[d1], d2_perm, average_method='arithmetic'
                )
            null_p95.iloc[i, j] = float(np.percentile(null, 95))
            null_p99.iloc[i, j] = float(np.percentile(null, 99))

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
