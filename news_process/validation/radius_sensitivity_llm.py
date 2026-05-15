"""news_process.validation.radius_sensitivity_llm — Stage 35 LLM 升级 (v3.2.0)

Plan v14 §3.5 P5.2: stage 35 词典法 → LLM 法升级
    现行 stage 35 (radius_sensitivity.py) 是纯词典法 (5 个 jieba 词典).
    本模块新建 LLM 法 section, 与 dict-based 并存 (plan v14 P5.2 backward-compat).

核心洞察 (plan v14 R11):
    一次 LLM 调用的 unified_cot.txt v7 prompt 同时产出三阶段输出:
      stage 1: verification (is_bank_fintech_news + confidence)
      stage 2: sentiment + confidence
      stage 3: innovation_locus + innovation_substantiveness + confidences
    → 一组 LLM 调用产 sentiment + locus + substantiveness 三轴 robustness 报告.

实际 LLM 调用量 (plan v14 修订, 取代 180k 误估):
    N = 1170 (current production stage 14 input rows)
    L = 3 LLMs (gpt-5.4-nano / gemini-3.1-flash-lite / deepseek-v4-flash)
    R_new = 3 (radii ∈ {0, 2, 3}; radius=1 已缓存 baseline)
    T = 1 (仅 ctx 轨; full 轨缓存命中, 不受 radius 影响)
    Total = N × L × R_new × T = 1170 × 3 × 3 × 1 = 10,530

锚定文献:
    Hassan et al. (2019, QJE) Proximity-based Attribution 参数敏感性
    Sautner et al. (2023, JF) firm × topic 邻近化 robustness
    Bingler et al. (2022, FRL) cheap talk segment-level robustness
"""
from __future__ import annotations

import json
import logging
import os
import sys
from typing import Dict, List

import numpy as np
import pandas as pd

_HERE = os.path.dirname(os.path.abspath(__file__))
_PROJECT_PARENT = os.path.dirname(os.path.dirname(_HERE))
if _PROJECT_PARENT not in sys.path:
    sys.path.insert(0, _PROJECT_PARENT)

from news_process.core.config import load_config

logger = logging.getLogger(__name__)

# 检验参数 (plan v14 §3.5 P5.2)
RADII_TO_TEST: List[int] = [0, 1, 2, 3]
CACHED_RADIUS: int = 1  # 已存在的 baseline 配置, 不重跑

# κ 阈值 (plan v14 §5.2 R5-B, Landis & Koch 1977 substantial)
KAPPA_THRESHOLD_RADIUS = 0.70  # radius 稳健性: 期望高 (双轨内不同 radius 应稳定)


def cohens_kappa_2cat(y1: np.ndarray, y2: np.ndarray) -> Dict[str, float]:
    """Cohen's κ for 2-category labels (e.g., locus / substantiveness).

    Returns dict: {kappa, observed_agreement, expected_agreement, n}
    """
    mask = (~pd.isna(y1)) & (~pd.isna(y2))
    y1, y2 = y1[mask], y2[mask]
    n = len(y1)
    if n < 2:
        return {'kappa': float('nan'), 'observed_agreement': float('nan'),
                'expected_agreement': float('nan'), 'n': n}
    # 观察一致率
    p_o = np.mean(y1 == y2)
    # 预期一致率 (按 marginal 概率)
    cats = sorted(set(np.concatenate([y1, y2])))
    p_e = 0.0
    for c in cats:
        p_e += (np.mean(y1 == c) * np.mean(y2 == c))
    if p_e >= 1.0:
        return {'kappa': float('nan'), 'observed_agreement': float(p_o),
                'expected_agreement': float(p_e), 'n': int(n)}
    kappa = (p_o - p_e) / (1.0 - p_e)
    return {
        'kappa': float(kappa),
        'observed_agreement': float(p_o),
        'expected_agreement': float(p_e),
        'n': int(n),
    }


def estimate_llm_calls(n_articles: int, n_radii_new: int = 3, n_llms: int = 3) -> Dict[str, int]:
    """估算本次 stage 35 LLM 升级的 API 调用量 (plan v14 修订, 替代 180k 误估).

    Args:
        n_articles: stage 21 输入文章数 (默认从 stage 14 parquet 读)
        n_radii_new: 新 radii 数 (默认 3 = {0, 2, 3}, radius=1 缓存)
        n_llms: 并发 LLM 数 (默认 3)

    Returns:
        dict: {per_radius, total, with_full_track_wrong, savings_factor}
    """
    per_radius_ctx_only = n_articles * n_llms * 1  # 仅 ctx 轨
    total = per_radius_ctx_only * n_radii_new
    # 假设错误计算 (full + ctx 都重跑, 误估)
    naive_with_full = n_articles * n_llms * 2 * (n_radii_new + 1)
    return {
        'per_radius_calls': per_radius_ctx_only,
        'total_calls': total,
        'naive_full_track_count': naive_with_full,
        'savings_factor': round(naive_with_full / max(total, 1), 1),
    }


