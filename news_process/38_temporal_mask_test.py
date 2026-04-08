"""
38_temporal_mask_test.py — B2-1: 时间掩码前视偏误检验
=====================================================

学术依据:
    Tetlock et al. (2008, JF) §4.2:
    "We verify that our text-based measure does not inadvertently 
    incorporate future information by re-estimating regressions 
    after masking the most recent year(s) of news data."

功能:
    1. 加载已验证文章级数据 (21_tone_llms.parquet)
    2. 按配置的窗口逐步掩码最新 N 年的新闻
    3. 对掩码后的子集重建 Bank-Year 面板
    4. 比较掩码前后核心回归变量的面板统计量
    5. 输出稳定性诊断报告

输入:
    21_tone_llms.parquet (已验证文章级数据)
    
输出:
    temporal_mask_diagnostics.csv (掩码前后系数对比)
"""

import os
import numpy as np
import pandas as pd

from utils.helpers import (
    load_config, setup_logging, log_memory_usage,
    log_stage_summary
)

# ============================================================================
# 1. 配置
# ============================================================================

CONFIG = load_config()
STAGE_NAME = "38_temporal_mask_test"
logger = setup_logging(STAGE_NAME, CONFIG["paths"]["log_dir"])

MASK_CONFIG = CONFIG.get('temporal_mask_test', {})
MASK_WINDOWS = MASK_CONFIG.get('mask_windows', [])
STABILITY_THRESHOLD = MASK_CONFIG.get('coefficient_stability_threshold', 0.20)


def _build_masked_panel_stats(df: pd.DataFrame, max_year: int, 
                               n_years_mask: int) -> dict:
    """对掩码后的子集计算核心面板统计量。
    
    Args:
        df: 文章级 DataFrame (含 llm_vote_score_full, year 等)
        max_year: 原始数据的最大年份
        n_years_mask: 需要掩码的年数
    
    Returns:
        dict: 包含掩码后的核心统计量
    """
    cutoff_year = max_year - n_years_mask + 1
    df_masked = df[df['year'] < cutoff_year].copy()
    
    if len(df_masked) == 0:
        logger.warning(f"  掩码后无数据 (cutoff_year={cutoff_year})")
        return {'n_articles': 0, 'n_years': 0}
    
    stats = {
        'n_articles': len(df_masked),
        'n_years': df_masked['year'].nunique(),
        'year_range': f"{df_masked['year'].min()}-{df_masked['year'].max()}",
    }
    
    # 核心情感变量统计
    for track in ['_full', '_ctx', '_title']:
        score_col = f'llm_vote_score{track}'
        if score_col in df_masked.columns:
            panel = df_masked.groupby(['target_bank', 'year']).agg(
                tone_mean=(score_col, 'mean'),
                tone_std=(score_col, 'std'),
                n_obs=(score_col, 'count')
            ).reset_index()
            
            stats[f'panel_tone_mean{track}'] = panel['tone_mean'].mean()
            stats[f'panel_tone_std{track}'] = panel['tone_mean'].std()
            stats[f'panel_n_bankyr{track}'] = len(panel)
            stats[f'panel_avg_obs{track}'] = panel['n_obs'].mean()
    
    return stats


def main():
    """时间掩码前视偏误检验主流程。"""
    import time
    stage_start = time.time()
    
    if not MASK_CONFIG.get('enabled', False):
        logger.info("temporal_mask_test.enabled = false, 跳过")
        return
    
    logger.info("=" * 60)
    logger.info("B2-1: 时间掩码前视偏误检验")
    logger.info("=" * 60)
    
    # 加载已验证文章级数据
    input_filename = CONFIG.get('filenames', {}).get(
        'output_21_tone_llms', '21_tone_llms.parquet')
    input_path = os.path.join(CONFIG["paths"]["output_dir"], input_filename)
    
    if not os.path.exists(input_path):
        logger.error(f"输入文件不存在: {input_path}")
        return
    
    df = pd.read_parquet(input_path)
    logger.info(f"加载数据: {len(df):,} 行")
    
    # 时间解析
    if 'year' not in df.columns:
        if '日期' in df.columns:
            df['year'] = pd.to_datetime(df['日期']).dt.year
        else:
            logger.error("数据中无 'year' 或 '日期' 列")
            return
    
    max_year = df['year'].max()
    logger.info(f"数据年份范围: {df['year'].min()}-{max_year}")
    
    # 基准统计量（无掩码）
    baseline_stats = _build_masked_panel_stats(df, max_year, 0)
    baseline_stats['window'] = 'baseline'
    baseline_stats['n_years_masked'] = 0
    
    all_results = [baseline_stats]
    
    # 逐窗口掩码
    for window in MASK_WINDOWS:
        name = window['name']
        n_mask = window['n_years_mask']
        desc = window.get('description', name)
        
        logger.info(f"\n  ── 掩码窗口: {desc} (mask={n_mask}年) ──")
        
        masked_stats = _build_masked_panel_stats(df, max_year, n_mask)
        masked_stats['window'] = name
        masked_stats['n_years_masked'] = n_mask
        
        all_results.append(masked_stats)
        
        # 稳定性检查
        for track in ['_full', '_ctx', '_title']:
            baseline_mean = baseline_stats.get(f'panel_tone_mean{track}', None)
            masked_mean = masked_stats.get(f'panel_tone_mean{track}', None)
            
            if baseline_mean is not None and masked_mean is not None and baseline_mean != 0:
                pct_change = abs(masked_mean - baseline_mean) / abs(baseline_mean)
                if pct_change > STABILITY_THRESHOLD:
                    logger.warning(
                        f"  ⚠ {track} 情感均值变动 {pct_change:.1%} > "
                        f"阈值 {STABILITY_THRESHOLD:.0%} "
                        f"(baseline={baseline_mean:.4f}, masked={masked_mean:.4f})")
                else:
                    logger.info(
                        f"  ✓ {track} 情感均值稳定 "
                        f"(变动 {pct_change:.1%}, baseline={baseline_mean:.4f})")
    
    # 输出诊断报告
    results_df = pd.DataFrame(all_results)
    
    output_dir = CONFIG["paths"]["output_dir"]
    suffix = MASK_CONFIG.get('output_dir_suffix', '_temporal_mask')
    output_path = os.path.join(output_dir, f'temporal_mask_diagnostics{suffix}.csv')
    results_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"\n诊断报告已保存: {output_path}")
    
    # 汇总
    logger.info("\n" + "=" * 60)
    logger.info("时间掩码前视偏误检验汇总")
    logger.info("=" * 60)
    for _, row in results_df.iterrows():
        logger.info(f"  [{row['window']}] "
                    f"n_articles={int(row.get('n_articles', 0)):,}, "
                    f"n_years={int(row.get('n_years', 0))}, "
                    f"tone_mean_full={row.get('panel_tone_mean_full', 'N/A')}")
    
    log_stage_summary(logger, STAGE_NAME, stage_start, len(df), len(df))


if __name__ == "__main__":
    main()
