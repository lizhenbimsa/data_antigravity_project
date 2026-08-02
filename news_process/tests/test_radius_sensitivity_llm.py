"""v3.2.0 — Stage 35 LLM 升级测试 (plan v14 §3.5 P5.2)

测试范围:
    - estimate_llm_calls: LLM 调用量估算 (10.5k 修订)
    - cohens_kappa_2cat: κ 计算正确性
    - compute_radius_kappa_report: 多 radius vs baseline
    - 接口声明完整性 (主调用链路 importable)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

_PROJECT_PARENT = Path(__file__).resolve().parents[2]
if str(_PROJECT_PARENT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_PARENT))


def test_estimate_llm_calls_default():
    """默认 N=1170 + 3 radii new + 3 LLM = 10,530 (替代 180k 错估)."""
    from news_process.validation.radius_sensitivity_llm import estimate_llm_calls
    est = estimate_llm_calls(n_articles=1170)
    assert est['per_radius_calls'] == 1170 * 3 * 1   # 3510
    assert est['total_calls'] == 10530               # 3510 × 3
    # naive (含 full 轨重跑 + 重跑 baseline): 1170 × 3 × 2 × 4 = 28080
    # savings = 28080 / 10530 ≈ 2.67× (仅 track 维度优化; vs 180k 旧估算的 17× 含 N 错估)
    assert 2.0 <= est['savings_factor'] <= 5.0


def test_estimate_llm_calls_scaling():
    """N 扩容 17× 时 (1170 → ~20k) 总调用接近老估算 180k."""
    from news_process.validation.radius_sensitivity_llm import estimate_llm_calls
    est = estimate_llm_calls(n_articles=20000)
    assert est['total_calls'] == 180000  # 20000 × 3 × 3


def test_cohens_kappa_perfect_agreement():
    """κ = 1.0 当 100% 一致."""
    from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat
    y1 = np.array(['底层技术', '应用场景', '底层技术', '应用场景'])
    y2 = np.array(['底层技术', '应用场景', '底层技术', '应用场景'])
    k = cohens_kappa_2cat(y1, y2)
    assert k['kappa'] == 1.0
    assert k['observed_agreement'] == 1.0
    assert k['n'] == 4


def test_cohens_kappa_chance_agreement():
    """κ ≈ 0 当 marginal 一致但实际无关联."""
    from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat
    # 4 行 50/50 split, 完全随机一致 / 不一致
    y1 = np.array(['底层技术', '底层技术', '应用场景', '应用场景'])
    y2 = np.array(['底层技术', '应用场景', '底层技术', '应用场景'])
    k = cohens_kappa_2cat(y1, y2)
    # observed = 2/4 = 0.5; expected = 0.5×0.5 + 0.5×0.5 = 0.5; kappa = 0
    assert abs(k['kappa']) < 0.01


def test_cohens_kappa_handles_nan():
    """NaN 行被 mask 掉, 不参与 κ 计算."""
    from news_process.validation.radius_sensitivity_llm import cohens_kappa_2cat
    y1 = np.array(['底层技术', np.nan, '底层技术'], dtype=object)
    y2 = np.array(['底层技术', '应用场景', '底层技术'], dtype=object)
    k = cohens_kappa_2cat(y1, y2)
    assert k['n'] == 2  # mask 后 2 行


def test_radii_constants_match_plan():
    """plan v14 §3.5 P5.2: RADII = {0, 1, 2, 3}, baseline = 1."""
    from news_process.validation.radius_sensitivity_llm import CACHED_RADIUS, RADII_TO_TEST
    assert set(RADII_TO_TEST) == {0, 1, 2, 3}
    assert CACHED_RADIUS == 1


def test_module_importable_without_launch():
    """plan v14 §3.5 P5.2: 模块可 import + main 可调; 不强制 LLM launch."""
    import news_process.validation.radius_sensitivity_llm as mod
    assert hasattr(mod, 'main')
    assert hasattr(mod, 'estimate_llm_calls')
    assert hasattr(mod, 'compute_radius_kappa_report')
    assert hasattr(mod, 'cohens_kappa_2cat')


def test_parse_cache_returns_empty_df_when_cache_missing(tmp_path):
    """v3.2.0 M3/7: parse_track_results_from_cache 在 cache 不存在时返回空 DataFrame (graceful, 不 raise)."""
    from news_process.validation.radius_sensitivity_llm import parse_track_results_from_cache
    fake_cache = tmp_path / "_no_such_cache.db"
    df = parse_track_results_from_cache(
        radius=0,
        articles_df=pd.DataFrame({'article_idx': [], 'target_bank': []}),
        cache_db_path=str(fake_cache),
    )
    assert isinstance(df, pd.DataFrame)
    assert df.empty or len(df) == 0
    # Schema 应含预期列 (即使为空)
    expected_cols = {'article_idx'}
    assert expected_cols.issubset(set(df.columns))


def test_parse_cache_uses_radius_param(tmp_path, caplog):
    """v3.2.0 M3/7: radius 参数被传入 logger.info, 不是死参数."""
    import logging

    from news_process.validation.radius_sensitivity_llm import parse_track_results_from_cache
    fake_cache = tmp_path / "_no_cache.db"
    with caplog.at_level(logging.INFO, logger='news_process.validation.radius_sensitivity_llm'):
        parse_track_results_from_cache(
            radius=2,
            articles_df=pd.DataFrame({'article_idx': []}),
            cache_db_path=str(fake_cache),
        )
    # radius=2 应出现在日志中
    assert 'radius=2' in caplog.text


def test_parse_cache_empty_articles_yields_empty_df(tmp_path):
    """空 articles_df → 空结果."""
    # 创建空 sqlite (cache 存在但无表)
    import sqlite3

    from news_process.validation.radius_sensitivity_llm import parse_track_results_from_cache
    cache = tmp_path / "_empty.db"
    conn = sqlite3.connect(str(cache))
    conn.close()
    df = parse_track_results_from_cache(
        radius=0,
        articles_df=pd.DataFrame({'article_idx': [], 'target_bank': []}),
        cache_db_path=str(cache),
    )
    assert isinstance(df, pd.DataFrame)
    assert df.empty or len(df) == 0


def test_parse_args_dry_run_default():
    """M1/7: CLI --dry-run 是 default 行为 (launch=False 即 dry-run 路径)."""
    from news_process.validation.radius_sensitivity_llm import _parse_args
    args = _parse_args([])
    # 默认 launch=False (即 dry-run)
    assert args.launch is False
    # dry_run argparse store_true default False; main() 用 not args.launch 判断 dry-run 路径
    assert args.dry_run is False


def test_parse_args_launch_flag():
    """M1/7: --launch 触发真实跑."""
    from news_process.validation.radius_sensitivity_llm import _parse_args
    args = _parse_args(['--launch'])
    assert args.launch is True


def test_parse_args_radii_custom():
    """M1/7: --radii 自定义 radii 列表."""
    from news_process.validation.radius_sensitivity_llm import _parse_args
    args = _parse_args(['--radii', '0,2'])
    assert args.radii == '0,2'


def test_parse_args_max_concurrency_default():
    """plan v14 R20-A: 默认并发 250 (2026-07-21 项目统一; OpenLux 429 退路 8)."""
    from news_process.validation.radius_sensitivity_llm import _parse_args
    args = _parse_args([])
    assert args.max_concurrency == 250


def test_check_launch_prerequisites_returns_dict():
    """M1/7: 前置检查返回 dict 含 OpenLux/cache/stage_14 状态."""
    from news_process.validation.radius_sensitivity_llm import _check_launch_prerequisites
    checks = _check_launch_prerequisites()
    assert 'openlux_api_key_present' in checks
    assert 'llm_cache_exists' in checks
    assert isinstance(checks['openlux_api_key_present'], bool)


def test_compute_radius_kappa_report_two_radii():
    """compute_radius_kappa_report 接受 2 radii + 输出三维度 κ."""
    from news_process.validation.radius_sensitivity_llm import compute_radius_kappa_report
    labels = {
        1: pd.DataFrame({
            'article_idx': [0, 1, 2],
            'sentiment': ['正面', '正面', '负面'],
            'innovation_locus': ['底层技术', '应用场景', '底层技术'],
            'innovation_substantiveness': ['实质性', '象征性', '实质性'],
        }),
        2: pd.DataFrame({
            'article_idx': [0, 1, 2],
            'sentiment': ['正面', '正面', '负面'],
            'innovation_locus': ['底层技术', '应用场景', '应用场景'],
            'innovation_substantiveness': ['实质性', '象征性', '实质性'],
        }),
    }
    report = compute_radius_kappa_report(labels, baseline_radius=1)
    assert 'sentiment' in report
    assert 'innovation_locus' in report
    assert 'innovation_substantiveness' in report
    assert 2 in report['sentiment']
    # sentiment 完全一致 → kappa = 1
    assert report['sentiment'][2]['kappa'] == 1.0