def parse_track_results_from_cache(
    radius: int,
    articles_df: pd.DataFrame,
) -> Dict[int, pd.DataFrame]:
    """从 LLMCache (sqlite) 读取指定 radius 下的篇章级 stage 3 标签.

    Args:
        radius: sentence_radius 配置值
        articles_df: stage 14 输入子集 (含 target_bank, content_ctx 列)

    Returns:
        {article_idx: {'sentiment': str, 'locus': str, 'substantiveness': str,
                       'sent_conf': float, 'locus_conf': float, 'subst_conf': float}}

    注: 实际生产中, 该函数应调用 tone_llms._aggregate_track + LLMCache lookup;
        本 module 仅声明接口, 落地实现待 M5 第 2 commit (调用真 LLM 时).
    """
    raise NotImplementedError(
        "parse_track_results_from_cache 待 M5 第 2 commit 落地 — 需调用 yunwu API key + tone_llms._aggregate_track. "
        "本 commit 仅声明接口 + κ 计算工具 + 调用量估算; "
        "实际 10.5k LLM 调用 launch 命令: "
        "F:/Anaconda3/python.exe -m news_process.validation.radius_sensitivity_llm --launch"
    )


def compute_radius_kappa_report(
    labels_by_radius: Dict[int, pd.DataFrame],
    baseline_radius: int = 1,
) -> Dict[str, Dict[int, Dict[str, float]]]:
    """计算每个非基线 radius vs baseline radius 的 κ (sentiment + locus + substantiveness).

    Args:
        labels_by_radius: {radius: DataFrame(article_idx, sentiment, locus, substantiveness)}
        baseline_radius: 比较基线 (默认 radius=1)

    Returns:
        {dimension: {radius: {kappa, observed_agreement, n}}}
    """
    if baseline_radius not in labels_by_radius:
        raise ValueError(f"baseline_radius {baseline_radius} 不在 labels_by_radius keys")

    base = labels_by_radius[baseline_radius]
    report: Dict[str, Dict[int, Dict[str, float]]] = {
        'sentiment': {},
        'innovation_locus': {},
        'innovation_substantiveness': {},
    }

    for radius, df_r in labels_by_radius.items():
        if radius == baseline_radius:
            continue
        # 按 article_idx 对齐 (假设 index 一致)
        merged = base.merge(df_r, on='article_idx', suffixes=('_base', '_var'))
        for dim in ['sentiment', 'innovation_locus', 'innovation_substantiveness']:
            base_col = f'{dim}_base'
            var_col = f'{dim}_var'
            if base_col in merged.columns and var_col in merged.columns:
                k = cohens_kappa_2cat(merged[base_col].values, merged[var_col].values)
                report[dim][radius] = k
            else:
                report[dim][radius] = {'kappa': float('nan'), 'n': 0,
                                       'observed_agreement': float('nan'),
                                       'expected_agreement': float('nan')}

    return report


def write_radius_llm_report(report: Dict, output_path: str,
                             call_estimates: Dict[str, int],
                             baseline_n: int) -> None:
    """写 stage 35 LLM 法 robustness 报告 (plan v14 §3.5 P5.2).

    Args:
        report: compute_radius_kappa_report 返回值
        output_path: JSON 输出路径
        call_estimates: estimate_llm_calls 返回值
        baseline_n: baseline radius 的文章数
    """
    out = {
        'stage': '35_radius_sensitivity_llm',
        'methodology': 'plan v14 §3.5 P5.2; Hassan 2019 QJE + Sautner 2023 JF 等参数敏感性',
        'cached_radius': CACHED_RADIUS,
        'new_radii': [r for r in RADII_TO_TEST if r != CACHED_RADIUS],
        'baseline_n': baseline_n,
        'call_estimates': call_estimates,
        'kappa_threshold_radius': KAPPA_THRESHOLD_RADIUS,
        'pass_criterion': '全部 radius vs baseline κ ≥ 0.70 (Landis & Koch substantial)',
        'kappa_report': report,
        'passed': all(
            all(r['kappa'] >= KAPPA_THRESHOLD_RADIUS for r in dim_report.values() if not np.isnan(r['kappa']))
            for dim_report in report.values()
        ),
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2, default=str)
    logger.info(f"Stage 35 LLM 法报告已写入: {output_path}")


def main():
    """Stage 35 LLM 法主入口 (复用 stage 35 thin shim, --llm flag 触发).

    工作流:
        1. estimate_llm_calls: 给用户看实际预算
        2. 对每个 new radius ∈ {0, 2, 3}: 重抽 ctx → 调 LLM → cache
        3. parse_track_results_from_cache 收集双轨标签
        4. compute_radius_kappa_report
        5. write_radius_llm_report
    """
    CONFIG = load_config()
    stage_14_filename = CONFIG.get('filenames', {}).get(
        'output_14_fintech_intensity', '14_fintech_intensity.parquet')
    stage_14_path = os.path.join(CONFIG['paths']['output_dir'], stage_14_filename)

    logger.info(f"=== Stage 35 LLM 法升级 (plan v14 §3.5 P5.2) ===")

    # 1. 估算 LLM 调用量 (替代 plan v13/v14 早期 180k 误估)
    df_stage14 = pd.read_parquet(stage_14_path)
    n_articles = len(df_stage14)
    estimates = estimate_llm_calls(n_articles=n_articles)
    logger.info(f"  N (stage 14 输入): {n_articles}")
    logger.info(f"  实际 LLM 调用: {estimates['total_calls']:,} "
                f"(= {estimates['per_radius_calls']:,} × {len(RADII_TO_TEST) - 1} new radii)")
    logger.info(f"  早前错估 (含 full 轨重跑): {estimates['naive_full_track_count']:,} "
                f"({estimates['savings_factor']}× 节省)")

    # 2-5: 实际 LLM 调用 + κ 报告 (launch-ready 占位)
    logger.info("  M5 第 2 commit 落地: 调 tone_llms._aggregate_track + LLMCache + κ 报告")
    logger.info("  CLI: F:/Anaconda3/python.exe -m news_process.validation.radius_sensitivity_llm --launch")


if __name__ == '__main__':
    main()
